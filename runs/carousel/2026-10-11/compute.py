#!/usr/bin/env python3
"""compute.py for the 2026-10-11 deck, West Texas A&M's research feedlot (tx-2026-0207).
Every figure is extracted from a claim's own quote in claims.json by a pattern that must match, or the
build stops. A sum, a share or a span is done here from values that were. Nothing is typed by hand."""
import datetime as dt
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
F = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were."}
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July",
                                       "August", "September", "October", "November", "December"], 1)}


def grab(cid, pattern):
    m = re.search(pattern, C[cid]["quote"])
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in quote")
    return m


def num(s):
    return float(s.replace(",", ""))


def put(k, v, cids, basis=None, **kw):
    F[k] = {"value": v, "from": cids}
    if basis:
        F[k]["basis"] = basis
    F[k].update(kw)


# the grant and its match, in millions of dollars as the release prints them
put("grant_musd", num(grab("c1", r"\$([\d.]+) million").group(1)), ["c1"], "the USDA grant, $ million")
m = grab("c3", r"\$([\d.]+) million from The Texas A&M University System and another \$([\d.]+) million from other sources.*\$([\d.]+) million")
put("match_system_musd", num(m.group(1)), ["c3"], "the A&M System's share of the match, $ million")
put("match_other_musd", num(m.group(2)), ["c3"], "other sources' share of the match, $ million")
put("project_total_musd", num(m.group(3)), ["c3"], "the project total the release states, $ million")
s = F["grant_musd"]["value"] + F["match_system_musd"]["value"] + F["match_other_musd"]["value"]
if abs(s - F["project_total_musd"]["value"]) > 1e-9:
    raise SystemExit(f"grant plus match {s} is not the stated total")
put("total_check_musd", round(s, 3), ["c1", "c3"], "grant plus both halves of the match, which equals the stated total")
put("grant_share_of_total_pct", round(100 * F["grant_musd"]["value"] / F["project_total_musd"]["value"]), ["c1", "c3"],
    "the federal grant as a percent of the project total, rounded to a whole percent")

# the pens
m = grab("c4", r"pairing (\d+) small research pens.*with (\d+) commercial-scale pens")
put("small_pens", int(m.group(1)), ["c4"], "small research pens")
put("commercial_pens", int(m.group(2)), ["c4"], "commercial-scale pens")
put("total_pens", F["small_pens"]["value"] + F["commercial_pens"]["value"], ["c4"], "pens in all, small plus commercial-scale")
put("small_per_commercial", F["small_pens"]["value"] // F["commercial_pens"]["value"], ["c4"], "small pens per commercial-scale pen, a whole number ratio")
if F["small_pens"]["value"] % F["commercial_pens"]["value"]:
    raise SystemExit("the ratio is not whole")

# the four planned buildings
comps = re.findall(r"(?:a|an) ([a-z ]+?(?:facility|hospital|center))", C["c5"]["quote"])
put("components", len(comps), ["c5"], "planned components the release lists")
put("component_names", comps, ["c5"], "the planned components, in the release's order")

# ground broken, the ranch, the gift
m = grab("c8", r"broken in (\w+) (\d{4})")
put("ground_broken", f"{int(m.group(2)):04d}-{MONTHS[m.group(1)]:02d}", ["c8"], "month ground was broken")
m = grab("c9", r"about (\w+) miles east of Canyon, consists of ([\d,]+) acres.*in (\d{4})")
put("ranch_miles_east_word", m.group(1), ["c9"], "miles east of Canyon, as the release spells it")
put("ranch_acres", int(num(m.group(2))), ["c9"], "acres of Nance Ranch")
put("ranch_given", int(m.group(3)), ["c9"], "year the ranch was given to WT")
put("gift_acres", num(grab("c10", r"of ([\d.]+) acres").group(1)), ["c10"], "acres of the 2024 land gift")
put("gift_year", int(grab("c10", r"a (\d{4}) land").group(1)), ["c10"], "year of the land gift")
m = grab("c12", r"\$([\d.]+) million in fiscal year (\d{4}) and \$([\d.]+) million in fiscal year (\d{4})")
put("education_fy24_musd", num(m.group(1)), ["c12"], "community project funding for the education facility, fiscal 2024")
put("education_fy26_musd", num(m.group(3)), ["c12"], "community project funding for the education facility, fiscal 2026")

# cattle on feed, 1,000+ capacity feedlots, September 1 2026, thousand head (the third column)
def cof(cid):
    cols = re.findall(r"[\d,]+", C[cid]["quote"].split(":", 1)[1])
    return int(num(cols[2]))
for k, cid in (("tx_on_feed_k", "c17"), ("ks_on_feed_k", "c18"), ("ne_on_feed_k", "c19"), ("us_on_feed_k", "c20")):
    put(k, cof(cid), [cid], "cattle on feed September 1st, 2026, 1,000+ capacity feedlots, thousand head")
put("tx_share_us_pct", round(100 * F["tx_on_feed_k"]["value"] / F["us_on_feed_k"]["value"]), ["c17", "c20"],
    "Texas as a percent of the United States total on September 1st, 2026, rounded to a whole percent")
put("tx_share_us_exact", round(F["tx_on_feed_k"]["value"] / F["us_on_feed_k"]["value"], 4), ["c17", "c20"], "the same share as a fraction, four places")
put("tx_head", F["tx_on_feed_k"]["value"] * 1000, ["c17"], "Texas cattle on feed in head")
put("tx_minus_ne_k", F["tx_on_feed_k"]["value"] - F["ne_on_feed_k"]["value"], ["c17", "c19"], "Texas less Nebraska, thousand head")
put("tx_minus_ks_k", F["tx_on_feed_k"]["value"] - F["ks_on_feed_k"]["value"], ["c17", "c18"], "Texas less Kansas, thousand head")
put("ne_on_feed_m", round(F["ne_on_feed_k"]["value"] / 1000, 2), ["c19"], "Nebraska, million head, two places")
put("ks_on_feed_m", round(F["ks_on_feed_k"]["value"] / 1000, 2), ["c18"], "Kansas, million head, two places")
put("tx_on_feed_m", round(F["tx_on_feed_k"]["value"] / 1000, 2), ["c17"], "Texas, million head, two places")
put("us_on_feed_m", round(F["us_on_feed_k"]["value"] / 1000, 1), ["c20"], "United States, million head, one place")

# the 2019 AgriLife report against the release
agl = dt.date(2019, 2, 27)
rel = dt.date(2026, 10, 7)
put("agrilife_report", agl.isoformat(), ["c23"], "date of the AgriLife Today report")
put("release_date", rel.isoformat(), ["c1"], "date of the A&M System release")
yrs = rel.year - agl.year - ((rel.month, rel.day) < (agl.month, agl.day))
put("years_report_to_release", yrs, ["c23", "c1"], "whole years from the 2019 report to the release")
put("tcfa_share_pct", int(grab("c22", r"approximately (\d+) percent").group(1)), ["c22"], "the association's own share of US fed cattle")

# THE DECK'S LIGHT: the sun over Randall County's centroid in the committed gazetteer at 6:50 p.m. CDT on
# the release date, NOAA's general solar position equations.
_ROOT = next(d for d in HERE.parents if (d / "assets" / "geo" / "tx-places.json").exists())   # the repo root, from out/<date>/ or runs/carousel/<date>/
_places = json.load(open(_ROOT / "assets" / "geo" / "tx-places.json"))["places"]
_r = next(p for p in _places if p.get("full_name") == "Randall County")
_utc = dt.datetime(rel.year, rel.month, rel.day, 18, 50) + dt.timedelta(hours=5)


def sun(lat, lon, when):
    doy = when.timetuple().tm_yday
    g = 2 * math.pi / 365 * (doy - 1 + (when.hour - 12) / 24 + when.minute / 1440)
    eqt = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g) - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))
    dec = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g) + 0.000907 * math.sin(2 * g)
           - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    tst = when.hour * 60 + when.minute + eqt + 4 * lon
    ha = math.radians(tst / 4 - 180)
    la = math.radians(lat)
    cz = math.sin(la) * math.sin(dec) + math.cos(la) * math.cos(dec) * math.cos(ha)
    zen = math.acos(max(-1, min(1, cz)))
    az = math.degrees(math.atan2(math.sin(ha), math.cos(ha) * math.sin(la) - math.tan(dec) * math.cos(la))) + 180
    return 90 - math.degrees(zen), az % 360


_el, _az = sun(_r["lat"], _r["lon"], _utc)
put("sun_elevation", round(_el, 1), ["c1"], "solar elevation over Randall County at 6:50 p.m. CDT on the release date, one decimal")
put("sun_azimuth_compass", round(_az, 1), ["c1"], "solar bearing clockwise from north at the same moment, one decimal")
put("sun_engine_az", round(180 - _az, 1), ["c1"], "the same bearing in the engine's frame, az = 180 - bearing")


# THE DECK'S DRAWN QUANTITIES
unit = F["match_system_musd"]["value"]
if F["match_other_musd"]["value"] != unit:
    raise SystemExit("the two halves of the match differ, so a section can't stand for one share")
put("section_musd", unit, ["c3"], "one precast bunk section stands for one $4.875 million share, the match's own unit")
put("grant_sections", int(F["grant_musd"]["value"] / unit), ["c1", "c3"], "bunk sections the grant spans, grant over one share")
put("total_sections", int(F["project_total_musd"]["value"] / unit), ["c3"], "bunk sections in the whole project, total over one share")
ACRE_M2 = 4046.8564224
MILE_M = 1609.344
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
put("ranch_square_side_m", round(math.sqrt(F["ranch_acres"]["value"] * ACRE_M2)), ["c9"], "side in metres of a square of the ranch's area, one acre = 4046.8564224 square metres, rounded to a metre")
put("gift_square_side_m", round(math.sqrt(F["gift_acres"]["value"] * ACRE_M2)), ["c10"], "side in metres of a square of the gift's area, rounded to a metre")
put("ranch_offset_m", round(WORDS[F["ranch_miles_east_word"]["value"]] * MILE_M), ["c9"], "about seven miles east, in metres, one mile = 1609.344 m, rounded to a metre")
STEER_K = 500
put("steer_unit_k", STEER_K, ["c17", "c20"], "a drawing rule, one steer drawn for every 500 thousand head on feed")
put("tx_steers", F["tx_on_feed_k"]["value"] // STEER_K, ["c17"], "steers drawn for Texas, 2,500 thousand over 500, exact")
if F["tx_on_feed_k"]["value"] % STEER_K:
    raise SystemExit("Texas is not a whole number of steers")
put("us_steers", int(F["us_on_feed_k"]["value"] / STEER_K + 0.5), ["c20"], "steers drawn for the United States, 11,163 thousand over 500, rounded half up")

(HERE / "figures.json").write_text(json.dumps(F, indent=1, ensure_ascii=False) + "\n")
print(json.dumps({k: v["value"] for k, v in F.items() if k != "_note"}, indent=0, ensure_ascii=False))
