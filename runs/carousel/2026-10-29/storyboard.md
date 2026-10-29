# Storyboard, 2026-10-29
# "The load went to the wind."

## The story, and what the fact check did to it

Soluna Holdings and Applied Digital entered a definitive agreement on October 21st, 2026 to form a jointly owned company
(c1) to develop a planned 50 MW critical IT data center for AI and HPC at Project Dorothy 3, near Silverton in Briscoe
County (c2). After closing Applied would hold 51% and Soluna 49% (c3). Closing depends on conditions that include the
approval of a tax abatement for the project in Briscoe County (c4), and the companies expect to close by the end of the
calendar year (c5). The tenant, ChronoScale, has signed only a non-binding letter of intent (c8), and Soluna says there
can be no assurance a lease follows (c9).

The place. Briscoe Wind is a 150 MW wind farm in Briscoe County (c6, c12). Soluna's first campus there, Project Dorothy,
is 100 MW built behind the meter at the wind farm (c12), and Dorothy 1 and 2 hold 98 MW energized (c13). In August Soluna
bought 397 acres beside it (c18) for Dorothy 3, which it describes as a campus of up to 300 MW (c14, c19). The wind farm's
substation sits directly across from that land (c20). The 397 acres exceed the 300 first identified, leaving room for more
data halls should further generation or storage become available (c21).

The turn. Phase 1 of Dorothy 3, the 50 MW the deal covers, is expected to draw power from both Briscoe Wind and the grid
(c7). Soluna describes Dorothy 3 as up to 300 MW and the wind farm as 150 MW. Code computes that the plan is 2.0 times the
wind farm (figures.json `d3_over_wind`). The deck sets those facts side by side. It never says the grid feed exists
BECAUSE the plan is bigger, because no claim says so.

The fact check moved four things, and every surface obeys them.
1. **Every Soluna figure is the company's own** (primary_corporate). ERCOT's Base Load classification (c15, c16) is
   Soluna's account and appears only attributed, if at all.
2. **No county agenda names the project.** The October 13th and 16th Commissioners Court agendas are scans that list no
   abatement item. That absence rests on no claim, so the deck does not state it. It states c22, the posted guidelines.
3. **No Briscoe County contact detail is verified.** The close points at the Commissioners Court only through c22.
4. **50 MW and 300 MW are two different numbers.** Phase 1 is 50 MW of a Dorothy 3 described as up to 300 MW. Every
   surface keeps them apart.

## Why this treatment, and what was grafted

Director B's THE PLACE is the spine: one county road on the Caprock, wind on its west side, the empty pasture on its
east, and the camera walking that road from the turbine to the county seat. The story's whole claim is "directly across
from", and a road between two sides of the frame is that claim drawn.

Grafted from Director A (THE MEASURED SCALE): the flanged tower section as the deck's unit. A section stands for 10 MW,
a drawing unit stated on every frame that uses it, so the turn is two columns of the wind's own parts, one twice the
other, standing on the pasture at true scale with a worker at their foot. It replaces B's frame 5 plan relief of two bands
on the road, which carried the risk the queue has named twice (a relief that reads as a tray or a bar chart).

Grafted from Director C (THE CONNECTION): the two feeds as two lines landing on one substation on frame 6, the wind's
wood H-frame from the left and the grid's lattice from the right, with no split drawn because c7 gives none.

Refused: C's strands as megawatts (a conductor's size follows current, and a utility reader would read it as a spec), A's
shadow-measured field (the slowest relief the repo has tried, for a figure the columns already show), B's chained gate as
a judgement of the deal (kept, but as the ownership split only, with the lock read as "not yet signed"), and B's
courthouse likeness (the kit courthouse is drawn to illustrate a county seat and is never named as Briscoe's).

## The world, and the laws that hold it

**LASTLIGHT, STAGED.** The chassis is `assets/js/deck/2026-10-29-caprock.js` and every frame loads it. It declares
`sky: lastLight` with the key at azimuth -78, elevation 10: the last light low in the west south west, as a late October
sun sets over the Llano. +x is east and +z is south. The county road runs north and south along x = 0. The wind farm and
its substation stand on the west side (x < 0), the pasture where Dorothy 3 is planned lies on the east side (x > 0). A
camera looking north has the key on its LEFT and every cast runs long to the right. A camera looking east has the key at
its back. A camera looking west sees the turbines against the seam.

One key casts. Substation lamps, a lit bay and a courthouse window are emissive and cast nothing.

The ground is Briscoe County's own: pale caliche for the road and pads, Quartermaster red bed earth in bare ground and the
disked strips, buffalo grass and blue grama gone to October straw, crushed limestone on the substation pad.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#08060F` | the DOM body behind the render |
| `accent` | `#6E7A5A` | mesquite, and it means ONE thing, what is planned for Dorothy 3: the flange rims of the planned column on 5, the survey flagging on 6, the 397 acre strip on 7, the gate's padlock tag on 8 |
| `hook` | `#ECE8DF` | light type on the dark |
| `dek` | `#D6D0C4` | the dek |
| `material` | `#DFE1DD` | the turbine and tower section paint |

The world's materials, from the Caprock country around Silverton: caliche, red bed earth, October straw grass, crushed
limestone, galvanized and weathered steel, wind tower paint, treated wood poles, the brick and granite of a county seat.

## The continuity devices

    CONTINUITY: CAMERA_MOVE, MOTIF_EVOLUTION, VALUE_ARC

1. **Camera move, along one road.** Up at a turbine from the road's verge (1), down onto the county (2), among the
   turbines at the first campus (3), through the substation's fence across the road (4), out on the pasture at the two
   columns (5), back across the road at the substation from the pasture (6), down onto the parcel (7), at the pasture's
   gate (8), and into the county seat (9).
2. **Motif evolution, the pasture's fence and what stands inside it.** The barbed wire fence along the road's east side is
   open and empty on 1, seen through the substation's mesh on 4, the ground the columns stand inside on 5, staked inside
   on 6, the parcel's outline on 7, chained shut at the gate on 8.
3. **Value arc, dusk to night.** The seam sinks across the deck, from the warm seam behind the turbine on 1 to full night
   at the courthouse on 9. The two reliefs (2, 7) carry the most light in the deck and stay inside the dark register.

## The rotation

    FULL_BLEED  MAP  OBJECT_AND_CAPTION  CLOSE_CROP  FIGURE_SCALE  FULL_BLEED  DIAGRAM  OBJECT_AND_CAPTION  FIGURE_SCALE

`TXLAYOUT.check` returns an empty list. Type sits on the dark sky or the dark unlit pasture on every frame.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | WIDE, eye 1.6 m on the pasture about 250 m from the tower, looking north west and up, fov 50 | the kit wind_turbine, a 90 m tapered tubular tower with flanges and a base door, nacelle and three twisted blades in three quarter view filling the upper two thirds, raked from the left by the low key against the warm seam, its gravel pad and pad mount transformer at its foot, a second turbine far off under the veil, the caliche road running north past its pad, contact at the tower foot, TXT.weather grime up the first metres |
| 02 | AERIAL, orthographic material relief, full bleed | Briscoe County raised as a caliche plateau among red earth neighbours from tx-counties.topo.json, county lines cut as grooves with one lit and one shadowed wall, a red sandstone pin at Silverton and a raised square of 397 acres at the map's own scale, tooth in albedo only |
| 03 | MEDIUM, eye 1.7 m on the pasture about 105 m off the hall's near corner, the hall running away to the right, fov 40 | the kit data_center as the first campus's hall, insulated metal panel walls, ten louvred intake bays as the chassis intake_bays at one per 10 MW, lit to the energized share with the last bay at its fraction, three kit wind_turbines behind it on the seam and a kit h_frame line from a turbine to the hall's far end, contact along the stem wall |
| 04 | CLOSE, eye 4.9 m inside the substation yard looking east and down, the radiator bank about 5 m off, fov 52 | the chassis radiator_bank of a transformer cropped by the left and bottom edges, weathered galvanized fins on two headers before the ribbed tank wall, raked by the key on a concrete pad over crushed rock, the kit chain_link_fence across the near foreground, the caliche road and the pasture's barbed wire fence beyond it lit in the pool |
| 05 | WIDE, eye 12 m about 145 m from the columns, looking north, fov 46 | two chassis section_stack columns of the chassis tower_section, 4.3 m at the foot and 3.0 m a section, tapering at the kit turbine's rate so thirty stand at its hub height, each on a concrete pedestal with the base door: the wind's at its section count with galvanized rims and the plan's at twice that with mesquite rims, raked from the left so every flange catches a lit line and both cast long to the right, a kit worker at their foot, contact and red dust splash at the base |
| 06 | MEDIUM, eye 1.15 m on the pasture, nearest stake about 5 m off, looking west across the road, fov 44 | the chassis survey_stake row receding across the near pasture with accent tops and flagging, one per 10 MW of Phase 1, and across the road about 240 m off the kit substation with a kit power_line of wood h_frames coming in from the turbines on the left and a kit power_line of 345 kV lattice towers from the right |
| 07 | AERIAL, orthographic material relief, full bleed | the parcel in plan at one px per metre: a square of 397 acres and a nested square of 300 acres sharing the road corner as disked furrow strips of turned red earth, each with one lit and one shadowed wall, fence posts proud along the outer edge, the caliche road along the west edge and the substation pad across it |
| 08 | CLOSE, eye 0.9 m, 5 m back from a double gate, fov 40 | two kit ranch_gates as one double gate closed across the pasture's caliche entrance, leaf widths in the ratio of the two ownership shares, galvanized tube raked along the top rails, a chassis chain and padlock at the off centre seam, contact under every post, white rust at the welds |
| 09 | WIDE, eye 1.3 m on the square's walk, courthouse about 130 m off filling half the width below the type, fov 44 | the kit county_courthouse in its romanesque style at night, brick and granite raked by the same low key from the left, one upper window emissive and non casting, a kit resident walking toward the steps at about 30 m turned away, contact at every base |

Showstopper frame: 05, two columns of the wind's own tower sections standing on the dark pasture in one pool of last light, one twice the other, every flange a lit tick, a worker at their foot for the size of it. Its depth is a horizon low behind the columns, haze over the far pasture, contact and long cast shadow across the lit grass, and the near column occluding the far turbines.
Tonal arc: the warm seam behind the turbine on 01, the lit caliche plateau on 02, the bays' glow on 03, the raked radiator
on 04, the columns' lit flanges on 05, the substation pool across the road on 06, the lit parcel on 07, the gate's lit
rails on 08, and the darkest frame on 09 with one window lit.
VALUE CUT: frame 5. The deck turns from what is built to what is planned, and the twice-height column is that turn.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "a utility scale wind turbine on the flat Caprock at last light, its tower and nacelle raked by the low key, the rotor cut by the top edge, a barbed wire fence and the caliche county road crossing the foreground with the dark empty pasture across it"
  rect: [700, 150, 380, 1200]
  bleeds: [right, bottom]
accent: "none"
job: >
  Put the reader on one county road in Briscoe County, under a wind turbine, before a word of the deal: the load came to
  this wind, and the pasture across the road is where the plan would stand.

claims: [c1, c2, c4, c6]
numerals:
  - value_from: c2

depth:
  eye: 1.4
  horizon: 1010
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, CAST_SHADOW, OCCLUSION]
  subject_at: {X: -60, Z: -70}

composition:
  structure: >
    The turbine stands just right of centre from about 250 m, seen from a low eye so the tower rises from the horizon and the rotor fills the upper two thirds in three quarter view. A second turbine stands far off on the left under the veil, and the dark pasture below the horizon carries the type.
  bands: >
    Top third, the dark sky with the lit rotor and the kicker and counter above it. Middle third, the lit tower and nacelle against the warm seam, the far turbine under the veil. Bottom third, the hook and dek on the dark pasture below the horizon, the turbine's base and pad lit at the horizon line casting shadow, with the source line and the site line.
  focal: "the lit nacelle and the upper tower, the lightest large area in the frame"

art:
  technique: "physically based render of the kit wind_turbine, barbed_wire_fence and caliche_road in the lastLight world, staged on the turbine"
  why_this_technique: "a modelled turbine raked by the last light reads as the machine the story is about, standing in a real place, rather than an icon of wind"
  palette: "warm white turbine paint, caliche, October straw grass, galvanized wire, near black sky with a warm seam"
  value_structure: >
    Lightest is the lit side of the tower and nacelle. Darkest is the sky and the unlit pasture. Frame median L* planned
    at 12.

type:
  hook: "The load went to the wind"
  dek: "Soluna announced on October 21st a deal with Applied Digital for a 50 MW AI data center beside the Briscoe Wind Farm near Silverton. Closing depends in part on a tax abatement in Briscoe County. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the kit wind_turbine is present with its tower, nacelle and at least two blades visible"
  - "the turbine's tower stands at least 300 px tall at full size"
  - "the turbine's base meets the ground at the horizon with a contact shadow"
  - "the hook and dek sit on the dark pasture and no blade or tower crosses their glyphs"
  - "the turbine carries no logo or wordmark"
  - "the frame's median L* at 432px is 24 or lower"

risks:
  - "a thin turbine silhouette can leave the subject rect sparse, so the rect hugs the tower and nacelle and the fence carries the foreground"
```

```yaml
slide: 2
layout: MAP
primary_image:
  subject: "Briscoe County raised as a caliche plateau among its red earth neighbours, county lines cut as grooves, a pin at Silverton and a raised square of 397 acres at the map's own scale"
  rect: [200, 350, 520, 900]
  bleeds: []
accent: "#6E7A5A"
job: >
  Say where, and how small the land is against a county: the 397 acres are a square a reader can barely find on the
  plateau.

claims: [c2, c18, c19]
numerals:
  - value_from: c18

data_in_art:
  figure: side_m_acres
  drives: "square side length in px, at the map's own metres per px"

depth:
  eye: 1000
  horizon: 0
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The county fills the middle of the frame from edge to edge with its neighbours bleeding off the left, right and bottom.
    Briscoe stands proud in pale caliche and casts its edge long onto the darker neighbours, Silverton's pin and the
    square sit inside it, and a label and leader name each.
  bands: >
    Top band, the hook and dek on the dark field outside the relief's pool. Middle, the lit plateau with the pin and the
    square. Bottom, the neighbours' relief falling from lit to dark, every groove casting its shadow, with the county names in mono and the source line.
  focal: "the lit Briscoe County plateau with the square in it"

art:
  technique: "TXBENCH.relief material relief of committed county geometry, four materials, under the chassis key"
  why_this_technique: "a where frame wants cartography, and a relief lets one county stand proud and cast its shadow without a flat map"
  palette: "caliche plateau, red bed earth neighbours, red sandstone pin, mesquite square"
  value_structure: >
    Lightest is the lit plateau. Darkest is the field outside the pool. Frame median L* planned at 16.

type:
  hook: "397 acres near Silverton"
  dek: "Soluna bought the land in August for Dorothy 3, its planned AI campus. The square is 397 acres at the map's own scale. Its place on the map is drawn to illustrate."
  labels: ["BRISCOE", "SILVERTON", "397 ACRES"]

verbatim: []

acceptance:
  - "Briscoe County stands raised above its neighbours with a visible cast shadow on at least one edge"
  - "at least four neighbouring counties are visible as lower relief"
  - "the 397 acre square is visible inside Briscoe and is under 30 px on a side at full size"
  - "a leader lands on the square and another on Silverton's pin"
  - "the raised Briscoe County plateau spans at least 40 percent of the frame width"
  - "no flat colour fill reads as a map tray, the relief bleeds left, right and bottom"

risks:
  - "a relief map can read as a tray, so it bleeds three edges and the pool falls off to the field"
```

```yaml
slide: 3
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "a long single storey data hall among wind turbines, ten intake bays lit warm with the last one lit to its fraction, a wood H-frame line tying it to the turbines behind the meter"
  rect: [0, 600, 1080, 520]
  bleeds: [left, right]
accent: "none"
job: >
  Show what is already here: the first campus built behind the meter at the wind farm, nearly all of it energized, and the
  chief executive's line about bringing load to the generation.

claims: [c10, c12, c13]
numerals:
  - value_from: c12
  - value_from: c13

data_in_art:
  figure: bays_energized
  drives: "lit bay count, one bay per section_mw, the last bay's glow set to its fraction"

depth:
  eye: 1.7
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The hall runs away from the camera across the frame in three quarter view, its near end large on the left and its far
    end small on the right, every bay's louvres glowing. Three turbines stand on the seam behind it, and a short wood pole
    line crosses from the turbines to the hall.
  bands: >
    Top third, the dark sky with the hook and the dek, a turbine's blades crossing above the dek. Middle, the hall's lit
    bays. Bottom, the caliche pad and straw grass in the pool falling to dark, the label naming the bay unit and the source
    line.
  focal: "the row of glowing intake bays"

art:
  technique: "physically based render of the kit data_center, wind_turbine and h_frame in the lastLight world, staged on the hall"
  why_this_technique: "a built hall with its bays lit makes energized capacity a thing a reader can count, at one bay per unit"
  palette: "pale grey panel walls, warm bay glow, caliche pad, turbine white against the seam"
  value_structure: >
    Lightest is the bay glow and the lit end wall. Darkest is the sky and the grass beyond the pool. Frame median L* planned at 13.

type:
  hook: "Built behind the meter"
  dek: 'Soluna describes Project Dorothy as 100 MW built behind the meter at the 150 MW wind farm. In September it said 98 MW was energized. Its chief executive says Soluna was built "to bring load to the generation". One bay stands for 10 MW. Drawn to illustrate.'
  labels: ["ONE BAY, 10 MW"]

verbatim: ["to bring load to the generation"]

acceptance:
  - "the kit data_center hall is present and modelled with panel walls and louvred bays"
  - "the kit data_center hall stands at least 120 px tall at full size"
  - "ten intake bays are visible along the hall, nine fully lit and one lit dimmer than the others"
  - "at least two wind turbines stand behind the hall"
  - "a pole line connects toward the hall from the turbines"
  - "the hall owns at least 40 percent of the frame width at 432px"
  - "the hook and dek sit on dark sky clear of the turbine blades"

risks:
  - "the kit data_center's own bay count may differ, so the frame builds its lit bay row from the figure rather than trusting the model's panels"
```

```yaml
slide: 4
layout: CLOSE_CROP
primary_image:
  subject: "inside the wind farm substation's fence, a transformer's galvanized radiator bank cropped by the left and bottom edges, and across the caliche road the pasture's barbed wire fence lit in the pool with empty grass going to black"
  rect: [0, 560, 620, 790]
  bleeds: [left, bottom]
accent: "none"
job: >
  Make "directly across from" literal: the wind farm's substation on one side of a county road and the empty pasture on
  the other.

claims: [c20, c18]
numerals: []

depth:
  eye: 4.9
  horizon: 860
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, OCCLUSION, CAST_SHADOW, AERIAL]
  subject_at: {X: -14, Z: 0}

composition:
  structure: >
    The radiator bank fills the lower left, close and cropped, every fin raked by the key. The chain link mesh crosses
    the near foreground soft. Beyond, the road runs across the frame and the pasture's fence stands lit in a pool on the far
    side, its posts small.
  bands: >
    Top third, the dark sky with the hook and dek. Middle right, the road and the lit pasture fence. Bottom left, the lit radiator bank in the foreground casting shadow onto the crushed rock pad, with the source line.
  focal: "the lit radiator fins and the pasture fence across the road"

art:
  technique: "physically based render of a transformer radiator bank built in the slide, with the kit chain_link_fence, caliche_road and barbed_wire_fence in the lastLight world"
  why_this_technique: "the claim is a distance between two real things, and a camera standing in one looking at the other draws it"
  palette: "weathered galvanized steel, crushed limestone, caliche, straw grass, near black sky"
  value_structure: >
    Lightest is the raked fins and the pool on the far fence. Darkest is the sky. Frame median L* planned at 10.

type:
  hook: "Directly across from the land"
  dek: "Soluna says the wind farm's substation sits directly across from the land it bought. It says that positions Dorothy 3 for behind the meter access to generation it owns outright. The substation, road and pasture are drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "a transformer radiator bank fills at least a quarter of the frame, cropped by the left or bottom edge"
  - "chain link mesh is visible in the foreground"
  - "a barbed wire fence with at least three posts stands across a road beyond the substation"
  - "the transformer carries a weathered surface rather than a flat grey"
  - "the hook and dek sit on dark sky"

risks:
  - "the kit substation has read as grey clay, so the chassis gives it a weathered galvanized skin and the crop stays on the radiators"
```

```yaml
slide: 5
layout: FIGURE_SCALE
primary_image:
  subject: "two columns of flanged wind tower sections standing on the dark pasture, the wind farm's at its section count with galvanized rims and Dorothy 3's planned at twice that with mesquite rims, a worker at their foot"
  rect: [380, 100, 400, 1100]
  bleeds: []
accent: "#6E7A5A"
job: >
  The turn, drawn so it reads without the headline: in the wind's own parts at one scale, the AI campus planned beside the
  wind farm stands twice as tall as the wind.

claims: [c6, c14, c19]
numerals:
  - value_from: c14
  - value_from: c6
  - computed_by: figures.json d3_over_wind
  - computed_by: figures.json section_mw

data_in_art:
  figure: sections_d3
  drives: "the number of sections in the planned column, beside sections_wind in the wind's column, at one section_mw a section"

depth:
  eye: 1.6
  horizon: 1040
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: -34}

composition:
  structure: >
    The two columns stand side by side in the middle of the frame from a low eye 34 m off, the wind's on the left at half
    the height of the plan's on the right. The worker stands at the foot of the shorter column, small, so the columns
    have a size. The key comes from the left and every flange throws a lit line, and both columns cast long to the right
    across the straw grass.
  bands: >
    Top, the dark sky with the hook and the dek to the left of the tall column's top. Middle, the two lit columns, the tall
    one rising past the short one by its own height again. Bottom, the lit pasture in the foreground with both columns' long shadow across the straw grass, the labels at each column's foot and the source line.
  focal: "the planned column's top flange, twice as high as the wind column's"

art:
  technique: "physically based render of the chassis tower_section stacks and a kit person in the lastLight world, staged on both columns"
  why_this_technique: "a ratio is two rendered lengths at one scale, and measuring the load in the wind's own tower sections measures it in the wind's units"
  palette: "warm white section paint, galvanized and mesquite flange rims, straw grass, red earth, near black sky"
  value_structure: >
    Lightest is the lit side of both columns and their flange lines. Darkest is the sky. Frame median L* planned at 11.

type:
  hook: "The plan is twice the wind"
  dek: "Soluna describes Dorothy 3 as up to 300 MW and the wind farm beside it as 150 MW. Each section stands for 10 MW, a drawing unit. Drawn to illustrate."
  labels: ["WIND FARM 150 MW", "DOROTHY 3 UP TO 300 MW"]

verbatim: []

acceptance:
  - "two columns of flanged sections stand side by side, the right one's top at least 1.8 times the left one's height above the ground"
  - "the left column shows 15 distinct sections and the right 30, counted by lit flange lines"
  - "a person stands at the foot of a column and is under one fifth of the frame height"
  - "the taller column stands at least 600 px tall at full size"
  - "the right column's flange rims carry the mesquite accent and the left column's do not"
  - "both columns cast shadows to the right across lit ground"
  - "the hook and dek sit on dark sky"

risks:
  - "stacks can read as chimneys or silos, so frame 1's turbine shows the same flange at its base and the dek names the section as a drawing unit"
```

```yaml
slide: 6
layout: FULL_BLEED
primary_image:
  subject: "survey stakes with mesquite flagging close in the pasture foreground, and across the road the wind farm substation in its pool, a wood pole line coming in from the turbines on the left and a lattice transmission line coming in from the right"
  rect: [0, 620, 1080, 730]
  bleeds: [left, right, bottom]
accent: "#6E7A5A"
job: >
  The mechanism the release states: Phase 1 is expected to draw power from both Briscoe Wind and the grid, two lines into
  one place, with no split between them made public.

claims: [c7, c2]
numerals:
  - value_from: c7
  - computed_by: figures.json section_mw

data_in_art:
  figure: sections_phase1
  drives: "the number of survey stakes in the row, one per section_mw of Phase 1"

depth:
  eye: 1.5
  horizon: 900
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, OCCLUSION, CAST_SHADOW, AERIAL]
  subject_at: {X: -40, Z: 0}

composition:
  structure: >
    The stakes stand large in the near foreground, the nearest a third of the frame tall, receding in a row toward the road.
    Across the road the substation sits in its pool, the wood H-frames march in from the left out of the turbines and the
    lattice towers march in from the right, both landing on the yard. Leaders name the two lines.
  bands: >
    Top third, the dark sky with the hook and the dek, the lattice towers' tops under the dek. Middle, the lit substation and
    both lines. Bottom, the lit stakes and straw grass in the foreground, each stake casting a shadow, with the labels and the source line.
  focal: "the lit substation where both lines land"

art:
  technique: "physically based render of the chassis survey_stake, kit substation and two kit power_line runs in the lastLight world"
  why_this_technique: "two lines arriving at one yard draws the release's two sources without inventing a split"
  palette: "weathered pine stakes with mesquite flagging, galvanized lattice, treated wood poles, straw grass, near black sky"
  value_structure: >
    Lightest is the substation pool and the flagging. Darkest is the sky. Frame median L* planned at 10.

type:
  hook: "Two feeds for Phase 1"
  dek: "Phase 1 of Dorothy 3 is the 50 MW in the deal. Soluna expects it to draw power from both Briscoe Wind and the grid, subject to definitive documentation. Each stake stands for a fifth of it, a drawing unit. Drawn to illustrate."
  labels: ["BRISCOE WIND", "THE GRID"]

verbatim: []

acceptance:
  - "five survey stakes with flagging stand in the foreground, the nearest at least 300 px tall at full size"
  - "a line of wood pole structures enters from the left and a line of lattice towers from the right"
  - "both lines end at the substation"
  - "a leader lands on each line and its label names the source"
  - "the hook and dek sit on dark sky"

risks:
  - "conductors are hairlines at 432px, so the structures carry the lines and the leaders name them"
```

```yaml
slide: 7
layout: DIAGRAM
primary_image:
  subject: "the parcel in plan, a square of 397 acres and a nested square of 300 acres sharing the road corner, cut as disked furrow strips with lit and shadowed walls, fence posts proud along the outer edge, the caliche road and the substation pad across it"
  rect: [60, 400, 960, 900]
  bleeds: []
accent: "#6E7A5A"
job: >
  Show the room the release describes: the land is bigger than the campus first planned, and Soluna says the extra land
  leaves room for more data halls if more generation or storage arrives.

claims: [c18, c21, c20]
numerals:
  - value_from: c18
  - value_from: c21
  - computed_by: figures.json acres_extra

data_in_art:
  figure: side_m_acres
  drives: "the outer square's side in px at one px per metre scale, beside side_m_first for the nested square"

depth:
  eye: 1000
  horizon: 0
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The outer square fills most of the frame from straight above, its furrow strip lit on the key's side and shadowed on
    the other. The nested square shares the road corner at the upper left, leaving an L of grass on the right and bottom
    that is the extra land. The road runs down the left edge and the substation pad sits across it.
  bands: >
    Top band, the hook and dek on the dark field. Middle and bottom, the lit parcel with the L and its label, the posts
    casting a comb of shadows, and the source line.
  focal: "the L-shaped strip of extra land between the two squares"

art:
  technique: "TXBENCH.relief material relief of the parcel at true area, five materials, under the chassis key"
  why_this_technique: "an area comparison wants parallel projection, and a furrow cut into the ground with a lit and a shadowed wall reads as land, not a chart"
  palette: "red earth furrows, straw grass, caliche road, crushed limestone pad, mesquite on the outer strip"
  value_structure: >
    Lightest is the lit furrow walls and the road. Darkest is the field outside the pool. Frame median L* planned at 15.

type:
  hook: "Room for more data halls"
  dek: "The 397 acres exceed the 300 acres Soluna first identified for the campus. Soluna says the extra 97 acres leave room to add data halls if more generation or storage becomes available. Squares are drawn to area, not the parcel's shape."
  labels: ["397 ACRES", "300 ACRES", "SUBSTATION", "97 ACRES MORE"]

verbatim: []

acceptance:
  - "the parcel's outer square is present as a furrow strip and spans at least 60 percent of the frame width"
  - "two nested squares are visible, the inner one's side at least 0.85 and at most 0.9 of the outer's"
  - "both squares are cut as furrows showing one lit wall and one shadowed wall"
  - "fence posts stand proud along the outer square's edge and cast shadows"
  - "a road runs along one edge with a raised pad across it"
  - "the relief bleeds left, right and bottom with no tray edge"

risks:
  - "a plan relief can read as a tray, so the ground is full bleed and the posts stand proud with real casts"
```

```yaml
slide: 8
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "a double galvanized ranch gate closed across the pasture's caliche entrance, its two leaves split in the ratio of the two ownership shares, a chain and padlock at the off centre seam"
  rect: [0, 640, 1080, 560]
  bleeds: [left, right]
accent: "#6E7A5A"
job: >
  The deal's terms as a gate across the land: two owners in an unequal split, and a lock that stays shut until the
  conditions are met and a tenant signs.

claims: [c3, c8, c9, c5]
numerals:
  - value_from: c3

data_in_art:
  figure: applied_pct
  drives: "the width of the left gate leaf as a share of the opening, beside soluna_pct for the right leaf"

depth:
  eye: 0.9
  horizon: 980
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The gate spans the frame's width from a low eye 5 m back, its top rails catching the key from the left. The seam sits
    just off centre, with the chain and padlock hanging there. The caliche entrance runs under it into the dark pasture.
  bands: >
    Top, the dark sky with the hook and dek. Middle, the lit gate rails and the lock. Bottom, the caliche entrance in the
    pool, the leaf labels and the source line.
  focal: "the padlock at the off centre seam"

art:
  technique: "physically based render of two kit ranch_gates and a chassis padlock in the lastLight world, staged on the gate"
  why_this_technique: "an ownership split is two widths at one scale, and a gate across the land is what a joint company holds"
  palette: "galvanized tube, painted oilfield pipe posts, caliche, mesquite padlock tag, near black sky"
  value_structure: >
    Lightest is the lit top rails. Darkest is the pasture behind the gate. Frame median L* planned at 10.

type:
  hook: "A letter of intent, not a lease"
  dek: "After closing Soluna expects Applied to hold 51% and itself 49%. ChronoScale is majority owned by Applied. ChronoScale has signed a non-binding letter of intent to lease. Soluna says a lease may not follow. It expects closing by year end. Drawn to illustrate."
  labels: ["APPLIED 51%", "SOLUNA 49%"]

verbatim: []

acceptance:
  - "a double gate spans at least 70 percent of the frame width"
  - "the seam between the two leaves sits off centre, the left leaf wider than the right"
  - "a chain and padlock hang at the seam"
  - "every gate post meets the ground with a contact shadow"
  - "the hook and dek sit on dark sky"

risks:
  - "a gate can read as a judgement on the deal, so the copy states the conditions and the tenant's letter as the release does"
```

```yaml
slide: 9
layout: FIGURE_SCALE
primary_image:
  subject: "a county courthouse on its square at night, drawn to illustrate a county seat, one upper window lit, a resident walking toward the steps"
  rect: [140, 420, 800, 800]
  bleeds: []
accent: "none"
job: >
  The consequence and the way in: the deal closes only if Briscoe County approves a tax abatement, and the county posts its
  abatement guidelines beside its Commissioners Court agendas.

claims: [c4, c22]
numerals: []

depth:
  eye: 1.0
  horizon: 1060
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, OCCLUSION, CAST_SHADOW, AERIAL]
  subject_at: {X: 0, Z: -70}

composition:
  structure: >
    The courthouse fills half the width from 130 m on the square's walk, below the type, raked by the same low key from the left, its upper rooms lit. A resident walks toward the steps at about 30 m, turned away, small. The square's walk
    leads in from the bottom.
  bands: >
    Top, the dark sky with the hook and dek. Middle, the lit facade and the clock tower. Bottom, the lit walk in the foreground with the resident's shadow, and the source line.
  focal: "the lit upper window in the raked facade"

art:
  technique: "physically based render of the kit county_courthouse and a kit person in the lastLight world, staged on the courthouse"
  why_this_technique: "the next step is a public body, and a county seat at night with one window lit is where a reader would take it"
  palette: "brick and granite, warm window, near black sky"
  value_structure: >
    Lightest is the raked facade and the lit window. Darkest is the sky. Frame median L* planned at 8, the deck's darkest.

type:
  hook: "An abatement comes first"
  dek: "Closing depends in part on approval of a tax abatement for the project in Briscoe County. The county posts its tax abatement guidelines beside its Commissioners Court agendas. The courthouse is drawn to illustrate a county seat."
  labels: []

verbatim: ["TAX ABATEMENT - GUIDELINES AND CRITERIA"]

acceptance:
  - "a courthouse with a tower fills at least 45 percent of the frame width"
  - "at least one upper window glows warm"
  - "a person walks on the walk at under one fifth of the frame height, turned away from the camera"
  - "the facade is raked from the left so its pilasters or arches cast to the right"
  - "the hook and dek sit on dark sky"

risks:
  - "a kit person can read as a mannequin, so the resident stays at 12 m, walking, turned away and lit from the camera side"
```
