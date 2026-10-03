# Storyboard, 2026-10-03
# "Not closed yet."

## The story, and what the fact check did to it

Kodiak AI named Interstate 45 between the Dallas-Fort Worth and Houston areas as its first
driverless long-haul lane on September 25th (c1, c3), and plans unsupervised service there by the
end of the year (c2, c13). IKEA is the launch shipper (c20), on a 219 mile driver-out leg between
Kodiak's Houston and Dallas-area facilities (c23) that is part of IKEA's 292 mile route from its
Baytown distribution center to its Frisco store (c24). Kodiak says its trucks now complete runs
between its Lancaster hub and Houston without human intervention, and that on those runs the
safety observer never touched the wheel (c5, c6). The observer comes out only after Kodiak closes
its safety case (c38, c18), a structured argument backed by evidence that its driver can operate
safely in a defined environment (c10). Kodiak measures that case by the share of its claims and
evidence that are materially complete (c8): 84% as of February, 86% through April, 91% as of July
(c27) and 93% at the end of August (c7, c26). It expects 100% by year end (c9). Its release says
its forward looking statements are not predictions of actual performance (c17). The state's
authorization costs nothing and does not expire (c34, c35), TxDMV says the law doesn't let it
require crash history (c37), and anyone can send its Enforcement Division a concern (c36).

The record carries this as tx-2026-0198, and the state's authorization as tx-2026-0188.

**WHAT THE FACT CHECK CHANGED.**
- **The observer is never placed aboard in the present tense.** The pages say the safety observer
  never touched the wheel on these runs (c6). No frame says the observer is still in the cab.
- **The 3.5 million miles are company-wide** and never miles on this route (c12). The deck doesn't
  print them.
- **The measure is never safety.** It is the share of the safety case's claims and evidence that
  Kodiak calls materially complete (c8). It is never "93 percent safe" or "93 percent ready".
- **Every figure is the company's own** and frame 7 says so.
- **The van's load is a drawing of the measure**, one stack per percentage point, and frames 1, 5
  and 6 say so. It is never a claim about what any Kodiak trailer carries.
- **The hub is drawn with the kit warehouse** and is not a likeness of Kodiak's Lancaster facility.

## Why this treatment, and what was grafted

Three directors pitched THE MACHINE, THE CASE and THE LANE. Two of them chose the same hero
without seeing each other: a 53 ft van loaded to 93 of 100 places with the last seven open. THE
MACHINE's version is the spine, because it carries Kodiak's own verb. The company says it will
CLOSE its safety case (c38, c18), and a van has exactly one part that closes when its load is
complete, its rear doors. So the van is loaded from the nose, one stack per point, and its doors
stay folded open on seven bare places.

- From THE MACHINE: the spine, the van divided into 100 places on its floor, the road frames that
  show what the truck already does, the section with floor tapes where the load stood, the
  roofless count from a crane, and the macro out through the doors.
- From THE CASE: the honest unit, said on the cover and on frames 5 and 6, and the warning that the
  load must never read as freight, capacity, miles or safety.
- From THE LANE: the corridor read in its own ground, Blackland clay and cotton stubble at the north
  end and post oak country further south, and a Texan at the van at the close.
- Refused: THE CASE's warehouse interiors (two new kit models and two interior frames for one
  count), THE LANE's painted band on the trailer (it reads as livery), its 89 hay bales and its
  canvas map (the hero would not be rendered there), and every cab interior shot, which deck no. 34
  spent three frames on.
- Refused from all three: any printed numeral inside the render.

## The world, and the laws that hold it

**THE LANCASTER END OF INTERSTATE 45 ON AN OCTOBER MORNING, A NORTHER LYING NORTHWEST.** The
chassis is `assets/js/deck/2026-10-03-norther.js` and every frame loads it. It declares
`sky: stormFront`, tuned to a Blackland green-grey haze (0x8c9088) rather than the preset's West
Texas dust, with the fog thinned so the world reads past a kilometre. One light: the sun at
azimuth 68, elevation 11, low in the east southeast under the trailing edge of the front. The
table gives stormFront to "a deadline", and this story is a company's own year-end date on an
argument it has not finished. The front stays behind the truck in every frame and nothing about it
is rain, lightning or menace.

+x is east and -z is north. At the hub the van's rear faces east, so the low sun shines straight
into the open doors. On the highway the truck runs south (+z), so its driver side faces the sun.

**THE HERO OBJECT.** One Class 8 tractor and one 53 ft dry van. The tractor is the kit's
`semi_truck` with `sensors:'full'` and no trailer, white, no lettering. The van is `dry_van`, a kit
addition in the chassis: 16.15 m long, 2.59 m wide, 4.10 m tall, floor 1.24 m up, interior divided
into 100 places (50 rows of 0.318 m by 2 files), swing doors that fold flat against the sides,
and options to lift the roof or take off the near wall. `carton_stack` (a kit addition) stands in
a place, kraft flat-pack cartons on edge. `load_bar` (a kit addition) is a pair of decking beams
across the load face in the accent.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#1C2027` | the DOM body behind the render |
| `accent` | `#B4664F` | dusk_ember in brand.yaml, the iron red of a post oak road cut and the working colour of a decking beam. Only ever the load bar across the load face, and frame 5's AUG 93 label |
| `hook` | `#F7F3EC` | the hook, light on the slate front |
| `dek` | `#EEE9E1` | the dek |
| `rule` | `#E8E3DA` | the site line, the source line and the counter |

The world's own colours are lit materials: the norther's slate deck (#353C4A), Blackland vertisol
(#2A2824), October cotton stubble (#B8A888), white painted van steel warm in the low sun, kraft
carton (#B79A70), a laminated oak trailer floor (#7B5A3D), chrome.

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE, VALUE_ARC

1. **Motif evolution.** The van's load is the progress indicator. Open and lit at the hub (1),
   closed and running (2 to 4, 7), in section with the tapes where it stood (5), counted from above
   (6), seen from inside out over the bare places (8), beside a person (9).
2. **Camera move.** The same van from five sides at the hub (doorway, section, crane, inside, a
   person's height), and the same truck from three road positions moving south.
3. **Value arc.** The road under the front dims through 3 and 4. The section on 5 is the high
   point. The turn on 7 is a DECLARED cut to the deck's darkest frame, the closed doors running
   away, because it is where the reader's trust in the figures changes. The hub comes back up to its
   mid value on 8 and 9. Revised after round three, when 7 was recomposed behind the rig and
   measured 19.7. Exposure is set per frame, measured by deck_coherence.

## The rotation

    FULL_BLEED  SPLIT_HORIZON  CLOSE_CROP  FULL_BLEED  DIAGRAM  FULL_BLEED  FULL_BLEED  OBJECT_AND_CAPTION  FIGURE_SCALE

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | WIDE, standing eye 1.7 m at the van's rear three quarter, horizon on the lower third | the 53 ft van, white painted panels lit warm on their flank by the 11 degree sun and into the open doorway, road grime on the lower rails and mud flaps from TXT.weather, a contact under the tandems and the landing gear on jointed concrete, a long soft cast toward the front |
| 02 | WIDE, long lens at 1.2 m from 150 m, horizon at 0.55 of the height | the disked Blackland field in the lower band, a TXT.ground dirt surface tuned to vertisol black with clods, cotton stubble rows raking in the low sun, the truck side on along the highway above it |
| 03 | CLOSE, chase car at 2.0 m, 3.5 m off the cab door | the tractor's cab and long hood, the kit's white paint with road film low on the door and a chrome grab rail catching the sun, the roof sensor bar's black housing with its lit band, contact shadow of the tyres on the concrete lane |
| 04 | MEDIUM, 4.9 m over the sleeper looking south past the roof sensor housing | the concrete carriageway ahead, tyre polish in the wheel paths and dark joints, the white roof fairing and black lidar housing at the bottom edge with grime in the seams, delineator posts and the shoulder grass under the cloud |
| 05 | WIDE, long lens near parallel at 1.6 m square to the van | the van in section, oak floor and white scuff liner with E-track rails, 47 near kraft stacks with seeded lean and flute edges, the aluminium cut edges, a contact on the apron, the front's sky above |
| 06 | AERIAL, crane at 22 m, 46 m off, horizon on the upper third | the roofless van's load, 93 kraft stack tops lit on their top faces with shadow lines between rows, seven bare oak places scuffed with wheel tracks, the van's cast on the apron joints |
| 07 | CLOSE, low at 0.9 m, the tractor's front three quarter cropped by the frame, into the sun | the tractor's front, chrome grille and bumper radar with road grime at the bumper, headlights lit, the white hood rim lit by the sun behind it, Houston hazed far off |
| 08 | MEDIUM, standing eye 1.95 m, 8.5 m square behind the open doors | the oak floor of the seven bare places, laminated oak strips in a varnished wood material raked gold by the sun through the doorway, worn dark in the wheel tracks and scuffed with nail lines, the load bar's rubber pad pressed on the white liner at the near left |
| 09 | MEDIUM, 1.4 m, 8 m off the open rear | the open rear and the swung door, aluminium frame with locking bars and cam keepers, the door's inner face scuffed, a contact under the bumper and the person's feet, the person lit from the east on the camera's side |

Showstopper frame: 01, the open van glowing against the slate front, its depth built from the lit doorway against the darkest sky, the truck receding in a long soft cast, the warehouse in green-grey haze and the black prairie to a horizon on the lower third
Tonal arc: the hub opens mid dark on 01, the road frames dim under the front on 03 and 04, the section on 05 is the high point, the turn on 07 is a declared cut to the darkest frame, and the hub comes back up to mid value on 08 and 09.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "a white 53 ft van and its tractor on a concrete truck court, the rear doors folded flat against the sides, the low sun shining into the doorway onto a wall of kraft carton stacks that stops short of the doors, an ember decking beam across the face"
  rect: [0, 520, 1080, 830]
  bleeds: [left, right, bottom]
accent: "#B4664F"
job: >
  Stop the scroll on the open van and say the whole story in the hook, the lane is named and the
  case that lets the observer out is not closed.

claims: [c3, c7, c8, c38]
numerals:
  - value_from: c7

data_in_art:
  figure: arm_aug
  drives: mark count, the number of carton stacks placed in the van from the nose, with arm_open bare places left at the doors

depth:
  eye: 1.7
  horizon: 900
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A standing eye at the van's rear three quarter, so the open doorway faces the reader and the
    van's long flank recedes away to the left toward the tractor and the dark front.
  bands: >
    Top third, the slate shelf cloud holding the kicker and the hook. Middle third, the dek over
    the front, then the van's roofline and the lit doorway. Bottom third, the doorway's lit carton
    face and bare floor, the tandem axles and mud flaps on their contact shadows, the court's
    joints running toward the lens.
  focal: "the lit doorway, the kraft wall and the bare floor in front of it"

art:
  technique: "physically based render through txthree.js in the deck's stormFront world, the chassis's dry_van, carton_stack and load_bar, the kit semi_truck tractor and warehouse"
  why_this_technique: "the measure is a share of an argument, and a lit van loaded from the nose turns a share into a load a reader sees stop short of the doors"
  palette: "slate front, warm white steel, kraft, oak, black prairie, one ember beam"
  value_structure: >
    Lightest is the lit doorway and the van's sunlit flank. Darkest is the shelf cloud over the
    front and the court under the van. Frame median L* planned at 38.

type:
  hook: "Not closed yet."
  dek: "Kodiak AI named Interstate 45 from Dallas to Houston its first driverless long-haul lane. It says it closes its safety case before that launch, and at the end of August it called 93 percent of it complete. This van is loaded to that measure, one stack per point."
  labels: []

verbatim: []

acceptance:
  - "a white van with its rear doors folded open reads at 432px as one object owning the lower half of the frame"
  - "kraft carton stacks fill the van from the far end and stop short of the doors, with bare floor visible between the last stack and the doorway"
  - "an ember beam (#B4664F) crosses the load face and no other object in the frame is ember"
  - "the van's tyres touch the court with a contact shadow darker than the concrete beside them"
  - "the court runs back to a hazed horizon behind the van, clear of the dek"
  - 'the hook reads "Not closed yet."'
  - "the frame's median L* at 432px is between 30 and 46"

risks:
  - "the seven bare places are a sliver at this distance, so the lit doorway as an AREA is the focal and frame 6 carries the count"
```

```yaml
slide: 2
layout: SPLIT_HORIZON
primary_image:
  subject: "the whole truck side on at speed along Interstate 45, doors closed, sensors on the roof and mirrors, the low sun on its east side, the slate front behind it, a fencerow of cedar elms in haze"
  rect: [0, 250, 1080, 520]
  bleeds: [left, right]
accent: none
job: >
  Name the lane, its length and its shipper, with the truck doing the thing it already does.

claims: [c2, c3, c20, c23, c24]
numerals:
  - value_from: c23

depth:
  eye: 1.2
  horizon: 400
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: -150}

composition:
  structure: >
    A long lens from a rise in the field puts the truck side on across the upper frame on the
    highway, and the October prairie between the shoulder and the lens is the type's ground.
  bands: >
    Top third, the slate front, the haze and the truck side on with the cotton stubble beyond
    the road. Middle third, the near prairie, bunchgrass in October straw running from the
    shoulder toward the lens. Bottom third, the same bunchgrass at its tallest, each clump lit on
    its east face with shadow between the clumps, darkest under the hook and dek.
  focal: "the truck's sunlit east side against the dark front"

art:
  technique: "physically based render on a long lens, kit highway, crop_rows and cedar_elm, TXT.ground dirt as vertisol"
  why_this_technique: "a lane is a place, and the side on truck on its own road at its own scale says the leg is being driven"
  palette: "black clay, straw stubble, slate, warm white"
  value_structure: >
    Lightest is the truck's lit side. Darkest is the disked field and the front. Frame median L* planned at 20, revised from 43 after round three put the near prairie under the type and the frame measured 20.3.

type:
  hook: "219 miles, mostly Interstate 45."
  dek: "IKEA will be the launch shipper, on a leg of its route from Baytown to Frisco. Kodiak plans to run it with no one in the cab."
  labels: []

verbatim: []

acceptance:
  - "the truck reads at 432px as one long white object crossing the frame on a highway"
  - "the roof sensor bar is visible on the cab against the sky"
  - "the near field reads at 432px as grass running from the shoulder to the bottom edge"
  - "a horizon sits between 0.22 and 0.36 of the frame height"
  - 'the hook reads "219 miles, mostly Interstate 45."'
  - "the frame's median L* at 432px is between 12 and 28"

risks:
  - "a long lens flattens the truck into a silhouette, so the sun must rake its side and the front must be darker than it"
```

```yaml
slide: 3
layout: CLOSE_CROP
primary_image:
  subject: "the tractor's cab and hood from a chase car alongside and a little ahead, the roof sensor bar, the mirror pod and the bumper radar that do the driving, the driver's door and the dark glass, cropped by the frame"
  rect: [0, 500, 1080, 850]
  bleeds: [left, right, bottom]
accent: none
job: >
  Show the machine that has carried IKEA's freight for four years, while the copy gives the
  record the company counts for it, with an observer aboard every mile.

claims: [c21, c22]
numerals:
  - value_from: c21
  - value_from: c22

depth:
  eye: 2.0
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, OCCLUSION, CAST_SHADOW, FORM_SHADING, AERIAL]
  subject_at: {X: 0, Z: 3.5}

composition:
  structure: >
    A chase car's camera a lane over, at a medium three quarter, holds the cab and the front of the
    van against the lane, so the sensor kit on the roof reads and the hood is not the whole frame.
  bands: >
    Top third, the sky and the hook. Middle third, the dek, then the roof fairing, the sensor bar
    and the mirror pod against the sky, the dark side glass. Bottom third, the white door panel lit warm with
    road film darkening toward its sill, the chrome steps and the round chrome fuel tank catching
    the sun with their straps in shadow, and the concrete lane under them.
  focal: "the roof sensor bar and the mirror pod, lit against the dark front"

art:
  technique: "physically based render, close crop, the kit semi_truck tractor with its full sensor kit"
  why_this_technique: "the claim is that the machine drove, and the machine's own sensors are the honest picture of that; no figure is placed in a cab the record does not show"
  palette: "white steel, chrome, slate glass, warm sun"
  value_structure: >
    Lightest is the sunlit door and chrome. Darkest is the glass and the shade under the cab. Frame median L* planned at 20, revised from 29 after round three pulled the camera back to a medium three quarter and the frame measured 19.8.

type:
  hook: "More than 1,300 loads for IKEA."
  dek: "Kodiak says it has delivered more than 1,300 loads and logged more than 750,000 autonomous miles carrying IKEA goods over four years, with a safety observer aboard."
  labels: []

verbatim: []

acceptance:
  - "the roof sensor bar and a mirror sensor pod are visible at 432px"
  - "no person and no hands are drawn anywhere in the frame"
  - "the cab and the front of the van fill more than half the frame width"
  - "the sky is visible above the cab roof"
  - 'the hook reads "More than 1,300 loads for IKEA."'
  - "the frame's median L* at 432px is between 12 and 28"

risks:
  - "no. 34 featured mirror pods and printed the observer line, so this frame leads with the roof bar and carries the IKEA record no. 34 never did"
```

```yaml
slide: 4
layout: FULL_BLEED
primary_image:
  subject: "the view from high behind the cab past the roof sensor housing along southbound Interstate 45 under the front's cloud, a line of delineator posts with amber reflectors running ahead on the shoulder and stopping short of the horizon"
  rect: [0, 640, 760, 620]
  bleeds: [left]
accent: none
job: >
  Put the year end on the road, one reflector for each day left in the year the company named.

claims: [c2, c9]
numerals:
  - computed_by: "out/2026-10-03/compute.py, days_to_year_end, December 31st minus the run date"

data_in_art:
  figure: days_to_year_end
  drives: mark count, the number of delineator posts placed on the shoulder ahead of the truck

depth:
  eye: 4.3
  horizon: 560
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, TEXTURE_GRADIENT, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera sits where the machine looks, so the hood fills the bottom and the lane runs to a
    horizon on the upper half, the reflectors marching up it until the last.
  bands: >
    Top third, the cloud deck and the bright seam under it, holding the type. Middle third, the
    lane converging, the reflectors, the fencerows of post oak country. Bottom third, the concrete
    lane lit grey under the cloud with tyre polish in the wheel paths, the truck's own shadow across
    the left lane, and the white roof fairing and black lidar housing at the bottom edge.
  focal: "the bright seam under the cloud where the lane ends"

art:
  technique: "physically based render, linear perspective, a count as texture gradient, kit highway and semi_truck, raised_pavement_marker built in the chassis"
  why_this_technique: "a date is a distance ahead, and a count on the road the truck is driving makes the days physical"
  palette: "slate, white hood, wet grey concrete, amber reflectors, a pale seam"
  value_structure: >
    Lightest is the seam on the horizon. Darkest is the road under the cloud. Frame median L* planned at 32, revised twice, after round one measured 39.6 and round three measured 31.4 with the camera raised over the fairing.

type:
  hook: "89 days left in the year."
  dek: "Kodiak says it expects to launch driverless operations by year end. One post along the road ahead for each day left after October 3rd."
  labels: []

verbatim: []

acceptance:
  - "the tractor's roof and the sensor housing cross the bottom edge of the frame"
  - "delineator posts on the shoulder run ahead and visibly stop before the horizon"
  - "a horizon with a bright seam under dark cloud sits in the upper half"
  - "no post is placed beyond the eighty ninth"
  - 'the hook reads "89 days left in the year."'
  - "the frame's median L* at 432px is between 24 and 40"

risks:
  - "the far posts merge into a line, so the dek says what one post stands for and the count rests on compute.py"
```

```yaml
slide: 5
layout: DIAGRAM
primary_image:
  subject: "the van at the hub seen square on its side with the near wall taken off, carton stacks filling it from the nose, three pale floor tapes where the load face stood earlier, the ember beam at the load face and bare floor to the open doors"
  rect: [0, 600, 1080, 600]
  bleeds: [left, right]
accent: "#B4664F"
job: >
  Show the measure climbing, one scale for four readings and the doors as the company's 100.

claims: [c7, c8, c9, c27]
numerals:
  - value_from: c27
  - value_from: c7
  - value_from: c9

data_in_art:
  figure: arm_feb
  drives: x position of the first floor tape, interior length times arm_feb over 100, with arm_apr, arm_jul and arm_aug placed on the same scale

depth:
  eye: 1.6
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, CAST_SHADOW, FORM_SHADING, AERIAL]
  subject_at: {X: 0, Z: 90}

composition:
  structure: >
    A long lens from 90 m is near parallel, so every length along the van is on one scale, and the
    labels hang under the van at the positions the measure sets.
  bands: >
    Top third, the front's sky and the hook. Middle third, the dek, then the van in section with
    its stacks and tapes. Bottom third, the labels on the court under the van, the tandem on its
    contact shadow.
  focal: "the ember beam at the load face and the bare floor beyond it"

art:
  technique: "physically based render on a near parallel long lens, the chassis's dry_van in section, DOM SVG leaders that end short of the glyphs"
  why_this_technique: "a series is a quantity, and a quantity wants parallel projection so four lengths share one scale"
  palette: "slate, white liner, oak, kraft, caliche tape, one ember beam"
  value_structure: >
    Lightest is the white liner inside the van. Darkest is the front. Frame median L* planned at 43.

type:
  hook: "84. 86. 91. 93."
  dek: "The share of its safety case's claims and evidence Kodiak calls materially complete, by month in 2026. Each tape marks where the load stood. The doors are 100."
  labels: ["FEB 84", "APR 86", "JUL 91", "AUG 93", "DOORS 100"]

verbatim: []

acceptance:
  - "the van's interior is visible along its whole length with stacks from the nose to the load face"
  - "three pale tapes cross the floor inside the van behind the load face"
  - "the labels read FEB 84, APR 86, JUL 91, AUG 93 and DOORS 100, each under its own position"
  - "the AUG 93 label is bold and the ember beams stand at the load face inside the section"
  - "every leader ends short of a stack and short of the glyphs"
  - 'the hook reads "84. 86. 91. 93."'
  - "the frame's median L* at 432px is between 35 and 51"

risks:
  - "the section reads as a toy cutaway, so the whole world stays in it, sky, haze, contact and grime, and the cut edge is the van's own aluminium"
```

```yaml
slide: 6
layout: FULL_BLEED
primary_image:
  subject: "the van seen from a crane with its roof lifted off, 93 kraft stack tops in two files from the nose, seven bare oak places at the open doors, the tractor whole beyond on the court"
  rect: [140, 520, 870, 700]
  bleeds: []
accent: "#B4664F"
job: >
  Let the reader count the measure, ninety three places loaded and seven bare.

claims: [c7, c8, c9]
numerals:
  - value_from: c7
  - computed_by: "out/2026-10-03/compute.py, arm_open, arm_target minus arm_aug"

data_in_art:
  figure: arm_aug
  drives: mark count, rendered stack tops, with arm_open bare places, one place per percentage point

depth:
  eye: 14.5
  horizon: 360
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, TEXTURE_GRADIENT, AERIAL]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A crane's eye off the van's rear quarter pitched down onto the roofless van, the two files of
    stack tops running away from the lens on the diagonal, the bare places nearest it.
  bands: >
    Top third, the court under the front's light, holding the hook. Middle third, the
    tractor and the far stack tops. Bottom third, the near kraft stack tops lit on
    their top faces with dark seams between rows, the seven bare oak places with wheel tracks and
    nail lines, the open doors folded flat with their hinges in sun, and the court's joints and oil
    stains.
  focal: "the seven bare oak places at the doors against the lit kraft tops"

art:
  technique: "physically based render from a raised camera, isotype at true scale, the chassis's dry_van with its roof off"
  why_this_technique: "a percentage of a fixed container is a count, and a count a reader can make is the most honest picture of it"
  palette: "kraft tops in sun, oak floor, white steel, slate"
  value_structure: >
    Lightest is the sunlit kraft tops. Darkest is the van's shadow on the court. Frame median L* planned at 34.

type:
  hook: "93 places loaded. 7 places bare."
  dek: "One place on the floor for each point of Kodiak's own measure. The last 7 places are the share it didn't call complete at the end of August."
  labels: []

verbatim: []

acceptance:
  - "stack tops in two files fill the van from the far end and stop short of the doors"
  - "bare floor at the door end of the van is visible as an area distinct from the stack tops"
  - "the ember beam (#B4664F) crosses the van at the load face"
  - "the whole rig is in frame from the tractor nose to the open doors, seen on the diagonal from the van's rear quarter"
  - 'the hook reads "93 places loaded. 7 places bare."'
  - "the frame's median L* at 432px is between 26 and 42"

risks:
  - "a camera pointed at the ground fails the world gate, so the pitch stays shallow and the horizon stays in frame"
```

```yaml
slide: 7
layout: FULL_BLEED
primary_image:
  subject: "the van and tractor running north away from the lens on the highway, the van's closed rear doors nearest, the low sun raking its east flank, the tractor's sensor bar at the far end against the slate sky"
  rect: [0, 480, 1080, 620]
  bleeds: [left, right]
accent: none
job: >
  Turn the deck, every figure in it is the company's own account of its own case.

claims: [c8, c17, c18]
numerals: []

depth:
  eye: 2.3
  horizon: 810
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: -4, Z: 26}

composition:
  structure: >
    A camera on the east verge behind the rig puts the van's closed rear doors and its lit flank
    across the frame, running away up the lane, with the caption in the slate sky above it.
  bands: >
    Top third, the bright sky under the cloud's edge and the hook. Middle third, the van's closed
    doors and flank. Bottom third, the concrete lane with tyre polish in the wheel paths catching the
    sun's glare, the truck's contact shadow under its front tyres, and coastal grass tufts back lit
    at the shoulder, the dek on the darker lane.
  focal: "the closed rear doors against the lit flank"

art:
  technique: "physically based render from behind, the flank raked by the low sun, the kit semi_truck with the chassis's dry_van closed"
  why_this_technique: "the turn is a caution, and closed doors show a load the reader is asked to take on the company's word"
  palette: "pale seam, slate, rim lit white, dark road"
  value_structure: >
    Lightest is the van's lit flank. Darkest is the shade under the van and the road. Frame median L* planned at 20, revised from 44 after the camera went behind the rig in round three and the frame measured 19.7. The turn frame is now the deck's darkest.

type:
  hook: "Every readiness figure is Kodiak's own."
  dek: "The readiness measure is the company's account of its own safety case. Its release lists closing that case by year end among forward looking statements it says \"are not predictions of actual performance.\""
  labels: []

verbatim:
  - c17: "are not predictions of actual performance"

acceptance:
  - "the van reads as one object at rear three quarter at 432px"
  - "the van's rear doors are closed"
  - "the lit flank reads lighter than the road at 432px"
  - 'the hook reads "Every readiness figure is Kodiak''s own."'
  - "the frame's median L* at 432px is between 12 and 28"

risks:
  - "round one shot into the sun turned the truck black, and a front three quarter on the lit side repeated slide 3, so the camera went behind the rig"
```

```yaml
slide: 8
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "the van's open rear seen square on from the court, the low sun behind the camera lighting the kraft load face, the two ember beams across it and the bare floor in front of it, the slate front above"
  rect: [200, 470, 680, 880]
  bleeds: [bottom]
accent: "#B4664F"
job: >
  Put the reader on the bare floor while the company says what fills it, the remaining work it calls identified and scheduled.

claims: [c39]
numerals: []

data_in_art:
  figure: arm_open
  drives: mark count, the bare floor places between the load face and the doors

depth:
  eye: 1.6
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, TEXTURE_GRADIENT, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: 2}

composition:
  structure: >
    Square on to the open rear from a standing eye, so the van's opening is one poster object under
    the sky and the load face and the bare floor sit in it, lit by the sun behind the camera.
  bands: >
    Top third, the slate front and the hook and dek. Middle third, the van's header, the roof bows
    in shade and the kraft load face with its two ember beams. Bottom third, the unloaded oak floor planks lit and raked gold by the sun, each strip a shade
    apart, dark wheel tracks and nail lines in them, the load bar's rubber pad and a kraft corner at
    the near left.
  focal: "the lit kraft face and the bare floor in front of it"

art:
  technique: "physically based render at the chassis's dry_van doorway, the sun behind the camera"
  why_this_technique: "the state's terms are about what is not asked, and the bare floor is what is not yet loaded"
  palette: "dark van interior, gold oak, white doorway, one ember beam"
  value_structure: >
    Lightest is the lit kraft face and floor. Darkest is the van's roof and walls. Frame median L* planned at 30, revised from 39 after the type band was darkened before the panel and the frame measured 30.1.

type:
  hook: "The work left."
  dek: "Kodiak founder and chief executive Don Burnette says the company has identified and scheduled the remaining work, and that it is concentrated on final engineering verification and validation."
  labels: []

verbatim: []

acceptance:
  - "the kraft load face is the brightest area in the frame"
  - "bare oak floor runs from the bottom edge to the load face with no stack on it"
  - "two ember beams (#B4664F) cross the load face"
  - 'the hook reads "The work left."'
  - "the frame's median L* at 432px is between 22 and 38"

risks:
  - "a camera inside the van shows no sky, so the van's roof and walls must cover the view above as a built interior"
```

```yaml
slide: 9
layout: FIGURE_SCALE
primary_image:
  subject: "a Texan standing at the open rear of the van on the court, the floor above her waist, the bare places beside her, the stacks rising behind, the swung door beside her, lit from the east"
  rect: [0, 560, 840, 560]
  bleeds: [left]
accent: "#B4664F"
job: >
  Close on what the record can't show, how many of the company's miles ran on this lane, with a Texan beside the van.

claims: [c2, c12]
numerals:
  - value_from: c12

data_in_art:
  figure: arm_open
  drives: mark count, the bare places beside the person at true scale

depth:
  eye: 1.4
  horizon: 880
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, FORM_SHADING, AERIAL]
  subject_at: {X: 2, Z: 0}

composition:
  structure: >
    A person at true scale beside the open rear, so the van's height and the bare floor have a size
    a reader knows.
  bands: >
    Top third, the front and the hook. Middle third, the dek, then the van's rear frame and the
    person's head and shoulders. Bottom third, the oak floor edge above her waist, the near stacks'
    kraft faces lit, the ICC bumper and mud flap with road grime, her shoes on the court with a
    contact shadow and the concrete joints running toward the lens.
  focal: "the person lit against the van's dark interior beside the bare floor"

art:
  technique: "physically based render, kit person at true scale, the chassis's dry_van open"
  why_this_technique: "the next step is a person's, and a person beside the van is the honest scale for it"
  palette: "slate, warm white, kraft, oak, one ember beam"
  value_structure: >
    Lightest is the person's lit face and the van's lit frame. Darkest is the van's interior and the
    front. Frame median L* planned at 34.

type:
  hook: "More than 3.5 million miles. How many here?"
  dek: "Kodiak counts more than 3.5 million autonomous miles since 2019. Its release doesn't say how many of them ran between Dallas and Houston, the lane it means to open with no one in the cab."
  labels: []

verbatim: []

acceptance:
  - "a person stands at the van's rear at true scale, the van floor above her waist"
  - "the person's face and front are lit, not a silhouette"
  - "bare floor is visible in the van beside her"
  - 'the hook reads "More than 3.5 million miles. How many here?"'
  - "the frame's median L* at 432px is between 26 and 42"

risks:
  - "a figure against a dark interior reads as a cutout, so the key is on the camera's side and her feet carry a contact"
```
