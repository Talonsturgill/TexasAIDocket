#!/usr/bin/env python3
"""guards_shape.py — the guard workflow's own wiring, checked rather than remembered.

WHY THIS EXISTS

`guards.yml` was one job called `guards` and is several now, split because six steps were
ninety percent of a fourteen minute wall clock and none of them waited on each other. The split
is a clear win and it introduces exactly one new way to be wrong, so that way is checked here.

A REQUIRED STATUS CHECK IS MATCHED BY NAME. A protected branch waits for a check called
`guards`, and if the job that carries that name stops existing, or stops depending on one of
the real jobs, the branch is no longer waiting for anything. The failure is silent and it is
silent in the worst direction: the merge goes green while a whole job is red or absent.

That is the same defect this repository already collects under a name. UPGRADE_BACKLOG's item 6
is a list of gates that exist and are connected to nothing, and GATE_LESSONS is a list of green
suites that were wrong about the product. A job nobody waits on is a gate connected to nothing,
one level up from the usual case, because the thing left unconnected is a whole job rather than
a script.

WHAT IT REFUSES

  a real job that the aggregate does not wait on
  an aggregate that has gone missing or been renamed
  a job with no steps, which passes by having nothing to do
  an aggregate that does real work, because then it is a job rather than a gate on jobs

    guards_shape.py --self-test
    guards_shape.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:                                                  # pragma: no cover
    print("guards_shape: PyYAML missing (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "guards.yml"

# The name a protected branch waits on. Changing it is a branch-protection change and not a
# workflow change, so it is written here rather than inferred from whatever happens to be last.
AGGREGATE = "guards"


def problems(doc: dict) -> list[str]:
    """Everything wrong with the workflow's shape, in the order it would bite."""
    out: list[str] = []
    jobs = doc.get("jobs") or {}
    if not jobs:
        return ["the workflow declares no jobs at all"]

    agg = jobs.get(AGGREGATE)
    if agg is None:
        return [f"no job named {AGGREGATE!r}; a required status check matches by name, so a "
                f"protected branch is now waiting for a check that never reports"]

    needs = agg.get("needs") or []
    if isinstance(needs, str):
        needs = [needs]
    real = [n for n in jobs if n != AGGREGATE]

    missing = [n for n in real if n not in needs]
    if missing:
        out.append(f"{AGGREGATE} does not wait on {', '.join(sorted(missing))}; those jobs can "
                   f"go red while the required check goes green")

    unknown = [n for n in needs if n not in jobs]
    if unknown:
        out.append(f"{AGGREGATE} waits on {', '.join(sorted(unknown))}, which is not a job here")

    for name, job in jobs.items():
        steps = job.get("steps") or []
        if not steps:
            out.append(f"job {name!r} has no steps, so it passes by having nothing to do")

    # THE AGGREGATE MUST NOT BE A PLACE WORK HIDES. Its whole value is that it is a name with
    # dependencies behind it. A real check living in there runs AFTER everything else and
    # serialises the thing the split exists to parallelise.
    agg_runs = [s for s in (agg.get("steps") or []) if s.get("run")]
    if len(agg_runs) > 1:
        out.append(f"{AGGREGATE} carries {len(agg_runs)} run steps; it is a gate on the other "
                   f"jobs and belongs in one of them if it does work")
    return out


def self_test() -> int:
    failures = 0

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    good = {"jobs": {
        "gates": {"steps": [{"run": "true"}]},
        "build": {"steps": [{"run": "true"}]},
        AGGREGATE: {"needs": ["gates", "build"], "steps": [{"run": "echo ok"}]}}}
    check("a correctly wired workflow reports nothing", not problems(good), str(problems(good)))

    # THE DEFECT THIS EXISTS FOR. A job added and not wired in.
    orphan = {"jobs": {**good["jobs"], "browser": {"steps": [{"run": "true"}]}}}
    p = problems(orphan)
    check("a job the aggregate does not wait on is CAUGHT",
          any("does not wait on browser" in x for x in p), str(p))

    gone = {"jobs": {"gates": {"steps": [{"run": "true"}]}}}
    check("an aggregate that has been renamed away is caught",
          any("required status check" in x for x in problems(gone)), str(problems(gone)))

    empty = {"jobs": {**good["jobs"], "hollow": {"steps": []}}}
    check("a job with no steps is caught",
          any("nothing to do" in x for x in problems(empty)), str(problems(empty)))

    ghost = {"jobs": {"gates": {"steps": [{"run": "true"}]},
                      AGGREGATE: {"needs": ["gates", "vanished"], "steps": [{"run": "true"}]}}}
    check("waiting on a job that does not exist is caught",
          any("not a job here" in x for x in problems(ghost)), str(problems(ghost)))

    working = {"jobs": {"gates": {"steps": [{"run": "true"}]},
                        AGGREGATE: {"needs": ["gates"],
                                    "steps": [{"run": "echo"}, {"run": "pytest"}]}}}
    check("real work hiding in the aggregate is caught",
          any("run steps" in x for x in problems(working)), str(problems(working)))

    # AND THE REAL FILE, which is the only reason any of the above matters.
    if WORKFLOW.exists():
        live = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
        check("the committed workflow is wired correctly", not problems(live),
              "; ".join(problems(live)))

    if failures:
        print(f"\nguards_shape self-test: {failures} FAILED")
        return 1
    print("\nguards_shape self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not WORKFLOW.exists():
        print(f"guards_shape: {WORKFLOW} is missing", file=sys.stderr)
        return 2
    found = problems(yaml.safe_load(WORKFLOW.read_text(encoding="utf-8")))
    if found:
        print("guards workflow shape:", file=sys.stderr)
        for f in found:
            print(f"  - {f}", file=sys.stderr)
        return 1
    jobs = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]
    print(f"guards shape ok: {len(jobs) - 1} job(s) behind the {AGGREGATE!r} check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
