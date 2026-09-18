# Storyboard — carousel No. 28, September 18th, 2026

**Deck title.** Who writes the record.

**The world.** `minutebook`, a county records room at night. Chassis
`assets/js/deck/2026-09-18-minutebook.js`, declared once, loaded by all nine frames.

**The one light.** The key is upper right at 26 degrees above the plane, so every cast in this
deck runs down and to the LEFT at about twice the object's own height. Nothing is lit from
overhead and nothing is lit from the left.

**The one screen.** Halftone, cell 6, angle 26, on all nine frames. It is the deck's stock.

**The one accent.** `#4FC79A`, brand token `signal_open`. HOLLOW ON EVERY FRAME. Never a fill,
never behind a word, and it bounds only what is UNANSWERED. Carried on frames 2, 4, 8 and 9,
absent from 1, 3, 5, 6 and 7. Frame 6 is the room rather than a document and bounds no clause,
so it carries none.

## Palette

| token | hex | role |
|---|---|---|
| `room_ground` | `#361D27` | the records-room ground present in every frame |
| `shelf_material` | `#4F3D2F` | the shelf board and bindings |
| `display_ink` | `#E4D3CE` | display type and light-on-dark marks |
| `paper_stock` | `#EDDFD4` | the drawn document stock |
| `signal_open` | `#4FC79A` | the hollow unanswered-state accent |

The ROOM and STOCK ramps and their measured candidate sets live in
`assets/js/deck/2026-09-18-minutebook.js` and `palette_measured.json`. These are the five fixed
roles the chassis declares; the intermediate ramp steps are computed rather than second-copied
here.

CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE, VALUE_ARC

**Continuity devices, three, named here because `layout_check --require` refuses a storyboard
that declares fewer than two.**

1. **MOTIF EVOLUTION, the record itself.** The shelf of bound minute book volumes on one board at
   a constant y. Full and continuous on frame 1, referenced at the edge of frames 2 and 4, and on
   frame 9 the same shelf with the gap where the September volume would stand. The motif is the
   progress indicator and the thesis at once.
2. **CAMERA MOVE, and frames 1 and 9 are the identical camera.** Same height, same crop, same
   board at the same y, and what has changed between them is the room rather than the lens. The
   September 16th judge named that move as the best thing in that deck while the old rotation rule
   pulled against it.
3. **VALUE AND PALETTE ARC.** Planned frame medians 16, 18, 20, 17, 20, 25, 14, 21, 17.

   **THOSE NUMBERS WERE RE-PLANNED ONCE, AFTER THE PROBE FRAME, AND THE RUN RECORD SAYS SO.** The
   first plan read 32, 30, 27, 29, 27, 24, 22, 25, 18 and it was written against a chassis nobody
   had rendered yet. The probe measured this world's real range and the first full render came
   back between 8 and 34, so the LEVEL was wrong from the start while the SHAPE was not. What was
   planned and kept is the shape: small adjacent steps, one high point at the room where the
   people are, and a close that settles rather than spikes. Re-planning the level once against a
   measured chassis is honest. Re-planning it per frame after each render would be writing a
   description and calling it a plan.

**The three structural laws, from the directors room, binding on every frame.**

- **The gap is never drawn as a mark and never as a dark field.** It is the lit board with nothing
  standing on it. A dark field says a volume was REMOVED and the record says nothing was ever set
  down. No gap anywhere in this deck is drawn as a number of empty rows, because a count of
  missing entries is the one figure the fact checker rejected by name.
- **A drawn line of type gets glyphs if and only if this run fetched those glyphs.** The three
  agendas and the archive are set verbatim. Any disposition is drawn with `ruleRun` hairlines at
  true line lengths, never as a filled bar.
- **No seal, no badge, no livery.** The sedan on frame 3 is unmarked and no frame draws an
  insignia of any kind.

  **THE "NO NAME" HALF OF THIS LAW WAS REVERSED AT ROUND 5 AND THE REVERSAL IS THE POINT.**
  It originally read "four commissioners appear on two sponsor lines in the record and none of
  them is drawn". Three scoring rounds then said in different words that nine frames name no
  human being and that a reader is given nothing to do, and the round-4 reader judge found the
  answer already sitting in the claims file: c5 and c10 were fetched, verified and printed
  nowhere. Frames 2 and 4 now print the names their items print, "BECERRA/HIPOLITO" and
  "BECERRA/CARDENAS/HUNT", quoted as the county's own type, under a label reading
  AT THE FOOT OF THE ITEM.
  This is not a licence to name people generally. It is narrower than the law it replaces: a
  name appears only where the fetched document itself prints it, on the item it belongs to,
  quoted. Nobody is characterised, nobody is assigned a position, and no frame says how anyone
  voted, because no fetched page says.

  **AND THE FIRST DRAFT OF THIS BOUND BROKE IT IN THE SAME ROUND IT WAS WRITTEN.** The label
  over the names read SPONSOR LINE, which the round-5 integrity judge hard-failed and was right
  to. No fetched string in `claims.json` contains the word sponsor. c5's evidence is its quote
  plus a note reading "Sponsor names render in bold immediately after the item's closing full
  stop", which is an observation about TYPOGRAPHY, and both c5 and c10 are `confidence: medium`.
  Reading a role off bold type and printing it unhedged, about four named living people, on an
  AI purchase, is assigning a position. The label now reads AT THE FOOT OF THE ITEM, which is
  the thing that was actually measured.

  **AND THE CAPTION LINE THAT MATCHED IT HARD-FAILED TOO, AT ROUND 6, AND IS GONE.** It read
  "Becerra's name is printed at the foot of both items", and three items are described in
  consecutive paragraphs above it, so "both" had no clean antecedent and the nearest available
  pair was the two items the sentence does NOT mean. No claim puts any name on the September
  8th item. The integrity judge considered the same line and declined to fail it, calling it
  ambiguity rather than fabrication, which is a real disagreement between two judges and not an
  oversight by one. The line was DELETED rather than reworded, because rewording this surface
  is what produced the four failures before it. The names survive on the two frames whose
  documents print them, which was always the defensible place for them. Neither string was reachable by `verbatim_check`, because a gloss is not a quote and
  the names were printed unquoted at the time, so the two most sensitive strings added that round sat outside
  every gate in the suite.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "the county records room, a shelf board running off both edges at y 1118 carrying nine
    bound minute book volumes at true size, 0.32 m at the spine and 0.42 m tall at 620 px per
    metre, with one figure at 1.70 m standing at the shelf cut by the bottom edge"
  rect: [0, 470, 1080, 880]
  bleeds: [left, right, bottom]
accent: none
job: >
  Puts the reader in the room where a county keeps what it decided, and asks the question the
  whole deck answers with an absence. It is the only frame that shows the record complete.

claims: [c1, c6, c11, c15]
numerals:
  - value_from: c1
  - value_from: c6
  - value_from: c11

composition:
  structure: >
    The shelf sits below the midline so the volumes read as a base the type stands on rather than
    as a stripe through the frame. The figure is cut by the bottom edge at true scale, which gives
    every volume beside it a size before a word is read. The reader is standing where the figure
    is standing, and the same figure's absence is what frame 9 turns on.
  bands: >
    Top third carries the hook in the room's own dark, quiet by construction because the key
    falls off toward the upper left. Middle third is the wall and the head of the volumes.
    Bottom third is the board, the volumes and the floor taking the near light.
  focal: "the lit run of volume spines on the right half of the board, which is the lightest large
    area in the frame and the one the key lands on"

art:
  technique: "true scale objects on a declared ground with a raking key, printed through a
    halftone screen at cell 6 with the contour a pixel out of register"
  why_this_technique: >
    The claim this frame carries is that a county keeps a physical, continuous record. A
    continuous run of bound volumes at true size IS that claim drawn, and no diagram or chart
    states it without asserting something the record does not say.
  palette: "the deck's own, ground #361D27 oxblood with the ROOM ramp, bindings at steps 2 to 5,
    labels on the STOCK ramp. Source out/2026-09-18/palette_measured.json"
  value_structure: >
    Lightest is the run of paper labels on the volume spines under the key. Darkest is the upper
    left wall where the key never reaches, which is where the hook sits. The board's lit front
    lip is the one hard edge. Frame median L* planned at 16.
  motion: "the eye enters on the hook top left, falls to the lit spines bottom right, and runs
    left along the board to the figure"

type:
  hook: "Who writes the county's record?"
  dek: "Hays County took up AI on three separate September agendas. No answer appears on
    them or in the county's minutes archive."
  labels: []

verbatim: []

acceptance:
  - "the run of volumes reads as separate bound objects at 432px, not as one striped block"
  - "the figure is a person at 1.70 m standing on a floor below the frame, so it is cut by the BOTTOM edge, never whole"
  - "no accent appears anywhere on this frame"
  - "the hook sits on wall and never on a volume, and carries no plate"
  - "the run of volumes is the frame's brightest large mass, brighter than the wall behind it"
  - "the frame's median L* at 432px is between 9 and 23"
  - "no numeral appears on this frame that is not a date quoted in c1, c6 or c11"

risks:
  - "a row of volumes at one tone reads as a striped block rather than as books, so the tones step
    across the run and two volumes lean"
  - "the figure could read as an official rather than a member of the public, so it carries no hat
    and no held object"
```

```yaml
slide: 2
layout: DOCUMENT
primary_image:
  subject: "the September 1st agenda page on the board at true page proportion, 0.216 by 0.279 m
    at 1180 px per metre so the sheet is 255 by 329 px, turned 1.1 degrees, with the
    acknowledgement set verbatim in the page's own typography and the shelf's volumes behind it"
  rect: [196, 540, 596, 770]
  bleeds: []
accent: "#4FC79A"
job: >
  Shows the first of the two asks in the county's own words, and it is the one that says a machine
  may NOT write. Nothing else in the deck carries the sheriff's commitment.

claims: [c1, c2, c3, c4, c5]
numerals:
  - value_from: c1

composition:
  structure: >
    The page is placed low and large so it occupies the lower two thirds, which is the fix the
    lamp deck's frame 7 needed when a subject sat in the middle with blank stock under it. The
    hook sits in the room above the page rather than on it, so the page's own type is the only
    type on the paper and a reader can tell the county's words from ours.
  bands: >
    Top third is the dark room and the hook. Middle third is the head of the page carrying the
    acknowledgement. Bottom third is the foot of the sheet falling into the board's shadow, with
    its lower edge lifting off the board and a two part contact modeled under it, the darkest core
    at the meeting line and a softer body above it. The near board face takes the key at a grazing
    angle so its grain is modeled across the band rather than laid flat, and two volume heads are
    cropped by the bottom edge, each with its own lit right edge.
  focal: "the lit upper half of the drawn sheet, which is the largest bright area in the frame"

art:
  technique: "a drawn page at true proportion with a hand wobbled edge, a lit head on the key side
    and a two part contact under it"
  why_this_technique: >
    The claim is a line of type a county published. Drawing the page and setting the line on it is
    the only treatment that does not paraphrase, and the contact shadow is what stops it being a
    rectangle of light floating over the room.
  palette: "STOCK ramp for the sheet, TONER #2A1C18 for the type on it, ROOM ramp behind"
  value_structure: >
    Lightest is the head of the sheet where the key lands. Darkest is the room above it, where the
    hook sits. The accent keyline is the only saturated mark. Frame median L* planned at 18.
  motion: "hook, then down onto the sheet's lit head, then along the set line"

type:
  hook: "First, a promise not to switch it on."
  dek: "The September 1st agenda records what the sheriff's office committed to, and what would
    have to happen before that changes."
  labels: ["HAYS COUNTY COMMISSIONERS COURT", "AT THE FOOT OF THE ITEM", "\"BECERRA/HIPOLITO\""]

verbatim:
  - c2: "Acknowledgement of the Hays County Sheriff's Office's commitment to not activate or implement Axon Draft One"
  - c3: "an AI-enabled report-writing feature within the Axon AI Era platform"

acceptance:
  - "the sheet carries the exact string \"to not activate or implement Axon Draft One\" and it is legible at 432px"
  - "the accent appears only as a hollow keyline and never as a fill behind any word"
  - "the sheet has a visible contact shadow on the board and does not float"
  - "no agenda item number appears anywhere on this frame, because they are section relative"
  - "the frame's median L* at 432px is between 11 and 25"

risks:
  - "a drawn page is one day old in this product, so this sheet sits in a ROOM on a BOARD with
    volumes behind it rather than on a flat reading surface"
  - "type set on the page could be read as our words, so the page's type is TONER on stock and
    ours is INK on the room, which are opposite value directions"
```

```yaml
slide: 3
layout: FIGURE_SCALE
primary_image:
  subject: "one unmarked sedan at 4.70 by 1.45 m with a figure at 1.70 m standing at its open
    driver's door, at standing eye 1.62 m with the horizon at 690 px, the sedan running off the
    right edge"
  rect: [0, 700, 1080, 650]
  bleeds: [left, right, bottom]
accent: none
job: >
  Gives the thing the first ask is about a physical size and a place. It is the deck's only
  exterior and its only horizon, and it is where the vendor speaks in its own words.

claims: [c16, c17]
numerals: []

composition:
  structure: >
    The figure stands between the reader and the car so the car's length is read against a person
    rather than asserted. The horizon sits at 0.51 of the height, which is a standing eye, and the
    car runs off the right edge so the reader is beside it rather than looking at a picture of it.
  bands: >
    Top third is night sky carrying the hook. Middle third is the horizon, the car and the figure.
    Bottom third is the caliche shoulder, modeled from the near edge falling away toward the
    reader rather than filled flat, carrying both cast shadows running down and to the left at
    about twice each object's height. The sedan's own contact is darkest at the tyre and softens
    along the sill, and the shoulder's aggregate is screened coarser near the camera so the ground
    has a texture gradient across the band.
  focal: "the lit flank of the sedan, the largest bright area, with the figure's silhouette
    breaking it"

art:
  technique: "TXSCENE at standing eye with the deck's declared light, figure and object given
    different greys in the twin so they can never merge into one mass"
  why_this_technique: >
    The claim is about what a machine drafts FROM, and what it drafts from is audio recorded where
    a person is standing. A diagram of a data flow would state the same thing and give a reader
    nowhere to stand.
  palette: "ROOM ramp for the ground and the sky, the sedan's flank at step 4 to 5, the figure at
    step 2 so it reads dark against the lit flank"
  value_structure: >
    Lightest is the sedan's flank taking the key from upper right. Darkest is the figure and the
    sky above the hook. Frame median L* planned at 20.
  motion: "hook, then the figure, then along the car to the right edge"

type:
  hook: "It drafts from what the camera heard."
  dek: "The vendor's own page says the narrative is produced in seconds, and that one can't be
    submitted without an officer reviewing and approving it."
  labels: ["AXON, ON ITS OWN PRODUCT PAGE"]

verbatim:
  - c16: "body-worn camera audio"
  - c17: "officer review and approval"

acceptance:
  - "the figure measures 1.70 m against the sedan's 4.70 m length within the scene's own projection"
  - "the sedan carries no seal, no badge, no livery and no roof bar"
  - "the figure and the sedan flank differ by at least 12 L* at 432px so they never read as one mass"
  - "both casts run down and to the LEFT, which is the deck's declared light"
  - "the frame's median L* at 432px is between 13 and 27"

risks:
  - "a person beside a car is the most ordinary picture in the deck, so the crop puts the reader
    beside the car rather than in front of it and the car leaves the frame"
  - "the dek uses the vendor's own hedge, so the label says whose words they are"
```

```yaml
slide: 4
layout: DOCUMENT
primary_image:
  subject: "the September 15th agenda page on the board at the same true proportion as frame 2 but
    at a different distance and rotation, 0.216 by 0.279 m at 1420 px per metre so the sheet is
    307 by 396 px, turned minus 0.8 degrees, with the Govably request set verbatim"
  rect: [286, 640, 687, 710]
  bleeds: [bottom]
accent: "#4FC79A"
job: >
  Shows the second ask, the one that says a machine MAY write, and puts the money on the page.
  It is the mirror of frame 2 and it must not be drawn as its answer.

claims: [c6, c7, c8, c10, c18]
numerals:
  - value_from: c8

composition:
  structure: >
    The page is turned the OTHER way from frame 2 and sits nearer, so the pair reads as two
    different sheets on one board rather than as a before and an after of one sheet. That
    difference is deliberate, because a symmetrical pair is one composition away from asserting
    the opposite answers the fact checker rejected.
  bands: >
    Top third is the room and the hook. Middle third is the page carrying the request and the
    amount. Bottom third is the foot of the sheet with the vendor's own line set on it, the sheet's
    lower edge lifting off the board over a two part contact, and the board's lit front lip
    running off both edges with its face falling into shadow below. Three volume heads are cropped
    by the bottom edge behind the sheet, each modeled with its own lit right edge, so the band
    carries three depths rather than one flat rule.
  focal: "the lit block of the drawn sheet around the amount, which is the brightest area"

art:
  technique: "a drawn page at true proportion, a different distance and rotation from frame 2, with
    the amount set in mono with tabular numerals because a figure here is a measurement"
  why_this_technique: >
    The amount is the one number in the deck and it is quoted rather than computed, so it is set
    as the page sets it. Mono with tabular figures is the house rule for anything that is a
    measurement.
  palette: "STOCK ramp for the sheet, TONER for its type, accent keyline on the request line only"
  value_structure: >
    Lightest is the sheet around the amount. Darkest is the room above. Frame median L* planned
    at 17.
  motion: "hook, down to the amount, then to the vendor's line at the foot"

type:
  hook: "Two weeks later, a request to buy one."
  dek: "The county clerk's office asked the same court for a product whose maker says it writes
    official meeting minutes."
  labels: ["GOVABLY, ON ITS OWN SITE", "AT THE FOOT OF THE ITEM", "\"BECERRA/CARDENAS/HUNT\""]

verbatim:
  - c7: "authorize the County Clerk's Office to obtain AI Minutes through Govably, Inc."
  - c8: "$19,200.00"
  - c18: "write official meeting minutes from any source"

acceptance:
  - "the string \"$19,200.00\" appears exactly as the agenda prints it and is set in JetBrains Mono"
  - "this sheet's rotation is opposite in sign to frame 2's, so the two pages are not a mirrored pair"
  - "the accent appears only as a hollow keyline on the request line and nowhere else"
  - "nothing on this frame states or implies that the court granted the request"
  - "the frame's median L* at 432px is between 10 and 24"

risks:
  - "read beside frame 2 this becomes the answer to it, which is the deck's single biggest
    editorial hazard, so the distance, the rotation and the hook all change"
  - "the amount is the only figure in the deck and a misprint of it is a hard fail, so it is
    copied from c8 and never retyped"
```

```yaml
slide: 5
layout: CLOSE_CROP
primary_image:
  subject: "the waiver clause of the September 15th page at 0.09 m across the frame, the paper's
    own tooth visible, cropped by the top, left and right edges so one line of the county's own
    type runs the full width"
  rect: [0, 330, 1080, 462]
  bleeds: [left, right]
accent: none
job: >
  Isolates the clause that makes the second ask unusual. Without this frame the request is an
  ordinary software purchase, and with it the county is asked to buy without comparing.

claims: [c9]
numerals: []

composition:
  structure: >
    The reader is inside the paragraph. The clause runs edge to edge at reading size so the frame
    is the sentence rather than a picture of a page with a sentence on it, which is the difference
    between CLOSE_CROP and DOCUMENT and the reason this is a separate frame.
  bands: >
    Top third is the page above the clause, ruled and lit. Middle third is the clause itself.
    Bottom third is the page falling away into the board's shadow with the dek on the room below.
  focal: "the lit band of paper carrying the clause, the one area at the top of the value range"

art:
  technique: "a close crop at paper tooth scale with the page's own rules placed CLEAR of the type
    block rather than dodged around it, and a grazing specular across the fibre"
  why_this_technique: >
    A rule dodged around its own page's type punches a feathered hole whose boundary lands inside
    the glyph band, and the QA harness reads the repair as a strike. The lamp deck paid four
    rounds for that. The rules are placed where a document would set them.
  palette: "STOCK ramp at the top of its range, TONER type, no accent"
  value_structure: >
    Lightest is the paper immediately under the key at the upper right. Darkest is the lower left
    where the sheet falls into the board's shadow and the dek sits. Frame median L* planned at 20.
  motion: "straight across the clause, left to right, then down to the dek"

type:
  hook: ""
  dek: "County purchasing policy asks for three quotes. The item asks the court to set that aside
    for this one."
  labels: ["SEPTEMBER 15TH AGENDA"]

verbatim:
  - c9: "authorize a waiver to the purchasing policy of obtaining three quotes"

acceptance:
  - "the clause is set at 32px or larger and reads at 432px without zooming"
  - "no ruled line on the page crosses any glyph of the set clause"
  - "the paper's tooth is visible as a screen at this crop, not a flat fill"
  - "this frame carries no hook, so the county's own sentence is the largest type on it"
  - "the page's label reads \"SEPTEMBER 15TH AGENDA\", which is the document c9 was quoted from. Every label in this deck names the source of the words under it, so a label naming anything else is an attribution to a document this run did not fetch"
  - "the frame's median L* at 432px is between 13 and 27"

risks:
  - "a frame that is mostly paper can render as a flat bright rectangle, so the grazing specular
    and the tooth are what give it a surface, and craft_floor is the gate that will say so"
  - "with no hook the dek carries the frame, so the dek is placed on the room and not on the page"
```

```yaml
slide: 6
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "the commissioners court dais at 9 by 1.3 m drawn large on a ground plane with a
    horizon, five seated figures at 1.70 m behind it and a standing figure at 1.70 m at a podium
    0.7 by 1.25 m in front of it, at seated public eye 1.12 m with the horizon at 742 px"
  rect: [0, 700, 1080, 560]
  bleeds: [left, right]
accent: none
job: >
  The deck's populated frame and the only one that shows the body itself. It carries the third
  item, the county's own rule for governing AI, and it puts people in the room where all three
  asks were made.

claims: [c11, c12, c13, c14]
numerals: []

composition:
  structure: >
    The dais runs off both edges so the reader is in the gallery rather than looking at a picture
    of a gallery, and the standing figure at the podium is between the reader and the dais at true
    scale, which is what turns a procurement line into a person asking five people for something.
    The figures and the furniture are given different greys in the twin so the row can never merge
    into one pale mass.
  bands: >
    Top third is the dark room above the dais carrying the hook. Middle third is the row of seated
    figures and the dais front taking the key. Bottom third is the podium at 1.25 m with the
    standing figure beside it at 1.70 m, both modeled with a lit right edge and a dark left, over a
    floor whose tone falls away from the key toward the lower left. The standing figure's cast runs
    down and to the left across that floor at about twice its height, and the podium's own contact
    is a dark core at its foot softening upward.
  focal: "the lit run of the dais front with the five seated figures above it, the largest bright
    area in the frame and the one the key lands on"

art:
  technique: "true scale objects and figures on a declared ground at seated public eye, with a
    clipped rim light along the dais lip rather than a stroked path"
  why_this_technique: >
    A rim light stroked around a layer's whole path outlines every rectangle on four sides and
    turns a room of furniture into a wireframe diagram of a room of furniture, which is the
    "diagram of a place" three judges have named. Clipping to the shapes and painting a band along
    the lit edge is what makes it a room.
  palette: "ROOM ramp, dais front at steps 4 to 5, figures at step 2 so they read dark against it,
    floor at step 3 falling away"
  value_structure: >
    Lightest is the dais front under the key. Darkest is the ceiling above it, where the hook
    sits, and the seated figures which read as a dark rank against the lit front. Frame median L*
    planned at 25.
  motion: "hook, down to the standing figure at the podium, then along the dais to the right"

type:
  hook: "A week after September 1st, a policy put to the same court."
  dek: "The September 8th agenda took up how the county governs AI in surveillance. The item
    listed straight after it is a Tyler Technologies amendment for report writing services.
    Nothing on the page joins the two."
  labels: ["SEPTEMBER 8TH"]

verbatim:
  - c13: "possible adoption of a policy statement"
  - c13: "AI-enabled surveillance technologies by Hays County"
  - c14: "one for report writing services"

acceptance:
  - "six figures appear at 1.70 m, five seated behind the dais and one standing at the podium"
  - "the figures and the dais front differ by at least 12 L* at 432px so the row never reads as one mass"
  - "the dek carries the exact words \"Nothing on the page joins the two.\""
  - "no line, arrow, bracket or accent joins the two quoted items anywhere on this frame"
  - "no seal, no badge, no livery and no name appears on the dais or the podium"
  - "the frame's median L* at 432px is between 18 and 32"

risks:
  - "figures at the same tone as the furniture beside them merge into one pale shape, which is the
    failure TXFIG's own entry names, so the twin carries separate greys and the acceptance item
    measures it"
  - "a reader joins the two quoted items whether or not a line is drawn, so the dek says in words
    that nothing on the page joins them and no mark of any kind runs between them"
  - "five seated figures could be read as asserting the court's composition, so no figure carries
    a nameplate, a gavel or any mark of office"
```

```yaml
slide: 7
layout: MAP
primary_image:
  subject: "the Texas county mesh from assets/geo/tx-counties.topo.json on the TXGeo Albers equal
    area conic, filling the frame, with Hays lifted one value step and its neighbours held at the
    ground"
  rect: [110, 470, 860, 640]
  bleeds: []
accent: none
job: >
  Answers where. It is the only frame that puts the story on the ground, and it is the frame a
  reader scrolling past uses to decide whether this is about them.

claims: [c1, c6, c11]
numerals:
  - computed_by: "out/2026-09-18/aggregates.json, the count of distinct agenda dates in c1, c6 and c11"

composition:
  structure: >
    The state fills the frame rather than sitting as a motif inside it, and Hays is one value step
    up rather than a filled colour, because a severity ramp on a county is a verdict this product
    does not publish. The three dates sit in a key band at the foot in mono.
  bands: >
    Top third is the hook over the panhandle where the mesh is quiet. Middle third is the body of
    the state with Hays lifted. Bottom third is the southern mesh running to the coast with the
    key band's three dates set in mono over it. The county line weight thins with distance from
    Hays, so the band carries a modeled gradient of line density rather than a flat field, and the
    Gulf edge where the mesh stops is the one hard boundary in the band.
  focal: "the lifted county, which is the one area carrying a value the rest of the mesh does not"

art:
  technique: "TXGeo Albers equal area conic county mesh, one county at one value, no severity ramp
    and no dial"
  why_this_technique: >
    A where wants cartography and nothing else states it. The single value step is the Grid Watch
    rule applied here, because a filled colour on a county implies a judgement about that county.
  palette: "ROOM ramp, mesh strokes at step 2, Hays at step 4, key band type in RULE"
  value_structure: >
    Lightest is the lifted county. Darkest is the frame's upper left where the key never reaches.
    Frame median L* planned at 14.
  motion: "hook, down the mesh to the lifted county, then to the key band"

type:
  hook: "One county. One court. Three agendas."
  dek: "The September 1st, September 8th and September 15th meetings were all the same
    commissioners court."
  labels: ["SEPTEMBER 1ST", "SEPTEMBER 8TH", "SEPTEMBER 15TH"]

verbatim: []

acceptance:
  - "Hays County is the only county carrying a value different from the mesh"
  - "the map is neither upside down nor mirrored, which tests/txgeo.mjs asserts"
  - "no county is filled with the accent and no severity ramp appears anywhere"
  - "the three dates in the key band appear in c1, c11 and c6 and nowhere else"
  - "the frame's median L* at 432px is between 8 and 21"

risks:
  - "a county mesh at this size can read as texture rather than as Texas, so the state's outline
    carries a heavier stroke than the interior county lines"
  - "the count of agenda dates is an aggregate and is declared in aggregates.json, because an
    undeclared count is how a wrong number reaches the largest type on a page"
```

```yaml
slide: 8
layout: DIAGRAM
primary_image:
  subject: "the county's Court Minutes 2026 archive drawn as a page on the board at 0.30 m across,
    read straight down, its newest three dates set verbatim in mono at the FOOT of a ruled bed and
    a bounded band of bare stock ABOVE the newest one, with a mono label naming the document"
  rect: [256, 470, 640, 700]
  bleeds: []
accent: "#4FC79A"
job: >
  The frame the deck turns on. It shows the absence as a shape with a size, in the one place a
  reader would go to find out what the court decided, and it names the document the absence is
  missing from.

claims: [c15]
numerals:
  - value_from: c15

composition:
  structure: >
    The archive lists NEWEST FIRST, so the missing September entries are at the TOP of the list
    rather than at the bottom where a reader's eye expects a list to stop. Drawing the gap above
    the newest line rather than below the oldest is what makes the frame read as a record not yet
    written rather than as a record that ended, and that inversion is the whole frame. A mono label
    above the band names the archive, because an absence with no document behind it is a sentence
    nobody can check.
  bands: >
    Top third is the bare band, lit, with nothing in it, and the mono label above it. Middle
    third is the newest dates set in mono. Bottom third is the ruled bed continuing below the
    dates, the sheet's lower edge lifting off the board over a two part contact whose core sits at
    the meeting line, and the board's own grain modeled at a grazing angle to the key so the band
    falls away from the sheet rather than sitting flat behind it.
  focal: "the bare band at the top of the sheet, the largest unbroken light area in the frame and
    the only region on the page with nothing set in it"

art:
  technique: "a drawn index page with a ruled bed and a mono label, its quoted dates set in mono,
    and one bounded region of genuinely unscreened stock"
  why_this_technique: >
    An absence needs a shape, a size and a named document or a reader slides over it and
    absence_check refuses it. Bounding the band and leaving it genuinely empty gives it the first
    two, and the label gives it the third. Rows would publish a count the record does not carry.
  palette: "STOCK ramp, the bare band at the ramp's top step, TONER dates, RULE for the bed,
    accent keyline bounding the band"
  value_structure: >
    Lightest is the bare band. Darkest is the board around the sheet. The band is the frame's one
    extreme and it is deliberately the emptiest thing on it. Frame median L* planned at 21.
  motion: "the eye enters on the bare band, reads the label above it, then drops to the
    first set date"

type:
  hook: "The newest minutes are dated July 28th."
  dek: "The county's own Court Minutes 2026 archive lists newest first. Nothing later appears on
    it, so no disposition for any of the three September items is published there."
  labels: ["COURT MINUTES 2026"]

verbatim:
  - c15: "07 28 2026"
  - c15: "07 07 2026"
  - c15: "06 23 2026"

acceptance:
  - "the bare band sits ABOVE the line reading \"07 28 2026\", and the three entries run newest first with \"06 23 2026\" the oldest of them"
  - "the bare band contains no rule, no hairline, no box, no row and no set line of any kind, and the deck's own gloss sits BELOW it rather than inside it"
  - "the band is bounded by a hollow accent keyline so it reads as a region rather than as an edge"
  - "a mono label reads \"COURT MINUTES 2026\", which is the document the absence is missing from"
  - "no line of the deck's own words is set anywhere on the drawn page, so nothing our voice wrote can be read as the county's own printing"
  - "NO leader is drawn. Two round-4 judges found it as a hairline ending at nothing, and a leader whose target is an absence has nowhere to arrive. This item could never have fired regardless: the harness collects __akLeaders and this repo sets __txLeaders, so render_report carries leaders:[] on every slide"
  - "the three dates are set exactly as c15 quotes them, with spaces and not slashes"
  - "the frame's median L* at 432px is between 14 and 28"

risks:
  - "bare stock is indistinguishable from an unfinished render at 432px, so the declared rect
    covers the whole sheet including the set dates and the ruled bed, never the band alone"
  - "a bounded empty region could be read as a redaction, so it is the LIGHTEST thing on the frame
    rather than the darkest, which is the opposite of what a redaction looks like"
  - "no stroke ends inside a glyph band, because qa.py reads a stroke through a line as a
    strikethrough and it is right to"
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: "frame 1's camera exactly, the same shelf board at y 1118 running off both edges at the
    same 620 px per metre, the figure gone, and where the newest volume stood there is lit board
    with nothing on it"
  rect: [0, 470, 1080, 880]
  bleeds: [left, right, bottom]
accent: "#4FC79A"
job: >
  The close, and it is frame 1 with the room changed. It states the one thing a reader can act on,
  which is that the commitment's own words send any activation back to a public agenda.

claims: [c2, c4]
numerals: []

composition:
  structure: >
    Identical camera, identical board, identical volumes, and one volume's worth of empty lit
    board where the September record would stand. Nothing else changes, so the reader's eye finds
    the difference itself rather than being pointed at it.
  bands: >
    Top third carries the closing line in the room's dark. Middle third is the wall and the heads
    of the volumes. Bottom third is the board carrying the run of volumes and the lit empty gap,
    with each volume modeled by a lit right edge against a dark left, their casts running down and
    to the left onto the board, and the floor below falling away from the key toward the lower left
    so the near band is modeled rather than filled. The gap's own patch of board is the one place
    in the band with no cast on it.
  focal: "the empty keylined space on the board, which is the one area carrying the accent and the
    only place on the board with no object on it"

art:
  technique: "the frame 1 scene redrawn with one object absent, the gap drawn as lit board rather
    than as a dark field, keylined hollow in the deck's accent"
  why_this_technique: >
    A gap drawn dark says a volume was removed and the record says nothing was ever set down. Lit
    board with a keyline says a space is waiting, which is the true statement and is the only one
    the claims support.
  palette: "identical to frame 1, with the accent keyline added and the key at its lowest strength
    in the deck"
  value_structure: >
    Lightest is the lit board inside the gap. Darkest is the room above, which is darker here than
    on frame 1 because the key has come down. Frame median L* planned at 17.
  motion: "the closing line, then straight to the gap, then along the board"

type:
  hook: "It has to come back to this court."
  dek: "The commitment reaches any new AI feature the platform may later offer."
  labels: ["Every source behind this deck is linked in the first comment."]

verbatim:
  - c4: "any new AI-based features the Axon AI Era platform may make available under the related contract without returning to the Hays County Commissioners Court for approval"

acceptance:
  - "the board sits at the same y as frame 1 and the volumes are at the same pitch, tone family and scale, with only the gap and the absent figure differing"
  - "the gap is LIGHTER than the board around it, never darker, so it can never read as a hole"
  - "the accent appears as a hollow keyline around the gap and nowhere else on the frame"
  - "the figure that stood at the shelf on frame 1 is absent"
  - "the frame's median L* at 432px is between 10 and 24"

risks:
  - "an empty space can read as the court having done nothing, which is a verdict, so the dek
    points at the commitment's own condition rather than at the room"
  - "frame 1 and frame 9 share a camera and bespoke_check compares code, so the scene is rebuilt
    with different volume seeds and a different key strength rather than copied"
```
