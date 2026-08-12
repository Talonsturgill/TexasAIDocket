/* aksdf.js — CPU signed-distance-field raymarcher (no GPU, no deps).
 *
 * Renders organic, sculptural, painterly 3D that triangle meshes are bad at:
 * blended blob forms, carved terrain-like masses, twisted monuments, soft
 * molten shapes. Pure JS per-pixel raymarching into an ImageData, then drawn
 * upscaled onto the slide canvas (the slight softness reads as airbrush/
 * painterly, a feature for editorial art).
 *
 * Quality ladder implemented (the Quilez canon):
 *   - sphere-traced raymarch with early-out
 *   - tetrahedral-gradient normals
 *   - 5-tap ambient occlusion
 *   - soft shadows (cone factor k)
 *   - fresnel rim + two-tone (warm key / cool shadow) ramp
 *   - exponential fog to a sky color
 *
 * PERFORMANCE (measured in this container): ~2-6s at 480x600 internal for a
 * 3-5 primitive scene with shadows+AO. Keep internal res <= 600x750 and scene
 * SDFs cheap (< ~12 primitives). Budget guard: opts.deadlineMs (default 15000)
 * degrades by skipping shadow rays first, then AO, never returns unfinished rows.
 *
 * USAGE (inside renderReady):
 *   <script src="@@ASSETS@@/js/aksdf.js"></script>
 *   const S = TXSDF;
 *   const scene = (p) => {                    // return [signedDistance, materialId]
 *     const a = S.sdSphere(S.sub(p,[0,1,0]), 1.0);
 *     const b = S.sdBox(S.sub(p,[1.2,0.5,0]), [0.6,0.5,0.6]);
 *     return [S.smin(a, b, 0.5), 1];
 *   };
 *   TXSDF.render(canvas2dCtx, {
 *     scene, width: 540, height: 675,         // internal res; drawn to fit canvas box
 *     box: [0,0,1080,1350],                   // destination rect on the slide canvas
 *     cam: { pos:[3.5,2.5,5], look:[0,0.8,0], fov: 50 },
 *     light: [0.5,0.8,0.3],
 *     mats: { 1: { color:[1.0,0.78,0.17], spec: 0.4 } },
 *     sky: [0.02,0.04,0.08], fog: 0.06,
 *     keyColor: [1.0,0.93,0.8], shadowColor: [0.16,0.22,0.34],  // two-tone ramp
 *     seed: 20260711
 *   });
 *
 * Deterministic. Text never goes here (DOM/SVG only). Mark the region busy if
 * type must sit on it (plate rules apply as with any art).
 */
(function (global) {
  "use strict";
  const S = {};

  /* ---------- vec3 helpers (arrays, allocation-light) ---------- */
  S.sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  S.add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
  S.mul = (a, s) => [a[0] * s, a[1] * s, a[2] * s];
  S.dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  S.len = (a) => Math.hypot(a[0], a[1], a[2]);
  S.norm = (a) => { const l = S.len(a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
  S.cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  S.mix = (a, b, t) => a + (b - a) * t;
  S.mix3 = (a, b, t) => [S.mix(a[0], b[0], t), S.mix(a[1], b[1], t), S.mix(a[2], b[2], t)];
  S.clamp = (x, a, b) => x < a ? a : (x > b ? b : x);

  /* ---------- SDF primitives ---------- */
  S.sdSphere = (p, r) => S.len(p) - r;
  S.sdBox = (p, b) => {
    const qx = Math.abs(p[0]) - b[0], qy = Math.abs(p[1]) - b[1], qz = Math.abs(p[2]) - b[2];
    const ox = Math.max(qx, 0), oy = Math.max(qy, 0), oz = Math.max(qz, 0);
    return Math.hypot(ox, oy, oz) + Math.min(Math.max(qx, Math.max(qy, qz)), 0);
  };
  S.sdRoundBox = (p, b, r) => S.sdBox(p, b) - r;
  S.sdTorus = (p, R, r) => Math.hypot(Math.hypot(p[0], p[2]) - R, p[1]) - r;
  S.sdCapsule = (p, a, b, r) => {
    const pa = S.sub(p, a), ba = S.sub(b, a);
    const h = S.clamp(S.dot(pa, ba) / S.dot(ba, ba), 0, 1);
    return S.len(S.sub(pa, S.mul(ba, h))) - r;
  };
  S.sdCylinder = (p, h, r) => {
    const dx = Math.hypot(p[0], p[2]) - r, dy = Math.abs(p[1]) - h;
    return Math.min(Math.max(dx, dy), 0) + Math.hypot(Math.max(dx, 0), Math.max(dy, 0));
  };
  S.sdCone = (p, angle, h) => { // apex at origin, opening down y
    const q = Math.hypot(p[0], p[2]);
    return Math.max(S.dot([q, p[1]], [Math.cos(angle), Math.sin(angle)]), -h - p[1]);
  };
  S.sdPlane = (p, n, d) => S.dot(p, n) + d;

  /* ---------- operators ---------- */
  S.opUnion = Math.min;
  S.opSub = (a, b) => Math.max(a, -b);
  S.opInter = Math.max;
  S.smin = (a, b, k) => { // polynomial smooth min — the organic blend
    const h = S.clamp(0.5 + 0.5 * (b - a) / k, 0, 1);
    return S.mix(b, a, h) - k * h * (1 - h);
  };
  S.smax = (a, b, k) => -S.smin(-a, -b, k);
  S.opTwist = (p, k) => { // twist around y
    const c = Math.cos(k * p[1]), s = Math.sin(k * p[1]);
    return [c * p[0] - s * p[2], p[1], s * p[0] + c * p[2]];
  };
  S.opRepXZ = (p, sx, sz) => [
    ((p[0] % sx) + sx * 1.5) % sx - sx / 2, p[1],
    ((p[2] % sz) + sz * 1.5) % sz - sz / 2];

  /* ---------- cheap deterministic 3D value noise + fbm (self-contained) ---------- */
  let SEED = 11;
  S.reseed = (s) => { SEED = s >>> 0 || 11; };
  function hash3(x, y, z) {
    let h = (x | 0) * 374761393 + (y | 0) * 668265263 + (z | 0) * 2147483647 + SEED * 144665;
    h = (h ^ (h >>> 13)) * 1274126177;
    return (((h ^ (h >>> 16)) >>> 0) % 100000) / 100000;
  }
  S.noise3 = function (x, y, z) {
    const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
    const xf = x - xi, yf = y - yi, zf = z - zi;
    const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf), w = zf * zf * (3 - 2 * zf);
    function n(i, j, k) { return hash3(xi + i, yi + j, zi + k); }
    return S.mix(
      S.mix(S.mix(n(0, 0, 0), n(1, 0, 0), u), S.mix(n(0, 1, 0), n(1, 1, 0), u), v),
      S.mix(S.mix(n(0, 0, 1), n(1, 0, 1), u), S.mix(n(0, 1, 1), n(1, 1, 1), u), v), w) * 2 - 1;
  };
  S.fbm3 = function (x, y, z, oct) {
    let a = 0.5, f = 1, sum = 0;
    for (let i = 0; i < (oct || 4); i++) { sum += a * S.noise3(x * f, y * f, z * f); f *= 2.02; a *= 0.5; }
    return sum;
  };

  /* ---------- the renderer ---------- */
  S.render = function (ctx, opts) {
    const W = opts.width || 540, H = opts.height || 675;
    const box = opts.box || [0, 0, ctx.canvas.width / 2, ctx.canvas.height / 2];
    const scene = opts.scene;
    const MAXD = opts.maxDist || 40, MAXSTEPS = opts.maxSteps || 110, EPS = opts.eps || 0.0012;
    const deadline = performance.now() + (opts.deadlineMs || 15000);
    let doShadow = opts.shadows !== false, doAO = opts.ao !== false;

    // camera basis
    const cam = opts.cam || {};
    const ro = cam.pos || [3.5, 2.5, 5];
    const look = cam.look || [0, 0.8, 0];
    const fov = (cam.fov || 50) * Math.PI / 180;
    const fw = S.norm(S.sub(look, ro));
    const fr = S.norm(S.cross(fw, [0, 1, 0]));
    const fu = S.cross(fr, fw);
    const fl = 1 / Math.tan(fov / 2);

    const L = S.norm(opts.light || [0.5, 0.8, 0.3]);
    const sky = opts.sky || [0.02, 0.04, 0.08];
    const fogK = opts.fog != null ? opts.fog : 0.05;
    const keyC = opts.keyColor || [1.0, 0.93, 0.8];
    const shC = opts.shadowColor || [0.16, 0.22, 0.34];
    const mats = opts.mats || { 1: { color: [0.8, 0.8, 0.8], spec: 0.3 } };

    function map(p) { return scene(p); }
    function normal(p) { // tetrahedral gradient
      const e = 0.0015;
      const k1 = [1, -1, -1], k2 = [-1, -1, 1], k3 = [-1, 1, -1], k4 = [1, 1, 1];
      let n = [0, 0, 0];
      for (const k of [k1, k2, k3, k4]) {
        const d = map([p[0] + k[0] * e, p[1] + k[1] * e, p[2] + k[2] * e])[0];
        n = S.add(n, S.mul(k, d));
      }
      return S.norm(n);
    }
    function softShadow(p, l) {
      let res = 1.0, t = 0.03;
      for (let i = 0; i < 40 && t < 12; i++) {
        const h = map([p[0] + l[0] * t, p[1] + l[1] * t, p[2] + l[2] * t])[0];
        if (h < 0.001) return 0.0;
        res = Math.min(res, 14 * h / t);
        t += S.clamp(h, 0.02, 0.4);
      }
      return S.clamp(res, 0, 1);
    }
    function ao(p, n) {
      let occ = 0, sca = 1;
      for (let i = 1; i <= 5; i++) {
        const hr = 0.025 + 0.14 * i;
        const d = map([p[0] + n[0] * hr, p[1] + n[1] * hr, p[2] + n[2] * hr])[0];
        occ += (hr - d) * sca; sca *= 0.72;
      }
      return S.clamp(1 - 1.7 * occ, 0, 1);
    }

    const img = ctx.createImageData(W, H);
    const data = img.data;
    for (let y = 0; y < H; y++) {
      if (performance.now() > deadline) {          // degrade, never abort a frame
        if (doShadow) { doShadow = false; }
        else if (doAO) { doAO = false; }
      }
      const sy = (1 - 2 * (y + 0.5) / H) * (H / W); // keep square pixels
      for (let x = 0; x < W; x++) {
        const sx = 2 * (x + 0.5) / W - 1;
        const rd = S.norm([
          fr[0] * sx + fu[0] * sy + fw[0] * fl,
          fr[1] * sx + fu[1] * sy + fw[1] * fl,
          fr[2] * sx + fu[2] * sy + fw[2] * fl]);
        // march
        let t = 0, hit = -1, d = 0;
        for (let i = 0; i < MAXSTEPS; i++) {
          const p = [ro[0] + rd[0] * t, ro[1] + rd[1] * t, ro[2] + rd[2] * t];
          const r = map(p); d = r[0];
          if (d < EPS * t + EPS) { hit = r[1]; break; }
          t += d;
          if (t > MAXD) break;
        }
        let col;
        if (hit < 0) {
          // sky with subtle vertical ramp
          const g = S.clamp(0.5 - rd[1] * 0.8, 0, 1);
          col = [sky[0] * (0.7 + g), sky[1] * (0.7 + g), sky[2] * (0.7 + g)];
        } else {
          const p = [ro[0] + rd[0] * t, ro[1] + rd[1] * t, ro[2] + rd[2] * t];
          const n = normal(p);
          const m = mats[hit] || mats[1] || { color: [0.8, 0.8, 0.8], spec: 0.3 };
          const dif = S.clamp(S.dot(n, L), 0, 1);
          const sh = doShadow ? softShadow(S.add(p, S.mul(n, 0.02)), L) : 1.0;
          const occ = doAO ? ao(p, n) : 1.0;
          const hemi = S.clamp(0.5 + 0.5 * n[1], 0, 1);      // sky bounce
          // fresnel rim
          const fre = Math.pow(S.clamp(1 + S.dot(rd, n), 0, 1), 3);
          // two-tone: lit zones toward keyColor, unlit toward shadowColor
          const lit = dif * sh;
          const ramp = S.mix3(shC, keyC, S.clamp(lit, 0, 1));
          // sun term modulated by the shadow ray ONLY; AO belongs to sky/indirect
          // (Quilez outdoor-lighting rule: never double-darken the key).
          const indirect = 0.25 * occ;
          col = [
            m.color[0] * ramp[0] * (indirect + 0.9 * lit),
            m.color[1] * ramp[1] * (indirect + 0.9 * lit),
            m.color[2] * ramp[2] * (indirect + 0.9 * lit)];
          // hemispheric fill
          col = S.add(col, S.mul([sky[0] * 2.2, sky[1] * 2.4, sky[2] * 2.8], 0.35 * hemi * occ * (m.color[0] + m.color[1] + m.color[2]) / 3));
          // specular
          const hv = S.norm(S.sub(L, rd));
          const spe = Math.pow(S.clamp(S.dot(n, hv), 0, 1), 34) * (m.spec != null ? m.spec : 0.3) * sh;
          col = S.add(col, S.mul(keyC, spe));
          // rim
          col = S.add(col, S.mul([0.35, 0.55, 0.75], fre * 0.35 * occ));
          if (m.emissive) col = S.add(col, S.mul(m.emissive, 1));
          // fog
          const fga = 1 - Math.exp(-fogK * fogK * t * t);
          col = S.mix3(col, sky, S.clamp(fga, 0, 1));
        }
        // filmic-ish curve + gamma
        const o = (y * W + x) * 4;
        for (let c = 0; c < 3; c++) {
          let v = col[c];
          v = (v * (2.51 * v + 0.03)) / (v * (2.43 * v + 0.59) + 0.14);  // ACES approx
          data[o + c] = 255 * Math.pow(S.clamp(v, 0, 1), 1 / 2.2);
        }
        data[o + 3] = 255;
      }
    }
    // upscale into the destination box with smoothing (painterly)
    const tmp = document.createElement('canvas');
    tmp.width = W; tmp.height = H;
    tmp.getContext('2d').putImageData(img, 0, 0);
    ctx.save();
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(tmp, box[0], box[1], box[2], box[3]);
    ctx.restore();
    return { internal: [W, H], shadows: doShadow, ao: doAO };
  };

  global.TXSDF = S;
})(typeof window !== "undefined" ? window : globalThis);
