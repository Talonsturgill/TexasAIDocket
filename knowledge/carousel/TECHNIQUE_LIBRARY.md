# Technique library — the variety engine's palette

Named techniques the deck engine can actually execute, each with what it is for, what it costs,
and how it fails. **A technique is named in the dossier before any code is written**, and
`ledger/carousel/artwork.json` records what shipped so tomorrow cannot reach for the same one.

Two things this file is not.

It is not a menu to pick from at random. A technique is chosen because **this claim wants it**.
The dossier field is `why_this_technique`, and "it looked good" is not an answer to it. A
cartographic claim wants cartography. A claim about a quantity over time does not become one by
being drawn on a map.

It is not a promise that the engine will make it beautiful. Every entry below has a failure mode
recorded because somebody will hit it, and knowing the failure in advance is most of the craft.

**Everything here is deterministic per seed.** `TX.reseed(seed)` and `TX.rng(seed)`, seed derived
from the run date. `render.py` scans inline scripts and `qa.py` FAILS on `Math.random()`, because
a slide that draws differently on a re-render cannot be reviewed. A critic who asks for one fix
and gets a different drawing back has no way to tell whether the fix worked.

---

## ATMOSPHERES — fields, washes, weather

The ground a slide sits on. An atmosphere is never the subject. When it becomes the subject, the
slide has nothing to say and is dressing that fact.

**Big Bend dusk field** — `TX.fbm2` domain-warped over the dark base, warm at the horizon line,
cold above. The house atmosphere and therefore the one to be most careful with, because it will
read as the default. *Fails when:* the warm band reaches the frame edge, which turns a horizon
into a stripe. Peaks go above the fade, geometry goes through it.

**Caliche haze** — a low-contrast pale wash over the lower third, `TX.fbm2` at large scale with a
tight value range. Good under a figure that needs to sit on something without competing.
*Fails when:* the value range creeps and dry haze starts to read as humidity. Caliche haze is dust
hanging in hot air, not water, and the difference is the whole register.

**Heat shimmer** — horizontal domain warp increasing with height above the horizon, amplitude
under 6px. Reads instantly as Texas summer. *Fails when:* it touches type. Warp the field, never
the glyphs.

**Dust column** — vertical `TX.warp2` with a hard falloff, one column, off-center. For stories
about something arriving. *Fails when:* there are two. One is weather, two is a pattern.

**Norther front** — a hard horizontal value break with a soft gradient beneath, the cold side
above. The one atmosphere with a real edge in it, so it does structural work. *Fails when:* the
break lands on the vertical center and cuts the slide in half.

**Grain** — `TX.grainTile` at low opacity over everything. Not optional on a flat field: an
untextured gradient reads as an unfinished render on a phone screen. *Fails when:* the tile
repeats visibly, which happens above about 4 percent opacity at 2x.

---

## STRUCTURES — generative systems

Systems that organise a frame. Reach for these when the claim is about **many of something**, or
about a pattern rather than a quantity.

**Flow field** — particle paths advected through `TX.simplex2`. For movement, drift, transmission.
*Fails when:* the paths are uniform in length, which reads as hair.

**Contour set** — nested isolines from an fBm field, thinning outward. Excellent under a figure
because it carries texture without value. *Fails when:* line spacing goes below 3px at 2x and
moirés on the thumbnail. Always check the 432px thumb.

**Hachure field** — `TX.hachureField` slope and aspect strokes, or `TX.hachureFromGrid` when the source is already a grid. Reads as terrain without a single
colour, and it is the honest way to draw relief in one hue. *Fails when:* the slope source is
flat, which produces uniform strokes and looks like a texture swatch.

**Voronoi districts** — d3 Delaunay over seeded points. The natural shape for service territories
and anything partitioned. *Fails when:* it is used for counties. Counties have real boundaries in
`assets/geo/`, and inventing their shapes is a fabrication a Texan will spot instantly.

**Stipple field** — density-mapped dots, density carrying the quantity. Reads as engraving.
*Fails when:* the dot count is high enough to grey out, at which point it is a wash pretending to
be data.

**Grid decay** — a regular grid whose cells degrade across the frame. For "this used to be
orderly". *Fails when:* the decay is linear and reads as a gradient over a grid.

**Wire relief** — `TX.reliefShade` 2.5D relit heightfield, with `TX.reliefRect` and `TX.reliefDome` for the bounded cases. The workhorse for terrain that has to carry
a label. *Fails when:* the light direction disagrees with the slide's value structure, which the
dossier declares.

---

## CARTOGRAPHY AND DATA

**Use `TXGeo` and never hand-place a Texas shape.** It is the same Albers equal-area conic the
website's map builder uses, so a slide and the site agree about where a place is. `tests/txgeo.mjs`
asserts the map is neither upside down nor mirrored, because Albers y grows northward and screen y
grows downward and neither library objects.

**County choropleth** — the 254-county mesh, one value per county. The most legible Texas frame
there is. *Fails when:* the scale has more than about five steps. A reader is matching swatches to
a legend, not reading a gradient.

**Single-county spotlight** — the state in silhouette, one county lifted in value. For a story
about one place. *Fails when:* the county is small and east, where 254 counties are dense. Add a
leader line to a label outside the mesh.

**Zone overlay** — ERCOT load zones over counties. **The mapping from county to zone must come
from a citable source**, and where it does not exist the slide says so rather than guessing, per
the law about publishing the size of what is not public.

**Line and node** — transmission as a path, substations as nodes. *Fails when:* the line reads as
a crack in the terrain. Give it a contact shadow with `TXCARVE`, or lift it in value.

**Dot density** — one dot per unit, placed inside the real county polygon. Honest and hard to
misread. *Fails when:* the unit is large enough that placement implies a location it does not have.

**Slope chart** — two points and a line, for one quantity at two times. Almost always better than
a bar pair, because the eye reads the angle. *Fails when:* the axis is truncated, which is a lie
told with a true number.

**The residual bar** — measured against modeled, with the gap drawn. **A bar, never a dial**, and
one hue at one intensity at every value. This is the grid watch's rule and it holds on a slide
too: a dial implies a red zone, and a red zone is a verdict the data cannot carry.

---

## DEPTH — the dimension bench

**`TX3D` is a software renderer on Canvas 2D.** Plan the camera arithmetically before rendering.
Compute the horizon y from the camera pitch and check the subject lands where the dossier says.
Eyeballing camera placement is how a mountain ends up in the bottom fifteen percent of the frame,
twice, before anybody works out why.

**Heightfield terrain** — `TX3D.heightfield` over an fBm source with fog. *Fails when:* the fog
start is inside the subject, which flattens the thing the camera came for.

**Parallax planes** — three to five flat layers at different depths, each with its own value.
Cheap, reliable, and reads as depth immediately. **Reach for this before a full 3D scene.**
*Fails when:* the layers share a value, at which point it is a collage.

**Extruded county** — one county polygon given thickness. The single most Texas-specific depth
move available. *Fails when:* the extrusion is deep enough to hide the shape, which is the only
reason the slide chose the county.

**Zdog scene** — vector 3D with rounded strokes, for a diagrammatic object like a transformer or a
cooling tower. *Fails when:* used for terrain, which it is not built for.

**SDF raymarch** — `TXSDF`, CPU signed distance fields. Expensive and worth it for one hero frame
per deck at most. *Fails when:* the step count is tuned for the full-size render and the thumbnail
gets a different surface.

**Three.js bench** — `txthree.js`, GPU through SwiftShader. The heaviest thing here. **Budget one
slide.** *Fails when:* it is used because it is impressive rather than because the claim needs it,
which the `why_this_technique` field exists to catch.

---

## SURFACE AND MARK

**Engraving** — `TXENGRAVE` white-line intaglio. Formal, archival, and the right register for a
statute or a filing. *Fails when:* the line density fights the type. Engrave the ground, not the
message.

**Wind-worked carve** — `TXCARVE` surfaces with two-part contact shadows. The contact shadow is
what makes a thing sit on a surface rather than float above it. *Fails when:* the shadow is one
part, which reads as a drop shadow and cheapens the whole frame.

**Post-processing** — `TXPOST` film-grade grade and bloom over a finished canvas. Last step, never
a rescue. *Fails when:* it is used to fix a value structure the composition never had.

**OKLCH palette** — `TXC`. Derive every colour of a deck from the story's own region, and name the
source in the dossier. Perceptual lightness is why palettes here hold their value relationships
when hue changes, which hex arithmetic does not.

**The reserved red.** `--flag-red` is for genuine urgency only, meaning an open comment deadline a
reader can still act on. Nothing else in the system wears it. A reservation with a duplicate is not
a reservation.

---

## TYPE AND CAROUSEL MECHANICS

**`TX.fitText` for display type**, never a hand-guessed size. The slide is 1080x1350 and it will be
read at 432px wide in feed.

**Everything is checked at the thumb.** A slide that only works at full size does not work. The
pixel critic reads both, and the thumbnail is the one a reader actually sees.

**`TX.svgPlate` measures the laid-out text** and draws the plate behind it. Never hand-size a plate:
the measurement is the point, and a plate sized by eye is a plate that clips on the one deck where
the headline runs long.

**Knockout labels** — `TX.canvasLabel` for a label that must survive over busy terrain.
*Fails when:* the plate is opaque enough to become a box, which is furniture. Aim for the least
plate that keeps the type legible.

**Safe margins.** Nothing important inside the outer band. LinkedIn crops, and the crop is not
announced.

**Slide 1 is the whole decision.** It is the only slide most people see. Give it the strongest
technique in the deck and the shortest line, four to seven words per the brevity principle.

**Nine different jobs.** If the nine dossiers could be produced by filling in one template nine
times, the deck is one drawing nine times, and `bespoke_check.py` will say so in a number after the
fact. `dossier_check.py` catches it before anything is drawn, which is where it is cheap.

---

## COHERENCE — the art varies, the frame does not

This section is in tension with everything above it, and holding both at once is the craft.
`bespoke_check.py` demands the nine DRAWINGS differ. This demands the FRAME around them does not.
A deck that breaks the first rule is a template. A deck that breaks the second is not a
publication, it is nine posters that happened to arrive on the same day.

**The measurement that produced this section.** The first two decks this product shipped:

| | slides | slide counter | furniture type sizes on every slide |
|---|---|---|---|
| 2026-08-16 | 8 | **none anywhere** | 24px, 25px |
| 2026-08-18 | 9 | `01 / 09` on all nine | 24px, 25px |

Both were green on every gate that existed. A reader following the account got a numbered nine
part deck one day and an unnumbered eight part deck the next. The type furniture held by accident
rather than by rule, and the numbering did not hold at all.

`scripts/carousel/coherence_check.py` now measures this. What it enforces:

- **The counter spine is all or nothing, then correct.** Number every slide or number none.
  Numbering some is a missing slide as far as a reader can tell, and a counter promising a total
  the deck does not deliver is an untruth printed on the page in the reader's own arithmetic.
- **Some type size appears on every slide.** The kicker, the counter and the source line are the
  deck's furniture and they do not get redesigned per slide.
- **No two slides lead with the same line.** Two slides saying one thing is one slide.

**What it deliberately does NOT gate, and why that matters as much.** Display type sizes vary
wildly across a good deck, 132 and 112 and 66 on one, 92 and 82 and 78 on another, because
`TX.fitText` fits each headline to its own box, which this file requires two sections up. A gate
on that would have failed both shipped decks for doing the right thing, and would have pushed the
next run toward hand-sized type. Colour count is left alone for the same reason. **A gate that
fires on correct behaviour gets switched off, and then it protects nothing.**

---

## READABILITY — the reader is giving this two seconds

A slide is read at 432px inside a scroll. It is SCANNED, not read, and the most common way a deck
fails is not ugliness. It is a slide that is a paragraph set in a large face.

- **Sixty five words is the ceiling and it is a backstop, not a target.** The shipped decks run a
  mean of 28.6 and 35.2 words a slide with a heaviest slide of 54, so the ceiling fails on
  regression rather than on good writing. If a slide is near it, the slide has two ideas in it.
- **One idea per slide.** The tell is the claim count. A slide citing five or more claims is
  usually an argument that wants two slides, and the gate warns on it rather than failing,
  because a summary slide legitimately gathers many.
- **The opening line is four to seven words.** Slide 1 is the only slide most people see. Every
  word past seven is a word spent before the reader has decided to stay.
- **Read every slide with the images off.** If the strings alone do not carry the decision, the
  art is doing work the copy should be doing, and the art disappears on a slow connection.

---

## ENGAGEMENT — the unit is the swipe, not the slide

A nine slide carousel is not nine slides. It is **eight decisions to swipe**, and each one is made
in about a second on the strength of what the slide just did. Pretty is what stops the scroll.
Owing the reader something is what moves them to slide 2.

**Every slide except the last must end owing the reader something.** Four ways to build that debt,
and they rotate like everything else here.

- **The open loop.** Name the thing and withhold the number. "The schedule gives each block a
  length. It never says which block follows the morning." The reader swipes to find out what does.
- **The withheld actor.** Name the decision and not who made it, then land the decider next.
- **The turn.** A slide that reverses what the previous three built. Best placed at 5 or 6, which
  is where attention sags, and it is the single most reliable way to rescue a middle.
- **The counter-image.** Every claim in this record has one, and it is usually the most
  interesting thing on the page. The award is not a running machine. The robot is built in Austin
  and starts its shift in Illinois. **Put the counter-image on its own slide.** A deck that only
  argues one way reads as promotion, and this record's whole standing is that it does not.

**The value arc.** Nine slides at one brightness is a deck nobody remembers, however good each
frame is. Plan the deck's value structure across the SEQUENCE before any slide is coded, and give
it one deliberate inversion, the way 2026-08-16 put a single paper slide at position 5 in an
otherwise dark deck. The inversion is what a reader remembers the deck by.

**Judge the strip, never the slide.** The contact sheet is the real design surface, because it is
how the flow critic sees the deck and how a reader's memory stores it. A deck can be nine strong
frames and a weak strip. Open the contact sheet before the pixel critics, not after.

---

## HOW TO CHOOSE

In order.

1. **What is the claim?** Cartographic, quantitative, sequential, or about a physical thing.
2. **What did the last decks use?** `ledger/carousel/artwork.json` holds the exclusions. No two
   decks alike is ledger-enforced, not a preference.
3. **What does this story's own region look like?** A Panhandle story and a Gulf story should not
   be able to swap palettes.
4. **What will it look like at 432px?** Decide this before writing the code, not after the critic
   says so.
5. **What is the failure mode above, and what is the plan for it?** That plan is an acceptance item
   in the dossier, which is what the pixel critic grades against.

**When two techniques both fit, take the one that is harder to do well.** The engine is a harness,
not a template, and the deck that stops a Texan scrolling is not the one that played it safe.
