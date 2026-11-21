# Slide brief, frame 5 of 9, 2026-11-20 (BESPOKE, LOOK V2, tone PEOPLE)

**You are the artist for this frame only.** Read `knowledge/carousel/BESPOKE.md`, `.claude/agents/carousel-slide-artist.md`, the LOOK V2 section of `CLAUDE.md` and `knowledge/carousel/ARSENAL.md` first. The deck plan is `out/2026-11-20/storyboard.md` (your dossier is its slide 5 yaml block, which carries your acceptance list; the CRAFT PLAN row is your starting concept). Claims are `out/2026-11-20/claims.json`.

## The story in one line
East Texas A&M researchers in Commerce tested AI that flags a drone fed false GPS, using only the drone's own motion sensors (how fast, which way, over how much time) and no GPS readings, on 96 recorded flights (42 normal, 54 spoofed), with 22 held back as the test. Given 10 readings, a model called Chronos scored 97.5% on one balanced measure. Nothing was flown live; running the check in flight is the next step. The deck's argument is TWO KINDS OF POSITION: what the drone is told is frosted periwinkle glass that casts NO shadow, what its own motion says it flew is amber and always casts a shadow. Never draw an alarm, a detection or the check running in flight. 97.5% is never accuracy and never a share of attacks caught. Never name a maker of Chronos. The ridge and valley is the release's own example, on no real place (no limestone ledges, no landmark, no road sign). No ETAMU, NSF or any logo or seal. People are drawn to illustrate, never likenesses: no face turned to camera, no face over a fifth of the frame.

## The beat
ITS OWN MOTION. Know: Make the idea click, the drone checks itself against its own motion and never asks the GPS. c4 c15.
Planned picture (a strong starting concept, not a cage; pitch three and you may beat it): a macro of the drone's flight controller board with its motion sensor chip, three amber machined arrows rising from the chip, the GPS puck unplugged and set aside in frosted glass at the frame edge.
Camera: MACRO, 90 mm equivalent at 0.15 m, raked three quarter.

## The copy (fixed)
- kicker: `Its own motion`
- counter: `05 / 09`
- headline (verbatim): `It never asks the GPS`
- dek (verbatim, except the one exception below): `The method reads the drone's own motion sensors for how fast it moves, in what direction and over how much time. It uses no GPS data. One arrow stands for each, drawn to illustrate.`
- labels: ["how fast", "which way", "how long"] (tone pills from TXLOOK.css; only a label on the amber subject may be amber)
- claim ids (the `src` furniture): `c4 c15`

**The one exception.** A dek sentence that only describes the picture ("drawn to illustrate", "one tile stands for one flight") must describe YOUR picture truthfully. Rewrite only that sentence, keep "drawn to illustrate", add no number, date, name or claim. Every other sentence stays word for word. House rules on any word you set: no em or en dashes, no colons or semicolons, no first person, can't never cannot, no sentence opening with And or But, straight quotes, banned words gap, gaps, matters, pattern, patterns.

## The figures (window.FIG, exactly)
`{}`
Every count or length you draw is computed from window.FIG in your code with a check that throws on a mismatch.

## The spine
- chassis: `assets/js/deck/2026-11-20-truetrack-bespoke.js` (declares `bespoke: true`, LOOK V2 tone `people`, accent amber `#ff9f1c` meaning MOTION THE DRONE ITSELF MEASURED and nothing else). Load it after `txdeck.js` and `txlook.js`, exactly as `out/2026-11-20/tmp/probe/slides/slide-01.html` loads it (copy that file's head and boot shape, never its picture). Note `CH.develop(await TXT.snapshot(R, { stage: false }), gl)`.
- accent on this frame: the three motion arrows are amber. The unplugged GPS puck is frosted glass.
- PEOPLE tone: periwinkle sky, apricot key, plum fill. Shadows lean plum and navy, never black. No dark room, no black type band. Seat type with `CH.seat`, footer with `TXLOOK.footWash`.
- THE SHADOW RULE: anything showing the reported (false) position is frosted periwinkle glass (`CH.GHOST`) with castShadow false. Anything real casts a shadow.
- chassis models (installed by CH.boot; read their notes in the chassis): survey_quad (options props 'still'|'spin'|'folded', lift m, open:true shows the flight_board, ghost:true for the frosted shadowless twin, legs, shell colour, lamp; userData.gps, .body, .camera, .board; about 0.70 m motor to motor, origin on the ground) and flight_board (36 mm board, userData.imu the motion sensor chip). Plus every kit model in ARSENAL (person, pickup, pasture, hill_country_terrain, mesquite, live_oak, conference_table, desk, laptop, monitor and more). K.make merges a model's `options` as defaults, so pass real values. You may refine a model's look in your own frame but never edit the chassis file.
- a chassis probe render (`out/2026-11-20/tmp/probe/render/slide-01.png`) shows every chassis model and mode builds.
- type faces, counter, kicker, site line and `TXDECK.finish` are fixed. Everything else is yours.
- file: `out/2026-11-20/slides/slide-05.html`
- your render dir: `out/2026-11-20/work/render-05` (yours alone): `python3 .claude/skills/carousel-engine/render.py --slides-dir out/2026-11-20/slides --out-dir out/2026-11-20/work/render-05 --only 5 --timeout 300000`
- your concepts: `out/2026-11-20/briefs/slide-05.concepts.md`
- `@@ASSETS@@` resolves to `assets/` at render time. All scratch stays inside `out/2026-11-20/`; never write under any .claude directory.

## The neighbours
- frame before: COMMERCE, TEXAS. Show who did this, students in Commerce, without inventing a face.
- frame after: 96 REAL FLIGHTS. Make the evidence physical and countable, 96 real flights, 54 of them lied to.

## What already ran, so do not repeat it
November 19th drew macro sort glass and flies, a tube rack on a bench, a bucket trap in brush, a relief map, glazed boxes, a fence road and a phone on a porch bench (wonder). November 18th drew a survey satellite, stake grids, an air column relief (explainer). November 17th a violet scoring machine and card drawer (watch). October 26th drew delivery drones and a dock in Round Rock, October 18th a survey quadcopter over brush. Judges lately charged: subjects small in the lower half seen from high and far, walls filling the top half, flat face on elevations reading as UI, top down trays reading as charts, capsule people and mannequins, soft kit hands, objects floating with no contact shadow, sky banding behind headlines, uncountable units at feed size, crawling insects reading as ants, a phone screen reading as blobs, a grid under half the frame in a void. Place your type where THIS picture leaves quiet; the planned seat for this frame is noted in the storyboard, and neighbours put theirs elsewhere.
