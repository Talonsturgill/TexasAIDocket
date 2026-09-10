#!/usr/bin/env python3
"""gate_wiring.py — a gate that nothing runs is a gate that is red, and nobody finds out.

THE DEFECT THIS EXISTS FOR (2026-09-10, carousel no. 20)

`construction_check.py` appears in `.github/workflows/guards.yml` in no form and in
`prompts/daily_routine.md` in no form. The run reached scoring round 3 before it was run once,
by a session that went looking rather than by anything in the machine, and it had been RED the
whole time at 5 of 9 frames carrying one primitive against a threshold of half. The finding was
real: run back over the four decks before it the same gate returns 2, 1, 4 and 1.

`verbatim_check.py` had the same gap and it cost a second thing. Its own `--self-test` was red on
a clean checkout of `main`, and had been for days, because its last assertion was pinned to "the
newest shipped deck" and the newest deck moves every night. Nothing opened the file, so nothing
noticed. Two gates, one omission, and the omission is the same in both.

WHY NOT JUST ADD TWO NAMES TO TWO LISTS

Because both lists are hand maintained and both are `human` owned. The actor that WRITES a
carousel gate is `upgrade`, and `upgrade` can edit neither `.github/workflows/**` nor
`prompts/**`, so the actor that builds a gate is structurally unable to connect it. That is not
a hypothetical: `shipped_check.py`'s own header records three gates that waited on a maintainer,
and its `g_ledgers` docstring says in as many words that this is why the registry lives there.
Adding two names fixes today and leaves the mechanism that produced today intact.

WHAT COUNTS AS WIRED, AND WHY THE THIRD ROUTE IS MEASURED RATHER THAN GREPPED

  guards.yml    a real invocation. A `--self-test` line is NOT one, and that filter is the whole
                lesson of GATE_LESSONS entry 14 ("A self-test is not wiring").
                `port_audit` counted a script as wired if anything named it, every gate is
                named on a `--self-test` line, so for the entire class of file the check
                mattered most for it could not fail.
  the routine    the same rule. A phase that runs the gate in anger.
  shipped_check  the registry the upgrade lane owns. One step in `guards.yml` calls that file, so
                 a gate registered there is genuinely run by CI against published artifacts.

The third route is not a grep. `shipped_check` records which carousel modules its gate loop
ACTUALLY LOADED while running, and hands that set here. A registered adapter that returns early
without ever importing its gate has not run it, and this reports it as unwired, which is the
honest answer and is the same question `shipped_check`'s own reachability assertion asks.

WHAT THIS DOES NOT COVER, stated because an exemption nobody wrote down is how the next silent
surface grows. Its census is `scripts/carousel/*.py` only, which is the suite the upgrade lane
builds and the suite that has produced every orphan so far. `scripts/shared/**` and
`scripts/site/**` are the `daily` and `human` lanes' and are not read here.

    gate_wiring.py                 take the measurement and grade it
    gate_wiring.py --self-test
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CAROUSEL = REPO_ROOT / "scripts" / "carousel"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "guards.yml"
ROUTINE = REPO_ROOT / "prompts" / "daily_routine.md"

# A GATE IS A FILE THAT CAN BE ASKED. Declaring `--self-test` is the one uniform property every
# checker in this directory has, and it is a property of the FILE rather than of a list somebody
# maintains, so a gate written tomorrow is in the census the moment it exists.
SELF_TEST_FLAG = '"--self-test"'


def gates() -> list[str]:
    """Every carousel gate, by module name, taken from the directory rather than a list."""
    return sorted(p.stem for p in CAROUSEL.glob("*.py")
                  if SELF_TEST_FLAG in p.read_text(encoding="utf-8"))


def invoked_in(text: str, stem: str) -> bool:
    """Is this gate RUN by that text, as opposed to merely named in it.

    Two filters and each one has a fault behind it. The invocation must be a python call, so a
    gate named in a sentence of prose is not wiring. And a `--self-test` invocation is not
    wiring, because a self-test proves the checker can go red and says nothing whatever about
    anything calling it in anger.
    """
    pat = re.compile(r"python3?\s+\S*" + re.escape(stem + ".py")
                     + r"(?!\s*(?:\\\s*\n\s*)?--self-test)")
    return bool(pat.search(text))


def check(loaded: set[str], workflow: str | None = None, routine: str | None = None,
          census: list[str] | None = None) -> list[str]:
    """Every gate that nothing in this machine runs. Pure, so callers can fixture it."""
    wf = WORKFLOW.read_text(encoding="utf-8") if workflow is None else workflow
    rt = ROUTINE.read_text(encoding="utf-8") if routine is None else routine
    names = gates() if census is None else census

    out: list[str] = []
    if not names:
        return ["the census found no carousel gate at all, so this check is grading nothing"]
    for stem in names:
        if invoked_in(wf, stem) or invoked_in(rt, stem) or stem in loaded:
            continue
        out.append(
            f"{stem}.py is run by nothing. It is in guards.yml in no form, the routine names it "
            f"in no phase, and shipped_check's gate loop never loaded it. A gate nobody runs is "
            f"a gate that is red without anybody finding out. The fix inside the upgrade lane is "
            f"a registry entry in scripts/carousel/shipped_check.py")
    return out


def measure_loaded() -> set[str]:
    """Which carousel modules the wired `shipped_check` step loads when it runs for real.

    Run rather than read. `shipped_check.run` is the thing `guards.yml` actually calls, so it is
    what gets asked, on the NEWEST deck, which is the sweep in which every registered gate
    applies. A narrowed sweep over an older deck loads less, because a gate that postdates a
    deck returns before it imports anything, and `shipped_check` refuses to grade the census in
    that case for exactly this reason.

    The spy covers both routes a gate reaches this suite by: an ordinary `import`, which lands
    in `sys.modules`, and `spec_from_file_location`, which does not, and which is how
    `g_construction` loads its gate. A spy watching only the first would have called
    `construction_check` unwired and been wrong about one of the two gates this file exists for.

    NO RECURSION, and it is worth stating because the shape invites it. `shipped_check.run`
    calls `check` here, which is pure and reads the three lists. It never calls back into this
    function.
    """
    sys.path.insert(0, str(CAROUSEL))
    import shipped_check as sc                                          # noqa: PLC0415

    runs = sc.shipped_runs()
    if not runs:
        return set()
    original = importlib.util.module_from_spec
    seen: set[str] = set()

    def spy(spec):
        seen.add(spec.name)
        return original(spec)

    before = set(sys.modules)
    importlib.util.module_from_spec = spy
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            sc.run(only=runs[-1].name)
    finally:
        importlib.util.module_from_spec = original
    return ((set(sys.modules) - before) | seen) & set(gates())


def self_test() -> int:
    bad = 0

    def ok(label, cond, extra=""):
        nonlocal bad
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            bad += 1

    # ---- THE DEFECT THIS EXISTS FOR, replayed on the two gates that produced it. The strings
    # below are the state of the repository on the morning of 2026-09-10.
    both_missing = check(loaded=set(), workflow="", routine="",
                         census=["construction_check", "verbatim_check"])
    ok("construction_check, in neither list and in no registry, is CAUGHT",
       any(x.startswith("construction_check") for x in both_missing), str(both_missing))
    ok("verbatim_check, the same, is CAUGHT",
       any(x.startswith("verbatim_check") for x in both_missing), str(both_missing))
    ok("...and the finding names the repair the upgrade lane can actually make",
       all("shipped_check.py" in x for x in both_missing), str(both_missing))

    # ---- A SELF-TEST LINE IS NOT WIRING, which is GATE_LESSONS
    # entry 14 ("A self-test is not wiring") and the reason the whole
    # census exists. `port_audit` counted a mention, every gate is mentioned on a self-test line,
    # and so the check could not fail for the class of file it was written for.
    only_st = "          python3 scripts/carousel/verbatim_check.py --self-test\n"
    ok("a gate that CI only self-tests is still an orphan",
       check(set(), only_st, "", ["verbatim_check"]), "a --self-test line counted as wiring")
    ok("...and a real invocation beside it clears it",
       not check(set(), only_st + "          python3 scripts/carousel/verbatim_check.py --run x\n",
                 "", ["verbatim_check"]))

    # A LINE CONTINUATION IS THE SHAPE guards.yml ACTUALLY USES, so it is tested rather than
    # assumed. `foo.py \` newline `--self-test` is one invocation, not two.
    ok("a self-test invocation split across a line continuation is still not wiring",
       check(set(), "python3 scripts/carousel/verbatim_check.py \\\n  --self-test\n", "",
             ["verbatim_check"]))

    # PROSE NAMING A GATE IS NOT WIRING EITHER. The routine and the workflow are both full of
    # sentences about gates, and a sentence runs nothing.
    ok("a gate named in a sentence is not wired by it",
       check(set(), "", "See scripts/carousel/verbatim_check.py for what it measures.\n",
             ["verbatim_check"]))

    # ---- THE THREE ROUTES, each on its own, because a check that passes on any of them and is
    # never tested on two of them is a check wired to one.
    ok("a real guards.yml invocation is wiring",
       not check(set(), "python3 scripts/carousel/shipped_check.py\n", "", ["shipped_check"]))
    ok("a real routine invocation is wiring",
       not check(set(), "", "python3 scripts/carousel/panel_ready.py --date <date>\n",
                 ["panel_ready"]))
    ok("a module shipped_check's loop actually loaded is wiring",
       not check({"ledger_check"}, "", "", ["ledger_check"]))

    # ---- AN EMPTY CENSUS MUST NOT READ AS CLEAN. A checker that grades nothing and prints a
    # pass is this repository's oldest shape, and it is one line to refuse.
    ok("a census of nothing is a finding rather than a pass",
       check(set(), "", "", []), "an empty census reported clean")

    # ---- AND THE LIVE REPOSITORY, which is the only reason any of the above matters. The
    # measurement is taken the way `main()` takes it.
    loaded = measure_loaded()
    ok("the measurement saw shipped_check's loop load real gates", len(loaded) >= 10,
       f"only {sorted(loaded)}")
    ok("construction_check is loaded through spec_from_file_location and the spy sees it",
       "construction_check" in loaded, str(sorted(loaded)))
    live = check(loaded)
    ok("every gate in scripts/carousel is run by something", not live, "; ".join(live))

    # ---- AND THE CENSUS'S OWN WIRING, PROVED BY BEHAVIOUR RATHER THAN ASSERTED.
    #
    # This file is graded by its own rule and the answer it gets is "shipped_check loaded it".
    # That answer is worth nothing unless shipped_check RUNS it and ACTS on what it says, which
    # is the exact inference GATE_LESSONS
    # entry 14 ("A self-test is not wiring") refuses to let a checker make about itself. So a
    # finding is planted and the wired step is asked what it does with one. It must land in the
    # fatal list on stderr rather than in the notes on stdout, because a note is a thing a green
    # build prints.
    import shipped_check as sc                                          # noqa: PLC0415
    import gate_wiring as gw                                            # noqa: PLC0415
    newest = sc.shipped_runs()[-1].name
    planted = "A PLANTED WIRING FINDING"
    real_check, out, err = gw.check, io.StringIO(), io.StringIO()
    try:
        gw.check = lambda *a, **k: [planted]
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            sc.run(only=newest)
    finally:
        gw.check = real_check
    ok("shipped_check RUNS the census, and a finding from it is FATAL",
       planted in err.getvalue(), (err.getvalue() or out.getvalue())[-400:])
    ok("...and it is not filed as a note a green build would print",
       planted not in out.getvalue(), out.getvalue()[-400:])

    # A NARROWED SWEEP MUST REFUSE TO GRADE RATHER THAN GRADE WRONG. A gate that postdates an
    # older deck returns before importing anything, so over that deck the measurement is short
    # and every missing gate would be reported as an orphan. Saying which kind of absence this
    # is out loud is
    # GATE_LESSONS entry 37 ("A law with no mechanism, reported as a skip"). A skip that
    # means "not covered at all" is not a skip.
    older = [p.name for p in sc.shipped_runs()][:-1]
    if older:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            sc.run(only=older[0])
        ok(f"a sweep narrowed to {older[0]} says the census was NOT TAKEN",
           "gate wiring: NOT TAKEN" in out.getvalue(), out.getvalue()[-400:])

    print("\ngate_wiring self-test: " + ("all passed" if not bad else f"{bad} FAILED"))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], allow_abbrev=False)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    found = check(measure_loaded())
    if found:
        print("gate wiring:", file=sys.stderr)
        for f in found:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print(f"gate wiring ok: {len(gates())} carousel gate(s), every one run by something")
    return 0


if __name__ == "__main__":
    sys.exit(main())
