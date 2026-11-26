#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-25, carousel no. 87. Appends one entry to each variety ledger,
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
D, N = "2026-11-25", 87
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0260", "related_items": ["tx-2026-0257", "tx-2026-0249"],
 "instrument": "UTMB Health's November 19th release on AI in its lung cancer screening program, Bunkerhill's UTMB case study and the USPSTF lung cancer screening recommendation, fetched November 25th, 2026.",
 "topic": "UTMB Health uses an AI system built with Bunkerhill to review radiology reports and flag lung nodules for a patient navigator, who ranks follow up by a validated risk score, and most of the nodules the program found came from patients who were not having lung cancer screening.",
 "angle": "The second finding. A scan drawn as a periwinkle field that covers only part of a glass lung holds a gold bead nobody ordered it to find, and the bead moves from report to navigator to the people who decide, then to a patient in her 20s, her family and the reader's own scan.",
 "angle_note": "Gold means a nodule flagged for a person only, and frame 7's bead is plain lilac glass because no claim says the AI flagged that patient. No accuracy, count or after adoption timing is drawn. Bunkerhill's 80 percent never appears. The patient story is Dr. Nishi's account. Periwinkle is a scan ordered for something else and frosted white a screening exam.",
 "entities": ["UTMB Health", "Bunkerhill", "Shawn Nishi", "Amanda Rodriguez", "US Preventive Services Task Force"],
 "places": ["Texas", "Galveston", "Galveston County"],
 "what_was_refused": "any accuracy figure, any count of patients or scans, any after adoption timing, Bunkerhill's marketing figures as UTMB results, the Brock score as UTMB's score, and robotic bronchoscopy as part of the flagging system.",
 "keywords": ["lung cancer screening", "lung nodule", "incidental finding", "radiology reports", "patient navigator", "UTMB Health", "Bunkerhill", "risk score"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "BESPOKE, LOOK V2 people tone, nine slide artists. A glass lung crossed by a periwinkle scan slice with a gold bead (1), an aging stack of manila chart folders on a records cart (2), a fanned stack of report sheets with one gold flag and a binder clip (3), a navigator lifting a gold flagged card from a ranked card file by a window (4), a diagonal rail of nine flagged report plates climbing from a small steel reader bridge, its cyan beam on the first plate, to a navigator's hands and a doctor's hand on the last (5), three glass lungs, each holding one gold bead, one bare in a white enamel screening cradle and two crossed by thin periwinkle scan slabs (6), a steel age rule on limestone with a lilac glass bead at 20 (7), a family of seven under a live oak with an eighth half hidden at the trunk (8), the cover's glass lung, large, crossed by three thin periwinkle scan slabs at shoulder, chest and bases (9).",
 "structural_laws": STRUCT,
 "techniques": ["transmission glass lungs with an acrylic scan slice", "aged manila folders on a wire cart", "a fanned report stack relief with a binder clip", "an over the shoulder navigator at a card file", "a steep diagonal hand off rail from reader to hands on a leather pad", "an orthographic row of three glass lungs, one cradled and two banded", "a diagonal steel age rule on a limestone ledge", "a chest height family group under a live oak", "a glass lung crossed by three thin acrylic scan slabs"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders."},
 "accent": {"hex": ACC, "name": "flag gold", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "A nodule flagged for a person, only."},
 "ground": {"hex": "#ff9f62", "note": "People tone apricot floor under periwinkle and plum."}})
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
