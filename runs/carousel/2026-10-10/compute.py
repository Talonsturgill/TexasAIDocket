#!/usr/bin/env python3
"""compute.py for the 2026-10-10 deck, Austin Community College's AI policy (tx-2026-0212).
Every figure is extracted from a claim's own quote in claims.json by a pattern that must match, or the
build stops. A count is a count of things the quotes list, done here. A span is date or clock
arithmetic on what the quotes print. Nothing is typed by hand."""
import datetime as dt
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July",
                                       "August", "September", "October", "November", "December"], 1)}
ABBR = {m[:3]: i for m, i in MONTHS.items()}


def grab(cid, pattern):
    m = re.search(pattern, C[cid]["quote"])
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in quote")
    return m


F = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were."}


def put(k, v, cids, basis=None, **kw):
    F[k] = {"value": v, "from": cids}
    if basis:
        F[k]["basis"] = basis
    F[k].update(kw)


def clock(h, m, ampm):
    h = int(h) % 12 + (12 if ampm.startswith("p") else 0)
    return h * 60 + int(m or 0)


def event(cid):
    """an event line, 'Monday, October 12 | 6:30-9 p.m. | Rio Grande Campus', as (month, day, start, end, campus)"""
    m = grab(cid, r"\w+day, (\w+) (\d+) \| (\d+)(?::(\d+))?( ?[ap]\.m\.)?-(\d+)(?::(\d+))? ?([ap])\.m\. \| ([\w ]+) Campus")
    end_ampm = m.group(8)
    start_ampm = (m.group(5) or end_ampm).strip()
    return (MONTHS[m.group(1)], int(m.group(2)), clock(m.group(3), m.group(4), start_ampm),
            clock(m.group(6), m.group(7), end_ampm), m.group(9))


# the post, and the year every event line leaves out
pm = grab("c31", r"(\w{3}) (\d+), (\d{4})")
posted = dt.date(int(pm.group(3)), ABBR[pm.group(1)], int(pm.group(2)))
put("posted", posted.isoformat(), ["c31"], "date the college posted the announcement")

# the five rules of the framework, one claim each
RULES = ["c5", "c6", "c7", "c8", "c9"]
names = [grab(c, r"^([^:]+):").group(1) for c in RULES]
put("rules", len(names), RULES, "rules in the TRUST framework, one quoted line each")
put("rule_names", names, RULES, "the rules' own names, in the post's order")
framework = grab("c1", r"newly launched (\w+) framework").group(1)
put("framework_letters", len(framework), ["c1"], "letters in the framework's name, read from c1, one per rule")
assert F["rules"]["value"] == F["framework_letters"]["value"], "a rule per letter"

# the three October events
EV = {"town_hall": "c10", "convocation": "c13", "seminar": "c14"}
for k, cid in EV.items():
    mo, day, start, end, campus = event(cid)
    d = dt.date(posted.year, mo, day)
    put(k, d.isoformat(), [cid, "c31"], f"date of the {k.replace('_', ' ')}, the year from the post")
    put(k + "_hours", (end - start) / 60, [cid], f"length of the {k.replace('_', ' ')} on the clock")
    put(k + "_campus", campus, [cid], f"campus of the {k.replace('_', ' ')}")
    put("days_post_to_" + k, (d - posted).days, [cid, "c31"], f"days from the post to the {k.replace('_', ' ')}")
put("events", len(EV), list(EV.values()), "October events the post lists")
put("public_hours", sum(F[k + "_hours"]["value"] for k in EV), list(EV.values()),
    "hours across the three events, on the clock")

# the college
put("students", int(grab("c20", r"More than ([\d,]+) students").group(1).replace(",", "")), ["c20"],
    "students the college says rely on it each year, more than", floor=True)
DOCS = [c for c in ["c19"] if "Acceptable Use of Artificial Intelligence Policy" in C[c]["quote"]]
put("existing_documents", len(DOCS), DOCS, "documents titled as an acceptable use policy that the AI hub already links")

# context
ORD = {"sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9}
put("el_paso_grade", ORD[grab("c27", r"through (\w+) grade").group(1)], ["c27"], "grade through which the El Paso ISD draft bars AI for schoolwork")
rv = grab("c30", r"on (\w+) (\d+)\.")
put("richardson_vote", dt.date(posted.year, MONTHS[rv.group(1)], int(rv.group(2))).isoformat(), ["c30", "c31"],
    "date the Richardson board is expected to vote, the year from this run's post")

(HERE / "figures.json").write_text(json.dumps(F, indent=1) + "\n")
print(json.dumps({k: v["value"] for k, v in F.items() if k != "_note"}, indent=0))

# THE DECK'S LIGHT, computed rather than chosen: the sun over Travis County (the committed gazetteer's
# area weighted centroid) at the town hall's start, 6:30 p.m. Central Daylight Time, which is UTC-5.
# NOAA's general solar position equations (fractional year, equation of time, declination).
import math
_places = json.load(open(HERE.parents[1] / "assets" / "geo" / "tx-places.json"))["places"]
_travis = next(p for p in _places if p.get("id") == "county-travis")
_th = dt.date.fromisoformat(F["town_hall"]["value"])
_start_min = event("c10")[2]
_utc = dt.datetime(_th.year, _th.month, _th.day) + dt.timedelta(minutes=_start_min + 5 * 60)


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


_el, _az = sun(_travis["lat"], _travis["lon"], _utc)
put("sun_elevation", round(_el, 1), ["c10", "c31"], "solar elevation in degrees over Travis County at the town hall's start, NOAA equations, one decimal")
put("sun_azimuth_compass", round(_az, 1), ["c10", "c31"], "solar azimuth in degrees clockwise from north at the same moment, one decimal")
(HERE / "figures.json").write_text(json.dumps(F, indent=1) + "\n")
print("sun", F["sun_elevation"]["value"], F["sun_azimuth_compass"]["value"])

# THE DECK'S DRAWN QUANTITIES
put("desks_drawn", F["students"]["value"] // 1000, ["c20"], "desks drawn on the count frame, one per 1,000 of the students the college says rely on it each year, floored")
put("desk_scale", 1000, ["c20"], "students each drawn desk stands for, the drawing's own rule")
_last = dt.date.fromisoformat(F["seminar"]["value"])
put("walk_pavers", (_last - posted).days + 1, ["c31", "c14"], "pavers in the walk, one per calendar day from the post to the seminar, both ends counted")
for k in ("town_hall", "convocation", "seminar"):
    put("paver_" + k, (dt.date.fromisoformat(F[k]["value"]) - posted).days, [EV[k], "c31"], f"index of the {k.replace('_', ' ')}'s paver, the post's day being 0")
_sm = event("c10")[2]
put("clock_minute_deg", (_sm % 60) * 6, ["c10"], "minute hand angle clockwise from twelve at the town hall's start")
put("clock_hour_deg", ((_sm // 60) % 12) * 30 + (_sm % 60) * 0.5, ["c10"], "hour hand angle clockwise from twelve at the town hall's start")
# the engine's azimuth runs clockwise from +z (south) toward +x (east); compass bearing B maps to 180 - B
put("key_az_engine", round(180 - F["sun_azimuth_compass"]["value"], 1), ["c10", "c31"], "the sun's bearing in the engine's frame, 180 minus the compass bearing")
(HERE / "figures.json").write_text(json.dumps(F, indent=1) + "\n")
print({k: F[k]["value"] for k in ("desks_drawn", "walk_pavers", "paver_town_hall", "paver_convocation", "paver_seminar", "clock_minute_deg", "clock_hour_deg", "key_az_engine")})
