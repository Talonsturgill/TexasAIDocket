#!/usr/bin/env python3
"""merge_ready.py — can this branch still be merged, asked as an exit code.

WHY THIS EXISTS. 2026-09-13, and it cost two days of shipping.

The September 12th and September 13th runs both finished their work, pushed, opened a pull
request, and never merged. Neither run could say why. Both reported that CI had not started, and
the September 13th run wrote a confident account blaming the credentials the session was using,
built out of the one lever that returned an error message. It was wrong.

**A `pull_request` workflow runs against the pull request's MERGE REF, and GitHub cannot build a
merge ref for a conflicted pull request.** So a conflicted branch does not get a red run. It gets
NO RUN AT ALL, on the pull request and on every push after it, and the pull request page shows an
empty check list rather than a failure. The owner said it plainly: *"the reason u dont run the ci
is because #301 is dirty, u keep not being able to run ci cause its dirty but u dont see that its
dirty then u settlo on some other reason, which is wrong, u should in those cases just resolves
the issues, then the ci will be able to run like normal."*

THE CONFLICT IS NOT BAD LUCK. IT IS SCHEDULED.

Measured on 2026-09-13, and corrected the same evening after a review bot checked the inventory.
FOUR cron workflows run `site_build` and commit `docs/` to `main`, eight pushes a day between
them: `news.yml` four times daily, `gridwatch.yml` twice, `datacenters.yml` and `generators.yml`
once each. A daily run regenerates the WHOLE of `docs/`, about a thousand files, because the site
is a pure function of the ledgers. So a run branch and `main` touch the same generated files
within hours of each other, every day, and the branch goes un-mergeable with nobody doing
anything wrong.

NOT writers, and the first cut wrongly counted both: `pages.yml` has `contents: read` and only
deploys what is already committed, and `queuewatch.yml` stages its ledger and raw files alone.

That is why this is a checker and not a paragraph in the routine. The condition is invisible from
inside a session, it arrives on a timer rather than in response to anything the run did, and the
symptom it produces is SILENCE, which is the one signal a run reads as nothing being wrong.

WHAT IT ASKS, AND WHY IT IS PHRASED THIS WAY

Not "did CI pass", which is `guards.yml`'s question and needs the network. This asks the local
question whose answer decides whether CI can run at all: **does this branch still merge into its
base.** `git merge-tree --write-tree` answers it without touching the working tree, without a
checkout, and without a remote round trip beyond the fetch the caller already did.

It sorts the conflicts, because the two kinds need different work and a run that cannot tell them
apart will hand-edit a generated file:

    GENERATED   anything under `docs/`. Never resolved by hand. Rebuild with site_build.py and
                the conflict resolves itself, which is what `CLAUDE.md` already requires.
    AUTHORED    everything else. A ledger, a script, a run record. These are read and merged.

A branch with 400 generated conflicts and no authored ones is ten minutes of work. A branch with
one authored conflict in `ledger/docket.json` may be an editorial decision, and on 2026-09-13 it
was exactly that: `main` had corrected an item's November 3rd date from a comment deadline to an
election day, and both runs' re-verify lines still called it a comment window.

    merge_ready.py                       # the current branch against origin/main
    merge_ready.py --base origin/main --branch HEAD
    merge_ready.py --fetch               # refresh the base ref first
    merge_ready.py --self-test
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Paths the build writes wholesale. A conflict here is never resolved by hand.
GENERATED_PREFIXES = ("docs/",)

# EXCEPT THESE, WHICH LIVE UNDER A GENERATED PREFIX AND ARE NOT GENERATED. `ownership.yaml`
# gives `docs/videos/videos.json` to `dispatch`, append-only, with the note that no build in
# this repo may write, reformat or delete it and `site_build` copies it through verbatim. So
# "rebuild and the conflict resolves itself" is false for it in the one way that matters: a
# rebuild would carry the conflicted bytes straight through, markers and all, or clobber a feed
# another repository publishes. It is read and merged by hand like any authored file.
GENERATED_EXCEPTIONS = ("docs/videos/videos.json",)


def git(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd or REPO_ROOT),
                          capture_output=True, text=True)


def conflicts(base: str, branch: str, cwd: Path | None = None):
    """(mergeable, conflicted_paths). Never touches the working tree.

    The paths come from `--name-only -z`'s FILENAME BLOCK rather than from its prose report.
    See the comment on the parse for what reading the prose cost.
    """
    r = git("merge-tree", "--write-tree", "--name-only", "-z", base, branch, cwd=cwd)
    if r.returncode == 0:
        return True, []
    if r.returncode > 1 and "CONFLICT" not in r.stdout:
        raise SystemExit(f"merge_ready: git could not compare {base} and {branch}: "
                         f"{(r.stderr or r.stdout).strip()[:300]}")
    # THE FILENAME BLOCK, NOT THE PROSE. `--name-only` prints the written tree's oid, then one
    # NUL separated filename per conflicted path, then the human readable report. The first cut
    # read the report instead, splitting each `CONFLICT (...)` line on its last " in ", and a
    # modify/delete conflict says "Version run of docs/a.html left in tree." So the path came out
    # as `tree.`, which starts with neither prefix and was therefore filed as AUTHORED. A wrong
    # path is worse than a missing one: it sends a run to read a file that does not exist while
    # the real conflict goes unnamed. `-z` also survives a filename with a space or a newline.
    head, _, _rest = r.stdout.partition("\0\0")
    parts = head.split("\0")
    paths = [p for p in parts[1:] if p.strip()]
    if not paths:                       # no filename block, fall back rather than report clean
        for line in r.stdout.splitlines():
            if line.startswith("CONFLICT (") and "): " in line:
                tail = line.split("): ", 1)[1]
                cand = tail.split(" deleted in ")[0].split(" in ")[0].strip()
                if cand and cand not in paths:
                    paths.append(cand)
    seen, ordered = set(), []
    for p in paths:
        if p not in seen:
            seen.add(p)
            ordered.append(p)
    return False, ordered


def is_generated(path: str) -> bool:
    return path.startswith(GENERATED_PREFIXES) and path not in GENERATED_EXCEPTIONS


def split(paths):
    gen = [p for p in paths if is_generated(p)]
    authored = [p for p in paths if not is_generated(p)]
    return gen, authored


def report(base: str, branch: str, cwd: Path | None = None) -> int:
    ok, paths = conflicts(base, branch, cwd=cwd)
    if ok:
        print(f"merge_ready: {branch} merges cleanly into {base}. "
              f"A pull request from it has a merge ref, so CI can run")
        return 0
    gen, authored = split(paths)
    print(f"merge_ready: {branch} does NOT merge into {base}. {len(paths)} conflicted path(s)",
          file=sys.stderr)
    print(f"  GitHub cannot build a merge ref for a conflicted pull request, so `guards.yml` will "
          f"not run AT ALL. Not red. Absent. Read that empty check list as this, and never as a "
          f"permissions problem", file=sys.stderr)
    if gen:
        print(f"\n  {len(gen)} generated, under {' '.join(GENERATED_PREFIXES)}. Merge the base in "
              f"and REBUILD rather than resolving these by hand:", file=sys.stderr)
        for p in gen[:5]:
            print(f"    {p}", file=sys.stderr)
        if len(gen) > 5:
            print(f"    ... and {len(gen) - 5} more", file=sys.stderr)
    if authored:
        print(f"\n  {len(authored)} AUTHORED, and each of these is read rather than regenerated:",
              file=sys.stderr)
        for p in authored:
            print(f"    {p}", file=sys.stderr)
    else:
        print(f"\n  No authored conflict. Every one is generated, so this is a base merge and a "
              f"rebuild", file=sys.stderr)
    return 1


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    import tempfile
    bad = 0

    def ok(label, cond, extra=""):
        nonlocal bad
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            bad += 1

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        git("init", "-q", "-b", "main", str(d), cwd=d.parent)
        git("config", "user.email", "t@example.com", cwd=d)
        git("config", "user.name", "T", cwd=d)
        (d / "docs").mkdir()
        (d / "docs" / "index.html").write_text("base\n")
        (d / "ledger.json").write_text('{"items": 1}\n')
        git("add", "-A", cwd=d); git("commit", "-qm", "base", cwd=d)

        git("checkout", "-qb", "run", cwd=d)
        (d / "runs.md").write_text("a run record\n")
        git("add", "-A", cwd=d); git("commit", "-qm", "run work", cwd=d)

        okc, paths = conflicts("main", "run", cwd=d)
        ok("a branch that only adds files merges cleanly", okc and not paths, str(paths))

        # THE REPLAY. main moves under the branch the way a cron push does, and both sides
        # rewrite the same generated file.
        git("checkout", "-q", "main", cwd=d)
        (d / "docs" / "index.html").write_text("the cron rebuilt this\n")
        git("commit", "-qam", "gridwatch: settled day", cwd=d)
        git("checkout", "-q", "run", cwd=d)
        (d / "docs" / "index.html").write_text("the run rebuilt this\n")
        git("commit", "-qam", "site rebuild", cwd=d)

        okc, paths = conflicts("main", "run", cwd=d)
        ok("a generated file rewritten on both sides conflicts", not okc and paths, str(paths))
        gen, authored = split(paths)
        ok("...and it is sorted as generated, not authored",
           gen == ["docs/index.html"] and not authored, f"gen={gen} authored={authored}")
        ok("...and the report says do not merge", report("main", "run", cwd=d) == 1)

        # AND AN AUTHORED CONFLICT IS CALLED WHAT IT IS, because it needs a person's judgement.
        git("checkout", "-q", "main", cwd=d)
        (d / "ledger.json").write_text('{"items": 2}\n')
        git("commit", "-qam", "a correction on main", cwd=d)
        git("checkout", "-q", "run", cwd=d)
        (d / "ledger.json").write_text('{"items": 3}\n')
        git("commit", "-qam", "the run's own edit", cwd=d)
        _okc, paths = conflicts("main", "run", cwd=d)
        gen, authored = split(paths)
        ok("an authored conflict is reported separately from the generated ones",
           "ledger.json" in authored and "docs/index.html" in gen, f"authored={authored}")

        # A MODIFY/DELETE CONFLICT NAMES A REAL PATH. Codex found this on PR 305: the first cut
        # read the prose report and split on its last " in ", and modify/delete says "Version run
        # of docs/a.html left in tree.", so the path came out as `tree.` and was filed AUTHORED.
        git("checkout", "-q", "main", cwd=d)
        (d / "gone.json").write_text("base\n")
        (d / "docs" / "gone.html").write_text("base\n")
        git("add", "-A", cwd=d); git("commit", "-qm", "two files to fight over", cwd=d)
        git("checkout", "-q", "run", cwd=d); git("merge", "main", "-q", cwd=d)
        (d / "gone.json").write_text("the run edits it\n")
        (d / "docs" / "gone.html").write_text("the run edits it\n")
        git("commit", "-qam", "run edits both", cwd=d)
        git("checkout", "-q", "main", cwd=d)
        (d / "gone.json").unlink(); (d / "docs" / "gone.html").unlink()
        git("commit", "-qam", "main deletes both", cwd=d)
        _okc, paths = conflicts("main", "run", cwd=d)
        ok("a modify/delete conflict names the real paths",
           "gone.json" in paths and "docs/gone.html" in paths, str(paths))
        ok("...and no prose fragment is mistaken for one",
           not any(x in paths for x in ("tree.", "run", "main")), str(paths))
        gen, authored = split(paths)
        ok("...and each lands on the right side",
           "docs/gone.html" in gen and "gone.json" in authored, f"gen={gen} authored={authored}")
        git("checkout", "-q", "main", cwd=d); git("reset", "-q", "--hard", "HEAD~2", cwd=d)
        git("checkout", "-q", "run", cwd=d); git("reset", "-q", "--hard", "HEAD~2", cwd=d)

        # AND IT GOES GREEN AGAIN once the base is merged and the generated file rebuilt, which
        # is the whole cure this gate points at.
        git("merge", "main", "-q", "--no-commit", cwd=d)
        (d / "docs" / "index.html").write_text("rebuilt on top of both\n")
        (d / "ledger.json").write_text('{"items": 3}\n')
        git("add", "-A", cwd=d); git("commit", "-qm", "merge main and rebuild", cwd=d)
        okc, paths = conflicts("main", "run", cwd=d)
        ok("...and merging the base and rebuilding clears it", okc and not paths, str(paths))

    # THE DISPATCH FEED IS NOT GENERATED, whatever prefix it sits under. `ownership.yaml` gives
    # it to another repository, append-only, and a rebuild would carry conflicted bytes through.
    ok("docs/videos/videos.json is not classified as generated",
       not is_generated("docs/videos/videos.json"),
       "the dispatch feed would be sent for a rebuild that cannot resolve it")
    ok("...while an ordinary page under docs/ still is", is_generated("docs/index.html"))

    # A FETCH THAT FAILED MUST NOT REPORT READINESS off a stale ref, which is the one way this
    # gate could manufacture the false green it exists to prevent.
    import subprocess as _sp
    _r = _sp.run([sys.executable, str(Path(__file__).resolve()),
                  "--fetch", "--base", "no-such-remote/main"],
                 capture_output=True, text=True, cwd=str(REPO_ROOT))
    ok("a failed --fetch exits non-zero rather than comparing a stale ref",
       _r.returncode != 0, f"exit {_r.returncode}: {(_r.stdout + _r.stderr)[:200]}")
    ok("...and says why", "stale" in (_r.stdout + _r.stderr), (_r.stdout + _r.stderr)[:200])

    print("\nmerge_ready self-test: " + ("all passed" if not bad else f"{bad} FAILED"))
    return 1 if bad else 0


def main() -> int:
    a = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    a.add_argument("--base", default="origin/main")
    a.add_argument("--branch", default="HEAD")
    a.add_argument("--fetch", action="store_true", help="refresh the base ref first")
    a.add_argument("--self-test", action="store_true")
    args = a.parse_args()
    if args.self_test:
        return self_test()
    if args.fetch:
        # A FETCH THAT FAILED AND WAS IGNORED IS THIS GATE'S WORST OUTCOME. The comparison would
        # fall back to a stale `origin/main`, print that the branch merges cleanly, and hand back
        # exit 0 for a branch that conflicts with the real base. A gate built to stop a false
        # green must not manufacture one out of a dropped network.
        remote, _, ref = args.base.partition("/")
        f = git("fetch", remote, ref or "main")
        if f.returncode != 0:
            print(f"merge_ready: could not fetch {args.base}, so the comparison would be against "
                  f"a stale ref and its answer would mean nothing. "
                  f"{(f.stderr or f.stdout).strip()[:300]}", file=sys.stderr)
            return 2
    return report(args.base, args.branch)


if __name__ == "__main__":
    raise SystemExit(main())
