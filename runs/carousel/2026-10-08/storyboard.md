# Storyboard, 2026-10-08
# "Software on the radio"

## The story, and what the fact check did to it

TxDOT launched the first phase of Project Nexus at Fort Worth Alliance Airport on September 10th (c1, c15),
the state's part of the federal eVTOL Integration Pilot Program it was picked for in March (c4). The FAA
picked eight projects from more than 30 proposals, across 26 states (c5 to c7), and called the kickoff the
first Texas demonstration under the program (c21) and the sixth location to launch (c3). The first phase
flies traditional aircraft, helicopters and fixed-wing planes (c13), and its first flights carry no
passengers and collect data and validate routes (c14). The pilot advances in phases over three years (c16),
with medical supplies or organs between rural facilities and Austin and San Antonio next (c17) and
passengers across the Texas triangle last (c18). The FAA says it will write new rules from the data (c12),
and more test flights were planned through the year (c23).

At the kickoff, by its own account, Merlin was an invited guest (c25) and demonstrated AI-powered air
traffic control communications, autonomous takeoff and landing and in-flight re-planning with its Merlin
Pilot (c26), narrated by its chief executive (c27), framed as reducing pilot workload (c28). Its release
calls its expectations of the software's capability and performance forward-looking (c31) and carries a
photo of a Cessna Caravan at Alliance Airport (c32). Joby said its own autonomous Caravan, J208, would stop
at AFW on September 10th on a coast to coast run (c36). The record carries the decision as tx-2026-0205.

**WHAT THE FACT CHECK CHANGED.**
- **Nobody says who was aboard.** No source says whether a pilot sat in Merlin's Caravan. The cockpit is
  never shown through, and every frame that raises it names the three releases it is absent from.
- **No result.** No source prints how the demonstration went. The deck says so and says whose words the
  capabilities are.
- **Neither TxDOT nor the FAA names Merlin.** Merlin's presence rests on its own release and one Dallas
  Innovates caption credited to TxDOT (c33).
- **The phases are not counted.** c16 says "in phases" and c17 "the next phases". No frame prints a phase
  count. The runway carries YEARS, the one interval the release states, counted from September 10th, and
  every frame drawing them says where the count starts.
- **The two Caravans are never shown together as a fact.** Joby's stop was a published schedule. Frame 3
  draws the pair and says no source places them side by side.
- **2029 is out.** It is in Dallas Innovates only and never the state's word.

## Why this treatment, and what was grafted

Three directors pitched THE RADIO CALL (one Caravan, its call to the tower drawn as one fine accent
thread), THE SCHEDULE (the runway read as the state's three years, the plane standing where today falls)
and TWO CARAVANS AND THE PAPER (two identical airframes and what three releases print about them).

- From THE RADIO CALL, the spine and the cover: the one thing Merlin says its software did that faces
  outward is the radio, so the deck opens on the Caravan close with the thread leaving its antenna, and
  frame 2 is the tower where it lands. The thread is gone at the close, where the FAA's data takes over.
- From TWO CARAVANS, the pair on frame 3, the record table as nine airfield lamps on frame 4 (one lit),
  the macro of the stopped propeller for "traditional aircraft" on frame 5, and the leaders on frame 6.
- From THE SCHEDULE, the close: the runway read as the state's three years, one edge lamp per day, the first
  28 lit up to where the plane stands on October 8th, and the eight threshold stripes for the eight projects on
  frame 8. Three year bars were tried first and collapsed into one line at the horizon in any true
  perspective, so the close counts days rather than years.
- Refused: the cabin interior (a new model the size of the hero, built against a deadline, which is the
  defect no. 34 was charged for in every round), the empty cockpit in any form, and a passenger count.

## The world, and the laws that hold it

**AN AIRFIELD IN NORTH TEXAS AT LAST LIGHT.** The chassis is `assets/js/deck/2026-10-08-nexus.js` and
every frame loads it. It declares `sky: lastLight` with the haze at #1E2536 and the light at azimuth -104
and elevation 6, the sun just down in the west. +x is east, +z is south, the runway runs along z centred
on x = 0, 30 m wide, its threshold at the south end.

1. **Start dark.** A near black sky, one warm seam in the west, the subject in a pool of light and the
   world behind it gone dark. Every exterior frame stages its subject.
2. **Type is light, on the dark sky band**, and every wash only darkens.
3. **The airfield's own lamps are the brightest things on the ground**: tungsten white edges, amber
   caution, green threshold. They are lights in the world, never the accent.
4. Every standing thing gets `TXT.contact`, every frame `TXT.weather`.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#1A1C21` | the DOM body behind the render |
| `accent` | `#8FE0F0` | comal_lit, the machine's own trace and the record's yes: the radio thread on 1 and 2, the lit lamp on 4, the three capability leaders' ends on 6, one threshold stripe on 8, the three year bars on 9. Absent on 3, 5 and 7 |
| `hook` | `#F2EEE6` | light type on the dark sky |
| `dek` | `#E4DFD5` | the dek |
| `rule` | `#E4DFD5` | the site line, the source line and the counter |

The world's lit materials: the Caravan's white paint over aluminium with a navy cheat line, dark glass,
spring steel gear, black satin blades with yellow tips; runway asphalt #3A3B3D with rubber in the
touchdown zone, faded paint #D9D6CC, jointed apron concrete; little bluestem straw in the infield
(#8A8058, #6E6A48); lamp white #FFE2A8, caution amber #E8A33A, threshold green.

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE, EDGE_TEASE

1. **Motif evolution.** The one Caravan changes state: taxiing with its lights on and the thread
   leaving it (1), its tail parked with the thread arriving at the tower (2), doubled (3), parked beyond
   the lamp record (4), the stopped propeller (5), broadside under the three leaders (6), absent from the
   map (7), lined up on the eight stripes (8), and rolling into the three years with no thread (9).
2. **Edge tease.** Frame 1's thread leaves by the right edge and frame 2's enters from the left and
   lands on the tower cab.
3. **Camera move.** Close at the nose (1), across the field (2), back for the pair (3), down to the lamps
   (4), in to the spinner (5), broadside on a long lens (6), up to the map (7), 30 m up over the threshold
   (8), down beside the runway's edge behind the plane (9).

## The rotation

    FULL_BLEED  SPLIT_HORIZON  OBJECT_AND_CAPTION  DIAGRAM  OBJECT_AND_CAPTION  CLOSE_CROP  MAP  FIGURE_SCALE  FULL_BLEED

Round 1's flow critic moved Merlin's three claims ahead of the record, so the reader meets what Merlin says
it showed (4) before the table of what the three releases print (5), and the record frame alone carries the
absence. The lamp table is declared as one object with its captions, because at thumb scale the lit apron and
its nine lamps read as one silhouette against the dark sky. The threshold's eight stripes are joined by the threshold bar into one figure of scale (8).

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | CLOSE, eye 1.1 m, 13 m off the left front quarter, horizon on the lower third | the Caravan's nose, cowling and wing root, lofted white skin with panel lines, rivet rows, the navy cheat line and exhaust soot aft of the stack, the turning disc, gear pants with a contact and grit on worn apron concrete, raked by the west key |
| 02 | WIDE, eye 1.6 m on the ramp looking north, horizon on the lower third | the Caravan's tail, fin and stabiliser, lofted tail cone with belly grime and the lit red beacon, the fin's west face raked, a contact at the tail wheel line; the tower's precast shaft and amber cab beyond |
| 03 | MEDIUM, eye 1.7 m, 34 m off the pair's front quarter | the two Caravans, one model at two seeds, each nose gear with contact and oil on jointed concrete, one shared pool |
| 04 | MEDIUM, eye 2.2 m, long lens broadside from the west | the Caravan side on, a lofted white skin with panel lines, rivet rows and the navy cheat line, lit along its whole west side by the low key, belly grime on the pod, contacts under all three wheels on the runway paint |
| 05 | CLOSE, eye 0.8 m over the apron, long lens | the nine lamp units, frangible dark stems and glass heads with contacts and long east casts on worn apron concrete, one head lit in the accent |
| 06 | MACRO, eye 2.0 m, 3.2 m off the spinner | the spinner and three twisted blades, modelled in eight tapered stations, black satin paint with yellow tips, raked by the west key along each leading edge, soot on the cowl aft of the stack, the nose gear's contact below |
| 07 | AERIAL, the state in TXGeo's Albers projection | the Texas outline as a lit edge on the dark, four lamp heads for the cities, Houston dimmer |
| 08 | AERIAL, 30 m up and 70 m south of the threshold | the eight threshold stripes on rubbered asphalt, worn paint, the Caravan lined up on them with its long east shadow across four |
| 09 | WIDE, eye 1.6 m on the west infield behind the threshold, looking up the runway | the runway's west edge with one lamp per day, the 28 elapsed lit in the accent on dark stems from the near corner up toward the Caravan, the later ones dark glass, the infield straw lit warm by the threshold flood, the Caravan lit at the depth of the 28th |

Showstopper frame: 01, the Caravan's nose close and low at last light with every light on, the disc turning and one cyan thread leaving its antenna for the dark
Tonal arc: dark and quiet through the ramp frames, lifting a little on 05 and 08 where lamps and paint fill the floor, darkest on the map at 07, closing on 09's lit run of days

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "the Caravan's nose, cowling, turning propeller disc and left wing root, close and low, every light on, the radio thread rising from the spine antenna and leaving by the right edge"
  rect: [0, 470, 1080, 880]
  bleeds: [left, right, bottom]
accent: "#8FE0F0"
job: >
  Put the machine in front of the reader at the moment its software would talk, and say in the first
  line whose account that is and which documents leave it out.

claims: [c1, c2, c25, c26]
numerals: []

depth:
  eye: 1.1
  horizon: 1010
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera kneels on the apron off the Caravan's left front quarter. The nose and the disc sit
    right of centre in the lower half, the left wing root and strut run off the left edge, the nose gear
    stands on the concrete in the lower third. The thread climbs from the spine and leaves by the right
    edge above the horizon. The type sits in the dark sky above.
  bands: >
    Top third, the near black sky and the hook and dek. Middle third, the wing's leading edge, the
    windshield and the thread climbing to the right. Bottom third, the cowling, the disc, the nose gear
    and the lit concrete under it going dark toward the camera.
  focal: "the lit west face of the cowling and spinner inside the turning disc"

art:
  technique: "physically based render, the chassis Caravan on the deck's apron, staged, with the radio path as one fine emissive tube"
  why_this_technique: "a plane reads as a plane only modelled, lit from one side and standing on its own wheels, and a radio call reads only as a line from one thing to another"
  palette: "white paint and navy cheat line, black satin blades, worn apron concrete, navy black sky, the one warm seam"
  value_structure: >
    Lightest is the lit cowling, the landing light and the seam. Darkest is the sky and the near
    concrete. Frame median L* planned at 5.0.

type:
  hook: "Software on the radio"
  dek: "Merlin says it demonstrated AI-powered air traffic control communications at TxDOT's Project Nexus kickoff on September 10th. Neither TxDOT's release nor the FAA's names Merlin. The plane is drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the Caravan's spinner, cowling, wing root and nose gear are modelled and lit, and the Caravan owns at least 40 percent of the frame"
  - "a fine cyan thread rises from the spine behind the far wing and leaves by the right edge, and it is the only accent on the frame"
  - "the nose wheel stands on the concrete with a dark contact under it"
  - "no wing, strut or thread crosses a glyph of the hook or the dek"
  - "the sky above the horizon is near black"

risks:
  - "the thread reads as a cable or a beam, so it stays one fine tube with no glow halo and the dek says it is drawn to illustrate"
  - "the disc ring reads as a target, so its tip ring stays faint"
```

```yaml
slide: 2
layout: SPLIT_HORIZON
primary_image:
  subject: "the Caravan's tail, fin and stabiliser near at lower left, the runway across the middle with its lamps, and the control tower's lit cab across the field where the thread lands"
  rect: [0, 700, 1080, 650]
  bleeds: [left, right, bottom]
accent: "#8FE0F0"
job: >
  Say where this happened and who launched it, and land the call where a call goes, the tower.

claims: [c1, c4, c15, c21]
numerals: []

depth:
  eye: 1.6
  horizon: 880
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: -6, Z: 12}

composition:
  structure: >
    The camera stands on the ramp behind the Caravan's tail looking north across the runway. The tail
    and stabiliser fill the lower left, cut by the left and bottom edges. The runway's lamp rows cross the
    middle band. The tower stands on the right third far off, its cab lit amber against the seam, and
    the thread enters from the left edge and lands on the cab glass.
  bands: >
    Top third, the dark sky and the type. Middle third, the horizon, the tower and the runway's lamps.
    Bottom third, the tail, the stabiliser and the lit ramp concrete.
  focal: "the tower's amber cab where the thread lands"

art:
  technique: "physically based render, the chassis Caravan and the chassis control tower on the deck's airfield, with the runway's edge lamp rows and the radio path"
  why_this_technique: "a radio call needs both ends in one place, and only a modelled field at true scale puts the tower where a pilot would see it"
  palette: "white tail and red beacon, amber cab glow, lamp white and caution amber, navy black sky"
  value_structure: >
    Lightest is the tail's lit west face, the lamps and the cab. Darkest is the sky and the infield
    beyond the runway. Frame median L* planned at 1.2.

type:
  hook: "Phase one began here"
  dek: "The Texas Department of Transportation launched the first phase of Project Nexus at Fort Worth Alliance Airport, as part of a federal pilot program for new aircraft. The FAA called it the first Texas demonstration under the program. The tower and the radio path are drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the Caravan's tail, fin and stabiliser are modelled with the beacon lit, and they own at least 25 percent of the frame"
  - "the tower stands on the right third with a lit cab, and the thread ends on the cab"
  - "the apron flood lights the ground under the gear, and its pool falls to the dark before the tower"
  - "the thread enters from the left edge, matching frame 1's exit"
  - "the hook reads 'Phase one began here'"

risks:
  - "the tower reads as a lamp post at its distance, so it stands near enough to read its cab and shaft"
```

```yaml
slide: 3
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "two identical unmarked Caravans parked on the apron in one pool of light, noses three quarters to camera, the nearer one large and the other just behind it"
  rect: [0, 620, 1080, 730]
  bleeds: [left, right, bottom]
accent: none
job: >
  Show that two companies each say they brought an autonomous Caravan, by their own accounts, and that the
  airplane itself is the ordinary part.

claims: [c32, c33, c36]
numerals:
  - computed_by: "out/2026-10-08/compute.py, caravans, one each in c32 and c36"

data_in_art:
  figure: caravans
  drives: the count of rendered Caravans, 2, one model at two seeds

depth:
  eye: 1.7
  horizon: 900
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera stands off the pair's front quarter. The near Caravan sits left of centre, the far one
    one plane back and to the right, the same heading, both in one pool. Mono labels sit under each on
    the dark concrete. The type sits in the sky.
  bands: >
    Top third, the sky and the type. Middle third, the two airframes wing to wing. Bottom third, the two nose gears and their pants standing on the lit jointed apron concrete, each with a dark contact and an oil stain, the shared pool fading to the dark at the edges, and the two mono labels on the concrete under the wheels.
  focal: "the two lit cowlings side by side, the same plane twice"

art:
  technique: "physically based render, the chassis Caravan twice in one staged pool"
  why_this_technique: "a count of two airplanes is two modelled airplanes, the same model, so a reader sees nothing outside tells them apart"
  palette: "white paint, navy cheat line, jointed concrete, navy black sky"
  value_structure: >
    Lightest is the two lit cowlings and wings. Darkest is the sky and the edges of the apron. Frame median L* planned at 10.7.

type:
  hook: "Two Caravans, by two companies' word"
  dek: "Merlin's release pictures its Caravan at Alliance Airport. Joby said J208, a Caravan with its autonomous flight technology, would stop there on September 10th. Each release speaks for its own aircraft. Both are drawn to illustrate, unmarked."
  labels: ["MERLIN'S CARAVAN", "JOBY'S J208"]

verbatim: []

acceptance:
  - "exactly two Caravans are modelled and lit, and together they span at least 70 percent of the frame width"
  - "neither airframe carries a registration, a logo or a livery"
  - "each label sits under its own airplane and crosses no wheel or strut"
  - "the nearer Caravan's nose wheel and the farther one's main gear stand on the concrete with contacts"

risks:
  - "the pair reads as a scene that happened, so the dek says no source places them together"
```

```yaml
slide: 4
layout: DIAGRAM
primary_image:
  subject: "the Caravan broadside on the runway, side on across most of the width, three leaders from Merlin's own words to the gear, the spine antenna and the wing, and a fourth to the cockpit glass"
  rect: [0, 600, 1080, 560]
  bleeds: [left, right]
accent: "#8FE0F0"
job: >
  Set Merlin's own three claims against the parts they would use, and name the one thing none of the
  releases says.

claims: [c26, c27, c31]
numerals:
  - computed_by: "out/2026-10-08/compute.py, the three capabilities counted from c26's own list"

data_in_art:
  figure: capabilities
  drives: the count of accent leaders, 3, each landing on its part

depth:
  eye: 2.2
  horizon: 1000
  cues: [LINEAR_PERSPECTIVE, CAST_SHADOW, AERIAL, RELATIVE_SIZE]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A long lens from the west so the side reads nearly as an elevation. The Caravan spans the width in
    the lower middle. Three labels stand above it with leaders that end on their parts, and a fourth
    label below names the absence at the cockpit glass.
  bands: >
    Top third, the type. Middle third, the labels and the wing. Bottom third, the belly pod and the spring steel main gear with their pants standing on the runway's faded edge paint, the dark contacts under the wheels, the wheels' shadow running east on the lit asphalt, and the absence label below.
  focal: "the lit side of the fuselage and the three leader ends"

art:
  technique: "physically based render, a long lens profile of the chassis Caravan, with DOM SVG leaders landing on projected part coordinates"
  why_this_technique: "a claim about what parts did reads only when each leader lands on the part"
  palette: "white side and navy cheat line, runway paint, cyan leader ends, navy black sky"
  value_structure: >
    Lightest is the lit side of the fuselage and the wing. Darkest is the sky. Frame median L* planned at 1.5.

type:
  hook: "Three things Merlin says it showed"
  dek: "Merlin says the demonstration, narrated by its chief executive, showed the Merlin Pilot can safely and effectively perform responsibilities traditionally managed by human pilots. Its release calls its expectations forward-looking."
  labels: ["AUTONOMOUS TAKEOFF AND LANDING", "AI-POWERED AIR TRAFFIC CONTROL COMMUNICATIONS", "IN-FLIGHT RE-PLANNING AND THREAT AVOIDANCE"]

verbatim:
  - c26: "AUTONOMOUS TAKEOFF AND LANDING"
  - c26: "AI-POWERED AIR TRAFFIC CONTROL COMMUNICATIONS"
  - c26: "IN-FLIGHT RE-PLANNING"

acceptance:
  - "the Caravan spans at least 75 percent of the frame width, side on"
  - "each of the three leaders ends on its part, the main gear, the comm blade on the spine and the wing root"
  - "the frame carries no absence label, because the record frame after it carries the absence alone"
  - "no leader crosses a glyph"

risks:
  - "a leader stopping in the air looks like one reaching a part, so every leader's end is declared in __txLeaders"
```

```yaml
slide: 5
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "nine airfield edge lamps in a three by three block on the apron, one head lit in the accent"
  rect: [100, 620, 980, 560]
  bleeds: [right]
accent: "#8FE0F0"
job: >
  Put the record in front of the reader as a table they can count: three releases, three questions,
  one yes.

claims: [c1, c2, c25, c26, c31, c32]
numerals:
  - computed_by: "out/2026-10-08/compute.py, record_cells and record_cells_yes"

data_in_art:
  figure: record_cells
  drives: the count of rendered lamp units, 9, and record_cells_yes sets the 1 lit head

depth:
  eye: 0.8
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, TEXTURE_GRADIENT, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A long lens from just above the apron. The nine lamps stand in a block across the lower middle, rows
    receding, columns under three mono heads, row labels at the left. The one lit head is in the first
    row, Merlin's column. The Caravan's nose stands at the back of the pool, softened by the stage.
  bands: >
    Top third, the sky and the type. Middle third, the column heads, the far rows and the Caravan's nose.
    Bottom third, the near row of lamp stems and glass heads standing on worn apron concrete with grime in its saw cut joints, each lamp throwing a long east shadow across the slab toward the right edge, the foreground texture of the concrete lit by the pool.
  focal: "the one lit lamp head and its glow on the concrete"

art:
  technique: "physically based render, an isotype of nine chassis lamp units on the deck's apron"
  why_this_technique: "a table of yes and no reads at a glance as lamps on or off, in the airfield's own furniture"
  palette: "dark stems, glass heads, worn concrete, one cyan head, navy black sky"
  value_structure: >
    Lightest is the one lit head and its glow, and the concrete in the pool. Darkest is the sky and the
    eight dark heads. Frame median L* planned at 13.5.

type:
  hook: "What three releases print"
  dek: "A lamp is lit where a release says it. Only Merlin's names its Caravan, in a photo caption. None of the three says whether a pilot was aboard, and none prints a measured result."
  labels: ["TXDOT", "FAA", "MERLIN", "NAMES THE CARAVAN", "PILOT ABOARD", "PRINTS A RESULT"]

verbatim: []

acceptance:
  - "nine lamp stems and heads are modelled with contacts, and exactly one head is lit"
  - "the lit head sits in the MERLIN column and the NAMES THE CARAVAN row"
  - "the near row's lamps stand at least 60 px tall at 432 px"
  - "the column and row labels read and cross no stem"

risks:
  - "the lit glow blooms over its own column head, so the head sits above the far row"
```

```yaml
slide: 6
layout: CLOSE_CROP
primary_image:
  subject: "the Caravan's stopped three blade propeller, spinner and cowling inlet, close, cut by the right and bottom edges"
  rect: [100, 800, 980, 550]
  bleeds: [right, bottom]
accent: none
job: >
  Say what the state's first phase actually flies, and show that the airplane is the traditional part.

claims: [c13, c14]
numerals: []

depth:
  eye: 2.0
  horizon: 1100
  cues: [CAST_SHADOW, OCCLUSION, AERIAL, RELATIVE_SIZE]
  subject_at: {X: 0, Z: 6}

composition:
  structure: >
    The camera stands off the nose's left quarter and close. The spinner sits right of centre, a blade
    rising to the upper left, a blade falling off the bottom edge. The wing's leading edge crosses the
    top of the image band. The far field sits low under the cowl so the frame keeps its horizon.
  bands: >
    Top third, the dark sky and the type. Middle third, the spinner, the blades and the wing's edge.
    Bottom third, the white cowl's lower curve with its dark inlet and exhaust soot, the nose gear leg and its pant standing on the apron with a contact, its shadow and the pool's light falling off toward the dark foreground.
  focal: "the lit leading edge of the rising blade and the spinner's lit side"

art:
  technique: "physically based render, the chassis propeller rebuilt as twisted tapered blades, close"
  why_this_technique: "the propeller is the one part of the plane that says ordinary airplane at a glance"
  palette: "black satin blades, yellow tips, white spinner and cowl, soot"
  value_structure: >
    Lightest is the spinner's west side and the blade's lit edge. Darkest is the sky and the inlet.
    Frame median L* planned at 1.1.

type:
  hook: "Phase one flies traditional aircraft"
  dek: "TxDOT says the first phase tests helicopters and fixed-wing planes across the state, and that its first flights carry no passengers. The flights collect data and validate routes."
  labels: []

verbatim: []

acceptance:
  - "the spinner, at least two blades and the cowl inlet are modelled and own at least 35 percent of the frame"
  - "the blades show taper and twist, never a flat plank"
  - "the cowl and the lower blade run off the bottom edge on the dark, the crop closing on the propeller"
  - "the hook reads 'Phase one flies traditional aircraft'"

risks:
  - "the blades read as planks at close range, so they are built in eight twisted stations"
```

```yaml
slide: 7
layout: MAP
primary_image:
  subject: "Texas from TXGeo's Albers projection as a stone slab lit at its west edge, its 254 county lines cut in, four city lamps, Houston dimmer, Alliance marked"
  rect: [120, 540, 880, 740]
  bleeds: []
accent: none
job: >
  Say where the program means to fly next, in the FAA's words, and which city is only eventually.

claims: [c8, c9, c15]
numerals:
  - computed_by: "out/2026-10-08/compute.py, cities counted from c8's own list"

data_in_art:
  figure: cities
  drives: the count of city lamp marks, 4, three full and one dim

composition:
  structure: >
    The state fills the frame's middle, its west edge lit. The four city lamps stand at TXGeo's places.
    Houston is a dim ring marked eventually. A small mark at Fort Worth names Alliance. The type sits
    above.
  bands: >
    Top third, the type. Middle third, the Panhandle and the cities. Bottom third, the Hill Country and the south of the state as the dark slab's interior, the coastline's lit edge running down to the border, and the one dim ring for Houston near the coast.
  focal: "the cluster of lamps in the triangle"

art:
  technique: "TXGeo Albers cartography on the canvas bench, the outline as a lit edge, cities as the airfield's lamp heads"
  why_this_technique: "a list of cities is a map, and the lamps carry the airfield's light into it"
  palette: "lamp white, a warm edge, navy black"
  value_structure: >
    Lightest is the city lamps and the lit west edge. Darkest is everything else. Frame median L* planned at 1.9.

type:
  hook: "Dallas, Austin, San Antonio, then Houston"
  dek: "The FAA's selection names Archer, BETA, Joby and Wisk as the Texas project's partners, and Merlin is not among them. It says they will support regional flights connecting Dallas, Austin and San Antonio, and eventually Houston."
  labels: ["DALLAS", "AUSTIN", "SAN ANTONIO", "HOUSTON, EVENTUALLY", "ALLIANCE"]

verbatim: []

acceptance:
  - "the outline is TXGeo's, never hand drawn, and spans at least 65 percent of the frame width, the height the dek leaves setting the fit"
  - "four city marks stand at TXGeo places, and Houston's is visibly dimmer"
  - "no route line is drawn between the cities"
  - "the Texas outline is drawn as a lit edge with four lamp heads, and the state spans at least 65 percent of the frame width at 432 px"

risks:
  - "the one frame without the hero reads as a break, so the cities are the airfield's own lamp heads"
```

```yaml
slide: 8
layout: FIGURE_SCALE
primary_image:
  subject: "the runway threshold from 17 m up, eight painted threshold stripes joined by the threshold bar, one in the accent, the Caravan lined up beyond them with its long shadow running east"
  rect: [0, 560, 1080, 700]
  bleeds: [left, right]
accent: "#8FE0F0"
job: >
  Put Texas in the federal program at its true size, one of eight, and say what the data is for.

claims: [c3, c5, c6, c7, c12]
numerals:
  - value_from: c5
  - value_from: c6
  - value_from: c7

data_in_art:
  figure: projects
  drives: the count of threshold stripes, 8, one painted in the accent

depth:
  eye: 30
  horizon: 330
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: -20}

composition:
  structure: >
    From above and behind the threshold, the stripes cross the lower middle, four either side of the
    centreline. The Caravan sits lined up on them, nose north, its shadow running east across the
    stripes. The runway runs on to the dark at the top of the image band.
  bands: >
    Top third, the type and the dark beyond the runway's end. Middle third, the Caravan and the stripes.
    Bottom third, the near ends of the eight painted stripes on rubbered asphalt, worn and cracked, the row of green threshold lamps glowing across them, the plane's long shadow lit across them, and the infield straw's texture at both edges.
  focal: "the one accent stripe beside the lit airplane"

art:
  technique: "physically based render from above, the chassis runway's threshold and the Caravan, staged on both"
  why_this_technique: "a count of eight is eight painted things, and a runway already carries them"
  palette: "faded white paint on rubbered asphalt, one cyan stripe"
  value_structure: >
    Lightest is the stripes and the airplane in the pool. Darkest is the sky and the runway's end.
    Frame median L* planned at 11.3.

type:
  hook: "One of eight"
  dek: "The FAA picked eight projects across 26 states from more than 30 proposals, and says the Texas kickoff made Texas the sixth place to launch. It will use the data to write new rules. Each stripe is one project, drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "exactly eight threshold stripes are countable at 432 px, and exactly one is in the accent"
  - "the Caravan is modelled and lined up on the centreline with its shadow across at least two stripes"
  - "the threshold bar joins the eight stripes into one painted figure"
  - "the stripe band fills at least 20 percent of the frame height and the Caravan spans at least 30 percent of the frame width at 432 px"
  - "the sky shows above the runway's far end"

risks:
  - "eight stripes merge at thumb scale, so the camera is high enough to separate them"
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: "from the west infield behind the threshold, one lamp along the runway's west edge for every day of the three years counted from September 10th, the 28 lit in the accent running from the near corner up to the Caravan at day 28, the rest dark glass running on into the dark"
  rect: [0, 620, 1080, 520]
  bleeds: [left, right]
accent: "#8FE0F0"
job: >
  Show how much of the state's own schedule has happened, in the schedule's own unit, and end on what
  comes next.

claims: [c1, c2, c16, c18, c23, c25]
numerals:
  - computed_by: "out/2026-10-08/compute.py, elapsed_days and schedule_days counted from September 10th, 2026"

data_in_art:
  figure: elapsed_days
  drives: the count of lit accent lamps, 28, and schedule_days sets the 1096 lamps along the edge, so the 28th stands where plane_m, 76.6 m, puts the Caravan

depth:
  eye: 1.0
  horizon: 980
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: -77}

composition:
  structure: >
    The camera stands just west of the runway's west edge, low, looking north. The lit day lamps run from
    the bottom left corner up the edge toward the horizon, nearer ones larger, and stop beside the
    Caravan, which rolls tail to camera on the right of centre. The unlit lamps run on past it into the
    dark. The type sits in the sky above the warm seam.
  bands: >
    Top third, the type in the sky. Middle third, the runway's far reach, the bars and the plane.
    Bottom third, the green threshold lamps glowing across the frame on their dark stems, the near asphalt with its touchdown rubber and sealed cracks, the white edge lamps starting their run at both edges, and the plane's shadow lit long in the foreground.
  focal: "the lit tail of the Caravan and the first bar beyond it"

art:
  technique: "physically based render along the chassis runway, 1,096 instanced day lamps on the west edge, the first 28 unfogged in the accent"
  why_this_technique: "a count of days reads as that many lamps, the airfield's own way of marking a length, and the few lit ones against the long dark row are the share of the schedule that has passed"
  palette: "dark straw, asphalt, the lit cyan day lamps, the dark glass of the days to come, the warm seam"
  value_structure: >
    Lightest is the lamps, the bars and the plane's landing light. Darkest is the sky and the runway's
    far end. Frame median L* planned at 2.5.

type:
  hook: "28 days into the three years"
  dek: "TxDOT says the pilot runs in phases over three years, with passengers last. Counted from September 10th, 28 of 1,096 days had passed by October 8th. More test flights were planned through the rest of the year. None of the three releases says whether a pilot was aboard at the kickoff."
  labels: ["28 DAYS"]

verbatim: []

acceptance:
  - "a row of lamps runs along the runway's west edge, the 28 nearest lit in the accent, running from the near corner toward the Caravan"
  - "the Caravan is modelled with its lit beacon and nav lights and spans at least 30 percent of the frame width at 432 px"
  - "the DAY 28 label sits above the last lit lamp and crosses no lamp"
  - "the unlit lamps continue past the lit run as dark glass toward the horizon"
  - "the lit run of days enters from the right edge and climbs toward the horizon, with the infield straw in the lower half"
  - "the runway's lit run of day lamps spans at least 60 percent of the frame width at 432 px"
  - "the sky above the horizon is near black with the warm seam low at the left"

risks:
  - "the bars vanish in the stage's fog, so their material is unfogged"
```
