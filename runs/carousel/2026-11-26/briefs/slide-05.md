# Slide brief, frame 5 of 9, 2026-11-26 (BESPOKE, LOOK V2, tone EXPLAINER)

**You are the artist for this frame only.** Read `knowledge/carousel/BESPOKE.md`, `.claude/agents/carousel-slide-artist.md`, the LOOK V2 section of `CLAUDE.md` and `knowledge/carousel/ARSENAL.md` first. The deck plan is `out/2026-11-26/storyboard.md` (your dossier is its slide 5 yaml block, which carries your acceptance list; the CRAFT PLAN row is your starting concept). Claims are `out/2026-11-26/claims.json`.

## The story in one line
Texas Tech's IMMS in Lubbock and Fort Worth based AVX Defense Technologies built two tools under the Army's FleetSpace program, an AI enabled maintenance decision tool (FSUI) and an engine life tracker (PSV), and Texas Tech says both have been provided to the Army. In testing the neural networks restored 37 percent of missing and corrupted flight data, cut data volume by up to 30 percent and files by up to 73 percent, and predicted unplanned and 480 hour phase maintenance actions. The deck's argument is BEFORE IT FAILS: one illustrative engine drawn to no maker's design and its record drawn as metal, the gold mark following what the software puts out. RULES: every result is from testing, never from service. Texas Tech says the tools were provided to the Army; never fielded, deployed, used or bought. No aircraft type, unit, cost, accuracy or savings figure exists and none may be implied. The software recommends and predicts; people inspect and decide; no frame shows the software fixing or flying anything. Not a war deck: no weapons, no insignia.

## The beat
FOUR EIGHTY. Know: in testing, the networks predicted unplanned and 480 hour phase maintenance actions. c5.
Planned picture (a strong starting concept, not a cage; pitch three and you may beat it): a brushed stainless hour rule running diagonally across an indigo bench mat, etched ticks with no numerals, a polished brass end stop, and one dusk gold enamel tab clipped at the 480 hour stop casting a shadow.
Camera and largest object: TXBENCH relief of a brushed stainless hour rule, stainless with brass and one accent enamel tab, the chassis key, casts from the rule and tab onto the indigo mat, weathered with brushed grain and edge wear
Data in art: the rule's length and its major ticks are set from FIG.phase_hours in the slide's own code, one major tick every 10 hours stated as a drawing rule
Planned type seat: see the dossier's composition bands. Put the type where YOUR picture leaves quiet.

## The copy (fixed)
- kicker: `Phase hours`
- counter: `05 / 09`
- headline (verbatim): `480 hour phase actions, predicted in testing`
- dek (verbatim, except the one exception below): `In testing, the neural networks predicted unplanned maintenance actions. They predicted 480 hour phase maintenance actions too.`
- labels: ["480 hour phase"]
- claim ids (the `src` furniture): `c5 c4`

**The one exception.** A dek sentence that only describes the picture ("drawn to illustrate") must describe YOUR picture truthfully. Rewrite only that sentence, keep "drawn to illustrate" or "drawn to no maker's design" where it is, add no number, date, name or claim. Every other sentence stays word for word. House rules on any word you set: no em or en dashes, no colons or semicolons, no first person, can't never cannot, no sentence opening with And or But, straight quotes, banned words gap, gaps, matters, pattern, patterns.

## The figures (window.FIG, exactly)
`{"phase_hours": 480}`
Every count or length you draw is computed from window.FIG in your code with a check that throws on a mismatch.

## The spine
- chassis: `assets/js/deck/2026-11-26-flightrecord-bespoke.js` (declares `bespoke: true`, LOOK V2 tone `explainer`, accent dusk gold `#e0956a` meaning WHAT THE SOFTWARE PUTS OUT and nothing else). Load it after `txdeck.js` and `txlook.js`, exactly as `out/2026-11-26/tmp/probe/slides/slide-01.html` loads it (copy that file's head and boot shape, never its picture; its render is `out/2026-11-26/tmp/probe/render/slide-01.png`, a model proof of the engine and stand). Use `CH.develop(await TXT.snapshot(R, {}), gl)`, then seat type with `CH.seat`, footer with `TXLOOK.footWash`, and `TXDECK.finish(cx)` last.
- accent on this frame: YES, #e0956a, on what the software puts out only (a tag, a restored cell, the phase mark, the flagged blade or part, the two cased tools)
- MATERIAL CODE: bead blasted titanium and heat tinted nickel alloy are the machine (`CH.titaniumMat(K)`, `CH.heatMat(K, THREE)`). Bare 6061 aluminium is the record (`CH.aluMat(K)`). The accent is `CH.goldMat(K)`.
- EXPLAINER tone: cerulean over ice blue, a clean near white key, an indigo fill, indigo and violet in every shadow, never black. No dark room, no black type band. Grey mid tones fail value_register, so surfaces take saturated colour; bare metal reflects the coloured studio.
- chassis models (read their doc comments in the chassis): `turboshaft_engine` (panel, cutaway, tag, axisY; illustrative, drawn to no maker's design; userData.parts), `engine_stand` (axisY default 0.92, hook; userData.hookAt), `blisk` (blades, diameter, flag, heat; lies in the x-z plane, userData.bladeAt(i)), `record_tray` (cols, rows, filled, w; row major from the near left corner; userData.cellAt(i)). Mount the engine on the stand with `K.make('turboshaft_engine', { axisY: stand.userData.axisY })`. Helpers `CH.goldMat`, `CH.titaniumMat`, `CH.aluMat`, `CH.heatMat`, `CH.ortho`, `CH.leader`, `CH.pin`, `CH.project`, `CH.studioOpts`, `CH.roomOpts`, `CH.rigSpec`, `CH.rigOpts`, `CH.aim`, `CH.canvasTex`. Plus every kit model in ARSENAL (event_recorder, mill_vise, person, laptop, monitor, desk, document_stack and more). The chassis models are BASIC geometry; REFINE their look inside your own frame (more parts, materials, wear) but never edit the chassis file. Anything else you need you build in your own frame, at true size in metres, never as a bare primitive.
- a TXBENCH relief file shape to copy (never its picture): `runs/carousel/2026-11-25/slides/slide-03.html` (CH.bootFlat, TXBENCH.relief under the chassis key).
- type faces, counter, kicker, site line and `TXDECK.finish` are fixed. Everything else is yours.
- NO aircraft type, insignia, unit patch, tail number, maker's mark (GE, AVX, Army), legible screen or likeness. No weapon. No person except, if a frame needs one, a gloved hand cropped at the wrist.
- file: `out/2026-11-26/slides/slide-05.html`
- your render dir: `out/2026-11-26/work/render-05` (yours alone): `python3 .claude/skills/carousel-engine/render.py --slides-dir out/2026-11-26/slides --out-dir out/2026-11-26/work/render-05 --only 5 --timeout 300000`
- your concepts: `out/2026-11-26/briefs/slide-05.concepts.md`
- `@@ASSETS@@` resolves to `assets/` at render time. All scratch stays inside `out/2026-11-26/`; never write under any .claude directory.

## The neighbours
- frame before: UP TO. Know: in testing, data volume fell by up to 30 percent and files by up to 73 percent, ceilings both. c6.
- frame after: THE ONE BLADE. Know: the Propulsion System Validator tracks an engine's remaining life on its own and recommends maintenance from the manual. c7 c8.

## What already ran, so do not repeat it
November 25th drew glass lungs, manila chart folders, a fanned report stack, a card drawer, a family under a live oak (people). November 24th drew a stitched aerial Gulf Coast subdivision, damaged roofs, a downed oak, a responder at a tailgate (wonder). November 22nd drew cutaway exam rooms, a stethoscope wall, studio benches, exam paper and an open binder (explainer). November 21st drew a tracked rover on rubble (win). Judges lately charged: stray floating cubes beside a drawer, lumpy clasped hands, kit people from behind reading as mannequins, a dark wash reading as a plate behind the close's type, type crossing drawer pulls, a share drawing unreadable at feed size, a close repeating the cover, flat face on elevations, top down trays reading as charts, missing contact shadows, sky banding behind headlines, uncountable units at feed size, a hero under a tenth of the frame, "drawn to illustrate" closing eight deks. Place your type where THIS picture leaves quiet; neighbours put theirs elsewhere.
