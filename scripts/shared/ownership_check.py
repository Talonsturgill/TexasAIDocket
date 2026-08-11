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

    ownership_check.py --actor carousel --diff origin/main...HEAD
    ownership_check.py --actor gridwatch --staged
    ownership_check.py --actor carousel --files docs/index.html ledger/docket.json
    ownership_check.py --self-test

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
        """Every actor allowed to produce a change to this path."""
        w = list(self.rebuild_by)
        if self.owner and self.owner not in w:
            w.append(self.owner)
        return w


class OwnershipMap:
    def __init__(self, doc: dict):
        self.actors = list((doc.get("actors") or {}).keys())
        self.branch_actors = dict(doc.get("branch_actors") or {})
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

    def actor_for_branch(self, branch: str) -> str | None:
        best = None
        for prefix, actor in self.branch_actors.items():
            if branch.startswith(prefix) and (best is None or len(prefix) > len(best[0])):
                best = (prefix, actor)
        return best[1] if best else None


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
        ("human",     "docs/index.html",           True,  "an actor absent from rebuild_by FAILS"),
        ("human",     "docs/videos/index.html",    False, "last match wins, carve-out overrides"),
        ("carousel",  "docs/videos/index.html",    True,  "carve-out revokes the broader grant"),
        ("gridwatch", "ledger/gridwatch/x.jsonl",  False, "owner may append"),
        ("carousel",  "ledger/gridwatch/x.jsonl",  True,  "non-owner may not touch the series"),
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

    # Branch inference, including longest-prefix wins.
    for branch, expect in [("claude/carousel-2026-08-11", "carousel"),
                           ("gridwatch/2026-08-11", "gridwatch"),
                           ("main", None)]:
        got = omap.actor_for_branch(branch)
        ok = got == expect
        print(f"  {'ok  ' if ok else 'FAIL'}  branch {branch!r} -> {got}")
        if not ok:
            failures += 1

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
    ap.add_argument("--actor", help="carousel | gridwatch | ask | dispatch | human")
    ap.add_argument("--diff", help="git range, e.g. origin/main...HEAD")
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
