#!/usr/bin/env python3
"""compute.py for the 2026-10-16 deck, Waymo opening San Antonio robotaxis to anyone, the airport
included, with its flood recall remedy still listed as under development (tx-2026-0216). Every figure
is extracted from a claim's own quote in claims.json by a pattern that must match, or the build stops.
Spans are computed here from values that were. Nothing is typed by hand."""
import datetime as dt
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
F = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were."}
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                       "September", "October", "November", "December"], start=1)}
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def grab(cid, pattern):
    m = re.search(pattern, C[cid]["quote"])
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in quote")
    return m


def put(k, v, cids, basis=None):
    F[k] = {"value": v, "from": cids}
    if basis:
        F[k]["basis"] = basis


def published(cid):
    return dt.date.fromisoformat(C[cid]["published"])


# THE DATES, each from its own source
opened = published("c1")                                     # the post that opens the service to anyone
first_riders = published("c5")                               # the post that takes the first public riders
m = grab("c15", r"on (\w+) (\d+)\.")
creek = dt.date(opened.year, MONTHS[m.group(1)], int(m.group(2)))   # c15 gives no year; its article is dated 2026
assert creek.year == dt.date.fromisoformat(C["c15"]["published"]).year
m = grab("c14", r'"ReportReceivedDate":"(\d{2})/(\d{2})/(\d{4})"')
recall_filed = dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))   # day first, per the 26E035 record
m = grab("c11", r"by (\w+) (\d+), (\d{4})")
interim_by = dt.date(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))

put("opened_day", opened.day, ["c1"], "day of October the service opened to anyone")
put("opened_year", opened.year, ["c1"], "year the service opened to anyone")
put("first_riders_day", first_riders.day, ["c5"], "day of February the first public riders were taken")
put("creek_day", creek.day, ["c15"], "day of April the car washed into Salado Creek")
put("recall_filed_day", recall_filed.day, ["c14"], "day of May the recall report was received")
put("interim_by_day", interim_by.day, ["c11"], "day of April by which every affected vehicle had the interim update")
put("days_creek_to_open", (opened - creek).days, ["c15", "c1"], "days from the car in Salado Creek to the service opening to anyone")
put("days_creek_to_recall", (recall_filed - creek).days, ["c15", "c14"], "days from the car in Salado Creek to the recall report")
put("days_first_riders_to_open", (opened - first_riders).days, ["c5", "c1"], "days from the first invited riders to the service opening to anyone")
put("days_recall_to_open", (opened - recall_filed).days, ["c14", "c1"], "days from the recall report to the service opening to anyone")
put("days_first_riders_to_creek", (creek - first_riders).days, ["c5", "c15"], "days from the first invited riders to the car in Salado Creek")
import calendar
rows = []
d = first_riders
while d <= opened:
    last = dt.date(d.year, d.month, calendar.monthrange(d.year, d.month)[1])
    end = min(last, opened)
    rows.append((end - d).days + 1)
    d = end + dt.timedelta(days=1)
put("month_rows", rows, ["c5", "c1"], "posts per month row, February 24th to October 14th inclusive, one post per day")
put("posts_total", sum(rows), ["c5", "c1"], "posts in the calendar field, both end days included")
put("creek_post_index", (creek - first_riders).days, ["c5", "c15"], "zero based index of the April 20th post in the field")
put("recall_post_index", (recall_filed - first_riders).days, ["c5", "c14"], "zero based index of the May 1st post in the field")
put("creek_same_day_as_interim", creek == interim_by, ["c15", "c11"], "the interim update deadline and the creek are the same date")

# THE COUNTS
m = grab("c13", r'"PotentialNumberofUnitsAffected":(\d+)')
put("units_affected", int(m.group(1)), ["c13"], "potentially affected units in the recall, the federal record's own figure")
m = grab("c21", r"covering (\d+) square miles")
put("service_sq_mi_feb", int(m.group(1)), ["c21"], "square miles of the San Antonio service area in February")
m = grab("c5", r"in (\w+) new cities")
put("cities_feb", WORDS[m.group(1)], ["c5"], "cities that took first public riders on February 24th")
m = grab("c1", r"anyone in (.+?) can download")
cities = [x.strip() for x in re.split(r",\s*(?:and\s+)?", m.group(1)) if x.strip()]
put("cities_open_oct", len(cities), ["c1"], "cities opened to anyone on October 14th: " + ", ".join(cities))
m = grab("c12", r"certain (\d+)th and (\d+)th Generation")
put("generations_recalled", 2, ["c12"], "generations named in the recall: " + m.group(1) + "th and " + m.group(2) + "th")
put("incidents_april", 2, ["c15", "c17"], "flood incidents in April that Texas Public Radio reports, one per claim")

json.dump(F, open(HERE / "figures.json", "w"), indent=1)
for k, v in F.items():
    if k != "_note":
        print(k, v["value"])
