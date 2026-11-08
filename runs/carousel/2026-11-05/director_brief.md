# Directors room brief, carousel no. 69, November 5th, 2026

## The story (docket item tx-2026-0241, admitted this run)

Applied Optoelectronics (AOI) of Sugar Land filed its third quarter 2026 results with the SEC on November 5th, 2026,
with its quarterly report on Form 10-Q the same day. It makes optical transceivers, the parts that carry data as
light between machines in AI data centers (800G and 1.6T products). The facts the record holds, by docket claim:

- c1 The chief financial officer says the 2027 capacity expansion plan in the US will take longer to complete "due to
  longer than expected time to obtain necessary electrical power among other construction related issues."
- c2 Total manufacturing equipment capacity is approaching 330,000 units per month (all sites, not only Texas).
- c3 By the end of 2026 it expects equipment installed to produce over 500,000 pieces of 800G and 1.6 Tb products per month.
- c4 It expects capacity over 1 million pieces of 800G and 1.6 Tb transceivers per month by the end of 2027.
- c5 The chief executive says it is scaling 800G and 1.6T manufacturing for demand for AI-related optical technologies.
- c6 It recently secured a multi-year strategic agreement with a Tier 1 hyperscale datacenter customer (unnamed).
- c7 Three manufacturing sites, Sugar Land Texas, Ningbo China and Taipei Taiwan.
- c8 It makes its laser chips ONLY in its Sugar Land facility, where its laser design team is.
- c9 At the Sugar Land headquarters it mainly makes lasers and laser components and some data center transceivers.
- c10, c11 It leases about 209,665 square feet at 1111 Gillingham Lane in Sugar Land, used mainly for manufacturing.
- c12 It bought about 388,133 square feet at 14621 Kirby Drive and 11555 North Spectrum Boulevard in Pearland.
- c13, c14 Two more leased buildings on Chimney Rock Road in Houston, about 356,186 and 737,621 rentable square
  feet, "to be constructed", substantial completion about 16 months after the August 31st, 2026 leases.
- c15 Fort Bend County's abatement agreement places the Sugar Land headquarters zone in Fort Bend County.

What the record does NOT have, so nothing of it is drawn as fact: which building is waiting on power, which utility,
how many megawatts, the hyperscale customer's name, how many people work there, any AI used on the plant floor (this is
AI HARDWARE made in Texas, not AI used to make it). The Pearland and Chimney Rock sites have no sourced county.

The honest shape: a Texas plant that makes the light AI data centers run on says its own growth is waiting on the same
thing the data centers are waiting on, electrical power. The company still states the targets. The deck must keep
"expects" as expects. Figures are company statements and forecasts, never measurements.

## What is off the table (variety ledger, last 30 days)

The last four decks were all SPATIAL SCENES at night with TXBENCH reliefs: a dark interior lab (no. 65), a lastLight
west side block (no. 66), a floodlit weigh station (no. 67), a lastLight Permian well pad (no. 68). Do not pitch a
fifth exterior pad at last light with a kit vehicle or a kit industrial object standing alone. No pump jacks, trucks,
weigh stations, foundry hearths. An INTERIOR clean room or a MACRO bench is the obvious difference this time, and a
pitch that argues for an exterior must say why.

## What failed in the last three decks, by the judges' own words (repair these upstream)

- "A slab in a void", "dead lower third", "empty lower half": a single box-shaped object with an empty field under it.
  Named on nos. 66, 67 and 68 by all three judges. An optical transceiver is a metal box. If a transceiver is a hero it
  must be cropped, opened, angled with its heat sink fins, pull tab, gold edge contacts and fiber ferrules doing the
  work, never a grey brick.
- "Flat painted props", "stickers": accent props painted flat on the canvas instead of lit material.
- Models built from primitives in the chassis read as toys (robot arm, pipe ends as coins, gauge cabinet a plain box).
- "Unlit silhouette, no rim" on the hero: the key behind the subject left it black.
- A TXBENCH relief of round objects in plan reads as dials. A relief of bars reads as a chart.
- A grid of identical units seen straight on reads as a pictogram chart, not as objects.

## The craft refresh (Phase 1)

- Black on black product light: one backlight behind the subject gives the rim, black flags at the sides stop spill, and
  the background must sit far enough back to stay black. https://fstoppers.com/education/photographing-black-product-black-background-453965 , https://petapixel.com/2020/05/23/how-to-shoot-a-rim-light-product-photo-with-one-light
- A semiconductor wafer's colour is thin film interference: three.js MeshPhysicalMaterial `iridescence` with
  `iridescenceThicknessRange` in nanometres (defaults 100 to 400, IOR about 1.3) shifts hue with viewing angle, and a
  thickness map gives a real oxide film's variation. https://threejs.org/docs/pages/MeshPhysicalMaterial.html

## The confirmed instincts (instincts.py --top 5)

1. Read every repair at 432px against the defect it was meant to cure, because a repair can be worse than the defect.
2. Write every acceptance item so that rendering NOTHING fails it, not just so that rendering too much fails it.
3. A claim's own paraphrase can assert more than its quote, and every surface downstream inherits the excess.
4. Rebuild every artifact derived from a thing you just changed in the same commit that changes it.
5. Run house_style_check straight after admitting anything to the record.

## The rotation rule (travels with every brief)

> The rotation rule changed on 2026-09-16. Read `knowledge/carousel/ILLUSTRATION_SYSTEM.md`,
> "THE DECK IS THE UNIT", and judge against that. If anything in your own definition disagrees
> with it, this paragraph wins. At most TWO of the same archetype in a row and at least THREE distinct,
> not five. ONE visual argument, ONE light, ONE grade for the whole deck, and no screen at all,
> because the print register is deleted. Judge
> whether the nine frames read as one deck and whether at least two continuity devices are
> doing real work, and treat a deck that turns the page nine different ways as a FAULT.

## The rules every pitch obeys

- Every frame is RENDERED: `txthree.js` spatial scenes (a room built by `TXT.interior`, or the deck's world with
  `TXT.sky`) or `txbench.js` material reliefs. At least six of nine physical, at least five standing in a world, a room
  or a measured relief. No print screen, halftone, hatch or stipple, ever.
- THE STAGE: start in `lastLight` or `floodlit`, or argue for a dark interior. One subject fills a third to two thirds
  of the frame on a dark field, true blacks and one bright edge. Light type on the dark field. A wash only darkens.
- Six of nine frames carry a figure from the claims in the DRAWING (`data_in_art`), not just in the headline.
- Name every object by its kit model from `knowledge/carousel/ARSENAL.md` (`K.make('structural_frame', {...})`,
  `machine_pad`, `padmount_transformer`, `power_transformer`, `utility_pole`, `server_row`, `server_rack`,
  `vertical_machining_centre`, `document_stack`, `desk`, `monitor`, `laptop`...). A thing the kit lacks (a transceiver
  module, a laser chip, a wafer, a fiber ferrule) is built ONCE in the chassis as a kit-convention model, metres, and
  you state its real dimensions in metres (an OSFP module is about 0.1 m long; a laser chip is a fraction of a
  millimetre, so a macro frame is a macro frame).
- No numeral is invented. Ratios and spans are computed in Python later. A pitch may ask for a computed figure (for
  example the ratio of 1 million to 330,000, or the square feet in the three Texas properties side by side at one scale).
- Text stays DOM. Never type in 3D.
- House rules for any copy you sketch: no colons or semicolons, no em or en dashes, no "cannot", no sentence opening with
  And or But, no first person, ordinal dates month first with no year for this year, never the words gap, matters or
  pattern. Never guess a pronoun for a named person, use the title.

## Read before you pitch

`knowledge/carousel/ILLUSTRATION_SYSTEM.md` (THE STAGE, THE WORLD, THE DECK IS THE UNIT, THE ARTWORK CARRIES THE
DATA, What still fails), `knowledge/carousel/ARSENAL.md` (THE ENGINE and THE KIT), `knowledge/carousel/TECHNIQUE_LIBRARY.md`,
`prompts/carousel_studio.md`, `examples/bold-proof/README.md`, `examples/art-direction-proof/README.md`.

## What to return

ONE treatment: a name, the visual argument in one sentence a reader could see without the headline, the world and why,
the continuity devices (at least two), then nine rows, each with layout archetype (FULL_BLEED, DOCUMENT, FIGURE_SCALE,
OBJECT_AND_CAPTION, GRID, DIAGRAM, CLOSE_CROP, SPLIT_HORIZON), shot (AERIAL, WIDE, MEDIUM, CLOSE, MACRO), subject with
its kit model or its built size in metres, the claim ids, the figure it draws (if any) and what drawn parameter it sets,
and a draft hook of 3 to 8 words. Name your hardest frame and why it is buildable. Then say in two sentences how your
treatment differs from each of nos. 66, 67 and 68.
