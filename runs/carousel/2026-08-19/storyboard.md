# Storyboard, August 19th, 2026

Carousel No. 3. Story `tx-2026-0072`. Eight slides.

**Slide 4 was cut after scoring.** Its headline promised "Whose water, and whose power" and the
frame delivered only water, and it sat directly before the deck's densest frame. The scorer named
it the most cuttable frame twice. The water theme survives on the guardrails frame, which already
names WATER as one of the four. The freed frame went to the close, which had no way for a reader
to act.

## The synthesis, and why this one

Three treatments came back and all three independently refused the same four things, which is the
strongest signal the room produced.

- **No map, unanimously.** The record carries no geography for this item. All three directors
  reached the same conclusion by different routes, and two of them named it as the variety move as
  well as the honest one. Both shipped decks led with cartography. This one has none.
- **Slide 5 is the inversion, and it is `c11` against `c12`.** All three put the deck's one bright
  frame on the same fact, that one office worded the same instruction two ways on the same day.
- **The counter-image is an absence.** All three built it on the unnamed project in `c17`.
- **The reserved red stays unspent.** No comment window on this story is open to a reader.

**THE SPINE IS THE STOPPED CLOCK.** It wins on one idea the other two do not have: *one day is 46
pixels, everywhere in the deck, and no time axis is truncated*. This story IS a schedule, so a
constant rate makes three otherwise unlike frames comparable by length, and it is the
compute-not-generate law expressed as geometry rather than as a caption. Its slide 1 also draws the
only thing this run can actually prove, which is an absence, and it proves it with a light source
rather than by asserting it.

**GRAFTED FROM THE DOCUMENT LENS, and it is the best single idea in the room: RULED MEANS QUOTED.**
A hairline above and below a block of type means the words are a source's own, with attribution in
mono under the lower rule carrying publisher and claim id. Unruled type is the Docket's. A reader
learns it by slide 3, and it is what lets slide 6 land without one word of accusation from us. It
also serves the readability brief directly, because a reader always knows whose sentence they are
reading.

**GRAFTED FROM THE QUEUE LENS.** Its warning about verdicts, which the clock lens needed. A measure
that falls below a datum reads as failure to most people, and this record supports a missed date
rather than a judgment. So no fill under any bar, no zone shading, no severity ramp, one hue at one
intensity per measure. Also its discipline of exactly one of a thing, because two would imply a
count the record does not carry.

**ONE DEVIATION REFUSED.** The clock lens proposed replacing the constellation's coordinates footer
with the notice identifier, on the grounds that a story with no place has a docket number instead.
It is a good argument and `config/brand.yaml` is human owned, so the footer stays. It resolves to
Travis County from the gazetteer, where the commission that has to act on this sits.

## The three laws this deck is built on

1. **No horizon anywhere.** No sky, no ground, no landscape. Every frame is a sheet, a field or an
   instrument, seen straight on or straight down.
2. **One day is 46 pixels, on every slide that draws time, and no axis is truncated.**
3. **Ruled means quoted.** Attribution under the lower rule, always, with the claim id.

## Palette, the Texas county courthouse at night

The answer to a statewide story. Every Texas county has one, so it is statewide by construction
rather than by averaging, it is a public record material rather than a landscape, and it is where a
public schedule gets posted and a public clock gets kept.

`tower #16151C` masonry in shadow, warm neutral with no violet so it can't be read as the house Big
Bend night. `dial #EFE9DA` enameled cast iron lit from behind, the deck's light and its only near
white on dark. `cordova #D9CDB4` Cordova cream limestone, Williamson County. `brass #B98D46` the
movement's works, line colour. `pecos #8E4B3A` masonry red, fill only, never type on dark.
`patina #4E6B62` oxidized copper, slide 6 alone. `paper #F6F1E4` on `ink #23202B`, slide 5 alone.

## The value arc

Mid dark with one void, darker with one bright rule, a raked bed of identical panels, a lit table,
**PAPER, the inversion**, the only multi colour frame, **the deck's floor**, one lit cell resolving.

Eight beats for eight frames. The ninth beat, dark with a brass line only, belonged to the old
slide 4 named at the top of this file, the frame cut after the second scoring pass.

The inversion at 5 is a different kind from 2026-08-16's paper slide. That was handmade tooth with
a torn deckle. This is machine flat, neatlined, grain at 2 percent. Same material, opposite
treatment. The trough at 7 keeps the back half from coasting.

---

```yaml
slide: 1
job: >
  Open on the one thing this run can actually prove happened, which is that a date came and went,
  and prove it with a light source rather than by asserting it.
claims: [c2]
numerals:
  - computed_by: "out/2026-08-19/compute.py, spans.days_since_deadline_passed"
composition:
  structure: >
    An August month sheet embossed into limestone, filling the frame at a slight tilt, with one
    cell cut clean through it. The sheet is a grid so the reader counts rather than reads, and the
    hole sits left of centre so the eye finds it before it finishes crossing the frame. A raking
    key from the low left rakes across every raised tile and then finds no floor in the void,
    which is what separates a hole from a dark tile.
  bands: >
    Top third is masonry in shadow carrying the counter and the source chip. Middle third is the
    month sheet with the void left of centre. Bottom third is where the tilted sheet's lower edge
    and the long shadow it throws across the limestone actually land, so the base of the frame is
    lit stone and raking shadow with the display line sitting on it rather than a caption band
    ruled under the art.
  focal: >
    The void. The eye is pulled there because it is the only place in the frame where the key
    light dies, and every other cell returns some light.
art:
  technique: "Three.js bench, txthree.js, the deck's one GPU frame"
  why_this_technique: >
    The claim is an absence and an absence needs a light source to prove it. A drawn empty
    rectangle is ambiguous at any size, because it reads equally as a dark tile. A hole that
    swallows a raking light is not ambiguous. Nothing else in the library computes occlusion, and
    the library says to spend the one heavy technique on the slide most people are the only one to
    see.
  palette: >
    Cordova cream limestone from the Williamson County quarry that faces a large share of Texas
    courthouses, on tower masonry shadow. Drawn from the courthouse rather than from soil because
    this story has no county.
  value_structure: >
    Lightest is the tile faces catching the key at cordova. Darkest is inside the void, which is
    the deck's first true black and the only true black in the first five frames. The lit faces
    do the counting and the void does the argument.
  motion: >
    The key rakes left to right across the tiles, so the eye travels the same way and arrives at
    the void from the lit side.
type:
  hook: "August 7th came and went."
  dek: >
    ERCOT set itself a date to tell service providers how every large load was classified. That
    date passed 12 days ago.
  labels: ["AUGUST 2026", "ERCOT MARKET NOTICE M-A080326-01"]
acceptance:
  - "the weekday alignment of the month sheet is computed in Python from the date, never placed by hand"
  - "the void reads as a hole rather than as a dark tile at 432px, judged on the thumb first"
  - "the raking key produces no floor inside the void at any point along its opening"
  - "grain does not repeat visibly at 2x, which means at or under 4 percent"
  - "the numeral 12 traces to computed.json spans.days_since_deadline_passed"
  - "no violet appears anywhere in the ground, so it can't be read as the house Big Bend night"
risks:
  - "SwiftShader softens the emboss until the void stops reading as a hole at thumb size. Named fallback is the same frame rebuilt with TX.reliefRect and a two part contact shadow"
  - "a month sheet invites a reader to count all thirty one cells and lose the one that matters"
```

```yaml
slide: 2
job: >
  Give the reader the ratio that makes the whole story, which is how little warning there was
  against how long the silence has run, at one true rate so neither can be exaggerated.
claims: [c1]
numerals:
  - computed_by: "out/2026-08-19/compute.py, spans.days_directive_to_deadline"
  - computed_by: "out/2026-08-19/compute.py, spans.days_since_directive"
composition:
  structure: >
    One horizontal rule across the full width, ticked once per day at the deck's constant rate,
    with two bars sharing a single origin tick at August 3rd. The four day bar runs above the rule
    and the sixteen day bar runs below it. Sharing an origin is what makes the eye read the ratio
    before it reads either figure, and it removes any chance of a truncated axis, because both
    measures start at the same drawn point.
  bands: >
    Top third carries the display line over the contour ground. Middle third is the day rule with
    the four day bar above it. The sixteen day bar runs BELOW the rule, so the bottom third holds
    the longest measured object in the frame, over a contour ground whose tone deepens toward the
    base and takes the ruled quote and its attribution on top of that modeled falloff.
  focal: >
    The origin tick where the two bars meet, because it is the only place in the frame where two
    different measures touch.
art:
  technique: "contour set as ground, with the true rate day rule over it and TX.canvasLabel knockouts"
  why_this_technique: >
    A measured rule needs a ground that carries texture without value, and the library names the
    contour set as exactly that. The rule itself is the survey register's scale bar redenominated
    in days. The slope chart's anti truncation law governs it, because a truncated time axis is a
    lie told with a true number and this deck is entirely about elapsed time.
  palette: >
    tower ground, contour set in cordova at low contrast, the four day bar in dial at full value,
    the sixteen day bar in brass at just over half.
  value_structure: >
    The four day bar is the brightest object in the deck's first five frames and the shortest. The
    sixteen day bar is the longest and deliberately dimmer. Brightness and length carry opposite
    weights, so neither reads as more important than the other and the reader has to hold both.
  motion: >
    Left to right along the rule, then a vertical jump at the origin tick between the two bars.
type:
  hook: "Four days of warning."
  dek: >
    ERCOT recorded the letter on August 3rd. Its own classification date was August 7th, and 16
    days have passed since the letter arrived.
  labels: ["AUGUST 3RD", "AUGUST 7TH", "4 DAYS", "16 DAYS"]
acceptance:
  - "the rate holds at 46 pixels per day across both bars, measured, not eyeballed. The four day bar is 184px and lands ON the August 7th tick. The sixteen day bar is 736px and lands ON the August 19th tick, which is the run date. An earlier draft drew both 9px short so the measure would read as open, which encoded 3.80 and 15.80 days at this frame's own stated rate"
  - "both bars begin at the same drawn origin tick and neither axis is truncated"
  - "the terminal tick on the four day bar is drawn open rather than closed, so the measure stops without landing"
  - "no fill sits under either bar and no zone shading appears, because a measure that falls reads as a verdict"
  - "contour spacing never drops below 3px at 2x, checked on the 432px thumb for moire"
  - "both numerals trace to computed.json spans"
risks:
  - "two bars on one rule can read as a comparison of two quantities rather than two durations"
  - "the contour ground competes with the rule if its contrast creeps above about 5 percent"
```

```yaml
slide: 3
job: >
  Say what actually stopped, which is not construction and not a project but a sorting, and show
  that the sorting has no answers in it.
claims: [c2, c5]
composition:
  structure: >
    A bounded rectangular field of partition cells with a class legend beside it, every cell at
    one identical value and every legend swatch empty. A partition drawn with no assignment is the
    claim itself rather than a decoration of it. The field is clipped square at all four edges and
    boxed by a hard neatline so it can never be mistaken for a shape on a map.
  bands: >
    Top third is the notice's own subject line set as a document header. Middle third is the
    partition field. The field bleeds down through the bottom third rather than stopping at a
    caption band, so the base carries brass cell hatching and the grain of the stone under it,
    with the empty class legend and the quoted sentence sitting on that texture.
  focal: >
    The empty legend, because it is the only element in the frame that promises a key and then
    supplies nothing.
art:
  technique: "Voronoi districts, unassigned, inside a rectangular neatline"
  why_this_technique: >
    The library gives Voronoi to anything partitioned and Batch Zero is a classification. Its
    named failure is using it for counties, which is answered by the neatline and by there being
    no state silhouette anywhere in this deck. Drawing the partition with every cell identical is
    the only honest way to show a sorting whose results were never issued.
  palette: >
    tower ground, cells outlined in brass hairline at one weight, legend swatches ruled in cordova
    and left unfilled.
  value_structure: >
    Every panel is one identical material at one identical value, because nothing was assigned.
    The panels do not differ. The LIGHT does, because there is one key in the room and it rakes
    across the whole bed from the high left, so an edge facing the lamp catches it and an edge
    facing away sits in its own shadow. No panel owns any part of that gradient and no panel is
    lit differently from its neighbour, so the partition still carries no assignment.

    This line was rewritten during the scoring rounds and the reason is on the record. It asked
    for a completely flat frame, and its own risks list already named what that produces, which is
    a frame that reads as an unfinished render. The deck shipped exactly that failure once already
    on slide 7, where two judges independently read an under-drawn frame as one that had not
    finished rendering. A flat frame is not the only honest way to draw an unassigned partition.
    Identical panels under one light is honest about the same thing and is worth looking at.
  motion: >
    None by design. The eye wanders the field, finds no differentiation, and settles on the legend.
type:
  hook: "Nobody was told the answer."
  dek: >
    The classification was to say how each large load falls. No service provider was told which
    class anything landed in.
  labels: ["UPDATE REGARDING BATCH ZERO TIMELINES AND PROCESSES", "no class stated"]
acceptance:
  - "no cell differs in fill, material or treatment from any other cell in the field. One key falls across the whole bed and every panel is drawn by the same rule, so a value difference between two panels is a fact about where the lamp is and never about what either panel was assigned"
  - "the legend carries EXACTLY ONE row, reading no class stated, which is what c2 supports and nothing more"
  - "no legend label names a classification category, because no source publishes one. An earlier draft of this file asked for at least two empty swatches so the emptiness would read as a pattern, and the frame shipped three NAMED categories instead. A key with one entry that says nothing can be keyed is the honest drawing"
  - "the field is clipped square at all four edges and reads as a rectangle rather than as a region"
  - "no state silhouette, county boundary or coastline appears anywhere in the frame"
  - "the subject line is quoted verbatim from the notice and carries its attribution under the rule"
risks:
  - "a Voronoi field is an inherently map-like object and a reader may supply a Texas that is not there"
  - "a completely flat frame can read as an unfinished render rather than as a deliberate choice"
```

```yaml
slide: 4
job: >
  Put the three figures the two documents actually state side by side, with their own wordings and
  their own sources, in the one form that presents them without implying arithmetic between them.
claims: [c6, c8, c9]
numerals:
  - value_from: c6
  - value_from: c8
composition:
  structure: >
    A mid century oil chart table. Two pixel rules top and bottom, hairlines between rows, tabular
    mono figures on a shared decimal alignment, and a measured plate behind each row. A table is
    the only form that presents three figures with three different denominators without inviting a
    reader to combine them.
  bands: >
    Top third carries the display line and the top rule. Middle third is the three rows. The low
    lamp lighting the table falls off across the bottom third, so the base carries a graded wash
    over the stone with the per row attribution set into it, and the plate shadows under the last
    row are the darkest modeled tone in the frame.
  focal: >
    The first row's figure, which is the largest type in the table and the number the letter
    itself opens with.
art:
  technique: "mid century oil chart table with TX.svgPlate measured plates and tabular mono"
  why_this_technique: >
    These three figures have no legal relationship to each other. Any proportional drawing would
    invite the multiplication the claims file explicitly rejects, where the queue total and the
    data centre share get multiplied into a number no source carries. A table refuses that by
    construction, and it is the deck's only table so it reads as a beat rather than as a fallback.
  palette: >
    tower ground, rules and hairlines in brass, figures in dial, attribution in cordova at small
    size.
  value_structure: >
    Lit as a document under a low lamp. Brightest at the top rule and falling off by the third row,
    which puts the value gradient on the same axis as the sources' descending confidence.
  motion: >
    Straight down the table, row to row, held by the hairlines.
type:
  hd: "Three figures, two documents."
  dek: >
    Each of these is quoted as its own document words it. None of them may be multiplied by
    another.
  labels: ["approximately 474 gigawatts", "Approximately 90 percent", "more than five times"]
acceptance:
  - "no fourth figure appears anywhere on this slide, computed or otherwise"
  - "the queue figure uses the signed letter's wording and the phrase approximately over appears nowhere"
  - "the share row carries the source's own words new power requests, so it can never read as a share of gigawatts"
  - "the third row is marked to the press release, which is the medium confidence source of the three"
  - "every row carries its own claim id under the bottom rule"
risks:
  - "three figures in one frame is the deck's densest slide and may push the reading load"
  - "a table is the easiest frame in the deck to make dull, and it sits directly before the inversion"
```

```yaml
slide: 5
job: >
  The turn. Show that one office worded the same instruction two ways on the same day, and let the
  reader find the difference without one word of accusation from us.
claims: [c11, c12]
composition:
  structure: >
    A survey sheet with a hard neatline and two equal columns divided by a single hairline running
    floor to ceiling. Left column is the press release, right column is the signed letter, set at
    identical size, measure and leading. Equal treatment is the argument, because any difference in
    weight would be us scoring one against the other.
  bands: >
    Top third carries a column head over each block and six words of ours. Middle third is the two
    quoted blocks. The bottom third carries the sheet's own grain and the slight lighting falloff
    across the paper toward the base, with the attribution and the primary document line sitting on
    that texture rather than on a flat field.
  focal: >
    The vertical hairline between the two columns, which is the only mark in the frame that
    separates rather than describes.
art:
  technique: "survey sheet on the paper register, flat and untextured, with a hard neatline and TX.fitText"
  why_this_technique: >
    This is the deck's turn and it reverses what the first five frames built, from a schedule
    stopping to the two documents not agreeing on what stopped. It has to look like the record
    rather than like an argument, so it gets the plainest sheet in the deck. It is deliberately the
    opposite treatment of the 2026-08-16 paper slide, which was torn deckle and stipple tooth. This
    one is machine flat with grain at 2 percent.
  palette: >
    paper ground with ink type, the deck's only light frame. The words that differ between the two
    wordings are marked in pecos, which clears contrast on paper and is plainly not flag red.
  value_structure: >
    The inversion. Dark ink on a light ground, where every other frame in the deck is light on
    dark. It is the brightest frame by a wide margin and it is the only one a reader reads rather
    than looks at.
  motion: >
    Left column top to bottom, then right column top to bottom, then back to the hairline.
type:
  hook: "One office. The same day. Two wordings."
  dek: >
    The signed letter words it more narrowly than the press release does. Both are on the record
    and they are not interchangeable.
  labels: ["THE PRESS RELEASE", "THE SIGNED LETTER"]
acceptance:
  - "both strings are verbatim, neither paraphrased and neither blended into a single sentence"
  - "the two columns are identical in type size, measure and leading, measured rather than judged"
  - "no arrow, highlight, adjective or verdict of ours appears between the two blocks"
  - "the reserved flag red appears nowhere on the slide and pecos is used only on differing words"
  - "each column carries its publisher and claim id under the lower rule"
  - "both blocks are legible at 432px with a rendered cap height of at least 11px, or the two blocks stack on a horizontal rule instead"
risks:
  - "two columns of quoted type may fall under the legible cap height at thumb size, and the stated fallback is stacking them"
  - "a divergence between two documents can read as a gotcha, which is not this record's voice, and any adjective from us would confirm that reading"
```

```yaml
slide: 6
job: >
  Argue the other way. The counter-image, where the sector says it will comply and the four
  guardrails are named in the Governor's own words.
claims: [c16, c18]
composition:
  structure: >
    Four equal vertical bands seen straight down, in the manner of the Capitol rotunda's geometric
    inlay, one guardrail word set into each band. Four named demands is a division of a field
    rather than a quantity, and equal widths are deliberate, because unequal areas would imply a
    proportion no source states.
  bands: >
    Top third carries the lead line stating who said this and when, over the terrazzo ground.
    Middle third is where the four guardrail words sit, inlaid into the four bands at their widest
    reading size, and it is the only place in the frame carrying type at display scale. The four
    inlay bands themselves run full height through all three thirds, so the bottom third is
    terrazzo texture and the graded tone of the four stones, with the quoted guardrail sentence set
    over that inlay rather than under it.
  focal: >
    The band boundaries, because four hard vertical edges in a deck that has had almost none read
    as structure the moment the frame opens.
art:
  technique: "terrazzo inlay, four equal bands, straight down, under the rotunda inlay licence"
  why_this_technique: >
    This is the deck's counter-image and a deck that only argues one way reads as promotion. Four
    named guardrails is a division of a field, and the Capitol's own geometric inlay is the state's
    device for dividing a field. It is also the deck's only multi colour frame, which makes it
    register as a beat immediately after the white sheet.
  palette: >
    cordova, pecos, patina and brass as the four bands, on the terrazzo ground. This is the deck's
    only appearance of all four together and the second of only two appearances of patina.
  value_structure: >
    The widest value spread inside any single frame in the deck, which is what makes it land as a
    beat coming out of the inversion. No band is lighter than another by enough to rank them.
  motion: >
    Left to right across the four bands, in the order the Governor names them.
type:
  hook: "The sector said it will comply."
  dek: >
    The Governor's office said this on August 18th. It is a statement about his own policy rather
    than a measured result.
  labels: ["GRID", "WATER", "NEIGHBORHOODS", "PAY THEIR OWN WAY"]
acceptance:
  - "all four bands are identical in width, measured rather than judged"
  - "no circle, pie, arc or dial appears anywhere in the frame"
  - "the attribution states that the Governor's office said this, never that it is established"
  - "the four band words are the Governor's own, in his order, and none is paraphrased"
  - "patina appears on this slide and on no other, which is what artwork.json records"
risks:
  - "the courthouse palette can drift into heritage nostalgia and patina is the colour that does it"
  - "four equal bands can read as a chart with four equal values rather than as four named things"
```

```yaml
slide: 7
job: >
  The deck's floor and its emotional centre. One project ended before construction, no source names
  it, and the frame publishes the size of that gap instead of filling it.
claims: [c17]
composition:
  structure: >
    A survey title block at frame scale with every field filled from the record except one, which
    is ruled and left empty and labelled as not named in the source. A filled block with one blank
    field is the compute-not-generate law's corollary made visible, which is that where a thing
    can't be computed the record says so and publishes the size of the gap.
  bands: >
    Top third carries the quoted sentence at the largest quoted size in the deck. Middle third is
    the title block. The block sits on stone and throws a contact shadow that falls through the
    bottom third, and the empty NAME field is ruled into that lit and shadowed surface, so the band
    the reader finishes on carries the modeled stone and the absence cut into it.
  focal: >
    The empty field, pulled there because every other field in the block is filled and the eye
    finishes on the one that is not.
art:
  technique: "survey title block at frame scale, oil chart rules, one field ruled and left empty"
  why_this_technique: >
    The library's withheld actor device, except the actor stays withheld because the record
    genuinely does not have it. Every other way of drawing this would either invent a project or
    say nothing. A ruled empty field says precisely what is missing and precisely how large the
    missing thing is, which is the only honest drawing available.
  palette: >
    tower ground at the deck's floor, block rules in brass, the filled field values in cordova, the
    empty field ruled in brass with nothing inside it.
  value_structure: >
    The deck's darkest frame. One small lit block on near black, with nothing else in the frame
    carrying light at all. It is the quietest slide and the trough that stops the back half
    coasting.
  motion: >
    Down the filled fields in order, arriving at the empty one last.
type:
  hook: "One project is not named."
  dek: >
    The August 18th release says a data centre ended operations before construction began. It names
    no company, no county and no project.
  labels: ["DATE", "PUBLISHER", "SOURCE", "NAME", "NOT NAMED IN THE SOURCE"]
acceptance:
  - "no company, project, county or sector guess appears anywhere in the frame"
  - "the NAME field is drawn, ruled and empty rather than omitted, so the gap has a visible size"
  - "the quoted sentence keeps the source's own words including could not, which the contraction rule exempts inside a quote"
  - "no causal claim links this project's end to the audit, because no source makes one"
  - "exactly one field is empty, because two would imply a count the record does not carry"
risks:
  - "an empty field can read as an unfinished slide rather than as a deliberate statement, and the label is the only thing preventing it"
  - "a reader may infer the project was cancelled by the audit, which no source says"
```

```yaml
slide: 8
job: >
  Close on everything a reader can still watch or file into, each item saying exactly what its own
  source verifies and nothing beyond it.
claims: [c3, c4, c19, c20, c21]
numerals:
  - value_from: c21
composition:
  structure: >
    One cell lit from behind in a mostly empty field, the callback to slide 1's void inverted, with
    the light it throws falling down onto the dated list beneath. The cell and the list are one
    composition rather than two stacked, and the shaft is what joins them.
  bands: >
    Top third carries the headline. Middle third holds the lit cell and the top of its shaft. The
    shaft widens as it falls and washes the first rows of the list, so the bottom third is modeled
    light rather than a footer band.
  focal: >
    The lit cell, because it is the only source of light in the frame and it is the same cell the
    deck opened by cutting a hole in.
art:
  technique: "a single cell lit from behind, throwing a widening shaft down onto a dated list"
  why_this_technique: >
    The callback to slide 1, inverted. That cell was a hole a light died in. This is the same cell
    with the light behind it, which is the register's payoff and the reason this deck never needed
    to draw a dial. The shaft exists because the third scoring pass found the payoff image and the
    payoff content sitting in the same frame without meeting.
  palette: >
    tower ground, the cell in dial lit from behind, the list ruled in brass, everything else unlit.
  value_structure: >
    Resolves to mid dark after the floor at slide 7. The lit cell is the only light and it is the
    deck's last word, so the value rises once at the very end rather than fading out.
  motion: >
    Down from the headline to the lit cell, then down the shaft into the list.
type:
  hd: "What is still open to you."
  rows: >
    Four, each one fact from one source. August 20th and the good cause exception filing. August
    21st, a second open meeting on the commission's own calendar. September 4th, a public comment
    deadline, said plainly to have no docket named against it. Project 58482, the proposed rule on
    Large Load Demand Management Service, which took a comment on August 18th.
acceptance:
  - "the copy says ERCOT committed to file, and never that it has filed or has not filed"
  - "nothing on the slide asserts any outcome of either open meeting"
  - "the September 4th deadline and the Project 58482 filing sit on SEPARATE rows, because c20 names no docket and c21 names no deadline, and nothing fetched links them"
  - "the counter reads 08 / 08, and the Lone Star brand mark sits in the masthead as on every slide"
  - "no date column string overruns its own column, measured on the ink rather than the element box"
risks:
  - "a closing slide about a future meeting invites a prediction, and the copy discipline is the only thing stopping one"
  - "four rows under one headline reads as a list of equivalent things, and only the third row's own sentence says the deadline has no docket attached"
```
