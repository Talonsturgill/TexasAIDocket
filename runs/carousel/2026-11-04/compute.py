#!/usr/bin/env python3
"""Figures for carousel no. 68. Every value is read out of a claim quote or computed from values that were."""
import json, re, datetime
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
def num(cid, pat, f=float):
    m = re.search(pat, C[cid]["quote"]); assert m, (cid, pat); return f(m.group(1).replace(",", ""))
boe = num("c6", r"Total production was ([\d,]+) barrels", int)
qoq = num("c6", r"a (\d+)% increase", int)
oil = num("c7", r"production was ([\d,]+) barrels of oil per day", int)
ftday = num("c8", r"averaging over ([\d,]+) feet per day", int)
capex = num("c9", r"were \$(\d+) million", int)
acres = num("c10", r"approximately ([\d,]+) net acres", int)
oil26 = num("c12", r"target to ([\d.]+) MBbls/d")
oil4q = num("c13", r"over (\d+) MBbls/d", int)
tx_pct = num("c15", r"Approximately (\d+)% of our net leasehold", int)
nm_pct = num("c15", r"remaining (\d+)% is located", int)
lease25 = num("c16", r"approximately ([\d,]+) net leasehold", int)
xom_techs = num("c25", r"more than (\d+) technologies", int)
xom_year = num("c20", r"by year-end (\d{4})", int)
xom_target = num("c26", r"approximately ([\d.]+) million", float)
xom_target_year = num("c26", r"per day by (\d{4})", int)
# computed
oil_share_pct = round(100 * oil / boe, 1)            # rule: one decimal, half up via round on a float of exact ints
HOURS = 24                                           # hours in a day, the divisor
ft_per_hour = round(ftday / HOURS, 1)                # rule: one decimal
rrc_date = datetime.date(2026, 5, 21); rel_date = datetime.date(2026, 11, 4)
assert "2026/05/21" in C["c27"]["url"]
assert "November 4, 2026" in C["c4"]["quote"]
days_between = (rel_date - rrc_date).days
ai_tools = ["artificial lift monitoring system", "large language models"]
assert "AI-powered artificial lift monitoring system" in C["c1"]["quote"] and "large language models" in C["c2"]["quote"]
llm_uses = ["development strategy", "wellbore placement", "drilling parameters"]
for s in llm_uses: assert s in C["c2"]["quote"], s
assert tx_pct + nm_pct == 100
F = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were.",
 "boe_per_day": {"value": boe, "from": ["c6"], "basis": "third quarter total production, barrels of oil equivalent per day"},
 "qoq_pct": {"value": qoq, "from": ["c6"], "basis": "increase on the prior quarter, percent"},
 "oil_per_day": {"value": oil, "from": ["c7"], "basis": "third quarter average daily crude oil, barrels"},
 "oil_share_pct": {"value": oil_share_pct, "from": ["c6", "c7"], "basis": "computed: crude oil barrels over total barrels of oil equivalent, percent, rounded to one decimal"},
 "fastest_ft_per_day": {"value": ftday, "from": ["c8"], "basis": "the company's fastest well, over this many feet a day"},
 "hours_per_day": {"value": HOURS, "from": ["c8"], "basis": "computed: the hours in the day c8's feet per day is spread over, the divisor of fastest_ft_per_hour"},
 "fastest_ft_per_hour": {"value": ft_per_hour, "from": ["c8"], "basis": "computed: the 2,700 feet a day over 24 hours, rounded to one decimal"},
 "capex_musd": {"value": capex, "from": ["c9"], "basis": "third quarter cash capital expenditures, millions of dollars"},
 "net_acres": {"value": acres, "from": ["c10"], "basis": "approximately this many net acres, West Texas and Southeast New Mexico"},
 "oil_target_2026": {"value": oil26, "from": ["c12"], "basis": "2026 oil production target, MBbls/d, midpoint"},
 "oil_4q_over": {"value": oil4q, "from": ["c13"], "basis": "expected fourth quarter oil production, over this many MBbls/d"},
 "texas_lease_pct": {"value": tx_pct, "from": ["c15"], "basis": "share of net leasehold acreage in Texas at year end 2025"},
 "nm_lease_pct": {"value": nm_pct, "from": ["c15"], "basis": "share of net leasehold acreage in New Mexico at year end 2025"},
 "lease_acres_2025": {"value": lease25, "from": ["c16"], "basis": "net leasehold acres at December 31st, 2025"},
 "ai_tools": {"value": len(ai_tools), "from": ["c1", "c2"], "basis": "computed: the AI tools the release names (the artificial lift monitor and the language models)"},
 "llm_uses": {"value": len(llm_uses), "from": ["c2"], "basis": "computed: the uses the release names for the language models"},
 "days_since_rrc": {"value": days_between, "from": ["c27", "c4"], "basis": "computed: days from the Tribune's May 21st, 2026 report to the November 4th, 2026 release"},
 "xom_technologies": {"value": xom_techs, "from": ["c25"], "basis": "more than this many technologies ExxonMobil is deploying in the Permian"},
 "xom_automate_year": {"value": xom_year, "from": ["c20"], "basis": "the year end by which ExxonMobil plans to automate more than half its unconventional fleet"},
 "xom_target_mboe": {"value": xom_target, "from": ["c26"], "basis": "ExxonMobil's Permian target, million oil-equivalent barrels a day"},
 "xom_target_year": {"value": xom_target_year, "from": ["c26"], "basis": "the year of ExxonMobil's Permian target"},
}
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print(json.dumps({k: v["value"] for k, v in F.items() if k != "_note"}))
