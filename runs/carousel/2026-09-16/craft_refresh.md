# Phase 1 craft refresh, 2026-09-16

Rotating focus: what carries a WHERE claim when the county map is spent.

Measured off the last three shipped decks rather than guessed:

| deck | layouts, in slide order |
|---|---|
| 2026-09-13 | FIGURE_SCALE DOCUMENT CLOSE_CROP DIAGRAM GRID OBJECT_AND_CAPTION SPLIT_HORIZON MAP FULL_BLEED |
| 2026-09-14 | FULL_BLEED DOCUMENT GRID CLOSE_CROP DIAGRAM FIGURE_SCALE MAP DOCUMENT OBJECT_AND_CAPTION |
| 2026-09-15 | FULL_BLEED DIAGRAM FIGURE_SCALE CLOSE_CROP DOCUMENT SPLIT_HORIZON OBJECT_AND_CAPTION MAP FULL_BLEED |

Two findings, both actionable today.

1. **MAP has run in all three, at slide 7 or 8 every time, and all three drew the same
   object**: 254 county geometries on the TXGeo Albers equal-area conic with a neatline and a
   computed scale bar. That is the same drawing three runs running, which is precisely what
   `bespoke_check` measures within a deck and `artwork.json` is supposed to stop across decks.
   The craft library's own rule is that a technique is chosen because THIS claim wants it, and a
   claim about a quantity does not become cartographic by being drawn on a map. **A MAP frame
   this run has to earn itself against a claim that is genuinely about where, or it does not run.**

2. **TYPE_AS_OBJECT has gone unspent for three decks.** It is capped at one per deck, so it is the
   cheapest unused variety in the rotation, and it is the layout that fits a story whose whole
   turn is a single phrase from a document. Carve it, cast it, stack it, pour it.

General practice scanned for the alternatives to a filled county map when a story is about place:
graduated and proportional symbol marks, dot density, cartogram and hex tile grids, and dasymetric
treatment. The register that transfers to this engine is the proportional symbol and the dot at
true position, because both are drawings of a COUNT standing somewhere rather than a fill over an
area, and this engine already has the bench for both (`TXSCENE` at true scale, `TXGeo` for the
position). The choropleth critique matters here for the same reason it matters in a newsroom: a
filled area reads as an area's worth of importance, and the record's own claims are almost never
about area.

Sources read: axismaps.com/guide/choropleth, maplibrary.org alternatives to traditional choropleth
maps, en.wikipedia.org/wiki/Dasymetric_map.
