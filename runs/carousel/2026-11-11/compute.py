#!/usr/bin/env python3
"""Figures for carousel no. 74, SpaceX asks Starbase for a tax abatement on a gas-fired power plant and super-compute
facility on 444 acres beside Brownsville (tx-2026-0246).

Every value is read out of a claim quote by a pattern, or computed here from values that were.

RULES, stated so they are choices rather than accidents:
- capex is the notice's "approximately $24 billion" for INITIAL PHASES, an estimate, never spent money
- water is the Tribune's "up to $220 million", a ceiling, never an amount paid
- water_share_pct is water over capex times 100, rounded to one decimal, and is a comparison of a ceiling with an
  estimate, never of two payments; capex_per_water is capex over water, floored to a whole number
- days_to_hearing counts from this edition's date, 2026-11-11, to the hearing date in the notice
- acres convert to square metres at 4046.8564224 per acre; side_m is the side of a square of that area, rounded to
  the metre, a drawing scale and never the tract's shape (no plat is in the record)
- the moratorium's 90 days are the Tribune's; its start is "last week", so no end date is computed
"""
import json, re, datetime as dt, math
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
def q(cid): return C[cid]["quote"]
def num(cid, pat, f=float):
    m = re.search(pat, q(cid)); assert m, (cid, pat); return f(m.group(1).replace(",", ""))

capex_billion = num("c2", r"approximately \$(\d+) billion", int)
acres = num("c3", r"approximately (\d+)-acre tract", int)
water_million = num("c15", r"up to \$(\d+) million", int)
moratorium_days = num("c13", r"its own (\d+)-day moratorium", int)
m = re.search(r"Wednesday, December (\d+), (\d{4})", q("c4")); hearing = dt.date(int(m.group(2)), 12, int(m.group(1)))
ch312 = num("c5", r"under Chapter (\d+) of the Texas Tax Code", int)
ch380 = num("c5", r"agreement under Chapter (\d+) of the Texas Local", int)
edition = dt.date(2026, 11, 11)
days_to_hearing = (hearing - edition).days
water_share_pct = round(water_million * 1e6 / (capex_billion * 1e9) * 100, 1)
capex_per_water = math.floor(capex_billion * 1e9 / (water_million * 1e6))
area_m2 = acres * 4046.8564224
side_m = round(math.sqrt(area_m2))

F = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were."}
def put(k, v, frm, basis): F[k] = {"value": v, "from": frm, "basis": basis}
put("capex_billion", capex_billion, ["c2"], "estimated capital investment for initial phases, billions of dollars, approximately")
put("acres", acres, ["c3"], "acres in the tract, approximately")
put("water_million", water_million, ["c15"], "millions of dollars SpaceX agreed to give for water and wastewater projects, up to")
put("moratorium_days", moratorium_days, ["c13"], "days in Brownsville's moratorium, per the Tribune")
put("hearing_day", hearing.day, ["c4"], "day of December 2026 the Starbase City Commission meets")
put("hearing_year", hearing.year, ["c4"], "year of the hearing")
put("ch312", ch312, ["c5"], "Texas Tax Code chapter for the abatement")
put("ch380", ch380, ["c5"], "Local Government Code chapter for the economic development agreement")
put("days_to_hearing", days_to_hearing, ["c4"], "days from this edition's date, November 11th 2026, to the hearing")
put("water_share_pct", water_share_pct, ["c15", "c2"], "the water ceiling as a percent of the capex estimate, one decimal")
put("capex_per_water", capex_per_water, ["c2", "c15"], "capex estimate over the water ceiling, floored")
put("side_m", side_m, ["c3"], "side in metres of a square holding the tract's area, a drawing scale only")
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print(json.dumps({k: v["value"] for k, v in F.items() if k != "_note"}))
