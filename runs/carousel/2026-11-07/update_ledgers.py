#!/usr/bin/env python3
"""update_ledgers.py for 2026-11-07, carousel no. 71. Appends one entry to each variety ledger,
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
D, N = "2026-11-07", 71
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0179", "related_items": [],
 "instrument": "The City of Dallas Finance Committee briefing of December 9th, 2025 on AI-powered camera technology (dallascityhall.com, fetched November 7th, 2026), and the city's September 8th memo as FOX 4 and Dallas Express reported it (fetched November 8th, 2026). The first build's GovTech republications of the Dallas Morning News were withdrawn because www.govtech.com names ClaudeBot with Disallow / for the whole host.",
 "topic": "Dallas put City Detect cameras on its sanitation brush and bulk trash trucks. The city's September 8th memo, as FOX 4 and Dallas Express reported it, says the cameras scanned 10,000 properties, about 3,700 property owners were sent courtesy notices, about 300 cases were opened for inspection, and 57 citations went to 34 properties after code officers reviewed and confirmed the detections and inspected in person. By the city manager's memo 39 of the 57 citations were in Council Districts 4, 8 and 7 in southern Dallas. The three-year contract is $852,000 a year, subject to annual City Council appropriations, and Chad West withdrew a move to cut it once the city manager agreed to brief the council.",
 "angle": "One house from truck to porch at night. The camera on the truck's rail over its conspicuity tape, the still with its flag box and the briefing's eight conditions, the analyst's three trays, the courtesy notice in the mailbox, the officer at the pile, a column of 10,000 cards beside the 57 in his hand, the 57 citation cards fanned on the street 39 and the rest, three blank folders for the contract's terms, and the resident with a notice that asks for no action yet.",
 "angle_note": "Every frame is drawn to illustrate. One 0.2 mm card stands for one property scanned and one citation card for one citation, at the same card. The memo's counts measure different things and the deck draws no funnel between them. The October committee briefing's outcome is carried by no host this project may read, so no surface says what it decided. Same docket item as no. 31 on September 21st, outside the 30 day window.",
 "entities": ["City of Dallas", "City Detect", "Dallas Code Compliance", "Dallas City Council", "Chad West", "FOX 4", "Dallas Express"],
 "places": ["Dallas", "southern Dallas"],
 "what_was_refused": "every claim read through www.govtech.com, any funnel or rate between the memo's counts, FOX 4's rounded headline figure, the 70 percent figure that could not be read word for word, and any NBC 5, dallasnews.com or Dallas Observer material.",
 "keywords": ["Dallas", "AI cameras", "code compliance", "brush trucks", "City Detect", "southern Dallas", "courtesy notices", "Dallas City Council", "Council Districts 4, 8 and 7"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by update_ledgers.py.",
 "register": "SPATIAL SCENES on one residential Dallas street at night in the lastLight world (frames 1, 2, 4, 5, 6, 7 and 9) and two built interiors (3, the code office, and 8, the committee dais). Chassis assets/js/deck/2026-11-07-curbside.js: camera_pod, body_flank, brush_pile, tire, paper_column, letter_tray, notice, clipboard and plan_folder models with the kit's ranch_house, person, desk, monitor, mailbox and hearing_dais, and bluebonnet bands as the one accent for the city's flag and paper.",
 "structural_laws": [
  "A WARM KEY DESATURATES A COOL ACCENT. Under the lastLight key a bluebonnet band rendered near L* 30 and fell under the accent floor until it carried its own emissive.",
  "A KIT PERSON SEATED FROM BEHIND READS AS A SILHOUETTE. The over the shoulder analyst read only where a screen or lamp put light on the cheek.",
  "ONE SCALE MEANS ONE THING. Reusing frame 6's column at a different unit on frame 7 broke the deck's measured scale for all three judges, so the citations were drawn as cards at frame 6's own card.",
  "A LABEL ON PALE PRESSBOARD DIES. Light mono type over a lit folder face fell to about 2 to 1 and moved onto the dark wood above.",
  "A FOOT WASH OVER A CURB EDGE STILL STRIKES THE SOURCE LINE. The curb's lit edge ran through the claim ids until that corner was darkened on its own."],
 "techniques": [
  "a finned camera pod bolted to a white brush truck rail with cut limbs in the bed",
  "the parcel's still with a bluebonnet flag box round the pile and eight condition labels on the road",
  "an over the shoulder analyst at a desk with the still on screen and three labelled trays",
  "a brick mailbox pillar with a courtesy notice standing in its mouth",
  "a code officer at a curb pile and tires holding a clipboard with a bluebonnet cover",
  "a 10,000 card column beside the officer and the 57 card sheaf in his hand",
  "the 57 citation cards fanned on the asphalt, 39 and the rest either side of a painted lane line",
  "three blank pressboard folders on a committee dais ledge for the contract's three terms",
  "a resident at the porch under a lit lantern holding a notice with its bluebonnet band"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A staged night street and two dark rooms."},
 "accent": {"hex": "#4E5FA8", "name": "bluebonnet, the city's flag and paper", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The flag box on 2, the notice band on 3, 4 and 9, the sheaf cover on 5 and 6."},
 "ground": {"hex": "#05060A", "note": "The night sky and the dark street."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
mv = json.loads((OUT / "caption_moves.json").read_text())
add("captions", {"date": D, "carousel_no": N, "opening_move": mv["opening_move"], "structure": mv["structure"],
 "closing_move": mv["closing_move"],
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": "Opens on the two counts a reader will conflate, 3,700 notices and 57 citations, attributes the memo's process to the memo and the outlets, places 39 of the 57 in three southern Dallas districts, and closes on the question the council's next yearly appropriation leaves open.",
 "move_note": "A ledger from the memo's counts to the southern Dallas share to the yearly cost, attributed to the memo as Dallas Express and FOX 4 reported it, closing on what the council should see before another year."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
