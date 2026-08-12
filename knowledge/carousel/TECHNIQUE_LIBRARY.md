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

**Dust column** — vertical `TX.warp2` with a hard falloff, one column, off-centre. For stories
about something arriving. *Fails when:* there are two. One is weather, two is a pattern.

**Norther front** — a hard horizontal value break with a soft gradient beneath, the cold side
above. The one atmosphere with a real edge in it, so it does structural work. *Fails when:* the
break lands on the vertical centre and cuts the slide in half.

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
