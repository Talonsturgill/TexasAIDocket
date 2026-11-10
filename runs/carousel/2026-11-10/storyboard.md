# Carousel no. 73, November 10th, 2026: the tray

## The story, and what the fact check did to it

The Texas Advanced Computing Center at UT Austin published its account on October 29th of the symposium it held for
Texas researchers in September (c18, c19). Frontera, for most of its life the fastest academic supercomputer in the
United States (c3), was retired in October 2026 after more than eight million jobs (c1) and over seven years of
production, the longest run on any TACC system (c2). Its successor Horizon is in its first phase of early operations
(c4), its power infrastructure complete, its exabyte storage in place (c5) and its AI-focused hardware going in (c6).

Jose Rizo-Rey of UT Southwestern Medical Center (c7) studies synaptic transmission (c15). His lab simulates a 5.3
million atom system, a vesicle, a flat bilayer and four SNARE protein complexes (c8, c11), the proteins that let
vesicles fuse with their target membranes (c12). On Frontera it ran on 64 CPU nodes at 43 nanoseconds per day (c8). On
Vista, eight GPU nodes gave him "almost the same speed" (c9), after a lot of GROMACS optimization with TACC staff (c10).
The simulations point to the local detergent model, the SNAREs mixing the hydrophobic interiors of the two membranes
(c13, c14). Vista has 860 compute nodes and the GH200 Grace Hopper Superchip is the processor for the majority (c25,
c26). Each Frontera node held two Intel Xeon Platinum 8280 processors (c30, c32).

The fact check held it to its words. Vista's speed is Rizo-Rey's spoken "almost the same speed" and no figure, so no
frame draws a speed, a bar or an axis, and every frame that sets the two counts side by side says one tray per node,
drawn to illustrate. Vista's GPU node count was rejected (only 860 for all nodes and "the majority" exist), so the
eight raised cells on frame 7 stand for his eight inside 860 and nothing claims a count of GH200 nodes. One superchip
per node was rejected, so the GPU tray is drawn closed. Frontera's node count at retirement was rejected, so no frame
draws Frontera's full size. The membrane, the vesicle and the SNAREs are drawn to illustrate and never as the lab's
structure or a frame of its simulation.

Docket item tx-2026-0245, admitted this run. Places: Austin, Travis County, and Dallas, Dallas County.

## Why this treatment, and what was grafted

Base: THE MEASURE. One machined tray stands for one node. The same tray envelope is counted 64 times in brushed steel for
Frontera and eight times in black anodise for Vista, at one scale, so the eight to one reads before a word does. It is
the only hard comparison the claims allow, and drawing the unit keeps the speed out of the picture. In space (1, 6, 9)
the trays stand in open towers of eight on a raised floor; in plan (3, 7) they are a relief where every tray has a
chamfer, a lit edge and a cast.

Grafted from WHAT THE MACHINE WAS COMPUTING: the membrane as a section relief in the deck's own metals, steel heads, a
graphite core and four copper SNARE bundles (4), then the same section with its state moved, the two graphite cores run
together where the bundles stand (5). It is the only thing the deck can show that the machine was for.

Grafted from THE ROOM WHERE ONE MACHINE ENDS: the opened Frontera node at macro (2), Horizon's bay with its floor up and
its power whips run to a half filled tower (8), and the reverse angle that closes the deck on Frontera's 64 dark beyond Vista's
eight lit (9). The status light motif becomes the accent: cyan means a Vista GPU node and nothing else.

Dropped: a full server row (the subject this record draws most), a kit person (charged as a mannequin on nos. 69 to 71),
the hands at the GPU tray (the same risk), a superchip product shot (one superchip per node was rejected), a speed bar of
any kind.

## The world, and the laws that hold it

`floodlit`, staged, inside one TXT.interior machine hall with no window and no ceiling, the flood hung high and out of
frame. The key is a cold LED flood at azimuth -60, elevation 30: high on the upper left, so every lit edge faces left and
up and every cast runs to the lower right. The hall's walls stay in shadow. The reliefs read the same declaration and are
raked from the upper left. Type is light on the dark field. A wash only darkens.

## Palette

graphite raised floor #1A1C20, brushed stainless #9EA3A8 (as rendered, far darker in shadow), copper fins #B87A4B, black
anodise #0E1013, steel posts #3A3E44, hall wall #15171B, comal_lit #8FE0F0

A Central Texas machine hall at night: graphite, steel, copper and black anodise under one cold flood. The accent is
brand.yaml's comal_lit, the blue of the Comal spring, and it means ONE thing, a Vista GPU node. It sits on the black
tower on 1, the black row on 3, the pulled tray on 6, the eight raised cells on 7 and the eight lit trays on 9. Nothing
on Frontera and nothing on Horizon is cyan.

## The continuity devices

CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE, VALUE_ARC

1. **Motif evolution, the tray.** One tray envelope on every machine frame: the 64 steel and 8 black in towers (1), one
   steel tray opened (2), the 64 and 8 in plan (3), one black tray pulled out on its rails (6), eight black cells raised
   among 860 (7), Horizon's floor waiting for trays (8), and the 64 dark beyond the 8 lit (9). The membrane frames (4, 5)
   carry the same metals.
2. **Camera move, one hall.** A low three quarter on the towers (1), down into one tray (2), straight down on the floor
   (3), the section (4, 5), level at the black tower (6), straight down again (7), across Horizon's bay (8), and the
   reverse of the cover from behind the black tower (9).
3. **Value arc.** The flood pool is brightest on 1, held near black with lit edges on the reliefs, and the cyan count
   grows from one tower (1) to one pulled tray (6) to the lit eight (9) while Frontera's steel goes dark.

## The rotation

    FULL_BLEED  CLOSE_CROP  GRID  DIAGRAM  DIAGRAM  OBJECT_AND_CAPTION  DIAGRAM  SPLIT_HORIZON  CLOSE_CROP

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | MEDIUM, high three quarter, eye 2.15 m above the floor, 4.6 m back, fov 36 | eight open towers of eight chassis compute_tray in brushed stainless on steel corner posts, a block of two rows of four on the chassis raised_floor, one tower of eight black anodise trays forward right in the flood pool, each tray a rounded box with a perforated bezel, two handles and a lit chamfer, TXT.contact under every tower |
| 02 | MACRO, eye 0.42 m above the floor, looking down 55 degrees at one tray, fov 30 | one chassis compute_tray, cpu kind, lid off, two copper fin stacks of thin plates on copper bases, DIMM rows either side, a fan wall at the back, brushed stainless walls with a rolled lip, seated on a perforated raised floor tile, TXT.contact under it |
| 03 | AERIAL, orthographic material relief | an 8 by 8 block of steel tray tops and, across a wide groove, one row of eight black anodise tray tops with a cyan strip at each front edge, every top proud of a graphite carrier with a chamfer lit on the key side and a cast into its gutter |
| 04 | CLOSE, orthographic material relief | a membrane section of a flat bilayer and a vesicle's arching bilayer, steel head beads with high specular over a matte graphite core, raked from the upper left so each bead casts on its neighbour, four copper coiled bundles standing in the cleft and casting over both, the copper darkened in its grooves |
| 05 | CLOSE, orthographic material relief | the joined membrane section, steel head beads parted around one raised graphite core band, raked from the upper left so the band's lit edge and its shadow read, the four copper bundles casting over the heads, the copper darkened in its grooves |
| 06 | MEDIUM, eye 0.9 m, 1.7 m from the tower, fov 30 | the black tower of eight chassis compute_tray, the top tray pulled half out on two steel slide rails, its cyan front strip lit and its rails polished where the tray slides, TXT.contact under the tower |
| 07 | AERIAL, orthographic material relief | a field of 860 square graphite cells in 43 columns by 20 rows, matte with tooth in the albedo, raked from the upper left with square gutters in shadow, eight cells raised in black anodise with lit chamfers and cyan tops so only they throw long shadows, dust in the gutters |
| 08 | WIDE, eye 1.5 m, fov 34, horizon at y 560 | the chassis raised_floor, graphite laminate tiles with steel edges lit by the flood and a lifted row open to the dark plenum, TXT.contact under the tower, scuffs and dust along the tile seams, black power whips in TXT.tube, one chassis tray_tower half filled with unlit trays in the pool |
| 09 | CLOSE, eye 0.62 m, at tray height beside the black tower, fov 40 | the black tower of eight chassis compute_tray cropped by the right and bottom edges, eight cyan front strips stacked, and beyond it the eight steel towers unlit with only their tray lips catching the flood, TXT.contact under every tower |

Showstopper frame: 01, the black tower's eight cyan edges stacked in the pool with its contact and cast shadow running long
toward the camera, the eight steel towers stepping away into haze and the dark, near towers occluding far ones, every lip
rimmed cold.
Tonal arc: the brightest pool on 01, the copper fins catching hard on 02, the reliefs held near black and lit at their
edges on 03 to 05 and 07, the cyan peak on 06, the darkest frame on 08 with one half filled tower in the pool, and the lit eight
against a dark field on 09.
VALUE CUT: frame 4. The deck turns from the machine to what it computed.

---
```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "eight open towers of eight brushed steel compute trays receding on a raised floor, and one tower of eight black anodised trays with cyan front strips forward right in a cold flood pool"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#8FE0F0"
data_in_art: {figure: cpu_nodes, drives: 'the number of steel trays built, eight towers of eight, with gpu_nodes setting the black trays in the one forward tower'}
job: 'Set the whole comparison in one image, 64 trays against 8 at one scale, before a number is read.

  '
claims: [c7, c8, c9, c28]
numerals:
- {value_from: c8}
- {value_from: c9}
depth:
  eye: 2.15
  horizon: 360
  cues: [CAST_SHADOW, FORM_SHADING, OCCLUSION, RELATIVE_SIZE, LINEAR_PERSPECTIVE, AERIAL]
  subject_at: {X: 0.6, Z: 0}
composition: {structure: 'A high three quarter view. The eight steel towers stand as a block of two rows of four, left and behind, the black tower stands forward right of centre in the pool, so the eye meets the eight first and then counts the others behind it.

    ', bands: 'Top third, the dark hall wall with the kicker, hook and dek. Middle third, the tops of the towers with their lit lips and the far towers fading. Bottom third, the black tower''s lit base in the flood pool, the raised floor tiles and its long shadow running toward the camera.

    ', focal: the stack of eight cyan edges on the black tower}
art: {technique: 'physically based render of the chassis compute_tray towers on the chassis raised_floor inside a TXT.interior hall in the floodlit world, staged on every tower', why_this_technique: 'the claim is a count of physical machines, and rendered trays at one true size let a reader count units rather than read a chart', palette: 'brushed steel, black anodise, graphite floor, comal_lit', value_structure: 'Lightest is the flood pool on the floor and the lips of the near trays. Darkest is the hall wall and the far towers. Frame median L* planned at 16.

    '}
type:
  hook: "64 nodes on Frontera. 8 on Vista."
  dek: "Jose Rizo-Rey's lab at UT Southwestern Medical Center typically ran a simulation on 64 CPU nodes of TACC's Frontera. He says eight GPU nodes of Vista gave \"almost the same speed.\" One tray per node, drawn to illustrate."
  labels: []
verbatim: []
acceptance: ['the black tower stands at least 300 px tall at full size and owns at least an eighth of the frame area', eight distinct steel towers are countable at 432 px, 'exactly eight black trays are visible in the forward tower, each with a lit cyan front strip, and the frame fails if the black tower is missing', every tower casts a shadow to the lower right on the floor, no tower crosses a glyph of the hook or dek, the frame's median L* at 432 px is 30 or lower]
risks: ['equal height towers can read as speed bars, so the towers are open frames with gaps between trays and the dek says one tray per node']
```

```yaml
slide: 2
layout: CLOSE_CROP
primary_image:
  subject: "one Frontera compute tray with its lid off on a perforated floor tile, two copper heat sinks of thin fins, rows of memory either side and a fan wall at the back"
  rect: [0, 640, 1080, 710]
  bleeds: [left, right, bottom]
accent: "none"
data_in_art: {figure: xeons_per_node, drives: 'the number of copper heat sinks built in the open tray, one per processor'}
job: 'Show what one Frontera node was, made of metal, and say it is retired.

  '
claims: [c1, c2, c3, c24, c29, c30]
numerals:
- {value_from: c1}
- {value_from: c2}
depth:
  eye: 0.42
  horizon: 120
  cues: [CAST_SHADOW, FORM_SHADING, OCCLUSION, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'Looking down into the tray from its front left. The two copper fin stacks sit side by side in the lower middle, the memory rows run toward the back either side, the fan wall closes the far end. The tray is cut by the left, right and bottom edges.

    ', bands: 'Top third, the dark floor beyond the tray and the type. Middle third, the fan wall and the far ends of the memory rows. Bottom third, the two copper fin stacks lit hard by the flood, each fin casting a shadow on the next.

    ', focal: the two copper fin stacks}
art: {technique: 'physically based render of the chassis compute_tray in its open cpu state on a raised floor tile in the floodlit hall', why_this_technique: 'the claim is what a node was, and a macro render of its parts gives the reader a real object with copper and steel, where an icon would give a symbol', palette: 'brushed steel, copper, graphite, black fan plastic', value_structure: 'Lightest is the copper fin edges facing the flood. Darkest is the floor beyond and the inside corners of the tray. Frame median L* planned at 18.

    '}
type:
  hook: "More than eight million jobs"
  dek: "For most of its service life Frontera was the fastest academic supercomputer in the United States. TACC's executive director calls its more than seven years of production the longest run on any TACC system. Each node held two Intel Xeon processors."
  labels: []
verbatim: []
acceptance: ['the open tray owns at least half the frame area at 432 px', 'exactly two copper heat sinks are visible, and the frame fails if either is missing', the fins of each heat sink read as separate plates at full size, the tray's steel wall shows a lit lip on its key side, no fin or wall crosses a glyph of the hook or dek, the frame's median L* at 432 px is 30 or lower]
risks: ['thin fins can strobe at 432 px, so at most 14 fins per stack, crosswise to the light']
```

```yaml
slide: 3
layout: GRID
primary_image:
  subject: "a machined plate in plan holding an 8 by 8 block of steel tray tops and, across a wide groove, one row of eight black tray tops with cyan front strips"
  rect: [80, 470, 920, 800]
  bleeds: []
accent: "#8FE0F0"
data_in_art: {figure: node_ratio, drives: 'eight rows of steel trays against one row of black trays at equal row width, the cpu block built from cpu_nodes cells and the black row from gpu_nodes cells'}
job: 'Make the eight to one countable in plan, every tray the same size, so the ratio is an area a reader can see.

  '
claims: [c8, c9]
numerals:
- {value_from: c8}
- {value_from: c9}
depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]
composition: {structure: 'A plan. The 8 by 8 steel block fills the middle, a wide groove runs across under it, and the one black row sits under the groove at the same width. Labels sit left of each group with leaders.

    ', bands: 'Top third, bare graphite with the kicker, hook and dek. Middle third, the upper rows of the steel block with lit chamfers. Bottom third, the lower steel rows with lit chamfers, the groove in shadow and the black row with its cyan strips.

    ', focal: the black row of eight under the groove}
art: {technique: 'TXBENCH material relief of a graphite carrier holding steel and anodised tray tops, raked from the upper left', why_this_technique: 'the quantity is a count of identical units, and a parallel projection keeps every tray exactly the same size so the count is honest', palette: 'graphite, brushed steel, black anodise, comal_lit', value_structure: 'Lightest is the chamfer edges facing the key and the cyan strips. Darkest is the carrier and the gutters. Frame median L* planned at 14.

    '}
type:
  hook: "64 CPU nodes against 8 GPU nodes"
  dek: "On 64 Frontera nodes the 5.3 million atom simulation typically ran at 43 nanoseconds a day. Rizo-Rey says eight Vista GPU nodes gave \"almost the same speed.\" His account, not a benchmark. One tray per node."
  labels: ["64 CPU nodes, Frontera", "8 GPU nodes, Vista"]
verbatim: []
acceptance: ['the steel block spans at least 600 px wide at full size', 'the black row carries exactly eight trays and the steel block exactly 64, and the frame fails if either group is missing', every tray top shows a lit chamfer on its upper left edge and a cast into its gutter at full size, each label's leader ends on its own group within 24 px, the frame's median L* at 432 px is 30 or lower]
risks: ['72 identical units can read as blinds or a keyboard, so the trays are wider than tall, the gutters deep enough to cast into and no border frames the block']
```

```yaml
slide: 4
layout: DIAGRAM
primary_image:
  subject: "a section of two membranes in metal relief, a flat bilayer across the lower third and a vesicle's curved bilayer above it, steel heads outside, a graphite core inside, four copper coiled bundles bridging them"
  rect: [0, 470, 1080, 880]
  bleeds: [left, right, bottom]
accent: "none"
data_in_art: {figure: snares, drives: 'the number of copper coiled bundles bridging the two membranes'}
job: 'Show what the 5.3 million atoms were, a vesicle, a flat bilayer and four SNAREs, as one object a reader can name.

  '
claims: [c11, c12, c15]
numerals:
- {value_from: c8}
- {value_from: c11}
depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]
composition: {structure: 'A section. The flat bilayer runs edge to edge across the lower third, the vesicle''s bilayer arcs from the upper left and comes closest at the middle, and the four bundles stand in the cleft between them, casting to the lower right.

    ', bands: 'Top third, bare graphite with the type. Middle third, the vesicle''s arc and the tops of the bundles. Bottom third, the flat bilayer with its two rows of lit heads and its core in shadow.

    ', focal: the four bundles in the cleft}
art: {technique: 'TXBENCH material relief of a membrane section in steel, graphite and copper, raked from the upper left', why_this_technique: 'a section shows heads out and tails in, which no surface view can, and a relief keeps the drawing in the deck''s metals', palette: 'brushed steel heads, graphite core, copper bundles, black carrier', value_structure: 'Lightest is the top of each head bead and the bundle crests. Darkest is the core and the cleft. Frame median L* planned at 13.

    '}
type:
  hook: "A vesicle, a bilayer, four SNARE complexes"
  dek: "Rizo-Rey's simulations contain a vesicle, a flat bilayer and four SNARE protein complexes. The SNAREs let vesicles fuse with their target membranes. His research focuses on synaptic transmission. Drawn to illustrate."
  labels: ["vesicle", "flat bilayer", "SNARE complexes"]
verbatim: []
acceptance: ['the flat bilayer spans the full frame width and the membranes together own at least a third of the frame height at full size', 'exactly four copper bundles bridge the cleft, and the frame fails if any membrane or bundle is missing', each membrane shows two rows of heads with a darker core between them at full size, each label's leader ends on its own part within 24 px, the frame's median L* at 432 px is 30 or lower]
risks: ['head beads can read as ornament or a necklace, so they are packed, small and set in two rows with the core visible between']
```

```yaml
slide: 5
layout: DIAGRAM
primary_image:
  subject: "the same membrane section with the vesicle pressed onto the flat bilayer where the four copper bundles stand, the two outer head rows bend into each other round a fusion neck and the two graphite cores run together through it"
  rect: [0, 470, 1080, 880]
  bleeds: [left, right, bottom]
accent: "none"
data_in_art: {figure: snares, drives: 'the number of copper bundles ringing the place where the two cores join'}
job: 'Show the lab''s finding, the local detergent model, as a change of state on the same object.

  '
claims: [c13, c14, c34]
numerals: []
depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]
composition: {structure: 'The frame 4 section and bench. The vesicle''s arc now meets the flat bilayer in the middle, the outer head rows curl round a neck there and the two cores run through it as one, two bundles each side of it.

    ', bands: 'Top third, bare graphite with the type. Middle third, the vesicle''s arc pressed down. Bottom third, the merged core through the neck and the flat bilayer running out both edges, its heads casting shadow on the core.

    ', focal: the joined core between the bundles}
art: {technique: 'TXBENCH material relief, the same bench and materials as frame 4 with the contact changed', why_this_technique: 'the claim is a change in the same structure, and holding the bench and light constant makes the change the only thing that moves', palette: 'brushed steel heads, graphite core, copper bundles, black carrier', value_structure: 'Lightest is the raised joined core''s lit edge and the bundle crests. Darkest is the carrier. Frame median L* planned at 13.

    '}
type:
  hook: "SNAREs act as a local detergent"
  dek: "Rizo-Rey calls it the local detergent model of membrane fusion. In it the SNAREs catalyze mixing of the hydrophobic interiors of the two membranes. Drawn to illustrate, not a frame from the simulation."
  labels: []
verbatim: []
acceptance: ['the joined membrane section owns at least a third of the frame height at full size', 'the neck''s waist is at least 160 px wide at full size and its core continues the membranes'' own core', 'exactly four copper bundles are visible, two each side of the joined core, and the frame fails if the joined membrane section or the join is missing', the heads curl round the neck at full size, the frame's median L* at 432 px is 30 or lower]
risks: ['a raised band with hard edges read as a plug in round 1, so the neck carries the membranes'' own core height and ridges']
```

```yaml
slide: 6
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "the black tower of eight Vista trays with its top tray pulled half out on two steel slide rails, its cyan strip lit"
  rect: [120, 560, 760, 790]
  bleeds: [bottom]
accent: "#8FE0F0"
data_in_art: {figure: gpu_nodes, drives: 'the number of black trays built in the tower'}
job: 'Say the speed was work, a lot of GROMACS tuning with TACC staff, on the machine itself.

  '
claims: [c10, c33]
numerals: []
depth:
  eye: 0.9
  horizon: 600
  cues: [CAST_SHADOW, FORM_SHADING, OCCLUSION, RELATIVE_SIZE, AERIAL]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'The black tower stands left of centre on the raised floor with its top tray drawn toward the camera on its rails, the pulled tray reaches toward the camera. The flood comes from the upper left behind the tower.

    ', bands: 'Top third, the dark hall wall with the type. Middle third, the pulled tray and its rails. Bottom third, the tower''s lower trays with lit lips and its shadow on the floor.

    ', focal: the pulled tray's lit cyan strip}
art: {technique: 'physically based render of the chassis tray_tower in the floodlit hall, staged on the tower', why_this_technique: 'the claim is that work went into the speed, and an opened machine with its tray out reads as a machine being worked on without drawing a person', palette: 'black anodise, steel rails, comal_lit, graphite floor', value_structure: 'Lightest is the cyan strips and the pulled tray''s lip. Darkest is the wall and the tower''s shadowed side. Frame median L* planned at 12.

    '}
type:
  hook: "The speed took a lot of tuning"
  dek: "Rizo-Rey says reaching it on Vista \"required a lot of optimizations with GROMACS, with the help of people here at TACC.\" GROMACS is free and open source software for molecular dynamics."
  labels: []
verbatim: []
acceptance: ['the tower stands at least 420 px tall at full size', 'the tower carries exactly eight black trays and the top one is pulled out on visible rails, and the frame fails if the tower is missing', the pulled tray's cyan strip is lit, no part of the tower crosses a glyph of the hook or dek, the frame's median L* at 432 px is 30 or lower]
risks: ['a black tower in a dark hall goes to silhouette, so the rim from the flood catches every tray lip']
```

```yaml
slide: 7
layout: DIAGRAM
primary_image:
  subject: "a field of 860 low square cells in plan, 43 columns by 20 rows, with eight cells raised in black anodise with cyan strips casting long shadows"
  rect: [0, 580, 1080, 560]
  bleeds: [left, right]
accent: "#8FE0F0"
data_in_art: {figure: vista_nodes, drives: 'the number of cells in the field, with gpu_nodes setting the raised cells'}
job: 'Place his eight nodes inside the whole of Vista, so the reader sees how small a share of a public machine the work needed.

  '
claims: [c9, c25, c26, c28]
numerals:
- {value_from: c25}
- {value_from: c9}
depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]
composition: {structure: 'A plan. The field of cells fills the middle and lower frame, the eight raised cells stand together in a short row below centre, casting to the lower right across their neighbours.

    ', bands: 'Top third, bare graphite with the type. Middle third, the upper field. Bottom third, the lower field with the eight raised cells lit on their key edges and their long shadows.

    ', focal: the eight raised cells}
art: {technique: 'TXBENCH material relief of a graphite field of low tiles with eight raised anodised cells, raked from the upper left', why_this_technique: 'the claim is a part inside a whole, and identical cells at one size make 860 a field and eight a visible few', palette: 'graphite, black anodise, comal_lit', value_structure: 'Lightest is the cyan strips and the raised cells'' lit edges. Darkest is the field. Frame median L* planned at 10.

    '}
type:
  hook: "Rizo-Rey's 8 nodes, in Vista's 860"
  dek: "Vista has 860 compute nodes. TACC says the NVIDIA GH200 Grace Hopper Superchip is the processor for the majority. It pairs a Grace CPU with a Hopper GPU. One cell per node. His eight nodes are raised."
  labels: ["860 compute nodes", "his 8 nodes"]
verbatim: []
acceptance: ['the field spans at least 700 px wide at full size', 'each label''s leader ends on its own part within 24 px', 'the field holds exactly 860 cells and exactly eight are raised, and the frame fails if the raised cells are missing', only the raised cells throw casts longer than a cell, the frame's median L* at 432 px is 30 or lower]
risks: ['860 small cells can turn to texture at 432 px, which is acceptable only if the eight cast and nothing else does']
```

```yaml
slide: 8
layout: SPLIT_HORIZON
primary_image:
  subject: "one empty tower frame in the flood pool beside a row of tiles lifted open to the dark plenum, three unlit black trays at its foot and a fourth sliding in on its rails, every slot above dark and empty, black power whips running to it"
  rect: [80, 640, 920, 560]
  bleeds: []
accent: "none"
job: 'Say what comes next, Horizon in early operations with power and storage in and its AI hardware arriving.

  '
claims: [c4, c5, c6, c24]
numerals: []
depth:
  eye: 1.5
  horizon: 560
  cues: [LINEAR_PERSPECTIVE, CAST_SHADOW, FORM_SHADING, RELATIVE_SIZE, AERIAL]
  subject_at: {X: 0.4, Z: -1.5}
composition: {structure: 'A three quarter view from the left across the bay. The tower stands in the pool right of centre, its empty slots open to the dark, the whips run to its foot from the lower left. The hall above the floor line is dark and carries the type.

    ', bands: 'Top third, the dark hall with the type. Middle third, the tower''s empty upper slots against the dark. Bottom third, the open plenum in shadow, the whips lit along their tops and the near tiles.

    ', focal: the tray sliding into the tower}
art: {technique: 'physically based render of the chassis raised_floor with lifted tiles, TXT.tube power whips and a chassis tray_tower with five of its eight trays taken out and one sliding in, in the floodlit hall, staged on the tower', why_this_technique: 'the claim is a machine not yet installed, and the deck''s own tower half filled and unlit shows hardware going in without inventing any of it, and no tray is lit because cyan means a Vista node', palette: 'graphite floor, black whips, steel posts, black anodise', value_structure: 'Lightest is the tower''s lit posts and the floor in the pool. Darkest is the plenum and the hall. Frame median L* planned at 10.

    '}
type:
  hook: "Horizon is in early operations"
  dek: "Frontera's successor is in its first phase. TACC's executive director says its power infrastructure is complete and an exabyte-capacity storage system is in place. Initial deployment of its AI-focused hardware is underway."
  labels: []
verbatim: []
acceptance: ['the raised floor owns at least a third of the frame height at full size', 'the tower stands at least 300 px tall at full size', 'at least four empty slots and one tray sliding in read at 432 px, and the frame fails if the floor, the tower or the whips are missing', no tray is lit, the tower casts a shadow to the lower right, the frame's median L* at 432 px is 30 or lower]
risks: ['an empty bay reads as void, so the whips and the open row carry the foreground']
```

```yaml
slide: 9
layout: CLOSE_CROP
primary_image:
  subject: "the black tower of eight Vista trays seen level from tray height, its eight cyan strips stacked, at the right edge, and beyond it the eight steel towers unlit"
  rect: [500, 560, 580, 790]
  bleeds: [right, bottom]
accent: "#8FE0F0"
data_in_art: {figure: cpu_nodes, drives: 'the number of dark steel trays beyond, with gpu_nodes setting the lit black trays in front'}
job: 'Close on the consequence, Frontera dark and the same work on eight lit trays, and point to Horizon.

  '
claims: [c1, c8, c9, c21, c22, c23]
numerals:
- {value_from: c8}
- {value_from: c23}
depth:
  eye: 0.62
  horizon: 560
  cues: [CAST_SHADOW, FORM_SHADING, OCCLUSION, RELATIVE_SIZE, LINEAR_PERSPECTIVE, AERIAL]
  subject_at: {X: 0.6, Z: 0}
composition: {structure: 'The cover''s hall from tray height. The camera stands close beside the black tower, which fills the right half and is cut by the right and bottom edges. The steel towers recede beyond it to the left, unlit, only their lips catching the flood.

    ', bands: 'Top third, the dark hall with the type. Middle third, the far steel towers. Bottom third, the black tower''s stacked cyan strips, its lit edges and its shadow on the floor.

    ', focal: the stacked cyan strips}
art: {technique: 'physically based render of the chassis compute_tray towers from the cover''s hall, reversed, staged on the black tower', why_this_technique: 'the close is the consequence of the cover, and the same objects seen from the other side close the loop the reader opened', palette: 'black anodise, comal_lit, dark steel, graphite floor', value_structure: 'Lightest is the cyan strips. Darkest is the far towers and the hall. Frame median L* planned at 10.

    '}
type:
  hook: "Frontera is dark. The work moved."
  dek: "More than 130,000 U.S. researchers have used TACC's systems since 2001. For one of them, eight Vista GPU nodes gave \"almost the same speed\" as 64 on Frontera. An early Horizon user says it enters full production soon."
  labels: []
verbatim: []
acceptance: ['the black tower stands at least 500 px tall at full size', 'eight lit cyan strips are visible on the black tower, and the frame fails if the steel towers beyond are missing', the steel towers beyond carry no cyan, no tower crosses a glyph of the hook or dek, the frame's median L* at 432 px is 30 or lower]
risks: ['the dark towers can vanish entirely, so a cold rim from the flood catches their lips']
```
