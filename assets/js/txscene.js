/* txscene.js — the 2.5D scene bench. A ground plane, a horizon, one light, and objects
 * placed at TRUE SCALE in metres. Offline, deterministic, Canvas 2D only, no dependencies.
 *
 * WHY THIS EXISTS (2026-09-11, the upgrade session after carousel no. 21).
 *
 * Twenty one decks shipped and the judges' craft finding was the same one every time, in
 * different words: a small primitive floating in a gradient with the type stacked above it.
 * "Assembled, not drawn." "An object in a void." "Frame 9 is two planes and two books."
 * The cause was structural rather than a lapse of taste. Every frame was drawn in screen
 * pixels with no camera, so nothing had a size, nothing stood on anything, nothing cast a
 * shadow onto anything, and a bus was a slab because a slab is what you draw when you do
 * not know how tall a bus is.
 *
 * This file gives a frame a CAMERA. Everything below is in metres. A school bus is 12 by 3.
 * A person is 1.7. A utility pole is 12. Put them on the ground at a depth and they come out
 * the right size relative to each other, the ground recedes correctly, the horizon sits
 * where the eye height says, and one declared light casts every shadow onto the plane. That
 * is most of what makes a drawing read as a place rather than a diagram of one.
 *
 * THE MODEL. A pinhole camera at height `eye` metres above a flat ground, looking level, so
 * the horizon is a horizontal line at `horizon` screen px. World axes: X lateral (right is
 * positive), Y up (ground is 0), Z depth in front of the camera. A point projects to
 *
 *     sx = w/2 + f * X / Z
 *     sy = horizon - f * (Y - eye) / Z
 *
 * with `f` the focal length in px. So the ground at depth Z sits at sy = horizon + f*eye/Z,
 * and an object of height H at depth Z is H*f/Z px tall. Camera pitch is deliberately not
 * modelled: a level camera keeps every vertical vertical, which is what a poster wants, and
 * the horizon can still be placed anywhere by choosing `eye` and `horizon` together. The
 * deck-wide "44 inch law" (seated eye height, horizon at one y on every frame) is one call.
 *
 * SPRITES. An object is a list of parts in its own metres, origin at the centre of its
 * footprint, y UP. Parts are polygons, rects, ellipses and thick round-capped lines, which
 * is enough to draw anything in this register and keeps every shape transformable by the
 * same affine map. `txobjects.js` and `txfig.js` build sprites; this file places them.
 *
 * USAGE (inside renderReady, on a 2x canvas already scaled):
 *
 *   const S = TXSCENE.create(cx, { w:1080, h:1350, eye:1.4, horizon:640, f:820,
 *                                  sky:'#C9D7D1', light:{az:-40, el:38} });
 *   S.ground({ near:1.5, far:400, fill:'#8B8F7E' });
 *   S.gridZ({ dz:4, from:2, to:120, ink:'rgba(0,0,0,0.12)', width:1.2 });
 *   const bus = TXOBJ.sprite('school_bus');
 *   S.shadow(bus, { X:6, Z:30, ink:'#1B1830', alpha:0.32 });
 *   S.sprite(bus, { X:6, Z:30, inks:{ ink:'#1B1830', paper:'#F2EBDD', accent:'#D8731F' } });
 *
 * Draw far things first. The bench does not z-sort for you, because a slide is a drawing and
 * the drawer decides the order.
 */
(function (global) {
  "use strict";

  var SCENE = {};

  function need(v, name) {
    if (v == null || (typeof v === "number" && !isFinite(v)))
      throw new TypeError("TXSCENE: option '" + name + "' is required and must be finite");
    return v;
  }
  function num(v, d) { return (typeof v === "number" && isFinite(v)) ? v : d; }

  function hexToRgb(h) {
    if (typeof h !== "string") return null;
    var m = h.replace("#", "");
    if (m.length === 3) m = m[0] + m[0] + m[1] + m[1] + m[2] + m[2];
    if (m.length !== 6) return null;
    return [parseInt(m.slice(0, 2), 16), parseInt(m.slice(2, 4), 16), parseInt(m.slice(4, 6), 16)];
  }
  function rgbToHex(c) {
    return "#" + c.map(function (v) {
      var s = Math.max(0, Math.min(255, Math.round(v))).toString(16);
      return s.length < 2 ? "0" + s : s;
    }).join("");
  }
  function mixHex(a, b, t) {
    var A = hexToRgb(a), B = hexToRgb(b);
    if (!A || !B) return a;
    return rgbToHex([A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t, A[2] + (B[2] - A[2]) * t]);
  }
  // Perceived lightness, for tone steps that read evenly.
  function lum(hex) {
    var c = hexToRgb(hex); if (!c) return 0.5;
    var f = function (v) { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]);
  }

  /* -------------------------------------------------------------- the camera */

  SCENE.create = function (cx, o) {
    o = o || {};
    var w = num(o.w, 1080), h = num(o.h, 1350);
    var eye = num(o.eye, 1.4);                 // metres above the ground
    var horizon = num(o.horizon, Math.round(h * 0.48));
    var f = num(o.f, 820);                     // focal length in px
    var sky = o.sky || "#DDE3E0";
    var fogZ = num(o.fogZ, 260);               // depth at which a form has faded 63% to sky
    var light = o.light || { az: -35, el: 40 };
    if (typeof light.az !== "number" || typeof light.el !== "number")
      throw new TypeError("TXSCENE: light needs numeric az and el in degrees");
    if (light.el <= 2 || light.el >= 88)
      throw new RangeError("TXSCENE: light elevation " + light.el + " casts no usable shadow; use 8 to 75");
    var azR = light.az * Math.PI / 180, elR = light.el * Math.PI / 180;
    var cot = 1 / Math.tan(elR);
    var ctx = cx;

    var S = { w: w, h: h, eye: eye, horizon: horizon, f: f, sky: sky, light: light, ctx: ctx };

    S.project = function (X, Y, Z) {
      if (Z <= 0.05) Z = 0.05;
      return [w / 2 + f * X / Z, horizon - f * (Y - eye) / Z];
    };
    S.groundY = function (Z) { return horizon + f * eye / Math.max(0.05, Z); };
    S.depthAt = function (sy) { return sy <= horizon + 0.01 ? Infinity : f * eye / (sy - horizon); };
    S.ppm = function (Z) { return f / Math.max(0.05, Z); };          // px per metre at depth Z
    S.fade = function (hex, Z) {                                        // atmospheric perspective
      var k = 1 - Math.exp(-Math.max(0, Z) / fogZ);
      return mixHex(hex, sky, k);
    };
    // Shadow displacement per metre of height, in world XZ, pointing AWAY from the light.
    S.shadowVec = function () { return [-Math.sin(azR) * cot, -Math.cos(azR) * cot]; };

    /* ------------------------------------------------------------ the ground */

    // Fills the ground plane from `far` to `near` metres and returns the screen trapezoid.
    S.ground = function (g) {
      g = g || {};
      var near = num(g.near, 0.8), far = num(g.far, 600);
      var yN = Math.min(h, S.groundY(near)), yF = S.groundY(far);
      ctx.save();
      if (g.fill) {
        if (g.fadeToSky) {
          var grd = ctx.createLinearGradient(0, yF, 0, yN);
          grd.addColorStop(0, S.fade(g.fill, far));
          grd.addColorStop(0.25, S.fade(g.fill, far * 0.25));
          grd.addColorStop(1, g.fill);
          ctx.fillStyle = grd;
        } else ctx.fillStyle = g.fill;
        ctx.fillRect(0, yF, w, yN - yF);
      }
      ctx.restore();
      return { top: yF, bottom: yN };
    };

    // Receding joints: lines of constant depth every dz metres between two depths.
    S.gridZ = function (g) {
      g = g || {};
      var dz = num(g.dz, 2), from = num(g.from, 2), to = num(g.to, 200);
      ctx.save();
      ctx.strokeStyle = g.ink || "rgba(0,0,0,0.14)";
      for (var Z = from; Z <= to; Z += dz) {
        var y = S.groundY(Z);
        if (y < horizon + 0.5) break;
        ctx.lineWidth = Math.max(0.4, num(g.width, 1.2) * Math.min(1, 12 / Z));
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
      }
      ctx.restore();
    };
    // Lines of constant lateral position every dx metres, converging on the vanishing point.
    S.gridX = function (g) {
      g = g || {};
      var dx = num(g.dx, 2), from = num(g.from, -60), to = num(g.to, 60);
      var zN = num(g.near, 0.8), zF = num(g.far, 400);
      ctx.save();
      ctx.strokeStyle = g.ink || "rgba(0,0,0,0.14)";
      ctx.lineWidth = num(g.width, 1.2);
      for (var X = from; X <= to; X += dx) {
        var a = S.project(X, 0, zN), b = S.project(X, 0, zF);
        ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke();
      }
      ctx.restore();
    };
    // A road or a strip of ground of width `wm` centred at X, from far to near, as a filled band.
    S.strip = function (g) {
      g = g || {};
      var X = num(g.X, 0), wm = num(g.w, 6), zN = num(g.near, 0.8), zF = num(g.far, 400);
      var p = [S.project(X - wm / 2, 0, zF), S.project(X + wm / 2, 0, zF),
               S.project(X + wm / 2, 0, zN), S.project(X - wm / 2, 0, zN)];
      ctx.save(); ctx.fillStyle = g.fill || "#333";
      ctx.beginPath(); ctx.moveTo(p[0][0], p[0][1]);
      for (var i = 1; i < 4; i++) ctx.lineTo(p[i][0], p[i][1]);
      ctx.closePath(); ctx.fill(); ctx.restore();
      return p;
    };

    /* ------------------------------------------------------------ sprites */

    // The affine map from a sprite's local metres (x right, y up, origin at the footprint
    // centre) at world (X, Z) to screen px. Returns [a, d, e, f] for setTransform-free use.
    function mapper(X, Z, mirror, lift) {
      Z = Math.max(0.05, Z);
      var s = f / Z;
      var ox = w / 2 + f * X / Z, oy = horizon + f * (eye - (lift || 0)) / Z;
      var mx = mirror ? -1 : 1;
      return function (lx, ly) { return [ox + s * lx * mx, oy - s * ly]; };
    }
    // The screen rect of a local-metre rect on a sprite placed at (X, Z): for mounting DOM
    // type onto a drawn sign, screen or sheet.
    S.rectBox = function (o, r) {
      var M = mapper(num(o.X, 0), need(o.Z, "Z"), !!o.mirror, o.y);
      var a = M(r.x, r.y + r.h), b = M(r.x + r.w, r.y);
      return { x: Math.min(a[0], b[0]), y: Math.min(a[1], b[1]), w: Math.abs(b[0] - a[0]), h: Math.abs(b[1] - a[1]) };
    };

    function partPoints(part) {
      // Every part as a polygon in local metres, for shadows and hulls.
      var pts = [];
      if (part.type === "poly") pts = part.pts.slice();
      else if (part.type === "rect") {
        var x = part.x, y = part.y, pw = part.w, ph = part.h;
        pts = [[x, y], [x + pw, y], [x + pw, y + ph], [x, y + ph]];
      } else if (part.type === "ellipse") {
        for (var i = 0; i < 24; i++) {
          var a = i / 24 * Math.PI * 2;
          pts.push([part.cx + Math.cos(a) * part.rx, part.cy + Math.sin(a) * part.ry]);
        }
      } else if (part.type === "line") {
        // a thick line is a capsule; approximate by its two ends widened
        var r = (part.width || 0.1) / 2;
        for (var k = 0; k < part.pts.length; k++) {
          var p = part.pts[k];
          pts.push([p[0] - r, p[1] - r], [p[0] + r, p[1] - r], [p[0] + r, p[1] + r], [p[0] - r, p[1] + r]);
        }
      }
      return pts;
    }

    function resolveFill(fill, inks, tone) {
      if (!fill || fill === "ink") return inks.ink;
      if (fill === "paper") return inks.paper;
      if (fill === "accent") return inks.accent || inks.ink;
      if (fill === "tone") {
        // a mid value between ink and paper, darker for lower tone numbers
        var t = tone == null ? 0.5 : tone;
        return mixHex(inks.ink, inks.paper, t);
      }
      if (fill === "none") return null;
      return fill; // an explicit colour
    }

    function drawPart(part, M, fill, strokeInk) {
      if (part.type === "poly") {
        var p0 = M(part.pts[0][0], part.pts[0][1]);
        ctx.beginPath(); ctx.moveTo(p0[0], p0[1]);
        for (var i = 1; i < part.pts.length; i++) { var p = M(part.pts[i][0], part.pts[i][1]); ctx.lineTo(p[0], p[1]); }
        ctx.closePath();
        if (fill) { ctx.fillStyle = fill; ctx.fill(); }
        if (part.stroke) { ctx.strokeStyle = strokeInk; ctx.lineWidth = part.strokePx || 1.5; ctx.stroke(); }
      } else if (part.type === "rect") {
        var a = M(part.x, part.y + part.h), b = M(part.x + part.w, part.y);
        var x0 = Math.min(a[0], b[0]), y0 = Math.min(a[1], b[1]);
        var pw = Math.abs(b[0] - a[0]), ph = Math.abs(b[1] - a[1]);
        if (part.r) {
          var r = Math.min(part.r * (pw / part.w), pw / 2, ph / 2);
          ctx.beginPath();
          ctx.moveTo(x0 + r, y0); ctx.lineTo(x0 + pw - r, y0); ctx.quadraticCurveTo(x0 + pw, y0, x0 + pw, y0 + r);
          ctx.lineTo(x0 + pw, y0 + ph - r); ctx.quadraticCurveTo(x0 + pw, y0 + ph, x0 + pw - r, y0 + ph);
          ctx.lineTo(x0 + r, y0 + ph); ctx.quadraticCurveTo(x0, y0 + ph, x0, y0 + ph - r);
          ctx.lineTo(x0, y0 + r); ctx.quadraticCurveTo(x0, y0, x0 + r, y0); ctx.closePath();
          if (fill) { ctx.fillStyle = fill; ctx.fill(); }
          if (part.stroke) { ctx.strokeStyle = strokeInk; ctx.lineWidth = part.strokePx || 1.5; ctx.stroke(); }
        } else {
          if (fill) { ctx.fillStyle = fill; ctx.fillRect(x0, y0, pw, ph); }
          if (part.stroke) { ctx.strokeStyle = strokeInk; ctx.lineWidth = part.strokePx || 1.5; ctx.strokeRect(x0, y0, pw, ph); }
        }
      } else if (part.type === "ellipse") {
        var c = M(part.cx, part.cy), e = M(part.cx + part.rx, part.cy + part.ry);
        ctx.beginPath(); ctx.ellipse(c[0], c[1], Math.abs(e[0] - c[0]), Math.abs(e[1] - c[1]), 0, 0, Math.PI * 2);
        if (fill) { ctx.fillStyle = fill; ctx.fill(); }
        if (part.stroke) { ctx.strokeStyle = strokeInk; ctx.lineWidth = part.strokePx || 1.5; ctx.stroke(); }
      } else if (part.type === "line") {
        var q0 = M(part.pts[0][0], part.pts[0][1]), q1 = M(part.pts[0][0] + (part.width || 0.1), part.pts[0][1]);
        ctx.beginPath(); ctx.moveTo(q0[0], q0[1]);
        for (var j = 1; j < part.pts.length; j++) { var q = M(part.pts[j][0], part.pts[j][1]); ctx.lineTo(q[0], q[1]); }
        ctx.lineCap = part.cap || "round"; ctx.lineJoin = "round";
        ctx.lineWidth = Math.max(0.6, Math.abs(q1[0] - q0[0]));
        ctx.strokeStyle = fill || strokeInk; ctx.stroke();
      }
    }

    // Draw a sprite at world (X, Z). `inks` maps the symbolic fills; `tone` shifts every
    // 'tone' part; `fade` mixes the inks toward the sky by depth (on by default).
    S.sprite = function (sprite, o) {
      o = o || {};
      var X = num(o.X, 0), Z = need(o.Z, "Z");
      var inks = o.inks || { ink: "#1B1830", paper: "#F2EBDD", accent: "#D8731F" };
      if (o.fade !== false) inks = { ink: S.fade(inks.ink, Z), paper: S.fade(inks.paper, Z), accent: S.fade(inks.accent || inks.ink, Z) };
      var M = mapper(X, Z, !!o.mirror, o.y);
      ctx.save();
      if (o.alpha != null) ctx.globalAlpha = o.alpha;
      for (var i = 0; i < sprite.parts.length; i++) {
        var part = sprite.parts[i];
        if (o.only && part.fill !== o.only) continue;     // one plate of the sprite, e.g. only:"accent"
        var fill = resolveFill(part.fill, inks, part.tone != null ? part.tone : o.tone);
        if (o.silhouette) fill = part.fill === "none" ? null : inks.ink;
        drawPart(part, M, fill, inks.ink);
      }
      ctx.restore();
      var bb = S.spriteBox(sprite, o);
      return bb;
    };

    // The screen box a sprite occupies at (X, Z), for placing labels and for the gate.
    S.spriteBox = function (sprite, o) {
      var M = mapper(num(o.X, 0), need(o.Z, "Z"), !!o.mirror, o.y);
      var a = M(-sprite.w / 2, 0), b = M(sprite.w / 2, sprite.h);
      return { x: Math.min(a[0], b[0]), y: Math.min(a[1], b[1]), w: Math.abs(b[0] - a[0]), h: Math.abs(b[1] - a[1]) };
    };

    /* ------------------------------------------------------------ shadows */

    // The ground shadow of a sprite, projected from the declared light and drawn ONCE at the
    // given alpha however many parts overlap. Draw it before the sprite.
    S.shadow = function (sprite, o) {
      o = o || {};
      var X = num(o.X, 0), Z = need(o.Z, "Z"), mx = o.mirror ? -1 : 1, lift = num(o.y, 0);
      var sv = S.shadowVec();
      var ops = [];
      var onGround = function (lx, ly) {
        ly = Math.max(0, ly + lift);
        return S.project(X + lx * mx + sv[0] * ly, 0, Z + sv[1] * ly);
      };
      for (var i = 0; i < sprite.parts.length; i++) {
        var part = sprite.parts[i];
        if (part.fill === "none" || part.noShadow) continue;
        if (part.type === "line") {
          // a thick line's shadow is the same stroke laid on the ground
          var lp = [];
          for (var j = 0; j < part.pts.length; j++) lp.push(onGround(part.pts[j][0], part.pts[j][1]));
          ops.push({ stroke: true, pts: lp, width: (part.width || 0.1) * f / Math.max(0.05, Z), cap: part.cap || "round" });
          continue;
        }
        var pts = partPoints(part), poly = [];
        for (var k = 0; k < pts.length; k++) poly.push(onGround(pts[k][0], pts[k][1]));
        ops.push({ pts: poly });
      }
      paintShadow(ops, o);
    };

    // Paints a set of shadow shapes ONCE through an offscreen mask, so overlapping parts do
    // not stack alpha and the whole shadow reads as one flat tone.
    function paintShadow(ops, o) {
      var scale = ctx.getTransform ? (ctx.getTransform().a || 1) : 1;
      var tmp = document.createElement("canvas");
      tmp.width = Math.round(w * scale); tmp.height = Math.round(h * scale);
      var t = tmp.getContext("2d"); t.scale(scale, scale);
      t.fillStyle = "#000"; t.strokeStyle = "#000"; t.lineJoin = "round";
      for (var i = 0; i < ops.length; i++) {
        var p = ops[i].pts; if (!p || p.length < (ops[i].stroke ? 1 : 3)) continue;
        t.beginPath(); t.moveTo(p[0][0], p[0][1]);
        for (var k = 1; k < p.length; k++) t.lineTo(p[k][0], p[k][1]);
        if (ops[i].stroke) { t.lineCap = ops[i].cap; t.lineWidth = Math.max(0.6, ops[i].width); t.stroke(); }
        else { t.closePath(); t.fill(); }
      }
      // tint the mask to the ink
      t.globalCompositeOperation = "source-in";
      t.fillStyle = o.ink || "#1B1830";
      t.fillRect(0, 0, w, h);
      ctx.save();
      ctx.globalAlpha = o.alpha == null ? 0.3 : o.alpha;
      if (o.blur) ctx.filter = "blur(" + o.blur + "px)";
      ctx.drawImage(tmp, 0, 0, w, h);      // under the caller's transform, 1:1 with the backing store
      ctx.restore();
    }

    /* ------------------------------------------------------------ solids */

    // A box on the ground: front face at Z, depth d behind it. Flat shaded from the light,
    // with a hull shadow. Faces are drawn back to front. Returns the screen polygons.
    S.box = function (o) {
      o = o || {};
      var X = num(o.X, 0), Z = need(o.Z, "Z"), bw = num(o.w, 2), bh = num(o.h, 2), bd = num(o.d, 2);
      var base = o.fill || "#8A8F82";
      var x0 = X - bw / 2, x1 = X + bw / 2, z0 = Z, z1 = Z + bd;
      var P = function (x, y, z) { return S.project(x, y, z); };
      var top = [P(x0, bh, z0), P(x1, bh, z0), P(x1, bh, z1), P(x0, bh, z1)];
      var front = [P(x0, 0, z0), P(x1, 0, z0), P(x1, bh, z0), P(x0, bh, z0)];
      var side = null;
      if (x0 > 0.001) side = [P(x0, 0, z0), P(x0, 0, z1), P(x0, bh, z1), P(x0, bh, z0)];          // we see the left face
      else if (x1 < -0.001) side = [P(x1, 0, z0), P(x1, 0, z1), P(x1, bh, z1), P(x1, bh, z0)];     // we see the right face
      // shading from the light: faces facing the light are lighter
      var L = [Math.sin(azR) * Math.cos(elR), Math.sin(elR), Math.cos(azR) * Math.cos(elR)];
      var shade = function (n) { var d = Math.max(0, n[0] * L[0] + n[1] * L[1] + n[2] * L[2]); return 0.55 + 0.45 * d; };
      var fx = S.fade(base, Z);
      var faceFill = function (k) { return k >= 1 ? mixHex(fx, "#FFFFFF", (k - 1) * 0.6) : mixHex(fx, "#000000", (1 - k) * 0.9); };
      if (o.shadow !== false) {
        var sv = S.shadowVec();
        var hull = [];
        [[x0, z0], [x1, z0], [x1, z1], [x0, z1]].forEach(function (c) {
          hull.push(S.project(c[0], 0, c[1]));
          hull.push(S.project(c[0] + sv[0] * bh, 0, c[1] + sv[1] * bh));
        });
        paintShadow([{ pts: convexHull(hull) }], { ink: o.shadowInk || "#1B1830", alpha: num(o.shadowAlpha, 0.3), blur: o.shadowBlur });
      }
      ctx.save();
      var faces = [[top, [0, 1, 0]], [front, [0, 0, -1]]];
      if (side) faces.push([side, [x0 > 0 ? -1 : 1, 0, 0]]);
      faces.forEach(function (fc) {
        var poly = fc[0], k = shade(fc[1]);
        ctx.fillStyle = faceFill(k * (o.exposure || 1));
        ctx.beginPath(); ctx.moveTo(poly[0][0], poly[0][1]);
        for (var i = 1; i < 4; i++) ctx.lineTo(poly[i][0], poly[i][1]);
        ctx.closePath(); ctx.fill();
        if (o.edge) { ctx.strokeStyle = o.edge; ctx.lineWidth = num(o.edgePx, 1.2); ctx.stroke(); }
      });
      ctx.restore();
      return { top: top, front: front, side: side };
    };

    function convexHull(pts) {
      pts = pts.slice().sort(function (a, b) { return a[0] - b[0] || a[1] - b[1]; });
      var cross = function (o, a, b) { return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]); };
      var lower = [], upper = [];
      pts.forEach(function (p) { while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) lower.pop(); lower.push(p); });
      for (var i = pts.length - 1; i >= 0; i--) { var p = pts[i]; while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], p) <= 0) upper.pop(); upper.push(p); }
      upper.pop(); lower.pop();
      return lower.concat(upper);
    }

    /* ------------------------------------------------------------ helpers */

    // A row of copies of one sprite along X at one depth, for fences, bays, cars in a lot.
    S.row = function (sprite, o) {
      o = o || {};
      var from = num(o.from, -10), to = num(o.to, 10), step = num(o.step, sprite.w || 2), Z = need(o.Z, "Z");
      var boxes = [];
      for (var X = from; X <= to + 1e-9; X += step) {
        if (o.shadow) S.shadow(sprite, { X: X, Z: Z, ink: o.shadowInk, alpha: o.shadowAlpha, blur: o.shadowBlur, mirror: o.mirror });
        boxes.push(S.sprite(sprite, { X: X, Z: Z, inks: o.inks, tone: o.tone, mirror: o.mirror, fade: o.fade, silhouette: o.silhouette }));
      }
      return boxes;
    };

    // A flat sheet on the ground (a slab, a court, a lot) as a quad from (X-w/2..X+w/2, Z..Z+d).
    S.slab = function (o) {
      o = o || {};
      var X = num(o.X, 0), Z = need(o.Z, "Z"), sw = num(o.w, 4), sd = num(o.d, 4);
      var p = [S.project(X - sw / 2, 0, Z), S.project(X + sw / 2, 0, Z), S.project(X + sw / 2, 0, Z + sd), S.project(X - sw / 2, 0, Z + sd)];
      ctx.save(); ctx.fillStyle = o.fill || "#666";
      ctx.beginPath(); ctx.moveTo(p[0][0], p[0][1]); ctx.lineTo(p[1][0], p[1][1]); ctx.lineTo(p[2][0], p[2][1]); ctx.lineTo(p[3][0], p[3][1]); ctx.closePath(); ctx.fill();
      if (o.edge) { ctx.strokeStyle = o.edge; ctx.lineWidth = num(o.edgePx, 1.2); ctx.stroke(); }
      ctx.restore();
      return p;
    };

    S.mix = mixHex;
    S.lum = lum;
    return S;
  };

  /* ---------------------------------------------------------------- sprite tools */

  // Build a sprite from parts, computing its footprint width and height in metres.
  SCENE.sprite = function (parts, meta) {
    var minx = Infinity, maxx = -Infinity, maxy = -Infinity;
    parts.forEach(function (p) {
      var pts = [];
      if (p.type === "poly") pts = p.pts;
      else if (p.type === "rect") pts = [[p.x, p.y], [p.x + p.w, p.y + p.h]];
      else if (p.type === "ellipse") pts = [[p.cx - p.rx, p.cy - p.ry], [p.cx + p.rx, p.cy + p.ry]];
      else if (p.type === "line") pts = p.pts.map(function (q) { return [q[0], q[1] + (p.width || 0.1) / 2]; }).concat(p.pts.map(function (q) { return [q[0] - (p.width || 0.1) / 2, q[1]]; }), p.pts.map(function (q) { return [q[0] + (p.width || 0.1) / 2, q[1]]; }));
      pts.forEach(function (q) { if (q[0] < minx) minx = q[0]; if (q[0] > maxx) maxx = q[0]; if (q[1] > maxy) maxy = q[1]; });
    });
    var s = { parts: parts, w: maxx - minx, h: maxy, minx: minx, maxx: maxx };
    if (meta) for (var k in meta) s[k] = meta[k];
    return s;
  };

  // Merge sprites side by side or in place (a figure beside a desk, a sign on a pole).
  SCENE.compose = function (list) {
    var parts = [];
    list.forEach(function (it) {
      var sp = it.sprite, dx = it.dx || 0, dy = it.dy || 0, sc = it.scale || 1, mx = it.mirror ? -1 : 1;
      sp.parts.forEach(function (p) {
        var q = JSON.parse(JSON.stringify(p));
        if (q.type === "poly") q.pts = q.pts.map(function (v) { return [v[0] * sc * mx + dx, v[1] * sc + dy]; });
        else if (q.type === "rect") { var x0 = q.x * sc * mx + dx, x1 = (q.x + q.w) * sc * mx + dx; q.x = Math.min(x0, x1); q.w = Math.abs(x1 - x0); q.y = q.y * sc + dy; q.h *= sc; if (q.r) q.r *= sc; }
        else if (q.type === "ellipse") { q.cx = q.cx * sc * mx + dx; q.cy = q.cy * sc + dy; q.rx *= sc; q.ry *= sc; }
        else if (q.type === "line") { q.pts = q.pts.map(function (v) { return [v[0] * sc * mx + dx, v[1] * sc + dy]; }); q.width = (q.width || 0.1) * sc; }
        parts.push(q);
      });
    });
    return SCENE.sprite(parts);
  };

  SCENE.mix = mixHex;
  SCENE.hexToRgb = hexToRgb;
  SCENE.lum = lum;

  global.TXSCENE = SCENE;
})(typeof window !== "undefined" ? window : globalThis);
