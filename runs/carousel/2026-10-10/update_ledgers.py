"""Append this run's entries to the three carousel variety ledgers, measured off the final renders."""
import json, re, sys, statistics, subprocess
from pathlib import Path
REPO = Path('/home/user/TexasAIDocket'); D = '2026-10-10'; N = 48
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
 "date": D, "carousel_no": N, "docket_item": "tx-2026-0212",
 "related_items": ["tx-2026-0117", "tx-2026-0177"],
 "instrument": "Austin Community College's October 9th, 2026 InfoHub post Help Shape ACC's AI Policy Development, the college's AI Resource Hub Responsible Use Guidance page and its About ACC page, all read on October 10th, 2026.",
 "topic": "Austin Community College says it is developing what it calls its first-ever AI policy, shaped by a five rule framework called TRUST that two collegewide committees developed. Its AI Resource Hub already links a PDF titled Acceptable Use of Artificial Intelligence Policy, marked for faculty and staff only. The post names no adoption date, no vote and no adopting body, and opens three October events, a town hall on October 12th, a faculty convocation on October 16th and a community seminar on October 22nd.",
 "angle": "A campus lawn at last light. The kit student desk with its laptop lit and a blank sheet is the hero, standing on a walk of limestone pavers, one per day from the post to the seminar, granite on the three event days. Five rule labels on the desk's parts, 79 desks for 79,000 students, the titled page on the lid, a seated person at the keys, the walk with its three dates, the shut lid at the walk's end, the town hall room at 6:30, and the empty seat on the town hall paver at the close",
 "angle_note": "The desk, the walk, the page and the room are drawn to illustrate. The existing PDF's content was not read, so the deck shows its title and its access label only.",
 "entities": ["Austin Community College", "TRUST framework", "Collegewide AI Strategic Planning and Implementation Steering Committees"],
 "places": ["Austin", "Rio Grande Campus", "Eastview Campus", "Highland Campus"],
 "what_was_refused": "Any reading of the existing policy PDF, which is faculty and staff only. Any adoption date, vote or adopting body, which the post does not name. Any claim about what the new policy will require. The Spectrum News report, whose host disallows the fetcher.",
 "keywords": ["Austin Community College", "ACC", "AI policy", "TRUST framework", "acceptable use", "AI town hall", "community college", "higher education AI", "Austin", "generative AI"]})

put('artwork', {
 "date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by out/2026-10-10/update_ledgers.py.",
 "register": "RENDERED, NOT PRINTED. A staged lastLight deck on a campus lawn (key az -77.7 el 6.4 from the computed sun, ground #0B0A10) declared once in assets/js/deck/2026-10-10-lastlawn.js. One hero, the kit student_desk with its laptop lit and a blank sheet, on all nine frames. Chassis models for a paver walk with granite inlays (one paver per day), a policy sheet, a paperback and a wall clock.",
 "structural_laws": [
  "A GRID COUNT NEEDS ITS UNITS LIT. With the block's lids dark the piece count read the lawn and the desks as one or two pieces, so the lids stay lit low and the far screens alias. The machine queue carries it at repeat 2.",
  "A LIT MATERIAL IN THE ACCENT DRIFTS UNDER A LOW KEY. The granite printed as an unlit material at its hex, which reads as flat paint.",
  "A KIT FIGURE READ UP CLOSE IS A MANNEQUIN. Two panel rounds named the figures on 5, 8 and 9, and the cure was the crop and the silhouette, never the material.",
  "A CAMERA THAT PITCHES DOWN ONTO A DESK PUTS THE LID THROUGH THE DEK. A loop that pitches up until the lid's projected top clears the dek band ends the fight."],
 "techniques": [
  "the desk three quarter on the first paver of a walk across a dark lawn, the granite inlay three pavers ahead",
  "the desk in profile on one paver with five rule labels on DOM leaders to its parts",
  "79 desks with low lit lids in six columns, the hero apart in its own pool, the count asserted in the frame",
  "the laptop square to the camera from above, its lit page carrying the title of the existing PDF",
  "over the shoulder of a seated person cropped at the shoulder, a hand at the trackpad, the blank sheet on the desk",
  "the walk of fourteen pavers from a raised camera, three granite inlays with their dates on the open lawn",
  "the desk side-on on the last paver, the laptop shut with a paperback on it",
  "a dark town hall room from behind the hero desk, the audience in silhouette, a clock at 6:30 beside the window",
  "the desk side-on on the town hall paver with its seat empty and turned to the reader"],
 "value": {"per_frame_median_L": meds, "deck_median_L": round(statistics.median(meds), 1), "max_adjacent_delta": round(max(adj), 1), "mean_adjacent_delta": round(sum(adj) / len(adj), 2),
           "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A near black staged deck."},
 "accent": {"hex": "#9A3B2A", "name": "sunset granite", "frames_above_floor": accent,
            "note": "The granite inlays on the event days of the walk."},
 "ground": {"hex": "#0B0A10", "note": "The deck's declared ground behind the render."}})

put('captions', {
 "date": D, "carousel_no": N, "opening_move": "the correction", "structure": "Pivot",
 "closing_move": "name what is still not public, and how big that is",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas,
 "commas_per_100w": round(100 * commas / words, 2) if words else 0.0, "chars": len(cap.rstrip('\n')),
 "hashtags": re.findall(r'#\w+', cap),
 "critic_note": "The critic chose candidate B, the correction pivot, and the copywriter carried it verbatim; the c19 sentence was later reworded to the source's access label after two judges read it as the document's audience.",
 "move_note": "Opens on the college's own word first-ever, pivots to the use policy PDF its AI site already links, and closes on the question of who decides between the two."})
print(meds, accent)
