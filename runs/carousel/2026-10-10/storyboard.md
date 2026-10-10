# Storyboard, 2026-10-10
# "An Austin college is writing AI policy"

## The story, and what the fact check did to it

Austin Community College says it is developing an AI policy in alignment with its newly launched TRUST
framework (c1), which it calls its first-ever AI policy (c3). Two collegewide AI committees developed the
framework (c4). Its five rules are one sentence each: tell where AI was used (c5), review outputs (c6), use
your own judgment (c7), safeguard integrity (c8) and treat IP with respect (c9). The college posted this on
October 9th (c31) and set three October events: a Faculty and Student AI Town Hall on Monday, October 12th,
6:30 to 9 p.m. at the Rio Grande Campus (c10), which will explore in-progress AI policies (c11); a faculty
convocation titled The Two AIs (c12) on October 16th at Eastview (c13); and a community seminar on E. M.
Forster's The Machine Stops (c15) on October 22nd at Highland (c14). Faculty, staff, students and community
members are invited (c16), and feedback goes through a form (c17). The college says more than 79,000
students rely on it each year (c20). The record carries the decision as tx-2026-0212.

**WHAT THE FACT CHECK CHANGED.**
- **"First-ever" is the college's word, never ours.** Its AI resource site already links a faculty and staff
  document titled Acceptable Use of Artificial Intelligence Policy (c19). The deck shows that document.
- **The post names no adoption date, no vote and no adopting body (c18).** Nothing on any frame says the town
  hall decides anything.
- **No campus count, no form deadline, no syllabus rule** survived. No map is drawn, because no campus
  position is in the claims.
- **The Dallas College course was dropped** (its page is off limits in robots.txt). The other classroom
  context (c21 to c30) is not used on a frame.

## Why this treatment, and what was grafted

Three directors pitched THE OBJECT (one student desk walked along a paver calendar), THE PLACE (a campus
lawn, a door and a room at the town hall's hour) and THE EVIDENCE (a blank sheet that is never written on,
and every published count drawn at true scale). All three chose the kit's `student_desk` with its laptop
as the hero on their own, which is the strongest signal the room gave.

- From THE OBJECT, the spine: the paver walk, one paver per day from the post (October 9th) to the seminar
  (October 22nd), with the three event days inlaid in Capitol granite, the desk's position on it as the
  progress mark, the five leader diagram, the hands at the keyboard, the shut lid on the seminar's paver
  where the walk ends, and the walker on the close.
- From THE PLACE, the light: the sun over Travis County at the town hall's start, computed in `compute.py`
  from the committed gazetteer (elevation 6.4, bearing 257.7, engine azimuth -77.7). The town hall room
  seen from the back with figures turned away, and a wall clock set to the start.
- From THE EVIDENCE, the blank sheet on the desk top beside the laptop, never written on, standing for a
  policy that has no published text yet, and the existing Acceptable Use document set beside it.
- Refused: the 79,000 desk block from a roof (render budget, and it reads as an event rather than a year),
  the school wing and a skyline (a K-12 building reads as the wrong institution, and no real ACC building is
  drawn), the survey ruler accent (the site's link colour, and cool beside the laptop screens), a map (no
  campus positions in the claims), and the context frame (the spine is ACC).

## The world, and the laws that hold it

**A CAMPUS LAWN AND A LIMESTONE WALK IN TRAVIS COUNTY AT LAST LIGHT.** The chassis is
`assets/js/deck/2026-10-10-lastlawn.js` and every frame loads it. It declares `sky: lastLight` with the light
at azimuth -77.7 and elevation 6.4, the sun's own position at 6:30 p.m. on October 12th, low in the west
south west. +x is east and +z is south. The key rakes every desk from the west and every shadow runs east.

1. **Start dark.** A near black sky with one warm seam low in the west, the desk in a pool of light, the
   lawn and the oaks behind it gone to the dark.
2. **Type is light, on the dark field**, and every wash only darkens.
3. **The laptop's lid is the deck's one practical.** It is dim and cool so it never lifts a frame into the
   mid tones.
4. Every standing thing gets `TXT.contact`, every frame `TXT.weather`.
5. **No real ACC building, room or screen is drawn.** The desk, the walk and the room are drawn to illustrate
   and the deks say so.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#0B0A10` | the DOM body behind the render |
| `accent` | `#9A3B2A` | Capitol granite, the event days: the October 12th inlay ahead on 1, all three inlays on 6, the October 22nd inlay on 7, the October 12th inlay under the desk on 9. Absent on 2, 3, 4, 5 and 8 |
| `hook` | `#EEEAE0` | light type on the dark sky |
| `dek` | `#DCD6C8` | the dek |
| `screen` | `#D8E2EA` | the laptop lid's dim cool light |

The world's materials: the desk's putty laminate and charcoal seat on a near black bent tube, Austin
limestone pavers, polished sunset red granite in three of them, a St. Augustine lawn going black past the
pool, live oaks as dark masses, one warm seam. The sheet is limestone white. Nothing else is bright.

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE

1. **Motif evolution.** The one desk and its two things, the lit lid and the blank sheet: alone on the first
   paver (1), labelled with the five rules (2), first of 79 (3), its screen showing the document that already
   exists beside the blank sheet (4), a person's hands at its keys (5), standing on the town hall's paver
   (6), lid shut on the last paver where the walk ends (7), in the room (8), and on the town hall's paver
   again with somebody walking up to it (9). The sheet stays blank on every frame.
2. **Camera move.** Low three quarter on the cover (1), pure profile (2), raised long lens over the rows (3),
   square to the screen (4), over the shoulder (5), low along the walk (6), close at the shut lid (7), from
   the back of the room (8), and standing behind the walker (9).

## The rotation

    FULL_BLEED  DIAGRAM  GRID  DOCUMENT  CLOSE_CROP  FULL_BLEED  CLOSE_CROP  FIGURE_SCALE  FIGURE_SCALE

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | MEDIUM, eye 0.8 m, 2.3 m off the desk's front left quarter, horizon on the upper third | the student desk, putty laminate with a dark T-mould edge and pencil groove, a charcoal moulded seat, one near black bent tube per side raked from the west, rubber glides with contacts on the first limestone paver, the lit lid and a blank limestone white sheet on the top |
| 02 | MEDIUM, eye 0.75 m, pure side profile, long lens | the desk in elevation, lit along its top by the raking west key, the bent tube's whole run from back post to floor runner catching the west key along its top, the seat shell's raked back, the wire book rack under the seat, contact shadows under its runners, five leaders to its parts |
| 03 | WIDE, eye 2.4 m, long lens fov 26 behind 79 desks | the hero desk at full detail in the near left corner, its tube and laminate lit, then 78 instanced desks in rows with their lids lit low receding into the dark lawn, staged as one subject |
| 04 | CLOSE, eye 1.0 m, square to the lid at 0.6 m | the laptop lid and its lit page, aluminium with a thin bezel, the drawn page of the existing document's title, the blank sheet's edge and the putty top in the foreground, the dark lawn and the seam beyond the lid |
| 05 | CLOSE, eye 1.2 m over the right shoulder | a seated person cropped at the shoulder, cotton sleeve and hands on the keyboard lit from the camera's side and by the lid, the blank sheet under the left hand, the desk's T-mould edge running off the bottom |
| 06 | WIDE, eye 0.5 m, low along the walk | fourteen limestone pavers, lit in the pool and weathered dark at the joints, sawn faces with chamfered arrises and joints of dark soil, three inlaid with polished granite, the desk large on the October 12th paver at the right third, lawn either side going to black |
| 07 | CLOSE, eye 0.95 m, front right of the desk on the last paver | the desk top with the lid shut and a paperback on it, matte laminate lit by the low key with a contact shadow under the book, the paperback's soft cover and page block, the granite inlay at the bottom edge, the walk stopping and the lawn falling to the dark past it |
| 08 | WIDE, eye 1.15 m, behind the desk at the back of a room | the hero desk in the near corner, its putty top lit by its lid and its tube in shadow with a contact on the floor, then the room, concrete floor with tooth, the back wall in shadow, one window of last light on the left, rows of public seating with figures turned away, a lectern in the window's pool, a wall clock at the start time |
| 09 | MEDIUM, eye 1.6 m, behind and left of a walker | the desk on the October 12th paver with the lid lit and the seat empty, a person walking up the walk toward it lit from the camera's side, the oak trunk dark behind |

Showstopper frame: 03, seventy nine desks in rows on a black lawn with every lid lit low, the near desk sharp and raked by the west light with its contact and cast shadow, the rows receding through the haze into the dark under one warm seam on the horizon
Tonal arc: near black on the lawn through 1 to 3, lifting on 4 where the lit page is the frame's largest light, darker again on 5 to 7 where the lid shuts, held in the dark room on 8 with one window, closing on 9 with the lit lid and the granite on the dark walk

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "the student desk whole on the first limestone paver of a walk across a dark campus lawn, its laptop lid lit and a blank sheet beside it, the October 12th granite inlay three pavers ahead"
  rect: [40, 590, 1000, 760]
  bleeds: [bottom]
accent: "#9A3B2A"
job: >
  Put the one desk the rules are written for in front of the reader, and say whose plan this is and that
  the college calls it its first-ever.

claims: [c1, c3, c31]
numerals: []

data_in_art:
  figure: paver_town_hall
  drives: the position of the granite inlaid paver ahead of the desk, index 3 counted from the post's day

depth:
  eye: 0.8
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera sits low off the desk's front left quarter so the lid and the sheet rise against the dark lawn
    and the seat's back runs toward the right edge. The walk runs from the desk away to the upper left, and
    its third paver ahead carries the granite inlay, small and warm in the pool's edge, the tease of the
    town hall.
  bands: >
    Top third, the near black sky over a dark oak mass far off, with the hook and dek. Middle third, the lid,
    the sheet and the desk top, the walk running back. Bottom third, the bent tube lit along its top, the glides and the
    first paver with its contact shadow, the paver's texture in the pool, the lawn going black toward the camera.
  focal: "the lit lid and the blank sheet on the desk top, the lightest area in the frame"

art:
  technique: "physically based render of the kit student desk staged on a limestone walk in a lastLight world"
  why_this_technique: "a desk is a thing every reader has sat in, and it reads as that one object only modelled, lit and standing on the ground"
  palette: "putty laminate, charcoal seat, near black tube, limestone pavers, a granite inlay, a black lawn and sky"
  value_structure: >
    Lightest is the lit lid and the sheet. Darkest is the sky and the near lawn. Frame median L* planned at 13.

type:
  hook: "An Austin college is writing AI policy"
  dek: "Austin Community College says it is developing what it calls its \"first-ever\" AI policy. A framework called TRUST is meant to help shape it. The post is dated October 9th. The desk and the walk are drawn to illustrate."
  labels: []

verbatim:
  - c3: "first-ever"

acceptance:
  - "the desk's top, seat, bent tube and glides are modelled and lit, and the desk owns at least 30 percent of the frame"
  - "the laptop lid is lit and a blank sheet lies beside it, and rendering no sheet fails this item"
  - "a granite inlaid paver is visible ahead of the desk on the walk, and it is the only red area in the frame"
  - "every glide stands on the paver with a dark contact under it"
  - "no part of the desk or the oak crosses a glyph of the hook or the dek"
  - "the sky above the horizon is near black"

risks:
  - "an oak crown behind the hook lit plum is a busy mid tone under type, so the oak stands past the stage fog as a silhouette"
  - "a desk alone on a lawn reads as abandoned, so it stands on the walk in the pool like a stage"
```

```yaml
slide: 2
layout: DIAGRAM
primary_image:
  subject: "the student desk in pure side profile on the lawn, five leaders to five of its parts, each labelled with one TRUST rule's own name"
  rect: [140, 520, 800, 760]
  bleeds: []
accent: none
job: >
  Name the five rules in the college's own words and tie each to the place on the desk where a student's
  work passes.

claims: [c4, c5, c6, c7, c8, c9]
numerals: []

data_in_art:
  figure: rules
  drives: the number of leaders and labels on the desk, 5, one per rule

depth:
  eye: 0.75
  horizon: 560
  cues: [CAST_SHADOW, AERIAL, OCCLUSION, RELATIVE_SIZE]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A near orthographic profile so the desk reads as an elevation drawing of a real object, its writing
    surface on the left and its seat on the right. The five labels stand in the dark sky and the dark lawn
    around it, each with a leader ending short of its glyphs at the part it names.
  bands: >
    Top third, the sky with the hook, the dek and two labels. Middle third, the desk top with the lid and the
    sheet, the seat's back, two labels. Bottom third, the tube and the wire book rack lit along their tops, their contact shadow on the
    lawn, one label.
  focal: "the lit lid and the sheet on the writing surface, the lightest area"

art:
  technique: "physically based render in profile with DOM leaders, a labelled elevation"
  why_this_technique: "the rules are for the person at the desk, and an elevation lets five short labels sit at five real parts without crossing"
  palette: "the desk's own materials, the black lawn and sky"
  value_structure: >
    Lightest is the lid and the sheet, darkest the sky. Frame median L* planned at 11.

type:
  hook: "Five rules, one for each letter of TRUST"
  dek: "The college says two collegewide AI committees developed the framework. Each rule is one sentence in its post. Matching each rule to a part of the desk is an illustration."
  labels: ["TELL WHERE AI WAS USED", "REVIEW OUTPUTS", "USE YOUR OWN JUDGMENT", "SAFEGUARD INTEGRITY", "TREAT IP WITH RESPECT"]

verbatim:
  - c5: "TELL WHERE AI WAS USED"
  - c6: "REVIEW OUTPUTS"
  - c7: "USE YOUR OWN JUDGMENT"
  - c8: "SAFEGUARD INTEGRITY"
  - c9: "TREAT IP WITH RESPECT"

acceptance:
  - "exactly five rule labels are set, and fewer than five fails this item"
  - "every leader ends short of its label's glyphs and touches a modelled part of the desk"
  - "the desk is seen in profile, its tube's whole run visible from back post to floor runner"
  - "the desk owns at least 30 percent of the frame"
  - "the label text matches the post's rule names word for word"

risks:
  - "the mapping of rules onto parts is the deck's drawing, so the dek says so"
  - "a profile reads flat, so the key rakes the tube's top and the contact darkens the lawn under the runners"
```

```yaml
slide: 3
layout: GRID
primary_image:
  subject: "79 student desks in rows on a dark lawn, every laptop lid lit low, the full detail hero desk sharp in the near corner with its lid the brightest"
  rect: [0, 600, 1080, 750]
  bleeds: [left, right, bottom]
accent: none
job: >
  Show the scale of who these rules govern, one desk for every thousand of the more than 79,000 students the
  college says rely on it each year.

claims: [c20]
numerals:
  - computed_by: "compute.py desks_drawn, students floored to thousands"
  - value_from: c20

data_in_art:
  figure: desks_drawn
  drives: the count of desks rendered, 79, asserted in the frame's code

depth:
  eye: 2.4
  horizon: 470
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, TEXTURE_GRADIENT, AERIAL, CAST_SHADOW]
  subject_at: {X: 0, Z: -8}

composition:
  structure: >
    A raised long lens from behind the rows so every lid faces the camera, the rows running away into the
    dark under the seam. The hero desk stands in front of the block at full detail with the brightest lid, the
    rest instanced with their lids lit low, the whole count staged as one subject.
  bands: >
    Top third, the sky and the seam with the hook and dek. Middle third, the far rows as low lit lids and putty
    tops going to dark. Bottom third, the near rows and the hero desk, lit and modelled.
  focal: "the hero desk sharp in front of the block with its lid lit, the lightest area"

art:
  technique: "physically based render of an isotype count, instanced kit desks staged as one subject"
  why_this_technique: "a count a reader can believe is a count of real things at one scale, and desks are the thing the students sit at"
  palette: "low lit lids, putty tops, black lawn, one warm seam"
  value_structure: >
    Lightest is the hero's lid, darkest the sky and the lawn between rows. Frame median L* planned at 14.

type:
  hook: "79 desks, one for every thousand students"
  dek: "The college says more than 79,000 students rely on it for their education each year. Each desk here stands for a thousand of them."
  labels: ["ONE DESK = 1,000 STUDENTS A YEAR"]

verbatim: []

acceptance:
  - "exactly 79 desks are rendered and the frame's code refuses to render another number"
  - "the near hero desk is modelled at full detail and the rows read as separate desks at 432px"
  - "the lids are lit low, the hero lid brightest, and the far rows fall into the dark without a grey wash"
  - "the horizon and the seam are in frame and the sky above is near black"
  - "the label names the set it counts, students a year"
  - "the near hero desk stands at least 300 px tall in the full frame"

risks:
  - "78 lit lids alias into a striped field at feed size, so the block lids glow low and only the hero lid is bright"
  - "rows of desks can read as an empty exam hall, so the hook names the count of students first"
```

```yaml
slide: 4
layout: DOCUMENT
primary_image:
  subject: "the hero desk's laptop square to the camera, its lit page carrying the title of the document the college's AI site already links"
  rect: [140, 560, 760, 620]
  bleeds: []
accent: none
job: >
  Turn the deck: the college calls the coming policy its first-ever, and its own AI site already links a
  faculty and staff document titled Acceptable Use of Artificial Intelligence Policy.

claims: [c19, c3]
numerals: []

data_in_art:
  figure: existing_documents
  drives: the count of titled documents drawn on the page, 1

depth:
  eye: 1.0
  horizon: 600
  cues: [OCCLUSION, CAST_SHADOW, AERIAL, RELATIVE_SIZE]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera stands square to the lid at seated height so the page is axis aligned and its title sits on it
    as DOM type. The blank sheet is off this frame, so the titled page is the one document in it. The dark lawn and the seam
    show over the lid's top.
  bands: >
    Top third, the sky and seam with the hook and dek. Middle third, the lit page with the document title.
    Bottom third, the keyboard lit by the page and the putty top's
    grain running off the edge with the lid's shadow across it.
  focal: "the lit page with the title, the lightest area"

art:
  technique: "physically based render with a drawn page on the lid and DOM type registered to the lid's rect"
  why_this_technique: "the existing document is a title on a page, and showing it on the same desk that carries the blank sheet on every other frame sets the two side by side without a word of argument"
  palette: "the lid's cool page, aluminium, putty, the black field"
  value_structure: >
    Lightest is the page, darkest the sky. Frame median L* planned at 20.

type:
  hook: "Its AI hub already links a use policy"
  dek: "The college's AI Resource Hub links a faculty and staff document titled Acceptable Use of Artificial Intelligence Policy. The post calls the coming policy the college's \"first-ever.\" The page is drawn to illustrate."
  labels: ["ACCEPTABLE USE OF ARTIFICIAL INTELLIGENCE POLICY"]

verbatim:
  - c19: "ACCEPTABLE USE OF ARTIFICIAL INTELLIGENCE POLICY"
  - c3: "first-ever"

acceptance:
  - "the document's title sits on the lit page, inside the lid's rect, and a title set off the page fails this item"
  - "no second document and no sheet sits beside the titled page"
  - "the lid is square to the camera and no type is rotated"
  - "the dark lawn and the seam show above the lid"
  - "the page is the lightest area and no part of the frame is a grey wash"
  - "the lid owns at least 30 percent of the frame width"

risks:
  - "a white page blows out, so it is a dim cool page near L* 70 and the rest stays black"
  - "a reader may take the existing document as proof a policy exists, so the dek says only that the site links a document with that title"
```

```yaml
slide: 5
layout: CLOSE_CROP
primary_image:
  subject: "the hero desk seen from the side with its lid lit and the blank sheet on its top, and the hands of a person seated at it, cropped by the right edge"
  rect: [40, 640, 1040, 520]
  bleeds: [right]
accent: none
job: >
  Put the person the rules are written for at the desk, under the rule that says AI should never replace
  their judgment.

claims: [c7, c5]
numerals: []

depth:
  eye: 1.2
  horizon: 430
  cues: [OCCLUSION, CAST_SHADOW, RELATIVE_SIZE, AERIAL]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    Over the right shoulder from behind, the shoulder and arm entering from the right edge, the hands at the
    keys in the lid's light, the sheet under the left hand. The lawn and the seam sit behind the lid in the
    upper left.
  bands: >
    Top third, the sky and the seam with the hook and dek. Middle third, the lid and the hands. Bottom third,
    the sleeve lit from the camera's side, the desk top's grain and the sheet in the hands' shadow, running off the bottom edge.
  focal: "the hands on the keys in the lid's light, the lightest skin and the lit keys"

art:
  technique: "physically based render, the kit person cropped at the shoulder, lit from the camera's side"
  why_this_technique: "the rule is about a person's own judgment, so a person's hands at the keys carry it, and a crop keeps the kit figure out of mannequin range"
  palette: "skin and cotton lit by the lid, putty, charcoal, the black field"
  value_structure: >
    Lightest is the hands and the lid, darkest the sky. Frame median L* planned at 12.

type:
  hook: "The judgment stays with the person"
  dek: "\"AI can support your work, but it should never replace your expertise, decision-making, or responsibility,\" the third rule reads. The first asks people to say when AI plays a meaningful role."
  labels: []

verbatim:
  - c7: "AI can support your work, but it should never replace your expertise, decision-making, or responsibility"

acceptance:
  - "a seated person's hands are in the lid's light at the desk, and a frame with no hands fails this item"
  - "no face is in frame and the figure is cropped by the right frame edge"
  - "the hands are lit from the camera's side and read as hands at 432px"
  - "the horizon and the seam are visible behind the lid"
  - "the quote in the dek matches the post word for word"
  - "the seated person's sleeve and hands stand at least 400 px wide in the full frame"

risks:
  - "kit hands at a crop may read as mittens, so the lid's light grazes the knuckles and the crop holds the sleeve large"
```

```yaml
slide: 6
layout: FULL_BLEED
primary_image:
  subject: "a walk of fourteen limestone pavers across the dark lawn, one per day from the post to the seminar, three inlaid with granite, the desk standing on the October 12th paver"
  rect: [0, 650, 1080, 700]
  bleeds: [left, right, bottom]
accent: "#9A3B2A"
job: >
  Lay out the three dates the college set as a measured calendar, one paver per day from its post to its
  seminar.

claims: [c10, c12, c13, c14, c31]
numerals:
  - computed_by: "compute.py walk_pavers, days from the post to the seminar, both ends counted"

data_in_art:
  figure: walk_pavers
  drives: the count of pavers laid, 14, and the inlays at indices 3, 7 and 13

depth:
  eye: 0.5
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, TEXTURE_GRADIENT, RELATIVE_SIZE, CAST_SHADOW, AERIAL]
  subject_at: {X: 0, Z: -3}

composition:
  structure: >
    A low camera beside the first paver, the walk running diagonally away to the upper right, the pavers
    packing tighter with distance. The desk stands large at the right third on the October 12th paver. Three
    small labels name the inlaid days.
  bands: >
    Top third, the sky and the seam with the hook and dek. Middle third, the far walk and the later inlays, the
    desk's lid. Bottom third, the near pavers lit in the pool with their stone texture and dark joints, the first inlay, the desk's glides and contact shadows.
  focal: "the desk's lit lid over the October 12th inlay, the lightest area"

art:
  technique: "physically based render of a measured walk, pavers as a calendar at one pitch"
  why_this_technique: "a calendar a reader walks along makes three dates into distances, and the desk standing on one of them says which comes first"
  palette: "limestone pavers, polished granite, putty and charcoal, a black lawn"
  value_structure: >
    Lightest is the lit lid and the near pavers in the pool, darkest the sky and the far lawn. Frame median L*
    planned at 13.

type:
  hook: "Three dates on fourteen pavers"
  dek: "One paver for each day from the October 9th post to the October 22nd seminar at Highland, both ends counted. The town hall is October 12th at Rio Grande. A faculty convocation titled The Two AIs is October 16th at Eastview."
  labels: ["OCTOBER 12TH TOWN HALL", "OCTOBER 16TH CONVOCATION", "OCTOBER 22ND SEMINAR"]

verbatim:
  - c12: "The Two AIs"

acceptance:
  - "exactly fourteen pavers are laid and three carry granite inlays, and the frame's code refuses another count"
  - "the desk stands on the October 12th paver with contacts under its glides"
  - "the three labels sit beside their inlays and none crosses a paver edge or a glyph"
  - "the horizon and the seam are in frame"
  - "the inlays are the only red areas in the frame"
  - "the near limestone pavers stand at least 300 px wide in the full frame, and the desk at least 280 px tall"

risks:
  - "a quantity in perspective reads short at the far end, so the labels carry the dates and the dek states the rule"
```

```yaml
slide: 7
layout: CLOSE_CROP
primary_image:
  subject: "the desk on the walk's last paver, the laptop lid shut with a paperback on it, the granite inlay at the bottom edge, the walk stopping and the lawn falling to the dark past it"
  rect: [0, 700, 1080, 650]
  bleeds: [left, right, bottom]
accent: "#9A3B2A"
job: >
  Show where the post's dates end and what it does not name, at the seminar on The Machine Stops.

claims: [c14, c15, c18]
numerals: []

data_in_art:
  figure: paver_seminar
  drives: the desk's position on the walk, paver index 13, and the count of pavers ending there

depth:
  eye: 0.95
  horizon: 500
  cues: [OCCLUSION, CAST_SHADOW, AERIAL, RELATIVE_SIZE]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A close three quarter from the front right, the desk top cropped by the right and bottom edges, the shut
    lid and the paperback the largest things, the inlay at the bottom edge. Past the desk the walk stops and
    the lawn runs to the dark.
  bands: >
    Top third, the sky with the hook and dek. Middle third, the shut lid, the paperback, the sheet, the end of
    the walk beyond. Bottom third, the desk top's edge lit by the low key, its shadow on the paver, and the granite
    inlay's polished texture.
  focal: "the paperback's lit cover on the shut lid"

art:
  technique: "physically based render at detail scale, the one unlit lid in the deck"
  why_this_technique: "the absence is what the post leaves unnamed, and a walk that simply stops says that without drawing a thing that is not there"
  palette: "a soft cover, aluminium, limestone, granite, the black lawn"
  value_structure: >
    Lightest is the paperback and the sheet, darkest the sky and the lawn past the walk. Frame median L*
    planned at 10.

type:
  hook: "The walk ends where the post does"
  dek: "The post names no adoption date, no vote and no adopting body. Its last date is the October 22nd seminar. It is a guided discussion of E. M. Forster's story The Machine Stops."
  labels: []

verbatim:
  - c15: "The Machine Stops"

acceptance:
  - "the lid is shut and a paperback lies on it, and an open lid fails this item"
  - "no paver is laid past the one the desk stands on"
  - "the granite inlay shows at the bottom edge and is the only red area"
  - "the horizon is in frame and the sky is near black"
  - "nothing on the frame says or shows a vote or an adoption"
  - "the desk top stands at least 300 px wide in the full frame"

risks:
  - "a shut lid beside a story titled The Machine Stops can read as a verdict, so the dek says it is a discussion of a story"
```

```yaml
slide: 8
layout: FIGURE_SCALE
primary_image:
  subject: "a town hall room seen from behind the hero desk, rows of seating with people turned away, a lectern in the window's pool, a wall clock at the start time"
  rect: [0, 520, 1080, 830]
  bleeds: [left, right, bottom]
accent: none
job: >
  Show the room the college has asked people into, at the hour it starts, and who it invited.

claims: [c10, c11]
numerals: []

data_in_art:
  figure: clock_minute_deg
  drives: the rotation angle of the clock's hands, minute at 180 degrees and hour at 195, the town hall's start

depth:
  eye: 1.15
  horizon: 560
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, OCCLUSION, CAST_SHADOW]
  subject_at: {X: 0, Z: -5}

composition:
  structure: >
    The camera stands behind the hero desk at the back of a room dark around one window of last light. The
    desk takes the near left corner with its lid lit. The seating runs toward a lectern in the window's pool,
    the clock on the back wall above.
  bands: >
    Top third, the dark ceiling and wall with the hook and dek and the clock. Middle third, the lectern in the
    window light, the backs of the seated figures. Bottom third, the hero desk with its lid lit, the near seat frames in shadow, the concrete floor's
    texture catching the window light.
  focal: "the lectern in the window's pool of last light"

art:
  technique: "physically based render inside TXT.interior, figures at true scale turned away"
  why_this_technique: "an invitation is a room with seats and a time, and the figures at true scale give the room its size"
  palette: "concrete, dark walls, a warm window, black seat frames, the lit lid"
  value_structure: >
    Lightest is the window and the lectern, darkest the ceiling and the back corners. Frame median L* planned
    at 12.

type:
  hook: "October 12th, 6:30 p.m., the town hall"
  dek: "The college says its Faculty and Student AI Town Hall will explore in-progress AI policies. It runs until 9 p.m. at the Rio Grande Campus. The room is drawn to illustrate."
  labels: []

verbatim:
  - c11: "explore in-progress AI policies"

acceptance:
  - "the clock's hands read 6:30, and a clock reading another time fails this item"
  - "at least six seated figures are turned away from the camera and none shows a face"
  - "the window is the room's one light source and the back wall is in shadow"
  - "the hero desk takes the near corner with its lid lit"
  - "the room is dark around the window, with no grey wash"
  - "the hero desk stands at least 400 px tall in the near corner"

risks:
  - "a hearing room was drawn on October 4th, so there is no dais and the seating is loose rows"
  - "the window's daytime exterior can put a pale slab in the room, so its outside is forced dark"
```

```yaml
slide: 9
layout: FIGURE_SCALE
primary_image:
  subject: "the desk on the October 12th granite paver with its lid lit and its seat empty, a person walking up the walk toward it"
  rect: [320, 560, 700, 790]
  bleeds: [bottom]
accent: "#9A3B2A"
job: >
  Close on the next step a reader can take, the seat open at the town hall on October 12th and the seminar
  open to community members on October 22nd.

claims: [c16, c17]
numerals: []

data_in_art:
  figure: paver_town_hall
  drives: the desk's position on the walk, paver index 3, the town hall's day counted from the post

depth:
  eye: 1.6
  horizon: 500
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: -2}

composition:
  structure: >
    A standing camera behind and left of a walker on the walk, the desk ahead on the granite paver at the
    right third, the walker at true scale beside it giving the desk its size. The oak trunk is dark behind.
  bands: >
    Top third, the sky and the seam with the hook and dek. Middle third, the walker's shoulders and the lit
    lid. Bottom third, the walk lit in the pool with its stone texture, the granite inlay, the walker's and
    the desk's contact shadows.
  focal: "the lit lid over the granite inlay, the lightest area"

art:
  technique: "physically based render at figure scale, the kit person walking, lit from the camera's side"
  why_this_technique: "the next step is a person going to the seat, and a walker beside the desk makes the invitation a picture"
  palette: "limestone and granite, putty and charcoal, a lit lid, the black lawn"
  value_structure: >
    Lightest is the lid and the paver in the pool, darkest the sky. Frame median L* planned at 13.

type:
  hook: "Community members are invited too"
  dek: "The college invites faculty, staff, students and community members to take part in one or more of the events. Feedback and questions go through a form on its page about getting involved with generative AI."
  labels: []

verbatim: []

acceptance:
  - "the desk stands on a granite inlaid paver with its lid lit and its seat empty"
  - "a walking person at true scale is turned three quarters away and lit from the camera's side"
  - "the walk runs from the camera to the desk with contacts under the walker's feet and the desk's glides"
  - "the horizon and the seam are in frame and the sky is near black"
  - "the dek names who is invited and where feedback goes"
  - "the desk stands at least 220 px tall and the walker at least 300 px"

risks:
  - "the kit person reads as a mannequin, so the figure is turned away and under a fifth of the frame"
```
