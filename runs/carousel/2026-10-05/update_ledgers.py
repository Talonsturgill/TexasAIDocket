"""Append this run's entries to the three carousel variety ledgers, measured off the final renders."""
import json, re, sys, statistics, subprocess
from pathlib import Path
REPO = Path('/home/user/TexasAIDocket'); D = '2026-10-05'; N = 43
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
 "date": D, "carousel_no": N, "docket_item": "tx-2026-0201",
 "related_items": ["tx-2026-0162", "tx-2026-0102"],
 "instrument": "The UT REAL Health AI page announcing its funded pilot projects, read on October 5th, 2026, and the laboratory's own about and symposium pages.",
 "topic": "UT REAL Health AI, the UT System's health care AI laboratory, funded 12 pilot projects out of 120 systemwide submissions, with awards totalling more than $3.6 million. Pilots include a triage assistant called Leah across seven UT hospital sites, referral triage at UTMB Galveston, six Epic tools at Dell Medical School and a suicide risk read of clinical notes across more than 7 million records. Only the no-show project states what it already saved, more than 6,500 appointments and $900,000 at UTHealth Houston, the project's own count.",
 "angle": "One hospital tower at blue hour carries the count: 120 lit bays for the submissions and a 2 by 6 gold block for the funded pilots. The deck goes to an emergency entrance, a nurses' station of six gold screens, one gold screen of ruled notes, a waiting room at one seat per 500 appointments, the facade with one bay burning full and eleven at an ember, a Galveston palm boulevard, a Dallas campus from above with two gold bays, and the first lot again, fuller, with a person walking in.",
 "angle_note": "The 6,500 and the $900,000 are always the project's own count and never an audit. The San Antonio figure is always a projection. The page carries no date, so no award date is stated.",
 "entities": ["UT REAL Health AI", "University of Texas System", "UTHealth Houston", "UT Health San Antonio", "UT San Antonio", "UTMB", "UT Dell Medical School", "UT Southwestern", "UT Tyler", "UT Austin"],
 "places": ["Houston", "San Antonio", "Galveston", "Austin", "Dallas", "Tyler"],
 "what_was_refused": "Any award date, which the page does not give. Any reading of the no-show figure as independently verified. A UT Austin item on the pilots, whose source answered 403. Syndicated coverage on a host the crawl boundary refuses.",
 "keywords": ["UT REAL Health AI", "UT System", "health care AI", "AI pilots", "no-show", "UTHealth Houston", "emergency triage", "referral triage", "Epic", "clinical notes", "symposium"]})

put('artwork', {
 "date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by out/2026-10-05/update_ledgers.py.",
 "register": "RENDERED, NOT PRINTED. A blue hour deck on the humid coast. One wards world (blueHour sky, Gulf haze, lamp key at az -60 el 32) declared once in assets/js/deck/2026-10-05-wards.js. One hero, the kit hospital at ten floors with a chassis bay skin of 120 lit room cards, the funded pilots a 2 by 6 gold block. Lot lamps as downward spot cones, gold screens for the pilots' tools indoors.",
 "structural_laws": [
  "A PANE BEHIND A KIT CURTAIN WALL TAKES THE KIT'S MULLION PITCH. Lay a bay skin as cards proud of the mullions with a dark reveal, or the bays read as barcode and can't be counted.",
  "AN EMISSIVE CARD OR SCREEN ON THE SHADOW MAP SPECKLES. Take panes and screens off receiveShadow.",
  "A LAMP POOL SEEN FROM A STANDING EYE AT 60 M IS A LINE. Stand one lamp inside 30 m of the camera, in open ground, or the pool never reads.",
  "A GRID'S PIECES ARE MEASURED AGAINST THE MEDIAN OUTSIDE ITS RECT. When the type stands on a dark band, the floor has to sit within 12 Lab of that band or the whole floor counts as one subject.",
  "PUTTING ELEVEN BAYS BACK TO THE BASE WHITE SAYS THEY LOST THEIR FUNDING. Dim them to an ember of the accent instead."],
 "techniques": [
  "the hospital tower from the far kerb of its visitor lot at blue hour, 120 lit bays, the gold block on the seventh and eighth floors",
  "the porte-cochere at night from the drive, a worker in the lobby light, a sedan at the kerb, type on the dark apron",
  "a nurses' station of six gold screens on veneer desks before a ribbon of night glass, two leaders",
  "one gold screen of seven ruled blocks on a desk, a chair back at near left, night glass behind",
  "a waiting room from a raised eye, thirteen seated in groups of seven and six, thirty empty chairs beyond, night glazing",
  "the tower face through a long lens, one bay full gold and eleven at an ember",
  "a Galveston palm boulevard at blue hour, lamp pools on the verge, the tower hazed beyond",
  "a Dallas campus from above, the tower on a marked lot, two gold bays, the skyline hazed",
  "frame 1's lot again, fuller, a person walking into a lamp pool"],
 "value": {"per_frame_median_L": meds, "deck_median_L": round(statistics.median(meds), 1), "max_adjacent_delta": round(max(adj), 1), "mean_adjacent_delta": round(sum(adj) / len(adj), 2),
           "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A dark blue hour deck, the waiting room at frame 5 the declared value cut."},
 "accent": {"hex": "#E0956A", "name": "dusk_gold, a funded pilot", "frames_above_floor": accent,
            "note": "The gold bay block on 1 and 9, the gold screens on 3 and 4, the one full bay and eleven embers on 6, two bays on 8."},
 "ground": {"hex": "#16202A", "note": "The deck's declared ground, a dark blue hour deck with light type."}})

put('captions', {
 "date": D, "carousel_no": N, "opening_move": "the place", "structure": "Zoom out",
 "closing_move": "name what happens next and when",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas,
 "commas_per_100w": round(100 * commas / words, 2) if words else 0.0, "chars": len(cap.rstrip('\n')),
 "hashtags": re.findall(r'#\w+', cap),
 "critic_note": "The critic chose the candidate opening on the place, the no-show project at UTHealth Houston, over the candidate opening on who funded the pilots.",
 "move_note": "Opens at UTHealth Houston on the one project that counted what it saved, marks the figure as the project's own and the San Antonio figure as a projection, zooms out to the 12 of 120 and three other pilots, and closes on the symposium's dates with the question of whether a second pilot brings a count."})
print(meds, accent)
