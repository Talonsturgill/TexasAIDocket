# Storyboard — carousel no. 23, September 13th, 2026

Docket items `tx-2026-0150` and `tx-2026-0151`. Claims file `out/2026-09-13/claims.json`.

## The synthesis, and why

Three directors pitched. The SET lens is the spine, because its structural law answers the
machine's own top instinct, which is that a count is only drawn where a document counted it. Its
frame 7 is the deck's turn and the strongest image any of the three proposed. Its accent law is
the argument stated as a colour, and its reading of the gazetteer is the correct one, which is
that the committed places file holds counties and metros and no cities, so no county is lit and
no county is named anywhere in this deck.

Grafted from the SCALE lens, frame 3, a child seated on the end of a made adult bed with most of
the mattress empty beside them. It is the most screenshotable image proposed and it makes the
size argument without a word.

Grafted from the EVIDENCE lens, frame 6, the reading workstation with a radiologist doing the
work, and its construction law, which is that every lit surface in this deck carries content and
none is a plain plate. That law is the direct guard against the plate-with-a-headline failure
the illustration system was written to end.

Rejected, and each for a reason. The SCALE lens wanted an untruncated ground dimension with a
confidence interval drawn as a physical extent. It is a good frame and it is a chart in a coat,
two decks after this project shipped one. The EVIDENCE lens wanted a Galveston seawall, and it
named that frame as its own cuttable one. The SCALE lens wanted the accent on every child. The
SET lens's accent law is sharper and is used here instead.

## The register

Night paper and one pale ink, printed. Scenes drawn in greys into an offscreen twin at true
scale, then `TXINK.print` lays paper, screens tone into ink, lays a contour plate a pixel out of
register, and paints one accent flat. Figures are 0.85 to 1.83 m. A hospital block is 60 m. A
hospital bed is 2.2 m. The scanner is drawn from parts in metres and is not in the catalogue,
which goes in `knowledge/carousel/UPGRADE_BACKLOG.md` as a proposal.

**THE ACCENT MARKS THE SECOND PAPER**, bluebonnet `#4E5FA8`, on frames 4, 5 and 6 and nowhere
else, so the colour is a chapter mark a reader can follow rather than a highlighter. It came off
frame 8 in the repair pass, where it had been two flat rules laid beside the map's two points and
running away from them. Frame 7 is a field of children and carries none, which is the deck's
argument made in colour rather than in a sentence. The accent never sets a glyph.

**EVERY LIT SURFACE CARRIES CONTENT.** A display carries a study, a page carries type, a box
carries a label. No frame's bright region is an empty rectangle.

## The rotation

    1 FIGURE_SCALE  2 DOCUMENT  3 CLOSE_CROP  4 DIAGRAM  5 GRID
    6 OBJECT_AND_CAPTION  7 SPLIT_HORIZON  8 MAP  9 FULL_BLEED

Nine distinct, no consecutive repeat, TYPE_AS_OBJECT unused, FULL_BLEED and CLOSE_CROP two
between them, six frames bleeding an edge. `TXLAYOUT.check` returned an empty list.

## THE NINE

```yaml
slide: 1
layout: FIGURE_SCALE
primary_image:
  subject: an MRI scanner drawn from parts in metres, front face 2.20 m wide by 1.95 m tall and 1.70 m deep, bore aperture 0.60 m centred 1.05 m above the floor, its patient table 2.30 m long with the deck at 0.78 m, with a child at 1.22 m standing at the foot of the table and an adult at 1.72 m behind the child
  rect: [140, 380, 940, 660]
  bleeds: [right]
accent: none
job: >
  Stop the scroll on the size difference the panel's own sentence is about, drawn as two bodies
  and one machine on one floor, and set the deck's register on frame one.
claims: [c2, c5]
numerals: []
composition:
  structure: >
    Camera at 1.35 m, horizon 700, focal 780. The scanner front face sits at Z 4.6 m and runs off
    the top and right edges, so the machine is cropped by the reader's own frame rather than
    floating in it. The table runs toward the camera and leaves the bottom edge. The child stands
    at Z 3.1 m at the table's foot, the adult at Z 4.2 m behind and left of the child, and the
    two figures give the bore its size.
  bands: >
    TOP third, the dark scanner room wall carrying the kicker and the hook, with the magnet's
    shoulder entering it from the right. MIDDLE third, the bore mouth, both figures and the table.
    BOTTOM third, the scanner room floor with its joints receding toward the horizon, the patient
    table leaving the frame, and both figures' contact shadows lying across the stipple texture
    before the print fades into the solid paper band the dek sits in.
  focal: >
    The bore mouth, an AREA of about 210 by 150 px, the darkest ellipse in the frame, with the
    child's head band about 90 px to its left at the same height.
art:
  technique: "TXSCENE at true scale with a bespoke sprite drawn in metres from rect, poly and ellipse parts, TXFIG for both figures, printed by TXINK as a stipple at cell 5, seven dots a cell."
  why_this_technique: >
    A stipple is the field guide plate and it is the right register for a comparative series of
    bodies, where a reader is being asked to look at two things side by side rather than to read
    a photograph. It also keeps its dots as dots at 432 px, where a fine halftone on a matte
    composite shell would grey out into a wash.
  palette: >
    suite #1B1E21 paper, limestone #EDE6D6 ink. Greys in the twin, shell #9CA3A8 for the
    scanner's painted composite with its lit face #DDE2E4, bore #0A0C0E for the aperture with its
    lip #E6EBEC over ring #767D83 and its far wall #2B3136, wall #0C0E11, floor #4C5359, table
    deck #EDF1F2 over its edge #868E94, pedestal #5E666C, figures #E2E6E7.
  value_structure: >
    The ceiling is the darkest zone and carries the type. The scanner's lit top face is the
    lightest mass. The bore is the one true black inside the image. Frame median L* planned at 22.
  motion: >
    The eye lands on the hook, drops to the bore, and is carried left down the child to the floor.
type:
  hook: "Children are not small adults."
  dek: "The panel's own sentence says children go through continuous physiologic and anatomic changes, which is why a model fitted to adults is not the model a child needs."
  labels: ["AJR EXPERT PANEL REVIEW", "SEPTEMBER 9TH, 2026", "01 / 09", "c2 c5   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim:
  - c5: "continuous physiologic and anatomic changes"
acceptance:
  - the frame carries "continuous physiologic and anatomic changes"
  - the adult figure is at least 1.35 times the child's pixel height in the render
  - at 432 px the child and the adult are tellable apart by head to height ratio, not only by height
  - the bore reads as a dark ellipse inside a lighter face, not as a black rectangle
  - both figures carry a contact shadow on the floor and neither floats
  - the scanner's rect touches the right edge
  - the two figures are PALE against the dark wall and do not merge into it
  - the stipple dots are visible as dots in the floor at 432 px
  - no screen dot sits inside the hook's or the dek's glyph band
risks:
  - "a bespoke machine drawn from parts reads as a slab. The bore, the table and the lit top face are the three things that stop it, and all three have to survive to 432 px"
  - "the child reads as a short adult. TXFIG's child proportion has to do real work at feed size"
```

```yaml
slide: 2
layout: DOCUMENT
primary_image:
  subject: the panel review's first page lying on the scanner's patient table pad turned 1 degree, cropped by the left and right edges with the screened pad running below it to the bottom edge, the table rail crossing its lower left corner, carrying its own running head and the underrepresentation sentence set on it with the four places the sentence names underlined in it
  rect: [0, 400, 1080, 950]
  bleeds: [left, right]
accent: none
job: >
  Put the claim on the document that made it, so the sentence belongs to the panel rather than to
  this deck, and show where the page physically sits.
claims: [c1, c2, c3, c4]
numerals:
  - value_from: c2
  - value_from: c3
composition:
  structure: >
    Thirty degrees down onto the page in its own plane. The sheet is turned 1.5 degrees off
    square and is crossed at its lower left by the table rail, so the bright region is not a
    rectangle by construction, which is what `construction_check` reads. A second sheet sits
    behind and below it, offset 18 px, so the front sheet reads as lifted.
  bands: >
    TOP band, a shallow strip of pad in shadow carrying the kicker and the counter and nothing
    else. MIDDLE, the page itself from y 268 to y 834, running head, rule and the sentence, with
    the rail crossing its lower left, its cast shadow modelling the pad's depth beneath it and
    the page's own light falling away into the shadow at its lower right. BOTTOM, the pad's
    stipple and screen texture running under a solid band of the deck's own ground that carries
    the hook, with the rail's shadow and the pad's own tone reaching into it. THIS FRAME AND
    FRAME 7 ARE THE TWO THAT DO NOT OPEN kicker, hook, image, dek: the page comes first and the
    sentence about it comes second, which is the order a reader meets a document in.
  focal: >
    The sentence block, an AREA of about 700 by 190 px, the only fully lit type in the frame.
art:
  technique: "a drawn sheet with a TXINK.wobble edge over a line screen at cell 6 and minus 18 degrees, with DOM type set on flat paper above the print."
  why_this_technique: >
    The line screen carries only the pad and the second sheet. The front sheet is flat paper with
    no screen on it at all, and that difference is what makes one page read as lifted off
    another. A halftone here would put dots inside the document's own typography.
  palette: >
    suite #1B1E21 paper, limestone #EDE6D6 ink, page #E3DED0 for the sheet with its own ink
    #1A1C1A and its rule #BCB4A0 and the reader's underline #8A7F63, the pad graded from #28332F
    to #43514B, second sheet #9E9A8C, rail #C2C8C6 over its shadow side #6E7674, wall #0E1114.
  value_structure: >
    The pad is the darkest field and carries the type. The page is the lightest plate and is the
    only unscreened area in the frame. Frame median L* planned at 46.
  motion: >
    Hook at top left, down the page's own left margin, along the sentence, out at the rail.
type:
  hook: "The panel named where the gap is."
  dek: "Artificial intelligence (AI) applications have transformed radiology, yet pediatric medical imaging remains substantially underrepresented in AI development, validation, regulation, and implementation."
  labels: ["THE DOCUMENT", "10.2214/AJR.26.35523", "02 / 09", "c1 c2 c3 c4   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim:
  - c4: "pediatric medical imaging remains substantially underrepresented in AI development, validation, regulation, and implementation"
  - c1: "Pediatric Artificial Intelligence in Radiology"
acceptance:
  - the page reads "pediatric medical imaging remains substantially underrepresented" and no line on it reads "adequately represented"
  - the page's own bounding box is rotated between 0.5 and 1.5 degrees off square in the render
  - the page is turned off square and is crossed by the rail, so its lit region is not a rectangle
  - the verbatim sentence is legible at 1080 px and its block is identifiable as type at 432 px
  - the second sheet is visible behind the first as a wedge along its top edge
  - the page runs off the left and right edges and has a margin on neither, and the screened pad carries the frame below it
  - the page carries a light, brightest at its head and falling away to its lower right, so no part of it is a flat empty plate
  - the four words the sentence names are UNDERLINED where the panel wrote them, and no numbered row appears anywhere on the page
  - the line screen appears on the pad and NOT on the front page
  - the DOI on the page matches c3 character for character
risks:
  - "a page on a dark ground is the commonest plate in this project's history. The turn, the crop and the rail are what stop it, and all three must be measured on the render"
```

```yaml
slide: 3
layout: CLOSE_CROP
primary_image:
  subject: a made hospital bed at 2.2 by 1.3 m cropped by the left, right and bottom edges at mattress height, with a child at 1.14 m seated on the near end in ordinary clothes with their feet clear of the floor, and about 1.5 m of made mattress flat and empty beside them
  rect: [0, 360, 1080, 590]
  bleeds: [left, right]
accent: none
job: >
  Make the size argument physical, with an object every reader has seen and a body that does not
  fit it, so that off label stops being a phrase and becomes a picture.
claims: [c7]
numerals: []
composition:
  structure: >
    Camera at 0.95 m, mattress height, horizon off the frame entirely. The bed runs off three
    edges so the reader is inside the bay rather than looking at it. The child sits at the near
    left on a 0.55 m seat with knees over the edge. The empty mattress occupies more than half
    the frame's width to the child's right, which is the whole argument.
  bands: >
    TOP third, the bay wall in shadow, carrying the kicker, the hook and the dek. MIDDLE third,
    the child, the mattress and the bed's near rail rolled down. BOTTOM third, the bed frame, the four castors with their two part contact shadows, and the
    tile floor's halftone texture receding toward the far wall before the print fades to paper
    under the furniture band.
  focal: >
    The empty mattress, an AREA of about 560 by 210 px, the lightest plate in the frame, read
    against the child's silhouette at its left end.
art:
  technique: "TXOBJ hospital_bed and a TXFIG seated child on the scene bench, printed as a halftone at cell 9 and 18 degrees, with two part contact shadows at all four castors."
  why_this_technique: >
    A coarse halftone puts the reader inside the weave of a bed sheet, which is what a close crop
    at mattress height is for. Cell 9 is the coarsest cell that still resolves the child's head
    at 432 px, and the two part contact is the named guard against the bed floating, which is
    this technique's own recorded failure.
  palette: >
    suite #1B1E21 paper, limestone #EDE6D6 ink. Greys, sheet #E6EAEC for the made mattress, bed
    frame #7E858A, floor #5E6368, the child #15181A against the pale mattress, wall #0E1114.
  value_structure: >
    The wall is the darkest zone and carries the type. The mattress is the lightest. The floor is
    a mid field of coarse dots. Frame median L* planned at 34.
  motion: >
    Hook at top, down to the child, then right along the empty mattress and out of frame.
type:
  hook: "Off label, in the panel's own words."
  dek: "The review names the practice among its ethical and regulatory concerns for children, beside consent for secondary data use and the need for postdeployment surveillance."
  labels: ["THE CONCERN THE PANEL NAMES", "ETHICS AND REGULATION", "03 / 09", "c7   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim:
  - c7: "off-label use of adult-trained AI models"
acceptance:
  - the hook reads "Off label" and no label on this frame reads "approved for children"
  - the mattress plate is the lightest region in the frame, above L* 80, and the child's silhouette the darkest mark on it, under L* 20
  - the child wears ordinary clothes, with no gown, no drip stand, no monitor and no raised rail
  - the child's feet are clear of the floor by a visible gap
  - the empty mattress runs from the child to the right edge and is the lightest plate in the frame
  - all four castors carry a contact shadow whose median L* differs from the floor beside it by 4 or more
  - the bed's rect touches the right edge
risks:
  - "a child on a hospital bed tips into a charity appeal in one bad drawing. No face, no gown, no equipment, and the caption stays inside the record's own words"
  - "the halftone at cell 9 is coarse enough to lose the child's head at feed size. Measure it before the first panel"
```

```yaml
slide: 4
layout: DIAGRAM
primary_image:
  subject: one filing box at true scale, 0.40 by 0.28 m, taped shut and carrying a dated label, standing on a 0.90 m cart in the control room with the window into the magnet room behind it, a person's forearm at the left frame edge for scale
  rect: [40, 360, 1040, 900]
  bleeds: [right]
accent: "#4E5FA8"
job: >
  Show what a fixed model is, which is a thing that was sealed and then not touched, and hang the
  second paper's three figures off the object that holds them.
claims: [c16, c17, c20, c22, c26]
numerals:
  - value_from: c20
  - value_from: c22
composition:
  structure: >
    Square on to the box at 0.9 m object distance, camera at 1.20 m. The box sits centre right on
    the cart. The control room window is a lighter band behind it at 2.8 m carrying the magnet
    room beyond. A forearm enters from the left edge at the cart's height so the box has a size.
    Four leaders run from mono labels to four different physical features, the tape seal, the
    dated label, the box's body and the window.
  bands: >
    TOP third, the dark ceiling and the upper wall, carrying kicker, hook and dek. MIDDLE third,
    the window band, the box, the cart top and the four leaders. BOTTOM third, the cart's legs with their shadows on the floor, the forearm entering at the
    left edge, and the floor's hatch texture carrying the cart's mass down to the furniture
    band.
  focal: >
    The taped seal across the box lid, an AREA of about 190 by 60 px, the one accent in the frame.
art:
  technique: "TXOBJ filing_box at true scale on the scene bench under a hatch screen at cell 7 and 38 degrees, three threshold passes at three angles, with leaders authored as SVG paths in the DOM ending short of every glyph band."
  why_this_technique: >
    A diagram is an engraving with labels on it and the cross hatch is its native surface. Board
    and tape are exactly what a three angle hatch draws well, and the leaders being DOM paths
    rather than canvas strokes is what keeps the occlusion gate from reading a leader through a
    letterform as a strikethrough.
  palette: >
    suite #1B1E21 paper, limestone #EDE6D6 ink, accent bluebonnet #4E5FA8 on the seal and the
    label card, over its own shade #3F4E8C. Greys, board #D2C9AE for the box's front with its lid
    skirt #C3B99B, its lit top #F1E9D3 and its shaded right face #8F8872, hand hole #5C5646, card
    rule #DCE2F2, cart #7E858B, window glass #AFB7BB in a #4E555A frame, the bore beyond it
    #E2E7E9, arm #C8CCCD, wall #101316, floor #2B3137 with the runner the cart stands on at
    #3D444B.
  value_structure: >
    The wall and ceiling are darkest and carry the type. The window band is the lightest field and
    the box sits against it. Frame median L* planned at 30.
  motion: >
    Hook, down the left leader to the seal, then clockwise round the other three labels.
type:
  hook: "They sealed the model before they tested it."
  dek: "The second paper fitted its model on one brain metastasis cohort, kept 7 features, and then ran the fixed model on 69 patients it had never met."
  labels: ["A BRAIN METASTASIS SURVIVAL MODEL", "TEXAS DEPARTMENTS AMONG ITS AUTHORS", "04 / 09", "c16 c17 c20 c22 c26   TEXAS AI DOCKET", "texasaidocket.com", "198 FITTED", "7 FEATURES KEPT", "69 MET", "SEALED"]
verbatim:
  - c20: "without refitting or recalibration"
acceptance:
  - a label on the box reads "SEALED" and no label on this frame reads "refitted and recalibrated"
  - every leader terminates on the feature it names, within 24 px of that feature's own coordinates, asserted by the frame's own __txLeaders declaration
  - no leader crosses a glyph, and every leader ends short of the label's glyph band
  - the accent appears on the seal and the label card and on nothing else, under 8 percent of the frame
  - the label card carries 7 ruled marks, one per retained feature, and is not an empty swatch
  - the box reads as three planes at three values with a cast shadow on the cart top under it
  - the window band runs off the right edge
  - the box reads as a box with a lid and a taped seam at 432 px, not as a rectangle
  - the three numerals on this frame are 198, 7 and 69 and each is present in c20 or c22
risks:
  - "a filing box is one step from clip art. True scale, the forearm, the cart and the window behind are the four things that make it a place"
  - "the hatch at cell 7 over board and tape may flatten the seal. If it does the seal gets its own value in the twin rather than a heavier accent"
```

```yaml
slide: 5
layout: GRID
primary_image:
  subject: two blocks of identical front view figures at one long lens scale, the upper block 198 units in nine rows of 22, the lower block 69 units in three rows of 22 and a short row of 3, a hairline gutter between them, each block's set named in mono beneath it
  rect: [70, 420, 940, 700]
  bleeds: []
accent: "#4E5FA8"
job: >
  Make the two cohorts countable, so the reader sees the size of what was tested against the size
  of what was learned rather than reading two numbers about it.
claims: [c16, c20]
numerals:
  - value_from: c20
  - computed_by: "out/2026-09-13/compute.py, the block geometry at 22 columns from the two cohort sizes in c20"
composition:
  structure: >
    A long lens at focal 2400 and Z 16, so every unit is exactly the same height and a count
    cannot be misread as perspective. The two blocks share a left edge and sit clear of every
    frame edge, because a block that runs off an edge cannot be totalled and this one is meant to
    be. The gutter is 34 px, wider than any row gap inside a block.
  bands: >
    TOP third, flat dark ground carrying the kicker, the hook and the dek. MIDDLE third, the
    upper block of 198 and the gutter. BOTTOM third, the lower block of 69 units as one accented mass with its own silhouette, its
    mono label beneath it, and the line screen's vertical texture on the ground carrying depth
    under the furniture band.
  focal: >
    The lower block, an AREA of about 940 by 200 px, the only accented mass in the frame, read
    against the taller block above it.
art:
  technique: "TXFIG front view units at one scale on a long lens, over a vertical line screen at cell 4, with each block's mono label measured off the laid out string by TX.svgPlate."
  why_this_technique: >
    An isotype with a body instead of a dot is the one form where the unit means a person, which
    is the whole point of both papers. The long lens is what stops a count from being a
    perspective, and a fine vertical line screen reads as texture at feed size and as engraving
    at full size without competing with the units themselves.
  palette: >
    suite #1B1E21 paper, limestone #EDE6D6 ink, both blocks drawn in one ink #E6EAEC and the
    lower block's hue remapped to accent bluebonnet #4E5FA8 inside the print. Ground #16191C, the
    label plates #12151A.
  value_structure: >
    The ground is uniformly dark and carries the type. The upper block is ink and the lower block
    is accent, so the two populations differ in hue rather than in value. Frame median L* at 26.
  motion: >
    Hook, down to the top left of the upper block, across it, over the gutter into the lower block.
type:
  hook: "Fitted to 198. Tested on 69."
  dek: "The model was built on a public cohort. It then ran on an independent cohort without refitting."
  labels: ["THE BRAIN METASTASIS COHORTS", "ONE UNIT IS ONE PATIENT", "05 / 09", "c16 c20   TEXAS AI DOCKET", "texasaidocket.com", "198  THE COHORT IT WAS BUILT ON", "69  THE COHORT IT HAD NOT MET"]
verbatim:
  - c20: "198"
  - c20: "69"
acceptance:
  - the frame carries "THE COHORT IT HAD NOT MET"
  - the upper block contains exactly 198 drawn units and the lower exactly 69, counted by the frame's own script, which throws if either count is wrong
  - the two blocks are separated by a gutter of at least 40 px in the render
  - the gutter between the two blocks is wider than any row gap inside either block at 432 px
  - the lower block is visibly about a third of the upper at 432 px
  - every unit is the same height in the render, within 1 px
  - BOTH BLOCKS ARE DRAWN IN THE SAME MEDIUM. Every one of the 267 units goes through the print in one ink and takes the same screen, and the accent is a hue remapped into the printed pixels inside a mask of the lower block's own units, so the two cohorts differ in colour and in nothing else
  - no unit in either block is occluded by a label plate
  - the accent covers the lower block only and measures under 8 percent of the frame
risks:
  - "267 units grey out at feed size. The plan is that the block SHAPES carry it at 432 px and the units carry it at 1080. If the lower block is not resolvable as a separate population at thumb scale, the columns drop and both blocks get taller"
```

```yaml
slide: 6
layout: OBJECT_AND_CAPTION
primary_image:
  subject: a reading workstation drawn large on the floor plane, a 1.6 m desk, an office chair, two 0.40 by 0.62 m portrait diagnostic displays on a 0.55 m arm, and a seated radiologist at 1.70 m with seat height 0.45 m, the displays the only light in the frame and each one carrying a study rather than a blank field
  rect: [0, 440, 1080, 890]
  bleeds: [left, right]
accent: "#4E5FA8"
job: >
  Put a person doing the work in the deck, and carry the second paper's own conclusion in the room
  where that conclusion would actually be applied.
claims: [c16, c22, c24, c25]
numerals:
  - value_from: c22
composition:
  structure: >
    Camera at 1.15 m, a seated eye, horizon at the floor to wall junction at 780. The desk runs
    off both side edges. The two displays stand at Z 2.1 m, the radiologist seated at Z 2.6 m
    with their back three quarters to the camera. The room has no key light at all. Every lit
    surface in the frame is emissive and carries content.
  bands: >
    TOP third, the dark ceiling and back wall carrying kicker, hook and dek. MIDDLE third, the
    two displays, the arm and the radiologist's head and shoulders. BOTTOM third, the desk top with the displays' light falling across it, the chair base and its
    contact shadow, and the floor's halftone texture holding that shadow down to the furniture
    band.
  focal: >
    The right hand display, an AREA of about 250 by 380 px, the lightest plate in the frame, with
    the accent on the study it carries.
art:
  technique: "TXOBJ desk and office_chair with a seated TXFIG and two bespoke displays drawn in metres, printed as a halftone at cell 6 and 22 degrees, with three parallax planes behind the desk at their own values."
  why_this_technique: >
    A reading room is dark by protocol so the display can be read, so the only honest lighting for
    this room is emissive, and a halftone at cell 6 is what gives a dark interior depth without a
    second lamp. The three planes are what give the room depth without inventing a window.
  palette: >
    suite #1B1E21 paper, limestone #EDE6D6 ink, accent bluebonnet #4E5FA8 on one display's study
    only. Greys, display #DCE2E4 in a #2A3038 bezel, desk #474C52 with its lit top graded #2B3036
    to #5A626A and its edge #3A4046 over shade #20252A, chair #454B51, the display arm #41474D,
    the radiologist #B6BDC3, ceiling and far wall #0B0D0F, floor #232830. THERE IS NO SEPARATE
    WALL BAND. A mid grey plate behind the desk put a step in the twin that the edge pass fired
    on, and the contour it drew ran edge to edge through the seated radiologist's shoulders.
  value_structure: >
    The ceiling and the far wall are darkest and carry the type. The two displays are the only
    light and are the lightest plates. Frame median L* planned at 18, the deck's floor.
  motion: >
    Hook, down to the lit displays, left along the desk, out at the chair.
type:
  hook: "It did worse on the patients it had never seen."
  dek: "It scored 0.615 on the brain metastasis cohort it was built on and 0.574 on the cohort it had not met. The paper's own intervals are 0.543 to 0.687 and 0.491 to 0.658, and its authors ask for cautious use."
  labels: ["WHAT THE SECOND PAPER CONCLUDED", "THE AUTHORS' OWN WORDS", "06 / 09", "c16 c22 c24 c25   TEXAS AI DOCKET", "texasaidocket.com", "\"limited standalone discrimination\""]
verbatim:
  - c24: "limited standalone discrimination"
acceptance:
  - the frame carries "Limited standalone discrimination." and no label on it reads "successful discrimination"
  - each display carries at least 12 drawn slice cells, so neither lit rectangle is empty
  - both displays carry visible content and neither is a plain lit rectangle
  - the seated figure reads as a person at a desk at 432 px, with head and shoulders separable from the chair
  - no key light exists in the frame and no object casts a shadow away from a display
  - the two numerals on this frame are 0.615 and 0.574 and both are present in c22
  - the accent sits on one display's study and measures under 8 percent of the frame
  - the accent is the study's own slice marks and covers none of the cells the item above counts
  - the displays stand ON the desk and the seated figure is at the desk, so nothing in the room floats
risks:
  - "a dark room lit by two glowing rectangles is the exact failure the illustration system was written to end. The content on each display is what stops it, and it has to be measured on the render rather than asserted here"
```

```yaml
slide: 7
layout: SPLIT_HORIZON
primary_image:
  subject: one straight horizontal cut at y 356, and below it a field of about fifty children at true scale from 0.85 to 1.45 m standing and walking on open ground under a high September sun, each with its own short contact shadow, two of them near enough to be cropped by the bottom edge, the field running off the left, right and bottom edges
  rect: [0, 356, 1080, 994]
  bleeds: [left, right, bottom]
accent: none
job: >
  Turn the deck. Everything before this frame is a set somebody counted. This is the set nobody
  did, and the frame carries no accent for exactly that reason.
claims: [c4, c6]
numerals: []
composition:
  structure: >
    One straight cut with no gradient, no glow and no transition. Above it, flat unworked ground
    carrying the kicker alone. Below it, the hook in dark ink and the field, camera at 1.65 m with the horizon at 0.20 of the
    lower half so the ground fills it. The field runs off three edges so there is no boundary
    anywhere in it and no total a reader could take.
  bands: >
    TOP band, the flat cut ground carrying the kicker and the counter alone. Below the cut at
    y 356 the hook is set in the deck's DARKEST ink on its LIGHTEST field, which is the only
    place in nine frames the type changes sides, and it is here because this is the frame where
    the deck changes its mind. MIDDLE, the horizon and the far children. BOTTOM, the near
    children cropped by the bottom edge, each with its own contact shadow, and the dek on a
    knockout plate over them.
  focal: >
    The near right group of three children, an AREA of about 300 by 260 px, the largest
    silhouettes in the frame.
art:
  technique: "TXFIG.crowd with children true on the scene bench under one declared sun, printed as a halftone at cell 9 and 30 degrees, each figure carrying a short contact shadow solved from that sun."
  why_this_technique: >
    The coarsest screen in the deck, so at feed size the field reads as a printed newspaper
    photograph of a lot of small people rather than as a pattern. One short contact shadow per
    figure is what seats fifty pictograms on one ground instead of floating them.
  palette: >
    suite #1B1E21 paper, limestone #EDE6D6 ink. Above the cut, #0E1013, the deck's darkest
    ground. Below it, sky band #B4AFA2 falling to ground #9A958A, figures #2A2E2C against it with
    their own paper #141614. No accent anywhere on this frame.
  value_structure: >
    The frame inverts. Above the cut is the darkest zone in the deck and below it is the lightest
    field, so this is the deck's value inversion. Frame median L* planned at 72.
  motion: >
    Hook, straight down through the cut into the field, then out along the bottom edge.
type:
  hook: "Neither record puts a figure on this."
  dek: "The review's record names insufficient external validation and carries no measurement of how far outside the training data a child sits."
  labels: ["THE SET NOBODY COUNTED", "WHAT THE RECORD DOES NOT HOLD", "07 / 09", "c4 c6   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim:
  - c6: "insufficient external validation"
acceptance:
  - the frame carries "insufficient external validation" and no label on it reads "no evidence"
  - the row of pixels at y 355 and the row at y 357 differ by more than 40 L*, so the cut is hard
  - the cut at y 356 is straight and hard, with no gradient or glow across it
  - the hook is dark ink on the lit field below the cut, not limestone on the dark ground above it
  - every figure below the cut carries a contact shadow and none floats
  - the field runs off the left, right and bottom edges with no boundary visible
  - there is no accent pixel anywhere on this frame
  - the children are tellable from adults by proportion at 432 px, and no adult figure appears
  - no two figures stand close enough to read as one taller figure leading a smaller one by the hand
  - at least one figure is cropped by the bottom edge, so the declared bottom bleed is drawn and not only planned
risks:
  - "a field of pictograms reads as a pattern rather than as people. The size variation from 0.85 to 1.55 m and the individual shadows are what stop it"
  - "the absence claim needs the document named AND the document actually opened. Only the PubMed records were fetched, not the full papers, so the hook says record rather than paper and the absences entry says so in as many words. An absence scoped to a document nobody read is the failure absence_check cannot see, because absence_check only asks whether a frame names where it looked"
```

```yaml
slide: 8
layout: MAP
primary_image:
  subject: Texas from assets/geo in Albers, all 254 counties as a hairline mesh filling a neatline cut to the state's own aspect, over a whole degree graticule at a lighter weight than the mesh, with a computed scale bar in the sheet's left margin, two points lit for the two Texas radiology departments on the panel with their names in a key band UNDER the sheet on stems from their own points, and three parallel vertical leaders running off the top edge carrying the three out of state department names
  rect: [60, 330, 960, 920]
  bleeds: []
accent: none
job: >
  Show the boundary and what is outside it as one drawing, and name the two departments a Texan
  is already inside.
claims: [c11, c12, c13, c14, c15]
numerals:
  - computed_by: "out/2026-09-13/compute.py, the five department claims c11 to c15 partitioned by whether each claim's own quoted byline names a Texas city, which is what the hook's two and the dek's three are"
  - computed_by: "the frame's own scale bar. 100 miles is converted to pixels through the fitted Albers projection from the gazetteer distance between Houston and Dallas, so the bar's LENGTH is computed and the round number on it is the bar's unit"
composition:
  structure: >
    No camera. A drafting sheet in true Albers plan, the same projection the website's map builder
    uses. The mesh sits inside a neatline with a bisection placed graticule. Two lit points carry
    labels on short leaders placed outside the mesh. Three leaders leave the top edge PARALLEL and
    vertical, so they read as a diagrammatic device rather than as compass bearings.
  bands: >
    TOP third, the sheet's head, the kicker, the hook, and the three leaders leaving the edge.
    MIDDLE third, the mesh with the panhandle and north Texas, the two lit points and their labels.
    BOTTOM third, the Gulf coast, the scale bar, the neatline's lower rule.
  focal: >
    The two lit points and the gap between them, an AREA of about 420 by 200 px. They are target
    symbols, a dark ring around a pale disc around a dark centre, which is what makes a point read
    against a county mesh at 432 px when it carries no colour.
art:
  technique: "TXGeo Albers county mesh as hairline ground with a neatline, a whole degree graticule found by bisection and a computed scale bar, over a hatch screen at cell 8 and 12 degrees."
  why_this_technique: >
    A cartographic claim wants cartography, and this is one, because the deck is asserting where
    the panel's members sit. The mesh comes from the committed geodata rather than from a drawing,
    so the state's shape is real. NO COUNTY IS LIT AND NO COUNTY IS NAMED, because the committed
    gazetteer holds counties and metros and no cities, and a city to county join here would be a
    claim nothing computed.
  palette: >
    suite #1B1E21 paper, limestone #EDE6D6 ink for the furniture, mesh #BAC2C8 over a state fill
    #4A525A, outline #F0F4F5, graticule #333A40 under the mesh, points #FAFCFC ringed in #0B0E11,
    sheet ground #20262B on a #191D20 table. NO ACCENT: the bluebonnet marks the second paper and
    this frame is the first paper's.
  value_structure: >
    The sheet is dark and even and the state is a mass three steps lighter than it, so the mesh
    reads as counties ON something. The mesh is a hairline at one weight and the graticule is
    lighter than the mesh, because at the same weight the graticule is the loudest thing on the
    sheet. The two points are the only closed pale discs. Frame median L* planned at 26.
  motion: >
    Hook, down the three leaving leaders, into the mesh, across to the two points.
type:
  hook: "Two of the panel's departments are Texan."
  dek: "The two here are at Baylor College of Medicine with Texas Children's Hospital in Houston, and at UT Southwestern Medical Center in Dallas. The three leaving the sheet are the children's hospitals of Boston, Cincinnati and Philadelphia."
  labels: ["WHERE THE PANEL SITS", "ALBERS EQUAL AREA CONIC", "08 / 09", "c11 c12 c13 c14 c15   TEXAS AI DOCKET", "texasaidocket.com", "BAYLOR COLLEGE OF MEDICINE", "AND TEXAS CHILDREN'S HOSPITAL", "UT SOUTHWESTERN", "MEDICAL CENTER", "BOSTON", "CINCINNATI", "PHILADELPHIA", "100 MILES"]
verbatim:
  - c11: "Baylor College of Medicine and Texas Children's Hospital"
  - c12: "UT Southwestern Medical Center"
acceptance:
  - the frame carries "UT SOUTHWESTERN" and no label on it reads "Harris County"
  - the Panhandle's north edge is above the Gulf coast in the render, so the projection is not flipped
  - the mesh is drawn from assets/geo through TXGeo and is neither mirrored nor upside down
  - no county is lit and no county name appears anywhere on the frame
  - the three leaders leaving the top edge are parallel and vertical
  - each of the five departments is on the frame, the two Texas ones named in full and the three others by the city their claim names
  - there is no accent pixel anywhere on this frame, because the accent marks the second paper
  - the two points are findable at 432 px without colour, as pale discs inside dark rings
  - each Texas department's name sits UNDER the sheet at the foot of a stem drawn from its own point, and no label plate lands on the county mesh
risks:
  - "three leaders leaving the top edge read as bearings to a reader who knows where those cities are. Parallel and vertical is the mitigation"
  - "a map is the deck's least urgent content one frame from the close. It earns the slot only as the last set diagram in a deck of set diagrams"
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: a children's hospital at true scale seen from the drop off at dusk, the 60 by 30 m block at Z 72 with its windows and its canopy soffit lit, a drop off canopy at 4.6 m, two live oaks, and a parent at 1.68 m walking in holding the hand of a child at 1.14 m
  rect: [0, 330, 1080, 625]
  bleeds: [left, right]
accent: none
job: >
  Land the deck somewhere a Texan could stand, and give them the one question to ask when they
  get there.
claims: [c7, c10, c27]
numerals: []
composition:
  structure: >
    Camera at 1.60 m, horizon at 815, focal 720. The hospital block sits at Z 72 m and runs off
    both side edges, its upper storeys below y 640 so the sky above them is a clean dark reserve.
    The canopy crosses at Z 24 m and its soffit is lit. Two live oaks at Z 34 m and Z 44 m break
    the facade so the building is not a slab. The pair walk at Z 6.5 m and are cropped by the
    bottom edge, so the reader is behind them and walking in with them.
  bands: >
    TOP third, the dusk sky graded from its darkest at the frame's top to a band of residual
    light at the horizon, carrying kicker, hook and dek. MIDDLE third, the lit block, the canopy
    with its lit soffit, and the two oaks in silhouette against the building. BOTTOM third, the
    drop off apron with the canopy's pool of light lying across it, the pair and their own contact
    shadows on it, and the stipple texture on the apron carrying depth down into the solid paper
    band the dek sits in.
  focal: >
    The lit entrance under the canopy, an AREA of about 300 by 170 px, the brightest plate in the
    frame, with the pair's joined hands reading against it.
art:
  technique: "TXSCENE at standing eye with TXOBJ hospital and live_oak at true scale on one horizon, printed as a stipple at cell 5, returning to frame 1's surface so the deck closes in the register it opened in."
  why_this_technique: >
    The stipple returns the reader to the plate frame 1 set, which is what makes nine frames read
    as one deck. Dusk rather than daylight because the deck is printed on night paper and because
    a lit entrance is the only thing in this frame a reader is meant to walk toward.
  palette: >
    suite #1B1E21 paper, limestone #EDE6D6 ink. Greys, dusk_high #0C0E11 at the top of the sky
    through #161B20 to dusk_low #232A31 at the horizon, facade #6E747A for the block's mass with
    window #EDF1F2 for its lit openings, soffit #E8ECEE under the canopy and glazing #F2F5F6 at
    the entrance, apron #8E8A7E in the pool of light falling to #6A665D and #3E4144 away from it,
    oak_shade #232A24, figures #0F1110.
  value_structure: >
    The top of the sky is the darkest zone and carries the type. The lit entrance and the window
    openings are the lightest plates and they are the only lit things in the frame. The apron is a
    mid field under the canopy and falls away from it. The figures are the darkest marks in the
    lower half. Frame median L* planned at 28.
  motion: >
    Hook, down the facade, along the canopy, out at the pair in the bottom left.
type:
  hook: "Ask what it was validated on."
  dek: "A parent can ask at the desk what population each imaging tool was validated on. The Food and Drug Administration's device list carries the word pediatric in two device names and nowhere in its own text. The panel wants pediatric infrastructure, not adult tools reused."
  labels: ["WHAT A TEXAN CAN DO", "WHERE THE ANSWER IS PUBLISHED", "09 / 09", "c7 c10 c27   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim: []
acceptance:
  - the frame names the Food and Drug Administration's device list and no label on it reads "unvalidated tool"
  - the lit entrance is the brightest region in the frame, at least 25 L* above the facade beside it
  - the pair read as an adult and a child by proportion at 432 px and their hands are joined
  - neither figure is cut by the left edge
  - the hospital block runs off both side edges and is broken by the two oaks, so it is not a slab
  - every lit surface in the frame carries content, the windows and the soffit, and none is a plain plate
  - the dek's glyph band sits entirely on sky and never crosses the building
  - both figures and both oaks carry contact shadows on the apron
  - the closing line names a concrete action a reader could take at a hospital desk
  - the stipple cell matches frame 1's, so the deck closes in the register it opened in
risks:
  - "frame 9 has been the thinnest frame for six consecutive decks by the ledger's own count. It is built first, before 8 and 7, and it gets a rebuild budgeted whether or not it needs one"
```
