#!/usr/bin/env python3
"""Every figure this deck draws, EXTRACTED from claims.json rather than typed.

Each value is pulled out of a claim's `quote` by a pattern anchored on the words around it, so
the value on a frame and the value in the FAA's draft are the same string by construction. If a
quote changes, this raises rather than publishing yesterday's number.

WHAT IT CHECKS BEFORE IT PUBLISHES ANYTHING.
1. The draft's Table 2.2-1 prints five metro rows and a total row (c7). The totals are asserted
   to equal the sums of the rows, column by column. If the document's own arithmetic did not
   hold, the deck would have to say so rather than pick one.
2. Every delivery is three transits (c8), so the transits column is asserted to be three times
   the deliveries column in every row.
3. Each Charger may launch at most 1,000 deliveries a day (c24). The per metro delivery cap is
   asserted to equal chargers times that, so the frame that draws chargers and the frame that
   draws deliveries are drawing the same cap.

WHAT IT REFUSES TO COMPUTE, and the refusals are part of the argument.
- NO RATE OF OPERATOR REVIEW. c18 says an image goes to an operator when the pod can't identify
  the target. The draft gives no share, no rate and no count of such cases, and never says
  "only". Nothing here estimates one.
- NO DELIVERIES FLOWN. Every per day number in this file is a MAXIMUM the draft assesses. None is
  a forecast or a count of flights.
- NO NOISE IN A READER'S YARD. c21's figures are DNL, a yearly day night average. The hover
  sound level in the noise report is a single event SEL and was rejected by the fact check for
  being quoted against the wrong label. Nothing converts one metric to the other.
- NO COUNTY COUNT. The Section 106 letter's county list (c25) and its own stated total disagree
  in the fact check's reading, so neither number is published.

UNITS. The draft gives lengths in feet. Geometry is built in metres, so feet are converted at
0.3048 m per foot, exactly, and rounded to three decimals for geometry. A metre figure is never
printed on a frame. Every figure a reader sees is in the draft's own unit.
"""
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
doc = json.loads((HERE / "claims.json").read_text(encoding="utf-8"))
C = {c["id"]: c for c in doc["claims"]}
FT = 0.3048


def grab(cid, pattern, label):
    m = re.search(pattern, C[cid]["quote"])
    if not m:
        raise SystemExit("compute: %s not found in %s's quote" % (label, cid))
    return m.groups() if len(m.groups()) > 1 else m.group(1)


def n(s):
    return float(s.replace(",", "")) if "." in s else int(s.replace(",", ""))


def m3(feet):
    return round(feet * FT, 3)


# ------------------------------------------------------------------ Table 2.2-1, c7
ROW = r"%s ([\d,]+) ([\d,]+) ([\d,]+) ([\d,]+) ([\d,]+)"
METROS = ["Houston", "San Antonio", "Austin", "Amarillo", "El Paso"]
COLS = ["area_sq_mi", "chargers", "dropboxes", "deliveries_max", "transits_max"]
table = {}
for name in METROS + ["Total"]:
    vals = grab("c7", ROW % re.escape(name), name)
    table[name] = dict(zip(COLS, [n(v) for v in vals]))
for col in COLS:
    s = sum(table[k][col] for k in METROS)
    if s != table["Total"][col]:
        raise SystemExit("compute: Table 2.2-1 %s rows sum to %s, total row says %s" % (col, s, table["Total"][col]))

legs = {"three": 3}[grab("c8", r"Each delivery includes (\w+) transits", "transits per delivery")]
per_charger = n(grab("c24", r"maximum of ([\d,]+) deliveries per day from each Charger", "per charger"))
for k in METROS + ["Total"]:
    r = table[k]
    if r["transits_max"] != legs * r["deliveries_max"]:
        raise SystemExit("compute: %s transits are not %d times deliveries" % (k, legs))
    if r["deliveries_max"] != per_charger * r["chargers"]:
        raise SystemExit("compute: %s deliveries are not chargers times %d" % (k, per_charger))

# ------------------------------------------------------------------ the aircraft, c11 c13 c14
cruise_ft = n(grab("c11", r"altitude of (\d+) feet above ground level", "cruise"))
span_ft, height_ft, length_ft = (n(v) for v in grab(
    "c14", r"wingspan of approximately ([\d.]+) feet, a height of approximately ([\d.]+) feet, and a length of approximately ([\d.]+) feet", "dimensions"))
props = n(grab("c13", r"design with (\d+) propellers", "propellers"))
weight_lb, payload_lb = (n(v) for v in grab("c13", r"approximately (\d+) pounds when combined with its maximum payload weight of (\d+) pounds", "weight"))
hover_s = n(grab("c19", r"\(approximately (\d+) seconds\)", "delivery hover"))
hover_ft = n(grab("c19", r"Maintain hover at (\d+) feet AGL", "hover height"))
if hover_ft != cruise_ft:
    raise SystemExit("compute: the delivery hover height is not the cruise height")

# ------------------------------------------------------------------ the day, c9 c10
day_pct, night_pct = (n(v) for v in grab("c10", r"Approximately (\d+)% of flights .* and (\d+)% of flights", "day and night shares"))
if day_pct + night_pct != 100:
    raise SystemExit("compute: the day and night shares do not make a whole")
hours = n(grab("c9", r"operations (\d+) hours a day", "hours"))

# ------------------------------------------------------------------ a Charger is a site, c32
docks_max, docks_typical = (n(v) for v in grab("c32", r"up to a maximum of (\d+) individual .* most Chargers would have around (\d+) docks", "docks per Charger"))

# ------------------------------------------------------------------ noise, c20 c21 c22
threshold_db = n(grab("c20", r"at or above DNL (\d+) dB", "threshold"))
step_db = n(grab("c20", r"increase the DNL by ([\d.]+) dB", "step"))
delivery_db_at_any_distance = n(grab("c21", r"no more than DNL ([\d.]+) dB at any distance", "delivery DNL"))
delivery_db_cap = n(grab("c21", r"would not exceed DNL ([\d.]+) dB at any point", "cap DNL"))
per_location = n(grab("c21", r"rate of (\d+) average daily deliveries", "per location"))
screen_db = n(grab("c35", r"^([\d.]+) dB, because this is the DNL threshold", "screening line"))
if screen_db != delivery_db_cap:
    raise SystemExit("compute: the draft's screening line is not its delivery cap")
screen_step = n(grab("c35", r"increases of ([\d.]+) dB or more", "screening step"))
if screen_step != step_db:
    raise SystemExit("compute: the screening step is not the FAA's significance step")
existing_db, lift_db = (n(v) for v in grab("c37", r"existing DNL of ([\d.]+) dB, the added noise on its own must be at least a DNL ([\d.]+) dB", "lift"))
if lift_db != delivery_db_cap:
    raise SystemExit("compute: the added noise that lifts 63.5 to 65 is not the delivery cap, frame 7's comparison would be wrong")
setback_ft = n(grab("c22", r"at least (\d+) feet away", "dropbox setback"))
setback_load = n(grab("c22", r"Dropbox with up to (\d+) deliveries per day", "dropbox load"))

figures = {
    "_note": "Every value is extracted from a claim's quote by compute.py, run at build time. Per day values are MAXIMUMS the draft assesses, never deliveries flown. Metre values are geometry only and are never printed; a reader sees the draft's own units.",
    "metros": {k: dict(table[k], **{"from": ["c7"]}) for k in METROS},
    "total": dict(table["Total"], **{"from": ["c7"], "basis": "the draft's maximum"}),
    "transits_per_delivery": {"value": legs, "word": "three", "from": ["c8"]},
    "per_charger_max": {"value": per_charger, "from": ["c24"]},
    "cruise": {"feet": cruise_ft, "metres": m3(cruise_ft), "from": ["c11"], "rounding": "feet times 0.3048, three decimals, geometry only"},
    "aircraft": {"span_ft": span_ft, "height_ft": height_ft, "length_ft": length_ft,
                 "span_m": m3(span_ft), "height_m": m3(height_ft), "length_m": m3(length_ft),
                 "propellers": props, "weight_lb": weight_lb, "payload_lb": payload_lb,
                 "from": ["c13", "c14"], "basis": "approximately, as the draft says"},
    "delivery_hover": {"seconds": hover_s, "feet": hover_ft, "from": ["c19"]},
    "day": {"hours": hours, "day_pct": day_pct, "night_pct": night_pct, "from": ["c9", "c10"]},
    "noise": {"threshold_dnl_db": threshold_db, "significant_step_db": step_db,
              "delivery_dnl_db_any_distance": delivery_db_at_any_distance, "delivery_dnl_db_cap": delivery_db_cap,
              "at_deliveries_per_location": per_location, "screening_dnl_db": screen_db, "lift_existing_dnl_db": existing_db, "lift_added_dnl_db": lift_db,
              "from": ["c20", "c21", "c26", "c35", "c37"]},
    "charger_docks": {"max": docks_max, "typical": docks_typical, "from": ["c32"], "basis": "a Charger is a site of docks, not one mast"},
    "charger_towers": {"docks": n(grab("c34", r"consist of (\d+) docks", "typical docks")), "towers_word": grab("c34", r"arranged in (\w+) towers", "towers"), "from": ["c34"]},
    "dropbox_setback": {"feet": setback_ft, "metres": m3(setback_ft), "load_per_day": setback_load, "from": ["c22"]},
}
SLUG = {"Houston": "houston", "San Antonio": "san_antonio", "Austin": "austin", "Amarillo": "amarillo", "El Paso": "el_paso"}
figures["chargers"] = dict({SLUG[k]: table[k]["chargers"] for k in METROS}, **{"from": ["c7"]})
figures["deliveries"] = dict({SLUG[k]: table[k]["deliveries_max"] for k in METROS}, **{"from": ["c7"], "basis": "the draft's maximum per day"})
(HERE / "figures.json").write_text(json.dumps(figures, indent=1) + "\n", encoding="utf-8")
print("compute: figures.json written, table totals, transit legs and charger caps all hold")
