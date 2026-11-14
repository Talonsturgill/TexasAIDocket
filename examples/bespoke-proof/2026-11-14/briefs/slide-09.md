# Slide brief, frame 9 of 9, 2026-11-14 (bespoke proof)

**You are the artist for this frame only.** Read `knowledge/carousel/BESPOKE.md` and `.claude/agents/carousel-slide-artist.md` first.

## The beat
The close. The announcement gives no install or completion date. The reader should be left with the open question: when does Texas Tech put a date on it?

## The copy (fixed)
- kicker: `Texas Tech, Lubbock`
- counter: `09 / 09`
- headline (verbatim): `No install date announced`
- dek (verbatim, see the one exception below): `Texas Tech's November 13th announcement says the award will help establish the cluster. It gives no install or completion date. The plate is drawn to illustrate.`
- labels the shipped frame carried (optional, keep any you use verbatim): ["AWARD", "over $19 million", "CHIPS, PER THE DEAN", "newest generation, Nvidia", "IN SERVICE"]
- claim ids (the `src` furniture): `c4 c1 c2 c8`

**The one exception.** A dek sentence that only describes the picture ("drawn to illustrate", "one wafer stands for $1 million", "the boat ... has no far end", "twelve wafers, capped at both ends") must describe YOUR picture truthfully. Rewrite only those sentences to fit what you draw, keep "drawn to illustrate", add no number, date, name or claim the copy does not already carry. Every other sentence stays word for word. If you keep the deck's unit (one wafer stands for $1 million), keep its sentence.

## The figures (window.FIG, exactly)
`{"nov_wafers": 19}`

What the art must carry: an absence: an empty date, an unfinished thing. Nothing drawn may imply a date. Every count you draw is computed from window.FIG in your code with a check that throws on a mismatch.

## The spine
- chassis: `assets/js/deck/2026-11-14-waferbench-bespoke.js` (declares `bespoke: true`, LOOK V2 tone `explainer`, accent `#22d3ee` meaning the November award and nothing else). Load it after `txdeck.js` and `txlook.js`, as the worked slides do.
- shared models you MAY use (never must): `wafer`, `wafer_boat`, `lab_bench` from the chassis's `installKit`.
- type faces, counter, kicker, site line and `TXDECK.finish` are fixed. Everything else is yours.
- file: `examples/bespoke-proof/2026-11-14/slides/slide-09.html`
- your render dir: `examples/bespoke-proof/2026-11-14/work/render-09` (yours alone)
- your concepts: `examples/bespoke-proof/2026-11-14/briefs/slide-09.concepts.md`
- `@@ASSETS@@` resolves to `assets/` at render time, as in the worked slides.

## The neighbours
- frame before: The chips.
- frame after: (none, this is the close).

## What already ran, so do not repeat it
The shipped Nov 14 deck and the look v2 proof (`examples/look-v2-proof/2026-11-14/slides/slide-09.html`) drew THIS beat as: the same wafer boat on the same lab bench under the same light, headline top left at y 150, art in the lower half. Every frame of both decks did the same. Your frame must not be a wafer boat on a bench with the type top left, unless your concept makes a far stronger case than that and you say why in your concepts file. The last four decks before it were dark staged scenes of kit objects (cable reels, city limit signs, crates, pallets).
