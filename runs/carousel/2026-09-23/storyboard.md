# Storyboard — carousel no. 32, 2026-09-23
# "SOUGHT BY", rebuilt as a render

## Why this storyboard was rewritten on the day it shipped

The first build of this deck pushed all nine frames through a line screen at cell 6. That is the
print register, the faded look the owner had already rejected on the decks of September 20th and
21st, and it came back because the routine, the treatment director and the reference example all
still ORDERED it. The owner, on seeing it: *"delete that fallback bullshit look, make it impossible
for me to have to tell u this again."* The screen module, its example deck and every instruction
to print are deleted, `print_ban.py` refuses any of them returning, and this deck is RENDERED
through `txthree.js`: one hero object modelled once in metres, a physically based material, one
light, soft shadow on a ground it stands on, fog in the horizon's own hue.

The claims changed underneath it too. Twelve claims were first fetched from `gov.texas.gov`, whose
robots file refuses this fetcher. Eight were re-sourced from hosts that permit it (Troutman
Pepper's client alert, the Texas Tribune and CBS Texas), c8 and c23 were split out of one Tribune
paragraph, and four were dropped. **The Odessa frame went with them**, because c19 to c21 had no
permitted source, and frame 8 is now the agency's own engine permitting page, c15, which this run
fetched from `tceq.texas.gov` under a permitting robots file.

## What the fact check did to this deck

The spine was once that the air permit follows the ENGINES rather than the grid connection, so
the September 21st halt reaches projects the August 3rd audit cannot. **That mechanism is not
established and is not asserted.** c14 and c15 say only that the agency publishes NSR guidance and an engine permitting overview, and **c14's `typically` is never spent as `must`.** Frame 8 says the page
exists and that nothing verified says whether these forty need one.

What the deck does assert, set side by side on frame 3 and labelled by source:

    THE GOVERNOR, AS CBS QUOTED IT   "complete the ERCOT and TWDB audits. Until they do, TCEQ
                                     will issue no permits sought by data center projects."   c3
    THE ERCOT AUDIT, AS THE TRIBUNE  "all data centers advancing through ERCOT's
    REPORTED IT                      interconnection queue"                                 c5

The halt reaches permits sought by data center projects. It waits on two audits. The record
states the ERCOT audit's scope and states nothing about the water board's. The deck decides
nothing between the two readings.

**THE DECK NEVER SAYS THE AGENCY HAS HALTED ANYTHING.** It is a directive, nothing verified says
a permit has been refused, and every string says the Governor directed. The text sets a date for a
report back, October 19th.

## The world, and the laws that hold it

**A GAS GENERATION YARD ON A CALICHE PAD AT NIGHT.** The chassis is
`assets/js/deck/2026-09-23-gensetyard.js` and every frame loads it.

**ONE HERO OBJECT.** A containerised reciprocating gas generator set on its skid, modelled once in
metres: a 12.2 m enclosure, 2.9 m of box on a 0.44 m skid and slab, a louvred radiator end, a
roof cooler, a silencer and a 3.2 m exhaust stack, four access doors. Every frame shows that one
machine from a new camera or in a new state, or forty of it. No per unit rating anywhere, because
76 over about 40 is a division no document performs, and nothing about the model's size claims
an output.

**ONE LIGHT.** `TXDECK.declare` holds it at azimuth -105 and elevation 27: low, from the pad's
west and slightly behind. `TXT.deckRig` reads it on every frame, so nine cameras see one lamp by
construction and no frame can carry a second copy. Every radiator or plain end facing west is
lit, every door side facing south is in shade, every cast runs east.

**THE ACCENT LAW. AMBER IS THE STATE'S PAPER. STEEL IS THE MACHINERY. THEY NEVER TOUCH.**
`#E0A33F` lands on the directive's rule (3), the Governor's share (4), the twenty eight days the
agency has to answer (7) and the cancellation on the hearing table (9). Paper amber is unlit and
outside the tone map, `YARD.paperMat`, because a printed colour does not turn orange under a
lamp and the accent has to read as one colour across four frames. It never touches a set, a stack, a skid or
the pad.

**THE MUTE WORLD LAW.** Paper is the only thing that carries glyphs. No maker's plate, no unit
number, no sign at the gate, so no drawn yard can be read as one real facility, which matters
because no source gives a site plan for the project in c16.

## Palette

| token | hex | where |
|---|---|---|
| `night` | `#0D1117` | the ground of every frame, and the DOM body behind the render |
| `amber` | `#E0A33F` | the state's paper, frames 3, 4, 7 and 9 only |

The machine's own colours live in the chassis as material values and are lit, so no frame
carries them as flat hex, and the palette names only what a frame declares as a token.

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE, VALUE_ARC

1. **Motif evolution.** The same set is the line (1), the machine close (2), the yard behind the
   notice (3), forty in a block (5), one beside a person (6), the object on the pad beside the
   days (7) and the stacks (8). A reader recognises a thing before a surface.
2. **Camera move.** Down the line (1), in to its end (2), round to the notice (3), up over the pad
   (4, 5, 7), down to a person's eye (6), to the ground under the stacks (8), then indoors (9).
3. **Value arc.** Measured on the probe render, every frame's median sits between 7 and 9 L*, so
   the deck never strobes. No value cut is declared because none is taken.

## The rotation

    FULL_BLEED  CLOSE_CROP  DOCUMENT  DIAGRAM  GRID  FIGURE_SCALE  DIAGRAM  FULL_BLEED  OBJECT_AND_CAPTION

No repeat in a row, seven distinct, no TYPE_AS_OBJECT, FULL_BLEED and CLOSE_CROP three between
them, seven frames bleeding an edge against a floor of four.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "a line of forty containerised gas generator sets on a caliche pad at night, seen from off its near end, the nearest sets lit on their west ends and the line running into fog at a vanishing point left of centre"
  rect: [0, 560, 1080, 560]
  bleeds: [left, right]
accent: none
job: >
  Put the reader on the pad before a word of policy, so the thing being argued about is a
  machine they have seen the size of rather than a category.

claims: [c1, c16, c17]
numerals: []

data_in_art:
  figure: behind_the_meter.units
  drives: the count of sets built in the receding line

depth:
  eye: 2.1
  horizon: 990
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, OCCLUSION, CAST_SHADOW, FORM_SHADING]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The line runs from the lower right corner to a vanishing point left of centre, so the reader
    enters at the nearest set and is carried into the dark. The type sits in the sky above the
    stacks, which stop under the dek by the camera's pitch rather than by a plate.
  bands: >
    Top third, the night sky, the hook and the dek. Middle third, the stack tops and the far end
    of the line dissolving into fog at the horizon. Bottom third, the near sets at full modeling,
    each lit west end turning to a shaded door side, over a caliche pad whose grain tightens
    toward the horizon and darkens toward the bottom edge.
  focal: "the lit west end of the nearest set, the largest bright area and the only place at full detail"

art:
  technique: "physically based render through txthree.js, forty instances of the chassis hero under the deck light, fog in the horizon hue"
  why_this_technique: >
    The claim is a count of machines that are physically somewhere. A field or a gradient would
    say the same thing about any count. Forty objects through one camera is what makes the far
    end of the line unreadable, and the unreadable far end is the point of the frame.
  palette: "night ground, painted steel and galvanised stacks lit by the deck's one lamp, no amber"
  value_structure: >
    Lightest is the run of lit west ends down the line. Darkest is the sky at the top, where the
    type sits. The line falls into the fog toward its vanishing point, so distance reads as
    atmosphere rather than as a cut.
  motion: "lower right to the vanishing point, then up the near stacks into the type"

type:
  hook: "Sought by"
  dek: "Two words decide who a permit halt reaches."

verbatim: []

acceptance:
  - "the frame reads \"Sought by\" and \"Two words decide who a permit halt reaches.\""
  - "the number of sets built in the line equals behind_the_meter.units from figures.json, 40"
  - "no amber #E0A33F appears anywhere on the frame"
  - "no stack top crosses the hook or the dek"
  - "the far end of the line meets the horizon in fog rather than stopping"

risks:
  - "forty sets at a 4.6 m pitch read as a wall rather than a count at thumb size. Frame 5 is where the count is made countable, so the near six stay at full detail here"
```

```yaml
slide: 2
layout: CLOSE_CROP
primary_image:
  subject: "the hero set's louvred radiator end and roof cooler at detail scale from low off its corner, the stack rising behind, the next set dark at the left, with no wire, conduit or insulator anywhere"
  rect: [280, 80, 540, 840]
  bleeds: []
accent: none
job: >
  Put the stated consequence, denial of interconnection, beside the machine at detail scale. The
  frame asserts nothing about whether this project asks for a connection.

claims: [c10, c5]
numerals: []

depth:
  eye: 0.9
  horizon: 860
  cues: [LINEAR_PERSPECTIVE, FORM_SHADING, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: -6.1, Z: 0}

composition:
  structure: >
    The louvred end fills the top two thirds square to the reader, the door side runs off the
    right edge in shade, and the next set holds the left edge. 
  bands: >
    Top third, the roof cooler and the lit frame of the end, with the stack rising behind it.
    Middle third, the fourteen raked louvres at their densest. Bottom third, the skid and slab
    lit along their west edges, the contact shadow under the slab, and the caliche pad in front
    holding the hook and the dek.
  focal: "the lit frame of the radiator end around the dark louvre bank, the brightest shape in the frame"

art:
  technique: "physically based close render of the chassis hero turned half a turn so its radiator end takes the deck light"
  why_this_technique: >
    The stated consequence is about a grid connection, so the frame shows the machine the story
    is about at detail scale and asserts nothing about its connection.
  palette: "night ground, painted steel, dark louvres, no amber"
  value_structure: >
    Lightest is the lit frame of the radiator end. Darkest is the louvre recess and the pad under
    the type. The door side carries the mid tones in shade.
  motion: "down the louvres to the slab, then across to the type"

type:
  hook: "A connection to deny"
  dek: "A project that fails to complete the ERCOT audit is to be denied interconnection. That audit covers data centers in the interconnection queue."

verbatim: []

acceptance:
  - "the frame reads \"A connection to deny\""
  - "no wire, cable, conduit, insulator or pole appears anywhere on the frame"
  - "the set's slab sits above the hook, so no part of the machine crosses a letterform"
  - "no amber #E0A33F appears anywhere on the frame"

risks:
  - "a louvre bank at night can read as a black rectangle. The fourteen slats are raked so each catches the key on its upper edge"
```

```yaml
slide: 3
layout: DOCUMENT
primary_image:
  subject: "a posted notice on a single post at the edge of the pad, turned into the deck's light, the directive's two sentences on the page, the yard in the fog behind it"
  rect: [0, 400, 1080, 950]
  bleeds: [left, right, bottom]
accent: "#E0A33F"
job: >
  Show the two scopes of the directive side by side, so the reader reads the
  sentences themselves rather than a paraphrase of them.

claims: [c3, c5]
numerals: []

depth:
  eye: 1.45
  horizon: 760
  cues: [AERIAL, OCCLUSION, CAST_SHADOW, HEIGHT_IN_FIELD, FORM_SHADING]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The board stands square to the reader in the centre with its page lit by the deck's lamp,
    because a page under a lamp is the only lit sheet in a yard at night. Its type is projected
    onto the page's rect through the camera, so the words sit on the paper rather than beside it.
  bands: >
    Top third, the sky, the hook and the dek over the board's top edge. Middle third, the page
    with its amber rule and the first sentence, the yard's sets in the fog either side. Bottom
    third, the second sentence at the foot of the page, the dark board frame, and the post
    running down to its cast shadow on the lit caliche pad.
  focal: "the lit page and its amber rule, the brightest surface in the deck"

art:
  technique: "physically based render of a notice board and page turned to face the deck light, with the page's type projected onto it through the frame's camera"
  why_this_technique: >
    The claim is two sentences about one directive, from two reports of it. Drawing the page as a thing that stands in the yard
    makes it the state's paper in the machine's world, and projecting the type onto it keeps the
    words vector and legible.
  palette: "night ground, paper white, the board's dark stain, the amber rule"
  value_structure: >
    Lightest is the page. Darkest is the sky above the board where the hook sits. The yard behind
    sits in the fog at the mid tones.
  motion: "down the page from the amber rule through the two sentences"

type:
  hook: "Two scopes"
  dek: "The halt reaches permits sought by data center projects. The ERCOT audit it waits on reaches the interconnection queue."

verbatim:
  - quote: "complete the ERCOT and TWDB audits. Until they do, TCEQ will issue no permits sought by data center projects."
    claim: c3
  - quote: "all data centers advancing through ERCOT's interconnection queue"
    claim: c5

acceptance:
  - "the frame reads \"Until they do, TCEQ will issue no permits sought by data center projects.\""
  - "the frame reads \"all data centers advancing through ERCOT's interconnection queue\""
  - "both quoted sentences sit inside the drawn page's rect"
  - "the amber rule across the page head is the only amber on the frame"
  - "the post leaves the bottom edge between the source line and the site line, crossing neither"

risks:
  - "a lit page in a dark frame can burn out. The paper is off white and the bloom threshold on this frame is raised"
```

```yaml
slide: 4
layout: DIAGRAM
primary_image:
  subject: "one hundred steel plates laid ten by ten on the pad under a parallel camera, ninety of them painted amber and ten left steel along the far row"
  rect: [120, 420, 960, 600]
  bleeds: []
accent: "#E0A33F"
job: >
  Make the Governor's share a fill level the reader can see, and keep the queue's gigawatts on
  no scale beside it, because they are two denominators.

claims: [c8, c23]
numerals:
  - value_from: c8
  - value_from: c23

data_in_art:
  figure: data_center_share.percent
  drives: the count of plates painted amber

depth:
  eye: 26
  horizon: 0
  cues: [FORM_SHADING, CAST_SHADOW, HEIGHT_IN_FIELD, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A parallel camera, because perspective would shrink the far rows and a reader would read the
    shrink as a smaller share. The plates fill row by row from the near edge so the ten steel
    plates are the far row and the share reads as a level, and the two figures sit in the pad's
    open corners either side of the field.
  bands: >
    Top third, the hook and the dek. Middle third, the plate field from its far steel row to its
    middle, each plate a raised block casting east. Bottom third, the near amber rows at full
    modeling on the caliche, the 474 GW figure at the left and the 90% figure at the right.
  focal: "the ten steel plates of the far row against the ninety amber, the only break in the field"

art:
  technique: "parallel projection render of one hundred plates on the pad under the deck light"
  why_this_technique: >
    A share of one hundred is exactly one hundred things, and plates on the same pad the machines
    stand on keep the diagram in the deck's world rather than on a chart.
  palette: "night ground, amber for the share, steel for the rest"
  value_structure: >
    Lightest are the lit tops of the amber plates. Darkest is the pad around the field and the
    sky band under the type. The steel plates sit a step below the amber.
  motion: "down the field from the steel row to the figures"

type:
  hook: "Ninety percent of the new ones"
  dek: "ERCOT counts more than 474 gigawatts of requests to connect. The Governor puts data centers at about ninety percent of the new ones."

verbatim: []

acceptance:
  - "exactly ninety plates are amber and ten are steel, one hundred in all"
  - "the frame reads \"90%\" and \"474 GW\""
  - "the frame reads \"on no scale here\" beside the 474 GW figure"
  - "no plate crosses the dek"

risks:
  - "ninety amber plates is a lot of accent. It is the frame where the state's number IS the subject, and every other frame holds amber to one small sheet"
```

```yaml
slide: 5
layout: GRID
primary_image:
  subject: "forty generator sets in four columns of ten on the pad under a parallel camera from high off their lit ends, each a box with a lit end, a door side and a stack"
  rect: [40, 480, 1000, 640]
  bleeds: []
accent: none
job: >
  Make the forty countable, and put the 76 megawatts beside a physical quantity of machines the
  supplier calls behind-the-meter capacity.

claims: [c16, c17, c18]
numerals:
  - value_from: c16
  - value_from: c17

data_in_art:
  figure: behind_the_meter.units
  drives: the count of sets in the grid

depth:
  eye: 40
  horizon: 0
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION, HEIGHT_IN_FIELD]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A parallel camera again, because a count must not shrink with distance. Four columns of ten
    run diagonally down the frame so each set reads as a whole box with its stack, and the block
    sits clear of every edge so the count can be performed.
  bands: >
    Top third, the hook and the dek over the far corner of the block. Middle third, the body of
    the block, rows of lit west ends and shaded door sides with stacks casting east. Bottom
    third, the near corner of the block over the lit caliche pad, and the 76 MW label.
  focal: "the near corner of the block, where the sets are largest and the stacks read"

art:
  technique: "parallel projection render of forty instances of the chassis hero in a grid"
  why_this_technique: >
    Approximately 40 is the claim's own number and the frame builds exactly that many, so a
    reader who counts gets the source's figure and nothing else.
  palette: "night ground, painted steel, galvanised stacks, no amber"
  value_structure: >
    Lightest are the forty lit ends. Darkest are the shaded gaps between rows. The pad sits in
    the mid dark.
  motion: "down the columns from the far corner to the label"

type:
  hook: "About forty, behind the meter"
  dek: "A gas compression company says it will supply one data center with 76 megawatts of behind-the-meter capacity from about 40 reciprocating gas engines."

verbatim: []

acceptance:
  - "the grid holds exactly forty sets, behind_the_meter.units from figures.json"
  - "the frame reads \"76 MW, behind the meter\""
  - "no set crosses the dek"
  - "no amber #E0A33F appears anywhere on the frame"

risks:
  - "from high up forty boxes can read as a textile. The camera is oblique enough that each shows a stack"
```

```yaml
slide: 6
layout: FIGURE_SCALE
primary_image:
  subject: "the hero set whole from off its lit end at a standing eye, a person in coveralls and a hard hat beside it, and the rest of the line behind it going into the fog"
  rect: [0, 80, 1080, 780]
  bleeds: [left, right]
accent: none
job: >
  Give the machine a size a reader already owns, by standing a person next to it.

claims: [c16, c17]
numerals: []

data_in_art:
  figure: behind_the_meter.units
  drives: the count of sets, one in front and the rest behind in the line

depth:
  eye: 2.4
  horizon: 760
  cues: [RELATIVE_SIZE, LINEAR_PERSPECTIVE, AERIAL, OCCLUSION, CAST_SHADOW, FORM_SHADING]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The hero stands across the right of the frame with its lit west end turned to the reader and
    the person a step off that end, so the two heights compare against one edge. The line runs
    away to the left into fog, and the pad below holds the type.
  bands: >
    Top third, the stacks of the hero and the next sets rising off the top edge. Middle third,
    the lit west end of the hero, the person against it, and the line receding left. Bottom
    third, the slab and skid, the person's feet and cast shadow on the lit caliche, and the
    hook and dek on the pad.
  focal: "the person against the lit end of the hero, the one human shape in the deck"

art:
  technique: "physically based render of the chassis hero with a modelled person under the deck light"
  why_this_technique: >
    Scale is the claim, and scale needs a body. A person modelled in the same world under the
    same light is the one measure every reader carries.
  palette: "night ground, painted steel, dark coveralls, a white hard hat, no amber"
  value_structure: >
    Lightest is the hero's lit end. Darkest is the pad under the type. The person reads as a dark
    figure against the light end.
  motion: "from the person up the lit end, then along the line into the fog"

type:
  hook: "A set like these"
  dek: "A generator set drawn on its skid, with a person beside it. Its size is drawn to illustrate, not taken from a claim."

verbatim: []

acceptance:
  - "a person with a head, a body and two legs stands beside the hero, readable at 432 px"
  - "the frame reads \"A set like these\""
  - "the line behind the hero holds the rest of behind_the_meter.units"
  - "no amber #E0A33F appears anywhere on the frame"

risks:
  - "the person is made of capsules and can read as a toy. It is small in the frame on purpose, as a person beside a 12 m machine is"
```

```yaml
slide: 7
layout: DIAGRAM
primary_image:
  subject: "two runs of standing day plates on steel rails on one concrete slab at one pitch under a parallel camera, forty nine above in steel and twenty eight below in amber, the hero set on the pad in front"
  rect: [80, 540, 920, 640]
  bleeds: []
accent: "#E0A33F"
job: >
  Put the directive's two waits side by side as lengths, so a reader sees the report back comes
  sooner than the directive did.

claims: [c9, c24, c4]
numerals:
  - computed_by: "out/2026-09-23/compute.py, clocks.days_audit_to_halt"
  - computed_by: "out/2026-09-23/compute.py, clocks.days_halt_to_report"

data_in_art:
  figure: clocks.days_audit_to_halt
  drives: the count of day plates in the first run, with the second run's count from clocks.days_halt_to_report

depth:
  eye: 20
  horizon: 0
  cues: [FORM_SHADING, CAST_SHADOW, HEIGHT_IN_FIELD, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    One pitch for both runs and both left aligned, so the comparison is a length and nothing
    else. The runs stand facing the lamp so every day is a separate lit plate, and the hero sits
    on the pad below them as the thing the days are about.
  bands: >
    Top third, the hook and the dek. Middle third, the forty nine plate run with its two dates and
    the twenty eight plate run ending in the amber plate. Bottom third, the hero set on the pad
    at full modeling, its lit door side and stack, casting east across the caliche.
  focal: "the amber second run ending short of the first, the one accent"

art:
  technique: "parallel projection render of standing day plates and the chassis hero under the deck light"
  why_this_technique: >
    Days are countable things. Standing each one up as a plate that catches the lamp makes the
    count physical, and a parallel camera keeps the two runs honest as lengths.
  palette: "night ground, pale steel for the first run, amber for the second, which is the state's clock"
  value_structure: >
    Lightest is the first run's lit faces. Darkest is the pad between the runs. The second run is
    the accent, so the two read as two periods and the second as the state's.
  motion: "left to right along the first run, back and along the second to the amber plate"

type:
  hook: "Forty nine days, then twenty eight"
  dek: "The audit was ordered August 3rd. The directive came 49 days later. The agency must answer to the Governor's office by October 19th, 28 days later."

verbatim: []

acceptance:
  - "the first run holds exactly 49 plates and the second exactly 28, at one pitch"
  - "the second run is amber and the first is steel, and nothing else on the frame is amber"
  - "the frame reads \"August 3rd\", \"September 21st\" and \"By October 19th\""
  - "no plate or label crosses the dek"

risks:
  - "seventy seven plates can read as a barcode. They stand 2 m tall so each catches its own light"
```

```yaml
slide: 8
layout: FULL_BLEED
primary_image:
  subject: "the galvanised exhaust stacks of the line from a worm's eye on the pad beside the first set, the nearest stack towering at the right and the rest marching away down and to the left into the fog"
  rect: [120, 320, 960, 760]
  bleeds: [right]
accent: none
job: >
  Show the part of the machine an air permit is about, and say only what the record says about
  whether these need one.

claims: [c15, c17]
numerals: []

data_in_art:
  figure: behind_the_meter.units
  drives: the count of stacks in the receding line

depth:
  eye: 0.35
  horizon: 990
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    From the ground the stacks become the subject rather than the boxes. The nearest towers at
    the right edge and the line falls away down and to the left, so the empty sky in the upper
    left holds the type without a plate.
  bands: >
    Top third, the hook in the sky and the nearest stack rising to the top right. Middle third,
    the dek, and the line of stacks falling away left into the fog. Bottom third, the lit west
    ends of the nearest sets, their slabs, and the caliche pad running to the horizon.
  focal: "the nearest galvanised stack catching the lamp against the night sky"

art:
  technique: "physically based worm's eye render of the chassis hero line"
  why_this_technique: >
    The page c15 names is about engine operations, and the stack is the one part of an engine a
    reader associates with an air permit. Looking up at forty of them makes that part the subject.
  palette: "night ground, galvanised stacks, painted steel, no amber"
  value_structure: >
    Lightest are the lit sides of the stacks and the west ends. Darkest is the sky at the upper
    left where the type sits. The far line sits in the fog.
  motion: "down the line of stacks from the right edge to the fog at the left"

type:
  hook: "Engines have a page of their own"
  dek: "The agency publishes an \"Overview of air permitting requirements and options for new internal combustion engine operations.\" Nothing verified says whether these engines need an air permit."

verbatim:
  - quote: "Overview of air permitting requirements and options for new internal combustion engine operations."
    claim: c15

acceptance:
  - "the frame reads \"Engines have a page of their own\""
  - "the frame never says the engines need a permit, only that the page exists"
  - "the line holds behind_the_meter.units sets"
  - "no amber #E0A33F appears anywhere on the frame"

risks:
  - "a second line of sets can read as a repeat of frame 1. The camera is on the ground and the stacks lead, where frame 1 stands at eye height and the ends lead"
```

```yaml
slide: 9
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "a hearing room with nobody in it, six rows of eight folding chairs either side of an aisle facing a table, the amber cancellation posted on the table's front and a sheet on its top"
  rect: [0, 160, 1080, 680]
  bleeds: [left, right]
accent: "#E0A33F"
job: >
  Close on the hearing a Texan could have spoken at, which the agency says will be rescheduled,
  and on the report back date, October 19th.

claims: [c12, c13, c4]
numerals: []

depth:
  eye: 4.6
  horizon: 120
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, CAST_SHADOW, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    From the back of the room and above, down the aisle to the table, so the empty rows are the
    subject and the table is where the eye ends. The floor in front of the last row holds the
    caption.
  bands: >
    Top third, the table at the far end with its amber sheet and the first rows. Middle third,
    the empty rows either side of the aisle, seats and backs catching the light from the west.
    Bottom third, the nearest row's legs and cast shadows on the lit floor, then the hook, the
    dek and the amber note.
  focal: "the amber sheet on the table at the end of the aisle"

art:
  technique: "physically based render of chairs, a table and a sheet under the deck light"
  why_this_technique: >
    The claim is a hearing that did not happen. Forty eight empty chairs are the most direct
    image of that there is, and the same lamp keeps the room in the yard's world.
  palette: "night ground, dark seats, galvanised legs, the table's wood, the amber sheet"
  value_structure: >
    Lightest is the amber sheet and the lit floor down the aisle. Darkest is the fog at the far
    wall. The chairs carry the mid tones.
  motion: "down the aisle to the table, then back down to the caption"

type:
  hook: "A hearing with no date"
  dek: "The agency canceled the notice and comment hearing on data center permit O4791, captioned to Vantage Data Centers TX11. It says the hearing will be rescheduled for a later date. Separately, TCEQ answers to the Governor's office by October 19th."

verbatim: []

acceptance:
  - "the frame reads \"A hearing with no date\""
  - "the frame reads \"Separately, TCEQ answers to the Governor's office by October 19th.\""
  - "no person appears anywhere in the room"
  - "the notice on the table's front and the sheet on its top are the only amber on the frame, and no type is amber"

risks:
  - "an empty room can read as a stock image. The amber sheet ties it to the deck's paper and the lamp ties it to the yard"
```
