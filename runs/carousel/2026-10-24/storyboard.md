# Storyboard, 2026-10-24
# "Tesla's Texas vehicle and Megapack rows read Production. The robot row reads Construction."

## The story, and what the fact check did to it

Tesla's update for the third quarter of 2026, its webcast set for October 21st (c1), carries a table of installed
annual capacity. Under its Texas label it lists Model Y at more than 375,000 a year (c2), the Cybertruck and the
Cybercab at more than 125,000 each (c3, c4) and Megapack at 50 GWh (c5), all with the status Production. The Texas row
for Optimus, the company's humanoid robot, reads Construction and carries no figure (c6). Tesla defines construction as
factory and infrastructure buildout plus tool installation (c11). Optimus production began on lines in Fremont,
California, where the row reads Early Ramp (c7, c27). The supporting table lists AI training compute in the Texas rows,
Cortex 1 at more than 105 MW and Cortex 2 at more than 120 (c12, c13), for vehicle and humanoid robot autonomy software
(c22), beside a plan for 400 MW by year end with no location (c21). The Austin Fab is still under construction, with
equipment commissioning planned for 2027 (c23, c24). Tesla began putting the Cybercab into its Austin Robotaxi fleet
(c28). The footnote is the honest half: installed capacity is not the current production rate (c8, c9, c10), and the
update gives no count of Cybercabs built, deployed or carrying riders (c34). NHTSA's audit of how Tesla certified a car
with no steering wheel, pedals or mirrors is still open (c35, c42, c43).

The fact check moved four things. The Cybertruck, Cybercab and Cortex 2 rows sit under the Texas label by table layout
alone, so every surface says "the Texas rows" or "under the Texas label" and never names a plant for them. The 400 MW
plan and the 40 MW of other compute carry no location and are never placed in Texas. The two million unsupervised miles
are service wide and stay off the deck. NHTSA's 1,000 is an estimated population and is never a count of cars.

## Why this treatment, and what was grafted

Director B's plant walk is the spine. The table's only verb is its status column, and a walk turns that column into
light a reader sees before reading a word: a lit line where the table says Production, a dark slab where it says
Construction. It is the one treatment whose cover reads as a factory at 432 px, and it makes Construction visible as
an absence, bolts and tape where a robot line would be. Two plan reliefs carry the figures the doors can't, the three
vehicle rows at one scale and the training compute at one scale.

Grafted from Director C: the reader's question. A lit bay looks like output, so the copy names every light as the
status Tesla printed, frame 8 covers the one car the deck shows, and the close reverses the cover from the dark end and
says a lit bay is a status, not a count. Grafted from Director A: the empty plan as a raw outline, so the 400 MW goal is
an empty groove with no ground under it. Refused from A: bars lying in a field, which a reader takes for sculpture.
Refused from C: a concrete box as the hero, which reads as a bunker before it reads as a quantity, and the cabin
cutaway, which would make a second car frame and tip the deck toward a robotaxi story.

## The world, and the laws that hold it

**FLOODLIT, A PLANT APRON AT NIGHT.** The chassis is `assets/js/deck/2026-10-24-apron.js` and every frame loads it. It
declares `sky: floodlit` with the key at azimuth -58, elevation 25: one cold LED flood on a far mast to the camera's
left and in front, the lowest elevation the world allows, so every jamb, bolt and column has one lit edge and every
cast runs long to the right and away. A material relief reads the same light from the upper left of its frame and its
casts run down and to the right. +x is east, +z south, a bay door faces +z.

The argument for this world: a plant runs on its own light at night. Under one flood on a black sky the only other
light in any frame is the bay's own, and that is the variable the deck reads. Three of the last four decks stood in
lastLight, and a dusk seam would put a time of day on a table that has none.

1. **Start dark.** Black sky, a sealed apron that is lit only where the flood lands, tilt up panels shaded on the face
   away from the key.
2. **Type is light, on the dark field**, and every wash only darkens.
3. **Bluebonnet is the only accent** and means one thing, planned or under construction and not yet installed.
4. Every standing thing gets `TXT.contact`, every spatial frame `TXT.weather`.
5. **No logo, no wordmark, no product likeness, no robot.** The crossover is unbadged primer grey, the car on frame 8 is
   under a fabric cover, and the plant's plan is the table's order, not the site's.
6. **The status is the light.** A bay whose row reads Production has its high bay rows lit warm. The Optimus bay has the
   same rows modelled and off.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#08060F` | the DOM body behind the render |
| `accent` | `#4E5FA8` | bluebonnet tape, planned or under construction: 5, 6, 7, 9 |
| `hook` | `#ECE8DF` | light type on the dark |
| `dek` | `#D6D0C4` | the dek |
| `material` | `#CFC8BA` | Austin chalk aggregate concrete where the flood rakes it |

The world's materials: tilt up concrete panels in a chalk aggregate, galvanized steel jambs and bollards, a sealed
concrete apron with worn joints and oil stains, warm 3500K high bay light inside the lit bays, plywood crates with steel
strapping, primed red oxide steel, grey cover fabric, and the black Blackland clay past the apron's edge.

## The continuity devices

    CONTINUITY: CAMERA_MOVE, MOTIF_EVOLUTION, VALUE_ARC

1. **Camera move.** Arrive wide on the apron (1), stand at the Model Y threshold (2), drop to plan for the vehicle rows
   (3), stand beside the battery enclosures (4), step inside the dark bay (5), plan again for the compute (6), look up at
   the Fab's steel (7), stand behind the covered car looking out (8), and look back along the apron from the dark end (9).
2. **Motif evolution, the bay's light and the bluebonnet tape.** High bay rows lit where the table says Production (1,
   2, 4, 8, 9), the same rows dark in the Optimus bay (5), and the tape appearing only on what is planned or under
   construction: the empty pads (5), the empty 400 MW groove (6), the Fab's equipment pads (7), the dark bay's
   threshold (9).
3. **Value arc.** Four warm doors in a black field (1), the brightest at the lit threshold (2), the reliefs on a dark
   slab (3, 6), the darkest at the turn inside the unlit bay (5) where only the flood wedge and two lamps carry light,
   and the close back to the four lit doors seen from the dark end (9).

## The rotation

    FULL_BLEED  CLOSE_CROP  DIAGRAM  FIGURE_SCALE  FULL_BLEED  DIAGRAM  SPLIT_HORIZON  OBJECT_AND_CAPTION  FULL_BLEED

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | WIDE, a crane eye 9 m over the apron, 52 m off the third door, looking down the wall from the west, fov 34 | the chassis plant_wall, 80 m of tilt up chalk aggregate panels with reveals and a galvanized coping, five vertical lift door openings 10 by 8 m with galvanized jambs, four bays lit inside by warm downlight over their lines (covered bodies, a crossover, enclosures), the fifth dark with two work lamps on its threshold, the sealed apron lit by the flood with worn joints and painted lane lines, bollards with contact, a kit worker on the lane |
| 02 | CLOSE, eye 1.2 m just inside the first lit bay's door, 14 m down the line, fov 30 | the kit crossover in unbadged primer grey on the chassis line_carrier, a steel skillet on a floor track, the nearest body cropped by the left edge and the second in the bay's warm downlight, contact and tyre polish under each carrier, the dark back wall behind |
| 03 | MACRO, an orthographic relief of the apron in plan | three line channels, milled into dark sealed concrete with tooth in its albedo, a crowned steel rail in each catching a specular line, a raised galvanized stop block at each measured end casting to the lower right, two saw cut joints, grime along the channel lips |
| 04 | MEDIUM, eye 1.4 m off the row's west end, looking east along it, fov 40 | five chassis megapack_unit enclosures in a row on the apron 30 m out from the plant wall, louvred white steel with a grey plinth, grime at the base, a kit worker beside the second for scale, the wall and its lit doors behind the row |
| 05 | CLOSE, eye 0.9 m just inside the dark bay's door, 4 m off the nearest bolt group, looking in with the flood over its shoulder, fov 46 | the chassis anchor_bolt_set at detail, four threaded galvanized rods 0.32 m proud with hex nuts and plate washers in a grout pocket, lit by the cold flood wedge that enters through the door and rakes the sealed slab, one kit machine_pad in bluebonnet tape around a bolt group, two plywood tool_crates in silhouette, a tripod_work_lamp's warm pool, the apron outside through the door |
| 06 | MACRO, an orthographic relief of a steel plate in plan | finned anodised aluminium blocks at one MW scale on a blackened steel plate, a cast iron offcut set apart, an empty milled groove holding bluebonnet tape, casts to the lower right |
| 07 | WIDE, eye 2.6 m off the slab's corner, 12 m off the nearest column, fov 44 | the chassis steel_frame, W section columns on a 9 m grid rising 14 m to open web joists and rod bracing in red oxide primer, no cladding, two kit machine_pads in bluebonnet tape on its slab, contact at every column base |
| 08 | MEDIUM, eye 1.35 m on the apron at the third door, 11 m off the covered car, looking into the lit bay, fov 42 | the chassis covered_pod, the kit crossover's body under a grey fabric cover at roughness 0.95 with a hem of folds above the wheels and its small parts hidden, on a line_carrier with contact, a staged pool on the carrier, the bay's dark walls round it as a room, the next carrier empty behind |
| 09 | WIDE, a crane eye 7.5 m over the apron, 32 m east of the dark bay, looking back along the wall, fov 42 | the same plant_wall seen from its east end, the dark fifth bay large on the right with two tripod_work_lamps and bluebonnet tape on its threshold, the four lit bays diminishing to the left under the flood, contact under every lamp and bollard |

Showstopper frame: 05, the dark robot bay at seated eye, its depth from the bolts in the foreground against the crates and the far wall, contact and cast shadow across the wedge, four galvanized bolts close enough to read their threads, the flood's one cold wedge across the slab, bluebonnet tape on empty pads and the high bay lamps overhead present and off
Tonal arc: four warm doors in a black field on 01, the brightest at the lit threshold on 02, the reliefs low and dark on 03 and 06, the battery row mid on 04, the darkest frame at the turn on 05 where only the wedge and two lamps carry light, the steel lifting against black on 07, the covered car under the bay's light on 08 and the close on 09 back to the four lit doors from the dark end
VALUE CUT: frame 5. The deck turns from what the table lists as made in Texas to the one row that is not, and the unlit bay is that turn.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "a tilt up plant wall at night along a sealed apron, five vertical lift door openings, four lit inside and the fifth dark with two work lamps"
  rect: [0, 600, 1080, 750]
  bleeds: [left, right, bottom]
accent: none
job: >
  Say the whole story as one picture: Tesla's own table lists Texas rows as Production, and one row, the robot, as
  Construction.

claims: [c2, c3, c4, c5, c6]
numerals: []

data_in_art:
  figure: production_rows
  drives: the count of lit door openings, one per Texas row of the manufacturing table whose status reads Production, with the fifth door dark for the one row that reads Construction

depth:
  eye: 9.0
  horizon: 560
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 40, Z: 0}

composition:
  structure: >
    The camera stands at crane height over the apron, looking down the wall from the west, so the five door openings
    recede from the left edge toward the wall's east end at the right, the first door cropped by the left edge. The black sky above the parapet holds the hook and the dek. The apron runs off the bottom.
  bands: >
    Top third, the black sky with the hook and the dek. Middle third, the wall's parapet and the four warm door
    openings receding with the dark fifth at the far end. Bottom third, the sealed apron lit by the flood, the bollards'
    casts running right, the worker on the painted lane.
  focal: "the nearest lit door opening and the line light inside it, the brightest area"

art:
  technique: "physically based render of the chassis plant_wall, bollards and the kit person in the floodlit world, staged on the near door and the worker"
  why_this_technique: "the status column of the table becomes light a reader sees before reading a word, and only a place at true scale gives the bays a size"
  palette: "chalk aggregate concrete, galvanized steel, warm 3500K bay light, a cold LED flood, black clay, black sky"
  value_structure: >
    Lightest are the near door's interior line light and the jamb's lit edge. Darkest are the sky, the wall's shadow
    face and the fifth door. Frame median L* planned at 12.

type:
  hook: "Tesla's Texas vehicle and Megapack rows read Production. The robot row reads Construction."
  dek: "The lit doors are Model Y, Cybertruck, Cybercab and Megapack under Tesla's Texas label. The dark door is Optimus, its humanoid robot. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the plant wall spans the full frame width and stands at least 160 px tall at 432px"
  - "five door openings are visible in the wall at full size"
  - "exactly four door openings show warm lit interiors and the fifth shows no lit high bay row"
  - "the nearest door opening spans at least 200 px of the frame width at full size"
  - "the apron is lit with at least one bollard cast visible at 432 px"
  - "no logo, wordmark or legible sign in frame"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "lit door interiors are the mid tone risk, so the back walls stay unlit and only the lamp rows and the line carry light"
```

```yaml
slide: 2
layout: CLOSE_CROP
primary_image:
  subject: "an unbadged primer grey crossover body on a steel line carrier inside the first lit door, cropped by the right edge and the door header"
  rect: [0, 620, 1000, 560]
  bleeds: [left]
accent: none
job: >
  Put a size on the biggest Texas row: Model Y at more than 375,000 a year of installed capacity, status Production.

claims: [c2, c8]
numerals:
  - value_from: c2

depth:
  eye: 1.2
  horizon: 560
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 2, Z: -3}

composition:
  structure: >
    The camera stands just outside the first door at threshold height, angled along the wall, so the steel jamb runs
    up the left third and the line recedes into the bay. The crossover's nose and A pillar sit on the carrier in the
    right half and run off the right edge and the header. Black sky shows above the parapet at top left.
  bands: >
    Top third, the black sky and the parapet at left with the hook and the dek over them. Middle third, the jamb, the
    crossover's roof rimmed by the bay light and the lamp rows receding. Bottom third, the carrier, the floor track and
    the threshold slab lit by the flood, its texture worn with oil and tyre polish and the carrier's shadow.
  focal: "the crossover's roof line and windscreen rimmed warm by the bay light, the brightest area"

art:
  technique: "physically based render of the kit crossover on the chassis line_carrier inside the chassis plant_wall's first bay, floodlit, staged on the car"
  why_this_technique: "a body on a line is what a row reading Production means, and a close crop puts the reader at the line"
  palette: "primer grey paint, galvanized steel, warm bay light, a cold flood on the threshold"
  value_structure: >
    Lightest are the car's roof rim and the lamp rows. Darkest are the sky, the bay's back wall and the shadow under
    the carrier. Frame median L* planned at 16.

type:
  hook: "More than 375,000 Model Y a year, installed"
  dek: "Tesla lists Model Y in Texas at more than 375,000 a year of installed capacity, status Production. It also says installed capacity is not the current production rate. The bay is drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the crossover body spans at least 380 px of the frame width at full size"
  - "the car carries no badge, wordmark or legible plate"
  - "at least one lit high bay row is visible inside the bay at 432 px"
  - "black sky shows in the top left of the frame"
  - "the frame's median L* at 432px is 28 or lower"

risks:
  - "the kit crossover can read as a toy box, so it is cropped close with its curved glasshouse in the light and the boxy rear out of frame"
```

```yaml
slide: 3
layout: DIAGRAM
primary_image:
  subject: "three line channels milled into dark sealed concrete in plan, each with a crowned steel rail and a raised stop block at its measured end, the Model Y channel three times the length of the other two"
  rect: [80, 660, 940, 520]
  bleeds: []
accent: none
job: >
  Measure the three Texas vehicle rows against each other on one scale, so the three to one to one is geometry and not
  a typed ratio.

claims: [c2, c3, c4, c8]
numerals:
  - value_from: c2
  - value_from: c3
  - value_from: c4

data_in_art:
  figure: model_y
  drives: channel length, each channel's length from its row's installed capacity at one pixel scale, Model Y from model_y and the Cybertruck and Cybercab from cybertruck and cybercab

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The apron in plan fills the lower 60 percent. Three channels run left to right from one datum near the left edge,
    stacked with clear slab between them, the Model Y channel running nearly the full width and the other two a third
    of it. Mono labels sit above each channel's left end, clear of the rails.
  bands: >
    Top third, the dark ground with the hook and the dek. Middle third, the Model Y channel with its label and stop
    block. Bottom third, the Cybertruck and Cybercab channels in relief, their rails lit and their stop blocks casting shadow, the footnote line under them.
  focal: "the Model Y channel's stop block and the rail's specular line, the brightest area"

art:
  technique: "material relief through txbench.js, four materials (sealed slab, channel floor, steel rail, stop block) under the deck's light"
  why_this_technique: "a quantity is read in plan, never in perspective, and a channel cut to length is a figure a reader can run a thumb along"
  palette: "dark sealed concrete, black channel floor, bright crowned steel, galvanized stop blocks"
  value_structure: >
    Lightest are the rails' specular lines and the stop blocks' lit tops. Darkest are the channel floors and the casts.
    Frame median L* planned at 10.

type:
  hook: "Three vehicle rows on one scale"
  dek: "Each channel's length is the floor Tesla prints for its row. The Model Y floor is three times the Cybertruck and Cybercab floors, each printed as more than."
  labels: ["Model Y >375,000", "Cybertruck >125,000", "Cybercab >125,000", "installed annual capacity, not output"]

verbatim:
  - claim: c2
    text: "Model Y >375,000"
  - claim: c3
    text: "Cybertruck >125,000"
  - claim: c4
    text: "Cybercab >125,000"

acceptance:
  - "the Model Y channel is at least 780 px long at full size"
  - "three channels are visible, each with a lit rail"
  - "the Model Y channel measures three times the length of the Cybercab channel within 2 percent at full size"
  - "every stop block casts a shadow at least 50 px long at full size"
  - "the slab carries at most two saw cut joints, and no ruled grid"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "a relief under a 25 degree key casts short, so steps stand at least 28 px proud"
```

```yaml
slide: 4
layout: FIGURE_SCALE
primary_image:
  subject: "five white louvred battery enclosures in a row on the apron outside the fourth lit door, a worker at the row's end"
  rect: [0, 730, 1010, 450]
  bleeds: [left]
accent: none
job: >
  Say what else the Texas rows list as in production: Megapack at 50 GWh, and that the update's highlights call the
  same figure planned capacity.

claims: [c5, c25, c26]
numerals:
  - value_from: c5

data_in_art:
  figure: megapack_units
  drives: the enclosure count, one enclosure per ten GWh of the Megapack row, a drawing rule the dek states

depth:
  eye: 1.6
  horizon: 600
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A standing three quarter on the enclosure row, which runs from the left third diagonally into the right edge. The
    lit fourth door glows behind and above the row. The worker stands at the near end, three quarters away, lit from the
    camera's side.
  bands: >
    Top third, the black sky over the wall with the hook and the dek. Middle third, the enclosure row's louvred faces
    raked by the flood and the lit doors behind. Bottom third, the lit apron in the foreground with each enclosure's contact shadow and cast, and the worker's silhouette.
  focal: "the near enclosure's lit louvres and the worker beside it, the brightest area"

art:
  technique: "physically based render of five chassis megapack_unit enclosures and the kit person in the floodlit world, staged on the row"
  why_this_technique: "a GWh has no size of its own, so a counted row of enclosures with a person for scale is the honest picture of the row"
  palette: "white powder coated steel, grey plinth, chalk concrete wall, warm door, cold flood"
  value_structure: >
    Lightest are the enclosures' lit faces. Darkest are the sky and the enclosures' shadow sides. Frame median L*
    planned at 18.

type:
  hook: "Tesla says Megafactory Texas began production"
  dek: "The table lists Megapack in Texas at 50 GWh, status Production. The update's highlights call the same 50 GWh planned capacity. Each enclosure drawn here stands for a fifth of it."
  labels: []

verbatim: []

acceptance:
  - "the enclosure row is at least 600 px wide at full size and each enclosure at least 110 px tall"
  - "exactly five enclosures stand in the row at full size"
  - "a worker stands beside the row, under a fifth of the frame height"
  - "every enclosure has a contact shadow on the apron at 432 px"
  - "the frame's median L* at 432px is 30 or lower"

risks:
  - "white enclosures lift the frame into the mid tones, so their shadow faces turn to the camera and the flood rakes only the near faces"
```

```yaml
slide: 5
layout: FULL_BLEED
primary_image:
  subject: "inside the dark Optimus bay, galvanized anchor bolts close to the lens, empty pads in bluebonnet tape and crated tools beyond, two work lamps, the high bay lamps present and off"
  rect: [0, 760, 1080, 590]
  bleeds: [left, right, bottom]
accent: "#4E5FA8"
job: >
  Show the turn: the Texas row for Optimus reads Construction with no figure, so where the robot line would be there
  is a slab of bolts, tape and crates, and production of the robot began in California.

claims: [c6, c7, c11, c27]
numerals: []

data_in_art:
  figure: optimus_texas_capacity
  drives: the bay's line, zero carriers and zero lit high bay rows, because the Texas Optimus row's capacity cell is a hyphen

depth:
  eye: 0.75
  horizon: 820
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera sits low just inside the open door and looks into the bay, so the flood comes over its shoulder. A bolt
    group in its grout pocket stands in the lower middle inside a taped footprint, its rods lit on their near faces and
    their shadows run long across the lit slab. The other bolt groups, the taped empty pads and two crates lie beyond,
    a tripod work lamp stands at the left, the unlit fixtures hang overhead, and the bay falls to black behind.
  bands: >
    Top third, the bay's dark roof with the unlit lamp rows, the hook and the dek. Middle third, the crates, the taped
    pads and the two work lamps' small pools. Bottom third, the bolt group at detail with its long casts across the lit
    wedge.
  focal: "the bolt threads and nuts in the flood wedge, the brightest area"

art:
  technique: "physically based render inside a TXT.interior bay of the chassis anchor_bolt_set, tool_crate, tripod_work_lamp and lamp rows and three kit machine_pads, floodlit through the door, staged on the slab group"
  why_this_technique: "an absence has to be drawn as the things that wait for it, and bolts, tape and crated tools are what Tesla's own definition of construction names"
  palette: "galvanized steel, sealed concrete, plywood and steel strapping, bluebonnet tape, warm work lamps, the cold flood"
  value_structure: >
    Lightest are the bolt threads in the wedge and the work lamp heads. Darkest are the roof, the far wall and the
    slab outside the wedge. Frame median L* planned at 8.

type:
  hook: "Construction, with no figure"
  dek: "Tesla's Texas row for Optimus gives no capacity figure. Tesla defines construction as buildout and tool installation. Robot production began in Fremont, California. The bay is drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the nearest bolt group spans at least 160 px of the frame width at full size with four rods visible"
  - "at least one taped pad shows bluebonnet tape at 432 px"
  - "no robot, figure or vehicle stands in the bay"
  - "the bay shows no lit high bay lamp, its only lights the flood wedge and the work lamps"
  - "the frame's median L* at 432px is 20 or lower"

risks:
  - "a dark slab as the largest shape reads as nothing, so the bolts are close and large and the wedge crosses them"
```

```yaml
slide: 6
layout: DIAGRAM
primary_image:
  subject: "finned aluminium blocks on a blackened steel plate in plan at one MW scale, a cast iron offcut apart, an empty milled groove holding bluebonnet tape"
  rect: [0, 690, 1080, 420]
  bleeds: [left, right]
accent: "#4E5FA8"
job: >
  Measure the AI training compute the Texas rows list, Cortex 1 and Cortex 2, against the year end plan that names no
  place.

claims: [c12, c13, c14, c21, c22]
numerals:
  - value_from: c12
  - value_from: c13
  - value_from: c21

data_in_art:
  figure: cortex1_mw
  drives: block length, each block's length from its row's MW at one pixel scale, Cortex 1 from cortex1_mw, Cortex 2 from cortex2_mw, the offcut from other_mw and the empty groove from plan_mw

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    A steel plate in plan fills the lower 60 percent. Two finned blocks for Cortex 1 and Cortex 2 sit from one datum at
    the left, the cast iron offcut sits apart at the right, and below them the empty groove runs long across the plate
    with tape laid in it. Mono labels sit beside each piece.
  bands: >
    Top third, the dark ground with the hook and the dek. Middle third, the two finned blocks and the offcut with their
    labels. Bottom third, the milled groove in relief with its tape laid in it, its walls lit along one edge and in shadow along the other.
  focal: "the two finned blocks' lit fins, the brightest area"

art:
  technique: "material relief through txbench.js, four materials (blackened plate, finned aluminium, cast iron, tape) under the deck's light"
  why_this_technique: "megawatts are a quantity, read in plan at one scale, and an empty groove is the size of a plan that has no place"
  palette: "blackened steel, anodised aluminium, cast iron, bluebonnet tape"
  value_structure: >
    Lightest are the fins' lit edges. Darkest are the plate and the groove floor. Frame median L* planned at 10.

type:
  hook: "Training compute, in megawatts"
  dek: "The rows under Tesla's Texas label list Cortex 1 at more than 105 MW and Cortex 2 at more than 120. Tesla plans 400 MW by year end for vehicle and humanoid robot autonomy software and names no place."
  labels: ["Cortex 1 >105 MW", "Cortex 2 >120 MW", "other compute, place not given", "400 MW planned, place not given"]

verbatim:
  - claim: c12
    text: "Cortex 1 >105 MW"
  - claim: c13
    text: "Cortex 2 >120 MW"

acceptance:
  - "the two finned blocks together are at least 420 px long at full size"
  - "two finned blocks and one offcut stand proud of the plate with casts at full size"
  - "the empty groove measures the plan's length at the blocks' scale within 2 percent"
  - "the groove holds bluebonnet tape visible at 432 px"
  - "fins read as fins at 432 px, not as a ruled grid"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "fins at a tight pitch can read as graph paper, so the pitch stays wide and the fin tops catch the key"
```

```yaml
slide: 7
layout: SPLIT_HORIZON
primary_image:
  subject: "an unclad steel frame in red oxide primer rising against the black sky, two empty pads in bluebonnet tape on its slab"
  rect: [0, 470, 1080, 700]
  bleeds: [left, right]
accent: "#4E5FA8"
job: >
  Name the next thing being built: the Austin Fab, still under construction, with equipment commissioning planned for
  2027.

claims: [c23, c24]
numerals:
  - value_from: c24

data_in_art:
  figure: fab_machines_placed
  drives: machine count on the pads, zero machines placed on the two taped pads, because equipment commissioning is planned for 2027 and not begun

depth:
  eye: 2.6
  horizon: 700
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A camera at standing height off the slab's corner looks across it at the steel, so the columns rise from the slab
    through the frame to the joists against the black sky. The two taped pads lie empty on the lit slab in the lower
    half, and the type sits in the black sky above the joists.
  bands: >
    Top third, the black sky with the hook and the dek over the joists. Middle third, the columns' lit flanges and the
    bracing. Bottom third, the slab in the foreground lit by the flood, its texture worn, the taped pads and their levelling plates in relief.
  focal: "the nearest column's lit flange and its base plate on the slab, the brightest area"

art:
  technique: "physically based render of the chassis steel_frame and two kit machine_pads in the floodlit world, staged on the frame"
  why_this_technique: "a building that is not yet a building is steel and empty pads, which is what still under construction looks like"
  palette: "red oxide primer, galvanized base plates, sealed concrete, bluebonnet tape, black clay"
  value_structure: >
    Lightest are the flanges' lit edges. Darkest are the sky and the columns' shadow faces. Frame median L* planned at
    10.

type:
  hook: "The Austin Fab is still under construction"
  dek: "Tesla says it kept building the Austin Fab this quarter and plans to start commissioning equipment there in 2027. The steel is drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the steel frame stands at least 40 percent of the frame height tall, its top chord clear of the dek"
  - "at least four columns rise from the slab to the joists at full size"
  - "two taped pads show bluebonnet tape at 432 px with no machine on either"
  - "every column base has a contact shadow on the slab"
  - "sky shows above the steel in the top fifth of the frame"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "a lattice of thin members can read as a wireframe, so the columns are built as I sections with flanges that catch the flood"
  - "60 percent of the height would put the base plates in the footer under a three line dek, so the frame is held at about half the height and the camera closes on it"
```

```yaml
slide: 8
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "a two seat car under a fitted grey fabric cover on a line carrier just inside the third bay's open door, nose to the apron, seen from the apron into the lit bay"
  rect: [100, 610, 920, 520]
  bleeds: []
accent: none
job: >
  Say what the deck can say about the Cybercab on the road: deployment in Austin began, the update gives no count, and
  the federal audit of its certification is open.

claims: [c28, c34, c35, c42, c43]
numerals: []

depth:
  eye: 1.5
  horizon: 600
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera stands on the apron at the third door, close and low, and looks into the lit bay. The covered car sits on
    its carrier in the lower middle third, the next carrier empty behind it, and the bay's dark back wall and side walls
    hold the type.
  bands: >
    Top third, the bay's dark interior with the lamp rows high above the type, the hook and the dek. Middle third, the
    covered car under the lamp rows' warm light. Bottom third, the carrier and the floor track in a staged pool, each with its contact shadow.
  focal: "the cover's roof under the lamp rows, the brightest area"

art:
  technique: "physically based render of the chassis covered_pod and line_carrier inside the chassis plant_wall's third bay, floodlit through the door, staged on the car"
  why_this_technique: "a cover declines to draw a product and declines to draw the cabin the audit is about, which is what the record can say"
  palette: "grey fabric, galvanized carrier, warm bay light, the cold flood, black sky"
  value_structure: >
    Lightest are the cover's roof and the carrier deck in the pool. Darkest are the car's front, its hem and the bay's back wall.
    Frame median L* planned at 14.

type:
  hook: "Cybercab deployment began in Austin. Tesla gives no count."
  dek: "The cars go into its Austin Robotaxi fleet. The update gives no count of cars built. Federal regulators are auditing how Tesla certified a car that lacks permanently attached pedals and steering wheel. The car is drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the covered car spans at least 380 px of the frame width at full size"
  - "the cover shows hem folds and the wheels show below it at 432 px"
  - "the bay's side and back walls stand dark around the car, with no sky or dusk gradient in frame"
  - "no badge, wordmark or cabin detail is visible"
  - "the frame's median L* at 432px is 26 or lower"

risks:
  - "a grey cover can read as a lump, so the loft carries a clear roof line, wheel arches and hem folds"
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: "the same plant wall seen from its dark fifth door, two work lamps standing lit on the taped threshold, four lit doors diminishing along the wall"
  rect: [0, 600, 1080, 750]
  bleeds: [left, right, bottom]
accent: "#4E5FA8"
job: >
  Close on the consequence: a lit bay is a status Tesla printed, not a count of what it makes, and the audit of the car
  is still open.

claims: [c8, c9, c10, c34]
numerals: []

data_in_art:
  figure: production_rows
  drives: the count of lit door openings seen from the dark end, one per Texas row of the manufacturing table whose status reads Production

depth:
  eye: 7.5
  horizon: 600
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 72, Z: 0}

composition:
  structure: >
    The cover reversed. The camera stands over the apron east of the wall, looking back along it, so the dark fifth door
    stands large on the right with its two work lamps and taped threshold, and the four lit doors diminish toward the
    left.
  bands: >
    Top third, the black sky with the hook and the dek. Middle third, the wall and its four warm openings receding.
    Bottom third, the threshold in the foreground with the tape lit by the lamp's glow, and the apron's texture under the flood.
  focal: "the work lamp's head and the tape under it, the brightest near area, against the four warm doors"

art:
  technique: "physically based render of the chassis plant_wall, tripod_work_lamp and the kit person in the floodlit world, from the opposite end of frame 1, staged on the wall"
  why_this_technique: "standing in the row that is not lit and looking back is the reader's own question, how many, made into a place"
  palette: "chalk concrete, galvanized steel, warm bay light, bluebonnet tape, the cold flood, black sky"
  value_structure: >
    Lightest are the work lamp's head and the nearest lit door. Darkest are the sky, the wall's shadow face and the
    dark bay beside the camera. Frame median L* planned at 10.

type:
  hook: "A lit bay is a status, not a count"
  dek: "Tesla says installed capacity is not the current production rate, which turns on uptime, supply, downtime for upgrades, regulation and other factors. Its update gives no count of Cybercabs built."
  labels: []

verbatim: []

acceptance:
  - "the plant wall stands at least 150 px tall at 432px at its nearest lit door"
  - "four lit door openings are visible along the wall at full size"
  - "two work lamps stand on the dark bay's threshold with bluebonnet tape across it"
  - "the camera stands at the opposite end of the wall from frame 1, with the lit openings receding to the left"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "a reversed cover can read as the same frame twice, so the camera stands at the opposite end, the dark door is the nearest and largest opening, and the lamps stand lit on its threshold"
```
