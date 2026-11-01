# Storyboard, 2026-11-01
# "The metal still has to be melted."

## The story, and what the fact check did to it

Texas A&M's Department of Materials Science and Engineering takes a $2 million grant (c1) from the WoodNext Foundation,
which manages the philanthropy of Roku's founder Anthony Wood and his wife Susan (c2, c4, c5), through a donor advised fund
(c6). It builds the Aggie AI Foundry, a campus facility meant to use robotics and AI to speed the development of new alloys
(c3), a fully automated system from idea generation through testing (c7). Robotics will mix, melt and test the materials
with computer controlled arms along an assembly line that takes samples (c8). The university's goal is "from months to a
week or less" (c9) and it calls the foundry the first lab of its kind in academia (c12). Existing self driving labs focus on
materials that are easy to make (c11) and can't handle alloys at temperatures up to 3,000 degrees Celsius (c10). Ibrahim
Karaman and Raymundo Arróyave conceived it (c13 to c15) and have published more than 100 papers together (c16). Arróyave
says no computational tool anywhere in the world can predict how an alloy is going to behave (c17). Several dozen elements
give roughly a trillion mixes (c18).

Beside it the National Science Foundation funds the Autonomous Robotic Metallurgist (ARM-MIP, c20) at the Texas A&M
Engineering Experiment Station (c24), an open access facility (c21) that designs, makes, tests and learns from new alloys
(c22), for researchers at non-R1 and EPSCoR institutions too (c23). Its record lists 4100000 dollars obligated of an
estimated 24900000 (c25, c26), from September 1st, 2026 to August 31st, 2032 (c27, c28). PhaseForge, led by Arróyave
(c29), is NSF backed free open software (c30, c31) applying machine learning to CALPHAD to say whether a material can exist
at all (c32, c33).

The fact check moved four things, and every surface obeys them.
1. **"Months to a week or less" is the university's goal.** No surface states it as a result.
2. **"First lab of its kind" is the university's own claim** and is always attributed.
3. **No opening date and no count of arms or samples exists.** No surface implies the foundry is running. Every lab frame
   says drawn to illustrate.
4. **No deck source names a county or College Station.** The deck names Texas A&M and the Engineering Experiment Station.

## Why this treatment, and what was grafted

Director B's ONE CHANGING OBJECT is the spine. One alloy at true bench scale in each state it passes through: glowing in a
copper pocket, cooled in a tray, marked, cut and etched, pulled until it breaks. The metal has to be made because no tool
predicts how it behaves (c17), so the deck shows the made thing and never a screen with an answer.

Grafted from Director C (THE PLACE): frame 6 puts the WoodNext tray of 20 buttons beside a 249 well tray with 41 filled,
at one scale, so the two funders read as two sizes of one unit without a ratio typed anywhere; and C's 72 dogbones in a
raking pool as frame 7's relief. Refused from C: the full room, the arc melter cabinet and a person at the hearth, because
a kit person at the edge of a glowing chamber is the mannequin charge of the week and a cabinet is a slab. Refused from B:
the sample tag punched with 72 dimples (an embossed calendar, no. 64's charge) and a researcher leaning over the tray on 6.
Grafted from Director A (MEASURED EVIDENCE), which reported after the spine was chosen: buttons about 0.45 of their diameter tall so each casts across its neighbour, and every relief's keyMask shaped as a soft window pane on the bench so it falls to black. Refused from A: dusk gold pocket rings as the accent (the glow and the copper would trip the accent gate on every frame) and a nameplate punched with 72 marks (no. 64's embossed charge).

## The world, and the laws that hold it

**LASTLIGHT, STAGED, INDOORS.** The chassis is `assets/js/deck/2026-11-01-foundry.js` and every frame loads it. It declares
`sky: lastLight` with the key at azimuth -60, elevation 14: low window light from the left. A camera looking north (-z) has
the key on its LEFT, every lit edge is on the left, and every cast runs long to the right. TXBENCH reads the same
declaration, raking from the upper left. The txthree frames stand in a dark `TXT.interior` room with its window on the left
and the back wall in shadow, at bench scale, so the room is never shown wide. The glow of metal being made is a practical
point light that casts nothing.

The materials: machined water cooled copper, arc melted alloy (silver grey with frozen ripples and a faint temper tint),
black epoxy bench, alumina, plain steel for the test bars, paper.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#08080B` | the DOM body behind the render |
| `accent` | `#4E5FA8` | bluebonnet, ONLY as a paint pen mark on the one alloy the deck follows. Frames 4, 5, 8, 9 |
| `hook` | `#ECE8DF` | light type on the dark |
| `dek` | `#D6D0C4` | the dek |
| `material` | `#B87333` | machined copper |

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE, VALUE_ARC

1. **Motif evolution, one alloy through its states.** Glowing on 1, a powder before it exists on 2, cooled buttons as money
   on 3 and 6, on the line on 4, marked on its paper on 5, as bars on 7, etched on 8, pulled apart on 9.
2. **Camera move on one bench.** Macro at the pocket on 1, bench height on 3 to 6, the same tray camera pulled back from 3 to
   6, the reliefs as plan views under the one rake.
3. **Value arc, the heat drains out.** White gold glow on 1 and 4, dull silver through the middle, cold broken steel on 9.

## The rotation

    FULL_BLEED  CLOSE_CROP  GRID  DIAGRAM  OBJECT_AND_CAPTION  GRID  CLOSE_CROP  CLOSE_CROP  FULL_BLEED

`TXLAYOUT.check` returns an empty list. Type sits on the dark room or the dark field on every frame.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | MACRO, low, eye 0.24 m over the copper, 0.42 m back from the hot pocket, fov 42 | the chassis copper_hearth with 20 pockets, true metal copper face milled in quiet arcs that live only in its roughness, one alloy_button glowing in the second row's middle pocket with a soft halo, cooled buttons in the other pockets, one broad specular sweep across the top, the copper block running off the bottom of the frame |
| 02 | AERIAL, orthographic material relief | five slumped powder heaps of different metals on a black tray, each a cone with grain in its height and its own albedo, raked at 14 degrees so each casts long to the lower right, a keyMask pool falling to black |
| 03 | CLOSE, eye 0.24 m, 0.55 m from the tray, looking down 28 degrees, fov 34 | the chassis sample_tray of anodised aluminium with 20 wells in two rows of 10, each holding a cooled alloy_button that catches a highlight and casts into the next well, seated on the bench with a contact |
| 04 | MEDIUM, eye 0.9 m, 1.6 m from the bench, fov 34 | the chassis robot_arm on the bench holding a button between a glowing copper_hearth on the left and a pair of tensile grips with a marked tensile_bar on the right, a powder boat beside the hearth, every standing thing seated with a contact |
| 05 | CLOSE, eye 0.32 m, 0.6 m from the stack, fov 32 | the chassis offprint_stack of 100 sheets in one block, its edge showing the sheets, with the marked alloy_button on top, the mark facing the camera, a contact under the stack |
| 06 | MEDIUM, eye 0.42 m, 1.05 m from the trays, looking down 30 degrees, fov 34 | two chassis sample_trays, bead blasted dark anodised aluminium with bevelled edges and scuffed corners, lit from the window so each well has a lit wall and a shadowed wall, seated on the bench with contacts and weathered with grime at their feet, the 20 well tray full and the 249 well tray in rows of 25 with its first 41 wells holding domed alloy_buttons that cast into the next well |
| 07 | AERIAL, orthographic material relief | 72 tensile bars, ground steel with a satin sheen and real fillets, raked by the low key so every bar casts to the lower right on matte black phenolic, the phenolic scuffed and the bars' ends dulled by handling, a keyMask pool falling to black at the right and bottom, 6 rows of 12 |
| 08 | MACRO, orthographic material relief | the section of the button, bright polished alloy with etched dendrite trunks and right angle branches standing proud of a dark etched floor, lit by the low key so each branch casts, set in a black bakelite mount with a worn bevel, a bluebonnet paint mark across the rim, a pool falling to black |
| 09 | AERIAL, orthographic material relief | the pulled tensile bar, ground steel lying flat on the phenolic with a soft contact under both halves, necked ends and dull rough fracture faces, the grips bitten by jaw serrations, raked by the low key so every edge casts, a blue mark on the left grip, on scuffed black phenolic falling to black |

Showstopper frame: 01, the glowing button in its copper pocket at a low macro; its depth is made by the copper running away from the reader into the dark room on a wide lens, the button's glow lighting its pocket, the cooled buttons smaller behind it, and one broad specular sweep across the metal.
Tonal arc: white gold glow on 01, dull powder in a pool on 02, silver buttons on 03, the glow again on 04, paper and the blue mark on 05, the two trays on 06, the bars' lit edges on 07, the etched section on 08, the broken bar's lit edges on 09.
VALUE CUT: frame 4. The deck turns from what the money is to how the metal gets made.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "a water cooled copper hearth at macro with twenty pockets in four rows of five, one alloy button glowing in the near pocket, cooled buttons in the others"
  rect: [0, 560, 1080, 620]
  bleeds: [left, right]
accent: "none"
job: >
  Put the reader at the moment the metal is made, the one step software can't do, and name the foundry and its money.

claims: [c1, c2, c7, c8]
numerals:
  - value_from: c1

data_in_art:
  figure: grant_buttons
  drives: the hearth's pocket count, four rows of five, one button in each and the near one glowing

depth:
  eye: 0.11
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera sits low over the copper so the block runs away from the reader in perspective, the glowing button in the
    second row's middle pocket the brightest point a third up from the bottom, the cooled buttons smaller behind it and the
    near row larger in front of it.
  bands: >
    Top third, the dark room with the kicker, the hook and the dek. Middle third, the far pockets falling into the dark.
    Bottom third, the glowing button and the near row, the lit copper around them and the copper block running off the
    bottom of the frame.
  focal: "the glowing button, the brightest area in the frame"

art:
  technique: "physically based render of the chassis copper_hearth and alloy_button in a dark TXT.interior room, the copper a true metal with its own studio reflection, the hot button an emissive material with a practical point light that lights the copper and casts nothing"
  why_this_technique: "the claim is that metal has to be physically made, so the made metal is rendered as metal with its heat lighting real copper"
  palette: "near black room, machined copper, white gold glow, silver grey alloy"
  value_structure: >
    Lightest is the glowing button and its reflection in the pocket. Darkest is the room and the hearth's shadow side.
    Frame median L* planned at 12.

type:
  hook: "The metal still has to be melted"
  dek: "Texas A&M plans the Aggie AI Foundry, where computer controlled arms will mix, melt and test new alloys. A $2 million WoodNext Foundation grant will help build it. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "one button in the second row's middle pocket glows gold and is the brightest object in the frame at 432 px"
  - "the hearth's four rows of five read in perspective, nineteen pockets holding cooled silver buttons, the outer pockets of the near rows cropped by the frame edge"
  - "the copper around the glowing pocket is lit warm by the glow"
  - "the copper block runs past the bottom of the frame so no front face stands in it"
  - "no hearth or button crosses a glyph of the hook or dek"
  - "the frame's median L* at 432 px is 30 or lower"
  - "the copper_hearth owns at least a third of the frame height at 432px"
risks:
  - "a glow can read as a white ball or a stove burner, so the core is gold not white, the pocket rings are low and the cooled buttons around it say these are melts"
```

```yaml
slide: 2
layout: CLOSE_CROP
primary_image:
  subject: "five slumped heaps of metal powder in five different metals on a black tray, raked low so each heap casts long"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "none"
job: >
  Show what the AI is choosing among, elements as powder before any alloy exists, and the size of the choice in words.

claims: [c3, c11, c18]
numerals: []

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    Five heaps of different sizes sit across the lower two thirds, the nearest cropped by the bottom and right edges, each a
    slumped cone with grain, lit from the upper left so each throws a long cast to the lower right over the tray.
  bands: >
    Top third, the dark tray and the type. Middle third, three heaps in the pool. Bottom third, two heaps cropped by the edge,
    lit on their flanks, their shadow running off to the right, falling to black at the bottom.
  focal: "the largest heap's lit flank in the centre of the pool"

art:
  technique: "TXBENCH multi-material relief, five powders on an anodised tray raked by the low key, with a keyMask pool"
  why_this_technique: "a powder heap is a height field, and a heap that stands and casts reads as material rather than as an icon of an element"
  palette: "near black tray, five powder greys and warms from tungsten grey to copper to nickel"
  value_structure: >
    Lightest is the lit flanks of the heaps. Darkest is the tray outside the pool and the casts.
    Frame median L* planned at 14.

type:
  hook: "Roughly a trillion ways to mix them"
  dek: "Several dozen elements give AI roughly a trillion possible mixes, the university says. Existing self driving labs focus on materials that are relatively easy to make. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "exactly five powder heaps are visible, told apart by albedo at 432 px"
  - "every heap casts a shadow to the lower right"
  - "the tray outside the pool falls to near black"
  - "no legible text is rendered in the art"
  - "the frame's median L* at 432 px is 30 or lower"
  - "the powder heaps own at least half of the frame height at 432px"
risks:
  - "heaps can read as blobs, so each has grain in its height, a slump at its foot and a long cast"
```

```yaml
slide: 3
layout: GRID
primary_image:
  subject: "an anodised tray of 20 cooled arc melted buttons in two rows of 10, seen oblique, each button catching a highlight and casting into the next well"
  rect: [0, 720, 1000, 450]
  bleeds: [left]
accent: "none"
job: >
  Make the WoodNext grant a countable physical thing: one button a drawing unit of $100,000, twenty buttons.

claims: [c1, c2, c4, c5, c6]
numerals:
  - value_from: c1
  - computed_by: "compute.py, grant_buttons and button_unit_usd"

data_in_art:
  figure: grant_buttons
  drives: the number of buttons in the tray

depth:
  eye: 0.24
  horizon: 420
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The tray runs across the frame at an oblique, two rows of ten buttons receding to the right, the near row larger, each
    button a lit dome with its cast in the next well, the tray's bevelled edge catching a line of light.
  bands: >
    Top third, the dark room and the type. Middle third, the far row of buttons and the tray's far edge. Bottom third, the
    near row lit in the pool and the tray's front bevel bleeding off the bottom.
  focal: "the near row of buttons, the brightest area"

art:
  technique: "physically based render of the chassis sample_tray and alloy_button in a dark TXT.interior room, staged on the tray"
  why_this_technique: "a button that stands and casts is a unit a reader counts, and the drawing unit makes money into the deck's own material"
  palette: "near black room, dark anodised tray, silver buttons with a temper tint"
  value_structure: >
    Lightest is the buttons' highlights. Darkest is the room and the empty well floors.
    Frame median L* planned at 14.

type:
  hook: "$2 million, in buttons"
  dek: "The WoodNext Foundation manages the philanthropy of Roku's founder, Anthony Wood, and his wife Susan. The grant comes through a donor advised fund. One button is $100,000, so 20 buttons. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "exactly 20 buttons are in the tray, two rows of 10, countable at full size"
  - "every button casts a shadow into the tray toward the lower right"
  - "the tray is seated on the bench with a contact shadow"
  - "the buttons read as domes and not as flat discs at 432 px"
  - "the frame's median L* at 432 px is 30 or lower"
  - "the sample_tray with its buttons owns at least a third of the frame height at 432px"
risks:
  - "round things in rows read as dials, so the camera is oblique and every button is a lit dome with a cast"
```

```yaml
slide: 4
layout: DIAGRAM
primary_image:
  subject: "a six axis arm on the bench holding a button between a glowing copper hearth and a pair of tensile grips with a marked test bar, a powder boat beside the hearth"
  rect: [40, 730, 1040, 430]
  bleeds: [right]
accent: "#4E5FA8"
job: >
  Show the line the university describes, mix, melt and test, as one bench the arm works along, and why existing labs can't.

claims: [c8, c10, c11]
numerals:
  - value_from: c10

data_in_art:
  figure: max_temp_c
  drives: the tick count of a steel rule standing beside the hearth, one tick per 500 degrees up to max_temp_c

depth:
  eye: 0.9
  horizon: 500
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The bench runs across the frame. The powder boat on the left, the glowing hearth left of centre, the arm rising from the
    back of the bench with its gripper over the centre, the grips with the marked bar on the right. Three mono labels sit
    above the three stations with leaders landing on each.
  bands: >
    Top third, the dark room and the type. Middle third, the arm's upper links and the labels. Bottom third, the bench with
    its three stations, the hearth's glow the warm point on the left.
  focal: "the gripper over the hearth's glow"

art:
  technique: "physically based render of the chassis robot_arm, copper_hearth, alloy_button, crucible and tensile_bar on an epoxy bench in a dark TXT.interior room"
  why_this_technique: "the claim is a sequence of physical steps, so the steps are physical stations one arm can reach"
  palette: "near black room, pale grey arm, copper, white gold glow, steel, the blue mark on the bar's grip"
  value_structure: >
    Lightest is the hearth's glow and the arm's lit edge. Darkest is the room behind the arm.
    Frame median L* planned at 16.

type:
  hook: "Mix, melt and test, on one line"
  dek: "Robotics will mix, melt and test the materials with computer controlled arms along an assembly line that takes samples, the university says. Existing self driving labs can't handle alloys at up to 3,000 degrees Celsius. Drawn to illustrate."
  labels: ["MIX", "MELT", "TEST"]

verbatim: []

acceptance:
  - "the arm, the hearth and the grips are all in frame and each sits on the bench with a contact"
  - "the hearth holds one glowing button that is the warmest point in the frame"
  - "three labels, MIX, MELT and TEST, each have a leader that lands on its station"
  - "a steel rule beside the hearth carries exactly six ticks"
  - "the bar in the grips carries a blue mark at its grip end"
  - "the frame's median L* at 432 px is 30 or lower"
  - "the robot_arm stands at least a third of the frame height at 432px"
risks:
  - "an arm from primitives reads as a toy, so its links are rounded castings with joint housings and a cable run, and it is shown at bench scale only"
```

```yaml
slide: 5
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "a block of 100 sheets of offprints seen at its edge with the marked alloy button resting on top"
  rect: [140, 620, 800, 620]
  bleeds: []
accent: "#4E5FA8"
job: >
  Name who conceived the foundry and the standing they bring, and set the university's own first of its kind claim as theirs.

claims: [c12, c13, c14, c15, c16]
numerals:
  - value_from: c16

data_in_art:
  figure: papers_together
  drives: the number of sheets in the stack

depth:
  eye: 0.32
  horizon: 470
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The stack sits centre bottom, its long edge toward the key so the sheet edges read as fine lines, the button on top with
    its blue mark facing the reader, the stack's cast running right across the bench.
  bands: >
    Top third, the dark room and the type. Middle third, the button on the stack. Bottom third, the stack's lit edge and its
    cast on the dark bench.
  focal: "the button and its blue mark on the top sheet"

art:
  technique: "physically based render of the chassis offprint_stack and alloy_button in a dark TXT.interior room, staged on the stack"
  why_this_technique: "a hundred papers is a physical height, and the button on top says the papers are about this metal"
  palette: "near black room, off white paper in shadow, silver button, the blue mark"
  value_structure: >
    Lightest is the stack's lit edge and the button's highlight. Darkest is the bench outside the pool.
    Frame median L* planned at 16.

type:
  hook: "Two researchers, more than 100 papers"
  dek: "Ibrahim Karaman, who heads the department, and Raymundo Arróyave conceived the foundry. They have published more than 100 papers together. The university calls it the first lab of its kind in academia. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the stack shows separate sheet edges along its lit side at full size"
  - "the button on top carries the blue mark, facing the camera"
  - "the stack casts a shadow to the right on the bench"
  - "the stack's lit face stays under L* 75 at 432 px so the frame is not pale"
  - "the frame's median L* at 432 px is 30 or lower"
  - "the offprint_stack with its button stands at least a quarter of the frame height at 432px"
risks:
  - "a pale paper block pushes the frame into the mid tones, so the stack is mostly on its shadow side with only the edge lit"
```

```yaml
slide: 6
layout: GRID
primary_image:
  subject: "two anodised trays at one scale on the bench, 20 buttons filling the left tray, a 249 well tray on the right in rows of 25 with its first 41 wells holding buttons"
  rect: [0, 820, 1080, 420]
  bleeds: [left, right]
accent: "none"
job: >
  Set the WoodNext grant beside the NSF award at one scale: what NSF has obligated and the whole estimated award.

claims: [c1, c20, c22, c24, c25, c26]
numerals:
  - value_from: c25
  - value_from: c26
  - computed_by: "compute.py, nsf_obligated_money_m, nsf_total_money_m, nsf_obligated_buttons, nsf_total_buttons, grant_buttons"

data_in_art:
  figure: nsf_total_buttons
  drives: the number of wells in the right tray, with nsf_obligated_buttons setting how many hold a button and grant_buttons the left tray

depth:
  eye: 0.42
  horizon: 430
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The same tray camera as frame 3 pulled back and up. The small full tray sits in front, the long tray behind it runs off the right
    edge, its first 41 wells full from the near left corner and the rest empty, so the share reads as a lit patch in a field
    of dark wells.
  bands: >
    Top third, the dark room and the type. Middle third, the far rows of the long tray falling into the dark. Bottom third,
    the small tray and the long tray's full near corner lit in the pool, each button's shadow in its well, the edge bleeding off the right.
  focal: "the 41 full wells at the long tray's near corner"

art:
  technique: "physically based render of two chassis sample_trays and alloy_buttons in a dark TXT.interior room, staged on both trays"
  why_this_technique: "two quantities at one unit read as two sizes of the same thing, and a dark empty well is the money not yet obligated"
  palette: "near black room, dark anodised trays, silver buttons"
  value_structure: >
    Lightest is the full wells' button highlights. Darkest is the empty wells and the room.
    Frame median L* planned at 14.

type:
  hook: "NSF has obligated $4.1 million of $24.9 million"
  dek: "The $24.9 million is the award's estimated total. Its Autonomous Robotic Metallurgist at the Texas A&M Engineering Experiment Station is built to design, make, test and learn from new alloys. In front, the WoodNext grant at $100,000 a button. Drawn to illustrate."
  labels: ["WOODNEXT", "NSF ARM-MIP"]

verbatim: []

acceptance:
  - "the left tray holds exactly 20 buttons and the right tray has exactly 249 wells"
  - "exactly 41 of the right tray's wells hold a button, filled from one corner"
  - "full and empty wells are told apart by value at 432 px"
  - "every button casts into its well toward the lower right"
  - "both labels have a leader landing on their tray"
  - "the frame's median L* at 432 px is 30 or lower"
  - "the two chassis sample_trays own at least a third of the frame height at 432px"
risks:
  - "249 round wells can read as a vent grille or dials, so the camera is oblique, the wells are lit from one side and the full corner is in the pool"
```

```yaml
slide: 7
layout: CLOSE_CROP
primary_image:
  subject: "72 steel tensile bars standing proud on matte black phenolic in six rows of twelve, raked so each casts to the lower right"
  rect: [0, 600, 1080, 750]
  bleeds: [left, right, bottom]
accent: "none"
job: >
  Make the award's length physical, one bar a month for six years, and say who the platform is open to.

claims: [c21, c23, c27, c28]
numerals:
  - computed_by: "compute.py, award_months and award_years"

data_in_art:
  figure: award_months
  drives: the number of tensile bars in the relief, rows of twelve

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    Six rows of twelve dogbones run across the frame at one pitch, the pool on the upper left rows so the first years are
    lit and the later years fall toward the dark, each bar's fillets catching the key.
  bands: >
    Top third, the dark phenolic and the type. Middle third, the lit first rows. Bottom third, the later rows' shadow falling to black
    at the bottom and right edges.
  focal: "the first row of bars in the pool"

art:
  technique: "TXBENCH multi-material relief, steel dogbones on phenolic raked by the low key, with a keyMask pool"
  why_this_technique: "a bar that stands and casts is a counted unit, and the dogbone is the thing a tensile test pulls"
  palette: "near black phenolic, steel grey bars with lit edges"
  value_structure: >
    Lightest is the bars' lit edges in the pool. Darkest is the phenolic and the casts.
    Frame median L* planned at 14.

type:
  hook: "Six years, one bar a month"
  dek: "The NSF award runs from September 1st to August 31st, 2032. The platform is open access, and its intended users include researchers at non-R1 and EPSCoR institutions. One bar is one month. Drawn to illustrate."
  labels: ["2026", "2032"]

verbatim: []

acceptance:
  - "exactly 72 bars in six rows of twelve, countable at full size"
  - "every bar casts a shadow to the lower right"
  - "each bar shows its wide grips and narrow gauge at full size"
  - "the phenolic outside the pool falls to near black"
  - "the frame's median L* at 432 px is 30 or lower"
  - "the bars own at least half of the frame height at 432px"
risks:
  - "72 bars can read as a grille, so the pool lights only the first rows and the rest fall into the dark"
```

```yaml
slide: 8
layout: CLOSE_CROP
primary_image:
  subject: "a deep etched polished section of the alloy button at macro, dendrite trunks with right angle branches standing proud of a dark etched floor, a blue paint mark across the rim"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#4E5FA8"
job: >
  Show why the metal has to be made and looked at: the structure inside it that no tool predicts, and the free software that narrows what can exist.

claims: [c17, c29, c30, c32, c33]
numerals: []

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The section's rim arcs across the frame from left to right, the polished face filling the lower two thirds with dendrite
    trees branching at right angles, the blue mark on the rim at the left, the pool on the centre.
  bands: >
    Top third, the dark mount and the type. Middle third, the rim and the upper dendrites. Bottom third, the densest
    dendrites lit in the pool, their shadow falling to black at the bottom edge.
  focal: "the dendrite trunks in the centre of the pool"

art:
  technique: "TXBENCH multi-material relief, polished alloy with etched dendrites, a bakelite mount and a paint mark, raked by the low key, with a keyMask pool"
  why_this_technique: "an etched section is a true height field, and its structure is the behaviour no tool predicts"
  palette: "near black mount, bright polished dendrites, dark etched floor, the blue mark"
  value_structure: >
    Lightest is the dendrites' lit edges. Darkest is the etched floor and the mount.
    Frame median L* planned at 16.

type:
  hook: "No tool can say how it will behave"
  dek: "Arróyave says no computational tool anywhere in the world can predict how an alloy is going to behave. His NSF backed PhaseForge applies machine learning to CALPHAD to say whether a material can exist at all. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "at least six dendrite trunks with right angle branches cross the etched face at full size"
  - "the blue mark crosses the section's rim"
  - "every dendrite casts to the lower right"
  - "no legible text is rendered in the art"
  - "the frame's median L* at 432 px is 30 or lower"
  - "the section owns at least half of the frame height at 432px"
risks:
  - "dendrites can read as frost or a plant, so the branches meet at right angles and the rim and mount say it is a cut metal section"
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: "one flat steel tensile bar pulled to fracture, its two halves apart across the frame, each necked at the break and ending in a rough fracture face, the grips bitten by jaw serrations, a blue mark on the left grip"
  rect: [40, 840, 1040, 432]
  bleeds: [right]
accent: "#4E5FA8"
job: >
  Close on the answer only testing gives, a broken bar, and on what a reader can do: add to PhaseForge or use the platform.

claims: [c9, c21, c23, c31]
numerals: []

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The bar runs across the frame on a slight diagonal, the left half's marked grip at the left edge, the break in the
    middle third where both necks pinch to a jagged slanted line, the right grip at the right edge, every edge casting to
    the lower right under the low key.
  bands: >
    Top third, the dark bench and the type. Middle third, the necks and the break lit in the pool. Bottom third, the
    grips' lit bevels and their shadow on the dark phenolic, falling to black at the bottom edge.
  focal: "the jagged break between the two necked halves"

art:
  technique: "TXBENCH multi-material relief: ground steel with jaw bites on the grips, dull rough fracture faces, a paint mark, on black phenolic, raked by the low key with a keyMask pool"
  why_this_technique: "the break is a height field with a slanted lip, and a relief lights its fracture faces and necks crisply where the spatial render could not"
  palette: "near black phenolic, ground steel, dull grey fracture, the blue mark"
  value_structure: >
    Lightest is the steel's lit bevels and the grips. Darkest is the phenolic outside the pool and the gap.
    Frame median L* planned at 14.

type:
  hook: "So the bar still gets pulled"
  dek: "The goal is alloys in a week or less instead of months, a target and not a result. PhaseForge is free online and anyone can contribute to it. The NSF platform is open to outside researchers. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the bar lies in two separate halves with a dark gap between them at the middle third"
  - "each half narrows at the break before a rough dull fracture face"
  - "the left grip carries the blue mark"
  - "every edge of the bar casts to the lower right"
  - "the frame's median L* at 432 px is 30 or lower"
  - "the tensile bar halves span at least half of the frame width at 432px"
risks:
  - "a flat bar can read as a cut out shape, so the grips carry jaw bites, the necks pinch and every edge casts"
```
