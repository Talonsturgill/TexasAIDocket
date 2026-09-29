# Storyboard, 2026-09-29
# "813 gas generators. One customer, at first."

## The story, and what the fact check did to it

El Paso Electric asked the PUCT to amend its certificate so it can build and own the McCloud
facility, a 366 MW natural gas plant made of 813 modular 450 kW generators (c1, c6), typically
installed in groups of four or five, each group on one step-up transformer (c7). It would stand on
about 31 acres immediately beside the data center Wurldwide LLC is developing in northeast El Paso
County (c8), which the case record says Meta owns (c2) and which Meta calls its newest AI-focused
data center (c3). That data center is intended at first to be the only retail customer of the
plant's output (c9). On September 23rd two SOAH judges filed a proposal for decision (c38). They
found need shown and cost-effectiveness, reliability and alternatives not shown (c27), and they
recommend approval only if the utility holds its other customers harmless from the plant's capital
and operating costs for the life of the facility, and denial without that condition (c28, c29,
c30). The commissioners decide at an open meeting with no date set (c37). The record admitted this
today as tx-2026-0193.

**WHAT THE FACT CHECK CHANGED.**
- **No "no transmission to the site".** The record says transmission limits and the time to
  expand them made a co-located plant the only option on the data center's timeline (c14, c15).
  No frame draws or says an absence of lines.
- **No bare $551.8 million.** It is the City witness's figure including transmission and
  financing (c19, c22). The judges' own generation-only figure is about $499.8 million (c20, c21).
The deck prints one dollar figure, the judges' approximately $499.8 million for the generation facilities alone, on frame 8 with c21's scope.
- **The bridge is "up to five years"** (c23), and the utility's witness expects under three (c24).
  Never a flat five.
- **"Monday" and no date** for the City Council vote (c46).
- **The utility's statement is not acceptance** of the counteroffer (c48).
- **The plant and its layout are DRAWN.** The record gives a count, a grouping and an acreage,
  never a site plan or a unit's dimensions. Every frame's source line says DRAWN.

## Why this treatment, and what was grafted

Three directors pitched CONSEQUENCE AND SCALE, THE BILL and THE VERDICT ON PAPER, and all three
independently built the deck's turn the same way: a twenty unit measure of the plant's estimated
service life (c19), five units marked for the bridge (c23), then all twenty under the judges'
condition (c30), seen twice through one camera. Three directors finding the same device without
seeing each other is the strongest evidence the room produces that it is the right one.

The deck is CONSEQUENCE AND SCALE's spine: one photographer walking one site in the last hour of
light, goldenHour, capitol granite as the one accent for the years the utility's other customers pay none of the plant's costs.

- From THE BILL: the ruler is an oilfield pipe-rail fence on the pad's edge, twenty spans, one per
  year, rather than a survey pole. A fence belongs to a Texas site; a banded pole is a prop. Also
  the one-scale MW ramp of frame 4.
- From THE VERDICT ON PAPER: the findings page of frame 5 (need shown, cost and reliability not),
  the vendor detail of frame 6, and "drawn to illustrate" carried on every frame.
- Refused: highNoon (THE BILL) and overcast (THE VERDICT) are both light decks with dark type, and
  the register allows one per eight runs; the pipe lengths for dollars per kW (no frame left, and a
  price the deck otherwise never prints); a clipboard in a resident's hands (the kit person has no
  hold pose).

## The world, and the laws that hold it

**THE CHIHUAHUAN DESERT EAST OF THE FRANKLIN MOUNTAINS AT THE END OF A SEPTEMBER DAY.** The chassis
is `assets/js/deck/2026-09-29-mccloud.js` and every frame loads it. It declares `sky: goldenHour`,
tuned (a deeper zenith, a cyan horizon, a gold haze band, a thin fog so a range 5 km out still
reads) and one light at azimuth -84, elevation 5, a hair south of west. +x is east, -z is north.
The Franklin ridge stands west of the site and a lower range east. The sun sets over the
Franklins, so a frame looking west looks into the sun, and a frame looking east gets the warm faces
and a blue sky. The world table's line for golden hour into the sun is scale, weight and
consequence.

The hero is one modular gas generator (`modular_gas_genset`, a kit addition in the chassis), in
blocks of five around one `padmount_transformer` (`genset_block`), and a yard of any count drawn as
instanced low detail units (`MC.yard`). The year fence (`MC.yearFence`) is the ruler.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#16181D` | the DOM body behind the render |
| `accent` | `#9A3B2A` | capitol granite, the years the utility's other customers pay none of the plant's costs, frames 1, 7 and 8. It replaced bluebonnet on the first render, because a blue accent under a blue golden hour sky measured as sky |
| `hook` | `#F1ECE3` | the hook |
| `dek` | `#E2DBCF` | the dek |
| `rule` | `#C9BFAF` | the site line, the source line and the counter |

The world's own colours are lit materials: Hueco Bolson caliche and sand, creosote olive scrub,
warm grey enclosure paint, utility green transformers, yellow gas risers, and the Franklins going
violet in the haze toward the sun.

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE
    VALUE CUT: frame 9

1. **Motif evolution.** The year fence: five panels capitol granite on frame 7, all twenty on
   frame 8 on the same camera, the two frames adjacent so the swipe is the before and after, and a
   dark banded line across the pad's edge in the last light on 9.
2. **Camera move.** One site from nine positions: low along the rows (1), beside one block (2), up
   over the whole pad (3), square to the beam ruled south of the field (4), at the transformer door
   (5), at an enclosure's corner (6), side on to the fence (7 and 8, one camera), out on the public
   road into the sun (9).

The edge tease the first plan declared (frame 2's yellow gas header arriving as the spine of frame
3's nearest row) was dropped after round 1, because two judges measured it absent at feed size and
a device the pixels do not carry is a claim the deck does not keep. The bare fence the first plan
put on frame 3 went for the same reason: at 250 m from the aerial camera it does not resolve.

## The rotation

    FULL_BLEED  FIGURE_SCALE  FULL_BLEED  DIAGRAM  DOCUMENT  CLOSE_CROP  SPLIT_HORIZON  SPLIT_HORIZON  FULL_BLEED

Frame 3 was declared GRID and re-declared FULL_BLEED on the first render: from 90 m up the field of 813 comes apart into one mass at thumb scale, not countable units, so it is a place, not a count.

`TXLAYOUT.check` returns an empty list.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "the field of 813 modular gas generators on graded caliche, a lane between block rows running from a louvred corner at the lower left into dust haze, green transformers at the end of every block, the low sun from the left laying shadows three bodies long across the lane, the eastern range faint on the horizon under a clear blue sky"
  rect: [0, 500, 1080, 520]
  bleeds: [left, right]
accent: "#9A3B2A"
job: >
  Stop the scroll on the scale of the thing, and state the whole story's tension in the hook, a
  plant built from one small box multiplied for one customer.

claims: [c2, c3, c6, c8, c9, c28, c29, c39]
numerals:
  - value_from: c6

data_in_art:
  figure: units
  drives: mark count, the instanced units drawn in the field

depth:
  eye: 0.9
  horizon: 700
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, CAST_SHADOW, OCCLUSION, TEXTURE_GRADIENT]
  subject_at: {X: 4, Z: -30}

composition:
  structure: >
    A monument camera down a lane between rows so the rows converge on a vanishing point on the
    horizon's upper third, and the count is felt as depth before it is read as a number.
  bands: >
    Top third, a blue golden hour sky holding the hook and dek. Middle third, the horizon, the far
    rows dissolving into haze and the faint eastern range. Bottom third, the nearest enclosures,
    their lit west faces, their long shadows across the caliche lane.
  focal: "the warm lit faces of the nearest block against the long shadow of the lane"

art:
  technique: "physically based render through txthree.js in the deck's goldenHour world, the yard instanced at true scale"
  why_this_technique: "the claim is a count of physical machines on one site, and only a rendered place makes a count a scale"
  palette: "Hueco Bolson caliche, warm grey enclosure paint, utility green, a blue golden hour sky"
  value_structure: >
    Lightest is the sun-struck faces of the near enclosures and the haze at the horizon. Darkest is
    the shadow side of the near row and the zenith behind the hook. Frame median L* planned at 30, rewritten from 48 after the renders measured the golden hour deck darker than planned.

type:
  hook: "813 gas generators. One customer, at first."
  dek: "El Paso Electric wants to build them beside Meta's AI data center in northeast El Paso County. Two judges recommend approval with a condition on who pays, and denial without it."
  labels: []

verbatim: []

acceptance:
  - "at least three rows of enclosures read as separate rows at 432px"
  - "the nearest enclosure shows a lit face and a shaded face that differ in value at 432px"
  - "the horizon sits above the dek's last line and below the frame's midpoint"
  - "no stack, plume or flame rises above any enclosure roof by more than a stub"
  - "no type crosses an enclosure"
  - "the render report's instance count for the field equals figures.json units"

risks:
  - "the field reads as texture rather than machines at feed size, so the near block is modelled at full detail"
  - "carousel no. 32 also showed enclosures on caliche, so the unit is small, grouped on transformers, and lit from the side under a blue sky rather than an amber one"
```

```yaml
slide: 2
layout: FIGURE_SCALE
primary_image:
  subject: "one block of five modular gas generators side by side on a concrete pad with the green step-up transformer at its end, yellow gas risers at each unit, a person at true scale standing at the pad corner, the desert and the rest of the field beyond"
  rect: [0, 520, 1080, 560]
  bleeds: [left, right]
accent: none
job: >
  Say what one unit of the 813 is and how they are grouped, with a person for the size, so the
  count on the cover becomes a thing a reader can picture.

claims: [c6, c7]
numerals:
  - value_from: c6

data_in_art:
  figure: units_per_group_max
  drives: unit count per block on the one transformer

depth:
  eye: 1.6
  horizon: 690
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: -16}

composition:
  structure: >
    A three quarter view of one block from standing eye height so the five enclosures step away
    toward the transformer and the person at the corner gives every one of them a size.
  bands: >
    Top third, sky and type. Middle third, the enclosures' roofline and stubs against the sky, the
    far field on the horizon. Bottom third, the lit concrete pad with the five enclosures' long
    modelled shadows raking across it, the yellow risers, and the person lit on the camera side.
  focal: "the lit end face of the nearest enclosure beside the person"

art:
  technique: "physically based render with the kit person at true scale"
  why_this_technique: "a size needs something a reader already knows the size of"
  palette: "warm grey paint, gas-line yellow, utility green, pale concrete"
  value_structure: >
    Lightest is the lit enclosure faces and the sky at the horizon. Darkest is the transformer's
    shade side and the shadows on the pad. Frame median L* planned at 34, rewritten from 36 after the renders measured the golden hour deck darker than planned, rewritten from 46 after the first render measured 26.5 and the second 33.1.

type:
  hook: "Four or five to a transformer"
  dek: "The plan would buy 813 modular gas generators rated at 450 kilowatts each. They are typically installed in groups of four or five, each group connected to a step-up transformer."
  labels: []

verbatim: []

acceptance:
  - "five enclosures and one transformer read as separate objects at 432px"
  - "the person stands on the ground with a contact shadow and reads as a person, not a post"
  - "each enclosure touches its pad with a contact shadow"
  - "no type crosses the person or an enclosure"
  - "the frame's median L* at 432px is between 22 and 48"

risks:
  - "the person reads as a mannequin, so the key is on the camera's side of the figure"
```

```yaml
slide: 3
layout: FULL_BLEED
primary_image:
  subject: "the whole field from 90 m up: 813 instanced enclosures in blocks on transformers on a graded pad beside the long pale data hall, the year fence a thin line along the pad's west edge, the creosote desert running to the horizon"
  rect: [0, 540, 1080, 810]
  bleeds: [left, right, bottom]
accent: none
job: >
  Put the plant on its ground beside its one customer, the count drawn as units a reader could
  count, and name whose data center it is.

claims: [c1, c2, c6, c7, c8, c14]
numerals:
  - value_from: c8
  - value_from: c6

data_in_art:
  figure: units
  drives: mark count, one rendered unit per generator

depth:
  eye: 90
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, TEXTURE_GRADIENT, CAST_SHADOW]
  subject_at: {X: 40, Z: -150}

composition:
  structure: >
    An oblique aerial so the field's rows recede and compress toward the data hall behind them,
    the count reading as a surface of repeated units with the one building they serve closing it.
  bands: >
    Top third, sky and type. Middle third, the data hall and the horizon with the eastern range.
    Bottom third, the field's nearest rows seen from above at an angle, each unit's lit roof and
    lit west face modelled against its own shadow on the caliche, the scrub at the pad edge.
  focal: "the dense lit field of enclosures against the pale wall of the data hall"

art:
  technique: "physically based render, the field instanced one unit per generator"
  why_this_technique: "a count is drawn as the thing counted, at the scale it stands"
  palette: "caliche, warm grey units, the pale data hall wall, blue sky"
  value_structure: >
    Lightest is the lit unit roofs and the data hall wall. Darkest is the shadow lanes between
    rows. Frame median L* planned at 34, rewritten from 36 after the renders measured the golden hour deck darker than planned, rewritten from 50 after the render measured 33.3, because lifting the exposure dropped the dek under 4.5 to 1.

type:
  hook: "About 31 acres beside the data center"
  dek: "The McCloud plant would sit on already-disturbed land immediately next to the data center, which Wurldwide LLC, owned by Meta, is developing. Its generators would run islanded, fed by a natural gas pipeline."
  labels: []

verbatim: []

acceptance:
  - "the field's rows read as separate units near the lens at 432px"
  - "the data hall reads as one long building behind the field"
  - "the render report's instance count for the field equals figures.json units"
  - "no numeral appears in the art"
  - "the frame's median L* at 432px is between 22 and 48"

risks:
  - "a reader takes the layout for the site plan, so the source line says DRAWN and the dek never describes an arrangement"
```

```yaml
slide: 4
layout: DIAGRAM
primary_image:
  subject: "a primer grey beam ruled on the caliche south of the field to the 1,000 MW commitment, white stakes at the first 220 MW, the second 220 MW and the peak, and a separate bar in the enclosures' own paint in front of the beam, from the same origin, that stops at 366 MW, the field's block rows behind under the eastern range, seen square from 6.5 m up"
  rect: [0, 700, 1080, 650]
  bleeds: [left, right, bottom]
accent: none
job: >
  Set the plant's size against what the customer committed to, at one scale, so a reader sees
  the plant is sized for one step of a larger ramp.

claims: [c1, c10, c11, c12, c13]
numerals:
  - value_from: c1
  - value_from: c10
  - value_from: c11
  - value_from: c12

data_in_art:
  figure: plant_share_of_peak
  drives: the grey line's length against the pale line's length, one scale

depth:
  eye: 4
  horizon: 590
  cues: [LINEAR_PERSPECTIVE, CAST_SHADOW, AERIAL, RELATIVE_SIZE]
  subject_at: {X: 0, Z: -22}

composition:
  structure: >
    The lines run across the frame square to a long lens so their lengths compare without
    foreshortening, with DOM labels above each tick and the block row standing behind as the
    thing the grey line measures.
  bands: >
    Top third, sky and type. Middle third, the block row on the horizon. Bottom third, the two
    ruled lines on the caliche and their labels.
  focal: "the bright pale line running on past where the grey line stops"

art:
  technique: "physically based render with lines ruled on the ground and DOM leaders"
  why_this_technique: "two quantities in one unit want two lengths at one scale, laid on the ground the plant stands on"
  palette: "caliche, a pale lime-white ruled line, enclosure grey"
  value_structure: >
    Lightest is the pale ruled line and the sky. Darkest is the block row's shade sides. Frame median L* planned at 32, rewritten from 50 after the renders measured the golden hour deck darker than planned.

type:
  hook: "366 MW against 1,000"
  dek: "The data center has committed to 1,000 MW by the end of 2029. The judges found existing resources can serve about the first 220 MW of its load, and the second 220 MW requires additional capacity."
  labels: ["220 MW, REGION 1", "220 MW MORE, REGION 2", "1,000 MW BY 2029", "366 MW McCLOUD"]

verbatim: []

acceptance:
  - "the grey line ends at a point whose distance from the origin is the pale line's full length times figures.json plant_share_of_peak, within 2 percent, measured off the render"
  - "each label sits above the tick it names within 24px"
  - "the two lines read as two separate lines at 432px"
  - "no label crosses a line or an enclosure"

risks:
  - "the diagram reads as a verdict that the plant falls short, so the dek names Region 1 as served from existing resources"
```

```yaml
slide: 5
layout: DOCUMENT
primary_image:
  subject: "the dark green step-up transformer's cabinet door square to the lens, a portrait page of the judges' proposal for decision in the door's clear document pocket with their two lines set on the page, and past the cabinet's edge on the right the next block's lit end, the field and the eastern range"
  rect: [0, 470, 1080, 880]
  bleeds: [left, right, bottom]
accent: none
job: >
  Put the judges' findings in their own words on the site they judge: need shown, and the rest
  not shown.

claims: [c27, c38, c39]
numerals: []

depth:
  eye: 1.4
  horizon: 760
  cues: [OCCLUSION, CAST_SHADOW, AERIAL, RELATIVE_SIZE]
  subject_at: {X: 0, Z: -2.2}

composition:
  structure: >
    The door shot square so the page's DOM lines register to it without rotation, the page low
    in the frame, and a slice of the world to its right so the document stands on the site.
  bands: >
    Top third, the type on the dark door, sky to the right. Middle third, the page in its pocket
    and past the cabinet's edge the next block and the horizon. Bottom third, the door's foot with
    dust at its sill on the concrete pad, and to the right the transformer's cast shadow across the
    caliche and the next block's pad in raking light.
  focal: "the lit page in the pocket against the dark green door"

art:
  technique: "physically based render, a document registered to a rendered surface"
  why_this_technique: "the claim is the judges' own sentence, and a document frame prints it where the thing it judges stands"
  palette: "utility green steel, a white page, the sun's glow"
  value_structure: >
    Lightest is the page. Darkest is the door's green around it. Frame median L* planned at 22, rewritten from 36 after the renders measured the golden hour deck darker than planned.

type:
  hook: "Need shown. Cost and alternatives, not."
  dek: "The two judges filed their proposal for decision on September 23rd. They found the utility showed a need for capacity to serve the data center."
  labels: ["did not show that the McCloud facility is a cost-effective and reliable resource", "failed to show that it adequately considered alternatives"]

verbatim:
  - c27: "did not show that the McCloud facility is a cost-effective and reliable resource"
  - c27: "failed to show that it adequately considered alternatives"

acceptance:
  - "the page reads as a sheet of paper in a pocket on a door at 432px"
  - "both quoted lines are legible at 432px and sit on the page's area"
  - "the frame shows sky above the transformer"
  - "no page line crosses the page's edge"

risks:
  - "the page reads as a sticker, so it sits behind a clear pocket with a lit edge"
```

```yaml
slide: 6
layout: CLOSE_CROP
primary_image:
  subject: "one enclosure's south face at the pad's edge, cropped by the right edge: intake louvre blades raked by the low sun, a blank data plate above them, the roof silencer and stack, and past its corner on the left the yellow gas riser and valve against the desert, the horizon and the sky"
  rect: [60, 690, 1020, 660]
  bleeds: [right, bottom]
accent: none
job: >
  Say how the machine was chosen: the vendor the data center preferred, no request for proposals,
  no cost-benefit analysis, and a first of its kind for this utility.

claims: [c16, c17, c18, c52]
numerals: []

depth:
  eye: 1.5
  horizon: 690
  cues: [OCCLUSION, CAST_SHADOW, TEXTURE_GRADIENT, AERIAL]
  subject_at: {X: 0, Z: -2}

composition:
  structure: >
    The enclosure fills the right two thirds, cropped by the right edge, so the reader stands at
    the machine. The sliver of world on the left keeps it in the place.
  bands: >
    Top third, sky and type. Middle third, the louvres and the plate. Bottom third, the riser, the
    valve and the dust at the base.
  focal: "the sun-raked louvre bank beside the yellow riser"

art:
  technique: "physically based render at detail scale"
  why_this_technique: "the finding is about this machine, and detail is where a reader believes it exists"
  palette: "warm grey paint, gas-line yellow, dark louvres"
  value_structure: >
    Lightest is the lit rounded edge and the sky sliver. Darkest is the louvre recesses. Frame median L* planned at 24, rewritten from 40 after the renders measured the golden hour deck darker than planned.

type:
  hook: "The vendor the data center preferred"
  dek: "El Paso Electric engaged Enchanted Rock after the data center preferred it. It considered no other vendor, issued no request for proposals and ran no cost-benefit analysis for ratepayers. The plant would be its first experience with modular gas generation."
  labels: []

verbatim: []

acceptance:
  - "the louvre blades read as separate blades at 432px"
  - "the gas riser reads as a yellow pipe with a valve"
  - "the frame shows sky past the enclosure's corner"
  - "no brand or maker's name appears anywhere in the art"

risks:
  - "a close crop loses the place, so a sliver of horizon stays in frame"
  - "a studio shot of the model passes the list, so the enclosure's base meets a pad with a contact shadow and the horizon is in frame"
```

```yaml
slide: 7
layout: SPLIT_HORIZON
primary_image:
  subject: "the year fence side on, twenty spans of oilfield pipe rail with sheet panels along the pad's west edge, the first five panels capitol granite and the rest bare primer, a galvanised collar on the post that ends the third span, a block of generators behind it, the eastern desert under a blue sky"
  rect: [0, 660, 1080, 690]
  bleeds: [left, right, bottom]
accent: "#9A3B2A"
job: >
  Draw the utility's offer as time: the data center pays for up to five years of a twenty year
  life, and nobody has decided the rest.

claims: [c19, c23, c25, c26, c48]
numerals:
  - value_from: c19
  - value_from: c23

data_in_art:
  figure: bridge_years_max
  drives: the number of capitol granite spans out of service_life_years spans

depth:
  eye: 1.4
  horizon: 650
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL]
  subject_at: {X: 0, Z: -42}

composition:
  structure: >
    A long lens side on to the fence so its twenty spans read at one scale edge to edge, the
    sun behind the camera lighting every rail, the horizon at mid frame for the split.
  bands: >
    Top third, sky and type. Middle third, the horizon with the block of generators and its
    transformer standing behind the fence, the far desert and the eastern range. Bottom third,
    the fence's twenty spans running across, its lit rails and posts, and their long shadows
    across the textured caliche.
  focal: "the run of five capitol granite panels against the primer panels that follow"

art:
  technique: "physically based render with the fence as a bar that is never a dial"
  why_this_technique: "a length of time wants a length, and a fence is the thing a Texas site already measures itself by"
  palette: "capitol granite paint, primer grey pipe, caliche, blue sky"
  value_structure: >
    Lightest is the sky at the horizon and the lit rails. Darkest is the fence's shadow on the
    caliche. Frame median L* planned at 38, rewritten from 50 after the renders measured the golden hour deck darker than planned.

type:
  hook: "Up to five years, then no decision"
  dek: "El Paso Electric proposes a bridge of up to five years in which the data center pays all the plant's capital costs. Its witness testified that no decision has been made on who pays after that. Its chief executive told KVIA it isn't seeking to shift those costs onto residential or other customers."
  labels: ["UP TO YEAR 5, BRIDGE", "YEAR 20, ESTIMATED SERVICE LIFE"]

verbatim: []

acceptance:
  - "twenty spans read as countable spans at 432px"
  - "exactly bridge_years_max panels are the accent and the rest are not, measured off the render"
  - "post 0 and post 20 are both inside the frame"
  - "the fence's first and last spans differ in projected length by under 10 percent"
  - "the accent covers under 8 percent of the frame"
  - "no type crosses the fence"

risks:
  - "the fence reads as a fence and not a timeline, so the labels name the unit"
```

```yaml
slide: 8
layout: SPLIT_HORIZON
primary_image:
  subject: "frame 7's camera, fence, block and desert unchanged, with all twenty panels capitol granite"
  rect: [0, 660, 1080, 690]
  bleeds: [left, right, bottom]
accent: "#9A3B2A"
job: >
  The turn. The judges' condition covers every year, and the reader sees it as one changed state
  of the same fence before they read it.

claims: [c19, c20, c21, c28, c30, c46]
numerals:
  - value_from: c19

data_in_art:
  figure: service_life_years
  drives: the number of capitol granite spans, all of them

depth:
  eye: 1.4
  horizon: 650
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL]
  subject_at: {X: 0, Z: -42}

composition:
  structure: >
    Frame 7 exactly, one parameter changed, so the swipe is a before and after.
  bands: >
    Top third, sky and type. Middle third, the horizon with the same block and transformer behind
    the fence, the far desert and the eastern range. Bottom third, the fence with every top rail
    painted, lit by the sun behind the camera, and the long post shadows across the caliche.
  focal: "the full run of capitol granite panels across the frame"

art:
  technique: "physically based render, motif state change on an identical camera"
  why_this_technique: "a condition that covers the whole life is the whole length"
  palette: "capitol granite paint, primer grey posts, caliche, blue sky"
  value_structure: >
    Lightest is the sky and the lit rails. Darkest is the fence's shadow. Frame median L* planned
    at 38, rewritten from 49 after the renders measured the golden hour deck darker than planned.

type:
  hook: "For the life of the plant"
  dek: "The judges recommend approval only if the utility's other customers pay none of the plant's capital and operating costs, unless the plant later meets the statute's test. Its generation facilities are estimated at about $499.8 million. El Paso City Council has authorized a counteroffer for a full hold harmless."
  labels: ["For the life of the McCloud facility", "OTHER CUSTOMERS PAY NONE"]

verbatim:
  - c30: "For the life of the McCloud facility"

acceptance:
  - "all twenty panels are the accent, measured off the render"
  - "the camera, fence and block match frame 7 within 2px at every post"
  - "at 432px the accented length is at least 3.5 times frame 7's, measured off the thumbs"
  - "the accent covers under 8 percent of the frame"
  - "no type crosses the fence"

risks:
  - "the condition is overstated as a ruling, so the kicker says PROPOSED and the dek says recommend"
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: "the field of 813 into the sun: the block rows in silhouette with glowing seams on their rounded edges, the year fence a dark banded line in the middle distance, the Franklin ridge against the burning horizon, a chain link fence on the public road receding along the right of the frame"
  rect: [0, 520, 1080, 830]
  bleeds: [left, right, bottom]
accent: none
job: >
  Close on the public's route and the open question: the commission has not ruled, the city is
  negotiating, and the docket is where a Texan reads it.

claims: [c6, c37, c42, c44, c45]
numerals:
  - value_from: c45

data_in_art:
  figure: units
  drives: mark count of the silhouetted field

depth:
  eye: 1.6
  horizon: 740
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, OCCLUSION, CAST_SHADOW]
  subject_at: {X: -80, Z: 0}

composition:
  structure: >
    The camera turns into the sun over the ridge at last, the field going to silhouette, from the
    public road with its chain link fence receding on the right, so the reader stands where the
    public stands.
  bands: >
    Top third, the sky warming toward the sun and the type. Middle third, the ridge and the
    burning seam, the silhouetted rows. Bottom third, the chain link fence with the sun glinting
    on its wire receding along the right, the public road's shoulder, and the scrub and caliche
    going dark in long shadow toward the lens.
  focal: "the burning seam over the ridge behind the silhouetted rows"

art:
  technique: "physically based render into the sun"
  why_this_technique: "the deck ends on what is unresolved, and a backlit place keeps its shapes and loses its detail"
  palette: "rose and gold sky, violet ridge, dark silhouettes"
  value_structure: >
    Lightest is the sun's seam on the horizon. Darkest is the silhouetted rows and the ground.
    Frame median L* planned at 23, rewritten from 34 after round 1 dimmed the key to the ridge's shadow and the render measured 22.9.

type:
  hook: "The commission has not ruled"
  dek: "KVIA reports that five commissioners will accept, change or reject the proposal and that a final order is expected by December 7th. Docket 59076 on the PUCT Interchange holds comments from 1118 protestors and a residential customer."
  labels: []

verbatim: []

acceptance:
  - "the rows read as silhouettes with lit edges at 432px"
  - "the chain link fence reads as a fence receding along the right edge at 432px"
  - "the sun's glow sits at the right edge over a thin band of ridge, not in the type band"
  - "the frame's median L* at 432px is between 18 and 40"

risks:
  - "a figure in the dark is a named defect, so no person stands in this backlit frame"
```
