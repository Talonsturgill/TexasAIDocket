# Storyboard — the FIGURE BEARING reference

Three frames, three figures, three ways of drawing a number. It is a reference for ONE step,
the step from a computed value to a geometry on the canvas, and it exists because there was no
example of that step anywhere in this repo: every deck in the history reports 0 of 9 frames
mapping a computed figure onto drawn geometry.

THE ARTWORK CARRIES THE DATA in `knowledge/carousel/ILLUSTRATION_SYSTEM.md` is the law and
`scripts/carousel/figure_bearing.py` is the gate. This directory is what a green one looks like.

It is deliberately NOT a nine frame deck and it writes no chassis of its own. A real run does
both, per THE CHASSIS LAW. Adding a fourth world here would only put a variable between a reader
and the thing being shown.

CONTINUITY: MOTIF_EVOLUTION

**MOTIF_EVOLUTION.** The mark, at one pitch across all three frames. A field of 95 on frame 1,
one filled column against its own outline on 2, and on 3 that same field again with the 87
picked out of it as a 1.74 mark sliver. One measuring stick used three times, so the sizes are
comparable by eye and the reader is never asked to trust a re-scaling.

```yaml
slide: 1
layout: GRID
primary_image: >
  A field of 95 marks on a lit desk, one mark per 50 active systems, the last mark drawn short
  because 4,749 is not 95 fifties.
claims: [c1]
numerals:
  - value_from: c1
data_in_art:
  figure: active_systems
  drives: mark count
job: >
  Hand the reader the size of the whole record as something countable rather than as a numeral
  they skim.
acceptance:
  - the last mark is visibly shorter than the others, and it is the remainder rather than a
    rendering fault
  - every mark has a contact shadow, so the field sits on the desk instead of floating
```

```yaml
slide: 2
layout: OBJECT_AND_CAPTION
primary_image: >
  Two columns in one scale. The whole is an outline at low value, the share is filled, and one
  tick carries the share's height back onto the whole.
claims: [c1, c2]
numerals:
  - value_from: c2
data_in_art:
  figure: small_systems
  drives: column height
job: >
  Draw 3,579 of 4,749 as a PART rather than as a second quantity, which is what two free standing
  bars would have said.
acceptance:
  - both columns share one baseline and one top, so the share reads off the whole
  - the filled column's height is 3579/4749 of the span, measurable off the render
```

```yaml
slide: 3
layout: GRID
primary_image: >
  87 marks at one mark each, at frame 1's pitch, against 72 ghosted marks standing for the 3,579
  at frame 1's scale.
claims: [c1, c3]
numerals:
  - value_from: c3
data_in_art:
  figure: large_systems
  drives: mark count
job: >
  Close by putting the large end and the small end on ONE measuring stick, so the asymmetry is
  seen rather than asserted.
acceptance:
  - the 87 marks are countable in rows of 19
  - the ghosted field is present and deliberately uncountable, which is what a number that size
    honestly looks like
```
