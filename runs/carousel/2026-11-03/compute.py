#!/usr/bin/env python3
"""Figures for carousel no. 67. Every value is read out of a claim quote or computed from values that were."""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
def num(cid, pat):
    m = re.search(pat, C[cid]["quote"]); assert m, (cid, pat); return int(m.group(1).replace(",", ""))
WORDS = {"five": 5, "six": 6}
def word(cid, pat):
    m = re.search(pat, C[cid]["quote"]); assert m, (cid, pat); return WORDS[m.group(1)]
built = num("c1", r"We have (\d+)\+ driverless trucks")
miles = num("c2", r"surpassed ([\d,]+) commercial driverless miles")
on_time = num("c2", r"maintaining (\d+)% on-time")
charger = num("c3", r"own and operate (\d+) trucks"); assert charger == num("c19", r"operate (\d+) Aurora")
deliv_a = num("c4", r"expected in (\d{4}) and"); deliv_b = num("c4", r"and (\d{4}), Charger")
rate = num("c11", r"rate of (\d+) trucks per week")
behind = word("c12", r"about (\w+) weeks behind")
rev26 = num("c12", r"approximately \$(\d+) million")
q3_rev = num("c13", r"totaled \$(\d+) million")
q3_loss = num("c14", r"totaled \$(\d+) million")
milestone = num("c15", r"exceeding the (\d+)-truck milestone")
end27 = num("c16", r"more than ([\d,]+) driverless trucks")
nb_year = num("c18", r"second half of (\d{4})")
exempt = word("c20", r"important, (\w+)-year exemption")
scale_steps = ["determine if a station is open", "navigate to an available scale lane", "adapt to different scale configurations"]
for s in scale_steps: assert s in C["c9"]["quote"], s
causes = ["material availability", "component quality", "end-of-line testing"]
for s in causes: assert s in C["c10"]["quote"], s
F = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were.",
 "trucks_built": {"value": built, "from": ["c1"], "basis": "the '20+' driverless trucks already built"},
 "driverless_miles": {"value": miles, "from": ["c2"], "basis": "commercial driverless miles passed in September"},
 "on_time_pct": {"value": on_time, "from": ["c2"], "basis": "on-time delivery since launch, in percent"},
 "charger_trucks": {"value": charger, "from": ["c3", "c19"], "basis": "trucks under Charger's non-binding MOU"},
 "delivery_first_year": {"value": deliv_a, "from": ["c4"], "basis": "first year of Charger's expected truck delivery"},
 "delivery_last_year": {"value": deliv_b, "from": ["c4"], "basis": "second year of Charger's expected truck delivery"},
 "weekly_rate": {"value": rate, "from": ["c11"], "basis": "targeted trucks per week in early December"},
 "weeks_behind": {"value": behind, "from": ["c12"], "basis": "'about six weeks behind', the word read as a number"},
 "revenue_2026": {"value": rev26, "from": ["c12"], "basis": "expected 2026 revenue, millions of dollars, approximately"},
 "q3_revenue": {"value": q3_rev, "from": ["c13"], "basis": "third quarter revenue, millions of dollars"},
 "q3_operating_loss": {"value": q3_loss, "from": ["c14"], "basis": "third quarter operating loss including stock-based compensation, millions of dollars"},
 "milestone_trucks": {"value": milestone, "from": ["c15"], "basis": "the truck milestone expected by the end of February"},
 "trucks_end_2027": {"value": end27, "from": ["c16"], "basis": "driverless trucks in operation Aurora expects to exceed at the end of 2027"},
 "hardware_start_year": {"value": nb_year, "from": ["c18"], "basis": "planned start of production, second half of 2027"},
 "exemption_years": {"value": exempt, "from": ["c20"], "basis": "the FMCSA exemption's term in years, the word read as a number"},
 "scale_steps": {"value": len(scale_steps), "from": ["c9"], "basis": "computed: the weigh station steps the letter names (station open, scale lane, scale configuration)"},
 "ramp_causes": {"value": len(causes), "from": ["c10"], "basis": "computed: the three constraints the letter names on the ramp"},
}
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print(json.dumps({k: v["value"] for k, v in F.items() if k != "_note"}))
