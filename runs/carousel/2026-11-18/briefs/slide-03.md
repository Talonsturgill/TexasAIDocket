# Slide brief, frame 3 of 9, 2026-11-18 (BESPOKE, LOOK V2, tone EXPLAINER)

**You are the artist for this frame only.** Read `knowledge/carousel/BESPOKE.md`, `.claude/agents/carousel-slide-artist.md`, the LOOK V2 section of `CLAUDE.md` and `knowledge/carousel/ARSENAL.md` first. The deck plan is `out/2026-11-18/storyboard.md` (your dossier is its slide 3 yaml block, which carries your acceptance list; the CRAFT PLAN row is your starting concept). Claims are `out/2026-11-18/claims.json`.

## The story in one line
A UT Dallas team paired satellite readings of eight air pollutants from 2022 with CDC cancer prevalence for all 254 Texas counties and used machine learning. Counties with more pollution tended to have more cancer, but the researchers say it is an association between places, never proof that pollution causes cancer in any one person. No county is named or valued anywhere. No NASA, ESA, CDC or UT logo or seal.

## The beat
THE INSTRUMENT. Feel: precision. Know: The readings came from Sentinel-5 Precursor and Copernicus. c17 c23 c2. FIG pollutants.
Planned picture (a strong starting concept, not a cage; you pitch three and may beat it): the chassis survey_satellite in silver and graphite foil with a crinkle bump, a blue cell solar wing, a nadir instrument with baffle, a star tracker and antenna, a dusk gold glass swath fan of eight bands opening off the bottom, TXT.studio explainer
Camera: CLOSE, low three quarter from below right, 50 mm, the solar wing on a diagonal.

## The copy (fixed)
- kicker: `The instrument`
- counter: `03 / 09`
- headline (verbatim): `A view of all of Texas`
- dek (verbatim, except the one exception below): `The air readings came from the Sentinel-5 Precursor satellite and the Copernicus Atmosphere Monitoring Service. Public CDC data supplied the cancer side. The craft is drawn to illustrate.`
- labels: [] (add none unless the picture truly needs one; any label is a tone pill, never dusk gold unless it marks what the satellite read)
- claim ids (the `src` furniture): `c17 c23 c2`

**The one exception.** A dek sentence that only describes the picture ("drawn to illustrate", "the slab is drawn to illustrate") must describe YOUR picture truthfully. Rewrite only that sentence, keep "drawn to illustrate", add no number, date, name or claim. Every other sentence stays word for word. House rules on any word you set: no em or en dashes, no colons or semicolons, no first person, can't never cannot, no sentence opening with And or But, straight quotes, banned words gap, gaps, matters, pattern, patterns.

## The figures (window.FIG, exactly)
`{"pollutants": 8}`
Every count or length you draw is computed from window.FIG in your code with a check that throws on a mismatch. 

## The spine
- chassis: `assets/js/deck/2026-11-18-landbench-bespoke.js` (declares `bespoke: true`, LOOK V2 tone `explainer`, accent dusk gold `#e0956a` meaning WHAT THE SATELLITE READ, the air as measured, and nothing else). Load it after `txdeck.js` and `txlook.js`, exactly as `out/2026-11-18/tmp/probe/slides/slide-01.html` loads it (copy that file's head and boot shape, never its picture; delete its NANMESH debug line).
- accent on this frame: the swath fan is the ONLY dusk gold; the satellite foil is silver and graphite, never gold.
- EAST IS ALWAYS FRAME RIGHT on any frame with geography.
- EXPLAINER tone: cerulean, ice and indigo; shadows lean indigo, never black; no dark room, no black type band.
- models for this frame: survey_satellite (chassis). Options {wing: 7, yaw: 0.35}. Origin at bus centre, nadir -y, wing along +x. The chassis's two models (survey_satellite, air_monitor_shelter) are installed by CH.boot; read their notes in the chassis. Plus every kit model in ARSENAL. K.make merges a model's `options` as defaults, so pass real values.
- a chassis probe render (`out/2026-11-18/tmp/probe/chassis_probe.png`) shows both chassis models build.
- type faces, counter, kicker, site line and `TXDECK.finish` are fixed. Everything else is yours. Seat type with `CH.seat`, footer with `TXLOOK.footWash`.
- file: `out/2026-11-18/slides/slide-03.html`
- your render dir: `out/2026-11-18/work/render-03` (yours alone): `python3 .claude/skills/carousel-engine/render.py --slides-dir out/2026-11-18/slides --out-dir out/2026-11-18/work/render-03 --only 3 --timeout 300000`
- your concepts: `out/2026-11-18/briefs/slide-03.concepts.md`
- `@@ASSETS@@` resolves to `assets/` at render time. All scratch stays inside `out/2026-11-18/`; never write under any .claude directory.

## The neighbours
- frame before: WHY SATELLITES. Feel: how much land one station leaves. Know: Ground monitors are costly and missing in places. c13 c25.
- frame after: WHAT IT READ. Feel: the air has parts. Know: Eight pollutants in 2022, sulfur dioxide the strongest predictor. c4 c6 c26. FIG pollutants.

## What already ran, so do not repeat it
November 17th drew a steel scoring machine on a violet sweep, a card cabinet drawer, paper strata, paper columns on a plaza, a desk and chair under a lamp, and a Dallas County relief with raised tiles. November 16th drew a gold ribbon under an open caliper. November 15th drew a student desk from above and a gym of desks. November 14th drew wafers in a quartz boat and a county relief. So no desks, chairs, lamps, paper stacks, calipers or extruded per-county height maps. Judges lately charged: walls filling the top half, subjects cropped, sky banding behind headlines, wavy kit wood, flat face-on squares with typed labels, type plates reading as UI, top-down trays reading as charts, capsule people and mannequins, soft kit hands, uncountable units at feed size. Place your type where THIS picture leaves quiet; neighbours put theirs elsewhere. Integrity: association never causation; R squared is a model fit; Moran's I is cancer clustering; nothing drawn implies a real county's value.
