# Storyboard, deck no. 11, August 29th 2026

Story: the National Science Foundation's Center for Human and Robot Co-Adaptation at the
University of Texas at Austin, `tx-2026-0104`. Every fact traces to `out/2026-08-29/claims.json`.
Every numeral traces to `out/2026-08-29/compute.py`, which reads that file and refuses a figure it
can't find in a quote.

## The synthesis, and what each room contributed

Three directors ran on three lenses. Two of them independently arrived at interiors, and both of
those independently reported the same constraint from the ledger, so it is recorded first because
it bounds every other decision here. **`ledger_check` reads `LIGHT_L = 60.0` against
`value.deck_median_L` and the light deck cap is already spent**, twice, inside the eight run
window. This deck is planned mid dark and its measured median has to come in under sixty.

**The concept comes from the person room, and it is one object.** An empty day room chair with
the afternoon slat light bending across the dish a body left in the cushion. Presence recorded by
a material, without anybody being asked. That is this story's argument in a single picture and
neither of the other rooms produced anything as strong.

**The argument's spine comes from the document room.** One deployment, three documents, and the
biggest type on the page names the fewest rooms. The agency's release names four settings, the
agency's own award abstract names three facility types, and the university names six places, one
of which is a rehabilitation hospital. Setting all three between the same two margins at three
sizes makes the finding unarguable without a single number carrying it.

**That room also produced the sentence that keeps this deck honest**, and it ships on the hero
frame. *The most specific list is the awardee's own.* Nothing here was concealed and a deck that
implied otherwise would be wrong on the facts.

**The register comes from the room lens and the person lens together**, and the person lens wins
the palette, because "an assisted living day room in Central Texas in late August with the west
blinds shut" is a real material world and "institutional corridor grey" is a mood.

**What was rejected, and why.** The room lens wanted three orthographic floor plans as the hero.
Its own risk list names the reason not to: the plans need furniture no source describes, and this
record's whole promise is that it draws only what a document names. The document lens wanted all
nine frames typographic, which its own risk list calls a flat strip. The person lens wanted a
digital twin frame built from `c27`, cut because a lattice over a chair is the one cliché in this
subject and `c27` is a side fact.

**One thing all three rooms got right and it is in the laws below.** No robot is drawn anywhere in
this deck. No document in this record describes what any machine looks like.

## The laws this deck is held to

1. **No person, no robot, no sensor and no machine is depicted on any frame.** Presence is drawn
   only as the mark a body leaves on a material. Compression, polish, burnish, a rail at a height
   built for a hand.
2. **The room is register and never evidence.** A drawn chair, ceiling, floor or door asserts
   nothing about any site. Every fact on a frame is carried by text with a claim id, and every
   quoted string is verbatim.
3. **No arithmetic on the money.** Three quoted strings at identical weight, and nothing between
   any two of them that implies order, difference or reconciliation. The frame prints that rule.
4. **One light, one azimuth.** An August afternoon through a shut west blind, from frame left.
   Frame 7 carries no light at all and says so by construction. Frame 9 carries a second light
   from outside the room and that is the whole point of it.
5. **Nothing carved, milled, engraved or embossed.** Depth here is compression, transmission,
   orthographic line weight and specular return. This is what separates the deck from nos. 6, 8
   and 9 at a glance.
6. **Every count names the set it counted**, in the counting document's own words, and every count
   is `len()` of a list `compute.py` split out of a quoted string.
7. **No numeral is typed.** Slat pitch, cushion depth, rail height, ceiling module, bar lengths and
   every plate width come from `computed.json`.
8. **The reserved red is spent once**, on `September 1st, 2026` on frame 9, and appears nowhere
   else in nine frames.
9. **Every headline sits on a scrim or a plate.** The run's own smoke test put a canvas field
   under a headline and `qa.py` returned seven strikethrough failures on one line.
10. **No cartography, no county, no coordinate.** The record names Austin and nothing finer.

## The palette

Source: an assisted living day room and a rehabilitation corridor in Central Texas at four in the
afternoon in late August, with the west blinds shut, plus the drawings that describe such a room.

| token | hex | what it is |
|---|---|---|
| `blind_gold` | `#F2D48E` | direct sun through one slat. The deck's light and its only saturated warm |
| `vct_wax` | `#EDE7D2` | vinyl composition tile returning that slat light |
| `vct_pale` | `#C6C3B4` | the same tile in ambient |
| `wall_greige` | `#9A9789` | painted gypsum in a shaded room |
| `stainless` | `#ADB1AE` | grab bar, door hardware, closer arm |
| `oak_rail` | `#A87C4C` | the laminate handrail. Frame 6 only, the deck's one wood tone |
| `vinyl_blue` | `#5E7183` | wipe clean upholstery. Frames 1 and 8 only |
| `shade` | `#202629` | the room with the blinds shut. A cool near black, deliberately not no. 10's warm dark |
| `graphite` | `#4E5257` | line and rule on the dark frames |
| `bond` | `#E4E4DE` | laser bond. Frame 7 only |
| `blueline` | `#2C4C86` | diazo print ink. Frame 7 only |
| `flag_red` | `#BF0A30` | reserved. Frame 9 only, on the date |

## The value arc

Planned per frame 32, 40, 28, 26, 24, 40, 68, 30, 38. Planned deck median near 32, decisively mid
dark, which clears `LIGHT_L`. **This block is a plan. The ledger entry takes its measurement off
the rendered thumbs and never off this page.**

```yaml
slide: 1
job: >
  The cover, and the deck's whole argument in one object. A room the record names, with the shape
  of a person in it who was never asked, drawn entirely by the way the light bends.
claims: [c21, c22, c35]
numerals:
  - value_from: c8
  - computed_by: "compute.py, award_date from the award record's own date field, formatted to house style"
composition:
  structure: >
    The chair is square on at seated eye height, so the reader is looking at it from the height of
    the chair opposite rather than standing over it. It fills the middle band and its feet sit on
    lit tile in the lower band, because a chair floating in a dark field is a product photograph
    and a chair on a lit floor is a room.
  bands: >
    The top third carries the masthead over the shaded wall, unlit, plus the headline on its
    scrim. The middle third is the chair itself with nine slat bands crossing it, and it is where
    the deflection happens. The bottom third is lit vinyl composition tile carrying the two part
    contact shadow, the quoted consent sentence and the foot.
  focal: >
    The seat cushion read as a lit area, not as the stripes themselves. It is the region where
    `blind_gold` lands broadest and it is the only place in the frame where the light is
    interrupted by a shape, so the eye goes there and finds the interruption.
art:
  technique: "TX.reliefShade over a authored cushion heightfield, with the slat light as a projected contour set, and a TXCARVE two part contact shadow onto a floor lit first"
  why_this_technique: >
    The claim is that the rooms are named and the consent procedure is not written yet, so the
    person in the room is exactly the thing the record does not contain. A compression map is a
    body recorded by a material without anybody being asked. Drawing the depression as a bend in
    nine stripes rather than as shading is also the only version that survives the reduction to
    432px, because a shading gradient at that size is a smudge and a bent line is still a bent line.
  palette: "vinyl_blue, blind_gold, vct_wax, shade, stainless. An assisted living day room with the west blinds shut"
  value_structure: >
    Lightest is the `blind_gold` slat band where it crosses the seat and the lit tile below the
    chair. Darkest is the shaded wall behind, in `shade`, which carries no slat light at all
    because the blind is between it and the window.
  motion: "in along the slat bands from frame left, arrested at the seat where they bend, then down the chair leg into its own shadow"
type:
  hook: "The rooms are named. Consent is not."
  dek: "The university's own account names the rooms. Houses, dorms, cafes, a public museum and a rehabilitation hospital."
  labels: ["NSF AWARD 2535195", "c21 c22 c35", "texasaidocket.com", "01 / 09"]
acceptance:
  - "the slat bands crossing the SEAT deflect by at least 14 px at 2160 wide and at least 3 px on the 432 thumb, and the bands crossing the BACKREST are dead straight, both asserted by the frame's own script. A craft judge read the first version as wavy upholstery because every band bent, which is not what a flat back panel does to a line of light"
  - "the floor inside the contact zone is LIT before the shadow is cast, so the two part contact shadow has a lit ground to subtract from rather than a dark one, which the frame draws in that order rather than asserting in prose"
  - "the headline sits on a scrim and qa.py reports zero `text struck by a drawn rule` failures on this frame"
  - "no person, no robot and no machine appears anywhere on this frame"
  - 'the dek carries "a rehabilitation hospital" and names the six places in the university''s own order'
risks:
  - "the deflection is under 3 px on the thumb, at which point this is a picture of a chair and the deck has no hook"
  - "the chair reads as sentimental. The guard is that no caption interprets it and the only quoted sentence is c22 in its own future tense"
```

```yaml
slide: 2
job: >
  The hero. Sets all three documents' descriptions of the same deployment on one shared
  measure at three sizes, so the reader sees that the biggest type names the fewest rooms without
  a single number carrying the argument.
claims: [c33, c15, c21]
numerals:
  - computed_by: "compute.py, n_release_settings as len() of the list split out of c33's own quote"
  - computed_by: "compute.py, n_abstract_facilities as len() of the list split out of c15's own quote"
  - computed_by: "compute.py, n_university_places as len() of the list split out of c21's own quote"
composition:
  structure: >
    Three horizontal bands sharing one measure between x=96 and x=984, closed top and bottom by a
    rule and separated by hairlines. One measure is what makes the comparison fair, and three
    sizes solved by TX.fitText to fill that measure is what makes it unarguable. The document that
    says least is set largest, at the top, where a reader starts.
  bands: >
    The top third is band one, the agency's release, one line at the largest size in the deck. The
    middle third is band two, the agency's own award abstract, wrapping to two lines. The bottom
    third is band three, the university's list at the smallest size, and it is the only band with
    modeled ground under it. A soft wash grades the `shade` field darker toward the frame foot, and
    a low amplitude grain runs over the whole of that wash so the smallest type sits in a lit
    depth rather than on a flat plate, with the three mono attributions and the fairness line
    reading against that graded texture. That texture ends at y=1078, where the sheet the three
    lists are printed on is trimmed. Below the trim is the surface it was set down on, darker and
    coarser, carrying the sheet's cast and nothing else. Three documents is the frame's subject, so
    the frame is a document, and the last 270 px is the object rather than an empty gradient.
  focal: >
    Band one's single line, read as a light area rather than as letterforms. It is the largest
    contiguous region of `vct_wax` on the frame and it sits on the deck's darkest ground, so it
    wins the eye and then disappoints it, which is the frame's whole job.
art:
  technique: "three simultaneous type scales on one shared measure, solved by TX.fitText, over a mid century oil chart rule band with 2px rules top and bottom and hairlines between"
  why_this_technique: >
    This is the only construction in which the entire argument is one image. Any chart of three
    counts would put a number in the largest type on the page and this deck's law is that the
    count names its set. Setting the actual words at three solved sizes lets the reader do the
    comparison directly, and the ruled band is the register a record product earns honestly.
  palette: "shade ground, vct_wax for band one, vct_pale for band two, wall_greige for band three, graphite rules, blind_gold on the rehabilitation hospital phrase only"
  value_structure: >
    Lightest is band one's type, and it descends band by band so the type gets both smaller and
    dimmer as the documents get more specific. Darkest is the `shade` ground. The one exception is
    `a rehabilitation hospital` in band three, lifted to `blind_gold`, because it is the phrase
    that exists in one document and in neither of the others.
  motion: "top to bottom, large to small, light to dim, which is the specificity gradient running the wrong way round"
type:
  hook: "Same deployment. Three grains."
  dek: "The most specific list is the awardee's own."
  labels: ["NSF release, c33, 4 settings", "NSF abstract, c15, 3 types", "UT Austin, c21, 6 places", "texasaidocket.com", "02 / 09"]
acceptance:
  - "all three bands are set between x=96 and x=984 and each band's laid out line width is within 12 px of that measure"
  - "band one's type size is strictly greater than band two's, and band two's strictly greater than band three's, asserted by the frame's own script off getBoundingClientRect"
  - 'each attribution carries "4 settings" or "3 types" or "6 places" beside the document it counted, so no count on the frame is a bare number'
  - 'the frame carries "a rehabilitation hospital" and it is the only string on the frame in blind_gold #F2D48E'
  - 'the dek reads "The most specific list is the awardee''s own."'
  - "no numeral on this frame is absent from computed.json"
  - "the sheet's trimmed edge crosses the full frame width at y=1078 with a lit paper thickness above it and a cast below it, and it is not a straight line at any x"
  - "no word and no numeral appears anywhere below the trimmed edge except the foot"
risks:
  - "band three goes sub legible at 432. It is DOM text at any size, the six places are restated at reading size on frame 1's dek, and what has to survive the thumb is the three sizes and the one lifted phrase"
  - "the frame reads as an accusation. The dek is the guard and it ships as written"
```

```yaml
slide: 3
job: >
  Says what "always on" actually means to somebody lying under it, by drawing the layer of a
  building that already never switches off, and puts the five year span on the frame.
claims: [c15, c16, c7, c35]
numerals:
  - value_from: c7
  - computed_by: "compute.py, end_date from the award record's expDate, formatted to house style"
composition:
  structure: >
    Looking straight up. There is no horizon anywhere on this frame and no floor, which is the one
    orientation in the deck that removes the reader's footing, and it is the orientation a person
    on a ward actually has.
  bands: >
    The top third is ceiling grid receding toward the wall head, with the thin bright line above
    the blind head rail at the very top. The middle third is the open field of tile carrying the
    quoted phrase on its plate. The bottom third is the deepest tile in the room, where the stipple
    runs at its coarsest and the bounce light dies into an unlit corner, so the band carries a real
    tonal gradient rather than a caption. The diffuser, the sprinkler and the detector sit in it,
    each with its own soft cast shadow across the tile face, and their leader lines run down
    through that graded texture into the foot.
  focal: >
    The lit band of tile immediately below the blind head rail, an area of `vct_pale` at the
    frame's light extreme, which is where the only daylight in the room reaches the ceiling.
art:
  technique: "stipple field at true fissure density over a computed 24 by 48 inch lay in grid, one soft bounce gradient, TX.canvasLabel knockout callouts"
  why_this_technique: >
    The claim is that the deployments are always on and grow more complex for five years, and the
    honest picture of always on is the layer of a building that has always been always on. The
    sprinkler, the diffuser and the smoke detector are already there and nobody consented to those
    either. Stipple is the right mark because a mineral fibre tile IS a stipple field, so the
    texture is the material rather than a treatment applied to it.
  palette: "vct_pale for the tile, wall_greige for the grid tee, shade in the corners, blind_gold on the head rail line only, stainless on the fixtures"
  value_structure: >
    Lightest is the head rail line and the tile band under it. Darkest is the far corner of the
    ceiling where the bounce does not reach. The fixtures sit mid, in `stainless`.
  motion: "up and outward from the lit head rail band into the darker field, along the grid tees"
type:
  hook: "Always on. Increasing in complexity."
  dek: "The agency's own abstract calls the sites \"always-on, participatory living laboratories\", and says the deployments \"will increase in complexity over the Center's duration\"."
  labels: ["SPRINKLER", "DIFFUSER", "SMOKE DETECTOR", "c15 c16", "texasaidocket.com", "03 / 09"]
acceptance:
  - "no periodic stripe appears anywhere on this frame, which is what separates it from frames 1 and 8"
  - "the ceiling grid lines land on the module compute.py emitted and no grid pitch is a typed pixel value"
  - "the stipple is visibly non uniform at 432 px and the canvas clears craft_floor's variance floor"
  - "each of the three callouts terminates on its own fixture's coordinates and declares them through window.__txLeaders"
  - 'the dek carries "always-on, participatory living laboratories" and carries "will increase in complexity"'
risks:
  - "a ceiling is a boring picture. It survives on the fissure texture being real and on the callouts naming things a reader recognises from a waiting room"
```

```yaml
slide: 4
job: >
  Shows the award record as the thing it actually is, a machine readable file, and names the one
  field on it that most readers would get wrong. It is a cooperative agreement and not a grant.
claims: [c10, c11, c2, c12, c6, c7, c8, c35]
numerals:
  - value_from: c6
  - value_from: c7
  - computed_by: "compute.py, start_date and end_date from the record's own fields, formatted to house style"
composition:
  structure: >
    A dead flat character field filling the frame at 4px line height, composed only of characters
    present in the fetched response, with six rows lifted to full glyph scale. The scale break IS
    the citation, because a field only means anything inside the file it lives in.
  bands: >
    The top third is dense field with the masthead over it. The middle third carries the six lifted
    rows on their knockout plates, which is the only legible text in the field. The bottom third
    returns to the character field at its full density, and it is treated as a texture rather than
    as a backdrop. A wash grades it darker toward the frame foot and a grain sits over it, so the
    hook's scrim has modeled tone to sit in and the field reads as depth falling away under the
    citation rather than as a flat pattern behind a caption.
  focal: >
    The block of six lifted rows, read as one lit rectangle against the noise. It is the largest
    contiguous area of `vct_wax` on the frame and the only place a reader can land.
art:
  technique: "a dead flat character field at 4px line height as a decorative texture, with six DOM text rows at full scale on TX.svgPlate knockout plates"
  why_this_technique: >
    The whole content of c10 is one field on one record, and a field pulled out and set as a
    headline is an assertion about a document a reader cannot see. Leaving it in its file, at its
    real density, and lifting only what is cited, is the honest version and it is also the only
    frame in the deck whose texture is literally its evidence.
  palette: "shade ground, graphite for the field, vct_wax for the lifted rows, blind_gold on the transType value only"
  value_structure: >
    Lightest is the six lifted rows. Darkest is the ground the field sits on. The field itself is
    held between 1.6 and 2.4 to 1 against that ground so it reads as text texture rather than as a
    pattern.
  motion: "the eye is refused by the field and settles on the lifted block, which is the intent"
type:
  hook: "It is not a grant."
  dek: "The instrument on the record is a cooperative agreement and not a grant. The record's own field says so."
  labels: ["\"transType\":\"Cooperative Agreement\"", "\"fundProgramName\":\"STCs - 2026 Class\"", "c10 c11 c2 c12 c6 c7", "texasaidocket.com", "04 / 09"]
acceptance:
  - "the character field is marked data-decorative and contains at least 4000 characters, all of which appear in the claim quotes this frame cites"
  - "exactly seven rows are lifted to full glyph scale and each is DOM text byte identical to a substring of its claim's quote"
  - 'the frame carries "Cooperative Agreement" at full glyph scale and carries "perfCity":"AUSTIN", which is the one place this deck names'
  - "the field measures between 1.6 and 2.4 to 1 against its ground, asserted off the render"
  - "no lifted row is overprinted by any other element, and qa.py reports zero occlusion failures"
risks:
  - "the field reads as a hacker motif. The guards are the low contrast ratio, the character set assertion and the fact that the only legible thing on the frame is six cited rows"
```

```yaml
slide: 5
job: >
  Puts the money on the record without doing anything to it. Three quoted strings from three
  documents at identical weight, in a room that is almost empty, because the money is the one part
  of this story that never enters the room.
claims: [c3, c20, c31, c30, c5, c10, c35]
numerals:
  - value_from: c3
  - value_from: c20
  - value_from: c31
  - value_from: c30
  - value_from: c5
composition:
  structure: >
    Level across an empty room at seated eye height with a deep field, and the ruled money band
    staggered low across the floor plane in the lower third. The subject is absent and the composition
    is the emptiness, which is the doctrine's most under used move and the right one for a figure
    nobody in the room will ever see.
  bands: >
    The top third is the thin bright line above the blind head rail and the shaded upper wall,
    carrying the masthead and the hook on its scrim. The middle third is wall, cove base and the
    slat gradient reaching the floor, each slat carrying a lit lip and the next slat's shadow. The
    bottom third is three staggered plates, the dek on its own plate, and the foot.
  focal: >
    The three plates, read as three separate lit areas at three different origins, because they
    are the only hard edged construction in an otherwise soft frame. Three, never one band.
art:
  technique: "the Marfa empty field with a computed slat gradient, plus three separate toothed plates at three different left origins, JetBrains Mono, with no shared axis and nothing drawn between any two"
  why_this_technique: >
    THIS BLOCK IS THE ROUND ONE HARD FAIL, KEPT RATHER THAN QUIETLY REPLACED. It read that
    tabular numerals let a reader compare two figures by eye and that the alignment does the work
    the arithmetic is forbidden to do. That is the comparison this deck is forbidden to invite,
    planned in as a feature, and an integrity judge found the frame drawing it with a hairline
    between each pair. Three quoted strings from three documents are not commensurable and the
    layout may not suggest they are. Three plates at three different left origins, no shared left
    or right, nothing between any two, and the frame asserts all of that off getBoundingClientRect
    rather than trusting the plan to have stayed true. The empty room is what says the money is
    not in it.
  palette: "shade, wall_greige, vct_pale, blind_gold on the head rail line, graphite for the rules"
  value_structure: >
    Lightest is the head rail line at the top and the ruled band's rules at the bottom. Darkest is
    the corner of the room away from the window. Nothing in the middle competes, deliberately.
  motion: "across the room from the lit left toward the dark right, then down the staggered plates"
type:
  hook: "The size as each document gives it."
  dek: "Each figure is quoted from the document named beside it. Nothing here converts one into another."
  labels: ["\"estimatedTotalAmt\":\"29999998\"", "five-year, $30 million award", "approximately $6 million annually", "c3 c20 c31", "texasaidocket.com", "05 / 09"]
acceptance:
  - "no two plates share a left origin and no two share a right edge, asserted by the frame's own script off getBoundingClientRect"
  - "no rule, tick, arrow, bracket or connector sits between any two of them, asserted by the frame rather than eyeballed"
  - "each plate carries its own document name and claim id at the same mono size"
  - 'the dek reads "Each figure is quoted from the document named beside it. Nothing here converts one into another."'
  - "all three horizontal bands carry work and the canvas clears craft_floor's variance floor"
  - "no numeral appears on this frame that is not a substring of a claim quote in claims.json"
risks:
  - "a judge DID read the comparison into it in round one, drawn by an axis the plan called a feature. Kept here as the record of what the risk section got wrong: it named the right danger and then prescribed the layout that caused it"
  - "the empty room reads as unfinished. All three bands must carry real material variance rather than a gradient"
```

```yaml
slide: 6
job: >
  The turn. Carries the university's own promise of community influence at full size and in the
  deck's only warm hue, so the deck argues both ways rather than reading as a prosecution.
claims: [c23, c26]
numerals:
composition:
  structure: >
    A square on elevation of one corridor wall running off both frame edges, so the rail has no
    beginning and no end inside the frame. A handrail is the one piece of a building designed
    entirely around a body that is not depicted, and it is present at every step, which is the
    sentence this frame carries.
  bands: >
    The top third is upper wall carrying the masthead and the hook. The middle third is the rail
    itself with its brackets and the burnish band above it, plus the quote on its measured plate.
    The bottom third is the lower wall, where the wall's lit gradient falls off below the rail and
    each bracket's two part contact shadow reaches down into it, ending on the rubber cove base
    which carries its own dark under edge and a grain over the paint. The foot sits on that graded
    lower wall rather than on a plate.
  focal: >
    The lit top edge of the rail, read as a continuous band of `oak_rail` at the frame's warm
    extreme, running the full width. It is the lightest warm area in the frame and the only
    saturated thing on it.
art:
  technique: "TX.reliefShade on a round rail section so it carries a lit top edge and a dark under edge, with two part contact shadows from each bracket onto a wall lit first, and TX.svgPlate sizing the quote plate from its own laid out lines"
  why_this_technique: >
    The claim is a promise about people being able to influence deployment at every step. A rail is
    a thing a person's hand is on at every step, and it is the only object in this deck that a
    building puts there for a body rather than for a system. A ridge has two edges, and a rail
    drawn as one stroke is a line.
  palette: "oak_rail, wall_greige, stainless on the brackets, blind_gold in the burnish band, shade in the cove"
  value_structure: >
    Lightest is the rail's lit top edge. Darkest is the underside of the rail and the cove base
    below. The wall sits mid, lit first so the bracket shadows have something to subtract from.
  motion: "along the rail, left to right, off both edges"
type:
  hook: "Every step of the way."
  dek: "\"Every step of the way, community members will have an opportunity to influence how, when and where robots get deployed\""
  labels: ["GOOD SYSTEMS", "c23 c26", "texasaidocket.com", "06 / 09"]
acceptance:
  - "the rail reads as a cylinder with at least three distinct value steps across its section and its lit edge on the deck's declared azimuth"
  - "the bracket spacing comes from computed.json and no bracket x position is a typed pixel value"
  - "the wall inside each bracket's contact zone is lit before the shadow is cast, which the frame does by painting the gypsum and its lamp first and subtracting the casts after"
  - 'the frame carries "Every step of the way, community members" as DOM text, never canvas fillText'
  - "oak_rail #A87C4C appears on this frame and on no other frame in the deck"
risks:
  - "the turn gets cut in a later round and the deck becomes an accusation. It must not ship in that state"
```

```yaml
slide: 7
job: >
  Sets a thing a drawing can specify to the degree beside a thing the record says is still to be
  written, in one drawing convention, so the absence is structural rather than rhetorical. The
  deck's only frame with no light source.
claims: [c22, c35]
numerals:
composition:
  structure: >
    No camera at all. A quarter inch orthographic plan detail of one doorway on a bond sheet, with
    a drawing sheet title block. A plan can specify a door swing to the degree and cannot specify a
    consent procedure that has not been written, and putting the two in the same convention is the
    argument.
  bands: >
    The top third is bond with the sheet's north arrow and the masthead. The middle third is the
    doorway detail, jamb, leaf, swing arc and the 45 degree clear floor hatch. The bottom third is
    the title block carrying c22 whole, the scale note and the foot.
  focal: >
    The 45 degree hatched clear floor area inside the swing, read as a mid toned area on the light
    bond. It is the largest patterned region on an otherwise open sheet and it is what the drawing
    reserves for a body.
art:
  technique: "orthographic line weight hierarchy authored in SVG, diazo blueline on bond, cut lines heaviest at the jamb, leaf lighter, swing arc a hairline dash, clear floor a 45 degree hatch, with a drawing sheet title block"
  why_this_technique: >
    Line weight is the only depth cue on this frame and it is the correct one, because a plan has
    no light in it. The record product earns the engineering drawing register honestly, and this is
    the one frame where the convention itself is the point rather than the styling.
  palette: "bond ground, blueline for every line and every character, graphite in the title block rules only"
  value_structure: >
    Lightest is the open bond of the corridor side. Darkest is the poched jamb. This is the only
    frame in the deck whose ground is light, and it is the deck's value inversion.
  motion: "along the swing arc from the latch to the jamb, into the title block"
type:
  hook: "The swing is drawn. The procedure is not."
  dek: "\"An internal ethics board will oversee the research and develop consent and opt-out procedures.\""
  labels: ["SCALE ONE QUARTER INCH TO ONE FOOT", "LEAF WIDTH", "CLEAR FLOOR AREA", "c22", "texasaidocket.com", "07 / 09"]
acceptance:
  - "at least four distinct stroke weights are measurable off the SVG"
  - "the swing arc terminates on the leaf's own computed latch coordinate and declares it through window.__txLeaders"
  - "nothing on this frame is a filled black rectangle, because a black field reads as a redaction and the record says nothing was removed"
  - "the frame declares no light source and carries no gradient, shadow or specular anywhere"
  - 'the title block carries "An internal ethics board will oversee the research", whole and verbatim'
risks:
  - "the light ground pulls the deck median up. It is one frame of nine and the arc is planned around it"
  - "it pairs with frame 4 in bespoke_check. They are separated by light physics, hue, ground value and mark, and by two frames in the sequence"
```

```yaml
slide: 8
job: >
  Says the adaptation runs both ways, which is the half of the director's own sentence everybody
  drops, by drawing behaviour recorded in a floor.
claims: [c24, c25, c35]
numerals:
composition:
  structure: >
    A grazing sight line along the floor plane at ankle height, so the tile is seen almost edge on
    and the specular return is the only thing carrying information. This camera is a consequence
    of the claim rather than a choice, because grazing incidence is physically the only way a wear
    path in floor wax is visible at all.
  bands: >
    The top third is the far wall and the baseboard, dark, carrying the hook on its scrim. The
    middle third is the receding floor where the path is broadest and brightest. The bottom third is
    the near floor at the heaviest mark weight in the frame, where the wax grain is coarsest, the
    tile joints are widest and the path's sheen opens out toward the reader before running off the
    bottom edge. The quote and the foot sit on that near field texture.
  focal: >
    The walked path itself, read as a broad lighter area of sheen down the middle distance of the
    floor. It carries the frame's light extreme and it has no drawn edge anywhere.
art:
  technique: "a computed specular lobe at grazing incidence over a wear heightfield, TX.reliefShade as the base, TX.grainTile over the wax"
  why_this_technique: >
    The director's own sentence says people adapt their behaviour when they integrate robots into
    their environment. A path polished into floor wax is exactly that, behaviour recorded by a
    material at room scale, and it is frame 1's cushion argument enlarged from one body to
    everybody who has walked there.
  palette: "vct_wax on the path, vct_pale off it, shade at the baseboard and in the doorway recess on the far wall"
  value_structure: >
    Lightest is the sheen on the path. Darkest is the baseboard and the wall above it. The
    difference between path and floor is sheen only and never a drawn line.
  motion: "down the path into the depth of the corridor, past the doorway recess on the far wall"
type:
  hook: "People adapt too."
  dek: "\"while recognizing that people also adapt their behavior when they integrate robots into their environment\""
  labels: ["UT AUSTIN, c24", "NSF AWARD 2535195", "c24", "texasaidocket.com", "08 / 09"]
acceptance:
  - "the path is a sheen differential against the surrounding wax, MEASURED off the canvas by the frame's own probe at two sample points and thrown if the two are not separated, with no drawn edge anywhere"
  - "the path curves around nothing depicted, because nothing is depicted"
  - "no machine, no person and no sensor appears on this frame"
  - 'the frame carries "people also adapt their behavior" and attributes it to UT AUSTIN, the document, because no fetched span in claims.json names a speaker for that sentence. Round 3 hard failed this frame for printing a title the evidence layer had laundered in from a claim text'
risks:
  - "at 432 px the path vanishes and the frame is a picture of a floor. The separation is measured on the thumb, not at full size"
```

```yaml
slide: 9
job: >
  The close, and the only frame carrying a next step a reader can take. The deck's only second
  light source, arriving from outside the room.
claims: [c6, c12, c22, c2, c25, c35]
numerals:
  - value_from: c6
  - computed_by: "compute.py, start_date from the record's startDate, formatted to house style"
composition:
  structure: >
    A two point perspective interior corner with a door standing open onto a lit corridor. Eight
    frames have had one light and one room. The close is the only frame where light arrives from
    somewhere else, and an open door is this deck's argument resolved into a step rather than a mood.
  bands: >
    The top third is the dark upper corner and the door head, carrying the masthead. The middle
    third is the open leaf and the lit corridor slot, which is where the date sits. The bottom third
    is the floor, and it carries the frame's only graded light. The spill wedge from the opening
    falls across it as a real gradient, the leaf's two part contact shadow is cut into that lit
    ground, and a grain runs over the whole floor plane. The next step lines and the foot read
    against that wedge.
  focal: >
    The lit corridor slot in the opening, an area at the frame's light extreme against the deck's
    darkest near plane. It is the brightest region on the frame and the date sits on it.
art:
  technique: "two point perspective solved arithmetically before rendering, a computed spill wedge from the lit aperture onto floor and near wall, a two part contact shadow where the leaf meets the floor, and the reserved red as ink on the lit slot"
  why_this_technique: >
    The claim is that the work starts on a dated day, the procedures do not exist yet and the
    university has promised people a say. An aperture is the only construction that can be dark,
    light and directional at once, and the date has to sit on the light for the reserved red to be
    legible at all.
  palette: "shade on the near plane, vct_wax in the slot, blind_gold in the spill wedge, stainless on the hardware, flag_red on the date only"
  value_structure: >
    Lightest is the corridor slot. Darkest is the near door leaf, which is the frame's foreground
    and carries no light at all. The spill wedge grades between them on the floor.
  motion: "through the opening, out of the room the deck has spent eight frames inside"
type:
  hook: "September 1st, 2026."
  dek: "The work starts that day. The consent and opt-out procedures are still to be developed."
  labels: ["One door, and a date on it.", "THE WORK STARTS  c6", "ASK FOR THE PROCEDURES BEFORE SEPTEMBER 1ST", "NSF AWARD 2535195", "c6 c22 c23", "texasaidocket.com", "09 / 09"]
acceptance:
  - 'the frame carries "September 1st, 2026." in flag_red #BF0A30, it is the only red string in the deck, and it sits on the light rather than on the dark so it measures 4.5 to 1 or better'
  - "the corridor slot is the brightest region on the frame, measured off the render"
  - "both vanishing points and the horizon are asserted by the frame's own script against the values declared here"
  - 'the frame carries "ASK FOR THE PROCEDURES BEFORE SEPTEMBER 1ST", which names what to ask for and by when'
  - "a two part contact shadow sits where the leaf meets the floor, on a floor lit first"
risks:
  - "the red fails contrast against the slot. It is measured before the deck is scored, and the fix is to move the date onto the wedge rather than to dim the slot"
```
