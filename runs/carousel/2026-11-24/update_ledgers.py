#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-24, carousel no. 86. Appends one entry to each variety ledger,
the artwork values measured off the final renders by deck_coherence and layout_check's own
functions, the caption's counts measured off caption.txt. Then ledger_check --derive rewrites the
caption exclusion lists."""
import json, re, sys, subprocess
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] if HERE.parent.name == "out" else HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts/carousel"))
import deck_coherence as DC, layout_check as LC
STRUCT = json.loads((Path(__file__).resolve().parent / "structural_laws.json").read_text()) if (Path(__file__).resolve().parent / "structural_laws.json").exists() else []
from PIL import Image
D, N = "2026-11-24", 86
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0258", "related_items": ["tx-2026-0254", "tx-2026-0253"],
 "instrument": "Texas A&M's November 24th release on CLARKE and the CLARKE project site at clarke.crasar.org, fetched November 24th, 2026.",
 "topic": "Texas A&M developed CLARKE, an AI tool that stitches drone imagery into an orthomosaic, rates the damage to each building in a color coded view and finds damaged roads so crews can route around them, with a trained operator reviewing every assessment. Its developers say minutes instead of 18 to 24 hours. It learned from more than 21,000 damaged homes in 10 disasters, Harvey among them, 125 responders from 63 agencies have trained on it, and Texas A&M says Florida's state drone team made it standard operating procedure. The release and the project site name no Texas user.",
 "angle": "Every roof, read. A drawn Gulf Coast neighbourhood goes through every state the tool puts it through, loose drone frames, a stitched map, every roof judged in a cool ramp, a person's check that turns hollow rims filled, a gold route around a fallen oak, and frame 1's camera over undamaged Texas ground at the close.",
 "angle_note": "The colour code is three cool steps with no legend or class name, because the classes are not public. Gold means only the way through. No ratio of the two timings is printed. The absence is scoped to the two documents.",
 "entities": ["Texas A&M University", "CLARKE", "CRASAR", "Tom Manzini", "David Merrick", "FL-UAS1", "Semafor", "National Science Foundation", "AI Institute for Societal Decision Making"],
 "places": ["Texas", "College Station", "Brazos County", "Florida", "Pennsylvania"],
 "what_was_refused": "the damage classes, any time per flight, any accuracy figure, the AAAI paper behind a bot wall, the unconfirmed game changer line, and any claim that Texas does not use the tool.",
 "keywords": ["CLARKE", "drone imagery", "damage assessment", "orthomosaic", "disaster response", "Hurricane Harvey", "Texas A&M", "emergency management"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "BESPOKE, LOOK V2 wonder tone, nine slide artists. A Gulf Coast subdivision aerial with hollow rims (1), a rural road of hour markers (2), a relief of drone frames stitching into one plane (3), one damaged roof (4), a plate archive (5), an operator at a tailgate (6), a bucket truck routing around a fallen oak (7), a helmet wall (8) and frame 1's camera over Texas ground (9). Spine assets/js/deck/2026-11-24-roofread-bespoke.js with chassis models downed_oak, rescue_helmet, ortho_plate, plate_rack, survey_quad and helpers lots, carpet, rims, route, roofDamage.",
 "structural_laws": STRUCT,
 "techniques": ["an instanced 2,000 roof aerial with hollow cool rims", "hour markers on a long lens road", "a stitching relief of anodised plates", "a stripped roof with decking and a tarp", "a raked archive of anodised plates", "a screen lit operator at dusk", "a gold route tube around a fallen oak", "a counted helmet wall", "a mirrored aerial on undamaged ground"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders."},
 "accent": {"hex": ACC, "name": "wonder gold", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The way through, the route around damaged roads, only."},
 "ground": {"hex": "#3f7d3a", "note": "St. Augustine lawn and gumbo clay under the wonder tone's cobalt and peach."}})
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
