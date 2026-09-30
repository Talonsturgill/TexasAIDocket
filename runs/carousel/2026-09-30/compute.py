#!/usr/bin/env python3
"""compute.py for the 2026-09-30 deck. Every figure is extracted from a claim's own quote in
claims.json by a pattern that must match, or the build stops. Nothing is typed. A derived figure
names the rule that made it."""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}


def num(cid, pattern):
    q = C[cid]["quote"]
    m = re.search(pattern, q)
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in quote")
    g = m.group(1).lower()
    if g in WORDS:
        return WORDS[g]
    g = g.replace(",", "").replace("$", "")
    return float(g) if "." in g else int(g)


F = {"_note": "Every value is extracted from a claim quote by compute.py, or derived from extracted values by a rule stated beside it."}


def put(k, v, cids, basis=None, **kw):
    F[k] = {"value": v, "from": cids}
    if basis:
        F[k]["basis"] = basis
    F[k].update(kw)


put("human_share_min_pct", num("c1", r"at least (\d+) percent"), ["c1"], "share of written responses routed to human scorers, at least")
put("engine_record_pct", num("c13", r"Approx\. (\d+)%"), ["c13"], "approximate share of responses whose score of record the engine assigns")
put("spanish_human_pct", num("c2", r"are (\d+) percent human"), ["c2"], "share of Spanish-language written responses scored by people")
put("training_sample", num("c16", r"~([\d,]+) human scored"), ["c16"], "human scored field test responses the engine is programmed on, per item")
put("cost_low_m", num("c14", r"\$(\d+)-\d+M"), ["c14"], "low end of the yearly cost of full human scoring, millions of dollars")
put("cost_high_m", num("c14", r"\$\d+-(\d+)M"), ["c14"], "high end, millions of dollars")
put("redesign_x_low", num("c15", r"With (\d+)-\d+x"), ["c15"])
put("redesign_x_high", num("c15", r"With \d+-(\d+)x"), ["c15"])
put("hybrid_start_year", num("c17", r"December (\d{4})"), ["c17"])
put("scorer_exact_pct", num("c18", r"at (\d+)% exact"), ["c18"])
put("scorer_adjacent_pct", num("c18", r"and (\d+)% adjacent"), ["c18"])
put("students_credited", num("c19", r"about ([\d,]+) students"), ["c19"], "students who received additional credit in the annual review")
put("improved_pct", num("c24", r"About ([\d.]+)%"), ["c24"], "share of exams reviewed whose scores improved")
put("exams_reviewed_m", num("c24", r"more than ([\d.]+) million"), ["c24"], "exams reviewed, millions, a floor")
put("campuses_up", num("c25", r"^(\w+) campuses"), ["c25"])
put("districts_up", num("c25", r"campuses and (\w+) districts"), ["c25"])
names = re.search(r"consist of (.+) ISDs", C["c26"]["quote"]).group(1)
dl = [s.strip() for s in re.split(r",\s*|\s+and\s+", names) if s.strip()]
put("districts_affected", len(dl), ["c26"], "districts the agency named as affected, counted from the list in the quote", names=dl)

# DERIVED, with the rule beside each.
# The per-hundred split: of every 100 responses, the engine's score stands on engine_record_pct and
# people score at least human_share_min_pct. The two are the agency's own shares and sum to 100.
assert F["engine_record_pct"]["value"] + F["human_share_min_pct"]["value"] == 100, "the two shares no longer sum to 100"
put("per100_engine", F["engine_record_pct"]["value"], ["c13"], "of every 100 responses, rule: engine_record_pct")
put("per100_people", F["human_share_min_pct"]["value"], ["c1"], "of every 100 responses, rule: human_share_min_pct")
put("per4_engine", F["engine_record_pct"]["value"] * 4 // 100, ["c13"], "of every 4 responses, rule: engine_record_pct x 4 / 100")
put("per4_people", F["human_share_min_pct"]["value"] * 4 // 100, ["c1"], "of every 4 responses, rule: human_share_min_pct x 4 / 100")
put("per1000_improved", round(F["improved_pct"]["value"] * 1000 / 100), ["c24"], "of every 1,000 exams reviewed, rule: round(improved_pct x 1000 / 100)")
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print(json.dumps({k: v["value"] for k, v in F.items() if k != "_note"}))
