#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-12, carousel no. 75. Appends one entry to each variety ledger,
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
D, N = "2026-11-12", 75
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0188", "related_items": ["tx-2026-0206", "tx-2026-0209"],
 "instrument": "The Texas Department of Motor Vehicles' Company and Vehicle Summary Report, data as of October 29th, 2026, its Automated Vehicles Regulatory Program page and its adoption of 43 TAC Chapter 220, with Volvo Group's October 5th, 2026 and Kodiak AI's October 8th, 2026 releases, all fetched November 12th, 2026.",
 "topic": "The Texas Department of Motor Vehicles' Company and Vehicle Summary Report, data as of October 29th, 2026, lists 17 companies and 3,164 automated vehicles under the authorization Senate Bill 2807 requires for commercial operation since May 28th, 2026. Waymo lists 1,259 and Tesla Robotaxi 1,080, 74 percent between them, and 14 companies list fewer than 100. The authorization carries no fee and doesn't expire. Dallas asked the department to require crash history and the department said the Transportation Code doesn't allow it. Volvo says its Waabi hauls run with an observer in the driver's seat and Kodiak and Charger with a safety driver.",
 "angle": "The roster, parked: one stand-in car per ten listed vehicles in rows of ten bays at last light, Waymo and Tesla Robotaxi as two long columns, a dusk_gold stripe, the fifteen packed in rank order behind white dividers, the last car alone in its row, a steel rule with a stop at May 28th and no end stop, Dallas on the seam behind the tail, a stopped car at a crosswalk, a person in a sleeper cab's driver's seat, and a person outside the fence.",
 "angle_note": "Every car is a neutral stand-in drawn to illustrate, one per ten listed vehicles rounded half up and never fewer than one. The report names no routes or vehicle types, so no car is drawn as a truck or a robotaxi of any maker. The freight statements are kept apart from the roster rows. No source says whether the public can look up an authorization, so the deck says neither.",
 "entities": ["Texas Department of Motor Vehicles", "Waymo", "Tesla Robotaxi", "Avride", "Aurora", "Kodiak", "Waabi", "Volvo", "Charger USA", "City of Dallas", "City of Austin", "Department of Public Safety"],
 "places": ["Texas", "Dallas", "Houston", "Laredo"],
 "what_was_refused": "a join of the Volvo/Waabi and Kodiak/Charger runs to the roster's rows, Atlas Energy Solutions' 38 as Kodiak trucks, any public lookup of an authorization, and any count of listed vehicles running with nobody aboard.",
 "keywords": ["TxDMV", "automated vehicles", "driverless", "authorization", "SB 2807", "Waymo", "Tesla Robotaxi", "robotaxi", "crash history", "autonomous trucks"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "A MIX. Spatial scenes in the staged lastLight world on one parked lot at last light (1 to 4, 6, 7 and 9), the kit semi_cab_interior (8) and a TXBENCH material relief of a stainless rule on a rubber mat (5). Chassis assets/js/deck/2026-11-12-roster.js: fleet_lot (the roster parked at one stand-in kit crossover per ten listed vehicles, instanced from one baked model per material, rows of ten bays, stall bars, wheel stops, white company dividers and a dusk_gold stripe) and wheel_stop (precast curb stop), with a glass environment that carries the warm seam.",
 "structural_laws": [
  "K.MAKE RE-CENTRES A MODEL THROUGH AN INNER GROUP. A plan's local coordinates don't survive TXT.add, so a frame takes the offset from the world bounding box, never from localToWorld on the outer group.",
  "A LOT LAID ONE COMPANY TO A ROW MAKES THE SMALL COMPANIES THE LONGEST COLUMN. The fifteen are packed in rank order so a column's depth is its share.",
  "COATED GLASS UNDER A DARK SKY READS AS A FLAT SLAB. The glass takes its own environment with a warm horizon band.",
  "A CAMERA LOOKING TOWARD PLUS Z FLIPS THE PLAN LEFT FOR RIGHT. Frame 9 placed its person by unprojecting a screen point onto the ground rather than by world coordinates.",
  "A TRANSPARENT FENCE MESH DRAWS OVER A FIGURE IN FRONT OF IT. The mesh is alpha tested with depth on."],
 "techniques": [
  "the first stand-in at its front quarter from 3.8 m with rows of identical sensor-topped cars receding behind",
  "the whole lot through a long lens from 230 m, three columns from one front baseline, a gold stripe, a pool on the asphalt",
  "the third column from in front, labels in a column on the left with elbow leaders to each company's run",
  "the last row at eye level, one car beside open bays with wheel stops casting",
  "a stainless rule relief, a stop block at May 28th, one graduation a day to a gold groove, grooves off the edge",
  "the tail of the lot through a 16 degree lens with Dallas hazed on the seam",
  "a stand-in stopped behind a stop bar and a person past its nose on a worn crosswalk",
  "a person in a sleeper cab's driver's seat from the passenger side, cap, the wheel",
  "a person outside a chain link fence at the lot's tail, the last car and the long columns beyond"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders."},
 "accent": {"hex": ACC, "name": "dusk_gold as rendered, where the two largest names end", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The stripe on 2, 3 and 9, the report date groove on 5."},
 "ground": {"hex": "#16171B", "note": "Asphalt blue black."}})
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
