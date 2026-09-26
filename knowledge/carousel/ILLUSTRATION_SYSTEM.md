# The illustration system — how a frame gets an IMAGE

Written 2026-09-11, the upgrade session after carousel no. 21, on the owner's instruction that
the artwork was "very mediocre" and had to be a different order of thing by the next run. This
file is the whole of that answer in one place: the diagnosis, the law, the ten layouts, THE
RENDER, the libraries, the order of work, and the gates.
**Read it before the directors room. Read it again before the art build.** The example that
shows it working is `examples/figure-bearing/`, solid shaded forms drawing a computed figure,
the owner's own worked example, and its contact sheet is what a director looks at before pitching.

> **THE PRINT SCREEN IS DELETED (owner, 2026-09-23).** *"delete that fallback bullshit look, make
> it impossible for me to have to tell u this again."* `assets/js/txink.js` and
> `examples/editorial-deck/` are gone, `scripts/carousel/print_ban.py` fails the build if either
> returns, and every frame is RENDERED. Read THE RENDER below. Anything in this file that still
> describes a screen, a paper stock or a print is history and is marked as such.

## The diagnosis, so the cure is not mistaken for taste

Twenty one decks shipped and three judges found the same thing under all of them in different
words. "Assembled, not drawn." "An object in a void." "A diagram of a place." "Two planes and two
books." "Clip art." "The same page nine times." Every one of those decks passed every gate,
because every gate asks whether what is on the frame is RIGHT and none asked whether there was an
image on it at all.

The cause was structural, four ways at once, and none of them was a lapse of taste:

1. **Nothing had a size.** Every frame was drawn in screen pixels with no camera. A bus was a
   slab because a slab is what you draw when you do not know how tall a bus is, and nothing
   stood on anything or cast a shadow onto anything.
2. **One skeleton.** Kicker top, headline under it, a small drawing under that, source line at
   the bottom. Where the image went and how much of the page it took was never decided per
   frame, so it was the same on all nine.
3. **Surfaces instead of subjects.** The technique library is atmospheres, fields, plates and
   grades. Those are what a frame is made OF. None of them is what a frame is a picture OF, and
   a run reaching for a technique reached for a surface.
4. **Nobody in the picture.** A deck about a school, a hearing room, a grid crew or a ward drew
   the room and nobody in it. A figure gives every object beside it a size, gives the reader
   somewhere to stand, and turns a statistic into a count of people.

So the cure is not a nicer gradient. It is a camera, a subject RENDERED at true scale with a real
material and a real light, a decision per frame about where the image goes, and a gate. (This
sentence said "a print register that says a hand made it" until 2026-09-23. The print register
became the faded look the owner rejected, and it is deleted.)

## THE DECK IS THE UNIT (2026-09-16, owner, and it outranks every rule below it)

    "the artwork for the carousel post is just like, it's not good enough. it doesn't really
     flow together. all the slides don't really flow together. the artwork kind of just seems
     like it's like thrown on the page. I want each page to really seem like custom artwork,
     not just like somebody went and like threw some text boxes on a page."

Everything under the headings below this one was written on 2026-09-11 to fix a FRAME, and it
worked on its own terms. Twenty six decks now carry a real drawn subject on every frame. This
section is about the DECK, and where the two disagree the deck wins, because a reader swipes a
deck and never once sees a frame on its own.

### What was measured, so the cure is not mistaken for taste

Four facts, all read off shipped artifacts in both products rather than argued:

1. **The grade was never called.** `assets/js/txpost.js` is a complete film grade, ported,
   working and documented, and it was loaded by **1 shipped slide out of 205**. The sibling
   product loads its own copy on **127 of 127**. `txcolor.js`, the OKLCH ramp builder, ran 1 of
   205 against 118 of 127. The pass that separates drawn shapes from a graded still sat in this
   repo the whole time, uncalled. That alone is most of the flat look.
2. **There was no deck.** Every frame reached into a permanent bin of finished parts
   (`txobjects`, `txfig`) and placed them. That gives a deck uniform PARTS and no unity of
   WORLD, which is exactly what "assembled, not drawn" means and why `txobjects.js` did not cure
   it. The sibling writes a NEW chassis per run, named for that deck's world, and all nine
   frames draw from it. This product had written **zero** in twenty six decks.
3. **The frames did not agree about the light.** Nothing required them to, so they did not.
4. **The deck strobed.** Each frame's median L*, in slide order, on 2026-09-16:
   77.8, 77.4, 32.5, 36.1, 54.9, 34.4, 77.4, 44.3, 17.9. Frame 6 to frame 7 is a 43 point jump
   back to near white, and there are four such cuts. Across nineteen decks the median adjacent
   jump was **21.0 L*** against the sibling's **2.6**, and **ninety percent of sibling decks
   carry at most one hard cut while not one deck here did.**

**The scorer was reading the last one backwards.** On 2026-09-16 the craft judge wrote "a
genuine value arc (measured 77.8, 77.5, ...; spread 64.8)" and gave the deck CREDIT for it. A
spread is a property of a set. A deck is a sequence. Nothing measured adjacency, so the rubric
rewarded the amplitude of the strobe. `scripts/carousel/deck_coherence.py` measures it now and
`config/carousel/deck_coherence.json` carries the derivation of every threshold.

### THE CHASSIS LAW

**Every run writes ONE module at `assets/js/deck/<date>-<world>.js`, named for that deck's world, and
every one of the nine frames loads it.** It holds three things and nothing else:

- **one light**, as an azimuth and an elevation, so every cast in the deck runs the same way
- **one material vocabulary**, the ramp and the primitives that deck's world is made of
- **one way of seating type**, which is a reserve and never a plate

`assets/js/txdeck.js` is the base every chassis is built on and `TXDECK.declare` is how the
chassis states the deck. There is exactly ONE declaration per deck, in that one file, so nine
frames **cannot** hold nine lights. Coherence here is structural rather than checked, which is
the difference between a rule and a property.

**What a chassis is not.** There is no `drawFrame()` in it and there never will be. A shared
projection helper is house furniture. A shared draw-the-whole-slide is a template, which is the
defect `bespoke_check.py` was written for, and `deck_chassis.py` refuses one by name. **The
chassis hands a frame primitives. The frame decides what to build from them.** Every frame's
composition is still written per frame, which is the whole strength of this machine.

The run owns `assets/js/deck/**` and nothing else under `assets/`. It may build a world. It may
not edit the workshop.

### ONE LIGHT, ONE MATERIAL, ONE GRADE, AND NO SCREEN

Declared once in the chassis, for all nine frames. Not one per frame, which is what the old
wording under THE PRIMARY IMAGE LAW said and what produced nine unrelated pictures.

**`TXDECK.finish(cx)` is the last thing that touches the art canvas on every frame, without
exception.** One line, no arguments to invent, the deck's own grade. A frame may move exactly
two knobs, bloom and aberration, and nothing else. DOM type sits above the canvas and is never
graded, so the grade can be strong without costing a single point of legibility.

### THE CONTINUITY MANDATE, and it replaces the old variety mandate

The old rule said the deck must turn the page: nine different layouts, a different look each
time, at least five distinct archetypes, never the same one twice running. **That rule is why
the deck does not flow together, and the machine was obeying it correctly.** It was told the
wrong thing.

**Choose at least TWO of these per deck and name them in the storyboard:**

- **Panorama spine.** The nine grounds are one continuous canvas 9 x 1080 wide, the camera
  translating x += 1080 per frame, so each swipe REVEALS rather than cuts. Only art crosses a
  cut line and type never sits on one.
- **Edge tease.** Something interesting is cut by the right edge of frame n and completes on
  n+1: a ridge, a route, a cable, a chart line, half a glyph.
- **Motif evolution.** One object or system recurs on every frame and CHANGES STATE with the
  argument. A gauge fills, a shadow lengthens, a queue grows, a light comes on. It doubles as
  the progress indicator.
- **Camera move.** The same world from evolving positions: wide establish, then detail, then
  overhead. Two frames may share an archetype for exactly this reason and the rotation now
  allows it.
- **Value and palette arc.** The ground shifts across the deck with the story, monotonically,
  in steps the reader feels rather than sees. Dusk to night, never night to noon to night.

The 2026-09-16 deck already did one of these by accident and its judge noticed: frame 6 "lands
hard because it is the identical camera to frame 3 with the light inverted". That is a camera
move, it was the best thing in the deck, and the rotation rule was pulling against it the whole
time.

**The rotation, rebalanced.** At most **two** of the same archetype in a row (two is a beat, a
before and an after, the same camera with the light moved; three is a rut). At least **three**
distinct over nine. TYPE_AS_OBJECT at most once. **The image law did not move**, because the
defect the old table was written for was never "too few layouts", it was "no image": at least
thirty percent of the frame, at least four frames bleeding an edge, at least two the reader is
inside. A deck of nine FULL_BLEED frames with a real image on each and a spine running through
them is excellent. A deck of nine different layouts with a headline over a small object is what
the judges called clip art.

### NO PLATE, EVER

Six frames of nine on 2026-09-16 put an opaque rectangle behind the headline, and the source
comment beside one of them reads *"the plate is the critic's own fix for the placeholder-bar
reading"*. A critic said the type sat badly and the repair was more plate. **A plate is what a
frame reaches for when the art under it was drawn without knowing where the type goes.**

So the art is told where the type goes BEFORE it draws:

```js
await document.fonts.ready;
TX.fitText(hook, { min: 82, max: 120, maxLines: 3 });   // fit FIRST, then measure
var boxes = TXDECK.lineBoxes('.hook, .dek, .kick', 16);
var mask  = TXDECK.reserveMask(boxes, 28);               // fn(x,y) -> 0..1
```

Every field, grain, hatch, stipple and scatter pass multiplies its density by `mask(x, y)`, and
a layer that can't consult a mask as it goes gets `TXDECK.punch` afterwards. The type then sits
in quiet the picture actually has. `deck_chassis.py` fails the build on any fill over 0.55 alpha
behind display type.

A wash under 0.55 is atmosphere and is allowed. The distinction is measured, not argued.

### WHAT THE FIRST CHASSIS DECK COST TO BUILD, and every line here was paid for

`examples/lamp-deck/` is the reference build, nine frames of the 2026-09-16 story rebuilt in
this system with the same claims and the same copy. It went from 34 machine QA failures to 0.
These are the things that cost rounds, so the next deck does not pay for them again.

**A hole punched in a light layer is a plate with the sign flipped.** The reserve was punched
out of the lamp's pool at full strength, and it put a visible dark rounded rect behind the site
line and the footnote. This file's own paragraph above had already called that "a plate drawn in
the negative" and the code did it anyway. Light DIMS toward type. It is not removed from around
it. Soft and partial, and a wide feather.

**A frame has two kinds of type and they want OPPOSITE things from the light.** Light on dark
(the headline, the dek, the furniture) needs the light dimmed toward it or the wash destroys the
contrast. Dark on light (type printed ON a drawn document) NEEDS the light, and punching the
pool away from it put a dark blob behind the footnote and took its contrast DOWN. One reserve
list for both is wrong twice. Keep two, and reserve BOTH from drawn edges, because a rule
through a glyph is a strike whichever way the values run.

**A MID GROUND IS THE WORST GROUND, and no choice of ink fixes it.** Measured off the renders,
the band behind the furniture on three frames sat at Y 0.086 to 0.193. Dark ink measured 1.7 to
3.0 against it and pale ink would have measured 1.4. Three rounds went into choosing an ink and
all three were wasted, because nothing contrasts against a mid tone. **Move the GROUND, not the
ink.** The lamp's falloff takes the band to the deck's own dark and the furniture is then one
pale ink across all nine frames, which is what it should have been from the start.

**Canvas text cannot be registered to DOM text in a variable font.** TYPE_AS_OBJECT was carved
by drawing the headline again on the canvas, offset either side of the cast direction. It
ghosted, and not by a fixable amount: the headline is Archivo at `"wdth" 116` and `cx.font` has
no width axis, so the two copies agreed at the first letter and drifted further apart with every
glyph after it. **Carve with a `text-shadow` pair** computed from `TXDECK.castDir()`. It is
applied to the glyphs themselves so it can never drift, and the type stays vector in the PDF.

**A rim light is a clip, never a stroke.** Stroking a layer's whole path outlines every rect on
all four sides and turns a room of furniture into a wireframe diagram of a room of furniture,
which is the "diagram of a place" the judges named, drawn by the call meant to cure it. Clip to
the shapes and paint a band along the lit edge.

**Atmospheric perspective can delete the subject.** The first room frame mixed every row so far
toward the ground colour that the near row was within 3 L* of the wall, and the room read as an
empty black rectangle. A depth cue that takes the nearest object to within noise of the
background has not created depth.

**A page's own rules do not dodge that page's own type.** Quieting a document's rules against
its own text punches a feathered hole whose boundary lands inside the glyph band, and the QA
harness reads the repair as a strike. The tell is that the reported strike MOVES when the text
moves. Place the rules clear of the blocks, which is how a document is set anyway.

**Bisect before theorising.** One strike survived four different fixes. Removing the pool made
the frame pass, which named the cause in one render: the title sat on the steepest part of the
falloff. The four fixes before that were aimed at the tooth, the dither, the reserve and the
leading, and every one of them was a guess. **Never reason from an absence to a cause without
first asking something that can answer**, which is the rule CLAUDE.md already states about
empty CI check lists and is the same rule here.

**When a frame's QA goes sideways across rounds, recompose it rather than tune it.** Frame 7
went 45, 53, 52 and back on the same measure while the falloff and the ruled bed were moved
around. Its real problem was that the subject sat in the middle with blank stock under it.
Moving the page down so the document occupies the lower two thirds cleared it in one render.
This is the repro of the round rule in `prompts/daily_routine.md`: every round closing what the
last one named and naming a new one is the signal to stop repairing and start over on that
frame.

### The order of work, amended

The chassis comes before any frame. Phase 10.5 builds it and renders ONE probe frame against
it, because a chassis that is wrong is wrong nine times.

## THE FRAME STANDS IN A PLACE (2026-09-20, owner, and it sits beside THE ARTWORK CARRIES THE DATA)

**A frame is built on the scene bench. Something is placed through the camera, at true scale in
metres, on a ground plane, casting a shadow from the deck's one declared light. A frame drawn in
screen pixels is a diagram of a place rather than a place, and a deck of them reads flat.**

The owner: *"everything is very flat and 2d, we need to teach the automation and agents through
research how to do more 2.5d and expand its artwork capabilities beyond this flat look"*.

### It was never a missing capability, and that is the whole finding

`assets/js/txscene.js` is a 2.5D scene bench. A ground plane, a horizon, a level pinhole camera,
objects at TRUE SCALE IN METRES, one declared light casting every shadow onto the plane. It was
written on **September 11th, 2026**, for this exact complaint. Its own docstring:

> Twenty one decks shipped and the judges' craft finding was the same one every time, in
> different words: a small primitive floating in a gradient with the type stacked above it.
> "Assembled, not drawn." "An object in a void." The cause was structural rather than a lapse
> of taste. Every frame was drawn in screen pixels with no camera, so nothing had a size,
> nothing stood on anything, nothing cast a shadow onto anything, and a bus was a slab because
> a slab is what you draw when you do not know how tall a bus is.

Measured across 27 shipped decks and 241 frames on the day this law was written:

| | |
|---|---|
| staged frames per deck | median **0**, best ever **5** |
| distinct depth cues per deck | median **0**, best ever **5** |
| 2026-09-18, -19 and -20 | **zero** depth cues, all three decks |
| `S.fade`, aerial perspective | **never used**, 0 of 27 decks |
| `S.box` and `S.slab`, form shading | **never used**, 0 of 27 decks |
| `tx3d.js`, the software 3D renderer | **1** frame of 241 |
| `three.module.min.js` | **0** frames |

Fifty four frames LOAD the bench and then draw in screen pixels anyway. **A camera a frame does
not place through is a camera it did not use.**

So nothing here needed inventing. The kit was complete and optional, and a cue nobody is asked
for is a cue that does not appear. That is the third defect of this exact shape found in one day.

### The cues, from the perception literature rather than from taste

Pictorial depth, the kind available to a flat printed frame, is carried by eight cues. They are
not interchangeable and they are not equally strong. **Occlusion is the most reliable and gives
only ORDINAL depth**, which is to say it tells a reader what is in front, never how far.
Relative size and texture gradient give METRIC depth, a distance a reader can estimate. Aerial
perspective is measurably more powerful than its reputation suggests.

**Depth is several weak cues agreeing, not one strong cue repeated.** That is why the gate counts
distinct cues as well as staged frames.

Every one of them already has a call:

| cue | what it is | the call |
|---|---|---|
| **occlusion** | a nearer form hides part of a farther one | draw far first. `S.row`. The bench does NOT z-sort, deliberately, because a slide is a drawing and the drawer decides the order |
| **relative size** | the same object subtends less at distance | `S.ppm(Z)`, px per metre at depth Z |
| **height in the field** | on a ground plane, farther is higher | `S.groundY(Z)` |
| **linear perspective** | parallels converge at the horizon | `S.project(X, Y, Z)` |
| **texture gradient** | a texture packs denser with distance | `S.gridZ`, `S.gridX`, `S.strip` |
| **aerial perspective** | distance washes contrast toward the sky | `S.fade(hex, Z)` |
| **cast shadow** | where the light is blocked, on the plane | `S.shadow(sprite)`, from the ONE declared light |
| **form shading** | a lit face and a shadow face on one solid | `S.box`, `S.slab` |

### The two nobody has ever reached for, and they are the cheap half

`S.fade` and `S.box` have not been used by a single deck in 27. They are also the two that most
directly answer the word the owner used.

**Flat is what a shape filled with ONE value looks like.** `S.box` gives a solid a lit face and a
shadow face off the same declared light, so the form turns in space instead of being a silhouette
with a colour. One call, and a slab becomes a thing.

**Distance with no atmosphere reads as a sticker on glass.** `S.fade(hex, Z)` walks a hue toward
the sky value with depth. It is the cue that separates a far row from a near one when both are
the same object at the same brightness, and it is what makes the ground go somewhere instead of
stopping.

### What the gate asks

`scripts/carousel/depth_floor.py`, against `config/carousel/depth_floor.json`:

- **at least five frames of nine are STAGED.** Staged means the frame builds the bench, places
  something through the camera, and casts a shadow from the declared light. All three. September
  12th and 13th both reached five in a real run, so this is a high water mark rather than a
  stretch, and every deck since has been under it.
- **at least four distinct cues across the deck.** One under the high water, deliberately: the
  fifth cue is where a frame makes a choice, and a quota met by reaching for whatever is cheapest
  is not the same as a frame that needed it.
- **the scene's light agrees with the chassis's.** `TXDECK.declare` names one light for the deck
  and `TXSCENE.create` takes its own. Two surfaces holding their own copy of one rule with
  nothing in between checking them is this repo's oldest defect, and it has already shipped the
  wrong site URL on three decks, a missing hashtag block and a missing progress counter. Here it
  would put the scene's shadows and the chassis's shadows running different ways under one sun.

### Why it is measured in the code and not in the pixels

Four pixel statistics were tried first, against 59 decks of the reference corpus: modelling
inside lit forms, count of value shelves, aerial contrast ratio, and mass surviving a blur. **None
of them separated the two corpora.** Depth here is a property of how a frame was CONSTRUCTED, and
the construction is in the source. A gate that measured the output would have reported clean.

### WHAT STAGING THE REFERENCE COST, and three of the four were the same mistake

`examples/figure-bearing/` was restaged onto the bench in four render passes. Three of the four
failures were **the same defect wearing different names**, and it is the one hazard worth knowing
before writing a frame against this bench.

**EVERY OPTION ON THIS BENCH IS OPTIONAL, AND A WRONG NAME IS SILENTLY A DEFAULT.** These are
plain object literals with `num(g.x, default)` behind them. Nothing throws, nothing warns, and
the frame renders. Three times in one sitting:

- `Lm.pool` takes `x` and `y`. Given `cx` and `cy` it translated to `undefined`, went NaN, and
  painted the whole pool at the ORIGIN, which put a warm glow over the kicker on three frames.
- `S.strip` takes `X, w, near, far, fill`. Given `from`, `to` and `ink` it drew its DEFAULT
  six metre band from 0.8 to 400 metres, a grey wedge across two thirds of the frame that read
  as a catastrophic cast shadow.
- `S.gridX` takes X extents in `from`/`to` and Z extents in `near`/`far`. `S.gridZ` takes Z
  extents in `from`/`to`. **They are not the same shape.** Given gridZ's arguments, gridX draws
  every line off frame to the right, in silence.

**The check that catches all three is to look at the render.** Each was invisible in the source,
silent at run time, and obvious in the image. Read the signature in `txscene.js` before the call,
and then look at the picture.

**AN OBJECT TALLER THAN THE EYE PROJECTS ABOVE THE HORIZON, and the type lives up there.** Frame
2's first cut stood a 3.1 m volume at a 1.4 m eye, its top edge landed at y 421, and the machine
QA reported the dek struck through. The fix was not to move the type. The figure on that frame is
a RATIO, so the metres were free, and the whole volume became 1.4 m: **its top now sits exactly on
the horizon**, which is what eye height means and is a better frame than the one that failed.

Before placing anything tall, ask what `horizon - f * (H - eye) / Z` comes to and whether the type
is already there.

### What this does NOT say

It does not say every frame is a landscape. A DOCUMENT frame showing a page, a TYPE_AS_OBJECT
frame where the headline is the image, and a GRID frame of pure isotype marks can all be staged:
put the page on a desk at a depth, stand the letters on the ground, give the marks a plane to
sit on and a shadow each. **Staging is not a subject, it is a space the subject occupies.** Four
of nine frames may still be flat, and the gate says which four is the deck's choice.

It does not license a render engine this repo does not have. `tx3d.js` exists for a heightfield
or a mesh and is the right tool perhaps once a deck. The bench is the ordinary path.

## THE ARTWORK CARRIES THE DATA (2026-09-20, owner, and it outranks THE PRIMARY IMAGE LAW below)

**A frame's image is built out of the story's own computed numbers. The geometry a reader looks
at IS a figure from `figures.json`, set as a bar height, a mark count, a stipple density, an arc
sweep, a spacing, a radius. A frame whose image encodes nothing is wallpaper with good lighting,
and this deck does not ship nine of them.**

The owner, on four consecutive shipped decks:

> "it keeps doing that faded look, doesnt seems like its making each run bespoke on its own ...
> the alaska one juts seems miles ahead as far as the actual coherence of the artwork, like it
> earns its way on scren, and is relevant to the story, the texas one seems uncoordinated still
> and random on the art"

### What was measured, so the cure is not mistaken for taste

Four guesses about "faded" were tested against pixels before this rule was written, and **all
four were wrong.** Ground chroma, tonal range, ink mass and mass-under-blur were measured across
59 shipped decks of the reference corpus and this repo's own frames:

| | reference | here |
|---|---|---|
| median ground chroma (OKLCh C) | 0.0214 | 0.0215 |
| median tonal range (L\* p98 minus p2) | 0.63 | 0.66 |
| median ink mass | 0.209 | 0.325 |
| ink surviving an 8 px blur | 0.98 | 0.92 |

**They are indistinguishable.** "Faded" is not a palette defect, not a contrast defect and not a
hairline-texture defect, and a fix aimed at any of them would have been the fifth wrong guess.
The difference is in WHAT THE FRAMES DRAW:

    The reference computes its numbers and DRAWS THEM.
    This repo computed its numbers and drew a PICTURE NEXT TO THEM.

Counted on the storyboards of the four decks that prompted this, frames carrying **no numeral at
all**: 6 of 9, 4 of 9, 2 of 9, 6 of 9. The images were a control room, a walkway, a brick wall, a
garage. Every one drawn well, lit from one declared key, graded, seated on a chassis, and every
one of them silent about the story it sat beside.

### Why the chassis work did not reach this, which is the part worth understanding

THE DECK IS THE UNIT, above, made nine frames look like ONE deck. It was right and it holds. It
is a rule about COHERENCE, and coherence is not the same question as whether the art says
anything: nine identical silent frames are perfectly coherent. The chassis raised the ceiling and
nothing made a run climb to it.

The score history is the proof, and it is the reason this law lands at CONCEPTION rather than at
review:

| deck | score | rounds |
|---|---|---|
| 2026-09-14 | 7.118 | 1 |
| 2026-09-15 | 7.578 | 1 |
| 2026-09-16 | 7.492 | 1 |
| 2026-09-17 | 6.856 | 5 |
| 2026-09-18 | 6.800 | 6 |
| 2026-09-20 | 6.968 | 5 |

**More rounds produced worse decks.** A frame conceived as wallpaper is not rescued by five
rounds of better lighting, and every round spent tuning one is a round that could not have fixed
it. **Quality here is set when the frame is conceived and it is not recoverable afterwards.**

### What a frame declares, in its dossier, before it is drawn

```yaml
data_in_art:
  figure: small_systems_of_all    # a key in figures.json, or a claim's computed value
  drives: mark count              # the drawn parameter that figure SETS
```

`drives` names a parameter a renderer can set. "Column height", "mark count", "stipple density",
"arc sweep", "ring radius", "row spacing". It never names a mood: "the sense that the system is
strained" is not a parameter and no reviewer can check a drawing against it.

Then **draw that.** The value reaches the canvas, not only the headline. A figure stated in type
and nowhere else is the exact defect this law exists for, and the gate looks for the number in the
frame's code with the text nodes stripped out, so a headline cannot satisfy it.

### The floor, and why it is six rather than nine

`config/carousel/figure_bearing.json` sets it and `scripts/carousel/figure_bearing.py` enforces
it, at the STORYBOARD, before a frame is drawn and while changing it is cheap. Six of nine.

The median of what shipped is four, the reference standard asks for the mapping on every frame,
and six is the midpoint: reachable in one run and impossible to reach with wallpaper. It is
deliberately not nine, because a cover and a closing frame can honestly carry no quantity, and a
floor that forbids that gets routed around rather than met.

### WHAT THE FIRST FIGURE BEARING FRAMES COST TO BUILD, and every line here was paid for

`examples/figure-bearing/` is three frames, three figures, three ways of drawing a number, and it
exists because there was no example of this step anywhere in this repo. It took four renders. The
first one **reproduced the exact defect this law exists to fix**, which was worth more than a
clean first pass.

**`TXDECK.pick(ramp, i)` TAKES AN INDEX, NOT A FRACTION, and this is the fastest way to draw a
faded frame by accident.** The ramp is SEVEN steps and `pick` does `Math.round(i)` on it. So
`pick(ramp, 0.74)`, written by an author who meant "74 percent up the ramp", returns **step 1**,
the second darkest, and `pick(ramp, 0.18)` returns step 0. Every fill lands on the two darkest
steps of seven and the whole frame sinks into the ground. The first render of these three frames
did exactly that and looked precisely like the decks the owner was complaining about. Nothing
errors, nothing warns, and the geometry is perfectly correct underneath. **Write integer steps,
0 to 6, and read them as steps.**

**`Lm.pool` takes `x` and `y` and `reserve`. It does not take `cx`, `cy` or `mask`.** Passing the
wrong keys does not throw. `translate(undefined, undefined)` makes the whole gradient NaN and the
pool renders at the ORIGIN, which put a warm glow in the top left corner of all three frames,
over the kicker. Machine QA caught it as *"text struck by a drawn rule"*, which names the symptom
three hundred pixels from the cause. `Lm.desk` does take `mask`, and a function rather than a
list, which is why the mistake looked reasonable. `Lm.falloff` is a VERTICAL gradient taking
`from`, `mid` and `end`, and not a radial with a centre and a radius.

**The check that catches all three is to look at the render.** Each was invisible in the source,
silent at run time, and obvious in the image.

**A SECOND SCALE IS HOW YOU DRAW A LIE WITHOUT NOTICING.** Frame 3 first drew the 87 large systems
at one mark each against the 3,579 small ones at one mark per 50. Both were labelled, both counts
were computed, every numeral traced. On the page **87 looked bigger than 3,579**, and the frame
argued the opposite of the record it was drawn from. The fix was one scale: frame 1's field, with
the 87 picked out of it as a 1.74 mark sliver. A frame that needs two scales to make its point is
usually a frame whose point is not true at one.

### What this does NOT say

It does not say every frame is a chart. A map whose projection is the story's own geography, a
document drawn at the size the record gives it, a person at true scale beside a thing whose
dimension is a computed figure, a room whose depth is set by a measured distance: all of these
carry data and none of them is a chart. THE TEN LAYOUTS all remain available. What changes is
that the layout has to be chosen for what the frame must ENCODE, and seven of those ten can be
drawn either way.

It does not relax one line of THE PRIMARY IMAGE LAW below. A subject is still a thing, it still
owns thirty percent, it still bleeds, it is still lit by one declared key. This law says what
that subject's dimensions come from.

**And it is a gate rather than a paragraph, deliberately.** The rule it restates has existed in
the reference repo's doctrine since long before this one, in prose, and this machine never did
it. GATE_LESSONS' oldest shape is a rule stated somewhere with nothing in between checking it.

## THE PRIMARY IMAGE LAW

**Every frame carries one drawn subject that owns at least thirty percent of the frame, reads
as one silhouette at feed size, and on most frames runs off at least one edge.** The type is
placed around the image, never the other way round. The dossier names the subject, the rect it
owns in frame px and the edges it bleeds, and `scripts/carousel/layout_check.py` reads the
pixels afterwards and refuses a frame whose rect turns out to hold a flat plate with words on it.

What follows from it:

- **The image is planned first and drawn first.** A frame's dossier opens with `layout` and
  `primary_image`. Its code draws the image before a line of type exists, and the type is fitted
  into the reserve the image leaves.
- **A subject is a THING.** A bus, a courthouse, a pump jack, a person at a desk, a sheet of
  paper, a page of a rule, a county. A field, a haze, a gradient, a wash and a grain are not
  subjects. They are what the subject stands in.
- **True scale or no scale.** If the subject is a physical thing it is drawn in metres on the
  scene bench beside something whose size a reader knows, which is usually a person.
- **Most frames bleed.** A subject cropped by the frame is inside the reader's space. A subject
  floating in the middle with margin all round is a postage stamp, and a deck of postage stamps
  is what the judges called "objects in a void". At least four frames of nine bleed an edge.
- **One accent per deck, used with restraint.** One colour from `config/brand.yaml`, never the
  flag red, present on three to six frames and never over eight percent of any frame. The rest
  of the deck is the rendered world in its own materials and light.
- **One light per scene.** Declared once, in the camera, and every shadow in the scene falls
  from it.

## THE TEN LAYOUTS, and the rotation

The table lives in `assets/js/txlayout.js`, in the browser and in Node, and `layout_check.py`
carries a copy its self-test asserts against that file. The names:

| archetype | the image | the type |
|---|---|---|
| **FULL_BLEED** | fills the frame edge to edge | one reserve, a band top or bottom, kept quiet by the scene itself (a black ceiling, a dark sky, `the render keeps it quiet by construction) |
| **SPLIT_HORIZON** | one side of one straight horizontal cut, at least 55 percent of the height | the other side, on flat ground |
| **TYPE_AS_OBJECT** | the headline IS the image, carved, cast, stacked, extruded, poured | the rest is small. At most one per deck |
| **OBJECT_AND_CAPTION** | one object drawn large on a ground plane with a horizon, the poster | a short caption beside or under it |
| **DIAGRAM** | a drawing annotated with leaders and mono labels, the thing explained | the labels ARE the type |
| **GRID** | repeated units at true scale, the isotype, a count a reader can count | a headline and a number under each unit |
| **DOCUMENT** | a drawn page, form, screen, ledger or letter with its own typography inside it | the type on the page is image, not caption |
| **MAP** | cartography from `assets/geo/`, places named | a caption, and the labels on the map |
| **CLOSE_CROP** | the subject cropped by at least two edges, at detail scale, the reader inside it | one reserve |
| **FIGURE_SCALE** | a person at true scale beside the thing, so the thing has a size | in the sky or ground the composition leaves empty |

**The rotation over nine frames (rebalanced 2026-09-16, see THE CONTINUITY MANDATE above):** at
most two of the same archetype in a row, at least three distinct, TYPE_AS_OBJECT at most once,
FULL_BLEED and CLOSE_CROP at least two between them, at least four frames bleeding an edge, and
at least two continuity devices named in the storyboard. Check the sequence before any dossier
is written:

    node -e 'require("./assets/js/txlayout.js"); console.log(TXLAYOUT.check(["FULL_BLEED","DOCUMENT","FIGURE_SCALE","OBJECT_AND_CAPTION","GRID","DIAGRAM","CLOSE_CROP","SPLIT_HORIZON","FULL_BLEED"]))'

An empty list is a plan. Anything else is a rewrite before a single dossier.

**Which layout wants which claim.** A claim about a thing wants OBJECT_AND_CAPTION or
CLOSE_CROP. A claim about a place wants FULL_BLEED or SPLIT_HORIZON. A claim that is a document's
own words wants DOCUMENT. A count wants GRID. A mechanism wants DIAGRAM. A where wants MAP. A
"how big" wants FIGURE_SCALE. A single phrase that is the whole story wants TYPE_AS_OBJECT, once.

## THE RENDER (2026-09-23, owner, and it REPLACES the print register, which is deleted)

**The owner, verbatim:** *"a few days ago we made a bunch of updates to the automation so that it
would stop just trying to use like that faded look with the stupid shapes because it looked bad.
And so it would start actually creating like its own artwork for each run. But it's not doing
that. It's reverted back to the same old bullshit artwork on these last runs."* And then:
*"delete that fallback bullshit look, make it impossible for me to have to tell u this again."*

### What the faded look was, measured

This section used to be THE PRINT REGISTER: every scene drawn in greys on an offscreen twin, then
pushed through a halftone, line, hatch or stipple screen onto a paper stock by `TXINK.print`. It
argued that "a gradient is what a screen does when nobody decided anything". What it produced was
one engraved texture over every surface, so steel, caliche, water and sky all read as the same
faded etching, and that texture is what the owner has been rejecting since September 20th.
Loaded, by frame:

| decks | frames printed | |
|---|---|---|
| 2026-09-14, -15, -16 | 9 of 9 | |
| 2026-09-17, -18 | 0 of 9 | the owner's fixes had landed |
| 2026-09-19, -20, -21, -23 | 9 of 9 | **reverted** |

**`assets/js/txthree.js`, the GPU physically based bench, was loaded by ZERO frames in the
history of this repository.** It was always here.

### Why it came back, because the September 20th fix missed this

It was not drift. This file and `prompts/daily_routine.md` ORDERED it. The routine said every
frame is "printed in paper and ink" and pointed every director at `examples/editorial-deck/`, a
deck built on the print, as "what a 7 looks like". The treatment director, the pixel critic and the
flow critic carried the same pointer. September 20th added THE ARTWORK CARRIES THE DATA and THE
FRAME STANDS IN A PLACE, both right, and **neither asked whether a frame was printed**, so every
run passed both new gates while producing the look they were written to end. A fix that does not
measure the defect does not hold.

Pixel statistics could not have caught it either, and that was measured on 2026-09-23 rather than
assumed: a high frequency residual scored the owner's own worked example at 0.84, higher than a
printed deck, and a spectral periodicity test scored one printed deck at 0.00 because shipped WebP
compression erases the frequencies a screen lives in. **The look is chosen in the code, so
`print_ban.py` refuses it in the code.**

### What a frame is now

The sister corpus's own doctrine is THE RENDERED LADDER: *"hero slides should reach for the
highest rung the story supports. GPU PBR, real materials, soft shadow maps, IBL reflections, ACES.
The default for object heroes."* Its decks render solid objects and carry ONE hero object through
all nine frames, a tide staff on one deck and a sea ice model on another. No screen anywhere.

1. **ONE HERO OBJECT, modelled once and carried through the deck.** Built as `three.js` geometry
   in the deck's chassis (`TXT.extrude`, `TXT.lathe`, `TXT.tube`, boxes with bevels), so every
   frame renders the SAME object from a new camera or in a new state. That is the continuity
   device, and it is stronger than any screen, because a reader recognises a thing before they
   recognise a texture.
2. **A real material and one rig.** `TXT.mat.steel`, `clay`, `plastic`, `emissive`, lit by one of
   `TXT.rigs` chosen in the chassis for the deck. Soft shadow onto a ground the object touches,
   and a contact where it touches.
3. **At least six of nine frames render through `txthree.js` and call `snapshot()`.** Counted by
   `print_ban.py`. The others may be solid shaded forms on the canvas bench (`S.box`, `S.slab`,
   the way `examples/figure-bearing/` does it). None is printed.
4. **The figure is geometry.** Forty engines are forty rendered units, a ratio is two rendered
   lengths at ONE scale, and any quantity uses parallel projection. Perspective is for scenes.
5. **The finish is a GRADE, never a screen.** `txpost.js` for tone, a vignette and fine grain over
   a render. Grain on a solid render reads as film. A screen over it reads as the faded look.
6. **Text stays DOM**, seated in quiet the render leaves for it, because the PDF must keep vector
   type and because 3D type is how a render starts looking like a template.

### What a director is told

Pitch the HERO OBJECT first, in metres, as geometry: what it is, what it is made of, and the one
thing about its shape the story turns on. Then nine cameras and states of that object. A pitch that
names a screen, a paper, a stock or a print register is pitching the deleted look.

## THE WORLD (2026-09-24, owner, and it is what THE RENDER was missing)

**The owner, verbatim, the day after THE RENDER shipped:** *"the artwork hasnt hit the mark yet
ever, and it needs to be a SHOWSTOPPER every single slide should literally look world reknowned."*

### What was measured on the first rendered deck

Carousel no. 32 obeyed THE RENDER to the letter. One hero object, a real material, one rig, all
nine frames through `txthree.js`. Artwork craft scored 6.8, and the reason is in the pixels rather
than in the taste of whoever drew it. `examples/world-proof/compare.webp` renders no. 32's own
model and camera four ways beside the frame that shipped, so the difference is the engine alone.

1. **An object in a void.** `TXT.setup` gave a frame a flat background colour and a grey plane.
   Seven chassis under `assets/js/deck/` each improvised a sky under deadline, and no. 32's was
   near black with a two degree band. No horizon, no light in the sky, no haze in depth.
2. **Hard shadows nobody asked for.** Every rig set `shadow.radius` and `PCFSoftShadowMap` ignores
   it, so for two months every cast shadow shipped hard edged. VSM is now the default.
3. **Two tone curves.** The renderer mapped ACES and `TXDECK.finish` ran a second filmic curve on
   top. Pure white came out near 231 of 255 and the mids lifted. That is the murk, measured.
   `TXT.snapshot` now marks the page and the grade skips its own curve on a rendered frame.
4. **Clean clay.** Nothing standing in Texas is clean at the bottom.

A render inherits its world from the engine, and the engine gave it none. All four are fixed IN
THE ENGINE, so no run has to remember them.

### What a frame stands in now

```js
// the chassis, once: TXDECK.declare({ ..., light:{ az:-62, el:8 }, sky:'goldenHour' })
const W = TXT.deckWorld();                 // the deck's ONE world, resolved from the declaration
const R = TXT.setup(gl, { w:1080, h:1350, fog:[W.haze, W.fogDensity], exposure:W.exposure, tone:W.tone, fov:36 });
TXT.frame(R, { from:[x, 1.6, z], look:[0, 2, 0] });
TXT.sky(R);                                // dome, IBL rendered FROM it, fog in its horizon hue
TXT.deckRig(R, W.rig, { target:[0,0,0], distance:80 });    // the sun IS the declared light
TXT.ground(R, { surface:'caliche', size:900 });            // caliche, dirt, asphalt, concrete, grass
TXT.scatter(R, { kind:'grass', count:6000, area:[...], avoid:[[...the pad...]] });
TXT.add(R, hero); TXT.contact(R, hero);    // the dark core where it meets the ground
TXT.weather(R, {});                        // grime at the base, mottle in the paint
const shot = await TXT.snapshot(R);
```

1. **Choose the world for the STORY, in the treatment, before any code.** The storyboard's
   treatment names the deck's `world:` once and says why this story wants that light. The chassis
   declares it. A dossier does not restate it, for the same reason SLIDE_DOSSIER_SPEC gives for
   the light: a second copy is how nine frames end up under two suns.

| world | what the light does | declared el | a story about | type |
|---|---|---|---|---|
| `goldenHour` | low warm sun, long shadows, blue sky | 4 to 14 | building, ambition, what is coming | light, on the shadowed ground or sky |
| `goldenHour`, camera INTO the sun | silhouette, cool rim on steel, a glowing seam | 3 to 8 | scale, weight, consequence | light |
| `blueHour` | an amber seam under deep blue, lamps on | the LAMP, 25 to 45 | the grid after dark, demand that does not sleep | light |
| `nightSodium` | black sky, city glow on one horizon, sodium key | the LAMP, 20 to 60 | what runs all night, what is not seen | light |
| `highNoon` | bleached sky, short black shadows | 55 to 78 | heat, water, strain | dark |
| `overcast` | no disc, everything soft and honest | 35 to 60 | procedure, a filing, a waiting room | dark |
| `stormFront` | a bruised sky and one shaft of sun | 6 to 16 | risk, a warning, a deadline | light |

   The chassis declares the light with an elevation in its world's range, and the world itself
   as `sky` in the same `TXDECK.declare`: a preset name, or `{ preset:'goldenHour', haze:0xd8b48e }`
   to tune one. Frames read it with `TXT.deckWorld()`, and `TXT.sky` THROWS when a frame hands it
   a different world, the way `TXT.deckRig` reads the light rather than trusting a frame's copy.
   Never edit `TXT.worlds`, which every future deck stands on.
2. **The sun is the deck's light.** `TXT.sky` puts the sun's glow where `TXDECK.declare` says,
   so the glow, the key, the cast shadows and the warm side of every object agree on all nine
   frames by construction. Pointing the camera toward the declared azimuth puts the glow in frame,
   and that is the strongest image this engine makes.
3. **Every standing thing gets `TXT.contact`.** A cast shadow says where the light is. A contact
   says the thing has weight. Without one every render floats.
4. **Everything manufactured has an edge.** `TXT.roundedBox(w, h, d, r, material)` for enclosures,
   cabinets, buildings and tanks, with r from 2 to 6 cm for plate steel. A sharp CG edge catches
   no light, and that is most of why a primitive looks like a primitive.
5. **`TXT.weather(R)` before every snapshot.** Grime toward the ground, mottle in paint and
   roughness, in world space and seeded.
6. **Scatter makes a place and never touches the type.** A pad is bare and graded, the field
   around it is not. `avoid` rectangles in world metres keep the pad a pad and the type's reserve
   calm. Grass over a headline is a plate made of weeds.
7. **The camera is a photographer's.** Eye at 1.5 to 1.7 m for a human frame, 0.4 to 0.9 m for a
   monument, 40 to 150 m up for a site. Field of view 26 to 40, the compressed look of industrial
   photography, and wider than 55 only inside a room. The horizon on a third and never through
   the middle. The hero owns 30 to 60 percent of the frame, and something in the foreground (a
   fence post, a stone, a kerb) gives the depth a reader feels before they see it.
8. **Type sits on the calm value.** The sky above the horizon, or the dark ground under a
   backlight. Never over scatter and never over the busy middle. `qa.py` measures the contrast.

### THE SHOWSTOPPER TEST, which every critic and the scorer apply

At 432 px, with the type covered:

1. Does it read as a PHOTOGRAPH of a PLACE at a TIME OF DAY?
2. Is there one thing to look at, lit from the side its shadows say?
3. Is there a sky or a deliberate interior, a horizon on a third, and haze in the distance?
4. Does everything standing touch the ground, with a contact and dirt at its base?
5. Would it hold as the opening spread of a serious magazine's feature on this story?

**A deck whose every frame passes all five is the artwork 10 in the rubric.** It was a cap at 6
for one day, 2026-09-24, and the scale was recalibrated to the sibling product's that evening: a
cap on a scale whose typical deck is 7 decides the verdict before the deck is read. A frame that
fails it now scores by how far it falls on the descriptors, and the critics still name every
failed question as a defect to fix.

### The gate

`print_ban.py` counts frames that stand in a world, meaning rendered AND calling `TXT.sky` in the
frame's own code, on the render context the frame keeps, before the snapshot it keeps: at least
five of nine from 2026-09-24, and the probe frame one of one. Five rather than nine because an
interior is a real frame. The other four may be rooms, desks or documents, and **every one of them
stands in a room `TXT.interior` built**: a floor with tooth, walls that take the shadows, a lit
window, the studio environment and the deck's rig. A rendered frame that calls neither `TXT.sky`
nor `TXT.interior` before its kept snapshot FAILS the run and is named, because a floor, a plane
and a background colour are exactly the void no. 32 shipped.

### What this does NOT say

- It does not say every frame is outdoors, and it does not say golden hour. The table exists so
  decks differ, and the variety ledger still measures the palette each world produces.
- It does not replace THE ARTWORK CARRIES THE DATA. Forty sets is still forty rendered units.
- It does not license a chassis to write its own sky, its own ground texture or its own develop
  that tone maps again. The engine carries those now, and a second copy is how they drift.

## THE FIVE LIBRARIES

All under `assets/js/`, all deterministic per seed, all loaded with `@@ASSETS@@/js/<name>.js`.

**THE LOAD ORDER, and it is stated rather than discovered because two of these throw on a
missing dependency:**

```
noise.js  txtype.js  txcolor.js  txpost.js  txdeck.js  deck/<date>-<world>.js  [txscene.js txfig.js
txobjects.js]  txlayout.js        and, as an ES module, three.module.min.js + txthree.js
```

`txcolor.js` and `txpost.js` are NOT optional and are not "for hero frames". They were loaded by
one slide in 205 and that is the single largest measured cause of the flat look. `txdeck.js`
throws on load without them, which is deliberate: the failure it prevents is a frame that
renders ungraded and looks fine on its own.

The bracketed four are the scene bench and are used when a frame needs true-scale objects. They
are a bin of parts and the chassis is the deck's world, so **the chassis comes first and the bin
serves it**, never the other way round.

### txscene.js — the camera and the ground

A pinhole camera at `eye` metres above a flat ground, looking level, horizon at `horizon` px,
focal length `f` px. World X is lateral, Y is up, Z is depth. Everything in metres.

```js
const S = TXSCENE.create(cx, { w:1080, h:1350, eye:1.4, horizon:640, f:820, sky:"#000",
                               fogZ:1e9, light:{ az:-40, el:38 } });
S.ground({ near:0.8, far:400, fill:"#4A4A4A" });          // the plane, far to near
S.gridZ({ dz:4, from:2, to:120, ink:"rgba(0,0,0,.3)" });   // joints of constant depth
S.strip({ X:-6, w:7, near:1, far:500, fill:"#333" });      // a road
S.shadow(sprite, { X:6, Z:30, ink:"#000", alpha:.5 });    // the ground shadow, from the light
S.sprite(sprite, { X:6, Z:30, inks:{ ink:"#DCDCDC", paper:"#141414", accent:"#DCDCDC" } });
S.box({ X:20, Z:60, w:30, h:9, d:40, fill:"#B9B4A5" });    // a shaded block with a hull shadow
S.rectBox({ X, Z }, { x, y, w, h })                        // a local rect's screen box, to mount type on a sign
S.project(X, Y, Z); S.groundY(Z); S.ppm(Z);                // the arithmetic, when you need it
```

Draw far things first. The bench does not sort. **Every scene declares one light** (`az`
degrees from the camera axis, `el` above the horizon, 8 to 75) and every shadow falls from it.
The sun 16 degrees up throws the long shadows of a poster at dusk. 50 degrees is noon.

Two cameras worth knowing. **Standing eye** (1.6 to 1.7 m, horizon around 0.55 to 0.67 of the
height) for places. **Seated eye** (1.05 to 1.15 m) for rooms. A **long lens** (f 2400 at Z 16)
flattens a row of units to equal size for a GRID. A **low horizon** (horizon 0.65 and up) with a
tall subject bleeds the top for FIGURE_SCALE.

### txfig.js — people

```js
TXFIG.figure({ pose:"walk", height:1.7, hat:"hard", hold:"clipboard" })
TXFIG.figure({ view:"front" })                    // the isotype front view, for counts
TXFIG.figure({ pose:"sit", seat:0.45 })           // seated, at a desk or a dais
TXFIG.crowd(12, { seed:7, hats:["hard"], holds:["bag"], children:true })
```

Poses: `stand walk stride point wave raise phone carry sit crossed lean`. Hats: `hard brim
cap`. Held things: `briefcase box placard clipboard phone bag`. Eight head canon, 1.70 m unless
told otherwise, `child:true` for a child's proportions. Mirror through TXSCENE to face left.

A person is not decoration. Use one where the claim has a person in it: the student the rule
is for, the lineman on the pole, the commissioner behind the dais, the queue at the counter.

### txobjects.js — the catalogue

Forty four objects at true scale. `examples/objects/catalogue-1.jpg` and `catalogue-2.jpg`
show every one beside a 1.7 m figure, and that is the page to look at before choosing a
subject.

    vehicles     school_bus sedan (sensor:true for a robotaxi) pickup truck_semi ambulance
    the grid     utility_pole (transformer:true) transmission_tower wind_turbine pump_jack
                 substation data_center power_plant cooling_tower solar_panel
                 battery_container server_rack
    water, land  water_tower windmill stock_tank live_oak pine mesquite cattle fence_post
    buildings    house (style:"two_story") school civic_facade (dome:true) capitol hospital
                 warehouse strip_mall
    the street   road_sign (kind:"stop") billboard camera_pole streetlight traffic_signal
    interiors    desk office_chair student_desk dais podium hospital_bed filing_box
                 pallet_boxes voting_booth
    the air      drone helicopter

`TXOBJ.sprite(name, opts)`. Bodies are ink, details are paper, and `{ body:"accent" }` paints
one object in the accent. `TXOBJ.wire(S, [X,Z,Y], [X,Z,Y])` strings a catenary between two
points, so a row of poles reads as a line. `TXOBJ.fence(S, [x0,z0], [x1,z1])` runs a fence.
Objects that come in populations (`live_oak`, `house`) take `seed` and vary.

A subject that is not in the catalogue is drawn as parts in metres with `TXSCENE.sprite(parts)`,
four part kinds: `poly`, `rect`, `ellipse`, `line` (thick, round capped). The tablet in frame 6
of the example deck is nine lines. When a run draws one worth keeping, it goes in the backlog as
a proposal for the catalogue.

### txthree.js — the render (and txink.js, which is deleted)

`txink.js` sat here until 2026-09-23 and is deleted on the owner's instruction. Its API is not
reproduced, because a signature in this file is an invitation to call it.

```js
// an ES module script, inside window.renderReady. The world first, then the deck's object.
import * as THREE from '@@ASSETS@@/js/three.module.min.js';
import { init } from '@@ASSETS@@/js/txthree.js';
const TXT = init(THREE);
const W = TXT.deckWorld();                                 // the deck's ONE world, from the chassis
const R = TXT.setup(glCanvas, { w:1080, h:1350, fog:[W.haze, W.fogDensity],
                                exposure:W.exposure, tone:W.tone, fov:36 });
TXT.frame(R, { from:[7, 1.6, 9], look:[0, 1.8, 0] });
TXT.sky(R);                                                // sky + IBL from it + fog in its hue
TXT.deckRig(R, W.rig, { target:[0, 0, 0], distance:60 }); // the sun IS the declared light
TXT.ground(R, { surface:'caliche', size:900 });            // the object stands ON something
const hero = buildHero(THREE, TXT);                        // the deck's one object, from the chassis
TXT.add(R, hero); TXT.contact(R, hero);                    // add() sets the shadow flags
TXT.weather(R, {});
const shot = await TXT.snapshot(R);                        // render + black frame sentinel
if (!shot.ok) throw new Error('black frame');              // never ship a black rectangle
```

The whole world is documented at the top of THE WORLD above and in the header of
`assets/js/txthree.js`, with every option. `TXT.roundedBox`, `TXT.scatter` and `TXT.weather` are
there too.

Verified in this container on 2026-09-23: WebGL2 through SwiftShader, a PBR steel solid with fog
and a soft shadow rendered cleanly in 5.8 seconds. Rules: `setup` sets pixel ratio before size,
so the 2x store is filled; never `Math.random`, use `TX.rng(seed)`; text stays DOM; perspective
for scenes and parallel projection for any quantity; fog in the sky's own hue.

**The reserve rule survives the print.** Type never sits on busy surface. The render keeps the
type's zone quiet by construction: sky above a horizon, a dark ceiling, a floor falling off away
from the key light. The furniture band is 130 px top and bottom.

### txlayout.js — the table and the furniture

`TXLAYOUT.check(sequence)` at plan time. `TXLAYOUT.mount(document.body, { kicker, kicker2,
counter, src, ink })` writes the kicker, the counter and the source line in their fixed
positions, so bespoke code is only ever the image and the headline. **The site line is static
HTML in every slide**, `<div class="tx-site" id="site">texasaidocket.com</div>` with the
`.tx-site` rule the example slides carry, because `coherence_check` reads it from the FILE with
a regex and a line a script mounts is not in the file. `mount` throws if asked for it.
`TXLAYOUT.reserve(arch)` is where the type goes for each archetype, as a starting rect.

## THE ORDER OF WORK, which is half of the craft

1. **Rotation before dossiers.** Write the nine layouts as a list, run `TXLAYOUT.check`, then
   assign a subject to each, then write the dossiers. A dossier written before its layout is a
   dossier for the one skeleton.
2. **Frames 7, 8 and 9 first.** Every judged deck was thinnest at the end, because the budget
   ran out where the argument lands. Build the close first, then the turn, then the open.
3. **Image before type, on every frame.** Draw the scene, render it, look at it at 432 px with
   no type on it. If it is not an image yet, no headline will make it one.
4. **One hero object, one material, one light, for the deck.** Declared in the chassis, held by
   the critic. Nothing is screened.
5. **Then the type,** into the reserve the image left. `TX.fitText` for the hook. The furniture
   through `TXLAYOUT.mount`.
6. **Then the gates,** `qa.py` and `layout_check.py --require`, before any critic sees a
   frame. A critic's round costs more than a gate's, and the gate is what finds the plate.

## THE GATE, so this is a law and not a mood

`scripts/carousel/layout_check.py` reads `storyboard.md` and the renders and measures:

    1  the rotation over the nine `layout` values
    2  each `primary_image.rect` at least 0.30 of the frame
    3  at least four rects touching a frame edge, and every declared bleed real
    4  detail inside the rect, on the pixels: a quarter of the 8 px cells that are not under
       type carry a luminance std over 6 (a DOCUMENT's type counts as its image)
    5  a silhouette at thumb scale: the subject covers 8 percent of the rect and one piece
       holds half of it (a GRID must come apart into four or more pieces instead)
    6  the accent: present on three to six frames, never over 8 percent of one, never flag red

The routine runs it with `--require`, so a deck with no `layout` keys is a run that did not
plan its layouts, and that is a fail. The example deck measures clean on all six. Carousel no.
21, given full frame rects and measured the same way, fails 4 or 5 on seven of nine frames,
which is the finding the judges made in words and the number that says the gate is aimed at it.

## What still fails, named so nobody rediscovers it

- **An object in a void.** A render in front of a flat background colour, which is every frame of
  no. 32. `TXT.sky`, and `print_ban.py` counts it. (2026-09-24)
- **Clean clay.** A painted enclosure with no grime at its base and no mottle in its paint reads
  as a maquette. `TXT.weather(R)`. (2026-09-24)
- **A sky that mixes orange into blue.** The midpoint of the two is grey, and the first world
  proof came out as mauve smog. Warmth lives at the horizon on the sun's side and the zenith stays
  blue, which is how the presets are built. (2026-09-24)
- **Weeds over the headline, and faceted stones.** Scatter without `avoid` lands under the type,
  and a flat shaded stone reads as a game asset. (2026-09-24)
- **A chassis that develops its own frame and grades it filmic again.** The renderer already tone
  maps. `TXDECK.finish` now skips its own curve on a rendered frame, and a chassis must not route
  around it. (2026-09-24)
- **A horizon that reads as sea.** Every judge named it on frames 1, 3, 4, 5, 8 and 9 of no. 34, in
  all five rounds, and no fix a run could make touched it, because the cause was the engine. Fog
  was mixed after tone mapping in a colour the sky never shows, so a fogged ground printed a flat
  strip below a brighter sky. **Fixed in `txthree.js`:** the fog is the sky's own colour in every
  direction, a far field carries the ground to the horizon, and the far plane reaches whatever
  ground a frame builds. Call `TXT.sky` and `TXT.ground`, and never hand-build a horizon plane, a
  terrain skirt or a backdrop strip. If a band still shows, something in the frame at the horizon
  has `fog:false` or is a flat 2D layer. (2026-09-26)
- **A camera pointed at the ground.** No. 33's frame 6 called `TXT.sky` and looked straight down
  through an orthographic camera, so it showed no sky and the showstopper test capped it in all
  five rounds. No. 34's frames 4 and 5 looked down on a yard and were named as objects in a dark
  gradient. `TXT.snapshot` now measures the horizon against the camera, and `print_ban.py` fails
  the frame off the render report on the probe. A camera with something built overhead within 12 m
  (a room, a cab roof, a canopy) is inside, and looking down is an interior shot. Measured: no. 34's
  page on the cab seat passes, and its two yards fail. Keep the horizon in frame, or stand the
  camera inside something built. (2026-09-26)
- **A far skyline standing on a line.** No. 34's Houston stood on the sea band with a hard base,
  and every judge asked to haze it. Kit far models (`city_skyline`, `mesa`) now haze toward the
  sky behind them, heaviest near the ground, so the base dissolves and the crowns stay clear. Place
  them 2 to 10 km out and let the haze carry the distance. (2026-09-26)
- **A figure in the dark.** No. 34's frame 9 used the kit's `person` in dark clothes, backlit at
  blue hour, and every judge read it as a low-poly mannequin in all five rounds. The model is
  detailed. What they saw was a silhouette with no light on its face side. Put the key on the
  side the camera sees, or crop to the shoulder. (2026-09-26)
- **A cab or a room built from primitives.** No. 34's frame 3 built the cab from a capsule seat,
  a torus wheel and a box dash, and it was named in all five rounds. The kit has no vehicle
  interior. Stand outside the cab and look in, or crop to one part modelled at kit detail, and put
  the missing model in the backlog. (2026-09-26)

- **A subject at the wrong distance.** A 60 m school at Z 58 is 30 px tall on a phone. Bring
  the subject in until it owns its rect, and let something else carry the distance.
- **A crowd as a mass.** Figures at the same tone as the furniture beside them merge into one
  pale shape. Give the figures and the objects different greys in the twin.
- **Busy surface under type.** The contrast gate will catch it and the critic will fail it. The
  render keeps the reserve quiet by construction: sky, ceiling, or a floor falling off.
- **A ring or a leader through a letter.** Draw marks beside type in the DOM (an SVG path), and
  end every leader short of the glyph band. `qa.py` reads a canvas stroke through a line as a
  strikethrough, and it is right.
- **Rotated DOM text.** The QA's line boxes are axis aligned and rotated lines overlap. Rotate
  the drawn sheet a degree if you must, never the type by more than that.
- **The accent everywhere.** One object, one stroke, one window. Three to six frames.
- **Any screen at all.** Halftone, line, hatch, stipple: the print screen is DELETED on the
  owner's instruction of 2026-09-23 and `print_ban.py` fails the build on one. What varies
  between frames is the camera and the state of the hero object. What holds them together is
  that it is the SAME object, rendered in one material under one rig.
- **A slab where a thing should be.** If it is not in the catalogue, draw it in metres from
  parts, and put it in the backlog.
- **Nine frames that are one call.** `bespoke_check` compares slide CODE and fails a deck at a
  median similarity of 0.55. The print pipeline is shared by design, so the scene inside each
  frame's `draw` has to carry its own drawing. The example deck measures 0.46 with every frame
  a different scene, and a deck that copies a frame and swaps the object will not.
- **A site line a script wrote.** `coherence_check` reads `class="tx-site"` from the HTML
  file. The line is static in every slide, never mounted.
- **The model's own defaults, which it reaches for when design direction runs out** (2026-09-23).
  Anthropic's prompting guide for the model the routine now runs on lists five: a cream or
  off-white ground, italic accent words in headlines, numbered "01, 02, 03" section labels,
  monospace labels and pill-shaped buttons. It also gives the cure, which is to name them: a
  general "avoid a generic look" mostly swaps one default for another. For this brand four of
  the five are out and one stays. **A cream, paper or off-white ground** is the retired paper
  register (`paper` is `quoted_only` in `config/brand.yaml`) and the faded look the owner
  rejected. **Italic accent words** carry emphasis the headline's own words should carry.
  **Numbered section labels** duplicate the `NN / NN` counter, which is the only numbering the
  furniture prints. **Pill-shaped chips and tags** are web furniture, not render furniture.
  **Monospace stays**: the counter, the site line, the kicker and a DIAGRAM's labels are this
  brand's instrument voice. A frame uses one of the four only where its dossier argues for it.
  When a deck falls into a default this list does not name, the retro adds it here with the
  date and the frame, because the guide's own advice is to work iteratively and extend the list
  from what the first result reached for.
