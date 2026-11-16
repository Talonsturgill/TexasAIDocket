# Slide brief, frame 8 of 9, 2026-11-16 (carousel no. 79, BESPOKE, LOOK V2)

**You are the artist for this frame only.** Read `knowledge/carousel/BESPOKE.md`, `.claude/agents/carousel-slide-artist.md`, the LOOK V2 section of `CLAUDE.md` and `knowledge/carousel/ARSENAL.md` first. The deck plan is `out/2026-11-16/storyboard.md` (your dossier is its slide 8 yaml block, which carries your acceptance list). Claims are `out/2026-11-16/claims.json`.

## The beat
The question. Features against four named symptoms, nothing connected yet.
Planned picture (a strong starting concept, not a cage; you pitch three and may beat it): a brushed aluminium patch panel on limestone with four feature terminals and four symptom terminals, indigo braided leads hanging loose and unplugged. Camera: MEDIUM, orthographic relief raked from the upper right.

## The copy (fixed)
- kicker: `The question`
- counter: `08 / 09`
- headline (verbatim): `First, learn whether automation can spot the differences`
- dek (verbatim, except the one exception below): `Then see how they relate to anxiety, post traumatic stress, depression and sleep difficulties. The leads hang unplugged, drawn to illustrate.`
- labels (optional, keep any you use verbatim): ["Coherence", "Emotional tone", "Organization", "Level of detail", "Anxiety", "Post traumatic stress", "Depression", "Sleep difficulties"]
- claim ids (the `src` furniture): `c11`

**The one exception.** A dek sentence that only describes the picture ("drawn to illustrate", "one block per year") must describe YOUR picture truthfully. Rewrite only that sentence, keep "drawn to illustrate", add no number, date, name or claim. Every other sentence stays word for word. House rules on any word you set: no em or en dashes, no colons or semicolons, no first person, can't never cannot, no sentence opening with And or But, straight quotes, banned words gap, gaps, matters, pattern, patterns.

## The figures (window.FIG, exactly)
`{"symptoms_named": 4, "features_named": 4}`
Every count you draw is computed from window.FIG in your code with a check that throws on a mismatch.

## The spine
- chassis: `assets/js/deck/2026-11-16-voicebench-bespoke.js` (declares `bespoke: true`, LOOK V2 tone `explainer`, accent dusk gold `#e0956a` meaning THE VETERAN'S OWN SPOKEN WORDS and nothing else). Load it after `txdeck.js` and `txlook.js`, exactly as `runs/carousel/2026-11-15/slides/slide-01.html` loads its chassis (copy that file's head and boot shape, never its picture).
- this frame carries NO gold accent anywhere.
- shared models you MAY use (never must): `voice_ribbon` (a symmetric gold waveform strip; options length, amp, thick, seed, cycles, paper), `vernier_caliper` (open = jaw gap in m, no readout), `gauge_head` (dark smoked window, no needle; userData.slotY for a ribbon) from the chassis's installKit, plus every kit model in ARSENAL.
- type faces, counter, kicker, site line and `TXDECK.finish` are fixed. Everything else is yours. LOOK V2: colour, never black, shadows lean indigo. Seat type with `CH.seat`, footer with `TXLOOK.footWash`.
- file: `out/2026-11-16/slides/slide-08.html`
- your render dir: `out/2026-11-16/work/render-08` (yours alone): `python3 .claude/skills/carousel-engine/render.py --slides-dir out/2026-11-16/slides --out-dir out/2026-11-16/work/render-08 --only 8 --timeout 300000`
- your concepts: `out/2026-11-16/briefs/slide-08.concepts.md`
- `@@ASSETS@@` resolves to `assets/` at render time.

## The neighbours
- frame before: The plan, the showstopper. Four named features, four dark instruments, nothing measured.
- frame after: Close. A one year pilot, federal grants only if it finds something, a tool to support clinicians.

## What already ran, so do not repeat it
Yesterday's deck (no. 78, people tone) was school desks, lockers, binders and a board room on studio sweeps and interiors; its judges charged a wall filling the top half with the subject cropped, sky banding behind a headline, flat pale trousers, wavy kit wood, an orange room fighting the accent. The fourteen decks before it put the headline top left at y 150 with the art under it on every frame. Place your type where THIS picture leaves quiet. Integrity: no result, accuracy, sample size or veteran count exists; never draw a reading, a fill level, a score or a connection. No real VA building, clinic or person.
