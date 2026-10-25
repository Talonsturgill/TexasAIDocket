"""Every figure the October 25th deck states or draws, extracted from a claim quote or computed here.

No figure in the deck is typed. Each value below is parsed out of the verified quote it cites in
claims.json, and figures.json is written from this file alone.
"""
import datetime as dt
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
    return int(s.replace(",", ""))


figures = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were."}
F = lambda k, v, src, basis: figures.__setitem__(k, {"value": v, "from": src, "basis": basis})

# THE TRIBUNE'S RECORDS, 2020 through 2025 (c27, c28, c29)
fac = num(grab("c27", r"identified ([\d,]+) unique data center facilities"))
sub = num(grab("c28", r"Of those, ([\d,]+) facilities"))
never = num(grab("c29", r"and ([\d,]+) facilities never submitted"))
F("facilities", fac, ["c27"], "data center facilities in the Tribune's records, 2020 through 2025")
F("submitted", sub, ["c28"], "facilities that submitted the water survey at least once, per the Tribune")
F("never", never, ["c29"], "facilities that never submitted a requested survey, per the Tribune")
if sub + never != fac:
    raise SystemExit("the submitted and never counts no longer sum to the facilities count")
F("never_pct", round(100 * never / fac), ["c27", "c29"], "computed: never submitted over facilities, as a whole percent, rounded half up from 69.76")
F("submitted_pct", round(100 * sub / fac), ["c27", "c28"], "computed: submitted at least once over facilities, as a whole percent")
F("record_first_year", int(grab("c27", r"covering (\d{4}) through")), ["c27"], "the first year of the Tribune's records")
F("record_last_year", int(grab("c27", r"through (\d{4})")), ["c27"], "the last year of the Tribune's records")

# THE PENALTY (c31) and the survey's reach (c38)
F("fine", num(grab("c31", r"\$([\d,]+) fine")), ["c31"], "the most a Class C misdemeanor fine can be, in dollars")
F("survey_gallons_million", int(grab("c38", r"more than (\d+) million gallons")), ["c38"], "the survey targets facilities using more than this many million gallons a year")

# 2025, per the Tribune (c44, c45)
F("surveyed_2025", num(grab("c44", r"Of the ([\d,]+) facilities")), ["c44"], "facilities the water board surveyed in 2025")
F("new_2025", num(grab("c44", r", ([\d,]+) are new")), ["c44"], "of those, new to the board's tracking")
F("new_2025_resp_pct", float(grab("c44", r"only ([\d.]+)%")), ["c44"], "the share of the new facilities that responded, as printed")
F("completed_last_year", num(grab("c45", r"^([\d,]+) facilities completed")), ["c45"], "facilities that completed the survey last year")
F("gallons_billion", float(grab("c45", r"([\d.]+) billion gallons")), ["c45"], "billion gallons those facilities reported together")

# ERCOT'S NOTICE (c1, c4, c7, c19, c22, c26)
F("mw_floor", int(grab("c4", r"at least (\d+) MW")), ["c3", "c4"], "the smallest peak requested load the request reaches, MW")
F("mw_upper", int(grab("c4", r"less than (\d+) MW")), ["c4"], "the top of the smaller developers' band, MW")
F("kv", int(grab("c7", r"\((\d+) kV")), ["c7"], "transmission voltage, kV and above")
F("business_days", {"two": 2}[grab("c22", r"within (\w+) Business Days")], ["c22"], "business days a service provider had to enter the developer's contact")
notice = dt.datetime.strptime(grab("c1", r"NOTICE DATE: (\w+ \d+, \d{4})"), "%B %d, %Y").date()
due = dt.datetime.strptime(grab("c19", r"on (\w+ \d+, \d{4})"), "%B %d, %Y").date()
report = dt.datetime.strptime(grab("c26", r"later than (\w+ \d+, \d{4})"), "%B %d, %Y").date()
F("due_hour", int(grab("c19", r"(\d+) p\.m\.")), ["c19"], "the response deadline's hour, p.m. Central Prevailing Time")
F("notice_to_due_days", (due - notice).days, ["c1", "c19"], "computed: calendar days from the notice date to the response deadline")
F("due_to_report_days", (report - due).days, ["c19", "c26"], "computed: calendar days from the response deadline to the expected report")
F("today_to_report_days", (report - dt.date(2026, 10, 25)).days, ["c26"], "computed: calendar days from this deck's date, October 25th, 2026, to the expected report")
F("due_day", due.day, ["c19"], "the day of October the responses were due")
F("report_day", report.day, ["c26"], "the day of December the report is expected by")

# INSIDE CLIMATE NEWS (c55)
F("permit_actions", int(grab("c55", r"identified (\d+) permitting actions")), ["c55"], "permitting actions FracTracker and Public Citizen counted after the pause, their count")


# THE THRESHOLD AS A HELD VOLUME (c38) and what last year's answers reported (c45)
import math
GAL_M3 = 0.003785411784                      # the US gallon in cubic metres, by definition
thr_gal = figures["survey_gallons_million"]["value"] * 1_000_000
F("tank_diameter_m", 60, ["c38"], "a drawing rule: the threshold tank is drawn 60 m across")
F("tank_height_m", round(thr_gal * GAL_M3 / (math.pi * 30 ** 2), 1), ["c38"], "computed: 10 million US gallons in cubic metres over the area of a 60 m circle, to 0.1 m")
F("tanks_reported", round(figures["gallons_billion"]["value"] * 1_000_000_000 / thr_gal), ["c45", "c38"], "computed: the 1.4 billion gallons reported over the 10 million gallon threshold, tanks of it")

(HERE / "figures.json").write_text(json.dumps(figures, indent=1) + "\n")
print("figures.json:", len(figures) - 1, "figures")
