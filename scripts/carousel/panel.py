#!/usr/bin/env python3
"""panel.py — three judges, a median, and any one hard fail stops the deck.

WHY THIS EXISTS, in one measurement.

On 2026-08-19 the deck was scored twelve times. The first seven were a SINGLE scorer, which is
what `prompts/daily_routine.md` Phase 15 spawns. The last five were three independent judges.

    single scorer, 7 rounds     6.51 6.87 6.93 6.82 6.56 6.62 6.71    ZERO hard fails found
    panel of three, 5 rounds    6.53 7.14 7.01 7.44 8.03             FOUR hard fails found

Two of those four were fabrications that had already survived every gate in the suite and a
full pixel review. One grader had cleared them seven times.

WHAT ONE GRADER STRUCTURALLY CANNOT DO

On three separate rounds all three judges independently named the SAME defect, and twice that
defect had been introduced by the previous round's own fix. A single scorer has no way to tell
a real finding from its own taste, because there is nothing to compare against. Three do: an
agreement is evidence, and a lone objection is a lead worth reading rather than a verdict.

It also stopped the run twice from shipping a number over the bar. At 7.14 and again at 7.44
the deck cleared 7.0 and did not ship, because all three judges named a defect the run had just
created. A number over the threshold is not the definition of done.

THE ARITHMETIC, AND WHY IT IS HERE RATHER THAN IN A PROMPT

**Median, not mean.** One generous judge should not carry a deck and one harsh judge should not
sink it. With three judges the median is the one nobody's outlier moves.

**Hard fails UNION.** Any single judge finding a hard fail stops the deck, whatever the other
two said and whatever the median is. A hard fail is a claim about a promise this product made
in public, and two judges failing to notice it is not evidence it did not happen.

**Spread is reported.** When judges disagree by more than SPREAD_NOTE the deck is not
understood yet, and the disagreement is more informative than the median.

This is a script rather than a paragraph in the routine for the reason the whole repo is built
on: a run under pressure can reason about a paragraph. It computes a number from three files
and cannot be talked out of it, which is the same argument as `run_complete.py`.

    panel.py --date 2026-08-19 --judges a.json b.json c.json --out score.json
    panel.py --self-test
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SCORE_KEYS = ("weighted_score", "score", "weighted_total", "total", "weighted")

# Judges disagreeing by more than this are not looking at the same deck yet.
SPREAD_NOTE = 0.75

# The lenses. Three judges reading identically are one judge with more tokens, which is the
# failure this design exists to avoid. Each is given a different thing to be suspicious of, and
# these three are the ones that actually caught the 2026-08-19 defects.
LENSES = {
    "integrity": "every claim, every numeral, every absence, every noun. Try to REFUTE the deck",
    "craft": "the art as a designer sees it. Value structure, focal, detail budget, per frame",
    "reader": "a Texan seeing this in the feed once. What do they learn and what can they do",
}


def score_of(d: dict) -> float | None:
    for k in SCORE_KEYS:
        if isinstance(d.get(k), (int, float)):
            return float(d[k])
    return None


def criteria_of(j: dict) -> dict:
    """Judge's per-criterion scores as {name: (score, weight)}, in either shape they arrive in."""
    c = j.get("criteria")
    out = {}
    if isinstance(c, dict):
        for k, v in c.items():
            if isinstance(v, dict) and "score" in v:
                out[k] = (float(v["score"]), float(v.get("weight") or 0))
    elif isinstance(c, list):
        for v in c:
            if isinstance(v, dict) and v.get("name") and "score" in v:
                out[v["name"]] = (float(v["score"]), float(v.get("weight") or 0))
    return out


RUBRIC = REPO_ROOT / "config" / "carousel" / "scoring_rubric.yaml"


def threshold() -> float:
    """The bar, read from the rubric the judges are graded against, never carried here.

    `run_complete.py` reads the same key from the same file. Two modules with two copies of one
    number is the defect this repo has now closed four times in other places.
    """
    import yaml
    doc = yaml.safe_load(RUBRIC.read_text(encoding="utf-8"))
    t = doc.get("threshold")
    if not isinstance(t, (int, float)):
        raise SystemExit(f"panel: {RUBRIC} declares no numeric threshold")
    return float(t)


def combine(judges: list, bar: float | None = None) -> tuple:
    """Returns (verdict dict, problems list).

    PER-CRITERION MEDIAN, THEN WEIGHTED, whenever the judges supply criteria. That is what
    actually produced the 2026-08-19 shipped score, and it differs from the cruder method: the
    three judges totalled 8.09, 8.17 and 7.70, whose median is 8.09, while the per-criterion
    medians weight out to 8.034. The finer method is the right one and not because it scored
    lower. A judge can reach the same total by different routes, so a median of totals throws
    away exactly the disagreement the panel exists to surface, and it lets two judges who
    disagree about every criterion look like agreement.

    Falls back to a median of totals when a judge supplies no criteria, because a panel that
    cannot combine is worse than a coarse one.
    """
    if bar is None:
        bar = threshold()
    probs = []
    scores, fails = [], []
    per = {}
    for i, j in enumerate(judges):
        s = score_of(j)
        if s is None:
            probs.append(f"judge {i + 1} returned no score under any of {SCORE_KEYS}")
            continue
        scores.append(s)
        for name, (sc, w) in criteria_of(j).items():
            per.setdefault(name, {"scores": [], "weight": w})
            per[name]["scores"].append(sc)
            if w:
                per[name]["weight"] = w
        for hf in (j.get("hard_fails") or []):
            fails.append({"judge": i + 1, "fail": hf})
        # A judge saying ship is false while reporting no hard fail is still a refusal.
        if j.get("ship") is False and not (j.get("hard_fails") or []):
            fails.append({"judge": i + 1, "fail": "judge returned ship: false with no hard fail "
                                                  "named, which is a refusal either way"})
    if not scores:
        return {}, (probs or ["no judge returned a usable score"])
    if len(scores) < 3:
        probs.append(f"only {len(scores)} judge(s) scored. The panel is three, because a median "
                     f"of two is a mean and one outlier moves it")

    complete = per and all(len(v["scores"]) == len(scores) for v in per.values()) \
        and all(v["weight"] for v in per.values())
    if complete:
        merged = {k: {"score": round(statistics.median(v["scores"]), 3), "weight": v["weight"],
                      "judges": v["scores"]}
                  for k, v in per.items()}
        headline = round(sum(m["score"] * m["weight"] for m in merged.values()), 3)
        method = "per-criterion median across three judges, then weighted by the rubric"
    else:
        if per:
            probs.append("the judges did not all return the same criteria with weights, so the "
                         "panel fell back to a median of totals. That discards the per-criterion "
                         "disagreement this panel exists to surface")
        merged = {}
        headline = round(statistics.median(scores), 3)
        method = "median of judge totals (fallback)"

    spread = max(scores) - min(scores)
    verdict = {
        "weighted_score": headline,
        "judges": [round(s, 3) for s in scores],
        "spread": round(spread, 3),
        "criteria": merged,
        "hard_fails": [f["fail"] for f in fails],
        "hard_fails_by_judge": fails,
        # SHIP IS NOT "the median cleared the bar". It is that AND no judge found a hard fail.
        #
        # AND IT WAS NEITHER, FOR NINE ROUNDS. 2026-08-26.
        #
        # This field read `not fails` and this module never opened the rubric, so a 6.72 deck
        # under a 7.0 bar came back `"ship": true` with no caveat anywhere in the file. The floor
        # lived only in `run_complete.py`, which is a separate command a run has to remember to
        # run. The comment directly above stated the correct rule the whole time and the code
        # implemented half of it, which is the worst arrangement of the two, because the file
        # reads as though it had been thought about.
        #
        # A panel that cannot say "under the bar" is not a panel, it is a hard-fail counter. The
        # bar is read from the same rubric the judges are graded against, so there is one number
        # and not two.
        "ship": (not fails) and headline >= bar,
        "threshold": bar,
        "over_threshold": headline >= bar,
        "method": method,
    }
    if not fails and headline < bar:
        verdict["hold_reason"] = (
            f"no judge found a hard fail, and the median {headline} is under the rubric's "
            f"{bar} bar. This is a HOLD. Keep working the deck")
    if spread > SPREAD_NOTE:
        verdict["note"] = (
            f"the judges disagree by {spread:.2f}, which is wider than {SPREAD_NOTE}. The deck is "
            f"not understood yet and the disagreement is worth more than the median. Read the "
            f"outlier's reasoning before acting on the number")
    # A criterion the judges split on is the most useful thing in this file.
    split = [k for k, m in merged.items() if m["judges"] and max(m["judges"]) - min(m["judges"]) >= 1.5]
    if split:
        verdict["contested"] = split
    return verdict, probs


def count_round(date: str) -> int:
    """How many times this deck has been scored, counted by this module rather than typed.

    THE CAP NEEDS A NUMBER AND A TYPED ONE WOULD BE WORTHLESS. `run_complete` ships a deck that
    is under the bar once `rounds` reaches the rubric's `max_rounds`, which makes that field the
    most valuable lie in the run: a run under pressure could write 10 in it at round two and be
    finished. So the run does not get to write it. Every invocation appends one line here and the
    round number is the length of the file.

    It lives in `out/<date>/`, which is gitignored scratch, and that is the right home: the count
    is a fact about ONE run's session and means nothing to the next one. A round counter that
    survived into `runs/` would be a number a later session could edit.
    """
    log = REPO_ROOT / "out" / date / "panel_rounds.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"date": date}) + "\n")
    return sum(1 for ln in log.read_text(encoding="utf-8").splitlines() if ln.strip())


def run(date: str, paths: list, out: str | None) -> int:
    judges = []
    for p in paths:
        f = Path(p)
        if not f.exists():
            print(f"panel: no judge file at {f}", file=sys.stderr)
            return 1
        judges.append(json.loads(f.read_text(encoding="utf-8")))
    verdict, probs = combine(judges)
    if verdict:
        verdict["rounds"] = count_round(date)
    for p in probs:
        print(f"  note  {p}", file=sys.stderr)
    if not verdict:
        return 1
    dest = Path(out) if out else (REPO_ROOT / "out" / date / "score.json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(verdict, indent=1) + "\n", encoding="utf-8")
    if verdict["ship"]:
        why = f"SHIP (over the {verdict['threshold']} bar, no hard fail)"
    elif verdict["hard_fails"]:
        why = f"{len(verdict['hard_fails'])} hard fail(s), HOLD"
    else:
        why = f"HOLD, under the {verdict['threshold']} bar"
    print(f"panel: {verdict['judges']} -> median {verdict['weighted_score']}, "
          f"spread {verdict['spread']}, round {verdict['rounds']}, {why}")
    print(f"panel: written to {dest}")
    return 0


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    bad = 0

    def ok(label, cond, extra=""):
        nonlocal bad
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            bad += 1

    def j(score, fails=None, ship=True):
        return {"weighted_score": score, "hard_fails": fails or [], "ship": ship}

    BAR = 7.0          # the hermetic bar for these cases, so the rubric can move without
                       # rewriting every assertion below

    # THE REAL FINAL ROUND of 2026-08-19, with the real per-criterion scores. The three judges
    # totalled 8.09, 8.17 and 7.70. A median of TOTALS is 8.09. The per-criterion medians weight
    # out to 8.034, which is what actually shipped, and this asserts the finer method is used.
    W = {"artwork_craft": 0.28, "claim_integrity": 0.20, "story_and_stakes": 0.18,
         "sequence_and_momentum": 0.12, "voice": 0.12, "variety": 0.10}

    def jc(total, per):
        return {"weighted_score": total, "hard_fails": [], "ship": True,
                "criteria": {k: {"score": v, "weight": W[k]} for k, v in per.items()}}

    A = jc(8.09, {"artwork_craft": 8.0, "claim_integrity": 8.5, "story_and_stakes": 8.0,
                  "sequence_and_momentum": 8.0, "voice": 7.5, "variety": 8.5})
    B = jc(8.17, {"artwork_craft": 7.8, "claim_integrity": 8.7, "story_and_stakes": 8.2,
                  "sequence_and_momentum": 8.2, "voice": 7.8, "variety": 9.0})
    C = jc(7.70, {"artwork_craft": 7.5, "claim_integrity": 8.5, "story_and_stakes": 7.8,
                  "sequence_and_momentum": 7.8, "voice": 7.5, "variety": 8.0})
    v, _ = combine([A, B, C])
    ok("the real round-five panel weights to the 8.034 that shipped",
       v["weighted_score"] == 8.034, str(v.get("weighted_score")))
    ok("...by per-criterion median rather than a median of totals",
       "per-criterion" in v["method"] and v["weighted_score"] != 8.09, v["method"])
    ok("...and ships", v["ship"] is True)
    ok("...and the per-criterion medians are kept, so a reader sees where they split",
       v["criteria"]["artwork_craft"]["score"] == 7.8, str(v["criteria"].get("artwork_craft")))

    # A criterion the judges genuinely split on is surfaced by name.
    D = jc(7.5, {"artwork_craft": 9.0, "claim_integrity": 8.5, "story_and_stakes": 8.0,
                 "sequence_and_momentum": 8.0, "voice": 7.5, "variety": 8.5})
    E = jc(7.5, {"artwork_craft": 5.0, "claim_integrity": 8.5, "story_and_stakes": 8.0,
                 "sequence_and_momentum": 8.0, "voice": 7.5, "variety": 8.5})
    v, _ = combine([D, E, A])
    ok("a criterion the judges split on by 1.5 or more is named",
       "artwork_craft" in (v.get("contested") or []), str(v.get("contested")))

    # A judge omitting criteria drops the panel to the coarse method, and says so.
    v, probs = combine([A, B, j(7.70)])
    ok("a judge with no criteria falls back to a median of totals, loudly",
       "fallback" in v["method"] and any("fell back" in p for p in probs), v["method"])

    # THE REAL ROUND ONE, where two judges found hard fails.
    v, _ = combine([j(6.32, ["slide 3 strips c2's date qualifier"], ship=False),
                    j(6.82),
                    j(6.53, ["slide 7 asserts a suppression no claim supports"], ship=False)])
    ok("the real round-one panel medians to 6.53", v["weighted_score"] == 6.53, str(v))
    ok("...and does not ship", v["ship"] is False)
    ok("...and carries BOTH judges' hard fails", len(v["hard_fails"]) == 2, str(v["hard_fails"]))

    # THE PROPERTY THAT MATTERS MOST. A high median does not outvote one hard fail.
    v, _ = combine([j(9.0), j(9.0), j(8.5, ["an unverified fact on slide 4"], ship=False)])
    ok("a 9.0 median with ONE judge's hard fail does NOT ship", v["ship"] is False, str(v))
    ok("...and the median is still reported honestly", v["weighted_score"] == 9.0, str(v))

    # Median resists a single outlier in both directions.
    v, _ = combine([j(6.0), j(7.5), j(7.6)])
    ok("one harsh judge does not sink a deck two judges cleared", v["weighted_score"] == 7.5, str(v))
    v, _ = combine([j(7.4), j(7.5), j(9.9)])
    ok("one generous judge does not carry a deck", v["weighted_score"] == 7.5, str(v))

    # A refusal with no hard fail named is still a refusal.
    v, _ = combine([j(7.5), j(7.5), j(7.5, ship=False)])
    ok("a judge returning ship:false with no hard fail still stops the deck",
       v["ship"] is False, str(v))

    # Disagreement is surfaced.
    v, _ = combine([j(6.2), j(7.0), j(8.1)])
    ok("judges disagreeing by more than the note threshold say so", "note" in v, str(v))
    v, _ = combine([j(7.4), j(7.5), j(7.6)])
    ok("...and judges who agree do not", "note" not in v, str(v))

    # Two judges is not a panel.
    v, probs = combine([j(7.0), j(8.0)])
    ok("a panel of two is flagged, because a median of two is a mean",
       any("median of two is a mean" in p for p in probs), str(probs))

    # A judge with no score at all.
    v, probs = combine([j(7.0), {"criteria": []}, j(7.4)])
    ok("a judge returning no score is reported rather than silently dropped",
       any("no score" in p for p in probs), str(probs))

    ok("three lenses are defined, and they differ", len(LENSES) == 3 and len(set(LENSES.values())) == 3)

    # THE BAR, WHICH THIS MODULE DID NOT READ FOR NINE ROUNDS (2026-08-26).
    v, _ = combine([j(6.52), j(7.14), j(6.36)], bar=BAR)
    ok("a 6.72 median with no hard fail does NOT ship", v["ship"] is False, str(v))
    ok("...and the file says why in words", "under the" in v.get("hold_reason", ""), str(v))
    ok("...and carries the bar it was judged against", v["threshold"] == BAR)
    ok("...and over_threshold is false", v["over_threshold"] is False)
    v, _ = combine([j(7.0), j(7.0), j(7.0)], bar=BAR)
    ok("a median exactly ON the bar ships", v["ship"] is True, str(v))
    ok("...with no hold_reason", "hold_reason" not in v)
    v, _ = combine([j(8.4), j(8.6), j(8.5, ["a fabricated figure on slide 3"], ship=False)], bar=BAR)
    ok("a hard fail still stops a deck well over the bar", v["ship"] is False, str(v))
    ok("...and hold_reason is not used for the hard-fail case, which has its own field",
       "hold_reason" not in v, str(v))
    ok("the live rubric still declares a numeric bar", isinstance(threshold(), float))

    print("\npanel self-test: " + ("all passed" if not bad else f"{bad} FAILED"))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date")
    ap.add_argument("--judges", nargs="*", default=[])
    ap.add_argument("--out")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not (a.date and a.judges):
        ap.error("--date and --judges, or --self-test")
    return run(a.date, a.judges, a.out)


if __name__ == "__main__":
    raise SystemExit(main())
