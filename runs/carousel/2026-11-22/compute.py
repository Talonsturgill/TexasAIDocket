#!/usr/bin/env python3
"""Figures for the November 22nd, 2026 carousel, the Dell Med and IC² Institute AI Learning Lab (tx-2026-0257).

Every value is read out of a claim quote by a regex, or computed here from values so read.

RULES, stated so they are choices rather than accidents:
- clinicians is c2's 80 Dell Med clinicians
- half is clinicians // 2, the size of each arm, because c4 says half have Claude and c5 says the other half
  rely on UpToDate. Printed only as a count of chairs or people drawn, or as the word half
- ama_2026_pct and ama_2023_pct are c15's 81% and 38%, the release's citation of an AMA survey. They are
  never set as the lab's finding and never turned into a ratio or a difference on any surface
- ama_year and ama_base_year are c15's 2026 and 2023
- announced_month, announced_day, announced_year are c1's October 20, 2026
- questions is the count of Kang's quoted questions, c9, c10 and c11, counted from the claims list
"""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
def q(cid): return C[cid]["quote"]
def rx(cid, pat):
    m = re.search(pat, q(cid)); assert m, (cid, pat); return m.group(1)
clinicians = int(rx("c2", r"(\d+) Dell Med clinicians"))
half = clinicians // 2
assert half * 2 == clinicians
p26 = int(rx("c15", r"found that (\d+)% of doctors"))
p23 = int(rx("c15", r"the (\d+)% reported in"))
y26 = int(rx("c15", r"a (\d{4}) American Medical Association"))
y23 = int(rx("c15", r"reported in (\d{4})"))
mon = rx("c1", r"Published (\w+) \d+, \d{4}")
day = int(rx("c1", r"Published \w+ (\d+), \d{4}"))
yr = int(rx("c1", r"Published \w+ \d+, (\d{4})"))
questions = sum(1 for cid in ("c9", "c10", "c11") if q(cid).rstrip().endswith("?"))
F = {
 "_note": "Every value is extracted from a claim quote by compute.py, or computed here from values so extracted.",
 "clinicians": {"value": clinicians, "from": ["c2"], "basis": "Dell Med clinicians in the lab"},
 "half": {"value": half, "from": ["c2", "c4", "c5"], "basis": "clinicians // 2, the size of each arm"},
 "ama_2026_pct": {"value": p26, "from": ["c15"], "basis": "percent of doctors using AI in practice, the release citing a 2026 AMA survey"},
 "ama_2023_pct": {"value": p23, "from": ["c15"], "basis": "percent reported in 2023, the release citing the AMA"},
 "ama_year": {"value": y26, "from": ["c15"], "basis": "the survey year"},
 "ama_base_year": {"value": y23, "from": ["c15"], "basis": "the earlier year the release compares with"},
 "announced_month": {"value": mon, "from": ["c1"], "basis": "month of the announcement"},
 "announced_day": {"value": day, "from": ["c1"], "basis": "day of the announcement"},
 "announced_year": {"value": yr, "from": ["c1"], "basis": "year of the announcement"},
 "questions": {"value": questions, "from": ["c9", "c10", "c11"], "basis": "count of the researcher's quoted questions"},
}
json.dump(F, open(HERE / "figures.json", "w"), indent=1, ensure_ascii=False)
print({k: v["value"] for k, v in F.items() if k != "_note"})
