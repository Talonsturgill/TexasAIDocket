# Slide brief, frame 7 of 9, 2026-11-14 (bespoke proof)

**You are the artist for this frame only.** Read `knowledge/carousel/BESPOKE.md` and `.claude/agents/carousel-slide-artist.md` first.

## The beat
What the cluster is for. The project will combine AI with simulation data and lab results to shorten development cycles, including AI-enabled epitaxial growth of ultrawide-bandgap semiconductors. The reader should see crystal layers being grown and steered.

## The copy (fixed)
- kicker: `Texas Tech, Lubbock`
- counter: `07 / 09`
- headline (verbatim): `AI to steer how the crystals grow`
- dek (verbatim, see the one exception below): `The project will integrate AI with high-fidelity simulation data and experimental results, which the university says should shorten development cycles. Planned work includes AI-enabled epitaxial growth of ultrawide-bandgap semiconductors. Drawn to illustrate.`
- labels the shipped frame carried (optional, keep any you use verbatim): []
- claim ids (the `src` furniture): `c6 c7 c11`

**The one exception.** A dek sentence that only describes the picture ("drawn to illustrate", "one wafer stands for $1 million", "the boat ... has no far end", "twelve wafers, capped at both ends") must describe YOUR picture truthfully. Rewrite only those sentences to fit what you draw, keep "drawn to illustrate", add no number, date, name or claim the copy does not already carry. Every other sentence stays word for word. If you keep the deck's unit (one wafer stands for $1 million), keep its sentence.

## The figures (window.FIG, exactly)
`{}`

What the art must carry: epitaxy: atomic layers growing on a crystal, terraces and islands of a new layer. Name no specific material. Every count you draw is computed from window.FIG in your code with a check that throws on a mismatch.

## The spine
- chassis: `assets/js/deck/2026-11-14-waferbench-bespoke.js` (declares `bespoke: true`, LOOK V2 tone `explainer`, accent `#22d3ee` meaning the November award and nothing else). Load it after `txdeck.js` and `txlook.js`, as the worked slides do.
- shared models you MAY use (never must): `wafer`, `wafer_boat`, `lab_bench` from the chassis's `installKit`.
- type faces, counter, kicker, site line and `TXDECK.finish` are fixed. Everything else is yours.
- file: `examples/bespoke-proof/2026-11-14/slides/slide-07.html`
- your render dir: `examples/bespoke-proof/2026-11-14/work/render-07` (yours alone)
- your concepts: `examples/bespoke-proof/2026-11-14/briefs/slide-07.concepts.md`
- `@@ASSETS@@` resolves to `assets/` at render time, as in the worked slides.

## The neighbours
- frame before: The turn.
- frame after: The chips.

## What already ran, so do not repeat it
The shipped Nov 14 deck and the look v2 proof (`examples/look-v2-proof/2026-11-14/slides/slide-07.html`) drew THIS beat as: the same wafer boat on the same lab bench under the same light, headline top left at y 150, art in the lower half. Every frame of both decks did the same. Your frame must not be a wafer boat on a bench with the type top left, unless your concept makes a far stronger case than that and you say why in your concepts file. The last four decks before it were dark staged scenes of kit objects (cable reels, city limit signs, crates, pallets).
