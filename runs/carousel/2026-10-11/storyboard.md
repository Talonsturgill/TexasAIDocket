# Storyboard, 2026-10-11
# "The pens are counted. The AI isn't."

## The story, and what the fact check did to it

West Texas A&M University received a $9.75 million grant from the U.S. Department of Agriculture, which the
A&M System's release of October 7th calls the largest federal award in University history (c1), through
USDA's Research Facilities Act Program for a center for beef cattle research and innovation (c2). A
required dollar for dollar match, $4.875 million from the A&M System and $4.875 million from other sources,
brings the project to $19.5 million (c3), with the Texas Cattle Feeders Association, its members and donors
matching the System's share (c13). The research feedlot pairs 90 small research pens with 45
commercial-scale pens (c4) and plans four buildings (c5). Ground was broken in November 2025 next to WT's
Nance Ranch (c8), about seven miles east of Canyon, 2,393 acres given to WT in 1971 (c9). The release says
new feeding, health and handling techniques "can be evaluated with traditional and artificial
intelligence-powered approaches" (c6). **It names no AI tool, vendor, camera, model or result (c7).** On
September 1st USDA NASS counted 2,500 thousand cattle on feed in Texas's large feedlots, Nebraska 2,470,
Kansas 2,320 and the United States 11,163 (c17 to c20). The record carries the decision as tx-2026-0207.

**WHAT THE FACT CHECK CHANGED.**
- **No county is named on any frame.** The release says Canyon and Nance Ranch and never a county, so the
  claims file rejected Randall County as a location. Canyon is the place the deck names.
- **NIFA's own pages returned 503.** The award rests on the A&M System's release. The agency's name as the
  release spells it is never printed.
- **The 2019 AgriLife drones (c23, c24) are AgriLife's feedlot near Amarillo, not WT's.** No frame draws or
  names them. A director pitched a frame for them and it was refused for exactly this reason.
- **No pen size, layout or AI device is in the record.** Every pen and every animal is drawn to illustrate.

## Why this treatment, and what was grafted

Three directors pitched THE EVIDENCE (the bunk as the unit every count is drawn in), THE PLACE (one yard at
last light, the camera walking down a bunk) and THE PLAN, NOT THE PRACTICE (what the release names is lit,
what it leaves out stays dark). All three chose the chassis's `feed_bunk` as the hero on their own.

- From THE PLACE, the spine and the cover: the full bunk looking west into the seam with steers at the
  rail and an elevator on the horizon, the four precast sections as the money, the line of steers as the
  NASS count, and the person at the empty bunk on the close.
- From THE EVIDENCE, the measured frames: the unset section and four survey stakes for the four planned
  buildings, the map with the ranch and the gift drawn as squares of their areas, and the long lens that
  keeps equal units equal.
- From THE PLAN, NOT THE PRACTICE, the hook ("The pens are counted. The AI isn't."), the page clipped to the
  neck rail with the one AI sentence, the near triplet of pens staged as one subject, and the rule that the
  accent marks only the AI question.
- Refused: the 2019 AgriLife frame (it would sit an unrelated feedlot inside WT's deck), the NASS table as a
  flat canvas chart (the line of steers carries it rendered), the "NO TOOL, NO VENDOR" mono list in the sky
  (the blank tag says it as an object), and an empty bunk on the cover (a non-Panhandle reader needs the
  animals to read a feedyard at 432 px).

## The world, and the laws that hold it

**A PANHANDLE FEEDYARD AT LAST LIGHT.** The chassis is `assets/js/deck/2026-10-11-feedyard.js` and every
frame loads it. It declares `sky: lastLight` with the key at azimuth -79.1 and elevation 6.1, the sun's own
position over Randall County's centroid at 6:50 p.m. CDT on October 7th, the release's date, computed in
`compute.py` from NOAA's equations (figures `sun_engine_az`, `sun_elevation`). +x is east and +z is south.
The key rakes every bunk lip and every steer from the west and every cast runs long to the east.

1. **Start dark.** A near black sky with one warm seam low in the west, the subject in a pool of light, the
   yard behind it gone to the dark.
2. **Type is light, on the dark field**, and every wash only darkens.
3. **The ration is the deck's warmest thing and the tag is its one accent.** Nothing else is bright.
4. Every standing thing gets `TXT.contact`, every frame `TXT.weather`.
5. **Nothing drawn is WT's real yard.** The bunks, pens, cattle and stakes are drawn to illustrate and the
   deks say so.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#0A0909` | the DOM body behind the render |
| `accent` | `#E0956A` | dusk gold, the AI question and nothing else: the blank ear tag on 1 and 8, the rule beside the AI sentence on 7. Absent on 2, 3, 4, 5, 6 and 9 |
| `hook` | `#EEEAE0` | light type on the dark sky |
| `dek` | `#DCD6C8` | the dek |
| `concrete` | `#BDB3A2` | the precast bunk, the chassis material |

The world's materials: buff grey precast concrete, galvanized pipe going warm on its west faces, pale caliche
in the alleys and on the site yard, packed pen dirt in near black brown, steam flaked corn in pale gold in the
throat, Hereford red with white faces, a concrete elevator against the ember seam. No bluebonnet, no Gulf
blue, no granite red, no amber badge.

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE

1. **Motif evolution.** The one fence line bunk changes state with the argument: full with steers at the rail
   (1), four sections bracketed as money (2), the ranch it stands beside (3, as the site mark), multiplied
   into 135 pens on alleys with empty throats (4), one unset section on dunnage on bare caliche (5), a long
   rail lined with 22 steers (6), the post the release's sentence hangs on (7), the rail a tagged steer's head
   comes through (8), and fresh, fed and empty with a person beside it where one commercial pen meets two
   small ones (9).
2. **Camera move.** Low along the bunk into the seam (1), long lens square to the sections (2), the map from
   above (3), up over the alley (4), monument low on the pad (5), standing in the alley along the line (6),
   close at the post (7), closer at the head (8), and standing beside the person (9).

## The rotation

    FULL_BLEED  DIAGRAM  MAP  GRID  OBJECT_AND_CAPTION  SPLIT_HORIZON  DOCUMENT  CLOSE_CROP  FIGURE_SCALE

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | WIDE, eye 2.35 m in the feed alley west of a north to south bunk, looking south south east along it, horizon on the upper third | the feed bunk, precast J sections with dark joints and a gold windrow of flaked corn in the throat raked by the 6.1 degree west sun, a galvanized neck rail rim lit, four kit Hereford steers with their heads at the rail and contact shadows on the apron, the nearest filling the right third, a grain elevator in silhouette on the seam |
| 02 | MEDIUM, eye 1.1 m, long lens fov 14 at 26 m off the alley side | the 12.2 m bunk of four precast sections, concrete with joint grime and a worn lip, its windrow lit along the top, contact on caliche, DOM brackets under the sections |
| 03 | AERIAL, a plan at one scale measured from Canyon | the ranch square at its true area in the concrete tone with a soft lit edge, laid on the one mile survey sections, Canyon a lamp point, the gift square on its edge. No county line: neither the committed gazetteer nor a source this run may fetch places Canyon |
| 04 | AERIAL, 30 m up over the near end of a feed alley, looking along it about 15 degrees down, horizon in the top eighth | the near commercial pen and its two small partners across the alley, pen dirt floors worn and hoof pocked, pipe fences, empty concrete bunk throats, staged as one lit subject while 132 more pens run into the dark |
| 05 | MEDIUM, eye 0.6 m, 4.5 m off, looking north | one precast bunk section on two timber dunnage blocks on graded caliche, its J end raked by the key, grime at its base, contact marks under the timbers, four survey stakes with pale flagging receding behind it |
| 06 | WIDE, eye 1.5 m in the alley, looking east south east along a 22 m bunk, horizon on the upper third | the line of 22 Hereford steers at the rail, the near five full detail and side lit in the pool behind a pipe divider, the far seventeen instanced and falling into the dark, the windrow lit along the throat |
| 07 | CLOSE, eye 1.45 m, 1.1 m from a neck rail post, looking south | a letter page clipped to the galvanized rail with a binder clip, its lower edge curled, lit by the low west key against the near black sky, the empty dark throat and the rail running off the right edge |
| 08 | CLOSE, eye 1.15 m, 1.5 m off, looking south | a Hereford steer's head and dewlap through the neck rail, the kit's smooth hide with short hair, white face raked by the west key and the neck in shade, the dewlap over the bunk's grimed lip, the blank dusk gold tag in its near ear, the rail crossing upper left, the windrow along the lower left |
| 09 | MEDIUM, eye 1.6 m in a new pen, looking north east along a fresh bunk | a kit person in work clothes standing three quarters away at the rail, lit on the camera's side, the fed bunk with no animals at it, pipe dividers cutting it into one long pen and two short ones, the seam low left |

Showstopper frame: 01, a full bunk of gold ration running from the bottom left corner toward the horizon with nine white faces at the rail, the nearest raked by the low sun and carrying a blank dusk gold tag, and the sky gone near black above it
Tonal arc: near black around one lit bunk on 1 and 2, darkest on the map at 3, the pool tightening on the near pens at 4 and the pad at 5, the widest light along the line of steers at 6, lifting to the deck's brightest thing on 7 where the page is lit, darker and closer at 8, settling on 9 with one lit person at a fed bunk

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "a full concrete fence line feed bunk running north to south from the bottom left toward the upper right, nine Hereford steers with their heads at the neck rail on the left, the nearest filling the left third, the gold windrow lit in the throat"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#E0956A"
job: >
  Put the yard in front of the reader and say whose award this is, that the pens are counted and that the AI
  is not named.

claims: [c1, c4, c7]
numerals:
  - value_from: c1

data_in_art:
  figure: sun_elevation
  drives: the length of every rail post's cast down the apron, post height over tan of the key elevation

depth:
  eye: 2.35
  horizon: 470
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera stands raised in the feed alley west of a bunk that runs north to south, so the low west key
    lights every face at the rail and no steer shades the next. It looks south south east along the bunk,
    which runs from the bottom left toward the upper right with the gold windrow open in its throat. The
    steers stand behind the rail on the left of the run, the nearest close and large, the rest stepping away.
  bands: >
    Top third, the near black sky with the hook and dek. Middle third, the rail and the heads, the lit pen
    dirt on the right. Bottom third, the bunk's back wall and throat with the windrow, the alley caliche falling to
    the dark toward the camera.
  focal: "the nearest steer's white face and the gold windrow beside it, the lightest area in the frame"

art:
  technique: "physically based render of the kit Hereford and the chassis feed bunk staged in a lastLight world"
  why_this_technique: "a feedyard is a place a Panhandle reader knows by its bunk and its rail, and only a modelled, lit bunk reads as that place"
  palette: "precast grey, galvanized pipe, flaked corn gold, Hereford red and white, black pen dirt, one ember seam"
  value_structure: >
    Lightest is the white face and the windrow on the seam. Darkest is the sky and the near alley. Frame median L* planned at 12.

type:
  hook: "The pens are counted. The AI isn't."
  dek: "West Texas A&M received $9.75 million from USDA for a research feedlot near Canyon. The A&M System calls it the largest federal award in WT's history. The yard and the cattle are drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the feed bunk runs from the bottom left edge toward the horizon with a lit windrow of ration in its throat, and rendering no ration fails this item"
  - "the nearest steer stands at least 300 px tall at full size, its white face side lit from camera left or behind the camera"
  - "the bunk and the steers own at least a third of the frame height at 432px"
  - "at least three steers have their heads at the neck rail, each with a contact shadow on the apron"
  - "a blank dusk gold tag hangs in the nearest steer's ear, and it is the only dusk gold area in the frame"
  - "the sky above the hook is near black"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "the kit Hereford reads as plastic from behind, so no rump faces the camera"
  - "a long bunk straight down the axis can read as a flat line, so the throat's lit windrow must carry the depth"
```

```yaml
slide: 2
layout: DIAGRAM
primary_image:
  subject: "a 12.2 m bunk of four precast concrete sections seen square on through a long lens, three joints between them, a windrow along the top, brackets under the sections"
  rect: [0, 600, 1080, 520]
  bleeds: [left, right]
accent: none
job: >
  Show the money as the bunk's own units: the grant spans two sections and each half of the match spans one.

claims: [c1, c3, c13]
numerals:
  - value_from: c1
  - value_from: c3

data_in_art:
  figure: grant_sections
  drives: the bracket span under the sections, two sections for the grant and one for each half of the match, out of total_sections 4

depth:
  eye: 1.1
  horizon: 560
  cues: [CAST_SHADOW, AERIAL, RELATIVE_SIZE, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A long lens from the alley side, a little off square, so the four sections print at nearly one size and
    the joints read as the dividers between shares. The brackets sit under the bunk in the dark ground, each
    with its label.
  bands: >
    Top third, the sky with the hook and dek. Middle third, the bunk's back wall, the rail and the lit windrow.
    Bottom third, the brackets and their labels on the dark caliche.
  focal: "the lit windrow and the joints along the bunk's top edge, the lightest area"

art:
  technique: "physically based render, a long lens flattening equal units, DOM leaders"
  why_this_technique: "a dollar for dollar match is a statement about equal parts, and equal precast sections at one depth make the parts equal by construction"
  palette: "precast grey, galvanized pipe, flaked corn gold, dark caliche"
  value_structure: >
    Lightest is the windrow and the bunk's top edge. Darkest is the sky and the ground under the brackets. Frame median L* planned at 12.

type:
  hook: "USDA pays half. The match pays the rest."
  dek: "A required dollar for dollar match brings the project to $19.5 million. The A&M System puts in $4.875 million. The Texas Cattle Feeders Association, donors and other sources match it. Each section is drawn to stand for one $4.875 million share."
  labels: ["USDA GRANT $9.75 MILLION", "A&M SYSTEM $4.875 MILLION", "OTHER SOURCES $4.875 MILLION"]

verbatim: []

acceptance:
  - "the bunk shows exactly four precast sections with three dark joints between them"
  - "the far section prints at least 0.85 of the near section's length at full size"
  - "the grant's bracket spans exactly two sections and each match bracket spans exactly one"
  - "the bunk spans at least 80 percent of the frame width"
  - "no bracket or leader crosses a glyph"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "a perspective row would print the near share larger and lie about the match, so the lens stays long and the camera far"
```

```yaml
slide: 3
layout: MAP
primary_image:
  subject: "a plan at one scale measured from Canyon, laid on the one mile survey sections of the Panhandle, with the ranch drawn as a square of 2,393 acres and the gift as a square of 42.84 acres on its edge"
  rect: [0, 560, 1080, 640]
  bleeds: [left, right]
accent: none
job: >
  Put the feedlot somewhere a Texan can stand: about seven miles east of Canyon, beside a ranch the size of the
  square, broken ground last November.

claims: [c8, c9, c10]
numerals:
  - value_from: c9
  - value_from: c10

data_in_art:
  figure: ranch_square_side_m
  drives: the side of the ranch square at the map's own projected scale, with gift_square_side_m for the gift and ranch_offset_m for its distance east of Canyon

composition:
  structure: >
    The map window is set so Canyon sits on the left third and the ranch square about two thirds across, at
    one scale, with a leader from Canyon reading about seven miles east. The one mile survey sections are
    the scale, each a field in its own dark tone. No county is named and none is drawn.
  bands: >
    Top third, the hook and dek on the dark field. Middle third, Canyon's point, the leader and the ranch
    square. Bottom third, the gift square standing on the ranch's south edge with its lit west side, and the
    survey sections, each field in its own dark tone with its rows, running to the edge.
  focal: "the ranch square in the concrete tone, the lightest area"

art:
  technique: "TXGeo cartography on the committed Albers projection, areas drawn as squares at one scale"
  why_this_technique: "where the feedlot is and how big the ranch is are both distances, and a map at one scale is the only drawing that holds both"
  palette: "the deck's near black ground, caliche hairlines, the ranch square in precast grey"
  value_structure: >
    Lightest is the ranch square and the type. Darkest is the field. Frame median L* planned at 9.

type:
  hook: "The feedlot goes up beside WT's 2,393-acre ranch"
  dek: "The ranch lies about seven miles east of Canyon and was given to WT in 1971. Canyon ranchers Mike and Gary Kuhlman gave 42.84 acres beside it in 2024. Each is drawn as a square of its own area, not its real shape or exact place."
  labels: ["CANYON", "NANCE RANCH", "KUHLMAN GIFT", "ABOUT SEVEN MILES EAST", "EACH SQUARE IS ONE MILE ON A SIDE"]

verbatim: []

acceptance:
  - "the ranch square's side is computed from ranch_acres at the map's scale and the square spans at least 120 px at full size"
  - "no county is named on the frame, and every position is measured from Canyon at the one scale"
  - "the gift square sits on the ranch square's edge at the same scale"
  - "the one mile survey sections are drawn at the same scale as the squares"
  - "the frame's median L* at 432px is 18 or lower"

risks:
  - "a flat map between renders strobes, so the field holds the deck's near black and takes the deck's grade"
```

```yaml
slide: 4
layout: GRID
primary_image:
  subject: "a plan of 135 pens on feed alleys seen from 30 m up, the near commercial pen and its two small partners across the alley lit in the pool, the rest running into the dark"
  rect: [0, 560, 1080, 640]
  bleeds: [left, right]
accent: none
job: >
  Draw the count: 90 small research pens paired with 45 commercial-scale pens, every commercial pen facing two
  small ones.

claims: [c4]
numerals:
  - value_from: c4

data_in_art:
  figure: small_pens
  drives: the instanced pen count, 90 small and commercial_pens 45, 135 pen floors in all, two small pens of frontage facing each commercial pen

depth:
  eye: 30
  horizon: 150
  cues: [LINEAR_PERSPECTIVE, TEXTURE_GRADIENT, AERIAL, CAST_SHADOW, RELATIVE_SIZE]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera stands over the near end of one feed alley and looks down its length. The near commercial pen
    and the two small pens across from it are lit in the pool, and the rows recede to the horizon through the
    stage fog so the count reads as a field of units without any one standing out.
  bands: >
    Top third, the seam on the horizon and the hook in the dark sky. Middle third, the rows receding along the
    alley. Bottom third, the lit triplet and the two bunk lines facing across the alley.
  focal: "the near commercial pen's lit bunk and its two small partners, the lightest area"

art:
  technique: "physically based render of an instanced count staged as one subject, texture gradient down the alley"
  why_this_technique: "a count is a grid of real units, and a lit near triplet tells the reader what one unit of the pairing is before the rows say how many"
  palette: "pen dirt near black, caliche alleys, precast grey bunks, galvanized pipe"
  value_structure: >
    Lightest is the lit triplet's bunks and alley. Darkest is the far rows and the sky. Frame median L* planned at 12.

type:
  hook: "90 research pens paired with 45 commercial ones"
  dek: "That is 135 pens in all. Each commercial-scale pen here faces two small research pens across a feed alley. The layout and pen sizes are drawn to illustrate the count."
  labels: ["45 COMMERCIAL-SCALE PENS", "90 SMALL RESEARCH PENS"]

verbatim: []

acceptance:
  - "the plan carries exactly 135 pen floors, 90 small and 45 commercial-scale"
  - "the lit commercial pen faces exactly two lit small pens across one feed alley"
  - "the horizon and the seam show in the top eighth of the frame"
  - "the pens fill at least half of the frame's area"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "a camera looking down trips the no sky check, so the horizon stays in frame"
  - "135 units can read as texture, so the lit triplet carries the unit"
```

```yaml
slide: 5
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "one precast bunk section on two timber dunnage blocks on bare graded caliche, four survey stakes with pale flagging receding behind it"
  rect: [0, 700, 1080, 650]
  bleeds: [left, right, bottom]
accent: none
job: >
  Say the four buildings are planned and the ground is broken, so the feedlot is still a plan.

claims: [c5, c8]
numerals:
  - value_from: c8

data_in_art:
  figure: components
  drives: the number of survey stakes behind the section, 4, one per planned building, labelled in the release's order

depth:
  eye: 0.6
  horizon: 620
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera is low on the pad and close, so the section fills the lower band with its J end turned to the
    west key. The four stakes recede at 7, 15, 27 and 45 m behind it on a string line, each with its label in
    the dark above it.
  bands: >
    Top third, the sky with the hook and dek. Middle third, the stakes and their labels against the seam.
    Bottom third, the section on its dunnage, the caliche and its contact marks.
  focal: "the lit J end of the section, the lightest area"

art:
  technique: "physically based render on a worn caliche ground, a receding row for depth"
  why_this_technique: "an unset precast section on timber is what a funded and unbuilt feedlot looks like at ground level"
  palette: "pale caliche, precast grey, raw pine dunnage, pale flagging"
  value_structure: >
    Lightest is the lit J end and the caliche in the pool. Darkest is the sky. Frame median L* planned at 14.

type:
  hook: "Ground is broken. Four facilities are planned."
  dek: "Ground was broken in November 2025. Plans call for a precision beef cattle handling facility, a veterinary care and research hospital, an advanced technology feed and production center and a metabolism and physiology center. The section and stakes are drawn to illustrate."
  labels: ["CATTLE HANDLING FACILITY", "VETERINARY HOSPITAL", "FEED AND PRODUCTION CENTER", "METABOLISM AND PHYSIOLOGY CENTER"]

verbatim: []

acceptance:
  - "one precast section with its J profile lit at one end rests on two dunnage blocks, each with a contact mark on the caliche"
  - "exactly four survey stakes stand behind it, each with pale flagging and its own label"
  - "the section spans at least 50 percent of the frame width"
  - "the stakes' labels sit in the dark and no label crosses a stake"
  - "the frame's median L* at 432px is 25 or lower"

risks:
  - "a section on dunnage can read as a concrete block, so the J end is lit hard and turned to the camera"
```

```yaml
slide: 6
layout: SPLIT_HORIZON
primary_image:
  subject: "a line of 22 Hereford steers at one long bunk, the near five behind a pipe divider lit in the pool, the far seventeen stepping off into the dark"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: none
job: >
  Say why the Panhandle: Texas had more cattle on feed on September 1st than Nebraska or Kansas, and the
  near pen of five out of a line of 22 is its share.

claims: [c17, c18, c19, c20]
numerals:
  - computed_by: "out/2026-10-11/compute.py, tx_on_feed_m, ne_on_feed_m, ks_on_feed_m, us_on_feed_m, tx_share_us_pct"

data_in_art:
  figure: tx_steers
  drives: the steer count in the near pen, 5, against us_steers 22 in the whole line, one steer per steer_unit_k 500 thousand head

depth:
  eye: 1.5
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera stands in the alley and looks east south east down the bunk, the west key behind its right
    shoulder lighting every face. The near five stand in the pool behind a divider that closes their pen,
    and the line runs on past it to the dark.
  bands: >
    Top third, the dark sky with the hook and dek. Middle third, the heads at the rail and the line receding.
    Bottom third, the bunk's back wall in shadow and its gold windrow lit along the throat, the alley caliche
    worn and hoof marked running to the frame's bottom edge.
  focal: "the five lit faces in the near pen, the lightest area"

art:
  technique: "physically based render of an isotype count staged on the near five, an instanced line behind"
  why_this_technique: "a share of a national count is a part of a line, and steers at a rail are the line a reader in a feedyard county already knows"
  palette: "Hereford red and white, precast grey, flaked corn gold, near black pen dirt"
  value_structure: >
    Lightest is the five faces and the windrow. Darkest is the sky and the far line. Frame median L* planned at 13.

type:
  hook: "Texas's large feedlots held more cattle than Nebraska's or Kansas's"
  dek: "On September 1st USDA estimated 2.5 million cattle on feed in Texas's large feedlots, 2.47 million in Nebraska and 2.32 million in Kansas. Texas held 22 percent of the 11.16 million nationwide. Each steer is drawn to stand for 500 thousand head."
  labels: ["TEXAS", "UNITED STATES"]

verbatim: []

acceptance:
  - "exactly 22 steers stand at the rail and exactly 5 of them stand in the near pen behind a pipe divider"
  - "the near five are side lit with their faces on the camera's side and each stands at least 120 px tall at full size"
  - "all 22 heads are separable at 432px"
  - "the line of steers and the bunk own at least a third of the frame height at 432px"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "the stage fog can swallow the far seventeen, so the stage depth is tuned to keep them as dark forms against the pen dirt"
```

```yaml
slide: 7
layout: DOCUMENT
primary_image:
  subject: "a letter page clipped to the bunk's galvanized neck rail with a binder clip, its lower edge curled, the release's one AI sentence set on it with a dusk gold rule in the margin"
  rect: [140, 420, 800, 860]
  bleeds: []
accent: "#E0956A"
job: >
  Show the one sentence the release spends on AI, word for word, hung on the thing it is about.

claims: [c6, c7]
numerals: []

depth:
  eye: 1.45
  horizon: 430
  cues: [CAST_SHADOW, OCCLUSION, AERIAL, RELATIVE_SIZE]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera stands close and nearly square to the page, which hangs from the rail and turns a little toward
    the west key so the key lights it. The rail crosses the upper part of the frame and runs off both sides,
    the empty dark throat sits under the page.
  bands: >
    Top third, the dark sky and the hook. Middle third, the rail and the page's upper half with the sentence.
    Bottom third, the page's curled lower edge throwing a thin shadow, the bunk's lip and dark throat, the
    concrete back wall raked along its top edge by the key and grimed toward the alley.
  focal: "the lit page and its sentence, the lightest area in the frame"

art:
  technique: "physically based render of a drawn document in the world, DOM type registered to the page"
  why_this_technique: "the claim is a document's own words, and a page hung on the bunk reads as that document where the work would happen"
  palette: "paper white in warm key light, galvanized pipe, near black sky and throat, one dusk gold rule"
  value_structure: >
    Lightest is the page. Darkest is the sky and the throat. Frame median L* planned at 16.

type:
  hook: "The release mentions AI once"
  dek: "The mention is a planned way of evaluating techniques. The page is drawn to illustrate. The words are the release's own."
  labels: ["New feeding, health and handling techniques can be evaluated with traditional and artificial intelligence-powered approaches that are designed to increase beef production efficiency and advance feedlot management practices."]

verbatim:
  - c6: "New feeding, health and handling techniques can be evaluated with traditional and artificial intelligence-powered approaches that are designed to increase beef production efficiency and advance feedlot management practices."

acceptance:
  - "the page carries the c6 sentence verbatim and no other legible line"
  - "a dusk gold rule runs in the page's margin beside the sentence, and rendering no rule fails this item"
  - "the page owns at least 30 percent of the frame and the rail crosses the frame above it"
  - "the frame's median L* at 432px is 30 or lower"

risks:
  - "a bright page in a dark deck reads as a cream ground, so it stays a page in a dark field and under 40 percent of the frame"
```

```yaml
slide: 8
layout: CLOSE_CROP
primary_image:
  subject: "a Hereford steer's head and dewlap through the neck rail, white face raked by the west key, a blank dusk gold tag in its near ear"
  rect: [300, 380, 780, 970]
  bleeds: [right, bottom]
accent: "#E0956A"
job: >
  Name what the release leaves out, on the one object a feedyard would read: no tool, no vendor, no camera, no
  model, no result.

claims: [c7]
numerals: []

depth:
  eye: 1.15
  horizon: 420
  cues: [OCCLUSION, CAST_SHADOW, RELATIVE_SIZE]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The head comes through the rail toward the camera's left, cropped by the top and right edges, the rail
    crossing the upper left in the foreground. The tag hangs in the lit ear and the windrow runs along the
    lower left.
  bands: >
    Top third, the dark sky with the hook and dek, the rail. Middle third, the face, the ear and the tag.
    Bottom third, the dewlap's folds in shade, the bunk's concrete lip and the gold windrow in the throat
    with its flakes lit and raked by the key, the dewlap's shadow falling across the lip.
  focal: "the white face and the tag in the ear beside it, the lightest area"

art:
  technique: "physically based render at detail scale, close crop with foreground occlusion"
  why_this_technique: "a blank tag on a real animal says nothing is written down yet without drawing a device the record never names"
  palette: "Hereford white and red, galvanized pipe, flaked corn gold, one dusk gold tag"
  value_structure: >
    Lightest is the white face. Darkest is the sky and the shadowed neck. Frame median L* planned at 16.

type:
  hook: "No AI tool, vendor or result is named"
  dek: "The release names no camera or model either. The blank tag is drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the steer's head owns at least 35 percent of the frame and is cropped by the top or right edge"
  - "a blank dusk gold tag hangs in the near ear, at least 40 px tall at full size, with nothing printed on it"
  - "the neck rail crosses the frame in front of or above the head"
  - "the frame's median L* at 432px is 25 or lower"

risks:
  - "the kit head at this scale may read as a toy, so the key is on the camera's side and the crop stays at head and dewlap"
```

```yaml
slide: 9
layout: FIGURE_SCALE
primary_image:
  subject: "a person standing three quarters away at a fresh bunk with ration in its throat and no animals, pipe dividers cutting it into one long pen and two short ones"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: none
job: >
  Close on who runs the research and the question the release leaves open: which tool, and what result.

claims: [c1, c6, c7, c16]
numerals: []

data_in_art:
  figure: small_per_commercial
  drives: the divider count along the bunk, one commercial-scale pen of frontage then two small pens of half its frontage

depth:
  eye: 1.6
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera stands in the new pen and looks north east along the bunk, the key over its left shoulder
    lighting the person on the side the camera sees. The person stands at the rail at true scale, which gives
    the bunk its size, and the dividers step down the run behind them.
  bands: >
    Top third, the dark sky with the hook and dek. Middle third, the person's head and shoulders against the
    seam, the rail. Bottom third, the bunk's concrete lip and its lit gold windrow, the apron with contact
    under the person's boots and the hoof pocked pen dirt running off the frame.
  focal: "the lit windrow and the person's lit side, the lightest area"

art:
  technique: "physically based render with the kit person as the scale reference"
  why_this_technique: "a question about who measures what is a question about a person at the bunk"
  palette: "work clothes, precast grey, flaked corn gold, galvanized pipe, near black pen"
  value_structure: >
    Lightest is the windrow and the person's lit side. Darkest is the sky. Frame median L* planned at 13.

type:
  hook: "Which tool, and what result?"
  dek: "The release ties the work to WT's Feedlot Research Group. The grant is awarded. The AI approaches are a plan. The person and the pens are drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "a person stands at the rail at true scale, at least 300 px tall at full size, lit on the camera's side"
  - "the bunk carries a lit windrow and no animal stands at it"
  - "pipe dividers cut the bunk into one long pen then two short pens of half its frontage"
  - "the frame's median L* at 432px is 22 or lower"

risks:
  - "a figure against the seam goes to a silhouette, so the key stays on the camera's side"
```
