#!/usr/bin/env python3
"""update_ledgers.py for 2026-10-29, carousel no. 62. Appends one entry to each variety ledger,
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
D, N = "2026-10-29", 62
OUT = ROOT / "out" / D
L = ROOT / "ledger/carousel"
def add(name, entry):
    p = L / f"{name}.json"; t = json.loads(p.read_text())
    t["entries"] = [e for e in t["entries"] if e.get("date") != D] + [entry]
    p.write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n")
frames = [OUT / "render" / f"slide-{i:02d}.png" for i in range(1, 10)]
med = [round(DC.median_lstar(f), 1) for f in frames]
d = [abs(a - b) for a, b in zip(med, med[1:])]
acc = [round(LC.accent_coverage(Image.open(f).convert("RGB"), "#6E7A5A"), 4) for f in frames]
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0233", "related_items": ["tx-2026-0187", "tx-2026-0152"],
 "instrument": "Soluna's release of October 21st, 2026 on its definitive agreement with Applied Digital, its September 14th and August 24th releases on Project Dorothy and the Dorothy 3 land, and the Briscoe County Public Notices page, all fetched October 29th, 2026.",
 "topic": "Soluna and Applied Digital agreed to form a joint company to develop a planned 50 MW AI data center at Dorothy 3 near Silverton, beside the 150 MW Briscoe Wind Farm Soluna owns. Applied is expected to hold 51 percent. Closing depends in part on a Briscoe County tax abatement and is expected by year end. ChronoScale, majority owned by Applied, signed a non-binding letter of intent to lease. Soluna describes Dorothy 3 as up to 300 MW on 397 acres across the road from the wind farm's substation, and expects Phase 1 to draw from both the wind farm and the grid.",
 "angle": "Rendered in the lastLight world along a single county road on the Caprock: a turbine at last light, Briscoe County raised as a caliche relief, the existing hall's bays lit by the energized share, a transformer's radiators across the road from the pasture, the wind's tower sections stacked beside the plan's at twice the height, survey stakes for Phase 1 before the substation with its wood and lattice lines, the parcel drawn to area, a padlocked ranch gate, and the county courthouse at night.",
 "angle_note": "Every frame is drawn to illustrate. No turbine model, site plan, connection design or parcel shape is in the record. Tower sections, stakes and bays are drawing units of 10 MW. Silverton's pin is the Census gazetteer point.",
 "entities": ["Soluna Holdings", "Applied Digital", "ChronoScale", "Briscoe Wind", "Briscoe County Commissioners Court"],
 "places": ["Silverton", "Briscoe County"],
 "what_was_refused": "any statement that the abatement was granted or scheduled, a split of Phase 1's power between wind and grid, the ERCOT Batch Zero classification as more than conditional, a lease as signed, and the parcel's real shape.",
 "keywords": ["Soluna", "Applied Digital", "Briscoe Wind", "behind the meter", "tax abatement", "Dorothy 3", "AI data center", "Silverton"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "SPATIAL SCENES in TXT's lastLight world, staged, with two TXBENCH material reliefs. Chassis assets/js/deck/2026-10-29-caprock.js: key az -78 el 10, chassis models tower_section, section_stack, survey_stake, gate_lock, radiator_bank and intake_bays, white tower paint, lit galvanized flanges, caliche, red bed earth and a mesquite accent for what is planned.",
 "structural_laws": [
  "A STACK OF SHORT CANS READS AS A SILO. At 1 m a section on a 4.3 m diameter the columns read as grain bins; at 3 m a section the thirty stand at a kit turbine's hub height and taper at its rate, and read as towers.",
  "A FRAME FACING THE LOW SUN IS A HAZE FIELD. The power frame looking into the key was a grey middle; turned north west with the sun off the frame, the substation read.",
  "A RELIEF CASTS ONLY DOWNWIND OF ITS KEY. Briscoe's plateau cast only east, so a tighter crop that left less ground east of it cut the cast fraction under the floor.",
  "MICRO HEIGHT UNDER A 10 DEGREE KEY IS A CAMOUFLAGE PRINT. Noise in a relief's height cast long blotches; the grain belongs in the albedo.",
  "A KIT MODEL'S MERGED WINDOW MESH LIGHTS EVERY PANE OR NONE. The courthouse could not show one lit window."],
 "techniques": [
  "a kit turbine at last light over a caliche county road and a barbed wire fence",
  "Briscoe County raised as a caliche relief among red bed neighbours with Silverton's pin and a square of the acres at map scale",
  "a data hall's ten intake bays lit one per 10 MW, the last filled to its fraction, wind turbines behind",
  "a transformer's radiator bank close at the lower left, the county road and the pasture fence beyond",
  "the wind's fifteen tower sections beside the plan's thirty, a worker at their feet and a turbine at their depth",
  "survey stakes on the pasture for Phase 1 before the substation with a wood line from the left and a lattice line from the right",
  "the parcel in plan as a relief, the 300 acres in disked red earth and the 97 acre L lit in the accent",
  "a padlocked double ranch gate across the caliche entrance, its leaves at 51 and 49",
  "the county courthouse at night with a resident on the walk"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A staged lastLight deck."},
 "accent": {"hex": "#6E7A5A", "name": "mesquite, what is planned", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The planned column's bands on 5, the stake tops and flagging on 6, the 97 acre L on 7, the padlock tag on 8."},
 "ground": {"hex": "#08060F", "note": "The lastLight world's dark sky."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
win = json.loads((OUT / "captions" / "winner.json").read_text())
add("captions", {"date": D, "carousel_no": N, "opening_move": win["opening_move"], "structure": win["structure"],
 "closing_move": win["closing_move"],
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": win.get("why_this_opening", "")[:900],
 "move_note": "Opens on the substation across from 397 acres, then zooms in from the deal to Phase 1, the land and the wind farm, then the county condition, and closes on which public body decides the abatement and when."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
