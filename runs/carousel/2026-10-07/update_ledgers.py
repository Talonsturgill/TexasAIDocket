"""Append this run's entries to the three carousel variety ledgers, measured off the final renders."""
import json, re, sys, statistics, subprocess
from pathlib import Path
REPO = Path('/home/user/TexasAIDocket'); D = '2026-10-07'; N = 45
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
 "date": D, "carousel_no": N, "docket_item": "tx-2026-0204",
 "related_items": ["tx-2026-0128"],
 "instrument": "Saronic's September 30th, 2026 release on PR Newswire announcing the Port Alpha groundbreaking, Saronic's home page, and the Texas Tribune's June 18th, 2026 report on the Cameron County tax break, all read on October 7th, 2026.",
 "topic": "Saronic breaks ground on Port Alpha at the Port of Brownsville, a yard it calls software defined for autonomous and manned ships, on 835 acres with an option on nearly 4,400, more than 2,500 feet of quay, build positions for final erection and vessels up to 850 feet. Saronic puts private capital above $3 billion and direct jobs at up to 10,000. The Tribune reported in June that the Cameron County Commissioners Court approved a $211 million tax break, a 95% abatement over 20 years, before Saronic had picked the port, with 35% of the full-time workforce required to be local and the break shrinking if Saronic misses its job projections.",
 "angle": "A humid Gulf noon on the Brownsville Ship Channel. An illustrative autonomous hull carried through the deck, afloat, close at its mast, broadside with its 150 tonne payload as a steel block, on keel blocks at the head of an 850 foot line, and gone from the ground at the close. The release's figures drawn at true scale in bluebonnet plan ink, the commissioners court as the only interior and the turn, and a crew of workers with the local share in the ink.",
 "angle_note": "The hull is drawn to illustrate on every frame that shows it and is not Saronic's design. The squares are equal areas, not the parcel's shape. The jobs figure is Saronic's own. The abatement terms are as the Tribune reported them in June.",
 "entities": ["Saronic Technologies", "Port Alpha", "Port of Brownsville", "Cameron County Commissioners Court", "The Texas Tribune", "Greater Brownsville Economic Development Corporation"],
 "places": ["Brownsville", "Cameron County", "Brownsville Ship Channel"],
 "what_was_refused": "Any reading of the county's agreement beyond the Tribune's report, since the county's agenda files were scanned images with no text. Any job projection the abatement is measured against, which the sources don't give. The hull as Saronic's real design. The governor's release, which the host's robots rule refused.",
 "keywords": ["Saronic", "Port Alpha", "Port of Brownsville", "Cameron County", "tax abatement", "shipyard", "autonomous ships", "jobs", "local hiring"]})

put('artwork', {
 "date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by out/2026-10-07/update_ledgers.py.",
 "register": "RENDERED, NOT PRINTED. A humid Gulf noon deck on the Brownsville Ship Channel. One portalpha world (highNoon sky, haze #D3D8D4, sun at az 25 el 58) declared once in assets/js/deck/2026-10-07-portalpha.js. One hero, an illustrative hard chine autonomous hull built in the chassis, carried through seven frames and absent by design on the courtroom and the close. Chassis kit models for the hull, a keel block line and a riprap bank.",
 "structural_laws": [
  "A WASH RING FLAT ON THE WATER FORESHORTENS TO NOTHING FROM A BANK A FEW METRES UP. Stand the foam on the hull's skin at the waterline instead.",
  "TXT.scatter SEEDS AT Y 0, SO LAND RAISED ABOVE THE WATER BURIES EVERY FIELD UNDER IT. Lift each field by the bank's height.",
  "A TILED GROUND TEXTURE STROBES INTO A CHECKER FROM 1,000 M. Paint soft seeded patches tens of metres across on a canvas instead.",
  "A CROWD LAID OUT BY RANDOM POSITIONS HIDES A THIRD OF ITSELF. When the count is the claim, lay the rows out by projection so every body stays visible.",
  "A BRIGHT WINDOW BEHIND A HEADLINE READS AS A STRIKE WHERE GLYPHS BREAK IT. Keep it within 28 grey levels of the wall behind the type."],
 "techniques": [
  "the illustrative hull afloat three quarters on across the channel from the south bank, the yard bank's palms and sheds in haze",
  "the faceted deckhouse and mast from the yard bank at close range, the far bank low under it",
  "the hull broadside on a long lens with one primer steel block for its 150 tonne payload, three plan ink leaders to labels on the sky",
  "the yard bank from 1,000 m, a graded square for 835 acres and a dashed square for nearly 4,400",
  "the hull on keel blocks on graded clay, the block line and a plan ink line running 850 feet into haze, a person and a pickup",
  "the commissioners courtroom from the back row's aisle, residents seated from behind, the walnut dais cropped past both edges",
  "the bank from 260 m over the channel, the quay line and four build positions, two solid and two dashed",
  "twenty workers in four staggered rows before the hull on its blocks, seven in plan ink vests",
  "frame 5's camera to the centimetre, the hull and blocks gone, their footprint worn into the clay beside the line"],
 "value": {"per_frame_median_L": meds, "deck_median_L": round(statistics.median(meds), 1), "max_adjacent_delta": round(max(adj), 1), "mean_adjacent_delta": round(sum(adj) / len(adj), 2),
           "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A mid light noon deck, the courtroom at frame 6 the declared dip."},
 "accent": {"hex": "#4E5FA8", "name": "bluebonnet, the plan's ink", "frames_above_floor": accent,
            "note": "The ink marks a release figure that is not built, and the seven local vests."},
 "ground": {"hex": "#5E6266", "note": "The deck's declared ground behind the render."}})

put('captions', {
 "date": D, "carousel_no": N, "opening_move": "the quiet decision", "structure": "Clock",
 "closing_move": "ask the one question the decision leaves open",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas,
 "commas_per_100w": round(100 * commas / words, 2) if words else 0.0, "chars": len(cap.rstrip('\n')),
 "hashtags": re.findall(r'#\w+', cap),
 "critic_note": "The critic chose candidate A, the quiet decision told as a clock, over B's two things on a pivot.",
 "move_note": "Opens on the county deciding before the company did, runs the dates in order from the June vote to the September groundbreaking, and closes by asking which projection the break is measured against."})
print(meds, accent)
