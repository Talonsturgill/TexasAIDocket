# Storyboard, 2026-10-22
# "Fed short viral posts, the models skipped steps"

## The story, and what the fact check did to it

Researchers at Texas A&M, with the University of Texas at Austin and Purdue listed as the paper's institutions,
continually trained four open language models on mixes of junk and control posts drawn from 1 million public
Twitter/X posts (c6, c16, c25). Under the engagement measure, junk is under 30 tokens with popularity over 500 and
control is over 100 tokens with popularity 0 (c18, c19). On Llama3 8B Instruct, the most sensitive of the four (c57),
ARC Challenge with chain of thought scored 72.1, 71.2, 69.3, 64.1 and 57.2 as the junk share rose from none to all,
against a base of 77.2 (c33). Variable tracking did not fall at every step (c36). The paper names thought skipping
as the main failure (c38), with No Thinking in 84% of failures under junk training (c39). The repair is partial:
instruction data 4.8 times the junk tokens (c44) still left the best repaired model 17.3 points under the baseline
(c47). The limits are the paper's own: one platform, four open models, closed models untested, doses rather than an
estimate of the internet (c62, c64, c65).

The fact check moved three things. The releases date the posts to 2010 and the paper to 2023 (c17), so the deck
prints no collection year and the record was corrected. The release's definition of junk leaves out quotes, so the
deck uses the paper's (c18, c19). The release frames Tu as the lead and the paper credits Z. Wang with the idea, so
the deck names the institutions and quotes Tu and Xing only as speakers.

## Why this treatment, and what was grafted

Director A's stair is the spine. The paper's own language is steps, plans and skipped steps (c38), and a stair is
the one built thing whose use depends on its steps: with treads gone it still stands and can't be climbed. Every
score becomes the stair's rise from the ground at ONE scale, 0.06 m per point, computed in code, so a falling score
is lost height a reader can stand under, and the brass datum is where the base model stood.

Grafted from Director B: one length scale for every score, never a second, and plan views only where the subject's
own convention is a plan (frame 2's surface). From Director C: the close of the limits, four tested stairs beside an
empty pad where no closed model was tested (frame 8), which replaces A's limestone plaque, since a plaque carrying
type is a plate. Refused from C: the feeding metaphor, because a feed trial invites an animal study nobody ran.
Refused from B: seven new models in a day.

## The world, and the laws that hold it

**LASTLIGHT, A STAIR IN AN EMPTY FIELD.** The chassis is `assets/js/deck/2026-10-22-stair.js` and every frame loads
it. It declares `sky: lastLight` with the key at azimuth -58, elevation 10: the sun just down, one low warm key from
the camera's left and in front, every nosing lit along its edge, every cast running long to the right and away. A
material relief reads the same light from the left of its frame and its casts run to the right. +x is east, +z south,
and a stair climbs toward -z.

The argument for this world: a stair is read by its nosing edges and the shadows under its treads, and a low raking
key is the one light that draws both. The stair stands in no real place, which is honest for a lab study with no
Texas deployment.

1. **Start dark.** Limestone held to a mid albedo, weathering steel stringers, a dark caliche ground, the pool where
   the stair stands.
2. **Type is light, on the dark field**, and every wash only darkens.
3. **Dusk gold is the only accent** and means one thing, the brass datum where the base model stood.
4. Every standing thing gets `TXT.contact`, every spatial frame `TXT.weather`.
5. **No brain, no robot, no screen, no logo, no platform mark.** Every frame says drawn to illustrate.
6. **One scale.** 0.06 m per score point on every stair, set once in the chassis, every rise computed from
   figures.json in the frame's own code.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#08060F` | the DOM body behind the render |
| `accent` | `#E0956A` | dusk gold, the brass datum: 3, 4, 7, 9 |
| `hook` | `#ECE6DA` | light type on the dark |
| `dek` | `#D8CFC0` | the dek |
| `material` | `#B9AE98` | Central Texas limestone treads and piers, held down |

The world's materials: sawn limestone #B9AE98 held to a mid albedo, exposed aggregate treads cast with limestone
slivers (control) or bottle green and amber glass chips (junk) in a buff matrix, weathering steel stringers #5E3A26,
a dark caliche ground, a brass datum strip, a warm 2700 K key and the near black lastLight sky.

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE, VALUE_ARC

1. **Motif evolution, the stair.** Whole but missing its middle treads (1), its own tread surface at native size
   (2), walked down landing by landing as the dose rises (3), broken into a cliff (4), stripped to its stringers (5),
   laid out as new treads for the repair (6), rebuilt and stopping short of the brass (7), multiplied into the four
   tested stairs beside an empty pad (8), and the base stair beside the junk stair at the close (9).
2. **Camera move around one stair.** Low at the foot (1), down onto a tread (2), back to a long low oblique (3), onto
   the landing lip (4), under the open side (5), down the row of treads (6), standing on the top landing (7), a wide
   from the front (8), and back to the cover's side to close (9).
3. **Value arc.** The cover's lit nosings in a dark field, the surface close on 2 the most detailed frame, the long
   dark walk with one brass line on 3, the darkest frames at the cliff (4) and the skipped steps (5), the warmest
   frame on 6 where the clean treads lie in the pool, then the repair and the close falling back to one pool.

## The rotation

    FULL_BLEED  CLOSE_CROP  DIAGRAM  CLOSE_CROP  OBJECT_AND_CAPTION  CLOSE_CROP  FULL_BLEED  GRID  FIGURE_SCALE

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | MEDIUM, eye 2.7 m, 8 m from the foot, three quarter from the right, fov 32 | the chassis stair_flight at full detail: two weathering steel stringers with sawtooth tops, exposed aggregate treads with a bullnose nosing in junk glass chip aggregate, its middle treads missing so the empty stringer notches show, a sawn limestone landing on a stone pier, standing on dark caliche with contact shadows and grime at the feet |
| 02 | MACRO, an orthographic plan relief of one tread's surface | a TXBENCH relief of exposed aggregate: a buff cement matrix with tooth in albedo, glossy glass chips standing proud with lengths under the junk token scale on the left and matte limestone slivers longer than the control token scale on the right, a brass divider strip between, every piece casting to the right |
| 03 | WIDE, eye 3.4 m, 41 m off at a front oblique, fov 18 | five open stairs side by side, one per dose, each rising to a landing on a limestone pier, weathering steel stringers and aggregate treads with aggregate treads and steel stringers, lit along every nosing by the low key, contact shadows at every pier foot and grime on the pier bases, descending left to right with the dose, a long sawn limestone wall behind carrying the brass datum strip at the base model's height, staged as one subject in the pool |
| 04 | CLOSE, eye 0.45 m above the 50 percent landing, fov 30 | the variable tracking walk at the same scale, sawn limestone landings with aggregate tops lit by the key and weathered pier faces, a single short riser up to the 80 percent landing, then its edge and a sheer pier face down to the 100 percent landing far below in shadow with contact at its foot, the datum wall high behind with its brass line |
| 05 | MEDIUM, eye 1.0 m, three quarter from the open side, fov 34 | the stair carcass, two weathering steel stringers rising to a landing on a pier, treads present only on the foot's share of the run and the rest bare notched teeth raked by the key |
| 06 | MEDIUM, eye 1.1 m, 6 m back, low oblique, fov 22 | cut treads laid end to end on the ground, one in junk glass aggregate then clean limestone treads to 4.8 times its length, the last one sawn short with its saw face lit, each with its own contact |
| 07 | CLOSE, eye 1.6 m standing on the repaired stair's top landing, fov 34 | the repaired stair's top landing in pale fresh limestone, the datum wall beside it with the brass strip above the landing, the bare wall between them lit in the pool, the flight falling away below |
| 08 | WIDE, eye 1.4 m, 14 m back, fov 30 | four stair flights side by side, each weathering steel stringers and aggregate treads with lit nosings, contact shadows at every foot and grime on the stringer bases, their tops cropped by the frame so no height is read, and a fifth pad of bare concrete with a chalk outline and no stair, all on the dark caliche in one pool |
| 09 | WIDE, eye 1.7 m, 17 m off, a front three quarter from the right, fov 30 | the base height stair whole beside the all junk stair with its middle treads gone, the datum wall behind both, a kit person at the foot of the broken flight under a fifth of the frame, lit from the camera side |

Showstopper frame: 01, the freestanding stair with its middle treads gone, every surviving nosing lit by the low key and the empty notches catching the light against a near black sky
Tonal arc: the lit nosings of 1 in a dark field, the detailed surface of 2, the long dark walk on 3 with one brass line, the cliff of 4 and the bare stringers of 5 the darkest, the clean treads of 6 the warmest, the repaired landing of 7, the four stairs of 8 and the close of 9 back to one pool
VALUE CUT: frame 6. The deck turns from what junk did to what the repair did, and the warm clean treads in the pool are that turn.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "a freestanding open stair of weathering steel stringers and glass aggregate treads rising to a limestone landing on a pier, its middle treads missing, at the junk model's score on the deck scale"
  rect: [150, 540, 870, 700]
  bleeds: []
accent: none
job: >
  Say the finding as one picture, a stair that can't be climbed because its middle steps are gone, and say who found it.

claims: [c6, c16, c26, c27, c33, c38]
numerals: []

data_in_art:
  figure: arc_cot_j100
  drives: stair height, the all junk score at 0.06 m per point

depth:
  eye: 2.7
  horizon: 560
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: -2}

composition:
  structure: >
    The camera stands above head height and three quarter to the stair's foot, so the flight climbs from the lower left toward the
    upper right and the gap in its treads sits in the middle of the frame. The landing and its pier stand at the top
    right and the near black sky holds the type above.
  bands: >
    Top third, the dark sky with the hook and the dek. Middle third, the upper flight, the landing and the gap where
    the treads are missing, the empty notches lit. Bottom third, the first treads, the stringer feet in contact with
    the caliche and their long casts to the right.
  focal: "the lit nosings and the empty stringer notches around the gap, the brightest area"

art:
  technique: "physically based render of the chassis stair_flight in the lastLight world, staged"
  why_this_technique: "a stair with its steps gone is the paper's main finding made physical, and it reads before a word"
  palette: "weathering steel, glass chip aggregate, sawn limestone, a warm low key"
  value_structure: >
    Lightest are the tread nosings and the notch edges in the key. Darkest are the sky, the stringer undersides and
    the ground beyond the pool. Frame median L* planned at 12.

type:
  hook: "Trained on short, popular posts, models skipped steps"
  dek: "Researchers at Texas A&M, the University of Texas at Austin and Purdue trained four language models on rising doses of short, popular posts. As the junk share rose, their reasoning skipped steps. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the stair spans at least 600 px of the frame width at full size, and a frame with no stair fails"
  - "the stair stands at least 200 px tall at 432px"
  - "at least three treads in the middle of the flight are missing and the stringer notches there are visible at 432 px"
  - "the stair stands on the ground with a contact shadow under each stringer foot and the pier"
  - "the landing at the top is modelled as a slab on a pier, not a floating plate"
  - "no brain, robot, screen or platform mark in frame"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "the stringers can read as two dark bars in the dark, so their top edges and notches carry the key"
```

```yaml
slide: 2
layout: CLOSE_CROP
primary_image:
  subject: "one tread's exposed aggregate surface at native size: short glossy glass chips on the left, long matte limestone slivers on the right, a brass divider strip between"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: none
job: >
  Define junk and control in one surface the reader can see: short and shiny against long and dull, at one length scale.

claims: [c16, c18, c19]
numerals:
  - value_from: c18
  - value_from: c16

data_in_art:
  figure: junk_tokens_lt
  drives: the longest glass chip, shorter than the junk token limit at 4 px per token, and every limestone sliver longer than control_tokens_gt at the same scale

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The surface fills the lower 60 percent and bleeds off three edges, the brass divider running from the lower left
    to the upper right across it, glass chips scattered on the left of it and limestone slivers laid long on the
    right. Two DOM labels sit just above the surface, one over each side.
  bands: >
    Top third, the dark ground above the surface with the hook and the dek. Middle third, the two labels and the top
    edge of the surface. Bottom third, the glossy chips and matte slivers in relief, each casting its shadow to the right off the edge.
  focal: "the cluster of glossy glass chips catching the key at the left, the brightest area"

art:
  technique: "material relief through txbench.js, four materials under the deck's light"
  why_this_technique: "the definition is a length and a shine, and a relief shows both as material at one scale"
  palette: "buff cement matrix, bottle green and amber glass, pale limestone, brass"
  value_structure: >
    Lightest are the glass chip glints and the limestone sliver edges. Darkest are the matrix in shadow and the dark
    ground above. Frame median L* planned at 22.

type:
  hook: "Junk meant short and popular"
  dek: "Junk was posts under 30 tokens with popularity over 500, counting likes, retweets, replies and quotes. Control was posts over 100 tokens with popularity 0. Both came from the same 1 million public posts. Drawn to illustrate, lengths at one scale."
  labels: ["junk, under 30 tokens", "control, over 100 tokens"]

verbatim: []

acceptance:
  - "the surface spans the full frame width at full size, and a frame with no surface fails"
  - "the exposed aggregate relief is modelled with chips and slivers proud of the matrix, and a frame without them fails"
  - "the aggregate surface owns at least half of the frame height"
  - "every glass chip is shorter than the junk limit at the frame's token scale and every sliver longer than the control limit"
  - "the glass chips read as glossy and the limestone slivers as matte at 432 px"
  - "every chip and sliver casts a shadow to the right"
  - "the brass divider is not the accent and carries no label"
  - "the frame's median L* at 432px is 30 or lower"

risks:
  - "a field of small pieces can read as noise, so pieces are few, large and cast long"
```

```yaml
slide: 3
layout: DIAGRAM
primary_image:
  subject: "five open stairs side by side, one per junk dose, each rising to a landing on a pier at its score, lower left to right, under a brass datum on a sawn wall behind"
  rect: [0, 600, 1080, 600]
  bleeds: [left, right]
accent: "#E0956A"
job: >
  Show the dose response as one built thing at one scale: each landing's height is a score, and every added share of junk takes height off.

claims: [c28, c30, c31, c32, c33, c57]
numerals:
  - value_from: arc_cot_m1
  - value_from: arc_cot_base
  - value_from: junk_ratios_m1

data_in_art:
  figure: arc_cot_j0
  drives: landing height for each of the five landings at 0.06 m per point, from arc_cot_j0 to arc_cot_j100

depth:
  eye: 3.4
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: -6}

composition:
  structure: >
    A long lens from a front oblique sets five stairs side by side, so their landings compare as heights against
    one brass line. The no junk stair stands at the left and the all junk stair at the right, each with its own
    stringers, treads and pier, and the long datum wall behind with one brass line above them all. Each stair
    carries a DOM label of its dose and score over it.
  bands: >
    Top third, the dark sky with the hook and the dek. Middle third, the datum line and the landing tops with their
    labels. Bottom third, the piers, the flights and their casts on the caliche.
  focal: "the brass datum running above the lit landing tops, the one warm line in the frame"

art:
  technique: "physically based render of the chassis stair_flight, landing_pier and datum_wall, long lens, staged in lastLight"
  why_this_technique: "a dose response read as heights of one stair at one scale needs no axis and no chart"
  palette: "sawn limestone, aggregate treads shifting from limestone to glass, weathering steel, brass"
  value_structure: >
    Lightest are the landing nosings and the brass line. Darkest are the pier faces in shadow and the sky. Frame
    median L* planned at 14.

type:
  hook: "More junk, a shorter climb"
  dek: "Llama3 8B Instruct was the most sensitive of the four models. Its ARC Challenge reasoning score fell from 72.1 with no junk to 57.2 with all junk. Each landing is its score at one scale. Brass marks the base model at 77.2. Drawn to illustrate."
  labels: ["0% 72.1", "20% 71.2", "50% 69.3", "80% 64.1", "100% 57.2", "base 77.2"]

verbatim: []

acceptance:
  - "five stairs are modelled, each with its own landing on a pier, and a frame with fewer fails"
  - "each landing's height is computed from arc_cot_m1 at the deck scale in the frame's own code"
  - "the brass datum is computed from arc_cot_base and sits above every landing"
  - "the walk spans at least 900 px of the frame width at full size"
  - "the tallest stair stands at least 110 px tall at 432px"
  - "the five stairs together span at least 360 px of the width at 432px"
  - "the landings read as stone at 432 px, with nosings and cast shadows, not as flat bars"
  - "each DOM label sits over its own stair, within 120 px of its own landing, and no label is struck by the brass line"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "the walk can read as a step chart, so every landing carries a nosing, a pier with tooth and a cast shadow"
  - "the first two landings differ by under a point and will look level, which is true and must not be exaggerated"
```

```yaml
slide: 4
layout: CLOSE_CROP
primary_image:
  subject: "the variable tracking walk from a low three quarter: a flight up to the no junk landing, a fall to the half junk landing, the 80 percent landing a short step higher, then a sheer drop to the all junk landing, under the brass datum on the wall"
  rect: [0, 640, 780, 710]
  bleeds: [left, bottom]
accent: "#E0956A"
job: >
  Show that the fall was not steady: a step up where a step down was expected, then a cliff.

claims: [c30, c31, c36]
numerals:
  - value_from: var_tracking_m1
  - value_from: var_tracking_base

data_in_art:
  figure: var_tracking_j80
  drives: landing height for each of the three landings, at 0.06 m per point

depth:
  eye: 0.45
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: -2.5}

composition:
  structure: >
    The camera lies just above the half junk landing and looks along the walk. The short riser and the 80 percent
    landing's lit edge cross the frame in the middle, and beyond the edge the stair simply ends, the pier face
    dropping to the low landing in shadow. The datum wall stands behind with its brass line high above.
  bands: >
    Top third, the dark sky and the brass line with the hook and dek. Middle third, the riser, the landing edge and
    the drop. Bottom third, the near landing's aggregate surface lit by the key, its texture raked, running off the bottom edge.
  focal: "the lit edge of the 80 percent landing against the dark drop beyond it"

art:
  technique: "physically based render of the chassis walk at close range, staged in lastLight"
  why_this_technique: "a non monotone result is a step the wrong way, and a reader feels a step"
  palette: "sawn limestone, aggregate treads, brass"
  value_structure: >
    Lightest are the landing edge and the near tread surface. Darkest are the drop and the sky. Frame median L*
    planned at 11.

type:
  hook: "Half junk scored below 80% junk"
  dek: "On a variable tracking test the same model scored 86.3 with no junk, 59.4 at half junk, 60.7 at 80% and 22.4 with all junk. The fall was not steady. Brass marks the base model at 98.3. Drawn to illustrate, heights at one scale."
  labels: ["0% 86.3", "50% 59.4", "80% 60.7", "100% 22.4", "base 98.3"]

verbatim: []

acceptance:
  - "the riser from the half junk landing up to the 80 percent landing is modelled and visible"
  - "the walk owns at least half of the frame height"
  - "the drop from the 80 percent landing to the all junk landing is visible as a pier face"
  - "every landing height is computed from var_tracking_m1 at the deck scale"
  - "the brass datum is computed from var_tracking_base and sits above every landing"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "a 1.3 point step is 8 cm at the deck scale and can vanish, so the eye sits near the landings and never exaggerates it"
```

```yaml
slide: 5
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "the stair carcass: two weathering steel stringers rising to a landing on a pier, treads only on the foot's share of the run and bare notched stringers above"
  rect: [520, 560, 560, 790]
  bleeds: [right, bottom]
accent: none
job: >
  Show thought skipping, the paper's main failure, as the share of a stair with no treads to step on.

claims: [c38, c39]
numerals:
  - value_from: c39

data_in_art:
  figure: no_thinking_m1_pct
  drives: bare stringer length as a share of the run

depth:
  eye: 1.0
  horizon: 640
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: -2}

composition:
  structure: >
    The carcass stands on the right two thirds seen three quarter from its open side, the treads at the foot lit,
    the long bare stringers climbing past them to the landing with their notches raked by the key. The type sits on
    the dark field at the left and top.
  bands: >
    Top third, the sky, the landing and the hook. Middle third, the bare stringers and the dek. Bottom third, the few
    lit treads at the foot and the stringer feet with their long shadows on the caliche.
  focal: "the run of bare lit notches climbing above the last tread"

art:
  technique: "physically based render of the chassis stair_flight carcass, staged in lastLight"
  why_this_technique: "a step with nothing to stand on is what skipping a step means"
  palette: "weathering steel, glass aggregate treads, sawn limestone"
  value_structure: >
    Lightest are the notch edges and the few treads. Darkest are the stringer sides and the sky. Frame median L*
    planned at 10.

type:
  hook: "Most failures skipped the thinking"
  dek: "The paper names thought skipping as the main reasoning failure. Its \"No Thinking\" category turned up in 84% of failures with junk defined by engagement and in over 70% across all cases. The bare share of the stair is that 84%. Drawn to illustrate."
  labels: []

verbatim:
  - c39: "No Thinking"

acceptance:
  - "the stringers span at least 450 px of the frame height at full size, and a frame with no stair fails"
  - "the stair carcass is modelled with two weathering steel stringers and notched tread seats, and a frame without them fails"
  - "the carcass stands at least 180 px tall at 432px"
  - "the bare share of the run is computed from no_thinking_m1_pct in the frame's own code"
  - "the treads that remain sit at the foot and read as treads at 432 px"
  - "the empty notches read as notches at 432 px"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "a reader could take 84 percent of steps for 84 percent of failures, so the dek names the set"
```

```yaml
slide: 6
layout: CLOSE_CROP
primary_image:
  subject: "two stacks of cut treads on the caliche: one junk glass aggregate tread alone, and beside it fresh limestone treads stacked four high with a fifth sawn to 0.8 of a tread on top, every end in frame"
  rect: [0, 790, 1080, 420]
  bleeds: [left, right]
accent: none
job: >
  Show the size of the repair: one tread of junk against 4.8 treads of clean data.

claims: [c42, c43, c44]
numerals:
  - value_from: c43
  - value_from: c44

data_in_art:
  figure: it_multiple
  drives: the count of clean treads and the sawn length of the last one, at the junk tread's length

depth:
  eye: 1.1
  horizon: 600
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: -3}

composition:
  structure: >
    The row runs across the frame from the dark glass tread at the left to the sawn short limestone tread at the
    right, seen from a low oblique so every unit is the same size, each with its own contact shadow and a gap.
    Labels sit above the junk tread and above the clean run.
  bands: >
    Top third, the sky and the hook. Middle third, the dek and the labels. Bottom third, the treads lying on the caliche in the pool, each lit along its nosing and casting its own contact shadow to the right.
  focal: "the warm lit clean treads in the pool against the one dark glass tread"

art:
  technique: "physically based render of the chassis tread_slab, staged in lastLight"
  why_this_technique: "a ratio of lengths reads as units of the same object laid side by side"
  palette: "pale clean limestone, glass aggregate, dark caliche"
  value_structure: >
    Lightest are the clean tread tops and the sawn face. Darkest are the glass tread and the sky. Frame median L*
    planned at 20.

type:
  hook: "Repair data at 4.8 times the junk"
  dek: "To repair the all junk model, the researchers scaled its instruction tuning from 5k to 50k examples, the whole Alpaca set. That data came to 4.8 times the junk tokens and still didn't fully undo the damage. Drawn to illustrate."
  labels: ["junk tokens", "4.8 times the junk tokens"]

verbatim: []

acceptance:
  - "one junk tread and limestone treads totaling 4.8 of its length are modelled, the last sawn to 0.8 of a tread"
  - "both stacks span at least 340 px of the width at 432px, and both ends of every tread are inside the frame"
  - "the limestone tread count and the last tread's length are computed from it_multiple in the frame's own code"
  - "the sawn top tread's short end and its saw face are visible, and the junk tread is darker than every limestone tread"
  - "the frame's median L* at 432px is 30 or lower"

risks:
  - "five pale slabs can read as a bar, so each carries its own aggregate and nosing and stands apart"
```

```yaml
slide: 7
layout: FULL_BLEED
primary_image:
  subject: "the repaired stair's top landing in fresh limestone beside the datum wall, the brass line above it and the bare wall between"
  rect: [0, 470, 1080, 880]
  bleeds: [left, right, bottom]
accent: "#E0956A"
job: >
  Show the repair falling short: the rebuilt stair still stops under the line where the base model stood.

claims: [c41, c47, c51]
numerals:
  - value_from: c47

data_in_art:
  figure: gap_arc_pct
  drives: datum height above the repaired landing, at 0.06 m per point

depth:
  eye: 1.6
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: -1.5}

composition:
  structure: >
    The camera stands on the repaired top landing and looks along the datum wall, the brass line running across
    above the landing at the computed shortfall, the bare lit wall between them the subject. The flight falls away
    below the frame.
  bands: >
    Top third, the sky, the hook and the brass line. Middle third, the bare wall between the line and the landing.
    Bottom third, the landing's fresh limestone surface lit by the key, its grain raked and its nosing casting a shadow.
  focal: "the bare lit wall between the landing and the brass line"

art:
  technique: "physically based render of the chassis stair_flight and datum_wall, staged in lastLight"
  why_this_technique: "a shortfall is a distance to a line, and a wall makes the distance a surface"
  palette: "fresh pale limestone, sawn wall stone, brass"
  value_structure: >
    Lightest are the landing nosing and the brass line. Darkest are the sky and the wall away from the pool. Frame
    median L* planned at 16.

type:
  hook: "Repaired, still 17.3 points short"
  dek: "The best repaired models still trailed the baseline by 17.3 points on the ARC Challenge reasoning test. The paper says the damage persisted after tuning at the scales it tested. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the distance from the landing top to the brass line is computed from gap_arc_pct at the deck scale"
  - "the brass line is visible across at least 500 px of the frame at full size"
  - "the landing and wall subject owns at least half of the frame height"
  - "the landing reads as stone with a nosing at 432 px"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "a wall face is a broad flat plane, so its coursing and tooth carry detail and the pool falls off along it"
```

```yaml
slide: 8
layout: GRID
primary_image:
  subject: "four stair flights side by side with their tops cropped by the frame, and a fifth bare pad with a chalk outline and no stair"
  rect: [0, 0, 1080, 760]
  bleeds: [left, right, top]
accent: none
job: >
  Name what the study did not test: four open models stand, and the place for a closed model is empty.

claims: [c15, c25, c58, c65]
numerals:
  - value_from: c25

data_in_art:
  figure: models
  drives: the count of stair flights built, with one empty pad beside them

depth:
  eye: 1.4
  horizon: 700
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: -8}

composition:
  structure: >
    Four flights stand in a row across the left three quarters, each climbing out of the top of the image band so
    no height is read, and the empty pad with its chalk outline sits at the right in the same pool. Model names sit
    in mono on the ground beside each flight's foot.
  bands: >
    Top third, the sky with the hook and the dek. Middle third, the flights climbing out of the image band. Bottom
    third, the feet, the pad and the labels on the caliche.
  focal: "the empty pad with its pale chalk outline beside the fourth stair"

art:
  technique: "physically based render of four chassis stair_flight models and a pad, staged in lastLight"
  why_this_technique: "what was not tested is an absence, and an empty pad beside four stairs makes it one"
  palette: "weathering steel, limestone, pale chalk, dark caliche"
  value_structure: >
    Lightest are the chalk outline and the nosings. Darkest are the sky and the stair undersides. Frame median L*
    planned at 13.

type:
  hook: "Four main models. No ChatGPT or Gemini."
  dek: "The study tested Llama3 8B Instruct, two Qwen2.5 models and Qwen3 4B Thinking on Twitter/X posts. An appendix test found the larger Llama3 70B Instruct also fell after all junk training. Closed models like ChatGPT or Gemini were not tested. Drawn to illustrate."
  labels: ["Llama3 8B", "Qwen2.5 7B", "Qwen2.5 0.5B", "Qwen3 4B", "not tested"]

verbatim: []

acceptance:
  - "four stair flights are modelled, computed from figures.json models, and a frame with another count fails"
  - "the four flights and the pad span at least 340 px of the width at 432px"
  - "every flight's top is cropped by the image band so no height can be read"
  - "the empty pad has a visible outline and no stair"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "four flights can read as one mass, so they stand apart with dark gaps and their own casts"
```

```yaml
slide: 9
layout: FIGURE_SCALE
primary_image:
  subject: "the base height stair whole beside the all junk stair with its middle treads gone, a person at the broken stair's foot, the datum wall behind"
  rect: [180, 470, 900, 880]
  bleeds: [right, bottom]
accent: "#E0956A"
job: >
  Close on the consequence: the stair the base model climbs beside the one junk left, and the researchers' own call about data.

claims: [c1, c4, c33, c65, c68, c69]
numerals:
  - value_from: arc_cot_m1
  - value_from: arc_cot_base

data_in_art:
  figure: arc_cot_base
  drives: stair height of the whole stair, at 0.06 m per point

depth:
  eye: 1.7
  horizon: 600
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: -3}

composition:
  structure: >
    The camera stands front and to the right, as on the cover. The whole stair climbs on the left to the brass line, the broken
    one stands beside it shorter with its gap, and one person at the broken stair's foot gives the scale. The type
    sits in the dark sky at the upper left.
  bands: >
    Top third, the sky, the brass line and the hook. Middle third, the two landings and the gap in the broken
    flight. Bottom third, the feet of both stairs and the person, lit from the camera side, their shadows long on the caliche.
  focal: "the gap in the broken stair beside the whole one, lit"

art:
  technique: "physically based render of two chassis stair_flight models, the datum_wall and a kit person, staged in lastLight"
  why_this_technique: "the close sets the stair the base model climbs against the one junk left, at one scale"
  palette: "limestone, weathering steel, glass aggregate, brass"
  value_structure: >
    Lightest are the nosings and the brass line. Darkest are the sky and the ground beyond the pool. Frame median L*
    planned at 13.

type:
  hook: "\"We want to emphasize the importance of data\""
  dek: "Texas A&M's Zhengzhong Tu says companies and researchers focus too much on model architectures and training resources. His doctoral student Shuo Xing says recovery was very hard even with higher quality data. Testing larger closed models is still needed. Drawn to illustrate."
  labels: []

verbatim:
  - c69: "We want to emphasize the importance of data"

acceptance:
  - "both stairs are modelled, their rises computed from arc_cot_base and arc_cot_m1 at the deck scale"
  - "the whole stair stands at least 180 px tall at 432px"
  - "the broken stair is missing at least three middle treads, visible at 432 px"
  - "a person stands at the broken stair's foot under a fifth of the frame height"
  - "the brass datum is visible and sits at the whole stair's top"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "the kit person can read as a mannequin, so it stays small, three quarter away and lit from the camera side"
```
