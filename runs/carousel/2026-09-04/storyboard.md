# Carousel no. 15 — storyboard and dossiers

**The decision.** The Department of Homeland Security Science and Technology Directorate ran an
operational assessment of facial biometric image capture on the pedestrian exit lane at the
Progreso International Bridge, for U.S. Customs and Border Protection. It published its account
on September 1st, 2026. Item tx-2026-0120 in the record.

**The angle.** The account is written in adjectives. It publishes no accuracy rate, no count of
images captured, no retention period, no deployment decision and no date range for the May
assessment. The one hard figure in it belongs to the crossing rather than to the machine. And
the same agency publishes a measured monthly count of pedestrians walking IN at this port while
stating plainly that it collects no comparable data on the way out.

**The register.** The inside of an optical instrument, and the lane it was pointed down, at an
international bridge over the Rio Grande after dark. Flocked baffle black, hardcoat anodised
housing, coated glass, poured concrete, hot dip galvanized steel, die-cut foam, river silt.

**THE DECK'S TWO LAWS OF LIGHT, and they carry the argument as physics rather than as a caption.**

1. **The light has two owners and they never trade roles.** High pressure sodium is the bridge's
   own light, ambient, warm, wide and low. 4000K LED is what the test brought, directional, cool,
   narrow and high. No object in nine frames takes both as its key. Frame 5 declares neither,
   which is that frame's whole argument.
2. **No face, no body, no person, no uniform and no vehicle anywhere in nine frames.** A deck
   about facial capture that draws a face has invented the one thing the record does not publish.
   Movement appears once, on frame 5, as the machine's own record of it.

**Two more laws.**

3. **Filled means the account states it. Cut and empty means it does not.** Absence is always
   drawn as a lit slot with a lip, a side wall and a floor, never as a black rectangle. Deck 9's
   own `avoid_next` records what a black field does here. It reads as a REDACTION, which says
   something was removed when the record says nothing was ever stated.
4. **No ratio is drawable.** Six companies demonstrated and three solutions carried forward are
   counts of different things, and no frame puts them on one scale.

**The reserved red is argued UNSPENT.** `--flag-red` is for an open comment deadline a reader can
still act on. September 8th, 2026 is a briefing on a different program in a different city, and
giving it the reserved colour would be the drawing asserting it is a door onto the Progreso test
when the copy says plainly that it is not. The date is set instead in `led_cool`, the brightest
ink on frame 9.

**Palette**, drawn from Hidalgo County at the bridge after dark and from the inside of an optical
instrument. Six near misses against decks 6 to 14 were measured rather than assumed, and each
token below that moved says what it moved away from.

| token | hex | source | moved from |
|---|---|---|---|
| `river_night` | `#0D1417` | the Rio Grande under the span at night, green black, carrying no violet so it can never read as the house Big Bend register | |
| `baffle` | `#0D1013` | flocked matte interior of a lens barrel, near zero reflectance | |
| `citrus_dark` | `#1E2E26` | Hidalgo County grove canopy in the dark. The deck's SECOND dark, so the dark frames differ by hue rather than all reading as one black field | |
| `housing` | `#2B343E` | Type III hardcoat anodised aluminium, cool and on the blue side of neutral | deck 6's `console #24322F` |
| `slab` | `#2E3130` | the walkway's poured concrete outside any light pool | |
| `slab_sodium` | `#6E5A40` | the same slab inside a sodium pool | |
| `slab_led` | `#869597` | the same slab inside an LED pool. One material, two lights, two values AND two hues | deck 9's `#949AA0` |
| `sodium` | `#D9701F` | high pressure sodium on the bridge approach, the bridge's own light | deck 9's guard yellow `#E7B819` and deck 6's `#D99A32` |
| `led_cool` | `#C3D4DE` | the 4000K external work lighting the night tests used | deck 9's `highbay #E9EEF3` |
| `galv` | `#6E7B7E` | hot dip galvanized pole, canopy frame and chain link fabric | deck 9's `#7E8385` |
| `paint_worn` | `#A9AEA4` | worn traffic paint on the slab. The deck's ink | deck 9's `#B9BCBA` |
| `foam` | `#1A1D1C` | charcoal die-cut closed cell foam. Frame 8 only, and a material no deck here has touched | |
| `rio_turbid` | `#6B6A4C` | the Rio Grande's suspended silt under lamp light | |
| `glass_lit` | `#F1F4F2` | the transilluminated field of a chrome on glass target. Frame 5 only | |
| `chrome_bar` | `#8E9A9E` | evaporated chrome bars on that target. Frame 5 only | |
| `flag_red` | `#BF0A30` | reserved, and UNSPENT this deck | |

**The value arc, planned per frame median L\***, measured off the rendered PNGs after every round.

```
F1  24   the lane
F2  18   three heights
F3  21   six in, three out
F4  13   they built it twice, the darkest frame
F5  88   JUDGED SUITABLE. The inversion and the turn
F6  32   the other lane, the counter image
F7  28   one direction is counted
F8  17   the case, the hero
F9  25   no room here
```

Planned deck median **24**, which sits in the gap between the priors of 22.2 and 27.7 rather than
on top of 20.4 and 21.2. The junction that matters is frame 4 to frame 5, seventy five points, and
it falls exactly at the seam between the built place and the modelled one.

---

```yaml
slide: 1
job: >
  Puts the reader standing in the pedestrian exit lane and states the whole decision, so that
  every frame after it is apparatus the reader has already walked past.
claims: [c1, c12, c27, c28]
numerals: []

composition:
  structure: >
    A true one point corridor with the vanishing point at 0.42 of the width rather than centred,
    so the lane runs away from the reader off axis and the eye has somewhere to travel. This
    content wants a corridor because the record's own subject is a walkway a person moves down,
    and a corridor is the only construction that makes the reader the pedestrian rather than an
    observer of one.
  bands: >
    The top third carries the masthead over the canopy soffit, where a modeled LED wash falls off
    across the ribbed underside and the ribs take a graded highlight on their lower edge. The
    middle third carries the headline over the lane's deepest recession, with the far sodium pools
    reading through the type's scrim. The bottom third is the slab itself in three lit stages, a
    warm sodium pool at the reader's feet grading across broom finish concrete tooth into an
    unlit stretch and then into the first LED pool, with the near diamond mesh crossing the lower
    left corner as a modeled occluder that takes its own rim light.
  focal: >
    The lit slab area at the reader's feet in the lower third, the largest area of the frame's
    warmest and lightest value, which pulls the eye down into the lane before it climbs the type.

art:
  technique: "Parallax planes, five declared depths, with a diamond mesh near plane that occludes"
  why_this_technique: >
    Depth here has to be believable rather than impressive, because the claim is that a person
    walks past cameras without stopping. Parallax planes read as depth immediately at 432px where
    a full 3D scene would resolve to mud, and the library says to reach for them first.
  palette: >
    river_night #0D1417 ground, slab #2E3130, slab_sodium #6E5A40, slab_led #869597,
    sodium #D9701F, led_cool #C3D4DE, galv #6E7B7E, paint_worn #A9AEA4
  value_structure: >
    Lightest is the sodium pool on the slab at the bottom of the frame, which is where the light
    is. Darkest is the canopy shadow behind the near mesh at the upper left. The five planes are
    declared at L* 8, 14, 22, 48 and 61 so no two share a value.
  motion: "Down the lane and away, then back up the type"

type:
  hook: "Tested on the faces walking out."
  dek: "The Department of Homeland Security Science and Technology Directorate ran it for Customs and Border Protection at the Progreso International Bridge in Hidalgo County. The bridge director puts the annual walk out at over 1.1 million."
  labels: ["DHS S AND T", "c1 c12 c27 c28", "texasaidocket.com", "01 / 09"]

acceptance:
  - 'the hook reads exactly "Tested on the faces walking out." and is six words'
  - 'the near diamond mesh plane occludes at least 30 percent of the plane behind it, drawn as real occlusion rather than as a tint'
  - 'the five parallax planes hold five distinct median L* values at least 6 apart, and none is within 6 of another'
  - 'the string "Hidalgo County" appears on this frame, and so does "Customs and Border Protection", because a deck whose subject is one body''s account has to name that body in reader copy rather than in a footer chip'
  - 'no person, no face, no body and no vehicle appears anywhere on this frame'
  - 'the sodium pools are emitted falloff on the slab and are never bounded by a drawn stroke'
risks:
  - 'the layers share a value and the frame becomes a collage rather than a corridor'
  - 'a corridor at night resolves to one dark field at 432px, so the slab''s three lit stages have to survive the thumb'
```

```yaml
slide: 2
job: >
  Shows the apparatus that was actually installed, and dates the request that produced it, so the
  reader learns this was asked for rather than arrived.
claims: [c2, c28, c29]
numerals:
  - value_from: c2

composition:
  structure: >
    A vertical looking straight up the pole at eighty eight degrees, with no ground plane and no
    horizon anywhere, so the pole runs out of the bottom of the frame and the reader is beneath
    it. This content wants the vertical because the record's own detail is that mount HEIGHT was
    varied for people of different statures, and height is only legible against a body's own axis.
  bands: >
    The top third carries the pole head and the highest collar against sodium skyglow, with the
    housing's upper face taking a cool LED rim and its underside falling into its own shade.
    The middle third carries the second collar, its bracket and knuckle modeled as a real
    assembly, and the headline set beside the pole rather than over it. The bottom third carries
    the lowest collar nearest the reader at the largest scale, its downward spill cone drawn as a
    graded volume in humid air rather than as a flat wedge, with the pole's galvanized spangle
    coarsening toward the reader as a modeled surface.
  focal: >
    The lowest collar's housing in the bottom third, the largest modeled object in the frame and
    the one carrying the brightest LED rim.

art:
  technique: "Diagrammatic mast and three mount assemblies drawn in canvas 2D, no ground plane"
  why_this_technique: >
    The library reserves the diagrammatic register for an object like a transformer, and a camera
    mast is exactly that. Its failure is being reached for when the subject is terrain, and there
    is no terrain on this frame at all.
  palette: "baffle #0D1013 ground, galv #6E7B7E, housing #2B343E, led_cool #C3D4DE, sodium #D9701F skyglow"
  value_structure: >
    Lightest is the LED rim along the lowest collar's housing at the bottom of the frame. Darkest
    is the pole's own shaded flank running the full height. The sodium skyglow sits at a mid value
    behind everything and never touches an object as a key.
  motion: "Up the pole, collar to collar"

type:
  hook: "It had to account for hats and umbrellas."
  dek: "Customs and Border Protection asked for it in October 2025. Cameras went up on poles at different heights, so people of different statures would land in frame. The technologies had to account for walking pace, hats, sunglasses and umbrellas."
  labels: ["MOUNTS", "c2 c28 c29", "texasaidocket.com", "02 / 09"]

acceptance:
  - 'three camera collars are drawn at three different heights on one pole, and no two collars share a height'
  - 'no ground plane and no horizon line appears anywhere on this frame'
  - 'the interval between collars is drawn and is never dimensioned, because the account states no figure for it'
  - 'each collar is a real assembly carrying a bracket and a knuckle, not a box on a stick'
  - 'the string "October 2025" appears on this frame and traces to c2, and the hook names the human factors c29 records rather than repeating the date the dek already carries'
risks:
  - 'a pole against a sky is three boxes on a stick unless every collar is a real assembly'
  - 'the spill cones grey out the frame and the modeled housings stop reading'
```

```yaml
slide: 3
job: >
  Draws the selection that put three products at the border, and physically prevents a reader
  from computing a ratio out of two counts that measure different things.
claims: [c3, c4]
numerals:
  - value_from: c3
  - value_from: c4

composition:
  structure: >
    Dead flat orthographic with zero perspective, an object plane across the upper half and an
    image plane across the lower, split by a hard horizontal break at the element line. This
    content wants an optical layout because a selection IS a filter, and a schematic draws
    selection as physics rather than as a funnel graphic that would invite arithmetic.
  bands: >
    The top third carries six ray bundles entering from the object plane, each labelled, each an
    emissive stroke on baffle black with a modeled falloff along its own length rather than a flat
    line. The middle third carries the element itself, a real optical element with thickness,
    two curved faces and a coating bloom grading across it. The bottom third carries three image
    points landing on drawn knife edge baffles with real thickness, each baffle taking a lit top
    edge and falling to a shaded inner face, with the two carried NEC solutions and the one joint
    Paravision and AiFi solution named on the baffle faces beneath them.
  focal: >
    The optical element in the middle of the frame, the one modeled solid in an otherwise linear
    frame, carrying the coating bloom that is the lightest area on the frame.

art:
  technique: "Line and node as an optical layout, orthographic, emissive stroke, no ground plane"
  why_this_technique: >
    The library's failure mode for line and node is that a line reads as a crack in terrain. There
    is no terrain here at all, and the lines are lifted in value against near black, so the one
    failure the technique has cannot occur.
  palette: "baffle #0D1013 ground, led_cool #C3D4DE rays, housing #2B343E baffles, paint_worn #A9AEA4 labels"
  value_structure: >
    Lightest is the coating bloom across the element at the frame's centre. Darkest is the baffle
    black between the ray bundles. The three image points sit at a mid value so they read as
    landings rather than as sources.
  motion: "Down through the element, six in and three out"

type:
  hook: "Six were invited. Three came south."
  dek: "Six companies were invited to the Maryland Test Facility. Three solutions were carried forward for data collection at the bridge."
  labels: ["SELECTION", "c3 c4", "texasaidocket.com", "03 / 09"]

acceptance:
  - 'exactly six ray bundles enter and exactly three image points land'
  - 'the six and the three never sit on one shared baseline or one shared scale, and a hard horizontal break separates the two planes'
  - 'each of the three landings carries its own name, reading "NEC NSS" twice and "PARAVISION" once, with the full names set as the object plane and image plane captions'
  - 'the optical element is drawn with thickness and two curved faces, not as a single line'
risks:
  - 'a ray diagram reads as generic technology decoration rather than as a selection'
  - 'a reader computes three over six, which would be a ratio of different units'
```

```yaml
slide: 4
job: >
  Shows that the crossing was built twice, once in Maryland to practise on and once as itself,
  and lets the reader find the one line that does not match.
claims: [c30]
numerals: []

composition:
  structure: >
    One point perspective with the vanishing point DEAD CENTRE, deliberately against frame 1's
    off centre construction, with two extruded architectural wireframes of the same footprint
    superimposed on that single vanishing point. This content wants superposition because a
    replica is best drawn by laying it exactly on the thing it copies, and a caption saying they
    match is weaker than a reader seeing where they do not.
  bands: >
    The top third carries the near copy's own soffit, a modeled ceiling taking a cool LED
    gradient across its ribs. The middle third carries a VISIBLE GAP along the axis and then the
    second structure beyond it, at identical station spacing and identical width, one in led_cool
    and one in galv, line only. The gap is what makes two structures two rather than one long
    corridor, and the first render without it read as a single tunnel with two side labels.
    The bottom third carries the shared footprint where the two volumes agree exactly, drawn as a
    modeled floor plane in slab with a low sodium wash graded from the left and the mesh line of
    the near end of both volumes crossing it, so the agreement is a lit surface rather than a
    diagram.
  focal: >
    The near volume's lit soffit, the only closed modeled surface in the frame and the largest
    light area on it, which is what a reader's eye arrives on before it travels down the axis to
    the second structure past the gap.

art:
  technique: "Line and node as ONE architectural geometry drawn twice at two depths on one axis"
  why_this_technique: >
    The claim is a copy and its original. The first build of this frame drew a DIFFERENCE, one
    volume roofed and one open, and a panel found that neither the roof nor the sky is in any
    claim and that the open sky contradicts frame 1's own canopy. A replica is a thing built to
    the same dimensions somewhere else, so the honest drawing is one geometry repeated at two
    depths, with the near copy the one that was built first.
  palette: "river_night #0D1417 ground, led_cool #C3D4DE Maryland and the floor wash, galv #6E7B7E Progreso, slab #2E3130 floor. NO sodium on this frame, because the replica belongs to the test rather than to the bridge, and because frame 1 already owns the orange floor"
  value_structure: >
    Lightest is the Maryland soffit at the top of the frame. Darkest is the open sky above the
    Progreso volume, which is the deck's deepest black. The two wireframes sit between them and
    are separated by hue rather than by value, so neither reads as more real than the other.
  motion: "Along the shared floor to the vanishing point, then up to the ceiling that is only there once"

type:
  hook: "They built the lane twice."
  dek: "A replica of the pedestrian exit environment went up at the Maryland Test Facility first, so the vendors could install and assess their prototypes before taking them to the crossing."
  labels: ["REPLICA", "c30", "texasaidocket.com", "04 / 09"]

acceptance:
  - 'the two wireframes share one vanishing point and one station spacing, differ only in how far along the axis they sit, and are separated by a drawn gap so a reader sees two structures rather than one'
  - 'the labels read "MARYLAND TEST FACILITY, BUILT FIRST" and "PROGRESO BORDER CROSSING", which are the two place names and the order c30 itself carries, and neither asserts a physical property of either place'
  - 'the two wireframes are separated by hue and their median L* values differ by less than 8, so neither reads as more real'
  - 'no fill is used on either wireframe. Line only'
risks:
  - 'two wireframes on one vanishing point read as one confused drawing rather than as two buildings'
  - 'the darkest frame in the deck goes muddy at 432px'
```

```yaml
slide: 5
job: >
  Shows what the software was actually doing, and puts the deck's one bright frame at the seam
  between the built place and the modelled one. THE TURN.
claims: [c15, c18]
numerals: []
breather: false

composition:
  structure: >
    Macro square on at one to one against a transilluminated chrome on glass resolution target,
    with the target's own edges outside the frame, so the reader is standing at the image plane
    rather than looking at an object. This content wants a resolution target because suitability
    for matching is a resolution judgement, and a resolution target is the physical object that
    turns such a judgement into a number.
  bands: >
    The top third carries the coarsest bar groups at full scale, chrome on lit glass, each bar
    with a specular edge highlight that paper cannot make. The middle third carries the middle
    groups and the headline set in the target's own clear field. The bottom third carries the
    finest groups running down to the drawn resolution limit, where the bars stop resolving and
    become a modeled grey field, and the group and element numerals sit beside them as blank
    chrome pads with a lit bevel and a shaded inner face and nothing struck on them.
  focal: >
    The resolution limit picket in the lower right, the largest continuous dark mass on the
    deck's lightest frame, where the bar pitch narrows past the point a pair can be told apart.

art:
  technique: "Chrome on glass resolution target, transmitted light, macro at one to one"
  why_this_technique: >
    The account says the software judged whether images were suitable. It never says suitable at
    what. A target with its numbering removed is that condition drawn rather than argued, and it
    is the one frame in the deck with no drawn light source of its own.
  palette: "glass_lit #F1F4F2 ground, chrome_bar #8E9A9E bars, baffle #0D1013 ink"
  value_structure: >
    Lightest is the transilluminated glass field across the whole frame, which is why this is the
    deck's inversion. Darkest is the resolution limit picket in the lower right, where the pitch
    closes to a solid. No sodium and no LED appears anywhere on this frame, and it is the only
    frame in nine that declares neither.
  motion: "Down through the groups to where they stop resolving"

type:
  hook: "Judged suitable. Suitable at what?"
  dek: "Artificial intelligence and other technologies built a three dimensional model of the capture zone, watched pedestrian movement, and judged whether a face was good enough to match in Customs and Border Protection's Traveler Verification Service. The account gives no rate for how often it was right."
  labels: ["SUITABILITY", "c15 c18", "texasaidocket.com", "05 / 09"]

acceptance:
  - 'the bar groups run in a true geometric progression and no bar is drawn narrower than 5 device pixels at 432px wide'
  - 'every group and element numeral pad is blank, carrying a lit bevel and a shaded inner face and no character, and the string "Traveler Verification Service" appears on this frame because c15 names where the judged image goes'
  - 'this frame''s median L* is above 80 and it is the only frame in the deck above 60'
  - 'no sodium and no LED colour appears anywhere on this frame'
  - 'each chrome bar carries a specular edge highlight, so the frame cannot be read as paper on a light table'
risks:
  - 'moire on the 432px thumb where the fine groups sit'
  - 'a lit flat field reads as deck 14''s light table under a new name'
```

```yaml
slide: 6
job: >
  Carries the record's own countervailing fact, that a lane out was provided for people who
  declined, and is the one frame in nine where every field the drawing offers is filled.
claims: [c13, c14]
numerals: []

composition:
  structure: >
    Plan oblique at forty five degrees from above and behind the mast, looking down two lanes on
    one slab, so the two lanes are seen as equal areas of ground rather than as a diagram. This
    content wants ground rather than a schematic because the opt out is a place a person walks
    rather than a policy, and a schematic would make it a rule.
  bands: >
    The top third carries the far end of both lanes where the two light species meet, with a
    solved overlap term grading between them rather than a hard seam. The middle third carries the
    lane bodies at equal width on the same modeled broom finish concrete, the capture footprint
    drawn as an area of light with no outline anywhere. The bottom third carries the near ends of
    both lanes at the largest scale, the painted lane edge given real thickness with a lit lip on
    its sodium side and a shaded inner face, the concrete tooth coarsening toward the reader, and
    the two language labels set at one shared size on the slab surface.
  focal: >
    The lit capture footprint area in the middle third, the largest area of LED value on the
    frame, which is exactly the ground a person walks out of by taking the other lane.

art:
  technique: "Two computed falloff pools of different species on one slab, with a solved overlap term"
  why_this_technique: >
    The division between the two lanes is drawn IN LIGHT rather than in paint, so the frame states
    the choice without ranking the two options. Any technique that drew a boundary would be
    delivering a verdict the record does not.
  palette: "slab #2E3130, slab_sodium #6E5A40, slab_led #869597, sodium #D9701F, led_cool #C3D4DE, paint_worn #A9AEA4"
  value_structure: >
    Lightest is the LED capture footprint in the middle of the frame. Darkest is the unlit slab
    between the two pools at the frame's edges. The two lanes hold the same width and the same
    surface and differ only in which light falls on them, so no value ranking exists between them.
  motion: "Across the slab from one pool to the other"

type:
  hook: "One lane was provided for saying no."
  dek: "Signs in English and Spanish told pedestrians that United States citizens could opt out. An opt-out lane was provided. The mandate the test serves applies to travelers who are not citizens."
  labels: ["OPT-OUT LANE", "c13 c14", "texasaidocket.com", "06 / 09"]

acceptance:
  - 'the two lanes are drawn at the same width on the same surface and differ only in light species'
  - 'no sign, no placard and no posted notice is depicted anywhere on this frame, and no Spanish lane name is set, because the account says signs were in English and Spanish and never says what they said'
  - 'the capture footprint is an area of light with no drawn outline or stroke around it'
  - 'no person, no face and no body appears anywhere on this frame'
  - 'the painted lane edge has real thickness with a lit lip and a shaded inner face'
risks:
  - 'two lanes drawn unequally deliver a verdict the record does not'
  - 'a lane plan reads as an infographic rather than as ground'
```

```yaml
slide: 7
job: >
  Sets the one direction that is counted beside the one that is not, using the same agency's own
  published series and its own statement about what it does not collect.
claims: [c25, c26]
numerals:
  - value_from: c26
  - computed_by: "out/2026-09-04/compute.py, may_inbound_pedestrians, the published count read out of the fetched data row and given its thousands separator by code"

composition:
  structure: >
    A physical tally register seen at a shallow three quarter oblique, two parallel runs of
    monthly counter drums on one machined plate, the upper run turned to real figures and the
    lower run blank. This content wants a counting machine because the claim is about what gets
    counted, and a bar chart would invite a comparison between a number and an absence, which is
    not a comparison anyone can make.
  bands: >
    The top third carries the register's back plate and the headline, the plate taking a graded
    LED wash across its anodised face with its upper edge lit and its body falling away. The
    middle third carries the upper drum run, the counted direction, each drum a real cylinder with
    a lit crown, a shaded flank and a cast into the plate's channel, every drum the same size,
    because they are the digits of one figure rather than a series of months. The bottom third carries the lower drum run, the uncounted
    direction, identical cylinders in the identical channel with identical lit crowns and shaded
    flanks and no figure struck on any of them, and the register's own machined base below with a
    two part contact shadow on the bench face.
  focal: >
    The struck run of drums across the middle third, the largest area of lit cylinder face on the
    frame and the only place in it where a figure is struck at all.

art:
  technique: "Extruded counter drums in a machined channel, shallow three quarter oblique, two part contact shadows"
  why_this_technique: >
    The library's residual bar is the closest fit and it is wrong here, because there is no
    residual. There is a series and the absence of a series. Identical drums in identical channels
    with one run struck and one run blank is the craft finding executed as an object.
  palette: "housing #2B343E plate, galv #6E7B7E drums, led_cool #C3D4DE crowns and figures, baffle #0D1013 channel floor, sodium #D9701F low fill"
  value_structure: >
    Lightest is the lit crown of the struck run across the middle of the frame. Darkest is the
    channel floor beneath the blank run at the bottom. Every blank drum's crown is lit to the same
    value as a struck drum's crown, so the lower run reads as machinery nobody turned rather than
    as machinery that was removed.
  motion: "Along the upper run to the turned drum, then down to the run that carries nothing"

type:
  hook: "The way in is counted every month."
  dek: "101,306 pedestrians entered the United States here in May 2026, the month the partners were at the bridge. No comparable data is collected on the way out."
  labels: ["BTS BORDER DATA", "c25 c26", "texasaidocket.com", "07 / 09"]

acceptance:
  - 'the string "101,306" appears on this frame with its thousands separator, and matches computed.json may_inbound_pedestrians display'
  - 'the upper drum run carries struck figures and the lower drum run carries none'
  - 'every blank drum draws a lit crown, a shaded flank and a channel floor, and the blank crowns'' median L* is within 6 of the struck crowns'' median L*'
  - 'the frame states that 101,306 is a count of people entering, in words, so it can''t be read as a count of the people the cameras watched'
  - 'the two drum runs are the same length and sit in the same channel geometry'
risks:
  - 'a reader takes 101,306 for the number of faces the cameras captured, which is the most dangerous misread available in this deck'
  - 'an empty run reads as a redaction rather than as a count nobody keeps'
```

```yaml
slide: 8
job: >
  The hero. Shows in one object that the account was cut for eight things and shipped with
  three, by naming each missing measurement in the slot it would have occupied.
claims: [c7, c9, c31, c18, c19, c20, c21, c22]
numerals:
  - computed_by: "out/2026-09-04/compute.py, performance_facts_asked and performance_facts_published, counted over the five named absences each of which carries its own claim"

composition:
  structure: >
    Die-cut foam seen TWELVE DEGREES OFF AXIS, filling the frame edge to edge with no case lip
    and no border, the eight cavities laid in TWO RANKS at two different x origins. The first
    build stacked all eight in one track on one shared left edge and a craft judge read it as a
    bar chart on a single baseline, which is a defect two prior decks record killing in draft.
    Two ranks with no shared origin is what stops a reader measuring a length off it.
  bands: >
    The top third carries the headline over open foam, the material's own sueded surface modeled
    across it with the LED falling from frame left. The middle third carries the two ranks side by
    side, three cavities on the left holding seated anodised plates under the heading STATED, each
    plate throwing a two part contact into its own cavity floor, and the first of the five empty
    ones on the right under the heading NOT STATED. The bottom third carries the rest of the empty
    rank, each cavity with a near side wall falling to near black on its left, a head wall across
    its top, a lit lip on the cut edge and a modeled foam floor lifted well clear of its own
    darkest corner, with the label of what is missing set on that floor.
  focal: >
    The rank of five empty cavities, the largest connected area of the frame and the place the
    light dies inside each opening, which is what the frame came to show.

art:
  technique: "Die-cut closed cell foam cavities at twelve degrees off axis, with a near side wall, a head wall, a lit lip and a modeled floor"
  why_this_technique: >
    Foam is a material no deck here has touched, matte and sueded and light eating, and a cut
    cavity is the one shape that means a thing was expected. A rectangle would be a box and a
    black field would be a redaction, and deck 9's own avoid_next records what that costs.
  palette: "foam #2C312F ground, cavity walls #0B0F0D and #121715, cavity floor #39413C to #2A312D, seated plates #C9D6CE to #8E9C95, led_cool rim"
  value_structure: >
    Lightest is the seated plate face in the first rank, which is where the account's own words
    are. Darkest is the near side wall of each cavity falling away from its lit lip. Every cavity
    floor sits clearly above its own darkest corner, so a hole reads as a hole rather than as
    something struck out.
  motion: "Across the filled rank, then down into the empty one"

type:
  hook: "Eight slots. Three of them filled."
  dek: "Two agencies and one vendor filed a finding. Five measurements were never stated rather than removed."
  labels: ["SLOTS", "c7 c9 c31 c18 c22", "texasaidocket.com", "08 / 09"]

acceptance:
  - 'exactly three cavities are filled and exactly five are empty, and all eight openings are the same size'
  - 'the five empty cavity labels read "ACCURACY RATE", "IMAGES CAPTURED", "RETENTION PERIOD", "DEPLOYMENT DECISION" and "ASSESSMENT DATES"'
  - 'the three seated plates read "EXCEEDED EXPECTATIONS", "HIGH-QUALITY FACIAL IMAGES" and "IT DID JUST THAT", every one a literal substring of a quote in claims.json, and each names its speaker beneath it as "CBP", "NEC NSS" and "S AND T" so a vendor describing its own product is not drawn as a government finding'
  - 'the eight cavities sit in two ranks of three and five at two different x origins, so there is no shared baseline a reader could measure a length against, and no empty cavity appears under the heading STATED'
  - 'every cavity shows a near side wall 40px wide and a head wall 40px deep, both real quadrilaterals with area rather than a hairline and a bar, and every cavity floor is DARKER than the foam around it and lighter than its own walls'
  - 'no empty cavity is drawn as a flat black rectangle, and every one carries a lit lip and a modeled floor'
  - 'the dek says the five measurements were never stated RATHER THAN REMOVED, so absence can not be read as redaction'
risks:
  - "a dark cavity reads as a redaction, which would accuse somebody of removing what was never written"
  - "eight cavities at 432px collapse into a grid of dark tiles"
  - "the three seated plates line up and read as bars, which is what the first build did"
```

```yaml
slide: 9
job: >
  Leaves the reader with the only dated public room the record actually holds, and says in the
  drawing itself that it does not open onto this test.
claims: [c32, c23, c24]
numerals:
  - value_from: c24

composition:
  structure: >
    A two point oblique into a sealed instrument housing with no ground plane, carrying two
    collimated axes that are not coplanar, so they pass each other and never cross. This content
    wants non intersection because the hardest thing to say in words, that the dated room belongs
    to a different program, is the easiest thing to draw as geometry.
  bands: >
    The top third carries the housing's upper interior and the headline, the anodised wall taking
    a graded fall from a lit upper corner into its own shade. The middle third carries the two
    axes crossing the frame at different depths, each a real beam with a modeled falloff along its
    length, each seated between drawn physical stops. The bottom third carries the two terminations
    on the housing's lower interior wall, the Dallas axis landing on a lit aperture plate with a
    cut edge, a bevel and a modeled inner face carrying the date, and the Progreso axis landing on
    a blank baffle with no aperture cut in it at all, its surface modeled in the same anodised
    material so the absence of an opening is the only difference between them.
  focal: >
    The lit aperture plate in the bottom third, the brightest area on the frame, which is the one
    opening a reader can actually walk through.

art:
  technique: "Two non-intersecting collimated axes terminating on drawn apertures inside a housing"
  why_this_technique: >
    Every other closing frame this deck could have drawn would put the Dallas date and the
    Progreso test in one picture and imply a connection. Two beams that pass and never meet says
    the opposite, and says it before the copy does.
  palette: "baffle #0D1013 ground, housing #2B343E walls, led_cool #C3D4DE beams and aperture, galv #6E7B7E stops"
  value_structure: >
    Lightest is the lit aperture plate at the bottom of the frame. Darkest is the blank baffle
    beside it, which is the same material with no opening in it. The two beams sit at a mid value
    so neither competes with the aperture.
  motion: "Along both beams to two different terminations"

type:
  hook: "The only date belongs to Dallas."
  dek: "The account announces no comment period, no hearing and no docket. The nearest dated room in this record is a different program. Dallas takes a briefing on its police Flock plate readers on September 8th, 2026."
  labels: ["DIFFERENT PROGRAM", "c21 c23 c24", "texasaidocket.com", "09 / 09"]

acceptance:
  - 'the two axes are drawn at different depths and do not intersect anywhere in the frame'
  - 'the string "September 8th, 2026" appears on this frame and is set in led_cool #C3D4DE'
  - 'the reserved red #BF0A30 appears nowhere on this frame or anywhere in the deck'
  - 'the Progreso termination is a BLANKED OPENING with the same lit lip, side wall and floor as the aperture beside it and nothing going through, never a flat dark rectangle, because the deck''s own third law says absence is drawn as a lit slot'
  - 'the frame states in words that the Dallas briefing is a different program'
risks:
  - 'two glowing lines read as science fiction rather than as an instrument'
  - 'a reader takes the Dallas date as a door onto Progreso, which is the one thing this frame exists to prevent'
```
