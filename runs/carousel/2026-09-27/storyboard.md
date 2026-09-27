# Storyboard, 2026-09-27
# "Rent, recommended overnight"

## The story, and what the fact check did to it

On September 4th, 2026 the Justice Department filed a proposed final judgment against Pinnacle
Property Management Services (c3, c4), which the Competitive Impact Statement places in Frisco and
calls one of the largest apartment managers in the United States (c12). Pinnacle licensed RealPage's
AI Revenue Management and YieldStar (c20). RealPage is headquartered in Richardson (c15). The
Federal Register published the judgment, the statement and the amended complaint on September
18th, 2026 (c1) and invites comment within 60 days of the notice (c8). The record admitted it today
as tx-2026-0189.

The AI in use, as the complaint alleges it: nonpublic lease data runs through a machine learning
model whose learned parameters serve every AIRM client (c23), retrained three to four times a year
(c24). Every night AIRM forecasts each property's vacancies (c25) and a new floor plan price is
generated daily (c26). By default auto-accept approves a 3% daily and an 8% weekly change (c27).
Accepting can be done in bulk and declining takes "specific business commentary" (c30, c31). Nearly
60% of final floor plan prices landed within 2.5% of the recommendation (c33).

**WHAT THE FACT CHECK CHANGED.**
- **Every mechanism is an allegation.** c21 to c36 and c64 are the plaintiffs' words or the
  Justice Department's summary of them. Every frame that describes the software says "the
  complaint says". Nothing here is a court finding (c59).
- **Frisco is the complaint's and the statement's**, never the judgment's, whose own definition
  says Dallas (c12 caution). The deck says the government places Pinnacle in Frisco.
- **No close date is printed.** The notice says within 60 days of the notice (c8), and the
  statement says the later of that or a newspaper summary (c9). No frame prints a close date.
- **The judgment does not ban RealPage** (c53) and binds Pinnacle only (c55). Frame 7's hook
  exists to stop the reader taking the lamps going off as a ban.
- **16 million units is an allegation** and ships only as that (c34).
- **The building is drawn.** It is a kind of building and no one's property.

## Why this treatment, and what was grafted

Three directors pitched THE NIGHT RUN, GLASS OFFICE and FRONTAGE ROAD, and all three chose the
same world and the same accent without seeing each other: nightSodium and #7FB2D9, the one cool
light in a sodium lot being a screen. The deck is THE NIGHT RUN's spine, one garden building
through one night, because the complaint's mechanism is a clock (c25, c26) and a building at 2 a.m.
is what "every night" looks like.

- From GLASS OFFICE: the recommendation screen as the accent's one home, with accept as one lit bar
  and decline as a small outlined box (frame 2), and the judgment's pages laid on the same desk as
  the screen they govern (frame 6).
- From FRONTAGE ROAD: the two steel columns at one scale for 3% and 8% in front of the leasing door
  (frame 3), and the guard against a Tollway claim nothing supports.
- From THE NIGHT RUN: the five breezeway lamps as the motif that goes dark under the five software
  limits while the screen stays on (frames 3 and 7, one camera), the 48 buildings in five clusters
  (frame 5), and the lit-window share across the road (frame 8).
- Refused: a ridge line standing for rent (a building's height is not a price), a map of county
  lines at night (a map with nothing on it at 432 px), a seated figure (the kit has no sit pose).

## The world, and the laws that hold it

**A TEXAS GARDEN APARTMENT LOT AT TWO IN THE MORNING.** The chassis is
`assets/js/deck/2026-09-27-nightrent.js` and every frame loads it. It declares `sky: nightSodium`,
tuned once so the zenith stays black and the city glow sits low on the south horizon, and one
light at azimuth 196, elevation 26, inside the preset's lamp range of 20 to 60. The key is the
city's glow BEHIND the building from any lot camera: the roofline takes a warm rim against the
glow, and the facade is lit by what is in the lot, the pole lamps, the breezeway wall packs and the
few windows still lit. Why this light: "what runs all night, what is not seen" is the world
table's own line for nightSodium, and it is the complaint's verb.

**ONE HERO OBJECT.** `garden_apartment`, built once in the chassis as a kit model: three storeys at
3.05 m, a brick ground floor and lap siding above, a 6 in 12 gable ridge, balconies with steel
pickets, five open breezeway cores with concrete stairs and wall packs, condensers on pads at the
back, and a leasing office storefront in the west end bay. `NIGHTRENT.hero(K, o)` makes it the same
way on every frame.

**THE SCREEN IS THE ACCENT.** `#7FB2D9`. The leasing office's glow and its monitor (1, 2, 3, 6, 7)
and the resident's laptop (9). Nothing else is cool.

**THE MUTE WORLD LAW.** No company name, no logo, no readable screen text drawn in the art. Every
word a screen carries is DOM.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#171310` | the DOM body behind the render |
| `accent` | `#7FB2D9` | the office glow, the monitor, the laptop |
| `hook` | `#F3EEE6` | the hook on every frame, in the black sky or the dark room |
| `dek` | `#E4DDD2` | the dek |
| `rule` | `#CBBFAE` | the site line, the source line and the counter |

The world's own colours are lit materials: red-brown Texas brick, greige lap siding, dark shingle,
wet black asphalt with worn stall paint, sodium amber pools, a black sky with an amber glow low in
the south, and one cool screen.

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE, VALUE_ARC
    VALUE CUT: frame 6

1. **Motif evolution, the breezeway lamps and the screen.** Five wall packs lit on 1, 3, 4 and 5,
   dark on 7 and 8 under the five software limits, and the screen on through all of it, passing to
   a resident's laptop on 9.
2. **Camera move.** The lot (1), into the office (2), out to the elevation (3), up the stair (4), up
   over five metros (5), back to the desk (6), frame 3's exact camera (7), across the road (8), into a
   unit (9).
3. **Value arc.** One night at one grade, stepping darker after frame 7 as the breezeway light goes.

## The rotation

    FULL_BLEED  CLOSE_CROP  DIAGRAM  FIGURE_SCALE  GRID  DOCUMENT  DIAGRAM  GRID  CLOSE_CROP

`TXLAYOUT.check` returns an empty list.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "the hero at night from 100 m out in its lot, off the west end and low, the whole front receding to the right with all five breezeway cores lit and the east gable against the glow, the leasing storefront nearest and glowing cool, a sodium pool on the wet asphalt in the foreground"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#7FB2D9"
job: >
  Stop the scroll on an ordinary Texas apartment lot at night and make the one cool light in it
  the question the deck answers.

claims: [c3, c12, c20, c26]
numerals: []

depth:
  eye: 1.6
  horizon: 880
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, OCCLUSION, CAST_SHADOW, FORM_SHADING]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A standing camera in the lot 38 m off the front facade, turned so the building runs from the
    right edge back toward the left and the leasing storefront lands on the left third. The ridge
    stands against the amber glow low in the south, and the type sits in the black sky above.
  bands: >
    Top third, the black sky with the hook and the dek. Middle third, the roofline against the glow,
    the three floors of balconies, the five lit breezeway slots and the cool storefront. Bottom third, the wet asphalt lot modelled by the sodium pool, worn stall paint receding in perspective, a pickup and a sedan in the foreground, their paint lit by the pole and each on its own contact shadow, a curbed island with grass, and the pole's base.
  focal: "the cool storefront at the west end against the warm lot"

art:
  technique: "physically based render through txthree.js in the declared nightSodium world, the chassis garden_apartment, kit streetlight, pickup and sedan, stall paint, contact and weather"
  why_this_technique: >
    The claim is a machine running where people live while they sleep. Only a render of a real
    lot at the real hour makes one cool window read as the thing that is awake.
  palette: "black sky, amber glow, red brick, greige siding, sodium pools on black asphalt, one cool storefront"
  value_structure: >
    Lightest is the breezeway slots, the sodium pool and the storefront. Darkest is the sky behind
    the type and the lot's corners. Frame median L* planned at 14.
  motion: "from the hook down to the storefront, along the facade to the lit slots"

type:
  kicker: "The night shift"
  hook: "Rent, recommended overnight"
  dek: "The Justice Department has proposed a judgment against Pinnacle, an apartment manager the complaint places in Frisco. The complaint says Pinnacle's RealPage software recommends a new price for every floor plan every night."

acceptance:
  - "the frame reads \"Rent, recommended overnight\""
  - "all five breezeway cores are in frame and lit"
  - "the storefront at the west end is the only cool coloured area on the frame"
  - "no pole, tree or roof edge crosses the hook or the dek"

risks:
  - "dark on dark: the facade must separate from the lot, carried by the sodium pool and the lit slots"
```

```yaml
slide: 2
layout: CLOSE_CROP
primary_image:
  subject: "inside the leasing office at night from behind an empty office chair, a filing cabinet by the storefront and the lot's warm light falling through it at the left, the desk with a 27 inch monitor showing a drawn recommendation screen, a wide lit accept bar and a small outlined decline box, two tolerance bands around the recommendation line"
  rect: [300, 620, 780, 680]
  bleeds: [right]
accent: "#7FB2D9"
job: >
  Put the reader in the chair where the complaint says the price arrives, and show how much easier
  yes is than no.

claims: [c21, c30, c31, c33]
numerals:
  - value_from: c33   # nearly 60%, 2.5%
  - value_from: c33   # 5%, band label

data_in_art:
  figure: band_near_px
  drives: "the half-height in screen-texture px of the inner tolerance band around the recommendation line, 2.5 points at 12 px per point, and the outer band at 5 points on the same scale (band_close_px)"

composition:
  structure: >
    A seated camera behind the chair's back, the monitor on the right half of the frame near
    frontal, the chair's back cropped by the bottom edge, the storefront glass on the left with the
    lot's sodium pool through it. The type sits on the dark wall and ceiling above.
  bands: >
    Top third, the dark ceiling and wall with the hook and the dek. Middle third, the monitor's lit
    screen with its bars and bands, the storefront glass at the left. Bottom third, the veneer desk edge catching the screen light, the keyboard's keys modelled by it, and the empty chair's leather back and headrest rounded in the monitor's glow, with the chair's shadow falling toward the camera.
  focal: "the lit accept bar on the screen"

art:
  technique: "physically based render in a TXT.interior room, kit desk, office_chair and monitor, a canvas texture on the monitor face drawn from figures.json, sodium through the storefront"
  why_this_technique: >
    The claim is about an interface's shape. A real screen in a real empty room at night shows the
    asymmetry the complaint alleges without anybody being there to click.
  palette: "near black room, bronze mullions, cool screen, warm sodium through the glass"
  value_structure: >
    Lightest is the screen. Darkest is the ceiling behind the type. Frame median L* planned at 12.
  motion: "from the hook to the accept bar, down to the empty chair"

type:
  kicker: "The leasing office"
  hook: "Yes in bulk, no with a reason"
  dek: "A manager can accept in bulk and must give \"specific business commentary\" to decline, the complaint says. It puts nearly 60% of final floor plan prices within 2.5% of RealPage's recommendation and more than 85% within 5%."
  labels: ["2.5%", "5%", "recommended"]

verbatim:
  - c31: "specific business commentary"

acceptance:
  - "the frame reads \"Yes in bulk, no with a reason\""
  - "the monitor shows a wide lit bar and a small outlined box beside it"
  - "two bands of different widths sit around one line on the screen, labelled 2.5% and 5%, and read as two at thumb size"
  - "the chair is empty and no person is in the room"
  - "the storefront glass behind the desk reads as dark night glass and nothing bright sits behind the type"

risks:
  - "the screen texture must stay illegible as text, every word is DOM"
```

```yaml
slide: 3
layout: DIAGRAM
primary_image:
  subject: "the shared lot camera 150 m off the hero's front, all five breezeway cores lit, the storefront at the west end, and 12 m from the lens two brushed steel columns on base plates, 0.75 m and 2.0 m tall, labelled 3% a day and 8% a week, a resident standing beside them for scale"
  rect: [0, 640, 1080, 560]
  bleeds: [left, right]
accent: "#7FB2D9"
job: >
  Make the default limits a size a reader can see at one scale, standing where the price is set.

claims: [c27, c28, c29]
numerals:
  - value_from: c27   # 3%
  - value_from: c27   # 8%

data_in_art:
  figure: column_daily_m
  drives: "the height in metres of the first steel column, 3 points at 0.25 m per point, and the second column's height from column_weekly_m on the same scale"

depth:
  eye: 1.6
  horizon: 1010
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, CAST_SHADOW, FORM_SHADING]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A long lens from 150 m flattens the building into an elevation across the frame. The two
    columns stand on the walk before the leasing door at the left, their tops read against the
    brick. Leaders in mono land on each column's top.
  bands: >
    Top third, the black sky with the hook and the dek. Middle third, the roof, the three floors,
    the five lit slots and the storefront. Bottom third, the two steel columns with lit edges and their cast shadows on the concrete walk before the leasing door, the curb, and the asphalt lot with stall paint under a sodium pool.
  focal: "the two columns at the leasing door"

art:
  technique: "physically based render, long lens elevation, two rounded steel columns placed by figures.json, SVG leaders landing on projected tops"
  why_this_technique: >
    Two percentages compared want one scale and one zero. Steel columns at the door keep the
    comparison in the place the limits act on.
  palette: "black sky, brick, siding, steel columns lit by the lot, cool storefront"
  value_structure: >
    Lightest is the lit slots and the storefront. Darkest is the sky. Frame median L* planned at 12.
  motion: "from the hook to the columns, along the facade"

type:
  kicker: "The auto-accept limits"
  hook: "3% a day, 8% a week"
  dek: "The complaint says AIRM and YieldStar can accept recommendations automatically, and the default limits are 3% a day and 8% a week. It says a landlord who turns auto-accept on in effect hands pricing authority to RealPage inside those limits."
  labels: ["3% a day", "8% a week"]

acceptance:
  - "the frame reads \"3% a day, 8% a week\" with each pair on its own line"
  - "two columns stand on one zero line and the taller is more than twice the shorter"
  - "each leader ends at its column top"
  - "a standing person beside the columns gives them a size"
  - "all five breezeway cores are in frame and lit"

risks:
  - "at 150 m the columns are small; they must stay readable at 432 px"
```

```yaml
slide: 4
layout: FIGURE_SCALE
primary_image:
  subject: "a resident walking in across the lot 30 m from the lens, lit by a pole's pool, toward the lit second breezeway of the hero 70 m off, the three storeys and the roofline under the night sky"
  rect: [0, 630, 1080, 520]
  bleeds: [left, right]
accent: none
job: >
  Put a person beside the machine's input, the lease, at true size.

claims: [c23, c24, c34]
numerals:
  - value_from: c34   # 16 million

depth:
  eye: 1.5
  horizon: 1050
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, OCCLUSION, CAST_SHADOW, FORM_SHADING]
  subject_at: {X: 0, Z: 6}

composition:
  structure: >
    A standing camera 9 m off the breezeway mouth, the stair core on the right two thirds, the
    resident at its foot lit by the wall pack on the camera's side. The ridge and the black sky sit
    above, where the type goes.
  bands: >
    Top third, the black sky over the ridge with the hook and the dek. Middle third, the breezeway's
    lit landings and the balconies either side. Bottom third, the resident modelled by the wall pack, the resident's cast shadow on the concrete walk, the stair's first treads and steel stringers, and the wet walk shining with the lamp.
  focal: "the resident at the lit stair foot"

art:
  technique: "physically based render, kit person, the chassis breezeway, a wall pack pool"
  why_this_technique: >
    The complaint's input is a lease, and a lease is a person. Beside the building the resident lives in,
    the figure gives it a size.
  palette: "warm stair light, black sky, brick and siding in shade"
  value_structure: >
    Lightest is the breezeway light. Darkest is the sky. Frame median L* planned at 13.
  motion: "from the hook down the stair to the resident"

type:
  kicker: "Where the data comes from"
  hook: "Leases feed the model"
  dek: "The complaint says landlords' nonpublic lease data runs through a machine learning model whose learned parameters serve every AIRM client. It says the model is generally retrained three to four times a year. It says RealPage has data from over 16 million units."

acceptance:
  - "the frame reads \"Leases feed the model\""
  - "a walking person stands in a lamp pool and is lit on the side the camera sees"
  - "the building behind rises to its roofline below the dek"
  - "the breezeway cores in frame are lit"

risks:
  - "a figure lit from behind reads as a silhouette; the wall pack must be camera side"
```

```yaml
slide: 5
layout: GRID
primary_image:
  subject: "forty eight copies of the hero at night on a dark prairie in five clusters of 17, 13, 12, 4 and 2, each lit by its breezeway lamps, two across so each cluster runs back as far as its count, seen from a rise with the horizon and its glow at the top of the frame"
  rect: [0, 620, 1080, 420]
  bleeds: [left, right]
accent: none
job: >
  Show how many Texas places the complaint names, at the size of the building a Texan lives in.

claims: [c15, c36, c37, c38]
numerals:
  - computed_by: "out/2026-09-27/compute.py, texas_submarkets, rows under a Texas area in Appendix A counted"
  - computed_by: "out/2026-09-27/compute.py, texas_submarkets_by_area"

data_in_art:
  figure: texas_submarkets
  drives: "building instance count, split into clusters by texas_submarkets_by_area"

depth:
  eye: 60
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, CAST_SHADOW]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A site camera 60 m up and 700 m back on a long lens so every building reads near the same size.
    Five clusters left to right in the order of the counts. Mono labels under each cluster.
  bands: >
    Top third, the black sky and the glow with the hook and the dek. Middle third, the clusters of
    lit roofs. Bottom third, the nearest clusters' roofs and lit breezeways modelled in perspective, their shadows on the prairie, the lot lamps' pools between them, with a mono label under each cluster.
  focal: "the largest cluster at the left"

art:
  technique: "physically based render, 48 clones of one chassis model, long lens isotype"
  why_this_technique: >
    A count wants units a reader can count, and the unit here is the building itself.
  palette: "black prairie, sodium lit roofs, amber horizon"
  value_structure: >
    Lightest is the lit slots and roofs. Darkest is the ground between clusters. Frame median L*
    planned at 10.
  motion: "left to right along the clusters"

type:
  kicker: "Appendix A of the complaint"
  hook: "48 Texas submarkets"
  dek: "The complaint lists them as places where it says aligned pricing harmed or is likely to harm renters. Frisco and Richardson are on the list. RealPage has its headquarters in Richardson."
  labels: ["Dallas-Plano-Irving 17", "Austin-Round Rock 13", "Houston 12", "San Antonio 4", "Fort Worth 2"]

acceptance:
  - "the frame reads \"48 Texas submarkets\""
  - "five separate clusters of buildings are visible and the leftmost is the largest"
  - "each cluster carries its count and its area name under it"
  - "the rows inside each cluster are separated by lit ground"

risks:
  - "48 buildings at a distance can read as texture; the long lens and the lamps keep each one a building"
```

```yaml
slide: 6
layout: DOCUMENT
primary_image:
  subject: "the proposed final judgment lying on a dark leather desk pad in the leasing office, a letter page with nine ruled entries, three of them tied to the judgment's own words in the margin beside it, the monitor's cool light falling across it and a pen beside it"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#7FB2D9"
job: >
  Lay the paper on the desk it governs, and count what it asks.

claims: [c3, c39, c40, c41, c42, c43, c44, c45, c46, c47, c48, c12]
numerals:
  - computed_by: "out/2026-09-27/compute.py, judgment_requirements, numbered items i to ix counted"

data_in_art:
  figure: judgment_requirements
  drives: "the number of ruled entries drawn on the page"

composition:
  structure: >
    A seated camera looking down the desk at the page square to the lens, the monitor's lower edge
    glowing at the top of the desk. The type sits on the dark wall above.
  bands: >
    Top third, the dark wall with the hook and the dek. Middle third, the monitor's glow and the top
    of the page. Bottom third, the page's lower ruled entries lit by the screen with the mullion shadow across them, the page's curl and cast shadow on the veneer desk, and a pen lying beside it.
  focal: "the page's nine entries"

art:
  technique: "physically based render in the TXT.interior office, a page texture drawn on canvas with ruled entries, DOM text registered to three entries"
  why_this_technique: >
    The claim is the document's own list. A page on the desk under the screen says whose desk it is.
  palette: "dark room, white page lit by the screen, bronze mullion shadows"
  value_structure: >
    Lightest is the page. Darkest is the wall behind the type. Frame median L* planned at 16.
  motion: "from the hook down the page's entries"

type:
  kicker: "The proposed final judgment"
  hook: "Nine terms for Pinnacle"
  dek: "The impact statement sums up the proposed judgment against Pinnacle in nine terms. Beside the data limits they require a compliance officer, an annual audit and inspections."

verbatim:
  - c43: "chief antitrust compliance officer"
  - c45: "inspect its documents"
  - c48: "if the Court finds that Pinnacle has violated the terms"

acceptance:
  - "the frame reads \"Nine terms for Pinnacle\""
  - "a page with exactly nine ruled entries lies on the desk"
  - "three entries carry the judgment's own words"
  - "the monitor's cool light falls across the page"

risks:
  - "an interior frame after four exteriors must hold the deck's value; the page is the light"
```

```yaml
slide: 7
layout: DIAGRAM
primary_image:
  subject: "frame 3's exact camera and lot, the five breezeway cores now dark and the two steel columns still standing, the leasing storefront still glowing at the west end, each dark core with a short mono label naming one limit"
  rect: [0, 640, 1080, 560]
  bleeds: [left, right]
accent: "#7FB2D9"
job: >
  Turn the deck. The judgment switches off inputs at one landlord and leaves the screen on.

claims: [c39, c40, c41, c50, c51, c46, c53]
numerals:
  - computed_by: "out/2026-09-27/compute.py, software_limits, the five limits this deck read counted"

data_in_art:
  figure: software_limits
  drives: "the number of breezeway cores built and the number switched off"

depth:
  eye: 1.6
  horizon: 1010
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, CAST_SHADOW, FORM_SHADING]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    Identical to frame 3 so the change is the lamps. Five leaders drop to the five dark slots.
  bands: >
    Top third, the black sky with the hook and the dek. Middle third, the facade with five dark slots
    and the lit storefront. Bottom third, the five labels' leaders dropping to the dark slots, the walk and curb in the foreground where the steel columns stood, lit by the pole, and the asphalt lot with stall paint under the sodium pool.
  focal: "the lit storefront beside the dark slots"

art:
  technique: "physically based render, frame 3's camera, lamps off, SVG leaders"
  why_this_technique: >
    The same camera with one state changed is how a reader sees exactly what the judgment did.
  palette: "as frame 3, darker"
  value_structure: >
    Lightest is the storefront. Darkest is the sky and the dark slots. Frame median L* planned at 10.
  motion: "along the five dark slots to the storefront"

type:
  kicker: "What the judgment switches off"
  hook: "The screen stays on"
  dek: "Five of its limits on how Pinnacle may price. It isn't a ban on RealPage, and the government may review the code and pseudocode of Pinnacle's own product."
  labels: ["third-party nonpublic data", "pooling across owners", "rivals' sensitive data", "required acceptance", "built-in rent floors"]

acceptance:
  - "the frame reads \"The screen stays on\""
  - "the camera, lot and columns are frame 3's"
  - "all five breezeway cores are dark"
  - "the storefront still glows in the accent"
  - "five labels each end at one dark core"

risks:
  - "dark slots may read as a blackout; the hook and dek carry the correction"
```

```yaml
slide: 8
layout: GRID
primary_image:
  subject: "from the near kerb across a four lane road, three buildings in a row: the hero in the middle with its five breezeway cores dark, and a neighbour either side with its cores lit and 3 and 8 of its 12 front units lit, a bench on the verge"
  rect: [0, 600, 1080, 440]
  bleeds: [left, right]
accent: none
job: >
  Say what the judgment is not: one landlord, proposed, and a case that goes on around it.

claims: [c55, c56, c58, c59, c36]
numerals:
  - value_from: c36   # 26% to 69%

data_in_art:
  figure: lit_units_low
  drives: "the number of lit front units on the first other building, and lit_units_high on the second"

depth:
  eye: 1.6
  horizon: 900
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, OCCLUSION, CAST_SHADOW]
  subject_at: {X: 0, Z: -40}

composition:
  structure: >
    A camera on the near verge looking along the road at an angle, so the three buildings recede
    to the right across it: a lit neighbour, the dark hero in the middle, a lit neighbour. The
    four lane road runs across the foreground, and the type sits in the sky.
  bands: >
    Top third, the black sky with the hook and the dek. Middle third, the three buildings. Bottom third, the four lane road's asphalt lit and modelled by a sodium pool from a streetlight just out of frame, lane paint receding in perspective, the lit kerb edge and its shadow.
  focal: "the two lit buildings beside the dark one"

art:
  technique: "physically based render, three chassis buildings, kit road and streetlight"
  why_this_technique: >
    The judgment's scope is a fact about neighbours. Three buildings side by side show it.
  palette: "black sky, lit and dark windows, sodium on asphalt"
  value_structure: >
    Lightest is the lit windows. Darkest is the sky. Frame median L* planned at 10.
  motion: "from the lit buildings to the dark one"

type:
  kicker: "The rest of the case"
  hook: "It binds one landlord"
  dek: "The judgment is proposed and Pinnacle admits nothing. It must follow the terms before the court enters them. The government's claims against the remaining defendants go on."

acceptance:
  - "the frame reads \"It binds one landlord\""
  - "the middle building's breezeway cores are dark and both neighbours' are lit"
  - "the two neighbours show different numbers of lit windows"

risks:
  - "lit windows standing for penetration is a device; the dek names what the numbers are"
```

```yaml
slide: 9
layout: CLOSE_CROP
primary_image:
  subject: "inside a unit's kitchen at night, seen from the counter's end by the fridge, a resident standing square to an open laptop on the counter, the screen the room's cool light, cabinets and a tile backsplash, the lot's sodium through the window at the left"
  rect: [300, 560, 780, 790]
  bleeds: [right, bottom]
accent: "#7FB2D9"
job: >
  Hand the reader the one thing a Texan can do, and where to send it.

claims: [c1, c8, c9, c10, c11, c62]
numerals:
  - value_from: c8   # 60 days

composition:
  structure: >
    A seated camera three quarter from the laptop side, the resident's face and hands lit by the
    screen, the slider glass behind with the lot's warm light. The type sits on the dark wall and
    ceiling above.
  bands: >
    Top third, the dark room with the hook and the dek. Middle third, the resident and the laptop.
    Bottom third, the table top lit by the screen, the laptop's keyboard, the resident's forearms and hands modelled by the screen light, and a mug casting a soft shadow.
  focal: "the laptop screen and the lit face"

art:
  technique: "physically based render in a TXT.interior room, kit person, desk and laptop"
  why_this_technique: >
    The next step is a letter a person writes. A person writing it at night closes the night.
  palette: "dark room, cool screen, warm slider light"
  value_structure: >
    Lightest is the screen. Darkest is the ceiling. Frame median L* planned at 12.
  motion: "from the hook to the screen"

type:
  kicker: "What a Texan can do"
  hook: "Comment before the court rules"
  dek: "Comment within 60 days of the September 18th notice. Email ATR.Public-Comments-Tunney-Act-MB@usdoj.gov in English, to the Antitrust Division's Technology and Digital Platforms Section."

acceptance:
  - "the frame reads \"Comment before the court rules\""
  - "the laptop screen is the only cool light in the room"
  - "the email address sits whole on one line"
  - "no close date is printed anywhere on the frame"

risks:
  - "the kit person has no sit pose; crop at the shoulder and hide the legs under the table"
```
