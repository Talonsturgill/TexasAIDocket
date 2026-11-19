# Directors room brief, November 18th, 2026 (BESPOKE run, LOOK V2, tone EXPLAINER)

## The story (docket item tx-2026-0251, statewide, research-and-science)
A UT Dallas team (School of Economic, Political and Policy Sciences; doctoral student Fangchao Dong and associate
professor Muhammad Tauhidur Rahman co-corresponding, doctoral student Hao Chen) studied all 254 Texas counties (c1, c24).
It paired public CDC cancer prevalence data with satellite readings of eight air pollutants taken in 2022 (c2, c4), from
Sentinel-5 Precursor and the Copernicus Atmosphere Monitoring Service (c23), and applied machine learning (c3). The paper
compared four algorithms (c20); a support vector machine fit best, R squared 0.791 (c21). Counties with more pollution
tended to have more cancer (c5). Sulfur dioxide was the most influential environmental predictor (c6, c26). Air falls into
three major clusters (c7): east worst, west best, central in between (c8). High cancer counties sit next to other high
cancer counties rather than at random (c9), Moran's I 0.69 (c22). Ground monitors are costly, which limited earlier
spatial work (c13); satellites let the team look across all of Texas (c17) and the paper says satellite data can support
assessment where ground monitoring is unavailable (c25). THE HONEST TURN: not every more polluted place had more cancer
(c10); cancer reflects many influences (c19); the results are NOT evidence that pollution causes cancer in any one person
(c11); satellite data may be less precise than ground monitors (c12); the team wants more research on cost and accuracy
(c18). Rahman says the method can show where medical centers are and where government should focus (c14). Published
online March 5th in Environmental Monitoring and Assessment (c11); UT Dallas announced it November 6th.
Verified claims: out/2026-11-18/claims.json (c1 to c26). Figures: out/2026-11-18/figures.json (counties 254, pollutants 8,
data_year 2022, clusters 3, algorithms 4, r_squared 0.791, r2_of_100 79, morans_i 0.69).

Integrity limits: this is an ASSOCIATION between places, never causation, never a risk to a person. No county is named as
a cancer hotspot, because no claim names one (the deck may say "East Texas" only as the source says it). No real map data of
cancer rates or pollution per county exists in the claims, so any county map drawn is illustrative and labelled so, and must
not imply specific counties' values; the three clusters may be drawn as east, central, west bands as c8 states. R squared
is a model fit, never "explains 79 percent of cancer". Moran's I is about cancer clustering, not pollution. No CDC or NASA or
ESA logo; Sentinel-5P may be drawn as a generic satellite labelled illustrative. Texan check: statewide. The close carries
the next step a reader can take: the paper is published (Environmental Monitoring and Assessment) and the method is meant
to show where to look first, especially places without ground monitors.

## This is a BESPOKE run. Read knowledge/carousel/BESPOKE.md first, then CLAUDE.md LOOK V2.
Tone EXPLAINER (recent: Nov 14 explainer, 15 people, 16 explainer, 17 watch; explainer fits a method story). Pitch the
deck's VISUAL ARGUMENT and NINE BEATS: for each frame what it must make a reader FEEL and KNOW, the figure it carries
(figures.json key), the claim ids, and a suggested world/camera/medium that differs from both neighbours. No archetype
layout list, no rects, no depth blocks. The deck shares a spine only (tone, palette, grade, type faces, counter, site line,
the accent's ONE meaning, which you propose). Name at least two continuity devices that do real work. Name every kit object
by its model from knowledge/carousel/ARSENAL.md THE KIT, and say in metres what must be built for anything the kit lacks.
Two routes: TXT spatial scenes (txthree.js) and TXBENCH material reliefs (txbench.js); at least six of nine frames physical.
Text stays DOM. No print screen ever. Look at examples/look-v2-proof/2026-11-14/ and examples/bespoke-proof/2026-11-14/.

## What the last decks already did (do not repeat)
Nov 17: a steel scoring machine, a card cabinet drawer, reams of paper, a gold chute to a desk. Nov 16: a gold ribbon under
an open caliper, instruments. Nov 15: student desk from above, gym of desks from bleachers. Nov 14: wafers in a quartz boat,
a county relief (so a Texas county relief needs a clearly different treatment: e.g. not a plain extruded county map).
Nov 13: ERCOT RFI. Judges lately charged: walls filling the top half, subjects cropped, sky banding behind headlines, wavy
kit wood, flat face-on squares with typed labels, type plates reading as UI, top-down trays reading as charts, capsule
people and mannequins, soft kit hands, uncountable blocks at feed size, kit desks and chairs repeated.

## Rotation rule (travels with every brief)
The rotation rule changed on 2026-09-16. Read knowledge/carousel/ILLUSTRATION_SYSTEM.md, "THE DECK IS THE UNIT". On a
bespoke run BESPOKE.md wins: each frame owns its world, light and camera; the spine is tone, grade, type faces and accent.
No screen at all, because the print register is deleted.

## Numbers
No numeral is produced by a model. Every count drawn comes from figures.json. If a frame draws units, the dek says it is
drawn to illustrate.

## House rules for every word you write
No em or en dashes, no colons or semicolons in copy, no first person, "can't" never "cannot", no sentence opening with And or
But, straight quotes, dates "March 5th" with no year. Banned words: gap, gaps, matters, pattern, patterns.

## Instincts (confirmed by three or more runs)
- Read every repair at 432px against the defect it was meant to cure.
- A claim's paraphrase can assert more than its quote. Hold every surface to the quote.
- Write every acceptance item so that rendering NOTHING fails it.
