"""Append this run's entries to the three carousel variety ledgers, measured off the final renders."""
import json, re, sys, statistics, subprocess
from pathlib import Path
REPO = Path('/home/user/TexasAIDocket'); D = '2026-10-06'; N = 44
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
 "date": D, "carousel_no": N, "docket_item": "tx-2026-0203",
 "related_items": ["tx-2026-0061", "tx-2026-0062"],
 "instrument": "The City of Taylor's October 2nd, 2026 news release on the proposed Taylor Technology Campus development agreement and its project page setting the terms beside what applies without them, read on October 6th, 2026, with the city's data center page and KEYE's report on the ballot petition.",
 "topic": "Taylor publishes the terms of a proposed development agreement with Big Watt Digital and PowerHouse Data Centers for the 664-acre Taylor Technology Campus before an October 8th council vote. The land would be annexed. Data centers, generation and batteries would sit at least 700 feet from the south line near FM 112, accessory buildings 500 feet, with a 400 foot buffer and berms at least 6 feet high. Noise would be capped at the greater of 65 dBA or the pre-construction level, set by an acoustic study at the property lines, against the state's 85 dBA without the agreement. Cooling would run on reclaimed water with a 1.575 million gallon initial fill. The developers would commit $28.2 million and seek no abatement. About 1,400 residents had petitioned for a ban that the city found can't go on the ballot.",
 "angle": "A worked Blackland clay field at golden hour, the terms staked as 6 foot survey lath in survey pink. A stake driven at the south line fence, then pulled, then the terms' distances seen from above as raked lines, a sound level meter at the line beside bars for the noise terms, raked lines paced to a hall drawn for scale, a turfed berm with a stake at its toe, the first fill drawn as a basin with a lath drowned in it, the petition's lath in raked blocks, and a stake alone at the fence with FM 112 running into the sun.",
 "angle_note": "Every distance is a minimum the terms write, at least. The hall is drawn for scale and the real buildings' size is not in the record. The basin's 6 foot depth is a drawing rule, not a claim. The 1,400 is KEYE's about. The agreement is a proposal awaiting a vote.",
 "entities": ["City of Taylor", "Taylor City Council", "Big Watt Digital", "PowerHouse Data Centers", "Taylor Technology Campus", "Taylor ISD", "Williamson County", "HALT Taylor Data Centers", "KEYE"],
 "places": ["Taylor", "Williamson County", "FM 112"],
 "what_was_refused": "Any building height or footprint, which the record doesn't give. Any reading of the 65 dBA as a fixed cap, since the pre-construction level could raise it. The attorney general's investigation as part of this project, since Spectrum ties it to Blueprint Data Centers. A Leander item whose host refused every client.",
 "keywords": ["Taylor", "Taylor Technology Campus", "development agreement", "annexation", "data center", "setback", "noise", "reclaimed water", "Williamson County", "council vote", "petition"]})

put('artwork', {
 "date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by out/2026-10-06/update_ledgers.py.",
 "register": "RENDERED, NOT PRINTED. A golden hour deck on Blackland clay. One prairie world (goldenHour sky, warm haze #C9B393, low sun at az -78 el 7) declared once in assets/js/deck/2026-10-06-prairie.js. One hero, the 6 foot survey lath with survey pink flagging, carried through all nine frames as the deck's unit of measure. Chassis kit models for the lath, an earthen berm, a sound level meter on a tripod and a fill basin solved from its volume.",
 "structural_laws": [
  "A DISTANCE STAKED FROM ABOVE NEEDS A RAKED LINE UNDER IT. A row of lath at 120 m is sub-pixel at 432 px, and a bare raked strip lighter than the field is what reads as the line.",
  "AN AERIAL OVER FINE FURROWS ALIASES INTO A LINE SCREEN. Keep furrow pitch over 3 m at 45 m up, or leave the aerial on plain worked clay.",
  "A COUNT OF BLOCKS READS ONLY WHEN EACH BLOCK STANDS ON ITS OWN LIGHTER GROUND. Fourteen squares of lath with no apron read as one dark field.",
  "A STAKE NEARER THE CAMERA THAN THE BERM IT MEASURES STANDS TALLER ON SCREEN UNLESS THE EYE SITS AT ITS HEIGHT OR THE LENS IS LONG. Look along the berm instead so the crest recedes.",
  "A LOW SUN SKY STEPS IN 8 BITS. Deband the flat sky after the snapshot with a window wider than the steps, never under 40 px at 2x."],
 "techniques": [
  "a worked clay field from the FM 112 shoulder at golden hour, ridges raked by the low sun, one flagged lath at the right behind the south line fence",
  "frame 1's camera to the centimetre, the rows gone, one lath pulled and lying on the ridge crests",
  "the field from 60 m over the south line, three raked lines at 400, 500 and 700 feet with pink leaders, a hall beyond the last",
  "a sound level meter on a tripod at the south line beside a flagged lath, two bars at 65 and 85 dBA from one zero",
  "seven raked lines paced from the fence to a hall drawn for scale, a person at the fence beside a lath",
  "a turfed berm seen along its length from its end, a bare lath at its toe",
  "a basin cut in the clay holding the first fill, a lath drowned to its top in the near water",
  "1,400 lath in fourteen raked blocks from 26 m up, two people in the aisle, the far blocks in haze",
  "one flagged lath at the fence, FM 112 running west into the low sun with a pickup and utility poles"],
 "value": {"per_frame_median_L": meds, "deck_median_L": round(statistics.median(meds), 1), "max_adjacent_delta": round(max(adj), 1), "mean_adjacent_delta": round(sum(adj) / len(adj), 2),
           "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A dark clay deck, the sunlit close at frame 9 the declared value cut."},
 "accent": {"hex": "#E05A8F", "name": "survey pink, a staked distance", "frames_above_floor": accent,
            "note": "Measured above the floor on 3 (the leaders), 4 (the WITH bar) and 9 (the flagging). The flagging on 1, 5 and 8 reads smaller than the floor."},
 "ground": {"hex": "#1E1A16", "note": "The deck's declared ground, a dark clay deck with light type."}})

put('captions', {
 "date": D, "carousel_no": N, "opening_move": "the before and after", "structure": "Ledger",
 "closing_move": "name what is still not public, and how big that is",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas,
 "commas_per_100w": round(100 * commas / words, 2) if words else 0.0, "chars": len(cap.rstrip('\n')),
 "hashtags": re.findall(r'#\w+', cap),
 "critic_note": "The critic chose the candidate opening on the before and after, county land with no zoning against the terms in feet. It noted that captions.json's opening_moves_recent lagged one run.",
 "move_note": "Opens on the two states of the land, unzoned in the county or annexed under terms in feet, lays out the terms as a ledger of distances, money and the abatement not sought, and closes on the one measurement the noise term waits on."})
print(meds, accent)
