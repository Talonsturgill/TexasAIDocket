#!/usr/bin/env python3
"""computed.py — every numeral this deck states that the sources do not state.

THE LAW THIS SERVES. No numeral reaches published copy except quoted from a source or computed
here, from the claims file, by code a reader could rerun. Nothing below is typed. Each figure is
derived from the text of the claim it cites, so a claim that changes changes the figure.
"""
import json, re, sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
claims = {c["id"]: c for c in json.load(open(RUN / "claims.json"))["claims"]}
out = {}

# 1. HOW MANY PARTIES MUST FIND A NOTARY. c5's quote names them in one parenthesis. The count is
#    the length of that list, taken from the source's own enumeration rather than from memory.
q5 = claims["c5"]["quote"]
inside = re.search(r"\(([^)]*)\)", q5).group(1)                 # "ILLE, DSP, and TSP"
parties = [p.strip() for p in re.split(r",\s*(?:and\s+)?|\s+and\s+", inside) if p.strip()]
out["notarizing_parties"] = {
    "value": len(parties), "unit": "parties", "basis": "measured", "from": ["c5"],
    "how": "the members of the parenthesised list in c5's verbatim quote, counted",
    "members": parties}

# 2. HOW MANY WAYS A DEVELOPER HAS TO SHOW SOMETHING. c38's legend defines one letter code per
#    way, as "X = Name (...)". The count is how many such definitions the legend carries.
codes = re.findall(r"\b([A-Z]) = ([A-Z][A-Za-z/\- ]+?) \(", claims["c38"]["quote"])
out["evidence_kinds"] = {
    "value": len(codes), "unit": "kinds of proof", "basis": "measured", "from": ["c38"],
    "how": "the letter definitions in c38's legend, counted",
    "members": [f"{a} = {b.strip()}" for a, b in codes]}

# 3. HOW MANY REQUIREMENT ROWS THE ELIGIBILITY TABLE CARRIES. c39's quote is the contiguous run
#    of rows, one per line. The count is the number of lines in it.
rows = [r.strip() for r in claims["c39"]["quote"].split("\n") if r.strip()]
out["requirement_rows"] = {
    "value": len(rows), "unit": "requirement rows", "basis": "measured", "from": ["c39"],
    "how": "the lines of c39's contiguous quote, counted. c39's own note says a twelfth row, "
           "Site Verification, sits outside this run, so this is the rows inside the quote and "
           "is never described as the whole table",
    "members": rows}

# 4. HOW MANY PROJECTS GALAXY NAMED IN EACH CLASS. Counted over the claims that carry a named
#    project, by which class string their own quote ends in. Never from the 4.2 GW figure, which
#    c26 forbids being treated as a sum.
named = ["c28", "c29", "c30", "c31", "c32"]
base = [c for c in named if re.search(r"classified as Batch Zero Base Load", claims[c]["quote"])]
studied = [c for c in named if re.search(r"classified as Batch Zero Studied Load", claims[c]["quote"])]
out["galaxy_base_load_projects"] = {
    "value": len(base), "unit": "projects", "basis": "measured", "from": base,
    "how": "the claims among c28 to c32 whose own quote reads 'classified as Batch Zero Base Load'"}
out["galaxy_studied_load_projects"] = {
    "value": len(studied), "unit": "projects", "basis": "measured", "from": studied,
    "how": "the claims among c28 to c32 whose own quote reads 'classified as Batch Zero Studied Load'"}

# 5. THE ONE THAT MOVED. A project whose quote says it was submitted as one class and classified
#    as the other. Found by reading the quotes, not by knowing the answer.
moved = [c for c in named
         if re.search(r"submitted \w+ as Base Load", claims[c]["quote"])
         and re.search(r"conditionally classified as Studied Load", claims[c]["quote"])]
out["reclassified_projects"] = {
    "value": len(moved), "unit": "projects", "basis": "measured", "from": moved,
    "how": "the claims among c28 to c32 whose quote carries BOTH 'submitted ... as Base Load' and "
           "'conditionally classified as Studied Load'"}

# 6. THE EXTENDED CLOCK. c3 gives ten business days and a five day extension. Their sum is the
#    longest a respondent can have, and it is arithmetic, so it happens here.
d = int(re.search(r"(\d+) business days", claims["c3"]["quote"]).group(1))
e = int(re.search(r"(\d+)-day extension", claims["c3"]["quote"]).group(1))
out["clock_days"] = {"value": d, "unit": "business days", "basis": "measured", "from": ["c3"],
                     "how": "read out of c3's own quote"}
out["extension_days"] = {"value": e, "unit": "days", "basis": "measured", "from": ["c3"],
                         "how": "read out of c3's own quote"}
out["clock_plus_extension"] = {
    "value": d + e, "unit": "days at the outside", "basis": "modeled", "from": ["c3"],
    "how": f"{d} business days plus a {e} day extension, summed here. MODELED because the source "
           "adds the two units without saying whether the extension is business days, so this is "
           "an upper bound on a respondent's time and is never printed as a deadline"}

json.dump(out, open(RUN / "figures.json", "w"), indent=2, ensure_ascii=False)
for k, v in out.items():
    print(f"{k:32s} {v['value']:>6}  {v['unit']:<22} {v['basis']}")
