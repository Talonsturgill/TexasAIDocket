"""Append this run's entries to the three carousel variety ledgers, measured off the final renders."""
import json, re, sys, statistics, subprocess
from pathlib import Path
REPO = Path('/home/user/TexasAIDocket'); D = '2026-10-04'; N = 42
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
 "date": D, "carousel_no": N, "docket_item": "tx-2026-0200",
 "related_items": ["tx-2026-0194"],
 "instrument": "The Texas Tribune and ProPublica's October 1st, 2026 report on TEA's help for Alpha School's AI platform, their September 2nd, 2026 report on Alpha and vouchers, and the State Board of Education's June 2025 minutes.",
 "topic": "The State Board of Education voted the Alpha leaders' AI charter bid down 10 to 3, the Tribune reports. Emails obtained by the Tribune and ProPublica show Texas Education Agency staff then helped Alpha's platform reach districts: the commissioner offered an introduction to Houston ISD's appointed superintendent, staff drafted a to-do list including a single-page explainer for districts, and at least 10 districts were approached. Houston, Aldine and Fort Davis launched supplemental pilots, 5 districts did not pursue it, and the only charter with scores fell short of the passing rate an Alpha leader claimed.",
 "angle": "A noon school day carried by a yellow school bus: the bus on Congress Avenue under the Capitol, an empty hearing room with 10 chairs and 3, the commissioner's quoted line on a sheet on an oak desk, 7 walkers for the return visit, 10 buses on a lot with the 3 pilots on accent bays and 5 stop arms out, a Fort Davis clock with a 2 hour sector, 4 middle schools along an Aldine street, columns at the same scale for the claim and the results, and the bus at a kerb with a parent beside it for the question a reader can ask.",
 "angle_note": "Every 10 to 3 is the Tribune's. The Valenta veto in the board's minutes is never joined to Alpha on the deck. The 50 to 60 percent is always Alpha's claim and never appears without ProPublica's report that TEA's results don't back it. Counts of districts are floors.",
 "entities": ["Alpha School", "Texas Education Agency", "Mike Morath", "State Board of Education", "Houston ISD", "Aldine ISD", "Fort Davis ISD", "Texas Preparatory School"],
 "places": ["Austin", "Houston", "Aldine", "Fort Davis", "Ector County", "Fort Bend", "Irving", "Pecos", "Pflugerville"],
 "what_was_refused": "Any link between the June 2025 Valenta Academy veto and Alpha, which the reporting does not make. Any district contract or board document for the pilots, none of which was found. Any reading of the AI platform's effect beyond the one charter's published scores.",
 "keywords": ["Alpha School", "AI school", "Texas Education Agency", "Mike Morath", "State Board of Education", "charter school", "Houston ISD", "Aldine ISD", "Fort Davis ISD", "two hour learning", "TimeBack"]})

put('artwork', {
 "date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by out/2026-10-04/update_ledgers.py.",
 "register": "RENDERED, NOT PRINTED. A noon deck exposed down to hold the light deck cap. One noonbell world (highNoon sky, pale haze, sun at elevation 58) declared once in assets/js/deck/2026-10-04-noonbell.js. One hero, the kit school_bus unlettered with a white roof, its stop arm out for a no and folded with the accent card for a pilot. Chassis models for the school clock, the measured column, the letter sheet, and limestone ashlar on the rooms' back walls.",
 "structural_laws": [
  "A ROOM BUILT INSIDE A CHASSIS HELPER IS INVISIBLE TO print_ban. Call TXT.interior in the slide and hand the room to the helper.",
  "A KIT MODEL'S size IS NOT ITS TOP. The conference table's size[1] is 1.0 m and its top 0.74 m; measure the top off the model's own box before standing anything on it.",
  "A CANVAS MAP ON A ROUNDED BOX LANDS AT THE WRONG SCALE. Put a drawn wall on a plane of the wall's own size.",
  "THE BOTTOM VEIL PEAKS BELOW THE FOOTER. Over asphalt or shadow, a feathered wash centred on the footer row is what clears 4.5.",
  "A HIGH SUN HIDES EVERY SHADOW BEHIND ITS CASTER FROM A STANDING EYE. Raise the camera over a table or a desk so the top receives what stands on it."],
 "techniques": [
  "the bus at the kerb of Congress Avenue in the near right, stop arm out, the Capitol hazed at the avenue's end",
  "an empty hearing room in limestone, ten chairs and three either side of an aisle before the dais",
  "a near overhead oak desk, one letter sheet with the quoted line, a ballpoint for scale",
  "seven walkers in profile along a school's canopy walk, a long lens across the walk",
  "ten buses nose on in a lot from 10 m up, three on accent bays, five with arms out, two set back",
  "a campus clock in its cast stone surround against the sky, a two hour sector in the accent",
  "aerial down an Aldine street to four middle school wings and Houston's towers in haze",
  "columns at one scale on an oak table in a limestone room, a glass band for the claim and a solid accent column for the result",
  "the bus's front three quarter at a residential kerb, a parent beside it turned away"],
 "value": {"per_frame_median_L": meds, "deck_median_L": round(statistics.median(meds), 1), "max_adjacent_delta": round(max(adj), 1), "mean_adjacent_delta": round(sum(adj) / len(adj), 2),
           "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. Exposed down deck-wide at the round cap (N.EXPOSURE 0.47 in the chassis) so the deck median sits under the ledger's light line of 60, because no. 38 on 2026-09-30 was this window's one light deck."},
 "accent": {"hex": "#C2477A", "name": "the platform, a magenta", "frames_above_floor": accent,
            "note": "The pilot bays and windshield cards on frame 5, the two hour sector on frame 6 and the passed column on frame 8."},
 "ground": {"hex": "#E7E3DA", "note": "The deck's declared ground, a light noon deck with dark type."}})

put('captions', {
 "date": D, "carousel_no": N, "opening_move": "the object", "structure": "Two columns",
 "closing_move": "ask the one question the decision leaves open",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas,
 "commas_per_100w": round(100 * commas / words, 2) if words else 0.0, "chars": len(cap.rstrip('\n')),
 "hashtags": re.findall(r'#\w+', cap),
 "critic_note": "The critic chose the candidate opening on the one-page explainer, the object the emails describe, over the before and after candidate.",
 "move_note": "Opens on the explainer TEA staff helped with, sets the board's vote beside what the agency did, counts the districts approached, piloting and declining, and closes on the Governor's office's standard by asking who in a reader's district decides what counts as proof."})
print(meds, accent)
