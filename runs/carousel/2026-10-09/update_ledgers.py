"""Append this run's entries to the three carousel variety ledgers, measured off the final renders."""
import json, re, sys, statistics, subprocess
from pathlib import Path
REPO = Path('/home/user/TexasAIDocket'); D = '2026-10-09'; N = 47
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
 "date": D, "carousel_no": N, "docket_item": "tx-2026-0208",
 "related_items": ["tx-2026-0094", "tx-2026-0151"],
 "instrument": "UTMB's September 22nd, 2026 release on OpenEvidence, OpenEvidence's about page, Texas Health and Safety Code Sec. 183.005, the UT System Regents' August 2026 agenda book item 65, the Regents' meetings page and Regents' Rule 10403, and the PubMed abstract of an MRI survival model with UTMB radiology authors, all read on October 9th, 2026.",
 "topic": "UTMB says OpenEvidence, an AI platform that answers clinical questions with citations, has run inside its electronic health record since March and that more than half of its clinicians use it for clinical decision support. The release prints no count, no total and no accuracy figure. Texas Health and Safety Code Sec. 183.005 already requires a practitioner who uses AI for diagnostic purposes to disclose it to patients. No source says which this is. UTMB's separate Qualified Health AI agreement reaches $9,850,000 on the Regents' consent agenda.",
 "angle": "A clinic's concrete apron on the upper Gulf coast at night under a cold flood. The rolling clinical workstation cart is the hero, its monitor swivelling across the deck. Its back is to the reader on the cover with the clinic lights on the horizon, a cart stands for each campus, a precast barrier is filled to its half tick and left open, aluminium bars show a different tool's published test, galvanized columns at a common scale carry the Qualified Health contract, the statute page lies on an exam room desk, and the screen turns to the reader at the close",
 "angle_note": "The cart, the lights, the screen and the rooms are drawn to illustrate. The statute is never linked to UTMB. The C-index bars belong to a different tool and say nothing about OpenEvidence.",
 "entities": ["UTMB", "OpenEvidence", "Qualified Health", "UT System Board of Regents", "Texas Medical Board", "Texas Legislature"],
 "places": ["Galveston", "Southeast Texas", "Austin"],
 "what_was_refused": "Any link between Sec. 183.005 and UTMB's use, since no source calls it diagnostic purposes. Any accuracy, error or outcome figure, which the release does not print. Any count of clinicians or queries. Any claim that the Regents approved the Qualified Health amendment, since no vote record was read. Any year on the March go-live.",
 "keywords": ["UTMB", "OpenEvidence", "clinical decision support", "electronic health record", "Health and Safety Code 183.005", "AI disclosure", "Qualified Health", "UT System Regents", "Galveston", "medical AI"]})

put('artwork', {
 "date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by out/2026-10-09/update_ledgers.py.",
 "register": "RENDERED, NOT PRINTED. A staged floodlit deck on a clinic's apron at night (key az -50 el 40, haze #0E1220) declared once in assets/js/deck/2026-10-09-chart.js. One hero, a rolling clinical workstation cart built in the chassis, carried through all nine frames, its monitor's swivel the motif. Chassis kit models for the cart, a galvanized column and a precast channel barrier, with a channel fill that takes a computed length.",
 "structural_laws": [
  "K.MAKE RECENTRES A MODEL'S CHILDREN ON ITS BOUNDING BOX. A model whose own geometry is not centred moves under any child added after make(), so build a measured exhibit on its own centre or a fill lands off its tick.",
  "A GRID COUNT AND A LIT APRON PULL AGAINST EACH OTHER. Four carts on one lit ground join into one silhouette at thumb scale, so a count frame keeps the ground dark between its units and seats each on its own pad.",
  "A LIT MATERIAL IN THE ACCENT IS BLEACHED BY A COLD KEY. Print the accent as an unlit material when it carries the record's mark.",
  "A FRAME SHOT DOWN ONTO A CART'S WORK SURFACE PUTS THE MAST THROUGH THE TYPE. Lay a document on a desk beside the cart and light it from the screen out of frame."],
 "techniques": [
  "the cart from behind on the apron under the flood, monitor back to the reader, a hundred amber points on the horizon",
  "the clinician's standing eye over the push bar, the lit answer with citation chips, keys and badge reader, a dark room",
  "four carts through a long lens, each on its own amber pad, the ground dark between them",
  "a precast channel barrier on the apron, the top channel cast amber to its half tick and fading open past it, the cart side on with its monitor edge on",
  "the same barrier and camera, two brushed aluminium bars at one scale and an empty third channel",
  "three galvanized columns at one metre per million dollars, seven clamp sleeves above a weld, the cart dark at their foot",
  "the statute page on a black blotter on an exam room desk, its disclosure block printed in amber, lit from the screen out of frame",
  "an exam room from beside the empty patient chair, the cart's screen turned to it",
  "frame 1's camera returned, the cart turned to face the reader with its answer lit"],
 "value": {"per_frame_median_L": meds, "deck_median_L": round(statistics.median(meds), 1), "max_adjacent_delta": round(max(adj), 1), "mean_adjacent_delta": round(sum(adj) / len(adj), 2),
           "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A near black staged deck, lifting in the exam room on 7 and 8."},
 "accent": {"hex": "#E3A83B", "name": "badge amber", "frames_above_floor": accent,
            "note": "The clinic lights, the campus pads, the half fill and the statute's disclosure block."},
 "ground": {"hex": "#0E1220", "note": "The deck's declared haze behind the render."}})

put('captions', {
 "date": D, "carousel_no": N, "opening_move": "the two things", "structure": "Two columns",
 "closing_move": "name what happens next and when",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas,
 "commas_per_100w": round(100 * commas / words, 2) if words else 0.0, "chars": len(cap.rstrip('\n')),
 "hashtags": re.findall(r'#\w+', cap),
 "critic_note": "The critic took neither candidate as written and adopted a rewrite of candidate A verbatim.",
 "move_note": "Opens on a statute and a release that both describe AI in the health record, sets UTMB's account beside the statute's text without joining them, and closes on the Regents' November meeting and how to testify."})
print(meds, accent)
