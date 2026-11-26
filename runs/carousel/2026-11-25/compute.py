#!/usr/bin/env python3
"""Figures for the November 25th, 2026 carousel, UTMB Health's AI lung nodule flagging (tx-2026-0260).

Every value is read out of a claim quote by a regex, or computed here from values so read.

RULES, stated so they are choices rather than accidents:
- share_num and share_den are c17's "two-thirds", parsed from the word, a rough share ("Roughly") with no
  denominator in the release. It is drawn only as 2 of every 3, never as a percent and never as a count
- of_nine is share_num/share_den of nine drawing units, rounded half up: the incidental nodules when nine
  are drawn. A drawing unit, never a count of patients or nodules
- program_start is c3's 2016
- patient_decade is c18's "in her 20s"; relatives_low and relatives_high are c21's "seven or eight"
- vendor_pct is c25's 80%, Bunkerhill's own claim with no baseline. It never appears as UTMB's result
- age_low, age_high, pack_years, quit_years are c28's federal screening criteria
"""
import json, re
from fractions import Fraction
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
def q(cid): return C[cid]["quote"]
def rx(cid, pat):
    m = re.search(pat, q(cid)); assert m, (cid, pat); return m.group(1)
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
ORD = {"half": 2, "halves": 2, "thirds": 3, "third": 3, "quarters": 4, "fourths": 4}
num, den = rx("c17", r"Roughly (\w+)-(\w+) of"), rx("c17", r"Roughly \w+-(\w+) of")
num = WORDS[rx("c17", r"Roughly (\w+)-")]; den = ORD[rx("c17", r"Roughly \w+-(\w+)")]
share = Fraction(num, den)
of_nine = int(share * 9 + Fraction(1, 2))
start = int(rx("c3", r"in (\d{4}) to screen"))
decade = int(rx("c18", r"in her (\d+)s"))
rl = WORDS[rx("c21", r"named (\w+) or \w+ relatives")]; rh = WORDS[rx("c21", r"named \w+ or (\w+) relatives")]
vp = int(rx("c25", r"enables (\d+)% faster"))
al = int(rx("c28", r"aged (\d+) to \d+ years")); ah = int(rx("c28", r"aged \d+ to (\d+) years"))
py = int(rx("c28", r"(\d+) pack-year")); qy = int(rx("c28", r"past (\d+) years"))
F = {
 "_note": "Every value is extracted from a claim quote by compute.py, or computed here from values so extracted.",
 "share_num": {"value": num, "from": ["c17"], "basis": "numerator of roughly two-thirds"},
 "share_den": {"value": den, "from": ["c17"], "basis": "denominator of roughly two-thirds"},
 "of_nine": {"value": of_nine, "from": ["c17"], "basis": "share_num/share_den of 9 drawing units, rounded half up"},
 "units": {"value": 9, "from": ["c17"], "basis": "the drawing unit total for of_nine, a rule not a count"},
 "program_start": {"value": start, "from": ["c3"], "basis": "year the screening program was established"},
 "patient_decade": {"value": decade, "from": ["c18"], "basis": "the patient was in her 20s"},
 "relatives_low": {"value": rl, "from": ["c21"], "basis": "low end of seven or eight relatives"},
 "relatives_high": {"value": rh, "from": ["c21"], "basis": "high end of seven or eight relatives"},
 "vendor_pct": {"value": vp, "from": ["c25"], "basis": "Bunkerhill's own claim, no baseline"},
 "age_low": {"value": al, "from": ["c28"], "basis": "USPSTF lower age"},
 "age_high": {"value": ah, "from": ["c28"], "basis": "USPSTF upper age"},
 "pack_years": {"value": py, "from": ["c28"], "basis": "USPSTF pack-year history"},
 "quit_years": {"value": qy, "from": ["c28"], "basis": "USPSTF years since quitting"},
}
json.dump(F, open(HERE / "figures.json", "w"), indent=1, ensure_ascii=False)
print({k: v["value"] for k, v in F.items() if k != "_note"})
