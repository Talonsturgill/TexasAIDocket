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

WHAT THIS COVERS, AND THE EXEMPTION THAT USED TO BE HERE. Until 2026-09-13 the census was
`scripts/carousel/*.py` alone, and the docstring said so plainly on the grounds that the other
directories belong to other lanes. **Writing an exemption down honestly is not the same as it
being right, and this one hid seven things.** A new checker in `scripts/shared/` reported clean
while nothing ran it, and six under `scripts/site/` had declared a `--self-test` no workflow and
no phase had ever asked: `grain`, `mark`, `sky`, `watch_page`, `ask_eval` and `tdlr_fetch`. A
wiring check that cannot see a directory reports clean about a place it never looked.

The census is `scripts/{carousel,shared,site}/*.py` now, 90 gates where it graded 32, and
"run by something" has three routes: a workflow or a phase calls it, `shipped_check`'s gate loop
loads it, or something that IS run imports it. Lane ownership decides who may FIX an orphan,
which is a different question from whether one exists, and this file only ever answered the
second.

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

# THE DIRECTORIES OF STANDALONE CHECKERS. Widened from `carousel` alone on 2026-09-13.
#
# The old census was `scripts/carousel/*.py` and the exemption was written down honestly in the
# docstring, which is exactly what let it survive: a limit nobody disputes is a limit nobody
# revisits. It hid a real orphan. `scripts/shared/merge_ready.py` was added that day to catch a
# defect that had cost two days of shipping, and it reported clean here while nothing ran it.
#
# `scripts/site` CAME IN THE SAME EVENING, once this file learned to read imports. Under the
# direct rule alone 24 of its 43 checkers looked like orphans and 22 were not: `grain`, `mark`,
# `sky`, `theme`, `truetype`, `texas_map` and the rest are LIBRARIES `site_build.py` imports, so
# their invocation is an import rather than a `python3 x.py`. Reporting 24 findings of which zero
# are actionable is the cry-wolf failure `invoked_in`'s own docstring refuses, so the route was
# built rather than the directory excused. See `reached`.
#
# The two that survived the import route were real orphans and were treated differently on their
# merits. `ask_eval` is BUILT in CI now rather than self-tested, because building 867 cases off
# the record is the check. `tdlr_fetch` is in NOT_A_GATE with its reason.
CENSUS = ("carousel", "shared", "site")

# Every module in the census, by stem, so the import reader can tell one of ours from `json`.
MODULES = {p.stem: p for d in CENSUS for p in (REPO_ROOT / "scripts" / d).glob("*.py")}

# NOT A GATE, WITH THE REASON BESIDE IT. Same shape as `config/decider_groups.json`: saying two
# things are different is a judgement, so it is written where it can be read and argued with, and
# AN ENTRY WITH NO REASON FAILS THIS CHECK.
#
# The census rule is that a file declaring `--self-test` is a checker that can be asked. It is a
# good rule and it misclassifies a fetcher, whose self-test exercises its PARSER while its actual
# job needs the network. `gen_port_manifest.py` needs no entry here because it declares no
# self-test at all, which is the same distinction arrived at by accident.
NOT_A_GATE = {
    "tdlr_fetch": ("A fetcher for the Comptroller's certified register, not a checker. Its "
                   "--self-test exercises the parser and its --build goes to the network, so "
                   "wiring it into CI would fetch a state register on every pull request. What "
                   "IS checked is its output, through the data center dossiers that read it."),
}
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "guards.yml"

# EVERY WORKFLOW, because `guards.yml` is not the only thing that runs a checker. `livecheck.py`
# has its own six-hourly workflow and reading only `guards.yml` would have reported it an orphan,
# which is the same fault as the census: a checker that cannot see a file reports confidently
# about a place it never looked.
WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"
ROUTINE = REPO_ROOT / "prompts" / "daily_routine.md"

# A GATE IS A FILE THAT CAN BE ASKED. Declaring `--self-test` is the one uniform property every
# checker in this directory has, and it is a property of the FILE rather than of a list somebody
# maintains, so a gate written tomorrow is in the census the moment it exists.
SELF_TEST_FLAG = '"--self-test"'


def gates() -> list[str]:
    """Every gate this repo has, by module name, taken from the directories rather than a list.

    A file that declares `--self-test` is a checker and is in the census. A file that does not
    is not, which is why `gen_port_manifest.py` needs no exemption written for it: it generates
    the port manifest and `port_audit` checks the output, so it is not a thing that can be asked.
    No list to maintain and nothing to keep in sync.
    """
    out = []
    for d in CENSUS:
        for p in (REPO_ROOT / "scripts" / d).glob("*.py"):
            if SELF_TEST_FLAG in p.read_text(encoding="utf-8"):
                out.append(p.stem)
    return sorted(set(out))


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


def imported_by(stem: str, seen: set[str] | None = None) -> set[str]:
    """The modules `stem` imports, restricted to this repo's own scripts.

    Read with `ast` rather than by importing, because importing a module to find out whether
    anything imports it runs its top level, and several of these draw or fetch on import.
    Imports inside a function body count: `shipped_check` and this file both do it, and a call
    that only happens sometimes is still a call.
    """
    import ast
    p = MODULES.get(stem)
    if p is None:
        return set()
    try:
        tree = ast.parse(p.read_text(encoding="utf-8"))
    except SyntaxError:
        return set()
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            out.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            out.add(n.module.split(".")[0])
    return {m for m in out if m in MODULES}


def reached(roots: set[str]) -> set[str]:
    """Everything an invoked module pulls in, transitively.

    THE ROUTE THAT LET `scripts/site` INTO THE CENSUS. Under the direct rule alone, 24 of its 43
    checkers looked like orphans and not one of them was: `grain`, `mark`, `sky`, `theme`,
    `truetype` and the rest are LIBRARIES that `site_build.py` imports, so their invocation is an
    import rather than a `python3 x.py`. A gate reporting 24 findings of which zero are
    actionable teaches a run to scroll past the 25th, which is the cry-wolf failure `invoked_in`
    already refuses for prose.

    With this route the same directory reports TWO, and both were real: `ask_eval` and
    `tdlr_fetch` had a `--self-test` that nothing had ever run. Both were wired in the same
    change, so this went green on the day it landed.
    """
    seen, stack = set(roots), list(roots)
    while stack:
        for child in imported_by(stack.pop()):
            if child not in seen:
                seen.add(child)
                stack.append(child)
    return seen - set(roots)


def check(loaded: set[str], workflow: str | None = None, routine: str | None = None,
          census: list[str] | None = None) -> list[str]:
    """Every gate that nothing in this machine runs. Pure, so callers can fixture it."""
    wf = (workflow if workflow is not None else
          "\n".join(p.read_text(encoding="utf-8") for p in sorted(WORKFLOW_DIR.glob("*.yml"))))
    rt = ROUTINE.read_text(encoding="utf-8") if routine is None else routine
    names = gates() if census is None else census

    out: list[str] = []
    # THE EXEMPTIONS ARE GRADED FIRST, before any early return. An unjustified exemption is a
    # finding about this file rather than about the census, so a narrowed or empty census must
    # not be able to hide one.
    for stem, why in NOT_A_GATE.items():
        if not str(why or "").strip():
            out.append(f"{stem} is excused in NOT_A_GATE with no reason written. An exemption "
                       f"nobody justified is how the next silent surface grows")
    if not names:
        return out + ["the census found no gate at all, so this check is grading nothing"]
    direct = {s for s in MODULES if invoked_in(wf, s) or invoked_in(rt, s)}
    indirect = reached(direct | set(loaded))
    for stem in names:
        if stem in direct or stem in loaded or stem in indirect or stem in NOT_A_GATE:
            continue
        out.append(
            f"{stem}.py is run by nothing. No workflow calls it, the routine names it in no "
            f"phase, shipped_check's gate loop never loaded it, and nothing that IS run imports "
            f"it. A gate nobody runs is "
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

    # THE WIDENED CENSUS ACTUALLY REACHES `scripts/shared`, asserted rather than assumed. This
    # is the widening's own replay: before 2026-09-13 a checker in that directory could be run by
    # nothing and this file would report clean, which is how `merge_ready.py` was born an orphan.
    ok("the census reaches scripts/shared", "merge_ready" in gates(),
       "the widened census does not see scripts/shared, so a shared orphan reports clean")
    ok("...and a shared gate nothing runs is reported",
       bool(check(set(), workflow="", routine="", census=["merge_ready"])),
       "a shared checker with no caller came back clean")
    ok("...and the real wiring clears it",
       not check(set(), census=["merge_ready"]),
       "merge_ready is in the census and nothing in the machine runs it")

    # AND EVERY WORKFLOW COUNTS, not only guards.yml. `livecheck.py` runs on its own schedule in
    # livecheck.yml, and reading one file would call it an orphan.
    ok("a checker wired by a workflow other than guards.yml is not an orphan",
       not check(set(), census=["livecheck"]),
       "only guards.yml is being read, so every other workflow's checkers look unwired")

    # THE IMPORT ROUTE, which is what let `scripts/site` into the census at all.
    ok("the census reaches scripts/site", "site_build" in gates(),
       "the census does not see scripts/site")
    ok("a library reached only by an import is not an orphan",
       not check(set(), census=["truetype"]),
       "truetype is imported by site_build and nothing calls it as python3 truetype.py, so "
       "without the import route it reports as an orphan and 21 others report with it")
    ok("...and the import reader finds that edge", "truetype" in reached({"site_build"}),
       f"reached from site_build: {sorted(reached({'site_build'}))[:6]}")
    ok("an unreachable checker is still reported",
       bool(check(set(), workflow="", routine="", census=["site_build"])),
       "with nothing invoked and nothing imported, even a root must come back as an orphan")

    # AN EXEMPTION WITHOUT A REASON IS ITSELF A FINDING.
    # Mutate THIS module's global rather than `import gate_wiring`, which under `python3
    # gate_wiring.py` yields a second module object whose NOT_A_GATE `check` never reads.
    _keep = dict(NOT_A_GATE)
    try:
        NOT_A_GATE["a_fixture"] = ""
        ok("an exemption with no reason written is reported",
           any("no reason written" in f for f in check(set(), workflow="", routine="",
                                                       census=[])),
           "NOT_A_GATE accepted a blank reason")
        NOT_A_GATE["a_fixture"] = "a reason"
        ok("...and one with a reason is accepted",
           not any("no reason written" in f for f in check(set(), census=[])),
           "a justified exemption was still reported")
    finally:
        NOT_A_GATE.clear()
        NOT_A_GATE.update(_keep)

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
    print(f"gate wiring ok: {len(gates())} gate(s) across {', '.join(CENSUS)}, every one run by something")
    return 0


if __name__ == "__main__":
    sys.exit(main())
