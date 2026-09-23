# Storyboard — carousel no. 32, 2026-09-23
# "SOUGHT BY"

## What the fact check did to this deck, and it is the reason the deck is good

The deck was planned on a different argument and **the fact checker refuted half of it before a
line of code was written**, which is what that phase is for and is the cheapest place this could
have happened.

The original spine was that the air permit follows the ENGINES rather than the grid connection,
so the September 21st halt reaches projects the August 3rd audit structurally could not. **The
mechanism half is not established and is cut.** No agency page reachable this run states that a
stationary gas engine or turbine of this class requires an air authorization. Seven were checked.
The categorical rule lives in Health and Safety Code 382.0518 and 30 TAC 116.110 and both hosts
failed to serve text. What survives is weaker and is carried as `c14` and `c15`, which say only
that engines and turbines sit inside the agency's air permitting programme. **The word
`typically` in c14 is load bearing and no frame may spend it as though it were `must`.**

**The closing frame was cut with it.** The deck was to end on the Crusoe air permit at the
Abilene campus, permit 182126, with the route to comment. Nothing about it is verified. The
notice PDF serves 200 and does not extract, and a first read of it invented an applicant, a
reference number and an expansion of NAPD that is not what those letters mean. The whole finding
is dropped.

**What replaced it is better, and the fact checker found it inside the document.** The halt is
written on TWO SCOPES AT ONCE, on the same page, and they pull against each other:

    APPLICANT SCOPED   "all permits sought by data centers"          c1
                       "TCEQ will issue no permits sought by
                        data center projects"                        c3

    AUDIT SCOPED       "until the Electric Reliability Council of
                        Texas (ERCOT) completes its audit"           c1
                       "TCEQ must align its permitting decisions
                        with the Governor's directives and use the
                        information from those audits"               c11

A project that never enters the interconnection process generates no audit information. Read the
first way, the halt reaches it. Read the second way, there is nothing to align to. **Both
sentences are on the page and the deck's job is to put them beside each other rather than to
decide between them.** Three separate releases confine the audit to the queue in three different
phrasings (`c5`, `c6`, `c9`) and the only consequence either audit directive names is refusal of
a connection (`c7`, `c10`), so the gap is documented rather than inferred.

**THE DECK NEVER SAYS THE AGENCY HAS HALTED ANYTHING.** This is a directive, not a rule, and
nothing verified says a permit has been refused. Every string says the Governor directed. The one
enforceable thing in the text is a report back on October 19th.

**AND THE ODESSA CONTRACT IS NOT DRAWN AS AN ESCAPE, AND IT IS NOT DRAWN AS A CONNECTION EITHER.**
`immediately adjacent` is a statement about DISTANCE and not about metering, and nothing verified
says where the meter sits between that plant and that project in either direction. Frame 8 exists
to refuse both readings, not to add a second instance of the first.

**THIS PARAGRAPH SAID "THE SUPPLYING PLANT IS ITSELF A GRID RESOURCE" AND THAT IS NOT ESTABLISHED.**
It was the sentence a scorer hard-failed on frame 8 in round 1, and it went on living here, in
`compute.py` and in `claims.json` through two further rounds, because each round repaired the one
copy the scorer quoted. Six wrong statements in committed files across three rounds, every one
found by a reader and none by a check.

## The world, and the three laws that hold it

**A GAS GENERATION YARD ON A WEST TEXAS PAD AT TWENTY TO TEN AT NIGHT, LIT BY ITS OWN MAST.**
The chassis is `assets/js/deck/2026-09-23-gensetyard.js` and every frame loads it.

**ONE LIGHT.** A yard mast, high and off the camera's left shoulder, 28 degrees above the plane.
Every lit face in this deck is a LEFT face, every right face is the dark side, and every cast runs
DOWN AND TO THE RIGHT at 1.881 times the object's own height, which is checked in Node against the
chassis rather than asserted. A 1.7 m person throws 3.20 m. A 3.0 m skid throws 5.64 m.

**THE ACCENT LAW. AMBER IS THE STATE'S PAPER. STEEL IS THE MACHINERY. THEY NEVER TOUCH.**
`#E0A33F` lands only on a directive page, a posted notice and a docket line, on frames 3, 4, 7 and
9. It never touches an engine, a stack, a skid, a fence rail or the pad. Frames 1, 2, 5, 6 and 8
are the machinery frames and carry NONE. A reader who swipes twice has the code without being told
it, and the deck's argument is that these are two systems and only one of them has ever had to
answer for the other.

**THE MUTE WORLD LAW. PAPER IS THE ONLY THING IN THIS DECK THAT CARRIES GLYPHS.** No maker's plate
on a set, no unit number stencilled on a skid, no company name on the switchgear house, no sign at
the gate. It is also why no drawn yard can be read as one real facility, which matters because no
source gives a site plan for the West Texas project and the deck must not appear to have one.

**THE GROUND WAS MEASURED.** `#322C44`'s nearest neighbour among the shipped grounds this run
could read is September 20th's `#2E2016` at dE76 **24.54**, against a floor of 10, with chroma
inside the band those grounds occupy. Two earlier passes picked warm darks by eye and both landed
inside dE 3 of `#2E2016`.

**14.18 STOOD HERE AND IN THE CHASSIS AND IT WAS WRONG.** A scorer recomputed the distance by
hand, got about 26, and said the two files could not both be right. Four of the last six shipped
decks record no ground colour at all, so "the last six" is a window this comparison cannot fill,
and the claim is narrowed to the two entries that carry a hex. A wrong measurement in a committed
file is worse than none, and this one sat two paragraphs from the paragraph congratulating this
run for catching exactly that in the value arc.

**THE SCREEN IS A LINE SCREEN AT CELL 6**, which is the banknote and the engineering sheet.
**IT SAID CELL 5 HERE UNTIL A SCORER READ THE CHASSIS BESIDE IT.** The chassis moved to 6 when
the press was measured across all nine steps and `bright` and `glare` collided at cell 5, and the
chassis records why. This file kept its own copy of the number and nobody updated it, which is
this repo's oldest defect shape and is the third instance of it in one run. The distinguishing
argument was written against cell 5 and is restated against what the deck actually prints: none
of the last three decks' stocks is a LINE screen at all, they are halftone, hatch and stipple.

## The continuity devices, three of them

    CONTINUITY: MOTIF_EVOLUTION, VALUE_ARC, EDGE_TEASE
    VALUE CUT: frame 4

**THE ONE CUT IS FRAME 4 AND IT IS DECLARED RATHER THAN DISCOVERED.** `deck_coherence` measured a
25 L* step from frame 3 to frame 4 and refused to let it pass unnamed, which is the whole point of
that gate: a cut is a decision somebody makes, never a thing that happens.

It is the turn. Frames 1 and 2 are the machines, frame 3 is the page somebody wrote, and **frame 4
is where the deck stops describing and starts arguing.** The page is the deck's one lit surface
because a page under a mast is the only lit thing in a yard at night. The argument about that page
is the deck's own, and it sits in the deck's own dark. Everything after it comes back up toward the
engines.

Two attempts were made to hold the value instead, and both were refused by the frame rather than by
taste. Growing frame 4's lit area put a screened surface under a mono figure, which machine QA reads
as a rule through the line and is right to. Dropping frame 3's page a step to `stone` cost the
dark-on-light quotes their contrast. **The frame is mostly dark because its type bands have to be,
and that is a construction rather than a mood.**


1. **Motif evolution. THE ENGINE.** Forty of them as a receding line (1), one cropped to its stack
   (2), forty counted as marks (5), one beside a person (6), one seen small through a window from
   the room where the hearing was to be (9). It changes state with the argument and doubles as the
   progress indicator.
2. **Value and palette arc.** The frame medians PLANNED before any frame existed were 21, 22,
   41, 12, 14, 20, 13, 12, 14. What the nine shipped PNGs MEASURE at 432 px is
   15.7, 21.1, 37.7, 12.2, 12.4, 15.7, 12.7, 11.9, 13.6, written by `out/2026-09-23/measure.py` into
   `measurements.json` and copied here from that file.

   **THE PLANNED ROW WAS LABELLED "MEASURED" AND IT WAS NOT, WHICH IS THE FOURTH WRONG
   MEASUREMENT THIS RUN COMMITTED AND THE FOURTH A READER FOUND RATHER THAN A CHECK.** A scorer
   put the two rows side by side and named frames 1, 3 and 6 as disagreeing, which they do. The
   two rows are separated now because they answer different questions: the plan is what the deck
   set out to do and the measurement is what the press gave it, and `plan_render_check` compares
   the measurement against each frame's declared BAND rather than against either row.

   **THIS ARC WAS REVISED ONCE AND THE REVISION IS STATED RATHER THAN QUIETLY APPLIED.** The
   first plan wrote a smooth monotonic descent, 40 down to 14 in four point steps, before a
   frame existed. The press then said otherwise: a DOCUMENT frame carrying a lit page and a
   GRID frame carrying forty lit flanks are structurally brighter than a night interior, and the
   deck rendered a track whose largest step was a 25.7 L* cut into frame 4.
   `deck_coherence` refused it and named the cut.

   The cure was the ART and not the plan. Frame 3's page came off full white to the chassis bond
   value and its desk went a step down, frames 2, 5, 7 and 9 each dropped their largest fills one
   step, and `deck_coherence` passed the track it then measured.

   **THE 6.44 THAT STOOD HERE WAS A WRONG MEASUREMENT AND IT IS RECORDED RATHER THAN QUIETLY
   REPLACED.** The flow critic tried to reproduce it from the planned medians beside it, got
   8.375, and could construct no exclusion that recovered 6.44. They were right and the figure
   was stale: it was measured on an earlier cut of the art and never rewritten when the frames
   changed under it. CLAUDE.md says a wrong measurement in a file is worse than none, because the
   next reader inherits it and stops looking, and that is exactly what happened here for two
   rounds. There is no typed figure in its place now. The deck's own track is whatever
   `deck_coherence` prints against the current render, and the run record carries that print.
   September 16th's deck ran a 43 point jump back to near white and `deck_coherence` exists
   because of it.
3. **Edge tease.** The line of skids cut by frame 1's right edge completes into frame 2's crop.

## The rotation

    FULL_BLEED  CLOSE_CROP  DOCUMENT  DIAGRAM  GRID  FIGURE_SCALE  SPLIT_HORIZON  MAP  OBJECT_AND_CAPTION

`TXLAYOUT.check` returns `[]`. Nine distinct, no repeat in a row, no TYPE_AS_OBJECT, FULL_BLEED
and CLOSE_CROP present, five frames bleeding an edge against a floor of four.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "a line of about forty reciprocating gas sets on skids receding across a caliche pad at night, stacks rising out of the mast's pool into an empty sky, bleeding left, right and bottom"
  rect: [0, 300, 1080, 1050]
  bleeds: [left, right, bottom]
accent: none
job: >
  Put the reader on the pad before a word of policy, so the thing being argued about is a
  machine they have seen the size of rather than a category.

claims: [c1, c16, c17]
numerals:
  - value_from: c17
  - computed_by: "out/2026-09-23/compute.py, behind_the_meter.units read out of c17's quote"

data_in_art:
  figure: behind_the_meter.units
  drives: the count of skids drawn in the receding line

depth:
  eye: 1.65
  horizon: 700
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: -3, Z: 14}

composition:
  structure: >
    The line runs from the lower left corner to a vanishing point right of centre, so the reader
    enters at the nearest set and is carried into the dark. The type sits in the sky above the
    stacks, where the mast's falloff has already made the ground quiet, so no plate is needed
    anywhere on the frame.
  bands: >
    Top third, empty sky and the hook. Middle third, the stack tops crossing the horizon and the
    far end of the line fading in aerial perspective. Bottom third, the near two sets at full modeling, each enclosure carrying a lit left cheek against a shadowed right return so the form turns rather than sitting flat, their casts running down and right across a pad whose caliche darkens in a continuous gradient toward the bottom edge.
  
  focal: "the near set's lit LEFT flank, the largest bright area in the frame and the only place at full detail"

art:
  technique: "true-scale staging on the scene bench under one declared mast, printed through a line screen"
  why_this_technique: >
    The claim is about a count of machines that are physically somewhere. A field or a gradient
    would say the same thing about any count. Placing forty objects through a camera at twelve
    metres apiece is what makes the far end of the line unreadable, and the unreadable far end IS
    the point of the frame.
  palette: "West Texas caliche and galvanised steel under a discharge lamp, drawn from the chassis grey scale only"
  value_structure: >
    Lightest is the mast pool on the pad at the near left. Darkest is the sky above the stack
    tops, which is where the type sits. The pool falls off to the deck's own dark by two thirds of
    the way down the line, so the aerial cue and the type reserve are the same gesture.
    Frame median L* planned at 21.
  motion: "lower left to upper right along the line, then up the near stack and off the top"

type:
  hook: "SOUGHT BY"
  dek: "Two words decide who a permit halt reaches."
  labels: ["TEXAS AI DOCKET", "September 23rd", "01 / 09"]

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 15 and 27"
  - "the number of skids drawn in the receding line equals behind_the_meter.units from figures.json"
  - "a set in the line turns, lit 0.532,0.426,0.035,0.035 shade 0.581,0.426,0.035,0.035 at 432px"
  - "no amber appears anywhere on this frame, at any coverage"
  - "every cast shadow runs down and to the right"
  - "no glyph appears on any drawn object, only in the DOM type"
  - "the far end of the line is within 8 L* of the sky it sits against at 432px, so distance reads as atmosphere rather than as a cut"

risks:
  - "forty objects at twelve metres apiece may read as a texture rather than as a count, which is acceptable here because frame 5 is where the count is made countable, but the near two must stay at full detail or the frame is wallpaper"
  - "a stack at 11.5 m projects well above the horizon at this eye, so the hook band must be measured against the drawn stack tops rather than assumed clear"
```

```yaml
slide: 2
layout: CLOSE_CROP
primary_image:
  subject: "one galvanised exhaust stack and the radiator louvre bank beside it, cropped by the top, left and right edges, at detail scale, with no wire, conduit or insulator anywhere in frame"
  rect: [0, 0, 1080, 1150]
  bleeds: [top, left, right]
accent: none
job: >
  Make the absence of a connection physical. This is the only frame the reader is inside, and
  what it is missing is the whole of the audit's reach.

claims: [c7, c10]
numerals: []

depth:
  eye: 1.65
  horizon: 700
  cues: [OCCLUSION, TEXTURE_GRADIENT, CAST_SHADOW, FORM_SHADING]
  subject_at: {X: 0.4, Z: 3.2}

composition:
  structure: >
    The stack runs the full height slightly off vertical and off centre left, and the louvre bank
    fills the right two thirds with its fins running to a vanishing point just off frame. There is
    no horizon and no sky, so the reader has no way out of the picture, which is the frame's
    argument stated as composition.
  bands: >
    Top third, the stack's upper barrel leaving frame and the hook set into the dark between it
    and the louvres. Middle third, the louvre fins at their densest. Bottom third, the skid rail modeled from its lit top edge down to its dark underside, and the contact shadow spreading down and right where the set meets a pad whose caliche tooth coarsens toward the reader.
  
  focal: "the lit left cheek of the stack barrel, a continuous bright column and the brightest area in the frame"

art:
  technique: "close staging with form shading off the declared light, printed through the deck's line screen at its own cell"
  why_this_technique: >
    An absence needs a surface convincing enough that the reader believes the absence is real. A
    diagram of a disconnected box asserts it. A photograph-scale crop of a machine with nowhere
    for a cable to go demonstrates it.
  palette: "galvanised steel and painted enclosure, chassis grey scale only"
  value_structure: >
    Lightest is the stack's lit left cheek. Darkest is the gap between the stack and the louvre
    bank, which is the deck's void step and is where the hook sits. The louvre fins carry the mid
    range and nothing else does.
    Frame median L* planned at 22.
  motion: "up the stack, then right across the fins and down to the contact"

type:
  hook: "DENIED CONNECTION"
  dek: "The audit names one consequence and calls it denial of connection to the Texas grid. A machine standing on a pad is not asking for one."
  labels: ["c7", "02 / 09"]

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 16 and 28"
  - "the stack turns, lit 0.17,0.61,0.05,0.05 shade 0.29,0.61,0.05,0.05 at 432px"
  - "no wire, cable, conduit, insulator, bushing or transmission structure appears anywhere in the frame"
  - "no amber appears anywhere on this frame, at any coverage"
  - "the louvre fin pitch reads as separable fins at 432px rather than as a flat grey panel"
  - "the words denial of connection to the Texas grid are ATTRIBUTED to the audit rather than said in the deck's own voice, and carry the claim id c7. Quote marks were tried and taken back: they are not how this deck marks borrowed language anywhere else, frame 3 sets its verbatim material as real type on a drawn page, and nested quotes in this file broke its own parse"

risks:
  - "a close crop with no horizon can lose the deck's world entirely, so the pad's caliche and one skid rail must stay in the bottom band"
  - "an absence frame that names no document is exactly what absence_check refuses, so the dek must cite the audit directive and not merely assert the absence"
```

```yaml
slide: 3
layout: DOCUMENT
primary_image:
  subject: "the directive as a single sheet of agency bond lying on a desk at a slight angle, its two governing sentences set as real type in two separate ruled blocks, the rest of the page ruled but empty"
  rect: [176, 448, 740, 740]
  bleeds: []
accent: "#E0A33F"
job: >
  Put the two scopes on one page, in the document's own words, so the reader sees the conflict
  rather than being told about it.

claims: [c1, c3, c11, c4]
numerals:
  - value_from: c4
  - computed_by: "out/2026-09-23/compute.py, clocks.days_halt_to_report from the two quoted dates"

data_in_art:
  figure: clocks.days_halt_to_report
  drives: the count of ruled lines on the drawn page

depth:
  eye: 1.15
  horizon: 700
  cues: [LINEAR_PERSPECTIVE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0.62}

composition:
  structure: >
    The sheet occupies the lower two thirds and runs off the bottom edge, so the reader is over it
    rather than looking at it. The two quoted blocks sit at the page's upper third and its lower
    third with ruled emptiness between them, because the distance between the two sentences on the
    real page is the frame's whole content.
  bands: >
    Top third, the desk surface falling to the deck's dark and the hook. Middle third, the first
    quoted block, applicant scoped. Bottom third, the second quoted block on stock that falls off in tone toward the page's lower edge as the desk drops out of the mast's pool, the sheet's own slight curl catching light along its right margin, and the amber docket line under it.
  
  focal: "the first quoted block, the largest continuous bright area on the sheet and the only place carrying dark type on light stock"

art:
  technique: "a drawn page staged on a desk under the declared light, with its own typography inside it"
  why_this_technique: >
    A claim that is a document's own words wants the document. Setting the two sentences as a list
    on a dark ground would make them the deck's assertion. Setting them on a drawn page under the
    same mast as the yard keeps them what they are, which is something somebody wrote.
  palette: "agency bond and fused toner against the deck's dark desk, with the one amber on the docket line"
  value_structure: >
    Lightest is the sheet itself, held off full white at the chassis bond value because four cream
    sheets at full white made September 18th's canvas mean strobe. Darkest is the desk beyond the
    pool. The light DIMS toward the hook rather than being punched away from it.
    Frame median L* planned at 41.
  motion: "down the sheet from the first block to the second, then right to the amber line"

type:
  hook: "ONE PAGE, TWO SCOPES"
  dek: "One sentence names who is asking. One names an audit a project may never enter."
  labels: ["PERMITS SOUGHT   c1", "ALIGN PERMITTING DECISIONS   c11", "03 / 09"]

verbatim:
  - c1: "all permits sought by data centers"
  - c11: "align its permitting decisions with the Governor's directives and use the information from those audits"

acceptance:
  - "the frame's median L* at 432px is between 35 and 47"
  - "the count of ruled lines on the drawn page equals clocks.days_halt_to_report from figures.json"
  - "the sheet reads as dark type on light stock, and the two quoted blocks are the only type on it"
  - "amber appears only on the docket line and covers under 2 percent of the frame"
  - "no opaque fill over 0.55 alpha sits behind the hook"
  - "the sheet casts a contact shadow running down and to the right onto the desk"
  - "the words all permits sought by data centers appear verbatim and carry c1"

risks:
  - "a document frame is where a plate creeps in, because a critic reading the hook as badly seated asks for a box. The fix is the desk falling darker, never a box"
  - "twenty eight ruled lines at this page size may crowd. The rule pitch is set from the count rather than the count from the pitch, and if it crowds the PAGE grows"
```

```yaml
slide: 4
layout: DIAGRAM
primary_image:
  subject: "two channels drawn as drafted plan sections running left to right across the frame, the upper one the interconnection queue with its shaded share, the lower one the permit counter, with leaders and mono labels landing on each"
  rect: [0, 330, 1080, 780]
  bleeds: [left, right]
accent: "#E0A33F"
job: >
  Show that the two instruments are scoped on different axes, which is the deck's argument, and
  give the reader the size of the queue at the same time.

claims: [c5, c6, c8, c9]
numerals:
  - value_from: c8
  - computed_by: "out/2026-09-23/compute.py, queue.gigawatts and data_center_share.percent, each from c8 and neither multiplied by the other"

data_in_art:
  figure: data_center_share.percent
  drives: the length of the shaded run on the upper channel

depth:
  eye: 1.4
  horizon: 700
  cues: [OCCLUSION, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 6}

composition:
  structure: >
    The two channels are parallel and do not meet, which is the claim. The upper carries a band of
    new requests with ninety percent of its length shaded, the lower carries a counter with no
    band at all, because nothing measures how many permits this reaches and the deck refuses to
    draw one.
  bands: >
    Top third, the hook and the upper channel's label. Middle third, the two channels with their
    leaders. Bottom third, the lower channel's counter drawn as a modeled plan section with its front face lit against its return face in shadow, the queue figure set in mono beside it and the amber counter line.
  
  focal: "the shaded run on the upper channel, a long unbroken bright band and the only shaded area in the frame"

art:
  technique: "drafting, with world-coordinate leaders that terminate on their targets"
  why_this_technique: >
    A mechanism wants a diagram, and this claim is a mechanism. Every other frame in the deck is a
    place, so the one frame that is genuinely about how two rules are worded is the one allowed to
    be a drawing of an idea.
  palette: "drafting ink on the deck's ground, one amber on the counter"
  value_structure: >
    Lightest is the shaded new-requests run. Darkest is the space between the two channels, which
    is the point and is left completely empty. Nothing bridges them.
    Frame median L* planned at 12.
  motion: "left to right along the upper channel, drop to the lower, left to right again"

type:
  hook: "NINETY PERCENT OF THE NEW ONES"
  dek: "The queue holds about 474 gigawatts of requests to connect. The state puts data centers at about ninety percent of the new ones."
  labels: ["474 GW", "90%", "THE WHOLE QUEUE, ON NO SCALE HERE", "NEW POWER REQUESTS", "PERMITS SOUGHT BY DATA CENTERS", "NO COUNT IN THE DIRECTIVE", "04 / 09"]

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 6 and 18"
  - "the shaded fraction of the new-requests band equals data_center_share.percent from figures.json, within 2 percent of the band's drawn length"
  - "nothing is drawn joining the two channels, at any point along them"
  - "the figure 474 appears in mono with a space before GW"
  - "no arrow, funnel, nesting or bracket relates the 474 figure to the ninety percent"
  - "every leader terminates within 24 design px of the coordinates it declares"
  - "amber appears only on the counter line and covers under 3 percent of the frame"

risks:
  - "474 and ninety percent on one frame is exactly the shape that reads as a funnel whatever the structural law says, so they must sit on DIFFERENT channels with nothing between them, and the dek must name the two denominators in two separate sentences"
  - "a diagram is the frame most likely to come out as a plate with words on it, so the channels must carry drawn section detail rather than being two filled rectangles"
```

```yaml
slide: 5
layout: GRID
primary_image:
  subject: "forty reciprocating gas sets drawn as forty separate units at one scale on a ruled pad, one mark per engine, seen from a long lens so near and far read the same size"
  rect: [60, 300, 960, 900]
  bleeds: []
accent: none
job: >
  Make the count countable. This is the frame the deck exists to earn and the only place the
  forty are separable.

claims: [c16, c17, c18]
numerals:
  - value_from: c16
  - value_from: c17
  - computed_by: "out/2026-09-23/compute.py, behind_the_meter.units and behind_the_meter.megawatts, read from c17 and c16 and never divided"

data_in_art:
  figure: behind_the_meter.units
  drives: the mark count

depth:
  eye: 1.4
  horizon: 700
  cues: [RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 16}

composition:
  structure: >
    A long lens at sixteen metres flattens the rows so every unit subtends the same width, which
    is what makes this a count rather than a perspective. Eight columns of five. Each unit casts
    its own short contact down and to the right, so the field is objects on a plane and not a
    pattern.
  bands: >
    Top third, the hook and the megawatt figure in mono. Middle third, the field of forty. Bottom third, the last row of units at full modeling, each enclosure carrying its lit flank against its shade flank, the pad between the rows falling off in tone toward the bottom edge, and the source line over the darkest part of it.
  
  focal: "the field of forty taken as one mass, the largest bright area in the frame, with the reader's eye landing on the top left unit first"

art:
  technique: "isotype at true scale, one mark per unit, one scale only"
  why_this_technique: >
    Neurath's rule is that a greater quantity is more units of the same size and never a bigger
    unit, and this deck's own history says the same thing from the other side. A second scale is
    how you draw a lie without noticing, and a frame that needs two scales is usually a frame
    whose point is not true at one.
  palette: "steel units on caliche, chassis grey scale only"
  value_structure: >
    Lightest is the lit left flank repeated forty times, which is what makes the field read as one
    bright mass at thumb scale. Darkest is the pad between the rows. No unit is picked out and
    none is coloured, because nothing distinguishes one of these engines from another.
    Frame median L* planned at 14.
  motion: "left to right along the top row, then down the field row by row"

type:
  hook: "FORTY, BEHIND THE METER"
  dek: "One West Texas data center has contracted 76 megawatts from about 40 reciprocating gas engines. None of them asks the grid for anything."
  labels: ["76 MW", "c16", "c17", "05 / 09"]

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 8 and 20"
  - "the number of units drawn equals behind_the_meter.units from figures.json exactly"
  - "the field comes apart into at least four separable pieces at 432px"
  - "every unit is drawn at the same width, within 2 design px"
  - "no unit is painted in the accent and no amber appears on this frame"
  - "76 and 40 never appear joined by a division, a per, a slash or an each, in any label or dek"
  - "each unit carries its own contact shadow running down and to the right"

risks:
  - "forty units at one scale can merge into one pale mass at thumb scale, which layout_check measures as a GRID failing to come apart. The pad between rows must stay at the deck's dark, and the row pitch must be read off the render rather than reasoned from the camera"
  - "the word approximately is in the source and the drawing is exact, so the dek must carry about and the frame must not imply a counted inventory"
```

```yaml
slide: 6
layout: FIGURE_SCALE
primary_image:
  subject: "one gas set on its skid at true scale with a person at 1.70 m standing at its radiator end, the stack running up out of the top of the frame, seen from a standing eye"
  rect: [0, 0, 1080, 900]
  bleeds: [top, left, right]
accent: none
job: >
  Give the count a size. Forty of a thing means nothing until the reader knows how big one is and
  that somebody stands next to it.

claims: [c16, c17]
numerals: []

depth:
  eye: 1.65
  horizon: 700
  cues: [RELATIVE_SIZE, LINEAR_PERSPECTIVE, CAST_SHADOW, FORM_SHADING, AERIAL]
  subject_at: {X: 0.5, Z: 9}

composition:
  structure: >
    The set runs the full width and is cropped by both side edges, the person stands at its right
    hand end at nine metres so the enclosure roof sits well above their head, and the stack leaves
    the frame at the top. The reader reads the person first because it is the only thing in the
    deck with a human outline, then reads the machine against it.
  bands: >
    Top third, the stack barrel and the hook in the dark beside it. Middle third, the enclosure
    flank at full detail with the person against it. Bottom third, the skid rail modeled from its lit top edge down to its dark underside, the two casts running down and right, and the pad's texture gradient coarsening toward the reader.
  
  focal: "the person, the smallest object in the frame and the only one the reader's eye is built to find, standing against the enclosure's lit flank"

art:
  technique: "true-scale staging with a figure, on the scene bench under the declared mast"
  why_this_technique: >
    A how big claim wants a figure beside the thing. The doctrine is explicit that a bus is a slab
    because a slab is what you draw when you do not know how tall a bus is, and the cure is a
    person at a known height in the same camera.
  palette: "steel, caliche and one worker in work clothes, chassis grey scale only"
  value_structure: >
    Lightest is the enclosure's lit left flank. Darkest is the underside of the skid and the pad
    beyond the pool. The person is given a grey distinct from the enclosure behind them, because
    figures at the same tone as the object beside them merge into one pale shape.
    Frame median L* planned at 20.
  motion: "to the person first, up the enclosure, up the stack and out"

type:
  hook: "THIS IS ONE OF THEM"
  dek: "A single set on its skid, and somebody who works on it."
  labels: ["06 / 09"]

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 14 and 26"
  - "the person is drawn at 1.70 m through the same camera as the enclosure"
  - "the person's grey differs from the enclosure behind them by at least 10 L* at 432px"
  - "the enclosure turns, lit 0.100,0.500,0.035,0.035 shade 0.748,0.500,0.035,0.035 at 432px"
  - "the person and the enclosure each cast onto the pad, both running down and to the right"
  - "no amber appears anywhere on this frame, at any coverage"
  - "no glyph appears on the enclosure, the skid or the stack"

risks:
  - "an object taller than the eye projects above the horizon and the type lives up there. The enclosure at 3.0 m against a 1.65 m eye is checked before the hook is placed"
  - "a figure at nine metres is small enough to be lost in the screen, so the figure's own silhouette is drawn clear of the louvre bank rather than in front of it"
```

```yaml
slide: 7
layout: SPLIT_HORIZON
primary_image:
  subject: "a single straight horizontal cut across the frame, the pad and the yard's far fence below it, and above it a measured rule carrying two runs of tick marks, forty nine and twenty eight, at one pitch"
  rect: [0, 700, 1080, 650]
  bleeds: [left, right, bottom]
accent: "#E0A33F"
job: >
  Give the argument a clock. Two spans at one pitch, so the reader sees that the halt came late and
  the answer comes soon.

claims: [c9, c4]
numerals:
  - computed_by: "out/2026-09-23/compute.py, clocks.days_audit_to_halt and clocks.days_halt_to_report, both calendar differences between dates read out of the quotes"

data_in_art:
  figure: clocks.days_audit_to_halt
  drives: the tick count in the first run

depth:
  eye: 1.65
  horizon: 700
  cues: [LINEAR_PERSPECTIVE, AERIAL, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 40}

composition:
  structure: >
    The horizon is the cut and it sits at the deck's own held horizon of 700, which is the one
    frame where the deck's camera height becomes the composition. Below it the pad recedes to the
    fence. Above it the rule runs left to right with its two runs of ticks, so the sky carries the
    measurement and the ground carries the place.
  bands: >
    Top third, the hook. Middle third, the rule and its two tick runs, with the amber mark at the
    report back. Bottom third, the pad receding to the yard's far fence with its texture gradient tightening with distance, the fence posts modeled one by one with a lit left face against a dark right face, and the ground beyond the last post falling to the deck's own dark where the mast's pool runs out. The source line sits over the darkest part of that falloff.
  
  focal: "the amber tick at the report back, the only chromatic mark on the frame and the one place the run of identical ticks breaks"

art:
  technique: "a measured rule at one pitch, over a staged ground"
  why_this_technique: >
    A claim about a quantity over time does not become one by being drawn on a map. Two spans at
    one pitch is the only drawing where a reader can see that forty nine is longer than twenty
    eight without being told, and the pitch being identical is the whole reason the comparison is
    honest.
  palette: "drafting ink over caliche and fence, one amber on the report back"
  value_structure: >
    Lightest is the run of ticks on the dark sky. Darkest is the ground beyond the fence where the
    mast's pool has run out. The horizon cut is the frame's one hard edge.
    Frame median L* planned at 13.
  motion: "left to right along the rule, stopping at the amber"

type:
  hook: "FORTY NINE DAYS, THEN TWENTY EIGHT"
  dek: "The audit was ordered August 3rd. The directive came 49 days later. The agency answers to the Governor's office 28 days after that."
  labels: ["AUGUST 3RD", "SEPTEMBER 21ST", "OCTOBER 19TH", "c9", "c4", "07 / 09"]

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 7 and 19"
  - "the tick count in the first run equals clocks.days_audit_to_halt from figures.json exactly"
  - "the tick count in the second run equals clocks.days_halt_to_report from figures.json exactly"
  - "both runs are drawn at the same pitch, within 1 design px"
  - "the horizon is a single straight cut and the ground below it occupies at least 0.40 of the frame height"
  - "amber appears only on the report back tick and covers under 1 percent of the frame"
  - "no numeral on this frame is absent from figures.json"

risks:
  - "forty nine ticks at a legible pitch is a long rule, and if it does not fit the frame the answer is a shorter tick rather than a second pitch, because two pitches would make the comparison a lie"
  - "a split horizon with an empty sky is the frame most likely to read as a chart on a background, so the ground half must carry the fence, the pad texture gradient and real aerial falloff"
```

```yaml
slide: 8
layout: MAP
primary_image:
  subject: "the Texas outline in the site's own Albers projection, dark, with two places marked, and at Odessa a pair of drawn bars at one scale giving the neighbouring plant against the slice contracted from it"
  rect: [70, 290, 940, 880]
  bleeds: []
accent: none
job: >
  Kill the reading the deck would otherwise invite, which is that contracting next door is the
  same as leaving the grid. It is not, and this is the frame that says so.

claims: [c19, c20, c21]
numerals:
  - value_from: c19
  - value_from: c20
  - computed_by: "out/2026-09-23/compute.py, adjacent_plant.plant_mw and adjacent_plant.phase1_max_mw, each read from its own quote"

data_in_art:
  figure: adjacent_plant.plant_mw
  drives: the length of the plant bar, with the contracted bar at the same scale

depth:
  eye: 1.4
  horizon: 700
  cues: [OCCLUSION, RELATIVE_SIZE, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 30}

composition:
  structure: >
    The state sits centred and low with ONE mark, Odessa west. The bars sit beside it rather than
    on it, at one scale, one above the other.
    THIS BLOCK PROMISED TWO MARKS AND THE FRAME WAS NEVER BUILT WITH TWO. It read "the two marks
    well apart, Odessa west and the Bexar County mark south east", while the acceptance list six
    lines down asks for one mark and the render has one. A round 4 scorer found the plan
    contradicting itself AND the render inside a single block, which is the more useful half of
    the finding: a plan that disagrees with itself cannot be used to judge anything.
    The plan is what was wrong. Frame 8's whole subject is the Odessa power purchase as the
    counter example to behind the meter supply, and a second mark for a canceled Bexar hearing
    would put two unrelated stories on one map and split a frame whose argument is a ratio
    between two lengths. Bexar is frame 9's, where it is the room the reader is standing in.
  bands: >
    Top third, the hook. Middle third, the state outline with the Odessa mark. Bottom third, the two bars modeled with a lit top edge over a shaded body so they read as drawn objects standing on the map rather than as filled rectangles, their mono figures beside them and the source line.
  
  focal: "the longer bar, the single longest continuous bright run in the frame, with the short bar directly under it for the comparison"

art:
  technique: "cartography through TXGeo, the same Albers the site's map builder uses, with a measured bar pair"
  why_this_technique: >
    A where claim wants a map, and this frame has two wheres that are four hundred miles apart.
    Drawing the bar pair at the Odessa mark is what ties the quantity to the place, which a
    separate chart frame could not do.
  palette: "the deck's ground for the state's interior, steel for the coast and border, no accent"
  value_structure: >
    Lightest is the longer bar. The state's interior is INKED rather than left as the ground, and
    this sentence used to say it was the frame's darkest region, four lines above the number that
    refutes it. Filled at the deck's ground the interior was not ink at all and the subject
    measured 0.30 of its largest piece against a floor of 0.50, so it had to become a mass, and a
    mass is lighter than the ground by definition. It is darker than the bars and darker than the
    outline, and that is the rank the frame needs, so the outline still reads as a drawn edge
    rather than as a filled shape. The Odessa mark is the only point
    of full brightness besides the bars.
    MEASURED RATHER THAN ASSERTED, because a round 4 scorer read this interior as among the
    brightest areas in the frame and the measurement does not support that. Off the 432px render
    the state interior sits at median L* 15.6 against a frame median of 11.8, so it is four L*
    above the frame and not among the brightest; the long bar reaches p90 76.5 and is the
    lightest thing here, exactly as this block says. The interior was already moved from `dark`
    to `deep` once for this reason and the source comment records it.
    Frame median L* planned at 12.
  motion: "to the state, out to the Odessa mark, down to the bars"

type:
  hook: "NEXT DOOR SAYS NOTHING ABOUT THE METER"
  dek: "An Odessa project contracts up to 207 megawatts from a 1,180 megawatt plant immediately adjacent to it. Adjacent is a statement about distance. The record does not say where the meter sits."
  labels: ["1,180 MW", "207 MW", "ODESSA", "c20", "c21", "08 / 09"]

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 6 and 18"
  - "the two bars are drawn at one scale and their lengths are in the ratio adjacent_plant.plant_mw to adjacent_plant.phase1_max_mw from figures.json, within 2 design px"
  - "the Texas outline is neither mirrored nor inverted, checked against TXGeo"
  - "the Odessa mark is drawn, is the only place mark on the frame, and is on land"
  - "no amber appears anywhere on this frame, at any coverage"
  - "the frame nowhere draws the Odessa contract as leaving the grid, and carries no meter, no break and no disconnect symbol"
  - "76 does not appear on this frame, in any label, figure or dek"

risks:
  - "putting the behind the meter figure and the adjacent plant figures on one frame would join two arrangements the record keeps apart, so 76 is forbidden here by acceptance rather than by intention"
  - "a bar pair on a map is two visual systems at once and can read as a chart pasted on cartography. The bars sit inside the state's own bounding box and share the map's ink so they read as annotation"
```

```yaml
slide: 9
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "an empty hearing room at night, chairs still stacked against the wall, one amber notice taped to the inside of the door, and through the window a single stack of the yard lit by its mast at the far end of the lot"
  rect: [0, 320, 1080, 1030]
  bleeds: [left, right, bottom]
accent: "#E0A33F"
job: >
  Land on the public's own door rather than on the state's. The deck's last fact is that the room
  where a Texan could have spoken about a data center permit was already dark before any of this.

claims: [c12, c13, c4]
numerals: []

depth:
  eye: 1.15
  horizon: 700
  cues: [LINEAR_PERSPECTIVE, OCCLUSION, CAST_SHADOW, FORM_SHADING]
  subject_at: {X: 0, Z: 4.5}

composition:
  structure: >
    A seated eye, because this is a room somebody sits in. The stacked chairs run along the left
    wall into the corner, the door with its notice is right of centre, and the window is beyond it
    carrying the one piece of the yard the reader has been in for eight frames. The room is lit
    only by what comes through that window, so the mast is still the deck's one light.
  bands: >
    Top third, the ceiling falling to the deck's dark and the hook. Middle third, the door, the
    amber notice and the window with the stack in it. Bottom third, the floor taking the window's light in a modeled falloff from the sill toward the reader, and the stacked chairs carrying lit top rails against shadowed frames where they lean on the wall.
  
  focal: "the amber notice on the door, the only chromatic area in the frame and the brightest thing in a dark room"

art:
  technique: "an interior staged on the bench, lit through one opening by the deck's declared mast"
  why_this_technique: >
    The deck has spent eight frames outdoors and the argument ends indoors, with a person's right
    to speak rather than with a machine. Carrying the same light through a window is what makes
    the last frame belong to the same night as the first.
  palette: "institutional wall and floor, stacked steel chairs, one amber notice"
  value_structure: >
    Lightest is the amber notice, then the window. Darkest is the ceiling and the far corner,
    which is most of the frame and is why this is the deck's floor. The value arc ends here on
    purpose.
    Frame median L* planned at 14.
  motion: "to the notice, out through the window to the stack, back to the closing line"

type:
  hook: "THE ROOM WAS ALREADY EMPTY"
  dek: "The state canceled the notice and comment hearing on Bexar County data center permit O4791, captioned to Vantage Data Centers TX11. It says the hearing will be rescheduled for a later date and gives no date."
  labels: ["c12", "c13", "c4", "NO DATE YET FOR THE HEARING. TCEQ ANSWERS TO THE GOVERNOR'S OFFICE BY OCTOBER 19TH.", "texasaidocket.com", "09 / 09"]

verbatim:
  - c13: "The hearing will be rescheduled for a later date."

acceptance:
  - "the frame's median L* at 432px is 20 or lower"
  - "the sentence The hearing will be rescheduled for a later date appears verbatim and carries c13"
  - "amber appears only on the notice and covers between 0.2 and 4 percent of the frame"
  - "the window carries exactly one stack and no other part of the yard"
  - "the chairs are stacked and no chair is drawn set out for an audience"
  - "no person is drawn in this room"
  - "the room's light enters through the window only, and every cast in the room runs from it"
  - "the frame nowhere says the permit was refused, withdrawn or denied"

risks:
  - "an empty room is the easiest frame in any deck to draw as an empty rectangle, so the stacked chairs must carry real form shading and the floor must carry the light's falloff from the window"
  - "drawing a person here would invent an attendance nobody recorded, and drawing chairs set out would imply a hearing that did not happen"
```
