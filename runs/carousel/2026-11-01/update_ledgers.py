#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-01, carousel no. 65. Appends one entry to each variety ledger,
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
D, N = "2026-11-01", 65
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0229", "related_items": [],
 "instrument": "Texas A&M Engineering news of October 22nd and September 4th, Texas A&M Stories of October 26th, and the NSF Award API record for award 2534344, all fetched November 1st, 2026.",
 "topic": "A $2 million WoodNext Foundation grant will help Texas A&M build the Aggie AI Foundry, where computer controlled arms are to mix, melt and test new alloys, because the university says existing self driving labs can't handle alloys at up to 3,000 degrees Celsius. A separate NSF award has obligated $4.1 million of an estimated $24.9 million for the open access Autonomous Robotic Metallurgist, running September 1st, 2026 to August 31st, 2032.",
 "angle": "One alloy followed through its states in a dark lab: a button glowing in a water cooled copper hearth among cooled ones, five powder heaps, a tray of twenty buttons for the grant, the line of crucible, hearth and grips, a button on a hundred offprints, two trays at one unit for the two funders, a rack of seventy two bars for the award's months, the etched section of a button, and the pulled bar broken in two.",
 "angle_note": "Every frame is drawn to illustrate. One button is $100,000, one bar is one month and one sheet is one paper, each counted by compute.py. No person is drawn.",
 "entities": ["Texas A&M University", "Texas A&M Engineering Experiment Station", "WoodNext Foundation", "National Science Foundation", "Roku"],
 "places": [],
 "what_was_refused": "any opening date or construction timeline for the foundry (no source gives one), any claim that the foundry runs today, and the goal of a week or less stated as a result.",
 "keywords": ["Texas A&M", "Aggie AI Foundry", "self driving lab", "alloys", "NSF", "materials science", "PhaseForge", "WoodNext Foundation"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "SPATIAL SCENES in a dark TXT.interior lab, staged, with four TXBENCH material reliefs. Chassis assets/js/deck/2026-11-01-foundry.js: copper_hearth, alloy_button, sample_tray, tensile_bar, crucible, robot_arm, offprint_stack and steel_rule, true metal copper with its own studio reflection, and bluebonnet as the one accent for the same alloy.",
 "structural_laws": [
  "A RASTERISED METAL REFLECTS ONLY ITS ENVIRONMENT. Copper with a grind painted into its colour read as walnut until it was metalness 1 with the grind in its roughness and a softbox on the camera's mirror ray.",
  "A PRACTICAL LIGHT A FEW CENTIMETRES FROM A DOME SATURATES IT. The hot button's point light clipped its neighbours' facing sides into hard stepped edges until it was cut to a quarter.",
  "A SHADOW CAMERA'S NEAR PLANE AT ITS TARGET CLIPS WHAT STANDS ABOVE IT. A rig distance of half a metre put the near plane at the bench and broke every dome's shadow into blocks.",
  "THE GRADE'S BLOOM SAMPLES A QUARTER RESOLUTION BUFFER. On a dark macro it laid square cells round every bright dome edge, so a macro frame passes bloom strength zero.",
  "A SECOND BOX BUTTED ON A BLOCK IS A SEAM. The hearth was made one deep block with its pockets offset back rather than a block and an extension."],
 "techniques": [
  "a low macro over a water cooled copper hearth, one button glowing among nineteen cooled ones",
  "five powder heaps as a raking material relief, graphite, copper, nickel, titanium and brass",
  "a sample tray of twenty buttons, one per $100,000 of the grant",
  "the line of crucible, hearth and grips with a six axis arm, labelled mix, melt and test",
  "one button on a stack of a hundred offprints, the accent band on its flank",
  "two trays at one unit, twenty buttons for WoodNext and forty one of two hundred forty nine for NSF",
  "a rack relief of seventy two tensile bars in rows of twelve, one a month",
  "an etched section of a button with dendrites standing proud, the accent across the mount",
  "a pulled flat tensile bar broken in two as an orthographic relief, the accent on its grip"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A staged dark lab."},
 "accent": {"hex": "#4E5FA8", "name": "bluebonnet, the same alloy", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The band on the button over the papers, the mark across the section's mount and the paint on the broken bar's grip."},
 "ground": {"hex": "#08080B", "note": "The dark lab and the reliefs' black phenolic."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
add("captions", {"date": D, "carousel_no": N, "opening_move": "the plain question", "structure": "Pivot",
 "closing_move": "point at the record, plainly, without a call to action",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": "Opens on the question a reader would ask of an AI lab with a furnace, pivots from the software claim to the physical line, and closes on the award record's named users.",
 "move_note": "Opens asking why an AI lab melts metal, gives the trillion mixes and Arróyave's limit, then the grant, the line and the goal stated as a goal, then the separate NSF award, and closes asking who outside Texas A&M makes the first alloy."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
