# Storyboard, 2026-10-12
# "It judges flood risk on the device"

## The story, and what the fact check did to it

UT San Antonio's release of September 28th, 2026 describes a field-ready prototype flood warning node
(c3) led by Chen Pan (c13), with Mimi Xie of UTSA and Hua Zhang and Wenlu Wang of Texas A&M
University-Corpus Christi (c14). It carries four optical water-level sensors mounted at varying heights
(c1) and senses temperature, humidity, light and precipitation (c2). TinyML runs a compressed machine
learning model on a small low-power microcontroller (c4), which judges imminent local flood risk from
current and recent readings without a central server (c5, c6). A solar system charges its battery (c8),
and a LoRa radio reaches more than a half-mile through city streets and up to five miles open (c9), to a
central site where a second, larger model draws predictive maps (c10). The release reports 98.82%
validation accuracy in initial assessments post-training (c7), and parts for one prototype cost roughly
$150 to $220 (c11). Pan is pursuing a patent and the team aims at a weatherized commercial product (c12).
NOAA's Texas Coastal Management Program funded it in part (c15). The release frames the danger at
"low-water crossings in San Antonio" (c16). The record carries it as tx-2026-0141.

**WHAT THE FACT CHECK CHANGED.**
- **The release is dated September 28th**, not September 8th as the record held. The record was corrected
  this run.
- **The release names no installation site, no operating city or county, no field test against a real
  flood and no false alarm or missed event figure (c19).** Every node, crossing and water level in the deck
  is drawn to illustrate, and the deks say so.
- **The sensor heights, the housing and the mounting are not in the release.** No height or depth numeral
  is printed anywhere, and the depth gauge carries no numerals.
- **UT Arlington's radar finding (c20, c21) and the NWS line on drownings (c22) are context, not this
  device.** Their frames attribute them by name.

## Why this treatment, and what was grafted

Three directors pitched THE INSTRUMENT (the water climbing the node's four sensors is the argument), THE
CROSSING (one low water crossing met from the driver's seat, ending on the turn around) and TESTED ON DATA,
NOT ON A FLOOD (every figure comes from a bench or a spec sheet, none from water at a crossing).

- From THE CROSSING, the spine and the bookends: the cover from the driver's eye with the edge lines running
  under the water, the radar columns on the bank, the map with reach circles in a legend rather than on a
  site, the parts on dry asphalt, and the close on a pickup caught mid turn.
- From THE INSTRUMENT, the motif: one ring lit at the waterline on the cover, two in the diagram, three at
  the waterline macro and on the close, the fourth never. The macro at the waterline is its frame.
- From TESTED ON DATA, the evidence frame: the node's own rail laid along the slab's lip as a bar lit for
  98.82 of 100 units with the bare remainder at the end stop, and the closing absences scoped to the
  release.
- **Refused:** the lab bench interior (a second world for two frames), the macro of a circuit board (a new
  close range model no source describes), a dollar-graduated steel rule (a chart convention on an object),
  the green status lamp (a second accent, and an all-clear light is a verdict).
- **The accent.** The chassis was drafted with a warning red. Two directors argued, correctly, that a red
  ring on a flood sensor reads as an alarm that fired, which is exactly the verdict a prototype with no
  field test can't carry. The accent is BEACON AMBER #FFA21F, the colour of the flashing beacons on Texas
  flood signs, the complement of the cold lamp, and distinct from yesterday's dusk gold. It lights ONLY a
  sensor ring the water has reached, at one intensity, never a ramp.

## The world, and the laws that hold it

**ONE LOW WATER CROSSING AT NIGHT.** The chassis is `assets/js/deck/2026-10-12-crossing.js` and every
frame loads it. It declares `sky: floodlit` with the key at azimuth -135 and elevation 48: the one cobra
head streetlight on the north west bank. +x is east and +z is south. The road runs north to south, the
creek west to east.

1. **Start dark.** A black sky, the lamp's pool on the subject, the banks gone to black.
2. **Type is light, on the dark field**, and every wash only darkens.
3. **The amber ring is the only accent.** Nothing else is warm and bright except the lamp's own white.
4. Every standing thing gets `TXT.contact`, every frame `TXT.weather`.
5. **Water reflects.** The floodwater is opaque and murky, and what stands above it is mirrored on its
   surface (`CH.mirror`), with the lamp's streak (`CH.streak`) and a wake where it meets a post.
6. **Nothing drawn is a real site.** The deks say drawn to illustrate.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#0C0D10` | the DOM body behind the render |
| `accent` | `#FFA21F` | beacon amber, a sensor ring the water has reached and nothing else: one ring on 1, two on 3, three on 8 and 9. Absent on 2, 4, 5, 6, 7 |
| `hook` | `#ECEAE4` | light type on the dark sky |
| `dek` | `#D9D6CE` | the dek |
| `material` | `#B9B4A8` | galvanized steel and concrete, the chassis material |

The world's materials: galvanized pipe, a satin aluminium rail, grey polycarbonate, black clearcoat lenses,
pale limestone concrete slab and footing, wet black asphalt with chalk white edge lines, silt brown
floodwater, black green juniper and live oak, the lamp's cold white. No caliche, no rust, no Gulf blue.

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE

1. **Motif evolution.** The water climbs the node's rail: one ring lit at the waterline (1), the node standing
   beyond the columns (2), two rings (3), the box above the water (4), a plan glyph at the centre of two circles (5),
   a built node beside its own parts on dry asphalt (6), the node behind the column (7), three rings at the waterline
   (8), three rings and a turning pickup (9). The fourth sensor is never wet.
2. **Camera move.** The driver's eye down the grade (1), low on the bank (2), across the creek to the node (3), up to
   its box (4), above the county (5), down on the asphalt (6), level along the slab's lip (7), at the waterline (8),
   and the waterline turned to face the road (9).

## The rotation

    FULL_BLEED  SPLIT_HORIZON  DIAGRAM  CLOSE_CROP  MAP  GRID  OBJECT_AND_CAPTION  CLOSE_CROP  FULL_BLEED

Reordered after the flow review's first round: the radar finding is the stake straight after the cover, the device
runs unbroken from its parts to its reach to its cost, the score turns the deck at 7 and the absences pay it off at 8.

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | WIDE, eye 1.6 m on the south approach, the driver's seat, looking north down the grade into the flooded dip, horizon on the upper third | the flood node on the east shoulder, galvanized post on a footing in the water, aluminium rail with four lensed sensors, one amber ring at the waterline, grey enclosure, panel and arms rim lit by the lamp, mirrored on the water; the asphalt approach and its chalk edge lines running under brown water with a foam line at the slab's lip |
| 02 | MEDIUM, eye 0.35 m on the bank top, long lens, level | two clear rain columns on round bases, the left filled full and the right filled short by the computed share, lit from behind by the lamp so the water glows; the node soft and small beyond |
| 03 | MEDIUM, eye 1.5 m, a long lens at 11 m from the west south west, near elevation | the whole flood node, galvanized pipe and satin aluminium with grey polycarbonate, rim lit by the cold lamp down its north west edges, a wake at its foot, grime toward the waterline, two amber rings |
| 04 | CLOSE, eye 1.3 m, 0.7 m below and off the enclosure, looking up | the enclosure, grey polycarbonate with a gasket seam, mottled and dusty, lit along its lid edge by the lamp, its underside in shadow, cable glands grimed |
| 05 | AERIAL, a plan, Bexar County at one scale | Bexar County's real boundary from the committed geodata as a dark slab with its north west edge lit, San Antonio placed, and a legend outside the county holding two reach circles at the map's own scale around a plan glyph of the node |
| 06 | WIDE, eye 1.6 m on the south approach's dry asphalt 6 m back, pitched down 20 degrees, the water a band at the top | the node in parts laid in rows on wet black asphalt in the lamp's pool, post in two lengths, the rail with its four sensors, the enclosure, the panel, the antenna, the rain gauge, six shield plates and the footing ring, each with its contact shadow; a cold white cost bar on the asphalt at one centimetre per dollar |
| 07 | MEDIUM, eye 0.23 m over the dry slab, 4.7 m off, looking east south east and up | one tall clear measuring column on the slab's downstream lip, acrylic on an aluminium base with hairline ticks, its water glowing cold to 98.82 of its 100 units with the meniscus a bright line, the empty sliver of dark glass under the rim, its contact shadow on the concrete |
| 08 | MACRO, eye 1.0 m, 0.9 m off the rail, at the waterline | the sensor rail, satin aluminium with black clearcoat lenses, lit by the lamp from the upper left, silt grime below the waterline, its wake on the water and its image mirrored in it |
| 09 | WIDE, eye 1.0 m at the waterline on the east bank, looking south west up the approach | the node in the water to its third sensor, left of centre, three amber rings; a kit pickup stopped across the lane mid turn up the grade, its lamps emissive, the edge lines entering the water short of its bumper |

Showstopper frame: 01, the chalk edge lines of a Hill Country road running down into a sheet of brown floodwater under one cold lamp, a solar sensor post standing in it with one amber ring burning at the waterline and its image on the water
Tonal arc: black around the lit node and road on 1, the glowing water in the glass on 2 the brightest small thing, black around the node on 3, tightest and darkest at the box on 4, darkest on the map at 5, the asphalt pool at 6, a column of cold light at 7, closest and darkest water at 8, settling on 9 with the amber at the post and the truck turned away

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "the flood node standing on the east shoulder of a flooded low water crossing, seen from the driver's eye on the south approach, its four sensors on the rail with the first ring amber at the waterline, the road's chalk edge lines running down under brown water"
  rect: [520, 260, 560, 1090]
  bleeds: [right, bottom]
accent: "#FFA21F"
job: >
  Put the place in front of the reader, name the device and the release, and say the AI runs on the post.

claims: [c3, c5, c16, c19]
numerals: []

data_in_art:
  figure: wet_cover
  drives: lit ring count on the rail, the water plane height set at the first sensor so 1 ring is lit and 3 are dark

depth:
  eye: 1.6
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 4.2, Z: -2}

composition:
  structure: >
    The camera stands on the south approach at a driver's eye, looking north down the grade. The two chalk
    edge lines run from the bottom of the frame down into brown water that covers the dip. The node stands on
    the east shoulder in the water, large in the right half, its panel near the top of the frame. The far
    approach climbs out of the water into black, with the lamp's pool on the water.
  bands: >
    Top third, the black sky with the hook and dek, the lamp's glow at the left edge. Middle third, the node's
    enclosure and arms, the far bank in black, the water's surface with the node's image. Bottom third, the
    near approach's wet asphalt with its lit texture and edge lines entering the water, the node's rail, its
    amber ring and its reflection in the foreground.
  focal: "the amber ring at the waterline on the node's rail, with the edge lines leading into the water beside it"

art:
  technique: "physically based render of the chassis flood node and low water crossing staged in the floodlit world, with mirrored reflections on opaque floodwater"
  why_this_technique: "a low water crossing is a place a Texan knows from the driver's seat, and only a modelled road running into lit water reads as that place"
  palette: "wet black asphalt, chalk edge lines, silt brown water, galvanized steel, grey polycarbonate, one beacon amber ring, the lamp's cold white"
  value_structure: >
    Lightest is the lamp's streak on the water and the node's lit rail. Darkest is the sky and the far banks.
    Frame median L* planned at 12.

type:
  hook: "It judges flood risk on the device"
  dek: "UT San Antonio's prototype runs its AI on the device, with no server. Its release says risk at San Antonio's low-water crossings often climbs before regional alerts sound. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the flood node stands in the right half with its panel, enclosure and sensor rail all in frame, and a frame without the node fails this item"
  - "the node stands at least 600 px tall at full size"
  - "exactly one sensor ring is lit in #FFA21F, at the waterline, and the three above it are dark"
  - "the two chalk edge lines run from the bottom edge into the water and stop at it"
  - "the node's image shows on the water's surface below it"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "a 4 cm ring at 4 m is small, so the camera stands close enough that the lit ring reads as a mark at 432 px"
  - "the water reads as a black void unless the lamp's streak and the node's image are on it"
```

```yaml
slide: 2
layout: SPLIT_HORIZON
primary_image:
  subject: "two clear rain columns side by side on the bank top, the left filled full and the right filled short by the radar share, lit from behind by the lamp so the water glows"
  rect: [260, 500, 560, 850]
  bleeds: [bottom]
accent: none
job: >
  Make the case for a local sensor first: a regional reading can come in low.

claims: [c18, c20]
numerals:
  - value_from: c20

data_in_art:
  figure: radar_fill_frac
  drives: the right column's water height as a fraction of the left's, one minus the radar's roughly 20 percent

depth:
  eye: 0.35
  horizon: 760
  cues: [CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A long lens level with the columns' middle, so the two heights compare without perspective. The columns
    stand on a flat limestone pad on the bank top. The lamp sits behind them out of frame, so the glass shows
    by its rim and the water inside glows. The node stands small and soft beyond in the dark.
  bands: >
    Top third, the hook and dek in black. Middle third, the two columns' upper halves and the difference
    between their water lines, with their labels. Bottom third, the aluminium bases on the limestone pad, its
    texture lit by the lamp behind and the contact shadows falling toward the camera.
  focal: "the two water lines, the left one higher, the brightest edges in the frame"

art:
  technique: "physically based render of two rendered lengths at one scale, glass backlit on a dark field"
  why_this_technique: "a percentage shortfall in rain is a difference in height, and two columns of water at one scale are the honest drawing of it"
  palette: "clear acrylic, rainwater lit cold, aluminium bases, pale limestone pad, black"
  value_structure: >
    Lightest is the water inside the columns. Darkest is the sky and the ground beyond. Frame median L* planned at 12.

type:
  hook: "Radar can read the storm low"
  dek: "UT San Antonio's release says regional models can miss very local flash floods. UT Arlington checked radar against more than 300 rain gauges and found it can read storm totals roughly 20% low under some conditions."
  labels: ["RAIN GAUGES", "RADAR"]

verbatim: []

acceptance:
  - "two rain columns stand side by side with water in both, and a frame without the columns fails this item"
  - "each column stands at least 380 px tall at full size"
  - "the right column's water line sits lower than the left's by a fifth of the left's height, measured off the render within 5 percent"
  - "the labels read \"RAIN GAUGES\" and \"RADAR\""
  - "the water in each column is plainly lighter than the field beside it"
  - "the frame's median L* at 432px is 20 or lower"

risks:
  - "glass on a dark field goes murky, so the lamp sits behind the columns"
```

```yaml
slide: 3
layout: DIAGRAM
primary_image:
  subject: "the whole flood node in near elevation, panel to footing, standing in the water with two amber rings at and under the waterline, leaders to its parts"
  rect: [620, 360, 460, 990]
  bleeds: [bottom]
accent: "#FFA21F"
job: >
  Name what the node carries, part by part, so the reader knows what the AI reads.

claims: [c1, c2, c4, c8]
numerals: []

data_in_art:
  figure: sensor_count
  drives: four rendered optical sensors on the rail, each with its own leader, the count c1 gives

depth:
  eye: 1.5
  horizon: 760
  cues: [CAST_SHADOW, AERIAL, OCCLUSION, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A long lens from the west south west makes the node read nearly parallel. It stands centre left in the
    water with the far bank black behind. Leaders run from the parts to mono labels in the black on the right.
  bands: >
    Top third, the hook and dek in the black sky, the panel at its foot. Middle third, the enclosure, arms and
    the labels for them. Bottom third, the rail and its sensors at the waterline, the lit wake, the post's
    shadow on the water and its reflection.
  focal: "the rail with its four sensors and the two lit rings, the brightest small marks in the frame"

art:
  technique: "physically based render of the node through a long lens, with DOM SVG leaders ending short of the glyphs"
  why_this_technique: "the claim is a list of parts on one object, and a diagram on the rendered object is the one form that names each part where it is"
  palette: "galvanized steel, aluminium, grey polycarbonate, white plastic of the gauge and shield, silt brown water, two amber rings"
  value_structure: >
    Lightest is the white rain gauge and shield and the lit rail. Darkest is the sky and the water away from the
    node. Frame median L* planned at 10.

type:
  hook: "Four water sensors stacked on one node"
  dek: "Four optical water-level sensors at varying heights, plus temperature, humidity, light and precipitation. Drawn to illustrate."
  labels: ["FOUR OPTICAL WATER-LEVEL SENSORS", "MICROCONTROLLER AND BATTERY", "TEMPERATURE AND HUMIDITY", "PRECIPITATION", "SOLAR PANEL"]

verbatim: []

acceptance:
  - "the whole node from panel to waterline is in frame, and a frame without the node fails this item"
  - "the node stands at least 900 px tall at full size"
  - "exactly two sensor rings are lit in #FFA21F and two are dark"
  - "a leader ends on each of the four sensors, and the label reads \"FOUR OPTICAL WATER-LEVEL SENSORS\""
  - "every leader ends at least 8 px short of its label's glyphs"
  - "the frame's median L* at 432px is 20 or lower"

risks:
  - "leaders crossing the hook or dek, so every label sits below the dek in the black"
  - "a long lens flattening the arms into one line, so the camera stays a little off square"
```

```yaml
slide: 4
layout: CLOSE_CROP
primary_image:
  subject: "the node's grey enclosure at detail scale from below, its lid seam, two cable glands and the rail's cable, the antenna and the panel's edge above against the black sky"
  rect: [560, 80, 520, 1150]
  bleeds: [right]
accent: none
job: >
  Show where the model runs, in the box on the post, with no server and no grid line.

claims: [c4, c5, c6]
numerals: []

data_in_art: null

depth:
  eye: 1.3
  horizon: 1150
  cues: [OCCLUSION, CAST_SHADOW, RELATIVE_SIZE]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera stands close below the enclosure looking up. The box fills the middle of the frame, cropped by
    the left and right edges, the post running up out of the top, the antenna and the panel's underside above.
    The lamp catches the lid's edge from the upper left.
  bands: >
    Top third, the hook and dek over the black sky and the panel's dark underside. Middle third, the enclosure,
    its seam and glands. Bottom third, the cable from the rail and the galvanized post lit down one edge, its
    shadow side falling into the dark.
  focal: "the lit lid edge of the enclosure and its cable glands"

art:
  technique: "physically based render at detail scale, the enclosure's polycarbonate weathered and the lamp raking it"
  why_this_technique: "the claim is that the model lives in a small box rather than a data center, and only the box at its own size makes that physical"
  palette: "grey polycarbonate, black glands and cable, galvanized post, the cold lamp edge"
  value_structure: >
    Lightest is the lid's lit edge. Darkest is the sky and the box's shadowed underside. Frame median L* planned at 9.

type:
  hook: "No server in the loop"
  dek: "TinyML shrinks a machine learning model to run on a small, low-power microcontroller. The model on the node judges imminent flood risk from current and recent readings without a central server."
  labels: []

verbatim: []

acceptance:
  - "the enclosure fills the middle of the frame with its lid seam and two cable glands visible, and a frame without the enclosure fails this item"
  - "the enclosure is at least 420 px wide at full size"
  - "no amber appears anywhere in the frame"
  - "the antenna rises from the enclosure toward the top edge"
  - "the frame's median L* at 432px is 18 or lower"

risks:
  - "a plain grey box reads as clay, so TXT.weather mottles it and the glands and seam carry the detail"
```

```yaml
slide: 5
layout: MAP
primary_image:
  subject: "Bexar County's real boundary as a dark slab with a lit north west edge, San Antonio placed, and a legend outside the county with two reach circles at the map's scale around a plan glyph of the node"
  rect: [60, 600, 960, 700]
  bleeds: []
accent: none
job: >
  Show how far the node's radio reaches, at the county's own scale, without placing it anywhere.

claims: [c9, c19]
numerals: []

data_in_art:
  figure: lora_open_m
  drives: the outer circle's radius at the map's scale, with the inner circle at lora_street_m on the same scale

depth: null

composition:
  structure: >
    The county is drawn large from the committed geodata in the deck's projection, a dark slab with its cast
    falling south east and its north west rim lit cold. San Antonio is a small lamp point. To the county's
    right, in a legend tray, two circles share the map's scale around a plan glyph of the node.
  bands: >
    Top third, the hook and dek. Middle third, the county and the legend tray. Bottom third, the county's
    southern half as an extruded slab with its cast shadow falling south east and the lit rim.
  focal: "the legend's two circles beside the county, the outer one's lit rim"

art:
  technique: "canvas cartography from TXGeo, solid shaded slab with a cast from the deck's key, the one companion frame"
  why_this_technique: "a reach in miles is a claim about a place, and the county's own outline is the one ruler a Bexar County reader carries"
  palette: "dark granite slab, the lamp's cold white rim, caliche ink for the labels"
  value_structure: >
    Lightest is the county's lit rim and the circles. Darkest is the field. Frame median L* planned at 8.

type:
  hook: "Over a half-mile in town, up to five miles open"
  dek: "The node's LoRa radio reaches more than a half-mile through city streets and up to five miles in open areas, the release says. No site is named, so the circles show scale only."
  labels: ["SAN ANTONIO", "BEXAR COUNTY", "OPEN AREAS", "CITY STREETS"]

verbatim: []

acceptance:
  - "Bexar County's outline from the committed geodata is drawn, and a frame without it fails this item"
  - "the county spans at least 520 px across at full size"
  - "the outer circle's radius is ten times the inner's, measured off the render within 5 percent"
  - "neither circle sits on the county"
  - "the frame's median L* at 432px is 14 or lower"

risks:
  - "circles centred on the county would imply a site the release never names"
```

```yaml
slide: 6
layout: GRID
primary_image:
  subject: "the node in parts laid in rows on dry wet-black asphalt in the lamp's pool: post in two lengths, the rail with its four sensors, the enclosure, the panel, antenna, rain gauge, six shield plates and the footing ring, with a cold white cost bar on the asphalt"
  rect: [0, 700, 1080, 420]
  bleeds: [left, right]
accent: none
job: >
  Show the prototype as the kit of parts it is today, and what the parts cost.

claims: [c11, c15]
numerals:
  - value_from: c11

data_in_art:
  figure: cost_low_m
  drives: the cost bar's solid length at one centimetre per dollar, with the open channel on to cost_bar_m

depth:
  eye: 1.2
  horizon: 330
  cues: [CAST_SHADOW, RELATIVE_SIZE, TEXTURE_GRADIENT, LINEAR_PERSPECTIVE]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera stands on the dry approach above the water, pitched down, the parts in rows filling the lower
    two thirds. The cost bar runs across the front row. The flooded dip is a black band at the top under the
    horizon.
  bands: >
    Top third, the hook and dek over the black and the water's far edge. Middle third, the larger parts, the
    post, the panel and the enclosure. Bottom third, the four sensors and the shield plates on the asphalt's
    lit texture, each with its contact shadow, and the cost bar's glow.
  focal: "the four sensors laid in a row, the repeated unit, and the cost bar under them"

art:
  technique: "physically based render, a knolled grid of the chassis node's own parts on worn asphalt, each with its contact shadow"
  why_this_technique: "a parts cost is a claim about a kit, and the kit laid out at true size is the only way to show what the money buys"
  palette: "wet black asphalt, galvanized steel, aluminium, grey polycarbonate, white plastic, the lamp's cold white bar"
  value_structure: >
    Lightest is the cost bar and the white plates. Darkest is the asphalt beyond the pool. Frame median L* planned at 14.

type:
  hook: "$150 to $220 in parts"
  dek: "Parts for one prototype station cost roughly $150 to $220, the release says. A Texas Coastal Management Program grant approved by the Texas Land Commissioner helped fund the work. The parts are drawn to illustrate."
  labels: ["$150", "$220"]

verbatim: []

acceptance:
  - "the four sensors lie in a row with the post, the panel and the enclosure beside them, and a frame without the sensors fails this item"
  - "the parts span at least 80 percent of the frame width"
  - "the cost bar's solid length is 150 of 220 units of its full length, measured off the render within 5 percent"
  - "every part has a contact shadow on the asphalt"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "a grid of small parts reads as clutter, so the rows are spaced and the pool is tight"
```

```yaml
slide: 7
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "one tall clear measuring column standing on the crossing's dry slab at night, its water glowing cold to 98.82 of its 100 units, the empty sliver of glass under the rim, labels 100 at the rim and 98.82 at the water's top"
  rect: [600, 360, 460, 960]
  bleeds: []
accent: none
job: >
  Put the one score the release gives at its true size, and say what it was scored on.

claims: [c7, c19]
numerals:
  - value_from: c7

data_in_art:
  figure: validation_lit_m
  drives: the column's water height as validation_lit_m over validation_bar_m of the column's full height, with the empty sliver under the rim

depth:
  eye: 0.55
  horizon: 940
  cues: [CAST_SHADOW, AERIAL, RELATIVE_SIZE]
  subject_at: {X: 3.6, Z: 0}

composition:
  structure: >
    A low camera just over the dry slab looks east south east and a little up at one tall measuring column
    standing on the slab's downstream lip, right of the type. The creek and the far bank are dark behind it. Two
    mono labels sit to its right, 100 at the rim and 98.82 at the water's top.
  bands: >
    Top third, the hook and dek on black, the column's rim and the two labels. Middle third, the glowing water
    in the column against the dark creek. Bottom third, the column's aluminium base on the slab's lit texture,
    its contact shadow falling south east, the slab's edge and the dark water beyond.
  focal: "the bright meniscus line just under the dark rim, the empty sliver between them"

art:
  technique: "physically based render, a single measuring column at true scale, its water emissive and glowing on the dark field"
  why_this_technique: "a validation share is a fill against a whole, and a measuring column filled to its figure is the honest drawing of a score taken on data rather than in a flood"
  palette: "clear acrylic, cold glowing water, aluminium, pale limestone concrete, black"
  value_structure: >
    Lightest is the glowing water and the meniscus line. Darkest is the sky and the creek. Frame median L* planned at 6.

type:
  hook: "98.82%, scored on data"
  dek: "The release reports 98.82% validation accuracy in initial assessments after training."
  labels: ["FULL SCALE", "98.82%"]

verbatim: []

acceptance:
  - "one measuring column stands on the slab with glowing water inside it, and a frame without the column fails this item"
  - "the column stands at least 750 px tall at full size"
  - "the water's top sits below the rim by 1.18 percent of the column's height, measured off the render within 30 percent of that sliver"
  - "the labels read \"FULL SCALE\" and \"98.82\", with \"FULL SCALE\" above \"98.82\""
  - "no amber appears anywhere in the frame"
  - "the frame's median L* at 432px is 18 or lower"

risks:
  - "the sliver is about 10 px at full size, so the meniscus is drawn as a bright line under a dark rim"
  - "looking toward the lamp washes the frame, so the camera faces away from it"
```

```yaml
slide: 8
layout: CLOSE_CROP
primary_image:
  subject: "the node's rail at the waterline, cropped by the top and bottom edges, the fourth sensor dry above the surface with its ring dark, the third under the murky water with its ring lit amber"
  rect: [580, 0, 330, 1350]
  bleeds: [top, bottom]
accent: "#FFA21F"
job: >
  Say what the release does not name, on the thing it describes.

claims: [c1, c19]
numerals: []

data_in_art:
  figure: wet_close
  drives: lit ring count on the rail, the water plane height set at the third sensor so 3 rings are lit and 1 is dark

depth:
  eye: 1.0
  horizon: 760
  cues: [OCCLUSION, AERIAL, CAST_SHADOW]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera is close at the waterline. The rail runs up through the frame, cropped by both edges, with its
    sensors stacked. The water fills the lower part with the rail's image in it. The far bank is a black line.
  bands: >
    Top third, the hook and dek beside the fourth sensor and the rail's top. Middle third, the third sensor at
    the waterline and the wake. Bottom third, the water with the rail's image and the lit rings in it.
  focal: "the third ring at the waterline, doubled in the water"

art:
  technique: "physically based macro render with mirrored reflections on opaque floodwater"
  why_this_technique: "the four sensors as rungs are the device's whole mechanism, and only a macro at the waterline shows which have been reached"
  palette: "satin aluminium, black clearcoat lenses, beacon amber rings, silt brown water, black"
  value_structure: >
    Lightest is the lamp's glint on the dry lens and the amber rings. Darkest is the sky and the water away
    from the rail. Frame median L* planned at 9.

type:
  hook: "No flood test is named"
  dek: "The release names no installation site, no city or county running it and no field test against a real flood. It gives no false alarm or missed event figure. It describes a prototype the team aims at small coastal towns. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the rail and its sensors run up through the frame with the waterline crossing it, and a frame without the rail fails this item"
  - "the rail spans at least 70 percent of the frame height"
  - "the third sensor's ring is lit in #FFA21F under the waterline and the top sensor's ring above the water is dark"
  - "the waterline crosses the rail between the third and fourth sensors"
  - "the frame's median L* at 432px is 18 or lower"

risks:
  - "rings under opaque water vanish, so the water sits at the third ring and the lower two show through their reflections and the halo light"
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: "the node standing in floodwater to its third sensor on the right, three amber rings, and up the approach a pickup stopped across the lane mid turn, the edge lines entering the water short of its bumper"
  rect: [0, 400, 1080, 950]
  bleeds: [left, right, bottom]
accent: "#FFA21F"
job: >
  Hand the reader the step that is theirs: turn around at the water.

claims: [c22]
numerals: []

data_in_art:
  figure: wet_close
  drives: lit ring count on the node's rail, the water plane height at the third sensor, the same as frame 8

depth:
  eye: 1.0
  horizon: 600
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 4.2, Z: -2}

composition:
  structure: >
    The camera stands at the waterline on the east bank looking south west up the approach. The node stands in
    the water on the right, tall. The road climbs out of the water to the right, its edge lines
    entering the water, and a pickup is stopped across the lane up the grade, turned away from the water.
  bands: >
    Top third, the hook and dek in black, the node's panel on the right. Middle third, the pickup on the
    grade on the left and the far bank. Bottom third, the water with the node's image, the lit rings and the lamp's streak.
  focal: "the pickup turned back up the grade short of the water, with the three amber rings on the right"

art:
  technique: "physically based render of the crossing, the node and the kit pickup staged together in the floodlit world"
  why_this_technique: "the next step is a driver's, and only the road, the water and a vehicle in one place make the step legible"
  palette: "silt brown water, wet asphalt, chalk edge lines, a dark grey work pickup with lit lamps, galvanized steel, three amber rings"
  value_structure: >
    Lightest is the pickup's lamps and the lamp's streak. Darkest is the sky and the banks. Frame median L* planned at 10.

type:
  hook: "Turn around at the water"
  dek: "The National Weather Service cites the CDC. Over half of flood drownings happen when a vehicle is driven into flood water. Whatever a sensor reports, the turn is the driver's. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the pickup stands on the approach turned across the lane and dry of the water, and a frame without the pickup fails this item"
  - "the node stands at least 700 px tall at full size"
  - "exactly three sensor rings are lit in #FFA21F"
  - "the edge lines enter the water between the camera and the pickup"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "a kit pickup at close range reads as a toy, so it stands nine metres or more from the camera"
```
