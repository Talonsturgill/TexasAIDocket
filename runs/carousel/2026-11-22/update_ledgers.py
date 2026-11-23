#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-22, carousel no. 85. Appends one entry to each variety ledger,
the artwork values measured off the final renders by deck_coherence and layout_check's own
functions, the caption's counts measured off caption.txt. Then ledger_check --derive rewrites the
caption exclusion lists."""
import json, re, sys, subprocess
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] if HERE.parent.name == "out" else HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts/carousel"))
import deck_coherence as DC, layout_check as LC
from PIL import Image
D, N = "2026-11-22", 85
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0257", "related_items": ["tx-2026-0201", "tx-2026-0228"],
 "instrument": "The IC² Institute's October 20th release on the AI Learning Lab and the IC² Institute's AI Learning Lab project page, fetched November 22nd, 2026.",
 "topic": "The IC² Institute and Dell Medical School announced the AI Learning Lab on October 20th. Its 80 Dell Med clinicians, faculty, residents and students, meet paid actors in simulated encounters. Half get Claude and half rely on UpToDate with its AI capability switched off. Researcher Sookja Kang asks how fast clinicians reach for their AI tool, whether they accept its output or interrogate it, and how much reasoning gets handed off as a diagnosis evolves. The release reports no findings and cites a 2026 American Medical Association survey with 81% of doctors using AI against 38% in 2023.",
 "angle": "The fair test. Two matched exam rooms with one tool switched off, a wall of eighty stethoscopes, a live actor rather than a page, a book and a switch for the AI that is off, and Kang's three questions built as instruments at rest: a timing rail, two slips on limestone and three handoff trays. Exam paper lengths carry the survey, and an empty rubric in an open binder closes on the curriculum.",
 "angle_note": "No frame implies a result or a better group, because the release reports none. Cyan means only the tool within reach. The survey figures are the release's citation, drawn as the release states them. The book, switch and slips are drawn to illustrate, to no vendor's design.",
 "entities": ["IC² Institute", "Dell Medical School", "AI Learning Lab", "Claude", "UpToDate", "Sookja Kang", "Tu-Quyen Dao", "James Korndorffer", "American Medical Association"],
 "places": ["Texas", "Austin", "Travis County"],
 "what_was_refused": "any study dates, the team roster, the project page's Executive Vice Dean title, any claim that the study has data, and any frame suggesting which group reasons better.",
 "keywords": ["clinical reasoning", "medical education", "simulated encounters", "Claude", "UpToDate", "Dell Med", "IC2 Institute", "AI Learning Lab"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "BESPOKE, LOOK V2 explainer tone, nine slide artists. TXT.studio sweeps throughout, a cut away exam room pair (1), a corridor wall (2), a doorway encounter (3), a relief wall plate (4), three studio benches for the questions (5, 6, 7), exam table lengths (8) and a still life of an open binder (9). Spine assets/js/deck/2026-11-22-fairtest-bespoke.js with chassis models exam_table, stethoscope, timing_rail, handoff_tray, output_slip and paper_roll.",
 "structural_laws": [
  "K.MAKE CENTRES A MODEL'S FOOTPRINT, so a chassis model that records an end point or places parts from its own origin lands offset; the spine must read positions back from the built group, never from the build arguments.",
  "A CONTRAST SEAT OVER A LIGHT STUDIO BENCH MUDDIES THE BENCH TO GREY VIOLET; keep each seat to its own line box with a tight fade.",
  "THE KIT PERSON'S COAT IGNORES A SLIDE'S MATERIAL SWAP, so a white coat under a strong key blows out; lower the key on the figure.",
  "A CLOSER CAMERA ON A MIRRORED PAIR CROPS ONE HALF FIRST; test both halves in frame in code before the render."],
 "techniques": ["two mirrored cut away limestone exam rooms with one cyan screen", "a corridor wall of chassis stethoscopes in a counted grid", "a doorway encounter with a seated actor on an exam table", "a book and a switched off toggle in relief on a wall plate", "a timing rail with a cyan carriage at rest", "two paper slips on pitted limestone with a graphite pen across one", "three handoff trays on a limestone bench with every shuttle parked on the clinician's side", "two lengths of exam table paper drawn to the survey's shares", "an open binder with an empty rubric grid and two shut laptops"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders."},
 "accent": {"hex": ACC, "name": "explainer cyan", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The AI tool within reach only."},
 "ground": {"hex": "#e8dcc4", "note": "Cream limestone and caliche under the explainer tone's cerulean sweep and indigo shade."}})
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
