# Slide brief, frame 5 of 9, 2026-11-22 (BESPOKE, LOOK V2, tone EXPLAINER)

**You are the artist for this frame only.** Read `knowledge/carousel/BESPOKE.md`, `.claude/agents/carousel-slide-artist.md`, the LOOK V2 section of `CLAUDE.md` and `knowledge/carousel/ARSENAL.md` first. The deck plan is `out/2026-11-22/storyboard.md` (your dossier is its slide 5 yaml block, which carries your acceptance list; the CRAFT PLAN row is your starting concept). Claims are `out/2026-11-22/claims.json`.

## The story in one line
The IC² Institute and Dell Medical School at UT Austin announced the AI Learning Lab on October 20th, 2026. 80 Dell Med clinicians, a mix of faculty, residents and students, meet paid actors playing patients in live simulated encounters. Half have Claude to help diagnose. The other half rely on UpToDate with its AI capability disabled. Researcher Sookja Kang asks how quickly clinicians click on their AI tool, whether they accept AI output or interrogate it, and how much reasoning gets handed off as the diagnosis evolves. Researchers compare the groups with rubrics, observation and post encounter interviews. The release cites a 2026 AMA survey, 81% of doctors using AI against 38% in 2023. Results could help Dell Med and other schools decide how and when AI enters the curriculum. The deck's argument is THE FAIR TEST: two matched halves, one tool switched off, and three questions built as instruments at rest. RULES: NO RESULTS EXIST, so no frame shows or implies an outcome, a score, a faster or slower, a right or wrong diagnosis, or a better group. The patients are ACTORS and every room is drawn to illustrate, never Dell Med's real building. Claude and UpToDate appear in copy and pills only: no logo, no interface, no legible screen, a screen may glow and show nothing. People are never likenesses: no face turned to camera, no face over 2 percent of the frame, keep them from behind, in silhouette, at distance or cropped (kit people read as mannequins up close).

## The beat
QUESTION ONE. Know: how quickly do clinicians click on their AI tool. c9.
Planned picture (a strong starting concept, not a cage; pitch three and you may beat it): a worm's eye view eleven centimetres above a limestone desk looking down an anodised indigo timing rail whose brass graduation ridges pack tighter into the distance toward a laptop glowing plain cyan, a knurled carriage parked hard against the near zero stop, three small brass tabs at the rail's foot with the first one lit.
Camera and largest object: CLOSE, a chassis timing_rail, anodised indigo aluminium with brass ridges under a soft studio key and a cool rim, contact shadow on a limestone slab weathered at its edge, TXT.studio explainer.
Planned type seat: see the dossier's composition bands. Put the type where YOUR picture leaves quiet.

## The copy (fixed)
- kicker: `Question one`
- counter: `05 / 09`
- headline (verbatim): `How fast do they click?`
- dek (verbatim, except the one exception below): `Researcher Sookja Kang asks how quickly the clinicians click on their AI tool. The rail is drawn to illustrate and stands at zero.`
- labels: [] (tone pills from TXLOOK.css)
- claim ids (the `src` furniture): `c9`

**The one exception.** A dek sentence that only describes the picture ("drawn to illustrate", "one stethoscope stands for one clinician") must describe YOUR picture truthfully. Rewrite only that sentence, keep "drawn to illustrate", add no number, date, name or claim. Every other sentence stays word for word. House rules on any word you set: no em or en dashes, no colons or semicolons, no first person, can't never cannot, no sentence opening with And or But, straight quotes, banned words gap, gaps, matters, pattern, patterns.

## The figures (window.FIG, exactly)
`{"questions": 3}`
Every count or length you draw is computed from window.FIG in your code with a check that throws on a mismatch. Data in art for this frame: the number of brass question tabs equals FIG.questions and the first is lit, in the slide's own code.

## The spine
- chassis: `assets/js/deck/2026-11-22-fairtest-bespoke.js` (declares `bespoke: true`, LOOK V2 tone `explainer`, accent cyan `#22d3ee` meaning THE TOOL WITHIN REACH and nothing else, paired at equal intensity where both arms show). Load it after `txdeck.js` and `txlook.js`, exactly as `out/2026-11-22/test/slide-01.html` loads it (copy that file's head and boot shape, never its picture). Note `CH.develop(await TXT.snapshot(R, { stage: false }), gl)` and `TXDECK.finish(cx)` last.
- accent on this frame: YES. The far laptop glows CH.toolMat(K). The carriage is brass, never cyan. The first brass question tab is lit (brass, brighter), the others dull.
- EXPLAINER tone: a clear bright morning, cerulean over ice blue, a near white key, indigo fill. Shadows lean indigo, never black. No dark room, no black type band. Seat type with `CH.seat`, footer with `TXLOOK.footWash`. Grey mid tones fail value_register, so surfaces take saturated tone colour.
- chassis models (installed by CH.boot; read their notes in the chassis): exam_table (1.95 x 1.2 x 0.72 m, options back, vinyl, cabinet, paper, step; userData.seat is the seat top height; head at -x, drawers on +z), stethoscope (pose 'coiled' flat on a surface or 'hung' from a hook at its origin, tube colour), timing_rail (length, pitch, at; origin at the zero stop, rail along +x; userData.carriage), handoff_tray (at 0 = shuttle on the clinician's side +z, 1 = tool's side; filled; userData.shuttle), output_slip (annotated, seed, curl), paper_roll (length, tick; sheet unrolls along +x; userData.end). CH.toolMat(K) is the one tool glow material. Plus every kit model in ARSENAL (person with poses sit_read, read, stand, point; office_chair; desk; laptop; monitor; workstation_cart; student_desk; student_desk_rows; conference_table). K.make merges a model's options as defaults. The chassis models are basic geometry: REFINE their look inside your own frame (bevels, materials, wear, more parts) but never edit the chassis file. Anything else your picture needs you build in your own frame, at true size in metres, never as a bare primitive. A seated person must actually sit ON the seat (place by userData.seat), with contact.
- a chassis probe render (`out/2026-11-22/test/render/slide-01.png`) shows every chassis model builds.
- type faces, counter, kicker, site line and `TXDECK.finish` are fixed. Everything else is yours.
- file: `out/2026-11-22/slides/slide-05.html`
- your render dir: `out/2026-11-22/work/render-05` (yours alone): `python3 .claude/skills/carousel-engine/render.py --slides-dir out/2026-11-22/slides --out-dir out/2026-11-22/work/render-05 --only 5 --timeout 300000`
- your concepts: `out/2026-11-22/briefs/slide-05.concepts.md`
- `@@ASSETS@@` resolves to `assets/` at render time. All scratch stays inside `out/2026-11-22/`; never write under any .claude directory.

## The neighbours
- frame before: AI OFF. Know: the comparison half is not toolless, it is a real encyclopedia with its AI switched off. c5.
- frame after: QUESTION TWO. Know: do they accept the AI's output or interrogate it. c10.

## What already ran, so do not repeat it
November 21st drew a tracked rover on rubble, a staged town aerial, brass plate stacks, a pegboard of credentials and a data rail (win tone). November 20th drew a survey quadcopter on a ridge, a frosted twin, a clay tablet and a loupe (people). November 19th drew sort glass, flies and a tube rack (wonder). November 18th a survey satellite and stake grids (explainer). Judges lately charged: toy cubes on a flat sweep with labels doing the explaining and no scale cue, a part floating above its body, the top 40 percent flat and empty, walls filling the top half, flat face on elevations reading as UI, top down trays reading as charts, capsule people and mannequins, soft kit hands, objects with no contact shadow, sky banding behind headlines, uncountable units at feed size, a hero under a tenth of the frame. Place your type where THIS picture leaves quiet; neighbours put theirs elsewhere.
