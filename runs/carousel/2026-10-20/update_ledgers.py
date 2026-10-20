#!/usr/bin/env python3
"""update_ledgers.py for 2026-10-20, carousel no. 55. Appends one entry to each variety ledger,
the artwork values measured off the final renders by deck_coherence and layout_check's own
functions, the caption's counts measured off caption.txt. Then ledger_check --derive rewrites the
caption exclusion lists."""
import json, re, sys, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/carousel"))
import deck_coherence as DC, layout_check as LC
from PIL import Image
D, N = "2026-10-20", 55
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0222", "related_items": ["tx-2026-0101", "tx-2026-0137"],
 "instrument": "The Journal of Imaging paper on PubMed Central (PMC13412611) and Houston Methodist's Leading Medicine blog post on image based AI in its operating rooms, both fetched October 20th, 2026.",
 "topic": "Houston Methodist fitted four high resolution wall cameras in each of the 15 operating rooms of Walter Tower's cardiothoracic suite. A Journal of Imaging study estimates the image based AI deployment was associated with about 25 more cases a month, a 95% interval of 8.3 to 41.0 over a baseline of about 339, calls it associated rather than caused, can't separate it from the change management program that came with it, ran a placebo test where the suite ranked second of 11, and discloses the hospital's minority equity interest in the vendor, Apella.",
 "angle": "Rendered in the floodlit world inside a tiled operating room: the wall camera close on its tile for the cover, a white card relief model of one room with four camera brackets, a wall of 339 sterile container ends with a nurse for scale, the same wall crowned by 25 gold ends, 25 lids in 41 taped bays with a white stripe to 8.3, eleven clamps on a towel with the second gold, a crew member pointing at a turnover board under the camera, the paper's disclosure clipped to a steel back table, and the gold container waiting for the next case under the camera.",
 "angle_note": "Every frame is drawn to illustrate. One container end is one case, one bay is one case and one clamp is one unit of the placebo test, all from figures.json. No real room, product or person is depicted.",
 "entities": ["Houston Methodist", "Walter Tower", "Apella Technology", "Journal of Imaging"],
 "places": ["Houston", "Harris County", "Texas"],
 "what_was_refused": "The 25 is never stated as a count or as caused by the cameras. The camera installation date and the software deployment date are kept apart. mdpi.com answered 403, so the paper is read on PubMed Central.",
 "keywords": ["Houston Methodist", "operating room", "computer vision", "Apella", "surgical cameras", "case volume", "AI", "hospital", "Walter Tower", "Journal of Imaging"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by out/2026-10-20/update_ledgers.py.",
 "register": "SPATIAL SCENES in TXT's floodlit world inside TXT.interior rooms with three material reliefs. Chassis assets/js/deck/2026-10-20-suite.js: key az -40 el 40, eight chassis models (operating table, surgical light, room camera with a pan on its knuckle, anesthesia station, back table, service boom, sterile container, turnover board), a glazed tile wall, a scrub cap and an instanced model with per unit value.",
 "structural_laws": [
  "TXT.interior's BACK WALL IS 0.2 M THICK AND CENTRED ON z = -d/2. Anything placed at the wall's nominal plane sits inside it and vanishes; the face is at -d/2 + 0.1.",
  "A SMALL TXT.ground UNDER A WIDE SHOT SHOWS ITS OWN EDGE. A 9 m vinyl square read as two lit slabs with a ruled terminator; size it past the frustum.",
  "K.make RE-CENTRES A MODEL'S FOOTPRINT. A wall mounted model whose back sits on the wall plane needs keepOrigin, or its face is pulled behind the wall.",
  "A ROOM CAMERA ROTATED WHOLE TURNS ITS PLATE OFF THE WALL. The plate must stay flush and the head pan on its knuckle.",
  "A CLOSE ON A KIT MODEL EXPOSES IT. The sterile container read as a toy suitcase until it was rebuilt with a gasket, filter plates, bail handles and a tamper tag."],
 "techniques": [
  "a wall camera close on a glazed tile wainscot under its stainless cap, the lens turned three quarters to the reader",
  "a white card relief model of one operating room in plan, four gloss black camera brackets with steel lens rings on the wall tops, leaders to the door and the table",
  "a wall of 339 instanced sterile container ends, 13 across, a nurse at its foot, from a long lens",
  "the same wall and camera with 25 gold ends crowning it",
  "a plan relief of 41 taped bays on vinyl, 25 ribbed lids, a white tape stripe at the foot of each bay to 8.3",
  "a plan relief of eleven hemostatic clamps on a huck towel, the second anodised gold",
  "a crew member pointing at a turnover board on the tile beside a wall camera whose shadow crosses the board",
  "a plan relief of a page clipped to a brushed steel back table, the disclosure as DOM type",
  "the gold container on the back table close, the wall camera rim lit on the tile behind"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A staged floodlit interior deck."},
 "accent": {"hex": "#E0956A", "name": "dusk gold", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The added cases: the gold container ends, lid rims, the gold clamp and the waiting container."},
 "ground": {"hex": "#08060F", "note": "The floodlit world's black field around the stage."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
add("captions", {"date": D, "carousel_no": N, "opening_move": "the number that is wrong", "structure": "Ledger",
 "closing_move": "ask the one question the decision leaves open",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": (OUT / "captions" / "critic_note.txt").read_text().strip()[:900],
 "move_note": "Opens on the 25 a reader will take for a count and corrects it in the next line, then lays out what is known, what the study can't separate and the interval that sizes the unknown, and closes on what another Texas hospital would want proven."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
