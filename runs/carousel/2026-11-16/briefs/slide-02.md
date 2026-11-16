# Slide brief, frame 2 of 9, 2026-11-16 (carousel no. 79, BESPOKE, LOOK V2)

**You are the artist for this frame only.** Read `knowledge/carousel/BESPOKE.md`, `.claude/agents/carousel-slide-artist.md`, the LOOK V2 section of `CLAUDE.md` and `knowledge/carousel/ARSENAL.md` first. The deck plan is `out/2026-11-16/storyboard.md` (your dossier is its slide 2 yaml block, which carries your acceptance list). Claims are `out/2026-11-16/claims.json`.

## The beat
The problem. The words remain, finding them is hard, invisible at an ordinary table.
Planned picture (a strong starting concept, not a cage; you pitch three and may beat it): a warm family table by a window, one illustrative veteran in the foreground with a short gold ribbon that stops, others talking across in soft focus. Camera: MEDIUM, eye 1.15 m seated, over a shoulder, fov 38.

## The copy (fixed)
- kicker: `The struggle`
- counter: `02 / 09`
- headline (verbatim): `The words are there. Finding them is hard.`
- dek (verbatim, except the one exception below): `Many veterans Rocio Norman treated reported trouble finding words or keeping up in fast or noisy talk, even when standard tests showed no clear impairment. People drawn to illustrate.`
- labels (optional, keep any you use verbatim): []
- claim ids (the `src` furniture): `c16 c17`

**The one exception.** A dek sentence that only describes the picture ("drawn to illustrate", "one block per year") must describe YOUR picture truthfully. Rewrite only that sentence, keep "drawn to illustrate", add no number, date, name or claim. Every other sentence stays word for word. House rules on any word you set: no em or en dashes, no colons or semicolons, no first person, can't never cannot, no sentence opening with And or But, straight quotes, banned words gap, gaps, matters, pattern, patterns.

## The figures (window.FIG, exactly)
`{}`
This frame draws no count. Keep window.FIG = {}.

## The spine
- chassis: `assets/js/deck/2026-11-16-voicebench-bespoke.js` (declares `bespoke: true`, LOOK V2 tone `explainer`, accent dusk gold `#e0956a` meaning THE VETERAN'S OWN SPOKEN WORDS and nothing else). Load it after `txdeck.js` and `txlook.js`, exactly as `runs/carousel/2026-11-15/slides/slide-01.html` loads its chassis (copy that file's head and boot shape, never its picture).
- this frame MAY carry the accent, on the voice ribbon or a label naming the speech only.
- shared models you MAY use (never must): `voice_ribbon` (a symmetric gold waveform strip; options length, amp, thick, seed, cycles, paper), `vernier_caliper` (open = jaw gap in m, no readout), `gauge_head` (dark smoked window, no needle; userData.slotY for a ribbon) from the chassis's installKit, plus every kit model in ARSENAL.
- type faces, counter, kicker, site line and `TXDECK.finish` are fixed. Everything else is yours. LOOK V2: colour, never black, shadows lean indigo. Seat type with `CH.seat`, footer with `TXLOOK.footWash`.
- file: `out/2026-11-16/slides/slide-02.html`
- your render dir: `out/2026-11-16/work/render-02` (yours alone): `python3 .claude/skills/carousel-engine/render.py --slides-dir out/2026-11-16/slides --out-dir out/2026-11-16/work/render-02 --only 2 --timeout 300000`
- your concepts: `out/2026-11-16/briefs/slide-02.concepts.md`
- `@@ASSETS@@` resolves to `assets/` at render time.

## The neighbours
- frame before: Cover. A spoken story made solid, and an instrument not yet closed on it.
- frame after: The tests. Built for two other conditions, a sieve sized for big stones while the fine grains of a voice fall through.

## What already ran, so do not repeat it
Yesterday's deck (no. 78, people tone) was school desks, lockers, binders and a board room on studio sweeps and interiors; its judges charged a wall filling the top half with the subject cropped, sky banding behind a headline, flat pale trousers, wavy kit wood, an orange room fighting the accent. The fourteen decks before it put the headline top left at y 150 with the art under it on every frame. Place your type where THIS picture leaves quiet. Integrity: no result, accuracy, sample size or veteran count exists; never draw a reading, a fill level, a score or a connection. No real VA building, clinic or person.
