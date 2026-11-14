#!/usr/bin/env python3
"""Figures for carousel no. 77, the Texas Semiconductor Innovation Fund's award to Texas Tech for an AI computing cluster
in Lubbock (tx-2026-0247).

Every value is read out of a claim quote by a pattern, or computed here from values that were.

RULES, stated so they are choices rather than accidents:
- the November award is "over $19 million" (c1). nov_floor_m is that floor and is never treated as exact: no sum, ratio
  or difference uses it as if it were the award
- the May award is "roughly $4.5 million" (c17). It is approximate and is never summed with anything either
- the January award (c15) and the clean room total (c16) are exact as stated, so tech_match_m is total minus award
- awards_2026 counts the dated 2026 announcements this record holds from the fund to this college: January (c15),
  May (c17) and November (c1, c2). It is a count of announcements, not of dollars
- DRAWING UNIT. One 200 mm wafer stands for $1 million (usd_m_per_wafer). It is a drawing scale and never a count of
  wafers made or bought. jan_wafers and match_wafers are exact counts at that unit. may_whole is the whole wafers in
  roughly $4.5 million and may_part the remainder, drawn as a cleaved half and never as an exact half million.
  nov_wafers is the November floor at that unit, drawn with no far end plate because the award is over that amount
- pitch_mm is the boat's slot pitch, a drawing choice for legibility at feed size, never a real boat's pitch
- any drawing unit is a drawing scale and never money: it is declared here with the rule that rounds it
"""
import json, re, datetime as dt
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
def q(cid): return C[cid]["quote"]
def num(cid, pat, cast=float):
    m = re.search(pat, q(cid)); assert m, (cid, pat)
    v = cast(m.group(1).replace(",", "")); return int(v) if float(v).is_integer() else v

nov_floor_m = num("c1", r"over \$(\d+)")
jan_award_m = num("c15", r"\$(\d+) million")
room_total_m = num("c16", r"to \$(\d+) million")
may_award_m = num("c17", r"roughly \$([\d.]+) million")
chips_act_year = num("c19", r"Act in (\d{4})")
tech_match_m = room_total_m - jan_award_m
assert "November 13, 2026" in q("c2")
usd_m_per_wafer = 1
jan_wafers = int(jan_award_m / usd_m_per_wafer)
match_wafers = int(tech_match_m / usd_m_per_wafer)
may_whole = int(may_award_m // usd_m_per_wafer)
may_part = round(may_award_m / usd_m_per_wafer - may_whole, 6)
nov_wafers = int(nov_floor_m / usd_m_per_wafer)
assert match_wafers == jan_wafers and may_part > 0
pitch_mm = 16
wafer_mm = 200
awards_2026 = len(["c15", "c17", "c1"])

F = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were."}
def put(k, v, frm, basis): F[k] = {"value": v, "from": frm, "basis": basis}
put("nov_floor_m", nov_floor_m, ["c1"], "the November award's stated floor in millions of dollars, over this amount, never exact")
put("jan_award_m", jan_award_m, ["c15"], "the January award toward the clean room, millions of dollars")
put("room_total_m", room_total_m, ["c16"], "the clean room project total after Texas Tech's match, millions of dollars")
put("tech_match_m", tech_match_m, ["c15", "c16"], "the clean room total minus the January award, Texas Tech's match")
put("may_award_m", may_award_m, ["c17"], "the May award, roughly this many millions of dollars, never exact")
put("chips_act_year", chips_act_year, ["c19"], "the year the Texas CHIPS Act was signed")
put("awards_2026", awards_2026, ["c15", "c17", "c1"], "dated 2026 announcements of awards from the fund to this college in the record")
put("usd_m_per_wafer", usd_m_per_wafer, [], "DRAWING UNIT: one wafer stands for this many millions of dollars")
put("jan_wafers", jan_wafers, ["c15"], "wafers in the January boat at the drawing unit")
put("match_wafers", match_wafers, ["c15", "c16"], "wafers in Texas Tech's matching boat at the drawing unit")
put("may_whole", may_whole, ["c17"], "whole wafers in the May boat at the drawing unit")
put("may_part", may_part, ["c17"], "the remainder of roughly 4.5 at the drawing unit, drawn as a cleaved half wafer")
put("nov_wafers", nov_wafers, ["c1"], "wafers in the November boat at the drawing unit, the floor, with no far end plate")
put("pitch_mm", pitch_mm, [], "DRAWING CHOICE: boat slot pitch in millimetres")
put("wafer_mm", wafer_mm, [], "DRAWING CHOICE: wafer diameter in millimetres")
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
json.dump({k: v["value"] for k, v in F.items() if k != "_note"}, open(HERE / "computed.json", "w"), indent=1)
print(json.dumps({k: v["value"] for k, v in F.items() if k != "_note"}))
