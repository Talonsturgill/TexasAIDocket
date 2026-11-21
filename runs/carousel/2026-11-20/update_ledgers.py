#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-20, carousel no. 83. Appends one entry to each variety ledger,
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
D, N = "2026-11-20", 83
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0253", "related_items": ["tx-2026-0186"],
 "instrument": "East Texas A&M University's November 16th, 2026 news release on its GPS spoofing study accepted at WATCH 2026, with NSF Award 2502117 and the WATCH 2026 programme for context, fetched November 20th, 2026.",
 "topic": "East Texas A&M researchers in Commerce tested whether AI can spot false location in a drone's flight records from its own motion sensors, with no GPS readings. On a public dataset of 96 recorded flights, 42 normal and 54 spoofed, with 22 whole flights held back for testing, they compared several models, and a pretrained model called Chronos scored 97.5 percent on 10 consecutive readings. The paper's first author is an undergraduate. Running the check during flight is a next step.",
 "angle": "A search drone sent to sweep a ridge flies into the next valley. The cover on a bluestem ridge, the real drone and its frosted glass twin on a studio sweep, an aerial of the sweep it was given and the amber path it flew, the shell-off drone on a lab table with the team's places set, the flight controller with amber arrows and the GPS puck unplugged, a clay tablet of 96 tracks with an enlarged pair, the 22 sealed tiles before the 74 training tiles, a glass loupe over nickel studs with the score on its rim, and the grounded drone back on the ridge beside its case of 22 cartridges.",
 "angle_note": "Every frame is drawn to illustrate and shows no real place. The reported position is always frosted periwinkle glass that casts no shadow. Amber means motion the drone itself measured only. The score is never drawn as an accuracy and the check is never shown flying live.",
 "entities": ["East Texas A&M University", "National Science Foundation", "WATCH 2026", "ACM CCS", "Chronos"],
 "places": ["Texas", "Commerce"],
 "what_was_refused": "the dataset's name and the other seven models (not on a primary page fetched), any live flight or real search, a face for any team member, a map of a real ridge, and any claim that the method works in the air.",
 "keywords": ["GPS spoofing", "drones", "motion sensors", "Chronos", "East Texas A&M", "Commerce", "NSF", "AI"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "BESPOKE, LOOK V2 people tone, nine slide artists. Outdoor TXT.sky worlds (1, 3, 6, 9), TXT.studio sweeps (2, 5, 7, 8), a TXT.interior lab (4). Spine assets/js/deck/2026-11-20-truetrack-bespoke.js with chassis models survey_quad and flight_board.",
 "structural_laws": [
  "DEPTH_FLOOR READS THE SLIDE'S OWN TEXT, so a frame that adds its subject through a chassis helper (CH.put, CH.aim) is not counted as staged; call TXT.add and TXT.frame in the slide itself.",
  "KIT PEOPLE AT A CLOSE TABLE CAMERA READ AS CARTOON HANDS; show the team by their places set rather than by cropped figures.",
  "A SWEEP'S HORIZON BAND IS MINIFIED TO A SMOOTH GRADIENT, so panel_ready's middle ground patch fails unless the texel scale is large enough to survive the mipmaps.",
  "THE REPORTED POSITION IS FROSTED GLASS WITH castShadow FALSE in every frame, so the shadow alone says which drone is real."],
 "techniques": ["a bluestem ridge crest at last light with two searchers turned away and a survey drone banking toward the saddle", "a solid survey drone on a brushed resin sweep beside its frosted glass twin that casts no shadow", "an aerial oblique of a frosted lawnmower sweep on the crest with one amber beaded path dropping over the saddle", "a shell-off survey drone on a laminate lab table with four open laptops set and nobody drawn", "a macro flight controller with three machined amber arrows from its motion chip and the GPS puck unplugged in glass", "a caliche clay tablet of 96 raised tracks, pewter and kinked copper, with an enlarged pair in a bevelled well", "22 sealed tiles in a glass case before a tray of 74 engraved training tiles across a glass sill", "a glass bar magnifier over ten nickel studs on a plum ribbon above a rose enamel score bar", "the grounded drone on its launch mat beside an open case of 22 flight log cartridges, back on the ridge"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders."},
 "accent": {"hex": ACC, "name": "people amber", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "Motion the drone itself measured only."},
 "ground": {"hex": "#c98a5a", "note": "Copper bluestem and laminate under the people tone's periwinkle and plum."}})
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
