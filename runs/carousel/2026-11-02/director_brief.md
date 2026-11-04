# Directors room brief, carousel no. 66, November 2nd, 2026

## The story (docket item tx-2026-0236)
San Antonio Animal Care Services and Southwest Research Institute (SwRI) are running an automated
survey of unrestrained dogs. A cell phone mounted on a vehicle window films the street, and object
detection and data analysis software picks dogs out of the video. Automated AND human review of the
clips then checks four things about each detected dog: was it unrestrained, was anyone supervising
it, how many dogs were present, and was it owned or a stray. The owned or stray call is made by
APPEARANCE: "Strays appear to be malnourished and skittish, while dogs that seem healthier and more
approachable are likely owned by local families and are classified as roaming." The project repeats
the city's 2019 manual (volunteer) count in the same 32 study areas. Field research runs October to
December 2026, then a final report with summary data and videos goes to Animal Care Services. Both
the city and SwRI say it is a SAMPLE, not a count of every dog: "Because the project uses a sampling
methodology, it is not intended to count every unrestrained dog in San Antonio." The 2019 study's
findings were not reachable this run, so no 2019 count may appear anywhere.

Claims: `out/2026-11-02/claims.json`, ids c1 to c22 only (story A). Figures:
`out/2026-11-02/figures.json` (study_areas 32, prior_survey_year 2019, survey_year 2026,
years_between 7, field_months 3, review_checks 4, classes 2). No other numeral may be drawn.

The honest tension a Texan should feel: a machine is now deciding, from how a dog LOOKS through a
car window, whether it is somebody's pet or a stray, and a human checks the clip. The deck must not
claim accuracy, results or counts. None exist yet.

## Read before pitching
- `prompts/carousel_studio.md` (two render routes, the hardest-frame audition)
- `knowledge/carousel/ILLUSTRATION_SYSTEM.md`: THE STAGE, THE WORLD, THE DECK IS THE UNIT,
  THE ARTWORK CARRIES THE DATA, "What still fails"
- `knowledge/carousel/ARSENAL.md`: KIT and ENGINE sections. Name every object by kit model and
  options (`K.make('sedan', {...})`). The kit has `sedan`, `pickup`, `ranch_house`,
  `chain_link_fence`, `privacy_fence`, `driveway`, `road`, `streetlight`, `utility_pole`,
  `stop_sign`, `crosswalk`, `person`, `live_oak` and more. **The kit has NO dog and NO phone.**
  Anything the kit lacks is built ONCE in the chassis as a kit model in metres. A dog is the
  hardest subject in this story: say exactly how it would be built so it does not read as a toy
  (the last deck's robot arm was charged as "a toy of cylinders and boxes" by all three judges in
  every round). A treatment that keeps the dog small, at distance, in silhouette, or seen as a
  detection on a phone screen is allowed and may be wiser.
- `knowledge/carousel/TECHNIQUE_LIBRARY.md`, `knowledge/carousel/SLIDE_DOSSIER_SPEC.md`
- Look at `examples/bold-proof/README.md` and `examples/world-proof/compare.webp`.

## The rotation rule (travels with this brief)
> The rotation rule changed on 2026-09-16. Read `knowledge/carousel/ILLUSTRATION_SYSTEM.md`,
> "THE DECK IS THE UNIT", and judge against that. If anything in your own definition disagrees
> with it, this paragraph wins. At most TWO of the same archetype in a row and at least THREE
> distinct, not five. ONE visual argument, ONE light, ONE grade for the whole deck, and no screen
> at all, because the print register is deleted. Judge whether the nine frames read as one deck
> and whether at least two continuity devices are doing real work, and treat a deck that turns
> the page nine different ways as a FAULT.

Layout archetypes: FULL_BLEED, DOCUMENT, FIGURE_SCALE, OBJECT_AND_CAPTION, GRID, DIAGRAM,
CLOSE_CROP, SPLIT_HORIZON (see `assets/js/txlayout.js`). Name at least two continuity devices.

## Studio rules
- At least six of nine frames physical: `txthree.js` spatial scenes or `txbench.js` material
  reliefs (measured height, two materials, cast shadows, carrier over 30 percent of frame).
- At least five frames stand in `TXT.sky`, `TXT.interior` or `TXBENCH.relief`.
- Start in `lastLight` or `floodlit`: dark field, one subject filling a third to two thirds of the
  frame in a pool of light, light type on the dark field, never a pale wash. A San Antonio street
  at dusk under a streetlight is a natural staged world.
- At least six frames declare `data_in_art`: a figure from figures.json and the drawn parameter it
  sets (32 study areas as 32 measured tiles, the four checks as four marks, two classes as two
  states, 2019 to 2026 as a measured span).
- Name the HARDEST frame and its build risk. One evidence frame must draw a computed quantity.
- The close shows the consequence, in a composition different from the cover.
- Text stays DOM. No first person, no colons, semicolons, dashes, emojis. Never the words gap,
  matters, pattern.

## What hurt the last three decks (the judges' own words, weakest frames)
- No. 65 (Nov 1, foundry lab): "A toy arm of cylinders and boxes, plain primitives, a mid grey
  floor"; "a beige slab in the grey middle, a thick flat ring for the mark"; "72 dogbones at relief
  height 10 read as an embossed calendar tile". The audition took sixteen readings because render
  settings (metal read as wood, a practical light clipping neighbours) were found late.
- No. 64 (Oct 31, road paint): "Lower half mid-tone brown, dull dark planks with no focal";
  "the field bleeds both edges as wallpaper, far rows as bright as near".
- No. 63 (Oct 30, balance weights): "A generic CG dais with bright streak-noise wood"; "a flat grey
  sheet reading as a diagram card"; "a dead lower zone".
Recent decks were all lastLight staged interiors or road surfaces with TXBENCH reliefs. Be visibly
different from a lab, a balance and road paint.

## Variety exclusions
Caption opening moves used in the last six runs: the before and after, the two things, the
object, the number that is wrong, the correction, the plain question. Recent worlds: foundry
interior, road paint at dusk, brass balance in a case.

## Instincts the machine has confirmed
- Read every repair at 432px against the defect it was meant to cure.
- Write every acceptance item so that rendering NOTHING fails it.
- A claim's own paraphrase can assert more than its quote. Stay inside the quotes.

## Craft refresh (this run)
- Fur reads when normals are perturbed by fractal noise stretched along the body (ThreeMojo
  animals, github.com/SethKitchen/ThreeMojo/wiki/Animals). Lathe geometry suits tapered torso and
  limbs.
- A single streetlight as subject, a warm amber pool, is a classic night street composition.
EOF
