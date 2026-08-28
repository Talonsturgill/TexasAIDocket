# Storyboard, deck no. 10, August 28th 2026

Story: PUCT Docket 59220, `tx-2026-0108`. Every fact traces to `out/2026-08-28/claims.json`.
Every numeral traces to `out/2026-08-28/compute.py`, which reads that file and refuses a figure
it can't find in a quote.

## The synthesis, and what each room contributed

Three directors ran on three lenses and all three independently chose the Llano Estacado. That
is not a coincidence worth ignoring. The record names exactly one place, Armstrong County, and
after nine consecutive decks of an object or an interior at arm's length, land at distance is
the one register the ledger leaves open.

**The concept comes from the unanswered-question room.** Every obvious drawing of an absence is
spent here, and the reason is that they were all one drawing, a hole. This story is not a
subtraction. The order is complete and in force, the statute is complete, the machine and the
load are both real, and the thing nobody settled sits BETWEEN two fully present things. In a
measured section that is a **contact**, and a contact is drawn with ink rather than with
emptiness. Nothing in this deck is drawn empty.

**The attribution law comes from the place room**, and it is the best single idea any of the
three had. **Caliche and gypsum carry the commission. Ochre carries a party.** A reader is told
who is speaking before they read a word, and the deck's sharpest trap, the applicants' 525.5
figure that the order merely records, is disarmed in the drawing rather than in a footnote.

**The one computed scale comes from the ratio room.** Megawatts reach pixels at one rate,
declared once in `compute.py`, so two frames can be compared by eye and a reader is right to.

**One frame was rebuilt on the fact-checker's finding rather than on any director's pitch.** Two
rooms planned a frame around 265.5 megawatts appearing twice, as the generator and as the first
load. It does not. The commission's finding for that load is 265 megawatts and 265.5 is what
GOODNIT1 generates. Slide 5 is now about exactly that, two figures that look alike and are not
the same thing, which is a truer frame than the one that was planned and is the whole reason
the phase exists.

## The laws this deck is held to

1. **One low sun, one azimuth**, on every frame carrying drawn light. Slides 2 and 5 carry none
   and say so by construction.
2. **The section is craft and never evidence.** No frame names a rock, a formation, an age or a
   landform. Armstrong County is the only place word and it comes from c3.
3. **Nothing is drawn empty.** Every absence here is a contact between two present things.
4. **Caliche and gypsum are the commission. Ochre is a party.** No plate mixes them.
5. **525.5 appears on one frame only**, inside the same visual block as its attribution, never
   set larger than that attribution.
6. **Every figure is JetBrains Mono, tabular.** Fraunces has already shipped a 3 that read as a 5.
7. **No cartography, no county shape, no coordinate.** No claim supports a spatial distribution.
8. **The deck never states what the unanswered question IS.** No claim states it. The motion's
   characterisation is quoted and nothing is added to it.

## Palette, Armstrong County's own section, source per colour

| token | hex | source |
|---|---|---|
| `sky_predawn` | `#1A1C33` | the Panhandle sky before sunrise, cold blue, deliberately not the house Big Bend violet |
| `rim_light` | `#F2D9B4` | first direct sun on a caprock edge, pale rather than gold |
| `caliche_cap` | `#E4DCC6` | the Ogallala caprock hardpan that caps the Llano. **The commission's value** |
| `trujillo` | `#C6A277` | buff Triassic ledge sandstone |
| `tecovas` | `#8C8496` | the lavender-gray mudstone slope. A hue no deck here has carried |
| `ochre` | `#B4903F` | the yellow band in that same slope. **A party's value** |
| `quartermaster` | `#7E3B2E` | the red-brown claystone that floors the section |
| `satin_spar` | `#F5F1E6` | fibrous white gypsum veins cutting the red beds. The deck's light and its type |
| `ledge_shadow` | `#241E22` | the underside of a ledge lip. The deck's true dark |
| `flag_red` | `#BF0A30` | reserved. Spent once, slide 9, as ink on `caliche_cap` |

Declared as plain pairs so the colour check can read them:

    sky_predawn #1A1C33
    rim_light #F2D9B4
    caliche_cap #E4DCC6
    trujillo #C6A277
    tecovas #8C8496
    ochre #B4903F
    quartermaster #7E3B2E
    satin_spar #F5F1E6
    ledge_shadow #241E22
    flag_red #BF0A30

## Camera plan, nine constructions, no class twice

1 long range landscape elevation at standing eye height. 2 three quarter isometric diagram with
no ground plane. 3 level mid range with one course filling the middle band. 4 square and close on
a bedded face with no horizon. 5 dead flat, zero perspective, zero drawn light. 6 square on a
raking lit face. 7 full bleed at reading distance with a translucent overlay. 8 looking up a
slope from the floor. 9 plan view straight down at near zero relief.

Five frames sit on rock, four step onto a drawing surface or a diagram.

---

```yaml
slide: 1
job: >
  The only frame in the deck that is a place, establishing the ground this decision sits on and
  the fact that the commission approved something here, before any quantity is introduced.
claims: [c3, c5, c28]
numerals:
  - value_from: c3
composition:
  structure: >
    The horizon is pushed to the bottom fifth so the sky takes four fifths of the frame, because
    the Llano Estacado's own signature is that the land is a ruled line and the sky is everything
    else, and a reader who recognises that horizon has placed the story before reading a word.
  bands: >
    The top third is unbroken pre-dawn sky graded from `sky_predawn` at the frame edge toward a
    colder value near the horizon, carrying the masthead and nothing else. The middle third is
    more of that graded sky and carries the hook, set high so it sits in air rather than on
    ground. The bottom third carries the whole of the land, which is a lit caprock rim in
    `rim_light` running the horizon, a shadowed plain below it in `quartermaster` with a
    two layer ground texture of low frequency mounds and a high frequency seed head stipple whose
    tips catch the sun and whose bases fall into `ledge_shadow`, and beneath that the dek, the
    source line and the counter.
  focal: >
    The lit caprock rim read as a band of area rather than as an edge, drawn between 32 and 63
    px tall so it survives the reduction to 432 px, which the eye finds because it is the lightest
    thing in the frame and the only place the sun has reached.
art:
  technique: "TX3D heightfield with atmospheric fog, plus TX.fbm2 ground tooth in two layers"
  why_this_technique: >
    The claim is that an enormous decision sits somewhere nothing on the horizon changes, and the
    only construction that says that is one where the machinery is texture and the ground is the
    subject. A heightfield at grazing sun with real distance fog gives aerial perspective that a
    flat wash can't, and it is CPU and deterministic, which the GPU bench is not.
  palette: "sky_predawn, rim_light, quartermaster, ledge_shadow. Armstrong County caprock at dawn"
  value_structure: >
    Lightest is the `rim_light` caprock band along the horizon in the lower fifth, and it is the
    one thing the sun has touched. Darkest is the plain in shadow immediately below it, with the
    sky sitting mid dark above.
  motion: "down the empty sky, arrested by the lit rim, then along it"
type:
  hook: "Approved. The question underneath is still open."
  dek: "Two AI data center complexes will sit behind one wind farm's own meter in Armstrong County."
  labels: ["GOODNIT1", "265.5 MW", "ARMSTRONG COUNTY", "c2", "c3"]
acceptance:
  - "a continuous horizon runs the full 1080 px width with its y between 1060 and 1120, and sky covers 74 percent or more of the frame area"
  - "a `rim_light` band at least 30 px tall runs unbroken across 60 percent or more of the horizon, and its median L* is at least 25 above the land beneath it, so the declared focal is still an area after the reduction to 432 px"
  - 'the hook reads exactly "Approved. The question underneath is still open."'
  - "the ground canvas measures a luminance standard deviation above 6 at 432 px wide, so a dead heightfield fails rather than passing as night"
  - "no turbine, building, mast or structure is drawn anywhere in the frame"
risks:
  - "a heightfield at grazing incidence can come back near uniform and read as a plausible night, which the standard deviation item is written to catch"
  - "the sky can grade into a warm value near the horizon and read as the house Big Bend dusk, which is the register this deck is not"
```

```yaml
slide: 2
job: >
  Show the physical arrangement the whole docket is about, one generator and two loads meeting
  at a single point of interconnection, as the engineering diagram it actually is.
claims: [c4, c5, c6, c7, c28]
numerals:
  - value_from: c5
  - value_from: c3
composition:
  structure: >
    Three labelled bodies hang on one node with a single line leaving it, laid out as a single
    line diagram because a point of interconnection is a diagrammatic object and drawing it as a
    landscape would invent a site the record never describes.
  bands: >
    The top third carries the hook and the eyebrow naming the order. The middle third carries the
    diagram itself, the node and the three bodies with their megawatt labels. The bottom third
    carries the quoted finding from c7 on a `satin_spar` rule, the commission's reason for
    weighing both loads together, over a low field of `tecovas` stipple tooth that gives the band
    a modeled ground rather than a flat one, plus the source line and the counter.
  focal: >
    The node, drawn as a two value disc 80 px across in `rim_light` over `#B98F52`, which the eye
    finds because it is the only warm and the only modelled thing on a cold flat field. It takes a
    commission value rather than ochre, because the point of interconnection is the commission's
    own finding and law 4 reserves ochre for a party.
art:
  technique: "a single line diagram authored directly in SVG with real stroke weight, no ground plane and no cast"
  why_this_technique: >
    Every other frame in the deck is a lit surface, and this claim is not a surface. It is a
    topology. A diagram drawn with genuine stroke weight is the one construction that states the
    arrangement without asserting a building, a fence or a site plan that no filing describes.
  palette: "sky_predawn field, satin_spar strokes, ochre node, caliche_cap on the commission's quote"
  value_structure: >
    Lightest is the `satin_spar` stroke set of the diagram itself in the middle band. Darkest is
    the `sky_predawn` field it hangs on, which is unbroken and carries no gradient.
  motion: "left along the line into the node, then out to the two loads"
type:
  hook: "A 260 MW load behind one interconnection."
  dek: "\"the Crusoe One and Crusoe Two loads will be co-located with GOODNIT1 and interconnected at the GOODNIT1 point of interconnection\""
  labels: ["GOODNIT1", "265.5 MW", "Crusoe One Load", "265 MW", "Crusoe Two Load", "260 MW", "c4", "c5", "c6", "c7"]
acceptance:
  - "exactly three labelled bodies are drawn plus the shared settlement meter tapped off the generator leg and cited to c28, and three lines meet at the node, one to the generator and one to each load"
  - 'the hook reads exactly "A 260 MW load behind one interconnection." and the eyebrow reads "PUCT DOCKET 59220, ORDER"'
  - "the literal strings \"GOODNIT1\", \"Crusoe One Load\" and \"Crusoe Two Load\" all appear, each within 40 px of its own body"
  - '"265.5 MW", "265 MW" and "260 MW" are each set in JetBrains Mono with tabular numerals, including the "260 MW" inside the hook, and none appears in Fraunces'
  - "the frame carries zero cast shadows and zero gradients, and every stroke measures 4.5 to 1 or better against the field"
  - "the node is an 80 px disc drawn in two values, `#F2D9B4` over `#B98F52`, and is the only warm element on the frame"
risks:
  - "a single line diagram can read as a corporate slide, which the stroke weight and the cold field are the defence against"
  - "three bodies and three figures in one band is the frame most likely to collide two line boxes"
```

```yaml
slide: 3
job: >
  State the condition itself in the commission's own words, as a thing in force that everything
  underneath it sits under.
claims: [c2, c8]
numerals: []
composition:
  structure: >
    One lit ledge course runs off both frame edges so it reads as continuing past the picture,
    because a condition in force is not an object with ends, and the shadow its lip throws is the
    reach of that condition made physical.
  bands: >
    The top third is cold sky above the course, holding the hook. The middle third is the ledge
    itself, its lit top face and its bedded front, with the quoted condition ruled onto the face.
    The bottom third is the shadow the lip throws, a graded mass falling from the underside into
    `ledge_shadow` with the talus tooth of broken ledge stone catching light at its upper edge,
    and along its foot the order's name, the claim ids and the counter.
  focal: >
    The lit top face of the ledge, read as a band of area, which the eye finds because it is the
    lightest surface in the frame and the only one the sun meets square.
art:
  technique: "TX.reliefShade over a computed ledge profile, with the lip's cast solved from the deck's one sun"
  why_this_technique: >
    A ledge is the only form in a section that carries load, and this claim is about a duty that
    everything below it now carries. Relief shading gives the course a real top and a real
    underside, so the shadow is subtracted from a lit ground rather than painted onto a dark one.
  palette: "trujillo ledge, rim_light on its top face, ledge_shadow beneath the lip, sky_predawn above"
  value_structure: >
    Lightest is the ledge's top face across the middle band. Darkest is the shadow immediately
    under the lip, which is the deck's first true dark and is where the light dies.
  motion: "across the lit face left to right, then down into the shadow it throws"
type:
  hook: "The condition is the whole load."
  dek: "\"Crusoe and Ensign must ensure that the Crusoe Two Load fully curtails its consumption in the manner directed by ERCOT\""
  labels: ["ERCOT, the grid operator the order names", "c2", "c8"]
acceptance:
  - "a single lit ledge spans the full 1080 px width with a top face 30 px or taller, and the shadow beneath its lip measures 12 L* or more darker than that face"
  - "the literal string \"fully curtails its consumption in the manner directed by ERCOT\" appears in full inside a ruled band with \"c8\" beneath it"
  - "the ledge's top face is the lightest area in the frame excluding sky"
  - 'the frame carries the string "ERCOT, the grid operator the order names" and the eyebrow reads "CONDITION 1"'
  - "the quoted condition sits on a solid opaque knockout plate, not a partial opacity, set in `satin_spar` which law 4 makes a commission value, and no bedding line crosses a glyph"
risks:
  - "the shadow can be painted on a ground that is already near black, which reads as nothing, so the ground under the lip is lit first"
  - "a full width course with type on it is the frame most likely to trip the art crossing glyphs gate"
```

```yaml
slide: 4
job: >
  Give the three time figures the order attaches to the condition, and keep the one that is
  hedged visibly hedged.
claims: [c9, c10]
numerals:
  - value_from: c9
  - value_from: c10
  - computed_by: "out/2026-08-28/compute.py, vein widths from ratio_elected_to_window and ratio_window_to_notice"
composition:
  structure: >
    Three veins cut across the bedding at an angle rather than lying in it, because these three
    figures were attached to the arrangement rather than being part of it, and a vein is the one
    form in a section that crosses what it is set into.
  bands: >
    The top third carries the hook and the uppermost vein, which is the sixty minute notice. The
    middle third carries the thirty minute vein, the widest and the most lit, and the quoted
    condition beside it. The bottom third carries the ten minute vein at its narrowest, running
    down into the bedded face's own lower courses where the stipple tooth coarsens and the
    parting walls throw their own small shadows, with the claim ids and the counter along the foot.
  focal: >
    The thirty minute vein's lit fibre body in the middle band, an area, which the eye finds
    because it is the widest bright mass on a face that is otherwise mid dark.
art:
  technique: "fibrous gypsum vein set drawn as filled bodies with a lit fibre body and a dark parting wall, over a relit bedded face"
  why_this_technique: >
    A time scale has shipped twice in fourteen days and a graduated rail shipped yesterday, so
    the calendar constructions are spent. A vein set carries three magnitudes as three widths at
    one computed rate without becoming a chart, and it keeps the deck inside its own section.
  palette: "satin_spar veins, tecovas bedded face, ochre on the hedged vein, ledge_shadow parting walls"
  value_structure: >
    Lightest is the thirty minute vein's fibre body in the middle band. Darkest is the parting
    wall on the down sun side of each vein, which is what makes a vein a body rather than a line.
  motion: "across the face along the veins, from the widest down to the narrowest"
type:
  hook: "Thirty minutes, or ten if they say so."
  dek: "\"Crusoe or Ensign may reduce the required time period from 30 minutes to 10 minutes by providing written confirmation to ERCOT of the Crusoe Two Load's capability to curtail within 10 minutes.\""
  labels: ["When practicable", "60 minutes", "30 minutes", "10 minutes", "c9", "c10"]
acceptance:
  - 'exactly three vein bodies cross the face, each with a lit fibre body and a darker parting wall on one side, and each carries exactly one of the strings "60 minutes", "30 minutes", "10 minutes"'
  - "the three vein widths stand in the ratios compute.py emits from 10, 30 and 60, within 2 px each, and no width is typed into the frame"
  - "the words \"When practicable\" appear on the sixty minute vein, which is drawn as a BROKEN vein rather than in a party colour rather than `satin_spar` because the order hedges it"
  - "the frame nowhere states that ten minutes is required, and the word \"may\" from c9 appears"
  - "each figure sits on a fully opaque knockout of its own vein and no bedding line crosses a glyph"
risks:
  - "three veins and three labels in one face is a collision risk, so each label is knocked out of its own vein rather than floated beside it"
  - "reading the hedged vein as simply a fourth colour rather than as a hedge, which the `When practicable` string on the vein itself defends"
```

```yaml
slide: 5
job: >
  Set the three findings side by side so a reader sees that two of them look alike and measure
  different things, which is the mistake this docket's own record invites a reader to make.
claims: [c3, c5]
numerals:
  - value_from: c3
  - value_from: c5
composition:
  structure: >
    Three quoted fragments sit in two columns with all three figures locked to one computed
    column position, because the argument here is made by tabular alignment rather than by
    drawing, and a reader compares the digits by eye without having to count them.
  bands: >
    The top third carries the hook and the eyebrow naming the order as the source of all three.
    The middle third carries the three aligned rows, each a figure in mono beside the thing it
    measures. The bottom third carries a fine even `tecovas` tooth running the full width as the
    frame's only texture, a stipple laid at one density so it reads as a ground and not as a
    wash, with the two claim ids, the source line and the counter set into it.
  focal: >
    The figure column in the middle band, read as a single tall block of area, which the eye
    finds because it is the only high contrast mass on an otherwise even field.
art:
  technique: "flat type on a tecovas field with zero drawn light and zero depth, one computed alignment column"
  why_this_technique: >
    This is pure reading and the point is a half megawatt difference between two figures that a
    reader will otherwise assume are one figure. Any modelling at all would give the eye
    somewhere else to go. The deck's flattest frame is what makes slides 3 and 7 read as lit.
  palette: "tecovas field, satin_spar type, caliche_cap on the two commission findings"
  value_structure: >
    Lightest is the `satin_spar` figure column in the middle band, set as three rows reading as
    one mass. Darkest is the `tecovas` field it sits on, which carries no gradient anywhere.
  motion: "straight down the figure column"
type:
  hook: "Alike is not the same."
  dek: "\"Goodnight owns and operates GOODNIT1, a stand-alone 265.5-MW wind generation resource in Armstrong County.\""
  labels: ["265.5 MW  GOODNIT1's own rating", "265 MW  the first data center", "260 MW  the second data center", "c3", "c5"]
acceptance:
  - "the three figures \"265.5\", \"265\" and \"260\" are left aligned within 2 px of one another on a column x emitted by compute.py"
  - "each figure carries on its own row the words naming what it measures, and no row carries a figure without them"
  - "the frame's ground measures a luminance range under 8 L* excluding type, so no gradient, no cast and no specular appears anywhere"
  - "both claim ids \"c3\" and \"c5\" appear and both quoted fragments are verbatim"
  - 'the strap reads exactly "ALL THREE FROM THE COMMISSION''S OWN FINDINGS" and the three row labels read "GOODNIT1''s own rating", "the first data center" and "the second data center"'
risks:
  - "a flat frame can read as unfinished, which the even tooth across the bottom band is there to prevent"
  - "a reader can take the three rows as a total, which is why no row is summed and no rule runs under them"
```

```yaml
slide: 6
job: >
  Carry the deck's one contested figure and make its attribution structural rather than a
  footnote, so a reader at feed size can't take the applicants' arithmetic for the commission's.
claims: [c12, c3, c5]
numerals:
  - value_from: c12
  - value_from: c3
  - computed_by: "out/2026-08-28/compute.py, px_per_mw and contended_px"
composition:
  structure: >
    One magnitude is plotted against a labelled reference on an untruncated axis that includes a drawn and
    labelled zero, because the claim is a comparison rather than a change, which is how the order itself sets them, and the eye reads a change
    as an angle before it reads either endpoint.
  bands: >
    The top third carries the hook and, in the same block, the attribution strap naming the
    applicants, set no smaller than the figure's own caption. The middle third carries the two
    plotted states as filled seated blocks with the slope between them and a full width hairline
    at the resource's nameplate. The bottom third carries the drawn zero, the axis foot with its
    ticks, the megawatt per pixel rate printed as a scale bar, and a raking `trujillo` face
    beneath it whose lit grain runs out of the frame, with the claim ids and the counter on it.
  focal: >
    The pair of filled seated blocks in the middle band, read as one mass, which the eye finds
    because they are the only filled areas on a face that is otherwise line work.
art:
  technique: "slope chart, untruncated, with a drawn zero, mounted on a raking lit sandstone face"
  why_this_technique: >
    The bar pair shipped six days ago and the residual bar at true ratio is spent. A slope is
    neither, and it is the honest figure for a claim about how an obligation changed rather than
    how big it is. Mounting it on a lit face keeps the frame inside the deck's own section.
  palette: "trujillo face, ochre on the applicants' plotted state, caliche_cap on the nameplate hairline"
  value_structure: >
    Lightest is the raking sandstone face across the middle and lower bands where the sun crosses
    the grain. Darkest is the recess the seated blocks sit in, which is what gives them an edge.
  motion: "up the slope from the first state to the second, then down to the labelled zero"
type:
  hook: "The applicants did the arithmetic."
  dek: "\"it would result in a total curtailment of 525.5 MW\""
  labels: ["THE APPLICANTS' FIGURE, AS THE ORDER RECORDS IT", "265.5 MW  GOODNIT1 nameplate", "525.5 MW", "c12", "c3", "c5"]
acceptance:
  - "the attribution outranks the figure by every measure a reader uses. THE APPLICANTS' FIGURE, AS THE ORDER RECORDS IT is set at 34 px on a full width saturated ochre strap ABOVE the chart, and 525.5 is set at 32 px, so the numeral is never the larger of the two. The earlier form of this item demanded the two sit within 60 px and the render had them 157 apart, which is the plan describing a frame that was not built"
  - "525.5 is set in `#B4903F` and no `caliche_cap` value appears inside its block"
  - "the value axis includes zero, zero is drawn and carries a label, and no axis is truncated"
  - "both plotted values sit at y positions computed by compute.py at the deck's single px_per_mw rate, and that rate appears on the frame as a scale bar"
  - "the nameplate hairline is drawn in `caliche_cap` and is visually distinct in construction from the two plotted areas, which are filled blocks of 40 by 40 px or more"
  - 'the frame carries the strings "0 MW", "100 MW" and "265.5 MW  GOODNIT1 nameplate", and the hook reads exactly "The applicants did the arithmetic."'
risks:
  - "a reader at 432 px reads the headline figure and never reaches the attribution, which putting the attribution in the hook block at 32 px is the whole defence against"
  - "a slope chart on a lit face can read as a chart pasted over scenery, which the shared sun and the recessed blocks are meant to prevent"
```

```yaml
slide: 7
job: >
  The turn, and the deck's one image. Show the thing nobody settled as a contact between two
  fully decided bodies rather than as a hole in either of them.
claims: [c18, c19, c17]
numerals: []
composition:
  structure: >
    Two complete rock courses meet along one irregular line a little above centre and run edge to
    edge, with a sheet of drafting film laid over the lower course only, because the order is
    complete and the statute is complete and the unsettled thing lives in the join between them.
  bands: >
    The top third is the upper course, buff sandstone lit from one side with every bed and every
    fracture drawn, carrying the eyebrow that names the motion. The middle third is the contact
    itself and the hook set beside it. The bottom third is the lower course in `quartermaster`
    under the same raking light, its bedding and its grain drawn in full with the shadow of each
    parting lying along it, read through the drafting film at partial transmittance so that lit
    texture stays legible, with the film's straight ruled top edge crossing it and the drafter's
    hachured contact mark ruled in graphite ON the film. BELOW the film, and not on it, a matte
    writing panel carries the motion's quoted words, the claim ids and the counter. Two judges
    read that opaque panel as the film itself and reported the film as opaque; the film is
    measured at 66 percent transmittance and the rock's texture reads through it at full
    retention, so what was wrong was this dossier saying the words sit on the film.
  focal: >
    The contact itself read as a band of area rather than as a line, thickened by the lit lip on
    its upper side and the shaded lip on its lower one, which the eye finds because it is the one
    thing in the frame belonging to neither material.
art:
  technique: "two relit courses meeting on a computed irregular contact, with a translucent drafting film over the lower course"
  why_this_technique: >
    Every obvious drawing of an absence is spent here and every one of them was a hole. This
    claim is not a hole. Both sides are decided and complete, and a contact is the only figure
    that says settled and unsettled at once. Translucency is a material this project has never
    used, which is also why the frame can't read as a repeat.
  palette: "trujillo upper course, quartermaster lower course, satin_spar film and graphite type, rim_light on the contact's upper lip"
  value_structure: >
    Lightest is the drafting film across the lower half, which makes this the deck's brightest
    frame and its one inversion. Darkest is the shaded lip immediately below the contact.
  motion: "along the contact edge to edge, then down through the film to the writing panel below it"
type:
  hook: "Decided above. Decided below. Not between."
  dek: "\"Nor did the Order directly address the critical legal and policy issue of first impression that underlies this case\""
  labels: ["MOTION FOR REHEARING, DOCKET 59220", "\"the Order is excessive, arbitrary and capricious, unsupported by the evidentiary record, and not authorized by the language of PURA.\"", "c17", "c18", "c19"]
acceptance:
  - "one continuous contact runs from the left frame edge to the right with no break, and neither course contains any region larger than 60 by 60 px that is flat within 2 L*"
  - "the film covers the lower course only, its top edge visible as a straight ruled line, with the rock legible through it at a measured transmittance between 55 and 75 percent. Measured on the render, the texture standard deviation under the film is 13.1 against 10.6 on the bare course above it, so the rock reads through at full retention"
  - "the graphite hachured contact mark is ruled ON the film and is a drafter's mark rather than a section symbol, and the motion's words sit on the matte writing panel BELOW the film, never on the film itself"
  - "the literal string \"the critical legal and policy issue of first impression that underlies this case\" appears in full with \"c18\" beneath it"
  - 'the eyebrow reads "MOTION FOR REHEARING, DOCKET 59220" and sits in the same block as the hook'
  - "this is the deck's inversion, its median lightness at least 15 above BOTH its neighbours, slides 6 and 8. It is not the deck's lightest frame and was never going to be, because the reserved red on slide 9 only clears contrast as ink on caliche and that fixes slide 9 as the pale one"
  - "no string anywhere on this frame states what the unanswered issue is, because no claim states it"
risks:
  - "a reader who does not know what a contact is reads it as decoration, which is why no copy depends on the geology"
  - "three lit rock faces on slides 3, 4 and 7 is the closest pair bespoke_check will find, and it has to be measured before scoring rather than after"
```

```yaml
slide: 8
job: >
  The counter image. Show the commission's own edge, the things it declined to take into the
  case, and refuse to depict a thing that does not exist.
claims: [c13, c15]
numerals: []
composition:
  structure: >
    The camera looks back up the slope for the only time in the deck, so what is above the reader
    is what was considered, and nothing is drawn above the rim but sky, which is how the frame
    refuses to depict a resource nobody has built.
  bands: >
    The top third is `sky_predawn` above a rim silhouette that crosses the full width, carrying
    the hook. The middle third is the upper slope with its bedding traces thinning as they climb,
    and the first quoted refusal set on a `caliche_cap` plate. The bottom third is the near slope
    in `quartermaster` under shadow, its bedding traces at their densest with real talus tooth
    and cast pebble shadows in the foreground, carrying the second quoted refusal, the claim ids
    and the counter.
  focal: >
    The rim crest drawn as a band about 40 px deep running the full width, cool because the sky
    is the only thing lighting it, which the eye finds because it is the boundary between the
    frame's only light and all of its dark.
art:
  technique: "bedding trace contour set on a slope seen from below, thinning monotonically toward the rim"
  why_this_technique: >
    A refusal to weigh a thing that does not exist can't be drawn as a blank, because a blank is
    the drawing this deck has forbidden itself. Traces that thin as they climb and then simply
    stop at a rim say the same thing with ink, and the sky above the rim is genuinely empty
    because nothing has been built there.
  palette: "quartermaster near slope, tecovas upper slope, caliche_cap quote plates, sky_predawn above the rim"
  value_structure: >
    Lightest is the sky above the rim silhouette, which is the frame's only light and the whole
    reason the rim reads. Darkest is the near slope in the bottom band, the deck's deepest value.
  motion: "up the slope along the thinning traces to the rim, then stopping"
type:
  hook: "What the order left out."
  dek: "\"GOODNIT2 does not yet exist, is not a part of the application, and should not be considered in this proceeding.\""
  labels: ["commission staff and ERCOT, answering as parties", "\"The Commission denies all other motions and any other requests for general or specific relief, if not expressly granted.\"", "c13", "c15"]
acceptance:
  - "at least nine nested bedding traces are drawn and their spacing thins monotonically from the bottom of the frame to the rim"
  - "the rim crest is drawn as a band about 40 px deep across the full 1080 px width, in a COOL value because the sky is its only light, and no form, mass or plane is drawn above it other than sky"
  - "the literal string \"GOODNIT2 does not yet exist, is not a part of the application, and should not be considered in this proceeding.\" appears in full with \"c13\" beneath it"
  - 'the words "commission staff and ERCOT" appear within 60 px of that quote, the plate carrying it is `#B4903F` because a party said it, and the commission''s own ordering paragraph beneath it sits on `#E4DCC6`'
  - 'the hook reads exactly "What the order left out." and the second quote is attributed to "PUCT DOCKET 59220, ORDER, ORDERING PARAGRAPH 6"'
risks:
  - "a contour set can moire at the 432 px thumb, so no two traces sit closer than 9 px at 2160"
  - "attributing the GOODNIT2 sentence to the commission is the exact error a second reading of the order caught this run, and the attribution label is the only thing preventing it"
```

```yaml
slide: 9
job: >
  Close on the surface the deck opened on, hand the reader the docket number and the one dated
  door the record actually holds, and scope that door honestly to the calendar it came off.
claims: [c22, c24, c26, c27]
numerals:
  - value_from: c24
  - computed_by: "out/2026-08-28/compute.py, comment_date rendered month first with the ordinal"
composition:
  structure: >
    The camera looks straight down at the hardpan at near zero relief, so the reader who spent
    seven frames descending through a section is standing back on the ground they opened on, and
    the one grazing key across it is the deck's only direct light on a flat surface.
  bands: >
    The top third is open caliche hardpan under the grazing key, with the hook set on it. The
    middle third carries the dated door, a `caliche_cap` plate with the deadline in `flag_red`,
    the docket number beneath it and the scoping sentence beneath that. The bottom third carries
    the two remaining quotes on the hardpan itself, where the stipple tooth coarsens away from
    the key and the small stones throw their own cast shadows across the pan, with the colophon,
    the site line and the counter set into that texture.
  focal: >
    The dated plate in the middle band, an area carrying both the frame's lightest ground and the
    deck's one reserved colour, which the eye finds because nothing else on nine frames is red.
art:
  technique: "stipple field as caliche hardpan tooth under one grazing key, plan view, with knockout labels"
  why_this_technique: >
    The reserved red only clears contrast as ink on the deck's one pale ground, so the pale ground
    has to be the closing frame. Plan view at near zero relief is also the one camera class the
    deck has not spent, and standing back on the surface is the shape the argument wants.
  palette: "caliche_cap hardpan, satin_spar type, flag_red on the date, quartermaster in the tooth"
  value_structure: >
    Lightest is the hardpan where the grazing key crosses it, which carries the dated plate.
    Darkest is the cast shadow of the small stones in the tooth away from the key.
  motion: "across the pan with the key, arrested by the red"
type:
  hook: "The open door is in another proceeding."
  dek: "\"Ensign respectfully asks the Commission to grant rehearing and amend its Order to find that no conditions are necessary on Crusoe Two.\""
  labels: ["PUCT PROJECT 59550, A SEPARATE PROCEEDING", "COMMENTS DUE  c24", "September 17th, 2026", "QUINQUENNIAL REVIEW OF SYSTEM-WIDE OFFER CAP PROGRAM", "DOCKET 59220", "Motion for rehearing filed August 18th, 2026", "texasaidocket.com", "c22", "c24", "c26", "c27"]
acceptance:
  - "\"September 17th, 2026\" is the only text in the whole deck set in `#BF0A30`, and it measures 4.5 to 1 or better at its worst point against `caliche_cap`"
  - 'the frame NAMES the proceeding the deadline belongs to, reading "PUCT PROJECT 59550, A SEPARATE PROCEEDING" directly above the date. It never says the calendar entry names no docket, because the feed this run fetched shows that entry reading "Project 59550"'
  - "no string on this frame joins the September date to docket 59220"
  - "the caliche ground measures a luminance standard deviation of 4 or more at 432 px with a left to right L* falloff of 10 or more from the grazing key"
  - "the site line renders exactly \"texasaidocket.com\""
  - "the date appears ONCE and in ONE spelling. The frame carried it at 74px and then the order's own sentence naming the same day sixty pixels under it, in a different spelling, on the deck's only call to action. The label COMMENTS DUE now names what the date is without spending it again"
  - "the site line is legible where it sits, measuring at least 100 L of separation between its ink and the ground beside it, since a plan view carries no scrim and a desiccation crack ran through it"
  - 'the frame carries the strings "PUCT PROJECT 59550, A SEPARATE PROCEEDING", "DOCKET 59220" and "texasaidocket.com", the hook reads exactly "The open door is in another proceeding.", and no string on the frame names a calendar, since no claim carries one'
risks:
  - "a caption that drops the scoping sentence recreates a printed join no code produced, which is a defect this deck has shipped once before"
  - "a plan view of a flat pan can render near uniform, which the standard deviation and falloff items are written to catch"
```

## The frame to cut if the deck goes to eight

Slide 3. Its claim rides comfortably as the first vein's clause on slide 4, so the content loss
is close to nothing, and it is the deck's third lit rock face, which makes it the likeliest half
of the closest pair `bespoke_check` will find. Slide 6 is never the cut, because 525.5 is the
most interesting figure in the record and slide 6 is the frame built to attribute it correctly.
