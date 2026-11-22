# Slide brief, frame 6 of 9, 2026-11-21 (BESPOKE, LOOK V2, tone WIN)

**You are the artist for this frame only.** Read `knowledge/carousel/BESPOKE.md`, `.claude/agents/carousel-slide-artist.md`, the LOOK V2 section of `CLAUDE.md` and `knowledge/carousel/ARSENAL.md` first. The deck plan is `out/2026-11-21/storyboard.md` (your dossier is its slide 6 yaml block, which carries your acceptance list; the CRAFT PLAN row is your starting concept). Claims are `out/2026-11-21/claims.json`.

## The story in one line
TEEX staged the finals of DARPA's Triage Challenge at Disaster City in College Station, November 5th to 13th, a 52 acre mock community built to collapse. Autonomous drones and ground robots worked alongside human medics, locating simulated casualties, reading vital signs from a distance and relaying the data to the medics. RoboScout won the Systems competition and $1.5 million, Disruptors the Data competition and $1 million, out of more than $3 million. DARPA's director said human machine teams outperform every approach, then said that is not enough. TRIAGE-X, for systems that deliver an antidote, is open until November 25th. The deck's argument is THE HANDOFF: one lime link shows what the machine hands the medic. RULES: no source calls these systems AI, so never write AI. Every casualty is simulated, a role player in mock makeup: never draw a real injury, blood or gore, never imply a real patient or a real disaster. Every machine is drawn to illustrate, to no maker's or team's design, no logos, no DARPA or TEEX seal, no railroad name. People are never likenesses: no face turned to camera, no face over a fifth of the frame, keep them at distance, from behind, occluded or cropped (kit people read as mannequins up close, which judges charged on the last five decks).

## The beat
THE FIELD. Know: Make a crowd countable without a face, more than 100 people. c12.
Planned picture (a strong starting concept, not a cage; pitch three and you may beat it): one hundred laminated badges on woven lanyards hanging from hooks on a perforated board in a tent, ten rows of ten, with one more badge cut by the right edge for 'more than'.
Camera: MEDIUM, orthographic three quarter onto the board.
Planned type seat: bottom band over the tent floor.

## The copy (fixed)
- kicker: `The field`
- counter: `06 / 09`
- headline (verbatim): `More than 100 people competed`
- dek (verbatim, except the one exception below): `Participants came from the U.S. military, universities, tech companies and startups. One badge stands for one participant, drawn to illustrate.`
- labels: [] (tone pills from TXLOOK.css, never lime unless the label marks the handoff link itself)
- claim ids (the `src` furniture): `c12`

**The one exception.** A dek sentence that only describes the picture ("drawn to illustrate", "one badge stands for one participant") must describe YOUR picture truthfully. Rewrite only that sentence, keep "drawn to illustrate", add no number, date, name or claim. Every other sentence stays word for word. House rules on any word you set: no em or en dashes, no colons or semicolons, no first person, can't never cannot, no sentence opening with And or But, straight quotes, banned words gap, gaps, matters, pattern, patterns.

## The figures (window.FIG, exactly)
`{"participants": 100}`
Every count or length you draw is computed from window.FIG in your code with a check that throws on a mismatch.

## The spine
- chassis: `assets/js/deck/2026-11-21-handoff-bespoke.js` (declares `bespoke: true`, LOOK V2 tone `win`, accent lime `#a3e635` meaning WHAT THE MACHINE HANDS THE MEDIC and nothing else). Load it after `txdeck.js` and `txlook.js`, exactly as `out/2026-11-21/test/probe-shape.html` loads it (copy that file's head and boot shape, never its picture). Note `CH.develop(await TXT.snapshot(R, { stage: false }), gl)` and `TXDECK.finish(cx)` last.
- accent on this frame: NONE. This frame carries no lime at all.. Money is brass (CH.BRASS), never lime. The rover is teal powder coat (CH.ROVER).
- WIN tone: deep blue sky to pale horizon, butter key, teal fill, mint rim. Shadows lean teal, never black. No dark room, no black type band. Seat type with `CH.seat`, footer with `TXLOOK.footWash`. A night frame stays deep teal and violet, never black.
- chassis models (installed by CH.boot; read their notes in the chassis): triage_rover (tracked, 0.86 x 0.95 x 0.98 m, options pan, tilt, mast, explode 0 to 1, lamp, grime, coat; userData.radio is where the lime link starts, userData.lens the standoff lens, userData.head, userData.stages), rubble_pile (options w, d, h, seed, section:true for a sectioned pile cut on z = 0 with a braced pocket, userData.pocket and userData.top, pocket height), survey_quad and flight_board (carried from November 20th). Plus every kit model in ARSENAL (person, pickup, live_oak, drone_dock, vtol_drone, suv, conference_table, laptop and more). K.make merges a model's `options` as defaults, so pass real values. The chassis models are basic geometry: REFINE their look inside your own frame (bevels, materials, wear, better track belts, more parts) as the November 20th artists did, but never edit the chassis file. Anything else your picture needs you build in your own frame, at true size in metres, never as a bare primitive.
- a chassis probe render (`out/2026-11-21/test/render/slide-01.png`) shows the rover, its exploded mast and both rubble modes build.
- type faces, counter, kicker, site line and `TXDECK.finish` are fixed. Everything else is yours.
- file: `out/2026-11-21/slides/slide-06.html`
- your render dir: `out/2026-11-21/work/render-06` (yours alone): `python3 .claude/skills/carousel-engine/render.py --slides-dir out/2026-11-21/slides --out-dir out/2026-11-21/work/render-06 --only 6 --timeout 300000`
- your concepts: `out/2026-11-21/briefs/slide-06.concepts.md`
- `@@ASSETS@@` resolves to `assets/` at render time. All scratch stays inside `out/2026-11-21/`; never write under any .claude directory.

## The neighbours
- frame before: NIGHT COURSE. Give the reader the tension of the night course, a machine still working while the people around it duck. c27 c28 c16.
- frame after: THE PURSE. Make the money weigh something, and let a reader compare the two wins by eye. c12 c3 c23.

## What already ran, so do not repeat it
November 20th drew a survey quadcopter on a ridge, its frosted twin, a clay track tablet, a lab with laptops and a loupe (people tone). November 19th drew sort glass, flies, a tube rack and a phone on a porch (wonder). November 18th a survey satellite and stake grids (explainer). November 17th a scoring machine. Judges lately charged: a puck stem floating above its body, the top 40 percent flat and empty, a wash seam behind a headline, subjects small in the lower half seen from high and far, walls filling the top half, flat face on elevations reading as UI, top down trays reading as charts, capsule people and mannequins, soft kit hands, objects floating with no contact shadow, sky banding behind headlines, uncountable units at feed size. Place your type where THIS picture leaves quiet; neighbours put theirs elsewhere.
