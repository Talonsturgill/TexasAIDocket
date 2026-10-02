"""Append this run's entries to the three carousel variety ledgers, measured off the final renders."""
import json, re, sys, statistics
from pathlib import Path
REPO = Path('/home/user/TexasAIDocket'); D = '2026-10-02'; N = 40
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
 "date": D, "carousel_no": N, "docket_item": "tx-2026-0195",
 "related_items": ["tx-2026-0150", "tx-2026-0101"],
 "instrument": "Texas Children's Hospital's September 28th release on the BRSK1 study, the American Journal of Human Genetics abstract via Europe PMC, the AI-MARRVEL paper's abstract, GeneMatcher's own description and the Texome Project's pages.",
 "topic": "An AI classifier, AI-MARRVEL, flagged a rare change in BRSK1 for a child in the Texome Project whose standard genetic analysis had found nothing. GeneMatcher widened the study to more affected people from unrelated families, fruit fly work showed the human gene largely corrected disabled flies while the patients' variants only partly did, and the researchers name the BRSK1 variants a likely diagnosis. Texome offers free testing to underserved families with a suspected rare disease who can't pay.",
 "angle": "The fruit fly culture vial carried through every frame: on a Houston medical district parapet at golden hour with downtown behind, empty on a consult room desk, marked with the machine's green tape before a monitor carrying the benchmark bars, beside a page of marks and ruled lines, at the end of the tapes for the tool's scores, at macro with its flies down on the food, in a tray beside its siblings, whole again on the coping, and live on the desk under the visit schedule.",
 "angle_note": "Precision and the share of cases found are never called accuracy. Likely is never upgraded to certain. The ten people are never assigned to the seven families. Fly heights are a picture of largely and partially, never a measurement.",
 "entities": ["Texas Children's Hospital", "Baylor College of Medicine", "Duncan Neurological Research Institute", "Texome Project", "AI-MARRVEL", "GeneMatcher", "American Journal of Human Genetics", "Hugo Bellen"],
 "places": ["Houston"],
 "what_was_refused": "Any accuracy figure. Any number of children Texome has reached. Which affected person belongs to which family. Any claim that the software made the diagnosis.",
 "keywords": ["BRSK1", "AI-MARRVEL", "rare disease", "genetic diagnosis", "Texome Project", "GeneMatcher", "fruit flies", "Drosophila", "Texas Children's", "Baylor College of Medicine"]})

put('artwork', {
 "date": D, "carousel_no": N,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, by out/2026-10-02/update_ledgers.py, and the gate suite by exit code.",
 "register": "RENDERED, NOT PRINTED. One goldenHour world declared once in assets/js/deck/2026-10-02-vials.js, the sun raised to 12 degrees with a warmer horizon haze. One hero built in the chassis (fly_vial with climbing, down, partial and empty states, flies posed in bands by state, a wrapped accent tape, cornmeal food) and vial_tray, a parapet coping and city helper, and a consult room whose west window is seen by its barred sun patch.",
 "structural_laws": [
  "A 2D LENS BLUR MASKED BY THE HERO'S SILHOUETTE LEAVES THE WORLD SHARP THROUGH CLEAR GLASS. Blur a band uniformly, inside the glass and out, or not at all.",
  "A ROOM'S WALLS CAST IN TXT.interior, SO A SUN OUTSIDE THEM NEVER ARRIVES. Put the spot inside the wall and cut the window into an unseen occluder half a metre in front of it.",
  "A SUN PATCH OR A HORIZON EDGE BEHIND A LINE OF TYPE IS A STRIKE TO qa.py. Aim the patch below the dek and pad the type band past the last line.",
  "A DARKER TYPE GROUND RAISES CONTRAST AND CAN TRIP THE RULE DETECTOR ON HEAVY SERIF LAST LINES. Reword a short last line rather than darken further.",
  "A FLY AT TRUE SCALE IS A SPECK AT 432 PX. Scale it up, darken the body, fold the wings over the abdomen and pose the flies in bands, so the state reads as a position.",
  "AN EMISSIVE ACCENT DRIFTS OFF ITS HEX UNDER A BRIGHTER SUN. Measure the lit pixels against the hex and saturate the emissive, not the base colour."],
 "techniques": [
  "one fly vial on a parapet coping at golden hour, downtown Houston low behind it",
  "a consult room from the corner, an empty chair, the empty vial small on the desk, the visit schedule on the wall, the window's barred sun on the wall",
  "a monitor carrying two bars at one scale, the marked vial on the desk edge cropped by the bottom",
  "a page pinned on the wall with ten marks and seven ruled lines, the vial in front of its corner",
  "two white tapes projected to one screen length with 98 and 57 filled in the accent, the vial at their end, the skyline behind",
  "a macro on the food with the flies lying on it, the plug's foot at the top edge",
  "five vials in a cardboard tray from close, one label baseline and a bracket over the three patient variant vials",
  "the opening vial whole again on the coping, closer and from a little higher",
  "the consult room again, the vial live with flies on the desk, five visit stickers under the schedule's rule"],
 "value": {"per_frame_median_L": meds, "deck_median_L": round(statistics.median(meds), 1), "max_adjacent_delta": round(max(adj), 1), "mean_adjacent_delta": round(sum(adj) / len(adj), 2),
           "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders. Frame 2 is the declared value cut."},
 "accent": {"hex": "#4FC79A", "name": "a bench marker green, the machine's mark", "frames_above_floor": [1, 3, 5, 8],
            "note": "Only ever the tape on the vial, the AI-MARRVEL bar and the two tape fills. Never a fly."},
 "ground": {"hex": "#20232B", "note": "The deck's declared ground, a dark register deck."}})

put('captions', {
 "date": D, "carousel_no": N, "opening_move": "the correction", "structure": "Pivot",
 "closing_move": "ask the one question the decision leaves open",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas,
 "commas_per_100w": round(100 * commas / words, 2) if words else 0.0, "chars": len(cap.rstrip('\n')),
 "hashtags": re.findall(r'#\w+', cap),
 "critic_note": "The critic chose A, the correction, over B's ledger, and its required edits were applied before caption_check passed.",
 "move_note": "Opens by correcting the headline a reader expects, pivots from the software's flag to the families and flies that tested it, and closes on how many children Texome has reached."})
print(meds)
