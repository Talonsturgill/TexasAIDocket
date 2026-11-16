#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-16, carousel no. 79. Appends one entry to each variety ledger,
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
D, N = "2026-11-16", 79
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0249", "related_items": ["tx-2026-0201", "tx-2026-0228"],
 "instrument": "UT Health San Antonio's November 5th, 2026 article on a collaborative AI project for veterans with mild brain injuries, fetched November 16th, 2026.",
 "topic": "A $200,000 San Antonio Medical Foundation grant funds a year long UT San Antonio and South Texas Veterans Health Care System proof of concept pilot that plans to use natural language processing on recordings already made at the San Antonio VA, in which veterans described how they were injured and an important life event, to assess coherence, emotional tone, organization and level of detail. Norman says many veterans with mild brain injury struggle to find words even when standard tests show no clear impairment, and most adult language tests were built for aphasia after a stroke or severe injury. No result exists yet.",
 "angle": "A spoken story drawn as a single machined gold ribbon that changes state across every frame while every instrument stays open, dark or unplugged: a ribbon under an open caliper, a short gold voice at a family table, a sieve that catches labelled stones while gold grains fall through, a card drawer of 18 year blocks, paired gold inlays in cantera, a voice flattened into transcript pages under a lamp, dark gauge heads the ribbon threads, a patch panel with nothing patched, and the ribbon stopping short of a closed ranch gate.",
 "angle_note": "Every frame is drawn to illustrate. No result, accuracy, sample size or veteran count exists, so no frame draws a reading, a fill level, a score or a connection. No real VA building, clinic or person is depicted. The ribbon is seeded and never a real recording. Gold means the veteran's own spoken words only.",
 "entities": ["UT Health San Antonio", "UT San Antonio", "San Antonio Medical Foundation", "South Texas Veterans Health Care System"],
 "places": ["San Antonio", "Bexar County"],
 "what_was_refused": "any result or accuracy (none published), a count of veterans or recordings (not stated), the VA building the recordings were made in (the article says only the San Antonio VA), the article date as printed copy (it is in page metadata, not text).",
 "keywords": ["veterans", "traumatic brain injury", "speech", "natural language processing", "UT Health San Antonio", "VA", "biomarker", "clinic"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "BESPOKE, LOOK V2 explainer tone, nine slide artists. TXT.studio sweeps (1, 4, 7), TXT.interior rooms (2 kitchen table, 6 lamplit reading table), TXBENCH reliefs (3 sieve cutaway, 5 cantera inlays, 8 patch panel), an outdoor TXT scene (9 Hill Country gate). Spine assets/js/deck/2026-11-16-voicebench-bespoke.js with chassis models voice_ribbon, vernier_caliper and gauge_head.",
 "structural_laws": [
  "DUSK GOLD UNDER A COOL TONE RENDERS SALMON OR MAUVE. Every frame's gold ribbon read copper or rose until the metal got a warm reflection or fill; the explainer cobalt environment pulls #e0956a away from gold.",
  "A CHASSIS SLOT CAN BE CLOSED BY ITS OWN POSTS. The gauge_head's corner posts blocked the ribbon slot its note promised, so frame 7 built its own head.",
  "THE RELIEF BENCH LOCKS THE KEY TO THE CHASSIS LIGHT AND TAKES NO CAMERA, so a relief frame can't rake to an oblique; planning one as an oblique wastes a round.",
  "A RADIAL TYPE WASH READS AS STRIKETHROUGH ROWS. qa flags each headline line whose background varies along its run; a level band behind the column clears it.",
  "A COUNT OF BLOCKS READS AS ITS DIVIDERS. 18 blocks parted by 17 guides read as 17 until each block carried its own tab."],
 "techniques": ["a machined gold waveform ribbon on a studio sweep under an open stainless caliper", "a family table seen over a veteran's shoulder, one short gold ribbon among violet talk", "a brass sieve in cutaway catching two labelled stones while gold grains fall through", "an oak card drawer of 18 year blocks under a task light", "two polished gold waveform inlays in a cantera limestone slab", "a lamplit reading table where a paper ribbon flattens into transcript lines", "dark gauge heads in a receding row threaded by one gold ribbon", "a patch panel with feature and symptom jacks and every plug hanging free", "a gold ribbon stopping short of a closed ranch gate above the Hill Country, a caliper beside it"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders."},
 "accent": {"hex": ACC, "name": "dusk gold", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The veteran's own spoken words only: the voice ribbon and speech labels."},
 "ground": {"hex": "#ffc68a", "note": "The explainer tone's peach floor under cerulean and indigo."}})
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
