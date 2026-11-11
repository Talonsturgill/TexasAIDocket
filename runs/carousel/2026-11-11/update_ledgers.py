#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-11, carousel no. 74. Appends one entry to each variety ledger,
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
D, N = "2026-11-11", 74
OUT = ROOT / "out" / D
L = ROOT / "ledger/carousel"
def add(name, entry):
    p = L / f"{name}.json"; t = json.loads(p.read_text())
    t["entries"] = [e for e in t["entries"] if e.get("date") != D] + [entry]
    p.write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n")
frames = [OUT / "render" / f"slide-{i:02d}.png" for i in range(1, 10)]
med = [round(DC.median_lstar(f), 1) for f in frames]
d = [abs(a - b) for a, b in zip(med, med[1:])]
acc = [round(LC.accent_coverage(Image.open(f).convert("RGB"), "#3FA07A"), 4) for f in frames]
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0246", "related_items": ["tx-2026-0128", "tx-2026-0071"],
 "instrument": "The City of Starbase's notice of a December 9th, 2026 public hearing on a Chapter 312 tax abatement and a Chapter 380 agreement with SpaceX, fetched from starbase.texas.gov, with the Texas Tribune's November 10th, 2026 story on the $24 billion project and its August 31st, 2026 story on Brownsville's de-annexation, fetched November 11th, 2026.",
 "topic": "Starbase's City Commission meets December 9th, 2026 to consider a Chapter 312 tax abatement and a Chapter 380 agreement with SpaceX for a gas-fired power plant and super-compute facility on an approximately 444 acre tract east of Brownsville, initial phases estimated at approximately $24 billion. Brownsville de-annexed the land at SpaceX's request in August for up to $220 million in water and wastewater projects, on an offer good that day only, and Starbase annexed it. The Tribune says the project circumvents Brownsville's 90 day data center moratorium.",
 "angle": "The line that moved: a green city limit sign standing on the caliche shoulder at last light, the tract's area as a green square at true scale between Boca Chica Blvd and the channel, 109 precast blocks of the water ceiling beside a single block, a pulled survey lath beside its hole, 90 flagged stakes run north to the horizon, the line ending at a gas-fired unit 1,340 m out, 28 chairs in a dark hearing room, the lectern, and the sign again at night on the road to the meeting.",
 "angle_note": "The square holds the tract's area, never its shape. The plant, the room and the blocks are drawn to illustrate. No turbine count, site plan, water demand or ERCOT connection is drawn, because none is in the record. Super-compute facility is the notice's term and data center the Tribune's.",
 "entities": ["City of Starbase", "SpaceX", "City of Brownsville", "Cameron County", "Port of Brownsville", "Cameron County Enterprise Zone", "Texas Tribune", "South Texas Environmental Justice Network", "ERCOT"],
 "places": ["Starbase", "Brownsville", "Cameron County"],
 "what_was_refused": "a de-annexed acreage (no claim gives one), any turbine count or plant design, the moratorium's text from Brownsville's own page (403), any statement that the site will or will not connect to ERCOT, and the hearing's outcome.",
 "keywords": ["SpaceX", "Starbase", "Brownsville", "tax abatement", "Chapter 312", "Chapter 380", "de-annexation", "data center moratorium", "gas-fired power plant", "super-compute facility", "Cameron County"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "Spatial scenes, all nine, in the staged lastLight world on the tidal flats east of Brownsville (1 to 6 and 9), the key at azimuth -68 and elevation 7 so every cast runs right, and a dark TXT.interior hearing room around one lamp (7, 8). Chassis assets/js/deck/2026-11-11-cityline.js: survey_lath (green, old or no flagging, standing or lying), unit_block (precast cube with chamfer, loops and dimples) and a tidal flat albedo with vein and mottle controls, with signal_open green as rendered (#3FA07A) as the one accent for a city limit as it stands now.",
 "structural_laws": [
  "A SPRITE GLOW DOES NOT RENDER IN THE SNAPSHOT. lampGlow sprites were invisible, so every emitted point (sodium lamps, reflector lenses) is a MeshBasicMaterial mesh with toneMapped false.",
  "A PLANE NEAR THE FLAT Z-FIGHTS IT AT A KILOMETRE. Road and water laid within half a metre of the polygon-offset tidal flat vanished from the 700 m aerial, and lifting them two to three metres made them read.",
  "A LOW KEY'S CAST RUNS AWAY FROM AN EYE LEVEL CAMERA. At elevation 7 the posts' shadows fall right and back and foreshorten to slivers, so the cover's casts read only faintly.",
  "AN EMISSIVE SIGN FACE READS AS A CARD. The kit sheeting's glow lit the face from nowhere, so the cover's face takes its falloff from the key with glow 0.",
  "A TYPE WASH LONGER THAN THE DEK DARKENS THE SUBJECT. The type-reserve fade crossed the sign's top third until it was cut to 50 px."],
 "techniques": [
  "a green CITY LIMIT sign on perforated posts in a warm pool on the caliche shoulder, low three quarter at last light",
  "a green ribbon square of the tract's area at true scale from 700 m up, a road on its near side and channel water beyond",
  "109 precast blocks stacked six by six by three with one begun, beside one block alone, long lens",
  "a weathered survey lath lying on cracked salt crust beside its pit and crumbs, close",
  "90 flagged stakes run north from the lower left to the horizon, sodium lamps on the far seam",
  "the flagged line run 1,340 m to a gas-fired unit in its own pool, long lens, no wire drawn",
  "28 padded chairs facing an empty dais and lectern in one lamp's pool",
  "the lectern and gooseneck microphone in one lamp, a dais behind",
  "the cover's sign at night from the lane, amber pavement markers stepping into the dark"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders."},
 "accent": {"hex": "#3FA07A", "name": "signal_open as rendered, a city limit as it stands now", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The sign face on 1 and 9, the square's ribbon on 2, the flagging on 5 and 6."},
 "ground": {"hex": "#3E352B", "note": "The tidal clay umber of the flats."}})
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
