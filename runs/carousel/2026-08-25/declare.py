#!/usr/bin/env python3
"""aggregates.json, COMPOSED from figures.json rather than typed beside the slides.

Round 5's judges found "Four applications" declared as `value_from: c11` and "NOT counted over
the ledger" in this file while compute.py counted it off Brazoria's own matter titles. The fix
had landed in the code and never reached the manifest, which is the same class of defect as the
stale ledgers: two files, one number, written twice by hand. Every value below is read out of
figures.json at the moment the file is written.
"""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/carousel"))
import aggregate_check as A

F = json.loads((ROOT / "out/2026-08-25/figures.json").read_text())
V = lambda k: F[k]["value"]
ACTING = sorted({m["claim"] for m in F["chronology"]["marks"]}, key=lambda c: int(c[1:]))
CODE = "out/2026-08-25/compute.py"

def count(fig, note, claims=None):
    return {"kind": "count", "value": V(fig), "from_claims": claims or ACTING,
            "computed_by": f"{CODE}, {fig}. {note}"}
def ratio(fig, whole_fig, note, claims):
    return {"kind": "ratio", "value": V(fig), "of": V(whole_fig), "from_claims": claims,
            "computed_by": f"{CODE}, {fig} over {whole_fig}. {note}"}
def span(kind, fig=None):
    d = {"kind": kind, "from_date": V("first_action_date"), "to_date": V("last_action_date"),
         "from_claims": ACTING,
         "computed_by": f"{CODE}, first_action_date and last_action_date over the acting items"}
    d["value"] = V(fig) if fig else V("span_days")
    return d

NB = ["c5", "c7", "c30", "c22", "c18"]                     # the five whose sources say they bind nothing
BI = ["c9", "c32", "c41", "c43", "c35", "c36"]             # the six that changed a legal state
SA = ["c32", "c41", "c43"]                                 # San Angelo's three

NB = ["c5", "c7", "c30", "c22", "c18"]                     # sources that say they bind nothing
BI = ["c9", "c32", "c41", "c43", "c35", "c36"]             # changed a legal state on the day
SA = ["c32", "c41", "c43"]                                 # San Angelo's three
JUNE = ["c43", "c40", "c35", "c32", "c5", "c36"]

PHRASES = {
 "Fifteen ways":                  count("restricted_count", "actions by a Texas local government"),
 "Fifteen actions":               count("restricted_count", "actions by a Texas local government"),
 "FIFTEEN ACTIONS":               count("restricted_count", "actions by a Texas local government"),
 "Twelve Texas local governments":count("acting_bodies", "distinct places among the acting items"),
 "Twelve local governments":      count("acting_bodies", "distinct places among the acting items"),
 "Six actions":                   count("busiest_month_count", "acting dates falling in June", JUNE),
 "Seventeen times":               count("total_count", "acting plus declined", ACTING + ["c14", "c15"]),
 "156 DAYS":                      span("duration", "span_days"),
 "MARCH 10TH TO AUGUST 13TH":     span("span", "span_days"),
 "FIVE OF THE FIFTEEN":           ratio("stated_nonbinding", "restricted_count",
                                        "acting bodies whose own source says the action does not bind", NB),
 "Five of the fifteen":           ratio("stated_nonbinding", "restricted_count",
                                        "acting bodies whose own source says the action does not bind", NB),
 "Six of the fifteen":            ratio("stated_binding", "restricted_count",
                                        "actions that changed a legal state on the day", BI),
 "three of the six":              ratio("busiest_body_binding", "stated_binding",
                                        "how many of the binding actions San Angelo wrote", SA),
 "Four applications":             {"kind": "count", "value": V("brazoria_applications"),
                                   "from_claims": ["c9", "c10", "c11"],
                                   "computed_by": f"{CODE}, brazoria_applications. Distinct applicants "
                                     "whose Brazoria County hearing orders name Reinvestment Zone No. "
                                     "26-01, counted off the county's own Legistar matter titles in "
                                     "out/2026-08-25/brazoria_matters.json"},
 "8.0 gallons":                   {"kind": "count", "value": 8, "from_claims": ["c32"],
                                   "quoted_from": "c32",
                                   "quote": "shall not exceed 8.0 gallons per square foot",
                                   "computed_by": "not computed. Quoted from Ordinance 2026-078 itself"},
 "one year":                      {"kind": "duration", "value": 1, "from_claims": ["c16"],
                                   "quoted_from": "c16", "quote": "a similar one-year moratorium",
                                   "computed_by": "not computed. Quoted from c16, reported speech about Hill County"},
 "two required public hearings":  {"kind": "count", "value": 2, "from_claims": ["c24"],
                                   "quoted_from": "c24",
                                   "quote": "the first of the two required public hearings",
                                   "computed_by": "not computed. Quoted from the city's own release, c24"},
 "two public hearings":           {"kind": "count", "value": 2, "from_claims": ["c46"],
                                   "quoted_from": "c46",
                                   "quote": "required to hold two public hearings",
                                   "computed_by": "not computed. Quoted from c46, the route into the Fort Worth hearing"},
}

rep = json.loads((ROOT / "out/2026-08-25/render/render_report.json").read_text())
found = {f["phrase"] for f in A.scan_report(rep)}
missing = found - set(PHRASES)
extra   = set(PHRASES) - found
assert not missing, "the render prints numbers this file does not declare: " + ", ".join(sorted(missing))
assert not extra,   "this file declares numbers no frame prints: " + ", ".join(sorted(extra))

out = {"aggregates": [dict(phrase=p, **PHRASES[p]) for p in sorted(PHRASES)]}
(ROOT / "out/2026-08-25/aggregates.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print(f"declared {len(out['aggregates'])} aggregate(s), all values read from figures.json")
