"""Append this run's entries to the three carousel variety ledgers, measured off the final renders."""
import json, re, sys, statistics, subprocess
from pathlib import Path
REPO = Path('/home/user/TexasAIDocket'); D = '2026-10-12'; N = 50
sys.path.insert(0, str(REPO / 'scripts/carousel'))
from deck_coherence import median_lstar
meds = [round(median_lstar(REPO / f'out/{D}/render/slide-0{i}.png'), 1) for i in range(1, 10)]
adj = [abs(meds[i + 1] - meds[i]) for i in range(8)]
cap = (REPO / f'out/{D}/caption.txt').read_text()
body = cap.split('#')[0]; words = len(body.split()); commas = body.count(',')
lc = subprocess.run([sys.executable, str(REPO / 'scripts/carousel/layout_check.py'), '--date', D, '--require'], capture_output=True, text=True).stdout
accent = [int(m.group(1)) for m in re.finditer(r'^\s+0(\d)\s.*accent (\d\.\d+)', lc, re.M) if float(re.search(r'accent (\d\.\d+)', m.group(0)).group(1)) >= 0.002]

def put(name, entry):
    p = REPO / 'ledger/carousel' / f'{name}.json'; d = json.loads(p.read_text())
    d['entries'] = [e for e in d['entries'] if e.get('date') != D] + [entry]
    p.write_text(json.dumps(d, indent=1, ensure_ascii=False) + '\n')


put('topics', {
 "date": D, "carousel_no": N, "docket_item": "tx-2026-0141",
 "related_items": ["tx-2026-0167"],
 "instrument": "UT San Antonio's September 28th, 2026 release on Chen Pan's solar flood warning node, UT Arlington's September 28th, 2026 release on its statewide flood warning project, and the National Weather Service's Turn Around Don't Drown page, all read on October 12th, 2026.",
 "topic": "UT San Antonio's prototype flood warning node carries optical water-level sensors at varying heights on a solar powered post and runs a TinyML model on its own microcontroller to judge imminent flood risk with no central server. The release reports 98.82% validation accuracy in initial assessments after training and parts of roughly $150 to $220 per station, and names no site, no operator, no field test against a real flood and no false alarm figure.",
 "angle": "A San Antonio low water crossing on a wet night under a cold lamp. The flood node is the hero: in the water to its first sensor on the cover, beyond rain columns for the radar finding, stacked and labelled, its box at detail scale, its reach on a stone model of Bexar County, a built station beside its own parts and a cost bar, a glass column filled to the validation score, its rail at the waterline for what the release leaves out, and a pickup turning back up the grade at the close",
 "angle_note": "The node, the crossing, the columns, the parts and the pickup are drawn to illustrate. No installation site is in the record, so no crossing is named and the reach circles show scale only.",
 "entities": ["UT San Antonio", "Chen Pan", "Klesse College of Engineering and Integrated Design", "UT Arlington", "Water Engineering Research Center", "National Weather Service", "Texas A&M University-Corpus Christi", "NOAA Texas Coastal Management Program"],
 "places": ["San Antonio", "Bexar County", "Hill Country"],
 "what_was_refused": "Any named crossing or installation site, which the release never gives. A field accuracy figure, which the release does not report. The full Federal Register text for the day's admitted trucking item through unblock.federalregister.gov, which robots.txt disallows; the GovInfo PDF was read instead.",
 "keywords": ["UTSA", "flood warning", "low water crossing", "TinyML", "edge AI", "LoRa", "San Antonio", "flash flood", "Turn Around Don't Drown", "flood sensor"]})

put('artwork', {
 "date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by out/2026-10-12/update_ledgers.py.",
 "register": "RENDERED, NOT PRINTED. A staged floodlit low water crossing at night (key az -135 el 48, ground #0C0D10) declared once in assets/js/deck/2026-10-12-crossing.js, with cold cobra head lamps as the practicals and 3D rain lit where a lamp stands. One hero, the chassis's flood_node, on eight of nine frames. Chassis models for the node, its exploded parts, a rain column, a depth gauge and the crossing itself.",
 "structural_laws": [
  "RAIN IS THE WORLD'S TEXTURE ONLY WHERE A LAMP CATCHES IT. Uniform rain over the frame read as a screen; lit only near a lamp, thinned in the type band and faded above the lamp heads, it read as weather.",
  "A LIT PUDDLE AT THE POST CARRIES THE ACCENT WHERE A RING CAN'T. At cover distance a 4 cm ring is under a pixel, so the amber reads from the water around the post.",
  "A CANVAS MAP NEEDS ITS OWN MATERIAL. A flat slab under the detail line read as a void; a lit stone relief clipped to the county, rougher to the north west, read as the model's surface.",
  "A LEADER FOR A PART ABOVE THE DEK RISES BESIDE THE DEK. Each label takes its own riser, the higher label the inner one, so no two leaders cross."],
 "techniques": [
  "the node in the water to its first sensor from the driver's eye, a near lamp behind the lens lighting its face and a far lamp's streak on the flood",
  "two rain columns square to the lens, the gauge column full and the radar column at four fifths, the node lit beyond them",
  "the node in near elevation through a long lens, leaders routed beside the dek to each part",
  "the enclosure at detail scale from below, silt runs under its lid seam",
  "Bexar County as a raised stone slab among the metro's other counties, the reach circles at the map's own scale in a legend off the county",
  "a built station standing beside its own parts on the asphalt, a cost bar with its zero stop at 0.55 of a centimetre per dollar",
  "a wide glass column filled to the validation share, rain films and drops on the glass, leaders to the rim and the meniscus",
  "the rail at the waterline in macro, the third ring amber where the water reaches it",
  "a pickup turned up the grade away from the water, the node at the waterline in its amber pool"],
 "value": {"per_frame_median_L": meds, "deck_median_L": round(statistics.median(meds), 1), "max_adjacent_delta": round(max(adj), 1), "mean_adjacent_delta": round(sum(adj) / len(adj), 2),
           "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A near black staged deck."},
 "accent": {"hex": "#FFA21F", "name": "beacon amber", "frames_above_floor": accent,
            "note": "A sensor ring the water has reached and the lit water at the post. Above the presence floor on 1, 8 and 9; drawn on 3's two lit rings below it."},
 "ground": {"hex": "#0C0D10", "note": "The deck's declared ground behind the render."}})

put('captions', {
 "date": D, "carousel_no": N, "opening_move": "the place", "structure": "Zoom out",
 "closing_move": "name what is still not public, and how big that is",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas,
 "commas_per_100w": round(100 * commas / words, 2) if words else 0.0, "chars": len(cap.rstrip('\n')),
 "hashtags": re.findall(r'#\w+', cap),
 "critic_note": "The critic chose candidate B, the place-led scene, and the copywriter carried it with light edits.",
 "move_note": "Opens on a low-water crossing in San Antonio, zooms out to the prototype and what the release reports, and closes by asking where the field record is."})
print(meds, accent)
