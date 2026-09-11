# The editorial deck — a reference build of the illustration system

Nine frames re-drawing carousel no. 21's verified story with the libraries that shipped on
2026-09-11: `txscene.js`, `txfig.js`, `txobjects.js`, `txink.js` and `txlayout.js`. Every
claim id is that run's (`runs/carousel/2026-09-11/claims.json`) and every quoted string is
verbatim from it. It is not a shipped run. It is the bar.

- `slides/slide-01.html` to `slide-09.html`: the frames, each self-contained, each loading only
  `@@ASSETS@@` libraries.
- `storyboard.md`: the nine dossiers, each declaring `layout`, `primary_image` and `accent`
  beside the keys `dossier_check` already reads.
- `slide-NN.webp` and `contact_sheet.jpg`: the renders at 1080 by 1350, for a critic or a
  director to read.
- `render_report.json`: the render report the layout gate reads for text boxes.

The rotation: FULL_BLEED, DOCUMENT, FIGURE_SCALE, OBJECT_AND_CAPTION, GRID, DIAGRAM, CLOSE_CROP,
SPLIT_HORIZON, FULL_BLEED. Four screens: halftone at three cells, a line screen at two, a hatch,
a stipple twice.

To rebuild and check it:

    python3 .claude/skills/carousel-engine/render.py --slides-dir examples/editorial-deck/slides --out-dir out/upgrade/ed
    python3 .claude/skills/carousel-engine/qa.py --render-dir out/upgrade/ed
    python3 scripts/carousel/layout_check.py --run-dir examples/editorial-deck --require

`layout_check` reads the committed webps and the storyboard directly, so the third line runs on
a fresh clone with nothing rendered. `qa.py` reports WARN on the deck (safe zone notes on the
furniture) and no FAIL.

Read `knowledge/carousel/ILLUSTRATION_SYSTEM.md` for what each frame is demonstrating and why.
