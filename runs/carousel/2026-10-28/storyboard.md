# Storyboard, 2026-10-28
# "The camera flags. People decide."

## The story, and what the fact check did to it

The City of Dallas runs City Detect, a computer vision tool that flags possible exterior property and right-of-way
conditions for trained staff to review (c3). The cameras ride on 50 Sanitation brush collection vehicles that already
travel Dallas neighborhoods on routine service (c5), along existing routes with no separate patrol routes (c6), two per
vehicle (c44). The city's own October 19th, 2026 briefing to the Quality of Life, Arts, and Culture Committee (c1, c2)
says an observation is not a confirmed Code violation and staff make that call (c4), that staff review every computer
generated observation before Code Compliance acts (c13), and that faces and license plates are blurred (c12).

Its results table counts 5,318 observations reviewed (c22), 2,928 courtesy notices (c23), 473 field inspections (c24),
374 voluntary corrections (c25), 34 direct abatements (c26) and 101 under formal enforcement (c27). It says success is
measured by neighborhood conditions and service delivery, not by the number of citations generated (c28). The first
letter a resident got used to be a formal notice of violation (c15). A courtesy letter is now an educational reminder
outside the citation process that sets no deadline (c16), and a courtesy notice alone never opens an enforcement case
(c17). Among its next steps it lists calibrating detection accuracy (c29) and setting performance measures around
accuracy (c30). It publishes no accuracy figure.

The December 9th, 2025 briefing (c33) proposed 100 cameras (c34) at $852,000 a year (c36), a human in the loop for all
actions (c38), and a city right to end the contract on 10 days written notice without penalty (c37).

The fact check moved four things, and every surface obeys them.
1. **The table's rows are never joined.** The briefing does not say one row is a subset of another, so the deck draws
   six rows at one scale with no arrow, no remainder and no funnel, and the copy never says one row "led to" another.
2. **FOX 4's 3,700, 57 and 34 are refused.** They relay a September 8th memo that was not fetched, from a different
   period, and FOX 4's 34 properties would be confused with the table's 34 abatements.
3. **The 32 and 68 split is refused.** The slide gives it no base.
4. **NBC 5's October reporting is out of bounds.** The crawl boundary refuses nbcdfw.com, so the blight score story is
   not on any frame.

Carousel no. 31 on September 21st covered this program through the wording of its courtesy notice. This deck is the
October 19th count and the measure the count leaves out.

## Why this treatment, and what was grafted

Director B's route is the spine. One white brush truck works one Dallas block at last light, and the stations after the
camera, the desk, the mailbox, the curb, are each a person's work. The two count frames are drawn in the brush the truck
exists to collect: cut cedar elm limbs racked in a city yard at one scale, one length of limb per item, and then the
same rack with a bare seventh arm where an accuracy row would lie. A curb relief was built first and twice failed the
audition as flat bars, so the representation changed to the rack.

Grafted from Director A: the fleet frame, fifty trucks in a yard with a hundred lit lenses, and A's refusal of FOX 4's
relayed counts and of any division into a rate. Grafted from Director C: the instrument framing, that a count is
graduations and an uncalibrated instrument is blank stock, carried in the frame 8 copy rather than a second material.
Refused from C: two relief frames of steel rules, because a third relief deck in four days would tire the panel and the
brush is this story's own material. Refused from A and C: the ember accent, which read pink on no. 41.

## The world, and the laws that hold it

**LASTLIGHT, A STAGED WORLD.** The chassis is `assets/js/deck/2026-10-28-route.js` and every frame loads it. It declares
`sky: lastLight` with the key at azimuth -125, elevation 12, the last light low in the west north west. +x is east and +z is south.
The street runs north and south, the houses stand on its east side facing west into the last light, and the camera
stands on the west side of the street looking east or north east, so the truck's driver side and the house fronts take
the key and every cast runs long to the right.

The argument for this world. The truck is white and the camera is small and dark. A near black field is where the white
cab and the camera's one cold lamp hold, and the staged pool falls only where something happens: the truck, the desk,
the mailbox, the curb where a person stands.

1. **Start dark.** Near black sky, a warm seam low in the west, pools only where something acts.
2. **Type is light, on the dark field**, and every wash only darkens.
3. **Signal cyan #7CC6D6 is the only accent** and means one thing: a computer vision observation, which the city says is
   not a confirmed violation. It is the status lamp on each camera pod (1, 2, 3, 9), the screen's tiles on 4 and the
   observations limb's tag on 5 and 7. Nothing a person decided carries it.
4. Every standing thing gets `TXT.contact`, every exterior frame `TXT.weather`, every frame `TXDECK.finish`.
5. **No livery, seal, lettering or unit number on any truck, and no condition drawn on any house.** The truck, pods and
   yard are drawn to illustrate and to no maker's design, and every frame that shows them says so.
6. **No face within 4 m.** A person is a back, a shoulder or a figure six metres off.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#08070C` | the DOM body behind the render |
| `accent` | `#7CC6D6` | the pods' lamps, the screen tiles, the observations tag |
| `hook` | `#ECE8DF` | light type on the dark |
| `dek` | `#D6D0C4` | the dek |
| `material` | `#E4E2DC` | the truck's white enamel |

The world's materials, from Dallas on the Blackland Prairie: near black clay, red orange Dallas brick and Austin chalk
trim on the ranch houses, a concrete curb and gutter, worn asphalt, cedar elm limbs with pale cut ends and small dark
leaves, a late October lawn gone half to straw, white municipal enamel with road film, worked and rust streaked steel
in the brush body, a blue boom, galvanized grapple tines, black hoses.

## The continuity devices

    CONTINUITY: CAMERA_MOVE, MOTIF_EVOLUTION, EDGE_TEASE

1. **Camera move, along one route.** From the curb beside the truck (1) up over the yard (2), in to the pod (3), into
   the reviewer's office (4), across the city yard to the limb rack (5), out to the mailbox (6), the
   inspector at the curb (7), closer on the rack (8) and back up the street as the truck leaves (9).
2. **Motif evolution, the brush.** In the grapple on 1, heaped in fifty bodies on 2, out of focus beyond the pod on 3,
   a tile on the screen on 4, cut to measure on 5, behind the mailbox on 6, at the inspector's feet on 7, racked and then absent from the seventh arm on 8, and riding away in the body on 9.
3. **Edge tease.** The curb on 6 runs off the right edge and is the curb the inspector stands on in 7.

## The rotation

    FULL_BLEED  GRID  CLOSE_CROP  CLOSE_CROP  DIAGRAM  OBJECT_AND_CAPTION  FIGURE_SCALE  DIAGRAM  FULL_BLEED

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | MEDIUM, eye 4.3 m, 9 m behind the truck's rear corner, fov 34 | the chassis brush_truck's open ribbed steel body in worked rust streaked plate, loaded with instanced cut limbs and leaf cards, the blue knuckle boom reaching forward, both camera pods on its front corners with lamps lit, raked by the low key from the camera's left, grime low on its walls |
| 02 | AERIAL, eye 34 m, 40 m south of the yard, fov 28 | fifty brush_trucks instanced per mesh in five rows of ten on worn concrete, each pod lamp lit, the front row cut by the bottom edge, the yard's apron lights making one pool |
| 03 | CLOSE, eye 3.3 m, 0.7 m off the near pod, fov 30 | the chassis camera_pod at detail, a clearcoat dark housing with visor, coated lens and status lamp on its bracket off the body's top rail, the worked steel of the body corner beneath, the street beyond in depth |
| 04 | CLOSE, eye 1.25 m behind a desk, fov 40 | a kit monitor whose emissive screen carries 5,318 tiles, the room's one source, on a kit desk lit cold by the screen, in a TXT.interior room dark around the screen |
| 05 | CLOSE, eye 1.75 m, 15.5 m square on to the rack, fov 40 | the chassis limb_rack, galvanized steel dulled by weather, raked by the low key from the camera's left, contact shadows on the yard concrete, grime low on its columns, six arms projecting toward the camera, and six chassis cut_limb models in barked cedar elm with ringed pale cut ends lying on the arms at one scale, the 5,318 limb crossing the frame, the fence and yard concrete in the key's pool |
| 06 | MEDIUM, eye 1.2 m, 2.6 m off the mailbox, fov 38 | the kit mailbox, a red orange brick column with mortar joints and a black steel box with its door open, lit from the left, contact on the lawn, grime at its base, the chassis notice_letter pale inside, the curb running off the right edge |
| 07 | WIDE, eye 1.6 m, 17 m off the truck, fov 40 | the brush_truck parked with its boom stowed, a kit person in a vest on the sidewalk at the truck's front, turned toward the windrow, a ranch house behind them |
| 08 | MACRO, eye 1.0 m, 7.6 m off the first upright, fov 40 | the frame 5 rack's first upright at the right edge, galvanized steel raked by the key, a seventh arm bare and lit with a blank stock tag, contact and shadow on the yard concrete, the six limbs running off the right edge above |
| 09 | WIDE, eye 1.5 m, from the street's centre line, fov 34 | the brush_truck 45 m down the street, white enamel and worked steel caught by the last of the key, contact on the asphalt, road film low on its body, its tail lamps and pod lamps the last lights before the seam, the inspector small at the curb |

Showstopper frame: 01, the loaded truck body large in a pool, its depth made by the body walls converging forward, the boom occluding the street and the two cold lamps on the pods.
Tonal arc: the lit truck on near black on 01, the yard's pool on 02, the pod's dark shell on 03, the screen's glow on 04,
the rack in the yard's pool on 05, the mailbox in its pool on 06, the inspector's pool on 07, the bare arm on 08, and
the deck's darkest on 09 where only the lamps carry light.
VALUE CUT: frame 8. The deck turns from what was counted to what was not, and the bare arm is that turn.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "the brush truck's loaded body seen from above its rear corner, the blue knuckle boom reaching forward, both camera pods lit cold on the body's corners"
  rect: [0, 640, 1080, 580]
  bleeds: [left, right]
accent: "#7CC6D6"
job: >
  Put the reader at the curb beside the machine before a word of the count: a city truck everybody has seen, carrying
  a camera nobody looks at.

claims: [c2, c5, c6, c41, c44]
numerals:
  - value_from: c5
  - value_from: c2

data_in_art:
  figure: pile_len_m
  drives: the length of the curbside brush windrow, a ten cubic yard pickup solved to a half ellipse section in compute.py

depth:
  eye: 4.3
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: -1.9, Z: 0}

composition:
  structure: >
    A camera raised behind the truck's rear corner, looking forward along the open body, so the load of cut limbs,
    the body's ribbed walls and the boom read as one machine filling the lower half and bleeding off the bottom and
    right. The two camera pods sit on the body's front corners, one each side, both lamps lit. The street beyond is dark.
  bands: >
    Top third, the dark sky with the hook and the dek. Middle third, the boom, the body's top rails and the two pods
    with their lamps.
    Bottom third, the load of barked cedar elm limbs with pale cut ends lit by the key, leaves among them, and the ribbed worked steel walls of the body with their rust streaks and shadow.
  focal: "the two pods' cold lamps over the lit load, the pair the hook names"

art:
  technique: "physically based render of the chassis brush_truck, kit road, ranch_house, cedar_elm and a chassis brush windrow in the lastLight world, staged on the truck"
  why_this_technique: "a modelled truck lit at the curb reads as a real city truck working a real block, which is what the claim is about"
  palette: "white enamel, worked rust streaked steel, city blue boom, cedar elm bark, asphalt, brick going dark"
  value_structure: >
    Lightest is the lit limb ends and the pod lamps. Darkest is the sky and the street behind. Frame median L* planned at 4.

type:
  hook: "Cameras ride 50 brush trucks"
  dek: "The trucks already run routine Sanitation routes, the city's October 19th briefing says. An April city memo planned two cameras per truck. The truck is drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the brush truck's ribbed body, its load of limbs and the blue boom are all visible and modelled"
  - "the truck spans at least 70 percent of the frame width at 432px"
  - "two camera pods are visible on the body's corners with their cyan lamps lit"
  - "the load of limbs reads as cut wood with bark and pale ends"
  - "the hook and dek sit on dark sky and no part of the truck crosses their glyphs"
  - "no lettering, seal or unit number appears on the truck"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "a load of limbs seen from above can read as toy blocks, so each limb is barked, bent and cut with ringed ends and the leaves stay small"
```

```yaml
slide: 2
layout: GRID
primary_image:
  subject: "fifty brush trucks in five rows of ten in a dark yard from above, a hundred cold pod lamps lit"
  rect: [0, 0, 1080, 1350]
  bleeds: [left, right, bottom]
accent: "#7CC6D6"
job: >
  Show the scale the city set: one truck is fifty trucks, and two cameras are a hundred lit lenses.

claims: [c5, c33, c36, c38, c44, c34]
numerals:
  - value_from: c5
  - computed_by: "out/2026-10-28/compute.py, trucks times cameras per truck"
  - value_from: c36

data_in_art:
  figure: trucks
  drives: the number of trucks instanced in the yard, five rows of ten, and cameras_fleet sets the number of lit pod lamps

depth:
  eye: 34
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, TEXTURE_GRADIENT, AERIAL]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A high camera south of the yard looking north, so the five rows recede and shrink and the front row is cut by the
    bottom edge. The rows are one subject, a fleet, lit in one pool, with the lamps as a field of points.
  bands: >
    Top third, dark sky with the hook and the dek. Middle third, the far rows shrinking into the dark. Bottom third, the
    near rows large with their white cabs and lit lamps, cut by the bottom edge.
  focal: "the near rows of white cabs and the grid of lit lamps"

art:
  technique: "physically based render of fifty chassis brush_trucks instanced per mesh on a worn concrete TXT.ground in the lastLight world"
  why_this_technique: "fifty real trucks counted out in rows make the figure a thing the eye can count rather than a numeral"
  palette: "white enamel, worked steel, worn concrete, sodium apron light, the cold lamps"
  value_structure: >
    Lightest is the near cabs' roofs and hoods. Darkest is the sky and the yard beyond the rows. Frame median L* planned at 13.

type:
  hook: "50 trucks, 100 cameras planned"
  dek: "The December 2025 plan priced the system at $852,000 a year for 100 cameras, with a human in the loop for all actions. The yard is drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the near row of trucks stands at least 120 px tall at 432px"
  - "fifty trucks are visible in five rows of ten, the front row cut by the bottom edge"
  - "pod lamps read as a field of cold points over the rows"
  - "the rows recede in perspective and the far row is smaller than the near row"
  - "the hook and dek sit on dark sky"
  - "no lettering on any truck"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "fifty trucks may exceed the render budget, so each mesh is one InstancedMesh with fifty instances"
```

```yaml
slide: 3
layout: CLOSE_CROP
primary_image:
  subject: "the camera pod close on the body's top rail, cropped by the right edge, its lens and cold lamp, the street beyond in depth"
  rect: [370, 570, 710, 630]
  bleeds: [right]
accent: "#7CC6D6"
job: >
  Name the machine for what the city says it is: a flag for trained staff, never a confirmed violation.

claims: [c3, c4, c6, c12]
numerals: []

data_in_art:
  figure: cameras_per_truck
  drives: the number of camera pods modelled on the body, one per side, the near one drawn at detail

depth:
  eye: 3.3
  horizon: 820
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, OCCLUSION, CAST_SHADOW, AERIAL]
  subject_at: {X: 1.24, Z: -0.35}

composition:
  structure: >
    The camera sits just behind and above the near pod, so the pod is large on the right with its lens turned toward the
    curb and the street falls away beyond it.
  bands: >
    Top third, dark sky with the hook and dek. Middle third, the pod, its visor and lens and the body's top rail. Bottom third, the ribbed body side in dented, rust streaked steel catching the key on each rib, and below it the street with the windrow's bark and the curb in soft depth.
  focal: "the pod's dark shell and lens rim catching the key, with the cold lamp beside the lens"

art:
  technique: "physically based close render of the chassis camera_pod on the brush_truck in the lastLight world"
  why_this_technique: "a real lens on a real bracket at true scale shows how small and how ordinary the instrument is"
  palette: "dark powder coat, coated glass, worked steel, cold lamp"
  value_structure: >
    Lightest is the lit rim of the body's top rail and the pod's lit edge. Darkest is the sky and the lens. Frame median L* planned at 3.

type:
  hook: "The camera flags. Staff decide, the city says."
  dek: "City Detect flags possible conditions along the route for trained staff to review. The city says an observation is not a confirmed Code violation, and faces and license plates are blurred."
  labels: []

verbatim: []

acceptance:
  - "the near pod's housing, visor, lens and cyan lamp are visible and the pod is at least 180 px wide at 432px scale times 2.5"
  - "the main lens carries the cyan coating and the status lamp beside it is lit"
  - "the body's top rail and ribbed side are visible below the pod"
  - "the hook and dek sit on dark sky"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "a dark pod on a dark sky vanishes, so the pod is set against the lit body side and the key rims its top"
```

```yaml
slide: 4
layout: CLOSE_CROP
primary_image:
  subject: "a reviewer's monitor close on a desk in a dark office, its screen a field of 5,318 small tiles"
  rect: [260, 560, 820, 790]
  bleeds: [right, bottom]
accent: "#7CC6D6"
job: >
  Show the first person after the camera, and the size of the pile they work through, one tile per observation reviewed.

claims: [c13, c22]
numerals:
  - value_from: c22

data_in_art:
  figure: observations
  drives: the number of tiles drawn on the monitor's screen, one per observation reviewed

depth:
  eye: 1.25
  horizon: 700
  cues: [LINEAR_PERSPECTIVE, OCCLUSION, CAST_SHADOW, RELATIVE_SIZE]
  subject_at: {X: 0.2, Z: -0.4}

composition:
  structure: >
    The camera stands in the reviewer's seat, so the monitor fills the middle of the frame and the screen's field of
    tiles is the image. The screen is the room's one source and throws its cold light down the desk.
  bands: >
    Top third, the dark wall with the hook and dek. Middle third, the monitor and its tiled screen.
    Bottom third, the desk's wood grain lit cold by the screen, the stand's base and its contact shadow.
  focal: "the screen's tiled field, the brightest area in the frame"

art:
  technique: "physically based render in a TXT.interior room, kit monitor and desk, the screen an emissive canvas texture of tiles"
  why_this_technique: "a real screen carrying one mark per observation makes the count a pile of work a person faces"
  palette: "cold screen light, dark laminate, paper, a dark office"
  value_structure: >
    Lightest is the screen. Darkest is the room around it. Frame median L* planned at 5.

type:
  hook: "5,318 observations, each one reviewed"
  dek: "The city's results table counts 5,318 observations reviewed. Staff review every one before Code Compliance acts, the briefing says. One tile here stands for one observation, drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the monitor owns at least a third of the frame width at 432px"
  - "the monitor's screen carries a dense field of small tiles"
  - "the screen sits inside the bezel with an even border and its tiles are the brightest area in the frame"
  - "the desk and paper are lit by the screen"
  - "the hook and dek sit on the dark wall"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "a screen of tiles can read as a UI screenshot, so the monitor's bezel, stand and the desk carry the frame"
```

```yaml
slide: 5
layout: DIAGRAM
primary_image:
  subject: "a galvanized cantilever rack in a city yard, six cut cedar elm limbs racked on its arms at one scale, one length of limb per item"
  rect: [0, 560, 1080, 660]
  bleeds: [left, right]
accent: "#7CC6D6"
job: >
  Lay the city's own six counts side by side at one scale, in the brush the truck collects, so the reader sees 5,318
  against 101 before reading a number.

claims: [c2, c22, c23, c24, c25, c26, c27]
numerals:
  - value_from: c22
  - value_from: c23
  - value_from: c24
  - value_from: c25
  - value_from: c26
  - value_from: c27

data_in_art:
  figure: observations_m
  drives: the length of each limb in metres, every row at 8.4 m over 5,318 per item

depth:
  eye: 1.75
  horizon: 980
  cues: [LINEAR_PERSPECTIVE, CAST_SHADOW, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: 4.2}

composition:
  structure: >
    The rack faces the camera square on across a city yard, with the chain link fence behind it. Six limbs lie on its
    arms in the table's own order from the top arm down, each butt on the first upright's line, so their lengths are
    the counts. Each label sits just above its own limb's butt.
  bands: >
    Top third, the hook and dek over the dark sky. Middle third, the top arm's 5,318 limb running across the frame past
    the second upright and the 2,928 limb at a little over half.
    Bottom third, the four short limbs as barked stubs with pale ringed cut ends lit on their galvanized arms, the uprights' columns casting long shadows onto the yard's worn concrete, and the chain link fence catching the key.
  focal: "the 5,318 limb running most of the frame's width beside the 2,928 limb at a little over half"

art:
  technique: "physically based render of the chassis limb_rack and cut_limb models in the lastLight world, a yard staged in one pool"
  why_this_technique: "real limbs racked at one scale make each count a physical length a city crew would stack, never a bar"
  palette: "galvanized steel, cedar elm bark, pale cut ends, yard concrete, a dark sky"
  value_structure: >
    Lightest is the galvanized uprights and the cut ends. Darkest is the sky and the yard outside the pool. Frame median L* planned at 1.

type:
  hook: "What the city counted"
  dek: "Six rows of the October 19th results table at one scale, one length of limb per item. The table doesn't say one row comes out of another."
  labels: ["OBSERVATIONS REVIEWED 5,318", "COURTESY NOTICES 2,928", "FIELD INSPECTIONS 473", "VOLUNTARY CORRECTIONS 374", "DIRECT ABATEMENTS 34", "FORMAL ENFORCEMENT 101"]

verbatim: []

acceptance:
  - "the 5,318 limb runs at least 340 px of the 432px frame width"
  - "six limbs lie on the rack's arms, each butt on the first upright's line"
  - "the 5,318 limb is at least 1.7 times the 2,928 limb at 432px"
  - "the limbs and uprights cast onto the yard and read as solid objects in depth"
  - "each label sits at its own limb's end and none crosses a limb"
  - "no arrow or connector joins the rows"
  - "the frame's median L* at 432px is 26 or lower"

risks:
  - "a rack seen square on can flatten into a bar chart, so the arms project toward the camera, the uprights cast and the fence and yard carry the depth"
```

```yaml
slide: 6
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "a brick mailbox at the curb with its door open and a folded letter inside, the curb running off the right edge"
  rect: [180, 560, 900, 790]
  bleeds: [right, bottom]
accent: none
job: >
  Show what a resident actually gets now: a letter that sets no deadline, where the first letter used to be a notice of
  violation.

claims: [c15, c16, c23]
numerals:
  - value_from: c23

data_in_art:
  figure: pile_len_m
  drives: the length of the brush windrow at the curb beside the mailbox

depth:
  eye: 1.2
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The mailbox stands left of centre and large, its door open toward the camera with the folded letter inside, lit by
    the key from the left. The curb runs from it off the right edge, and a windrow and a dark house sit behind.
  bands: >
    Top third, dark sky with the hook and dek. Middle third, the mailbox's brick column, its box and open door. Bottom third, the mailbox's brick base with its mortar joints and contact shadow, the half straw lawn in blades, and the concrete curb with its lit lip running off the right edge.
  focal: "the open mailbox door and the pale letter inside"

art:
  technique: "physically based render of the kit mailbox and the chassis notice_letter at the curb in the lastLight world"
  why_this_technique: "a real letter in a real mailbox is where the city's change of wording reaches a household"
  palette: "red orange brick, black steel box, pale paper, lawn straw"
  value_structure: >
    Lightest is the letter and the lit brick face. Darkest is the house and sky. Frame median L* planned at 6.

type:
  hook: "A courtesy letter sets no deadline"
  dek: "The table counts 2,928 courtesy notices. A courtesy letter is now an educational reminder outside the citation process, the briefing says. The first letter used to be a formal notice of violation."
  labels: []

verbatim: []

acceptance:
  - "the mailbox stands at least 150 px tall at 432px"
  - "the kit mailbox with a brick column is visible with its door open"
  - "a folded pale letter is visible inside the box with no legible text"
  - "the curb runs off the right edge"
  - "the hook and dek sit on dark sky"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "the letter can vanish in the box's shadow, so the box's mouth faces the key"
```

```yaml
slide: 7
layout: FIGURE_SCALE
primary_image:
  subject: "the brush truck parked at the curb with its boom stowed, a person in a vest standing on the sidewalk at the truck's front, turned away toward the windrow"
  rect: [0, 620, 1080, 600]
  bleeds: [left, right]
accent: "#7CC6D6"
job: >
  Show the step a camera can't take: a person walks to the curb and decides on site whether a violation exists.

claims: [c18, c19, c24, c25]
numerals:
  - value_from: c24
  - value_from: c25

data_in_art:
  figure: pile_len_m
  drives: the length of the brush windrow at the inspector's feet

depth:
  eye: 1.6
  horizon: 720
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 6, Z: -2}

composition:
  structure: >
    A standing camera on the sidewalk side of the street. The inspector stands at the curb on the left third, turned
    three quarters away toward the windrow, small against the parked truck that fills the middle and right. The truck's scale
    against the person is the frame.
  bands: >
    Top third, dark sky with the hook and dek. Middle third, the truck's cab, body and the inspector's head and shoulders
    against it. Bottom third, the curb's lit lip, the windrow's bark and leaves at the inspector's feet, the lawn in blades and the truck's tyres with their casts on the asphalt.
  focal: "the inspector's lit figure against the white truck"

art:
  technique: "physically based render of the brush_truck, a kit person, kit ranch house and lawn in the lastLight world"
  why_this_technique: "a real person at true scale beside the real truck makes the human step physical"
  palette: "white enamel, a hi vis vest gone dull in the dusk, lawn straw, brick"
  value_structure: >
    Lightest is the truck's lit side. Darkest is the house and sky. Frame median L* planned at 4.

type:
  hook: "A person walks to the curb"
  dek: "In a prioritized inspection a Code Inspector checks on site whether a violation exists. The table counts 473 field inspections and 374 voluntary corrections."
  labels: []

verbatim: []

acceptance:
  - "the parked truck stands at least 110 px tall at 432px"
  - "a person stands fully in frame on the sidewalk near the truck's front, feet and contact shadow visible, with no face visible"
  - "the parked truck with its boom stowed fills the middle and right"
  - "the person reads at two thirds to four fifths of the truck's height, standing on the sidewalk a little nearer the camera than the truck"
  - "the hook and dek sit on dark sky"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "the kit person reads as a mannequin close up, so the figure stands at the truck's depth, about 15 m off, and turned away"
```

```yaml
slide: 8
layout: DIAGRAM
primary_image:
  subject: "the frame 5 rack's first upright at the right edge, its six limbs running off above and the seventh arm bare with a blank tag, labelled for accuracy"
  rect: [500, 520, 580, 760]
  bleeds: [right]
accent: "#7CC6D6"
job: >
  Make the measure the briefing leaves out a thing the reader can see is absent, without accusing anyone: the row for
  accuracy holds nothing.

claims: [c2, c29, c30, c22, c23, c24, c25, c26, c27]
numerals: []

data_in_art:
  figure: observations_m
  drives: the six limb lengths at the frame 5 scale above the empty seventh arm

depth:
  eye: 1.0
  horizon: 1000
  cues: [LINEAR_PERSPECTIVE, CAST_SHADOW, OCCLUSION, FORM_SHADING]
  subject_at: {X: -0.6, Z: 0}

composition:
  structure: >
    The same rack and the same light as frame 5, seen low and close from the side of its first upright, which stands at
    the right edge with a seventh arm added at the bottom. The six racked limbs run off the right edge above, and the
    seventh arm projects bare toward the reader with a blank stock tag on it and the accuracy label beside it. The dark
    yard and fence fill the left, the breath before the close.
  bands: >
    Top third, the hook and dek over the dark sky, the upright's top at the right edge. Middle third, the limbs' butts on
    their arms at the right edge and the dark fence.
    Bottom third, the bare seventh arm in galvanized steel lit by the key with the blank tag hanging from it, its shadow on the yard's concrete, a made place with nothing racked on it.
  focal: "the bare seventh arm and its blank tag, the brightest thing low in the frame"

art:
  technique: "physically based render of the frame 5 rack and limbs in the lastLight world, one arm added and left bare"
  why_this_technique: "the same rack at the same scale makes the bare arm read as a measured nothing rather than a hole in the drawing"
  palette: "galvanized steel, cedar elm bark, pale cut ends, yard concrete, a dark sky"
  value_structure: >
    Lightest is the galvanized uprights and the bare arm. Darkest is the sky and the yard outside the pool. Frame median L* planned at 1.

type:
  hook: "Accuracy is still a next step"
  dek: "The October 19th briefing lists calibrating detection accuracy and setting accuracy measures as next steps. It publishes no accuracy figure, so the lowest arm holds no limb and its tag is blank."
  labels: ["ACCURACY, NO FIGURE IN THE BRIEFING"]

verbatim: []

acceptance:
  - "the rack's first upright stands at least 220 px tall at 432px"
  - "the bare seventh arm is visible below the limbs on the first upright with the blank tag hanging from it"
  - "the six racked limbs run off the right edge above the bare arm and no part of the rack crosses the hook or dek"
  - "the seventh arm holds no limb"
  - "the accuracy label sits beside the bare arm"
  - "the frame's median L* at 432px is 26 or lower"

risks:
  - "an empty arm can read as a render fault, so the same galvanized arm, its key light and the label make it a made place"
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: "the brush truck leaving down a dark street, its tail lamps and two cold pod lamps the last lights before the seam, the inspector small at the curb"
  rect: [0, 600, 1080, 750]
  bleeds: [left, right, bottom]
accent: "#7CC6D6"
job: >
  Close on the consequence: the truck goes on to the next block and the decisions stay with people, at a cost the city
  can end on short notice.

claims: [c1, c2, c28, c32, c33, c36, c37]
numerals:
  - value_from: c36
  - value_from: c37

data_in_art:
  figure: cameras_per_truck
  drives: the number of lit pod lamps on the leaving truck

depth:
  eye: 1.5
  horizon: 740
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: -45}

composition:
  structure: >
    A camera on the street's centre line looking north up the street. The truck is 45 m off, small and dark with its
    lamps lit, the curb and houses converging toward it, the inspector a small lit figure at the right curb in the middle
    distance, the windrow gone.
  bands: >
    Top third, dark sky with the hook and dek. Middle third, the street converging to the truck and its lamps. Bottom third, the worn asphalt with its joints and stains in the streetlight's pool, both concrete curbs converging with lit lips, and the near lawn edges in blades.
  focal: "the truck's lamps at the street's vanishing point"

art:
  technique: "physically based render of the brush_truck, kit road, ranch houses, streetlight and person in the lastLight world"
  why_this_technique: "a street that converges on a leaving truck closes the route the deck followed"
  palette: "asphalt, brick, the tail lamps, the cold lamps, one streetlight"
  value_structure: >
    Lightest is the lamps and the inspector's pool. Darkest is the sky and the street's far reaches. Frame median L* planned at 3.

type:
  hook: "People make the decisions, the city says"
  dek: "The October 19th briefing to the Quality of Life, Arts, and Culture Committee says success is not measured by citations. The December 2025 plan proposed $852,000 a year on a contract the city could end with 10 days written notice. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the leaving truck with its lamps stands at least 20 px tall at 432px"
  - "the truck is visible down the street with red tail lamps and two cyan pod lamps lit"
  - "the inspector is visible small at the right curb with no face"
  - "the curbs converge toward the truck"
  - "the hook and dek sit on dark sky"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "a small truck at 45 m can read as nothing, so its lamps and the streetlight pool carry it"
```
