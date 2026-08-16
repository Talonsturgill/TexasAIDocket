#!/usr/bin/env python3
"""Every numeral this deck publishes that is not quoted verbatim from a source.

The law in CLAUDE.md: a numeral reaches published copy either quoted from a source or
computed by code from the record. Nothing on a slide is typed. Run this, read the JSON,
and copy nothing by hand -- copy.json is generated from it.
"""
import json, math
from pathlib import Path

HERE = Path(__file__).resolve().parent
GAZ = json.loads((HERE.parents[1] / "assets/geo/tx-places.json").read_text(encoding="utf-8"))

# --- inputs, each a figure quoted verbatim in claims.json ------------------------------
FOOTPRINT_SQFT      = 100_000_000    # "The 100-million-square-foot facility"
PHASE_ONE_USD       = 16_800_000_000 # "more than $16.8 billion"
PHASE_ONE_JOBS      = 3_000          # "will create 3,000 new jobs"
TEF_GRANT_USD       = 30_000_000     # "A Texas Enterprise Fund (TEF) grant of $30 million"
FEET_PER_MILE       = 5_280          # a definition, not a measurement

out = {}

# --- the footprint as a square -------------------------------------------------------
# sqrt of an area is a side. This is the whole of slide 1 and it is exact.
side_ft = math.isqrt(FOOTPRINT_SQFT)
assert side_ft * side_ft == FOOTPRINT_SQFT, "not a perfect square, do not round it into copy"
out["footprint_square_side_ft"] = {"value": side_ft, "label": "measured",
    "from": ["c-footprint"], "how": "isqrt(100000000)"}
out["footprint_square_side_mi"] = {"value": round(side_ft / FEET_PER_MILE, 2), "label": "measured",
    "from": ["c-footprint"], "how": "10000 / 5280, rounded to 2 decimals"}
out["footprint_sq_mi"] = {"value": round(FOOTPRINT_SQFT / FEET_PER_MILE**2, 2), "label": "measured",
    "from": ["c-footprint"], "how": "100000000 / 5280^2, rounded to 2 decimals"}

# --- what the state and the company are each putting in per job ----------------------
out["phase_one_usd_per_job"] = {"value": round(PHASE_ONE_USD / PHASE_ONE_JOBS), "label": "measured",
    "from": ["c-phase-one"], "how": "16800000000 / 3000"}
out["tef_usd_per_job"] = {"value": round(TEF_GRANT_USD / PHASE_ONE_JOBS), "label": "measured",
    "from": ["c-phase-one", "c-tef"], "how": "30000000 / 3000"}
out["tef_share_of_phase_one_pct"] = {"value": round(100 * TEF_GRANT_USD / PHASE_ONE_USD, 2),
    "label": "measured", "from": ["c-phase-one", "c-tef"],
    "how": "100 * 30000000 / 16800000000, rounded to 2 decimals"}

# --- the roof against the county it lands in -----------------------------------------
COUNTY_LAND_SQ_MI = 787.467    # Census 2024 gazetteer, GEOID 48185, ALAND_SQMI
out["county_land_sq_mi"] = {"value": COUNTY_LAND_SQ_MI, "label": "measured",
    "from": ["c27"], "how": "quoted from the gazetteer, not computed"}
out["footprint_share_of_county_pct"] = {
    "value": round(100 * (FOOTPRINT_SQFT / FEET_PER_MILE**2) / COUNTY_LAND_SQ_MI, 2),
    "label": "measured", "from": ["c5", "c27"],
    "how": "100 * (100000000 / 5280^2) / 787.467, rounded to 2 decimals"}

# --- where the story is, from the committed gazetteer --------------------------------
county = next(p for p in GAZ["places"] if p["id"] == "county-grimes")
def dm(dec):
    d = int(abs(dec)); m = int(round((abs(dec) - d) * 60))
    if m == 60: d, m = d + 1, 0
    return d, m
lat_d, lat_m = dm(county["lat"]); lon_d, lon_m = dm(county["lon"])
out["county_footer"] = {
    "value": f"GRIMES COUNTY  {lat_d} degrees {lat_m} minutes N  {lon_d} degrees {lon_m} minutes W",
    "label": "measured", "from": ["assets/geo/tx-places.json county-grimes"],
    "how": "area-weighted centroid from us-atlas counties-10m, decimal degrees to degrees and minutes"}
out["county_lonlat"] = {"value": [county["lon"], county["lat"]], "label": "measured",
    "from": ["assets/geo/tx-places.json county-grimes"], "how": "verbatim from the gazetteer"}

# --- the deck's own seed, so the art is reproducible ---------------------------------
out["seed"] = {"value": 20260816, "label": "measured", "from": [], "how": "the run date"}

if __name__ == "__main__":
    (HERE / "computed.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    for k, v in out.items():
        print(f"{k:34s} {v['value']}")
