# Directors brief, carousel no. 71, November 7th, 2026

## The story (docket item tx-2026-0179)

Dallas put AI-enabled cameras from the vendor City Detect on its sanitation brush and bulky trash
trucks. Side-facing cameras photograph parcels from the public right of way as the truck drives its
route (25 to 35 MPH), software flags possible code concerns (high grass, trash, tires, illegal
dumping, graffiti, boarded windows, collapsing structures), a code compliance analyst reviews each
flag, staff decide whether to send a courtesy notice or open a case, and a code officer inspects
in person before any citation. Faces and license plates are blurred. The December 2025 Finance
Committee briefing says "NOT automated ticketing" and "There is a human in the loop for all
actions". The contract is $852,000 a year, a three-year estimated $2,556,000, terminable on 10 days'
notice.

The counter-image: in four months the cameras photographed more than 20,000 code concerns, and that
resulted in 57 citations at 34 properties, primarily in southern Dallas. About 13,800 of the 20,000
images were in southern Dallas. Council member Chad West asked who can see the images and whether
the system lands harder on lower income neighborhoods. On October 19th, 2026 the council committee
heard that notices will be softened, will carry a QR code to the city's housing resource page, and
that blurring now covers a whole person. Images are kept 12 months. A council member asked for an
audit of the images. The October figures (5,318 observations reviewed, 2,928 courtesy notices, 473
field inspections, 374 voluntary corrections, 101 formal enforcement actions) are NOT a step by step
count. The city gave no timeline and the committee did not ask for another briefing.

The verified claims file is `out/2026-11-07/claims.json` (being finished now). The source texts are
in `out/2026-11-07/tmp/src/` (`a._sanitation_and_code_*.txt` is the city's own briefing,
`ai-flagged-20-000-*` the September piece, `dallas-revises-*` the October piece). Every numeral
drawn must come from a claim. NBC 5 and dallasnews.com are off limits to this project.

Texan profile: places Dallas, a public body, no next step yet. The close must carry the next step,
which the record supports as: a courtesy notice opens no case and sets no deadline, and it will
link to the city's housing resource page.

## What is off the table (the last 30 days of decks)

Nos. 64 to 70: League City plate reader cameras vote (no. 64, a camera story, so this deck must not
look like it: no pole cameras, no plate readers), the Aggie AI Foundry, a San Antonio loose dog
survey, Aurora at a night weigh station, a Permian well pad at last light, a dock door bay at last
light, and an ExxonMobil rig floor at night under floods. Do not reuse: a night industrial pad, a
rig floor, a dock door wedge of light, racks of pipe or coins as counters, a weigh station. No. 61
(Zipline, Round Rock) drew a suburban Texas street by day. This deck is the first residential
Dallas street at night in the window.

## What the last three decks' judges charged (so this deck does not repeat it)

- A hero that reads as rounded boxes from every angle but one (the rig gripper, all three judges).
- A plan-view relief that reads as blinds or a bar chart (no. 70 frame 8, all three judges).
- A kit person front-lit like a mannequin at the wrong depth (no. 70 frame 4).
- Grey noise strata with a dot for a subject (no. 70 frame 7).
- Coin pictograms in a straight-on grid; a dead left half; an unlit silhouette with no rim (no. 68).
- A cold white box room, primitive worker, grey rack faces (no. 69).
The repair that held: crop to the part the chassis builds well, a rim behind the hero, a low raking key.

## Route rules (prompts/carousel_studio.md, binding)

Three distinct visual arguments across the three directors. At least one draws the evidence
directly with a measured scale or a changing material motif. Choose `txthree.js` spatial scenes,
`txbench.js` material reliefs (two materials, real height range, cast shadows, carrier at least 30
percent of the frame), or a deliberate mix. At least six of nine frames physical renders, at least
five standing in a world or a measured relief. One material vocabulary, one light, one grade, one
visual argument. Start in `lastLight` (the default, staged) or `floodlit`; argue any other world.
One subject a third to two thirds of the frame. Light type on the dark field. No plate. Name every
object by its kit model from `knowledge/carousel/ARSENAL.md` (`ranch_house`, `two_story_house`,
`driveway`, `chain_link_fence`, `privacy_fence`, `road`, `streetlight`, `utility_pole`, `live_oak`,
`crape_myrtle`, `pickup`, `sedan`, `person`, interior `desk` and monitors). The kit has NO brush or
garbage truck and no truck camera: say in metres what the chassis builds instead, and prefer
compositions that crop to the part a chassis can build well (the side camera housing on the truck's
flank, a cab door, a grapple jaw at rest) over a whole truck at distance.

Name the hardest frame and why it is buildable. At least six frames declare `data_in_art`, a figure
from the claims and the drawn parameter it sets. Declare at least two continuity devices.

> The rotation rule changed on 2026-09-16. Read `knowledge/carousel/ILLUSTRATION_SYSTEM.md`,
> "THE DECK IS THE UNIT", and judge against that. If anything in your own definition disagrees
> with it, this paragraph wins. At most TWO of the same archetype in a row and at least THREE distinct,
> not five. ONE visual argument, ONE light, ONE grade for the whole deck, and no screen at all,
> because the print register is deleted. Judge
> whether the nine frames read as one deck and whether at least two continuity devices are
> doing real work, and treat a deck that turns the page nine different ways as a FAULT.

## The instincts the machine has confirmed

- Read every repair at 432px against the defect it was meant to cure, because a repair can be worse than the defect.
- Write every acceptance item so that rendering NOTHING fails it, not just so that rendering too much fails it.
- A claim's own paraphrase can assert more than its quote, and every surface downstream inherits the excess.
- Rebuild every artifact DERIVED from a thing you just changed in the same commit that changes it.
- Run house_style_check straight after admitting anything to the record.

## Craft refresh, November 7th (focus: hard-surface models that read as boxes)

- A sharp digital edge looks false because real edges catch a sliver of highlight. A narrow, consistent bevel on each hard edge is what carries the highlight at distance; an inconsistent or heavy bevel reads sloppy. https://3d.irpr.agency/glossary/bevel/ and https://discourse.threejs.org/t/how-to-make-a-rounded-edge-and-rounded-corner-cube-by-buffergeometry-with-split-vertices/36740/3
- Separation on a dark field comes from a narrow light behind and to the side of the subject drawing a line along its contour, the body reflecting a dark surround. https://theslantedlens.com/laws-light-separation/
- Small objects ground best with a tight contact shadow at low opacity, not heavy full-scene occlusion. https://threepipe.org/plugin/SSContactShadowsPlugin.html
