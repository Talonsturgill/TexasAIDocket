#!/usr/bin/env python3
"""Figures for the November 26th, 2026 carousel, Texas Tech's FleetSpace tools for Army aviation (tx-2026-0263).

Every value is read out of a claim quote by a regex, or computed here from values so read.

RULES, stated so they are choices rather than accidents:
- phase_hours is c5's 480-hour phase maintenance interval, a maintenance interval and never a count
- restored_pct is c6's 37% of missing and corrupted flight data restored, in testing
- volume_cut_pct and files_cut_pct are c6's ceilings ("up to"), never averages
- volume_left_pct and files_left_pct are 100 minus each ceiling, the share left at the ceiling
- restored_of_100 is restored_pct cells of a 100 cell drawing grid, a drawing unit and never a count of records
- students_floor is c11's "more than 18", always drawn and written as more than 18
- partner_since is c12's 2019, partner_years is the run year minus it
- capstones is c18's "three"
- tools is the two tools c9 names, FSUI and PSV
"""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
def rx(cid, pat):
    m = re.search(pat, C[cid]["quote"]); assert m, (cid, pat); return m.group(1)
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
RUN_YEAR = 2026
phase = int(rx("c5", r"(\d+)-hour phase"))
restored = int(rx("c6", r"restored (\d+)% of missing"))
vol = int(rx("c6", r"data volume by up to (\d+)%"))
files = int(rx("c6", r"data files up to (\d+)%"))
students = int(rx("c11", r"more than (\d+) undergraduate"))
since = int(rx("c12", r"since (\d{4})"))
caps = WORDS[rx("c18", r"completed (\w+) capstone")]
tools = len(re.findall(r"\b(FSUI|PSV)\b", C["c9"]["quote"].split(",")[0]))
F = {
 "_note": "Every value is extracted from a claim quote by compute.py, or computed here from values so extracted.",
 "phase_hours": {"value": phase, "from": ["c5"], "basis": "the 480-hour phase maintenance interval the networks predicted actions for, in testing"},
 "restored_pct": {"value": restored, "from": ["c6"], "basis": "percent of missing and corrupted flight data restored, in testing"},
 "restored_of_100": {"value": restored, "from": ["c6"], "basis": "restored_pct cells of a 100 cell drawing grid, a drawing unit"},
 "grid_cells": {"value": 100, "from": ["c6"], "basis": "the drawing grid for restored_of_100, a rule not a count"},
 "volume_cut_pct": {"value": vol, "from": ["c6"], "basis": "ceiling on data volume reduction, up to"},
 "files_cut_pct": {"value": files, "from": ["c6"], "basis": "ceiling on data file reduction, up to"},
 "volume_left_pct": {"value": 100 - vol, "from": ["c6"], "basis": "100 minus volume_cut_pct"},
 "files_left_pct": {"value": 100 - files, "from": ["c6"], "basis": "100 minus files_cut_pct"},
 "students_floor": {"value": students, "from": ["c11"], "basis": "more than 18 students, a floor"},
 "partner_since": {"value": since, "from": ["c12"], "basis": "year IMMS and AVX began partnering"},
 "partner_years": {"value": RUN_YEAR - since, "from": ["c12"], "basis": "run year 2026 minus partner_since"},
 "capstones": {"value": caps, "from": ["c18"], "basis": "capstone projects students completed"},
 "tools": {"value": tools, "from": ["c9"], "basis": "the two tools provided to the Army, FSUI and PSV"},
}
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print({k: v["value"] for k, v in F.items() if k != "_note"})
