#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-02, carousel no. 66. Appends one entry to each variety ledger,
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
D, N = "2026-11-02", 66
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0236", "related_items": [],
 "instrument": "The Southwest Research Institute press release on the automated survey, the City of San Antonio news release of October 20th and the Animal Care Services statistics page, all fetched November 2nd, 2026.",
 "topic": "Southwest Research Institute and San Antonio Animal Care Services will repeat the city's 2019 manual survey of unrestrained dogs in the same 32 study areas, using a phone mounted on a vehicle window with object detection software, with automated and human review of the clips. Field research is expected to run through December 2026, then SwRI forwards a final report to the department. The city says the sample is not meant to count every unrestrained dog.",
 "angle": "A tan dog on a west side street at night, seen through the survey car's window inside a gold detection box, then on the phone's screen, inside labelled corners, split as stray and roaming, on a reviewer's screen beside unticked checks, then caliche plugs on a clay city plan for the 32 areas, the 2019 mould beside the 2026 cast with a 7 year rule, a field block over October to December with the report past it, and the dog watching the survey car leave.",
 "angle_note": "Every frame is drawn to illustrate, to no breed. No 2019 finding is drawn and no person is drawn.",
 "entities": ["Southwest Research Institute", "City of San Antonio", "San Antonio Animal Care Services", "Jon Gary", "Mike Koets"],
 "places": ["San Antonio"],
 "what_was_refused": "any 2019 finding (the study PDF was not fetched), any statement that the survey is already running, and any accuracy figure for the stray or roaming call (no source gives one).",
 "keywords": ["San Antonio", "Animal Care Services", "SwRI", "loose dogs", "unrestrained dogs", "object detection", "machine vision", "survey"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "SPATIAL SCENES on one staged lastLight west side block at night, with three TXBENCH material reliefs. Chassis assets/js/deck/2026-11-02-sightline.js: street_dog (an SDF body with fur normals in lean and full builds) and window_phone, the kit crossover, chain link, ranch house and yards, and dusk gold as the one accent for the machine's detection.",
 "structural_laws": [
  "A CAMERA-SPACE OCCLUDER BUILT FOR ONE FOV IS WRONG AT ANOTHER. The window seal was placed with the old fov after the frame's fov changed and its bevel ran through the type column until it was placed with the real one.",
  "A SCREEN IN A RENDER IS A SECOND RENDER. The phone's and the monitor's screens took a render target of the lens view; the frame's own detection box had to be sized to that target's aspect or it fell off the screen.",
  "A LINE IN FRONT OF THE SUBJECT STRIKES IT. Sight lines from a lens to a box crossed the dog until the dog was drawn last over them, and then they were cut altogether.",
  "A FRONTAL KEY FLATTENS A BODY SEEN FROM BEHIND. The close's dog read as felt until the frontal key was cut to a third and a low side key from camera left raked the flank.",
  "A LOW CAMERA SHOWS A DARK WORLD AS A PLATE. At 0.35 m the close's rect fell under the detail floor; at 0.62 m the lit walk in the pool carried it."],
 "techniques": [
  "the cover from inside the car, the window seal and sill in camera space, the dog boxed in four gold corners",
  "the phone clamped on the lowered glass, its screen a render target of the lens view with the box inside",
  "the dog inside four labelled corners, the dog drawn over the marks",
  "two street_dog builds side by side, lean and wary against full and stepping, each boxed",
  "a reviewer's monitor lit only from its screen, the clip beside four unticked rings set as type",
  "32 caliche plugs on a clay city plan with diagonal arterials as a material relief",
  "the 2019 mould and the 2026 cast as two 4 by 8 blocks with a 7 division steel rule between, set in one dark bed",
  "a caliche block over three month graduations on a dark steel rule, the report plug on a plain plate past December",
  "the dog at its own height watching the survey car's tail lamps down a dark street"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A staged night street and dark reliefs; the planned arc was rewritten to the measured one after the render."},
 "accent": {"hex": "#E0956A", "name": "dusk gold, the machine's detection", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The box around the dog on 1, 3 and 4, small on the screens of 2 and 5, the chamfers of the 2026 plugs on 7."},
 "ground": {"hex": "#09080C", "note": "The night street and the reliefs' black clay."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
mv = json.loads((OUT / "caption_moves.json").read_text())
add("captions", {"date": D, "carousel_no": N, "opening_move": mv["opening_move"], "structure": mv["structure"],
 "closing_move": mv["closing_move"],
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": "Opens on the release's own definition of a stray, climbs through the instrument, the review, the sample and the timeline, and closes on the question the report could answer.",
 "move_note": "Opens on how a stray looks, quotes the release's two labels, then the phone, the software and the review in the release's tense, the 2019 repeat in 32 areas as a sample, the director's line and the December window, and closes asking whether the report will say how often a person and the software disagreed."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
