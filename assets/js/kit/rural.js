/* kit/rural.js, see assets/js/txkit.js for the conventions.
 *
 * The working country: cattle (a Texas longhorn or a Hereford, modelled as one smooth body from a
 * signed distance field so it has real anatomy and no seams), the Aermotor windmill that waters
 * them, the galvanized stock tank it fills, a barn, round hay bales, a wrapped cotton module, a
 * grain bin, a pipe-rail gate and a cattle guard. Metres, y up, base on y = 0, front faces +z.
 */
export function install(K, THREE, TXT) {
  const TAU = Math.PI * 2;
  const V3 = THREE.Vector3;

  /* ---- local materials and textures ------------------------------------------------------ */
  const MATS = new Map();
  function mat(key, params, physical) {
    if (MATS.has(key)) return MATS.get(key);
    const P = Object.assign({ roughness: 0.8, metalness: 0 }, params || {});
    const m = physical ? new THREE.MeshPhysicalMaterial(P) : new THREE.MeshStandardMaterial(P);
    MATS.set(key, m); return m;
  }
  const TEX = new Map();
  function ltex(key, paint, opts, size, linear) {
    const k = key + '|' + JSON.stringify(opts || {});
    if (TEX.has(k)) return TEX.get(k);
    const W = (size && size[0]) || 512, H = (size && size[1]) || W;
    const c = document.createElement('canvas'); c.width = W; c.height = H;
    paint(c.getContext('2d'), W, H, K.rng(57 + key.length * 13 + ((opts && opts.seed) || 0) * 101), opts || {});
    const t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8;
    if (!linear) t.colorSpace = THREE.SRGBColorSpace;
    TEX.set(k, t); return t;
  }
  const rgb = (c, k) => { const q = new THREE.Color(c); k = k == null ? 1 : k;
    return 'rgb(' + [q.r, q.g, q.b].map((v) => Math.max(0, Math.min(255, Math.round(v * 255 * k)))).join(',') + ')'; };

  // Hot dip galvanized: spangle crystals, a little white rust, streaks.
  function paintSpangle(x, W, H, r, o) {
    x.fillStyle = o.base || '#a9adb0'; x.fillRect(0, 0, W, H);
    for (let i = 0; i < 260; i++) {
      const cx = r() * W, cy = r() * H, rr = 8 + r() * 30, k = 0.95 + r() * 0.1;
      x.fillStyle = rgb(o.base || '#a9adb0', k);
      x.beginPath(); const n = 5 + Math.floor(r() * 4);
      for (let j = 0; j < n; j++) { const a = j / n * TAU + r() * 0.5, q = rr * (0.6 + r() * 0.5); x.lineTo(cx + Math.cos(a) * q, cy + Math.sin(a) * q); }
      x.closePath(); x.fill();
    }
    if (o.streaks) for (let i = 0; i < 40; i++) {
      const sx = r() * W, len = H * (0.1 + r() * 0.5), g = x.createLinearGradient(0, H - len, 0, H);
      g.addColorStop(0, 'rgba(90,70,50,0)'); g.addColorStop(1, 'rgba(90,70,50,' + (0.04 + r() * 0.07) + ')');
      x.fillStyle = g; x.fillRect(sx, H - len, 2 + r() * 6, len);
    }
    for (let i = 0; i < 30; i++) { x.fillStyle = 'rgba(235,235,225,' + (0.03 + r() * 0.05) + ')'; x.beginPath(); x.arc(r() * W, r() * H, 3 + r() * 16, 0, TAU); x.fill(); }
  }
  function paintNoise(x, W, H, r, o) {
    x.fillStyle = o.base || '#808080'; x.fillRect(0, 0, W, H);
    const im = x.getImageData(0, 0, W, H), d = im.data;
    for (let i = 0; i < d.length; i += 4) { const k = 1 + (r() - 0.5) * 2 * (o.amp || 0.1); d[i] *= k; d[i + 1] *= k; d[i + 2] *= k; }
    x.putImageData(im, 0, 0);
  }

  const M = {
    galv: () => mat('galvSpangle', { color: 0xffffff, metalness: 0.8, roughness: 0.4, map: ltex('spangle', paintSpangle, {}) }),
    galvDull: () => mat('galvDull', { color: 0xffffff, metalness: 0.7, roughness: 0.55, map: ltex('spangle', paintSpangle, { base: '#9ea2a4', streaks: true }) }),
    pipe: () => mat('rustyPipe', { color: 0x5b4636, metalness: 0.55, roughness: 0.7 }),
    paint: (c) => mat('paintSteel' + c, { color: c, metalness: 0.3, roughness: 0.5 }),
    conc: () => mat('concR', { color: 0xffffff, roughness: 0.92, map: K.tex('concrete') }),
    wood: (c) => mat('woodR' + c, { color: 0xffffff, roughness: 0.85, map: K.tex('wood', { color: c || '#8a6a4a' }) }),
    black: () => mat('blackR', { color: 0x161617, roughness: 0.7 }),
  };

  /* ---- geometry helpers ------------------------------------------------------------------ */
  function box(w, h, d, material, x, y0, z, parent, uvMetres) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), material);
    if (uvMetres) K.uvBox(m.geometry, uvMetres);
    m.position.set(x || 0, (y0 || 0) + h / 2, z || 0);
    if (parent) parent.add(m); return m;
  }
  function rbox(w, h, d, r, material, x, y0, z, parent, seg, uvMetres) {
    const m = TXT.roundedBox(w, h, d, r, material, { segments: seg || 2 });
    if (uvMetres) K.uvBox(m.geometry, uvMetres);
    m.position.set(x || 0, (y0 || 0) + h / 2, z || 0);
    if (parent) parent.add(m); return m;
  }
  function cyl(rt, rb, h, material, x, y0, z, seg, parent) { return K.cyl(rt, rb, h, material, x, y0, z, seg || 20, parent); }
  function bar(a, b, r, material, parent, seg) { return K.bar(a, b, r, material, seg || 8, parent); }
  function tube(pts, r, material, seg, radial, parent) {
    const m = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts.map((p) => new V3(p[0], p[1], p[2]))), seg || 32, r, radial || 8, false), material);
    if (parent) parent.add(m); return m;
  }
  function lathe(profile, material, seg, parent) {
    const m = new THREE.Mesh(new THREE.LatheGeometry(profile.map((p) => new THREE.Vector2(p[0], p[1])), seg || 48), material);
    if (parent) parent.add(m); return m;
  }
  function deform(geo, fn, smooth) {
    const p = geo.attributes.position, v = new V3();
    for (let i = 0; i < p.count; i++) { v.fromBufferAttribute(p, i); fn(v, i); p.setXYZ(i, v.x, v.y, v.z); }
    p.needsUpdate = true;
    if (smooth !== false) smoothNormals(geo);
    return geo;
  }
  function smoothNormals(geo) {
    const p = geo.attributes.position, idx = geo.index;
    const key = (i) => Math.round(p.getX(i) * 1e4) + ',' + Math.round(p.getY(i) * 1e4) + ',' + Math.round(p.getZ(i) * 1e4);
    const acc = new Map(), keys = new Array(p.count);
    for (let i = 0; i < p.count; i++) { keys[i] = key(i); if (!acc.has(keys[i])) acc.set(keys[i], new V3()); }
    const a = new V3(), b = new V3(), c = new V3(), n = new V3(), e = new V3();
    const tri = idx ? idx.count / 3 : p.count / 3;
    for (let t = 0; t < tri; t++) {
      const i0 = idx ? idx.getX(t * 3) : t * 3, i1 = idx ? idx.getX(t * 3 + 1) : t * 3 + 1, i2 = idx ? idx.getX(t * 3 + 2) : t * 3 + 2;
      a.fromBufferAttribute(p, i0); b.fromBufferAttribute(p, i1); c.fromBufferAttribute(p, i2);
      n.subVectors(c, b).cross(e.subVectors(a, b));
      acc.get(keys[i0]).add(n); acc.get(keys[i1]).add(n); acc.get(keys[i2]).add(n);
    }
    const nor = new Float32Array(p.count * 3);
    for (let i = 0; i < p.count; i++) { const v = acc.get(keys[i]).clone().normalize(); nor[i * 3] = v.x; nor[i * 3 + 1] = v.y; nor[i * 3 + 2] = v.z; }
    geo.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
    return geo;
  }
  // value noise, 3D, seeded by a small table
  function makeNoise(seed) {
    const rr = K.rng(seed), perm = new Float32Array(4096);
    for (let i = 0; i < 4096; i++) perm[i] = rr();
    const h = (x, y, z) => perm[(((x * 73856093) ^ (y * 19349663) ^ (z * 83492791)) >>> 0) & 4095];
    const f = (t) => t * t * (3 - 2 * t);
    return function (x, y, z) {
      const X = Math.floor(x), Y = Math.floor(y), Z = Math.floor(z), u = f(x - X), v = f(y - Y), w = f(z - Z);
      const l = (a, b, t) => a + (b - a) * t;
      return l(l(l(h(X, Y, Z), h(X + 1, Y, Z), u), l(h(X, Y + 1, Z), h(X + 1, Y + 1, Z), u), v),
               l(l(h(X, Y, Z + 1), h(X + 1, Y, Z + 1), u), l(h(X, Y + 1, Z + 1), h(X + 1, Y + 1, Z + 1), u), v), w);
    };
  }
  const smooth01 = (a, b, x) => { const t = Math.max(0, Math.min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
  // A tube whose radius follows rf(t); optional per vertex colour cf(t, angle) -> THREE.Color
  function taperTube(points, rf, material, seg, radial, cf) {
    const curve = new THREE.CatmullRomCurve3(points.map((p) => new V3(p[0], p[1], p[2])));
    const fr = curve.computeFrenetFrames(seg, false);
    const pos = [], nor = [], col = [], uv = [], idx = [];
    const P = new V3(), N = new V3();
    for (let i = 0; i <= seg; i++) {
      const t = i / seg; curve.getPointAt(t, P); const r = rf(t);
      for (let j = 0; j <= radial; j++) {
        const a = j / radial * TAU;
        N.copy(fr.normals[i]).multiplyScalar(Math.cos(a)).addScaledVector(fr.binormals[i], Math.sin(a)).normalize();
        pos.push(P.x + N.x * r, P.y + N.y * r, P.z + N.z * r); nor.push(N.x, N.y, N.z); uv.push(j / radial, t);
        if (cf) { const c = cf(t, a); col.push(c.r, c.g, c.b); }
      }
    }
    for (let i = 0; i < seg; i++) for (let j = 0; j < radial; j++) {
      const a = i * (radial + 1) + j, b = a + radial + 1; idx.push(a, b, a + 1, b, b + 1, a + 1);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); if (cf) g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
    g.setIndex(idx);
    return new THREE.Mesh(g, material);
  }
  function centre(g) {
    const bb = new THREE.Box3().setFromObject(g), c = new V3(); bb.getCenter(c);
    const inner = new THREE.Group(); while (g.children.length) inner.add(g.children[0]);
    inner.position.set(-c.x, -bb.min.y, -c.z); g.add(inner); return g;
  }

  /* ---- signed distance body and a surface nets mesher ------------------------------------ */
  function sdEll(px, py, pz, e) {
    let x = px - e.c[0], y = py - e.c[1], z = pz - e.c[2];
    if (e.ay) { const u = y * e.ay[1] + z * e.ay[2], w = y * e.az[1] + z * e.az[2]; y = u; z = w; }   // pitched about x
    x /= e.r[0]; y /= e.r[1]; z /= e.r[2];
    const k0 = Math.sqrt(x * x + y * y + z * z);
    const x2 = x / e.r[0], y2 = y / e.r[1], z2 = z / e.r[2];
    const k1 = Math.sqrt(x2 * x2 + y2 * y2 + z2 * z2);
    return k1 < 1e-9 ? -Math.min(e.r[0], e.r[1], e.r[2]) : k0 * (k0 - 1) / k1;
  }
  function sdRC(px, py, pz, s) {        // round cone a->b, radii r1 -> r2 (Inigo Quilez)
    const bx = s.b[0] - s.a[0], by = s.b[1] - s.a[1], bz = s.b[2] - s.a[2];
    const l2 = bx * bx + by * by + bz * bz, rr = s.r1 - s.r2, a2 = l2 - rr * rr, il2 = 1 / l2;
    const ax = px - s.a[0], ay = py - s.a[1], az = pz - s.a[2];
    const y = ax * bx + ay * by + az * bz, z = y - l2;
    const xx = ax * l2 - bx * y, xy = ay * l2 - by * y, xz = az * l2 - bz * y;
    const x2 = xx * xx + xy * xy + xz * xz, y2 = y * y * l2, z2 = z * z * l2;
    const k = Math.sign(rr) * rr * rr * x2;
    if (Math.sign(z) * a2 * z2 > k) return Math.sqrt(x2 + z2) * il2 - s.r2;
    if (Math.sign(y) * a2 * y2 < k) return Math.sqrt(x2 + y2) * il2 - s.r1;
    return (Math.sqrt(x2 * a2 * il2) + y * rr) * il2 - s.r1;
  }
  function smin(a, b, k) { if (k <= 0) return Math.min(a, b); const h = Math.max(k - Math.abs(a - b), 0) / k; return Math.min(a, b) - h * h * k * 0.25; }
  function buildSDF(prims) {
    // bounding sphere per primitive for an early out
    prims.forEach((p) => {
      if (p.t === 'e') { p.bc = p.c; p.br = Math.max(p.r[0], p.r[1], p.r[2]); }
      else { p.bc = [(p.a[0] + p.b[0]) / 2, (p.a[1] + p.b[1]) / 2, (p.a[2] + p.b[2]) / 2];
             p.br = Math.hypot(p.b[0] - p.a[0], p.b[1] - p.a[1], p.b[2] - p.a[2]) / 2 + Math.max(p.r1, p.r2); }
    });
    return function (x, y, z) {
      let d = 1e9;
      for (let i = 0; i < prims.length; i++) {
        const p = prims[i], k = p.k || 0;
        const dx = x - p.bc[0], dy = y - p.bc[1], dz = z - p.bc[2], lim = d + k + p.br * 1.05;
        if (d < 1e8 && dx * dx + dy * dy + dz * dz > lim * lim && lim > 0) continue;
        const di = p.t === 'e' ? sdEll(x, y, z, p) : sdRC(x, y, z, p);
        d = d > 1e8 ? di : smin(d, di, k);
      }
      return d;
    };
  }
  function surfaceNets(sdf, lo, hi, h) {
    const nx = Math.ceil((hi[0] - lo[0]) / h) + 1, ny = Math.ceil((hi[1] - lo[1]) / h) + 1, nz = Math.ceil((hi[2] - lo[2]) / h) + 1;
    const val = new Float32Array(nx * ny * nz), I = (i, j, k) => i + nx * (j + ny * k);
    const B = 4, rad = B * h * 0.87;
    for (let bk = 0; bk < nz; bk += B) for (let bj = 0; bj < ny; bj += B) for (let bi = 0; bi < nx; bi += B) {
      const cx = lo[0] + (bi + B / 2) * h, cy = lo[1] + (bj + B / 2) * h, cz = lo[2] + (bk + B / 2) * h;
      const dc = sdf(cx, cy, cz), skip = Math.abs(dc) > rad * 1.25 + h;
      for (let k = bk; k < Math.min(nz, bk + B); k++) for (let j = bj; j < Math.min(ny, bj + B); j++) for (let i = bi; i < Math.min(nx, bi + B); i++)
        val[I(i, j, k)] = skip ? dc : sdf(lo[0] + i * h, lo[1] + j * h, lo[2] + k * h);
    }
    const cell = new Int32Array((nx - 1) * (ny - 1) * (nz - 1)).fill(-1), C = (i, j, k) => i + (nx - 1) * (j + (ny - 1) * k);
    const verts = [];
    const E = [[0, 1], [2, 3], [4, 5], [6, 7], [0, 2], [1, 3], [4, 6], [5, 7], [0, 4], [1, 5], [2, 6], [3, 7]];
    const cv = new Float32Array(8), co = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 1], [1, 0, 1], [0, 1, 1], [1, 1, 1]];
    for (let k = 0; k < nz - 1; k++) for (let j = 0; j < ny - 1; j++) for (let i = 0; i < nx - 1; i++) {
      let neg = 0;
      for (let q = 0; q < 8; q++) { cv[q] = val[I(i + co[q][0], j + co[q][1], k + co[q][2])]; if (cv[q] < 0) neg++; }
      if (neg === 0 || neg === 8) continue;
      let sx = 0, sy = 0, sz = 0, n = 0;
      for (const [a, b] of E) {
        if ((cv[a] < 0) === (cv[b] < 0)) continue;
        const t = cv[a] / (cv[a] - cv[b]);
        sx += co[a][0] + (co[b][0] - co[a][0]) * t; sy += co[a][1] + (co[b][1] - co[a][1]) * t; sz += co[a][2] + (co[b][2] - co[a][2]) * t; n++;
      }
      cell[C(i, j, k)] = verts.length / 3;
      verts.push(lo[0] + (i + sx / n) * h, lo[1] + (j + sy / n) * h, lo[2] + (k + sz / n) * h);
    }
    const idx = [];
    const quad = (a, b, c, d, flip) => { if (a < 0 || b < 0 || c < 0 || d < 0) return; if (flip) idx.push(a, c, b, a, d, c); else idx.push(a, b, c, a, c, d); };
    for (let k = 0; k < nz; k++) for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) {
      const v0 = val[I(i, j, k)] < 0;
      if (i < nx - 1 && j > 0 && k > 0 && j < ny - 1 && k < nz - 1) { const v1 = val[I(i + 1, j, k)] < 0; if (v0 !== v1) quad(cell[C(i, j - 1, k - 1)], cell[C(i, j, k - 1)], cell[C(i, j, k)], cell[C(i, j - 1, k)], v1); }
      if (j < ny - 1 && i > 0 && k > 0 && i < nx - 1 && k < nz - 1) { const v1 = val[I(i, j + 1, k)] < 0; if (v0 !== v1) quad(cell[C(i - 1, j, k - 1)], cell[C(i - 1, j, k)], cell[C(i, j, k)], cell[C(i, j, k - 1)], v1); }
      if (k < nz - 1 && i > 0 && j > 0 && i < nx - 1 && j < ny - 1) { const v1 = val[I(i, j, k + 1)] < 0; if (v0 !== v1) quad(cell[C(i - 1, j - 1, k)], cell[C(i, j - 1, k)], cell[C(i, j, k)], cell[C(i - 1, j, k)], v1); }
    }
    // project onto the surface, normals from the field gradient
    const e = h * 0.35, nor = new Float32Array(verts.length);
    for (let v = 0; v < verts.length; v += 3) {
      let x = verts[v], y = verts[v + 1], z = verts[v + 2];
      // tetrahedral gradient: four samples give the value and the gradient together
      const a = sdf(x + e, y - e, z - e), b = sdf(x - e, y - e, z + e), c = sdf(x - e, y + e, z - e), d4 = sdf(x + e, y + e, z + e);
      let gx = a - b - c + d4, gy = -a - b + c + d4, gz = -a + b - c + d4;
      const gl = Math.sqrt(gx * gx + gy * gy + gz * gz) || 1; gx /= gl; gy /= gl; gz /= gl;
      const d = Math.max(-h, Math.min(h, (a + b + c + d4) / 4));
      verts[v] = x - gx * d; verts[v + 1] = y - gy * d; verts[v + 2] = z - gz * d; nor[v] = gx; nor[v + 1] = gy; nor[v + 2] = gz;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
    g.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
    g.setIndex(idx);
    return g;
  }

  /* ================================================================================ CATTLE */
  function cattleSpec(breed, r) {
    const LH = breed === 'longhorn';
    const H = LH ? 1.4 : 1.3, B = LH ? 0.78 : 0.66, Lz = LH ? 0.8 : 0.76, W = LH ? 0.27 : 0.32;
    const lr = LH ? 0.9 : 1;                         // leg radius factor
    const P = [];
    const E = (c, rr, k) => P.push({ t: 'e', c, r: rr, k: k || 0 });
    const R = (a, b, r1, r2, k) => P.push({ t: 'r', a, b, r1, r2, k: k || 0 });
    const Yc = (H + B) / 2 - 0.02, Hy = (H - B) / 2;
    E([0, Yc, -0.02], [W, Hy, Lz]);                                                           // barrel
    E([0, H - 0.11, -0.04], [W * 0.6, 0.09, Lz * 0.96], 0.14);                                // topline
    E([0, B + 0.2, Lz - 0.16], [W * 0.74, 0.26, 0.28], 0.16);                                 // chest, brisket
    E([0, H - 0.21, Lz - 0.2], [W * 0.84, 0.22, 0.3], 0.16);                                  // shoulder
    E([0, H - 0.15, -Lz + 0.2], [W * 0.92, 0.21, 0.34], 0.14);                                // rump
    for (const s of [-1, 1]) {
      E([s * W * 0.7, H - 0.1, -Lz + 0.44], [0.07, 0.06, 0.08], 0.12);                        // hooks
      E([s * 0.09, H - 0.14, -Lz - 0.04], [0.05, 0.05, 0.05], 0.1);                          // pins
      E([s * W * 0.6, B + 0.18, -Lz + 0.2], [0.15 * lr, 0.32, 0.24], 0.12);                  // thigh, stifle
    }
    // legs (stance varies a little by seed)
    const fs = (r() - 0.5) * 0.12, hs = (r() - 0.5) * 0.12;
    const fx = W * 0.55, hx = W * 0.54;
    [[-1, fs], [1, -fs]].forEach(([s, dz]) => {
      const kz = Lz - 0.13 + dz;
      R([s * W * 0.6, B + 0.16, Lz - 0.2], [s * fx, 0.38, kz], 0.105 * lr, 0.062 * lr, 0.09);   // forearm
      E([s * fx, 0.37, kz + 0.008], [0.052 * lr, 0.05, 0.05 * lr], 0.03);                      // knee
      R([s * fx, 0.37, kz], [s * fx, 0.11, kz + 0.01], 0.05 * lr, 0.043 * lr, 0.025);         // cannon
      R([s * fx, 0.11, kz + 0.01], [s * fx, 0.05, kz + 0.05], 0.05 * lr, 0.042 * lr, 0.02);    // fetlock, pastern
    });
    [[-1, hs], [1, -hs]].forEach(([s, dz]) => {
      const hz = -Lz - 0.06 + dz;
      R([s * W * 0.6, B + 0.02, -Lz + 0.14], [s * hx, 0.48, hz], 0.11 * lr, 0.056 * lr, 0.08);  // gaskin
      E([s * hx, 0.5, hz - 0.04], [0.035 * lr, 0.05, 0.04], 0.03);                             // point of hock
      R([s * hx, 0.47, hz], [s * hx, 0.11, hz + 0.07], 0.048 * lr, 0.042 * lr, 0.025);         // cannon
      R([s * hx, 0.11, hz + 0.07], [s * hx, 0.05, hz + 0.11], 0.048 * lr, 0.04 * lr, 0.02);    // pastern
    });
    // head frame: poll, axis a down the face, w out of the face
    const pitch = LH ? 1.0 : 1.05, HL = LH ? 0.54 : 0.46;
    const poll = [0, H - 0.02, Lz + 0.34];
    const ax = [0, -Math.sin(pitch), Math.cos(pitch)], aw = [0, Math.cos(pitch), Math.sin(pitch)];
    const at = (u, w, x) => [x || 0, poll[1] + ax[1] * u + aw[1] * w, poll[2] + ax[2] * u + aw[2] * w];
    const HE = (u, w, rx, ru, rw, k) => P.push({ t: 'e', c: at(u, w), r: [rx, ru, rw], ay: ax, az: aw, k: k || 0 });
    // neck into the back of the skull
    R([0, H - 0.24, Lz - 0.12], at(0.1, -0.1), 0.25, 0.13, 0.14);
    E([0, B + 0.14, Lz + 0.02], [0.06, LH ? 0.1 : 0.14, LH ? 0.12 : 0.16], 0.1);              // dewlap
    const hw = LH ? 0.9 : 1;
    HE(0.02, -0.04, 0.11 * hw, 0.06, 0.08, 0.04);                   // poll
    HE(0.12, -0.03, 0.125 * hw, 0.12, 0.1, 0.05);                   // cranium, eye sockets
    HE(0.3 * HL / 0.5, -0.005, 0.095 * hw, 0.2 * HL / 0.5, 0.07, 0.06);   // face
    HE(0.27 * HL / 0.5, -0.1, 0.085 * hw, 0.17 * HL / 0.5, 0.065, 0.06);  // cheeks, jaw
    HE(HL - 0.05, -0.035, 0.095 * hw, 0.07, 0.085, 0.05);           // muzzle
    R(at(HL - 0.12, -0.12), at(HL - 0.04, -0.1), 0.045, 0.04, 0.04); // chin
    R([0, H - 0.1, -Lz - 0.03], [0, H - 0.22, -Lz - 0.1], 0.045, 0.032, 0.05);                 // tail head
    if (!LH) E([0, B - 0.02, -Lz + 0.36], [0.1, 0.08, 0.12], 0.07);                             // udder
    const muz = at(HL, -0.03);
    return { P, H, B, Lz, W, poll, muz, at, fx, hx, fs, hs, LH, HL };
  }
  K.define('cattle', {
    size: [0.8, 1.55, 2.5],
    options: { breed: 'hereford', horns: true, spread: 1.9, coat: 'auto' },
    note: 'A beef animal standing, facing +z, modelled as one smooth body (signed distance field meshed with surface nets): barrel, topline, hooks and pins, dewlap, jointed legs with knees and hocks, cloven hooves, head, ears, eyes, tail with a switch. breed hereford (red with a white face, crest, underline and socks; horns true gives the down curving horns, false is polled) or longhorn (rangy, spread in metres tip to tip, coat auto | red | paint | brindle | dun | speckle).',
    make(o, r) {
      const breed = o.breed === 'longhorn' ? 'longhorn' : 'hereford', LH = breed === 'longhorn';
      const S = cattleSpec(breed, r), sdf = buildSDF(S.P);
      const geo = surfaceNets(sdf, [-0.42, -0.02, -S.Lz - 0.25], [0.42, S.H + 0.12, S.Lz + 0.8], 0.025);
      // coat
      const nz = makeNoise((o.seed || 1) * 17 + 3), pos = geo.attributes.position, col = new Float32Array(pos.count * 3);
      let coat = o.coat && o.coat !== 'auto' ? o.coat : (LH ? ['paint', 'red', 'speckle', 'brindle', 'dun', 'paint'][Math.floor(r() * 6)] : 'hereford');
      const red = new THREE.Color(LH ? 0x8b3a1c : 0x7a2c14), white = new THREE.Color(0xe9e2d4), black = new THREE.Color(0x1f1a17);
      const dun = new THREE.Color(0xb89a6c), brown = new THREE.Color(0x4a2b1a), nose = new THREE.Color(LH ? 0x2b2522 : 0xc28a7d);
      const patch = new THREE.Color(r() < 0.5 ? 0x8a3a1c : 0x221c19);
      const c = new THREE.Color();
      const segDist = (px, py, pz, a, b) => { const bx = b[0] - a[0], by = b[1] - a[1], bz = b[2] - a[2];
        const t = Math.max(0, Math.min(1, ((px - a[0]) * bx + (py - a[1]) * by + (pz - a[2]) * bz) / (bx * bx + by * by + bz * bz)));
        return Math.hypot(px - a[0] - bx * t, py - a[1] - by * t, pz - a[2] - bz * t); };
      for (let i = 0; i < pos.count; i++) {
        const x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i);
        const n1 = nz(x * 9, y * 9, z * 9) * 0.7 + nz(x * 23, y * 23, z * 23) * 0.3, n2 = nz(x * 2.2 + 11, y * 2.2, z * 2.2), n3 = nz(x * 60, y * 60, z * 60);
        let w = 0;
        if (coat === 'hereford') {
          c.copy(red).multiplyScalar(0.88 + n1 * 0.22);
          const head = smooth01(S.Lz + 0.27, S.Lz + 0.3, z + (n1 - 0.5) * 0.08);
          const crest = 1 - smooth01(0.09, 0.105, segDist(x, y, z, S.at(0.0, 0.0), [0, S.H + 0.02, S.Lz - 0.25]) + (n1 - 0.5) * 0.04);
          const under = (1 - smooth01(S.B + 0.05, S.B + 0.08, y + (n1 - 0.5) * 0.1)) * smooth01(S.B - 0.16, S.B - 0.1, y) * smooth01(-S.Lz + 0.05, -S.Lz + 0.2, z) * (1 - smooth01(0.3, 0.42, Math.abs(y - 0.4) < 1 ? 1 - y : 0));
          const brisket = smooth01(S.Lz - 0.3, S.Lz - 0.15, z) * (1 - smooth01(S.B + 0.3, S.B + 0.4, y)) * (1 - smooth01(0.1, 0.18, Math.abs(x)));
          const socks = 1 - smooth01(0.34, 0.37, y + (n1 - 0.5) * 0.1);
          w = Math.max(head, crest, under * (y > 0.45 ? 1 : 0), brisket, socks);
          // red eye patches
          if (head > 0) { const ey = S.at(0.13, 0.02); const ep = Math.hypot(Math.abs(x) - 0.12, y - ey[1], z - ey[2]); w *= smooth01(0.03, 0.06, ep + (n1 - 0.5) * 0.03); }
          c.lerp(white.clone().multiplyScalar(0.92 + n1 * 0.1), w);
        } else {
          const base = coat === 'dun' ? dun : coat === 'brindle' ? brown : coat === 'speckle' ? white : red;
          c.copy(base).multiplyScalar(0.86 + n1 * 0.24);
          if (coat === 'paint') { const p = smooth01(0.52, 0.55, n2 + (n1 - 0.5) * 0.12); c.lerp(white, p); if (r() < 0) c.set(0); }
          if (coat === 'speckle') { const p = smooth01(0.55, 0.6, n2); c.lerp(patch, p); const sp = nz(x * 40, y * 40, z * 40); if (sp > 0.72) c.lerp(patch, 0.8); }
          if (coat === 'brindle') { const st = nz(x * 3, y * 26, z * 3); c.lerp(black, smooth01(0.45, 0.6, st) * 0.8); }
          if (coat === 'red') { const p = smooth01(0.6, 0.64, n2); c.lerp(white, p * (y < S.B + 0.15 ? 1 : 0.4)); }
          if (coat === 'dun') { c.lerp(brown, (1 - smooth01(0.25, 0.4, y)) * 0.7); }
        }
        // darker muzzle, nose pad
        const nt = S.at(S.HL + 0.02, -0.01), dm = Math.hypot(x * 0.8, y - nt[1], z - nt[2]);
        c.lerp(nose, (1 - smooth01(0.045, 0.075, dm)) * 0.85);
        // hooves region below the pasterns, darker points
        if (y < 0.08) c.lerp(black, 0.3);
        c.multiplyScalar(0.94 + n3 * 0.12);
        col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b;
      }
      geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
      const hide = mat('hide', { color: 0xffffff, vertexColors: true, roughness: 0.85, sheen: 0.25, sheenRoughness: 0.7, sheenColor: 0xb8a48a }, true);
      const g = new THREE.Group();
      g.add(new THREE.Mesh(geo, hide));
      // find the surface along a ray (for eyes, ears, horn roots)
      const onSurface = (from, dir) => { const p = new V3(...from), d = new V3(...dir).normalize();
        let sd = sdf(p.x, p.y, p.z), n = 0;
        while (sd < 0 && n++ < 200) { p.addScaledVector(d, Math.max(0.002, -sd)); sd = sdf(p.x, p.y, p.z); }
        for (let i = 0; i < 12; i++) { p.addScaledVector(d, -sd); sd = sdf(p.x, p.y, p.z); }
        return p; };
      // eyes
      const eyeM = mat('eye', { color: 0x0c0806, roughness: 0.08, metalness: 0.1 }, false);
      for (const s of [-1, 1]) {
        const p = onSurface(S.at(0.13, 0.03), [s, 0.02, 0.12]);
        const e = new THREE.Mesh(new THREE.SphereGeometry(0.019, 16, 12), eyeM); e.position.copy(p).add(new V3(-s * 0.006, 0, 0)); g.add(e);
        const lid = new THREE.Mesh(new THREE.TorusGeometry(0.02, 0.006, 6, 18), mat('eyelid', { color: 0x2a211d, roughness: 0.8 }));
        lid.position.copy(e.position); lid.rotation.y = s * Math.PI / 2 * 0.8; g.add(lid);
      }
      // ears: cupped, horizontal, slightly drooping
      for (const s of [-1, 1]) {
        const root = onSurface(S.at(0.07, -0.05), [s, 0.1, -0.1]);
        const ear = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 10, 0, TAU, 0, Math.PI * 0.62), mat('ear' + breed + coat, { color: LH ? (coat === 'dun' ? 0xa88a60 : 0x7a3a22) : 0x7a2c14, roughness: 0.85, side: THREE.DoubleSide }));
        ear.scale.set(0.035, 0.11, 0.065); ear.rotation.set(0, 0, -s * (Math.PI / 2 + 0.25)); ear.rotation.y = s * 0.35;
        ear.position.copy(root).add(new V3(s * 0.07, -0.01, 0)); g.add(ear);
        const inner = new THREE.Mesh(new THREE.CircleGeometry(1, 16), mat('earIn', { color: 0xc9a58f, roughness: 0.9, side: THREE.DoubleSide }));
        inner.scale.set(0.045, 0.028, 1); inner.position.copy(ear.position).add(new V3(s * 0.005, 0.012, 0.004)); inner.rotation.set(-Math.PI / 2 + 0.2, 0, s * 0.3); g.add(inner);
      }
      // nostrils
      for (const s of [-1, 1]) { const p = onSurface([s * 0.03, S.muz[1] - 0.01, S.muz[2] + 0.02], [s * 0.3, 0, 1]);
        const n = new THREE.Mesh(new THREE.SphereGeometry(0.012, 10, 8), mat('nostril', { color: 0x120c0a, roughness: 0.4 })); n.scale.set(0.7, 1, 0.5); n.position.copy(p); g.add(n); }
      // horns
      if (o.horns !== false || LH) {
        const hornCol = (t) => new THREE.Color(0xd9c7a0).lerp(new THREE.Color(0xb49a6a), smooth01(0, 0.35, t) * 0.4).lerp(new THREE.Color(0x2b241e), smooth01(0.72, 0.97, t)).multiplyScalar(1 - 0.08 * Math.max(0, Math.sin(t * 70)) * (1 - t));
        const hm = mat('horn', { color: 0xffffff, vertexColors: true, roughness: 0.5, clearcoat: 0.15, clearcoatRoughness: 0.5 }, true);
        for (const s of [-1, 1]) {
          const root = S.at(0.0, -0.01, s * 0.07);
          let pts;
          if (LH) {
            const sp = (o.spread || 1.9) / 2, up = 0.18 + r() * 0.12, fw = (r() - 0.3) * 0.12;
            const [, ry, rz] = root;
            pts = [root, [s * 0.18, ry + 0.02, rz + 0.01], [s * sp * 0.45, ry + 0.04, rz + fw * 0.5], [s * sp * 0.78, ry + up * 0.45, rz - 0.02 + fw],
                   [s * sp * 0.97, ry + up, rz - 0.09 + fw * 1.5], [s * sp, ry + up * 1.35, rz - 0.19 + fw]];
          } else {
            const [, ry, rz] = root;
            pts = [root, [s * 0.16, ry + 0.025, rz + 0.0], [s * 0.24, ry + 0.045, rz + 0.06], [s * 0.27, ry + 0.03, rz + 0.13], [s * 0.26, ry - 0.01, rz + 0.18]];
          }
          const rBase = LH ? 0.055 : 0.038;
          g.add(taperTube(pts, (t) => rBase * (1 - 0.86 * Math.pow(t, 0.9)) + 0.003, hm, LH ? 64 : 32, 14, (t) => hornCol(t)));
        }
      }
      // hooves: two claws each, with dew claws
      const hoofM = mat('hoof', { color: 0x2a2320, roughness: 0.55 });
      const hoofGeo = new THREE.LatheGeometry([[0, 0], [0.034, 0], [0.036, 0.008], [0.03, 0.045], [0.018, 0.068], [0, 0.07]].map((p) => new THREE.Vector2(p[0], p[1])), 20);
      const feet = [[-S.fx, S.Lz - 0.13 + S.fs + 0.06], [S.fx, S.Lz - 0.13 - S.fs + 0.06], [-S.hx, -S.Lz - 0.06 + S.hs + 0.12], [S.hx, -S.Lz - 0.06 - S.hs + 0.12]];
      feet.forEach(([x, z]) => {
        for (const s of [-1, 1]) { const h = new THREE.Mesh(hoofGeo, hoofM); h.scale.set(0.62, 1, 1.25); h.position.set(x + s * 0.02, 0, z); h.rotation.x = 0.12; g.add(h); }
        const dew = new THREE.Mesh(new THREE.SphereGeometry(0.012, 8, 6), hoofM); dew.position.set(x, 0.1, z - 0.07); g.add(dew);
      });
      // tail and switch
      const tailCol = new THREE.Color(); const tc = S.P.length; void tc;
      const tailTop = [0, S.H - 0.22, -S.Lz - 0.11];
      const tailPts = [tailTop, [0.0, S.H - 0.4, -S.Lz - 0.16], [0.02, 0.8, -S.Lz - 0.17], [0.035, 0.55, -S.Lz - 0.14]];
      const switchWhite = coat === 'hereford';
      tailCol.set(switchWhite ? 0x7a2c14 : (coat === 'dun' ? 0x9c7f58 : coat === 'speckle' ? 0xd9d2c4 : 0x6e2f18));
      const tailM = mat('tail' + coat, { color: tailCol, roughness: 0.85 });
      g.add(taperTube(tailPts, (t) => 0.034 - 0.018 * t, tailM, 24, 8));
      const swM = mat('switch' + coat, { color: switchWhite ? 0xe6dfd2 : (coat === 'brindle' ? 0x1e1916 : coat === 'dun' ? 0x3a2a1c : 0x2a1f19), roughness: 0.95 });
      const sw = new THREE.SphereGeometry(1, 14, 10);
      deform(sw, (v) => { const k = 1 + 0.25 * Math.sin(v.x * 9 + v.z * 7) * Math.sin(v.y * 5); v.x *= k; v.z *= k; if (v.y < 0) { v.x *= 1 + 0.4 * -v.y; v.z *= 1 + 0.3 * -v.y; } });
      const swm = new THREE.Mesh(sw, swM); swm.scale.set(0.045, 0.16, 0.04); swm.position.set(0.04, 0.44, -S.Lz - 0.135); g.add(swm);
      for (let k = 0; k < 7; k++) { const a = r() * TAU; tube([[0.04, 0.5, -S.Lz - 0.135], [0.04 + Math.cos(a) * 0.03, 0.36, -S.Lz - 0.135 + Math.sin(a) * 0.03], [0.04 + Math.cos(a) * 0.05, 0.27 + r() * 0.04, -S.Lz - 0.135 + Math.sin(a) * 0.05]], 0.006, swM, 8, 5, g); }
      return centre(g);
    },
  });

  /* ============================================================================== WINDMILL */
  function angleLeg(parent, a, b, size, material) {
    // galvanized L angle from a to b, legs of the L facing out from the tower centre
    const A = new V3(...a), B = new V3(...b), len = A.distanceTo(B), mid = A.clone().add(B).multiplyScalar(0.5);
    const g = new THREE.Group(); g.position.copy(mid);
    const dir = B.clone().sub(A).normalize();
    const out = new V3(mid.x, 0, mid.z).normalize();
    const side = new V3().crossVectors(dir, out).normalize(), o2 = new V3().crossVectors(side, dir).normalize();
    const m = new THREE.Matrix4().makeBasis(side, dir, o2); g.quaternion.setFromRotationMatrix(m);
    const t = size * 0.1;
    const f1 = new THREE.Mesh(new THREE.BoxGeometry(size, len, t), material); f1.position.set(0, 0, -t / 2); g.add(f1);
    const f2 = new THREE.Mesh(new THREE.BoxGeometry(t, len, size), material); f2.position.set(size / 2 - t / 2, 0, -size / 2); g.add(f2);
    parent.add(g); return g;
  }
  K.define('windmill', {
    size: [3.2, 12.5, 3.2],
    options: { tower: 10, wheel: 2.44, yaw: 0.6, platform: true, ladder: true, pipe: true },
    note: 'Aermotor style water pumping windmill: four post galvanized angle lattice tower with girts and rod cross bracing on concrete footings, wooden platform, side ladder, pump rod down the centre to a pump stand with a discharge pipe, a geared head with its domed hood, an 18 sail wheel (wheel = diameter in metres, 8 ft default) on two rings, and a long tail vane. yaw turns the head.',
    make(o, r) {
      const g = new THREE.Group();
      const Ht = o.tower || 10, base = Math.max(1.8, Ht * 0.26), topw = 0.46;
      const galv = M.galv(), dull = M.galvDull(), conc = M.conc();
      const corner = (y, sx, sz) => { const w = base + (topw - base) * (y / Ht); return [sx * w / 2, y, sz * w / 2]; };
      const C = [[-1, -1], [1, -1], [1, 1], [-1, 1]];
      C.forEach(([sx, sz]) => {
        angleLeg(g, corner(0.05, sx, sz), corner(Ht, sx, sz), 0.064, galv);
        rbox(0.34, 0.25, 0.34, 0.02, conc, corner(0, sx, sz)[0], -0.05, corner(0, sx, sz)[2], g, 2, 1);
        // anchor stub
        box(0.07, 0.3, 0.012, galv, corner(0, sx, sz)[0] * 0.98, 0.0, corner(0, sx, sz)[2] * 0.98, g);
      });
      // girts and cross bracing, panel by panel
      const levels = [0.45]; let y = 0.45; while (y < Ht - 1.2) { y += Math.max(1.0, (Ht - y) * 0.28); if (y < Ht - 0.6) levels.push(Math.min(y, Ht - 0.6)); }
      levels.push(Ht - 0.15);
      levels.forEach((ly) => {
        for (let k = 0; k < 4; k++) { const a = corner(ly, ...C[k]), b = corner(ly, ...C[(k + 1) % 4]); bar(a, b, 0.018, galv, g, 6); }
      });
      for (let i = 0; i < levels.length - 1; i++) for (let k = 0; k < 4; k++) {
        const a0 = corner(levels[i], ...C[k]), b0 = corner(levels[i], ...C[(k + 1) % 4]), a1 = corner(levels[i + 1], ...C[k]), b1 = corner(levels[i + 1], ...C[(k + 1) % 4]);
        bar(a0, b1, 0.008, dull, g, 6); bar(b0, a1, 0.008, dull, g, 6);
      }
      // platform
      if (o.platform !== false) {
        const py = Ht - 1.35, pw = 1.6;
        const plank = M.wood('#7d6a55');
        for (let k = 0; k < 4; k++) {
          const side = new THREE.Group(); side.rotation.y = k * Math.PI / 2; side.position.y = py; g.add(side);
          for (let j = 0; j < 3; j++) { const pb = box(pw - j * 0.001, 0.035, 0.14, plank, 0, 0, pw / 2 - 0.08 - j * 0.155, side, 1.2); pb.rotation.y = (r() - 0.5) * 0.01; }
          bar([-pw / 2, -0.04, pw / 2 - 0.2], [pw / 2, -0.04, pw / 2 - 0.2], 0.02, galv, side, 6);
        }
        C.forEach(([sx, sz]) => bar(corner(py - 0.9, sx, sz), [sx * 0.72, py - 0.05, sz * 0.72], 0.012, galv, g, 6));
      }
      // ladder up the front face, on the right leg
      if (o.ladder !== false) {
        const top = Ht - 1.35;
        const L0 = corner(0.05, 1, 1), L1 = corner(top, 1, 1);
        const off = (p, d) => [p[0] - 0.35 + d, p[1], p[2] + 0.04];
        bar(off(L0, 0), off(L1, 0), 0.012, galv, g, 6);
        const rungs = Math.floor(top / 0.36);
        for (let k = 1; k < rungs; k++) { const t = k / rungs, yy = top * t; const p = corner(yy, 1, 1); bar([p[0] - 0.35, yy, p[2] + 0.04], [p[0] - 0.01, yy, p[2] + 0.02], 0.009, galv, g, 6); }
      }
      // mast, head, wheel, tail
      const head = new THREE.Group(); head.position.y = Ht; head.rotation.y = o.yaw != null ? o.yaw : 0.6; g.add(head);
      cyl(0.045, 0.05, 0.55, galv, 0, -0.1, 0, 16, head);
      const hm = M.paint(0x8f9395);
      // gearbox body and the domed hood over it
      rbox(0.26, 0.28, 0.48, 0.05, hm, 0, 0.35, 0.05, head, 3);
      const hood = lathe([[0, 0], [0.17, 0], [0.17, 0.16], [0.15, 0.24], [0.1, 0.3], [0.04, 0.33], [0, 0.335]], galv, 32, null);
      hood.rotation.x = Math.PI / 2; hood.position.set(0, 0.5, 0.05); head.add(hood);
      cyl(0.03, 0.03, 0.12, hm, 0, 0.62, -0.05, 12, head);
      // wheel on the shaft, offset to the side as the head carries it
      const Dw = o.wheel || 2.44, Rw = Dw / 2;
      const wheel = new THREE.Group(); wheel.position.set(0.12, 0.5, 0.55); head.add(wheel);
      const hub = cyl(0.07, 0.07, 0.16, hm, 0, 0, 0, 24, null); hub.rotation.x = Math.PI / 2; wheel.add(hub);
      const rIn = Rw * 0.36, rOut = Rw;
      for (const rr of [Rw * 0.4, Rw * 0.97]) { const ring = new THREE.Mesh(new THREE.TorusGeometry(rr, 0.012, 6, 96), galv); ring.scale.z = 2.2; wheel.add(ring); }
      for (let k = 0; k < 6; k++) { const a = k / 6 * TAU; bar([0, 0, 0.02], [Math.cos(a) * Rw * 0.97, Math.sin(a) * Rw * 0.97, 0], 0.012, galv, wheel, 6);
        bar([0, 0, -0.12], [Math.cos(a + 0.2) * Rw * 0.6, Math.sin(a + 0.2) * Rw * 0.6, 0], 0.006, galv, wheel, 6); }
      // one sail: tapered, cupped, pitched
      const sg = new THREE.PlaneGeometry(1, 1, 3, 8), sp = sg.attributes.position;
      for (let i = 0; i < sp.count; i++) {
        const u = sp.getX(i) + 0.5, v = sp.getY(i) + 0.5;
        const rad = rIn + v * (rOut - rIn), w = (0.1 + v * 0.15) * Dw / 2.44, a = (u - 0.5) * w;
        const cup = 0.018 * (1 - (2 * u - 1) ** 2), pitch = 0.62 - v * 0.12;
        sp.setXYZ(i, a * Math.cos(pitch) - cup * Math.sin(pitch), rad, a * Math.sin(pitch) + cup * Math.cos(pitch));
      }
      sg.computeVertexNormals();
      const sm = mat('sail', { color: 0xffffff, metalness: 0.75, roughness: 0.42, map: ltex('spangle', paintSpangle, {}), side: THREE.DoubleSide });
      const sails = new THREE.InstancedMesh(sg, sm, 18);
      for (let k = 0; k < 18; k++) sails.setMatrixAt(k, new THREE.Matrix4().makeRotationZ(k / 18 * TAU));
      wheel.add(sails);
      // tail bone and vane
      const tl = Dw * 1.0;
      for (const s of [-1, 1]) bar([0, 0.45 + s * 0.08, -0.1], [0, 0.5 + s * 0.25, -tl], 0.016, galv, head, 6);
      bar([0, 0.53, -0.1], [0, 0.5, -tl], 0.012, galv, head, 6);
      const vw = Dw * 0.6, vh = Dw * 0.32;
      const vshape = new THREE.Shape([[0, -vh * 0.4], [vw * 0.85, -vh / 2], [vw, 0], [vw * 0.85, vh / 2], [0, vh * 0.4]].map((p) => new THREE.Vector2(p[0], p[1])));
      const vg = new THREE.ExtrudeGeometry(vshape, { depth: 0.004, bevelEnabled: true, bevelThickness: 0.003, bevelSize: 0.008, bevelSegments: 2 });
      K.uvBox(vg, 1.0);
      const vane = new THREE.Mesh(vg, mat('vane', { color: 0xffffff, metalness: 0.75, roughness: 0.4, map: ltex('spangle', paintSpangle, {}) }));
      vane.rotation.y = Math.PI / 2; vane.position.set(0, 0.5, -tl + vw * 0.35); head.add(vane);
      for (const yy of [-0.25, 0, 0.25]) bar([0.01, 0.5 + yy * vh, -tl + vw * 0.35], [0.01, 0.5 + yy * vh * 0.8, -tl + vw * 0.35 - vw * 0.95], 0.006, galv, head, 5);
      // pump rod, furl wire, pump stand and discharge
      bar([0, 0.3, 0], [0, Ht - 0.2, 0], 0.016, mat('rodWood', { color: 0x7a6650, roughness: 0.9 }), g, 8);
      if (o.pipe !== false) {
        cyl(0.05, 0.05, 0.9, galv, 0, 0, 0, 16, g); cyl(0.065, 0.065, 0.06, galv, 0, 0.82, 0, 16, g);
        cyl(0.03, 0.03, 0.35, galv, 0, 0.9, 0, 12, g);
        tube([[0, 0.7, 0], [0.3, 0.7, 0.05], [base / 2 + 0.6, 0.66, 0.2], [base / 2 + 1.0, 0.5, 0.25]], 0.03, galv, 24, 10, g);
        const tee = cyl(0.045, 0.045, 0.14, galv, 0, 0, 0, 16, null); tee.rotation.z = Math.PI / 2; tee.position.set(0.06, 0.7, 0); g.add(tee);
      }
      tube([[0.02, Ht + 0.3, 0.02], [0.03, Ht - 3, 0.03], [0.04, 1.3, 0.06]], 0.003, galv, 12, 4, g);
      box(0.03, 0.45, 0.03, galv, corner(1.2, 1, -1)[0] - 0.05, 1.0, corner(1.2, 1, -1)[2] + 0.05, g);
      return g;
    },
  });

  /* ============================================================================ STOCK TANK */
  K.define('stock_tank', {
    size: [3.1, 0.66, 3.1],
    options: { d: 3.05, h: 0.61, water: 0.8, inlet: true },
    note: 'Round galvanized stock tank (10 ft x 2 ft default): vertical corrugated sidewall with spangle and water line staining, rolled pipe rim, crimped bottom chime, murky water with an algae line, and a float valve on an inlet pipe over the rim. water is the fill fraction.',
    make(o, r) {
      const D = o.d || 3.05, R = D / 2, H = o.h || 0.61, g = new THREE.Group();
      const n = Math.round(TAU * R / 0.068), seg = n * 6;
      const side = new THREE.CylinderGeometry(R, R, H - 0.03, seg, 6, true);
      deform(side, (v) => { const a = Math.atan2(v.z, v.x), k = 1 + (0.009 * Math.sin(a * n)) / R; v.x *= k; v.z *= k; }, false);
      side.computeVertexNormals(); side.translate(0, (H - 0.03) / 2 + 0.03, 0);
      const uv = side.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * TAU * R / 1.5, uv.getY(i) * H / 1.5);
      const sideM = mat('tankSide', { color: 0xffffff, metalness: 0.78, roughness: 0.45, side: THREE.DoubleSide, map: ltex('tankspangle', paintSpangle, { streaks: true }) });
      g.add(new THREE.Mesh(side, sideM));
      const galv = M.galv();
      const rim = new THREE.Mesh(new THREE.TorusGeometry(R + 0.005, 0.022, 12, 160), galv); rim.rotation.x = Math.PI / 2; rim.position.y = H - 0.005; g.add(rim);
      const chime = new THREE.Mesh(new THREE.TorusGeometry(R + 0.004, 0.018, 8, 160), galv); chime.rotation.x = Math.PI / 2; chime.position.y = 0.02; chime.scale.z = 1.3; g.add(chime);
      const bottom = new THREE.Mesh(new THREE.CircleGeometry(R, 96), mat('tankBottom', { color: 0x5d5f55, roughness: 0.9 })); bottom.rotation.x = -Math.PI / 2; bottom.position.y = 0.03; g.add(bottom);
      const wl = 0.03 + (H - 0.06) * (o.water != null ? o.water : 0.8);
      const water = new THREE.Mesh(new THREE.CircleGeometry(R - 0.005, 96), mat('stockWater', { color: 0x31402c, roughness: 0.12, metalness: 0.0, clearcoat: 0.6, clearcoatRoughness: 0.08, envMapIntensity: 0.6 }, true));
      water.rotation.x = -Math.PI / 2; water.position.y = wl; g.add(water);
      // algae line inside the wall
      const alg = new THREE.Mesh(new THREE.CylinderGeometry(R - 0.004, R - 0.004, 0.07, 128, 1, true), mat('algae', { color: 0x3e4a2a, roughness: 0.9, side: THREE.BackSide }));
      alg.position.y = wl + 0.02; g.add(alg);
      if (o.inlet !== false) {
        const a = -0.7 + (r() - 0.5) * 0.4, px = Math.cos(a) * R, pz = Math.sin(a) * R;
        const out = new V3(px, 0, pz).normalize();
        tube([[px + out.x * 0.9, 0.0, pz + out.z * 0.9], [px + out.x * 0.5, 0.2, pz + out.z * 0.5], [px + out.x * 0.1, H + 0.12, pz + out.z * 0.1], [px - out.x * 0.15, H + 0.1, pz - out.z * 0.15], [px - out.x * 0.3, wl + 0.08, pz - out.z * 0.3]], 0.021, galv, 40, 10, g);
        const valve = rbox(0.08, 0.06, 0.06, 0.01, M.paint(0x8a7a52), px - out.x * 0.3, wl + 0.03, pz - out.z * 0.3, g, 2);
        void valve;
        const ball = new THREE.Mesh(new THREE.SphereGeometry(0.075, 24, 16), mat('float', { color: 0xc9c4b2, roughness: 0.5 })); ball.scale.y = 0.8;
        ball.position.set(px - out.x * 0.62, wl + 0.03, pz - out.z * 0.62); g.add(ball);
        bar([px - out.x * 0.3, wl + 0.04, pz - out.z * 0.3], [ball.position.x, wl + 0.05, ball.position.z], 0.004, galv, g, 6);
      }
      return g;
    },
  });

  /* ================================================================================== BARN */
  function paintRPanel(x, W, H, r, o) {
    // three major ribs per tile (12 in centres), two minor ribs between; ribs vary along U
    const base = o.color || '#a3a7a9';
    x.fillStyle = base; x.fillRect(0, 0, W, H);
    const rib = W / 3;
    for (let i = 0; i < 3; i++) {
      const x0 = i * rib;
      const g = x.createLinearGradient(x0, 0, x0 + rib * 0.16, 0);
      g.addColorStop(0, rgb(base, 0.62)); g.addColorStop(0.35, rgb(base, 1.18)); g.addColorStop(0.7, rgb(base, 0.96)); g.addColorStop(1, rgb(base, 0.72));
      x.fillStyle = g; x.fillRect(x0, 0, rib * 0.16, H);
      for (const m of [0.45, 0.72]) { x.fillStyle = rgb(base, 0.9); x.fillRect(x0 + rib * m, 0, 2, H); x.fillStyle = rgb(base, 1.08); x.fillRect(x0 + rib * m + 2, 0, 2, H); }
    }
    for (let i = 0; i < 120; i++) { x.fillStyle = 'rgba(0,0,0,' + (0.02 + r() * 0.03) + ')'; x.fillRect(r() * W, r() * H, 1 + r() * 3, 20 + r() * 120); }
    // screw lines
    for (const yy of [0.2, 0.7]) for (let i = 0; i < 3; i++) { x.fillStyle = 'rgba(30,30,30,0.5)'; x.fillRect(i * rib + rib * 0.3, yy * H, 3, 3); x.fillRect(i * rib + rib * 0.85, yy * H, 3, 3); }
  }
  function paintBoardBatten(x, W, H, r, o) {
    const base = o.color || '#8e2b1f', boards = 3, bw = W / boards;
    for (let i = 0; i < boards; i++) {
      x.fillStyle = rgb(base, 0.86 + r() * 0.2); x.fillRect(i * bw, 0, bw, H);
      for (let k = 0; k < 16; k++) { x.strokeStyle = 'rgba(0,0,0,' + (0.04 + r() * 0.08) + ')'; x.lineWidth = 1 + r() * 2; const xx = i * bw + r() * bw; x.beginPath(); x.moveTo(xx, 0); x.lineTo(xx + (r() - 0.5) * 8, H); x.stroke(); }
      for (let k = 0; k < 30; k++) { x.fillStyle = 'rgba(240,230,215,' + (0.05 + r() * 0.1) + ')'; x.fillRect(i * bw + r() * bw, r() * H, 2 + r() * 8, 1 + r() * 3); }   // paint wear
      // batten
      const bx = i * bw - bw * 0.1;
      x.fillStyle = 'rgba(0,0,0,0.35)'; x.fillRect(bx + bw * 0.2, 0, 4, H);
      x.fillStyle = rgb(base, 1.05); x.fillRect(bx, 0, bw * 0.2, H);
      x.fillStyle = 'rgba(255,255,255,0.08)'; x.fillRect(bx, 0, 3, H);
    }
  }
  K.define('barn', {
    size: [13.5, 8.2, 19.5],
    options: { style: 'gable', material: 'metal', color: null, roof: null, trim: null, w: 12, l: 18, open: true, leanTo: true },
    note: 'A Texas barn, gable end forward (+z): style gable | gambrel, material metal (R panel steel with a wainscot, trim, standing ridge cap, an open side shed on steel posts) or wood (red board and batten, white trim, X braced doors, hayloft door with a hay hood, a louvered cupola). Big sliding doors on a track, one pulled open onto a dark interior; framed glazed windows.',
    make(o, r) {
      const wood = o.material === 'wood', gambrel = o.style === 'gambrel';
      const W = o.w || 12, L = o.l || 18, He = gambrel ? 3.4 : wood ? 4.0 : 4.6;
      const g = new THREE.Group();
      const wallCol = o.color != null ? o.color : wood ? 0x8e2b1f : [0xb7b9b6, 0xc9bda3, 0x9aa3a0, 0x8a4a33][Math.floor(r() * 4)];
      const trimCol = o.trim != null ? o.trim : wood ? 0xece6da : 0x3b3d3e;
      const roofCol = o.roof != null ? o.roof : wood ? 0x6f7477 : 0xaeb2b4;
      const hex = (c) => '#' + new THREE.Color(c).getHexString();
      const wallM = wood ? mat('barnBB' + wallCol, { color: 0xffffff, roughness: 0.85, map: ltex('boardbatten', paintBoardBatten, { color: hex(wallCol) }) })
                         : mat('barnR' + wallCol, { color: 0xffffff, roughness: 0.5, metalness: 0.35, map: ltex('rpanel', paintRPanel, { color: hex(wallCol) }) });
      const tile = wood ? 0.9 : 0.915;
      const roofM = mat('barnRoof' + roofCol, { color: 0xffffff, roughness: 0.42, metalness: 0.6, map: ltex('rpanel', paintRPanel, { color: hex(roofCol) }) });
      const trimM = mat('trim' + trimCol, { color: trimCol, roughness: 0.55, metalness: wood ? 0 : 0.3 });
      const dark = mat('barnDark', { color: 0x0d0b09, roughness: 1 });
      // the profile, half, from the eave to the ridge
      const prof = gambrel ? (() => { const bx = W / 2 * 0.6, by = He + (W / 2 - bx) * Math.tan(1.05), ry = by + bx * Math.tan(0.42); return [[W / 2, He], [bx, by], [0, ry]]; })()
                           : [[W / 2, He], [0, He + W / 2 * (wood ? 0.62 : 0.33)]];
      const ridge = prof[prof.length - 1][1];
      const outline = [[-W / 2, 0], [W / 2, 0]].concat(prof, prof.slice(0, -1).reverse().map(([x, y]) => [-x, y]));
      // gable walls with a door opening in the front
      const doorW = Math.min(4.8, W * 0.42), doorH = Math.min(He - 0.4, 4.0);
      for (const s of [1, -1]) {
        const shp = new THREE.Shape(outline.map(([x, y]) => new THREE.Vector2(x, y)));
        if (s > 0) { const hole = new THREE.Path([[-doorW / 2, 0.15], [doorW / 2, 0.15], [doorW / 2, doorH], [-doorW / 2, doorH]].map(([x, y]) => new THREE.Vector2(x, y))); shp.holes.push(hole); }
        const geo = new THREE.ExtrudeGeometry(shp, { depth: 0.12, bevelEnabled: false }); geo.translate(0, 0, -0.06);
        K.uvBox(geo, tile);
        const m = new THREE.Mesh(geo, wallM); m.position.z = s * L / 2; g.add(m);
      }
      // side walls
      for (const s of [-1, 1]) { const m = box(0.12, He, L, wallM, s * W / 2, 0, 0, g); K.uvBox(m.geometry, tile); }
      // interior dark behind the door, and a floor
      box(W - 0.3, He - 0.1, 0.05, dark, 0, 0, L / 2 - 3.5, g);
      box(doorW + 0.4, 0.02, 3.4, mat('barnFloor', { color: 0x3b3329, roughness: 1 }), 0, 0.12, L / 2 - 1.75, g);
      for (const s of [-1, 1]) box(0.05, He, 3.5, dark, s * (doorW / 2 + 0.2), 0, L / 2 - 1.75, g);
      box(doorW + 0.4, 0.05, 3.5, dark, 0, doorH + 0.05, L / 2 - 1.75, g);
      // wainscot and base
      box(W + 0.26, 0.15, L + 0.26, M.conc(), 0, 0, 0, g, 1);
      if (!wood) {
        const wc = mat('wainscot', { color: 0xffffff, roughness: 0.5, metalness: 0.35, map: ltex('rpanel', paintRPanel, { color: hex(new THREE.Color(trimCol).multiplyScalar(1.4).getHex()) }) });
        for (const s of [-1, 1]) { const m = box(0.03, 0.95, L + 0.02, wc, s * (W / 2 + 0.075), 0.15, 0, g); K.uvBox(m.geometry, tile); }
        const m2 = box(W + 0.16, 0.95, 0.03, wc, 0, 0.15, -L / 2 - 0.075, g); K.uvBox(m2.geometry, tile);
        for (const sx of [-1, 1]) { const m3 = box((W - doorW) / 2 - 0.05, 0.95, 0.03, wc, sx * (doorW / 2 + ((W - doorW) / 2) / 2 + 0.05), 0.15, L / 2 + 0.075, g); K.uvBox(m3.geometry, tile); }
        for (const s of [-1, 1]) box(0.06, 0.05, L + 0.1, trimM, s * (W / 2 + 0.09), 1.1, 0, g);
      }
      // corner trim
      for (const sx of [-1, 1]) for (const sz of [-1, 1]) box(0.18, He, 0.18, trimM, sx * (W / 2), 0.15, sz * (L / 2), g);
      // roof planes, overhang, ridge cap
      const ov = 0.35, t = 0.06;
      for (const s of [-1, 1]) {
        for (let i = 0; i < prof.length - 1; i++) {
          const [x0, y0] = prof[i], [x1, y1] = prof[i + 1];
          const len = Math.hypot(x1 - x0, y1 - y0) + (i === 0 ? ov : 0) + 0.02, ang = Math.atan2(y1 - y0, x0 - x1);
          const geo = new THREE.BoxGeometry(len, t, L + 2 * ov);
          K.uvBox(geo, tile);
          const uva = geo.attributes.uv; for (let k = 0; k < uva.count; k++) { const u = uva.getX(k); uva.setX(k, uva.getY(k)); uva.setY(k, u); }
          const m = new THREE.Mesh(geo, roofM);
          const cx = (x0 + x1) / 2 + (i === 0 ? ov / 2 * Math.cos(ang) : 0), cy = (y0 + y1) / 2 - (i === 0 ? ov / 2 * Math.sin(ang) : 0);
          m.position.set(s * cx + s * Math.sin(ang) * t * 0.5, cy + Math.cos(ang) * t * 0.5 + 0.02, 0); m.rotation.z = -s * ang; g.add(m);
          // rake trim along both gables
          for (const sz of [-1, 1]) { const rk = new THREE.Mesh(new THREE.BoxGeometry(len, 0.2, 0.05), trimM); rk.position.set(m.position.x, m.position.y - 0.05, sz * (L / 2 + ov + 0.02)); rk.rotation.z = m.rotation.z; g.add(rk); }
        }
        // eave trim / fascia
        const ex = W / 2 + ov * Math.cos(Math.atan2(prof[1][1] - prof[0][1], prof[0][0] - prof[1][0]));
        box(0.05, 0.16, L + 2 * ov, trimM, s * (ex + 0.02), He - ov * Math.sin(Math.atan2(prof[1][1] - prof[0][1], prof[0][0] - prof[1][0])) - 0.08, 0, g);
      }
      const capA = Math.atan2(prof[prof.length - 1][1] - prof[prof.length - 2][1], prof[prof.length - 2][0]);
      for (const s of [-1, 1]) { const cp = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.02, L + 2 * ov), trimM); cp.position.set(s * 0.14, ridge + t + 0.03 - 0.14 * Math.tan(capA), 0); cp.rotation.z = -s * capA; g.add(cp); }
      // sliding doors on a track
      const track = box(doorW * 2 + 0.4, 0.14, 0.1, trimM, 0, doorH + 0.12, L / 2 + 0.12, g); void track;
      const doorM = wood ? wallM : mat('barnDoor' + wallCol, { color: 0xffffff, roughness: 0.5, metalness: 0.35, map: ltex('rpanel', paintRPanel, { color: hex(wallCol) }) });
      const leaf = (x) => {
        const dg = new THREE.Group(); dg.position.set(x, 0.12, L / 2 + 0.2); g.add(dg);
        const p = box(doorW / 2, doorH, 0.05, doorM, 0, 0, 0, dg); K.uvBox(p.geometry, tile);
        const fw = 0.14, tz = 0.04;
        box(doorW / 2, fw, 0.04, trimM, 0, 0, tz, dg); box(doorW / 2, fw, 0.04, trimM, 0, doorH - fw, tz, dg); box(doorW / 2, fw, 0.04, trimM, 0, doorH / 2 - fw / 2, tz, dg);
        box(fw, doorH, 0.04, trimM, -doorW / 4 + fw / 2, 0, tz, dg); box(fw, doorH, 0.04, trimM, doorW / 4 - fw / 2, 0, tz, dg);
        if (wood) for (const [y0, y1] of [[fw, doorH / 2 - fw / 2], [doorH / 2 + fw / 2, doorH - fw]]) {
          const hw = doorW / 4 - fw, len = Math.hypot(2 * hw, y1 - y0), a = Math.atan2(y1 - y0, 2 * hw);
          for (const s of [-1, 1]) { const d = new THREE.Mesh(new THREE.BoxGeometry(len, fw * 0.8, 0.035), trimM); d.position.set(0, (y0 + y1) / 2, tz + 0.005); d.rotation.z = s * a; dg.add(d); }
        }
        for (const s of [-1, 1]) { const w = cyl(0.06, 0.06, 0.04, M.black(), s * doorW / 6, 0, 0, 16, null); w.rotation.x = Math.PI / 2; w.position.set(s * doorW / 6, doorH + 0.1, -0.02); dg.add(w); }
        box(0.03, 0.3, 0.06, M.black(), doorW / 4 - 0.12, doorH * 0.45, 0.06, dg);
        return dg;
      };
      if (o.open !== false) { leaf(-doorW / 4 - doorW / 2 - 0.05); leaf(doorW / 4); }
      else { leaf(-doorW / 4); leaf(doorW / 4); }
      // windows along the sides
      const glass = K.finish.glass(), sill = trimM;
      const nWin = Math.max(2, Math.floor(L / 5));
      for (const s of [-1, 1]) for (let i = 0; i < nWin; i++) {
        const z = -L / 2 + (i + 0.5) * L / nWin, wy = He * 0.45, ww = 1.2, wh = 0.9;
        const wg = new THREE.Group(); wg.position.set(s * (W / 2 + 0.07), wy, z); wg.rotation.y = s * Math.PI / 2; g.add(wg);
        box(ww - 0.04, wh - 0.04, 0.02, dark, 0, 0.02, -0.02, wg);
        const pane = box(ww - 0.1, wh - 0.1, 0.01, glass, 0, 0.05, 0.0, wg); void pane;
        box(ww, 0.07, 0.07, trimM, 0, wh - 0.07, 0.02, wg); box(ww + 0.12, 0.05, 0.12, sill, 0, -0.05, 0.04, wg);
        box(0.07, wh, 0.07, trimM, -ww / 2 + 0.035, 0, 0.02, wg); box(0.07, wh, 0.07, trimM, ww / 2 - 0.035, 0, 0.02, wg);
        box(0.04, wh, 0.04, trimM, 0, 0, 0.02, wg); box(ww, 0.04, 0.04, trimM, 0, wh / 2 - 0.02, 0.02, wg);
      }
      if (wood) {
        // hayloft door and hay hood
        const hy = doorH + 0.5, hw = 1.5, hh = Math.min(1.6, ridge - hy - 0.9);
        const hd = new THREE.Group(); hd.position.set(0, hy, L / 2 + 0.08); g.add(hd);
        box(hw, hh, 0.05, wallM, 0, 0, 0, hd).geometry.attributes.uv && K.uvBox(hd.children[0].geometry, tile);
        box(hw, 0.12, 0.04, trimM, 0, 0, 0.04, hd); box(hw, 0.12, 0.04, trimM, 0, hh - 0.12, 0.04, hd);
        box(0.12, hh, 0.04, trimM, -hw / 2 + 0.06, 0, 0.04, hd); box(0.12, hh, 0.04, trimM, hw / 2 - 0.06, 0, 0.04, hd);
        const dl = Math.hypot(hw - 0.24, hh - 0.24);
        for (const s of [-1, 1]) { const d = new THREE.Mesh(new THREE.BoxGeometry(dl, 0.1, 0.035), trimM); d.position.set(0, hh / 2, 0.045); d.rotation.z = s * Math.atan2(hh - 0.24, hw - 0.24); hd.add(d); }
        // hood at the peak with a pulley beam
        const hoodY = ridge - 0.25;
        for (const s of [-1, 1]) { const rp = new THREE.Mesh(new THREE.BoxGeometry(1.1, 0.06, 1.3), roofM); rp.position.set(s * 0.45, hoodY - 0.25, L / 2 + 0.6); rp.rotation.z = s * -0.55; g.add(rp); }
        box(0.14, 0.14, 1.4, mat('beam', { color: 0x4a3a2a, roughness: 0.9 }), 0, hoodY - 0.55, L / 2 + 0.7, g);
        // cupola
        const cu = new THREE.Group(); cu.position.set(0, ridge - 0.1, 0); g.add(cu);
        box(1.2, 1.0, 1.2, wallM, 0, 0, 0, cu);
        for (let k = 0; k < 4; k++) { const f = new THREE.Group(); f.rotation.y = k * Math.PI / 2; cu.add(f);
          for (let j = 0; j < 6; j++) { const lv = box(0.9, 0.04, 0.08, trimM, 0, 0.3 + j * 0.1, 0.62, f); lv.rotation.x = 0.6; } }
        const cr = new THREE.Mesh(new THREE.ConeGeometry(1.05, 0.7, 4, 1), roofM); cr.rotation.y = Math.PI / 4; cr.position.y = 1.35; cu.add(cr);
        cyl(0.02, 0.02, 0.6, M.black(), 0, 1.6, 0, 8, cu);
      }
      if (!wood && o.leanTo !== false) {
        // open shed along the +x side on square steel posts
        const sw = 4.2, lowH = He - 0.2 - sw * 0.2, x0 = W / 2 + 0.1;
        const geo = new THREE.BoxGeometry(Math.hypot(sw + 0.3, sw * 0.2), 0.05, L * 0.66); K.uvBox(geo, tile);
        const uva = geo.attributes.uv; for (let k = 0; k < uva.count; k++) { const u = uva.getX(k); uva.setX(k, uva.getY(k)); uva.setY(k, u); }
        const lr = new THREE.Mesh(geo, roofM); lr.position.set(x0 + sw / 2 + 0.1, He - 0.35 - sw * 0.1, -L * 0.17); lr.rotation.z = -Math.atan2(sw * 0.2, sw + 0.3); g.add(lr);
        const pm = mat('postPaint', { color: 0x3b3d3e, metalness: 0.4, roughness: 0.5 });
        const posts = 4;
        for (let i = 0; i < posts; i++) { const z = -L * 0.17 - L * 0.33 + 0.2 + i * (L * 0.66 - 0.4) / (posts - 1); box(0.1, lowH, 0.1, pm, x0 + sw, 0, z, g); }
        box(0.1, 0.25, L * 0.66, pm, x0 + sw, lowH - 0.25, -L * 0.17, g);
      }
      return g;
    },
  });

  /* ============================================================================= HAY BALES */
  // A bale lathe: profile from the centre of one face, over the shoulder, along the side, to the
  // other face. Its UV v runs by arc length so an atlas can paint faces and side separately.
  function baleGeometry(R, Wd, rr, radial, noiseSeed, flat) {
    const pts = [], lens = [];
    const push = (x, y) => pts.push(new THREE.Vector2(x, y));
    const nFace = 10, nArc = 5, nSide = 12;
    for (let i = 0; i <= nFace; i++) push((R - rr) * i / nFace, -Wd / 2);
    for (let i = 1; i <= nArc; i++) { const a = -Math.PI / 2 + i / nArc * Math.PI / 2; push(R - rr + Math.cos(a) * rr, -Wd / 2 + rr + Math.sin(a) * rr); }
    for (let i = 1; i <= nSide; i++) push(R, -Wd / 2 + rr + (Wd - 2 * rr) * i / nSide);
    for (let i = 1; i <= nArc; i++) { const a = i / nArc * Math.PI / 2; push(R - rr + Math.cos(a) * rr, Wd / 2 - rr + Math.sin(a) * rr); }
    for (let i = nFace - 1; i >= 0; i--) push((R - rr) * i / nFace, Wd / 2);
    let acc = 0; lens.push(0);
    for (let i = 1; i < pts.length; i++) { acc += pts[i].distanceTo(pts[i - 1]); lens.push(acc); }
    const geo = new THREE.LatheGeometry(pts, radial);
    const uv = geo.attributes.uv, np = pts.length;
    for (let i = 0; i < uv.count; i++) { const j = i % np; uv.setY(i, lens[j] / acc); }
    const nz = makeNoise(noiseSeed);
    deform(geo, (v) => {
      const rr2 = Math.hypot(v.x, v.z);
      if (rr2 > 1e-4) {
        const a = Math.atan2(v.z, v.x);
        const bump = (nz(Math.cos(a) * 3 + 5, v.y * 4, Math.sin(a) * 3) - 0.5) * 0.05 + (nz(Math.cos(a) * 9, v.y * 12, Math.sin(a) * 9) - 0.5) * 0.015;
        const bulge = 0.03 * Math.cos(v.y / Wd * Math.PI);
        const k = (rr2 + (bump + bulge) * (rr2 / R)) / rr2; v.x *= k; v.z *= k;
      }
      v.y += (nz(v.x * 4, 1, v.z * 4) - 0.5) * 0.03 * (Math.abs(v.y) > Wd / 2 - 0.02 ? 1 : 0);
    });
    geo.rotateZ(Math.PI / 2);           // axis along x
    if (flat) deform(geo, (v) => { const fl = -R * 0.9; if (v.y < fl) v.y = fl + (v.y - fl) * 0.15; });
    geo.translate(0, R * 0.9, 0);
    return { geo, len: acc };
  }
  function paintBaleAtlas(x, W, H, r, o) {
    // v (canvas y, flipped) by arc length: [0, f] face, then shoulder, side, shoulder, [1 - f, 1] face
    const f = o.f, sideA = o.s0, sideB = o.s1, base = o.base, outer = o.outer;
    x.fillStyle = base; x.fillRect(0, 0, W, H);
    const Y = (v) => (1 - v) * H;
    // faces: spiral bands are diagonal stripes in (angle, radius) space
    for (const [v0, v1, dir] of [[0, f, 1], [1 - f, 1, -1]]) {
      const y0 = Y(v1), y1 = Y(v0), span = y1 - y0, pitch = span / 26;
      for (let k = -30; k < 60; k++) {
        const yy = y0 + k * pitch;
        x.strokeStyle = rgb(base, 0.72 + r() * 0.5); x.lineWidth = pitch * (0.3 + r() * 0.5);
        x.beginPath(); x.moveTo(0, yy); x.lineTo(W, yy + dir * pitch); x.stroke();
      }
      for (let k = 0; k < 1200; k++) { x.strokeStyle = rgb(base, 0.6 + r() * 0.65); x.lineWidth = 1 + r() * 1.5; const px = r() * W, py = y0 + r() * span, l = 6 + r() * 20;
        x.beginPath(); x.moveTo(px, py); x.lineTo(px + l, py + (r() - 0.5) * 4); x.stroke(); }
    }
    // the rolled side: strands around the circumference, weathered outer colour
    const s0 = Y(sideB), s1 = Y(sideA);
    x.fillStyle = outer; x.fillRect(0, s0, W, s1 - s0);
    for (let k = 0; k < 3500; k++) { x.strokeStyle = rgb(outer, 0.62 + r() * 0.7); x.lineWidth = 0.8 + r() * 1.8; const px = r() * W, py = s0 + r() * (s1 - s0), l = 10 + r() * 50;
      x.beginPath(); x.moveTo(px, py); x.lineTo(px + l, py + (r() - 0.5) * 5); x.stroke(); }
    if (o.wrap === 'net') {
      x.strokeStyle = 'rgba(245,245,240,0.35)'; x.lineWidth = 1;
      for (let i = -H; i < W; i += 14) { x.beginPath(); x.moveTo(i, s0); x.lineTo(i + (s1 - s0), s1); x.stroke(); x.beginPath(); x.moveTo(i + (s1 - s0), s0); x.lineTo(i, s1); x.stroke(); }
    } else if (o.wrap === 'twine') {
      for (let k = 0; k < 9; k++) { const yy = s0 + (k + 0.5) * (s1 - s0) / 9; x.strokeStyle = 'rgba(214,160,60,0.9)'; x.lineWidth = 2.5;
        x.beginPath(); x.moveTo(0, yy); for (let px = 0; px <= W; px += 32) x.lineTo(px, yy + (r() - 0.5) * 3); x.stroke(); }
    }
  }
  K.define('hay_bale', {
    size: [5.2, 2.6, 3.4],
    options: { count: 6, layout: 'auto', age: 'auto', wrap: 'net', d: 1.52, w: 1.52 },
    note: 'Round hay bales (5 x 5 ft default), instanced: lumpy rolled sides with net wrap or twine, spiral faces, a flattened contact patch where each sits. layout row | pyramid | scatter (auto: pyramid at 5 and more); age fresh | weathered (grey outer, gold faces).',
    make(o, r) {
      const n = Math.max(1, Math.min(20, o.count || 6)), R = (o.d || 1.52) / 2, Wd = o.w || 1.52;
      const age = o.age && o.age !== 'auto' ? o.age : (r() < 0.5 ? 'fresh' : 'weathered');
      const base = age === 'fresh' ? '#c7a960' : '#b89a5a', outer = age === 'fresh' ? '#b9a15c' : '#8f8573';
      const { geo, len } = baleGeometry(R, Wd, 0.14, 64, 7 + (o.seed || 1), true);
      const f = (R - 0.14) / len, arc = 0.14 * Math.PI / 2 / len;
      const tex = ltex('bale', paintBaleAtlas, { f, s0: f + arc, s1: 1 - f - arc, base, outer, wrap: o.wrap || 'net' }, [1024, 1024]);
      const m = mat('bale' + age + (o.wrap || 'net'), { color: 0xffffff, roughness: 0.95, map: tex });
      const g = new THREE.Group(), list = [];
      const layout = o.layout && o.layout !== 'auto' ? o.layout : n >= 5 ? 'pyramid' : 'row';
      const put = (x, y, z, yaw) => list.push(new THREE.Matrix4().compose(new V3(x, y, z), new THREE.Quaternion().setFromEuler(new THREE.Euler(0, yaw, 0))
        .multiply(new THREE.Quaternion().setFromAxisAngle(new V3(1, 0, 0), r() * 0.3)), new V3(1 + (r() - 0.5) * 0.04, 1, 1)));
      if (layout === 'pyramid') {
        const bottom = Math.ceil((n + 1) / 2), top = n - bottom;
        for (let i = 0; i < bottom; i++) put(0, 0, (i - (bottom - 1) / 2) * (2 * R * 0.99), (r() - 0.5) * 0.06);
        for (let i = 0; i < top; i++) put((r() - 0.5) * 0.06, R * 1.62, (i - (top - 1) / 2) * (2 * R * 0.99), (r() - 0.5) * 0.06);
      } else if (layout === 'row') {
        for (let i = 0; i < n; i++) put((i - (n - 1) / 2) * (Wd + 0.05), 0, (r() - 0.5) * 0.15, (r() - 0.5) * 0.1);
      } else {
        for (let i = 0; i < n; i++) put((r() - 0.5) * n * 2.2, 0, (r() - 0.5) * n * 1.6, r() * TAU);
      }
      const im = new THREE.InstancedMesh(geo, m, list.length); list.forEach((M4, i) => im.setMatrixAt(i, M4)); g.add(im);
      // loose straw at the foot of the stack
      const tufts = [];
      for (let k = 0; k < 40; k++) tufts.push(new THREE.Matrix4().compose(new V3((r() - 0.5) * 3, 0.01, (r() - 0.5) * (n * 1.2)), new THREE.Quaternion().setFromEuler(new THREE.Euler(0, r() * TAU, 0)), new V3(1, 1, 1)));
      const sg = new THREE.PlaneGeometry(0.25, 0.012); sg.rotateX(-Math.PI / 2);
      const st = new THREE.InstancedMesh(sg, mat('straw', { color: 0xc9ad66, roughness: 0.9, side: THREE.DoubleSide }), tufts.length);
      tufts.forEach((M4, i) => st.setMatrixAt(i, M4)); g.add(st);
      return centre(g);
    },
  });

  /* ========================================================================= COTTON MODULE */
  function paintCotton(x, W, H, r, o) {
    x.fillStyle = '#ece8df'; x.fillRect(0, 0, W, H);
    for (let k = 0; k < 900; k++) { x.fillStyle = 'rgba(255,255,255,' + (0.3 + r() * 0.5) + ')'; x.beginPath(); x.arc(r() * W, r() * H, 2 + r() * 7, 0, TAU); x.fill(); }
    for (let k = 0; k < 900; k++) { x.fillStyle = 'rgba(' + (90 + r() * 60) + ',' + (60 + r() * 40) + ',30,' + (0.3 + r() * 0.5) + ')'; x.fillRect(r() * W, r() * H, 1 + r() * 3, 1 + r() * 2); }
    if (o.rings) for (let k = 0; k < 40; k++) { x.strokeStyle = 'rgba(160,150,135,' + (0.1 + r() * 0.15) + ')'; x.lineWidth = 2; const yy = k * H / 40; x.beginPath(); x.moveTo(0, yy); x.lineTo(W, yy + H / 40); x.stroke(); }
  }
  function paintWrap(x, W, H, r, o) {
    const base = o.color || '#e2b41c';
    x.fillStyle = base; x.fillRect(0, 0, W, H);
    for (let k = 0; k < 60; k++) { const yy = r() * H; x.strokeStyle = 'rgba(0,0,0,' + (0.03 + r() * 0.06) + ')'; x.lineWidth = 1 + r() * 3; x.beginPath(); x.moveTo(0, yy); x.bezierCurveTo(W / 3, yy + (r() - 0.5) * 20, W * 2 / 3, yy + (r() - 0.5) * 20, W, yy + (r() - 0.5) * 8); x.stroke(); }
    for (let k = 0; k < 40; k++) { x.fillStyle = 'rgba(255,255,255,' + (0.04 + r() * 0.08) + ')'; x.fillRect(r() * W, r() * H, 30 + r() * 120, 2 + r() * 5); }
    // film overlap seams and a narrow band stripe along each edge of the wrap
    for (const yy of [0.08, 0.92]) { x.fillStyle = 'rgba(0,0,0,0.12)'; x.fillRect(0, yy * H, W, 3); }
    // a tag panel (blank)
    x.fillStyle = 'rgba(250,250,245,0.9)'; x.fillRect(W * 0.3, H * 0.4, W * 0.05, H * 0.12);
    // dust near the bottom of the film
    for (let k = 0; k < 80; k++) { x.fillStyle = 'rgba(120,100,70,' + (0.03 + r() * 0.06) + ')'; x.beginPath(); x.arc(r() * W, r() * H, 5 + r() * 30, 0, TAU); x.fill(); }
  }
  K.define('cotton_module', {
    size: [2.5, 2.3, 2.3],
    options: { shape: 'round', count: 1, wrap: 0xe2b41c },
    note: 'Harvested cotton. shape round: the plastic wrapped round module a picker drops (2.29 m across, 2.44 m wide) in yellow film with its loose tail, white lint and trash specks showing on the spiral faces; count lays them in a row. shape rect: a 32 ft rectangular module, packed cotton under a fitted tarp with tie ropes.',
    make(o, r) {
      const g = new THREE.Group(), n = Math.max(1, Math.min(8, o.count || 1));
      const hex = '#' + new THREE.Color(o.wrap != null ? o.wrap : 0xe2b41c).getHexString();
      if (o.shape === 'rect') {
        const L = 9.75, W = 2.4, H = 3.0;
        const cot = mat('cottonBody', { color: 0xffffff, roughness: 1, map: ltex('cotton', paintCotton, {}) });
        const core = new THREE.Mesh(new THREE.BoxGeometry(W, H * 0.92, L, 8, 8, 24), cot);
        deform(core.geometry, (v) => { const k = 1 - 0.04 * Math.max(0, v.y / (H / 2)); v.x *= k; v.x += (Math.sin(v.z * 3) * 0.02 + Math.sin(v.y * 5 + v.z) * 0.015) * Math.sign(v.x); });
        K.uvBox(core.geometry, 1.5); core.position.y = H * 0.46; g.add(core);
        const tarpM = mat('tarp' + hex, { color: 0xffffff, roughness: 0.55, map: ltex('wrap', paintWrap, { color: hex }), side: THREE.DoubleSide });
        const prof = []; for (let i = 0; i <= 24; i++) { const a = Math.PI * i / 24; prof.push(new THREE.Vector2(Math.cos(a) * (W / 2 + 0.04), H * 0.92 - 0.2 + Math.sin(a) * 0.3)); }
        prof.unshift(new THREE.Vector2(W / 2 + 0.05, H * 0.5)); prof.push(new THREE.Vector2(-W / 2 - 0.05, H * 0.5));
        const pts = []; for (let i = 0; i <= 24; i++) pts.push(new V3(0, 0, -L / 2 - 0.1 + (L + 0.2) * i / 24));
        const shp = new THREE.Shape(prof); void shp;
        // tarp as a swept open profile
        const pos = [], idx = [], uv = [];
        prof.forEach((p, i) => { for (let j = 0; j <= 24; j++) { const z = -L / 2 - 0.1 + (L + 0.2) * j / 24; pos.push(p.x + Math.sin(z * 2 + i) * 0.01, p.y + (i === 0 || i === prof.length - 1 ? Math.sin(z * 1.3) * 0.08 : 0), z); uv.push(i / prof.length * 3, j / 24 * 4); } });
        for (let i = 0; i < prof.length - 1; i++) for (let j = 0; j < 24; j++) { const a = i * 25 + j, b = a + 25; idx.push(a, b, a + 1, b, b + 1, a + 1); }
        const tg = new THREE.BufferGeometry(); tg.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); tg.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); tg.setIndex(idx); tg.computeVertexNormals();
        g.add(new THREE.Mesh(tg, tarpM));
        const rope = mat('rope', { color: 0xd8d2c0, roughness: 0.9 });
        for (let k = 0; k < 7; k++) { const z = -L / 2 + 0.6 + k * (L - 1.2) / 6; const pr = prof.map((p) => [p.x * 1.01, p.y + 0.01, z]); tube(pr, 0.008, rope, 40, 5, g); }
        return centre(g);
      }
      const R = 1.145, Wd = 2.44;
      const { geo, len } = baleGeometry(R, Wd, 0.1, 72, 31 + (o.seed || 1), true);
      // two materials by arc length: film on the side and shoulders, cotton on the faces
      const f = (R - 0.1) / len;
      const cotM = mat('cottonFace', { color: 0xffffff, roughness: 1, emissive: 0x2a2826, map: ltex('cotton', paintCotton, { rings: true }) });
      const wrapM = mat('wrap' + hex, { color: 0xffffff, roughness: 0.32, clearcoat: 0.6, clearcoatRoughness: 0.3, map: ltex('wrap', paintWrap, { color: hex }) }, true);
      // split the index by uv.y: faces (v < f*0.92 or v > 1 - f*0.92) get cotton
      const idx = geo.index.array, uvA = geo.attributes.uv, A = [], B = [];
      for (let t = 0; t < idx.length; t += 3) {
        const v = (uvA.getY(idx[t]) + uvA.getY(idx[t + 1]) + uvA.getY(idx[t + 2])) / 3;
        (v < f * 0.95 || v > 1 - f * 0.95 ? A : B).push(idx[t], idx[t + 1], idx[t + 2]);
      }
      geo.setIndex(A.concat(B)); geo.clearGroups(); geo.addGroup(0, A.length, 0); geo.addGroup(A.length, B.length, 1);
      // faces: planar uv; wrap: repeat around
      for (let i = 0; i < uvA.count; i++) { const v = uvA.getY(i); if (v < f || v > 1 - f) { const p = geo.attributes.position; uvA.setXY(i, p.getZ(i) / 1.2, p.getY(i) / 1.2); } else uvA.setXY(i, uvA.getX(i) * 6, v * 2); }
      for (let i = 0; i < n; i++) {
        const m = new THREE.Mesh(geo, [cotM, wrapM]); m.position.set((i - (n - 1) / 2) * (Wd + 0.6), 0, (r() - 0.5) * 0.4); m.rotation.y = (r() - 0.5) * 0.12; g.add(m);
        // the loose film tail
        const a0 = -0.9 + r() * 0.3, tail = [];
        for (let k = 0; k <= 10; k++) { const a = a0 - k * 0.07, rr = R + 0.012 + k * 0.004; tail.push([Math.cos(a) * rr, R * 0.9 + Math.sin(a) * rr]); }
        const tp = [], ti = [], tu = [];
        tail.forEach(([yy, zz], k) => { for (const xx of [-Wd / 2 + 0.05, Wd / 2 - 0.05]) { tp.push(xx, Math.max(0.01, zz), yy); tu.push(xx > 0 ? 1 : 0, k / 10); } });
        for (let k = 0; k < tail.length - 1; k++) { const a = k * 2; ti.push(a, a + 2, a + 1, a + 1, a + 2, a + 3); }
        const tgm = new THREE.BufferGeometry(); tgm.setAttribute('position', new THREE.Float32BufferAttribute(tp, 3)); tgm.setAttribute('uv', new THREE.Float32BufferAttribute(tu, 2)); tgm.setIndex(ti); tgm.computeVertexNormals();
        const tm = new THREE.Mesh(tgm, mat('wrapTail' + hex, { color: 0xffffff, roughness: 0.35, map: ltex('wrap', paintWrap, { color: hex }), side: THREE.DoubleSide }));
        tm.position.copy(m.position); tm.rotation.y = m.rotation.y; tm.rotation.x = 0; g.add(tm);
      }
      return centre(g);
    },
  });

  /* ============================================================================= GRAIN BIN */
  function paintBinSheet(x, W, H, r) {
    paintSpangle(x, W, H, r, { base: '#aeb2b4' });
    // one tile = one sheet 2.85 m wide by 0.81 m ring, lap seams with bolt rows
    x.fillStyle = 'rgba(0,0,0,0.28)'; x.fillRect(0, 0, W, 4); x.fillRect(0, 0, 4, H);
    x.fillStyle = 'rgba(255,255,255,0.12)'; x.fillRect(0, 4, W, 2); x.fillRect(4, 0, 2, H);
    x.fillStyle = 'rgba(30,30,30,0.6)';
    for (let i = 8; i < H; i += 11) { x.fillRect(9, i, 3, 3); x.fillRect(16, i + 5, 3, 3); }
    for (let i = 8; i < W; i += 14) x.fillRect(i, 9, 3, 3);
    for (let i = 0; i < 12; i++) { const sx = r() * W, len = H * (0.2 + r() * 0.6), g = x.createLinearGradient(0, 0, 0, len);
      g.addColorStop(0, 'rgba(110,80,50,' + (0.08 + r() * 0.12) + ')'); g.addColorStop(1, 'rgba(110,80,50,0)'); x.fillStyle = g; x.fillRect(sx, 8, 3 + r() * 4, len); }
  }
  K.define('grain_bin', {
    size: [8.6, 10.2, 8.6],
    options: { d: 7.3, rings: 8, fan: true, ladder: true },
    note: 'Corrugated steel grain bin (24 ft default, rings of 32 in): horizontal corrugation in the silhouette, sheet laps and bolt rows, a 30 degree roof with standing ribs, a peak collar and cap, roof vents, an eave lip, a caged side ladder with a roof ladder to the peak, an entry door, an aeration fan with its transition, on a concrete pad.',
    make(o, r) {
      const D = o.d || 7.3, R = D / 2, He = (o.rings || 8) * 0.813, g = new THREE.Group();
      const pitch = 0.1, amp = 0.011, prof = [];
      for (let y = 0.15; y <= He + 1e-6; y += pitch / 4) prof.push([R + amp * Math.sin((y - 0.15) / pitch * TAU), y]);
      const wall = new THREE.LatheGeometry(prof.map((p) => new THREE.Vector2(p[0], p[1])), 112);
      const uv = wall.attributes.uv, pp = wall.attributes.position;
      for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * TAU * R / 2.85, (pp.getY(i) - 0.15) / 0.813);
      const wallM = mat('binWall', { color: 0xffffff, metalness: 0.8, roughness: 0.4, map: ltex('binsheet', paintBinSheet, {}, [1024, 292]) });
      g.add(new THREE.Mesh(wall, wallM));
      const galv = M.galv();
      rbox(D + 0.6, 0.15, D + 0.6, 0.02, M.conc(), 0, 0, 0, g, 1, 1).visible = false;
      const pad = cyl(R + 0.35, R + 0.38, 0.15, M.conc(), 0, 0, 0, 96, g); K.uvBox(pad.geometry, 3);
      // roof
      const ang = 30 * Math.PI / 180, peakR = 0.45, rise = (R + 0.12 - peakR) * Math.tan(ang);
      const roof = lathe([[R + 0.14, He - 0.02], [R + 0.14, He + 0.03], [peakR, He + 0.03 + rise], [peakR, He + 0.08 + rise]], mat('binRoof', { color: 0xffffff, metalness: 0.78, roughness: 0.38, map: ltex('spangle', paintSpangle, {}) }), 112, g);
      K.uvBox(roof.geometry, 2);
      const ribs = [], sl = Math.hypot(R + 0.14 - peakR, rise), nr = Math.round(TAU * R / 0.62);
      for (let k = 0; k < nr; k++) {
        const a = k / nr * TAU, mid = (R + 0.14 + peakR) / 2;
        const m4 = new THREE.Matrix4().compose(new V3(Math.cos(a) * mid, He + 0.05 + rise / 2, Math.sin(a) * mid),
          new THREE.Quaternion().setFromEuler(new THREE.Euler(0, -a, 0)).multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(0, 0, ang))), new V3(1, 1, 1));
        ribs.push(m4);
      }
      const rg = new THREE.BoxGeometry(sl, 0.035, 0.03); rg.translate(0, 0.0, 0);
      const rim = new THREE.InstancedMesh(rg, galv, ribs.length); ribs.forEach((m4, i) => rim.setMatrixAt(i, m4)); g.add(rim);
      const eave = new THREE.Mesh(new THREE.TorusGeometry(R + 0.14, 0.03, 8, 160), galv); eave.rotation.x = Math.PI / 2; eave.position.y = He; g.add(eave);
      // peak collar, cap, fan cap
      lathe([[peakR + 0.02, He + rise], [peakR + 0.02, He + rise + 0.2], [0.35, He + rise + 0.25], [0.35, He + rise + 0.45], [0.55, He + rise + 0.5], [0.1, He + rise + 0.72], [0, He + rise + 0.74]], galv, 48, g);
      // roof vents
      for (let k = 0; k < 4; k++) {
        const a = k / 4 * TAU + 0.4, rr = R * 0.6, y = He + (R + 0.12 - rr) * Math.tan(ang) + 0.05;
        const v = new THREE.Group(); v.position.set(Math.cos(a) * rr, y, Math.sin(a) * rr); v.rotation.y = -a + Math.PI / 2; v.rotation.x = 0; g.add(v);
        const hood = rbox(0.5, 0.28, 0.45, 0.03, galv, 0, -0.02, 0, v, 2); hood.rotation.x = -ang * 0; void hood;
        box(0.44, 0.14, 0.02, M.black(), 0, 0.02, 0.23, v);
      }
      // side ladder with cage, roof ladder to the peak
      if (o.ladder !== false) {
        const la = 0.35, lx = Math.cos(la) * (R + 0.25), lz = Math.sin(la) * (R + 0.25);
        const L = new THREE.Group(); L.position.set(lx, 0, lz); L.rotation.y = -la + Math.PI / 2; g.add(L);
        for (const s of [-1, 1]) bar([s * 0.22, 0.4, 0], [s * 0.22, He + 0.6, 0], 0.02, galv, L, 8);
        for (let y = 0.6; y < He + 0.5; y += 0.3) bar([-0.22, y, 0], [0.22, y, 0], 0.012, galv, L, 6);
        for (let y = 2.3; y < He + 0.4; y += 0.9) { const hoop = new THREE.Mesh(new THREE.TorusGeometry(0.38, 0.012, 6, 24, Math.PI), galv); hoop.rotation.x = Math.PI / 2; hoop.rotation.z = Math.PI; hoop.position.set(0, y, -0.0); hoop.scale.set(1, 1, 1); L.add(hoop); }
        for (let k = 0; k < 5; k++) { const a = Math.PI * (k + 0.5) / 5; bar([Math.cos(a) * 0.38, 2.3, Math.sin(a) * 0.38], [Math.cos(a) * 0.38, He + 0.4, Math.sin(a) * 0.38], 0.01, galv, L, 5); }
        for (let k = 0; k < 3; k++) bar([0, k * 0.8 + 0.4, -0.25], [0, k * 0.8 + 0.4, 0], 0.012, galv, L, 5);
        // roof ladder: two rails along the slope to the collar
        const x0 = R + 0.1, x1 = peakR + 0.1, y0 = He + 0.1, y1 = He + rise + 0.1;
        for (const s of [-1, 1]) { const p0 = [Math.cos(la) * x0 - Math.sin(la) * s * 0.2, y0, Math.sin(la) * x0 + Math.cos(la) * s * 0.2], p1 = [Math.cos(la) * x1 - Math.sin(la) * s * 0.2, y1, Math.sin(la) * x1 + Math.cos(la) * s * 0.2]; bar(p0, p1, 0.016, galv, g, 6); }
        for (let t = 0.05; t < 1; t += 0.09) { const xx = x0 + (x1 - x0) * t, yy = y0 + (y1 - y0) * t + 0.02; bar([Math.cos(la) * xx - Math.sin(la) * 0.2, yy, Math.sin(la) * xx + Math.cos(la) * 0.2], [Math.cos(la) * xx + Math.sin(la) * 0.2, yy, Math.sin(la) * xx - Math.cos(la) * 0.2], 0.01, galv, g, 5); }
      }
      // entry door
      const da = Math.PI / 2 + 0.15;
      const door = new THREE.Group(); door.position.set(Math.cos(da) * (R + 0.02), 0.3, Math.sin(da) * (R + 0.02)); door.rotation.y = -da + Math.PI / 2; g.add(door);
      rbox(0.75, 1.2, 0.05, 0.02, galv, 0, 0, 0, door, 2);
      for (const yy of [0.15, 0.95]) box(0.08, 0.1, 0.06, M.black(), -0.36, yy, 0.02, door);
      box(0.2, 0.04, 0.06, M.black(), 0.25, 0.6, 0.03, door);
      if (o.fan !== false) {
        const fa = Math.PI / 2 - 0.5, fx = Math.cos(fa), fz = Math.sin(fa);
        const F = new THREE.Group(); F.position.set(fx * (R + 0.05), 0, fz * (R + 0.05)); F.rotation.y = -fa + Math.PI / 2; g.add(F);
        const fanM = M.paint(0x6f7c86);
        box(0.8, 0.6, 0.8, galv, 0, 0.3, 0.35, F);                                        // transition
        const housing = cyl(0.55, 0.55, 0.45, fanM, 0, 0, 0, 40, null); housing.rotation.x = Math.PI / 2; housing.position.set(0, 0.75, 1.0); F.add(housing);
        const intake = cyl(0.42, 0.42, 0.05, mat('fanGrille', { color: 0x2a2d30, metalness: 0.6, roughness: 0.5, wireframe: false }), 0, 0, 0, 40, null); intake.rotation.x = Math.PI / 2; intake.position.set(0, 0.75, 1.25); F.add(intake);
        const mot = cyl(0.18, 0.18, 0.4, M.paint(0x2c4f6e), 0, 0, 0, 24, null); mot.rotation.x = Math.PI / 2; mot.position.set(0, 0.75, 1.45); F.add(mot);
        for (let k = 0; k < 4; k++) { const a = k / 4 * TAU; bar([Math.cos(a) * 0.4, 0.75 + Math.sin(a) * 0.4, 1.26], [Math.cos(a) * 0.18, 0.75 + Math.sin(a) * 0.18, 1.3], 0.012, galv, F, 5); }
        box(0.9, 0.5, 0.1, galv, 0, 0, 0.9, F);
        box(0.8, 0.15, 0.8, M.conc(), 0, 0, 1.0, F);
      }
      return g;
    },
  });

  /* ============================================================================ RANCH GATE */
  K.define('ranch_gate', {
    size: [5.4, 1.9, 0.4],
    options: { w: 3.66, rails: 5, finish: 'galvanized', color: 0x2f4a3a, open: 0, fence: true },
    note: 'Pipe rail ranch gate (12 ft default) closed across the opening: galvanized tube frame, five rails spaced tighter at the bottom, a diagonal brace, welded joints, hung on pin hinges from a painted oilfield pipe post with a domed cap; latch post with a chain latch; H braces and barbed wire running off both sides. finish galvanized | painted (color). open swings it in degrees.',
    make(o, r) {
      const Wg = o.w || 3.66, g = new THREE.Group();
      const tubeM = o.finish === 'painted' ? M.paint(o.color != null ? o.color : 0x2f4a3a) : M.galv();
      const postM = mat('oilfieldPipe', { color: 0x3a3632, metalness: 0.45, roughness: 0.6 });
      const tr = 0.021, Hg = 1.27;
      const hingeX = -Wg / 2 - 0.1;
      // posts
      for (const x of [hingeX, Wg / 2 + 0.1]) {
        cyl(0.057, 0.057, 1.75, postM, x, 0, 0, 24, g);
        const cap = new THREE.Mesh(new THREE.SphereGeometry(0.06, 20, 10, 0, TAU, 0, Math.PI / 2), postM); cap.position.set(x, 1.75, 0); g.add(cap);
        const bead = new THREE.Mesh(new THREE.TorusGeometry(0.058, 0.006, 6, 24), postM); bead.rotation.x = Math.PI / 2; bead.position.set(x, 1.75, 0); g.add(bead);
      }
      // gate leaf
      const leaf = new THREE.Group(); leaf.position.set(hingeX, 0, 0); leaf.rotation.y = -(o.open || 0) * Math.PI / 180; g.add(leaf);
      const x0 = 0.1, x1 = Wg + 0.1 - 0.04;
      const rails = Math.max(3, o.rails || 5), ys = [];
      for (let i = 0; i < rails; i++) { const t = i / (rails - 1); ys.push(0.18 + (Hg - 0.18) * Math.pow(t, 1.25)); }
      ys.forEach((y) => { const b = bar([x0, y, 0], [x1, y, 0], tr, tubeM, leaf, 14); void b; });
      bar([x0, 0.12, 0], [x0, Hg + 0.04, 0], tr * 1.15, tubeM, leaf, 14);
      bar([x1, 0.14, 0], [x1, Hg + 0.02, 0], tr, tubeM, leaf, 14);
      bar([x0, ys[1], 0], [x1 * 0.55, Hg, 0], tr * 0.8, tubeM, leaf, 12);
      const weld = mat('weld', { color: 0x6b6b66, metalness: 0.5, roughness: 0.7 });
      ys.forEach((y) => { for (const x of [x0, x1]) { const w = new THREE.Mesh(new THREE.SphereGeometry(tr * 1.35, 10, 8), weld); w.position.set(x, y, 0); leaf.add(w); } });
      for (const x of [x0, x1]) { const c = new THREE.Mesh(new THREE.SphereGeometry(tr, 12, 8), tubeM); c.position.set(x, x === x0 ? Hg + 0.04 : Hg + 0.02, 0); leaf.add(c); }
      // hinges: collars on the gate, pins on brackets on the post
      for (const y of [0.3, Hg - 0.15]) {
        const col = cyl(0.03, 0.03, 0.09, mat('hinge', { color: 0x4a4540, metalness: 0.5, roughness: 0.6 }), 0.0, y - 0.045, 0, 16, leaf); void col;
        bar([0.0, y, 0], [x0, y, 0], 0.012, tubeM, leaf, 8);
        bar([hingeX + 0.05, y + 0.05, 0], [hingeX + 0.1, y + 0.05, 0], 0.012, postM, g, 8);
      }
      // chain latch on the far post
      const cx = Wg / 2 + 0.1, links = [];
      for (let k = 0; k < 9; k++) { const t = k / 8; links.push([cx - 0.06 - t * 0.1, Hg - 0.25 - Math.sin(t * Math.PI) * 0.12, 0.04 + Math.sin(t * Math.PI) * 0.03]); }
      const lm = mat('chain', { color: 0x5b5752, metalness: 0.7, roughness: 0.45 });
      links.forEach((p, k) => { const L = new THREE.Mesh(new THREE.TorusGeometry(0.018, 0.0045, 6, 12), lm); L.scale.set(1, 1.6, 1); L.position.set(...p); L.rotation.set(k % 2 ? Math.PI / 2 : 0, 0, 1.2); g.add(L); });
      // H braces, fence posts and barbed wire off both sides
      if (o.fence !== false) {
        const wireM = mat('wire', { color: 0x7d7a74, metalness: 0.6, roughness: 0.5 });
        for (const s of [-1, 1]) {
          const px = s * (Wg / 2 + 0.1), bx = px + s * 2.4, ex = px + s * 5.0;
          cyl(0.057, 0.057, 1.55, postM, bx, 0, 0, 20, g);
          const cap = new THREE.Mesh(new THREE.SphereGeometry(0.06, 16, 8, 0, TAU, 0, Math.PI / 2), postM); cap.position.set(bx, 1.55, 0); g.add(cap);
          bar([px, 1.15, 0], [bx, 1.15, 0], 0.03, postM, g, 12);
          bar([px, 0.15, 0.0], [bx, 1.1, 0.0], 0.006, wireM, g, 4);
          const tpost = cyl(0.02, 0.02, 1.3, mat('tpost', { color: 0x2d4b3a, metalness: 0.3, roughness: 0.6 }), ex, 0, 0, 8, g); void tpost;
          for (const y of [0.4, 0.7, 1.0, 1.3]) {
            const ww = K.cable([px, y, 0.03], [ex, y - 0.01, 0.03], 0.02, 0.0025, wireM, g); void ww;
            const barbs = []; for (let x = Math.min(px, ex) + 0.1; x < Math.max(px, ex); x += 0.12) barbs.push(new THREE.Matrix4().compose(new V3(x, y - 0.01, 0.03), new THREE.Quaternion().setFromEuler(new THREE.Euler(0.7, 0, 0.5)), new V3(1, 1, 1)));
            const bim = new THREE.InstancedMesh(new THREE.BoxGeometry(0.004, 0.03, 0.004), wireM, barbs.length); barbs.forEach((m4, k) => bim.setMatrixAt(k, m4)); g.add(bim);
          }
        }
      }
      return g;
    },
  });

  /* ========================================================================== CATTLE GUARD */
  K.define('cattle_guard', {
    size: [7.4, 1.4, 4.9],
    options: { w: 4.9, l: 2.13, finish: 'pipe', color: 0xd6a820, wings: true },
    note: 'A ranch road cattle guard, road running along z: steel pipe rails across the road on I beam stringers over a dark pit, concrete grade beams at both approaches with caliche ramps, and pipe wings flaring up at each end to the fence line. finish pipe (bare, weathered) | galvanized | painted (color).',
    make(o, r) {
      const Wd = o.w || 4.9, L = o.l || 2.13, g = new THREE.Group();
      const railM = o.finish === 'galvanized' ? M.galv() : o.finish === 'painted' ? M.paint(o.color != null ? o.color : 0xd6a820) : M.pipe();
      const topY = 0.32, pr = 0.044;
      const conc = M.conc(), cal = mat('caliche', { color: 0xffffff, roughness: 0.95, map: K.tex('concrete', { color: '#cbbb98' }) });
      // pit
      box(Wd, 0.01, L, mat('pit', { color: 0x221d18, roughness: 1 }), 0, 0.0, 0, g);
      for (const s of [-1, 1]) { const m = box(Wd + 0.3, topY - 0.02, 0.3, conc, 0, 0, s * (L / 2 + 0.15), g); K.uvBox(m.geometry, 3); }
      for (const s of [-1, 1]) { const m = box(0.3, topY - 0.02, L + 0.6, conc, s * (Wd / 2 + 0.15), 0, 0, g); K.uvBox(m.geometry, 3); }
      // I beam stringers along the road
      const beamM = M.pipe();
      for (let k = 0; k < 4; k++) {
        const x = -Wd / 2 + 0.4 + k * (Wd - 0.8) / 3;
        box(0.12, 0.012, L + 0.5, beamM, x, topY - 2 * pr - 0.012, 0, g); box(0.12, 0.012, L + 0.5, beamM, x, 0.02, 0, g); box(0.01, topY - 2 * pr - 0.04, L + 0.5, beamM, x, 0.03, 0, g);
      }
      // rails
      const n = Math.max(6, Math.floor(L / 0.18));
      for (let i = 0; i < n; i++) {
        const z = -L / 2 + 0.09 + i * (L - 0.18) / (n - 1);
        const rail = cyl(pr, pr, Wd + 0.2, railM, 0, 0, 0, 20, null); rail.rotation.z = Math.PI / 2; rail.position.set(0, topY - pr, z); g.add(rail);
        for (const s of [-1, 1]) { const c = new THREE.Mesh(new THREE.CircleGeometry(pr, 20), mat('pipeEnd', { color: 0x151311, roughness: 0.9 })); c.rotation.y = s * Math.PI / 2; c.position.set(s * (Wd / 2 + 0.1 + 0.001), topY - pr, z); g.add(c); }
      }
      // approaches: caliche ramps up to the rails
      for (const s of [-1, 1]) {
        const shp = new THREE.Shape([[0, 0], [1.4, 0], [0, topY - 0.01]].map(([a, b]) => new THREE.Vector2(a, b)));
        const geo = new THREE.ExtrudeGeometry(shp, { depth: Wd + 0.9, bevelEnabled: false }); geo.translate(0, 0, -(Wd + 0.9) / 2);
        geo.rotateY(s > 0 ? -Math.PI / 2 : Math.PI / 2); K.uvBox(geo, 3);
        const m = new THREE.Mesh(geo, cal); m.position.set(0, 0, s * (L / 2 + 0.3)); g.add(m);
      }
      // wings
      if (o.wings !== false) {
        for (const s of [-1, 1]) {
          const x = s * (Wd / 2 + 0.25), post = (xx, zz, h) => cyl(0.05, 0.05, h, railM, xx, 0, zz, 16, g);
          const zs = [-L / 2 - 0.2, L / 2 + 0.2];
          zs.forEach((z) => { post(x, z, 1.3); const c = new THREE.Mesh(new THREE.SphereGeometry(0.05, 12, 6, 0, TAU, 0, Math.PI / 2), railM); c.position.set(x, 1.3, z); g.add(c); });
          for (const y of [0.45, 0.85, 1.25]) bar([x, y, zs[0]], [x, y, zs[1]], 0.03, railM, g, 12);
          // flared panels outward along the fence line
          for (const z of zs) {
            const ex = x + s * 1.2, ez = z + Math.sign(z) * 0.6;
            post(ex, ez, 1.3);
            for (const y of [0.45, 0.85, 1.25]) bar([x, y, z], [ex, y, ez], 0.028, railM, g, 12);
            bar([x, 0.2, z], [ex, 1.2, ez], 0.02, railM, g, 10);
          }
        }
      }
      return g;
    },
  });
}
