#!/usr/bin/env python3
"""Emit the three frames of the FIGURE BEARING reference.

WHAT THIS PROVES, and it is one thing rather than a deck. THE ARTWORK CARRIES THE DATA, in
knowledge/carousel/ILLUSTRATION_SYSTEM.md, says a frame's geometry is a computed figure. Before
this existed there was NO EXAMPLE ANYWHERE IN THIS REPO of a frame that does it: every deck in
the history reports 0 of 9 frames mapping a figure onto drawn geometry, so a run reading the law
had the rule and nothing to copy. The reference corpus this machine is measured against has 59
decks of examples.

Three frames, three different figures, three different ways of drawing a number:

    frame 1   ISOTYPE      4,749 active systems, one mark per 50, marks laid in rows
    frame 2   COLUMNS      3,579 of 4,749, two column heights in the same scale
    frame 3   ONE ROW      87 returned by the third query, against the 3,579 ghosted behind

Every count on the canvas is derived from `figures.json` in this directory by the frame's own
code. Nothing here is a number a person chose for looking right, which is the same law the prose
has always answered to, applied to the picture.

It reuses the 2026-09-16 lamp chassis rather than writing a fourth world, because what is being
demonstrated is the data-to-geometry step and a new chassis would only add a variable. A real run
writes its own, per THE CHASSIS LAW.

    python3 examples/figure-bearing/build.py out/fb/slides
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "slides"
OUT.mkdir(parents=True, exist_ok=True)
FIG = json.loads((HERE / "figures.json").read_text(encoding="utf-8"))

SHELL = """<!doctype html>
<!-- FIGURE BEARING REFERENCE, frame {n} of 3. Archetype {arch}.
     data_in_art: {fig} drives {drives}.
{note} -->
<html>
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="@@ASSETS@@/fonts/fonts.css">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ width:1080px; height:1350px; overflow:hidden; background:#08060F; }}
  body {{ position:relative; font-family:"Manrope", sans-serif; -webkit-font-smoothing:antialiased; }}
  canvas#art {{ position:absolute; left:0; top:0; width:1080px; height:1350px; }}
  .hook {{ position:absolute; font-family:"Fraunces", serif; font-weight:700;
          line-height:0.99; letter-spacing:-0.022em; color:#F2E9DA;
          font-variation-settings:"opsz" 144; z-index:10; }}
  .dek {{ position:absolute; font-size:30px; line-height:1.42; color:#BEB2A4; z-index:10; }}
  .tx-site {{ position:absolute; right:80px; bottom:80px; font-family:"JetBrains Mono", monospace;
             font-size:24px; letter-spacing:0.07em; line-height:1.5; color:#6E6376;
             white-space:nowrap; z-index:20; }}
  .hook {{ left:84px; top:130px; width:880px; font-size:96px; }}
  .dek  {{ left:84px; top:{dek}px; width:700px; }}
{css}
</style>
</head>
<body>
<canvas id="art" width="2160" height="2700"></canvas>
<div class="tx-site" id="site" style="color:#A99CB2">texasaidocket.com</div>
{dom}
<script src="@@ASSETS@@/js/noise.js"></script>
<script src="@@ASSETS@@/js/txtype.js"></script>
<script src="@@ASSETS@@/js/txcolor.js"></script>
<script src="@@ASSETS@@/js/txpost.js"></script>
<script src="@@ASSETS@@/js/txdeck.js"></script>
<script src="@@ASSETS@@/js/txscene.js"></script>
<script src="@@ASSETS@@/js/deck/2026-09-16-lamp.js"></script>
<script src="@@ASSETS@@/js/txlayout.js"></script>
<script>
window.renderReady = new Promise(async function (resolve, reject) {{
  try {{
    await document.fonts.ready;
    TX.reseed({seed});
    TXLAYOUT.mount(document.body, {{
      kicker: '{kick}', counter: "0{n} / 03", src: '{src}', ink: '#A99CB2'
    }});
    TX.fitText(document.getElementById("hook"), {{ min: 68, max: 96, maxLines: 3 }});
    var cv = document.getElementById("art"), cx = cv.getContext("2d");
    cx.scale(2, 2);
    var W = 1080, H = 1350, Lm = TXLAMP;
    var boxes = TXDECK.lineBoxes(".hook, .dek, .kick, .ctr, .src, .lab, .tx-site", 18);
    var mask  = TXDECK.reserveMask(boxes, 30);

    // THE BENCH. One ground plane, one camera, and the CHASSIS's light rather than a second
    // copy of it. depth_floor.py fails a frame whose scene light disagrees with the deck's.
    var S = TXSCENE.create(cx, {{
      w: W, h: H, eye: 1.4, horizon: 560, f: 820,
      sky: "#1A1630", fogZ: 42, light: {{ az: 64, el: 26 }}
    }});
{body}
    TXDECK.finish(cx, {{ mask: mask }});
    resolve(true);
  }} catch (e) {{ reject(e); }}
}});
</script>
</body>
</html>
"""

# ---------------------------------------------------------------------------------------------
# FRAME 1. ISOTYPE, STANDING ON A GROUND PLANE. The count is the mark count and the marks are
# SOLIDS at true scale, ten to a row, rows receding from 4 to 13 metres. Every depth cue the
# bench has falls out of that one decision: they get smaller with distance (relative size), sit
# higher in the frame (height in field), pack denser (texture gradient), wash toward the sky
# (aerial), turn a lit face to the west door (form shading) and each throws a cast shadow east.
ONE_MARK_IS = 50
F1 = """
    var ACTIVE = @@ACTIVE@@, PER = @@PER@@;      // figures.json active_systems
    var marks = Math.round(ACTIVE / PER);        // 95, and the field IS that number
    var cols = 10, pitchX = 0.62, z0 = 4.0, dz = 1.0;
    var mw = 0.30, mh = 0.42, md = 0.30;

    S.ground({ near: 1.2, far: 90, fill: "#171233", fadeToSky: true });
    S.gridZ({ dz: 1.0, from: z0 - 0.5, to: z0 + 10.5, ink: "rgba(224,149,106,0.10)", width: 1.1 });

    // FAR FIRST. The bench does not z-sort, deliberately, so occlusion is the drawer's order.
    var rows = Math.ceil(marks / cols);
    for (var r = rows - 1; r >= 0; r--) {
      var Z = z0 + r * dz;
      var inRow = Math.min(cols, marks - r * cols);
      for (var c = 0; c < inRow; c++) {
        var X = (c - (cols - 1) / 2) * pitchX;
        // the last mark is the REMAINDER and is drawn short, because 4,749 is not 95 fifties
        var last = (r * cols + c) === marks - 1 && (ACTIVE % PER !== 0);
        var hh = last ? mh * ((ACTIVE % PER) / PER) : mh;
        S.box({ X: X, Z: Z, w: mw, h: hh, d: md, fill: "#C9BEE4",
                shadowInk: "#0A0718", shadowAlpha: 0.34 });
      }
    }
"""


# ---------------------------------------------------------------------------------------------
# FRAME 2. A FILL LEVEL IN A VOLUME. The share is a SOLID standing inside the wireframe of the
# whole, one footprint, one scale, so 3,579 of 4,749 reads as a level rather than as a second
# quantity standing next to the first.
F2 = """
    var ALL = @@ALL@@, SMALL = @@SMALL@@;        // figures.json active_systems, small_systems
    var Z = 6.0, bw = 2.0, bd = 2.0, hAll = 1.40;   // hAll == eye height, so the whole
                                                   // volume tops out ON the horizon
    var hSm = hAll * (SMALL / ALL);              // the level, computed and not chosen

    S.ground({ near: 1.2, far: 90, fill: "#171233", fadeToSky: true });
    // S.strip takes X, w, near, far, fill. It took from/to/ink once and silently drew its
    // default 6 m band from 0.8 to 400 m, which is a grey wedge over two thirds of the frame.
    S.strip({ X: 0, w: 6.0, near: 3, far: 26, fill: "rgba(224,149,106,0.05)" });
    S.gridZ({ dz: 1.2, from: 3, to: 26, ink: "rgba(224,149,106,0.13)", width: 1.3 });
    // gridX takes X extents in from/to and Z extents in near/far. gridZ takes Z in
    // from/to. They are not the same shape and the wrong one draws off frame in silence.
    S.gridX({ dx: 1.5, from: -7, to: 7, near: 3, far: 26,
              ink: "rgba(224,149,106,0.09)", width: 1.1 });

    // the solid: the share, lit and shadowed off the deck's one light
    S.box({ X: 0, Z: Z, w: bw, h: hSm, d: bd, fill: "#CFC3E8",
            shadowInk: "#0A0718", shadowAlpha: 0.30, shadowBlur: 14 });

    // the whole, as a wireframe standing in the same footprint. Drawn through S.project so the
    // verticals converge with everything else in the frame rather than being drawn upright.
    var x0 = -bw / 2, x1 = bw / 2, zA = Z, zB = Z + bd;
    var P = function (x, y, z) { return S.project(x, y, z); };
    var top = [P(x0, hAll, zA), P(x1, hAll, zA), P(x1, hAll, zB), P(x0, hAll, zB)];
    cx.save();
    cx.strokeStyle = "rgba(224,149,106,0.60)";
    cx.lineWidth = 2.2;
    cx.beginPath();
    top.forEach(function (pt, i) { i ? cx.lineTo(pt[0], pt[1]) : cx.moveTo(pt[0], pt[1]); });
    cx.closePath(); cx.stroke();
    [[x0, zA], [x1, zA], [x1, zB], [x0, zB]].forEach(function (c) {
      var a = P(c[0], 0, c[1]), b = P(c[0], hAll, c[1]);
      cx.beginPath(); cx.moveTo(a[0], a[1]); cx.lineTo(b[0], b[1]); cx.stroke();
    });
    cx.restore();
"""


# ---------------------------------------------------------------------------------------------
# FRAME 3. THE SAME FIELD, ONE SCALE, WITH THE SLIVER LIT. Frame 1's grid at frame 1's pitch and
# depths, held back, and the 87 picked out of it at 87/50 of a mark. A second scale would let
# this frame draw 87 as large as 3,579 without anybody noticing, which is the lie it refuses.
F3 = """
    var BIG = @@BIG@@, ALL = @@ALL@@, PER = 50;  // figures.json large_systems, active_systems
    var marks = Math.round(ALL / PER), lit = BIG / PER;
    var cols = 10, pitchX = 0.62, z0 = 4.0, dz = 1.0;
    var mw = 0.30, mh = 0.42, md = 0.30;

    S.ground({ near: 1.2, far: 90, fill: "#171233", fadeToSky: true });
    S.gridZ({ dz: 1.0, from: z0 - 0.5, to: z0 + 10.5, ink: "rgba(224,149,106,0.10)", width: 1.1 });

    var rows = Math.ceil(marks / cols);
    for (var r = rows - 1; r >= 0; r--) {
      var Z = z0 + r * dz;
      var inRow = Math.min(cols, marks - r * cols);
      var lead = Math.floor((cols - Math.ceil(lit)) / 2);   // the sliver sits mid row, not on the edge
      for (var c = 0; c < inRow; c++) {
        var i = r * cols + (c - lead);
        var X = (c - (cols - 1) / 2) * pitchX;
        var on = r === 0 && i >= 0 && i < lit;
        var frac = on ? Math.min(1, lit - i) : 1;
        S.box({ X: X, Z: Z, w: mw * (on ? frac : 1), h: mh, d: md,
                fill: on ? "#F0E6FF" : "#332A55",
                shadowInk: "#0A0718", shadowAlpha: on ? 0.40 : 0.16 });
      }
    }
"""


FRAMES = [
    dict(n=1, arch="GRID", fig="active_systems", drives="mark count", seed=20260921,
         kick="What the record holds", src="c1   TEXAS AI DOCKET", dek=430,
         note="     One mark per 50 systems. The field IS the count and the last mark is short,\n"
              "     because 4,749 is not 95 fifties and rounding it would be a typed number.",
         hook="Texas runs 4,749 community water systems.",
         deck="Every one of them is on the EPA's own record, and the record is public.",
         css="", body=F1.replace("@@ACTIVE@@", str(FIG["active_systems"]["value"]))
                 .replace("@@PER@@", str(ONE_MARK_IS))),
    dict(n=2, arch="OBJECT_AND_CAPTION", fig="small_systems", drives="column height",
         seed=20260922, kick="What most of them are", src="c1 c2   TEXAS AI DOCKET", dek=430,
         note="     The share is drawn INSIDE the whole at one scale. Two free standing bars\n"
              "     would draw a comparison of strangers rather than a part of something.",
         hook="3,579 of them serve fewer than 3,301 people.",
         deck="The filled column is that share, at the same scale as the whole beside it.",
         css="", body=F2.replace("@@ALL@@", str(FIG["active_systems"]["value"]))
                 .replace("@@SMALL@@", str(FIG["small_systems"]["value"]))),
    dict(n=3, arch="GRID", fig="large_systems", drives="mark count", seed=20260923,
         kick="What the large end looks like", src="c1 c3   TEXAS AI DOCKET", dek=430,
         note="     Frame 1's field redrawn at frame 1's scale, with the 87 picked out of it as a\n"
              "     1.74 mark sliver. A second scale would have let this frame draw 87 as big as\n"
              "     3,579 without anybody noticing, which is the lie this frame refuses.",
         hook="87 of them serve more than 50,000.",
         deck="Drawn on frame 1's scale, where one mark is 50 systems. The large end is under two marks of 95.",
         css="", body=F3.replace("@@BIG@@", str(FIG["large_systems"]["value"]))
                 .replace("@@ALL@@", str(FIG["active_systems"]["value"]))),
]

for f in FRAMES:
    dom = (f'<h1 class="hook" id="hook">{f["hook"]}</h1>\n'
           f'<p class="dek">{f["deck"]}</p>')
    (OUT / f"slide-{f['n']:02d}.html").write_text(
        SHELL.format(dom=dom, **{k: v for k, v in f.items() if k not in ("hook", "deck")}),
        encoding="utf-8")
print(f"wrote {len(FRAMES)} frames to {OUT}")
