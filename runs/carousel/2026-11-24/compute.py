#!/usr/bin/env python3
"""Figures for the November 24th, 2026 carousel, Texas A&M's CLARKE (tx-2026-0258).

Every value is read out of a claim quote by a regex, or computed here from values so read.

RULES, stated so they are choices rather than accidents:
- hours_low and hours_high are c2's 18 to 24 hours, the developers' own comparison
- hours_low_minutes is hours_low * 60, the low end of that comparison in minutes, so a drawn time
  scale can set 7 minutes and 18 hours on one axis. It is printed only as a drawn length
- homes is c3's "more than 21,000", a floor and never an exact count. disasters is c3's 10
- polygons, views and orthomosaics are c17's dataset counts on the project site
- buildings and minutes are c16's "roughly 2,000 buildings in about 7 minutes", both approximate
- responders, agencies, states are c8's 125, 63 and 14
- season_year is c10's 2024 hurricane season
- No ratio of 7 minutes against 18 hours is published as a number, because the two timings come from
  two pages and the site's clock starts after stitching (c16)
"""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
def q(cid): return C[cid]["quote"]
def rx(cid, pat):
    m = re.search(pat, q(cid)); assert m, (cid, pat); return m.group(1)
def n(s): return int(s.replace(",", ""))
hl = int(rx("c2", r"instead of (\d+) to \d+ hours")); hh = int(rx("c2", r"instead of \d+ to (\d+) hours"))
homes = n(rx("c3", r"more than ([\d,]+) homes")); dis = int(rx("c3", r"in (\d+) major disasters"))
orth = n(rx("c25", r"^([\d,]+) orthomosaics")); views = n(rx("c25", r"([\d,]+) building views")); poly = n(rx("c25", r"([\d,]+) building polygons"))
bld = n(rx("c16", r"roughly ([\d,]+) buildings")); mins = int(rx("c16", r"about (\d+) minutes"))
assert mins == int(rx("c22", r"about (\d+) minutes"))
resp = int(rx("c8", r"^(\d+) emergency responders")); ag = int(rx("c8", r"from (\d+) agencies")); st = int(rx("c8", r"spanning (\d+) states"))
yr = int(rx("c10", r"the (\d{4}) hurricane season"))
F = {
 "_note": "Every value is extracted from a claim quote by compute.py, or computed here from values so extracted.",
 "hours_low": {"value": hl, "from": ["c2"], "basis": "low end of the developers' 18 to 24 hour comparison"},
 "hours_high": {"value": hh, "from": ["c2"], "basis": "high end of that comparison"},
 "hours_low_minutes": {"value": hl * 60, "from": ["c2"], "basis": "hours_low * 60, drawn only as a length on a time scale"},
 "homes": {"value": homes, "from": ["c3"], "basis": "more than this many damaged homes in the training imagery, a floor"},
 "disasters": {"value": dis, "from": ["c3"], "basis": "major disasters in the training imagery"},
 "orthomosaics": {"value": orth, "from": ["c25"], "basis": "orthomosaics in the CRASAR-U-DROIDs dataset"},
 "building_views": {"value": views, "from": ["c25"], "basis": "building views in the dataset"},
 "polygons": {"value": poly, "from": ["c25"], "basis": "building polygons in the dataset"},
 "buildings": {"value": bld, "from": ["c16"], "basis": "roughly this many buildings per finished orthomosaic"},
 "minutes": {"value": mins, "from": ["c16", "c22"], "basis": "about this many minutes per finished orthomosaic"},
 "responders": {"value": resp, "from": ["c8"], "basis": "emergency responders trained"},
 "agencies": {"value": ag, "from": ["c8"], "basis": "agencies those responders come from"},
 "states": {"value": st, "from": ["c8"], "basis": "states, plus Puerto Rico"},
 "season_year": {"value": yr, "from": ["c10"], "basis": "the hurricane season of the Florida and Pennsylvania deployments"},
}
json.dump(F, open(HERE / "figures.json", "w"), indent=1, ensure_ascii=False)
print({k: v["value"] for k, v in F.items() if k != "_note"})
