# Slide brief, frame 2 of 9, 2026-11-18 (BESPOKE, LOOK V2, tone EXPLAINER)

**You are the artist for this frame only.** Read `knowledge/carousel/BESPOKE.md`, `.claude/agents/carousel-slide-artist.md`, the LOOK V2 section of `CLAUDE.md` and `knowledge/carousel/ARSENAL.md` first. The deck plan is `out/2026-11-18/storyboard.md` (your dossier is its slide 2 yaml block, which carries your acceptance list; the CRAFT PLAN row is your starting concept). Claims are `out/2026-11-18/claims.json`.

## The story in one line
A UT Dallas team paired satellite readings of eight air pollutants from 2022 with CDC cancer prevalence for all 254 Texas counties and used machine learning. Counties with more pollution tended to have more cancer, but the researchers say it is an association between places, never proof that pollution causes cancer in any one person. No county is named or valued anywhere. No NASA, ESA, CDC or UT logo or seal.

## The beat
WHY SATELLITES. Feel: how much land one station leaves. Know: Ground monitors are costly and missing in places. c13 c25.
Planned picture (a strong starting concept, not a cage; you pitch three and may beat it): the chassis air_monitor_shelter on a concrete pad with inlet mast and met mast, kit chain_link_fence round it, kit pickup and kit person in a vest at the door, kit mesa on the horizon, TXT.ground caliche with scatter and kit mesquite, TXT.contact and TXT.weather
Camera: WIDE, eye height 1.6 m, 50 m back, 35 mm, horizon at 0.62 of the frame.

## The copy (fixed)
- kicker: `Why satellites`
- counter: `02 / 09`
- headline (verbatim): `Ground monitoring is costly`
- dek (verbatim, except the one exception below): `That cost has limited this kind of study, the researchers say. The paper says satellite data can help where ground monitoring is unavailable. Drawn to illustrate.`
- labels: [] (add none unless the picture truly needs one; any label is a tone pill, never dusk gold unless it marks what the satellite read)
- claim ids (the `src` furniture): `c13 c25`

**The one exception.** A dek sentence that only describes the picture ("drawn to illustrate", "the slab is drawn to illustrate") must describe YOUR picture truthfully. Rewrite only that sentence, keep "drawn to illustrate", add no number, date, name or claim. Every other sentence stays word for word. House rules on any word you set: no em or en dashes, no colons or semicolons, no first person, can't never cannot, no sentence opening with And or But, straight quotes, banned words gap, gaps, matters, pattern, patterns.

## The figures (window.FIG, exactly)
`{}`
Every count or length you draw is computed from window.FIG in your code with a check that throws on a mismatch. This frame draws no count; set window.FIG = {} and draw nothing as a quantity.

## The spine
- chassis: `assets/js/deck/2026-11-18-landbench-bespoke.js` (declares `bespoke: true`, LOOK V2 tone `explainer`, accent dusk gold `#e0956a` meaning WHAT THE SATELLITE READ, the air as measured, and nothing else). Load it after `txdeck.js` and `txlook.js`, exactly as `out/2026-11-18/tmp/probe/slides/slide-01.html` loads it (copy that file's head and boot shape, never its picture; delete its NANMESH debug line).
- accent on this frame: this frame carries NO dusk gold (a ground monitor is not the satellite).
- EAST IS ALWAYS FRAME RIGHT on any frame with geography.
- EXPLAINER tone: cerulean, ice and indigo; shadows lean indigo, never black; no dark room, no black type band.
- models for this frame: air_monitor_shelter (chassis), plus kit chain_link_fence, pickup, person (worker, vest), mesquite, mesa. The chassis's two models (survey_satellite, air_monitor_shelter) are installed by CH.boot; read their notes in the chassis. Plus every kit model in ARSENAL. K.make merges a model's `options` as defaults, so pass real values.
- a chassis probe render (`out/2026-11-18/tmp/probe/chassis_probe.png`) shows both chassis models build.
- type faces, counter, kicker, site line and `TXDECK.finish` are fixed. Everything else is yours. Seat type with `CH.seat`, footer with `TXLOOK.footWash`.
- file: `out/2026-11-18/slides/slide-02.html`
- your render dir: `out/2026-11-18/work/render-02` (yours alone): `python3 .claude/skills/carousel-engine/render.py --slides-dir out/2026-11-18/slides --out-dir out/2026-11-18/work/render-02 --only 2 --timeout 300000`
- your concepts: `out/2026-11-18/briefs/slide-02.concepts.md`
- `@@ASSETS@@` resolves to `assets/` at render time. All scratch stays inside `out/2026-11-18/`; never write under any .claude directory.

## The neighbours
- frame before: READ FROM ORBIT. Feel: the scale of it. Know: A UT Dallas team read all 254 counties from above. c1 c2 c24. FIG counties.
- frame after: THE INSTRUMENT. Feel: precision. Know: The readings came from Sentinel-5 Precursor and Copernicus. c17 c23 c2. FIG pollutants.

## What already ran, so do not repeat it
November 17th drew a steel scoring machine on a violet sweep, a card cabinet drawer, paper strata, paper columns on a plaza, a desk and chair under a lamp, and a Dallas County relief with raised tiles. November 16th drew a gold ribbon under an open caliper. November 15th drew a student desk from above and a gym of desks. November 14th drew wafers in a quartz boat and a county relief. So no desks, chairs, lamps, paper stacks, calipers or extruded per-county height maps. Judges lately charged: walls filling the top half, subjects cropped, sky banding behind headlines, wavy kit wood, flat face-on squares with typed labels, type plates reading as UI, top-down trays reading as charts, capsule people and mannequins, soft kit hands, uncountable units at feed size. Place your type where THIS picture leaves quiet; neighbours put theirs elsewhere. Integrity: association never causation; R squared is a model fit; Moran's I is cancer clustering; nothing drawn implies a real county's value.
