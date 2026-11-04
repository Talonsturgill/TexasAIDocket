# Carousel no. 67, November 3rd, 2026: the scale lane

## The story, and what the fact check did to it

Aurora Innovation's third quarter shareholder letter, filed with the SEC on October 28th, 2026, says the Aurora
Driver can now determine on its own whether a weigh station is open, navigate to an available scale lane and adapt
to different scale configurations (c9), where autonomous trucks used to rely on voluntary inspections to bypass weigh
stations (c8). It says that in November the Driver will run directly to sites for several customers, through security
checkpoints (c6, c7). It counts 20+ driverless trucks built (c1) and 500,000 commercial driverless miles with 100%
on-time delivery since launch (c2). The same letter says its production ramp is about six weeks behind its prior plan
(c12), held back by material availability, component quality and end-of-line testing (c10), with 20 trucks a week now
expected in early December (c11), more than 200 trucks by the end of February (c15) and more than 1,000 in operation at
the end of 2027 (c16). Third quarter revenue was $3 million (c13) against an operating loss of $257 million including
stock-based compensation (c14). In Texas, Dallas to Houston is Aurora's own named route (c21). Dallas to Laredo is
where Charger Logistics PLANS to start under a non-binding MOU for 500 trucks with delivery expected in 2027 and 2028
(c3, c4, c19). AUMOVIO is readying a line for Aurora's third generation hardware in New Braunfels, production planned
for the second half of 2027 (c17, c18). FMCSA's five year exemption lets driverless trucks use cab mounted beacons in
place of warning devices set out by hand (c20).

The fact check found no primary Aurora page naming Fort Worth to El Paso as a current route, so the deck names only
Dallas to Houston as Aurora's. It found the Dallas and Laredo line to be Charger's plan, so it is drawn in rust and
never carries an Aurora truck. The letter names no Texas weigh station and no customer site, so the station and the
gate are generic, and the station names no Texas site because the letter names none.

Docket item tx-2026-0239, admitted this run on the letter and Aurora's September 23rd release.

## Why this treatment, and what was grafted

Base: WEIGH-IN (the scale lane lens). The deck is built where the machine makes a call a driver used to make, a
weigh station on an interstate at night under one cold LED flood, and then puts the company's own figures on the
same scale. Grafted from THE SCALE LINE and THE STRIPE AND THE PAD, which both arrived at it independently: one
accent with ONE meaning, rust primer for anything the letter says will happen and has not. That turns the letter's
own tense into something a reader sees. Grafted from THE STRIPE AND THE PAD: November's gate with the stop bar in primer (built first as a view from inside
the cab, recomposed to the boom when the cab view could not show the empty seat and the gate at once), and one yard seen twice, among the
twenty built tractors (4) and from the light mast over the 200 and 1,000 stalls Aurora expects (9). Grafted from THE
SCALE LINE: the six week rule with a scribed prior plan line and a primer stop, and the mill scale bar against the
billet at one scale. Dropped: the Texas wide county map in favour of a corridor crop, the high bay interior, and a
guard figure the letter never mentions.

## The world, and the laws that hold it

`floodlit`, staged. The key is azimuth 52, elevation 38: +x east, +z south, so a camera looking north has the key
upper right, lit edges on the right and casts running to the lower left. TXBENCH reliefs read the same light raked
from the upper right. One subject sits in a pool on the pad; the interstate behind it goes dark. Type is light on
the dark sky. A wash only darkens. The tractor runs with its headlamps on in every scene.

## Palette

steel #5C6167, concrete #8E8B85, asphalt #18181A, bead white #E8E6DF, rust #8C5A3C

Interstate concrete and asphalt at night under a 5000K flood, galvanized steel, a white tractor and van, the yellow
of scale kerb rails, the blued steel of a weighbeam. The accent is rust #8C5A3C, read as red oxide primer, and it
means ONE thing: what the letter says will happen and has not. It sits on frames 3, 5, 7 and 9.

## The continuity devices

CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE, VALUE_ARC

1. **Motif evolution, the scale.** The scale deck the tractor crosses (1, 2) becomes the steel rule that measures the
   ramp (5), the plate that weighs the quarter (6) and the stall paint that counts the trucks (9). Primer marks every
   place the letter moves from what is to what is expected.
2. **Camera move.** Beside the deck (1), up over the station (2), down at the gate's boom (3), at the yard's corner
   (4), in to a cab corner (8), then the same yard from the mast (9).
3. **Value arc, one flood.** The pool shrinks as the deck moves from what exists (1 to 4) to what is measured (5 to 7)
   to what is expected (9), whose primer stalls run out of the light into the dark.

## The rotation

    FULL_BLEED  DIAGRAM  CLOSE_CROP  GRID  CLOSE_CROP  DIAGRAM  MAP  OBJECT_AND_CAPTION  FULL_BLEED

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | MEDIUM, eye 2.6 m on the apron 26 m ahead of the cab, fov 32 | the kit semi_truck tractor, white paint and chrome raked by the flood, lit headlamps, full sensors and a white 53 ft van, weathered by TXT.weather and seated by TXT.contact on the chassis truck_scale's steel deck with diamond tread in the albedo and bump, yellow kerb rails and a dark pit line |
| 02 | WIDE, eye 14 m from the light pole's side, 66 m back, fov 34 | the kit semi_truck tractor at the fork, white paint and chrome with lit headlamps coming down the ramp, casts and contact shadows on asphalt lit by the flood, two chassis truck_scale decks with diamond tread and yellow kerb rails beside it, three emissive rings each spilling light, the kit highway beyond as the bypassed mainline |
| 03 | CLOSE, eye 1.5 m beyond the boom, 9 m from the grille, fov 38 | the kit semi_truck tractor's grille and cab, white paint and chrome with lit headlamps, cropped by the left and bottom edges, weathered by TXT.weather, the chassis guard_gate's striped boom with bevelled segments across the foreground and a primer stop bar on the asphalt with contact shadow |
| 04 | WIDE, eye 10 m at the yard's corner 40 m out, fov 30 | the twenty tractors, kit semi_truck bobtails in white paint and chrome with lit headlamps, casts and contact shadows on worn concrete, the chassis yard_stalls between them, a kit warehouse gone dark behind |
| 05 | MACRO, orthographic material relief | the steel rule, ground tool steel with machined week grooves raked by the key, set into dark concrete with grain in the albedo, a scribed witness line, a primer clamp stop with a long cast and three steel shims |
| 06 | AERIAL, orthographic material relief | the loss bar, blackened mill scale steel with a long cast on a steel datum, raked relief, a polished billet at its foot at the same scale and a hairline groove |
| 07 | AERIAL, orthographic material relief | the corridor relief, a raked clay relief with county lines in the albedo only, a raised bead white inlay and a row of primer studs with casts, a primer punch at New Braunfels |
| 08 | MACRO, eye 3.4 m beside the cab roof, fov 38 | the cab corner, white paint and black pod glass lit by the flood, the kit semi_truck's roof sensor bar and pod, with the chassis cab_beacon glowing amber on its magnetic base |
| 09 | AERIAL, eye 30 m up the yard light mast, fov 34 | the stall field, the chassis yard_stalls in primer thermoplastic running out of the light into the dark, lit near the twenty kit tractors in their corner pool with casts and contact shadows |

Showstopper frame: 01, the white driverless tractor on the scale deck under one cold flood with its headlamps on; its depth is the yellow kerb rails converging, the tractor's cast and contact on the deck, the scale house window and the lit signal falling into the dark.
Tonal arc: the flood's pool on the tractor and deck on 01, a wide pool over the station on 02, the gate's pool through the dark cab on 03, a pool over the twenty tractors on 04, the steel rule raked in a pool on 05, the bar and billet on 06, the corridor bead in a pool on 07, one amber lamp on 08, and the primer stalls running out of the light on 09.
VALUE CUT: frame 5. The deck turns from what the machine does to what the letter measures.

---
```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "a white driverless tractor and van with its headlamps on, rolling onto the steel deck of an interstate truck scale at night under one cold flood, yellow kerb rails converging toward it"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "none"
job: >
  Put the reader at the roadside everyone has passed, a weigh station at night, with one thing changed: the truck on
  the scale is making the scale house call itself.

claims: [c9]
numerals: []

depth:
  eye: 0.95
  horizon: 640
  cues: [LINEAR_PERSPECTIVE, CAST_SHADOW, RELATIVE_SIZE, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: -3}

composition:
  structure: >
    A low three quarter front view from the apron puts the tractor's grille and lit headlamps at the right centre,
    the van receding left out of frame. The yellow kerb rails run from the bottom edge toward the cab so the eye is
    led onto the scale before it reads the truck. The flood comes from upper right and lights the cab's right side.
  bands: >
    Top third, the black sky with the kicker, the hook and the dek. Middle third, the tractor's cab, sensor pods and
    roof sensor bar against the dark. Bottom third, the steel scale deck lit in the pool, the yellow rails in the foreground converging on the cab, and the tractor's cast and contact shadow on the deck.
  focal: "the lit headlamps and the bright right side of the white cab, the largest lit area in the frame"

art:
  technique: "physically based render of the kit semi_truck with full sensors on the chassis truck_scale in the floodlit world, staged on the tractor, headlamps lit by the chassis"
  why_this_technique: "a modelled truck on a modelled scale at true size is the place the claim happens, and only a physical render gives the white cab and the steel deck their real response to one flood"
  palette: "white cab and van, chrome grille, galvanized steel, yellow kerb rails, near black asphalt and sky, cold LED white"
  value_structure: >
    Lightest is the flood side of the cab and the headlamps. Darkest is the sky and the asphalt beyond the pool.
    Frame median L* planned at 12.

type:
  hook: "The truck can now tell if the scale is open"
  dek: "Aurora says its driverless trucks can now tell whether a weigh station is open and steer to an available scale lane on their own."
  labels: []

verbatim: []

acceptance:
  - "a tractor with a grille, two lit headlamp pairs, side sensor pods and a roof sensor bar is identifiable at 432 px"
  - "the tractor stands on a steel deck bounded by two yellow kerb rails, and both rails are visible"
  - "the tractor casts a shadow on the deck toward the lower left and touches it with a contact shadow"
  - "the tractor stands at least 150 px tall at 432 px"
  - "no rail, pole or lamp glow crosses a glyph of the hook or dek"
  - "the frame's median L* at 432 px is 30 or lower"
risks:
  - "a white cab under a cold flood can read flat blue, so the flood rakes from the right and the left side falls into shadow"
```

```yaml
slide: 2
layout: DIAGRAM
primary_image:
  subject: "an interstate weigh station from a high oblique: the exit ramp leaving the mainline at a chevron gore, two scale decks with yellow rails, the driverless tractor at the fork facing the camera, and three lit rings in travel order where the truck decides"
  rect: [0, 690, 1080, 560]
  bleeds: [left, right]
accent: "none"
job: >
  Show the mechanism. The three things the letter says the truck now checks for itself are three places on one
  station, and the mainline it used to take past the station is still there.

claims: [c8, c9]
numerals:
  - computed_by: "figures.json scale_steps, the count of steps c9 names"

data_in_art:
  figure: scale_steps
  drives: ring count, one lit ring on the apron per step the letter names

depth:
  eye: 18
  horizon: 480
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A high oblique keeps the horizon inside the frame so the station reads as a place. The mainline runs across the
    upper left into the dark, the ramp's two edge lines diverge from it at a chevron gore, and the driverless tractor
    comes down toward the camera at the fork. Three rings sit in travel order on the ramp, at the fork and at the
    scale deck's entry, each with a leader to a mono label in the dark ground.
  bands: >
    Top third, the dark sky and far mainline with the type. Middle third, the ramp, the first two rings and the
    tractor at the fork. Bottom third, the scale decks lit in the pool with their yellow rails, the third ring's light spilling on the deck, and the asphalt falling into shadow.
  focal: "the tractor at the fork and the nearest lit ring, inside the pool"

art:
  technique: "physically based render of the chassis station (truck_scale, scale_house, scale_signal, flood_pole) and the kit semi_truck and highway in the floodlit world, with DOM leaders"
  why_this_technique: "the letter's three steps are positions on a real station, and a high oblique render is the only view that shows all three at once without becoming a plan drawing"
  palette: "pale concrete apron in the pool, near black asphalt, galvanized steel, yellow rails, the warm window, the white tractor"
  value_structure: >
    Lightest is the apron inside the pool and the tractor's roof. Darkest is the mainline and the sky.
    Frame median L* planned at 11.

type:
  hook: "Open, which lane, which scale"
  dek: "Autonomous trucks have relied on voluntary inspections to bypass weigh stations, the letter says. It says the Aurora Driver can now handle three steps on its own."
  labels: ["station open", "available scale lane", "scale configuration", "the bypass"]

verbatim: []

acceptance:
  - "exactly three lit rings are visible on the apron, each with one leader"
  - "the scale deck and the tractor are both identifiable at 432 px"
  - "the tractor at the fork stands at least 40 px tall at 432 px"
  - "the scale deck spans at least a third of the frame width"
  - "the horizon is inside the frame and the sky shows above it"
  - "each leader ends within 24 px of its ring"
  - "no leader or ring crosses a glyph of the hook, dek or a label"
  - "the frame's median L* at 432 px is 30 or lower"
risks:
  - "chassis models read as slabs from 18 m, so the tractor carries the eye and the house keeps its window, canopy and steps"
```

```yaml
slide: 3
layout: CLOSE_CROP
primary_image:
  subject: "a driverless tractor's lit grille and cab stopped short of a customer site's guard gate at night, the striped boom down across the lane in the foreground and a primer stop bar on the asphalt, the cab cropped by the left and bottom edges"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#8C5A3C"
job: >
  Put the reader at November's gate, where the letter says the trucks will drive straight into customer sites
  through security checkpoints. The stop bar is primer because that has not happened yet.

claims: [c6]
numerals: []

depth:
  eye: 1.5
  horizon: 760
  cues: [OCCLUSION, LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW]
  subject_at: {X: 3, Z: 4}

composition:
  structure: >
    A low camera beyond the boom looks back at the tractor's nose. The grille and headlamps fill the left half,
    cropped by the left and bottom edges. The striped boom crosses the lower third in front of the bumper, and the
    primer stop bar lies on the asphalt before it.
  bands: >
    Top third, the black sky with the kicker, the hook and the dek. Middle third, the cab, the windshield, the sensor
    pod and the lit grille. Bottom third, the striped boom in the foreground lit by the headlamps, the bumper's cast
    and the primer stop bar on the asphalt.
  focal: "the lit headlamps and the grille above the black and white boom, the brightest forms in the frame"

art:
  technique: "physically based render of the kit semi_truck at the chassis guard_gate in the floodlit world, staged on the gate and the tractor"
  why_this_technique: "a modelled boom in front of a modelled truck at true size is the checkpoint the claim describes, and the primer bar is a physical mark a reader can see is not crossed"
  palette: "white cab and chrome, black and white boom, primer on asphalt, near black sky"
  value_structure: >
    Lightest is the lit grille, the headlamps and the boom's white segments. Darkest is the sky and the asphalt beyond the pool.
    Frame median L* planned at 6.

type:
  hook: "Next, through the security gate"
  dek: "Aurora says that in November its trucks will drive directly to sites for several customers, through security checkpoints."
  labels: []

verbatim: []

acceptance:
  - "a tractor grille with two lit headlamp pairs and a side sensor pod is identifiable at 432 px"
  - "a black and white striped boom crosses the lane in front of the tractor"
  - "a primer coloured bar lies across the lane before the boom and the tractor has not crossed it"
  - "the tractor stands at least 140 px tall at 432 px"
  - "no cab edge or boom crosses a glyph of the hook or dek"
  - "the frame's median L* at 432 px is 30 or lower"
risks:
  - "the gate reads only as a barrier arm, so the boom keeps its cabinet and the stop bar stays in the light"
```

```yaml
slide: 4
layout: GRID
primary_image:
  subject: "twenty white driverless tractors without trailers in two ranks of ten on a concrete yard at night, headlamps lit, white stall stripes between them, staged in one flood with a dark warehouse behind"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "none"
job: >
  Count what exists. The letter says 20+ driverless trucks are built, and twenty rendered tractors are that count at
  true scale.

claims: [c1, c2]
numerals:
  - value_from: c1
  - value_from: c2

data_in_art:
  figure: trucks_built
  drives: tractor count, one rendered tractor per truck built

depth:
  eye: 6
  horizon: 560
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: -20}

composition:
  structure: >
    A raised front oblique from the yard's edge looks along two ranks of ten so each tractor is countable by its cab
    and headlamps. The near tractor is cropped by the left edge. The ranks recede to the right and the warehouse goes
    dark behind them. Every cast runs to the lower left, longer than a tractor is wide.
  bands: >
    Top third, the sky and the warehouse roofline with the type. Middle third, the two ranks of cabs. Bottom third, the near noses lit in the pool, the white stall stripes between them and every tractor's cast and contact shadow in the foreground.
  focal: "the near rank's lit cabs and headlamps, the brightest repeated form in the frame"

art:
  technique: "physically based render of twenty kit semi_truck tractors with the chassis yard_stalls in the floodlit world, staged as one subject"
  why_this_technique: "a count of trucks is most honest as the trucks, at true scale, seen oblique with real casts so they read as objects rather than icons"
  palette: "white cabs, chrome, pale concrete in the pool, white stall paint, near black yard beyond, the dark warehouse"
  value_structure: >
    Lightest is the flood side of the near cabs and the headlamps. Darkest is the sky and the yard past the pool.
    Frame median L* planned at 10.

type:
  hook: "20+ driverless trucks are built"
  dek: "The letter says production is accelerating. The Aurora Driver passed 500,000 commercial driverless miles in September with 100% on-time delivery since launch, by Aurora's own count."
  labels: []

verbatim: []

acceptance:
  - "twenty tractors are drawn in two ranks of ten, at least eighteen whole at 432 px, the near rank's end units cropped by the frame edges"
  - "each tractor in the near rank is identifiable by its grille and lit headlamps at 432 px"
  - "every tractor casts a shadow toward the lower left"
  - "stall stripes are visible between the near tractors"
  - "the twenty tractors span at least two thirds of the frame width"
  - "no cab or glow crosses a glyph of the hook or dek"
  - "the frame's median L* at 432 px is 30 or lower"
risks:
  - "twenty tractors can read as a toy lot, so the camera is low enough to keep scale and the far rank falls into the dark"
```

```yaml
slide: 5
layout: CLOSE_CROP
primary_image:
  subject: "a ground steel rule set into dark concrete, cut with week grooves, a scribed witness line for the prior plan and a primer stop standing six graduations past it with a long cast, three steel shims lying in the slot behind the stop"
  rect: [0, 600, 1080, 750]
  bleeds: [left, right, bottom]
accent: "#8C5A3C"
job: >
  Measure the slip. The letter's own words, about six weeks behind its prior plan, drawn as six week graduations
  between a scribed line and a primer stop, with the three named causes as shims.

claims: [c12, c10, c11]
numerals:
  - value_from: c11

data_in_art:
  figure: weeks_behind
  drives: graduation count between the prior plan line and the primer stop, one groove per week

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The rule runs across the frame and off both edges. The scribed witness line stands at the left third. The
    primer stop stands six week graduations to the right of it. The pool lands on the six week span and fades out
    at both ends.
  bands: >
    Top third, the dark concrete with the type. Middle third, the rule, the witness line, the six graduations and
    the primer stop. Bottom third, the concrete grain falling dark out of the light, the stop's long cast shadow and the three steel shims in relief.
  focal: "the primer stop standing proud of the steel in the pool, with its cast"

art:
  technique: "TXBENCH material relief, ground steel, blued steel, primer and concrete raked by the deck's light from the upper right, with a keyMask pool"
  why_this_technique: "a length on a machined rule is the plainest physical form of a delay, and a relief gives the grooves and the stop real height and real casts"
  palette: "ground tool steel, blued witness line, red oxide primer, dark concrete"
  value_structure: >
    Lightest is the steel face in the pool and the stop's lit top. Darkest is the concrete outside the pool.
    Frame median L* planned at 8.

type:
  hook: "About six weeks behind its own plan"
  dek: "Material availability, component quality and problems found in end-of-line testing held the ramp back, the letter says. Aurora now expects 20 trucks a week in early December."
  labels: ["prior plan", "about six weeks", "material, components, testing"]

verbatim: []

acceptance:
  - "exactly six week grooves lie between the witness line and the primer stop"
  - "the stop is primer coloured and casts a shadow toward the lower left"
  - "three shims are drawn behind the stop"
  - "the steel rule spans the full frame width and stands at least 60 px tall at 432 px"
  - "the relief carries at least two materials and a cast shadow"
  - "no label crosses a groove line"
  - "the frame's median L* at 432 px is 30 or lower"
risks:
  - "a rule and a stop can read as a UI slider, so the grooves are machined with real depth and the stop is a clamp with a screw"
```

```yaml
slide: 6
layout: DIAGRAM
primary_image:
  subject: "a blackened mill scale steel bar lying on a steel datum almost the full width of the frame with a long cast, and at its left end on the same datum a polished billet at the same scale, a hairline groove marking the expected 2026 revenue"
  rect: [0, 700, 1080, 420]
  bleeds: [left, right]
accent: "#8C5A3C"
job: >
  Weigh the quarter. Revenue and the operating loss as two lengths at one scale, so the reader sees the difference
  before reading a figure.

claims: [c13, c14, c12]
numerals:
  - value_from: c13
  - value_from: c14
  - value_from: c12

data_in_art:
  figure: q3_operating_loss
  drives: bar length, at the same pixels per million dollars as the billet set by q3_revenue

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    One datum runs across the frame below the type. The billet stands at its left end and the loss bar lies beside it
    on the same datum, running almost to the right edge. Both are the same height, so length alone carries the
    figure. Labels sit in the dark field above and below.
  bands: >
    Top third, the hook and the dek on the dark field beside the top of the bar. Middle third, the bar's length and
    its cast. Bottom third, the lit steel datum, the billet with its own cast shadow and the hairline groove in relief.
  focal: "the billet at the bar's foot, small and lit, against the long dark bar"

art:
  technique: "TXBENCH material relief, mill scale steel, polished steel and a concrete bed, raked from the upper right"
  why_this_technique: "two lengths at one scale need real height and a cast so the shorter one still reads as a thing at feed size"
  palette: "blue black mill scale, polished steel, dark concrete"
  value_structure: >
    Lightest is the billet and the datum in the pool. Darkest is the bed beyond the pool.
    Frame median L* planned at 7.

type:
  hook: "$3 million in revenue, a $257 million operating loss"
  dek: "Third quarter revenue and operating loss at one scale. The loss includes stock-based compensation. Aurora expects about $9 million of revenue for 2026."
  labels: ["revenue $3 million", "operating loss $257 million", "2026 revenue expected, about $9 million"]

verbatim: []

acceptance:
  - "the bar's length divided by the billet's length matches 257 to 3 within 3 percent"
  - "the billet and the bar stand on one datum line"
  - "the loss bar spans at least 300 px wide at 432 px"
  - "the billet is visible at 432 px as a lit block with its own cast"
  - "the relief carries at least two materials and a cast shadow"
  - "no label crosses the bar or the billet"
  - "the frame's median L* at 432 px is 30 or lower"
risks:
  - "the billet is a few pixels at feed size, so its specular and its cast carry it and it is never drawn at a second scale"
```

```yaml
slide: 7
layout: MAP
primary_image:
  subject: "the corridor from Dallas south to Houston and Laredo in dark Blackland clay relief, county lines in the albedo, a raised bead white inlay from Dallas to Houston, a row of primer studs from Dallas toward Laredo, and a primer punch at New Braunfels"
  rect: [0, 620, 1080, 600]
  bleeds: [left, right]
accent: "#8C5A3C"
job: >
  Say where in Texas, and with which status. One route Aurora runs, one route a customer plans, one hardware line
  being readied.

claims: [c21, c3, c4, c19, c17, c18]
numerals:
  - value_from: c3
  - value_from: c4
  - value_from: c18

data_in_art:
  figure: charger_trucks
  drives: stud count along the planned Dallas to Laredo chord, one stud per truck in the MOU

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The crop runs from Dallas at the top to Laredo and Houston at the bottom, the state as the ground and never a
    card. The white inlay runs from Dallas to Houston. The primer studs run from Dallas toward Laredo. The New
    Braunfels punch sits where the gazetteer puts it. Place names sit as mono labels beside their pins.
  bands: >
    Top third, the hook and the dek on the dark clay beside Dallas. Middle third, the two routes diverging. Bottom third, Houston, New Braunfels and Laredo as lit pins with casts, the clay relief falling to shadow at the Gulf.
  focal: "the bead white inlay catching the key where the two routes leave Dallas"

art:
  technique: "TXBENCH material relief over TXGeo cartography, clay, thermoplastic bead and primer, county lines in the albedo only"
  why_this_technique: "places are the claim, and a relief map gives an inlay that exists and studs that are planned two different physical states a reader can tell apart"
  palette: "Blackland clay, bead white thermoplastic, primer, caliche pins"
  value_structure: >
    Lightest is the white inlay and the pins in the pool. Darkest is the clay outside it.
    Frame median L* planned at 8.

type:
  hook: "Aurora's own route, and a customer's plan"
  dek: "Dallas to Houston is Aurora's own route. Charger Logistics plans to start between Dallas and Laredo under a non-binding MOU for 500 trucks, with delivery expected in 2027 and 2028. Routes drawn straight between places. New Braunfels is marked at Comal County's center."
  labels: ["Dallas", "Houston", "Laredo", "New Braunfels, AUMOVIO line"]

verbatim: []

acceptance:
  - "the Dallas to Houston line is raised white and the Dallas to Laredo line is a row of primer studs"
  - "four labelled pins mark Dallas, Houston, Laredo and New Braunfels"
  - "the relief of the corridor owns at least half the frame height"
  - "the county lines sit within 8 px of the clay so they read as cut marks, not walls"
  - "the relief carries at least two materials and a cast shadow"
  - "no label crosses a route line"
  - "the frame's median L* at 432 px is 30 or lower"
risks:
  - "a county relief has read as a card on a table, so the crop bleeds and the pool lands on the routes"
```

```yaml
slide: 8
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "the roof corner of the white driverless tractor at night with its side sensor pod, a small amber beacon lit on a magnetic base on the cab roof, and the empty shoulder of the road below in the dark"
  rect: [140, 520, 940, 760]
  bleeds: [right]
accent: "none"
job: >
  Show what replaces the triangles. When a driverless truck stops, the exemption the letter cites lets a beacon on
  the cab do the job of warning devices a driver would set out by hand.

claims: [c20]
numerals: []

depth:
  eye: 3.4
  horizon: 620
  cues: [OCCLUSION, CAST_SHADOW, RELATIVE_SIZE, AERIAL]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A close camera beside the cab roof looks along it. The beacon sits at the centre right on the roof corner, the
    sensor pod's arm crossing below it, the cab's edge catching the flood. The shoulder and an empty lane fall away
    to the dark.
  bands: >
    Top third, the black sky with the type. Middle third, the beacon, the roof sensor bar and the pod. Bottom third, the lit cab side and pod arm in the foreground falling to the dark shoulder, the beacon's amber glow on the roof.
  focal: "the lit amber dome of the beacon, the one warm light in the frame"

art:
  technique: "physically based render of the kit semi_truck roof corner and a chassis cab_beacon in the floodlit world, staged on the cab corner"
  why_this_technique: "a lamp the size of a fist needs a real macro of the real cab to read as a device rather than a dot"
  palette: "white cab, black pod glass, amber lamp, near black road"
  value_structure: >
    Lightest is the beacon and the lit cab edge. Darkest is the sky and the shoulder.
    Frame median L* planned at 7.

type:
  hook: "When it stops, a light on the cab"
  dek: "The letter says FMCSA granted a five-year exemption letting driverless trucks use cab-mounted warning beacons in place of warning devices set out by hand."
  labels: []

verbatim: []

acceptance:
  - "an amber dome beacon on a round base is identifiable at 432 px"
  - "the beacon stands on the cab roof beside the sensor bar"
  - "the beacon's dome stands at least 30 px wide at 432 px and the cab corner owns at least a third of the frame width"
  - "no warning triangle is drawn anywhere in the frame"
  - "no lamp glow crosses a glyph of the hook or dek"
  - "the frame's median L* at 432 px is 30 or lower"
risks:
  - "a stopped truck with a beacon can read as a breakdown, so the copy names the exemption's case and nothing else"
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: "the same yard from the top of its light mast: the twenty tractors in a corner pool, and from them rows of painted stalls, 200 primer stalls inside the pool's falloff and the rest of 1,000 primer stalls running out into the dark"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#8C5A3C"
job: >
  Show the distance between what exists and what Aurora expects, at one stall per truck, and give the reader the
  filing to read.

claims: [c15, c16, c1]
numerals:
  - value_from: c15
  - value_from: c16
  - value_from: c1

data_in_art:
  figure: trucks_end_2027
  drives: stall count, one painted stall per truck, the first trucks_built white and milestone_trucks inside the pool

depth:
  eye: 30
  horizon: 480
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A high camera on the mast looks over the twenty tractors in the near corner pool. Rows of primer stalls run away
    from them across the dark yard, the first 200 inside the pool's falloff, the rest fading out toward the horizon.
    The horizon stays inside the frame.
  bands: >
    Top third, the dark sky and the far yard with the type. Middle third, the primer stalls running into the dark.
    Bottom third, the twenty lit tractors in their pool with casts and contact shadows on the concrete, the first stalls in the foreground.
  focal: "the twenty lit tractors in the near pool, with the primer rows leading the eye away from them"

art:
  technique: "physically based render of the kit semi_truck tractors and the chassis yard_stalls in the floodlit world, staged on the twenty"
  why_this_technique: "one stall per truck turns two expected counts into a field a reader can see is far larger than what stands in it"
  palette: "white cabs, pale concrete in the pool, primer stalls, near black yard"
  value_structure: >
    Lightest is the twenty cabs in the pool. Darkest is the far yard and the sky.
    Frame median L* planned at 7.

type:
  hook: "From 20+ built to 1,000+ expected"
  dek: "Aurora expects more than 200 trucks by the end of February and more than 1,000 in operation at the end of 2027. Each primer stall is one expected truck. The filing is on the SEC's EDGAR site, dated October 28th."
  labels: ["20+ built", "more than 200 by end of February, expected", "more than 1,000 by end of 2027, expected"]

verbatim: []

acceptance:
  - "twenty tractors stand in the lit corner and none stands in a primer stall"
  - "primer stall rows run from the tractors into the dark and fade before the horizon"
  - "the horizon is inside the frame and the sky shows above it"
  - "the twenty tractors' stalls are white and every other stall is primer"
  - "the stall field owns at least a third of the frame height"
  - "no label or leader crosses a glyph of the hook or dek"
  - "the frame's median L* at 432 px is 30 or lower"
risks:
  - "a thousand thin stripes alias at a high camera, so the stripes are 0.15 m wide at a 4.4 m pitch and fade into the dark"
```
