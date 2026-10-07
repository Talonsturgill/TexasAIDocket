# Storyboard, 2026-10-07
# "Port Alpha, drawn to its own figures"

## The story, and what the fact check did to it

Saronic announced the groundbreaking of Port Alpha at the Port of Brownsville on September 30th (c1). It
calls the yard a clean-sheet, software-defined facility built to deliver autonomous, autonomy-capable and
manned ships (c6), and its chief executive says it is designed to produce autonomous and manned vessels at
scale (c20). The site is 835 acres with an option to nearly 4,400 (c2, c3), more than $3 billion of
private capital (c4), up to 10,000 direct jobs (c5). The first phase has more than 2,500 feet of deepwater
quay (c13), two to four build positions for final erection (c14), 8 to 10 production buildings (c12),
vessels up to 850 feet at first (c9) and over 1,200 after expansion (c10), Navy landing craft among the
first ships (c16). Saronic's own page says its Marauder has a top speed of 25+ knots, a range up to 5,400
nautical miles and a 150 metric ton payload (c23), and claims the first known at-sea rescue by an
autonomous boat (c24). In June the Cameron County Commissioners Court approved a tax break the Texas
Tribune put at $211 million (c26), before Saronic had picked the site (c27, c37), a 95% abatement over 20
years (c28), with 35% of the full-time workforce to be local (c29) and a smaller break if the jobs fall
short (c30). Opponents told the court it takes money from public schools (c32). The record carries this as
tx-2026-0204, admitted this run.

**WHAT THE FACT CHECK CHANGED.**
- **The Marauder's length is not claimed** (the foot mark could not be settled). No hull length is printed
  anywhere. The vessel the deck draws is ILLUSTRATIVE, 46 m, and every frame showing it says so in its
  kicker or dek.
- **No vote date.** The Tribune's June 18th article is the date carried, never a vote day.
- **Nothing says Saronic accepted the abatement.** The deck says the court approved it and the company had
  not chosen a site then. It never joins the abatement to the groundbreaking as a signed deal.
- **The 75,000 tonnes and the 7,401 production jobs are out** (each sits between em dashes in its source).
- **No sum of the Tribune's job breakdown** is drawn or printed.
- **The yard is not built.** Every quay, block line and build position is drawn to the release's figures
  and labelled as the plan.

## Why this treatment, and what was grafted

Three directors pitched THE YARD (an 850 foot hull drawn full size on the clay, then taken away), THE
COUNTY (a public lectern carried from the June courtroom to the waterfront, a granite bar 95% buried) and
THE BOAT (one windowless autonomous hull in the ship channel, through its states, to its painted
outline). THE BOAT is the spine, because the yard exists to make that kind of thing and it carries the
story's AI: a ship built to need nobody aboard. The hull was probed before synthesis
(`out/2026-10-07/tmp/probe/`) and reads as a vessel at true scale.

- From THE BOAT: the hero and its states (afloat, broadside with the payload drawn as one steel block,
  on blocks out of the water, small in its site), the mast at close range, the Marauder's figures as a
  diagram.
- From THE YARD: the release's figures drawn at true scale on the ground (850 feet as a line of keel blocks
  running into haze, the quay and the build positions in the plan's ink, the two acreages as squares of
  equal area), the plan's ink as the accent, and the close where the same camera shows the ground with
  the ship and the blocks gone.
- From THE COUNTY: one frame in the commissioners court, the room where the county voted, and the close's
  question about what the county can hold the company to.
- Refused: the lectern as hero (a third small carried prop in a week), the granite bar (a second hero),
  stormFront (a verdict on the deal) and blueHour (two days ago).

## The world, and the laws that hold it

**THE BROWNSVILLE SHIP CHANNEL AT MIDDAY, IN GULF HUMIDITY.** The chassis is
`assets/js/deck/2026-10-07-portalpha.js` and every frame loads it. It declares `sky: highNoon` with the
haze pulled to a humid Gulf grey and the light at azimuth 25 and elevation 58, the October sun high in the
south south east. The probe showed this world makes the water carry the sky and the grey hull read as
steel, which no other world did. +x is east, +z is south. The yard bank's edge lies on z = 0 with the land
north of it at 2.2 m above the water, the channel runs east and west, 180 m wide (illustrative), and the
far bank lies south.

1. **The light deck cap binds.** 09-30 sits in the eight run window at a median of 60.6, so this deck must
   stay under 60. The probe measured 64.7. The chassis exposes down to the deck's exposure, and every
   exterior frame gives at least half its height to water or ground. Planned deck median 53.
2. **Type is dark ink on the sky band**, the world's own `ink: 'dark'`, and never on the water.
3. The water is a `TXT.ground` plane at y 0, so it takes the grazing fade into the horizon, with a seeded
   non periodic normal map (never a sine) and a low roughness so it carries the sky.
4. Every standing thing gets `TXT.contact`, every frame `TXT.weather`, every bank a riprap edge.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#5E6266` | the DOM body behind the render |
| `accent` | `#4E5FA8` | bluebonnet, the plan's ink. It marks a figure from the release that is not built: the keel block line, the quay line, the build positions, the acreage squares, the leaders, and the seven vests. Frames 3, 4, 5, 7, 8, 9. Absent on 1, 2 and the courtroom at 6 |
| `hook` | `#16181C` | dark type on the noon sky |
| `dek` | `#2A2E34` | the dek |
| `rule` | `#2A2E34` | the site line, the source line and the counter |

The world's lit materials: haze grey hull #6E757C with a black boot top and red antifouling, deck grey
#3B4044, brackish channel #2C3A33, delta clay #8A7F6C, saltgrass straw #A39A6B, thornscrub olive #5F6A4E,
Washingtonia palms, riprap granite #9D978A, and the humid haze at the horizon.

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE
    VALUE ARC: held between 43.5 and 61.9, dipping at the courtroom turn, the deck median 56.6 under the light deck line

The medians are the measured renders, written before the panel: 59.5, 61.9, 58.6, 59.3, 54.2, 43.5, 52.6, 56.6, 56.2.

1. **Motif evolution.** The one autonomous hull changes state: afloat in the channel (1), its mast up
   close (2), broadside carrying one steel block of its payload (3), a speck at the bank of its 835 acres
   (4), out of the water on keel blocks at the head of an 850 foot block line (5), absent in the courtroom where the county voted (6), a speck at the head of the quay line (7), on blocks among the people who would build it (8), and
   gone with its blocks at the close (9).
2. **Camera move.** 01 across the channel, in to 02, back across for the broadside 03, up 450 m for 04,
   down to the yard ground for 05, indoors for 06, up 170 m along the bank for 07, back to the hull for 08,
   and 09 is frame 05's camera to the centimetre with the ship and the blocks gone.

## The rotation

    FULL_BLEED  CLOSE_CROP  DIAGRAM  SPLIT_HORIZON  FIGURE_SCALE  OBJECT_AND_CAPTION  FULL_BLEED  FIGURE_SCALE  FULL_BLEED

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | MEDIUM, standing eye 1.6 m on the south bank's riprap, horizon on the upper third | the channel water, a glossy brackish plane with a seeded two octave normal map carrying the noon sky, darkening toward the near bank, riprap stones wet at the waterline; the hull beyond in haze grey plate with seams, a black boot top and a wash line where it meets the water |
| 02 | CLOSE, eye 3 m on the yard bank's edge 14 m from the hull | the faceted deckhouse and mast, flat steel plate chamfered at 13 degrees, grime streaks under the sensor arms, the sun striking the top facets and the shaded side reading cool from the sky |
| 03 | WIDE, long lens from the south bank, horizon at mid frame | the hull broadside, plate strakes and butts, the rail, the boot top at the waterline, the steel block of the payload on the open deck in primer, its contact on the deck plate |
| 04 | AERIAL, 1,000 m up over the south bank looking north | the yard bank's scrub and delta clay, a graded square of bare clay for the 835 acres with a worn surface in world space, the scrub thinning at its edge, the larger square fading into haze |
| 05 | WIDE, standing eye 1.6 m on the graded yard | the hull out of the water on keel blocks, antifouling red below the boot top grimed where it sat in the water, each block in concrete and timber with a contact on the graded clay, the block line running 850 feet into haze |
| 06 | MEDIUM, seated eye 1.35 m in the back row's aisle in the commissioners court | the hearing dais in walnut veneer cropped past both edges, the public seating rows with residents seen from behind, a TXT.interior room with a lit window in the back wall |
| 07 | AERIAL, 170 m up over the channel's edge looking west along the bank | the bank, a riprap slope of individual stones under the yard's graded edge, the quay line in the plan's ink along it, the build position rectangles running inland, the water in the near third |
| 08 | MEDIUM, standing eye 1.6 m beside the hull on blocks | the hull's flank on its blocks, the plate's grime and drain streaks, twenty workers on the clay beneath it, seven in the plan's ink |
| 09 | WIDE, frame 05's camera to the centimetre | the graded yard clay, worn in world space with tyre tracks and grit, the 850 foot line in the plan's ink running into haze, the person and the pickup at the near end with their contacts |

Showstopper frame: 01, the grey hull across the brackish channel at noon, its boot top and wash at the water, the far bank's palms and haze behind, the near riprap giving the depth
Tonal arc: held mid light through the exterior frames near 52, lifting on 05 and 09 where the bright clay fills the frame, dipping on 06 indoors at the turn, the closing pair 05 and 09 the brightest

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "an autonomous hull afloat in the Brownsville Ship Channel, seen across the water from the south bank, its boot top and wash at the waterline"
  rect: [0, 430, 1080, 920]
  bleeds: [left, right, bottom]
accent: none
job: >
  Put the thing the yard exists to make in front of the reader, in the water where it would sail, and say
  in the first line that the county's break came before the site.

claims: [c1, c6, c26, c27]
numerals: []

depth:
  eye: 1.6
  horizon: 450
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 24}

composition:
  structure: >
    The camera stands on the south bank's riprap, the near stones in the lower left corner. The hull lies
    three quarters on across the middle third, its bow to the right, the far bank's scrub and palms on the
    horizon on the upper third. The type sits in the sky above.
  bands: >
    Top third, the noon sky and the hook. Middle third, the hull, the far bank and the haze. Bottom third, the brackish water darkening toward the camera, its texture a seeded noise of wind ruffle that carries a dim wash of the haze, and the wet riprap stones in the foreground corner lit on their tops with dark shadow between them.
  focal: "the hull's lit flank and its dark deckhouse against the pale haze"

art:
  technique: "physically based render, the chassis hull on a glossy water ground with a seeded normal map, the kit palm and mesquite on the far bank"
  why_this_technique: "a ship reads as a ship only in water that carries the sky and a wash at its waterline"
  palette: "haze grey hull, brackish channel green, delta scrub olive, Gulf haze"
  value_structure: >
    Lightest is the sky at the horizon and the lit hull flank. Darkest is the near water and the boot top.
    Frame median L* planned at 59.5.

type:
  hook: "The tax break came first"
  dek: "Saronic broke ground on Port Alpha, a shipyard for autonomous and manned ships, at the Port of Brownsville on September 30th. The Tribune reported the county approved its tax break in June, before Saronic had picked the port. The vessel is drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the hull spans at least 45 percent of the frame's width and stands at least 110 px tall at 432 px, in the middle third"
  - "a black boot top and a broken white wash line run along the hull where it meets the water"
  - "the channel water owns at least a third of the frame height, darker than the sky, with no regular ripple"
  - "no tree, palm or mast crosses a glyph of the hook or the dek"
  - "the far bank shows as land with trees on the horizon, never as open sea"
  - "the hook reads 'The tax break came first' in dark ink on the sky"

risks:
  - "the hull reads as Saronic's real design, so the dek says it is drawn to illustrate"
  - "a flat sea horizon, so the far bank carries scrub, palms and a low structure"
```

```yaml
slide: 2
layout: CLOSE_CROP
primary_image:
  subject: "the hull's faceted deckhouse and sensor mast seen from the bank at close range, no window anywhere"
  rect: [240, 600, 840, 750]
  bleeds: [right, bottom]
accent: none
job: >
  Show what replaces a bridge on a ship built to need no crew, and give the company's own claim for what
  an autonomous boat has done.

claims: [c24]
numerals: []

depth:
  eye: 3.0
  horizon: 1010
  cues: [LINEAR_PERSPECTIVE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: 9}

composition:
  structure: >
    The camera stands on the yard bank's edge looking up and south at the deckhouse and the mast, the mast
    rising into the upper right. The far bank sits low, under the deckhouse line, so the frame keeps its
    horizon.
  bands: >
    Top third, the sky and the mast's sensor arms. Middle third, the faceted deckhouse catching the sun on
    its top facets. Bottom third, the deck edge and the rail lit along its top, a sliver of water carrying the light of the sky, and the far bank's scrub in haze under the deckhouse line.
  focal: "the sunlit top facets of the deckhouse against the darker sky above the mast"

art:
  technique: "physically based render, the chassis deckhouse and mast as faceted flat plate"
  why_this_technique: "flat chamfered plate is how a ship with no windows reads at close range"
  palette: "haze grey plate, dark sensor housings, noon blue sky"
  value_structure: >
    Lightest is the sky near the horizon and the top facets. Darkest is the shaded side of the deckhouse.
    Frame median L* planned at 61.9.

type:
  hook: "An autonomous boat made a rescue, Saronic says"
  dek: "Its home page claims the first known at-sea rescue by an autonomous boat. The deckhouse and mast are drawn to illustrate, not Saronic's design."
  labels: []

verbatim:
  - c24: "first known at-sea rescue by an autonomous boat"

acceptance:
  - "the deckhouse and mast fill at least half the frame's height"
  - "no window, no ladder and no door with glass shows anywhere on the deckhouse or mast"
  - "a line of far bank or water shows below the deckhouse so the frame keeps a horizon"
  - "the top facets are measurably lighter than the side facets at 432 px"
  - "the hook reads 'An autonomous boat made a rescue, Saronic says'"

risks:
  - "a camera pointed up loses its horizon and print_ban fails it, so the far bank is kept in frame"
```

```yaml
slide: 3
layout: DIAGRAM
primary_image:
  subject: "the hull broadside on a long lens with one steel block of its payload on the open deck, leaders to the block, the mast and the stern"
  rect: [0, 560, 1080, 520]
  bleeds: [left, right]
accent: "#4E5FA8"
job: >
  Give Saronic's own figures for its Marauder and make the payload a thing with a size.

claims: [c23, c16]
numerals:
  - value_from: c23

data_in_art:
  figure: payload_block_edge_m
  drives: the cube's edge length on the deck, 2.673 m, 150 metric tons of steel as one block

depth:
  eye: 1.8
  horizon: 760
  cues: [RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: 24}

composition:
  structure: >
    A long lens from the south bank holds the hull exactly side on across the frame, the horizon at mid
    height. The steel block sits on the after deck. Three leaders in the plan's ink run up from the block,
    the stern and the mast to labels in the sky.
  bands: >
    Top third, the hook and the three labels on the sky. Middle third, the hull broadside and the block.
    Bottom third, the water under the hull, its texture a seeded wind ruffle carrying a dark wash of the hull's reflection and a lighter wash of the haze toward the frame's foot.
  focal: "the steel block on the after deck, primer red on grey plate"

art:
  technique: "physically based render with DOM SVG leaders that land on the projected points"
  why_this_technique: "a leader that lands on the block makes the payload a measured object, not a number"
  palette: "haze grey hull, primer red block, bluebonnet leaders"
  value_structure: >
    Lightest is the sky. Darkest is the boot top and the water under the hull. Frame median L* planned at 58.6.

type:
  hook: "What Saronic says its Marauder does"
  dek: "These are Saronic's figures for its Marauder. The release names Navy landing craft for the yard's first phase. The hull and the block are drawn to illustrate."
  labels: ["TOP SPEED 25+ KNOTS", "RANGE UP TO 5,400 NAUTICAL MILES", "PAYLOAD 150 METRIC TONS, DRAWN AS ONE STEEL BLOCK"]

verbatim: []

acceptance:
  - "the steel block reads as a solid cube on the deck at 432 px, at least 30 px on a side at full size"
  - "each leader ends on the projected point it names, within 24 px, written to __txLeaders"
  - "every label sits on the sky, no leader crosses a glyph and no palm stands in a label"
  - "the hull runs at least 70 percent of the frame's width"
  - "the hook reads 'What Saronic says its Marauder does'"

risks:
  - "the block reads as a deckhouse, so it is primer red and squared off with a contact on the deck"
```

```yaml
slide: 4
layout: SPLIT_HORIZON
primary_image:
  subject: "the yard bank from 1,000 m up over the south bank, a graded square of clay drawn to the area of 835 acres and a larger square to nearly 4,400, both edged in the plan's ink"
  rect: [0, 900, 1080, 450]
  bleeds: [left, right, bottom]
accent: "#4E5FA8"
job: >
  Make 835 acres and the option to nearly 4,400 a size on the ground beside the channel.

claims: [c2, c3]
numerals:
  - value_from: c2
  - value_from: c3

data_in_art:
  figure: site_side_m
  drives: the side length of the graded square, 1838.2 m, and option_side_m sets the outer square's side length at 4219.7 m

depth:
  eye: 1000
  horizon: 660
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: -900}

composition:
  structure: >
    The camera hangs 1,000 m over the south bank looking north, pitched five degrees down, so the sky band
    holds the type. The graded square fills the lower half from the bank, and the larger square's dashed
    far edge and sides lie beyond it toward the haze.
  bands: >
    Top third, the sky, the hook and the horizon haze. Middle third, the graded square and the scrub
    around it. Bottom third, the channel water in shadow tone with a seeded ruffle texture, the near bank's riprap lit on the stone tops, and the speck of the hull with its shadow at the bank.
  focal: "the bare graded square, lighter than the scrub around it"

art:
  technique: "physically based render at aerial scale, a dirt ground square over scrub scatter, accent edges as flat strips on the ground"
  why_this_technique: "an equal area square at true scale is the honest way to draw an acreage whose shape is not in the record"
  palette: "delta clay, thornscrub olive, brackish channel, bluebonnet edges"
  value_structure: >
    Lightest is the graded clay square and the horizon haze. Darkest is the channel water. Frame median L* planned at 59.3.

type:
  hook: "835 acres, and an option on more"
  dek: "Port Alpha sits on 835 acres, with an option to expand to nearly 4,400, Saronic says. Each is drawn as a square of that area, not the site's real shape."
  labels: []

verbatim: []

acceptance:
  - "the graded square is visibly lighter than the scrub around it at 432 px and owns at least a quarter of the frame's area"
  - "two outlines are distinguishable at 432 px, the inner one solid and closed, the outer one dashed with its far edge and both sides showing"
  - "the ground reads as soft patches of scrub and bare land, never a tiled checker"
  - "the type stands on the sky band above the horizon haze"
  - "the hook reads '835 acres, and an option on more'"

risks:
  - "the squares read as the parcel's real shape, so the dek says they are not"
```

```yaml
slide: 5
layout: FIGURE_SCALE
primary_image:
  subject: "the hull out of the water on keel blocks at the head of a line of blocks running 850 feet into haze, a person and a pickup beside it"
  rect: [0, 300, 1080, 700]
  bleeds: [left, right]
accent: "#4E5FA8"
job: >
  Give 850 feet a size a reader can stand beside, against the illustrated hull and a person.

claims: [c9, c10]
numerals:
  - value_from: c9
  - value_from: c10

data_in_art:
  figure: vessel_m
  drives: the length of the keel block line, 259.1 m from the hull's stern to the last block

depth:
  eye: 1.6
  horizon: 470
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, TEXTURE_GRADIENT]
  subject_at: {X: -12, Z: -60}

composition:
  structure: >
    A standing eye on the graded yard. The hull sits on its blocks at the left, bow toward the camera. The
    block line runs from its stern away to the right into haze, a painted line in the plan's ink beside
    it. A person and a pickup stand in the near right.
  bands: >
    Top third, the sky and the hook. Middle third, the hull and the receding block line. Bottom third, the graded clay lit by the high sun with tyre tracks and grit in its texture, the person and the pickup each with a contact shadow on the clay, and the near ground in the foreground.
  focal: "the hull's red antifouling and black boot top above its blocks"

art:
  technique: "physically based render, the chassis hull and keel blocks, the kit person and pickup at true scale"
  why_this_technique: "a person and a pickup beside a hull and its blocks give 850 feet a size no number gives"
  palette: "haze grey and antifouling red, concrete and timber blocks, delta clay, bluebonnet line"
  value_structure: >
    Lightest is the graded clay and the haze. Darkest is the boot top and the shadow under the hull.
    Frame median L* planned at 54.2.

type:
  hook: "Room for ships up to 850 feet"
  dek: "Saronic says the yard will first build vessels up to 850 feet. An expansion could support vessels over 1,200 feet. The blocks run 850 feet and the hull is drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the block line visibly continues from the hull's stern into haze and its last block is within the frame or the haze"
  - "the hull stands on blocks with daylight under its keel and a contact under each block"
  - "a person stands under a fifth of the frame's height near the hull, and the hull on its blocks stands at least 150 px tall at 432 px"
  - "the painted line beside the blocks shows in the accent"
  - "the hook reads 'Room for ships up to 850 feet' and no mast or sensor rises into it"
  - "the person wears work clothes and no vest, so the accent means only the plan's line"

risks:
  - "the block line is sub-pixel past 150 m, so each block is 1.4 m tall and the painted line 0.6 m wide"
```

```yaml
slide: 6
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "the Cameron County commissioners courtroom from the back row's aisle, the walnut dais cropped past both edges under a lit window in the back wall, residents seated from behind"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: none
job: >
  Put the reader in the room where the county gave the break, before it knew the site.

claims: [c26, c27, c28, c37]
numerals:
  - value_from: c26
  - value_from: c28

depth:
  eye: 1.15
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: -5}

composition:
  structure: >
    A seated eye in the back row's aisle seat. The public rows lead to the dais across the room, residents
    seated on the chairs seen from behind. A tall window in the back wall behind the dais lights the room,
    the county seal and the flags at the right.
  bands: >
    Top third, the room's back wall and ceiling with the hook. Middle third, the dais and the seated
    residents. Bottom third, the black chair backs nearest the camera lit along their top rails by the window light, the carpet's texture and the shadow of each chair on it.
  focal: "the lit walnut front of the dais"

art:
  technique: "physically based render in a TXT.interior room, the kit hearing_dais, public_seating and person"
  why_this_technique: "the county's decision happened in a room, and a room is a real frame"
  palette: "walnut, institutional wall beige, carpet blue grey, noon window light"
  value_structure: >
    Lightest is the window and the lit dais. Darkest is the chair backs nearest the camera. Frame median L* planned at 43.5.

type:
  hook: "The county voted before a site was chosen"
  dek: "The Texas Tribune reported on June 18th that the court approved a $211 million tax break for Saronic, a 95% abatement over 20 years. Saronic said then it had not chosen a site."
  labels: []

verbatim: []

acceptance:
  - "the dais spans the frame's width, is cropped by both edges and stands at least 90 px tall at 432 px"
  - "residents are seen from behind and no face shows at more than a fifth of the frame"
  - "a lit window shows in the back wall"
  - "every seated resident sits on a chair"
  - "the room stands in a TXT.interior with a wainscot, a seal and flags, never a flat background"
  - "the hook reads 'The county voted before a site was chosen'"

risks:
  - "the kit person reads as a mannequin, so every person is turned away and small"
```

```yaml
slide: 7
layout: FULL_BLEED
primary_image:
  subject: "the yard bank from 260 m up over the channel looking inland, the quay line in the plan's ink running 2,500 feet along the riprap, two build positions drawn solid and two dashed"
  rect: [0, 600, 1080, 620]
  bleeds: [left, right]
accent: "#4E5FA8"
job: >
  Put the quay and the build positions on the bank at the release's figures, as the plan they are.

claims: [c13, c14, c12]
numerals:
  - value_from: c13
  - value_from: c14
  - value_from: c12

data_in_art:
  figure: quay_m
  drives: the length of the quay line along the bank, 762 m, and positions_min sets two solid build positions with positions_max dashed to four

depth:
  eye: 260
  horizon: 160
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, CAST_SHADOW, TEXTURE_GRADIENT]
  subject_at: {X: -380, Z: -60}

composition:
  structure: >
    An aerial oblique over the water's edge looking west along the bank. The quay line runs from the near
    left into haze. The build positions run inland from it as long rectangles. The hull floats small at
    the near end.
  bands: >
    Top third, the sky and the hook over the haze. Middle third, the bank, the quay line and the build
    positions receding. Bottom third, the channel water in shadow tone with a seeded ruffle texture, and the near riprap slope with each stone lit on its top and dark between, the bank's graded edge above it.
  focal: "the near build position's bright graded rectangle edged in the accent"

art:
  technique: "physically based render at aerial scale, flat accent strips on the ground, the chassis hull for scale"
  why_this_technique: "lines at true scale on the real ground are the plan, drawn without pretending it is built"
  palette: "brackish channel, riprap grey, delta clay, bluebonnet lines"
  value_structure: >
    Lightest is the graded build positions and the haze. Darkest is the near water. Frame median L* planned at 52.6.

type:
  hook: "More than 2,500 feet of quay, planned"
  dek: "Saronic says two to four build positions will handle final ship erection, beside 8 to 10 production buildings. The quay is drawn to its length, the rest to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the quay line runs along the bank from the near frame into haze, and the bank with its riprap owns at least a third of the frame height"
  - "four build positions are counted at 432 px as closed rectangles, two solid and two dashed, all in the accent, and no other accent line competes with them"
  - "the hull shows small at the near end of the quay line"
  - "the water fills at least a fifth of the frame's height in the lower part"
  - "the hook reads 'More than 2,500 feet of quay, planned'"

risks:
  - "accent lines thinner than 6 m vanish at 80 m up, so each strip is 8 m wide"
```

```yaml
slide: 8
layout: FIGURE_SCALE
primary_image:
  subject: "twenty workers on the clay before the hull on its blocks, seven in vests in the plan's ink"
  rect: [0, 560, 1080, 720]
  bleeds: [left, right]
accent: "#4E5FA8"
job: >
  Give the jobs the release promises and the local share the abatement requires a picture of people.

claims: [c5, c29]
numerals:
  - value_from: c5
  - value_from: c29

data_in_art:
  figure: crew_local_drawn
  drives: the count of accent vests, 7 of crew_drawn 20 people, the 35% local share

depth:
  eye: 1.6
  horizon: 420
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: -40}

composition:
  structure: >
    A standing eye beside the hull's flank on its blocks. The workers stand and walk on the clay in the
    hull's shade and in the sun at its edge, the seven accent vests spread through them.
  bands: >
    Top third, the sky and the hook over the hull's sheer. Middle third, the hull's flank. Bottom third, the workers on the graded clay, half in the hull's shadow and half lit by the high sun, each with a contact shadow, the clay's texture of tracks and grit between them.
  focal: "the group of workers in the sun at the hull's bow"

art:
  technique: "physically based render, the kit crowd and person at true scale under the chassis hull"
  why_this_technique: "people at their real size beside a hull give the jobs figure a body"
  palette: "haze grey hull, delta clay, work clothes, bluebonnet vests"
  value_structure: >
    Lightest is the sky and the sunlit clay. Darkest is the shade under the hull. Frame median L* planned at 56.6.

type:
  hook: "Up to 10,000 jobs, Saronic says"
  dek: "The Tribune reported the break would require 35% of the full-time workforce to be local. Seven of the twenty drawn here wear the local share."
  labels: []

verbatim: []

acceptance:
  - "exactly twenty people are counted at full size, none hidden behind another, and exactly seven wear accent vests"
  - "the kicker says the frame is drawn to illustrate, and no mast rises into the hook"
  - "every person stands on the clay with a contact and none is cropped at the face"
  - "the hull's flank fills the middle third and stands at least 150 px tall at 432 px"
  - "the hook reads 'Up to 10,000 jobs, Saronic says'"

risks:
  - "a crowd of kit people reads as mannequins, so they stand at 15 to 30 m and turn in different directions"
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: "frame 05's camera to the centimetre, the hull and the blocks gone, the 850 foot line in the plan's ink alone on the graded clay, the person and the pickup at its near end"
  rect: [0, 640, 1080, 520]
  bleeds: [left, right]
accent: "#4E5FA8"
job: >
  Leave the reader on the condition the county can hold the company to, over the ground where the
  frame 05 hull stood.

claims: [c30, c32, c9]
numerals:
  - value_from: c9

data_in_art:
  figure: vessel_m
  drives: the length of the painted line, 259.1 m, the same 850 feet the blocks ran on frame 05

depth:
  eye: 1.6
  horizon: 470
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, TEXTURE_GRADIENT]
  subject_at: {X: -12, Z: -60}

composition:
  structure: >
    Frame 05 exactly, with the hull and its blocks removed. The painted line runs away into haze where
    the blocks stood. The person and the pickup stand where they stood.
  bands: >
    Top third, the sky and the hook. Middle third, the line receding into haze and the empty ground.
    Bottom third, the graded clay lit by the high sun with tyre tracks and grit in its texture, the person and the pickup each with a contact shadow on the clay, and the near ground in the foreground.
  focal: "the near end of the painted line on the bright clay"

art:
  technique: "physically based render, frame 05's camera, the kit person and pickup"
  why_this_technique: "the same camera with the ship gone is the plainest way to say the yard is not built"
  palette: "delta clay, bluebonnet line, Gulf haze"
  value_structure: >
    Lightest is the graded clay and the haze. Darkest is the shadow under the pickup. Frame median L* planned at 56.2.

type:
  hook: "The break would shrink if jobs fall short"
  dek: "The Tribune reported the condition, and that opponents told the court the break would take money from public schools. The line runs 850 feet, the longest Saronic says the yard can build at first."
  labels: []

verbatim: []

acceptance:
  - "the camera, the person and the pickup are identical to frame 05 to the pixel"
  - "no hull and no keel block shows anywhere in the frame"
  - "the graded yard clay owns at least 40 percent of the frame height, worn with tyre tracks and grit at full size"
  - "the painted line in the accent runs from the near ground into haze"
  - "the hook reads 'The break would shrink if jobs fall short' and the kicker says the frame is drawn to illustrate"

risks:
  - "an empty frame reads as unfinished, so the line and the person carry it"
```
