# Carousel no. 70, November 6th, 2026: the rig floor

## The story, and what the fact check did to it

On its third quarter call of October 30th, 2026, ExxonMobil's chief executive Darren Woods said the company has three
automated drilling rigs in operation in the Permian and is the only operator there using them (c1, c2). He said it
expects automated rigs on about 25% of its Permian fleet next year (c4) and approximately half by 2028 (c5). The
company's own post of October 26th says mechanical arms and robotic systems now do much of the heavy drill pipe handling
that used to put people on the rig floor beside moving machinery (c7), that it expects similar staffing levels on
automated rigs (c9), and that the technology has the potential to eliminate roughly one-third of high-consequence
drilling incidents (c8, a stated potential). Helmerich & Payne said on October 7th that it expects to deploy seven more
FlexRobotics systems for ExxonMobil over 12 months, nine in all (c29). Reuters, on site in August, reported more than 30
Permian rigs with two automated then (c16, c17), a contractor in a small office on the rig running the robots from a
screen (c18), steel pipes of roughly 2,000 pounds (c19), columns of pipe over two stories tall that robotic arms now
position and connect (c26), a crew working the robot's moves out with Houston (c25), the first rig's two miles drilled
horizontally in a little over six days, the third fastest time in the company's history (c21 to c23), about a third of
significant injuries happening on the rig floor (c24), and a gate around the drilling floor of a rig in Midland with a
sign reading "Red Zone: Restricted Area." (c27, c28).

The fact check held it to its words. No source calls these rigs AI, so the deck says automated or robotic. The safety
gain is a potential, never a result. c24's third (where injuries happen) and c8's third (a potential) are different
figures and are never drawn as one. c5's half of the Permian fleet and c6's more than half of unconventional rigs are
kept apart. H&P's nine systems and the call's three rigs are different counts and are never reconciled. Nothing in the
record gives the fleet's size today, any rig's own number, the crew size or the robot's maker beyond the FlexRobotics
name, so every machine in the deck is drawn to illustrate, to no maker's or operator's design.

Docket item tx-2026-0242, admitted this run.

## Why this treatment, and what was grafted

Base: THE FLOOR AT ARM'S LENGTH. The deck starts where a floor hand's hands were, on the tool joint in the robot's
gripper, and steps back one frame at a time until the reader stands outside the Red Zone gate, then in the driller's
cabin, then over the pipe rack. Close crops answer the primitive charge by construction: the camera only holds what the
chassis can build at that distance, a gripper, a tool joint, the slips, a gate, a stand.

Grafted from THE PIPE IS THE MEASURE: the fleet share drawn on one rack of drill pipe at one stated scale, one rack of
20 joints standing for the whole Permian fleet (a drawing unit, never printed), so about 25% next year is five banded
joints (frame 8) and approximately half by 2028 is ten (frame 9). Grafted from THE EMPTY FLOOR UNDER THE LIGHTS: the
two miles of lateral drawn on one scale against the rig that drilled them (frame 7), and the cabin's window onto the
lit floor (frame 6). Dropped: the wide lease road view of the whole mast, because the brand book refuses derricks as
default imagery and a 42 m lattice at 120 m is the postcard; the mast here is a lit lattice behind the floor, never the
subject. Dropped: the scribed plate for c8, because two drawn thirds would be read as one figure; c8 stays in the close's
copy as a potential.

## The world, and the laws that hold it

`floodlit`, staged. The key is one cold LED flood at azimuth -60, elevation 26, high on the camera's left: every steel
face toward the reader takes a lit left edge and every cast runs right and away. The sky is near black with no seam,
which is the plainest difference from no. 68's last light Permian pad. The mast's own floods are emissive lamps that
light nothing they are not near. The rig floor is two stories up, so past its edge the pad falls to dark through
`TXT.stage`. Type is light on the dark field. A wash only darkens. The three reliefs read the same declaration and are
raked from the upper left, across the grating bars and the joints, never along them.

## Palette

mill scale #2A2C2F, worn tool joint #8A8C8E, arm paint #C9CBC6, mast paint #A39C8C, safety yellow #C4A43A, deck steel
#45474A, night #08060F, ember #B4664F

A Permian rig floor under its floods: blue black mill scale on the pipe, tool joints worn bright, an off white arm, a
faded cream mast, sun worn safety yellow on the rails, grey deck steel, the black sky. The accent is dusk_ember #B4664F
and it means ONE thing: pipe work handed to a machine, a painted band on a joint's box end. It sits on the gripped joint
(1, 5), the stand (4) and the rack's banded joints (7, 9). Nothing else wears it.

## The continuity devices

CONTINUITY: CAMERA_MOVE, MOTIF_EVOLUTION

1. **Camera move, out of the Red Zone.** At arm's length on the gripper (1), a step back to the gate (2), straight down
   on the floor plate (3), outside the gate looking up the stand (4), back in at the slips (5), into the cabin (6), down
   out to the section (7), down on the rack (8), and over the rack to the floor beyond (9).
2. **Motif evolution, the ember band.** One banded joint in the gripper (1), the banded joint made up into the string
   (5), five of 20 joints on the rack (8), ten of 20 on the rack in the place itself (9), the band growing as the
   company's plan does.

## The rotation

    CLOSE_CROP  FULL_BLEED  DIAGRAM  FIGURE_SCALE  CLOSE_CROP  FULL_BLEED  SPLIT_HORIZON  DIAGRAM  FULL_BLEED

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | MACRO, eye 1.45 m, 0.9 m off the gripper, level, the black sky and the lit mast in the upper third, fov 34 | the chassis pipe_robot gripper closed on a chassis drill_pipe tool joint, worn bright joint steel with a hardband ring and an ember band on the pin, the jaw's die pads biting, off white arm castings with bolt rings and a cable loom, raked from the upper left so every edge toward the lens is lit, TXT.weather grime on the jaws |
| 02 | MEDIUM, eye 1.6 m on the floor outside the gate, fov 38 | the chassis red_zone_gate, a pipe swing gate in sun worn safety yellow with a red sign plate and a white band, chain latch and hinge pins, its top rail crossing the frame at chest height, the arm and the stand beyond it in the pool, contact on the grating |
| 03 | AERIAL, orthographic material relief | the rig floor plate as nine steel panels, bar grating with bearing bars and cross rods and three diamond tread panels lit by the flood's keyMask, mill scale dark steel, the bars casting across each other under the upper left key |
| 04 | WIDE, eye 1.15 m at the floor's edge 6 m from the setback, looking up, fov 44 | a row of seven chassis pipe_stand columns racked on the setback, three joints each of mill scale pipe with bright tool joints and an ember band on the nearest, lit by the mast flood and rising out of the top edge, a kit person in a vest and hard hat outside the yellow gate lit from the camera side for scale |
| 05 | CLOSE, eye 1.0 m, three quarters on the well 3 m out, fov 18 | the chassis drill_pipe pin tool joint in worn bright steel with a shaded ember band and turned pin threads entering the box of the joint held in the chassis rig_floor slips, the chassis pipe_robot casting above with bolt rings, raked by the flood from the upper left |
| 06 | MEDIUM, eye 1.4 m inside a TXT.interior cabin, fov 54 | the kit desk under three kit monitors whose glow and two low warm lamps are the room's warm source, two joystick consoles at the desk edge with lit indicator lamps, a contractor in a hi-vis vest and cap seated over the shoulder at the lower left, the back window glowing with the floor's cold floods |
| 07 | WIDE, orthographic material relief, elevation section | the earth in section as a dark strata block with a lit lateral bore groove carrying a raised steel string, two miles at one scale, the rig at the left edge as a raised pin at the same scale, a drawn break in the vertical because depth is not in the record |
| 08 | AERIAL, orthographic material relief | one rack of 20 drill pipe joints, mill scale steel bodies with bright worn upset tool joints and raised ember paint bands on five, lying across two rust streaked steel rack beams, raked from the upper left so each joint casts onto the one below, grime where the joints rest on the beams |
| 09 | MEDIUM, eye 2.4 m on the pipe deck beside the rack, looking over it to the floor, fov 40 | the chassis drill_pipe rack, 20 joints on two rack beams in the pool, ten with ember bands nearest the lens, mill scale and bright joints raked from the upper left, contact on the deck, the rig floor beyond with the arm parked and the stand in the slips, the lit mast fogged above |

Showstopper frame: 01, the gripper's jaws closed on the tool joint at arm's length, each die pad casting a hairline across the bright joint under the raking flood, the ember band on the pin, one specular line climbing the pipe into the black, the mast's lamps soft behind, its depth the jaw's occlusion of the pipe and the cast shadow of the gripper across the joint.
Tonal arc: brightest steel on 01, darker on 02 and 03, the floor pool peaks again on 04 and 05, the darkest room on 06 lit only by its screens, the reliefs held near black on 07 and 08, and the rack lit in its pool on 09.
VALUE CUT: frame 6. The deck turns from the machine on the floor to the people who now run it from a screen.

---
```yaml
slide: 1
layout: CLOSE_CROP
primary_image:
  subject: "a robotic arm's gripper closed on a drill pipe just above its banded pin at arm's length, the pipe rising out of the top edge into the black, the lit lattice mast soft behind"
  rect: [240, 620, 840, 540]
  bleeds: [right]
accent: "#B4664F"
job: 'Put the reader where a floor hand''s hands used to be, on the pipe, and show that a machine holds it now, before any figure arrives.

  '
claims: [c1, c7]
numerals: []
depth:
  eye: 1.45
  horizon: 520
  cues: [CAST_SHADOW, FORM_SHADING, OCCLUSION, RELATIVE_SIZE, AERIAL]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'A close view level with the gripper. The joint runs vertically through the left half of the frame from the bottom edge out of the top. The gripper enters from the right, its jaws closed around the joint just above its banded pin. The upper arm leaves the frame at the upper right edge, clear of the type column.

    ', bands: 'Top third, the black sky and the fogged lattice of the mast with its lamps, carrying the kicker, the hook and the dek. Middle third, the gripper jaws and the bright tool joint with its ember band. Bottom third, the mill scale pipe body lit along one edge and the arm''s wrist and cable loom in the pool, their shadows on the grating below, which falls to dark.

    ', focal: the closed jaws on the bright tool joint and its ember band}
art: {technique: 'physically based close render of the chassis pipe_robot and drill_pipe on the chassis rig_floor in the floodlit world, staged on the gripper', why_this_technique: 'the claim is that a machine now does the handling, and a close render gives steel and cast paint their real response to one cold flood, so the gripper reads as a working tool rather than a toy', palette: 'mill scale pipe, worn bright joints, off white arm paint, black sky, the ember band', value_structure: 'Lightest is the specular line on the tool joint and the jaw edges toward the key. Darkest is the sky and the floor beyond the pool. Frame median L* planned at 16.

    '}
type:
  hook: "A robot arm now holds the pipe"
  dek: "ExxonMobil says three of its Permian drilling rigs are automated. Mechanical arms and robotic systems now do much of the heavy pipe handling on the rig floor. The arm is drawn to illustrate."
  labels: []
verbatim: []
acceptance: [a robotic gripper closed around a vertical pipe is identifiable at 432 px, 'the gripper and tool joint together own at least a third of the frame area at full size, and the frame fails if the gripper is missing or not touching the pipe', the gripped joint shows an ember band at its pin tool joint, 'a lit lattice mast or its lamps shows behind the subject in the upper third', no jaw or pipe crosses a glyph of the hook or dek, the frame's median L* at 432 px is 30 or lower]
risks: ['an arm at close range can read as stacked boxes, so the crop holds the jaws, die pads, bolt rings and cable loom and leaves the plain upper casting out of the frame']
```

```yaml
slide: 2
layout: FULL_BLEED
primary_image:
  subject: "the yellow pipe gate around the drilling floor with its red sign plate, its top rail across the frame at chest height, the robotic arm holding a stand beyond it in the pool of the flood"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#B4664F"
job: 'Show where people now stand, outside a gate, and why that floor is the one worth fencing.

  '
claims: [c28, c27, c20]
numerals: []
depth:
  eye: 1.6
  horizon: 600
  cues: [LINEAR_PERSPECTIVE, CAST_SHADOW, OCCLUSION, RELATIVE_SIZE, AERIAL]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'A standing view from the floor outside the gate. The gate''s top rail crosses the frame from edge to edge at chest height, its red sign plate left of centre. Beyond it the floor opens into the pool where the arm holds the stand, which rises out of the top edge past the lit mast.

    ', bands: 'Top third, the black sky, the lit lattice and the stand with the kicker, the hook and the dek. Middle third, the arm, the stand and the slips in the pool beyond the gate. Bottom third, the gate''s yellow rails and red sign plate close to the lens, lit from the left with their shadows thrown across the grating.

    ', focal: the red sign plate on the yellow gate against the lit floor beyond}
art: {technique: 'physically based render of the chassis red_zone_gate, pipe_robot, pipe_stand and rig_floor under the chassis rig_mast in the floodlit world', why_this_technique: 'the claim is a place a person may no longer stand, and a render with a real gate in the foreground and the machine beyond puts the reader on the right side of it', palette: 'safety yellow rails, a red sign plate with a white band, deck steel, the off white arm, the black sky', value_structure: 'Lightest is the floor pool around the slips and the lamps. Darkest is the sky and the floor outside the pool. Frame median L* planned at 15.

    '}
type:
  hook: "A Red Zone gate rings a drilling floor"
  dek: "The sign on one ExxonMobil automated rig in Midland reads \"Red Zone: Restricted Area.\" The rig floor is the most common place for accidents on a rig, Reuters reported."
  labels: []
verbatim:
- c28: "Red Zone: Restricted Area."
acceptance: [a yellow pipe gate with a red sign plate in the foreground is identifiable at 432 px, 'the gate spans the full frame width and its sign plate is at least 120 px wide at full size, and the frame fails if the gate is missing', the robotic arm holding a stand shows beyond the gate in the lit pool, the stand rises toward the top edge, no rail or pipe crosses a glyph of the hook or dek, the frame's median L* at 432 px is 30 or lower]
risks: ['a gate in front of a machine can read as clutter, so the gate is close and simple and the arm stands alone in the pool behind it']
```

```yaml
slide: 3
layout: DIAGRAM
primary_image:
  subject: "the rig floor plate seen straight down as nine steel panels, six of bar grating and three of diamond tread plate lit by the flood, a measured relief"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "none"
job: 'Measure the danger the robots take on, a third of significant injuries on one floor, as a share the reader can count.

  '
claims: [c24]
numerals: []
data_in_art: {figure: injury_tiles, drives: 'the count of floor panels drawn as lit diamond tread plate, out of nine'}
depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]
composition: {structure: 'A plan of the floor as a three by three grid of steel panels filling the lower two thirds. The three panels of the right hand column are diamond tread plate inside the flood''s pool, the other six bar grating left in the dark. Two leaders name the lit third and the rest.

    ', bands: 'Top third, black steel beyond the plate with the kicker, the hook and the dek. Middle third, the upper panels with the lit tread plate column starting. Bottom third, the lower panels, the lit tread plate column''s raised diamonds throwing shadows across it and the dark grating bars in relief, with a leader line to each part.

    ', focal: the lit column of diamond tread plate against the dark grating}
art: {technique: 'TXBENCH material relief, multi material height field with bearing bars, cross rods and raised diamonds, raked by the chassis key and gated by a keyMask pool', why_this_technique: 'a share wants something countable, and nine panels of the actual floor surface, three of them lit, make the third a thing the reader can count without a chart', palette: 'mill scale dark steel, bright worn diamond tops, black gaps between bars', value_structure: 'Lightest is the raised diamond tops in the pool. Darkest is the gaps between the grating bars. Frame median L* planned at 14.

    '}
type:
  hook: "About a third of significant injuries happen here"
  dek: "The rig floor holds that share across the history of well drilling, ExxonMobil's Bart Cahir told Reuters. The nine plates stand for all of those injuries, and the lit three for the floor's share."
  labels: ["on the floor", "elsewhere"]
verbatim: []
acceptance: [a steel floor of grating panels is identifiable at 432 px, 'the nine panel floor plate covers at least half of the frame area, and the frame fails if it is smaller', 'exactly three of the nine panels are diamond tread plate in the lit pool, and the frame fails if the count is not three of nine', 'the grating bars cast visible shadows across the cross rods at full size', the leader for the third lands on a tread plate panel within 24 px, the frame's median L* at 432 px is 30 or lower]
risks: ['a plan relief can read as a flat pattern, so the bars carry real height and cast, and the pool, not a colour, marks the third']
```

```yaml
slide: 4
layout: FIGURE_SCALE
primary_image:
  subject: "a row of racked stands of drill pipe, three joints each, rising from the setback out of the top edge past the lit mast, with a worker in a vest and hard hat outside the gate for scale"
  rect: [160, 0, 760, 1350]
  bleeds: [top, bottom]
accent: "#B4664F"
job: 'Give the pipe a size, over two stories and about a ton, against a person who used to steady it by hand.

  '
claims: [c26, c19]
numerals:
- {value_from: c19}
data_in_art: {figure: stand_m, drives: 'the drawn height of the stand above the floor, three joints of joint_m each, against the kit person at true scale'}
depth:
  eye: 1.6
  horizon: 1050
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'A wide view from the floor looking up the stand, which runs from the slips at lower centre out of the top edge, its tool joints stepping up the frame. The worker stands at lower left outside the gate, small against the pipe. The mast''s lit lattice frames the stand.

    ', bands: 'Top third, the stand''s upper joints against the black sky and the mast lamps, with the kicker, the hook and the dek. Middle third, the middle joint and its tool joints climbing past the racking board. Bottom third, the three steel slip segments in the lit rotary, the arm''s off white gripper casting on the lowest joint with its bright tool joint, and the worker in a hi vis vest outside the yellow gate, all modelled in the pool.

    ', focal: the tall pipe rising from the lit floor beside the small worker}
art: {technique: 'physically based render of the chassis pipe_stand, pipe_robot, rig_floor, red_zone_gate and rig_mast with a kit person in the floodlit world', why_this_technique: 'height is a ratio, and a person and a pipe at true scale in one perspective view state it without a number', palette: 'mill scale pipe, bright joints, the ember band, the off white arm, safety yellow, a hi vis vest, the black sky', value_structure: 'Lightest is the floor pool and the joints'' speculars. Darkest is the sky between the lattice. Frame median L* planned at 14.

    '}
type:
  hook: "Over two stories of pipe, moved by an arm"
  dek: "The steel pipes weigh roughly 2,000 pounds, Reuters reported. Workers would usually help move that pipe. The worker is drawn to illustrate."
  labels: []
verbatim: []
acceptance: [tall vertical pipes beside a small standing person are identifiable at 432 px, 'the stands run at least 700 px tall at full size from the floor to the top edge, and the frame fails if the stands are shorter than four times the person', the person wears a vest and hard hat and is lit from the camera side, the person stands outside a yellow gate, no pipe or lattice crosses a glyph of the hook or dek, the frame's median L* at 432 px is 30 or lower]
risks: ['the kit person reads as a mannequin when back lit, so the key falls on the side the camera sees and the person stays small']
```

```yaml
slide: 5
layout: CLOSE_CROP
primary_image:
  subject: "a tight close on the threaded pin entering the box of the joint held in the slips, the gripper's casting above holding the banded tool joint"
  rect: [280, 390, 480, 960]
  bleeds: [bottom]
accent: "#B4664F"
job: 'Show the one task the machine took from a person, making up the connection at the rotary, at the distance a floor hand saw it.

  '
claims: [c26, c10]
numerals: []
data_in_art: {figure: joint_m, drives: 'the joint length of the pipe in the gripper and in the slips, so the box sits at the height a full joint puts it'}
depth:
  eye: 1.3
  horizon: 480
  cues: [CAST_SHADOW, FORM_SHADING, OCCLUSION, RELATIVE_SIZE]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'A tight three quarter close at the well. The gripper''s off white casting, lit from the camera side as on the cover, comes in from the upper right with its jaw closed on the next joint, whose banded tool joint and turned pin fill the middle of the frame. The pin''s threads are entering the box mouth of the joint held in the slips, and the slip handles stand out at the rotary below.', bands: 'Top third, the gripper''s casting falling to black behind the kicker, the hook and the dek, its lit jaw and underside just below the dek. Middle third, the pin tool joint in worn bright steel with its ember band lit by the flood. Bottom third, the lit pin threads entering the box mouth, the box shoulder, and the slip handles casting shadow at the rotary.', focal: the pin threads entering the box mouth}
art: {technique: 'physically based close render of the chassis pipe_robot, drill_pipe and rig_floor rotary and slips in the floodlit world', why_this_technique: 'the connection is a few centimetres of steel meeting steel, and only a close render shows threads, joints and slips as the machined parts they are', palette: 'worn bright joints, mill scale bodies, grey slips with die faces, the ember band, the off white arm', value_structure: 'Lightest is the joints'' speculars and the rotary rim. Darkest is the sky and the floor beyond the pool. Frame median L* planned at 15.

    '}
type:
  hook: "The arm makes the connection"
  dek: "Where workers used to help move the pipe, robotic arms now position columns of drill pipe and connect them to a drill string, Reuters reported. ExxonMobil says it contracted drilling operators to modernize its fleet with robotic systems."
  labels: []
verbatim: []
acceptance: [a threaded pin entering the box of a pipe held below is identifiable at 432 px, 'the pin, its banded tool joint and the box together stand at least 560 px tall at full size, and the frame fails if they are shorter', 'the pin threads touch the box mouth with no gap of black between them', 'the pin tool joint carries an ember band', no casting or pipe crosses a glyph of the hook or dek, the frame's median L* at 432 px is 30 or lower]
risks: ['the hardest frame, so after a relief that read as boxes it takes the plan''s fallback, a tight crop on the gripper, pin and box where the turned threads carry it']
```

```yaml
slide: 6
layout: FULL_BLEED
primary_image:
  subject: "the driller's cabin at night, a desk of three lit screens with two joystick consoles and an empty chair, the back window glowing with the floor's cold floods"
  rect: [0, 520, 1080, 830]
  bleeds: [left, right, bottom]
accent: "none"
job: 'Turn from the machine to the people who run it, a contractor at a screen in a small office on the rig.

  '
claims: [c18, c25]
numerals: []
depth:
  eye: 1.2
  horizon: 700
  cues: [LINEAR_PERSPECTIVE, OCCLUSION, RELATIVE_SIZE, CAST_SHADOW]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'An over the shoulder view inside the cabin. The person sits at the lower left, their shoulder and head cut by the frame, facing three screens on the desk. The window band behind the screens shows the lit floor and the arm in the pool.

    ', bands: 'Top third, the dark cabin ceiling and wall with the kicker, the hook and the dek. Middle third, the window band with the lit floor and arm, and the screens. Bottom third, the desk, the person''s shoulder and the controls.

    ', focal: the glowing screens with the lit floor through the window above them}
art: {technique: 'physically based render inside a TXT.interior room with kit desk, monitors, office chair and person, the floor seen through the window', why_this_technique: 'the claim is a change in where a person works, and a real dark room around one source of light puts the reader at the controls', palette: 'dark cabin steel, warm screen glow, the cold flood through the glass, a hi vis vest', value_structure: 'Lightest is the screens and the window band. Darkest is the cabin''s corners. Frame median L* planned at 12.

    '}
type:
  hook: "The controls are on a screen"
  dek: "A contractor runs the robotic machinery from a small office on the rig, Reuters reported. Employees on the rig set the robot's precise moves with ExxonMobil's central operations team in Houston."
  labels: []
verbatim: []
acceptance: [a desk of lit screens with joystick controls in a dark room with a window is identifiable at 432 px, 'the desk and its three screens span at least 500 px of the frame width at full size, and the frame fails if there are fewer than three screens', 'two joystick consoles stand at the desk edge in front of the screens', the window glows cold and dimmer than the screens, no screen or glow crosses a glyph of the hook or dek, the frame's median L* at 432 px is 30 or lower]
risks: ['a room can go to mud, so the screens are the warm source, the window the cold one, and the corners stay black']
```

```yaml
slide: 7
layout: SPLIT_HORIZON
primary_image:
  subject: "the earth in section with a two mile horizontal bore lit inside it, the rig a small raised pin at the left, drawn to illustrate, a measured relief"
  rect: [0, 620, 1080, 730]
  bleeds: [left, right, bottom]
accent: "none"
job: 'Show what the first automated rig did, two miles sideways in a little over six days, against its own size.

  '
claims: [c21, c22, c23]
numerals: []
data_in_art: {figure: lateral_m, drives: 'the drawn length of the lateral bore across the section, at one scale with the rig''s height'}
depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]
composition: {structure: 'A horizontal cut at the upper third. Above it, black. Below it, the dark strata block. The rig stands at the cut''s left end as a small raised pin. The bore drops from it and turns to run as a lit groove with a raised steel string across nearly the whole width.

    ', bands: 'Top third, black above the surface line with the kicker, the hook and the dek. Middle third, the surface line, the rig pin and the descending bore. Bottom third, the lateral running across the strata and the drawn depth break.

    ', focal: the long lit lateral running across the dark strata}
art: {technique: 'TXBENCH material relief of a geologic section, layered rock as a height field with a cut groove and a raised steel string', why_this_technique: 'two miles beside a rig is a ratio a drawing can hold and a sentence can''t, and a section is how drillers draw a lateral', palette: 'dark strata in mill scale greys and caliche, a bright steel string, black above ground', value_structure: 'Lightest is the steel string''s top in the groove. Darkest is the black above the surface. Frame median L* planned at 12.

    '}
type:
  hook: "Two miles sideways in a little over six days"
  dek: "Helmerich & Payne supplied ExxonMobil's first automated rig. Its run was the third fastest drilling time in the company's history, Reuters reported. The depth is not in the record and is drawn to illustrate."
  labels: ["two miles"]
verbatim: []
acceptance: [a long horizontal line through layered rock below a small rig is identifiable at 432 px, 'the earth in section, a dark strata block with a lit lateral bore, owns at least a third of the frame height, and the frame fails if the strata block is missing or flat', 'the lateral runs at least 800 px of the frame width at full size, and the frame fails if it is shorter', the rig at the left is drawn at the same scale and is visibly tiny beside the lateral, a drawn break marks the vertical as not to scale, the frame's median L* at 432 px is 30 or lower]
risks: ['the depth is unknown, so a break in the vertical says so, and only the horizontal is to scale']
```

```yaml
slide: 8
layout: DIAGRAM
primary_image:
  subject: "one rack of twenty drill pipe joints seen straight down, lying across two rack beams, five with ember bands in one group, a measured relief"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#B4664F"
job: 'Draw next year''s plan as a share of one rack, so about 25% is a count of joints the reader can see.

  '
claims: [c4]
numerals:
- {value_from: c4}
data_in_art: {figure: rack_next, drives: 'the count of rack joints carrying the ember band, out of the rack_unit joints'}
depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]
composition: {structure: 'A plan of the rack. Twenty joints lie side by side across the frame, cropped by both side edges so no pipe end shows, on two steel beams. The five nearest the top carry the ember band at their tool joints in one group.

    ', bands: 'Top third, the first banded joints and black steel above them with the kicker, the hook and the dek. Middle third, the rest of the rack. Bottom third, the lower joints lit along their crowns with their bright upset tool joints, each throwing a shadow onto the next, resting on the rust streaked second rack beam that runs edge to edge.

    ', focal: the five banded joints at the top of the rack}
art: {technique: 'TXBENCH material relief, round joints as height profiles with upset tool joints, two materials and a raised paint band, raked by the chassis key', why_this_technique: 'a share of a fleet whose size is not in the record wants a whole that is drawn rather than counted, and one rack of the pipe this deck is about is that whole', palette: 'mill scale, bright joints, ember paint, dark rack steel', value_structure: 'Lightest is the specular line along each joint''s crown. Darkest is the gaps between the joints. Frame median L* planned at 14.

    '}
type:
  hook: "About 25% of the fleet next year"
  dek: "ExxonMobil expects to expand automated rigs to that share of its Permian fleet, chief executive Darren Woods said. The rack stands for the whole fleet, not a rig count."
  labels: ["about 25%"]
verbatim: []
acceptance: [a rack of parallel pipes seen from above is identifiable at 432 px, 'exactly five of the twenty joints carry an ember band, and the frame fails if the count is not five of twenty', the joints cover at least half of the frame area, 'each joint casts onto the joint below it at full size', the label "about 25%" lands beside the banded group within 24 px, the frame's median L* at 432 px is 30 or lower]
risks: ['a rack in plan can read as stripes, so each joint carries its upset and tool joint and a real cast, and the band is raised paint rather than a colour fill']
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: "one rack of twenty drill pipe joints on the pipe deck in the pool of the flood, ten with ember bands nearest the lens, the rig floor beyond with the arm parked and the stand in the slips"
  rect: [20, 900, 1060, 450]
  bleeds: [right, bottom]
accent: "#B4664F"
job: 'Close on the plan as the place itself, half the rack handed to machines by 2028, with the crews the company expects to keep.

  '
claims: [c5, c9]
numerals:
- {value_from: c5}
data_in_art: {figure: rack_2028, drives: 'the count of rack joints carrying the ember band, out of the rack_unit joints'}
depth:
  eye: 2.4
  horizon: 560
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'A standing view from the pipe deck over the rack. The twenty joints run from the lower left toward the floor, ten banded nearest the lens. Beyond them the rig floor stands in its own pool, the arm parked and the stand in the slips, the mast''s lamps above.

    ', bands: 'Top third, the black sky, the mast lamps and the rig floor with the kicker, the hook and the dek. Middle third, the far end of the rack and the floor''s edge. Bottom third, the ten nearest joints lit in the pool with raised ember bands on their bright tool joints, mill scale bodies catching specular lines, their shadows falling onto the rack beams and the deck.

    ', focal: the ten banded joints at the near end of the rack}
art: {technique: 'physically based render of the chassis drill_pipe joints on rack beams with the chassis rig_floor, pipe_robot, pipe_stand and rig_mast in the floodlit world', why_this_technique: 'the close has to show the consequence in the place, and the same rack as frame 8 seen in the yard turns a share into steel on the ground', palette: 'mill scale, bright joints, ember paint, deck steel, the off white arm, the black sky', value_structure: 'Lightest is the joints'' speculars in the near pool and the floor''s lamps. Darkest is the sky and the deck between pools. Frame median L* planned at 14.

    '}
type:
  hook: "About half by 2028, with similar staffing"
  dek: "Woods said ExxonMobil expects automated rigs on approximately half its Permian fleet by 2028. The company expects similar staffing levels on automated rigs."
  labels: []
verbatim: []
acceptance: [a rack of pipes on the ground with a lit rig floor beyond is identifiable at 432 px, 'exactly ten of the twenty joints carry an ember band, and the frame fails if the count is not ten of twenty', the rack spans at least 700 px of the frame width at full size, the rig floor beyond shows the robotic arm, no pipe or lamp crosses a glyph of the hook or dek, the frame's median L* at 432 px is 30 or lower]
risks: ['twenty joints in perspective can fuse at 432 px, so the camera is high enough to separate them and the banded ten sit nearest the lens']
```
