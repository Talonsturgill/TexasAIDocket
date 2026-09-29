"""Append this run's entries to the three carousel variety ledgers, measured off the final renders."""
import json, re, sys, statistics
from pathlib import Path
REPO = Path('/home/user/TexasAIDocket'); D = '2026-09-29'; RUN = REPO / 'runs/carousel' / D
sys.path.insert(0, str(REPO / 'scripts/carousel'))
from deck_coherence import median_lstar
meds = [round(median_lstar(RUN / f'slides/slide-0{i}.png' if (RUN / f'slides/slide-0{i}.png').exists() else REPO / f'out/{D}/render/slide-0{i}.png'), 1) for i in range(1, 10)]
adj = [abs(meds[i + 1] - meds[i]) for i in range(8)]
cap = (REPO / f'out/{D}/caption.txt').read_text()
body = cap.split('#')[0]; words = len(body.split()); commas = body.count(',')

def put(name, entry):
    p = REPO / 'ledger/carousel' / f'{name}.json'; d = json.loads(p.read_text())
    d['entries'] = [e for e in d['entries'] if e.get('date') != D] + [entry]
    p.write_text(json.dumps(d, indent=1, ensure_ascii=False) + '\n')

put('topics', {
 "date": D, "carousel_no": 37, "docket_item": "tx-2026-0193",
 "instrument": "The SOAH proposal for decision in PUCT Docket 59076 (Item 176), El Paso Electric's application to build the McCloud facility, read with the docket's filing list on the PUCT Interchange, Meta's own announcement of the El Paso data center and KVIA's report of the City Council's counteroffer.",
 "topic": "The SOAH administrative law judges recommend the PUCT approve El Paso Electric's 366 MW McCloud plant, 813 modular gas generators beside Meta's AI data center in northeast El Paso County, only if the utility's other customers are held harmless from its capital and operating costs for the life of the plant. The utility offered a bridge period in which the data center pays the capital costs and would not commit to who pays after it.",
 "angle": "The bridge in the utility's plan against the life of the plant in the judges': a year fence painted for the bridge, then for the whole life, on the same camera, with the judges' findings on need, cost-effectiveness and alternatives set on their own page.",
 "angle_note": "The proposal is a recommendation and never a ruling, so the kicker says PROPOSED and every dek says recommend. The data center is the only retail customer at first, per c9, and the cover says at first. The cost figure is the judges' approximately $499.8 million for the generation facilities, not the $551.8 million that includes transmission and financing. The McCloud tier on the scale frame starts where Region 1 ends, because the judges found existing resources serve Region 1.",
 "entities": ["El Paso Electric", "Public Utility Commission of Texas", "State Office of Administrative Hearings", "Wurldwide LLC", "Meta Platforms", "Enchanted Rock", "City of El Paso", "KVIA"],
 "places": ["El Paso County", "El Paso"],
 "what_was_refused": "Any claim the commission has ruled. Any payer after the bridge. The $551.8 million as the plant's cost. The CEO's 'those costs' line, whose referent the record does not give. Any claim the plant falls short of the data center's load.",
 "keywords": ["El Paso Electric", "McCloud", "Docket 59076", "Meta", "data center", "gas generators", "hold harmless", "PUCT", "SOAH", "Enchanted Rock", "El Paso County"]})

put('artwork', {
 "date": D, "carousel_no": 37,
 "written_from": "deck_coherence's median L* per frame at 432 px off the final renders, by out/2026-09-29/tmp/ledgers.py, and the gate suite by exit code.",
 "register": "RENDERED, NOT PRINTED. One goldenHour world declared once in assets/js/deck/2026-09-29-mccloud.js, the key at azimuth -84 elevation 9 after round one raised it from 3.5, the haze pulled to a dust gold, one hero built in the chassis (modular_gas_genset, padmount_transformer, genset_block) and a yard of 813 units whose units nearest the lens are built as the full model, and one accent, capitol granite #9A3B2A, on the fence panels the data center pays for and a DOM bar on 1, 7 and 8.",
 "structural_laws": [
  "A SUN AT 3.5 DEGREES LIGHTS THE GROUND AT SIX PERCENT OF ITS STRENGTH. Every ground in the first render read as violet asphalt, because at that elevation the sky light carries the ground. At 9 degrees the caliche reads as caliche.",
  "A FENCE SEEN ALONG ITS LENGTH LIES ABOUT ITS OWN RATIO. Five spans of twenty took about 45 percent of the fence on screen. Side on, every span projects at one length and the painted run is the share it stands for.",
  "A PIPE RAIL IS UNDER A PIXEL AT FEED SIZE. The accent had to live on a panel between the rails, and the lit paint had to be set darker than the accent it must read as.",
  "A METALLIC DOOR MIRRORS THE SKY BEHIND THE HOOK. The transformer door read as a lit patch until its paint was made matte and its nameplate hidden.",
  "A SUN BEHIND THE RIDGE STILL LIGHTS THE VALLEY unless the key is dimmed for that frame, because the directional light does not know the ridge is there."],
 "techniques": [
  "a lane between block rows at the yard's west edge with the units within fifty metres built as the full model and a worker in the lane",
  "one block of five on its pad with its transformer, the camera low and pitched up so the block fills the lower half",
  "the whole yard of 813 from 90 m up beside the data hall",
  "a primer beam ruled to the 1,000 MW commitment with the plant's tier laid on it from the end of Region 1",
  "the transformer's cabinet door square to the lens with the judges' two lines set on a page in its pocket",
  "one unit turned so the low sun rakes its intake louvres, the gas riser past its corner",
  "a twenty span fence side on, five granite panels then twenty on one camera",
  "the field into the sun from the public road with the sun behind the Franklin ridge"],
 "value": {"per_frame_median_L": meds, "deck_median_L": round(statistics.median(meds), 1), "max_adjacent_delta": round(max(adj), 1), "mean_adjacent_delta": round(sum(adj) / len(adj), 2),
           "note": "Measured by deck_coherence's median_lstar at 432 px off the final renders."},
 "accent": {"hex": "#9A3B2A", "name": "capitol granite, the costs the data center carries", "frames_above_floor": [1, 7, 8],
            "note": "Painted fence panels on 7 and 8 and a DOM bar on 1, 7 and 8."},
 "ground": {"hex": "#16181D", "note": "The deck's declared ground."}})

put('captions', {
 "date": D, "carousel_no": 37, "opening_move": "the two things", "structure": "Two columns",
 "closing_move": "name what is still not public, and how big that is",
 "first_line": cap.splitlines()[0], "words": words, "commas": commas,
 "commas_per_100w": round(100 * commas / words, 2) if words else 0.0, "chars": len(cap.rstrip('\n')),
 "hashtags": re.findall(r'#\w+', cap),
 "critic_note": "The critic chose the two things. After panel round one the unscoped CEO line came out, because the record does not say what 'those costs' are, the Commission's separate case went in from c25, and the cost line was scoped to the plant's total estimated cost.",
 "move_note": "Opens on the two spans side by side, lays the utility's offer against the judges' condition, and closes on the payer the record does not yet name, put as a question."})
print(meds)
