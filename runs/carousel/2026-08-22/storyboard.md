# Storyboard, August 22nd, 2026 — Project 58482

Synthesis: Treatment B, "the room and who is standing in it", taken as the spine. The register is
the Houston flight control room read as a working object, because a docket index and a status
board are the same thing, a fixed set of positions each carrying a name and a short code, and
because a board never speculates about who is in the chair. That last property is not decoration.
It is the fact check's own limit turned into a drawing.

Corrections applied to the treatment as pitched:
- The treatment said 8 of 34 rows are quoted. The real count, taken in code, is TEN, and the
  remainder is 24. Both are declared in aggregates.json. The typed pair would have shipped wrong.
- Every figure is set in JetBrains Mono with tabular numerals and never in Fraunces. FIELD_NOTES
  2026-08-12 records Fraunces rendering 3 as 5 at feed size, and this deck's figures are 75, 34,
  25.521, 58482 and September 4th.
- flag_red measured about 3.0 contrast as ink on this deck's ground in this run's own smoke test,
  so red is spent as a FILLED GROUND under white mono and never as type.


## Palette, as declared tokens

`room #101A1B`, `console #24322F`, `console_lit #8FA396`, `face_sun #C7D2C4`,
`legend #E8EFE4`, `trace #9FD3B4`, `event_amber #D99A32`, `key_dark #060C0D`,
`flag_red #BF0A30`

```yaml
slide: 1
job: >
  State how many filings stand in the docket, and state in the same breath how many of them this
  deck actually quotes. No other frame carries the size of the room or the size of the gap.
claims: [c7]
numerals:
  - value_from: c7          # 34 filings, and the case style
  - computed_by: "aggregates.json, ten index rows carrying a verbatim quote, and 34 minus 10"
composition:
  structure: >
    A milled console plane in plan oblique at 25 degrees holds thirty four recesses in a seven by
    five grid less one, so occupancy is read as a filled surface before any single name is read.
  bands: >
    Top carries the kicker and the case style line. Middle carries the board itself at 820 by 560.
    Bottom carries the console plane running on past the board's lower lip, that lip's own two part
    contact shadow falling across it, and the figure 34 cut into the lit metal at 190px with the gap
    line beside it, so the lower third is modeled surface rather than type on a flat ground.
  focal: >
    The lit cluster of ten recesses in the board's upper left quadrant, read as one bright area
    against twenty four unlit ones.
art:
  technique: "wind-worked carve, TXCARVE, with two part contact shadows under one raking key"
  why_this_technique: >
    Thirty four filings is a claim about many of something occupying a fixed structure. A carve
    makes each row a seat in a surface rather than an item in a list, so the reader sees how full
    the room is before they read a word of it.
  palette: >
    Mission Control Center, Houston, Building 30. room #101A1B ground, console #24322F the plane,
    trace #9FD3B4 the lit blocks, key_dark #060C0D inside an unlit recess, legend #E8EFE4 type.
  value_structure: >
    Lightest is the display figure 34 in legend. Darkest is the interior of an unlit recess in
    key_dark. The console plane sits at a lit mid so every contact shadow has something to
    subtract from.
  motion: "the eye lands on the lit cluster, reads the board's extent, then drops to the figure"
type:
  hook: "34 filings are already in."
  dek: "The case style reads Large Load Demand Management Service."
  labels: ["10 rows are quoted on the frames that follow. The other 24 rows stand in the filing index and are not read here."]
acceptance:
  - "exactly 34 recesses are present and countable at 432px"
  - "exactly 10 recesses carry a lit block in trace #9FD3B4 and 24 do not"
  - "no recess is empty of its block, because absence of light never means absence of a filing"
  - 'the gap line reads exactly "10 rows are quoted on the frames that follow. The other 24 rows stand in the filing index and are not read here."'
  - "every contact shadow is two part, a 6px core and a 40px ambient, never a single drop"
  - "the figure 34 is set in JetBrains Mono, not Fraunces"
risks:
  - "a one part contact shadow reads as a drop shadow and cheapens the whole plane"
  - "a 34 in the display face could read as 54 at feed size, which is why the figure is mono"
```

```yaml
slide: 2
job: >
  Show that the door into this rule asks for a number rather than for an industry. This is the
  frame the whole deck turns on and no other frame carries the definition.
claims: [c6, c1, c20]
numerals:
  - value_from: c6          # 75 megawatts, at a single site
composition:
  structure: >
    A machined legend housing sits centered in the middle band and is lit from behind, so the
    definition arrives as a condition being satisfied rather than as a caption in a box.
  bands: >
    Top carries one line in console_lit naming what the frame is about. Middle carries the housing
    at 780 by 430. Bottom carries the housing's own two part contact shadow falling onto a lit
    shelf, plus the source line, so the lower third holds drawn form rather than empty ground.
  focal: >
    The cut figure 75 MW at 168px, the brightest area anywhere in the deck's dark half, its light
    spilling fourteen pixels past the glyph edges onto the housing's inner wall.
art:
  technique: >
    wire relief, TX.reliefRect, with TX.svgPlate measuring the cut legend, plus an engineering OPEN
    DIMENSION authored in SVG beneath the figure. Grafted from the threshold treatment.
  why_this_technique: >
    An event indicator is a plate that stays dark until a condition is true. The rule's definition
    IS a condition, so the housing argues the claim instead of containing it.
  palette: >
    console #24322F the housing, key_dark #060C0D the unlit plate, legend #E8EFE4 the cut legend
    and the figure, console_lit #8FA396 the lip catching spill, room #101A1B the ground.
  value_structure: >
    Lightest is the cut figure. Darkest is the unlit plate immediately around it, so the extreme
    light and the extreme dark are adjacent and the reader cannot look anywhere else.
  motion: "straight in, no travel. The frame is one object seen square"
type:
  hook: "The threshold is the definition"
  dek: "An entity with a total non-coincident peak demand at a single site that is equal to or greater than 75 megawatts (MW)."
  labels: ["16 TAC Section 25.521, proposed",
           "The rule as published in the Texas Register does not contain the words data center."]
acceptance:
  - 'the figure reads exactly "75MW" and is legible at 432px'
  - 'the frame states the absence and names the document it looked in, reading exactly "The rule as published in the Texas Register does not contain the words data center."'
  - 'the quoted definition carries the words "at a single site", because the threshold is per site and dropping that makes the number wrong'
  - "the housing carries a two part contact shadow onto a shelf that is itself lit"
  - "nothing on this frame is flag_red #BF0A30"
  - "no external key light touches the housing, because the frame declares internal emission"
  - "the dimension under the figure carries EXACTLY ONE terminator, on its left, and runs off the right frame edge with no arrowhead and no cap, because equal to or greater than has no upper bound"
risks:
  - "reliefRect lighting that disagrees with the declared emission and reads as two suns"
  - 'an open dimension can read as a rendering bug, so a 20px mono note at the open end reads "no upper bound"'
  - "dropping 'at a single site' would make 75 megawatts a claim about a company rather than a site"
```

```yaml
slide: 3
job: >
  Give the reader the one sentence they would actually be commenting on, at full size, with
  nothing else in the frame competing with it.
claims: [c5, c1]
numerals:
  - value_from: c1          # the section number 25.521
composition:
  structure: >
    An almost empty dark field is broken by one machined seam of light across the lower third, so
    the sentence sits on a surface rather than floating in a void.
  bands: >
    Top two thirds are ground falling to key_dark at the top edge, carrying the hook and then the
    sentence on the optical centre. Bottom third carries the seam as a machined groove with a lit
    upper lip and a dark floor, and the plane below it takes the raking key's falloff from lit metal
    down to key_dark at the bottom edge, so the lower third is a modeled surface.
  focal: >
    The sentence block itself, set large enough to be the largest light area in the frame.
art:
  technique: "the empty field with one machined seam of light, TX.fitText at deck maximum"
  why_this_technique: >
    The sentence is the entire subject of the frame and any drawn ground would compete with it.
    Restraint is the argument here, and the seam is what makes the emptiness a surface rather
    than an unfinished render.
  palette: >
    room #101A1B falling to key_dark #060C0D at the top edge, legend #E8EFE4 the sentence,
    console_lit #8FA396 the seam with a legend core.
  value_structure: >
    Lightest is the sentence. Darkest is the top edge. The seam sits between them and is the only
    thing establishing that the dark is a plane and not an absence.
  motion: "the eye rests on the sentence, then drops to the seam, which stops it"
type:
  hook: "What the rule would require"
  dek: "ERCOT must develop a Large Load Demand Management Service (LLDMS) to competitively procure demand reductions from large load customers consistent with this section."
  labels: ["16 TAC Section 25.521, proposed"]
acceptance:
  - "the quoted sentence is complete and is not truncated with an ellipsis"
  - "the seam runs the full 1080px width and does not land on the vertical centre"
  - "the frame carries no second bright element besides the sentence and the seam"
  - 'the section number reads "25.521" in JetBrains Mono'
risks:
  - "an empty field reads as an unfinished render, and only the seam and the scanline prevent it"
```

```yaml
slide: 4
job: >
  Name the trade association and the operator in the index's own grammar, and show they share a
  file stamp. No other frame puts two rows side by side.
claims: [c15, c17, c19]
numerals:
  - value_from: c15         # item 10, 4/8/2026
  - value_from: c17         # item 25, 4/8/2026
composition:
  structure: >
    A flat emissive table read straight down with no perspective, five columns at index widths,
    so the one column where both rows agree can be lit as a band.
  bands: >
    Top carries the hook. Middle carries the two row table with 2px rules top and bottom and a 1px
    hairline between. Bottom carries the console face the sheet lies on, taking a raking falloff
    from lit metal to key_dark at the bottom edge, with the sheet's own edge and its two part
    contact shadow across it, and the discipline line sits on that modeled metal.
  focal: >
    The file stamp column, drawn as a full height lit band behind both cells, so the agreement
    between the two rows is an area rather than two repeated words.
art:
  technique: >
    an oil chart table, flat and emissive. THE TABLE ITSELF carries no drawn light, because a screen
    emits rather than reflects. The console face it lies on is lit, so the frame has a modeled base
    and the flat table reads as a sheet on a surface rather than as an unfinished render.
  why_this_technique: >
    Two rows differing in one field and agreeing in another is exactly a table's job. This is the
    deck's one unlit frame, declared as a law rather than left as a look, because a screen emits
    and does not reflect.
  palette: >
    room #101A1B ground, legend #E8EFE4 the cells, trace #9FD3B4 the lit stamp column,
    console_lit #8FA396 the rules.
  value_structure: >
    Lightest is the lit stamp band. Darkest is the console face at the bottom edge where the raking
    key dies. The table rows sit between them and neither cast nor receive a shadow themselves.
  motion: "across the first row, down to the second, then the eye returns to the lit column"
type:
  hook: "2 filings here share a date."
  dek: "4/8/2026 Data Center Coalition COM DCC Comments Regarding the Large Load Demand Management Service"
  labels: ["4/8/2026 CyrusOne, LP COM CyrusOne, LP Comments in Response to Commission Staff's Questions",
           "The party field in the filing index gives a name. It gives nothing else."]
acceptance:
  - "the rules measure 2px at top and bottom and 1px between the two rows"
  - 'both file stamp cells read "4/8/2026" and sit inside the lit trace #9FD3B4 band'
  - "no shadow falls on the table rows themselves, because the table is emissive"
  - "the sheet's own edge carries a two part contact shadow onto the lit console face below it"
  - 'the bottom line reads exactly "The party field in the filing index gives a name. It gives nothing else."'
risks:
  - "a flat frame reads as unfinished, and the scanline plus the rule weights plus the lit column are the three things carrying it"
```

```yaml
slide: 5
job: >
  Dissect one index row and name, on the frame, the things the row does not say. This is the
  deck's counter-image and its argument against its own lens.
claims: [c13, c19]
numerals:
  - value_from: c13         # item 33, 8/3/2026
composition:
  structure: >
    Ground and ink invert here and nowhere else in the deck, and one row set large across the
    upper middle drops two leaders, one onto each ruled void.
  bands: >
    Top carries the hook on the light ground. Middle carries the dissected row and its leaders.
    Bottom carries the two ruled voids and their labels, which are the darkest areas in a light
    frame, so the lower third holds the frame's entire value extreme.
  focal: >
    The two ruled voids read together as one dark mass low centre. That is the frame's extreme
    value and the one place the light dies.
art:
  technique: "knockout labels with leader polylines terminating on each field's own bounding box"
  why_this_technique: >
    A callout is the only drawing that can point at a thing and at the absence of a thing with the
    same mark, which is exactly what this claim needs. Each leader is built from its target's own
    coordinates so it lands on the thing rather than near it.
  palette: >
    face_sun #C7D2C4 the ground, key_dark #060C0D the type and the voids, room #101A1B the void
    fill, console #24322F the leader rules.
  value_structure: >
    Lightest is the face_sun ground. Darkest is the interior of the two voids. The inversion from
    every other frame in the deck is what marks this as the frame that turns on the deck itself.
  motion: "the row is read left to right, then two leaders pull the eye down and stop in the dark"
type:
  hook: "What a row actually publishes."
  dek: "Helen Bryant"
  labels: ["Nothing here states who a filer is.", "This record does not expand PC."]
acceptance:
  - 'void one reads exactly "Nothing here states who a filer is."'
  - 'void two reads exactly "This record does not expand PC."'
  - "no leader terminates in empty ground, and every leader lands within 24px of its declared target"
  - "the words individual, resident, Texan, homeowner and public appear nowhere on this frame"
  - "this is the only frame in the deck whose ground is face_sun #C7D2C4"
risks:
  - "a leader stopping in void looks identical to a leader reaching something small, so every void is a ruled rectangle with a stated size"
```

```yaml
slide: 6
job: >
  Run the remaining named rows and let the party field's own separators do the drawing, so a
  reader sees that two pipes sit inside one field rather than between three parties.
claims: [c18, c14, c12, c11]
numerals:
  - value_from: c18         # item 26, 4/12/2026
  - value_from: c14         # item 28, 7/16/2026
  - value_from: c12         # item 32, 8/3/2026
  - value_from: c11         # item 34, 8/18/2026
composition:
  structure: >
    A left aligned column of four plates whose widths are the measured strings themselves, so the
    ragged right edge is data rather than a layout decision.
  bands: >
    Top carries the hook. Middle carries the four plates read top to bottom. Bottom carries the
    longest plate and the item type codes as literal strings, so the lower third holds the widest
    lit area in the frame.
  focal: >
    The longest plate, carrying "Zack Butler | EnerShield AI | Blind Mice Labs", which is both the
    widest lit area and the row the reader came for.
art:
  technique: "TX.svgPlate plates measured from the laid out text, with the index's pipes drawn as full height dividers at true glyph positions"
  why_this_technique: >
    Two of these four party fields are single strings containing two and three names. Drawing the
    separator as a real divider is the only way a reader sees the pipes are inside one field,
    which is the exact thing a careless deck would get wrong.
  palette: >
    console #24322F the plates, legend #E8EFE4 the strings, console_lit #8FA396 the drawn pipe
    dividers, room #101A1B the ground.
  value_structure: >
    Lightest is the string on the Fedor Mikheev plate, which is the widest as laid out. Darkest is
    the ground beyond the ragged edge, so
    the raggedness is legible as a shape rather than as an alignment error.
  motion: "top to bottom down the left edge, with the right edge stepping in and out as data"
type:
  hook: "The rest of the roll."
  dek: '"4/12/2026 Zack Butler | EnerShield AI | Blind Mice Labs PC"'
  labels:
    - '"8/3/2026 Jennifer Carrig COM Large Load Demand Services "Say No to incentives""'
    - '"8/18/2026 Modern Tex Consulting LLC COM Comments of Modern Tex Consulting LLC ..."'
acceptance:
  - "four plates are present and no two plates share a width"
  - "every pipe is U+007C, the separator c14 and c18 quote, set in its own span and scaled
    vertically, because a different glyph inside a quoted row is a quoted string the deck rewrote"
  - "each of the four rows opens and closes with a straight quotation mark, as slide 7 does, because
    the site publishes an unmarked string as this project own prose"
  - 'the nested quotes in "Say No to incentives" render as straight quotes'
  - "no plate width is a typed number, every one comes from TX.svgPlate measuring the laid out text"
risks:
  - "a plate opaque enough to become a box is furniture, so plates sit at the least opacity that keeps mono legible"
```

```yaml
slide: 7
job: >
  Show the commission's own three rows and that the deadline is carried inside two of their
  descriptions. No other frame shows the agency's side of the index.
claims: [c10, c8, c9]
numerals:
  - value_from: c10         # item 29, 7/24/2026, Sept. 4
  - value_from: c8          # item 30, 7/30/2026
  - value_from: c9          # item 31, 7/30/2026, 09/04/2026
composition:
  structure: >
    A stepped bracket hierarchy on a drawn spine, three rungs stepping right and down, because
    these rows are a proposal and two acknowledgements of it rather than three peers.
  bands: >
    Top carries the hook. Middle carries the spine at x 150 and the three rungs. Bottom carries the
    third rung, the spine's own cast shadow falling right across the console face beneath it, and the
    console face's raking falloff, so the lower third holds modeled metal as well as the amber mark.
  focal: >
    The two amber date marks read together as one lit pair against an otherwise neutral frame.
art:
  technique: "a stepped bracket on a drawn spine, TX.canvasLabel over the console face, raking key declared"
  why_this_technique: >
    A bracket states a relationship that a flat table cannot. These three rows are not a list,
    they are one document and two receipts for it, and the step down says so without a caption.
  palette: >
    console #24322F the console face, legend #E8EFE4 the strings, event_amber #D99A32 on the two
    date marks only, room #101A1B the ground, key_dark #060C0D the spine shadow.
  value_structure: >
    Lightest is the amber pair. Darkest is the spine's cast shadow on the console face. The rest
    of the frame is deliberately held at a neutral mid so the amber has nothing to compete with.
  motion: "down the spine, stepping right at each rung, ending on the acknowledgement"
type:
  hook: "2 rows here carry the deadline."
  dek: "\"7/24/2026 PUC RULES & PROJECTS PRJ OM Item No. 29 - Staff Memo & PFP w/Sept. 4 Comment Deadline\""
  labels: ['"7/30/2026 PUC OPDM PRJ PROPOSAL FOR PUBLICATION NEW §25.521"',
           '"7/30/2026 RULES & PROJECTS PRJ Texas Register Acknowledgement of Receipt - Comment Deadline 09/04/2026"']
acceptance:
  - "PFP and OPDM appear with no expansion and no gloss within 200px of either"
  - "event_amber #D99A32 appears on exactly two marks on this frame and nowhere else"
  - "the section symbol renders as § and not as the word section"
  - "the hyphens inside the quoted descriptions are U+002D and are neither an em dash nor an en dash"
  - 'each of the three rows opens and closes with a straight quotation mark, because each is a verbatim index row and the site publishes an unmarked string as this project''s own prose'
  - 'the hook counts only the rows on this frame and names no total, because the deck quotes 10 of 34 rows and has no standing to count over the index'
risks:
  - "amber is a second accent and accents creep, so it appears on this frame and slide 8 only"
```

```yaml
slide: 8
job: >
  Put the remaining time up as a magnitude and corroborate the date against the commission's own
  calendar. No other frame carries the clock.
claims: [c2, c16]
numerals:
  - value_from: c2          # September 4th, 2026
  - value_from: c16         # the calendar's own deadline entry
  - computed_by: "aggregates.json, (2026-09-04 minus 2026-08-22).days, with both ends printed on the frame"
composition:
  structure: >
    A segmented numeric readout drawn as physical segments fills the middle band, with the dead
    segments drawn in key_dark rather than omitted, so the instrument is visible as well as the value.
  bands: >
    Top carries the hook naming the date. Middle carries the readout at 620 by 420. Bottom carries the
    readout housing's lower bezel as lit modeled metal with its two part contact shadow on the shelf
    below, and the interval label and calendar line sit on that shelf, so the lower third is drawn form.
  focal: >
    The lit segments of the readout, the largest bright area in the deck after slide 2's figure.
art:
  technique: "a segmented numeric readout drawn as physical segments, emission declared"
  why_this_technique: >
    A number of days is a magnitude and this deck carries no time axis by law. A readout that
    shows its dead segments is the honest form, because it shows the instrument as well as the
    value, which is the difference between a measurement and a graphic.
  palette: >
    the dead segments sit darker than their plate, event_amber #D99A32 the lit segments, room
    #101A1B the ground, legend #E8EFE4 the labels.
  value_structure: >
    Lightest is the lit segment set. Darkest is a dead segment. The two sit inside the same glyph
    cells, so the reader reads the instrument and the reading at once.
  motion: "the eye lands on the lit digits, then drops to the two dates that produced them"
type:
  hook: "The window closes September 4th."
  dek: "13 days from August 22nd, 2026 to September 4th, 2026"
  labels: ["Public Comment Deadline - Friday, September 4, 2026"]
acceptance:
  - "every dead segment is drawn in key_dark #060C0D and none is omitted"
  - "the label names both ends of the interval, August 22nd, 2026 and September 4th, 2026"
  - "the value is interpolated from the computation in aggregates.json and is typed nowhere in the slide source"
  - "no flag_red #BF0A30 appears on this frame, which is the frame most tempted by it"
  - "the readout carries no severity ramp, one hue at one intensity at every value"
risks:
  - "a countdown is the classic place a severity ramp sneaks in, and a ramp would be a verdict this deck does not get to publish"
```

```yaml
slide: 9
job: >
  Carry the dated next step and spend the reserved red once. This is the only frame a reader can
  act from and the only frame in the deck carrying red.
claims: [c3, c4, c2]
numerals:
  - value_from: c3          # Project Number 58482
  - value_from: c2          # September 4th, 2026
composition:
  structure: >
    A solid red block occupies the middle band carrying measured white mono, with the channel
    sentence quoted beneath it on the deck ground, so the action reads before the mechanism.
  bands: >
    Top carries the hook. Middle carries the red block at 900 by 380 with two lines of white mono.
    Bottom carries the lit console shelf, which begins at 1010. The red block's own two part
    contact shadow falls immediately under its lower lip at 600, on the deck ground, NOT on that
    shelf, because the block sits 380px above it. The quoted filing sentence sits above that shelf on the deck ground. The filing
    address and the title block sit on the shelf itself, so the lower third carries the shadow that
    puts the block on a surface rather than a caption on a flat ground.
  focal: >
    The red block, unambiguously the frame's one area of extreme chroma and the only one in the deck.
art:
  technique: "a solid reserved red ground carrying TX.svgPlate measured white mono"
  why_this_technique: >
    brand.yaml reserves red for an open window a reader can still act on, and this is the only
    frame where that is true. Red as ground under white ink clears the contrast floor while red as
    ink on this deck's ground measured about 3.0 in this run's own smoke test, so the same
    decision satisfies the focal law and the contrast floor at once.
  palette: >
    flag_red #BF0A30 the block, legend #E8EFE4 the mono on it, room #101A1B the ground,
    console_lit #8FA396 the title block rules.
  value_structure: >
    The red block is the frame's chroma extreme and the white mono on it the frame's lightest ink.
    Everything else is held at a neutral mid so nothing competes with the one thing to act on.
  motion: "straight to the block, then down to the sentence that says how"
type:
  hook: "Refer to Project Number 58482."
  dek: "FILE BY SEPTEMBER 4TH, 2026"
  labels: ["REFER TO PROJECT NUMBER 58482",
           "Interested persons may file comments electronically through the interchange on the commission's website",
           "interchange.puc.texas.gov",
           "texasaidocket.com"]
acceptance:
  - "white legend #E8EFE4 on flag_red #BF0A30 measures at or above 4.5 to 1"
  - "flag_red #BF0A30 appears on this frame and on no other frame in the deck"
  - 'the site line reads exactly "texasaidocket.com" and matches config/brand.yaml visual.constellation.site'
  - 'the project number reads "58482" in JetBrains Mono and the date reads "SEPTEMBER 4TH, 2026"'
  - "no coordinate and no county name appears anywhere on this frame, because the story names no place"
  - 'the quoted filing sentence ends at the word website and carries NO closing period, because c4 has none and a verbatim quote is never completed for it'
  - 'the frame prints the filing address "interchange.puc.texas.gov", read from the host of the claim urls in claims.json and typed nowhere'
  - 'the title block scope reads "ERCOT REGION" and not "STATEWIDE", because the rule''s requirement runs to ERCOT and ERCOT is not the state'
risks:
  - "the placeless score is carried here rather than by a county, so the title block names the docket as the venue this story actually has"
```
