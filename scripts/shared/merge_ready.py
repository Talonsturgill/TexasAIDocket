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

Measured on 2026-09-13. `gridwatch.yml` runs at 14:00 and 20:00 UTC and each run rewrites about
126 files under `docs/`. `pages.yml` runs every two hours. A daily run regenerates the WHOLE of
`docs/`, about a thousand files, because the site is a pure function of the ledgers. So a run
branch and `main` touch the same generated files within hours of each other, every day, and the
branch goes un-mergeable on its own with nobody doing anything wrong.

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


def git(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd or REPO_ROOT),
                          capture_output=True, text=True)


def conflicts(base: str, branch: str, cwd: Path | None = None):
    """(mergeable, conflicted_paths). Never touches the working tree.

    `--name-only` prints the written tree's oid on the first line and then the conflict report,
    so the oid is dropped and only `CONFLICT (...): ... in <path>` lines are read. Parsing the
    prose is deliberate: the porcelain here is stable and the alternative is a real checkout.
    """
    r = git("merge-tree", "--write-tree", "--name-only", base, branch, cwd=cwd)
    if r.returncode == 0:
        return True, []
    if r.returncode > 1 and "CONFLICT" not in r.stdout:
        raise SystemExit(f"merge_ready: git could not compare {base} and {branch}: "
                         f"{(r.stderr or r.stdout).strip()[:300]}")
    paths = []
    for line in r.stdout.splitlines():
        if line.startswith("CONFLICT") and " in " in line:
            p = line.rsplit(" in ", 1)[1].strip()
            if p and p not in paths:
                paths.append(p)
    return False, paths


def split(paths):
    gen = [p for p in paths if p.startswith(GENERATED_PREFIXES)]
    authored = [p for p in paths if not p.startswith(GENERATED_PREFIXES)]
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

        # AND IT GOES GREEN AGAIN once the base is merged and the generated file rebuilt, which
        # is the whole cure this gate points at.
        git("merge", "main", "-q", "--no-commit", cwd=d)
        (d / "docs" / "index.html").write_text("rebuilt on top of both\n")
        (d / "ledger.json").write_text('{"items": 3}\n')
        git("add", "-A", cwd=d); git("commit", "-qm", "merge main and rebuild", cwd=d)
        okc, paths = conflicts("main", "run", cwd=d)
        ok("...and merging the base and rebuilding clears it", okc and not paths, str(paths))

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
        remote, _, ref = args.base.partition("/")
        git("fetch", remote, ref or "main")
    return report(args.base, args.branch)


if __name__ == "__main__":
    raise SystemExit(main())
