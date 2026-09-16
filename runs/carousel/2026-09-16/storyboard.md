# Carousel no. 26 — 2026-09-16 — TWO ROOMS, ONE MARK

**Story.** The University of Texas at Arlington published an account on September 10th of an AI
conversational tutor built on a National Science Foundation grant and designed so that it will
NOT give the student the answer. It offers a hint. The same release says the same researcher has
already begun testing the same system with the Fort Worth Police Department on de-escalation
training, where it judges whether an officer is listening. A footnote at the foot of the page
says that second half is funded by the Department of Justice under its own grant number.

**THE SYNTHESIS, AND WHY EACH PIECE CAME FROM WHERE IT DID.** Three directors were spawned on
three lenses and the deck takes its spine from one, its register from the second and its single
best image from the third. That is written down because the next run should know the panel was
used as a panel rather than as three drafts to pick between.

- **The spine is the TWO ROOMS lens.** The only surprising fact in this record is that one method
  has two customers, and a reader feels a change of ROOM in their body before they can argue
  about it. So frames 3 and 6 are ONE CAMERA, declared once, and the light between them inverts.
- **The register is the PAPER TRAIL lens**, and it is the piece that was measured rather than
  argued. `ledger_check.LIGHT_L` is 60.0 and the last nine decks measured deck medians of 11.4,
  31.5, 71.1, 18.1, 42.0, 6.1, 13.5, 6.0 and 13.7. **Seven of nine came in under L\* 20.** The
  habit is the near-black deck, not the light one, and three decks running have shipped one lit
  sheet on a near-black ground. This deck runs MID, planned median 44, on a pale stock with dark
  ink. It clears the light cap by sixteen points and it is not the frame the last three shipped.
- **The one image is the WITHHELD ANSWER lens**, frame 1. A page of a student's own working, and
  the entire contribution of a three quarter million dollar federally funded machine is one mark
  in the margin you have to look for.

**THE STRUCTURAL LAW. THE ACCENT IS THE MACHINE'S OWN MARK, AND NOTHING ELSE WEARS IT.**
Wherever the system hands something to a person, it appears in `fed_blue` at one intensity. In
the classroom it is a nine millimetre tick in a margin. In the Fort Worth room it is a patch on
the floor between two people. Nowhere else in nine frames. **A reader who never reads a word
watches one mark migrate out of a margin and into a room between two human beings**, which is
the whole argument and it is carried in colour rather than in a headline. Frames 2, 5, 7 and 9
carry none, and frame 9 carrying none is the deck's load bearing absence.

**Camera and light.** Frames 3 and 6 are identical by construction: a seated public eye at
1.10 m, horizon 838 px, f 820, and they share no wall, floor or ceiling construction. **What is
identical is the reader's body and not the architecture.** The light is what changes and it never
trades roles. A fluorescent troffer grid at 2.9 m, azimuth 0, elevation 72, is the institution's
light and falls on frames 3, 5 and 9, so top faces are the brightest thing and every shadow is
short and hard under a leg. One warm lamp at 1.2 m, azimuth 118, elevation 14, is the light of a
room where two people are talking and falls on frames 4, 6 and 8, so sides are lit, top faces are
dark and shadows run long toward the reader. Frames 1, 2 and 7 are copy stands over a table at
elevation 18. Nine constructions, one deliberate repeat, and the repeat is the argument.

**Palette, MEASURED rather than chosen by eye.** Both other directors' palettes were measured
first and five of six of one and six of eight of the other came back COLLISION against the 65
hexes of the last eight decks. That is not a failure of taste. Four consecutive decks shipped a
warm cream ink on a warm dark ground and the space is used up, so this deck went where the space
is, which is COOL, and which is also the honest material palette for a 1970s engineering building
and a municipal training room. `out/2026-09-16/palette_measured.json` carries the arithmetic. A
random colour's nearest neighbour in this window is p10 9.84 and median 27.82.

    bond       L* 76   #BBC0C6   the copy stock and the deck's most common value  dE 10.59
    toner      L*  1   #070016   the ink                                          dE 10.56
    table      L* 37   #525862   the work surface                                 dE 10.65
    block      L* 57   #818C90   painted concrete block, both rooms' walls        dE 11.08
    shade      L* 25   #343C46   rooms behind, and the deck's dark                dE 10.65
    lamp       L* 71   #D9A45E   the warm lamp in room two, never a mark          dE 13.84
    fed_blue   L* 14   #00205B   THE ACCENT, PMS 281 C, `flag_blue` in brand.yaml dE 24.32

`fed_blue` is dark against a pale stock on purpose, so a nine millimetre tick reads as a MARK at
432 px rather than as a glow. Flag red `#BF0A30` is UNSPENT and that is deliberate: there is no
comment window, no hearing and no deadline anywhere in this record, so a reserved red would be a
false urgency.

**The value arc, and THE SCREEN FLOOR THAT RE-PLANNED IT.** Planned per frame: 68, 62, 44, 30,
52, 26, 58, 40, 22. Deck median 44, spread 46.

**A PALE STOCK INVERTS THE SCREEN CEILING INTO A SCREEN FLOOR, and this run measured it rather
than reasoning about it.** On a dark ground a screen bounds how LIGHT a frame can get. On this
one it bounds how DARK, because TXINK lays toner where the twin is dark and a screen can only
put down so many marks. Frame 9 was written first with a hatch at cell 6 and a planned 22, it
rendered at 57.6, and the probe says why. `out/2026-09-16/screen_floors.json` carries the
arithmetic, measured by printing a black field and a white field through all nine configurations
on this deck's own stock and ink and reading the press back:

    stipple c5   floor 64.0   ceiling 77.5     stipple c6   floor 64.0   ceiling 77.5
    hatch   c6   floor 45.9   ceiling 77.5     hatch   c7   floor 45.2   ceiling 77.5
    line    c4   floor  8.9   ceiling 77.5     line    c5   floor  9.9   ceiling 77.5
    halftone c7  floor  3.6   ceiling 77.5     halftone c8  floor  3.4   ceiling 77.5
    halftone c9  floor  3.6   ceiling 77.5

**So a stipple on this stock is a LIGHT FRAME'S SCREEN and nothing else**, a hatch cannot reach
below the mid forties whatever is drawn in it, and only halftone and line can carry a dark frame.
The screens were then assigned to the value each frame needs rather than to the texture that
sounded right, and every one of the nine targets above is inside its own screen's measured range:

    1 stipple c5  68      4 line c5     30      7 hatch c7    58
    2 line c4     62      5 hatch c6    52      8 halftone c8 40
    3 halftone c7 44      6 halftone c9 26      9 line c4     22

No two adjacent frames share a screen mode. **What this does NOT excuse is a frame that came out
flat because nothing was drawn in it**, and frame 9 was redrawn rather than merely rescreened.

**Six refusals, each from a different director and each load bearing.**

1. **NO UNIFORM, NO BADGE, NO WEAPON AND NO VEHICLE IN NINE FRAMES.** All three directors wrote
   this independently. The record describes an officer LISTENING, and drawing the equipment would
   make the deck about policing instead of about the method.
2. **NOTHING IS DRAWN AS A VERDICT ABOUT A PERSON.** Frame 6's accent is symmetrical about the
   midpoint between two chairs so it points at neither, and frame 8's three readings are three
   identical units whose whole difference lives in a ruled nameplate. Nothing is ranked, dimmed,
   crossed or coloured.
3. **THE TWO MONEY STRINGS NEVER SHARE A FRAME.** The university prints `$750,000` (c4) and the
   federal record prints `749999` and `FY 2026 = $749,999.00` (c24). One string per frame,
   attributed to whoever printed it, five frames apart, never rounded and never a third form.
4. **THE TWO FUNDERS ARE NEVER BLURRED.** Frame 7 draws them on two carriers. The university's
   own sheet has a lit lip and a contact shadow, the federal record is set into the frame with no
   carrier at all, and under the Department of Justice grant number a ruled field is left empty
   and LIT rather than black, because no federal record for it was reached this run (a4).
5. **NO PERFORMANCE IS EVER SHOWN.** Neither source publishes an evaluation result for either use
   (a3). Every frame draws a design or a funder. No accuracy figure exists and none is implied.
6. **NO COUNTY IS DRAWN AND NO MAP RUNS.** Neither source names a county (a2), and MAP drew the
   same 254 county Albers sheet on decks 23, 24 and 25. All three directors refused it
   independently.

---

```yaml
slide: 1
layout: CLOSE_CROP
primary_image:
  subject: "one sheet of engineering homework at true page size, 216 by 279 mm, on a work table under a copy stand, covered in a student's own graphite working, with a ruled and empty answer line across the foot and ONE nine millimetre fed_blue tick in the left margin beside line seven"
  rect: [0, 150, 1080, 1200]
  bleeds: [left, right, bottom]
accent: "#00205B"
job: >
  Put the deck's whole thesis in the reader's hands before a word of it is argued. A page of
  somebody's own reasoning, and the entire contribution of the funded machine is a mark you have
  to look for.
claims: [c15, c10, c4]
numerals:
  - value_from: c4
composition:
  structure: >
    The camera is 0.32 m above the sheet and square to it, so the reader is inside the page
    rather than looking at a desk. The sheet is cropped by left, right and bottom, which puts
    the reader's own body where the student's would be. The working runs eleven lines down the
    upper two thirds and stops, and the ruled answer line sits alone across the foot with 60 mm
    of bare page above it, so the emptiest part of the frame is the part the machine did not fill.
  bands: >
    Top third, the head of the sheet and the hook in the reserve. Middle third, eleven lines of
    graphite working and the single fed_blue tick in the left margin. Bottom third, bare stock,
    the ruled answer line, and a 0.14 m mechanical pencil lying across the lower right with a two
    part contact shadow.
  focal: "the lit upper-middle field of the sheet where the graphite is densest, which is the lightest large area in the frame. The tick is found second, which is the point"
art:
  technique: "stipple at cell 5 as the paper's own tooth, with the graphite drawn as token length strokes rather than glyphs. Measured range 64.0 to 77.5, and this frame wants 68"
  why_this_technique: >
    A stipple is the field guide's mark and it is the only screen that reads as paper fibre
    rather than as printing. The working must read as made by a hand and must print NO word and
    NO numeral, so it is strokes at true pencil weight and never letterforms.
  palette: "bond stock, toner graphite, table under the sheet, one fed_blue tick"
  value_structure: >
    The sheet is the lightest thing in the frame and the table is the darkest. The tick is the
    only saturated mark. Frame median L* planned at 68.
  motion: "down the working, stall at the empty answer line, back up to the tick"
type:
  hook: "It was built to not tell you."
  dek: "A federal grant is paying for a tutor that answers a student with a hint."
  labels: ["c15", "c4"]
verbatim: []
acceptance:
  - "the fed_blue tick is exactly one mark, in the left margin, and appears nowhere else on the frame"
  - "the tick measures 9 mm at true page scale and terminates at least 4 mm short of the first stroke on its line"
  - "no glyph and no numeral appears anywhere in the graphite working, which is strokes only"
  - "the ruled answer line carries no mark of any kind"
  - "the frame's median L* at 432px is 60 or higher"
  - "the mechanical pencil throws a two part contact shadow, and the shadow region and the ground region differ by 4.0 L* or more"
risks:
  - "a stipple at cell 5 has a FLOOR on a pale stock and the sheet may come back muddy. Print a black field through this configuration and measure before trusting 68"
  - "token strokes can accidentally read as words at 432 px, which would fail verbatim_check and deserve to"
```

```yaml
slide: 2
layout: DOCUMENT
primary_image:
  subject: "the National Science Foundation award record printed to US letter, 216 by 279 mm, lying on the same work table turned 0.6 degrees, carrying the award id 2539663, the title, and the abstract sentence at reading size"
  rect: [108, 470, 868, 740]
  bleeds: []
accent: "none"
job: >
  Hand the reader the federal government's own statement of the problem, in its own words, so
  the tutor's refusal is a funded policy rather than one researcher's preference.
claims: [c31, c22, c30]
numerals:
  - value_from: c22
composition:
  structure: >
    A copy stand at elevation 18 over the table, the sheet turned 0.6 degrees so it is a physical
    object rather than a screenshot. The c31 sentence is the only line at reading size and every
    other line is real text set small, so the eye lands on the sentence without being pointed at.
  bands: >
    Top third, the award id and the title in mono at the sheet's head. Middle third, the abstract
    with the c31 sentence at reading size. Bottom third, the sheet's foot LIFTING off the table on
    its own cockle, so the near edge carries a lit paper thickness and throws a two part contact
    shadow that rakes across the table's grain and falls away into shade at the frame's foot.
  focal: "the block of the abstract paragraph around the c31 sentence, the lightest dense area on the sheet"
art:
  technique: "line screen at cell 4 carrying the table only, the sheet painted unscreened after the press. Measured range 8.9 to 77.5"
  why_this_technique: >
    A line screen is the banknote's mark and it belongs to a document. The sheet is painted after
    the press because a screened field cannot hold type at the contrast a reading frame needs.
  palette: "bond sheet, toner type, table beneath, no accent"
  value_structure: >
    The sheet is the lightest thing and the table edge at the foot is the darkest. Frame median
    L* planned at 62.
  motion: "head to the sentence, then down to the foot"
type:
  hook: "The problem, in the government's words."
  dek: "The award that paid for the tutor says why it exists."
  labels: ["c31", "c22"]
verbatim:
  - c31: "students frequently use them to obtain answers rather than develop the reasoning and problem-solving skills that define engineering competence"
acceptance:
  - "the frame prints the c31 sentence verbatim inside straight quotation marks and attributes it to the award record"
  - "the award id reads exactly 2539663"
  - "no accent pixel appears anywhere on this frame"
  - "the sheet's near edge carries a lit paper thickness, so it sits ON the table rather than floating"
  - "the frame's median L* at 432px is 55 or higher"
risks:
  - "a full page of real text at true scale is unreadable at 432 px and can read as grey noise. The c31 sentence must be at least 26 px at render scale"
```

```yaml
slide: 3
layout: FULL_BLEED
primary_image:
  subject: "a classroom at a seated public eye of 1.10 m with three ranks of student desks at Z 3.0, 5.2 and 7.6 and nine seated figures at true scale, lit only by one fluorescent troffer band across the ceiling at 2.9 m, with exactly one desk in the near rank carrying a lit tablet"
  rect: [0, 0, 1080, 1350]
  bleeds: [left, right, top, bottom]
accent: "#00205B"
job: >
  ROOM ONE. Establish the camera the reader will be put back into three frames later, and show
  that the instructor teaches while the machine lives in the homework.
claims: [c13, c33]
numerals:
  - value_from: c33
composition:
  structure: >
    The reader sits in the third row. The near rank is cropped by both edges and the bottom so
    the reader is inside the room rather than watching it. The troffer band runs across the
    ceiling as the only light, so every top face is bright and every shadow is short and hard.
  bands: >
    Top third, ceiling and the troffer band. Middle third, three ranks of desks and nine figures.
    Bottom third, the near rank's desktops cropped, and the one lit tablet.
  focal: "the lit tablet and the pool it throws on the near desktop, the only saturated area in a frame otherwise built of greys"
art:
  technique: "halftone at cell 7, figures and furniture given different greys in the twin. Measured range 3.6 to 77.5, which is why a room frame takes a halftone here"
  why_this_technique: >
    A halftone is the newspaper photograph and a room full of people is a photograph. The
    separate greys exist because a crowd at one tone merges into a single pale mass, which is a
    named failure in the illustration system.
  palette: "block walls, table desktops, shade under the desks, bond ceiling, one fed_blue tablet pool"
  value_structure: >
    The ceiling band is the lightest thing and the floor under the near rank is the darkest.
    Frame median L* planned at 44.
  motion: "along the troffer band, down the ranks, stop at the lit tablet"
type:
  hook: "The courses do not change."
  dek: "The instructor still teaches. The machine lives in the homework, across four undergraduate courses."
  labels: ["c13", "c33"]
verbatim: []
acceptance:
  - "exactly nine seated figures are drawn"
  - "exactly one tablet is lit and it is in the near rank"
  - "the fed_blue appears only as the pool of light on the desktop and never as the tablet's own face"
  - "the accent covers less than 8 percent of the frame"
  - "every figure and the furniture beside it differ by at least 8 L* in the twin, so the rank does not merge"
  - "the frame's median L* at 432px is between 36 and 52"
risks:
  - "this is a Texas classroom and deck 21 on September 11th was a Texas classroom. The separations are the light, the eye height and the palette, and they must hold in the render rather than in this paragraph"
  - "nine figures at Z 3 to 7.6 can come out 30 px tall. Bring the near rank in until the figures own their share of the rect"
```

```yaml
slide: 4
layout: FIGURE_SCALE
primary_image:
  subject: "a 1.6 by 1.2 m kitchen table with two seated figures at it, one at child proportions and one at 1.70 m, and a third 1.70 m figure standing beside it at X -1.02 Z 1.72, under one warm lamp at 1.2 m, with a 0.25 by 0.18 m tablet on the table whose face is one flat slab of the frame's brightest ink"
  rect: [0, 340, 1080, 1010]
  bleeds: [left, right, bottom]
accent: "none"
job: >
  Show where the project came from, which is one person watching two kinds of people do the same
  thing, and give the reader a human size for everything else in the deck.
claims: [c5, c11]
numerals: []
composition:
  structure: >
    Standing eye at 1.60 m with the horizon at 0.58, so the reader is the person standing and
    watching. The warm lamp rakes from the right at elevation 14 so sides are lit and every top
    face is dark, which is the exact inverse of the classroom's overhead grid and the first time
    the reader meets that light.
  bands: >
    Top third, the dark room behind and the hook. Middle third, the table, the three figures and
    the tablet. Bottom third, the floor LIT by the lamp at elevation 14, carrying the long raking
    shadows of three table legs and of the standing figure, each one a separate modeled mass
    running toward the reader across a floor with its own stipple texture. The verbatim quote sits
    in the dark between two of those shadows.
  focal: "the flat slab of the tablet face, the brightest area in the frame and the thing being handed over whole"
art:
  technique: "line screen at cell 5, the tablet face painted flat and unscreened. A stipple was planned here and CANNOT reach 30 on this stock, measured floor 64.0, so the screen changed rather than the number"
  why_this_technique: >
    The tablet's AREA is the frame's whole comparison against slide 1's nine millimetre tick, so
    it is painted flat where everything else is screened, and the difference in area is the
    argument.
  palette: "shade room, table surface, lamp key, toner figures, no accent"
  value_structure: >
    The tablet face is the lightest thing and the room behind the figures is the darkest. Frame
    median L* planned at 30.
  motion: "from the standing figure down the sightline to the tablet, then out to the quote"
type:
  hook: "It started with her own children."
  dek: "Shuchi Deb is an associate professor at the University of Texas at Arlington. She watched her own children and her students use AI without learning."
  labels: ["c11", "c5"]
verbatim:
  - c11: "They were just using AI to finish the assignment,"
acceptance:
  - "no accent pixel appears anywhere on this frame"
  - "the tablet face is a single flat unscreened area and carries no drawn content"
  - "every table leg and both seated figures throw a two part contact shadow, and each shadow region differs from its ground region by 4.0 L* or more"
  - "the c11 quote is printed verbatim inside straight quotation marks with attribution"
  - "the child figure is drawn at child proportions rather than as a scaled adult"
  - "the frame's median L* at 432px is between 24 and 36"
risks:
  - "a warm lamp and a dark room can collapse into one value. The lamp key and the shade must differ by at least 20 L* in the render"
```

```yaml
slide: 5
layout: TYPE_AS_OBJECT
primary_image:
  subject: "the university's own headline verb pair cut as solid letterforms 0.9 m tall standing on a concrete floor, seen at a shallow three quarter from an eye of 0.55 m, running off both frame edges so the phrase is bigger than the frame"
  rect: [0, 300, 1080, 900]
  bleeds: [left, right]
accent: "none"
job: >
  Make the method physical at a size, in the university's own three words, so the deck's claim
  about restraint is a thing standing on a floor rather than an adjective.
claims: [c1, c32]
numerals: []
composition:
  structure: >
    The camera is at 0.55 m, below the letters' midline, with the horizon at 0.70, so the reader
    looks slightly up at the words and they have mass. The phrase runs off both edges because a
    phrase that fits inside the frame is a headline and a phrase that does not is an object.
  bands: >
    Top third, the room behind and the hook. Middle third, the letterforms. Bottom third, the
    concrete floor at its own aggregate texture, the feet of the letterforms with a two part
    contact shadow under each, and their cast shadows running right from the ceiling grid, so the
    bottom band is a lit floor with modeled masses on it rather than a caption strip.
  focal: "the lit faces of the letterforms, the largest bright area in the frame"
art:
  technique: "hatch at cell 6 on the floor, the letter faces unscreened. Measured range 45.9 to 77.5 and this frame wants 52"
  why_this_technique: >
    Screening the floor and leaving the faces flat is what makes the letters read as solid bodies
    standing in a room rather than as type laid over a picture of one.
  palette: "bond letter faces, block floor, shade behind, no accent"
  value_structure: >
    The letter faces are the lightest thing and the room behind them is the darkest. Frame median
    L* planned at 52.
  motion: "left to right along the phrase, then down into the cast shadows"
type:
  hook: "teaches, not tells"
  dek: "The university's own words for what it built."
  labels: ["c1"]
verbatim:
  - c1: "teaches, not tells"
acceptance:
  - "the phrase printed is exactly teaches, not tells and is attributed to the university's own headline"
  - "every letterform throws a cast shadow from the ceiling grid at elevation 72, and all shadows run the same direction"
  - "no accent pixel appears anywhere on this frame"
  - "the letterforms cross both the left and the right frame edge"
  - "the frame's median L* at 432px is between 44 and 60"
risks:
  - "nobody has cast this sentence into a building, so the frame must attribute the words to the release by claim id or a reader may take the band for a photograph of a real wall"
```

```yaml
slide: 6
layout: FULL_BLEED
primary_image:
  subject: "a de-escalation training room at THE SAME CAMERA as frame 3, eye 1.10 m, horizon 838 px, f 820, with two office chairs facing each other 2.2 m apart at Z 3.2 and Z 5.4, a seated 1.70 m figure in each, four folded chairs against a painted block wall and a door with a push bar, lit by one warm lamp"
  rect: [0, 0, 1080, 1350]
  bleeds: [left, right, top, bottom]
accent: "#00205B"
job: >
  THE TURN. Put the reader back in the same body, in a different room, and let them find the same
  mark on the floor between two people.
claims: [c7, c8, c9]
numerals: []
composition:
  structure: >
    Identical eye height, horizon and focal length to frame 3, and no shared wall, floor or
    ceiling construction with it. The ceiling grid is OFF. One warm lamp rakes from the right at
    elevation 14 so every shadow runs long toward the reader and every chair back's top is dark,
    the exact inverse of the classroom.
  bands: >
    Top third, the block wall, the door with the push bar and the hook at half width in the
    lamp's dark side. Middle third, the two chairs and the two seated figures. Bottom third, the
    near chair's seat and legs CROPPED at the frame foot as a modeled mass, the carpet tile grid
    receding under it with its own texture, the long raking shadows of both chairs running toward
    the reader, and the fed_blue patch lying flat between them.
  focal: "the fed_blue patch on the carpet between the two chairs, the only saturated area in the frame and the same ink the reader met in a margin on slide 1"
art:
  technique: "halftone at cell 9. A cross hatch was planned here and CANNOT reach 26 on this stock, measured floor 45.2, so the screen changed rather than the number"
  why_this_technique: >
    A cross hatch is the engraver's mark and it belongs to a room drawn rather than photographed,
    which is what separates this room from frame 3's halftone crowd.
  palette: "block walls, shade floor, lamp key, toner figures, one fed_blue floor patch"
  value_structure: >
    The lamp's lit side of the near chair is the lightest thing and the ceiling is the darkest.
    Frame median L* planned at 26.
  motion: "in through the door, down to the two figures, stop on the patch between them"
type:
  hook: "The same machine is in a second room."
  dek: "Testing with the Fort Worth Police Department has already begun."
  labels: ["c7", "c8"]
verbatim: []
acceptance:
  - "no uniform, no badge, no weapon and no vehicle appears anywhere on this frame"
  - "the fed_blue patch is symmetrical about the midpoint between the two chairs, so it points at neither figure"
  - "the fed_blue patch is one flat value with no ramp and no hot centre"
  - "the accent covers less than 8 percent of the frame"
  - "the eye height, horizon and focal length match slide 3 exactly at 1.10 m, 838 px and 820"
  - "no wall, floor or ceiling construction call is shared with slide 3"
  - "every shadow in the frame runs toward the reader, which is the opposite direction to slide 3"
  - "the frame's median L* at 432px is between 20 and 32"
risks:
  - "two people in chairs with no uniform may read as two people in chairs. The folded chairs, the push bar and the carpet tile grid carry the institution and they must be legible at 432 px or the turn is a caption"
  - "bespoke_check will find this frame and frame 3 as the deck's closest pair. The other seven have to be genuinely unlike each other or a declared pair becomes a template"
```

```yaml
slide: 7
layout: DOCUMENT
primary_image:
  subject: "the bottom 150 mm of the university's release at true page size, cropped by left, right and bottom, lifted off the table with a lit lip and a two part contact shadow, carrying the asterisk and the Department of Justice footnote, with the federal award's own funding line set into the frame beside it on no carrier at all"
  rect: [0, 200, 1080, 1150]
  bleeds: [left, right, bottom]
accent: "none"
job: >
  Show that two federal agencies pay for this system and only one of them is above the footnote,
  without ever putting the two money strings in one frame.
claims: [c7, c8, c9, c19, c24, c2]
numerals:
  - value_from: c24
composition:
  structure: >
    Two carriers in one frame, which is how the deck draws attribution without drawing a verdict.
    The university's sheet is a physical object with a lit lip and a shadow. The federal record is
    set into the frame with no carrier and no shadow, because it is a record rather than a page.
    Under the Department of Justice grant number a ruled field is left EMPTY and LIT.
  bands: >
    Top third, three real paragraphs of the release at true scale and the hook. Middle third, the
    hairline rule and the footnote at true 7 pt. Bottom third, the federal funding line on no
    carrier, and the lit empty field under the grant number.
  focal: "the lit empty ruled field under the grant number, the one place in the deck where the record has nothing to show"
art:
  technique: "hatch at cell 7 carrying the table only, both documents painted unscreened. Measured range 45.2 to 77.5 and this frame wants 58"
  why_this_technique: >
    The same screen as frame 2 on the table and a different crop, a different camera and a
    different value, so the deck's two document frames are two readings of one stock rather than
    one move twice.
  palette: "bond sheet, toner type, table beneath, no accent"
  value_structure: >
    The release's lit head is the lightest thing and the table under the sheet's foot is the
    darkest. Frame median L* planned at 58.
  motion: "down the paragraphs to the rule, across the footnote, out to the federal line"
type:
  hook: "Two agencies pay for this."
  dek: "The release names the National Science Foundation up top. The Department of Justice is a footnote."
  labels: ["c19", "c24"]
verbatim:
  - c19: "This work is sponsored by the Fort Worth Police Department and funded by the U.S. Department of Justice under Grant No. 15PBJA-23-GG-06172-NTCP"
acceptance:
  - "the footnote is printed verbatim and includes the grant number 15PBJA-23-GG-06172-NTCP exactly"
  - "the only money string on this frame is the federal record's, and it reads either 749999 or FY 2026 = $749,999.00, and the string $750,000 appears nowhere on it"
  - "the university's sheet throws a two part contact shadow and the federal line has no carrier and no shadow"
  - "the ruled field under the grant number is lit rather than black and carries no mark"
  - "no accent pixel appears anywhere on this frame"
  - "the frame's median L* at 432px is 50 or higher"
risks:
  - "a reader may attach the federal money string to the Department of Justice grant number, which is the one thing the record flatly refutes. The two carriers and the empty field are the mitigation and a cold reader must be tested against this frame before the panel"
  - "a lit empty field can read as a redaction, which would say something was removed from a page where nothing was. It carries no hard edge and nothing sits under it"
```

```yaml
slide: 8
layout: DIAGRAM
primary_image:
  subject: "three identical units at true scale on a long lens at f 2400 at Z 16, each unit two front view 1.70 m figures 1.4 m apart with a 0.35 m panel between them casting a fed_blue patch on the floor, the three units identical by construction with every difference in a ruled nameplate beneath"
  rect: [0, 330, 1080, 780]
  bleeds: [left, right]
accent: "#00205B"
job: >
  Draw what the system listens for as three readings rather than as a score, without ranking,
  dimming or colouring any one of them.
claims: [c8, c9]
numerals: []
composition:
  structure: >
    A long lens at f 2400 flattens three units to equal size, so identity is a property of the
    construction rather than something the eye has to be persuaded of. Nothing is greyed, crossed
    or ordered, and every difference in the deck's whole argument lives in three ruled nameplates.
  bands: >
    Top third, the hook and the dek. Middle third, the three units at equal size. Bottom third,
    the ground receding under all three units carrying their own cast shadows as three separate
    modeled masses, the nameplates standing on posts with a contact shadow under each, and the
    floor's hatch texture falling away into shade at the frame's foot.
  focal: "the band of three fed_blue floor patches, read as one horizontal row, the only saturated area in the frame"
art:
  technique: "halftone at cell 8 on the room, the three units painted FLAT and unscreened in over() as an annotated drawing with a ruled baseline and three mono labels. Planned as a GRID and re-declared a DIAGRAM after the render: a GRID is a COUNT and is held to coming apart into separable units at thumb scale, which on a printed ground it would not, and bending the frame until it did would have made it the plate this gate exists to refuse"
  why_this_technique: >
    An isotype is what a count wants, and here the count is three readings of one interaction. A
    long lens is the only way three units at three depths come out the same size without the
    drawing cheating.
  palette: "block ground, toner figures, three fed_blue floor patches, no lamp"
  value_structure: >
    The nameplate faces are the lightest thing and the ground behind the units is the darkest.
    Frame median L* planned at 40.
  motion: "left to right across the three units, then back along the nameplates"
type:
  hook: "It reads three things."
  dek: "Kind and listening. Following what the person wants to talk about. Not connecting."
  labels: ["c8"]
verbatim:
  - c8: "kind and listening"
  - c8: "follows that conversation"
  - c8: "doesn't connect with the person"
acceptance:
  - "exactly three units are drawn and they are identical in size within 2 px"
  - "the three units stand on one ruled baseline and each carries one mono label beneath it"
  - "no unit is coloured, dimmed, crossed, ranked or ordered by any visual property"
  - "the three fed_blue patches are identical in area within 5 percent"
  - "the accent covers less than 8 percent of the frame"
  - "the grid comes apart into at least four separable pieces at thumb scale"
  - "the frame's median L* at 432px is between 34 and 46"
risks:
  - "putting the whole difference into three mono nameplates is exactly what decks 13 and 15 were marked down for. The defence is that the source ranks nothing, so encoding an order in the drawing would invent one"
```

```yaml
slide: 9
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "one podium at 0.7 by 1.25 m drawn large on a floor with a horizon, a 1.70 m standing figure at it, three student desk backs cropped in the near ground, under the same fluorescent grid as frame 3 at azimuth 0 elevation 72, with no machine light anywhere in the frame"
  rect: [0, 460, 1080, 890]
  bleeds: [left, right, bottom]
accent: "none"
job: >
  Close on the front of the room, which does not change, and give the reader the only dated thing
  in the record. The award starts October 1st and the tutor is not in a classroom yet.
claims: [c27, c25, c13]
numerals:
  - value_from: c27
  - value_from: c25
composition:
  structure: >
    A standing eye at 1.65 m from 4.5 m back with the horizon at 0.60 and f 1100, so the room
    flattens and the podium sits square to the reader. The absence of the accent is the frame's
    load bearing property and the composition leaves the near desktops empty so a reader can see
    there is no mark on them.
  bands: >
    Top third, the ceiling grid and the hook. Middle third, the podium and the standing figure.
    Bottom third, three desk backs cropped at true scale as modeled masses, each with a lit top
    edge from the ceiling grid and a short hard shadow under it on a floor carrying its own hatch
    texture, receding into shade at the frame's foot.
  focal: "the lit top face of the podium, the brightest area in a frame built of greys"
art:
  technique: "line screen at cell 4. A cross hatch was planned here, rendered at 57.6 against a planned 22, and the probe that followed is what re-planned the whole arc"
  why_this_technique: >
    The same institution's light as frame 3 with a different mark and a different lens, so the
    deck returns to where it started without redrawing it.
  palette: "block walls, shade floor, bond podium face, toner figure, NO ACCENT ANYWHERE"
  value_structure: >
    The podium's lit top face is the lightest thing and the floor at the frame's foot is the
    darkest. Frame median L* planned at 22.
  motion: "from the empty desktops up to the podium, then out to the dates"
type:
  hook: "Nothing has been graded yet."
  dek: "The award starts October 1st, 2026 and runs to September 30th, 2029. Neither the university nor the federal record publishes a result."
  labels: ["c27", "c25"]
verbatim: []
acceptance:
  - "no fed_blue pixel appears anywhere on this frame, which is the deck's load bearing absence"
  - "the three near desktops carry no mark of any kind"
  - "the dek prints the dates October 1st, 2026 and September 30th, 2029 and both trace to c27 and c25"
  - "the frame states that no result is published rather than that the system does not work"
  - "the podium throws a two part contact shadow and the shadow and ground regions differ by 4.0 L* or more"
  - "the frame's median L* at 432px is 28 or lower"
risks:
  - "an empty room can read as a verdict that the project is vapour, which a3 explicitly forbids. The copy says only what the documents date"
  - "this close names no comment window and no hearing, because the record holds none. A judge who wants a door for the reader will be right and there is nothing in the claims file to give them"
```
