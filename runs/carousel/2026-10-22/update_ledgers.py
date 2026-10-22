#!/usr/bin/env python3
"""update_ledgers.py for 2026-10-22, carousel no. 57. Appends one entry to each variety ledger,
the artwork values measured off the final renders by deck_coherence and layout_check's own
functions, the caption's counts measured off caption.txt. Then ledger_check --derive rewrites the
caption exclusion lists."""
import json, re, sys, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]   # runs/carousel/<date>/update_ledgers.py
sys.path.insert(0, str(ROOT / "scripts/carousel"))
import deck_coherence as DC, layout_check as LC
from PIL import Image
D, N = "2026-10-22", 57
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0223", "related_items": ["tx-2026-0092", "tx-2026-0119"],
 "instrument": "The paper on arXiv (2510.13928v3, abstract and HTML full text) and Texas A&M Engineering News' release, both fetched October 22nd, 2026.",
 "topic": "Researchers at Texas A&M, UT Austin and Purdue continually trained Llama3 8B Instruct, two Qwen2.5 models and Qwen3 4B Thinking on mixes of short, popular Twitter/X posts. Reasoning fell with the junk share (ARC Challenge with chain of thought from 72.1 to 57.2 on Llama3), thought skipping was the main failure, and instruction data at 4.8 times the junk tokens left the best repaired models 17.3 points under the baseline.",
 "angle": "Rendered in the staged lastLight world on one scale, 0.06 m per point: a stair with its middle treads gone for the cover, a relief of glass chips against limestone slivers for the two training sets, five stairs one per dose under a brass datum, a walk of four landings with a short step up and a cliff, the bare carcass of a stair at the No Thinking share, one junk tread beside 4.8 clean ones, the repaired flight still under the brass, four flights beside an empty chalked pad, and the whole stair beside the broken one with a figure for scale.",
 "angle_note": "Every frame is drawn to illustrate. Every rise is a score at one scale, read from figures.json by the frame's own code. No real place, product or person is depicted.",
 "entities": ["Texas A&M University", "University of Texas at Austin", "Purdue University", "COLM 2026"],
 "places": ["College Station", "Brazos County", "Austin", "Texas"],
 "what_was_refused": "The release's 2010 date for the posts (the paper says its dataset was collected in 2023) and its junk definition without quotes. No collection year printed. The junk shares are never stated as a measure of the internet, and the closed models are never said to have been tested.",
 "keywords": ["Texas A&M", "UT Austin", "Purdue", "language models", "training data", "brain rot", "Twitter/X", "reasoning", "thought skipping", "COLM"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by out/2026-10-22/update_ledgers.py.",
 "register": "SPATIAL SCENES in TXT's lastLight world, staged, with one material relief. Chassis assets/js/deck/2026-10-22-stair.js: key az -58 el 10, five chassis models (an open stair flight, a landing on a pier, a coursed datum wall with a brass band, one cast tread, a chalked pad), sawn limestone, weathering steel with a warm shadow side, exposed aggregate.",
 "structural_laws": [
  "A COPLANAR ACCENT PLANE Z-FIGHTS INTO A SCREEN. A face plane 0.5 mm in front of the brass strip rendered a fine moire the critics read as the deleted print look.",
  "A BAND THAT MARKS A LEVEL RISES FROM IT. Hung down from the datum, the band ate the shortfall under the nearest landing.",
  "A METAL UNDER THE LASTLIGHT SKY MIRRORS IT. A brass at metalness 0.9 read white or cream; a dark base with the accent in its emissive held the colour.",
  "A CANVAS TILE DRAWS EACH MARK AT ITS WRAPPED COPIES, or a cloud cut at the edge repeats as a hard rectangle.",
  "A KIT FIGURE UNDER A STRONG FILL READS PALE. Dark cloth set on the meshes and a low fill held it as a silhouette."],
 "techniques": [
  "an open stair with its middle treads gone, feet on lit caliche, pier at right",
  "a plan relief of glass chips against limestone slivers at one token scale, a brass divider",
  "five stairs one per dose from a long lens under a brass datum on a coursed wall",
  "four landings from a low three quarter, a fall, a short step up and a cliff, under the datum",
  "a stair carcass with treads only at the foot, the bare notched stringers lit",
  "one junk tread beside a stack of clean limestone treads, the top one sawn short",
  "the repaired flight from its open side, a fresh limestone landing under the brass",
  "four flights climbing out of frame on a plinth beside an empty chalked pad",
  "the whole stair beside the broken one, a figure in silhouette for scale"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A staged lastLight deck."},
 "accent": {"hex": "#E0956A", "name": "dusk gold", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The brass datum where the base model stood."},
 "ground": {"hex": "#08060F", "note": "The lastLight world's dark field around the stage."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
add("captions", {"date": D, "carousel_no": N, "opening_move": "the who", "structure": "Ladder",
 "closing_move": "ask the one question the decision leaves open",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": (OUT / "captions" / "critic_note.txt").read_text().strip()[:900],
 "move_note": "Names the three institutions first, climbs from the junk definition through the dose, the failure and the repair to the limits, and closes on whether other platforms would do the same."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
