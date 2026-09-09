# Phase 1 craft refresh, 2026-09-09

**Rotating focus: VARIETY ACROSS THE SERIES**, chosen because it is the criterion the last panel
scored lowest and it is the one the artwork ledger exists to protect. Carousel no. 17 on
September 7th took 6.0 on `variety` against a 6.8 bar while every other criterion sat at 7.0 or
better, so the deck did not lose marks on craft. It lost them on being the fifth of its kind.

## The finding, and it came off the ledger rather than off a search

Read `register` on the last five entries in `ledger/carousel/artwork.json` in a column:

| date | register |
|---|---|
| September 2nd | a desk under one grazing key at azimuth 118 |
| September 3rd | a print room's light table, seen from directly above |
| September 4th | the inside of an optical instrument, after dark |
| September 5th | an assay bench in a dark room, one warm lamp never in frame |
| September 7th | a raised floor machine hall on standby, lit only from below |

**Five consecutive decks are an interior, at night or in a windowless room, lit by one artificial
source.** Every one of them is a different DRAWING and the ledger's technique lists prove it, which
is why `bespoke_check` and the technique exclusions kept passing. Those two mechanisms measure
technique, and technique is not what a reader carries away from a strip. **Register is.** A reader
following this account for a week saw five dark rooms.

The last daylight register was August 28th, the Llano Estacado before sunrise, and the last
outdoor one was August 30th, a caliche field at last light with one daylight frame at the turn.
That is eight and ten days ago respectively.

## What the series-design literature adds, and it is the smaller half

Series cover practice describes the same tension this repo already states in
`TECHNIQUE_LIBRARY.md`'s coherence section: a series is held together by CONSTANTS, typically the
type furniture and one base colour, and it is told apart by VARIABLES, typically the image and an
accent hue. The failure mode named there is the one measured above. When a series holds its
variables constant and varies only inside them, the covers stop reading as a family and start
reading as a reprint.

This product already fixes its constants correctly. `coherence_check.py` holds the counter spine
and the furniture type sizes, which is exactly the right thing to freeze. What has drifted is the
variable the ledger was built to rotate.

## The instruction to the directors room

**Today's register is outdoors, in daylight, with the sun as the source.** Not a room, not a
bench, not a bay, not a hall. A place in Texas a person could stand in, at an hour the light is
doing something. If the story's own subject is indoor equipment, the frame that carries it is
still outdoors and the equipment sits in the landscape it draws from.

Two supporting calls that follow from it:

- **The palette comes off the ground, not off the hardware.** Four of the five above drew their
  palettes from manufactured surfaces (machined stainless, oiled maple, galvanized steel, a
  perforated floor tile). The palette source named in the dossier is a Texas soil, a Texas
  vegetation community or a Texas sky today.
- **The value arc inverts the other way.** Those five decks are dark decks with a light turn.
  A light deck with one dark turn is a different memory, and the inversion is what a reader
  stores the strip by.

## Sources

- [SPINE, creating cohesive visual consistency when designing a book series](https://spinemagazine.co/articles/creating-cohesive-visual-consistency-when-designing-a-book-series)
- [The Book Designer, building visually compelling book series covers](https://www.thebookdesigner.com/book-series-covers/)
- `ledger/carousel/artwork.json`, entries for August 28th through September 7th
- `runs/carousel/2026-09-07/score.json`, `variety` 6.0 across judges 6.8, 6.0 and 5.5
