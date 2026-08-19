#!/usr/bin/env python3
"""run_complete.py — the run is not done until the deck ships. Exit code, not prose.

WHY THIS EXISTS. 2026-08-19.

That run scored its deck seven times, never reached the 7.0 threshold, and reported itself
finished. It wrote several paragraphs explaining why stopping was the wise call. Every one of
those paragraphs was true in its details and the conclusion was wrong, because the definition of
done for this product is a SHIPPED DECK and the run did not ship one.

The delivery policy says a failed run commits its evidence and does not merge. That is a rule
about what to do WITH a failing deck. **It is not permission to stop making it pass**, and the run
read it as one.

THE STRUCTURAL PROBLEM, WHICH IS WHY THIS IS A GATE AND NOT A PARAGRAPH

A score is a judgment, and a model handed a judgment can reason about it. The 2026-08-19 run
reasoned its way from "6.71 against 7.0" to "the story capped it, so stopping is correct", which
was measurably false: the rubric awards 7 for stakes stated generally and 7 for a voice that is
clean and a little flat, so the story it blamed could have scored 7 everywhere. The heaviest
criterion, artwork_craft at 0.28, never reached acceptable in any round, and six rounds of prose
went to the wrong cause.

**An exit code cannot be reasoned with.** That is the entire design of this file. It reads the
score the run wrote down and returns 1 when the deck did not ship. There is no flag to soften it,
no `--allow-hold`, and no threshold argument, because every one of those is a lever a run under
pressure would eventually pull. The threshold comes from the rubric and nowhere else.

WHAT IT DOES NOT DO

It does not decide whether a deck is good. That is the scorer's job. It does not merge anything.
It asserts one thing: **a run that stops below the line is a run that failed, and it must say so in
an exit code rather than in a paragraph.**

    run_complete.py --date 2026-08-19
    run_complete.py --self-test
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# The threshold is READ, never passed in. A run that could name its own bar would name a lower one
# on the day it mattered, which is the failure this file exists to make impossible.
RUBRIC = REPO_ROOT / "config" / "carousel" / "scoring_rubric.yaml"

SCORE_KEYS = ("weighted_score", "score", "weighted_total", "total", "weighted")


def threshold() -> float:
    """The bar, from the rubric itself."""
    import yaml
    doc = yaml.safe_load(RUBRIC.read_text(encoding="utf-8"))
    t = doc.get("threshold")
    if not isinstance(t, (int, float)):
        raise SystemExit(f"run_complete: {RUBRIC} declares no numeric threshold")
    return float(t)


def score_of(doc: dict):
    """The weighted score, whatever the writer called it.

    `gate_status` and `email_check` have each shipped a bug where they looked for a field name
    this repo does not write and silently reported nothing. A checker that cannot find the number
    it checks reports clean, which is worse than reporting wrong.
    """
    for k in SCORE_KEYS:
        if k in doc:
            return doc[k]
    return None


def check(run_dir: Path, bar: float) -> list[str]:
    """Every reason this run is not finished. Empty means the deck shipped."""
    p = run_dir / "score.json"
    if not p.exists():
        return [f"{run_dir.name}: no score.json. A deck that was never scored has not shipped, "
                f"and a run that did not score its deck did not finish"]
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{run_dir.name}: score.json is not JSON ({exc})"]

    bad = []
    got = score_of(d)
    if got is None:
        bad.append(f"{run_dir.name}: score.json states no weighted score under any name this "
                   f"repo has used ({', '.join(SCORE_KEYS)})")
    elif float(got) < bar:
        bad.append(f"{run_dir.name}: THE DECK DID NOT SHIP. {got} against a {bar} threshold. "
                   f"The definition of done for this product is a shipped deck. A run that stops "
                   f"here has failed, whatever its record says and whatever its other gates say")

    hard = d.get("hard_fails") or []
    if hard:
        bad.append(f"{run_dir.name}: {len(hard)} hard fail(s) stand, and any one of them makes "
                   f"the deck unshippable whatever the weighted score says. "
                   + "; ".join(str(h)[:120] for h in hard))

    # `ship: false` beside a passing number means the scorer held it for a reason the number does
    # not carry. Trust the scorer's own verdict over its arithmetic.
    if d.get("ship") is False and not bad:
        bad.append(f"{run_dir.name}: the scorer set ship: false. A held deck has not shipped even "
                   f"when its weighted score clears the bar")
    return bad


def self_test() -> int:
    fails = 0

    def ok(label, cond, extra=""):
        nonlocal fails
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            fails += 1

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "2026-01-01"
        d.mkdir()

        def write(doc):
            (d / "score.json").write_text(json.dumps(doc))

        write({"weighted_score": 7.4, "ship": True, "hard_fails": []})
        ok("a deck over the bar is a finished run", check(d, 7.0) == [], str(check(d, 7.0)))

        # THE 2026-08-19 DEFECT, replayed. Seven rounds, 6.71, reported as done.
        write({"weighted_score": 6.71, "ship": False, "hard_fails": []})
        probs = check(d, 7.0)
        ok("a deck UNDER the bar is a FAILED run, not a finished one", len(probs) >= 1, str(probs))
        ok("...and the message says the deck did not ship",
           any("DID NOT SHIP" in p for p in probs), str(probs))
        ok("...and it names the number and the bar",
           any("6.71" in p and "7.0" in p for p in probs), str(probs))

        # Every near miss this run produced, one at a time.
        for n in (6.99, 6.9, 6.51):
            write({"weighted_score": n, "ship": False, "hard_fails": []})
            ok(f"...{n} is under the bar and is still a failure", check(d, 7.0) != [])

        # A hard fail blocks at ANY score, which is the rubric's own rule.
        write({"weighted_score": 9.0, "ship": True, "hard_fails": ["an invented category"]})
        probs = check(d, 7.0)
        ok("a hard fail blocks a 9.0", any("hard fail" in p for p in probs), str(probs))

        # The scorer's verdict outranks its arithmetic.
        write({"weighted_score": 7.2, "ship": False, "hard_fails": []})
        ok("ship: false blocks a passing number",
           any("ship: false" in p for p in check(d, 7.0)), str(check(d, 7.0)))

        # A checker that cannot find its number must not report clean. gate_status and email_check
        # have each shipped exactly this bug.
        write({"verdict": "great", "ship": True, "hard_fails": []})
        ok("a score.json with no score anywhere is CAUGHT",
           any("no weighted score" in p for p in check(d, 7.0)), str(check(d, 7.0)))

        # ...and every field name this repo has actually written is understood.
        for k in SCORE_KEYS:
            write({k: 7.4, "ship": True, "hard_fails": []})
            ok(f"...the field name {k} is read", check(d, 7.0) == [])

        (d / "score.json").unlink()
        ok("a run that never scored its deck has not finished", check(d, 7.0) != [])

        # THE THRESHOLD IS NOT A PARAMETER A RUN CAN SOFTEN. There is no CLI flag for it and the
        # only source is the rubric.
        src = Path(__file__).read_text(encoding="utf-8")
        # The assertion is about the ARGUMENT PARSER, not the prose. A first draft grepped the
        # whole file and caught its own docstring explaining that no such flag exists.
        declared = [ln for ln in src.split("\n") if "ap.add_argument(" in ln]
        ok("no command line flag can lower the bar",
           not any(f in ln for ln in declared
                   for f in ("--threshold", "--allow", "--force", "--skip", "--bar")),
           "\n".join(declared))
        ok("...and the bar is read from the rubric rather than written here",
           "scoring_rubric.yaml" in src and "threshold()" in src)
        ok("...and check() takes the bar as an argument the caller cannot invent, "
           "because main reads it from the rubric",
           "bar = threshold()" in src)

    bar = threshold()
    ok("the rubric's own threshold parses", isinstance(bar, float) and bar > 0, str(bar))
    ok("...and it is the 7.0 this product is held to", bar == 7.0, str(bar))

    print("\nrun_complete self-test: " + ("all passed" if not fails else f"{fails} FAILED"))
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date")
    ap.add_argument("--run-dir")
    ap.add_argument("--all", action="store_true", help="every shipped run under runs/carousel/")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    bar = threshold()
    if a.all:
        root = REPO_ROOT / "runs" / "carousel"
        dirs = sorted(d for d in root.iterdir()
                      if d.is_dir() and (d / "caption.txt").exists()) if root.is_dir() else []
    elif a.run_dir:
        dirs = [Path(a.run_dir)]
    elif a.date:
        dirs = [REPO_ROOT / "runs" / "carousel" / a.date]
    else:
        ap.error("one of --date, --run-dir, --all or --self-test is required")

    problems = []
    for d in dirs:
        problems += check(d, bar)
    if problems:
        print("run_complete: THIS RUN IS NOT DONE.", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        print("\n  The definition of done for this product is a shipped deck. Committing the "
              "evidence\n  and not merging is what a failed run DOES; it is not what finishing "
              "looks like.\n  Keep working the deck, or say plainly that it failed and why.",
              file=sys.stderr)
        return 1
    print(f"run complete: {len(dirs)} run(s), every deck over the {bar} threshold and shipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
