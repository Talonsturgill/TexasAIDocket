#!/usr/bin/env python3
"""update_ledgers.py for 2026-10-23, carousel no. 58. Appends one entry to each variety ledger,
the artwork values measured off the final renders by deck_coherence and layout_check's own
functions, the caption's counts measured off caption.txt. Then ledger_check --derive rewrites the
caption exclusion lists."""
import json, re, sys, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]   # runs/carousel/<date>/update_ledgers.py
sys.path.insert(0, str(ROOT / "scripts/carousel"))
import deck_coherence as DC, layout_check as LC
from PIL import Image
D, N = "2026-10-23", 58
OUT = ROOT / "out" / D
L = ROOT / "ledger/carousel"
def add(name, entry):
    p = L / f"{name}.json"; t = json.loads(p.read_text())
    t["entries"] = [e for e in t["entries"] if e.get("date") != D] + [entry]
    p.write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n")
frames = [OUT / "render" / f"slide-{i:02d}.png" for i in range(1, 10)]
med = [round(DC.median_lstar(f), 1) for f in frames]
d = [abs(a - b) for a, b in zip(med, med[1:])]
acc = [round(LC.accent_coverage(Image.open(f).convert("RGB"), "#BD452C"), 4) for f in frames]
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0228", "related_items": [],
 "instrument": "UT Southwestern Medical Center's news release of October 20th, 2026, and the authors' Research Square preprint rs-9249025 v1 (abstract page and full text), all fetched October 23rd, 2026.",
 "topic": "UT Southwestern researchers asked three open source language models which of two matched emergency patients to see first, with records from Stanford Medicine and Beth Israel Deaconess. With no added detail all three beat chance. Once stigmatizing detail was added, nearly 10% of patients were incorrectly downgraded in some instances, frequent emergency use and past psychiatric emergencies among the strongest effects. The first author says each tool should be tested against real patient outcomes before use.",
 "angle": "Rendered in the staged lastLight world on a shale ledge as bone record cards: the pair in a holder with an ember tape on the notched card for the cover, two stacks for the two departments, three sorting trays per model before and after the line from one locked camera, a relief of the card with the stigmatizing wording on the tape over the neutral one, 17 wristbands for 17 visits, a drawer of 100 index cards with one flagged block of ten, a relief of ten strips with the two strongest effects in ember, and the tape peeling off the card for the close.",
 "angle_note": "Every frame is drawn to illustrate. No real patient, record, hospital, product or person is depicted, and no Texas hospital is said to use these models.",
 "entities": ["UT Southwestern Medical Center", "Stanford Medicine", "Beth Israel Deaconess Medical Center", "npj Digital Medicine", "Research Square"],
 "places": ["Dallas", "Dallas County", "Texas"],
 "what_was_refused": "Any Texas hospital using these models for triage, 'lead author' for Jarrett, in-hospital death inside the 6 hour window, and the preprint's two model ranges standing in for the published three model result.",
 "keywords": ["UT Southwestern", "emergency triage", "language models", "stigmatizing language", "bias", "emergency department", "Dallas", "npj Digital Medicine"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by runs/carousel/2026-10-23/update_ledgers.py.",
 "register": "SPATIAL SCENES in TXT's lastLight world, staged, with two material reliefs. Chassis assets/js/deck/2026-10-23-ledger.js: key az 62 el 14, chassis models record_card, card_holder, sorting_tray, wristband, card_stack, card_drawer and shale_ledge, ruled bone card stock, an ember clearcoat vinyl tape, graphite steel, Eagle Ford shale.",
 "structural_laws": [
  "A PEEL TOWARD THE LENS FORESHORTENS TO NOTHING. The close's lift only read once it curled out past the card's edge in profile over the dark ledge.",
  "A CURL BUILT OF SEGMENTS RIBS. Rounded boxes along an arc showed a seam per segment; one box bent vertex by vertex shaded smooth.",
  "A DARK SHALE SWALLOWS THE POOL. At #2a2b2f the ledge read black under the key; lifting the albedo let the contact and casts show.",
  "A KNOCK BEHIND TYPE ON A PALE RELIEF IS A SMUDGE. The footer's dark halo over a light card read as a stain; the type sat cleaner on the foot wash alone.",
  "A RELIEF ACCENT NEEDS ITS ALBEDO NEAR THE SRGB TARGET'S LINEAR VALUE, or the grade and the ambient grey it into brick."],
 "techniques": [
  "two bone cards in a graphite holder, the ember tape on the notched one, raking key",
  "two card stacks on the ledge with leaders to the two department names",
  "three steel sorting trays, the notched card in each front slot, one locked camera",
  "a material relief of the card, the neutral line in ink above the tape's stigmatizing line",
  "seventeen wristbands in three rows on the shale, ember tabs",
  "the same three trays, the middle tray's taped card moved to the back slot",
  "a long drawer of 100 index cards in ten blocks, the flagged block at the end",
  "a relief of ten equal strips on a card, two in ember and named",
  "the cover's pair again, the tape peeling off the notched card past its edge"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A staged lastLight deck."},
 "accent": {"hex": "#BD452C", "name": "ember tape", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The vinyl tape that stands for the added stigmatizing line."},
 "ground": {"hex": "#07070C", "note": "The lastLight world's dark field around the stage."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
add("captions", {"date": D, "carousel_no": N, "opening_move": "the place", "structure": "Zoom out",
 "closing_move": "point at the record, plainly, without a call to action",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": (OUT / "captions" / "critic_note.txt").read_text().strip()[:900],
 "move_note": "Opens on Dallas and the one rewritten line, widens to the three models, the before and after, the record sources and hospitals exploring AI, and closes on the first author's ask and the models the release leaves unnamed."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
