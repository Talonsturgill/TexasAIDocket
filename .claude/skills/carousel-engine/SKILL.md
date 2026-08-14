---
name: carousel-engine
description: Render engine and QA harness for Texas AI Docket LinkedIn carousel slides. Turns per-slide HTML/CSS/SVG/Canvas art into exact 1080x1350 PNGs at 2x, a vector-text PDF for LinkedIn upload, feed-size thumbnails, and a contact sheet, with objective machine QA (render errors, missing fonts, clipped or offscreen or tiny text, contrast estimates, safe-zone violations, art crossing glyphs). Use whenever building or reviewing carousel slides. The engine is a HARNESS, not a template: every deck's art is bespoke code written per run.
---

# carousel-engine — render + QA harness

The quality layer is fixed; the art is not. Slides are hand-coded HTML files, one per slide,
using any mix of CSS, SVG, Canvas 2D, d3 and the committed art libraries. This engine renders
them deterministically, checks them objectively, and assembles the deliverables.

**Every rule below is enforced by code in this directory.** Read them as the contract the
machine will hold you to, not as advice. Each exists because the failure it describes ships
silently: it renders, it looks like art, and it is wrong.

## Pipeline (per run)

```bash
bash .claude/skills/carousel-engine/bootstrap.sh          # once per session; installs pip deps

# 1. write slides to      out/<run>/slides/slide-01.html ... slide-NN.html
python3 .claude/skills/carousel-engine/render.py \
    --slides-dir out/<run>/slides --out-dir out/<run>/render       # PNGs + render_report.json
python3 .claude/skills/carousel-engine/qa.py --render-dir out/<run>/render  # machine_qa.json, exit!=0 on FAIL
python3 .claude/skills/carousel-engine/assemble.py \
    --slides-dir out/<run>/slides --render-dir out/<run>/render \
    --out-dir out/<run>/final --title "<document title>"           # carousel.pdf (VECTOR) + sheet + thumbs
```

Re-render only fixed slides with `--only 3,7`. Read every report. **Never ship a FAIL.** A
`qa.py` warning is an advisory for the pixel critics, not a free pass.

`examples/demo-deck/` is four slides exercising SVG filter atmospheres, d3 cartography through
TXGeo, a seeded flow field, and software 3D. It is a PLUMBING reference, not a style template.

## Slide HTML contract

- One file per slide: `slide-01.html`, `slide-02.html`, ... Design for the viewport: exactly
  **1080x1350 CSS px**. `margin: 0`; nothing may scroll. Body overflow is a hard fail.
- Reference committed assets ONLY via the `@@ASSETS@@` token, which the engine resolves to an
  absolute `file://` path:

  ```html
  <link rel="stylesheet" href="@@ASSETS@@/fonts/fonts.css">
  <script src="@@ASSETS@@/js/noise.js"></script>       <!-- TX.simplex2/fbm2/warp2/rng -->
  <script src="@@ASSETS@@/js/txtype.js"></script>      <!-- TX.fitText, TX.svgPlate -->
  <script src="@@ASSETS@@/js/txlabel.js"></script>     <!-- TX.canvasLabel knockout plates -->
  <script src="@@ASSETS@@/js/tx3d.js"></script>        <!-- TX3D software 3D renderer -->
  <script src="@@ASSETS@@/js/txgeo.js"></script>       <!-- TXGeo Texas projection -->
  <script src="@@ASSETS@@/js/d3.v7.min.js"></script>
  <script src="@@ASSETS@@/js/topojson-client.min.js"></script>
  ```

  Geodata via `fetch("@@ASSETS@@/geo/tx-counties.topo.json")` (254 counties) and
  `tx-places.json` (the gazetteer). **NO external URLs, no CDNs, no Google Fonts.** render.py
  rejects any `http(s)://` reference.
- **Async art must gate the screenshot**: set
  `window.renderReady = new Promise(resolve => { /* draw, then */ resolve(); })`. The engine
  awaits it, capped at 30s. Without it you get a 400ms grace and a half-drawn frame.
- **Canvas = 2x backing store.** Any `<canvas>` styled at `W x H` CSS px must set
  `canvas.width = W*2; canvas.height = H*2; ctx.scale(2,2)`. Screenshots are taken at
  deviceScaleFactor 2 and the PDF embeds the canvas bitmap, so a 1x canvas ships blurry. qa.py
  FAILS under 1.5x and WARNs from 1.5x to 1.9x.
- **Text is HTML or SVG, never canvas.** Canvas text rasterises into the PDF. HTML and SVG text
  stays vector, survives LinkedIn's recompression, and feeds the platform's semantic ranker and
  accessibility mode. Draw art on canvas; set type in DOM or SVG layers above it.
- Mark intentionally tiny or bleeding text (footers, coordinates, watermark type used as
  texture) with `data-decorative` so QA does not flag it. Both `data-decorative` and
  `data-overlap-ok` inherit to descendants.

### The five gates that read pixels rather than markup

These catch the failures a DOM inspection structurally cannot see, because canvas and SVG
geometry are invisible to it.

- **Art may never cross a label's glyphs.** qa.py samples a thin ring around every
  non-decorative label's ink and FAILS when ink of the GLYPHS' OWN VALUE touches the
  letterforms across the label, whatever layer drew it: a canvas groove edge, a scored outline,
  an SVG leader rule, a specular highlight. Type set over art needs a declared defense: an
  opaque knockout plate, a scrim on a dark ground, or a halo. A halo is the opposite value, so
  it never trips the gate. `data-overlap-ok` demotes the FAIL to a WARN when the layering is
  deliberate and you have judged it legible.

  **A knockout plate must actually knock out.** A plate at 93 percent opacity still lets seven
  percent of a high-contrast streamline through, and seven percent of an edge is still an edge
  running across a letterform. Use a solid fill.

- **Nothing opaque may be painted over type.** render.py hit-tests every non-decorative text
  line box against every opaque element box using the `elementsFromPoint` stack; qa.py FAILS
  when a foreign plate covers 20x6px or more of a line box, WARNs from 12x4px. A padded plate's
  BACKGROUND is not a line box, which is how a tag can overprint the bottom third of a subtitle
  and pass with zero fails. The text's own plate, ancestor or descendant, is never its own
  occluder. The remedy is to move the plate or the type, never to declare the overlap away.

- **Text may never overprint text.** qa.py FAILS when two elements' text line boxes intersect.
  Deliberate layering must be declared with `data-overlap-ok` on the floating element; the gate
  then warns and the pixel critics judge it. Note that two labels sharing a horizontal band
  read as a collision even when the glyphs do not touch, so put furniture above or beside other
  furniture rather than beneath it.

- **An SVG label must sit inside its own plate.** render.py measures every `<svg><text>`
  against the `<rect>` painted under it, against any opaque `<rect>` appended AFTER it (SVG has
  no z-index, document order IS the stack), and against any opaque DOM element composited above
  the whole `<svg>`. qa.py fails all three.

  **Never type a plate width.** Build it from the label: `TX.svgPlate(textEl, {padX, padY,
  fill, stroke})` in txtype.js measures the laid-out text with `getBBox`, adds padding and any
  stroke, and inserts the rect as the label's immediately preceding sibling. Call it after
  `await document.fonts.ready`. `TX.svgPlateAll(selector, opts)` does a whole set. A plate
  width and a label are otherwise two separately typed numbers, and they drift.

- **A canvas that draws nothing still renders.** Any visible canvas covering 25 percent or more
  of the slide FAILS if its pixels are near-uniform: a dead frame or an empty art layer. This
  is the gate that catches the quietest bug in the whole engine, because invalid coordinates do
  not throw. See the determinism note below for the specific trap.

### Opt-in contracts a slide can declare about itself

Each is optional. Declaring one means the slide is asserting something checkable, and the gate
then holds it to its own assertion. A failure here is the slide contradicting itself, never a
taste call.

- **What the art says without words**, on `<body>`:

  ```html
  <body data-encodes='[{"claim":"load is flat overnight", "reads":"differ",
                        "a":[[732,1052,82,98]], "b":[[736,500,74,540]]}]'>
  ```

  Regions are `[x,y,w,h]` in CSS px; a CSS selector string also works. qa.py reports the
  CIELAB distance and rank separability between the two populations AT 432px WIDE, plus how
  much of each region is art rather than furniture. `reads` is REQUIRED and is `"differ"` (the
  two regions must be tellable apart) or `"same"` (an absence or sameness claim). A declaration
  that omits it FAILS, because a probe that states no direction is a number nobody can be wrong
  about. A `"differ"` whose regions are under 4.0 dE apart at feed scale FAILS, because at that
  distance the probe is measuring the same thing twice.

  **MEASURE THE RECTS OFF THE RENDERED PNG, NEVER OFF THE STORYBOARD'S CAMERA ARITHMETIC.**
  Camera maths puts the rect where the feature was supposed to land. Open the PNG, find the
  feature, then write the numbers.

- **A contact shadow must have something to subtract from**:

  ```html
  <body data-contacts='[{"what":"the transformer on the pad",
                         "shadow":[[236,1178,608,30]], "ground":[[236,1248,608,30]]}]'>
  ```

  qa.py takes the median CIELAB L* of each region at 432px wide and FAILS below 4.0 L* of
  separation, WARNs below 8.0. Declare it on every object the dossier says sits on something.
  The fix for a failure is never a stronger shadow, it is a LIT GROUND: put a warm pool of
  light under where the object sits, then cast into it. A shadow drawn on a ground that is
  already near-black is a one L* change and reads as nothing.

- **A leader must land on the thing it points at, and say where that is.** Every drafting
  leader, callout rule or detail-circle tail is authored as a world-coordinate polyline that
  terminates ON the target's own coordinates, never as a fixed offset from the annotation's own
  center:

  ```js
  var SITE = [BX + 2, 838];                       // the feature's own coordinates
  var leader = [[168, 884], [128, 856], SITE];    // bends, then the target
  window.__txLeaders = [{ target: "the substation's fence line",
                          at: SITE, to: leader[leader.length - 1] }];
  ```

  qa.py FAILS when `to` and `at` are more than 24 design px apart. No pixel test can settle
  this, because the landing tick puts ink at the terminus either way, and a leader stopping in
  void looks exactly like a leader reaching something small. The discipline is the point:
  writing `at:` forces you to go find the target.

### Determinism

Seed all noise: `TX.reseed(seed)` and `TX.rng(seed)`. Derive the seed from the run date. The
same inputs must reproduce the same pixels, because a repair pass otherwise repaints art a
pixel critic already reviewed, and the shipped PNG cannot be rebuilt from the committed HTML.

**ENFORCED**: render.py scans each slide's inline scripts and qa.py FAILS `Math.random()`,
`crypto.getRandomValues()` and `crypto.randomUUID()`, and WARNs on `Date.now()` and
`new Date()`, naming the line. A vendored library loaded by `src=` is not read.

**THE TRAP THAT COSTS A WHOLE SLIDE.** `TX.rng(seed)` RETURNS A GENERATOR FUNCTION. It does not
return a number.

```js
const R = TX.rng(20260812);       // correct: R is a generator
let x = R() * 1080;               // correct: a number

let x = TX.rng() * 1080;          // WRONG: function times number is NaN
```

NaN coordinates draw nothing and throw nothing. render.py reports zero errors and zero
warnings, and the slide comes out blank. The near-uniform canvas gate is what catches it, so
never ship a slide whose canvas gate you have not read.

### Fonts

Use the families in `assets/fonts/fonts.css`: Fraunces (100-900 plus italic, opsz), JetBrains
Mono (400/500/700), Space Grotesk (300-700), Archivo (100-900, stretch 62 to 125 percent),
Manrope (200-800), Instrument Serif (plus italic), Bricolage Grotesque (200-800, stretch 75 to
100), Unbounded (200-900). Never request a weight or family not declared there; QA fails
missing fonts. No faux bold or italic.

The house pairing is Fraunces for display, Manrope for body, JetBrains Mono for anything that
is a measurement. Figures are set in mono with tabular numerals, because a figure on this
product is a measurement and columns of measurements must align.

## Hard numbers (QA enforces the starred ones)

- Canvas 1080x1350 (4:5). PDF page is the same. *Body overflow is a hard fail.*
- *Text floor 24px* (warn), body text 32px or more, headlines 60-110px, hook display 120-170px.
  A 1080px canvas reads at about 390px on a phone, which is 0.36x.
- Safe zone: primary text inside **80px margins** (warn outside); keep about 150px clear top
  and bottom for platform UI.
- Contrast: body text 4.5:1 or better against its LOCAL background. QA estimates the worst
  point along the run of the text, not the mean: type over a gradient can average 10:1 and
  still fall to 2:1 somewhere. The fix is a reserve, a scrim that lifts the floor under the
  whole text block, or moving the type off the graded band entirely.

  Watch for figure and ground drawn from the same palette family. An ember headline over an
  ember dusk band is the same colour in the same place, and no weight fixes it.
- *Canvas health:* see the near-uniform and backing-store rules above.
- PDF: vector mode required (`assemble_report.json` has `pdf_mode: "vector"`), target 2 to
  25 MB.

## In this directory

- `render.py` — HTML to PNG at 2x, plus in-page QA extraction (`render_report.json`)
- `qa.py` — machine gate over the PNGs (`machine_qa.json`, exit 1 on FAIL)
- `assemble.py` — vector PDF (Chromium print plus pypdf merge), contact sheet, 432px feed
  thumbs (`assemble_report.json`)
- `bootstrap.sh` — pip deps. It also repairs a known broken pypdf import: some distributions
  ship a cryptography build whose rust binding panics at import, which would kill the vector
  PDF path mid-run. The probe runs in a subprocess because a panic can poison the interpreter.

## Art libraries (committed, offline)

All under `assets/js/`, all zero-network, all deterministic per seed.

| file | global | what it is |
|---|---|---|
| `noise.js` | `TX` | seeded simplex 2D/3D, fBm, domain warp, seeded PRNG, grain tiles |
| `txgeo.js` | `TXGeo` | the Texas Albers projection, counties, borders mesh, place anchors |
| `tx3d.js` | `TX3D` | software 3D on Canvas 2D: camera, heightfield, box, line3d, fog |
| `txtype.js` | `TX` | display type fitting, `svgPlate` measured from the laid-out text |
| `txlabel.js` | `TX` | knockout-plate canvas labels |
| `txcolor.js` | `TXC` | OKLCH palette engine |
| `txcarve.js` | `TXCARVE` | wind-worked surfaces and two-part contact shadows |
| `txhachure.js` | `TX` | slope and aspect hachure fields |
| `txrelief.js` | `TX` | 2.5D relit heightfield form shading |
| `txsdf.js` | `TXSDF` | CPU signed-distance-field raymarcher |
| `txengrave.js` | `TXENGRAVE` | white-line intaglio, the engraving bench |
| `txpost.js` | `TXPOST` | film-grade post-processing for slide canvases |
| `txthree.js` | — | the GPU illustration bench (three.js plus SwiftShader) |
| `d3.v7.min.js`, `topojson-client.min.js`, `zdog.min.js`, `three.module.min.js` | vendor | untouched |

`TXGeo` uses the same Albers equal-area conic the website's map builder uses, so a slide and
the site agree about where places are. `tests/txgeo.mjs` asserts that, and asserts the map is
neither upside down nor mirrored, because Albers y grows northward while screen y grows
downward and nothing in either library objects.
