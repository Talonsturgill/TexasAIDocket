#!/usr/bin/env python3
"""update_ledgers.py for 2026-10-28, carousel no. 62. Appends one entry to each variety ledger,
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
D, N = "2026-10-28", 62
OUT = ROOT / "out" / D
L = ROOT / "ledger/carousel"
def add(name, entry):
    p = L / f"{name}.json"; t = json.loads(p.read_text())
    t["entries"] = [e for e in t["entries"] if e.get("date") != D] + [entry]
    p.write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n")
frames = [OUT / "render" / f"slide-{i:02d}.png" for i in range(1, 10)]
med = [round(DC.median_lstar(f), 1) for f in frames]
d = [abs(a - b) for a, b in zip(med, med[1:])]
acc = [round(LC.accent_coverage(Image.open(f).convert("RGB"), "#7CC6D6"), 4) for f in frames]
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0179", "related_items": ["tx-2026-0116", "tx-2026-0129"],
 "instrument": "The City of Dallas briefing Update on the Sanitation and Code Compliance AI Camera System to the Quality of Life, Arts, and Culture Committee, dated October 19th, 2026, with the Finance Committee briefing of December 9th, 2025 and the city memo of April 10th, 2026.",
 "topic": "Dallas runs City Detect computer vision cameras on 50 Sanitation brush trucks along their existing routes. The October 19th briefing says an observation is not a confirmed Code violation, that staff review every one before Code Compliance acts, and that a first courtesy letter is now an educational reminder with no deadline. Its results table counts 5,318 observations reviewed, 2,928 courtesy notices, 473 field inspections, 374 voluntary corrections, 34 direct abatements and 101 formal enforcement. It publishes no accuracy figure and lists calibrating detection accuracy and setting accuracy measures as next steps.",
 "angle": "Rendered in the lastLight world along one route: the loaded brush truck with its two lit camera pods, the fleet of fifty in a yard, the pod close, a reviewer's monitor tiled one tile per observation, the results table as cut cedar elm limbs racked at one scale in a city yard, a courtesy letter in a brick mailbox, the same rack with a bare seventh arm and a blank tag for accuracy, an inspector at the curb, and the truck leaving up the street.",
 "angle_note": "Every frame is drawn to illustrate. The truck, pods, monitor, rack and letter follow no maker's or city's design and carry no lettering.",
 "entities": ["City of Dallas", "City Detect", "Dallas Sanitation", "Dallas Code Compliance", "Quality of Life, Arts, and Culture Committee"],
 "places": ["Dallas", "Dallas County"],
 "what_was_refused": "FOX 4's relayed memo counts (3,700 violations, 57 citations, 34 properties) as figures on any frame, any rate or share computed from the results table, the 32 and 68 proactive split whose base the slide doesn't state, and any statement that the cameras issue citations.",
 "keywords": ["computer vision", "City Detect", "Dallas", "code compliance", "brush trucks", "courtesy notice", "accuracy"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "SPATIAL SCENES in TXT's lastLight world, staged, one TXT.interior room. Chassis assets/js/deck/2026-10-28-route.js: key az -125 el 12, chassis models brush_truck, camera_pod, brush_pile, cut_limb, limb_rack, count_token and notice_letter, white enamel, worked rust streaked steel, city blue, cedar elm bark with ringed pale cut ends, galvanized steel.",
 "structural_laws": [
  "A PLAN VIEW RELIEF OF BARS ON A CURB READS AS A BAR CHART OR A UI TRAY. Two audition rounds failed it, and a rack of real limbs at one scale in a yard read as stock a crew would stack.",
  "K.MAKE CENTRES A MODEL'S FOOTPRINT. A model whose origin carries meaning, a limb's butt or a rack's published arm coordinates, must set userData.keepOrigin or every butt shifts by half its own length.",
  "A LOAD OF FACETED PRISMS READS AS TOY BLOCKS. The truck load rebuilt from the barked, bent cut_limb with ringed ends read as wood at feed size.",
  "A SCREEN PLANE PLACED BY BOUNDING BOX MISREGISTERS AGAINST THE BEZEL. Seated in the kit monitor's own head at its display rectangle it sat flush.",
  "AN ACCENT IN DOM TYPE DOESN'T COUNT AT THUMB SCALE. Solid accent surfaces, a coated lens, a tape band, a blank tag and a title strip, carried it."],
 "techniques": [
  "the loaded brush truck from above its rear corner with both pods lit",
  "fifty trucks instanced in a dark yard from above, the near rows in the pool",
  "the camera pod close on the body's top rail with a warm fill and rim",
  "a monitor in a dark office, its screen 5,318 flat tiles in runs",
  "a galvanized cantilever rack in a city yard carrying six limbs at one scale",
  "a brick mailbox at the curb with the letter under the mail door's pull",
  "the same rack closer with a bare seventh arm and a blank cyan stock tag",
  "an inspector at the truck's front on the sidewalk beside the windrow",
  "the truck leaving up a dark street, the inspector in a warm pool at the curb"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A staged lastLight deck."},
 "accent": {"hex": "#7CC6D6", "name": "the camera's cold cyan", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The pods' coated lenses and lamps, the review queue's title strip on 4, the tape on the 5,318 limb and the blank accuracy tag on 7."},
 "ground": {"hex": "#08070C", "note": "The lastLight world's dark sky."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
win = json.loads((OUT / "captions" / "winner.json").read_text())
add("captions", {"date": D, "carousel_no": N, "opening_move": win["opening_move"], "structure": win["structure"],
 "closing_move": win["closing_move"],
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": win.get("why_this_opening", "")[:900],
 "move_note": "Opens on the cameras riding the brush trucks, sets up the ticketing reading, turns on the briefing's line that an observation is not a confirmed violation and that staff review every one, then the changed first letter, and closes on the accuracy figure the briefing doesn't publish."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
