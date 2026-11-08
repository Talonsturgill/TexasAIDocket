#!/usr/bin/env python3
"""Figures for carousel no. 71, Dallas's AI cameras on its brush trucks (tx-2026-0179).

Every value is read out of a claim quote by a pattern, or computed here from values that were. Number words are
mapped by the WORDS table, a parse and never an estimate.

RE-SOURCED ON NOVEMBER 8TH. The first build read the Dallas Morning News through www.govtech.com, whose robots.txt
names ClaudeBot with Disallow / for the whole host. Those claims are withdrawn (tmp/claims_govtech_withdrawn.json).
The counts here come from the city's September 8th memo as FOX 4 and Dallas Express reported it, and from the city's
own December 2025 briefing.

RULES, stated so they are choices rather than accidents:
- The memo's counts (properties scanned, notices, cases, citations) measure different things. Nothing here forms a
  funnel or a rate between them, and no ratio computed below is printed except the memo's own 68 percent.
- DRAWING UNITS, never printed as findings: one card of 0.2 mm stands for one property scanned (frame 6), and on frame 7
  one fanned card stands for one citation, 39 left of a lane line and the rest right of it.
- mph to metres per second by the international mile, 0.44704, nearest 0.1 m/s (drawing only, never printed).
"""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
WORDS = {"three": 3, "four": 4}


def q(cid):
    return C[cid]["quote"]


def num(cid, pat, f=int):
    m = re.search(pat, q(cid)); assert m, (cid, pat); return f(m.group(1).replace(",", "").replace("$", ""))


F = {}
def put(name, value, src, basis):
    F[name] = {"value": value, "from": src, "basis": basis}


cameras_plan = num("c1", r"Implement (\d+) AI-enabled cameras")
cams_per_vehicle = num("c3", r"(\d+) cameras mounted on")
mph_lo = num("c4", r"\((\d+)-\d+ MPH\)"); mph_hi = num("c4", r"\(\d+-(\d+) MPH\)")
contract_total = num("c9", r"\$([\d,]+)")
contract_years = WORDS[re.search(r"a (three)-year contract", q("c9")).group(1)]
per_year = num("c10", r"\$([\d,]+) per year")
notice_days = num("c11", r"with (\d+) days")
conditions = len([b for b in q("c8").split("•")[1:] if b.strip()])          # the briefing's bulleted list, counted
properties_scanned = num("c46", r"scanned ([\d,]+) properties")
memo_violations = num("c46", r"resulted in ([\d,]+) violations")
citations = num("c47", r"^(\d+) citations")
properties = num("c47", r"at (\d+) properties")
assert (citations, properties) == (num("c50", r"says (\d+) citations"), num("c50", r"at (\d+) properties"))   # two reports of one memo agree
notices = num("c53", r"approximately ([\d,]+) property owners")
cases = num("c52", r"about (\d+) cases")
south_citations = num("c55", r"memo, (\d+) citations")
south_pct = num("c55", r"or (\d+)%")
districts = len(re.split(r",\s*|\s+and\s+", re.search(r"Districts ([\d, and]+?) in", q("c55")).group(1)))
terms = 3                                                                     # see the assert: cost (c10), appropriations (c9), termination (c11)
assert all(k in q(c) for k, c in (("per year", "c10"), ("appropriations", "c9"), ("terminate", "c11")))
trays = 3                                                                     # reviewed, courtesy notice (c53), case opened (c52)
assert conditions == 8 and districts == 3 and contract_total == per_year * contract_years, (conditions, districts)
assert round(100 * south_citations / citations) == south_pct, (south_citations, citations, south_pct)   # the memo's share re-derived

put("cameras_plan", cameras_plan, ["c1"], "AI-enabled cameras the December 2025 briefing planned")
put("cams_per_vehicle", cams_per_vehicle, ["c3"], "cameras mounted on one city vehicle")
put("mph_lo", mph_lo, ["c4"], "lower speed at which the cameras photograph")
put("mph_hi", mph_hi, ["c4"], "upper speed at which the cameras photograph")
put("speed_ms", round(mph_hi * 0.44704, 1), ["c4"], "computed, the upper speed in m/s for the drawn motion blur; never printed")
put("contract_total", contract_total, ["c9"], "estimated three-year contract, dollars")
put("contract_years", contract_years, ["c9"], "contract term in years")
put("per_year", per_year, ["c10"], "contract cost per year, dollars")
put("notice_days", notice_days, ["c11"], "days of written notice to terminate")
put("conditions", conditions, ["c8"], "property conditions the briefing lists, counted from its list")
put("properties_scanned", properties_scanned, ["c46"], "properties the cameras scanned, per the September 8th memo")
put("memo_violations", memo_violations, ["c46"], "violations that resulted in notices, per the memo as FOX 4 reported it")
put("citations", citations, ["c47", "c50"], "citations issued, per the memo")
put("properties", properties, ["c47", "c50"], "properties the citations went to")
put("notices", notices, ["c53"], "property owners sent courtesy notices, approximately")
put("cases", cases, ["c52"], "cases opened for in-person inspection, about")
put("south_citations", south_citations, ["c55"], "citations in Council Districts 4, 8 and 7")
put("south_pct", south_pct, ["c55"], "the memo's share of citations in those districts, re-derived from 39 of 57")
put("districts", districts, ["c55"], "southern Dallas council districts named, counted")
put("terms", terms, ["c9", "c10", "c11"], "contract terms drawn on frame 8, counted by the assert")
put("trays", trays, ["c52", "c53"], "trays on frame 3: reviewed, courtesy notice, case opened")
F["_note"] = "Every value is extracted from a claim quote by compute.py, or computed here from values that were."
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print(json.dumps({k: v["value"] for k, v in F.items() if k != "_note"}))
