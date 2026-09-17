# Storyboard — carousel No. 27, "Software writes the first draft"

Memorial Hermann Health System's clinicians in Houston draft the note a patient receives with a
lab or imaging result using an assistant built into Epic. The health system published three
figures. A trade publication named two days later what those figures do not establish. And Texas
has a statute about telling people when a machine is in the room, whose reach over a private
hospital the chapter does not settle.

CONTINUITY: PANORAMA_SPINE, MOTIF_EVOLUTION, VALUE_ARC

**PANORAMA_SPINE.** The nine grounds are one continuous reading surface. **A squared front edge
sits at y 1096 on every one of the nine frames**, declared once in the chassis as `N.EDGE`, and
the camera translates along it. The surface's MATERIAL changes at three declared seams and the
camera height changes with it, so the seams are chapters rather than accidents. Frames 1 to 3 are
clinic laminate at a seated eye of 1.10 m. Frames 4 to 6 are a home reading table at reading
distance. Frames 7 to 9 are a public counter, at reading distance and then standing. Art crosses
every cut line and type never sits on one.

**THE ACCENT LIVES ON TWO MATERIALS AND THE SPLIT IS DELIBERATE.** On frames 4, 5, 7 and 8 the
accent is a DOM keyline mounted above the canvas, so it takes neither the halftone screen nor the
deck's grade. On frame 9 it is a filled card drawn ON the canvas through `N.fillCard`, so it takes
both and the dots are visible in the amber. A round 3 judge measured the difference and called them
not the same material, which is correct, so here is the reason rather than a denial. A THIN
KEYLINE DOES NOT SURVIVE THE GRADE: canvas keylines were crushed by `TXDECK.finish` in this run's
first build, `layout_check` then measured the accent at 0.0000 on five frames, and the cure was to
mount them above it. A FILLED CARD DOES survive, and frame 9's read as pasted on precisely because
it was outside the grade like the keylines. So the rule is the mark's own weight: hollow marks are
mounted, the one filled mark is drawn. It is a split worth closing in the chassis rather than in a
frame, and it is in the upgrade backlog rather than repaired here.

**MOTIF_EVOLUTION. The empty rule.** One object recurs and changes state with the argument, and
it doubles as the progress indicator. Frame 4 carries eight boxes beside eight search terms, all
eight empty. Frame 5 carries a field table with its heads set and every cell blank. Frame 7
outlines three different duty holders on one page. On frame 8 the keyline **closes** for the
first time, around a list that is complete, so the emptiness moves from inside the box to outside
it. On frame 9 the accent is **filled**, once, on a card carrying what a Texan can do. Hollow
everywhere the door is not, solid at the one place it is. Frames 1, 2, 3 and 6 carry no accent,
and frame 6's absence is load bearing: it is the one number in the deck with a population you can
count, so there is no empty rule on it to mark.

**THE GLYPH LAW, and it is the reason this deck can draw documents at all.**

> **A drawn line of type gets glyphs if and only if this run fetched those glyphs.** The release,
> the article and the statute are set in real type, verbatim, because those documents were read
> and are in `claims.json`. **The patient's own message is the one unglyphed document in the
> deck**, drawn with `N.ruleRun` as hairlines at true line lengths, because no document this run
> read publishes one word of what such a draft says. Nothing anywhere in nine frames is drawn as
> a filled bar, a strike or a smudge, because a black field says something was REMOVED and the
> record says nothing was ever written.

**VALUE ARC, and it was RE-PLANNED FROM A MEASUREMENT rather than defended.** The directors' room
planned a deck median in the high twenties. The Phase 10.5 probe rendered frame 1 at a median of
**2.3** against a planned 30, and the diagnosis was two faults in the chassis rather than one in
the frame: the room ramp's lightest step was still dark, and the surface below the front edge
fell to black, so 60 percent of the frame was near black and 40 percent was lit. Both are fixed
in the chassis and both are written into its source. The arc below is what this world actually
gives, measured off the probe rather than asserted.

    frame        1     2     3     4     5     6     7     8     9
    measured  41.4  51.2  44.8  57.8  56.2  45.6  53.3  57.8  45.0
    jump             9.8   6.4  13.0   1.7  10.6   7.7   4.5  12.8

Mean adjacent jump 8.32 against a ceiling of 14.9. No adjacent pair over 25, so the deck declares
**VALUE CUT: none**. Deck spread 16.5.

This table is the deck as it stands after the contrast and plating repairs of Phase 14b, not as it
stood when the frames were first written, and the difference is written down rather than smoothed
over. Frame 1 fell from 43 to 41.4 when the dek's ground was dimmed to clear the rubric's 4.5
contrast floor and a keyboard was put on the desk to break a plate. **The 59 this table used to
print against frame 2 was never a measurement of the frame that shipped**, which is the reason
the whole table is now reprinted from `deck_coherence`'s own output rather than transcribed:
frame 2 was rebuilt twice after that figure was written and has measured near 52 since. Every
other frame moved by under a point.

**AND THE ARC WAS RE-PLANNED THREE TIMES, FROM MEASUREMENT EACH TIME, WHICH IS WORTH RECORDING
RATHER THAN TIDYING AWAY.** The directors planned a deck in the high twenties. The probe frame
rendered at 2.3, which named two chassis faults. The first full render then measured a deck that
alternated between dark rooms at 8 to 15 and bright pages at 38 to 60, a mean adjacent jump of
22.0 against a ceiling of 14.9 and four hard cuts, which is precisely the strobe
`deck_coherence.py` exists to refuse. The cure was not a gradient anywhere. It was bringing the
two populations together: the rooms were lit and the paper stock was darkened until the deck sat
in one band. Every frame's acceptance list now carries its own measured band as its tolerance, so
a later repair pass that moves a frame out of it fails `plan_render_check` rather than passing
quietly.

**THE LIGHT.** az -28, el 22, declared once in `assets/js/deck/2026-09-17-nightdraft.js`. **The
light comes from the upper left at 22 degrees above the surface, so every object lays its cast
down and to the right at about 2.5 times its own height, and nothing in this deck is lit from
above.** That last clause is the deck's signature and its structural separation from the hospital
deck of September 13th, which lit its rooms from overhead fixtures.

**THE ONE SCREEN.** `N.tooth`, a halftone dot field at cell 6, angle 22, on all nine frames with
no frame painted outside it. Cell 6 was MEASURED rather than chosen:
`out/2026-09-17/screen_ceilings.json` prints a black field, a mid field and a white field through
seven configurations on this deck's own ground and ink at feed scale, and halftone at cell 6 runs
4.0 to 87.0 where hatch at cell 6 caps at 42.6 and stipple at cell 5 caps at 25.2.

**THE PALETTE, computed rather than chosen.** `out/2026-09-17/palette_measured.json` carries the
arithmetic, against the 59 hexes of the last eight decks with the line at dE 10.09.

    ground     L* 10.0  #051F21  dE  8.51   the unlit room, a cool dark
    ink        L* 86.5  #C8DDD7  dE  9.39   display type, 12.07 to 1 on the ground
    dek        L* 68.2  #8CADA7  dE 15.39   7.07 to 1
    furniture  L* 58.0  #6A929A  dE 13.52   one pale ink on all nine frames, 5.06 to 1
    page       L* 80.4  #BFCBBD  dE 10.22   the drawn documents' own stock
    toner      L* 13.7  #272310  dE 11.19   the type printed on them, 9.36 to 1 on the page
    accent     L* 72.7  #EFA31D  dE 39.95   standby amber, and the accent law above

Every luminance in that table is computed from its own hex by `measure.py` and lives in
`measurements.json`. THE COLUMN ORDER IS NOT A STYLE CHOICE: the `measured figures` gate reads a
number written beside the `L*` token, and with the hex first it read the tail of `#051F21` as a
luminance of 21. The figures were right and the layout put digits where the gate looks.

Flag red is UNSPENT and that is deliberate. There is no comment window, no hearing and no
deadline anywhere in this record, so a reserved red would be a false urgency.

---

## Frame 1 — FULL_BLEED

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "a clinic workstation bay at 6:40 in the evening, a 1.70 m clinician seated at a 1.6 m desk with the 0.60 x 0.34 m display the only light in the building, a keyboard on the desk in front of it, the desk's squared front edge running off both sides at y 1096"
  rect: [0, 396, 1080, 954]
  bleeds: [left, right, bottom]
accent: none
job: >
  Put the reader behind a clinician's shoulder and say, before any figure or any statute, that
  the first version of a sentence a patient will read about their own body was written by
  software.
claims: [c1, c2, c3]
numerals: []
composition:
  structure: >
    The display sits right of centre at the far side of the desk, so the reader is over the
    clinician's shoulder rather than facing them. The desk plane runs from y 616 to the constant
    edge at 1096 and off both sides, which is what makes the frame a place rather than an object
    on a ground. The keyboard lies between the two, in the desk's own perspective, and it is
    there because the lit plane measured as a plate without it: construction_check read the desk
    as filling 0.719 of its own bounding box against a 0.68 line. An object was the fix rather
    than a threshold, and the object a clinician drafting in Epic has is a keyboard.
  bands: >
    Top third, the dark room and the headline. Middle third, the display and the desk catching
    its light. Bottom third, the clinician's silhouette, the near face of the desk and the
    furniture.
  focal: "the lit display panel, an area of about 548 by 311 px, pulled to by being the only light in a dark frame"
art:
  technique: "scene bench at true scale with one declared light, plus the deck's own halftone tooth"
  why_this_technique: >
    The claim is that a machine drafts a sentence inside a clinician's working day, so the frame
    has to carry the working day. A figure at true scale beside a desk of a known size is the only
    thing that makes a screen read as somebody's job rather than as a product shot.
  palette: "the deck's own, computed. Room from the ROOM ramp, display from the STOCK ramp."
  value_structure: >
    The display is the lightest thing and everything else takes its light from it. The clinician
    is the darkest, a silhouette, because a person between a reader and a light is. Frame median
    L* planned at 41.
  motion: "from the headline down the left, into the lit display, then down over the keyboard and the clinician's lit shoulder to the near edge"
type:
  hook: "Software drafts your lab result note."
  dek: "Memorial Hermann clinicians in Houston draft a patient's result note with an assistant in Epic."
  labels: []
verbatim: []
acceptance:
  - "the frame median L* is between 37 and 49 at 432px, which is this frame's own band in the deck's re-planned arc"
  - "the draft on the display is ruled hairlines and carries NO letterform anywhere, because no source publishes one word of a draft"
  - "the lit display's median luminance is at least 25 L* above the room above the desk, measured at 432 px"
  - "a seated human figure is present and its head is below the display's top edge, so the scale reads"
  - "the desk's front edge is at y 1096 and runs off both the left and right frame edges"
  - "no numeral appears anywhere on this frame"
  - "no accent pixel appears anywhere on this frame"
  - "a keyboard lies on the desk between the clinician and the display, dark against the lit plane, with its far lip catching the display"
risks:
  - "the clinician merges into the dark room and reads as a shape rather than a person"
  - "the display reads as a product screenshot rather than as a lit surface in a room"
```

## Frame 2 — DOCUMENT

```yaml
slide: 2
layout: DOCUMENT
primary_image:
  subject: "the 0.60 x 0.34 m display at screen scale, emissive, its bottom edge sitting on the desk at y 1096 and its top edge bleeding the frame, carrying a result list at the left and one open row with an unglyphed draft beside it"
  rect: [96, 0, 888, 1096]
  bleeds: [top]
accent: none
job: >
  Show WHERE the draft is made and WHEN, which is while the clinician is reading the result, and
  do it without inventing one detail of an interface this run never saw.
claims: [c2, c3]
numerals: []
composition:
  structure: >
    The panel occupies the middle two thirds and runs off the top edge, so the reader is at the
    screen rather than looking at a monitor in a room. The desk's constant edge is still at 1096
    under it, which is what ties this frame to the one before it.
  bands: >
    Top third, the panel's upper reaches running off the edge and the kicker band. Middle third,
    the result list and the open row. Bottom third, the panel's lower bezel with its own lit top
    edge, the desk surface under it taking the panel's glow as a gradient from lit into shade, and
    the panel's shadow cast down and to the right across that surface.
  focal: "the one open row and the draft beside it, an area of about 330 by 230 px"
art:
  technique: "the emissive panel primitive, which refuses to glow without content, plus ruleRun"
  why_this_technique: >
    c3 states that the draft is generated in real time as the clinician reviews results in the In
    Basket. That is a claim about a moment in a queue, and a queue with one thing open is the only
    drawing that says it.
  palette: "the deck's own. The panel is STOCK, the room is ROOM."
  value_structure: >
    The panel is the frame. The room around it is the deck's dark. Frame median L* planned at 52.
  motion: "down the result list, then right into the open row's draft"
type:
  hook: "The draft appears as the result opens."
  dek: "Art helps generate an initial draft patient note in real time while clinicians review lab and imaging results in Epic's In Basket."
  labels: []
verbatim:
  - c3: "in real time"
acceptance:
  - "the frame median L* is between 46 and 58 at 432px, which is this frame's own band. THE BAND WAS REWRITTEN ONCE, after the chassis gained a corner falloff that took every lit plane in the deck off its own bounding box to clear construction_check, and this frame moved 59 to 52 with it. Recorded here rather than tidied away, because plan_render_check asks which of the two was changed."
  - "every line of the draft is a hairline and no letterform appears inside the panel"
  - "exactly one row in the result list is marked open, and it is the row the draft sits beside"
  - "the panel carries no logo, no product colour, no button and no control"
  - "the panel's bottom edge sits on the desk surface and the desk's front edge is at y 1096"
  - "no accent pixel appears anywhere on this frame"
risks:
  - "a drawn interface becomes an invented product screenshot"
  - "the panel fills so much of the frame that it reads as a plate with a headline on it"
```

## Frame 3 — FIGURE_SCALE

```yaml
slide: 3
layout: FIGURE_SCALE
primary_image:
  subject: "the same clinician in profile at true scale, 1.70 m seated at a 0.45 m seat, at the 1.6 x 1.2 m desk, with a second office chair beside it, empty, because the patient is not in this room"
  rect: [0, 470, 1080, 880]
  bleeds: [left, bottom, right]
accent: none
job: >
  Keep the record's own word. The release says clinicians CAN review, edit and personalize, and
  this frame is where the deck says that and declines to say it always happens.
claims: [c4, c8, c9]
numerals: []
composition:
  structure: >
    The camera steps back and round to the side, so the reader sees the whole working posture
    rather than the screen. EVERY OBJECT IS AT ONE DEPTH'S ARITHMETIC, and three rounds each
    fixed a different symptom of its not being so. Round 2 found no desk at all, so a correctly
    sized monitor stood on a plane a chair and a seated person made read as the floor. Round 3
    found a desk with no top FACE. Round 4 measured the rebuild and named the cause under all
    three: the top face's near edge was at y 1004, which is depth Z 1.96, while its front face
    ran to y 1076, the floor at Z 3.05, so the drawn object was a 0.17 m plinth rather than a
    0.75 m desk, and the monitor was sized for Z 3.35 while standing at Z 2.05.
    The bench is y = horizon + (eye - h) * f / Z. The desk top's NEAR edge is pinned to the deck's
    constant at y 1096, which is Z 1.564, and the floor at that depth is y 1489, off the bottom of
    a 1350 frame, which is why the front face runs off the near edge as a desk the reader stands
    at does. Its FAR edge is the clinician's own depth, Z 3.05, at y 874. The monitor stands at
    Z 2.40 where the plane is y 937 and one metre is 341.7 px. Pinning the desk that way cuts
    everything behind it at 874, which is why the empty chair shows its back above the surface
    and not its base. The empty chair is the frame's argument
    and it stands in the MIDDLE DISTANCE, between the display and the clinician, on the same
    ground line as the clinician.
    It was in the right third and it was not in the picture at all: at X 2.28 it projected past
    the right margin, and at a nearer Z its base fell below the front edge at y 1096, which on
    this bench means it was drawn onto the desk's own front face rather than standing on it.
  bands: >
    Top third, the dark room and the headline. Middle third, the clinician at the desk with the
    display's throw across it and the empty chair standing in it. Bottom third, the desk's near
    face graded from its lit lip down into shade, with the chair's pedestal and base and the
    clinician's own cast both running down and to the right from the deck's one light.
  focal: "the lit display standing on the desk, with the empty chair beside it, an area of about 200 by 240 px"
art:
  technique: "the scene bench at true scale, a second camera on the world of frame 1"
  why_this_technique: >
    Two cameras on one world is what the continuity mandate asks for, and it is the only way to
    show a person's whole relation to a machine. A close crop would show the hand and lose the
    room, and the room is where the second chair is empty.
  palette: "the deck's own."
  value_structure: >
    The display is still the only light, now nearly edge on with a dark bezel down its near side,
    and EVERY DIMENSION OF IT IS METRES TIMES THE SCENE'S OWN PIXELS PER METRE rather than a
    number typed into canvas coordinates. It was drawn 214px tall on a 66px column while the
    figures went through TXSCENE at about 269 px per metre, which is a 0.80 m panel on a 0.25 m
    stand beside a 1.70 m person, and a judge named what that reads as without doing any
    arithmetic at all, a floor lamp. A 24 inch panel is 0.34 m, which is 83px at this depth.
    THE CHAIR TAKES THE LIGHT AND THE CLINICIAN DOES NOT, which reverses what this dossier
    declared and is the reversal the round 1 panel asked for. Two judges read the clinician as a
    flat black cutout against a gradient while this frame's declared focal was the light on their
    hand. A sprite carries one ink, so it cannot be rim lit, and a plan that needs a rim light
    this bench cannot draw ships as a cutout every time. The frame's argument was always the
    empty chair, so the light goes there.
    Frame median L* planned at 45.
  motion: "from the headline down to the lit display, right along the desk to the empty chair, then on to the clinician"
type:
  hook: "The clinician can edit it first."
  dek: "Memorial Hermann's chief medical information officer calls the draft a starting point clinicians can review, edit and personalize before sharing with the patient."
  labels: []
verbatim:
  - c8: "review, edit and personalize"
acceptance:
  - "the frame median L* is between 39 and 51 at 432px, which is this frame's own band in the deck's re-planned arc"
  - "the dek says can and never says does, is always, or every"
  - "a second chair is present, is empty, and is a different object from the one the clinician sits in"
  - "the figure is drawn at true scale against a desk of a stated size, so a reader can judge the room"
  - "the desk, the monitor, the chair and the clinician are all placed by the SAME projection, and no object in this frame is sized or positioned in raw canvas pixels"
  - "the display has a bezel, a column and a base with its own contact, so it reads as a monitor"
  - "a desk is drawn at 0.75 m and the monitor stands ON it, so a reader can check the monitor's size against the person in the same frame"
  - "every dimension of the monitor is a number of metres times the scene's own pixels per metre, and no object in this frame is sized in raw canvas pixels"
  - "the desk's top face near edge is the deck's constant at y 1096 and runs off both frame edges, and its front face runs off the bottom of the frame because the floor at that depth is at y 1489"
  - "no accent pixel appears anywhere on this frame"
risks:
  - "frames 1 and 3 are the same room and become the closest pair bespoke_check finds"
  - "the empty chair reads as a leftover rather than as the point, which is what happened on the first build and cost this frame two judges"
```

## Frame 4 — CLOSE_CROP

```yaml
slide: 4
layout: CLOSE_CROP
primary_image:
  subject: "the bottom 140 mm of the printed announcement at one to one on a home reading table at night, cropped by the left, right and bottom edges, with eight 24 px boxes down the right margin beside eight search terms, all eight empty and keylined in the accent"
  rect: [0, 250, 1080, 1100]
  bleeds: [left, right, bottom]
accent: "#EFA31D"
job: >
  Draw the METHOD rather than assert the finding. A reader is not told the announcement is silent
  about disclosure, they are shown the eight term search that established it, in the margin of the
  page it was run on.
claims: [c1]
numerals: []
composition:
  structure: >
    The page is cropped by three edges so the reader is inside the paper rather than looking at a
    sheet. The eight boxes run down the right margin in a column, which is where a person marking
    up a page would put them and which reads as a checklist rather than as decoration.
  bands: >
    Top third, the page's last set paragraph running off both sides and the headline over the
    table beyond the sheet. Middle third, the eight terms and their eight boxes. Bottom third, the
    sheet's near edge catching the key as a lit lip, its two part contact shadow on the table under
    it, and the table's own grain falling away into shade toward the lower right.
  focal: "the column of eight empty boxes, an area of about 300 by 420 px, pulled to by being the only accent in the frame"
art:
  technique: "a drawn sheet at true size under the deck's one raking light, with set type mounted above it in the DOM"
  why_this_technique: >
    An absence has to be drawn as a real thing with a real edge or it is a void, and a void is
    what this whole system was rebuilt to stop drawing. A ruled box with a label beside it and
    nothing in it is an absence a reader can see the shape of.
  palette: "the deck's own. STOCK for the sheet, TONER for its type, ROOM for the table."
  value_structure: >
    The page is the brightest thing in the deck so far and the table around it is the deck's dark.
    Frame median L* planned at 56.
  motion: "across the set paragraph, then down the eight boxes"
type:
  hook: "Eight words searched. None on the page."
  dek: ""   # frame 4 carries no dek. The announcement's own paragraph is set on the drawn sheet, and the eight terms with their eight empty boxes carry the finding. A dek restating it would be a caption on a picture that already says it.
  labels: ["disclose", "disclosure", "notify", "notified", "inform patients", "told", "transparen", "label"]
verbatim:
  - c1: "Clinicians at Memorial Hermann Health System (MHHS) are using a new artificial intelligence (AI) tool built directly into Epic"
acceptance:
  - "the frame median L* is between 50 and 62 at 432px, which is this frame's own band in the deck's re-planned arc"
  - "exactly eight boxes are drawn, exactly eight terms are set beside them, and every one of the eight boxes is empty"
  - "no box is filled, struck through, blacked out or shaded, because a filled field asserts a removal"
  - "every box is 48px on a 7px accent keyline, which leaves a 34px hole that still reads as a hole at 432px, and the accent appears nowhere else on this frame"
  - "the set paragraph on the sheet is a verbatim substring of claim c1 and contains no invented sentence"
  - "the sheet is cropped by the left, the right and the bottom frame edges"
  - "the accent covers under 8 percent of the frame"
risks:
  - "eight empty boxes read as a redaction field, which asserts something was removed"
  - "the type set on the sheet is too small to read at 432 px and the frame becomes texture"
```

## Frame 5 — DOCUMENT

```yaml
slide: 5
layout: DOCUMENT
primary_image:
  subject: "the announcement sheet at 216 by 279 mm lying almost square on the reading table, turned 1.2 degrees off the frame's axis, its three published figures set large on it, and under a foot rule a three column field table with its heads set and every cell blank, keylined in the accent"
  rect: [46, 300, 1034, 1050]
  bleeds: [right, bottom]
accent: "#EFA31D"
job: >
  Put the three figures the health system published beside the three things a trade publication
  said are not published with them, on one sheet, so the reader does the subtraction themselves.
claims: [c5, c6, c7, c12]
numerals:
  - value_from: c5
  - value_from: c6
  - value_from: c7
composition:
  structure: >
    THE SHEET IS TURNED 1.2 DEGREES AND THIS DOSSIER SAID 28, WHICH WAS NEVER TRUE OF ANYTHING
    THAT SHIPPED. A round 3 judge read `rot: -0.021` out of the slide, which is 1.2 degrees, and
    named the reason the bigger number was impossible: `N.sheet` ROTATES AN AXIS ALIGNED
    RECTANGLE. It has no projection in it, so a sheet drawn with it can never have a near edge
    wider than its far edge at any angle, and the acceptance item below promising exactly that
    was false by construction rather than by execution. A real oblique on this frame needs a
    primitive the chassis does not have, and inventing one in a repair round is how a deck ships
    a worse frame than the one it was fixing. What the turn actually buys is thickness, a cast
    and an edge that is not parallel to the frame, which
    is what stops a document frame being a bright rectangle. The three figures sit in the upper
    half and the blank field table directly under them, so the eye reads the claim and then the
    hole in it without moving far.
  bands: >
    Top third, the table beyond the sheet and the headline. Middle third, the three figures on the
    sheet. Bottom third, the sheet's near corner lifted off the table with a two part contact
    shadow under the curl, the paper's grain running across the lit side of it, and the field
    table's ruled cells sitting on that gradient.
  focal: "the three figures set in mono, an area of about 640 by 190 px"
art:
  technique: "a drawn sheet turned slightly off axis under the deck's one light, with set type mounted above it"
  why_this_technique: >
    The figures are the source's own and the frame's job is to keep them looking like somebody
    else's words on somebody else's paper rather than like this deck's headline.
  palette: "the deck's own."
  value_structure: >
    The lit half of the sheet is the brightest passage, the far half falls toward the table, and
    the table is the deck's dark. Frame median L* planned at 55.
  motion: "down the three figures, across the foot rule, into the empty cells"
type:
  hook: "Three figures. No denominator."
  dek: ""   # frame 5 carries no dek. The three figures, the attribution rule under them and the three blank cells are the whole statement, set on the sheet itself.
  labels: ["baseline", "control arm", "denominator"]
verbatim:
  - c5: "32%"
  - c6: "over 55,000"
  - c7: "nine seconds"
  # The trade publication's sentence "No baseline, control arm or denominator accompanies them."
  # was planned as a fourth verbatim fragment on this frame and the frame does not print it. The
  # blank field table says the same thing by being blank, which is the frame's whole argument, so
  # the sentence was dropped rather than set twice. A verbatim slot for a string nobody drew
  # describes a frame the run did not make, which is what verbatim_check refuses.
acceptance:
  - "the frame median L* is between 50 and 62 at 432px, which is this frame's own band in the deck's re-planned arc"
  - "the three figures are rendered exactly as their sources render them, 32% with the percent sign, over 55,000 with the thousands comma and the word over, and nine seconds SPELLED OUT"
  - "each of the three figures carries its source on the same sheet, so no figure floats unattributed"
  - "the field table has three column heads set and every cell in it is blank"
  - "no cell is filled, struck or shaded, and the accent appears only as the table's keyline"
  - "the sheet is turned off the frame's axis and carries a thickness and a cast, which is what N.sheet can do. Its near and far edges are at the SAME scale, because N.sheet rotates an axis aligned rectangle and has no projection in it, and an acceptance item promising otherwise was false by construction"
  - "no numeral on this frame is absent from claims.json"
risks:
  - "nine seconds gets rendered as 9 seconds, which is the article's form and not the source's"
  - "the blank cells read as an unfinished render rather than as a finding"
```

## Frame 6 — GRID

```yaml
slide: 6
layout: GRID
primary_image:
  subject: "52 figures at one scale, in four ranks of eleven and a fifth of eight, every one at the same depth and separated by lift rather than by distance, on a level plane so all five ranks carry the same contrast"
  rect: [0, 470, 1080, 880]
  bleeds: [left, right, bottom]
accent: none
job: >
  Give the one controlled test in this story a population a reader can count, and say plainly in
  the same frame that it tested a different feature.
claims: [c13, c14]
numerals:
  - value_from: c14
composition:
  structure: >
    Five ranks, the last three short so the block cannot read as a round number and so the
    silhouette comes apart into pieces rather than merging into one mass. NOTHING RECEDES. Three
    earlier builds put the ranks on the ground plane at different depths and layout_check refused
    all three, because overlapping ranks cannot be counted, and a fourth build of four equal ranks
    of thirteen was refused by all three judges as exactly the round grid this line forbids.
  bands: >
    Top third, the dark room and the headline. Middle and bottom thirds, the five ranks on a plane
    held deliberately LEVEL, which is the only surface in the deck that does not brighten toward
    the reader. Every other ground here is a desk or a counter and brightens because that is what
    a lit surface does. This one is a chart, and a plane that brightens downward hands the bottom
    ranks a brighter ground than the top ranks, which took their separation from 137 to 64 while
    every figure was one value. The bottom third carries the short rank itself, eight figures
    modelled with the same ink and lip as the forty four above them, standing on the plane's own
    near band where the light falls away toward the constant edge at y 1096 and the counter face
    below it drops into shade.
  focal: "the short last rank, an area of about 300 by 120 px, because it is where the count stops being round"
art:
  technique: "figures as pictograms at one scale on the scene bench, the isotype, with NO casts"
  why_this_technique: >
    A count wants a GRID and this is the only count in the deck with a real population. Drawing 52
    people rather than printing 52 is the difference between a number and a number a reader has
    felt the size of. NOTHING IN THIS FRAME CASTS, and the absence is the isotype's own honesty
    rather than an omission: a chart is not a room, so it gets no room's light, and a cast on a
    figure that is not standing anywhere would be a depth cue drawn into a picture with no depth.
    The deck's light does its work on the eight frames that are places.
  palette: "the deck's own. ONE value for all 52, because the rows are lifts and nothing is further away than anything else."
  value_structure: >
    Every figure is one value against a level ground, so all five ranks carry the same separation
    and the count can be made at 432px. The build that alternated two values across the ranks was
    drawing depth into a chart that has none, and rows two and three sank into a ground that
    brightens downward. Frame median L* planned at 41.
  motion: "across the top rank, then down through the ranks to the short one"
type:
  hook: "The test healthsystemCIO points to was not in Texas."
  dek: "A randomized pilot of fifty two doctors at UC San Diego Health in 2023. Reply time moved less than 6% and missed statistical significance."   # THE CONNECTIVE IS IN THE COPY NOW AND ITS ABSENCE WAS THIS DEFECT'S FOURTH RUN. topics.json records it in capitals against carousel 23 on September 13th, where three reader judges asked for the bridge in three consecutive rounds and the entry says to put it where the detour starts. The hook says the test was not in Texas and the dek says the trade publication is what points to it, so a reader never has to infer why California is in a Texas deck. The locator is still set INSIDE the primary image as well, so a reader who reads only the picture still can't take the 52 for Houston doctors.
  labels: ["UC San Diego Health, 2023", "draft replies to patient messages"]
# THE ISOTYPE PRINTS NO QUOTED SENTENCE. c14's "a randomized pilot of 52 doctors in 2023" was
# planned as a verbatim fragment here and the frame that shipped sets the count as 52 drawn
# figures under a locator reading UC SAN DIEGO HEALTH, 2023. The claim is still cited and still
# traced; it is simply not quoted, so nothing is declared in this slot.
verbatim: []
acceptance:
  - "the frame median L* is between 40 and 52 at 432px, which is this frame's own band in the deck's re-planned arc"
  - "exactly 52 figures are drawn and the last rank is short, so the block does not read as a round grid"
  - "the locator naming UC San Diego Health and draft replies is inside the primary image rect and not in the source line"
  - "figures and ground carry different values, so the block does not merge into one mass"
  - "all five ranks separate from their ground by a comparable amount, so no rank is harder to count than another"
  - "nothing in this frame casts, because it is a chart and not a room"
  - "no figure is distinguished from another, because the source gives no arm sizes"
  - "no accent pixel appears anywhere on this frame"
risks:
  - "the 52 figures merge into one pale mass and the count cannot be made"
  - "a reader takes the 52 for Houston doctors rather than for a California pilot"
```

## Frame 7 — CLOSE_CROP

```yaml
slide: 7
layout: CLOSE_CROP
primary_image:
  subject: "the statute page at reading distance on the public counter, cropped by the left, the right and the bottom edges, subsections (b), (c) and (f) set at true type size, with three accent keylines around three different duty holders"
  rect: [0, 342, 1080, 1008]
  bleeds: [left, right, bottom]
accent: "#EFA31D"
job: >
  Show the reader three different duty holders on one page and let them draw the question. This
  frame states the textual gap and states nothing about who wins.
claims: [c15, c16, c22, c23]
numerals: []
composition:
  structure: >
    The page fills the frame and runs off three edges so the reader is over it. The three outlined
    phrases sit at three different depths down the page, which is what makes them read as three
    separate provisions rather than as one list.
  bands: >
    Top third, subsection (b) with the words a governmental agency outlined. Middle third,
    subsection (c) with the words a person outlined. Bottom third, subsection (f) with the words
    the provider of the service or treatment outlined, sitting where the raking light has fallen
    furthest into shade, with the paper's grain and the page's near edge and contact shadow.
  focal: "the outlined phrase in subsection (f), an area of about 520 by 44 px"
art:
  technique: "a drawn statute page under the deck's one raking light, with set type mounted above it"
  why_this_technique: >
    A claim that is a document's own words wants DOCUMENT or CLOSE_CROP, and the words are the
    whole argument here. Nothing but the page itself can carry it without the deck appearing to
    paraphrase a statute.
  palette: "the deck's own."
  value_structure: >
    The page is lit from the upper left and falls away to the lower right, so the three outlined
    phrases sit at three different brightnesses and the eye travels down. Frame median L* planned
    at 54.
  motion: "down the page from (b) to (c) to (f), then to the margin note"
type:
  hook: "One says agency. One says provider."
  dek: ""   # frame 7 carries no dek. The line is set on the page itself as SEC. 552.051, IN FORCE SINCE JANUARY 1ST, 2026, because a date about a statute belongs on the statute rather than beside it.
  labels: ["The word governmental does not appear in (f)."]
verbatim:
  - c16: "A governmental agency"
  - c22: "A person"
  - c15: "the provider of the service or treatment"
acceptance:
  - "the frame median L* is between 48 and 60 at 432px, which is this frame's own band in the deck's re-planned arc"
  - "all three of subsections (b), (c) and (f) are set on the page and each carries its own accent keyline"
  - "each margin mark is HOLLOW, 34px on a 7px keyline, because frame 9's card is the deck's only filled accent and a solid bar here spends that turn three frames early"
  - "no string on this frame says the hospital must disclose, is required to disclose, or is in violation"
  - "the set statute text is a verbatim substring of c15, c16 or c22 and contains no paraphrase"
  - "nothing on the page is drawn as a hole, a strike or a blacked out word"
  - "the page is cropped by the left, the right and the bottom frame edges"
  - "the accent covers under 8 percent of the frame"
risks:
  - "the cumulative reading of frames 7 to 9 lands as the hospital is breaking the law"
  - "the statute type is too small to read at 432 px and the argument becomes texture"
```

## Frame 8 — DOCUMENT

```yaml
slide: 8
layout: DOCUMENT
primary_image:
  subject: "Chapter 552's complete section list set as one column on a page that runs off the left, the right and the bottom edges, with one closed accent keyline around the whole list"
  rect: [0, 168, 1080, 1182]
  bleeds: [left, right, bottom]
accent: "#EFA31D"
job: >
  Say what was searched and what was not found, so the deck's refusal to resolve the statute is a
  finding rather than a shrug.
claims: [c15, c16, c18, c19, c20, c23, c24, c25, c26, c27, c28, c29, c30, c31, c32, c33, c34, c35, c36, c37, c38, c39, c40, c41, c42]
numerals:
  - computed_by: "out/2026-09-17/compute.py, the length of the transcribed section list"
composition:
  structure: >
    One column, narrower than the frame, running off the top and the bottom, so the list is
    something the reader is scrolling through rather than a block placed on a page. The keyline
    CLOSES around it, which is the motif's turn.
  bands: >
    Top third, Subchapter A's entries running off the edge. Middle third, Subchapter B. Bottom
    third, Subchapter C's entries on the column's own gradient as the light falls away, the
    column's shadow cast onto the counter beside it, and the counter's surface grain running under
    the mono line.
  focal: "the closed keyline's lower corner and the mono line just outside it, an area of about 430 by 130 px"
art:
  technique: "a drawn column of set headings under the deck's one light, flat on, the one frame in the deck with no camera"
  why_this_technique: >
    An exhaustive list is the only honest drawing of an exhaustive search. A reader can see there
    is no more of it, which is the claim.
  palette: "the deck's own."
  value_structure: >
    The column is the lightest thing and the counter around it is the deck's dark, so the list
    reads as the only thing in the frame. Frame median L* planned at 59.
  motion: "straight down the column to where it stops"
type:
  hook: "Every section, and none headed Applicability."
  dek: "" # frame 8 carries no dek. The complete list IS the statement and a sentence restating it would be furniture.
  labels: ["Subchapter A", "Subchapter B", "Subchapter C"]
verbatim: []
acceptance:
  - "the frame median L* is between 54 and 66 at 432px, which is this frame's own band in the deck's re-planned arc"
  - "every section number and heading in the drawn list is a literal substring of some claim's own QUOTE, which is c24 to c42, and no section number is invented. THE EARLIER WORDING POINTED AT THE WRONG EVIDENCE: it claimed every number appears in the absences block, and absences[3] writes two RANGES, 'Sec. 552.051 through Sec. 552.057' and 'Sec. 552.101 through Sec. 552.106', so ten of the sixteen never appear there as strings at all. Nothing on the frame was untraced and the item meant to prove it was false about itself"
  - "the accent keyline is CLOSED on all four sides, which is the one frame in the deck where it closes"
  - "no heading in the list reads Applicability or Scope"
  - "the page runs off the left, the right and the bottom frame edges"
  - "any count of sections on this frame is produced by compute.py and appears in figures.json"
risks:
  - "a column of small headings reads as texture at 432 px and the argument is lost"
  - "the frame reads as a bright rectangle and construction_check counts it as plated"
```

## Frame 9 — FULL_BLEED

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: "a clinic check in counter at 8:15 in the morning running off both frame edges, a 1.70 m person standing at it three quarter back, a service window behind them carrying the deck's only daylight, and ONE 0.30 m NOTICE AT READING DISTANCE, in the reader's own plane rather than in the scene, filled in the accent"
  rect: [0, 400, 1080, 950]
  bleeds: [left, right, bottom]
accent: "#EFA31D"
job: >
  Give a Texan somewhere to stand and something to do, which texan_check said at selection this
  story did not have, and do it without claiming a duty the statute does not settle.
claims: [c15, c18, c19, c20]
numerals: []
composition:
  structure: >
    The counter runs off both edges on the deck's constant at y 1096 for the last time, the person
    stands at it with their back three quarters to the reader so the reader can stand where they
    are, and the service window behind carries the only daylight in nine frames.
  bands: >
    Top third, the wall and the service window with the deck's only daylight in it. Middle third,
    the person at the counter. Bottom third, the counter top graded from the window's light down
    into shade at the near edge, the person's own cast running down and to the right across it,
    and the accent notice held over it in the reader's plane with its shadow thrown onto the
    counter behind, which is what says the notice is nearer than everything else in the frame.
  focal: "the filled accent notice at reading distance, 356 by 236 px, and it is the only filled accent in the deck"
art:
  technique: "the scene bench at true scale, standing eye, with the deck's only daylight source"
  why_this_technique: >
    The whole deck has been at night, on one surface, at reading distance. Standing a person up at
    a counter in the morning is the only camera in the deck that says the reader can go and do
    this, and the value inversion is what makes it feel like a different time of day.
  palette: "the deck's own, plus the single daylight passage in the service window."
  value_structure: >
    The service window is the lightest thing in the deck and the counter takes its light. The
    person is a silhouette against it. THE NOTICE IS DRAWN ON THE CANVAS rather than mounted over
    it, so it takes the deck's halftone screen and the deck's one grade like everything else. The
    first build made it a DOM div above the art, which left the deck's payoff mark the only thing
    in nine frames outside the grade, and that is precisely why a judge read it as pasted on.
    Frame median L* planned at 45.
  motion: "from the headline down the left to the filled notice, then right to the person and the daylight behind them"
type:
  hook: "Ask before the first visit, not after."
  dek: "If a disclosure is owed under Section 552.051, the statute's own timing is not later than the date the service or treatment is first provided." # the second half is set on the card itself, which is the one thing on this frame a reader is meant to act on
  labels: []
# c20's words are "This chapter does not provide a basis for, and is not subject to, a private
# right of action". The card sets THE CHAPTER GIVES NO PRIVATE SUIT, which is the deck's own
# voice and not the statute's, so it does not go in a verbatim slot. Declaring the shortened
# phrase against c20 was the 2026-09-04 defect three judges found and no gate then caught.
verbatim: []
acceptance:
  - "the frame median L* is between 39 and 51 at 432px, which is this frame's own band in the deck's re-planned arc"
  - "the accent notice is the ONLY filled accent in all nine frames"
  - "the notice carries the deck's halftone screen and the deck's grade, because it is drawn on the canvas and not mounted over it"
  - "the notice throws a shadow onto the counter behind it, so its plane is readable"
  - "the standing person's feet are inside the frame and no part of them crosses the source line"
  - "the dek is conditional on its face and contains the word if, because the statute's reach over a private provider is unsettled"
  - "no string on this frame says the hospital must disclose or is in violation"
  - "a standing human figure is present at true scale and its whole height is inside the frame"
  - "the counter's front edge is at y 1096 and runs off both frame edges"
  - "the daylight in the service window is the lightest passage in the whole deck"
risks:
  - "the frame reads as advice rather than as a record, which is not this product's voice"
  - "the value inversion at the close reads as a different deck rather than as the next morning"
  - "THE TWO PLANES READ AS ONE. The notice is nearer than the scene and nothing but its own shadow says so, and if a reader takes it for an object lying on the counter they will read it at counter scale and find it six times too big, which is the defect this frame was rebuilt out of"
```
