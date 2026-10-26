"""Every figure the October 26th deck states or draws, extracted from a claim quote or computed here.

No figure in the deck is typed. Each value below is parsed out of the verified quote it cites in
claims.json, and figures.json is written from this file alone.
"""
import json
import math
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

FT = 0.3048          # metres in a foot, by definition
MI = 1609.344        # metres in a statute mile, by definition

# THE HEIGHT (c40, c45) and THE REACH (c3, c33)
ft = num(grab("c40", r"above (\d+) feet"))
F("station_ft", ft, ["c40"], "the aircraft holds station above this many feet while the droid rides the tether down, per DroneXL")
F("station_m", round(ft * FT, 1), ["c40"], "computed: feet times 0.3048, to one decimal")
F("cruise_ft", num(grab("c45", r"about (\d+) feet")), ["c45"], "about this many feet in flight, per DroneXL")
F("cruise_mph", num(grab("c45", r"up to (\d+) mph")), ["c45"], "top speed in mph, per DroneXL")
miles = {"three": 3}[grab("c3", r"within (\w+) miles")]
F("reach_mi", miles, ["c3"], "the company's service reach from the ETJ facility, in miles, as Round Rock relays it")
F("reach_m", round(miles * MI), ["c3"], "computed: miles times 1,609.344, to the metre")
area = math.pi * miles ** 2
F("reach_sq_mi", round(area, 1), ["c3"], "computed: the area of a circle of that radius in square miles, to one decimal")
# THE AUSTIN CEILING in the FAA draft, as DroneXL relays it (c36)
F("austin_chargers", num(grab("c36", r"ceiling is (\d+) Chargers")), ["c36"], "Chargers in the draft's Austin ceiling, per DroneXL")
F("austin_dropboxes", num(grab("c36", r"(\d+) Dropbox")), ["c36"], "Dropbox pickup kiosks in the draft's Austin ceiling, per DroneXL")
F("austin_per_day", num(grab("c36", r"([\d,]+) deliveries a day")), ["c36"], "deliveries a day in the draft's Austin ceiling, per DroneXL")
sqm = num(grab("c36", r"across ([\d,]+) square miles"))
F("austin_sq_mi", sqm, ["c36"], "square miles in the draft's Austin ceiling, per DroneXL")
F("austin_over_reach", round(sqm / area), ["c3", "c36"], "computed: the draft's Austin area over the three mile circle's area, to the whole number")
# THE ORDER (c32, c37, c42, c46, c47)
F("first_order_day", int(grab("c32", r"October (\d+)")), ["c32"], "the day in October the first Round Rock orders were taken, per DroneXL")
F("comment_close_day", int(grab("c37", r"October (\d+)")), ["c37"], "the day in October the FAA comment period closed, per DroneXL")
F("days_after", int(grab("c37", r"October \d+, (\w+) days").replace("two", "2")), ["c37"], "days the comment period ran after the first order, as DroneXL states it")
if figures["comment_close_day"]["value"] - figures["first_order_day"]["value"] != figures["days_after"]["value"]:
    raise SystemExit("the two October days no longer differ by the stated count")
F("rowlett_vote_for", int(grab("c47", r"Motion passed (\d)-0")), ["c47"], "votes for Rowlett's hub and kiosk ordinance")
F("rowlett_vote_against", int(grab("c47", r"Motion passed \d-(\d)")), ["c47"], "votes against")
F("rowlett_year", int(grab("c46", r"(\d{4})")), ["c46"], "the year of Rowlett's vote")
F("first_5000", num(grab("c29", r"first ([\d,]+) residents")), ["c29"], "residents in First Flight's early access, per Zipline")
F("pod_lb", num(grab("c38", r"about (\d+) pounds")), ["c38"], "delivery weight limit, about this many pounds, per DroneXL citing Community Impact")
F("tether_seconds", num(grab("c39", r"about (\d+) seconds")), ["c39"], "the delivery sequence on the tether takes about this many seconds, per DroneXL")
F("checks_per_s", num(grab("c21", r"more than (\d+) safety")), ["c21"], "safety checks a second, per Zipline")
F("adjust_ms", num(grab("c21", r"every (\d+) milliseconds")), ["c21"], "position adjustment interval in ms, per Zipline")
F("app_businesses", num(grab("c44", r"counted (\d+) businesses")), ["c44"], "businesses on the app in Round Rock on day one, per News 4 via DroneXL")

(HERE / "figures.json").write_text(json.dumps(figures, indent=1) + "\n")
print(json.dumps({k: v["value"] for k, v in figures.items() if k != "_note"}))
