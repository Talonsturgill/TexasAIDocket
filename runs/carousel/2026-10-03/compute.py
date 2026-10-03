#!/usr/bin/env python3
"""compute.py for the 2026-10-03 deck. Every figure is extracted from a claim's own quote in
claims.json by a pattern that must match, or the build stops. Number words are read through one
stated table. Nothing is typed. A derived figure names the rule that made it."""
import json, re, datetime as dt
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
WORDS = {"four": 4}
RUN_DATE = dt.date.fromisoformat(HERE.name) if re.match(r"\d{4}-\d{2}-\d{2}$", HERE.name) else dt.date(2026, 10, 3)


def num(cid, pattern, flags=0):
    q = C[cid]["quote"]
    m = re.search(pattern, q, flags)
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


put("lane_miles", num("c3", r"(\d+) miles apart"), ["c3", "c23"], "miles between the Dallas-Fort Worth and Houston areas along I-45, the company's figure for the driver-out leg")
assert num("c23", r"cover (\d+) miles") == F["lane_miles"]["value"]
put("ikea_route_miles", num("c24", r"(\d+)-mile delivery route"), ["c24"], "miles of IKEA's Baytown to Frisco route the leg is part of")
put("arm_feb", num("c27", r"ARM of (\d+)% as of February"), ["c27"], "readiness measure as of February 2026, percent")
put("arm_apr", num("c27", r"(\d+)% through April"), ["c27"], "readiness measure through April 2026, percent")
put("arm_jul", num("c27", r"(\d+)% as of July"), ["c27"], "readiness measure as of July 2026, percent")
put("arm_aug", num("c7", r"stood at (\d+)%"), ["c7", "c26"], "readiness measure at the end of August 2026, percent of the safety case's claims and evidence materially complete")
assert num("c26", r"reached (\d+)%") == F["arm_aug"]["value"]
assert num("c26", r"up from (\d+)%") == F["arm_jul"]["value"]
put("arm_target", num("c9", r"reach (\d+)%"), ["c9"], "the readiness measure the company expects to reach before launch, percent")
put("arm_open", F["arm_target"]["value"] - F["arm_aug"]["value"], ["c7", "c9"],
    "percentage points of the safety case's claims and evidence not yet materially complete at the end of August, by the company's own measure",
    rule="arm_target - arm_aug")
put("ikea_loads", num("c21", r"more than ([\d,]+) loads"), ["c21"], "loads delivered for IKEA over four years, more than")
put("ikea_miles", num("c22", r"more than ([\d,]+) miles"), ["c22"], "miles autonomously carrying IKEA goods with a safety observer aboard, more than")
put("ikea_years", num("c21", r"last (\w+) years"), ["c21"], "years of the IKEA partnership")
put("autonomous_miles_m", num("c12", r"more than ([\d.]+) million"), ["c12"], "millions of autonomous miles the company has driven since 2019, more than")
put("route_since", num("c11", r"since (\d{4})"), ["c11"], "year the company began hauling Dallas to Houston with safety drivers")
put("atlas_trucks", num("c15", r"into (\d+) driverless trucks"), ["c15"], "driverless trucks owned and operated by Atlas in the Permian as of June 30th, 2026")
put("atlas_hours", num("c16", r"surpassed ([\d,]+) cumulative hours"), ["c16"], "cumulative hours of paid driverless operation in the Permian, more than")
put("enforce_days", num("c32", r"enforceable (\d+) days"), ["c32"], "days after the final rules took effect that TxDMV authorization became enforceable")
put("leg_share_of_route", round(F["lane_miles"]["value"] / F["ikea_route_miles"]["value"], 4), ["c23", "c24"],
    "fraction of IKEA's route the driver-out leg covers, for drawing the leg as a length along the route at one scale; never printed",
    rule="lane_miles / ikea_route_miles, rounded to 4 places")
year_end = dt.date(RUN_DATE.year, 12, 31)
put("days_to_year_end", (year_end - RUN_DATE).days, ["c2", "c9"],
    "days from the run date to December 31st, the last day of the year the company names for its launch",
    rule="date(2026,12,31) - run date")
months = {"arm_feb": 2, "arm_apr": 4, "arm_jul": 7, "arm_aug": 8}
put("arm_series", [[months[k], F[k]["value"]] for k in months], ["c27", "c7"],
    "the readiness measure by month of 2026, month number and percent, for drawing as rendered heights at one scale; the month numbers come from the quote's month names")

out = HERE / "figures.json"
out.write_text(json.dumps(F, indent=1) + "\n")
print(f"figures: {len(F) - 1} written to {out}")
for k, v in F.items():
    if k != "_note":
        print(f"  {k} = {v['value']}")
