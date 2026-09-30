# Storyboard, 2026-09-30
# "A machine reads it first."

## The story, and what the fact check did to it

The Texas Education Agency scores the written answers on English language STAAR tests with an
automated scoring engine first, and at least 25 percent then go to human scorers (c1). The agency's
own chart puts the engine's score as the score of record on about 75% of answers (c13). The rest
are double human scored, one score of record and one audit (c31): a random sample (c32), answers the
engine flags with condition codes (c6) and answers it scores with low confidence, often on the
border between two score points (c7). A person's score is the score of record (c3). Spanish
language written answers are 100 percent human scored (c2). For each question the engine is
programmed on about 3,000 answers people scored in field tests (c16, c4), and the agency requires it
to agree with scorers as often as scorers agree with one another (c5). Hybrid scoring began in
December 2023 (c17). This fall the agency's annual review gave about 27,200 students more credit
(c19) after content experts reread short typed answers (c21), and the agency said none of those had
been scored by the engine (c20). About 1.7% of more than 1.6 million exams reviewed improved (c24),
and no score went down (c30). A parent or guardian with a concern can ask the district, whose
testing staff can request a rescore for a fee (c12, c9). A rescore goes to people (c10), and the fee
is waived if the score changes (c11). The record admitted this today as tx-2026-0194.

**WHAT THE FACT CHECK CHANGED.**
- **No "11 districts improved".** The headline said so and the body did not (rejected). The deck
  never prints a district count.
- **The ~3,000 is per question**, from the slide's own heading (c16 note). The deck says "for each
  question".
- **Nothing about the engine's accuracy.** The claims hold the agency's requirement (c5), never a
  measured error, and the September corrections were answers the engine never scored (c20).
- **No fee amount, no window date, no vendor, no location for any scoring.** None is in the claims.
- **No rubric frame.** The rubric's point scales are in no claim, so a director's rubric poster and
  score bars were cut.
- **No map.** No claim places the districts, and two of their names are not towns.

## Why this treatment, and what was grafted

Three directors pitched CONSEQUENCE AND SCALE, THE PROCEDURE SHOWN AS A ROUTE and THE READER'S
HAND. All three chose overcast light, bluebonnet as the one accent and a Texas ISD campus as the
ground, and two of them independently chose one student desk as the thing a reader can stand in
for an answer. Three directors meeting there without seeing each other is the room's strongest
evidence.

The deck is CONSEQUENCE AND SCALE's spine: one student combo desk, carried from one desk alone on a
practice field to a football field of 3,000, a block of 100 where 25 have two readers, and back.

- From THE READER'S HAND: the turn. Frame 7 is frame 1's field filled with 27,200 desks from the
  camera frame 1 stood in, and the ending with a parent at the desk.
- From THE PROCEDURE: the covered walkway, which the parent walks on frame 8 to the district's door,
  and the discipline that grey never reads as bad.
- Refused: the scoring route as invented architecture (a judge would read a building that does not
  exist), paper bundles for digital answers, the rubric poster and score bars (not in the claims),
  the painted map (no locations in the claims).

## The world, and the laws that hold it

**A TEXAS ISD CAMPUS ON A GREY SEPTEMBER MORNING.** The chassis is
`assets/js/deck/2026-09-30-firstreader.js` and every frame loads it. It declares `sky: overcast`,
tuned toward a cool, luminous lid (never cream), and one light at azimuth -40, elevation 48. +x is
east, -z is north. The school wing stands north of the practice field, its long face toward the
south. The world table's line for overcast is procedure, a filing, a waiting room, and this story is
a procedure with no villain and no verdict. Soft light also keeps a count countable: 3,000 hard
shadows would double every desk.

The hero is `student_desk`, a kit addition in the chassis: a one piece combo chair desk with a putty
laminate top, a bent black tube frame and a charcoal shell, the laptop from the kit on it. A field
of any count is drawn as instanced low detail desks (`FR.field`).

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#D7D9DA` | the DOM body behind the render |
| `accent` | `#4E5FA8` | bluebonnet, a person reading an answer. Only the shirts of the readers, seated at a screen or leaning over one. The parent wears her own shirt, never the accent, so she never reads as staff. Frames 3, 4, 5, 6 and 7 |
| `hook` | `#12131A` | the hook |
| `dek` | `#1E2028` | the dek |
| `rule` | `#2A2C33` | the site line, the source line and the counter |

The world's own colours are lit materials: buff ISD brick with cast stone bands, late September
bermuda gone to straw, galvanized chain link, putty laminate, charcoal seat shells and a cool grey
lid of cloud.

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE
    VALUE CUT: none

1. **Motif evolution.** The number of people standing at the desk is the progress indicator: none
   on 1 and 2, two at a quarter of the desks on 3, two at the one on 4, one at every desk on 5, one
   reading at one desk deep in the full field on 7, a parent on the walk on 8, and the parent leaning over the desk on 9.
2. **Camera move.** One campus from nine positions. Frames 1 and 9 share one camera exactly, the
   empty desk and the parent at it, and frame 7 is the crane up from that same seat over the full
   field. Frames 3 and 6 share one camera, a quarter attended of a hundred and a few of a thousand.

## The rotation

    FULL_BLEED  FULL_BLEED  FIGURE_SCALE  DIAGRAM  FIGURE_SCALE  SPLIT_HORIZON  FULL_BLEED  OBJECT_AND_CAPTION  FULL_BLEED

Frame 3 was declared GRID and re-declared FIGURE_SCALE on the first render. After the critics' round, frame 3's attended quarter is drawn as the far left quarter of the square, because the near one swelled to half the block in perspective, frame 6 was redrawn from frame 3's camera as one thousand desks, the improved seventeen with a content expert seated at a lit screen, frame 7 became a crane from frame 1's seat to 7.2 m so the full field reads larger than frame 2, and frame 8 gained the covered entry walk its dossier named: from the light pole the block of one hundred comes apart into one mass at thumb scale, so its count is carried by the readers standing at a quarter of the desks, which give every desk its size.

`TXLAYOUT.check` returns an empty list.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "one student combo desk alone on a straw practice field with its laptop open and lit, the school wing, flags and live oaks soft in haze behind it"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: none
job: >
  Stop the scroll on one desk that stands for one child's answer, and say the whole story in the
  hook, a machine is the first reader.

claims: [c1, c17, c2, c14, c22]
numerals:
  - value_from: c17
  - value_from: c1

depth:
  eye: 1.1
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, CAST_SHADOW, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: -3}

composition:
  structure: >
    A seated eye camera close to one desk so the desk owns the lower frame and the school on the
    horizon gives it a place, the empty field between them the distance a reader feels.
  bands: >
    Top third, the luminous lid of cloud holding the hook and dek. Middle third, the school wing,
    flagpole and oaks on the horizon in haze. Bottom third, the desk, the laptop's lit screen, the
    straw grass and the desk's contact on it.
  focal: "the lit laptop screen on the desktop against the dark seat shell"

art:
  technique: "physically based render through txthree.js in the deck's overcast world"
  why_this_technique: "the claim is about every child's answer, and a real desk on a real field is the one object every Texan has sat at"
  palette: "straw bermuda, buff ISD brick, putty laminate, charcoal shell, a cool grey sky"
  value_structure: >
    Lightest is the sky's lid behind the type and the laptop screen. Darkest is the seat shell and
    the book rack's shadow. Frame median L* planned at 66.

type:
  hook: "A machine reads it first."
  dek: "Since December 2023 the Texas Education Agency has sent the longer written STAAR answers to an automated engine first, unless the test is in Spanish. The agency said scoring every answer by hand would have cost $15 million to $20 million more a year."
  labels: []

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 57 and 75"
  - 'the hook reads "A machine reads it first."'
  - "the desk reads as a school combo chair desk at 432px, seat and top both visible"
  - "the laptop screen is lighter than every other part of the desk at 432px"
  - "the school wing and a flag read on the horizon, below the dek's last line"
  - "the desk touches the ground with a contact darker than the grass beside it"
  - "no type crosses the desk"

risks:
  - "an overcast sky reads as a flat grey card, so the lid is tuned lighter at the horizon and the haze carries the school"
```

```yaml
slide: 2
layout: FULL_BLEED
primary_image:
  subject: "a high school football field covered goal line to goal line with 3,000 identical student desks in exact rows, a yellow goal post near, the school wing and oaks hazed beyond"
  rect: [0, 520, 1080, 830]
  bleeds: [left, right, bottom]
accent: none
job: >
  Make the engine's training a size, the number of answers people scored for it, one desk each.

claims: [c16, c4, c5]
numerals:
  - value_from: c16

data_in_art:
  figure: training_sample
  drives: mark count, one instanced desk per human scored answer

depth:
  eye: 9
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, TEXTURE_GRADIENT, OCCLUSION]
  subject_at: {X: 0, Z: -45}

composition:
  structure: >
    From the stands behind the end zone, the rows run away down the field so the count is felt as
    depth before it is read, the goal post in the near corner setting the scale.
  bands: >
    Top third, sky and type. Middle third, the far rows melting into haze at the school and oaks.
    Bottom third, the lit foreground, the near rows of desks modelled at full detail, their charcoal seat shells and putty tops catching the soft key, their contacts on the turf, the white yard lines running between them, and the yellow goal post rising in the near corner.
  focal: "the near rows of desks, each with its own soft contact"

art:
  technique: "instanced render of 3,000 desks at true scale on the kit ground"
  why_this_technique: "a count only becomes a size when it stands somewhere a reader knows the size of, and every Texan knows a football field"
  palette: "field green gone straw, white yard lines, charcoal shells, putty tops, goal post yellow"
  value_structure: >
    Lightest is the sky and the far haze. Darkest is the seat shells in the near rows. Frame median L* planned at 59.

type:
  hook: "About 3,000 answers taught it."
  dek: "For each question the engine is programmed on about 3,000 field test answers that people scored. The agency requires it to agree with scorers as often as scorers agree with each other."
  labels: []

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 49 and 67"
  - 'the hook reads "About 3,000 answers taught it."'
  - "the render report's instance count for the field equals figures.json training_sample"
  - "at least four near rows read as separate rows of desks at 432px"
  - "the far rows fade into haze rather than ending on a hard edge"
  - "the goal post reads as a goal post"
  - "no type crosses a desk"

risks:
  - "3,000 desks read as texture at feed size, so the near rows are full detail and the camera is low enough to show seats"
```

```yaml
slide: 3
layout: FIGURE_SCALE
primary_image:
  subject: "a block of 100 student desks on the practice field in a ten by ten grid, 25 of them each read by two adults in bluebonnet shirts, one seated at the screen and one leaning in at its side, the other 75 alone with screens lit"
  rect: [0, 600, 1080, 750]
  bleeds: [left, right, bottom]
accent: "#4E5FA8"
job: >
  Show the agency's own split as a block a reader can count, three in four alone and one in four
  with two people.

claims: [c13, c31, c3]
numerals:
  - value_from: c13

data_in_art:
  figure: per100_people
  drives: mark count, the desks with two readers at them, of a block of per100_engine plus per100_people

depth:
  eye: 7
  horizon: 590
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: -18}

composition:
  structure: >
    A long lens from a light pole's platform so the grid compresses into countable rows, with the
    readers, one standing proud of each attended desk as the one vertical in the block.
  bands: >
    Top third, sky and type. Middle third, the school wing and the far rows. Bottom third, the near rows of desks at full detail with the readers at them, their bluebonnet shirts and dark trousers modelled by the soft key, each figure's contact on the straw grass, and the laptops' lit screens.
  focal: "a near desk with its two readers in bluebonnet"

art:
  technique: "isotype grid rendered at true scale, long lens compression"
  why_this_technique: "a share wants units a reader can count, and people standing at a desk are what the share means"
  palette: "straw grass, charcoal shells, bluebonnet shirts, buff brick"
  value_structure: >
    Lightest is the sky and the lit screens. Darkest is the shells and the readers' trousers. Frame median L* planned at 62.

type:
  hook: "About 75% keep the machine's score."
  dek: "In the agency's own chart the engine sets the score of record on about 75% of answers. Two people read the rest. A person's score is the one that counts."
  labels: []

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 52 and 70"
  - 'the hook reads "About 75% keep the machine''s score."'
  - "the render report counts per100_people desks with readers and per100_engine desks without"
  - "each reader sits in a seat or stands on the ground with a contact, turned to the screen, and reads as a person reading"
  - "the bluebonnet shirts are the only saturated blue in the frame"
  - "the grid's rows read as rows at 432px"
  - "no type crosses a reader"

risks:
  - "fifty kit people cost render time, so the block is probed first"
```

```yaml
slide: 4
layout: DIAGRAM
primary_image:
  subject: "one desk with two readers at it, one seated at the screen and one leaning in at its side, close, with three plain desks beside it, and mono labels on leaders naming what sends an answer to people"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#4E5FA8"
job: >
  Name what sends an answer to people, the strange ones, the close calls and a random draw.

claims: [c33, c34, c6, c7, c32]
numerals: []

data_in_art:
  figure: per4_people
  drives: mark count, one of every four desks in the row has readers, per4_engine have none

depth:
  eye: 1.6
  horizon: 620
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0.6, Z: -4}

composition:
  structure: >
    Standing eye off the end of a row of four desks, the nearest with two readers, so the labels can point
    at a real thing rather than at a box.
  bands: >
    Top third, sky and type. Middle third, the readers' heads and the school on the horizon.
    Bottom third, the lit foreground, the four desks modelled close, their seat shells, tube frames and book racks, the two readers' legs and contacts on the grass, and the leaders' ends landing on the readers' desk.
  focal: "the two readers leaning to one screen"

art:
  technique: "render with DOM SVG leaders and mono labels"
  why_this_technique: "a mechanism wants a diagram, and the thing it explains is the two people at a desk"
  palette: "straw, charcoal, bluebonnet shirts"
  value_structure: >
    Lightest is the sky. Darkest is the readers' trousers and the shells. Frame median L* planned at 68.

type:
  hook: "Low confidence scores go to people."
  dek: "So do answers that are blank, too short, in another language, off topic or worded unlike the answers the engine learned from. So does a random sample."
  labels: ["LOW CONFIDENCE", "CONDITION CODE", "RANDOM SAMPLE"]

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 58 and 76"
  - 'the hook reads "Low confidence scores go to people."'
  - "four desks read as four desks, one with two readers"
  - "every leader lands within 24px of the readers' desk"
  - "no leader crosses a letter"
  - "the readers touch the ground with contacts"

risks:
  - "labels over a busy field fail contrast, so they sit in the sky band and the leaders drop to the readers' screen"
```

```yaml
slide: 5
layout: FIGURE_SCALE
primary_image:
  subject: "a classroom row of five student desks along a window wall, an adult reader in bluebonnet seated at every one, bent to the screen"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#4E5FA8"
job: >
  Show the one route the machine never touches, the Spanish language test, every answer with a
  person.

claims: [c2]
numerals:
  - value_from: c2

data_in_art:
  figure: spanish_human_pct
  drives: mark count, readers drawn per desk row, spanish_human_pct of the row's desks get one

depth:
  eye: 1.2
  horizon: 640
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: -4}

composition:
  structure: >
    A room seen from a seated eye across a row, a window band at sill height on the far wall carrying the light and the pale wall
    carrying the type, every desk attended.
  bands: >
    Top third, the pale wall and window light with the type. Middle third, the readers. Bottom third, the five desks at full detail, their shells and tube frames modelled by the window light, the readers' legs, and the contacts where every glide and shoe meets the tiled floor.
  focal: "the nearest reader beside the nearest desk"

art:
  technique: "render in a room TXT.interior builds, window as soft light, the deck's key casting"
  why_this_technique: "the claim is people reading, and a room is where people read"
  palette: "painted block wall, VCT floor, putty laminate, bluebonnet"
  value_structure: >
    Lightest is the window and wall. Darkest is the shells and trousers. Frame median L* planned at 64.

type:
  hook: "Spanish STAAR answers skip the machine."
  dek: "Written answers on the Spanish language STAAR are 100 percent human scored."
  labels: []

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 54 and 72"
  - 'the hook reads "Spanish STAAR answers skip the machine."'
  - "five desks and five readers read as separate figures at 432px"
  - "the render report counts one reader at every desk"
  - "the room has a lit window and walls that take shadows"
  - "no type crosses a reader's head"

risks:
  - "a room goes dark and bleak, so the interior light is raised and the camera faces the window wall"
```

```yaml
slide: 6
layout: SPLIT_HORIZON
primary_image:
  subject: "frame 3's camera on the practice field, now one thousand desks in rows to the school, one per exam, every screen dark except a seeded seventeen, which are lit, a content expert in bluebonnet seated at each"
  rect: [0, 620, 1080, 730]
  bleeds: [left, right, bottom]
accent: "#4E5FA8"
job: >
  Put the review on one scale, the share of exams that improved as a few lit screens in a thousand, drawn as the content experts whose rereading raised a score, seated at lit screens among dark ones.

claims: [c24, c21, c19]
numerals:
  - value_from: c24

data_in_art:
  figure: per1000_improved
  drives: mark count, the lit screens with an expert seated at them, of one thousand desks drawn

depth:
  eye: 7.5
  horizon: 560
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, TEXTURE_GRADIENT, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: -34}

composition:
  structure: >
    One level horizon cut, the rows of desks running away below it to the school, the sky above
    it holding the type.
  bands: >
    Top third, sky and type. Middle third, the far straight and the school. Bottom third, the near rows of desks at full detail with their screens dark and contacts on the straw, the lit screens scattered through the middle rows, and the kerb and infield grass beside them.
  focal: "the few experts at lit screens among the dark ones"

art:
  technique: "instanced render at true scale from the same camera as frame 3, a share drawn per thousand"
  why_this_technique: "a share of exams reads as the few people at lit screens among a field of dark ones, from frame 3's camera, so 3 and 6 are one place before and after, and the accent keeps its one meaning, a person reading"
  palette: "straw grass, charcoal shells, putty tops, lit screens, bluebonnet shirts, buff brick"
  value_structure: >
    Lightest is the sky and the lit screens. Darkest is the seat shells in the near rows. Frame median L* planned at 62.

type:
  hook: "About 1.7% of exams improved."
  dek: "Officials reviewed more than 1.6 million exams. Content experts reread the answers typed as a number, word or phrase. About 17 of every 1,000 improved."
  labels: []

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 53 and 71"
  - "the render report counts per1000_improved lit screens among one thousand desks"
  - "the camera matches frame 3's"
  - "the desks read as rows running to the school at 432px"
  - "every lit screen has an expert seated at it, and all seventeen stand inside the frame"

risks:
  - "seventeen screens are small at feed size, so they are lit well above the sky and kept to the middle rows"
```

```yaml
slide: 7
layout: FULL_BLEED
primary_image:
  subject: "frame 1's field and camera, filled to the oak line with 27,200 desks in exact rows, one content expert in bluebonnet leaning over one desk in the near rows"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#4E5FA8"
job: >
  The turn. The fall's correction was people, and it reached 27,200 students, one desk each on the
  same field frame 1 left empty.

claims: [c20, c19, c21, c23, c22]
numerals:
  - value_from: c19

data_in_art:
  figure: students_credited
  drives: mark count, one instanced desk per student credited

depth:
  eye: 1.1
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, TEXTURE_GRADIENT, OCCLUSION]
  subject_at: {X: 0, Z: -3}

composition:
  structure: >
    Frame 1's camera craned up to 7.2 m from the same seat, so the change is the field and the height, the rows running from frame 1's desk
    into the haze.
  bands: >
    Top third, sky and type. Middle third, the far rows and haze. Bottom third, frame 1's own desk at full detail with its lit laptop, the next rows of desks behind it, their seat shells and contacts, and the straw grass between the rows.
  focal: "the field itself, 27,200 desks running from the camera's feet to the school, with one content expert in bluebonnet reading at a desk in the near rows as its scale"

art:
  technique: "instanced render at true scale, the same camera as frame 1"
  why_this_technique: "the same place empty and full is the clearest before and after a render can make"
  palette: "straw, charcoal, putty, one bluebonnet shirt"
  value_structure: >
    Lightest is the sky and the haze. Darkest is the near shells. Frame median L* planned at 61.

type:
  hook: "The agency says the engine scored none of the regraded answers."
  dek: "About 27,200 students got more credit on the reading test after content experts reread short typed answers, like \"ferst\" for \"first.\" That says nothing about how often the engine's own scores would change."
  labels: []

verbatim:
  - c23: "ferst"
  - c23: "first"

acceptance:
  - "the frame's median L* at 432px is between 51 and 69"
  - 'the hook reads "The agency says the engine scored none of the regraded answers."'
  - "the render report's instance count for the field equals figures.json students_credited"
  - "the camera matches frame 1's within a metre"
  - "the rows read as rows into haze at 432px"
  - "one person reading at a desk reads as a person"

risks:
  - "27,200 instanced desks under SwiftShader cost time, so the far field is one low detail instanced mesh per material"
```

```yaml
slide: 8
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "the school's covered walkway to the front entrance, a parent walking it toward the doors, the flagpole beside the entrance"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: none
job: >
  Show the door a family can use, the district's testing staff, who can ask for a person to read it.

claims: [c12, c10]
numerals: []

depth:
  eye: 1.6
  horizon: 640
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: -9}

composition:
  structure: >
    Standing eye down the covered walkway so its columns converge on the entrance and the parent
    walks into the frame's depth.
  bands: >
    Top third, sky and type. Middle third, the walkway roof and the school's entrance. Bottom third, the lit foreground, the broom finished walk running into the frame, the galvanized columns' footings with their contacts, and the parent walking under the roof, legs and shoes modelled by the soft key.
  focal: "the parent under the walkway roof"

art:
  technique: "render with a kit person at true scale under a built walkway"
  why_this_technique: "the claim is a route a person takes, and a walkway is a route"
  palette: "galvanized steel, broom concrete, buff brick"
  value_structure: >
    Lightest is the sky. Darkest is the walkway's underside. Frame median L* planned at 61.

type:
  hook: "Start with the district."
  dek: "A rescore can start with a parent or guardian's concern about a score. Rescores are read by people."
  labels: []

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 52 and 70"
  - 'the hook reads "Start with the district."'
  - "the walkway's columns read as columns converging on the entrance"
  - "the parent reads as a person with a contact"
  - "the flags read on the flagpole"

risks:
  - "the underside of the roof is a mid dark band, so type sits in the sky above the roof"
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: "frame 1's desk and camera, the parent in her own shirt standing at its side and leaning over it to read the laptop's screen"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: none
job: >
  Close on the one thing a parent can do, ask for a person to read it, on the desk the deck opened on.

claims: [c9, c11, c35]
numerals: []

depth:
  eye: 1.1
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, CAST_SHADOW]
  subject_at: {X: 0, Z: -3}

composition:
  structure: >
    Frame 1's exact camera with one state changed, a person at the desk.
  bands: >
    Top third, sky and type. Middle third, the parent's head and the school on the horizon. Bottom third, the desk at full detail with its lit laptop and seat shell, the parent's trousers and shoes behind it with their contacts on the straw grass.
  focal: "the parent reading the screen"

art:
  technique: "physically based render, the same camera as frame 1"
  why_this_technique: "the close is the cover with a person in it, which is the whole argument"
  palette: "straw, charcoal, putty, the parent's white shirt"
  value_structure: >
    Lightest is the sky and the screen. Darkest is the shell and the parent's trousers. Frame median L* planned at 67.

type:
  hook: "Ask the district for a rescore."
  dek: "District testing staff request it for a fee, inside a window set in the agency's Calendar of Events. If the score changes, the fee is waived."
  labels: []

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 58 and 76"
  - 'the hook reads "Ask the district for a rescore."'
  - "the parent reads as a person standing on the ground at the desk's side, head down to the screen"
  - "the camera matches frame 1's within a metre"
  - "the parent's head sits below the dek"

risks:
  - "a kit person can read as a mannequin, so the key is on the camera's side"
```
