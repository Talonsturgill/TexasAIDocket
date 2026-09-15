#!/usr/bin/env python3
"""compute.py — every numeral this deck states that its sources do not state.

THE LAW THIS SERVES. No numeral reaches published copy except quoted from a source or computed
here, from the claims file or from committed data, by code a reader could rerun. Nothing below
is typed.
"""
import json, re, sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = Path("/home/user/TexasAIDocket")
claims = {c["id"]: c for c in json.load(open(RUN / "claims.json"))["claims"]}
out = {}

# 1. HOW MANY RISKS ERCOT'S TABLE CARRIES. Counted as the claims that carry a Description cell
#    of that table, which are the three the fact-checker filed one per row. Never from memory.
rows = [cid for cid in ("c16", "c19", "c22") if cid in claims]
out["risk_rows"] = {
    "value": len(rows), "unit": "risks", "basis": "measured", "from": rows,
    "how": "the claims carrying a Description cell of the Addressing Emerging Operational Risks "
           "table, one per row, counted",
    "members": [claims[c]["quote"][:60] for c in rows]}

# 2. HOW MANY OF THE THREE MITIGATIONS THE SLIDE RECORDS AS IN FORCE. Read off the status cells
#    by whether the cell states an effective date, rather than by knowing the answer. c18 is the
#    only status cell in the table carrying the word `effective`.
status = {"c18": "ride-through", "c21": "oscillations", "c26": "modeling"}
in_force = [c for c in status if "effective" in claims[c]["quote"].lower()]
out["mitigations_in_force"] = {
    "value": len(in_force), "unit": "mitigations", "basis": "measured", "from": in_force,
    "how": "the status cells among c18, c21 and c26 whose own quote contains the word "
           "'effective'. A rule with an effective date is in force and one without is not",
    "members": [status[c] for c in in_force]}
out["mitigations_not_in_force"] = {
    "value": len(status) - len(in_force), "unit": "mitigations", "basis": "measured",
    "from": sorted(set(status) - set(in_force)),
    "how": "the other status cells of the same three, by the same test",
    "members": [status[c] for c in sorted(set(status) - set(in_force))]}

# 3. HOW MANY COUNTIES THE MAP FRAME DRAWS. Counted off the committed geodata the frame renders,
#    not off general knowledge that Texas has 254. If the topology ever changed, so would this.
topo = json.load(open(ROOT / "assets/geo/tx-counties.topo.json"))
key = next(iter(topo["objects"]))
out["counties_drawn"] = {
    "value": len(topo["objects"][key]["geometries"]), "unit": "counties", "basis": "measured",
    "from": ["assets/geo/tx-counties.topo.json"],
    "how": f"the geometries in the committed county topology, object '{key}', counted. This is "
           f"the same file the frame draws from, so the figure and the drawing cannot disagree"}

# 4. HOW MANY PROPER NAMES THE PRESENTATION CARRIES. The absence frame states that the document
#    names no data center, company or generator. a2 enumerates every proper name in it, so the
#    count is the length of that enumeration rather than an assertion about emptiness.
a2 = next(a for a in json.load(open(RUN / "claims.json"))["absences"] if a["id"] == "a2")
m = re.search(r"complete set of proper names in the document is (.+?)\. Everything else",
              a2["how_it_was_looked_for"])
names = [n.strip() for n in re.split(r",\s*(?:and\s+)?|\s+and\s+", m.group(1)) if n.strip()]
out["proper_names_in_document"] = {
    "value": len(names), "unit": "proper names", "basis": "measured", "from": ["a2"],
    "how": "the enumeration inside a2's own how_it_was_looked_for, split on its list separators "
           "and counted. The absence is a2's; this is only its size",
    "members": names}

# 5. HOW MANY PAGES THE PRESENTATION HAS. The caption says "six pages" and the absence claims
#    rest on having read all of them, so the figure is counted off the extraction's own page
#    markers rather than remembered from the fetch.
pages = re.findall(r"^--- PAGE (\d+) ---$", (RUN / "sources" /
                   "ercot-iga-update-2026-09-14.txt").read_text(encoding="utf-8"), re.M)
out["presentation_pages"] = {
    "value": len(pages), "unit": "pages", "basis": "measured",
    "from": ["out/2026-09-15/sources/ercot-iga-update-2026-09-14.txt"],
    "how": "the PAGE markers the showrunner's pypdf extraction wrote, counted. The extraction "
           "carries the source url, its byte count and its SHA256 in its own header",
    "members": pages}

# 6. HOW MANY DOCUMENTS THE DECK RESTS ON. The first comment says "two official records", so the
#    count is the distinct source urls across every claim the deck cites, never a remembered two.
urls = sorted({c["url"] for c in claims.values()})
out["documents_cited"] = {
    "value": len(urls), "unit": "documents", "basis": "measured", "from": sorted(claims),
    "how": "the distinct source urls across every claim in claims.json, counted",
    "members": urls}

json.dump(out, open(RUN / "figures.json", "w"), indent=1)
for k, v in out.items():
    print(f"{v['value']:>6}  {k:28} {v['unit']:16} <- {', '.join(v['from'])[:50]}")
