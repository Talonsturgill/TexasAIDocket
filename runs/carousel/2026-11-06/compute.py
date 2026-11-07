#!/usr/bin/env python3
"""Figures for carousel no. 70, ExxonMobil's automated Permian rigs (tx-2026-0242).

Every value is read out of a claim quote by a pattern, or computed here from values that were. Number words in a quote
("three", "two", "half", "a third") are mapped by the WORDS table, which is a parse and never an estimate.

UNIT RULES, stated so they are choices rather than accidents:
- pounds to kilograms by the exact international pound, 0.45359237 kg, rounded to the nearest 10 kg (drawing only)
- miles to metres by the international mile, 1609.344 m (drawing only, never printed)
- a drill pipe joint is drawn 9.4 m long (Range 2, a drawing choice disclosed in the storyboard, never printed)
- THE RACK UNIT, a choice and never a claim: one drawn rack of 20 joints stands for the Permian fleet, so a share of
  the fleet is a share of the rack. 25% of 20 is 5 joints and approximately half is 10. Never printed as a count.
"""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
WORDS = {"two": 2, "three": 3, "seven": 7, "nine": 9, "half": 0.5, "a third": 1 / 3, "one-third": 1 / 3}


def q(cid):
    return C[cid]["quote"]


def num(cid, pat, f=float):
    m = re.search(pat, q(cid)); assert m, (cid, pat); return f(m.group(1).replace(",", ""))


def word(cid, pat):
    m = re.search(pat, q(cid)); assert m, (cid, pat); return WORDS[m.group(1)]


rigs_now = word("c1", r"We have (three) in operation today")
share_next_pct = num("c4", r"about (\d+)% of our Permian fleet next year", int)
share_2028 = word("c5", r"approximately (half) by 2028")
year_half = num("c5", r"half by (\d{4})", int)
fleet_aug_floor = num("c16", r"more than (\d+) drilling rigs", int)
auto_aug = word("c17", r"(two) of which are automated")
pipe_lb = num("c19", r"roughly ([\d,]+) pounds", int)
m = re.search(r"drilled (two) miles horizontally underground in a little over (six) days", q("c22")); assert m
lateral_miles = {"two": 2}[m.group(1)]; days_floor = {"six": 6}[m.group(2)]
rank_fastest = {"third": 3}[re.search(r"the (third) fastest time", q("c23")).group(1)]
injury_share = word("c24", r"about (a third) of significant injuries")
incident_potential = word("c8", r"roughly (one-third) of high-consequence")
hp_added = word("c29", r"deploy (seven) additional")
hp_total = word("c29", r"operating to (nine)\.")
hp_months = num("c29", r"over the next (\d+) months", int)
technologies_floor = num("c12", r"more than (\d+) technologies", int)
goal_mboe = num("c13", r"approximately ([\d.]+) million oil-equivalent barrels per day", float)
goal_year = num("c13", r"per day by (\d{4})", int)
assert hp_total - hp_added == 2  # the release's own arithmetic: two deployed before, seven more, nine in all

RACK = 20                                             # the rack unit, a drawing choice (see the docstring)
rack_next = round(RACK * share_next_pct / 100)        # rule: nearest whole joint
rack_2028 = round(RACK * share_2028)
pipe_kg = int(round(pipe_lb * 0.45359237, -1))        # rule: nearest 10 kg, drawing only
lateral_m = round(lateral_miles * 1609.344)           # rule: nearest metre, drawing only
JOINT_M = 9.4                                          # Range 2 joint, drawing choice
STAND_JOINTS = 3                                       # a triple stand, drawing choice
stand_m = round(JOINT_M * STAND_JOINTS, 1)
injury_floor_tiles = 9                                 # a floor drawn as nine plates, a drawing choice
injury_tiles = round(injury_floor_tiles * injury_share)

F = {
 "_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were.",
 "rigs_now": {"value": rigs_now, "from": ["c1"], "basis": "automated rigs in operation, October 30th, 2026 call"},
 "share_next_pct": {"value": share_next_pct, "from": ["c4"], "basis": "about this percent of the Permian fleet next year"},
 "share_2028": {"value": share_2028, "from": ["c5"], "basis": "approximately half of the Permian fleet by 2028, as a fraction"},
 "year_half": {"value": year_half, "from": ["c5"], "basis": "the year of approximately half"},
 "fleet_aug_floor": {"value": fleet_aug_floor, "from": ["c16"], "basis": "more than this many Permian rigs, Reuters, August; a floor, never a count"},
 "auto_aug": {"value": auto_aug, "from": ["c17"], "basis": "automated rigs at the time of the August report"},
 "pipe_lb": {"value": pipe_lb, "from": ["c19"], "basis": "roughly this many pounds per tall steel pipe"},
 "pipe_kg": {"value": pipe_kg, "from": ["c19"], "basis": "computed, pounds to kg, nearest 10 kg; drawing mass only, never printed"},
 "lateral_miles": {"value": lateral_miles, "from": ["c22"], "basis": "miles drilled horizontally by the first automated rig"},
 "lateral_m": {"value": lateral_m, "from": ["c22"], "basis": "computed, miles to metres; drawing only, never printed"},
 "days_floor": {"value": days_floor, "from": ["c22"], "basis": "a little over this many days"},
 "rank_fastest": {"value": rank_fastest, "from": ["c23"], "basis": "the third fastest time in Exxon's history"},
 "injury_share": {"value": round(injury_share, 4), "from": ["c24"], "basis": "about a third of significant injuries happen on the rig floor"},
 "incident_potential": {"value": round(incident_potential, 4), "from": ["c8"], "basis": "stated POTENTIAL, roughly one-third of high-consequence incidents; never a result"},
 "hp_added": {"value": hp_added, "from": ["c29"], "basis": "additional FlexRobotics systems over the next 12 months"},
 "hp_total": {"value": hp_total, "from": ["c29"], "basis": "FlexRobotics systems operating for ExxonMobil after the expansion"},
 "hp_before": {"value": hp_total - hp_added, "from": ["c29"], "basis": "computed, total less additional"},
 "hp_months": {"value": hp_months, "from": ["c29"], "basis": "the window for the seven"},
 "technologies_floor": {"value": technologies_floor, "from": ["c12"], "basis": "more than this many technologies in the Permian"},
 "goal_mboe": {"value": goal_mboe, "from": ["c13"], "basis": "approximately this many million oil-equivalent barrels a day"},
 "goal_year": {"value": goal_year, "from": ["c13"], "basis": "the year of the production goal"},
 "rack_unit": {"value": RACK, "from": [], "basis": "drawing unit, a choice: one rack of 20 joints stands for the Permian fleet; never printed"},
 "rack_next": {"value": rack_next, "from": ["c4"], "basis": "computed: share_next_pct of rack_unit, nearest joint"},
 "rack_2028": {"value": rack_2028, "from": ["c5"], "basis": "computed: share_2028 of rack_unit"},
 "joint_m": {"value": JOINT_M, "from": [], "basis": "drawing choice, Range 2 joint length in metres; never printed"},
 "stand_m": {"value": stand_m, "from": [], "basis": "computed: a triple stand of joint_m joints; drawing only"},
 "injury_floor_tiles": {"value": injury_floor_tiles, "from": [], "basis": "drawing choice: the floor as nine plates; never printed"},
 "injury_tiles": {"value": injury_tiles, "from": ["c24"], "basis": "computed: injury_share of the nine plates"},
}
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print(json.dumps({k: v["value"] for k, v in F.items() if not k.startswith("_")}))
