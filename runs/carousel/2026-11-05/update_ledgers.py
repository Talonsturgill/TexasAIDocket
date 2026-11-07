#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-05, carousel no. 69. Appends one entry to each variety ledger,
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
D, N = "2026-11-05", 69
OUT = ROOT / "out" / D
L = ROOT / "ledger/carousel"
def add(name, entry):
    p = L / f"{name}.json"; t = json.loads(p.read_text())
    t["entries"] = [e for e in t["entries"] if e.get("date") != D] + [entry]
    p.write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n")
frames = [OUT / "render" / f"slide-{i:02d}.png" for i in range(1, 10)]
med = [round(DC.median_lstar(f), 1) for f in frames]
d = [abs(a - b) for a, b in zip(med, med[1:])]
acc = [round(LC.accent_coverage(Image.open(f).convert("RGB"), "#9A5028"), 4) for f in frames]
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0241", "related_items": [],
 "instrument": "Applied Optoelectronics' third quarter 2026 results release (Form 8-K, Exhibit 99.1) and its Form 10-Q for the same quarter, both filed with the SEC on November 5th, all fetched November 5th, 2026.",
 "topic": "Applied Optoelectronics, which makes its laser chips only in Sugar Land, says its 2027 capacity expansion plan in the United States will take longer because of a longer than expected time to obtain necessary electrical power, among other construction issues. It expects equipment for over 500,000 pieces of 800G and 1.6 Tb products a month by the end of 2026 and capacity for over 1 million by the end of 2027. The 10-Q gives Gillingham Lane at about 209,665 square feet, the Kirby property in Pearland at about 388,133, and two Chimney Rock Road buildings still to be constructed at about 356,186 and 737,621 rentable square feet, leased on August 31st with completion anticipated about 16 months later.",
 "angle": "One empty bay lit only through its dock door at last light, twenty taped machine pads for the 2027 target at one drawing unit. The bay with one gold pad, the transceiver on the floor, the Sugar Land plant at its stated area, a relief of four stated areas, ten of twenty pads gold, sixteen survey stakes for the months to completion, the CFO's sentence over a waiting transformer, a hall of switches for the unnamed customer, and every pad gold with the floor still empty.",
 "angle_note": "No building, site or utility is identified as the one waiting, because the release names none. Every frame is drawn to illustrate. The pads and stakes are drawing units that carry computed counts, never physical quantities.",
 "entities": ["Applied Optoelectronics"],
 "places": ["Sugar Land", "Pearland", "Houston", "Chimney Rock Road", "Fort Bend County"],
 "what_was_refused": "any claim that the 1 million a month target sits in the United States, any site or utility for the power wait, any size for the three other Houston buildings, and Sugar Land as the company's only Texas manufacturing site.",
 "keywords": ["Applied Optoelectronics", "optical transceivers", "laser chips", "electrical power", "Sugar Land", "Houston", "data centers", "earnings release"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "SPATIAL SCENES in one dark bay lit only through its dock door at last light (frames 1, 2, 5, 8 and 9), exteriors at last light (3, 6 and 7) and one TXBENCH material relief (4). Chassis assets/js/deck/2026-11-05-dockdoor.js: dock_door, osfp_module, survey_stake and conduit_stub kit models with the kit's machine_pad, structural_frame, warehouse, padmount_transformer, utility_pole, server_row and person, and dusk_gold floor tape as the one accent for a stated capacity target.",
 "structural_laws": [
  "A FORMWORK LIP OUTSIDE A STATED SIDE REORDERS THE SQUARES. A lip added outside the stated side on the cut pads only drew the 356,186 square bigger than the 388,133 one, so every outer edge is now the stated side.",
  "TWO SURFACES AT ONE DEPTH BAND LIKE ACNE. A slab added under a raised pad face at the face's own height drew banded triangles a reviewer took for shadow acne.",
  "A ROOFLESS CUTAWAY NEEDS THE DOOR TO MAKE ITS LIGHT. Lighting the floor with a spot inside the bay read as an overhead lamp; a low source outside cut by the casting back wall made a hard trapezoid from the sill.",
  "A CONTACT DISC AT MACRO SCALE IS A FACETED PLATE. TXT.contact and a levelling plate under an object a few centimetres long read as a low-poly disc.",
  "A MATTE GROUND UNDER AN APRON Z-FIGHTS. TXT.ground laid under a kit apron drew white patches where the two planes met."],
 "techniques": [
  "a dark bay down a wedge of dock door light, one pad taped gold in the stripe",
  "an OSFP class module on the epoxy in a soft pool of the door's spill",
  "a tilt wall plant at its stated floor area at last light with a warm clerestory band",
  "a material relief of four squares of stated area, two raised steel slabs and two cut clay pads",
  "a plan oblique of twenty pads, ten gold and ten grey, under a hard trapezoid of door light",
  "sixteen survey laths on a string line at last light, two flagged, a worker at the near end",
  "a padmount transformer with three capped conduit stubs beyond the open door",
  "a cold aisle with a top of rack switch, pale pull tabs and a warm strip fixture",
  "the bay from the dock leveller with every pad gold and a worker in the door light"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A dark bay and staged exteriors."},
 "accent": {"hex": "#9A5028", "name": "dusk_gold floor tape as rendered, a stated capacity target", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The gold pad on 1, the gold rows on 5, the string line and flags on 6, and every pad on 9."},
 "ground": {"hex": "#0A0A0C", "note": "The bay's black and the dark epoxy."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
mv = json.loads((OUT / "caption_moves.json").read_text())
add("captions", {"date": D, "carousel_no": N, "opening_move": mv["opening_move"], "structure": mv["structure"],
 "closing_move": mv["closing_move"],
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": "Opens on the place the chips are made, carries the 2026 and 2027 targets as the company's own expectations, and closes on the question the release leaves open, which site the power is for.",
 "move_note": "Pivots from where the company makes its chips to what it says is late, keeps the power wait attributed, and says what the release does not, which building waits and how much of the 2027 capacity is in the United States."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
