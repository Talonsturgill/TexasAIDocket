#!/usr/bin/env python3
"""compute.py for the 2026-10-04 deck. Every figure is extracted from a claim's own quote in
claims.json by a pattern that must match, or the build stops. Number words are read through one
stated table. Nothing is typed. A derived figure names the rule that made it."""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "nine": 9, "zero": 0, "third": 3}


def num(cid, pattern, flags=0):
    q = C[cid]["quote"]
    m = re.search(pattern, q, flags)
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in quote")
    g = m.group(1)
    if g.lower() in WORDS:
        return WORDS[g.lower()]
    g = g.replace(",", "")
    return float(g) if "." in g else int(g)


F = {"_note": "Every value is extracted from a claim quote by compute.py, or derived from extracted values by a rule stated beside it."}


def put(k, v, cids, basis=None, **kw):
    F[k] = {"value": v, "from": cids}
    if basis:
        F[k]["basis"] = basis
    F[k].update(kw)


put("districts_approached", num("c16", r"approached at least (\d+) school districts"), ["c16"], "school districts state officials and Alpha affiliates approached, at least")
put("pilot_districts", num("c17", r"at least (\w+) of those districts"), ["c17"], "districts that launched pilots, at least: Houston, Fort Davis, Aldine")
put("declined_districts", num("c19", r"at least (\w+) school districts"), ["c19"], "districts that confirmed they were approached and did not pursue an agreement, at least")
put("approached_unnamed", F["districts_approached"]["value"] - F["pilot_districts"]["value"] - F["declined_districts"]["value"], ["c16", "c17", "c19"],
    "approached districts the reporting names neither as a pilot nor as one that declined, at least this many by the reporting's own floors",
    rule="districts_approached - pilot_districts - declined_districts")
put("board_for", num("c7", r"voted it down (\d+) to \d+"), ["c7"], "board members the Tribune counts voting the Alpha leaders' charter bid down")
put("board_against", num("c7", r"voted it down \d+ to (\d+)"), ["c7"], "board members the Tribune counts on the other side of that vote")
put("board_seats_voting", F["board_for"]["value"] + F["board_against"]["value"], ["c7"], "members counted in the Tribune's tally, for drawing one seat per member", rule="board_for + board_against")
put("fd_students", num("c23", r"enrolls around (\d+) students"), ["c23"], "Fort Davis ISD enrollment, around")
put("aldine_students", num("c24", r"roughly (\d+) students"), ["c24"], "Aldine students the platform is deployed to, roughly")
put("aldine_campuses", num("c24", r"across (\w+) middle school campuses"), ["c24"], "Aldine middle school campuses in the pilot")
put("tea_others", num("c33", r"with (\w+) other TEA leaders"), ["c33"], "TEA leaders besides the commissioner on the repeat campus visit")
put("tea_party", 1 + F["tea_others"]["value"], ["c33"], "people in the commissioner's party on that visit, the commissioner and the others", rule="1 + tea_others")
put("model_hours", num("c34", r"basic subjects in (\w+) hours a day"), ["c34"], "hours a day Alpha's full model gives AI to teach basic subjects")
put("day_hours_on_dial", 12, ["c34"], "hours on a clock face, the dial the model's hours are drawn on; a property of a clock, never printed", rule="constant of the drawn dial")
put("model_dial_degrees", round(360 * F["model_hours"]["value"] / 12, 4), ["c34"], "degrees of a twelve hour dial the model's hours sweep, for drawing; never printed", rule="360 * model_hours / 12")
put("tprep_pass", num("c28", r"just (\d+)% of students passed"), ["c28", "c41"], "percent of Texas Preparatory School students who passed, last year")
assert num("c41", r"from \d+% to (\d+)%") == F["tprep_pass"]["value"]
put("tprep_pass_before", num("c41", r"from (\d+)% to \d+%"), ["c41"], "percent at approaches grade level before the partnership")
put("tprep_grade_before", num("c42", r"dropped from (\d+)% to"), ["c42"], "percent at grade level before the partnership")
put("tprep_grade_after", num("c42", r"to (zero) after"), ["c42"], "percent at grade level after the partnership")
put("tprep_f_ratings", num("c43", r"its (third) consecutive F"), ["c28", "c43"], "consecutive F ratings")
put("alpha_claim_low", num("c39", r"to (\d+)% to \d+% of students passing"), ["c39"], "low end of the passing share an Alpha leader claimed, percent")
put("alpha_claim_high", num("c39", r"to \d+% to (\d+)% of students passing"), ["c39"], "high end of that claimed share, percent")
put("states_rejected", num("c37", r"at least (\w+) states"), ["c37"], "states that rejected Alpha's charter pitch, at least")
put("tprep_fail", 100 - F["tprep_pass"]["value"], ["c28"], "percent who did not pass, for drawing the remainder of a hundred; never printed", rule="100 - tprep_pass")

json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print(json.dumps({k: v["value"] for k, v in F.items() if k != "_note"}))
