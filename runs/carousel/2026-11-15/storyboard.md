# Carousel no. 78, November 15th, 2026: a hundred desks, and the rules on few of them

## The story, and what the fact check did to it

Texas 2036, a nonprofit policy group, published a preview of its report on AI in Texas schools on November 10th, 2026 (c1).
In fall 2025, 86% of Texas school and district leaders reported teachers using AI and 61% reported student use (c2). Only
29% reported a district policy governing student AI use (c3), and 20% a policy for teachers and staff (c4). By the group's
own analysis 42 states have issued some form of statewide AI guidance for schools (c5) and Texas is not among them (c6). Its
priorities are statewide guidance (c7), safety standards before tools reach classrooms (c8), teacher training (c9) and age
appropriate AI literacy (c10). The report's author Renzo Soto (c12) says AI has not changed what works for students (c11).
Texas 2036 reports that nearly 85% of Texas voters call student data privacy extremely or very important if schools use AI
(c13), and 71% call teaching responsible use important (c15).

The fact check found no name for who ran the leader survey or the voter poll, so every figure is stated as Texas 2036's report
of it. The report itself is not on the group's reports page yet, so the deck calls it only what the article calls it. The
survey shares answer different questions, so no frame sets one against another, subtracts them or draws them as two bars.

Docket item tx-2026-0248, statewide, health-and-education. No Texas place is named, so the art and the close carry it.

## Why this treatment, and what was grafted

Base: THE HUNDRED DESKS (the room lens). Every figure is a person reporting on people, so the deck stands in the rooms a
teacher or a parent knows. One unit, one leader in a hundred, is carried in school objects a reader already counts by. Grafted
from A HUNDRED OF EVERYTHING: the locker bank for student use and the voters kept apart from leaders. Grafted from THE EMPTY
BINDER: the shelf of 42 binders with one empty slot for Texas, and the four tab dividers over blank leaves for the priorities.
Dropped: the meter stick (it sets 61 beside 29 and reads as a comparison the source never makes), the stadium crowd of a hundred
(capsule people at scale), the Capitol close (the next step the claims support is the district), the charging carts.

## The spine

`assets/js/deck/2026-11-15-ruleroom-bespoke.js`. LOOK V2, tone PEOPLE (warm apricot key, plum fill, periwinkle sky), bespoke.
Each frame owns its world, light, camera and type position. Shadows lean plum, never black.

### Palette

The shared PEOPLE tone is `TXLOOK.TONES.people` in `assets/js/txlook.js`. These are its base colours before scene lighting and the grade; each dossier also describes its materials and local lighting.

| token | hex | role |
|---|---|---|
| skyTop | #2b4fb8 | upper sky |
| skyMid | #4a7be0 | middle sky |
| skyLow | #ffc7a8 | low sky and rim |
| floor | #ff9f62 | studio floor |
| wall | #4673d8 | studio wall |
| key | #ffdcb0 | warm key light |
| fill | #7a52c8 | plum fill light |
| shade | #3b1f5e | plum shadow |
| ink | #fff6ec | headline ink |
| dek | #f2e8ff | supporting type |
| accent | #ff9f1c | a written rule |

THE ACCENT is the people tone's amber #ff9f1c and means ONE thing: a WRITTEN RULE (a district policy, a staff policy sheet,
statewide guidance). It is absent from frames 1, 2, 3 and 8 and present on 4, 5, 6 and 9 only where a claim counts a written
rule. The four priorities (7) are proposals and carry none. Data labels use the tone's plain ink pill (.lab.plain), never amber.

CONTINUITY: MOTIF_EVOLUTION, VALUE_ARC
1. THE HUNDRED. One unit per leader in a hundred (figures.json per_hundred): 100 desks with 86 lit (2), 100 lockers with 61 ajar
   (3), the same 100 desks with 29 amber folders (4), 100 staff mailboxes with 20 amber sheets (5). Every dek says drawn to
   illustrate.
2. THE ACCENT AS THE WRITTEN RULE. Nothing amber on the cover. Folders (4), sheets (5), binder spines (6), a policy binder on the
   board's dais (9). The colour's arrival is the story's turn from use to rules.
3. VALUE ARC THROUGH THE SCHOOL DAY. Morning studio light (1), late morning gym (2), noon hallway (3), afternoon gym (4), office (5), library (6),
   desk blotter (7), after school pickup (8), evening board room (9).

## THE NINE BEATS

1. COVER. Feel: that is my kid's classroom. Know: AI use is widely reported and a written policy is not. c1 c2 c3.
   A student desk at true size on a TXT.studio sweep, its laptop open and lit, the desktop beside it bare where a rule would lie.
   No count, no accent. Low three quarter, the desk filling more than half the frame.
2. USE, TEACHERS. Feel: the size of it. Know: 86 in 100 leaders reported teachers using AI. c2. FIG teacher_use_of_100, per_hundred.
   A sunlit school gym (TXT.interior) seen from the top of the bleachers, a hundred student desks, 86 laptops lit by seeded order,
   14 dark. Perspective, never top down, a custodian at the far door for scale.
3. USE, STUDENTS. Feel: it is in children's hands. Know: 61 in 100 reported student use. c2. FIG student_use_of_100, per_hundred.
   A TXBENCH relief of five separated hallway locker banks, four columns by five tiers per bank, 61 doors ajar with a cool screen light from the crack, the
   rest shut. Raking key, off axis, long casts.
4. THE TURN, STUDENT POLICY (the hardest frame). Feel: lots of glow and very little paper. Know: only 29 in 100 reported a
   district policy on student AI use. c2 c3. FIG student_policy_of_100, per_hundred. The laptop lids stay dark so only policy is counted.
   The same gym at a teacher's standing eye height, late sun through the doors, amber pocket folders on 29 desks. Every desk and
   every folder visible.
5. STAFF POLICY. Feel: teachers were not handed a rulebook either. Know: 20 in 100 reported a policy for teachers and staff. c4.
   FIG staff_policy_of_100, per_hundred. A staff mailbox wall of 10 by 10 cubbies (chassis model cubby_wall) on a TXT.studio
   sweep, 20 cubbies holding an amber sheet standing proud, a teacher's hand at one empty cubby.
6. THE STATES. Feel: Texas is missing from a shelf most states are on. Know: 42 states have issued statewide school AI guidance by
   Texas 2036's count, and Texas is not among them. c5 c6. FIG states_with_guidance. A school library (TXT.interior) with a long
   oak shelf (chassis shelf_run) of 42 ring binders (chassis ring_binder) with amber spines and blank pockets, one empty slot
   inside the run with a plain pill reading Texas. Every binder visible, no other slots drawn, no state named.
7. THE ASK. Feel: the fix is concrete and could be written. Know: the four priorities. c7 c8 c9 c10. FIG priorities.
   A TXBENCH relief of four pressboard tab dividers fanned on a desk blotter over blank leaves, four plain pills (statewide
   guidance, safety standards, teacher training, AI literacy). No amber.
8. THE PUBLIC. Feel: parents care, and they vote. Know: nearly 85% of Texas voters call student data privacy extremely or very
   important, and 71% call teaching responsible use important. c13 c15. Nothing counted in the art (no unit for voters).
   An outdoor TXT scene at after school pickup, a brick ISD wing (school), a school bus at the curb, parents at the covered walk.
9. CLOSE AND NEXT STEP. Feel: this is decided somewhere a Texan can walk into. Know: student AI policy is a district's to write
   and most leaders reported none. c3 c6. A district board room in the evening (TXT.interior), the hearing dais with one amber
   policy binder on it, the public comment podium facing it, public seating with one empty chair on the aisle nearest the camera.

Showstopper frame: 04
VALUE CUT: frame 7
The cut moves from the institutional reading room to the report's proposed priorities as a close-up of brighter paper and coloured dividers. The changed world is the story's turn, not an implied common room.

Tonal arc: warm morning studio, bright gym, cool noon hallway, gold afternoon gym, soft office, quiet library, desk close up,
open after school sky, lamplit evening board room.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | CLOSE, eye 0.9 m, three quarter from the front left, 1.6 m off the desk, fov 32 | the kit student_desk with its putty laminate top and charcoal moulded seat, and the kit laptop open and lit on it, on a TXT.studio sweep in the people tone with TXT.contact under every foot |
| 02 | WIDE, eye 7 m at the top of the bleachers, three quarter down the rows, fov 40 | a hundred kit student_desk models in ten rows on a maple gym floor in a TXT.interior gym, each with a kit laptop, 86 lit and 14 dark, a kit person at the far door for scale |
| 03 | MEDIUM, orthographic relief, the locker bank raked from the upper left | five separated hallway locker banks as a TXBENCH.relief, four columns by five tiers per bank of enamelled steel doors with pressed louvres and recessed handle cups, 61 doors ajar with a cool light from the crack |
| 04 | WIDE, eye 1.7 m at the corner of the rows, fov 38 | the same hundred kit student_desk models in the TXT.interior gym, rounded laminate tops and tubular steel legs with contact shadows, all laptops dark, and 29 chassis pocket_folder models in the accent amber lying on desks, late sun through the gym doors |
| 05 | MEDIUM, eye 1.5 m, the wall at a slight angle, fov 34 | the chassis cubby_wall of a hundred oak staff mailbox cubbies on a TXT.studio sweep, 20 holding a chassis policy_sheet in the accent amber standing proud, a kit person's hand at one empty cubby |
| 06 | AERIAL, eye 4.2 m above the reading room, the complete shelf from near its centre, fov 34 | the chassis shelf_run in honey oak with grain, lit by window light, each of its 42 chassis ring_binder models in clear coated amber vinyl with blank spine pockets standing in a contact shade, one empty slot inside the complete visible run, in a TXT.interior school library |
| 07 | MACRO, orthographic relief, four dividers fanned on a desk blotter | four pressboard tab dividers as a TXBENCH.relief fanned on a navy leather desk blotter over blank leaves, each in a different tone colour, no accent |
| 08 | WIDE, eye 1.4 m on the school drive, fov 36 | a kit school brick ISD wing with a covered walk, a kit school_bus at the curb and kit person models as parents at pickup, under TXT.sky in the people world with TXT.ground concrete and lawn |
| 09 | MEDIUM, eye 1.1 m behind an empty aisle chair, looking up the aisle, fov 34 | a kit hearing_dais in a TXT.interior district board room in the evening, one chassis ring_binder in the accent amber on the dais, a kit podium facing it, kit public_seating with one empty chair on the aisle nearest the camera |

Showstopper frame: 04, the sunlit gym at a teacher's eye height, a hundred desks with their laptop lids dark and only 29 amber folders among them. Its depth is the rows receding from the lens, each desk occluding the next and casting onto the maple.
Tonal arc: warm morning studio on 01, a bright gym on 02, a cool hallway noon on 03, gold afternoon in the gym on 04, soft office light on 05, a quiet library on 06, a desk close up on 07, the open after school sky on 08, the lamplit evening board room on 09.

---

```yaml
slide: 1
layout: OBJECT_AND_CAPTION
primary_image:
  subject: one student desk at true size on a warm studio sweep, its laptop open and lit, the bare laminate beside the laptop where a written rule would lie
  rect: [432, 234, 636, 750]
  bleeds: []
accent: '#ff9f1c'
job: Put the story in one familiar object before any figure is read, a school desk with AI on it and nothing written beside it.
claims: [c1, c2, c3]
numerals:
- {value_from: c1}
- {value_from: c2}
depth:
  eye: 0.9
  horizon: 420
  cues: [LINEAR_PERSPECTIVE, CAST_SHADOW, FORM_SHADING, OCCLUSION]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'BESPOKE. The slide artist composes the picture and places the type where this picture leaves quiet (knowledge/carousel/BESPOKE.md). CLOSE, eye 0.9 m, three quarter from the front left, 1.6 m off the desk, fov 32.', bands: 'Top third, the warm sweep wall with room for the type wherever the artist seats it. Middle third, the laptop lid and screen and the desk top catching the key. Bottom third, the foreground: the chrome legs and the moulded seat on the apricot floor, each foot in a soft contact shadow, the seat shell modelled with a rim of light.', focal: the lit laptop screen and the empty laminate beside it}
art: {technique: 'physically based render of the kit student_desk and laptop in a TXT.studio sweep, LOOK V2 people tone', why_this_technique: 'a desk and a laptop are the two things every reader can picture in a Texas classroom, and the bare desktop beside the screen is the absence the story is about', palette: 'putty laminate, charcoal seat shell, brushed aluminium, the people sweep from apricot floor to periwinkle wall, plum shadow', value_structure: Lightest is the lit laptop screen and the key on the laminate. Darkest is the plum shadow under the desk. No near black field.}
verbatim: []
acceptance: [the kit student_desk spans at least 540 px of the frame width at 1080 px, the laptop screen is lit and is the brightest region of the frame, nothing in the accent amber appears anywhere in the frame, the desk's feet stand in a contact shadow on the sweep, no numeral on this slide is absent from claims.json, 'the desk spans at least 540 px at 1080 px, measured on the art', 'the kit student_desk with its putty laminate top and charcoal moulded seat is present and modelled, never a primitive stand in']
risks: []
type:
  hook: "Only 29% of school leaders reported a student AI policy"
  dek: "Texas 2036 said on November 10th that 86% of Texas school and district leaders reported teachers using AI in fall 2025. The desk and its empty sheet protector are drawn to illustrate."
  labels: []
```

```yaml
slide: 2
layout: FULL_BLEED
primary_image:
  subject: a sunlit school gym from the top of the bleachers, a hundred desks in ten rows, eighty six laptops lit and fourteen dark, a custodian at the far door
  rect: [0, 0, 1080, 1350]
  bleeds: [left, right, bottom]
accent: '#ff9f1c'
data_in_art: {figure: teacher_use_of_100, drives: 'the number of lit laptops among the hundred desks, eighty six, chosen by a seeded shuffle so the lit ones do not cluster'}
job: Make the share of leaders who reported teacher use something a stranger can see, a gym of a hundred desks mostly lit.
claims: [c2]
numerals:
- {value_from: c2}
depth:
  eye: 7.0
  horizon: 180
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'BESPOKE. The slide artist composes the picture and places the type where this picture leaves quiet (knowledge/carousel/BESPOKE.md). WIDE, eye 7 m at the top of the bleachers, three quarter down the rows, fov 40.', bands: 'Top third, the gym wall and clerestory windows with the type in the quiet of the wall. Middle third, the far rows of desks with their screens. Bottom third, the foreground: the near rows at full size on the maple boards, each desk casting onto the floor, the court line paint and the board grain lit by the sun shafts.', focal: the field of lit screens}
art: {technique: 'physically based render of the kit student_desk, laptop and person in a TXT.interior gym with clerestory light', why_this_technique: 'one desk per leader in a hundred turns a percentage into a room a parent can count, and a gym is the one school room that holds a hundred desks', palette: 'maple floor with court lines, putty desk tops, cool white screen glow, brick wall, clerestory sun, plum shadow', value_structure: Lightest is the clerestory shafts and the lit screens. Darkest is the plum shade under the bleacher end. Mid tones carry colour.}
verbatim: []
acceptance: ['the frame''s code builds exactly FIG.per_hundred desks and lights exactly FIG.teacher_use_of_100 laptops, and throws if either differs', 'no camera looks straight down, the floor recedes in perspective', the lit and dark laptops are told apart at 432 px, a kit person stands in the gym for scale, nothing in the accent amber appears in the frame, 'the field of desks fills at least half the frame height at 1080 px wide at 1080 px, measured on the art', 'a hundred kit student_desk models in ten rows on a maple gym floor in a TXT.interior gym is present and modelled, never a primitive stand in']
risks: []
type:
  hook: "86% of leaders reported teachers using AI"
  dek: "Texas school and district leaders, fall 2025, per Texas 2036. Drawn to illustrate, one desk for each leader in a hundred. A lit laptop marks reported teacher use."
  labels: []
```

```yaml
slide: 3
layout: GRID
primary_image:
  subject: the counted door field across five separated school hallway locker banks, a hundred doors, sixty one standing ajar with a cool screen light inside, the rest shut
  rect: [12, 114, 1056, 732]
  bleeds: []
accent: '#ff9f1c'
data_in_art: {figure: student_use_of_100, drives: 'the number of locker doors standing ajar, sixty one, each throwing a cast across its neighbour'}
job: Carry student use as a hundred lockers with sixty one open, a different school object at the same unit.
claims: [c2]
numerals:
- {value_from: c2}
depth:
  eye: 0
  horizon: 0
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'BESPOKE. The slide artist composes the picture and places the type where this picture leaves quiet (knowledge/carousel/BESPOKE.md). MEDIUM, orthographic relief, the locker bank raked from the upper left.', bands: 'Top third, the tops of the lockers and the hallway wall with the type. Middle third, the open and shut doors with their louvres and casts. Bottom third, the foreground: the bottom tier of doors and the terrazzo floor strip with its aggregate, the open doors casting long shadows across the shut ones.', focal: the open doors and their light}
art: {technique: 'TXBENCH.relief height field of the locker bank on TXLOOK.sky2d with TXLOOK.reliefLight, at least two materials', why_this_technique: 'lockers are where a student keeps a device, and an open door is a gesture a reader reads as in use without a legend', palette: 'saturated teal enamel, brushed steel handle cups, terrazzo floor strip, cool screen light, plum cast shadow', value_structure: Lightest is the key on the door bevels and the light from the cracks. Darkest is the cast inside the open doors. Colour in every mid tone.}
verbatim: []
acceptance: ['the frame''s code builds exactly FIG.per_hundred doors and opens exactly FIG.student_use_of_100, and throws if either differs', 'the relief report shows at least two materials, a real height range and cast shadows', open doors read as open at 432 px, the camera or key is off axis so the bank never reads as a flat grille, nothing in the accent amber appears in the frame, 'the hallway locker banks stand at least 700 px tall at 1080 px frame width and every counted door is inside its measured primary image rectangle', 'a hallway locker bank as a TXBENCH.relief is present and modelled, never a primitive stand in']
risks: []
type:
  hook: "61% reported students using it too"
  dek: "Same leaders, same fall 2025 survey, per Texas 2036. Drawn to illustrate, one locker for each leader in a hundred. An open door marks reported student use."
  labels: []
```

```yaml
slide: 4
layout: FULL_BLEED
primary_image:
  subject: the gym from a raised corner, late sun through the doors, a hundred desks with their laptops dark and 29 amber folders among them
  rect: [0, 0, 1080, 1350]
  bleeds: [left, right, bottom]
accent: '#ff9f1c'
data_in_art: {figure: student_policy_of_100, drives: 'the number of amber pocket folders lying on the desks, 29; no other survey share is drawn on this frame'}
job: Turn the deck from use to rules, the same room with only 29 written policies in it.
claims: [c2, c3]
numerals:
- {value_from: c2}
- {value_from: c3}
depth:
  eye: 1.7
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'BESPOKE. The slide artist composes the picture and places the type where this picture leaves quiet (knowledge/carousel/BESPOKE.md). WIDE, eye 1.7 m at the corner of the rows, fov 38.', bands: 'Top third, the gym wall and doors with the sun and the type. Middle third, the receding rows with screens and folders. Bottom third, the foreground: the nearest desks at full size, a folder on a laminate top in sharp detail, the maple boards and their shadows.', focal: the nearest amber folder on a desk}
art: {technique: physically based render of the kit desks and laptops and the chassis pocket_folder in the TXT.interior gym, why_this_technique: 'the same hundred desks carry only the policy share in amber, without implying a joint distribution with teacher use', palette: 'maple floor, putty desk tops, dark laptop lids, amber folders, gold late sun, plum shade', value_structure: Lightest is the amber folders and laminate tops. Darkest is the plum shade under the near desks. The amber folders are the most saturated thing in the frame.}
verbatim: []
acceptance: ['the frame''s code builds exactly FIG.per_hundred desks and places exactly FIG.student_policy_of_100 amber folders, lights no laptop, and throws if either differs', every folder is visible at full size, the amber appears only on the folders, 'the camera stands at eye height, not above the rows', no numeral on this slide is absent from claims.json or figures.json, 'the rows of desks fill at least half the frame height at 1080 px, measured on the art', 'the same hundred kit student_desk models in the TXT.interior gym is present and modelled, never a primitive stand in']
risks: []
type:
  hook: "A student AI policy, reported by 29%"
  dek: "One desk for each leader in a hundred, drawn to illustrate. An amber folder marks a leader who reported a district policy governing student AI use."
  labels: []
```

```yaml
slide: 5
layout: OBJECT_AND_CAPTION
primary_image:
  subject: a staff mailbox wall of a hundred oak cubbies, twenty holding an amber sheet, a teacher reaching into an empty one
  rect: [0, 0, 1080, 1350]
  bleeds: [left, right, bottom]
accent: '#ff9f1c'
data_in_art: {figure: staff_policy_of_100, drives: 'the number of cubbies holding an amber policy sheet, twenty, the rest empty or holding plain memos'}
job: Show that a written policy for teachers was reported even more rarely, twenty sheets in a hundred mailboxes.
claims: [c4]
numerals:
- {value_from: c4}
depth:
  eye: 1.5
  horizon: 600
  cues: [LINEAR_PERSPECTIVE, CAST_SHADOW, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'BESPOKE. The slide artist composes the picture and places the type where this picture leaves quiet (knowledge/carousel/BESPOKE.md). MEDIUM, eye 1.5 m, the wall at a slight angle, fov 34.', bands: 'Top third, the upper rows of cubbies and the sweep with the type. Middle third, the cubby rows with the amber sheets. Bottom third, the foreground: the lowest rows and the plinth on the sweep floor, the teacher''s hand and sleeve at an empty cubby, deep shadows inside each cell.', focal: the amber sheets standing proud}
art: {technique: physically based render of the chassis cubby_wall and policy_sheet with a kit person in a TXT.studio sweep, why_this_technique: 'every teacher checks a staff mailbox, so a sheet in it is the plainest picture of a policy handed to staff', palette: 'honey oak cubbies, brass label rails, amber sheets, cream memos, plum shadow inside each cubby, the people sweep', value_structure: Lightest is the key on the oak faces and the sheets. Darkest is the cast inside the deep cubbies.}
verbatim: []
acceptance: ['the frame''s code places exactly FIG.staff_policy_of_100 amber sheets in a wall of FIG.per_hundred cubbies, and throws if either differs', the cubby interiors read as deep at 432 px, the amber appears only on the policy sheets, a kit person or hand gives the wall human scale, no numeral on this slide is absent from claims.json or figures.json, 'the cubby wall spans at least 700 px of the frame width at 1080 px, measured on the art', 'the chassis cubby_wall of a hundred oak staff mailbox cubbies on a TXT.studio sweep is present and modelled, never a primitive stand in']
risks: []
type:
  hook: "Just 20% reported a policy for staff"
  dek: "A policy for teachers and staff, per Texas 2036. Drawn to illustrate, one staff mailbox for each leader in a hundred, an amber sheet where a leader reported one."
  labels: []
```

```yaml
slide: 6
layout: OBJECT_AND_CAPTION
primary_image:
  subject: a complete oak library shelf of forty two sharp amber binders, one empty slot inside the run with a plain pill reading Texas
  rect: [0, 0, 1080, 1350]
  bleeds: [left, right, bottom]
accent: '#ff9f1c'
data_in_art: {figure: states_with_guidance, drives: 'the number of amber binders on the shelf, forty two, with one further empty slot for Texas and no other slots drawn'}
job: Put Texas in the one empty place on a shelf of states that have issued guidance.
claims: [c5, c6]
numerals:
- {value_from: c5}
- {value_from: c6}
depth:
  eye: 1.0
  horizon: 560
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'BESPOKE. The slide artist composes the picture and places the type where this picture leaves quiet (knowledge/carousel/BESPOKE.md). AERIAL, eye 4.2 m above the reading room, the complete shelf from near its centre, fov 34.', bands: 'Top third, the library wall with the type. Middle third, the shelf and the binders receding. Bottom third, the foreground: the empty slot and its oak floor with a soft contact shade, the shelf front edge and the near binders sharp.', focal: the empty slot}
art: {technique: physically based render of the chassis shelf_run and ring_binder in a TXT.interior library, why_this_technique: 'statewide guidance is a document a district keeps on a shelf, and an empty slot is an absence a reader sees without a sentence', palette: 'oak shelf, amber binder spines, clear spine pockets, library window light, plum wall', value_structure: Lightest is the key along the binder spines and the empty slot's floor. Darkest is the back of the shelf behind the binders.}
verbatim: []
acceptance: ['the frame''s code builds exactly FIG.states_with_guidance amber binders and one empty slot, and throws if the count differs', no state name appears on any binder, all binders and the empty slot are sharp and inside the frame, no total count of states is printed or drawn, the label Texas sits at the empty slot, 'the shelf and its binders span at least 800 px of the frame width at 1080 px, measured on the art', 'the chassis shelf_run in honey oak with grain is present and modelled, never a primitive stand in']
risks: []
type:
  hook: "42 states have issued school AI guidance. Not Texas."
  dek: "Some form of statewide AI guidance, model policy, framework or support for schools, by Texas 2036's count. Texas is not among them. One binder per state, drawn to illustrate."
  labels:
  - "Texas"
```

```yaml
slide: 7
layout: DIAGRAM
primary_image:
  subject: four pressboard tab dividers fanned on a desk blotter over blank pages, each tab carrying one priority as a plain pill
  rect: [0, 0, 1080, 1350]
  bleeds: [left, right, bottom]
accent: '#ff9f1c'
data_in_art: {figure: priorities, drives: 'the number of tab dividers, four, read from figures.json'}
job: Name the four things the report asks for as an outline with blank pages behind it.
claims: [c7, c8, c9, c10]
numerals:
- {value_from: c7}
- {value_from: c8}
depth:
  eye: 0
  horizon: 0
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'BESPOKE. The slide artist composes the picture and places the type where this picture leaves quiet (knowledge/carousel/BESPOKE.md). MACRO, orthographic relief, four dividers fanned on a desk blotter.', bands: 'Top third, the blotter with the type. Middle third, the fanned tabs and their pills. Bottom third, the foreground: the divider edges and blank leaves stacked at measured heights, each casting onto the blotter, the leather grain lit.', focal: the four tabs}
art: {technique: TXBENCH.relief height field of dividers and blotter on TXLOOK.sky2d with TXLOOK.reliefLight, why_this_technique: 'a divider is the start of a rulebook with nothing written in it yet, which is exactly what a list of priorities is', palette: 'cerulean, mint, apricot and periwinkle pressboard, cream blank leaves, navy leather blotter, plum casts', value_structure: Lightest is the key on the tab edges and the blank leaves. Darkest is the cast under the fanned dividers.}
verbatim: []
acceptance: ['the frame''s code draws exactly FIG.priorities dividers, and throws if the count differs', the relief report shows at least two materials and cast shadows, nothing in the accent amber appears in the frame, each tab carries one plain pill naming one priority, no numeral on this slide is absent from claims.json or figures.json, 'the fanned dividers own at least half the frame area at 1080 px, measured on the art', 'four pressboard tab dividers as a TXBENCH.relief fanned on a navy leather desk blotter over blank leaves is present and modelled, never a primitive stand in']
risks: []
type:
  hook: "The report names four priorities"
  dek: "Statewide guidance for every district. Safety standards before AI tools reach classrooms. Training for teachers. Age appropriate AI literacy for students."
  labels:
  - "Statewide guidance"
  - "Safety standards"
  - "Teacher training"
  - "AI literacy"
```

```yaml
slide: 8
layout: SPLIT_HORIZON
primary_image:
  subject: after school pickup at a brick Texas campus, a school bus at the curb, parents waiting at the covered walk under a warm late sky
  rect: [0, 0, 1080, 1350]
  bleeds: [left, right, bottom]
accent: '#ff9f1c'
job: Bring in the voters as parents at the curb, kept apart from the school leaders.
claims: [c13, c15]
numerals:
- {value_from: c13}
- {value_from: c15}
depth:
  eye: 1.4
  horizon: 640
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'BESPOKE. The slide artist composes the picture and places the type where this picture leaves quiet (knowledge/carousel/BESPOKE.md). WIDE, eye 1.4 m on the school drive, fov 36.', bands: 'Top third, the late sky with the type. Middle third, the school wing and the bus. Bottom third, the foreground: the concrete drive and curb with the bus wheels and the parents'' feet in contact shadows, the lawn verge.', focal: the parents at the covered walk}
art: {technique: 'physically based render of the kit school, school_bus and person under TXT.sky with TXT.ground, TXT.contact and TXT.weather', why_this_technique: 'the people who answer a voter poll about schools are the parents at the curb, and an outdoor frame breaks the run of rooms', palette: 'red ISD brick with cast stone bands, school bus chrome yellow, concrete walk, lawn, periwinkle sky, apricot key', value_structure: Lightest is the sky and the key on the brick. Darkest is the plum shade under the covered walk.}
verbatim: []
acceptance: [the frame stands under TXT.sky and the render report says SKY IN FRAME, 'a kit school_bus and kit person models are used, never primitive stand ins', no count of voters is drawn, nothing in the accent amber appears in the frame, no numeral on this slide is absent from claims.json, 'the school wing and bus together span at least 760 px of the frame width at 1080 px, measured on the art', 'a kit school brick ISD wing with a covered walk is present and modelled, never a primitive stand in']
risks: []
type:
  hook: "Nearly 85% of Texas voters call student privacy important"
  dek: "They call protecting student data and privacy extremely or very important if schools use AI, Texas 2036 says. In the same reporting, 71% call teaching responsible use important."
  labels: []
```

```yaml
slide: 9
layout: OBJECT_AND_CAPTION
primary_image:
  subject: a district board room in the evening, the trustees' dais with one amber policy binder on it, the public comment podium, and an empty chair on the aisle nearest the reader
  rect: [0, 0, 1080, 1350]
  bleeds: [left, right, bottom]
accent: '#ff9f1c'
job: Hand the reader the next step, the room where a district writes its policy, with a seat left for them.
claims: [c3, c5, c6]
numerals:
- {value_from: c3}
- {value_from: c5}
depth:
  eye: 1.1
  horizon: 560
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'BESPOKE. The slide artist composes the picture and places the type where this picture leaves quiet (knowledge/carousel/BESPOKE.md). MEDIUM, eye 1.1 m behind an empty aisle chair, looking up the aisle, fov 34.', bands: 'Top third, the dais and the wall with the type. Middle third, the dais front, the binder and the podium. Bottom third, the foreground: the empty aisle chair and the seat backs beside it, the carpet aisle receding, each chair in a contact shadow.', focal: the amber binder on the dais}
art: {technique: 'physically based render of the kit hearing_dais, podium and public_seating and the chassis ring_binder in a TXT.interior board room', why_this_technique: 'a district policy is adopted in this room, and an empty chair invites the reader into it without a call to action', palette: 'walnut dais, plum walls, amber lamps, the amber binder, navy seat fabric, warm evening light', value_structure: Lightest is the lamps on the dais and the amber binder. Darkest is the plum wall behind. No near black field.}
verbatim: []
acceptance: [the frame stands in a room TXT.interior builds and the render report says ROOM IN FRAME, 'exactly one amber binder appears, on the dais', the empty chair on the aisle is the nearest object, 'kit models are used for the dais, podium and seating', no numeral on this slide is absent from claims.json, 'the dais spans at least 520 px of the frame width at 1080 px, measured on the art', 'a kit hearing_dais in a TXT.interior district board room in the evening is present and modelled, never a primitive stand in']
risks: []
type:
  hook: "Ask your district whether it has an AI policy"
  dek: "Only 29% of Texas school and district leaders reported a district policy on student AI use, per Texas 2036. Texas is not among its 42 states with statewide guidance."
  labels: []
```
