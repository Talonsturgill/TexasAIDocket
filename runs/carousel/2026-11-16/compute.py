#!/usr/bin/env python3
"""Figures for carousel no. 79, UT San Antonio and VA pilot reading veterans' speech with natural language
processing (tx-2026-0249).

Every value is read out of a claim quote by a pattern, or counted here from a list a quote carries.

RULES, stated so they are choices rather than accidents:
- the grant (c2) is as the grantee's newsroom states it. No per month or per year figure is derived from it
- the study is one year long (c3). No end date is computed, because no start date is stated
- features (c8) counts the four named features the team plans to assess. The quote says "such as", so the
  count is of the features NAMED, never a total of what the study measures. Every frame says named
- symptoms (c11) counts the symptoms named after "such as", under the same rule
- recording_prompts (c6) counts the two things veterans described in the recordings
- tests_built_for counts the two conditions c18 says most adult language tests were built for
- leads counts the three researchers the grant sentence (c2) names
- no accuracy, sample size or result is in any claim, so none is drawn or printed
"""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
def q(cid): return C[cid]["quote"]
def num(cid, pat):
    m = re.search(pat, q(cid)); assert m, (cid, pat)
    return int(m.group(1).replace(",", ""))

grant_usd = num("c2", r"received a \$([\d,]+) collaborative grant")
assert "one-year" in q("c3"); study_years = 1
norman_years = num("c5", r"veterans for (\d+) years")
feat = re.search(r"such as (.*?)\.$", q("c8")).group(1)
features = [f.strip() for f in re.split(r", | and ", feat) if f.strip()]
assert features == ["coherence", "emotional tone", "organization", "level of detail"], features
sym = re.search(r"such as (.*?)\.$", q("c11")).group(1)
symptoms = [s.strip() for s in re.split(r", | and ", sym) if s.strip()]
assert len(symptoms) == 4, symptoms
prompts = ["how they were injured", "an important life event"]
assert all(p in q("c6") for p in ("described how they were injured", "recounted an important life event"))
tests_for = ["aphasia following a stroke", "severe brain injury"]
assert "aphasia" in q("c18") and "following a stroke or individuals with severe brain injury" in q("c18")
leads = re.findall(r"(\w+ [\w-]+), PhD", q("c2"))
assert len(leads) == 3, leads

F = {
 "_note": "Every value is extracted from a claim quote by compute.py, or counted here from a list a quote carries.",
 "grant_usd": {"value": grant_usd, "from": ["c2"], "basis": "grant from the San Antonio Medical Foundation, as UT Health San Antonio states it"},
 "study_years": {"value": study_years, "from": ["c3"], "basis": "the pilot is a one year proof of concept study"},
 "norman_years": {"value": norman_years, "from": ["c5"], "basis": "years Rocio Norman has worked with veterans"},
 "features_named": {"value": len(features), "from": ["c8"], "basis": "features the team names that it plans to assess: " + ", ".join(features)},
 "symptoms_named": {"value": len(symptoms), "from": ["c11"], "basis": "symptoms named that the differences will be compared with"},
 "recording_prompts": {"value": len(prompts), "from": ["c6"], "basis": "what veterans described in the recordings: how they were injured, an important life event"},
 "tests_built_for": {"value": len(tests_for), "from": ["c18"], "basis": "the conditions most adult language assessments were developed for, per Norman: aphasia after a stroke, severe brain injury"},
 "leads": {"value": len(leads), "from": ["c2", "c4"], "basis": "researchers named on the grant"},
}
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
json.dump({k: v["value"] for k, v in F.items() if not k.startswith("_")}, open(HERE / "computed.json", "w"), indent=1)
print(json.dumps({k: v["value"] for k, v in F.items() if not k.startswith("_")}))
