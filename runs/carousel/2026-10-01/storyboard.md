# Storyboard, 2026-10-01
# "Same pole. Two councils."

## The story, and what the fact check did to it

In 2023 the Legislature added $1 to Texans' auto insurance to fight catalytic converter theft (c15).
The Motor Vehicle Crime Prevention Authority turned that fee into at least 3,200 Flock plate reader
cameras (c17), putting at least $30 million of it toward the network (c16). Then the Governor ordered
every state agency to pause funding for Flock cameras, confirmed in a Tribune article dated August
28th (c12, c13, c14). Since then at least 14 cities and counties have shut off more than 900 Flock
cameras (c1). El Paso ordered every Flock fixed camera on city property removed within 60 days and
barred new contracts (c32, c33). Leander stopped using the cameras and the data on September 4th "in
response to community concerns" (c20, c21, c22). Kyle voted 6-1 to keep its contract without the
grant (c8, c9). College Station voted 4-2 to keep its two agreements (c23), and its chief says "You
can't afford the number of cops it would take" (c7), under rules that require reasonable suspicion
for any search and keep every search (c27, c28). Laredo's council voted 7-2 to put $1 million a year
for 165 cameras to a nonbinding referendum in May (c2, c3). League City's nonbinding question is on
the November 3rd ballot, called on August 11th, before the pause (c34, c35). College Station
describes the cameras as solar powered and LTE connected, photographing the rear of passing vehicles
day and night and sorting make, model and color (c25, c26).

The record carries this as tx-2026-0111 (the pause), tx-2026-0174 (El Paso), tx-2026-0180 (Leander),
tx-2026-0190 (College Station) and tx-2026-0048 (League City).

**WHAT THE FACT CHECK CHANGED.**
- **No date for the Governor's order.** The article says Thursday night. The deck says "in late
  August" (c1's words) and cites the article's date.
- **No date for Laredo's vote.** The deck says the council voted, never when.
- **900 is never drawn and never set against 3,200.** Two populations from two sources.
- **League City is never a reaction to the pause.** Its call came on August 11th.
- **No retention period for captures.** Only "all searches are retained indefinitely".
- **College Station's two amounts are never summed.**
- **No covered or bagged camera.** No claim says any camera was covered.
- **No county names** beyond Kendall and Harris, and the deck needs neither.

## Why this treatment, and what was grafted

Three directors pitched THE OBJECT, CONSEQUENCE AND SCALE and THE READER'S ROAD. All three chose blue
hour with the streetlight as the declared key, all three built the same `plate_reader` from Flock's
own specification, and all three refused to set 900 against 3,200. Three directors meeting there
blind is the room's strongest evidence.

The spine is THE OBJECT's: one pole, the same object on every frame, and its STATE carries the
argument. On, multiplied, switched off, unbolted, kept, and finally absent from the room that
decides it. Holding the object still and changing only its state is the fairest way to tell a split
decision. Nobody is cast as the villain.

- From THE READER'S ROAD: the green town limit sign as the accent and a continuity motif. It is real
  roadside material, it marks where a town's own say begins, and it can't be confused with the
  blue hour seam the way a warm accent would be. Also its close, "Your council decides this in
  public."
- From CONSEQUENCE AND SCALE: the empty council chamber, so the deck ends where the decision is made
  with nobody in it to read as a mannequin, and its discipline that a count is one rendered unit per
  camera.
- Refused: fourteen scissor viewports (one renderer, fourteen worlds, too much risk for one frame),
  a lit lens (the device has no visible light, and a glow is an invention a judge would name), a
  road map on a hood (a paper ground, and a cartographic claim the sources do not make), a vote
  board (invented furniture), a bagged camera (no claim).

## The world, and the laws that hold it

**A TEXAS ROADSIDE AT BLUE HOUR.** The chassis is `assets/js/deck/2026-10-01-plates.js` and every frame
loads it. It declares `sky: blueHour` and one light at azimuth -60, elevation 34. In blue hour the
declared light is the LAMP: a TxDOT cobra head streetlight stands where the key says on every
exterior frame, so its head and the shadows agree by construction. +x is east, -z is north. The
amber seam lies west and south west. The cameras work "during the day and night" (c25), and blue hour
is the hinge between the two, when the streetlight a town has always paid for comes on beside a
camera it now has to decide to pay for. The sky is one large softbox, so a 7 cm black pole holds its
silhouette.

The hero is `plate_reader`, a kit addition in the chassis, drawn to Flock's published Falcon
specification: a black 12 ft breakaway aluminum pole of 2.875 in OD on a cast base and a footing, two
21.25 by 28 in solar panels on the top, a camera body 8.75 by 5 by 2.875 in on band clamps aimed down
the lane at the rear of passing cars, and an LTE puck. Nothing ties it to the street but four bolts
and a radio. No frame prints a dimension. `city_limit_sign` is the second kit addition: a TxDOT
style green panel with a white border on two posts, blank, since the sources name no town to put on
it.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#1A2133` | the DOM body behind the render |
| `accent` | `#3E8F68` | the green of a town limit sign's sheeting. Only ever a sign. Frames 1, 4, 7 and 8 |
| `hook` | `#F2F1EC` | the hook, light on the blue sky |
| `dek` | `#D9DCE3` | the dek |
| `rule` | `#E6E7EA` | the site line, the source line and the counter |

The world's own colours are lit materials: asphalt blue black, a caliche shoulder gone grey violet in
the dusk, Ashe juniper near black, live oak olive, black powder coat, panel glass holding the cobalt
sky, the cool white of a 4000K LED cobra head, and the amber seam on the west horizon.

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE
    VALUE CUT: none

1. **Motif evolution.** The pole's state is the progress indicator: on (1, 2), multiplied (3), the
   nearest one standing dark beside a town line (4), unbolted on the ground beside its bare footing
   (5), off beside on (6), kept and multiplied (7, 8), and absent from the room that decides it (9).
   The green town limit sign rides with it, ahead on 1, fourteen on 4, at the corner of each kept
   field on 7 and 8.
2. **Camera move.** The camera circles the one pole: a low three quarter into the seam (1), pure side
   view (2), inside the front rank of the field (3), the driver's eye down the road (4), a standing
   eye over the footing (5), square on to the pair (6), the long lens on the two counts held at one
   height and one spacing so 32 and 165 read at one scale (7, 8), and then inside, from the public
   seats (9).

## The rotation

    FULL_BLEED  DIAGRAM  FULL_BLEED  SPLIT_HORIZON  FIGURE_SCALE  OBJECT_AND_CAPTION  GRID  GRID  FULL_BLEED

`TXLAYOUT.check` returns an empty list.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "one plate reader pole on a caliche shoulder beside a four lane road, seen low from behind its shoulder, its two solar panels a dark T against the amber seam, a streetlight lit behind it and a sedan leaving down the lane it watches"
  rect: [0, 430, 1080, 920]
  bleeds: [left, right, bottom]
accent: "#3E8F68"
job: >
  Stop the scroll on the object itself, and say the whole turn in the hook, the state stopped paying
  for the camera on the pole.

claims: [c12, c15, c17, c1]
numerals:
  - value_from: c15
  - value_from: c17

depth:
  eye: 0.8
  horizon: 900
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: -5}

composition:
  structure: >
    A low camera close behind the pole looks up past it toward the west seam, so the panels stand
    as one dark T against the brightest band of sky and the lane runs away beside it into the dusk.
  bands: >
    Top third, cobalt sky holding the hook and dek. Middle third, the panels, the camera head and
    the streetlight's lit head against the deepening blue. Bottom third, the seam on the horizon,
    the lane with the sedan's tail lamps, the green town limit sign far down the shoulder, the
    pole's breakaway base and its contact on the caliche.
  focal: "the camera head and its panels against the brightest part of the sky"

art:
  technique: "physically based render through txthree.js in the deck's blueHour world, kit road, streetlight, sedan and trees, the chassis's plate_reader"
  why_this_technique: "the story is a physical thing on a real roadside, and a black pole only holds its shape against a lit sky"
  palette: "cobalt zenith, amber seam, asphalt blue black, caliche grey violet, black powder coat, one green sign"
  value_structure: >
    Lightest is the seam and the streetlight head. Darkest is the pole and the panels against them.
    Frame median L* planned at 30.

type:
  hook: "The state stopped paying for this."
  dek: "A dollar added to Texas auto insurance in 2023 bought at least 3,200 Flock plate reader cameras. In late August the Governor ordered state agencies to pause the money."
  labels: []

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 22 and 40"
  - 'the hook reads "The state stopped paying for this."'
  - "the pole, its two panels and the camera head all read at 432px as one plate reader on a pole"
  - "the panels are darker than the sky directly behind them at 432px"
  - "a streetlight with a lit head stands on the frame"
  - "a sedan with lit tail lamps is in the lane, going away from the camera"
  - "a green town limit sign is visible on the shoulder, smaller than the pole"
  - "the pole's base touches the ground with a contact darker than the caliche beside it"
  - "no type crosses the panels or the camera head"

risks:
  - "a black pole at blue hour disappears into the sky, so the camera puts the panels against the seam and the lamp rims the pole"
```

```yaml
slide: 2
layout: DIAGRAM
primary_image:
  subject: "the same plate reader in pure side view on its shoulder, panels, LTE puck, camera on its band clamp and breakaway base all legible, the rear of a sedan in the lane below its aim"
  rect: [0, 360, 1080, 990]
  bleeds: [left, right, bottom]
accent: none
job: >
  Show what the thing is and what it records, in the city's own words, so every later frame is read
  as this object.

claims: [c25, c26, c27]
numerals: []

depth:
  eye: 1.9
  horizon: 1010
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL]
  subject_at: {X: 0, Z: -9}

composition:
  structure: >
    A side elevation of the pole, like a product drawing that happens to be a photograph, so each
    part has its own place in the frame and a leader can land on it.
  bands: >
    Top third, the hook and dek in the sky, then the panel pair with its puck. Middle third, the
    camera head on its clamp, its aim down the lane. Bottom third, the base and footing on the
    shoulder, the lane and the sedan's rear twelve metres down it, the horizon low.
  focal: "the camera head on its clamp, with the lane it watches running out of frame"

art:
  technique: "the render as a staged side view, with DIAGRAM leaders as DOM SVG ending short of every glyph"
  why_this_technique: "the claim is a description of parts, and a leader to the real part is the shortest way to say which part does what"
  palette: "cobalt sky lightening to the seam, asphalt, caliche, black powder coat, pale panel glass"
  value_structure: >
    Lightest is the low sky behind the pole. Darkest is the pole and camera body. Frame median L*
    planned at 30.

type:
  hook: "It runs on sunlight and a cell signal."
  dek: "College Station describes its cameras as solar powered and LTE connected. They photograph the rear of passing cars by day and by night."
  labels: ["solar-powered", "LTE-connected", "the rear of passing vehicles", "make, model, and color"]

verbatim:
  - c25: "solar-powered"
  - c25: "LTE-connected"
  - c25: "the rear of passing vehicles"
  - c26: "make, model, and color"

acceptance:
  - "the frame's median L* at 432px is between 22 and 40"
  - 'the hook reads "It runs on sunlight and a cell signal."'
  - "four labels are present and each leader ends within 24px of the part it names"
  - "the solar panels, the camera head and the breakaway base are each separately legible at 432px"
  - "the camera head points toward the sedan, not toward the viewer"
  - "no wire or overhead line runs to the pole"
  - "the pole stands on the ground with a contact darker than the shoulder"

risks:
  - "a side view flattens the panels into a line, so the panels face the camera at a three quarter on their own bracket"
```

```yaml
slide: 3
layout: FULL_BLEED
primary_image:
  subject: "a field of 3,200 identical plate reader poles in exact ranks on fall pasture at blue hour, the nearest at full detail, the far ranks a fine comb of panel Ts under the seam"
  rect: [0, 470, 1080, 880]
  bleeds: [left, right, bottom]
accent: none
job: >
  Make the dollar a size, one rendered pole for every camera the fee bought.

claims: [c15, c16, c17]
numerals:
  - value_from: c15
  - value_from: c17
  - value_from: c16

data_in_art:
  figure: cameras_funded_min
  drives: instance count, one rendered pole per camera, 80 files by 40 ranks

depth:
  eye: 2.4
  horizon: 560
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, TEXTURE_GRADIENT, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: -120}

composition:
  structure: >
    The camera stands just in front of the first rank and looks down the long axis toward the seam,
    so the count is felt as depth before it is read and the nearest pole sets the size of all of
    them.
  bands: >
    Top third, the sky holding the hook and dek. Middle third, the ranks shrinking into haze under
    the seam. Bottom third, the foreground ranks at full size, their panels lit by the sky and each
    base casting its contact shadow on the graded grass.
  focal: "the near ranks of poles, each with its own contact on the grass"

art:
  technique: "instanced render of 3,200 poles at true scale on the kit ground, the near ranks at full detail"
  why_this_technique: "a count only becomes a size when it stands somewhere, and one pole per camera keeps the count honest"
  palette: "fall pasture straw gone blue grey, black powder coat, pale panel glass, cobalt and amber sky"
  value_structure: >
    Lightest is the sky and the seam. Darkest is the near poles. Frame median L* planned at 30.

type:
  hook: "One dollar. At least 3,200 cameras."
  dek: "The Motor Vehicle Crime Prevention Authority put at least $30 million of the fee into Flock cameras, a Tribune analysis found."
  labels: []

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 22 and 40"
  - 'the hook reads "One dollar. At least 3,200 cameras."'
  - "the code draws exactly the figure's count of poles, 3,200, and window.__txDrawn says so"
  - "the nearest poles read as plate readers at 432px, panels and camera head both visible"
  - "the ranks recede to the horizon and the far ranks are lighter than the near ones"
  - "no type crosses a near pole's panels"

risks:
  - "3,200 poles in SwiftShader is slow, so the far ranks are instanced low detail and only the first ranks are full models"
```

```yaml
slide: 4
layout: SPLIT_HORIZON
primary_image:
  subject: "a straight two lane road seen from the driver's seat running to the seam, fourteen green town limit signs stepping down the right shoulder, and the nearest plate reader pole dark on the shoulder in the right foreground"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#3E8F68"
job: >
  Say what happened after the pause, in places rather than cameras, one sign for each city or county
  the reporting counts.

claims: [c1, c5, c6, c12]
numerals:
  - value_from: c1

data_in_art:
  figure: jurisdictions_off_min
  drives: sign count, one town limit sign per city or county along the shoulder

depth:
  eye: 1.15
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, OCCLUSION, CAST_SHADOW]
  subject_at: {X: 3.6, Z: -12}

composition:
  structure: >
    One straight horizontal cut at the horizon, the sky above for the type and the road below,
    so the signs step away down the shoulder as a count you can follow with the eye.
  bands: >
    Top third, the sky holding the hook and dek. Middle third, the cut, which is the horizon with
    the seam on it and the far signs shrinking into its haze. Bottom third, the foreground road's
    vanishing lines on lit asphalt, the near signs, and the near pole on the right shoulder cropped
    by the right edge, its shadow across the caliche.
  focal: "the near signs and the near pole on the right shoulder"

art:
  technique: "the render from a driver's eye with a long lens, kit road and the chassis's city_limit_sign and plate_reader"
  why_this_technique: "the count is of places, so it is drawn as the thing that marks a place on a Texas road"
  palette: "asphalt, caliche shoulder, highway green sheeting, black powder coat, cobalt and amber sky"
  value_structure: >
    Lightest is the seam on the cut. Darkest is the road and the near pole. Frame median L* planned
    at 26.

type:
  hook: "At least 14 cities and counties shut them off."
  dek: "More than 900 Flock cameras went dark after the state money was rescinded in late August. Plano, Robinson and Kendall County ended their contracts."
  labels: []

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 18 and 36"
  - 'the hook reads "At least 14 cities and counties shut them off."'
  - "the code draws exactly the figure's count of signs, 14, and window.__txDrawn says so"
  - "the near signs read as green signs with a white border at 432px"
  - "the horizon runs across the frame below the dek's last line"
  - "the near pole on the right shoulder reads as the same plate reader as frame 1"

risks:
  - "the far signs merge into one green line at thumb size, so the road carries a slight curve that separates them"
```

```yaml
slide: 5
layout: FIGURE_SCALE
primary_image:
  subject: "the plate reader unbolted and lying whole on a dry caliche shoulder beside its bare footing and four anchor bolts, a worker in a vest standing beside it for scale, a white work pickup behind, and a surveyor's rod with 60 graduations laid on the ground"
  rect: [0, 470, 1080, 880]
  bleeds: [left, right, bottom]
accent: none
job: >
  Show what a removal order does to the object, and the clock El Paso put on it.

claims: [c32, c33]
numerals:
  - value_from: c32

data_in_art:
  figure: el_paso_days
  drives: graduation count on the rod, one painted band per day

depth:
  eye: 1.6
  horizon: 560
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: -7}

composition:
  structure: >
    A standing eye over the footing so the four bare bolts and the pole lying beside them are read
    together, the worker giving the pole its size against a person.
  bands: >
    Top third, the sky holding the hook and dek. Middle third, the pickup and the dry horizon, the
    worker standing. Bottom third, the foreground caliche with the pole lying along it, the rod
    beside it, and the footing with its four bolts casting short shadows in the lamp light.
  focal: "the empty footing with its four bolts beside the lying pole"

art:
  technique: "the render with a kit person for scale and the chassis's plate_reader in its stub and lying states"
  why_this_technique: "a removal is a physical event, and a person beside the lying pole is what tells a reader how small the thing was"
  palette: "dry far west caliche, scrub, white work truck, a hi vis vest, black powder coat"
  value_structure: >
    Lightest is the sky and the vest. Darkest is the pole and the bolt shadows. Frame median L*
    planned at 28.

type:
  hook: "El Paso gave it 60 days."
  dek: "On September 15th the council directed the removal of every Flock fixed camera on city property, and no new contract with any provider of them."
  labels: []

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 20 and 38"
  - 'the hook reads "El Paso gave it 60 days."'
  - "the code paints exactly the figure's count of bands on the rod, 60, and window.__txDrawn says so"
  - "the pole lies on the ground with its panels and camera head still attached"
  - "the footing shows four bolts standing up and no pole"
  - "one person stands at true height beside the pole, lit from the camera's side"
  - "the person's face is not the subject and the person is smaller than a fifth of the frame height"

risks:
  - "a removal order is not a removal, so the dek says directed, and the frame is read as what the order calls for"
```

```yaml
slide: 6
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "two identical plate reader poles three metres apart on one curb, square on, the streetlight between and behind them, the left one dark and the right one with its streetlight lit beside it"
  rect: [0, 300, 1080, 760]
  bleeds: [left, right]
accent: none
job: >
  The turn. The same object under the same light, and two councils giving it opposite answers.

claims: [c20, c21, c22, c23, c7, c27, c28]
numerals:
  - value_from: c21
  - value_from: c23

depth:
  eye: 1.3
  horizon: 880
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL]
  subject_at: {X: 0, Z: -9}

composition:
  structure: >
    Square on and symmetric, so the two poles are read as one object twice and the only difference
    a reader can find is the words under each one.
  bands: >
    Top third, the hook. Middle third, the two poles, their panels against the sky, the streetlight
    between. Bottom third, the lit curb and asphalt in the foreground with each pole's contact
    shadow, the two captions over the dark road, Leander under the left pole and College Station
    under the right.
  focal: "the two camera heads at the same height, one under each set of panels"

art:
  technique: "the render, a symmetric staged pair, captions in the DOM under each pole"
  why_this_technique: "a split decision is fairest drawn as the same thing twice"
  palette: "concrete curb, asphalt, black powder coat, cobalt sky, a cool white cobra head"
  value_structure: >
    Lightest is the sky between the poles and the lamp. Darkest is the two poles. Frame median L*
    planned at 28.

type:
  hook: "Same pole. Two councils."
  dek: ""
  labels:
    - "LEANDER. Stopped September 4th, \"in response to community concerns.\""
    - "COLLEGE STATION. Kept, 4-2. \"You can't afford the number of cops it would take.\""

verbatim:
  - c22: "in response to community concerns"
  - c7: "You can't afford the number of cops it would take"

acceptance:
  - "the frame's median L* at 432px is between 20 and 38"
  - 'the hook reads "Same pole. Two councils."'
  - "two plate reader poles of identical height stand on one curb at 432px"
  - "the Leander caption sits under the left pole and the College Station caption under the right"
  - "both camera heads are at the same height and aim the same way"
  - "each pole touches the curb with a contact darker than the concrete beside it"

risks:
  - "symmetry reads as a diagram, so the streetlight stands off centre behind them and the curb runs in perspective"
```

```yaml
slide: 7
layout: GRID
primary_image:
  subject: "32 plate reader poles in four exact ranks of eight on a mown verge seen through a long lens, every one the same size, a green town limit sign at the near left corner"
  rect: [0, 520, 1080, 700]
  bleeds: [left, right]
accent: "#3E8F68"
job: >
  Show a town that kept paying without the state, at the size of the cameras its missing grant was
  for.

claims: [c8, c9, c10]
numerals:
  - value_from: c9
  - value_from: c8

data_in_art:
  figure: kyle_cameras
  drives: instance count, one pole per camera, eight files by four ranks

depth:
  eye: 7
  horizon: 560
  cues: [RELATIVE_SIZE, TEXTURE_GRADIENT, AERIAL, CAST_SHADOW]
  subject_at: {X: 0, Z: -120}

composition:
  structure: >
    A long lens from far back and a little up so every pole is one size and the count reads as a
    grid, the horizon held in the upper third.
  bands: >
    Top third, the sky holding the hook and dek. Middle third, the four ranks of poles, their panels
    a row of Ts. Bottom third, the foreground verge with its grass texture and the near rank's
    contact shadows, the green sign at the near left.
  focal: "the four ranks of panel Ts"

art:
  technique: "instanced render on a long lens, near parallel, held identical to frame 8"
  why_this_technique: "a count compared across two frames has to be drawn at one scale or the eye compares sizes instead of counts"
  palette: "mown verge, black powder coat, pale panel glass, highway green, cobalt sky"
  value_structure: >
    Lightest is the sky. Darkest is the poles. Frame median L* planned at 28.

type:
  hook: "Kyle kept paying, 6-1."
  dek: "Its $205,000 grant for 2026 has not arrived. $80,000 of it would help pay for these 32 Flock cameras."
  labels: []

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 20 and 38"
  - 'the hook reads "Kyle kept paying, 6-1."'
  - "the code draws exactly the figure's count of poles, 32, and window.__txDrawn says so"
  - "every pole reads at the same size at 432px"
  - "a green town limit sign stands at the near left corner"
  - "the horizon is in frame above the poles"

risks:
  - "a long lens from 7 m reads as looking down, so the horizon stays in the upper third and the sky holds the type"
```

```yaml
slide: 8
layout: GRID
primary_image:
  subject: "165 plate reader poles in eleven ranks of fifteen on a South Texas caliche lot with mesquite at the edges, through the same long lens, spacing and height as frame 7, a green town limit sign at the near left corner"
  rect: [0, 470, 1080, 760]
  bleeds: [left, right]
accent: "#3E8F68"
job: >
  The other answer, put to voters, at the same scale as Kyle so the swipe from 32 to 165 is one
  scale.

claims: [c2, c3, c4]
numerals:
  - value_from: c3
  - value_from: c2

data_in_art:
  figure: laredo_cameras
  drives: instance count, one pole per camera, fifteen files by eleven ranks

depth:
  eye: 7
  horizon: 520
  cues: [RELATIVE_SIZE, TEXTURE_GRADIENT, AERIAL, CAST_SHADOW]
  subject_at: {X: 0, Z: -120}

composition:
  structure: >
    Frame 7's camera, lens and spacing exactly, on a different ground, so the only thing that
    changes on the swipe is how many there are and where they stand.
  bands: >
    Top third, the sky holding the hook and dek. Middle third, the eleven ranks receding, mesquite
    at their edges. Bottom third, the caliche lot and the near ranks, the green sign at the near
    left.
  focal: "the near ranks of panel Ts"

art:
  technique: "instanced render on the long lens of frame 7, kit mesquite on a caliche ground"
  why_this_technique: "the same lens makes 165 a size beside 32 without a chart"
  palette: "pale South Texas caliche, mesquite olive, black powder coat, cobalt sky"
  value_structure: >
    Lightest is the sky and the caliche. Darkest is the poles and the mesquite. Frame median L*
    planned at 30.

type:
  hook: "Laredo will ask its voters."
  dek: "Its council voted 7-2 for a nonbinding referendum in May on spending $1 million a year to keep 165 cameras."
  labels: []

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 20 and 40"
  - 'the hook reads "Laredo will ask its voters."'
  - "the code draws exactly the figure's count of poles, 165, and window.__txDrawn says so"
  - "the poles are the same size at 432px as the poles on frame 7"
  - "mesquite stands at the edges of the lot"
  - "a green town limit sign stands at the near left corner"

risks:
  - "eleven ranks on a long lens merge into a band, so the spacing is wide enough that the near three ranks separate at 432px"
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: "an empty council chamber at blue hour seen from the public seats, a curved dais with nine chairs and microphones, the flags, the back of empty public seating in the foreground, the window behind the dais deep blue"
  rect: [0, 470, 1080, 880]
  bleeds: [left, right, bottom]
accent: none
job: >
  End where the decision is made, in a room a reader can walk into, and name the next dates.

claims: [c34, c35, c2, c3]
numerals:
  - value_from: c34
  - computed_by: "compute.py, laredo_yes plus laredo_no, the votes cast on c2, drawn as dais chairs and never printed"

data_in_art:
  figure: laredo_votes_cast
  drives: chair count at the dais, one chair per vote cast on Laredo's referendum call

depth:
  eye: 1.15
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, OCCLUSION, CAST_SHADOW]
  subject_at: {X: 0, Z: -6}

composition:
  structure: >
    From the third public row, the empty seats lead the eye down the aisle to the dais, so the
    reader is placed where a member of the public sits.
  bands: >
    Top third, the dark wall and window above the dais holding the hook and dek. Middle third, the
    dais, its chairs, the flags. Bottom third, the foreground rows of public seats, their backs lit
    from the dais and their shadows on the carpet leading down the aisle.
  focal: "the dais and its row of empty chairs"

art:
  technique: "the render in a room TXT.interior builds, kit hearing_dais, public_seating and flags_pair"
  why_this_technique: "the next step is a room, and a reader recognises a council chamber faster than any sentence about one"
  palette: "walnut dais, blue grey carpet, brass name plates, the deep blue of the window"
  value_structure: >
    Lightest is the lit dais front and the window. Darkest is the seat backs. Frame median L* planned
    at 26.

type:
  hook: "Your council decides this in public."
  dek: "League City votes on November 3rd, on a question its council called on August 11th. Laredo votes in May."
  labels: []

verbatim: []

acceptance:
  - "the frame's median L* at 432px is between 18 and 38"
  - 'the hook reads "Your council decides this in public."'
  - "the code draws exactly the figure's count of chairs at the dais, 9, and window.__txDrawn says so"
  - "the dais reads as a council dais at 432px"
  - "the room has walls and a floor, never a flat colour behind the dais"
  - "nobody sits in the chamber"

risks:
  - "an empty room reads as dead, so the dais is lit and the window behind it holds the blue hour"
```
