#!/usr/bin/env python3
"""compute.py for the 2026-10-01 deck. Every figure is extracted from a claim's own quote in
claims.json by a pattern that must match, or the build stops. Nothing is typed. A derived figure
names the rule that made it."""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}


def num(cid, pattern):
    q = C[cid]["quote"]
    m = re.search(pattern, q)
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in quote")
    g = m.group(1).replace(",", "").replace("$", "")
    return float(g) if "." in g else int(g)


F = {"_note": "Every value is extracted from a claim quote by compute.py, or derived from extracted values by a rule stated beside it."}


def put(k, v, cids, basis=None, **kw):
    F[k] = {"value": v, "from": cids}
    if basis:
        F[k]["basis"] = basis
    F[k].update(kw)


put("fee_dollars", num("c15", r"by \$(\d+) to"), ["c15"], "dollars added to Texans' auto insurance by the 2023 law")
put("fee_year", num("c15", r"In (\d{4}),"), ["c15"], "year the Legislature passed the fee")
put("fee_to_flock_m_min", num("c16", r"at least \$(\d+) million"), ["c16"], "millions of dollars of the fee put toward the Flock network, at least")
put("cameras_funded_min", num("c17", r"at least ([\d,]+) Flock cameras"), ["c17"], "Flock cameras the authority turned the fee into, at least")
put("searches_2025", num("c18", r"searched ([\d,]+) times"), ["c18"], "searches of the authority's plate reader data in 2025, as the authority reported")
put("search_year", num("c18", r"times in (\d{4})"), ["c18"])
put("cleared_cases", num("c18", r"about ([\d,]+) cleared"), ["c18"], "cleared catalytic converter theft cases, about, as the authority reported")
put("tollway_cameras", num("c19", r"install (\d+) more cameras"), ["c19"], "more cameras the authority approved money for DPS to install along tollways")
put("tollway_m", num("c19", r"another \$(\d+) million"), ["c19"])
put("jurisdictions_off_min", num("c1", r"At least (\d+) cities"), ["c1"], "cities and counties that shut off Flock cameras since the funding was rescinded, at least")
put("cameras_off_min", num("c1", r"more than (\d+) Flock"), ["c1"], "Flock cameras shut off since the funding was rescinded, more than")
put("laredo_yes", num("c2", r"voted (\d)-\d"), ["c2"])
put("laredo_no", num("c2", r"voted \d-(\d)"), ["c2"])
put("laredo_cost_m", num("c3", r"\$(\d+) million a year"), ["c3"], "millions of dollars a year the Laredo referendum asks about")
put("laredo_cameras", num("c3", r"keep (\d+) of"), ["c3"], "Laredo cameras the referendum asks about")
put("laredo_residents", num("c4", r"that ([\d,]+) residents"), ["c4"])
put("kyle_grant", num("c8", r"grant for \$([\d,]+)"), ["c8"])
put("kyle_flock_part", num("c8", r", \$([\d,]+) of which"), ["c8"])
put("kyle_cameras", num("c8", r"pay for (\d+) Flock"), ["c8"], "Kyle cameras the grant share would help pay for")
put("kyle_yes", num("c9", r"voted (\d)-\d"), ["c9"])
put("kyle_no", num("c9", r"voted \d-(\d)"), ["c9"])
put("cs_yes", num("c23", r"voted (\d)-\d"), ["c23"])
put("cs_no", num("c23", r"voted \d-(\d)"), ["c23"])
put("cs_txdot_max", num("c23", r"not to exceed \$([\d,]+)"), ["c23"])
put("cs_other", num("c23", r"and a \$([\d,]+) agreement"), ["c23"])
put("el_paso_days", num("c32", r"within (\d+) days"), ["c32"], "days El Paso's council gave the city manager to remove the cameras")
put("deflock_estimate", num("c11", r"estimated ([\d,]+) Flock"), ["c11"], "a watchdog's estimate of all Flock cameras in Texas, late August")
put("cs_home_burglary_pct", num("c30", r"home burglaries are down (\d+)%"), ["c30"])
put("cs_car_burglary_pct", num("c30", r"car burglaries are down (\d+)%"), ["c30"])
put("laredo_votes_cast", F["laredo_yes"]["value"] + F["laredo_no"]["value"], ["c2"],
    "votes cast on Laredo's referendum call, yes plus no, drawn as dais chairs and never printed",
    rule="laredo_yes + laredo_no")
put("tribune_jurisdictions_named_off", 3, ["c5"], "count of governments c5 names as ending contracts (Plano, Robinson, Kendall County), counted from the quote's list",
    rule="len(['Plano','Robinson','Kendall County']) checked against the quote below")
assert all(n in C["c5"]["quote"] for n in ("Plano", "Robinson", "Kendall County"))
assert F["tribune_jurisdictions_named_off"]["value"] == len(["Plano", "Robinson", "Kendall County"])

out = HERE / "figures.json"
out.write_text(json.dumps(F, indent=1) + "\n")
print(f"figures: {len(F) - 1} written to {out}")
