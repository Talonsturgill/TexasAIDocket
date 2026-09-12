# Storyboard — carousel no. 22, September 12th, 2026

Docket item `tx-2026-0131`. Claims file `out/2026-09-12/claims.json`, 28 verified claims and 9
rejected findings. Every claim id below is that file's and every quoted string is verbatim from
it. Every numeral comes out of `computed.json`, which `compute.py` writes by lifting figures out
of claim quotes with regular expressions that raise rather than fall back.

## The story, in one paragraph

Texas State University is in the second phase of a TxDOT funded project that reads pavement
damage out of paired 2D surface images and 3D depth data at pixel level. The thing that is
changing is not who drives and not who takes the pictures. TxDOT donated the van and a vendor
already collects the imagery. **What changes is who decides whether a crack counts**, and that
decision is what a pavement condition score is, and a pavement condition score is what TxDOT
uses to identify roads needing repair and plan the money for it.

## THE DIRECTORS ROOM, and what was taken from where

Three treatments came back on three lenses, THE INSTRUMENT, THE SHOULDER and THE HANDOVER. All
three independently converged on three things, which is the strongest signal the room produced
and is why all three are law below: **an accent that means one thing and only one thing**, **the
turn landing on c17**, and **a cover frame with a person on the shoulder beside a vehicle at
true scale**.

**THE HANDOVER is the spine.** Its argument is that every other reading of this story is about a
machine getting better at looking, which is a claim the record can only support at 0.780 and
0.626 and would have to hedge for nine frames, while the record fully supports a chain of custody
over one judgement. Its rotation, its accent law and six of its nine frames are taken as written.

**Grafted from THE SHOULDER:**

- **The accent means a PERSON.** THE HANDOVER's law was "the hand", which is nearly the same
  thing and is harder to hold, because a scanner head is not a hand. THE SHOULDER's is cleaner
  and it makes frame 4, frame 6 and frame 9's absences all mean the same thing. On frame 3 the
  granite moves off the scanner heads and onto the figure standing beside the van.
- **It is always the same road.** Lane width, fog line width and aggregate size are constant
  across every frame that draws pavement, so a reader who measures one frame against another
  gets a true answer.
- **The pickup carries no brake light and no motion streak.** The record says the work posed a
  risk. The drawing does not get to stage a near miss.
- **No frame counts sections.** Ten sections with one marked asserts one in ten, and nothing
  fetched gives a rate. THE HANDOVER's break lines survive this because a single lane with an
  unterminated extent counts nothing.

**Grafted from THE INSTRUMENT:**

- **Nothing is portraited.** No agency mark, no university mark, no lettering on the van, no
  likeness of a named researcher and no portrait of the Dewitt C. Greer Building.
- **The reserved flag red stays unspent, and the reason is stated rather than assumed.** The
  only dated door in this record belongs to TxDOT's governing body and is not about this
  project, so a reserved red on it would be a false urgency.
- **Frame 8's scope goes on the frame.** Against U-Net, in a 2025 paper by this group, and c18
  stays off the frames entirely.

**Cut from THE HANDOVER, on its own stated fallback.** Its frame 9 drew the Ric Williamson
Hearing Room, and its own risk register names the danger first and plainest: the deck would be
drawing a room the record does not put this project in. THE INSTRUMENT and THE SHOULDER both
closed in a room too and both flagged the same risk, so all three treatments walked into it.
**The close is the road the money is aimed at**, and the commission's published calendar stays
as a mono foot where it can be read as what it is.

## THE LIGHT DECK CAP IS THE BINDING CONSTRAINT, and two directors found it before the gate did

`ledger_check.py` sets `LIGHT_L` at 60.0 and `LIGHT_CAP` at 1 over a window of the last eight
entries, counted off `deck_median_L` measured on the shipped PNGs rather than off anything a run
says about itself.

Measured from `artwork.json`, the window this deck joins is 09-04 at 22.5, 09-05 at 16.5, 09-07
at 11.4, 09-08 at 31.5, **09-09 at 71.1**, 09-10 at 18.1, 09-11 at 42.0 and this deck. September
3rd at 73.1 rolls out of the window, and its waiver with it.

**So there is already one light deck in this deck's window and it carries no waiver. A paper
register is available if and only if this deck measures under 60.** The arc below is planned at a
median of 44, which is the most headroom of the three treatments, and **it is measured off the
rendered PNGs at round one rather than at round three**, which is the failure two ledger entries
in a row have recorded.

The arc below was written for the paper register and is kept as the RELATIVE shape it always was,
because what it describes is which frames carry the ink and which breathe. On the inverted
register every value reads as its complement, so frame 2 is the deck's one BRIGHT frame and frame
4 its darkest, exactly as planned, and the deck median lands far under the threshold rather than
far over it.

    frame   1    2    3    4    5    6    7    8    9
    rank   mid  light mid  dark  light dark  mid  mid  dark     measured at every round

**`measure.py` runs after every render pass and writes `measurements.json`.** The cap is counted
off `deck_median_L` and the deck is held to it at round one.

## THE REGISTER, AND THE MEASUREMENT THAT CHANGED IT MID PLAN

**The plan opened on a PAPER register and the first rendered frame refused it, which is the whole
argument for measuring at frame one rather than at round three.**

The paper version of frame 9 rendered clean, read handsomely and **measured a median L\* of 91.5**
against the cap's threshold of 60.0. That is not a drawing that came out too pale. It is what a
PRINT ON PAPER IS: a screen is marks on a ground, most pixels are the ground, and the median of a
hatched field on caliche is caliche. An ink heavy arc cannot move a median that is counting the
paper between the strokes, so the three treatments' planned medians of 44, 48 and 55 were all
unreachable in that register and no amount of extra coverage would have reached them.

**So the register inverts and nothing else about the deck changes.** `TXINK.print` maps the twin's
luminance straight onto the ground to ink axis, so the same scene greys with `ground` and `ink`
swapped give the same drawing on the other material. The page becomes the hot mix and the ink
becomes the caliche.

    ground    #161310   hot mix asphalt, the page itself
    ink       #E4D8C3   caliche, the shoulder stone the type is cut from
    dek       #CFC0A4   the same stone weathered
    furniture #96876E   road base dust
    accent    #9A3B2A   capitol granite, and it means a person

Measured by `measure_palette.py` against the 81 hexes of the last eight decks, where a random
colour's nearest neighbour is p10 9.03 and median 27.17, the accent is the one token that comes
back **CLEAR at dE 17.06**. The furniture is close at 11.50. The two inks sit near the window's
own pale end for the structural reason every register's extremes do.

**Contrast, measured against the ground:** the hook at 13.14 to 1, the dek at 10.34, the
furniture at 5.28. The accent is 2.67 to 1 against the ground and **never carries type**, which
the accent law already required of it: it marks a person and a mark is not a word. Its
findability is HUE rather than luminance, because it is the only chromatic thing in a deck of
warm neutrals, and that is measured on frame 1 where the first granite mark exists rather than
assumed here.

**The hour moves with the register.** A bright sky on this page prints as the heaviest ink mass in
the frame, which puts the loudest thing in the emptiest place, so the light is declared once at
azimuth -58 and **elevation 18**, the end of the working day. That is a low sun like September
10th's and the two decks are told apart by everything else: this one is caliche on asphalt with a
hatched sky and silhouette landscape, that one was rose and violet road base at ground level.
Frames 2 and 5 carry no drawn light at all, being a sheet and a plan.

**Measured result on the first frame built:** median L\* 6.1, p05 4.4, p95 68.8. Under the
threshold with room to spare, and the per frame arc below is now a floor to keep rather than a
ceiling to stay under.

**Type inks were measured twice and the first set is recorded because the lesson is the point.**
On the paper register the furniture had to be DARKER than the ground and `#9B8B72` failed at 2.6
to 1. On this one it has to be lighter. The role is the same and the value is the opposite, which
is why a register change is never a find and replace.

## The rotation

    1 FULL_BLEED  2 DOCUMENT   3 FIGURE_SCALE  4 CLOSE_CROP  5 DIAGRAM
    6 TYPE_AS_OBJECT           7 OBJECT_AND_CAPTION          8 SPLIT_HORIZON   9 FULL_BLEED

`TXLAYOUT.check` returns an empty list. Eight distinct, no consecutive repeat, TYPE_AS_OBJECT
once, FULL_BLEED and CLOSE_CROP three between them, six frames bleeding an edge.

## THE ACCENT LAW

**`#9A3B2A` MEANS A PERSON AND MEANS NOTHING ELSE.** On frames **1, 3, 5 and 7 only**, four of
nine, inside the three to six the gate counts and never over four percent of a frame.

    1  the rater standing on the fog line
    3  the person standing at the van's rear doors, unnamed
    5  the extent the rater's own judgement covered
    7  the verification sheet under the engineer's hand

Frames 2, 4, 6, 8 and 9 carry none, and on each of them the reason is the same: no claim on that
frame has a person in it. **Frame 9's absence is the load bearing one**, because no claim puts
this decision in a room with a named decider, so no granite marks a hand there.

## The turn

**Frame 7, set up by frame 6 at maximum volume.** Frames 1 through 6 build one direction without
hedging, that the judgement left the shoulder, and frame 6 gives the principal investigator's own
case for it in four words formed in the road itself. Frame 7 reverses it out of the same team's
own peer reviewed paper, which says the precision of the technology often leads to inaccuracies
that must be verified by pavement engineers. A person sits back down at a desk with the granite
sheet under their hand, and the accent law makes the reversal legible before a word is read.

## WHAT THREE SMOKE TESTS ESTABLISHED BEFORE A DOSSIER WAS WRITTEN

The paper register has never been printed by this project and the example deck is night paper
throughout, so three throwaway frames were rendered and read before any frame of this deck was
planned. Each found something that would otherwise have cost a review round.

1. **Furniture ink at `#9B8B72` measures 2.6 to 1 against the paper and `qa.py` warned on every
   line of it.** The values above are the answer and they are measured, not chosen.
2. **`TXINK.reserve` has to be asked for BOTH bands on a paper frame.** The first probe reserved
   only the top, the source line and the site line printed over a dark hatch, and `qa.py` failed
   it as a rule struck through the glyphs. Every frame calls the reserve for the band its type is
   in.
3. **A hand built sprite's part key is `type`, not `kind`, an ellipse takes `cx cy rx ry` and a
   line takes `pts` and `width`.** The survey van's first draft used `kind` and `x y w h`
   throughout. **It drew nothing, and render.py reported zero errors and zero warnings.** This is
   the SKILL's own NaN trap wearing a different costume, and the only thing that caught it was
   opening the PNG.

A fourth thing the probes settled is craft rather than plumbing. **A pavement surface at detail
scale reads, and a crack is told from a stain by a LIT LIP on the crack's upper edge**, which is
what a depth map sees and a photograph does not. That is claim c6 drawn rather than captioned.
The stain has to be drawn far darker than the first probe made it, or a reader cannot tell there
are two things to tell apart.

## THE ORDER OF WORK

**Frames 9, 8 and 7 first.** Four consecutive ledger entries record a ninth frame thinner than
its eighth, and none has paid it. Then 1, then the middle. Every frame is read at 432 px with no
type on it before its type is fitted.

---

## THE NINE

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: a rater standing on the fog line of a two lane highway at 1.7 m in a hard hat with a clipboard, at Z 7, and a truck_semi at true 17 by 4.1 m passing in the far lane at Z 26, seen from the shoulder seven metres behind him
  rect: [0, 240, 1080, 1110]
  bleeds: [left, right, bottom]
accent: "#9A3B2A"
job: >
  Stop the scroll on the wince. A Texan has driven past this person, and no caption is needed to
  know what that job is or why somebody would want it done from a van instead.
claims: [c1, c15, c16]
numerals: []
composition:
  structure: >
    Camera at 1.62 m, horizon at 668, focal 860 px, light az -58 el 18 as the register declares
    it once for the whole deck. THE CAMERA STANDS ON THE SHOULDER, not on the centreline, so
    the road's centre is 2.10 m to its right and the rater has the left third to stand in. The
    rater is on the near fog line at Z 3.55 and comes out 412 px tall, 31 percent of the frame,
    the one vertical in a frame made entirely of horizontals. The semi is in the far lane at
    Z 30 and comes out 118 px tall, which is what a 4.1 m body at that depth IS. The dossier
    first declared Z 7 and Z 26 against a 900 px focal and a horizon at 470, and none of those
    three survived the frame being built: the rater at Z 7 on the fog line projected to x 41,
    cut in half by the left edge. The plan is corrected to the geometry one TXSCENE call
    actually solved rather than the render being bent to a plan that put the subject off frame.
  bands: >
    TOP third, unscreened paper carrying the kicker, the hook and the dek. MIDDLE third, the
    horizon, the semi, the fence line and the rater's head. BOTTOM third, the pavement and the
    caliche shoulder cropped by the frame, fading to paper under the furniture band.
  focal: >
    The rater's torso and head, an AREA of about 160 by 230 px left of centre, the largest single
    value contrast in the frame and the only granite on it.
art:
  technique: "TXSCENE at standing eye with TXOBJ truck_semi, fence_post and mesquite and a TXFIG rater, printed by TXINK as a halftone at cell 8, angle 22, contour plate at 1.0, -0.8 px."
  why_this_technique: >
    A halftone is the newspaper photograph and frame 1 is a photograph of a person at work.
    Nothing else in the deck is a photograph. A coarse cell keeps the dots visible as dots at
    feed size and says a hand made this before a word is read.
  palette: >
    page #161310 hot mix, ink #E4D8C3 caliche, granite #9A3B2A on the rater alone. Twin greys, sky
    #0A0A0A over a lit haze, caliche shoulder #8E8E8E, hot mix #3A3A3A, fog line #D2D2D2, semi
    body #BEBEBE so the rater does not merge with it, rater #D8D8D8, crack floor #101010 with a
    lit lip #6A6A6A.
  value_structure: >
    The sky is the lightest field and carries the type. The rater is the darkest. The caliche
    shoulder behind him is the mid that separates them. Target frame median L* 38.
  motion: >
    Hook, dek, down the fence line to the semi, across to the rater, down to the shoulder.
type:
  hook: "Somebody used to stand here."
  dek: 'A rater measured the length and severity of the distress by hand on a sampled portion of the pavement section, in the traffic and the weather.'
  labels: ["TEXAS STATE UNIVERSITY", "Second phase, closer to statewide deployment", "01 / 09", "c1 c15 c16   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim:
  - c15: "a sampled portion of the pavement section"
acceptance:
  - "the rater measures 405 to 420 px head to heel and the semi 110 to 125 px, both solved from ONE TXSCENE call at the depths declared in composition, never typed"
  - "the camera stands on the shoulder rather than on the centreline, so the road's centre sits right of the frame's middle and the rater is not cut by the left edge"
  - "the rater reads as a mass distinct from the caliche behind him, measured on the render inside the focal rect rather than asserted from the twin"
  - "the semi carries no brake light, no motion streak and no speed line, because the record says the work posed a risk and the drawing does not stage a near miss"
  - "granite appears on the rater's BODY and nowhere else, the clipboard included, between one and three percent of the frame"
  - "no halftone dot sits inside the hook's or the dek's glyph band"
risks:
  - "the rater merges with the ground behind him. The twin greys are declared far apart for exactly this and the acceptance item measures the separation on the render."
```

```yaml
slide: 2
layout: DOCUMENT
primary_image:
  subject: a printed performance measure sheet 0.60 m wide, square to the camera, orthographic, running off the bottom edge, set as an engineering chart with a rule pair and eleven hairline rows
  rect: [90, 210, 900, 1140]
  bleeds: [bottom]
accent: "none"
job: >
  Show what the pen was writing. The score is a thing the agency publishes a definition for, and
  the money sentence under it is the agency's own words rather than this deck's reading of them.
claims: [c8, c9, c10]
numerals:
  - value_from: c9
  - computed_by: "compute.py good_score, lifted out of c9's own quote by regex"
composition:
  structure: >
    Dead flat orthographic. The deck's declared camera does not apply and the frame says so. The
    definition sentence as the head, the threshold figure in JetBrains Mono at display size in
    the middle band between a rule pair, then the ratio sentence and the money sentence as two
    ruled rows beneath.
  bands: >
    TOP third, the reserve, hook and dek on paper. MIDDLE third, the sheet head, the definition
    and the ruled threshold. BOTTOM third, the sheet's lower half carrying the ratio and the
    money sentence, the sheet's own cast shadow on the desk under its lower edge, and the line
    screen's grain in the desk running out to the bleed.
  focal: >
    The threshold figure and the rule pair bracketing it, an AREA of about 480 by 260 px in the
    sheet's middle, the highest local contrast on the frame.
art:
  technique: "A drawn sheet with TXINK.wobble on its edge over a line screen at cell 5, angle 90, with the engraving confined to the desk band at the head and DOM type on the sheet."
  why_this_technique: >
    A document frame has to BE a document, so the type on the page is the image rather than a
    caption about one. The engraving stays in the desk band where there is open ground for it,
    which is the failure carousel no. 21 recorded when its intaglio had nowhere to be.
  palette: >
    page #161310 hot mix, ink #E4D8C3 caliche, no granite. The sheet is laid over the finished
    print in the ink itself, its rules and its type in the page colour #161310, the sheet head in
    #3A322A, the row labels in #4A4036, the quoted cells in #241E19, the dek in #332B23, the desk
    #242424 with its engraving in #464646 and #3A3A3A, and the sheet cast #060606.
  value_structure: >
    The deck's light inversion. Paper across three quarters of the frame, ink rules and type at
    the floor. Target frame median L* 76, thirty two above the deck median.
  motion: >
    Hook, onto the sheet at the definition, down to the threshold between the rules, down to the
    money sentence.
type:
  hook: "Seventy is where good begins."
  dek: 'The agency defines it as "a combined index of ride quality and pavement surface distress."'
  labels: ["THE SCORE", "02 / 09", "PAVEMENT CONDITION SCORE", "GOOD OR BETTER", "c8 c9 c10 c11   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim:
  - c8: "a combined index of ride quality and pavement surface distress"
  - c10: "Tracking pavement quality helps TxDOT identify roads in need of repair and plan funding"
verbatim_revised_2026_09_12: >
  The plan set three whole sentences on this sheet and coherence_check measured the frame at
  108 words against a 65 word ceiling, which at 432 px is a paragraph rather than a slide. The
  definition and the money sentence stay, each cut to the span the frame prints. The ratio
  sentence goes, and c11 comes off the cite line with it, because a claim id on a frame is a
  promise that the frame shows something from it.
acceptance:
  - "every figure on the frame is JetBrains Mono with tabular numerals"
  - "the three quoted sentences are present character for character against claims.json and each carries its claim id in the source line"
  - "the sheet is cut by the bottom edge and its left and right margins are visible, so it reads as a page rather than as a plate"
  - "at least eleven distinct ruled rows are countable at 432 px"
  - "the sheet never imitates the txdot.gov page layout and carries no seal, logo or screenshot furniture"
risks:
  - "a sheet carrying three quoted sentences reads as a wall. Set the definition small, the threshold large, and the money sentence in the middle weight."
  - "this is the deck's only frame over 60 and the cap is counted on the deck median. If the deck measures over 60 at round one, ink goes onto frames 1 and 9 rather than a wash onto this one."
```

```yaml
slide: 3
layout: FIGURE_SCALE
primary_image:
  subject: the TxDOT donated mobile research van at 6.4 by 2.35 by 2.6 m, three quarter from the rear left at Z 7.5, with a 2.4 m transverse scanner boom at 2.9 m carrying two 0.45 m sensor heads, cut by the right edge, and an unnamed 1.7 m figure at Z 6 standing at its rear doors
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
  plan_revised_2026_09_12: >
    The first rect described a box floating inside the frame and declared a bottom bleed the
    drawing does not have. layout_check measured the frame and found ink running off the RIGHT
    edge only, because the bottom band is the furniture reserve and the ground fades into it.
    Declaring a bleed the frame does not have makes a critic grade against the wrong plan, so
    the plan is corrected to what was built rather than the other way round.
accent: "#9A3B2A"
job: >
  Name the agency's own contribution as a physical object and make the handover visible. The
  person is beside the machine rather than on the road, which is the whole of what has happened.
claims: [c5, c1, c3]
numerals: []
composition:
  structure: >
    Camera at 1.62 m, horizon at 840, focal 1050 px, same light. The van is a long horizontal
    ink body running out of the right edge. THE FIGURE STANDS AT THE SAME DEPTH AS THE VAN, at
    Z 9.0, and comes out 198 px against the van's 303. The plan first asked for 283 px against
    284 so the two would read as the same height, which would have put the person NEARER the
    camera than the thing they are the scale for, and a figure-scale frame whose figure is
    closer than its subject is the one arrangement that makes the comparison a lie.
  bands: >
    TOP third, the reserve, hook and dek on paper. MIDDLE third, the van's roof and the boom.
    BOTTOM third, the van's body, the figure, the caliche and the contact shadows, cropped.
  focal: >
    The figure at the rear doors, an AREA of about 110 by 285 px left of the van's mass, the only
    granite in the frame and the one vertical against a horizontal body.
art:
  technique: "A hand built van in metres on a TXSCENE ground plane with TXFIG beside it and a two part contact shadow under each tyre, printed by TXINK as a hatch at cell 7, angle 40."
  why_this_technique: >
    The engraver's cross hatch is what gives a long flat flank a readable tone without turning it
    into a field of dots, and it is a different screen from both frames beside it. The contact
    shadow is two parts because a one part shadow reads as a drop shadow and cheapens the frame.
  palette: >
    page #161310 hot mix, ink #E4D8C3 caliche, granite #9A3B2A on the person alone. Twin greys,
    sky #0A0A0A, caliche yard #7A7A7A, van body #9C9C9C, its sill and tyres #3A3A3A, its glass and
    roof cap #E8E8E8, the fence #4A4A4A and the person #D8D8D8.
  value_structure: >
    The caliche is the light field. The van body is the dark. The contact shadows under the tyres
    are the darkest and are what make it stand on something. Target frame median L* 46.
  motion: >
    Hook, down to the boom, along the roof line to the left, down the flank to the figure.
type:
  hook: "TxDOT handed over a van."
  dek: 'The university''s release lists what prepared the data. An automated 2D/3D pavement laser scanner, and "a TxDOT-donated mobile research van."'
  labels: ["THE EQUIPMENT", "Ingram School of Engineering", "THE RELEASE LISTS THE SCANNER AND THE VAN SEPARATELY", "03 / 09", "c1 c3 c5   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim:
  - c5: "a TxDOT-donated mobile research van"
acceptance:
  - "the van's silhouette comes apart into at least six named pieces at 432 px, which are body, roof cap, side and rear door glass, door seam, wheels with their rims, boom mast and transverse boom with two sensor heads. THE CAB IS OFF THE RIGHT EDGE and there is no cab glass on the frame"
  - "the figure and the van stand at THE SAME DEPTH, Z 9.0, and their heights agree with the projection at that depth within four percent, 198 px against 303 px"
  - "the van carries no lettering, no livery and no agency mark anywhere on the body"
  - "the frame states in mono that THE RELEASE LISTS THE SCANNER AND THE VAN SEPARATELY, because c5 lists an automated 2D/3D pavement laser scanner and a TxDOT-donated mobile research van as two items in one sentence about what prepared the data, and no claim mounts one on the other. The boom is drawn and the disclosure is printed beside it"
  - "the contact shadow under each tyre has a crisp core and a softening body, sampled at the tyre contact and 0.4 m outboard"
  - "granite is on the figure only and nothing on the frame names or implies who employs them"
risks:
  - "a vehicle not in the catalogue drawn as one polygon is the slab failure. Six named pieces are specified in metres and the acceptance item measures the silhouette coming apart. If it will not come apart, rebuild it from the ambulance sprite's chassis proportions and put the van in the backlog as a catalogue proposal."
```

```yaml
slide: 4
layout: CLOSE_CROP
primary_image:
  subject: 1.2 m of aged hot mix filling the frame at 0.35 m eye, one 0.9 m crack and one bitumen stain of near identical plan shape side by side, with the same 1.2 m redrawn along the foot as a shallow section where the crack is a trough and the stain is flat
  rect: [0, 0, 1080, 1350]
  bleeds: [top, left, right, bottom]
accent: "none"
job: >
  Get inside the decision at the height a person actually looks at a crack from, and show the one
  discrimination the whole method exists to make.
claims: [c6]
numerals: []
composition:
  structure: >
    Camera at 0.35 m eye, no horizon. Plan of the surface from y 0 to y 1080, then a hairline,
    then the section band from y 1080 to 1350 running off both edges. The crack and the stain sit
    side by side in the plan at the same two x positions the section reads.
  bands: >
    TOP third, the crack and the stain entering the frame. MIDDLE third, both at full extent with
    their mono marks beside them. BOTTOM third, the section band with the crack's trough walls in
    light and shade, the depth of the asphalt body under the surface line, and the stipple grain
    running off both edges into the hook's reserve.
  focal: >
    The crack mouth and its lit lip, an AREA of about 300 by 300 px left of centre, the only
    place in the frame carrying all three depth values against each other.
art:
  technique: "An authored Canvas stipple field at cell 5 where the dots ARE the aggregate, with a carved crack giving a lit lip, a side wall and a floor, over a drawn section profile."
  why_this_technique: >
    A stipple is the one screen in the library where the technique and the material are literally
    the same thing, because a stone population is a count of marks. The lit lip is the craft
    point of the frame, since it is what a depth map sees and a photograph does not.
  palette: >
    page #161310 hot mix, ink #E4D8C3 caliche, no granite. Twin greys, asphalt #6E6E6E across the
    plan, aggregate flecks #8E8E8E and #5E5E5E with lit faces #A6A6A6 and #C4C4C4, the crack and
    the stain both #1C1C1C in plan, the section body #3A3A3A, the trough floor #101010, its shaded
    wall #4A4A4A, its lit lip #EFEFEF and the surface line #D6D6D6.
  value_structure: >
    The deck's floor. The crack's floor is the darkest thing in the deck and its lit lip is the
    lightest thing in the frame. The stain is a mid with no lit edge at all, which is the point.
    Target frame median L* 17.
  motion: >
    Down the crack from the top edge, left to the stain, down to the section band, across it.
type:
  hook: "Depth tells a crack from a stain."
  dek: 'The system pairs 2D photos with 3D depth maps. It ranks severe hazards like crumbling concrete above minor surface cracks.'
  labels: ["THE SURFACE", "04 / 09", "STAIN", "CRACK", "SECTION", "c6   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim: []
acceptance:
  - "in the plan half the crack and the stain differ by under 6 dE at 432 px, because the frame's whole argument is that they look alike on the surface"
  - "THE SECTION SHOWS THE CRACK ALONE. No mark of any kind sits at the stain's x position in the section band, because an unbroken profile drawn there is a claim that a stain has no depth and no fetched source carries it. This frame's own risk block prescribed exactly this disposition"
  - "the crack is drawn as a body with a lit lip, a side wall and a floor, three distinct measured values, never as a black line"
  - "the stipple field does not grey out, meaning the plan half carries a per pixel luminance std over 6 in at least a quarter of its 8 px cells, MEASURED ON THE 432 px THUMB, because a field that holds at full resolution and dissolves at feed width has failed at the only size a reader sees"
  - "no printed numeral, no scale bar and no dimension appears anywhere INSIDE THE PRIMARY IMAGE RECT, and the section carries no depth figure because no claim carries one"
risks:
  - "the first probe's stain was almost invisible and the frame lost its argument. Draw it at twice that density and read it at 432 px before calling the frame done."
  - "drawing the stain as an unbroken profile is a READING of c6 rather than a quotation of it. No word on the frame says a stain has no depth, and if an integrity judge reads the section as an assertion, the section keeps the crack and loses the stain."
```

```yaml
slide: 5
layout: DIAGRAM
primary_image:
  subject: 150 m of one 3.6 m lane in true plan straight down, running off both side edges, with stationing ticks along the top, the sampled portion the old method read marked as a granite run terminated at both ends by drafting break lines, and the continuous reading drawn as an unbroken fine screen over the whole length
  rect: [0, 300, 1080, 760]
  bleeds: [left, right]
accent: "#9A3B2A"
job: >
  Draw what the old judgement actually covered against what the new one does, in plan, and say
  with the drawing rather than with a hedge that the record does not state the fraction.
claims: [c15, c1]
numerals: []
  # NO NUMERAL ON THIS FRAME AT ALL. The plan asked for the stationing interval printed once in
  # mono. numeral_trace authorises a printed figure only where its digits occur in the evidence
  # of a claim the frame cites, and neither c1 nor c15 carries that digit in its quote, its
  # text, its title or its url. A reader following the cite would arrive at a page without the
  # number. The ticks carry the rhythm and the interval is not printed.
composition:
  structure: >
    True plan, zero perspective, no light and no shadow anywhere on this frame. The lane band
    sits across the middle third. Leaders run up to two mono labels above it and one below.
    THE SAMPLED RUN TAKES BREAK LINES AT BOTH ENDS because no fetched source states what
    fraction was sampled, so the drawing asserts an extent it does not know. NO FRAME IN THIS
    DECK COUNTS SECTIONS, because ten sections with one marked asserts one in ten.
  bands: >
    TOP third, the reserve, hook, dek and the stationing ticks. MIDDLE third, the lane band, the
    granite run with its break lines, and the leaders. BOTTOM third, the lane band's lower half
    under its continuous screen, the leader line down to the mono label, the neatline, and the
    line screen's grain carried to the bleed.
  focal: >
    The granite run and both break lines, an AREA of about 400 by 180 px across the middle, the
    only saturated thing on an otherwise line drawn frame.
art:
  technique: "Survey and engineering drawing register in true plan, four stroke weights, a neatline, DOM mono labels and SVG leaders declared in window.__txLeaders, printed by TXINK as a line screen at cell 4, angle 0."
  why_this_technique: >
    A claim about EXTENT wants a plan, because a plan is the one view in which extent is the
    whole image. A line screen at the finest cell keeps the lane a surface rather than a bar.
  palette: >
    page #161310 hot mix, ink #E4D8C3 caliche, granite #9A3B2A on the sampled run. The lane band ramped
    from #787878 through #9C9C9C to #7E7E7E under its own fine screen in #A4A4A4 and #7A7A7A, the lane edges #EAEAEA, the
    stationing ticks #D2D2D2, the leaders #CFCFCF and the neatline #8A8A8A. No light anywhere.
  value_structure: >
    Paper is the ground. The lane band is the mid. The ticks and leaders are the ink. Target
    frame median L* 58.
  motion: >
    Hook, along the tick row left to right, down into the lane, along the granite run to the
    break line at its end.
type:
  hook: "The old rating read a sample."
  dek: 'Manual collection happened at "a sampled portion of the pavement section." The university describes the new reading as "pixel-level detection of pavement damage."'
  labels: ["THE EXTENT", "05 / 09", "SAMPLED PORTION", "PIXEL LEVEL, CONTINUOUS", "c1 c15   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim:
  - c15: "a sampled portion of the pavement section"
  - c1: "pixel-level detection of pavement damage"
acceptance:
  - "both ends of the granite run carry a drafting LONG BREAK line, a straight run interrupted by a visible Z kink, drawn in the ink so the kink reads against the granite. It is never a dimension terminator, because an arrowhead is the drafting sign for a MEASURED span and this frame refuses to assert one"
  - "the stationing ticks are drawn at a constant interval computed in code, every fifth one taller, and NO numeral appears anywhere on the frame"
  - "no leader crosses a letterform and every leader stops at least 12 px short of the glyph band"
  - "the lane band is cut by both side edges"
  - "the granite is a HATCH over the lane rather than a solid fill, so the lane's own screen reads through it and the mark never outweighs the small person-marks on frames 1, 3 and 7 that the accent law is built around. Under five percent of the frame, measured on the render"
risks:
  - "a plan with no light is the flattest frame in the deck and craft_floor reads variance per frame. The tick row, the four stroke weights and the screened lane are what carry it."
```

```yaml
slide: 6
layout: TYPE_AS_OBJECT
primary_image:
  subject: the four words OFTEN SUBJECTIVE AND COSTLY formed in hot mix as RAISED bodies at 0.28 m cap height on a ground plane at 30 degrees oblique, each letter with a lit top face, a shaded wall and a short hard cast from the declared sun
  rect: [60, 400, 960, 560]
  bleeds: []
accent: "none"
job: >
  Give the argument for the handover at full volume, in the principal investigator's own words,
  formed in the material the argument is about.
claims: [c4]
numerals: []
composition:
  structure: >
    Camera at 1.62 m, horizon at 330, focal 820 px, same light. ONE ELEMENT, TWO LINES, ONE
    DEPTH, standing upright on the road rather than lying flat on it. The size is solved: each
    line is fitted to its measure, its cap height is MEASURED off the rendered glyph, and the
    depth it stands at follows from the declared 0.28 m cap. The recession is carried by the
    concrete joints running back behind the words. The first build set the two lines as two
    spans at two depths so they receded, which is honest geometry for type lying flat and
    dishonest bookkeeping everywhere else: build_copy.py derives the deck's copy record from the
    largest laid out node, and two spans meant the record said this frame's hook was AND COSTLY.
    The attribution in mono below the mass, on its own knockout plate.
  bands: >
    TOP third, the kicker and the lit ground plane running back to the horizon. MIDDLE third, the
    first line of raised letters, their walls and their casts. BOTTOM third, the second line's
    letters with their casts falling down and left across the ground, the halftone grain in the
    lit ground between them, and the attribution under it all.
  focal: >
    The first line's lit top faces, an AREA of about 960 by 290 px, the brightest sustained
    region in the frame.
art:
  technique: "Letterforms as raised bodies on a TXSCENE ground plane, each with a top face, a wall and a cast, printed by TXINK as a halftone at cell 9, angle 8."
  why_this_technique: >
    RAISED rather than cut, declared here because a previous deck declared a milled trough and
    shipped raised type and the ledger recorded a drawing nobody made. A coarse halftone at cell
    9 keeps the dots visible as dots at display size on a frame that is mostly one mass.
  palette: >
    page #161310 hot mix, ink #E4D8C3 caliche, no granite. The letter tops are DOM type in
    #E9DECB, their walls #2A2520, the concrete ground #BDBDBD, the sky #080808 and the attribution
    plate the page colour #161310 with its type in #CFC0A4 and #E4D8C3.
  value_structure: >
    Heavy ink. The letter tops are the light, the walls are the dark, the ground between the
    casts is the mid. Target frame median L* 27.
  motion: >
    Down the first line left to right, down the casts, into the second line, down to the
    attribution.
type:
  hook: "OFTEN SUBJECTIVE AND COSTLY"
  dek: 'Wang describes the purpose as reducing reliance on traditional human inspection. He calls that inspection "often subjective and costly."'
  labels: ["THE ARGUMENT", "06 / 09", "FENG WANG, TEXAS STATE UNIVERSITY", "c4   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim:
  - c4: "often subjective and costly"
acceptance:
  - "the word OFTEN is present on the frame, because dropping a qualifier the claim carries is a fault this project has shipped before"
  - "at 432 px all four words are legible as words, read with no type furniture on the frame before frame 5 is started"
  - "every letter has three measured values, a top face, a wall joined to it with no gap, and a cast continuing beyond the wall in a darker value. EVERY CAST RUNS DOWN AND RIGHT, in agreement with the deck's light declared once at az -58 el 18. The item read down and left against az +34 el 52 until 2026-09-12, which was the treatment's own light and not the deck's, and the register section wins"
  - "the quote is attributed to Wang by name on the frame and is set apart from the deck's own voice"
  - "no glyph is rotated more than one degree in the DOM and the type is DOM text rather than canvas fillText"
risks:
  - "raised type on a ground plane at an oblique is the hardest drawing in the deck and a low contrast proud body is exactly what disappears at feed size. If the four words are not words at 432 px, the frame becomes a plain quote plate and TYPE_AS_OBJECT is spent nowhere."
```

```yaml
slide: 7
layout: OBJECT_AND_CAPTION
primary_image:
  subject: a desk at 1.6 by 1.2 m with an office_chair and a seated 1.7 m figure at Z 2.2, a monitor carrying nothing legible, and one 0.30 by 0.21 m sheet on the desk under the figure's hand
  rect: [20, 720, 1042, 500]
  bleeds: []
  plan_revised_2026_09_12: >
    The plan declared the desk's near edge cut by the bottom edge. At a seated eye of 1.48 m
    and a desk at Z 2.72 the near edge lands well above it, and the furniture reserve owns the
    band below that. layout_check measured no bleed on this frame and it is right.
accent: "#9A3B2A"
job: >
  Turn the deck. The same team's own paper puts the judgement back in a human hand, and the
  accent that was on the rater in frame 1 comes back to a person here.
claims: [c14, c17]
numerals: []
composition:
  structure: >
    Seated eye at 1.15 m, horizon at 700. THE DECK'S ONE INTERIOR AND ITS ONE SEATED CAMERA, and
    the change is the argument, because the reader sits down where the verification happens. The
    desk mass left of centre, the figure behind it, the chair back rising right, the near edge of
    the desk cut by the bottom edge.
  bands: >
    TOP third, the reserve, hook and dek on the unlit wall. MIDDLE third, the figure, the monitor
    and the chair back. BOTTOM third, the desk top and the sheet under the hand, the two part
    contact shadow under each castor, and the floor carrying the light's falloff out to the
    bleed.
  focal: >
    The sheet and the hand on it, an AREA of about 180 by 130 px below centre, the only granite
    in the frame.
art:
  technique: "TXSCENE interior at seated eye with TXOBJ desk and office_chair and a seated TXFIG, a two part contact under each chair castor, printed by TXINK as a hatch at cell 6, angle 68."
  why_this_technique: >
    The cross hatch at a fine cell carries a falloff across a large flat floor without banding,
    which is where a halftone at this size would post to visible rings, and it separates a figure
    from the furniture beside it. The figure and the furniture take separate twin greys so they
    do not merge into one pale mass, which is the named failure of TXFIG.
  palette: >
    page #161310 hot mix, ink #E4D8C3 caliche, granite #9A3B2A on the sheet alone. Twin greys, the
    unlit room #0C0C0C, the figure and the hand #DCDCDC, the desk #6E6E6E, the chair #4E4E4E, the
    unlit floor #2C2C2C and the sheet in granite #9A3B2A.
  value_structure: >
    The wall is the light, the figure is the dark, the desk and the chair are the two mids
    between them. Target frame median L* 49.
  motion: >
    Hook, to the figure's head, down the arm to the hand, onto the sheet.
type:
  hook: "An engineer still has to check."
  dek: 'The team''s own 2025 paper says the precision of the technology often leads to inaccuracies.'
  labels: ["THE TURN", "SENSORS 25(4), 2025", "07 / 09", "c14 c17   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim:
  - c17: "must be verified by pavement engineers"
acceptance:
  - "the figure, the desk and the chair each read as separate masses on the render, declared as #DCDCDC, #6E6E6E and #4E4E4E in the twin"
  - "the monitor carries no legible string of any kind, because nothing in the record describes what is on it"
  - "THE GRANITE IS THE SHEET ITSELF, a filled plane in the desk's own plane with its own ruling, and a HAND RESTS ON IT. The first build put a granite pencil loop on a white card with the nearest finger 165 px away, so on the deck's one turn the accent marked an empty circle on a desk"
  - "the seated figure's eye height agrees with the declared 1.15 m camera within three percent"
  - "the desk floats clear of the furniture reserve and NO edge bleeds, which is what layout_check measures on this frame"
risks:
  - "a crowd as a mass. The three twin greys are declared well apart for exactly this and the acceptance item measures the separation on the render."
```

```yaml
slide: 8
layout: SPLIT_HORIZON
primary_image:
  subject: below one straight cut at y 552, a 3 m run of pavement under one long raking shadow with a single hairline crack crossing it, cut by the left, right and bottom edges, and the measurement carried on a plate laid on that road
  rect: [0, 552, 1080, 798]
  bleeds: [left, right, bottom]
  plan_revised_2026_09_12: >
    THREE THINGS THE FIRST BUILD GOT WRONG AND THE MEASUREMENT FOUND. The cut was planned at
    y 594 with the chart ABOVE it, and the chart's own axis band collided with the dek, so the
    halves were swapped and the cut fell to 743. That put the pavement on top, where the type
    reserve eats it, and SPLIT_HORIZON's own rule asks the image side for 55 percent of the
    height. The drawn side was really 20 percent. The cut is now at 552, the pavement owns 59
    percent below it and the type sits on flat ground above it, which is the archetype's shape.
    The RAKE was a comb of eight equal light bands and it gave the frame no mass at all, 0.13 of
    the subject in its largest piece against a floor of 0.50. One long shadow replaces it.
    And the four figures, which are the whole point of the frame, were set straight onto the
    aggregate. They are on a plate now, laid on the road with its own cast under it.
accent: "none"
job: >
  Print the measured result honestly, on a zero anchored axis, and let the reader see that the
  hardest class is still the lowest scoring one.
claims: [c19, c20, c7]
numerals:
  - value_from: c19
  - value_from: c20
  - computed_by: "compute.py f1_unet, f1_model, f1_thin_unet, f1_thin_model and the two gains"
composition:
  structure: >
    One straight horizontal value break at y 552, nowhere near the vertical centre. ABOVE it,
    flat ground carrying the hook and the dek and nothing else. BELOW it, 59 percent of the
    height is pavement under one long raking falloff with a hairline crack crossing the lower
    band. THE MEASUREMENT IS A CALICHE CARD LAID ON THAT ROAD, x 100 to 980 and y 612 to 1024,
    carrying the zero anchored axis, the two plotted segments, the four endpoint labels in mono
    and the scope line. Both endpoint pairs sit BELOW their own point: above it, the 0.780 pair
    landed on the 1.0 gridline with dashes running out of either side of it and a reader at 432
    px took a published F1 score for a perfect one.
  bands: >
    TOP third, the reserve, the hook and the dek on flat paper. MIDDLE third, the axis, the two
    plotted segments, the four endpoint labels and the cut. BOTTOM third, the pavement under its
    raking light, the hairline crack and its shadow, and the stipple grain running off both edges
    and the bottom.
  focal: >
    The card's chart area with its zero baseline and endpoint labels, an AREA of about 560 by
    240 px above the cut, the only ink on a paper ground.
art:
  technique: "An authored Canvas pavement at an oblique over a drawn slope chart with the axis anchored at zero and the zero printed, printed by TXINK as a stipple at cell 5, angle 0, below the cut only."
  why_this_technique: >
    A bar pair invites a comparison the claim does not license and a dial is forbidden outright,
    so the eye reads an angle against a drawn zero and nothing else. The stipple returns from
    frame 4 because this is the same material seen from further away, which ties the deck's two
    surface frames together.
  palette: >
    page #161310 hot mix, ink #E4D8C3 caliche, no granite. The road #8E8E8E under one raking
    falloff, the cut #E8E8E8, the crack #121212 with its lit lip #D6D6D6, and the measurement on a
    caliche card #E4D8C3 whose axis is #6B5B48, whose zero and plotted segments are the page
    colour #161310, whose category labels are #544636 and whose scope line is #241E19.
  value_structure: >
    The pavement below the cut is the dark. The paper above it is the light. The cut between
    them is the frame's only hard edge. Target frame median L* 44.
  motion: >
    Hook, down to the zero, up the two segments, down over the cut onto the crack.
type:
  hook: "Thin cracks still score the lowest."
  dek: 'The largest gain came on the thinnest cracks.'
  labels: ["THE MEASUREMENT", "TWO PUBLISHED F1 SCORES", "08 / 09", "ALL DISTRESS", "THIN CRACKS", "U-NET", "THIS MODEL", "One 2025 paper by this group.", "c7 c19 c20   TEXAS AI DOCKET", "texasaidocket.com"]
verbatim: []
  # NO VERBATIM FRAGMENT ON THIS FRAME. The plan declared c7's "improve detection of hairline
  # cracks" and the frame prints no such string, which verbatim_check is right to refuse: a
  # verbatim slot is a promise that these are somebody else's words, and a promise for a string
  # nobody drew describes a frame the run did not make. U-NET stays as a label because it is a
  # model's name, which is what the paper calls it.
acceptance:
  - "the y axis runs from zero to one, the zero is drawn and printed, and the thin crack rise measures nine to ten percent of the axis height"
  - "all four figures are JetBrains Mono with tabular numerals and each comes from computed.json"
  - "the frame prints the scope, one 2025 paper by this group, and never presents either figure as a statewide accuracy result"
  - "the value break is one straight horizontal line at y 552 and the pavement half is at least 55 percent of the height"
  - "the crack in the lower half is the thinnest drawn element in the deck and is still visible at 432 px"
risks:
  - "0.531 to 0.626 on a zero anchored axis is a nearly flat line at 432 px. If the frame dies at feed size the fix is a longer x span, never a truncated y axis, which would be a lie told with a true number."
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: a farm to market road at the end of the working day at true scale, a house at 140 m, a water tower at 260 m, a live oak at 40 m, a mailbox and a fence line near, the road running from the bottom edge to the horizon, nobody in the frame
  rect: [0, 300, 1080, 1050]
  bleeds: [left, right, bottom]
accent: "none"
job: >
  Close on the road the money is aimed at, and hand the reader the one dated public thing that
  exists, stated as exactly what it is.
claims: [c10, c7, c23, c24, c25, c26]
numerals:
  - computed_by: "compute.py commission_date, the first calendar entry after the run date"
  - computed_by: "compute.py agenda_posts_on and agenda_lead_days"
composition:
  structure: >
    Camera at 1.62 m, horizon at 700, focal 780 px, the light dropped to el 18 for the hour. The
    road runs from the bottom centre to the horizon. The house, the water tower and the oak sit
    on the horizon at their true distances. The mailbox and the fence are near, cropped. It is
    the same road as frames 1, 4, 5, 6 and 8, at the same lane width and the same aggregate.
  bands: >
    TOP third, the sky, the reserve, the hook and the dek. MIDDLE third, the horizon with the
    water tower, the house and the oak. BOTTOM third, the road surface taking the long rake of
    the low sun, the mailbox and the fence posts with their shadows lying across the caliche, and
    the wordmark and the mono foot on the reserve beneath them.
  focal: >
    The house and the water tower on the horizon, an AREA of about 280 by 150 px right of
    centre, the lightest sustained mass below the sky.
art:
  technique: "TXSCENE at standing eye with TXOBJ house, water_tower, live_oak and fence_post and a hand built mailbox in metres, printed by TXINK as a hatch at cell 7, angle 74."
  why_this_technique: >
    The hatch returns from frames 3 and 7 at a third angle, so the deck's last frame is made of
    the same marks as its middle without repeating either. A low sun gives the road a long rake
    that the opening frame's high sun does not, so frames 1 and 9 are the same road at two hours
    rather than the same drawing twice.
  palette: >
    page #161310 hot mix, ink #E4D8C3 caliche, no granite anywhere and the absence is the point.
    Twin greys, sky #EDEDED, caliche #A8A8A8, hot mix #343434, fog line #D8D8D8, water tower and
    house #7A7A7A, live oak #2E2E2E, fence #3C3C3C, wire #4A4A4A and the mailbox #232323.
  value_structure: >
    The sky is the light, the oak is the dark, the road between them takes the rake. Target
    frame median L* 35.
  motion: >
    Hook, dek, down the road to the horizon, right to the house and the tower, down to the foot.
type:
  hook: "The score still aims the money."
  dek: 'The release names three next steps and dates none of them.'
  labels: ["THE STAKE", "TEXAS TRANSPORTATION COMMISSION", "09 / 09", "c7 c10 c23 c24 c25 c26   TEXAS AI DOCKET", "texasaidocket.com"]
  mono_foot: "Meets September 24th in Austin, open to the public. No agenda is posted for any of the four meetings left this year."
verbatim: []
acceptance:
  - "no string on the frame states or implies that this project is on any agenda, and no drawn room, dais or seat appears anywhere"
  - "every figure in the mono foot comes from computed.json and none is typed, and the one date is month first with the ordinal and carries no year. THE FOOT CARRIES ITS OWN SUBJECT, the commission, so no reader can attach the meeting to this project or to the release"
  - "the frame carries no granite anywhere, measured at zero percent, because no claim here has a person in it"
  - "the water tower is smaller than the house's roof line and sits above it, so the depth reads"
  - "the road is cut by the bottom edge and the fence line by both side edges, and the road surface carries a BROKEN CENTRE LINE rather than a comb of transverse bands, because bands at decreasing spacing toward a vanishing point are the visual grammar of sleepers and the frame read as railroad track"
risks:
  - "a ninth frame thinner than the eighth is a fault four ledger entries in a row have recorded and none has paid. THIS FRAME IS BUILT FIRST and a rebuild is budgeted for it anyway."
  - "all three treatments closed in a public room and all three flagged that a room plus a date delivers a verdict no sentence delivers. The room is cut for that reason and the calendar stays as a foot."
```

## THE FRAME THAT WAS CUT, offered here rather than lost

THE INSTRUMENT's frame 6 drew Texas in Albers as a survey sheet with three published totals for
one network ruled beside it. The university's release puts the highway network at 703,000 lane
miles and cites nothing for it, while the federal HM-60 table gives Texas 707,436 total lane
miles for 2024 and 699,229 for 2023, counting every public road rather than highways alone
(c2, c12, c13). `compute.py` computes that ordering rather than asserting it, and the build
breaks if it flips.

It is the best pure evidence available in the claims file and it belongs to a different deck, one
about where a number came from rather than about who holds the judgement. It is written down here
so the next run can find it, and its own risk is recorded with it: a state outline with one tint
and no counties is the definition of a diagram of a place, and no claim in this run resolves to a
county.
