#!/usr/bin/env python3
"""compute.py for the 2026-10-15 deck, the AI deposition transcript argued before the Supreme Court of
Texas (tx-2026-0127). Every figure is extracted from a claim's own quote or supporting quote in
claims.json by a pattern that must match, or the build stops. Spans and positions are computed here
from values that were. Nothing is typed by hand."""
import datetime as dt
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
F = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were."}
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                       "September", "October", "November", "December"], start=1)}


def text(cid):
    c = C[cid]
    return "\n".join([c["quote"]] + c.get("supporting_quotes", []))


def grab(cid, pattern):
    m = re.search(pattern, text(cid))
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in quote")
    return m


def put(k, v, cids, basis=None):
    F[k] = {"value": v, "from": cids}
    if basis:
        F[k]["basis"] = basis


# the dates, each from its own source
m = grab("c8", r"back in (\w+) (\d{4})")
struck = (int(m.group(2)), MONTHS[m.group(1)])
put("struck_year", struck[0], ["c8"], "the year the trial court struck the transcript")
m = grab("c2", r"Date Filed: (\d{2})/(\d{2})/(\d{4})")
filed = dt.date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
m = grab("c23", r"(\w+), (\w+) (\d+), (\d{4})")
argued = dt.date(int(m.group(4)), MONTHS[m.group(2)], int(m.group(3)))
put("filed_day", filed.day, ["c2"], "day of the month the mandamus was filed")
put("argued_day", argued.day, ["c23"], "day of the month of the argument")
put("argued_year", argued.year, ["c23"], "year of the argument")

# THE STAIR: one riser per calendar month from the strike's month to the argument's month
months = (argued.year - struck[0]) * 12 + (argued.month - struck[1])
put("months_struck_to_argued", months, ["c8", "c23"],
    "calendar months from the strike's month to the argument's month, month granularity because c8 gives no day")
# where the filing sits on that stair: whole months past the strike month, plus the day's share of its month
fm = (filed.year - struck[0]) * 12 + (filed.month - struck[1])
import calendar
frac = round((filed.day - 1) / calendar.monthrange(filed.year, filed.month)[1], 3)
put("filed_step", round(fm + frac, 3), ["c8", "c2"], "the filing's position on the month stair, in risers from the strike month")
put("days_filed_to_argued", (argued - filed).days, ["c2", "c23"], "days from the mandamus filing to the argument")

# THE BENCH
m = grab("c22", r"(\w+) of the (\w+) justices")
put("justices_heard", WORDS[m.group(1).lower()], ["c22"], "justices who heard the argument")
put("justices_seats", WORDS[m.group(2).lower()], ["c22"], "seats on the court")
put("justices_absent", F["justices_seats"]["value"] - F["justices_heard"]["value"], ["c22"], "seats empty at argument")

# THE CLOCK
put("minutes_per_side", int(grab("c25", r"Time for Argument: (\d+) minutes for each side").group(1)), ["c25"], "minutes of argument for each side")
put("real_party_first", int(grab("c25", r"present the first (\d+) minutes").group(1)), ["c25"], "the real party's counsel's minutes")
put("amicus_minutes", int(grab("c25", r"present the remaining (\d+) minutes").group(1)), ["c25"], "the deposition reporters' association's minutes as amicus")
put("argument_minutes_total", 2 * F["minutes_per_side"]["value"], ["c25"], "both sides together")
assert F["real_party_first"]["value"] + F["amicus_minutes"]["value"] == F["minutes_per_side"]["value"]

# THE TWO RECORDS of the one deposition, counted from the claims that name them
recs = [cid for cid, pat in (("c13", r"video recording"), ("c6", r"transcript of a deposition")) if re.search(pat, text(cid))]
put("records_count", len(recs), recs, "the deposition's two records named in the claims, its video recording and its written transcript")

json.dump(F, open(HERE / "figures.json", "w"), indent=1)
for k, v in F.items():
    if k != "_note":
        print(k, v["value"])
