#!/usr/bin/env python3
"""Figures for the November 20th, 2026 carousel, East Texas A&M's test of AI that flags a drone fed
false GPS from its own motion (tx-2026-0253).

Every value is read out of a claim quote by a regex, or computed here from values so read.

RULES, stated so they are choices rather than accidents:
- flights is c5's 96, normal c6's 42 and spoofed c6's 54. normal + spoofed must equal flights
- held_out is c8's 22 whole flights set aside for testing. trained is flights - held_out, the flights
  left for training, computed, and printed only if a frame needs it
- models is c9's eight, read from the word
- readings is c11's 10 consecutive readings
- score_pct is c11's 97.5, a score on one measure balancing caught abnormal stretches against correct
  alerts. It is never called accuracy and never drawn as a share of attacks caught
- grant_floor is c13's about $200,000, printed with "about", never drawn
- grant_years is c13's two-year, read from the word
- team_ug and team_grad are c23's two and two
"""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
C = {c["id"]: c for c in json.load(open(HERE / "claims.json"))["claims"]}
def q(cid): return C[cid]["quote"]
def rx(cid, pat):
    m = re.search(pat, q(cid)); assert m, (cid, pat); return m.group(1)
WORDS = {"two": 2, "eight": 8}
flights = int(rx("c5", r"from (\d+) actual drone flights"))
normal = int(rx("c6", r"(\d+) were normal"))
spoofed = int(rx("c6", r"and (\d+) were conducted under controlled spoofing"))
assert normal + spoofed == flights
held_out = int(rx("c8", r"set aside (\d+) entire flights"))
trained = flights - held_out
models = WORDS[rx("c9", r"compared (\w+) AI models")]
readings = int(rx("c11", r"Given (\d+) consecutive readings"))
score_pct = float(rx("c11", r"scored ([\d.]+)%"))
grant = int(rx("c13", r"about \$([\d,]+)").replace(",", ""))
grant_years = WORDS[rx("c13", r"a (\w+)-year National Science Foundation")]
team_ug = WORDS[rx("c23", r"includes (\w+) undergraduate")]
team_grad = WORDS[rx("c23", r"and (\w+) graduate research assistants")]
F = {
 "_note": "Every value is extracted from a claim quote by compute.py, or computed here from values so extracted.",
 "flights": {"value": flights, "from": ["c5"], "basis": "real drone flights in the public dataset"},
 "normal": {"value": normal, "from": ["c6"], "basis": "flights flown normally"},
 "spoofed": {"value": spoofed, "from": ["c6"], "basis": "flights flown under controlled spoofing attacks"},
 "held_out": {"value": held_out, "from": ["c8"], "basis": "whole flights set aside for testing, unseen in training"},
 "trained": {"value": trained, "from": ["c5", "c8"], "basis": "flights - held_out, the flights left for training"},
 "models": {"value": models, "from": ["c9"], "basis": "AI models compared"},
 "readings": {"value": readings, "from": ["c11"], "basis": "consecutive readings the best model was given"},
 "score_pct": {"value": score_pct, "from": ["c11"], "basis": "Chronos's score on one measure balancing caught abnormal stretches against correct alerts, never accuracy"},
 "grant_about": {"value": grant, "from": ["c13"], "basis": "about this many dollars of NSF funding, printed with about, never drawn"},
 "grant_years": {"value": grant_years, "from": ["c13"], "basis": "the grant's length in years"},
 "team_ug": {"value": team_ug, "from": ["c23"], "basis": "undergraduate research assistants on the team"},
 "team_grad": {"value": team_grad, "from": ["c23"], "basis": "graduate research assistants on the team"},
}
json.dump(F, open(HERE / "figures.json", "w"), indent=1)
print({k: v["value"] for k, v in F.items() if k != "_note"})
