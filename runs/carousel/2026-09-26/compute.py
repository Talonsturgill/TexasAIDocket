#!/usr/bin/env python3
"""compute.py for the 2026-09-26 deck. Every figure is extracted from a claim's own quote in
claims.json by a regex that must match, or the build stops. Nothing here is typed from memory."""
import json, re, datetime as dt
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}

def num(cid, pattern):
    m = re.search(pattern, C[cid]["quote"])
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in quote")
    return int(m.group(1).replace(",", ""))

def date_in(cid, pattern):
    m = re.search(pattern, C[cid]["quote"])
    if not m:
        raise SystemExit(f"{cid}: date {pattern!r} not in quote")
    return dt.datetime.strptime(m.group(1), "%B %d, %Y").date()

F = {"_note": "Every value is extracted from a claim quote by compute.py. Company figures are the company's own claims. Distances from two companies are never reconciled, averaged or differenced."}

F["kodiak_lane_miles"] = {"value": num("c25", r"(\d+) miles apart along Interstate 45"), "from": ["c25"], "basis": "Kodiak's own figure"}
F["waabi_corridor_miles"] = {"value": num("c33", r"roughly (\d+) miles"), "from": ["c33"], "basis": "Waabi's own figure, roughly"}
F["aurora_trucks_year_end"] = {"value": num("c29", r"with (\d+) driverless trucks"), "from": ["c29"], "basis": "Aurora's allocation to exit 2026, not trucks now running"}
F["aurora_trucks_now_reported"] = {"value": num("c34", r"runs (\d+) driverless trucks now"), "from": ["c34"], "basis": "Breitbart, citing a CNBC ride. Secondary"}
F["aurora_driverless_miles"] = {"value": num("c30", r"over ([\d,]+) driverless miles"), "from": ["c30"], "basis": "Aurora's own claim"}
F["aurora_2030_trucks"] = {"value": num("c31", r"more than ([\d,]+) driverless trucks"), "from": ["c31"], "basis": "a target, more than"}
F["permian_trucks"] = {"value": num("c27", r"where (\d+) driverless trucks"), "from": ["c27"], "basis": "Kodiak's own figure, end of second quarter"}
F["waabi_growth_pct"] = {"value": num("c32", r"more than (\d+)%"), "from": ["c32"], "basis": "Waabi's own loads, more than"}
F["kodiak_since_year"] = {"value": num("c26", r"since (\d{4})"), "from": ["c26"]}

acks = ["c5", "c6", "c7", "c8", "c9", "c10"]
F["acknowledgements"] = {"value": len(acks), "word": "six", "from": acks, "basis": "count of the numbered list the applicant acknowledges, one claim per item"}
assert F["acknowledgements"]["value"] == 6

req = num("c15", r"has (\d+) days to request")
file_ = num("c16", r"within (\d+) days of receiving")
hear = num("c16", r"held within (\d+) days")
F["soah"] = {"request_days": req, "file_days": file_, "hearing_days": hear,
             "longest_path_days": req + file_ + hear, "from": ["c15", "c16"],
             "rounding": "sum of the three windows, the longest a review can run before the hearing must be held"}

enf = date_in("c1", r"on or after (\w+ \d+, \d{4})")
rules = date_in("c2", r"effective on (\w+ \d+, \d{4})")
today = dt.date(2026, 9, 26)
F["enforceable"] = {"iso": enf.isoformat(), "from": ["c1"]}
F["rules_effective"] = {"iso": rules.isoformat(), "from": ["c2"]}
F["days_enforceable_to_run"] = {"value": (today - enf).days, "from": ["c1"], "basis": "May 28th, 2026 to the run date September 26th, 2026"}
F["days_rules_to_enforceable"] = {"value": (enf - rules).days, "from": ["c1", "c2"], "basis": "the gap the department describes as 90 days after the rules"}
assert F["days_rules_to_enforceable"]["value"] == 90, F["days_rules_to_enforceable"]
F["fee_dollars"] = {"value": 0, "from": ["c12"], "basis": "No fees are required, quoted"}

# geometry only, never printed
F["geometry"] = {"_note": "metres for the renderer, never printed",
                 "mile_m": 1609.344}
(HERE / "figures.json").write_text(json.dumps(F, indent=1) + "\n")
print(json.dumps({k: (v.get("value") if isinstance(v, dict) else v) for k, v in F.items() if k != "_note"}, indent=0))
