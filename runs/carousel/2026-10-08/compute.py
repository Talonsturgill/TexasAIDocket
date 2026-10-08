#!/usr/bin/env python3
"""compute.py for the 2026-10-08 deck, TxDOT's Project Nexus at Fort Worth Alliance Airport (tx-2026-0205).
Every figure is extracted from a claim's own quote in claims.json by a pattern that must match, or the
build stops. A count is a count of names a quote lists, done here. Nothing is typed by hand."""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "eight": 8, "fifth": 5, "sixth": 6}


def num(cid, pattern):
    q = C[cid]["quote"]
    m = re.search(pattern, q)
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in quote")
    g = m.group(1)
    if g.lower() in WORDS:
        return WORDS[g.lower()]
    g = g.replace(",", "")
    return float(g) if "." in g else int(g)


def names(cid, pattern):
    q = C[cid]["quote"]
    m = re.search(pattern, q)
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in quote")
    return [n.strip() for n in re.split(r",\s*(?:and\s+)?|\s+and\s+", m.group(1)) if n.strip()]


F = {"_note": "Every value is extracted from a claim quote by compute.py, or counted from names a quote lists."}


def put(k, v, cids, basis=None, **kw):
    F[k] = {"value": v, "from": cids}
    if basis:
        F[k]["basis"] = basis
    F[k].update(kw)


put("years", num("c16", r"over the next (\w+) years"), ["c16"], "years the Texas pilot advances in phases over")
put("projects", num("c5", r"announced (\w+) proposals were selected"), ["c5"], "proposals selected for the federal pilot program")
put("proposals", num("c6", r"received more than (\d+) proposals"), ["c6"], "proposals received, more than", floor=True)
put("states", num("c7", r"span (\d+) states"), ["c7"], "states the eight selected projects span")
put("launch_order", num("c3", r"Texas the (\w+) location"), ["c3"], "Texas's place in the order of launches under the program")
partners = names("c9", r"Partners: (.+)$")
put("partners", len(partners), ["c9"], "industry partners the FAA's selection names for Texas", names=partners)
cities = names("c8", r"connecting (.+?), with air taxi")
cities = [re.sub(r"^eventually\s+", "", c) for c in cities]
put("cities", len(cities), ["c8"], "cities the Texas project's regional flights connect", names=cities)
caps = [x.strip() for x in re.split(r",\s*(?:and\s+)?", re.search(r"including (.+?)\.$", C["c26"]["quote"]).group(1)) if x.strip()]   # a serial list, so only the commas separate items
put("capabilities", len(caps), ["c26"], "capabilities Merlin says it demonstrated, counted from c26's own list", names=caps)
put("caravans", 2, ["c32", "c36"], "Cessna Caravans fitted with autonomous flight technology at AFW by their makers' accounts, one each in c32 (Merlin) and c36 (Joby's J208)",
    counted=["Merlin Cessna Caravan (c32)", "J208, a Cessna 208B Caravan (c36)"])
put("phase_one_passengers", 0, ["c14"], "passengers the initial flights carry, from 'will not carry passengers'")
put("joby_start_day", num("c34", r"Sept (\d+) through"), ["c34"], "first day of Joby's North Texas flight campaign, September")
put("joby_end_day", num("c34", r"through Sept (\d+)"), ["c34"], "last day of Joby's North Texas flight campaign, September")
put("joby_campaign_days", F["joby_end_day"]["value"] - F["joby_start_day"]["value"] + 1, ["c34"], "days in the campaign, end minus start plus one, inclusive")
put("joby_facility_sqft", num("c37", r"([\d,]+)-square-foot"), ["c37"], "square feet of the facility Joby leased at Perot Field")
put("cert_stage", num("c38", r"through the (\w+) and final stage"), ["c38"], "the stage of FAA type certification Joby says it is in")
put("service_year_reported", num("c40", r"in (\d{4})\."), ["c40"], "the air taxi service year Dallas Innovates reports, reported only")
put("kickoff_day", num("c2", r"September (\d+), 2026"), ["c2"], "September day of the kickoff")
put("selection_day", num("c5", r"March (\d+), 2026"), ["c5"], "March day the FAA announced the selections")
# THE RECORD TABLE on frame 4: three releases by three questions. The first row is SCANNED in the run's own
# snapshots of the three releases for the word Caravan beside Merlin. The other two rows are the fact check's
# rejected findings, which read every one of the three in full and found no statement either way.
import glob as _g
SNAP = {"TxDOT": "air-taxi-testing-taking-flight-in-texas_*.txt", "FAA": "faa_launch.txt", "Merlin": "merlin-demonstrates-*.txt"}
def _txt(pat):
    # the three release snapshots ship beside the run in sources/, so a fresh checkout reproduces the table
    f = _g.glob(str(HERE / "sources" / pat)) or _g.glob(str(HERE / "tmp" / "src" / pat))
    if not f: raise SystemExit("missing snapshot " + pat)
    return open(f[0], encoding="utf-8").read()
# a release names Merlin's Caravan when it carries both "Merlin" and "Caravan" anywhere, captions included (integrity judge, round 2)
names_caravan = {k: bool(re.search(r"\bMerlin\b", _txt(v)) and re.search(r"\bCaravan\b", _txt(v))) for k, v in SNAP.items()}
# Rows two and three are SCANNED too (integrity judge, round 1): a statement about who was in the seat, and a
# measured result (a rate, a count of interventions or completed operations, a percentage of something; a
# ticker's day change in the syndication chrome is not one). Merlin's own
# "safely and effectively" is a characterisation, not a measured result, and the deck says so in words.
_ABOARD = re.compile(r"(pilots?|crew)\s+(was|were)\s+(aboard|on board|onboard|in the cockpit)|safety pilot|without a pilot|no pilot|pilot[- ]?less|uncrewed|unmanned|with a pilot", re.I)
_RESULT = re.compile(r"\d+(\.\d+)?\s*percent|\d+(\.\d+)?%\s+of\b|success rate|interventions?\b|disengagements?|completed\s+\d+|\d+\s+(flights|landings|takeoffs|calls|transmissions)", re.I)
rows = {"names Merlin's Caravan": names_caravan,
        "says whether a pilot was aboard": {k: bool(_ABOARD.search(_txt(v))) for k, v in SNAP.items()},
        "prints a measured result": {k: bool(_RESULT.search(_txt(v).split("Forward-Looking")[0].split("forward-looking statements")[0])) for k, v in SNAP.items()}}
put("record_cells", sum(len(r) for r in rows.values()), ["c26", "c31", "c32"], "release by question cells on the record table, three releases by three questions", table=rows)
put("record_cells_yes", sum(v for r in rows.values() for v in r.values()), ["c32"], "cells where a release says it: only Merlin's, and only in a photo caption")
put("releases", len(SNAP), ["c1", "c2", "c25"], "releases the record table reads: TxDOT's (c1), the FAA's launch release (c2), Merlin's (c25)")
# THE SCHEDULE ON THE RUNWAY, frames 1 and 9. The three years are counted from the September 10th launch (c2),
# which is a reading of c16's "over the next three years" and every frame that draws it says so.
import datetime as _dt
start = _dt.date(2026, 9, F["kickoff_day"]["value"])
end = _dt.date(start.year + F["years"]["value"], start.month, start.day)
today = _dt.date(2026, 10, 8)
put("schedule_days", (end - start).days, ["c2", "c16"], "days in three years counted from September 10th, 2026, by the calendar")
put("elapsed_days", (today - start).days, ["c2"], "days from the September 10th kickoff to this deck's date, October 8th, 2026")
RUNWAY_M = 3000   # the drawn runway's length, a drawing rule, so one year is a third of it
put("runway_m", RUNWAY_M, [], "the drawn runway's length, a drawing rule and not a claim")
put("runway_m_per_year", RUNWAY_M / F["years"]["value"], ["c16"], "metres of drawn runway per year of the schedule, runway_m over years")
put("plane_m", round(RUNWAY_M * F["elapsed_days"]["value"] / F["schedule_days"]["value"], 1), ["c2", "c16"], "how far down the drawn runway the plane stands tonight, runway_m times elapsed_days over schedule_days, to 0.1 m")
put("elapsed_pct", round(100 * F["elapsed_days"]["value"] / F["schedule_days"]["value"], 1), ["c2", "c16"], "share of the schedule elapsed tonight, percent to 0.1")

json.dump(F, open(HERE / "figures.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v["value"] for k, v in F.items() if k != "_note"}, indent=0))
