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
# FRAME 1. ISOTYPE. The count IS the mark count, which is the oldest way of drawing a number and
# the one that survives a phone screen. One mark per 50 systems, so 4,749 lands at 95 marks: few
# enough to count a row of, many enough that the field reads as a quantity rather than a legend.
ONE_MARK_IS = 50
F1 = """
    var ACTIVE = @@ACTIVE@@, PER = @@PER@@;                 // figures.json active_systems
    var marks = Math.round(ACTIVE / PER);      // 95, and the grid is that number
    var cols = 19, rows = Math.ceil(marks / cols);
    var mw = 30, mh = 44, gx = 44, gy = 62;
    var x0 = (W - (cols * gx - (gx - mw))) / 2, y0 = 742;

    Lm.pool(cx, { x: 540, y: 968, r: 760, squash: 0.58, rot: -0.14, strength: 0.92, reserve: boxes });
    Lm.desk(cx, { y: 688, mask: mask, seed: 41, lampX: 540, lampY: 820 });

    var ramp = TXDECK.ramp();   // 7 steps. pick() takes an INDEX 0..6, not a fraction
    for (var i = 0; i < marks; i++) {
      var r = Math.floor(i / cols), c = i % cols;
      var x = x0 + c * gx, y = y0 + r * gy;
      // the last row is the remainder and is drawn short, because 4,749 is not 95 fifties
      var partial = (i === marks - 1) && (ACTIVE % PER !== 0);
      var h = partial ? mh * ((ACTIVE % PER) / PER) : mh;
      cx.fillStyle = TXDECK.pick(ramp, 5 - Math.floor(r / 2));
      cx.fillRect(x, y + (mh - h), mw, h);
      cx.fillStyle = TXDECK.pick(ramp, 1);
      cx.fillRect(x, y + mh + 4, mw, 3);       // the contact each mark stands on
    }
    Lm.falloff(cx, { from: 1196, mid: 0.70, end: 0.94 });
"""


# ---------------------------------------------------------------------------------------------
# FRAME 2. COLUMNS IN ONE SCALE. Two heights, one ladder, and the SMALL count is drawn inside the
# whole rather than beside it, because 3,579 of 4,749 is a share and two free standing bars would
# draw it as a comparison of strangers.
F2 = """
    var ALL = @@ALL@@, SMALL = @@SMALL@@;                  // figures.json active_systems, small_systems
    var base = 1108, top = 470, span = base - top;
    var wAll = 300, xAll = 150, xSm = 560;

    Lm.pool(cx, { x: 600, y: 940, r: 720, squash: 0.56, rot: -0.18, strength: 0.90, reserve: boxes });
    Lm.desk(cx, { y: 688, mask: mask, seed: 41, lampX: 540, lampY: 820 });
    var ramp = TXDECK.ramp();   // 7 steps. pick() takes an INDEX 0..6, not a fraction

    // the whole, drawn as an outline: it is the denominator and not a second quantity
    cx.strokeStyle = TXDECK.pick(ramp, 3);
    cx.lineWidth = 3;
    cx.strokeRect(xAll, top, wAll, span);
    cx.fillStyle = TXDECK.pick(ramp, 1);
    cx.fillRect(xAll, top, wAll, span);

    // the share, at the SAME scale, filled
    var hSm = span * (SMALL / ALL);
    cx.fillStyle = TXDECK.pick(ramp, 6);
    cx.fillRect(xSm, base - hSm, wAll, hSm);
    cx.strokeStyle = TXDECK.pick(ramp, 3);
    cx.strokeRect(xSm, top, wAll, span);

    // the rule the two stand on, and the one tick that marks the share on the whole
    cx.fillStyle = TXDECK.pick(ramp, 2);
    cx.fillRect(110, base, 840, 4);
    cx.fillStyle = TXDECK.pick(ramp, 5);
    cx.fillRect(xAll - 34, base - hSm, 30, 5);
    Lm.falloff(cx, { from: 1196, mid: 0.70, end: 0.94 });
"""


# ---------------------------------------------------------------------------------------------
# FRAME 3. ONE ROW AGAINST THE FIELD. 87 marks at the SAME pitch frame 1 used, so the swipe from
# a full field to a single short row is the argument, drawn. The 3,579 sits behind at low value:
# present, uncountable, which is what a number that size honestly looks like.
F3 = """
    var BIG = @@BIG@@, ALL = @@ALL@@, PER = 50;   // figures.json large_systems, active_systems
    var cols = 19, mw = 30, mh = 44, gx = 44, gy = 62;
    var field = Math.round(ALL / PER);            // frame 1's 95, redrawn at frame 1's pitch
    var lit = BIG / PER;                          // 1.74 marks, and the sliver is the argument
    var x0 = (W - (cols * gx - (gx - mw))) / 2, y0 = 742;
    var ramp = TXDECK.ramp();   // 7 steps. pick() takes an INDEX 0..6, not a fraction

    Lm.pool(cx, { x: 540, y: 968, r: 760, squash: 0.58, rot: -0.14, strength: 0.92, reserve: boxes });
    Lm.desk(cx, { y: 688, mask: mask, seed: 41, lampX: 540, lampY: 820 });

    for (var i = 0; i < field; i++) {
      var r = Math.floor(i / cols), c = i % cols;
      var x = x0 + c * gx, y = y0 + r * gy;
      // the whole record, held back, so the eye goes to what is picked out of it
      cx.fillStyle = TXDECK.pick(ramp, 2);
      cx.fillRect(x, y, mw, mh);
      // the 87, at the SAME scale, which is where the honesty of this frame lives: the large
      // end is under two marks of ninety five and drawing it any bigger would be a lie a
      // separate scale lets you tell without noticing
      if (i < lit) {
        var frac = Math.min(1, lit - i);
        cx.fillStyle = TXDECK.pick(ramp, 6);
        cx.fillRect(x, y, mw * frac, mh);
      }
      cx.fillStyle = TXDECK.pick(ramp, 1);
      cx.fillRect(x, y + mh + 4, mw, 3);
    }
    Lm.falloff(cx, { from: 1196, mid: 0.70, end: 0.94 });
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
