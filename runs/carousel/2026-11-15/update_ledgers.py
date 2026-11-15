#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-15, carousel no. 78. Appends one entry to each variety ledger,
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
D, N = "2026-11-15", 78
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0248", "related_items": ["tx-2026-0053", "tx-2026-0177", "tx-2026-0194"],
 "instrument": "Texas 2036's November 10th, 2026 article previewing its report In Ctrl of AI in Schools, fetched November 15th, 2026.",
 "topic": "Texas 2036 reports that in a fall 2025 survey 86 percent of Texas school and district leaders reported teachers using AI and 61 percent reported student use, while 29 percent reported a district policy governing student AI use and 20 percent a policy for teachers and staff. By the group's own count 42 states have issued some form of statewide AI guidance for schools and Texas is not among them. Its priorities are statewide guidance, safety standards for tools, teacher training and AI literacy. Nearly 85 percent of Texas voters call student data privacy extremely or very important if schools use AI, per the group.",
 "angle": "One unit per leader in a hundred carried in school objects: a desk with an AI chat and an empty sheet protector, a gym of 100 desks with 86 laptops lit, 100 lockers with 61 open and lit, the same desks with 29 amber folders, 100 staff mailboxes with 20 amber sheets, a shelf of 42 amber binders with one empty slot for Texas, four tab dividers over blank pages, a bus with every shade drawn, and an evening board room with one amber binder on the dais and an empty chair.",
 "angle_note": "Every frame is drawn to illustrate. One desk, locker or mailbox stands for one leader in a hundred; the survey shares are what leaders reported per Texas 2036, never classroom shares, and no two shares are set against each other. No state is named on any binder and no total of states is drawn. Amber marks a written rule only.",
 "entities": ["Texas 2036", "Texas Legislature", "Texas school districts"],
 "places": ["Texas"],
 "what_was_refused": "who ran the leader survey or the voter poll (unnamed in the article), the report as published (only previewed), any difference or ratio between survey shares, a total count of states, the research associations of AI with student performance (not verified verbatim).",
 "keywords": ["schools", "AI policy", "teachers", "students", "Texas 2036", "statewide guidance", "school boards", "classroom AI"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "BESPOKE, LOOK V2 people tone, the first bespoke deck: nine slide artists, nine worlds. Studio sweeps (1, 5), TXT.interior rooms (2, 4 gym, 6 reading room, 9 board room), TXBENCH reliefs (3 lockers, 7 tab dividers), an outdoor TXT scene (8 bus). Spine assets/js/deck/2026-11-15-ruleroom-bespoke.js with chassis models ring_binder, pocket_folder, policy_sheet, cubby_wall and shelf_run.",
 "structural_laws": [
  "A KIT COLOUR CAN LAND ON THE ACCENT'S HUE UNDER A WARM KEY. The kit bus's paint rendered at the amber's hue; frames repainted it lemon and checked the hue.",
  "KEEPING EVERY COUNTED UNIT VISIBLE FIGHTS FILLING THE FRAME. Frame 4's camera search found no stand that showed all 29 folders past 100 desks and filled more than about half the height.",
  "AN EMPTY SLOT AT THE END OF A ROW READS AS THE ROW ENDING. Frame 6 moved the gap inside the run with a binder on each side.",
  "ON A BESPOKE DECK THE HEADLINES MUST BE PLACED, OR THEY ALL LAND WIDE AND CENTRED. Distinct_check counted 2 places until frames 1 and 6 took narrow side columns.",
  "A HEAVIER TYPE SEAT FIXES CONTRAST AND READS AS A PLATE. Frame 1's seat cleared 4.5 and cost composition."],
 "techniques": ["a student desk from above on a studio sweep with a lit AI chat and an empty sheet protector", "a gym of 100 desks from the bleachers, 86 laptops lit", "a perspective relief of 100 lockers with 61 doors swung open and lit inside", "the same gym from a raised corner, 29 amber folders on the desks", "a wall of 100 oak staff mailboxes with 20 amber sheets and a teacher's hand", "a reading room shelf of 42 amber binders with one empty slot inside the run", "a relief of four pressboard tab dividers fanned over blank leaves on a leather blotter", "a school bus close along its side with every window shade drawn", "an evening board room from the aisle, an empty chair and one amber binder on the dais under a downlight"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders."},
 "accent": {"hex": ACC, "name": "people tone amber", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "Written rules only: folders (4), sheets (5), binders (6, 9)."},
 "ground": {"hex": "#ff9f62", "note": "The people tone's apricot floor and plum shadow."}})
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
