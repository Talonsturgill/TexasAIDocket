# Storyboard — the editorial deck, a reference build of the illustration system (2026-09-11)

## What this is, and what it is not

This deck re-draws carousel no. 21's verified story (docket item `tx-2026-0142`, claims file at
`runs/carousel/2026-09-11/claims.json`) with the illustration system that shipped the same day:
`txscene.js`, `txfig.js`, `txobjects.js`, `txink.js` and `txlayout.js`. Every claim id below is
that run's, every quoted string is verbatim from that claims file, and no numeral in the copy is
new. It is a REFERENCE for the directors, the pixel critics and the flow critic, and the bar a
routine run is now held to. It is not a shipped run. It carries no email, no caption, no ledger
entry, and nothing under `runs/`.

**Read `knowledge/carousel/ILLUSTRATION_SYSTEM.md` before this file.** Every dossier below
declares the three keys `layout_check.py` measures: `layout` (one of the ten archetypes),
`primary_image` (the subject, the rect it owns in frame px, and the edges it bleeds) and
`accent` (the deck's one accent, `#E0956A`, dusk gold from `config/brand.yaml`).

## The register

Night paper (`#0F0C1C`) and one pale ink (`#EDE6D6`), printed. Every frame's scene is drawn in
greys into an offscreen twin at true scale, then `TXINK.print` lays the paper, screens the tone
into ink (halftone, line, hatch or stipple, chosen per frame and named below), lays the contour
plate a pixel out of register, and paints the one accent flat on top. One declared key light per
scene. Figures are 1.55 to 1.75 m. A school bus is 12 m. The Capitol is 94 m to the star.

## The rotation

    1 FULL_BLEED   2 DOCUMENT   3 FIGURE_SCALE   4 OBJECT_AND_CAPTION   5 GRID
    6 DIAGRAM      7 CLOSE_CROP   8 SPLIT_HORIZON   9 FULL_BLEED

Eight distinct, no consecutive repeat, TYPE_AS_OBJECT unused, FULL_BLEED and CLOSE_CROP three
between them, eight frames bleeding at least one edge.

## THE NINE

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: a classroom at seated eye height, three rows of student desks with students, a whiteboard on the far wall, troffers overhead
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#E0956A"
job: >
  Stop the scroll with the room the rule lands in, drawn as a place with people in it rather
  than as a diagram of one, and set the deck's register on frame one: night paper, pale ink,
  halftone.
claims: [c11, c14]
numerals: []
composition:
  structure: >
    Camera at 1.15 m, a seated student's eye, horizon at 700. Three rows of four desks recede
    from Z 2.4 to 7.8 m. The back wall at 9.2 m carries the whiteboard and a clock. The ceiling
    is kept black above y 560 so the type reserve is dark by construction, and the troffers
    begin below it.
  bands: >
    TOP third, the reserve, kicker, hook and dek on black ceiling. MIDDLE third, the whiteboard,
    the far rows and the troffers. BOTTOM third, the near row cropped by the frame and the tile
    floor with its joints, fading to paper under the furniture band.
  focal: >
    The whiteboard, an AREA of about 520 by 160 px on the far wall, the lightest plate in the
    frame, with the accent marker stroke on it.
art:
  technique: "TXSCENE room with TXFIG seated figures and TXOBJ student desks, printed by TXINK as a halftone at cell 6, angle 22, with the contour plate at 1.0, -0.8 px."
  why_this_technique: >
    A halftone is the register of a printed school photograph, and cell 6 keeps the dots a
    visible mark at feed size while still resolving a figure's head at 432 px. The room is
    drawn at true scale so the desks, the students and the ceiling agree about how big a
    classroom is, which no screen-pixel drawing has managed in twenty one decks.
  palette: >
    night #0F0C1C paper, limestone #EDE6D6 ink, dusk gold #E0956A accent on the two marker
    strokes only. Greys in the twin: floor #4A4A4A, wall #2E2E2E, figures #E2E2E2, desks #7A7A7A.
  value_structure: >
    The ceiling is the darkest zone and carries the type. The whiteboard is the lightest. The
    floor is a mid field of dots. Frame median L* planned under 40.
  motion: >
    The eye lands on the hook, drops to the whiteboard, and is carried down the rows to the
    near desk at the bottom left.
type:
  hook: "Texas put AI in a money class."
  dek: "The board's own course text tells a student to research career pathways using artificial intelligence tools."
  labels: ["TEXAS STATE BOARD OF EDUCATION", "19 TAC SECTION 113.26", "01 / 09", "c11 c14   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim:
  - c14: "artificial intelligence tools"
acceptance:
  - at 432 px the three rows of desks and the students at them are countable as rows
  - the whiteboard reads as a lighter rectangle on the far wall with two accent strokes on it
  - the halftone dots are visible as dots in the floor at 432 px, not as a grey
  - no halftone dot sits within the hook's or the dek's glyph band, the ceiling above y 560 is solid paper
```

```yaml
slide: 2
layout: DOCUMENT
primary_image:
  subject: the attachment itself, a sheet on the desk with a second sheet behind it, the rule's own words set on it
  rect: [92, 540, 900, 810]
  bleeds: [bottom]
accent: "#E0956A"
job: >
  Put the reader's eye on the sentence that carries the whole story, on the document it
  lives in, so the deck's evidence is the thing drawn rather than a caption about it.
claims: [c14, c18, c19]
numerals: []
composition:
  structure: >
    A sheet at 860 by 980 px turned 1.6 degrees, a second sheet behind it offset up and right,
    a soft cast shadow, a fold line two thirds down. The rule's section heading, the knowledge
    statement and expectation (C) are set on the sheet in a document face. The sheet runs off
    the bottom of the frame.
  bands: >
    TOP third, the reserve with the hook and dek on night. MIDDLE third, the sheet's head, the
    heading and the expectation. BOTTOM third, the rest of the sheet, the fold, and the bleed.
  focal: >
    The phrase artificial intelligence tools, an AREA of about 300 by 44 px, under a hand laid
    accent marker stroke that sits BEHIND the type and never through it.
art:
  technique: "A drawn sheet (TXINK.wobble on its edge, flat paper fill) over a TXINK line screen at cell 5 that carries the desk and the sheet behind, with DOM type on the sheet in Instrument Serif."
  why_this_technique: >
    A document frame has to be a document. The type on the page is the image, so it is real
    DOM type in a document face, and the paper it sits on is flat so the type prints clean. The
    line screen at minus 24 degrees carries only the shadow and the sheet behind, which is
    what makes the front sheet read as lifted off the desk.
  palette: >
    night paper, limestone ink for the sheet, page ink #1B1830 for the document type, dusk gold
    for the one marker stroke.
  value_structure: >
    The sheet is the lightest thing and the largest. The night around it is the darkest. The
    second sheet is a mid tone in lines.
  motion: >
    Hook, then the sheet's heading, then down the expectation to the accent, then off the
    bottom of the frame with the sheet.
type:
  hook: "Chapter three hands it over."
  dek: "The verb is research. The student does it, and the course text names the tool."
  labels: ["KNOWLEDGE STATEMENT (3)", "CAREERS AND EARNING POTENTIAL", "02 / 09", "c14 c18 c19   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim:
  - c14: "research career pathways using labor-market data, online resources, and artificial intelligence tools to evaluate income growth, employment trends, global competition, comparative advantage, technological change, creative destruction, required skills, and possible employers"
acceptance:
  - the sheet's left and top edges are visibly not straight at 1080 px, and read as straight at 432 px
  - the accent stroke sits behind the words artificial intelligence tools and touches no letter
  - a second sheet is visible behind the first at the top right, in lines rather than flat
  - the sheet runs off the bottom edge of the frame
```

```yaml
slide: 3
layout: FIGURE_SCALE
primary_image:
  subject: a student with a bag on the Capitol's south walk, the Capitol centre section at 62 m leaving the top of the frame
  rect: [120, 0, 960, 1180]
  bleeds: [top, right]
accent: "#E0956A"
job: >
  Give the statute a size. A student at 1.66 m against 94 m of granite says who the rule is
  for and who made it, without a word of caption.
claims: [c8, c9]
numerals: []
composition:
  structure: >
    Camera at 1.6 m standing eye, horizon at 905, focal 720 px. The Capitol centre section at
    X 30, Z 62 so its dome leaves the top and its right wing leaves the right edge. The walk
    runs up the middle. The student at Z 5.2 on the left, two more people at 15 and 24 m so
    the scale reads three times.
  bands: >
    TOP third, the dome and the type in the sky it leaves empty on the left. MIDDLE third, the
    drum, the main block and the near walk. BOTTOM third, the student, the cast shadow and the
    walk's granite joints.
  focal: >
    The student, an AREA of about 110 by 230 px at the lower left, the one figure the reader
    stands beside.
art:
  technique: "TXOBJ capitol and live_oak, TXFIG walk pose with a bag, printed by TXINK as a stipple at cell 5, seven dots a cell, contour plate at -1.0, 0.8 px."
  why_this_technique: >
    Stipple is granite. It gives a stone building its grain and a night sky its stars in one
    pass, and its dots stay dots at 432 px where a fine halftone would go grey.
  palette: >
    night paper, limestone ink, dusk gold on the flag alone. Twin greys: walk #8A8A8A, lawn
    #3C3C3C, building #D6D6D6, oak #9A9A9A.
  value_structure: >
    The building is the light mass on the right. The sky on the left is the dark that holds
    the type. The walk is a mid field.
  motion: >
    Hook top left, across to the dome, down the drum to the portico, down the walk to the
    student and the shadow at the bottom left.
type:
  hook: "The board acts under statute."
  dek: "The statute the board cites makes it responsible for graduation requirements, and treats the half credit as one a student must comply with."
  labels: ["THE STATUTE BEHIND THE ITEM", "03 / 09", "c8 c9   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim: []
acceptance:
  - the dome leaves the top edge of the frame and the right wing leaves the right edge
  - the student at the bottom left is under one seventh of the building's visible height
  - the walk's joints converge on a point under the portico
  - the flag is the only pixel of accent on the frame
```

```yaml
slide: 4
layout: OBJECT_AND_CAPTION
primary_image:
  subject: a school bus at 6.6 m at dusk on a caliche lot, bleeding both sides, with its long shadow, a fence line, a pole and an oak
  rect: [0, 330, 1080, 1020]
  bleeds: [left, right, bottom]
accent: "#E0956A"
job: >
  The poster frame. One object every reader knows the size of, drawn at that size, close, so
  the implementation date has a vehicle.
claims: [c9, c12, c13]
numerals: ["2027"]
composition:
  structure: >
    Camera at 1.3 m, horizon at 700, focal 700 px, the light 16 degrees above the horizon
    from the left so the bus throws a shadow the length of the lot. The bus at Z 6.6 spans
    more than the frame's width. The type sits in the dusk sky above the roof line.
  bands: >
    TOP third, the type in the sky and the pole's crossarm at the right. MIDDLE third, the
    bus. BOTTOM third, the lot, the shadow, the driver and a student walking in.
  focal: >
    The bus, an AREA of about 1080 by 340 px, the frame's one object.
art:
  technique: "TXOBJ school_bus mirrored, utility_pole with transformer, live_oak, a TXOBJ fence and wire, TXFIG stand and walk, printed by TXINK as a halftone at cell 8, angle 30, contour plate at 1.4, -1.0 px. Accent plate: the lamps and the stop arm drawn from a second sprite at the same world position."
  why_this_technique: >
    A large object takes a coarse cell. At cell 8 the dots are the size of the bus's rub rail
    and the object reads as a print of a photograph rather than as a vector, which is the
    difference between drawn and placed.
  palette: >
    night paper, limestone ink, dusk gold on four lamps and the stop arm. Twin greys: lot
    #4A4A4A, sky to #5A5A5A at the horizon, bus #DCDCDC.
  value_structure: >
    The bus is the lightest mass. The sky above is dark and carries the type. The lot is a mid
    dot field with the black shadow across it.
  motion: >
    Hook, down to the bus's roof, along the windows to the hood, down the shadow to the bottom
    right.
type:
  hook: "Taught from the school year that opens in 2027."
  dek: "One half credit on completion, and a curriculum requirement rather than an elective by the statute the board cites."
  labels: ["IMPLEMENTATION", "04 / 09", "c9 c12 c13   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim: []
acceptance:
  - the bus leaves both the left and the right edge of the frame
  - the shadow on the lot is longer than the bus is tall and points away from the light on the left
  - four small accent plates sit on the bus, the lamps and the stop arm, and nothing else on the frame is accent
  - the halftone cell is visibly coarser than frame 1's at 432 px
```

```yaml
slide: 5
layout: GRID
primary_image:
  subject: ten identical units, a student seated at a desk, on two shelves of five, three printed in the accent
  rect: [80, 560, 920, 660]
  bleeds: []
accent: "#E0956A"
job: >
  The count. Ten knowledge statements, three of which name a machine, as ten things a reader
  can count without reading a number.
claims: [c12, c13, c19, c20, c21]
numerals: []
composition:
  structure: >
    Two shelves at y 820 and 1160, each with its own long lens (2400 px focal at 16 m) so every
    unit is exactly 150 px a metre. Five units a shelf at 1.28 m spacing. Units 3, 4 and 7 are
    the accent, and their labels read the verb rather than the number.
  bands: >
    TOP third, the reserve, hook and dek. MIDDLE third, the first shelf. BOTTOM third, the
    second shelf and the labels.
  focal: >
    Units 3 and 4 side by side on the first shelf, an AREA of about 330 by 200 px, the two
    accent units the eye lands on first.
art:
  technique: "TXFIG sit pose at seat 0.45 with TXOBJ student_desk, ten times, printed by TXINK as a vertical line screen at cell 4, contour plate at 0.9, -0.7 px. The three accent units are painted flat over their print."
  why_this_technique: >
    The isotype wants identical units and a screen that does not fight them. A fine vertical
    line screen reads as a texture at 432 px and as engraving at 1080, and it keeps the units
    from becoming clip art by giving them a print surface.
  palette: >
    night paper, limestone ink, dusk gold for three units and three labels.
  value_structure: >
    Ten mid units on black, three of them in the frame's only colour. The type above is the
    lightest thing.
  motion: >
    Hook, down to the first shelf, count left to right, drop to the second shelf, count again.
type:
  hook: "Ten chapters. The machine is in three."
  dek: "Every chapter of the course text is a thing a student must be able to do with money. Seven of them carry none of the four machine terms."
  labels: ["THE COURSE TEXT", "TEN KNOWLEDGE STATEMENTS", "05 / 09", "01", "02", "RESEARCH", "EXPLAIN", "05", "06", "APPRAISE", "08", "09", "10", "c12 c13 c19 c20 c21   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim: []
acceptance:
  - ten units are countable at 432 px, five on each shelf
  - exactly three units are accent and their labels are the three verbs
  - every unit is the same size, a seated figure at a desk, and no two overlap
  - the line screen is visible as lines at 1080 px inside the pale units
```

```yaml
slide: 6
layout: DIAGRAM
primary_image:
  subject: one student at one desk, close, with a monitor, a phone in hand and a second screen, annotated by three leaders
  rect: [400, 560, 680, 790]
  bleeds: [right, bottom]
accent: "#E0956A"
job: >
  Explain the three expectations as three things on one desk, so the reader sees what each
  verb is done to rather than reading three quotations.
claims: [c14, c15, c16]
numerals: []
composition:
  structure: >
    Camera at 1.05 m, horizon at 900, focal 900 px. The desk at X 1.15, Z 3.2 sits right of
    centre and leaves the whole left column to three notes. A pool of light on the desk and
    the floor falls to black toward the notes. Three leaders run from the notes' right edges
    to a dot on the monitor, the phone and the second screen.
  bands: >
    TOP third, the hook and the first note. MIDDLE third, the second note and the monitor and
    figure. BOTTOM third, the third note, the desk's front, the chair and the floor.
  focal: >
    The monitor, an AREA of about 170 by 140 px, the first leader's target.
art:
  technique: "TXOBJ desk and office_chair, TXFIG sit pose holding a phone, a bespoke tablet sprite, printed by TXINK as a cross hatch at cell 7, angle 38, contour plate at 1.2, -0.9 px. Leaders drawn flat in ink with accent dots, ending short of every glyph band."
  why_this_technique: >
    A diagram is an engraving with labels, and the engraver's hatch is its native surface:
    three passes at three angles carry three tones, and the contour plate carries the edge.
    The leaders are flat ink so they read as annotation rather than as part of the print.
  palette: >
    night paper, limestone ink, dusk gold on the three leader dots and the three phrases.
  value_structure: >
    The figure and the desk are the mid hatched mass. The pool of floor under them is the mid
    field. The left column is black and carries the notes.
  motion: >
    Hook, down the three notes, each leader carrying the eye across to its object and back.
type:
  hook: "Three verbs, three chapters, one desk."
  dek: ""
  labels: ["THE THREE EXPECTATIONS", "06 / 09", "Research", "Explain", "Appraise", "c14 c15 c16   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim:
  - c14: "artificial intelligence tools"
  - c15: "algorithm-driven recommendations"
  - c16: "automated investment platforms"
acceptance:
  - three leaders each end in a dot on a different object, the monitor, the phone, the second screen
  - no leader crosses a letter of any note
  - the hatch shows three line directions at 1080 px inside the figure
  - the floor is black under the notes column and hatched under the desk
```

```yaml
slide: 7
layout: CLOSE_CROP
primary_image:
  subject: the board's release so close the reader is inside the newsprint, the sentence set large on a sheet cropped by both sides
  rect: [0, 560, 1080, 640]
  bleeds: [left, right]
accent: "#E0956A"
job: >
  Put the reader inside the announcement at the two words it ends on, so the absence the deck
  is about is something seen rather than counted.
claims: [c22, c23, c24]
numerals: []
composition:
  structure: >
    A sheet wider than the frame, turned under a degree, cropped by the left and right edges,
    carrying the release's one sentence in five lines of a document face at 106 px. The
    halftone under the type is coarse enough to read as newsprint under a loupe. A hand drawn
    ring in the accent around the last two words.
  bands: >
    TOP third, the reserve with the hook and dek. MIDDLE third, the first three lines. BOTTOM
    third, the last two lines and the ring, fading to paper under the furniture band.
  focal: >
    The words and more, an AREA of about 420 by 110 px, ringed.
art:
  technique: "A mid grey sheet in the twin, printed by TXINK as a halftone at cell 9, angle 18, so the sheet itself is a visible dot field, with DOM type over it in Instrument Serif and the ring as an SVG path from TXINK.wobble in the DOM."
  why_this_technique: >
    The crop is the point. At cell 9 the dots are a texture the reader can see through the
    letters, which is what a newsprint macro looks like, and the ring is in the DOM rather than
    the canvas so it is a mark beside the type and never a rule through it.
  palette: >
    night paper, limestone ink for the dot field, page ink #1B1830 for the type, dusk gold for
    the ring.
  value_structure: >
    The sheet is the light field, the largest in the deck. The type on it is the darkest. The
    night above it carries the hook.
  motion: >
    Hook, into the sheet at the first line, down five lines to the ring.
type:
  hook: "Its own summary ends in \"and more.\""
  dek: "The board's release names the goals and no technology. The course text names three."
  labels: ["THE ANNOUNCEMENT", "07 / 09", "c22 c23 c24   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim:
  - c22: "The new TEKS will teach students how to set goals, budget, save, invest, develop business plans and more."
acceptance:
  - the sheet leaves the left and the right edge of the frame
  - the halftone dots are visible between the letters of the sentence at 1080 px
  - the ring encloses and more and touches no letter
  - the five lines of the sentence are the source's words in order with nothing added
```

```yaml
slide: 8
layout: SPLIT_HORIZON
primary_image:
  subject: a Texas high school at dusk at true scale, a flagpole, three buses in the lot, students walking in, a water tower and an oak behind
  rect: [0, 540, 1080, 810]
  bleeds: [left, right, bottom]
accent: "#E0956A"
job: >
  Take the story to the district that has to staff it, as a place at the hour buses run,
  under one straight cut with the ask above it.
claims: [c22, c24]
numerals: []
composition:
  structure: >
    One straight cut at y 540. Above it, flat night and the type. Below it, camera at 1.7 m,
    horizon at 790, focal 640 px. The school at Z 58, three buses at 24 to 30 m, seven students
    at 7 to 8 m, the water tower at 260 m, the oak at 44 m, the pole and wire at 16 m.
  bands: >
    TOP third, the type on night. MIDDLE third, the cut, the sky, the school and the tower.
    BOTTOM third, the buses, the students and the lot fading to paper under the furniture.
  focal: >
    The school's entrance block with the flag, an AREA of about 200 by 120 px on the horizon.
art:
  technique: "TXOBJ school, water_tower, school_bus, live_oak, utility_pole and wire, TXFIG crowd, printed by TXINK as a halftone at cell 6, angle 26, contour plate at 1.1, -0.8 px."
  why_this_technique: >
    The split wants the image to be a photograph's worth of place, so the halftone returns at
    the fine cell of frame 1, which also ties the deck's first and eighth frames together.
  palette: >
    night paper, limestone ink, dusk gold on the flag alone.
  value_structure: >
    The type half is flat night. The image half is a mid dot field with the light school
    across it and the black cut between.
  motion: >
    Hook, dek, drop across the cut to the flag, along the building, down to the students.
type:
  hook: "Ask your district who is staffing the three expectations."
  dek: "The release quotes the board chairman on what he calls the vital aspect of the new standards, and it is not the machine."
  labels: ["THE DISTRICT", "08 / 09", "c22 c24   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim: []
acceptance:
  - one straight horizontal cut separates flat night above from the image below
  - three buses are countable in the lot at 432 px
  - the water tower is smaller than the school's entrance block and sits above the roof line, so the depth reads
  - the flag is the frame's only accent
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: night over a small Texas town at true scale, a water tower, houses, a transmission line, a pump jack, a fence, the road to the horizon
  rect: [0, 500, 1080, 850]
  bleeds: [left, right, bottom]
accent: "#E0956A"
job: >
  Close on Texas at the scale the rule reaches, one lit window in one house, with the
  constellation fixed under it.
claims: [c1, c2, c5, c9, c11]
numerals: []
composition:
  structure: >
    Camera at 2.2 m, horizon at 700, focal 640 px. The road runs from the bottom centre to the
    horizon. Three towers at 420 to 520 m, the water tower at 170 m, five houses at 96 to 140
    m, the pump jack at 48 m, an oak and a mesquite near, a fence line across the middle
    distance. The type in the sky above, the constellation on the near ground below.
  bands: >
    TOP third, the hook and dek on night. MIDDLE third, the horizon with every object on it.
    BOTTOM third, the road, the fence, the wordmark, the star and the date.
  focal: >
    The lit window, an AREA of about 16 by 16 px in the middle house, the frame's only accent.
art:
  technique: "TXOBJ water_tower, house, transmission_tower and wire, pump_jack, live_oak, mesquite and a fence, printed by TXINK as a stipple at cell 5, six dots a cell, contour plate at -1.0, 0.9 px."
  why_this_technique: >
    Stipple at night is stars and dust, the register frame 3 opened, so the deck closes in
    the surface it stood the Capitol in. Everything sits on one horizon at true scale so the
    town has a size the bus and the school gave the reader earlier.
  palette: >
    night paper, limestone ink, dusk gold for one window.
  value_structure: >
    The sky is black and carries the type. The horizon is a thin light band of objects. The
    near ground is a mid stipple with the road lighter.
  motion: >
    Hook, down to the horizon, along it to the tower and the lit window, down the road to the
    wordmark.
type:
  hook: "The rule is made. The credit is required."
  dek: "The board acted on an attachment headed \"Text of Proposed New 19 TAC\". The filed rule is unchecked here."
  labels: ["19 TAC SECTION 113.26", "09 / 09", "TEXAS AI DOCKET", "Item dated September 4th, 2026", "c1 c2 c5 c9 c11   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim:
  - c11: "Text of Proposed New 19 TAC"
acceptance:
  - the water tower, the pump jack and the houses all stand on one horizon line
  - the road's two edges converge on the horizon
  - one window is accent and nothing else on the frame is
  - the wordmark, the star and the site line are all present and below the image
```
