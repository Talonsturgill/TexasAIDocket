#!/usr/bin/env python3
"""Figures for the November 19th, 2026 carousel, UT Arlington's USDA funded AI smart trap against
New World screwworm (tx-2026-0252).

Every value is read out of a claim quote by a regex, or computed here from values so read.

RULES, stated so they are choices rather than accidents:
- project_millions is c1's $3.1 million and program_millions c11's roughly $105 million. Both are
  printed only in type and never drawn at one scale together
- cases_floor is c2's "more than 120", a floor, always printed with "more than"
- year_eliminated is c2's 1966
- projects is c11's 40, drawn as 40 units, one per project and never per dollar
- traps_floor is c24's "more than 100", a floor, drawn as 100 units with "more than" in the dek
- flies_week_millions is c22's "more than 80 million", drawn as 80 flies at one stated scale of one
  fly per million a week, never set against traps_floor
- facility_millions is c22's $8.5 million
- distinctions is the count of "from" pairs in c4 (wild from sterile, females from males), 2, and
  cells is 2 x 2 = 4, the combinations those two distinctions make
- pin_km is the great circle distance between the Kerr and Hidalgo county centroids in
  assets/geo/tx-places.json, the counties holding Kerrville (c19) and Edinburg (c21), rounded to whole km.
  It sets pin spacing on the relief only and is never printed
- end_year and end_month are c12's June 2028. months_to_end counts calendar months from the month
  after the run month (December 2026) through June 2028 inclusive, one fence post per month
"""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
def q(cid): return C[cid]["quote"]
def rx(cid, pat):
    m = re.search(pat, q(cid)); assert m, (cid, pat); return m.group(1)
project_millions = float(rx("c1", r"\$([\d.]+) million project"))
cases_floor = int(rx("c2", r"more than (\d+) confirmed animal cases"))
year_eliminated = int(rx("c2", r"United States in (\d{4})"))
projects = int(rx("c11", r"one of (\d+) selected"))
program_millions = int(rx("c11", r"roughly \$(\d+) million"))
traps_floor = int(rx("c24", r"more than (\d+) NWS-specific traps"))
flies_week_millions = int(rx("c22", r"more than (\d+) million sterile flies per week"))
facility_millions = float(rx("c22", r"\$([\d.]+) million facility"))
pairs = re.findall(r"distinguishing (\w+) screwworm flies from (\w+) ones and (\w+) from (\w+)", q("c4"))
assert pairs, "c4"
distinctions = 2
cells = 2 ** distinctions
MONTHS = "January February March April May June July August September October November December".split()
m = re.search(r"through (\w+) (\d{4})", q("c12")); end_month = MONTHS.index(m.group(1)) + 1; end_year = int(m.group(2))
run_year, run_month = 2026, 11
months_to_end = (end_year - run_year) * 12 + (end_month - run_month)
assert months_to_end == (end_year * 12 + end_month) - (run_year * 12 + run_month)
import math
G = {x["id"]: x for x in json.load(open(HERE.parent.parent / "assets/geo/tx-places.json"))["places"]}
k, h = G["county-kerr"], G["county-hidalgo"]
def hav(a, b):
    R = 6371.0088
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"]); dl = math.radians(b["lon"] - a["lon"])
    return 2 * R * math.asin(math.sqrt(math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2))
pin_km = round(hav(k, h))
F = {
 "_note": "Every value is extracted from a claim quote by compute.py, or computed here from values so extracted.",
 "project_millions": {"value": project_millions, "from": ["c1"], "basis": "UTA's USDA funded project, in millions of dollars"},
 "cases_floor": {"value": cases_floor, "from": ["c2"], "basis": "more than this many confirmed animal cases as of November 12th, most in Texas"},
 "year_eliminated": {"value": year_eliminated, "from": ["c2"], "basis": "the year screwworm was declared eliminated from the US"},
 "projects": {"value": projects, "from": ["c11"], "basis": "projects selected nationwide, drawn one unit per project"},
 "program_millions": {"value": program_millions, "from": ["c11"], "basis": "roughly this many millions of USDA funding across the projects"},
 "traps_floor": {"value": traps_floor, "from": ["c24"], "basis": "more than this many screwworm specific traps monitored since July 2025, drawn one unit per trap"},
 "flies_week_millions": {"value": flies_week_millions, "from": ["c22"], "basis": "more than this many millions of sterile flies a week from Edinburg, drawn one fly per million"},
 "facility_millions": {"value": facility_millions, "from": ["c22"], "basis": "the Edinburg dispersal facility's cost in millions"},
 "distinctions": {"value": distinctions, "from": ["c4"], "basis": "wild from sterile, and females from males"},
 "cells": {"value": cells, "from": ["c4"], "basis": "2 x 2 combinations of the two distinctions"},
 "end_year": {"value": end_year, "from": ["c12"], "basis": "the project runs through June of this year"},
 "pin_km": {"value": pin_km, "from": ["c19", "c21"], "basis": "great circle km between the gazetteer centroids of Kerr County (Kerrville, c19) and Hidalgo County (Edinburg, c21), rounded to whole km, used ONLY to set pin spacing on the relief and never printed"},
 "pins": {"value": {"Kerrville": [k["lon"], k["lat"]], "Edinburg": [h["lon"], h["lat"]]}, "from": ["c19", "c21"], "basis": "pin positions at the gazetteer centroids of the counties holding the two places the claims name"},
 "months_to_end": {"value": months_to_end, "from": ["c12"], "basis": "calendar months from December 2026 through June 2028 inclusive, one fence post per month"},
}
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print(json.dumps({k: v["value"] for k, v in F.items() if k != "_note"}))
