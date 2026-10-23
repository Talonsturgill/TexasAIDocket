# Storyboard, 2026-10-23
# "One added line moved the higher risk patient back"

## The story, and what the fact check did to it

UT Southwestern Medical Center in Dallas reported on October 20th, 2026 a study published in npj Digital Medicine
(c1, c2, c3). Records from emergency departments at Stanford Medicine and Beth Israel Deaconess Medical Center were
used, not a Texas hospital (c11). Patients were paired with one of similar starting severity (c12), and three open
source models were asked which was more likely to deteriorate and who should be seen first (c9, c10). With no social
or stigmatizing detail in the record, all three picked the higher risk patient at rates well above chance (c13). One
added line changed that. The release's own wording pair sets "established patient with multiple chronic conditions"
against "17 visits in the past 12 months" (c19). Frequent ED use and past psychiatric emergencies had some of the
strongest effects (c16), a single added detail sometimes shifted a model away from the patient who later deteriorated
(c8, c14), and in some instances nearly 10% of patients were incorrectly downgraded (c15). The authors' ask is plain
(c21). Bias varies by model, and each tool should be tested against real patient outcomes before use.

The fact check moved three things. The paper itself is behind a client challenge, so the deck stands on the release.
The authors' May preprint tested two different models (c30), so every preprint figure on a frame is named as the
preprint's (frame 8 only) and none stands in for the published result. The release names no Texas hospital using these
models for triage (c23), so no frame or caption places the tool in a Texas emergency room.

## Why this treatment, and what was grafted

Director B's record card is the spine. The whole experiment is one line of words on a record, so the record is drawn
as a physical card at one measured size, 127 by 203 mm, and the added line is a strip of ember tape with height and a
cast. Every count is rendered with that card or that tape. Triage is deciding what is looked at first, and one pool of
last light on one card is that decision made visible.

Grafted from Director C: the locked camera swap. Frames 3 and 6 share one camera on three sorting trays, and on 6 the
only thing that moves is the notched card dropping to the back slot of one tray. Refused from C: a supine figure on a
stretcher, which reads as a body, and a map of Texas for a study run on California and Massachusetts records. Refused
from Director A: the balance whose pan rises when paper is added, because a reader takes a physics error for a mistake
rather than for the argument.

## The world, and the laws that hold it

**LASTLIGHT, A STILL LIFE ON A SHALE LEDGE.** The chassis is `assets/js/deck/2026-10-23-ledger.js` and every frame
loads it. It declares `sky: lastLight` with the key at azimuth 62, elevation 14: the sun just down on the right, one low
warm key from the camera's right and in front, every card edge lit along its top, every cast running long to the left
and away. A material relief reads the same light from the right of its frame and its casts run to the left. +x is
east, +z south, a card faces +z.

The argument for this world: a record is read at hand distance, under one light, and the dark around it is everything
nobody is looking at. No hospital room is drawn, which keeps clear of nos. 55 and 56.

1. **Start dark.** Eagle Ford shale ledge near black, graphite steel held rough, bone card faces turned into the key.
2. **Type is light, on the dark field**, and every wash only darkens.
3. **Dusk ember is the only accent** and means one thing, the added line.
4. Every standing thing gets `TXT.contact`, every spatial frame `TXT.weather`.
5. **No screen, no robot, no brain, no logo, no real chart, no person's face.** Every carrier is disclosed in plain words.
6. **One card.** 127 by 203 by 0.25 mm, set once in the chassis, so a stack or a drawer is that card multiplied.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#07070C` | the DOM body behind the render |
| `accent` | `#BD452C` | dusk ember (#B4664F in the chassis) as it renders through the tone curve, the added line: 1, 4, 5, 6, 7, 8, 9 |
| `hook` | `#ECE6DA` | light type on the dark |
| `dek` | `#D8CFC0` | the dek |
| `material` | `#D8D0BE` | Austin Chalk bone, the card face |

The world's materials: bone record card stock with a corner notch for the patient who later deteriorated, ember vinyl
tape with a clearcoat, graphite steel at metalness 0.2, white vinyl wristbands with nickel snaps, an Eagle Ford shale
ledge #24262B with laminations, Blackland Prairie clay ground #17130F, the near black lastLight sky.

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE, VALUE_ARC

1. **Motif evolution, the ember tape.** Laid across one of two cards (1), absent from the stacks (2), absent from the
   trays (3), laid over the neutral line at macro (4), counted as 17 wristbands each with an ember tab (5), riding the
   card that dropped back (6), on the ten cards behind the divider (7), the two ember strips among ten (8), and peeled
   curling off the card at the close (9).
2. **Camera move.** Low at card height on the cover (1), a three quarter on the stacks (2), one locked camera on the
   trays (3 and 6), down onto the card (4), a long lens on the row of bands (5), over the drawer front (7), down onto a
   card of strips (8), and further back than the cover to close (9).
3. **Value arc.** The cover's two lit cards in a dark field, the darker stacks of 2, the trays in one pool on 3, the
   brightest frame at the card's face on 4, the bands in a line on 5, the darkest frame at the turn on 6 where only the
   tape is warm, the drawer on 7, the strips on 8 and the close on 9 back to one pool.

## The rotation

    FULL_BLEED  DIAGRAM  OBJECT_AND_CAPTION  DOCUMENT  GRID  OBJECT_AND_CAPTION  CLOSE_CROP  SPLIT_HORIZON  FULL_BLEED

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | CLOSE, eye 0.27 m above the ledge, 0.9 m off, a raised three quarter from the right, fov 30 | two bone record cards upright in a graphite steel two slot holder, card stock with a rounded corner, a notch on the right card and an ember vinyl tape with a clearcoat laid across its middle, standing on the dark shale ledge with contact shadows and grit at the holder's feet, the key raking their top edges |
| 02 | WIDE, eye 0.40 m above the ledge, 1.5 m off, three quarter from the right, fov 30 | two stacks of the deck's card on the ledge, each a block of instanced card edges with a slight lean and a top pair slid forward to show one notched card and one plain card, contact at each foot, the key on the stack edges |
| 03 | MEDIUM, eye 0.30 m above the ledge, 1.0 m off, a front three quarter from the right, fov 28 | three graphite steel stepped two slot sorting trays in a row, each holding a matched pair with the notched card in the front slot, the trays' folded edges catching the key, contact and grit at every foot |
| 04 | MACRO, an orthographic relief of one card propped toward the key | the bone record card, card stock with tooth and debossed ruled lines lit along their edges by the key, a raised ember tape strip laid over one line with its near corner lifted, a steel prop rod casting to the left, the shale falling to black outside the pool |
| 05 | MEDIUM, eye 0.30 m above the ledge, 1.1 m off, a low view from the front, fov 24 | seventeen closed white vinyl wristbands standing on edge in three rows of six, six and five on the ledge, each loop with a nickel snap and no accent, each casting its own shadow to the left on the lit shale, dark gaps between them |
| 06 | MEDIUM, frame 3's camera exactly | the same three sorting trays, the middle tray's notched card now in the back slot with its ember tape and the plain card in front, contact and grit at every foot, the tape the one warm thing |
| 07 | CLOSE, eye 0.28 m above the drawer, 0.8 m off, a low three quarter over the drawer front, fov 30 | a graphite steel index card drawer on the ledge, a rod through 100 upright cards as instanced card stock, a tabbed divider near the back, ten notched cards behind it each carrying an ember flag folded over its top edge, the drawer seated on the lit shale with contact |
| 08 | MACRO, an orthographic relief of one card | a TXBENCH relief of a bone card carrying ten laid strips at small angles, two in ember vinyl and eight in bone, each with height and a cast to the left and a curled right end |
| 09 | CLOSE, eye 0.21 m above the ledge, 0.7 m off, a three quarter from the right closer than the cover, the left card cropped | the cover's holder and two bone cards, card stock lit by the key with contact at the holder's feet on the lit shale, the ember tape across the notched card stuck across most of its width and its free end curling off past the card's right edge over the dark ledge, with its cast on the card |

Showstopper frame: 01, two bone cards standing in one pool of last light on near black shale, the ember tape's raised edge the brightest line and the dark sky above them
Tonal arc: the two lit cards of 1 in a dark field, the darker stacks of 2, one pool on the trays of 3, the brightest frame at the card face of 4, the row of bands on 5, the darkest at the turn on 6 with only the tape warm, the drawer of 7, the strips of 8 and the close of 9 back to one pool
VALUE CUT: frame 6. The deck turns from what the models did right to what one line did, and the dark frame with one warm strip is that turn.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "two bone record cards upright in a graphite steel holder on a shale ledge, the right card notched and carrying an ember tape strip across its middle"
  rect: [160, 600, 800, 750]
  bleeds: [bottom]
accent: "#BD452C"
job: >
  Say the finding as one picture, two matched records that differ by one strip of tape, and say who found it.

claims: [c1, c2, c8, c10, c12]
numerals: []

depth:
  eye: 0.12
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera stands at card height, three quarter to the holder from the right, so the two cards face the key and
    the camera at once and the near card overlaps the far one. The ledge runs off the left, right and bottom edges and
    the near black sky above it holds the hook and the dek.
  bands: >
    Top third, the dark sky with the hook and the dek. Middle third, the upper halves of both cards, the tape across
    the right card, their lit top edges. Bottom third, the holder, the ledge's lit top in the pool with the long casts
    to the left and the shale's laminated front edge falling to black.
  focal: "the ember tape and the lit face of the right card, the brightest area"

art:
  technique: "physically based render of the chassis record_card, card_holder, label_tape and shale_ledge in the lastLight world, staged"
  why_this_technique: "two records identical but for one strip is the study's design made physical, and it reads before a word"
  palette: "bone card stock, ember vinyl, graphite steel, Eagle Ford shale, a warm low key"
  value_structure: >
    Lightest are the card faces and their top edges in the key. Darkest are the sky and the shale beyond the pool.
    Frame median L* planned at 3.

type:
  hook: "One added line moved the higher risk patient back"
  dek: "UT Southwestern researchers asked AI models which of two matched emergency patients to see first. A single added detail sometimes shifted a model away from the patient who later deteriorated. The cards are drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the two record cards stand upright in the holder and together span at least 420 px of the frame width at full size"
  - "the cards stand at least 160 px tall at 432px"
  - "the ember tape crosses the right card and is visible at 432 px"
  - "the holder stands on the ledge with a contact shadow under its feet"
  - "no screen, logo or face in frame"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "bone card faces can lift the frame into the mid tones, so the pool stays tight and the ledge beyond it falls to black"
```

```yaml
slide: 2
layout: DIAGRAM
primary_image:
  subject: "two stacks of the deck's record card on the shale ledge, one per emergency department, each with its top pair slid forward"
  rect: [30, 760, 1000, 450]
  bleeds: []
accent: none
job: >
  Say where the records came from and how they were matched, two departments outside Texas and patients paired by severity.

claims: [c11, c12]
numerals: []

data_in_art:
  figure: departments
  drives: the stack count, one stack per department the release names

depth:
  eye: 0.35
  horizon: 470
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The two stacks stand side by side across the middle of the frame, seen from a raised three quarter so their
    tops and fronts both show. Each top pair is slid forward toward the camera, one notched card and one plain card.
    A DOM label stands above each stack with a short leader to its top.
  bands: >
    Top third, the dark sky with the hook and the dek. Middle third, the two labels and the stack tops with their
    slid pairs. Bottom third, the stack fronts, their card edges lit in fine lines by the key, the contact shadows and
    long casts to the left on the lit shale.
  focal: "the two slid top pairs, the lit card faces, the brightest area"

art:
  technique: "physically based render of two instanced card stacks in the lastLight world, staged as one subject"
  why_this_technique: "a stack of cards at one card size is a record set a reader can see, one per department"
  palette: "bone card stock, graphite steel, Eagle Ford shale, a warm low key"
  value_structure: >
    Lightest are the slid card faces and the stack edges in the key. Darkest are the sky and the far ledge.
    Frame median L* planned at 3.

type:
  hook: "Two emergency departments, paired patients"
  dek: "The records came from Stanford Medicine in California and Beth Israel Deaconess Medical Center in Massachusetts, not a Texas hospital. Each patient was paired with one of similar starting severity."
  labels: ["Stanford Medicine", "Beth Israel Deaconess"]

verbatim: []

acceptance:
  - "two card stacks stand on the ledge, each at least 120 px tall at 432px"
  - "each stack's top pair is slid forward and shows one notched card and one plain card at full size"
  - "both stacks stand on the ledge with a contact shadow at their feet"
  - "each label sits above its own stack with a leader that lands on that stack's top"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "card edges in a stack can read as a grey block, so the key rakes them and every tenth card is offset"
```

```yaml
slide: 3
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "three graphite steel sorting trays in a row, each holding a matched pair with the notched card in the front slot"
  rect: [0, 740, 1080, 450]
  bleeds: [left, right]
accent: none
job: >
  Show the baseline, every model putting the patient who later deteriorated in front before any line was added.

claims: [c9, c10, c13]
numerals: []

data_in_art:
  figure: models
  drives: the tray count, one tray per open source model the release says was tested

depth:
  eye: 0.30
  horizon: 500
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    Three trays in a row across the frame from a front three quarter, the near tray largest and the row receding to
    the left. Each tray is a stepped two slot rack, its front slot lower, and the notched card stands in front in all
    three. The camera is locked here and reused exactly on frame 6.
  bands: >
    Top third, the dark sky with the hook and the dek. Middle third, the card tops in all three trays and the notches
    on the front cards. Bottom third, the trays' folded steel bases, their contact shadows and casts to the left on the
    lit shale.
  focal: "the notched front cards in the near two trays, the brightest area"

art:
  technique: "physically based render of three chassis sorting_tray models with cards in the lastLight world, staged as one subject"
  why_this_technique: "a tray's front slot is the patient seen first, and three trays are the three models"
  palette: "graphite steel, bone card stock, Eagle Ford shale, a warm low key"
  value_structure: >
    Lightest are the card faces and the tray edges in the key. Darkest are the sky and the shadowed tray backs.
    Frame median L* planned at 3.

type:
  hook: "First, all three models beat chance"
  dek: "With no social or stigmatizing detail in the record, all three open source models picked the higher risk patient at rates well above chance. Each tray stands for one model, and the notched card is the patient who later deteriorated."
  labels: []

verbatim: []

acceptance:
  - "three sorting trays stand in a row and the near tray is at least 140 px wide at 432px"
  - "in every tray the notched card stands in the front slot"
  - "every tray stands on the ledge with a contact shadow under its base"
  - "the camera position matches frame 6 exactly"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "thin steel trays can vanish in the dark, so their folded top edges carry the key"
```

```yaml
slide: 4
layout: DOCUMENT
primary_image:
  subject: "one bone record card propped toward the key, its ruled lines debossed and an ember tape strip laid over one line"
  rect: [70, 690, 1010, 660]
  bleeds: [right, bottom]
accent: "#BD452C"
job: >
  Put the two wordings side by side in the record's own place, the neutral line under the stigmatizing one.

claims: [c19]
numerals:
  - value_from: c19

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The card fills the lower 55 percent, cropped off the right and bottom edges, its ruled lines running across it.
    The ember tape lies across the middle line with its near left corner lifted, and the neutral wording shows in DOM
    type on the ruled line above the tape, and the stigmatizing wording is set on the tape itself.
  bands: >
    Top third, the dark ground with the hook and the dek. Middle third, the card's top edge, the neutral line in type
    and the tape with its lifted corner. Bottom third, the debossed ruled lines lit along their edges and the card's
    stock texture under the key.
  focal: "the ember tape and its lifted corner, the brightest area"

art:
  technique: "material relief through txbench.js, four materials under the deck's light"
  why_this_technique: "a line of words on a record is the whole experiment, and a relief gives the tape height and a cast on the card"
  palette: "bone card stock, ember vinyl, graphite steel, near black shale"
  value_structure: >
    Lightest are the card face in the pool and the tape's raised edge. Darkest are the shale outside the pool and the
    casts. Frame median L* planned at 8.

type:
  hook: "Neutral words against stigmatizing ones"
  dek: "One wording pair in the study set a neutral description against a stigmatizing one. The tape here carries the second, set under the first."
  labels: ["established patient with multiple chronic conditions", "17 visits in the past 12 months"]

verbatim:
  - claim: c19
    text: "established patient with multiple chronic conditions"
  - claim: c19
    text: "17 visits in the past 12 months"

acceptance:
  - "the record card fills at least 45 percent of the frame area at full size"
  - "the ember tape strip crosses the card and stands visibly proud with a cast to the left"
  - "the debossed ruled lines show at 432 px"
  - "both wordings are set as DOM type, the stigmatizing one on the tape"
  - "the frame's median L* at 432px is 30 or lower"

risks:
  - "a pale card face is the mid tone risk, so the pool falls off fast toward the edges and the card tilts into the key"
```

```yaml
slide: 5
layout: GRID
primary_image:
  subject: "seventeen closed white vinyl wristbands standing on edge in three rows of six, six and five on the shale ledge"
  rect: [20, 720, 1040, 460]
  bleeds: []
accent: "#BD452C"
job: >
  Make the stigmatizing line physical, seventeen visits a reader can count.

claims: [c19]
numerals:
  - value_from: c19

data_in_art:
  figure: visits
  drives: the wristband count, one band per visit in the line

depth:
  eye: 0.10
  horizon: 560
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A raised view from the front looks down on three rows of loops standing on edge, six, six and five, square to
    the camera and each separated by dark. Every loop takes the key on its right side and casts to the left. The
    ledge bleeds off three edges.
  bands: >
    Top third, the dark sky with the hook and the dek. Middle third, the row of loops with their lit rims and ember
    tabs. Bottom third, the ledge's lit top in front of the row, the casts to the left and the shale front falling to
    black.
  focal: "the lit rims of the loops across the middle, the brightest area"

art:
  technique: "physically based render of seventeen chassis wristband models in the lastLight world, staged as one subject"
  why_this_technique: "a count of identical units reads as a count, and a wristband is the token a hospital visit leaves"
  palette: "white vinyl, nickel snaps, ember tabs, Eagle Ford shale, a warm low key"
  value_structure: >
    Lightest are the loop rims in the key. Darkest are the gaps between loops and the sky. Frame median L* planned at 3.

type:
  hook: "17 visits, one line on a record"
  dek: "The stigmatizing line counted 17 visits in the past 12 months. One wristband stands for one visit."
  labels: []

verbatim: []

acceptance:
  - "seventeen wristbands stand in three rows and each is countable at 432 px"
  - "the rows span at least 600 px of the frame width at full size"
  - "every band stands on the ledge with its own cast to the left"
  - "no two bands touch at 432 px"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "seventeen loops can merge into one bright mass, so the rows are spaced and the loops turned square to the camera"
```

```yaml
slide: 6
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "the same three sorting trays, the middle tray's notched card now in the back slot wearing the ember tape"
  rect: [0, 740, 1080, 450]
  bleeds: [left, right]
accent: "#BD452C"
job: >
  Show the turn, the one card that moved back once the line was added, from the camera the reader already knows.

claims: [c8, c13, c14, c21]
numerals: []

data_in_art:
  figure: models
  drives: the tray count, unchanged from frame 3

depth:
  eye: 0.30
  horizon: 500
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    Frame 3's camera, frame 3's trays. In the middle tray the notched card has dropped to the back slot and carries
    the ember tape, and the plain card stands in front. The other two trays are as they were. The frame is darker than
    3 and the tape is the one warm thing.
  bands: >
    Top third, the dark sky with the hook and the dek. Middle third, the card tops, the moved card higher in the back
    slot with its ember tape. Bottom third, the tray bases with their contact shadow and casts to the left on the lit
    shale ledge.
  focal: "the ember tape on the moved card in the middle tray, the brightest area"

art:
  technique: "physically based render of the three chassis sorting_tray models in the lastLight world, frame 3's camera"
  why_this_technique: "a locked camera lets a reader see the one card that moved before reading a word"
  palette: "graphite steel, bone card stock, ember vinyl, Eagle Ford shale, a warm low key"
  value_structure: >
    Lightest are the ember tape and the moved card's top edge. Darkest are the sky and the shadowed trays.
    Frame median L* planned at 3.

type:
  hook: "Then the higher risk patient sometimes went second"
  dek: "A single added detail sometimes shifted a model's priority away from the patient who later deteriorated, the senior author says. The bias varied by model. One tray shows the taped card moved to the back."
  labels: []

verbatim: []

acceptance:
  - "the middle tray's notched card stands in the back slot with the ember tape on it"
  - "the other two trays hold their notched cards in the front slot, as on frame 3"
  - "three sorting trays stand on the ledge with contact shadows, the near tray at least 140 px wide at 432px"
  - "the camera position matches frame 3 exactly"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "the move is small at feed size, so the moved card stands taller in the back slot and the tape is the frame's one accent"
```

```yaml
slide: 7
layout: CLOSE_CROP
primary_image:
  subject: "a graphite steel index card drawer of 100 upright cards, ten notched cards with ember flags behind a divider"
  rect: [0, 760, 1080, 420]
  bleeds: [left, right]
accent: "#BD452C"
job: >
  Size the effect, nearly ten in a hundred moved back, as cards a reader can count by their flags.

claims: [c15]
numerals:
  - value_from: c15

data_in_art:
  figure: downgraded_of_100
  drives: the number of flagged cards behind the divider out of per_hundred cards in the drawer

depth:
  eye: 0.22
  horizon: 430
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A low three quarter over the drawer front looks down its length, the cards receding toward the back, a tabbed
    divider near the back and ten notched cards behind it, each with an ember flag standing above its top edge. The
    drawer is cropped by the right and bottom edges and runs toward the upper left.
  bands: >
    Top third, the dark sky with the hook and the dek, the drawer's far end. Middle third, the divider and the ten
    flagged cards with their flags in the key. Bottom third, the near cards' lit top edges in the drawer, the drawer's
    steel front and its contact shadow on the shale.
  focal: "the ten ember flags behind the divider, the brightest area"

art:
  technique: "physically based render of the chassis card_drawer with instanced cards in the lastLight world, staged"
  why_this_technique: "a drawer of a hundred cards is a share a reader can count without a chart"
  palette: "graphite steel, bone card stock, ember vinyl, Eagle Ford shale, a warm low key"
  value_structure: >
    Lightest are the ten ember flags and the near card tops in the key. Darkest are the drawer's inside and the
    sky. Frame median L* planned at 4.

type:
  hook: "Nearly 10% moved back"
  dek: "Nearly 10% of patients were incorrectly downgraded once stigmatizing information was added. The drawer holds 100 cards in blocks of ten, and the flagged block stands for the share."
  labels: ["nearly 10 in 100"]

verbatim: []

acceptance:
  - "the drawer holds upright cards across at least 600 px of the frame width at full size"
  - "ten flagged cards stand behind the divider and their ember flags are visible at 432 px"
  - "the drawer sits on the ledge with a contact shadow under its front"
  - "the near card tops are lit as separate lines rather than one block at full size"
  - "the frame's median L* at 432px is 26 or lower"

risks:
  - "a hundred card tops merge into one block, so the key rakes across the drawer and the ten carry flags above the divider"
```

```yaml
slide: 8
layout: SPLIT_HORIZON
primary_image:
  subject: "one bone record card carrying ten laid strips, two in ember vinyl and eight in bone, each standing proud with a cast"
  rect: [0, 720, 1080, 630]
  bleeds: [left, right, bottom]
accent: "#BD452C"
job: >
  Name which added lines moved the models most and which did not, naming the preprint where its figures are used.

claims: [c16, c26, c34, c38]
numerals:
  - value_from: c34

data_in_art:
  figure: conditions
  drives: the strip count on the card, one strip per condition the preprint tested

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The card fills the lower half and bleeds off three edges. Ten strips lie across it at small angles, their right
    ends curled. The two ember strips sit third and sixth from the top. Two DOM labels name the ember strips at their
    left ends. The split is the card's top edge against the dark ground above.
  bands: >
    Top third, the dark ground with the hook and the dek. Middle third, the card's top edge and the first five strips
    with the first ember strip and its label. Bottom third, the last five strips with the second ember strip and its
    label, every strip lit along its edge with its cast to the left.
  focal: "the two ember strips, the brightest area"

art:
  technique: "material relief through txbench.js, three materials under the deck's light"
  why_this_technique: "ten added lines are ten strips on one record, and the two that moved the models most are ember"
  palette: "bone card stock, ember vinyl, near black shale"
  value_structure: >
    Lightest are the strip edges and the card face in the pool. Darkest are the casts and the shale outside the pool.
    Frame median L* planned at 10.

type:
  hook: "Visits and psychiatric history stood out"
  dek: "The release names frequent emergency use and past psychiatric emergencies among the strongest effects. The authors' unreviewed May preprint tested 10 added lines and found no harmful shift from race, language or insurance."
  labels: ["frequent emergency visits", "psychiatric emergencies"]

verbatim: []

acceptance:
  - "ten strips lie on the card and each is countable at 432 px"
  - "two strips are ember and eight are bone"
  - "every strip stands proud of the card with a cast to the left"
  - "the card fills at least 40 percent of the frame area at full size"
  - "the frame's median L* at 432px is 30 or lower"

risks:
  - "frames 4 and 8 are both card reliefs, so 8 shows a whole card of ten strips and 4 a macro of one"
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: "the cover's holder and two cards, the ember tape on the notched card with its free end curling off past the card's right edge"
  rect: [100, 595, 815, 605]
  bleeds: []
accent: "#BD452C"
job: >
  Close on the consequence, how the record is written changes the answer, and the authors' ask before any hospital uses one.

claims: [c1, c4, c21, c23]
numerals: []

depth:
  eye: 0.14
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera stands closer than the cover's, on the notched card with the left card cropped and the notched corner in
    frame. The tape lies across the notched card where the cover laid it, stuck along its left half, its right
    end curling off past the card's right edge over the dark ledge, so the lift reads in profile. The ledge bleeds off three edges and the dark sky holds the type.
  bands: >
    Top third, the dark sky with the hook and the dek. Middle third, the two cards in the holder and the tape with its
    lifted curl and its cast on the card. Bottom third, the holder's base and feet on the ledge's lit top with the casts to the
    left and the shale front.
  focal: "the lifted ember curl on the lit face of the notched card, the brightest area"

art:
  technique: "physically based render of the chassis record_card and card_holder with the tape strip curled off the card in the lastLight world, staged"
  why_this_technique: "a tape taken off the card is the record rewritten, which is what the authors say decides the answer"
  palette: "bone card stock, ember vinyl, graphite steel, Eagle Ford shale, a warm low key"
  value_structure: >
    Lightest are the card faces and the tape's lit edge. Darkest are the sky and the shale beyond the pool.
    Frame median L* planned at 5.

type:
  hook: "Test each tool on real outcomes first"
  dek: "Bias varies by model, so each AI tool should be tested on real patient outcomes before use, the first author says. UT Southwestern's October 20th release names no Texas hospital using these models for triage."
  labels: []

verbatim: []

acceptance:
  - "the two record cards stand in the holder and together span at least 420 px of the frame width at full size"
  - "the ember tape crosses the notched card and its curled end stands off the card, at least 50 px wide at 432px"
  - "the two bone cards stand at least 120 px tall at 432px"
  - "the holder rail stands under both cards, its feet cropped by the close"
  - "the notched card's clipped corner is in frame"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "a curl of thin tape can read as a printed bar, so it is built with thickness and lifts toward the camera"
```
