"""Append this run's entries to the three carousel variety ledgers, measured off the final renders."""
import json, re, sys, statistics, subprocess
from pathlib import Path
REPO = Path('/home/user/TexasAIDocket'); D = '2026-10-11'; N = 49
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
 "date": D, "carousel_no": N, "docket_item": "tx-2026-0207",
 "related_items": [],
 "instrument": "The Texas A&M University System's October 7th, 2026 release on West Texas A&M's USDA grant for a research feedlot, USDA NASS Cattle on Feed released September 18th, 2026, and the Texas Cattle Feeders Association's own page, all read on October 11th, 2026.",
 "topic": "West Texas A&M received a $9.75 million USDA grant, which the A&M System calls the largest federal award in WT's history, for a research feedlot near Canyon pairing 90 small research pens with 45 commercial-scale pens, with a required match bringing the project to $19.5 million. The release says new techniques can be evaluated with traditional and AI-powered approaches and names no AI tool, vendor, camera, model or result.",
 "angle": "A Panhandle feedyard at last light. The precast fence line feed bunk is the hero: full with Hereford steers at the rail on the cover, its sections bracketed as the money, the ranch as a square on the mile survey sections, the pens on alleys under sodium lamps, an unset section on dunnage with survey stakes, a line of steers for the cattle on feed count, the release's AI sentence clipped to the rail, a blank tag in a steer's ear, and a person at a fed, empty bunk at the close",
 "angle_note": "The bunks, pens, cattle, stakes and person are drawn to illustrate. No pen size, layout or AI device is in the record. AgriLife's 2019 drone work near Amarillo is a different feedlot and is not drawn or linked.",
 "entities": ["West Texas A&M University", "Texas A&M University System", "USDA", "Texas Cattle Feeders Association", "WT Feedlot Research Group", "Center for Advancing Food Animal Production in the Panhandle"],
 "places": ["Canyon", "Nance Ranch", "Texas Panhandle"],
 "what_was_refused": "Any county named as the site, which the release never does. The awarding agency's own pages, which returned 503. Any AI tool, vendor or result, which the release does not name. AgriLife's 2019 Amarillo drone feedlot as WT's. County hairlines on the map, because no committed or reachable source places Canyon.",
 "keywords": ["West Texas A&M", "WTAMU", "research feedlot", "USDA grant", "Canyon", "Texas Panhandle", "cattle on feed", "beef cattle research", "AI in agriculture", "precision livestock"]})

put('artwork', {
 "date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, layout_check's accent share, by out/2026-10-11/update_ledgers.py.",
 "register": "RENDERED, NOT PRINTED. A staged lastLight Panhandle feedyard (key az -79.1 el 6.1 from the computed sun, ground #0A0909) declared once in assets/js/deck/2026-10-11-feedyard.js, with sodium yard lamps as the one practical. One hero, the chassis's precast J section feed_bunk, on eight of nine frames. Chassis models for the bunk, a plan of pens on alleys, a survey stake, a clipped page, a blank panel ear tag and a yard lamp.",
 "structural_laws": [
  "A LOW SUN ALONG A ROW OF CATTLE SHADES EACH STEER WITH THE NEXT. Run the bunk across the sun, north to south, so every face takes the key.",
  "A BACK WALL SHADES THE THROAT UNDER A LOW SUN. The windrow reads only when the light runs along the bunk or a lamp stands on the pen side.",
  "A KIT STEER BEHIND A NECK RAIL PUTS ITS BACK THROUGH THE DEK. Step the camera back until the body sits under the type band.",
  "A GRID COUNT NEEDS ITS UNITS LIT SEPARATELY. Lamp pools on single pens over near black yard dirt made the pens countable."],
 "techniques": [
  "a full bunk running north to south from a raised alley camera, nine Herefords at the rail, the windrow lit, a blank tag in the nearest ear",
  "four precast sections square on from the pen side, DOM brackets from the projected joints for the grant and each half of the match",
  "a canvas plan at one scale on one mile survey sections, the ranch and the gift as squares of their areas, a leader from Canyon",
  "135 pens on one alley from 40 m up, three sodium pools on the near pens, feathered knock-outs for the labels",
  "an unset section on dunnage on a lit caliche pad, four survey stakes receding with stacked labels",
  "22 steers along a bunk from the alley, the near five in their own pen, the far seventeen instanced",
  "a letter page clipped to the neck rail, the release's one AI sentence set on it with a dusk gold rule",
  "a Hereford's head through the neck rail with a blank dusk gold tag, the bunk lip below",
  "a person three quarters at the rail inside the long pen, dividers cutting the bunk into one long pen and two short ones"],
 "value": {"per_frame_median_L": meds, "deck_median_L": round(statistics.median(meds), 1), "max_adjacent_delta": round(max(adj), 1), "mean_adjacent_delta": round(sum(adj) / len(adj), 2),
           "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. A near black staged deck."},
 "accent": {"hex": "#E0956A", "name": "dusk gold", "frames_above_floor": accent,
            "note": "The blank ear tag on 1 and 8 and the rule beside the AI sentence on 7."},
 "ground": {"hex": "#0A0909", "note": "The deck's declared ground behind the render."}})

put('captions', {
 "date": D, "carousel_no": N, "opening_move": "the who", "structure": "Ledger",
 "closing_move": "ask the one question the decision leaves open",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas,
 "commas_per_100w": round(100 * commas / words, 2) if words else 0.0, "chars": len(cap.rstrip('\n')),
 "hashtags": re.findall(r'#\w+', cap),
 "critic_note": "The critic chose candidate B, the who-led ledger, and the copywriter carried it with light edits.",
 "move_note": "Opens on who pays for half the feedlot, keeps a ledger of what the release counts, and closes on whether WT's Feedlot Research Group will name the tool and report the result."})
print(meds, accent)
