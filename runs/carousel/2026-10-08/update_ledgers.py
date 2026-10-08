"""Append this run's entries to the three carousel variety ledgers, measured off the final renders."""
import json, re, sys, statistics, subprocess
from pathlib import Path
REPO = Path('/home/user/TexasAIDocket'); D = '2026-10-08'; N = 46
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
 "date": D, "carousel_no": N, "docket_item": "tx-2026-0205",
 "related_items": [],
 "instrument": "TxDOT's release on Project Nexus, the FAA's September 10th, 2026 release on the Fort Worth launch and its March 9th, 2026 selection release, Merlin's release as GlobeNewswire syndicated it, Joby's September 10th, 2026 release and Dallas Innovates' September 15th, 2026 report, all read on October 8th, 2026.",
 "topic": "TxDOT launches the first phase of Project Nexus at Fort Worth Alliance Airport under the federal eVTOL integration pilot program. Merlin says TxDOT invited it to demonstrate its Merlin Pilot there, including AI-powered air traffic control communications, from a Cessna Caravan. Neither TxDOT's release nor the FAA's names Merlin, and none of the releases says whether a pilot was aboard or prints a measured result. TxDOT runs the program in phases, passengers last.",
 "angle": "Last light on the Alliance apron. An illustrative white Caravan carried through the deck, a fine cyan radio thread from its comm blade to the tower, the record of the releases as a block of airfield lamps with Merlin's photo caption the only lamp lit, the selected projects as threshold stripes, and the close as a lamp per day along a runway edge with the elapsed days lit.",
 "angle_note": "The Caravan, the tower and the radio path are drawn to illustrate. No source places Merlin's and Joby's Caravans side by side. The day count runs from September 10th, 2026.",
 "entities": ["TxDOT", "Federal Aviation Administration", "Merlin", "Joby Aviation", "BETA Technologies", "Archer", "Wisk", "Project Nexus"],
 "places": ["Fort Worth", "Fort Worth Alliance Airport", "Dallas", "Austin", "San Antonio", "Houston"],
 "what_was_refused": "Whether a pilot was aboard Merlin's Caravan, and any result of the demonstration, since no release prints either. A 2029 service date, which only Dallas Innovates reports. Any phase count, which TxDOT does not give.",
 "keywords": ["Project Nexus", "TxDOT", "FAA", "eIPP", "Merlin", "AI air traffic control", "autonomous flight", "Cessna Caravan", "Fort Worth Alliance Airport", "air taxi"]})

put('artwork', {
 "date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by out/2026-10-08/update_ledgers.py.",
 "register": "RENDERED, NOT PRINTED. A staged lastLight airfield deck at Alliance (sun az -104 el 6, haze #1E2536) declared once in assets/js/deck/2026-10-08-nexus.js. One hero, an illustrative white 208B-proportioned Caravan built in the chassis, carried through seven frames and absent by design on the record table and the map. Chassis kit models for the Caravan, an airfield lamp row, a windsock and a control tower, and an apron flood that makes the stage's pool a real light.",
 "structural_laws": [
  "THE STAGE'S POOL DECAL DARKENS EVERY GROUND OUTSIDE ITS HOLE, SO A SPOT LIGHT ON THE APRON SHOWS ONLY INSIDE IT. Light the subject's own pool with the flood, and widen the pool when a second patch must read.",
  "PERSPECTIVE OVERSTATES THE NEAR END OF A RECEDING ROW. A row of lamps whose first 28 of 1,096 are lit reads as mostly lit from beside the near end, so put the camera where the near run is short on screen and the dark ones read as a row.",
  "A LOFT OF THREE STATIONS IS A FACETED CONE. A spinner needs nine stations on an ogive and 64 segments.",
  "A DARK SLAB MAP NEAR THE FIELD'S OWN VALUE COMES APART AT THUMB SCALE. Keep the slab a measurable step lighter than the ground and cut the county lines into it."],
 "techniques": [
  "the Caravan's nose close and low from the left front quarter under the apron flood, a fine cyan thread rising off the comm blade",
  "the Caravan from behind its tail on the ramp, the thread crossing the field to the tower's lit cab",
  "two Caravans in echelon under one flood, one labelled Merlin's, one Joby's J208",
  "the Caravan broadside on a long lens with three cyan leaders to the main gear, the comm blade and the wing root",
  "nine airfield lamps in a three by three block on jointed apron concrete from above, one head lit cyan",
  "the stopped propeller and spinner close, the cowling running off the right",
  "Texas as a stone slab from TXGeo with its county lines cut in and four city lamps, Houston dim",
  "the threshold from 17 m up, eight stripes joined by the bar, one in the accent, the Caravan on the centreline",
  "from the west infield, one lamp per day along the runway edge, 28 lit, the Caravan at the depth of the 28th"],
 "value": {"per_frame_median_L": meds, "deck_median_L": round(statistics.median(meds), 1), "max_adjacent_delta": round(max(adj), 1), "mean_adjacent_delta": round(sum(adj) / len(adj), 2),
           "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A dark staged deck, lifting on the record table and the threshold."},
 "accent": {"hex": "#8FE0F0", "name": "radio cyan", "frames_above_floor": accent,
            "note": "The radio path, the one lit record lamp, the Texas stripe and the elapsed days."},
 "ground": {"hex": "#1E2536", "note": "The deck's declared haze behind the render."}})

put('captions', {
 "date": D, "carousel_no": N, "opening_move": "the plain question", "structure": "Question and answer",
 "closing_move": "name what is still not public, and how big that is",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas,
 "commas_per_100w": round(100 * commas / words, 2) if words else 0.0, "chars": len(cap.rstrip('\n')),
 "hashtags": re.findall(r'#\w+', cap),
 "critic_note": "The critic asked for one rewrite of candidate A and accepted it with one edit.",
 "move_note": "Opens on whether software worked the radio, answers from Merlin's own account and the two releases that skip it, counts the day of the three years, and closes by asking whether three releases' silence on who was aboard and how it went is the whole public record."})
print(meds, accent)
