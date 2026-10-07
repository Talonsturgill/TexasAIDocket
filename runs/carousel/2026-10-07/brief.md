# Directors' brief, October 7th, 2026 (carousel no. 45)

## The story
Saronic Technologies broke ground on September 30th, 2026 on PORT ALPHA, a shipyard on 835 acres at
the Port of Brownsville, Cameron County, at the mouth of the Rio Grande Valley on the Brownsville Ship
Channel. Saronic builds autonomous surface vessels (Corsair, Mirage, Marauder; the Marauder is 180 ft).
The release calls the yard itself "software-defined", built to deliver autonomous, autonomy-capable
and manned ships. First phase: Landing Craft Utility vessels for the U.S. Navy among them; 2,500+ ft of
deepwater quay; 2 to 4 build positions for final ship erection; 8 to 10 production buildings; vessels
up to 850 ft at first, over 1,200 ft after expansion; up to 10,000 direct jobs; more than $3 billion
private capital. In June the Cameron County Commissioners Court approved a 95% property tax abatement
over 20 years ($211 million, the Tribune reports) BEFORE Saronic had picked the site, with a 35% local
hiring requirement and a reduction if the jobs fall short; opponents said it takes money from public
schools. Record item tx-2026-0204. EVERY FIGURE COMES FROM out/2026-10-07/claims.json, by claim id.
Spine: a thing somebody DID (broke ground) plus the public deal under it (the abatement).
What it can't say: the yard does not exist yet; no ship has been built there; the abatement's terms
rest on the Tribune because the county agenda is a scanned file; whether the jobs arrive is unknown.

## THE ROTATION RULE (travels with every brief)
> The rotation rule changed on 2026-09-16. Read `knowledge/carousel/ILLUSTRATION_SYSTEM.md`,
> "THE DECK IS THE UNIT", and judge against that. If anything in your own definition disagrees
> with it, this paragraph wins. At most TWO of the same archetype in a row and at least THREE distinct,
> not five. ONE hero object, ONE light, ONE grade for the whole deck, and no screen at all,
> because the print register is deleted. Judge
> whether the nine frames read as one deck and whether at least two continuity devices are
> doing real work, and treat a deck that turns the page nine different ways as a FAULT.

## Read before pitching
- knowledge/carousel/ILLUSTRATION_SYSTEM.md (THE DECK IS THE UNIT, THE ARTWORK CARRIES THE DATA, THE WORLD,
  THE SHOWSTOPPER TEST, What still fails)
- knowledge/carousel/ARSENAL.md, ENGINE and KIT sections. The kit has NO ship, NO boat, NO crane, NO quay
  and NO water model. Anything marine is a CHASSIS model built under the kit's conventions
  (metres, y up, origin on the ground, front +z, K.box/K.mat/K.tex), and must be planned at a detail a
  judge will accept at the frame's crop. Kit models you can use as-is: warehouse (production sheds),
  shipping_container, palm, person, crowd, pickup, flagpole, road, streetlight, chain_link_fence,
  city_skyline (far), utility_pole, power_line.
- examples/world-proof/compare.webp and examples/figure-bearing/contact_sheet.webp
- knowledge/carousel/TECHNIQUE_LIBRARY.md, knowledge/carousel/SLIDE_DOSSIER_SPEC.md (CRAFT PLAN)

## Variety ledger, what is off the table
- Worlds of the last twelve decks: goldenHour x4 (latest yesterday, no. 44), blueHour x2, stormFront x2,
  highNoon (10-04), overcast (09-30), nightSodium (09-27). A goldenHour deck today repeats yesterday.
- Accents of the last five: bench green #4FC79A, dusk ember #B4664F, magenta #C2477A, dusk gold #E0956A,
  survey pink #E05A8F. Pick a different accent hex from config/brand.yaml.
- Carried hero objects nos. 40 to 44 (vial, van, bus, hospital, survey lath): judges charged variety
  for "another carried hero object". One hero is the law, so make it vary by STATE and CAMERA hard.
- Count-as-objects frames repeat nos. 38, 41, 43, 44. A tenth count-as-rows frame is a variety charge.
- Last deck's recurring art defects: banded flat sky zenith (keep sky to a third or less, frame toward the
  horizon band, not the zenith), water with regular ripples and no modelled banks, chassis models judged
  primitive at the crop they were shown.

## Craft refresh (Phase 1)
Banding is 8 bit quantisation over a low contrast gradient. A frame that crops the sky to the band near
the horizon, where the haze changes colour fastest, shows fewer rings. Scale cue first: a person, a palm,
a pickup at true scale beside anything big.

## Instincts the machine has confirmed
- Read every repair at 432px against the defect it was meant to cure.
- Write every acceptance item so that rendering NOTHING fails it.
- Make every count on a frame name the set it counted.
- After answering a composition gate, re-read the frame for what the new furniture now asserts.

## What a pitch returns
Nine SUBJECTS and nine LAYOUTS first (names from assets/js/txlayout.js), then the WORLD from the table in
THE WORLD with the reason this story wants that light, the hero by kit model and options or in metres
if it must be built, at least two continuity devices, six frames with data_in_art (figure and the drawn
parameter it sets), the shot per frame (AERIAL/WIDE/MEDIUM/CLOSE/MACRO, none more than three), the
showstopper frame, the tonal arc, the accent hex, and a one-line hook per frame.
