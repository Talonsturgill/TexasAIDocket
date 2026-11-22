#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-21, carousel no. 84. Appends one entry to each variety ledger,
the artwork values measured off the final renders by deck_coherence and layout_check's own
functions, the caption's counts measured off caption.txt. Then ledger_check --derive rewrites the
caption exclusion lists."""
import json, re, sys, subprocess
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] if HERE.parent.name == "out" else HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts/carousel"))
import deck_coherence as DC, layout_check as LC
from PIL import Image
D, N = "2026-11-21", 84
OUT = ROOT / "out" / D
L = ROOT / "ledger/carousel"
def add(name, entry):
    p = L / f"{name}.json"; t = json.loads(p.read_text())
    t["entries"] = [e for e in t["entries"] if e.get("date") != D] + [entry]
    p.write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n")
frames = [OUT / "render" / f"slide-{i:02d}.png" for i in range(1, 10)]
med = [round(DC.median_lstar(f), 1) for f in frames]
d = [abs(a - b) for a, b in zip(med, med[1:])]
ACC = json.loads((OUT / "accent.json").read_text())["hex"]
acc = [round(LC.accent_coverage(Image.open(f).convert("RGB"), ACC), 4) for f in frames]
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0254", "related_items": ["tx-2026-0186"],
 "instrument": "DARPA's account of the Triage Challenge finals, DARPA's Triage Challenge program page and TEEX's account of staging the finals at Disaster City, fetched November 21st, 2026.",
 "topic": "TEEX staged the finals of DARPA's Triage Challenge at Disaster City in College Station from November 5th to November 13th, a 52 acre mock community with structures that can collapse, rubble piles and a derailed train. Autonomous drones and ground robots worked alongside first responders on simulated casualties and relayed critical data to human medics. RoboScout won the Systems competition and $1.5 million and Disruptors the Data competition and $1 million, out of more than $3 million. DARPA's director said human machine teams outperform every approach, then that it is not enough. TRIAGE-X is open until November 25th.",
 "angle": "The handoff. A lime link carries what the machine hands the medic. A tracked rover on rubble with a medic and tablet beyond, the whole staged town on a plot sized from 52 acres, model courses on studio risers, a section through rubble with a role player in a braced pocket, the night course lit by a controlled burst, credentials on a raked fence run, brass stacks at a shared scale, a kneeling medic taking the lime beam from the rover in a concrete room, and an open dose case with an empty pocket.",
 "angle_note": "Every frame is drawn to illustrate, to no team's design, and shows no real place layout. No surface calls the systems AI, because no source does. Every casualty is a simulated role player with no injury and no face. Lime means what the machine hands the medic only, never money, which is brass. More than figures are drawn to their floor and run off the frame.",
 "entities": ["DARPA", "TEEX", "Texas A&M Engineering Extension Service", "RoboScout", "Disruptors", "DRONE", "Stephen Winchell", "Jeremy Pamplin"],
 "places": ["Texas", "College Station", "Disaster City", "Brazos County"],
 "what_was_refused": "the word AI (no source uses it), any statement that no real patient was involved (no source says it), the runner up and component prizes (table cells only), the real Disaster City site plan, and any team's actual hardware.",
 "keywords": ["triage", "autonomous", "drones", "ground robots", "Disaster City", "TEEX", "DARPA", "medics", "TRIAGE-X"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "BESPOKE, LOOK V2 win tone, nine slide artists. Outdoor TXT.sky worlds (1, 2, 4, 7, 9), a night world built on the win shade (5), TXT.studio sweeps (3, 6), a TXT.interior concrete room (8). Spine assets/js/deck/2026-11-21-handoff-bespoke.js with chassis models triage_rover, rubble_pile, survey_quad and flight_board.",
 "structural_laws": [
  "K.CYL TAKES THE CYLINDER'S BOTTOM Y, NOT ITS CENTRE, so a chassis model placing wheels or a mast by centre floats every cylinder by half its height; the spine wraps it in a centre helper.",
  "A STRONGER TYPE SEAT IN THE TONE'S TEAL OVER A WARM OR VIOLET SKY TURNS IT SLATE OLIVE; seat in the sky's own hue and keep the fade tight.",
  "A BUTTER KEY AND THE WIN GRADE PUSH A DARK TEAL HULL TO EMERALD; blue shift the coat under a strong key so the hero reads one colour across frames.",
  "A LOW CAMERA UNDER A TYPE BAND MAKES RAILS AND TRIM STRIKE THE DEK; place the dek from the lowest projected rail."],
 "techniques": ["a tracked rover close and low on fractured concrete with a lime link to a medic's tablet", "a raked aerial of a staged town on a plot sized from 52 acres with a survey tape", "five model courses on teal studio risers", "an orthographic section through rubble with a braced pocket and a reading cone", "a night course lit by a controlled burst behind earth filled blast walls", "one hundred credentials on a raked temporary fence run in a studio", "three machined brass stacks at one scale beside the rover", "a kneeling kit medic with a cross patch taking the rover's lime beam on a tablet beside an empty litter", "an open hard case with one empty dose pocket on a pickup tailgate"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders."},
 "accent": {"hex": ACC, "name": "win lime", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "What the machine hands the medic only."},
 "ground": {"hex": "#d9c7a4", "note": "Sun bleached concrete, caliche and Brazos clay under the win tone's blue sky and teal shade."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
mv = json.loads((OUT / "caption_moves.json").read_text())
add("captions", {"date": D, "carousel_no": N, "opening_move": mv["opening_move"], "structure": mv["structure"],
 "closing_move": mv["closing_move"],
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": mv["critic_note"], "move_note": mv["move_note"]})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
