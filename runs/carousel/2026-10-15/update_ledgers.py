"""Append this run's entries to the three carousel variety ledgers, measured off the final renders."""
import json, re, sys, statistics, subprocess
from pathlib import Path
REPO = Path('/home/user/TexasAIDocket'); D = '2026-10-15'; N = 51
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
 "date": D, "carousel_no": N, "docket_item": "tx-2026-0127",
 "related_items": [],
 "instrument": "Courthouse News's October 6th, 2026 report on the Supreme Court of Texas argument in In re Patrick Hughey, the court's submission schedule for October 6th, 2026, its case information for 25-0463 (read September 7th, 2026) and Texas Rules of Civil Procedure 199.1(c) and 203.6(a), read on October 15th, 2026.",
 "topic": "A Montgomery County trial court struck a deposition transcript made with an AI platform in April 2025 because no certified shorthand reporter prepared it. The Ninth District denied relief, the employee petitioned for mandamus on May 29th, 2025, and the Supreme Court of Texas heard argument on October 6th, 2026. Its orders through October 9th, 2026 carry no ruling. The rules already let a written transcription of a recording be used like a stenographic deposition, and let a court require a certified reporter's transcript for good cause.",
 "angle": "A granite courthouse stair with a riser for every month from the strike to the argument, with the bound transcript carried through the deck: on the bottom tread under lit doors on the cover, in the deposition room beside the camera that made the other record, face down on the ledge below the trial court, standing on the filing's tread in the stair's measured elevation, beside the rule under a lamp, on the lectern before a bench with an empty chair, open at its certificate with the argument's minute rail, and open near the top of the flight at the close.",
 "angle_note": "The stair, the courthouse, the office, the room, the bench and every person are drawn to illustrate. No real building is depicted, and the justices are kit figures with no likeness.",
 "entities": ["Supreme Court of Texas", "Montgomery County", "Ninth District Court of Appeals", "Courthouse News", "Jimmy Blacklock", "Jane Bland", "Kyle Hawkins", "Evan Young", "J. Brett Busby", "John Devine", "Bradley Snead", "Stephanie L. Bryant", "Texas Deposition Reporters Association", "Texas Court Reporters Association"],
 "places": ["Montgomery County", "Austin", "Conroe"],
 "what_was_refused": "The court's own case page was not fetched again, because search.txcourts.gov is outside the crawl boundary; the September 7th reading stands and the email says so. The amicus and merits briefs behind the case page were not read for the same reason. The Texas Legislature Online statute pages under capitol.texas.gov/tlodocs were not fetched.",
 "keywords": ["AI transcript", "deposition", "court reporter", "Supreme Court of Texas", "mandamus", "Montgomery County", "Rule 203.6", "certified shorthand reporter", "In re Hughey", "Texas courts"]})

put('artwork', {
 "date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by out/2026-10-15/update_ledgers.py.",
 "register": "RENDERED, NOT PRINTED. A staged lastLight world declared once in assets/js/deck/2026-10-15-transcript.js (key az -58 el 7, ground #08060F), two outdoor sets at night and three rooms. One hero, the chassis's deposition_transcript, on every frame. Chassis models for the transcript, a flamed granite stair with bronze nosings, a court front with lit glass doors, a brick office, a video camera on a tripod, a rule page and a lectern rail.",
 "structural_laws": [
  "A WRAPPED TEXTURE OR NONE. Large blotches drawn without wrapping were cut at every tile seam and read as camouflage blocks at a distance. Every mark is drawn at its neighbours' offsets now, and joints sit on the tile edge.",
  "AN ELEVATION THAT HIDES THE TREADS HIDES THE COUNT. The stair seen square from the side was a flat sawtooth. A quarter turn off its open end gives every month a lit tread over a dark riser.",
  "THE SNAPSHOT STAGES BY DEFAULT. An interior that wants its own room has to say stage false, or the room fogs to the sky's hue and the walnut wall reads navy.",
  "A BENCH OF NINE IS SEEN FROM ITS CENTRE OF CURVATURE. From there every seat stands at one distance and all nine fit one lens."],
 "techniques": [
  "a low wide lens up the whole flight to a dark court front whose glass doors are the only light up there, the transcript in a lamp pool on the bottom tread",
  "a brick office at night among loblolly pines, one glazed room lit with the deposition inside",
  "the deposition room with the camera on its tripod and the transcript on the table, leaders to the camera's lit flip screen and the transcript's cover",
  "a floodlit classical courthouse beyond a granite ledge, the transcript face down on the ledge",
  "the stair a quarter turn off its open end through a long lens, three dated leaders and the transcript standing on the filing's tread",
  "the rule page under a desk lamp with the rule's own words set on its projected corners and a bluebonnet tab at the certified reporter clause",
  "the bench of nine from its centre of curvature, eight seated and one empty, the lectern with the transcript in the near corner",
  "the transcript open at its certificate on the lectern with a twenty segment rail, the last five in bluebonnet",
  "the flight from its top step through a wide lens, the open certificate the one bright thing and the treads falling into the dark"],
 "value": {"per_frame_median_L": meds, "deck_median_L": round(statistics.median(meds), 1), "max_adjacent_delta": round(max(adj), 1), "mean_adjacent_delta": round(sum(adj) / len(adj), 2),
           "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A dark staged deck with one declared value cut into frame 7."},
 "accent": {"hex": "#4E5FA8", "name": "bluebonnet", "frames_above_floor": accent,
            "note": "Certification only: the camera's lit flip screen, the tab and underline at the certified reporter clause, and the rail's five amicus minutes. The AI transcript's own certificate is grey ink, because the struck transcript is never drawn certified."},
 "ground": {"hex": "#08060F", "note": "The deck's declared ground behind the render."}})

put('captions', {
 "date": D, "carousel_no": N, "opening_move": "the before and after", "structure": "Clock",
 "closing_move": "ask the one question the decision leaves open",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas,
 "commas_per_100w": round(100 * commas / words, 2) if words else 0.0, "chars": len(cap.rstrip('\n')),
 "hashtags": re.findall(r'#\w+', cap),
 "critic_note": "The critic chose candidate B, the before and after on a clock. The shipped caption is that candidate after one rewrite of its middle paragraphs, and the copywriter carried it verbatim.",
 "move_note": "Opens on the strike and the argument 18 months apart, walks the clock from the deposition to the bench, and closes on what will count as good cause."})
print(meds, accent)
