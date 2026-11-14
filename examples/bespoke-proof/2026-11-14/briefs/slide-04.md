# Slide brief, frame 4 of 9, 2026-11-14 (bespoke proof)

**You are the artist for this frame only.** Read `knowledge/carousel/BESPOKE.md` and `.claude/agents/carousel-slide-artist.md` first.

## The beat
The match. Texas Tech will match the state's $12 million, so the clean room project is $24 million. The reader should see two equal halves making one whole, the state's and the university's.

## The copy (fixed)
- kicker: `Texas Semiconductor Innovation Fund`
- counter: `04 / 09`
- headline (verbatim): `Texas Tech will match it, for a $24 million project`
- dek (verbatim, see the one exception below): `The university will match the state's funding, bringing the clean room project to $24 million. The state's twelve wafers sit in a quartz boat and Texas Tech's twelve in a dark carbide boat. Drawn to illustrate.`
- labels the shipped frame carried (optional, keep any you use verbatim): ["state", "Texas Tech"]
- claim ids (the `src` furniture): `c15 c16`

**The one exception.** A dek sentence that only describes the picture ("drawn to illustrate", "one wafer stands for $1 million", "the boat ... has no far end", "twelve wafers, capped at both ends") must describe YOUR picture truthfully. Rewrite only those sentences to fit what you draw, keep "drawn to illustrate", add no number, date, name or claim the copy does not already carry. Every other sentence stays word for word. If you keep the deck's unit (one wafer stands for $1 million), keep its sentence.

## The figures (window.FIG, exactly)
`{"jan_wafers": 12, "match_wafers": 12, "pitch_mm": 16}`

What the art must carry: two equal halves of 12 and 12, distinguishable as state and Texas Tech. Every count you draw is computed from window.FIG in your code with a check that throws on a mismatch.

## The spine
- chassis: `assets/js/deck/2026-11-14-waferbench-bespoke.js` (declares `bespoke: true`, LOOK V2 tone `explainer`, accent `#22d3ee` meaning the November award and nothing else). Load it after `txdeck.js` and `txlook.js`, as the worked slides do.
- shared models you MAY use (never must): `wafer`, `wafer_boat`, `lab_bench` from the chassis's `installKit`.
- type faces, counter, kicker, site line and `TXDECK.finish` are fixed. Everything else is yours.
- file: `examples/bespoke-proof/2026-11-14/slides/slide-04.html`
- your render dir: `examples/bespoke-proof/2026-11-14/work/render-04` (yours alone)
- your concepts: `examples/bespoke-proof/2026-11-14/briefs/slide-04.concepts.md`
- `@@ASSETS@@` resolves to `assets/` at render time, as in the worked slides.

## The neighbours
- frame before: January, the first award: $12 million toward a clean room for semiconductor work.
- frame after: May, the second award: roughly $4.

## What already ran, so do not repeat it
The shipped Nov 14 deck and the look v2 proof (`examples/look-v2-proof/2026-11-14/slides/slide-04.html`) drew THIS beat as: the same wafer boat on the same lab bench under the same light, headline top left at y 150, art in the lower half. Every frame of both decks did the same. Your frame must not be a wafer boat on a bench with the type top left, unless your concept makes a far stronger case than that and you say why in your concepts file. The last four decks before it were dark staged scenes of kit objects (cable reels, city limit signs, crates, pallets).
