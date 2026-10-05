# Storyboard, 2026-10-05
# "12 of 120."

## The story, and what the fact check did to it

The UT System's health care AI laboratory, UT REAL Health AI (c1), launched in 2025 on legislative
approval and dedicated funding (c2), announced funding for 12 pilot projects (c6), chosen from 120
systemwide submissions (c7), more than $3.6 million in all (c8). They put AI into emergency triage
at seven UT hospital sites (c10, c47), six Epic tools at Dell Medical School (c15, c51), notes read
for suicide risk across more than 7 million records (c17), referral triage being deployed at UTMB
Galveston (c13, c49), and more. One entry, the no-show project (c16), states what it already
saved, more than 6,500 appointments and $900,000 at UTHealth Houston (c22), and it is set to expand
to UT Health San Antonio, where the page projects at least 15,000 a year (c23). The laboratory's
symposium is October 7th and 8th in Austin (c24).

The record carries this as tx-2026-0201.

**WHAT THE FACT CHECK CHANGED.**
- **The page is undated.** No surface says when the pilots were announced.
- **The 6,500 and the $900,000 are the project's own report.** Every surface attributes them.
- **15,000 is a projection** and always says so.
- **The Houston Chronicle's October 2nd reporting is out.** Its copy sits on a host that bars this
  project, so the 571 use cases and the unanswered questions appear nowhere.
- **The no-show lead is not printed.** The page spells the name one way and gives no institution.
- **The hospital is drawn.** No frame is a picture of a named campus, and frame 1's dek says each
  gold window stands for one funded pilot, not for a room where one runs.

## Why this treatment, and what was grafted

Three directors pitched THE KEPT APPOINTMENT, ONE SYSTEM MANY BUILDINGS and THE NIGHT SHIFT, and
all three chose blue hour and dusk gold without seeing each other. THE NIGHT SHIFT's facade is the
spine, because a hospital tower is the one Texas building whose face is already a grid a reader can
count, and a tower at blue hour is the building that never goes dark. Its 120 bays are the 120
submissions and twelve burn gold.

- From THE NIGHT SHIFT: the bay skin, the 2 by 6 gold block, the nurses' station with six screens,
  the close crop on a note at the deepest hour, the facade square on for the turn, and the close on
  frame 1's camera.
- From ONE SYSTEM, MANY BUILDINGS: the same tower type standing in other places, Galveston under
  palms and Dallas from above, so the system reads as a system, and the turn as the same facade
  with eleven golds put out.
- From THE KEPT APPOINTMENT: chairs as appointments at one scale, here one seat per 500 so the
  project's own Houston count and San Antonio's projection sit in one room as 13 and 30.
- Refused: a 6,500 chair lot (a memorial register, and a render budget), a page rendered as type on
  a screen or a corkboard (type is never rendered into a texture), a phone, bed and ambulance built
  new for one frame each, a terrazzo map, a loblolly stand built from nothing, and burnt orange,
  which is one university's livery on a story about eleven institutions.

## The world, and the laws that hold it

**A TEXAS HOSPITAL AT BLUE HOUR ON THE HUMID COAST.** The chassis is
`assets/js/deck/2026-10-05-wards.js` and every frame loads it. It declares `sky: blueHour`, tuned
with a grey blue Gulf haze and the engine's own glow kept on (fixed on October 3rd, so no. 39's
suppression is not needed), clouds off. In blue hour the declared light is the LAMP, the lot's LED
heads and the porte-cochere soffit, at azimuth -60 and elevation 32. Every cast in the deck runs
the same way. The calm value for type is the deep blue sky above the roofline, and type is light.

1. The hero is the kit `hospital` at ten floors, the kit's cap. The chassis lays a bay skin in the
   tower's ribbon glass, 10 floors of 12 bays (`bays_per_floor`), one emissive pane per bay.
2. Base bays are a cool corridor white at seeded low strengths, each behind glass whose roughness
   varies by seed, never a transmission pass (the craft refresh).
3. Gold bays are the accent and only ever mean a funded pilot.
4. Every standing thing gets `TXT.contact`, every frame `TXT.weather`, and type sits on the sky or
   on a dark wall, never on scatter.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#16202A` | the DOM body behind the render |
| `accent` | `#E0956A` | dusk_gold. A funded pilot's light: the twelve gold bays (1, 9), the station's six screens (3), the note screen (4) and the one gold bay left on the turn (6). Never a sky, a lamp, a person or a car |
| `hook` | `#F3F1EC` | light type on the blue sky |
| `dek` | `#E6E3DC` | the dek |
| `rule` | `#E6E3DC` | the site line, the source line and the counter |

The world's own colours are lit materials: warm precast near #A9A397, tinted ward glass near
#1C2731 at night, cool LED corridor white #DCE6E2, Gulf haze #5A6C80, lot asphalt #24272B, live
oak #34402F, St. Augustine in the islands, palm trunks on the Galveston boulevard.

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE, VALUE_ARC
    VALUE CUT: frame 5

1. **Motif evolution.** The gold bays are the argument's state. Twelve in a 2 by 6 block (1), the
   bays' light seen from inside as six gold screens (3) and one screen (4), eleven put out and one
   left (6), and twelve again on the close (9).
2. **Camera move.** Wide from the visitor lot (1), under the porte-cochere (2), into the station
   (3), close on one screen (4), raised over the waiting room (5), square to the facade on a long
   lens from the garage (6), out to a Galveston boulevard (7), up over a Dallas campus (8), and
   back to frame 1's camera exactly (9).
3. **Value arc.** Blue hour opens at mid dark on 1 and 2, the station steps down on 3, frame 4 is
   the deepest hour and the darkest frame, the waiting room lifts on 5, the facade holds on 6,
   Galveston and Dallas sit mid on 7 and 8, and the lot closes at the deck's lightest on 9.

## The rotation

    FULL_BLEED  FIGURE_SCALE  DIAGRAM  CLOSE_CROP  GRID  CLOSE_CROP  SPLIT_HORIZON  OBJECT_AND_CAPTION  FULL_BLEED

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | WIDE, standing eye 1.6 m at the far kerb of the visitor lot, horizon on the lower third | the hospital tower, warm precast with its bay skin of 120 lit panes behind glass of varied roughness, the 2 by 6 gold block on floors 7 and 8, grime at the podium base from TXT.weather and a contact where it meets the plaza |
| 02 | MEDIUM, standing eye 1.6 m on the drive under the porte-cochere | the porte-cochere soffit and its four precast columns, lit by its own downlights, the sedan at the kerb with its tyre polish and contact on the concrete apron, the glazed lobby glowing behind |
| 03 | MEDIUM, seated eye 1.2 m across a nurses' station | three desks end to end under six monitors, veneer tops worn at the edge, six screens glowing dusk gold, mesh chairs, the ribbon window on the left wall with the lot lamps below it |
| 04 | CLOSE, 0.7 m off one monitor | the monitor, a satin black bezel and aluminium stand lit only by its own gold screen, a contact where its base meets the worn veneer desk, dust along the bezel's lower edge, a mesh chair back cropped hard at the near left |
| 05 | WIDE, raised eye 2.6 m pitched down over a waiting room | two blocks of stacking chairs in charcoal vinyl on chrome, thirteen seated people seen from behind and thirty empty seats across an aisle, each block's contacts on a worn concrete floor, the lobby glazing onto blue hour |
| 06 | CLOSE, long lens from a garage deck 70 m off at 14 m | the tower face square on, precast spandrels and ribbon glass, eleven bays put back to cool white and one gold, the roof parapet and helipad edge against the sky |
| 07 | MEDIUM, standing eye 1.6 m on a Galveston boulevard | palms on the median and the hospital's podium and tower behind, salt grime on the precast base, the boulevard asphalt worn, palm trunks with contacts in sand coloured verges |
| 08 | AERIAL, 40 m up over a Dallas campus | the hospital tower, warm precast lit by the lot lamps from below and the sky from above, grime streaks under the roof units from TXT.weather, a contact where the podium meets the plaza, the Dallas skyline hazed beyond |
| 09 | WIDE, frame 1's camera to the centimetre | the hospital tower, warm precast with the same twelve gold bays in its skin, lit by the lot lamps and the sky, grime at the podium base and a contact on the plaza, the lot fuller with cars on fresh seeds |

Showstopper frame: 01, the tower at blue hour from its own lot, twelve gold rooms in a grid of 120, the amber seam behind its left shoulder and the lot lamps pooling on worn asphalt
Tonal arc: mid dark on 01 and 02, steps down on 03, darkest on 04 at the deepest hour, lifts on 05, holds on 06, mid on 07 and 08, and closes lightest on 09.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "a Texas hospital tower at blue hour seen from its visitor lot, 120 lit bays with twelve in dusk gold"
  rect: [0, 470, 1080, 880]
  bleeds: [left, right, bottom]
accent: "#E0956A"
job: >
  Stop the scroll on a hospital that never goes dark and put the whole story in one count, twelve
  gold rooms in a grid of 120, before a word is read.

claims: [c1, c6, c7, c8]
numerals:
  - value_from: c6
  - value_from: c7
  - value_from: c8

data_in_art:
  figure: submissions
  drives: bay count on the tower face, bays_per_floor across each of ten floors, with pilots setting the gold bay count

depth:
  eye: 1.6
  horizon: 930
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: -110}

composition:
  structure: >
    A standing eye at the far kerb of the visitor lot, the tower filling the middle of the frame
    so its grid of rooms reads as a count, the lot's lamps and parked cars leading in.
  bands: >
    Top third, the deep blue sky holding the kicker and the hook. Middle third, the dek, then the
    tower's upper floors with the gold block. Bottom third, the podium, the porte-cochere glow, the
    lot's lamps pooling on worn asphalt and a parked sedan cropped at the left edge.
  focal: "the 2 by 6 block of gold bays on the tower face"

art:
  technique: "physically based render through txthree.js in the deck's blueHour world, the kit hospital with the chassis bay skin, sedan, streetlight and live_oak"
  why_this_technique: "a lit tower is a grid of rooms a reader can count at a glance, so the count is the building"
  palette: "deep blue zenith, amber seam, warm precast, cool corridor white, dusk gold"
  value_structure: >
    Lightest is the lit bays and the porte-cochere glow. Darkest is the asphalt between lamp pools
    and the tinted glass. Frame median L* planned at 34.

type:
  hook: "12 of 120."
  dek: "The UT System's health care AI laboratory funded 12 pilot projects out of 120 submissions. The awards total more than $3.6 million. Each gold window stands for one funded pilot."
  labels: []

verbatim: []

acceptance:
  - "the tower's face shows 120 lit bays at full size, 12 across each of 10 floors, and a render with no bay skin fails"
  - "exactly 12 bays read dusk gold #E0956A in one 2 by 6 block at 432px"
  - "the hook reads '12 of 120.' in light type on the sky"
  - "a lamp pool lies on the asphalt under each lot streetlight, lighter than the asphalt between"
  - "the frame's median L* at 432px is between 26 and 42"

risks:
  - "the gold bays melt into the warm porte-cochere glow, so the base bays stay a cool white and the lobby glow stays below the block"
```

```yaml
slide: 2
layout: FIGURE_SCALE
primary_image:
  subject: "the hospital's porte-cochere at blue hour, a sedan at the kerb and a worker at the glazed lobby doors"
  rect: [0, 0, 1080, 760]
  bleeds: [left, right, top]
accent: none
job: >
  Put the reader at the door where an emergency comes in, at true human scale, for the pilot that
  works on triage and transfer across seven UT hospital sites.

claims: [c10, c47]
numerals:
  - value_from: c47

depth:
  eye: 1.6
  horizon: 880
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: -14}

composition:
  structure: >
    A standing eye on the drive lane under the canopy, the soffit's downlights running away from
    the camera, the lobby glass glowing at the end, one worker under a fifth of the frame for scale.
  bands: >
    Top third, the tower and a band of blue sky past the canopy edge. Middle third, the canopy
    soffit and its lights, the lit lobby glass, the sedan at the kerb and the worker. Bottom third,
    the hook and the dek over the dark asphalt drive, lit by the canopy's glow.
  focal: "the lit lobby glass at the end of the canopy"

art:
  technique: "physically based render, the kit hospital's own porte-cochere, sedan and person"
  why_this_technique: "a person at the door gives the scale of a room where a triage decision is made"
  palette: "deep blue sky, warm soffit downlight, precast columns, charcoal sedan, concrete apron"
  value_structure: >
    Lightest is the lobby glass and the soffit lights. Darkest is the drive's asphalt beyond the
    canopy and the sedan's tyres. Frame median L* planned at 13, rewritten after the type moved down onto the dark drive.

type:
  hook: "One AI assistant, seven UT hospital sites"
  dek: "At UT San Antonio, a pilot deploys an assistant called Leah for emergency triage and transfer decisions. The page says it was trained on more than 400,000 trauma cases."
  labels: []

verbatim: []

acceptance:
  - "a band of blue sky shows past the canopy edge in the top quarter, and the snapshot reports SKY IN FRAME"
  - "the worker stands under a fifth of the frame height, turned three quarters away"
  - "the sedan's tyres touch the apron with a contact darker than the concrete beside them"
  - "the frame's median L* at 432px is between 8 and 24"

risks:
  - "the canopy closes the sky out of frame, so the camera keeps the canopy edge in the top quarter"
```

```yaml
slide: 3
layout: DIAGRAM
primary_image:
  subject: "a night nurses' station, six monitors glowing dusk gold on three desks under a ribbon window"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#E0956A"
job: >
  Go inside one of the gold rooms and show what a pilot is made of, six tools on six screens,
  annotated in the page's own words.

claims: [c15, c51]
numerals:
  - value_from: c51

data_in_art:
  figure: epic_tools
  drives: monitor count on the station, each screen glowing in the accent

depth:
  eye: 1.2
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: -2.6}

composition:
  structure: >
    A seated eye across the station so the six screens read as a row of six, the ribbon window
    on the left wall carrying the lot lamps, two leaders in mono landing on two screens.
  bands: >
    Top third, the room's dark wall and ceiling holding the hook. Middle third, the dek and the
    window band. Bottom third, the veneer desks lit by the six gold screens, the mesh chairs casting soft shadow on the floor, and two leader lines landing on screens.
  focal: "the row of six gold screens"

art:
  technique: "physically based render, TXT.interior with the kit desk, monitor and office_chair, DOM SVG leaders in mono"
  why_this_technique: "six screens make six tools a count, and leaders say what two of them do in the page's words"
  palette: "dark grey blue walls, veneer desks, gold screen light, blue window"
  value_structure: >
    Lightest is the six screens. Darkest is the floor under the desks and the far wall. Frame
    median L* planned at 14, rewritten after pixel round 2 asked for a darker floor under the labels so the station reads as a room lit by its six screens.

type:
  hook: "Six tools inside Epic"
  dek: "At UT Dell Medical School a pilot implements six AI tools built into Epic. They automate lab result messaging and generate imaging summaries for patients."
  labels: ["AUTOMATE LAB RESULT MESSAGING", "PATIENT-FACING IMAGING SUMMARIES"]

verbatim:
  - c51: "lab result messaging"
  - c51: "patient-facing imaging summaries"

acceptance:
  - "exactly six monitors stand on the station and all six screens glow dusk gold"
  - "each leader ends within 24px of the screen it names"
  - "the room stands in TXT.interior and the snapshot reports ROOM IN FRAME"
  - "the frame's median L* at 432px is between 6 and 22"

risks:
  - "six gold screens over eight percent of the frame, so the camera stands back far enough that they stay under it"
```

```yaml
slide: 4
layout: CLOSE_CROP
primary_image:
  subject: "one monitor at the deepest hour, its screen glowing gold with unglyphed lines of a clinical note"
  rect: [200, 500, 680, 650]
  bleeds: []
accent: "#E0956A"
job: >
  Hold on one screen where a tool will read what a clinician wrote, the deck's darkest frame and
  the one pilot that reads words, in the future tense the page uses.

claims: [c17]
numerals:
  - value_from: c17

data_in_art:
  figure: notes_records_millions
  drives: note block count on the screen, one block of ruled lines per million records

depth:
  eye: 1.2
  horizon: 700
  cues: [RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: -0.7}

composition:
  structure: >
    A close camera 0.7 m off the monitor, the screen the only key, a chair back cropped hard at
    the near left, the dark window behind with two lot lamps.
  bands: >
    Top third, the dark wall and window holding the hook. Middle third, the dek and the monitor's
    top edge. Bottom third, the screen's gold glow, the stand and the desk edge.
  focal: "the gold screen"

art:
  technique: "physically based render, TXT.interior lit low, the kit monitor and office_chair, the screen an emissive canvas of ruled lines with no letters"
  why_this_technique: "a note is lines a reader recognises without reading, and no letters means no invented text"
  palette: "near black blue room, gold screen, a cool rim on the chair"
  value_structure: >
    Lightest is the screen. Darkest is the room around it. Frame median L* planned at 20.

type:
  hook: "It will read the notes."
  dek: "A Dell Medical School pilot will use large language models across more than 7 million patient records. It will look for signs of suicide risk."
  labels: []

verbatim: []

acceptance:
  - "the screen carries exactly 7 blocks of ruled lines and no letterforms"
  - "the screen glows dusk gold and is the lightest area of the frame"
  - "the frame's median L* at 432px is 28 or lower"

risks:
  - "the frame crushes to a void, so the room keeps a low interior light and two lot lamps in the window"
```

```yaml
slide: 5
layout: GRID
primary_image:
  subject: "a waiting room seen from above the seats, thirteen people seated in one block and thirty empty chairs across an aisle"
  rect: [40, 600, 1000, 470]
  bleeds: []
accent: none
job: >
  Draw the one stated result at one scale beside its projection, so the reader sees the project's
  own Houston count and San Antonio's projected count as seats in one room.

claims: [c16, c22, c23]
numerals:
  - value_from: c22
  - value_from: c23
  - computed_by: "out/2026-10-05/compute.py, seat_unit, the largest of 100, 250, 500 and 1000 dividing both counts"

data_in_art:
  figure: noshow_seats
  drives: occupied seat count, with sa_seats setting the empty seat count at the same seat_unit

depth:
  eye: 2.6
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: -6}

composition:
  structure: >
    A raised eye pitched down so both blocks count, the occupied block near left, the empty block
    across the aisle, the lobby glazing onto blue hour in the top band.
  bands: >
    Top third, the glazing and the blue sky outside holding the hook. Middle third, the dek and the
    far block of empty chairs. Bottom third, the seated block lit from the ceiling, each person's shadow pooled under the seat on worn concrete, and two labels beside the blocks.
  focal: "the block of thirteen seated people"

art:
  technique: "physically based render, TXT.interior with the kit public_seating and person, sky through the glazing"
  why_this_technique: "a seat is the size of an appointment everyone knows, so two counts at one scale are two blocks of seats"
  palette: "charcoal vinyl on chrome, worn concrete, the people's greys kept apart from the chairs, blue glazing"
  value_structure: >
    Lightest is the glazing and the ceiling lights. Darkest is the floor under the seats. Frame
    median L* planned at 12, rewritten after pixel round 2: the floor is the room's dark so the pale chairs and the seated people stand off it as countable blocks, and frame 5 is the declared value cut.

type:
  hook: "One entry states what it saved."
  dek: "The page credits the no-show project with more than 6,500 appointments saved at UTHealth Houston and cites no audit behind it. It projects at least 15,000 a year at UT Health San Antonio."
  labels: ["HOUSTON, AS THE PAGE STATES IT", "SAN ANTONIO, PROJECTED", "ONE SEAT = 500 APPOINTMENTS"]

verbatim: []

acceptance:
  - "exactly 13 people sit in the near block and exactly 30 empty seats stand in the far block"
  - "the label reads 'SAN ANTONIO, PROJECTED' beside the empty block"
  - "the glazing shows blue sky in the top band"
  - "the frame's median L* at 432px is between 6 and 22"

risks:
  - "the seated people read as mannequins, so they are seen from behind and under a fifth of the frame each"
```

```yaml
slide: 6
layout: CLOSE_CROP
primary_image:
  subject: "the tower face square on through a long lens, eleven bays put back to cool white and one left gold"
  rect: [0, 700, 1080, 650]
  bleeds: [left, right, bottom]
accent: "#E0956A"
job: >
  Turn the deck on the same facade, the eleven gold rooms put out and one left, because only one
  entry on the page states what it already saved.

claims: [c6, c22]
numerals:
  - computed_by: "out/2026-10-05/compute.py, pilots_without_savings_figure, pilots - 1"

data_in_art:
  figure: pilots_without_savings_figure
  drives: mark count, the gold bays put back to cool white in the 2 by 6 block, with pilots_with_savings_figure as the gold mark count left

depth:
  eye: 14
  horizon: 300
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, FORM_SHADING, OCCLUSION]
  subject_at: {X: 0, Z: -70}

composition:
  structure: >
    A long lens square on the tower from a garage deck, the bays flattened to one size so eleven
    and one are a count, the roof parapet and helipad edge against the sky in the top band.
  bands: >
    Top third, the sky above the parapet holding the hook. Middle third, the dek and the upper
    floors. Bottom third, floors 5 to 8 with the one gold bay's glow among the lit cool bays, and the garage parapet's concrete lip in the foreground.
  focal: "the one gold bay"

art:
  technique: "physically based render, the kit hospital and bay skin through a 22 degree lens"
  why_this_technique: "the same facade with the state moved is a before and after the reader can count"
  palette: "warm precast, cool corridor white, one dusk gold bay, deep blue sky"
  value_structure: >
    Lightest is the one gold bay and the cool bays. Darkest is the tinted glass between bays.
    Frame median L* planned at 22, rewritten after only the gold block was left lit.

type:
  hook: "Eleven entries, no saved count."
  dek: "Only the no-show entry states what it already saved, and the page cites no audit behind it. The other eleven describe the work, not what it saved."
  labels: []

verbatim: []

acceptance:
  - "exactly one bay reads dusk gold and the eleven others of the 2 by 6 block read cool white"
  - "the roof parapet stands against sky and the snapshot reports SKY IN FRAME"
  - "the frame's median L* at 432px is between 16 and 32"

risks:
  - "the long lens loses the sky, so the camera keeps the parapet in the top third"
```

```yaml
slide: 7
layout: SPLIT_HORIZON
primary_image:
  subject: "a hospital behind a palm lined boulevard in Galveston at blue hour"
  rect: [0, 760, 1080, 590]
  bleeds: [left, right, bottom]
accent: none
job: >
  Take the system to the coast for the one pilot the page says is being deployed, referral triage
  at UTMB Galveston, and say what it does in the page's verbs.

claims: [c13, c49]
numerals: []

depth:
  eye: 1.6
  horizon: 820
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION, FORM_SHADING]
  subject_at: {X: 10, Z: -95}

composition:
  structure: >
    A standing eye on a boulevard median, palms marching away, the hospital set back on the right,
    the sky split from the ground at the horizon so type rides the sky.
  bands: >
    Top third, the sky holding the hook. Middle third, the dek and the palm crowns. Bottom third, the hospital's lit podium in haze, the boulevard asphalt under lamp light and the palm trunks casting shadow on their verges.
  focal: "the lit podium and tower beyond the palms"

art:
  technique: "physically based render, the kit hospital on another seed, palm, road and streetlight"
  why_this_technique: "palms on a boulevard place the frame on the coast without a word"
  palette: "deep blue sky, salt pale haze, palm trunk grey, warm precast"
  value_structure: >
    Lightest is the lit bays and the lamp pools. Darkest is the palm trunks against the haze.
    Frame median L* planned at 33.

type:
  hook: "UTMB is deploying referral triage."
  dek: "In Galveston the tool reads the health record, assigns an urgency score and routes patients to a level of care."
  labels: []

verbatim: []

acceptance:
  - "at least four palms stand on the boulevard, each with a contact on its verge"
  - "the hospital stands beyond the palms and reads as one building at 432px"
  - "the frame's median L* at 432px is between 25 and 41"

risks:
  - "palms crowd the type band, so their crowns stay below the dek"
```

```yaml
slide: 8
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "a hospital tower and podium from 40 m up at blue hour, the Dallas skyline hazed beyond"
  rect: [0, 0, 1080, 700]
  bleeds: [left, right, top]
accent: "#E0956A"
job: >
  Show that two of the twelve already have a run behind them, from above a Dallas campus, and say
  how big each run is in the page's words.

claims: [c19, c20]
numerals:
  - value_from: c19
  - value_from: c20

depth:
  eye: 40
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: -90}

composition:
  structure: >
    An elevated camera over the lot, the tower at the centre right, the skyline hazed 4 km out on
    the horizon, the lot lamps pooling below.
  bands: >
    Top third, the sky and the hazed skyline holding the hook. Middle third, the dek and the
    tower's roof and helipad. Bottom third, the lit podium, the lot's asphalt with lamp pools and car shadows, and the near light poles in the foreground.
  focal: "the lit tower against the hazed skyline"

art:
  technique: "physically based render, the kit hospital, city_skyline dallas, streetlight, sedan"
  why_this_technique: "a raised camera shows the campus as a place in a city"
  palette: "deep blue sky, skyline glow, warm precast, lot lamp white"
  value_structure: >
    Lightest is the skyline glow and the lit bays. Darkest is the lot between pools. Frame median
    L* planned at 26, rewritten after pixel round 3 filled the ground around the tower with a dark marked lot.

type:
  hook: "Two more expand earlier platforms."
  dek: "A trial prescreening platform was validated on nearly 40,000 patients at UT Southwestern. An AI grading platform for medical school simulation exams has run for more than three years."
  labels: []

verbatim: []

acceptance:
  - "the Dallas skyline stands on the horizon hazed lighter than the tower"
  - "the horizon is in frame and the snapshot reports SKY IN FRAME"
  - "the frame's median L* at 432px is between 18 and 34"

risks:
  - "the camera looks at the ground, so the horizon sits on the upper third"
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: "the hospital tower from frame 1's camera, the same twelve gold bays, the lot fuller"
  rect: [0, 470, 1080, 880]
  bleeds: [left, right, bottom]
accent: "#E0956A"
job: >
  Close on the same building with the same twelve lit, and give the reader a dated next step and
  a question to take to a hospital.

claims: [c6, c24, c54]
numerals:
  - value_from: c24

data_in_art:
  figure: pilots
  drives: gold bay count, unchanged from frame 1

depth:
  eye: 1.6
  horizon: 930
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: -110}

composition:
  structure: >
    Frame 1's camera to the centimetre, the lot now fuller, one person walking in, the same twelve
    gold.
  bands: >
    Top third, the sky holding the hook. Middle third, the dek and the tower's upper floors.
    Bottom third, the lit podium, the fuller lot's cars on their shadows, lamp pools on worn asphalt and a person walking in under the light.
  focal: "the 2 by 6 block of gold bays"

art:
  technique: "physically based render, frame 1's scene with the state moved"
  why_this_technique: "the same camera says the building and the pilots are still there"
  palette: "as frame 1"
  value_structure: >
    Lightest is the lit bays and the lamp pools. Darkest is the asphalt. Frame median L* planned
    at 36.

type:
  hook: "Austin, October 7th and 8th"
  dek: "UT REAL Health AI holds its symposium there. Its page carries a link to register."
  labels: []

verbatim: []

acceptance:
  - "exactly 12 bays read dusk gold in the same 2 by 6 block as frame 1"
  - "more cars stand in the lot than on frame 1"
  - "the frame's median L* at 432px is between 28 and 44"

risks:
  - "the close reads as frame 1 again, so the lot fills and a person walks in"
```
