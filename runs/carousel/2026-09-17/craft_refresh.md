# Phase 1 — craft refresh, 2026-09-17

**Focus area chosen: drawing a MESSAGE as a document rather than as a screenshot.** Today's
deck turns on a note a patient reads, so the technique most likely to be reached for is the
drawn document at true scale under the deck's one light, which is what
`ILLUSTRATION_SYSTEM.md` calls DOCUMENT and what `examples/editorial-deck/` frames 02 and 07
demonstrate.

**The open web scan was unproductive and is recorded as such rather than padded.** A search on
editorial illustration of screens and messages returned stock libraries, a screenshot copyright
explainer and a Microsoft support thread. Nothing in it would change a decision on this deck,
and reporting a survey that taught nothing would be the kind of green banner `GATE_LESSONS.md`
is about.

**What the run actually took its craft from, which is the repo and is stronger:**

1. **A drawn document is a subject only if it is lit and sized.** `ILLUSTRATION_SYSTEM.md` is
   explicit that a white rectangle with words on it is a plate, and a plate is the single defect
   the whole system was rebuilt to kill. The reference build's sheet is placed at a rotation,
   cropped by three edges, and lit by a pool that is an ellipse rather than a circle because the
   lamp is off to one side.
2. **The two kinds of type want opposite things from the light**, and the reference build paid
   for that lesson twice. Light on dark needs the light dimmed toward it. Dark ink printed ON a
   drawn sheet needs the light, and punching the pool away from it is a plate with the sign
   flipped. Two reserve lists, not one.
3. **A mid ground is the worst ground and no choice of ink fixes it.** Three rounds went into
   choosing an ink against a band at Y 0.086 to 0.193 before somebody moved the GROUND instead.
4. **Set real type inside the document.** The reference frames carry set type in the drawn page,
   not greeked lines, and that is what makes the page read as a page. It also means every word
   inside a drawn document is published copy and is read by `numeral_lint` and the house style
   gate like any other string.
5. **Bisect before theorising.** One strike on the reference build survived four fixes aimed at
   the tooth, the dither, the reserve and the leading. Removing the pool named the cause in one
   render.

**A defect found while reading, and it is going to the retro rather than being fixed here.**
`layout_check.py --prose` exists to find surfaces still carrying the superseded rotation rule.
It reports six, all under `.claude/`, and signs off with "every surface this repo can write is
current". That is not true. `knowledge/carousel/TECHNIQUE_LIBRARY.md` under SUBJECTS still says
"rotated so no two frames in a row share one and at least five appear" and still lists "nine
frames share one screen" as a failure, and `ILLUSTRATION_SYSTEM.md` line 502 still says "Nine
halftones. Vary the screen with the layout." Both are writable by the `upgrade` lane, both
contradict the 2026-09-16 amendment in the same file, and the gate aimed at exactly this missed
them because it only scans the surfaces it already knew about. Handed to Phase 17.
