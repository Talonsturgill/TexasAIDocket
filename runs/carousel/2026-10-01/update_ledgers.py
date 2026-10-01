"""Append this run's entries to the three carousel variety ledgers, measured off the final renders."""
import json, re, sys, statistics
from pathlib import Path
REPO = Path('/home/user/TexasAIDocket'); D = '2026-10-01'
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
 "date": D, "carousel_no": 39, "docket_item": "tx-2026-0111",
 "related_items": ["tx-2026-0048", "tx-2026-0174", "tx-2026-0180", "tx-2026-0190"],
 "instrument": "The Texas Tribune's September 24th account of Texas cities and counties after the state funding pause, its two August 28th articles on the Governor's order and the $1 auto insurance fee, and the cities' own records from Leander, College Station, El Paso and League City.",
 "topic": "A $1 fee added to Texas auto insurance in 2023 paid for a state network of Flock plate reader cameras through the Motor Vehicle Crime Prevention Authority. In late August the Governor ordered state agencies to pause funding them. At least 14 cities and counties shut off more than 900 cameras, the Tribune reported, while councils split. El Paso directed removal within 60 days, Leander stopped, Kyle kept its contract 6 to 1, College Station kept its cameras 4 to 2, Laredo set a May referendum and League City votes November 3rd.",
 "angle": "One plate reader on a pole carried through every frame: on a road at blue hour, counted as 3,200, dark beside fourteen town lines, unbolted under El Paso's clock, paired under two councils, counted again as 32 and 165 on one lot, and seen through the window of an empty council chamber.",
 "angle_note": "The 900 shut off are never set against the 3,200 funded. No calendar date for the Governor's order or Laredo's vote. League City's ballot was called before the pause and is never framed as a reaction. A removal order is shown as what it calls for, under a dek that says directed.",
 "entities": ["Flock Safety", "Motor Vehicle Crime Prevention Authority", "Governor Greg Abbott", "The Texas Tribune", "El Paso", "Leander", "Kyle", "College Station", "Laredo", "League City"],
 "places": ["El Paso", "Leander", "Kyle", "College Station", "Laredo", "League City", "Plano", "Robinson", "Kendall County"],
 "what_was_refused": "The 900 as a share of the 3,200. A date for the Governor's order or for Laredo's vote. A sum of College Station's two contract figures. Any retention period for the images. Any claim that an El Paso camera has already come down.",
 "keywords": ["Flock Safety", "license plate readers", "plate reader cameras", "MVCPA", "auto insurance fee", "Governor Abbott", "El Paso", "League City", "Laredo referendum", "College Station", "Kyle", "Leander"]})

put('artwork', {
 "date": D, "carousel_no": 39,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, by out/2026-10-01/update_ledgers.py, and the gate suite by exit code.",
 "register": "RENDERED, NOT PRINTED. One blue hour world declared once in assets/js/deck/2026-10-01-plates.js, tuned off the preset's mauve (horizonGlow 0.3, glow 0.4, clouds 0, agx), the key due west with a lit cobra head standing where it is. One hero built in the chassis (plate_reader, the Flock Falcon from its own specification, with on, off and stub states), one accent, highway green #3E8F68, only ever the sheeting of a town limit sign, and shared lots and lenses as chassis helpers.",
 "structural_laws": [
  "THE BLUE HOUR PRESET PRINTS MAUVE through its broad horizon glow and clouds. Turn both down in the deck's own world before a frame is drawn.",
  "BACKLIT GRASS PRINTS BLACK when the key stands behind the camera's view. Fewer, larger, lighter tufts read as pasture; dense small ones read as stipple.",
  "A LAMP HEAD, A ROD OR A SIGN THAT SHARES A SCREEN COLUMN WITH ANOTHER VERTICAL READS AS ONE OBJECT. Every round named a merge somewhere. Place verticals in screen space, not world space.",
  "A COUNT COMPARED ACROSS TWO FRAMES WANTS ONE LOT AND ONE LENS, filled in the same order, so only the count and the ground differ.",
  "A CEILING OR WALL EDGE BEHIND THE HOOK READS AS A RULE THROUGH THE TYPE. Put the room's junction above the kicker or below the dek.",
  "AN ACCENT SURFACE UNDER BLUE HOUR COOLS OFF ITS HEX. A frame whose sign reads too blue takes an emissive tint, measured at thumb scale, not a new hex."],
 "techniques": [
  "one plate reader on the parkway of a four lane road at blue hour, low behind its shoulder, a distribution line and the town limit sign down the road",
  "the same pole in side view with four leaders in the city's own words, a sedan's rear in the far lane, the lit lamp in the sky band",
  "3,200 poles as forty files and eighty ranks on a fall pasture from a raised eye just short of the first rank",
  "a rural two lane road into the seam, fourteen town limit signs stepping out geometrically, the dark reader cropped at the right edge",
  "a standing eye over a footing with four bare bolts, the reader lying back from it, a worker, a truck, a grade rod in sixty bands, a mesa on the horizon, the type at the foot",
  "two identical readers on one curb from a crouch, the lamp between them, the hook and a caption under each pole on a concrete apron",
  "32 poles filling the near ranks of one lot on a mown verge from a shared lens",
  "165 poles filling the same lot to the vanishing point on caliche from the same lens",
  "an empty council chamber from the centre aisle, nine dais chairs, a window behind the dais holding blue hour with a plate reader in silhouette"],
 "value": {"per_frame_median_L": meds, "deck_median_L": round(statistics.median(meds), 1), "max_adjacent_delta": round(max(adj), 1), "mean_adjacent_delta": round(sum(adj) / len(adj), 2),
           "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. Frame 9 is the declared value cut."},
 "accent": {"hex": "#3E8F68", "name": "highway green, a town limit sign's sheeting", "frames_above_floor": [1, 2, 4],
            "note": "Only ever a sign. Frames 1 and 2 carry one sign each, tinted toward the hex because blue hour cools it, and frame 4 carries the fourteen."},
 "ground": {"hex": "#1A2133", "note": "The deck's declared ground, a dark register deck."}})

put('captions', {
 "date": D, "carousel_no": 39, "opening_move": "the deadline", "structure": "Zoom in",
 "closing_move": "name the next event, its date inside the question",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas,
 "commas_per_100w": round(100 * commas / words, 2) if words else 0.0, "chars": len(cap.rstrip('\n')),
 "hashtags": re.findall(r'#\w+', cap),
 "critic_note": "The critic chose B, the deadline, over A's hook. Required edits: vote tallies as words, the Tribune attribution on the 14 and 900, the line narrating the split cut, and one idea per sentence on College Station.",
 "move_note": "Opens on League City's date, zooms from the 2023 fee to the statewide pause to six councils, and closes on the same date as a question a driver could answer."})
print(meds)
