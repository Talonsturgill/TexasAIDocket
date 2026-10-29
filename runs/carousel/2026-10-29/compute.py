"""Every figure the October 29th deck states or draws, extracted from a claim quote or computed here.

No figure in the deck is typed. Each value below is parsed out of the verified quote it cites in
claims.json, and figures.json is written from this file alone.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
claims = {c["id"]: c for c in json.loads((HERE / "claims.json").read_text())["claims"]}


def grab(cid, pattern, group=1):
    m = re.search(pattern, claims[cid]["quote"])
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in its quote")
    return int(m.group(group).replace(",", ""))


figures = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were."}
F = lambda k, v, src, basis: figures.__setitem__(k, {"value": v, "from": src, "basis": basis})

wind = grab("c6", r"a (\d+) MW wind farm")
if grab("c12", r"the (\d+) MW Briscoe Wind Farm") != wind:
    raise SystemExit("the two releases no longer agree on the wind farm's size")
F("wind_mw", wind, ["c6", "c12"], "the Briscoe Wind Farm's size in MW, per Soluna")
dorothy = grab("c12", r"Project Dorothy is a (\d+) MW")
F("dorothy_mw", dorothy, ["c12"], "the older Dorothy campus in MW, built behind the meter, per Soluna")
energized = grab("c13", r"account for (\d+) MW")
F("energized_mw", energized, ["c13"], "Dorothy 1 and 2 energized capacity in MW, per Soluna on September 14th")
d3 = grab("c14", r"the (\d+) MW next phase")
if grab("c19", r"up to (\d+) MW") != d3:
    raise SystemExit("the two releases no longer agree on Dorothy 3's size")
F("d3_mw", d3, ["c14", "c19"], "Dorothy 3, the next phase, in MW, up to this, per Soluna")
phase1 = grab("c7", r"\((\d+) MW Critical IT\)")
if grab("c2", r"planned (\d+) MW critical IT") != phase1:
    raise SystemExit("the release no longer agrees with itself on Phase 1")
F("phase1_mw", phase1, ["c2", "c7"], "Phase 1 of Dorothy 3 in MW of critical IT, per Soluna")
F("applied_pct", grab("c3", r"hold a (\d+)% interest"), ["c3"], "Applied's expected share of the project company, per Soluna")
F("soluna_pct", grab("c3", r"remaining (\d+)% interest"), ["c3"], "Soluna's expected share of the project company, per Soluna")
if figures["applied_pct"]["value"] + figures["soluna_pct"]["value"] != 100:
    raise SystemExit("the two shares no longer sum to the whole")
acres = grab("c18", r"purchase of (\d+) acres")
F("acres", acres, ["c18"], "acres Soluna bought for Dorothy 3")
first = grab("c21", r"exceed the (\d+) acres")
F("acres_first", first, ["c21"], "acres Soluna first identified for the campus")
F("acres_extra", acres - first, ["c18", "c21"], "computed: acres bought minus acres first identified")
F("extra_request_mw", grab("c17", r"additional (\d+) MW request"), ["c17"], "a further load request at the Dorothy campus in MW, under study, per Soluna")
# THE TURN, computed
F("d3_over_wind", round(d3 / wind, 2), ["c14", "c6"], "computed: Dorothy 3's planned MW over the wind farm's MW, to two decimals")
F("d3_minus_wind", d3 - wind, ["c14", "c6"], "computed: MW by which Dorothy 3's plan exceeds the wind farm's size")
F("energized_pct_of_wind", round(100 * energized / wind), ["c13", "c6"], "computed: energized MW over the wind farm's MW, as a whole percent")
F("phase1_pct_of_d3", round(100 * phase1 / d3), ["c7", "c14"], "computed: Phase 1's MW over Dorothy 3's planned MW, as a whole percent")
F("campus_planned_mw", dorothy + d3, ["c12", "c14"], "computed: the older campus's MW plus Dorothy 3's planned MW")
F("campus_over_wind", round((dorothy + d3) / wind, 2), ["c12", "c14", "c6"], "computed: the two campuses' MW over the wind farm's MW, to two decimals")

# THE DRAWING SCALE. One flanged tower section stands for SECTION_MW megawatts on the deck's columns.
# It is a drawing unit chosen here, never a claim, and the deck names it wherever a column is drawn.
SECTION_MW = 10
F("section_mw", SECTION_MW, [], "the drawing unit: megawatts one tower section stands for on the deck's columns. A choice, not a claim")
F("sections_wind", round(wind / SECTION_MW, 2), ["c6"], "computed: the wind farm's MW in sections")
F("sections_d3", round(d3 / SECTION_MW, 2), ["c14"], "computed: Dorothy 3's planned MW in sections")
F("sections_phase1", round(phase1 / SECTION_MW, 2), ["c7"], "computed: Phase 1's MW in sections")
F("bays_dorothy", round(dorothy / SECTION_MW, 2), ["c12"], "computed: the older campus's MW in bays at the same unit")
F("bays_energized", round(energized / SECTION_MW, 2), ["c13"], "computed: energized MW in bays at the same unit")
ACRE_M2 = 4046.8564224   # square metres in an international acre, by definition
F("side_m_acres", round((acres * ACRE_M2) ** 0.5, 1), ["c18"], "computed: the side in metres of a square of the acres bought")
F("side_m_first", round((first * ACRE_M2) ** 0.5, 1), ["c21"], "computed: the side in metres of a square of the acres first identified")

(HERE / "figures.json").write_text(json.dumps(figures, indent=1) + "\n")
print(json.dumps({k: v["value"] for k, v in figures.items() if k != "_note"}))
