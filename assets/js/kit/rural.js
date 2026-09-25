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
  // sRGB in, sRGB out (a THREE.Color holds linear values, so go through its hex string)
  const rgb = (c, k) => { const h = parseInt(new THREE.Color(c).getHexString(), 16); k = k == null ? 1 : k;
    return 'rgb(' + [h >> 16, (h >> 8) & 255, h & 255].map((v) => Math.max(0, Math.min(255, Math.round(v * k)))).join(',') + ')'; };

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

  /* ---- signed distance body and a surface nets mesher (cattle) ---------------------------
   * Primitives: 'e' ellipsoid (optionally pitched about x), 'r' round cone, 'b' a tapered rounded
   * box along an axis in the yz plane (lateral is world x), and any of them with `sub` carves.
   * The field is meshed in REGIONS of different cell size (head fine, legs fine, barrel coarse),
   * each overlapping the next by two cells, so detail goes where the silhouette needs it. Every
   * superblock of 8 cells evaluates only the primitives that can reach it, which is most of the
   * speed. */
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
  function sdTB(px, py, pz, p) {        // tapered rounded box: half widths s0 -> s1, centre offset c0 -> c1 along n
    const qx = px - p.a[0], qy = py - p.a[1], qz = pz - p.a[2];
    const u = qy * p.d[1] + qz * p.d[2], w = qy * p.n[1] + qz * p.n[2];
    const t = u <= 0 ? 0 : u >= p.L ? 1 : u / p.L;
    const hx = p.s0[0] + (p.s1[0] - p.s0[0]) * t - p.rr, hw = p.s0[1] + (p.s1[1] - p.s0[1]) * t - p.rr;
    const dx = Math.abs(qx) - hx, du = Math.abs(u - p.L / 2) - p.L / 2, dw = Math.abs(w - (p.c0 + (p.c1 - p.c0) * t)) - hw;
    const ox = dx > 0 ? dx : 0, ou = du > 0 ? du : 0, ow = dw > 0 ? dw : 0;
    return Math.sqrt(ox * ox + ou * ou + ow * ow) + Math.min(Math.max(dx, du, dw), 0) - p.rr;
  }
  function smin(a, b, k) { if (k <= 0) return Math.min(a, b); const h = Math.max(k - Math.abs(a - b), 0) / k; return Math.min(a, b) - h * h * k * 0.25; }
  const primD = (p, x, y, z) => p.tt === 0 ? sdEll(x, y, z, p) : p.tt === 1 ? sdRC(x, y, z, p) : sdTB(x, y, z, p);
  // every primitive gets the same fields in the same order, so the hot loop sees one object shape
  const Z3 = [0, 0, 0];
  const normPrim = (p) => ({ tt: p.t === 'e' ? 0 : p.t === 'r' ? 1 : 2, sub: !!p.sub, k: p.k || 0, bc: Z3, br: 0,
    c: p.c || Z3, r: p.r || Z3, ay: p.ay || null, az: p.az || null, a: p.a || Z3, b: p.b || Z3, r1: p.r1 || 0, r2: p.r2 || 0,
    d: p.d || Z3, n: p.n || Z3, L: p.L || 0, s0: p.s0 || Z3, s1: p.s1 || Z3, c0: p.c0 || 0, c1: p.c1 || 0, rr: p.rr || 0 });
  function evalPrims(L, x, y, z) {
    let d = 1e9;
    for (let i = 0; i < L.length; i++) {
      const p = L[i], k = p.k || 0;
      const dx = x - p.bc[0], dy = y - p.bc[1], dz = z - p.bc[2], dd = dx * dx + dy * dy + dz * dz;
      if (p.sub) {
        const lim = p.br * 1.05 + k + (d < 0 ? -d : 0);
        if (d > 1e8 || dd > lim * lim) continue;
        d = -smin(-d, primD(p, x, y, z), k);
      } else {
        const lim = d + k + p.br * 1.05;
        if (d < 1e8 && lim > 0 && dd > lim * lim) continue;
        const di = primD(p, x, y, z);
        d = d > 1e8 ? di : smin(d, di, k);
      }
    }
    return d;
  }
  function buildSDF(prims) {
    prims = prims.map(normPrim);
    prims.forEach((p) => {
      if (p.tt === 0) { p.bc = p.c; p.br = Math.max(p.r[0], p.r[1], p.r[2]); }
      else if (p.tt === 1) { p.bc = [(p.a[0] + p.b[0]) / 2, (p.a[1] + p.b[1]) / 2, (p.a[2] + p.b[2]) / 2];
        p.br = Math.hypot(p.b[0] - p.a[0], p.b[1] - p.a[1], p.b[2] - p.a[2]) / 2 + Math.max(p.r1, p.r2); }
      else { const m = p.L / 2, cm = (p.c0 + p.c1) / 2;
        p.bc = [p.a[0], p.a[1] + p.d[1] * m + p.n[1] * cm, p.a[2] + p.d[2] * m + p.n[2] * cm];
        p.br = Math.hypot(m, Math.max(p.s0[0], p.s1[0]), Math.max(p.s0[1], p.s1[1]) + Math.abs(p.c1 - p.c0) / 2); }
    });
    // carving primitives run last, so they cut what the rest built
    const all = prims.filter((p) => !p.sub).concat(prims.filter((p) => p.sub));
    const f = (x, y, z) => evalPrims(all, x, y, z);
    // the primitives that can matter anywhere inside a ball of radius `rad` about (cx, cy, cz), chosen
    // from `src` (all of them by default): anything farther than a known surface plus its blend is out
    f.near = function (cx, cy, cz, rad, src) {
      src = src || all;
      const add = [], ds = []; let m = 1e9;
      for (const p of src) {
        if (p.sub) continue;
        const dx = cx - p.bc[0], dy = cy - p.bc[1], dz = cz - p.bc[2], lo = Math.sqrt(dx * dx + dy * dy + dz * dz) - p.br * 1.05 - rad;
        if (lo > m + (p.k || 0)) continue;
        const di = primD(p, cx, cy, cz); add.push(p); ds.push(di); if (di + rad * 1.25 < m) m = di + rad * 1.25;
      }
      const L = [];
      for (let i = 0; i < add.length; i++) if (ds[i] - rad * 1.25 < m + (add[i].k || 0) + 0.002) L.push(add[i]);
      for (const p of src) if (p.sub && Math.hypot(cx - p.bc[0], cy - p.bc[1], cz - p.bc[2]) - p.br * 1.05 - rad < (p.k || 0) + 0.01) L.push(p);
      return L;
    };
    return f;
  }
  // Surface nets over a uniform grid. Blocks of 8 cells, then of 4, each keep only the primitives
  // that can reach them, and a block farther from the surface than its own radius is filled with
  // its centre value and never sampled again. Normals come from the field's gradient.
  function surfaceNets(sdf, lo, hi, h) {
    const nx = Math.ceil((hi[0] - lo[0]) / h) + 1, ny = Math.ceil((hi[1] - lo[1]) / h) + 1, nz = Math.ceil((hi[2] - lo[2]) / h) + 1;
    const val = new Float32Array(nx * ny * nz).fill(1), I = (i, j, k) => i + nx * (j + ny * k);
    const bx = Math.ceil(nx / 4), by = Math.ceil(ny / 4), lists = new Array(bx * by * Math.ceil(nz / 4)), BI = (i, j, k) => (i >> 2) + bx * ((j >> 2) + by * (k >> 2));
    const r8 = 3.5 * h * 1.733, r4 = 1.5 * h * 1.733, nearB = [];
    const fill = (i0, j0, k0, n, v) => { if (v > 0) return; for (let k = k0; k < Math.min(nz, k0 + n); k++) for (let j = j0; j < Math.min(ny, j0 + n); j++) for (let i = i0; i < Math.min(nx, i0 + n); i++) val[I(i, j, k)] = v; };
    for (let bk = 0; bk < nz; bk += 8) for (let bj = 0; bj < ny; bj += 8) for (let bi = 0; bi < nx; bi += 8) {
      const cx = lo[0] + (bi + 3.5) * h, cy = lo[1] + (bj + 3.5) * h, cz = lo[2] + (bk + 3.5) * h;
      const L8 = sdf.near(cx, cy, cz, r8 + h);
      const d8 = L8.length ? evalPrims(L8, cx, cy, cz) : 1;
      if (Math.abs(d8) > r8 * 1.25 + h) { fill(bi, bj, bk, 8, d8); continue; }
      for (let qk = bk; qk < Math.min(nz, bk + 8); qk += 4) for (let qj = bj; qj < Math.min(ny, bj + 8); qj += 4) for (let qi = bi; qi < Math.min(nx, bi + 8); qi += 4) {
        const ex = lo[0] + (qi + 1.5) * h, ey = lo[1] + (qj + 1.5) * h, ez = lo[2] + (qk + 1.5) * h;
        const L4 = sdf.near(ex, ey, ez, r4 + h, L8), d4 = L4.length ? evalPrims(L4, ex, ey, ez) : d8;
        if (Math.abs(d4) > r4 * 1.25 + h) { fill(qi, qj, qk, 4, d4); continue; }
        lists[BI(qi, qj, qk)] = L4; nearB.push(qi, qj, qk);
        for (let sk = qk; sk < Math.min(nz, qk + 4); sk += 2) for (let sj = qj; sj < Math.min(ny, qj + 4); sj += 2) for (let si = qi; si < Math.min(nx, qi + 4); si += 2) {
          const d2 = evalPrims(L4, lo[0] + (si + 0.5) * h, lo[1] + (sj + 0.5) * h, lo[2] + (sk + 0.5) * h);
          if (Math.abs(d2) > h * 1.2) { fill(si, sj, sk, 2, d2); continue; }
          for (let k = sk; k < Math.min(nz, sk + 2); k++) for (let j = sj; j < Math.min(ny, sj + 2); j++) for (let i = si; i < Math.min(nx, si + 2); i++)
            val[I(i, j, k)] = evalPrims(L4, lo[0] + i * h, lo[1] + j * h, lo[2] + k * h);
        }
      }
    }
    const cell = new Int32Array((nx - 1) * (ny - 1) * (nz - 1)).fill(-1), C = (i, j, k) => i + (nx - 1) * (j + (ny - 1) * k);
    let verts = new Float32Array(3 << 15), nvx = 0; const vl = [];
    const EA = [0, 2, 4, 6, 0, 1, 4, 5, 0, 1, 2, 3], EB = [1, 3, 5, 7, 2, 3, 6, 7, 4, 5, 6, 7];
    const OX = [0, 1, 0, 1, 0, 1, 0, 1], OY = [0, 0, 1, 1, 0, 0, 1, 1], OZ = [0, 0, 0, 0, 1, 1, 1, 1];
    const cv = new Float32Array(8), OFF = new Int32Array(8);
    for (let c = 0; c < 8; c++) OFF[c] = OX[c] + nx * (OY[c] + ny * OZ[c]);
    // only nodes in a sampled block, or one cell below it, can start a cell or an edge the surface crosses
    const seen = new Uint8Array(nx * ny * nz);
    const eachNear = (fn) => {
      seen.fill(0);
      for (let b = 0; b < nearB.length; b += 3) {
        const i0 = Math.max(0, nearB[b] - 1), j0 = Math.max(0, nearB[b + 1] - 1), k0 = Math.max(0, nearB[b + 2] - 1);
        const i1 = Math.min(nx, nearB[b] + 4), j1 = Math.min(ny, nearB[b + 1] + 4), k1 = Math.min(nz, nearB[b + 2] + 4);
        for (let k = k0; k < k1; k++) for (let j = j0; j < j1; j++) for (let i = i0; i < i1; i++) { const q = I(i, j, k); if (!seen[q]) { seen[q] = 1; fn(i, j, k, q); } }
      }
    };
    eachNear((i, j, k, q) => {
      if (i >= nx - 1 || j >= ny - 1 || k >= nz - 1) return;
      let neg = 0;
      for (let c = 0; c < 8; c++) { cv[c] = val[q + OFF[c]]; if (cv[c] < 0) neg++; }
      if (neg === 0 || neg === 8) return;
      let sx = 0, sy = 0, sz = 0, n = 0;
      for (let e = 0; e < 12; e++) {
        const a = EA[e], b = EB[e];
        if ((cv[a] < 0) === (cv[b] < 0)) continue;
        const tt = cv[a] / (cv[a] - cv[b]);
        sx += OX[a] + (OX[b] - OX[a]) * tt; sy += OY[a] + (OY[b] - OY[a]) * tt; sz += OZ[a] + (OZ[b] - OZ[a]) * tt; n++;
      }
      if (nvx * 3 + 3 > verts.length) { const g2 = new Float32Array(verts.length * 2); g2.set(verts); verts = g2; }
      cell[C(i, j, k)] = nvx; verts[nvx * 3] = lo[0] + (i + sx / n) * h; verts[nvx * 3 + 1] = lo[1] + (j + sy / n) * h; verts[nvx * 3 + 2] = lo[2] + (k + sz / n) * h; nvx++;
      vl.push(lists[BI(i, j, k)] || lists[BI(Math.min(nx - 1, i + 1), Math.min(ny - 1, j + 1), Math.min(nz - 1, k + 1))] || null);
    });
    let idx = new Uint32Array(6 << 15), ni = 0;
    const quad = (a, b, c, d, flip) => { if (a < 0 || b < 0 || c < 0 || d < 0) return;
      if (ni + 6 > idx.length) { const g2 = new Uint32Array(idx.length * 2); g2.set(idx); idx = g2; }
      idx[ni] = a; idx[ni + 3] = a; if (flip) { idx[ni + 1] = c; idx[ni + 2] = b; idx[ni + 4] = d; idx[ni + 5] = c; } else { idx[ni + 1] = b; idx[ni + 2] = c; idx[ni + 4] = c; idx[ni + 5] = d; } ni += 6; };
    eachNear((i, j, k, q) => {
      const v0 = val[q] < 0;
      if (i < nx - 1 && j > 0 && k > 0 && j < ny - 1 && k < nz - 1) { const v1 = val[q + 1] < 0; if (v0 !== v1) quad(cell[C(i, j - 1, k - 1)], cell[C(i, j, k - 1)], cell[C(i, j, k)], cell[C(i, j - 1, k)], v1); }
      if (j < ny - 1 && i > 0 && k > 0 && i < nx - 1 && k < nz - 1) { const v1 = val[q + nx] < 0; if (v0 !== v1) quad(cell[C(i - 1, j, k - 1)], cell[C(i - 1, j, k)], cell[C(i, j, k)], cell[C(i, j, k - 1)], v1); }
      if (k < nz - 1 && i > 0 && j > 0 && i < nx - 1 && j < ny - 1) { const v1 = val[q + nx * ny] < 0; if (v0 !== v1) quad(cell[C(i - 1, j - 1, k)], cell[C(i, j - 1, k)], cell[C(i, j, k)], cell[C(i - 1, j, k)], v1); }
    });
    // project onto the surface; tetrahedral gradient, four samples give the value and the normal together.
    // Each vertex first narrows its block's list to the primitives within reach of its own samples.
    const nv = nvx, P = new Float32Array(nv * 3), N = new Float32Array(nv * 3), e = h * 0.35, SUB = [], DS = new Float64Array(256);
    for (let v = 0; v < nv; v++) {
      const x = verts[v * 3], y = verts[v * 3 + 1], z = verts[v * 3 + 2], L0 = vl[v];
      let L = L0;
      if (L0 && L0.length > 2 && L0.length <= 256) {
        let m = 1e9;
        for (let i = 0; i < L0.length; i++) { const p = L0[i]; if (p.sub) { DS[i] = -1e9; continue; } DS[i] = primD(p, x, y, z); if (DS[i] < m) m = DS[i]; }
        SUB.length = 0; const reach = e * 2.2;
        for (let i = 0; i < L0.length; i++) { const p = L0[i]; if (p.sub ? Math.hypot(x - p.bc[0], y - p.bc[1], z - p.bc[2]) - p.br * 1.05 < p.k + reach : DS[i] - reach < m + reach + p.k) SUB.push(p); }
        L = SUB;
      }
      const F = L ? (a1, a2, a3) => evalPrims(L, a1, a2, a3) : sdf;
      const a = F(x + e, y - e, z - e), b = F(x - e, y - e, z + e), c = F(x - e, y + e, z - e), d4 = F(x + e, y + e, z + e);
      let gx = a - b - c + d4, gy = -a - b + c + d4, gz = -a + b - c + d4;
      const gl = Math.sqrt(gx * gx + gy * gy + gz * gz) || 1; gx /= gl; gy /= gl; gz /= gl;
      const d = Math.max(-h, Math.min(h, (a + b + c + d4) / 4));
      P[v * 3] = x - gx * d; P[v * 3 + 1] = y - gy * d; P[v * 3 + 2] = z - gz * d; N[v * 3] = gx; N[v * 3 + 1] = gy; N[v * 3 + 2] = gz;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(P, 3)); g.setAttribute('normal', new THREE.BufferAttribute(N, 3));
    g.setIndex(nv > 65535 ? new THREE.BufferAttribute(idx.slice(0, ni), 1) : new THREE.BufferAttribute(Uint16Array.from(idx.subarray(0, ni)), 1));
    return g;
  }

  /* ================================================================================ CATTLE
   * A Hereford or a Texas longhorn, as a cow, a steer or a bull. The body is built the way a beef
   * animal is: a deep rectangular barrel with a level topline, hooks and pins and a tailhead you
   * can see, a brisket and dewlap hanging forward between the legs, a flank that climbs to the
   * stifle, muscled forearms and gaskins over clean cannons. The head is a wedge, broad and flat at
   * the forehead, narrowing down the face and flaring to a wide square muzzle with a moist nose pad
   * and flared nostrils, carried low and forward on a thick neck.
   * The mesh is cached per breed and sex, so a herd costs one field build per kind of animal. */
  function cattleSpec(breed, sex) {
    const LH = breed === 'longhorn', bull = sex === 'bull', cow = sex === 'cow';
    const S = LH
      ? { H: 1.42, B: 0.8, W: 0.225, Lf: 0.6, Lr: -0.8, hs: 1.04, HL: 0.58, pitch: 1.0, hw: 0.86, th: 0.7, knee: 0.47, hock: 0.57, rump: 0.14, lr: 0.92, bk: 0.75, pd: 0.8, drop: 0.16 }
      : { H: 1.3, B: 0.6, W: 0.3, Lf: 0.62, Lr: -0.72, hs: 1.05, HL: 0.46, pitch: 0.98, hw: 1.12, th: 1, knee: 0.41, hock: 0.5, rump: 0.03, lr: 1.06, bk: 1, pd: 1, drop: 0.2 };
    if (bull) { S.H += 0.05; S.W += 0.025; S.hw *= 1.06; S.hs *= 1.06; S.B -= 0.02; }
    if (sex === 'steer' && !LH) { S.W += 0.01; }
    const { H, B, W, Lf, Lr, HL, hw, lr } = S, s = HL / 0.5;
    const P = [];
    const ang = (a) => ({ ay: [0, Math.cos(a), Math.sin(a)], az: [0, -Math.sin(a), Math.cos(a)] });
    const E = (c, r, k, a, sub) => P.push(Object.assign({ t: 'e', c, r, k: k || 0, sub: !!sub }, a ? ang(a) : {}));
    const R = (a, b, r1, r2, k) => P.push({ t: 'r', a, b, r1, r2, k: k || 0 });
    const T = (a, d, n, L, s0, s1, c0, c1, rr, k, sub) => P.push({ t: 'b', a, d, n, L, s0, s1, c0, c1, rr, k: k || 0, sub: !!sub });
    const Z = [0, 0, 1], Y = [0, 1, 0];
    /* barrel: deep, rectangular, level topped, with a round paunch under the ribs */
    T([0, (H + B) / 2 + 0.06, Lr + 0.34], Z, Y, Lf - 0.08 - (Lr + 0.34), [W * 0.98, (H - B) / 2 - 0.06], [W * 0.94, (H - B) / 2 - 0.02], 0.02, -0.035, 0.2, 0);
    E([0, B + 0.25 * S.pd + 0.02 * (1 - S.pd), 0.02], [W * 1.04, 0.28 * S.pd, 0.46], 0.2);
    /* hindquarter: a box whose floor is the flank rising to the stifle, the round down the thigh */
    T([0, H - 0.23, Lr], Z, Y, 0.52, [W * 0.8, 0.21], [W * 0.95, 0.23], -S.rump, 0, 0.15, 0.16);
    for (const q of [-1, 1]) {
      E([q * W * 0.6, B + 0.38, Lr + 0.15], [0.14 * S.th + 0.03, 0.32, 0.21], 0.14, 0.1);           // round, thigh
      R([q * W * 0.72, H - 0.2, Lr + 0.3], [q * (W - 0.04), B + 0.14, Lr + 0.4], 0.12 * S.th + 0.02, 0.075, 0.1); // stifle, forward of the thigh
      E([q * (W - 0.02), H - 0.09, Lr + 0.36], [0.055, 0.045, 0.055], 0.05);                        // hooks
      E([q * 0.1, H - 0.1 - S.rump, Lr - 0.02], [0.05, 0.05, 0.05], 0.05);                          // pins
      E([q * (W - 0.09), H - 0.4, Lf - 0.2], [0.1, 0.34, 0.22], 0.18, -0.38);                        // shoulder blade
      E([q * (W - 0.05), B + 0.32, Lf - 0.03], [0.08, 0.09, 0.08], 0.08);                           // point of shoulder
    }
    R([0, H - 0.02 - S.rump * 0.5, Lr + 0.12], [0, H - 0.1 - S.rump, Lr - 0.07], 0.07, 0.05, 0.06);   // tailhead
    E([0, H - 0.08, Lf - 0.3], [0.12, 0.06, 0.2], 0.1);                                                 // withers
    E([0, B + 0.06, Lf + 0.02], [0.16 * S.bk, 0.16, 0.18 * S.bk], 0.12);                               // brisket, forward and low
    /* head frame: poll, a down the face, w out of the face */
    const poll = [0, H - S.drop, Lf + 0.42], hs = S.hs;
    const ax = [0, -Math.sin(S.pitch), Math.cos(S.pitch)], aw = [0, Math.cos(S.pitch), Math.sin(S.pitch)];
    // head units: everything in the head frame is scaled by hs, so one number sizes the whole head
    const at = (u, w, x) => [(x || 0) * hs, poll[1] + (ax[1] * u + aw[1] * w) * hs, poll[2] + (ax[2] * u + aw[2] * w) * hs];
    const HT = (u0, u1, s0, s1, c0, c1, rr, k, sub, x) => T(at(u0, 0, x), ax, aw, (u1 - u0) * hs, [s0[0] * hs, s0[1] * hs], [s1[0] * hs, s1[1] * hs], c0 * hs, c1 * hs, rr * hs, k * hs, sub);
    const HE = (u, w, x, r, k, sub) => P.push({ t: 'e', c: at(u, w, x), r: [r[0] * hs, r[1] * hs, r[2] * hs], ay: ax, az: aw, k: (k || 0) * hs, sub: !!sub });
    /* neck: thick, carried forward, a throat under it and a dewlap to the brisket */
    const nb = [0, H - 0.31, Lf - 0.25], na = at(0.1, -0.16);
    R(nb, na, bull ? 0.33 : 0.3, LH ? 0.15 : 0.165, 0.1);
    R([0, B + 0.3, Lf + 0.05], at(0.1, -0.21), 0.13, 0.095, 0.1);                                     // throat, into the angle of the jaw
    { const th = at(0.12, -0.23), mid = [0, (th[1] + B + 0.1) / 2, (th[2] + Lf + 0.12) / 2];              // dewlap, throat to brisket
      E(mid, [LH ? 0.035 : 0.045, Math.hypot(th[1] - B - 0.1, th[2] - Lf - 0.12) / 2 + 0.03, LH ? 0.07 : 0.1], 0.08, -Math.atan2(th[2] - Lf - 0.12, th[1] - B - 0.1)); }
    if (bull) { const cm = [0, (nb[1] + na[1]) / 2 + 0.2, (nb[2] + na[2]) / 2 - 0.02];                  // crest: the neck arches, it does not hump
      E(cm, [0.13, 0.1, 0.34], 0.16, -Math.atan2(na[1] - nb[1], na[2] - nb[2]) * 0.6); }
    /* skull and face: a wedge, flat in front. Widest across the eye sockets, narrowing down the
       face, then flaring again into the square muzzle */
    HT(-0.03, 0.19, [0.105 * hw, 0.08], [0.12 * hw, 0.075], -0.08, -0.075, 0.045, 0.03);                  // forehead, poll to orbits
    HT(0.15, 0.44 * s, [0.105 * hw, 0.06], [0.072 * hw, 0.05], -0.06, -0.05, 0.035, 0.05);                 // face, nasal bridge
    HT(0.08, 0.42 * s, [0.085 * hw, 0.095], [0.06 * hw, 0.055], -0.185, -0.125, 0.045, 0.06);              // jaw
    HT(0.405 * s, 0.515 * s, [0.094 * hw, 0.068], [0.096 * hw, 0.066], -0.075, -0.075, 0.042, 0.045);     // muzzle, wide and square
    HE(0.475 * s, -0.148, 0, [0.055, 0.045, 0.028], 0.03);                                                  // chin, lower lip
    HE(-0.025, -0.06, 0, LH ? [0.12 * hw, 0.045, 0.06] : [0.095, 0.05, 0.068], 0.04);                       // poll
    for (const q of [-1, 1]) {
      HE(0.2, -0.165, q * 0.07 * hw, [0.035, 0.1, 0.07], 0.04);                                             // cheek, the big chewing muscle
      HE(0.13, -0.03, q * 0.108 * hw, [0.04, 0.035, 0.032], 0.025);                                         // brow ridge
      HE(0.175, -0.07, q * 0.105 * hw, [0.035, 0.036, 0.032], 0.02);                                        // eye socket, lids
      HE(0.49 * s, -0.03, q * 0.055 * hw, [0.034, 0.035, 0.03], 0.022);                                     // nostril flare
      HE(0.518 * s, -0.036, q * 0.058 * hw, [0.01, 0.03, 0.024], 0.008, true);                              // nostril, a slit
    }
    /* legs: the knee and hock heights set the stance */
    const fx = Math.max(0.16, W * 0.63), hx = Math.max(0.15, W * 0.6), fz = Lf - 0.1, hz = Lr + 0.05, kn = S.knee, hk = S.hock;
    for (const q of [-1, 1]) {
      R([q * (W - 0.07), B + 0.08, Lf - 0.14], [q * fx, kn + 0.02, fz], 0.1 * lr, 0.056 * lr, 0.07);       // arm, forearm
      E([q * (fx + 0.005), kn + (B - kn) * 0.55, fz + 0.01], [0.068 * lr, 0.13, 0.078 * lr], 0.05);        // forearm muscle
      E([q * fx, kn, fz + 0.008], [0.056 * lr, 0.058, 0.056 * lr], 0.03);                                   // knee
      R([q * fx, kn - 0.01, fz], [q * fx, 0.125, fz + 0.01], 0.047 * lr, 0.042 * lr, 0.02);                 // cannon
      R([q * fx, kn - 0.05, fz - 0.025], [q * fx, 0.14, fz - 0.02], 0.022 * lr, 0.02 * lr, 0.02);           // flexor tendon
      E([q * fx, 0.115, fz + 0.005], [0.053 * lr, 0.048, 0.056 * lr], 0.02);                               // fetlock
      R([q * fx, 0.11, fz + 0.01], [q * fx, 0.055, fz + 0.04], 0.045 * lr, 0.047 * lr, 0.015);             // pastern
      R([q * W * 0.62, B + 0.1, Lr + 0.34], [q * hx, hk + 0.02, hz], 0.09 * lr, 0.05 * lr, 0.06);           // stifle to hock, sloping back
      E([q * hx, hk + 0.16, hz + 0.1], [0.065 * lr, 0.13, 0.08 * lr], 0.05, 0.75);                         // gaskin
      R([q * hx, hk + 0.2, hz + 0.02], [q * hx, hk + 0.01, hz - 0.04], 0.028 * lr, 0.034 * lr, 0.03);      // hamstring to the point of hock
      E([q * hx, hk, hz - 0.01], [0.045 * lr, 0.06, 0.055 * lr], 0.03);                                     // hock
      R([q * hx, hk - 0.02, hz], [q * hx, 0.125, hz + 0.05], 0.049 * lr, 0.042 * lr, 0.02);                 // cannon
      E([q * hx, 0.115, hz + 0.05], [0.053 * lr, 0.048, 0.056 * lr], 0.02);                                 // fetlock
      R([q * hx, 0.11, hz + 0.055], [q * hx, 0.055, hz + 0.085], 0.045 * lr, 0.047 * lr, 0.015);            // pastern
    }
    /* sex */
    if (cow) E([0, B + 0.02, Lr + 0.34], LH ? [0.08, 0.06, 0.09] : [0.1, 0.07, 0.11], 0.07);                 // udder, small: beef
    else E([0, B + 0.0, 0.02], [0.035, 0.04, 0.09], 0.06, -0.2);                                            // sheath
    if (bull) E([0, B + 0.02, Lr + 0.2], [0.065, 0.11, 0.07], 0.06);                                        // scrotum
    Object.assign(S, { P, poll, ax, aw, at, fx, hx, fz, hz, s, nb, na, LH, sex });
    return S;
  }
  // value noise like makeNoise, without allocating per call (the coat samples it ~200k times)
  function cattleNoise(seed) {
    const rr = K.rng(seed), perm = new Float32Array(4096);
    for (let i = 0; i < 4096; i++) perm[i] = rr();
    return function (x, y, z) {
      const X = Math.floor(x), Y = Math.floor(y), Z = Math.floor(z);
      let u = x - X, v = y - Y, w = z - Z; u = u * u * (3 - 2 * u); v = v * v * (3 - 2 * v); w = w * w * (3 - 2 * w);
      const hx0 = X * 73856093, hx1 = (X + 1) * 73856093, hy0 = Y * 19349663, hy1 = (Y + 1) * 19349663, hz0 = Z * 83492791, hz1 = (Z + 1) * 83492791;
      const a = perm[((hx0 ^ hy0 ^ hz0) >>> 0) & 4095], b = perm[((hx1 ^ hy0 ^ hz0) >>> 0) & 4095], c = perm[((hx0 ^ hy1 ^ hz0) >>> 0) & 4095], d = perm[((hx1 ^ hy1 ^ hz0) >>> 0) & 4095];
      const e = perm[((hx0 ^ hy0 ^ hz1) >>> 0) & 4095], f = perm[((hx1 ^ hy0 ^ hz1) >>> 0) & 4095], g = perm[((hx0 ^ hy1 ^ hz1) >>> 0) & 4095], h = perm[((hx1 ^ hy1 ^ hz1) >>> 0) & 4095];
      const ab = a + (b - a) * u, cd = c + (d - c) * u, ef = e + (f - e) * u, gh = g + (h - g) * u;
      const lo = ab + (cd - ab) * v, hi = ef + (gh - ef) * v;
      return lo + (hi - lo) * w;
    };
  }
  // head coordinates of a point: u down the face, w out of it
  const headUW = (S, x, y, z) => { const qy = y - S.poll[1], qz = z - S.poll[2]; return [(qy * S.ax[1] + qz * S.ax[2]) / S.hs, (qy * S.aw[1] + qz * S.aw[2]) / S.hs]; };
  const CATTLE_MESH = new Map(), CATTLE_H = 0.016;
  function cattleMesh(breed, sex) {
    const key = breed + '|' + sex;
    if (CATTLE_MESH.has(key)) return CATTLE_MESH.get(key);
    const S = cattleSpec(breed, sex), sdf = buildSDF(S.P);
    const X = S.W + 0.14;
    const geo = surfaceNets(sdf, [-X, -0.02, S.Lr - 0.2], [X, S.H + 0.2, S.poll[2] + S.HL * 0.9 + 0.1], CATTLE_H);
    // a Hereford's curly poll: the forehead's hair raised into tufts
    if (!S.LH) {
      const nz = cattleNoise(911), p = geo.attributes.position, n = geo.attributes.normal;
      for (let i = 0; i < p.count; i++) {
        if (p.getZ(i) < S.poll[2] - 0.2) continue;
        const [u, w] = headUW(S, p.getX(i), p.getY(i), p.getZ(i));
        if (u > 0.16 || u < -0.1 || w < -0.05) continue;
        const k = (1 - smooth01(0.06, 0.16, u)) * smooth01(-0.1, -0.04, u) * smooth01(-0.05, -0.015, w);
        const x = p.getX(i), y = p.getY(i), z = p.getZ(i), d = (nz(x * 120, y * 120, z * 120) - 0.45) * 0.0045 * k;
        p.setXYZ(i, x + n.getX(i) * d, y + n.getY(i) * d, z + n.getZ(i) * d);
      }
    }
    const out = { S, sdf, geo };
    CATTLE_MESH.set(key, out); return out;
  }
  // Short hair: a screen space bump from an object space streak pattern that lies head to tail on
  // the body and down the legs, fading out before it can alias. Plus a wet nose (vertex `wet`).
  function hideMaterial() {
    if (MATS.has('hideHair')) return MATS.get('hideHair');
    const m = new THREE.MeshPhysicalMaterial({ color: 0xffffff, vertexColors: true, roughness: 0.75, metalness: 0,
      sheen: 0.35, sheenRoughness: 0.55, sheenColor: 0xcdb89a, specularIntensity: 0.6 });
    m.onBeforeCompile = (sh) => {
      sh.vertexShader = sh.vertexShader
        .replace('#include <common>', '#include <common>\nattribute float wet;\nvarying float vWet;\nvarying vec3 vOP;\nvarying vec3 vON;')
        .replace('#include <begin_vertex>', '#include <begin_vertex>\nvWet = wet; vOP = position; vON = normal;');
      sh.fragmentShader = sh.fragmentShader
        .replace('#include <common>', `#include <common>
varying float vWet; varying vec3 vOP; varying vec3 vON;
float hH(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float hN(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3. - 2. * f);
  return mix(mix(hH(i), hH(i + vec2(1, 0)), f.x), mix(hH(i + vec2(0, 1)), hH(i + vec2(1, 1)), f.x), f.y); }
float hairStreak(vec2 along_across){ vec2 p = along_across;
  return hN(vec2(p.x * 28., p.y * 230.)) * 0.6 + hN(vec2(p.x * 70., p.y * 520.) + 17.) * 0.4; }
float hairH(vec3 p, vec3 n){
  vec3 w = pow(abs(n), vec3(4.)); w /= (w.x + w.y + w.z);
  float leg = 1. - smoothstep(0.5, 0.7, p.y);
  // sides: hair runs along z on the body, down y on the legs
  float sx = mix(hairStreak(vec2(p.z, p.y + 0.3 * p.z)), hairStreak(vec2(p.y, p.z)), leg);
  float sy = hairStreak(vec2(p.z, p.x));
  float sz = mix(hairStreak(vec2(p.x, p.y)), hairStreak(vec2(p.y, p.x)), 0.5);
  float coat = hN(p.xz * 45. + p.y * 30.) * 0.35;
  return (sx * w.x + sy * w.y + sz * w.z + coat) * 0.0009;
}
vec3 hairBump(vec3 sp, vec3 sn, vec2 dH, float fd){
  vec3 sX = normalize(dFdx(sp)), sY = normalize(dFdy(sp));
  vec3 r1 = cross(sY, sn), r2 = cross(sn, sX); float det = dot(sX, r1) * fd;
  return normalize(abs(det) * sn - sign(det) * (dH.x * r1 + dH.y * r2));
}`)
        .replace('#include <roughnessmap_fragment>', '#include <roughnessmap_fragment>\nroughnessFactor = mix(roughnessFactor, 0.26, vWet);')
        .replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
{ float fw = length(fwidth(vOP)); float amp = (1. - smoothstep(0.0015, 0.005, fw)) * (1. - vWet);
  if (amp > 0.001) { float hh = hairH(vOP, normalize(vON)) * amp;
    vec2 dH = vec2(dFdx(hh) / max(length(dFdx(vOP)), 1e-5), dFdy(hh) / max(length(dFdy(vOP)), 1e-5));
    normal = hairBump(-vViewPosition, normal, dH, faceDirection); } }`);
    };
    m.customProgramCacheKey = () => 'txkit-cattle-hide-1';
    // a closed smooth body under soft (VSM) shadows streaks where it shadows itself; casting from the
    // back faces moves the occluder to the far side of the hide
    m.shadowSide = THREE.BackSide;
    MATS.set('hideHair', m); return m;
  }
  // a cupped, pointed cattle ear, x along its length, the cup opening toward +y
  function earGeometry(L, Wd) {
    const nu = 12, nv = 10, pos = [], idx = [], col = [];
    for (let i = 0; i <= nu; i++) {
      const u = i / nu, wd = Wd * Math.pow(Math.sin(Math.PI * Math.min(1, 0.12 + u * 0.95)), 0.75) * (1 - 0.2 * u) + 0.004;
      for (let j = 0; j <= nv; j++) {
        const v = j / nv * 2 - 1;
        pos.push(L * u, -0.55 * wd * (1 - v * v) * Math.sin(Math.PI * Math.min(1, u * 1.15)) + 0.15 * wd * v * v, v * wd);
        const edge = smooth01(0.55, 0.95, Math.abs(v)) * 0.8 + smooth01(0.8, 1, u) * 0.4;
        col.push(0.55 + 0.3 * edge, 0.36 + 0.42 * edge, 0.32 + 0.4 * edge);
      }
    }
    for (let i = 0; i < nu; i++) for (let j = 0; j < nv; j++) { const a = i * (nv + 1) + j, b = a + nv + 1; idx.push(a, a + 1, b, b, a + 1, b + 1); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
    g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
    return g;
  }
  // one claw of a cloven hoof: a half cone, flat inside, the toe drawn forward and the wall sloped
  let CLAW = null;
  function clawGeometry() {
    if (CLAW) return CLAW;
    const g = new THREE.LatheGeometry([[0, 0], [0.036, 0], [0.037, 0.006], [0.031, 0.04], [0.02, 0.066], [0, 0.07]].map((p) => new THREE.Vector2(p[0], p[1])), 14, 0, Math.PI);
    deform(g, (v) => { if (v.z > 0) v.z *= 1.55; v.z -= v.y * 0.55; }, false);
    g.computeVertexNormals(); CLAW = g; return g;
  }
  K.define('cattle', {
    size: [0.8, 1.55, 2.5],
    options: { breed: 'hereford', sex: 'auto', horns: 'auto', spread: 1.9, coat: 'auto' },
    note: 'A beef animal standing, facing +z, one smooth body from a signed distance field: a deep rectangular barrel with a level topline, hooks, pins and tailhead, brisket and dewlap, a flank rising to the stifle, muscled forearms and gaskins, cloven hooves, a wedge head with a wide square muzzle, wet nose and flared nostrils, short hair on the hide. breed hereford (red, white face, crest, underline, socks and switch; polled unless horns true, which gives short horns sweeping out and forward) or longhorn (rangy; lyre horns spread in metres tip to tip, coat auto | red | paint | brindle | dun | speckle). sex auto (hereford cow, longhorn steer) | cow (small beef udder) | steer | bull (crest, heavier neck and head).',
    make(o, r) {
      const breed = o.breed === 'longhorn' ? 'longhorn' : 'hereford', LH = breed === 'longhorn';
      const sex = ['cow', 'steer', 'bull'].includes(o.sex) ? o.sex : (LH ? 'steer' : 'cow');
      const { S, sdf, geo: base } = cattleMesh(breed, sex);
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', base.attributes.position); geo.setAttribute('normal', base.attributes.normal); geo.setIndex(base.index);
      /* ---- coat ---- */
      const nz = cattleNoise((o.seed || 1) * 17 + 3), pos = geo.attributes.position, col = new Float32Array(pos.count * 3), wet = new Float32Array(pos.count);
      const coats = ['paint', 'red', 'speckle', 'brindle', 'dun', 'paint'];
      const coat = !LH ? 'hereford' : (o.coat && o.coat !== 'auto' && coats.includes(o.coat) ? o.coat : coats[Math.floor(r() * 6)]);
      const redHex = LH ? [0x8b3a1c, 0x7a2f16, 0x93481f][Math.floor(r() * 3)] : [0x6e2914, 0x773018, 0x652511][Math.floor(r() * 3)];
      const red = new THREE.Color(redHex), white = new THREE.Color(0xe6ddcc), black = new THREE.Color(0x1d1815);
      const dun = new THREE.Color(0xb3915f), brown = new THREE.Color(0x4a2b1a), dirt = new THREE.Color(0x7d6a52);
      const noseLH = coat === 'paint' || coat === 'speckle' ? 0x9c6a62 : 0x2b2522;
      const nose = new THREE.Color(LH ? noseLH : 0x7d5752), nostril = new THREE.Color(0x2a1714);
      const patch = new THREE.Color(r() < 0.55 ? redHex : 0x231c19);
      const redEyes = !LH && r() < 0.45;
      const c = new THREE.Color(), tmp = new THREE.Color();
      const segDist = (px, py, pz, a, b) => { const bx = b[0] - a[0], by = b[1] - a[1], bz = b[2] - a[2];
        const t = Math.max(0, Math.min(1, ((px - a[0]) * bx + (py - a[1]) * by + (pz - a[2]) * bz) / (bx * bx + by * by + bz * bz)));
        return Math.hypot(px - a[0] - bx * t, py - a[1] - by * t, pz - a[2] - bz * t); };
      // the plane behind the jaw where a white face ends, slanting back down the throat
      const nd = [S.na[0] - S.nb[0], S.na[1] - S.nb[1], S.na[2] - S.nb[2]], nl = Math.hypot(...nd); nd[0] /= nl; nd[1] /= nl; nd[2] /= nl;
      const crestA = S.at(-0.03, -0.06), crestB = [0, S.H + 0.01, S.Lf - 0.34];
      const eyeUW = [0.175, -0.07];
      const edge = 0.02;                                            // a colour border is a hair line, not an airbrush
      for (let i = 0; i < pos.count; i++) {
        const x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i), ny = base.attributes.normal.getY(i);
        const n1 = nz(x * 9, y * 9, z * 9) * 0.55 + nz(x * 26, y * 26, z * 26) * 0.3 + nz(x * 70, y * 70, z * 70) * 0.15;
        const n2 = nz(x * 2.2 + 11, y * 2.2, z * 2.2) * 0.75 + nz(x * 11 + 5, y * 11, z * 11) * 0.25, n3 = nz(x * 60, y * 60, z * 60);
        const rag = (n1 - 0.5) * 0.09;
        const [hu, hw2] = headUW(S, x, y, z), hx = x / S.hs;
        const inHead = z > S.Lf + 0.1 && hu > -0.12;
        let w = 0;
        if (coat === 'hereford') {
          c.copy(red).multiplyScalar(0.86 + n1 * 0.26);
          const along = (x - S.na[0]) * nd[0] + (y - S.na[1]) * nd[1] + (z - S.na[2]) * nd[2];
          const below = S.na[1] - y;                                   // the throat carries the white further back
          const face = smooth01(-edge, edge, along + 0.05 + Math.max(0, below) * 0.55 + rag);
          const crest = 1 - smooth01(0.055 - edge, 0.055 + edge, segDist(x, y, z, crestA, crestB) + rag * 0.8);
          const topSide = y > S.H - 0.25 || z > S.Lf - 0.2 ? 1 : 0;
          const under = (1 - smooth01(S.B + 0.07 - edge, S.B + 0.07 + edge, y + rag * 1.3)) * smooth01(S.Lr + 0.2, S.Lr + 0.34, z)
            * Math.max(1 - smooth01(-0.55, -0.25, ny), 1 - smooth01(0.12, 0.16, Math.abs(x)));
          const chest = (1 - smooth01(0.11 - edge, 0.11 + edge, Math.abs(x) + rag)) * smooth01(S.Lf - 0.35, S.Lf - 0.2, z) * (1 - smooth01(S.B + 0.42, S.B + 0.46, y + rag));
          const socks = 1 - smooth01(S.knee + 0.04 - edge, S.knee + 0.04 + edge, y + rag * 1.4);
          w = Math.max(face, crest * topSide, under, chest, socks);
          if (redEyes && inHead) { const ep = Math.hypot(Math.abs(hx) - 0.105 * S.hw, hu - eyeUW[0], hw2 - eyeUW[1]);
            w *= smooth01(0.045 - edge, 0.045 + edge, ep + rag * 0.6); }
          tmp.copy(white).multiplyScalar(0.9 + n1 * 0.12);
          c.lerp(tmp, w);
        } else {
          const base2 = coat === 'dun' ? dun : coat === 'brindle' ? brown : coat === 'speckle' ? white : red;
          c.copy(base2).multiplyScalar(0.84 + n1 * 0.28);
          if (coat === 'paint') { const p = smooth01(0.53 - 0.03, 0.53 + 0.03, n2 + rag * 1.4); c.lerp(tmp.copy(white).multiplyScalar(0.92 + n1 * 0.1), p); w = p; }
          if (coat === 'speckle') { const p = smooth01(0.57, 0.6, n2 + rag); c.lerp(patch, p); const sp = nz(x * 38, y * 38, z * 38) + (n3 - 0.5) * 0.2; if (sp > 0.7) c.lerp(patch, 0.85); }
          if (coat === 'brindle') { const st = nz(x * 3 + n1 * 2, y * 24, z * 3); c.lerp(black, smooth01(0.48, 0.58, st) * 0.8); }
          if (coat === 'red') { const p = smooth01(0.62, 0.65, n2 + rag); c.lerp(white, p * (y < S.B + 0.15 ? 1 : 0.35)); w = p; }
          if (coat === 'dun') { c.lerp(brown, (1 - smooth01(0.25, 0.45, y)) * 0.6); }
          // dark points on the longhorn's muzzle and ear edges, darker poll
          if (inHead && hu > 0.36 * S.s) c.lerp(black, 0.25 * (1 - w));
        }
        // shade: the underside and the legs darker, grime at the fetlocks
        const underK = 1 - 0.16 * (1 - smooth01(-0.6, 0.1, ny)) * (1 - smooth01(S.B, S.B + 0.4, y));
        c.multiplyScalar(underK * (1 - 0.1 * (1 - smooth01(S.knee - 0.1, S.B, y))));
        c.lerp(dirt, 0.4 * (1 - smooth01(0.06, 0.2, y + (n1 - 0.5) * 0.06)));
        // muzzle: nose pad, nostrils, the mouth line
        let wt = 0;
        if (inHead && hu > 0.4 * S.s) {
          const pad = smooth01(0.47 * S.s, 0.49 * S.s, hu + (n3 - 0.5) * 0.01) * smooth01(-0.1, -0.08, hw2) * (1 - smooth01(0.085, 0.1, Math.abs(hx)));
          c.lerp(tmp.copy(nose).multiplyScalar(0.9 + n3 * 0.2), pad); wt = pad;
          const hole = 1 - smooth01(0.008, 0.02, Math.hypot((Math.abs(hx) - 0.058 * S.hw - (hw2 + 0.036) * 0.35) * 1.4, (hu - 0.518 * S.s) * 0.8, (hw2 + 0.036) * 0.45));
          c.lerp(nostril, hole * 0.9);
          const mouth = 1 - smooth01(0.003, 0.008, Math.abs(hw2 + 0.122));
          c.lerp(nostril, mouth * smooth01(0.42 * S.s, 0.46 * S.s, hu) * 0.4);
        }
        // the eye rim
        if (inHead) { const er = Math.hypot(Math.abs(hx) - 0.105 * S.hw, hu - eyeUW[0], hw2 - eyeUW[1]); c.lerp(black, (1 - smooth01(0.028, 0.04, er)) * 0.7); }
        // the udder and sheath are bare and pink
        if (sex === 'cow' && y < S.B + 0.05 && Math.abs(z - (S.Lr + 0.34)) < 0.14 && Math.abs(x) < 0.12) c.lerp(tmp.set(0xc99c8c), (1 - smooth01(S.B - 0.02, S.B + 0.05, y)) * 0.8);
        if (y < 0.075) c.lerp(black, 0.35);
        c.multiplyScalar(0.95 + n3 * 0.1);
        col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b; wet[i] = wt;
      }
      geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
      geo.setAttribute('wet', new THREE.BufferAttribute(wet, 1));
      const g = new THREE.Group(), outer = new THREE.Group(); outer.add(g);
      const body = new THREE.Mesh(geo, hideMaterial()); g.add(body);
      // find the surface along a ray from inside the body (for eyes, ears, horn roots)
      const onSurface = (from, dir) => { const p = new V3(...from), d = new V3(...dir).normalize();
        let sd = sdf(p.x, p.y, p.z), n = 0;
        while (sd < 0 && n++ < 200) { p.addScaledVector(d, Math.max(0.002, -sd)); sd = sdf(p.x, p.y, p.z); }
        for (let i = 0; i < 12; i++) { p.addScaledVector(d, -sd); sd = sdf(p.x, p.y, p.z); }
        return p; };
      /* eyes: dark, wet, set in the lids under the brow */
      const lidM = mat('cattleLid' + breed, { color: LH ? 0x2a211c : 0x4a2a20, roughness: 0.75 });
      const eyeM = mat('cattleEye', { color: 0x1c110a, roughness: 0.05, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.03 }, true);
      for (const q of [-1, 1]) {
        const c0 = S.at(eyeUW[0], eyeUW[1], q * 0.06 * S.hw), p = onSurface(c0, [q, 0, 0.15]);
        const e = new THREE.Mesh(new THREE.SphereGeometry(0.028 * S.hs, 20, 14), eyeM);
        e.scale.set(0.7, 0.8, 1.1); e.position.copy(p).add(new V3(-q * 0.014 * S.hs, 0.001, 0)); g.add(e);
        // the upper lid: a cap over the top of the eye, tilted out with the face
        const lid = new THREE.Mesh(new THREE.SphereGeometry(0.028 * S.hs * 1.1, 18, 8, 0, TAU, 0, 1.0), lidM);
        lid.scale.set(0.8, 0.8, 1.12); lid.position.copy(e.position); lid.rotation.set(0.15, 0, -q * 0.55); g.add(lid);
      }
      /* ears: cupped leaves set level off the side of the poll, behind the horns */
      // the cup's inside is the geometry's front face
      const earOut = mat('cattleEar' + coat + redHex, { color: LH ? (coat === 'dun' ? 0x9c7f58 : coat === 'speckle' ? 0xcfc6b6 : coat === 'brindle' ? 0x3d2618 : redHex) : redHex, roughness: 0.85, sheen: 0.3, sheenRoughness: 0.6, sheenColor: 0xcdb89a, side: THREE.BackSide }, true);
      // inside: pink skin in the cup, hair toward the rim (the geometry carries that as vertex colour)
      const earIn = mat('cattleEarIn' + breed, { color: LH ? 0x9a8478 : 0xffffff, vertexColors: true, roughness: 0.9, sheen: 0.25, sheenRoughness: 0.6, sheenColor: 0xd8ccbb, side: THREE.FrontSide }, true);
      const eg = earGeometry((LH ? 0.21 : 0.22) * S.hs, (LH ? 0.068 : 0.078) * S.hs);
      for (const q of [-1, 1]) {
        const root = onSurface(S.at(0.07, -0.125, q * 0.04), [q, 0, -0.15]);
        // level and out to the side, the opening forward, the tip drooping a little and swept back
        const side = new THREE.Group(); side.position.copy(root).add(new V3(-q * 0.015, 0, 0)); side.scale.x = q; g.add(side);
        for (const m2 of [earOut, earIn]) {
          const ear = new THREE.Mesh(eg, m2); ear.rotation.order = 'YZX'; ear.rotation.set(Math.PI / 2 - 0.15, 0.65, -0.5); side.add(ear);
        }
      }
      /* horns */
      const horned = o.horns === true || o.horns === 'true' || (LH && o.horns !== false && o.horns !== 'false');
      if (horned) {
        const hornCol = (t) => tmp.set(0xe0cc9c).lerp(new THREE.Color(0xb08a55), smooth01(0, 0.4, t) * 0.55)
          .lerp(new THREE.Color(0x2a221c), smooth01(LH ? 0.78 : 0.82, 0.99, t)).multiplyScalar(1 - 0.12 * Math.max(0, Math.sin(t * 90)) * Math.pow(1 - t, 3)).clone();
        // horn is keratin: a waxy, warm, half matte sheen, not a lacquer that mirrors the sky
        const hm = mat('cattleHorn', { color: 0xffffff, vertexColors: true, roughness: 0.58, specularIntensity: 0.45, clearcoat: 0.08, clearcoatRoughness: 0.5, sheen: 0.3, sheenRoughness: 0.4, sheenColor: 0xe9d9b0 }, true);
        const sp = Math.max(0.5, (o.spread || 1.9) / 2 - 0.1), up = 0.16 + r() * 0.12, fw = (r() - 0.4) * 0.08;
        const rBase = LH ? (sex === 'cow' ? 0.042 : sex === 'bull' ? 0.066 : 0.056) : (sex === 'bull' ? 0.05 : 0.042);
        for (const q of [-1, 1]) {
          const root = S.at(LH ? -0.005 : 0.005, LH ? -0.055 : -0.06, q * (LH ? 0.1 : 0.095) * S.hw), [rx, ry, rz] = root;
          const P2 = (dx, dy, dz) => [rx + q * dx, ry + dy, rz + dz];
          const pts = LH
            ? [P2(-0.03, -0.005, 0), P2(0.1, 0.005, -0.015), P2(sp * 0.33, -0.015, 0.0 + fw * 0.3), P2(sp * 0.6, -0.005, 0.06 + fw), P2(sp * 0.8, up * 0.2, 0.07 + fw),
               P2(sp * 0.93, up * 0.6, 0.01 + fw * 0.5), P2(sp, up, -0.07)]
            : [P2(-0.02, 0, 0), P2(0.07, -0.004, 0), P2(0.15, -0.012, 0.025), P2(0.21, -0.035, 0.075), P2(0.23, -0.075, 0.125), P2(0.215, -0.115, 0.155)];
          g.add(taperTube(pts, (t) => rBase * (1 - 0.97 * Math.pow(t, LH ? 1.1 : 1.6)) * (1 + 0.05 * Math.sin(t * 90) * Math.pow(1 - t, 3)) + 0.0012,
            hm, LH ? 72 : 36, 16, (t) => hornCol(t)));
        }
      }
      /* hooves: two claws each and the dew claws behind */
      const hoofM = mat('cattleHoof', { color: 0x2b2420, roughness: 0.5, side: THREE.DoubleSide });
      const feet = [[-S.fx, S.fz + 0.045], [S.fx, S.fz + 0.045], [-S.hx, S.hz + 0.09], [S.hx, S.hz + 0.09]];
      feet.forEach(([x, z]) => {
        for (const q of [-1, 1]) { const h = new THREE.Mesh(clawGeometry(), hoofM); h.position.set(x + q * 0.004, 0, z); if (q < 0) h.scale.x = -1; h.rotation.y = q * 0.06; g.add(h); }
        for (const q of [-1, 1]) { const dew = new THREE.Mesh(new THREE.SphereGeometry(0.011, 8, 6), hoofM); dew.scale.set(1, 0.8, 1.3); dew.position.set(x + q * 0.022, 0.1, z - 0.06); g.add(dew); }
      });
      /* tail, hanging close to the round, and its switch */
      const tailTop = [0, S.H - 0.1 - S.rump, S.Lr - 0.07];
      const tailPts = [tailTop, [0, S.H - 0.3, S.Lr - 0.12], [0.008, S.B + 0.1, S.Lr - 0.11], [0.02, S.hock + 0.02, S.Lr - 0.08]];
      const tailM = mat('cattleTail' + coat + redHex, { color: coat === 'hereford' ? redHex : coat === 'dun' ? 0x9c7f58 : coat === 'speckle' ? 0xd9d2c4 : coat === 'brindle' ? 0x3d2618 : redHex, roughness: 0.85 });
      g.add(taperTube(tailPts, (t) => 0.036 - 0.02 * t, tailM, 28, 10));
      const swM = mat('cattleSwitch' + coat, { color: coat === 'hereford' ? 0xe3dccd : (coat === 'brindle' ? 0x1e1916 : coat === 'dun' ? 0x3a2a1c : coat === 'speckle' ? 0xe0d8c8 : 0x2a1f19), roughness: 0.95 });
      const sw0 = [0.02, S.hock + 0.06, S.Lr - 0.08];
      for (let k = 0; k < 16; k++) {
        const a = r() * TAU, rr = 0.012 + r() * 0.03, len = 0.2 + r() * 0.12;
        g.add(taperTube([sw0, [sw0[0] + Math.cos(a) * rr * 0.6, sw0[1] - len * 0.4, sw0[2] + Math.sin(a) * rr * 0.6],
          [sw0[0] + Math.cos(a) * rr, sw0[1] - len * 0.8, sw0[2] + Math.sin(a) * rr], [sw0[0] + Math.cos(a) * rr * 1.2, sw0[1] - len, sw0[2] + Math.sin(a) * rr * 1.2]],
          (t) => 0.014 * (1 - t) + 0.002, swM, 8, 5));
      }
      /* teats on a cow */
      if (sex === 'cow') {
        const tM = mat('cattleTeat', { color: 0xb88a7c, roughness: 0.6 });
        for (const a of [-1, 1]) for (const b of [-1, 1]) {
          const tt = new THREE.Mesh(new THREE.CapsuleGeometry(0.01, 0.03, 4, 8), tM);
          tt.position.set(a * 0.045, S.B - 0.055, S.Lr + 0.34 + b * 0.045); g.add(tt);
        }
      }
      // a little variety between animals of one kind, without another field build
      const sc = 0.97 + r() * 0.06; g.scale.set(sc * (0.98 + r() * 0.04), sc, sc);
      return centre(outer);
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
    for (let k = 0; k < 25; k++) { x.fillStyle = 'rgba(120,100,70,' + (0.02 + r() * 0.03) + ')'; x.beginPath(); x.arc(r() * W, r() * H, 5 + r() * 30, 0, TAU); x.fill(); }
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
        const v0 = uvA.getY(idx[t]), v1 = uvA.getY(idx[t + 1]), v2 = uvA.getY(idx[t + 2]);
        (Math.max(v0, v1, v2) < f * 0.97 || Math.min(v0, v1, v2) > 1 - f * 0.97 ? A : B).push(idx[t], idx[t + 1], idx[t + 2]);
      }
      geo.setIndex(A.concat(B)); geo.clearGroups(); geo.addGroup(0, A.length, 0); geo.addGroup(A.length, B.length, 1);
      // faces: planar uv; wrap: repeat around
      for (let i = 0; i < uvA.count; i++) { const v = uvA.getY(i); if (v < f * 0.97 || v > 1 - f * 0.97) { const p = geo.attributes.position; uvA.setXY(i, p.getZ(i) / 1.2, p.getY(i) / 1.2); } else uvA.setXY(i, uvA.getX(i) * 6, v * 2); }
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
          new THREE.Quaternion().setFromEuler(new THREE.Euler(0, -a, 0)).multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(0, 0, -ang))), new V3(1, 1, 1));
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
