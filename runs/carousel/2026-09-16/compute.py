#!/usr/bin/env python3
"""The two counts this deck computed, so they can be re-run rather than taken on trust.

Every other numeral on the deck is quoted from a source and is declared in aggregates.json with
the string it came out of. These two are the deck's own arithmetic over the claims file, which is
exactly what aggregates.json exists to declare.
"""
import json, re, pathlib

claims = {c["id"]: c for c in json.loads(pathlib.Path("out/2026-09-16/claims.json").read_text())["claims"]}

# 1. THE THREE READINGS. c8 enumerates them in one sentence as a list of "when" clauses.
q8 = claims["c8"]["quote"]
readings = re.findall(r"when the officer|when an officer", q8)
print(f"c8 enumerates {len(readings)} readings  ->  the deck prints 'three things'")

# 2. THE TWO AGENCIES. Distinct federal funders named across the three claims that name one.
funders = set()
for cid in ("c2", "c19", "c30"):
    t = claims[cid]["quote"]
    if "National Science Foundation" in t or "NSF" in t:
        funders.add("National Science Foundation")
    if "Department of Justice" in t:
        funders.add("U.S. Department of Justice")
print(f"distinct federal funders across c2, c19, c30: {len(funders)}  ->  the deck prints 'Two agencies'")
for f in sorted(funders):
    print("   ", f)
