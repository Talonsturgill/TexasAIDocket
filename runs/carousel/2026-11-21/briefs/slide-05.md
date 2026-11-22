# Slide brief, frame 5 of 9, 2026-11-21 (BESPOKE, LOOK V2, tone WIN)

**You are the artist for this frame only.** Read `knowledge/carousel/BESPOKE.md`, `.claude/agents/carousel-slide-artist.md`, the LOOK V2 section of `CLAUDE.md` and `knowledge/carousel/ARSENAL.md` first. The deck plan is `out/2026-11-21/storyboard.md` (your dossier is its slide 5 yaml block, which carries your acceptance list; the CRAFT PLAN row is your starting concept). Claims are `out/2026-11-21/claims.json`.

## The story in one line
TEEX staged the finals of DARPA's Triage Challenge at Disaster City in College Station, November 5th to 13th, a 52 acre mock community built to collapse. Autonomous drones and ground robots worked alongside human medics, locating simulated casualties, reading vital signs from a distance and relaying the data to the medics. RoboScout won the Systems competition and $1.5 million, Disruptors the Data competition and $1 million, out of more than $3 million. DARPA's director said human machine teams outperform every approach, then said that is not enough. TRIAGE-X, for systems that deliver an antidote, is open until November 25th. The deck's argument is THE HANDOFF: one lime link shows what the machine hands the medic. RULES: no source calls these systems AI, so never write AI. Every casualty is simulated, a role player in mock makeup: never draw a real injury, blood or gore, never imply a real patient or a real disaster. Every machine is drawn to illustrate, to no maker's or team's design, no logos, no DARPA or TEEX seal, no railroad name. People are never likenesses: no face turned to camera, no face over a fifth of the frame, keep them at distance, from behind, occluded or cropped (kit people read as mannequins up close, which judges charged on the last five decks).

## The beat
NIGHT COURSE. Know: Give the reader the tension of the night course, a machine still working while the people around it duck. c27 c28 c16.
Planned picture (a strong starting concept, not a cage; pitch three and you may beat it): the triage rover in silhouette on a rutted dirt lane at night, earth filled barrier units ahead with two helmets just showing at one end, a controlled burst blooming warm orange through drifting smoke far behind, one lime link from the rover's mast through the smoke to a medic in cover at frame left.
Camera: WIDE, camera low at 0.6 m behind and beside the rover, 40 mm equivalent.
Planned type seat: lower left over the dark lane.

## The copy (fixed)
- kicker: `Night course`
- counter: `05 / 09`
- headline (verbatim): `It searched through the blast`
- dek (verbatim, except the one exception below): `On the Human Machine Teaming night course a robot searched for casualties during a controlled explosion while role players took cover. Each team worked with assigned medics. The course simulated an attack on a forward operating base.`
- labels: [] (tone pills from TXLOOK.css, never lime unless the label marks the handoff link itself)
- claim ids (the `src` furniture): `c27 c28 c16`

**The one exception.** A dek sentence that only describes the picture ("drawn to illustrate", "one badge stands for one participant") must describe YOUR picture truthfully. Rewrite only that sentence, keep "drawn to illustrate", add no number, date, name or claim. Every other sentence stays word for word. House rules on any word you set: no em or en dashes, no colons or semicolons, no first person, can't never cannot, no sentence opening with And or But, straight quotes, banned words gap, gaps, matters, pattern, patterns.

## The figures (window.FIG, exactly)
`{}`
Every count or length you draw is computed from window.FIG in your code with a check that throws on a mismatch. This frame draws no count, so window.FIG stays {} and no count is drawn.

## The spine
- chassis: `assets/js/deck/2026-11-21-handoff-bespoke.js` (declares `bespoke: true`, LOOK V2 tone `win`, accent lime `#a3e635` meaning WHAT THE MACHINE HANDS THE MEDIC and nothing else). Load it after `txdeck.js` and `txlook.js`, exactly as `out/2026-11-21/test/probe-shape.html` loads it (copy that file's head and boot shape, never its picture). Note `CH.develop(await TXT.snapshot(R, { stage: false }), gl)` and `TXDECK.finish(cx)` last.
- accent on this frame: the lime handoff link only (an emissive tube or lit line from the machine radio, CH.ACCENT), under 8 percent of the frame. Money is brass (CH.BRASS), never lime. The rover is teal powder coat (CH.ROVER).
- WIN tone: deep blue sky to pale horizon, butter key, teal fill, mint rim. Shadows lean teal, never black. No dark room, no black type band. Seat type with `CH.seat`, footer with `TXLOOK.footWash`. A night frame stays deep teal and violet, never black.
- chassis models (installed by CH.boot; read their notes in the chassis): triage_rover (tracked, 0.86 x 0.95 x 0.98 m, options pan, tilt, mast, explode 0 to 1, lamp, grime, coat; userData.radio is where the lime link starts, userData.lens the standoff lens, userData.head, userData.stages), rubble_pile (options w, d, h, seed, section:true for a sectioned pile cut on z = 0 with a braced pocket, userData.pocket and userData.top, pocket height), survey_quad and flight_board (carried from November 20th). Plus every kit model in ARSENAL (person, pickup, live_oak, drone_dock, vtol_drone, suv, conference_table, laptop and more). K.make merges a model's `options` as defaults, so pass real values. The chassis models are basic geometry: REFINE their look inside your own frame (bevels, materials, wear, better track belts, more parts) as the November 20th artists did, but never edit the chassis file. Anything else your picture needs you build in your own frame, at true size in metres, never as a bare primitive.
- a chassis probe render (`out/2026-11-21/test/render/slide-01.png`) shows the rover, its exploded mast and both rubble modes build.
- type faces, counter, kicker, site line and `TXDECK.finish` are fixed. Everything else is yours.
- file: `out/2026-11-21/slides/slide-05.html`
- your render dir: `out/2026-11-21/work/render-05` (yours alone): `python3 .claude/skills/carousel-engine/render.py --slides-dir out/2026-11-21/slides --out-dir out/2026-11-21/work/render-05 --only 5 --timeout 300000`
- your concepts: `out/2026-11-21/briefs/slide-05.concepts.md`
- `@@ASSETS@@` resolves to `assets/` at render time. All scratch stays inside `out/2026-11-21/`; never write under any .claude directory.

## The neighbours
- frame before: THE JOB. Make the idea click, the machine must find a person it can't reach, read them and tell a human. c10 c18 c14 c15.
- frame after: THE FIELD. Make a crowd countable without a face, more than 100 people. c12.

## What already ran, so do not repeat it
November 20th drew a survey quadcopter on a ridge, its frosted twin, a clay track tablet, a lab with laptops and a loupe (people tone). November 19th drew sort glass, flies, a tube rack and a phone on a porch (wonder). November 18th a survey satellite and stake grids (explainer). November 17th a scoring machine. Judges lately charged: a puck stem floating above its body, the top 40 percent flat and empty, a wash seam behind a headline, subjects small in the lower half seen from high and far, walls filling the top half, flat face on elevations reading as UI, top down trays reading as charts, capsule people and mannequins, soft kit hands, objects floating with no contact shadow, sky banding behind headlines, uncountable units at feed size. Place your type where THIS picture leaves quiet; neighbours put theirs elsewhere.
