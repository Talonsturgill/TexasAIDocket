/* txink.js — the print register. Paper, screens, contour ink, duotone, misregistered plates.
 *
 * WHY THIS EXISTS (2026-09-11). Every deck to date rendered flat vector shapes over a soft
 * gradient with a grain overlay on top, and every judge found a version of the same word for
 * it: "assembled", "clip art", "a diagram of a place". A gradient is what a screen does when
 * nobody decided anything. A PRINT is a set of decisions: a paper, an ink or two, a screen
 * that turns tone into dots or lines a reader can see, a contour that says a hand drew the
 * edge, and plates that do not quite register. Those marks are why an illustration in a
 * magazine looks made and a stock vector looks placed.
 *
 * This file turns a flat scene (anything drawn on a canvas, TXSCENE included) into a print.
 * The shape of every function is the same: take a source canvas at backing resolution, return
 * a new canvas of the same size, never touch the source. The caller composes the result onto
 * the frame with `TXINK.lay(ctx, canvas, o)`, which draws it in CSS units under the caller's
 * transform so a 2x canvas lands 1:1.
 *
 *   const art = TXINK.canvas(cx);                        // an offscreen twin of the frame
 *   // ...draw the scene into art.ctx (it is already scaled like cx)...
 *   TXINK.paper(cx, { base: "#F2EBDD", fibre: 0.07, seed: 11 });
 *   const tone = TXINK.screen(art.el, { mode: "halftone", cell: 7, angle: 22, ink: "#1B1830" });
 *   TXINK.lay(cx, tone, { alpha: 0.92 });
 *   const line = TXINK.edges(art.el, { ink: "#1B1830", threshold: 24 });
 *   TXINK.lay(cx, line, { dx: 1.5, dy: -1 });           // misregistered on purpose
 *
 * SCREENS. `halftone` (round dots on a rotated grid, area proportional to darkness, the
 * newspaper), `line` (parallel lines whose weight carries the tone, the banknote), `hatch`
 * (three threshold passes at three angles, the engraver's cross hatch), `stipple` (jittered
 * dots whose count carries the tone, the field guide). Each reads at feed size when `cell` is
 * 5 to 9 CSS px. Under 4 the screen becomes texture and stops being a mark, over 12 the tone
 * breaks up. Say which in the dossier and let the pixel critic hold you to it.
 *
 * Every function is deterministic for a given seed, so the QA harness re-render compares equal.
 */
(function (global) {
  "use strict";

  var INK = {};

  function hexToRgb(h) {
    var m = String(h).replace("#", "");
    if (m.length === 3) m = m[0] + m[0] + m[1] + m[1] + m[2] + m[2];
    return [parseInt(m.slice(0, 2), 16), parseInt(m.slice(2, 4), 16), parseInt(m.slice(4, 6), 16)];
  }
  function rng(seed) {
    var t = (seed >>> 0) || 1;
    return function () { t += 0x6D2B79F5; var r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; };
  }
  function scaleOf(ctx) { return ctx.getTransform ? (ctx.getTransform().a || 1) : 1; }
  function mk(w, h) { var c = document.createElement("canvas"); c.width = w; c.height = h; return c; }

  // An offscreen twin of a frame context: same backing size, same scale, so scene code that
  // draws in CSS units draws into it unchanged.
  INK.canvas = function (ctx) {
    var s = scaleOf(ctx), el = mk(ctx.canvas.width, ctx.canvas.height), c = el.getContext("2d");
    c.scale(s, s);
    return { el: el, ctx: c, scale: s, w: ctx.canvas.width / s, h: ctx.canvas.height / s };
  };

  // Compose a backing-resolution canvas onto a frame context in CSS units.
  INK.lay = function (ctx, canvas, o) {
    o = o || {};
    var s = scaleOf(ctx), w = ctx.canvas.width / s, h = ctx.canvas.height / s;
    ctx.save();
    if (o.alpha != null) ctx.globalAlpha = o.alpha;
    if (o.blend) ctx.globalCompositeOperation = o.blend;
    ctx.drawImage(canvas, o.dx || 0, o.dy || 0, w, h);
    ctx.restore();
  };

  // Luminance of a canvas as a Float32Array at a reduced size (one value per `cell` CSS px),
  // which is the antialiased sample every screen wants: the mean of the cell, not a point.
  function lumaMap(src, cellPx) {
    var W = Math.max(1, Math.round(src.width / cellPx)), H = Math.max(1, Math.round(src.height / cellPx));
    var c = mk(W, H), x = c.getContext("2d");
    x.imageSmoothingEnabled = true; x.imageSmoothingQuality = "high";
    x.drawImage(src, 0, 0, W, H);
    var d = x.getImageData(0, 0, W, H).data, out = new Float32Array(W * H), a = new Float32Array(W * H);
    for (var i = 0, k = 0; i < d.length; i += 4, k++) { out[k] = (0.2126 * d[i] + 0.7152 * d[i + 1] + 0.0722 * d[i + 2]) / 255; a[k] = d[i + 3] / 255; }
    return { w: W, h: H, l: out, a: a, cell: cellPx };
  }
  function sampleMap(m, x, y) {
    // bilinear, x and y in backing px
    var fx = x / m.cell - 0.5, fy = y / m.cell - 0.5;
    var x0 = Math.floor(fx), y0 = Math.floor(fy), tx = fx - x0, ty = fy - y0;
    var g = function (ix, iy) { ix = Math.min(m.w - 1, Math.max(0, ix)); iy = Math.min(m.h - 1, Math.max(0, iy)); var k = iy * m.w + ix; return [m.l[k], m.a[k]]; };
    var p00 = g(x0, y0), p10 = g(x0 + 1, y0), p01 = g(x0, y0 + 1), p11 = g(x0 + 1, y0 + 1);
    var l = (p00[0] * (1 - tx) + p10[0] * tx) * (1 - ty) + (p01[0] * (1 - tx) + p11[0] * tx) * ty;
    var a = (p00[1] * (1 - tx) + p10[1] * tx) * (1 - ty) + (p01[1] * (1 - tx) + p11[1] * tx) * ty;
    return [l, a];
  }

  /* ------------------------------------------------------------------ screens */

  // Render the tone of `src` as a screen. Returns a canvas of ink on transparent.
  INK.screen = function (src, o) {
    o = o || {};
    var mode = o.mode || "halftone";
    var scale = o.scale || 2;                      // backing px per CSS px of the source
    var cell = (o.cell || 7) * scale;
    var ang = (o.angle == null ? 15 : o.angle) * Math.PI / 180;
    var gamma = o.gamma || 1.0;
    var ink = o.ink || "#1B1830";
    var out = mk(src.width, src.height), c = out.getContext("2d");
    var m = lumaMap(src, Math.max(1, cell / 2));   // sample at half a cell for smooth tone
    var W = src.width, H = src.height;
    var dark = function (x, y) { var s = sampleMap(m, x, y); var d = (1 - s[0]) * s[1]; return Math.pow(Math.min(1, Math.max(0, d)), gamma); };
    var invert = !!o.invert;                       // ink where the source is LIGHT (for a dark paper)
    if (invert) dark = function (x, y) { var s = sampleMap(m, x, y); return Math.pow(Math.min(1, Math.max(0, s[0] * s[1])), gamma); };
    c.fillStyle = ink; c.strokeStyle = ink; c.lineCap = "round";
    var diag = Math.sqrt(W * W + H * H);
    var cosA = Math.cos(ang), sinA = Math.sin(ang);
    var toScreen = function (u, v) { return [W / 2 + u * cosA - v * sinA, H / 2 + u * sinA + v * cosA]; };
    var r = rng(o.seed || 7);

    if (mode === "halftone") {
      var maxR = cell * 0.62, minD = o.floor == null ? 0.04 : o.floor;
      for (var v = -diag / 2; v <= diag / 2; v += cell) {
        for (var u = -diag / 2; u <= diag / 2; u += cell) {
          var p = toScreen(u, v); if (p[0] < -cell || p[1] < -cell || p[0] > W + cell || p[1] > H + cell) continue;
          var d = dark(p[0], p[1]); if (d < minD) continue;
          var rad = maxR * Math.sqrt(d);
          c.beginPath(); c.arc(p[0], p[1], rad, 0, Math.PI * 2); c.fill();
        }
      }
    } else if (mode === "line") {
      var step = cell * 0.5, maxW = cell * 0.9;
      for (var v2 = -diag / 2; v2 <= diag / 2; v2 += cell) {
        var prev = null;
        for (var u2 = -diag / 2; u2 <= diag / 2 + step; u2 += step) {
          var q = toScreen(u2, v2);
          var dd = (q[0] < -cell || q[1] < -cell || q[0] > W + cell || q[1] > H + cell) ? 0 : dark(q[0], q[1]);
          if (prev && (dd > 0.03 || prev[2] > 0.03)) {
            c.lineWidth = Math.max(0.3, maxW * (dd + prev[2]) / 2);
            c.beginPath(); c.moveTo(prev[0], prev[1]); c.lineTo(q[0], q[1]); c.stroke();
          }
          prev = [q[0], q[1], dd];
        }
      }
    } else if (mode === "hatch") {
      // three passes: each adds a family of lines where the tone is darker than its threshold
      var passes = o.passes || [[ang, 0.22], [ang + Math.PI / 2 + 0.2, 0.5], [ang + Math.PI / 4, 0.76]];
      var lw = Math.max(0.8, cell * 0.16 * (o.weight || 1));
      c.lineWidth = lw;
      passes.forEach(function (ps) {
        var a2 = ps[0], thr = ps[1], ca = Math.cos(a2), sa = Math.sin(a2);
        var ts = function (u, v) { return [W / 2 + u * ca - v * sa, H / 2 + u * sa + v * ca]; };
        var st = cell * 0.35;
        for (var v3 = -diag / 2; v3 <= diag / 2; v3 += cell * 0.9) {
          var on = false, sx = 0, sy = 0;
          for (var u3 = -diag / 2; u3 <= diag / 2 + st; u3 += st) {
            var q3 = ts(u3, v3);
            var inside = q3[0] >= -1 && q3[1] >= -1 && q3[0] <= W + 1 && q3[1] <= H + 1;
            var hit = inside && dark(q3[0], q3[1]) > thr;
            if (hit && !on) { on = true; sx = q3[0]; sy = q3[1]; }
            else if (!hit && on) { on = false; c.beginPath(); c.moveTo(sx, sy); c.lineTo(q3[0], q3[1]); c.stroke(); }
          }
        }
      });
    } else if (mode === "stipple") {
      var per = o.perCell || 6, dot = Math.max(0.6, cell * 0.11 * (o.weight || 1));
      for (var y = 0; y < H; y += cell) for (var x = 0; x < W; x += cell) {
        var d4 = dark(x + cell / 2, y + cell / 2);
        var n = Math.round(d4 * d4 * per + (r() < d4 * per - Math.floor(d4 * per) ? 1 : 0));
        for (var k = 0; k < n; k++) { var px = x + r() * cell, py = y + r() * cell; c.beginPath(); c.arc(px, py, dot * (0.7 + r() * 0.6), 0, Math.PI * 2); c.fill(); }
      }
    } else throw new Error("TXINK.screen: unknown mode '" + mode + "'");
    return out;
  };

  /* ------------------------------------------------------------------ contour ink */

  // The drawn edge: a Sobel on the source's luminance, thresholded, laid down as ink. This is
  // what makes a flat shape read as drawn rather than placed. `threshold` is in luminance
  // steps out of 255 across one CSS px; 18 to 30 keeps object edges and drops tone steps.
  INK.edges = function (src, o) {
    o = o || {};
    var scale = o.scale || 2, ink = hexToRgb(o.ink || "#1B1830"), thr = (o.threshold == null ? 24 : o.threshold) / 255;
    var soft = o.soft == null ? 0.6 : o.soft;
    var m = lumaMap(src, scale);                   // one sample per CSS px
    var W = m.w, H = m.h, out = mk(W, H), c = out.getContext("2d"), img = c.createImageData(W, H), d = img.data;
    var L = m.l, A = m.a;
    for (var y = 1; y < H - 1; y++) for (var x = 1; x < W - 1; x++) {
      var i = y * W + x;
      var gx = -L[i - W - 1] - 2 * L[i - 1] - L[i + W - 1] + L[i - W + 1] + 2 * L[i + 1] + L[i + W + 1];
      var gy = -L[i - W - 1] - 2 * L[i - W] - L[i - W + 1] + L[i + W - 1] + 2 * L[i + W] + L[i + W + 1];
      var ax = -A[i - W - 1] - 2 * A[i - 1] - A[i + W - 1] + A[i - W + 1] + 2 * A[i + 1] + A[i + W + 1];
      var ay = -A[i - W - 1] - 2 * A[i - W] - A[i - W + 1] + A[i + W - 1] + 2 * A[i + W] + A[i + W + 1];
      var g = Math.sqrt(gx * gx + gy * gy) / 4 + Math.sqrt(ax * ax + ay * ay) / 4;
      var a = g < thr ? 0 : Math.min(1, (g - thr) / (thr * soft + 1e-6));
      if (a <= 0) continue;
      var k = i * 4; d[k] = ink[0]; d[k + 1] = ink[1]; d[k + 2] = ink[2]; d[k + 3] = Math.round(a * 255);
    }
    c.putImageData(img, 0, 0);
    if (o.width && o.width > 1) {
      // thicken by drawing the line layer over itself with small offsets
      var t = mk(W, H), tc = t.getContext("2d"), r = (o.width - 1) * 0.5;
      [[-r, 0], [r, 0], [0, -r], [0, r], [0, 0]].forEach(function (off) { tc.drawImage(out, off[0], off[1]); });
      return t;
    }
    return out;
  };

  /* ------------------------------------------------------------------ tone maps */

  // Map the source's luminance onto a ramp from `shadow` to `highlight`, optionally through
  // `mid`. Alpha is kept. This is the two-ink print, or the risograph.
  INK.duotone = function (src, o) {
    o = o || {};
    var sh = hexToRgb(o.shadow || "#1B1830"), hi = hexToRgb(o.highlight || "#F2EBDD"), mid = o.mid ? hexToRgb(o.mid) : null;
    var gamma = o.gamma || 1;
    var W = src.width, H = src.height, out = mk(W, H), c = out.getContext("2d");
    c.drawImage(src, 0, 0);
    var img = c.getImageData(0, 0, W, H), d = img.data;
    var lut = new Uint8ClampedArray(256 * 3);
    for (var v = 0; v < 256; v++) {
      var t = Math.pow(v / 255, gamma), col;
      if (mid) { if (t < 0.5) { var u = t * 2; col = [sh[0] + (mid[0] - sh[0]) * u, sh[1] + (mid[1] - sh[1]) * u, sh[2] + (mid[2] - sh[2]) * u]; } else { var u2 = (t - 0.5) * 2; col = [mid[0] + (hi[0] - mid[0]) * u2, mid[1] + (hi[1] - mid[1]) * u2, mid[2] + (hi[2] - mid[2]) * u2]; } }
      else col = [sh[0] + (hi[0] - sh[0]) * t, sh[1] + (hi[1] - sh[1]) * t, sh[2] + (hi[2] - sh[2]) * t];
      lut[v * 3] = col[0]; lut[v * 3 + 1] = col[1]; lut[v * 3 + 2] = col[2];
    }
    for (var i = 0; i < d.length; i += 4) {
      var l = Math.round(0.2126 * d[i] + 0.7152 * d[i + 1] + 0.0722 * d[i + 2]);
      d[i] = lut[l * 3]; d[i + 1] = lut[l * 3 + 1]; d[i + 2] = lut[l * 3 + 2];
    }
    c.putImageData(img, 0, 0);
    return out;
  };

  // Posterise the source to `steps` flat tones, which is what a silkscreen does to a photo.
  INK.posterise = function (src, o) {
    o = o || {};
    var steps = o.steps || 4, W = src.width, H = src.height, out = mk(W, H), c = out.getContext("2d");
    c.drawImage(src, 0, 0);
    var img = c.getImageData(0, 0, W, H), d = img.data, q = 255 / (steps - 1);
    for (var i = 0; i < d.length; i += 4) { d[i] = Math.round(d[i] / q) * q; d[i + 1] = Math.round(d[i + 1] / q) * q; d[i + 2] = Math.round(d[i + 2] / q) * q; }
    c.putImageData(img, 0, 0);
    return out;
  };

  // Recolour a mask (anything with alpha) to one flat ink: a plate.
  INK.tint = function (src, hex) {
    var out = mk(src.width, src.height), c = out.getContext("2d");
    c.drawImage(src, 0, 0);
    c.globalCompositeOperation = "source-in"; c.fillStyle = hex; c.fillRect(0, 0, src.width, src.height);
    return out;
  };

  /* ------------------------------------------------------------------ paper */

  // A paper ground: a base colour with fibre and a faint mottle, tiled from one seeded tile
  // so it costs nothing. `fibre` 0.04 to 0.10 is visible at feed size without reading as dirt.
  INK.paper = function (ctx, o) {
    o = o || {};
    var s = scaleOf(ctx), w = ctx.canvas.width / s, h = ctx.canvas.height / s;
    var base = o.base || "#F2EBDD", fibre = o.fibre == null ? 0.06 : o.fibre, seed = o.seed || 3;
    ctx.save();
    ctx.fillStyle = base; ctx.fillRect(0, 0, w, h);
    var T = 384, tile = mk(T, T), tc = tile.getContext("2d"), img = tc.createImageData(T, T), d = img.data, r = rng(seed);
    // mottle: a few soft blobs; fibre: short horizontal streaks
    var blobs = [];
    for (var b = 0; b < 26; b++) blobs.push([r() * T, r() * T, 30 + r() * 70, (r() - 0.5) * 2]);
    var streaks = [];
    for (var q = 0; q < 900; q++) streaks.push([r() * T, r() * T, 6 + r() * 26, (r() - 0.5) * 2]);
    var v = new Float32Array(T * T);
    blobs.forEach(function (bl) { for (var y = 0; y < T; y++) for (var x = 0; x < T; x++) { var dx = Math.min(Math.abs(x - bl[0]), T - Math.abs(x - bl[0])), dy = Math.min(Math.abs(y - bl[1]), T - Math.abs(y - bl[1])); var dd = (dx * dx + dy * dy) / (bl[2] * bl[2]); if (dd < 1) v[y * T + x] += bl[3] * (1 - dd) * (1 - dd) * 0.5; } });
    streaks.forEach(function (st) { var y = Math.round(st[1]) % T; for (var k = 0; k < st[2]; k++) { var x = (Math.round(st[0]) + k) % T; v[y * T + x] += st[3] * 0.9 * Math.sin(k / st[2] * Math.PI); } });
    for (var i = 0; i < T * T; i++) { var n = v[i] + (r() - 0.5) * 0.9; var g = n > 0 ? 255 : 0; d[i * 4] = g; d[i * 4 + 1] = g; d[i * 4 + 2] = g; d[i * 4 + 3] = Math.min(255, Math.round(Math.abs(n) * 255 * fibre)); }
    tc.putImageData(img, 0, 0);
    ctx.fillStyle = ctx.createPattern(tile, "repeat");
    ctx.fillRect(0, 0, w, h);
    ctx.restore();
  };

  /* ------------------------------------------------------------------ plates */

  // Lay several plates with misregistration, the way a press does: each plate is a canvas
  // (a screen, an edge pass, a tinted mask), shifted by its own offset and multiplied down.
  //   TXINK.press(cx, [{ canvas: tone, alpha: .9 }, { canvas: line, dx: 1.5, dy: -1 }], { wobble: 1.2, seed: 5 })
  INK.press = function (ctx, plates, o) {
    o = o || {};
    var r = rng(o.seed || 9), wob = o.wobble == null ? 0 : o.wobble;
    plates.forEach(function (p) {
      var dx = (p.dx || 0) + (r() - 0.5) * 2 * wob, dy = (p.dy || 0) + (r() - 0.5) * 2 * wob;
      INK.lay(ctx, p.canvas, { dx: dx, dy: dy, alpha: p.alpha, blend: p.blend || "multiply" });
    });
  };

  /* ------------------------------------------------------------------ hand */

  // An SVG path `d` redrawn as a polyline with a slow wobble, so a ruled line reads as a
  // drawn one. Needs a document (it measures with a temporary SVG path). `amp` in px.
  INK.wobble = function (d, o) {
    o = o || {};
    var amp = o.amp == null ? 1.2 : o.amp, freq = o.freq || 0.018, seed = o.seed || 1, step = o.step || 6;
    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", d); svg.appendChild(path); svg.style.position = "absolute"; svg.style.width = "0"; svg.style.height = "0";
    document.body.appendChild(svg);
    var L = path.getTotalLength(), out = [], r = rng(seed), ph1 = r() * 100, ph2 = r() * 100;
    for (var t = 0; t <= L; t += step) {
      var p = path.getPointAtLength(t), q = path.getPointAtLength(Math.min(L, t + 1));
      var nx = -(q.y - p.y), ny = q.x - p.x, nl = Math.sqrt(nx * nx + ny * ny) || 1; nx /= nl; ny /= nl;
      var off = amp * (Math.sin(t * freq + ph1) * 0.7 + Math.sin(t * freq * 2.7 + ph2) * 0.3);
      out.push((t === 0 ? "M" : "L") + (p.x + nx * off).toFixed(2) + " " + (p.y + ny * off).toFixed(2));
    }
    document.body.removeChild(svg);
    return out.join(" ");
  };

  // A hatch fill for a polygon in CSS px on a context: parallel lines clipped to the shape,
  // for a shadow side, a ground, a roof. `spacing` and `width` in CSS px.
  INK.hatchFill = function (ctx, pts, o) {
    o = o || {};
    var ang = (o.angle == null ? 45 : o.angle) * Math.PI / 180, sp = o.spacing || 6, lw = o.width || 1.2, r = rng(o.seed || 1), jit = o.jitter || 0;
    var minx = Infinity, miny = Infinity, maxx = -Infinity, maxy = -Infinity;
    pts.forEach(function (p) { minx = Math.min(minx, p[0]); miny = Math.min(miny, p[1]); maxx = Math.max(maxx, p[0]); maxy = Math.max(maxy, p[1]); });
    var cx = (minx + maxx) / 2, cy = (miny + maxy) / 2, R = Math.sqrt((maxx - minx) * (maxx - minx) + (maxy - miny) * (maxy - miny)) / 2 + sp;
    ctx.save();
    ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); for (var i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]); ctx.closePath(); ctx.clip();
    ctx.strokeStyle = o.ink || "#1B1830"; ctx.lineWidth = lw; ctx.lineCap = "round";
    var ca = Math.cos(ang), sa = Math.sin(ang);
    for (var v = -R; v <= R; v += sp) {
      var j = (r() - 0.5) * jit;
      var x0 = cx + (-R) * ca - (v + j) * sa, y0 = cy + (-R) * sa + (v + j) * ca, x1 = cx + R * ca - (v + j) * sa, y1 = cy + R * sa + (v + j) * ca;
      ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();
    }
    ctx.restore();
  };

  /* ------------------------------------------------------------------ the one call */

  // Draw a scene as a print, in one call. `draw(ctx)` paints the TONE scene into an offscreen
  // twin in greys (light objects on a dark ground for a night deck, dark on light for paper).
  // The ground is laid as paper, the twin is screened into ink dots or lines, the contour
  // plate is laid on top slightly out of register, and `over(ctx)` then paints anything that
  // must stay flat colour (the one accent plate, a lamp). Returns the plates for reuse.
  //
  //   TXINK.print(cx, {
  //     ground: "#0F0C1C", ink: "#EDE6D6", fibre: 0.05, seed: 21,
  //     screen: { mode: "halftone", cell: 6, angle: 22, gamma: 1.1 },
  //     edges: { threshold: 22, width: 1.4, alpha: 0.85, dx: 1.2, dy: -0.8 },
  //     draw: function (a) { ...TXSCENE on a... },
  //     over: function (c) { ...accent plate... }
  //   });
  INK.print = function (ctx, o) {
    o = o || {};
    var ground = o.ground || "#0F0C1C", ink = o.ink || "#EDE6D6";
    var g = hexToRgb(ground), dark = (0.2126 * g[0] + 0.7152 * g[1] + 0.0722 * g[2]) < 128;
    var twin = INK.canvas(ctx);
    twin.ctx.fillStyle = dark ? "#000000" : "#FFFFFF"; twin.ctx.fillRect(0, 0, twin.w, twin.h);
    if (o.draw) o.draw(twin.ctx, twin);
    INK.paper(ctx, { base: ground, fibre: o.fibre == null ? 0.05 : o.fibre, seed: o.seed || 3 });
    var plates = [];
    var sc = o.screen || { mode: "halftone", cell: 6, angle: 22 };
    if (sc !== false) {
      var tone = INK.screen(twin.el, { mode: sc.mode || "halftone", cell: sc.cell || 6, angle: sc.angle == null ? 22 : sc.angle, gamma: sc.gamma, floor: sc.floor, perCell: sc.perCell, weight: sc.weight, passes: sc.passes, ink: ink, invert: dark, scale: twin.scale, seed: o.seed || 3 });
      plates.push({ canvas: tone, alpha: sc.alpha == null ? 0.95 : sc.alpha, blend: dark ? "screen" : "multiply" });
    }
    var ed = o.edges;
    if (ed !== false) {
      ed = ed || {};
      var line = INK.edges(twin.el, { ink: ink, threshold: ed.threshold == null ? 22 : ed.threshold, width: ed.width || 1.4, scale: twin.scale, soft: ed.soft });
      plates.push({ canvas: line, alpha: ed.alpha == null ? 0.85 : ed.alpha, dx: ed.dx == null ? 1.2 : ed.dx, dy: ed.dy == null ? -0.8 : ed.dy, blend: dark ? "screen" : "multiply" });
    }
    INK.press(ctx, plates, { wobble: o.wobble == null ? 0.4 : o.wobble, seed: o.seed || 3 });
    if (o.over) o.over(ctx, twin);
    return { twin: twin, plates: plates, dark: dark };
  };

  // Quiet the furniture bands: fade the print into the ground colour over the top and bottom
  // strips where the kicker, counter, source and site lines sit, so a full bleed image never
  // strikes a label. Call after print() and before mounting type. Heights in CSS px.
  INK.reserve = function (ctx, o) {
    o = o || {};
    var s = scaleOf(ctx), w = ctx.canvas.width / s, h = ctx.canvas.height / s, ground = o.ground || "#0F0C1C";
    var g = hexToRgb(ground), rgba = function (a) { return "rgba(" + g[0] + "," + g[1] + "," + g[2] + "," + a + ")"; };
    ctx.save();
    // `top`/`bottom` are the full band heights; `topSolid`/`bottomSolid` the part of each band
    // that is fully ground, so the fade occupies only the difference and type never sits on
    // a half faded print.
    if (o.top) {
      var ts = Math.min(o.top, o.topSolid == null ? o.top * 0.6 : o.topSolid);
      var gt = ctx.createLinearGradient(0, ts, 0, o.top); gt.addColorStop(0, rgba(1)); gt.addColorStop(1, rgba(0));
      ctx.fillStyle = rgba(1); ctx.fillRect(0, 0, w, ts); ctx.fillStyle = gt; ctx.fillRect(0, ts, w, o.top - ts);
    }
    if (o.bottom) {
      var bs = Math.min(o.bottom, o.bottomSolid == null ? o.bottom * 0.6 : o.bottomSolid);
      var gb = ctx.createLinearGradient(0, h - o.bottom, 0, h - bs); gb.addColorStop(0, rgba(0)); gb.addColorStop(1, rgba(1));
      ctx.fillStyle = gb; ctx.fillRect(0, h - o.bottom, w, o.bottom - bs); ctx.fillStyle = rgba(1); ctx.fillRect(0, h - bs, w, bs);
    }
    if (o.rect) { ctx.fillStyle = rgba(o.rectAlpha == null ? 0.92 : o.rectAlpha); ctx.fillRect(o.rect.x, o.rect.y, o.rect.w, o.rect.h); }
    ctx.restore();
  };

  INK.rng = rng;
  global.TXINK = INK;
})(typeof window !== "undefined" ? window : globalThis);
