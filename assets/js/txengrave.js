/* txengrave.js — WHITE-LINE INTAGLIO, the engraving bench.
 * Committed 2026-07-31 for Carousel No. 21.
 *
 * WHAT THIS IS. One surface that carries modelled tone with genuine detail
 * everywhere, instead of a uniform hatch. It is the line-engraver's vocabulary
 * implemented as code, and it exists because "distribute the detail" turned out
 * to be a plan and not a technique (FIELD_NOTES 2026-07-30, No. 20's retro,
 * artwork craft 6.0 for the fourth time in five runs).
 *
 * WHITE LINE, NOT BLACK LINE. A black-line engraving on paper is a LIGHT deck,
 * and the one-light-deck-per-eight-runs allowance was spent on 2026-07-25.
 * White-line, where the cut prints LIGHT against a solid inked field, is the
 * dark register's native form of the same craft. That is why every stroke here
 * is drawn in a light ink over a dark ground.
 *
 * THE FOUR RULES IT IMPLEMENTS (FIELD_NOTES 2026-07-31, from RISD's "The
 * Brilliant Line", the Met's printmaking notes and the Library Company's
 * banknote-engraving material):
 *
 *   1. THE LAY WRAPS THE FORM. Hatching direction follows the surface it
 *      describes, so the DIRECTION FIELD is the modelling, before any value is
 *      applied. A hatch whose direction is constant across a frame is
 *      decoration. This is exactly what No. 20's uniform contour drift got
 *      wrong.
 *   2. THE SWELLED LINE. A stroke tapers at both ends and widens in the middle,
 *      and crossed swelled lines form lozenges that carry tone by themselves.
 *      Line-weight variance IS the technique, not a garnish on it.
 *   3. THREE PARTS, SEPARATELY CONTROLLABLE. mainline, crossline, interdot.
 *      Tone is the RELATIONSHIP between a dominant lay, a crossing lay, and the
 *      dots that sit in the diamonds.
 *   4. WHAT SETS A LINE'S THICKNESS IS THE LIGHT. Thickness is a lighting
 *      decision made per stroke, not a global stroke weight.
 *
 * WHY RULE 3 MATTERS MORE THAN IT LOOKS. Three independently gated channels are
 * a PER-REGION DETAIL BUDGET EXPRESSED AS A DRAWING SYSTEM. "Everywhere" is not
 * an argument this function accepts. A budget with no line that reads "not here"
 * is not a budget, and that is the whole diagnosis from No. 20.
 *
 * USAGE
 *   <script src="@@ASSETS@@/js/noise.js"></script>
 *   <script src="@@ASSETS@@/js/akcolor.js"></script>
 *   <script src="@@ASSETS@@/js/aksnow.js"></script>
 *   <script src="@@ASSETS@@/js/akengrave.js"></script>   // load AFTER those
 *
 *   const eng = TXENGRAVE.create({seed: 20260731, light: {azDeg:118, elDeg:34}});
 *   await document.fonts.ready;                 // MANDATORY before reserve()
 *   eng.reserve(TXENGRAVE.boxesFor("[data-reserve]"));
 *   eng.surface(cx, {
 *     region: [80, 300, 920, 600],
 *     form:  (x, y) => <height in px>,
 *     tone:  (x, y) => <0..1 darkness target>,
 *     budget:{main: 5.0, cross: 7.0, dots: true},
 *     inkLo: "#6E8378", inkHi: "#BFD0C4", alpha: 1.0
 *   });
 *
 * PERFORMANCE, THE LESSON THAT WILL BITE OTHERWISE. `cx.filter` applies PER DRAW
 * OP. A surface of ~1,300 strokes drawn under a set filter blurs 1,300 times and
 * blew the 45s navigation budget on 2026-07-30. Nothing in this file ever sets
 * cx.filter inside a stroke loop. Blur once, at composite, on an offscreen
 * canvas, which is what drawOffscreen() is for.
 *
 * COLOUR SAFETY. Every colour here is resolved through an integer-indexed ramp
 * or TXC.mixOklab. NO COLOUR HELPER IS EVER NESTED INSIDE ANOTHER, because
 * lerpHex and its cousins return an "rgb()" string, feeding rgb(...) into a hex
 * parser yields NaN on every channel, and canvas then silently keeps the
 * PREVIOUS fillStyle with a clean machine gate (instinct 0.97, run 2026-07-30).
 */
(function (global) {
  "use strict";

  var TAU = Math.PI * 2;

  /* The five-token weight system, at 1080px width. Assign by MEANING.
   * Uniform line weight is the number one amateur tell. */
  var TOKENS = [0.75, 1.25, 2.0, 3.5, 5.5];

  function need(v, name) {
    if (v == null) throw new TypeError("TXENGRAVE: missing required option " + name);
    return v;
  }
  function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }
  function lerp(a, b, t) { return a + (b - a) * t; }

  /* Snap to the nearest weight token. Keeps variance reading as a SYSTEM
   * rather than as noise, which is the difference between an engraving and a
   * scribble. Lay lines are allowed to float between hair and bold, so this is
   * applied only where the caller asks for it. */
  function snapToken(w) {
    var best = TOKENS[0], bd = Math.abs(w - TOKENS[0]);
    for (var i = 1; i < TOKENS.length; i++) {
      var d = Math.abs(w - TOKENS[i]);
      if (d < bd) { bd = d; best = TOKENS[i]; }
    }
    return best;
  }

  /* Deterministic integer-cell hash. Interdot placement MUST NOT use a
   * per-slide RNG, or a panorama or a re-render will not reproduce. */
  function hash2(gx, gy, seed) {
    var s = Math.sin(gx * 127.1 + gy * 311.7 + seed * 0.0001) * 43758.5453;
    return s - Math.floor(s);
  }

  function Engraver(opts) {
    opts = opts || {};
    this.seed = opts.seed == null ? 20260731 : opts.seed;
    var L = opts.light || {};
    var az = (L.azDeg == null ? 118 : L.azDeg) * Math.PI / 180;
    var el = (L.elDeg == null ? 34 : L.elDeg) * Math.PI / 180;
    /* World light vector. Rule 4 hangs off this and nothing else. */
    this.L = [Math.cos(az) * Math.cos(el), Math.sin(az) * Math.cos(el), Math.sin(el)];
    this.reserved = [];
    this.stats = {main: 0, cross: 0, dots: 0, widths: []};
  }

  /* ------------------------------------------------------------------ reserve
   * THE STRUCTURAL KILL FOR "TEXT AGAINST GEOMETRY".
   *
   * qa.py's text_collisions walk is DOM-only, so any label positioned against
   * canvas or SVG geometry can collide freely and the gate still returns PASS
   * with zero warns (instinct 0.98). That defect has been a HARD FAIL twice in
   * ten runs, on 2026-07-25 and 2026-07-29.
   *
   * The usual answer is a knockout plate. This is better: the art is generated
   * AFTER text layout, from MEASURED boxes, and the generator multiplies lay
   * density by zero inside them. The stroke is never generated. There is
   * nothing to collide with, and there is no plate to size wrong.
   *
   * Strokes TAPER out across the feather rather than being clipped, so the
   * boundary reads as a burin field on a real plate and not as a rectangular
   * hole punched in a texture.
   *
   * You MUST await document.fonts.ready before calling this. A box measured
   * against a fallback face is the wrong box, and that is how run 2026-07-29
   * shipped six labels off their own plates.
   */
  Engraver.prototype.reserve = function (boxes) {
    if (!boxes) return this;
    for (var i = 0; i < boxes.length; i++) {
      var b = boxes[i];
      if (!b || b.length !== 4) continue;
      if (!(b[2] > 0 && b[3] > 0)) continue;   /* a zero box means an unlaid node */
      this.reserved.push(b);
    }
    return this;
  };

  /* Reservation weight at a point: 0 inside a reserved box, ramping to 1 across
   * `feather` px outside it. Multiplicative across overlapping boxes. */
  Engraver.prototype.mask = function (x, y, feather) {
    var f = feather == null ? 18 : feather;
    var m = 1;
    for (var i = 0; i < this.reserved.length; i++) {
      var b = this.reserved[i];
      /* signed distance to the box, negative inside */
      var dx = Math.max(b[0] - x, 0, x - (b[0] + b[2]));
      var dy = Math.max(b[1] - y, 0, y - (b[1] + b[3]));
      var d = Math.sqrt(dx * dx + dy * dy);
      if (d >= f) continue;
      var t = d / f;
      m *= t * t * (3 - 2 * t);           /* smoothstep, so no hard rim */
      if (m <= 0.001) return 0;
    }
    return m;
  };

  /* --------------------------------------------------------------- normalAt
   * Analytic-ish surface normal from the caller's height field, by central
   * differences on a 6px stencil. This is what rules 1 and 4 both read. */
  Engraver.prototype.normalAt = function (form, x, y) {
    var h = 6;
    var dzdx = (form(x + h, y) - form(x - h, y)) / (2 * h);
    var dzdy = (form(x, y + h) - form(x, y - h)) / (2 * h);
    var n = [-dzdx, -dzdy, 1];
    var len = Math.sqrt(n[0] * n[0] + n[1] * n[1] + 1) || 1;
    return [n[0] / len, n[1] / len, n[2] / len];
  };

  /* ---------------------------------------------------------------- surface
   * Draw one engraved region. Everything above becomes pixels here. */
  Engraver.prototype.surface = function (cx, o) {
    o = o || {};
    var region = need(o.region, "region");
    var form = o.form || function () { return 0; };
    var tone = o.tone || function () { return 0.5; };
    var budget = o.budget || {};
    var gapMain = budget.main == null ? 6.0 : budget.main;
    var gapCross = budget.cross == null ? 0 : budget.cross;
    var wantDots = !!budget.dots;
    var alpha = o.alpha == null ? 1.0 : o.alpha;
    var feather = o.feather == null ? 18 : o.feather;
    var inkLo = o.inkLo || "#6E8378";
    var inkHi = o.inkHi || "#BFD0C4";
    var wMax = o.wMax == null ? 3.5 : o.wMax;
    var crossDeg = o.crossDeg == null ? 78 : o.crossDeg;   /* off-90 on purpose */
    var step = o.step == null ? 6 : o.step;                /* polygon sample, px */
    var self = this;

    var x0 = region[0], y0 = region[1], rw = region[2], rh = region[3];
    var diag = Math.sqrt(rw * rw + rh * rh);

    /* An 8-step ink ladder, indexed by INTEGER. Never nested, never re-parsed. */
    var ink = [];
    for (var s = 0; s < 8; s++) ink.push(TXC.mixOklab(inkLo, inkHi, s / 7));

    cx.save();
    cx.beginPath();
    cx.rect(x0, y0, rw, rh);
    cx.clip();
    cx.globalAlpha = alpha;

    /* ---- channel 1, the MAINLINE. Always present. ---------------------- */
    this._layPass(cx, {
      x0: x0, y0: y0, rw: rw, rh: rh, diag: diag, gap: gapMain, angOff: 0,
      form: form, tone: tone, wMax: wMax, step: step, feather: feather,
      ink: ink, toneGate: 1.1, channel: "main"
    });

    /* ---- channel 2, the CROSSLINE. Only in the darks. ------------------ */
    if (gapCross > 0) {
      this._layPass(cx, {
        x0: x0, y0: y0, rw: rw, rh: rh, diag: diag, gap: gapCross,
        angOff: crossDeg * Math.PI / 180,
        form: form, tone: tone, wMax: wMax * 0.6, step: step, feather: feather,
        ink: ink, toneGate: 0.45, channel: "cross"
      });
    }

    /* ---- channel 3, the INTERDOT. Only in the deepest darks. ----------- */
    if (wantDots) {
      var cell = Math.max(gapMain, 5) * 1.6;
      cx.fillStyle = ink[6];
      for (var gy = Math.floor(y0 / cell); gy <= Math.floor((y0 + rh) / cell); gy++) {
        for (var gx = Math.floor(x0 / cell); gx <= Math.floor((x0 + rw) / cell); gx++) {
          var jx = hash2(gx, gy, self.seed), jy = hash2(gx + 71, gy + 13, self.seed);
          var px = (gx + jx) * cell, py = (gy + jy) * cell;
          if (px < x0 || px > x0 + rw || py < y0 || py > y0 + rh) continue;
          if (tone(px, py) > 0.22) continue;
          if (self.mask(px, py, feather) < 0.9) continue;
          var r = 0.6 + 0.5 * hash2(gx + 7, gy + 29, self.seed);
          cx.beginPath();
          cx.arc(px, py, r, 0, TAU);
          cx.fill();
          self.stats.dots++;
        }
      }
    }

    cx.restore();
    return this.stats;
  };

  /* One hatching pass. Lines are seeded on a rotated raster and then WALK the
   * direction field, so the lay bends with the form (rule 1) instead of running
   * straight across it. */
  Engraver.prototype._layPass = function (cx, p) {
    var self = this;
    var cxm = p.x0 + p.rw / 2, cym = p.y0 + p.rh / 2;
    var nLines = Math.ceil(p.diag / p.gap);
    var half = p.diag / 2;
    /* base raster angle, rotated by the pass's own offset */
    var baseAng = p.angOff + Math.PI / 2;
    var ca = Math.cos(baseAng), sa = Math.sin(baseAng);

    for (var i = 0; i <= nLines; i++) {
      var off = -half + i * p.gap;
      /* seed point on the raster line, then walk both ways along the field */
      var sx = cxm + ca * off, sy = cym + sa * off;
      var pts = this._walk(p, sx, sy, +1);
      var back = this._walk(p, sx, sy, -1);
      back.reverse();
      var poly = back.concat(pts.slice(1));
      if (poly.length < 3) continue;
      this._ribbon(cx, poly, p);
      this.stats[p.channel]++;
    }
  };

  /* Walk the direction field from a seed, producing a centreline. */
  Engraver.prototype._walk = function (p, sx, sy, dir) {
    var pts = [], x = sx, y = sy;
    var maxSteps = Math.ceil(p.diag / p.step) + 2;
    for (var k = 0; k < maxSteps; k++) {
      if (x < p.x0 - 40 || x > p.x0 + p.rw + 40 || y < p.y0 - 40 || y > p.y0 + p.rh + 40) break;
      pts.push([x, y]);
      var n = this.normalAt(p.form, x, y);
      /* RULE 1. The lay runs along the isolines of the height field, which is
       * rot90 of the gradient. Where the surface is flat the gradient is zero
       * and we fall back to the pass's base angle, so a flat region still gets
       * a coherent lay instead of noise. */
      var gx = -n[0], gy = -n[1];
      var gl = Math.sqrt(gx * gx + gy * gy);
      var ang;
      if (gl < 1e-4) ang = p.angOff;
      else ang = Math.atan2(gx, -gy) + p.angOff;
      x += Math.cos(ang) * p.step * dir;
      y += Math.sin(ang) * p.step * dir;
    }
    return pts;
  };

  /* RULES 2 and 4. Every stroke is a FILLED TAPERED POLYGON, never a stroked
   * path, so the taper is real geometry. Width across strokes is set by the
   * light; width along the stroke is the swell. */
  Engraver.prototype._ribbon = function (cx, poly, p) {
    var n = poly.length;
    if (n < 3) return;
    var up = [], dn = [];
    var anyInk = false;

    for (var i = 0; i < n; i++) {
      var pt = poly[i];
      var t = i / (n - 1);
      var nn = this.normalAt(p.form, pt[0], pt[1]);
      var ndotl = clamp(nn[0] * this.L[0] + nn[1] * this.L[1] + nn[2] * this.L[2], 0, 1);

      /* RULE 4. Lines FATTEN in shadow and THIN toward the light, which is how
       * a burin actually behaves and is why the result reads as modelled rather
       * than as texture. */
      var wStroke = 0.75 + (p.wMax - 0.75) * Math.pow(1 - ndotl, 1.6);
      /* RULE 2. The swell. */
      var w = wStroke * Math.pow(Math.sin(Math.PI * t), 0.7);

      /* tone gate: the crossline channel exists only in the darks */
      var tv = p.tone(pt[0], pt[1]);
      if (tv > p.toneGate) w = 0;
      /* the reservation */
      w *= this.mask(pt[0], pt[1], p.feather);

      if (w > 0.12) { anyInk = true; this.stats.widths.push(w); }

      /* segment normal */
      var a = poly[Math.max(i - 1, 0)], b = poly[Math.min(i + 1, n - 1)];
      var dx = b[0] - a[0], dy = b[1] - a[1];
      var dl = Math.sqrt(dx * dx + dy * dy) || 1;
      var nx = -dy / dl, ny = dx / dl;
      up.push([pt[0] + nx * w / 2, pt[1] + ny * w / 2]);
      dn.push([pt[0] - nx * w / 2, pt[1] - ny * w / 2]);
    }
    if (!anyInk) return;

    /* light-indexed ink, integer step, never a nested helper */
    var mid = poly[(n / 2) | 0];
    var mn = this.normalAt(p.form, mid[0], mid[1]);
    var ml = clamp(mn[0] * this.L[0] + mn[1] * this.L[1] + mn[2] * this.L[2], 0, 1);
    var idx = clamp(Math.round(ml * 7), 0, 7);
    cx.fillStyle = p.ink[idx];

    cx.beginPath();
    cx.moveTo(up[0][0], up[0][1]);
    for (var j = 1; j < up.length; j++) cx.lineTo(up[j][0], up[j][1]);
    for (var k = dn.length - 1; k >= 0; k--) cx.lineTo(dn[k][0], dn[k][1]);
    cx.closePath();
    cx.fill();
  };

  /* -------------------------------------------------------------- guilloche
   * An epitrochoid family, the curve every engine-turned security document is
   * built from. Drawn as ARCS, each with its own light-derived width, so the
   * figure carries weight variance without building a single 50,000-point
   * ribbon. Parameters are meant to be STORY NUMBERS.
   */
  Engraver.prototype.guilloche = function (cx, o) {
    o = o || {};
    var R = need(o.R, "R"), r = need(o.r, "r"), d = need(o.d, "d");
    var cxp = need(o.cx, "cx"), cyp = need(o.cy, "cy");
    var turns = o.turns == null ? 37 : o.turns;
    var scale = o.scale == null ? 1 : o.scale;
    var arcs = o.arcs == null ? 8 : o.arcs;
    var samples = o.samples == null ? 2600 : o.samples;
    var inkLo = o.inkLo || "#6E8378", inkHi = o.inkHi || "#BFD0C4";
    var wBase = o.wBase == null ? 0.6 : o.wBase;
    var wPeak = o.wPeak == null ? 1.4 : o.wPeak;
    var feather = o.feather == null ? 18 : o.feather;
    var self = this;

    var ink = [];
    for (var s = 0; s < 8; s++) ink.push(TXC.mixOklab(inkLo, inkHi, s / 7));

    var total = turns * TAU;
    var per = Math.ceil(samples / arcs);
    var drawn = 0;

    for (var a = 0; a < arcs; a++) {
      var t0 = (a / arcs) * total, t1 = ((a + 1) / arcs) * total;
      /* one width per arc, from the light, so the figure has real variance */
      var phase = (a / arcs) * TAU;
      var lit = 0.5 + 0.5 * Math.cos(phase - Math.atan2(this.L[1], this.L[0]));
      var w = lerp(wBase, wPeak, lit);
      cx.strokeStyle = ink[clamp(Math.round(lit * 7), 0, 7)];
      cx.lineWidth = w;
      cx.lineJoin = "round";
      cx.lineCap = "round";
      cx.beginPath();
      var started = false;
      for (var i = 0; i <= per; i++) {
        var t = t0 + (t1 - t0) * (i / per);
        var k = (R + r) / r;
        var x = cxp + scale * ((R + r) * Math.cos(t) + d * Math.cos(k * t));
        var y = cyp + scale * ((R + r) * Math.sin(t) - d * Math.sin(k * t));
        if (self.mask(x, y, feather) < 0.85) { started = false; continue; }
        if (!started) { cx.moveTo(x, y); started = true; }
        else cx.lineTo(x, y);
        drawn++;
      }
      cx.stroke();
    }
    return {arcs: arcs, points: drawn};
  };

  /* --------------------------------------------------------- drawOffscreen
   * Render a whole engraving pass into its own canvas and composite ONCE.
   * cx.filter applies per draw op, so this is the only safe place to blur.
   */
  function drawOffscreen(w, h, fn, opts) {
    opts = opts || {};
    var c = document.createElement("canvas");
    c.width = w; c.height = h;
    var g = c.getContext("2d");
    fn(g);
    return c;
  }

  /* --------------------------------------------------------------- boxesFor
   * Measure laid-out DOM and SVG nodes into reservation boxes.
   * CALL ONLY AFTER `await document.fonts.ready`. A box measured against a
   * fallback face is the wrong box.
   */
  function boxesFor(selector, opts) {
    opts = opts || {};
    var padBody = opts.padBody == null ? 14 : opts.padBody;
    var padMono = opts.padMono == null ? 8 : opts.padMono;
    var nodes = document.querySelectorAll(selector);
    var out = [];
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      var r = el.getBoundingClientRect();
      if (!(r.width > 0 && r.height > 0)) continue;      /* unlaid node */
      var mono = (el.getAttribute("data-reserve") === "mono");
      var pad = mono ? padMono : padBody;
      /* half any halo/stroke the caller declared */
      var hs = parseFloat(el.getAttribute("data-halo") || "0") / 2;
      out.push([r.left - pad - hs, r.top - pad - hs,
                r.width + 2 * (pad + hs), r.height + 2 * (pad + hs)]);
    }
    return out;
  }

  var API = {
    create: function (o) { return new Engraver(o); },
    boxesFor: boxesFor,
    drawOffscreen: drawOffscreen,
    TOKENS: TOKENS,
    snapToken: snapToken,
    hash2: hash2
  };

  global.TXENGRAVE = API;
})(typeof window !== "undefined" ? window : globalThis);
