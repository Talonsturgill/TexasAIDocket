#!/usr/bin/env python3
"""Every number this deck states by counting rather than by quoting, computed from the claims.

NOT ONE OF THESE IS TYPED. The deck asserts one count in display type, "Three bodies, one
answer", and a count is a fresh factual assertion in the largest type on the page. It is derived
here from the parties the fetched documents actually name in the chain, so a reader who disagrees
with the number can see which sentence each party came out of.

The rest of the deck's numerals are QUOTED and are traced in claims.json rather than here.
"Twenty five megawatts and larger" is c12's own audience line. Every date on every frame is
inside a claim quote. Nothing on any frame was summed, converted, ranked or rounded.
"""
import json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
for cand in (HERE / "claims.json", HERE.parents[2] / "out" / HERE.name / "claims.json"):
    if cand.exists():
        CLAIMS_PATH = cand
        break
else:
    raise FileNotFoundError("no claims.json beside %s" % HERE)

claims = {c["id"]: c for c in json.loads(CLAIMS_PATH.read_text())["claims"]}

# THE CHAIN, and each party is read out of a quote rather than listed by hand. c13 is the
# sentence that names the two institutions and the direction the answer travels. c16 names the
# party that has to sign. A party counts once, whichever sentence it turns up in.
CHAIN_SOURCES = ("c13", "c16")
PARTY_PATTERNS = {
    "the water board": r"\bTWDB\b",
    "the grid operator": r"\bERCOT\b",
    "the developer": r"\bdata center developer\b",
}

found = {}
for cid in CHAIN_SOURCES:
    quote = claims[cid]["quote"]
    for party, pat in PARTY_PATTERNS.items():
        if re.search(pat, quote):
            found.setdefault(party, []).append(cid)

bodies = sorted(found)

out = {
    "bodies_in_the_chain": len(bodies),
    "bodies": {p: found[p] for p in bodies},
    "sources_read": list(CHAIN_SOURCES),
}

if __name__ == "__main__":
    print(json.dumps(out, indent=2))
