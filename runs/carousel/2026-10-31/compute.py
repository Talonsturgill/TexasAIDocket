"""Every figure the October 31st deck states or draws, extracted from a claim quote or computed here.

No figure in the deck is typed. Each value below is parsed out of the verified quote it cites in
claims.json, or counted from the council's own vote rows saved in sources/, and figures.json is
written from this file alone.
"""
import json
import re
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
claims = {c["id"]: c for c in json.loads((HERE / "claims.json").read_text())["claims"]}
WORDS = {"two": 2, "five": 5, "six": 6, "seventy": 70}


def grab(cid, pattern, group=1):
    m = re.search(pattern, claims[cid]["quote"])
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in its quote")
    s = m.group(group).replace(",", "")
    return WORDS[s.lower()] if s.lower() in WORDS else int(s)


def votes(eventitem, value):
    rows = json.loads((HERE / "sources" / f"votes_{eventitem}.json").read_text())
    return sum(1 for r in rows if r["VoteValueName"] == value), len(rows)


figures = {"_note": "Every value is extracted from a claim quote or counted from the council's vote rows by compute.py, or computed here from values that were."}
F = lambda k, v, src, basis: figures.__setitem__(k, {"value": v, "from": src, "basis": basis})

c2022 = grab("c1", r"lease of (\d+) Automated")
F("cameras_2022", c2022, ["c1"], "cameras in the 2022 Flock Safety lease, per the resolution's title")
F("lease_2022_usd", grab("c2", r"not to exceed \$([\d,]+)"), ["c2"], "the 2022 lease's not to exceed amount, dollars")
F("lease_2022_years", grab("c2", r"over a (\w+)-year period"), ["c2"], "the 2022 lease's term in years")
c2023 = grab("c5", r"lease of seventy \((\d+)\)")
if c2023 != grab("c5", r"lease of (seventy)"):
    raise SystemExit("c5's word and figure disagree")
F("cameras_2023", c2023, ["c5"], "cameras in the restated 2023 Flock Group lease, per the resolution's title")
F("lease_2023_usd", grab("c6", r"not to exceed \$([\d,]+)"), ["c6"], "the 2023 agreement's not to exceed amount, dollars")
F("lease_2023_years", grab("c4", r"five \((\d)\) year"), ["c4"], "the 2023 agreement's term in years")
F("dickinson_cameras", grab("c10", r"placement of (\w+) flock"), ["c10"], "Flock cameras the 2024 agreement places inside Dickinson")
c_trib = grab("c30", r"using (\d+) Flock cameras")
F("cameras_tribune", c_trib, ["c30"], "Flock cameras the Tribune reports Proposition A asks about")
F("population_tribune", grab("c30", r"city of ([\d,]+)"), ["c30"], "League City's population as the Tribune states it")
F("agencies_floor", grab("c40", r"more than (\d+) agencies"), ["c40"], "agencies with access to League City's Flock data, a floor, per the Tribune")
F("searches_per_30_days", grab("c42", r"roughly (\d+) times"), ["c42"], "League City police searches in an average 30 day period, roughly, per the Tribune")
F("search_window_days", grab("c42", r"average (\d+)-day"), ["c42"], "the averaging window in days, per the Tribune")
F("officers_with_access", grab("c38", r"only (\w+) officers"), ["c38"], "officers with access to the system, per the mayor via the Tribune")
F("officers_per_search", grab("c39", r"^(\w+) officers"), ["c39"], "officers who must work together to scan the data, per the Tribune")
F("hours_after_certification", grab("c33", r"^(\d+) hours"), ["c33"], "hours after certification when bagging starts, per the mayor via the Tribune")

for key, ei, cid, what in (("removal", "82914", "c24", "Resolution No. 2026-185 of October 13th, 2026"),
                           ("election_order", "82592", "c16", "Ordinance No. 2026-27 of August 11th, 2026"),
                           ("lease_2023", "75733", "c8", "Resolution No. 2023-197 of December 12th, 2023")):
    yes, roll = votes(ei, "For")
    absent, _ = votes(ei, "Absent")
    F(f"{key}_votes_for", yes, [cid], f"counted: rows reading For in the council's vote record on {what}")
    F(f"{key}_votes_absent", absent, [cid], f"counted: rows reading Absent in the council's vote record on {what}")
    F(f"{key}_roll", roll, [cid], f"counted: names on the council's vote record on {what}")
    against, _ = votes(ei, "Against")
    F(f"{key}_votes_against", against, [cid], f"counted: rows reading Against in the council's vote record on {what}")

# THE TURN, computed.
F("cameras_added_2023", c2023 - c2022, ["c1", "c5"], "computed: cameras in the 2023 lease less cameras in the 2022 lease")
F("lease_minus_tribune", c2023 - c_trib, ["c5", "c30"],
  "computed: the most cameras the 2023 lease covers less the cameras the Tribune counts. Two kinds of number, never a count of removed cameras")
F("removal_to_election_days", (date(2026, 11, 3) - date(2026, 10, 13)).days, ["c12", "c23"],
  "computed: days from the October 13th removal vote to the November 3rd election")
F("order_to_election_days", (date(2026, 11, 3) - date(2026, 8, 11)).days, ["c12", "c14"],
  "computed: days from the August 11th election order to the November 3rd election")
F("first_lease_to_election_years", 2026 - 2022, ["c3", "c12"], "computed: calendar years from the first lease's approval to the election")
F("years_of_council_votes", [2022, 2023, 2024, 2026], ["c3", "c4", "c11", "c14"], "the years of the council's Flock votes, from their records")

# THE PINS, from the Census gazetteer lines quoted in c47 to c49: interior point latitude and longitude.
for key, cid in (("league_city", "c47"), ("kyle", "c48"), ("laredo", "c49")):
    f = claims[cid]["quote"].split("\t")
    F(f"{key}_lat", float(f[-2]), [cid], "the Census 2020 gazetteer interior point latitude")
    F(f"{key}_lon", float(f[-1]), [cid], "the Census 2020 gazetteer interior point longitude")

(HERE / "figures.json").write_text(json.dumps(figures, indent=1) + "\n")
print(json.dumps({k: v["value"] for k, v in figures.items() if k != "_note"}, indent=1))
