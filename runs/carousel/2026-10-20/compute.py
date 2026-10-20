"""Every figure the October 20th deck states or draws, extracted from a claim quote or computed here.

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

F("rooms", int(grab("c2", r"in a (\d+)-room cardiothoracic suite")), ["c2"], "operating rooms in Walter Tower's cardiothoracic suite")
F("cameras_per_room", {"four": 4}[grab("c3", r"outfitted with (\w+) high-resolution")], ["c3"], "wall mounted cameras in each operating room, the quote's 'four'")
F("deploy_year", int(grab("c4", r"in December (\d{4})")), ["c4"], "year the software was deployed at Walter Tower, December")
F("window_months", int(grab("c5", r"Over a (\d+)-month period")), ["c5"], "months in the study window")
F("pre_months", int(grab("c5", r"spanning (\d+) months pre-deployment")), ["c5"], "months before deployment")
F("post_months", int(grab("c5", r"and (\d+) months post-deployment")), ["c5"], "months after deployment")
F("window_cases", int(grab("c5", r"monitored (\d+) surgical cases")), ["c5"], "surgical cases at the suite over the window")
F("added_cases", int(grab("c6", r"approximately (\d+) cases per month")), ["c6"], "estimated additional cases a month, approximately")
F("ci_low", float(grab("c6", r"95% CI ([\d.]+) to")), ["c6"], "lower end of the 95 percent interval, cases a month")
F("ci_high", float(grab("c6", r"to ([\d.]+);")), ["c6"], "upper end of the 95 percent interval, cases a month")
F("rise_pct", int(grab("c6", r"corresponding to a (\d+)% increase")), ["c6"], "percent increase in monthly case volume relative to baseline")
F("baseline_cases", int(grab("c7", r"approximately (\d+) cases per month")), ["c7"], "baseline cases a month, approximately")
F("perm_units", int(grab("c8", r"among the (\d+) units")), ["c8"], "units in the placebo permutation test, Walter Tower and its donor sites")
F("donor_sites", int(grab("c8", r"Walter Tower and (\d+) donor sites")), ["c8"], "donor sites in the permutation test")
F("perm_p", float(grab("c8", r"empirical p = ([\d.]+)")), ["c8"], "empirical p of the permutation test")
F("perm_rank", {"second": 2}[grab("c8", r"had the (\w+)-largest ratio")], ["c8"], "Walter Tower's rank among the units, the quote's 'second'")
F("video_days", int(grab("c17", r"maximum of (\d+) days and audio")), ["c17"], "days video is retained at most, per the paper")
F("audio_days", int(grab("c17", r"audio for a maximum of (\d+) days")), ["c17"], "days audio is retained at most, per the paper")
F("access_roles", {"three": 3}[grab("c18", r"restricted to (\w+) designated roles")], ["c18"], "roles that may open an intraoperative recording, the quote's 'three'")
F("train_cases", num(grab("c20", r"comprising ([\d,]+) surgical cases")), ["c20"], "surgical cases in the training data")
F("train_rooms", int(grab("c20", r"across (\d+) operating rooms")), ["c20"], "operating rooms in the training data")
F("published_day", int(grab("c1", r"2026 Jun (\d+);")), ["c1"], "day of June 2026 the study was published")
F("post_end_year", int(grab("c27", r"through September (\d{4})")), ["c27"], "year the post deployment period ended, September")
# computed
F("cameras_total", figures["rooms"]["value"] * figures["cameras_per_room"]["value"], ["c2", "c3"], "cameras across the suite, 15 rooms times 4")
F("with_added", figures["baseline_cases"]["value"] + figures["added_cases"]["value"], ["c6", "c7"], "baseline plus the estimate, approximately; drawn, never printed")
F("ci_low_whole", int(figures["ci_low"]["value"]), ["c6"], "the interval's low end floored to a whole case for drawing, 8.3 to 8")
F("ci_high_whole", int(figures["ci_high"]["value"]), ["c6"], "the interval's high end floored to a whole case for drawing, 41.0 to 41")
F("years_to_publish", 2026 - figures["post_end_year"]["value"], ["c1", "c27"], "years from the end of the study window, September 2023, to publication in June 2026")

(HERE / "figures.json").write_text(json.dumps(figures, indent=1) + "\n")
for k, v in figures.items():
    if k != "_note":
        print(f"{k:20} {v['value']}")
