#!/usr/bin/env python3
"""compute.py for the 2026-09-28 deck. Every figure is extracted from a claim's own quote in
claims.json by a pattern that must match, or the build stops. Nothing is typed. Figures from
different documents are never summed or subtracted against each other: 68 planned (the plan
application), 33 installed and 34 projected (the annual report) and 97 across the service
territory (the Tribune) are three scopes, and this file keeps them apart."""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}

def num(cid, pattern, key="quote"):
    q = C[cid].get(key) or ""
    m = re.search(pattern, q)
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in {key}")
    g = m.group(1).lower()
    if g in WORDS:
        return WORDS[g]
    g = g.replace(",", "").replace("$", "")
    return float(g) if "." in g else int(g)

F = {"_note": "Every value is extracted from a claim quote by compute.py. The four camera figures come from three documents with three scopes and are never combined."}
def put(k, v, cids, basis=None, **kw):
    F[k] = {"value": v, "from": cids}
    if basis: F[k]["basis"] = basis
    F[k].update(kw)

put("cameras_installed", num("c8", r"Actual: (\d+) cameras installed"), ["c8"], "the annual report's answer under the detections metric, a count of cameras")
put("cameras_projected_2026", num("c8", r"Projected: (\d+) for 2026"), ["c8"], "the same line's projection")
put("detections_reported", 0, ["c8"], "the number of detection counts the detections line reports: none. Drawn as an empty column, never printed as a count of fires", counted=True)
put("cameras_planned", num("c23", r"a total of (\d+) cameras"), ["c23"], "the plan application, Tier 2 and Tier 3")
put("cameras_per_site", num("c25", r"with (\w+) physical cameras"), ["c25"])
put("cameras_service_territory", num("c41", r"deployed (\d+) wildfire detection cameras"), ["c41"], "across the whole service territory, which includes New Mexico. Never a Texas count")
put("ignitions_overhead", num("c18", r"Actual: (\d+)"), ["c18"], "ignitions associated with overhead lines, reporting year")
put("ignitions_projected_2026", num("c18", r"Projected: (\d+) for 2026"), ["c18"])
put("nifc_wildfires", num("c20", r"Actual: (\d+)"), ["c20"], "wildfires the NIFC reported in counties SPS serves")
put("downed_tier1", num("c19", r"Tier 1: (\d+)"), ["c19"])
put("downed_tier2", num("c19", r"Tier 2: (\d+)"), ["c19"])
put("downed_tier3", num("c19", r"Tier 3: (\d+)"), ["c19"])
put("capex_2026", num("c15", r"anticipates (\$[\d,]+) of capital"), ["c15"])
put("capex_plan_2026", num("c15", r"compared to (\$[\d,]+) estimated"), ["c15"])
put("capex_change_pct", num("c15", r"resulting in a ([\d.]+)% change"), ["c15"], "the report's own figure")
calc = round((F["capex_2026"]["value"] - F["capex_plan_2026"]["value"]) / F["capex_plan_2026"]["value"] * 100, 2)
assert calc == F["capex_change_pct"]["value"], (calc, F["capex_change_pct"])
F["capex_change_pct"]["checked"] = "recomputed from the two costs to two places and equal"
put("capex_ratio_drawn", round(F["capex_2026"]["value"] / F["capex_plan_2026"]["value"], 4), ["c15"], "the actual over the plan, the length ratio two bars are drawn at", computed=True)
put("opex_2025", num("c14", r"was (\$[\d,]+) as compared"), ["c14"])
put("utilities_filed", num("c43", r"Only (\w+) of \d+ utility"), ["c43"])
put("utilities_total", num("c43", r"of (\d+) utility companies"), ["c43"])
put("utilities_dated", num("c45", r"^(\w+) more have given"), ["c45"])
put("utilities_preparing", num("c45", r"another (\d+) have indicated"), ["c45"])
put("utilities_silent", num("c45", r"leaves (\d+) who have not"), ["c45"])
s = sum(F[k]["value"] for k in ("utilities_filed", "utilities_dated", "utilities_preparing", "utilities_silent"))
assert s == F["utilities_total"]["value"], s
F["utilities_total"]["checked"] = "filed, dated, preparing and silent sum to the total"
put("utilities_not_filed", F["utilities_total"]["value"] - F["utilities_filed"]["value"], ["c43"], "total minus filed, same sentence, same scope", computed=True)
put("tier23_share_pct", num("c27", r"approximately (\d+) percent"), ["c27"])
put("service_counties", num("c29", r"and (\d+) counties"), ["c29"])
put("service_sq_mi", num("c29", r"approximately ([\d,]+) square miles"), ["c29"])
put("intervene_days", num("c5", r"is (\d+) calendar days"), ["c5"])
put("plan_investment_musd", num("c22", r"including \$([\d.]+) million"), ["c22"])
put("shutoffs_since_2024", num("c52", r"shut off power (\w+) times", key="second_quote"), ["c52"])
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print("figures:", len(F) - 1)
