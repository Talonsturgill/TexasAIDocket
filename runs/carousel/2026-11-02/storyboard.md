# Carousel no. 66, November 2nd, 2026: the dog count on the car window

## The story, and what the fact check did to it

San Antonio Animal Care Services and Southwest Research Institute are repeating the city's 2019 manual
count of unrestrained dogs with a cell phone mounted on a vehicle window and object detection software
(c1, c2, c3, c15, c18). Automated and human review of each clip checks four things: whether the dog was
unrestrained, any human supervision, the number of dogs present, and whether it was owned or a stray
(c4, c5). The owned or stray call is made by appearance (c6, c7). The survey covers the same 32 study
areas as 2019 (c8, c17), is a sample and not a count of every dog (c12, c19), runs October to December
(c10, c20), and ends in a final report to Animal Care Services (c11, c21). The fact checker held the
release's own words (malnourished and skittish, not undernourished and wary) and found no reachable 2019
finding (c22 names the study, nothing more). So the deck draws no count, no accuracy and no result.

Docket item tx-2026-0236, admitted this run on the city's release and SwRI's.

## Why this treatment, and what was grafted

Base: THE CAMERA'S EYE. The deck is built from where the machine sits, a phone on a car window rolling
down a San Antonio street at last light, then hands the clip to the person who checks it, then leaves the
machine for the record. Its motif, a thin dusk gold detection box of four corners, carries the review's
four checks and changes state frame by frame.

Grafted from THE MEASURED SAMPLE: the 32 study areas as caliche plugs pressed up out of a black clay city
plan (frame 6), the 2019 to 2026 span as a mould of 32 empty pockets beside 32 cast plugs on a steel
rule of 7 divisions (frame 7), and the field window as a caliche block over 3 month graduations on a
steel rule cropped at both edges (frame 8). Those beat the base's brass boxes, sidewalk slabs and kerb
card, each of which risked a charge the last three decks already took (embossed calendar, kit person as
mannequin, flat grey card). Grafted from THE NEIGHBORHOOD: one built block whose fixed coordinates (house, fence line, driveway, kerb, streetlight, oak) live in the chassis so every street frame is the same street from a new position, a sheen on the coat so the raking key draws a fur rim at feed size, and no added practical light, so no lamp clips its neighbours (no. 65's lesson).

The dog was prototyped before the synthesis. A tube built dog read as a toy at 3 m; a signed distance
body meshed by `K.sdfMesh`, with the hock angulated, reads as a lean street dog at 5 m. So no frame puts
a dog closer than about 4 m to the lens, and every dog is in the light pool.

## The world, and the laws that hold it

`lastLight`, staged. The key is azimuth -58, elevation 12: +x east, +z south, so a camera looking north
has the key on its left, lit edges on the left and casts running to the right. TXBENCH reliefs read the
same light raked from the upper left. One subject sits in a pool on the ground; the street behind it goes
dark. Type is light on the dark sky or dark ground. A wash only darkens.

## Palette

limestone #EDE6D6, caliche #E4D8C3, clay #17130F, dusk_gold #E0956A, asphalt #1C1C1F

West side San Antonio at the end of the day: cream limestone (#EDE6D6), caliche (#E4D8C3), black clay
(#17130F), straw parkway, galvanized chain link, live oak near black, near black asphalt, the warm seam.
The accent is dusk_gold #E0956A and it means ONE thing, the machine's detection: the box on frames 1, 3
and 4. Frames 2 and 5 carry it small, on a screen, too small to count as the frame's colour.

## The continuity devices

CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE, VALUE_ARC

1. **Motif evolution.** The gold four cornered box: around the dog in the lens view (1), drawn as four
   sight lines from the phone to its corners (3), split in two over two dogs (4), on the reviewer's
   paused clip (5), then gone from 6 to 9 as the deck leaves the machine for the record and the street.
2. **One dog.** The same tan dog (seed 66) on 1, 3, 5 and 9, at the lens on 1 and at its own height on 9.
3. **Value arc, last light to night.** The seam visible behind the street on 1 to 4, the dark room on 5,
   the reliefs in a pool on 6 to 8, the darkest sky on 9 with the camera turned away from the seam.

## The rotation

    FULL_BLEED  CLOSE_CROP  DIAGRAM  OBJECT_AND_CAPTION  CLOSE_CROP  GRID  FIGURE_SCALE  DIAGRAM  OBJECT_AND_CAPTION

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | MEDIUM, eye 1.15 m at the lens inside the car window, fov 32 | the chassis street_dog, tan, full, mid step on a straw parkway 5 m out, one SDF body with fur normals, seated by TXT.contact in the pool, a kit chain_link_fence and a limestone kit ranch_house dark behind, the crossover's black rubber window seal cropping the left and bottom edges in the foreground |
| 02 | CLOSE, eye 1.36 m on the rear seat, 0.8 m behind the phone, fov 40 | the chassis window_phone clamped over the kit crossover's lowered rear glass, an aluminium handset whose lit screen carries a render target of the lens view, the boxed tan dog, rubber jaws and an arm to the clamp, the real street dark beyond the opening with the dog in its pool on the parkway |
| 03 | WIDE, eye 3.9 m above and behind the car's rear quarter, fov 21, the car cropped out below the frame (recomposed in scoring round 2) | the street_dog on the parkway inside a gold box of four labelled corners, the dog seated by TXT.contact in the pool and drawn over the corner marks |
| 04 | MEDIUM, eye 1.1 m at the lens, fov 34 | two chassis street_dog bodies 1.3 m apart on one parkway, a brown lean dog with its head below its back, ribs showing and tail tucked, and a tan fuller dog with its head up and ears pricked stepping toward the car, both in the pool with contact shadows |
| 05 | CLOSE, eye 1.3 m at a reviewer's seat in a dark room, fov 42 | a kit monitor whose screen carries a render target of the lens view, the tan dog boxed in gold, beside four lit check rows, on a kit desk whose wood edge takes the screen's light, TXT.interior dark around it with its window on the left |
| 06 | AERIAL, orthographic material relief | a black clay city plan of grooved streets and low lots running off every edge, matte clay with grain in its albedo, raked by the deck's low key, the street grooves weathered with a darker fill, carrying 32 caliche plugs in 4 rows of 8 standing proud, chamfered, sawn caliche with straight saw marks in the albedo, each casting to the lower right, a keyMask pool falling off to black |
| 07 | AERIAL, orthographic material relief | a black clay slab with 32 empty square pockets in 4 rows of 8, matte clay with grain in its albedo, each pocket cut with one lit wall and one shadowed wall under the deck's key and dust settled in its floor, a brushed steel rule inlaid below it cut into 7 equal divisions with crisp grooves, and 32 sawn caliche plugs in the same arrangement standing proud below the rule with gold chamfers, casting to the lower right |
| 08 | AERIAL, orthographic material relief | a brushed steel survey rule cropped at both edges with month grooves, set into black clay, its edge catching the key and its face worn along the middle, a sawn caliche block with chisel courses in its albedo standing over exactly 3 graduations with a long cast, and a small separate caliche plug off the graduations for the final report |
| 09 | MEDIUM, eye 0.75 m near the dog's height, 4.4 m from it, fov 34 | the tan street_dog standing where the driveway crosses the sidewalk, turned three quarter away and looking east down a dark street where the kit crossover's tail lamps are small, a kit chain_link_fence receding on the left, broom finished concrete underfoot with a contact shadow, the seam behind the camera |

Showstopper frame: 01, the lens view through the car window, the tan dog mid step in the last warm light inside a thin gold box, the seal cropping two edges; its depth is the window seal occluding the foreground, the dog's cast and contact on the parkway, and the fence and house falling into haze.
Tonal arc: the warm pool on the dog against the seam on 01, the phone's aluminium edge in the dark door on 02, the gold corners on 03, two dogs in one pool on 04, the screen's glow in the dark room on 05, the caliche plugs in a pool on 06, mould and cast on 07, the field block on the rule on 08, and the darkest sky on 09.
VALUE CUT: frame 6. The deck turns from what the machine sees to what the record can say.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "a tan street dog mid step on a straw parkway at last light, seen through the open window of a car from the phone's own position, a thin gold four cornered box around it, the black window seal cropping the left and bottom edges"
  rect: [0, 600, 1080, 750]
  bleeds: [left, right, bottom]
accent: "#E0956A"
job: >
  Put the reader where the survey's camera sits, looking at a loose dog on a San Antonio street the way
  the software sees it, before any claim is made about it.

claims: [c1, c2, c3, c9, c15]
numerals:
  - value_from: c9

data_in_art:
  figure: review_checks
  drives: corner count of the detection box, one corner per check

depth:
  eye: 1.15
  horizon: 600
  cues: [OCCLUSION, CAST_SHADOW, RELATIVE_SIZE, AERIAL, LINEAR_PERSPECTIVE]
  subject_at: {X: 0, Z: -5}

composition:
  structure: >
    The window seal and the door glass occlude the left and bottom edges, so the reader is inside the car.
    The dog stands in the pool of light at the centre right, 5 m out, the fence and the house behind it
    falling dark, the box drawn around the dog alone.
  bands: >
    Top third, the dark sky with the kicker, the hook and the dek. Middle third, the house and fence going
    dark with the dog in its pool. Bottom third, the lit parkway and the dog's cast, cropped by the seal.
  focal: "the dog in the pool, inside the gold box, the brightest form in the frame"

art:
  technique: "physically based render of the chassis street_dog on a straw parkway in the lastLight world, staged on the dog, with the kit crossover's window seal in the foreground and a DOM drawn box of four corners"
  why_this_technique: "a modelled street in perspective puts the reader at the lens, which is the whole subject of the story"
  palette: "warm tan coat in the pool, straw parkway, galvanized fence, dark limestone, near black sky with the warm seam"
  value_structure: >
    Lightest is the dog's lit flank and the pool. Darkest is the window seal and the sky above the roofline.
    Frame median L* planned at 4 (the arc rewritten after the render, see the run record).

type:
  hook: "A phone on a vehicle window will survey San Antonio's loose dogs"
  dek: "Southwest Research Institute and the city's Animal Care Services will repeat a 2019 manual survey with machine vision software. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "a four legged dog with a head, a tail and four separate legs is identifiable at 432 px"
  - "the dog stands inside the gold box and the box encloses nothing else"
  - "the box has exactly four corner marks"
  - "a dark window seal crops the left edge of the frame"
  - "the dog casts a shadow on the parkway and touches it with a contact shadow"
  - "the dog's figure stands at least 120 px tall at 432 px"
  - "no box line or seal crosses a glyph of the hook or dek"
  - "the frame's median L* at 432 px is 30 or lower"
risks:
  - "the dog reads as a toy at close range, so it stays 5 m out and in the pool, never nearer"
```

```yaml
slide: 2
layout: CLOSE_CROP
primary_image:
  subject: "a smartphone clamped over the lowered rear glass of the survey car, seen from inside the cabin, its screen showing the lens view of the tan dog boxed in gold while the real dog steps along the parkway beyond the window"
  rect: [150, 520, 780, 600]
  bleeds: []
accent: "none"
job: >
  Show the instrument plainly. The whole survey rests on an ordinary phone clipped to a car window.

claims: [c2, c3, c18]
numerals: []

depth:
  eye: 1.25
  horizon: 420
  cues: [OCCLUSION, CAST_SHADOW, RELATIVE_SIZE, FORM_SHADING]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The car's rear door fills the frame as a dark field, cropped by the left, right and bottom edges. The
    phone and its clamp stand on the top edge of the lowered glass at the centre, lit by the key from the
    left, the lens island facing the reader. The roofline and a band of sky sit above.
  bands: >
    Top third, sky above the roof with the type. Middle third, the window opening with the phone on the
    glass edge. Bottom third, the door's dark dust grey metallic panel, its shoulder crease catching the warm key as a long highlight, the lower door falling to near black with road grime along the sill.
  focal: "the three lens discs on the phone's back, the brightest specular points in the frame"

art:
  technique: "physically based render of the chassis window_phone on the kit crossover's rear glass in the lastLight world, staged on the phone"
  why_this_technique: "an aluminium handset and glass need real specular response to read as a phone rather than a slab"
  palette: "dust grey metallic door, bead blasted aluminium, black glass and rubber, the warm key"
  value_structure: >
    Lightest is the phone's lit edge and the lens rings. Darkest is the cabin behind the glass and the
    lower door. Frame median L* planned at 3 (the arc rewritten after the render, see the run record).

type:
  hook: "The camera is a phone"
  dek: "The release describes \"a cellular phone mounted to a vehicle window with object detection and data analysis software\"."
  labels: []

verbatim:
  - c3: "a cellular phone mounted to a vehicle window with object detection and data analysis software"

acceptance:
  - "the phone stands at least 110 px tall at 432px"
  - "a phone with three separate round lenses is identifiable at 432 px"
  - "the phone sits on the top edge of a window glass, held by a clamp"
  - "the phone and clamp own at least a sixth of the frame"
  - "the car body fills at least half the frame as a dark field"
  - "no phone edge or reflection crosses a glyph of the hook or dek"
  - "the frame's median L* at 432 px is 30 or lower"
risks:
  - "a phone can read as a black slab, so its aluminium edge and lens rings carry the key and the glass shows a reflection"
```

```yaml
slide: 3
layout: DIAGRAM
primary_image:
  subject: "the dog on the parkway seen from above and behind the survey car, inside a gold box whose four corners each carry one check (recomposed in scoring round 2: the car and the long lines are cropped out, see the run record)"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#E0956A"
job: >
  Draw what the software does to a street: it puts a box around a dog, and each corner of that box is a
  question the review then answers.

claims: [c4, c5]
numerals:
  - computed_by: "compute.py, review_checks"

data_in_art:
  figure: review_checks
  drives: number of sight lines and labelled box corners

depth:
  eye: 3.4
  horizon: 380
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: -9}

composition:
  structure: >
    The car's rear quarter is cropped by the left and bottom edges. From the phone on its window four thin
    lines run out across the parkway and converge on a box standing around the dog in the pool, so the eye
    travels from the instrument to the subject along the lines.
  bands: >
    Top third, the dark sky and the type. Middle third, the dog in its box on the parkway with the four
    corner labels. Bottom third, the car's dark metallic roof modelled in a gradient from a lit rail to a shadowed crown, the rear glass with the phone on the window reflecting the seam, the roof's cast falling on the asphalt, cropped by the bottom and left edges.
  focal: "the dog inside the four labelled corners"

art:
  technique: "physically based render of the kit crossover, the window_phone and the street_dog in the lastLight world, with four emissive tubes and a box frame modelled in the scene"
  why_this_technique: "the view frustum drawn into the street makes the detection physical and countable"
  palette: "dark car, gold lines, straw parkway in the pool, dark houses"
  value_structure: >
    Lightest is the dog in the pool and the gold lines. Darkest is the sky and the street beyond the pool.
    Frame median L* planned at 6 (the arc rewritten after the render, see the run record).

type:
  hook: "Four checks on each clip"
  dek: "Video clips will go to automated and human review. Each detected dog will be checked."
  labels: ["unrestrained", "human supervision", "number of dogs present", "owned or a stray"]

verbatim:
  - c5: "determine any human supervision, verify the number of dogs present and assess whether the dog was owned or a stray"

acceptance:
  - "the dog stands at least 60 px tall at 432px inside the four corners"
  - "no corner mark touches a check word"
  - "exactly four labelled box corners"
  - "each of the four corner labels sits beside its own corner"
  - "a dog stands inside the box"
  - "no corner mark crosses a glyph of any label, hook or dek"
  - "the frame's median L* at 432 px is 30 or lower"
risks:
  - "the box over a render can read as a UI mock, so the box and lines are modelled in the scene and cast nothing but glow"
```

```yaml
slide: 4
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "two dogs on the same parkway in the same light, a brown lean dog with its head below its back and tail tucked, a tan fuller dog with its head up stepping toward the camera, each inside its own gold box"
  rect: [0, 600, 1080, 750]
  bleeds: [left, right, bottom]
accent: "#E0956A"
job: >
  Show the call the release describes. The two labels are the same kind of animal a few postures apart,
  and the difference is read from how each dog looks.

claims: [c6, c7]
numerals:
  - computed_by: "compute.py, classes"

data_in_art:
  figure: classes
  drives: number of boxed dogs and the build and pose each is made in

depth:
  eye: 1.1
  horizon: 560
  cues: [CAST_SHADOW, RELATIVE_SIZE, OCCLUSION, AERIAL, FORM_SHADING]
  subject_at: {X: 0, Z: -5.5}

composition:
  structure: >
    The two dogs stand 1.7 m apart at the same distance, the lean one on the left by the fence, the full
    one on the right a step forward. Each has its box, and its label sits under the box on the dark ground.
  bands: >
    Top third, the dark sky with the type. Middle third, the two dogs in one pool with their boxes.
    Bottom third, the straw parkway in the pool with each dog's long cast running to the right and the kerb's lit edge, the two labels set on the dark grass below the boxes.
  focal: "the two dogs side by side in the pool"

art:
  technique: "physically based render of two chassis street_dog bodies, lean and wary, full and stepping, in the lastLight world, staged on both"
  why_this_technique: "one SDF body in two builds and poses makes the difference a matter of shape and carriage, which is what the release says the call rests on"
  palette: "brown and tan coats in a warm pool, straw parkway, galvanized fence"
  value_structure: >
    Lightest is the tan dog's flank and the pool. Darkest is the brown dog's shadow side and the sky.
    Frame median L* planned at 5 (the arc rewritten after the render, see the run record).

type:
  hook: "Two labels for a loose dog"
  dek: "The release says strays \"appear to be malnourished and skittish\". Dogs that seem healthier and more approachable \"are likely owned by local families and are classified as roaming.\" Drawn to illustrate."
  labels: ["stray", "roaming"]

verbatim:
  - c6: "Strays appear to be malnourished and skittish"
  - c7: "are likely owned by local families and are classified as roaming."

acceptance:
  - "each dog stands at least 70 px tall at 432px"
  - "two dogs are identifiable at 432 px, each with four legs, a head and a tail"
  - "the left dog's head is lower than its back and its tail hangs between its hind legs"
  - "the right dog's head is above its back"
  - "each dog sits inside its own gold box and the boxes do not overlap"
  - "the labels stray and roaming sit under the left and right boxes"
  - "each dog touches the ground with a contact shadow"
  - "the frame's median L* at 432 px is 30 or lower"
risks:
  - "a lean dog could read as a verdict or as cruelty, so the lean dog is lean and never emaciated, with no sores"
```

```yaml
slide: 5
layout: CLOSE_CROP
primary_image:
  subject: "a computer monitor on a reviewer's desk in a dark room showing a paused street clip with a tan dog inside a gold box, four lit check rows beside it"
  rect: [100, 650, 900, 520]
  bleeds: []
accent: "none"
job: >
  Hand the clip from the machine to a person. The release says automated and human review verifies what
  the software found.

claims: [c4, c5]
numerals:
  - computed_by: "compute.py, review_checks"

data_in_art:
  figure: review_checks
  drives: number of lit check rows on the screen

depth:
  eye: 1.2
  horizon: 520
  cues: [OCCLUSION, RELATIVE_SIZE, CAST_SHADOW, FORM_SHADING]
  subject_at: {X: 0, Z: -0.8}

composition:
  structure: >
    From the reviewer's seat, the monitor fills most of the frame width and glows in a dark room. The screen holds the lens view with the boxed dog on its left
    and four short lit rows on its right.
  bands: >
    Top third, the dark wall with the type. Middle third, the monitor and its glow. Bottom third, the desk's wood edge lit by the screen, the keyboard's keys catching the glow, and the monitor's base and neck modelled in the screen light.
  focal: "the boxed dog on the screen, the brightest area"

art:
  technique: "physically based render of a TXT.interior room with a kit desk and monitor, the screen mapped with a render target of the street scene"
  why_this_technique: "the paused clip on a real screen in a dark room puts the human review in a place"
  palette: "dark walls, the screen's glow, the clip's warm pool, the gold box"
  value_structure: >
    Lightest is the screen. Darkest is the room's corners. Frame median L* planned at 4 (the arc rewritten after the render, see the run record).

type:
  hook: "A person reviews the clips too"
  dek: "The release says automated and human review of the video clips \"will verify that the detected animals were unrestrained.\""
  labels: []

verbatim:
  - c4: "Automated and human review of the video clips will verify that the detected animals were unrestrained"

acceptance:
  - "the monitor owns at least a third of the frame width at 432px"
  - "a monitor showing a dog inside a gold box is identifiable at 432 px"
  - "exactly four lit rows sit beside the clip on the screen"
  - "the desk's front edge runs across the lower part of the frame, lit by the screen"
  - "the room is dark around the screen with its corners near black"
  - "the frame's median L* at 432 px is 30 or lower"
risks:
  - "the kit person reads as a mannequin up close, so no person is drawn and the seat is the camera"
```

```yaml
slide: 6
layout: GRID
primary_image:
  subject: "a black clay city plan of grooved streets and lots running off every edge, with 32 pale caliche plugs in 4 rows of 8 standing proud and casting"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "none"
job: >
  Show the sample as a sample: 32 places lifted into the light, counted and not placed, with the rest of
  the city still there in the dark.

claims: [c8, c17, c12, c19]
numerals:
  - value_from: c8

data_in_art:
  figure: study_areas
  drives: plug count, 4 rows of 8

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The plan runs off three edges as a dark grooved field. 32 plugs stand in a regular block in its lower
    two thirds, each one a pale square with a chamfer and a long cast to the lower right.
  bands: >
    Top third, the dark field and the type. Middle third, the upper rows of plugs with their chamfers lit. Bottom third, the lower rows of caliche plugs in the pool, each casting long across the grooved clay, the clay falling to black at the bottom edge.
  focal: "the block of 32 plugs, the brightest area"

art:
  technique: "TXBENCH multi-material relief, caliche plugs on a black clay plan raked by the low key, with a pool"
  why_this_technique: "a piece that stands proud and casts is a countable unit, and the dark plan around it keeps the uncounted city in the picture"
  palette: "black clay, pale caliche, a faint steel groove"
  value_structure: >
    Lightest is the plug tops' lit chamfers. Darkest is the clay outside the pool and each cast.
    Frame median L* planned at 3 (the arc rewritten after the render, see the run record).

type:
  hook: "32 study areas, not the whole city"
  dek: "The city says the project is not intended to count every unrestrained dog in San Antonio. SwRI says the study takes a sampling approach rather than surveying the whole city."
  labels: []

verbatim:
  - c19: "it is not intended to count every unrestrained dog in San Antonio"

acceptance:
  - "the black clay city plan with its plugs owns at least half of the frame height at 432px"
  - "exactly 32 raised plugs are countable at full size, in 4 rows of 8"
  - "every plug casts a shadow to the lower right"
  - "the grooved plan reaches the left, right and bottom edges with no border"
  - "the relief report shows at least two materials and a cast fraction of 0.12 or more"
  - "the frame's median L* at 432 px is 30 or lower"
risks:
  - "a grid of squares reads as an embossed calendar, so the plugs stand tall with long casts and the plan carries street grooves"
```

```yaml
slide: 7
layout: FIGURE_SCALE
primary_image:
  subject: "a black clay slab with 32 empty square pockets above a steel rule cut into 7 divisions, and 32 caliche plugs in the same arrangement below it, standing proud with gold chamfers"
  rect: [0, 520, 1080, 760]
  bleeds: [left, right]
accent: "none"
job: >
  Show that 2026 repeats 2019 in the same places, seven years apart, without drawing a 2019 finding the
  record does not hold.

claims: [c9, c17, c10, c22]
numerals:
  - value_from: c9
  - value_from: c10
  - computed_by: "compute.py, years_between"

data_in_art:
  figure: years_between
  drives: number of equal divisions on the steel rule, with study_areas setting the pocket and plug counts

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The mould of 32 pockets sits above, the rule runs across the middle, and the 32 plugs stand below in
    the identical arrangement, so the same places read twice at one scale.
  bands: >
    Top third, the type over the dark mould's top edge. Middle third, the pockets and the rule. Bottom third, the 32 caliche plugs in the pool with gold chamfers lit on the key side, each casting across the black clay, the clay grain in its albedo falling to black at the edge.
  focal: "the gold chamfered plugs below the rule"

art:
  technique: "TXBENCH multi-material relief: black clay with recessed pockets, an inlaid steel rule, raised caliche plugs with gold chamfers"
  why_this_technique: "a mould and its cast say the same places without saying what was found in the first"
  palette: "black clay, pale caliche, steel, dusk gold"
  value_structure: >
    Lightest is the plug tops. Darkest is the pockets' shadowed walls and the clay outside the pool.
    Frame median L* planned at 3 (the arc rewritten after the render, see the run record).

type:
  hook: "The same 32 places as 2019"
  dek: "The 2019 survey was done by hand. The automated survey will repeat it in the same study areas. The 2019 findings are not shown here."
  labels: ["2019", "2026", "7 years"]

verbatim: []

acceptance:
  - "the black clay slab with its pockets, rule and plugs owns at least half of the frame height at 432px"
  - "the black clay slab with its 32 empty square pockets is present and modelled with real depth, each pocket showing a lit wall and a shadowed wall"
  - "32 recessed pockets and 32 raised plugs are countable at full size in the same 4 by 8 arrangement"
  - "the rule shows exactly 7 equal divisions"
  - "nothing sits inside any 2019 pocket"
  - "the plugs cast to the lower right and the pockets show one lit wall and one shadowed wall"
  - "the frame's median L* at 432 px is 30 or lower"
risks:
  - "two grids could read as a chart card, so both carry real height and casts and the rule is inlaid steel"
```

```yaml
slide: 8
layout: DIAGRAM
primary_image:
  subject: "a steel survey rule cropped at both edges with month grooves, a pale caliche block standing over exactly three graduations, and a small separate caliche plug beyond them"
  rect: [0, 640, 1080, 520]
  bleeds: [left, right]
accent: "none"
job: >
  Make the field window a length: October to December on the street, then a report to Animal Care Services.

claims: [c10, c20, c11, c21]
numerals:
  - computed_by: "compute.py, field_months"

data_in_art:
  figure: field_months
  drives: block length in month graduations

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The rule runs across the frame and off both edges, so no whole year shows. The block stands over three
    graduations with a long cast, and the report plug stands apart past its end.
  bands: >
    Top third, the type. Middle third, the rule and the block. Bottom third, the black clay with its grain lit in the pool's edge, the block's long cast running to the right across it, and the month labels set under the graduations.
  focal: "the caliche block on the rule"

art:
  technique: "TXBENCH multi-material relief: a steel rule with grooves on black clay, a caliche block and plug"
  why_this_technique: "a length on a measured rule is a bar and never a dial"
  palette: "black clay, steel, pale caliche"
  value_structure: >
    Lightest is the block's top. Darkest is the clay beyond the pool. Frame median L* planned at 3 (the arc rewritten after the render, see the run record).

type:
  hook: "October to December on the street, then a report"
  dek: "Field research is expected to run through December. SwRI will then forward Animal Care Services a final report on the study's findings and data."
  labels: ["OCT", "NOV", "DEC", "final report"]

verbatim:
  - c20: "Field research is expected to take place through December 2026."

acceptance:
  - "the brushed steel survey rule spans the full frame width and the block on it owns at least a third of the frame width at 432px"
  - "the block spans exactly three graduations"
  - "the report plug sits apart from the block and off the graduations"
  - "the rule runs off both side edges"
  - "the frame's median L* at 432 px is 30 or lower"
risks:
  - "a rule with labels can read as a calendar card, so there are no cells and the rule is cropped"
```

```yaml
slide: 9
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "the tan dog standing where the driveway crosses the sidewalk, seen near its own eye height, turned three quarter away toward a dark street where a car's tail lamps are small"
  rect: [40, 600, 1000, 460]
  bleeds: []
accent: "none"
job: >
  Leave the machine. The clip and its label go into a report, and the dog is still on its street.

claims: [c14, c21, c15]
numerals: []

depth:
  eye: 0.55
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: -4.2}

composition:
  structure: >
    The camera is at the dog's eye height. The dog stands in a pool at the end of the driveway, the fence
    running away on the left, the street running into the dark with two small red tail lamps far down it.
  bands: >
    Top third, the darkest sky with the type. Middle third, the dog, the fence and the street's vanishing.
    Bottom third, the broom finished concrete of the walk and the driveway apron, the dog's paws on it with a contact shadow and its cast running left, the parkway grass at the right edge.
  focal: "the dog in its pool"

art:
  technique: "physically based render of the chassis street_dog, a kit chain_link_fence, driveway, ranch_house and crossover in the lastLight world, staged on the dog"
  why_this_technique: "the low camera inverts the cover's scale, the dog large and the car small"
  palette: "tan coat, concrete driveway, galvanized fence, dark limestone, two deep red lamps"
  value_structure: >
    Lightest is the dog and the driveway in the pool. Darkest is the sky and the street. Frame median L* planned at 2 (the arc rewritten after the render, see the run record).

type:
  hook: "The ACS director calls it another tool"
  dek: "ACS Director Jon Gary says the study gives the city \"another tool to better understand where we are seeing unrestrained dogs\". SwRI will forward the final report to the department."
  labels: []

verbatim:
  - c14: "This study gives us another tool to better understand where we are seeing unrestrained dogs"

acceptance:
  - "a dog with four legs, a head and a tail is identifiable at 432 px and owns at least a fifth of the frame height"
  - "no gold box appears in the frame"
  - "two small red tail lamps are visible down the street"
  - "the dog touches the ground with a contact shadow"
  - "the frame's median L* at 432 px is 30 or lower"
risks:
  - "the dog nearer the lens than on the cover exposes the model, so it is turned three quarter away at 4.2 m"
```
