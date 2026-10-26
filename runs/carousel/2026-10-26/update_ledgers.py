#!/usr/bin/env python3
"""update_ledgers.py for 2026-10-26, carousel no. 61. Appends one entry to each variety ledger,
the artwork values measured off the final renders by deck_coherence and layout_check's own
functions, the caption's counts measured off caption.txt. Then ledger_check --derive rewrites the
caption exclusion lists."""
import json, re, sys, subprocess
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] if HERE.parent.name == "out" else HERE.parents[2]   # out/<date>/ or runs/carousel/<date>/
sys.path.insert(0, str(ROOT / "scripts/carousel"))
import deck_coherence as DC, layout_check as LC
from PIL import Image
D, N = "2026-10-26", 61
OUT = ROOT / "out" / D
L = ROOT / "ledger/carousel"
def add(name, entry):
    p = L / f"{name}.json"; t = json.loads(p.read_text())
    t["entries"] = [e for e in t["entries"] if e.get("date") != D] + [entry]
    p.write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n")
frames = [OUT / "render" / f"slide-{i:02d}.png" for i in range(1, 10)]
med = [round(DC.median_lstar(f), 1) for f in frames]
d = [abs(a - b) for a, b in zip(med, med[1:])]
acc = [round(LC.accent_coverage(Image.open(f).convert("RGB"), "#E0956A"), 4) for f in frames]
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0232", "related_items": ["tx-2026-0186"],
 "instrument": "The City of Round Rock's drone delivery page for residents, fetched October 26th, 2026, with Zipline's safety fact sheet and Austin announcement, DroneXL's October reports and Rowlett City Council's minutes of May 20th, 2025 (ORD-014-25).",
 "topic": "Zipline began taking drone delivery orders in Round Rock on October 9th from a hub in the city's extraterritorial jurisdiction. The city says its zoning doesn't specifically address drone hubs, that the FAA controls the flight paths it can't regulate, and that it is working with Zipline toward an in-city hub behind Renaissance Square on Interstate 35 that will help it write rules for future facilities. Rowlett's council voted 6 to 0 in May 2025 to add drone hubs and kiosks to its zoning code, with Zipline as the applicant.",
 "angle": "Rendered in the lastLight world as a night descent from the aircraft's station height to the ground: the aircraft at 91.4 m over the town, the dock tower in the field, the flight path as a long exposure over a city limit sign, the three mile reach as a ring on the land, the docked aircraft with the company's claims as leaders, an operations room, the turn to Rowlett's dais with one lit tally per vote, a resident under a pod coming down, and an empty staked pad.",
 "angle_note": "Every frame is drawn to illustrate. The aircraft, pod and tower follow no maker's design, the sign names no town, Rowlett's chamber is not drawn from any record of it and no strip centre is drawn at the proposed site.",
 "entities": ["Zipline", "City of Round Rock", "FAA", "Rowlett City Council", "DroneXL", "Community Impact"],
 "places": ["Round Rock", "Williamson County", "Rowlett", "Austin"],
 "what_was_refused": "any statement that the city approved the hub, any safety figure as other than the company's own, a cruise altitude, a hub layout or a site plan, the ETJ defined from a source that doesn't define it, and Rowlett's rule as preventing anything.",
 "keywords": ["drone delivery", "Zipline", "Round Rock", "extraterritorial jurisdiction", "zoning", "Rowlett", "special use permit", "FAA"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "SPATIAL SCENES in TXT's lastLight world, staged, two TXT.interior rooms. Chassis assets/js/deck/2026-10-26-tether.js: key az -55 el 8, chassis models delivery_drone, delivery_pod, dock_tower, street_glow and survey_stake, pale composite with carbon booms, galvanized lattice steel, dusk gold, walnut, cedar and worn asphalt.",
 "structural_laws": [
  "AN AIRCRAFT AT ITS TRUE HEIGHT IS A SPECK FROM THE GROUND. At 91.4 m the drone over the city limit sign was a few pixels at any honest camera, so its path became a long exposure of its wingtip lights at that height.",
  "A CORRIDOR DRAWN AS A TUBE READS AS A SEARCHLIGHT. A dashed lit line laid along screen points carried out to the station height read as a planned route.",
  "A KIT PERSON CLOSE TO THE LENS IS A MANNEQUIN. The operator held only at the next desk, seen whole from behind.",
  "A RANDOM WALK CRACK TEXTURE READS AS SHADOWS OR ROOTS. Short straight runs with hard turns read as cracks.",
  "AN UNLIT ACCENT IS A STICKER AND A LIT ONE LOSES ITS HEX. Emission at the hex over a dim albedo held both."],
 "techniques": [
  "the aircraft from 9 m off its port quarter at its station height over a street lamp grid",
  "a galvanized lattice dock tower in a field behind barbed wire, the aircraft leaving by the right edge",
  "a long exposure light trail at the station height over a city limit sign seen from below",
  "an aerial of a three mile ring laid on the land around a lit hub, its stripe widening with distance",
  "the aircraft docked in the cradle with leaders and a dashed route climbing out of frame",
  "an operations room lit by its screens with an operator at the next desk",
  "a walnut dais along its length from beside the lectern, one lit tally per vote, the minutes in the foreground",
  "a backyard at night, a resident at a cedar fence, the pod nearly down on its tether",
  "an empty staked pad on worn asphalt under one lamp"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A staged lastLight deck."},
 "accent": {"hex": "#E0956A", "name": "dusk gold, what comes down to the ground", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The pod's band on 1, 2 and 8, the cradle on 5 and the hub marks on the screens of 6."},
 "ground": {"hex": "#08070D", "note": "The lastLight world's dark sky."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
win = json.loads((OUT / "captions" / "winner.json").read_text())
add("captions", {"date": D, "carousel_no": N, "opening_move": win["opening_move"], "structure": win["structure"],
 "closing_move": win["closing_move"],
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": win.get("why_this_opening", "")[:900],
 "move_note": "Opens on the two cities in two orders, then runs the clock from Rowlett's vote to Round Rock's first order to the proposed in-city site, then names what the deck weighs, and closes on which order serves neighbors better."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
