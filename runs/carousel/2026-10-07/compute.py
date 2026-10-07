#!/usr/bin/env python3
"""compute.py for the 2026-10-07 deck, Saronic's Port Alpha at the Port of Brownsville (tx-2026-0204).
Every figure is extracted from a claim's own quote in claims.json by a pattern that must match, or the
build stops. Unit conversions use exact definitions stated beside them. Nothing is typed by hand."""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
WORDS = {"two": 2, "four": 4}

FT_M = 0.3048            # international foot, exact by definition
ACRE_M2 = 4046.8564224   # international acre, exact by definition
NMI_M = 1852.0           # international nautical mile, exact by definition


def num(cid, pattern):
    q = C[cid]["quote"]
    m = re.search(pattern, q)
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in quote")
    g = m.group(1)
    if g.lower() in WORDS:
        return WORDS[g.lower()]
    g = g.replace(",", "")
    return float(g) if "." in g else int(g)


F = {"_note": "Every value is extracted from a claim quote by compute.py, or derived from extracted values by a rule stated beside it."}


def put(k, v, cids, basis=None, **kw):
    F[k] = {"value": v, "from": cids}
    if basis:
        F[k]["basis"] = basis
    F[k].update(kw)


put("acres", num("c2", r"on (\d+) acres"), ["c2"], "acres Port Alpha sits on at the Port of Brownsville")
put("acres_option", num("c3", r"nearly ([\d,]+) acres"), ["c3"], "acres the site has an option to expand to, nearly")
put("invest_b", num("c4", r"more than \$(\d+) billion"), ["c4"], "billions of dollars of private capital, more than, per Saronic")
put("jobs", num("c5", r"up to ([\d,]+) direct jobs"), ["c5"], "direct jobs expected, up to, per Saronic")
put("gross_tons_initial", num("c7", r"initial ([\d,]+) gross tons"), ["c7"], "gross tons of annual shipbuilding capacity at opening")
put("gross_tons_potential_m", num("c8", r"over (\d+) million gross tons"), ["c8"], "million gross tons the capacity could scale to, over")
put("vessel_ft", num("c9", r"up to (\d+) feet"), ["c9"], "feet, the longest vessel the yard can build at first")
put("vessel_future_ft", num("c10", r"over ([\d,]+)$"), ["c10"], "feet, vessels the expanded site could build, over")
put("enclosed_msf", num("c11", r"([\d.]+) million square feet"), ["c11"], "million square feet of enclosed production space")
put("buildings_min", num("c12", r"across (\d+) to"), ["c12"], "production buildings, the low end")
put("buildings_max", num("c12", r"to (\d+) dedicated"), ["c12"], "production buildings, the high end")
put("quay_ft", num("c13", r"more than ([\d,]+) feet"), ["c13"], "feet of deepwater quay, more than")
put("positions_min", num("c14", r"^(\w+) to"), ["c14"], "build positions for final ship erection, the low end")
put("positions_max", num("c14", r"to (\w+) build"), ["c14"], "build positions for final ship erection, the high end")
put("marauder_knots", num("c23", r"top speed of (\d+)\+ knots"), ["c23"], "knots, the Marauder's top speed, 25+ per Saronic")
put("marauder_range_nmi", num("c23", r"up to ([\d,]+) nautical miles"), ["c23"], "nautical miles, the Marauder's range, up to")
put("marauder_payload_t", num("c23", r"capacity of (\d+) metric tons"), ["c23"], "metric tons, the Marauder's modular payload")
put("tax_break_m", num("c26", r"\$(\d+) million"), ["c26"], "millions of dollars, the tax break the Tribune reported")
put("tribune_cost_b", num("c27", r"\$([\d.]+) billion"), ["c27"], "billions, the shipyard's cost as the Tribune wrote it in June")
put("abatement_pct", num("c28", r"(\d+)% tax abatement"), ["c28"], "percent property tax abatement, as the Tribune reported")
put("abatement_years", num("c28", r"over (\d+) years"), ["c28"], "years the abatement runs, as the Tribune reported")
put("local_pct", num("c29", r"^(\d+)%"), ["c29"], "percent of the full time workforce required to be local residents")
put("jobs_engineering", num("c35", r"Another ([\d,]+) positions"), ["c35"], "engineering and design jobs, the Tribune's breakdown")
put("jobs_admin", num("c35", r"design, (\d+) in administration"), ["c35"], "administration and support jobs")
put("jobs_rd", num("c35", r"and (\d+) in research"), ["c35"], "research and development jobs")
put("edc_incentive_m", num("c36", r"\$(\d+) million"), ["c36"], "millions, the Greater Brownsville EDC's additional incentive")
put("navy_contract_m", num("c38", r"\$(\d+) million"), ["c38"], "millions, the Navy contract the Tribune reported")

# DERIVED, each by the rule beside it
put("quay_m", round(F["quay_ft"]["value"] * FT_M, 1), ["c13"], "metres of quay, feet times 0.3048", rule="quay_ft * 0.3048, one decimal")
put("vessel_m", round(F["vessel_ft"]["value"] * FT_M, 1), ["c9"], "metres, the longest vessel at first", rule="vessel_ft * 0.3048, one decimal")
put("vessel_future_m", round(F["vessel_future_ft"]["value"] * FT_M, 1), ["c10"], "metres, the expanded site's vessels", rule="vessel_future_ft * 0.3048, one decimal")
put("site_m2", round(F["acres"]["value"] * ACRE_M2), ["c2"], "square metres of site", rule="acres * 4046.8564224, whole")
put("site_side_m", round((F["acres"]["value"] * ACRE_M2) ** 0.5, 1), ["c2"], "metres on a side, the site drawn as a square of its own area", rule="sqrt(acres * 4046.8564224); a drawing rule, the parcel's real shape is not in the record")
put("option_side_m", round((F["acres_option"]["value"] * ACRE_M2) ** 0.5, 1), ["c3"], "metres on a side, the option drawn as a square of its own area", rule="sqrt(acres_option * 4046.8564224); a drawing rule")
put("vessels_along_quay", F["quay_ft"]["value"] // F["vessel_ft"]["value"], ["c9", "c13"], "whole 850 foot hulls end to end along the quay, at least", rule="quay_ft // vessel_ft, floor, since the quay is more than its stated length")
put("abated_share_pct", 100 - F["abatement_pct"]["value"], ["c28"], "percent of the abated tax still owed in the abatement's terms", rule="100 - abatement_pct")
put("local_jobs_at_full", F["jobs"]["value"] * F["local_pct"]["value"] // 100, ["c5", "c29"], "local residents among the full workforce if the up to figure were reached", rule="jobs * local_pct / 100; a projection on a projection, never published as a count")
put("marauder_range_km", round(F["marauder_range_nmi"]["value"] * NMI_M / 1000), ["c23"], "kilometres, the Marauder's range", rule="nmi * 1852 / 1000, whole")
put("option_multiple", round(F["acres_option"]["value"] / F["acres"]["value"], 1), ["c2", "c3"], "times the first site, the option to expand", rule="acres_option / acres, one decimal")

STEEL_T_M3 = 7.85        # density of carbon steel in tonnes per cubic metre, a stated drawing rule
put("payload_block_m3", round(F["marauder_payload_t"]["value"] / STEEL_T_M3, 2), ["c23"], "cubic metres of solid steel weighing the Marauder's payload", rule="payload_t / 7.85 t per m3, two decimals; a drawing rule for one block of steel")
put("payload_block_edge_m", round((F["marauder_payload_t"]["value"] / STEEL_T_M3) ** (1 / 3), 3), ["c23"], "metres on a side, that block drawn as a cube", rule="cube root of payload_block_m3, three decimals")
CREW_DRAWN = 20          # workers drawn on frame 8, a drawing rule
put("crew_drawn", CREW_DRAWN, ["c29"], "workers drawn at the hull on frame 8", rule="a drawing rule, twenty people")
put("crew_local_drawn", CREW_DRAWN * F["local_pct"]["value"] // 100, ["c29"], "of those twenty, the share the 35% local requirement names", rule="crew_drawn * local_pct / 100")

json.dump(F, open(HERE / "figures.json", "w"), indent=1)
for k, v in F.items():
    if k != "_note":
        print(f"{k:24s} {v['value']}")
