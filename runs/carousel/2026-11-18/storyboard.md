# Carousel, November 18th, 2026: Texas read from orbit, and where a satellite reading stops

## The story, and what the fact check did to it

A UT Dallas team studied all 254 Texas counties (c1, c24). It paired public CDC cancer prevalence data with satellite readings of eight air pollutants from 2022 (c2, c4), from Sentinel-5 Precursor and the Copernicus Atmosphere Monitoring Service (c23), and applied machine learning (c3). Four algorithms were compared (c20) and a support vector machine fit best, R squared 0.791 (c21). Counties with more pollution tended to have more cancer (c5) and sulfur dioxide was the most influential environmental predictor (c6, c26). The air falls into three major clusters (c7), the east worse, the west better and the centre between (c8). High cancer counties sit near other high cancer counties (c9), Moran's index 0.69 (c22). Ground monitors are costly, which limited earlier spatial work (c13), and the paper says satellite data can help where ground monitoring is unavailable (c25). Not every more polluted place had more cancer (c10), cancer reflects many influences (c19), and the results are not evidence that pollution causes cancer in any one person (c11, c12 on precision). Rahman says the method can show where medical centers are and where government should focus (c14). The team wants more research on cost and accuracy (c18). Published online March 5th in Environmental Monitoring and Assessment (c11).

The fact check narrowed c7 to the three clusters (east and west are c8), dropped a claim that liquor consumption led all predictors, dropped the 30 to 60 percent weights and TROPOMI, and confirmed the paper's abstract figures through two separate reads of the Springer page.

Docket item tx-2026-0251, statewide, research-and-science.

## Why this treatment, and what was grafted

Base: THE LAND. Texas held up as a slab of its own ground, read from orbit, then walked at ground level west to east, until the camera reaches the one place a satellite reading can't go, a single person. Grafted from THE EVIDENCE AND ITS LIMITS: the close is a terrain relief where satellite blocks are coarse everywhere except a sharp circle round one ground monitor, and one block over a town is outlined in gold as where to look first. Grafted from THE INSTRUMENT: the satellite is in silver and graphite foil, never gold, so it never borrows the accent. Sulfur dioxide moves onto the air column frame as the one band standing proud. Dropped: a Moran's index rail or bar (no claim gives the scale's range, so 0.69 is printed in the dek only), the molecule model, the compute rack (too near the November 17th machine), and the hospital close.

## The spine

`assets/js/deck/2026-11-18-landbench-bespoke.js`. LOOK V2, tone EXPLAINER, bespoke. Each frame owns its world, light, camera and type position. Shadows lean indigo, never black.

THE ACCENT is dusk gold #E0956A (brand.yaml) and means ONE thing: WHAT THE SATELLITE READ, the air as measured. It appears on frames 1 (the air sheet over the state), 3 (the swath from the satellite), 4 (the column's outline and the sulfur dioxide band), 6 (the three air blocks), 8 (the kerb that is the edge of one reading) and 9 (the outlined block). It is absent from 2 (a ground monitor is not the satellite), 5 (the fit is the model's, so its flags are bluebonnet) and 7 (cancer clustering is the CDC layer, not the satellite).

CONTINUITY: CAMERA_MOVE, MOTIF_EVOLUTION, VALUE_ARC
1. CAMERA_MOVE, orbit to ground. The camera starts over the whole state (1, 3), comes down to a column of air and a staked plot (4, 5), walks west to east (6, 7), lands at one person's shoulder (8), then lifts to a stretch of land to show where to look (9).
2. MOTIF_EVOLUTION, the gold air. A sheet over the state (1), a swath (3), a column (4), three blocks over three grounds (6), the edge of one reading (8), one outlined block (9).
3. EAST IS ALWAYS FRAME RIGHT. Every frame with geography holds west at left and east at right, so the east-worse finding lands in the same place in the eye every time.

### Palette

| token | hex | role |
|---|---|---|
| sky | TXLOOK.TONES.explainer | cerulean to ice sky and sweep |
| shade | indigo | shadows, never black |
| caliche | #e4d8c3 | West Texas ground |
| limestone | #ede6d6 | Hill Country ground |
| clay | #8c5a3c | East Texas red clay |
| pine | #2f5a3a | loblolly green |
| bluebonnet | #4e5fa8 | the model's flags and the cancer stones |
| accent | #e0956a | dusk gold, what the satellite read only |

## THE NINE BEATS

1. READ FROM ORBIT. Feel: the scale of it. Know: A UT Dallas team read all 254 counties from above. c1 c2 c24. FIG counties.
2. WHY SATELLITES. Feel: how much land one station leaves. Know: Ground monitors are costly and missing in places. c13 c25.
3. THE INSTRUMENT. Feel: precision. Know: The readings came from Sentinel-5 Precursor and Copernicus. c17 c23 c2. FIG pollutants.
4. WHAT IT READ. Feel: the air has parts. Know: Eight pollutants in 2022, sulfur dioxide the strongest predictor. c4 c6 c26. FIG pollutants.
5. THE FIT. Feel: a fair contest with a winner. Know: Four methods compared, the support vector machine fit best. c3 c20 c21. FIG r2_of_100.
6. EAST TO WEST. Feel: the air has a direction. Know: Three clusters, east worse, west better, and more pollution went with more cancer. c7 c8 c5. FIG clusters.
7. NEIGHBOURS. Feel: clumping you can see. Know: High cancer counties sit next to each other, not every polluted place had more cancer. c9 c22 c10 c19. FIG counties.
8. A PLACE IS NOT A PERSON. Feel: clarity without alarm. Know: The results say nothing about one person, and satellites are less precise than the ground. c11 c12.
9. WHERE TO LOOK FIRST. Feel: purpose. Know: The method shows where to look, especially where no monitor stands. c14 c25 c18 c11.

Showstopper frame: 08
VALUE CUT: frame 4
The cut drops from the open studio of 03 into the deck's one measured relief of air.

Tonal arc: open cerulean sky round a floating slab, a bright caliche flat, an ice studio, a raking relief of air, a fall pasture from above, a warm studio row of three grounds, a raking stone field, an early afternoon pasture at a shoulder, a raking terrain relief.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | WIDE, high three quarter from over the Gulf looking north northwest, fov 30 | a slab of Texas 0.6 m thick cut from the real outline by TXT.extrude, its top textured by region (caliche west, limestone centre, red clay and pine east), all 254 county lines engraved as hairline grooves, a 3 mm dusk gold glass air sheet floating above it casting a soft shadow, in TXT.sky v2explainer |
| 02 | WIDE, eye height 1.6 m, 50 m back, 35 mm, horizon at 0.62 of the frame | the chassis air_monitor_shelter on a concrete pad with inlet mast and met mast, kit chain_link_fence round it, kit pickup and kit person in a vest at the door, kit mesa on the horizon, TXT.ground caliche with scatter and kit mesquite, TXT.contact and TXT.weather |
| 03 | CLOSE, low three quarter from below right, 50 mm, the solar wing on a diagonal | the chassis survey_satellite in silver and graphite foil with a crinkle bump, a blue cell solar wing, a nadir instrument with baffle, a star tracker and antenna, a dusk gold glass swath fan of eight bands opening off the bottom, TXT.studio explainer |
| 04 | MEDIUM, orthographic front elevation relief raked from the upper left | a carved column of air over a plug of ground, a TXBENCH.relief raked from the upper left with cast shadows under each band, saturated glassy and matte materials, the ground strata weathered, a plug of ground in three strata (topsoil, caliche, limestone) under a rounded column of air cut into eight measured bands, the sulfur dioxide band standing proud, the column outline inlaid in dusk gold |
| 05 | MEDIUM, elevated oblique 9 m up and 35 degrees down, never top down | 100 kit lath_stake in a 10 by 10 grid at 1.5 m pitch on a graded caliche pad, FIG.r2_of_100 carrying bluebonnet flagging and the rest bare, kit pasture round it, kit pickup and kit person for scale, long stake shadows from a low west key, TXT.sky v2explainer |
| 06 | MEDIUM, frontal three quarter at slab top height, 85 mm | three 4 by 4 m ground slabs 0.8 m deep with their soil sections, west caliche with kit mesquite, centre a cut of kit hill_country_terrain with kit live_oak and ashe_juniper, east red clay with kit pine, each under a dusk gold glass air block with haze clearest west and densest east, TXT.studio explainer warmer sweep |
| 07 | CLOSE, raking close crop relief from the low west | a floor of limestone flagstones, a TXBENCH.relief raked low with cast shadows between stones, matte limestone and slate materials, chiselled weathered edges, exactly FIG.counties limestone flagstones from a seeded Voronoi laid in mortar, the darker bluebonnet slate stones gathered in contiguous groups, chiselled edges, mortar recessed |
| 08 | WIDE, 1.4 m just behind a resident's shoulder, 28 mm | kit person large in the left third looking out over a fall pasture, a 0.1 m dusk gold kerb set in the grass running away to the horizon and turning a far corner, kit ranch_house in limestone, three kit live_oak, a kit road with a kit pickup, TXT.sky v2explainer early afternoon, TXT.contact |
| 09 | AERIAL, high oblique relief raked from the east | a terrain of Texas land, a TXBENCH.relief raked from the east with cast shadows off every block, matte limestone and caliche materials, weathered terrace lips, an illustrative stretch of Texas land from noise.js fBm with a town of street grooves and building blocks, flat topped satellite blocks averaging the height everywhere except a sharp full detail circle round one thin ground monitor post, one averaged block outlined in raised dusk gold |

Showstopper frame: 08, a resident seen large from behind the shoulder while a thin gold kerb in the grass runs away across a pasture, past a limestone ranch house, three live oaks and a pickup, and turns a corner far off. Its depth is the 28 mm lens, the kerb converging to the horizon and the shadows of the oaks on the grass.
Tonal arc: open cerulean on 01, bright caliche on 02, an ice studio on 03, a raking relief on 04, a fall pasture from above on 05, a warmer studio on 06, raking stone on 07, early afternoon at a shoulder on 08, raking terrain on 09.

---
```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: a slab of Texas cut from the real outline floating in a clear cerulean sky, its top textured caliche west, limestone centre, red clay and pine east, all 254 county lines engraved as hairlines, a thin dusk gold glass sheet of measured air hovering over it and casting its shadow on the land
  rect: [60, 300, 960, 760]
  bleeds: []
accent: '#e0956a'
data_in_art: {figure: counties, drives: "engraved county boundary count read from assets/geo, asserted in code to equal FIG.counties"}
job: "Put the whole method in one object, every county of Texas read from above."
claims: [c1, c2, c24, c5]
numerals:
- {value_from: c1}
depth:
  eye: 40
  horizon: 0
  cues: [FORM_SHADING, CAST_SHADOW, RELATIVE_SIZE, AERIAL]
  subject_at: {X: 0, Z: 0}
composition: {structure: "BESPOKE. The slide artist composes the picture and places the type where this picture leaves quiet (knowledge/carousel/BESPOKE.md). WIDE, high three quarter from over the Gulf looking north northwest, fov 30.", bands: "Top third, open cerulean sky for the type. Middle third, the slab with the gold air sheet above it. Bottom third, the slab's cut edge in shadow and sky below it.", focal: "the gold air sheet's shadow on the engraved counties"}
art: {technique: "physically based render of an extruded real outline slab with engraved county grooves and a transmissive gold sheet in TXT.sky v2explainer", why_this_technique: "the study looked down on every county at once, so the state is drawn as one object under one measured layer of air", palette: "caliche, limestone, red clay and pine green under cerulean and ice sky, dusk gold glass", value_structure: "Lightest is the lit top of the slab under the sheet. Darkest is the indigo cut edge. No near black."}
verbatim: []
acceptance: ["the Texas slab spans at least 760 px of the frame width at 1080 px, measured on the art", "the frame code reads the county outlines from assets/geo/tx-counties.topo.json and throws unless their count equals FIG.counties", "the air sheet is the only dusk gold and it casts a visible shadow on the slab", "west is at frame left and east at frame right", "one small illustrative survey satellite may appear at top right, with no logo, flag or agency mark, and its beam lands on the air sheet only", "no numeral on this slide is absent from claims.json"]
risks: []
type:
  hook: "All 254 Texas counties, read from above"
  dek: "A UT Dallas team paired satellite readings of the air with CDC cancer data, county by county. Counties with more pollution tended to have more cancer. The slab, its sheet of air and the satellite are drawn to illustrate."
  labels: []
```

```yaml
slide: 2
layout: SPLIT_HORIZON
primary_image:
  subject: one small air monitoring shelter with a fence round it on an immense empty West Texas caliche flat, a worker at its door and a pickup beside it, a mesa on the far horizon and a huge sky
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: '#e0956a'
job: "Make the cost of ground monitoring physical, one station and a lot of land it can't see."
claims: [c13, c25]
numerals: []
depth:
  eye: 1.6
  horizon: 840
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL]
  subject_at: {X: 0, Z: 0}
composition: {structure: "BESPOKE. The slide artist composes the picture and places the type where this picture leaves quiet (knowledge/carousel/BESPOKE.md). WIDE, eye height 1.6 m, 50 m back, 35 mm, horizon at 0.62 of the frame.", bands: "Top third and more, the wide sky for the type. Middle band, the far mesa and the empty flat. Bottom third, the shelter, fence, pickup and worker on caliche with long shadows.", focal: "the shelter and the worker at its door"}
art: {technique: "physically based render of the chassis air_monitor_shelter with kit chain_link_fence, pickup, person, mesquite and mesa in TXT.sky v2explainer on TXT.ground caliche", why_this_technique: "a station a person can stand beside next to land that runs to the horizon shows why a ground network is costly and thin", palette: "caliche, galvanized steel, white fibreglass, olive scrub, cerulean sky", value_structure: "Lightest is the white shelter in the sun. Darkest is the indigo shadow under the pickup. Colour in the mid tones."}
verbatim: []
acceptance: ["the shelter, fence and pickup span at least 300 px of the frame width at 1080 px, measured on the art", "the chassis air_monitor_shelter is present with its inlet mast and met mast, never a plain box", "a kit person stands at the shelter door at true scale", "no dusk gold appears on this frame", "the ground runs empty to a far mesa with no second station in view", "no numeral on this slide is absent from claims.json"]
risks: []
type:
  hook: "Ground monitoring is costly"
  dek: "That cost has limited this kind of study, Dong says. The paper says satellite data can help where ground monitoring is unavailable. Drawn to illustrate."
  labels: []
```

```yaml
slide: 3
layout: OBJECT_AND_CAPTION
primary_image:
  subject: an illustrative survey satellite shot like a product, close and large in silver and graphite foil with a blue cell solar wing on a diagonal, a dusk gold glass swath of eight bands opening down off the bottom of the frame
  rect: [600, 220, 480, 1130]
  bleeds: [bottom, right]
accent: '#e0956a'
data_in_art: {figure: pollutants, drives: "band count in the swath fan, asserted in code to equal FIG.pollutants"}
job: "Show the instrument the readings came from, as a made thing seen up close."
claims: [c23, c2]
numerals: []
depth:
  eye: 0
  horizon: 0
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION, RELATIVE_SIZE]
  subject_at: {X: 0, Z: 0}
composition: {structure: "BESPOKE. The slide artist composes the picture and places the type where this picture leaves quiet (knowledge/carousel/BESPOKE.md). CLOSE, low three quarter from below right, 50 mm, the solar wing on a diagonal.", bands: "Top third, the wing tip and ice sweep. Middle third, the foil bus and instrument. Bottom third, the gold swath fanning off the frame in the foreground with its glow on the sweep, and a column of quiet sweep at right for the type.", focal: "the instrument aperture where the swath begins"}
art: {technique: "physically based render of the chassis survey_satellite in TXT.studio explainer", why_this_technique: "the readings came from orbit, so the instrument is shown as a crafted object and its swath carries the eight readings", palette: "silver and graphite foil, blue cell glass, chrome, dusk gold swath, ice and cerulean sweep", value_structure: "Lightest is the foil catching the key. Darkest is the indigo under the wing. No near black."}
verbatim: []
acceptance: ["the satellite spans at least 600 px of the frame width at 1080 px, measured on the art", "the frame code fans FIG.pollutants bands in the swath and throws if the count differs", "the swath is the only dusk gold and the foil is silver and graphite, never gold", "the satellite carries no logo, flag or agency mark", "the dek says the craft is drawn to illustrate", "no numeral on this slide is absent from claims.json"]
risks: []
type:
  hook: "Where the readings came from"
  dek: "The air readings came from the Sentinel-5 Precursor satellite and the Copernicus Atmosphere Monitoring Service. Public CDC data supplied the cancer side. The craft, its swath and the ground are drawn to illustrate."
  labels: []
```

```yaml
slide: 4
layout: DIAGRAM
primary_image:
  subject: a carved section elevation, a plug of Texas ground in three strata under a rounded column of air cut into eight measured bands, the sulfur dioxide band standing proud of the rest, the column outline inlaid in dusk gold
  rect: [240, 120, 600, 1000]
  bleeds: []
accent: '#e0956a'
data_in_art: {figure: pollutants, drives: "band count in the air column from FIG.pollutant_names, the first standing proud, asserted in code to equal FIG.pollutants"}
job: "Show the eight things the satellites read, and which one led."
claims: [c4, c6, c26]
numerals:
- {value_from: c4}
depth:
  eye: 0
  horizon: 0
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}
composition: {structure: "BESPOKE. The slide artist composes the picture and places the type where this picture leaves quiet (knowledge/carousel/BESPOKE.md). MEDIUM, orthographic front elevation relief raked from the upper left.", bands: "Top third, the column top and sky field. Middle third, the eight bands each casting onto the next, the sulfur dioxide band proud. Bottom third, the ground plug strata in raking light with their cast shadow, and the sky field beside it for the type.", focal: "the sulfur dioxide band standing proud"}
art: {technique: "TXBENCH.relief height field on TXLOOK.sky2d with TXLOOK.reliefLight, limestone, caliche, glassy bands and gold inlay", why_this_technique: "a geological column applied to air turns eight pollutants into layers a reader can count, and relief height lets one stand out without a chart", palette: "saturated explainer tints for the bands, caliche and limestone strata, dusk gold inlay", value_structure: "Lightest is the key on the proud band. Darkest is the cast under it. No near black."}
verbatim: []
acceptance: ["the carved column of air spans at least 800 px of the frame height at 1350 px, measured on the art", "the frame code builds one band per entry of FIG.pollutant_names and throws unless the count equals FIG.pollutants", "the sulfur dioxide band stands visibly prouder than the other seven and casts a longer shadow", "the column outline and the proud band carry the only dusk gold", "the TXBENCH.relief is present with measured height, never a flat drawing", "no numeral on this slide is absent from claims.json"]
risks: []
type:
  hook: "Eight pollutants, sulfur dioxide strongest"
  dek: "The study read eight air pollutants from 2022 data. Among the environmental predictors of cancer, sulfur dioxide was the most influential. The bands are drawn to illustrate, not heights in the sky."
  labels: []
```

```yaml
slide: 5
layout: FIGURE_SCALE
primary_image:
  subject: a graded caliche plot in a fall pasture staked on a 10 by 10 grid of lath survey stakes, 79 carrying bluebonnet flagging and 21 bare, each throwing a long countable shadow, a pickup and a worker at the edge for scale
  rect: [0, 420, 1080, 930]
  bleeds: [left, right, bottom]
accent: '#e0956a'
data_in_art: {figure: r2_of_100, drives: "flagged stake count of 100, computed from FIG.r2_of_100 and asserted in code"}
job: "Make the model's fit a thing a reader can count on the land, and say it is a fit."
claims: [c3, c20, c21, c27, c19]
numerals:
- {value_from: c21}
depth:
  eye: 9
  horizon: 300
  cues: [LINEAR_PERSPECTIVE, CAST_SHADOW, TEXTURE_GRADIENT, RELATIVE_SIZE]
  subject_at: {X: 0, Z: 0}
composition: {structure: "BESPOKE. The slide artist composes the picture and places the type where this picture leaves quiet (knowledge/carousel/BESPOKE.md). MEDIUM, elevated oblique 9 m up and 35 degrees down, never top down.", bands: "Top third, pasture running to a low horizon and sky for the type. Middle third, the far rows of stakes. Bottom third, the near flagged stakes with long shadows on caliche.", focal: "the boundary where flagged stakes give way to bare ones"}
art: {technique: "physically based render of kit lath_stake, pasture, pickup and person in TXT.sky v2explainer on TXT.ground caliche", why_this_technique: "stakes driven in land read as a survey, so 79 flagged of 100 is counted rather than charted, and the land keeps the deck in Texas", palette: "caliche pad, fall pasture, pale lath, bluebonnet flagging, cerulean sky", value_structure: "Lightest is the caliche in sun. Darkest is the indigo stake shadows. Colour in the mid tones."}
verbatim: []
acceptance: ["the grid of lath stakes on the winning pad spans at least 650 px of the frame width at 1080 px, and the pad itself at least 900 px, measured on the art", "the frame code flags FIG.r2_of_100 of 100 kit lath_stake and throws if either count differs", "the view is oblique with visible stake shadows, never top down", "no dusk gold appears on this frame, the flagging is bluebonnet", "the dek says R squared is a model fit, not a share of cancer explained", "no numeral on this slide is absent from claims.json"]
risks: []
type:
  hook: "Four methods tried, one fit best"
  dek: "A support vector machine fit best, with an R squared of 0.791, drawn here as 79 flagged stakes in 100 on the one pad that won. Rahman says socioeconomic and other variables were controlled for. The 0.791 is a model's fit, not how much cancer pollution causes. Cancer reflects many influences besides pollution."
  labels: []
```

```yaml
slide: 6
layout: OBJECT_AND_CAPTION
primary_image:
  subject: three slabs of real Texas ground in a row, west caliche with mesquite, central Hill Country limestone with a live oak, east red clay with loblolly pines, each under a dusk gold glass block of air, clearest in the west and densest in the east
  rect: [40, 420, 1000, 620]
  bleeds: []
accent: '#e0956a'
data_in_art: {figure: clusters, drives: "number of ground slabs and air blocks, asserted in code to equal FIG.clusters"}
job: "Make the three air clusters three kinds of ground a Texan can tell apart, with the haze in order."
claims: [c7, c8]
numerals: []
depth:
  eye: 0.8
  horizon: 700
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION, RELATIVE_SIZE]
  subject_at: {X: 0, Z: 0}
composition: {structure: "BESPOKE. The slide artist composes the picture and places the type where this picture leaves quiet (knowledge/carousel/BESPOKE.md). MEDIUM, frontal three quarter at slab top height, 85 mm.", bands: "Top third, the warm sweep wall for the type. Middle third, the three air blocks over the trees. Bottom third, the slab soil sections in the foreground and their contact shadows on the sweep.", focal: "the densest air block over the eastern pines"}
art: {technique: "physically based render of three ground slabs with kit mesquite, live_oak, ashe_juniper and pine under transmissive gold blocks in TXT.studio explainer", why_this_technique: "three samples at one scale side by side let order read at a glance without implying county values", palette: "caliche, limestone, red clay, olive and pine green, dusk gold glass, warm sweep", value_structure: "Lightest is the clear western block. Darkest is the indigo under the eastern slab. Colour in the mid tones."}
verbatim: []
acceptance: ["the three slabs together span at least 900 px of the frame width at 1080 px, measured on the art", "the frame code builds FIG.clusters slabs and throws if the count differs", "haze density steps up from west at frame left to east at frame right", "the air blocks are the only dusk gold", "the dek says the haze shows order only, not county values", "no numeral on this slide is absent from claims.json"]
risks: []
type:
  hook: "Worse air east, better air west"
  dek: "Dong describes three major clusters of air pollution, with central Texas in between. The haze shows the order of air quality only, not cancer or county values."
  labels: []
```

```yaml
slide: 7
layout: CLOSE_CROP
primary_image:
  subject: a close cropped field of 254 irregular limestone flagstones laid in mortar, the darker bluebonnet slate stones gathered in contiguous groups rather than scattered, every stone casting in raking light
  rect: [0, 0, 1080, 1350]
  bleeds: [top, right, bottom]
accent: '#e0956a'
data_in_art: {figure: counties, drives: "stone count in the seeded Voronoi field, asserted in code to equal FIG.counties"}
job: "Show clustering as something you can see in a floor of stones, and admit what it does not prove."
claims: [c9, c22]
numerals:
- {value_from: c22}
depth:
  eye: 0
  horizon: 0
  cues: [FORM_SHADING, CAST_SHADOW, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 0}
composition: {structure: "BESPOKE. The slide artist composes the picture and places the type where this picture leaves quiet (knowledge/carousel/BESPOKE.md). CLOSE, raking close crop relief from the low west.", bands: "Top third, a quieter mortar run for the type. Middle third, the gathered slate groups. Bottom third, the near stones in the foreground with long shadows off their chiselled edges.", focal: "the largest gathered group of slate stones"}
art: {technique: "TXBENCH.relief seeded Voronoi stone field on TXLOOK.sky2d with TXLOOK.reliefLight, limestone, slate and mortar", why_this_technique: "a floor of stones reads as ground, never as a chart, and gathered dark stones show neighbours resembling neighbours without naming any county", palette: "warm cream limestone, bluebonnet slate, grey mortar", value_structure: "Lightest is the key on the limestone lips. Darkest is the cast between stones. No near black."}
verbatim: []
acceptance: ["the floor of limestone flagstones covers at least 80 percent of the frame at 1080 px, measured on the art, modelled as a relief and never a flat drawing", "the frame code builds exactly FIG.counties stones and throws if the count differs", "the slate stones form contiguous groups, not a random scatter", "no dusk gold appears on this frame", "no county shape, name or outline appears, and the dek says the stones are drawn to illustrate", "no numeral on this slide is absent from claims.json"]
risks: []
type:
  hook: "High cancer counties sit near each other"
  dek: "The paper scores that clustering of cancer prevalence at a Moran's index of 0.69. The stones are drawn to illustrate."
  labels: []
```

```yaml
slide: 8
layout: FULL_BLEED
primary_image:
  subject: a resident seen large from just behind the shoulder in a fall pasture, a thin dusk gold kerb set in the grass running from near their boots straight away past a limestone ranch house, three live oaks and a pickup on a farm road, turning a corner far off, the edge of one satellite reading
  rect: [0, 380, 1080, 970]
  bleeds: [left, right, bottom]
accent: '#e0956a'
job: "Turn the paper's caution into one picture, a place is not a person."
claims: [c11, c10, c12]
numerals: []
depth:
  eye: 1.4
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL]
  subject_at: {X: 0, Z: 0}
composition: {structure: "BESPOKE. The slide artist composes the picture and places the type where this picture leaves quiet (knowledge/carousel/BESPOKE.md). WIDE, 1.4 m just behind a resident's shoulder, 28 mm.", bands: "Top third, cerulean sky for the type. Middle third, the far corner of the kerb, the house and oaks. Bottom third, the resident's lit shoulder in the foreground at left and the kerb starting in the near grass with its shadow.", focal: "the far corner where the gold kerb turns"}
art: {technique: "physically based render of kit person, pasture, ranch_house, live_oak, road and pickup with a gold kerb in TXT.sky v2explainer", why_this_technique: "one reading holds a house, trees, a road and a person at once, so the person is plainly not what it measured", palette: "fall pasture, limestone, live oak green, white pickup, dusk gold kerb, cerulean sky", value_structure: "Lightest is the sky near the horizon. Darkest is the indigo shade under the oaks. Colour in the mid tones."}
verbatim: []
acceptance: ["the kit person fills at least 40 percent of the frame height at 1350 px, measured on the art", "the gold kerb is visible from the near grass to a turned corner near the horizon", "the kerb is the only dusk gold and the resident wears none", "no numeral appears on this slide", "the dek says the results are not evidence about any one person", "no numeral on this slide is absent from claims.json"]
risks: []
type:
  hook: "A place is not a person"
  dek: "The researchers say the results don't establish that pollution causes cancer in any one person. Not every more polluted place had more cancer, and satellite data may be less precise than ground monitors. Drawn to illustrate."
  labels: []
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: a raking terrain relief of an illustrative stretch of Texas with a town, broken into flat topped satellite blocks everywhere except a sharp full detail circle round one ground monitor post, one averaged block outlined in raised dusk gold
  rect: [0, 0, 1080, 1350]
  bleeds: [left, right, top, bottom]
accent: '#e0956a'
job: "Close on what the method is for, knowing where to look first, especially where no monitor stands."
claims: [c14, c18, c11]
numerals:
- {value_from: c11}
depth:
  eye: 0
  horizon: 0
  cues: [FORM_SHADING, CAST_SHADOW, TEXTURE_GRADIENT, OCCLUSION]
  subject_at: {X: 0, Z: 0}
composition: {structure: "BESPOKE. The slide artist composes the picture and places the type where this picture leaves quiet (knowledge/carousel/BESPOKE.md). WIDE, high oblique relief raked from the east.", bands: "Top third, coarse terraces receding. Middle third, the sharp circle round the monitor and the gold block over the town. Bottom third, a band of the dimmest coarse terraces in the foreground, their shadows quiet for the type.", focal: "the gold outlined block over the town"}
art: {technique: "TXBENCH.relief from noise.js fBm with building blocks, block averaged outside one circle, limestone, caliche and gold", why_this_technique: "the satellite's coarse view and a ground monitor's sharp one side by side show where the method helps and where it is blurry, and the gold block is where to look first", palette: "limestone and caliche terrain, olive scrub, dusk gold outline", value_structure: "Lightest is the key on the terrace lips. Darkest is the cast off the blocks. No near black."}
verbatim: []
acceptance: ["the terrain relief covers at least 90 percent of the frame at 1080 px, measured on the art", "the frame code averages height into blocks everywhere outside one circle round the monitor post and states the block size as an illustrative constant", "one averaged block carries the only dusk gold, a raised outline marking where to look first", "the monitor post stands at the centre of the sharp circle", "the dek names Environmental Monitoring and Assessment and March 5th", "no numeral on this slide is absent from claims.json"]
risks: []
type:
  hook: "Where to look first"
  dek: "The team says the method can show where medical centers are and where government should focus. The team wants more research on cost and accuracy. The paper ran online March 5th in Environmental Monitoring and Assessment. The land and its blocks are drawn to illustrate."
  labels: []
```
