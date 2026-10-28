"""Every figure the October 28th deck states or draws, extracted from a claim quote or computed here.

No figure in the deck is typed. Each value below is parsed out of the verified quote it cites in
claims.json, and figures.json is written from this file alone.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
claims = {c["id"]: c for c in json.loads((HERE / "claims.json").read_text())["claims"]}


def quote(cid):
    return claims[cid]["quote"]


def grab(cid, pattern, group=1):
    m = re.search(pattern, quote(cid))
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in its quote")
    return m.group(group)


def num(s):
    return float(s.replace(",", "")) if "." in s else int(s.replace(",", ""))


figures = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were."}
F = lambda k, v, src, basis: figures.__setitem__(k, {"value": v, "from": src, "basis": basis})

YD3 = 0.764554857984   # cubic metres in a cubic yard, by definition

# THE RESULTS TABLE of the October 19th briefing (c22 to c27), each row in the table's own order
rows = [("observations", "c22", r"Observations Reviewed ([\d,]+)$", "observations reviewed"),
        ("notices", "c23", r"Courtesy Notices ([\d,]+)$", "courtesy notices"),
        ("inspections", "c24", r"Field Inspections ([\d,]+)$", "field inspections"),
        ("corrections", "c25", r"Voluntary Corrections ([\d,]+)$", "voluntary corrections"),
        ("abatements", "c26", r"Direct Abatements ([\d,]+)$", "direct abatements"),
        ("enforcement", "c27", r"Formal Enforcement ([\d,]+)$", "formal enforcement")]
for key, cid, pat, label in rows:
    F(key, num(grab(cid, pat)), [cid], f"{label}, the results table of the October 19th briefing")

# ONE SCALE for every drawn count: the largest row is FULL px long and every other row is drawn at the same px per item
FULL = 900
per = FULL / figures["observations"]["value"]
for key, cid, _, label in rows:
    F(f"{key}_px", round(figures[key]["value"] * per, 1), [cid, "c22"],
      f"computed: {label} times {FULL} over observations reviewed, the px length at one scale, to one decimal")

# ONE SCALE IN METRES for the rack frames: the largest row is a limb RACK_M long and every other row is cut at the same
# metres per item, so a row of 34 is a slice of limb and a row of 5,318 is the whole limb
RACK_M = 8.4
per_m = RACK_M / figures["observations"]["value"]
for key, cid, _, label in rows:
    F(f"{key}_m", round(figures[key]["value"] * per_m, 3), [cid, "c22"],
      f"computed: {label} times {RACK_M} m over observations reviewed, the limb length in metres at one scale, to the millimetre")

# THE FLEET (c5, c44, c34)
F("trucks", num(grab("c5", r"mounted on (\d+) Sanitation")), ["c5"], "Sanitation brush collection vehicles carrying cameras, October 19th briefing")
per_truck = {"two": 2}[grab("c44", r"\((\w+) per vehicle\)")]
F("cameras_per_truck", per_truck, ["c44"], "cameras per vehicle, the April 10th memo")
F("cameras_planned", num(grab("c34", r"Implement (\d+) AI-enabled")), ["c34"], "cameras the December 9th briefing proposed")
F("cameras_fleet", figures["trucks"]["value"] * per_truck, ["c5", "c44"], "computed: vehicles times cameras per vehicle")
if figures["cameras_fleet"]["value"] != figures["cameras_planned"]["value"]:
    raise SystemExit("50 trucks at two cameras each no longer equals the December plan's count")

# THE MONEY AND THE EXIT (c35, c36, c37)
F("cost_year", num(grab("c36", r"\$([\d,]+) per year")), ["c36"], "contract cost per year, December 9th briefing")
F("cost_three_year", num(grab("c35", r"\$([\d,]+),")), ["c35"], "three-year estimated amount, December 9th briefing")
F("notice_days", num(grab("c37", r"with (\d+) days")), ["c37"], "days of written notice to end the contract, December 9th briefing")

# THE BRUSH (c31): the monthly pickup a curb pile may reach
yd = num(grab("c31", r"up to (\d+) cubic yards"))
F("pile_yd3", yd, ["c31"], "cubic yards a monthly brush pickup may reach, October 19th briefing")
F("pile_m3", round(yd * YD3, 2), ["c31"], "computed: cubic yards times 0.764555, to two decimals")
# a curbside windrow 1.2 m high and 2.0 m deep, half ellipse in section: length solved so its volume is pile_m3
H, Dp = 1.2, 2.0
sect = 3.141592653589793 * (H) * (Dp / 2) / 2
F("pile_len_m", round(yd * YD3 / sect, 2), ["c31"], "computed: the windrow length whose half ellipse section 1.2 m high by 2.0 m deep holds pile_m3, to two decimals")

# THE SPLIT on the awareness slide (c21), never given a denominator
F("proactive_pct", num(grab("c21", r"(\d+)% Proactive")), ["c21"], "percent proactive as the slide prints it, with no stated base")
F("reactive_pct", num(grab("c21", r"(\d+)% Reactive")), ["c21"], "percent reactive as the slide prints it, with no stated base")

(HERE / "figures.json").write_text(json.dumps(figures, indent=1) + "\n")
print(json.dumps({k: v["value"] for k, v in figures.items() if k != "_note"}))
