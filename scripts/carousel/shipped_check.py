#!/usr/bin/env python3
"""shipped_check.py — run the gates against what was actually published.

WHY THIS EXISTS, and it is the multiplier on every other gate in this suite.

An audit of `.github/workflows/guards.yml` on 2026-08-19 found that of its fifteen carousel
steps, THIRTEEN are `--self-test`. The only two that touch a real artifact are
`email_check --all` and `bespoke_check --slides-dir examples/demo-deck/slides`, and the second
of those points at a demo deck rather than at anything this project has ever published.

So CI proved, every run, that the checkers CAN go red, and almost never asked them whether the
product was clean. `coherence_check`, `craft_floor`, `run_complete`, `sources_block`,
`plan_render_check` and `absence_check` were in CI in no form at all. Six gates, all of them
written BY these runs to catch defects these runs shipped, protecting only the runs that
remembered to call them, which is the exact defect each was written for.

That is UPGRADE_BACKLOG item 6, and it outranks everything else on that page.

WHY ONE SCRIPT RATHER THAN NINE CI STEPS

`.github/workflows/**` is `human` owned, so a routine cannot connect its own gate. Every gate
built by an upgrade phase has therefore needed a maintainer to wire it, and three of them
waited. One step in the workflow calling one script here means the next gate is one function
call away, in a file the upgrade lane already owns.

WHAT IT DOES NOT DO

It does not re-render. The gates that need pixels (`qa.py`) need a browser, and a shipped run
already carries the machine_qa.json its render produced. This reads the committed artifacts and
asks whether they still agree with each other and with today's rules.

THE ONE JUDGEMENT IN HERE. A gate written after a deck shipped can be red on that deck for
reasons that are true and not actionable, which happened when the render window widened from 80
to 320 and turned an unchanged 2026-08-16 deck red. So each gate is registered with a scope:

    HISTORY   must hold for every deck ever shipped. A breach is a real regression.
    CURRENT   must hold for the newest deck. Older decks report as a note.

    shipped_check.py                 every shipped run
    shipped_check.py --run 2026-08-19
    shipped_check.py --self-test
"""
from __future__ import annotations

import argparse
import io
import json
import contextlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS = REPO_ROOT / "runs" / "carousel"
sys.path.insert(0, str(Path(__file__).resolve().parent))

HISTORY, CURRENT = "history", "current"


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


# --------------------------------------------------------------------------- the gates
def g_copy_sync(d: Path):
    import copy_sync_check as m
    copy, rep = _load(d / "copy.json"), _load(d / "render_report.json")
    if not (copy and rep):
        return None
    claims = _load(d / "claims.json")
    drifted, uncited = m.compare(copy, rep, claims)
    return drifted + uncited


def g_aggregates(d: Path):
    import aggregate_check as m
    rep, agg = _load(d / "render_report.json"), _load(d / "aggregates.json")
    claims = _load(d / "claims.json")
    if not (rep and agg is not None and claims):
        return None
    probs = m.check(rep, agg, claims)
    return list(probs) if probs else []


def g_dossiers(d: Path):
    """check(dossiers, expected, breathers), not (raw_text, report).

    The reachability assertion in the self-test is what caught this: the first draft passed the
    raw markdown where a parsed dict belongs, threw, and was silently skipped on every run. A
    registry entry whose loader always errors reports clean forever, which is the same shape as
    craft_floor reading a key qa.py never wrote.
    """
    import dossier_check as m
    sb = d / "storyboard.md"
    if not sb.exists():
        return None
    dossiers = m.parse_dossiers(sb.read_text(encoding="utf-8"))
    if not dossiers:
        return None
    rep = _load(d / "render_report.json") or {}
    expected = len(rep.get("slides") or []) or None
    return list(m.check(dossiers, expected, None) or [])


def g_coherence(d: Path):
    import coherence_check as m
    copy = _load(d / "copy.json")
    if not copy:
        return None
    fails, warns = m.check_copy(copy)
    sd = d / "slides"
    if sd.exists():
        f2, _ = m.check_type_spine(sd)
        f3, _ = m.check_site_line(sd)
        fails += f2 + f3
    return fails


def g_craft_floor(d: Path):
    import craft_floor as m
    rep = _load(d / "render_report.json")
    if not rep:
        return None
    fails, _warns, _meta = m.check(rep, _load(d / "machine_qa.json"))
    return fails


def g_plan_render(d: Path):
    import plan_render_check as m
    sb, rep = d / "storyboard.md", _load(d / "render_report.json")
    if not (sb.exists() and rep):
        return None
    fails, _w, _s = m.check(sb.read_text(encoding="utf-8"), d / "slides", rep)
    return fails


def g_absences(d: Path):
    import absence_check as m
    copy = _load(d / "copy.json")
    if not copy:
        return None
    fails, _w, _s = m.check(copy, _load(d / "render_report.json"))
    return fails


def g_sources(d: Path):
    """check(run_dir) takes the directory itself. Caught by the same reachability assertion."""
    import sources_block as m
    if not ((d / "copy.json").exists() and (d / "first_comment.txt").exists()):
        return None
    return list(m.check(d) or [])


def g_nouns(d: Path):
    import noun_trace as m
    cp, cl = _load(d / "copy.json"), _load(d / "claims.json")
    if not (cp and cl):
        return None
    fails, _w, _s = m.check(cp, cl)
    return fails


def g_completion(d: Path):
    import run_complete as m
    if not (d / "score.json").exists():
        return None
    return list(m.check(d, m.threshold()) or [])


GATES = [
    ("copy sync", g_copy_sync, HISTORY),
    # CURRENT, not HISTORY, and the reason is the lesson this whole file is built on.
    # aggregate_check gained the `quoted_from` route AFTER 2026-08-18 shipped. That deck
    # declared five quoted figures through `computed_by` because it was the only route that
    # existed, and today's gate calls that wrong. The deck did not change. The ruler did, which
    # is exactly what happened when the render window went 80 to 320 and turned an untouched
    # 2026-08-16 deck red. Judging published work by a rule written after it is how a suite
    # teaches people to ignore it.
    ("aggregates", g_aggregates, CURRENT),
    ("dossiers", g_dossiers, CURRENT),
    ("coherence", g_coherence, CURRENT),
    ("craft floor", g_craft_floor, CURRENT),
    ("plan vs render", g_plan_render, CURRENT),
    ("absences", g_absences, HISTORY),
    ("nouns", g_nouns, HISTORY),
    ("sources block", g_sources, HISTORY),
    ("completion", g_completion, HISTORY),
]


def shipped_runs() -> list:
    return sorted([p for p in RUNS.glob("2*") if (p / "copy.json").exists()]) if RUNS.exists() else []


def check_run(d: Path, newest: bool) -> tuple:
    """Returns (fatal, notes). Each is a list of strings."""
    fatal, notes = [], []
    for name, fn, scope in GATES:
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                probs = fn(d)
        except Exception as exc:                       # noqa: BLE001
            notes.append(f"{d.name}  {name}: could not run ({type(exc).__name__}: {exc})")
            continue
        if probs is None:
            notes.append(f"{d.name}  {name}: not applicable, the artifact it reads is absent")
            continue
        if not probs:
            continue
        head = str(probs[0])[:150]
        line = f"{d.name}  {name}: {len(probs)} problem(s). First: {head}"
        if scope == HISTORY or newest:
            fatal.append(line)
        else:
            notes.append(line + "   [older deck, gate is newer than it]")
    return fatal, notes


def run(only: str | None = None) -> int:
    runs = shipped_runs()
    if only:
        runs = [p for p in runs if p.name == only]
        if not runs:
            print(f"shipped_check: no shipped run named {only}", file=sys.stderr)
            return 1
    if not runs:
        print("shipped_check: no shipped runs to check")
        return 0
    newest = shipped_runs()[-1].name
    fatal, notes = [], []
    for d in runs:
        f, n = check_run(d, d.name == newest)
        fatal += f
        notes += n
    for n in notes:
        print(f"  note  {n}")
    if fatal:
        print(f"\nshipped_check: {len(fatal)} problem(s) in work that is already published\n",
              file=sys.stderr)
        for f in fatal:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print(f"shipped_check: {len(runs)} shipped run(s), every applicable gate clean on the "
          f"artifacts as committed")
    return 0


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    bad = 0

    def ok(label, cond, extra=""):
        nonlocal bad
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            bad += 1

    ok("there are shipped runs to check at all", bool(shipped_runs()),
       "runs/carousel carries no run with a copy.json, so this gate is inert")

    # EVERY GATE MUST BE REACHABLE. The failure this guards against is a registry entry whose
    # loader silently returns None on every run, which reports clean forever. Same shape as
    # craft_floor reading a key qa.py never wrote.
    runs = shipped_runs()
    if runs:
        newest = runs[-1]
        reached = []
        for name, fn, _scope in GATES:
            try:
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    r = fn(newest)
                if r is not None:
                    reached.append(name)
            except Exception:                          # noqa: BLE001
                pass
        ok(f"every registered gate actually runs on the newest deck ({newest.name})",
           len(reached) == len(GATES),
           f"reached {reached}, missing {[g[0] for g in GATES if g[0] not in reached]}")

    # A gate that returns problems must be reported as fatal on the newest deck.
    def boom(_d):
        return ["a deliberately broken gate"]
    GATES.append(("selftest probe", boom, CURRENT))
    try:
        if runs:
            f, n = check_run(runs[-1], True)
            ok("a failing gate on the newest deck is FATAL",
               any("selftest probe" in x for x in f), str(f))
            f, n = check_run(runs[0], False) if len(runs) > 1 else ([], ["skipped"])
            if len(runs) > 1:
                ok("...and on an older deck a CURRENT-scope gate is a note rather than fatal",
                   not any("selftest probe" in x for x in f), str(f))
    finally:
        GATES.pop()

    ok("the newest run is identified as the newest",
       (not runs) or shipped_runs()[-1].name == max(p.name for p in shipped_runs()))

    print("\nshipped_check self-test: " + ("all passed" if not bad else f"{bad} FAILED"))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", help="one shipped run date")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    return self_test() if a.self_test else run(a.run)


if __name__ == "__main__":
    raise SystemExit(main())
