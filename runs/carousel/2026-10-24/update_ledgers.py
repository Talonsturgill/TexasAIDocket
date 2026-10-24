#!/usr/bin/env python3
"""update_ledgers.py for 2026-10-24, carousel no. 59. Appends one entry to each variety ledger,
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
D, N = "2026-10-24", 59
OUT = ROOT / "out" / D
L = ROOT / "ledger/carousel"
def add(name, entry):
    p = L / f"{name}.json"; t = json.loads(p.read_text())
    t["entries"] = [e for e in t["entries"] if e.get("date") != D] + [entry]
    p.write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n")
frames = [OUT / "render" / f"slide-{i:02d}.png" for i in range(1, 10)]
med = [round(DC.median_lstar(f), 1) for f in frames]
d = [abs(a - b) for a, b in zip(med, med[1:])]
acc = [round(LC.accent_coverage(Image.open(f).convert("RGB"), "#4E5FA8"), 4) for f in frames]
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0230", "related_items": ["tx-2026-0140"],
 "instrument": "Tesla's Q3 2026 Update (the investor relations PDF, its capacity table and footnotes) and NHTSA ODI's resume for Audit Query AQ26002, both fetched October 24th, 2026.",
 "topic": "Tesla's own capacity table lists Model Y, Cybertruck, Cybercab and Megapack under its Texas label at Production, and Optimus, its humanoid robot, at Construction with no capacity figure. Optimus production began in Fremont. Installed capacity is not the current production rate, and the update gives no count of Cybercabs built.",
 "angle": "Rendered in the floodlit world as a tilt up plant wall at night with a bay door per Texas row in the table's order, the Production rows lit and the Optimus bay dark. Inside the first lit bay the line, a relief of the vehicle rows at a shared scale, battery enclosures on the apron for the Megapack row, the dark bay's anchor bolts in taped pads under unlit lamps, a relief of the Cortex compute rows with the year end plan as an empty taped groove, the unclad Austin Fab steel on its taped pads, a covered car in a lit bay, and the wall again from the dark end for the close.",
 "angle_note": "Every frame is drawn to illustrate. No Tesla plant, product or person is depicted, the bays follow the table's order rather than the site, and the covered car is a fabric shell, not a Cybercab likeness.",
 "entities": ["Tesla", "NHTSA", "Optimus", "Cybercab", "Megapack", "Cortex"],
 "places": ["Austin", "Texas", "Fremont"],
 "what_was_refused": "NHTSA's 1,000 as a deployed count, the 400 MW plan placed in Texas, the nearly two million unsupervised miles as Austin only, the October 21st date as the PDF's own, and Texas rows read as one universal over the Early Ramp cathode and lithium rows.",
 "keywords": ["Tesla", "Optimus", "installed capacity", "Cybercab", "Megapack", "Cortex", "NHTSA"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "SPATIAL SCENES in TXT's floodlit world, staged, with two material reliefs. Chassis assets/js/deck/2026-10-24-apron.js: key az -58 el 25, chassis models plant_bay, plant_wall, line_carrier, bollard, anchor_bolt_set, tool_crate, tripod_work_lamp, megapack_unit, steel_frame and covered_pod, chalk tilt up panels, galvanized steel, warm 3500K bay light, bluebonnet tape.",
 "structural_laws": [
  "A CAMERA LOOKING INTO THE KEY SILHOUETTES ITS SUBJECT. The dark bay's bolts read black until the camera turned to stand in the door with the flood over its shoulder.",
  "A KIT CAR UNDER A CLOTH IS STILL THE KIT CAR. Draping the merged crossover kept its mirrors, glass and seams; only a lofted shell with no car beneath read as covered.",
  "A LIT MATERIAL ACCENT LEAVES THE ACCENT BAND. Satin tape took the key and the lamps and fell out of the 12 Lab unit band on two frames, so the tape stays a flat accent fill.",
  "A BOTTOM VEIL EATS A TAPE NEAR THE FOOTER. The taped pads near the foot of a frame fell to navy under the veil and foot wash.",
  "A PER LINE KNOCK BEHIND THE FOOTER READS AS A SMUDGE ON A LIT APRON. The full width foot wash replaced it."],
 "techniques": [
  "a crane eye on a 80 m tilt up wall, four lit bays and one dark bay, the apron under the flood",
  "the first lit bay from its threshold, three bodies on carriers",
  "a material relief of three milled channels at one scale, stop blocks inside each length",
  "five battery enclosures in a row on the apron, the wall and its lit doors behind",
  "the dark bay from its door, galvanized anchor bolts in a taped pad, crates, unlit lamps",
  "a material relief of two finned blocks and an offcut on blackened steel, the 400 MW plan an empty taped groove",
  "an unclad primed steel frame on two empty taped pads",
  "a covered car on its carrier just inside the lit third bay",
  "the wall from its dark end, two lamps on the taped threshold"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A staged floodlit deck."},
 "accent": {"hex": "#4E5FA8", "name": "bluebonnet tape", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "Tape on what is planned or under construction, not yet installed."},
 "ground": {"hex": "#08060F", "note": "The floodlit world's black sky and dark apron."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
add("captions", {"date": D, "carousel_no": N, "opening_move": "the quiet decision", "structure": "Ledger",
 "closing_move": "Ask the one question the decision leaves open.",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": (OUT / "captions" / "critic_note.txt").read_text().strip()[:900],
 "move_note": "Opens on where robot production began, a fact settled with no announcement, then lays out what the table says, the Optimus row at Construction and the vehicle and Megapack rows at Production, then what it does not, since installed capacity is not output, and to the vehicle and Megapack rows at Production, then the footnote that installed capacity is not output, and closes on how much Tesla actually made in Texas."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
