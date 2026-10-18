"""Every figure the October 18th deck states or draws, extracted from a claim quote or computed here.

No figure in the deck is typed. Each value below is parsed out of the verified quote it cites in
claims.json, and figures.json is written from this file alone.
"""
import json
import re
from datetime import date
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

F("drone_flights", num(grab("c10", r"more than ([\d,]+) times")), ["c10"], "drone flights over Texas since June, more than, as KRGV reports USDA")
F("animals_seen", num(grab("c11", r"more than ([\d,]+) animals")), ["c11"], "animals the drone flights observed, more than")
F("drone_cases", 0, ["c11"], "screwworm cases the drone flights found, the quote's 'no screwworm cases'")
assert "found no screwworm cases" in quote("c11")
F("flights_july", num(grab("c17", r"over ([\d,]+) drone surveillance flights")), ["c17"], "drone flights by the APHIS page last modified July 31st, over")
F("animals_july", num(grab("c17", r"observing over ([\d,]+) animals")), ["c17"], "animals observed by the same page, over")
F("flies_weekly_m", int(grab("c19", r"more than (\d+) million sterile flies per week")), ["c19"], "millions of sterile flies the Edinburg facility deploys a week, more than")
F("dispersal_capacity_m", int(grab("c20", r"up to (\d+) million sterile flies per week")), ["c20"], "millions of sterile flies a week the Edinburg facility can disperse, up to")
F("production_projected_m", int(grab("c21", r"capacity of (\d+) million sterile flies per week")), ["c21"], "millions of sterile flies a week the South Texas production plant is projected to make")
F("facility_cost_m", float(grab("c19", r"\$([\d.]+) million facility")), ["c19"], "cost in millions of dollars of the Edinburg dispersal facility")
F("counties_confirmed", int(grab("c27", r"detection: (\d+)")), ["c27"], "Texas counties with a confirmed detection, read October 18th")
F("premises_confirmed", int(grab("c28", r"detection: (\d+)")), ["c28"], "Texas premises with at least one confirmed detection, read October 18th")
F("first_case_day", int(grab("c26", r"On June (\d+), 2026")), ["c26"], "day of June of the first Texas confirmation")
F("eradicated_year", int(grab("c25", r"United States in (\d{4})")), ["c25"], "year the sterile insect technique helped eradicate screwworm from the United States")
F("keys_year", int(grab("c25", r"Florida Keys in (\d{4})")), ["c25"], "year of the Florida Keys outbreak the technique eliminated")
F("wild_animals", num(grab("c22", r"more than ([\d,]+) wild animals")), ["c22"], "wild animals APHIS examined, more than")
F("wild_species", int(grab("c22", r"across (\d+) species")), ["c22"], "species among them")
zone = re.search(r"following Texas counties: (.+)\.$", quote("c29")).group(1)
zone_counties = [c.strip() for c in zone.split(",")]
F("zone_counties", len(zone_counties), ["c29"], "counties with part of the infested zone: " + ", ".join(zone_counties))
F("report_hours", int(grab("c30", r"within (\d+) hours")), ["c30"], "hours from suspicion within which a case should be reported")
F("chiapas_year", int(grab("c32", r"In November (\d{4})")), ["c32"], "year screwworm was detected at the Chiapas checkpoint")
uses = re.search(r"select areas for increased (.+)$", quote("c4")).group(1)
use_list = [u.strip() for u in re.split(r", and |, ", uses) if u.strip()]
F("model_uses", len(use_list), ["c4"], "uses the Kerrville director names for the models: " + "; ".join(use_list))
# computed
F("herd_drawn", figures["animals_seen"]["value"] // 1000, ["c11"], "animals drawn on frame 7, one per thousand the drones observed, 36,000 divided by 1,000")
first = date(2026, 6, figures["first_case_day"]["value"])
F("days_since_first", (date(2026, 10, 18) - first).days, ["c26"], "days from the first Texas confirmation, June 3rd, to October 18th, 2026, the reading date")
F("years_since_eradication", 2026 - figures["eradicated_year"]["value"], ["c25"], "years from the 1966 eradication to 2026")
F("capacity_share_pct", round(100 * figures["flies_weekly_m"]["value"] / figures["dispersal_capacity_m"]["value"]), ["c19", "c20"],
  "the July 31st deployment as a share of the stated capacity, rounded to a whole percent; two different pages, so drawn only as two lengths, never printed as a percent")
F("production_over_capacity", figures["production_projected_m"]["value"] / figures["dispersal_capacity_m"]["value"], ["c20", "c21"], "projected production over dispersal capacity, a ratio of two quoted figures")

(HERE / "figures.json").write_text(json.dumps(figures, indent=1) + "\n")
for k, v in figures.items():
    if k != "_note":
        print(f"{k:26} {v['value']}")
