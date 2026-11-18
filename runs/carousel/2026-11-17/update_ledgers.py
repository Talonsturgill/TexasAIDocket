#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-17, carousel no. 80. Appends one entry to each variety ledger,
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
D, N = "2026-11-17", 80
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0194", "related_items": ["tx-2026-0248"],
 "instrument": "The Texas Tribune's October 7th, 2026 report on STAAR rescoring requests and TEA's December 2023 and March 2024 scoring documents, fetched November 17th, 2026.",
 "topic": "The Texas Education Agency's automated scoring engine scores the written answers on English STAAR tests first, with a share also routed to people under its December 2023 design. Requests to regrade reading answers rose sharply from spring 2024 to this spring, people did every rescore, the state raised thousands of reading scores while a tiny share of all open-ended reading answers changed, and Dallas ISD saw many of its rescored tests come back higher. A district pays a fee per test unless the score changes.",
 "angle": "A graphite violet scoring machine reads each typed answer first and a person's score is the deck's only gold: the machine with its glass read chamber and a dark desk waiting behind, why a machine as paper strata, the drawer of human scored cards, the fork where a page rises up a gold chute to a reader, the requests as true scale paper towers beside a person, a reader rescoring under a lamp, a single gilded sheet in a block of paper, Dallas County's raised tiles, and the cover's desk lit at the end of the gold route.",
 "angle_note": "Every frame is drawn to illustrate. STAAR is answered online, so every page carries greeked typed lines, never handwriting. TEA's design figures are dated to its 2023 and 2024 documents and the spring counts to the Tribune. No frame implies the engine got any answer wrong. Gold means a person's score only.",
 "entities": ["Texas Education Agency", "STAAR", "Dallas ISD", "Texas Tribune"],
 "places": ["Texas", "Dallas County"],
 "what_was_refused": "a TEA page for the spring counts (none answered), the 42 and 58 percent split (referent unclear), the separate 27,200 student text entry review (a different review the engine did not grade), the November 13th date of the governor's notice on the TCEQ story (only 'Friday' in the source).",
 "keywords": ["STAAR", "automated scoring", "rescore", "Texas Education Agency", "Dallas ISD", "schools", "testing", "reading"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "BESPOKE, LOOK V2 watch tone, nine slide artists. TXT.studio sweeps (1, 4, 7, 8, 9), a TXBENCH relief (2 paper strata), TXT.interior rooms (3 archive bay, 6 lamplit desk), an outdoor TXT dusk plaza (5). Spine assets/js/deck/2026-11-17-scorebench-bespoke.js with chassis models scoring_engine, response_sheet, card_cabinet and paper_column.",
 "structural_laws": [
  "DUSK GOLD UNDER THE WATCH CORAL KEY RENDERS ORANGE OR PEACH. Every gilt and tab frame fought it; violet rose floors and a cooled key are the cure.",
  "K.MAKE CENTRES A MODEL'S FOOTPRINT, so a model with a long arm (the engine's chute) shifts every child off its userData coordinates.",
  "A STUDIO SWEEP IS A GROUND, and depth_floor now says so.",
  "A RECT IS X, Y, WIDTH, HEIGHT. Writing corners pads the box with empty field and the detail floor refuses it.",
  "A CAMERA PUSHED IN TO A PAGE CROPS THE MACHINE THAT READS IT. The cover needed the whole infeed face and never got both."],
 "techniques": ["a graphite violet instrument with a smoked glass read chamber where a typed page curls over a roller under a lilac scan bar, an unlit desk waiting behind it", "a relief of one paper band beside a stack six to seven times its height with a graphite staff", "a card catalog drawer of 3,000 cards in 30 blocks with ticked gold tabs", "a smoked glass engine with three pages in its tray and one gold page riding a chute up to a reader under a lamp", "three plumb true scale paper columns with kraft ream wrappers on a dusk plaza beside a person looking up", "an over the shoulder reader at a walnut desk under a gold lamp in a dusk office", "a diagonal macro of a block of two hundred sheets with one gilded sheet pulled proud", "Dallas County as a limestone tablet with 34 of 100 tiles raised on gilt stacks", "the cover's lit desk at the end of a railed gold chute from the scoring machine"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders."},
 "accent": {"hex": ACC, "name": "dusk gold", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "A person's score only."},
 "ground": {"hex": "#c98a9a", "note": "Violet rose floors under the watch tone's violet sky, never its coral floor."}})
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
