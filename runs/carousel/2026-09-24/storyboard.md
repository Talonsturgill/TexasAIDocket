# Storyboard, 2026-09-24
# "The pod picks the spot"

## The story, and what the fact check did to it

The Federal Aviation Administration is taking comment until October 11th (c2) on a DRAFT
environmental assessment of Zipline's request to begin commercial drone package delivery over
Amarillo, Austin, El Paso, Houston and San Antonio (c1). The record holds it as tx-2026-0186.

The AI in use is in one paragraph of the draft. At a delivery the aircraft holds a hover at 330
feet (c11, c19) and lowers a pod on a winch line. The pod "automatically controls its position
laterally and evaluates the delivery location", and keeps descending if the location is
clear (c17). "If the pod is unable to automatically identify the delivery target and evaluate its
suitability, an image is sent to an operator for real-time evaluation" (c18).

**THE DECK NEVER SAYS "ONLY".** Every brief and every director pitch said a person sees the yard
only when the machine can't decide. The fact check refused it: the draft never says only, gives
no rate, and puts the operator sentence in its visual effects section alone. So the deck says
what c18 says and says out loud that the draft gives no figure for how often it happens.

**THE DECK NEVER PRINTS 74.1 dBA.** All three directors built a noise frame on it. The fact check
rejected it: the row label says a 75 second hover and the figure is the average of 30 second
tests, and an SEL can't be set against the DNL 65 threshold. The noise frame uses the draft's
DNL finding at a stated rate (c21) against its own significance test (c20), and attributes the
no significant impact conclusion to the draft (c26).

**EVERY COUNT IS A MAXIMUM.** 220 Chargers, 4,400 Dropboxes, 220,000 deliveries a day (c7) are
ceilings the draft assesses, and no frame says flights flown. compute.py asserts the table's own
arithmetic: rows sum to the total, transits are three times deliveries (c8), and each metro's
delivery cap is its Chargers times 1,000 (c24). All three hold.

**THE DRAFT'S AUTHORSHIP IS STATED IN ITS OWN WORDS.** "Zipline prepared this draft environmental
assessment (draft EA) under the supervision of the FAA" (c6), and the noise report rests on
testing data "collected by Zipline" (c27). Copy says prepared, never wrote, because the listed
preparers are at a consultancy.

## Why this treatment, and what was grafted

Three directors pitched: the machine's eye, the street under it, and the open door. The deck is
THE OPEN DOOR's spine and world, because its concept puts the mechanism and the reader's own
recourse in one shape: a machine that consults a person by exception, and a comment window that
consults the public the same way, open now with a date on it.

- From THE STREET UNDER IT: the patio and the table as the place the document is read, and the
  count gathered on one lot "to be counted" with the set named.
- From THE MACHINE'S EYE: the straight down frame that IS the image an operator would be sent,
  with no invented interface on it.
- Refused from all three: "only", the 74.1 figure, a named operator room (the draft names none),
  a computed count of counties (the letter and its own total disagree).

## The world, and the laws that hold it

**A NORTH SAN ANTONIO BACKYARD AT GOLDEN HOUR IN LATE SEPTEMBER.** The chassis is
`assets/js/deck/2026-09-24-droneline.js` and every frame loads it. It declares `sky: 'goldenHour'`
and one light at azimuth -58, elevation 9, inside the preset's 4 to 14. Why this light: a
September evening in Bexar County is inside the draft's 7 am to 10 pm window, where it puts about
95 percent of flights (c10), so it is an honest hour for a delivery rather than a dramatic one.
The low sun throws the long shadows that make the pod's position over the lawn readable in one
glance, and it turns a hundred metres of line into a lit thread, which no other world can.

**ONE HERO OBJECT.** The delivery aircraft with its pod and winch line, modelled once. Span, length
and height come from figures.json, converted by compute.py from the draft's 7.8, 8 and 1.8 feet
(c14). The configuration between those dimensions, and the pod's size, are ILLUSTRATIVE, because
the draft gives dimensions and a propeller count (c13) and no drawing a reader can check. Every
frame that shows the aircraft close says so.

**THE LINE IS THE MOTIF AND THE ACCENT.** `#8FE0F0`, comal_lit from config/brand.yaml, the lit
line where water meets air, worn by the winch line and by nothing else. Its state carries the
deck: paid out to the pod over the lawn (1), the whole height at one scale (2), at the pod (3),
hanging into the pod's own view (4), reeled in (5, 6), holding over the next yard (7), crossing
the page (8), and gone (9). It is on four frames, 1, 2, 3 and 7, and it is a thin line, so it
stays well under 8 percent of any frame. Frame 4 looks down from where the line would hang and
frame 8 looks down at a table, so neither sees it.

**THE LINE IS DRAWN WIDER THAN IT IS.** A winch line is millimetres across and sub pixel at 100
metres. Its LENGTH is the draft's height, computed. Its rendered width is chosen so it survives a
432 px thumb, and frame 2's diagram says so.

**THE MUTE WORLD LAW.** No house number, no street sign, no maker's mark, no logo on the aircraft.
The yard stands for a kind of place, a San Antonio block in one of the five metros, and never a
real address.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#131A24` | the DOM body behind the render, and the shadowed lawn under the type on low frames |
| `accent` | `#8FE0F0` | the winch line only, frames 1, 2, 3, 7 |
| `hook` | `#F4F1EA` | the hook on every frame, on the sky |
| `dek` | `#E2E6EA` | the dek on every frame |
| `rule` | `#C9D2DA` | the site line, the source line and the counter |

The world's own colours are lit materials in the chassis: Edwards limestone and brick house
fronts, weathered cedar, live oak near black green, St. Augustine going straw, an off white
composite airframe.

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE, VALUE_ARC

1. **Motif evolution.** The line falls behind the roofs (1), runs the whole height (2), holds at
   the pod (3), is out of sight from where it hangs (4), is reeled in (5, 6), holds over the next
   yard (7), and is gone on the close (9), where a gate stands open.
2. **Camera move.** One neighbourhood from evolving positions: the street (1), off the block's
   corner (2), pod height (3), straight down (4), a dock at eye level (5), high over a lot (6),
   across the fence (7), over the table (8), low into the sun (9).
3. **Value arc.** The camera turns steadily toward the one declared sun, so frames step from lit
   faces (1 to 5) through side light (6 to 8) to a rim lit silhouette (9) with the light never
   moving.

## The rotation

    FULL_BLEED  DIAGRAM  CLOSE_CROP  FULL_BLEED  FIGURE_SCALE  GRID  SPLIT_HORIZON  DOCUMENT  FULL_BLEED

`TXLAYOUT.check` returns an empty list. Seven distinct, no TYPE_AS_OBJECT, FULL_BLEED and
CLOSE_CROP four between them, seven frames bleeding an edge.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "a back lawn at golden hour from a crouch on the patio: the pod hanging about two metres over the grass in front of a cedar fence with its gate shut, the neighbour's house and live oaks beyond, and the lit line rising from the pod out of the top of the frame toward an aircraft at the draft's height"
  rect: [0, 600, 1080, 750]
  bleeds: [left, right, bottom]
accent: "#8FE0F0"
job: >
  Put the reader in their own yard with one strange thing in it before a word of policy, so the
  machine is something hanging over a lawn they know rather than a category.

claims: [c1, c2, c11, c17, c19, c31]
numerals:
  - value_from: c11   # 330, the cruise and hover height in feet
  - value_from: c2   # October 11th, the comment deadline

data_in_art:
  figure: cruise.metres
  drives: the length of the line, which runs from the pod to the draft's hover height and leaves the frame

depth:
  eye: 0.5
  horizon: 940
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, OCCLUSION, CAST_SHADOW, FORM_SHADING]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The fence runs across the lower third with the house roof above it. The pod hangs on the
    right third just over the fence line and the line rises from it straight out of the top of
    the frame. The type sits in the open sky on the left.
  bands: >
    Top third, deep blue sky, the hook and the dek on the left, the line rising on the right.
    Middle third, the pod on its line, the oak's crown at the left edge, the house roofline.
    Bottom third, the cedar fence boards modeled by the low sun with the shut gate in them, and
    the lawn's grass blades lit from the side with their shadows falling toward the camera.
  focal: "the pod on the right third and the lit thread of the line rising from it"

art:
  technique: "physically based render through txthree.js in the declared goldenHour world, sky, grass ground, scatter kept off the type, contact and weather"
  why_this_technique: >
    The claim is a physical arrangement in a real place, a machine a hundred metres up and a pod
    over a lawn. Only a render at true height can make the distance between them the thing a
    reader feels.
  palette: "deep blue zenith, warm haze at the horizon, straw lawn, near black oak, silver cedar, off white pod and aircraft, the accent line"
  value_structure: >
    Lightest is the horizon glow at the end of the street and the lit house fronts. Darkest is
    the oak crowns' shade and the foreground verge. The type sits on the sky's mid blue. The line
    is a thin bright stroke across it.
  motion: "from the pod up the line out of the frame, then left into the type"

type:
  kicker: "FAA draft, open for comment"
  hook: "The pod checks the spot"
  dek: "Zipline wants FAA approval to fly delivery drones over Houston, San Antonio, Austin, Amarillo and El Paso. The FAA takes comment until October 11th."

verbatim: []

acceptance:
  - "the frame reads \"The pod checks the spot\""
  - "the line runs from the pod to figures.json cruise.metres above the lawn, 100.584 m, and leaves the top of the frame"
  - "the pod reads as one object at 432 px, hanging clear of the fence"
  - "the line is the accent #8FE0F0 and nothing else on the frame is"
  - "no grass blade, leaf or line crosses the hook or the dek"

risks:
  - "the aircraft is out of frame at its true height. The line carries the frame, and frame 5 carries the aircraft's shape"
```

```yaml
slide: 2
layout: DIAGRAM
primary_image:
  subject: "the block from off its end at about the aircraft's own height: two rows of houses back to back, fenced yards, live oaks and two streets, the aircraft holding over one yard and its line falling the whole height between the roofs to the pod"
  rect: [0, 360, 1080, 990]
  bleeds: [bottom, left, right]
accent: "#8FE0F0"
job: >
  Make 330 feet a height a reader can read against a house and a person, at one scale, so the
  distance the decision is made across is measured rather than described.

claims: [c11, c19, c17]
numerals:
  - value_from: c11   # 330, the height in feet
  - value_from: c19   # 75, the hover in seconds

data_in_art:
  figure: cruise.metres
  drives: the aircraft's height on the frame at the same metres per pixel as the house and the person

depth:
  eye: 50
  horizon: 1210
  cues: [RELATIVE_SIZE, AERIAL, FORM_SHADING, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A long lens from far off the side flattens the scene to one scale. The ground line sits low,
    the house and the oak stand on it at the right, a person stands beside the pod at the foot of
    the line, and the line climbs the full height of the frame to the aircraft at the top. Mono
    leaders in the DOM mark the height and the hover.
  bands: >
    Top band, the sky, the hook and the dek, and the aircraft on the right with its leader. The
    middle, the horizon in haze and the rows of houses and oaks receding. Bottom band, the roofs
    and yards near the camera in raking light, the pod at the foot of the line with its leader.
  focal: "the lit line falling the whole height of the frame, from the aircraft to the pod"

art:
  technique: "physically based render of a whole neighbourhood from off its corner, DOM SVG leaders that land on the aircraft and the pod"
  why_this_technique: >
    A height means something only against the ground it is over. A neighbourhood in one view,
    rather than a chart, is what shows a reader how far above their roofs the decision sits.
  palette: "the sky's gradient top to bottom, the house and oak in warm side light, the accent line"
  value_structure: >
    Lightest is the haze on the horizon and the lit roofs. Darkest is the upper sky, under a
    light atmospheric wash where the type sits, and the shaded yards. The line is the one
    continuous bright stroke.
  motion: "down the line from the aircraft to the pod"

type:
  kicker: "The whole height, one block"
  hook: "It holds at 330 feet"
  dek: "The pod goes down on a line and back up while the aircraft hovers, for about 75 seconds. The aircraft, the pod and the line are drawn larger than they are."

verbatim: []

acceptance:
  - "the frame reads \"It holds at 330 feet\""
  - "the aircraft sits at cruise.metres above the ground and the line runs from it to the pod"
  - "a leader labelled with the height ends at the aircraft and a leader labelled with the hover ends at the pod"
  - "the dek says the aircraft, the pod and the line are drawn larger than they are, the houses stay at true scale, and the aircraft and the pod are each drawn large enough to find at 432 px"

risks:
  - "the aircraft is small at this distance. The leader finds it, and frame 5 carries its shape"
```

```yaml
slide: 3
layout: CLOSE_CROP
primary_image:
  subject: "the pod at detail scale on the end of its line a metre over the lawn, seen from low on the lawn so the grass it is judging fills the bottom of the frame, the fence, a house and an oak soft behind it in the low sun"
  rect: [120, 330, 960, 1020]
  bleeds: [right, bottom]
accent: "#8FE0F0"
job: >
  Show the thing that decides. The draft's AI is not a model card, it is this object steering
  itself sideways and judging a patch of grass.

claims: [c17]
numerals: []

data_in_art:
  figure: cruise.metres
  drives: the length of the line, which runs from the pod up to the draft's hover height and leaves the top of the frame

depth:
  eye: 0.6
  horizon: 893
  cues: [FORM_SHADING, CAST_SHADOW, AERIAL, OCCLUSION, RELATIVE_SIZE]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The pod fills the middle of the frame, cropped by the right edge, turned a little toward the
    step, its line leaving through the top. The yard falls out of focus behind it into the warm
    haze. The type sits in the calm upper left.
  bands: >
    Top third, the sky and the out of focus oak, the hook and the dek. Middle third, the pod's body
    and fins, lit on the sun side. Bottom third, the cedar fence's pickets in raking light, their long shadows, and the
    texture of the grass along the fence's foot, out of focus.
  focal: "the pod's lit shoulder and the band around its middle"

art:
  technique: "physically based close render of the chassis pod, weathered at its base, against the declared world"
  why_this_technique: >
    The claim is what a physical object does in a yard, so the frame shows the object in the yard
    close enough to read its shape and the grass it is judging.
  palette: "off white pod, dark band and fins, straw lawn, warm haze, the accent line"
  value_structure: >
    Lightest is the pod's sun side. Darkest is the band, the fins and the shadow on the grass. The
    background sits in the mid tones so the pod separates.
  motion: "down the line into the pod, then down to its shadow"

type:
  kicker: "What the draft describes"
  hook: "It judges the yard"
  dek: "On the way down the pod steers itself sideways and evaluates the spot. If the spot is clear, it keeps descending."

verbatim: []

acceptance:
  - "the frame reads \"It judges the yard\""
  - "the pod is cropped by the right edge and its line leaves through the top"
  - "the pod hangs over the lit lawn it is judging, and the lawn fills the bottom band of the frame"
  - "the dek says the pod keeps descending if the spot is clear, which is c17's condition, and nothing about an operator"

risks:
  - "a close pod against a soft yard can read as a product shot. The fins and the dirt at its base keep it a working object"
```

```yaml
slide: 4
layout: FULL_BLEED
primary_image:
  subject: "the yard seen straight down from a few metres above, the kind of image the draft says would be sent to an operator: the lawn, the cedar fence across it with its long evening shadow, the back step and the patio, and the pod itself below the camera on its line, coming down over the grass"
  rect: [0, 0, 1080, 1350]
  bleeds: [top, bottom, left, right]
accent: none
job: >
  Put the reader in the operator's chair for the one sentence in the draft where a person enters,
  and say plainly that the draft gives no figure for how often.

claims: [c18]
numerals: []

depth:
  eye: 4
  horizon: -1
  cues: [CAST_SHADOW, FORM_SHADING, RELATIVE_SIZE, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A straight down view. The fence runs across the middle, and its long evening shadow covers the
    lawn beyond it at the top, where the type sits. Below it the lit lawn, the shadow of the house,
    and the back step and patio at the bottom edge.
  bands: >
    Top band, the fence's long shadow over the lawn beyond it, the hook and the dek. The middle,
    the fence itself across the frame and the lit lawn below it. Bottom band, the back step's lit
    concrete with the texture of its broom finish, the patio beside it, and the long shadow of the
    house crossing both.
  focal: "the lit lawn below the fence, the open ground the pod would judge"

art:
  technique: "physically based render looking straight down in the declared world, the ground's own tooth and scatter as the whole image"
  why_this_technique: >
    The claim is about an image of a yard, so the frame is that image. No reticle and no interface
    are drawn, because the draft describes none.
  palette: "straw lawn, silver fence, pale concrete, long cool shadows, no accent"
  value_structure: >
    Lightest is the concrete step in the sun. Darkest is the fence's shadow band at the top, where
    the type sits. The lawn carries the mid tones.
  motion: "from the shaded band down across the fence to the lit lawn"

type:
  kicker: "The operator step"
  hook: "When it can't tell"
  dek: "If the pod can't identify the target and judge it, the draft says an image goes to an operator for real-time evaluation. The draft gives no figure for how often."

verbatim:
  - "an image is sent to an operator for real-time evaluation"

acceptance:
  - "the frame reads \"When it can't tell\""
  - "the camera looks straight down and the fence's shadow covers the top half, under the type"
  - "no reticle, box, crosshair or interface element is drawn on the image"
  - "the dek contains no word that implies a rate, not only, rarely or usually"

risks:
  - "a lawn from above can read as texture. The fence corner and the step are what make it a yard"
```

```yaml
slide: 5
layout: FIGURE_SCALE
primary_image:
  subject: "the aircraft whole, hung under a charger dock by its fin as the draft describes, at eye level on a concrete pad behind a strip centre, a standing person a pace off the wingtip at the same depth, both on the one pad, in low side light"
  rect: [180, 440, 760, 700]
  bleeds: []
accent: none
job: >
  Give the machine a size a reader can stand beside. The draft's dimensions build it, and a person
  stands next to it.

claims: [c12, c13, c14, c30]
numerals:
  - value_from: c13   # 63 pounds and the 8 pound payload
  - value_from: c14   # 7.8 and 8 feet, wingspan and length

data_in_art:
  figure: aircraft.span_m
  drives: the aircraft's wingspan, length and height in the model, beside a person at true scale

depth:
  eye: 1.6
  horizon: 717
  cues: [RELATIVE_SIZE, FORM_SHADING, CAST_SHADOW, OCCLUSION, AERIAL, LINEAR_PERSPECTIVE]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The dock arm holds the aircraft at about shoulder height beside the tower, the person stands
    a pace off its wingtip, and the strip centre's blank back wall runs off the left edge. The sky
    above holds the type.
  bands: >
    Top third, the sky, the hook and the dek. Middle third, the aircraft on its dock, the person,
    the tower. Bottom third, the concrete pad in the foreground with saw joints and grit texture, the
    tower's and the person's long shadows running east across it, lit on its sun side.
  focal: "the aircraft's lit wing edge beside the person's shoulder"

art:
  technique: "physically based render of the chassis aircraft beside a person at true scale"
  why_this_technique: >
    A size means nothing until it stands beside something a reader knows. The person and the dock
    are the ruler.
  palette: "off white composite, galvanised tower, pale concrete, the strip centre's buff block, no accent"
  value_structure: >
    Lightest is the airframe's sun side. Darkest is the tower's shadow side and the sky's zenith
    where the type sits.
  motion: "along the wing to the person"

type:
  kicker: "Illustrated to the draft's dimensions"
  hook: "About 63 pounds, fully loaded"
  dek: "The draft gives a wingspan of about 7.8 feet, a length of about 8 feet and a maximum payload of 8 pounds. It calls the aircraft highly automated."

verbatim: []

acceptance:
  - "the frame reads \"About 63 pounds, fully loaded\""
  - "the aircraft's span, length and height in the model are figures.json aircraft.span_m, length_m and height_m"
  - "a standing person is beside the aircraft on the same ground"
  - "the kicker says the drawing is illustrated to the draft's dimensions"
  - "no accent #8FE0F0 appears, because the line is reeled in"

risks:
  - "a reader who knows the real aircraft will see a different rotor layout. The kicker says it is illustrated"
```

```yaml
slide: 6
layout: GRID
primary_image:
  subject: "the draft's maximum of charger towers gathered on one caliche lot to be counted, in five blocks for the five metros, in one rank from one front line, every block five masts wide so its depth is its count, each on its own asphalt pad, seen from the sun's side at golden hour with the hazed horizon above"
  rect: [0, 570, 1080, 410]
  bleeds: []
accent: none
job: >
  Make the draft's ceiling countable, and name the set so a reader does not read a forecast.

claims: [c7, c24, c34]
numerals:
  - value_from: c7   # 220 Chargers, 4,400 Dropboxes and 220,000 deliveries a day, the totals row

data_in_art:
  figure: chargers.houston
  drives: the number of towers built in each of the five blocks, from each metro's row

depth:
  eye: 60
  horizon: 120
  cues: [RELATIVE_SIZE, CAST_SHADOW, FORM_SHADING, AERIAL, LINEAR_PERSPECTIVE]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    Five blocks of towers in a row across the lot, largest to smallest from left, each with its
    metro's name set under it in the DOM. A long lens keeps every tower the same size. The type
    sits in the sky and haze above the far edge.
  bands: >
    Top band, the far haze and sky, the hook and the dek. Middle band, the five blocks. Bottom
    band, the names and the source line on the lot's shadowed caliche.
  focal: "the two large blocks at the left, Houston and San Antonio"

art:
  technique: "physically based render of instanced chassis chargers on a caliche ground at a long focal length"
  why_this_technique: >
    A count wants a grid a reader can count, at one scale. The towers are drawn as towers so the
    count is of the thing the draft names.
  palette: "galvanised towers, caliche lot, long east shadows, no accent"
  value_structure: >
    Lightest is the lot in the sun. The towers are mid tones with dark cast shadows. The sky at the
    top is the calm ground for the type.
  motion: "left to right across the blocks"

type:
  kicker: "The draft's maximum, not flights flown"
  hook: "Up to 220 Chargers"
  dek: "Across Amarillo, Austin, El Paso, Houston and San Antonio the draft caps the proposal at 4,400 Dropboxes and 220,000 deliveries a day. Each mast stands for one Charger, which the draft says would typically be 36 docks in three towers of twelve."

verbatim: []

acceptance:
  - "the frame reads \"Up to 220 Chargers\""
  - "the blocks hold 65, 65, 30, 30 and 30 towers, from figures.json metros, and their total equals total.chargers"
  - "each block is named for its metro in DOM type"
  - "the kicker names the set as the draft's maximum"

risks:
  - "220 towers on one lot can read as one hub that exists. The dek says drawn together here to be counted"
```

```yaml
slide: 7
layout: SPLIT_HORIZON
primary_image:
  subject: "across the cedar fence from the neighbour's lawn, the pod holding over the next yard on its line, a person standing in their own yard, the houses and oaks in the low sun"
  rect: [0, 300, 1080, 480]
  bleeds: [left, right]
accent: "#8FE0F0"
job: >
  Say what the draft found about noise, in its own metric and against its own test, beside the
  person the test is about.

claims: [c21, c26, c29, c35]
numerals:
  - value_from: c21   # 400 deliveries a day and DNL 58.1 dB
  - value_from: c35   # 59.7 dB and the 1.5 dB rise

depth:
  eye: 1.6
  horizon: 405
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, OCCLUSION, CAST_SHADOW, AERIAL, FORM_SHADING]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The render holds the top of the frame down to a straight cut: the fence runs across, the
    neighbour stands on this side, the pod hangs over the far lawn with its line rising out of the
    top. Below the cut, on the flat dark of the neighbour's shaded lawn, two bars from zero in one
    hue set the draft's figure against the FAA's test.
  bands: >
    Top third, the sky, the pod's line and the far houses in haze. Middle third, the fence, the
    person, the pod over the far lawn. Bottom third, below the cut, the neighbour's lawn in
    shadow with its grass texture fading into the dark, the two bars, the hook and the dek.
  focal: "the pod over the far lawn, beside the neighbour's head"

art:
  technique: "physically based render above the cut, two DOM bars from zero in one hue below it, a bar and never a dial"
  why_this_technique: >
    The noise finding is a quantity against a threshold, so it is two lengths at one scale. The
    yard above it is who the number is about.
  palette: "the world above, the shaded lawn below the cut, bars in the rule ink"
  value_structure: >
    The render above carries the light. Below the cut the ground is the deck's dark, so the bars
    and the type read at full contrast.
  motion: "from the pod down to the bars"

type:
  kicker: "The draft's noise finding"
  hook: "It finds no significant impact"
  dek: "The draft ties 400 deliveries a day to places like a large apartment complex. At that rate it estimates delivery noise at no more than DNL 58.1 dB at any distance from a delivery point. It calls 59.7 dB the line below which a rise of 1.5 dB or more can't be significant."

verbatim: []

acceptance:
  - "the frame reads \"It finds no significant impact\""
  - "the draft's estimate, DNL 58.1, and its screening line, DNL 59.7, are printed as text from figures.json with no bar drawn"
  - "the hook states the draft's conclusion (c26) and the dek calls 58.1 an estimate, never a cap"
  - "a person stands in the yard by the fence, and the accent line clears the page counter"

risks:
  - "DNL from zero exaggerates nothing but reads flat. The labels carry the metric's name so nobody reads decibels as a percent"
```

```yaml
slide: 8
layout: DOCUMENT
primary_image:
  subject: "the draft propped on its clipboard on a weathered cedar patio table in low gold light, the back fence, the neighbours' roofs and the sky behind it, its title block, its prepared by line, its Table 2.2-1 as the draft prints it and its noise testing sentence printed on the page, the yard beyond"
  rect: [0, 380, 1080, 970]
  bleeds: [bottom, left, right]
accent: none
job: >
  Put the author of the draft on its own frame, in its own words, and say that every count in it
  is a ceiling.

claims: [c6, c27, c7, c36]
numerals: []

data_in_art:
  figure: total.deliveries_max
  drives: every number in the page's Table 2.2-1, the five metro rows and the total, set as the draft prints them

depth:
  eye: 1.2
  horizon: 640
  cues: [FORM_SHADING, CAST_SHADOW, RELATIVE_SIZE, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The page lies nearly square to the camera on the table's boards, lit across from the left, so
    its type reads. The table's far edge, the lawn and the fence fall away above it into the
    haze, where the hook sits.
  bands: >
    Top third, the yard beyond the table in haze, the hook and the dek. Middle third, the page lit
    across from the left. Bottom third, the foreground boards of the cedar table with their grain
    texture and the dark gaps between them, the page's shadow on the wood.
  focal: "the page's prepared by line and the table under it"

art:
  technique: "physically based render of a page texture drawn on a canvas with its own typography, on a cedar table in the declared world"
  why_this_technique: >
    The claim is what a document says about itself, so the frame is the document, lit where the
    reader would read it.
  palette: "warm white page, dark print, silver cedar grain, no accent"
  value_structure: >
    Lightest is the page. Darkest is the gaps between the boards and the far fence, which hold the
    type.
  motion: "from the hook down onto the page"

type:
  kicker: "Its own words"
  hook: "Zipline prepared it"
  dek: "The draft says Zipline prepared it under FAA supervision. Its noise figures rest on testing Zipline collected, in a report ICF prepared for the FAA. The page sets passages from across the draft side by side."

verbatim:
  - "Zipline prepared this draft environmental assessment (draft EA) under the supervision of the FAA"

acceptance:
  - "the frame reads \"Zipline prepared it\""
  - "the page carries the c6 sentence verbatim"
  - "the page sets Table 2.2-1's five metro rows and its total row with the draft's own numbers from figures.json, and draws no chart the draft does not print, under the table's own title and column headings"
  - "the page is not a facsimile of the FAA page, it is set in the deck's own type"

risks:
  - "page type rendered through a texture can blur. The page is drawn at 2x and the camera kept near square to it"
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: "the yard from a low camera looking west into the sun, the cedar gate from frame 1 standing open with light pouring through, a parcel on the grass casting a long shadow toward the camera, the neighbours' roofs beyond the fence, and the aircraft gone"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: none
job: >
  Close on the door the reader still has, the comment window, with its date and how to use it.

claims: [c2, c3, c18]
numerals:
  - value_from: c2   # October 11th
  - value_from: c3   # the 9 in the agency email address

depth:
  eye: 0.6
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, CAST_SHADOW, RELATIVE_SIZE, AERIAL, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A monument camera low on the lawn faces the declared sun. The open gate stands in the fence
    across the middle, light coming through it across the grass, the parcel in the foreground
    with its shadow reaching the lens. The sky above holds the type and the small aircraft.
  bands: >
    Top third, the sky and the hook and the dek, the aircraft small at the upper right. Middle
    third, the fence and the open gate against the burning horizon. Bottom third, the lawn in the foreground lit from behind so every blade rims, the parcel's long
    shadow reaching toward the lens, and the gate's light spilling across the grass.
  focal: "the bright gap of the open gate"

art:
  technique: "physically based render into the sun in the declared world, rim light on the fence and the parcel"
  why_this_technique: >
    The close is a place and a time of day, the same yard with the machine gone, so it is rendered
    like every other frame and the change of state carries the meaning.
  palette: "burning horizon, silhouetted fence and oak, straw lawn, the parcel's kraft brown"
  value_structure: >
    Lightest is the sun's glow through the gate. Darkest is the fence and the oak against it. The
    sky above is the calm mid ground for the type.
  motion: "from the parcel to the open gate to the sky"

type:
  kicker: "Public comment"
  hook: "Comments close October 11th"
  dek: "The draft gives no figure for how often an operator is sent an image. Email 9-FAA-Drone-Environmental@faa.gov and name the Zipline Texas Draft EA in the subject line."

verbatim: []

acceptance:
  - "the frame reads \"Comments close October 11th\""
  - "the dek carries the email address exactly as c3 quotes it, unbroken on one line"
  - "the dek puts the question the deck turns on, that the draft gives no figure for how often an operator is sent an image"
  - "the gate in the fence stands open with light through the gap"
  - "no accent line appears, because the line is reeled in"

risks:
  - "into the sun the type sits beside the glow. The declared azimuth puts the sun right of the type reserve"
```
