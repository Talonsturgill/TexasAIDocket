#!/usr/bin/env python3
"""update_ledgers.py for 2026-10-18, carousel no. 54. Appends one entry to each variety ledger,
the artwork values measured off the final renders by deck_coherence and layout_check's own
functions, the caption's counts measured off caption.txt. Then ledger_check --derive rewrites the
caption exclusion lists."""
import json, re, sys, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/carousel"))
import deck_coherence as DC, layout_check as LC
from PIL import Image
D, N = "2026-10-18", 54
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
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0218", "related_items": ["tx-2026-0207"],
 "instrument": "The USDA Agricultural Research Service's Tracking the Path of New World Screwworm page, KRGV's October 12th drone report, three APHIS screwworm pages, the CDC's screwworm page and the Texas Animal Health Commission's screwworm page, all fetched October 18th, 2026.",
 "topic": "USDA's research service in Kerrville builds AI predictive models that already pick areas for livestock and wildlife surveillance, adult fly trapping and sterile fly releases against New World screwworm in Texas, and its laboratory director says they can't predict people moving infested animals. The Texas Animal Health Commission counts 43 premises with a confirmed detection in 17 counties, USDA's drones found no case among more than 36,000 animals observed, and the Edinburg facility deploys more than 80 million sterile flies a week.",
 "angle": "Rendered last light brush country: a windmill water point with a release aircraft on the cover, a cast relief map of the infested zone, 43 windmills for 43 premises, a worker and a trap under the aircraft, 80 boxes in a 100 slot block beside the projected plant's 300 slots at the same pitch, 1966 carved in limestone, 36 cattle from a drone, a stock trailer leaving into the dark, and a shut gate with a rancher at the latch.",
 "angle_note": "Every frame is drawn to illustrate. One windmill is one premises, one box is one million flies a week and one animal is a thousand seen, all from figures.json. No real place, aircraft or facility is depicted.",
 "entities": ["USDA", "Agricultural Research Service", "Kim Lohmeyer", "APHIS", "Texas Animal Health Commission", "KRGV", "CDC"],
 "places": ["Kerrville", "Edinburg", "Zavala County", "Texas"],
 "what_was_refused": "federalregister.gov and faa.gov answered 403, so no rule text is carried. The drone finding is never stated as Texas having no cases, and the macro fly cover failed two audition readings and was replaced by the water point.",
 "keywords": ["New World screwworm", "sterile insect technique", "USDA", "Kerrville", "Edinburg", "predictive models", "AI", "drones", "livestock", "Texas Animal Health Commission"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by out/2026-10-18/update_ledgers.py.",
 "register": "SPATIAL SCENES in TXT's lastLight world with two material reliefs. Chassis assets/js/deck/2026-10-18-brush.js: key az -58 el 8, a warm rim, a capped sky image light, six chassis models (screwworm fly, fly trap, release aircraft, release box, survey drone, stock trailer), a galvanized override for kit metal that mirrored the navy sky.",
 "structural_laws": [
  "KIT METAL MIRRORS THE NIGHT SKY AS THE ACCENT. A high metalness blade or tank under a navy sky reads bluebonnet; every kit metal in a lastLight frame is overridden to a rough half metal.",
  "A TXT.stage BEHIND OR DEPTH GIVEN IN METRES PUTS THE FOG A KILOMETRE AWAY. Both are fractions of the subject's distance; passing 10 and 30 left a lit mid tone band behind the type.",
  "A PAINTED PLANE ROTATED BY -yaw AFTER ITS -90 DEGREE TILT IS MIRRORED. Slot paint must take rotation.z = +yaw to align with boxes turned by rotation.y = yaw, or the outline corners open.",
  "A TANK SEEN FROM A LOW EYE HAS NO WATER. Two attempts at a water surface failed review; the rim hiding the water and a drinking cow carried the water point.",
  "A CLOSE-UP ON A KIT PERSON READS AS A MANNEQUIN. The close passed only when the camera stood back and the whole gate, both posts and the rancher read as one unit."],
 "techniques": [
  "a windmill water point backlit on the seam from behind barbed wire, Herefords along the fence, a release aircraft low on the left",
  "a cast caliche relief of southwest Texas with the zone counties as galvanized rims, Zavala raised in red loam and enamel pins at Kerrville and Edinburg",
  "43 windmills in five staggered rows from a low eye, every wheel against the seam",
  "a worker beside a T-post with a bluebonnet lidded trap, a release aircraft overhead",
  "80 kraft boxes in a 100 slot painted block with three more blocks receding for the 300 plant, a worker for size",
  "1966 V-cut in Hill Country limestone under one raking band",
  "36 Herefords round a stock tank from over a survey drone's shoulder, its lamp the accent",
  "a pickup towing a slatted stock trailer down a caliche road into the seam",
  "a shut galvanized gate with a rancher at the latch post and a Hereford beyond the rails"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A staged last light deck."},
 "accent": {"hex": "#4E5FA8", "name": "bluebonnet", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "What the response sends: the pins, the trap lid, the tape on the release boxes, the drone's lamp."},
 "ground": {"hex": "#07070C", "note": "The lastLight world's dark sky behind the stage."}})
cap = (OUT / "caption.txt").read_text().strip()
import caption_check as CC
rate, commas, words = CC.comma_rate(cap)
add("captions", {"date": D, "carousel_no": N, "opening_move": "the two things", "structure": "Pivot",
 "closing_move": "name what happens next and when",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": rate,
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": (OUT / "captions" / "critic_note.txt").read_text().strip()[:900],
 "move_note": "Opens on the two facts that pull against each other, drones finding no case and the commission counting 43 premises, pivots to what the models do and what they can't see, and closes on the reader's next step and the number to call."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
