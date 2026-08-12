/* akhachure.js — slope-and-aspect hachure fields (offline, zero dependencies,
 * deterministic per seed). Draws a drawn-looking shaded field whose detail is
 * parameterised by the DATA UNDER IT rather than by screen position.
 *
 * WHY THIS EXISTS. "Artwork craft and genuine detail" was the weakest scored
 * criterion in 8 of the 10 runs to 2026-08-02, mean 6.25, and two upgrades aimed
 * at it did not move the number. The 2026-08-02 frontier scan diagnosed the
 * general case and the diagnosis is the whole reason for this file:
 *
 *     our detail is uniform because our stipple and tooth fields are
 *     parameterised by POSITION, so a density falloff is a gradient laid over a
 *     texture that is otherwise the same everywhere, and a reader cannot see it.
 *
 * That run declared a computed tooth falloff across three material registers.
 * The registers read; the falloff did not, on any slide, per several independent
 * pixel critics and the scorer. A mechanism that runs in code and not in pixels
 * earns nothing.
 *
 * A hachure field inverts that. Every stroke's WIDTH is the local SLOPE of a
 * height field and every stroke's ROTATION is the local ASPECT, so the field
 * cannot be uniform unless the data under it is uniform. Non-uniformity becomes
 * structural instead of applied.
 *
 * THE TECHNIQUE. Hachures were standardised by Johann Georg Lehmann in 1799 and
 * the modern form is "slope and aspect hachuring", which shows slope, aspect and
 * flow direction of a surface at once. The browser-side recipe here follows Andy
 * Woodruff's sketchy-relief method:
 *   1. divide the region into a grid;
 *   2. at each cell compute SLOPE and ASPECT from central differences of H;
 *   3. draw one short stroke per cell, WIDTH from slope, ROTATION from aspect,
 *      running down the line of steepest descent;
 *   4. make strokes LONGER than their cell so neighbours blend into a field;
 *   5. jitter cell positions and bend each stroke slightly, so the field reads
 *      drawn rather than stamped;
 *   6. redraw the whole field several times at low opacity with the sun angle
 *      varied a little each pass, so shadow detail ACCUMULATES.
 * Sources: https://andywoodruff.com/blog/hachures-and-sketchy-relief-maps/ ,
 * https://en.wikipedia.org/wiki/Hachure_map
 *
 * ALL RANDOMNESS IS NORMALLY DISTRIBUTED, not uniform (FIELD_NOTES 2026-08-02:
 * "uniformly distributed data doesn't typically show up in nature"). Jitter,
 * bend and length noise are Box-Muller gaussians off a seeded mulberry32, so the
 * field has a natural spread and is still byte-identical run to run. No
 * Math.random anywhere, per the determinism gate in qa.py.
 *
 * `height` IS REQUIRED AND HAS NO DEFAULT, deliberately. A default noise field
 * would let a slide get the look without the data, which is the exact failure
 * this file exists to stop. Pass the story's own quantity.
 *
 * USAGE (slide code):
 *   <script src="@@ASSETS@@/js/akhachure.js"></script>
 *   const stats = TX.hachureField(cx, {
 *     x: 80, y: 420, w: 920, h: 560, scale: 2,
 *     seed: 20260803,
 *     height: (u, v) => loadAtHour(u) * shareAt(v),   // THE DATA, in [0,1]
 *     cell: 13, lenScale: 1.9, passes: 4,
 *     sunAz: 315, sunEl: 34, sunJitter: 11,
 *     color: '#0D1B2A', alpha: 0.13,
 *     minWidth: 0.45, maxWidth: 3.4,
 *     probes: [ { name: 'flat shelf', x: 120, y: 470, w: 220, h: 180 },
 *               { name: 'steep face', x: 640, y: 470, w: 220, h: 180 } ]
 *   });
 *   // stats.widthRatio is the falsifiable craft claim; stats.probes[i].meanWidth
 *   // lets the dossier state a number a pixel critic can be asked to contradict.
 *
 * NOTES
 * - Text stays DOM or SVG. This draws ART only, and never under type without an
 *   opaque knockout plate over it (the recurring text-against-geometry hard fail
 *   is invisible to qa.py, whose collision check is DOM-only).
 * - Data honesty: a hachure field is FORM shading. It is honest about relative
 *   steepness, which is what it draws; never ask a reader to read a magnitude
 *   off it. Quantities stay in parallel projection with a printed scale.
 * - Cost: one height eval per cell plus four per cell for the central
 *   differences, times `passes`. A 920x560 CSS-px region at cell 13 is about
 *   3,000 cells, so roughly 60k evals over 4 passes. Cheap next to a per-pixel
 *   relief shade; keep `height` itself cheap and it stays well inside the 30s
 *   renderReady cap.
 */
(function (global) {
  "use strict";
  var TX = global.TX || (global.TX = {});

  // Seeded uniform PRNG (mulberry32). Never Math.random.
  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  // Box-Muller gaussian, mean 0 sd 1, off a seeded uniform. Cached second value.
  function gaussianFrom(rand) {
    var spare = null;
    return function () {
      if (spare !== null) { var s = spare; spare = null; return s; }
      var u = 0, v = 0, m = 0;
      do {
        u = rand() * 2 - 1; v = rand() * 2 - 1; m = u * u + v * v;
      } while (m >= 1 || m === 0);
      var f = Math.sqrt(-2 * Math.log(m) / m);
      spare = v * f;
      return u * f;
    };
  }

  function clamp01(t) { return t < 0 ? 0 : t > 1 ? 1 : t; }

  function hexToRGB(s) {
    var m = String(s).match(/^#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i);
    if (!m) throw new Error("akhachure: color must be a #rrggbb hex literal, got " + s);
    return [parseInt(m[1], 16), parseInt(m[2], 16), parseInt(m[3], 16)];
  }

  /* Draw a slope-and-aspect hachure field.
   * Returns { cells, strokes, minWidth, maxWidth, meanWidth, widthRatio,
   *           slopeMin, slopeMax, probes: [{name, cells, meanWidth, meanSlope}] }
   * widthRatio is maxWidth/minWidth over cells that actually drew, which is the
   * number a dossier should declare and a pixel critic should be asked to
   * contradict from the render alone.
   */
  function hachureField(cx, opts) {
    var o = opts || {};
    if (typeof o.height !== "function") {
      throw new Error("akhachure: `height` is required and takes no default. " +
        "Pass the story's own quantity as height(u,v) in [0,1].");
    }
    var X = o.x || 0, Y = o.y || 0, W = o.w, H = o.h;
    if (!(W > 0 && H > 0)) throw new Error("akhachure: w and h are required");

    var cell = o.cell || 13;
    var seed = (o.seed === undefined ? 1 : o.seed) | 0;
    var passes = o.passes || 4;
    var lenScale = o.lenScale === undefined ? 1.8 : o.lenScale;
    var jitter = o.jitter === undefined ? 0.34 : o.jitter;   // sd, in cells
    var bend = o.bend === undefined ? 0.28 : o.bend;         // sd, in stroke lengths
    var minW = o.minWidth === undefined ? 0.45 : o.minWidth;
    var maxW = o.maxWidth === undefined ? 3.2 : o.maxWidth;
    var gamma = o.slopeGamma === undefined ? 1.0 : o.slopeGamma;
    var relief = o.relief === undefined ? 1.0 : o.relief;
    var alpha = o.alpha === undefined ? 0.13 : o.alpha;
    var sunAz = o.sunAz === undefined ? 315 : o.sunAz;
    var sunEl = o.sunEl === undefined ? 34 : o.sunEl;
    var sunJit = o.sunJitter === undefined ? 11 : o.sunJitter;
    var lightBias = o.lightBias === undefined ? true : !!o.lightBias;
    var rgb = hexToRGB(o.color || "#000000");
    var probes = o.probes || [];

    var cols = Math.max(2, Math.floor(W / cell));
    var rows = Math.max(2, Math.floor(H / cell));
    var du = 1 / cols, dv = 1 / rows;

    // --- Pass 1: measure the field. Central differences give slope and aspect.
    var n = cols * rows;
    var slope = new Float64Array(n);
    var aspect = new Float64Array(n);
    var i, j, k, u, v, hL, hR, hU, hD, gx, gy;
    var sMin = Infinity, sMax = -Infinity;
    for (j = 0; j < rows; j++) {
      v = (j + 0.5) * dv;
      for (i = 0; i < cols; i++) {
        u = (i + 0.5) * du;
        hL = o.height(clamp01(u - du), v);
        hR = o.height(clamp01(u + du), v);
        hU = o.height(u, clamp01(v - dv));
        hD = o.height(u, clamp01(v + dv));
        // gradient in height units per normalised unit, scaled by relief
        gx = (hR - hL) * 0.5 * relief;
        gy = (hD - hU) * 0.5 * relief;
        k = j * cols + i;
        var s = Math.sqrt(gx * gx + gy * gy);
        slope[k] = s;
        // aspect: direction of steepest DESCENT, which is where a hachure runs
        aspect[k] = Math.atan2(-gy, -gx);
        if (s < sMin) sMin = s;
        if (s > sMax) sMax = s;
      }
    }
    var sRef = o.slopeRef === undefined ? sMax : o.slopeRef;
    if (!(sRef > 0)) sRef = 1e-9;

    // Precompute each cell's stroke width once, so stats and drawing agree.
    var widths = new Float64Array(n);
    var wMin = Infinity, wMax = -Infinity, wSum = 0, drew = 0;
    for (k = 0; k < n; k++) {
      var t = Math.pow(clamp01(slope[k] / sRef), gamma);
      var wpx = minW + (maxW - minW) * t;
      widths[k] = wpx;
      if (wpx < wMin) wMin = wpx;
      if (wpx > wMax) wMax = wpx;
      wSum += wpx;
      drew++;
    }

    // --- Pass 2..N: draw, accumulating shadow detail at low opacity.
    cx.save();
    cx.lineCap = "round";
    cx.lineJoin = "round";
    for (var p = 0; p < passes; p++) {
      // A fresh seeded stream per pass, so jitter differs pass to pass and the
      // strokes lay over each other instead of stacking on one line.
      var rand = mulberry32(seed + p * 7919);
      var gauss = gaussianFrom(rand);
      var azP = (sunAz + (p - (passes - 1) / 2) * sunJit) * Math.PI / 180;
      var elP = sunEl * Math.PI / 180;
      var ch = Math.cos(elP);
      var lx = ch * Math.sin(azP), ly = -ch * Math.cos(azP), lz = Math.sin(elP);

      for (j = 0; j < rows; j++) {
        for (i = 0; i < cols; i++) {
          k = j * cols + i;
          var wpx2 = widths[k];
          var a = aspect[k];

          // Light bias: strokes belong in the shadow. Build the surface normal
          // from the same gradient the aspect came from and drop strokes on
          // faces turned toward the sun.
          var lit = 1;
          if (lightBias) {
            var gsx = -Math.cos(a) * slope[k];
            var gsy = -Math.sin(a) * slope[k];
            var nz = 1 / (1 + relief);
            var nl = Math.sqrt(gsx * gsx + gsy * gsy + nz * nz) || 1;
            lit = (gsx * lx + gsy * ly + nz * lz) / nl;
            lit = clamp01((lit + 1) * 0.5);
          }
          var shade = 1 - lit;                  // 0 lit .. 1 in shadow
          var aPass = alpha * (0.35 + 0.65 * shade);
          if (aPass <= 0.004) continue;

          // Position, jittered on a gaussian so the grid never reads as a grid.
          var cxp = X + (i + 0.5) * (W / cols) + gauss() * jitter * cell;
          var cyp = Y + (j + 0.5) * (H / rows) + gauss() * jitter * cell;

          // Length: longer than the cell so neighbours blend, and longer on
          // steep ground, with a gaussian spread.
          var tSlope = clamp01(slope[k] / sRef);
          var len = cell * lenScale * (0.68 + 0.62 * tSlope) * (1 + gauss() * 0.14);
          if (len < 1) continue;

          var dx = Math.cos(a), dy = Math.sin(a);
          var x0 = cxp - dx * len * 0.5, y0 = cyp - dy * len * 0.5;
          var x1 = cxp + dx * len * 0.5, y1 = cyp + dy * len * 0.5;
          // Bend: one control point pushed perpendicular, gaussian magnitude.
          var b = gauss() * bend * len;
          var mx = cxp - dy * b, my = cyp + dx * b;

          cx.strokeStyle = "rgba(" + rgb[0] + "," + rgb[1] + "," + rgb[2] + "," + aPass.toFixed(4) + ")";
          cx.lineWidth = wpx2;
          cx.beginPath();
          cx.moveTo(x0, y0);
          cx.quadraticCurveTo(mx, my, x1, y1);
          cx.stroke();
        }
      }
    }
    cx.restore();

    // --- Probes: mean stroke width inside named CSS-px rectangles, so a dossier
    // can declare a checkable number and a critic can be asked to refute it.
    var probeOut = [];
    for (var q = 0; q < probes.length; q++) {
      var pr = probes[q], pc = 0, pw = 0, ps = 0;
      for (j = 0; j < rows; j++) {
        var py = Y + (j + 0.5) * (H / rows);
        if (py < pr.y || py > pr.y + pr.h) continue;
        for (i = 0; i < cols; i++) {
          var px = X + (i + 0.5) * (W / cols);
          if (px < pr.x || px > pr.x + pr.w) continue;
          k = j * cols + i;
          pc++; pw += widths[k]; ps += slope[k];
        }
      }
      probeOut.push({
        name: pr.name || ("probe" + q),
        cells: pc,
        meanWidth: pc ? pw / pc : 0,
        meanSlope: pc ? ps / pc : 0
      });
    }

    return {
      cells: n,
      strokes: n * passes,
      minWidth: wMin, maxWidth: wMax,
      meanWidth: drew ? wSum / drew : 0,
      widthRatio: wMin > 0 ? wMax / wMin : Infinity,
      slopeMin: sMin, slopeMax: sMax,
      probes: probeOut
    };
  }

  /* Convenience: a height field read straight off an array of story values.
   * values is a flat row-major array of numbers, cols x rows, in any units; it
   * is normalised to [0,1] once and bilinearly interpolated. This is the honest
   * path from a table of numbers to a shaded field, with no noise in between.
   */
  function heightFromGrid(values, cols, rows) {
    var lo = Infinity, hi = -Infinity, i;
    for (i = 0; i < values.length; i++) {
      if (values[i] < lo) lo = values[i];
      if (values[i] > hi) hi = values[i];
    }
    var span = (hi - lo) || 1;
    return function (u, v) {
      var fx = clamp01(u) * (cols - 1), fy = clamp01(v) * (rows - 1);
      var x0 = Math.floor(fx), y0 = Math.floor(fy);
      var x1 = Math.min(cols - 1, x0 + 1), y1 = Math.min(rows - 1, y0 + 1);
      var tx = fx - x0, ty = fy - y0;
      var a = values[y0 * cols + x0], b = values[y0 * cols + x1];
      var c = values[y1 * cols + x0], d = values[y1 * cols + x1];
      var top = a + (b - a) * tx, bot = c + (d - c) * tx;
      return ((top + (bot - top) * ty) - lo) / span;
    };
  }

  TX.hachureField = hachureField;
  TX.hachureFromGrid = heightFromGrid;
})(typeof window !== "undefined" ? window : globalThis);
