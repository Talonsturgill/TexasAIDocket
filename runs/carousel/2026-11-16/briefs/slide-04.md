# Slide brief, frame 4 of 9, 2026-11-16 (carousel no. 79, BESPOKE, LOOK V2)

**You are the artist for this frame only.** Read `knowledge/carousel/BESPOKE.md`, `.claude/agents/carousel-slide-artist.md`, the LOOK V2 section of `CLAUDE.md` and `knowledge/carousel/ARSENAL.md` first. The deck plan is `out/2026-11-16/storyboard.md` (your dossier is its slide 4 yaml block, which carries your acceptance list). Claims are `out/2026-11-16/claims.json`.

## The beat
The clinician. 18 years of listening to veterans, without drawing her.
Planned picture (a strong starting concept, not a cage; you pitch three and may beat it): an oak index card drawer pulled open on a desk, its guide card blocks counted one per year Norman has worked with veterans. Camera: MACRO, eye 0.25 m, raking along a desk top, fov 30.

## The copy (fixed)
- kicker: `The clinician`
- counter: `04 / 09`
- headline (verbatim): `Rocio Norman has worked with veterans for 18 years`
- dek (verbatim, except the one exception below): `She is a speech language pathologist and one of the researchers on the grant. One block of cards per year, drawn to illustrate.`
- labels (optional, keep any you use verbatim): []
- claim ids (the `src` furniture): `c5 c2`

**The one exception.** A dek sentence that only describes the picture ("drawn to illustrate", "one block per year") must describe YOUR picture truthfully. Rewrite only that sentence, keep "drawn to illustrate", add no number, date, name or claim. Every other sentence stays word for word. House rules on any word you set: no em or en dashes, no colons or semicolons, no first person, can't never cannot, no sentence opening with And or But, straight quotes, banned words gap, gaps, matters, pattern, patterns.

## The figures (window.FIG, exactly)
`{"norman_years": 18}`
Every count you draw is computed from window.FIG in your code with a check that throws on a mismatch.

## The spine
- chassis: `assets/js/deck/2026-11-16-voicebench-bespoke.js` (declares `bespoke: true`, LOOK V2 tone `explainer`, accent dusk gold `#e0956a` meaning THE VETERAN'S OWN SPOKEN WORDS and nothing else). Load it after `txdeck.js` and `txlook.js`, exactly as `runs/carousel/2026-11-15/slides/slide-01.html` loads its chassis (copy that file's head and boot shape, never its picture).
- this frame carries NO gold accent anywhere.
- shared models you MAY use (never must): `voice_ribbon` (a symmetric gold waveform strip; options length, amp, thick, seed, cycles, paper), `vernier_caliper` (open = jaw gap in m, no readout), `gauge_head` (dark smoked window, no needle; userData.slotY for a ribbon) from the chassis's installKit, plus every kit model in ARSENAL.
- type faces, counter, kicker, site line and `TXDECK.finish` are fixed. Everything else is yours. LOOK V2: colour, never black, shadows lean indigo. Seat type with `CH.seat`, footer with `TXLOOK.footWash`.
- file: `out/2026-11-16/slides/slide-04.html`
- your render dir: `out/2026-11-16/work/render-04` (yours alone): `python3 .claude/skills/carousel-engine/render.py --slides-dir out/2026-11-16/slides --out-dir out/2026-11-16/work/render-04 --only 4 --timeout 300000`
- your concepts: `out/2026-11-16/briefs/slide-04.concepts.md`
- `@@ASSETS@@` resolves to `assets/` at render time.

## The neighbours
- frame before: The tests. Built for two other conditions, a sieve sized for big stones while the fine grains of a voice fall through.
- frame after: The recordings. Two stories already set down, at several points in treatment.

## What already ran, so do not repeat it
Yesterday's deck (no. 78, people tone) was school desks, lockers, binders and a board room on studio sweeps and interiors; its judges charged a wall filling the top half with the subject cropped, sky banding behind a headline, flat pale trousers, wavy kit wood, an orange room fighting the accent. The fourteen decks before it put the headline top left at y 150 with the art under it on every frame. Place your type where THIS picture leaves quiet. Integrity: no result, accuracy, sample size or veteran count exists; never draw a reading, a fill level, a score or a connection. No real VA building, clinic or person.
