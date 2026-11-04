#!/usr/bin/env python3
"""Figures for carousel no. 66. Every value is read out of a claim quote or computed from values that were."""
import json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
def num(cid, pat):
    m = re.search(pat, C[cid]["quote"]); assert m, (cid, pat); return int(m.group(1))
areas = num("c8", r"spread across (\d+) areas"); assert areas == num("c17", r"same (\d+) study areas")
prior = num("c9", r"conducted in (\d{4})"); assert prior == num("c17", r"City's (\d{4}) effort")
year = num("c10", r"December of (\d{4})")
months = ["October", "November", "December"]
q = C["c10"]["quote"]; first, last = months.index("October"), months.index("December")
assert "October" in q and "December" in q
checks = [("unrestrained", "c4"), ("human supervision", "c5"), ("number of dogs", "c5"), ("owned or stray", "c5")]
for word, cid in checks: assert word.split()[0] in C[cid]["quote"], word
classes = [("stray", "c6"), ("roaming", "c7")]
for word, cid in classes: assert word in C[cid]["quote"].lower(), word
F = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were.",
 "study_areas": {"value": areas, "from": ["c8", "c17"], "basis": "study areas, from 'spread across 32 areas' and 'the same 32 study areas'"},
 "prior_survey_year": {"value": prior, "from": ["c9", "c17"], "basis": "the year of the manual survey the project repeats"},
 "survey_year": {"value": year, "from": ["c10"], "basis": "the year of the automated survey"},
 "years_between": {"value": year - prior, "from": ["c9", "c10"], "basis": "computed: survey_year minus prior_survey_year"},
 "field_months": {"value": last - first + 1, "from": ["c10"], "basis": "computed: calendar months October to December inclusive"},
 "review_checks": {"value": len(checks), "from": ["c4", "c5"], "basis": "computed: the checks the review makes on each detected dog (unrestrained, supervision, number present, owned or stray)"},
 "classes": {"value": len(classes), "from": ["c6", "c7"], "basis": "computed: the two labels a free dog can get, stray or roaming"},
}
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print(json.dumps({k: v["value"] for k, v in F.items() if k != "_note"}))
