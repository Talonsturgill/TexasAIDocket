/* txbench.js — multi-material digital bas-relief, lit by one raking key. (Texas AI Docket, adapted October 16th, 2026)
 *
 * txrelief.js shades ONE material with ONE ramp and no specular and no cast, which is right for a substrate and
 * wrong for a still life of several materials on one bench: wood, ivory, ebony and nickel each need their own
 * albedo and their own sheen, and a raised object needs to throw a shadow on the surface it stands on. This is
 * the bench for that. Plan view, height in CSS px out of the table.
 *
 *   TXBENCH.relief(cx, {x, y, w, h, scale: 2,
 *     height: (X, Y) => px,            // CSS-px coordinates on the page, height in CSS px
 *     material: (X, Y) => id,          // integer material id
 *     albedo: (X, Y, id) => [r, g, b], // linear 0..1, may vary (grain)
 *     spec: {id: [strength, shininess]},
 *     light: {azDeg, elDeg},           // azimuth 0 = toward the top of the frame, clockwise
 *     ambient: 0.22, diffuse: 0.95, ao: 0.9, shadow: 0.85, softness: 10});
 *
 *   Optional window light (No.87, 2026-10-15): keyMask: (X, Y) => 0..1 gates the key (a sun pane through a
 *   window; outside it only the ambient sky reaches the surface), keyColor: [r, g, b] tints the key and its
 *   specular, ambColor: [r, g, b] tints the ambient. All three default to the old behaviour (1, white, white).
 *   dither: true adds half an 8-bit step of per-pixel offset before quantising (off by default).
 *
 * Height is evaluated once per device pixel into a buffer. Normals are a Sobel of that buffer. Cavity occlusion
 * compares each height with a box-blurred copy. The cast is a march from each pixel toward the key across the
 * buffer, with a penumbra from the closest miss. Everything is deterministic. Text never goes here.
 */
(function (global) {
  "use strict";
  global.TXBENCH = {relief: relief};
  // Source: Talonsturgill/alaskaaicarousels, 03da46445a18974351cc6e74835679b3de2c89c8,
  // assets/js/akbench.js. Only the renderer is shared; no stories or ledger state are imported.
  function boxBlur(src, W, H, r) {
    const tmp = new Float32Array(W * H), out = new Float32Array(W * H);
    for (let y = 0; y < H; y++) { let s = 0; const o = y * W;
      for (let x = -r; x <= r; x++) s += src[o + Math.max(0, Math.min(W - 1, x))];
      for (let x = 0; x < W; x++) { tmp[o + x] = s / (2 * r + 1); s += src[o + Math.min(W - 1, x + r + 1)] - src[o + Math.max(0, x - r)]; } }
    for (let x = 0; x < W; x++) { let s = 0;
      for (let y = -r; y <= r; y++) s += tmp[Math.max(0, Math.min(H - 1, y)) * W + x];
      for (let y = 0; y < H; y++) { out[y * W + x] = s / (2 * r + 1); s += tmp[Math.min(H - 1, y + r + 1) * W + x] - tmp[Math.max(0, y - r) * W + x]; } }
    return out;
  }
  function relief(cx, o) {
    if (!cx || !cx.canvas || !o || !(o.w > 0 && o.h > 0)) throw new Error("TXBENCH needs a canvas and positive bounds");
    for (const k of ["height", "material", "albedo"]) if (typeof o[k] !== "function") throw new Error("TXBENCH needs " + k);
    const deck = global.TXDECK && global.TXDECK.deck();
    if (deck) {
      const light = {azDeg: deck.light.az, elDeg: deck.light.el};
      if (o.light && (o.light.azDeg !== light.azDeg || o.light.elDeg !== light.elDeg)) throw new Error("TXBENCH light differs from the chassis");
      o = Object.assign({}, o, {light});
    }
    const started = global.performance ? performance.now() : 0;
    const sc = o.scale || 2, X0 = Math.round(o.x * sc), Y0 = Math.round(o.y * sc), W = Math.round(o.w * sc), H = Math.round(o.h * sc);
    const hb = new Float32Array(W * H), mb = new Uint8Array(W * H);
    const materials = new Set(); let hMin = Infinity, casts = 0;
    for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
      const X = (X0 + i + 0.5) / sc, Y = (Y0 + j + 0.5) / sc;
      const height = o.height(X, Y), material = o.material(X, Y);
      if (!Number.isFinite(height) || !Number.isInteger(material) || material < 0 || material > 255) throw new Error("TXBENCH invalid height or material");
      hb[j * W + i] = height * sc; mb[j * W + i] = material;
      hMin = Math.min(hMin, height * sc); materials.add(material);
    }
    const az = (o.light && o.light.azDeg != null ? o.light.azDeg : 135) * Math.PI / 180, el = (o.light && o.light.elDeg != null ? o.light.elDeg : 26) * Math.PI / 180;
    const L = [Math.sin(az) * Math.cos(el), -Math.cos(az) * Math.cos(el), Math.sin(el)];   // screen x right, y down, z up
    const Hv = (() => { const h = [L[0], L[1], L[2] + 1], l = Math.hypot(h[0], h[1], h[2]); return [h[0] / l, h[1] / l, h[2] / l]; })();
    const blur = boxBlur(hb, W, H, Math.round((o.aoRadius || 7) * sc));
    const amb = o.ambient != null ? o.ambient : 0.22, dif = o.diffuse != null ? o.diffuse : 0.95, aoK = o.ao != null ? o.ao : 0.9, shK = o.shadow != null ? o.shadow : 0.85;
    const soft = (o.softness || 10) * sc, tanEl = Math.tan(el), stepLen = 1.5, maxLen = (o.castLength || 140) * sc;
    const lx = L[0] / Math.hypot(L[0], L[1]), ly = L[1] / Math.hypot(L[0], L[1]);
    let hMax = -Infinity; for (let q = 0; q < hb.length; q++) if (hb[q] > hMax) hMax = hb[q];   // a ray above every height can't be occluded
    const img = cx.createImageData(W, H), d = img.data, spec = o.spec || {};
    const dith = !!o.dither, keyMask = typeof o.keyMask === "function" ? o.keyMask : null, kC = o.keyColor || [1, 1, 1], aC = o.ambColor || [1, 1, 1];
    const at = (i, j) => hb[Math.max(0, Math.min(H - 1, j)) * W + Math.max(0, Math.min(W - 1, i))];
    // the cast: march toward the key; the penumbra is the closest miss over distance
    function march(i, j, h0) {
      let vis = 1;
      for (let t = stepLen; t < maxLen; t += stepLen * (1 + t / 120)) {
        const ray = h0 + t * tanEl; if (ray - hMax > soft * (0.15 + t / maxLen)) break;   // exact: past here every term is >= 1
        const hh = at(Math.round(i + lx * t), Math.round(j + ly * t));
        // Equal-height carrier pixels do not occlude one another.
        if (hh <= h0) continue;
        const over = hh - ray; if (over > 0) { vis = 0; break; }
        vis = Math.min(vis, -over / (soft * (0.15 + t / maxLen)) );
      }
      return Math.max(0, Math.min(1, vis));
    }
    // visBlur: n device px of box blur on the shadow term alone (No.87): a crinkled or scored top makes near-miss
    // rays that speckle the penumbra; the cast is soft by nature, the surface relief is not, so only the cast is blurred
    let visBuf = null;
    if (o.visBlur) { visBuf = new Float32Array(W * H); for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) visBuf[j * W + i] = march(i, j, hb[j * W + i]); visBuf = boxBlur(visBuf, W, H, o.visBlur); }
    for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
      const k = j * W + i, h0 = hb[k];
      const gx = (at(i + 1, j - 1) + 2 * at(i + 1, j) + at(i + 1, j + 1) - at(i - 1, j - 1) - 2 * at(i - 1, j) - at(i - 1, j + 1)) / 8;
      const gy = (at(i - 1, j + 1) + 2 * at(i, j + 1) + at(i + 1, j + 1) - at(i - 1, j - 1) - 2 * at(i, j - 1) - at(i + 1, j - 1)) / 8;
      let nx = -gx, ny = -gy, nz = 1; const nl = Math.hypot(nx, ny, nz); nx /= nl; ny /= nl; nz /= nl;
      const lam = Math.max(0, nx * L[0] + ny * L[1] + nz * L[2]);
      const vis = visBuf && !(o.visSharp && o.visSharp.indexOf(mb[k]) >= 0) ? visBuf[k] : march(i, j, h0);   // visSharp: materials whose own cast stays crisp (a measured scale's grooves)
      const cav = Math.max(0, blur[k] - h0) / sc, ao = Math.max(0, 1 - aoK * Math.min(1, cav / 6));
      const m = mb[k], X = (X0 + i + 0.5) / sc, Y = (Y0 + j + 0.5) / sc, a = o.albedo(X, Y, m);
      const sh = 1 - shK * (1 - vis), km = keyMask ? keyMask(X, Y) : 1;
      // Count lost key light on the actual material, not geometric occlusion in an unlit region.
      const keyEffect = km * dif * lam * Math.max(a[0] * kC[0], a[1] * kC[1], a[2] * kC[2]);
      if (vis < 0.9 && (1 - sh) * keyEffect >= 0.003) casts++;
      const sp = spec[m] ? km * spec[m][0] * Math.pow(Math.max(0, nx * Hv[0] + ny * Hv[1] + nz * Hv[2]), spec[m][1]) * sh : 0;
      const ka = amb * ao, kd = dif * lam * sh * km;
      const dz = dith ? (((Math.imul(k, 2654435761) >>> 0) % 997) / 997 - 0.5) : 0;   // half an 8-bit step of per-pixel offset, so a slow gradient can't quantise into contour rings
      for (let c = 0; c < 3; c++) { let v = a[c] * (ka * aC[c] + kd * kC[c]) + sp * kC[c]; v = v / (1 + v * 0.35); d[k * 4 + c] = 255 * Math.pow(Math.max(0, Math.min(1, v)), 1 / 2.2) + dz; }
      d[k * 4 + 3] = 255;
    }
    cx.save(); cx.setTransform(1, 0, 0, 1, 0, 0); cx.putImageData(img, X0, Y0); cx.restore();
    global.TXT_TONEMAPPED = true;
    const proof = {height_range: (hMax - hMin) / sc, materials: materials.size,
      cast_fraction: casts / (W * H), area: W * H / (cx.canvas.width * cx.canvas.height),
      render_ms: global.performance ? performance.now() - started : null};
    // The render report retains this measurement, just as it retains TXT.snapshot's verdict.
    console.error("TXBENCH: RELIEF " + JSON.stringify(proof));
    return {x: X0, y: Y0, w: W, h: H};
  }
})(typeof window !== "undefined" ? window : globalThis);
