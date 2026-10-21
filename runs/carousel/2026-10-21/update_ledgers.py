#!/usr/bin/env python3
"""update_ledgers.py for 2026-10-21, carousel no. 56. Appends one entry to each variety ledger,
the artwork values measured off the final renders by deck_coherence and layout_check's own
functions, the caption's counts measured off caption.txt. Then ledger_check --derive rewrites the
caption exclusion lists."""
import json, re, sys, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/carousel"))
import deck_coherence as DC, layout_check as LC
from PIL import Image
D, N = "2026-10-21", 56
OUT = ROOT / "out" / D
L = ROOT / "ledger/carousel"
def add(name, entry):
    p = L / f"{name}.json"; t = json.loads(p.read_text())
    t["entries"] = [e for e in t["entries"] if e.get("date") != D] + [entry]
    p.write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n")
frames = [OUT / "render" / f"slide-{i:02d}.png" for i in range(1, 10)]
med = [round(DC.median_lstar(f), 1) for f in frames]
d = [abs(a - b) for a, b in zip(med, med[1:])]
acc = [round(LC.accent_coverage(Image.open(f).convert("RGB"), "#8FE0F0"), 4) for f in frames]
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0225", "related_items": ["tx-2026-0204", "tx-2026-0084"],
 "instrument": "Lockheed Martin's October 14th, 2026 release on its Grand Prairie expansion, Hadrian's home page, Series C post and press page, Lockheed's PAC-3 page and a TDLR accessibility filing, all fetched October 21st, 2026.",
 "topic": "Lockheed Martin says Hadrian will bring a highly automated 24 machine cell to its Grand Prairie missile plant, expected in early 2027 and run by Lockheed's own workforce, inside a $300 million expansion past 735,000 square feet that has already added more than 30 machines and expects nearly 100 by the end of 2026. Hadrian calls its own factories and its software Opus AI powered. The release never says what AI would do in this cell.",
 "angle": "Rendered in the lastLight world inside a machine shop: a vise and a finished pocketed housing under the spindle for the cover, a plan relief of the slab, the fresh pour behind timber forms and the carpet tile with a rolled corner as squares at a single scale, a foam tray of 312 parts with a part lifted out, a converted room of 30 machining centres with a machinist, 100 machines from above, the same 100 beside 24 empty taped bays in the accent, a cyanotype drawing of the part with the part standing on it, the dark pendant screen, and the 24 empty bays at standing eye with Lockheed's machines lit along the wall.",
 "angle_note": "Every frame is drawn to illustrate. One pocket is one part, one machine is one machine and one bay is one of the cell's 24, all from figures.json. The housing is an illustrative part, never a PAC-3 component, and no product, logo or real interior is depicted.",
 "entities": ["Lockheed Martin", "Hadrian", "Opus", "Missiles and Fire Control"],
 "places": ["Grand Prairie", "Dallas County", "Texas"],
 "what_was_refused": "Anything about what AI does inside the cell, which no source says. The 2,000 Texas jobs are kept as the company's statewide figure, never Grand Prairie's. The 24 are never added to the nearly 100. Dallas tx-2026-0179 was refused by the 30 day rule.",
 "keywords": ["Lockheed Martin", "Hadrian", "Grand Prairie", "machining cell", "automation", "missiles", "manufacturing", "AI", "Opus", "Dallas County"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by out/2026-10-21/update_ledgers.py.",
 "register": "SPATIAL SCENES in TXT's lastLight world inside TXT.interior machine shop rooms with four material reliefs. Chassis assets/js/deck/2026-10-21-cell.js: key az -64 el 9, four chassis models (a pocketed housing part, a machine vise, a vertical machining centre with door, spindle, tool drum, pendant on a swing arm and stack light, an empty machine bay) and a relief vocabulary of epoxy, slab, pour, carpet, foam, granite and cyanotype.",
 "structural_laws": [
  "A HEIGHT NOISE UNDER A KEY NINE DEGREES UP TURNS TO BLOTCHES. On a relief lit that low, surface tooth belongs in albedo, never in height.",
  "A WIDE AERIAL OF 100 INSTANCED MACHINES MERGES INTO ONE SILHOUETTE AT THUMB SCALE. A count of that size reads as a block, so plan it as a DIAGRAM half, not a GRID.",
  "THE TONE CURVE GREYS A THIN ACCENT. Tape drawn through MeshStandardMaterial reads as grey at 432 px; draw it in MeshBasicMaterial with toneMapped false.",
  "K.make RE-CENTRES A MODEL'S FOOTPRINT. A machine whose table and vise are placed in model coordinates needs keepOrigin.",
  "TXT.interior's FLOOR Z FIGHTS A SECOND GROUND AT LONG RANGE. Lift the ground and everything on it 0.2 m in a wide aerial."],
 "techniques": [
  "a vise holding a finished pocketed housing under the end mill in an open machining centre, chips laid on the T slot table",
  "a plan relief of three floor finishes as squares at one scale, a fresh pour inside timber forms and carpet tile with a rolled corner",
  "a plan relief of a foam kitting tray of 312 parts in rows of 24, one pocket empty and its part on the bench, the next tray running off the edge",
  "a converted room of 30 machining centres in two rows with a machinist for scale under the aisle's high bay",
  "100 instanced machining centres from a steep aerial in ten rows of ten",
  "the same 100 beside 24 empty taped bays in the accent across one aisle",
  "a cyanotype third angle drawing of the part with hidden lines and a detail, the part standing on its own plan view",
  "the control pendant close on its swing arm, its screen dark",
  "24 empty taped bays at standing eye, a machinist on the near row, Lockheed's machines lit along the east wall"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A staged lastLight machine shop deck."},
 "accent": {"hex": "#8FE0F0", "name": "comal lit", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "Hadrian's cell only: the bay tape and the drawing's title tab."},
 "ground": {"hex": "#08060F", "note": "The lastLight world's black field around the stage."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
add("captions", {"date": D, "carousel_no": N, "opening_move": "the correction", "structure": "Two columns",
 "closing_move": "name what is still not public, and how big that is",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": (OUT / "captions" / "critic_note.txt").read_text().strip()[:900],
 "move_note": "Opens on the correction that the release gives AI no job, sets what is announced beside what Lockheed says is already done, names what Hadrian says of its own factories and closes on how many of the 24 machines will use AI."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
