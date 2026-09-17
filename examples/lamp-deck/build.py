#!/usr/bin/env python3
"""Emit the nine frames of carousel No. 26R. Each BODY below is hand written for its frame.

This script is a convenience for writing nine files in one go, not a template: the only thing
shared is the shell (fonts, furniture, load order), which bespoke_check.py strips before it
measures anything, exactly so a shared shell cannot put a floor under the score.
"""
import pathlib, sys

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("out/26R/slides")
OUT.mkdir(parents=True, exist_ok=True)

SHELL = """<!doctype html>
<!-- CAROUSEL 26R, frame {n} of 9. Archetype {arch}.
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
{css}
</style>
</head>
<body>
<canvas id="art" width="2160" height="2700"></canvas>
<div class="tx-site" id="site" style="color:{site}">texasaidocket.com</div>
{dom}
<script src="@@ASSETS@@/js/noise.js"></script>
<script src="@@ASSETS@@/js/txtype.js"></script>
<script src="@@ASSETS@@/js/txcolor.js"></script>
<script src="@@ASSETS@@/js/txpost.js"></script>
<script src="@@ASSETS@@/js/txdeck.js"></script>
<script src="@@ASSETS@@/js/deck/lamp.js"></script>
<script src="@@ASSETS@@/js/txlayout.js"></script>
<script>
window.renderReady = new Promise(async function (resolve, reject) {{
  try {{
    await document.fonts.ready;
    TX.reseed({seed});
    TXLAYOUT.mount(document.body, {{
      kicker: {kicker!r}, counter: "{n:02d} / 09", src: {src!r}, ink: {ink!r}
    }});
{fit}
    var cv = document.getElementById("art"), cx = cv.getContext("2d");
    cx.scale(2, 2);
    var W = 1080, H = 1350, Lm = TXLAMP;

    // TYPE RESERVES, measured off the real fitted type, handed to the art BEFORE it draws.
    // No plate. The quiet the type sits in is quiet the picture actually has.
    // TWO RESERVES, because the two kinds of type on this deck want OPPOSITE things from the
    // lamp, and the third build of this frame set used one list for both and was wrong twice.
    //
    //   LIGHT ON DARK (.hook, .dek, .lab and the furniture) sits on the dark desk. The pool
    //   washing across it destroys the contrast, so the LIGHT is dimmed toward those words.
    //
    //   DARK ON LIGHT (.doc) is ink printed ON a lit sheet. It NEEDS the light. Punching the
    //   pool away from it is what put a dark blob behind the footnote on frame 7 and took its
    //   contrast DOWN, which is the same mistake as a plate with the sign flipped.
    //
    // Both lists are reserved from the drawn EDGES (rules, bezels, sheet edges) via Lm.quiet,
    // because a line through a glyph is a strike whichever way round the values run.
    var boxes = TXDECK.lineBoxes(".hook, .dek, .kick, .ctr, .src, .lab, .doc, .tx-site", 18);
    var lit   = TXDECK.lineBoxes(".hook, .dek, .kick, .ctr, .src, .lab, .tx-site", 18);
    var mask  = TXDECK.reserveMask(boxes, 30);

{art}

    // THE LAST LINE THAT TOUCHES THE ART CANVAS, ON EVERY FRAME, WITH THE DECK'S ONE GRADE.
    TXDECK.finish(cx, {{ w: W, h: H{finish} }});
    resolve();
  }} catch (e) {{ reject(e); }}
}});
</script>
</body>
</html>
"""

FRAMES = []

# ---------------------------------------------------------------- 1. inside the page
FRAMES.append(dict(
    n=1, arch="CLOSE_CROP", seed=20260916,
    note="""     THE COVER. The camera is 0.32 m above a student's own page, cropped by three edges so the
     reader is inside it. The lamp is up and to the right and the pool falls across the working.
     THE RULED ANSWER LINE IS EMPTY and it stays empty for nine frames. The machine's entire
     contribution is ONE 9 mm tick in the margin beside line seven, and you have to look for it.
     The working is TOKEN STROKES and never letterforms, so the frame prints no word and no
     numeral that no source contains. Planned frame median L* 22.""",
    kicker="The hint, at its actual size", src="c15 c10 c4   TEXAS AI DOCKET",
    css="""  .hook { left:84px; top:158px; width:880px; font-size:118px; }
  .dek  { left:84px; top:454px; width:760px; }""",
    dom="""<h1 class="hook" id="hook">It was built to not tell you.</h1>
<p class="dek">A federal grant is paying for a tutor that answers a student with a hint.</p>""",
    fit='    TX.fitText(document.getElementById("hook"), { min: 84, max: 118, maxLines: 3 });',
    art="""    // the desk the page lies on, running off all three lower edges
    Lm.desk(cx, { y: 0, mask: mask, seed: 12, lampX: 880, lampY: 190 });

    // THE SHEET, bigger than the frame on three sides. The reader is inside it.
    var PX = -70, PY = 560, PW = 1290, PH = 980;
    Lm.sheet(cx, { x: PX, y: PY, w: PW, h: PH, rot: -0.013, seed: 31 });

    // the lamp's pool, landing on the page from the upper right
    Lm.pool(cx, { x: 905, y: 505, r: 760, squash: 0.60, rot: -0.20, strength: 1.0, reserve: lit });

    // the pad's ruled lines, and the margin rule the one mark sits outside of
    Lm.quiet(cx, boxes, function (g) {
      for (var rl = PY + 96; rl < PY + PH - 40; rl += 58) {
        Lm.rule(g, { x0: PX + 34, x1: PX + PW - 30, y: rl });
      }
    });
    cx.save();
    cx.strokeStyle = "rgba(196,110,96,0.30)"; cx.lineWidth = 2.4;
    cx.beginPath(); cx.moveTo(PX + 196, PY); cx.lineTo(PX + 196, PY + PH); cx.stroke();
    cx.restore();

    // the student's own working, seven lines of it, thinning as it goes down the page
    Lm.working(cx, { x: PX + 232, y: PY + 152, lines: 7, step: 58,
                     min: 300, jitter: 470, weight: 3.6, seed: 811 });

    // THE ANSWER LINE, heavier than the rules above it, and nothing on it
    Lm.rule(cx, { x0: PX + 196, x1: PX + 1050, y: PY + 806, answer: true });

    // THE ONE MARK THE MACHINE MADE, in the margin beside line seven
    Lm.tick(cx, { x: PX + 168, y: PY + 486, w: 9, h: 46, glow: 30 });

    // the lamp dying at the near edge of the desk, which is what lets the furniture read
    Lm.falloff(cx, { from: 1178, mid: 0.72, end: 0.94 });

    // the lamp itself, top right, telling the reader where the light is
    Lm.shade(cx, { x: 1016, y: 132, s: 0.82, rot: 0.16 });"""))

# ---------------------------------------------------------------- 2. the award record
FRAMES.append(dict(
    n=2, arch="DOCUMENT", seed=20260917,
    note="""     THE FEDERAL RECORD, on the same desk, under the same lamp, the camera lifted a little and
     swung left. The award page is the subject and its own typography is the image. The quote is
     the government's words, verbatim, and the two lines around it are set in the page's own
     face rather than the deck's, because type ON a document is image and not caption.
     Planned frame median L* 20.""",
    kicker="The federal award record", src="c31 c22 c30   TEXAS AI DOCKET",
    css="""  .hook { left:84px; top:150px; width:840px; font-size:96px; }
  .dek  { left:84px; top:404px; width:700px; }
  .doc  { position:absolute; font-family:"Instrument Serif", serif; color:#2B211A; z-index:9; }
  .doc.t{ left:282px; top:700px; width:576px; font-size:27px; line-height:1.34; color:#3A2E24; }
  .doc.q{ left:282px; top:868px; width:576px; font-size:31px; line-height:1.36; color:#1C1510; }
  .doc.m{ left:282px; top:598px; font-family:"JetBrains Mono", monospace; font-size:17px;
          letter-spacing:.10em; color:#5A4636; }""",
    dom="""<h1 class="hook" id="hook">The problem, in the government's words.</h1>
<p class="dek">The award that paid for the tutor says why it exists.</p>
<div class="doc m" data-decorative>AWARD 2539663 . STANDARD GRANT . IUSE</div>
<div class="doc t">Context-Aware Conversational Tutors for Longitudinal Learning in Engineering Education</div>
<div class="doc q">"students frequently use them to obtain answers rather than develop the reasoning and problem-solving skills that define engineering competence"</div>""",
    fit='    TX.fitText(document.getElementById("hook"), { min: 72, max: 96, maxLines: 3 });',
    art="""    // the desk, darker here because the page carries the light
    Lm.desk(cx, { y: 0, mask: mask, seed: 55, lampX: 300, lampY: 240 });

    // the award page, stood almost square to the camera, cropped at the foot
    var DX = 196, DY = 556, DW = 712, DH = 632;
    Lm.sheet(cx, { x: DX, y: DY, w: DW, h: DH, rot: 0.008, seed: 62, lit: 7, shade: 4 });

    // the pool, from the upper LEFT this frame because the camera swung, not the lamp.
    // The cast still runs down and right of every object, which is what keeps it one lamp.
    Lm.pool(cx, { x: 470, y: 856, r: 940, squash: 0.74, rot: 0.22, strength: 0.86, reserve: lit });

    // the page's own rules: a head rule under the award line, a foot rule above the crop
    Lm.quiet(cx, lit, function (g) {
      g.save();
      g.strokeStyle = "rgba(200,182,158,0.34)"; g.lineWidth = 1.6;
      g.beginPath(); g.moveTo(DX + 54, DY + 92); g.lineTo(DX + DW - 54, DY + 92); g.stroke();
      g.strokeStyle = "rgba(200,182,158,0.20)";
      g.beginPath(); g.moveTo(DX + 54, DY + 268); g.lineTo(DX + DW - 54, DY + 268); g.stroke();
      g.restore();
    });

    // the body of the abstract below the quote, as token strokes, falling off into the dark
    Lm.working(cx, { x: DX + 56, y: DY + 528, lines: 3, step: 32, min: 320, jitter: 220,
                     weight: 2.0, ink: "rgba(44,34,26,0.40)", seed: 404 });

    // the quote's own mark in the margin, the same 9 mm tick, now beside the government's words
    Lm.tick(cx, { x: DX + 14, y: DY + 268, w: 8, h: 132, glow: 12 });

    // the lamp's arm entering top left, the continuity object
    Lm.shade(cx, { x: 108, y: 118, s: 0.74, rot: -0.22 });"""))

# ---------------------------------------------------------------- 3. room one
FRAMES.append(dict(
    n=3, arch="FULL_BLEED", seed=20260918,
    note="""     ROOM ONE, ARLINGTON. The camera pulls all the way back off the desk for the first time.
     The desk and its pool are now the FOREGROUND, cropped at the bottom edge, and the room
     recedes into dark behind it: four rows of empty student desks, each row closer to the
     ground colour than the last, so distance reads as light and not merely as size.
     This is the establishing frame and frame 6 is its answer. Planned frame median L* 14.""",
    kicker="Room one, Arlington", src="c13 c33   TEXAS AI DOCKET",
    css="""  .hook { left:84px; top:150px; width:800px; font-size:100px; }
  .dek  { left:84px; top:408px; width:640px; }""",
    dom="""<h1 class="hook" id="hook">The courses do not change.</h1>
<p class="dek">The instructor still teaches. The machine lives in the homework, across four undergraduate courses.</p>""",
    fit='    TX.fitText(document.getElementById("hook"), { min: 76, max: 100, maxLines: 3 });',
    art="""    // THE ROOM, four rows receding, each mixed further toward the ground colour.
    // Overlap and value carry the depth. Nothing is drawn smaller and called far away.
    var rows = [];
    for (var r = 0; r < 4; r++) {
      (function (r) {
        rows.push(function (c) {
          var t = r / 4;
          var y = 612 + r * 104;
          var sc = 1 - t * 0.30;
          for (var d = -1; d < 5; d++) {
            var x = 96 + d * 214 * sc + r * 58;
            c.beginPath();
            c.rect(x, y, 168 * sc, 13 * sc);                 // the desk top
            c.rect(x + 16 * sc, y + 13 * sc, 10 * sc, 58 * sc); // near leg
            c.rect(x + 140 * sc, y + 13 * sc, 10 * sc, 58 * sc);
            c.fill();
            // a chair back behind each, a second silhouette so the row is not a fence
            c.beginPath();
            c.rect(x + 52 * sc, y - 46 * sc, 66 * sc, 9 * sc);
            c.rect(x + 80 * sc, y - 46 * sc, 9 * sc, 46 * sc);
            c.fill();
          }
        });
      })(r);
    }
    Lm.room(cx, { layers: rows });

    // the far wall, the darkest thing in the deck, with the doorway's thin spill
    // the far wall, with the lamp's own falloff across it rather than a flat black fill
    cx.save();
    var wg = cx.createLinearGradient(1080, 300, 180, 596);
    wg.addColorStop(0, "#14101F"); wg.addColorStop(1, "#06040C");
    cx.fillStyle = wg; cx.fillRect(0, 0, W, 596);
    cx.fillStyle = "rgba(224,149,106,0.16)"; cx.fillRect(884, 388, 22, 208);
    cx.restore();

    // THE FOREGROUND DESK, cropped by the bottom edge, the reader's own seat
    Lm.desk(cx, { y: 1088, mask: mask, seed: 77, lampX: 858, lampY: 1140 });
    // clear of the site line's own band at right 80, because the cure for art under furniture
    // is to move the art, never to carve a hole in the light where the furniture sits
    var SX = 286, SY = 1088, SW = 448, SH = 300;
    Lm.sheet(cx, { x: SX, y: SY, w: SW, h: SH, rot: -0.02, seed: 90 });
    Lm.quiet(cx, boxes, function (g) {
      for (var q = SY + 44; q < SY + SH - 120; q += 46) {
        Lm.rule(g, { x0: SX + 26, x1: SX + SW - 24, y: q });
      }
    });
    // the pool, tight on the near page only, so the room stays dark
    Lm.pool(cx, { x: 536, y: 1104, r: 540, squash: 0.46, rot: -0.10, strength: 1.05, reserve: lit });

    // the lamp dying before the frame edge, which quiets the furniture band
    Lm.falloff(cx, { from: 1150, mid: 0.70, end: 0.95 });

    // no tick in this frame. The room is where the machine is not.
    Lm.shade(cx, { x: 946, y: 858, s: 0.62, rot: 0.10 });"""))

# ---------------------------------------------------------------- 4. the origin
FRAMES.append(dict(
    n=4, arch="CLOSE_CROP", seed=20260919,
    note="""     THE ORIGIN. Two pages on one desk under the one lamp: a child's working on the left and a
     student's on the right, the same hand-height apart a kitchen table puts them. Two ticks,
     one on each page, because the thing she saw was the same thing twice. The camera is back
     down at page height, which is frame 1's height, so the deck returns to where it began
     before it leaves for good. Planned frame median L* 19.""",
    kicker="The origin", src="c5 c11   TEXAS AI DOCKET",
    css="""  .hook { left:84px; top:150px; width:830px; font-size:100px; }
  .dek  { left:84px; top:412px; width:720px; }""",
    dom="""<h1 class="hook" id="hook">It started with her own children.</h1>
<p class="dek">Shuchi Deb is an associate professor at the University of Texas at Arlington. She watched her own children and her students use AI without learning.</p>""",
    fit='    TX.fitText(document.getElementById("hook"), { min: 76, max: 100, maxLines: 3 });',
    art="""    Lm.desk(cx, { y: 0, mask: mask, seed: 140, lampX: 540, lampY: 210 });

    // the LEFT page, the child's: larger letters, fewer lines, closer to the frame edge
    var AX = -54, AY = 700, AW = 560, AH = 640;
    Lm.sheet(cx, { x: AX, y: AY, w: AW, h: AH, rot: 0.022, seed: 151 });
    for (var a = AY + 78; a < AY + AH - 30; a += 74) {
      Lm.rule(cx, { x0: AX + 30, x1: AX + AW - 26, y: a });
    }
    Lm.working(cx, { x: AX + 92, y: AY + 132, lines: 4, step: 74, min: 180, jitter: 230,
                     weight: 5.2, seed: 1611 });

    // the RIGHT page, the student's: tighter, denser, running off the right edge
    var BX = 566, BY = 762, BW = 610, BH = 588;
    Lm.sheet(cx, { x: BX, y: BY, w: BW, h: BH, rot: -0.016, seed: 172 });
    for (var b = BY + 58; b < BY + BH - 20; b += 50) {
      Lm.rule(cx, { x0: BX + 26, x1: BX + BW - 20, y: b });
    }
    Lm.working(cx, { x: BX + 74, y: BY + 106, lines: 6, step: 50, min: 240, jitter: 300,
                     weight: 3.2, seed: 1733 });

    // ONE POOL over both, because it is one lamp and one kitchen table
    Lm.pool(cx, { x: 552, y: 792, r: 720, squash: 0.50, rot: -0.06, strength: 0.98, reserve: lit });

    // THE MOTIF DOUBLES. One tick per page, the same mark on two different hands.
    Lm.tick(cx, { x: AX + 54, y: AY + 250, w: 10, h: 52, glow: 30 });
    Lm.tick(cx, { x: BX + 42, y: BY + 214, w: 9, h: 44, glow: 26 });

    // the lamp dying at the near edge of the desk, which is what lets the furniture read
    Lm.falloff(cx, { from: 1178, mid: 0.72, end: 0.94 });

    Lm.shade(cx, { x: 596, y: 168, s: 0.70, rot: -0.04 });"""))

# ---------------------------------------------------------------- 5. the method
FRAMES.append(dict(
    n=5, arch="TYPE_AS_OBJECT", seed=20260920,
    note="""     THE METHOD, and the deck's one TYPE_AS_OBJECT. The university's own two words are CUT INTO
     the desk, not laid on it. The cut catches the lamp on its upper right lip and goes black on
     the lower left, which is the same light as every other frame and is the whole reason the
     words read as carved rather than as a font choice. The type here is DOM on top of a carved
     shadow drawn beneath it, so the glyphs stay vector in the PDF.
     Planned frame median L* 24.""",
    kicker="The method", src="c1 c32   TEXAS AI DOCKET",
    css="""  .hook { left:78px; top:566px; width:940px; font-size:170px; line-height:0.92;
          font-family:"Archivo", sans-serif; font-variation-settings:"wdth" 116,"wght" 800;
          letter-spacing:-0.035em; color:#F6EEE0; text-transform:lowercase; }
  .dek  { left:84px; top:1016px; width:720px; }
  .lab  { position:absolute; left:84px; top:158px; width:820px;
          font-family:"Instrument Serif", serif; font-size:44px; line-height:1.24;
          color:#C9B9A6; z-index:10; }""",
    dom="""<div class="lab">The university's own words for what it built.</div>
<h1 class="hook" id="hook">teaches,<br>not tells</h1>
<p class="dek">From the headline of the university's own release, September 10th, 2026.</p>""",
    fit='    TX.fitText(document.getElementById("hook"), { min: 132, max: 170, maxLines: 2 });',
    art="""    // the desk surface, and this frame is nothing but the desk
    Lm.desk(cx, { y: 0, mask: mask, seed: 220, lampX: 880, lampY: 460 });

    // THE CUT. For each line box of the headline, a dark trough offset down and left (the cast)
    // and a lit lip offset up and right (the lamp), so the words sit IN the wood.
    // THE CUT IS DONE IN CSS, ON THE TYPE ITSELF, AND TWO EARLIER BUILDS OF THIS FRAME WERE
    // WRONG IN TWO DIFFERENT WAYS BEFORE THAT.
    //
    // Build one drew a blurred rect per line box, which at thumb size reads as a highlighter
    // pen. A rect behind type is a plate however it is shaded, which is the defect this whole
    // deck exists to remove.
    //
    // Build two drew the words again on the canvas, offset either side of the cast direction.
    // That ghosted, and the reason is worth keeping: the headline is Archivo with
    // `font-variation-settings: "wdth" 116`, and `cx.font` HAS NO WIDTH AXIS. Canvas rendered
    // the same string at width 100, so the two copies agreed at the first letter and drifted
    // further apart with every glyph after it. A canvas copy of DOM variable-font text cannot
    // be registered to it, at any offset.
    //
    // A text-shadow pair is the same carve, it is applied to the glyphs themselves so it can
    // never drift, and the type stays vector in the PDF. The offsets below ARE the deck's cast
    // direction, computed rather than eyeballed, so the cut is lit by the same lamp as
    // everything else in the deck.
    var dir = TXDECK.castDir();
    document.getElementById("hook").style.textShadow =
        (dir[0] * 9).toFixed(1) + "px " + (dir[1] * 9).toFixed(1) + "px 11px rgba(2,1,5,0.95), " +
        (dir[0] * 3).toFixed(1) + "px " + (dir[1] * 3).toFixed(1) + "px 2px rgba(2,1,5,0.80), " +
        (-dir[0] * 2.5).toFixed(1) + "px " + (-dir[1] * 2.5).toFixed(1) +
        "px 1px rgba(250,214,168,0.40)";

    // the pool, wide and low, raking across the cut from the upper right
    Lm.pool(cx, { x: 872, y: 700, r: 940, squash: 0.62, rot: -0.16, strength: 1.0, reserve: lit });

    // the grain again ON TOP of the cut, at low alpha, so the wood runs THROUGH the letters
    // rather than stopping at them. A cut that the grain respects is a sticker.
    var R2 = TX.rng(931);
    cx.save();
    for (var g2 = 0; g2 < 2600; g2++) {
      var gx = R2() * W, gy = 480 + R2() * 700;
      cx.fillStyle = R2() > 0.5 ? "rgba(226,190,150,0.030)" : "rgba(4,3,8,0.055)";
      cx.fillRect(gx, gy, 9 + R2() * 26, 0.9);
    }
    cx.restore();

    Lm.shade(cx, { x: 1002, y: 300, s: 0.68, rot: 0.20 });"""))

# ---------------------------------------------------------------- 6. room two
FRAMES.append(dict(
    n=6, arch="FULL_BLEED", seed=20260921,
    note="""     ROOM TWO, FORT WORTH. THE TURN, AND IT IS FRAME 3's CAMERA WITH THE LAMP MOVED. Same
     geometry, same rows, same foreground desk, and the reader feels the second room before the
     headline argues it. The one new element is a terminal's cool glow, because a police
     training station is a lit thing and the lamp is not the only emitter here. Cool against
     warm is how the two rooms differ without the deck changing stock. Planned frame median
     L* 16.""",
    kicker="Room two, Fort Worth", src="c7 c8 c9   TEXAS AI DOCKET",
    css="""  .hook { left:84px; top:150px; width:860px; font-size:100px; }
  .dek  { left:84px; top:446px; width:660px; }""",
    dom="""<h1 class="hook" id="hook">The same machine is in a second room.</h1>
<p class="dek">Testing with the Fort Worth Police Department has already begun.</p>""",
    fit='    TX.fitText(document.getElementById("hook"), { min: 76, max: 100, maxLines: 3 });',
    art="""    // THE SAME ROWS AS FRAME 3, same pitch, same scale ladder, mirrored about the centre so
    // the room reads as its twin rather than its copy.
    var rows2 = [];
    for (var r = 0; r < 4; r++) {
      (function (r) {
        rows2.push(function (c) {
          var t = r / 4, y = 612 + r * 104, sc = 1 - t * 0.30;
          for (var d = -1; d < 5; d++) {
            var x = W - (96 + d * 214 * sc + r * 58) - 168 * sc;
            c.beginPath();
            c.rect(x, y, 168 * sc, 13 * sc);
            c.rect(x + 16 * sc, y + 13 * sc, 10 * sc, 58 * sc);
            c.rect(x + 140 * sc, y + 13 * sc, 10 * sc, 58 * sc);
            c.fill();
            c.beginPath();
            c.rect(x + 52 * sc, y - 46 * sc, 66 * sc, 9 * sc);
            c.rect(x + 80 * sc, y - 46 * sc, 9 * sc, 46 * sc);
            c.fill();
          }
        });
      })(r);
    }
    Lm.room(cx, { layers: rows2 });

    cx.save();
    var wg2 = cx.createLinearGradient(0, 300, 900, 596);
    wg2.addColorStop(0, "#121524"); wg2.addColorStop(1, "#06040C");
    cx.fillStyle = wg2; cx.fillRect(0, 0, W, 596);
    cx.restore();

    // THE TERMINAL, the one cool emitter, standing on the far side of the room
    Lm.quiet(cx, boxes, function (g) { Lm.glow(g, { x: 214, y: 470, r: 330 }); }, { feather: 40 });
    Lm.quiet(cx, boxes, function (g) {
      g.save();
      g.fillStyle = "#0B0A18";
      g.fillRect(140, 384, 168, 112);          // the screen's bezel, dark against its own light
      g.fillStyle = "rgba(150,186,226,0.30)";
      g.fillRect(150, 394, 148, 92);
      g.fillStyle = "#0E0C1C";
      g.fillRect(196, 496, 56, 46);            // the stand
      g.restore();
    });

    // the foreground desk, the lamp now on the LEFT, which is the whole turn
    Lm.desk(cx, { y: 1088, mask: mask, seed: 260, lampX: 262, lampY: 1140 });
    var TX2 = 346, TY2 = 1088, TW2 = 448, TH2 = 300;
    Lm.sheet(cx, { x: TX2, y: TY2, w: TW2, h: TH2, rot: 0.018, seed: 271 });
    Lm.quiet(cx, boxes, function (g) {
      for (var q2 = TY2 + 44; q2 < TY2 + TH2 - 120; q2 += 46) {
        Lm.rule(g, { x0: TX2 + 26, x1: TX2 + TW2 - 24, y: q2 });
      }
    });
    Lm.pool(cx, { x: 544, y: 1104, r: 540, squash: 0.46, rot: 0.12, strength: 1.02, reserve: lit });

    // ONE TICK, on the second room's page. The machine arrived here too.
    Lm.tick(cx, { x: TX2 + 30, y: TY2 + 84, w: 9, h: 44, glow: 26 });

    Lm.falloff(cx, { from: 1150, mid: 0.70, end: 0.95 });

    Lm.shade(cx, { x: 126, y: 864, s: 0.62, rot: -0.12 });"""))

# ---------------------------------------------------------------- 7. the foot of the page
FRAMES.append(dict(
    n=7, arch="DOCUMENT", seed=20260922,
    note="""     THE FOOT OF THE PAGE. Frame 2's document again and deliberately so, cropped this time to
     its last inch, where the second funder is a footnote under a rule. Two ticks in the margin,
     one per agency, and they are the same mark the machine has been making since frame 1.
     The award number is set in mono because it is a record and not prose.
     Planned frame median L* 20.""",
    kicker="The foot of the page", src="c7 c8 c9 c19 c24 c2   TEXAS AI DOCKET",
    css="""  .hook { left:84px; top:150px; width:800px; font-size:104px; }
  .dek  { left:84px; top:400px; width:700px; }
  .doc  { position:absolute; font-family:"Instrument Serif", serif; color:#2B211A; z-index:9; }
  .doc.f{ left:238px; top:900px; width:640px; font-size:25px; line-height:1.36; color:#17100B; }
  .doc.g{ left:238px; top:1064px; font-family:"JetBrains Mono", monospace; font-size:24px;
          letter-spacing:.09em; color:#5E2A0A; }""",
    dom="""<h1 class="hook" id="hook">Two agencies pay for this.</h1>
<p class="dek">The release names the National Science Foundation up top. The Department of Justice is a footnote.</p>
<div class="doc f">This work is sponsored by the Fort Worth Police Department and funded by the U.S. Department of Justice under Grant No.</div>
<div class="doc g">15PBJA-23-GG-06172-NTCP</div>""",
    fit='    TX.fitText(document.getElementById("hook"), { min: 78, max: 104, maxLines: 2 });',
    art="""    Lm.desk(cx, { y: 0, mask: mask, seed: 310, lampX: 820, lampY: 700 });

    // the page's LAST INCH, running off the left, right and bottom edges. The reader is at the
    // foot of a document whose top they have already seen on frame 2.
    var FX = -96, FY = 700, FW = 1280, FH = 502;
    Lm.sheet(cx, { x: FX, y: FY, w: FW, h: FH, rot: -0.007, seed: 322, lit: 7, shade: 6 });

    Lm.pool(cx, { x: 640, y: 940, r: 760, squash: 0.62, rot: -0.14, strength: 1.0, reserve: lit });

    // the body above the footnote, token strokes, so the eye goes to the rule and not the words
    Lm.working(cx, { x: FX + 330, y: FY + 62, lines: 3, step: 38, min: 380, jitter: 300,
                     weight: 2.2, ink: "rgba(44,34,26,0.38)", seed: 3311 });

    // THE FOOTNOTE RULE. A short rule, a third of the measure, which is how a footnote is set.
    Lm.quiet(cx, lit, function (g) {
      g.save();
      g.strokeStyle = "rgba(206,188,164,0.46)"; g.lineWidth = 2;
      g.beginPath(); g.moveTo(FX + 330, FY + 158); g.lineTo(FX + 700, FY + 158); g.stroke();
      g.restore();
    });

    // TWO TICKS, one per funder, at the two heights the two agencies sit at on the page.
    // The upper is NSF, named at the top and off this crop. The lower is the footnote.
    Lm.tick(cx, { x: FX + 272, y: FY + 34, w: 9, h: 84, glow: 14 });
    Lm.tick(cx, { x: FX + 272, y: FY + 188, w: 9, h: 148, glow: 16 });

    // the rest of the award's body below the grant number, so the bottom third of the frame
    // carries the page rather than trailing off into blank stock
    // THE BOTTOM THIRD OF FRAME 7, which measured 23 percent of the frame's own craft density.
    // Blank stock is not a composition. The page below the grant number now carries the rest of
    // the award's body over the page's own ruled bed, which is what the rest of a real award
    // page has on it.
    Lm.quiet(cx, boxes, function (g) {
      for (var fr = FY + 178; fr < FY + FH - 14; fr += 40) {
        Lm.rule(g, { x0: FX + 286, x1: FX + 1044, y: fr });
      }
      Lm.working(g, { x: FX + 316, y: FY + 196, lines: 5, step: 40, min: 420, jitter: 440,
                      weight: 3.2, ink: "rgba(30,23,17,0.60)", seed: 7788 });
      /* the signature block a federal award page ends on: two short rules and a dated line */
      g.save();
      g.strokeStyle = "rgba(48,37,28,0.52)"; g.lineWidth = 2;
      g.beginPath(); g.moveTo(FX + 316, FY + 392); g.lineTo(FX + 610, FY + 392); g.stroke();
      g.beginPath(); g.moveTo(FX + 700, FY + 392); g.lineTo(FX + 940, FY + 392); g.stroke();
      g.restore();
      Lm.working(g, { x: FX + 330, y: FY + 358, lines: 1, step: 30, min: 190, jitter: 70,
                      weight: 3.4, ink: "rgba(30,23,17,0.62)", seed: 991 });
      Lm.working(g, { x: FX + 714, y: FY + 358, lines: 1, step: 30, min: 150, jitter: 60,
                      weight: 3.0, ink: "rgba(30,23,17,0.58)", seed: 992 });
    });

    // the desk the page ends on, with its grain, so the band below the document is a surface
    // rather than a flat plane. A falloff that removes the detail it is quieting has not
    // quieted the frame, it has deleted the bottom of it.
    Lm.desk(cx, { y: FY + FH - 4, mask: mask, seed: 7303, lampX: 560, lampY: FY + FH + 40 });
    TXDECK.contact(cx, { x: 540, y: FY + FH + 8, w: 1080, h: 22, height: 10,
                         ambient: 0.42, contact: 0.66, ambientBlur: 26, contactBlur: 6 });

    Lm.shade(cx, { x: 892, y: 402, s: 0.64, rot: 0.14 });"""))

# ---------------------------------------------------------------- 8. three readings
FRAMES.append(dict(
    n=8, arch="GRID", seed=20260923,
    note="""     THREE READINGS, NO SCORE. Three pages side by side in one pool, the isotype: a count the
     reader can count. Each page carries ONE tick at a different height, because the machine
     reads three things and reports each separately. The pages are the same stock and the same
     size, which is what makes them a count rather than three pictures. Planned frame median
     L* 22.""",
    kicker="Three readings, no score", src="c8 c9   TEXAS AI DOCKET",
    css="""  .hook { left:84px; top:150px; width:800px; font-size:104px; }
  .dek  { left:84px; top:392px; width:700px; }
  .lab  { position:absolute; font-family:"JetBrains Mono", monospace; font-size:19px;
          letter-spacing:.08em; line-height:1.4; color:#B6A594; width:270px; z-index:10; }
  .lab.a{ left:66px;  top:1148px; }
  .lab.b{ left:404px; top:1148px; }
  .lab.c{ left:742px; top:1148px; }""",
    dom="""<h1 class="hook" id="hook">It reads three things.</h1>
<p class="dek">Kind and listening. Following what the person wants to talk about. Not connecting.</p>
<div class="lab a">KIND AND<br>LISTENING</div>
<div class="lab b">FOLLOWS THAT<br>CONVERSATION</div>
<div class="lab c">DOESN'T CONNECT<br>WITH THE PERSON</div>""",
    fit='    TX.fitText(document.getElementById("hook"), { min: 78, max: 104, maxLines: 2 });',
    art="""    Lm.desk(cx, { y: 0, mask: mask, seed: 360, lampX: 540, lampY: 480 });

    // ONE POOL over all three, drawn BEFORE the pages so it lights the desk they sit on
    Lm.pool(cx, { x: 540, y: 820, r: 880, squash: 0.60, rot: 0.0, strength: 1.02, reserve: lit });

    // THE THREE, identical stock at identical size. Only the tick's height differs, which is
    // the whole reading. A varying page size here would make it a chart of something else.
    var tickY = [232, 342, 452];
    for (var i = 0; i < 3; i++) {
      var x = 66 + i * 338, y = 690, w = 272, h = 404;
      Lm.sheet(cx, { x: x, y: y, w: w, h: h, rot: (i - 1) * 0.012, seed: 371 + i * 17 });
      Lm.quiet(cx, boxes, function (g) {
        for (var rl2 = y + 46; rl2 < y + h - 24; rl2 += 44) {
          Lm.rule(g, { x0: x + 22, x1: x + w - 20, y: rl2 });
        }
      });
      Lm.working(cx, { x: x + 52, y: y + 74, lines: 3, step: 44, min: 96, jitter: 120,
                       weight: 2.6, ink: "rgba(40,31,24,0.46)", seed: 3711 + i * 29 });
      // ONE tick per page, each at its own height
      Lm.tick(cx, { x: x + 28, y: y + tickY[i] - 190, w: 9, h: 40, glow: 24 });
    }

    // the pool again, at low strength, OVER the pages so the light is on them and not under
    Lm.pool(cx, { x: 540, y: 880, r: 640, squash: 0.40, rot: 0.0, strength: 0.34, reserve: lit });

    // the lamp dying at the near edge of the desk, which is what lets the furniture read
    Lm.falloff(cx, { from: 1178, mid: 0.72, end: 0.94 });

    Lm.shade(cx, { x: 556, y: 486, s: 0.56, rot: 0.02 });"""))

# ---------------------------------------------------------------- 9. nothing graded
FRAMES.append(dict(
    n=9, arch="CLOSE_CROP", seed=20260924,
    note="""     THE CLOSE, AND IT IS FRAME 1's CAMERA EXACTLY. Same height above the same page, same crop,
     same ruled answer line, and the lamp has burned down to its lowest strength in the deck.
     THERE IS NO TICK. The motif resolves to absence, because the award has not started and
     nothing has been graded, and the one mark the machine has made on every frame since the
     cover is simply not there. That is the argument drawn rather than captioned, and it is why
     this frame carries no new object at all. Planned frame median L* 13.""",
    kicker="The record's own dates", src="c27 c25 c13   TEXAS AI DOCKET",
    css="""  .hook { left:84px; top:150px; width:840px; font-size:104px; }
  .dek  { left:84px; top:404px; width:720px; }""",
    dom="""<h1 class="hook" id="hook">Nothing has been graded yet.</h1>
<p class="dek">The award starts October 1st, 2026 and runs to September 30th, 2029. Neither the university nor the federal record publishes a result.</p>""",
    fit='    TX.fitText(document.getElementById("hook"), { min: 78, max: 104, maxLines: 2 });',
    art="""    // frame 1's desk and frame 1's seed, so the grain is the same grain
    Lm.desk(cx, { y: 0, mask: mask, seed: 12, lampX: 880, lampY: 190 });

    // FRAME 1's SHEET, at frame 1's rect and frame 1's rotation
    var PX = -70, PY = 560, PW = 1290, PH = 980;
    Lm.sheet(cx, { x: PX, y: PY, w: PW, h: PH, rot: -0.013, seed: 31 });

    // the lamp at its lowest in the deck. Same place, less of it.
    Lm.pool(cx, { x: 905, y: 505, r: 660, squash: 0.60, rot: -0.20, strength: 0.66, reserve: lit });

    Lm.quiet(cx, boxes, function (g) {
      for (var rl3 = PY + 96; rl3 < PY + PH - 40; rl3 += 58) {
        Lm.rule(g, { x0: PX + 34, x1: PX + PW - 30, y: rl3 });
      }
    });
    cx.save();
    cx.strokeStyle = "rgba(196,110,96,0.22)"; cx.lineWidth = 2.4;
    cx.beginPath(); cx.moveTo(PX + 196, PY); cx.lineTo(PX + 196, PY + PH); cx.stroke();
    cx.restore();

    // THE ANSWER LINE, still empty, nine frames later
    Lm.rule(cx, { x0: PX + 196, x1: PX + 1050, y: PY + 806, answer: true });

    // AND NO TICK. Deliberately. The margin beside line seven is bare.

    Lm.falloff(cx, { from: 1178, mid: 0.72, end: 0.94 });

    Lm.shade(cx, { x: 1016, y: 132, s: 0.82, rot: 0.16 });"""))

# THE FURNITURE INK IS PER FRAME AND PER CORNER.
#
# One value for the whole deck was carried over from a deck that was dark everywhere, and on the
# frames where paper reaches the band it measured 2.4 to 3.6 against a 4.5 line. Per frame fixed
# most of it and left two, because on frames 2 and 7 the two bottom items sit on DIFFERENT
# grounds: the source line lands on the lit page and the site line lands on bare desk beside it.
# A frame is not one ground, so the ink is read per corner.
#
#   dark  #3E2F22  the item lands on lit paper
#   pale  #9D91A6  the item lands on the dark desk
# Every frame now ends on the deck's own dark at the furniture band, so the furniture is ONE
# ink across the deck, which is what it should have been from the start.
INK  = {n: "#A99CB2" for n in range(1, 10)}
SITE = {n: "#A99CB2" for n in range(1, 10)}

for f in FRAMES:
    f.setdefault("finish", "")
    f["ink"] = INK[f["n"]]
    f["site"] = SITE[f["n"]]
    (OUT / f"slide-{f['n']:02d}.html").write_text(SHELL.format(**f), encoding="utf-8")

print(f"wrote {len(FRAMES)} frames to {OUT}")
