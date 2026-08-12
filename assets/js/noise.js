/* noise.js — seeded simplex noise (2D/3D) + fBm + seeded PRNG.
 * Self-contained, no network, deterministic per seed. Classic Gustavson/Peters
 * simplex port (public domain) with a mulberry32-shuffled permutation table.
 *
 * Usage in slide HTML:
 *   <script src="../assets/js/noise.js"></script>
 *   const R = TX.rng(42);            // seeded PRNG in [0,1)
 *   const n = TX.simplex2(x, y);     // [-1, 1]
 *   const f = TX.fbm2(x, y, {octaves: 5, lacunarity: 2, gain: 0.5});
 *   TX.reseed(1337);                 // reshuffle the permutation table
 */
(function (global) {
  "use strict";

  function mulberry32(seed) {
    let a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  const grad3 = [
    [1,1,0],[-1,1,0],[1,-1,0],[-1,-1,0],
    [1,0,1],[-1,0,1],[1,0,-1],[-1,0,-1],
    [0,1,1],[0,-1,1],[0,1,-1],[0,-1,-1]
  ];

  let perm = new Uint8Array(512);
  let permMod12 = new Uint8Array(512);

  function reseed(seed) {
    const rand = mulberry32(seed === undefined ? 11 : seed);
    const p = new Uint8Array(256);
    for (let i = 0; i < 256; i++) p[i] = i;
    for (let i = 255; i > 0; i--) {
      const j = Math.floor(rand() * (i + 1));
      const t = p[i]; p[i] = p[j]; p[j] = t;
    }
    for (let i = 0; i < 512; i++) {
      perm[i] = p[i & 255];
      permMod12[i] = perm[i] % 12;
    }
  }
  reseed(11);

  const F2 = 0.5 * (Math.sqrt(3) - 1);
  const G2 = (3 - Math.sqrt(3)) / 6;
  const F3 = 1 / 3;
  const G3 = 1 / 6;

  function dot2(g, x, y) { return g[0] * x + g[1] * y; }
  function dot3(g, x, y, z) { return g[0] * x + g[1] * y + g[2] * z; }

  function simplex2(xin, yin) {
    let n0 = 0, n1 = 0, n2 = 0;
    const s = (xin + yin) * F2;
    const i = Math.floor(xin + s);
    const j = Math.floor(yin + s);
    const t = (i + j) * G2;
    const x0 = xin - (i - t);
    const y0 = yin - (j - t);
    let i1, j1;
    if (x0 > y0) { i1 = 1; j1 = 0; } else { i1 = 0; j1 = 1; }
    const x1 = x0 - i1 + G2, y1 = y0 - j1 + G2;
    const x2 = x0 - 1 + 2 * G2, y2 = y0 - 1 + 2 * G2;
    const ii = i & 255, jj = j & 255;
    let t0 = 0.5 - x0 * x0 - y0 * y0;
    if (t0 >= 0) {
      t0 *= t0;
      n0 = t0 * t0 * dot2(grad3[permMod12[ii + perm[jj]]], x0, y0);
    }
    let t1 = 0.5 - x1 * x1 - y1 * y1;
    if (t1 >= 0) {
      t1 *= t1;
      n1 = t1 * t1 * dot2(grad3[permMod12[ii + i1 + perm[jj + j1]]], x1, y1);
    }
    let t2 = 0.5 - x2 * x2 - y2 * y2;
    if (t2 >= 0) {
      t2 *= t2;
      n2 = t2 * t2 * dot2(grad3[permMod12[ii + 1 + perm[jj + 1]]], x2, y2);
    }
    return 70 * (n0 + n1 + n2);
  }

  function simplex3(xin, yin, zin) {
    let n0, n1, n2, n3;
    const s = (xin + yin + zin) * F3;
    const i = Math.floor(xin + s), j = Math.floor(yin + s), k = Math.floor(zin + s);
    const t = (i + j + k) * G3;
    const x0 = xin - (i - t), y0 = yin - (j - t), z0 = zin - (k - t);
    let i1, j1, k1, i2, j2, k2;
    if (x0 >= y0) {
      if (y0 >= z0)      { i1 = 1; j1 = 0; k1 = 0; i2 = 1; j2 = 1; k2 = 0; }
      else if (x0 >= z0) { i1 = 1; j1 = 0; k1 = 0; i2 = 1; j2 = 0; k2 = 1; }
      else               { i1 = 0; j1 = 0; k1 = 1; i2 = 1; j2 = 0; k2 = 1; }
    } else {
      if (y0 < z0)       { i1 = 0; j1 = 0; k1 = 1; i2 = 0; j2 = 1; k2 = 1; }
      else if (x0 < z0)  { i1 = 0; j1 = 1; k1 = 0; i2 = 0; j2 = 1; k2 = 1; }
      else               { i1 = 0; j1 = 1; k1 = 0; i2 = 1; j2 = 1; k2 = 0; }
    }
    const x1 = x0 - i1 + G3, y1 = y0 - j1 + G3, z1 = z0 - k1 + G3;
    const x2 = x0 - i2 + 2 * G3, y2 = y0 - j2 + 2 * G3, z2 = z0 - k2 + 2 * G3;
    const x3 = x0 - 1 + 3 * G3, y3 = y0 - 1 + 3 * G3, z3 = z0 - 1 + 3 * G3;
    const ii = i & 255, jj = j & 255, kk = k & 255;
    let t0 = 0.6 - x0 * x0 - y0 * y0 - z0 * z0;
    if (t0 < 0) n0 = 0; else { t0 *= t0; n0 = t0 * t0 * dot3(grad3[permMod12[ii + perm[jj + perm[kk]]]], x0, y0, z0); }
    let t1 = 0.6 - x1 * x1 - y1 * y1 - z1 * z1;
    if (t1 < 0) n1 = 0; else { t1 *= t1; n1 = t1 * t1 * dot3(grad3[permMod12[ii + i1 + perm[jj + j1 + perm[kk + k1]]]], x1, y1, z1); }
    let t2 = 0.6 - x2 * x2 - y2 * y2 - z2 * z2;
    if (t2 < 0) n2 = 0; else { t2 *= t2; n2 = t2 * t2 * dot3(grad3[permMod12[ii + i2 + perm[jj + j2 + perm[kk + k2]]]], x2, y2, z2); }
    let t3 = 0.6 - x3 * x3 - y3 * y3 - z3 * z3;
    if (t3 < 0) n3 = 0; else { t3 *= t3; n3 = t3 * t3 * dot3(grad3[permMod12[ii + 1 + perm[jj + 1 + perm[kk + 1]]]], x3, y3, z3); }
    return 32 * (n0 + n1 + n2 + n3);
  }

  function fbm2(x, y, opts) {
    const o = opts || {};
    const octaves = o.octaves || 4;
    const lac = o.lacunarity || 2;
    const gain = o.gain || 0.5;
    let amp = 1, freq = 1, sum = 0, norm = 0;
    for (let i = 0; i < octaves; i++) {
      sum += amp * simplex2(x * freq, y * freq);
      norm += amp;
      amp *= gain; freq *= lac;
    }
    return sum / norm;
  }

  function fbm3(x, y, z, opts) {
    const o = opts || {};
    const octaves = o.octaves || 4;
    const lac = o.lacunarity || 2;
    const gain = o.gain || 0.5;
    let amp = 1, freq = 1, sum = 0, norm = 0;
    for (let i = 0; i < octaves; i++) {
      sum += amp * simplex3(x * freq, y * freq, z * freq);
      norm += amp;
      amp *= gain; freq *= lac;
    }
    return sum / norm;
  }

  // Domain warp: classic Inigo Quilez pattern for organic marbling.
  function warp2(x, y, strength, opts) {
    const s = strength === undefined ? 1 : strength;
    const qx = fbm2(x + 0.0, y + 0.0, opts);
    const qy = fbm2(x + 5.2, y + 1.3, opts);
    return fbm2(x + s * qx, y + s * qy, opts);
  }

  /* grainTile: data-URL of a small tileable monochrome grain square.
   * Use as a repeating CSS background for film grain — NEVER a full-frame
   * feTurbulence rect (the printed PDF embeds full-frame noise as a 10-40MB
   * incompressible bitmap; a repeated tile embeds once).
   *   const url = TX.grainTile(280, 46, 1);   // size px, strength 0-127, seed
   *   grainEl.style.backgroundImage = `url(${url})`;
   * Pair with: background-repeat: repeat; mix-blend-mode: overlay; opacity .05-.12
   */
  function grainTile(size, strength, seed) {
    const s = size || 280, k = strength === undefined ? 46 : strength;
    const rand = mulberry32(seed === undefined ? 1 : seed);
    const cv = (typeof document !== "undefined") ? document.createElement("canvas") : null;
    if (!cv) return null;
    cv.width = s; cv.height = s;
    const cx = cv.getContext("2d");
    const img = cx.createImageData(s, s);
    for (let i = 0; i < img.data.length; i += 4) {
      const v = 128 + (rand() - 0.5) * 2 * k;
      img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
      img.data[i + 3] = 255;
    }
    cx.putImageData(img, 0, 0);
    return cv.toDataURL("image/png");
  }

  global.TX = {
    rng: mulberry32,
    reseed: reseed,
    simplex2: simplex2,
    simplex3: simplex3,
    fbm2: fbm2,
    fbm3: fbm3,
    warp2: warp2,
    grainTile: grainTile
  };
})(typeof window !== "undefined" ? window : globalThis);
