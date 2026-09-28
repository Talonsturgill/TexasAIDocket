# Storyboard, 2026-09-28
# "Asked for fire detections. Counted cameras."

## The story, and what the fact check did to it

Southwestern Public Service Company, the Xcel Energy utility whose service area covers most of the
Texas Panhandle (c29, c46), runs AI smoke detection cameras from Pano AI (c26). Each camera site
carries two cameras that rotate to detect smoke (c25), and a human operator verifies and forwards
what they gather (c24). The PUCT approved SPS's resiliency plan on July 10th, 2025 (c10, c31, c32),
and its order lists the "number of artificial intelligence camera fire detections" among the
measures SPS must carry into its annual reports (c33, c34). SPS filed its first report on May 1st,
2026 (c9). Under that measure it wrote "Actual: 33 cameras installed" and "Projected: 34 for 2026"
(c8). The record admitted this today as tx-2026-0192, beside tx-2026-0191, the PUCT's wildfire
plan blueprint.

**WHAT THE FACT CHECK CHANGED.**
- **33 is cameras, and each site carries two (c25).** No frame draws 33 masts or sites. The count
  is drawn as 33 camera heads.
- **The detections line is an empty rail, never a zero.** The report doesn't say no fires were
  detected. It answers a different question. The same report DOES count fires (24 ignitions
  associated with its lines, c18, and 26 NIFC wildfires in its counties, c20), so no surface says
  the report counts no fires. It counts no DETECTIONS.
- **Three scopes, never combined.** 68 planned (c23, the application), 33 installed and 34
  projected (c8, the report) and 97 across the service territory including New Mexico (c41, the
  Tribune) are never summed, subtracted or set side by side. 97 is on no frame.
- **The utility's own caveat is carried fairly.** It says a partial year can't yet compare actual
  effectiveness with projections (c21). Frame 5 prints it.
- **Colorado (c47, c48) is on no frame.**
- **Smokehouse Creek's cause is the Tribune's report (c53) beside SPS's own testimony (c28).**
- **The station is DRAWN.** Its 12 m height, its enclosure and its antenna are not claimed. It
  stands for the kind of station c25 describes and is no one's site. Frame 1's source line says
  DRAWN.

## Why this treatment, and what was grafted

Three directors pitched THE WATCHTOWER, THE LEDGER LINE and THE LINE AND THE POLE. All three chose
the camera station as the hero, all three drew the 33 as camera heads rather than masts, and two of
three chose stormFront without seeing each other. The deck is THE WATCHTOWER's spine: one station,
nine positions, its two heads turning toward the reader as the argument lands, because the story is
about one kind of machine and what the state asked it to prove.

- From THE LEDGER LINE: the two rail fence on frame 6, the report's own words over a full top rail
  and the order's words over a bare lower rail. A table has rows and a ranch has rails, and the
  frame is the two lines of the ledger set in the grass. Also the hearing room on frame 8, which is
  the literal room where lawmakers heard the count, set for 160 with eight binders.
- From THE LINE AND THE POLE: the standing decayed wood pole of frame 2, cropped close, rather than
  a broken one. c53 says a pole snapped and nothing in the record describes its break, so the deck
  draws the kind of pole and not the event.
- Refused: a smoke plume anywhere (a plume claims a detection no claim reports), a snapped pole with
  a rotted core (a break no claim describes), a pole field under a cloud hole (a utility is not a
  pole), a laptop screen with a day bar (a screen is web furniture on this brand), and highNoon
  (THE LEDGER LINE's world). Noon over straw grass and white paper is the pale on pale the owner
  rejects, and stormFront gives the type a dark calm sky.

## The world, and the laws that hold it

**A PANHANDLE RED FLAG AFTERNOON UNDER A DRY FRONT.** The chassis is
`assets/js/deck/2026-09-28-watchtower.js` and every frame loads it. It declares `sky:
stormFront`, tuned once so the haze is a neutral dust grey rather than rain blue or peach, and one
light at azimuth -68, elevation 10, inside the preset's 6 to 16. The sun is a low shaft from the
west-southwest under a bruised deck of cloud to the north. Why this light: fire weather on the High
Plains is wind and a front over cured grass, and the world table gives stormFront to "risk, a
warning, a deadline", which is Rep. King's "January is coming" (c44). It is also a light none of
the last four decks used.

**ONE HERO OBJECT.** `wildfire_camera_station`, built once in the chassis as a kit model: a tapered
galvanized monopole on a concrete pier, a crossarm with two pan and tilt camera heads in white
sunshielded housings, an equipment enclosure with conduit, a panel antenna and a lightning rod. Its
`part:'head'` option makes one loose head on its turntable, which is how frame 6 counts cameras.
`WATCH.station(K, o)` makes it the same way on every frame.

**THE ACCENT IS THE STATE'S QUESTION.** `comal` `#2A7A9E` from `config/brand.yaml`. It marks the
line the state asked to be filled, and nothing else: the margin rule beside line j on frame 4, the
same rule beside the report's metric on frame 5, the flagging on the bare rail's end posts on frame
6, and the spine tabs of the eight filed plans on frame 8. It never touches a camera, a pole, the
grass or the sky. It is cool on purpose, so it can never read as flame.

**THE MUTE WORLD LAW.** No logo, no company name and no readable screen in the art. Every word on a
page is either DOM registered to the page or a hairline.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#15171C` | the DOM body behind the render |
| `accent` | `#2A7A9E` | comal, the state's question, frames 4, 5, 6, 8 |
| `hook` | `#F1ECE3` | the hook, on the storm deck |
| `dek` | `#E2DBCF` | the dek |
| `rule` | `#C9BFAF` | the site line, the source line and the counter |

The world's own colours are lit materials: cured shortgrass straw, caliche road, the red breaks
under a pale caprock far out in haze, galvanized steel, white powder coat on the heads, creosoted
pole brown gone silver, and a storm deck of slate and bruise.

## The continuity devices

    CONTINUITY: CAMERA_MOVE, MOTIF_EVOLUTION, EDGE_TEASE
    VALUE CUT: frame 8

1. **Camera move.** One station from nine positions: 38 m out at eye height (1), low in the grass
   by a pole with the station on the ridge (2), up level with the heads (3), seated at a desk for
   two frames with the page swapped (4, 5), at the rail fence beside it
   (6), square on to its own tube on cribbing (7), into the hearing room (8), and out at the ranch
   gate below it (9).
2. **Motif evolution.** The heads' pan steps across the deck. They face the plain on 1, split on 3,
   the heads leave the station on 6, where 33 stand on the rail, turn away from the lens on 7, and face the reader on 9.
3. **Edge tease.** The caliche road leaves frame 1 at the bottom right and arrives at the gate on
   frame 9.

## The rotation

    FULL_BLEED  FULL_BLEED  DIAGRAM  DOCUMENT  DOCUMENT  DIAGRAM  OBJECT_AND_CAPTION  GRID  FIGURE_SCALE

Frame 6 was re-declared DIAGRAM in round 1 because 33 heads on one rail can't come apart into countable pieces at thumb scale, and what the frame compares is a filled rail against a bare one.

`TXLAYOUT.check` returns an empty list.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "the wildfire camera station on a graded caliche pad at the caprock rim, 30 m from the lens through a 30 degree lens, its two heads splayed to the plain, lit from the left rear by the low shaft under the storm deck, a caliche road leading to it and a barbed wire fence across the foreground, cured straw grass to a hazed mesa 4 km out"
  rect: [0, 330, 1080, 1020]
  bleeds: [left, right, bottom]
accent: none
job: >
  Stop the scroll on a real Panhandle place with the AI in it, and state the substitution as an act
  in the hook.

claims: [c29, c46, c25, c26, c33, c34, c8, c56]
numerals: []

data_in_art:
  figure: cameras_per_site
  drives: head count on the crossarm

depth:
  eye: 1.6
  horizon: 900
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, CAST_SHADOW, OCCLUSION, TEXTURE_GRADIENT]
  subject_at: {X: 6, Z: -38}

composition:
  structure: >
    A standing camera 38 m off the mast, the mast on the right third so it rises through the sky
    band beside the hook rather than through it, the road entering from the bottom right and
    turning to the pad, the fence running across the lower left foreground.
  bands: >
    Top third, the bruised storm deck with the hook and the dek. Middle third, the mast and its two
    heads against the lighter band under the cloud, the caprock far out in haze on the left. Bottom
    third, straw grass modelled by the low shaft, the fence's T-posts and wire, the caliche road
    and the pad with the mast's long shadow running right.
  focal: "the two white camera heads at the top of the mast against the dark cloud deck"

art:
  technique: "physically based render through txthree.js in the deck's stormFront world"
  why_this_technique: "the claim is that this machine exists in this country, and only a rendered place carries that"
  palette: "Panhandle shortgrass straw, caliche, galvanized steel, white powder coat, a slate and bruise storm deck"
  value_structure: >
    Lightest is the white housing of the heads and the lit band under the cloud at the horizon.
    Darkest is the storm deck at the zenith where the hook sits. Frame median L* planned at 32.

type:
  hook: "Agreed to count fire detections. Counted cameras."
  dek: "The Xcel Energy utility for most of the Texas Panhandle runs AI smoke cameras. The order approving its plan lists the number of AI camera fire detections among the metrics it agreed to report. Its annual report answered that line with a count of cameras."
  labels: []

verbatim: []

acceptance:
  - "the two camera heads read as two separate boxed white housings at 432px"
  - "the mast touches its pad with a contact shadow and the pad touches the ground"
  - "a caliche road runs from the pad toward the bottom right edge and a barbed wire fence stands in the near left"
  - "no type crosses the mast or either head"
  - "no smoke plume and no flame anywhere in the frame"
  - "the frame's median L* at 432px is between 22 and 42"
  - "no numeral appears in the art"

risks:
  - "the mast is thin at 38 m and could read as a streetlight, so the heads must be large enough to read as cameras at 432px"
  - "stormFront can read as rain, so no precipitation and a dust grey haze"
```

```yaml
slide: 2
layout: FULL_BLEED
primary_image:
  subject: "a three phase distribution line of the kit's own 40 ft class wood poles crossing the cured straw plain away from the lens, the nearest 26 m out on the right third with its crossarm and porcelain insulators against the storm deck, the conductors running down the line to the horizon, the caprock breaks in the haze on the left"
  rect: [0, 0, 1080, 1350]
  bleeds: [top, left, right, bottom]
accent: none
job: >
  Say why this utility answers for fire in this place, with the kind of pole the Smokehouse Creek
  fire started at, drawn standing and whole.

claims: [c53, c28]
numerals: []

depth:
  eye: 1.5
  horizon: 870
  cues: [RELATIVE_SIZE, AERIAL, OCCLUSION, CAST_SHADOW, TEXTURE_GRADIENT]
  subject_at: {X: -1, Z: -2.5}

composition:
  structure: >
    Recomposed a second time after panel round 3: the kit's pole is a primitive at detail scale, so
    the frame steps back to a whole line of them crossing the plain, the nearest on the right third,
    the rest converging on the horizon beside the dek, the caprock in the haze on the left.
  bands: >
    Top third, the storm deck with the hook on the right half. Middle third, the pole's checked
    wood and the hazed ridge with the station. Bottom third, cured straw bunchgrass rising around the pole's weathered butt, each tuft modelled by the low shaft with its shade side toward the lens, the pole's long cast shadow running right across the grass, and the dek set on the darker grass under it.
  focal: "the lit west face of the pole's checked wood against the dark cloud"

art:
  technique: "physically based render, close crop at a low eye, heavy weathering on the kit pole"
  why_this_technique: "the claim is about a kind of object and its age, and a close crop at detail scale is where age shows"
  palette: "creosote brown gone silver, porcelain grey, straw, storm slate"
  value_structure: >
    Lightest is the lit face of the pole and the band under the cloud. Darkest is the pole's shade
    side and the zenith. Frame median L* planned at 30.

type:
  hook: "The Tribune traces the fire to a pole."
  dek: "The Tribune reports the Smokehouse Creek fire was the largest in Texas history. It says the fire started when a decayed Xcel Energy pole snapped and landed in dry grass. SPS testimony says its equipment \"appeared to be involved in two ignitions\" of the fire."
  labels: []

verbatim:
  - c28: "appeared to be involved in two ignitions"

acceptance:
  - "the line stands and is whole, and nothing in the frame is broken, burnt or smoking"
  - "at least four poles of the line read at 432px, the nearest on the right third with its crossarm"
  - "no pole, crossarm or conductor crosses a glyph of the hook or the dek"
  - "the caprock breaks read in the haze on the left horizon"
  - "the frame's median L* at 432px is between 20 and 40"

risks:
  - "a judge may read the station on the ridge as placed at the ignition site, so it stays small and no string places it"
```

```yaml
slide: 3
layout: DIAGRAM
primary_image:
  subject: "the station's crossarm and both camera heads at kit detail from 2.2 m away at 12.2 m up, one head turned toward the lens and one away, the mast dropping out of the bottom, the plain and the caprock breaks below the horizon"
  rect: [360, 560, 720, 790]
  bleeds: [right, bottom]
accent: none
job: >
  Show what the AI physically is and where the person stands in it, with leaders that land on the
  two heads.

claims: [c25, c24, c26]
numerals: []

data_in_art:
  figure: cameras_per_site
  drives: head count, each head carrying its own leader

depth:
  eye: 12.2
  horizon: 980
  cues: [LINEAR_PERSPECTIVE, AERIAL, FORM_SHADING, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    Level with the heads so the crossarm reads flat and the two housings sit side by side on the
    right two thirds, leaders running left from each head to mono labels in the sky, the country
    far below the horizon line.
  bands: >
    Top third, the hook on the storm deck. Middle third, the crossarm and the two heads with their
    leaders. Bottom third, the galvanized mast falling away out of the bottom edge with its conduit and flange splice lit on the west side, the straw plain and the red caprock breaks far below in haze with their shadowed gullies, and the dek set on the shadowed plain.
  focal: "the nearer white housing and its dark glass window"

art:
  technique: "physically based render with DOM SVG leaders ending short of the glyph band"
  why_this_technique: "the claim is a mechanism, two cameras and a person, and a diagram on the real object explains it"
  palette: "white powder coat, galvanized steel, the storm deck, the straw plain far below"
  value_structure: >
    Lightest is the lit housings. Darkest is the zenith behind the labels. Frame median L* planned at 34.

type:
  hook: "Two cameras turn. A person checks."
  dek: "The SPS application says each camera site carries two cameras that rotate to detect smoke. A human operator verifies and forwards what they gather. SPS named Pano AI as its partner."
  labels: ["two physical cameras that rotate", "verified and forwarded by a human operator", "shared with SPS and first responders"]

verbatim:
  - c25: "two physical cameras that rotate"
  - c24: "verified and forwarded by a human operator"

acceptance:
  - "each leader leaves the first label's last glyph and ends in a ring on its own head"
  - "the two housings read as two boxed cameras at 432px"
  - "no leader and no part of the station crosses a glyph"
  - "both heads sit below the dek's last line and the mast stays left of the site line"
  - "the frame's median L* at 432px is between 24 and 44"

risks:
  - "the operator is named and not drawn, because no claim says where the operator sits"
```

```yaml
slide: 4
layout: DOCUMENT
primary_image:
  subject: "the PUCT order's letter page on an oak office desk under the room's storm light, its list of measures drawn as hairlines with line j bare where the accent rule sits, a document stack at the right, the DOM line j set below with a leader landing on the bare line"
  rect: [0, 380, 1080, 970]
  bleeds: [left, right, bottom]
accent: "#2A7A9E"
job: >
  Show that the state wrote the question down, in its own words, in the approval.

claims: [c10, c31, c32, c33, c34]
numerals: []

depth:
  eye: 1.25
  horizon: 150
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: -0.6}

composition:
  structure: >
    Seated at the desk looking down on the page at about 40 degrees, the window on the upper left
    throwing the storm light across the desk, the page on the lower half and the document stack beside it on
    the right so the machine and the paper that asks about it share one surface.
  bands: >
    Top third, the window with the storm light and the dark wall beside it where the hook sits.
    Middle third, the desk's far edge, the document stack and the loose white head with its lit
    housing and cast shadow. Bottom third, the lit page lying on the veneer with a soft cast shadow
    under its curled edge, its hairline entries in graded grey, the accent rule beside line j.
  focal: "the lit page on the dark desk"

art:
  technique: "physically based render in a TXT.interior room, a page texture with hairline entries and DOM verbatim registered to the page"
  why_this_technique: "the claim is a document's own words, and the page as an object in the place it governs carries them"
  palette: "white page, oak veneer, white powder coat head, storm light through the window, a dark wall"
  value_structure: >
    Lightest is the page. Darkest is the wall behind the hook. Frame median L* planned at 26, rewritten from 38 after the room was lit to the deck's value track in round 1.

type:
  hook: "The order wrote the measure down."
  dek: "The PUCT approved the SPS resiliency plan on July 10th, 2025, as modified by the parties' agreement. The order lists the number of AI camera fire detections among the agreed metrics SPS will carry into its annual reports."
  labels: ["j. number of artificial intelligence camera fire detections;"]

verbatim:
  - c33: "j. number of artificial intelligence camera fire detections;"

acceptance:
  - "the line j label reads 'j. number of artificial intelligence camera fire detections;' exactly and ends inside x 1000"
  - "one accent bar #2A7A9E sits under the line j label and the accent appears nowhere else"
  - "the leader runs from the label to the bare line on the page"
  - "the page casts a soft shadow on the desk and the binders are neutral covers, no navy and no red"
  - "the frame's median L* at 432px is between 20 and 40"

risks:
  - "a room shot counts only when its walls or floor fill half the frame, so the window wall stays in"
```

```yaml
slide: 5
layout: DOCUMENT
primary_image:
  subject: "frame 4's desk and camera unchanged, the SPS annual report page now laid over the order, its tenth line bare where the same accent rule sits, the DOM metric heading and answer set below with a leader landing on it"
  rect: [0, 380, 1080, 970]
  bleeds: [left, right, bottom]
accent: "#2A7A9E"
job: >
  Show the answer the utility filed on the line the state asked for, in its own words, from the
  same place the question was read.

claims: [c9, c8, c21]
numerals:
  - value_from: c8
  - value_from: c9

depth:
  eye: 1.25
  horizon: 150
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: -0.6}

composition:
  structure: >
    Identical to frame 4, so the only change is the page and the head's turn. The swipe reads as the
    answer landing on the question.
  bands: >
    Top third, the window light and the dark wall with the hook. Middle third, the stack and the
    document stack at the right, lit from the window. Bottom third, the report
    page lying over the order on the veneer, each with a soft cast shadow under its curled edge,
    lit by the window, the metric and the answer registered to the page, the accent rule beside it.
  focal: "the report page on the desk"

art:
  technique: "physically based render, frame 4's camera with the page swapped"
  why_this_technique: "a camera held while one thing changes makes the change the whole message"
  palette: "as frame 4"
  value_structure: >
    Lightest is the page. Darkest is the wall. Frame median L* planned at 26, rewritten from 38 after the room was lit to the deck's value track in round 1.

type:
  hook: "The answer counted cameras."
  dek: "SPS filed its annual report on May 1st. Under the detections line it wrote 33 cameras installed and 34 projected for 2026. It says a partial year means actual effectiveness can't yet be compared with projections."
  labels: ["Number of artificial intelligence camera fire detections.", "Actual: 33 cameras installed", "Projected: 34 for 2026"]

verbatim:
  - c8: "Number of artificial intelligence camera fire detections."
  - c8: "Actual: 33 cameras installed"
  - c8: "Projected: 34 for 2026"

acceptance:
  - "the page labels read exactly as the report prints them"
  - "the report sheet is turned 13 degrees against the order sheet and four sheet corners are visible at 432px"
  - "the accent bar and the leader's end sit at the same frame position as on frame 4 within 4px"
  - "the desk, the grommet and the stack match frame 4 within 4px"
  - "the frame's median L* at 432px is between 20 and 40"

risks:
  - "bespoke_check may pair 4 and 5, which is the point, and their scene code differs in the page and the heads' pan"
```

```yaml
slide: 6
layout: DIAGRAM
primary_image:
  subject: "a two rail pipe corral fence seen within 10 degrees of square on, left to right across the frame, 33 loose white camera heads on their turntables along the top rail, the lower rail bare between two posts tied with accent flagging at its height, the station 57 m out on the right, its heads smaller than the rail's, a caliche two track along the fence"
  rect: [0, 560, 1080, 580]
  bleeds: [left, right]
accent: "#2A7A9E"
job: >
  Make the substitution physical, the count of cameras on one line and the count the state asked
  for on the line under it, with nothing on it.

claims: [c8, c33, c25]
numerals:
  - value_from: c8

data_in_art:
  figure: cameras_installed
  drives: mark count of rendered camera heads on the top rail (33), with detections_reported leaving the lower rail bare

depth:
  eye: 1.6
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL]
  subject_at: {X: 0, Z: -26}

composition:
  structure: >
    Near square on to the fence so every head is one size, the two rails as the two lines of the
    ledger, the corner post and the station on the right showing where a head belongs.
  bands: >
    Top third, the hook on the storm deck and the station's upper mast at the right. Middle third, the 33
    white heads on the top rail with their label, and the bare lower rail with its label and flagging.
    Bottom third, the fence's pipe posts standing in cured straw grass with their long shadows raking right, grass tufts modelled by the low shaft in the foreground, the caliche two track along the fence line, and the dek set on the shadowed grass.
  focal: "the row of 33 white heads on the top rail"

art:
  technique: "physically based render, an isotype of one instanced head at true size"
  why_this_technique: "the claim is a count, and a count a reader can count needs units at one size"
  palette: "white heads, galvanized pipe, straw, accent flagging, storm deck"
  value_structure: >
    Lightest is the row of heads. Darkest is the storm deck. Frame median L* planned at 34.

type:
  hook: "One line filled. One left bare."
  dek: "Each head on the top rail is one camera the report counts as installed. The lower rail is the line the order named. The report gives that line no count of detections. A missing count isn't a count of none."
  labels: ["Actual: 33 cameras installed", "number of artificial intelligence camera fire detections"]

verbatim:
  - c8: "Actual: 33 cameras installed"
  - c33: "number of artificial intelligence camera fire detections"

acceptance:
  - "exactly 33 heads stand on the top rail, each within 15 percent of the others' width at full size"
  - "no numeral and no mark appears on or beside the lower rail"
  - "the count label sits just over the heads and the order's line sits just under the bare rail with one accent bar under it"
  - "the station's heads render smaller than the rail heads"
  - "the frame's median L* at 432px is between 24 and 44"

risks:
  - "heads on a rail can read as storage, so the dek names them as installed cameras"
  - "the bare rail can read as zero, so the dek says in words that the report doesn't say none were made"
```

```yaml
slide: 7
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "two lengths of the station's own galvanized tube on timber cribbing on the pad, one above the other, left aligned on one end plate, the upper at the plan's cost and the lower at the anticipated cost on one scale, the station 27 m behind on the right third with its heads turned away across the grass"
  rect: [0, 600, 1080, 650]
  bleeds: [left, right]
accent: none
job: >
  Show the one number the report does measure exactly, money, as two lengths at one scale.

claims: [c15]
numerals:
  - value_from: c15

data_in_art:
  figure: capex_2026
  drives: length of the anticipated tube, set against capex_plan_2026 as the plan tube on one scale from one end plate

depth:
  eye: 1.2
  horizon: 820
  cues: [LINEAR_PERSPECTIVE, CAST_SHADOW, AERIAL, FORM_SHADING]
  subject_at: {X: 0, Z: -9}

composition:
  structure: >
    Square on to the two tubes so both lengths lie in one plane parallel to the lens and the ratio
    holds, the end plate on the left third, the longer tube bleeding the right edge, the station
    behind.
  bands: >
    Top third, the hook and the dek on the storm deck. Middle third, the station and the horizon.
    Bottom third, the two lit galvanized tubes lying on stacked timber cribbing on the caliche pad, each casting a hard shadow onto the pad, the end plate's bolt heads catching light, the cribbing's end grain and weathered faces modelled, the mono labels beside each tube's far end.
  focal: "the two lit galvanized tubes on the dark cribbing"

art:
  technique: "physically based render, two lengths at one scale, square on"
  why_this_technique: "a ratio needs one scale and one zero, and the station's own steel carries it"
  palette: "galvanized steel, weathered timber, caliche pad, storm deck"
  value_structure: >
    Lightest is the lit top of the tubes. Darkest is the storm deck. Frame median L* planned at 33.

type:
  hook: "The cost was projected to the dollar."
  dek: "For 2026 SPS anticipates $10,537,400 of AI camera capital costs against $6,423,554 in the plan. It calls that a 64.04% change."
  labels: ["PLAN $6,423,554", "ANTICIPATED $10,537,400"]

verbatim: []

acceptance:
  - "the lower tube's length over the upper tube's length measures 1.64 plus or minus 0.03 on the PNG"
  - "both tubes start at the same end plate"
  - "the tubes read as pale galvanized steel, lighter than the grass around them at 432px"
  - "the station stands on the right third with its crossarm and both heads clear of the dek"
  - "the frame's median L* at 432px is between 24 and 44"

risks:
  - "perspective can change the ratio, so the camera is square on and the check is measured off the render"
```

```yaml
slide: 8
layout: GRID
primary_image:
  subject: "a committee hearing room seen from behind the dais, the lawmakers' view: the bench and its microphones across the foreground, a witness podium, and 160 public seats in ten rows of sixteen facing the lens, eight of them carrying a white plan binder with an accent spine tab, the room lit from its left window"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#2A7A9E"
job: >
  Take the story from one utility to the state, in the room where lawmakers heard the count.

claims: [c43, c45, c1, c58, c37, c38]
numerals:
  - value_from: c43

data_in_art:
  figure: utilities_total
  drives: seat instance count (160), with utilities_filed setting the binder count (8)

depth:
  eye: 2.4
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, OCCLUSION, CAST_SHADOW]
  subject_at: {X: 0, Z: -9}

composition:
  structure: >
    Standing raised at the back of the gallery so the ten rows of sixteen recede to the dais, the
    eight binders scattered through the rows as white marks, the window light from the left.
  bands: >
    Top third, the hook on the dark upper wall. Middle third, the dais, the flags and the far rows.
    Bottom third, the nearest rows of padded seats in hard perspective, their seat backs and chrome frames catching the window light, two of the eight white binders on the near seats with their accent spine tabs, the carpet between rows in shade, and the dek set on the darker seat backs.
  focal: "the eight white binders on the dark seats"

art:
  technique: "physically based render in a TXT.interior room lit by the deck's rig through the window"
  why_this_technique: "the claim is a count of utilities heard in a room, and the room is where it was heard"
  palette: "dark upholstery, oak dais, window light, eight white binders, accent spine tabs"
  value_structure: >
    Lightest is the binders. Darkest is the hall wall behind the hook. Frame median L* planned at 9, rewritten from 26 after panel round 1 found the lit wall read as a plate behind the type, so the wall went dark and the value cut deepened.

type:
  hook: "Eight of 160 utilities had filed."
  dek: "The Tribune reports that count from a House hearing on wildfire mitigation plans, a different rule from resiliency plans. Four more had given a filing date and 135 were preparing plans. The PUCT's blueprint lists cameras as a \"Suggested\" tool, not a requirement."
  labels: ["ONE SEAT FOR EACH UTILITY THE HEARING COUNTED"]

verbatim:
  - c37: "Suggested"

acceptance:
  - "exactly 160 seats are modelled and exactly 8 carry a binder"
  - "eight separate white binder marks are countable at 432px"
  - "the witness podium stands in the well on the aisle, not among the seats"
  - "no flag, nameplate or cup crosses the dek, the label or the source line"
  - "the frame's median L* at 432px is between 5 and 20"

risks:
  - "a room set for 160 could imply the utilities attended, so the label names the seats as the count"
  - "the hero is absent from this one frame, by design"
```

```yaml
slide: 9
layout: FIGURE_SCALE
primary_image:
  subject: "a Texan at a galvanized pipe ranch gate closed across the caliche road 9.5 m out, lit on the camera side, a barbed wire fence of 30 T-posts leaving the gate's hinge side up the rise to the station 37 m out on the right third, both its heads turned to face the lens"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: none
job: >
  Give a Texan the place, the documents and the one formal way in.

claims: [c10, c9, c57, c34]
numerals:
  - value_from: c10
  - value_from: c9

data_in_art:
  figure: cameras_per_site
  drives: head count on the mast, both turned to face the lens

depth:
  eye: 1.6
  horizon: 900
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 8, Z: -70}

composition:
  structure: >
    The figure and the gate on the left third close to the lens, the fence line running from the
    gate up and to the right to the station on the right third, the road from frame 1 arriving at
    the gate.
  bands: >
    Top third, the hook and the dek on the storm deck. Middle third, the station, the fence line
    and the horizon. Bottom third, the galvanized pipe gate with its hinge post and chain, the figure from the waist up lit on the camera side, the pale caliche road with its wheel tracks and grass centre strip running to the gate, the first T-posts of the fence with their shadows.
  focal: "the figure's lit face and shoulders at the gate"

art:
  technique: "physically based render, a kit person at true scale beside the station"
  why_this_technique: "the claim is what a Texan can do, and a Texan at the gate below the machine is who does it"
  palette: "straw, caliche, galvanized gate, work clothes, storm deck"
  value_structure: >
    Lightest is the figure's lit side and the road. Darkest is the storm deck. Frame median L* planned at 31.

type:
  hook: "How many fires have the cameras detected?"
  dek: "Both filings are public on the PUCT Interchange, the order in Docket 57463 and the May 1st report in Project 57941. SPS says its 2027 annual report will carry a full year of data. Under the order that report will carry the same detections line."
  labels: []

verbatim: []

acceptance:
  - "the fence leaves the gate and recedes toward the station with no post crossing type"
  - "a pipe gate closes the road and the figure stands beside it"
  - "the figure stands at the gate turned toward the mast and reads as a person at 432px"
  - "the station's two heads face the lens"
  - "the hook asks the unanswered question and the dek names both filings and the 2027 report"
  - "the frame's median L* at 432px is between 22 and 42"

risks:
  - "the figure in the dark lesson, so the key comes from the camera side"
```
