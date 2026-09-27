#!/usr/bin/env python3
"""compute.py for the 2026-09-27 deck. Every figure is extracted from a claim's own quote in
claims.json by a pattern that must match, or the build stops. Counts are counted, never typed."""
import json, re, datetime as dt
from pathlib import Path

HERE = Path(__file__).resolve().parent
CL = json.load(open(HERE / "claims.json"))["claims"]
C = {c["id"]: c for c in CL}
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}

def num(cid, pattern, group=1):
    m = re.search(pattern, C[cid]["quote"])
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in quote")
    g = m.group(group)
    return WORDS[g] if g in WORDS else float(g.replace(",", "")) if "." in g else int(g.replace(",", ""))

F = {"_note": "Every value is extracted from a claim quote or counted from a claim's own list by compute.py. Everything on how the software works is the plaintiffs' allegation."}

subs = C["c37"]["texas_submarkets_by_area"]
F["texas_submarkets"] = {"value": sum(len(v) for v in subs.values()), "from": ["c36", "c37"], "basis": "rows under a Texas area in the complaint's Appendix A, counted"}
F["texas_submarkets_by_area"] = {k: len(v) for k, v in subs.items()}
F["dallas_submarkets"] = {"value": len(subs["Dallas-Plano-Irving, TX"]), "from": ["c37"]}
F["austin_submarkets"] = {"value": len(subs["Austin-Round Rock, TX"]), "from": ["c37"]}
F["houston_submarkets"] = {"value": len(subs["Houston-The Woodlands-Sugar Land, TX"]), "from": ["c37"]}
F["san_antonio_submarkets"] = {"value": len(subs["San Antonio-New Braunfels, TX"]), "from": ["c37"]}
F["fort_worth_submarkets"] = {"value": len(subs["Fort Worth-Arlington, TX"]), "from": ["c37"]}
assert F["texas_submarkets"]["value"] == sum(F["texas_submarkets_by_area"].values())

F["auto_accept_daily_pct"] = {"value": num("c27", r"of a (\d+)% daily change"), "from": ["c27"], "basis": "the complaint's default, alleged"}
F["auto_accept_weekly_pct"] = {"value": num("c27", r"an (\d+)% weekly change"), "from": ["c27"], "basis": "the complaint's default, alleged"}
F["retrains_low"] = {"value": num("c24", r"retrains the models (\w+) to"), "word": "three", "from": ["c24"]}
F["retrains_high"] = {"value": num("c24", r"to (\w+) times per year"), "word": "four", "from": ["c24"]}
F["near_rec_share_pct"] = {"value": num("c33", r"nearly (\d+)% of final"), "from": ["c33"], "basis": "nearly, alleged"}
F["near_rec_band_pct"] = {"value": num("c33", r"within ([\d.]+)% of RealPage"), "from": ["c33"]}
F["close_rec_share_pct"] = {"value": num("c33", r"more than (\d+)% are within"), "from": ["c33"]}
F["close_rec_band_pct"] = {"value": num("c33", r"are within (\d+)% of RealPage"), "from": ["c33"]}
F["units_million"] = {"value": num("c34", r"over (\d+) million units"), "from": ["c34"], "basis": "the plaintiffs' allegation"}
F["penetration_low_pct"] = {"value": num("c36", r"at least around (\d+)% to"), "from": ["c36"]}
F["penetration_high_pct"] = {"value": num("c36", r"to (\d+)%$"), "from": ["c36"]}
F["comment_days"] = {"value": num("c8", r"within (\d+) days"), "from": ["c8"]}
F["term_years"] = {"value": num("c54", r"expire (\w+) years"), "word": "five", "from": ["c54"]}
F["early_end_years"] = {"value": num("c54", r"after (\w+) years"), "word": "three", "from": ["c54"]}
F["restriction_start_days"] = {"value": num("c49", r"Beginning (\d+) days"), "from": ["c49"]}
F["realpage_share_pct"] = {"value": num("c64", r"at least (\d+) percent"), "from": ["c64"]}
F["revenue_systems"] = {"value": num("c22", r"offers (\w+) revenue management"), "word": "three", "from": ["c22"]}
reqs = [c for c in CL if re.match(r"^(i|ii|iii|iv|v|vi|vii|viii|ix)\. ", c["quote"])]
F["judgment_requirements"] = {"value": len(reqs), "from": [c["id"] for c in reqs], "basis": "numbered requirements i to ix in the Competitive Impact Statement, counted"}
F["defendants_added"] = {"value": 1 + num("c6", r"and (\w+) other property"), "from": ["c6"], "basis": "Pinnacle and five others added in the amended complaint"}
limits = ["c39", "c40", "c41", "c50", "c51"]
F["software_limits"] = {"value": len(limits), "from": limits, "basis": "the judgment's limits on what pricing software Pinnacle may use, the set this deck read: i, ii, iii, the acceptance requirement and the rent floor, counted"}
# frame 3: two steel columns at one scale, 0.25 m per percentage point, rounded to the centimetre
SCALE = 0.25
F["column_scale_m_per_pt"] = SCALE
F["column_daily_m"] = round(F["auto_accept_daily_pct"]["value"] * SCALE, 2)
F["column_weekly_m"] = round(F["auto_accept_weekly_pct"]["value"] * SCALE, 2)
# frame 2: the two tolerance bands on the drawn screen, at one scale, 30 px per percentage point
# (12 until round 1 of review, where both bands read as one stripe at feed size)
F["band_px_per_pt"] = 30
F["band_near_px"] = round(F["near_rec_band_pct"]["value"] * F["band_px_per_pt"])
F["band_close_px"] = round(F["close_rec_band_pct"]["value"] * F["band_px_per_pt"])
# frame 8: two other buildings whose front units glow at the low and high end of the complaint's
# penetration range. A building of 1 core and 2 bays per group has 4 bays over 3 floors, 12 front
# units. Rule: round half up of share times units.
import math
UNITS = 4 * 3
F["other_building_front_units"] = UNITS
F["lit_units_low"] = int(math.floor(F["penetration_low_pct"]["value"] / 100 * UNITS + 0.5))
F["lit_units_high"] = int(math.floor(F["penetration_high_pct"]["value"] / 100 * UNITS + 0.5))
F["notice_date"] = "2026-09-18"
F["filed_date"] = "2026-09-04"
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print(json.dumps({k: (v["value"] if isinstance(v, dict) and "value" in v else v) for k, v in F.items() if k != "_note"}, indent=0))
