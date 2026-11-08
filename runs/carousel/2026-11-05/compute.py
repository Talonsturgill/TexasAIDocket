#!/usr/bin/env python3
"""Figures for carousel no. 69. Every value is read out of a claim quote or computed from values that were.

UNIT RULE. c2's 330,000 is total manufacturing equipment capacity in units, across every product and site. c3 and c4
count pieces of 800G and 1.6 Tb products. The deck never puts c2 on the same scale as c3 and c4 and never prints a
ratio between them. The pad floor carries c3 and c4 only, at one drawing unit.
"""
import json, re, math, datetime
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}


def num(cid, pat, f=float):
    m = re.search(pat, C[cid]["quote"]); assert m, (cid, pat); return f(m.group(1).replace(",", ""))


cap_now = num("c2", r"approaching ([\d,]+) units per month", int)
cap_2026 = num("c3", r"produce over ([\d,]+) pieces", int)
cap_2027_m = num("c4", r"over (\d+) million pieces", int)
cap_2027 = cap_2027_m * 1_000_000
gill_sqft = num("c8", r"approximately ([\d,]+) square feet", int)
kirby_sqft = num("c10", r"approximately ([\d,]+) square feet", int)
m = re.search(r"approximately ([\d,]+) and ([\d,]+) rentable square feet", C["c11"]["quote"]); assert m
cr4_sqft, cr5_sqft = int(m.group(1).replace(",", "")), int(m.group(2).replace(",", ""))
months_to_done = num("c12", r"approximately (\d+) months", int)
lease_term_months = num("c14", r"term of (\d+) months", int)
assert "On August 31, 2026" in C["c11"]["quote"]
lease_date = datetime.date(2026, 8, 31)
run_date = datetime.date(2026, 11, 5)
assert "2026" in C["c3"]["quote"] and "2027" in C["c4"]["quote"]

# THE DRAWING UNIT, a choice and never a claim: one taped machine pad stands for 50,000 pieces of 800G and 1.6 Tb
# product a month. Chosen so the 2027 floor is a whole number of pads. Never printed on a slide.
PAD_UNIT = 50_000
assert cap_2027 % PAD_UNIT == 0 and cap_2026 % PAD_UNIT == 0
pads_2027 = cap_2027 // PAD_UNIT
pads_2026 = cap_2026 // PAD_UNIT

# areas. Rule: square feet to square metres by the exact international foot (0.3048 m), a square's side as the root
SQFT_M2 = 0.3048 ** 2
areas = {"gill": gill_sqft, "kirby": kirby_sqft, "cr4": cr4_sqft, "cr5": cr5_sqft}
side_m = {k: round(math.sqrt(v * SQFT_M2), 2) for k, v in areas.items()}          # rule: two decimals
tx_total_sqft = gill_sqft + kirby_sqft + cr4_sqft + cr5_sqft
to_build_sqft = cr4_sqft + cr5_sqft

# The Gillingham Lane plant drawn as a kit warehouse with its stated floor area and a 2 to 1 plan (a drawing choice,
# disclosed): length = sqrt(2A), depth = sqrt(A/2), metres, two decimals.
gill_m2 = gill_sqft * SQFT_M2
gill_len_m = round(math.sqrt(2 * gill_m2), 2)
gill_dep_m = round(math.sqrt(gill_m2 / 2), 2)

# The larger Chimney Rock lease's near edge as the side of a square of its stated area, staked once per month of the
# anticipated time to substantial completion. Months elapsed since the leases: whole calendar months completed from
# August 31st to the run date (rule: a month counts when its same-day anniversary, or the month's end, has passed).


def add_months(d, n):
    y, mo = d.year + (d.month - 1 + n) // 12, (d.month - 1 + n) % 12 + 1
    last = [31, 29 if y % 4 == 0 and (y % 100 or y % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mo - 1]
    return datetime.date(y, mo, min(d.day, last))


months_elapsed = max(n for n in range(0, months_to_done + 1) if add_months(lease_date, n) <= run_date)
stake_pitch_m = round(side_m["cr5"] / months_to_done, 2)

F = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were.",
     "cap_now": {"value": cap_now, "from": ["c2"], "basis": "total manufacturing equipment capacity, units per month, approaching; all products and sites; copy only, never on the pad scale"},
     "cap_2026": {"value": cap_2026, "from": ["c3"], "basis": "pieces of 800G and 1.6 Tb products per month the company expects equipment for by the end of 2026, over"},
     "cap_2027": {"value": cap_2027, "from": ["c4"], "basis": "pieces of 800G and 1.6 Tb transceivers per month the company expects capacity for by the end of 2027, over"},
     "pad_unit": {"value": PAD_UNIT, "from": [], "basis": "drawing unit, a choice: one taped machine pad per 50,000 pieces a month; never printed"},
     "pads_2026": {"value": pads_2026, "from": ["c3"], "basis": "computed: cap_2026 over pad_unit"},
     "pads_2027": {"value": pads_2027, "from": ["c4"], "basis": "computed: cap_2027 over pad_unit"},
     "gill_sqft": {"value": gill_sqft, "from": ["c8"], "basis": "square feet leased at 1111 Gillingham Lane, Sugar Land"},
     "kirby_sqft": {"value": kirby_sqft, "from": ["c10"], "basis": "square feet of the Kirby property, Pearland"},
     "cr4_sqft": {"value": cr4_sqft, "from": ["c11"], "basis": "rentable square feet, 17331 Chimney Rock Road, to be constructed"},
     "cr5_sqft": {"value": cr5_sqft, "from": ["c11"], "basis": "rentable square feet, 17433 Chimney Rock Road, to be constructed"},
     "tx_total_sqft": {"value": tx_total_sqft, "from": ["c8", "c10", "c11"], "basis": "computed: the four properties' stated square feet summed"},
     "to_build_sqft": {"value": to_build_sqft, "from": ["c11"], "basis": "computed: the two Chimney Rock buildings summed"},
     "side_m": {"value": side_m, "from": ["c8", "c10", "c11"], "basis": "computed: side in metres of a square of each stated area, two decimals"},
     "gill_len_m": {"value": gill_len_m, "from": ["c8"], "basis": "computed: kit warehouse length for the stated area at a 2 to 1 plan, a drawing choice"},
     "gill_dep_m": {"value": gill_dep_m, "from": ["c8"], "basis": "computed: kit warehouse depth for the stated area at a 2 to 1 plan, a drawing choice"},
     "months_to_done": {"value": months_to_done, "from": ["c12"], "basis": "months after the August 31st leases to anticipated substantial completion, approximately"},
     "months_elapsed": {"value": months_elapsed, "from": ["c11"], "basis": "computed: whole months from August 31st, 2026 to the run date"},
     "stake_pitch_m": {"value": stake_pitch_m, "from": ["c11", "c12"], "basis": "computed: side of the larger lease's square over months_to_done"},
     "lease_term_months": {"value": lease_term_months, "from": ["c14"], "basis": "Gillingham Lane lease term, months"},
     }
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print(json.dumps({k: v["value"] for k, v in F.items() if k != "_note"}))
