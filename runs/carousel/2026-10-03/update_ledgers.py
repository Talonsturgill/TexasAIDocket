"""Append this run's entries to the three carousel variety ledgers, measured off the final renders."""
import json, re, sys, statistics, subprocess
from pathlib import Path
REPO = Path('/home/user/TexasAIDocket'); D = '2026-10-03'; N = 41
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
 "date": D, "carousel_no": N, "docket_item": "tx-2026-0198",
 "related_items": ["tx-2026-0196", "tx-2026-0077"],
 "instrument": "Kodiak AI's September 25th release naming Dallas to Houston its driverless launch lane, its September 29th post on IKEA as launch shipper and its September 8th release on safety case readiness.",
 "topic": "Kodiak AI named Interstate 45 from Dallas to Houston its first driverless truck lane, with IKEA as launch shipper on a 219 mile leg, and says it closes its safety case before unsupervised service it expects by year end. Its own readiness measure, the share of the safety case's claims and evidence it calls materially complete, stood at 93 percent at the end of August. Its chief executive says the remaining work is identified and scheduled and concentrated on final engineering verification and validation, and its releases don't say how many of its 3.5 million autonomous miles ran on the lane.",
 "angle": "A tractor and 53 ft dry van loaded a carton stack per point of the company's measure, 93 places loaded and 7 bare at the doors, carried through a Lancaster truck court and the Interstate 45 lane under a norther: the open doors, the truck side on across the field, the cab and van for the IKEA record, 89 delineators for the days left in the year, the van in section with tapes at the earlier readings, the load from a crane, the closed doors running away, the open rear square on for the work left, and a Texan beside it for the miles the releases don't place.",
 "angle_note": "The 93 is never called a safety rating. The observer is never placed aboard in the present tense. Every readiness figure is attributed to the company. The 7 and the 89 are computed, not quoted.",
 "entities": ["Kodiak AI", "IKEA", "Don Burnette"],
 "places": ["Interstate 45", "Dallas", "Houston", "Lancaster", "Baytown", "Frisco"],
 "what_was_refused": "Any independent reading of the safety case. Any crash record for the lane. How many of the company's autonomous miles ran between Dallas and Houston. Any claim that a safety observer is still aboard.",
 "keywords": ["Kodiak AI", "driverless trucks", "autonomous trucking", "Interstate 45", "IKEA", "safety case", "Autonomy Readiness Measure", "verification and validation", "autonomous miles"]})

put('artwork', {
 "date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by out/2026-10-03/update_ledgers.py.",
 "register": "RENDERED, NOT PRINTED. One norther world (stormFront sky, slate haze, low east sun at 11 degrees) declared once in assets/js/deck/2026-10-03-norther.js. One hero built in the chassis: the kit semi_truck with full sensors and a chassis dry_van (doors, 100 load places, decking beams in the accent, floor tapes, a near-wall cut), with delineators and raised pavement markers for the road.",
 "structural_laws": [
  "SEVEN PLACES OF A HUNDRED IN A 53 FT VAN IS A METRE OF FLOOR. From standing eye it is a sliver; raise the camera to 4.5 m or more, or drop the near wall, before asking a reader to see it.",
  "AN EMISSIVE ACCENT IN SUN READS PINK. Albedo near the hex and an emissive at 0.7 brought the beams within the accent window.",
  "INTO THE SUN THE WHITE TRUCK GOES BLACK. Shoot the turn from the lit side or behind the rig.",
  "A FRONT THREE QUARTER OF THE CAB ON TWO FRAMES READS AS ONE DRAWING TO bespoke_check. Change the side of the truck the camera stands on, not the lens.",
  "THE GROUND PATCH CHECK READS THE BAND AT A QUARTER OF THE HEIGHT. A long lens with an empty sky there fails it; tilt down until the horizon and the hero sit in that band."],
 "techniques": [
  "the open van's rear three quarter on the court at 4.7 m eye, the load face with two accent beams and the bare oak at the doors",
  "a long lens across October prairie to the truck side on along the highway, the type on the near grass",
  "a close crop of the cab's roof sensor bar and mirror pod from the next lane",
  "the view over the cab's roof down the southbound lane, 89 delineators 4 m apart ending short of the haze",
  "the van in section side on, the load from the nose, pale tapes at the earlier readings and an accent dimension line from the load face to the doors",
  "the roofless van from a crane off its rear quarter, near wall dropped, both files of stacks and the bare places nearest",
  "the closed rear doors running away up the lane, the flank raked by the low sun",
  "the open rear square on from 5 m up, the bare oak band between sill and load face",
  "a Texan at the van's rear corner on the court, the doors open behind her"],
 "value": {"per_frame_median_L": meds, "deck_median_L": round(statistics.median(meds), 1), "max_adjacent_delta": round(max(adj), 1), "mean_adjacent_delta": round(sum(adj) / len(adj), 2),
           "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. Frame 7 is the declared value cut, the deck's darkest, at the turn."},
 "accent": {"hex": "#B4664F", "name": "dusk_ember, the decking beams across the load face", "frames_above_floor": accent,
            "note": "Only ever the beams at the load face and the dimension line for the open places on frame 5."},
 "ground": {"hex": "#1C2027", "note": "The deck's declared ground, a dark register deck."}})

put('captions', {
 "date": D, "carousel_no": N, "opening_move": "the number that is wrong", "structure": "Ladder",
 "closing_move": "name what is still not public, and how big that is",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas,
 "commas_per_100w": round(100 * commas / words, 2) if words else 0.0, "chars": len(cap.rstrip('\n')),
 "hashtags": re.findall(r'#\w+', cap),
 "critic_note": "The critic chose the candidate opening on the number that is wrong, and its required edits were applied before caption_check passed. The copywriter's concern that 'current' placed the observer aboard in the present tense was taken and the word cut.",
 "move_note": "Opens on the company's own 93, says what it measures and what it isn't, climbs through the lane, the state's terms and the reporting channel, and closes on how many of the company's miles ran on this lane."})
print(meds, accent)
