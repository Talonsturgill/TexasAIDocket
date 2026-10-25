#!/usr/bin/env python3
"""update_ledgers.py for 2026-10-25, carousel no. 60. Appends one entry to each variety ledger,
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
D, N = "2026-10-25", 60
OUT = ROOT / "out" / D
L = ROOT / "ledger/carousel"
def add(name, entry):
    p = L / f"{name}.json"; t = json.loads(p.read_text())
    t["entries"] = [e for e in t["entries"] if e.get("date") != D] + [entry]
    p.write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n")
frames = [OUT / "render" / f"slide-{i:02d}.png" for i in range(1, 10)]
med = [round(DC.median_lstar(f), 1) for f in frames]
d = [abs(a - b) for a, b in zip(med, med[1:])]
acc = [round(LC.accent_coverage(Image.open(f).convert("RGB"), "#C9B393"), 4) for f in frames]
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0171", "related_items": ["tx-2026-0143", "tx-2026-0202"],
 "instrument": "ERCOT Market Notice M-B091426-01 (the data center RFI, its Section C water questions, deadline and attestation), fetched October 25th, 2026, with the Texas Tribune's October 14th report on the water use survey's records and the water board's own survey pages.",
 "topic": "Records the Tribune obtained for 2020 through 2025 count 334 data center facilities and 233 never returned the water board's mailed survey, a Class C misdemeanor with a fine of up to $500 the board can't prosecute itself. ERCOT's September 14th notice now carries the board's Section C questions to proposed data centers of 25 to under 75 MW classed as Substantiated and to large loads in ERCOT's interconnection review not yet energized, with a notarized attestation and failures reported to the PUC and the Governor.",
 "angle": "Rendered in the lastLight world as a cast iron return plate, a threaded bore per facility and a brass hex plug in each of the 101 that answered, seen low from its open end, in plan, from above under the fine, and reversed from behind the brass for the close. Between, the survey's 10 million gallon line as a tank beside a data hall, last year's 1.4 billion gallons as a farm of 140 such tanks, the turn at a substation transformer bay, the request's MW band as a copper bus bar relief, and the notarized sheet with its day rule.",
 "angle_note": "Every frame is drawn to illustrate. No bore stands for a named facility, no water body is drawn, and no utility, ERCOT site or person is depicted.",
 "entities": ["ERCOT", "Texas Water Development Board", "PUC", "Office of the Governor", "The Texas Tribune"],
 "places": ["Texas", "Austin"],
 "what_was_refused": "any implication that ERCOT's request reaches the 233 facilities that skipped the survey, 'jointly' or 'the same questions' for Section C, a fine ever issued, the report of December 10th as existing, and Abbott's executive actions as law.",
 "keywords": ["water use survey", "TWDB", "ERCOT", "M-B091426-01", "Section C", "data centers", "notarized attestation", "Batch Zero"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "SPATIAL SCENES in TXT's lastLight world, staged, with three material reliefs. Chassis assets/js/deck/2026-10-25-returnplate.js: key az -62 el 13, chassis models return_plate and ground_storage_tank, gray cast iron with sand cast grain, brass hex plugs, caliche, a desert tan tank coating, tinned copper, glazed porcelain and cotton bond.",
 "structural_laws": [
  "A NOISY RELIEF SURFACE UNDER A CAST SPECKLES. Height noise on a channel web under a flange's cast broke into worm-like near-miss speckle; a flat height with tooth in the albedo cast one clean edge.",
  "A PLAN GRID TWICE IS ONE COMPOSITION TWICE. The tank roofs in plan repeated the plate in plan; the oblique farm of clones read as tanks standing on ground.",
  "A CLOSE CROP ON A SUBSTATION DRIVES ITS BUSHINGS THROUGH THE TYPE. Every close camera on the bay struck the hook, dek or footer; the yard held only from about 36 m.",
  "A FRAME THAT CALLS TXT.sky MUST SHOW IT. Pitching down over the bores until the haze left the frame took the sky with it, so the horizon stays behind the hook.",
  "THE ACCENT CAN CARRY THE MOTIF THROUGH THE TURN. The brass returned as the notary seal's foil disc on 8, so the answer-returned meaning crossed from the survey to the request."],
 "techniques": [
  "the return plate from 32 cm at its open end, open bores at the lens and the brass rank far",
  "a material relief of the plate in plan, 334 bores and 101 brass plugs",
  "the open bores from above under 'Up to $500', the horizon behind the figure",
  "a 60 m tank raked from the left beside a data hall's end",
  "an oblique aerial of 140 clones of that tank in blocks of seven by two",
  "an autotransformer bay of a substation yard, bushings lit against the dark",
  "a material relief of a copper bus bar at ten px per MW, the step at 25 and the slot to 75",
  "a material relief of a cotton bond sheet with an embossed crimp seal and a brass foil disc, a cast iron day rule of 28 ticks",
  "the plate reversed from behind the brass for the close"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A staged lastLight deck."},
 "accent": {"hex": "#C9B393", "name": "brass of a returned survey", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "Brass means an answer returned: the plugs on 1, 2 and 9 and the seal's foil on 8."},
 "ground": {"hex": "#0A0807", "note": "The lastLight world's dark sky and caliche."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
win = json.loads((OUT / "captions" / "winner.json").read_text())
add("captions", {"date": D, "carousel_no": N, "opening_move": win["opening_move"], "structure": win["structure"],
 "closing_move": "Name what happens next and when.",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": win.get("why_this_opening", "")[:900],
 "move_note": "Opens on the before and after, the mailed survey against the request that comes before the power flows, then the count and the fine, then whether the request reaches the 233 and why its list is drawn differently, then what the notice requires, and closes on whether ERCOT's expected report will say how many responded."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
