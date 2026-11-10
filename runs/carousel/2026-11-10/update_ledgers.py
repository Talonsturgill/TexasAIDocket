#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-10, carousel no. 73. Appends one entry to each variety ledger,
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
D, N = "2026-11-10", 73
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0245", "related_items": ["tx-2026-0125"],
 "instrument": "The Texas Advanced Computing Center's October 29th, 2026 account of its September symposium for Texas researchers, carried in full by HPCwire, with TACC's 2023 and 2024 Vista releases and its 2020 Frontera expansion release as carried by HPCwire, the TOP500 Frontera entry and the GROMACS home page, fetched November 10th, 2026.",
 "topic": "TACC retired Frontera in October 2026 after more than eight million jobs and over seven years of production. A UT Southwestern Medical Center lab that typically ran a 5.3 million atom membrane fusion simulation on 64 Frontera CPU nodes at 43 nanoseconds a day says eight GPU nodes of TACC's Vista gave almost the same speed, after a lot of GROMACS tuning with TACC staff. Horizon, the successor, is in early operations.",
 "angle": "One machined tray per node: 64 brushed steel trays in eight open towers against one tower of eight black trays with cyan light bars in a dark machine hall, the open Frontera node's two copper heat sinks, the count in plan, the membrane fusion system as a metal section relief before and after the SNAREs mix the cores, the pulled Vista tray, eight cells raised among Vista's 860, Horizon as the same tower half filled with unlit trays on an opened floor, and Frontera dark beyond the lit eight.",
 "angle_note": "One tray per node, drawn to illustrate, never TACC's room. No speed is drawn anywhere: Vista's speed is Rizo-Rey's spoken almost the same speed. The molecules are drawn to illustrate, never the lab's structure. No Vista GPU node count and no Frontera node count at retirement are stated.",
 "entities": ["Texas Advanced Computing Center", "The University of Texas at Austin", "UT Southwestern Medical Center", "Frontera", "Vista", "Horizon", "NSF Leadership-Class Computing Facility", "GROMACS", "NVIDIA GH200", "Oden Institute"],
 "places": ["Austin"],
 "what_was_refused": "any Vista speed figure, any Vista GPU node count, Frontera's node count at retirement, one superchip per node, the J.J. Pickle Research Campus, and UT Southwestern's city, which no fetched source states.",
 "keywords": ["TACC", "Frontera", "Vista", "Horizon", "supercomputer", "GPU nodes", "UT Southwestern", "membrane fusion", "SNARE", "GROMACS", "research computing"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "A MIX. Spatial scenes in one windowless machine hall under a cold flood in the floodlit world (frames 1, 2, 6, 8 and 9, TXT.interior with no ceiling, the flood high on the upper left) and TXBENCH material reliefs in steel, graphite, black anodise and copper (3, 4, 5 and 7). Chassis assets/js/deck/2026-11-10-tray.js: compute_tray (cpu stainless with an open state, gpu black anodise with a cyan light bar), tray_tower, raised_floor and equipment_crate (built, cut from frame 8 in panel round 2), with comal_lit cyan as the one accent for a Vista GPU node.",
 "structural_laws": [
  "A THIN LIGHT BAR VANISHES AT FEED SIZE. A 5 mm strip read at full size and measured nothing at the 216 px accent thumb; a bar a third of the bezel tall, unlit and outside the tone curve, carries the hue.",
  "A BLACK SUBJECT ON A DARK FLOOR BREAKS INTO DUST. The silhouette gate reads the subject against the median outside its rect, so a black tower only counts once a flood lights the floor round it.",
  "A RAISED FLOOR'S FRONT EDGE STRIKES THE SITE LINE. Extend the floor past the camera rather than wash the edge out.",
  "THE PRESET'S COLD FILL TINTS A FLOOR PERIWINKLE. Cut the non-shadow fill and the floor reads graphite.",
  "EMITTED LIGHT ON A RELIEF IS LAID ON AFTER THE WASHES. Under the footer wash and vignette the far LEDs dimmed to teal."],
 "techniques": [
  "eight open towers of eight steel trays against one black tower of eight with cyan light bars, high three quarter",
  "one Frontera tray open on the floor, two copper heat sinks of thin fins, macro",
  "64 steel tray fronts and eight black ones in plan on a graphite carrier",
  "a membrane section in metal: steel heads, graphite core, four copper SNARE bundles",
  "the same section with the outer head rows curled round a fusion neck and the cores run through it",
  "the black tower with its top tray pulled out on its rails",
  "860 graphite cells with eight raised and cyan topped",
  "an empty tower frame in the pool, three unlit trays at its foot and a fourth sliding in, whips running to it from the open row",
  "the cover's hall from tray height, Frontera's towers dark beyond the lit eight"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders."},
 "accent": {"hex": "#8FE0F0", "name": "comal_lit, a Vista GPU node", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The black tower's bars on 1, 6 and 9, the light bars on 3's black row, the eight raised cells on 7."},
 "ground": {"hex": "#1A1C20", "note": "The graphite raised floor and the relief carrier."}})
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
