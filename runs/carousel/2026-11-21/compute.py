#!/usr/bin/env python3
"""Figures for the November 21st, 2026 carousel, DARPA's Triage Challenge finals at TEEX's Disaster City
in College Station (tx-2026-0254).

Every value is read out of a claim quote by a regex, or computed here from values so read.

RULES, stated so they are choices rather than accidents:
- acres is c11's 52-acre mock community
- participants is c12's more than 100, a floor, always printed with "more than"
- prize_pool_m is c12's over $3 million, a floor, always printed with "more than"
- systems_prize_m is c3's $1.5 million to RoboScout, data_prize_m is c3's $1 million to Disruptors
- winners_m is systems_prize_m + data_prize_m, computed, and printed only if a frame needs it. It is never
  set against the pool as a share, because the pool is a floor
- competitions is c14's five, read from the word
- finals_start_day and finals_end_day are c1's Nov. 5 and Nov. 13. finals_days is the inclusive count of
  days from the first to the last, computed with date arithmetic
- created_year is c21's 2023. years_running is 2026 minus created_year, the finals year from c3
- drone_team is c25's two full-time members, read from the word
- championship_teams is c23's top two, read from the word
- triagex_close is c20's Nov. 25, 2026
- stations is c29's nearly a dozen, never printed as a number
"""
import json, re, datetime as dt
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
def q(cid): return C[cid]["quote"]
def rx(cid, pat):
    m = re.search(pat, q(cid)); assert m, (cid, pat); return m.group(1)
WORDS = {"two": 2, "five": 5}
acres = int(rx("c11", r"a (\d+)-acre mock community"))
participants = int(rx("c12", r"more than (\d+) participants"))
pool = float(rx("c12", r"over \$([\d.]+) million"))
sysp = float(rx("c3", r"Systems competition and \$([\d.]+) million"))
datap = float(rx("c3", r"Data competition and \$([\d.]+) million"))
grand = float(rx("c23", r"the \$([\d.]+) million grand prize"))
assert grand == sysp
competitions = WORDS[rx("c14", r"Each of the (\w+) competitions")]
d0 = int(rx("c1", r"Nov\. (\d+) through")); d1 = int(rx("c1", r"through Friday, Nov\. (\d+)"))
year = int(rx("c3", r"Nov\. \d+, (\d{4})"))
days = (dt.date(year, 11, d1) - dt.date(year, 11, d0)).days + 1
created = int(rx("c21", r"in (\d{4})\."))
team = WORDS[rx("c25", r"just (\w+) full-time members")]
top = WORDS[rx("c23", r"where the top (\w+) competed")]
close_day = int(rx("c20", r"Nov\. (\d+), \d{4}"))
F = {
 "_note": "Every value is extracted from a claim quote by compute.py, or computed here from values so extracted.",
 "acres": {"value": acres, "from": ["c11"], "basis": "acres of Disaster City's mock community"},
 "participants": {"value": participants, "from": ["c12"], "basis": "a floor, printed with more than"},
 "prize_pool_m": {"value": pool, "from": ["c12"], "basis": "millions of dollars in cash prizes, a floor, printed with more than"},
 "systems_prize_m": {"value": sysp, "from": ["c3", "c23"], "basis": "RoboScout's Systems prize and the grand prize, millions of dollars"},
 "data_prize_m": {"value": datap, "from": ["c3"], "basis": "Disruptors' Data prize, millions of dollars"},
 "winners_m": {"value": round(sysp + datap, 1), "from": ["c3"], "basis": "systems_prize_m + data_prize_m, never set against the pool"},
 "competitions": {"value": competitions, "from": ["c14"], "basis": "competitions in the finals"},
 "finals_start_day": {"value": d0, "from": ["c1"], "basis": "November day the finals began"},
 "finals_end_day": {"value": d1, "from": ["c1", "c3"], "basis": "November day the finals ended"},
 "finals_days": {"value": days, "from": ["c1"], "basis": "inclusive days from the first to the last day of the finals"},
 "year": {"value": year, "from": ["c3"], "basis": "the finals year"},
 "created_year": {"value": created, "from": ["c21"], "basis": "the year DARPA created the challenge"},
 "years_running": {"value": year - created, "from": ["c3", "c21"], "basis": "year - created_year"},
 "drone_team": {"value": team, "from": ["c25"], "basis": "full-time members of team DRONE"},
 "championship_teams": {"value": top, "from": ["c23"], "basis": "teams in the championship round"},
 "triagex_close_day": {"value": close_day, "from": ["c20"], "basis": "November day the TRIAGE-X topic closes"},
}
PLATE = 100000  # drawing rule, stated: one machined plate stands for $100,000
F["plate_usd"] = {"value": PLATE, "from": [], "basis": "drawing unit, one brass plate stands for this many dollars, a rule not a measurement"}
F["plates_pool"] = {"value": round(pool * 1e6 / PLATE), "from": ["c12"], "basis": "prize_pool_m * 1e6 / plate_usd, the floor of the purse in plates, the stack runs off the frame because the pool is more than"}
F["plates_systems"] = {"value": round(sysp * 1e6 / PLATE), "from": ["c3"], "basis": "systems_prize_m * 1e6 / plate_usd"}
F["plates_data"] = {"value": round(datap * 1e6 / PLATE), "from": ["c3"], "basis": "data_prize_m * 1e6 / plate_usd"}
F["close_after_finals_days"] = {"value": close_day - d1, "from": ["c1", "c20"], "basis": "triagex_close_day - finals_end_day, days the topic stays open after the finals end"}
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print({k: v["value"] for k, v in F.items() if k != "_note"})
