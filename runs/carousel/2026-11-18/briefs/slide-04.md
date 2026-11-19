# Slide brief, frame 4 of 9, 2026-11-18 (BESPOKE, LOOK V2, tone EXPLAINER)

**You are the artist for this frame only.** Read `knowledge/carousel/BESPOKE.md`, `.claude/agents/carousel-slide-artist.md`, the LOOK V2 section of `CLAUDE.md` and `knowledge/carousel/ARSENAL.md` first. The deck plan is `out/2026-11-18/storyboard.md` (your dossier is its slide 4 yaml block, which carries your acceptance list; the CRAFT PLAN row is your starting concept). Claims are `out/2026-11-18/claims.json`.

## The story in one line
A UT Dallas team paired satellite readings of eight air pollutants from 2022 with CDC cancer prevalence for all 254 Texas counties and used machine learning. Counties with more pollution tended to have more cancer, but the researchers say it is an association between places, never proof that pollution causes cancer in any one person. No county is named or valued anywhere. No NASA, ESA, CDC or UT logo or seal.

## The beat
WHAT IT READ. Feel: the air has parts. Know: Eight pollutants in 2022, sulfur dioxide the strongest predictor. c4 c6 c26. FIG pollutants.
Planned picture (a strong starting concept, not a cage; you pitch three and may beat it): a carved column of air over a plug of ground, a TXBENCH.relief raked from the upper left with cast shadows under each band, saturated glassy and matte materials, the ground strata weathered, a plug of ground in three strata (topsoil, caliche, limestone) under a rounded column of air cut into eight measured bands, the sulfur dioxide band standing proud, the column outline inlaid in dusk gold
Camera: MEDIUM, orthographic front elevation relief raked from the upper left.

## The copy (fixed)
- kicker: `What it read`
- counter: `04 / 09`
- headline (verbatim): `Eight pollutants, sulfur dioxide strongest`
- dek (verbatim, except the one exception below): `Satellites measured eight air pollutants in 2022. Among the environmental predictors of cancer, sulfur dioxide was the most influential. The bands are drawn to illustrate, not heights in the sky.`
- labels: [] (add none unless the picture truly needs one; any label is a tone pill, never dusk gold unless it marks what the satellite read)
- claim ids (the `src` furniture): `c4 c6 c26`

**The one exception.** A dek sentence that only describes the picture ("drawn to illustrate", "the slab is drawn to illustrate") must describe YOUR picture truthfully. Rewrite only that sentence, keep "drawn to illustrate", add no number, date, name or claim. Every other sentence stays word for word. House rules on any word you set: no em or en dashes, no colons or semicolons, no first person, can't never cannot, no sentence opening with And or But, straight quotes, banned words gap, gaps, matters, pattern, patterns.

## The figures (window.FIG, exactly)
`{"pollutants": 8, "pollutant_names": ["sulfur dioxide", "nitrogen dioxide", "carbon monoxide", "formaldehyde", "methane", "particulate matter smaller than 1 micrometer", "particulate matter smaller than 10 micrometers", "aerosols"]}`
Every count or length you draw is computed from window.FIG in your code with a check that throws on a mismatch. 

## The spine
- chassis: `assets/js/deck/2026-11-18-landbench-bespoke.js` (declares `bespoke: true`, LOOK V2 tone `explainer`, accent dusk gold `#e0956a` meaning WHAT THE SATELLITE READ, the air as measured, and nothing else). Load it after `txdeck.js` and `txlook.js`, exactly as `out/2026-11-18/tmp/probe/slides/slide-01.html` loads it (copy that file's head and boot shape, never its picture; delete its NANMESH debug line).
- accent on this frame: the column outline inlay and the proud sulfur dioxide band are the ONLY dusk gold.
- EAST IS ALWAYS FRAME RIGHT on any frame with geography.
- EXPLAINER tone: cerulean, ice and indigo; shadows lean indigo, never black; no dark room, no black type band.
- models for this frame: none (TXBENCH.relief). The chassis's two models (survey_satellite, air_monitor_shelter) are installed by CH.boot; read their notes in the chassis. Plus every kit model in ARSENAL. K.make merges a model's `options` as defaults, so pass real values.
- a chassis probe render (`out/2026-11-18/tmp/probe/chassis_probe.png`) shows both chassis models build.
- type faces, counter, kicker, site line and `TXDECK.finish` are fixed. Everything else is yours. Seat type with `CH.seat`, footer with `TXLOOK.footWash`.
- file: `out/2026-11-18/slides/slide-04.html`
- your render dir: `out/2026-11-18/work/render-04` (yours alone): `python3 .claude/skills/carousel-engine/render.py --slides-dir out/2026-11-18/slides --out-dir out/2026-11-18/work/render-04 --only 4 --timeout 300000`
- your concepts: `out/2026-11-18/briefs/slide-04.concepts.md`
- `@@ASSETS@@` resolves to `assets/` at render time. All scratch stays inside `out/2026-11-18/`; never write under any .claude directory.

## The neighbours
- frame before: THE INSTRUMENT. Feel: precision. Know: The readings came from Sentinel-5 Precursor and Copernicus. c17 c23 c2. FIG pollutants.
- frame after: THE FIT. Feel: a fair contest with a winner. Know: Four methods compared, the support vector machine fit best. c3 c20 c21. FIG r2_of_100.

## What already ran, so do not repeat it
November 17th drew a steel scoring machine on a violet sweep, a card cabinet drawer, paper strata, paper columns on a plaza, a desk and chair under a lamp, and a Dallas County relief with raised tiles. November 16th drew a gold ribbon under an open caliper. November 15th drew a student desk from above and a gym of desks. November 14th drew wafers in a quartz boat and a county relief. So no desks, chairs, lamps, paper stacks, calipers or extruded per-county height maps. Judges lately charged: walls filling the top half, subjects cropped, sky banding behind headlines, wavy kit wood, flat face-on squares with typed labels, type plates reading as UI, top-down trays reading as charts, capsule people and mannequins, soft kit hands, uncountable units at feed size. Place your type where THIS picture leaves quiet; neighbours put theirs elsewhere. Integrity: association never causation; R squared is a model fit; Moran's I is cancer clustering; nothing drawn implies a real county's value.
