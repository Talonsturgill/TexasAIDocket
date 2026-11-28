#!/usr/bin/env python3
"""Figures for the November 27th, 2026 carousel, the Comptroller's proposed Rule 3.308 (tx-2026-0255).

Every value is read out of a claim quote by a regex, or computed here from values so read.

RULES, stated so they are choices rather than accidents:
- state_fyNNNN are the fiscal note's General Revenue Fund 0001 losses, c26 to c31, in whole dollars
- local_fyNNNN are the fiscal note's losses to cities, counties and transit authorities, c32 to c37
- every one is the comptroller's own ESTIMATE of a proposed rule, never a measured loss
- state_total and local_total are the sum of the six fiscal years each, computed here
- *_bn values are dollars divided by 1e9, rounded half up to one decimal place, for type only
- state_growth_x is state_fy2032 over state_fy2027, rounded half up to one decimal place
- sheet_usd is the drawing unit, one sheet of paper per $1,000,000 of the estimate, a rule and never a count
- *_sheets is the loss divided by sheet_usd, rounded DOWN to whole sheets, *_reams and *_loose split it into 500 sheet reams
- *_stack_mm is *_sheets times 0.1 mm, the thickness of one sheet, rounded half up to one decimal
- hosted_named is the count of services c25 names, cloud computing, artificial intelligence, quantum computing
- tax_year is c7's 1987, window_days is c41's 30, adoption_day is c43's December 20
"""
import json, re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
def rx(cid, pat):
    m = re.search(pat, C[cid]["quote"]); assert m, (cid, pat); return m.group(1)
def money(cid, fy):
    return int(rx(cid, r"\$([\d,]+) in fiscal year " + str(fy)).replace(",", ""))
def r1(x):
    return float(Decimal(str(x)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
YEARS = list(range(2027, 2033))
state = {fy: money(f"c{26 + i}", fy) for i, fy in enumerate(YEARS)}
local = {fy: money(f"c{32 + i}", fy) for i, fy in enumerate(YEARS)}
F = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values so extracted. Every dollar is the comptroller's own estimate of a proposed rule."}
for i, fy in enumerate(YEARS):
    F[f"state_fy{fy}"] = {"value": state[fy], "from": [f"c{26 + i}"], "basis": f"estimated loss to General Revenue Fund 0001 in fiscal year {fy}"}
    F[f"state_fy{fy}_bn"] = {"value": r1(state[fy] / 1e9), "from": [f"c{26 + i}"], "basis": "state loss in billions, half up to one decimal, for type"}
    F[f"local_fy{fy}"] = {"value": local[fy], "from": [f"c{32 + i}"], "basis": f"estimated loss to cities, counties and transit authorities in fiscal year {fy}"}
    F[f"local_fy{fy}_m"] = {"value": int(Decimal(local[fy] / 1e6).quantize(Decimal("1"), rounding=ROUND_HALF_UP)), "from": [f"c{32 + i}"], "basis": "local loss in millions, half up to a whole number, for type"}
st, lt = sum(state.values()), sum(local.values())
F["state_total"] = {"value": st, "from": [f"c{n}" for n in range(26, 32)], "basis": "sum of the six state fiscal years 2027 to 2032"}
F["state_total_bn"] = {"value": r1(st / 1e9), "from": [f"c{n}" for n in range(26, 32)], "basis": "state_total in billions, half up to one decimal"}
F["local_total"] = {"value": lt, "from": [f"c{n}" for n in range(32, 38)], "basis": "sum of the six local fiscal years 2027 to 2032"}
F["local_total_bn"] = {"value": r1(lt / 1e9), "from": [f"c{n}" for n in range(32, 38)], "basis": "local_total in billions, half up to one decimal"}
F["state_growth_x"] = {"value": r1(state[2032] / state[2027]), "from": ["c26", "c31"], "basis": "state_fy2032 over state_fy2027, half up to one decimal"}
F["years_counted"] = {"value": len(YEARS), "from": [f"c{n}" for n in range(26, 32)], "basis": "fiscal years the note counts, 2027 to 2032"}
F["tax_year"] = {"value": int(rx("c7", r"in (\d{4})")), "from": ["c7"], "basis": "year the Legislature taxed data processing, per Huffines"}
F["window_days"] = {"value": int(rx("c41", r"no later than (\d+) days")), "from": ["c41"], "basis": "comment window from publication"}
import datetime as _dt
pub = _dt.datetime.strptime(rx("c45", r"Register (\w+ \d+, \d{4})"), "%B %d, %Y").date()
close = pub + _dt.timedelta(days=F["window_days"]["value"])
F["comment_close_month"] = {"value": close.strftime("%B"), "from": ["c45", "c41"], "basis": "publication date plus window_days"}
F["comment_close_day"] = {"value": close.day, "from": ["c45", "c41"], "basis": "publication date plus window_days, the last day comments can arrive"}
F["publication_day"] = {"value": pub.day, "from": ["c45"], "basis": "Texas Register issue date"}
F["adoption_day"] = {"value": int(rx("c43", r"December (\d+), 2026")), "from": ["c43"], "basis": "earliest possible adoption, December 20th"}
SHEET = 1_000_000
F["sheet_usd"] = {"value": SHEET, "from": ["c26"], "basis": "drawing unit, one sheet per $1,000,000 of the estimate, a rule"}
F["ream_sheets"] = {"value": 500, "from": ["c26"], "basis": "sheets in a ream, a drawing rule"}
for kind, src, base in (("state", state, 26), ("local", local, 32)):
    for i, fy in enumerate(YEARS):
        sh = src[fy] // SHEET
        cid = [f"c{base + i}"]
        F[f"{kind}_fy{fy}_sheets"] = {"value": sh, "from": cid, "basis": "loss over sheet_usd, rounded down"}
        F[f"{kind}_fy{fy}_reams"] = {"value": sh // 500, "from": cid, "basis": "whole reams of 500 sheets"}
        F[f"{kind}_fy{fy}_loose"] = {"value": sh % 500, "from": cid, "basis": "sheets left over after whole reams"}
        F[f"{kind}_fy{fy}_stack_mm"] = {"value": r1(sh * 0.1), "from": cid, "basis": "sheets times 0.1 mm"}
F["hosted_named"] = {"value": len(re.findall(r"cloud computing|artificial intelligence|quantum computing", C["c25"]["quote"])), "from": ["c25"], "basis": "services the proposal names as hosted technology"}
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print({k: v["value"] for k, v in F.items() if k != "_note" and not k.endswith(("_m",))})
