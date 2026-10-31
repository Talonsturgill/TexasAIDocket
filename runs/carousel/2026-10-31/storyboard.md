# Storyboard, 2026-10-31
# "Fixed locations on public roadways."

## The story, and what the fact check did to it

League City voters decide Proposition A on Tuesday, November 3rd, 2026 (c12): whether the police department keeps using
automated license plate reader cameras at fixed locations on public roadways (c13). The Tribune reports it is the first
such vote in Texas (c29) and counts 55 Flock cameras along public roads (c30). The ballot calls itself "a nonbinding
statement of voter preference" (c27), a word the council amended in on August 11th (c15). On October 13th the council
passed Resolution No. 2026-185, directing removal of the fixed cameras if a majority rejects them (c22, c23), with every
member on the roll voting For (c24). The mayor said no second vote is needed (c32) and that bagging starts 72 hours after
certification (c33).

The council's own record carries the whole arc. Resolution No. 2022-185 leased 42 Flock cameras over two years for up to
$233,400 (c1, c2, c3). Resolution No. 2023-197 restated a five year lease of 70 cameras for up to $899,600 (c4, c5, c6),
with every member on that roll voting For (c8). The election order of August 11th passed with one member absent (c14,
c16). The Tribune reports more than 400 agencies can access the data, all in Texas but the FBI (c40, c41), six officers in
League City have access and two must work together (c38, c39). Kyle and Laredo plan votes in May (c35).

The fact check moved four things, and every surface obeys them.
1. **55 is the Tribune's count and 70 is the most the 2023 lease covers.** They are two kinds of number. No surface
   subtracts them as cameras taken down.
2. **"Nonbinding" is the ballot's own word.** The resolution is what commits the council to removal, and it directs removal
   only if a majority rejects. No surface says the cameras will come down.
3. **"AI-powered" is the Tribune's phrase** (c34), never the deck's own voice.
4. **Galveston County's polling hours are not in the record.** The hours on frame 9 are Harris County's (c28) and say so.

## Why this treatment, and what was grafted

Director A's MEASURED EVIDENCE is the spine. Proposition A defines the cameras by where they stand, "fixed locations on
public roadways" (c13), so every count in the record is laid in the material of a public road: white thermoplastic marking
on Gulf Coast asphalt. Thermoplastic stands a few millimetres proud of the asphalt, so under a low key every stripe casts,
and a crosswalk's bars line up the way a roll call's names do. The deck never shows a camera, which keeps it clear of no.
39's plate reader on its pole and of any real camera model.

Grafted from Director C (ONE CHANGING OBJECT): the same camera with the state changed. Frames 6 and 7 stand at one corner
of one crosswalk, the voter's eye and then the paint's height. Grafted from Director B (THE PLACE AND THE NIGHT BEFORE):
the floodlit night register was weighed and refused for the light, because a relief needs the 10 to 20 degree rake only
lastLight reaches, but B's honesty about the conditional close is kept: frame 7 says "if voters say no".

Refused: C and B's canvas hood (cloth geometry the kit lacks, which both directors flagged as the highest risk, and an image
that suggests the outcome), B's council dais (no. 63's frame 8 was charged as a generic CG dais in all three rounds), A's
frame 3 as a plan relief (it is rebuilt as a txthree oblique, the recovery no. 63's frame 3 made), and the kit's
`plate_reader` (drawn to a maker's published specification).

## The world, and the laws that hold it

**LASTLIGHT, STAGED.** The chassis is `assets/js/deck/2026-10-31-roadpaint.js` and every frame loads it. It declares
`sky: lastLight` with the key at azimuth -64, elevation 14: the last light low in the west. A camera looking north (-z) has
the key on its LEFT, every lit edge of paint is on the left, and every cast runs long to the right. TXBENCH reads the same
declaration, so every relief is raked from the upper left and casts to the lower right.

The materials of the deck: fresh thermoplastic (bead white, a fine glint), worn thermoplastic (a dull grey white, the
aggregate showing through), Gulf Coast asphalt (near black, coarse aggregate in the albedo), a salt grey concrete gutter
pan, and a terracotta detectable warning panel at the kerb, which is the one accent.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#09080C` | the DOM body behind the render |
| `accent` | `#B4664F` | dusk_ember, worn ONLY as the terracotta warning panel and the terracotta start bar, the place the public stands, and League City's stud. Frames 6, 8, 9 |
| `hook` | `#ECE8DF` | light type on the dark |
| `dek` | `#D6D0C4` | the dek |
| `material` | `#E6E1D6` | fresh thermoplastic |

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE, VALUE_ARC

1. **Motif evolution, the road paint changes state with every claim.** A crosswalk at a stop bar on 1, tally stripes worn
   and fresh on 2, two inlaid bars on a gutter ruler on 3, raised markers in rows on 4, three crosswalks as three roll calls
   on 5, the crosswalk from the kerb on 6, the stop bar at paint height on 7, cut hour grooves on 8, studs on a slab of
   Texas on 9.
2. **Camera move around one intersection.** The car's eye on 1, the voter's eye on 6 and the paint's height on 7 are the
   same corner, closing in. The reliefs are plan views under the one rake.
3. **Value arc, last light to night.** The warm seam behind the car on 1, the lit paint through the middle, the darkest
   frame on 8, and the slab's coast edge catching the last of the seam on 9.

## The rotation

    FULL_BLEED  GRID  DIAGRAM  GRID  GRID  FULL_BLEED  GRID  DIAGRAM  MAP

`TXLAYOUT.check` returns an empty list. Type sits on the dark sky or the dark asphalt on every frame.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | WIDE, eye 2.5 m, 10.9 m in front of the car across the crosswalk, fov 40 | the kit crossover at a white stop bar with its headlights on, seen head on across the chassis continental_crosswalk of 8 thermoplastic bars 7 mm proud with a bead glint, TXT.ground asphalt worn, the car seated with TXT.contact and tyre polish, the headlights' throw lighting the bars that run toward the reader |
| 02 | AERIAL, orthographic material relief | an asphalt carrier with thermoplastic tally stripes in rows of 14, 42 worn and 28 fresh, each stripe 3.5 to 5 px proud with a bevel, raked at 14 degrees so each casts to the lower right, aggregate in the asphalt albedo, a keyMask pool falling off to black |
| 03 | AERIAL, a plan view straight down on a concrete gutter pan under the deck's raking key, a TXBENCH relief | the chassis gutter_rule: a salt grey concrete pan with a saw cut tick at every unit and a longer cut every 5, and two inlaid thermoplastic bars at one scale from one origin, 70 units and 55 units, separate, with chamfered edges, the key raking along the ticks, the pan seated in the asphalt with a grimy joint |
| 04 | CLOSE, eye 1.5 m over the officers' row, 4.2 m from the block's front, fov 40, horizon in the upper third | 400 chassis raised_marker wedges in a staggered block on an asphalt apron, ceramic white bodies with prismatic faces, six amber markers in a front row with two set close, each seated with a contact, the prism faces catching the key row by row, TXT.stage on the whole block |
| 05 | WIDE, eye 6.3 m, 11.9 m back over the lane, looking down about 28 degrees, fov 40 | three of the chassis continental_crosswalk laid across one lane one behind another on TXT.ground asphalt: 7 worn bars farthest, 7 fresh bars and one bare saw cut groove with lit and shadowed lips in the middle, 8 fresh bars nearest, each bar 7 mm proud, a concrete gutter pan and kerb on the left and a worn lane edge line on the right, staged on all three crosswalks |
| 06 | MEDIUM, eye 3.4 m, 11.4 m from the resident, fov 33 | the kit person, a resident, standing on the terracotta warning panel turned three quarters away, lit from the camera's side, the 8 bar crosswalk running across the road in front, a kit streetlight's cast behind, TXT.contact under the feet |
| 07 | MEDIUM, eye 1.05 m at the kerb corner behind the crosswalk's end, fov 42 | the crosswalk bars at paint height, 7 mm of thermoplastic each with a lit chamfer and a thin cast, the fresh paint's bead texture, the bars receding into the pool toward a band of sky, the stop bar to the right |
| 08 | AERIAL, orthographic material relief | a concrete kerb strip cut with 72 saw cut hour grooves in 3 rows of 24, each groove with a lit wall and a shadowed wall, a terracotta thermoplastic start bar at the head of the first row, a keyMask pool falling off to black |
| 09 | WIDE, eye 2.2 m, 11 m from a slab of Texas, fov 32, low oblique | Texas extruded from TXGeo's real outline 9 m wide and 0.25 m deep in dark asphalt standing on TXT.ground, three thermoplastic studs at the Census gazetteer points of League City (terracotta), Kyle and Laredo (white), the Gulf coast edge facing the key and catching the seam, TXT.contact along its foot |

Showstopper frame: 05, three roll calls laid as crosswalks across one lane, the 2023 bars dull and farthest, August with one bare saw cut where the absent member's bar would be, October's eight fresh bars nearest; its depth is made by the lane receding to a horizon in haze, the far crosswalk shrinking against the near, the kerb's cast shadow and the contact of every bar on the asphalt.
Tonal arc: the warm seam behind the car on 01, the worn and fresh stripes on 02, the gutter pan's lit ruler on 03, the
markers' prism glints on 04, the fresh bars on 05, the voter on the warning panel on 06, the paint at its own height on 07,
the darkest frame on 08 with only the grooves' lit walls, and the slab's coast edge on 09.
VALUE CUT: frame 5. The deck turns from what the city bought to what the council voted.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "a crossover waiting at a white stop bar at last light with its headlights on, seen from across the crosswalk, the thermoplastic bars running toward the reader lit by the headlights, the road falling dark behind"
  rect: [200, 720, 720, 630]
  bleeds: [bottom]
accent: "none"
job: >
  Put the reader at a crosswalk on the kind of public road the proposition is about, facing a car that waits at the line,
  on the eve of the first vote of its kind in Texas.

claims: [c12, c13, c27, c29]
numerals: []

data_in_art:
  figure: removal_roll
  drives: crosswalk bar count

depth:
  eye: 1.1
  horizon: 560
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera stands across the crosswalk at 3.1 m looking back at the waiting car, so the bars run toward the reader as a
    ladder of lit stripes in the headlights' throw and lead the eye up to the two lamps, the brightest points in the frame.
    The car and the bars own the lower half, the road recedes into the dark behind.
  bands: >
    Top third, the dark sky with the kicker, the hook and the dek. Middle third, the car with its headlights on and the road
    vanishing into the dark. Bottom third, the crosswalk bars lit by the headlights in the foreground, each with its edge and shadow on the asphalt texture, the stop bar behind them.
  focal: "the two headlights and the lit bars in their throw, the brightest area in the frame"

art:
  technique: "physically based render of the kit crossover on TXT.ground asphalt with the chassis continental_crosswalk and a thermo_bar stop bar in the lastLight world, its headlights throwing onto the bars, staged on the car and the crosswalk"
  why_this_technique: "a modelled road at paint scale makes the stripes physical, a few millimetres proud and casting, which is the material the whole deck counts in"
  palette: "near black asphalt, bead white thermoplastic, warm headlight throw, a warm seam low in the west"
  value_structure: >
    Lightest is the headlights and the bars in their throw. Darkest is the sky and the road beyond the pool.
    Frame median L* planned at 12.

type:
  hook: "League City votes Tuesday on its Flock cameras"
  dek: "Proposition A asks whether police keep plate reader cameras at fixed locations on public roadways. The Tribune reports it is the first such vote in Texas. Drawn to illustrate."
  labels: []

verbatim:
  - c13: "fixed locations on public roadways"

acceptance:
  - "at least four crosswalk bars run toward the camera, lit by the headlights"
  - "the two headlights are the brightest points in the frame at 432 px"
  - "the stop bar reads behind the crosswalk, in front of the car"
  - "the car is seated on the asphalt with a contact shadow under each tyre"
  - "no bar, car or kerb crosses a glyph of the hook or dek"
  - "the frame's median L* at 432 px is 26 or lower"
  - "the crossover and the continental_crosswalk are present, the car modelled with wheels and glass"
  - "the crossover at the stop bar stands at least 90 px tall at 432px"
risks:
  - "the road reads as no. 39's blue hour road, so the light is last light warm and the subject is the paint, with no pole and no camera"
```

```yaml
slide: 2
layout: GRID
primary_image:
  subject: "an asphalt carrier with thermoplastic tally stripes in rows of 14, 42 worn grey stripes and 28 fresh white stripes, each raised and casting under a raking key"
  rect: [0, 520, 1080, 830]
  bleeds: [left, right, bottom]
accent: "none"
job: >
  Show the purchase grew: the 42 cameras of 2022 still in the paint, and the 28 the 2023 lease added laid fresh beside them.

claims: [c1, c2, c3, c4, c5, c6]
numerals:
  - value_from: c1
  - value_from: c2
  - value_from: c5
  - value_from: c6
  - computed_by: "compute.py, cameras_added_2023"

data_in_art:
  figure: cameras_2022
  drives: worn stripe count, with cameras_added_2023 setting the fresh stripe count

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    Five rows of fourteen stripes run across the frame at one pitch, the first three rows worn and the last two fresh, so the
    reader sees the 2022 lease as the grey block and the growth as the white block below it without counting.
  bands: >
    Top third, the dark asphalt and the type. Middle third, the three worn rows. Bottom third, the two fresh rows lit in the pool, the brightest paint, each stripe's shadow raked to the right, falling to black at the bottom edge.
  focal: "the two fresh rows, the brightest area"

art:
  technique: "TXBENCH multi-material relief, thermoplastic on asphalt raked by the low key, with a keyMask pool"
  why_this_technique: "a stripe that stands proud and casts is a physical unit a reader counts, and worn against fresh paint tells old from new without a legend"
  palette: "near black asphalt, dull grey worn paint, bead white fresh paint"
  value_structure: >
    Lightest is the fresh stripes' lit edges. Darkest is the asphalt outside the pool and each stripe's cast.
    Frame median L* planned at 14.

type:
  hook: "42 cameras in 2022, then 70"
  dek: "The council leased 42 Flock cameras over two years for up to $233,400, then restated a five year lease of 70 for up to $899,600. One stripe is one camera. Drawn to illustrate."
  labels: ["2022", "2023, 70 IN ALL"]

verbatim: []

acceptance:
  - "exactly 42 worn stripes and 28 fresh stripes, 70 in all, countable at full size"
  - "every stripe casts a shadow to the lower right"
  - "worn and fresh stripes are told apart by value at 432 px"
  - "no legible text is rendered in the art, only the DOM labels"
  - "the frame's median L* at 432 px is 30 or lower"
  - "the tally stripes are present on the asphalt carrier with raised paint and casts"
  - "the asphalt carrier of stripes owns at least half of the frame height at 432px"
risks:
  - "a plan relief reads flat, so the rake is 14 degrees, the paint stands proud with a bevel, and a pool falls off to black"
```

```yaml
slide: 3
layout: DIAGRAM
primary_image:
  subject: "a salt grey concrete gutter pan cut with a saw cut ruler, two separate thermoplastic bars inlaid against it at one scale, the longer 70 units and the shorter 55"
  rect: [0, 700, 1080, 440]
  bleeds: [left, right]
accent: "none"
job: >
  Set the lease against the count without letting one be read as the other: up to 70 under the 2023 lease, 55 counted by the
  Tribune, two kinds of number.

claims: [c5, c30]
numerals:
  - value_from: c5
  - value_from: c30

data_in_art:
  figure: cameras_2023
  drives: the upper bar's length at one scale, with cameras_tribune setting the lower bar's length

depth:
  eye: 2.5
  horizon: 360
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The pan runs across the frame on a low oblique so the ruler's ticks recede in perspective, and the two bars lie along it
    from one origin, the upper running further. Labels sit in the dark asphalt above each bar with leaders to the bar ends.
  bands: >
    Top third, the dark asphalt and the type. Middle third, the upper bar and its label. Bottom third, the lower bar lit along its chamfer, the ruler ticks with their lit and shadowed walls in the pool, and the pan's edge falling off into shadow.
  focal: "the two bar ends against the ruler, the brightest paint"

art:
  technique: "physically based render of the chassis gutter_rule in the lastLight world, staged on the pan"
  why_this_technique: "two lengths at one scale on a real ruler compare two numbers honestly, and an oblique keeps the casts the plan reliefs were charged for losing"
  palette: "salt grey concrete, bead white thermoplastic, near black asphalt"
  value_structure: >
    Lightest is the bars' lit chamfers. Darkest is the asphalt beyond the pool.
    Frame median L* planned at 16.

type:
  hook: "70 leased, 55 on the roads"
  dek: "The 2023 lease covers 70 cameras. Proposition A asks about 55 along public roads, the Tribune reported. A lease and a road count measure different things. Drawn to illustrate."
  labels: ["70, THE 2023 LEASE", "55, ON THE ROADS"]

verbatim: []

acceptance:
  - "two separate bars lie along one ruler from one origin, the upper longer than the lower"
  - "the ratio of the lower bar's length to the upper's measures within 3 percent of 55 to 70 on the render"
  - "the ruler shows saw cut ticks with a lit wall and a shadowed wall"
  - "each label's leader lands on its own bar's end within 24 px"
  - "the frame's median L* at 432 px is 30 or lower"
  - "the gutter_rule pan is present with both inlaid bars and its tick ruler"
  - "the gutter pan owns at least 90 percent of the frame width at 432px"
risks:
  - "a reader subtracts the bars as removed cameras, so the dek says they are different measures and the bars never nest"
```

```yaml
slide: 4
layout: GRID
primary_image:
  subject: "400 white raised pavement markers in a staggered block on a dark asphalt apron, six amber markers in a front row with two set close together"
  rect: [0, 780, 1080, 410]
  bleeds: [left, right]
accent: "none"
job: >
  Show who can look: more than 400 agencies as 400 markers, and the six officers in League City in front of them.

claims: [c38, c39, c40, c41, c42]
numerals:
  - value_from: c40
  - value_from: c38
  - value_from: c39

data_in_art:
  figure: agencies_floor
  drives: white marker count, with officers_with_access setting the amber marker count and officers_per_search the close pair

depth:
  eye: 2.6
  horizon: 420
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, TEXTURE_GRADIENT, AERIAL]
  subject_at: {X: 0, Z: -6}

composition:
  structure: >
    The block recedes from the lower frame to the horizon in perspective, the rows shrinking, so 400 reads as a field rather
    than a count, and the six amber markers stand largest in the front row with two close together.
  bands: >
    Top third, the dark sky and the type. Middle third, the far rows of the block fading into the dark. Bottom third, the near rows lit in the pool, each marker's prism face catching the light and its shadow on the asphalt, the six amber markers in the foreground.
  focal: "the six amber markers in the front row, the warmest and brightest area"

art:
  technique: "physically based render of 400 instanced chassis raised_marker wedges in the lastLight world, staged on the whole block"
  why_this_technique: "a field of real markers in perspective makes 400 feel like a crowd, and the near amber row gives the six their own size"
  palette: "near black asphalt, ceramic white markers, amber prisms"
  value_structure: >
    Lightest is the prism faces catching the key in the front rows. Darkest is the sky and the apron beyond the pool.
    Frame median L* planned at 12.

type:
  hook: "More than 400 agencies can look"
  dek: "All but the FBI are in Texas. The mayor said six League City officers have access. Two must work together to scan the data. Each line is from the Tribune's reporting. One white marker is one agency, one amber marker one officer. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the block holds exactly 400 white markers and the front row 6 amber markers"
  - "two of the amber markers stand closer together than any other pair"
  - "every near marker is seated on the asphalt with a contact shadow"
  - "the amber markers read as a different colour from the white at 432 px"
  - "the frame's median L* at 432 px is 26 or lower"
  - "the raised_marker field is present with prism faces modelled"
  - "the marker block owns the full frame width and at least 150 px of height at 432px"
risks:
  - "400 small instances alias into noise at feed size, so the fov is narrow, the block is staggered and the far rows fall into fog"
```

```yaml
slide: 5
layout: GRID
primary_image:
  subject: "three crosswalks laid across one lane on black asphalt, one behind another, as three roll calls: 7 worn bars farthest, 7 fresh bars beside one bare saw cut groove, and 8 fresh bars nearest"
  rect: [0, 780, 1080, 470]
  bleeds: [left, right]
accent: "none"
job: >
  The turn. Show the council's three recorded votes on the cameras as three crosswalks, so the reader sees every vote For,
  one absence, and the eighth bar arriving on the removal resolution.

claims: [c4, c8, c14, c16, c22, c23, c24]
numerals:
  - computed_by: "compute.py, lease_2023_votes_for, election_order_votes_for, election_order_votes_absent, removal_votes_for, counted from the council's vote rows"

data_in_art:
  figure: removal_votes_for
  drives: fresh bar count in the third crosswalk, with lease_2023_votes_for setting the worn bars, election_order_votes_for the second crosswalk's bars and election_order_votes_absent its bare outline

depth:
  eye: 4.3
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, TEXTURE_GRADIENT, AERIAL]
  subject_at: {X: 0, Z: -3.75}

composition:
  structure: >
    Three crosswalks cross one lane one behind another, the oldest farthest, so the eye reads from the far worn row down the
    lane to the nearest and fullest crosswalk, with the bare saw cut in the middle row marking the absence.
  bands: >
    Top third, the type and the first crosswalk's worn bars. Middle third, the second crosswalk with its bare outline in the
    pool. Bottom third, the eight fresh bars lit on their bevels, the brightest paint, each shadow long to the right on the asphalt texture.
  focal: "the eight fresh bars of the third crosswalk"

art:
  technique: "physically based render of three chassis continental_crosswalk on TXT.ground asphalt in the lastLight world, staged on the three crosswalks"
  why_this_technique: "a crosswalk is the road's own row of identical marks, so a roll call laid as one is countable on a real lane, and a bare saw cut shows an absence as a recess in the road"
  palette: "near black asphalt, dull grey worn paint, bead white fresh paint, the saw cut's dark groove"
  value_structure: >
    Lightest is the fresh bars' lit bevels. Darkest is the asphalt outside the pool, the casts and the bare groove.
    Frame median L* planned at 14.

type:
  hook: "Seven For, seven For, then eight"
  dek: "December 12th, 2023, the lease. August 11th, the election order, one member absent. October 13th, a resolution on the cameras. No member on the three rolls voted against. One bar is one recorded vote. Drawn to illustrate."
  labels: ["2023 LEASE", "ELECTION ORDER", "OCTOBER 13TH"]

verbatim: []

acceptance:
  - "the first crosswalk shows exactly 7 worn bars, the second 7 bars and 1 bare outline, the third exactly 8 fresh bars"
  - "the bare saw cut reads as a groove with no paint, not as a bar"
  - "the three crosswalks recede on one lane with a kerb on one side"
  - "the third crosswalk's bars are the brightest paint in the frame at 432 px"
  - "the frame's median L* at 432 px is 30 or lower"
  - "all three crosswalks are present with raised bars and casts"
  - "the three crosswalks together own at least a third of the frame height at 432px"
risks:
  - "the far row shrinks with distance, so the camera stands high enough that all seven far bars stay countable"
```

```yaml
slide: 6
layout: FULL_BLEED
primary_image:
  subject: "a resident standing on the terracotta warning panel at the kerb, turned three quarters away, the eight bar crosswalk running across the road in front, a streetlight's long cast across the road behind"
  rect: [0, 680, 1080, 670]
  bleeds: [left, right, bottom]
accent: "#B4664F"
job: >
  Give the ballot's question a voter: the words "nonbinding statement of voter preference" read beside a person standing
  where the public stands.

claims: [c13, c14, c15, c27]
numerals: []

data_in_art:
  figure: removal_roll
  drives: crosswalk bar count

depth:
  eye: 1.6
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: -1.2, Z: -2}

composition:
  structure: >
    The resident stands on the left at the kerb on the warning panel, at true scale, the crosswalk running from their feet
    across the frame to the right, so the bars give the person a size and the person gives the road one.
  bands: >
    Top third, the dark sky and the type with the ballot words. Middle third, the resident's head and shoulders against the
    dark, the streetlight's long cast across the road. Bottom third, the warning panel's texture lit in the foreground, the feet with their contact shadow and the crosswalk bars lit in the pool.
  focal: "the resident on the terracotta panel, lit from the camera's side"

art:
  technique: "physically based render of the kit person on the chassis curb_ramp_warning with the chassis continental_crosswalk in the lastLight world, staged on the person"
  why_this_technique: "a person at true scale at the kerb is the voter the ballot addresses, and the same corner as frames 1 and 7 keeps the deck at one place"
  palette: "near black asphalt, terracotta panel, bead white bars, the resident's dark clothes lit warm"
  value_structure: >
    Lightest is the resident's lit side and the near bars. Darkest is the sky and the road beyond the pool.
    Frame median L* planned at 12.

type:
  hook: "The ballot calls itself nonbinding"
  dek: "Harris County's sample ballot reads \"As a nonbinding statement of voter preference, should the League City Police Department continue using automated license plate reader cameras at fixed locations on public roadways for law enforcement purposes?\" The council added the word on August 11th. Drawn to illustrate."
  labels: []

verbatim:
  - c27: "As a nonbinding statement of voter preference, should the League City Police Department continue using automated license plate reader cameras"

acceptance:
  - "the resident stands on the terracotta warning panel with a contact shadow under the feet"
  - "the resident's face side is lit and reads as a person, not a silhouette, at 432 px"
  - "the crosswalk shows exactly 8 bars running away from the kerb"
  - "the terracotta panel reads as the accent at 432 px"
  - "the frame's median L* at 432 px is 26 or lower"
  - "the kit person and the curb_ramp_warning are present"
  - "the kit person stands at least 140 px tall at 432px"
risks:
  - "the kit person reads as a mannequin, so they are lit from the camera's side, turned three quarters away, and kept under a third of the frame height"
```

```yaml
slide: 7
layout: GRID
primary_image:
  subject: "the crosswalk seen from the kerb corner, its bars of thermoplastic each with a lit edge, receding diagonally across the dark road"
  rect: [0, 620, 1080, 450]
  bleeds: [left, right]
accent: "#B4664F"
job: >
  Say what a no would set in motion: removal is already directed, so the frame drops to the paint itself, the thing that
  stays when a camera goes.

claims: [c22, c23, c24, c32]
numerals: []

data_in_art:
  figure: removal_votes_for
  drives: crosswalk bar count running away from the stop bar

depth:
  eye: 0.28
  horizon: 600
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, TEXTURE_GRADIENT, HEIGHT_IN_FIELD]
  subject_at: {X: 0, Z: -0.6}

composition:
  structure: >
    The camera lies almost on the asphalt at the kerb end of the crosswalk, so the bars recede as a run of lit edges into
    the pool across the lower half, the nearest bar's chamfer filling the foreground.
  bands: >
    Top third, a band of dark sky with the type. Middle third, the bars receding into the dark. Bottom third, the nearest bars' lit chamfers and their shadows on the asphalt texture in the foreground.
  focal: "the nearest bars' lit chamfers at paint height"

art:
  technique: "physically based macro render of the chassis continental_crosswalk on TXT.ground asphalt in the lastLight world"
  why_this_technique: "at paint height the marking is a physical thing with an edge and a shadow, which is the deck's unit seen at its own size"
  palette: "near black asphalt with coarse aggregate, bead white paint"
  value_structure: >
    Lightest is the nearest bars' lit chamfers. Darkest is the sky band and the far road.
    Frame median L* planned at 14.

type:
  hook: "If voters say no, removal is already directed"
  dek: "Resolution No. 2026-185 passed on October 13th with every member on the roll voting For. \"There's no second vote needed,\" Mayor Nick Long said, the Tribune reported. Drawn to illustrate."
  labels: []

verbatim:
  - c32: "there's no second vote needed"

acceptance:
  - "the nearest bar's chamfer is lit and its edge casts onto the asphalt"
  - "at least five crosswalk bars recede across the lower half of the frame"
  - "the crosswalk bars recede with at least four lit edges visible"
  - "a band of sky shows at the top of the frame behind the type"
  - "the frame's median L* at 432 px is 30 or lower"
  - "the continental_crosswalk is present at paint height"
  - "the continental_crosswalk owns the full frame width and at least 120 px of height at 432px"
risks:
  - "a camera this low points at the ground, so the frame aims level with a band of sky above the horizon"
```

```yaml
slide: 8
layout: DIAGRAM
primary_image:
  subject: "a concrete kerb strip cut with 72 saw cut hour grooves in three rows of 24, each groove with a lit wall and a shadowed wall, a terracotta start bar at the head of the first row"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#B4664F"
job: >
  Measure the promise: 72 hours after certification is when the mayor said bagging starts, laid as 72 cut grooves.

claims: [c22, c33, c46]
numerals:
  - value_from: c33

data_in_art:
  figure: hours_after_certification
  drives: groove count

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    Three rows of 24 grooves run across the kerb strip from the terracotta start bar, read like a ruler in hours, so the
    reader takes the length before the number.
  bands: >
    Top third, the dark ground and the type. Middle third, the first two rows of grooves in the pool. Bottom third, the third row of grooves with lit walls and shadowed walls, the strip's edge falling into shadow.
  focal: "the terracotta start bar and the first row of lit groove walls"

art:
  technique: "TXBENCH multi-material relief, saw cuts in a concrete kerb strip raked at 14 degrees with a keyMask pool"
  why_this_technique: "a cut groove is the negative of the deck's raised paint, so the hours read as work done to the road"
  palette: "salt grey concrete, terracotta thermoplastic, near black asphalt"
  value_structure: >
    Lightest is the grooves' lit walls and the start bar. Darkest is the asphalt and each groove's shadowed wall.
    Frame median L* planned at 12.

type:
  hook: "72 hours after the count is certified"
  dek: "If voters say no, that is when the city starts bagging the cameras, Long told the council, the Tribune reported. Houston Public Media quoted him on getting them down within 72 hours. One groove for each hour. Drawn to illustrate."
  labels: ["CERTIFIED"]

verbatim: []

acceptance:
  - "exactly 72 grooves in three rows of 24, countable at full size"
  - "each groove shows a lit wall and a shadowed wall"
  - "the terracotta start bar reads as the accent at 432 px"
  - "the frame's median L* at 432 px is 26 or lower"
  - "the kerb strip is present with its saw cut grooves"
  - "the kerb strip owns the full frame width and at least 150 px of height at 432px"
risks:
  - "concrete pushes mid tones, so the albedo is dark and a pool falls off to black"
```

```yaml
slide: 9
layout: MAP
primary_image:
  subject: "Texas extruded from its real outline in dark asphalt standing on the ground at last light, its county lines laid in worn paint on the top, Galveston and Harris counties laid in terracotta, three thermoplastic studs at League City in terracotta and at Kyle and Laredo in white, the coast edge catching the seam"
  rect: [60, 720, 960, 520]
  bleeds: []
accent: "#B4664F"
job: >
  Close on the next step and what follows: League City votes Tuesday, and Kyle and Laredo plan their own votes in May.

claims: [c25, c26, c28, c35, c47, c48, c49]
numerals:
  - value_from: c28

data_in_art:
  figure: league_city_lat
  drives: stud position, with league_city_lon and the kyle and laredo coordinates placing the other studs

depth:
  eye: 2.2
  horizon: 470
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The slab lies on a low oblique filling most of the frame width, the Gulf coast edge toward the key and the camera, so
    League City's terracotta stud sits nearest and brightest and the two white studs stand further inland.
  bands: >
    Top third, the dark sky and the type. Middle third, the slab's far panhandle falling into the dark. Bottom third, the coast edge lit by the seam, the slab's shadow on the ground, the three studs and their leader lines.
  focal: "League City's terracotta stud on the lit coast edge"

art:
  technique: "physically based render of Texas extruded with TXT.extrude from TXGeo's outline in the lastLight world, studs placed from the Census gazetteer"
  why_this_technique: "a slab of the real state at a low oblique places three towns honestly and keeps the road's material to the last frame"
  palette: "near black asphalt slab, terracotta and bead white studs, the warm seam"
  value_structure: >
    Lightest is the coast edge's lit face and the studs. Darkest is the sky and the ground beyond the pool.
    Frame median L* planned at 12.

type:
  hook: "Tuesday first, then Kyle and Laredo in May"
  dek: "League City lies in Galveston and Harris counties. Harris County vote centers take voters from 7 a.m. to 7 p.m. on Tuesday, November 3rd. Kyle and Laredo plan their own votes in May, the Tribune reported. Drawn to illustrate."
  labels: ["LEAGUE CITY", "KYLE", "LAREDO"]

verbatim: []

acceptance:
  - "the slab carries the real Texas outline, recognisable at 432 px"
  - "exactly three studs, League City's terracotta and the other two white"
  - "each DOM label's leader lands on its own stud within 24 px"
  - "the slab is seated on the ground with a contact shadow along its foot"
  - "the frame's median L* at 432 px is 26 or lower"
  - "the Texas slab is present with depth and three modelled studs"
  - "the Texas slab owns at least 70 percent of the frame width at 432px"
risks:
  - "the slab reads as a souvenir, so it stays dark asphalt with no star, lit only on its coast edge"
```
