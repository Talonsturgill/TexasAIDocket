#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-14, carousel no. 77. Appends one entry to each variety ledger,
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
D, N = "2026-11-14", 77
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0247", "related_items": ["tx-2026-0071", "tx-2026-0138"],
 "instrument": "Texas Tech Now announcements of the Texas Semiconductor Innovation Fund awards of November 13th, 2026, January 2026 and May 2026, all fetched November 14th, 2026.",
 "topic": "The Texas Semiconductor Innovation Fund gave Texas Tech's engineering college an award of over $19 million to help set up a next-generation computing cluster in Lubbock, announced November 13th, 2026. The announcement gives no install or completion date. It follows a $12 million award in January toward a clean room, which the university will match for a $24 million project, and roughly $4.5 million in May for wide and ultrawide bandgap research. The engineering dean says Texas Tech will be among the first universities with access to the newest generation of Nvidia chips to power the cluster.",
 "angle": "Every award drawn at a single scale, 1 wafer for every $1 million. November's boat of 19 has no far end plate because the award is a floor. January's 12 are capped at both ends, the match sets 12 in carbide beside 12 in quartz, May's 4 end in a cleaved half, a tray sets all 3 side by side, 1 wafer face carries a growing layer, 1 wafer is cut into dies for the chips, and a nameplate closes with 19 empty pockets under IN SERVICE.",
 "angle_note": "The wafers, boats, tray and plate are drawn to illustrate. No real lab, product or plate is depicted. No total of the three awards is printed or drawn, because one figure is a floor and one is approximate.",
 "entities": ["Texas Tech University", "Texas Semiconductor Innovation Fund", "Texas CHIPS Office", "Office of the Governor", "Nvidia"],
 "places": ["Lubbock", "Lubbock County", "Texas"],
 "what_was_refused": "a total of the three awards, any install or completion date, any chip count or delivery date for the Nvidia access, any statement that the January figure is exact (the integrity judge refuted 'exact' in round 1), the harsh environments purpose attached to the May award, and Shield AI, which named no county.",
 "keywords": ["Texas Tech", "TSIF", "Texas CHIPS Act", "semiconductors", "computing cluster", "Lubbock", "Nvidia", "clean room", "wafers"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "A MIX. Spatial scenes in the floodlit world inside a dark lab on one black epoxy bench (1, 3, 4, 5, 8) and TXBENCH material reliefs (2, 6, 7, 9). Chassis assets/js/deck/2026-11-14-waferbench.js: wafer (whole or cleaved, with notch, edge exclusion ring and laser scribe ID), wafer_boat (quartz or carbide, capped or open), lab_bench, and labEnv, a reflection environment of light strips for mirror silicon.",
 "structural_laws": [
  "MIRROR SILICON SHOWS ONLY WHAT IT REFLECTS. With nothing bright in the reflected direction a polished wafer renders as a matte dinner plate, so the chassis builds light strips for it to reflect.",
  "AUTO-AIMED REFLECTION STRIPS UNDER A PARALLEL CAMERA TURN EVERY WAFER WHITE. Every face reflects the same direction, so frames 3 and 4 use the cover's fixed strips.",
  "A FACE THAT CASTS ON ITSELF READS AS A SCREW HEAD. A domed disc in a relief splits along a hard terminator, so polished discs are flat faces with a rolled rim and a soft radial highlight in the albedo.",
  "A REPRESENTATION THAT CAN NOT SHOW AN END STATE IS THE WRONG ONE. Frame 6 began as three boats in perspective and became a plan view tray, because only a plan view shows capped, cleaved and open ends at one scale.",
  "A KIT PERSON AT THIS SCALE READS AS A MANNEQUIN. Two judges in two rounds named it, so frame 8 dropped the figure for the deck's own object.",
  "THE FIGURE BELONGS IN THE GEOMETRY OF THE CLOSE. Nineteen empty pockets in the IN SERVICE recess carry the November count onto the last frame."],
 "techniques": [
  "nineteen mirror wafers in a quartz boat with no far end plate, close and low on the bench",
  "Lubbock County raised in a relief of the committed county geometry",
  "January's twelve from above in a boat capped at both ends",
  "twelve in quartz beside twelve in carbide through a parallel camera",
  "May's four and a cleaved half, close at the near end",
  "a plan view tray of three channels, capped, cleaved and open",
  "one wafer face with terraces and a step flow layer growing across it",
  "one wafer cut into a grid of dies lying flat on the bench",
  "a nameplate with AWARD and CHIPS filled and nineteen empty pockets under IN SERVICE"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders."},
 "accent": {"hex": ACC, "name": "dusk_gold, the November award", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "Lubbock County's raised face, November's disc rims, the growing layer, the AWARD inlay."},
 "ground": {"hex": "#0B0A0D", "note": "Black epoxy lab bench in a dark room."}})
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
