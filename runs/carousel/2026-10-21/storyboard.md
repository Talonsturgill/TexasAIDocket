# Storyboard, 2026-10-21
# "A 24 machine cell, due in 2027"

## The story, and what the fact check did to it

Lockheed Martin announced on October 14th, 2026 that it is investing $300 million in its Grand Prairie
operation and expanding the manufacturing footprint to more than 735,000 square feet, with 100,000 square feet
of new space and 85,000 of office space turned over to manufacturing (c1, c2, c6). Hadrian will bring a highly
automated machining cell of 24 machines to the plant, operated by Lockheed's own production workforce and
expected to be operational in early 2027 (c3, c4). The plant supports PAC-3 MSE, THAAD, PrSM and JATM (c7) and
already holds hundreds of machining assets (c14). In a few months it added more than 30 high precision machines
(c10) and expects nearly 100 new machines by the end of 2026 (c11). Nearly 800 production employees made 250,000
parts there in 2025 (c12). Hadrian describes its own factories as combining process engineering, AI and robotics
(c15), and says its software Opus interprets legacy designs and automates manufacturing and inspection (c20, c21).
A state filing places the plant in Dallas County (c34). The record carries it as tx-2026-0225.

**WHAT THE FACT CHECK CHANGED.**
- **The cell is not running.** Every surface says expected to be operational in early 2027 (c4). The more than 30
  machines producing components are Lockheed's own (c10), never the cell.
- **No source says what AI does inside this cell.** The AI words are Hadrian's description of its own factories
  (c15, c20, c21). Nothing ties Opus to Grand Prairie, and the deck says so in its turn.
- **The 2,000 Texas jobs are the company's own figure and are statewide** (c5), never Grand Prairie's, never set
  against the nearly 800.
- **Whether the 24 count toward the nearly 100 is not stated.** The two sets are drawn apart and never nested.
- **Dallas County comes from the TDLR filing** (c34), never from the release.
- **No missile is drawn.** The plant makes parts and the deck draws a generic part.

## Why this treatment, and what was grafted

Three directors pitched THE MEASURE (count the plant in its own units, a part, a machine and a person at one
scale, the cell the one count that hasn't cut a part), THE CELL (one hall at night, the cell's 24 bays still
tape on the floor) and THE UNSAID (what the release establishes stands lit, what it leaves open carries a tag).

- **From THE MEASURE, the spine and the unit.** One illustrative part in three states: finished in the cover's
  vise, multiplied to one production employee's share in foam (3), and raw in the cell (9 has none at all). The
  plan reliefs at one scale for the areas (2), the nearly 100 machines (5) and the same bench with the cell
  beside them (6). The world, lastLight with the key low in the west, and the comal lit accent for Hadrian only.
- **From THE CELL, the honest image of the cell.** The 24 are drawn as empty taped bays, a plan drawn as a plan,
  rather than as idle machines nobody has said have arrived. On 6 in plan and on 9 at standing eye.
- **From THE UNSAID, the turn.** The pendant at close range with its screen black, the frame on which the deck says
  the release never says what the AI does here (8).
- **Refused.** The aerial of the plant (it would invent a roof plan for a real building). The training card and
  the truck court (each needed a figure the release doesn't give). The manila tag (a second motif would compete
  with the accent). A missile, a logo, the real building.
- **The accent.** Comal lit #8FE0F0, brand.yaml's, and it means ONE thing: Hadrian's cell. The tab on Hadrian's
  page (7), the 24 taped bays (6, 9). Three frames. Lockheed's machines carry warm neutral light only.

## The world, and the laws that hold it

**LASTLIGHT, A MACHINE SHOP AT SHIFT CHANGE.** The chassis is `assets/js/deck/2026-10-21-cell.js` and every frame
loads it. It declares `sky: lastLight` with the key at azimuth -64, elevation 9: the sun just down, one low warm
key entering the plant's west doors and windows, the plant behind every subject gone dark. A material relief
reads the same light from the left of its frame and every cast runs long to the right. +x is east and +z south.

The argument for this world: machined aluminium only reads under a raking key, and the low sun through a west
door at shift change is the one light that rakes every machined face and pocket wall. The last three worlds were
floodlit interiors, lastLight brush country exteriors and a darkfield bench, and none was a machine shop.

1. **Start dark.** Graphite enclosures, a near black epoxy floor, the pool where the subject stands.
2. **Type is light, on the dark field**, and every wash only darkens.
3. **Comal lit is the only accent** and means Hadrian's cell.
4. Every standing thing gets `TXT.contact`, every spatial frame `TXT.weather`.
5. **No missile, no logo, no real building.** Every frame says drawn to illustrate.
6. **The cell is never drawn running.** It is taped bays.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#08060F` | the DOM body behind the render |
| `accent` | `#8FE0F0` | comal lit, Hadrian's cell: 6, 7, 9 |
| `hook` | `#ECE6DA` | light type on the dark |
| `dek` | `#D8CFC0` | the dek |
| `material` | `#C9CDD1` | machined 6061, the part, the vise jaws |

The world's materials: graphite enamel #35383D over a charcoal plinth, a pale grey fascia band, brushed stainless
jambs and way covers, cast iron tables #4A4D50, bright anisotropic 6061 #D3D7DB, a near black epoxy floor #15181B,
the old slab, a fresh pour, charcoal carpet tile, black kitting foam, black granite, a cyanotype sheet #1D3A5F with
white line, a warm 2700 K key and one cold accent.

## The continuity devices

    CONTINUITY: CAMERA_MOVE, MOTIF_EVOLUTION, VALUE_ARC

1. **Camera move through one plant.** Through the open door at the vise (1), straight down on the floor at one
   scale (2), down onto a tray on the bench (3), standing in the converted room (4), straight down on the floor
   again held still across 5 and 6, down onto Hadrian's page (7), at the pendant (8), and standing at the edge of
   the cell's empty bays (9).
2. **Motif evolution, the part.** Finished and wet in the vise (1), multiplied in foam with one lifted (3), in the
   vises of the added machines (4), drawn as its own plan view on Hadrian's page (7), and absent from the cell (9).
   The accent is the second motif: it first appears on 6 and only marks the cell.
3. **Value arc.** The cover's lit vise in a dark machine, the reliefs dark with raked edges, the converted room's
   window light the warmest frame, then the pendant and the cell darkening to the close, one pool and a cold
   outline.

## The rotation

    CLOSE_CROP  DIAGRAM  OBJECT_AND_CAPTION  FIGURE_SCALE  DIAGRAM  DIAGRAM  DOCUMENT  CLOSE_CROP  FULL_BLEED

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | MACRO, eye 1.27 m, 0.75 m from the vise through the open door, fov 30 | the chassis machining_centre's work zone at full detail: the cast iron T-slot table, the machine_vise with hardened jaws, the finished housing_part in bright anisotropic 6061 with two real pockets and counterbored bosses, the spindle nose, a lathed holder and the end mill held clear, two segmented coolant hoses, aluminium chips, the stainless jamb and a door leaf slid back, lit by the low key through the door with the work light on behind |
| 02 | AERIAL, an orthographic plan relief of floor finishes | three squares at one scale, modelled as a TXBENCH relief in three materials under the low key with long casts and weathered saw joints: sealed old slab for more than 735,000 square feet, a fresh pour of 100,000 inside it with timber form boards on two edges, and 85,000 of charcoal carpet tile with one corner rolled back to bare slab, each with saw joints or tile seams as cavities and casts long to the right |
| 03 | CLOSE, an orthographic plan relief of a kitting tray | a black foam tray, modelled as a TXBENCH relief of matte foam and bright 6061 under the low key, each part in contact with its pocket floor and the foam worn at the edges, cut with 312 pockets in rows of 24, each holding the part in plan with its two pockets and four bosses, one pocket empty and that part lying on the steel bench beside the tray, every part casting into its pocket |
| 04 | WIDE, eye 1.6 m, 7 m back, fov 34, inside a converted office | the near machining_centre at full detail with its door shut, its window lit, the finished part in the vise, a kit person cropped at the shoulder at the pendant, then 30 machining_centre at low detail in two rows receding into the dark, the west windows laying parallelograms of last light across the floor |
| 05 | AERIAL, an orthographic plan relief of the shop floor | 100 machining_centre roofs in ten rows of ten, each the model's own plan: the enclosure roof, the column cap, the tool drum hood on its west side, the chip cart behind, the pendant arm and a stack pole whose long cast runs down the aisle |
| 06 | AERIAL, the same plan and light as 05 | the same 100 roofs, and across one empty aisle 24 empty bays in six rows of four, each a satin epoxy pad in a comal lit tape outline with four levelling plates, at the same scale |
| 07 | CLOSE, an orthographic plan relief of a page on a granite plate | a cyanotype engineering sheet of the part, three orthographic views in white line with leaders and no numerals, a blank title block with a comal lit tab, curled at one corner, lying on a black granite plate with the finished part standing on its own plan view and casting onto the sheet |
| 08 | CLOSE, eye 1.45 m, 0.55 m from the pendant, fov 36 | the machining_centre's control pendant on its swing arm: a bevelled pale housing, the black coated screen dark and reflecting nothing but the seam, four rows of keys, a knob and a handwheel, the shut door's window and graphite enclosure behind it falling to black |
| 09 | WIDE, eye 1.4 m, at the near corner of the bays, fov 34 | the near empty machine_bay, its satin epoxy pad over concrete tooth, comal lit tape, levelling plates with anchor bolts and the drop cord, the rest of the 24 receding in rows, a kit person three quarter away two bays back lit from the camera side, and four of Lockheed's machines far off on the right with their windows lit |

Showstopper frame: 01, the finished part in the vise through the open door, the low key raking every pocket wall and the chips, the machine around it black
Tonal arc: the lit vise in a black machine on 1, the dark floor reliefs of 2 and 3 with bright raked edges, the warmest frame on 4 with window light, the floor reliefs of 5 and 6 dark with one cold block, the page on 7, the black screen on 8 the darkest close, the empty bays on 9 one pool and a cold outline
VALUE CUT: frame 6. The deck turns from what the plant already does to what Hadrian's cell has not yet done, and the empty taped block beside the 100 is that turn.

---

```yaml
slide: 1
layout: CLOSE_CROP
primary_image:
  subject: "the work zone of a vertical machining centre seen through its open door: a finished aluminium part in the vise on the T-slot table, the end mill held clear above it, chips and coolant hoses"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: none
job: >
  Put the thing the plant makes in front of the reader, a machined part in a machine, and say the story, Hadrian's 24 machine cell is coming to Grand Prairie and is due in 2027.

claims: [c3, c4, c7, c34]
numerals:
  - value_from: cell_machines
  - value_from: cell_year

depth:
  eye: 1.27
  horizon: 430
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0.8}

composition:
  structure: >
    The camera stands in the open door at table height and looks down into the work zone. The part in its vise is
    the lit subject in the lower middle, the end mill comes down from above it, the jamb and a slid door leaf
    frame the left, and the enclosure's dark ceiling holds the type.
  bands: >
    Top third, the machine's dark interior ceiling and the work light, under the hook. Middle third, the dek, the
    spindle nose and the end mill. Bottom third, the vise and the part with its two pockets lit by the low key and holding shadow, the table's T-slots, chips catching light and the coolant hoses in shadow.
  focal: "the part's lit top face and its two pockets, the brightest area"

art:
  technique: "physically based render of the chassis machining_centre at full detail inside a TXT.interior shop, staged in the lastLight world"
  why_this_technique: "a part in a vise is what a machining cell is for, and a reader sees the work before any number"
  palette: "bright anisotropic 6061, cast iron, graphite enamel, black rubber, a warm low key"
  value_structure: >
    Lightest are the part's top faces, the jaw edges and the chips. Darkest are the enclosure ceiling and the
    pockets. Frame median L* planned at 9.

type:
  hook: "A 24 machine cell, expected in early 2027"
  dek: "Lockheed Martin says Hadrian will bring a highly automated machining cell to its Grand Prairie missile plant, run by Lockheed's own workforce. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the machining_centre work zone spans at least 700 px of the frame width at full size"
  - "the machining_centre work zone is modelled: the vise, the T-slot table and the spindle with its end mill are all in frame, and a frame missing any fails"
  - "the part spans at least 220 px of the frame width at full size, and a frame with no part fails this item"
  - "both pockets of the part read as openings with shadow at 432 px"
  - "the end mill is above the part and does not touch it"
  - "no missile, no logo and no screen output in frame"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "the machine interior can read as a grey box, so it carries a stainless jamb, T-slots, way covers and chips"
```

```yaml
slide: 2
layout: DIAGRAM
primary_image:
  subject: "three floor finishes as squares at one scale: old sealed slab for more than 735,000 square feet, a fresh pour of 100,000 inside it and 85,000 of carpet tile with a corner rolled back"
  rect: [200, 660, 820, 690]
  bleeds: [bottom]
accent: none
job: >
  Show the size of the expansion in one measured picture, the footprint and the two areas changing inside it, at one scale.

claims: [c1, c2]
numerals:
  - value_from: invest_m
  - value_from: footprint_sqft
  - value_from: new_sqft
  - value_from: office_sqft

data_in_art:
  figure: footprint_sqft
  drives: the side length of each square, the square root of its area at one scale (footprint_sqft, new_sqft, office_sqft)

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The big slab square fills the lower two thirds and bleeds off the bottom. The new pour and the carpet tile sit
    inside it as two smaller squares side by side, the pour with form boards proud and the carpet with a rolled
    corner, so their relative size reads before any number. Three DOM labels sit beside them.
  bands: >
    Top third, the dark floor beyond the slab with the hook and dek. Middle third, the two small squares and their
    labels. Bottom third, the slab's relief, its saw joints as cavities in shadow and its texture raked by the low light, running off the bottom edge.
  focal: "the rolled carpet corner, the tallest thing on the floor, raked by the key"

art:
  technique: "material relief through txbench.js, three floor materials at one scale"
  why_this_technique: "a plan at one scale is the only projection where 100,000 inside 735,000 reads true without the caption"
  palette: "grey sealed slab, a paler fresh pour, charcoal carpet tile, warm timber form boards"
  value_structure: >
    Lightest is the fresh pour's raked edge and the form boards. Darkest is the floor beyond the slab and the
    carpet. Frame median L* planned at 14.

type:
  hook: "Past 735,000 square feet"
  dek: "Lockheed says it is investing $300 million to grow the operation past 735,000 square feet, with 100,000 of new space and 85,000 of office turned to manufacturing. Each area is drawn as a square at one scale, not the plant's shape."
  labels: ["more than 735,000 sq ft", "100,000 new", "85,000 office"]

verbatim: []

acceptance:
  - "the squares together span at least 700 px of the frame width at full size"
  - "the slab square's side is computed from footprint_sqft and spans at least 700 px, and a frame with no slab fails"
  - "the new pour and carpet squares are computed from new_sqft and office_sqft at the slab's scale, the pour visibly larger"
  - "the form boards and the rolled carpet cast shadows to the right"
  - "no building shape, door or plant layout is drawn"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "a square of slab can read as an empty grey plate, so its saw joints are cavities and the casts are long"
```

```yaml
slide: 3
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "a black foam kitting tray holding one production employee's share of 2025's parts in plan, 312 pockets each with the part, one pocket empty and its part on the bench,"
  rect: [36, 620, 1020, 560]
  bleeds: []
accent: none
job: >
  Make 250,000 parts and nearly 800 people into one thing a reader can see, the parts one production employee's share stands for, drawn and never printed.

claims: [c12, c7, c8]
numerals:
  - value_from: parts_2025
  - value_from: employees
  - value_from: parts_year

data_in_art:
  figure: parts_per_employee
  drives: the number of pockets cut in the tray, each holding one part, rows of 24

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The tray fills the lower half of the frame, its pockets in rows, the bench's dark steel around it. One
    pocket near the top right is empty and its part lies on the steel bench above the tray, the one lifted unit
    that says each pocket is one part.
  bands: >
    Top third, the bench's dark steel with the hook, dek and the lifted part. Middle third, the tray's first rows. Bottom third, more rows of parts in relief, each casting a shadow into its pocket under the low light, running off the edge.
  focal: "the empty pocket and the lifted part beside it"

art:
  technique: "material relief through txbench.js, an isotype of a counted object in its real unit"
  why_this_technique: "a count shown as the real part in a real tray is read as parts, not as a bar"
  palette: "black kitting foam, bright 6061, dark steel"
  value_structure: >
    Lightest are the parts' raked top faces. Darkest are the foam and the pocket floors. Frame median L* planned at
    16.

type:
  hook: "250,000 parts in 2025"
  dek: "The plant makes components for missiles such as PAC-3 MSE and THAAD. It made 250,000 parts in 2025 and has nearly 800 production employees now. Split evenly and rounded down, that fills this tray, one pocket a part. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the foam tray spans at least 800 px of the frame width at full size"
  - "the tray holds exactly parts_per_employee pockets in rows of 24, and every pocket but one is countable at full size"
  - "each part shows its two pockets at full size, and a frame with no parts fails"
  - "one pocket is empty and its part lies on the bench outside the tray"
  - "no number on the frame is the share itself"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "312 small parts can read as a texture, so the lifted part is large enough to read as the unit"
```

```yaml
slide: 4
layout: FIGURE_SCALE
primary_image:
  subject: "a converted office turned machine room: the near machining centres of the east row with a machinist standing full length at the third for scale, and 30 machining centres in two rows receding into the dark under last light from the west windows"
  rect: [500, 360, 580, 760]
  bleeds: [right]
accent: none
job: >
  Show what the plant has already done on its own, more than 30 machines added in a few months, with a person for scale and the cell nowhere in it.

claims: [c10, c2]
numerals:
  - value_from: added_machines

data_in_art:
  figure: added_machines
  drives: the number of machining centres instanced in the two rows

depth:
  eye: 1.6
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: -3.2, Z: 2}

composition:
  structure: >
    The near machines of the east row fill the right third, doors shut and windows lit, the machinist standing at
    the third for scale. The two rows run back into the dark, a pool from the aisle's high bay on the floor between
    them. The dark ceiling holds the type.
  bands: >
    Top third, the stripped dark ceiling with the hook and dek. Middle third, the machine's lit window and the rows
    receding. Bottom third, the worn concrete floor modelled in relief under the aisle's pool, the machines' bases casting soft shadows across it.
  focal: "the near machine's lit window and the machinist standing beside the row"

art:
  technique: "physically based render of the chassis machining_centre, full and low detail, inside a TXT.interior room with a west window"
  why_this_technique: "rows of real machines in a room give 30 a size a reader can feel"
  palette: "graphite enamel, warm window light, cold lit glass, a dark epoxy floor"
  value_structure: >
    Lightest are the window light on the floor and the lit door windows. Darkest are the ceiling and the far end of
    the rows. Frame median L* planned at 12.

type:
  hook: "More than 30 machines, already"
  dek: "The company says it turned former office space into manufacturing areas and installed more than 30 high precision machines in a few months. These are Lockheed's own, not Hadrian's cell. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the near machining_centre stands at least 420 px tall at full size"
  - "the near machining_centre is modelled at full detail with its door, window, handle and pendant, and a frame without it fails"
  - "the near machine spans at least 300 px of the frame width, and a frame with no machine fails"
  - "at least ten further machines are distinguishable as separate machines at 432 px"
  - "the machinist stands full length under a fifth of the frame height, lit from the camera side, with a contact on the floor"
  - "no taped bay and no accent appears in the frame"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "a kit person can read as a mannequin, so only a shoulder and arm at the pendant are in frame"
```

```yaml
slide: 5
layout: DIAGRAM
primary_image:
  subject: "the shop floor in plan, 100 machining centre roofs in ten rows of ten, each with its column cap, tool drum hood, pendant arm, chip cart and a stack pole casting a long shadow down its aisle"
  rect: [0, 600, 680, 750]
  bleeds: [left, bottom]
accent: none
job: >
  Draw the plant's own buildout as machines at one scale, nearly 100 by the end of 2026, before the cell is set beside it.

claims: [c11]
numerals:
  - value_from: machines_by_2026

data_in_art:
  figure: machines_by_2026
  drives: the number of machine footprints laid out in rows of ten

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The block of 100 fills the middle and bleeds the sides and bottom, rows running across the frame so the low key's
    casts run down the aisles. The top band is bare dark floor for the type. The lower right corner of the floor is
    left empty, where frame 6 will set the cell.
  bands: >
    Top third, the dark epoxy with the hook and dek. Middle third, the first rows of roofs. Bottom third, the last rows of roofs in relief with their stack pole shadows, and the lit epoxy corner where frame 6 sets the cell.
  focal: "the first row's lit west edges and the long parallel casts"

art:
  technique: "material relief through txbench.js, a plan isotype of machines at one scale"
  why_this_technique: "plan view at one scale is the only projection where 100 and 24 can be set side by side truthfully"
  palette: "graphite roofs with a pale fascia line, a near black epoxy floor, steel stack poles"
  value_structure: >
    Lightest are the roofs' west lips and the fascia lines. Darkest are the floor and the casts. Frame median L*
    planned at 10.

type:
  hook: "Nearly 100 new machines"
  dek: "Lockheed expects to have added nearly 100 new advanced machines across the facility by the end of 2026. The block draws 100, at one scale. Drawn to illustrate."
  labels: ["nearly 100 by end of 2026"]

verbatim: []

acceptance:
  - "the 100 machining_centre roofs span at least 800 px of the frame width at full size"
  - "exactly machines_by_2026 roofs are drawn in rows of ten, and a frame with no roofs fails"
  - "each roof shows a column cap and a drum hood at full size, so it reads as a machine and not a rectangle"
  - "no floor grid lines are drawn between the machines"
  - "no accent appears in the frame"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "100 rectangles can read as graph paper, so each carries its parts and the floor carries no lines"
```

```yaml
slide: 6
layout: DIAGRAM
primary_image:
  subject: "the same plan and light as frame 5, the 100 machine roofs, and across one empty aisle Hadrian's cell as 24 empty bays in comal lit tape outlines on satin epoxy pads, six rows of four"
  rect: [0, 600, 1080, 750]
  bleeds: [left, right, bottom]
accent: "#8FE0F0"
job: >
  Set Hadrian's 24 beside the plant's own nearly 100 at one scale, as empty bays, because the cell has not cut a part and the release doesn't say whether it counts toward the 100.

claims: [c4, c11, c3]
numerals:
  - value_from: cell_machines
  - value_from: machines_by_2026
  - value_from: cell_year

data_in_art:
  figure: cell_machines
  drives: the number of empty taped bays laid out beside the 100 roofs (machines_by_2026), at the same pitch

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The 100 roofs keep frame 5's place and light, so the swipe adds one thing. The 24 bays sit in the lower right
    across an empty aisle, cold outlines with no machine in them. Two DOM labels name each set.
  bands: >
    Top third, the dark floor with the hook and dek. Middle third, the roofs. Bottom third, the last roofs in relief with their long shadows, and the block of 24 bays whose tape catches the low light on glossy pads.
  focal: "the 24 comal lit outlines, the only colour in the frame"

art:
  technique: "material relief through txbench.js on frame 5's bench, the cell added as taped bays"
  why_this_technique: "the same bench and light make the difference between the two blocks the only thing that changes"
  palette: "graphite roofs, near black epoxy, the comal lit tape"
  value_structure: >
    Lightest are the tape outlines and the roofs' lit lips. Darkest are the floor and the empty pads. Frame median L*
    planned at 10.

type:
  hook: "24 machines, expected in early 2027"
  dek: "The release doesn't say whether Hadrian's 24 count toward the nearly 100, so they are drawn apart, as empty bays. Drawn to illustrate."
  labels: ["nearly 100 by end of 2026", "Hadrian's 24"]

verbatim: []

acceptance:
  - "the 100 roofs and 24 bays span at least 800 px of the frame width at full size"
  - "exactly cell_machines taped bays are drawn, each a closed comal lit outline, and a frame without them fails"
  - "the 100 roofs are identical in place to frame 5"
  - "no machine stands in any bay"
  - "the two blocks are separated by an aisle at least one bay wide and are never drawn as one block"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "thin tape can vanish at 432 px, so the outline is wide enough to carry the accent and the pads are glossy"
```

```yaml
slide: 7
layout: DOCUMENT
primary_image:
  subject: "a cyanotype engineering sheet of the part on a black granite plate, three orthographic views in white line with hidden pockets dashed and a detail of one counterbore, a blank title block with a comal lit tab, and the finished part standing on its own plan view"
  rect: [30, 580, 1020, 750]
  bleeds: []
accent: "#8FE0F0"
job: >
  Put Hadrian's own words about its software beside a design and a part, and say plainly they describe Hadrian's factories, not this cell.

claims: [c20, c21, c15, c22]
numerals: []

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The sheet lies flat across the lower half on the granite, with the part standing on
    its plan view and casting onto the sheet. The verbatim line sits above the sheet as DOM, on the granite.
  bands: >
    Top third, the granite with the hook and dek. Middle third, the verbatim line and the sheet's top edge. Bottom third, the views in relief, the title block with its tab, and the part casting a long shadow onto the sheet under the low light.
  focal: "the part standing on its own drawing, raked by the key"

art:
  technique: "material relief through txbench.js, a drawn page with its own linework on a granite plate"
  why_this_technique: "a legacy drawing and the part it becomes are the two ends of what Hadrian says Opus does"
  palette: "cyanotype blue, white line, black granite, bright 6061, one comal lit tab"
  value_structure: >
    Lightest are the part and the white linework. Darkest are the granite and the sheet's blue. Frame median L*
    planned at 10.

type:
  hook: "Software it calls AI powered"
  dek: "Hadrian says this of the software in its own factories. Its home page also offers manufacturing cells deployed at customer sites. Drawn to illustrate."
  labels: []

verbatim:
  - claim: c20
    text: "Opus interprets legacy designs and automates manufacturing and inspection"

acceptance:
  - "the sheet spans at least 700 px of the frame width and its three views are distinguishable at 432 px"
  - "the part stands on the sheet with a cast shadow onto it, and a frame with no part fails"
  - "the drawing carries no numerals"
  - "the verbatim line matches c20 character for character"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "white linework can lift the frame into the mid tones, so the lines are thin and the blue is deep"
```

```yaml
slide: 8
layout: CLOSE_CROP
primary_image:
  subject: "the machining centre's control pendant in graphite enamel on a swing arm that enters level from the right, its screen black, its keys, knob and handwheel raked by a low warm work lamp, the shut door behind it"
  rect: [270, 600, 640, 750]
  bleeds: [bottom]
accent: none
job: >
  Turn the deck on its open question, what the AI does inside this cell, on the one object an operator would watch it on.

claims: [c3, c16, c15]
numerals: []

depth:
  eye: 1.45
  horizon: 560
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 1.48, Z: 1.53}

composition:
  structure: >
    The pendant fills the lower middle and is cut by the right and bottom edges, turned toward the reader, its screen
    a black slab. The enclosure's shut door and graphite panel fall away behind it into the dark, which holds the
    type.
  bands: >
    Top third, the dark enclosure with the hook and dek. Middle third, the pendant's top and its black screen. Bottom third, the keys, the knob and the handwheel lit on their west edges with shadow between them, cut by the edge.
  focal: "the black screen and the keys' lit edges under it"

art:
  technique: "physically based render of the chassis machining_centre's pendant at close range in the lastLight world"
  why_this_technique: "a dark screen on a real control is the honest picture of software the release does not describe"
  palette: "pale bevelled housing, black coated glass, dark keys, steel handwheel"
  value_structure: >
    Lightest are the housing's lit bevel and the key edges. Darkest are the screen and the background. Frame median
    L* planned at 8.

type:
  hook: "Will AI do anything here?"
  dek: 'Hadrian''s chief says it is bringing "the automation, software and workforce training from our own factories directly inside Lockheed Martin". The release never says whether AI does anything in this cell. Drawn to illustrate.'
  labels: []

verbatim:
  - claim: c16
    text: "the automation, software and workforce training from our own factories directly inside Lockheed Martin"

acceptance:
  - "the pendant spans at least 420 px of the frame width, and a frame with no pendant fails"
  - "the screen reads as black glass with no text, no chart and no numerals"
  - "at least two rows of keys read as separate keys at 432 px"
  - "no accent appears in the frame"
  - "the frame's median L* at 432px is 18 or lower"

risks:
  - "a dark screen on a dark background can vanish, so the bezel and housing bevel carry the key's edge"
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: "the cell as empty bays at standing eye: the near bay's glossy epoxy pad, comal lit tape, levelling plates and drop cord, the rest of the 24 receding, a machinist three quarter away at its edge, Lockheed's lit machines far off in the dark"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#8FE0F0"
job: >
  Close on what happens next and who does it, the cell expected in early 2027 and run by Lockheed's own workforce, with the jobs figure named as the company's own.

claims: [c3, c4, c5]
numerals:
  - value_from: cell_year
  - value_from: jobs_tx

data_in_art:
  figure: cell_machines
  drives: the number of empty bays built in four rows of six

depth:
  eye: 1.4
  horizon: 700
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The near bay fills the lower third, its tape running toward the reader, the machinist standing at its far edge.
    The rows of bays recede diagonally into the dark, and far beyond them a few of Lockheed's machines glow warm. The
    dark ceiling holds the type.
  bands: >
    Top third, the dark hall with the hook and dek. Middle third, the far bays and the distant machines. Bottom third, the near bay's glossy pad catching the light, its tape, and the levelling plates casting shadow in the foreground.
  focal: "the near bay's lit pad and its cold outline"

art:
  technique: "physically based render of the chassis machine_bay and machining_centre inside a TXT.interior hall"
  why_this_technique: "an empty bay a reader stands at is the cell as it is, a plan for 2027"
  palette: "glossy black epoxy, comal lit tape, steel plates, a warm distant glow"
  value_structure: >
    Lightest are the tape outline and the plates' edges. Darkest are the empty pads and the hall. Frame median L*
    planned at 8.

type:
  hook: "Lockheed's own crews will run it"
  dek: "The cell is expected to be operational in early 2027 and run by Lockheed's production workforce. The release's 2,000 Texas jobs are the company's own figure, statewide. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the near bay's tape outline spans at least 600 px of the frame width, and a frame with no bay fails"
  - "at least eight separate taped bays are distinguishable at 432 px"
  - "no machine stands in any bay"
  - "the machinist is under a fifth of the frame and lit from the camera side"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "an empty bay can read as nothing, so the tape is bright and the plates and cord give it scale"
```
