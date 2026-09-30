"""Append this run's entries to the three carousel variety ledgers, measured off the final renders."""
import json, re, sys, statistics
from pathlib import Path
REPO = Path('/home/user/TexasAIDocket'); D = '2026-09-30'; RUN = REPO / 'runs/carousel' / D
sys.path.insert(0, str(REPO / 'scripts/carousel'))
from deck_coherence import median_lstar
meds = [round(median_lstar(REPO / f'out/{D}/render/slide-0{i}.png'), 1) for i in range(1, 10)]
adj = [abs(meds[i + 1] - meds[i]) for i in range(8)]
cap = (REPO / f'out/{D}/caption.txt').read_text()
body = cap.split('#')[0]; words = len(body.split()); commas = body.count(',')

def put(name, entry):
    p = REPO / 'ledger/carousel' / f'{name}.json'; d = json.loads(p.read_text())
    d['entries'] = [e for e in d['entries'] if e.get('date') != D] + [entry]
    p.write_text(json.dumps(d, indent=1, ensure_ascii=False) + '\n')

put('topics', {
 "date": D, "carousel_no": 38, "docket_item": "tx-2026-0194",
 "instrument": "The Texas Education Agency's Scoring Process for STAAR Constructed Responses (December 2023) and its Hybrid Scoring Key Questions presentation (March 2024), read with The Texas Tribune's September 4th account of the annual rescore.",
 "topic": "The Texas Education Agency scores the constructed responses on English language STAAR tests with an automated scoring engine first, gives the engine's score as the score of record on about 75% of them, and sends at least a quarter to human scorers. That share is a random sample plus answers the engine flags with condition codes or scores with low confidence. Constructed responses on the Spanish language tests are 100 percent human scored. The agency said about 27,200 students got more credit after content experts reread short typed answers the engine never scored, and a district can request a human rescore for a fee that is waived if the score changes.",
 "angle": "A student desk on a Texas ISD campus stands for a child's written answer: alone on the practice field, as a field of 3,000, as a block of a hundred with a quarter attended, beside its readers, in a classroom where every desk has a reader, as a thousand with the improved share lit, as 27,200 from the same seat, and at the end with a parent reading it.",
 "angle_note": "Nothing says the engine is inaccurate. The September corrections were answers the engine never scored (c20), so the turn says so. No fee amount, no window, no vendor and no location for any scoring. The routing of flagged and low confidence answers to people rests on the agency's own sentence (c33, c34).",
 "entities": ["Texas Education Agency", "STAAR", "The Texas Tribune"],
 "places": [],
 "what_was_refused": "Any claim about the engine's accuracy. The headline's eleven districts improved. A rescore fee or window. A map of the districts. A rubric frame, since no claim carries the rubric's scales.",
 "keywords": ["STAAR", "automated scoring engine", "hybrid scoring", "Texas Education Agency", "rescore", "Spanish STAAR", "constructed response", "A-F ratings"]})

put('artwork', {
 "date": D, "carousel_no": 38,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, by out/2026-09-30/update_ledgers.py, and the gate suite by exit code.",
 "register": "RENDERED, NOT PRINTED. One overcast world declared once in assets/js/deck/2026-09-30-firstreader.js, tuned to a cool luminous lid (zenith 0x8d98a6, horizon 0xe3e6e6), the key at azimuth -40 elevation 48, dark type on the pale sky. One hero built in the chassis (student_desk, a combo chair desk carrying the kit laptop), fields of any count as instanced desks with footprint decals, and one accent, bluebonnet #4E5FA8, only ever the shirt of a person reading an answer.",
 "structural_laws": [
  "A PALE WASH UNDER THE FOOTER OVER A DENSE NEAR FIELD READS AS A SCRIM, and a judge calls it inverted aerial perspective. Darken the near band and set the footer light instead.",
  "A COUNT READ FROM A SEATED EYE HIDES BEHIND FOUR ROWS. 27,200 desks from frame 1's seat read as fewer than 3,000 seen from the stands. Craned up from the same seat, the field reads as the turn.",
  "THE KIT PERSON'S RESIDENT ROLE IGNORES A SHIRT COLOUR, which is what a parent wants and a scorer does not. A person meant to wear the accent is a worker with a shirt, no vest, no hat and dark trousers.",
  "A PERSON STANDING BESIDE A DESK IS NOT READING. All three round 1 judges named it on every reader. The kit person now has read and sit_read, and the chassis places readers in the desk's own frame, one in the seat and one leaning in at its side.",
  "A BRIGHT WINDOW OR A WALL EDGE BEHIND THE HOOK STRIKES THE TYPE. An interior frame's window goes at sill height in the frame's own code, so the wall above stays one plain value behind the type.",
  "A SHARE WANTS ONE CAMERA ON BOTH SIDES. Frames 3 and 6 share a camera, a quarter attended of a hundred and seventeen of a thousand."],
 "techniques": [
  "one combo desk alone on a straw practice field at a seated eye, three quarter, its laptop lit, the school wing and flags in haze",
  "3,000 instanced desks on the school's football field from above the south end zone past the goal post",
  "a block of one hundred desks with the attended quarter as the near left five by five, two readers at each",
  "a row of four desks from off the row's end, the nearest read by one person seated at its screen and one leaning in, three mono labels on DOM leaders landing on the screen",
  "a classroom row of five desks at seated eye, a reader seated and bent to the screen at every one, a window band at sill height behind them",
  "one thousand desks from frame 3's camera, every screen dark but seventeen, a content expert seated at each lit one",
  "27,200 desks craned up from frame 1's seat, running to the school, one content expert leaning over a desk in the near rows",
  "a covered entry walk built out from the school's doors, the parent walking it",
  "frame 1's desk and camera with the parent at its side, leaning over it to read the screen"],
 "value": {"per_frame_median_L": meds, "deck_median_L": round(statistics.median(meds), 1), "max_adjacent_delta": round(max(adj), 1), "mean_adjacent_delta": round(sum(adj) / len(adj), 2),
           "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders."},
 "accent": {"hex": "#4E5FA8", "name": "bluebonnet, a person reading an answer", "frames_above_floor": [3, 4, 5, 6, 7],
            "note": "Shirts only, and only on a person reading: the readers on 3, 4 and 5 and the content expert on 7. Frame 6 seats a content expert at each of the seventeen lit screens that improved. The parent on 8 and 9 wears her own shirt so she never reads as staff."},
 "ground": {"hex": "#D7D9DA", "note": "The deck's declared ground, a light register deck."}})

put('captions', {
 "date": D, "carousel_no": 38, "opening_move": "the plain question", "structure": "Question and answer",
 "closing_move": "ask the one question the decision leaves open",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas,
 "commas_per_100w": round(100 * commas / words, 2) if words else 0.0, "chars": len(cap.rstrip('\n')),
 "hashtags": re.findall(r'#\w+', cap),
 "critic_note": "The critic chose the plain question over the before and after, which failed the length band and closed on a restatement. Two fixes: 'written' in the hook to match c1, and the fee introduced before it is waived. Round 1's judges cut the line narrating the deck, the same defect cut on September 24th and 26th, and asked for the why (c14) and the attribution of the review figures.",
 "move_note": "Opens on the question a parent would ask, answers it with the Spanish exception, and closes on whether a family should have to ask for a person. The critic noted the 'Who' opener is starting to repeat and the next plain question should not start with it."})
print(meds)
