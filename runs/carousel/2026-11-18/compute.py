#!/usr/bin/env python3
"""Figures for the November 18th, 2026 carousel, the UT Dallas satellite and machine learning study of
air pollution and cancer prevalence across Texas counties (tx-2026-0251).

Every value is read out of a claim quote by a regex, or computed here from values so read.

RULES, stated so they are choices rather than accidents:
- counties (c1, c24) is 254 as both the release and the paper's abstract print it, and they must agree
- pollutants is the count printed in c4 and must equal the number of pollutants c4 lists by name
- clusters is the word "three" in c7, mapped to 3
- algorithms is the number of algorithms c20 names, which the abstract also calls "four"
- r_squared is the support vector machine's R squared as c21 prints it. r2_of_100 is r_squared times 100
  rounded to the nearest whole number, used ONLY to draw a 100 cell field with that many cells filled,
  labelled as the model's fit and never as a share of cancers explained by pollution
- morans_i is c22's 0.69, printed as quoted. It measures clustering of cancer prevalence between
  neighbouring counties, never pollution
- data_year is the year in c4 and c24, and they must agree
"""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
def q(cid): return C[cid]["quote"]
def rx(cid, pat):
    m = re.search(pat, q(cid)); assert m, (cid, pat); return m.group(1)
WORDS = {"three": 3, "four": 4, "eight": 8}
counties = int(rx("c1", r"all (\d+) Texas counties"))
assert counties == int(rx("c24", r"all (\d+) Texas counties"))
pollutants = WORDS[rx("c4", r"in \d{4} of (\w+) air pollutants")]
listed = rx("c4", r"air pollutants: (.*)\.$")
names = [n.strip() for n in re.split(r",| and ", listed) if n.strip()]
assert len(names) == pollutants, names
data_year = int(rx("c4", r"satellites in (\d{4})"))
assert data_year == int(rx("c24", r"counties in (\d{4})"))
clusters = WORDS[rx("c7", r"There are (\w+) major clusters")]
algorithms = len([a for a in re.split(r",\s*(?:and\s+)?", q("c20")) if a.strip()])
assert algorithms == 4
r_squared = float(rx("c21", r"R2 = ([\d.]+)"))
r2_of_100 = round(r_squared * 100)
morans_i = float(rx("c22", r"I = ([\d.]+)"))
pub_day = int(rx("c11", r"March (\d+)"))
F = {
 "_note": "Every value is extracted from a claim quote by compute.py, or computed here from values so extracted.",
 "counties": {"value": counties, "from": ["c1", "c24"], "basis": "every Texas county the study covered"},
 "pollutants": {"value": pollutants, "from": ["c4"], "basis": "air pollutants the satellites measured, equal to the names listed"},
 "pollutant_names": {"value": names, "from": ["c4"], "basis": "the eight pollutants in the order c4 lists them"},
 "data_year": {"value": data_year, "from": ["c4", "c24"], "basis": "the year of the satellite readings"},
 "clusters": {"value": clusters, "from": ["c7"], "basis": "major clusters of air pollution, east worst, west best, central between (c8)"},
 "algorithms": {"value": algorithms, "from": ["c20"], "basis": "machine learning algorithms the paper compared"},
 "r_squared": {"value": r_squared, "from": ["c21"], "basis": "the best model's R squared, support vector machine"},
 "r2_of_100": {"value": r2_of_100, "from": ["c21"], "basis": "r_squared x 100 rounded, drawn as filled cells of 100, a model fit"},
 "morans_i": {"value": morans_i, "from": ["c22"], "basis": "clustering of cancer prevalence between neighbouring counties"},
 "pub_day": {"value": pub_day, "from": ["c11"], "basis": "the day in March the paper went online"},
}
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print(json.dumps({k: v["value"] for k, v in F.items() if k != "_note"}))
