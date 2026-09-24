/* kit/power.js, see assets/js/txkit.js for the conventions.
 *
 * THE GRID FAMILY. ERCOT's physical plant, modelled from utility standards rather than from
 * memory of a picture: lattice towers built member by member as bolted steel ANGLES (an L
 * section, not a tube), insulator strings built disc by disc at the real 146 mm cap and pin
 * spacing, bundled conductors at the 457 mm (18 in) bundle spacing, and every structure at the
 * height its voltage class needs for clearance.
 *
 * Every structure that carries wire publishes where the wire goes, in its own local metres:
 *   g.userData.attach  = [{ x, y, z, n, spacing, circuit, phase }]   conductor attachment points
 *   g.userData.shield  = [{ x, y, z }]                                shield (static) wire points
 * `power_line` reads them to string catenaries between structures, and a deck can too.
 *
 * Every repeat is merged per material through a local builder (Bld), so a 400 member tower is
 * a handful of draw calls. Line direction is z throughout: arms reach along x, wire runs along z,
 * so the FRONT (+z) view is the classic view down the line with the arms spread across it.
 */
export function install(K, THREE, TXT) {
  const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
  const Y = V3(0, 1, 0);
  const DEG = Math.PI / 180;

  /* ================================================================================ builder */
  const TPL = new Map();
  function tpl(key, make) {
    if (!TPL.has(key)) {
      let g = make();
      if (g.index) g = g.toNonIndexed();
      if (!g.attributes.normal) g.computeVertexNormals();
      TPL.set(key, g);
    }
    return TPL.get(key);
  }
  const _m = new THREE.Matrix4(), _n = new THREE.Matrix3(), _v = new THREE.Vector3(), _q = new THREE.Quaternion();
  class Bld {
    constructor() { this.bins = new Map(); }
    add(mat, g, m4) {
      let bin = this.bins.get(mat);
      if (!bin) { bin = []; this.bins.set(mat, bin); }
      bin.push([g, m4.clone()]);
    }
    /* a mesh or geometry at a transform */
    geo(mat, geometry, pos, quat, scale) {
      let g = geometry.index ? geometry.toNonIndexed() : geometry;
      if (!g.attributes.normal) g.computeVertexNormals();
      _m.compose(pos || V3(0, 0, 0), quat || new THREE.Quaternion(), scale || V3(1, 1, 1));
      this.add(mat, g, _m.clone());
    }
    /* axis-aligned box centred at x,y,z, turned ry about y */
    box(mat, w, h, d, x, y, z, ry) {
      const g = tpl('box', () => new THREE.BoxGeometry(1, 1, 1));
      _q.setFromAxisAngle(Y, ry || 0);
      _m.compose(V3(x, y, z), _q, V3(w, h, d)); this.add(mat, g, _m);
    }
    /* a box whose long axis runs a->b, cross section w (along `side`) by d */
    beam(mat, a, b, w, d, side) {
      const A = arr(a), B = arr(b), dir = B.clone().sub(A), len = dir.length(); dir.normalize();
      let s = side ? arr(side) : (Math.abs(dir.y) > 0.9 ? V3(1, 0, 0) : Y.clone());
      s.sub(dir.clone().multiplyScalar(s.dot(dir))).normalize();
      const X = s, Z = X.clone().cross(dir);        // X = side, Y = dir, Z = X x Y
      _m.makeBasis(X, dir, Z); _m.scale(V3(w, len, d)); _m.setPosition(A.clone().add(B).multiplyScalar(0.5));
      this.add(mat, tpl('box', () => new THREE.BoxGeometry(1, 1, 1)), _m);
    }
    /* round bar a->b */
    bar(mat, a, b, r, seg) {
      seg = seg || 8;
      const A = arr(a), B = arr(b), dir = B.clone().sub(A), len = dir.length(); dir.normalize();
      _q.setFromUnitVectors(Y, dir);
      _m.compose(A.clone().add(B).multiplyScalar(0.5), _q, V3(r, len, r));
      this.add(mat, tpl('cyl' + seg, () => new THREE.CylinderGeometry(1, 1, 1, seg, 1, false)), _m);
    }
    /* tapered round a->b */
    cone(mat, a, b, r0, r1, seg) {
      seg = seg || 16;
      const A = arr(a), B = arr(b), dir = B.clone().sub(A), len = dir.length(); dir.normalize();
      const g = new THREE.CylinderGeometry(r1, r0, len, seg, 1, false);
      _q.setFromUnitVectors(Y, dir);
      this.geo(mat, g, A.clone().add(B).multiplyScalar(0.5), _q.clone());
    }
    /* steel ANGLE (L section) a->b, legs w, thickness about w/10. ref orients it:
     * mode 'bis' puts the heel away from ref (legs toward it, a tower leg), 'leg' lays one leg
     * in the plane and points the other along ref (a brace on a face). */
    ang(mat, a, b, w, ref, mode) {
      const A = arr(a), B = arr(b), dir = B.clone().sub(A), len = dir.length(); if (len < 1e-4) return; dir.normalize();
      let r = arr(ref || [1, 0, 0]); r.sub(dir.clone().multiplyScalar(r.dot(dir)));
      if (r.lengthSq() < 1e-8) r = Math.abs(dir.y) > 0.9 ? V3(1, 0, 0) : V3(0, 1, 0), r.sub(dir.clone().multiplyScalar(r.dot(dir)));
      r.normalize();
      let X, Z;
      if (mode === 'bis') { const c = dir.clone().cross(r); X = r.clone().add(c).normalize(); Z = X.clone().cross(dir); }
      else { Z = r; X = dir.clone().cross(Z); }
      _m.makeBasis(X, dir, Z); _m.scale(V3(w, len, w)); _m.setPosition(A.clone().add(B).multiplyScalar(0.5));
      this.add(mat, tpl('angle', () => {
        const t = 0.1, g1 = new THREE.BoxGeometry(1, 1, t), g2 = new THREE.BoxGeometry(t, 1, 1);
        g1.translate(0.5, 0, t / 2); g2.translate(t / 2, 0, 0.5);
        return mergeGeos([g1, g2]);
      }), _m);
    }
    /* sagging cable a->b, sag metres at mid span, radius r */
    cable(mat, a, b, sag, r, seg, radial) {
      const A = arr(a), B = arr(b), n = seg || 24, pts = [];
      if (!(A.distanceTo(B) > 1e-3)) return;                 // a zero length span has no curve
      for (let i = 0; i <= n; i++) {
        const t = i / n; pts.push(V3(A.x + (B.x - A.x) * t, A.y + (B.y - A.y) * t - sag * 4 * t * (1 - t), A.z + (B.z - A.z) * t));
      }
      const g = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), n * 2, r, radial || 5, false);
      this.geo(mat, g);
    }
    build(group, opts) {
      opts = opts || {};
      for (const [mat, bin] of this.bins) {
        let total = 0; bin.forEach(([g]) => { total += g.attributes.position.count; });
        const p = new Float32Array(total * 3), n = new Float32Array(total * 3), u = new Float32Array(total * 2);
        let o = 0;
        for (const [g, m4] of bin) {
          const P = g.attributes.position.array, N = g.attributes.normal.array, U = g.attributes.uv ? g.attributes.uv.array : null;
          const e = m4.elements; _n.getNormalMatrix(m4); const ne = _n.elements, c = P.length / 3;
          for (let i = 0; i < c; i++) {
            const x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2], j = (o + i) * 3;
            p[j] = e[0] * x + e[4] * y + e[8] * z + e[12]; p[j + 1] = e[1] * x + e[5] * y + e[9] * z + e[13]; p[j + 2] = e[2] * x + e[6] * y + e[10] * z + e[14];
            const a = N[i * 3], b = N[i * 3 + 1], d = N[i * 3 + 2];
            const nx = ne[0] * a + ne[3] * b + ne[6] * d, ny = ne[1] * a + ne[4] * b + ne[7] * d, nz = ne[2] * a + ne[5] * b + ne[8] * d;
            const l = Math.sqrt(nx * nx + ny * ny + nz * nz) || 1; n[j] = nx / l; n[j + 1] = ny / l; n[j + 2] = nz / l;
            if (U) { u[(o + i) * 2] = U[i * 2]; u[(o + i) * 2 + 1] = U[i * 2 + 1]; }
          }
          o += c;
        }
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(p, 3));
        geo.setAttribute('normal', new THREE.BufferAttribute(n, 3));
        geo.setAttribute('uv', new THREE.BufferAttribute(u, 2));
        const metres = (mat.userData && mat.userData.metres) || (mat.map && mat.map.userData && mat.map.userData.metres);
        if (mat.map && metres) K.uvBox(geo, metres);
        geo.computeBoundingBox(); geo.computeBoundingSphere();
        const m = new THREE.Mesh(geo, mat);
        if (mat.transparent || mat.userData.noShadow) m.castShadow = false;
        group.add(m);
      }
      this.bins.clear();
      return group;
    }
  }
  function arr(a) { return a.isVector3 ? a.clone() : V3(a[0], a[1], a[2]); }
  function mergeGeos(list) {
    let total = 0; const parts = list.map((g) => { const x = g.index ? g.toNonIndexed() : g; if (!x.attributes.normal) x.computeVertexNormals(); total += x.attributes.position.count; return x; });
    const p = new Float32Array(total * 3), n = new Float32Array(total * 3), u = new Float32Array(total * 2); let o = 0;
    parts.forEach((g) => { p.set(g.attributes.position.array, o * 3); n.set(g.attributes.normal.array, o * 3);
      if (g.attributes.uv) u.set(g.attributes.uv.array, o * 2); o += g.attributes.position.count; });
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(p, 3)); g.setAttribute('normal', new THREE.BufferAttribute(n, 3));
    g.setAttribute('uv', new THREE.BufferAttribute(u, 2));
    return g;
  }
  const lerp = (a, b, t) => a + (b - a) * t;
  const rbox = (w, h, d, rr, m, o) => tpl('rb' + [w, h, d, rr, o && o.segments].join(','), () => TXT.roundedBox(w, h, d, rr, null, o));
  const L3 = (a, b, t) => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];

  /* ============================================================================== materials */
  /* K.mat keys on JSON.stringify(params), and a texture's toJSON serialises its whole image, so
   * a textured material costs a PNG encode on every lookup. This cache keys a texture by uuid. */
  const KM = new Map();
  function kmat(key, params, physical) {
    const k = key + '|' + Object.entries(params || {}).map(([n, v]) => n + ':' + (v && v.isTexture ? v.uuid : v)).join(',') + (physical ? 'p' : '');
    if (!KM.has(k)) {
      const P = Object.assign({ roughness: 0.8, metalness: 0 }, params || {});
      KM.set(k, physical ? new THREE.MeshPhysicalMaterial(P) : new THREE.MeshStandardMaterial(P));
    }
    return KM.get(k);
  }
  const M = {
    galv: (r) => kmat('pw_galv', { color: r < 0.5 ? 0x9da2a4 : 0x8e9395, metalness: 0.72, roughness: r < 0.5 ? 0.46 : 0.56 }),
    galvDark: () => kmat('pw_galvd', { color: 0x74797c, metalness: 0.7, roughness: 0.5 }),
    alu: () => kmat('pw_alu', { color: 0xc3c7c9, metalness: 0.9, roughness: 0.34 }),
    conductor: () => kmat('pw_cond', { color: 0xa9adaf, metalness: 0.88, roughness: 0.4 }),
    shieldw: () => kmat('pw_ohgw', { color: 0x80868a, metalness: 0.8, roughness: 0.5 }),
    glass: () => kmat('pw_insglass', { color: 0x5f8378, metalness: 0.05, roughness: 0.1, clearcoat: 1,
                                         clearcoatRoughness: 0.05, envMapIntensity: 1.4 }, true),
    porc: () => kmat('pw_porc', { color: 0x5b3b27, metalness: 0, roughness: 0.18, clearcoat: 0.8, clearcoatRoughness: 0.1 }, true),
    porcGrey: () => kmat('pw_porcg', { color: 0x8a8d8c, metalness: 0, roughness: 0.2, clearcoat: 0.8, clearcoatRoughness: 0.12 }, true),
    polymer: () => kmat('pw_poly', { color: 0x6d7478, roughness: 0.62 }),
    concrete: () => kmat('pw_conc', { color: 0xffffff, roughness: 0.93, map: K.tex('concrete', { color: '#a7a298' }) }),
    wood: (c, h) => kmat('pw_wood', { color: 0xffffff, roughness: 0.9, map: poleTex(c || '#6e5a46', h) }),
    rust: () => kmat('pw_corten', { color: 0x4f3527, metalness: 0.3, roughness: 0.8 }),
    paint: (c, r) => kmat('pw_paint', { color: c, metalness: 0.25, roughness: r != null ? r : 0.5 }),
    white: () => kmat('pw_white', { color: 0xe9ebea, metalness: 0.15, roughness: 0.42 }),
    black: () => kmat('pw_black', { color: 0x1d1f21, metalness: 0.2, roughness: 0.6 }),
    rubber: () => K.finish.rubber(),
  };

  /* A treated pole: weathered grey brown with vertical checks, not a board texture. */
  const PTEX = new Map();
  function poleTex(color, horiz) {
    const key = color + (horiz ? 'h' : '');
    if (PTEX.has(key)) return PTEX.get(key);
    const N = 256, c = document.createElement('canvas'); c.width = c.height = N;
    const x = c.getContext('2d'), r = K.rng(4411);
    x.fillStyle = color; x.fillRect(0, 0, N, N);
    for (let i = 0; i < 260; i++) {
      x.fillStyle = 'rgba(' + (r() < 0.5 ? '0,0,0' : '255,245,230') + ',' + (0.03 + r() * 0.07) + ')';
      x.fillRect(r() * N, 0, 1 + r() * 3, N);
    }
    for (let i = 0; i < 14; i++) {           // drying checks
      x.strokeStyle = 'rgba(20,14,10,' + (0.35 + r() * 0.3) + ')'; x.lineWidth = 1 + r() * 1.5;
      const x0 = r() * N, y0 = r() * N, L = 40 + r() * 160; x.beginPath(); x.moveTo(x0, y0);
      x.lineTo(x0 + (r() - 0.5) * 6, y0 + L); x.stroke();
    }
    const im = x.getImageData(0, 0, N, N), d = im.data;
    for (let i = 0; i < d.length; i += 4) { const k = 1 + (r() - 0.5) * 0.12; d[i] *= k; d[i + 1] *= k; d[i + 2] *= k; }
    x.putImageData(im, 0, 0);
    let src = c;
    if (horiz) { src = document.createElement('canvas'); src.width = src.height = N; const y = src.getContext('2d');
      y.translate(N / 2, N / 2); y.rotate(Math.PI / 2); y.drawImage(c, -N / 2, -N / 2); }
    const t = new THREE.CanvasTexture(src); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 8; t.userData.metres = 1.2; PTEX.set(key, t); return t;
  }

  /* ============================================================================ insulators */
  /* A cap and pin disc (ANSI 52-3): 254 mm shell, 146 mm spacing. Profile is lathe (r, y), y up
   * from the disc's pin end. Glass and porcelain share it, polymer is a different object. */
  const discGeo = (seg) => tpl('disc' + (seg || 12), () => {
    const P = [[0.0, 0.0], [0.022, 0.0], [0.05, 0.03], [0.1, 0.036], [0.127, 0.042],
               [0.122, 0.058], [0.08, 0.08], [0.05, 0.1], [0.04, 0.13], [0.0, 0.146]];
    return new THREE.LatheGeometry(P.map(p => new THREE.Vector2(p[0], p[1])), seg || 12);
  });
  /* a silicone rubber long rod: a 25 mm core with sheds every `pitch`, alternating large and small */
  function polymerGeo(len, big, pitch) {
    const key = 'poly' + len.toFixed(2) + big + pitch;
    return tpl(key, () => {
      const P = [[0, 0], [0.04, 0], [0.04, 0.12], [0.016, 0.14]];
      let y = 0.2, k = 0;
      while (y < len - 0.2) {
        const R = k % 2 ? big * 0.72 : big;
        P.push([0.016, y - 0.012], [R, y - 0.004], [R, y + 0.004], [0.018, y + 0.02]);
        y += pitch; k++;
      }
      P.push([0.016, len - 0.14], [0.04, len - 0.12], [0.04, len], [0, len]);
      return new THREE.LatheGeometry(P.map(p => new THREE.Vector2(p[0], p[1])), 16);
    });
  }
  /* A suspension string hanging from `top` straight down `len` metres. kind glass|porcelain|polymer.
   * Grading ring at the line end when kv >= 230. Returns the bottom point [x,y,z]. */
  function string(b, top, len, kind, kv, hw) {
    const [x, y, z] = top;
    // hanger hardware: clevis, shackle and ball eye
    b.bar(hw, [x, y, z], [x, y - 0.22, z], 0.018, 6);
    b.box(hw, 0.05, 0.08, 0.1, x, y - 0.04, z);
    const s0 = y - 0.24, s1 = y - len + 0.28;
    if (kind === 'polymer') {
      const g = polymerGeo(s0 - s1, kv >= 230 ? 0.085 : 0.065, kv >= 230 ? 0.075 : 0.07);
      b.geo(M.polymer(), g, V3(x, s1, z));
      b.box(hw, 0.08, 0.14, 0.08, x, s0 + 0.02, z); b.box(hw, 0.08, 0.14, 0.08, x, s1 - 0.02, z);
    } else {
      const n = Math.max(3, Math.floor((s0 - s1) / 0.146));
      const mat = kind === 'porcelain' ? M.porc() : kind === 'grey' ? M.porcGrey() : M.glass();
      for (let i = 0; i < n; i++) {
        const yy = s0 - (i + 1) * 0.146;
        // disc: skirt down, pin down toward the line
        _q.setFromAxisAngle(V3(1, 0, 0), Math.PI);
        b.geo(mat, discGeo(), V3(x, yy + 0.146, z), _q.clone());
        b.bar(hw, [x, yy + 0.146, z], [x, yy + 0.1, z], 0.028, 8);   // the cemented iron cap
      }
    }
    const bot = [x, y - len, z];
    b.bar(hw, [x, s1, z], bot, 0.016, 6);
    if (kv >= 230) {                          // corona / grading ring around the line end
      const ring = tpl('ring' + kv, () => new THREE.TorusGeometry(kv >= 500 ? 0.34 : 0.24, 0.024, 8, 28));
      _q.setFromAxisAngle(V3(1, 0, 0), Math.PI / 2);
      b.geo(M.alu(), ring, V3(x, s1 + 0.1, z), _q.clone());
      b.bar(M.alu(), [x - 0.2, s1 + 0.1, z], [x + 0.2, s1 + 0.1, z], 0.012, 6);
    }
    return bot;
  }
  /* The bundle at a string's foot: yoke plate, suspension clamps and short conductor stubs so a
   * structure without spans still reads as dressed. Subconductors lie across the line (x). */
  function bundle(b, foot, n, spacing, hw, stub) {
    const [x, y, z] = foot, pts = bundlePts(n, spacing);
    if (n > 1) {
      const wx = n === 2 ? spacing + 0.1 : spacing * 1.2;
      b.box(hw, wx, 0.05, 0.08, x, y - 0.04, z);
      if (n > 2) b.box(hw, 0.06, spacing * 1.1, 0.08, x, y - 0.04 - spacing * 0.5, z);
    }
    const out = [];
    pts.forEach(([dx, dy]) => {
      const px = x + dx, py = y - 0.1 + dy;
      b.box(hw, 0.07, 0.07, 0.3, px, py, z);                     // clamp
      out.push([px, py, z]);
      if (stub) b.bar(M.conductor(), [px, py, z - stub], [px, py, z + stub], 0.0145, 8);
    });
    return out;
  }
  function bundlePts(n, s) {
    if (n <= 1) return [[0, 0]];
    if (n === 2) return [[-s / 2, 0], [s / 2, 0]];
    const R = s / (2 * Math.sin(Math.PI / n)), out = [];
    for (let i = 0; i < n; i++) { const a = Math.PI / 2 + i * 2 * Math.PI / n + (n === 4 ? Math.PI / 4 : 0);
      out.push([Math.cos(a) * R, Math.sin(a) * R - R]); }
    return out;
  }

  /* ================================================================================ lattice */
  /* Four corners of a square section of half width h at height y. Order around: ++, -+, --, +-. */
  const sq = (h, y) => [[h, y, h], [-h, y, h], [-h, y, -h], [h, y, -h]];
  /* One lattice panel between two sections of 4 corners each. Pattern X, K, or Z (single zigzag).
   * Legs are drawn by the caller. Faces listed by index 0..3 (face i joins corner i and i+1). */
  function panel(b, mat, S0, S1, pat, w, faces, flip) {
    const cx = (S0[0][0] + S0[2][0] + S1[0][0] + S1[2][0]) / 4, cy = (S0[0][1] + S1[0][1]) / 2, cz = (S0[0][2] + S0[2][2] + S1[0][2] + S1[2][2]) / 4;
    for (const f of faces || [0, 1, 2, 3]) {
      const a0 = S0[f], b0 = S0[(f + 1) % 4], a1 = S1[f], b1 = S1[(f + 1) % 4];
      const mid = L3(L3(a0, b0, 0.5), L3(a1, b1, 0.5), 0.5), inn = [cx - mid[0], cy - mid[1], cz - mid[2]];
      if (pat === 'X') { b.ang(mat, a0, b1, w, inn, 'leg'); b.ang(mat, b0, a1, w, inn, 'leg'); }
      else if (pat === 'K') { const m1 = L3(a1, b1, 0.5); b.ang(mat, a0, m1, w, inn, 'leg'); b.ang(mat, b0, m1, w, inn, 'leg');
        // redundant members: a secondary strut at mid height and sub-diagonals
        const ma = L3(a0, a1, 0.5), mb = L3(b0, b1, 0.5); b.ang(mat, ma, L3(ma, mb, 0.25), w * 0.7, inn, 'leg'); b.ang(mat, mb, L3(mb, ma, 0.25), w * 0.7, inn, 'leg'); }
      else if (pat === 'Kinv') { const m0 = L3(a0, b0, 0.5); b.ang(mat, m0, a1, w, inn, 'leg'); b.ang(mat, m0, b1, w, inn, 'leg'); }
      else { if ((f + (flip ? 1 : 0)) % 2) b.ang(mat, a0, b1, w, inn, 'leg'); else b.ang(mat, b0, a1, w, inn, 'leg'); }
    }
  }
  function ringStruts(b, mat, S, w, faces) {
    const cx = (S[0][0] + S[2][0]) / 2, cz = (S[0][2] + S[2][2]) / 2;
    for (const f of faces || [0, 1, 2, 3]) {
      const a = S[f], c = S[(f + 1) % 4], m = L3(a, c, 0.5);
      b.ang(mat, a, c, w, [cx - m[0], 1.2, cz - m[2]], 'leg');
    }
  }
  function planBrace(b, mat, S, w) {
    b.ang(mat, S[0], S[2], w, [0, 1, 0], 'leg'); b.ang(mat, S[1], S[3], w, [0, 1, 0], 'leg');
  }
  /* A tapered box truss from section A (4 corners) to section B, n bays of zigzag lacing on
   * every face, chords of width wc, lacing wl. Used for crossarms, bridges and gantry beams. */
  function truss(b, mat, A, B, n, wc, wl, o) {
    o = o || {};
    const cA = centroid(A), cB = centroid(B);
    for (let i = 0; i < 4; i++) {
      const inn = [ (cA[0] + cB[0]) / 2 - (A[i][0] + B[i][0]) / 2, (cA[1] + cB[1]) / 2 - (A[i][1] + B[i][1]) / 2, (cA[2] + cB[2]) / 2 - (A[i][2] + B[i][2]) / 2 ];
      b.ang(mat, A[i], B[i], wc, inn, 'bis');
    }
    const secs = [];
    for (let k = 0; k <= n; k++) secs.push([0, 1, 2, 3].map(i => L3(A[i], B[i], k / n)));
    for (let k = 0; k < n; k++) {
      if (k > 0 || o.endA) ringStruts(b, mat, secs[k], wl, o.ringFaces);
      panel(b, mat, secs[k], secs[k + 1], 'Z', wl, o.faces, k % 2 === 1);
    }
    if (o.endB) ringStruts(b, mat, secs[n], wl, o.ringFaces);
  }
  const centroid = (S) => [(S[0][0] + S[1][0] + S[2][0] + S[3][0]) / 4, (S[0][1] + S[1][1] + S[2][1] + S[3][1]) / 4, (S[0][2] + S[1][2] + S[2][2] + S[3][2]) / 4];

  /* gusset plates at leg joints: the bolted plate that makes a tower read as fabricated steel */
  function gusset(b, mat, p, out, s) {
    const d = V3(out[0], 0, out[2]).normalize();
    b.box(mat, s, s * 1.3, 0.012, p[0] - d.x * 0.02, p[1], p[2] - d.z * 0.02, Math.atan2(d.x, d.z));
  }
  function pier(b, x, z, r, above) {
    const g = new THREE.CylinderGeometry(r, r, above + 0.3, 20);
    b.geo(M.concrete(), g, V3(x, (above - 0.3) / 2, z));
  }

  /* ====================================================================== transmission tower */
  const TOWER = {
    // lowest arm y, arm spacing, arm reaches (bottom, mid, top), arm depth at the body, string
    // length, bundle, base half width, waist half width, top half width, shield peak height
    138: { y0: 16.5, dy: 4.6, reach: [4.1, 4.6, 4.0], ht: 1.8, str: 1.55, n: 1, sp: 0, base: 2.9, waist: 0.95, top: 0.7, peak: 2.6, leg: 0.13, br: 0.065 },
    345: { y0: 26.0, dy: 7.2, reach: [6.9, 7.6, 6.6], ht: 2.6, str: 3.2, n: 2, sp: 0.457, base: 4.6, waist: 1.45, top: 0.95, peak: 3.4, leg: 0.2, br: 0.09 },
  };
  function doubleCircuit(o, r) {
    const kv = o.voltage === 138 ? 138 : 345, T = Object.assign({}, TOWER[kv]);
    const hs = 1 + (o.height ? (o.height - 1) : 0);           // body extension factor
    T.y0 *= hs;
    const g = new THREE.Group(), b = new Bld();
    const steel = M.galv(r()), hw = M.galvDark();
    const kind = o.insulator || (kv === 138 ? (r() < 0.5 ? 'porcelain' : 'polymer') : (r() < 0.55 ? 'glass' : 'polymer'));
    const armY = [T.y0, T.y0 + T.dy, T.y0 + 2 * T.dy];
    const yTop = armY[2] + T.ht + T.dy * 0.42, yWaist = T.y0 - 0.5, pierH = 0.55;
    const hwAt = (y) => y <= yWaist ? lerp(T.base, T.waist, (y - pierH) / (yWaist - pierH)) : lerp(T.waist, T.top, (y - yWaist) / (yTop - yWaist));
    // ---- panel levels: lower body panels grow toward the ground, the arm zone follows the arms
    const lower = [], nLow = kv === 345 ? 7 : 6;
    let acc = 0; const wts = []; for (let i = 0; i < nLow; i++) { wts.push(Math.pow(1.22, nLow - 1 - i)); acc += wts[i]; }
    let yy = pierH; lower.push(yy); for (let i = 0; i < nLow; i++) { yy += (yWaist - pierH) * wts[i] / acc; lower.push(yy); }
    const upper = [yWaist];
    armY.forEach((ya) => { if (ya - upper[upper.length - 1] > 0.3) upper.push(ya); upper.push(ya + T.ht); });
    upper.push(yTop);
    const levels = lower.concat(upper.slice(1)).filter((v, i, a) => i === 0 || v - a[i - 1] > 0.25);
    // split tall panels in the arm zone so no brace runs more than about 4 m
    const lv = [levels[0]];
    for (let i = 1; i < levels.length; i++) { const d = levels[i] - levels[i - 1], k = levels[i - 1] >= yWaist - 0.01 && d > 4.2 ? 2 : 1;
      for (let j = 1; j <= k; j++) lv.push(levels[i - 1] + d * j / k); }
    const S = lv.map(y => sq(hwAt(y), y));
    // ---- legs, by panel so the angle tapers with height
    for (let k = 0; k < S.length - 1; k++) {
      const w = lerp(T.leg, T.leg * 0.55, k / (S.length - 1));
      for (let i = 0; i < 4; i++) b.ang(steel, S[k][i], S[k + 1][i], w, [-S[k][i][0], 0, -S[k][i][2]], 'bis');
    }
    // ---- bracing
    for (let k = 0; k < S.length - 1; k++) {
      const y = lv[k], w = lerp(T.br, T.br * 0.7, k / S.length);
      const pat = k === 0 ? 'K' : (y < yWaist - 0.01 ? 'X' : (k % 2 ? 'X' : 'X'));
      panel(b, steel, S[k], S[k + 1], pat, w);
      if (k > 0) ringStruts(b, steel, S[k], w * 0.85);
      if (k === 0 || Math.abs(y - yWaist) < 0.3 || armY.some(a => Math.abs(a - y) < 0.05)) planBrace(b, steel, S[k], w * 0.8);
      // gussets where the braces land on the legs
      if (k > 0) S[k].forEach((p) => gusset(b, hw, p, [p[0], 0, p[2]], w * 3.2));
    }
    ringStruts(b, steel, S[S.length - 1], T.br); planBrace(b, steel, S[S.length - 1], T.br * 0.8);
    // ---- crossarms, both sides, three levels: bottom chords level, top chords sloping to the tip
    const attach = [], shield = [];
    armY.forEach((ya, ai) => {
      [1, -1].forEach((sx) => {
        const L = T.reach[ai] * (0.97 + r() * 0.02) * (ai === 1 ? 1 : 1), h0 = hwAt(ya), h1 = hwAt(ya + T.ht), tw = kv === 345 ? 0.28 : 0.2;
        const A = [[sx * h0, ya, h0], [sx * h0, ya, -h0], [sx * h1, ya + T.ht, -h1], [sx * h1, ya + T.ht, h1]];
        const tipY = ya + (kv === 345 ? 0.55 : 0.4);
        const B = [[sx * L, ya, tw], [sx * L, ya, -tw], [sx * L, tipY, -tw], [sx * L, tipY, tw]];
        truss(b, steel, A, B, Math.max(3, Math.round((L - h0) / (kv === 345 ? 1.35 : 1.1))), T.br * 1.05, T.br * 0.72, { endB: true });
        // the hanger plate under the tip and the string
        const hx = sx * (L - 0.12);
        b.box(hw, 0.2, 0.05, tw * 2 + 0.1, hx, ya - 0.03, 0);
        const foot = string(b, [hx, ya - 0.05, 0], T.str, kind, kv, hw);
        const pts = bundle(b, foot, T.n, T.sp, hw, o.leads ? 0 : 0.9);
        attach.push({ x: foot[0], y: foot[1] - 0.1, z: 0, n: T.n, spacing: T.sp, circuit: sx > 0 ? 0 : 1, phase: ai });
      });
    });
    // ---- shield wire peaks: a short arm off the body top with a pyramid peak at each end
    const ht = hwAt(yTop), Le = T.reach[2] * 0.78;
    [1, -1].forEach((sx) => {
      // the earthwire arm: same form as a phase arm, shallower, its tip carrying a small peak
      const hA = T.dy * 0.3, yA = yTop - hA;
      const h0 = hwAt(yA);
      const A = [[sx * h0, yA, h0], [sx * h0, yA, -h0], [sx * ht, yTop, -ht], [sx * ht, yTop, ht]];
      const tipB = yA + 0.3, tw = 0.2;
      const B = [[sx * Le, yA, tw], [sx * Le, yA, -tw], [sx * Le, tipB, -tw], [sx * Le, tipB, tw]];
      truss(b, steel, A, B, Math.max(2, Math.round((Le - h0) / 1.3)), T.br, T.br * 0.7, { endB: true });
      const tip = [sx * Le, yA + T.peak, 0];
      [[tw, tw], [-tw, tw], [-tw, -tw], [tw, -tw]].forEach(([dx, dz]) =>
        b.ang(steel, [sx * Le + dx * 1.6, tipB, dz * 1.4], tip, T.br * 0.85, [-dx, 0, -dz], 'bis'));
      b.ang(steel, [sx * (Le - 1.2), tipB + 0.25, 0], [sx * Le, yA + T.peak * 0.6, 0], T.br * 0.7, [0, 0, 1], 'leg');
      b.box(hw, 0.12, 0.1, 0.35, tip[0], tip[1] + 0.05, 0);                       // suspension clamp
      if (!o.leads) b.bar(M.shieldw(), [tip[0], tip[1], -0.9], [tip[0], tip[1], 0.9], 0.0065, 6);
      shield.push({ x: tip[0], y: tip[1], z: 0 });
    });
    // ---- foundations, step bolts, anti climb guard, danger plate
    S[0].forEach((p) => { pier(b, p[0], p[2], 0.48, pierH); b.box(hw, 0.36, 0.05, 0.36, p[0], pierH + 0.02, p[2]); });
    const leg0 = S.map(s => s[0]);
    for (let y = 2.8; y < yTop - 1; y += 0.4) {
      const hwy = hwAt(y), p = [hwy, y, hwy];
      b.bar(hw, p, [p[0] + 0.14, y + 0.01, p[2] + 0.14], 0.009, 5);
    }
    const yAc = 3.4, hac = hwAt(yAc);
    for (let i = 0; i < 4; i++) {                             // barbed wire anti climbing band
      const a = sq(hac, yAc)[i], c = sq(hac, yAc)[(i + 1) % 4];
      for (let k = 0; k < 4; k++) b.bar(hw, [a[0], yAc + k * 0.14, a[2]], [c[0], yAc + k * 0.14, c[2]], 0.006, 4);
    }
    b.box(M.paint(0xe8e4d8, 0.5), 0.3, 0.4, 0.01, 0, 2.6, hwAt(2.6) + 0.02);    // number and danger plate
    b.box(M.paint(0xb42a22, 0.5), 0.3, 0.09, 0.012, 0, 2.75, hwAt(2.6) + 0.02);
    b.build(g);
    if (o.leads > 1) addLeads(g, attach, shield, o.leads, kv);
    g.userData.attach = attach; g.userData.shield = shield; g.userData.kv = kv;
    return g;
  }

  /* 765 kV: a single circuit, horizontal phases, self supporting. The body tapers to a waist and
   * opens into a window whose two raked columns carry a lattice bridge; the middle phase hangs
   * in the window on a V string, the outer phases hang off the bridge ends, six conductor bundles. */
  function horizontal765(o, r) {
    const g = new THREE.Group(), b = new Bld(), steel = M.galv(r()), hw = M.galvDark();
    const hs = o.height || 1;
    const yW = 22 * hs, yB = yW + 12.5, base = 5.2, waist = 1.6, pierH = 0.6;
    const ph = 14.6, Lb = ph + 3.6, str = 5.8;
    const hwAt = (y) => lerp(base, waist, (y - pierH) / (yW - pierH));
    const lv = [pierH]; const n = 7; let acc = 0, wts = []; for (let i = 0; i < n; i++) { wts.push(Math.pow(1.2, n - 1 - i)); acc += wts[i]; }
    let yy = pierH; for (let i = 0; i < n; i++) { yy += (yW - pierH) * wts[i] / acc; lv.push(yy); }
    const S = lv.map(y => sq(hwAt(y), y));
    for (let k = 0; k < S.length - 1; k++) {
      for (let i = 0; i < 4; i++) b.ang(steel, S[k][i], S[k + 1][i], lerp(0.22, 0.15, k / n), [-S[k][i][0], 0, -S[k][i][2]], 'bis');
      panel(b, steel, S[k], S[k + 1], k === 0 ? 'K' : 'X', 0.1);
      if (k > 0) ringStruts(b, steel, S[k], 0.09);
    }
    planBrace(b, steel, S[S.length - 1], 0.09); ringStruts(b, steel, S[S.length - 1], 0.1);
    // the two raked window columns: each a 4 chord lattice from half the waist to the bridge
    const cw = 0.75, bw = 1.1;
    [1, -1].forEach((sx) => {
      const A = [[sx * waist, yW, waist], [sx * (waist - 2 * cw) * 1, yW, waist], [sx * (waist - 2 * cw), yW, -waist], [sx * waist, yW, -waist]];
      const xt = sx * (ph - 3.2);
      const B = [[xt + sx * cw, yB, bw], [xt - sx * cw, yB, bw], [xt - sx * cw, yB, -bw], [xt + sx * cw, yB, -bw]];
      truss(b, steel, A, B, 7, 0.14, 0.08, {});
    });
    // bridge: a deep rectangular truss across the top
    const bh = 2.6;
    const A = [[-Lb, yB, bw], [-Lb, yB, -bw], [-Lb, yB + bh * 0.5, -bw * 0.7], [-Lb, yB + bh * 0.5, bw * 0.7]];
    const Bm = [[0, yB, bw], [0, yB, -bw], [0, yB + bh, -bw], [0, yB + bh, bw]];
    const C = [[Lb, yB, bw], [Lb, yB, -bw], [Lb, yB + bh * 0.5, -bw * 0.7], [Lb, yB + bh * 0.5, bw * 0.7]];
    truss(b, steel, A, Bm, 12, 0.14, 0.075, { endA: true }); truss(b, steel, Bm, C, 12, 0.14, 0.075, { endB: true });
    // phases: V strings (two strings converging to a six bundle yoke)
    const attach = [], shield = [];
    [-ph, 0, ph].forEach((px, i) => {
      const foot = [px, yB - str * 0.92, 0];
      [-1, 1].forEach((s) => {
        const top = [px + s * 3.0, yB, 0];
        vString(b, top, foot, hw);
      });
      b.box(hw, 1.2, 0.08, 0.12, px, foot[1] - 0.05, 0);
      const ring = tpl('ring765', () => new THREE.TorusGeometry(0.62, 0.035, 8, 36));
      _q.setFromAxisAngle(V3(0, 0, 1), 0);
      b.geo(M.alu(), ring, V3(px, foot[1] - 0.5, 0.35));
      bundle(b, [px, foot[1] - 0.1, 0], 6, 0.457, hw, o.leads ? 0 : 1.0);
      attach.push({ x: px, y: foot[1] - 0.2, z: 0, n: 6, spacing: 0.457, circuit: 0, phase: i });
    });
    // shield peaks above the columns
    [1, -1].forEach((sx) => {
      const x = sx * (ph - 3.2), tip = [x, yB + bh + 3.6, 0];
      [[0.7, 0.7], [-0.7, 0.7], [-0.7, -0.7], [0.7, -0.7]].forEach(([dx, dz]) => b.ang(steel, [x + dx, yB + bh * 0.55, dz], tip, 0.09, [-dx, 0, -dz], 'bis'));
      b.box(hw, 0.12, 0.1, 0.35, tip[0], tip[1] + 0.05, 0);
      if (!o.leads) b.bar(M.shieldw(), [tip[0], tip[1], -1.0], [tip[0], tip[1], 1.0], 0.007, 6);
      shield.push({ x: tip[0], y: tip[1], z: 0 });
    });
    S[0].forEach((p) => { pier(b, p[0], p[2], 0.55, pierH); b.box(hw, 0.4, 0.05, 0.4, p[0], pierH + 0.02, p[2]); });
    for (let y = 2.8; y < yW; y += 0.4) { const h = hwAt(y); b.bar(hw, [h, y, h], [h + 0.14, y + 0.01, h + 0.14], 0.009, 5); }
    b.build(g);
    if (o.leads > 1) addLeads(g, attach, shield, o.leads, 765);
    g.userData.attach = attach; g.userData.shield = shield; g.userData.kv = 765;
    return g;
  }
  function vString(b, top, foot, hw) {
    const d = V3(foot[0] - top[0], foot[1] - top[1], 0), len = d.length(); d.normalize();
    const n = Math.floor((len - 0.8) / 0.146);
    _q.setFromUnitVectors(Y, d.clone().negate());
    for (let i = 0; i < n; i++) {
      const p = V3(top[0], top[1], 0).add(d.clone().multiplyScalar(0.45 + i * 0.146));
      const q = new THREE.Quaternion().setFromUnitVectors(Y, d.clone().negate());
      b.geo(M.glass(), discGeo(), p, q);
    }
    b.bar(hw, top, [top[0] + d.x * 0.45, top[1] + d.y * 0.45, 0], 0.02, 6);
    b.bar(hw, [foot[0] - d.x * 0.35, foot[1] - d.y * 0.35, 0], foot, 0.02, 6);
  }
  /* conductor and shield leads leaving the structure along the line, sagging away to ±len */
  function addLeads(g, attach, shield, len, kv) {
    const b = new Bld(), rc = kv >= 345 ? 0.0145 : 0.012;
    attach.forEach((a) => bundlePts(a.n, a.spacing).forEach(([dx, dy]) => {
      [-1, 1].forEach((s) => b.cable(M.conductor(), [a.x + dx, a.y + dy, 0], [a.x + dx, a.y + dy - len * 0.06, s * len], len * 0.035, rc, 20, 6));
    }));
    shield.forEach((p) => [-1, 1].forEach((s) => b.cable(M.shieldw(), [p.x, p.y, 0], [p.x, p.y - len * 0.05, s * len], len * 0.03, 0.0065, 20, 5)));
    b.build(g);
  }

  K.define('transmission_tower', {
    size: [15.2, 49.5, 9.3],
    options: { voltage: 345, insulator: null, height: 1, leads: 0 },
    note: 'OPTIONS voltage 138 | 345 | 765; insulator glass | porcelain | polymer (null = seeded); height is a body extension factor; leads = metres of sagging conductor shown each side. Self supporting galvanized lattice. 345 kV: double circuit, vertical phases, twin bundle, about 49 m. 138 kV: double circuit about 32 m. 765 kV: single circuit horizontal, 6 bundle V strings. userData.attach and .shield give wire points.',
    make(o, r) {
      const kv = +o.voltage || 345;
      return kv >= 765 ? horizontal765(o, r) : doubleCircuit(Object.assign({}, o, { voltage: kv }), r);
    },
  });

  /* ============================================================================ pole parts */
  /* a faceted (12 sided) tapered steel pole shaft, flat facets like the real brake-formed tube */
  function facetTube(b, mat, y0, y1, r0, r1, sides, x, z) {
    const g = new THREE.CylinderGeometry(r1, r0, y1 - y0, sides || 12, 1, true).toNonIndexed();
    g.computeVertexNormals();
    b.geo(mat, g, V3(x || 0, (y0 + y1) / 2, z || 0));
  }
  /* a round wood pole, gently tapered, with a top cap */
  function woodPole(b, mat, x, z, h, rb, rt, below) {
    const g = new THREE.CylinderGeometry(rt, rb, h + (below || 0), 20, 1, false);
    b.geo(mat, g, V3(x, (h - (below || 0)) / 2, z));
  }
  /* a pin or post type insulator standing on y (porcelain ANSI 55-5 profile or a polymer post) */
  function pinInsulator(b, kind, x, y, z, hw, kv) {
    const s = (kv || 15) >= 30 ? 1.35 : 1;
    b.bar(hw, [x, y - 0.02, z], [x, y + 0.06, z], 0.013, 6);
    if (kind === 'polymer') {
      b.geo(M.polymer(), polymerGeo(0.3 * s, 0.06, 0.05), V3(x, y + 0.04, z));
      b.box(hw, 0.05, 0.05, 0.05, x, y + 0.04 + 0.3 * s, z);
      return [x, y + 0.06 + 0.3 * s, z];
    }
    const g = tpl('pin' + s, () => {
      const P = [[0, 0], [0.034, 0], [0.04, 0.03], [0.058, 0.05], [0.056, 0.06], [0.044, 0.068], [0.072, 0.095], [0.07, 0.106],
                 [0.048, 0.114], [0.092, 0.14], [0.09, 0.152], [0.05, 0.162], [0.045, 0.176], [0.036, 0.182], [0.042, 0.19], [0.03, 0.2], [0, 0.2]];
      return new THREE.LatheGeometry(P.map(p => new THREE.Vector2(p[0] * s, p[1] * s)), 16);
    });
    b.geo(kind === 'porcelain' ? M.porc() : M.porcGrey(), g, V3(x, y + 0.04, z));
    return [x, y + 0.04 + 0.2 * s, z];
  }
  /* station post / bushing: a lathe with sheds, base flange and top cap. h metres tall */
  let POSTSEG = 12;
  function postGeo(h, r0, rs, pitch, cap) {
    return tpl('post' + [h, r0, rs, pitch, cap, POSTSEG].map(v => (+v).toFixed(3)).join(','), () => {
      const P = [[0, 0], [r0 + 0.07, 0], [r0 + 0.07, 0.05], [r0 + 0.02, 0.07]];
      let y = 0.12;
      while (y < h - 0.2) { P.push([r0, y], [rs, y + pitch * 0.32], [r0, y + pitch * 0.6]); y += pitch; }
      P.push([r0, h - 0.12], [r0 + 0.03, h - 0.1], [r0 + 0.03, h - 0.03], [cap || r0 * 0.6, h - 0.02], [cap || r0 * 0.6, h], [0, h]);
      return new THREE.LatheGeometry(P.map(p => new THREE.Vector2(p[0], p[1])), POSTSEG);
    });
  }
  function post(b, mat, x, y, z, h, r0, rs, pitch) { b.geo(mat, postGeo(h, r0, rs || r0 * 2.1, Math.max(0.15, pitch || 0.11)), V3(x, y, z)); return [x, y + h, z]; }

  /* ========================================================================== monopole 138 */
  K.define('monopole_138', {
    size: [9.2, 30.5, 2.2],
    options: { circuits: 2, insulators: 'suspension', finish: null, height: 27 },
    note: 'OPTIONS circuits 1 | 2; insulators suspension | post (braced horizontal line post); finish galvanized | weathering (null = seeded); height m above ground. Tubular 12 sided tapered steel pole on an anchor bolt pier, curved davit arms, 138 kV polymer strings, shield wire peak. userData.attach/.shield.',
    make(o, r) {
      const g = new THREE.Group(), b = new Bld(), H = o.height || 27, hw = M.galvDark();
      const fin = o.finish || (r() < 0.5 ? 'galvanized' : 'weathering');
      const steel = fin === 'weathering' ? M.rust() : M.galv(r());
      const circuits = +o.circuits === 1 ? 1 : 2, post_ = o.insulators === 'post';
      const r0 = 0.56, r1 = 0.23, rad = (y) => lerp(r0, r1, y / H);
      // shaft in three slip jointed sections, each overlap a slightly proud ring
      const joints = [0.55, H * 0.42, H * 0.76, H];
      for (let i = 0; i < 3; i++) {
        facetTube(b, steel, joints[i], joints[i + 1] + (i < 2 ? 0.9 : 0), rad(joints[i]) * (i ? 1.0 : 1), rad(joints[i + 1] + 0.9) * (i < 2 ? 0.97 : 1));
        if (i) facetTube(b, steel, joints[i] - 0.05, joints[i] + 0.9, rad(joints[i]) * 1.04, rad(joints[i] + 0.9) * 1.03);
      }
      b.geo(steel, new THREE.CircleGeometry(r1, 12).rotateX(-Math.PI / 2), V3(0, H + 0.001, 0));
      // base: pier, grout, base plate, 12 anchor bolts with nuts, hand hole
      pier(b, 0, 0, 0.95, 0.45);
      b.box(steel, 1.55, 0.06, 1.55, 0, 0.5, 0);
      facetTube(b, steel, 0.53, 0.75, r0 + 0.06, r0 + 0.02);
      for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2 + 0.26, R = 0.66;
        b.bar(hw, [Math.cos(a) * R, 0.45, Math.sin(a) * R], [Math.cos(a) * R, 0.66, Math.sin(a) * R], 0.022, 6);
        b.bar(hw, [Math.cos(a) * R, 0.53, Math.sin(a) * R], [Math.cos(a) * R, 0.6, Math.sin(a) * R], 0.04, 6); }
      b.box(M.black(), 0.22, 0.4, 0.03, 0, 1.3, rad(1.3) - 0.005);
      b.box(steel, 0.28, 0.46, 0.02, 0, 1.3, rad(1.3) + 0.012);
      b.box(M.paint(0xf0ece0), 0.2, 0.28, 0.008, 0, 2.2, rad(2.2) + 0.01);
      // arms
      const attach = [], shield = [], ys = [H - 3.1, H - 6.9, H - 10.7], kind = 'polymer';
      const sides = circuits === 2 ? [1, -1] : [1, -1];
      ys.forEach((ya, i) => {
        const sx = circuits === 2 ? null : (i === 1 ? -1 : 1);
        (circuits === 2 ? [1, -1] : [sx]).forEach((s) => {
          const rp = rad(ya), L = circuits === 2 ? (i === 1 ? 3.6 : 3.1) : 3.3;
          b.box(steel, 0.08, 0.7, 0.5, s * (rp + 0.02), ya + 0.05, 0);                  // arm bracket plate
          if (post_) {
            // horizontal line post with a brace underneath
            const tip = [s * (rp + 1.85), ya + 0.12, 0];
            _q.setFromAxisAngle(V3(0, 0, 1), -s * Math.PI / 2);
            b.geo(M.polymer(), polymerGeo(1.8, 0.075, 0.07), V3(s * (rp + 0.05), ya + 0.12, 0), _q.clone());
            b.bar(steel, [s * rp, ya - 1.2, 0], [s * (rp + 1.3), ya + 0.08, 0], 0.035, 8);
            b.box(hw, 0.1, 0.1, 0.35, tip[0], tip[1] + 0.03, 0);
            if (!o.leads) b.bar(M.conductor(), [tip[0], tip[1] + 0.07, -0.9], [tip[0], tip[1] + 0.07, 0.9], 0.0125, 8);
            attach.push({ x: tip[0], y: tip[1] + 0.07, z: 0, n: 1, spacing: 0, circuit: s > 0 ? 0 : 1, phase: i });
          } else {
            // curved davit: a tapering tube rising as it reaches out
            const pts = []; for (let k = 0; k <= 10; k++) { const t = k / 10; pts.push(V3(s * (rp - 0.05 + L * t), ya + 0.9 * t * t, 0)); }
            const curve = new THREE.CatmullRomCurve3(pts);
            const tg = new THREE.TubeGeometry(curve, 20, 0.11, 10, false);
            const pa = tg.attributes.position;           // taper toward the tip
            for (let k = 0; k < pa.count; k++) { const t = Math.abs(pa.getX(k)) / (rp + L); const c = curve.getPoint(Math.min(1, Math.max(0, (Math.abs(pa.getX(k)) - rp) / L)));
              const f = 1 - 0.45 * Math.min(1, Math.max(0, (Math.abs(pa.getX(k)) - rp) / L));
              pa.setY(k, c.y + (pa.getY(k) - c.y) * f); pa.setZ(k, pa.getZ(k) * f); }
            tg.computeVertexNormals();
            b.geo(steel, tg);
            const tip = [s * (rp - 0.05 + L), ya + 0.9, 0];
            b.box(steel, 0.16, 0.06, 0.2, tip[0], tip[1] - 0.02, 0);
            const foot = string(b, [tip[0], tip[1] - 0.06, 0], 1.75, kind, 138, hw);
            bundle(b, foot, 1, 0, hw, o.leads ? 0 : 0.9);
            attach.push({ x: foot[0], y: foot[1] - 0.1, z: 0, n: 1, spacing: 0, circuit: s > 0 ? 0 : 1, phase: i });
          }
        });
      });
      // shield wire peak on the pole top
      b.bar(steel, [0, H - 0.2, 0], [0, H + 1.6, 0], 0.07, 10);
      b.box(hw, 0.1, 0.12, 0.32, 0, H + 1.62, 0);
      if (!o.leads) b.bar(M.shieldw(), [0, H + 1.66, -0.9], [0, H + 1.66, 0.9], 0.0065, 6);
      shield.push({ x: 0, y: H + 1.66, z: 0 });
      // ground lead and step bolts up one face
      for (let y = 3; y < H - 1; y += 0.42) { const rr = rad(y); b.bar(hw, [0, y, rr], [0, y + 0.02, rr + 0.18], 0.011, 5); }
      b.build(g);
      g.userData.attach = attach; g.userData.shield = shield; g.userData.kv = 138;
      return g;
    },
  });

  /* =============================================================================== H-frame */
  K.define('h_frame', {
    size: [9.8, 23.5, 1.4],
    options: { material: 'wood', height: 21, voltage: 138 },
    note: 'OPTIONS material wood | steel (weathering steel tubes); height m above ground; voltage 69 | 138. Two pole H-frame: poles 5.5 m apart, double timber crossarm, timber X brace, three phases horizontal (centre and outboard), static wire on each pole top.',
    make(o, r) {
      const g = new THREE.Group(), b = new Bld(), H = o.height || 21, hw = M.galvDark(), kv = +o.voltage === 69 ? 69 : 138;
      const steel = o.material === 'steel';
      const woodC = ['#665d50', '#5f5a4e', '#6b5e4d', '#5a5046'][Math.floor(r() * 4)];
      const pm = steel ? M.rust() : M.wood(woodC), tm = steel ? M.rust() : M.wood('#6e6456', true);
      const px = 2.75, rb = steel ? 0.33 : 0.23, rt = steel ? 0.18 : 0.14;
      [-px, px].forEach((x) => {
        if (steel) { pier(b, x, 0, rb + 0.25, 0.3); facetTube(b, pm, 0.3, H, rb, rt, 12, x, 0); b.geo(pm, new THREE.CircleGeometry(rt, 12).rotateX(-Math.PI / 2), V3(x, H, 0)); }
        else woodPole(b, pm, x, 0, H, rb, rt);
      });
      const ya = H - 1.6, L = kv === 138 ? 4.6 : 3.6;
      // double crossarm, one timber each side of the poles, through bolted
      [-1, 1].forEach((sz) => {
        b.beam(tm, [-L, ya, sz * (rb * 0.7 + 0.08)], [L, ya, sz * (rb * 0.7 + 0.08)], 0.3, 0.14, [0, 1, 0]);
        b.box(hw, 0.12, 0.12, 0.02, -px, ya, sz * (rb * 0.7 + 0.16)); b.box(hw, 0.12, 0.12, 0.02, px, ya, sz * (rb * 0.7 + 0.16));
      });
      // X brace, two timbers crossing, bolted to the pole faces
      const yb0 = ya - 1.6, yb1 = ya - 7.2;
      b.beam(tm, [-px + 0.1, yb0, rb * 0.6 + 0.08], [px - 0.1, yb1, rb * 0.6 + 0.08], 0.2, 0.1, [0, 0, 1]);
      b.beam(tm, [px - 0.1, yb0, -(rb * 0.6 + 0.08)], [-px + 0.1, yb1, -(rb * 0.6 + 0.08)], 0.2, 0.1, [0, 0, 1]);
      // knee braces under the crossarm
      [-1, 1].forEach((s) => b.beam(hw, [s * (px - 0.2), ya - 1.5, 0], [s * (px - 1.6), ya - 0.14, 0], 0.06, 0.02, [0, 0, 1]));
      const attach = [], shield = [];
      const kind = r() < 0.5 ? 'porcelain' : 'grey';
      [-L + 0.25, 0, L - 0.25].forEach((x, i) => {
        b.box(hw, 0.12, 0.04, rb * 1.4 + 0.5, x, ya + 0.17, 0);
        const foot = string(b, [x, ya - 0.18, 0], kv === 138 ? 1.6 : 1.05, kind, kv, hw);
        bundle(b, foot, 1, 0, hw, o.leads ? 0 : 0.9);
        attach.push({ x, y: foot[1] - 0.1, z: 0, n: 1, spacing: 0, circuit: 0, phase: i });
      });
      [-px, px].forEach((x) => {
        b.box(hw, 0.1, 0.25, 0.1, x + Math.sign(x) * (rt + 0.02), H - 0.1, 0);
        b.box(hw, 0.08, 0.08, 0.3, x + Math.sign(x) * (rt + 0.06), H + 0.05, 0);
        if (!o.leads) b.bar(M.shieldw(), [x + Math.sign(x) * (rt + 0.06), H + 0.1, -0.9], [x + Math.sign(x) * (rt + 0.06), H + 0.1, 0.9], 0.0065, 6);
        shield.push({ x: x + Math.sign(x) * (rt + 0.06), y: H + 0.1, z: 0 });
        // pole ground wire in its moulding
        b.box(M.paint(0x4a4038, 0.8), 0.03, H - 0.4, 0.02, x, H / 2, rb * 0.7 + 0.01);
      });
      b.build(g);
      g.userData.attach = attach; g.userData.shield = shield; g.userData.kv = kv;
      return g;
    },
  });

  /* ========================================================================== utility pole */
  K.define('utility_pole', {
    size: [2.6, 11.2, 4.6],
    options: { transformer: true, streetlight: false, guy: true, guyDir: -1, insulators: null, height: 10.7 },
    note: 'OPTIONS transformer (pole mount can), streetlight (cobra head on a davit), guy (down guy with yellow guard), guyDir -1 = anchor toward -z, 1 = +z; insulators porcelain | polymer (null = seeded); height m above ground (10.7 is a 40 ft class 3 pole). Three phase distribution: treated pine pole, 8 ft crossarm on flat braces, two crossarm pins and a pole top pin, neutral on a spool, cutout and arrester feeding a 25 to 50 kVA can.',
    make(o, r) {
      const g = new THREE.Group(), b = new Bld(), H = o.height || 10.7, hw = M.galvDark();
      const woodC = ['#6b6152', '#615a4e', '#6f6250', '#5d5347'][Math.floor(r() * 4)];
      const pole = M.wood(woodC), arm = M.wood('#746a5a', true);
      const kind = o.insulators || (r() < 0.6 ? 'grey' : 'polymer');
      const rb = 0.15, rt = 0.105, rad = (y) => lerp(rb, rt, y / H);
      woodPole(b, pole, 0, 0, H, rb, rt);
      b.geo(M.paint(0x3a3a38, 0.7), new THREE.CylinderGeometry(rt + 0.004, rt + 0.004, 0.02, 20), V3(0, H - 0.01, 0));
      const ya = H - 0.42, az = rad(ya) + 0.046;
      b.beam(arm, [-1.22, ya, az], [1.22, ya, az], 0.089, 0.114, [0, 0, 1]);
      b.bar(hw, [0, ya, -rad(ya) - 0.03], [0, ya, az + 0.07], 0.009, 6);                // through bolt
      [-1, 1].forEach((s) => b.beam(hw, [s * 0.04, ya - 0.72, rad(ya - 0.72) + 0.01], [s * 0.62, ya - 0.06, az], 0.035, 0.006, [0, 0, 1]));
      const attach = [], ph = [];
      [-1.07, 1.07].forEach((x) => ph.push(pinInsulator(b, kind, x, ya + 0.057, az, hw)));
      // pole top pin on its bracket
      b.box(hw, 0.05, 0.4, 0.06, 0, H - 0.25, rad(H) + 0.03);
      ph.push(pinInsulator(b, kind, 0, H + 0.05, rad(H) + 0.08, hw));
      ph.forEach((p, i) => {
        b.bar(M.conductor(), [p[0], p[1] + 0.012, p[2] - (o.leads ? 0 : 0.45)], [p[0], p[1] + 0.012, p[2] + (o.leads ? 0 : 0.45)], 0.0085, 8);
        attach.push({ x: p[0], y: p[1] + 0.012, z: p[2], n: 1, spacing: 0, circuit: 0, phase: i });
      });
      // neutral on a spool insulator, on a clevis
      const yn = H - 1.9, rn = rad(yn);
      b.box(hw, 0.05, 0.16, 0.12, 0, yn, rn + 0.05);
      b.geo(M.porcGrey(), tpl('spool', () => new THREE.LatheGeometry([[0.02, 0], [0.04, 0], [0.042, 0.01], [0.03, 0.03], [0.03, 0.05], [0.042, 0.07], [0.04, 0.08], [0.02, 0.08]].map(p => new THREE.Vector2(p[0], p[1])), 14)),
        V3(0, yn - 0.04, rn + 0.12));
      b.bar(M.conductor(), [0.05, yn, rn + 0.12 - (o.leads ? 0 : 0.7)], [0.05, yn, rn + 0.12 + (o.leads ? 0 : 0.7)], 0.0075, 8);
      const neutral = { x: 0.05, y: yn, z: rn + 0.12, n: 1, spacing: 0, circuit: 0, phase: 3, neutral: true };
      const tr = o.transformer !== false;
      if (tr) {
        // a 50 kVA can on a hanger bracket, ANSI 70 grey
        const yc = H - 3.55, rc = 0.29, zc = rad(yc) + rc + 0.07, can = M.paint(0x8f9594, 0.45);
        b.box(hw, 0.08, 0.9, 0.05, 0, yc + 0.45, rad(yc + 0.45) + 0.02);
        b.geo(can, new THREE.CylinderGeometry(rc, rc, 0.95, 28), V3(0, yc + 0.475, zc));
        b.geo(can, new THREE.CylinderGeometry(rc + 0.02, rc + 0.02, 0.05, 28), V3(0, yc + 0.97, zc));
        b.geo(can, new THREE.SphereGeometry(rc + 0.01, 28, 6, 0, Math.PI * 2, 0, 0.5), V3(0, yc + 0.84, zc));
        [0.2, 0.6].forEach((yy) => b.geo(can, new THREE.CylinderGeometry(rc + 0.008, rc + 0.008, 0.03, 28), V3(0, yc + yy, zc)));
        b.box(can, 0.2, 0.22, 0.14, 0.18, yc + 0.72, zc + 0.18, 0.7);               // LV bushing boss
        const hvTop = post(b, M.porcGrey(), 0, yc + 1.03, zc, 0.3, 0.028, 0.045, 0.06);
        [-0.1, 0, 0.1].forEach((dx) => post(b, M.porcGrey(), rc * 0.7 + dx * 0.3, yc + 0.6 + dx, zc + rc * 0.75, 0.1, 0.02, 0.035, 0.04));
        b.box(M.paint(0xe8e2cf, 0.5), 0.12, 0.08, 0.01, 0, yc + 0.35, zc + rc + 0.005);  // kVA stencil plate
        // cutout on the crossarm end, arrester beside it, leads to the bushing
        const cx = 0.78, cy = ya - 0.12;
        b.box(hw, 0.05, 0.05, 0.22, cx, cy, az + 0.12);
        _q.setFromAxisAngle(V3(1, 0, 0), 0.32);
        b.geo(M.porcGrey(), postGeo(0.36, 0.028, 0.042, 0.055), V3(cx, cy - 0.28, az + 0.25), _q.clone());
        b.bar(M.paint(0x3b3632, 0.6), [cx + 0.07, cy - 0.3, az + 0.24], [cx + 0.07, cy + 0.04, az + 0.35], 0.014, 8);  // fuse tube
        post(b, M.polymer(), cx - 0.3, ya - 0.3, az + 0.14, 0.3, 0.026, 0.042, 0.05);
        b.cable(hw, [1.07, ya + 0.25, az], [cx + 0.02, cy + 0.08, az + 0.33], 0.1, 0.005, 8, 5);
        b.cable(hw, [cx + 0.02, cy - 0.3, az + 0.24], hvTop, 0.25, 0.005, 12, 5);
        b.cable(M.black(), [rc * 0.7, yc + 0.7, zc + rc * 0.8], [0.05, yn, rn + 0.12], 0.15, 0.007, 10, 5);   // secondary to the neutral
      }
      if (o.streetlight) {
        const ys = H - 4.9, rs = rad(ys);
        b.box(hw, 0.12, 0.3, 0.05, rs + 0.02, ys, 0, Math.PI / 2);
        const pts = []; for (let k = 0; k <= 8; k++) { const t = k / 8; pts.push(V3(rs + 1.8 * t, ys + 0.45 * Math.sin(t * Math.PI / 2), 0)); }
        b.geo(M.galv(0), new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 16, 0.03, 8, false));
        const hx = rs + 1.8;
        const head = rbox(0.66, 0.16, 0.32, 0.06);
        b.geo(M.paint(0x9a9e9f, 0.4), head, V3(hx + 0.22, ys + 0.44, 0));
        b.box(K.finish.glass(0x3a4046), 0.4, 0.04, 0.24, hx + 0.3, ys + 0.36, 0);
        b.geo(M.black(), new THREE.CylinderGeometry(0.035, 0.035, 0.05, 12), V3(hx + 0.1, ys + 0.55, 0));
      }
      if (o.guy !== false) {
        const gd = o.guyDir === 1 ? 1 : -1;
        const top = [0, H - 0.6, gd * (rad(H - 0.6) + 0.02)], anc = [0, 0.25, gd * 4.3];
        b.box(hw, 0.06, 0.12, 0.06, 0, H - 0.6, gd * (rad(H - 0.6) + 0.02));
        b.bar(hw, top, anc, 0.0048, 5);
        b.bar(hw, anc, [0, -0.2, gd * 4.45], 0.014, 6);                              // anchor rod eye
        const d = V3(anc[0] - top[0], anc[1] - top[1], anc[2] - top[2]).normalize(), L = 2.5 / Math.abs(d.y);
        b.bar(M.paint(0xe8c21a, 0.45), anc, [anc[0] - d.x * L, anc[1] - d.y * L, anc[2] - d.z * L], 0.025, 10);  // guy guard
        const gi = L3(top, anc, 0.22);
        b.bar(M.polymer(), gi, L3(top, anc, 0.3), 0.012, 8);                     // fibreglass guy strain insulator
      }
      // ground wire moulding and the pole tag
      b.box(M.paint(0x3f3a33, 0.8), 0.028, H - 0.6, 0.014, 0, H / 2 - 0.2, -rad(H / 2) - 0.004);
      b.box(M.alu(), 0.07, 0.1, 0.004, 0, 1.8, rad(1.8) + 0.002);
      b.build(g);
      attach.push(neutral);
      g.userData.attach = attach; g.userData.shield = []; g.userData.kv = 13.8;
      return g;
    },
  });

  /* ============================================================================ power line */
  const LINE = { transmission_tower: [330, 0.034], monopole_138: [200, 0.03], h_frame: [230, 0.032], utility_pole: [45, 0.02] };
  K.define('power_line', {
    size: [15.2, 49.5, 660],
    options: { structure: 'transmission_tower', spans: 2, span: null, sag: null, structures: null },
    note: 'OPTIONS structure transmission_tower | monopole_138 | h_frame | utility_pole; spans; span m (null = typical: 330, 200, 230, 45); sag m at mid span (null = about span x 0.034); structures [[x, z, rotY], ...] places them yourself and the wires follow; voltage, insulator, insulators, height, material, circuits, transformer, streetlight, guy pass through to the structure. Structures along z with every conductor and shield wire strung as a sagging span between the attach points each structure publishes; bundles get spacers every 70 m.',
    make(o, r) {
      const g = new THREE.Group(), type = o.structure || 'transmission_tower', D = LINE[type] || LINE.transmission_tower;
      const span = o.span || D[0], n = o.spans || 2, sag = o.sag != null ? o.sag : span * D[1];
      const places = o.structures || Array.from({ length: n + 1 }, (_, i) => [0, (i - n / 2) * span, 0]);
      const so = { seed: o.seed, leads: 0.001 };
      ['voltage', 'insulator', 'insulators', 'height', 'material', 'circuits', 'transformer', 'streetlight', 'guy'].forEach((k) => { if (o[k] != null) so[k] = o[k]; });
      const made = places.map(([x, z, ry], i) => {
        let so2 = so;
        if (type === 'utility_pole') {             // guys only at the dead ends, a can on every other pole
          so2 = Object.assign({}, so, { seed: (o.seed || 1) * 13 + i });
          if (o.guy == null) { so2.guy = i === 0 || i === places.length - 1; so2.guyDir = i === 0 ? -1 : 1; }
          if (o.transformer == null) so2.transformer = i % 2 === 1;
        }
        const t = K.make(type, so2); t.position.set(x, 0, z); t.rotation.y = ry || 0; t.updateMatrix(); g.add(t); return t;
      });
      const b = new Bld(), cm = M.conductor(), sm = M.shieldw(), hw = M.galvDark();
      const W = (t, p, dx, dy) => V3(p.x + (dx || 0), p.y + (dy || 0), p.z).applyMatrix4(t.matrix);
      for (let i = 0; i < made.length - 1; i++) {
        const A = made[i], B = made[i + 1], la = A.userData.attach || [], lb = B.userData.attach || [];
        const segs = Math.max(24, Math.min(64, Math.round(A.position.distanceTo(B.position) / 6)));
        const rc = (A.userData.kv || 0) >= 138 ? 0.0145 : 0.0085;
        la.forEach((pa, k) => {
          const pb = lb[k]; if (!pb) return;
          const sg = pa.neutral ? sag * 0.85 : sag;
          const offs = bundlePts(pa.n, pa.spacing);
          offs.forEach(([dx, dy]) => b.cable(cm, W(A, pa, dx, dy), W(B, pb, dx, dy), sg, rc, segs, 6));
          if (pa.n > 1) {                                   // spacer dampers
            const L = A.position.distanceTo(B.position), m = Math.max(1, Math.floor(L / 70));
            for (let s = 1; s <= m; s++) {
              const t = s / (m + 1), P0 = W(A, pa), P1 = W(B, pb);
              const c = P0.clone().lerp(P1, t); c.y -= sg * 4 * t * (1 - t);
              const d = P1.clone().sub(P0).setY(0).normalize(), side = V3(-d.z, 0, d.x);
              const R = pa.n === 2 ? pa.spacing / 2 : pa.spacing / (2 * Math.sin(Math.PI / pa.n));
              if (pa.n === 2) b.bar(hw, c.clone().addScaledVector(side, -R), c.clone().addScaledVector(side, R), 0.02, 6);
              else { const q = c.clone(); q.y -= R; b.geo(hw, tpl('spc' + pa.n, () => new THREE.TorusGeometry(R, 0.018, 5, pa.n)), q, new THREE.Quaternion().setFromUnitVectors(V3(0, 0, 1), d)); }
            }
          }
        });
        (A.userData.shield || []).forEach((pa, k) => {
          const pb = (B.userData.shield || [])[k]; if (!pb) return;
          b.cable(sm, W(A, pa), W(B, pb), sag * 0.78, 0.0065, segs, 5);
        });
      }
      b.build(g);
      g.children.forEach((c) => { if (c.isMesh) c.castShadow = true; });
      return g;
    },
  });

  /* ====================================================================== yard equipment */
  const GRAV = new Map();
  function gravelMat(tone) {
    const key = tone || '#a39f97';
    if (!GRAV.has(key)) {
      const N = 512, c = document.createElement('canvas'); c.width = c.height = N;
      const x = c.getContext('2d'), r = K.rng(733);
      x.fillStyle = key; x.fillRect(0, 0, N, N);
      for (let i = 0; i < 9000; i++) {
        const k = 0.6 + r() * 0.75, rr = 1.2 + r() * 3.2, px = r() * N, py = r() * N;
        const base = parseInt(key.slice(1), 16), R = (base >> 16) * k, G = ((base >> 8) & 255) * k, B = (base & 255) * k * (0.95 + r() * 0.1);
        x.fillStyle = 'rgb(' + (R | 0) + ',' + (G | 0) + ',' + (B | 0) + ')';
        x.beginPath(); x.ellipse(px, py, rr, rr * (0.6 + r() * 0.4), r() * 3, 0, 6.3); x.fill();
        if (px < 6 || py < 6) { x.beginPath(); x.ellipse(px + N, py + N, rr, rr, 0, 0, 6.3); x.fill(); }
      }
      const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace;
      t.anisotropy = 8; t.userData.metres = 1.6;
      GRAV.set(key, kmat('pw_gravel' + key, { color: 0xffffff, roughness: 0.97, map: t }));
    }
    return GRAV.get(key);
  }
  function pad(b, x0, z0, x1, z1, tone) {
    b.box(gravelMat(tone), x1 - x0, 0.1, z1 - z0, (x0 + x1) / 2, 0.05, (z0 + z1) / 2);
  }
  /* chain link: a mesh texture on a thin transparent panel, 50 mm diamonds */
  let LINK = null;
  function linkMat() {
    if (LINK) return LINK;
    const N = 128, c = document.createElement('canvas'); c.width = c.height = N;
    const x = c.getContext('2d'); x.fillStyle = '#000'; x.fillRect(0, 0, N, N);
    x.strokeStyle = '#fff'; x.lineWidth = 9;
    for (let k = -1; k <= 1; k++) { x.beginPath(); x.moveTo(k * N, 0); x.lineTo(k * N + N, N); x.stroke(); x.beginPath(); x.moveTo(k * N + N, 0); x.lineTo(k * N, N); x.stroke(); }
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8;
    t.repeat.set(1, 1);
    LINK = kmat('pw_link', { color: 0xb3b7b8, metalness: 0.6, roughness: 0.45, alphaMap: t, transparent: true, opacity: 0.95,
                               side: THREE.DoubleSide, depthWrite: false });
    LINK.userData.metres = 0.07;
    return LINK;
  }
  /* a fence run a->b along the ground: posts every 3 m, top rail, fabric, 3 strand barbed arm */
  function fence(b, a, c, h, o) {
    o = o || {};
    const g = M.galv(0), dx = c[0] - a[0], dz = c[1] - a[1], L = Math.hypot(dx, dz), ux = dx / L, uz = dz / L;
    const nx = -uz, nz = ux, n = Math.max(1, Math.round(L / 3));
    for (let i = 0; i <= n; i++) {
      const px = a[0] + dx * i / n, pz = a[1] + dz * i / n, end = i === 0 || i === n;
      b.bar(g, [px, 0, pz], [px, h + 0.05, pz], end ? 0.05 : 0.036, 10);
      b.geo(g, tpl('cap', () => new THREE.SphereGeometry(1, 10, 5, 0, Math.PI * 2, 0, Math.PI / 2)), V3(px, h + 0.05, pz), null, V3(end ? 0.055 : 0.04, 0.03, end ? 0.055 : 0.04));
      const tip = [px + nx * 0.32, h + 0.36, pz + nz * 0.32];
      b.bar(g, [px, h, pz], tip, 0.018, 5);
    }
    b.bar(g, [a[0], h - 0.04, a[1]], [c[0], h - 0.04, c[1]], 0.021, 8);
    b.bar(g, [a[0], 0.08, a[1]], [c[0], 0.08, c[1]], 0.004, 4);                    // bottom tension wire
    for (let k = 1; k <= 3; k++) {
      const f = k / 3, oy = h + 0.36 * f, on = 0.32 * f;
      b.bar(g, [a[0] + nx * on, oy, a[1] + nz * on], [c[0] + nx * on, oy, c[1] + nz * on], 0.0035, 4);
    }
    const pg = new THREE.PlaneGeometry(L, h - 0.1);
    const uv = pg.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * L / 0.07, uv.getY(i) * (h - 0.1) / 0.07);
    _q.setFromAxisAngle(Y, -Math.atan2(dz, dx));
    b.geo(linkMat(), pg, V3((a[0] + c[0]) / 2, (h - 0.1) / 2 + 0.06, (a[1] + c[1]) / 2), _q.clone());
  }

  /* a power transformer, tank long along x, HV bushings along the -z edge, LV along +z.
   * s scales it (1 = a 345/138 kV autotransformer, about 300 MVA). Returns { hv, lv } terminals. */
  function powerTransformer(b, x, z, s, o) {
    o = o || {};
    const grey = M.paint(o.color || 0x8f9594, 0.42), hw = M.galvDark();
    const W = 6.4 * s, D = 3.1 * s, H = 4.1 * s, y0 = 0.45;
    b.box(M.concrete(), W + 5.5 * s, 0.35, D + 4.5 * s, x, 0, z);                           // pad
    [[1, 0], [-1, 0]].forEach(([sx]) => b.box(M.concrete(), 0.25, 0.3, D + 4.5 * s, x + sx * (W + 5.5 * s) / 2, 0.3, z)); // containment curb
    [1, -1].forEach((sz) => b.box(M.concrete(), W + 5.5 * s, 0.3, 0.25, x, 0.3, z + sz * (D + 4.5 * s) / 2));
    b.box(grey, W, 0.25, D, x, y0, z);
    b.geo(grey, rbox(W, H, D, 0.06), V3(x, y0 + 0.25 + H / 2, z));
    b.box(grey, W + 0.14, 0.12, D + 0.14, x, y0 + 0.25 + H - 0.06, z);                        // cover flange
    for (let i = 0; i <= Math.floor(W / 0.8); i++) {                                           // stiffeners
      const xx = x - W / 2 + 0.2 + i * (W - 0.4) / Math.floor(W / 0.8);
      [1, -1].forEach((sz) => b.box(grey, 0.1, H - 0.3, 0.1, xx, y0 + 0.25 + H / 2, z + sz * (D / 2 + 0.05)));
    }
    const yt = y0 + 0.25 + H;
    // radiator banks on both ends, fans beneath
    [1, -1].forEach((sx) => {
      [-1, 1].forEach((bz) => {
        const bx = x + sx * (W / 2 + 0.25), zc = z + bz * D * 0.26, nF = Math.round(18 * s + 4);
        const hR = H * 0.78, yR = y0 + 0.9 * s;
        for (let f = 0; f < nF; f++) b.box(grey, 0.55 * s + 0.2, hR, 0.012, bx + sx * (0.3 * s + 0.1), yR + hR / 2, zc - D * 0.2 + f * (D * 0.4) / (nF - 1));
        [yR + 0.05, yR + hR - 0.05].forEach((yy) => b.bar(grey, [bx - sx * 0.25, yy, zc], [bx + sx * (0.65 * s + 0.3), yy, zc], 0.07 * s + 0.03, 8));
        _q.setFromAxisAngle(V3(0, 0, 1), Math.PI / 2);
        b.geo(M.paint(0x6f7677, 0.5), tpl('fan', () => new THREE.CylinderGeometry(0.42, 0.42, 0.28, 20, 1, true)), V3(bx + sx * (0.3 * s + 0.1), yR - 0.25, zc), new THREE.Quaternion().setFromAxisAngle(V3(1, 0, 0), 0));
      });
    });
    // conservator on stands, Buchholz pipe
    const cz = z + D * 0.28, cy = yt + 1.15 * s, cl = W * 0.62;
    _q.setFromAxisAngle(V3(0, 0, 1), Math.PI / 2);
    b.geo(grey, new THREE.CylinderGeometry(0.5 * s, 0.5 * s, cl, 24), V3(x + W * 0.12, cy, cz), _q.clone());
    [-1, 1].forEach((e) => b.geo(grey, new THREE.SphereGeometry(0.5 * s, 20, 8, 0, Math.PI * 2, 0, Math.PI / 2), V3(x + W * 0.12 + e * cl / 2, cy, cz), new THREE.Quaternion().setFromAxisAngle(V3(0, 0, 1), -e * Math.PI / 2)));
    [-0.35, 0.35].forEach((f) => b.beam(grey, [x + W * 0.12 + f * cl, yt, cz], [x + W * 0.12 + f * cl, cy - 0.4 * s, cz], 0.12, 0.12));
    b.bar(grey, [x - W * 0.15, yt, cz], [x - W * 0.15, cy - 0.45 * s, cz], 0.05, 8);
    // bushings: three HV on turrets along -z, three LV and a neutral along +z
    const hvH = (o.hvH || 4.6) * s, lvH = (o.lvH || 2.6) * s, porc = o.polymer ? M.polymer() : M.porc(), hv = [], lv = [];
    const px = [-1, 0, 1].map((i) => x + i * W * 0.3);
    px.forEach((xx) => {
      b.geo(grey, new THREE.CylinderGeometry(0.34 * s, 0.4 * s, 0.6 * s, 18), V3(xx, yt + 0.3 * s, z - D * 0.3));
      hv.push(post(b, porc, xx, yt + 0.6 * s, z - D * 0.3, hvH, 0.13 * s + 0.03, 0.26 * s + 0.05, 0.13));
      b.bar(M.alu(), hv[hv.length - 1], [xx, hv[hv.length - 1][1] + 0.25, z - D * 0.3], 0.04, 8);
      hv[hv.length - 1] = [xx, hv[hv.length - 1][1] + 0.25, z - D * 0.3];
      // surge arrester on a bracket beside each HV bushing
      const ax = xx + 0.9 * s, az = z - D / 2 - 0.5 * s;
      b.box(grey, 0.5 * s, 0.1, 0.9 * s, ax, yt - 0.35, z - D / 2 - 0.25 * s);
      post(b, M.polymer(), ax, yt - 0.3, az, hvH * 0.75, 0.1 * s + 0.02, 0.2 * s + 0.04, 0.1);
      b.cable(M.alu(), [ax, yt - 0.3 + hvH * 0.75, az], hv[hv.length - 1], 0.4, 0.02, 10, 6);
    });
    px.forEach((xx) => { lv.push(post(b, porc, xx, yt, z + D * 0.32, lvH, 0.1 * s + 0.02, 0.2 * s + 0.04, 0.12)); });
    post(b, porc, x + W * 0.44, yt, z + D * 0.32, lvH * 0.45, 0.07, 0.13, 0.1);
    // control cabinet, ladder, nameplate, tap changer compartment
    b.geo(grey, rbox(1.3 * s, 1.9 * s, 0.6 * s, 0.03), V3(x + W * 0.25, y0 + 1.6 * s, z + D / 2 + 0.3 * s + 0.1));
    b.box(M.black(), 0.02, 1.6 * s, 0.01, x + W * 0.25, y0 + 1.6 * s, z + D / 2 + 0.62 * s + 0.1);
    b.geo(grey, rbox(1.0 * s, 2.0 * s, 0.7 * s, 0.03), V3(x - W * 0.3, y0 + 1.9 * s, z + D / 2 + 0.35 * s));
    b.box(M.white(), 0.5, 0.35, 0.01, x - W * 0.05, y0 + 2.2 * s, z + D / 2 + 0.11);
    [-0.2, 0.2].forEach((dx) => b.bar(hw, [x - W * 0.45 + dx, 0.4, z + D / 2 + 0.2], [x - W * 0.45 + dx, yt, z + D / 2 + 0.2], 0.02, 6));
    for (let yy = 0.7; yy < yt; yy += 0.3) b.bar(hw, [x - W * 0.45 - 0.2, yy, z + D / 2 + 0.2], [x - W * 0.45 + 0.2, yy, z + D / 2 + 0.2], 0.012, 5);
    return { hv, lv, top: yt };
  }

  /* SF6 dead tank breaker: three tanks, axis along z, two bushings each raked in a V */
  function deadTank(b, x, z, ps, kv) {
    const s = kv >= 345 ? 1 : 0.62, grey = M.paint(0x9aa0a0, 0.45), hw = M.galvDark(), ins = [], outs = [];
    const yT = 2.5 * s + 0.4, R = 0.48 * s, Lt = 2.6 * s, bh = (kv >= 345 ? 3.9 : 2.3);
    [-1, 0, 1].forEach((i) => {
      const xx = x + i * ps;
      _q.setFromAxisAngle(V3(1, 0, 0), Math.PI / 2);
      b.geo(grey, new THREE.CylinderGeometry(R, R, Lt, 24), V3(xx, yT, z), _q.clone());
      [-1, 1].forEach((e) => b.geo(grey, new THREE.SphereGeometry(R, 20, 8, 0, Math.PI * 2, 0, Math.PI / 2), V3(xx, yT, z + e * Lt / 2), new THREE.Quaternion().setFromAxisAngle(V3(1, 0, 0), e * Math.PI / 2)));
      [-1, 1].forEach((e) => {
        const base = V3(xx, yT + R * 0.8, z + e * Lt * 0.3), tilt = e * 0.3;
        const q = new THREE.Quaternion().setFromAxisAngle(V3(1, 0, 0), tilt);
        b.geo(grey, new THREE.CylinderGeometry(R * 0.62, R * 0.62, 0.75 * s, 20), base.clone().add(V3(0, 0.3 * s, 0).applyQuaternion(q)), q.clone());  // CT housing
        const pb = base.clone().add(V3(0, 0.62 * s, 0).applyQuaternion(q));
        b.geo(M.polymer(), postGeo(bh, 0.1 * s + 0.03, 0.2 * s + 0.05, 0.15), pb, q.clone());
        const top = pb.clone().add(V3(0, bh + 0.1, 0).applyQuaternion(q));
        b.box(M.alu(), 0.2, 0.08, 0.2, top.x, top.y, top.z);
        (e < 0 ? ins : outs).push([top.x, top.y + 0.04, top.z]);
      });
      // legs and frame
      [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([a, c]) => b.beam(M.galv(0), [xx + a * R * 0.8, 0.3, z + c * Lt * 0.35], [xx + a * R * 0.8, yT - R * 0.6, z + c * Lt * 0.35], 0.12, 0.12));
      b.box(M.concrete(), R * 2.4, 0.35, Lt * 1.0, xx, 0, z);
    });
    b.beam(M.galv(0), [x - ps - 0.5, yT - R - 0.1, z], [x + ps + 0.5, yT - R - 0.1, z], 0.18, 0.18);
    b.geo(grey, rbox(0.9 * s + 0.3, 1.8 * s, 0.7, 0.03), V3(x + ps + R + 0.7, 1.3 * s + 0.4, z));   // mechanism cabinet
    b.box(M.concrete(), 1.4, 0.35, 1.1, x + ps + R + 0.7, 0, z);
    return { ins, outs };
  }

  /* vertical break disconnect: three phases on a beam on two pipe columns, two posts a phase */
  function disconnect(b, x, z, ps, kv, open) {
    const s = kv >= 345 ? 1 : 0.65, st = M.galv(0), hw = M.galvDark(), yS = 4.6 * s + 0.6, ph = kv >= 345 ? 3.0 : 1.9, gap = 2.4 * s + 0.4;
    [-1.5 * ps, 1.5 * ps].forEach((dx) => {
      b.bar(st, [x + dx * 0.95, 0.3, z], [x + dx * 0.95, yS, z], 0.16 * s + 0.04, 12);
      pier(b, x + dx * 0.95, z, 0.4, 0.3);
    });
    b.beam(st, [x - 1.6 * ps, yS + 0.2, z], [x + 1.6 * ps, yS + 0.2, z], 0.3, 0.3 * s + 0.1);
    const a = [], c = [];
    [-1, 0, 1].forEach((i) => {
      const xx = x + i * ps;
      b.beam(st, [xx, yS + 0.35, z - gap / 2 - 0.3], [xx, yS + 0.35, z + gap / 2 + 0.3], 0.2, 0.2);
      const t0 = post(b, M.porcGrey(), xx, yS + 0.45, z - gap / 2, ph, 0.09 * s + 0.02, 0.17 * s + 0.04, 0.12);
      const t1 = post(b, M.porcGrey(), xx, yS + 0.45, z + gap / 2, ph, 0.09 * s + 0.02, 0.17 * s + 0.04, 0.12);
      b.box(M.alu(), 0.22, 0.12, 0.3, t0[0], t0[1] + 0.06, t0[2]); b.box(M.alu(), 0.22, 0.12, 0.3, t1[0], t1[1] + 0.06, t1[2]);
      if (open) b.bar(M.alu(), [xx, t0[1] + 0.12, t0[2]], [xx, t0[1] + 0.12 + gap * 0.95, t0[2] + 0.35], 0.05, 10);
      else b.bar(M.alu(), [xx, t0[1] + 0.12, t0[2]], [xx, t1[1] + 0.12, t1[2]], 0.05, 10);
      b.bar(M.alu(), [xx, t1[1] + 0.14, t1[2]], [xx, t1[1] + 0.6, t1[2] + 0.25], 0.012, 5);    // arcing horn
      a.push([xx, t0[1] + 0.15, t0[2]]); c.push([xx, t1[1] + 0.15, t1[2]]);
    });
    // operating pipe and the crank box
    b.bar(st, [x - 1.5 * ps * 0.95 + 0.3, 1.0, z], [x - 1.5 * ps * 0.95 + 0.3, yS, z], 0.03, 8);
    b.box(M.paint(0x9aa0a0, 0.5), 0.35, 0.5, 0.25, x - 1.5 * ps * 0.95 + 0.3, 1.1, z + 0.2);
    return { a, c };
  }

  /* dead end gantry: two square lattice columns and a lattice beam, strain strings each phase */
  function gantry(b, x, z, ps, kv, H, outDir) {
    const st = M.galv(0), hw = M.galvDark(), cw = kv >= 345 ? 0.55 : 0.4, span = 3 * ps + 3;
    [-1, 1].forEach((sx) => {
      const cx = x + sx * span / 2;
      truss(b, st, sq(cw * 1.35, 0.4).map(p => [p[0] + cx, p[1], p[2] + z]), sq(cw, H).map(p => [p[0] + cx, p[1], p[2] + z]),
            Math.round(H / 1.4), 0.1, 0.055, { endB: true, endA: true });
      [[1, 1], [-1, 1], [-1, -1], [1, -1]].forEach(([a, c]) => pier(b, cx + a * cw * 1.35, z + c * cw * 1.35, 0.3, 0.4));
      // shield peak
      b.bar(st, [cx, H, z], [cx, H + 3.5, z], 0.06, 8);
    });
    const bh = cw * 1.6, x0 = x - span / 2, x1 = x + span / 2;
    truss(b, st, [[x0, H - bh, z + cw], [x0, H - bh, z - cw], [x0, H, z - cw], [x0, H, z + cw]],
                 [[x1, H - bh, z + cw], [x1, H - bh, z - cw], [x1, H, z - cw], [x1, H, z + cw]], Math.round(span / 1.2), 0.09, 0.05, {});
    const pts = [];
    [-1, 0, 1].forEach((i) => {
      const xx = x + i * ps;
      // strain string pointing along outDir, conductor dropping from its end
      [-1, 1].forEach((dir) => {
        const len = kv >= 345 ? 3.4 : 1.8, a = [xx, H - bh, z + dir * cw], e = [xx, H - bh - 0.4, z + dir * (cw + len)];
        const d = V3(e[0] - a[0], e[1] - a[1], e[2] - a[2]).normalize(), n = Math.floor((len - 0.5) / 0.146);
        const q = new THREE.Quaternion().setFromUnitVectors(Y, d.clone().negate());
        if (kv >= 345) for (let k = 0; k < n; k++) b.geo(M.glass(), discGeo(8), V3(a[0], a[1], a[2]).addScaledVector(d, 0.3 + k * 0.146), q);
        else b.geo(M.polymer(), postGeo(len - 0.4, 0.02, 0.06, 0.15, 0.03), V3(a[0], a[1], a[2]).addScaledVector(d, len - 0.1), q);
        b.bar(hw, a, [a[0] + d.x * 0.3, a[1] + d.y * 0.3, a[2] + d.z * 0.3], 0.02, 6);
        pts.push({ dir, p: e, phase: i + 1 });
      });
    });
    return pts;
  }

  /* prefab control house: insulated metal panels, low slope roof, door, HVAC unit, wall pack */
  function controlHouse(b, x, z, w, d, h, ry) {
    const wall = kmat('pw_panel', { color: 0xffffff, roughness: 0.6, metalness: 0.2, map: K.tex('corrugated', { color: '#d9d2c1' }) });
    const trim = M.paint(0x6d6a63, 0.5);
    const g = new THREE.Group();
    const bb = new Bld();
    bb.box(M.concrete(), w + 1.2, 0.4, d + 1.2, 0, 0, 0);
    bb.box(wall, w, h, d, 0, 0.4 + h / 2, 0);
    bb.box(trim, w + 0.3, 0.25, d + 0.3, 0, 0.4 + h + 0.12, 0);
    bb.box(trim, w + 0.2, 0.06, d + 0.2, 0, 0.4 + h + 0.28, 0);
    bb.box(M.paint(0x8a8578, 0.5), 0.95, 2.1, 0.06, -w * 0.28, 0.4 + 1.05, d / 2 + 0.02);        // steel door
    bb.box(trim, 1.1, 0.08, 0.1, -w * 0.28, 0.4 + 2.16, d / 2 + 0.04);
    bb.box(M.alu(), 0.1, 0.03, 0.05, -w * 0.28 + 0.35, 0.4 + 1.0, d / 2 + 0.06);
    bb.box(M.concrete(), 1.6, 0.2, 1.2, -w * 0.28, 0.2, d / 2 + 0.6);                              // landing
    bb.geo(M.paint(0xcfcac0, 0.5), rbox(1.1, 1.5, 0.55, 0.03), V3(w * 0.2, 0.4 + 1.6, d / 2 + 0.3));   // wall mount HVAC
    for (let i = 0; i < 9; i++) bb.box(M.black(), 0.9, 0.02, 0.01, w * 0.2, 0.4 + 1.1 + i * 0.12, d / 2 + 0.58);
    bb.box(M.paint(0x3a3a3a, 0.5), 0.3, 0.2, 0.15, w * 0.05, 0.4 + h - 0.4, d / 2 + 0.08);         // wall pack light
    bb.box(K.finish.lamp(0xffe2b0, 0.4), 0.22, 0.02, 0.1, w * 0.05, 0.4 + h - 0.51, d / 2 + 0.1);
    bb.box(trim, w, 0.5, 0.25, 0, 0.4 + h - 0.15, -d / 2 - 0.12);                                  // cable entrance
    bb.build(g); g.position.set(x, 0, z); g.rotation.y = ry || 0;
    return g;
  }
  function mast(b, x, z, H) {
    pier(b, x, z, 0.55, 0.4); b.box(M.galvDark(), 0.9, 0.05, 0.9, x, 0.43, z);
    facetTube(b, M.galv(0), 0.45, H, 0.32, 0.09, 12, x, z);
    b.bar(M.galv(0), [x, H, z], [x, H + 2.2, z], 0.025, 6);
  }

  /* ============================================================================ substation */
  K.define('substation', {
    size: [58, 22, 76],
    options: { size: 'small', kv: 345, leads: true },
    note: 'OPTIONS size small | large (2 or 3 transformer bays); kv high side 345 | 138; leads draws the incoming and outgoing line stubs. A fenced ERCOT yard on a crushed rock pad: dead end gantries, vertical break disconnects, SF6 dead tank breakers, autotransformers with radiators and conservators, a 138 kV low side, lightning masts, control house. Lines enter from -z.',
    make(o, r) {
      const g = new THREE.Group(), b = new Bld(), large = o.size === 'large', kv = +o.kv === 138 ? 138 : 345;
      POSTSEG = 8;
      const nb = large ? 3 : 2, ps = kv >= 345 ? 4.6 : 3.0, pitch = kv >= 345 ? 22 : 15, lvps = 2.6;
      const xs = Array.from({ length: nb }, (_, i) => (i - (nb - 1) / 2) * pitch);
      const zG = -30, zS1 = -23, zB = -14.5, zS2 = -6, zT = 5, zLB = 15, zLG = 23;
      const X0 = xs[0] - pitch / 2 - 4, X1 = xs[nb - 1] + pitch / 2 + 4, Z0 = -35, Z1 = 31;
      pad(b, X0 - 2, Z0 - 2, X1 + 2, Z1 + 2);
      fence(b, [X0, Z0], [X1, Z0], 2.13); fence(b, [X1, Z0], [X1, Z1], 2.13); fence(b, [X0, Z1], [X0, Z0], 2.13);
      const gx = X1 - 12;                                          // gate gap in the front run
      fence(b, [X1, Z1], [gx + 5, Z1], 2.13); fence(b, [gx - 1, Z1], [X0, Z1], 2.13);
      // double swing gate (open a little)
      [gx - 1, gx + 5].forEach((hx, k) => { const s = k ? -1 : 1, a = 0.35 * s;
        const ex = hx + s * 3 * Math.cos(a), ez = Z1 + 3 * Math.sin(a);
        b.bar(M.galv(0), [hx, 0.1, Z1], [ex, 0.1, ez], 0.02, 6); b.bar(M.galv(0), [hx, 2.1, Z1], [ex, 2.1, ez], 0.02, 6);
        b.bar(M.galv(0), [ex, 0.1, ez], [ex, 2.1, ez], 0.02, 6);
        const pg = new THREE.PlaneGeometry(3, 2); const uv = pg.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * 3 / 0.07, uv.getY(i) * 2 / 0.07);
        b.geo(linkMat(), pg, V3((hx + ex) / 2, 1.1, (Z1 + ez) / 2), new THREE.Quaternion().setFromAxisAngle(Y, -Math.atan2(ez - Z1, ex - hx)));
      });
      const al = M.alu();
      xs.forEach((xb, bi) => {
        const gp = gantry(b, xb, zG, ps, kv, kv >= 345 ? 16.5 : 12.5, 1);
        const s1 = disconnect(b, xb, zS1, ps, kv), br = deadTank(b, xb, zB, ps, kv), s2 = disconnect(b, xb, zS2, ps, kv, bi === 1 && large);
        const tr = powerTransformer(b, xb, zT, kv >= 345 ? 1 : 0.75, { polymer: r() < 0.3 });
        const lb = deadTank(b, xb, zLB, lvps, 138);
        const lg = gantry(b, xb, zLG, lvps, 138, 11, 1);
        const drop = (p, q, s) => b.cable(al, p, q, s, 0.02, 14, 6);
        for (let i = 0; i < 3; i++) {
          const inn = gp.find(e => e.dir > 0 && e.phase === i), out = gp.find(e => e.dir < 0 && e.phase === i);
          drop(inn.p, s1.a[i], 1.2); drop(s1.c[i], br.ins[i], 0.5); drop(br.outs[i], s2.a[i], 0.5);
          drop(s2.c[i], tr.hv[i], 0.8);
          drop(tr.lv[i], lb.ins[i], 0.6);
          const lgi = lg.find(e => e.dir < 0 && e.phase === i), lgo = lg.find(e => e.dir > 0 && e.phase === i);
          drop(lb.outs[i], lgi.p, 0.7);
          if (o.leads !== false) {
            b.cable(M.conductor(), out.p, [out.p[0], out.p[1] + 4, out.p[2] - 24], -0.5, 0.0145, 16, 6);
            b.cable(M.conductor(), lgo.p, [lgo.p[0], lgo.p[1] + 1.5, lgo.p[2] + 14], -0.3, 0.012, 12, 6);
          }
        }
        // cable trench from the bay to the house
        b.box(M.concrete(), 0.9, 0.14, 50, xb + ps * 1.8, 0.1, -3);
        for (let k = 0; k < 50; k += 1.5) b.box(M.black(), 0.9, 0.005, 0.02, xb + ps * 1.8, 0.175, -28 + k);
      });
      // firewalls between adjacent transformers
      for (let i = 0; i < nb - 1; i++) b.box(M.concrete(), 0.35, 8.5, 9, (xs[i] + xs[i + 1]) / 2, 0.2, zT);
      // lightning masts at the corners, light poles
      [[X0 + 2, Z0 + 2], [X1 - 2, Z0 + 2], [X0 + 2, zT - 4], [X1 - 2, zT - 4]].forEach(([mx, mz]) => mast(b, mx, mz, 21));
      [[X0 + 2.5, Z1 - 3], [X1 - 2.5, 0]].forEach(([lx, lz]) => {
        b.bar(M.galv(0), [lx, 0, lz], [lx, 9, lz], 0.07, 10);
        b.box(M.paint(0x3a3a3a, 0.5), 0.5, 0.18, 0.35, lx, 9.1, lz); b.box(K.finish.lamp(0xffe2b0, 0.5), 0.4, 0.02, 0.28, lx, 9.0, lz);
      });
      b.build(g); POSTSEG = 12;
      g.add(controlHouse(b, X0 + 8.5, Z1 - 5.5, 12, 5.5, 3.4, 0));
      return g;
    },
  });

  /* ========================================================================== wind turbine */
  /* One blade, span along +y from its root flange, leading edge toward +x, pressure side +z.
   * Cylindrical root, a transition to the maximum chord at 22 percent span, a NACA 4 digit
   * section thinning from 40 to 15 percent, 13 degrees of twist washing out to the tip, prebend. */
  function bladeGeo(L, rootR, cmax) {
    return tpl('blade' + L + rootR + cmax, () => {
      const NS = 56, NA = 30, pos = [], idx = [];
      const sm = (t) => { t = Math.min(1, Math.max(0, t)); return t * t * (3 - 2 * t); };
      for (let i = 0; i < NS; i++) {
        const u = i / (NS - 1), s = u < 0.3 ? 0.3 * Math.pow(u / 0.3, 1.25) : u;   // denser at the root
        let c = s < 0.22 ? lerp(2 * rootR, cmax, sm((s - 0.03) / 0.19)) : lerp(cmax, cmax * 0.24, Math.pow((s - 0.22) / 0.78, 0.85));
        if (s > 0.96) c *= lerp(1, 0.45, (s - 0.96) / 0.04);
        const w = sm((s - 0.02) / 0.24);                                         // circle -> airfoil
        const t = s < 0.22 ? 0.42 : lerp(0.42, 0.16, Math.min(1, (s - 0.22) / 0.45));
        const tw = (s < 0.2 ? 13 : 13 * Math.pow(1 - (s - 0.2) / 0.8, 1.6)) * DEG;
        const bend = 2.2 * s * s, ct = Math.cos(-tw), st = Math.sin(-tw);
        for (let k = 0; k < NA; k++) {
          const th = (k / NA) * Math.PI * 2;
          const cx = -Math.cos(th) * rootR + 0.2 * rootR, cz = -Math.sin(th) * rootR;
          const xc = (1 + Math.cos(th)) / 2, up = Math.sin(th) >= 0 ? 1 : -1;      // xc 0 at LE (th = pi)
          const yt = 5 * t * (0.2969 * Math.sqrt(xc) - 0.126 * xc - 0.3516 * xc * xc + 0.2843 * xc ** 3 - 0.1036 * xc ** 4);
          const m = 0.025, p = 0.4, yc = xc < p ? m / (p * p) * (2 * p * xc - xc * xc) : m / ((1 - p) ** 2) * (1 - 2 * p + 2 * p * xc - xc * xc);
          const ax = (0.3 - xc) * c, az = (-yc - up * yt) * c;                       // suction side toward -z
          const x = lerp(cx, ax, w), z = lerp(cz, az, w);
          pos.push(x * ct + z * st, s * L, -x * st + z * ct + bend);
        }
      }
      for (let i = 0; i < NS - 1; i++) for (let k = 0; k < NA; k++) {
        const a = i * NA + k, b2 = i * NA + (k + 1) % NA, c2 = a + NA, d = b2 + NA;
        idx.push(a, c2, b2, b2, c2, d);
      }
      const tip = pos.length / 3; const lt = (NS - 1) * NA;
      let tx = 0, tz = 0; for (let k = 0; k < NA; k++) { tx += pos[(lt + k) * 3]; tz += pos[(lt + k) * 3 + 2]; }
      pos.push(tx / NA, L + 0.05, tz / NA);
      for (let k = 0; k < NA; k++) idx.push(lt + k, tip, lt + (k + 1) % NA);
      const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx);
      g.computeVertexNormals();
      return g;
    });
  }
  K.define('wind_turbine', {
    size: [121, 150, 14],
    options: { rotor: 0, hub: 90, diameter: 120, yaw: 0 },
    note: 'OPTIONS rotor angle deg (0 = a blade straight up); hub height m; diameter m; yaw deg (0 = rotor faces +z). A 2.5 to 3 MW class machine: 90 m tapered tubular steel tower with flanges and a base door, nacelle with cooler, met mast and obstruction light, spinner, three twisted and tapered airfoil blades with prebend, 5 degree shaft tilt, pad mount transformer.',
    make(o, r) {
      const g = new THREE.Group(), b = new Bld(), H = o.hub || 90, D = o.diameter || 120, R = D / 2;
      const paint = kmat('pw_wtg', { color: 0xdfe1dd, metalness: 0.1, roughness: 0.42 }), blade = kmat('pw_blade', { color: 0xe8eae6, roughness: 0.34 });
      const yTop = H - 2.3;
      // foundation pedestal, gravel, the tower in three flanged sections
      b.geo(M.concrete(), new THREE.CylinderGeometry(3.1, 3.3, 0.6, 40), V3(0, 0.2, 0));
      b.geo(gravelMat(), new THREE.CylinderGeometry(9, 9.2, 0.08, 40), V3(0, 0.04, 0));
      b.geo(paint, new THREE.CylinderGeometry(1.4, 2.15, yTop - 0.5, 48, 6, true), V3(0, 0.5 + (yTop - 0.5) / 2, 0));
      const rad = (y) => lerp(2.15, 1.4, (y - 0.5) / (yTop - 0.5));
      [0.55, yTop * 0.3, yTop * 0.58, yTop * 0.82].forEach((y) => b.geo(paint, new THREE.CylinderGeometry(rad(y) + 0.035, rad(y) + 0.035, 0.08, 48), V3(0, y, 0)));
      // base door with a steel stair and landing
      const dz = rad(2.4);
      b.geo(paint, rbox(1.1, 2.25, 0.12, 0.05), V3(0, 2.5, dz + 0.02));
      b.box(M.paint(0xbfc2bf, 0.4), 0.8, 1.95, 0.05, 0, 2.5, dz + 0.08);
      b.box(M.galv(0), 1.6, 0.06, 1.3, 0, 1.35, dz + 0.65);
      for (let k = 0; k < 5; k++) b.box(M.galv(0), 1.0, 0.04, 0.28, 0, 0.3 + k * 0.22, dz + 1.45 + (4 - k) * 0.24);
      [-0.8, 0.8].forEach((x) => { b.bar(M.galv(0), [x, 1.35, dz + 0.1], [x, 2.4, dz + 0.1], 0.02, 6); b.bar(M.galv(0), [x, 2.4, dz + 0.1], [x, 2.4, dz + 1.25], 0.02, 6);
        b.bar(M.galv(0), [x, 2.4, dz + 1.25], [x * 0.7, 1.3, dz + 2.4], 0.02, 6); });
      // pad mount transformer
      b.box(M.concrete(), 3, 0.2, 2.6, 6.5, 0, 4.5);
      b.geo(M.paint(0x6f7a6c, 0.5), rbox(2.3, 1.9, 1.9, 0.05), V3(6.5, 0.2 + 0.95, 4.5));
      b.box(M.paint(0x58624f, 0.5), 2.2, 0.04, 0.02, 6.5, 1.5, 5.46);
      b.build(g);
      // the head: yaw about y, then the nacelle, then the tilted rotor
      const head = new THREE.Group(); head.position.y = yTop; head.rotation.y = (o.yaw || 0) * DEG; g.add(head);
      const hb = new Bld(), nac = paint, NL = 10.5, NW = 3.9, NH = 3.9;
      hb.geo(paint, new THREE.CylinderGeometry(1.45, 1.45, 0.4, 40), V3(0, 0.2, 0));
      hb.geo(nac, rbox(NW, NH, NL, 0.55, null, { segments: 5 }), V3(0, 0.4 + NH / 2, -1.6));
      hb.geo(nac, rbox(NW * 0.86, NH * 0.9, 1.6, 0.5), V3(0, 0.4 + NH * 0.5, -1.6 + NL / 2 + 0.3));   // front bearing housing
      hb.box(M.paint(0xb9bcb8, 0.5), NW * 0.02, NH * 0.8, NL * 0.9, NW / 2 + 0.005, 0.4 + NH * 0.5, -1.6);       // panel seam
      hb.box(M.paint(0xb9bcb8, 0.5), NW * 0.02, NH * 0.8, NL * 0.9, -NW / 2 - 0.005, 0.4 + NH * 0.5, -1.6);
      hb.geo(M.paint(0xc9ccc8, 0.5), rbox(2.8, 0.9, 2.6, 0.15), V3(0, 0.4 + NH + 0.35, -1.6 - NL / 2 + 1.7));   // cooler
      for (let k = 0; k < 7; k++) hb.box(M.black(), 2.5, 0.03, 0.02, 0, 0.4 + NH + 0.05 + k * 0.1, -1.6 - NL / 2 + 0.39);
      hb.box(M.paint(0xc9ccc8, 0.5), 1.0, 0.1, 0.8, 0, 0.4 + NH + 0.02, -0.3);                                  // roof hatch
      const mx = 0, my = 0.4 + NH + 0.8, mz = -1.6 - NL / 2 + 0.4;
      hb.bar(M.galv(0), [mx, 0.4 + NH, mz], [mx, my + 1.6, mz], 0.04, 8);
      hb.bar(M.galv(0), [mx - 0.8, my + 1.2, mz], [mx + 0.8, my + 1.2, mz], 0.03, 6);
      hb.geo(M.black(), new THREE.CylinderGeometry(0.06, 0.06, 0.25, 10), V3(mx - 0.8, my + 1.35, mz));
      hb.box(M.black(), 0.03, 0.2, 0.35, mx + 0.8, my + 1.38, mz);
      hb.geo(K.finish.lamp(0xff2a1a, 2.2), new THREE.SphereGeometry(0.11, 12, 8), V3(mx, my + 1.72, mz));
      hb.build(head);
      // rotor: tilt 5 degrees, hub, spinner, three blades at 120 with 2 degrees of cone
      const rotor = new THREE.Group(); rotor.position.set(0, H - yTop, -1.6 + NL / 2 + 1.5); rotor.rotation.x = -5 * DEG;
      head.add(rotor);
      const spin = new THREE.Group(); spin.rotation.z = -(o.rotor || 0) * DEG; rotor.add(spin);
      const rb = new Bld();
      const sp = new THREE.LatheGeometry([[0, 3.6], [0.6, 3.45], [1.2, 2.9], [1.62, 2.0], [1.78, 1.0], [1.8, 0.2], [1.72, 0]].map(p => new THREE.Vector2(p[0], p[1])), 40);
      _q.setFromAxisAngle(V3(1, 0, 0), Math.PI / 2);
      rb.geo(paint, sp, V3(0, 0, -0.9), _q.clone());
      rb.build(spin);
      const bg = bladeGeo(R - 1.6, 1.15, R * 0.068);
      for (let k = 0; k < 3; k++) {
        const arm = new THREE.Group(); arm.rotation.z = k * 2 * Math.PI / 3; spin.add(arm);
        const m = new THREE.Mesh(bg, blade); m.position.y = 1.6; m.rotation.x = 2 * DEG; arm.add(m);
        const fl = new THREE.Mesh(tpl('bfl', () => new THREE.CylinderGeometry(1.2, 1.25, 0.3, 32)), paint); fl.position.y = 1.55; arm.add(fl);
      }
      return g;
    },
  });

  /* ========================================================================== solar array */
  let CELLS = null;
  function cellTex() {
    if (CELLS) return CELLS;
    const W = 256, Hh = 512, c = document.createElement('canvas'); c.width = W; c.height = Hh;
    const x = c.getContext('2d'), r = K.rng(1771);
    x.fillStyle = '#1c2431'; x.fillRect(0, 0, W, Hh);
    const cw = (W - 10) / 6, ch = (Hh - 14) / 24;
    for (let i = 0; i < 6; i++) for (let j = 0; j < 24; j++) {
      const px = 5 + i * cw, py = 5 + j * ch + (j >= 12 ? 4 : 0);
      const gr = x.createLinearGradient(px, py, px + cw, py + ch);
      const k = 0.9 + r() * 0.15;
      gr.addColorStop(0, 'rgb(' + (16 * k | 0) + ',' + (26 * k | 0) + ',' + (46 * k | 0) + ')');
      gr.addColorStop(1, 'rgb(' + (10 * k | 0) + ',' + (17 * k | 0) + ',' + (33 * k | 0) + ')');
      x.fillStyle = gr; x.fillRect(px + 0.7, py + 0.7, cw - 1.4, ch - 1.4);
      x.fillStyle = 'rgba(190,200,210,0.16)';
      for (let b = 1; b < 4; b++) x.fillRect(px + b * cw / 4, py + 1, 0.8, ch - 2);
    }
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    CELLS = t; return t;
  }
  K.define('solar_array', {
    size: [42, 3.4, 26],
    options: { rows: 5, cols: 36, tilt: 20, pitch: 5.8 },
    note: 'OPTIONS rows (trackers); cols (modules per row); tilt deg, positive faces +z, trackers run about plus or minus 60; pitch m row spacing. Single axis trackers, one module in portrait (1P): 2.28 x 1.13 m bifacial modules on a square torque tube 2.1 m up, W6 piles every 7 m, slew drive at mid row, controller and combiner. Tubes run along x.',
    make(o, r) {
      const g = new THREE.Group(), b = new Bld(), rows = o.rows || 5, cols = o.cols || 36, tilt = (o.tilt != null ? o.tilt : 20) * DEG, pitch = o.pitch || 5.8;
      const mw = 1.134, ml = 2.278, gap = 0.02, yT = 2.1, frame = kmat('pw_frame', { color: 0xb9bdbf, metalness: 0.85, roughness: 0.35 });
      const pile = M.galv(0), tube = M.galv(1);
      const glass = kmat('pw_pv', { color: 0xffffff, map: cellTex(), roughness: 0.16, metalness: 0.05, clearcoat: 1, clearcoatRoughness: 0.04, envMapIntensity: 1.25 }, true);
      // module template, origin on the tube axis: glass, frame, two rails and the clamps
      const glassG = tpl('pvglass', () => { const bg = new THREE.BoxGeometry(mw - 0.03, 0.006, ml - 0.03); bg.translate(0, 0.135, 0); return bg; });
      const frameG = tpl('pvframe', () => {
        const parts = [];
        const add = (w, h, d, x, y, z) => { const q = new THREE.BoxGeometry(w, h, d); q.translate(x, y, z); parts.push(q); };
        add(0.035, 0.035, ml, (mw - 0.035) / 2, 0.12, 0); add(0.035, 0.035, ml, -(mw - 0.035) / 2, 0.12, 0);
        add(mw, 0.035, 0.035, 0, 0.12, (ml - 0.035) / 2); add(mw, 0.035, 0.035, 0, 0.12, -(ml - 0.035) / 2);
        add(0.04, 0.05, ml * 0.9, 0.3, 0.08, 0); add(0.04, 0.05, ml * 0.9, -0.3, 0.08, 0);
        add(0.1, 0.08, 0.18, 0.3, 0.02, 0); add(0.1, 0.08, 0.18, -0.3, 0.02, 0);
        return mergeGeos(parts);
      });
      const Lrow = cols * (mw + gap) + 0.8, list = [];
      const zs = Array.from({ length: rows }, (_, j) => (j - (rows - 1) / 2) * pitch);
      zs.forEach((z) => {
        for (let i = 0; i < cols; i++) {
          let x = -Lrow / 2 + 0.4 + (i + 0.5) * (mw + gap); if (i >= cols / 2) x += 0.8 - 0.4 * 0; else x -= 0;
          list.push([x - 0.4 + (i >= cols / 2 ? 0.4 : 0), yT, z]);
        }
        // torque tube (square, turned with the modules), piles, bearings, drive
        b.beam(tube, [-Lrow / 2, yT, z], [Lrow / 2, yT, z], 0.13, 0.13, [0, Math.cos(tilt), Math.sin(tilt)]);
        const np = Math.max(2, Math.round(Lrow / 7));
        for (let k = 0; k <= np; k++) {
          const px = -Lrow / 2 + 0.3 + k * (Lrow - 0.6) / np;
          b.box(pile, 0.1, yT - 0.12, 0.008, px, (yT - 0.12) / 2, z + 0.075); b.box(pile, 0.1, yT - 0.12, 0.008, px, (yT - 0.12) / 2, z - 0.075);
          b.box(pile, 0.006, yT - 0.12, 0.15, px, (yT - 0.12) / 2, z);
          b.box(M.galvDark(), 0.12, 0.26, 0.26, px, yT - 0.05, z);                                        // bearing housing
          b.geo(M.concrete(), tpl('pilecol', () => new THREE.CylinderGeometry(0.2, 0.22, 0.12, 12)), V3(px, 0.02, z));
        }
        b.geo(M.paint(0x5d6166, 0.5), new THREE.CylinderGeometry(0.26, 0.26, 0.2, 20), V3(0, yT, z), new THREE.Quaternion().setFromAxisAngle(V3(0, 0, 1), Math.PI / 2));
        b.box(M.paint(0x43474b, 0.5), 0.25, 0.22, 0.3, 0.2, yT - 0.3, z + 0.1);                             // slew drive motor
        b.box(pile, 0.14, yT - 0.2, 0.14, 0, (yT - 0.2) / 2, z);
        // row controller with its own small panel, combiner box at the east end
        b.box(M.paint(0xd8d8d2, 0.5), 0.35, 0.45, 0.18, Lrow / 2 - 0.9, 1.1, z + 0.2);
        b.box(M.paint(0x1d2330, 0.3), 0.4, 0.02, 0.3, Lrow / 2 - 0.9, 1.45, z + 0.25);
        b.box(M.paint(0xcfd0cb, 0.5), 0.5, 0.6, 0.22, Lrow / 2 + 0.6, 0.9, z);
        b.bar(pile, [Lrow / 2 + 0.6, 0, z - 0.15], [Lrow / 2 + 0.6, 1.2, z - 0.15], 0.04, 6);
      });
      b.build(g);
      const q = new THREE.Quaternion().setFromAxisAngle(V3(1, 0, 0), tilt), Mx = new THREE.Matrix4(), S1 = V3(1, 1, 1);
      [[glassG, glass], [frameG, frame]].forEach(([geo, mat]) => {
        const im = new THREE.InstancedMesh(geo, mat, list.length);
        list.forEach((p, i) => { Mx.compose(V3(p[0], p[1], p[2]), q, S1); im.setMatrixAt(i, Mx); });
        im.instanceMatrix.needsUpdate = true; im.computeBoundingBox && im.computeBoundingBox(); im.computeBoundingSphere && im.computeBoundingSphere();
        g.add(im);
      });
      return g;
    },
  });

  /* ======================================================================= battery storage */
  function container(b, x, z, o) {
    const L = 12.19, Hc = 2.9, W = 2.44, y0 = 0.35, ribs = o.ribs, trim = M.paint(0x8e918f, 0.5), dk = M.paint(0x2f3234, 0.6);
    [-0.45, -0.15, 0.15, 0.45].forEach((f) => b.box(M.concrete(), 0.6, y0, W + 0.4, x + f * L, 0, z));
    b.box(ribs, L - 0.2, Hc - 0.25, W - 0.1, x, y0 + Hc / 2, z);
    // corner posts, top and bottom rails, castings
    [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([a, c]) => {
      b.box(trim, 0.16, Hc, 0.16, x + a * (L / 2 - 0.08), y0 + Hc / 2, z + c * (W / 2 - 0.08));
      [y0 + 0.08, y0 + Hc - 0.08].forEach((yy) => b.box(dk, 0.18, 0.12, 0.17, x + a * (L / 2 - 0.09), yy, z + c * (W / 2 - 0.085)));
    });
    [y0 + 0.08, y0 + Hc - 0.07].forEach((yy) => [-1, 1].forEach((c) => b.box(trim, L - 0.3, 0.15, 0.1, x, yy, z + c * (W / 2 - 0.05))));
    b.box(trim, L - 0.1, 0.06, W - 0.05, x, y0 + Hc - 0.02, z);
    // side cabinet doors on +z: outlines, handles, and the placards
    const nd = 5;
    for (let i = 0; i < nd; i++) {
      const cx = x - L / 2 + 1.0 + (i + 0.5) * (L - 2.0) / nd, dw = (L - 2.0) / nd - 0.12;
      b.box(dk, dw, 0.02, 0.01, cx, y0 + 0.3, z + W / 2 + 0.005); b.box(dk, dw, 0.02, 0.01, cx, y0 + Hc - 0.35, z + W / 2 + 0.005);
      b.box(dk, 0.02, Hc - 0.65, 0.01, cx - dw / 2, y0 + Hc / 2 - 0.02, z + W / 2 + 0.005); b.box(dk, 0.02, Hc - 0.65, 0.01, cx, y0 + Hc / 2 - 0.02, z + W / 2 + 0.005);
      b.box(M.alu(), 0.03, 0.25, 0.04, cx - 0.12, y0 + 1.3, z + W / 2 + 0.02); b.box(M.alu(), 0.03, 0.25, 0.04, cx + 0.12, y0 + 1.3, z + W / 2 + 0.02);
    }
    b.box(M.white(), 0.25, 0.25, 0.01, x - L / 2 + 0.55, y0 + 1.7, z + W / 2 + 0.01, 0);
    b.box(M.paint(0xc8261e, 0.5), 0.18, 0.18, 0.012, x - L / 2 + 0.55, y0 + 1.7, z + W / 2 + 0.012);
    b.box(M.paint(0xe6b422, 0.5), 0.3, 0.2, 0.01, x - L / 2 + 0.55, y0 + 1.3, z + W / 2 + 0.01);
    // HVAC units on the -x end wall, fire suppression vent on the roof
    [-0.55, 0.55].forEach((dz) => {
      b.geo(M.paint(0xd4d4cf, 0.45), rbox(0.4, 1.9, 0.95, 0.03), V3(x - L / 2 - 0.2, y0 + 1.35, z + dz));
      for (let k = 0; k < 10; k++) b.box(dk, 0.01, 0.02, 0.8, x - L / 2 - 0.405, y0 + 0.6 + k * 0.1, z + dz);
      b.geo(dk, tpl('hvfan', () => new THREE.CylinderGeometry(0.3, 0.3, 0.02, 20)), V3(x - L / 2 - 0.405, y0 + 1.85, z + dz), new THREE.Quaternion().setFromAxisAngle(V3(0, 0, 1), Math.PI / 2));
    });
    b.geo(M.paint(0xa8aaa6, 0.5), new THREE.CylinderGeometry(0.12, 0.12, 0.35, 14), V3(x + L * 0.3, y0 + Hc + 0.15, z));
    // conduit stubs down to the trench
    b.bar(M.paint(0x6b6b6b, 0.6), [x + L / 2 - 0.4, y0 + 0.4, z + W / 2 + 0.05], [x + L / 2 - 0.4, 0.05, z + W / 2 + 0.05], 0.04, 8);
  }
  function pcs(b, x, z) {
    const grey = M.paint(0xb9bcb8, 0.45), dk = M.paint(0x2f3234, 0.6);
    b.box(M.galvDark(), 6.4, 0.25, 2.6, x, 0.25, z);
    b.box(M.concrete(), 6.8, 0.25, 3.0, x, 0, z);
    b.geo(grey, rbox(3.6, 2.35, 2.3, 0.04), V3(x - 1.2, 0.5 + 1.175, z));
    for (let i = 0; i < 4; i++) for (let k = 0; k < 8; k++) b.box(dk, 0.7, 0.025, 0.01, x - 2.6 + i * 0.9 + 0.1, 0.8 + k * 0.1, z + 1.155);
    b.geo(M.paint(0x62705e, 0.5), rbox(2.1, 2.0, 2.2, 0.04), V3(x + 1.95, 0.5 + 1.0, z));             // MV transformer
    for (let k = 0; k < 12; k++) b.box(M.paint(0x56634f, 0.5), 0.012, 1.5, 0.3, x + 1.0 + k * 0.16, 1.4, z - 1.25);  // cooling fins
    b.box(M.paint(0xe6b422, 0.5), 0.3, 0.2, 0.01, x + 1.95, 1.8, z + 1.105);
  }
  K.define('battery_storage', {
    size: [66, 14, 42],
    options: { rows: 3, cols: 4, gsu: true },
    note: 'OPTIONS rows of containers; cols containers per row, paired with a PCS skid between each pair; gsu adds the main step up transformer and a dead end. Containerised BESS on a fenced crushed rock pad: 40 ft battery enclosures with side cabinet doors, HVAC units and hazard placards, inverter and MV transformer skids between pairs, a main step up transformer.',
    make(o, r) {
      const g = new THREE.Group(), b = new Bld(), rows = o.rows || 3, cols = o.cols || 4;
      const ribs = kmat('pw_cont', { color: 0xffffff, roughness: 0.5, metalness: 0.15, map: K.tex('corrugated', { color: '#e8e9e4' }) });
      ribs.userData.metres = 3.3;
      const pairs = Math.ceil(cols / 2), pairW = 2 * 12.19 + 1.2 + 7.4, rowP = 2.44 + 7.5;
      const W = pairs * pairW, zs = Array.from({ length: rows }, (_, j) => (j - (rows - 1) / 2) * rowP);
      zs.forEach((z) => {
        for (let p = 0; p < pairs; p++) {
          const x0 = -W / 2 + p * pairW + 12.19 / 2 + 0.3;
          container(b, x0, z, { ribs });
          if (2 * p + 1 < cols) container(b, x0 + 12.19 + 1.2, z, { ribs });
          pcs(b, x0 + 12.19 * 1.5 + 1.2 + 3.9, z);
        }
      });
      const gx = W / 2 + 8, X0 = -W / 2 - 4, X1 = W / 2 + (o.gsu !== false ? 16 : 4), Z0 = zs[0] - 8, Z1 = zs[rows - 1] + 8;
      pad(b, X0 - 1, Z0 - 1, X1 + 1, Z1 + 1);
      fence(b, [X0, Z0], [X1, Z0], 2.13); fence(b, [X1, Z0], [X1, Z1], 2.13); fence(b, [X1, Z1], [X0 + 8, Z1], 2.13); fence(b, [X0, Z1], [X0, Z0], 2.13);
      if (o.gsu !== false) {
        const tr = powerTransformer(b, gx, 0, 0.62, {});
        const gp = gantry(b, gx, -9, 2.6, 138, 11, 1);
        for (let i = 0; i < 3; i++) { const e = gp.find(q => q.dir > 0 && q.phase === i); b.cable(M.alu(), e.p, tr.hv[i], 0.6, 0.02, 12, 6);
          const f = gp.find(q => q.dir < 0 && q.phase === i); b.cable(M.conductor(), f.p, [f.p[0], f.p[1] + 1.5, f.p[2] - 14], -0.3, 0.012, 12, 6); }
      }
      // cable trench along each row
      zs.forEach((z) => b.box(M.concrete(), W, 0.12, 0.8, 0, 0.06, z + 2.44 / 2 + 1.2));
      b.build(g);
      return g;
    },
  });

  /* ===================================================================== thermal plant parts */
  /* a box of acoustic enclosure panels: vertical seams, a roof lip, doors on +z */
  function enclosure(b, x0, x1, z, w, h, color, o) {
    o = o || {};
    const mat = M.paint(color, 0.55), seam = M.paint(0x000000, 0.9), L = x1 - x0, xc = (x0 + x1) / 2;
    b.geo(mat, rbox(L, h, w, 0.04), V3(xc, 0.3 + h / 2, z));
    b.box(mat, L + 0.2, 0.15, w + 0.2, xc, 0.3 + h + 0.07, z);
    const n = Math.round(L / 1.2);
    for (let i = 1; i < n; i++) [-1, 1].forEach((s) => b.box(seam, 0.02, h - 0.1, 0.004, x0 + i * L / n, 0.3 + h / 2, z + s * (w / 2 + 0.002)));
    (o.doors || []).forEach((dx) => {
      b.box(M.paint(color, 0.5), 1.0, 2.1, 0.05, xc + dx, 0.3 + 1.05, z + w / 2 + 0.03);
      b.box(M.alu(), 0.12, 0.03, 0.05, xc + dx + 0.35, 0.3 + 1.05, z + w / 2 + 0.07);
      b.box(M.paint(0x3a3a3a, 0.5), 0.3, 0.15, 0.15, xc + dx, 0.3 + 2.4, z + w / 2 + 0.08);
    });
    (o.fans || []).forEach((dx) => { b.geo(M.paint(0x8a8d8c, 0.5), new THREE.CylinderGeometry(0.55, 0.6, 0.9, 20), V3(xc + dx, 0.3 + h + 0.55, z));
      b.box(M.black(), 1.0, 0.02, 0.05, xc + dx, 0.3 + h + 1.0, z); });
  }
  /* louvered face: horizontal slats on a rectangle, facing +z or -z */
  function louvres(b, mat, xc, y0, z, w, h, s, pitch) {
    const n = Math.floor(h / (pitch || 0.35));
    for (let k = 0; k < n; k++) {
      const q = new THREE.Quaternion().setFromAxisAngle(V3(1, 0, 0), s * 0.6);
      b.geo(mat, tpl('slat', () => new THREE.BoxGeometry(1, 1, 1)), V3(xc, y0 + (k + 0.5) * h / n, z + s * 0.12), q, V3(w, 0.02, 0.32));
    }
  }
  /* inlet filter house: a box on columns, weather hoods over every filter face */
  function filterHouse(b, xc, zc, w, d, h, yb, color) {
    const mat = M.paint(color, 0.5), st = M.paint(0x7c7f80, 0.5);
    b.box(mat, w, h, d, xc, yb + h / 2, zc);
    [-1, 1].forEach((s) => {
      const rowsN = Math.max(4, Math.round(h / 0.95));
      for (let k = 0; k < rowsN; k++) {
        const y = yb + (k + 0.8) * h / rowsN;
        const q = new THREE.Quaternion().setFromAxisAngle(V3(1, 0, 0), s * 0.55);
        b.geo(mat, tpl('hood', () => new THREE.BoxGeometry(1, 1, 1)), V3(xc, y, zc + s * (d / 2 + 0.3)), q, V3(w - 0.2, 0.04, 0.75));
        [-1, 1].forEach((e) => b.box(mat, 0.04, 0.55, 0.6, xc + e * (w / 2 - 0.12), y - 0.25, zc + s * (d / 2 + 0.3)));
        b.box(M.paint(0x3c3f41, 0.8), w - 0.3, h / rowsN - 0.25, 0.02, xc, y - h / rowsN * 0.45, zc + s * (d / 2 + 0.01));
      }
    });
    [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([a, c]) => {
      b.beam(st, [xc + a * (w / 2 - 0.3), 0.3, zc + c * (d / 2 - 0.3)], [xc + a * (w / 2 - 0.3), yb, zc + c * (d / 2 - 0.3)], 0.35, 0.35);
      pier(b, xc + a * (w / 2 - 0.3), zc + c * (d / 2 - 0.3), 0.4, 0.3);
    });
    [-1, 1].forEach((c) => b.beam(st, [xc - w / 2 + 0.3, yb * 0.5, zc + c * (d / 2 - 0.3)], [xc + w / 2 - 0.3, yb * 0.5, zc + c * (d / 2 - 0.3)], 0.25, 0.25));
    // access stair up the side and a platform rail
    b.box(M.galv(0), w, 0.05, 1.2, xc, yb - 0.02, zc + d / 2 + 1.0);
    for (let x = xc - w / 2; x <= xc + w / 2 + 0.01; x += 1.5) b.bar(M.paint(0xd6b02a, 0.5), [x, yb, zc + d / 2 + 1.55], [x, yb + 1.07, zc + d / 2 + 1.55], 0.022, 6);
    b.bar(M.paint(0xd6b02a, 0.5), [xc - w / 2, yb + 1.07, zc + d / 2 + 1.55], [xc + w / 2, yb + 1.07, zc + d / 2 + 1.55], 0.025, 6);
  }
  /* a stack: a steel cylinder, a top lip, a CEMS platform with handrail and a caged ladder */
  function stack(b, x, z, R, H, color, platY) {
    const mat = M.paint(color, 0.5), rail = M.paint(0xd6b02a, 0.5);
    b.geo(M.concrete(), new THREE.CylinderGeometry(R + 0.8, R + 0.9, 0.6, 32), V3(x, 0.1, z));
    b.geo(mat, new THREE.CylinderGeometry(R, R * 1.04, H, 40, 1, true), V3(x, 0.4 + H / 2, z));
    b.geo(mat, new THREE.CylinderGeometry(R + 0.12, R + 0.12, 0.5, 40, 1, true), V3(x, 0.4 + H - 0.25, z));
    b.geo(M.paint(0x2a2826, 0.9), new THREE.CircleGeometry(R, 32).rotateX(-Math.PI / 2), V3(x, 0.4 + H - 0.4, z));
    [H * 0.35, H * 0.7].forEach((yy) => b.geo(mat, new THREE.CylinderGeometry(R + 0.06, R + 0.06, 0.2, 40, 1, true), V3(x, yy, z)));
    (Array.isArray(platY) ? platY : [platY]).forEach((py) => {
      b.geo(M.galv(0), new THREE.RingGeometry(R, R + 1.3, 40, 1).rotateX(-Math.PI / 2), V3(x, py, z));
      b.geo(M.galv(0), new THREE.RingGeometry(R, R + 1.3, 40, 1).rotateX(Math.PI / 2), V3(x, py - 0.02, z));
      for (let k = 0; k < 24; k++) { const a = k / 24 * Math.PI * 2; b.bar(rail, [x + Math.cos(a) * (R + 1.25), py, z + Math.sin(a) * (R + 1.25)], [x + Math.cos(a) * (R + 1.25), py + 1.07, z + Math.sin(a) * (R + 1.25)], 0.022, 5); }
      b.geo(rail, new THREE.TorusGeometry(R + 1.25, 0.025, 5, 48).rotateX(Math.PI / 2), V3(x, py + 1.07, z));
      b.geo(rail, new THREE.TorusGeometry(R + 1.25, 0.02, 5, 48).rotateX(Math.PI / 2), V3(x, py + 0.55, z));
      for (let k = 0; k < 4; k++) { const a = k / 4 * Math.PI * 2 + 0.4; b.geo(M.paint(0x6e7070, 0.5), tpl('port', () => new THREE.CylinderGeometry(0.1, 0.1, 0.4, 10)), V3(x + Math.cos(a) * (R + 0.15), py + 0.9, z + Math.sin(a) * (R + 0.15)), new THREE.Quaternion().setFromUnitVectors(Y, V3(Math.cos(a), 0, Math.sin(a)))); }
    });
    const lx = x + R + 0.35;
    [-0.22, 0.22].forEach((dz) => b.bar(M.galv(0), [lx, 2.5, z + dz], [lx, 0.4 + H - 0.5, z + dz], 0.025, 6));
    for (let yy = 2.8; yy < H; yy += 0.3) b.bar(M.galv(0), [lx, yy, z - 0.22], [lx, yy, z + 0.22], 0.012, 5);
    for (let yy = 4.5; yy < H; yy += 1.2) b.geo(M.galv(0), tpl('cage', () => new THREE.TorusGeometry(0.38, 0.015, 4, 16, Math.PI)), V3(lx, yy, z), new THREE.Quaternion().setFromAxisAngle(V3(1, 0, 0), Math.PI / 2).premultiply(new THREE.Quaternion().setFromAxisAngle(Y, Math.PI / 2)));
  }
  function finFan(b, x, z, n) {
    const st = M.galv(0), body = M.paint(0x9a9d9b, 0.5);
    b.box(body, 3.2 * n, 1.2, 3.2, x, 3.2, z);
    for (let i = 0; i < n; i++) {
      const fx = x - 1.6 * n + 1.6 + i * 3.2;
      b.geo(body, new THREE.CylinderGeometry(1.35, 1.35, 0.6, 28, 1, true), V3(fx, 4.7, z));
      b.box(M.black(), 2.4, 0.02, 0.05, fx, 4.9, z); b.box(M.black(), 0.05, 0.02, 2.4, fx, 4.9, z);
    }
    [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([a, c]) => b.beam(st, [x + a * (1.6 * n - 0.2), 0.3, z + c * 1.4], [x + a * (1.6 * n - 0.2), 3.2, z + c * 1.4], 0.2, 0.2));
  }
  function pipe(b, pts, r, mat) {
    for (let i = 0; i < pts.length - 1; i++) b.bar(mat, pts[i], pts[i + 1], r, 12);
    for (let i = 1; i < pts.length - 1; i++) b.geo(mat, tpl('elb' + r, () => new THREE.SphereGeometry(r, 12, 8)), V3(pts[i][0], pts[i][1], pts[i][2]));
  }

  /* ======================================================================== gas peaker */
  function peakerUnit(b, z0, r) {
    const beige = 0xd3d4cf, grey = 0x8f9496;
    b.box(M.concrete(), 44, 0.3, 14, 1, 0, z0);
    enclosure(b, -17, -7.5, z0, 4.2, 4.4, beige, { doors: [-2], fans: [1.5] });               // generator
    enclosure(b, -7.5, 6, z0, 4.8, 5.4, beige, { doors: [-3, 3], fans: [-2, 2.5] });          // turbine package
    filterHouse(b, -6.5, z0, 7.4, 6.4, 5.6, 8.6, beige);
    // inlet plenum duct down to the package and the silencer
    b.box(M.paint(beige, 0.5), 2.8, 2.9, 3.2, -6.5, 5.7 + 1.45, z0);
    // exhaust: diffuser transition, SCR and CO catalyst housing, tempering air fans, stack
    const g = M.paint(grey, 0.5);
    b.geo(g, new THREE.CylinderGeometry(1.6, 1.2, 3, 24), V3(7.5, 3.2, z0), new THREE.Quaternion().setFromAxisAngle(V3(0, 0, 1), Math.PI / 2));
    b.box(g, 4, 6.8, 5.2, 11, 1.2 + 3.4, z0);
    b.box(g, 10, 7.6, 6, 18, 1.2 + 3.8, z0);
    for (let x = 13.5; x <= 22.5; x += 1.5) [-1, 1].forEach((s) => b.box(g, 0.14, 7.6, 0.14, x, 1.2 + 3.8, z0 + s * 3.07));       // stiffeners
    [2.2, 5, 7.8].forEach((y) => [-1, 1].forEach((s) => b.box(g, 10, 0.18, 0.18, 18, 1.2 + y, z0 + s * 3.1)));
    for (let x = 13.5; x <= 22.5; x += 3) [-1, 1].forEach((s) => b.beam(M.paint(0x6f7273, 0.5), [x, 0.3, z0 + s * 2.8], [x, 1.2, z0 + s * 2.8], 0.3, 0.3));
    b.box(M.galv(0), 10, 0.05, 1.2, 18, 1.2 + 7.6 + 0.02, z0 + 3.6);
    [0, 1].forEach((k) => { b.geo(M.paint(0x3d6e8a, 0.5), new THREE.CylinderGeometry(0.8, 0.8, 1.0, 24), V3(12 + k * 3, 1.3, z0 + 4.6), new THREE.Quaternion().setFromAxisAngle(V3(1, 0, 0), Math.PI / 2));
      b.box(M.paint(0x3d6e8a, 0.5), 0.9, 0.8, 1.0, 12 + k * 3 + 1.1, 1.0, z0 + 4.6); });
    b.box(g, 4, 5, 4.4, 24.5, 1.2 + 2.5, z0);
    stack(b, 27.5, z0, 1.9, 30, 0x8d9090, [19]);
    // fin fan lube cooler, fuel gas skid, pipes
    finFan(b, -12, z0 + 6.2, 2);
    b.box(M.concrete(), 5, 0.3, 3, 2, 0, z0 + 7);
    b.box(M.paint(0xd4b73a, 0.5), 4.5, 0.2, 2.5, 2, 0.3, z0 + 7);
    pipe(b, [[0.2, 0.6, z0 + 7], [0.2, 1.4, z0 + 7], [0.2, 1.4, z0 + 2.6], [0.2, 4.2, z0 + 2.6]], 0.14, M.paint(0xd4b73a, 0.5));
    [[1.5, 1.2], [3.5, 1.0]].forEach(([x, h]) => b.geo(M.paint(0xd4b73a, 0.5), new THREE.CylinderGeometry(0.35, 0.35, h, 16), V3(x, 0.5 + h / 2, z0 + 7)));
  }
  K.define('gas_peaker', {
    size: [48, 32, 22],
    options: { units: 1, transformer: true },
    note: 'OPTIONS units 1 | 2; transformer adds the generator step up. A simple cycle aeroderivative unit (LM6000 class): generator and turbine acoustic enclosures, elevated inlet filter house with weather hoods, exhaust diffuser, SCR and CO catalyst housing with tempering air fans, 30 m stack with CEMS platform and caged ladder, lube oil fin fan, fuel gas skid, step up transformer.',
    make(o, r) {
      const g = new THREE.Group(), b = new Bld(), n = +o.units === 2 ? 2 : 1;
      for (let i = 0; i < n; i++) peakerUnit(b, (i - (n - 1) / 2) * 20, r);
      if (o.transformer !== false) powerTransformer(b, -14, (n - 1) * 10 + 10.5, 0.55, { color: 0x8f9594 });
      b.build(g);
      return g;
    },
  });

  /* ======================================================================= combined cycle */
  function hrsg(b, x0, z0, r) {
    const L = 30, W = 11, H = 27, casing = M.paint(0x7f8b93, 0.55), steel = M.paint(0x6a6d6e, 0.5), rail = M.paint(0xd6b02a, 0.5);
    const xc = x0 + L / 2;
    b.box(M.concrete(), L + 2, 0.4, W + 2, xc, 0, z0);
    b.box(casing, L, H, W, xc, 0.4 + H / 2, z0);
    // buckstays around the casing, vertical columns
    for (let y = 2.5; y < H; y += 2.6) {
      [-1, 1].forEach((s) => b.box(steel, L + 0.3, 0.35, 0.3, xc, y, z0 + s * (W / 2 + 0.15)));
    }
    for (let x = x0; x <= x0 + L + 0.01; x += 3.75) [-1, 1].forEach((s) => b.box(steel, 0.45, H + 0.4, 0.45, x, 0.4 + H / 2, z0 + s * (W / 2 + 0.2)));
    // steam drums on the roof, across the unit, with their supports and risers
    [[x0 + 6, 1.0, 12], [x0 + 15, 0.8, 11], [x0 + 23, 0.7, 10]].forEach(([dx, R, dl]) => {
      b.geo(M.paint(0x777a7b, 0.5), new THREE.CylinderGeometry(R, R, dl, 28), V3(dx, 0.4 + H + R + 1.0, z0), new THREE.Quaternion().setFromAxisAngle(V3(1, 0, 0), Math.PI / 2));
      [-1, 1].forEach((e) => b.geo(M.paint(0x777a7b, 0.5), new THREE.SphereGeometry(R, 20, 8, 0, Math.PI * 2, 0, Math.PI / 2), V3(dx, 0.4 + H + R + 1.0, z0 + e * dl / 2), new THREE.Quaternion().setFromAxisAngle(V3(1, 0, 0), e * Math.PI / 2)));
      [-0.3, 0.3].forEach((f) => b.box(steel, 0.4, 1.0, 0.4, dx, 0.4 + H + 0.5, z0 + f * dl));
      for (let k = -2; k <= 2; k++) b.bar(M.paint(0x8a8d8c, 0.5), [dx + 0.5, 0.4 + H, z0 + k * 1.8], [dx + 0.5, 0.4 + H + 1.0 + R, z0 + k * 1.8], 0.16, 10);
    });
    // roof deck rail, stair tower on +z with landings every 3 m
    b.box(M.galv(0), L, 0.05, W, xc, 0.4 + H + 0.03, z0);
    for (let x = x0; x <= x0 + L; x += 2) [-1, 1].forEach((s) => b.bar(rail, [x, 0.4 + H, z0 + s * W / 2], [x, 0.4 + H + 1.07, z0 + s * W / 2], 0.022, 5));
    [-1, 1].forEach((s) => b.bar(rail, [x0, 0.4 + H + 1.07, z0 + s * W / 2], [x0 + L, 0.4 + H + 1.07, z0 + s * W / 2], 0.025, 6));
    const sx = x0 + L - 4, sz = z0 + W / 2 + 3;
    truss(b, M.galv(0), sq(1.8, 0.4).map(p => [p[0] + sx, p[1], p[2] + sz]), sq(1.8, H + 0.4).map(p => [p[0] + sx, p[1], p[2] + sz]), 9, 0.2, 0.1, { endA: true, endB: true });
    for (let y = 3.4; y < H; y += 3) {
      b.box(M.galv(0), 3.8, 0.05, 3.8, sx, y, sz);
      b.beam(M.galv(0), [sx - 1.6, y, sz - 1.2], [sx + 1.6, y + 3, sz - 1.2], 0.9, 0.05, [0, 0, 1]);
      b.bar(rail, [sx - 1.8, y + 1.07, sz + 1.8], [sx + 1.8, y + 1.07, sz + 1.8], 0.025, 6);
      b.box(M.galv(0), 2, 0.05, 1.2, sx, y, z0 + W / 2 + 0.8);
    }
    // external downcomers and feed piping
    [[x0 + 4, 0.3], [x0 + 12, 0.25], [x0 + 20, 0.22]].forEach(([px, pr]) => pipe(b, [[px, 1.4, z0 + W / 2 + 0.8], [px, H - 1, z0 + W / 2 + 0.8], [px, H + 1.2, z0 + 2]], pr, M.paint(0x9b9e9e, 0.45)));
    // outlet duct and the stack
    b.box(casing, 4, 8, 7, x0 + L + 2, 0.4 + H - 6, z0);
    stack(b, x0 + L + 7, z0, 3.3, 50, 0x8d9090, [30, 44]);
    b.box(casing, 3.6, 7, 6, x0 + L + 4.6, 0.4 + H - 6.5, z0);
    return { inlet: x0 };
  }
  function gtTrain(b, z0, r) {
    const beige = 0xc9c2ad;
    b.box(M.concrete(), 48, 0.35, 16, -32, 0, z0);
    enclosure(b, -56, -42, z0, 6.4, 7, beige, { doors: [-3, 3], fans: [0] });            // generator
    enclosure(b, -42, -18, z0, 8.4, 8.4, beige, { doors: [-8, 0, 7], fans: [-6, 0, 6] });   // gas turbine
    filterHouse(b, -36, z0, 13, 12, 10, 14, beige);
    b.box(M.paint(beige, 0.5), 4.2, 5.6, 5, -36, 8.7 + 2.8, z0);                         // inlet duct
    // exhaust diffuser: widening from the turbine to the HRSG inlet
    const d = M.paint(0x8e9391, 0.55);
    const geo = new THREE.CylinderGeometry(1, 1, 1, 4, 1, false).toNonIndexed(); geo.computeVertexNormals();
    const shape = [[-18, 2.2, 3.4, 3.4], [-12, 3.0, 8, 6], [-6, 0.4, 27, 11]];
    for (let i = 0; i < shape.length - 1; i++) {
      const [xa, ya, ha, wa] = shape[i], [xb, yb, hb, wb] = shape[i + 1];
      const pts = [[xa, ya, -wa / 2], [xa, ya + ha, -wa / 2], [xa, ya + ha, wa / 2], [xa, ya, wa / 2], [xb, yb, -wb / 2], [xb, yb + hb, -wb / 2], [xb, yb + hb, wb / 2], [xb, yb, wb / 2]];
      const fz = [[0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]], P = [];
      fz.forEach(([a, c, e, f]) => { const A = pts[a], C = pts[c], E = pts[e], F = pts[f]; P.push(...A, ...E, ...C, ...A, ...F, ...E); });
      const gg = new THREE.BufferGeometry(); gg.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); gg.computeVertexNormals();
      b.geo(d, gg, V3(0, 0, z0));
    }
    for (let x = -11; x < -6; x += 1.8) b.box(M.paint(0x6a6d6e, 0.5), 0.3, 0.3, 8 + (x + 12) * 0.5, x, 1.2, z0);
    finFan(b, -48, z0 + 8.5, 3);
  }
  function coolingTower(b, x, z, n) {
    const casing = M.paint(0x8b959b, 0.6), deck = M.paint(0x7a8186, 0.6), slat = M.paint(0x5d676d, 0.7), cell = 14, H = 11;
    const L = n * cell;
    b.box(M.concrete(), L + 2, 1.2, cell + 3, x, 0, z);                                        // basin
    b.box(casing, L, H - 4.2, cell, x, 5.4 + (H - 5.4) / 2 - 0.3, z);                          // fill casing above the louvres
    [-1, 1].forEach((s) => louvres(b, slat, x, 1.2, z + s * (cell / 2 - 0.1), L, 4.2, s, 0.3));
    for (let i = 0; i <= n; i++) b.box(casing, 0.3, 4.2, cell, x - L / 2 + i * cell, 1.2 + 2.1, z);  // partition walls between cells
    b.box(deck, L + 0.4, 0.3, cell + 0.4, x, H, z);
    for (let i = 0; i < n; i++) {
      const cx = x - L / 2 + cell / 2 + i * cell;
      const fs = new THREE.LatheGeometry([[4.4, 0], [4.25, 1.2], [4.3, 2.8], [4.7, 4.0], [4.6, 4.0], [4.15, 2.8], [4.1, 1.2], [4.3, 0]].map(p => new THREE.Vector2(p[0], p[1])), 48);
      b.geo(casing, fs, V3(cx, H + 0.15, z));
      b.geo(M.black(), new THREE.CircleGeometry(4.2, 36).rotateX(-Math.PI / 2), V3(cx, H + 1.6, z));
      for (let k = 0; k < 8; k++) { const a = k * Math.PI / 4 + i; b.beam(M.paint(0x2e3337, 0.6), [cx, H + 1.8, z], [cx + Math.cos(a) * 4.0, H + 1.8, z + Math.sin(a) * 4.0], 0.5, 0.05, [0, 1, 0]); }
      b.geo(M.paint(0x3a3f43, 0.6), new THREE.CylinderGeometry(0.5, 0.5, 0.6, 16), V3(cx, H + 1.9, z));
    }
    // stair up the end and the deck rail
    b.box(M.galv(0), 1.2, 0.05, cell, x + L / 2 + 1.2, H, z);
    for (let y = 0; y < H; y += 2.2) b.beam(M.galv(0), [x + L / 2 + 1.2, y, z - cell / 2 + (y / H) * cell], [x + L / 2 + 1.2, y + 2.2, z - cell / 2 + ((y + 2.2) / H) * cell], 0.9, 0.05, [1, 0, 0]);
    for (let xx = x - L / 2; xx <= x + L / 2; xx += 2) [-1, 1].forEach((s) => b.bar(M.paint(0xd6b02a, 0.5), [xx, H + 0.15, z + s * (cell / 2 + 0.1)], [xx, H + 1.2, z + s * (cell / 2 + 0.1)], 0.022, 5));
  }
  function acc(b, x, z, nx, nz) {
    const cell = 12, H = 24, st = M.paint(0x8e9391, 0.55), L = nx * cell, D = nz * cell;
    for (let i = 0; i <= nx; i += 1) for (let j = 0; j <= nz; j += 1) {
      const cx = x - L / 2 + i * cell, cz = z - D / 2 + j * cell;
      b.bar(M.concrete(), [cx, 0, cz], [cx, H, cz], 0.6, 12);
    }
    b.box(st, L + 1, 1.8, D + 1, x, H + 0.9, z);
    for (let i = 0; i < nx; i++) for (let j = 0; j < nz; j++) {
      const cx = x - L / 2 + cell / 2 + i * cell, cz = z - D / 2 + cell / 2 + j * cell;
      b.geo(st, new THREE.CylinderGeometry(4.9, 4.9, 1.2, 36, 1, true), V3(cx, H - 0.4, cz));
    }
    // A-frame bundles along z with a steam duct along the ridge, windwall around
    for (let i = 0; i < nx; i++) {
      const cx = x - L / 2 + cell / 2 + i * cell;
      [-1, 1].forEach((s) => { const q = new THREE.Quaternion().setFromAxisAngle(V3(0, 0, 1), s * 0.52);
        b.geo(M.paint(0x6c7275, 0.6), tpl('abund', () => new THREE.BoxGeometry(1, 1, 1)), V3(cx + s * 2.7, H + 1.8 + 4.6, z), q, V3(0.4, 10.5, D)); });
      b.geo(M.paint(0x9a9d9c, 0.5), new THREE.CylinderGeometry(0.9, 0.9, D + 2, 20), V3(cx, H + 1.8 + 9.3, z), new THREE.Quaternion().setFromAxisAngle(V3(1, 0, 0), Math.PI / 2));
    }
    [-1, 1].forEach((s) => b.box(M.paint(0x8b959b, 0.6), L + 1, 10, 0.2, x, H + 1.8 + 5, z + s * (D / 2 + 0.5)));
    [-1, 1].forEach((s) => b.box(M.paint(0x8b959b, 0.6), 0.2, 10, D + 1, x + s * (L / 2 + 0.5), H + 1.8 + 5, z));
  }
  K.define('power_plant', {
    size: [120, 58, 120],
    options: { units: 2, cooling: 'tower' },
    note: 'OPTIONS units 1 | 2 gas turbine and HRSG trains; cooling tower (mechanical draft) | acc (air cooled condenser). A combined cycle block: F class gas turbines with elevated inlet filter houses, exhaust diffusers into heat recovery steam generators with buckstays, drums, stair towers and 50 m stacks, a steam turbine hall, mechanical draft cooling tower or air cooled condenser, step up transformers, demin water tank.',
    make(o, r) {
      const g = new THREE.Group(), b = new Bld(), n = +o.units === 1 ? 1 : 2, pitch = 30;
      const zs = Array.from({ length: n }, (_, i) => (i - (n - 1) / 2) * pitch);
      zs.forEach((z) => { gtTrain(b, z, r); hrsg(b, -6, z, r); powerTransformer(b, -62, z + 4, 0.85, {}); b.box(M.concrete(), 0.35, 9, 10, -67.5, 0.2, z + 4); });
      // steam turbine hall behind the trains
      const zh = zs[0] - 34, wall = kmat('pw_hall', { color: 0xffffff, roughness: 0.6, metalness: 0.2, map: K.tex('corrugated', { color: '#cfcbc0' }) });
      wall.userData.metres = 2.4;
      b.box(M.concrete(), 48, 0.4, 26, -26, 0, zh);
      b.box(wall, 46, 24, 24, -26, 0.4 + 12, zh);
      b.box(M.paint(0x8a8578, 0.55), 46.6, 0.6, 24.6, -26, 24.6, zh);
      for (let i = 0; i < 6; i++) b.geo(M.paint(0x9a9d9c, 0.5), rbox(3, 1.2, 1.6, 0.1), V3(-46 + i * 8, 25.5, zh));
      b.box(M.paint(0x7c7a72, 0.5), 6, 8, 0.1, -12, 0.4 + 4, zh + 12.05);                         // roll up door
      for (let k = 0; k < 20; k++) b.box(M.paint(0x6c6a63, 0.5), 6, 0.03, 0.02, -12, 0.6 + k * 0.4, zh + 12.12);
      [-40, -26].forEach((x) => { b.box(M.paint(0x505254, 0.5), 5, 3, 0.08, x, 16, zh + 12.05); for (let k = 0; k < 10; k++) b.box(M.black(), 4.8, 0.04, 0.05, x, 14.6 + k * 0.3, zh + 12.1); });
      b.box(M.paint(0x8a8578, 0.5), 1.0, 2.1, 0.06, -34, 0.4 + 1.05, zh + 12.04);
      // steam and condensate lines from the HRSGs to the hall
      zs.forEach((z) => pipe(b, [[4, 29, z + 3], [4, 32, z + 3], [4, 32, zh + 8], [-8, 32, zh + 8], [-8, 20, zh + 8]], 0.35, M.paint(0xa3a6a5, 0.45)));
      // cooling
      if (o.cooling === 'acc') acc(b, -20, zs[n - 1] + 42, 3, 2);
      else coolingTower(b, -20, zs[n - 1] + 36, 5);
      // demin and raw water tanks
      [[34, zh + 2, 7, 12, 0xe8e8e4], [34, zh + 22, 5, 9, 0xd9d6ce]].forEach(([x, z, R, H, c]) => {
        b.geo(M.paint(c, 0.45), new THREE.CylinderGeometry(R, R, H, 48), V3(x, 0.3 + H / 2, z));
        b.geo(M.paint(c, 0.45), new THREE.CylinderGeometry(0.4, R, 1.0, 48), V3(x, 0.3 + H + 0.5, z));
        b.geo(M.concrete(), new THREE.CylinderGeometry(R + 0.4, R + 0.4, 0.4, 48), V3(x, 0.1, z));
        for (let y = 1; y < H; y += 0.6) b.bar(M.galv(0), [x + R + 0.1, y, z], [x + R + 0.1, y, z + 0.5], 0.015, 5);
      });
      b.build(g);
      return g;
    },
  });
}
