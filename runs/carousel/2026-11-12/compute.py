#!/usr/bin/env python3
"""Figures for carousel no. 75, TxDMV's automated vehicle authorization roster (tx-2026-0188).

Every value is read out of a claim quote by a pattern, or computed here from values that were.

RULES, stated so they are choices rather than accidents:
- the 17 company rows are c1 to c17, each row's count read from its own quote
- rows_sum is the sum of the 17 rows and is ASSERTED equal to the report's own total (c19)
- top2 is Waymo plus Tesla Robotaxi; top2_share_pct is top2 over the total times 100,
  rounded half up to a whole percent; rest is the total minus top2, over the other 15 companies
- under_100 counts companies listing fewer than 100 vehicles
- waymo_per_ite is Waymo's count over the smallest row's count, floored to a whole number
- days_enforceable counts from May 28th, 2026 (c26) to the report's data date (c20)
- unit is the drawing unit for a count rendered as objects: one car stands for 10 vehicles,
  each row rounded half up to whole units with a floor of one, a drawing scale and never a fleet
"""
import json, re, datetime as dt, math
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
def q(cid): return C[cid]["quote"]
def row(cid, name):
    m = re.search(re.escape(name) + r"\s+(\d[\d,]*)", q(cid)); assert m, (cid, name)
    return int(m.group(1).replace(",", ""))
NAMES = {"c1": ("Aurora", "dba Aurora"), "c2": ("Avride", "Avride"), "c3": ("Bot Auto", "Bot Auto TX Inc."),
 "c4": ("Atlas Energy Solutions", "dba Atlas Energy Solutions"), "c5": ("Gatik", "Gatik AI Incorporated"),
 "c6": ("International Transport Eng", "Transport Eng"), "c7": ("Kodiak", "Kodiak Robotics Inc."),
 "c8": ("May Mobility", "May Mobility Inc."), "c9": ("MOIA", "MOIA America"), "c10": ("Nuro", "dba Nuro"),
 "c11": ("PlusAI", "PlusAI Inc."), "c12": ("Stack", "Stack Opco LLC"), "c13": ("Tesla Robotaxi", "dba Tesla Robotaxi, LLC"),
 "c14": ("Torc", "Torc Robotics Inc."), "c15": ("Waabi", "Waabi Logistics Inc."), "c16": ("Waymo", "dba Waymo LLC"),
 "c17": ("Zoox", "Zoox, Inc.")}
rows = {short: row(cid, pat) for cid, (short, pat) in NAMES.items()}
companies = int(re.search(r"Total Companies: (\d+)", q("c18")).group(1))
total = int(re.search(r"Total Automated Vehicles: ([\d,]+)", q("c19")).group(1).replace(",", ""))
m = re.search(r"(\d+)/(\d+)/(\d{4})", q("c20")); data_date = dt.date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
m = re.search(r"on or after May (\d+), (\d{4})", q("c26")); enforce = dt.date(int(m.group(2)), 5, int(m.group(1)))
assert len(rows) == companies, (len(rows), companies)
rows_sum = sum(rows.values()); assert rows_sum == total, (rows_sum, total)
def half_up(x): return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
top2 = rows["Waymo"] + rows["Tesla Robotaxi"]
top2_share_pct = half_up(top2 / total * 100)
rest = total - top2
rest_companies = companies - 2
under_100 = sum(1 for v in rows.values() if v < 100)
smallest = min(rows.values())
waymo_per_ite = math.floor(rows["Waymo"] / smallest)
days_enforceable = (data_date - enforce).days
UNIT = 10
units = {k: max(1, half_up(v / UNIT)) for k, v in rows.items()}
units_total = sum(units.values())
ranked = sorted(rows.items(), key=lambda kv: -kv[1])

F = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were."}
def put(k, v, frm, basis): F[k] = {"value": v, "from": frm, "basis": basis}
for cid, (short, _) in NAMES.items():
    key = "n_" + re.sub(r"[^a-z0-9]+", "_", short.lower()).strip("_")
    put(key, rows[short], [cid], f"automated motor vehicles {short} lists on the October 29th report")
    put("u_" + key[2:], units[short], [cid], f"drawn units for {short}, one unit per {UNIT} vehicles, half up, floor 1")
put("companies", companies, ["c18"], "companies on the report")
put("total", total, ["c19"], "automated vehicles on the report")
put("rows_sum", rows_sum, [f"c{i}" for i in range(1, 18)], "sum of the 17 rows, asserted equal to the report's total")
put("top2", top2, ["c16", "c13"], "Waymo plus Tesla Robotaxi")
put("top2_share_pct", top2_share_pct, ["c16", "c13", "c19"], "top2 over the total, percent, rounded half up to a whole number")
put("rest", rest, ["c19", "c16", "c13"], "vehicles held by the other 15 companies")
put("rest_companies", rest_companies, ["c18"], "companies other than the top two")
put("under_100", under_100, [f"c{i}" for i in range(1, 18)], "companies listing fewer than 100 vehicles")
put("smallest", smallest, ["c6"], "the smallest row, International Transport Eng")
put("waymo_per_ite", waymo_per_ite, ["c16", "c6"], "Waymo's count over the smallest row's, floored")
put("days_enforceable", days_enforceable, ["c26", "c20"], "days from May 28th, 2026 to the report's data date")
put("unit", UNIT, [], "vehicles per drawn unit, a drawing scale")
put("units_total", units_total, [f"c{i}" for i in range(1, 18)], "sum of the drawn units")
put("data_day", data_date.day, ["c20"], "day of October the report's data is as of")
put("units", {k: units[k] for k, _ in ranked}, [f"c{i}" for i in range(1, 18)], "drawn units per company, one per unit vehicles, half up, floor 1, in rank order")
u_top2 = units["Waymo"] + units["Tesla Robotaxi"]
put("u_top2", u_top2, ["c16", "c13"], "drawn units for Waymo plus Tesla Robotaxi")
put("u_rest", units_total - u_top2, [f"c{i}" for i in range(1, 18)], "drawn units for the other 15 companies")
put("row_vehicles", UNIT * 10, [], "listed vehicles a full row of ten bays stands for, a drawing scale")
put("rank", [k for k, _ in ranked], [f"c{i}" for i in range(1, 18)], "companies in descending order of count")
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print(json.dumps({k: v["value"] for k, v in F.items() if k != "_note" and not k.startswith(("n_", "u_"))}))
print({k: v for k, v in ranked}); print(units)
