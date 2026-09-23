/* gensetyard.js — the chassis for carousel No. 32 (2026-09-23).
 *
 * WHAT THIS IS. The deck "THE DOOR THAT WAS ALWAYS THERE" spends nine frames on one gas
 * generation yard and the paper that yard has to come to, and argues that the Governor's
 * September 21st halt reaches projects the August 3rd audit structurally could not. Nine
 * frames share one light, one stock and one way of seating type, and this file is those
 * three things and nothing else. Every frame's COMPOSITION is written per frame.
 *
 * THE WORLD. A GAS GENERATION YARD ON A WEST TEXAS PAD AT TWENTY TO TEN AT NIGHT, LIT BY ITS
 * OWN MAST. Reciprocating gas sets in line on skids, their stacks going up out of the pool of
 * light into a sky with nothing in it, a switchgear house, a perimeter fence with a posted
 * notice wired to it. Inside that world, one interior the same fixture does not reach, which
 * is a counter where a permit is filed.
 *
 * WHY A YARD AT NIGHT, AND IT IS THE DECK'S ARGUMENT RATHER THAN A MOOD. The thing an air
 * permit regulates is the STACK. Not the building, not the racks, not the connection to the
 * grid. A project that contracts with the plant next door or stands its own engines behind
 * its own meter never enters the interconnection process the August audit reads, and the
 * audit never sees it. The engines are still engines. So the deck draws the engines, and the
 * one piece of paper that follows engines rather than wires.
 *
 * THE LIGHT, IN WORDS A FRAME AUTHOR CAN CHECK A DRAWING AGAINST. THE KEY IS A YARD MAST,
 * HIGH AND OFF THE CAMERA'S LEFT SHOULDER, AT 28 DEGREES ABOVE THE PLANE. So every lit face
 * in this deck is a LEFT face, every right face is the deck's dark side, and every cast runs
 * DOWN AND TO THE RIGHT at 1.88 times the object's own height. A 1.7 m person throws about
 * 3.2 m. A 3.0 m genset skid throws about 5.6 m. A 12 m stack throws about 22.6 m and runs
 * off the pad. If a drawn object has no contact where it meets the ground, or a cast running
 * left, that frame is wrong and gets redrawn rather than tuned.
 *
 * WHY A MAST RATHER THAN A SUN. Across twenty one decks the judges' finding was flatness, and
 * a mast is the honest cure rather than a stylistic one. A local source has a FALLOFF, so the
 * pad is lit and the sky and the far fence are not, which gives the type its quiet by
 * construction instead of by a plate. It is also when these yards are actually watched, and
 * the one frame that carries daylight is the counter, which is the point being made.
 *
 * THE GROUND WAS MEASURED, NOT CHOSEN. #322C44 is a night sky over a sodium lit pad. It sits
 * at dE76 14.18 from its nearest neighbour in the last six shipped grounds, against a floor of
 * 10, and its chroma is inside the band those six occupy so it reads as paper rather than as a
 * colour. The first two passes at this picked warm darks by eye and both landed inside dE 3 of
 * September 20th's #2E2016. A palette checked only by eye is a palette that repeats.
 *
 * THE ACCENT LAW, AND IT IS THE STRICTEST THING IN THIS FILE.
 *
 *     AMBER IS THE STATE'S PAPER. STEEL IS THE MACHINERY. THEY NEVER TOUCH.
 *
 * #E0A33F lands ONLY on a permit, a posted notice, a docket number and the comment door. It
 * never touches an engine, a stack, a skid, a container, a fence rail or the pad. The frames
 * that carry the machinery carry NONE AT ALL, and a reader who swipes twice has the code
 * without being told it. The deck's whole argument is that these are two separate systems and
 * that only one of them ever had to answer for the other.
 *
 * THE RESERVED RED IS NOT SPENT, DELIBERATELY. `signal_soon` #BF0A30 means a deadline inside a
 * week and nothing else on this project wears it. The report back is October 19th, which is
 * further out than that, and the Abilene comment file has no stated close date at all.
 * Spending the urgent colour on either would be this deck asserting an urgency the documents
 * do not carry.
 *
 * THE MUTE WORLD LAW, AND IT IS WHAT KEEPS AN INDUSTRIAL DECK FROM BEING NINE GREY BOXES.
 *
 *     PAPER IS THE ONLY THING IN THIS DECK THAT CARRIES GLYPHS.
 *
 * No manufacturer's plate on a genset, no door decal, no unit number stencilled on a skid, no
 * company name on the switchgear house, no sign at the gate. The world is mute and the paper
 * talks. It is also why no drawn yard can be read as one real facility, which matters because
 * the record names a permit number and a campus and gives no site plan.
 *
 * NOTHING IS DRAWN THAT HAS NOT HAPPENED. No permit is drawn refused, no stack is drawn
 * capped, no gate is drawn chained. The halt is an instruction to an agency about what it will
 * issue, and a drawing of a stopped construction site would publish a consequence nobody has
 * measured.
 *
 * THE FRAMES DRAW IN GREYS. Every scene is drawn into TXINK's offscreen twin in greys and the
 * print maps tone to ink on the deck's stock. That is why this file hands out a GREY SCALE
 * rather than a colour ramp. The one place real colour is painted is `over`, where the accent
 * and the type reserve go, after the screen has run.
 *
 * THE SCREEN IS A LINE SCREEN AT CELL 5, AND BOTH NUMBERS ARE PROBE FRAME DECISIONS. A LINE
 * screen is the banknote and the engineering sheet, which is what a permit drawing is, and it
 * is NOT the last three decks' screens: halftone at cell 7 on September 19th, hatch at cell 6
 * on September 20th, stipple at cell 5 on September 21st. Its gamma and perCell are NOT
 * guessed here. Phase 10.5 prints all nine steps of N.G as full width bands through this exact
 * press, reads each band's L* off the rendered PNG, and the numbers below are amended to what
 * that measured. September 21st shipped a scale spanning 95 L* in the twin that printed across
 * nineteen and was not monotonic, and five critics read that deck as hairline wireframes over
 * noise. Nothing was wrong with any frame's drawing. Every frame was drawing through a press
 * with no tonal range.
 */
(function (global) {
  "use strict";

  if (!global.TXDECK) throw new Error("gensetyard.js needs txdeck.js loaded first");

  /* ONE DECLARATION, AND IT IS THE ONLY ONE IN THE DECK. Nine frames can't hold nine lights. */
  TXDECK.declare({
    world: "gensetyard",
    light: { az: -48, el: 28, keyToFill: 6.2 },
    ground: "#322C44",
    material: "#CFD2D8",
    accent: "#E0A33F",
    grade: {
      exposure: -0.008,
      saturation: 1.02,
      contrast: 1.18,
      filmic: true,
      /* shadows toward the sky's own violet rather than to blue, highlights to a cool
       * discharge lamp rather than to a warm sun. A mast is not a sunset. */
      lift: [0.016, 0.012, 0.022],
      gain: [0.982, 1.006, 1.038],
      vignette: 0.24,
      bloom: { threshold: 0.78, strength: 0.26, radius: 10 },
      /* GRAIN AT 0.014, CARRIED FORWARD FROM THE SEPTEMBER 19TH MEASUREMENT rather than the
       * house 0.044. That run measured its vector PDF at 68.7 MB against 6 to 14 MB for every
       * deck before it, tested three hypotheses, and found cutting per pixel noise and the
       * dither was worth 9 MB while a raised screen floor and a higher gamma were worth
       * nothing. September 20th then measured 61.95 MB on a hatch and concluded the screen is
       * not the lever either. So this is the one knob known to move, and the size is
       * DISCLOSED rather than predicted. A number in this file that was guessed is worse than
       * no number. */
      grain: { amount: 0.014, size: 3, seed: 20260923 },
      aberration: 0,
      dither: false,
      sharpen: 0.32
    }
  });

  var N = {};
  N.W = 1080;
  N.H = 1350;
  N.SEED = 20260923;

  /* ------------------------------------------------------------------- stock
   *
   * The paper and the ink, once, for all nine frames. A screen is the deck's STOCK and
   * changing stock between frames is a different print job rather than variety.
   */
  N.GROUND = "#322C44";   /* night sky over a mast lit pad. Measured, see the header */
  N.INK    = "#CFD2D8";   /* galvanised steel under a discharge lamp, the deck's paper */
  N.ACCENT = "#E0A33F";   /* posted notice amber. THE STATE'S PAPER, and nothing else wears it */
  N.DEK    = "#A7A6B4";
  N.RULE   = "#8A8798";   /* the furniture, one pale ink on all nine frames */

  /* THE TWO MATERIALS, AND THE BOUNDARY BETWEEN THEM IS THE STORY.
   * `STEEL` is a painted genset enclosure and a galvanised stack under mast light. `BOND` is
   * the agency's own paper, which is deliberately NOT white: four cream sheets at full white
   * made September 18th's canvas mean strobe, and the judges converged on capping unscreened
   * stock rather than dimming it afterwards. Every glyph in the drawn world sits on BOND. */
  N.STEEL = "#8E939B";
  N.BOND  = "#C6C0AA";
  N.TONER = "#141318";

  N.CALICHE  = "#5A5140";  /* compacted pad, warm against the sky */
  N.GRAVEL   = "#3E3A38";
  N.STACKTOP = "#9AA0A4";  /* galvanised flue, the one thing the permit is about */
  N.DARKSTEEL= "#4A4E56";

  /* THE GREY SCALE THE FRAMES DRAW IN, nine steps, dark to light. A frame that picks its own
   * colours has left the deck. These are TWIN values: the print maps them onto the stock. */
  N.G = {
    voidd:  "#000000",
    deep:   "#0F0F12",
    dark:   "#26262B",
    shade:  "#3E3E45",
    mid:    "#63636B",
    stone:  "#86868E",
    metal:  "#A8A8AF",
    bright: "#D2D2D6",
    glare:  "#F2F2F4"
  };
  N.STEPS = ["voidd", "deep", "dark", "shade", "mid", "stone", "metal", "bright", "glare"];

  /* THE PRESS. One stock for nine frames.
   *
   * gamma 0.5 makes 2 * gamma exactly 1 for a dot screen, so coverage is LINEAR in the twin's
   * own luminance and nine declared steps land on nine distinct marks rather than four. A LINE
   * screen carries tone in stroke WEIGHT rather than in dot count, so the same reasoning runs
   * through `weight` instead of `perCell`. Both are probe frame decisions and Phase 10.5
   * amends them to what the nine band print actually measured.
   */
  N.SCREEN = { mode: "line", cell: 5, angle: 68, gamma: 0.5, floor: 0.04, weight: 1.00 };
  N.EDGES  = { threshold: 18, width: 1.3, alpha: 0.78, dx: -0.9, dy: 0.8 };

  /* ------------------------------------------------------------------ helpers
   *
   * PRIMITIVES, NOT A DRAWING. There is no drawFrame() in this file and there never will be.
   * A shared draw-the-whole-slide is a template, `deck_chassis.py` refuses one by name, and
   * the per frame composition is this machine's whole strength. What follows is the yard's
   * vocabulary. Each frame decides what to build from it.
   */

  /* The mast's pool on the pad. Takes x and y, in SCREEN px, and a reserve mask.
   * It does NOT take cx, cy or a rect list. Passing the wrong keys makes the gradient NaN and
   * paints the whole pool at the ORIGIN, which put a warm glow over the kicker on three frames
   * of the September 20th reference build and was reported three hundred pixels from its
   * cause. */
  N.pool = function (cx, o) {
    o = o || {};
    var x = o.x == null ? N.W * 0.30 : o.x;
    var y = o.y == null ? N.H * 0.62 : o.y;
    var r = o.r == null ? 760 : o.r;
    var peak = o.peak == null ? 0.90 : o.peak;
    var g = cx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0.00, "rgba(255,255,255," + peak + ")");
    g.addColorStop(0.34, "rgba(255,255,255," + (peak * 0.44) + ")");
    g.addColorStop(0.68, "rgba(255,255,255," + (peak * 0.12) + ")");
    g.addColorStop(1.00, "rgba(255,255,255,0)");
    cx.save();
    cx.globalCompositeOperation = "lighter";
    cx.fillStyle = g;
    cx.fillRect(0, 0, N.W, N.H);
    cx.restore();
    /* LIGHT DIMS TOWARD TYPE. IT IS NOT REMOVED FROM AROUND IT. A hole punched at full
     * strength is a plate with the sign flipped, and it put a visible dark rounded rect behind
     * the site line on the first chassis deck. Soft, partial, wide feather. */
    if (o.reserve) N.dim(cx, o.reserve, o.dim == null ? 0.42 : o.dim);
  };

  /* Dim a light layer toward the type, partially, with a wide feather. */
  N.dim = function (cx, mask, amount) {
    var im = cx.getImageData(0, 0, N.W, N.H), d = im.data;
    for (var y = 0; y < N.H; y += 1) {
      for (var x = 0; x < N.W; x += 1) {
        var m = mask(x, y);
        if (m <= 0) continue;
        var k = 1 - amount * m;
        var i = (y * N.W + x) * 4;
        d[i] *= k; d[i + 1] *= k; d[i + 2] *= k;
      }
    }
    cx.putImageData(im, 0, 0);
  };

  /* A reciprocating gas set on a skid, drawn in METRES as TXSCENE parts.
   * Not in the catalogue, so it is built from parts and goes in the backlog as a proposal.
   * Real machines of this class sit about 2.9 m to 3.2 m to the enclosure roof on a skid, and
   * the flue runs well above that. Nothing here is a slab. */
  N.genset = function (o) {
    o = o || {};
    var L = o.len == null ? 12.2 : o.len;      /* a 40 foot skid */
    var H = o.h == null ? 3.0 : o.h;           /* enclosure roof */
    var S = o.stack == null ? 11.5 : o.stack;  /* flue above grade */
    var inks = o.inks || {};
    return [
      /* skid */
      { kind: "rect", x: -L / 2, y: 0, w: L, h: 0.35, fill: inks.dark || N.G.dark },
      /* enclosure body, the lit LEFT face and the dark RIGHT face are set by the frame */
      { kind: "rect", x: -L / 2 + 0.2, y: 0.35, w: L - 0.4, h: H - 0.35,
        fill: inks.body || N.G.mid },
      /* roof band */
      { kind: "rect", x: -L / 2 + 0.2, y: H - 0.22, w: L - 0.4, h: 0.22,
        fill: inks.roof || N.G.stone },
      /* louvre bank, the radiator end */
      { kind: "rect", x: L / 2 - 2.6, y: 0.7, w: 2.2, h: H - 1.3,
        fill: inks.louvre || N.G.shade },
      /* THE STACK. The one thing an air permit is about. */
      { kind: "rect", x: -L / 2 + 2.1, y: H, w: 0.62, h: S - H,
        fill: inks.stack || N.G.metal },
      { kind: "rect", x: -L / 2 + 1.85, y: S - 0.5, w: 1.12, h: 0.30,
        fill: inks.cap || N.G.bright }
    ];
  };

  /* A run of chain link with a top rail, between two ground points, in metres. */
  N.fence = function (S, a, b, o) {
    o = o || {};
    var h = o.h == null ? 2.4 : o.h;
    var posts = o.posts == null ? 9 : o.posts;
    var ink = o.ink || N.G.shade;
    var i, t, X, Z, p0, p1;
    S.cx.save();
    S.cx.strokeStyle = ink;
    S.cx.lineWidth = o.w == null ? 2 : o.w;
    for (i = 0; i <= posts; i += 1) {
      t = i / posts;
      X = a[0] + (b[0] - a[0]) * t;
      Z = a[1] + (b[1] - a[1]) * t;
      p0 = S.project(X, 0, Z);
      p1 = S.project(X, h, Z);
      S.cx.beginPath(); S.cx.moveTo(p0.x, p0.y); S.cx.lineTo(p1.x, p1.y); S.cx.stroke();
    }
    p0 = S.project(a[0], h, a[1]); p1 = S.project(b[0], h, b[1]);
    S.cx.beginPath(); S.cx.moveTo(p0.x, p0.y); S.cx.lineTo(p1.x, p1.y); S.cx.stroke();
    S.cx.restore();
  };

  /* A sheet of the agency's own bond, drawn on a surface, with its own ruled blocks.
   * The ONLY thing in this deck that may carry glyphs. */
  N.sheet = function (cx, r, o) {
    o = o || {};
    cx.save();
    cx.fillStyle = o.fill || N.G.bright;
    cx.fillRect(r.x, r.y, r.w, r.h);
    if (o.rules) {
      cx.strokeStyle = o.rule || N.G.mid;
      cx.lineWidth = o.rw == null ? 1.4 : o.rw;
      for (var i = 0; i < o.rules.length; i += 1) {
        var y = r.y + r.h * o.rules[i];
        cx.beginPath(); cx.moveTo(r.x + r.w * 0.08, y);
        cx.lineTo(r.x + r.w * 0.92, y); cx.stroke();
      }
    }
    cx.restore();
  };

  N.rng = function (salt) { return TX.rng(N.SEED + (salt || 0)); };

  global.YARD = N;
})(this);
