"""Every figure the October 21st deck states or draws, extracted from a claim quote or computed here.

No figure in the deck is typed. Each value below is parsed out of the verified quote it cites in
claims.json, and figures.json is written from this file alone.
"""
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

F("invest_m", num(grab("c1", r"investing \$(\d+) million")), ["c1"], "millions of dollars Lockheed says it is investing at Grand Prairie")
F("footprint_sqft", num(grab("c1", r"more than ([\d,]+) square feet")), ["c1"], "square feet the manufacturing footprint expands to, more than")
F("new_sqft", num(grab("c2", r"includes ([\d,]+) square feet of new space")), ["c2"], "square feet of new space")
F("office_sqft", num(grab("c2", r"and ([\d,]+) square feet of office space")), ["c2"], "square feet of office space turned to manufacturing")
F("cell_machines", int(grab("c4", r"the (\d+)-machine cell")), ["c4"], "machines in the Hadrian cell")
F("cell_year", int(grab("c4", r"operational in early (\d{4})")), ["c4"], "year the cell is expected to be operational, early")
F("jobs_us", num(grab("c5", r"create ([\d,]+) jobs")), ["c5"], "jobs Lockheed plans across the United States, its own figure")
F("jobs_tx", num(grab("c5", r"including ([\d,]+) in Texas")), ["c5"], "of those, jobs in Texas, its own figure")
F("added_machines", int(grab("c10", r"more than (\d+) additional")), ["c10"], "high precision machines installed in a few months, more than")
F("machines_by_2026", int(grab("c11", r"nearly (\d+) new advanced machines")), ["c11"], "new advanced machines expected by the end of 2026, nearly")
F("employees", int(grab("c12", r"Nearly (\d+) production employees")), ["c12"], "production employees, nearly")
F("parts_2025", num(grab("c12", r"manufactured ([\d,]+) parts")), ["c12"], "parts the facility made in 2025")
F("parts_year", int(grab("c12", r"parts in (\d{4})")), ["c12"], "the year of the parts count")
F("agreement_years", {"seven": 7}[grab("c13", r"a (\w+)-year agreement")], ["c13"], "years in the Lockheed and Hadrian agreement, the quote's 'seven'")
F("agreement_signed", int(grab("c13", r"companies in (\d{4})")), ["c13"], "year the agreement was signed")
F("facilities_us", int(grab("c9", r"more than (\d+) facilities")), ["c9"], "facilities Lockheed says it will modernize or expand, more than")
F("hadrian_sites", {"four": 4}[grab("c17", r"operates (\w+) facilities")], ["c17"], "facilities Hadrian operates, the quote's 'four'")
F("tech_days", int(grab("c23", r"in (\d+) days or less")), ["c23"], "days Hadrian says it trains a factory technician in, or less")
F("pac3_produced", int(grab("c32", r"(\d+)\+ PAC-3 MSEs produced")), ["c32"], "PAC-3 MSEs produced, more than, per the PAC-3 page")
# computed
F("cell_share_of_new_pct", round(100 * figures["cell_machines"]["value"] / figures["machines_by_2026"]["value"]), ["c4", "c11"],
  "the cell's 24 machines as a share of the nearly 100 expected by end of 2026, rounded half up to a whole percent; drawn, never printed")
F("parts_per_employee", figures["parts_2025"]["value"] // figures["employees"]["value"], ["c12"],
  "250,000 parts over nearly 800 employees, floored to a whole part, and the 800 is a nearly; drawn, never printed")

(HERE / "figures.json").write_text(json.dumps(figures, indent=1) + "\n")
print(json.dumps({k: v["value"] for k, v in figures.items() if k != "_note"}))
