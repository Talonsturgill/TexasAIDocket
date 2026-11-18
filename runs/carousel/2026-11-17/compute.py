#!/usr/bin/env python3
"""Figures for the November 17th, 2026 carousel, the STAAR automated scoring engine and the rescore
surge (tx-2026-0194).

Every value is read out of a claim quote by a pattern, or computed here from values so read.

RULES, stated so they are choices rather than accidents:
- request counts (c1, c2, c3) are as the Texas Tribune reports them. The 2025 count is "last year" in a
  story dated October 7th, 2026, so it is the 2025 spring
- growth_2024_to_2026 is requests_2026 / requests_2024, rounded DOWN to a whole number, so "more than N
  times" is always true
- raised_share_floor is scores_raised_min / requests_2026. scores_raised is "more than 13,300", so the
  share is a floor. one_in is the whole number n with 1/n at or under that floor, so "at least one in n"
  is true. The Tribune's own wording ties the 13,300 to "the reviews" of that spring's requests
- dallas_higher_of_100 is the 34% Dallas ISD reports, drawn as 34 of 100 and labelled as such
- the 25 percent human share (c13, c22) is TEA's design as of December 2023 and March 2024 documents,
  never claimed for 2026
- the 27,200 students (c24) are a separate TEA review of text entry answers, never set beside the
  rescore requests
"""
import json, re, math
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
def q(cid): return C[cid]["quote"]
def num(cid, pat):
    m = re.search(pat, q(cid)); assert m, (cid, pat)
    return int(m.group(1).replace(",", ""))

r24 = num("c1", r"had ([\d,]+) requests")
r25 = num("c2", r"Then, ([\d,]+) requests")
r26 = num("c3", r"jumped to ([\d,]+)")
raised = num("c4", r"more than ([\d,]+) reading scores")
fee = num("c6", r"pay \$(\d+) per test")
dallas_tests = num("c8", r"more than ([\d,]+) reading tests")
dallas_pct = num("c8", r"and (\d+)% returned")
human_pct = num("c13", r"at least (\d+) percent")
train = num("c20", r"~([\d,]+) human scored")
cost_lo, cost_hi = [int(x) for x in re.search(r"\$(\d+)-(\d+)M more per year", q("c18")).groups()]
assert (cost_lo, cost_hi) == tuple(int(x) for x in re.search(r"\$(\d+) million to \$(\d+) million", q("c10")).groups())
scorers_lo, scorers_hi = 4, 5
assert "four to five times" in q("c11")
resp_lo, resp_hi = [int(x) for x in re.search(r"(\d+)-(\d+)x more", q("c19")).groups()]
assert "December 2023" in q("c9") and "December 2023" in q("c21")

growth = r26 // r24
human_one_in = 100 // human_pct
assert human_one_in * human_pct == 100
changed_pct_max = float(re.search(r"less than (\.\d+)%", q("c5")).group(1))
changed_one_in = round(100 / changed_pct_max)
assert abs(changed_one_in * changed_pct_max - 100) < 1e-9
F = {
 "_note": "Every value is extracted from a claim quote by compute.py, or computed here from values so extracted.",
 "requests_2024": {"value": r24, "from": ["c1"], "basis": "spring 2024 requests to regrade open-ended reading answers"},
 "requests_2025": {"value": r25, "from": ["c2"], "basis": "the year before spring 2026"},
 "requests_2026": {"value": r26, "from": ["c3"], "basis": "spring 2026 requests"},
 "growth_2024_to_2026": {"value": growth, "from": ["c1", "c3"], "basis": "requests_2026 // requests_2024, rounded down so 'more than N times' holds"},
 "scores_raised_min": {"value": raised, "from": ["c4"], "basis": "reading scores the state raised after the reviews, a floor"},
 "human_one_in": {"value": human_one_in, "from": ["c13", "c22"], "basis": "100 / human_pct_min, so at least one in this many answers also goes to people, TEA's design as of Dec 2023 and Mar 2024"},
 "changed_pct_max": {"value": changed_pct_max, "from": ["c5"], "basis": "fewer than this percent of all open-ended reading responses changed, a ceiling; printed in words as fewer than half of one percent"},
 "changed_one_in": {"value": changed_one_in, "from": ["c5"], "basis": "100 / changed_pct_max: fewer than one in this many open-ended reading responses changed, a ceiling; drawn on slide 7 as one gilded page among this many and printed on slide 7 as the single gilded page in 200"},
 "fee_usd": {"value": fee, "from": ["c6"], "basis": "per test, charged when the score does not change"},
 "dallas_tests_min": {"value": dallas_tests, "from": ["c8"], "basis": "Dallas ISD reading tests sent for rescoring, a floor"},
 "dallas_higher_pct": {"value": dallas_pct, "from": ["c8"], "basis": "share of Dallas ISD's that came back higher"},
 "human_pct_min": {"value": human_pct, "from": ["c13", "c22"], "basis": "share of answers also routed to people, TEA's design as of Dec 2023 and Mar 2024"},
 "training_responses": {"value": train, "from": ["c20"], "basis": "about this many human scored field test responses program the engine per question"},
 "hand_cost_low_musd": {"value": cost_lo, "from": ["c18"], "basis": "extra cost per year of scoring by hand, low end"},
 "hand_cost_high_musd": {"value": cost_hi, "from": ["c18"], "basis": "high end"},
 "scorers_multiple_low": {"value": scorers_lo, "from": ["c11"], "basis": "four to five times as many human scorers"},
 "scorers_multiple_high": {"value": scorers_hi, "from": ["c11"], "basis": "high end"},
 "responses_multiple_low": {"value": resp_lo, "from": ["c19"], "basis": "6-7x more constructed responses to grade each year"},
 "responses_multiple_high": {"value": resp_hi, "from": ["c19"], "basis": "high end"},
}
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
json.dump({k: v["value"] for k, v in F.items() if not k.startswith("_")}, open(HERE / "computed.json", "w"), indent=1)
print(json.dumps({k: v["value"] for k, v in F.items() if not k.startswith("_")}))
