#!/usr/bin/env python3
"""Figures for carousel no. 78, Texas 2036's November 10th, 2026 preview of its report on AI in Texas schools
(tx-2026-0248).

Every value is read out of a claim quote by a pattern, or computed here from values that were.

RULES, stated so they are choices rather than accidents:
- the survey shares (c2, c3, c4) are what Texas school and district leaders REPORTED to a fall 2025 survey, as Texas
  2036 reports it. They are never a measured share of classrooms, teachers or students, and they answer different
  questions, so no difference, ratio or sum between them is computed or drawn
- the voter share "nearly 85%" (c13) is approximate and is drawn as a floor-free approximate figure, never exact
- states_with_guidance (c5) is Texas 2036's own count. No total of states is typed anywhere, because no claim gives one
- DRAWING UNIT. One desk, seat or chip stands for one leader in a hundred (per_hundred). teacher_use_of_100 and the
  others are the reported percentages at that unit, exact because each source share is a whole percent
"""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
def q(cid): return C[cid]["quote"]
def num(cid, pat, i=1):
    m = re.search(pat, q(cid)); assert m, (cid, pat)
    v = float(m.group(i)); return int(v) if v.is_integer() else v

teacher_use_pct = num("c2", r"(\d+)% of Texas school and district leaders reported that teachers")
student_use_pct = num("c2", r"while (\d+)% reported student use")
student_policy_pct = num("c3", r"Only (\d+)%")
staff_policy_pct = num("c4", r"Just (\d+)%")
states_with_guidance = num("c5", r"analysis, (\d+) states")
voter_privacy_pct = num("c13", r"Nearly (\d+)%")
voter_literacy_pct = num("c15", r"^(\d+)%")
survey_year = num("c2", r"In fall (\d{4})")
prio_ids = ["c7", "c8", "c9", "c10"]  # the priorities the article lists, one claim each
priorities = len(prio_ids)
assert "November 10, 2026" in q("c1")
assert q("c6") == "Texas is not among them."
per_hundred = 100
for v in (teacher_use_pct, student_use_pct, student_policy_pct, staff_policy_pct): assert 0 < v < per_hundred

F = {
 "_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were.",
 "teacher_use_pct": {"value": teacher_use_pct, "from": ["c2"], "basis": "share of Texas school and district leaders who reported teachers using AI, fall 2025, per Texas 2036"},
 "student_use_pct": {"value": student_use_pct, "from": ["c2"], "basis": "share who reported student use"},
 "student_policy_pct": {"value": student_policy_pct, "from": ["c3"], "basis": "share who reported a district policy governing student AI use"},
 "staff_policy_pct": {"value": staff_policy_pct, "from": ["c4"], "basis": "share who reported a policy for teachers and staff"},
 "states_with_guidance": {"value": states_with_guidance, "from": ["c5"], "basis": "states with some form of statewide AI guidance for schools, Texas 2036's count; Texas is not among them (c6)"},
 "voter_privacy_pct": {"value": voter_privacy_pct, "from": ["c13"], "basis": "nearly this share of Texas voters, approximate, never exact"},
 "voter_literacy_pct": {"value": voter_literacy_pct, "from": ["c15"], "basis": "share of Texas voters who say teaching responsible AI use is important"},
 "survey_year": {"value": survey_year, "from": ["c2"], "basis": "the survey was taken in the fall of this year"},
 "priorities": {"value": priorities, "from": prio_ids, "basis": "the four priorities the report names"},
 "per_hundred": {"value": per_hundred, "from": [], "basis": "DRAWING UNIT: one desk, seat or chip per leader in a hundred"},
 "teacher_use_of_100": {"value": teacher_use_pct, "from": ["c2"], "basis": "units lit for teacher use at the drawing unit"},
 "student_use_of_100": {"value": student_use_pct, "from": ["c2"], "basis": "units lit for student use at the drawing unit"},
 "student_policy_of_100": {"value": student_policy_pct, "from": ["c3"], "basis": "units carrying a written student policy at the drawing unit"},
 "staff_policy_of_100": {"value": staff_policy_pct, "from": ["c4"], "basis": "units carrying a written staff policy at the drawing unit"},
}
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
json.dump({k: v["value"] for k, v in F.items() if not k.startswith("_")}, open(HERE / "computed.json", "w"), indent=1)
print(json.dumps({k: v["value"] for k, v in F.items() if not k.startswith("_")}))
