# Storyboard, 2026-10-17
# "What keeps T cells out of a tumor"

## The story, and what the fact check did to it

On October 13th MD Anderson announced SPACER, an AI model built with collaborating Texas institutions that helps
explain how immune cells find their way to specific places in the body and why they avoid others (c1). It reads
spatial transcriptomics, which measures gene activity inside intact tissue and shows which genes are active and
where (c2), and it looks at groups of neighboring cells rather than at cells one at a time (c3). The team ran it
across 37 datasets and reports it was four to 21 times more effective than existing approaches in benchmarking
tasks (c4). Immune cells appear to answer signals in their immediate surroundings (c5), tumors expressing antigen
presentation genes were more likely to attract T cells (c6), and mucins, large sugar coated proteins many cancers
make, may help create physical barriers that keep T cells away from tumors (c7). In several melanoma and gastric
cancer datasets, more mucin went with poorer responses to checkpoint inhibitors and poorer outcomes (c8). The
researchers believe it could potentially be used as a diagnostic tool (c9), and Linghua Wang calls the findings ideas
to test in the lab (c10). The study is in Nature Biomedical Engineering, published October 13th (c11, c16, c17), and
the release names five funders, the Cancer Prevention and Research Institute of Texas among them (c12). The record
carries it as tx-2026-0217.

**WHAT THE FACT CHECK CHANGED.**
- **No CPRIT figure and no voter sentence.** cprit.texas.gov refused the fetcher, so the deck says only that the
  Texas fund is one of the five funders the release names (c12).
- **The 37 datasets include mouse heart** (c20). The deck says several cancer types only where it quotes the
  release (c4), and frame 3 adds the abstract's own words.
- **Co-led is MD Anderson's word**, not the journal's (rejected). No frame names a lead author.
- **The mucin link is an association in existing data** (c8) and the release reports no use in patient care. Every
  frame that draws the wall says may, and frame 8 says association.
- **Nothing drawn is a patient's tissue.** Every section, slide and cell is drawn to illustrate. A dataset can hold
  more than one section, so one slide per dataset is a drawing convention, and frame 2 says so.

## Why this treatment, and what was grafted

Three directors pitched THE MEASURED EVIDENCE FIELD (one slide world under a darkfield key, seen at seven scales),
ADDRESSES AND A WALL (the release's own postal comparison, a copper route stopping at a mucin rampart) and WHAT A
TEXAN HOLDS (a glass slide the size of a finger, down to the wall and back up to the bench).

- **From THE MEASURED EVIDENCE FIELD, the spine and the world.** Nine plan views of one bench under a low key from
  the upper left, the 37 as a panorama of slides cut across two frames, the benchmark as one rule at two scales so
  four and 21 each get a frame, and the cover and frame 6 on the same camera.
- **From WHAT A TEXAN HOLDS, the honest close and the 2 by 2.** Lower and higher mucin by melanoma and gastric on
  frame 8, and a close that puts the slide back under a lens rather than in a clinic.
- **From ADDRESSES AND A WALL, the wall's build and the funders.** The mucin coat as the tallest thing on its frame,
  glossy, its cast falling over the tumor cells, and the funders as engraved lines on the slide's label.
- **Refused:** the postal route (SPACER infers signals and tracks no cell's route, so a drawn route overclaims), the
  sorting case (a second metaphor on top of the slide), every txthree frame and every new kit model (a microscope, a
  quarter, a gloved hand: each is a mannequin risk the relief route avoids), and a heart section beyond cancer
  (preclinical, one line in the caption at most).
- **The accent.** Dusk ember #B4664F, the brown a pathologist sees when T cells are stained, on the T cells and
  nothing else. It carries frames 1, 6, 7 and 8, the frames where a T cell is big enough to see.

## The world, and the laws that hold it

**A DARKFIELD BENCH.** The chassis is `assets/js/deck/2026-10-17-section.js` and every frame loads it. It declares
one key at azimuth 300, elevation 16: the light comes low from the upper left, so every lit face is an upper left face
and every cast runs down and to the right, about three and a half times the height of what casts it. There is no sky
and no room. Darkfield is how a microscope stages a specimen, oblique light on black so only edges and raised
surfaces glow, and it gives the bold register by construction.

1. **Start dark.** A near black bench and glass, one lit edge per subject.
2. **Type is light, on the dark field**, and the only wash darkens the footer row.
3. **Ember is the T cell and nothing else.**
4. **Heights are drawn to separate materials and are not measured.** Every frame that shows tissue says drawn to
   illustrate.
5. **Nothing drawn is a real patient's tissue, and nothing is a verdict on treatment.**

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#05040A` | the DOM body behind the render, the bench |
| `accent` | `#B4664F` | dusk ember, the T cells: 1, 6, 7, 8 |
| `hook` | `#ECE6DC` | light type on the dark |
| `dek` | `#D6CEC4` | the dek |
| `material` | `#3A1424` | the tissue ramp's oxblood |

The materials: black bench and slide glass, dark plum stroma fibre, oxblood tumor cells each with a nucleus dimple,
a pale cool mucin glaze with a hard specular, ember T cells, graphite spots, worn steel for the rule and the stage, and
the slide's frosted label end.

## The continuity devices

    CONTINUITY: CAMERA_MOVE, EDGE_TEASE, MOTIF_EVOLUTION

1. **Camera move, as a microscope turret.** Macro on the nest (1), out to the slide panorama (2, 3), the rule at two
   scales (4, 5), back down to cell scale (6, 7), core scale (8) and the whole slide on the stage (9).
2. **Edge tease.** The slide panorama is cut by frame 2's right edge and completes on frame 3. The rule's long bar
   runs off frame 4's right edge and ends on frame 5.
3. **Motif evolution.** The ember T cells' place against the tumor: halted outside the coat (1), pressed against the
   cells next door (6), banked at the wall's foot (7), inside the lower mucin cores and outside the higher ones (8).

## The rotation

    FULL_BLEED  GRID  GRID  CLOSE_CROP  FIGURE_SCALE  DIAGRAM  FULL_BLEED  SPLIT_HORIZON  OBJECT_AND_CAPTION

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | MACRO, plan view on one nest edge | the tumor nest, oxblood cells domed with a nucleus dimple each, ringed by the glossy mucin coat that catches the key on its upper left shoulder and casts over the first row of cells, ember T cells halted on the stroma outside it |
| 02 | WIDE, plan view on the bench at slide scale | the slide panorama's left half, black glass slides with green lit bevels and frosted label ends, each carrying its own dark section 2 px proud, casting thin shadows down and right on the black bench |
| 03 | WIDE, plan view on the bench at slide scale | the slide panorama's right half, black glass slides with lit bevels and frosted label ends casting thin shadows down and right, the cut slide completing at the left edge and the lower row ending short on bare bench |
| 04 | CLOSE, plan view on a steel stage rule | the rule plate in worn steel with engraved unit grooves, a frosted bar one unit long and a polished steel bar four units long whose cut end throws a long cast, a lower terrace running off the right edge |
| 05 | MEDIUM, plan view on the same rule from farther off | the stage rule, worn brushed steel lit along its top faces, the one unit frosted bar, the four unit steel bar and the terrace ending at 21 engraved units, each casting a long shadow down and right |
| 06 | MACRO, the cover's camera on a nest with no coat | the tumor nest, oxblood cells in relief lit on their upper left shoulders with a nucleus dimple each, the outer row carrying raised steel studs, ember T cells pressed into its margin casting short shadows, a raised kerb ringing one neighborhood |
| 07 | MACRO, plan view on the wall | the mucin wall crossing the frame on a diagonal, the tallest thing on the deck, its crest one bright glaze line, its cast falling over the tumor cells below it, ember T cells banked on its outer slope and none past the crest |
| 08 | MEDIUM, plan view on four cores | the tissue cores, four rounds of plum and oxblood relief on black glass lit from the upper left, the higher mucin cores ringed by a tall glossy glaze with ember T cells outside, each core casting a shadow down and right |
| 09 | CLOSE, plan view on a microscope stage | the black anodised stage plate with two spring clips holding the whole slide over the lit aperture, the section glowing at the aperture's rim, five engraved lines on the frosted label end |

Showstopper frame: 07, a pale glazed wall on a dark diagonal with ember cells banked against it and its long cast over the tumor cells; its depth is the wall's height against the cells, the cast falling across the cobbled tumor and the cavity shadow where the cells meet the wall's foot
Tonal arc: dark tissue with one glaze crescent on 1, the near black bench with a row of frosted labels on 2 and 3, the darkest frames on the steel rule at 4 and 5, the warm ember field on 6, the brightest glaze on 7, four small cores in the dark on 8, the lit aperture on 9
VALUE CUT: frame 7. The deck turns from what draws T cells in to what may keep them out, and the brightest glaze line in the deck is that turn.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "a tumor nest of oxblood cells ringed by a glossy pale mucin coat at macro, ember T cells halted on the dark stroma outside it, the section's edge running across under the type"
  rect: [0, 600, 1080, 750]
  bleeds: [left, right, bottom]
accent: "#B4664F"
job: >
  Put the finding in front of the reader as one image, a wall and the cells it keeps out, and name MD Anderson's AI model as the thing that found it.

claims: [c1, c7, c17, c24]
numerals:
  - value_from: c17

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    Plan view. The nest sits right of centre in the lower two thirds, its coat a closed ring that the bottom edge crops.
    The T cells crowd the stroma to the left of the coat and stop at its outer foot, so the eye runs from the dense
    ember field to the bright crescent of the coat and into the dark cells it encloses.
  bands: >
    Top third, the bare dark glass above the section's torn edge, carrying the kicker, hook and dek. Middle third, the
    section edge, the T cells and the coat's upper arc. Bottom third, the nest's domed cells in relief under the coat's cast shadow, their lit upper left shoulders, and the coat's lower arc cropped by the frame.
  focal: "the coat's lit crescent on its upper left shoulder, with the ember T cells pressed against its foot"

art:
  technique: "TXBENCH.relief multi-material relief with Voronoi cells for the nest and a spatial hash of bead cells for the T cells"
  why_this_technique: "the finding is physical, a coat that may wall cells off, and only a surface with height and a cast shows a wall"
  palette: "black glass, dark plum stroma, oxblood tumor, pale cool mucin glaze, ember T cells"
  value_structure: >
    Lightest is the coat's crescent and the lit shoulders of the T cells. Darkest is the bare glass and the nest's interior under the coat's cast. Frame median L* planned at 7.

type:
  hook: "What keeps T cells out of a tumor"
  dek: "An AI model from MD Anderson and Texas collaborators helps explain where immune cells go. One finding is about mucins, sugar coated proteins many cancers make. They may help keep away T cells, white blood cells of the immune system. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the nest of domed cells and its pale coat are whole in the lower half of the frame, and a frame without the coat fails this item"
  - "the tumor nest with its coat is at least 700 px across at full size and the coat's lit crescent reads at 432px"
  - "at least 150 ember T cells stand on the stroma left of the coat and none sits inside it"
  - "the hook and dek sit on dark glass above the section's edge"
  - "the frame's median L* at 432px is 14 or lower"

risks:
  - "macro tissue can read as a tray of beads, so the coat's crescent carries the frame and the copy names the tissue"
  - "the ember field can pass the 8 percent accent cap, so the bead count is measured on the render"
```

```yaml
slide: 2
layout: GRID
primary_image:
  subject: "the left half of a panorama of glass microscope slides on a black bench, two rows, each with a frosted label end and its own dark section, the last slide in each row cut by the right edge"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: none
job: >
  Say what SPACER reads, gene activity inside intact tissue and where it happens, and start the count of datasets as slides on a bench.

claims: [c2, c4]
numerals: []

data_in_art:
  figure: datasets
  drives: slide count on the shared panorama, laid out in two rows of which this frame draws the left half

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    Plan view on the bench. Two rows of slides run from the left edge to the right edge, the label ends aligned at the
    top of each row, so the frosted ends make two bright bands and the sections two rows of dark islands. The right
    edge cuts the last slide of each row, which completes on the next frame.
  bands: >
    Top third, bare black bench with the type. Middle third, the upper row of slides. Bottom third, the lower row of slides in relief, their lit bevels and the shadows they cast down and right onto the black bench.
  focal: "the two rows of frosted label ends, the brightest areas in the frame"

art:
  technique: "TXBENCH.relief of glass slides with bevelled edges, frosted label ends and seeded tissue sections"
  why_this_technique: "a count of datasets is a count of things, and a slide is the thing a reader can picture tissue on"
  palette: "black bench, black glass with a green lit bevel, frosted white label, dark plum and oxblood sections"
  value_structure: >
    Lightest are the frosted label ends. Darkest are the bench and the glass. Frame median L* planned at 4.

type:
  hook: "It reads gene activity where it happens"
  dek: "SPACER uses spatial transcriptomics, which measures gene activity inside intact tissue and shows which genes are active and where. Each glass slide drawn here stands for one dataset. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "two rows of glass slides with frosted label ends run across the frame, and a frame without the slides fails this item"
  - "each slide is at least 90 px wide at full size and the slides come apart into separate pieces at 432px"
  - "the last slide of each row is cut by the right edge"
  - "the frame's median L* at 432px is 12 or lower"

risks:
  - "slides on black can vanish, so their bevels and labels carry them"
```

```yaml
slide: 3
layout: GRID
primary_image:
  subject: "the right half of the slide panorama, the cut slides completing at the left edge, the lower row ending short on bare bench"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: none
job: >
  Land the count, 37 datasets, and say what the abstract says they span.

claims: [c4, c20]
numerals:
  - value_from: c4

data_in_art:
  figure: datasets
  drives: slide count, the rows ending at the 37th slide with the lower row short on bare bench

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The same bench and rows as frame 2, continued. The upper row runs to near the right edge and the lower row stops
    short, so the empty bench at lower right says the count ends here.
  bands: >
    Top third, bare bench with the type. Middle third, the upper row. Bottom third, the short lower row in relief with lit bevels and cast shadows, the last slide's shadow ending on the black bench where the count stops.
  focal: "the short lower row ending on bare bench"

art:
  technique: "TXBENCH.relief of glass slides, continuing frame 2's panorama"
  why_this_technique: "the count completes across a swipe, so the reader counts with the deck rather than being told"
  palette: "black bench, black glass with a green lit bevel, frosted white label, dark sections"
  value_structure: >
    Lightest are the frosted label ends. Darkest are the bench and the empty space after the last slide. Frame median L* planned at 4.

type:
  hook: "37 datasets, human tumors and mouse heart"
  dek: "The team ran SPACER across 37 datasets. The release says they represent several cancer types. The journal abstract adds mouse heart. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the slide panorama's upper row of glass slides runs across the frame and the lower row ends short on bare bench, and a frame without the slides fails this item"
  - "each glass slide in the panorama is at least 90 px wide at full size and the slides come apart into separate pieces at 432px"
  - "the slides drawn across frames 2 and 3 total 37"
  - "the frame's median L* at 432px is 12 or lower"

risks:
  - "the two halves can read as one frame twice, so the empty bench at lower right is the change"
```

```yaml
slide: 4
layout: CLOSE_CROP
primary_image:
  subject: "a worn steel stage rule at close range, engraved unit grooves, a frosted bar one unit long and a polished steel bar four units long whose cut end casts, a lower terrace running off the right edge"
  rect: [0, 600, 1080, 750]
  bleeds: [left, right, bottom]
accent: none
job: >
  Show the low end of the benchmark, four times existing approaches, as two lengths at one scale.

claims: [c4]
numerals:
  - value_from: c4

data_in_art:
  figure: benchmark_low
  drives: the steel bar's length in units of the frosted bar, at one scale

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The rule plate fills the lower half and bleeds three edges. The frosted bar sits on the upper track at the left,
    one unit long. The steel bar runs four units on the lower track and ends in a cut whose cast is the frame's
    strongest dark. A terrace continues past it and leaves the frame at the right.
  bands: >
    Top third, dark bench with the type. Middle third, the plate's upper edge, the unit grooves and the frosted bar.
    Bottom third, the steel bar in relief with its brushed texture lit along the top face, its cut end casting a long shadow, and the terrace leaving the frame.
  focal: "the steel bar's lit top face and its cut end"

art:
  technique: "TXBENCH.relief of a machined rule, grooves kept crisp, bars at one scale"
  why_this_technique: "a ratio is two lengths at one scale, and steel takes a raking key as a hard bright edge"
  palette: "worn steel, frosted glass, black anodised plate"
  value_structure: >
    Lightest is the steel bar's top face. Darkest is its cast and the bench. Frame median L* planned at 5.

type:
  hook: "Four times, the low end"
  dek: "In benchmarking tasks the team reports SPACER was four to 21 times more effective than existing approaches at finding signals linked to cell recruitment. One unit here stands for existing approaches."
  labels: ["existing approaches", "4"]

verbatim: []

acceptance:
  - "the steel bar is exactly four times the frosted bar's length, and a frame without both bars fails this item"
  - "the stage rule plate is at least 1000 px wide at full size and its frosted bar at least 100 px long"
  - "a terrace continues past the steel bar's end and runs off the right edge"
  - "the frame's median L* at 432px is 14 or lower"

risks:
  - "steel blocks can read as bars of chocolate, so the grooves are engraved fine and the top faces carry a brushed tooth"
```

```yaml
slide: 5
layout: FIGURE_SCALE
primary_image:
  subject: "the whole stage rule at one scale, the one unit frosted bar, the four unit steel bar now short, and the terrace ending at 21 engraved units"
  rect: [0, 620, 1080, 600]
  bleeds: [left, right]
accent: none
job: >
  Show the high end of the benchmark at the same scale as the low end, so four to 21 reads as a span, and say whose measure it is.

claims: [c4]
numerals:
  - value_from: c4

data_in_art:
  figure: benchmark_high
  drives: the terrace's end and the engraved groove count, 21 units at one scale

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The rule runs the full width in the middle of the frame, seen from farther off than frame 4. Three tracks stacked:
    one unit, four units, and the terrace to 21. DOM mono labels sit at each end.
  bands: >
    Top third, dark bench with the type. Middle third, the rule and its three tracks. Bottom third, the rule plate's lit machined lower edge in relief, the long shadow it casts down and right, and the bench's grain beyond it.
  focal: "the terrace's end at 21 against the short four unit bar above it"

art:
  technique: "TXBENCH.relief of the same machined rule, at one scale across the frame"
  why_this_technique: "the range only reads as a range when both ends share one scale"
  palette: "worn steel, frosted glass, black anodised plate"
  value_structure: >
    Lightest are the bars' top faces. Darkest is the bench. Frame median L* planned at 4.

type:
  hook: "21 times, the high end"
  dek: "Set at one scale, the range runs four to 21. It is the researchers' own benchmark against existing approaches."
  labels: ["existing approaches", "4", "21"]

verbatim: []

acceptance:
  - "the terrace is exactly 21 times the frosted bar's length and the steel bar four times it, and a frame without the three tracks fails this item"
  - "the rule spans at least 850 px of the frame's width"
  - "21 engraved unit grooves are countable at full size"
  - "the frame's median L* at 432px is 12 or lower"

risks:
  - "a long thin rule can read as a chart bar on black, so the plate carries a machined edge and a long cast"
```

```yaml
slide: 6
layout: DIAGRAM
primary_image:
  subject: "the cover's camera on a nest with no coat, its outer cells studded for antigen presentation, ember T cells pressed into its margin and three threaded between its cells, a raised ring around one group of neighboring cells"
  rect: [0, 580, 1080, 770]
  bleeds: [left, right, bottom]
accent: "#B4664F"
job: >
  Show what draws T cells in, the cells next door and the protein fragments they display, and that SPACER reads cells in groups.

claims: [c3, c5, c6]
numerals: []

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The cover's scale and light on a different nest. No coat. The nest's outer row of cells carries fine raised studs,
    and the T cells stand right against those cells. A low kerb rings one group of neighboring cells with a T cell
    inside the group, labelled in DOM.
  bands: >
    Top third, dark glass with the type. Middle third, the section edge and the T cells crowding the nest's margin.
    Bottom third, the nest's studded cells in relief, lit on their upper left shoulders, and the ringed neighborhood casting its kerb shadow.
  focal: "the ringed group of neighboring cells with a T cell inside it"

art:
  technique: "TXBENCH.relief with Voronoi cells, raised studs and bead cells, a DOM leader to the ringed group"
  why_this_technique: "the cover's camera with one thing removed makes the coat's absence the whole difference"
  palette: "dark plum stroma, oxblood tumor, steel studs, ember T cells"
  value_structure: >
    Lightest are the T cells' lit shoulders and the studs. Darkest is the bare glass and the stroma's lacunae. Frame median L* planned at 8.

type:
  hook: "Immune cells seem to answer signals close by"
  dek: "SPACER reads groups of neighboring cells. Tumors expressing antigen presentation genes were more likely to attract T cells. Those genes help cells show protein fragments to immune cells. Drawn to illustrate."
  labels: ["a group of neighboring cells"]

verbatim: []

acceptance:
  - "ember T cells stand against the nest's studded outer cells and at least three sit between its cells, and a frame without the nest fails this item"
  - "the tumor nest is at least 600 px across at full size and the ringed group of neighboring cells at least 200 px across"
  - "no glossy coat is drawn on this frame"
  - "the frame's median L* at 432px is 16 or lower"

risks:
  - "studs can read as noise at 432px, so they sit on the lit outer row only"
```

```yaml
slide: 7
layout: FULL_BLEED
primary_image:
  subject: "the mucin wall at macro crossing the frame on a diagonal, its glazed crest catching the key, ember T cells banked on its outer slope, its cast falling over the tumor cells below"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#B4664F"
job: >
  Turn the deck to the finding, a sugar coat that may form a physical barrier and keep T cells away.

claims: [c7]
numerals: []

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The wall runs from the lower left up to the right, the tallest thing in the deck. Above and left of it, ember T
    cells are banked on the stroma, thickest at the wall's foot. Below and right, the tumor's cells lie in the wall's
    cast. None of the T cells is past the crest.
  bands: >
    Top third, dark glass with the type. Middle third, the T cells banked on the stroma. Bottom third, the wall's
    glazed crest and the tumor cells in its shadow.
  focal: "the wall's glazed crest, the brightest line in the deck, with the T cells against its foot"

art:
  technique: "TXBENCH.relief with a glazed ridge, bead cells and Voronoi cells, a long cast"
  why_this_technique: "a barrier is a height, and a height under a low key is a bright edge and a long shadow"
  palette: "pale cool mucin glaze, ember T cells, dark plum stroma, oxblood tumor"
  value_structure: >
    Lightest is the wall's crest. Darkest is the cast over the tumor and the stroma's lacunae. Frame median L* planned at 9.

type:
  hook: "A sugar coat that may be a wall"
  dek: "Mucins are large sugar coated proteins many cancers make. The researchers found evidence mucins may help form physical barriers that keep T cells away from tumors. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the glazed wall crosses the whole frame and every ember T cell sits on its outer side, and a frame without the wall fails this item"
  - "the wall is at least 90 px wide at full size and its crest reads as a bright line at 432px"
  - "the wall's cast darkens the tumor cells along its lower side"
  - "the frame's median L* at 432px is 16 or lower"

risks:
  - "the glaze can read as icing or a crater rim, so its surface carries fine ripples and its crest one specular line"
```

```yaml
slide: 8
layout: SPLIT_HORIZON
primary_image:
  subject: "four round tissue cores on one bevelled glass array slide in two rows, melanoma and gastric, the left core of each row with low mucin and T cells inside, the right core ringed by a tall glaze with T cells held outside"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#B4664F"
job: >
  Show the association the release reports, more mucin with poorer response to checkpoint inhibitors in melanoma and gastric datasets, and say what those drugs do.

claims: [c8, c21, c23]
numerals: []

data_in_art:
  figure: cancer_types_mucin
  drives: row count, one row of cores per cancer type the mucin claim names

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The image takes the lower 60 percent and the type the dark top. Two rows of two cores, each row labelled in DOM.
    In each row the left core has a low rim with ember T cells inside it and the right core a tall glazed rim with the
    T cells outside it, so rim height is the only thing that changes across a row.
  bands: >
    Top third, dark glass with the type. Middle third, the melanoma row. Bottom third, the gastric row, two cores in relief with lit rims and cast shadows on the black glass.
  focal: "the right column's tall glazed rims with the T cells stopped outside them"

art:
  technique: "TXBENCH.relief small multiples, four cores at one scale"
  why_this_technique: "an association is two states side by side, and one variable stepped from low to high reads at a glance"
  palette: "black glass, dark plum stroma, oxblood tumor, pale mucin glaze, ember T cells"
  value_structure: >
    Lightest are the tall rims' crests. Darkest is the glass between the cores. Frame median L* planned at 6.

type:
  hook: "More mucin went with poorer response"
  dek: "In several melanoma and gastric cancer datasets, more mucin went with poorer responses to checkpoint inhibitors, drugs that help T cells kill cancer cells better. An association in existing data. Drawn to illustrate."
  labels: ["melanoma", "gastric", "lower mucin", "higher mucin"]

verbatim: []

acceptance:
  - "four cores stand in two rows, the left of each row with T cells inside and the right ringed by a tall rim with T cells outside, and a frame without the four cores fails this item"
  - "each core is at least 300 px across at full size and the cores come apart at 432px"
  - "the two rows carry the labels melanoma and gastric"
  - "the frame's median L* at 432px is 14 or lower"

risks:
  - "the rows can read as measured data, so the dek says association and the cores are drawn to illustrate"
```

```yaml
slide: 9
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "the whole glass slide held by two spring clips on a black anodised microscope stage, its section lit from the aperture beneath, five engraved lines on its frosted label end"
  rect: [0, 470, 1080, 880]
  bleeds: [left, right, bottom]
accent: none
job: >
  Close on the consequence, a finding to test in the lab and a possible diagnostic tool with no use reported, and name the Texas fund among the funders.

claims: [c7, c9, c10, c12]
numerals:
  - computed_by: "out/2026-10-17/compute.py funders, the funders c12 names, counted"

data_in_art:
  figure: funders
  drives: engraved line count on the slide's frosted label, one line per funder the release names

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The black stage plate fills the lower two thirds and bleeds three edges. The slide lies across it under two spring
    clips, its section over the round aperture, where light from below rims the tissue. The frosted label end at left
    carries five engraved lines, one named by a leader. The type sits on the dark plate above.
  bands: >
    Top third, dark stage plate with the type. Middle third, the slide, the clips and the lit aperture. Bottom third, the black bore of the aperture below the slide and the stage plate's lit machined front edge, with the dark bench below it.
  focal: "the darkfield ring of the aperture and the lit rim of the section"

art:
  technique: "TXBENCH.relief of a machined stage, clips and a glass slide over an aperture"
  why_this_technique: "the finding goes back under a lens, and a stage holding the slide says that without a person or a clinic"
  palette: "black anodised stage, spring steel clips, black glass, frosted label, the section in plum and oxblood lit from below"
  value_structure: >
    Lightest is the aperture's light and the frosted label. Darkest is the plate's cast and the bench. Frame median L* planned at 6.

type:
  hook: "New ideas to test in the lab"
  dek: "The researchers believe SPACER could potentially become a diagnostic tool for cancer therapies. The release reports no such use. The Cancer Prevention and Research Institute of Texas is one of five funders the release names. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the slide lies on the stage under two clips with its section over the lit aperture, and a frame without the slide fails this item"
  - "the black anodised stage plate is at least 1000 px wide at full size and the slide on it at least 800 px long"
  - "five engraved lines cross the frosted label end and a leader names the Texas fund on one of them"
  - "the frame's median L* at 432px is 14 or lower"

risks:
  - "a stage seen from above can read as a plain plate, so the clips and the aperture's light carry it"
```
