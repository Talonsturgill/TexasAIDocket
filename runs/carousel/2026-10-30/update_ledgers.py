#!/usr/bin/env python3
"""update_ledgers.py for 2026-10-30, carousel no. 63. Appends one entry to each variety ledger,
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
D, N = "2026-10-30", 63
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0234", "related_items": ["tx-2026-0030", "tx-2026-0075"],
 "instrument": "City of Plano Legistar records for Matter 1967 (File 26-884) and the City Council meetings of October 12th, October 26th and November 9th, 2026, Darwin AI's own site, Carahsoft's Darwin AI for Government page, and the Census Bureau's place files, all fetched October 30th, 2026.",
 "topic": "Plano's City Council agenda of October 12th carried a consent item to buy ChatGPT Enterprise for $190,000 and the Darwin AI governance platform for $150,000 from Carahsoft, Microsoft Enterprise for $10,000 from SHI, and a $40,000 reserve, inside a $390,000 not to exceed ceiling. The meeting's minutes note reads approved. The October 26th meeting's draft minutes mark the October 12th minutes approved, and the council meets next on November 9th.",
 "angle": "Weighed on a brass laboratory balance in the lastLight world: the loaded balance on a chalk plinth before city hall, the agenda sheet with a weight on item (f), the open case of 39 wells, the brass stack at macro, grooves of discs in Blackland clay, the needle on the reserve, the raised blued pan with the maker's words, the shut case on the dais ledge, and the balance on the plaza with a resident walking to the chamber.",
 "angle_note": "Every frame is drawn to illustrate. One slotted weight is $10,000, a drawing unit equal to the Microsoft line. The beam's tilt is a drawing rule. No license count, planned use or agenda memo is in the record.",
 "entities": ["City of Plano", "Plano City Council", "Carahsoft Technology Corporation", "Darwin AI", "OpenAI", "SHI Government Solutions"],
 "places": ["Plano", "Collin County", "Denton County"],
 "what_was_refused": "any claim that Darwin AI was bought to watch ChatGPT, a vote or tally, a license count or planned use, GovTech's reporting (ClaudeBot disallowed site wide), and the agenda memo on plano.legistar1.com (robots refuses all readers).",
 "keywords": ["Plano", "ChatGPT Enterprise", "Darwin AI", "AI governance", "consent agenda", "Carahsoft", "Legistar", "city procurement"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "SPATIAL SCENES in TXT's lastLight world, staged, with two TXBENCH material reliefs. Chassis assets/js/deck/2026-10-30-balance.js: slotted_weight, weight_stack, equal_arm_balance, weight_case and chalk_plinth, polished brass, heat blued steel as the one accent for the Darwin line, nickel for Microsoft, pecan and Austin chalk.",
 "structural_laws": [
  "A FLAT FRAME'S POST PASS RUNS IN CSS PIXELS. Called before the 2x transform, the scrim and veil darkened only the top left quadrant, and it read as a relief artifact for most of the run.",
  "A FIELD OF DISCS IN PLAN READS AS DIALS. The relief of the case read as clock faces twice; an oblique camera on a desk made them weights.",
  "RANDOM SLOT TURNS READ AS STRAY NOTCHES. Lined up on the far side, a stack reads as countable discs.",
  "A MACRO ON A NEEDLE IN FRONT OF A PILLAR HIDES THE NEEDLE. Close in, the pillar runs through the type or covers the blade.",
  "A ROOM'S WALL IS A DEAD FIELD UNTIL A WINDOW KEY RAKES THE SUBJECT. The dais read only once a warm spot crossed the case lid."],
 "techniques": [
  "a brass pillar balance loaded 19 to 15 on a chalk plinth, city hall behind at last light",
  "an agenda sheet relief with one slotted weight standing on row (f) and casting across its four lines",
  "an open pecan case of 39 wells on a council table, three metals and four empty wells",
  "the brass stack of 19 at macro over its pan",
  "two grooves of discs in near black Blackland clay with four empty seats",
  "the needle on the reserve's graduation over a nickel silver arc",
  "the blued stack raised in its pan from below, with the maker's quoted words",
  "the shut case on a walnut dais ledge raked by a window key",
  "the loaded balance close on the plaza with a resident walking toward the lit chamber"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A staged lastLight deck."},
 "accent": {"hex": "#4E5FA8", "name": "heat blued steel, the Darwin AI line", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The blued stacks and discs on 1, 3, 5, 6, 7 and 9."},
 "ground": {"hex": "#0A090D", "note": "The lastLight world's dark sky and the flat frames' dark field."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
add("captions", {"date": D, "carousel_no": N, "opening_move": "the number that is wrong", "structure": "Ledger",
 "closing_move": "name what is still not public, and how big that is",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": "Opens by correcting the figure a reader would assume, then lists the item line by line as a ledger, then the consent agenda and the minutes, and closes on which city work the two tools will serve.",
 "move_note": "Opens on what $390,000 is not, walks the four lines and the 79 cents, then the one motion, the minutes and the next meeting, and closes on a question about use."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
