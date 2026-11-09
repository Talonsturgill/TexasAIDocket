# Carousel no. 72, November 8th, 2026: the plate

## The story, and what the fact check did to it

Texas A&M AgriLife scientists in the Department of Biochemistry and Biophysics in College Station (c28) turned Google
DeepMind's AlphaFold-Multimer (c5, c6) into a yes or no classifier for protein interactions (c7) and ran it on every
pairing of a curated list of 1123 human mitochondrial proteins (c2). Of 630,003 possible pairs they kept 2,895 as likely
(c3, c4), 2895 interactions involving 1004 proteins, the paper's own 0.46% (c9). A pair counts when its mean ipTM score
reaches 0.5, which on their test set gives 67% recall at a false discovery rate of about 15% (c8, c10); the paper also
states 85% precision for direct interactions (c11). 57% of the predictions were in no existing database (c14). 85
uncharacterized proteins got at least one predicted partner (c30). About two years of lab work confirmed
several predicted partnerships in yeast and human cells (c19) and mapped the copper delivery pathway to cytochrome c
oxidase (c18). The predictions are free online as MitoMatch (c20, c21). The method can't give binding affinity (c24),
and the release says cures may still be far off (c23).

The fact check held it to its words. No count of pairs tested in the lab exists, so no frame draws one. The paper's
publication date is not a claim, so nothing says the paper is new. "A third missed" was rejected as computed from
recall, so nothing draws the complement of 67%. Every protein shape in the deck is a teaching model drawn to
illustrate, never a structure from the paper, and every brass position on the plate is a drawing unit or a computed
share, never a real MitoMatch coordinate.

Docket item tx-2026-0244, admitted this run.

## Why this treatment, and what was grafted

Base: THE MEASURE. The half matrix is a made object, a black anodised plate whose triangle holds one cell per pair, and
brass marks a likely pair. 630,003 is exactly every pair of 1123 proteins (compute.py asserts it), so the triangle is
the screen itself rather than a picture of it. The ratio is the story and scattered it is invisible at feed size, so the
deck gathers the 2,895 into one tile at the same scale (frame 4), stands a hundred calls above a step at 0.5 with the
false share in steel (5), and splits the block new against known (6).

Grafted from THE PAIR IN THE HAND: a physical teaching model of two proteins meeting, as the cover (1), the question (2)
and the close (9). It is built as a space-filling model, one sphere per atom group on a seeded fold, because that is what
a protein model on a lab bench looks like and it reads as a molecule at 432 px where a smooth form reads as a blob.
Grafted from THE ROOM WHERE IT WAS CHECKED: one dark lab at last light, a black epoxy bench under one window, the backlit
plates where several pairs were confirmed (8) and a rack of 85 tubes for the proteins given a predicted partner (7).

Dropped: the compute aisle (the claims place the compute at HPRC and a server row is the beat this record draws most),
the fanfold printout (a heavy build whose pale paper is the mid tone trap), the western blot (the claims name no assay)
and the steel rule (the step with its hundred calls carries the same cut and also the false share).

## The world, and the laws that hold it

`lastLight`, staged, inside one TXT.interior lab. The key is the last light through one window on the left: azimuth
-55, elevation 14, low on the frame's upper left, so every lit edge faces left and up and every cast runs right and
down. The reliefs read the same declaration and are raked from the upper left. The room's back wall is in shadow. Type is
light on the dark field. A wash only darkens. Brass is the only warm metal. Glass and plastic always have the window
behind them.

## Palette

black anodise #141416, satin milled aluminium #4A4E55, black epoxy #0D0E10, painted block #23272D, bone resin #D9D2C3,
brass #C9B393, blackened bronze #3A2E22, amber agar #B98A4C, milky polypropylene #CFCBC2, night #08060F

A College Station lab after hours: black epoxy and anodised metal, a pale resin model, amber plates. The accent is
brand.yaml's dust #C9B393 as brass and it means ONE thing, a likely pair. It sits on the cover's second chain (1), the
one tile (4), the 85 brass bosses (5), the block (6) and the lifted block (9). Nothing else is brass.

## The continuity devices

CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE

1. **Motif evolution, the brass.** A brass chain seated against a bone one (1), the two apart with no brass (2), the bare
   triangle (3), one brass tile among dark ones (4), 85 brass calls among 100 above the step (5), the block split new
   against known (6), and the block lifted out of its pocket (9).
2. **Camera move, one bench.** Macro at the bench top (1, 2), straight down on the plate (3 to 6), along the bench at
   tube height (7), into the window at the plates (8), and high three quarter over the plate's corner (9).

## The rotation

    CLOSE_CROP  OBJECT_AND_CAPTION  DIAGRAM  FIGURE_SCALE  DIAGRAM  CLOSE_CROP  FULL_BLEED  FULL_BLEED  OBJECT_AND_CAPTION

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | MACRO, eye 0.36 m above the bench, 0.55 m from the model, fov 20.5, the window seam behind | the chassis protein_pair seated, two space-filling chains of instanced atom spheres on a seeded fold, bone resin and brass, on a black epoxy plinth on the chassis lab_bench, rim lit from the window, TXT.contact under the plinth |
| 02 | CLOSE, eye 0.30 m, level with the models, fov 28, the window square behind the gap | the two chains apart on the plinth, 30 mm of window light between them, bone resin and blackened bronze, each rim lit, contact on the epoxy |
| 03 | AERIAL, orthographic material relief | the black anodised plate with the half matrix milled as a terrace, legs of leg_cells cells, the 1,122 step hypotenuse lit as a saw edge, graduations every hundred cells in the albedo, one protein's band raised and casting |
| 04 | AERIAL, orthographic material relief | the terrace ruled into square tiles of tile_side_cells cells, satin milled aluminium with tool marks in the albedo, raked by the low key from the upper left, V grooves with one lit and one shadowed wall, one tile in brass standing proud with its cast laid across two neighbours |
| 05 | AERIAL, orthographic material relief | a milled step wall across the frame for the 0.5 cut, satin aluminium with a bright lit face toward the key, the grooved field below it, above it a 10 by 10 block of square bosses, boss_brass in brass and boss_steel in bead blasted steel, every boss at one height and each casting a short shadow inside its gap |
| 06 | CLOSE, orthographic material relief | the brass block of block_cols columns, block_full_rows rows and a last row of block_last_row cells, polished brass for the new share and blackened bronze for the known with a broad sheen under the low key, one height, cell grooves shallow, its cast laid on the anodise, a lit notch at the short row |
| 07 | MEDIUM, eye at tube height 0.12 m over the bench, fov 20, the window behind the rack | the chassis tube_rack holding orphans microtubes in rows, milky polypropylene backlit by the window, snap caps side on, slate rack, contact on the epoxy |
| 08 | MEDIUM, eye 0.17 m over the bench, close on the tower, fov 30 | a tower of inverted chassis petri_plate dishes with amber agar, backlit so every rim glows, two more plates behind and one open plate in front with cream colonies on amber agar under a warm pool, contact on the epoxy |
| 09 | MEDIUM, eye 0.24 m above the bench, the cover's bench from a little higher and further back, fov 30 | the chassis protein_pair seated on its black plinth exactly as on the cover, bone resin and brass atom spheres rim lit from the window, TXT.contact under the plinth, and beside it the chassis pair_block in polished brass, its cells cut as grooves with every tenth groove wide, TXT.contact on the bench |

Showstopper frame: 01, the two chains seated with one bright rim line along the seam where brass meets bone, the window's warm seam behind, every atom sphere catching its own small highlight.
Tonal arc: the brightest rim on 01, the darkest frame with one slit of light on 02, the reliefs held near black and lit at their edges on 03 to 06, the backlit glow peaks on 07 and 08, and the brass on 09 in a pool.
VALUE CUT: frame 7. The deck turns from the screen to the bench.

---
```yaml
slide: 1
layout: CLOSE_CROP
primary_image:
  subject: "a space-filling teaching model of two proteins seated together, one chain bone white and one brass, on a black epoxy plinth on a lab bench, the window's last light behind"
  rect: [160, 560, 920, 700]
  bleeds: [right]
accent: "#C9B393"
job: 'Show the question the whole screen asks, two proteins that fit together, as one object a reader can see the size of, before any number arrives.

  '
claims: [c5, c7, c28]
numerals: []
depth:
  eye: 0.36
  horizon: 520
  cues: [CAST_SHADOW, FORM_SHADING, OCCLUSION, RELATIVE_SIZE, AERIAL]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'A close view level with the model. The two chains sit together in the lower right two thirds, the bone chain on the left and the brass chain on the right, cut by the right and bottom edges. The window square is behind them on the left, a warm seam low in the frame.

    ', bands: 'Top third, the dark back wall of the lab carrying the kicker, the hook and the dek. Middle third, the tops of both chains rim lit against the window seam. Bottom third, the lit bodies of the chains on their black plinth, the plinth''s shadow on the bench in the foreground, the epoxy falling into shadow under the type.

    ', focal: the seam where the brass chain meets the bone chain}
art: {technique: 'physically based render of the chassis protein_pair on the chassis lab_bench inside a TXT.interior lab in the lastLight world, staged on the model', why_this_technique: 'the claim is that two proteins can meet and a model can predict it, and a render gives a physical model of the pair, atom spheres with real highlights and casts, so the reader sees an object rather than an icon', palette: 'bone resin, brass, black epoxy, the dark wall and the warm window seam', value_structure: 'Lightest is the rim along the brass chain and the window seam. Darkest is the back wall and the bench beyond the pool. Frame median L* planned at 14.

    '}
type:
  hook: "An AI was asked which proteins pair up"
  dek: "Texas A&M scientists in College Station recast AlphaFold-Multimer as a yes or no test for which mitochondrial proteins interact. The model is drawn to illustrate, not a structure from the paper."
  labels: []
verbatim: []
acceptance: ['the protein_pair owns at least 40 percent of the frame area at 432 px, and the frame fails if the protein_pair is missing or unmodelled', two distinct chains in two different materials are identifiable at 432 px, 'the two chains together own at least a third of the frame area at full size, and the frame fails if either chain is missing or they do not touch', individual atom spheres with their own highlights are visible at native size, a warm window seam shows behind the model, no chain crosses a glyph of the hook or dek, the frame's median L* at 432 px is 30 or lower]
risks: ['a fold of spheres can read as a bunch of grapes or a toy, so the spheres are small, packed and matte resin, and the brass chain is metal with a sharp rim']
```

```yaml
slide: 2
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "the same two protein chains standing apart on the plinth, one bone and one blackened bronze, with the window's light passing through the gap between them"
  rect: [120, 640, 840, 620]
  bleeds: []
accent: "none"
job: 'Name the tool and the question it was used for, do these two meet, with the answer withheld.

  '
claims: [c5, c6, c7, c22]
numerals:
depth:
  eye: 0.30
  horizon: 760
  cues: [CAST_SHADOW, FORM_SHADING, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'Two chains left and right of centre in the lower half, apart, the window square directly behind the gap so a vertical slit of light falls between them and across the plinth toward the camera.

    ', bands: 'Top third, the dark wall with the type. Middle third, the window and the tops of both chains in silhouette with rims. Bottom third, the plinth in the foreground with the slit of light running toward the reader and each chain''s shadow either side of it.

    ', focal: the slit of light between the two chains}
art: {technique: 'physically based render of the chassis protein_pair in its apart state, contre jour against the window, in the lastLight lab', why_this_technique: 'the classifier answers a yes or no question about two chains, and two chains with light between them is that question before it is answered', palette: 'bone resin, blackened bronze, black epoxy, the warm slit', value_structure: 'Lightest is the slit and the rims. Darkest is the two chain bodies and the wall. Frame median L* planned at 10.

    '}
type:
  hook: "Do these two meet?"
  dek: "Google DeepMind built AlphaFold-Multimer to predict how protein chains fit together. The team used it as a yes or no test on each pair. Mutations in nearly 30% of mitochondrial proteins are tied to disease. The models are drawn to illustrate."
  labels: []
verbatim: []
acceptance: ['the two chains together span at least half the frame width at 432 px', two separate chains with a visible lit space between them are identifiable at 432 px, the frame fails if the chains touch or if no light passes between them, each chain shows a rim line on its window side, no brass appears anywhere in the frame, the frame's median L* at 432 px is 30 or lower]
risks: ['two dark forms against a bright window can go to flat silhouettes, so a low fill from the camera side keeps the near faces modelled']
```

```yaml
slide: 3
layout: DIAGRAM
primary_image:
  subject: "a black anodised plate filling the frame with a right triangle milled as a raised terrace, one cell per protein pair, its hypotenuse a fine stair catching the light, one protein's row and column raised as a band"
  rect: [240, 340, 800, 840]
  bleeds: []
accent: "none"
data_in_art: {figure: leg_cells, drives: 'the triangle''s legs in cells and the cell size, so the terrace holds exactly pairs cells, one per protein against each other one'}
job: 'Show that the screen was the whole half matrix, every pair once, as a shape a reader can hold, before the find is drawn.

  '
claims: [c2, c3, c4]
numerals:
- {value_from: c2}
- {value_from: c3}
depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]
composition: {structure: 'A plan of the plate. The triangle''s right angle sits at the lower right, its legs run up the right side and along the bottom, and its hypotenuse climbs from lower left to upper right. The empty half above the hypotenuse is bare plate and carries the type. One band, a protein''s row and column, is raised and casts.

    ', bands: 'Top third, bare black plate with the kicker, hook and dek. Middle third, the upper triangle with the hypotenuse''s lit edge. Bottom third, the broad base of the terrace in relief, the band''s shadow across it and the lit leg edge.

    ', focal: the lit hypotenuse stair}
art: {technique: 'TXBENCH material relief of a milled plate, anodise, satin aluminium and a raised band, raked from the upper left', why_this_technique: 'the quantity is a count of cells in a fixed shape, and a milled plate drawn in parallel projection keeps every cell the same size so the shape is the number', palette: 'black anodise, satin aluminium', value_structure: 'Lightest is the hypotenuse edge and the band''s lit wall. Darkest is the bare plate. Frame median L* planned at 9.

    '}
type:
  hook: "Every pair, once"
  dek: "The team built a curated list of 1123 proteins. Every possible pairing comes to 630,003 pairs, and the screen read all of them. The plate is drawn to illustrate."
  labels: ["1123 proteins", "630,003 pairs"]
verbatim: []
acceptance: ['the black anodised plate fills the full frame width and its terrace''s legs each run at least 70 percent of the frame width at full size, the most a right triangle can take below a four line dek', a right triangle raised from a dark plate is identifiable at 432 px, the triangle's hypotenuse shows a lit edge along its whole length, one band of a single row and column stands proud and throws a visible cast, 'the frame fails if the triangle is missing or filled with brass', no plate edge or band crosses a glyph of the hook or dek, the frame's median L* at 432 px is 30 or lower]
risks: ['a raised plate on a ground reads as a tray, so the plate is full bleed with no border and the terrace is the only raised field']
```

```yaml
slide: 4
layout: FIGURE_SCALE
primary_image:
  subject: "the same terrace ruled into square tiles, each holding the area of every likely pair, with one tile standing proud in brass near the right angle and casting across its neighbours"
  rect: [100, 300, 920, 870]
  bleeds: []
accent: "#C9B393"
data_in_art: {figure: tile_side_cells, drives: 'the side of every tile in cells, so one brass tile holds exactly the area of the likely pairs at the triangle''s own cell scale'}
job: 'Make 0.46% visible. All 2,895 likely pairs gathered at the same scale are one tile among the rest.

  '
claims: [c3, c4, c9]
numerals:
- {value_from: c4}
- {value_from: c4}
- {value_from: c9, computed_by: compute.py share_pct}
depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]
composition: {structure: 'The terrace as in frame 3, now ruled by grooves into square tiles at one pitch. The hypotenuse cuts through the edge tiles. One tile three in from the right angle stands proud in brass, its key side walls lit and its cast laid down right across two neighbours.

    ', bands: 'Top third, bare plate with the type. Middle third, the upper tiles and the hypotenuse. Bottom third, the base tiles in relief and the lit brass tile with its shadow across two neighbours, and a leader line to each figure.

    ', focal: the brass tile}
art: {technique: 'TXBENCH material relief, tiles cut by V grooves in satin aluminium, one tile in brass at a greater height, raked from the upper left', why_this_technique: 'a share this small vanishes when scattered, and gathering it into one unit at the same scale among identical units lets the reader count the rest', palette: 'black anodise, satin aluminium, brass', value_structure: 'Lightest is the brass tile''s lit walls and top. Darkest is the plate and the groove floors. Frame median L* planned at 10.

    '}
type:
  hook: "All 2,895 likely pairs fit in one tile"
  dek: "The screen kept 2,895 of 630,003 pairs as likely, the paper's 0.46%. Each tile on this plate holds the area of all 2,895. One is raised in brass."
  labels: ["630,003 pairs screened", "2,895 likely"]
verbatim: []
acceptance: ['the brass tile measures at least 40 px on a side at full size and the terrace spans at least 85 percent of the frame width', one brass tile is identifiable among dark tiles at 432 px, the brass tile throws a visible cast onto the neighbouring tiles, the tiles are square and of one size across the terrace, 'the frame fails if no brass tile is visible or if there is more than one', no groove or tile crosses a glyph of the hook or dek, the frame's median L* at 432 px is 30 or lower]
risks: ['a grid of tiles can read as a calendar or a floor, so the grooves are V cut with one lit and one shadowed wall and the brass tile is the only raised thing']
```

```yaml
slide: 5
layout: DIAGRAM
primary_image:
  subject: "a milled step crossing the plate diagonally for the 0.5 cutoff, the grooved field below it, and above it a square block of a hundred bosses, most in brass and the rest in steel, every boss at one height"
  rect: [0, 470, 1080, 880]
  bleeds: [left, right, bottom]
accent: "#C9B393"
data_in_art: {figure: boss_brass, drives: 'how many of the hundred bosses above the step are brass, with the remainder in steel equal to the stated false discovery rate'}
job: 'Show where the line is drawn and what it costs, a hundred calls that cleared it with the false share in steel.

  '
claims: [c8, c10, c11]
numerals:
- {value_from: c8}
- {value_from: c8}
- {value_from: c8}
- {value_from: c11}
depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]
composition: {structure: 'A step wall runs from the upper left toward the lower right of the art. Below and left is the grooved lower field. Above and right, on the upper level, a ten by ten block of square bosses, brass first in reading order and steel last, contiguous so the eye reads a proportion.

    ', bands: 'Top third, bare plate with the type. Middle third, the step wall''s lit face and the top rows of bosses. Bottom third, the grooved lower field in relief and the last rows of bosses, the steel ones, each with a short shadow.

    ', focal: the bright step wall}
art: {technique: 'TXBENCH material relief of a stepped plate with a boss field in two metals, raked from the upper left', why_this_technique: 'a threshold is a height you either clear or do not, and a milled step makes the cut physical while the boss field carries the stated precision as countable units', palette: 'black anodise, satin aluminium, brass, bead blasted steel', value_structure: 'Lightest is the step wall and the brass tops. Darkest is the lower field''s grooves. Frame median L* planned at 12.

    '}
type:
  hook: "The line sits at 0.5"
  dek: "A pair counts when its mean ipTM score reaches 0.5. On the authors' test set that gives 67% recall at a false discovery rate of about 15%. Of a hundred calls drawn above the line, the 15 in steel are the false share."
  labels: ["below 0.5", "0.5 and above", "85% precision"]
verbatim: []
acceptance: ['the milled step wall runs at least 70 percent of the frame width and the boss block spans at least 45 percent of it at full size', a diagonal step wall across the plate is identifiable at 432 px, a square block of bosses stands on the upper level with a brass share and a steel share that are told apart at 432 px, every boss is the same height, 'the frame fails if the boss count is not one hundred or the steel count is not the stated false share', no boss or step crosses a glyph of the hook or dek, the frame's median L* at 432 px is 30 or lower]
risks: ['a boss field under a low key can stripe like blinds, so the bosses are low and widely spaced and their casts stay inside the gaps']
```

```yaml
slide: 6
layout: CLOSE_CROP
primary_image:
  subject: "the brass block of every likely pair at close range, one cell per pair milled into its top, split by a seam into bright brass for the share no database held and blackened bronze for the share already known"
  rect: [140, 470, 860, 820]
  bleeds: []
accent: "#C9B393"
data_in_art: {figure: block_cols, drives: 'the block''s columns, full rows and short last row, so its cells number exactly the likely pairs, and the bright share by new_cells'}
job: 'Show what was new, most of it, and that the medium can say yes but never how strongly.

  '
claims: [c13, c14, c24]
numerals:
- {value_from: c14}
depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]
composition: {structure: 'The block sits low and centred, filling most of the lower two thirds, its last short row leaving a stepped notch at its lower right. A seam groove crosses it, bright brass above, dark bronze below.

    ', bands: 'Top third, bare plate with the type. Middle third, the bright brass cells. Bottom third, the bronze cells in relief, the lit notch at the short row and the block''s shadow on the anodise.

    ', focal: the seam between brass and bronze}
art: {technique: 'TXBENCH material relief of a milled block in two metals on the anodised plate, raked from the upper left', why_this_technique: 'a share of a count is two areas of one object, and cells at one height keep the drawing from implying a strength the paper says it can''t give', palette: 'brass, blackened bronze, black anodise', value_structure: 'Lightest is the brass cells. Darkest is the plate and the bronze. Frame median L* planned at 16.

    '}
type:
  hook: "Most of them had never been reported"
  dek: "57% of the predicted interactions were in none of the databases checked. Every cell stands at one height, because the method can't say how tightly a pair binds."
  labels: ["new, 57%", "already known"]
verbatim: []
acceptance: ['the brass block spans at least 60 percent of the frame width at full size', a brass block made of fine cells is identifiable at 432 px, a seam divides the block into a bright upper share and a dark lower share, the bright share is larger than the dark share, every cell stands at the same height, 'the frame fails if the block has no short last row', no cell crosses a glyph of the hook or dek, the frame's median L* at 432 px is 30 or lower]
risks: ['a fine cell grid can moire at feed size, so the cell grooves are shallow and the seam and the block''s outline carry the read']
```

```yaml
slide: 7
layout: FULL_BLEED
primary_image:
  subject: "a slate rack of 85 milky microtubes in aligned rows on the black bench, backlit by the window so every tube body glows at its rim"
  rect: [0, 620, 1080, 600]
  bleeds: [left, right]
accent: "none"
data_in_art: {figure: orphans, drives: 'the number of tubes in the rack, one per uncharacterized protein given at least one predicted partner'}
job: 'Turn the 85 uncharacterized proteins given a predicted partner into countable units at one size, and move the deck from the screen to the bench.

  '
claims: [c30]
numerals:
- {value_from: c30}
depth:
  eye: 0.12
  horizon: 640
  cues: [CAST_SHADOW, FORM_SHADING, OCCLUSION, RELATIVE_SIZE]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'A long lens at tube height. The rack runs across the frame in the lower middle, five rows deep, the window behind it so the tubes glow, the near row sharp.

    ', bands: 'Top third, the dark wall with the type. Middle third, the window seam and the caps of the far rows. Bottom third, the near rows glowing in the foreground, the rack and its shadow on the bench.

    ', focal: the near row of glowing tubes}
art: {technique: 'physically based render of the chassis tube_rack and microtube models in the lastLight lab, backlit', why_this_technique: 'a count of proteins is a count of things a lab keeps in tubes, and backlit plastic in a rack reads as units at one size', palette: 'milky polypropylene, slate, black epoxy, the warm seam', value_structure: 'Lightest is the tube rims against the window. Darkest is the wall and the bench. Frame median L* planned at 14.

    '}
type:
  hook: "85 little-known proteins got a predicted partner"
  dek: "The screen found at least one predicted partner for each of 85 uncharacterized proteins. One tube stands for each, drawn to illustrate."
  labels: []
verbatim: []
acceptance: ['the rack spans at least 70 percent of the frame width at full size', a rack of tubes in aligned rows is identifiable at 432 px, the tubes glow at their rims against the window, the rack holds exactly the stated count of tubes, 'the frame fails if the tubes read as a solid block with no gaps', no tube crosses a glyph of the hook or dek, the frame's median L* at 432 px is 30 or lower]
risks: ['tube caps seen from above read as dots, so the camera stays at tube height and the caps are seen side on']
```

```yaml
slide: 8
layout: FULL_BLEED
primary_image:
  subject: "a tower of inverted yeast plates with amber agar and cream colonies on the black bench, backlit by the window so every rim glows, two more plates beside it and one plate open, agar face up with cream colonies"
  rect: [90, 640, 990, 710]
  bleeds: [right, bottom]
accent: "none"
job: 'Show where the predictions were checked, at the bench, with no count of confirmed pairs.

  '
claims: [c19, c18]
numerals: []
depth:
  eye: 0.30
  horizon: 600
  cues: [CAST_SHADOW, FORM_SHADING, OCCLUSION, RELATIVE_SIZE, AERIAL]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'Looking into the window along the bench. The plate tower stands left of centre and fills the middle third, the open plate lies right in front, two plates sit behind it. The window is the frame''s light.

    ', bands: 'Top third, dark wall and the window''s upper edge with the type. Middle third, the tower''s glowing rims and the window seam. Bottom third, the tower''s base and the open plate in the lit foreground on the epoxy with their shadows.

    ', focal: the glowing amber rims of the plate tower}
art: {technique: 'physically based render of the chassis petri_plate model and one open plate built in the frame in the lastLight lab, backlit glass and agar', why_this_technique: 'the confirmation happened in yeast and human cells, and plates backlit at a bench, one opened to show its colonies, are where that work is done', palette: 'amber agar, cream colonies, clear polystyrene, black epoxy, the warm seam', value_structure: 'Lightest is the agar rims and the seam. Darkest is the bench beyond the pool. Frame median L* planned at 16.

    '}
type:
  hook: "Several pairs held up at the bench"
  dek: "About two years of lab work confirmed several predicted partnerships in yeast and human cells. The work also mapped the route copper takes inside mitochondria to cytochrome c oxidase. The plates are drawn to illustrate."
  labels: []
verbatim: []
acceptance: ['the dish tower stands at least 40 percent of the frame height at full size', a stack of round dishes with amber contents is identifiable at 432 px, the dish rims glow against the window, an open plate with cream colonies on amber agar is visible beside the stack, 'the frame fails if any number or count label is printed on the art', no dish crosses a glyph of the hook or dek, the frame's median L* at 432 px is 30 or lower]
risks: ['dishes stacked can read as domes or coins, so the camera is oblique and low and every dish shows its wall']
```

```yaml
slide: 9
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "the cover's protein teaching model on its black plinth on the bench, and beside it the brass block of every likely pair, one cell per pair, set down where anyone can reach it"
  rect: [140, 560, 860, 640]
  bleeds: []
accent: "#C9B393"
data_in_art: {figure: block_cols, drives: 'the brass block''s columns, full rows and short last row, one cell per likely pair, drawn here at a stated drawing unit beside the model'}
job: 'End on the consequence, the whole list set down beside the question it answers and offered free to anyone, with the honest limit.

  '
claims: [c4, c20, c21, c23, c29]
numerals:
- {value_from: c21}
depth:
  eye: 0.24
  horizon: 420
  cues: [CAST_SHADOW, FORM_SHADING, OCCLUSION, RELATIVE_SIZE, AERIAL]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'The cover''s bench seen again, a little higher and further back. The teaching model fills the middle of the frame on its black plinth, rim lit from the window behind and to the left. The brass block of the list rests on the bench in the lower right, beside the plinth and clear of it.

    ', bands: 'Top third, the dark room and the warm glow of the window with the type. Middle third, the teaching model in its pool, rim lit. Bottom third, the lit brass block on the bench in the foreground with its contact shadow, and the plinth''s front edge.

    ', focal: the brass block at the front edge}
art: {technique: 'physically based render of the chassis protein_pair on its plinth and the pair_block on the lab_bench in the lastLight lab, the cover''s light, staged on both', why_this_technique: 'the consequence is that the whole list now sits where anyone can reach it, and the block of every likely pair set down beside the model of the question is that act', palette: 'brass, bone resin, black epoxy, the warm window glow', value_structure: 'Lightest is the bone chain''s lit side and the brass block''s top. Darkest is the room around the pool. Frame median L* planned at 13.

    '}
type:
  hook: "The list is free to use"
  dek: "The team posted all 2,895 predictions as MitoMatch, free at mitomatch.web.app. The release says cures for diseases linked to mitochondria may still be far off. The block and model are drawn to illustrate."
  labels: []
verbatim: []
acceptance: ['the protein_pair spans at least 50 percent of the frame width at full size, and the brass block is fully in frame above the footer', a brass block in front of the two chain model is identifiable at 432 px, the block shows a visible thickness and a contact shadow on the bench, 'the frame fails if the block touches the model or is cut by the frame edge', no object crosses a glyph of the hook or dek, the frame's median L* at 432 px is 30 or lower]
risks: ['a thin block reads as a card or a chip, so it is drawn with real thickness in the deck''s polished brass and set clear of the model']
```
