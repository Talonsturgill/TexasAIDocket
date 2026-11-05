#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-04, carousel no. 68. Appends one entry to each variety ledger,
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
D, N = "2026-11-04", 68
OUT = ROOT / "out" / D
L = ROOT / "ledger/carousel"
def add(name, entry):
    p = L / f"{name}.json"; t = json.loads(p.read_text())
    t["entries"] = [e for e in t["entries"] if e.get("date") != D] + [entry]
    p.write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n")
frames = [OUT / "render" / f"slide-{i:02d}.png" for i in range(1, 10)]
med = [round(DC.median_lstar(f), 1) for f in frames]
d = [abs(a - b) for a, b in zip(med, med[1:])]
acc = [round(LC.accent_coverage(Image.open(f).convert("RGB"), "#E0956A"), 4) for f in frames]
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0240", "related_items": [],
 "instrument": "Permian Resources' third quarter 2026 results release as filed with the SEC on November 4th and its 2025 annual report on Form 10-K, with the Texas Tribune's May 21st report on the Railroad Commission, all fetched November 5th, 2026.",
 "topic": "Permian Resources' third quarter 2026 release says its production operations team has deployed an AI-powered artificial lift monitoring system to increase runtime and that it is integrating its subsurface data with large language models for wellbore placement and drilling parameters. It prints no measured result for either. Output averaged 457,528 barrels of oil equivalent a day, up 22% on the quarter, 208,029 barrels of it crude. Its 2025 annual report puts about 67% of its net leasehold in Texas and names Reeves County. The Railroad Commission told the Texas Tribune in May it was not aware of any AI use by oil and gas companies.",
 "angle": "A pump jack at last light, followed from its pad to the lease gate. The release page with pencil brackets, the carrier bar and chrome rod, a cutaway block with the lateral and its leaders, sucker rods at the quarter's ratio, a stock tank gauge at the crude share, pipe racks at the leasehold split, a steel tape of daily graduations, and a worker outside a closed lease gate.",
 "angle_note": "No well, lease or tank is identified, because the release names none. Every frame is drawn to illustrate. The rods, racks and tape are drawing units that carry computed ratios and counts, never physical quantities.",
 "entities": ["Permian Resources", "Railroad Commission of Texas", "The Texas Tribune"],
 "places": ["Reeves County", "Delaware Basin", "West Texas", "Southeast New Mexico"],
 "what_was_refused": "any runtime figure for the monitor, any count of monitored wells, any attribution of the production rise to AI, any claim that the monitored wells are in Texas, and ExxonMobil's drilling automation claims, which were verified and left out of the deck as a different company's story.",
 "keywords": ["Permian Resources", "artificial lift", "AI", "large language models", "Permian Basin", "Delaware Basin", "Reeves County", "Railroad Commission", "earnings release"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "SPATIAL SCENES on one staged Permian well pad at last light (frames 1, 3, 4, 6, 7 and 9) with three TXBENCH material reliefs (2, 5 and 8). Chassis assets/js/deck/2026-11-04-wellpad.js: release_page, strata_block, gauge_board and gauge_tape kit models with the kit's pump_jack, oil_tank, person, ranch_gate and cattle_guard, and dusk_gold as the one accent for a figure the release or record prints.",
 "structural_laws": [
  "THE KIT BAKES BY MATERIAL. A pump jack's polished rod and a tank's gauge board are merged into one mesh per material, so geometry parameters find nothing. Locate a part by its material's box, and fold kit vertices to a point to hide one.",
  "A GRAZING EDGE ON A PAINTED CYLINDER FLARES WHITE. A standard material's specular at a low sun turned the tank's silhouette into a white stripe that envMapIntensity did not touch. A physical material with specular intensity near 0.1 kept it green.",
  "A LIT ACCENT PLATE OVEREXPOSES. An emissive target at the accent hex rendered pale peach under a work light, so the albedo sits darker and less saturated than the target colour to land within twelve Lab of it.",
  "A RELIEF'S TOP EDGE IS A HARD LINE UNDER THE DEK. A relief starting at a fixed y drew a visible edge through the dek's last line until a darken-only feather of 170 px faded it into the type field.",
  "A THIN SUBJECT CAN'T SHARE A FULL-WIDTH HOOK. A rod and its bridle crossed the hook and dek wherever the camera put them until the type column narrowed to the left and the subject took the right half."],
 "techniques": [
  "a pump jack side on against the last light seam, its crank raked by a work light, on a dirt pad with long casts",
  "a release page on dark steel with two graphite brackets on its margin and a binder clip",
  "the carrier bar, two bridle cables and the chrome polished rod seen from beyond the well, the horsehead above",
  "a cutaway block of banded ground under the jack, the well string dropping to a pale lateral with three leaders",
  "two sucker rods on a tread plate at 100 to 122, the longer one tagged in brass",
  "a stock tank battery with a float gauge board whose target sits at the crude share",
  "two pipe racks of 67 and 33 box ends facing the low sun",
  "a steel tape of 167 daily graduations from a brass plumb bob to a brass clip",
  "a worker outside a closed lease gate, the jack working beyond it"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A staged pad at last light and dark reliefs."},
 "accent": {"hex": "#E0956A", "name": "dusk_gold, a figure the release or record prints", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The 22% tag on 5, the crude share target on 6, the plumb bob and clip at May 21st and November 4th on 8, and the leasehold labels on 7 in type."},
 "ground": {"hex": "#08090C", "note": "The pad at last light and the reliefs' black bed."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
mv = json.loads((OUT / "caption_moves.json").read_text())
add("captions", {"date": D, "carousel_no": N, "opening_move": mv["opening_move"], "structure": mv["structure"],
 "closing_move": mv["closing_move"],
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": "Opens on the two things the release credits, AI for runtime and compression for the record runtimes, keeps each claim attributed, and closes on how much of the runtime is the monitor's.",
 "move_note": "Puts the AI claim beside the operating credit the release actually gives, carries the leasehold and the regulator's May statement as dated facts, and closes naming what the release leaves unmeasured."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
