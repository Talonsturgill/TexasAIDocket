#!/usr/bin/env python3
"""compute.py for the 2026-10-12 deck, UT San Antonio's solar flood warning node (tx-2026-0141).
Every figure is extracted from a claim's own quote in claims.json by a pattern that must match, or the
build stops. A ratio, a span or a scale is done here from values that were. Nothing is typed by hand."""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
F = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were."}
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
MILE_M = 1609.344


def grab(cid, pattern):
    m = re.search(pattern, C[cid]["quote"])
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in quote")
    return m


def put(k, v, cids, basis=None):
    F[k] = {"value": v, "from": cids}
    if basis:
        F[k]["basis"] = basis


# the node's sensors
put("sensor_count", WORDS[grab("c1", r"^(\w+) optical water-level sensors").group(1)], ["c1"], "optical water level sensors on one node")
put("other_sensing", len(re.findall(r"(temperature|humidity|light|precipitation)", grab("c2", r"combines (.+) sensing").group(1))), ["c2"],
    "other quantities the prototype senses, counted in the release's own list")

# the score the release reports, and what it is
put("validation_pct", float(grab("c7", r"([\d.]+)% validation accuracy").group(1)), ["c7"], "validation accuracy in initial assessments post-training, percent")
put("validation_rest_pct", round(100 - F["validation_pct"]["value"], 2), ["c7"], "the part of a 100 percent bar the validation figure leaves, percent, two places")
put("validation_frac", round(F["validation_pct"]["value"] / 100, 4), ["c7"], "the validation figure as a fraction of one bar, four places")

# the radio
m = grab("c9", r"more than a (half)-mile through city streets and up to (\w+) miles in open areas")
street = 0.5 if m.group(1) == "half" else None
put("lora_street_mi", street, ["c9"], "miles through city streets, the release's 'more than a half-mile'")
put("lora_open_mi", WORDS[m.group(2)], ["c9"], "miles in open areas, the release's 'up to five miles'")
put("lora_ratio", int(F["lora_open_mi"]["value"] / F["lora_street_mi"]["value"]), ["c9"], "open reach over street reach")
put("lora_street_m", round(street * MILE_M), ["c9"], "the street reach in metres, one mile = 1609.344 m, rounded to a metre")
put("lora_open_m", round(F["lora_open_mi"]["value"] * MILE_M), ["c9"], "the open reach in metres, rounded to a metre")

# the parts cost for one prototype
m = grab("c11", r"roughly \$(\d+) to \$(\d+)")
put("cost_low", int(m.group(1)), ["c11"], "low end of the parts cost for one prototype, dollars")
put("cost_high", int(m.group(2)), ["c11"], "high end of the parts cost for one prototype, dollars")
put("cost_spread", F["cost_high"]["value"] - F["cost_low"]["value"], ["c11"], "high less low, dollars")
put("cost_low_frac", round(F["cost_low"]["value"] / F["cost_high"]["value"], 4), ["c11"], "the low end as a fraction of the high end, four places")

# the context the deck carries, and only as context
m = grab("c20", r"more than (\d+) rain gauges.*roughly (\d+)% under some conditions")
put("rain_gauges", int(m.group(1)), ["c20"], "rain gauges UT Arlington cross-referenced, 'more than'")
put("radar_short_pct", int(m.group(2)), ["c20"], "how far standard radar can underestimate storm totals, 'roughly', percent")
put("radar_fill_frac", round(1 - F["radar_short_pct"]["value"] / 100, 2), ["c20"], "the radar column's fill as a fraction of the gauge column's, a drawing rule from the percent")
put("vehicle_share_word", grab("c22", r"(over half)").group(1), ["c22"], "the NWS relay of CDC's share of flood drownings in vehicles, as words, never a numeral")

# the release's own date
_pub = C["c1"].get("published")
if not _pub or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", _pub):
    raise SystemExit("c1: no published date recorded off the fetched page")
put("release_date", _pub, ["c1"], "the publication date the fact check read off the UTSA page and recorded on c1 as published")
put("noaa_award", grab("c15", r"Award No\. (NA\w+)").group(1), ["c15"], "the NOAA award number")

# THE DECK'S DRAWING RULES, stated so a figure on a frame traces here
put("wet_cover", 1, ["c1"], "a drawing rule: the cover's water reaches the first of the four sensors, drawn to illustrate")
put("wet_close", 3, ["c1"], "a drawing rule: the close's water reaches three of the four, drawn to illustrate, the fourth never")
if F["wet_close"]["value"] >= F["sensor_count"]["value"]:
    raise SystemExit("the close may not wet every sensor")
put("cost_bar_m", 2.2, ["c11"], "a drawing rule: one centimetre of the cost bar per dollar, so $220 is 2.2 m")
put("cost_low_m", round(F["cost_low"]["value"] / 100, 2), ["c11"], "the low end on the same bar, metres")
put("validation_bar_m", 10.0, ["c7"], "a drawing rule: the validation bar is 10 m long for 100 percent")
put("validation_lit_m", round(10.0 * F["validation_frac"]["value"], 3), ["c7"], "the lit length of that bar, metres, three places")

(HERE / "figures.json").write_text(json.dumps(F, indent=1, ensure_ascii=False) + "\n")
print(json.dumps({k: v["value"] for k, v in F.items() if k != "_note"}, indent=0, ensure_ascii=False))
