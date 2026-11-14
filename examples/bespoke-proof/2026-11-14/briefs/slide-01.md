# Slide brief, frame 1 of 9, 2026-11-14 (bespoke proof)

**You are the artist for this frame only.** Read `knowledge/carousel/BESPOKE.md` and `.claude/agents/carousel-slide-artist.md` first.

## The beat
The cover. A very large promise that does not exist yet: over $19 million for a computing cluster in Lubbock that is not built. The reader should feel the size of the money and the emptiness of the thing, and want to swipe.

## The copy (fixed)
- kicker: `Texas Tech, Lubbock`
- counter: `01 / 09`
- headline (verbatim): `Over $19 million for a cluster not built yet`
- dek (verbatim, see the one exception below): `The state's chip fund will help Texas Tech set up a computing cluster in Lubbock, the university said on November 13th. One wafer stands for $1 million. The boat is drawn to illustrate and has no far end.`
- labels the shipped frame carried (optional, keep any you use verbatim): []
- claim ids (the `src` furniture): `c1 c2 c3 c4`

**The one exception.** A dek sentence that only describes the picture ("drawn to illustrate", "one wafer stands for $1 million", "the boat ... has no far end", "twelve wafers, capped at both ends") must describe YOUR picture truthfully. Rewrite only those sentences to fit what you draw, keep "drawn to illustrate", add no number, date, name or claim the copy does not already carry. Every other sentence stays word for word. If you keep the deck's unit (one wafer stands for $1 million), keep its sentence.

## The figures (window.FIG, exactly)
`{"nov_wafers": 19, "pitch_mm": 16}`

What the art must carry: the hook. Over is a floor, not an exact figure, so nothing drawn may imply exactly 19 or a known total. Every count you draw is computed from window.FIG in your code with a check that throws on a mismatch.

## The spine
- chassis: `assets/js/deck/2026-11-14-waferbench-bespoke.js` (declares `bespoke: true`, LOOK V2 tone `explainer`, accent `#22d3ee` meaning the November award and nothing else). Load it after `txdeck.js` and `txlook.js`, as the worked slides do.
- shared models you MAY use (never must): `wafer`, `wafer_boat`, `lab_bench` from the chassis's `installKit`.
- type faces, counter, kicker, site line and `TXDECK.finish` are fixed. Everything else is yours.
- file: `examples/bespoke-proof/2026-11-14/slides/slide-01.html`
- your render dir: `examples/bespoke-proof/2026-11-14/work/render-01` (yours alone)
- your concepts: `examples/bespoke-proof/2026-11-14/briefs/slide-01.concepts.md`
- `@@ASSETS@@` resolves to `assets/` at render time, as in the worked slides.

## The neighbours
- frame before: (none, this is the cover).
- frame after: Where and through whom.

## What already ran, so do not repeat it
The shipped Nov 14 deck and the look v2 proof (`examples/look-v2-proof/2026-11-14/slides/slide-01.html`) drew THIS beat as: the same wafer boat on the same lab bench under the same light, headline top left at y 150, art in the lower half. Every frame of both decks did the same. Your frame must not be a wafer boat on a bench with the type top left, unless your concept makes a far stronger case than that and you say why in your concepts file. The last four decks before it were dark staged scenes of kit objects (cable reels, city limit signs, crates, pallets).
