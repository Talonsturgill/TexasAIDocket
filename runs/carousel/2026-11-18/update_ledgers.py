#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-18, carousel no. 81. Appends one entry to each variety ledger,
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
D, N = "2026-11-18", 81
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0251", "related_items": [],
 "instrument": "UT Dallas's November 6th, 2026 news release on its Texas air pollution and cancer study and the abstract of the paper in Environmental Monitoring and Assessment, fetched November 18th, 2026.",
 "topic": "A UT Dallas team paired satellite readings of air pollutants from 2022 with CDC cancer prevalence for every Texas county and used machine learning. Counties with more pollution tended to have more cancer, sulfur dioxide was the strongest environmental predictor, the east had the worst air and the west the best, and high cancer counties sat near each other. The researchers say it is an association between places, not evidence that pollution causes cancer in any single person, and that satellite data may be less precise than ground monitors.",
 "angle": "Texas as a slab of its own ground read from orbit under a gold sheet of measured air. A costly ground monitor on an empty caliche flat, the satellite and its gold swath landing on fields and roads, a carved column of air bands with sulfur dioxide proud on top, survey pads with most stakes flagged on the pad that won, Texas grounds west to east under rising haze, a floor of flags with slate stones clumped, a resident in silhouette beside a parcel's gold boundary, and satellite blocks everywhere but a sharp circle round a monitor with a gold block to check first.",
 "angle_note": "Every frame is drawn to illustrate. No county is named or valued. R squared is a model fit and Moran's index is cancer clustering. Gold means what the satellite read only.",
 "entities": ["UT Dallas", "CDC", "Sentinel-5 Precursor", "Copernicus Atmosphere Monitoring Service", "Environmental Monitoring and Assessment"],
 "places": ["Texas"],
 "what_was_refused": "liquor consumption as the strongest predictor overall (the abstract says only relative), the 30 to 60 percent predictor weights, TROPOMI (not named), a licence string on the article page, and the synapsesocial aggregator as any source.",
 "keywords": ["air pollution", "cancer", "satellite", "machine learning", "sulfur dioxide", "UT Dallas", "public health", "remote sensing"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "BESPOKE, LOOK V2 explainer tone, nine slide artists. TXT.studio sweeps (1, 3, 6), outdoor TXT.sky worlds (2, 5, 8, 9), TXBENCH reliefs (4 air column, 7 flagstone floor). Spine assets/js/deck/2026-11-18-landbench-bespoke.js with chassis models survey_satellite and air_monitor_shelter.",
 "structural_laws": [
  "K.MAKE MERGES A MODEL'S OPTIONS AS DEFAULTS, so a description string in options becomes the value and NaN geometry.",
  "THE ENGINE'S AUTO BEVEL TURNS A THIN BOX TO NaN; thin boxes need userData.txBevel = false.",
  "FETCH IS REFUSED OVER FILE URLS by the craft floor; geodata loads by XMLHttpRequest.",
  "A LEVEL CAMERA WITH A SHIFTED LENS OVER A TXT.ground VERTEX ROW IN ITS OWN PLANE BREAKS THE RASTER; offset the ground grid.",
  "DUSK GOLD OVER WARM CALICHE OR PEACH LAND LOSES ITS MEANING; the land under the accent must stay cool and low chroma."],
 "techniques": ["a slab of Texas with 254 engraved county lines under a registered gold glass sheet scanned by a small satellite", "a close air monitoring station with lit analysers and a technician on an empty caliche flat", "a silver survey satellite throwing eight thin gold glass wedges onto a strip of Texas fields, roads and a dry creek", "a carved bas relief column of eight air bands over three ground strata with sulfur dioxide proud in gold glass", "four survey pads with 79 of 100 lath stakes flagged on the winner", "three slabs of Texas ground under gold air blocks of stepped haze", "a raked floor of 254 hand laid flags with cleft slate clumps in a wall's shadow", "a ranch parcel bounded by a flush gold inlay that turns before the house, one resident in silhouette", "satellite blocks averaged everywhere but a sharp circle round one monitor, one block outlined in gold"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders."},
 "accent": {"hex": ACC, "name": "dusk gold", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "What the satellite read only."},
 "ground": {"hex": "#e4d8c3", "note": "Caliche and limestone grounds under the explainer tone's cerulean sky."}})
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
