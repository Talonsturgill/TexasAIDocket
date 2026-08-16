# Storyboard, Carousel No. 1 — August 16th, 2026

## The story, and why this one

`tx-2026-0071`. On August 6th, 2026 the Governor announced SpaceX will build Terafab, a
vertically integrated semiconductor plant, in Grimes County. The state extended a Texas
Enterprise Fund grant of $30 million and the project is qualified under JETI. The company says
the plant is for producing AI chips at scale.

**Not the others.** The Abbott audit directive (`tx-2026-0072`) is the biggest policy story of
the fortnight and the docket on this same site already publishes it. `knowledge/shared/APPLICATIONS.md`
is explicit that the deck must not narrate the record back, and that the application layer goes
first. The Atlas and Kodiak driverless sand fleet is the best pure application story the scouts
found and it is not a decision the record holds, so Phase 8 rules it out. Terafab is both. It is
on the record as of this run and it is the manufacturing end of the application layer, which is
the loop APPLICATIONS.md says nobody draws.

**The through-line.** Texas has spent two years arguing about what plugs into its grid. Three
days before this announcement the state stopped 474 gigawatts of that queue pending an audit.
Then it paid toward a plant that is reported to be building its own generation and not joining
the queue at all. The deck ends somewhere a reader did not expect to be.

## The directors room, and what was grafted

Two lenses returned, scale and the loop. A third, the signed record, did not return before the
art phase and the deck went ahead without it, which is noted here rather than glossed.

**The spine is the showrunner's**, because neither treatment had claim c24 and c24 is the turn.
The plant is reported to be building its own gas fired generation rather than joining the queue
the state froze three days before the announcement. A deck that ends on that is a deck that
surprises a reader who has followed this story for two years.

**Grafted from the scale lens**, which was the stronger cartographer.

- The extruded county rather than a flat spotlight for slide 1. It makes the county an object
  and the roof a thing lying on it, which is the difference between a symbol on a map and a
  measurement.
- **The corner tag, "SCALE FIGURE. SITE PLAN NOT PUBLIC.", on every slide that draws the
  square.** This is the best single idea either room produced. The square is not a site plan and
  a frame screenshotted without that line can be read as a rendering of a building.
- Its refusal to convert 100 million square feet into acres, because a reader takes an acreage
  for a site size and no acreage is published. `compute.py` does not emit acres.

**Grafted from the loop lens**, which was the stronger disciplinarian.

- **No arrowheads and no causal verb anywhere.** Nothing in the record says these chips will run
  in Texas data centers. The company says they are for use on Earth and in space. The honest
  claim is that one state sits at both ends of one chain, and an arrowhead is a direction of
  flow that the record can't carry.
- **The queue is drawn as one hundred paths, one per percent, never one per gigawatt.** Ninety
  percent of 474 gigawatts is the product of two approximations and this deck does not publish
  it.
- The two grid figures never share a scale, and the frame says so in its own words.
- The norther front lands at 0.382 rather than the vertical center, and every contact shadow
  gets a lit ground to subtract from rather than a near black one.

`dedupe_check` clean, 0 entries in the ledger. `instincts.py --top 5` printed nothing, so the
room was handed nothing, which is correct on run one rather than a gap.

## Palette, drawn from Grimes County

Post Oak Savannah, not Permian and not Hill Country. Every accent is a material in that county.

| token | hex | the material |
|---|---|---|
| `night` | `#08060F` | the fixed base register, Big Bend at dusk |
| `deep` | `#0F0C1C` | same ladder |
| `panel` | `#191530` | same ladder |
| `line` | `#2B2447` | same ladder |
| `oak` | `#4A5236` | post oak and blackjack oak canopy in late summer |
| `bluestem` | `#C9A063` | little bluestem cured tawny by August |
| `loam` | `#A85433` | the iron red sandy loam where a county road is cut down into it |
| `bottom` | `#6B6448` | Navasota River bottomland silt |
| `granite` | `#9A3B2A` | the Capitol's own sunset granite, the accent on the paper frame |
| `sand` | `#D8C9AB` | the pale leached quartz horizon over the loam |
| `caliche` | `#E4D8C3` | type on dark, the house token |
| `paper` | `#F6F1E4` | the document register, slides 6 and 8 only |

**Value structure across the deck.** Slides 1 to 5 sit on the dark ladder with the tawny
bluestem carrying every figure. Slides 6 and 8 invert to `paper`, because they are documents
rather than land, and that inversion is the deck's rhythm rather than decoration. Slide 7 is the
darkest frame in the deck and slide 9 returns to `deep`. The lightest single element anywhere is
the roof plane on slide 1.

**The reserved red is not used.** No comment window on this story closes in a period a reader can
act on, so `--flag-red` stays unspent. The one dated way in, the August 19th hearing, is set in
`bluestem` on slide 9 and not in red.

---

```yaml
slide: 1
job: >
  Make the size land before any word does, by putting the plant's own stated floor area on the
  county it is going into, at true scale, and saying how far across that is.
claims: [c5, c1]
numerals:
  - computed_by: "out/2026-08-16/compute.py footprint_square_side_mi, isqrt(100000000) / 5280"
  - value_from: c5
composition:
  structure: >
    The county polygon is drawn large and low, filling the middle and lower half, and the roof
    square is laid on it at the same projected scale so the two are directly comparable without
    a caption explaining the comparison. The hook sits above the county in the top band because
    the reader has to read the number before the shape resolves, not after.
  bands: >
    The TOP third carries the kicker and the hook over a graded night sky with the dusk haze
    thinning upward. The MIDDLE third is the Grimes County polygon in oak green with the true
    scale roof square burning inside it in bluestem, and a leader from the square to its own
    dimension label. The BOTTOM third carries the county under a lit ground wash, the hachured
    Navasota bottom running out of frame to the west, a measured scale bar in tick marks, and
    the coordinates footer, so the eye lands on terrain with modeled tone rather than on a rule.
  focal: >
    The bluestem square, because it is the only saturated warm shape on a cold dark frame and it
    sits at the optical center of the county mass.
art:
  technique: "Extruded county, with a true-scale roof plate on its lit top face"
  why_this_technique: >
    The claim is cartographic and about size in a place, so it wants cartography at honest scale.
    A bar chart of square feet is a quantity floating in nowhere. Extruding the county makes it
    an OBJECT, so the roof reads as a thing lying on a thing rather than as a symbol printed on a
    region. TXGeo projects the county through the same Albers conic the website uses, so the
    square and the outline are measured against each other rather than illustrated.
  palette: "oak for the county mass, bluestem for the roof square, loam for the leader and ticks, caliche type"
  value_structure: >
    Darkest is the sky above the county. Lightest is the roof square, which is the subject. The
    county sits between the two so the square reads as something placed on it rather than part
    of it.
  motion: "Down from the hook, into the square, out along the leader to the dimension, then along the scale bar"
type:
  hook: "One roof. 1.89 miles across."
  dek: "Grimes County, August 6th"
  labels: ["10,000 FT A SIDE", "THE ROOF, AT TRUE SCALE", "GRIMES COUNTY", "5 MILES", "SCALE FIGURE.", "SITE PLAN NOT PUBLIC."]
acceptance:
  - "the roof square and the county outline are drawn through the same projection, so a reader measuring them against the scale bar gets the same answer twice"
  - "the figure 1.89 is legible at 432px against the oak county mass"
  - "the leader from the square terminates on the square's own edge within 24 design px, declared through window.__txLeaders"
  - "the bottom third carries the lit ground wash and the scale bar, and is not a bare strip under the map"
  - "no numeral on this slide is absent from claims.json or from compute.py"
  - "the corner tag reads SCALE FIGURE. SITE PLAN NOT PUBLIC. so the square can never be mistaken for a site plan"
  - "the extrusion depth is small enough that the county silhouette is still readable at 432px, since the outline is the only reason the county is drawn"
risks:
  - "A county polygon at this zoom can read as an abstract blob rather than a place. The leader label and the coordinates footer are what name it, and if they fail the slide is a shape."
  - "The square is 0.46 percent of the county's land area. Drawn honestly it is small, and the temptation will be to cheat it larger. It stays true scale and the dimension label carries the weight."
```

```yaml
slide: 2
job: >
  Put the county on the state so a reader who has never heard of Grimes knows within one beat
  whether this is near them.
claims: [c1]
numerals:
  - value_from: c1
composition:
  structure: >
    The full state silhouette is fitted small and high so the whole of Texas is visible at once,
    with one county lifted in value, because the question this slide answers is where in Texas
    and that question needs the whole state in frame rather than a crop of it.
  bands: >
    The TOP third carries the state outline with the counties mesh drawn once as a single path
    and Grimes lifted in bluestem. The MIDDLE third carries a leader line out of the dense east
    to a knockout label, and the two nearest cities a reader will actually know, set as ticked
    anchors. The BOTTOM third carries a caliche haze wash rising off the horizon line with the
    Navasota drawn as a contoured river trace through modeled texture, plus the counter and the
    coordinates footer sitting on that graded ground.
  focal: "The single lifted county, because everything else on the frame is one value"
art:
  technique: "Single-county spotlight with a leader out of the dense east"
  why_this_technique: >
    The technique library warns that a spotlight fails when the county is small and east, where
    254 counties are dense, and Grimes is exactly that county. The recorded fix is a leader line
    to a label outside the mesh, so the technique is chosen with its own failure mode already
    answered in the plan.
  palette: "line for the county mesh, oak for the state fill, bluestem for Grimes, caliche for the label"
  value_structure: >
    Darkest is the ground below the state. The state sits one step up in oak. The lifted county
    is the lightest thing on the frame and it is the only place any saturation appears.
  motion: "Across the state left to right, catching on the lifted county, then out along the leader"
type:
  hook: "Between Houston and Bryan."
  dek: "Post Oak Savannah, sandy loam over iron red clay. The Navasota River runs the western line."
  labels: ["GRIMES COUNTY", "787.467", "SQ MI OF LAND", "HOUSTON", "COLLEGE STATION AND BRYAN"]
acceptance:
  - "the state is drawn through TXGeo and is neither mirrored nor inverted, checkable by finding El Paso on the left and Beaumont on the right"
  - "the leader terminates on the Grimes polygon's own coordinates within 24 design px, declared through window.__txLeaders"
  - "the county borders are drawn as one mesh path so no shared edge is stroked twice into a doubled line"
  - "the 787 figure traces to c27 and appears nowhere else on this slide"
  - "the lifted county is distinguishable from its neighbours at 432px, declared through data-encodes with reads differ"
risks:
  - "At full-state fit Grimes is about a fingernail. If the value lift is too subtle it disappears at feed size, which is why the separation is declared and measured rather than judged."
```

```yaml
slide: 3
job: >
  Show what vertically integrated actually means here, which is three manufacturing stages that
  are normally three separate buildings in three separate countries, stacked into one.
claims: [c6, c5]
numerals:
  - value_from: c5
composition:
  structure: >
    Three horizontal planes in receding perspective, one per named stage, converging under a
    single roofline drawn as one continuous plane across all three, because the claim is that
    separate things became one thing and the frame has to perform that rather than list it.
  bands: >
    The TOP third carries the roof plane as one unbroken surface with a raking light across it
    and the hook knocked into the dark above it. The MIDDLE third carries the three stage planes
    in parallax, each at its own value, each labelled from the quote. The BOTTOM third carries
    the foundation slab in loam with a two-part contact shadow under it and a dust haze at the
    slab's edge, so the whole stack is sitting on modeled ground rather than floating.
  focal: "The single roof plane, because it is the widest continuous shape and the one the claim is about"
art:
  technique: "Parallax planes, with a TXCARVE two-part contact shadow"
  why_this_technique: >
    The technique library says to reach for parallax planes before a full 3D scene, and this
    claim needs exactly what they do, which is separate layers at separate depths reading as one
    object. A zdog scene would draw a building. The claim is not about a building's shape, it is
    about three things becoming one.
  palette: "panel and line for the receding planes, loam for the slab, bluestem for the raking light on the roof"
  value_structure: >
    The roof plane is lightest because it is the thing the sentence is about. Each stage plane
    steps darker as it recedes. The slab is darkest and carries the contact shadow.
  motion: "Up the stack from the slab, plane by plane, arriving at the roof"
type:
  hook: "Logic. Memory. Packaging."
  dek: "These stages normally sit in separate plants, often on separate continents. The company says all three go under one roof."
  labels: ["ONE ROOF", "ADVANCED PACKAGING", "MEMORY", "LOGIC"]
acceptance:
  - "the three stage labels are the three words the quote at c6 uses and no others"
  - "the contact shadow under the slab is declared through data-contacts and separates from its ground by more than 4.0 L* at 432px"
  - "the roof plane reads as one continuous surface rather than three roofs, checkable by whether any vertical break crosses it"
  - "each of the three planes is a different value, so the frame is depth and not a collage"
risks:
  - "Three stacked planes with labels is one keystroke away from a SaaS diagram. The raking light and the contact shadow are what keep it a made object, and if the light direction disagrees with the value structure the whole frame flattens."
```

```yaml
slide: 4
job: >
  Give the company's own stated purpose one uninterrupted frame, in its own words, because the
  reason a chip plant is an AI story is a sentence somebody said rather than an inference.
claims: [c7]
numerals: []
composition:
  structure: >
    A full-bleed engraved field with the quotation set as the only structure in the frame,
    because a quotation is the one kind of content that loses by being illustrated, and the
    slide's job is to let the sentence be the object.
  bands: >
    The TOP third carries the attribution line and a white-line intaglio field thinning upward.
    The MIDDLE third carries the quotation itself, set large, with the operative clause in
    bluestem and the rest in caliche. The BOTTOM third carries the engraving at its densest,
    the burin lines crowding into a graded mass toward the lower edge with the counter and the
    coordinates footer knocked out of that texture.
  focal: "The clause about AI chips at scale, because it is the only coloured text in the deck's darkest type block"
art:
  technique: "Engraving, TXENGRAVE white-line intaglio"
  why_this_technique: >
    The library names engraving as the register for a statute or a filing, and this is a
    quotation out of a state press release, which is the same register. It also says to engrave
    the ground and not the message, which is why the burin field thins where the type sits and
    crowds where it does not.
  palette: "night ground, caliche burin lines, bluestem on the operative clause"
  value_structure: >
    Darkest is the untouched ground at the top. The engraved mass at the bottom is the lightest
    area by density rather than by hue. The type sits in the calm band between them.
  motion: "Straight down the quotation, with the coloured clause arresting the eye halfway"
type:
  hook: "\"AI chips at scale\""
  dek: "The company's own words, in the state's own release"
  labels: ["ELON MUSK, IN THE GOVERNOR'S RELEASE, AUGUST 6TH"]
acceptance:
  - "the quotation on the slide matches c7 word for word, including the phrase on Earth and in space"
  - "the burin field density drops where the type sits, so no engraved line crosses a letterform"
  - "the attribution names both the speaker and the document, not just the speaker"
  - "the bottom third carries the densest engraved mass and not a rule with a caption on it"
risks:
  - "An engraved field at high density moires on the 432px thumb. Line spacing stays above 3px at 2x and the thumb is checked before this slide is signed off."
```

```yaml
slide: 5
job: >
  Set what the company is putting in beside what the state is putting in, and let the two
  figures be the argument without a word of framing.
claims: [c2, c3]
numerals:
  - value_from: c2
  - value_from: c3
  - computed_by: "out/2026-08-16/compute.py tef_share_of_phase_one_pct, 100 * 30000000 / 16800000000"
composition:
  structure: >
    Two columns of unequal mass on a common baseline, sized to the two figures at true ratio,
    because the entire point is that one is 0.18 percent of the other and any framing that made
    them comparable in size would be a lie told with true numbers.
  bands: >
    The TOP third carries the two column headers and the hook over a norther front value break,
    the cold side above. The MIDDLE third carries the two masses, the company's rising past the
    frame edge and the state's a thin band near the baseline, each with its figure in tabular
    mono. The BOTTOM third carries the baseline itself as a lit stone ledge with a hachured
    thickness and its own cast shadow, and the share figure sits on that ledge.
  focal: "The gap between the top of the small mass and the top of the frame, which is where the ratio actually lives"
art:
  technique: "The residual bar, one hue at one intensity"
  why_this_technique: >
    The grid watch's rule is that a bar carries the whole message in its length and wears no
    severity ramp, and it holds here for the same reason. These two figures are not good news or
    bad news, they are two sizes, and a gradient or a second hue would be a verdict this slide
    does not get to publish.
  palette: "bluestem for both masses at one intensity, loam for the ledge, caliche type"
  value_structure: >
    Both masses are the same value, which is the point. The ground behind them is darkest at the
    top and lifts toward the ledge, so the small mass is not lost against it.
  motion: "Left to right across the two masses, then down to the ledge where the share is stated"
type:
  hook: "$16.8 billion. $30 million."
  dek: "What the company says it will spend in the first phase, and what the state put in."
  labels: ["FIRST PHASE CAPITAL", "TEXAS ENTERPRISE FUND", "GRANT", "0.18 PERCENT OF THE FIRST PHASE", "SAME HUE, SAME SCALE. THE SHORT ONE IS NOT FLOORED."]
acceptance:
  - "the two masses are drawn at true ratio to the two figures, so the small one is 0.18 percent of the tall one and is not floored to a visible minimum"
  - "both masses are the same hue at the same intensity, with no gradient and no second colour"
  - "the 0.18 figure re-derives from c2 and c3 through compute.py tef_share_of_phase_one_pct, which ships beside the deck, and no figure on this slide is typed"
  - "the bottom third carries the modeled stone ledge with its own cast shadow rather than a hairline"
  - "neither figure is described as large, small, generous or cheap anywhere on the slide"
risks:
  - "A 0.18 percent bar is about two pixels tall at any honest scale, and a reader may read it as an axis line rather than a value. The label sits on it directly and the acceptance list forbids inflating it."
```

```yaml
slide: 6
job: >
  Name the four bodies that actually signed something, because a state announcement is one
  sentence and a school board vote is a room full of people in a county of eight hundred square
  miles.
claims: [c9, c10, c11, c12, c4]
numerals: []
composition:
  structure: >
    An inverted paper register, four ruled entries down the frame, each carrying a body and the
    sentence that body said, because the content is documentary and the deck has been dark for
    five slides, so the change of ground is the rhythm as much as the register.
  bands: >
    The TOP third carries the register head and the hook in capitol granite on paper, with a
    stipple-textured paper grain across the whole ground. The MIDDLE third carries the four
    entries with a paper_rule hairline between each and the quoted fragments set in Manrope. The
    BOTTOM third carries a deckle edge in graded stipple where the paper falls into shadow, with
    the counter and the coordinates footer sitting in that shaded texture.
  focal: "The Iola entry, because it is the only one of the four that names a vote"
art:
  technique: "Stipple field on the paper register, density carrying the paper's own tooth"
  why_this_technique: >
    The library says a stipple field reads as engraving and fails when it greys out into a wash.
    Here it is deliberately low density and is doing the job of a paper stock rather than
    carrying a quantity, which is the honest use of it. A dark treatment of this content would
    have made four quotations look like an indictment.
  palette: "paper ground, capitol_granite for the head, night for the body type, paper_rule hairlines"
  value_structure: >
    This is the lightest slide in the deck by a wide margin. The darkest thing on it is the body
    type. The deckle shadow at the bottom is the only mass.
  motion: "Straight down the register, entry by entry"
type:
  hook: "Four signatures, on the record."
  dek: "A governor, a county judge and two school boards"
  labels: ["OFFICE OF THE TEXAS GOVERNOR", "GRIMES COUNTY, ITS COUNTY JUDGE", "IOLA ISD, ITS BOARD OF TRUSTEES", "ANDERSON-SHIRO CISD"]
acceptance:
  - "each of the four entries carries the body's name and a fragment from its own claim, and no entry carries a sentence nobody said"
  - "the county executive is called a county judge in the label and is not described as a judge in any sentence, per the Texas language rule"
  - "the stipple density stays low enough that the paper reads as tooth and not as a grey wash"
  - "the bottom third carries the graded deckle shadow and not a bare paper edge"
risks:
  - "A light slide inside a dark deck is a deliberate high-variance move and it can read as a different deck. The wordmark, the star and the counter hold the constellation across the inversion, and if they do not the slide is an intruder."
```

```yaml
slide: 7
job: >
  Turn the deck, by putting this plant next to the queue the state just froze and showing that
  it is reported to be building its own power instead of joining it.
claims: [c13, c14, c15, c24]
numerals:
  - value_from: c13
  - value_from: c14
composition:
  structure: >
    A single dense mass of queued requests filling most of the frame with a hard stop bar across
    it, and one small separate object standing outside the mass entirely, because the claim is
    about being outside a thing and the frame has to show an outside for that to mean anything.
  bands: >
    The TOP third carries the hook and the queue figure with its date and its source named, over
    the coldest part of a norther front. The MIDDLE third carries the queue as a stipple field
    of many small units at high density, cut by the stop bar dated August 3rd. The BOTTOM third
    carries the plant as one lit mass on its own ground outside the field, with a heat shimmer
    off its own generation and a cast shadow anchoring it, so the bottom band holds the turn.
  focal: "The single lit object below the stop bar, because it is the only thing in the frame that is not in the field"
art:
  technique: "Arrested flow field, one hundred paths, with a hard norther front value break as the stop"
  why_this_technique: >
    An interconnection queue is transmission that has not moved, so a flow field stopped dead
    against a rule is the claim itself. The paths are ONE PER PERCENT and never one per gigawatt,
    because ninety percent of 474 gigawatts is the product of two approximations and publishing
    it would manufacture a precision neither source has. A bar chart would invite the reader to
    measure this plant against the queue, and the two figures come from different bodies seven
    weeks apart.
  palette: "line and panel for the queue field, loam and bluestem for the lit plant, caliche type"
  value_structure: >
    The queue field is a single mid value across a large area, deliberately monotonous. The stop
    bar is the hardest edge in the deck. The plant below it is the only lit thing.
  motion: "Down through the queue field, arrested at the stop bar, released onto the lit object"
type:
  hook: "The plant is not in the queue."
  dek: "The state froze 474 gigawatts of connection requests on August 3rd"
  labels: ["APPROXIMATELY 474 GIGAWATTS, GOVERNOR'S LETTER, AUGUST 3RD", "APPROXIMATELY 90 PERCENT DATA CENTERS", "TERAFAB, REPORTED TO BE BUILDING ITS OWN GENERATION", "SCALE FIGURE. SITE PLAN NOT PUBLIC."]
acceptance:
  - "the 474 figure carries the Governor's letter and the August 3rd date on the slide itself, and is never set beside ERCOT's separate 438,000 MW figure"
  - "the own-generation label says reported, because c24 is journalism and not the state's own document"
  - "the queue field and the lit plant separate by more than 4.0 dE at 432px, declared through data-encodes with reads differ"
  - "the plant's cast shadow is declared through data-contacts and separates from its ground by more than 4.0 L*"
  - "the stop bar sits at 0.382 of the frame height and not on the vertical center, per the norther front failure mode"
  - "exactly one hundred paths are drawn, one per percent, and no path count is derived from a gigawatt figure"
  - "no arrowhead appears anywhere and no label uses a verb of flow, because nothing in the record says these chips run in Texas data centers"
  - "path lengths vary across a seeded range, since uniform path length reads as hair"
risks:
  - "This is the slide that could read as a claim that the plant dodged the audit. It did not, and nothing here says it did. The labels state the queue and state the plant's reported power plan, and any sentence connecting them causally is cut."
```

```yaml
slide: 8
job: >
  Make the gap physical at the scale of the place, by drawing the one thing about this site that
  has been surveyed for a century and leaving the frame above it as an empty, ruled, labelled
  field.
claims: [c26, c5, c30]
numerals: []
composition:
  structure: >
    A section through Grimes County ground, with the ground line sitting well below the vertical
    center so the drawn half and the undrawn half are visibly unequal, because the claim is that
    far more is known about the dirt than about what is going on it and an even split would say
    the opposite.
  bands: >
    The TOP third is the emptiest field in the deck, night with grain and a faint graticule, and
    one measured plate naming what is not published. The MIDDLE third carries the heavy ground
    line and the first soil horizon, pale leached quartz sand hachured fine and near vertical.
    The BOTTOM third carries the iron red sandy loam hachured heavy and raking to the frame edge,
    with a lit cut face along the left, iron mottling picked out as specular points at the top of
    the value range, and a depth scale ticked down the right.
  focal: >
    The ground line, because it is the heaviest single rule in the deck and it is the boundary
    the whole slide is about.
art:
  technique: "Hachure field over layered soil horizons, with a wind-worked carve on the lit cut face"
  why_this_technique: >
    The library says a hachure field fails when its slope source is flat, and a layered soil
    section is the least flat source available. More to the point, the only thing about this site
    that can honestly be drawn is the dirt, because the dirt has been mapped for a century and
    the plant has not been published. Drawing a building outline here would invent the exact
    thing the slide says nobody has seen.
  palette: "sand for the leached quartz horizon, loam for the iron red beneath it, oak for the taproots, night above the line"
  value_structure: >
    The lightest thing in the whole deck is the lit cut face of the loam. The darkest is the
    empty field directly above it on the same frame. Every landscape a reader has seen is the
    other way round, and the eye catches that before the brain does.
  motion: "Down from the plate into the ground line, then along the horizons into the lit cut"
type:
  hook: "The soil is mapped. The site is not."
  dek: "Checked August 16th"
  labels: ["NO ACREAGE PUBLISHED", "NO SITE PLAN PUBLISHED", "NOT YET ON THE STATE'S JETI AGREEMENTS TABLE", "SANDY LOAM SURFACE LAYER", "MOTTLED RED CLAYPAN SUBSOIL", "TEXAS ALMANAC, SOILS OF TEXAS"]
acceptance:
  - "no building outline, envelope, massing or footprint is drawn anywhere above the ground line"
  - "the empty upper field is bounded by the ground line, carries grain and a graticule, and is never a bare canvas that the near-uniform gate would read as a dead frame"
  - "the JETI line says not yet and says checked August 16th, because the page carries no last updated date and ordinary filing lag is the likeliest reason"
  - "the ground line is stroked heavier than any other rule in the deck, and it sits far enough below the vertical center that the undrawn field is visibly the larger half"
  - "the hachure stroke length varies across the horizons, since a uniform field reads as a texture swatch"
  - "the reported water lines are absent from this slide, because a section through soil is not evidence about a water right"
risks:
  - "An empty field at 432px is indistinguishable from a slide that failed to render. Nothing in that field is unbounded, unlabelled or unmeasured, and the test is whether a stranger shown the thumb can say what is missing."
  - "This slide is one adjective from an accusation. It states what a page did and did not carry on one date. Nothing here says anybody failed to file."
```

```yaml
slide: 9
job: >
  Hand the reader the two dated things they can still do something with, and close the deck on
  the record rather than on a summary.
claims: [c28]
numerals: []
composition:
  structure: >
    A return to the deck's own dusk register at a wide camera, with the county now small and the state
    around it, so the deck visibly comes back to where it started and the closing information
    sits in the space the roof square used to occupy.
  bands: >
    The TOP third carries the star, the wordmark and a dust column rising off the horizon behind
    them. The MIDDLE third carries the two dated lines, the August 19th hearing and the record's
    own address, in bluestem on the dark. The BOTTOM third carries the Big Bend dusk field at its
    warmest, the horizon band graded down into the frame edge with grain over it, the counter, the
    site line and the coordinates footer sitting on that atmosphere.
  focal: "The August 19th line, because it is the only thing on the deck a reader can act on"
art:
  technique: "Big Bend dusk field with a dust column, and grain over everything"
  why_this_technique: >
    The house atmosphere is the right close because a close is the one place the deck should look
    like itself rather than like this story. The dust column is for something arriving, and what
    is arriving is a hearing three days out.
  palette: "night to deep to a dusk_ember horizon, bluestem on the dated lines, caliche on the wordmark"
  value_structure: >
    Darkest at the very top behind the star. The warm horizon band is the lightest area and it
    sits low, so the frame reads as a close rather than an opening.
  motion: "Down from the mark, through the two dated lines, resting on the horizon"
type:
  hook: "One date, still ahead of you."
  dek: "EVERY FACT TRACES TO A SOURCE, set as the closing footer"
  labels: ["AUGUST 19TH, 2026", "texasaidocket.com", "09 / 09"]
acceptance:
  - "the hearing date on this slide is the date the record carries at tx-2026-0073, traced to claim c28, and exactly ONE date appears so the actionable thing is unmistakable"
  - "the horizon band does not reach the left or right frame edge, per the Big Bend dusk field failure mode"
  - "the wordmark, the star, the counter and the site line are all present and the site line is the smallest type on the slide"
  - "the bottom third carries the graded dusk atmosphere with grain over it and not a flat strip"
  - "only one dust column is drawn, because one is weather and two is a pattern"
risks:
  - "A close slide is where a deck reaches for a summary. There is no summary here, only two dated things and the mark. If a sentence of recap appears it should be cut."
```
