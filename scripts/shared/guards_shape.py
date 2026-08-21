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
  a page check whose severities are wired wrong, which is checked BY RUNNING THE SHELL

THE LAST ONE IS A DIFFERENT KIND OF CHECK and the reason is worth stating. The two instrument
page checks report three outcomes now. A page reading wrong is exit 2 and must stay a warning,
because an instrument failing a build over presentation is a gate somebody eventually removes.
An instrument that has STOPPED is exit 3 and must fail, because a collector nobody notices is
dead is the one irreversible failure this project has.

That contract lives in a `case` block inside a YAML string, which is the least checked kind of
code in this repository: no linter reads it, no test imports it, and it is edited by whoever is
adding a step next to it. Grepping it for `exit 3` would be a gate on spelling. So this EXTRACTS
the block, substitutes a stub for the checker that exits with a chosen code, RUNS it under bash,
and asserts the code that comes out. Wire 3 to a warning and this goes red on the behaviour.

    guards_shape.py --self-test
    guards_shape.py
"""
from __future__ import annotations

import argparse
import re
import subprocess
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


# The checker invocation inside a step's shell, which is what gets stubbed out. Matched on the
# filename rather than the whole path so moving the scripts does not quietly disarm this.
PAGECHECK = re.compile(
    r"python3?\s+\S*(?:grid|water)watch_pagecheck\.py(?!\s+--self-test)")

# What each exit code from a page check must do to the STEP. This table is the contract, and
# every entry has a reason that is written down in the checkers themselves.
#
#   0  clean, and the step passes
#   2  the page reads wrong. ADVISORY, so the step passes and says so out loud
#   3  an instrument has stopped. HALTING, so the step fails
#   1  the checker itself broke, which was always a failure
SEVERITIES = {0: 0, 2: 0, 3: 3, 1: 1}

# The wiring those four codes are supposed to have, written once. The self-test builds its red
# cases by breaking this, so a fixture cannot quietly stop resembling the real step.
PAGE_RUN = """code=0
python3 scripts/gridwatch/waterwatch_pagecheck.py || code=$?
case "$code" in
  0) ;;
  2) echo "::warning::the page wants attention" ;;
  3) echo "::error::the instrument has stopped"
     exit 3 ;;
  *) exit "$code" ;;
esac"""


def severity_problems(doc: dict) -> list[str]:
    """Run each page check step's own shell against a stubbed checker and grade the mapping.

    Not a grep. A gate that reads a shell block for the string `exit 3` passes the day somebody
    writes `exit $((1 + 2))` and fails the day somebody adds the words to a comment, and neither
    of those is the question. The question is what the STEP does when the checker says 3, so the
    step is asked.
    """
    out: list[str] = []
    steps = [(job, st) for job, spec in (doc.get("jobs") or {}).items()
             for st in (spec.get("steps") or [])
             if isinstance(st.get("run"), str) and PAGECHECK.search(st["run"])]
    if not steps:
        return ["no step in this workflow runs an instrument page check; the two pages that "
                "nobody reads are now checked by nobody"]

    for job, st in steps:
        name = st.get("name") or "(unnamed)"
        for code, want in SEVERITIES.items():
            # `bash -e` is what GitHub gives a `run:` block by default, so it is what the block
            # is tested under. A block that only works without -e is a block that breaks the
            # day somebody sets a shell explicitly.
            script = PAGECHECK.sub(f"( exit {code} )", st["run"])
            r = subprocess.run(["bash", "-e", "-c", script], capture_output=True, text=True)
            if r.returncode != want:
                out.append(f"{job}/{name!r} maps checker exit {code} to step exit "
                           f"{r.returncode}, and it must be {want}"
                           + ("; an instrument that has STOPPED would go green"
                              if code == 3 and r.returncode == 0 else ""))
            if code == 2 and "::warning::" not in (r.stdout + r.stderr):
                out.append(f"{job}/{name!r} passes on exit 2 without a warning annotation, so "
                           f"a page reading wrong leaves no trace anybody will ever see")
            if code == 3 and want == r.returncode and "::error::" not in (r.stdout + r.stderr):
                out.append(f"{job}/{name!r} fails on exit 3 without an error annotation, so "
                           f"the log says a step failed and never says which instrument")
    return out


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

    out.extend(severity_problems(doc))
    return out


def self_test() -> int:
    failures = 0

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    # The page check step, wired the way the real workflow wires it. Every shape fixture below
    # carries one, because `problems` grades the severities too and a workflow with no
    # instrument check is itself a finding.
    PAGE_STEP = {"name": "the page", "run": PAGE_RUN}

    good = {"jobs": {
        "gates": {"steps": [{"run": "true"}, PAGE_STEP]},
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

    ghost = {"jobs": {"gates": {"steps": [{"run": "true"}, PAGE_STEP]},
                      AGGREGATE: {"needs": ["gates", "vanished"], "steps": [{"run": "true"}]}}}
    check("waiting on a job that does not exist is caught",
          any("not a job here" in x for x in problems(ghost)), str(problems(ghost)))

    working = {"jobs": {"gates": {"steps": [{"run": "true"}, PAGE_STEP]},
                        AGGREGATE: {"needs": ["gates"],
                                    "steps": [{"run": "echo"}, {"run": "pytest"}]}}}
    check("real work hiding in the aggregate is caught",
          any("run steps" in x for x in problems(working)), str(problems(working)))

    # ------------------------------------------------------------- THE SEVERITY WIRING
    # Each fixture below is a plausible way to write that step, and all but the first are
    # wrong. They are RUN, not read.
    def wf(run: str) -> dict:
        return {"jobs": {"gates": {"steps": [{"name": "the page", "run": run}]},
                         AGGREGATE: {"needs": ["gates"], "steps": [{"run": "echo ok"}]}}}

    check("a correctly wired page check reports nothing",
          not severity_problems(wf(PAGE_RUN)), str(severity_problems(wf(PAGE_RUN))))

    # THE DEFECT THIS EXISTS FOR, and it is close to the shape the step was written in for
    # months: one advisory branch and a catch-all that swallows the rest. Read quickly it looks
    # careful. What it does is turn a stopped instrument into a green build.
    swallow = wf('python3 scripts/gridwatch/waterwatch_pagecheck.py || { code=$?; echo "::warning::wants attention"; exit 0; }')
    pr = severity_problems(swallow)
    check("a step that swallows every non-zero code is CAUGHT",
          any("maps checker exit 3 to step exit 0" in x for x in pr), str(pr))
    check("...and it says plainly what that costs",
          any("would go green" in x for x in pr), str(pr))

    # The inverse, and it is the one that gets a gate deleted rather than a page fixed. Fail on
    # everything and the first drifted sentence blocks the build, so somebody removes the step.
    pr = severity_problems(wf("python3 scripts/gridwatch/waterwatch_pagecheck.py"))
    check("a step that fails on a page merely READING WRONG is caught",
          any("maps checker exit 2 to step exit 2" in x for x in pr), str(pr))

    pr = severity_problems(wf(PAGE_RUN.replace(
        '  2) echo "::warning::the page wants attention" ;;', "  2) ;;")))
    check("passing on exit 2 with no annotation is caught",
          any("without a warning annotation" in x for x in pr), str(pr))

    pr = severity_problems(wf(PAGE_RUN.replace(
        '  3) echo "::error::the instrument has stopped"\n     exit 3 ;;', "  3) exit 3 ;;")))
    check("failing on exit 3 with no annotation is caught",
          any("without an error annotation" in x for x in pr), str(pr))

    # THE CHECKER ITSELF BREAKING is not a severity, it is a broken checker, and it has always
    # been a failure. A step that treats exit 1 as a finding has stopped checking anything.
    pr = severity_problems(wf(PAGE_RUN.replace(
        '  *) exit "$code" ;;', '  *) echo "::warning::wants attention" ;;')))
    check("a step that treats a BROKEN checker as advisory is caught",
          any("maps checker exit 1 to step exit 0" in x for x in pr), str(pr))

    # AND THE STEP GOING MISSING ENTIRELY, which is the failure neither branch above can see,
    # because a rule about how a step behaves says nothing when there is no step.
    none = {"jobs": {"gates": {"steps": [{"run": "echo hello"}]},
                     AGGREGATE: {"needs": ["gates"], "steps": [{"run": "echo ok"}]}}}
    check("a workflow that checks neither instrument page is caught",
          any("checked by nobody" in x for x in severity_problems(none)),
          str(severity_problems(none)))

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
