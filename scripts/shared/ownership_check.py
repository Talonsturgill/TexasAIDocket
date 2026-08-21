#!/usr/bin/env python3
"""ownership_check.py — refuse a write that crosses an automation's lane.

WHY THIS EXISTS
This repo runs several unattended automations against one git history, and each of them ends
in a phase whose entire job is editing its own machine. Alaska kept its automations apart by
putting them in different repos and writing prose rules; that worked because the boundary was
also a repo boundary. Here the boundary is only as real as the check that enforces it.

WHAT IT DOES
Reads ownership.yaml, works out which files a change touches, and fails if the acting
automation does not own one of them. Rules are matched like .gitignore: evaluated in order,
LAST match wins, so broad defaults sit at the top and carve-outs below.

    ownership_check.py --actor daily --diff origin/main...HEAD
    ownership_check.py --actor gridwatch --staged
    ownership_check.py --actor daily --files docs/index.html ledger/docket.json
    ownership_check.py --branch claude/daily-2026-08-16 --diff-per-commit origin/main...HEAD
    ownership_check.py --self-test

A LANE IS SCOPED TO A COMMIT, NOT TO A BRANCH
Until 2026-08-16 the hook and CI disagreed about this and the disagreement was load bearing.
The hook checks the staged change against the stamp in `.git/ACTOR`, so it scopes a lane to one
commit. CI read ONE actor out of the branch prefix and checked the whole branch diff, so it
scoped a lane to a branch. The daily routine's own Phase 17 stamps `upgrade` and commits, on the
only branch Phase 16 gives it, so following the routine exactly produced a branch CI was built
to reject. The run that first shipped a deck hit it and had to route two commits around it.

`--diff-per-commit` is the agreement. It walks the range one commit at a time, reads that
commit's `Actor:` trailer, and checks only that commit's files against that actor. The trailer
is written by `.githooks/commit-msg` from the same `.git/ACTOR` stamp the pre-commit hook reads,
so one stamp drives both checkers and there is no second source of truth.

WHY A FALSE STAMP DOES NOT BUY ANYTHING, AND THE ONE PLACE IT WOULD
The trailer is written by the process being constrained, exactly like `.git/ACTOR`, so neither
is proof against a determined liar and neither is meant to be. Both are guardrails against a
routine wandering, and the lanes themselves are what carry the protection: `upgrade` owns the
machine and not the record, so a commit stamping `upgrade` to reach `ledger/docket.json` is
refused by the map whatever it calls itself.

`human` is the exception, because a maintainer owns every path, so an unattended run that
stamped `human` would own everything. That is why a branch declares which lanes it may carry.
`branch_also_allows` names the extra actors a prefix is allowed to stamp, and `human` is never
one of them. A `claude/daily-` branch may carry `daily` and `upgrade` commits and nothing else.

EXIT CODES
    0  every touched path is in the actor's lane
    1  a violation, or the checker was called wrongly
    2  the checker itself broke (bad yaml, no git). Distinct so CI can tell the difference
       between "you wrote out of lane" and "the gate is unavailable".
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:                                     # pragma: no cover
    print("ownership_check: PyYAML missing (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MAP = REPO_ROOT / "ownership.yaml"


# --------------------------------------------------------------------------- globbing
def glob_to_regex(pattern: str) -> re.Pattern:
    """Translate a path glob to a regex.

    `**` spans path segments, `*` does not, `?` is one non-separator character. Written out
    rather than using fnmatch because fnmatch's `*` happily crosses `/`, which would make
    `scripts/*` silently own `scripts/carousel/deep/file.py` and defeat the whole map.
    """
    out = ["^"]
    i, n = 0, len(pattern)
    while i < n:
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")          # zero or more leading segments
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    out.append("$")
    return re.compile("".join(out))


class Rule:
    __slots__ = ("path", "owner", "generated", "rebuild_by", "append_only", "note", "_rx")

    def __init__(self, raw: dict):
        self.path = raw["path"]
        self.owner = raw.get("owner")
        self.generated = bool(raw.get("generated", False))
        self.rebuild_by = list(raw.get("rebuild_by", []) or [])
        self.append_only = bool(raw.get("append_only", False))
        self.note = (raw.get("note") or "").strip()
        self._rx = glob_to_regex(self.path)

    def matches(self, path: str) -> bool:
        return bool(self._rx.match(path))

    def writers(self) -> list[str]:
        """Every actor allowed to produce a change to this path.

        A MAINTAINER MAY WRITE ANYTHING. The pre-commit hook has always said so in words, "a
        human at a keyboard owns everything, an unattended routine owns only its lane", and
        until 2026-08-11 the code did not implement it: `human` was refused on every path an
        automation owned, including the public docket a maintainer has to be able to seed and
        correct. The map exists to keep automations out of each other's lanes, not to lock the
        owner out of their own repository.

        `append_only` still binds a human, and that is deliberate. The protection the public
        record actually needs is not "nobody may write" but "nobody may quietly delete", which
        is exactly what CLAUDE.md's stop-and-ask list is about.
        """
        w = list(self.rebuild_by)
        if self.owner and self.owner not in w:
            w.append(self.owner)
        if "human" not in w:
            w.append("human")
        return w


class OwnershipMap:
    def __init__(self, doc: dict):
        self.actors = list((doc.get("actors") or {}).keys())
        self.branch_actors = dict(doc.get("branch_actors") or {})
        self.branch_also_allows = {k: list(v or []) for k, v in
                                   (doc.get("branch_also_allows") or {}).items()}
        self.rules = [Rule(r) for r in (doc.get("rules") or [])]
        if not self.rules:
            raise ValueError("ownership.yaml declares no rules")

    @classmethod
    def load(cls, path: Path) -> "OwnershipMap":
        return cls(yaml.safe_load(path.read_text(encoding="utf-8")))

    def rule_for(self, path: str) -> Rule | None:
        """Last matching rule wins, .gitignore style."""
        found = None
        for rule in self.rules:
            if rule.matches(path):
                found = rule
        return found

    def prefix_for_branch(self, branch: str) -> str | None:
        best = None
        for prefix in self.branch_actors:
            if branch.startswith(prefix) and (best is None or len(prefix) > len(best)):
                best = prefix
        return best

    def actor_for_branch(self, branch: str) -> str | None:
        prefix = self.prefix_for_branch(branch)
        return self.branch_actors[prefix] if prefix else None

    def actors_allowed_on_branch(self, branch: str) -> set[str]:
        """Every actor a commit on this branch may stamp.

        The branch's own actor, plus whatever `branch_also_allows` names for that prefix. A
        branch matching no prefix is a maintainer session, which may stamp anything.

        `human` is never addable here and the check below enforces it rather than trusting the
        map to be written carefully. A routine that could stamp `human` would own every path,
        which is the whole map switched off by one line in a commit message.
        """
        prefix = self.prefix_for_branch(branch)
        if prefix is None:
            return set(self.actors) or {"human"}
        allowed = {self.branch_actors[prefix]}
        allowed.update(a for a in self.branch_also_allows.get(prefix, []) if a != "human")
        return allowed

    def shadowed(self) -> list[tuple[int, str, str]]:
        """Rules a LATER rule has silently repealed.

        In a last-match-wins file a broad rule added at the bottom repeals a specific rule at
        the top, and the repealed rule still reads perfectly. That is not hypothetical here.
        `scripts/site/**` was written once as `owner: human` with the note "the gates, a
        routine that can edit the gate that judges it has no gate", and then written a second
        time further down with `rebuild_by: [carousel, gridwatch]`. The second won. For as long
        as it stood, the carousel could edit site_build.py, house_style_check.py and
        docket_build.py, which are the gates that judge it, while the file said the opposite in
        the plainest language anyone could write.

        The test is direct rather than clever. Build the most canonical path each rule exists
        to match, then ask the map which rule claims it. A rule that does not answer for its
        own namesake path is not narrowing anything, it is decoration.

        A rule may legitimately be overridden for PART of its range, which is how every
        carve-out here works. This only reports a rule overridden across the whole of it.
        """
        out = []
        for i, rule in enumerate(self.rules):
            probe = rule.path.replace("**/", "d/").replace("**", "d/f").replace("*", "f")
            probe = probe.rstrip("/") or "f"
            if not rule.matches(probe):
                continue                    # can't build a probe for it, so can't judge it
            winner = self.rule_for(probe)
            if winner is not rule:
                out.append((i, rule.path, winner.path if winner else "(none)"))
        return out


# --------------------------------------------------------------------------- git
def git(*args: str, cwd: Path = REPO_ROOT) -> str:
    proc = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def changed_files(diff: str | None, staged: bool, cwd: Path = REPO_ROOT) -> list[str]:
    if staged:
        out = git("diff", "--cached", "--name-only", "--diff-filter=ACMRD", cwd=cwd)
    else:
        out = git("diff", "--name-only", "--diff-filter=ACMRD", diff, cwd=cwd)
    return [line.strip() for line in out.splitlines() if line.strip()]


ACTOR_TRAILER = re.compile(r"^\s*Actor:\s*([A-Za-z0-9_-]+)\s*$", re.MULTILINE)


def commits_in(diff_range: str, cwd: Path = REPO_ROOT) -> list[str]:
    """Every non-merge commit the range introduces, oldest first.

    THE TWO DOTS ARE NOT A TYPO AND THE THREE DOTS ARE NOT INTERCHANGEABLE. `A...B` means
    merge-base-to-B for `git diff` and SYMMETRIC DIFFERENCE for `git rev-list`, which are
    different sets: the symmetric difference also carries commits that are on A and not on B.
    CI passes the range in diff spelling, so it is normalised here rather than at the call site,
    because the two spellings look identical in a workflow file and the wrong one silently
    judges this branch for commits it never made.

    `A..B` for rev-list is exactly merge-base-to-B along B, so it is the rev-list spelling of
    what `A...B` means to diff.

    MERGES ARE SKIPPED. A merge commit's diff against its first parent is the whole of the other
    side, which would re-flag every file that side legitimately carried, and the content a merge
    genuinely authors is conflict resolution that already appears in the commits being merged.
    Merging `main` into a run branch is routine here, and the commits it brings in are reachable
    from the base, so the range excludes them for the same reason.
    """
    rng = diff_range.replace("...", "..") if "..." in diff_range else diff_range
    out = git("rev-list", "--reverse", "--no-merges", rng, cwd=cwd)
    return [line.strip() for line in out.splitlines() if line.strip()]


def commit_actor(sha: str, default: str, cwd: Path = REPO_ROOT) -> tuple[str, bool]:
    """The actor a commit declares, and whether it declared one at all.

    An unstamped commit falls back to the branch's actor rather than to `human`. Falling back
    to `human` would mean any commit could opt out of the map by simply not stamping, which is
    the gate switched off by omission.
    """
    body = git("show", "-s", "--format=%B", sha, cwd=cwd)
    m = ACTOR_TRAILER.search(body)
    return (m.group(1), True) if m else (default, False)


def files_in_commit(sha: str, cwd: Path = REPO_ROOT) -> list[str]:
    out = git("diff-tree", "--no-commit-id", "--name-only", "-r",
              "--diff-filter=ACMRD", sha, cwd=cwd)
    return [line.strip() for line in out.splitlines() if line.strip()]


def deletes_lines(path: str, diff: str | None, staged: bool, cwd: Path = REPO_ROOT) -> bool:
    """True if the change removes or rewrites any existing line of `path`.

    An append leaves every prior line untouched, so a diff with no `-` body lines is an
    append. This is the check that protects a time series nobody can rebuild.
    """
    args = ["diff", "--unified=0"]
    if staged:
        args.append("--cached")
    elif diff:
        args.append(diff)
    args += ["--", path]
    for line in git(*args, cwd=cwd).splitlines():
        if line.startswith("---"):
            continue
        if line.startswith("-"):
            return True
    return False


# --------------------------------------------------------------------------- checking
class Violation:
    def __init__(self, path: str, reason: str, rule: Rule | None):
        self.path, self.reason, self.rule = path, reason, rule


def check(omap: OwnershipMap, actor: str, paths: list[str],
          diff: str | None = None, staged: bool = False,
          cwd: Path = REPO_ROOT, check_appends: bool = True) -> list[Violation]:
    violations: list[Violation] = []
    for path in paths:
        rule = omap.rule_for(path)
        if rule is None:
            violations.append(Violation(path, "no rule matches this path", None))
            continue

        writers = rule.writers()
        if actor not in writers:
            if rule.generated:
                why = (f"'{path}' is generated output; only {', '.join(sorted(writers))} "
                       f"may regenerate it")
            else:
                why = (f"'{path}' belongs to '{rule.owner}', not '{actor}'")
            violations.append(Violation(path, why, rule))
            continue

        if rule.append_only and check_appends:
            try:
                if deletes_lines(path, diff, staged, cwd=cwd):
                    violations.append(Violation(
                        path, "append-only: this change rewrites or deletes existing lines",
                        rule))
            except RuntimeError:
                pass                      # new file, or no diff context; nothing to protect
    return violations


def check_per_commit(omap: OwnershipMap, branch: str, diff_range: str,
                     cwd: Path = REPO_ROOT) -> int:
    """Walk a range one commit at a time, judging each against the actor it declares."""
    branch_actor = omap.actor_for_branch(branch)
    prefix_source = omap.prefix_for_branch(branch)
    allowed = omap.actors_allowed_on_branch(branch)
    if branch_actor is None:
        print(f"ownership: branch '{branch}' maps to no actor, treating as a maintainer session")
        branch_actor = "human"

    try:
        shas = commits_in(diff_range, cwd=cwd)
    except RuntimeError as exc:
        print(f"ownership: {exc}", file=sys.stderr)
        return 2

    if not shas:
        print(f"ownership: OK, {diff_range} introduces no non-merge commits")
        return 0

    failed = 0
    checked = 0
    inherited_failures = 0
    for sha in shas:
        actor, stamped = commit_actor(sha, branch_actor, cwd=cwd)
        subject = git("show", "-s", "--format=%s", sha, cwd=cwd).strip()
        short = sha[:9]

        if actor not in allowed:
            why = (f"stamps 'Actor: {actor}', which branch '{branch}' may not carry. "
                   f"Allowed here: {', '.join(sorted(allowed))}")
            print(f"ownership: FAIL  {short}  {subject}\n      {why}", file=sys.stderr)
            if actor == "human":
                print("      A routine may never stamp 'human'. That actor owns every path, "
                      "so it is the map switched off.", file=sys.stderr)
            failed += 1
            continue

        if omap.actors and actor not in omap.actors:
            print(f"ownership: FAIL  {short}  {subject}\n      unknown actor '{actor}'",
                  file=sys.stderr)
            failed += 1
            continue

        paths = files_in_commit(sha, cwd=cwd)
        checked += len(paths)
        # Append-only is judged against the commit's own diff, hence the explicit range.
        violations = check(omap, actor, paths, diff=f"{sha}^!", staged=False, cwd=cwd)
        mark = "ok  " if not violations else "FAIL"
        stamp = f"Actor: {actor}" + ("" if stamped else " (inherited from the branch)")
        line = f"  {mark}  {short}  {stamp:<44}  {len(paths):>3} path(s)  {subject[:48]}"
        print(line if not violations else line, file=sys.stdout if not violations else sys.stderr)
        for v in violations:
            print(f"          {v.path}\n              {v.reason}", file=sys.stderr)
        if violations:
            failed += 1
            if not stamped:
                inherited_failures += 1

    if failed:
        print(f"\nownership: FAIL, {failed} of {len(shas)} commit(s) wrote outside their lane.",
              file=sys.stderr)
        print("  A lane is scoped to a COMMIT here. Stamp the right actor at the phase that "
              "changes lane,\n  or record the change as a proposal and let a maintainer make "
              "it. The map is ownership.yaml.", file=sys.stderr)
        # THE CAUSE THIS MESSAGE NEVER NAMED, and it is the likeliest one when nothing stamped
        # itself. A routine stamps its actor, so an unstamped commit judged as a routine is
        # almost always a MAINTAINER session on a branch whose NAME claims that routine's lane.
        # A session working on the ask box called its branch claude/ask-effort-and-usage, which
        # is the prefix belonging to the ask box's archive routine, and every commit was then
        # judged against a lane the work was never in. The remedy is not a stamp and not a
        # proposal, both of which the paragraph above offers and neither of which can work,
        # since `human` may never be stamped on a prefixed branch and rightly so. It is to stop
        # claiming the lane.
        if inherited_failures and prefix_source:
            print(f"\n  {inherited_failures} of those stamped nothing and were judged as "
                  f"'{branch_actor}' because the branch\n"
                  f"  starts with '{prefix_source}'. If this is a maintainer session rather "
                  f"than that routine,\n"
                  f"  the branch NAME is the fault. Rename it to something matching no prefix "
                  f"in\n  ownership.yaml and every commit is judged as 'human', which owns "
                  f"every path.", file=sys.stderr)
        return 1
    print(f"\nownership: OK, {len(shas)} commit(s), {checked} path(s), every one inside the "
          f"lane its commit declared")
    return 0


def report(violations: list[Violation], actor: str, n_files: int) -> int:
    if not violations:
        print(f"ownership: OK, {n_files} path(s) all inside '{actor}'")
        return 0
    print(f"ownership: FAIL, {len(violations)} violation(s) for actor '{actor}'\n",
          file=sys.stderr)
    for v in violations:
        print(f"  {v.path}\n      {v.reason}", file=sys.stderr)
        if v.rule and v.rule.note:
            note = " ".join(v.rule.note.split())
            print(f"      why: {note}", file=sys.stderr)
    print("\n  An automation may not write outside its lane. If this change is genuinely "
          "needed,\n  record it as a proposal in the run record and let a maintainer session "
          "make it.\n  The map is ownership.yaml.", file=sys.stderr)
    return 1


# --------------------------------------------------------------------------- self-test
SELF_TEST_MAP = """
version: 1
actors:
  carousel: c
  gridwatch: g
  human: h
branch_actors:
  "claude/carousel-": carousel
  "gridwatch/": gridwatch
branch_also_allows:
  "claude/carousel-": [gridwatch, human]
rules:
  - path: "**"
    owner: human
  - path: "scripts/carousel/**"
    owner: carousel
  - path: "ledger/gridwatch/*.jsonl"
    owner: gridwatch
    append_only: true
  - path: "docs/**"
    generated: true
    rebuild_by: [carousel, gridwatch]
  - path: "docs/videos/index.html"
    owner: human
"""


def _self_test_per_commit() -> int:
    """The per-commit walk, against a real git history.

    This is the half that could not be tested without git actually producing commits, and it is
    the half the August 16th run needed: a `claude/carousel-` branch carrying one in-lane commit
    and one commit that changes lane the way Phase 17 does.
    """
    import io
    import contextlib

    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "r"
        repo.mkdir()
        git("init", "-q", "-b", "main", ".", cwd=repo)
        git("config", "user.email", "t@example.com", cwd=repo)
        git("config", "user.name", "t", cwd=repo)
        mapfile = repo / "ownership.yaml"
        mapfile.write_text(SELF_TEST_MAP, encoding="utf-8")
        (repo / "seed.txt").write_text("x\n", encoding="utf-8")
        git("add", "-A", cwd=repo)
        git("commit", "-qm", "seed", cwd=repo)
        base = git("rev-parse", "HEAD", cwd=repo).strip()

        def commit(path: str, body: str, msg: str, actor: str | None):
            p = repo / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body, encoding="utf-8")
            git("add", "-A", cwd=repo)
            full = msg if actor is None else f"{msg}\n\nActor: {actor}\n"
            git("commit", "-qm", full, cwd=repo)

        omap = OwnershipMap(yaml.safe_load(SELF_TEST_MAP))
        branch = "claude/carousel-2026-08-16"

        def run(rng="HEAD"):
            buf, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                rc = check_per_commit(omap, branch, f"{base}..{rng}", cwd=repo)
            return rc, buf.getvalue() + err.getvalue()

        # An unstamped commit inherits the branch's actor, so an ordinary run needs no trailer.
        commit("scripts/carousel/a.py", "a\n", "in lane, unstamped", None)
        rc, out = run()
        ok("an unstamped commit is judged as the branch's own actor", rc == 0, out)
        ok("...and says the actor was inherited", "inherited from the branch" in out, out)

        # THE CASE THE AUGUST 16TH RUN COULD NOT EXPRESS. A lane change mid-branch, stamped,
        # writing a file only the other actor owns. Under the old branch-wide check this was two
        # violations no matter how it was stamped.
        commit("ledger/gridwatch/s.jsonl", "1\n", "phase 17, changes lane", "gridwatch")
        rc, out = run()
        ok("a stamped commit changing lane mid-branch PASSES", rc == 0, out)

        # ...and the stamp buys nothing outside the declared set.
        commit("scripts/carousel/b.py", "b\n", "lying about the lane", "ask")
        rc, out = run()
        ok("a stamp the branch may not carry FAILS", rc == 1, out)
        ok("...and names what the branch is allowed", "Allowed here" in out, out)
        git("reset", "-q", "--hard", "HEAD~1", cwd=repo)

        # THE RED CASE THAT MATTERS MOST. `human` owns every path, so a run able to stamp it
        # would own the public record. The test map lists it in branch_also_allows on purpose.
        commit("CLAUDE.md", "rewritten\n", "stamping the one actor that owns everything", "human")
        rc, out = run()
        ok("a routine stamping 'human' is REFUSED", rc == 1, out)
        ok("...and is told why that actor is special",
           "switched off" in out or "owns every path" in out, out)
        git("reset", "-q", "--hard", "HEAD~1", cwd=repo)

        # An out-of-lane write inside a correctly stamped commit still fails, which is the
        # original guarantee and the one all of this must not have weakened.
        commit("CLAUDE.md", "rewritten\n", "in-lane stamp, out-of-lane file", "carousel")
        rc, out = run()
        ok("a correctly stamped commit writing out of lane still FAILS", rc == 1, out)
        git("reset", "-q", "--hard", "HEAD~1", cwd=repo)

        # MERGING THE BASE BRANCH IN. This is routine here: a run branch that sits open while
        # the gridwatch cron pushes to main has to merge main before it can land. Those commits
        # are another actor's and they must not read as this branch having written them.
        git("branch", "-q", "-f", "trunk", base, cwd=repo)
        git("checkout", "-q", "trunk", cwd=repo)
        commit("CLAUDE.md", "maintainer edit on trunk\n", "a maintainer edit on trunk", "human")
        new_base = git("rev-parse", "HEAD", cwd=repo).strip()
        git("checkout", "-q", "main", cwd=repo)
        git("merge", "-q", "--no-ff", "trunk", "-m", "Merge trunk", cwd=repo)

        buf, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            rc = check_per_commit(omap, branch, f"{new_base}..HEAD", cwd=repo)
        out = buf.getvalue() + err.getvalue()
        ok("merging the base branch in does not read as writing its files", rc == 0, out)

        # AND THE DIFF SPELLING OF THE SAME RANGE AGREES WITH THE REV-LIST SPELLING. CI writes
        # three dots. If the two spellings disagreed, CI would judge this branch for a commit
        # made on trunk by somebody else, which is the failure this normalisation exists for.
        buf, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            rc3 = check_per_commit(omap, branch, f"{new_base}...HEAD", cwd=repo)
        ok("...and three dots means the same set as two", rc3 == rc,
           buf.getvalue() + err.getvalue())

    return failures


def self_test() -> int:
    """Prove the gate can go RED. A gate that cannot fail proves nothing about what it guards."""
    omap = OwnershipMap(yaml.safe_load(SELF_TEST_MAP))
    cases = [
        # (actor, path, expect_violation, label)
        ("carousel",  "scripts/carousel/run.py",   False, "in-lane write passes"),
        ("gridwatch", "scripts/carousel/run.py",   True,  "cross-lane write FAILS"),
        ("carousel",  "CLAUDE.md",                 True,  "default rule protects the constitution"),
        ("human",     "CLAUDE.md",                 False, "maintainer may edit the constitution"),
        ("carousel",  "docs/index.html",           False, "rebuild_by may regenerate output"),
        ("ask",       "docs/index.html",           True,  "an actor absent from rebuild_by FAILS"),
        ("human",     "docs/index.html",           False, "a maintainer may regenerate output"),
        ("human",     "docs/videos/index.html",    False, "last match wins, carve-out overrides"),
        ("carousel",  "docs/videos/index.html",    True,  "carve-out revokes the broader grant"),
        ("gridwatch", "ledger/gridwatch/x.jsonl",  False, "owner may append"),
        ("carousel",  "ledger/gridwatch/x.jsonl",  True,  "non-owner may not touch the series"),
        # A maintainer owns everything, which is what the pre-commit hook has always said in
        # words. These two cases are what stopped the docket being seedable at all.
        ("human",     "scripts/carousel/run.py",   False, "a maintainer may write an automation's lane"),
        ("gridwatch", "scripts/carousel/run.py",   True,  "...but one automation still may not"),
    ]
    failures = 0
    for actor, path, expect_bad, label in cases:
        got = check(omap, actor, [path], check_appends=False)
        ok = bool(got) == expect_bad
        print(f"  {'ok  ' if ok else 'FAIL'}  {label}")
        if not ok:
            failures += 1
            print(f"        actor={actor} path={path} "
                  f"expected={'violation' if expect_bad else 'clean'} "
                  f"got={'violation' if got else 'clean'}", file=sys.stderr)

    # Glob discipline: `*` must not cross a separator, or every rule is wider than it reads.
    glob_cases = [
        ("scripts/*",       "scripts/a.py",              True),
        ("scripts/*",       "scripts/carousel/a.py",     False),
        ("scripts/**",      "scripts/carousel/a.py",     True),
        ("**",              "anything/at/all.txt",       True),
        (".claude/agents/carousel-*.md", ".claude/agents/carousel-scorer.md", True),
        (".claude/agents/carousel-*.md", ".claude/agents/dispatch-scorer.md", False),
    ]
    for pattern, path, expect in glob_cases:
        got = bool(glob_to_regex(pattern).match(path))
        ok = got == expect
        print(f"  {'ok  ' if ok else 'FAIL'}  glob {pattern!r} vs {path!r} -> {got}")
        if not ok:
            failures += 1

    # THE SHADOWED-RULE DETECTOR, replayed against the exact defect it was written for. The
    # real map carried these two rules in this order for a week. The strict one reads as
    # plainly as a rule can and was worth nothing, because the one below repealed it.
    repealed = OwnershipMap(yaml.safe_load("""
version: 1
actors: {carousel: c, human: h}
rules:
  - path: "**"
    owner: human
  - path: "scripts/site/**"
    owner: human
  - path: "scripts/site/**"
    owner: human
    rebuild_by: [carousel]
"""))
    shadows = repealed.shadowed()
    ok = [s[1] for s in shadows] == ["scripts/site/**"]
    print(f"  {'ok  ' if ok else 'FAIL'}  a rule repealed by a later duplicate is REPORTED")
    failures += 0 if ok else 1
    ok = "carousel" in repealed.rule_for("scripts/site/site_build.py").writers()
    print(f"  {'ok  ' if ok else 'FAIL'}  ...and the repeal was real, not cosmetic")
    failures += 0 if ok else 1

    # A carve-out narrower than the rule above it is the normal way this file works, and must
    # not be reported. Only a rule overridden across the WHOLE of its range is dead.
    carved = OwnershipMap(yaml.safe_load("""
version: 1
actors: {daily: d, human: h}
rules:
  - path: "**"
    owner: human
  - path: "scripts/site/**"
    owner: human
  - path: "scripts/site/gridwatch_page.py"
    owner: human
    rebuild_by: [daily]
"""))
    ok = carved.shadowed() == []
    print(f"  {'ok  ' if ok else 'FAIL'}  a narrower carve-out is NOT reported as shadowing")
    failures += 0 if ok else 1

    # And the shipped map itself, because the detector exists to guard that one.
    try:
        live = OwnershipMap.load(DEFAULT_MAP)
        live_shadows = live.shadowed()
        ok = live_shadows == []
        print(f"  {'ok  ' if ok else 'FAIL'}  the shipped ownership.yaml has no dead rules")
        if not ok:
            failures += 1
            for _, dead, by in live_shadows:
                print(f"        {dead!r} is repealed by {by!r}", file=sys.stderr)
    except Exception as exc:                                            # noqa: BLE001
        print(f"  FAIL  cannot read the shipped map: {exc}")
        failures += 1

    # Branch inference, including longest-prefix wins.
    for branch, expect in [("claude/carousel-2026-08-11", "carousel"),
                           ("gridwatch/2026-08-11", "gridwatch"),
                           ("main", None)]:
        got = omap.actor_for_branch(branch)
        ok = got == expect
        print(f"  {'ok  ' if ok else 'FAIL'}  branch {branch!r} -> {got}")
        if not ok:
            failures += 1

    # WHICH LANES A BRANCH MAY CARRY.
    allowed = omap.actors_allowed_on_branch("claude/carousel-2026-08-11")
    ok = allowed == {"carousel", "gridwatch"}
    print(f"  {'ok  ' if ok else 'FAIL'}  a branch carries its own actor plus what it declares"
          f"{'' if ok else '  ' + repr(allowed)}")
    failures += 0 if ok else 1

    # THE RED CASE FOR THE ONE ACTOR THAT WOULD SWITCH THE MAP OFF. The test map above lists
    # `human` in branch_also_allows on purpose. If it survives, an unattended run can own every
    # path by writing one line into a commit message, and every case above stops meaning
    # anything. This asserts the code drops it rather than the map being written carefully.
    ok = "human" not in allowed
    print(f"  {'ok  ' if ok else 'FAIL'}  ...but never 'human', even when the map asks for it")
    failures += 0 if ok else 1

    ok = omap.actors_allowed_on_branch("some/maintainer-branch") >= {"human"}
    print(f"  {'ok  ' if ok else 'FAIL'}  a branch matching no prefix is a maintainer session")
    failures += 0 if ok else 1

    failures += _self_test_per_commit()

    # The append-only guard against a real git history, because the line-level check is the
    # one piece that cannot be tested without git actually producing a diff.
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        git("init", "-q", "-b", "main", str(repo), cwd=repo.parent)
        git("config", "user.email", "t@example.com", cwd=repo)
        git("config", "user.name", "t", cwd=repo)
        series = repo / "ledger" / "gridwatch"
        series.mkdir(parents=True)
        (series / "x.jsonl").write_text('{"d":1}\n{"d":2}\n', encoding="utf-8")
        git("add", "-A", cwd=repo)
        git("commit", "-qm", "seed", cwd=repo)

        (series / "x.jsonl").write_text('{"d":1}\n{"d":2}\n{"d":3}\n', encoding="utf-8")
        git("add", "-A", cwd=repo)
        appended = deletes_lines("ledger/gridwatch/x.jsonl", None, True, cwd=repo)
        ok = appended is False
        print(f"  {'ok  ' if ok else 'FAIL'}  append to a series is allowed")
        failures += 0 if ok else 1
        git("commit", "-qm", "append", cwd=repo)

        (series / "x.jsonl").write_text('{"d":1}\n{"d":99}\n{"d":3}\n', encoding="utf-8")
        git("add", "-A", cwd=repo)
        rewrote = deletes_lines("ledger/gridwatch/x.jsonl", None, True, cwd=repo)
        ok = rewrote is True
        print(f"  {'ok  ' if ok else 'FAIL'}  rewriting a past reading is REFUSED")
        failures += 0 if ok else 1

    if failures:
        print(f"\nownership self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\nownership self-test: all passed (the gate can go red)")
    return 0


# --------------------------------------------------------------------------- cli
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--actor", help="daily | upgrade | gridwatch | ask | dispatch | human")
    ap.add_argument("--diff", help="git range, e.g. origin/main...HEAD")
    ap.add_argument("--diff-per-commit", metavar="RANGE",
                    help="walk the range one commit at a time, judging each against the "
                         "actor its 'Actor:' trailer declares. Needs --branch")
    ap.add_argument("--staged", action="store_true", help="check the staged change")
    ap.add_argument("--files", nargs="*", help="check these paths directly")
    ap.add_argument("--branch", help="infer the actor from this branch name")
    ap.add_argument("--map", default=str(DEFAULT_MAP))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    try:
        omap = OwnershipMap.load(Path(args.map))
    except Exception as exc:
        print(f"ownership: cannot read {args.map}: {exc}", file=sys.stderr)
        return 2

    if args.diff_per_commit:
        if not args.branch:
            print("ownership: --diff-per-commit needs --branch", file=sys.stderr)
            return 1
        return check_per_commit(omap, args.branch, args.diff_per_commit)

    actor = args.actor
    if not actor and args.branch:
        actor = omap.actor_for_branch(args.branch)
        if not actor:
            print(f"ownership: branch '{args.branch}' maps to no actor, treating as 'human'")
            actor = "human"
    if not actor:
        print("ownership: pass --actor or --branch", file=sys.stderr)
        return 1
    if omap.actors and actor not in omap.actors:
        print(f"ownership: unknown actor '{actor}', known: {', '.join(omap.actors)}",
              file=sys.stderr)
        return 1

    try:
        if args.files is not None:
            paths = list(args.files)
        elif args.staged or args.diff:
            paths = changed_files(args.diff, args.staged)
        else:
            print("ownership: pass --diff, --staged or --files", file=sys.stderr)
            return 1
    except RuntimeError as exc:
        print(f"ownership: {exc}", file=sys.stderr)
        return 2

    if not paths:
        print(f"ownership: OK, nothing changed")
        return 0

    return report(check(omap, actor, paths, args.diff, args.staged), actor, len(paths))


if __name__ == "__main__":
    sys.exit(main())
