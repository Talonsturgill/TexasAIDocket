# Carousel no. 76, November 13th, 2026: the empty yard

## The story, and what the fact check did to it

On November 5th, 2026 ERCOT gave the Public Utility Commission a preliminary summary (c1, c2) of its Data Center State and
Community Impact RFI. It went to 465 loads (c3). 433 of 465 (93%) submitted, covering about 177 GW, about 97% of the
interconnection capacity requested (c4). 417 came in on time and 16 late (c5), and 32 Medium Load responses had not
arrived (c6). All 245 Large Loads, those of 75 MW or greater, answered (c7), and they hold about 94% of the capacity, about
166 GW (c8). 33 projects ask for more than 1 GW each and hold 36% of it (c9). Every load zone has requests and West Texas
holds the plurality, 41%, 73 GW (c10). By zone, on 429 reviewed loads with NOIE zones left out and each load's zone set at
interconnection (c15, c16): West 88 Large, 39 Medium, 73 GW (c11), North 69, 85, 45 GW (c12), South 72, 38, 49 GW (c13),
Houston 14, 24, 10 GW (c14). Respondents answered 83% of nearly 67,000 questions (c17). Cooling questions had the highest N/A rate, fourth of five by count (compute.py, cooling_rate_rank and
cooling_count_rank), and many projects had not determined their final cooling configuration (c18). N/A ran about 16%
for Large Loads and 19% for Medium (c19), and projects due in 2028 or later answered N/A 30% more often (c20). ERCOT targets
a published final report on December 10th (c23). In the separate Batch Zero verification, ERCOT reviewed responses from 257
developers, about 5,140 questions (c24), is sending a second round to 80% of developers with a 5 business day deadline (c25,
c26), must finish this month to report on December 10th (c27), and names recurring problems including site control and
financial security (c28 to c31). The commission's calendar lists an open meeting on December 17th (c38).

The fact check took two things out. The per-row cooling and water N/A shares can't be quoted, so no frame prints or draws a
cooling percent. The cooling finding is a sentence (c18) and the deck carries it as a place, a poured pad with nothing on
it, never as a number. Every frame says preliminary where its claim does.

Docket item tx-2026-0072, statewide, on ERCOT.

## Why this treatment, and what was grafted

Base: THE EMPTY YARD. The finding a reader can't see in a table is that projects knew how much power they wanted and many
could not yet say how they would cool the building. A construction site makes that visible without a percent: primer steel
going up, power arriving, and a cooling yard poured, bolted and empty. Grafted from LAYDOWN YARD: capacity drawn as copper
bus bar, one lamination per gigawatt at one thickness, so 177 GW is a pack a worker stands beside (3) and the four zones
are four packs at one depth (4), and the Large Loads as cable reels, one reel per load (2). Dropped from LAYDOWN YARD: the
floodlit world (no. 73 was floodlit three days ago) and the 465 reel cover. Dropped from RECOVERED CORE: core boxes and
rubble (a millimetre per question needs explaining before it can mean anything at feed size), kept its rule that the
unanswered share is one continuous length, never a slot per respondent. Dropped from THE EMPTY YARD: the steel column
ruler (a bar chart in steel) and two DOCUMENT frames (the claims are words and the dek carries them).

## The world, and the laws that hold it

`lastLight`, staged. The sun is just down to the west. The key is azimuth -58, elevation 9, low on the left, so every cast
runs to the right and the anchor bolts, pad edges and lamination edges catch it. A cool rim from the back right edges the
dark steel. The whole site is staged as one subject in a pool on caliche, and the world behind it goes dark. Type is light
on the dark sky. A wash only darkens. The relief (5) reads the same key from the chassis.

## Palette

caliche lit #E4D8C3 falling to night #08060F, red oxide primer #7A3826, weathered concrete #8E8A82, raw copper #B87350,
galvanized grating #9AA0A6, black XLPE cable, Southern yellow pine reel timber #A8824E, mesquite olive grey, the warm seam,
dusk_ember #B4664F.

The accent is brand.yaml's dusk_ember #B4664F and means ONE thing: left blank. It is the painted layout line round each
empty equipment pad (1, 6, 7, 9), the epoxy lining of the trench's open stretch (5) and the caps on the empty pad's
conduit stubs (7). Copper is a material, never the accent. Nothing answered is ember.

## The continuity devices

CONTINUITY: CAMERA_MOVE, MOTIF_EVOLUTION, VALUE_ARC

1. **Camera move through one site plan.** Low at the pad edge (1), over the reel yard (2), beside the copper pack (3), the
   four packs at one depth (4), straight down into the trench (5), up over the whole yard (6), down to ankle height on one
   empty pad (7), into a bay of the frame (8), and out to the road (9).
2. **Motif evolution, the ember line.** Round the empty pads (1), lining the open trench in plan (5), round the empty pads seen whole from above (6),
   on one pad's capped conduits (7), still bare at night (9).
3. **Value arc.** The warm seam behind the frame on 1, copper and steel catching the low key on 2 to 4, steel and epoxy in
   the relief on 5, the yard in one pool on 6, a single pad on 7, one work light in a bay on 8, the darkest frame from the
   road on 9.

## The rotation

FULL_BLEED, GRID, FIGURE_SCALE, DIAGRAM, CLOSE_CROP, SPLIT_HORIZON, CLOSE_CROP, OBJECT_AND_CAPTION, FULL_BLEED.
`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | WIDE, eye 4.6 m, raised three quarter 24 m from the yard's centre, fov 40 | four chassis equipment_pad models in weathered concrete with ember layout lines, galvanized anchor bolts and capped conduit stubs, TXT.contact under each, the kit structural_frame in primer rising behind against the sky, raked by the low key with casts running right, TXT.weather grime on the slab edges |
| 02 | MEDIUM, eye 6 m, 14 m in front of the reel block, fov 30 | the chassis cable_reel instanced 245 times, galvanized flanges with ribs, wound black XLPE, a lit front block of 33 in the pool, TXT.contact under the front row |
| 03 | MEDIUM, eye 1.6 m, 7 m from the pack's end face, fov 32 | the chassis bus_pack of 177 copper laminations with darker spacers every tenth bar, on grey standoff insulators over oak dunnage, the kit person beside it lit from the camera side, TXT.contact under dunnage and boots |
| 04 | CLOSE, eye 0.9 m, 9 m from four packs set at one depth, fov 28 | four chassis bus_pack models of 73, 49, 45 and 10 laminations, raw copper with mill streaks in the roughness and dark fibreglass spacers every tenth bar, raked by the low key so every lamination edge catches, seated on grey epoxy insulators over oak dunnage with TXT.contact, oxidised at the cut ends, caliche falling to black behind |
| 05 | MACRO, orthographic relief | the chassis cable_trench in plan through TXBENCH.relief, concrete curbs, galvanized bar grating over the answered share, the open stretch lined in ember epoxy, caliche either side |
| 06 | AERIAL, 9 m up on the west side looking down across the yard, fov 50 | the whole yard as one staged subject: four empty equipment_pad models in a row in the pool, the kit person standing on the nearest pad |
| 07 | CLOSE, eye 1.5 m on one equipment_pad, fov 38 | one chassis equipment_pad cropped by the left and bottom edges, broom finished concrete, galvanized J bolts with nuts, two rows of ember capped conduit stubs, the later row longer by na_later_pct, and the ember layout line, a chassis cable_reel beyond the slab, TXT.contact and weathering |
| 08 | MEDIUM, eye 1.5 m inside a bay of the frame, fov 34 | the kit person in the read pose at a chassis plan_table of plywood on sawhorses with the kit document_stack, one chassis work_light on a tripod lighting the figure from the camera side, primer columns framing the bay |
| 09 | WIDE, eye 3.4 m on the kit caliche_road outside the kit ranch_gate, 40 m from the yard, fov 32 | the kit structural_frame in red oxide primer with mill scale mottle, a silhouette rim lit on the seam, TXT.contact at every column base and grime weathered on the lower columns, with the pool holding the four empty chassis equipment_pad models, the galvanized ranch_gate and fence between the road and the yard |

Showstopper frame: 06, four bolted pads outlined in ember with nothing on them, seen whole from above in one pool, and one
worker standing on the nearest.
Tonal arc: the warm seam behind the frame on 01, lit galvanized flanges on 02, copper edges on 03 and 04, steel and epoxy on
05, the yard in one pool on 06, one pad at ankle height on 07, a work light in a dark bay on 08, the yard from the dark road
on 09.
VALUE CUT: frame 5. The deck leaves the site for the trench in plan.

---
```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: four empty concrete equipment pads outlined in ember with anchor bolts and capped conduit stubs, close in the foreground, and the primer steel frame of a data hall rising behind them into the dark sky
  rect: [0, 930, 1080, 420]
  bleeds: [left, right, bottom]
accent: '#B4664F'
job: Say the whole finding in one image, the steel going up and the cooling yard empty, before any figure is read.
claims: [c1, c2, c3, c4, c18]
numerals:
- {value_from: c4}
- {value_from: c3}
- {value_from: c1}
depth:
  eye: 4.6
  horizon: 560
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'A low three quarter across the near pad; the four pads recede to the right, the primer frame stands behind them on the left half against the seam.', bands: 'Top third, the type on the dark sky. Middle third, the primer frame and the seam. Bottom third, the near pad''s weathered concrete slab lit by the low key with its ember layout line, galvanized anchor bolts and capped conduit stubs each casting long to the right across the broom finish, and the shadowed caliche falling dark at the bottom edge.', focal: the near pad's ember corner and its anchor bolts}
art:
  technique: physically based render of chassis equipment_pad models and the kit structural_frame on TXT.ground caliche in the lastLight world, staged on the yard
  why_this_technique: a cooling plant nobody has chosen is a poured, bolted pad with nothing on it, and steel standing behind it says the building is going ahead
  palette: weathered concrete, ember layout paint, galvanized bolts, primer steel, caliche, the warm seam
  value_structure: Lightest is the seam and the near pad's lit edge. Darkest is the sky and the frame's shadowed webs. Frame median L* planned at 12.
type:
  hook: "Answers cover about 177 GW. Cooling, often undecided."
  dek: "ERCOT sent its data center impact questions to 465 loads. In a preliminary summary to the utility commission on November 5th, cooling questions drew N/A answers at the highest rate."
  labels: []
verbatim: []
acceptance:
  - at least three empty equipment pads are visible and the nearest spans at least 400 px of the frame width at 1080 px
  - every pad carries an ember layout line and nothing stands on any pad
  - the near pad casts a shadow onto caliche and touches the ground
  - the primer structural_frame is present as the kit model with columns and girders, never a box
  - the sky shows above the horizon behind the type and the render report says SKY IN FRAME
  - no numeral on this slide is absent from claims.json
risks:
- the frame swallowing the pads so the empty yard reads as a construction stock photo
- the ember line reading pink under the warm key
```

```yaml
slide: 2
layout: GRID
primary_image:
  subject: a yard of cable reels on caliche, one reel per Large Load, a front block of 33 reels in the pool and the rest in rows falling to the dark
  rect: [0, 680, 1080, 600]
  bleeds: [left, right]
accent: '#B4664F'
data_in_art: {figure: reels_large, drives: 'the number of cable reels instanced in the yard, one per Large Load, with reels_lit setting the lit front block'}
job: Show that every Large Load answered and that a few very large projects carry a third of the capacity.
claims: [c7, c8, c9]
numerals:
- {value_from: c7}
- {value_from: c8}
- {value_from: c9}
depth:
  eye: 6
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'A raised three quarter over the front block of reels, rows receding to the seam.', bands: 'Top third, the type on the dark sky. Middle third, the back rows thinning into the dark. Bottom third, the lit front block of 33 reels with their flanges and wound cable.', focal: the lit front block}
art:
  technique: physically based render of instanced chassis cable_reel models on TXT.ground caliche in the lastLight world, the front block staged
  why_this_technique: a count reads without a caption when every unit is the same thing at the same size, and a reel is what a site stages before power arrives
  palette: galvanized flanges, black XLPE, caliche, the warm seam
  value_structure: Lightest is the front block's lit flange rims. Darkest is the sky and the back rows. Frame median L* planned at 11.
type:
  hook: "All 245 Large Loads answered"
  dek: "Large Loads are 75 MW or greater and hold about 94% of the capacity requested. Among them, 33 projects ask for more than 1 GW each and represent 36% of capacity. One reel stands for one load, drawn to illustrate."
  labels: []
verbatim: []
acceptance:
  - the frame's code instances FIG.reels_large reels and lights FIG.reels_lit of them in the front block
  - the lit front block of reels spans at least 600 px of the frame width at 1080 px
  - the reels read as reels with flanges and wound cable at 432 px, never as discs or coins
  - the front block sits in the pool and the back rows fall darker
  - the sky shows above the horizon and the render report says SKY IN FRAME
  - no numeral on this slide is absent from claims.json or figures.json
risks:
- 245 reels reading as noise at feed size
- the yard reading like yesterday's parked lot
```

```yaml
slide: 3
layout: FIGURE_SCALE
primary_image:
  subject: one copper bus pack of 177 laminations, its striped end face toward the camera on standoff insulators and oak dunnage, a worker in a hard hat standing beside it for size
  rect: [0, 700, 1000, 440]
  bleeds: [left]
accent: '#B4664F'
data_in_art: {figure: gw_requested, drives: 'the lamination count of the copper pack and its face width, pack_w_total'}
job: Make about 177 GW a thing with a size, one bar per gigawatt, beside a person.
claims: [c4, c5, c6]
numerals:
- {value_from: c4}
- {value_from: c5}
- {value_from: c6}
depth:
  eye: 1.6
  horizon: 700
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'The pack''s end face fills the centre, its length running back to the right on dunnage, the worker at its left shoulder.', bands: 'Top third, the type on the dark sky. Middle third, the striped copper face and the worker. Bottom third, the oak dunnage and grey epoxy standoff insulators catching the key on their left faces, the pack and the worker casting long to the right across lit caliche, and the caliche falling to shadow at the bottom edge.', focal: the striped copper end face}
art:
  technique: physically based render of the chassis bus_pack and the kit person on TXT.ground caliche in the lastLight world, staged on the pack
  why_this_technique: crews add capacity by bolting bars in parallel, so a thicker pack really is more capacity, and a person beside it gives the pack a size
  palette: raw copper, dark spacers, grey epoxy insulators, oak, caliche
  value_structure: Lightest is the copper edges catching the key. Darkest is the sky and the pack's shadow side. Frame median L* planned at 13.
type:
  hook: "433 of 465 answered"
  dek: "The 433 that answered cover about 177 GW, about 97% of the capacity requested. 417 came in on time and 16 late, and 32 Medium Load responses had not arrived. One copper bar stands for one gigawatt, drawn to illustrate."
  labels: []
verbatim: []
acceptance:
  - the frame's code builds the pack with FIG.gw_requested laminations
  - the copper end face stands at least 280 px wide at 1080 px
  - the spacers every tenth bar read as bands at 432 px so the face is not a flat copper block
  - the worker stands on the ground beside the pack, lit from the camera side, under a third of the frame
  - the pack casts a shadow onto caliche
  - the sky shows above the horizon and the render report says SKY IN FRAME
  - no numeral on this slide is absent from claims.json
risks:
- copper reading as brown mud or salmon under the warm key
- the laminations moire at feed size
```

```yaml
slide: 4
layout: DIAGRAM
primary_image:
  subject: four copper bus packs of 73, 49, 45 and 10 laminations in one row at one depth on a shared dunnage line, end faces toward the camera, each labelled with its load zone
  rect: [60, 620, 960, 460]
  bleeds: []
accent: '#B4664F'
data_in_art: {figure: west_gw, drives: 'the lamination count of each zone pack from west_gw, south_gw, north_gw and houston_gw, with face widths pack_w_west to pack_w_houston'}
job: Show where the capacity is asked for, West widest, Houston a sliver, at one scale.
claims: [c10, c11, c12, c13, c14, c15, c16]
numerals:
- {value_from: c10}
- {value_from: c11}
- {value_from: c12}
- {value_from: c13}
- {value_from: c14}
- {value_from: c15}
depth:
  eye: 0.9
  horizon: 610
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'Four end faces in a row across the frame at one depth, West on the left, the packs receding behind them.', bands: 'Top third, the type on the dark sky. Middle third, the four striped faces with a mono label under each. Bottom third, the oak dunnage and grey epoxy insulators under each pack catching the key on their left faces, the packs casting long to the right across lit caliche, and the caliche falling to shadow at the bottom edge.', focal: the West face}
art:
  technique: physically based render of four chassis bus_pack models at one depth on TXT.ground caliche in the lastLight world, staged on the row
  why_this_technique: four widths at one depth and one bar thickness are exact ratios a reader compares without reading a number
  palette: raw copper, dark spacers, oak, caliche
  value_structure: Lightest is the lamination edges. Darkest is the sky and the gaps between packs. Frame median L* planned at 12.
type:
  hook: "West Texas asked for 73 GW"
  dek: "Every ERCOT load zone has requests, and West Texas holds 41% of the capacity. Zone figures cover 429 loads and leave out NOIE zones. A load's actual zone is set at interconnection and may differ."
  labels: ["WEST 73 GW", "SOUTH 49 GW", "NORTH 45 GW", "HOUSTON 10 GW"]
verbatim: []
acceptance:
  - the frame's code builds the four packs with FIG.west_gw, FIG.south_gw, FIG.north_gw and FIG.houston_gw laminations
  - all four packs stand at one depth so their face widths compare directly
  - the West pack's end face stands at least 180 px tall at 1080 px
  - each label sits directly above its own pack, centred on it within 40 design px
  - the sky shows above the horizon and the render report says SKY IN FRAME
  - no numeral on this slide is absent from claims.json
risks:
- the row reading as a bar chart made of copper
- the Houston pack too thin to see at 432 px
```

```yaml
slide: 5
layout: CLOSE_CROP
primary_image:
  subject: a cable trench in plan on a diagonal, concrete curbs, galvanized bar grating over the answered share of its length, the open stretch lined in ember epoxy, caliche either side
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: '#B4664F'
data_in_art: {figure: answered_pct, drives: 'the grated share of the trench length, with the open ember stretch the remainder'}
job: Make 83% answered a length, and the rest a stretch left open.
claims: [c17, c19]
numerals:
- {value_from: c17}
- {value_from: c19}
depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]
composition: {structure: 'The trench crosses the frame on a diagonal from upper left to lower right; the grating runs most of its length and stops, the ember stretch runs off the lower right edge.', bands: 'Top third, the type on dark caliche. Middle third, the grated trench with curbs casting. Bottom third, the open ember stretch lit on its far wall and shadowed on its near wall, the concrete curbs casting onto rough caliche either side, and the channel running off the lower right edge.', focal: the edge where the grating stops}
art:
  technique: TXBENCH.relief material bas-relief, concrete, galvanized grating, ember epoxy and caliche, lit by the chassis key
  why_this_technique: an answered share is a length covered, and a relief makes the curbs and the open channel cast
  palette: weathered concrete, galvanized steel, ember epoxy, caliche
  value_structure: Lightest is the grating's lit bars and the curb tops. Darkest is the open channel's shadowed wall and the caliche field. Frame median L* planned at 15.
type:
  hook: "83% of the questions answered"
  dek: "Respondents answered 83% of nearly 67,000 questions. N/A ran about 16% for Large Loads and 19% for Medium Loads. The open stretch is the share left unanswered, drawn to illustrate."
  labels: []
verbatim: []
acceptance:
  - the grated length over the trench length equals FIG.answered_pct in the frame's code
  - the open stretch is lined in ember and the grating is galvanized, at least two materials in the render report
  - the curbs cast onto the caliche and the trench walls cast into the channel
  - the relief carrier covers at least 40 percent of the frame and reports a real height range
  - the trench with its curbs is at least 200 px wide across its axis at 1080 px
  - no numeral on this slide is absent from claims.json
risks:
- the trench reading as a progress bar
- the grating aliasing to grey at feed size
```

```yaml
slide: 6
layout: SPLIT_HORIZON
primary_image:
  subject: the whole yard from 9 m up, four empty pads outlined in ember in a row in the pool, and a worker standing on the nearest pad inside its ember line
  rect: [100, 710, 980, 450]
  bleeds: [right]
accent: '#B4664F'
job: Name cooling as the kind of question most often answered N/A and show the empty cooling yard, a place and never a number.
claims: [c18]
numerals:
- {value_from: c18}
depth:
  eye: 9
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'An aerial three quarter; the four pads sit in a row in the pool across the lower frame.', bands: 'Top 40 percent, the type on the dark sky above the horizon. Middle, the seam and the edge of the pool. Bottom, the four lit concrete pads with their bolts casting right, the worker with a long cast, and the caliche falling to black outside the pool.', focal: the worker on the nearest empty pad}
art:
  technique: physically based render of chassis equipment_pad models and the kit person on TXT.ground caliche in the lastLight world, staged as one subject
  why_this_technique: the yard where the cooling plant would stand, poured and bolted with nothing chosen, seen whole
  palette: ember, concrete, caliche, the warm seam
  value_structure: Lightest is the seam and the pads' lit edges. Darkest is the sky and the caliche outside the pool. Frame median L* planned at 12.
type:
  hook: "Cooling had the highest N/A rate"
  dek: "No category of questions drew N/A answers at a higher rate than cooling. Respondents indicated many projects had not determined their final cooling configuration."
  labels: []
verbatim: []
acceptance:
  - four pads outlined in ember, the far three empty and a worker on the nearest
  - the whole yard as one staged subject: four empty equipment_pad models in a row span at least 900 px of the frame width at 1080 px, and the nearest pad stands at least 200 px tall
  - the worker stands inside the nearest pad's ember line and reads as a person at 432 px
  - the horizon sits below the type and the render report says SKY IN FRAME
  - no numeral on this slide is absent from claims.json
risks:
- a 300 mm ember line vanishing at feed size
- the lit caliche pushing the frame into the mid tones
```

```yaml
slide: 7
layout: CLOSE_CROP
primary_image:
  subject: one empty equipment pad at ankle height, broom finished concrete, galvanized J bolts with nuts, two rows of ember capped conduit stubs, the later row longer, and the ember layout line, a cable reel beyond the slab
  rect: [0, 700, 1080, 440]
  bleeds: [left, right]
accent: '#B4664F'
data_in_art: {figure: stubs_later, drives: 'the number of capped conduit stubs in the longer row, the early row of stubs_early grown by na_later_pct'}
job: Turn from the count to the consequence, later projects left more blank, drawn as a longer row of capped stubs.
claims: [c20]
numerals:
- {value_from: c20}
depth:
  eye: 1.5
  horizon: 600
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'Low along the slab from its near corner; bolts and capped stubs march away, the feeder tail crosses from the right edge, the seam on the far side.', bands: 'Top third, the type on the dark sky. Middle third, the far edge of the slab and the seam. Bottom third, the near galvanized J bolts at full size with lit threads and long casts across the broom finished concrete, the ember layout line and the slab''s chamfered edge, cropped by the left and bottom edges.', focal: the ember caps on the conduit stubs}
art:
  technique: physically based render of one chassis equipment_pad and a chassis cable_reel tail on TXT.ground caliche in the lastLight world, staged on the pad
  why_this_technique: at ankle height the bolts and capped stubs say a machine was meant to stand here and nothing has been chosen to stand on them
  palette: broom finished concrete, galvanized bolts, ember caps and paint, black cable, caliche
  value_structure: Lightest is the bolt threads and the slab's lit edge. Darkest is the sky and the shadow behind each bolt. Frame median L* planned at 12.
type:
  hook: "Later projects said N/A more often"
  dek: "Projects asking to energize in 2028 or later answered N/A 30% more often than those due sooner. The longer row of capped stubs stands for them, drawn to illustrate."
  labels: []
verbatim: []
acceptance:
  - the frame's code builds two rows of capped stubs, FIG.stubs_early and FIG.stubs_later
  - the pad spans the full frame width at 1080 px, fills at least a third of the frame height, and is cropped by at least two edges
  - at least four anchor bolts and two capped conduit stubs are visible and nothing stands on the pad
  - the conduit caps and the layout line are ember and nothing else in the frame is
  - every bolt casts a shadow on the slab
  - the sky shows above the horizon and the render report says SKY IN FRAME
  - no numeral on this slide is absent from claims.json
risks:
- the bolts reading as dots at feed size
- a dead flat slab with nothing to look at
```

```yaml
slide: 8
layout: OBJECT_AND_CAPTION
primary_image:
  subject: an official leaning over a plywood plan table in a bay of the primer frame, a stack of documents on the table, one tripod work light lighting the figure from the camera side
  rect: [100, 760, 880, 500]
  bleeds: []
accent: '#B4664F'
data_in_art: {figure: dev_reviewed, drives: 'the number of response folders in the stack on the plan table, one folder per developer whose responses ERCOT reviewed'}
job: Say the check is not over, ERCOT is going back to most developers for more.
claims: [c24, c25, c26, c29, c31]
numerals:
- {value_from: c24}
- {value_from: c25}
- {value_from: c26}
depth:
  eye: 1.5
  horizon: 650
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'The table and the figure centre frame inside a bay, primer columns either side, the work light at the right throwing the pool.', bands: 'Top third, the type on the dark sky through the open frame. Middle third, the figure and the work light. Bottom third, the table top with the documents and the casts on caliche.', focal: the documents under the work light}
art:
  technique: physically based render of the kit person, kit document_stack, chassis plan_table and work_light inside the kit structural_frame on TXT.ground caliche in the lastLight world, staged on the table
  why_this_technique: a second round of questions is people reading paper on a site, and one work light makes the pool
  palette: plywood, white paper, primer steel, the work light's LED, caliche
  value_structure: Lightest is the paper under the lamp. Darkest is the sky and the bay behind the figure. Frame median L* planned at 10.
type:
  hook: "ERCOT expects to go back to 80% of developers"
  dek: "In a separate check of Batch Zero eligibility, ERCOT reviewed responses from 257 developers and expects to send 80% of them a second round, with a 5 business day deadline. Common issues so far include proving site control and confirming financial security posted."
  labels: []
verbatim: []
acceptance:
  - the frame's code builds the folder stack with FIG.dev_reviewed folders
  - the person stands at the table in the read pose, lit from the camera side, under a third of the frame
  - the table with the figure and the work light spans at least 500 px of the frame width at 1080 px
  - the work light is visible and its pool falls on the table top
  - at least two primer columns frame the bay
  - the sky shows above the horizon and the render report says SKY IN FRAME
  - no numeral on this slide is absent from claims.json
risks:
- the kit person reading as a mannequin
- the bay reading as an empty grey void
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: the yard from the caliche road outside the ranch gate at the end of last light, the primer frame a silhouette on the seam, the pool holding the four empty pads
  rect: [0, 900, 1080, 450]
  bleeds: [left, right, bottom]
accent: '#B4664F'
job: Close on the consequence and the next step, the report and the meeting.
claims: [c2, c23]
numerals:
- {value_from: c23}
depth:
  eye: 3.4
  horizon: 670
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'From the road; the gate post in the left foreground, the road leading in, the yard in its pool in the middle distance, the frame a silhouette above it.', bands: 'Top third, the type on the dark sky. Middle third, the frame on the seam and the lit pads. Bottom third, the gate rails and the dark caliche outside the fence, the darkest ground in the deck.', focal: the lit empty pads}
art:
  technique: physically based render of the kit caliche_road, ranch_gate, structural_frame, chassis equipment_pad on TXT.ground caliche in the lastLight world, staged on the yard
  why_this_technique: the reader stands outside the fence where the public stands, looking at a yard whose cooling is still a blank, with a date to watch
  palette: caliche, galvanized pipe, primer steel, ember, the warm seam
  value_structure: Lightest is the seam and the lit pads. Darkest is the sky and the road's shadowed verge. Frame median L* planned at 9.
type:
  hook: "Final report targeted for December 10th"
  dek: "ERCOT says detailed analysis is under way and targets a published final report on December 10th. The RFI figures are marked preliminary and subject to change."
  labels: []
verbatim: []
acceptance:
  - the pads in the pool are empty and outlined in ember
  - the structural_frame silhouette spans at least 400 px of the frame width and the lit pads at least 300 px
  - the ranch_gate post stands in the foreground on the near side of the yard
  - the sky shows above the horizon and the render report says SKY IN FRAME
  - no numeral on this slide is absent from claims.json
risks:
- the yard too small and grey in the middle distance, the defect charged on no. 73 frame 7
```
