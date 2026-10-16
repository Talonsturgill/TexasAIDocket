#!/usr/bin/env python3
"""update_ledgers.py for 2026-10-16, carousel no. 52. Appends one entry to each variety ledger,
the artwork values measured off the final renders by deck_coherence and layout_check's own
functions, the caption's counts measured off caption.txt. Then ledger_check --derive rewrites the
caption exclusion lists."""
import json, re, sys, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/carousel"))
import deck_coherence as DC, layout_check as LC
from PIL import Image
D, N = "2026-10-16", 52
OUT = ROOT / "out" / D
L = ROOT / "ledger/carousel"
def add(name, entry):
    p = L / f"{name}.json"; t = json.loads(p.read_text())
    t["entries"] = [e for e in t["entries"] if e.get("date") != D] + [entry]
    p.write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n")
frames = [OUT / "render" / f"slide-{i:02d}.png" for i in range(1, 10)]
med = [round(DC.median_lstar(f), 1) for f in frames]
d = [abs(a - b) for a, b in zip(med, med[1:])]
acc = [round(LC.accent_coverage(Image.open(f).convert("RGB"), "#2A7A9E"), 4) for f in frames]
add("topics", {"date": D, "carousel_no": N, "docket_item": "tx-2026-0216", "related_items": [],
 "instrument": "Waymo's October 14th, 2026 post opening San Antonio, San Diego and Tampa to anyone with the app, its February 24th, 2026 first riders post, NHTSA's recall record for campaign 26E026000 read through api.nhtsa.gov on October 16th, 2026, and Texas Public Radio's April and May 2026 reports on the Salado Creek incident and the pause.",
 "topic": "Waymo opened its San Antonio robotaxis to anyone with its app on October 14th, 2026, with San Antonio International Airport included. Its NHTSA flood recall, 26E026000, covers 3791 potentially affected units of its 5th and 6th generation driving systems, says the software may let a vehicle slow and then drive into standing water on higher speed roads, and on October 16th, 2026 still lists the remedy as under development. An empty Waymo washed into Salado Creek on April 20th, 2026, and the San Antonio service ran without riders in May.",
 "angle": "One white robotaxi carried through the deck and its relation to water: dry at the departures curb on the cover, at a February street curb with an invited rider, to its beltline in Salado Creek, front wheels into a sheet of standing water on a divided highway, one of 3791 on a dark lot, stopped nose on at the edge of still water with its reflection, at the end of a calendar of one curb post a day, through the window beyond the recall record's screen, and back at the curb with a traveller at the close.",
 "angle_note": "The car, the airport curb, the streets, the creek, the lot and every person are drawn to illustrate. No real vehicle, street or building is depicted, and the car carries no maker's mark.",
 "entities": ["Waymo", "Waymo LLC", "NHTSA", "Texas Public Radio", "San Antonio International Airport", "City of San Antonio Aviation", "Jesus Saenz"],
 "places": ["San Antonio", "Bexar County", "Salado Creek", "McCullough Avenue", "Contour Drive"],
 "what_was_refused": "GlobeNewswire answered 403 to every client, so record item tx-2026-0209 was repointed to Kodiak's own copy of the release. KSAT and the Express-News refuse crawlers by robots and were not read; the Salado Creek account rests on Texas Public Radio.",
 "keywords": ["Waymo", "robotaxi", "San Antonio", "airport", "NHTSA recall", "26E026", "flood", "standing water", "Salado Creek", "autonomous vehicles"]})
add("artwork", {"date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by out/2026-10-16/update_ledgers.py.",
 "register": "RENDERED, NOT PRINTED. A staged nightSodium world declared once in assets/js/deck/2026-10-16-curb.js (key az 40 el 34, ground #07080C), seven exterior sets at night and one room. One hero, the chassis's robotaxi on the kit SUV body, on every frame. Chassis models for the robotaxi, an airport departures curb, standing water, a curb bollard and a road stud, with an instanced low detail car field and a window cut for the room.",
 "structural_laws": [
  "A FLAT LINE AT EYE HEIGHT IS NO LINE. A comal hairline laid on the water foreshortened to under a pixel from 25 cm up. Stood upright facing the lens it reads full width.",
  "A GRID IS SEPARATED BY DARK, NOT BY SPACING. 3791 cars on lit asphalt merged into one piece at feed width. Drive aisles on a near black pad broke the field into countable blocks, and an unlit or low albedo apron did the same for the calendar of posts.",
  "THE STAGE POOL AND A HOT SPOT LIGHT THE FLOOR WHATEVER ITS ALBEDO. A black pad under a 2600 spot still read mid brown through specular alone. An unlit or specular free pad is the floor that stays dark.",
  "DARK GLASS IS A BLACK CARD AT NIGHT. The car's coated glass carries the world's lights and the A pillar stops reading as a loose rod."],
 "techniques": [
  "the car low from its quarter at a departures curb, banded bollards on the island and the terminal's lit glass behind",
  "the car side on at a street curb with a rider at true scale under a cobra head",
  "a close crop of the car to its beltline in a rippled flood, a comal waterline round the body",
  "a divided highway side on through a long lens, the front wheels into a standing water sheet, eleven road studs and three leaders",
  "a high long lens over 3791 instanced cars parked in blocks on a dark lot, the full model hero in a pool",
  "the car nose on at the far edge of still water on a raised set, its mirrored twin as the reflection and a standing comal line",
  "a calendar of 233 curb posts in month rows, the posts after the creek day banded and lit, a comal ring at April 20th",
  "a dark office at night, the recall record's fields set on the monitor's projected corners, the car outside through the blinds",
  "the curb again from the canopy edge, the bollard line running along the island and a traveller walking to the car"],
 "value": {"per_frame_median_L": med, "deck_median_L": sorted(med)[4], "max_adjacent_delta": round(max(d), 1), "mean_adjacent_delta": round(sum(d) / len(d), 2), "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A dark staged night deck."},
 "accent": {"hex": "#2A7A9E", "name": "comal", "frames_above_floor": [i + 1 for i, a in enumerate(acc) if a >= LC.ACCENT_PRESENT], "share": acc, "note": "The water line only, where water meets the car or the record: the creek waterline, the highway sheet's leading edge, the standing water line, the April 20th ring and the remedy field's rule."},
 "ground": {"hex": "#07080C", "note": "The deck's declared ground behind the render."}})
cap = (OUT / "caption.txt").read_text().strip()
body = "\n".join(l for l in cap.splitlines() if not l.startswith("#"))
words = len(re.findall(r"[A-Za-z0-9'][A-Za-z0-9',.%-]*", body))
commas = body.count(",") - len(re.findall(r"\d,\d", body))
add("captions", {"date": D, "carousel_no": N, "opening_move": "the object", "structure": "Ladder",
 "closing_move": "point at the record, plainly, without a call to action",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas, "commas_per_100w": round(100 * commas / words, 2),
 "chars": len(cap), "hashtags": re.findall(r"#\w+", cap),
 "critic_note": "The critic chose candidate A, the object on a ladder. The shipped caption is that candidate after one edit, carried verbatim by the copywriter.",
 "move_note": "Opens on the driverless car at the airport, climbs from the opening through the creek and the recall's own words to the remedy field, and closes on what the finished remedy will change."})
subprocess.run([sys.executable, str(ROOT / "scripts/carousel/ledger_check.py"), "--derive"], check=True, cwd=ROOT)
print("ledgers:", med, acc)
