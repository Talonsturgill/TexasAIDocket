#!/usr/bin/env python3
"""compute.py for the 2026-09-29 deck. Every figure is extracted from a claim's own quote in
claims.json by a pattern that must match, or the build stops. Nothing is typed. The two cost
figures are kept apart on purpose: approximately $499.8 million is the judges' own finding for
the generation facilities alone (c20, c21), and $551.8 million is the estimate the City's witness
gave including transmission interconnection and financing (c19, c22). They are never subtracted."""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}

def num(cid, pattern, key="quote"):
    q = C[cid].get(key) or ""
    m = re.search(pattern, q)
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in {key}")
    g = m.group(1).lower()
    if g in WORDS:
        return WORDS[g]
    g = g.replace(",", "").replace("$", "")
    return float(g) if "." in g else int(g)

F = {"_note": "Every value is extracted from a claim quote by compute.py. The two cost figures carry different scopes and are never combined."}
def put(k, v, cids, basis=None, **kw):
    F[k] = {"value": v, "from": cids}
    if basis: F[k]["basis"] = basis
    F[k].update(kw)

put("units", num("c6", r"purchase (\d+) modular"), ["c6"], "modular gas generators El Paso Electric proposes to buy")
put("kw_per_unit", num("c6", r"modular (\d+)-kilowatt"), ["c6"])
put("plant_mw", num("c1", r"operate a (\d+)-megawatt"), ["c1"])
put("acres", num("c8", r"approximately (\d+) acres"), ["c8"])
put("units_per_group_min", num("c7", r"groups of (\w+) or"), ["c7"])
put("units_per_group_max", num("c7", r"groups of \w+ or (\w+)"), ["c7"])
put("first_request_mw", num("c10", r"requested (\d+) MW"), ["c10"])
put("first_request_year", num("c10", r"MW by (\d{4})"), ["c10"])
put("second_request_mw", num("c11", r"additional (\d+) MW"), ["c11"])
put("peak_commit_mw", num("c12", r"\(([\d,]+) MW\)"), ["c12"])
put("peak_commit_year", num("c12", r"end of (\d{4})"), ["c12"])
put("bridge_years_max", num("c23", r"up to (\w+) years"), ["c23"], "the proposed bridge period, an upper bound")
put("bridge_expected_under_years", num("c24", r"less than (\w+) years"), ["c24"], "the EPE witness's expectation")
put("service_life_years", num("c19", r"(\d+)-year service life"), ["c19"])
put("total_cost_musd", num("c20", r"approximately \$([\d.]+) million"), ["c20", "c21"], "the judges' proposed finding, generation facilities only")
put("cash_cost_musd", num("c20", r"cost of \$([\d.]+) million"), ["c20"])
put("afudc_musd", num("c20", r"approximately \$([\d.]+) million in allowance"), ["c20"])
put("cost_incl_tx_musd", num("c22", r"EPE's \$([\d.]+) million estimate"), ["c22", "c19"], "the estimate including transmission interconnection and AFUDC, as the City's witness gave it")
put("usd_per_kw", num("c56", r"cost is \$([\d,]+) per kW"), ["c56", "c19"])
put("generic_ct_usd_per_kw", num("c56", r"compared to \$([\d,]+) per kW"), ["c56"])
put("city_cost_cap_musd", num("c22", r"cap of \$([\d.]+) million"), ["c22"])
put("protestor_comments", num("c45", r"FROM (\d+) PROTESTORS"), ["c45"])
put("ccn_threshold_mw", num("c36", r"more than (\d+) MW"), ["c36"])
parties = [p.strip() for p in re.search(r"counsel: (.*)\.", C["c35"]["quote"]).group(1).replace(" and ", " ").split(",") if p.strip()]
put("hearing_parties", len(parties), ["c35"], "the parties listed as appearing through counsel, counted", listed=parties)

# arithmetic the deck draws but never prints: the bridge's share of the service life, and the
# plant against the committed peak, each a ratio of two lengths at one scale
put("bridge_share_of_life", round(F["bridge_years_max"]["value"] / F["service_life_years"]["value"], 4), ["c23", "c19"],
    "drawn as the bridge's length against the service life's length at one scale, never printed", drawn_only=True)
put("plant_share_of_peak", round(F["plant_mw"]["value"] / F["peak_commit_mw"]["value"], 4), ["c1", "c12"],
    "drawn as the plant's length against the committed peak at one scale, never printed", drawn_only=True)
check_kw = F["units"]["value"] * F["kw_per_unit"]["value"]
put("units_times_rating_kw", check_kw, ["c6"], "a consistency check on the record, never printed", drawn_only=True)

json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print(json.dumps({k: v["value"] for k, v in F.items() if k != "_note"}, indent=0))
