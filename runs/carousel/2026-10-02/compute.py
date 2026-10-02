#!/usr/bin/env python3
"""compute.py for the 2026-10-02 deck. Every figure is extracted from a claim's own quote in
claims.json by a pattern that must match, or the build stops. Number words are read through one
stated table. Nothing is typed. A derived figure names the rule that made it."""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
WORDS = {"two": 2, "three": 3, "seven": 7, "nine": 9}


def num(cid, pattern, flags=0):
    q = C[cid]["quote"]
    m = re.search(pattern, q, flags)
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in quote")
    g = m.group(1)
    if g.lower() in WORDS:
        return WORDS[g.lower()]
    g = g.replace(",", "").replace("$", "")
    return float(g) if "." in g else int(g)


F = {"_note": "Every value is extracted from a claim quote by compute.py, or derived from extracted values by a rule stated beside it."}


def put(k, v, cids, basis=None, **kw):
    F[k] = {"value": v, "from": cids}
    if basis:
        F[k]["basis"] = basis
    F[k].update(kw)


put("affected_individuals", num("c10", r"studied (\d+) affected"), ["c10"], "affected individuals the study covered")
put("families", num("c10", r"from (\w+) unrelated families"), ["c10"], "unrelated families those individuals came from")
put("seizures", num("c13", r"^(\w+) individuals experienced seizures"), ["c13"], "affected individuals who experienced seizures")
put("genematcher_individuals", num("c28", r"found (\w+) individuals"), ["c28"], "individuals the paper says were found through GeneMatcher after the first")
put("variants_modeled", num("c29", r"model (\w+) missense"), ["c29"], "patient missense variants modeled in fruit flies")
put("training_variants_m", num("c33", r"over ([\d.]+) million variants"), ["c33"], "millions of variants AI-MARRVEL's classifier was trained on, over")
put("cohorts", num("c34", r"across (\w+) distinct"), ["c34"], "real-world cohorts in which AI-MARRVEL doubled the solved cases")
put("precision_pct", num("c35", r"precision rate of (\d+)%"), ["c35"], "precision of AI-MARRVEL's confidence metric, percent, NOT overall accuracy")
put("diagnosable_found_pct", num("c35", r"identified (\d+)% of diagnosable"), ["c35"], "percent of diagnosable cases the confidence metric identified")
put("metric_cases", num("c35", r"collection of (\d+) cases"), ["c35"], "cases in the collection the confidence metric was tested on")
put("texome_visits", num("c43", r"consists of (\d+) visits"), ["c43"], "study visits a Texome participant makes")
put("texome_years", num("c43", r"over a (\d+) year"), ["c43"], "years the Texome visits span")
put("gift_card_dollars", num("c41", r"\$(\d+) gift card"), ["c41"], "dollars of the gift card after all the visits")
put("texome_target_children", num("c46", r"~(\d+) children"), ["c46"], "children Texome plans to sequence, a target with a tilde, never a count served")
put("followup_months_first", num("c50", r"at (\d+) months"), ["c50"], "months to the first Texome re-evaluation")
put("solved_multiplier", 2, ["c34"], "the paper's word 'doubling', as a factor, drawn as two lengths at one scale and never printed as a numeral",
    rule="'doubling' in the quote, read as 2")
assert "doubling" in C["c34"]["quote"]
put("first_plus_matched", F["genematcher_individuals"]["value"] + 1, ["c27", "c28"],
    "the first Texome individual plus the nine found through GeneMatcher, computed only to assert it equals the release's 10, never printed",
    rule="genematcher_individuals + 1")
assert F["first_plus_matched"]["value"] == F["affected_individuals"]["value"]

out = HERE / "figures.json"
out.write_text(json.dumps(F, indent=1) + "\n")
print(f"figures: {len(F) - 1} written to {out}")
