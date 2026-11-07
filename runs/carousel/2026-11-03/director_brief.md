# Directors room brief, carousel no. 67, November 3rd, 2026

## The story (docket item tx-2026-0239)
Aurora Innovation's Third Quarter 2026 Shareholder Letter, filed with the SEC on October 28th, 2026,
is a company account of AI driving freight trucks with nobody in the cab. Three things it says are
NEW about what the machine does:
- The Aurora Driver "can now autonomously determine if a station is open, navigate to an available
  scale lane, and adapt to different scale configurations" (c9). Until now, autonomous trucks "have
  relied on voluntary enhanced pre-trip inspections (EPTI) to bypass weigh stations" (c8). Three
  steps, figures.json `scale_steps` 3.
- "In November, the Aurora Driver will be operating directly to sites for several driverless
  customers, including automated navigation through security checkpoints" (c6), and site to site
  "for the majority of our customers" over the coming months (c7).
- 20+ driverless trucks are built (c1). It passed 500,000 commercial driverless miles in September
  with 100% on-time delivery since launch, by its own count (c2).
The honest counter-image is in the same letter:
- The production ramp is "about six weeks behind our prior plan" (c12), held back by material
  availability, component quality and issues found in end-of-line testing (c10, `ramp_causes` 3).
  It now expects 20 trucks per week in early December (c11), 200 trucks by the end of February (c15)
  and more than 1,000 in operation at the end of 2027 (c16). All forward looking, all Aurora's.
- Third quarter revenue was $3 million (c13) against an operating loss of $257 million including
  stock-based compensation (c14). Expected 2026 revenue about $9 million (c12).
The Texas places, each with its exact status:
- Dallas to Houston is Aurora's own named commercial route (c21, its September 23rd release).
- Dallas to Laredo is where CHARGER LOGISTICS PLANS to start, under a NON-BINDING MOU for 500
  trucks, with delivery expected in 2027 and 2028 (c3, c4, c19). It is NOT a route Aurora runs
  today. Charger's president is quoted on "autonomous operations along the Laredo corridor" (c5).
- AUMOVIO is finalizing a production line for Aurora's third-generation hardware kit at its
  facility in New Braunfels, Texas, start of production planned for the second half of 2027
  (c17, c18). New Braunfels sits on the Interstate 35 corridor between Dallas and Laredo.
- FMCSA's five-year exemption lets driverless trucks use cab-mounted warning beacons instead of
  roadside triangles (c20, and record item tx-2026-0214).

Claims: `out/2026-11-03/claims.json`, story A ids c1 to c21 ONLY. Figures:
`out/2026-11-03/figures.json`. No other numeral may be drawn or printed. The letter names NO Texas
weigh station and NO Texas customer site, so no frame may say a Texas station or name a station,
city site or customer. A weigh station frame is a generic interstate station, not a located one.

The tension a Texan should feel: the truck now makes the call a driver used to make at the scale
house, and the company that built it is six weeks behind on building the trucks and spends far more
than it earns. The deck neither cheers nor scolds. It shows both halves of the company's own letter.

## Read before pitching
- `prompts/carousel_studio.md` (two render routes, the hardest-frame audition)
- `knowledge/carousel/ILLUSTRATION_SYSTEM.md`: THE STAGE, THE WORLD, THE DECK IS THE UNIT,
  THE ARTWORK CARRIES THE DATA, "What still fails"
- `knowledge/carousel/ARSENAL.md` KIT and ENGINE sections. Name every object by kit model and
  options. The kit HAS `semi_truck` (sensors: "pods", "roof", "full"; trailer, trailerColor,
  lettering), `semi_cab_interior` (a sleeper cab to stand a camera in, `lit`, `curtain`), `highway`
  (lanes, gantry, overpass), `warehouse` (docks, trucks), `road`, `traffic_signal`, `streetlight`,
  `city_limit_sign`, `person`, `pickup`, `gas_station`. The kit has NO weigh station, NO scale
  platform, NO scale house, NO guard booth or boom gate. Anything missing is built ONCE in the
  chassis as a kit model in metres. Say how, so it does not read as a primitive.
- `knowledge/carousel/TECHNIQUE_LIBRARY.md`, `knowledge/carousel/SLIDE_DOSSIER_SPEC.md`
- `examples/bold-proof/README.md`, `examples/world-proof/compare.webp`, `examples/kit/cab-proof.webp`

## The rotation rule (travels with this brief)
> The rotation rule changed on 2026-09-16. Read `knowledge/carousel/ILLUSTRATION_SYSTEM.md`,
> "THE DECK IS THE UNIT", and judge against that. If anything in your own definition disagrees
> with it, this paragraph wins. At most TWO of the same archetype in a row and at least THREE
> distinct, not five. ONE visual argument, ONE light, ONE grade for the whole deck, and no screen
> at all, because the print register is deleted. Judge whether the nine frames read as one deck
> and whether at least two continuity devices are doing real work, and treat a deck that turns
> the page nine different ways as a FAULT.

Layout archetypes: FULL_BLEED, SPLIT_HORIZON, TYPE_AS_OBJECT, OBJECT_AND_CAPTION, DIAGRAM, GRID,
DOCUMENT, MAP, CLOSE_CROP, FIGURE_SCALE. Check a sequence with
`node -e 'require("./assets/js/txlayout.js"); console.log(TXLAYOUT.check([...]))'`. Name at least
two continuity devices.

## Studio rules
- At least six of nine frames physical: `txthree.js` spatial scenes or `txbench.js` material
  reliefs (measured height, two materials, cast shadows, carrier over 30 percent of frame).
- At least five frames stand in `TXT.sky`, `TXT.interior` or a measured `TXBENCH.relief`.
- World: `floodlit` is the natural stage here, a pad at night under one cold LED flood, which is
  what a weigh station and a guard gate are. Its last use was no. 59 on October 24th. The last four
  decks were `lastLight`. Argue for your choice.
- One subject fills a third to two thirds of each frame in a pool of light on a dark field. Light
  type on the dark field. A wash may only darken.
- At least six frames declare `data_in_art`: a figure from figures.json and the drawn parameter it
  sets (3 steps as 3 marks, 20 built as 20 rendered trucks or tractors, 20 per week, 6 weeks as a
  measured offset on a rule, $3 million against $257 million as two lengths at ONE scale, 500
  trucks, 1,000, 2027 and 2028).
- Name the HARDEST frame and its build risk. One evidence frame must draw a computed quantity.
- The close shows the consequence, in a composition different from the cover, and gives the reader
  a next step (the letter is public on the SEC's EDGAR site and the record item tracks it).
- Text stays DOM. No first person, no colons, semicolons, dashes, emojis. Never the words gap,
  matters, pattern.

## What hurt the last three decks (the judges' own words, weakest frames)
- No. 66 (Nov 2, dogs on a night street): "banded clip on a primitive monitor, grey middle"; "slab
  in a void, dead lower third"; "boxy phone slab"; the TXBENCH plug grid read as an "embossed
  calendar". The SDF dog read as a smooth figurine at native size in every round.
- No. 65 (Nov 1, foundry lab): "A toy arm of cylinders and boxes, plain primitives, a mid grey
  floor"; "72 dogbones at relief height 10 read as an embossed calendar tile"; a room's navy back
  wall meeting the bench in a hard band behind the type.
- No. 64 (Oct 31, road paint): "Lower half mid-tone brown, dull dark planks with no focal"; "the
  field bleeds both edges as wallpaper, far rows as bright as near".
Lessons: a grid of identical units in plan reads as a calendar or a vent grille; give units real
height, an oblique camera and a cast longer than their width, and stage the light on part of the
field. A primitive slab as the largest object is charged every round. The kit semi_truck and
semi_cab_interior exist and were judged in no. 41 (October 3rd, a stormFront world): do not repeat
that look.

## Instincts the machine has confirmed (top five)
- Read every repair at 432px against the defect it was meant to cure.
- Write every acceptance item so that rendering NOTHING fails it.
- A claim's own paraphrase can assert more than its quote. Keep Aurora's tense.
- Rebuild every artifact derived from a thing you changed in the same commit.
- Run house_style_check straight after admitting anything to the record.

## Craft refresh (today)
Ambient occlusion over a height field is its own layer multiplied into the shaded relief; a
contact shadow is a blurred top-down pass that belongs UNDER a directional key shadow, never in
place of one; dark carousels with one bold claim on the cover stand out in a white feed.

## Variety exclusions
Opening moves off the table: the two things, the object, the number that is wrong, the correction,
the plain question, the quiet decision. Structures off: Two columns, Pivot, Ladder. Recent accents:
dusk gold #E0956A (66, 61), bluebonnet #4E5FA8 (65, 63), terracotta #B4664F (64), mesquite #6E7A5A
(62). Pick a different accent and give it ONE meaning.

## What to return
One complete treatment: a name, the visual argument in one sentence, the world, the accent and its
one meaning, the continuity devices, nine frames each with layout, the subject (kit model and
options, or metres for a chassis build), the claim ids, the figure it draws, and the camera. Then
the rotation list, the hardest frame and its risk, and how this differs from nos. 64 to 66 and 41.
