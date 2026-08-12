/* txcarve.js — wind-worked surfaces and two-part contact shadows.
 * Offline, deterministic per seed, ZERO dependencies beyond the committed
 * noise.js. Canvas 2D only.
 *
 * WHAT IT DRAWS IN TEXAS. The form this models is an erosional ridge cut by
 * wind into a loose surface: the Monahans dunes, a ploughed Panhandle section
 * seen low and raking, the crack polygons of a dry playa, a caliche cut, the
 * ripple field on a sand flat after a norther. The geometry is one family. The
 * parameters are the wind direction, the key light, and how deep the material
 * is.
 *
 * THE FAILURE THIS EXISTS TO PREVENT. Draw a carved surface as evenly weighted
 * contour lines and it does not read as a surface at all. It reads as a
 * topographic map laid over a gradient. Three things separate the two, and an
 * even hatch has none of them:
 *
 *   1. A RIDGE HAS TWO EDGES, NOT ONE. An erosional ridge has a steep windward
 *      face and a soft lee slope. Drawn as one stroke it is a line. Drawn as a
 *      bright windward edge with a dark lee shadow immediately beneath it, the
 *      same geometry becomes a form with a light side and a dark side. This is
 *      the highest-value difference available here and it costs one extra
 *      stroke.
 *   2. WEIGHT VARIES ALONG A RIDGE AND WITH DEPTH. A constant lineWidth reads
 *      as a drawn line at any density. Each ridge tapers along its own length,
 *      hairline at the ends and full weight through the middle third, and
 *      scales with distance, so the near field carries visibly heavier marks
 *      than the far field. Line-weight VARIANCE is what the eye reads as
 *      texture.
 *   3. CRESTS CATCH THE LIGHT. A wind-polished crest throws small specular
 *      glints where its tangent turns across the key. A few dozen tiny points
 *      at the top of the value range do more for "this is a surface" than
 *      hundreds more contour lines.
 *
 * ORDER-INDEPENDENT VALUE LADDER. The bands here are drawn as STRIPS between
 * adjacent contours, never as fills running from each contour to the frame
 * bottom. That is deliberate and it is not a style choice. The fill-to-bottom
 * form is order-dependent: run the loop dark to light and the last, lightest
 * band paints over every band behind it, the whole mass flattens to a single
 * value, and it does so WITHOUT throwing an error and while passing a machine
 * gate clean. Strips cannot express that bug.
 *
 * USAGE
 *   <script src="@@ASSETS@@/js/noise.js"></script>
 *   <script src="@@ASSETS@@/js/txcarve.js"></script>
 *
 *   const stats = TXCARVE.surface(cx, {
 *     top: gx => 1000 + 30 * TX.fbm2(gx * 0.0022, 7.1, {octaves: 5}),
 *     bottom: 1350, x0: 0, x1: 1080,
 *     lit: "#E4D8C3", shadow: "#2A1D14",
 *     seed: 20260811, lightDeg: 118, windDeg: 200,
 *   });
 *   TXCARVE.contactShadow(cx, {x: 540, y: 1010, w: 90, color: "#1B1830"});
 */
(function (global) {
  "use strict";
  var S = {};

  function need(v, name) {
    if (v === undefined || v === null) {
      throw new TypeError("TXCARVE: '" + name + "' is required");
    }
    return v;
  }
  function hexToRgb(h) {
    if (typeof h !== "string" || h.charAt(0) !== "#" || h.length !== 7) {
      throw new TypeError("TXCARVE: expected a #rrggbb colour, got " + String(h));
    }
    return [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16),
            parseInt(h.slice(5, 7), 16)];
  }
  function mix(a, b, t) {
    var pa = hexToRgb(a), pb = hexToRgb(b);
    t = Math.max(0, Math.min(1, t));
    return "rgb(" + Math.round(pa[0] + (pb[0] - pa[0]) * t) + "," +
                    Math.round(pa[1] + (pb[1] - pa[1]) * t) + "," +
                    Math.round(pa[2] + (pb[2] - pa[2]) * t) + ")";
  }
  function rgba(h, a) {
    var p = hexToRgb(h);
    return "rgba(" + p[0] + "," + p[1] + "," + p[2] + "," + a + ")";
  }
  function rng(seed) {
    if (global.TX && typeof global.TX.rng === "function") return global.TX.rng(seed);
    var s = seed >>> 0;
    return function () {
      s = (s + 0x6D2B79F5) >>> 0;
      var t = Math.imul(s ^ (s >>> 15), 1 | s);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function wiggle(x, k, seed) {
    if (global.TX && typeof global.TX.simplex2 === "function") {
      return global.TX.simplex2(x * k, seed);
    }
    return Math.sin(x * k * 6.283 + seed) * 0.5;
  }

  /* ---------------------------------------------------------------- surface
   * Draws a modelled mass of loose material below a crest contour.
   */
  S.surface = function (cx, o) {
    o = o || {};
    var top = need(o.top, "top");
    if (typeof top !== "function") throw new TypeError("TXCARVE: 'top' must be a function of x");
    var x0 = o.x0 == null ? 0 : o.x0;
    var x1 = o.x1 == null ? (cx.canvas ? cx.canvas.width : 1080) : o.x1;
    var bottom = o.bottom == null ? (cx.canvas ? cx.canvas.height : 1350) : o.bottom;
    var lit = o.lit || "#C9DCF0";
    var shadow = o.shadow || "#16283F";
    var seed = o.seed == null ? 1 : o.seed;
    var bands = o.bands == null ? 56 : o.bands;
    var gamma = o.gamma == null ? 0.34 : o.gamma;
    var lightDeg = o.lightDeg == null ? 118 : o.lightDeg;
    var windDeg = o.windDeg == null ? 200 : o.windDeg;
    var ridgeCount = o.ridges;   /* resolved below, once depth is known */
    var weightNear = o.weightNear == null ? 2.2 : o.weightNear;
    var weightFar = o.weightFar == null ? 0.55 : o.weightFar;
    var specular = o.specular !== false;
    var step = o.step == null ? 4 : o.step;

    var depth = Math.max(1, bottom - Math.min.apply(null, sampleTop(top, x0, x1, 24)));
    if (ridgeCount == null) {
      /* one ridge per ~3.4px of depth, scaled by how much width the region
       * actually spans. Calibrated against tests/txcarve_verify.py, where 46
       * ridges lost to the old hatch on detail_ratio and this density wins. */
      ridgeCount = Math.max(24, Math.round((depth / 3.4) * ((x1 - x0) / 1080)));
    }
    var r = rng(seed);
    var lightX = Math.cos(lightDeg * Math.PI / 180);
    var fall = Math.tan((windDeg - 180) * Math.PI / 180) * 0.16;

    /* 1. VALUE LADDER, as strips. See the order-independence note in the header. */
    var bandH = depth / bands;
    for (var b = 0; b < bands; b++) {
      var t = b / (bands - 1);
      var yOff = b * bandH;
      cx.beginPath();
      var x;
      for (x = x0 - step; x <= x1 + step; x += step) cx.lineTo(x, top(x) + yOff);
      for (x = x1 + step; x >= x0 - step; x -= step) {
        cx.lineTo(x, top(x) + yOff + bandH + 1.2);   /* 1.2px overlap kills seams */
      }
      cx.closePath();
      cx.fillStyle = mix(lit, shadow, Math.pow(t, gamma));
      cx.fill();
    }

    /* 2. RIDGES. Each ridge is a windward edge plus a lee shadow, tapered
     * along its own length and scaled by depth, so weight varies both within a
     * mark and between marks. */
    var weights = [];
    for (var i = 0; i < ridgeCount; i++) {
      var d = Math.pow(r(), 0.72);                 /* bias marks toward the crest */
      var yOff2 = 6 + d * (depth - 14);
      var near = 1 - d;
      var w = weightFar + (weightNear - weightFar) * Math.pow(near, 1.35);
      var len = (0.06 + Math.pow(r(), 1.6) * 0.34) * (x1 - x0);
      var sx = x0 - 60 + r() * (x1 - x0 + 40);
      var jitterSeed = 40 + i * 3.7;
      /* +-9 degrees about the wind-projected fall line, so no two ridges are
       * parallel. Level marks read as contours; varied ones read as erosion. */
      var tilt = fall + (r() - 0.5) * 0.32;
      var alpha = (0.26 + 0.40 * near) * (o.alphaScale == null ? 1 : o.alphaScale);
      weights.push(w);

      drawRidge(cx, top, sx, len, yOff2, w, alpha, tilt, jitterSeed, step,
                lit, shadow, lightX, near);
    }

    /* 2b. WIND POLISH. A fine, short, low-amplitude streak population filling
     * the space BETWEEN the ridges, so the surface is never bare ramp. This is
     * the term that carries detail_ratio; without it a ridge field is a few
     * marks floating on a gradient. */
    var pr = rng(seed + 313);
    var polish = o.polish == null ? ridgeCount * 4 : o.polish;
    for (var q = 0; q < polish; q++) {
      var pd = pr();
      var py = 3 + pd * (depth - 6);
      var pnear = 1 - pd;
      var px = x0 - 40 + pr() * (x1 - x0 + 80);
      var plen = (0.02 + pr() * 0.07) * (x1 - x0);
      cx.beginPath();
      var pseg = 4;
      for (var m = 0; m <= pseg; m++) {
        var pxx = px + (m / pseg) * plen;
        var pyy = top(pxx) + py + (pxx - px) * fall + 1.2 * wiggle(pxx, 0.02, q);
        m === 0 ? cx.moveTo(pxx, pyy) : cx.lineTo(pxx, pyy);
      }
      cx.lineWidth = 0.3 + 0.55 * pnear;
      cx.strokeStyle = rgba(pr() < 0.5 ? lit : shadow, (0.06 + 0.13 * pnear) *
                            (o.alphaScale == null ? 1 : o.alphaScale));
      cx.lineCap = "round";
      cx.stroke();
    }

    /* 3. SPECULAR CRESTS on the nearest, brightest ridges. */
    var spec = 0;
    if (specular) {
      var sr = rng(seed + 991);
      var n = o.speculars == null ? Math.round(ridgeCount * 0.9) : o.speculars;
      for (var k = 0; k < n; k++) {
        var sd = Math.pow(sr(), 2.1);              /* strongly favour the crest */
        var sy = 4 + sd * depth * 0.42;
        var sxx = x0 + sr() * (x1 - x0);
        var yy = top(sxx) + sy + 1.6 * wiggle(sxx, 0.011, sd * 40);
        cx.globalAlpha = 0.30 + 0.55 * (1 - sd);
        cx.fillStyle = o.specColor || "#F4F8FF";
        cx.beginPath();
        cx.arc(sxx, yy, 0.5 + sr() * 1.05, 0, 6.2832);
        cx.fill();
        spec++;
      }
      cx.globalAlpha = 1;
    }

    var mn = Math.min.apply(null, weights), mx = Math.max.apply(null, weights);
    var mean = weights.reduce(function (a, v) { return a + v; }, 0) / weights.length;
    var varr = weights.reduce(function (a, v) { return a + (v - mean) * (v - mean); }, 0) /
               weights.length;
    return {bands: bands, ridges: ridgeCount, weightMin: mn, weightMax: mx,
            weightVar: varr, speculars: spec, depth: depth};
  };

  function sampleTop(top, x0, x1, n) {
    var out = [], i;
    for (i = 0; i <= n; i++) out.push(top(x0 + (x1 - x0) * (i / n)));
    return out;
  }

  /* One ridge: a lee shadow first, then the windward edge above it, both
   * tapered. Drawn as short segments so lineWidth can change ALONG the mark,
   * which a single stroked path cannot express. */
  function drawRidge(cx, top, sx, len, yOff, w, alpha, fall, seed, step,
                     lit, shadow, lightX, near) {
    var segs = Math.max(6, Math.round(len / Math.max(6, step * 2)));
    var prev = null;
    for (var s = 0; s <= segs; s++) {
      var u = s / segs;
      var x = sx + u * len;
      var taper = Math.sin(Math.PI * Math.min(1, Math.max(0, u)));
      taper = Math.pow(taper, 0.62);               /* full weight over the middle */
      var y = top(x) + yOff + (x - sx) * fall +
              2.4 * wiggle(x, 0.010, seed) + 1.1 * wiggle(x, 0.031, seed + 5);
      if (prev) {
        /* lee side, below the crest, in the shadow colour */
        cx.beginPath();
        cx.moveTo(prev[0], prev[1] + w * 1.45);
        cx.lineTo(x, y + w * 1.45);
        cx.lineWidth = Math.max(0.4, w * taper * 1.15);
        cx.strokeStyle = rgba(shadow, alpha * 1.05);
        cx.lineCap = "round";
        cx.stroke();
        /* windward edge, lit, offset toward the key */
        cx.beginPath();
        cx.moveTo(prev[0] + lightX * 0.6, prev[1]);
        cx.lineTo(x + lightX * 0.6, y);
        cx.lineWidth = Math.max(0.35, w * taper);
        cx.strokeStyle = rgba(lit, alpha * (0.75 + 0.45 * near));
        cx.stroke();
      }
      prev = [x, y];
    }
  }

  /* ---------------------------------------------------------- contactShadow
   * Two parts, always: a tight contact term that says the object touches the
   * ground, and a wide ambient term that says it sits in a lit room. One
   * without the other reads as a sticker or as a smudge.
   */
  S.contactShadow = function (cx, o) {
    o = o || {};
    var x = need(o.x, "x"), y = need(o.y, "y");
    var w = o.w == null ? 60 : o.w;
    var color = o.color || "#101F33";
    var rgbv = hexToRgb(color);
    if (rgbv[0] + rgbv[1] + rgbv[2] === 0) {
      throw new TypeError("TXCARVE.contactShadow: shadow colour may not be pure black. " +
                          "Use a darkened background hue (house rule, DESIGN_DOCTRINE 4).");
    }
    var dirDeg = o.dirDeg == null ? 22 : o.dirDeg;
    var dx = Math.cos(dirDeg * Math.PI / 180), dy = Math.sin(dirDeg * Math.PI / 180);
    var tightA = o.tightAlpha == null ? 0.45 : o.tightAlpha;
    var wideA = o.wideAlpha == null ? 0.12 : o.wideAlpha;

    cx.save();
    /* wide ambient first, so the tight term sits on top of it */
    cx.filter = "blur(" + (o.wideBlur == null ? 22 : o.wideBlur) + "px)";
    cx.fillStyle = rgba(color, wideA);
    cx.beginPath();
    cx.ellipse(x + dx * w * 0.55, y + dy * w * 0.22, w * 1.5, w * 0.42, 0, 0, 6.2832);
    cx.fill();
    cx.filter = "blur(" + (o.tightBlur == null ? 4 : o.tightBlur) + "px)";
    cx.fillStyle = rgba(color, tightA);
    cx.beginPath();
    cx.ellipse(x + dx * w * 0.12, y + dy * w * 0.06, w * 0.52, w * 0.15, 0, 0, 6.2832);
    cx.fill();
    cx.restore();
    return {wide: w * 1.5, tight: w * 0.52};
  };

  global.TXCARVE = S;
})(typeof window !== "undefined" ? window : globalThis);
