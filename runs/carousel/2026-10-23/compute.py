"""Every figure the October 23rd deck states or draws, extracted from a claim quote or computed here.

No figure in the deck is typed. Each value below is parsed out of the verified quote it cites in
claims.json, and figures.json is written from this file alone.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
claims = {c["id"]: c for c in json.loads((HERE / "claims.json").read_text())["claims"]}
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}


def quote(cid):
    return claims[cid]["quote"]


def grab(cid, pattern, group=1):
    m = re.search(pattern, quote(cid))
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in its quote")
    return m.group(group)


figures = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were."}
F = lambda k, v, src, basis: figures.__setitem__(k, {"value": v, "from": src, "basis": basis})

# the release's wording pair: 17 visits in the past 12 months (c19), the same line in the preprint's Table 1 (c35)
visits = int(grab("c19", r"(\d+) visits in the past (\d+) months"))
months = int(grab("c19", r"(\d+) visits in the past (\d+) months", 2))
if (visits, months) != (int(grab("c35", r"(\d+) visits")), int(grab("c35", r"past (\d+) months"))):
    raise SystemExit("c19 and c35 disagree on the frequent visitor line")
F("visits", visits, ["c19", "c35"], "ED visits in the stigmatizing line, release and preprint alike")
F("months", months, ["c19", "c35"], "the months those visits are counted over")

# the release's one result figure: nearly 10% wrongly downgraded in some instances (c15)
pct = int(grab("c15", r"nearly (\d+)%"))
F("downgraded_pct", pct, ["c15"], "nearly this percent of patients wrongly downgraded in some instances, the release's own about")
F("downgraded_of_100", pct, ["c15"], "the same share drawn as units out of 100")
F("per_hundred", 100, ["c15"], "a percent is a count per hundred, so the drawer holds this many cards")
F("downgraded_one_in", round(100 / pct), ["c15"], "computed: 100 over the percent, so one unit in this many is drawn moved")

# three open source models in the published study (c9, c13), two departments (c11)
m3 = WORDS[grab("c9", r"asked (\w+) open-source")]
if WORDS[grab("c13", r"all (\w+) models")] != m3:
    raise SystemExit("c9 and c13 disagree on the model count")
F("models", m3, ["c9", "c13"], "open source language models in the published study, per the release")
depts = len(re.findall(r"(Stanford Medicine|Beth Israel Deaconess Medical Center)", quote("c11")))
F("departments", depts, ["c11"], "computed: emergency departments the release names, counted")

# the preprint, a different version: two models (c30), the pairs (c33), the window (c32), the conditions (c34)
F("preprint_models", WORDS[grab("c30", r"(\w+) models were evaluated").lower()], ["c30"], "models in the May preprint")
p1, p2 = int(grab("c33", r"(\d+) pairs")), int(grab("c33", r"and (\d+) from"))
F("preprint_pairs_mimic", p1, ["c33"], "preprint pairs from MIMIC-IV-ED")
F("preprint_pairs_mcmed", p2, ["c33"], "preprint pairs from MC-MED")
F("preprint_pairs_total", p1 + p2, ["c33"], "computed: the two datasets' pairs summed")
F("hours", int(grab("c32", r"within (\d+) hours")), ["c32"], "the preprint's window for the four interventions")
F("conditions", int(grab("c34", r"tested (\d+) conditions")), ["c34"], "test conditions in the preprint")
F("psych_holds", int(grab("c36", r"(\d+) prior psychiatric")), ["c36"], "prior psychiatric emergency holds in the preprint's added line")
lo1, hi1 = float(grab("c39", r"psychiatric history \(([\d.]+)% to ([\d.]+)%")), float(grab("c39", r"psychiatric history \(([\d.]+)% to ([\d.]+)%", 2))
lo2, hi2 = float(grab("c39", r"frequent ED visitor status \(([\d.]+)% to ([\d.]+)%")), float(grab("c39", r"frequent ED visitor status \(([\d.]+)% to ([\d.]+)%", 2))
F("preprint_psych_range", [lo1, hi1], ["c39"], "preprint harmful reprioritization range, psychiatric history")
F("preprint_freq_range", [lo2, hi2], ["c39"], "preprint harmful reprioritization range, frequent ED visitor")

(HERE / "figures.json").write_text(json.dumps(figures, indent=1) + "\n")
print(json.dumps({k: v["value"] for k, v in figures.items() if k != "_note"}))
