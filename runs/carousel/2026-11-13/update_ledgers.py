#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-13, carousel no. 76. Appends one entry to each variety ledger,
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
D, N = "2026-11-13", 76
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0072", "related_items": ["tx-2026-0143", "tx-2026-0187"],
 "instrument": "ERCOT's preliminary summary of the Data Center State and Community Impact RFI for the PUC open meeting of November 5th, 2026, ERCOT's November 5th, 2026 Batch Zero eligibility verification update, market notice M-B091426-01 of September 14th, 2026 and the PUC open meeting calendar, all fetched November 13th, 2026.",
 "topic": "ERCOT issued its Data Center State and Community Impact RFI to 465 loads and 433 answered, covering about 177 GW, 97 percent of requested capacity. All 245 Large Loads responded. West Texas holds 41 percent of capacity, 73 GW. Respondents answered 83 percent of nearly 67,000 questions and cooling questions drew N/A answers at the highest rate, fourth by count, with many projects not yet settled on a cooling configuration. Projects due in 2028 or later answered N/A 30 percent more often. In the separate Batch Zero verification ERCOT reviewed 257 developers and expects to send 80 percent a second round. A final report is targeted for December 10th, 2026.",
 "angle": "A cooling yard at last light: four poured equipment pads with ember layout lines, bolts and capped conduit stubs and nothing on them, a primer steel frame up behind, 245 cable reels for the Large Loads, a 177 lamination copper bus pack for the gigawatts, four zone packs, a trench grated for 83 percent of its length with its last stretch open in ember, two rows of capped stubs for the 2028 figure, an official at a plan table under a work light, and the yard seen from the gate.",
 "angle_note": "The pads, reels, packs and trench are drawn to illustrate, one reel per Large Load, one lamination per GW and one grated share per answered share. No real site is depicted. The summary gives no cooling share as a number, so no frame prints one.",
 "entities": ["ERCOT", "Public Utility Commission of Texas", "Texas Water Development Board", "Office of the Governor"],
 "places": ["Texas", "West Texas", "Houston"],
 "what_was_refused": "cooling as the largest share of unanswered questions (fourth of five by count, first by rate, computed from the summary's tables after the integrity judge refuted the first wording), a cooling share as a percentage, any count of projects without a cooling design, any statement about water use, and any join between the Batch Zero verification and the RFI answer rates.",
 "keywords": ["ERCOT", "data centers", "large loads", "RFI", "cooling", "Batch Zero", "PUCT", "West Texas", "interconnection"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "A MIX. Spatial scenes in the staged lastLight world on one cooling yard at last light (1 to 4 and 6 to 9) and a TXBENCH material relief of a grated trench (5). Chassis assets/js/deck/2026-11-13-coolingyard.js: equipment_pad, bus_pack, cable_reel, cable_trench, plan_table and work_light, and a cutGround helper that opens the caliche over a sunk trench.",
 "structural_laws": [
  "THE KIT BAKE COLLAPSES AN INSTANCEDMESH TO ITS FIRST INSTANCE. A pack of bars is separate meshes merged per material with K.merge.",
  "K.MAKE RE-CENTRES A MODEL ON ITS FOOTPRINT. A frame places a model by its centre and takes its run direction from its quaternion.",
  "A LOW KEY BEHIND THE CAMERA'S SUBJECT LEAVES EVERY CAMERA-FACING FACE DARK. Every frame looks with the key on its left.",
  "A TRENCH BUILT ON GRADE READS AS A RAISED WALKWAY. It sinks below grade and the ground shader discards over its footprint.",
  "A PROPORTION DRAWN BESIDE UNSCALED OBJECTS BECOMES A COMPARISON. Frame 6 set a trench for the unanswered share beside four cooling pads and read as cooling larger than the whole, so the pads stand alone as a place.",
  "A HIGHLY METALLIC COPPER UNDER A DARK SKY READS AS MAHOGANY. The copper is half metallic and the spacer every tenth bar is drawn wider and proud so the tens read at feed size."],
 "techniques": [
  "four empty pads with a primer frame behind at last light",
  "245 instanced reels with the front block in a pool",
  "one 177 lamination bus pack beside a worker",
  "four zone packs at one depth on one dunnage line with labels on one baseline",
  "a grated trench relief with its open stretch in ember",
  "the yard from 9 m up, four empty pads in a row in the pool and a worker on the nearest",
  "one pad at ankle height with two rows of capped stubs, the later row longer by the 2028 N/A figure, and a reel",
  "an official at a plan table under a work light in a bay",
  "the yard from beyond a ranch gate, the empty pads in the pool"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders."},
 "accent": {"hex": ACC, "name": "dusk_ember, left blank", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The pad layout lines and conduit caps, the open trench stretch."},
 "ground": {"hex": "#17150F", "note": "Caliche at last light."}})
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
