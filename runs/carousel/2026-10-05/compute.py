#!/usr/bin/env python3
"""compute.py for the 2026-10-05 deck. Every figure is extracted from a claim's own quote in
claims.json by a pattern that must match, or the build stops. Number words are read through one
stated table. Nothing is typed. A derived figure names the rule that made it."""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
WORDS = {"three": 3, "six": 6, "seven": 7, "eleven": 11}


def num(cid, pattern, flags=0):
    q = C[cid]["quote"]
    m = re.search(pattern, q, flags)
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in quote")
    g = m.group(1)
    if g.lower() in WORDS:
        return WORDS[g.lower()]
    g = g.replace(",", "")
    return float(g) if "." in g else int(g)


F = {"_note": "Every value is extracted from a claim quote by compute.py, or derived from extracted values by a rule stated beside it."}


def put(k, v, cids, basis=None, **kw):
    F[k] = {"value": v, "from": cids}
    if basis:
        F[k]["basis"] = basis
    F[k].update(kw)


put("pilots", num("c6", r"funding for (\d+) pilot projects"), ["c6"], "pilot projects UT REAL Health AI announced funding for")
put("submissions", num("c7", r"review of (\d+) systemwide submissions"), ["c7"], "systemwide submissions the pilots were chosen from")
put("award_total_millions", num("c8", r"more than \$([\d.]+) million"), ["c8"], "award total in millions of dollars, more than")
put("institutions", num("c8", r"across (\w+) UT institutions"), ["c8"], "UT institutions the awards span, as the page counts them")
put("moonshots", num("c9", r"^(\w+) moonshot projects"), ["c9"], "moonshot projects")
put("moonshot_cap", num("c9", r"up to \$([\d,]+)"), ["c9"], "dollars each moonshot project received, up to")
put("hospital_sites", num("c47", r"across (\w+) UT hospital sites"), ["c47"], "UT hospital sites the emergency triage assistant runs across")
put("trauma_cases", num("c47", r"more than ([\d,]+) trauma cases"), ["c47"], "trauma cases the assistant was trained on, more than")
put("fetal_accuracy_pct", num("c48", r"with (\d+)% accuracy"), ["c48"], "the accuracy the page gives the fetal movement app, percent")
put("noshow_appointments", num("c22", r"more than ([\d,]+) appointments"), ["c22"], "appointments the no-show project says it saved at UTHealth Houston, more than")
put("noshow_revenue", num("c22", r"\$([\d,]+) in revenue"), ["c22"], "revenue in dollars the no-show project says it saved at UTHealth Houston")
put("san_antonio_low", num("c23", r"recover ([\d,]+)"), ["c23"], "appointments a year the page projects at UT Health San Antonio, the low end")
put("notes_records_millions", num("c17", r"more than (\d+) million patient records"), ["c17"], "patient records in millions the suicide risk pilot will read, more than")
put("prescreen_patients", num("c19", r"nearly ([\d,]+) patients"), ["c19"], "patients the trial prescreening platform was validated on, nearly")
put("sim_encounters", num("c20", r"more than ([\d,]+) simulation encounters"), ["c20"], "simulation encounters the grading platform has supported, more than")
put("epic_tools", num("c51", r"implements (\w+) Epic-integrated"), ["c51"], "Epic tools the Dell Medical School pilot implements")
put("submissions_per_pilot", F["submissions"]["value"] // F["pilots"]["value"], ["c6", "c7"],
    "submissions for every pilot funded", rule="submissions // pilots, exact because 120 divides by 12",
    exact=F["submissions"]["value"] % F["pilots"]["value"] == 0)
assert F["submissions_per_pilot"]["exact"]
put("unfunded_submissions", F["submissions"]["value"] - F["pilots"]["value"], ["c6", "c7"],
    "submissions that were not among the funded pilots", rule="submissions - pilots")
put("pilots_without_savings_figure", F["pilots"]["value"] - 1, ["c6", "c22"],
    "funded pilots for which the page states no saved count: every pilot but the no-show project, the one whose entry states what it saved",
    rule="pilots - 1, the one being c22")
put("noshow_san_antonio_ratio_floor", round(F["san_antonio_low"]["value"] / F["noshow_appointments"]["value"], 1), ["c22", "c23"],
    "how many times the San Antonio projection's low end is the Houston count, to one decimal", rule="san_antonio_low / noshow_appointments, rounded half up to one decimal")

UNITS = (100, 250, 500, 1000)
both = (F["noshow_appointments"]["value"], F["san_antonio_low"]["value"])
seat = max(u for u in UNITS if all(v % u == 0 for v in both))
put("seat_unit", seat, ["c22", "c23"], "appointments one drawn seat stands for on the waiting room frame",
    rule="the largest of 100, 250, 500 and 1000 that divides both noshow_appointments and san_antonio_low exactly")
put("noshow_seats", both[0] // seat, ["c22"], "occupied seats drawn for the project's own Houston count", rule="noshow_appointments // seat_unit")
put("sa_seats", both[1] // seat, ["c23"], "empty seats drawn for San Antonio's projected low end", rule="san_antonio_low // seat_unit")
put("bays_per_floor", F["submissions"]["value"] // 10, ["c7"], "lit bays drawn on each of the hospital's ten floors, one bay per submission",
    rule="submissions // 10, the kit hospital's floor count, exact")
assert F["submissions"]["value"] % 10 == 0
put("pilots_with_savings_figure", F["pilots"]["value"] - F["pilots_without_savings_figure"]["value"], ["c6", "c22"],
    "funded pilots whose entry states what it saved", rule="pilots - pilots_without_savings_figure")

(HERE / "figures.json").write_text(json.dumps(F, indent=1) + "\n")
for k, v in F.items():
    if k != "_note":
        print(f"{k:32} {v['value']}")
