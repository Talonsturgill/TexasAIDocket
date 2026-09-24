/* kit/people.js, see assets/js/txkit.js for the conventions.
 *
 * `person` is the scale reference every frame uses. It is an articulated adult built from
 * lofted cross sections along a posed skeleton (no capsules): a sculpted head with face
 * planes, neck, torso shaped ring by ring, arms with elbows and hands with fingers, legs with
 * knees, and shoes. Clothing is its own shaped shell over the body. Everything is in metres,
 * the person stands on y = 0 and faces +z. Their LEFT is +x.
 *
 * `crowd` scatters N seeded people over an area.
 */
export function install(K, THREE, TXT) {
  const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
  const pick = (r, arr) => arr[Math.floor(r() * arr.length) % arr.length];
  const lerp = (a, b, t) => a + (b - a) * t;
  const clamp01 = (t) => Math.max(0, Math.min(1, t));
  const smooth = (t) => { t = clamp01(t); return t * t * (3 - 2 * t); };

  /* ---- LOFT: a skin through elliptical (super-elliptical) cross sections --------------------
   * ctrl: [{ p:[x,y,z], rx, ry, ryn? }]. rx lies along the frame's N (from `ref`), ry toward
   * +B (B = N x T), ryn toward -B (defaults to ry). Positions are smoothed with a Catmull-Rom
   * curve, radii with the same parameter. UVs are in metres (around, along) so a cloth texture
   * keeps its scale. caps: 'dome' | 'flat' | null at each end. */
  let LOW = false;     // set while a low-detail (crowd) person is being built
  function loft(ctrl, o) {
    o = o || {};
    const M = LOW ? Math.max(6, Math.round((o.seg || 16) * 0.5)) : o.seg || 16, n = o.n || 2, per = LOW ? Math.min(2, o.per || 5) : o.per || 5;
    const pts = ctrl.map((c) => V3(c.p[0], c.p[1], c.p[2]));
    const curve = pts.length > 2 ? new THREE.CatmullRomCurve3(pts, false, 'centripetal') : null;
    const S = (ctrl.length - 1) * per + 1;
    const ref = V3(...(o.ref || [1, 0, 0])).normalize();
    const cr = (a, b, c, d, t) => 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t * t * t);
    const radius = (key, u) => {
      const f = u * (ctrl.length - 1), i = Math.min(ctrl.length - 2, Math.floor(f)), t = f - i;
      const g = (j) => { const c = ctrl[Math.max(0, Math.min(ctrl.length - 1, j))]; return c[key] != null ? c[key] : c.ry; };
      return Math.max(0.0005, cr(g(i - 1), g(i), g(i + 1), g(i + 2), t));
    };
    const rings = [];
    for (let s = 0; s < S; s++) {
      const u = s / (S - 1);
      let P, T;
      if (curve) { P = curve.getPoint(u); T = curve.getTangent(u); }
      else { P = pts[0].clone().lerp(pts[1], u); T = pts[1].clone().sub(pts[0]).normalize(); }
      let N = ref.clone().sub(T.clone().multiplyScalar(ref.dot(T)));
      if (N.lengthSq() < 1e-6) N = Math.abs(T.y) < 0.9 ? V3(0, 1, 0) : V3(0, 0, 1);
      N.normalize();
      const B = N.clone().cross(T).normalize();
      rings.push({ P, T, N, B, rx: radius('rx', u), ry: radius('ry', u), ryn: radius('ryn', u) });
    }
    // dome caps: extra shrinking rings past each end
    const dome = (end) => {
      const base = end ? rings[rings.length - 1] : rings[0], sgn = end ? 1 : -1, extra = [];
      const L = Math.min(base.rx, base.ry, base.ryn) * (o.domeK || 0.9);
      for (let k = 1; k <= 4; k++) {
        const a = (k / 5) * Math.PI / 2, c = Math.cos(a);
        extra.push(Object.assign({}, base, { P: base.P.clone().addScaledVector(base.T, sgn * Math.sin(a) * L),
          rx: base.rx * c, ry: base.ry * c, ryn: base.ryn * c }));
      }
      return { rings: end ? extra : extra.reverse(), tip: base.P.clone().addScaledVector(base.T, sgn * L) };
    };
    let tipA = null, tipB = null;
    if (o.capStart === 'dome') { const d = dome(false); rings.unshift(...d.rings); tipA = d.tip; }
    else if (o.capStart === 'flat') tipA = rings[0].P.clone();
    if (o.capEnd === 'dome') { const d = dome(true); rings.push(...d.rings); tipB = d.tip; }
    else if (o.capEnd === 'flat') tipB = rings[rings.length - 1].P.clone();

    const pos = [], uv = [], idx = [];
    let along = 0;
    rings.forEach((R, i) => {
      if (i > 0) along += R.P.distanceTo(rings[i - 1].P);
      const circ = Math.PI * (R.rx + (R.ry + R.ryn) / 2);
      for (let j = 0; j <= M; j++) {
        const th = (j / M) * Math.PI * 2, c = Math.cos(th), s = Math.sin(th);
        const cx = Math.sign(c) * Math.pow(Math.abs(c), 2 / n), cy = Math.sign(s) * Math.pow(Math.abs(s), 2 / n);
        const ry = cy >= 0 ? R.ry : R.ryn;
        let x = R.P.x + R.N.x * R.rx * cx + R.B.x * ry * cy;
        let y = R.P.y + R.N.y * R.rx * cx + R.B.y * ry * cy;
        let z = R.P.z + R.N.z * R.rx * cx + R.B.z * ry * cy;
        if (o.floor != null && y < o.floor) y = o.floor;
        pos.push(x, y, z); uv.push((j / M) * circ, along);
      }
    });
    const W = M + 1;
    for (let i = 0; i < rings.length - 1; i++)
      for (let j = 0; j < M; j++) {
        const a = i * W + j, b = a + W;
        idx.push(a, b, a + 1, b, b + 1, a + 1);
      }
    const fan = (tip, ringI, flip) => {
      const t = pos.length / 3; pos.push(tip.x, tip.y, tip.z); uv.push(0, 0);
      for (let j = 0; j < M; j++) {
        const a = ringI * W + j;
        if (flip) idx.push(t, a + 1, a); else idx.push(t, a, a + 1);
      }
    };
    if (tipA) fan(tipA, 0, false);
    if (tipB) fan(tipB, rings.length - 1, true);
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
    g.setIndex(idx);
    g.computeVertexNormals();
    // weld the seam normals
    const nor = g.attributes.normal;
    for (let i = 0; i < rings.length; i++) {
      const a = i * W, b = a + M;
      const nx = nor.getX(a) + nor.getX(b), ny = nor.getY(a) + nor.getY(b), nz = nor.getZ(a) + nor.getZ(b);
      const l = Math.hypot(nx, ny, nz) || 1;
      nor.setXYZ(a, nx / l, ny / l, nz / l); nor.setXYZ(b, nx / l, ny / l, nz / l);
    }
    if (o.flipFaces) { for (let i = 0; i < idx.length; i += 3) { const t = idx[i]; idx[i] = idx[i + 1]; idx[i + 1] = t; } g.setIndex(idx); g.computeVertexNormals(); }
    return g;
  }
  K.loft = K.loft || loft;   // shared for other families that might want it (not required)

  /* ---- cloth textures, painted locally --------------------------------------------------- */
  const CT = new Map();
  function clothTex(kind, a, b, c) {
    const key = kind + a + b + c;
    if (CT.has(key)) return CT.get(key);
    const N = 256, cv = document.createElement('canvas'); cv.width = cv.height = N;
    const x = cv.getContext('2d'), r = K.rng(31 + kind.length * 7);
    const hex = (v) => '#' + v.toString(16).padStart(6, '0');
    if (kind === 'denim') {
      x.fillStyle = hex(a); x.fillRect(0, 0, N, N);
      for (let i = -N; i < N * 2; i += 3) {       // diagonal twill
        x.strokeStyle = 'rgba(255,255,255,' + (0.05 + r() * 0.07) + ')'; x.lineWidth = 1;
        x.beginPath(); x.moveTo(i, 0); x.lineTo(i + N, N); x.stroke();
      }
      for (let i = 0; i < 900; i++) { x.fillStyle = 'rgba(255,255,255,' + r() * 0.06 + ')'; x.fillRect(r() * N, r() * N, 1 + r() * 6, 1); }
    } else if (kind === 'plaid') {
      x.fillStyle = hex(a); x.fillRect(0, 0, N, N);
      const band = (p, w, col, al) => { x.fillStyle = col; x.globalAlpha = al; x.fillRect(p, 0, w, N); x.fillRect(0, p, N, w); x.globalAlpha = 1; };
      band(20, 70, hex(b), 0.55); band(150, 70, hex(b), 0.55); band(110, 8, hex(c), 0.8); band(236, 8, hex(c), 0.8);
      band(60, 3, '#ffffff', 0.35); band(190, 3, '#ffffff', 0.35);
    } else if (kind === 'weave') {
      x.fillStyle = hex(a); x.fillRect(0, 0, N, N);
      for (let i = 0; i < N; i += 2) { x.fillStyle = 'rgba(0,0,0,' + (0.02 + r() * 0.04) + ')'; x.fillRect(0, i, N, 1); x.fillRect(i, 0, 1, N); }
    }
    const t = new THREE.CanvasTexture(cv);
    t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    const rep = kind === 'plaid' ? 1 / 0.16 : kind === 'denim' ? 1 / 0.05 : 1 / 0.04;
    t.repeat.set(rep, rep);
    CT.set(key, t);
    return t;
  }
  function cloth(kind, color, extra) {
    extra = extra || {};
    if (kind === 'denim') return K.mat('p-denim', { color: 0xffffff, roughness: 0.92, map: clothTex('denim', color, 0, 0) });
    if (kind === 'plaid') return K.mat('p-plaid', { color: 0xffffff, roughness: 0.88, map: clothTex('plaid', color, extra.b, extra.c) });
    if (kind === 'suit') return K.mat('p-suit', { color, roughness: 0.62, sheen: 0.4, sheenColor: 0x888888, sheenRoughness: 0.6 }, true);
    if (kind === 'hivis') return K.mat('p-hivis', { color, roughness: 0.7, emissive: color, emissiveIntensity: 0.12 });
    return K.mat('p-cloth', { color, roughness: extra.rough || 0.86, sheen: 0.25, sheenColor: 0xffffff, sheenRoughness: 0.8 }, true);
  }

  /* ---- palettes ------------------------------------------------------------------------- */
  const SKIN = [0xf0d0b6, 0xe6b894, 0xd9a47c, 0xc98f64, 0xb37550, 0x9a6040, 0x7d4a2f, 0x5e3522, 0x4a2a1b];
  const HAIR = [0x1d1510, 0x2a1d14, 0x3b2a1c, 0x5a3d25, 0x7a5a38, 0x9a8468, 0x8c8a86, 0xc2bdb4, 0x121010];
  const SHIRTS = [0xf2f0ea, 0x9fb7d0, 0x2d3a52, 0x6b7d5c, 0xa2493b, 0x3d5f7a, 0xc9b58f, 0x484848, 0x7a2e2e, 0xe0d7c3, 0x5b6f8f];
  const PLAIDS = [[0x8c2a24, 0x2a2a2a, 0xd8c7a0], [0x2f4a6b, 0x1c2433, 0xc8c2b0], [0x4f6a3a, 0x2a3320, 0xd2c38f], [0x9d6a2f, 0x3b2a1a, 0xe8dcc0]];
  const DENIM = [0x2e4263, 0x3a5680, 0x243552, 0x4d6690, 0x1e2a3c];
  const KHAKI = [0xb9a27c, 0x8f7a5a, 0x5d584d, 0x3f4a3a, 0x6b6257];
  const SUITS = [0x23262d, 0x2e3440, 0x3a3a3c, 0x1c2230, 0x4a4540];

  /* ---- the head: a sphere sculpted into a skull, jaw and face planes --------------------- */
  const HEADS = new Map();
  function headShape(ux, uy, uz, W, Hh, D, fem) {
    // boxier skull
    let x = Math.sign(ux) * Math.pow(Math.abs(ux), 0.9), y = uy, z = Math.sign(uz) * Math.pow(Math.abs(uz), 0.9);
    // jaw and chin taper
    if (y < 0.05) { const t = (0.05 - y) / 1.05; x *= 1 - (fem ? 0.5 : 0.42) * Math.pow(t, 1.5); }
    // no skull behind the jaw: the neck is there
    if (z < 0 && y < -0.15) z *= 1 - 0.55 * smooth((-y - 0.15) / 0.7);
    // forehead slopes back a little, face plane flattens
    if (z > 0) z *= 1 - 0.1 * Math.max(0, y - 0.3) - 0.08 * x * x;
    let px = x * W, py = y * Hh, pz = z * D;
    if (uz > 0) {
      const fz = uz;       // only on the front
      const g = (dx, dy, sx, sy) => Math.exp(-(dx * dx) / (sx * sx) - (dy * dy) / (sy * sy));
      // nose: ridge from the brow growing to the tip
      const tn = clamp01((0.12 - uy) / 0.42);
      const below = uy < -0.30 ? Math.exp(-Math.pow((uy + 0.30) / 0.07, 2)) : 1;
      pz += D * 0.24 * tn * below * g(ux, 0, 0.1 + 0.06 * tn, 1) * fz;
      // nostril wings
      pz += D * 0.05 * g(Math.abs(ux) - 0.1, uy + 0.3, 0.06, 0.06) * fz;
      // brow ridge
      pz += D * 0.06 * g(0, uy - 0.2, 1, 0.07) * (Math.abs(ux) < 0.62 ? 1 : 0.3) * fz;
      // eye sockets
      pz -= D * 0.07 * g(Math.abs(ux) - 0.33, uy - 0.07, 0.14, 0.09) * fz;
      // cheekbones
      pz += D * 0.04 * g(Math.abs(ux) - 0.52, uy + 0.08, 0.16, 0.12) * fz;
      // lips and the mouth line
      pz += D * 0.05 * g(ux, uy + 0.5, 0.22, 0.07) * fz;
      pz -= D * 0.02 * g(ux, uy + 0.56, 0.25, 0.015) * fz;
      // chin
      pz += D * 0.06 * g(ux, uy + 0.82, 0.25, 0.14) * fz;
    }
    return [px, py, pz];
  }
  function headGeo(W, Hh, D, fem, shell) {
    const key = [W, Hh, D, fem, shell, LOW].map((v) => (typeof v === 'number' ? v.toFixed(4) : v)).join('|');
    if (HEADS.has(key)) return HEADS.get(key);
    const g = LOW ? new THREE.SphereGeometry(1, 22, 18) : new THREE.SphereGeometry(1, 40, 34);
    const p = g.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const ux = p.getX(i), uy = p.getY(i), uz = p.getZ(i);
      let [x, y, z] = headShape(ux, uy, uz, W, Hh, D, fem);
      if (shell) {
        // hair: a shell 4% out, pulled inside the head below the hairline
        const k = 1.045;
        const side = Math.abs(ux);
        const longHair = shell === 'long';
        const line = uz > 0.25 ? 0.5 - 0.35 * smooth((side - 0.45) / 0.5) : (uz > -0.3 ? 0.1 - 0.35 * smooth((-uz + 0.25) / 0.55) : -0.4);
        const lim = longHair ? (uz > 0.1 ? line : -0.9 + 0.5 * smooth((uz + 0.3) / 0.4)) : line;
        const b = smooth((uy - lim) / 0.07 + 0.5), inside = b < 0.5;
        const kk = lerp(0.9, k, b);
        if (longHair && uy < 0.1 && uz < 0.2) { const w = b * smooth((0.1 - uy) / 0.3); x *= 1 + 0.07 * w; z *= 1 + 0.05 * w * (uz < 0 ? 1 : 0); }
        x *= kk; y = y * kk + Hh * 0.01 * b; z *= kk;
      }
      p.setXYZ(i, x, y, z);
    }
    g.computeVertexNormals();
    HEADS.set(key, g);
    return g;
  }

  /* ---- hands -------------------------------------------------------------------------- */
  // Built hanging down -y with the palm facing -s*x (toward the body) and the thumb to +z.
  function hand(k, s, mat, pose) {
    const g = new THREE.Group();
    const L = 0.1 * k, B = 0.084 * k, T = 0.03 * k;
    const palm = loft([
      { p: [0, 0.012 * k, 0], rx: T * 0.42, ry: B * 0.34 },
      { p: [0, -0.03 * k, 0.002 * k], rx: T * 0.55, ry: B * 0.47 },
      { p: [-s * 0.002 * k, -0.07 * k, 0], rx: T * 0.5, ry: B * 0.5 },
      { p: [-s * 0.004 * k, -L + 0.004 * k, 0], rx: T * 0.4, ry: B * 0.47 }], { seg: 16, per: 3, n: 2.4, ref: [1, 0, 0], capStart: 'flat', capEnd: 'dome', domeK: 0.5 });
    g.add(new THREE.Mesh(palm, mat));
    const fl = [0.072, 0.082, 0.077, 0.062];
    if (LOW) {      // a mitten: the fingers as one curled blade
      g.add(new THREE.Mesh(loft([{ p: [0, -L + 0.01 * k, 0], rx: T * 0.38, ry: B * 0.45 }, { p: [-s * 0.012 * k, -L - 0.06 * k, 0], rx: T * 0.3, ry: B * 0.4 }],
        { seg: 12, capEnd: 'dome', ref: [1, 0, 0] }), mat));
    }
    for (let f = 0; f < (LOW ? 0 : 4); f++) {
      const zz = (0.03 - f * 0.02) * k * (B / (0.084 * k));
      const len = fl[f] * k;
      const curl = pose === 'point' ? (f === 0 ? 0.05 : 1.35) : pose === 'fist' ? 1.3 : 0.35 + f * 0.05;
      const ctrl = [];
      let px = 0, py = -L + 0.004 * k, a = 0;
      const rad = (0.0095 - f * 0.0006) * k;
      ctrl.push({ p: [px, py + 0.01 * k, zz], rx: rad, ry: rad * 0.85 });
      for (let j = 1; j <= 3; j++) {
        a += curl / 2.2;
        const seg = len / 3;
        py -= Math.cos(a) * seg; px += -s * Math.sin(a) * seg;
        ctrl.push({ p: [px, py, zz * (1 - j * 0.05)], rx: rad * (1 - j * 0.1), ry: rad * 0.85 * (1 - j * 0.1) });
      }
      g.add(new THREE.Mesh(loft(ctrl, { seg: 8, per: 2, capStart: 'flat', capEnd: 'dome', ref: [0, 0, 1] }), mat));
    }
    // thumb from the heel of the palm, forward and down
    const th = [[-s * 0.004, -0.02, 0.03], [-s * 0.012, -0.045, 0.052], [-s * 0.02, -0.07, 0.062], [-s * 0.028, -0.09, 0.064]]
      .map((q, i) => ({ p: q.map((v) => v * k), rx: (0.012 - i * 0.0011) * k, ry: (0.01 - i * 0.001) * k }));
    if (pose === 'point' || pose === 'fist') th.forEach((t, i) => { t.p[0] -= s * 0.012 * k * i; t.p[2] -= 0.008 * k * i; });
    g.add(new THREE.Mesh(loft(th, { seg: 8, per: 2, capStart: 'flat', capEnd: 'dome' }), mat));
    return g;
  }

  /* ---- shoes -------------------------------------------------------------------------- */
  function shoe(k, style, upper, sole) {
    const g = new THREE.Group();
    const L = 0.28 * k, heelZ = -0.06 * k;
    const boot = style === 'boot' || style === 'work' || style === 'western';
    const ctrl = [
      { p: [0, 0.05 * k, heelZ], rx: 0.036 * k, ry: 0.04 * k },
      { p: [0, 0.058 * k, heelZ + 0.05 * k], rx: 0.04 * k, ry: 0.052 * k },
      { p: [0, 0.054 * k, heelZ + 0.12 * k], rx: 0.043 * k, ry: 0.05 * k },
      { p: [0, 0.04 * k, heelZ + 0.2 * k], rx: 0.043 * k, ry: 0.036 * k },
      { p: [0, 0.028 * k, heelZ + L - 0.03 * k], rx: style === 'western' ? 0.026 * k : style === 'dress' ? 0.033 * k : 0.04 * k, ry: 0.024 * k },
    ];
    const body = new THREE.Mesh(loft(ctrl, { seg: 18, per: 4, capStart: 'dome', capEnd: 'dome', ref: [1, 0, 0], floor: 0.012 * k, n: 2.3 }), upper);
    g.add(body);
    // shaft around the ankle
    const shaftH = style === 'western' ? 0.24 : boot ? 0.15 : 0.085;
    const sh = new THREE.Mesh(loft([
      { p: [0, 0.04 * k, -0.015 * k], rx: 0.045 * k, ry: 0.05 * k },
      { p: [0, shaftH * 0.55 * k, -0.01 * k], rx: 0.044 * k, ry: 0.047 * k },
      { p: [0, shaftH * k, -0.005 * k], rx: (style === 'western' ? 0.05 : 0.043) * k, ry: (style === 'western' ? 0.052 : 0.045) * k }],
    { seg: 16, per: 3, capEnd: 'flat', ref: [1, 0, 0] }), upper);
    g.add(sh);
    // sole: an outline extruded, with a heel block for western and work boots
    const so = new THREE.Shape();
    const w0 = 0.034 * k, w1 = style === 'sneaker' ? 0.045 * k : 0.043 * k;
    so.moveTo(-w0, heelZ - 0.02 * k); so.quadraticCurveTo(0, heelZ - 0.045 * k, w0, heelZ - 0.02 * k);
    so.lineTo(w1, heelZ + 0.17 * k); so.quadraticCurveTo(w1 * (style === 'western' ? 0.4 : 0.9), heelZ + L + 0.01 * k, 0, heelZ + L + 0.005 * k);
    so.quadraticCurveTo(-w1 * (style === 'western' ? 0.4 : 0.9), heelZ + L + 0.01 * k, -w1, heelZ + 0.17 * k); so.closePath();
    const sg = new THREE.ExtrudeGeometry(so, { depth: (style === 'sneaker' ? 0.024 : 0.014) * k, bevelEnabled: true, bevelThickness: 0.003 * k, bevelSize: 0.003 * k, bevelSegments: 2, curveSegments: 10 });
    sg.rotateX(Math.PI / 2); sg.translate(0, (style === 'sneaker' ? 0.026 : 0.017) * k, 0);
    g.add(new THREE.Mesh(sg, sole));
    if (style === 'western' || style === 'work' || style === 'dress') {
      const hh = (style === 'western' ? 0.045 : 0.025) * k;
      const heel = TXT.roundedBox(0.058 * k, hh, 0.06 * k, 0.004 * k, sole);
      heel.position.set(0, hh / 2, heelZ + 0.005 * k); g.add(heel);
      g.position.y = hh - 0.012 * k;   // raised on the heel; caller keeps the sole on the ground
      g.userData.lift = hh - 0.012 * k;
    }
    if (style === 'sneaker') {           // a white midsole stripe reads as a trainer at any size
      const lace = TXT.roundedBox(0.05 * k, 0.012 * k, 0.09 * k, 0.005 * k, sole);
      lace.position.set(0, 0.078 * k, heelZ + 0.12 * k); lace.rotation.x = -0.35; g.add(lace);
    }
    return g;
  }

  /* ---- hats --------------------------------------------------------------------------- */
  function hat(kind, W, D, top, mat, rr) {
    const g = new THREE.Group();
    if (kind === 'cowboy') {
      const crownH = 0.12 * (W / 0.075);
      const prof = [[0.001, crownH], [0.5, crownH - 0.004], [0.8, crownH - 0.012], [0.95, crownH * 0.6], [1.0, 0]];
      const cr = new THREE.LatheGeometry(prof.slice().reverse().map((p) => new THREE.Vector2(p[0], p[1])), 48);
      const cp = cr.attributes.position;
      for (let i = 0; i < cp.count; i++) {
        let x = cp.getX(i), y = cp.getY(i), z = cp.getZ(i);
        // cattleman crease: a dip along the top, two pinches at the front
        const rr0 = Math.hypot(x, z);
        if (y > crownH * 0.7) y -= 0.016 * Math.exp(-(x * x) / 0.12) * (1 - rr0 * 0.6);
        if (z > 0 && y > crownH * 0.5) x *= 1 - 0.12 * z * (y / crownH);
        cp.setXYZ(i, x * W * 1.1, y, z * D * 1.07);
      }
      cr.computeVertexNormals();
      g.add(new THREE.Mesh(cr, mat));
      // brim: an annulus that curls up at the sides and dips front and back
      const bg = new THREE.RingGeometry(0.5, 1, 56, 5);
      const bp = bg.attributes.position;
      for (let i = 0; i < bp.count; i++) {
        const x = bp.getX(i), y = bp.getY(i), rad = Math.hypot(x, y), ang = Math.atan2(y, x);
        const ex = W * 1.1 + (rad - 0.5) * 2 * 0.1, ez = D * 1.07 + (rad - 0.5) * 2 * 0.1;
        const X = Math.cos(ang) * ex, Z = Math.sin(ang) * ez;
        const out = (rad - 0.5) * 2;
        const lift = 0.05 * out * out * Math.pow(Math.abs(Math.cos(ang)), 2) - 0.012 * out * Math.pow(Math.abs(Math.sin(ang)), 2);
        bp.setXYZ(i, X, lift, Z);
      }
      bg.computeVertexNormals();
      const brim = new THREE.Mesh(bg, K.mat('p-hatbrim-' + mat.uuid, { color: mat.color.getHex(), roughness: mat.roughness, side: THREE.DoubleSide }));
      g.add(brim);
      const band = new THREE.Mesh(new THREE.CylinderGeometry(W * 1.1, W * 1.105, 0.02, 40, 1, true), K.mat('p-hatband', { color: 0x2a1c14, roughness: 0.6, side: THREE.DoubleSide }));
      band.scale.z = (D * 1.07) / (W * 1.1); band.position.y = 0.012; g.add(band);
      g.position.y = top;
    } else if (kind === 'cap') {
      const dome = new THREE.SphereGeometry(1, 36, 18, 0, Math.PI * 2, 0, Math.PI / 2);
      dome.scale(W * 1.08, 0.1 * (W / 0.075), D * 1.06);
      g.add(new THREE.Mesh(dome, mat));
      const bill = new THREE.SphereGeometry(1, 24, 6, -Math.PI * 0.3, Math.PI * 0.6, Math.PI / 2 - 0.12, 0.12);
      bill.scale(W * 1.12, 0.3, D * 1.75);
      const bm = new THREE.Mesh(bill, K.mat('p-capbill-' + mat.uuid, { color: mat.color.getHex(), roughness: 0.8, side: THREE.DoubleSide }));
      bm.rotation.y = Math.PI / 2; bm.position.y = 0.005;
      bm.rotation.y = 0; g.add(bm);
      const btn = new THREE.Mesh(new THREE.SphereGeometry(0.006, 8, 6), mat); btn.position.y = 0.1 * (W / 0.075); g.add(btn);
      g.position.y = top;
    } else if (kind === 'hard') {
      const s = W / 0.075 * 0.8;
      const prof = [[0.001, 0.13], [0.05, 0.128], [0.09, 0.117], [0.115, 0.093], [0.128, 0.055], [0.132, 0.014], [0.14, 0.008], [0.143, 0.002], [0.13, -0.002], [0.12, 0.0]];
      const hg = new THREE.LatheGeometry(prof.slice().reverse().map((p) => new THREE.Vector2(p[0] * s, p[1] * s)), 48);
      const hp = hg.attributes.position;
      for (let i = 0; i < hp.count; i++) {
        let z = hp.getZ(i);
        const y = hp.getY(i);
        // longer peak at the front
        if (z > 0 && y < 0.02 * s) z *= 1.25;
        hp.setZ(i, z * (D / W) * 1.02);
      }
      hg.computeVertexNormals();
      g.add(new THREE.Mesh(hg, mat));
      const rib = new THREE.Mesh(new THREE.TorusGeometry(0.118 * s, 0.009 * s, 8, 40, Math.PI), mat);
      rib.rotation.y = Math.PI / 2; rib.scale.set(1, 1.08, (D / W) * 1.02); g.add(rib);
      g.position.y = top;
    }
    return g;
  }

  /* Merge every mesh under `root` that shares a material into one mesh (world space of root). */
  function mergeByMaterial(root) {
    root.updateMatrixWorld(true);
    const inv = new THREE.Matrix4().copy(root.matrixWorld).invert(), groups = new Map();
    root.traverse((m) => { if (m.isMesh && !m.isInstancedMesh) { if (!groups.has(m.material)) groups.set(m.material, []); groups.get(m.material).push(m); } });
    const out = new THREE.Group();
    for (const [mat, list] of groups) {
      const parts = list.map((m) => {
        let g = m.geometry.index ? m.geometry.toNonIndexed() : m.geometry.clone();
        g.applyMatrix4(new THREE.Matrix4().multiplyMatrices(inv, m.matrixWorld));
        if (!g.attributes.normal) g.computeVertexNormals();
        return g;
      });
      const hasUV = parts.every((g) => g.attributes.uv);
      let total = 0; parts.forEach((g) => { total += g.attributes.position.count; });
      const pos = new Float32Array(total * 3), nor = new Float32Array(total * 3), uv = hasUV ? new Float32Array(total * 2) : null;
      let o = 0;
      parts.forEach((g) => { pos.set(g.attributes.position.array, o * 3); nor.set(g.attributes.normal.array, o * 3);
        if (uv) uv.set(g.attributes.uv.array, o * 2); o += g.attributes.position.count; g.dispose(); });
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
      if (uv) geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
      out.add(new THREE.Mesh(geo, mat));
    }
    return out;
  }

  /* ---- the person ---------------------------------------------------------------------- */
  K.define('person', {
    size: [0.5, 1.75, 0.3],
    options: { seed: 1, role: 'resident', pose: 'stand', toward: 1, height: null, build: 'auto',
               hat: 'auto', vest: 'auto', skin: null, shirt: null, trousers: null, detail: 'full' },
    note: 'Articulated adult 1.60 to 1.90 m by seed. role resident|worker|official; pose stand|walk|point|hands_on_hips|look_up; toward -1|1 for point; hat auto|none|cap|cowboy|hard; build auto|male|female.',
    make(o, r) {
      LOW = o.detail === 'low';
      try { return makePerson(o, r); } finally { LOW = false; }
    },
  });
  function makePerson(o, r) {
    {
      const role = o.role || 'resident', pose = o.pose || 'stand';
      const fem = o.build === 'female' ? true : o.build === 'male' ? false : r() < 0.4;
      const H = o.height || (fem ? lerp(1.6, 1.76, r()) : lerp(1.68, 1.9, r()));
      const k = H / 1.75;
      const bw = (fem ? 0.9 : 1) * lerp(0.95, 1.1, r());     // shoulder / chest breadth
      const hw = (fem ? 1.04 : 1) * lerp(0.95, 1.08, r());   // hip breadth
      const belly = lerp(0, role === 'official' ? 0.02 : 0.025, r());
      const G = new THREE.Group();

      // palette by seed and role
      const skinC = o.skin != null ? (o.skin < 20 ? SKIN[o.skin | 0] : o.skin) : pick(r, SKIN);
      const skin = K.mat('p-skin', { color: skinC, roughness: 0.58, sheen: 0.3, sheenColor: 0xffd9c0, sheenRoughness: 0.6, clearcoat: 0.05 }, true);
      const hairC = pick(r, HAIR);
      const hairM = K.mat('p-hair', { color: hairC, roughness: 0.62, sheen: 0.8, sheenColor: 0xffffff, sheenRoughness: 0.45 }, true);
      let shirtKind = 'tee', shirtM, trouserM, jacket = false, sleeves = 'long', tie = null;
      const sroll = r();
      if (role === 'official') {
        const sc = o.shirt != null ? o.shirt : pick(r, SUITS);
        shirtM = cloth('suit', sc); trouserM = cloth('suit', sc); jacket = true; sleeves = 'long';
        tie = pick(r, [0x7a1f25, 0x1f3050, 0x3a3a3a, 0x5a2240, 0x2c4a3a]);
      } else {
        if (role === 'worker') shirtKind = sroll < 0.5 ? 'tee' : 'work';
        else shirtKind = sroll < 0.35 ? 'tee' : sroll < 0.6 ? 'plaid' : sroll < 0.8 ? 'button' : 'polo';
        sleeves = shirtKind === 'tee' || shirtKind === 'polo' ? 'short' : r() < 0.35 ? 'rolled' : 'long';
        if (shirtKind === 'plaid') { const pl = pick(r, PLAIDS); shirtM = cloth('plaid', pl[0], { b: pl[1], c: pl[2] }); }
        else shirtM = cloth('cloth', o.shirt != null ? o.shirt : shirtKind === 'work' ? pick(r, [0x6d7f8f, 0x8a7a5c, 0x3f4f5f, 0xb0a58a]) : pick(r, SHIRTS));
        const jeans = role === 'worker' ? r() < 0.7 : r() < 0.65;
        trouserM = o.trousers != null ? cloth('cloth', o.trousers, { rough: 0.9 }) : jeans ? cloth('denim', pick(r, DENIM)) : cloth('cloth', pick(r, KHAKI), { rough: 0.9 });
      }
      const shoeStyle = role === 'official' ? 'dress' : role === 'worker' ? 'work' : pick(r, ['sneaker', 'sneaker', 'western', 'boot']);
      const shoeUpper = shoeStyle === 'sneaker' ? K.mat('p-sneak', { color: pick(r, [0xe8e6e0, 0x2a2c30, 0x5a6470, 0xb8b2a6]), roughness: 0.8 })
        : shoeStyle === 'dress' ? K.mat('p-dress', { color: 0x151312, roughness: 0.3, clearcoat: 0.6, clearcoatRoughness: 0.3 }, true)
        : shoeStyle === 'work' ? K.mat('p-work', { color: pick(r, [0x7a5530, 0x5a3e24, 0x8f6a3e]), roughness: 0.75 })
        : K.mat('p-leather', { color: pick(r, [0x5a3a22, 0x3a2416, 0x7a4c2a, 0x2a1d16]), roughness: 0.5, clearcoat: 0.3, clearcoatRoughness: 0.5 }, true);
      const soleM = shoeStyle === 'sneaker' ? K.mat('p-sole', { color: 0xefece6, roughness: 0.7 }) : K.mat('p-dsole', { color: 0x1d1714, roughness: 0.7 });

      /* SKELETON (y from the ground, before the stance lift). */
      const Y = (f) => f * H;
      const shoulderX = 0.178 * k * bw, hipX = 0.086 * k * hw;
      const upperArm = 0.305 * k, foreArm = 0.25 * k, thigh = 0.43 * k, shin = 0.425 * k;
      const hipY = Y(0.52), shY = Y(0.805);
      const n3 = (x, y, z) => V3(x, y, z).normalize();
      // per pose: [upper arm dir, forearm dir] per side (+1 left, -1 right), leg dirs, head pitch/yaw, hand pose
      const arm = {}, leg = {};
      let headPitch = 0, headYaw = 0, torsoLean = 0;
      for (const s of [1, -1]) {
        arm[s] = { u: n3(s * 0.14, -1, 0.02), f: n3(s * 0.07, -1, 0.16), hand: 'relax' };
        leg[s] = { t: n3(s * 0.02, -1, 0.0), c: n3(s * 0.01, -1, -0.01) };
      }
      const tw = o.toward === -1 ? -1 : 1;
      if (pose === 'walk') {
        const lead = r() < 0.5 ? 1 : -1;
        leg[lead] = { t: n3(lead * 0.02, -1, 0.42), c: n3(lead * 0.01, -1, 0.12) };
        leg[-lead] = { t: n3(-lead * 0.02, -1, -0.2), c: n3(-lead * 0.01, -1, -0.62) };
        arm[lead] = { u: n3(lead * 0.1, -1, -0.32), f: n3(lead * 0.08, -1, -0.12), hand: 'relax' };
        arm[-lead] = { u: n3(-lead * 0.1, -1, 0.3), f: n3(-lead * 0.1, -0.75, 0.8), hand: 'relax' };
        torsoLean = 0.04;
      } else if (pose === 'point') {
        arm[tw] = { u: n3(tw * 0.85, 0.32, 0.45), f: n3(tw * 0.85, 0.38, 0.4), hand: 'point' };
        headYaw = tw * 0.5; headPitch = -0.05;
      } else if (pose === 'hands_on_hips') {
        for (const s of [1, -1]) arm[s] = { u: n3(s * 0.62, -1, -0.28), f: n3(-s * 0.55, -0.62, 0.22), hand: 'hip' };
      } else if (pose === 'look_up') {
        headPitch = -0.5;
        const s = r() < 0.5 ? 1 : -1;
        if (r() < 0.6) arm[s] = { u: n3(s * 0.55, 0.15, 0.55), f: n3(-s * 0.75, 0.45, -0.1), hand: 'shade' };
      }
      // legs: FK, then lift so the lower ankle sits at ankle height
      const ankleH = 0.075 * k;
      for (const s of [1, -1]) {
        const L = leg[s];
        L.hip = V3(s * hipX, hipY, 0);
        L.knee = L.hip.clone().addScaledVector(L.t, thigh);
        L.ankle = L.knee.clone().addScaledVector(L.c, shin);
      }
      const lift = ankleH - Math.min(leg[1].ankle.y, leg[-1].ankle.y);
      for (const s of [1, -1]) { leg[s].hip.y += lift; leg[s].knee.y += lift; leg[s].ankle.y += lift; }
      const Yl = (f) => Y(f) + lift;

      /* TORSO: trousers seat, then shirt or jacket over it. Rings [yFrac, halfW, front, back, zc]. */
      const bk = belly * k;
      const lower = [[0.495, 0.09, 0.03, 0.07, -0.014], [0.515, 0.156, 0.06, 0.108, -0.008], [0.54, 0.168, 0.085, 0.116, -0.004],                      [0.578, 0.163, 0.098 + bk * 0.6, 0.104, 0], [0.61, 0.157, 0.102 + bk, 0.094, 0.002]];
      const hemY = jacket ? 0.47 : shirtKind === 'plaid' || shirtKind === 'button' || shirtKind === 'work' ? (r() < 0.5 ? 0.6 : 0.555) : 0.55;
      const tucked = hemY >= 0.595;
      const upper = [[hemY, jacket ? 0.176 : tucked ? 0.16 : 0.172, (tucked ? 0.104 : 0.108) + bk, tucked ? 0.097 : 0.112, 0],
                     [hemY + 0.03, jacket ? 0.17 : 0.165, 0.106 + bk, 0.104, 0],
                     [Math.max(0.64, hemY + 0.06), 0.16, 0.108 + bk * 1.2, 0.096, 0],
                     [0.69, 0.16, 0.113 + bk * 0.7 + (fem ? 0.006 : 0), 0.098, 0.002],
                     [0.735, 0.165, 0.122 + (fem ? 0.022 : 0), 0.103, 0.006],
                     [0.775, 0.172, 0.112 + (fem ? 0.01 : 0), 0.104, 0.004],
                     [0.8, 0.17, 0.094, 0.098, 0.002], [0.817, 0.15, 0.076, 0.084, -0.002], [0.832, 0.118, 0.064, 0.07, -0.006],
                     [0.843, 0.09, 0.055, 0.06, -0.009], [0.853, 0.068, 0.05, 0.052, -0.01]];
      // keep the upper rings monotone in y after the hem choice
      for (let i = 1; i < upper.length; i++) if (upper[i][0] <= upper[i - 1][0]) upper[i][0] = upper[i - 1][0] + 0.012;
      const ring = (row, wk, extra) => ({ p: [0, Yl(row[0]), row[4] * k], rx: row[1] * k * wk + (extra || 0), ry: row[2] * k + (extra || 0), ryn: row[3] * k + (extra || 0) });
      // the shirt hem always clears the seat under it
      const wk = (i) => (i <= 3 ? lerp(hw, bw, i / 3) : bw);
      // the shirt always clears the seat under it: no trouser pokes through a hem
      const lowAt = (yf) => { let i = 1; while (i < lower.length - 1 && lower[i][0] < yf) i++;
        const a = lower[i - 1], b = lower[i], t = clamp01((yf - a[0]) / (b[0] - a[0])); return a.map((v, j) => lerp(v, b[j], t)); };
      upper.forEach((row, i) => {
        if (row[0] > 0.63) return;
        const lo = lowAt(row[0]), m = tucked && i === 0 ? 0.001 : 0.01;
        row[1] = Math.max(row[1], (lo[1] * hw + m) / wk(i)); row[2] = Math.max(row[2], lo[2] + m); row[3] = Math.max(row[3], lo[3] + m);
      });
      const torsoLower = lower.map((row) => ring(row, hw));
      const torsoUpper = upper.map((row, i) => ring(row, wk(i), jacket ? 0.006 * k : 0));
      // a ring interpolated anywhere in the shirt table, pushed out by `extra` metres
      const ringAt = (yf, extra) => {
        let i = 1; while (i < upper.length - 1 && upper[i][0] < yf) i++;
        const a = upper[i - 1], b = upper[i], t = clamp01((yf - a[0]) / (b[0] - a[0]));
        const row = a.map((v, j) => lerp(v, b[j], t)); row[0] = yf;
        return ring(row, lerp(wk(i - 1), wk(i), t), (jacket ? 0.006 * k : 0) + extra);
      };
      const body = new THREE.Group();
      body.add(new THREE.Mesh(loft(torsoLower, { seg: 28, per: 4, n: 2.3, ref: [1, 0, 0], capStart: 'dome', domeK: 0.5 }), trouserM));
      body.add(new THREE.Mesh(loft(torsoUpper, { seg: 32, per: 4, n: 2.2, ref: [1, 0, 0], capStart: 'flat', capEnd: 'flat' }), shirtM));
      const frontZ = (yf) => {           // the shirt's front surface at a height fraction
        for (let i = 1; i < upper.length; i++) if (yf <= upper[i][0]) {
          const t = (yf - upper[i - 1][0]) / (upper[i][0] - upper[i - 1][0]);
          return (lerp(upper[i - 1][2], upper[i][2], t) + lerp(upper[i - 1][4], upper[i][4], t)) * k + (jacket ? 0.006 * k : 0);
        }
        return 0.05 * k;
      };
      // belt with a buckle, when the shirt is tucked or short
      if (!jacket) {
        const beltY = 0.598;
        const belt = new THREE.Mesh(loft([ring([beltY - 0.008, 0.157, 0.103 + bk, 0.095, 0.002], hw, 0.004 * k), ring([beltY + 0.008, 0.157, 0.103 + bk, 0.095, 0.002], hw, 0.004 * k)],
          { seg: 28, per: 2, n: 2.3 }), K.mat('p-belt', { color: 0x2b1c12, roughness: 0.55 }));
        if (tucked) {
          body.add(belt);
          const bz = (0.103 + bk + 0.006) * k;
          const buckle = TXT.roundedBox(0.06 * k * (role === 'resident' && shoeStyle === 'western' ? 1.3 : 1), 0.042 * k, 0.008 * k, 0.004 * k, K.finish.chrome());
          buckle.position.set(0, Yl(beltY), bz); body.add(buckle);
        }
      }
      // collar, placket and buttons for button shirts, the V and tie for a suit
      if (shirtKind === 'plaid' || shirtKind === 'button' || shirtKind === 'work' || shirtKind === 'polo') {
        const col = new THREE.Mesh(loft([
          { p: [0, Yl(0.846), -0.008 * k], rx: 0.07 * k, ry: 0.062 * k }, { p: [0, Yl(0.862), -0.012 * k], rx: 0.068 * k, ry: 0.06 * k }],
        { seg: 24, per: 2 }), shirtM);
        body.add(col);
        // collar points folded down on the chest
        for (const s of [1, -1]) {
          const pt = TXT.extrude([[0, 0], [s * 0.05 * k, -0.008 * k], [s * 0.022 * k, -0.055 * k]], 0.004 * k, shirtM, { bevel: false });
          pt.position.set(s * 0.012 * k, Yl(0.853), frontZ(0.836) - 0.006 * k); pt.rotation.x = -0.45; body.add(pt);
        }
        const btnM = K.mat('p-btn', { color: 0xe9e4d8, roughness: 0.3 });
        for (let b = 0; b < (shirtKind === 'polo' ? 2 : 6); b++) {
          const yf = 0.82 - b * 0.036; if (yf < hemY + 0.01) break;
          const bt = new THREE.Mesh(new THREE.CylinderGeometry(0.0055 * k, 0.0055 * k, 0.003 * k, 10), btnM);
          bt.rotation.x = Math.PI / 2; bt.position.set(0, Yl(yf), frontZ(yf) + 0.001 * k); body.add(bt);
        }
        if (shirtKind === 'plaid' || shirtKind === 'work') for (const s of [1, -1]) {   // chest pockets with flaps
          const pk = TXT.roundedBox(0.075 * k, 0.012 * k, 0.012 * k, 0.003 * k, shirtM);
          pk.position.set(s * 0.085 * k, Yl(0.755), frontZ(0.755) - 0.002 * k); body.add(pk);
        }
      } else if (shirtKind === 'tee') {
        const neck = new THREE.Mesh(new THREE.TorusGeometry(0.066 * k, 0.006 * k, 6, 28), shirtM);
        neck.rotation.x = Math.PI / 2 - 0.25; neck.scale.set(1, 0.85, 1); neck.position.set(0, Yl(0.852), 0.004 * k); body.add(neck);
      }
      if (jacket) {
        /* the shirt V, the tie and the lapels follow the jacket's front surface row by row */
        const strip = (rows, mat, seg) => {
          // rows: [yf, xLeft, xRight, dz]; a ribbon over the chest, 2 quads wide
          const pos = [], idx = [];
          rows.forEach(([yf, x0, x1, dz], i) => {
            for (let j = 0; j <= 2; j++) {
              const x = lerp(x0, x1, j / 2);
              const hwid = ringAt(yf, 0).rx, bow = 1 - Math.pow(Math.min(1, Math.abs(x) / hwid), 2.2);
              pos.push(x, Yl(yf), (frontZ(yf) - (jacket ? 0 : 0)) * Math.pow(Math.max(0, bow), 1 / 2.2) + dz);
            }
            if (i > 0) for (let j = 0; j < 2; j++) { const a0 = (i - 1) * 3 + j, b0 = i * 3 + j; idx.push(a0, a0 + 1, b0, b0, a0 + 1, b0 + 1); }
          });
          const g = new THREE.BufferGeometry();
          g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
          return new THREE.Mesh(g, mat);
        };
        const ys = []; for (let y = 0.852; y >= 0.69; y -= 0.012) ys.push(+y.toFixed(3));
        const vw = (yf) => 0.056 * k * clamp01((yf - 0.69) / 0.16);
        const white = K.mat('p-white2', { color: 0xf3f1ec, roughness: 0.7, side: THREE.DoubleSide });
        body.add(strip(ys.map((y) => [y, -vw(y), vw(y), 0.0025 * k]), white));
        const tieM = K.mat('p-tie', { color: tie, roughness: 0.45, sheen: 0.6, sheenColor: 0xffffff, side: THREE.DoubleSide }, true);
        const tw2 = (yf) => yf > 0.835 ? 0.011 * k : lerp(0.03, 0.009, (yf - 0.7) / 0.135) * k;
        const tys = ys.filter((y) => y >= 0.7).concat([0.69]);
        body.add(strip(tys.map((y) => [y, -tw2(y) * (y < 0.7 ? 0.1 : 1), tw2(y) * (y < 0.7 ? 0.1 : 1), 0.0045 * k]), tieM));
        const knot = TXT.roundedBox(0.024 * k, 0.02 * k, 0.012 * k, 0.005 * k, tieM);
        knot.position.set(0, Yl(0.846), frontZ(0.846) + 0.003 * k); body.add(knot);
        // lapels: raised jacket-coloured bands along each side of the V
        const lap = K.mat('p-lapel', { color: new THREE.Color(shirtM.color).multiplyScalar(0.8).getHex(), roughness: 0.5, side: THREE.DoubleSide });
        for (const sd of [1, -1]) body.add(strip(ys.map((y) => { const x = vw(y); const lw = (0.012 + 0.03 * clamp01((0.852 - y) / 0.06) * clamp01((y - 0.69) / 0.1)) * k;
          return sd > 0 ? [y, x, x + lw, 0.004 * k] : [y, -x - lw, -x, 0.004 * k]; }), lap));
        const bt = new THREE.Mesh(new THREE.SphereGeometry(0.008 * k, 10, 6), K.mat('p-sbtn', { color: 0x151515, roughness: 0.3 }));
        bt.scale.z = 0.5; bt.position.set(0, Yl(0.655), frontZ(0.655) + 0.003 * k); body.add(bt);
        const pocket = (x, yf) => { const pk = TXT.roundedBox(0.1 * k, 0.012 * k, 0.01 * k, 0.003 * k, shirtM); pk.position.set(x, Yl(yf), frontZ(yf) * 0.93); body.add(pk); };
        pocket(0.1 * k, 0.58); pocket(-0.1 * k, 0.58);
      }

      // hi-vis vest and hard hat for workers
      const vest = o.vest === true || (o.vest === 'auto' || o.vest == null) && role === 'worker';
      if (vest) {
        const hv = cloth('hivis', pick(r, [0xc8f02a, 0xf06a1c, 0xd4f230]));
        const refl = K.mat('p-refl', { color: 0xcfd3d6, roughness: 0.25, metalness: 0.6, emissive: 0x303234, emissiveIntensity: 0.3 });
        const vr = [0.585, 0.62, 0.66, 0.7, 0.74, 0.775, 0.8].map((yf) => ringAt(yf, 0.011 * k));
        body.add(new THREE.Mesh(loft(vr, { seg: 32, per: 3, n: 2.2, capStart: "flat" }), hv));
        for (const yf of [0.635, 0.695]) {
          const band = loft([ringAt(yf - 0.01, 0.014 * k), ringAt(yf + 0.01, 0.014 * k)], { seg: 32, per: 2, n: 2.2 });
          body.add(new THREE.Mesh(band, refl));
        }
        for (const s of [1, -1]) {   // shoulder straps
          const st = loft([
            { p: [s * 0.1 * k, Yl(0.79), frontZ(0.79) + 0.006 * k], rx: 0.032 * k, ry: 0.005 * k },
            { p: [s * 0.11 * k, Yl(0.818), frontZ(0.815) - 0.02 * k], rx: 0.032 * k, ry: 0.005 * k },
            { p: [s * 0.115 * k, Yl(0.836), -0.005 * k], rx: 0.032 * k, ry: 0.005 * k },
            { p: [s * 0.11 * k, Yl(0.815), -0.08 * k], rx: 0.032 * k, ry: 0.005 * k },
            { p: [s * 0.1 * k, Yl(0.79), -0.105 * k], rx: 0.032 * k, ry: 0.005 * k }], { seg: 10, per: 4, n: 3, ref: [1, 0, 0] });
          body.add(new THREE.Mesh(st, hv));
        }
      }

      /* LEGS and SHOES */
      for (const s of [1, -1]) {
        const L = leg[s];
        const at = (a, b, t) => a.clone().lerp(b, t).toArray();
        const top = L.hip.clone().add(V3(-s * 0.012 * k, 0.07 * k, 0.004 * k));
        const wide = 1;
        const tr = [
          { p: top.toArray(), rx: 0.094 * k * hw, ry: 0.1 * k },
          { p: at(L.hip, L.knee, 0.22), rx: 0.086 * k * hw, ry: 0.09 * k },
          { p: at(L.hip, L.knee, 0.65), rx: 0.07 * k * hw, ry: 0.072 * k },
          { p: L.knee.toArray(), rx: 0.057 * k, ry: 0.06 * k },
          { p: at(L.knee, L.ankle, 0.35), rx: 0.057 * k, ry: 0.061 * k },
          { p: at(L.knee, L.ankle, 0.75), rx: 0.052 * k * wide, ry: 0.054 * k },
          { p: L.ankle.clone().add(V3(0, -0.02 * k, 0)).toArray(), rx: 0.056 * k, ry: 0.06 * k }];
        G.add(new THREE.Mesh(loft(tr, { seg: 20, per: 4, ref: [1, 0, 0], capEnd: 'flat', capStart: 'dome' }), trouserM));
        const sh = shoe(k, shoeStyle, shoeUpper, soleM);
        const foot = new THREE.Group(); foot.add(sh);
        // pitch the foot so it meets the ground (heel up on a trailing walk leg)
        const ay = L.ankle.y, heelLift = sh.userData.lift || 0;
        let pitch = 0;
        if (ay > ankleH + 0.004 * k) {
          // solve directly: toe at local (y = -ankleH, z = Lt); after rotation about x by +a (toe down)
          const Lt = 0.19 * k;
          let best = 0, err = 1e9;
          for (let a = 0; a < 1.2; a += 0.005) {
            const ty = ay + (-ankleH) * Math.cos(a) - Lt * Math.sin(a);
            if (Math.abs(ty) < err) { err = Math.abs(ty); best = a; }
          }
          pitch = best;
        } else if (L.t.z > 0.2) pitch = -0.12;       // leading heel strike, toe up a touch
        foot.position.set(L.ankle.x, L.ankle.y, L.ankle.z);
        sh.position.y = -ankleH + heelLift;
        foot.rotation.x = pitch; foot.rotation.y = s * 0.08;
        G.add(foot);
      }

      /* ARMS: skin under, sleeve over, hand at the wrist */
      const shoulders = {};
      for (const s of [1, -1]) {
        const A = arm[s];
        const S0 = V3(s * shoulderX, Yl(0.793), -0.004 * k);
        const E = S0.clone().addScaledVector(A.u, upperArm);
        let Wr = E.clone().addScaledVector(A.f, foreArm);
        if (A.hand === 'hip') {        // hands land on the hip crest
          const target = V3(s * 0.165 * k * hw, Yl(0.585), 0.01 * k);
          const d = target.clone().sub(S0), len = d.length();
          const reach = Math.min(len, upperArm + foreArm - 0.001);
          // elbow out to the side on the plane through the shoulder
          const a = (upperArm * upperArm - foreArm * foreArm + reach * reach) / (2 * reach);
          const hgt = Math.sqrt(Math.max(0, upperArm * upperArm - a * a));
          const dn = d.clone().normalize(), out = V3(s, 0, -0.35).sub(dn.clone().multiplyScalar(V3(s, 0, -0.35).dot(dn))).normalize();
          E.copy(S0).addScaledVector(dn, a).addScaledVector(out, hgt);
          Wr = S0.clone().addScaledVector(dn, reach);
        }
        const Ud = E.clone().sub(S0).normalize(), Fd = Wr.clone().sub(E).normalize();
        const at = (a, b, t) => a.clone().lerp(b, t).toArray();
        const armPts = [
          { p: S0.clone().addScaledVector(Ud, -0.012 * k).toArray(), rx: 0.05 * k * bw, ry: 0.054 * k },
          { p: at(S0, E, 0.3), rx: 0.047 * k * bw, ry: 0.05 * k },
          { p: at(S0, E, 0.72), rx: 0.041 * k, ry: 0.043 * k },
          { p: E.toArray(), rx: 0.036 * k, ry: 0.038 * k },
          { p: at(E, Wr, 0.25), rx: 0.04 * k, ry: 0.037 * k },
          { p: at(E, Wr, 0.7), rx: 0.032 * k, ry: 0.028 * k },
          { p: Wr.toArray(), rx: 0.027 * k, ry: 0.02 * k }];
        const armRef = [0, 0, 1];
        const cover = jacket || sleeves === 'long' ? 1 : sleeves === 'rolled' ? 0.55 : 0.28;   // fraction of the arm the sleeve covers
        if (cover < 1) G.add(new THREE.Mesh(loft(armPts, { seg: 16, per: 4, ref: armRef, capStart: 'dome', domeK: 0.55, capEnd: 'flat' }), skin));
        // sleeve: the same line, a little fuller, ending in a cuff
        const sl = [];
        const along = [0, 0.3 / 2, 0.72 / 2, 0.5, 0.625, 0.85, 1];
        for (let i = 0; i < armPts.length; i++) if (along[i] <= cover + 1e-6) sl.push(Object.assign({}, armPts[i], { rx: armPts[i].rx + (cover < 1 ? 0.01 : 0.007) * k, ry: armPts[i].ry + (cover < 1 ? 0.01 : 0.007) * k }));
        if (cover < 1) {
          const idx = along.findIndex((v) => v > cover);
          const t = (cover - along[idx - 1]) / (along[idx] - along[idx - 1]);
          const pa = V3(...armPts[idx - 1].p), pb = V3(...armPts[idx].p);
          const rr = lerp(armPts[idx - 1].rx, armPts[idx].rx, t) + 0.013 * k * (sleeves === 'rolled' ? 1.3 : 1);
          sl.push({ p: pa.lerp(pb, t).toArray(), rx: rr, ry: rr });
        } else {
          sl[sl.length - 1].rx = 0.036 * k; sl[sl.length - 1].ry = 0.034 * k;
          sl[sl.length - 1].p = Wr.clone().addScaledVector(Fd, -0.01 * k).toArray();
        }
        G.add(new THREE.Mesh(loft(sl, { seg: 18, per: 4, ref: armRef, capStart: 'dome', domeK: 0.55, capEnd: 'flat' }), shirtM));
        if (cover >= 1) G.add(new THREE.Mesh(loft(armPts.slice(-2), { seg: 14, per: 2, ref: armRef, capEnd: 'flat' }), skin));   // the wrist
        if (sleeves === 'rolled') {
          const e = sl[sl.length - 1];
          const cuff = loft([{ p: V3(...e.p).addScaledVector(Fd, -0.03 * k).toArray(), rx: e.rx + 0.004 * k, ry: e.ry + 0.004 * k }, { p: e.p, rx: e.rx + 0.004 * k, ry: e.ry + 0.004 * k }], { seg: 18, per: 2, ref: armRef, capEnd: 'flat' });
          G.add(new THREE.Mesh(cuff, shirtM));
        }
        if (jacket) {     // white shirt cuff shows past the jacket sleeve
          const c = loft([{ p: Wr.clone().addScaledVector(Fd, -0.018 * k).toArray(), rx: 0.03 * k, ry: 0.027 * k }, { p: Wr.clone().addScaledVector(Fd, 0.004 * k).toArray(), rx: 0.029 * k, ry: 0.026 * k }], { seg: 14, per: 2, ref: armRef, capEnd: 'flat' });
          G.add(new THREE.Mesh(c, K.mat('p-white', { color: 0xf3f1ec, roughness: 0.7 })));
        }
        // the hand, aligned to the forearm
        const hp = A.hand === 'point' ? 'point' : A.hand === 'hip' ? 'fist' : 'relax';
        const hnd = hand(k * (fem ? 0.92 : 1), s, skin, hp);
        const hq = new THREE.Quaternion().setFromUnitVectors(V3(0, -1, 0), Fd);
        hnd.quaternion.copy(hq);
        if (A.hand === 'point') hnd.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(V3(0, 1, 0), -s * Math.PI / 2 + s * 0.2));
        if (A.hand === 'hip') hnd.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(V3(0, 1, 0), s * 0.3));
        if (A.hand === 'shade') hnd.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(V3(0, 1, 0), s * Math.PI / 2));
        hnd.position.copy(Wr).addScaledVector(Fd, 0.005 * k);
        G.add(hnd);
        shoulders[s] = S0;
        // the trapezius and shoulder cap: a smooth slope from the collar into the top of the arm
        const cap = shirtM;
        const yoke = loft([
          { p: [s * 0.03 * k, Yl(0.842), -0.01 * k], rx: 0.07 * k, ry: 0.028 * k },
          { p: [s * 0.1 * k, Yl(0.826), -0.007 * k], rx: 0.085 * k, ry: 0.04 * k },
          { p: [S0.x * 0.93, S0.y + 0.022 * k, -0.005 * k], rx: 0.075 * k, ry: 0.048 * k },
          { p: S0.clone().addScaledVector(Ud, 0.03 * k).toArray(), rx: 0.05 * k * bw, ry: 0.05 * k }],
        { seg: 20, per: 4, ref: [0, 0, 1], capStart: 'dome', domeK: 0.6 });
        G.add(new THREE.Mesh(yoke, cap));
      }

      /* NECK and HEAD */
      const Hh = 0.117 * k * (fem ? 0.97 : 1), Wd = 0.074 * k * (fem ? 0.95 : 1) * lerp(0.96, 1.05, r()), D = 0.098 * k * (fem ? 0.97 : 1);
      const headC = V3(0, H + lift - Hh, 0.004 * k);
      const neckTop = headC.clone().add(V3(0, -Hh * 0.45, -0.022 * k));
      const neck = loft([{ p: [0, Yl(0.835), -0.012 * k], rx: 0.058 * k * (fem ? 0.85 : 1), ry: 0.056 * k },
                         { p: [0, Yl(0.86), -0.012 * k], rx: 0.05 * k * (fem ? 0.85 : 1), ry: 0.05 * k },
                         { p: neckTop.toArray(), rx: 0.05 * k * (fem ? 0.85 : 1), ry: 0.05 * k }], { seg: 18, per: 3, ref: [1, 0, 0] });
      G.add(new THREE.Mesh(neck, skin));
      const head = new THREE.Group();
      const pivot = new THREE.Group(); pivot.position.copy(neckTop); G.add(pivot);
      head.position.copy(headC).sub(neckTop); pivot.add(head);
      pivot.rotation.set(headPitch, headYaw, 0, 'YXZ');
      head.add(new THREE.Mesh(headGeo(Wd, Hh, D, fem, false), skin));
      // ears
      for (const s of [1, -1]) {
        const ear = new THREE.Mesh(new THREE.SphereGeometry(1, 14, 10), skin);
        ear.scale.set(0.009 * k, 0.03 * k, 0.019 * k); ear.position.set(s * Wd * 0.97, -Hh * 0.05, -D * 0.1); ear.rotation.y = s * 0.35;
        head.add(ear);
      }
      // eyes: white, iris, set into the sockets; brows in hair colour; lips a shade deeper than skin
      const surf = (ux, uy) => headShape(ux, uy, Math.sqrt(Math.max(0, 1 - ux * ux - uy * uy)), Wd, Hh, D, fem);
      const eyeW = K.mat('p-eyew', { color: 0xe8e2d8, roughness: 0.2 });
      const iris = K.mat('p-iris', { color: pick(r, [0x2a1a10, 0x3b2615, 0x2f3b45, 0x3b4a2c]), roughness: 0.15 });
      const lipC = new THREE.Color(skinC).multiplyScalar(0.82).lerp(new THREE.Color(0x8a4a45), fem ? 0.35 : 0.18);
      for (const s of [1, -1]) {
        const p = surf(s * 0.33, 0.07);
        const e = new THREE.Mesh(new THREE.SphereGeometry(0.0115 * k, 14, 10), eyeW);
        e.position.set(p[0], p[1], p[2] - 0.0085 * k); e.scale.set(1, 0.7, 1); head.add(e);
        const ir = new THREE.Mesh(new THREE.SphereGeometry(0.0058 * k, 10, 8), iris);
        ir.position.set(p[0] - s * 0.0005 * k, p[1], p[2] + 0.0015 * k); ir.scale.set(1, 1, 0.45); head.add(ir);
        const bp = surf(s * 0.33, 0.21);
        const brow = TXT.roundedBox(0.034 * k, 0.006 * k, 0.006 * k, 0.0025 * k, hairM);
        brow.position.set(bp[0], bp[1], bp[2] + 0.0015 * k); brow.rotation.z = -s * 0.1; brow.rotation.y = s * 0.3; head.add(brow);
      }
      const mp = surf(0, -0.5);
      const lips = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 8), K.mat('p-lip-' + lipC.getHexString(), { color: lipC.getHex(), roughness: 0.45 }));
      lips.scale.set(0.022 * k, 0.0055 * k, 0.006 * k); lips.position.set(mp[0], mp[1], mp[2] - 0.003 * k); head.add(lips);
      // hair (or the edge of it under a hat), and facial hair on some men
      const hatKind = o.hat && o.hat !== 'auto' ? o.hat
        : role === 'worker' ? 'hard'
        : role === 'official' ? (r() < 0.15 ? 'cowboy' : 'none')
        : (() => { const q = r(); return q < 0.25 ? 'cowboy' : q < 0.45 ? 'cap' : 'none'; })();
      const bald = !fem && r() < 0.12 && hatKind === 'none';
      const long = fem && r() < 0.75;
      if (!bald) head.add(new THREE.Mesh(headGeo(Wd, Hh, D, fem, long ? 'long' : 'short'), hairM));
      if (long && hatKind !== 'hard') {         // a ponytail or a fall of hair down the back
        const pt = loft([{ p: [0, Hh * 0.1, -D * 0.95], rx: 0.03 * k, ry: 0.025 * k }, { p: [0, -Hh * 0.5, -D * 1.05], rx: 0.04 * k, ry: 0.03 * k },
                         { p: [0, -Hh * 1.25, -D * 0.95], rx: 0.03 * k, ry: 0.022 * k }], { seg: 12, per: 3, capStart: 'dome', capEnd: 'dome' });
        head.add(new THREE.Mesh(pt, hairM));
      }
      if (!fem && r() < 0.3) {                 // a moustache, sometimes the beard
        const mo = surf(0, -0.4);
        const m = TXT.roundedBox(0.045 * k, 0.009 * k, 0.01 * k, 0.004 * k, hairM);
        m.position.set(mo[0], mo[1], mo[2] - 0.002 * k); head.add(m);
      }
      if (hatKind !== 'none') {
        const hatC = hatKind === 'hard' ? pick(r, [0xf2f0ea, 0xf2c200, 0xf07a1a, 0xf2f0ea])
          : hatKind === 'cowboy' ? pick(r, [0xd9c69a, 0x2a2420, 0xc2b49a, 0x6b4e34, 0xe0d2a8])
          : pick(r, [0x1f2b44, 0x7a1f25, 0x3f4a3a, 0xe8e4dc, 0x2a2a2a, 0xb05a22]);
        const hm = hatKind === 'hard' ? K.mat('p-hard', { color: hatC, roughness: 0.3, clearcoat: 0.8, clearcoatRoughness: 0.2 }, true)
          : K.mat('p-hat', { color: hatC, roughness: hatKind === 'cowboy' && (hatC === 0xd9c69a || hatC === 0xe0d2a8) ? 0.85 : 0.75 });
        head.add(hat(hatKind, Wd, D, Hh * (hatKind === 'cowboy' ? 0.32 : hatKind === 'cap' ? 0.28 : 0.33), hm, r));
      }
      body.rotation.x = torsoLean; G.add(body);
      const M = mergeByMaterial(G);
      M.userData.height = H; M.userData.role = role; M.userData.pose = pose;
      return M;
    }
  }

  /* ---- a crowd ------------------------------------------------------------------------- */
  K.define('crowd', {
    size: [8, 1.8, 5],
    options: { seed: 1, n: 12, detail: 'auto', area: [8, 5], roles: ['resident'], poses: ['stand', 'stand', 'stand', 'walk', 'walk', 'hands_on_hips', 'look_up'], face: null },
    note: 'N seeded people over area [w, d] (centred), min 0.65 m apart. face: [x, z] a point they turn toward, else roughly +z.',
    make(o, r) {
      const n = o.n || 12, area = o.area || [8, 5], roles = o.roles || ['resident'], poses = o.poses || ['stand', 'stand', 'stand', 'walk', 'walk', 'hands_on_hips', 'look_up'];
      const G = new THREE.Group(), placed = [];
      for (let i = 0; i < n; i++) {
        let x = 0, z = 0, tries = 0;
        do { x = (r() - 0.5) * area[0]; z = (r() - 0.5) * area[1]; tries++; }
        while (tries < 60 && placed.some((p) => Math.hypot(p[0] - x, p[1] - z) < 0.65));
        placed.push([x, z]);
        const p = K.make('person', { detail: o.detail && o.detail !== 'auto' ? o.detail : (n > 6 ? 'low' : 'full'), seed: (o.seed || 1) * 101 + i * 17, role: pick(r, roles), pose: pick(r, poses), toward: r() < 0.5 ? 1 : -1 });
        p.position.set(x, 0, z);
        p.rotation.y = o.face ? Math.atan2(o.face[0] - x, o.face[1] - z) + (r() - 0.5) * 0.4 : (r() - 0.5) * 0.9;
        G.add(p);
      }
      return G;
    },
  });
}
