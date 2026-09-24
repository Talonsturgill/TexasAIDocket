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

# HOW MANY TIMES A DECK MAY BE SCORED BEFORE THE SEARCH ENDS. Owner's instruction, 2026-08-26.
#
# This file was written against one failure and 2026-08-25 produced its mirror image. That run
# did not stop below the bar. It refused to stop, scored the same deck FIFTEEN times across a
# night, and never shipped, which cost the owner the night and a great deal of money and put no
# deck in front of a reader. An exit code that only ever says "keep going" is not a gate, it is
# a loop, and the two failures are the same mistake pointed in opposite directions.
#
# So the bar now has a bound on the SEARCH beside it, and the owner set it at five: a panel is a
# CHECK on a deck the run already believes is finished, and this run used it as a design loop,
# letting three judges find what a careful pass would have found for nothing. Past `max_rounds`,
# a deck with no hard fail is finished and ships at whatever it scored, and the email and the run record state that
# number and the shortfall out loud. What does NOT move: a hard fail still stops the deck at any
# round, `ship: false` still outranks the arithmetic, and a run under the cap that is under the
# bar is still a failed run. The cap ends the search. It does not lower the standard, and a run
# that reads it as permission to stop trying at round two has misread it: `rounds` is what the
# run ACTUALLY did, and writing a number there the run did not do is a lie in a file this
# project treats as evidence.


def threshold() -> float:
    """The bar, from the rubric itself."""
    import yaml
    doc = yaml.safe_load(RUBRIC.read_text(encoding="utf-8"))
    t = doc.get("threshold")
    if not isinstance(t, (int, float)):
        raise SystemExit(f"run_complete: {RUBRIC} declares no numeric threshold")
    return float(t)


# WHAT THE BAR WAS, BY DATE, for a deck that did not record its own.
#
# A BAR THAT RISES MUST NOT RECLASSIFY THE DECKS IT WAS RAISED OVER, and on 2026-09-16 that
# principle had to be learned twice in one change. `shipped_check` implemented it for decks
# that WROTE `threshold` into score.json and fell through to "the current one" otherwise, which
# was harmless while the bar only ever went down. The bar went up, 6.7 to 8.0, and three
# published decks at 7.42, 7.42 and 7.09 were reported as never having shipped.
#
# The second place was worse and nearly shipped. `scripts/site/site_context.py` decides which
# runs become ARTICLES by calling `threshold()` here, so raising the bar silently unpublished
# every deck between 7.09 and 7.58: fifteen article pages and about three hundred media files,
# the last three decks among them. It surfaced as `site_fresh_check` wanting to DELETE them, and
# the first reading of that was that the builder had a pre-existing bug.
#
# So the history lives HERE, once, and both readers ask it. Dates are the LAST date each bar
# applied to. Read from `config/carousel/scoring_rubric.yaml`'s own git history, plus this
# file's docstring for the pre-rubric bar ("never reached the 7.0 threshold", the 2026-08-19
# run), because the rubric was only created on 2026-09-13.
BAR_HISTORY = (
    ("2026-09-12", 7.0),   # before this repo carried its own rubric
    ("2026-09-15", 6.7),   # rubric created 2026-09-13 at 6.8 and lowered to 6.7 the same day
)


def bar_in_force(deck_date: str) -> float:
    """The threshold a deck of this date was actually held to.

    Anything after the last entry answers to the rubric as it stands, which is correct: a deck
    scored today is answerable to today's bar. A deck that RECORDED its own threshold should be
    read from that instead, and both callers do that first.
    """
    for last_date, bar in BAR_HISTORY:
        if deck_date <= last_date:
            return bar
    return threshold()


def bar_for_run(run_dir) -> float:
    """The bar this run answers to: its own recorded one, else the one in force on its date."""
    from pathlib import Path as _P
    p = _P(run_dir) / "score.json"
    if p.exists():
        try:
            got = json.loads(p.read_text(encoding="utf-8")).get("threshold")
        except (OSError, json.JSONDecodeError):
            got = None
        if isinstance(got, (int, float)) and not isinstance(got, bool):
            return float(got)
    return bar_in_force(_P(run_dir).name)


def max_rounds() -> int | None:
    """The round cap, from the rubric. None when the rubric declares none."""
    import yaml
    doc = yaml.safe_load(RUBRIC.read_text(encoding="utf-8"))
    m = doc.get("max_rounds")
    return int(m) if isinstance(m, (int, float)) else None


# THE LADDER, THE SIBLING'S GATE (owner, 2026-09-24). The bar steps down with the rounds of work a
# deck has had, and at the rubric's `max_rounds` the finished deck ships with its score and the
# shortfall named. There is no hold and no floor from `ladder_from` on. The owner's words, the day
# the floor held carousel no. 33 at 6.418 under 7.01: "The deck should always ship", "if the deck
# doesn't meet the standard, then there's never a reason to stop editing it to actually just meet
# the standard", and "Adopt Alaska's gate". So under the rung before the cap is KEEP EDITING, and
# at the cap it ships. A hard fail is repaired, never shipped and never held.
#
# The floor below stays for decks dated before `ladder_from`, because a gate does not reach back
# and reclassify work it did not judge (the same rule as RATCHET_SINCE).
def _rubric_doc() -> dict:
    import yaml
    return yaml.safe_load(RUBRIC.read_text(encoding="utf-8")) or {}


def ladder_from() -> str | None:
    """The first deck date the ladder governs, from the rubric. None when it declares none."""
    v = _rubric_doc().get("ladder_from")
    return str(v) if v else None


def on_ladder(run_dir) -> bool:
    """A DATED run on or after `ladder_from`. A folder that is not named as a date is not judged by
    date at all: compared as strings, 'r' sorts after '2026-09-24' and was put on the ladder."""
    import re
    lf, name = ladder_from(), Path(run_dir).name
    return bool(lf) and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", name)) and name >= lf


def rung(rounds) -> float | None:
    """The bar a deck must clear after `rounds` scoring rounds. None at or past the cap, where the
    finished deck ships whatever it scored."""
    doc = _rubric_doc()
    cap = doc.get("max_rounds")
    if isinstance(cap, (int, float)) and rounds is not None and rounds >= cap:
        return None
    bar = float(doc["threshold"])
    steps = sorted((x for x in (doc.get("ladder") or []) if isinstance(x, dict)),
                   key=lambda x: int(x.get("from_round", 1)))
    for x in steps:
        if rounds is not None and rounds >= int(x.get("from_round", 1)):
            bar = float(x["threshold"])
    return bar


def _check_ladder(run_dir: Path, d: dict) -> list[str]:
    name = run_dir.name
    got, n = score_of(d), rounds_of(d)
    bad = []
    if got is None:
        bad.append(f"{name}: score.json states no weighted score under any name this repo has "
                   f"used ({', '.join(SCORE_KEYS)})")
    hard = d.get("hard_fails") or []
    if hard:
        bad.append(f"{name}: {len(hard)} hard fail(s) stand. A hard fail is repaired, never "
                   f"shipped and never held: fix it, verify the fix, and the deck ships. "
                   + "; ".join(str(h)[:120] for h in hard))
    ov = d.get("owner_override") or {}
    if got is not None and not hard and not (ov.get("instruction") and ov.get("date")):
        # THE RUNG THE DECK WAS JUDGED AGAINST, when panel.py recorded it (Codex, #357). A later
        # change to the ladder or the cap must not unpublish or rewrite a deck already shipped,
        # the same rule `bar_for_run` keeps for the threshold. None recorded means the cap.
        need = d["rung"] if "rung" in d else rung(n)
        if need is not None and float(got) < need:
            bad.append(f"{name}: KEEP EDITING. {got} after {n if n is not None else 'an unknown number of'} "
                       f"round(s) is under this round's rung of {need}. A low score is a work "
                       f"order, never a reason to stop: fix the judges' named defects, re-render "
                       f"and re-score. At the round cap the finished deck ships whatever it scored")
    return bad


RATCHET_WINDOW = 10          # how many shipped decks the floor looks back over

# THE FLOOR DOES NOT REACH BACKWARDS. It was written on 2026-09-20, and pointed at the corpus it
# came from it failed the already-published 2026-08-30 deck for being under a level nobody had
# stated when it was drawn. A gate does not judge the work that produced it, which this repo has
# now said four times (CONSTRUCTION_SINCE, LAYOUT_SINCE, DECK_SINCE, RESERVE_SINCE) and is the
# right answer here for the same reason. Shipped decks are never rewritten.
RATCHET_SINCE = "2026-09-20"


def ratchet_floor(before: str | None = None, root=None) -> float | None:
    """THE FLOOR UNDER THE ROUND CAP, and it is a RATCHET rather than an aspiration.

    WHY IT EXISTS. 2026-09-20, the owner, on four consecutive shipped decks: "it looks like it
    reverted back ... and again reverting back to the low quality non-bespoke generic artwork".

    They were right, and the mechanism was in this file. `max_rounds` ended the SEARCH, which is
    correct and is what carousel no. 7 needed, and it also ended the STANDARD, which nobody
    decided. Past the cap a deck shipped at whatever it got. So the last twenty scored decks ran
    6.56 to 7.58 against a bar of 8.0, every one under it, four of them carrying the scorer's own
    sentence `This is a HOLD. Keep working the deck`, and every one shipped and merged. The 09-20
    commit message states it outright: "carousel 30 ships at 6.968 under an 8.0 bar at the cap".

    A FIXED FLOOR WOULD BE THE WRONG SHAPE, and it is worth saying why rather than discovering it.
    Set one at 8.0 and nothing ships, for weeks, because the machine has never been there. Set one
    at 6.5 and it licenses the regression it is supposed to stop. Either way a number typed today
    is a guess about a machine that is supposed to be improving, which is the same mistake as
    raising the bar to 8.0 and expecting the craft to follow it.

    So the floor is the MEDIAN OF THE LAST `RATCHET_WINDOW` SHIPPED DECKS, less one judge spread.
    What that buys, exactly:

      - A deck at or above the recent norm ships. The daily product cannot deadlock, and roughly
        half of any recent window clears its own median by construction.
      - A deck BELOW the recent norm does not. Reverting is the one thing made impossible, which
        is the owner's complaint stated as a property.
      - The floor RISES on its own as the craft rises, with nobody editing a number. It is the
        only part of this machine that improves without being told to.

    The tolerance is one median judge spread, measured across this repo's own scored decks rather
    than chosen, because three judges scoring the same deck twice do not return the same number
    and a floor inside that noise would refuse decks for being unlucky.

    None when there is not enough history to measure, and a gate that cannot measure its floor
    does not invent one: it falls back to the behaviour before this existed and says so.
    """
    import statistics
    from pathlib import Path as _P
    root = _P(root) if root else (REPO_ROOT / "runs" / "carousel")
    if not root.exists():
        return None
    rows = []
    for d in sorted(root.iterdir()):
        if before and d.name >= before:
            continue
        f = d / "score.json"
        if not f.exists():
            continue
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        got = score_of(doc)
        if isinstance(got, (int, float)) and not isinstance(got, bool):
            sp = doc.get("spread")
            rows.append((float(got),
                         float(sp) if isinstance(sp, (int, float))
                         and not isinstance(sp, bool) else None))
    if len(rows) < 3:
        return None

    # A ROLLING MEDIAN IS NOT A RATCHET, and calling it one was wrong (2026-09-20, review).
    # Ten decks at 8.0 with a 0.3 spread set the floor at 7.7. Six decks then ship AT 7.7,
    # legally, they enter the window, and the median falls to 7.7 and the floor to 7.4. The same
    # step repeats downward for ever, which is the regression this was written to make impossible
    # doing it one rung at a time. A rolling window follows the corpus wherever it goes, and that
    # is the opposite of a ratchet whichever direction it happens to be moving today.
    #
    # So the floor is the HIGH WATER MARK of that rolling value: the highest level this machine
    # has ever actually held across a full window. It is still derived and still rises on its
    # own. It simply cannot fall, which is the whole word.
    #
    # It cannot deadlock either, and that is worth stating because a floor that only rises sounds
    # like one that eventually stops everything. It rises only when the MEDIAN OF TEN SHIPPED
    # DECKS rose, so every level it holds is a level ten decks already cleared. A machine is never
    # asked for a score its own recent work has not produced.
    best = None
    for i in range(3, len(rows) + 1):
        window = rows[max(0, i - RATCHET_WINDOW):i]
        spreads = [sp for _, sp in window if sp is not None]
        f = statistics.median([sc for sc, _ in window]) - (
            statistics.median(spreads) if spreads else 0.0)
        best = f if best is None else max(best, f)
    return round(best, 3)


def rounds_of(doc: dict):
    """How many scoring rounds the run actually did, if it wrote the number down."""
    for k in ("rounds", "round", "scoring_rounds", "panel_rounds"):
        if isinstance(doc.get(k), (int, float)):
            return int(doc[k])
    return None


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


def check(run_dir: Path, bar: float, cap: int | None = None,
          runs_root: Path | None = None) -> list[str]:
    """Every reason this run is not finished. Empty means the deck shipped."""
    p = run_dir / "score.json"
    if not p.exists():
        return [f"{run_dir.name}: no score.json. A deck that was never scored has not shipped, "
                f"and a run that did not score its deck did not finish"]
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{run_dir.name}: score.json is not JSON ({exc})"]

    if on_ladder(run_dir):
        return _check_ladder(run_dir, d)

    # THE OWNER MAY END THE SEARCH, AND THE MACHINE RECORDS WHO DID (2026-09-02).
    #
    # Until today there was exactly one path under the bar: rounds >= cap. That is right about
    # the STANDARD and it was missing a fact about the world, which is that the bar is the
    # owner's and the owner can spend it. Deck 13 held at 6.562 in 3 rounds and the owner said
    # ship it. With no path for that instruction, a session wanting to obey has one move left:
    # write a round count it did not do. A gate that leaves lying as the only way to comply is a
    # gate that will eventually be lied to.
    #
    # So the override is a PATH rather than a hole. It demands the instruction in the owner's own
    # words and a date, it is refused when the deck carries a hard fail, and every surface that
    # reads this file keeps reporting the real score. It does not lower the bar. It records that
    # somebody with the authority to lower it did, and what they said.
    ov = d.get("owner_override") or {}
    overridden = bool(ov.get("instruction") and ov.get("date"))
    got = score_of(d)
    bad = []
    if got is None:
        bad.append(f"{run_dir.name}: score.json states no weighted score under any name this "
                   f"repo has used ({', '.join(SCORE_KEYS)})")
    elif float(got) < bar:
        n = rounds_of(d)
        if overridden:
            # under the bar, shipped on the owner's instruction, and saying so
            pass
        elif cap is not None and n is not None and n >= cap:
            # SHIPPED UNDER THE BAR, ON THE CAP, AND SAYING SO. This is the one path that is
            # under the threshold and not a failure, and it is only that because the run did the
            # work: `cap` rounds of it. The shortfall is stated rather than rounded away.
            #
            # AND IT IS NOT A FLOORLESS PATH, since 2026-09-20. `ratchet_floor` is the level this
            # machine has actually been holding, and a deck under it is a REGRESSION rather than
            # a deck that fell short of an aspiration. The cap ends the search; it does not end
            # the standard, and for a month it did.
            floor = (None if run_dir.name <= RATCHET_SINCE
                     else ratchet_floor(before=run_dir.name, root=runs_root))
            if floor is not None and float(got) < floor:
                bad.append(
                    f"{run_dir.name}: THE DECK WENT BACKWARDS. {got} against a {bar} bar is "
                    f"under {floor}, which is what the last {RATCHET_WINDOW} shipped decks have "
                    f"actually been holding. The {cap} round cap ends the SEARCH and it does not "
                    f"end the STANDARD. Shipping here is the regression the floor exists to "
                    f"refuse, so keep working the deck or ship fewer frames that clear it")
        else:
            reached = "" if n is None else f" in {n} round(s)"
            bad.append(f"{run_dir.name}: THE DECK DID NOT SHIP. {got} against a {bar} threshold"
                       f"{reached}. The definition of done for this product is a shipped deck. A "
                       f"run that stops here has failed, whatever its record says and whatever "
                       f"its other gates say"
                       + ("" if cap is None else
                          f". The {cap} round cap ends the search and it has not been reached, "
                          f"so keep working the deck"))

    hard = d.get("hard_fails") or []
    if hard and overridden:
        bad.append(f"{run_dir.name}: an owner override does not reach a hard fail. "
                   f"{len(hard)} stand(s), and a hard fail is a claim about a promise this "
                   f"product made in public. The override spends the THRESHOLD and nothing else")
    if hard:
        bad.append(f"{run_dir.name}: {len(hard)} hard fail(s) stand, and any one of them makes "
                   f"the deck unshippable whatever the weighted score says. "
                   + "; ".join(str(h)[:120] for h in hard))

    # `ship: false` beside a passing number means the scorer held it for a reason the number does
    # not carry. Trust the scorer's own verdict over its arithmetic. A deck shipped ON THE CAP is
    # the exception, because there `ship: false` is the scorer stating the shortfall the cap
    # already accepted, and reading it as a hold would put the loop straight back.
    _floor = (None if run_dir.name <= RATCHET_SINCE
              else ratchet_floor(before=run_dir.name, root=runs_root))
    on_cap = (cap is not None and (rounds_of(d) or 0) >= cap
              and score_of(d) is not None and float(score_of(d)) < bar
              and (_floor is None or float(score_of(d)) >= _floor))
    under_bar = score_of(d) is not None and float(score_of(d)) < bar
    if d.get("ship") is False and not bad and not on_cap and not (overridden and under_bar):
        bad.append(f"{run_dir.name}: the scorer set ship: false. A held deck has not shipped even "
                   f"when its weighted score clears the bar")
    return bad


def _check_dict(d: dict, bar: float, cap: int | None):
    """`check` against a score dict, for the self-test. Same code path, no temp dir."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "r"
        p.mkdir()
        (p / "score.json").write_text(json.dumps(d), encoding="utf-8")
        return check(p, bar, cap)


def self_test() -> int:
    check_d = _check_dict
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

    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "2026-01-01"
        d.mkdir()

        def write(doc):
            (d / "score.json").write_text(json.dumps(doc))

        # THE 2026-08-25 DEFECT, replayed: fifteen rounds, never shipped, no deck for a reader.
        write({"weighted_score": 6.68, "ship": False, "hard_fails": [], "rounds": 15})
        # THE OVERRIDE, and every way it must NOT work.
        base = {"weighted_score": 6.562, "rounds": 3, "hard_fails": [], "ship": False}
        ok("a deck under the bar below the cap is a failure without an override",
           check_d(base, 6.8, 5) != [])
        ov = dict(base, owner_override={"instruction": "ship the deck as is", "date": "2026-09-02"})
        ok("...and the owner's instruction, recorded, ends the search",
           check_d(ov, 6.8, 5) == [], str(check_d(ov, 6.8, 5)))
        ok("an override with no instruction is not an override",
           check_d(dict(base, owner_override={"date": "2026-09-02"}), 6.8, 5) != [])
        ok("an override with no date is not an override",
           check_d(dict(base, owner_override={"instruction": "ship it"}), 6.8, 5) != [])
        ok("AN OVERRIDE DOES NOT REACH A HARD FAIL",
           check_d(dict(ov, hard_fails=["a numeral that traces to nothing"]), 6.8, 5) != [])
        ok("...and the deck still reports its real score, never the bar",
           "6.562" in " ".join(check_d(dict(base), 6.8, 5)))

        ok("a deck under the bar ON the round cap is a finished run",
           check(d, 6.8, 5) == [], str(check(d, 6.8, 5)))
        ok("...and with no cap in force it is still a failure", check(d, 6.8, None) != [])

        write({"weighted_score": 6.68, "ship": False, "hard_fails": [], "rounds": 2})
        probs = check(d, 6.8, 5)
        ok("a deck under the bar BELOW the cap is still a failed run", probs != [], str(probs))
        ok("...and the message says the search has not run out",
           any("has not been reached" in p for p in probs), str(probs))

        # THE CAP IS NOT A HARD FAIL OVERRIDE. This is the half a run under pressure would
        # reach for, and it is the half that must not move.
        write({"weighted_score": 6.68, "ship": False, "hard_fails": ["a claim with no source"],
               "rounds": 40})
        ok("a hard fail stops the deck at any number of rounds",
           any("hard fail" in p for p in check(d, 6.8, 10)), str(check(d, 6.8, 5)))

        # A run that did not write down how many rounds it did gets no cap.
        write({"weighted_score": 6.68, "ship": False, "hard_fails": []})
        ok("no round count means no cap, because the cap is a claim about work done",
           check(d, 6.8, 5) != [])

    bar = threshold()
    ok("the rubric's own threshold parses", isinstance(bar, float) and bar > 0, str(bar))
    # PINNED ON PURPOSE, so the bar cannot drift a tenth at a time with nobody able to name the
    # run that moved it. That is the same failure `scoring_rubric.yaml` describes craft drifting
    # under, and it is why changing this number costs a commit here as well as there. It moved
    # from 6.8 to 6.7 on the owner's instruction, 2026-09-13, and from 6.7 to 8.0 on 2026-09-16
    # with the artwork upgrade. The pin did its job that day: the rubric edit alone went red here
    # and the bar could not move without a second deliberate commit naming it.
    ok("...and it is the 8.0 this product is held to", bar == 8.0, str(bar))
    cap = max_rounds()
    ok("...and the rubric declares the round cap beside it", cap == 5, str(cap))

    # THE RATCHET, and every case here is one the cap used to wave through.
    import tempfile as _tf
    with _tf.TemporaryDirectory() as td:
        root = Path(td)

        def deck(name, score, spread=0.3):
            d = root / name
            d.mkdir()
            (d / "score.json").write_text(json.dumps(
                {"weighted_score": score, "spread": spread}), encoding="utf-8")

        ok("no floor without enough history", ratchet_floor(root=root) is None)
        for i, sc in enumerate([7.0, 7.0, 7.0], start=1):
            deck(f"2026-01-0{i}", sc)
        f = ratchet_floor(root=root)
        ok("a floor appears once three decks are scored", f is not None, str(f))
        ok("...and it is the median less one judge spread", f == 6.7, str(f))

        deck("2026-01-04", 9.0)
        ok("one great deck moves the floor by the median and not the mean",
           ratchet_floor(root=root) == 6.7, str(ratchet_floor(root=root)))

        for i in range(5, 12):
            deck(f"2026-01-{i:02d}", 8.0)
        ok("the floor RISES on its own as the craft rises",
           ratchet_floor(root=root) == 7.7, str(ratchet_floor(root=root)))

        # A ROLLING MEDIAN IS NOT A RATCHET. Decks shipping legally AT the floor used to pull it
        # down one rung at a time, for ever, which is the regression this exists to refuse.
        for i in range(12, 21):
            deck(f"2026-01-{i:02d}", 7.7)
        ok("...and decks shipping AT the floor do not pull it down",
           ratchet_floor(root=root) == 7.7, str(ratchet_floor(root=root)))
        for i in range(21, 31):
            deck(f"2026-01-{i:02d}", 6.0)
        ok("...and a run of bad decks does not lower it either",
           ratchet_floor(root=root) == 7.7, str(ratchet_floor(root=root)))
        ok("...and `before` reads only the history that preceded a run",
           ratchet_floor(before="2026-01-04", root=root) == 6.7,
           str(ratchet_floor(before="2026-01-04", root=root)))

    # AND THE SHAPE THAT ACTUALLY SHIPPED FOR A MONTH: at the cap, under the bar, scorer holding.
    with _tf.TemporaryDirectory() as td:
        root = Path(td)
        for i in range(1, 11):
            d = root / f"2026-02-{i:02d}"
            d.mkdir()
            (d / "score.json").write_text(json.dumps(
                {"weighted_score": 7.0, "spread": 0.3}), encoding="utf-8")
        # Inside the floor's own window, after RATCHET_SINCE and before the ladder replaced it.
        run_d = root / "2026-09-22"
        run_d.mkdir()

        def verdict(score):
            (run_d / "score.json").write_text(json.dumps(
                {"weighted_score": score, "spread": 0.3, "rounds": 5, "ship": False,
                 "threshold": 8.0}), encoding="utf-8")
            return check(run_d, 8.0, 5, runs_root=root)

        ok("a deck at the recent norm still ships on the cap", not verdict(7.0))
        probs = verdict(6.2)
        ok("A DECK THAT WENT BACKWARDS IS REFUSED ON THE CAP", bool(probs), "it shipped")
        ok("...and the message names the floor and what it is",
           any("WENT BACKWARDS" in x and "6.7" in x for x in probs), str(probs[:1]))
        ok("...and `ship: false` under the floor is not waved through either",
           any("WENT BACKWARDS" in x for x in probs))

    # THE LADDER (owner, 2026-09-24). Read off the rubric rather than typed, so a later change to
    # the rungs cannot leave these tests asserting numbers the gate no longer uses.
    lf, cap5 = ladder_from(), max_rounds()
    ok("the rubric declares where the ladder starts, and a cap", bool(lf) and bool(cap5), f"{lf} {cap5}")
    top, low = rung(1), rung(cap5 - 1)
    ok("the rungs step DOWN with the rounds and never up", top is not None and low is not None
       and low <= top and all((rung(k) or 0) >= (rung(k + 1) or 0) for k in range(1, cap5 - 1)),
       f"{[rung(k) for k in range(1, cap5)]}")
    ok("at the cap there is no bar: the finished deck ships", rung(cap5) is None and rung(cap5 + 3) is None)
    with tempfile.TemporaryDirectory() as td:
        run_d = Path(td) / lf                                  # a deck the ladder governs
        run_d.mkdir()

        def lad(score, rounds, hard=()):
            (run_d / "score.json").write_text(json.dumps(
                {"weighted_score": score, "rounds": rounds, "ship": False, "hard_fails": list(hard)}))
            return check(run_d, float(top), cap5)

        ok("round 1 at the top rung is done", lad(top, 1) == [], str(lad(top, 1)))
        probs = lad(round(top - 0.01, 2), 1)
        ok("round 1 a hair under the top rung is KEEP EDITING, not a hold",
           any("KEEP EDITING" in x for x in probs) and not any("HOLD" in x or "BACKWARDS" in x for x in probs), str(probs))
        ok(f"the round {cap5 - 1} rung is lower, and a deck on it is done", lad(low, cap5 - 1) == [], str(lad(low, cap5 - 1)))
        ok("AT THE CAP A LOW DECK SHIPS, no floor under it", lad(5.0, cap5) == [], str(lad(5.0, cap5)))
        ok("the 2026-09-24 deck itself, 6.418 on the cap, ships", lad(6.418, cap5) == [])
        probs = lad(9.0, cap5, hard=["an unverified fact presented as verified"])
        ok("a hard fail still stops a deck on the cap, and says repair it",
           any("hard fail" in x and "repaired" in x for x in probs), str(probs))
        (run_d / "score.json").write_text(json.dumps({"weighted_score": 6.0, "rounds": 2, "hard_fails": [],
                                                       "owner_override": {"instruction": "ship it", "date": lf}}))
        ok("an owner override still ends the search under the rung", check(run_d, float(top), cap5) == [])
        (run_d / "score.json").write_text(json.dumps({"weighted_score": low, "rounds": cap5 - 1, "hard_fails": [],
                                                       "rung": round(low - 0.5, 2)}))
        ok("a RECORDED rung wins over the live rubric, so a later ladder cannot unpublish a deck",
           check(run_d, float(top), cap5) == [], str(check(run_d, float(top), cap5)))
        (run_d / "score.json").write_text(json.dumps({"weighted_score": 5.0, "rounds": cap5, "hard_fails": [],
                                                       "rung": None}))
        ok("...and a recorded cap completion stays one", check(run_d, float(top), cap5) == [])
        before = Path(td) / "2026-09-23"                        # the day before: the old rules hold
        before.mkdir()
        (before / "score.json").write_text(json.dumps({"weighted_score": 6.0, "rounds": 2, "ship": False,
                                                        "hard_fails": []}))
        ok("a deck dated before the ladder keeps the rules it was judged under",
           any("DID NOT SHIP" in x for x in check(before, 8.0, cap5)), str(check(before, 8.0, cap5)))

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

    bar, cap = threshold(), max_rounds()
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
        problems += check(d, bar, cap)
    if problems:
        print("run_complete: THIS RUN IS NOT DONE.", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        print("\n  The definition of done for this product is a shipped deck. Committing the "
              "evidence\n  and not merging is what a failed run DOES; it is not what finishing "
              "looks like.\n  Keep working the deck, or say plainly that it failed and why.",
              file=sys.stderr)
        return 1
    # NAME WHICH PATH EACH UNDER-THE-BAR RUN TOOK. There are two now, and reporting an owner's
    # instruction as "on the round cap" is the summary line telling a reader the wrong reason.
    on_cap, by_owner, on_rung = [], [], []
    for d in dirs:
        sp = d / "score.json"
        if not sp.exists():
            continue
        sd = json.loads(sp.read_text(encoding="utf-8"))
        sc = score_of(sd)
        if sc is None or float(sc) >= bar:
            continue
        ov = sd.get("owner_override") or {}
        if ov.get("instruction") and ov.get("date"):
            by_owner.append(d.name)
        elif on_ladder(d) and (sd["rung"] if "rung" in sd else rung(rounds_of(sd))) is not None:
            on_rung.append(d.name)      # cleared a lower rung before the cap, not the cap
        else:
            on_cap.append(d.name)
    parts = []
    if on_cap:
        parts.append(f"{len(on_cap)} under the bar on the {cap} round cap ({', '.join(on_cap)})")
    if on_rung:
        parts.append(f"{len(on_rung)} under the top bar on a lower rung of the ladder "
                     f"({', '.join(on_rung)})")
    if by_owner:
        parts.append(f"{len(by_owner)} under the bar on the owner's instruction "
                     f"({', '.join(by_owner)})")
    note = (", " + ", ".join(parts)) if parts else ""
    print(f"run complete: {len(dirs)} run(s) shipped against a {bar} threshold{note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
