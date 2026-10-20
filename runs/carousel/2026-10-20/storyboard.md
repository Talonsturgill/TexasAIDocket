# Storyboard, 2026-10-20
# "Four cameras in every room"

## The story, and what the fact check did to it

Houston Methodist put an image based AI system from Apella into Walter Tower's 15 room cardiothoracic suite at
Houston Methodist Hospital in December 2022 (c2, c4). Each operating room was fitted with four wall mounted cameras
(c3), and the system timestamps workflow steps and texts surgeons when a patient arrives, when the patient is draped
and when the case ends (c22, c23). The hospital's researchers published a study in the Journal of Imaging on June
27th, 2026 (c1). Its window ran 16 months, 6 before deployment and 10 after, through September 2023 (c5, c27).

The study estimates the deployment was associated with about 25 more cases a month, with a 95% interval of 8.3 to
41.0, about 7% over a baseline of about 339 (c6, c7). In the placebo permutation test Walter Tower ranked second of
11 units, an empirical p of 0.182, which the authors say does not reach conventional significance (c8, c9). They
call the rise associated with the deployment rather than caused by it (c10), and the estimate covers the cameras and
a change management program together, so it can't say which one did it (c11). Total operative minutes didn't move
significantly (c12). The hospital's blog says surgeons didn't operate faster and turnovers got shorter (c24), a claim
the study does not test. The hospital holds a minority equity interest in Apella (c13). An Apella employee ran the
original analyses (c14), a Houston Methodist analyst replicated them (c15), and the paper says Apella did not fund the
study (c16). The paper says video is kept up to 30 days and audio up to 7 (c17), recordings from incision to closure
open to three roles only (c18), and the surgeon is told when one is reviewed (c19). The record carries it as
tx-2026-0222.

**WHAT THE FACT CHECK CHANGED.**
- **The 5417 is the suite's case count over the window, never cases the cameras watched.** Installation began
  after the window opened. No frame says the cameras watched 5417 cases.
- **The 25 never stands alone.** Every surface that prints it says about, estimate, or carries the interval.
- **The cameras do record during surgery** (c18). No surface says they never see the operation. The deck says they
  stamp workflow events, which is what c22 says.
- **Turnover falling is the blog's claim** (c24), never a study finding. Frame 7 attributes it.
- **Audio** is the paper's account (c17). The blog says no audio is captured, so the close says "the paper says".
- **Apella's role** keeps the paper's own exception (c16): it did not fund the study, beyond its employee's analyses.

## Why this treatment, and what was grafted

Three directors pitched THE MEASURE (one sterile instrument container for each case, a wall of 339 in steel and 25
more with gold locks), THE LIMITS (the study's edges made into physical things: a slot, a recess, a fused shadow, a
groove of days) and THE ROOM (the empty table between cases under one lighthead, the minutes between operations,
a turnover crew in cap and mask, the deck ending at a camera's own mount).

- **From THE MEASURE, the unit and the evidence.** One rigid sterilization container stands for one case. It is a
  real object every operating room uses, its end is 0.28 by 0.15 m, and a wall of them at one scale makes 25 on 339
  a thin gold crown rather than a bar. The baseline wall (3), the crowned wall (4), the 25 lids in 41 taped floor
  bays (5), the disclosure on a clipboard (8).
- **From THE LIMITS, the cover, the turn and the close.** The reader stands where the wall camera stands and looks
  at an empty table between cases (1). The one shadow cast by a camera and a person together is "associated, not
  caused" (7). Eleven identical clamps with the second one gold is the placebo rank (6), a rank drawn at one height.
- **From THE ROOM, the turnover.** The close is the room between cases, first planned with a crew member wiping the table in a
  bouffant cap and mask, so the figure's face is covered as it is in life and the kit person doesn't read as a
  mannequin. Its corridor of fifteen doors was refused as too close to no. 47's corridor, and its quote about
  slotting cases like Tetris is in no claim.
- **Refused.** A patient on the table (no claim needs one and the cameras are not the story's surgeons). A model
  screen or a detection overlay (no output is published). A bar of 2/11 (a rank is never a bar). The Texas Medical
  Center skyline (the study is one suite). Any figure of the hospital's stores (the wall is a measure, and it says
  one container is drawn for each case).
- **The accent.** Dusk gold #E0956A, brand.yaml's, and it means ONE thing: Walter Tower's estimated added cases. The
  25 gold locks (4), the 25 gold lids (5), the gold handle ranked second (6), the one gold locked container waiting
  for the next case (9). Five frames. The cover's camera lamp is a cold white, never the accent.

## The world, and the laws that hold it

**FLOODLIT, INSIDE.** The chassis is `assets/js/deck/2026-10-20-suite.js` and every frame loads it. It declares
`sky: floodlit` with the key at azimuth -40, elevation 40: one cold white source from high on one side, the way an
operating room is lit, the room falling dark around its pool. A material relief reads the same light from the upper
left of its frame and every cast runs down and to the right. +x is east and +z south.

The argument for this world: an operating room has no sun and no dusk seam. It has one cold light over the table and
a room that goes dark past it. The last three worlds were nightSodium, a darkfield bench and lastLight brush country,
and none was an interior deck.

1. **Start dark.** Walls #1E2A2A in shadow, a floor pool where the subject stands, never a lit back wall.
2. **Type is light, on the dark field**, and every wash only darkens.
3. **Dusk gold is the only accent** and means the estimate.
4. Every standing thing gets `TXT.contact`, every spatial frame `TXT.weather` at low grime, because an operating
   room is clean and its wear is at the floor line.
5. **No patient, no surgery, no screen output.** The room is between cases.
6. **Nothing drawn is Walter Tower's real room or equipment.** Every frame says drawn to illustrate.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#08060F` | the DOM body behind the render |
| `accent` | `#E0956A` | dusk gold, the estimate: 4, 5, 6, 9 and the gold lock on 1 is NOT used |
| `hook` | `#ECE6DA` | light type on the dark |
| `dek` | `#D8CFC0` | the dek |
| `material` | `#C9CCCE` | brushed stainless, lids, table rails and clamps |

The world's materials: surgical green walls in shadow (#1E2A2A), grey green sheet vinyl floor, brushed 316 stainless,
anodised blue grey aluminium container bodies (#5D6F7C), black table pads, a pale grey blue sheet, ceil blue scrubs
(#5D8AA0), a cold 5000 K key (#EEF3F6) and one warm accent.

## The continuity devices

    CONTINUITY: CAMERA_MOVE, MOTIF_EVOLUTION, VALUE_ARC

1. **Camera move through one suite.** The wall camera close on its tile (1), the room from above as a model
   (2), a long lens square to the wall of containers, held still across 3 and 4, plan down onto the floor (5) and
   the towel (6), seated height at the tile wall (7), plan onto the steel table (8), and back into the room at the
   next case (9).
2. **Motif evolution, the container and its lock.** The camera that counts them (1), 339 steel locks
   in a wall (3), 25 gold locks crown it (4), 25 gold lids lie in 41 bays (5), one gold container waits for
   the next case under the camera (9).
3. **Value arc.** The cover's camera is lit on its dark tile; the walls of 3 and 4 are the brightest steel; the reliefs sit
   dark; the close is the darkest room with one pool.

## The rotation

    CLOSE_CROP  DIAGRAM  FIGURE_SCALE  FIGURE_SCALE  OBJECT_AND_CAPTION  GRID  FULL_BLEED  DOCUMENT  FULL_BLEED

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | CLOSE, eye 1.8 m, 1.1 m from the wall camera, fov 34, the lens turned three quarters toward the reader | the wall camera on its plate on the glazed tile wainscot under its stainless cap, a dark painted housing with a rounded body, an overhanging hood, a coated lens in a bezel ringed by IR emitters, a cable gland, a knuckle arm and a screwed wall plate, raked by the cold key from above with the plate's cast on the wall |
| 02 | AERIAL, an orthographic plan relief of one room as an architect's model | the room model, walls cut away and proud in matte card grey with lit tops, a table footprint and back table, the light's head swung aside, four gloss black camera brackets on four wall tops each casting a short shadow, a door swing engraved |
| 03 | WIDE, eye 1.9 m, 12 m back, fov 24, square to the wall | the wall of 339 sterile container ends, anodised blue grey bodies with stainless lid lips, black handles and steel locks, every end a separate unit with a dark seam, standing on a grey green vinyl floor with contact under the bottom row; a scrub nurse in ceil blue at its foot for size |
| 04 | WIDE, the same camera as 03 | the wall of 364 container ends, anodised blue grey bodies with stainless lid lips, black handles and latches, its top 25 ends anodised dusk gold all over across the top two rows, raked by the cold key against the unlit room, contact under the bottom row on the vinyl floor and scuffs at the floor line; the nurse unchanged |
| 05 | AERIAL, an orthographic plan relief of the floor | the vinyl floor with 41 taped bays in rows of six, 25 container lids in the first 25, ribbed stainless with gold anodised rims and locks, each throwing a cast down and right, a raised white tape stripe at the foot of every bay up to 8.3, ending a third of the way into bay 9 |
| 06 | MACRO, an orthographic plan relief of a green huck towel | eleven hemostatic clamps laid in one rank, stainless ring handles, box locks and serrated jaws, the second anodised gold all over, each casting onto the diamond weave, the second with gold ring handles |
| 07 | MEDIUM, eye 1.5 m, 4 m from a tile wall, fov 44 | the wall camera near on the left on a two piece boom arm, its pale housing lit by the key, turned on a turnover whiteboard on the glazed surgical green tile to the right, the board's gloss white face lit with a specular sheen, an aluminium frame casting onto the tile, lanes ruled in black and case blocks in four muted colours |
| 08 | CLOSE, an orthographic plan relief of the back table | a letter page with fibre tooth clipped by a steel clipboard clip to a brushed stainless table, the clip's cast across the top line, the steel going dark at the frame's edge |
| 09 | CLOSE, eye 1.25 m, 1.6 m from the back table, fov 40, the container turned three quarters | the sterile container with a gold anodised body waiting on the steel back table for the next case, its flush lid on a gasket line, perforated filter plates, latches, wire bail handles, ruled card and white tamper tag, its contact shadow on the steel; the back wall's camera rim lit high on the dark wall above the tiled wainscot behind |

Showstopper frame: 04, the wall of 364 container ends crowned by 25 gold locks with a person at its foot, depth from the person's contact and the wall's cast on the lit floor pool and the room gone black behind
Tonal arc: the camera dark on its tile on 1, the dark model on 2, the wall raked from the left on 3 and 4, the lit floor and towel of 5 and 6 the brightest pair, the turn on 7 back into the dark wall, the page on 8 the one bright object, the darkest room with one gold container on 9
VALUE CUT: frame 7. The deck turns from what the study counted to what it can't prove, and the camera beside the turnover board is that turn, two changes on one wall.

---

```yaml
slide: 1
layout: CLOSE_CROP
primary_image:
  subject: "a wall mounted operating room camera close in the lower middle of the frame, on its plate on a glazed tile wainscot under the stainless cap, its lens turned three quarters toward the reader"
  rect: [140, 680, 820, 560]
  bleeds: []
accent: none
job: >
  Put a camera in front of the reader and say what the story is, four AI cameras in each operating room of a Houston heart surgery suite.

claims: [c2, c3, c4, c6, c1]
numerals:
  - value_from: cameras_per_room
  - value_from: rooms

depth:
  eye: 1.8
  horizon: 300
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 3.48, Z: 0.2}

composition:
  structure: >
    The camera stands large in the lower middle on the room's right wall, which recedes to the right. The reader
    stands where the table would be and meets the lens. The wall above the tile's stainless cap is dark and plain, so the type sits on it.
  bands: >
    Top third, the dark wall above the camera with the hook. Middle third, the dek, the cap's lit edge and the camera's hood catching the
    key. Bottom third, the camera body, its knuckle arm and the screwed plate with its cast shadow on the glazed
    tile and its grout texture.
  focal: "the lens and hood under the key, the brightest area"

art:
  technique: "physically based render of the chassis room_camera on a TXT.interior wall, staged in the floodlit world"
  why_this_technique: "the camera is the story's new thing in the room, and a reader meeting its lens understands the watching before the numbers"
  palette: "dark painted housing, coated glass, a pale mount plate, surgical green grey tile, cold white light"
  value_structure: >
    Lightest are the hood's lit edge and the plate. Darkest are the wall and the lens. Frame median L* planned at 6.

type:
  hook: "Four cameras in every room"
  dek: "Houston Methodist put four wall cameras in each of the 15 operating rooms of Walter Tower's cardiothoracic suite. A study published in June ties its image based AI to more surgeries after it went live in December 2022. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the camera housing spans at least 360 px of the frame width at full size, and a frame with no camera fails this item"
  - "the lens, its bezel and the hood read at 432 px"
  - "the mount plate and arm show the camera is fixed to the wall"
  - "no patient, no person and no screen output in frame"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "the camera can read as a box on a stick, so it carries a rounded body, a hood, a bezel with emitters and a cable"
```

```yaml
slide: 2
layout: DIAGRAM
primary_image:
  subject: "one operating room as an architect's relief model seen from above, four camera brackets on its four walls, the table, the back table and the door swing"
  rect: [140, 480, 800, 870]
  bleeds: [bottom]
accent: none
job: >
  Show what the system is, four cameras in a room whose model stamps workflow events and texts the surgeon at three moments.

claims: [c3, c22, c23]
numerals:
  - value_from: cameras_per_room

data_in_art:
  figure: cameras_per_room
  drives: the number of camera brackets built on the room model's wall tops, one per camera

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The room model fills the lower two thirds, walls proud, the table at its middle, the door on the near wall.
    Four camera brackets sit on four wall tops, each with its own cast. Three leaders in the DOM run from labels to
    the door and the table.
  bands: >
    Top third, the dark board with the hook and dek. Middle third, the room's far walls, two camera brackets and the
    table. Bottom third, the near wall in relief with its lit top and cast shadow, the engraved door swing and two more brackets, crossed by the frame edge.
  focal: "the table at the model's centre, lit inside the walls"

art:
  technique: "material relief through txbench.js, an architect's model in matte card and gloss black"
  why_this_technique: "a plan model shows all four cameras and the room at once, which no single camera position can"
  palette: "matte card grey walls, a dark board, gloss black brackets, stainless table"
  value_structure: >
    Lightest are the wall tops facing the key. Darkest are the board and the casts. Frame median L* planned at 14.

type:
  hook: "Cameras log the workflow"
  dek: "The hospital says the cameras identify and timestamp workflow steps. It says the system texts the surgeon when a patient arrives, when the patient is draped and when the case ends. Drawn to illustrate."
  labels: ["patient arrives", "draped", "case ends"]

verbatim: []

acceptance:
  - "the room model owns at least half the frame height at full size"
  - "exactly four camera brackets stand on the model's wall tops, and a model with none fails this item"
  - "the table footprint sits inside the four walls"
  - "every wall casts a shadow down and to the right"
  - "each of the three leaders ends on the door or the table"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "a plan can read as a floor plan drawing, so the walls stand 18 px proud with lit tops and real casts"
```

```yaml
slide: 3
layout: FIGURE_SCALE
primary_image:
  subject: "a wall of 339 sterile instrument container ends stacked 13 across, a scrub nurse at its foot"
  rect: [0, 470, 1080, 880]
  bleeds: [left, right, bottom]
accent: none
job: >
  Set the baseline, about 339 cases a month in the suite before the cameras, one container for each case.

claims: [c7]
numerals:
  - value_from: baseline_cases

data_in_art:
  figure: baseline_cases
  drives: the number of container ends built in the wall, one per case, 13 across

depth:
  eye: 1.9
  horizon: 640
  cues: [RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: -1.0}

composition:
  structure: >
    A long lens square to the wall so every end is the same size. The wall fills the frame's lower two thirds and
    runs off both sides, one container alone on its top row so it reads as a count. The nurse stands at its foot
    under a fifth of the frame.
  bands: >
    Top third, the dark room with the hook and dek. Middle third, the wall's upper rows. Bottom third, the lower rows lit in the floor pool, the nurse's cast shadow and the wall's contact shadow on the vinyl texture.
  focal: "the wall's lit face in the pool"

art:
  technique: "physically based render, instanced chassis containers, a kit person, in a TXT.interior room"
  why_this_technique: "a count of real objects at one scale beside a person is a quantity a reader can feel, never a bar"
  palette: "anodised blue grey, stainless lid lips, black handles, steel locks, grey green floor, ceil blue scrubs"
  value_structure: >
    Lightest are the lid lips and handles in the pool. Darkest are the seams and the room. Frame median L* planned at 18.

type:
  hook: "About 339 a month"
  dek: "The paper puts the suite's baseline at about 339 cases a month. One container is drawn for each case. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the wall of container ends spans at least 520 px of the frame width and 560 px of its height at full size"
  - "the wall holds 339 container ends, 26 full rows of 13 and one more, and a frame with no wall fails this item"
  - "no lock on the wall is gold"
  - "every container end is separable from its neighbours at 432 px by a darker seam"
  - "a person stands at the wall's foot, shorter than half the wall at 0.157 m per end"
  - "the frame's median L* at 432px is 25 or lower"

risks:
  - "the wall can read as a stacked bar, so every end carries a handle, latches and a lock and the person stands beside it"
```

```yaml
slide: 4
layout: FIGURE_SCALE
primary_image:
  subject: "the same wall finished with 25 more container ends whose locks are dusk gold, the top two rows, a scrub nurse at its foot"
  rect: [0, 400, 1080, 950]
  bleeds: [left, right, bottom]
accent: "#E0956A"
job: >
  Draw the estimate at the scale of the baseline, about 25 more cases a month on about 339, a thin gold crown.

claims: [c6, c7]
numerals:
  - value_from: added_cases
  - value_from: rise_pct
  - value_from: baseline_cases

data_in_art:
  figure: added_cases
  drives: the number of gold locked container ends added on top of the baseline wall, finishing rows 27 and 28

depth:
  eye: 1.9
  horizon: 640
  cues: [RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: -1.0}

composition:
  structure: >
    The camera of frame 3 held still. The wall is complete at 13 by 28, and its top two rows carry gold locks that
    catch the key. Everything below is unchanged steel.
  bands: >
    Top third, the hook and the gold crown rows. Middle third, the steel rows. Bottom third, the lowest rows lit in the floor pool, the nurse and the contact shadow on the vinyl texture.
  focal: "the two gold locked rows, the warmest area"

art:
  technique: "physically based render, instanced chassis containers, a kit person, in a TXT.interior room"
  why_this_technique: "the before and after at one camera makes the size of the rise visible against the whole"
  palette: "as frame 3, with dusk gold locks"
  value_structure: >
    Lightest are the lid lips and the gold locks. Darkest are the seams and the room. Frame median L* planned at 18.

type:
  hook: "About 25 more a month"
  dek: "The study estimates the deployment was associated with about 25 more cases a month, 7% over a baseline of about 339. Gold marks the added cases. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the wall of container ends spans at least 520 px of the frame width and 560 px of its height at full size"
  - "exactly 25 container ends are anodised gold, all in the top two rows, and a frame with none fails this item"
  - "the wall is 13 across and 28 high"
  - "the steel rows below match frame 3's wall"
  - "the person stands at the wall's foot as on frame 3"
  - "the frame's median L* at 432px is 25 or lower"

risks:
  - "gold under a cold key can drift pink or brown, so the lock is the accent hex at low emissive, measured on the audition"
  - "364 instances can stall the render, so the wall is instanced per part"
```

```yaml
slide: 5
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "41 taped bays on a grey green vinyl floor in rows of six, the first 25 holding ribbed container lids with gold rims, a white tape stripe at the foot of the bays up to 8.3"
  rect: [0, 470, 1080, 880]
  bleeds: [left, right, bottom]
accent: "#E0956A"
job: >
  Show the 25 is an estimate whose interval runs from 8.3 to 41.0, one bay per case.

claims: [c6]
numerals:
  - value_from: added_cases
  - value_from: ci_low
  - value_from: ci_high

data_in_art:
  figure: ci_high
  drives: the number of taped bays, 41, with added_cases lids in the first 25 and the inlaid line at ci_low bays

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    Plan view onto the floor. Six rows of six bays and five more run down the lower half. The lids fill bays 1
    to 25 in reading order, the rest stand empty. A white tape stripe runs at the foot of every bay up to a third of the way into bay 9.
  bands: >
    Top third, the dark floor with the hook and dek. Middle third, the first two rows of lids. Bottom third, the fourth row's lids and the fifth row's single lid casting shadow, then the taped bays out to bay 41 with the vinyl's speckled texture in relief.
  focal: "the 25 lids, the brightest area"

art:
  technique: "material relief through txbench.js, five materials: vinyl, tape, stainless, gold, rubber"
  why_this_technique: "an interval is a range of counts, and empty bays a reader can count make the range concrete"
  palette: "grey green vinyl, pale tape, stainless lids, gold locks"
  value_structure: >
    Lightest are the lids' ribs facing the key. Darkest is the vinyl outside the pool. Frame median L* planned at 14.

type:
  hook: "Somewhere from 8.3 to 41.0"
  dek: "The 25 is the study's estimate. Its 95% interval runs from 8.3 to 41.0 more cases a month. Each bay is one case, and the white tape marks the low end. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the vinyl floor with its 41 taped bays and 25 container lids owns at least 640 px of the frame height, and a frame without the lids fails this item"
  - "exactly 41 taped bays and 25 lids, and a frame with no lids fails this item"
  - "the white tape stripe ends inside bay 9"
  - "bays 26 to 41 stand empty"
  - "every lid casts down and to the right"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "bays can read as a chart, so each lid carries ribs, filters and a lock and the floor carries vinyl speckle"
```

```yaml
slide: 6
layout: GRID
primary_image:
  subject: "eleven steel hemostatic clamps laid side by side on a green huck towel, the second anodised gold"
  rect: [0, 520, 1080, 830]
  bleeds: [left, right, bottom]
accent: "#E0956A"
job: >
  Draw the placebo test as a rank, Walter Tower second of 11 units, a p of 0.182 the authors call short of significance.

claims: [c8, c9]
numerals:
  - value_from: perm_units
  - value_from: perm_rank
  - value_from: perm_p

data_in_art:
  figure: perm_units
  drives: the number of clamps laid on the towel, 11, with the clamp at position perm_rank anodised gold

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    Plan onto the towel. Eleven identical clamps lie side by side, handles toward the reader, jaws away, all the same
    length because the paper gives a rank. The second from the left is anodised gold.
  bands: >
    Top third, the towel's weave in shadow with the hook and dek. Middle third, the clamps' jaws and box locks.
    Bottom third, the ring handles lit by the key with their cast shadow on the towel's woven texture, the gold clamp second from left.
  focal: "the gold clamp, the warmest area"

art:
  technique: "material relief through txbench.js, stainless clamps on a woven towel"
  why_this_technique: "a rank is drawn as equal objects in order, never as bars of different heights"
  palette: "surgical green huck towel, brushed stainless, one gold pair"
  value_structure: >
    Lightest are the clamps' upper edges. Darkest is the towel's weave between them. Frame median L* planned at 13.

type:
  hook: "Second of 11"
  dek: "In a placebo test against 10 donor sites, Walter Tower ranked second of 11, an empirical p of 0.182. The authors say it points the same way but does not reach conventional significance. One clamp per unit, and the gold one is Walter Tower. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the eleven clamps on the towel span at least 900 px of the frame width"
  - "exactly eleven clamps lie on the towel, and a frame with none fails this item"
  - "only the second clamp from the left is gold"
  - "all eleven clamps are the same length"
  - "every clamp casts onto the weave"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "eleven clamps can read as decoration, so the dek says one clamp is one unit of the test"
```

```yaml
slide: 7
layout: FULL_BLEED
primary_image:
  subject: "a wall camera on a boom arm turned on a turnover whiteboard on a glazed surgical green tile wall"
  rect: [120, 540, 960, 810]
  bleeds: [right, bottom]
accent: none
job: >
  Turn the deck, the rise is associated with the cameras and not shown to be caused by them, because a change program came with them.

claims: [c10, c11, c24]
numerals: []

depth:
  eye: 1.5
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, CAST_SHADOW, TEXTURE_GRADIENT, OCCLUSION]
  subject_at: {X: 0.4, Z: -2.8}

composition:
  structure: >
    The camera rides out from the tile wall on its boom arm, near and high on the left, its lens turned on the
    turnover board on the right half of the wall, so the two changes the study can't separate share one wall and one
    look.
  bands: >
    Top third, the dark upper wall, the camera and the hook. Middle third, the camera on its arm and the top of the
    board with its lanes. Bottom third, the board's lower lanes and its tray lit with their cast on the tile, the tile's grout and glaze texture and the arm's shadow.
  focal: "the lit board under the camera's look"

art:
  technique: "physically based render in a TXT.interior room with a tiled wall, the chassis room_camera on a boom arm and the chassis turnover_board"
  why_this_technique: "a camera and a program on one wall say two changes the study can't separate"
  palette: "surgical green glazed tile, grout, white board with muted case blocks, pale camera housing and stainless arm"
  value_structure: >
    Lightest is the board's face. Darkest is the upper wall. Frame median L* planned at 15.

type:
  hook: "Cameras plus a program"
  dek: "The authors call the rise associated, not caused. A change management program came with the cameras, and the study can't split the two. The hospital's blog says turnovers got shorter. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the tile wall with the board and the camera owns at least 700 px of the frame height, and the board at least 300 px of width"
  - "a wall camera and a turnover board share the wall, and a frame missing either fails this item"
  - "the camera's lens is turned toward the board, and no person is in frame"
  - "the tile's grout lines read at 432 px"
  - "the frame's median L* at 432px is 25 or lower"

risks:
  - "the board can read as a generic whiteboard, so its lanes carry case blocks and the camera stays in the same frame, turned on it"
```

```yaml
slide: 8
layout: DOCUMENT
primary_image:
  subject: "a letter page clipped by a steel clipboard clip to a brushed stainless back table, the paper's disclosure set on it"
  rect: [130, 450, 820, 900]
  bleeds: [bottom]
accent: none
job: >
  Say who ran the numbers, the hospital owns part of the vendor and the vendor's employee ran the first analyses.

claims: [c28, c13, c14, c15, c16]
numerals: []

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    Plan onto the table. The page fills the middle, clipped at its top edge, angled a degree in the drawing. The
    disclosure sentences sit on it as DOM type, square to the frame.
  bands: >
    Top third, the hook and the clip with its cast. Middle third, the page and its quoted lines. Bottom third, the
    page's lower half lit in relief over the brushed steel's grain texture going dark.
  focal: "the page, the brightest area"

art:
  technique: "material relief through txbench.js, paper, stainless clip and brushed steel"
  why_this_technique: "the paper's own words are the evidence, so the document is the image"
  palette: "paper, brushed stainless, the clip's polished steel"
  value_structure: >
    Lightest is the page. Darkest is the steel at the frame's edge. Frame median L* planned at 24.

type:
  hook: "The hospital owns part of Apella"
  dek: "Apella is the system's vendor. The paper says an Apella employee ran the original analyses and a Houston Methodist analyst replicated them. It says Apella did not fund the study and had no role beyond those analyses. Drawn to illustrate."
  labels: []

verbatim:
  - c13: "Houston Methodist Hospital holds a minority equity interest in Apella Technology."
  - c15: "These analyses were subsequently replicated independently by a Houston Methodist analyst using the same aggregated dataset."
  - c16: "Apella Technology did not fund the study and had no role in the study design, the interpretation of results, the decision to publish, or the preparation of the manuscript, beyond the analytical contribution described above"

acceptance:
  - "the page owns at least 600 px of the frame height at full size"
  - "a page is clipped to the table with its quoted lines legible at full size, and a frame with no page fails this item"
  - "the clip casts across the page's top edge"
  - "the type is square to the frame"
  - "the frame's median L* at 432px is 35 or lower"

risks:
  - "a pale page can lift the frame into mid tones, so the page is held to half the frame and the steel around it is dark"
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: "a sterile container anodised gold waiting on a steel back table between cases, a wall camera rim lit high on the dark wall above the tile behind"
  rect: [0, 860, 1080, 490]
  bleeds: [left, right, bottom]
accent: "#E0956A"
job: >
  Close on what a patient can know, who can open the surgery recordings and how consent works.

claims: [c18, c19, c26]
numerals:
  - value_from: access_roles

data_in_art:
  figure: cameras_per_room
  drives: the number of wall camera models built in the room, four, the back wall's in frame above the container

depth:
  eye: 1.25
  horizon: 700
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, TEXTURE_GRADIENT]
  subject_at: {X: 0.5, Z: 0.35}

composition:
  structure: >
    Low and close at the back table, the gold container fills the lower third on the steel with its contact shadow.
    Behind it the back wall's tile runs dark and the camera on it sits high and rim lit, its lens turned toward the
    operating table, out of frame to the left.
  bands: >
    Top third, the dark tile and the hook. Middle third, the dek and the camera on the tile. Bottom third, the gold
    container on the steel back table with its contact shadow.
  focal: "the gold container in the pool, the camera above it"

art:
  technique: "physically based render of chassis kit models in a TXT.interior room with a tiled wall"
  why_this_technique: "the room between cases is where the cameras keep watching, and the reader's question is about what they keep"
  palette: "as frame 1, dark surgical green tile, stainless steel, one gold container"
  value_structure: >
    Lightest is the container's lit face. Darkest are the walls. Frame median L* planned at 11.

type:
  hook: "Three roles can open surgery footage"
  dek: "Recordings from incision to closure open to three roles, and the surgeon is told of each review. The hospital's blog says signs are posted in its operating rooms and consent is folded into universal consent for care. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the gold container on the steel back table spans at least 400 px of the frame width in the bottom third, with its contact shadow, and a frame without it fails this item"
  - "a wall camera stands high on the wall above the tile behind the container, rim lit, and a frame with no camera fails this item"
  - "no person and no patient anywhere"
  - "the camera on the tile clears the dek by at least 30 px"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "the container can float off the steel, so its contact shadow is kept and the table edge runs under it"
```
