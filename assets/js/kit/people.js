/* kit/people.js, see assets/js/txkit.js for the conventions.
 *
 * `person` is the scale reference every frame uses: an articulated adult on a posed skeleton.
 * Everything is in metres, the person stands on y = 0 and faces +z. Their LEFT is +x.
 *
 *   GARMENTS are signed distance fields meshed by surface nets (sdfMesh). The shirt or jacket
 *   is ONE field: the torso table, both trapezius slopes and both sleeves blended with a
 *   smooth minimum, so cloth runs from the collar over the shoulder into the sleeve with no
 *   shell, shelf or armpit notch. The trousers are the seat and both legs as one field. Hems
 *   are plane cuts; elbow, knee, ankle-break, waist and blousing folds are displacements of
 *   the field, so they exist as geometry and shade from the field's own gradient.
 *   HEAD is a sphere sculpted into skull, brow, sockets, nose, lips and chin, sampled densely
 *   where the face is, with a vertex tint (warm cheeks and nose, darker sockets, beard shadow).
 *   Eyes have sclera, iris, pupil, lids, a lash line; brows follow the ridge.
 *   HAIR is a shell grown off the scalp by a per-style thickness (crop, side part, curly,
 *   buzz, receding, bald; long, bob, bun, curly long) plus a hanging curtain for long styles.
 *   SHOES are a last-shaped upper on a sole with thickness, toe spring, heel and laces.
 *   Build varies by seed from slim to heavy (belly, thighs, arms, neck, face).
 *
 * detail 'low' (crowds) keeps the same construction on coarser grids with simpler eyes/hands.
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

  /* ---- SIGNED DISTANCE garments -----------------------------------------------------------
   * A garment is ONE distance field: the torso, the trapezius and both sleeves are blended
   * with a smooth minimum, so the cloth runs from the collar over the shoulder into the sleeve
   * with no shell, shelf or notch. Hems are plane cuts, folds are displacements of the field.
   * sdfMesh meshes a field with surface nets on a narrow band (coarse pass, then only the
   * blocks the surface passes through), projects every vertex onto the surface and takes its
   * normal from the field's gradient, so the shading is smooth at a centimetre grid. */
  const smin = (a, b, k) => {
    if (k <= 1e-9) return a < b ? a : b;
    const h = Math.max(k - Math.abs(a - b), 0) / k;
    return (a < b ? a : b) - h * h * k * 0.25;
  };
  const smax = (a, b, k) => -smin(-a, -b, k);
  function ell2(x, z, a, c) {            // approximate signed distance to an ellipse
    const qx = x / a, qz = z / c, k0 = Math.sqrt(qx * qx + qz * qz);
    if (k0 < 1e-6) return -Math.min(a, c);
    const px = x / (a * a), pz = z / (c * c);
    return k0 * (k0 - 1) / Math.sqrt(px * px + pz * pz);
  }
  /* A tube through points with a radius per point. f(x,y,z) is the distance; f.info holds the
   * nearest segment's arc length, and the cos/sin of the angle around it (0 = the frame's N). */
  function tube(pts, rad, o) {
    o = o || {};
    const n = pts.length - 1, S = [], cum = [0], ref = o.ref || [0, 0, 1], k = o.k || 0;
    for (let i = 0; i < n; i++) {
      const a = pts[i], b = pts[i + 1];
      const dx = b[0] - a[0], dy = b[1] - a[1], dz = b[2] - a[2], l2 = dx * dx + dy * dy + dz * dz, l = Math.sqrt(l2) || 1e-6;
      const tx = dx / l, ty = dy / l, tz = dz / l;
      let nx = ref[0], ny = ref[1], nz = ref[2];
      let dp = nx * tx + ny * ty + nz * tz; nx -= dp * tx; ny -= dp * ty; nz -= dp * tz;
      let nl = Math.sqrt(nx * nx + ny * ny + nz * nz);
      if (nl < 1e-4) { nx = 1; ny = 0; nz = 0; dp = tx; nx -= dp * tx; ny -= dp * ty; nz -= dp * tz; nl = Math.sqrt(nx * nx + ny * ny + nz * nz); }
      nx /= nl; ny /= nl; nz /= nl;
      const bx = ty * nz - tz * ny, by = tz * nx - tx * nz, bz = tx * ny - ty * nx;
      S.push({ ax: a[0], ay: a[1], az: a[2], dx, dy, dz, l2: l2 || 1e-9, l, r0: rad[i], r1: rad[i + 1], nx, ny, nz, bx, by, bz, tx, ty, tz });
      cum.push(cum[i] + l);
    }
    const info = { along: 0, c: 1, s: 0, seg: 0, dist: 0 };
    const f = (x, y, z) => {
      let best = 1e9, out = 1e9;
      for (let i = 0; i < n; i++) {
        const s = S[i], px = x - s.ax, py = y - s.ay, pz = z - s.az;
        let t = (px * s.dx + py * s.dy + pz * s.dz) / s.l2; t = t < 0 ? 0 : t > 1 ? 1 : t;
        const vx = px - s.dx * t, vy = py - s.dy * t, vz = pz - s.dz * t, vl = Math.sqrt(vx * vx + vy * vy + vz * vz);
        const d = vl - (s.r0 + (s.r1 - s.r0) * t);
        if (d < best) {
          best = d; info.along = cum[i] + t * s.l; info.seg = i; info.dist = vl;
          const il = vl > 1e-6 ? 1 / vl : 0;
          info.c = (vx * s.nx + vy * s.ny + vz * s.nz) * il; info.s = (vx * s.bx + vy * s.by + vz * s.bz) * il;
        }
        out = i === 0 ? d : smin(out, d, k);
      }
      return out;
    };
    f.info = info; f.len = cum[n]; f.cum = cum; f.S = S;
    { // a bounding sphere, so a caller can skip the tube when it can't win
      let mn = [1e9, 1e9, 1e9], mx = [-1e9, -1e9, -1e9], rm = 0;
      pts.forEach((p) => { for (let j = 0; j < 3; j++) { mn[j] = Math.min(mn[j], p[j]); mx[j] = Math.max(mx[j], p[j]); } });
      rad.forEach((v) => { rm = Math.max(rm, v); });
      const cx = (mn[0] + mx[0]) / 2, cy = (mn[1] + mx[1]) / 2, cz = (mn[2] + mx[2]) / 2;
      const R0 = Math.hypot(mx[0] - cx, mx[1] - cy, mx[2] - cz) + rm + 0.012;
      f.lb = (x, y, z) => Math.sqrt((x - cx) * (x - cx) + (y - cy) * (y - cy) + (z - cz) * (z - cz)) - R0;
    }
    f.at = (along) => {       // the point and direction at an arc length
      let i = 0; while (i < n - 1 && cum[i + 1] < along) i++;
      const s = S[i], t = clamp01((along - cum[i]) / s.l);
      return { p: [s.ax + s.dx * t, s.ay + s.dy * t, s.az + s.dz * t], d: [s.tx, s.ty, s.tz], r: s.r0 + (s.r1 - s.r0) * t };
    };
    return f;
  }
  function sdfMesh(f, box, h, U) {
    const C = 8, pad = 2 * h;
    const x0 = box[0] - pad, y0 = box[1] - pad, z0 = box[2] - pad;
    const cnt = (a, b) => Math.ceil((b - a + 2 * pad) / (h * C)) * C + 1;
    const NX = cnt(box[0], box[3]), NY = cnt(box[1], box[4]), NZ = cnt(box[2], box[5]);
    const SY = NX, SZ = NX * NY, N = NX * NY * NZ;
    const val = new Float32Array(N).fill(NaN);
    const ev = (i, j, k) => { const q = i + j * SY + k * SZ; let v = val[q]; if (v !== v) { v = f(x0 + i * h, y0 + j * h, z0 + k * h); val[q] = v; } return v; };
    // hierarchical narrow band: a block is split only while the surface can pass through it
    const cells = [];
    const refine = (i, j, k, s) => {
      if (s === 1) { cells.push(i, j, k); return; }
      let near = false, pos = false, neg = false;
      const band = s * h * (s <= 2 ? 0.92 : 1.1);
      for (let c = 0; c < 8; c++) {
        const v = ev(i + (c & 1) * s, j + ((c >> 1) & 1) * s, k + ((c >> 2) & 1) * s);
        if (v < band && v > -band) near = true;
        if (v > 0) pos = true; else neg = true;
      }
      if (!near && !(pos && neg)) return;
      const t = s >> 1;
      for (let c = 0; c < 8; c++) refine(i + (c & 1) * t, j + ((c >> 1) & 1) * t, k + ((c >> 2) & 1) * t, t);
    };
    for (let k = 0; k + C < NZ; k += C) for (let j = 0; j + C < NY; j += C) for (let i = 0; i + C < NX; i += C) refine(i, j, k, C);
    const OFF = [0, 1, SY, 1 + SY, SZ, 1 + SZ, SY + SZ, 1 + SY + SZ];
    const EA = [0, 2, 4, 6, 0, 1, 4, 5, 0, 1, 2, 3], EB = [1, 3, 5, 7, 2, 3, 6, 7, 4, 5, 6, 7];
    const cid = new Int32Array(N).fill(-1), P = [], cellQ = [], cv = new Float64Array(8);
    for (let n = 0; n < cells.length; n += 3) {
      const i = cells[n], j = cells[n + 1], k = cells[n + 2];
      const q = i + j * SY + k * SZ;
      let mask = 0;
      for (let c = 0; c < 8; c++) { const v = ev(i + (c & 1), j + ((c >> 1) & 1), k + ((c >> 2) & 1)); cv[c] = v; if (v < 0) mask |= 1 << c; }
      if (mask === 0 || mask === 255) continue;
      let sx = 0, sy = 0, sz = 0, m = 0;
      for (let e = 0; e < 12; e++) {
        const a = EA[e], bb = EB[e];
        if (((mask >> a) & 1) === ((mask >> bb) & 1)) continue;
        const t = cv[a] / (cv[a] - cv[bb]);
        sx += (a & 1) + (((bb & 1) - (a & 1)) * t); sy += ((a >> 1) & 1) + ((((bb >> 1) & 1) - ((a >> 1) & 1)) * t);
        sz += ((a >> 2) & 1) + ((((bb >> 2) & 1) - ((a >> 2) & 1)) * t); m++;
      }
      cid[q] = P.length / 3;
      P.push(x0 + (i + sx / m) * h, y0 + (j + sy / m) * h, z0 + (k + sz / m) * h);
      cellQ.push(q, i, j, k);
    }
    const AX = [1, SY, SZ], quads = [];
    for (let c = 0; c < cellQ.length; c += 4) {
      const q = cellQ[c], v0 = val[q];
      for (let a = 0; a < 3; a++) {
        const v1 = val[q + AX[a]];
        if (v1 !== v1 || (v0 < 0) === (v1 < 0)) continue;
        const u = (a + 1) % 3, w = (a + 2) % 3;
        if (cellQ[c + 1 + u] === 0 || cellQ[c + 1 + w] === 0) continue;
        const c1 = cid[q - AX[u]], c2 = cid[q - AX[u] - AX[w]], c3 = cid[q - AX[w]];
        if (c1 < 0 || c2 < 0 || c3 < 0) continue;
        quads.push(cid[q], c1, c2, c3);
      }
    }
    // project onto the surface, normal from the gradient
    const nv = P.length / 3, NR = new Float32Array(nv * 3), e = h * 0.3;
    for (let v = 0; v < nv; v++) {
      let x = P[v * 3], y = P[v * 3 + 1], z = P[v * 3 + 2];
      let gx = 0, gy = 0, gz = 1;
      for (let it = 0; it < 1; it++) {
        const a = f(x + e, y - e, z - e), b = f(x - e, y - e, z + e), c = f(x - e, y + e, z - e), dd = f(x + e, y + e, z + e);
        const d = (a + b + c + dd) / 4;
        gx = a - b - c + dd; gy = -a - b + c + dd; gz = -a + b - c + dd;
        const gl = Math.sqrt(gx * gx + gy * gy + gz * gz) / (4 * e);
        if (gl < 1e-6) break;
        gx /= 4 * e * gl; gy /= 4 * e * gl; gz /= 4 * e * gl;
        const st = Math.max(-h * 0.6, Math.min(h * 0.6, d / gl));
        x -= gx * st; y -= gy * st; z -= gz * st;
        if (Math.abs(d) < h * 0.08) break;
      }
      P[v * 3] = x; P[v * 3 + 1] = y; P[v * 3 + 2] = z; NR[v * 3] = gx; NR[v * 3 + 1] = gy; NR[v * 3 + 2] = gz;
    }
    const pos = [], nor = [], uv = [], tmp = [0, 0, 0];
    const VR = new Int8Array(nv), VU = new Float32Array(nv * 2);
    let PER = 0;
    if (U) for (let v = 0; v < nv; v++) {
      const reg = U.region(P[v * 3], P[v * 3 + 1], P[v * 3 + 2]); VR[v] = reg;
      U.uv(P[v * 3], P[v * 3 + 1], P[v * 3 + 2], reg, tmp); VU[v * 2] = tmp[0]; VU[v * 2 + 1] = tmp[1]; PER = tmp[2];
    }
    const tri = (a, b, c) => {
      const ax = P[a * 3], ay = P[a * 3 + 1], az = P[a * 3 + 2];
      const ux = P[b * 3] - ax, uy = P[b * 3 + 1] - ay, uz = P[b * 3 + 2] - az, wx = P[c * 3] - ax, wy = P[c * 3 + 1] - ay, wz = P[c * 3 + 2] - az;
      const fx = uy * wz - uz * wy, fy = uz * wx - ux * wz, fz = ux * wy - uy * wx;
      if (fx * fx + fy * fy + fz * fz < 1e-14) return;
      const sn = fx * (NR[a * 3] + NR[b * 3] + NR[c * 3]) + fy * (NR[a * 3 + 1] + NR[b * 3 + 1] + NR[c * 3 + 1]) + fz * (NR[a * 3 + 2] + NR[b * 3 + 2] + NR[c * 3 + 2]);
      const ids = sn < 0 ? [a, c, b] : [a, b, c];
      const reg = VR[a] === VR[b] || VR[a] === VR[c] ? VR[a] : VR[b];
      const us = [];
      let per = 0;
      for (const id of ids) {
        pos.push(P[id * 3], P[id * 3 + 1], P[id * 3 + 2]); nor.push(NR[id * 3], NR[id * 3 + 1], NR[id * 3 + 2]);
        if (!U) { us.push(0, 0); continue; }
        if (VR[id] === reg) { us.push(VU[id * 2], VU[id * 2 + 1]); per = PER; }
        else { U.uv(P[id * 3], P[id * 3 + 1], P[id * 3 + 2], reg, tmp); us.push(tmp[0], tmp[1]); per = tmp[2]; }
      }
      if (per > 0) {                      // unwrap a cylindrical seam inside one triangle
        const lo = Math.min(us[0], us[2], us[4]), hi = Math.max(us[0], us[2], us[4]);
        if (hi - lo > per / 2) for (let q = 0; q < 6; q += 2) if (us[q] < (lo + hi) / 2) us[q] += per;
      }
      uv.push(...us);
    };
    for (let i = 0; i < quads.length; i += 4) {
      const a = quads[i], b = quads[i + 1], c = quads[i + 2], d = quads[i + 3];
      const dac = (P[a * 3] - P[c * 3]) ** 2 + (P[a * 3 + 1] - P[c * 3 + 1]) ** 2 + (P[a * 3 + 2] - P[c * 3 + 2]) ** 2;
      const dbd = (P[b * 3] - P[d * 3]) ** 2 + (P[b * 3 + 1] - P[d * 3 + 1]) ** 2 + (P[b * 3 + 2] - P[d * 3 + 2]) ** 2;
      if (dac < dbd) { tri(a, b, c); tri(a, c, d); } else { tri(a, b, d); tri(b, c, d); }
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
    return g;
  }
  K.sdfMesh = K.sdfMesh || sdfMesh;

  /* ---- cloth, painted locally: colour maps and tileable normal maps ----------------------- */
  const CT = new Map();
  const hex = (v) => '#' + v.toString(16).padStart(6, '0');
  function clothTex(kind, a, b, c) {
    const key = kind + a + b + c;
    if (CT.has(key)) return CT.get(key);
    const N = 256, cv = document.createElement('canvas'); cv.width = cv.height = N;
    const x = cv.getContext('2d'), r = K.rng(31 + kind.length * 7);
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
    } else if (kind === 'strands') {
      /* HAIR ALBEDO IN LOCKS, NOT GRAIN (weekly pass 2026-10-16). It was 260 streaks each the full
       * height of the tile, which is how wood grain is drawn, and at full size the judges and the
       * 2026-10-12 pass read it as wood grain on a pale cap. Hair clumps: each lock is a band with
       * a shaded parting at both edges and a sheen down its middle, the widths uneven and scaled to
       * close the tile exactly so no seam shows, and the fine strands inside are short and of
       * uneven length so no single streak runs the height of the head. */
      /* SOFTER LOCKS (2026-11-15, "a hairnet"). The lock bands were narrow with dark partings and
       * 520 fine streaks over them, which at a deck's scale beat into a regular ridged grain. Locks are
       * wider and uneven now, their shading a soft roll rather than a groove, and the fine strands are
       * fewer and fainter, so the map adds texture without drawing lines. The value of the hair (dark
       * roots, darker creases, one lock lighter than the next) is in the vertex colour, not here. */
      x.fillStyle = '#ffffff'; x.fillRect(0, 0, N, N);
      const ws = []; let tot = 0;
      while (tot < N) { const w = 12 + r() * 22; ws.push(w); tot += w; }
      let px = 0;
      for (const w0 of ws) {
        const w = w0 * N / tot, dk = 0.07 + r() * 0.08, lt = r() * 0.06;
        const gr = x.createLinearGradient(px, 0, px + w, 0);
        gr.addColorStop(0, 'rgba(0,0,0,' + dk + ')'); gr.addColorStop(0.45, 'rgba(0,0,0,' + lt + ')');
        gr.addColorStop(0.7, 'rgba(0,0,0,' + (lt * 0.5) + ')'); gr.addColorStop(1, 'rgba(0,0,0,' + (dk * 0.9) + ')');
        x.fillStyle = gr; x.fillRect(px, 0, w, N);
        px += w;
      }
      for (let i = 0; i < 220; i++) {
        const sx = r() * N, sy = r() * N, len = 12 + r() * 50;
        x.fillStyle = 'rgba(0,0,0,' + (0.03 + r() * 0.05) + ')';
        x.fillRect(sx, sy, 1, len); if (sy + len > N) x.fillRect(sx, sy - N, 1, len);
      }
    }
    const t = new THREE.CanvasTexture(cv);
    t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    const rep = kind === 'plaid' ? 1 / 0.16 : kind === 'denim' ? 1 / 0.05 : kind === 'strands' ? 1 / 0.06 : 1 / 0.04;
    if (kind === 'strands') t.repeat.set(5, 1.5); else t.repeat.set(rep, rep);
    CT.set(key, t);
    return t;
  }
  /* Tileable normal maps from a height field of integer-frequency waves. `crumple`: the soft
   * wrinkles cloth carries below the geometry's resolution. `strands`: hair, along v. */
  const NT = new Map();
  function normTex(kind) {
    if (NT.has(kind)) return NT.get(kind);
    const N = 192, r = K.rng(kind === 'crumple' ? 811 : 977), Hf = new Float32Array(N * N);
    const waves = [];
    if (kind === 'crumple') {
      for (let i = 0; i < 26; i++) {
        const fx = Math.round((r() - 0.5) * 12), fy = Math.round((r() - 0.5) * 12) || 1;
        waves.push([fx, fy, r() * 6.283, 1 / Math.pow(Math.hypot(fx, fy), 1.1)]);
      }
    } else {
      for (let i = 0; i < 30; i++) waves.push([Math.round(8 + r() * 30), Math.round((r() - 0.5) * 3), r() * 6.283, 0.6 + r() * 0.4]);
    }
    for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
      let s = 0;
      for (const w of waves) s += w[3] * Math.sin(6.2832 * (w[0] * i + w[1] * j) / N + w[2]);
      Hf[j * N + i] = kind === 'crumple' ? Math.abs(s) * -1 + s * 0.3 : s;   // ridged: creases, not ripples
    }
    const cv = document.createElement('canvas'); cv.width = cv.height = N;
    const x = cv.getContext('2d'), img = x.createImageData(N, N);
    const amp = kind === 'crumple' ? 2.2 : 1.4;
    for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
      const dx = (Hf[j * N + ((i + 1) % N)] - Hf[j * N + ((i + N - 1) % N)]) * amp, dy = (Hf[((j + 1) % N) * N + i] - Hf[((j + N - 1) % N) * N + i]) * amp;
      const l = Math.sqrt(dx * dx + dy * dy + 1), o = (j * N + i) * 4;
      img.data[o] = (-dx / l * 0.5 + 0.5) * 255; img.data[o + 1] = (dy / l * 0.5 + 0.5) * 255; img.data[o + 2] = (1 / l * 0.5 + 0.5) * 255; img.data[o + 3] = 255;
    }
    x.putImageData(img, 0, 0);
    const t = new THREE.CanvasTexture(cv);
    t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8;
    if (kind === 'crumple') t.repeat.set(1 / 0.5, 1 / 0.5); else t.repeat.set(5, 1.5);
    NT.set(kind, t);
    return t;
  }
  /* THE WEAVE, AT THE SIZE OF A THREAD (2026-11-15, "painted-on cloth that has no weave"). The
   * normal map was a crumple tile half a metre across, so cloth carried soft lumps and no thread at
   * all, and the lumps read as dough. Folds are geometry now (see the garment fields), so the map is
   * the cloth's own structure: a tileable height field of round threads crossing over and under,
   * plain for shirting, 2/1 twill for denim, khaki and suiting, a knit's columns of loops for a tee,
   * with a slub in every thread so no two repeats look alike. The tile is a centimetre or two, so the
   * thread pitch is real (0.5 to 1.6 mm) and mipmapping fades it with distance as a real cloth's does. */
  function weaveTex(kind) {
    const key = 'weave-' + kind;
    if (NT.has(key)) return NT.get(key);
    const N = 256, P = kind === 'twill' || kind === 'denim' ? 12 : 16, r = K.rng(kind.length * 131 + 7), Hf = new Float32Array(N * N);
    const slubW = new Float32Array(N / P * 2 + 2), slubF = new Float32Array(N / P * 2 + 2);
    for (let i = 0; i < slubW.length; i++) { slubW[i] = 0.75 + r() * 0.5; slubF[i] = 0.75 + r() * 0.5; }
    for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
      const ci = Math.floor(i / P), cj = Math.floor(j / P), fx = (i % P + 0.5) / P, fy = (j % P + 0.5) / P;
      let h;
      if (kind === 'knit') {               // columns of interlocking loops: a V per stitch
        const vx = Math.abs(fx - 0.5) * 2, v = Math.abs(((fy + vx * 0.5) % 1) - 0.5) * 2;
        h = Math.pow(Math.sin(Math.PI * fx), 0.6) * (0.55 + 0.45 * (1 - v)) * slubW[ci % slubW.length];
      } else {
        const over = kind === 'twill' || kind === 'denim' ? ((ci + cj) % 3) !== 0 : ((ci + cj) & 1) === 0;     // is the warp on top here
        const warp = Math.pow(Math.sin(Math.PI * fx), 0.7) * (0.55 + 0.45 * Math.sin(Math.PI * fy)) * slubW[ci % slubW.length];
        const weft = Math.pow(Math.sin(Math.PI * fy), 0.7) * (0.55 + 0.45 * Math.sin(Math.PI * fx)) * slubF[cj % slubF.length];
        h = over ? Math.max(warp, weft * 0.45) : Math.max(weft, warp * 0.45);
      }
      Hf[j * N + i] = h + (r() - 0.5) * 0.06;
    }
    const cv = document.createElement('canvas'); cv.width = cv.height = N;
    const x = cv.getContext('2d'), img = x.createImageData(N, N), amp = 1.6;
    for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
      const dx = (Hf[j * N + ((i + 1) % N)] - Hf[j * N + ((i + N - 1) % N)]) * amp, dy = (Hf[((j + 1) % N) * N + i] - Hf[((j + N - 1) % N) * N + i]) * amp;
      const l = Math.sqrt(dx * dx + dy * dy + 1), o = (j * N + i) * 4;
      img.data[o] = (-dx / l * 0.5 + 0.5) * 255; img.data[o + 1] = (dy / l * 0.5 + 0.5) * 255; img.data[o + 2] = (1 / l * 0.5 + 0.5) * 255; img.data[o + 3] = 255;
    }
    x.putImageData(img, 0, 0);
    const t = new THREE.CanvasTexture(cv);
    t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8;
    const tile = kind === 'knit' ? 0.012 : kind === 'twill' ? 0.011 : kind === 'denim' ? 0.016 : kind === 'fine' ? 0.006 : 0.009;   // metres per tile, UVs are in metres
    t.repeat.set(1 / tile, 1 / tile);
    NT.set(key, t);
    return t;
  }
  function cloth(kind, color, extra) {
    extra = extra || {};
    color = capAlb(color);
    if (extra.b != null) extra = Object.assign({}, extra, { b: capAlb(extra.b), c: capAlb(extra.c) });
    // the surface pass adds its own creases on top; they were the lumps, so it is asked for about half
    const tame = (m) => { m.userData.txRelief = 0.5; return m; };
    const ns = (wk, s) => ({ normalMap: weaveTex(wk), normalScale: new THREE.Vector2(s, s) });
    // a pale cloth's sheen is its own colour: a white sheen over a white shirt was the blow-out
    const tint = (c, w) => { const C = new THREE.Color(c), L = 0.2126 * C.r + 0.7152 * C.g + 0.0722 * C.b; return C.lerp(new THREE.Color(0xffffff), w * (1 - smooth((L - 0.2) / 0.4))).getHex(); };
    if (kind === 'denim') return tame(K.mat('p-denim', Object.assign({ color: 0xffffff, roughness: 0.9, map: clothTex('denim', color, 0, 0), sheen: 0.3, sheenColor: 0x8899bb, sheenRoughness: 0.8 }, ns('denim', 0.55)), true));
    if (kind === 'plaid') return tame(K.mat('p-plaid', Object.assign({ color: 0xffffff, roughness: 0.88, map: clothTex('plaid', color, extra.b, extra.c), sheen: 0.25, sheenColor: 0xf4efe6, sheenRoughness: 0.8 }, ns('plain', 0.55)), true));
    // worsted wool: dull, a soft sheen in its own colour, never satin (it read as satin at roughness 0.6)
    if (kind === 'suit') return tame(K.mat('p-suit', Object.assign({ color, roughness: 0.74, sheen: 0.35, sheenColor: tint(color, 0.35), sheenRoughness: 0.85 }, ns('fine', 0.45)), true));
    // fluorescent, so a little emissive, never enough to flatten the form (0.12 read as one flat tone, 2026-11-08)
    if (kind === 'hivis') return tame(K.mat('p-hivis', Object.assign({ color, roughness: 0.72, emissive: color, emissiveIntensity: 0.04 }, ns('knit', 0.6))));
    return tame(K.mat('p-cloth', Object.assign({ color, roughness: extra.rough || 0.86, sheen: 0.3, sheenColor: tint(color, 0.5), sheenRoughness: 0.8 },
      ns(extra.weave || (extra.rough ? 'twill' : 'plain'), 0.45)), true));
  }
  /* CLOTH IN ITS OWN SHADOW (2026-11-15, "a white shirt with no folds"). A fold, the inside of an
   * elbow, the gap between the legs and the arm against the side get less sky than the open cloth,
   * and the renderer has no ambient occlusion to say so, so a pale garment printed as one flat tone.
   * The garment's own distance field answers it: a step out along the normal that lands nearer the
   * cloth than the step itself is a step into a hollow. Two steps (7 mm for a fold, 2.4 cm for an arm
   * against the body) give a per-vertex occlusion, written as vertex colour on a copy of the cloth
   * material, so the hems and seams laid over it keep the plain one. */
  function fieldAO(geo, f, k, depth) {
    const P = geo.attributes.position, N = geo.attributes.normal, n = P.count, col = new Float32Array(n * 3), seen = new Map();
    const d1 = 0.007 * k, d2 = 0.024 * k, dp = depth == null ? 0.55 : depth;
    for (let i = 0; i < n; i++) {
      const x = P.getX(i), y = P.getY(i), z = P.getZ(i), key = Math.round(x * 4e4) + ',' + Math.round(y * 4e4) + ',' + Math.round(z * 4e4);
      let v = seen.get(key);
      if (v == null) {
        const nx = N.getX(i), ny = N.getY(i), nz = N.getZ(i);
        const a = clamp01(f(x + nx * d1, y + ny * d1, z + nz * d1) / d1), b = clamp01(f(x + nx * d2, y + ny * d2, z + nz * d2) / d2);
        v = 1 - dp * (1 - Math.pow(0.4 * a + 0.6 * b, 1.3));
        seen.set(key, v);
      }
      col[i * 3] = v; col[i * 3 + 1] = v * 0.99; col[i * 3 + 2] = v * 0.985;
    }
    geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
    return geo;
  }
  const AOM = new WeakMap();
  const aoMat = (m) => {
    if (!AOM.has(m)) { const c = m.clone(); c.vertexColors = true; c.name = m.name; AOM.set(m, c); }
    return AOM.get(m);
  };
  // the inside of a garment, seen through a cuff or a hem: the same cloth in its own shadow
  const clothIn = (m) => K.mat('p-cloth-in', { color: new THREE.Color(m.map ? 0x3a3a3c : m.color).multiplyScalar(m.map ? 0.5 : 0.32).getHex(), roughness: 0.95 });

  /* ---- GARMENT DETAIL ON A FIELD: seams, stitches, hems and cloth pieces with thickness ------
   * A garment's distance field gives every point its surface and its normal, so a detail is laid
   * ON the cloth rather than floated in front of it: a point is walked down the gradient to the
   * zero set and lifted out by the detail's own height. */
  function fGrad(f, x, y, z, e, out) {
    const a = f(x + e, y - e, z - e), b = f(x - e, y - e, z + e), c = f(x - e, y + e, z - e), d = f(x + e, y + e, z + e);
    const gx = a - b - c + d, gy = -a - b + c + d, gz = -a + b - c + d, l = Math.hypot(gx, gy, gz) || 1;
    out[0] = gx / l; out[1] = gy / l; out[2] = gz / l;
    return (a + b + c + d) / 4;
  }
  function onF(f, p, lift, e) {          // [x, y, z, nx, ny, nz] on the surface, `lift` out along its normal
    e = e || 0.0015;
    const g = [0, 0, 1];
    let x = p[0], y = p[1], z = p[2];
    for (let it = 0; it < 5; it++) {
      const d = fGrad(f, x, y, z, e, g), st = Math.max(-0.03, Math.min(0.03, d));
      x -= g[0] * st; y -= g[1] * st; z -= g[2] * st;
      if (Math.abs(d) < 1.5e-4) break;
    }
    fGrad(f, x, y, z, e, g);
    return [x + g[0] * lift, y + g[1] * lift, z + g[2] * lift, g[0], g[1], g[2]];
  }
  // n samples on the surface along a Catmull-Rom curve through guide points near it
  function curveOn(f, guide, n, lift) {
    const c = new THREE.CatmullRomCurve3(guide.map((q) => V3(q[0], q[1], q[2])), false, 'centripetal'), out = [];
    for (let i = 0; i <= n; i++) { const q = c.getPoint(i / n); out.push(onF(f, [q.x, q.y, q.z], lift)); }
    return out;
  }
  const orientOut = (g, nx, ny, nz, vi) => {       // flip a strip's winding so vertex vi faces (nx, ny, nz)
    g.computeVertexNormals();
    const nn = g.attributes.normal;
    if (nn.getX(vi) * nx + nn.getY(vi) * ny + nn.getZ(vi) * nz < 0) {
      const ix = g.index.array; for (let q = 0; q < ix.length; q += 3) { const t = ix[q]; ix[q] = ix[q + 1]; ix[q + 1] = t; }
      g.index.needsUpdate = true; g.computeVertexNormals();
    }
    return g;
  };
  /* A welt across surface samples: a seam's folded allowance stands a millimetre proud and throws
   * a line of light and a line of shadow, which is what reads as a seam at any distance. */
  const WELT = [[-1, -0.6], [-0.55, 0.55], [-0.15, 1], [0.15, 0.85], [0.55, 0.35], [1, -0.6]];
  function weltGeo(S, w, h, prof) {
    prof = prof || WELT;
    const pos = [], uv = [], idx = [], np = prof.length;
    let along = 0;
    for (let i = 0; i < S.length; i++) {
      const a = S[Math.max(0, i - 1)], b = S[Math.min(S.length - 1, i + 1)], s = S[i];
      const tx = b[0] - a[0], ty = b[1] - a[1], tz = b[2] - a[2];
      let bx = ty * s[5] - tz * s[4], by = tz * s[3] - tx * s[5], bz = tx * s[4] - ty * s[3];
      const bl = Math.hypot(bx, by, bz) || 1; bx /= bl; by /= bl; bz /= bl;
      if (i) along += Math.hypot(s[0] - S[i - 1][0], s[1] - S[i - 1][1], s[2] - S[i - 1][2]);
      for (const [u, v] of prof) { pos.push(s[0] + bx * u * w / 2 + s[3] * v * h, s[1] + by * u * w / 2 + s[4] * v * h, s[2] + bz * u * w / 2 + s[5] * v * h); uv.push(u * w / 2, along); }
    }
    for (let i = 0; i < S.length - 1; i++) for (let j = 0; j < np - 1; j++) { const a = i * np + j, b = a + np; idx.push(a, b, a + 1, b, b + 1, a + 1); }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.setIndex(idx);
    const h0 = Math.floor(S.length / 2), m = h0 * np + 2;
    return orientOut(g, S[h0][3], S[h0][4], S[h0][5], m);
  }
  // topstitching: short dashes of thread along surface samples, `off` metres to one side
  function stitchGeo(S, off, pitch, dash, w, h) {
    const pos = [], idx = [], uv = [];
    let acc = 0;
    for (let i = 1; i < S.length; i++) {
      const a = S[i - 1], b = S[i], L = Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]);
      if (L < 1e-6) continue;
      const tx = (b[0] - a[0]) / L, ty = (b[1] - a[1]) / L, tz = (b[2] - a[2]) / L;
      let bx = ty * a[5] - tz * a[4], by = tz * a[3] - tx * a[5], bz = tx * a[4] - ty * a[3];
      const bl = Math.hypot(bx, by, bz) || 1; bx /= bl; by /= bl; bz /= bl;
      for (let t = (pitch - acc) % pitch; t < L; t += pitch) {
        const q = t / L, cx = a[0] + (b[0] - a[0]) * q + bx * off, cy = a[1] + (b[1] - a[1]) * q + by * off, cz = a[2] + (b[2] - a[2]) * q + bz * off;
        const nx = a[3], ny = a[4], nz = a[5], v0 = pos.length / 3;
        for (const [u, s] of [[-0.5, -1], [-0.5, 1], [0.5, -1], [0.5, 1], [0, 0]]) {
          const lift = s === 0 ? h : 0;
          pos.push(cx + tx * u * dash + bx * s * w / 2 + nx * lift, cy + ty * u * dash + by * s * w / 2 + ny * lift, cz + tz * u * dash + bz * s * w / 2 + nz * lift);
          uv.push(u, s);
        }
        // a low tent: four faces round the raised centre, wound to face along the surface normal
        const ux = bx, uy = by, uz = bz, cr = (ty * uz - tz * uy) * nx + (tz * ux - tx * uz) * ny + (tx * uy - ty * ux) * nz;
        if (cr > 0) idx.push(v0, v0 + 2, v0 + 4, v0 + 2, v0 + 3, v0 + 4, v0 + 3, v0 + 1, v0 + 4, v0 + 1, v0, v0 + 4);
        else idx.push(v0, v0 + 4, v0 + 2, v0 + 2, v0 + 4, v0 + 3, v0 + 3, v0 + 4, v0 + 1, v0 + 1, v0 + 4, v0);
      }
      acc = (acc + L) % pitch;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.setIndex(idx);
    g.computeVertexNormals();
    return g;
  }
  /* A piece of cloth laid on a field (a pocket, a flap, a collar point, a lapel, a belt loop):
   * a grid on the surface `lift` out, `th` thick, its edges closed and softened by shared normals,
   * so it has a real edge with a real shadow under it, never a decal. P(u, v) gives guide points
   * near the surface; bulge(u, v) adds to the lift (a flap's roll, a lapel's turn). */
  function slabGeo(f, P, NU, NV, lift, th, o) {
    o = o || {};
    const bot = [], W = NU + 1;
    for (let j = 0; j <= NV; j++) for (let i = 0; i <= NU; i++) bot.push(onF(f, P(i / NU, j / NV), lift + (o.bulge ? o.bulge(i / NU, j / NV) : 0)));
    const pos = [], uv = [], idx = [], n = bot.length;
    const edgeK = (i, j) => (i === 0 || i === NU || j === 0 || j === NV ? 0.55 : 1);     // a soft edge: the top falls toward the rim
    bot.forEach((s, q) => { const i = q % W, j = (q / W) | 0, t = th * edgeK(i, j); pos.push(s[0] + s[3] * t, s[1] + s[4] * t, s[2] + s[5] * t); uv.push(i / NU * (o.w || 0.05), j / NV * (o.h || 0.05)); });
    bot.forEach((s, q) => { const i = q % W, j = (q / W) | 0; pos.push(s[0] - s[3] * 0.0004, s[1] - s[4] * 0.0004, s[2] - s[5] * 0.0004); uv.push(i / NU * (o.w || 0.05), j / NV * (o.h || 0.05)); });
    for (let j = 0; j < NV; j++) for (let i = 0; i < NU; i++) {
      const a = j * W + i, b = a + W;
      idx.push(a, a + 1, b, b, a + 1, b + 1);
      idx.push(n + a, n + b, n + a + 1, n + b, n + b + 1, n + a + 1);
    }
    const ring = [];
    for (let i = 0; i < NU; i++) ring.push(i);
    for (let j = 0; j < NV; j++) ring.push(j * W + NU);
    for (let i = NU; i > 0; i--) ring.push(NV * W + i);
    for (let j = NV; j > 0; j--) ring.push(j * W);
    for (let q = 0; q < ring.length; q++) { const a = ring[q], b = ring[(q + 1) % ring.length]; idx.push(a, n + a, b, b, n + a, n + b); }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.setIndex(idx);
    // the top's winding is decided against the surface normal at its middle; the rest follows from it
    const mid = Math.floor(NV / 2) * W + Math.floor(NU / 2), s = bot[mid];
    g.computeVertexNormals();
    const nn = g.attributes.normal;
    if (nn.getX(mid) * s[3] + nn.getY(mid) * s[4] + nn.getZ(mid) * s[5] < 0) {
      const ix = g.index.array; for (let q = 0; q < ix.length; q += 3) { const t = ix[q]; ix[q] = ix[q + 1]; ix[q + 1] = t; }
      g.computeVertexNormals();
    }
    return g;
  }
  /* A TURNED HEM round a garment's cut edge (a sleeve, a trouser leg, a shirt's hem). A plane cut
   * through a distance field is a solid stump, which is what made a sleeve read as painted on. So
   * the cut keeps a rounded bead in the field, and this lays the hem itself over it: a band whose
   * profile [da, dr] (along the axis out through the cut, out from the cloth) steps out at the
   * stitch line, runs flat and rolls over the lip into the opening, plus a dark cone inside that is
   * the cloth's inner face going up into the sleeve, so the opening has depth.
   * C is a point on the cut plane, A the axis out through it, Nr any direction across it. */
  function hemGeo(f, C, A, Nr, prof, o) {
    o = o || {};
    const NA = o.na || (LOW ? 16 : 44);
    const Ax = A.clone().normalize(), N = Nr.clone().sub(Ax.clone().multiplyScalar(Nr.dot(Ax))).normalize(), B = Ax.clone().cross(N);
    const rsurf = new Float32Array(NA), dirs = [];
    const P = new THREE.Vector3(), D = new THREE.Vector3();
    const radiusAt = (dir, da, r) => {
      for (let it = 0; it < 6; it++) {
        P.copy(C).addScaledVector(Ax, da).addScaledVector(dir, r);
        const d = f(P.x, P.y, P.z); r = Math.max(o.rMin || 0.004, r - d * 0.9);
        if (Math.abs(d) < 1e-4) break;
      }
      return r;
    };
    const daS = -0.0035;
    let guess = 0.05;
    for (let i = 0; i < NA; i++) {
      const th = (i / NA) * Math.PI * 2, dir = N.clone().multiplyScalar(Math.cos(th)).addScaledVector(B, Math.sin(th));
      dirs.push(dir);
      const off = o.off ? o.off(dir) : 0;
      // the first bearing finds the surface by marching out; each later one starts from its neighbour
      if (i === 0) { let r = 0.004; P.copy(C).addScaledVector(Ax, daS + off); while (r < 0.4 && f(P.x + dir.x * r, P.y + dir.y * r, P.z + dir.z * r) < 0) r += 0.004; guess = r; }
      guess = radiusAt(dir, daS + off, guess); rsurf[i] = guess;
    }
    const pos = [], uv = [], idx = [], np = prof.length;
    for (let i = 0; i <= NA; i++) {
      const q = i % NA, dir = dirs[q], off = o.off ? o.off(dir) : 0;
      let rPrev = rsurf[q];
      for (let j = np - 1; j >= 0; j--) {            // from the lip up, so each row starts from the one below it
        const [da, dr] = prof[j];
        const r = da < daS ? (rPrev = radiusAt(dir, da + off, rPrev)) : rsurf[q];
        D.copy(C).addScaledVector(Ax, da + off).addScaledVector(dir, r + dr);
        pos[(i * np + j) * 3] = D.x; pos[(i * np + j) * 3 + 1] = D.y; pos[(i * np + j) * 3 + 2] = D.z;
        uv[(i * np + j) * 2] = (i / NA) * Math.PI * 2 * rsurf[q]; uv[(i * np + j) * 2 + 1] = da;
      }
    }
    for (let i = 0; i < NA; i++) for (let j = 0; j < np - 1; j++) { const a = i * np + j, b = a + np; idx.push(a, b, a + 1, b, b + 1, a + 1); }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.setIndex(idx);
    const d0 = dirs[0], band = orientOut(g, d0.x, d0.y, d0.z, 3);
    if (!o.inside) return { band };
    // the inner face: from just inside the lip up into the garment
    const ip = [], iu = [], ii = [], RW = 3;
    for (let i = 0; i <= NA; i++) {
      const q = i % NA, dir = dirs[q], off = o.off ? o.off(dir) : 0, rs = rsurf[q];
      for (let j = 0; j < RW; j++) {
        const t = j / (RW - 1), da = lerp(prof[np - 1][0] - 0.0002, -o.inside, t), r = lerp(rs + prof[np - 1][1] - 0.0004, rs * 0.72, t);
        D.copy(C).addScaledVector(Ax, da + off).addScaledVector(dir, r);
        ip.push(D.x, D.y, D.z); iu.push(i / NA, t);
      }
    }
    for (let i = 0; i < NA; i++) for (let j = 0; j < RW - 1; j++) { const a = i * RW + j, b = a + RW; ii.push(a, b, a + 1, b, b + 1, a + 1); }
    const gi = new THREE.BufferGeometry();
    gi.setAttribute('position', new THREE.Float32BufferAttribute(ip, 3)); gi.setAttribute('uv', new THREE.Float32BufferAttribute(iu, 2)); gi.setIndex(ii);
    // it faces into the opening: toward the axis
    const inner = orientOut(gi, -d0.x, -d0.y, -d0.z, 1);
    return { band, inner };
  }
  // hem profiles [da, dr] in metres: along the axis out through the cut, out from the cloth
  const HEM = [[-0.027, -0.0009], [-0.023, 0.0007], [-0.0205, 0.0011], [-0.007, 0.0012], [-0.003, 0.001], [-0.0008, 0.0005], [0.0006, -0.0008], [0.0011, -0.0028]];
  const CUFF = [[-0.066, -0.0009], [-0.062, 0.0013], [-0.058, 0.0019], [-0.008, 0.002], [-0.003, 0.0017], [-0.0008, 0.0009], [0.0007, -0.0008], [0.0012, -0.003]];
  const ROLL = [[-0.05, -0.0009], [-0.046, 0.0022], [-0.04, 0.0036], [-0.03, 0.0038], [-0.026, 0.0016], [-0.023, 0.0038], [-0.01, 0.004], [-0.004, 0.0032], [-0.0009, 0.0014], [0.0008, -0.001], [0.0013, -0.0034]];
  const scaleProf = (p, sa, sr) => p.map(([a, b]) => [a * sa, b * (sr || 1)]);

  /* SKIN TAKES LIGHT IN (2026-11-15, "plastic skin"). Skin is translucent: light enters, scatters a
   * few millimetres, red farthest, and leaves, so its terminator is soft and warm where a plastic's
   * is a hard grey line. The physical lighting's Lambert term is replaced, for skin only, by a
   * wrapped one whose wrap is per channel (red most), the standard real-time stand-in for
   * subsurface scattering. Shadows still come from the shadow map, so a shadowed cheek stays in
   * shadow. The specular is skin's own: index 1.4 (F0 about 0.028), a little less than a plastic,
   * and a soft sheen for the down on the skin. Roughness about 0.5, varied by the surface pass. */
  const SSS_KEY = 'reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );';
  const SSS_REP = `{ float txNL = dot( geometryNormal, directLight.direction );
      vec3 txW = vec3( 0.22, 0.11, 0.07 );
      vec3 txL = clamp( ( vec3( txNL ) + txW ) / ( 1.0 + txW ), 0.0, 1.0 );
      reflectedLight.directDiffuse += directLight.color * txL * BRDF_Lambert( material.diffuseColor ); }`;
  function skinMat(key, params) {
    const m = K.mat(key, Object.assign({ roughness: 0.52, ior: 1.4, specularIntensity: 0.62, sheen: 0.18, sheenColor: 0xf0d8cc, sheenRoughness: 0.65 }, params), true);
    if (!m.userData.txSss) {
      m.userData.txSss = true;
      m.onBeforeCompile = (sh) => {
        const ch = THREE.ShaderChunk && THREE.ShaderChunk.lights_physical_pars_fragment;
        if (ch && ch.indexOf(SSS_KEY) >= 0) sh.fragmentShader = sh.fragmentShader.replace('#include <lights_physical_pars_fragment>', ch.replace(SSS_KEY, SSS_REP));
      };
      m.customProgramCacheKey = () => 'tx-skin-sss';
    }
    return m;
  }

  /* ---- palettes ------------------------------------------------------------------------- */
  /* SKIN IS HELD TO MEASURED HUMAN SKIN (weekly pass 2026-10-26). The kit person read as a mannequin
   * on four decks of seven that week (nos. 55, 56, 57, 61), and no. 57's bare forearm measured C* 52.
   * The palette was the cause the 2026-10-22 pass named and left open: its mid tones carried CIELAB a*
   * up to 20, about twice the redness of real skin, so under a warm key every arm rendered as orange
   * plastic. The envelope below is COMPUTED from a published in vivo measurement, never typed: Table 1
   * of "Variation in skin colour by race/ethnicity and body site" (PMC3465481), spectrophotometer
   * readings on the volar forearm and upper inner arm, as [mean, SD] per group. Each palette entry
   * keeps its own lightness, and its a* and b* are clamped into the widest mean +/- 2 SD of any group of
   * thirteen or more people, so the palette spans the measured hue and never leaves it. A deck that
   * passes `skin` as a colour gets that colour, untouched. */
  const SKIN_MEASURED = {        // [L*, a*, b*] as [mean, SD]; the five person biracial group is left out as too small
    asian_volar: [[59.47, 7.33], [8.55, 1.53], [19.60, 2.17]], asian_inner: [[59.30, 8.37], [9.17, 1.56], [19.41, 2.99]],
    black_volar: [[47.26, 7.66], [9.44, 1.12], [20.07, 2.07]], black_inner: [[46.49, 8.07], [9.84, 1.13], [20.13, 2.31]],
    white_volar: [[65.00, 4.45], [7.14, 1.63], [17.37, 2.55]], white_inner: [[65.22, 4.88], [7.67, 1.58], [17.18, 2.96]],
  };
  const SKIN_ENV = (() => {
    const rows = Object.values(SKIN_MEASURED), lo = (i) => Math.min(...rows.map((q) => q[i][0] - 2 * q[i][1])), hi = (i) => Math.max(...rows.map((q) => q[i][0] + 2 * q[i][1]));
    return { a: [lo(1), hi(1)], b: [lo(2), hi(2)] };
  })();
  const LAB = (() => {             // sRGB D65 <-> CIELAB, the standard formulas
    const lin = (c) => (c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)), gam = (c) => (c <= 0.0031308 ? 12.92 * c : 1.055 * Math.pow(c, 1 / 2.4) - 0.055);
    const W = [0.95047, 1, 1.08883], f = (t) => (t > 216 / 24389 ? Math.cbrt(t) : (24389 / 27 * t + 16) / 116), fi = (t) => (t * t * t > 216 / 24389 ? t * t * t : (116 * t - 16) / (24389 / 27));
    const toLab = (hex) => {
      const [r, g, b] = [16, 8, 0].map((k) => lin(((hex >> k) & 255) / 255));
      const X = (0.4124 * r + 0.3576 * g + 0.1805 * b) / W[0], Y = 0.2126 * r + 0.7152 * g + 0.0722 * b, Z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / W[2];
      return [116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z))];
    };
    const toHex = ([L, a, b]) => {
      const fy = (L + 16) / 116, X = W[0] * fi(fy + a / 500), Y = fi(fy), Z = W[2] * fi(fy - b / 200);
      const rgb = [3.2406 * X - 1.5372 * Y - 0.4986 * Z, -0.9689 * X + 1.8758 * Y + 0.0415 * Z, 0.0557 * X - 0.2040 * Y + 1.0570 * Z];
      return rgb.map((c) => Math.round(255 * clamp01(gam(clamp01(c))))).reduce((h, c) => h * 256 + c, 0);
    };
    return { toLab, toHex };
  })();
  /* THE MIDDLE OF THE MEASUREMENT, NOT ITS EDGE (2026-11-15, "orange-brown skin"). The clamp left seven
   * of nine rungs on the envelope's most saturated corner (a* 12.1, b* 24.3, C* 27), two SD above every
   * group's mean, and under the production apricot key that corner printed as orange. Each rung is now
   * drawn halfway from where the clamp put it toward the measured mean of the group nearest its
   * lightness (the darkest rungs toward the darker group's, the lightest toward the lighter's). Both
   * points lie inside the envelope, so the result does too. */
  const skinMean = (L) => {
    const M = (g) => [SKIN_MEASURED[g + '_volar'][1][0] / 2 + SKIN_MEASURED[g + '_inner'][1][0] / 2, SKIN_MEASURED[g + '_volar'][2][0] / 2 + SKIN_MEASURED[g + '_inner'][2][0] / 2];
    const B = M('black'), A = M('asian'), Wt = M('white');
    return L < 53 ? B.map((v, i) => lerp(v, A[i], smooth((L - 40) / 13))) : A.map((v, i) => lerp(v, Wt[i], smooth((L - 53) / 12)));
  };
  const holdSkin = (hex) => {
    const [L, a, b] = LAB.toLab(hex), cl = (v, [p, q]) => Math.min(q, Math.max(p, v)), m = skinMean(L);
    return LAB.toHex([L, lerp(cl(a, SKIN_ENV.a), m[0], 0.5), lerp(cl(b, SKIN_ENV.b), m[1], 0.5)]);
  };
  // the lightness ladder as first drawn, light to deep; the hue of every rung is the measured one above
  const SKIN = [0xf0d0b6, 0xe6b894, 0xd9a47c, 0xc98f64, 0xb37550, 0x9a6040, 0x7d4a2f, 0x5e3522, 0x4a2a1b].map(holdSkin);
  /* HAIR COLOUR AS PEOPLE HAVE IT (2026-11-15, "a white meringue"). One draw in nine was a near
   * white grey (0xc2bdb4, lifted a further 12 percent by the material), so at a deck's scale a light
   * head printed as a pale cap and the seed-1 hero carried it. Real heads run mostly near black to
   * mid brown, some auburn and dark blond, a few fair; grey is one draw in eighteen and is a dark
   * salt and pepper, never white. Same one draw, so no later seeded choice moves. */
  const HAIR = [0x16110e, 0x1b140f, 0x1d1510, 0x221811, 0x281b12, 0x2e2015, 0x34241a, 0x3b2a1c, 0x45301f,
                0x4f3622, 0x5a3d25, 0x623a22, 0x6e4a2c, 0x7a5a38, 0x7f6646, 0x8c7350, 0x121010, 0x6a6560];
  /* NO GARMENT IS PAPER WHITE (2026-11-15). A shirt at 0xf2f0ea is 0.87 linear luminance, and under
   * the production key it printed as flat white with no fold in it. Cloth that reads white is about
   * 0.55 to 0.75 in albedo, and the production key is bright, so any garment colour above 0.62 is scaled down to it, in linear light,
   * keeping its hue. */
  const capAlb = (c, max) => {
    const C = new THREE.Color(c), L = 0.2126 * C.r + 0.7152 * C.g + 0.0722 * C.b, M = max || 0.62;
    return L > M ? C.multiplyScalar(M / L).getHex() : C.getHex();
  };
  const SHIRTS = [0xf2f0ea, 0x9fb7d0, 0x2d3a52, 0x6b7d5c, 0xa2493b, 0x3d5f7a, 0xc9b58f, 0x484848, 0x7a2e2e, 0xe0d7c3, 0x5b6f8f];
  const PLAIDS = [[0x8c2a24, 0x2a2a2a, 0xd8c7a0], [0x2f4a6b, 0x1c2433, 0xc8c2b0], [0x4f6a3a, 0x2a3320, 0xd2c38f], [0x9d6a2f, 0x3b2a1a, 0xe8dcc0]];
  const DENIM = [0x2e4263, 0x3a5680, 0x243552, 0x4d6690, 0x1e2a3c];
  const KHAKI = [0xb9a27c, 0x8f7a5a, 0x5d584d, 0x3f4a3a, 0x6b6257];
  const SUITS = [0x23262d, 0x2e3440, 0x3a3a3c, 0x1c2230, 0x4a4540];

  /* ---- the head: a sphere sculpted into a skull, jaw and face ----------------------------
   * The sphere is sampled densely where the face is (a warped latitude/longitude grid), so the
   * lids, the nose, the philtrum and the lip line exist as geometry at hero distance. */
  const g2 = (dx, dy, sx, sy) => Math.exp(-(dx * dx) / (sx * sx) - (dy * dy) / (sy * sy));
  function headShape(ux, uy, uz, W, Hh, D, fem) {
    let x = Math.sign(ux) * Math.pow(Math.abs(ux), 0.9), y = uy, z = Math.sign(uz) * Math.pow(Math.abs(uz), 0.9);
    // jaw and chin taper, the jaw angle squarer on a man
    if (y < -0.05) { const t = (-0.05 - y) / 0.95; x *= 1 - (fem ? 0.27 : 0.19) * Math.pow(t, fem ? 1.6 : 2.0); }
    // no skull behind the jaw: the neck is there
    if (z < 0 && y < -0.15) z *= 1 - 0.55 * smooth((-y - 0.15) / 0.7);
    // forehead slopes back a little, face plane flattens, temples dip
    if (z > 0) z *= 1 - 0.1 * Math.max(0, y - 0.3) - 0.08 * x * x;
    let px = x * W, py = y * Hh, pz = z * D;
    px -= Math.sign(ux) * W * 0.035 * g2(Math.abs(ux) - 0.85, uy - 0.25, 0.2, 0.18) * smooth(uz / 0.3 + 0.5);
    px += Math.sign(ux) * W * 0.022 * g2(Math.abs(ux) - 0.8, uy + 0.03, 0.14, 0.1) * smooth(uz / 0.3 + 0.6);   // the zygomatic arch
    px += Math.sign(ux) * W * (fem ? 0.012 : 0.026) * g2(Math.abs(ux) - 0.72, uy + 0.62, 0.16, 0.12) * smooth(-uz / 0.3 + 0.8);   // the jaw's angle
    if (uz > -0.1) {
      const fz = smooth((uz + 0.1) / 0.5), ax = Math.abs(ux);
      let dz = 0;
      /* THE FACE'S PLANES AND A LIVING MOUTH (2026-11-15, "dead faces"). The sculpt had a nose, lips
       * and sockets but none of the planes between them, so the face read as one smooth mask: no
       * nasolabial fold, no ala set into the cheek, no philtrum columns, no vermilion edge, a mouth
       * line dead straight. The mouth now curves up a few millimetres at its corners with the cheek
       * apples lifted over them, which is the resting half smile of a person, not a mannequin's line. */
      dz += (fem ? 0.045 : 0.07) * g2(ax, uy - 0.2, 0.55, 0.075) * (ax < 0.62 ? 1 : 0.4);    // brow ridge
      dz += (fem ? 0.01 : 0.022) * g2(ux, uy - 0.17, 0.1, 0.05);                           // glabella
      dz -= 0.02 * g2(ux, uy - 0.1, 0.06, 0.05);                                          // nose root
      dz -= 0.115 * g2(ax - 0.33, uy - 0.06, 0.15, 0.1);                                   // eye sockets
      dz -= 0.012 * g2(ax - 0.3, uy + 0.075, 0.11, 0.025);                                 // the lid's lower edge, the tear trough
      const tn = Math.pow(clamp01((0.08 - uy) / 0.38), 1.3), below = uy < -0.3 ? Math.exp(-Math.pow((uy + 0.3) / 0.075, 2)) : 1;
      dz += (fem ? 0.18 : 0.21) * tn * below * g2(ux, 0, 0.05 + 0.05 * tn, 1);              // bridge to tip
      dz += 0.042 * g2(ux, uy + 0.265, 0.07, 0.06);                                        // the tip's ball
      dz += 0.045 * g2(ax - 0.105, uy + 0.3, 0.045, 0.042);                                 // alae
      dz -= 0.016 * g2(ax - 0.165, uy + 0.3, 0.02, 0.055);                                  // the crease that sets each ala into the cheek
      dz -= 0.014 * g2(ax - 0.05, uy + 0.34, 0.022, 0.018);                                // nostrils
      // the nasolabial fold: from beside the ala down past the mouth's corner, the cheek's mass outside it
      { const x0 = 0.15, y0 = -0.29, x1 = 0.31, y1 = -0.62, vx = x1 - x0, vy = y1 - y0, L2 = vx * vx + vy * vy;
        const t = clamp01(((ax - x0) * vx + (uy - y0) * vy) / L2), qx = ax - x0 - vx * t, qy = uy - y0 - vy * t;
        const dn = Math.hypot(qx, qy) * Math.sign(qx * vy - qy * vx || 1) * -1, win = Math.sin(Math.PI * Math.min(1, t * 1.15 + 0.05));
        dz -= 0.02 * win * Math.exp(-Math.pow(dn / 0.022, 2));
        dz += 0.028 * win * Math.exp(-Math.pow((dn - 0.075) / 0.06, 2)); }
      const mY = (q) => -0.515 + 0.03 * Math.pow(Math.min(1.3, q / 0.22), 2);               // the mouth line, its corners up
      const mo = uy - mY(ax);
      dz -= 0.012 * g2(ux, uy + 0.41, 0.025, 0.04);                                        // philtrum
      dz += 0.009 * g2(ax - 0.04, uy + 0.41, 0.014, 0.045);                                // its two columns
      dz += 0.05 * g2(ux, mo - 0.05, 0.19, 0.035);                                         // upper lip
      dz += 0.01 * g2(ux, mo - 0.074 + 0.008 * g2(ax, 0, 0.05, 1), 0.17, 0.01);            // the vermilion's edge, the bow
      dz -= 0.034 * g2(ux, mo, 0.21, 0.012);                                               // mouth line
      dz += (fem ? 0.05 : 0.042) * g2(ux, mo + 0.045, 0.16, 0.035);                        // lower lip
      dz -= 0.022 * g2(ax - 0.22, mo, 0.035, 0.04);                                        // mouth corners
      dz += 0.012 * g2(ax - 0.28, mo + 0.01, 0.035, 0.05);                                 // the knot of muscle beside each corner
      dz -= 0.025 * g2(ux, uy + 0.655, 0.16, 0.035);                                       // under the lip
      dz += 0.06 * g2(ux, uy + 0.82, 0.3, 0.13);                                           // chin
      dz += 0.045 * g2(ax - 0.55, uy + 0.05, 0.16, 0.12);                                  // cheekbones
      dz += 0.02 * g2(ax - 0.4, uy + 0.22, 0.12, 0.1);                                     // the cheek's apple, lifted by the smile
      dz -= 0.018 * g2(ax - 0.5, uy + 0.35, 0.12, 0.14);                                   // under the cheekbone
      pz += D * dz * fz;
    }
    return [px, py, pz];
  }
  function warp(n, a, b, w) {             // n+1 samples on [a, b] with density w
    const M = 600, cum = [0];
    for (let i = 0; i < M; i++) cum.push(cum[i] + w(a + (b - a) * (i + 0.5) / M));
    const out = [], tot = cum[M];
    let j = 0;
    for (let s = 0; s <= n; s++) {
      const target = tot * s / n;
      while (j < M - 1 && cum[j + 1] < target) j++;
      const t = (target - cum[j]) / ((cum[j + 1] - cum[j]) || 1);
      out.push(a + (b - a) * (j + t) / M);
    }
    return out;
  }
  /* Skin is not one colour: warmer over the cheeks, nose, ears and lips, a little darker in the
   * sockets and, on a man, a faint beard shadow. Multiplied into the face material. */
  function faceTint(ux, uy, uz, fem) {
    const ax = Math.abs(ux), f = smooth((uz + 0.1) / 0.5);
    let r = 1, g = 1, b = 1;
    /* MORE LIFE IN THE TINT (2026-11-15, "flat orange-brown"). The face read as one colour at a deck's
     * scale, so the blood is a little stronger where it shows (the cheeks, the nose, the ear side), the
     * forehead and the chin a touch paler and yellower, and the form is shaded where light is kept
     * off it: the band under the brow over the upper lid, and the underside of the jaw. All of it is a
     * multiplier on the measured palette, so the skin's hue stays where the measurement put it. */
    const warm = 0.2 * g2(ax - 0.45, uy + 0.2, 0.2, 0.17) + 0.15 * g2(ux, uy + 0.22, 0.08, 0.12) + 0.04 * g2(ux, uy - 0.35, 0.3, 0.15);
    g -= warm * 0.85 * f; b -= warm * 1.05 * f; r -= warm * 0.12 * f;
    const pale = 0.04 * (g2(ux, uy - 0.5, 0.35, 0.18) + g2(ux, uy + 0.8, 0.18, 0.1)) * f;
    b -= pale * 0.5;
    const sock = 0.13 * g2(ax - 0.33, uy - 0.08, 0.14, 0.08) * f + 0.09 * g2(ax - 0.33, uy - 0.15, 0.2, 0.05) * f;
    r -= sock * 0.85; g -= sock; b -= sock * 0.85;
    const jaw = 0.16 * smooth((-uy - 0.68) / 0.2) * smooth((uz + 0.2) / 0.4) * (1 - smooth((-uy - 0.9) / 0.08));
    r -= jaw * 0.85; g -= jaw; b -= jaw * 0.9;
    // the thin skin under the eye is a little cooler and darker; the nose tip and the ear-side of the cheek warmer
    const under = 0.05 * g2(ax - 0.3, uy + 0.06, 0.12, 0.05) * f;
    r -= under * 0.7; g -= under; b -= under * 0.6;
    const flush = 0.07 * g2(ux, uy + 0.27, 0.06, 0.06) * f + 0.06 * g2(ax - 0.75, uy + 0.15, 0.15, 0.2);
    g -= flush * 0.8; b -= flush * 0.9;
    if (!fem) { const beard = 0.08 * smooth((-uy - 0.35) / 0.2) * smooth((uz + 0.35) / 0.3) * (1 - 0.8 * g2(ux, uy + 0.52, 0.2, 0.06)); r -= beard; g -= beard; b -= beard * 0.8; }
    const fade = smooth((uy + 0.95) / 0.2);               // back to exactly the body skin at the neck
    return [lerp(1, r, fade), lerp(1, g, fade), lerp(1, b, fade)];
  }
  const HEADS = new Map();
  function headGeo(W, Hh, D, fem) {
    const key = [W, Hh, D, fem, LOW].map((v) => (typeof v === 'number' ? v.toFixed(4) : v)).join('|');
    if (HEADS.has(key)) return HEADS.get(key);
    // fine enough at the face that a lip's edge, a nostril and the fold beside the mouth are geometry
    const NLON = LOW ? 24 : 104, NLAT = LOW ? 18 : 88;
    const lon = warp(NLON, -Math.PI, Math.PI, (a) => 1 + 1.7 * Math.exp(-Math.pow(a / 0.85, 2)));
    const lat = warp(NLAT, 0, Math.PI, (t) => 1 + 1.5 * Math.exp(-Math.pow((t - 1.75) / 0.5, 2)) + 0.9 * Math.exp(-Math.pow((t - 1.05) / 0.28, 2)));
    const pos = [], uv = [], dirs = [], idx = [], col = [];
    for (let i = 0; i <= NLAT; i++) for (let j = 0; j <= NLON; j++) {
      const th = lat[i], ph = lon[j];
      const ux = Math.sin(th) * Math.sin(ph), uy = Math.cos(th), uz = Math.sin(th) * Math.cos(ph);
      pos.push(...headShape(ux, uy, uz, W, Hh, D, fem)); dirs.push(ux, uy, uz); uv.push(j / NLON, i / NLAT); col.push(...faceTint(ux, uy, uz, fem));
    }
    const Wd = NLON + 1;
    for (let i = 0; i < NLAT; i++) for (let j = 0; j < NLON; j++) {
      const a = i * Wd + j, b = a + Wd;
      if (i > 0) idx.push(a, b, a + 1);
      if (i < NLAT - 1) idx.push(b, b + 1, a + 1);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
    g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
    g.setIndex(idx);
    g.computeVertexNormals();
    const nor = g.attributes.normal;
    for (let i = 0; i <= NLAT; i++) {           // weld the seam at the back
      const a = i * Wd, b = a + NLON;
      const nx = nor.getX(a) + nor.getX(b), ny = nor.getY(a) + nor.getY(b), nz = nor.getZ(a) + nor.getZ(b), l = Math.hypot(nx, ny, nz) || 1;
      nor.setXYZ(a, nx / l, ny / l, nz / l); nor.setXYZ(b, nx / l, ny / l, nz / l);
    }
    /* CAVITY (2026-11-15): skin is darker where it folds in, the nostril, the mouth's line and corners,
     * the fold beside the nose, the lid's crease, because less light reaches in and what does is
     * scattered red. The concavity of each vertex against its grid neighbours two steps out darkens
     * its tint, and a convexity lifts it a little, so the face's planes read without a light on them. */
    if (!LOW) {
      const pa = g.attributes.position, ca = g.attributes.color, cav = new Float32Array(pa.count);
      for (let i = 2; i < NLAT - 1; i++) for (let j = 0; j <= NLON; j++) {
        const v = i * Wd + j, jj = (q) => ((q % NLON) + NLON) % NLON;
        const nb = [(i - 2) * Wd + j, (i + 2) * Wd + j, i * Wd + jj(j - 2), i * Wd + jj(j + 2)];
        let mx = 0, my = 0, mz = 0, el = 0;
        for (const q of nb) { mx += pa.getX(q); my += pa.getY(q); mz += pa.getZ(q); el += Math.hypot(pa.getX(q) - pa.getX(v), pa.getY(q) - pa.getY(v), pa.getZ(q) - pa.getZ(v)); }
        mx = mx / 4 - pa.getX(v); my = my / 4 - pa.getY(v); mz = mz / 4 - pa.getZ(v); el /= 4;
        cav[v] = (mx * nor.getX(v) + my * nor.getY(v) + mz * nor.getZ(v)) / (el * el + 1e-9) * 0.004;
      }
      for (let v = 0; v < pa.count; v++) {
        const c = Math.max(-0.06, Math.min(0.3, cav[v] * 1.5)), fr = smooth((dirs[v * 3 + 2] + 0.2) / 0.5);
        const dk = c > 0 ? c * fr : c * 0.5 * fr;
        ca.setXYZ(v, ca.getX(v) * (1 - dk * 0.8), ca.getY(v) * (1 - dk), ca.getZ(v) * (1 - dk * 0.95));
      }
    }
    g.userData.dirs = dirs;
    HEADS.set(key, g);
    return g;
  }
  /* A shell grown off the head along its normals by thickness T(ux, uy, uz) metres. Where T is
   * negative the shell sinks under the skin, so a hairline or a beard edge tapers rather than
   * ending in a step; triangles entirely under the skin are dropped. */
  function shellGeo(head, T, tone) {
    const p = head.attributes.position, n = head.attributes.normal, dirs = head.userData.dirs, idx = head.index.array;
    const cnt = p.count, out = new Float32Array(cnt * 3), th = new Float32Array(cnt), col = new Float32Array(cnt * 3);
    tone = tone || T.tone;
    for (let i = 0; i < cnt; i++) {
      const t = T(dirs[i * 3], dirs[i * 3 + 1], dirs[i * 3 + 2]);
      th[i] = t;
      // where the hair is thin (a hairline, a parting, a crease between locks) the eye sees down to
      // the darker roots; where it stands thick it shows its lit outer layer
      const v = (tone ? tone(dirs[i * 3], dirs[i * 3 + 1], dirs[i * 3 + 2]) : 1) * (0.68 + 0.32 * smooth(t / 0.0055));
      col[i * 3] = v; col[i * 3 + 1] = v * 0.985; col[i * 3 + 2] = v * 0.97;
      const tt = Math.max(t, -0.0015);
      out[i * 3] = p.getX(i) + n.getX(i) * tt; out[i * 3 + 1] = p.getY(i) + n.getY(i) * tt; out[i * 3 + 2] = p.getZ(i) + n.getZ(i) * tt;
    }
    const keep = [];
    for (let i = 0; i < idx.length; i += 3) if (th[idx[i]] > 0 || th[idx[i + 1]] > 0 || th[idx[i + 2]] > 0) keep.push(idx[i], idx[i + 1], idx[i + 2]);
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(out, 3));
    g.setAttribute('uv', head.attributes.uv.clone());
    g.setAttribute('color', new THREE.BufferAttribute(col, 3));
    g.setIndex(keep);
    g.computeVertexNormals();
    return g;
  }
  /* Hair styles as thickness over the scalp. The hairline is a table over the azimuth from the
   * face (0) to the nape (pi): forehead, temples, sideburn, over the ear, the nape. */
  const LINES = {
    short: [[0, 0.6], [0.45, 0.53], [0.8, 0.34], [1.0, 0.05], [1.15, -0.14], [1.3, -0.12], [1.42, 0.12], [1.75, 0.14], [2.1, -0.2], [2.5, -0.45], [3.2, -0.5]],
    long:  [[0, 0.58], [0.45, 0.5], [0.8, 0.32], [0.95, -0.2], [1.1, -0.75], [1.4, -0.95], [3.2, -0.95]],
    recede:[[0, 0.72], [0.3, 0.7], [0.6, 0.55], [0.9, 0.2], [1.15, -0.12], [1.3, -0.12], [1.42, 0.12], [1.75, 0.14], [2.1, -0.2], [2.5, -0.45], [3.2, -0.5]],
  };
  const lineAt = (tab, a) => {
    let i = 1; while (i < tab.length - 1 && tab[i][0] < a) i++;
    const t = smooth((a - tab[i - 1][0]) / (tab[i][0] - tab[i - 1][0]));
    return lerp(tab[i - 1][1], tab[i][1], t);
  };
  function hairThickness(style, k, ph) {
    const tab = style === 'long' || style === 'bob' || style === 'curlyLong' ? LINES.long : style === 'recede' ? LINES.recede : LINES.short;
    /* LOCKS AND A BROKEN HAIRLINE (weekly pass 2026-10-16). The shell was a smooth cap of even
     * thickness with one parting groove, and its hairline was one clean curve, so at full size it
     * read as a helmet or a pale block on nos. 48, 49 and 52, and the 2026-10-15 pass measured that
     * the hair MATERIAL was not the cause. Hair lies in locks that fan out from the crown whorl, and
     * a hairline is a scallop of lock ends rather than a line. So the thickness carries ridges
     * around the crown axis (12 locks, creased between, faded to nothing at the whorl so they
     * meet without a pinch) and the hairline is pushed in and out by two lock-scale waves. A
     * buzz, a tight crop and a bun are slicked or clipped and take a little of each. */
    /* CLUMPED, NOT RIDGED (2026-11-15, "a white meringue"). The lock profile was 1 - 2(1 - |sin|)^2,
     * which has a cusp at every crease, at a third of the hair's thickness, so twelve identical sharp
     * ridges ran from the crown and printed as piped meringue or a hairnet. The profile is now a smooth
     * roll (-cos), half as deep, and each lock is its own: its depth and its lightness are hashed from
     * its index, so one clump stands proud and lighter, its neighbour sits lower and darker. */
    const relief = { buzz: 0.06, tight: 0.08, bun: 0.1, recede: 0.12, curly: 0, curlyLong: 0 }[style];
    const lockAmp = relief == null ? 0.1 : relief;
    const lineAmp = style === 'buzz' || style === 'tight' ? 0.012 : 0.028;
    const hsh = (q) => { const v = Math.sin(q * 12.9898 + ph * 7.13) * 43758.5453; return v - Math.floor(v); };
    const lockAt = (ux, uy, uz) => {
      const cd = Math.acos(Math.max(-1, Math.min(1, 0.82 * uy - 0.57 * uz)));              // angle from the crown whorl
      const la = 6 * Math.atan2(-0.57 * uy - 0.82 * uz, ux) + 0.7 * Math.sin(cd * 4 + ph) + ph;
      const id = Math.floor(la / Math.PI + 0.5), h = hsh(id + 40), h2 = hsh(id + 91);
      return { cd, lk: -Math.cos(2 * la), h, h2 };
    };
    const curls = style === 'curly' || style === 'curlyLong';
    const fn = (ux, uy, uz) => {
      const az = Math.abs(Math.atan2(ux, uz));
      const m = uy - lineAt(tab, az) + lineAmp * (0.6 * Math.sin(az * 19 + ph) + 0.4 * Math.sin(az * 41 + 2 * ph));   // > 0 inside the hair
      const { cd, lk, h } = lockAt(ux, uy, uz);
      const lockK = 1 + lockAmp * (0.45 + 0.85 * h) * lk * smooth(cd / 0.35);
      const top = smooth((uy - 0.35) / 0.55) * (1 - 0.35 * smooth((Math.abs(ux) - 0.5) / 0.4)), front = smooth(uz / 0.6) * smooth((uy - 0.35) / 0.35), crown = smooth((uy + 0.2) / 0.7);
      let T;
      switch (style) {
        case 'buzz': T = 0.0032; break;
        case 'tight': T = 0.004 + 0.002 * top; break;
        case 'side': T = 0.0045 + 0.004 * crown + 0.016 * top + 0.007 * front - 0.007 * g2(ux - 0.4, uy - 0.62, 0.045, 0.4) * smooth(uz / 0.3 + 0.3) + 0.004 * top * smooth(-ux / 0.4); break;
        case 'curly': T = 0.006 + 0.005 * crown + 0.016 * top + 0.003 * (Math.sin(ux * 31 + ph) * Math.sin(uy * 29 + ph * 2) + Math.sin(uz * 27 + uy * 13 + ph * 3)); break;
        case 'recede': T = 0.004 + 0.004 * top; break;
        case 'bun': T = 0.004 + 0.004 * top; break;
        case 'long': case 'bob': T = 0.007 + 0.004 * crown + 0.01 * top + 0.004 * front; break;
        case 'curlyLong': T = 0.012 + 0.016 * top + 0.004 * (Math.sin(ux * 27 + ph) * Math.sin(uy * 25 + ph * 2) + Math.sin(uz * 23 + ph * 3)); break;
        default: T = 0.004 + 0.004 * crown + 0.0095 * top + 0.0055 * front;      // crop
      }
      T *= k * lockK;
      // a continuous taper through the hairline, so the edge is cut by interpolation, not by the grid
      if (m < -0.06) return -0.002;
      return lerp(-0.002, T + 0.0003 * Math.sin(ux * 90 + uy * 40 + ph), smooth((m + 0.02) / (uz > 0.3 ? 0.22 : 0.12)));
    };
    // the hair's value: each lock a little lighter or darker than the next, darker down in its creases
    // and at the whorl, a little lighter where the top catches the sky
    fn.tone = (ux, uy, uz) => {
      if (curls) return 0.84 + 0.16 * (0.5 + 0.5 * Math.sin(ux * 37 + ph) * Math.sin(uy * 33 + uz * 21 + ph * 2));
      const { cd, lk, h2 } = lockAt(ux, uy, uz), on = smooth(cd / 0.35);
      return (0.9 + 0.16 * h2 * on) * (1 - 0.1 * on * (0.5 - 0.5 * lk)) * (0.9 + 0.1 * smooth(cd / 0.25));
    };
    return fn;
  }
  /* Hair that falls below the skull: a thick curved slab around the back and sides of the
   * head, open at the face, its lower edge layered. Rows run down, columns around.
   * HANG (weekly pass 2026-10-03): the curtain is built in the head's frame, so a head bowed
   * to read swung its lower edge out behind the neck as a rigid plate, which no. 38's judges
   * named as "a spike of hair mesh" and "a hair clump detached behind the parent's neck".
   * `hang` is the head's pitch against the neck (the torso's lean tilts the neck too, so it is
   * left out), and `piv` is the top of the neck in the head's frame, the point the head turns
   * about. The hair below the skull is turned back by `hang` about that point, progressively from
   * the crown down, so it falls along the neck as it does when the head is upright, rather than
   * through the neck (turned about the head's centre it cut 2 cm into it) or out behind it. */
  function curtainGeo(W, Hh, D, k, len, curly, ph, hang, piv) {
    const NU = LOW ? 14 : 44, NV = LOW ? 6 : 22, th = (curly ? 0.034 : 0.024) * k;
    const yTop = 0.05 * Hh, pos = [], uv = [], idx = [], col = [];
    const a0 = 1.4, a1 = Math.PI * 2 - 1.4;                      // around the back
    const R = (a, y, s) => {                                      // outer radius factor
      const fl = smooth((-y) / (Hh * 1.2));
      // straight hair hangs in locks too (2026-10-16): a smooth curtain read as a rigid plate behind
      // the neck, so the outer face is creased into clumps that open toward the ends
      const lock = curly ? 0 : 0.05 * (0.4 + 0.6 * fl) * (1 - 2 * Math.pow(1 - Math.abs(Math.sin(a * 7 + 0.8 * Math.sin(y * 18 + ph) + ph)), 2));
      return 1.05 + 0.1 * fl + (curly ? 0.1 : 0) * fl + lock + s * 0.012 * Math.sin(a * 23 + ph) + (curly ? 0.04 * Math.sin(a * 11 + y * 60 + ph) : 0);
    };
    const bot = (a) => -len * Hh + 0.035 * k * Math.sin(a * 5 + ph) + 0.02 * k * Math.sin(a * 13 + ph * 2) - 0.04 * k * Math.cos(a - Math.PI) * (len > 1.3 ? 1 : 0);
    const put = (a, y, inner, v) => {
      const edge = smooth((a - a0) / 0.5) * smooth((a1 - a) / 0.5);
      const tt = th * (0.55 + 0.45 * edge) * (1 - 0.45 * v);
      const rr = R(a, y, 1) - (1 - edge) * 0.03 - (inner ? tt / (W * 1.1) : 0);
      const x = Math.sin(a) * W * rr; let z = Math.cos(a) * D * rr * 0.97 - 0.1 * D * smooth(-y / Hh), yy = y;
      if (hang) {
        const ang = -hang * smooth((yTop - y) / (Hh * 0.9)), c = Math.cos(ang), sn = Math.sin(ang);
        const py = piv ? piv[0] : yTop, pz = piv ? piv[1] : 0, dy = y - py, dz = z - pz;
        yy = py + dy * c - dz * sn; z = pz + dy * sn + dz * c;
      }
      pos.push(x, yy, z); uv.push(a / (Math.PI * 2), -y / 0.25);
      // value: darker at the root and on the inside, each hanging lock its own shade, creases darker
      const lockV = curly ? 0.88 + 0.12 * Math.sin(a * 11 + y * 60 + ph) : 0.8 + 0.2 * Math.sqrt(Math.abs(Math.sin(a * 7 + 0.8 * Math.sin(y * 18 + ph) + ph)));
      const per = 0.9 + 0.12 * Math.sin(Math.floor((a * 7 + ph) / Math.PI) * 2.7 + ph);
      const c = lockV * per * (inner ? 0.62 : 1) * lerp(0.82, 1.04, smooth(v * 1.6));
      col.push(c, c * 0.985, c * 0.97);
    };
    for (let side = 0; side < 2; side++)
      for (let v = 0; v <= NV; v++) for (let u = 0; u <= NU; u++) {
        const a = lerp(a0, a1, u / NU), y = lerp(yTop, bot(a), v / NV);
        put(a, y, side === 1, v / NV);
      }
    const Wd = NU + 1, off = (NV + 1) * Wd;
    for (let v = 0; v < NV; v++) for (let u = 0; u < NU; u++) {
      const a = v * Wd + u, b = a + Wd;
      idx.push(a, a + 1, b, b, a + 1, b + 1);                     // outer, facing out
      idx.push(off + a, off + b, off + a + 1, off + b, off + b + 1, off + a + 1);
    }
    for (let u = 0; u < NU; u++) {                                 // the bottom edge closed
      const a = NV * Wd + u;
      idx.push(a, off + a, a + 1, a + 1, off + a, off + a + 1);
    }
    for (const u of [0, NU]) for (let v = 0; v < NV; v++) {       // the two front edges
      const a = v * Wd + u, b = a + Wd;
      if (u === 0) idx.push(a, b, off + a, b, off + b, off + a); else idx.push(a, off + a, b, b, off + a, off + b);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
    g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
    g.setIndex(idx);
    g.computeVertexNormals();
    return g;
  }

  /* ---- hands -------------------------------------------------------------------------- */
  // Built hanging down -y with the palm facing -s*x (toward the body) and the thumb to +z.
  /* A RELAXED HAND, NOT A RAKE (2026-11-15). The fingers were four thin tapered sticks curled by
   * different amounts, so from three quarters they fanned out like a claw, and the palm was a flat
   * paddle. A hand at rest: the knuckles sit on an arc (the middle lowest, the little finger well up),
   * each finger bends a little at the knuckle and more at the middle joint, the bend growing toward
   * the little finger, the fingers lean in toward the middle and touch, every joint is a slight
   * swelling with the bone thinner between, each tip carries a nail, the thumb springs from a
   * fleshy mound and rests along the side of the index finger, and the back of the hand shows its
   * knuckles. */
  function hand(k, s, mat, pose, nailM) {
    const g = new THREE.Group();
    const L = 0.1 * k, B = 0.084 * k, T = 0.03 * k;
    const palm = loft([
      { p: [0, 0.012 * k, 0], rx: T * 0.44, ry: B * 0.34 },
      { p: [0, -0.03 * k, 0.002 * k], rx: T * 0.6, ry: B * 0.47 },
      { p: [-s * 0.003 * k, -0.07 * k, 0], rx: T * 0.54, ry: B * 0.5 },
      { p: [-s * 0.005 * k, -L + 0.006 * k, 0], rx: T * 0.44, ry: B * 0.48 }], { seg: LOW ? 10 : 18, per: 3, n: 2.4, ref: [1, 0, 0], capStart: 'flat', capEnd: 'dome', domeK: 0.5 });
    g.add(new THREE.Mesh(palm, mat));
    if (LOW) {      // a mitten: the fingers as one curled blade
      g.add(new THREE.Mesh(loft([{ p: [0, -L + 0.01 * k, 0], rx: T * 0.38, ry: B * 0.45 }, { p: [-s * 0.022 * k, -L - 0.055 * k, 0], rx: T * 0.3, ry: B * 0.4 }],
        { seg: 12, capEnd: 'dome', ref: [1, 0, 0] }), mat));
    } else {
      // the mounds of the palm: the thumb's at the heel on the thumb side, the little finger's along the other edge
      const blob = (p, sc, rot) => { const m = new THREE.Mesh(new THREE.SphereGeometry(1, 14, 10), mat); m.position.set(...p.map((v) => v * k)); m.scale.set(...sc.map((v) => v * k)); if (rot) m.rotation.set(...rot); g.add(m); };
      blob([-s * 0.007, -0.035, 0.02], [0.012, 0.03, 0.016], [0, 0, s * 0.25]);
      blob([-s * 0.006, -0.055, -0.026], [0.009, 0.034, 0.011]);
    }
    const fl = [0.074, 0.084, 0.079, 0.064], kn = [0.005, 0, 0.003, 0.013];
    const wr = [0.0104, 0.0108, 0.0102, 0.0091];
    const CURL = pose === 'point' ? [[0.03, 0.06, 0.03], [0.95, 1.5, 0.85], [1, 1.55, 0.85], [1.05, 1.55, 0.85]]
      : pose === 'fist' ? [[1.15, 1.55, 0.9], [1.2, 1.6, 0.9], [1.2, 1.6, 0.9], [1.2, 1.55, 0.9]]
      : [[0.2, 0.4, 0.22], [0.27, 0.5, 0.26], [0.33, 0.57, 0.28], [0.4, 0.64, 0.3]];
    const segs = [0.46, 0.3, 0.24];
    for (let f = 0; f < (LOW ? 0 : 4); f++) {
      const z0 = (0.0285 - f * 0.019) * k, len = fl[f] * k, rad = wr[f] * k, c = CURL[f];
      // the fingers lean in toward the middle as they go, so neighbours touch rather than fan
      const zTip = z0 * 0.84 + (f === 0 ? -0.001 : f === 3 ? 0.002 : 0) * k;
      let px = -s * 0.005 * k, py = -L + kn[f] * k, a = 0.06, run = 0;
      const ctrl = [{ p: [px, py + 0.012 * k, z0], rx: rad * 1.02, ry: rad * 0.9 }];
      const put = (r) => { const t = run / len; ctrl.push({ p: [px, py, lerp(z0, zTip, t)], rx: rad * r, ry: rad * r * 0.88 }); };
      put(1.05);                                                    // the knuckle
      let tipDir = null;
      for (let j = 0; j < 3; j++) {
        a += c[j];
        const seg = len * segs[j], half = seg * 0.5;
        const step = (d) => { py -= Math.cos(a) * d; px += -s * Math.sin(a) * d; run += d; };
        step(half); put([0.93, 0.85, 0.8][j]);                      // the bone, thinner
        step(half); put([0.95, 0.84, 0.66][j]);                     // the next joint swells; the last ring rounds the tip
        if (j === 2) tipDir = a;
      }
      g.add(new THREE.Mesh(loft(ctrl, { seg: 9, per: 2, capStart: 'flat', capEnd: 'dome', domeK: 0.75, ref: [0, 0, 1] }), mat));
      // the index tip, read off the finger's own last ring and its dome, so a press can be measured
      if (f === 0) { const e = ctrl[ctrl.length - 1], cap = e.rx * 0.75; g.userData.tip = V3(e.p[0] - s * Math.sin(tipDir) * cap, e.p[1] - Math.cos(tipDir) * cap, e.p[2]); }
      // the nail, on the back of the last bone
      if (nailM) {
        const nl = new THREE.Mesh(new THREE.SphereGeometry(1, 12, 8), nailM);
        const back = s, d = V3(-s * Math.sin(tipDir), -Math.cos(tipDir), 0), up = V3(back * Math.cos(tipDir), -Math.sin(tipDir), 0);
        const cp = ctrl[ctrl.length - 2].p, rr = rad * 0.8 * 0.86;
        nl.position.set(cp[0] + up.x * rr * 0.86 + d.x * 0.002 * k, cp[1] + up.y * rr * 0.86 + d.y * 0.002 * k, cp[2]);
        nl.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(V3(0, 0, 1), d, up));
        nl.scale.set(rad * 0.62, len * 0.12, 0.0016 * k); g.add(nl);
      }
      // the knuckle on the back of the hand
      const kb = new THREE.Mesh(new THREE.SphereGeometry(1, 10, 8), mat);
      kb.position.set(s * 0.008 * k, -L + kn[f] * k + 0.004 * k, z0 * 0.95); kb.scale.set(0.0052 * k, 0.0085 * k, rad * 0.8); g.add(kb);
    }
    // the thumb from its mound, forward and down, resting along the side of the index finger
    const th = [[-s * 0.005, -0.016, 0.024], [-s * 0.012, -0.04, 0.045], [-s * 0.019, -0.062, 0.054], [-s * 0.026, -0.075, 0.056], [-s * 0.032, -0.087, 0.054]]
      .map((q, i) => ({ p: q.map((v) => v * k), rx: [0.0135, 0.0118, 0.0112, 0.0102, 0.0094][i] * k, ry: [0.0115, 0.0102, 0.0098, 0.0086, 0.0078][i] * k }));
    if (pose === 'point' || pose === 'fist') th.forEach((t, i) => { t.p[0] -= s * 0.012 * k * i / 1.3; t.p[2] -= 0.008 * k * i / 1.3; });
    g.add(new THREE.Mesh(loft(th, { seg: LOW ? 6 : 10, per: 2, capStart: 'flat', capEnd: 'dome', domeK: 0.75 }), mat));
    if (nailM && !LOW) {
      const a = th[3].p, b = th[4].p, d = V3(b[0] - a[0], b[1] - a[1], b[2] - a[2]).normalize();
      const up = V3(s * 0.25, 0, 1).sub(d.clone().multiplyScalar(d.z)).normalize(), sd = d.clone().cross(up).normalize();
      const nl = new THREE.Mesh(new THREE.SphereGeometry(1, 12, 8), nailM);
      nl.position.set(b[0] + up.x * 0.0072 * k - d.x * 0.002 * k, b[1] + up.y * 0.0072 * k - d.y * 0.002 * k, b[2] + up.z * 0.0072 * k - d.z * 0.002 * k);
      nl.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(sd, d, up));
      nl.scale.set(0.0066 * k, 0.0085 * k, 0.0016 * k); g.add(nl);
    }
    return g;
  }

  /* THE INDEX TIP OF A 'point' HAND, in the hand's own frame, without building it (weekly pass
   * 2026-11-24). The same walk as the finger loop above for f = 0, so a press can aim the wrist
   * BEFORE the hand exists. The built hand records its own tip in userData.tip, and the person
   * publishes the distance between the two worlds as attach.hands[i].short, so a drift between
   * this walk and the loop shows up as a number rather than a finger in the air. */
  function indexTip(k, s) {
    const L = 0.1 * k, len = 0.074 * k, rad = 0.0104 * k, c = [0.03, 0.06, 0.03], segs = [0.46, 0.3, 0.24];
    const zTip = 0.0285 * k * 0.84 - 0.001 * k;
    let px = -s * 0.005 * k, py = -L + 0.005 * k, a = 0.06;
    for (let j = 0; j < 3; j++) { a += c[j]; const d = len * segs[j]; py -= Math.cos(a) * d; px += -s * Math.sin(a) * d; }
    const cap = rad * 0.66 * 0.75;
    return V3(px - s * Math.sin(a) * cap, py - Math.cos(a) * cap, zTip);
  }
  /* the turn that hangs a hand down its forearm Fd with its palm toward `palm` (both in the person's frame) */
  function handQuat(Fd, s, palm) {
    const q = new THREE.Quaternion().setFromUnitVectors(V3(0, -1, 0), Fd);
    const cur = V3(-s, 0, 0).applyQuaternion(q), want = palm.clone();
    cur.sub(Fd.clone().multiplyScalar(cur.dot(Fd))).normalize(); want.sub(Fd.clone().multiplyScalar(want.dot(Fd))).normalize();
    return q.premultiply(new THREE.Quaternion().setFromAxisAngle(Fd, Math.atan2(cur.clone().cross(want).dot(Fd), cur.dot(want))));
  }

  /* ---- shoes --------------------------------------------------------------------------
   * A last-shaped upper (heel counter, instep, vamp, toe box) standing on a sole with real
   * thickness, toe spring and, for heeled styles, a heel block; laces over a tongue. Local
   * frame: ground at y = 0, toe toward +z, the ankle above z = 0. */
  function shoe(k, style, upper, sole, lace) {
    const g = new THREE.Group();
    const western = style === 'western', dress = style === 'dress', sneaker = style === 'sneaker', work = style === 'work', boot = style === 'boot';
    const L = (western ? 0.29 : 0.278) * k, z0 = -0.062 * k, z1 = z0 + L;
    const soleT = (sneaker ? 0.03 : work ? 0.026 : boot ? 0.022 : 0.013) * k;
    const heelH = (western ? 0.036 : dress ? 0.014 : work || boot ? 0.006 : 0) * k;
    const zBall = z0 + L * 0.72;
    const toeN = western ? 0.55 : dress ? 0.8 : 1;
    const WT = [[0, 0.012], [0.03, 0.026], [0.1, 0.033], [0.3, 0.033], [0.5, 0.038], [0.7, 0.046], [0.82, 0.045], [0.91, 0.039 * toeN + 0.004], [0.965, 0.028 * toeN], [0.992, 0.014 * toeN], [1, 0.002]];
    const wAt = (t) => { let i = 1; while (i < WT.length - 1 && WT[i][0] < t) i++; const u = (t - WT[i - 1][0]) / (WT[i][0] - WT[i - 1][0]); return lerp(WT[i - 1][1], WT[i][1], smooth(u)) * k; };
    const HT = sneaker ? [[0, 0.07], [0.15, 0.078], [0.33, 0.09], [0.5, 0.078], [0.64, 0.062], [0.78, 0.052], [0.9, 0.046], [1, 0.036]]
      : dress ? [[0, 0.064], [0.15, 0.07], [0.33, 0.08], [0.5, 0.068], [0.64, 0.054], [0.78, 0.044], [0.9, 0.036], [1, 0.028]]
      : western ? [[0, 0.07], [0.15, 0.08], [0.33, 0.088], [0.5, 0.074], [0.64, 0.058], [0.78, 0.045], [0.9, 0.035], [1, 0.026]]
      : [[0, 0.074], [0.15, 0.082], [0.33, 0.094], [0.5, 0.082], [0.64, 0.066], [0.78, 0.056], [0.9, 0.05], [1, 0.04]];
    const hAt = (t) => { let i = 1; while (i < HT.length - 1 && HT[i][0] < t) i++; const u = (t - HT[i - 1][0]) / (HT[i][0] - HT[i - 1][0]); return lerp(HT[i - 1][1], HT[i][1], smooth(u)) * k; };
    const bend = (geo) => {
      const p = geo.attributes.position;
      for (let i = 0; i < p.count; i++) {
        const zz = p.getZ(i); let dy = 0;
        if (heelH > 0) dy += heelH * (1 - smooth((zz - (z0 + L * 0.28)) / (L * 0.42)));
        if (zz > zBall) dy += 0.013 * k * Math.pow((zz - zBall) / (z1 - zBall), 2);
        p.setY(i, p.getY(i) + dy);
      }
      geo.computeVertexNormals();
      return geo;
    };
    // the sole: a sampled outline, extruded, a welt wider than the upper
    const welt = (sneaker ? 0.003 : work || dress ? 0.004 : 0.002) * k;
    const so = new THREE.Shape(), NS = LOW ? 8 : 18;
    for (let i = 0; i <= NS; i++) { const t = 0.5 - 0.5 * Math.cos(Math.PI * i / NS); const x = wAt(t) + welt, z = z0 + t * L; if (i === 0) so.moveTo(x, -z); else so.lineTo(x, -z); }
    for (let i = NS - 1; i > 0; i--) { const t = 0.5 - 0.5 * Math.cos(Math.PI * i / NS); so.lineTo(-(wAt(t) + welt), -(z0 + t * L)); }
    so.closePath();
    const mkSole = (y0, th, mat) => {
      const sg = new THREE.ExtrudeGeometry(so, { depth: th, bevelEnabled: true, bevelThickness: Math.min(0.003 * k, th * 0.3), bevelSize: 0.0025 * k, bevelSegments: 1, curveSegments: 4 });
      sg.rotateX(-Math.PI / 2); sg.translate(0, y0 + Math.min(0.003 * k, th * 0.3), 0);
      g.add(new THREE.Mesh(bend(sg), mat));
    };
    if (sneaker) { mkSole(0, 0.006 * k, K.finish.rubber()); mkSole(0.006 * k, soleT - 0.006 * k, sole); }
    else mkSole(0, soleT, sole);
    // heel block under the raised rear
    if (heelH > 0.004 * k) {
      const hw = wAt(0.12) * (western ? 0.8 : 0.95), hl = L * (western ? 0.22 : 0.26);
      const heel = TXT.roundedBox(hw * 2, heelH + 0.004 * k, hl, 0.003 * k, sole);
      heel.position.set(0, (heelH + 0.004 * k) / 2, z0 + hl / 2 + 0.006 * k);
      if (western) { heel.scale.z = 0.9; heel.position.z += 0.006 * k; }
      g.add(heel);
    }
    // the upper
    const ctrl = [];
    const NT = LOW ? 6 : 10;
    for (let i = 0; i <= NT; i++) {
      const t = lerp(0.03, 0.975, i / NT), top = hAt(t), yc = soleT + (top - soleT) * 0.42;
      ctrl.push({ p: [0, yc, z0 + t * L], rx: wAt(t) * 0.97, ry: top - yc, ryn: yc - soleT + 0.006 * k });
    }
    const up = loft(ctrl, { seg: LOW ? 10 : 16, per: LOW ? 1 : 2, n: 2.25, ref: [1, 0, 0], capStart: 'dome', capEnd: 'dome', domeK: 0.35, floor: soleT * 0.8 });
    g.add(new THREE.Mesh(bend(up), upper));
    // the collar and shaft around the ankle
    const shaftH = western ? 0.24 : boot || work ? 0.15 : 0.09;
    const sh = loft([
      { p: [0, 0.045 * k, -0.018 * k], rx: 0.04 * k, ry: 0.05 * k },
      { p: [0, shaftH * 0.55 * k, -0.012 * k], rx: 0.041 * k, ry: 0.046 * k },
      { p: [0, shaftH * k, -0.008 * k], rx: (western ? 0.05 : 0.043) * k, ry: (western ? 0.052 : 0.046) * k }],
    { seg: LOW ? 10 : 18, per: LOW ? 1 : 3, capEnd: 'flat', ref: [1, 0, 0] });
    g.add(new THREE.Mesh(bend(sh), upper));
    // laces over a tongue on the vamp
    if (!LOW && !western && lace) {
      const t0 = dress ? 0.4 : 0.34, t1 = dress ? 0.58 : 0.62, nb = dress ? 4 : 6;
      const slope = (t) => Math.atan2(hAt(t + 0.02) - hAt(t - 0.02), 0.04 * L);
      const tm = (t0 + t1) / 2;
      const tongue = new THREE.Mesh(new THREE.BoxGeometry(wAt(tm) * 0.95, 0.006 * k, (t1 - t0) * L * 1.15), upper);
      tongue.position.set(0, hAt(tm) + 0.001 * k + (heelH ? heelH * (1 - smooth((tm - 0.28) / 0.42)) : 0), z0 + tm * L); tongue.rotation.x = -slope(tm); g.add(tongue);
      for (let b = 0; b < nb; b++) {
        const t = lerp(t0, t1, b / (nb - 1)), zz = z0 + t * L;
        const lift = heelH ? heelH * (1 - smooth((zz - (z0 + L * 0.28)) / (L * 0.42))) : 0;
        const bar = new THREE.Mesh(new THREE.BoxGeometry(wAt(t) * 1.25, 0.0032 * k, 0.0065 * k), lace);
        bar.position.set(0, hAt(t) + 0.0045 * k + lift, zz); bar.rotation.x = -slope(t); bar.rotation.y = (b % 2 ? 1 : -1) * 0.18; g.add(bar);
      }
    }
    g.userData.lift = 0;
    return g;
  }
  /* ---- hats --------------------------------------------------------------------------- */
  function hat(kind, W, D, top, mat, rr, Hh) {
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
      /* THE CAP FITS THE SKULL AND ITS BILL IS IN FRONT (weekly pass 2026-10-03). It was a
       * hemisphere 0.1 m tall, which stood about 2.4 cm proud of the scalp and read as a helmet
       * (no. 37's judges: "helmet-like"), and its bill was a sphere band near the equator, so it
       * printed as an upright plank on the wearer's RIGHT side: the model rotated it to the front
       * and then set the rotation back to 0. Now the crown is a lathe whose height is the head's
       * own height above the band plus a tenth of the head, six sewn panels pressed in at the
       * seams, and the bill is a crescent off the front of the band, pitched down and curved down
       * at its sides, as a worn bill is. Hh is the head's half height (makePerson passes it). */
      const hh = Hh || top / 0.32, crownH = (hh - top) + 0.1 * hh;
      const prof = [[1.0, 0], [0.99, 0.3], [0.94, 0.55], [0.84, 0.75], [0.66, 0.9], [0.4, 0.98], [0.001, 1.0]];
      const cr = new THREE.LatheGeometry(prof.map((q) => new THREE.Vector2(q[0], q[1] * crownH)), 96);
      const cp = cr.attributes.position;
      for (let i = 0; i < cp.count; i++) {
        const x = cp.getX(i), y = cp.getY(i), z = cp.getZ(i), az = Math.atan2(x, z);
        let dmin = 9;
        for (let j = 0; j < 6; j++) { const d = Math.abs(Math.atan2(Math.sin(az - (j + 0.5) * Math.PI / 3), Math.cos(az - (j + 0.5) * Math.PI / 3))); dmin = Math.min(dmin, d); }
        const seam = 1 - 0.018 * Math.exp(-(dmin * dmin) / 0.0016) * smooth(y / (crownH * 0.15));
        cp.setXYZ(i, x * W * 1.08 * seam, y, z * D * 1.06 * seam);
      }
      cr.computeVertexNormals();
      g.add(new THREE.Mesh(cr, mat));
      // the band: a slightly proud ring at the base, the crown's own colour a shade down
      const band = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 0.012 * (hh / 0.117), 64, 1, true),
        K.mat('p-capband-' + mat.uuid, { color: new THREE.Color(mat.color).multiplyScalar(0.82).getHex(), roughness: 0.85, side: THREE.DoubleSide }));
      band.scale.set(W * 1.09, 1, D * 1.07); band.position.y = 0.006 * (hh / 0.117); g.add(band);
      // the bill: a crescent from the band's front arc, tapering to nothing at its two ends
      const Lb = 0.74 * D, NU = 28, NV = 7, bp = [], bi = [];
      for (let v = 0; v <= NV; v++) for (let u = 0; u <= NU; u++) {
        const uu = (u / NU) * 2 - 1, a = uu * 1.05, t = v / NV, tp = Math.pow(Math.cos(uu * Math.PI / 2), 0.6);
        const ix = Math.sin(a) * W * 1.08, iz = Math.cos(a) * D * 1.06;
        let nx = Math.sin(a) / W, nz = Math.cos(a) / D; const nl = Math.hypot(nx, nz); nx /= nl; nz /= nl;
        const out = Lb * tp * t;
        bp.push(ix + nx * out, 0.003 * (hh / 0.117) - out * 0.15 - 0.16 * Lb * uu * uu * t * tp, iz + nz * out);
      }
      for (let v = 0; v < NV; v++) for (let u = 0; u < NU; u++) { const a = v * (NU + 1) + u, b = a + NU + 1; bi.push(a, b, a + 1, b, b + 1, a + 1); }
      const bill = new THREE.BufferGeometry(); bill.setAttribute('position', new THREE.Float32BufferAttribute(bp, 3)); bill.setIndex(bi); bill.computeVertexNormals();
      g.add(new THREE.Mesh(bill, K.mat('p-capbill-' + mat.uuid, { color: mat.color.getHex(), roughness: 0.8, side: THREE.DoubleSide })));
      const btn = new THREE.Mesh(new THREE.SphereGeometry(0.0065 * (hh / 0.117), 10, 6), mat); btn.position.y = crownH - 0.001; btn.scale.y = 0.5; g.add(btn);
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
        const Mx = new THREE.Matrix4().multiplyMatrices(inv, m.matrixWorld);
        g.applyMatrix4(Mx);
        if (!g.attributes.normal) g.computeVertexNormals();
        // a mirrored transform turns every triangle inside out once baked: wind them back
        if (Mx.determinant() < 0) for (const key of Object.keys(g.attributes)) {
          const at = g.attributes[key], is = at.itemSize, ar = at.array;
          for (let t = 0; t < at.count; t += 3) for (let c = 0; c < is; c++) { const i1 = (t + 1) * is + c, i2 = (t + 2) * is + c, tmp = ar[i1]; ar[i1] = ar[i2]; ar[i2] = tmp; }
        }
        return g;
      });
      const hasUV = parts.every((g) => g.attributes.uv);
      const hasC = mat.vertexColors && parts.every((g) => g.attributes.color);
      let total = 0; parts.forEach((g) => { total += g.attributes.position.count; });
      const pos = new Float32Array(total * 3), nor = new Float32Array(total * 3), uv = hasUV ? new Float32Array(total * 2) : null, col = hasC ? new Float32Array(total * 3) : null;
      let o = 0;
      parts.forEach((g) => { pos.set(g.attributes.position.array, o * 3); nor.set(g.attributes.normal.array, o * 3);
        if (uv) uv.set(g.attributes.uv.array, o * 2); if (col) col.set(g.attributes.color.array, o * 3); o += g.attributes.position.count; g.dispose(); });
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
      if (uv) geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
      if (col) geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
      out.add(new THREE.Mesh(geo, mat));
    }
    return out;
  }

  /* ---- the person ---------------------------------------------------------------------- */
  K.define('person', {
    size: [0.5, 1.75, 0.3],
    options: { seed: 1, role: 'resident', pose: 'stand', toward: 1, height: null, build: 'auto',
               hat: 'auto', hatColor: null, shade: false, vest: 'auto', skin: null, shirt: null, trousers: null, detail: 'full',
               headPitch: null, hands: null, handShape: null },
    note: 'Articulated adult 1.60 to 1.90 m by seed, slim to heavy. role resident|worker|official; pose stand|walk|point|hands_on_hips|look_up|read|sit_read|sit_drive|kneel (kneel puts one knee on the ground, the leg on the `toward` side forward with its foot flat, the trunk leaning in and the forearms reaching forward and down to a casualty or the ground, the hips at about 0.5 m; read leans over a desk on +z, head down, forearms forward; sit_read folds the legs so the hips sit at seat height); toward -1|1 for point; hat auto|none|cap|cowboy|hard, hatColor a colour for it; shade true raises a hand to shade the eyes in look_up (never by default); build auto|male|female. sit_drive sits upright at the wheel with the head level, eyes on the road, and both hands closed on the rim at ten and two of a nominal wheel ahead of the chest. headPitch, any pose: the pitch of the head from LEVEL in radians, positive looks down, whatever the torso does (0 is a level gaze; sit_read bakes about 0.52 down). hands, any pose: [left, right] grip points in the frame of the person (left is +x), each [x, y, z] or null; a hand closes on that point by two bone reach, and a point out of reach is reached toward. handShape, with hands: [left, right], each grip (default, the hand closes on the point) or press (the hand opens to a pointing hand, palm down, and the index fingertip lands on the point; attach.hands[i] then carries press true, tip, the measured fingertip, and short, metres from tip to point). With sit_drive or hands the origin is kept (feet on y 0, hips on z 0, the midline on x 0) and userData.attach publishes hip, seat (the measured underside of the trousers below the hips, where a cushion meets them), eye and hands (each grip, the point reached, and short, metres it fell short). semi_cab_interior publishes attach.rim, its own ten and two, so a driver takes hands: A.rim.map((p) => [p[0] - x, p[1] - y, p[2] - z]) for a person at x, y, z. The seeded skin palette is held to measured human skin; skin as a colour overrides it. Shirt and trousers are single distance-field garments with folds; hair has volume by style.',
    make(o, r) {
      LOW = o.detail === 'low';
      try { return makePerson(o, r); } finally { LOW = false; }
    },
  });
  function makePerson(o, r) {
    const role = o.role || 'resident', pose = o.pose || 'stand';
    const fem = o.build === 'female' ? true : o.build === 'male' ? false : r() < 0.4;
    const H = o.height || (fem ? lerp(1.6, 1.76, r()) : lerp(1.68, 1.9, r()));
    const k = H / 1.75;
    const mass = Math.pow(r(), 1.5) * (role === 'official' ? 0.85 : 1);          // 0 slim .. 1 heavy
    const bw = (fem ? 0.9 : 1) * lerp(0.96, 1.08, r()) * (1 + 0.05 * mass);    // shoulder / chest breadth
    const hw = (fem ? 1.05 : 1) * lerp(0.96, 1.06, r()) * (1 + 0.07 * mass);   // hip breadth
    const belly = lerp(0, 0.012, r()) + mass * (fem ? 0.022 : 0.04);
    const ph = [r() * 6.28, r() * 6.28, r() * 6.28, r() * 6.28];               // fold phases
    const G = new THREE.Group();

    // palette by seed and role
    const skinC = o.skin != null ? (o.skin < 20 ? SKIN[o.skin | 0] : o.skin) : pick(r, SKIN);
    const skin = skinMat('p-skin', { color: skinC });
    // nails: the skin's colour through a hard, glossier plate, a little paler and pinker
    const nailM = K.mat('p-nail', { color: new THREE.Color(skinC).multiplyScalar(1.1).lerp(new THREE.Color(0xd8a49a), 0.12).getHex(), roughness: 0.35, clearcoat: 0.45, clearcoatRoughness: 0.3 }, true);
    // ears are thin and backlit, so they run redder than the face
    const earM = skinMat('p-skin-ear', { color: new THREE.Color(skinC).lerp(new THREE.Color(0xb0524c), 0.14).getHex() });
    const hairC = pick(r, HAIR);
    // hair takes its value per vertex (roots, creases, one lock against the next) over its own colour;
    // its sheen is its own colour lifted, never a near white one, which frosted every head
    const hairM = K.mat('p-hair', { color: hairC, roughness: 0.58, map: clothTex('strands', 0, 0, 0), vertexColors: true,
      sheen: 0.3, sheenColor: new THREE.Color(hairC).lerp(new THREE.Color(0xe8d8c4), 0.35).getHex(), sheenRoughness: 0.5, specularIntensity: 0.6 }, true);
    // the face carries its own tint per vertex and a faint oily sheen the body doesn't
    const faceM = skinMat('p-skin-face', { color: skinC, vertexColors: true, clearcoat: 0.07, clearcoatRoughness: 0.4 });
    let shirtKind = 'tee', shirtM, trouserM, jacket = false, sleeves = 'long', tie = null, jeans = false;
    const sroll = r();
    if (role === 'official') {
      const sc = o.shirt != null ? o.shirt : pick(r, SUITS);
      shirtM = cloth('suit', sc); trouserM = cloth('suit', sc); jacket = true; sleeves = 'long';
      tie = pick(r, [0x7a1f25, 0x1f3050, 0x3a3a3a, 0x5a2240, 0x2c4a3a]);
    } else {
      if (role === 'worker') shirtKind = sroll < 0.5 ? 'tee' : 'work';
      else shirtKind = sroll < 0.35 ? 'tee' : sroll < 0.6 ? 'plaid' : sroll < 0.8 ? 'button' : 'polo';
      sleeves = shirtKind === 'tee' || shirtKind === 'polo' ? 'short' : r() < 0.35 ? 'rolled' : 'long';
      // A SHIRT COLOUR THE CALLER NAMED WINS ON EVERY SEED (2026-10-12). A plaid roll used to ignore
      // `shirt`, so no. 48 asked for a dark shirt at seed 8 and got a plaid one. The plaid is still
      // picked, so the seed's later draws are unchanged, and the cut (placket, flap pockets) stays.
      if (shirtKind === 'plaid') { const pl = pick(r, PLAIDS); shirtM = o.shirt != null ? cloth('cloth', o.shirt) : cloth('plaid', pl[0], { b: pl[1], c: pl[2] }); }
      else shirtM = cloth('cloth', o.shirt != null ? o.shirt : shirtKind === 'work' ? pick(r, [0x6d7f8f, 0x8a7a5c, 0x3f4f5f, 0xb0a58a]) : pick(r, SHIRTS));
      jeans = role === 'worker' ? r() < 0.7 : r() < 0.65;
      if (o.trousers != null) jeans = false;
      trouserM = o.trousers != null ? cloth('cloth', o.trousers, { rough: 0.9 }) : jeans ? cloth('denim', pick(r, DENIM)) : cloth('cloth', pick(r, KHAKI), { rough: 0.9 });
    }
    const shoeStyle = role === 'official' ? 'dress' : role === 'worker' ? 'work' : pick(r, ['sneaker', 'sneaker', 'western', 'boot']);
    const shoeUpper = shoeStyle === 'sneaker' ? K.mat('p-sneak', { color: capAlb(pick(r, [0xe8e6e0, 0x2a2c30, 0x5a6470, 0xb8b2a6])), roughness: 0.78, sheen: 0.3, sheenColor: 0xffffff, sheenRoughness: 0.8 }, true)
      : shoeStyle === 'dress' ? K.mat('p-dress', { color: 0x151312, roughness: 0.3, clearcoat: 0.7, clearcoatRoughness: 0.25 }, true)
      : shoeStyle === 'work' ? K.mat('p-work', { color: pick(r, [0x7a5530, 0x5a3e24, 0x8f6a3e]), roughness: 0.72, sheen: 0.3, sheenColor: 0xd8b890, sheenRoughness: 0.7 }, true)
      : K.mat('p-leather', { color: pick(r, [0x5a3a22, 0x3a2416, 0x7a4c2a, 0x2a1d16]), roughness: 0.48, clearcoat: 0.35, clearcoatRoughness: 0.45 }, true);
    const soleM = shoeStyle === 'sneaker' ? K.mat('p-sole', { color: capAlb(0xefece6), roughness: 0.65 }) : shoeStyle === 'work' ? K.mat('p-lug', { color: 0x2a211b, roughness: 0.8 }) : K.mat('p-dsole', { color: 0x3a2a1e, roughness: 0.6 });
    const laceM = shoeStyle === 'sneaker' ? K.mat('p-lace', { color: capAlb(0xf1efe9), roughness: 0.85 }) : shoeStyle === 'dress' ? K.mat('p-lace-d', { color: 0x141210, roughness: 0.7 }) : K.mat('p-lace-w', { color: 0xa08058, roughness: 0.85 });

    /* SKELETON (y from the ground, before the stance lift). */
    const Y = (f) => f * H;
    const shoulderX = 0.178 * k * bw, hipX = 0.086 * k * hw;
    const upperArm = 0.305 * k, foreArm = 0.25 * k, thigh = 0.43 * k, shin = 0.425 * k;
    const hipY = Y(0.52);
    const n3 = (x, y, z) => V3(x, y, z).normalize();
    const arm = {}, leg = {};
    let headPitch = 0, headYaw = 0, torsoLean = 0;
    // THE ARMS AT REST (weekly pass 2026-10-16). They hung straight and splayed, both alike, which
    // is a shop mannequin's A-pose, and the judges named it on nos. 48, 49, 51 and 52 ("a stiff
    // A-pose", "a mannequin"). A standing adult's upper arm falls nearly plumb and a little back,
    // the elbow carries a soft bend that brings the hand forward to the side of the thigh, and the
    // two arms never match. The bend varies by side off a fold phase already drawn, so no seed's
    // later draws (shirt, hair, hat) move.
    for (const s of [1, -1]) {
      const bend = 0.26 + 0.08 * Math.sin(ph[2] + (s > 0 ? 0 : 2.1));
      arm[s] = { u: n3(s * 0.11, -1, -0.05), f: n3(s * 0.05, -1, bend), hand: 'relax' };
      leg[s] = { t: n3(s * 0.025, -1, 0.0), c: n3(s * 0.01, -1, -0.01) };
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
      // A HAND SHADING THE EYES IS ASKED FOR, never rolled (weekly pass 2026-10-26). It was a 60 percent
      // seeded roll, and no. 61's resident looking up at an aircraft read to every round 2 and 3 judge as
      // "a saluting kit mannequin" with "a hand clamped over the face". The roll is still drawn so every
      // later seeded choice for this person is the one it was.
      r();
      if (o.shade === true) arm[s] = { u: n3(s * 0.55, 0.15, 0.55), f: n3(-s * 0.75, 0.45, -0.1), hand: 'shade' };
    } else if (pose === 'read' || pose === 'sit_read') {
      // Reading a screen or a page on a desk in front (+z): head down, standing forearms angled
      // down so the hands land on a desk top at about 0.76 m, seated forearms forward to it.
      // sit_read folds the legs to a seat, and the ankle lift below then sets the hips at about
      // knee height, which is where a school or office seat is.
      headPitch = 0.42; torsoLean = pose === 'read' ? 0.12 : 0.1;
      for (const s of [1, -1]) arm[s] = pose === 'read' ? { u: n3(s * 0.12, -1, 0.2), f: n3(-s * 0.14, -0.72, 0.7), hand: 'relax' }
        : { u: n3(s * 0.1, -1, 0.3), f: n3(-s * 0.12, -0.5, 1), hand: 'relax' };
      if (pose === 'sit_read') for (const s of [1, -1]) leg[s] = { t: n3(s * 0.06, -0.08, 1), c: n3(s * 0.01, -1, 0.06) };
    } else if (pose === 'sit_drive') {
      // A DRIVER, OR AN OBSERVER IN THE DRIVER'S SEAT (weekly pass 2026-11-12). The only seated pose was
      // sit_read, whose head pitch is baked in, and no. 75's frame 8 put it behind a truck's wheel: every
      // pixel critic, the flow critic and all nine panel cards in three rounds read a slumped or sleeping
      // mannequin, and the craft judge's last fix was "the person's hands on the rim". So the trunk sits
      // up against the seat back with a slight recline, the head is level (its pitch below cancels the
      // recline), the knees ride a little above the hips with the shins forward to the pedals, and both
      // hands close on the rim (the grip reach below), at the caller's points or a nominal wheel's.
      torsoLean = -0.06; headPitch = 0.06;
      for (const s of [1, -1]) {
        leg[s] = { t: n3(s * 0.07, 0.04, 1), c: n3(s * 0.02, -0.94, 0.34) };
        arm[s] = { u: n3(s * 0.1, -0.6, 0.8), f: n3(-s * 0.1, 0.1, 1), hand: 'grip', grip: null };
      }
    }
    if (pose === 'kneel') {
      // A KNEEL, ONE KNEE DOWN (weekly pass 2026-11-22). The kit had no kneel, so no. 84's frame 8 sank a
      // standing person to its knees and built the shins and boots by hand lying back along the floor, and
      // all three judges in all three rounds read "a primitive medic", "boots splayed as blocks", the round 3
      // craft judge's fix "a properly jointed figure ... kneeling at a role player". So the skeleton kneels:
      // the lead leg (toward, +x by default) has its thigh forward and its shin plumb to a flat foot, the
      // other thigh falls plumb to a knee on the ground and its shin lies back, rising a little to the ankle,
      // so the boot's toes tuck under it (the shoe pitch below finds the ground). The ankle lift then sets
      // the hips at about a shin's height. The trunk leans in, the head looks down and forward, and both
      // forearms reach forward and down to work at the ground or a casualty; `hands` places them exactly.
      const lead = tw;
      leg[lead] = { t: n3(lead * 0.1, 0.07, 1), c: n3(lead * 0.02, -1, 0.02) };
      leg[-lead] = { t: n3(-lead * 0.03, -1, -0.1), c: n3(-lead * 0.02, 0.45, -1) };
      torsoLean = 0.14; headPitch = 0.38;
      for (const s of [1, -1]) arm[s] = { u: n3(s * 0.12, -1, 0.5), f: n3(-s * 0.12, -0.55, 1), hand: 'relax' };
    }
    // A HAND ON A NAMED POINT, any pose (weekly pass 2026-11-12; kit-person-full-length asked for it as a
    // grip on a chain on no. 54). The point is in the person's own frame, left (+x) first.
    const gripAt = Array.isArray(o.hands) ? o.hands : null;
    if (gripAt) for (const [i, s] of [[0, 1], [1, -1]]) {
      const g = gripAt[i];
      if (Array.isArray(g) && g.length === 3 && g.every(Number.isFinite)) arm[s] = { u: arm[s].u, f: arm[s].f, hand: 'grip', grip: V3(g[0], g[1], g[2]) };
      // A FINGER ON THE POINT, not a fist (weekly pass 2026-11-24, queue kit-people-cartoon-at-table-range and
      // kit-person-reads-as-mannequin-within-two-metres). handShape [left, right], each 'grip' (the default)
      // or 'press': the hand opens to a pointing hand, palm down, and its index fingertip lands on the point.
      // No. 86 frame 6 built that finger by hand out of two capsules on a fist, and every judge in rounds
      // 2 to 4 still read the operator's hand as a mannequin's.
      if (arm[s].hand === 'grip' && Array.isArray(o.handShape) && o.handShape[i] === 'press') arm[s].press = true;
    }
    // THE HEAD'S PITCH, asked for (weekly pass 2026-11-12). Measured from level, so 0 is a level gaze in any
    // pose: the pivot below turns the head by headPitch + torsoLean, so the lean is taken back out here.
    if (Number.isFinite(o.headPitch)) headPitch = o.headPitch - torsoLean;
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
    // the torso leans about the hips; everything above them follows
    const pivY = Yl(0.52), cl = Math.cos(torsoLean), sl = Math.sin(torsoLean);
    const leanV = (v) => { const dy = v.y - pivY, dz = v.z; v.y = pivY + dy * cl - dz * sl; v.z = dy * sl + dz * cl; return v; };

    /* TORSO TABLES: rows [yFrac, halfW, front, back, zc]. The shirt table is the garment surface. */
    const bk = belly * k, mk = 1 + 0.06 * mass;
    const neckR = 0.058 * k * (fem ? 0.86 : 1) * (1 + 0.1 * mass), nr = neckR / k;
    const lower = [[0.495, 0.09, 0.03, 0.07, -0.014], [0.515, 0.156, 0.06, 0.108, -0.008], [0.54, 0.168, 0.085, 0.116, -0.004],
                   [0.578, 0.163, 0.098 + bk * 0.6, 0.104, 0], [0.61, 0.157, 0.102 + bk, 0.094, 0.002]];
    const hemY = jacket ? 0.47 : shirtKind === 'plaid' || shirtKind === 'button' || shirtKind === 'work' ? (r() < 0.5 ? 0.6 : 0.555) : 0.55;
    const tucked = hemY >= 0.595;
    const upper = [[hemY, jacket ? 0.176 : tucked ? 0.16 : 0.172, (tucked ? 0.104 : 0.11) + bk, tucked ? 0.097 : 0.112, 0],
                   [hemY + 0.03, jacket ? 0.17 : 0.166, 0.107 + bk, 0.104, 0],
                   [Math.max(0.64, hemY + 0.06), 0.16 * mk, 0.108 + bk * 1.2, 0.097, 0],
                   [0.69, 0.16 * mk, 0.113 + bk * 0.7 + (fem ? 0.006 : 0), 0.099, 0.002],
                   [0.735, 0.165 * mk, 0.121 + (fem ? 0.024 : 0) + bk * 0.3, 0.104, 0.006],
                   [0.775, 0.166 * mk, 0.112 + (fem ? 0.01 : 0), 0.105, 0.004],
                   [0.8, (jacket ? 0.165 : 0.158), 0.095, 0.099, 0.002], [0.817, 0.138, 0.079, 0.087, -0.002], [0.832, 0.11, 0.066, 0.072, -0.006],
                   [0.845, nr + 0.03, nr + 0.018, nr + 0.022, -0.01], [0.857, nr + 0.017, nr + 0.014, nr + 0.018, -0.012]];
    for (let i = 1; i < upper.length; i++) if (upper[i][0] <= upper[i - 1][0]) upper[i][0] = upper[i - 1][0] + 0.012;
    const ring = (row, wk, extra) => ({ p: [0, Yl(row[0]), row[4] * k], rx: row[1] * k * wk + (extra || 0), ry: row[2] * k + (extra || 0), ryn: row[3] * k + (extra || 0) });
    const wk = (i) => (i <= 3 ? lerp(hw, bw, i / 3) : bw);
    // the shirt always clears the seat under it
    const lowAt = (yf) => { let i = 1; while (i < lower.length - 1 && lower[i][0] < yf) i++;
      const a = lower[i - 1], b = lower[i], t = clamp01((yf - a[0]) / (b[0] - a[0])); return a.map((v, j) => lerp(v, b[j], t)); };
    upper.forEach((row, i) => {
      if (row[0] > 0.63) return;
      const lo = lowAt(row[0]), m = tucked && i === 0 ? 0.001 : 0.01;
      row[1] = Math.max(row[1], (lo[1] * hw + m) / wk(i)); row[2] = Math.max(row[2], lo[2] + m); row[3] = Math.max(row[3], lo[3] + m);
    });
    const JX = jacket ? 0.006 * k : 0;
    const ringAt = (yf, extra) => {
      let i = 1; while (i < upper.length - 1 && upper[i][0] < yf) i++;
      const a = upper[i - 1], b = upper[i], t = clamp01((yf - a[0]) / (b[0] - a[0]));
      const row = a.map((v, j) => lerp(v, b[j], t)); row[0] = yf;
      return ring(row, lerp(wk(i - 1), wk(i), t), JX + extra);
    };
    const frontZ = (yf) => {
      for (let i = 1; i < upper.length; i++) if (yf <= upper[i][0]) {
        const t = (yf - upper[i - 1][0]) / (upper[i][0] - upper[i - 1][0]);
        return (lerp(upper[i - 1][2], upper[i][2], t) + lerp(upper[i - 1][4], upper[i][4], t)) * k + JX;
      }
      return 0.05 * k;
    };
    // a lookup of a table's rows by height, Catmull-Rom smoothed so the torso has no ring kinks
    function tableLUT(rows, wkf, extra) {
      const NL = 180, y0 = Yl(rows[0][0]), y1 = Yl(rows[rows.length - 1][0]);
      const A = new Float32Array(NL), F = new Float32Array(NL), Bk = new Float32Array(NL), Z = new Float32Array(NL);
      const ys = rows.map((rw) => Yl(rw[0]));
      const cr = (a, b, c, d, t) => 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t * t * t);
      const col = (j, i) => { i = Math.max(0, Math.min(rows.length - 1, i)); return j === 1 ? rows[i][1] * k * wkf(i) : rows[i][j] * k; };
      for (let q = 0; q < NL; q++) {
        const y = lerp(y0, y1, q / (NL - 1));
        let i = 1; while (i < rows.length - 1 && ys[i] < y) i++;
        const t = clamp01((y - ys[i - 1]) / (ys[i] - ys[i - 1]));
        A[q] = cr(col(1, i - 2), col(1, i - 1), col(1, i), col(1, i + 1), t) + extra;
        F[q] = cr(col(2, i - 2), col(2, i - 1), col(2, i), col(2, i + 1), t) + extra;
        Bk[q] = cr(col(3, i - 2), col(3, i - 1), col(3, i), col(3, i + 1), t) + extra;
        Z[q] = cr(col(4, i - 2), col(4, i - 1), col(4, i), col(4, i + 1), t);
      }
      return (x, y, z) => {
        let t = (y - y0) / (y1 - y0) * (NL - 1); t = t < 0 ? 0 : t > NL - 1 ? NL - 1 : t;
        const i = Math.min(NL - 2, t | 0), f = t - i;
        const a = A[i] + (A[i + 1] - A[i]) * f, zc = Z[i] + (Z[i + 1] - Z[i]) * f, dz = z - zc;
        const c = dz > 0 ? F[i] + (F[i + 1] - F[i]) * f : Bk[i] + (Bk[i + 1] - Bk[i]) * f;
        let d = ell2(x, dz, a, c);
        d = Math.max(d, y0 - y, y - y1);
        return d;
      };
    }
    const noise = (x, y, z, s) => Math.sin(x * s + ph[0]) * Math.sin(y * s * 0.83 + ph[1]) * Math.sin(z * s * 1.17 + ph[2]) + 0.5 * Math.sin((x + z) * s * 1.9 + ph[3]) * Math.sin(y * s * 2.3 + ph[0]);

    /* TROUSERS: the seat and both legs as one field, hemmed over the shoe. */
    const seatRaw = tableLUT(lower, () => hw, 0);
    const waistTop = Yl(0.612);
    const legF = {};
    for (const s of [1, -1]) {
      const L = leg[s];
      const at = (a, b, t) => a.clone().lerp(b, t).toArray();
      const top = L.hip.clone().add(V3(-s * 0.012 * k, 0.07 * k, 0.004 * k)).toArray();
      const Cd = L.ankle.clone().sub(L.knee).normalize();
      const hemP = L.ankle.clone().addScaledVector(Cd, 0.036 * k).toArray();
      const hemR = (jacket ? 0.057 : jeans ? (shoeStyle === 'western' || shoeStyle === 'boot' ? 0.064 : 0.058) : 0.057) * k;
      const f = tube([top, at(L.hip, L.knee, 0.35), L.knee.toArray(), at(L.knee, L.ankle, 0.38), hemP],
        [0.101 * k * hw * (1 + 0.16 * mass), 0.087 * k * hw * (1 + 0.18 * mass), 0.061 * k * (1 + 0.08 * mass), 0.063 * k * (1 + 0.12 * mass), hemR], { ref: [0, 0, 1], k: 0.02 * k });
      const kneeA = f.cum[2], len = f.len;
      const cn = V3(Cd.x, Cd.y, Cd.z), tilt = n3(Cd.x, Cd.y, Cd.z + 0.35);
      L.trF = (x, y, z) => {
        let d = f(x, y, z);
        const I = f.info, dk = I.along - kneeA, de = len - I.along;
        /* FOLDS A GRID CAN HOLD (2026-11-15). The ripples were 3.7 cm waves on a 1.6 cm grid, which
         * surface nets put down as lumps, and the critic saw "no folds". Each fold is now at least
         * twice the grid in wavelength and deep enough to cast its own shade. */
        let fold = 0;
        // over and behind the knee: soft horizontal ripples, deepest at the back
        if (dk > -0.1 * k && dk < 0.1 * k) fold += 0.0032 * k * Math.exp(-Math.pow(dk / (0.05 * k), 2)) * (0.35 + 0.65 * Math.max(0, -I.c)) * Math.sin(dk * 115 / k + I.s * 1.6 + ph[1]);
        // THE BREAK: the hem rests on the shoe, so the last 15 cm of the leg buckle in Z folds with one fold across the front
        if (de < 0.15 * k) {
          const w = 1 - de / (0.15 * k);
          fold += 0.0042 * k * w * (0.55 + 0.45 * I.c) * Math.sin(de * 105 / k + I.s * 1.8 + ph[2]);
          fold += 0.0055 * k * Math.exp(-Math.pow((de - 0.055 * k) / (0.018 * k), 2)) * smooth((I.c - 0.1) / 0.5);
          // the front of the hem is carried forward over the instep, so the leg rests ON the shoe
          fold += 0.011 * k * Math.pow(smooth(1 - de / (0.075 * k)), 1.5) * Math.pow(Math.max(0, I.c), 1.5);
        }
        // jeans: whiskers fanning from the crotch over the front of the thigh
        if (jeans && I.along < 0.22 * k && I.c > 0) fold += 0.0018 * k * I.c * Math.sin((I.along * 0.7 + I.s * 0.06) * 140 / k) * (1 - I.along / (0.22 * k));
        // the pressed crease down the front of a trouser leg (never jeans): a soft ridge from the hip to the break
        if (!jeans && I.c > 0.55) fold += 0.0024 * k * Math.exp(-Math.pow(I.s / 0.11, 2)) * smooth(I.along / (0.12 * k)) * (1 - 0.6 * smooth((0.06 * k - de) / (0.05 * k)));
        // the cloth hangs off the thigh and the seat in long shallow drapes
        fold += 0.0014 * k * Math.sin(I.s * 3 + I.along * 9 / k + ph[0]) * smooth(I.along / (0.3 * k));
        d -= fold + 0.0006 * k * noise(x, y, z, 13);
        // hem: a plane, lower at the back, its edge a rounded bead (the turned hem is laid over it, see hemGeo)
        d = smax(d, (x - hemP[0]) * tilt.x + (y - hemP[1]) * tilt.y + (z - hemP[2]) * tilt.z, 0.005 * k);
        return d;
      };
      L.trTube = f; L.hemP = hemP; L.tilt = tilt; L.hemR = hemR;
    }
    const crotchY = Yl(0.5);
    const trouserF = (x, y, z) => {
      let d = seatRaw(x, y, z) - 0.0006 * k * noise(x, y, z, 12);
      const ks = 0.04 * k * smooth((y - crotchY) / (0.06 * k));
      const a = leg[1].trTube.lb(x, y, z) < d + ks ? leg[1].trF(x, y, z) : 1, b = leg[-1].trTube.lb(x, y, z) < d + ks ? leg[-1].trF(x, y, z) : 1;
      d = smin(d, smin(a, b, 0.008 * k), ks);
      return Math.max(d, y - waistTop);
    };

    /* THE UNTUCKED SHIRT FALLS OVER THE HIPS (weekly pass 2026-10-22). Below the waist the shirt's
     * rows were widened only to clear the seat TABLE, but the trousers are the seat and both thigh
     * tubes, and the thighs' tops stand wider than the seat. A clearance band over the real trousers
     * caught it, joined to the torso with a hard min and cut flat at the waistband, so the shirt's
     * lower 6 cm stood out as a second, wider tier with a ledge on top: a peplum. The judges named it
     * on no. 57 frame 9 as a ragged hem, and it is the waist of every untucked kit person. So each row
     * below the waistband is measured against the trousers it hangs over: march out from the row's
     * centre round 32 bearings to the trousers' surface, and scale the row's ellipse until every one
     * of those points sits inside it by the clearance. A row at the waistband is added so the curve
     * can't dip between the hip row and the chest. No random draw is added, so no seed moves. */
    if (!tucked && !jacket) {
      const clrT = 0.011 * k;
      if (upper[1][0] < 0.6) {
        upper.splice(2, 0, upper[1].slice()); upper[2][0] = 0.606;
        // wk() blends hip to shoulder breadth by row INDEX, so the row pushed down one index keeps
        // the breadth it had: the chest above the waist is exactly as before
        upper[3][1] *= lerp(hw, bw, 2 / 3) / wk(3);
      }
      for (let i = 0; i < upper.length && upper[i][0] < 0.63; i++) {
        const row = upper[i], y = Yl(row[0]), zc = row[4] * k;
        const a = row[1] * k * wk(i), cF = row[2] * k, cB = row[3] * k;
        const P = [];
        for (let j = 0; j < 32; j++) {
          const th = (j / 32) * Math.PI * 2, sx = Math.sin(th), sz = Math.cos(th);
          let rOut = 0;
          for (let rr = 0.02 * k; rr < 0.32 * k; rr += 0.003 * k) if (trouserF(rr * sx, y, zc + rr * sz) < 0) rOut = rr;
          if (rOut) P.push([(rOut + clrT) * sx, (rOut + clrT) * sz]);
        }
        // grow only the semi-axis a point presses on (the breadth, the front or the back), so a
        // seat that needs room behind does not also widen the hips: the cloth hangs, it isn't blown up
        let A = a, F = cF, B = cB;
        for (let it = 0; it < 24; it++) {
          let worst = null, q = 1;
          for (const [px, pz] of P) { const v = Math.hypot(px / A, pz / (pz > 0 ? F : B)); if (v > q) { q = v; worst = [px, pz]; } }
          if (!worst) break;
          const g = Math.min(q, 1.04);
          if (Math.abs(worst[0] / A) >= Math.abs(worst[1] / (worst[1] > 0 ? F : B))) A *= g; else if (worst[1] > 0) F *= g; else B *= g;
        }
        row[1] *= A / a; row[2] *= F / cF; row[3] *= B / cB;
      }
    }

    /* SHIRT (or jacket): torso, trapezius and sleeves in one field. */
    const torsoRaw = tableLUT(upper, wk, JX);
    const hemAbs = Yl(hemY);
    const shirtTop = Yl(0.868);
    const torsoF = (x, y, z) => {
      let yy = y, zz = z;
      if (torsoLean) { const dy = y - pivY; yy = pivY + dy * cl + z * sl; zz = -dy * sl + z * cl; }
      let d = torsoRaw(x, yy, zz);
      if (d > 0.03 * k) return d;
      const u = yy - hemAbs;
      let fold = 0;
      const fa = jacket ? 0.35 : 1;
      const th = Math.atan2(x, zz);
      if (!tucked && u < 0.14 * k) {                         // the hem hangs in soft vertical drapes
        fold += (jacket ? 0.4 : 1) * 0.004 * k * Math.pow(1 - u / (0.14 * k), 2) * Math.sin(th * 5 + ph[0]);
      }
      // GRAVITY: below the chest an untucked shirt hangs in long vertical drapes that deepen toward the hem
      if (!tucked) {
        const dr = smooth((Yl(0.7) - yy) / (0.16 * k));
        if (dr > 0) fold += fa * 0.0034 * k * dr * Math.sin(th * 6 + ph[0] + 0.8 * Math.sin(th * 2 + ph[1]));
      }
      // DRAG FOLDS from each armpit: the cloth is pulled from the arm's root toward the waist in a fan
      { const ax = Math.abs(x), dxa = 0.158 * k - ax, dya = Yl(0.77) - yy;
        if (dya > -0.01 * k && dxa > -0.02 * k) {
          const rho = Math.hypot(dxa, dya), phi = Math.atan2(dya, dxa);
          fold += fa * 0.0026 * k * smooth(rho / (0.04 * k)) * (1 - smooth((rho - 0.15 * k) / (0.07 * k))) * Math.sin(phi * 8 + (x > 0 ? ph[1] : ph[2]));
        } }
      if (tucked && u > 0.012 * k && u < 0.1 * k) {          // blousing above the belt: the shirt balloons and buckles over it
        const b = Math.sin(Math.PI * (u - 0.012 * k) / (0.088 * k));
        fold += b * (0.0035 * k + 0.0028 * k * Math.sin(th * 8 + ph[1] + 0.6 * Math.sin(th * 3 + ph[2])));
      }
      const side = smooth((Math.abs(x) / (0.16 * k) - 0.62) / 0.3);
      const yw = Yl(0.63);
      if (Math.abs(yy - yw) < 0.09 * k) fold += fa * 0.0016 * k * side * Math.exp(-Math.pow((yy - yw) / (0.035 * k), 2)) * Math.sin((yy - yw) * 150 / k + ph[2]);
      fold += fa * 0.0006 * k * noise(x, yy, zz, 11);
      d -= fold;
      // the hem, with a little life in it. ROUNDED, never a knife edge (weekly pass 2026-10-22): a
      // plane cut through the field is a crease narrower than the 1.6 cm mesh grid, so surface nets
      // put it down as a sawtooth with gradient normals scattered across it, and the judges read a
      // pale ragged line under the shirt on no. 57 frame 9 and under the vest on every worker. A hem
      // is cloth turned up on itself, so its edge is a bead about the grid's own size.
      const hem = hemAbs + (tucked ? 0 : 0.0025 * k * Math.sin(Math.atan2(x, zz) * 3 + ph[3]));
      return smax(d, hem - yy, HEMR);
    };
    const S0 = {}, Ecl = {}, Wrl = {};
    const traps = [];
    for (const s of [1, -1]) {
      const A = arm[s];
      const S = leanV(V3(s * shoulderX, Yl(0.793), -0.004 * k));
      const E = S.clone().addScaledVector(A.u, upperArm);
      let Wr = E.clone().addScaledVector(A.f, foreArm);
      if (A.hand === 'hip') {        // hands land on the hip crest
        const target = V3(s * 0.168 * k * hw, Yl(0.585), 0.012 * k);
        const d = target.clone().sub(S), len = d.length();
        const reach = Math.min(len, upperArm + foreArm - 0.001);
        const a = (upperArm * upperArm - foreArm * foreArm + reach * reach) / (2 * reach);
        const hgt = Math.sqrt(Math.max(0, upperArm * upperArm - a * a));
        const dn = d.clone().normalize(), out = V3(s, 0, -0.35).sub(dn.clone().multiplyScalar(V3(s, 0, -0.35).dot(dn))).normalize();
        E.copy(S).addScaledVector(dn, a).addScaledVector(out, hgt);
        Wr = S.clone().addScaledVector(dn, reach);
      }
      if (A.hand === 'grip') {       // the hand closes on a point: two bone reach, elbow down and out
        if (!A.grip) {               // sit_drive with no points: ten and two of a nominal wheel ahead of the chest
          const hy = leg[1].hip.y, R0 = 0.2 * k, ey = n3(0, 0.87, 0.5);
          A.grip = V3(0, hy + 0.5 * k, 0.43 * k).add(V3(s * R0 * Math.cos(Math.PI / 6), 0, 0)).addScaledVector(ey, R0 * Math.sin(Math.PI / 6));
        }
        // the palm faces in toward the midline and forward, and the rim sits in the curled fingers, so
        // the wrist stands back from the grip along the forearm and off it toward the back of the hand
        const hk = k * (fem ? 0.86 : 0.93) * (1 + 0.05 * mass);
        A.palm = A.press ? n3(-s * 0.3, -1, 0) : n3(-s, -0.2, 0.7);
        let wt = A.grip.clone(), Fd0 = A.grip.clone().sub(S).normalize();
        const tipL = A.press ? indexTip(hk, s) : null;
        for (let it = 0; it < (A.press ? 6 : 3); it++) {
          const pn = A.palm.clone().sub(Fd0.clone().multiplyScalar(A.palm.dot(Fd0))).normalize();
          if (A.press) wt = A.grip.clone().addScaledVector(Fd0, -0.004 * k).sub(tipL.clone().applyQuaternion(handQuat(Fd0, s, A.palm)));
          else wt = A.grip.clone().addScaledVector(Fd0, -0.095 * hk + 0.018 * k).addScaledVector(pn, -0.022 * hk);
          const d = wt.clone().sub(S), len = d.length();
          const reach = Math.min(len, upperArm + foreArm - 0.001);
          const a = (upperArm * upperArm - foreArm * foreArm + reach * reach) / (2 * reach);
          const hgt = Math.sqrt(Math.max(0, upperArm * upperArm - a * a));
          const dn = d.clone().normalize(), pole = V3(s * 0.55, -1, -0.1);
          const out = pole.sub(dn.clone().multiplyScalar(pole.dot(dn))).normalize();
          E.copy(S).addScaledVector(dn, a).addScaledVector(out, hgt);
          Wr = S.clone().addScaledVector(dn, reach);
          Fd0 = Wr.clone().sub(E).normalize();
        }
        A.short = Math.max(0, wt.distanceTo(S) - (upperArm + foreArm - 0.001)); A.wt = wt;
      }
      S0[s] = S; Ecl[s] = E; Wrl[s] = Wr;
      const nb = leanV(V3(s * 0.045 * k, Yl(0.84), -0.016 * k));
      traps.push(tube([nb.toArray(), [S.x - s * 0.03 * k, S.y + 0.012 * k, S.z - 0.006 * k]], [0.03 * k, (jacket ? 0.04 : 0.037) * k * bw], {}));
    }
    const A_UD = {}, A_FD = {};
    const cover = jacket || sleeves === 'long' ? 1 : sleeves === 'rolled' ? 0.55 : 0.3;
    const sleeveF = {};
    for (const s of [1, -1]) {
      const S = S0[s], E = Ecl[s], Wr = Wrl[s];
      const Ud = E.clone().sub(S).normalize(), Fd = Wr.clone().sub(E).normalize();
      A_UD[s] = Ud; A_FD[s] = Fd;
      let inner = Fd.clone().sub(Ud.clone().multiplyScalar(Fd.dot(Ud)));
      const bend = inner.length();
      if (bend < 0.05) inner = V3(0, 0, 1).sub(Ud.clone().multiplyScalar(Ud.z)); inner.normalize();
      const ease = (jacket ? 0.011 : cover < 1 ? 0.01 : 0.008) * k;
      const m1 = 1 + 0.14 * mass;
      const start = S.clone().add(V3(-s * 0.024 * k, -0.004 * k, 0));
      const f = tube([start.toArray(), S.clone().lerp(E, 0.42).toArray(), E.toArray(), E.clone().lerp(Wr, 0.3).toArray(), Wr.toArray()],
        [0.043 * k * bw * m1 + ease * 0.6, 0.045 * k * m1 + ease, 0.037 * k * m1 + ease, 0.039 * k * m1 + ease, 0.027 * k + ease], { ref: inner.toArray(), k: 0.014 * k });
      const tot = f.len, elbowA = f.cum[2];
      const cutA = cover >= 1 ? tot - (jacket ? 0.026 : 0.012) * k : 0.016 * k + (upperArm + foreArm) * cover;
      const cp = f.at(cutA);
      const famp = (0.003 + 0.0055 * Math.min(1, bend * 1.6)) * k;
      sleeveF[s] = (x, y, z) => {
        let d = f(x, y, z);
        if (d > 0.03 * k) return d;
        const I = f.info, de = I.along - elbowA, dc = cutA - I.along;
        let fold = 0;
        // the elbow: crescents on the inside of the bend, fanning round to the outside
        if (Math.abs(de) < 0.14 * k) fold += famp * Math.exp(-Math.pow(de / (0.065 * k), 2)) * (0.3 + 0.7 * Math.max(0, I.c)) * Math.sin(de * 125 / k + I.s * 1.5 + ph[0]);
        // a long sleeve is longer than the arm, so it stacks in twisting rings above the cuff
        if (cover >= 1 && dc < 0.13 * k) fold += 0.0034 * k * (1 - dc / (0.13 * k)) * Math.sin(dc * 115 / k + I.s * 1.9 + ph[3]);
        // the upper arm: the sleeve hangs from the shoulder in long folds down its inside
        fold += 0.0016 * k * smooth(I.along / (0.06 * k)) * (1 - smooth((I.along - upperArm * 0.8) / (0.08 * k))) * Math.max(0, -I.s * s) * Math.sin(I.c * 4 + I.along * 30 / k + ph[1]);
        if (cover < 1 && dc < 0.06 * k) fold += 0.0018 * k * smooth(1 - dc / (0.05 * k));   // the opening flares a little
        d -= fold + 0.0006 * k * noise(x, y, z, 12);
        return smax(d, (x - cp.p[0]) * cp.d[0] + (y - cp.p[1]) * cp.d[1] + (z - cp.p[2]) * cp.d[2], 0.005 * k);
      };
      sleeveF[s].tube = f; sleeveF[s].cp = cp;
    }
    const armpitY = Math.min(S0[1].y, S0[-1].y) - 0.065 * k;
    const neckC = leanV(V3(0, Yl(0.85), -0.012 * k));
    const clrLo = hemAbs - 0.005 * k, clrHi = Math.max(hemAbs + 0.1 * k, Yl(0.63)) + 0.04 * k;
    const clr = 0.011 * k, vY0 = Yl(0.69);
    const HEMR = 0.012 * k;     // the hem's bead, see torsoF
    // the shirt's body without its sleeves or neck hole: what a hem, a side seam or a vest is laid on
    const shirtBodyF = (x, y, z) => {
      let d = torsoF(x, y, z);
      for (const t of traps) if (t.lb(x, y, z) < d + 0.035 * k) d = smin(d, t(x, y, z), 0.035 * k);
      if (!tucked && y > clrLo && y < clrHi) d = smin(d, smax(trouserF(x, y, z) - clr, hemAbs - y, HEMR) + 0.7 * Math.max(0, y - clrHi + 0.06 * k), 0.008 * k);
      return d;
    };
    const shirtF = (x, y, z) => {
      let d = torsoF(x, y, z);
      for (const t of traps) if (t.lb(x, y, z) < d + 0.035 * k) d = smin(d, t(x, y, z), 0.035 * k);
      const ka = 0.024 * k * smooth((y - armpitY) / (0.07 * k));
      if (sleeveF[1].tube.lb(x, y, z) < d + ka) d = smin(d, sleeveF[1](x, y, z), ka);
      if (sleeveF[-1].tube.lb(x, y, z) < d + ka) d = smin(d, sleeveF[-1](x, y, z), ka);
      // the clearance band is a backstop only: the torso table below the waist is already widened
      // over the trousers (see THE UNTUCKED SHIRT FALLS OVER THE HIPS), so this band rarely shows
      if (!tucked && y > clrLo && y < clrHi) d = smin(d, smax(trouserF(x, y, z) - clr, hemAbs - y, HEMR) + 0.7 * Math.max(0, y - clrHi + 0.06 * k), 0.008 * k);
      // the neck opening and the top
      const nz = z - (neckC.z + (y - neckC.y) * 0.08);
      const hole = Math.max(ell2(x, nz, neckR + 0.004 * k, neckR * 0.96 + 0.004 * k), Yl(0.83) - y);
      d = Math.max(smax(d, -hole, 0.006 * k), y - shirtTop);
      if (jacket && y > vY0) {            // the jacket opens in a V down to the button
        let yy = y, zz = z;
        if (torsoLean) { const dy = y - pivY; yy = pivY + dy * cl + z * sl; zz = -dy * sl + z * cl; }
        const vw = 0.056 * k * clamp01((yy - vY0) / (Yl(0.85) - vY0));
        d = Math.max(d, -Math.max(Math.abs(x) - vw, 0.01 * k - zz));
      }
      return d;
    };

    /* Mesh both garments. UVs are cylindrical in metres: the torso around the body, each sleeve
     * and trouser leg around its own axis, so a plaid meets itself at a seam, as cloth does. */
    const hG = LOW ? 0.03 * k : 0.0128 * k;
    const cyl = (f, R, x, y, z, out) => { f(x, y, z); const I = f.info; out[0] = Math.atan2(I.s, I.c) * R; out[1] = I.along; out[2] = Math.PI * 2 * R; };
    const shirtU = {
      region: (x, y, z) => { const t = torsoF(x, y, z), a = sleeveF[1].tube.lb(x, y, z) < t ? sleeveF[1](x, y, z) : 1, b = sleeveF[-1].tube.lb(x, y, z) < t ? sleeveF[-1](x, y, z) : 1; return t <= a && t <= b ? 0 : a < b ? 1 : -1; },
      uv: (x, y, z, reg, out) => {
        if (reg === 0) { out[0] = Math.atan2(x, z) * 0.15; out[1] = y; out[2] = Math.PI * 2 * 0.15; }
        else cyl(sleeveF[reg].tube, 0.05, x, y, z, out);
      },
    };
    const bb = new THREE.Box3();
    const grow = (v, r0) => { bb.expandByPoint(V3(v.x - r0, v.y - r0, v.z - r0)); bb.expandByPoint(V3(v.x + r0, v.y + r0, v.z + r0)); };
    grow(V3(0, hemAbs, 0), 0.2 * k); grow(V3(0, shirtTop, 0), 0.2 * k);
    for (const s of [1, -1]) { grow(S0[s], 0.1 * k); grow(Ecl[s], 0.07 * k); if (cover >= 0.9) grow(Wrl[s], 0.06 * k); }
    bb.min.y = Math.max(bb.min.y, hemAbs - 0.02 * k); bb.max.y = Math.min(bb.max.y, shirtTop + 0.01 * k);
    // a long sleeve reaches the wrist, which on a short torso or a low hem hangs below the hem: the box
    // clipped it there, and the sleeve ended in a cut at the hem's height (it read as a short sleeve with a gap)
    for (const s of [1, -1]) { const cp = sleeveF[s].cp; bb.min.y = Math.min(bb.min.y, cp.p[1] - 0.06 * k); grow(V3(...cp.p), 0.06 * k); }
    { const sg = sdfMesh(shirtF, [bb.min.x, bb.min.y, bb.min.z, bb.max.x, bb.max.y, bb.max.z], hG, shirtU);
      G.add(LOW ? new THREE.Mesh(sg, shirtM) : new THREE.Mesh(fieldAO(sg, shirtF, k), aoMat(shirtM))); }
    const trU = {
      region: (x, y, z) => { const a = leg[1].trF(x, y, z), b = leg[-1].trF(x, y, z), c = seatRaw(x, y, z); return c < a && c < b ? 0 : a < b ? 1 : -1; },
      uv: (x, y, z, reg, out) => {
        // the seat takes the leg's own mapping on its side, so the weave meets itself only at the centre seam
        cyl(leg[reg === 0 ? (x >= 0 ? 1 : -1) : reg].trTube, 0.07, x, y, z, out);
      },
    };
    bb.makeEmpty();
    for (const s of [1, -1]) { grow(leg[s].hip, 0.13 * k); grow(leg[s].knee, 0.09 * k); grow(leg[s].ankle, 0.1 * k); }
    grow(V3(0, waistTop, 0), 0.19 * k);
    bb.max.y = waistTop + 0.01 * k;
    { const tg = sdfMesh(trouserF, [bb.min.x, bb.min.y, bb.min.z, bb.max.x, bb.max.y, bb.max.z], hG * 1.14, trU);
      G.add(LOW ? new THREE.Mesh(tg, trouserM) : new THREE.Mesh(fieldAO(tg, trouserF, k, 0.45), aoMat(trouserM))); }

    /* GARMENT DETAIL (2026-11-15, "painted-on cloth that has no weave or folds"). A garment that is only
     * its field is a smooth skin with a stump at every opening. Real cloth is cut and sewn: a hem turned
     * up with thickness at every opening, seams that stand a millimetre proud over the shoulder, round
     * the armhole and down the sides, an outseam down each leg, topstitching in gold thread on denim,
     * pocket mouths, belt loops. Each piece is laid on the garment's own field (see onF), so it lies on
     * the cloth and follows its folds. A crowd's low detail person skips all of it. */
    if (!LOW) {
      const threadC = (m) => (jeans && m === trouserM ? 0xc8902e : new THREE.Color(m.map ? 0x8a8478 : m.color).multiplyScalar(0.78).getHex());
      const threadM = (m) => K.mat('p-cloth-thread-' + threadC(m).toString(16), { color: threadC(m), roughness: 0.8 });
      const add = (geo, m) => { if (geo && geo.attributes.position.count) G.add(new THREE.Mesh(geo, m)); };
      const stitchAlong = (S, m, offs) => {
        const S2 = S.map((q) => [q[0] + q[3] * 0.0003 * k, q[1] + q[4] * 0.0003 * k, q[2] + q[5] * 0.0003 * k, q[3], q[4], q[5]]);
        for (const off of offs) add(stitchGeo(S2, off, 0.0034 * k, 0.0024 * k, 0.0009 * k, 0.00045 * k), threadM(m));
      };
      const weltOn = (f, guide, n, m, w, h, stitch) => {
        const S = curveOn(f, guide, n, 0);
        add(weltGeo(S, w || 0.0055 * k, h || 0.0009 * k), m);
        if (stitch) stitchAlong(S, m, stitch);
        return S;
      };
      const Wl = (p) => leanV(V3(p[0], p[1], p[2])).toArray();
      // hems: each sleeve, each trouser leg, and the shirt or jacket where it hangs free
      for (const s of [1, -1]) {
        const sf = sleeveF[s], cp = sf.cp;
        const prof = cover >= 1 ? (jacket ? scaleProf(HEM, 1.4, 1.2) : CUFF) : sleeves === 'rolled' ? ROLL : HEM;
        const h = hemGeo(sf, V3(...cp.p), V3(...cp.d), V3(0, 0, 1), scaleProf(prof, k, k), { inside: 0.04 * k, rMin: 0.02 * k });
        add(h.band, shirtM); add(h.inner, clothIn(shirtM));
        if (cover >= 1 && !jacket) {         // the cuff's button, on its outer side
          const q = onF(sf, [cp.p[0] - cp.d[0] * 0.03 * k + s * 0.055 * k, cp.p[1] - cp.d[1] * 0.03 * k, cp.p[2] - cp.d[2] * 0.03 * k + 0.055 * k], 0.003 * k);
          const bt = new THREE.Mesh(new THREE.CylinderGeometry(0.0038 * k, 0.0038 * k, 0.002 * k, 10), K.mat('p-btn', { color: 0xe9e4d8, roughness: 0.3 }));
          bt.position.set(q[0], q[1], q[2]); bt.quaternion.setFromUnitVectors(V3(0, 1, 0), V3(q[3], q[4], q[5])); G.add(bt);
        }
        const L = leg[s];
        const th = hemGeo(L.trF, V3(...L.hemP), L.tilt.clone(), V3(0, 0, 1), scaleProf(HEM, 1.25 * k, k), { inside: 0.03 * k, rMin: 0.03 * k });
        add(th.band, trouserM); add(th.inner, clothIn(trouserM));
      }
      if (!tucked) {
        const hb = hemGeo(shirtBodyF, leanV(V3(0, hemAbs, 0)), V3(0, -cl, -sl), V3(0, 0, 1), scaleProf(jacket ? scaleProf(HEM, 1.5, 1.3) : HEM, k, k),
          { na: 72, inside: 0.05 * k, rMin: 0.08 * k, off: jacket ? null : (dir) => -0.0025 * k * Math.sin(Math.atan2(dir.x, dir.z) * 3 + ph[3]) });
        add(hb.band, shirtM); add(hb.inner, clothIn(shirtM));
      }
      // seams on the shirt or jacket: over each shoulder, round each armhole, down each side
      for (const s of [1, -1]) {
        const S = S0[s];
        weltOn(shirtF, [Wl([s * 0.055 * k, Yl(0.88), -0.012 * k]), Wl([s * 0.11 * k, Yl(0.865), -0.01 * k]), [S.x + s * 0.012 * k, S.y + 0.075 * k, S.z]], 16, shirtM);
        // the armhole: an arc round the sleeve's root over the top, front, outside and back (the armpit is hidden)
        const tf = sleeveF[s].tube, at = tf.at(0.03 * k), ax = V3(...at.d);
        const n1 = V3(s, 0.4, 0).sub(ax.clone().multiplyScalar(ax.x * s + ax.y * 0.4)).normalize(), n2 = ax.clone().cross(n1), arc = [];
        for (let i = 0; i <= 26; i++) { const a = lerp(-2.15, 2.15, i / 26), dv = n1.clone().multiplyScalar(Math.cos(a)).addScaledVector(n2, Math.sin(a));
          arc.push(onF(shirtF, [at.p[0] + dv.x * 0.085 * k, at.p[1] + dv.y * 0.085 * k, at.p[2] + dv.z * 0.085 * k], 0)); }
        add(weltGeo(arc, 0.0055 * k, 0.0009 * k), shirtM);
        // the side seam, from under the arm to the hem
        const g = [];
        for (let yf = 0.75; yf >= hemY + 0.01; yf -= 0.03) { const rw = ringAt(yf, 0); g.push(Wl([s * (rw.rx + 0.05 * k), Yl(yf), rw.p[2] - 0.006 * k])); }
        if (g.length > 2) weltOn(shirtBodyF, g, 26, shirtM);
      }
      if (!jacket && shirtKind !== 'tee' && shirtKind !== 'polo') {      // the back yoke
        const g = [];
        for (let i = 0; i <= 6; i++) { const x = lerp(-0.125, 0.125, i / 6) * k; g.push(Wl([x, Yl(0.785) + 0.01 * k * Math.pow(x / (0.125 * k), 2), -0.22 * k])); }
        weltOn(shirtF, g, 24, shirtM);
      }
      // trousers: an outseam down each leg, on jeans an inseam too, both with gold topstitching
      for (const s of [1, -1]) {
        const L = leg[s], tf = L.trTube, g = [], gi = [];
        for (let a = 0.03 * k; a < tf.len - 0.04 * k; a += 0.06 * k) { const q = tf.at(a); g.push([q.p[0] + s * 0.16 * k, q.p[1], q.p[2]]); gi.push([q.p[0] - s * 0.12 * k, q.p[1], q.p[2]]); }
        if (g.length > 2) weltOn(trouserF, g, 44, trouserM, 0, 0, jeans ? [0.003 * k] : null);
        if (jeans && gi.length > 5) weltOn(L.trF, gi.slice(3), 32, trouserM, 0, 0, [0.0028 * k, 0.0056 * k]);
      }
      if (tucked) {
        // the pocket mouths and the fly, seen only when the shirt is tucked in
        for (const s of [1, -1]) {
          const g = jeans ? [[s * 0.05 * k, waistTop - 0.018 * k, 0.17 * k], [s * 0.1 * k, waistTop - 0.07 * k, 0.17 * k], [s * 0.2 * k, waistTop - 0.08 * k, 0.05 * k]]
            : [[s * 0.085 * k, waistTop - 0.015 * k, 0.17 * k], [s * 0.13 * k, waistTop - 0.08 * k, 0.15 * k], [s * 0.22 * k, waistTop - 0.15 * k, 0.03 * k]];
          weltOn(trouserF, g, 18, trouserM, 0.0045 * k, 0.0013 * k, jeans ? [0.0045 * k] : null);
        }
        weltOn(trouserF, [[0.004 * k, waistTop - 0.03 * k, 0.17 * k], [0.02 * k, waistTop - 0.09 * k, 0.17 * k], [0.01 * k, crotchY + 0.03 * k, 0.17 * k], [-0.003 * k, crotchY + 0.005 * k, 0.17 * k]],
          16, trouserM, 0.0045 * k, 0.0008 * k, jeans ? [-0.0045 * k] : null);
        if (!jacket) {        // belt loops, over the belt
          const beltY = Yl(0.598), bx = 0.157 * k * hw + 0.006 * k, bzf = (0.103 + bk) * k + 0.006 * k, bzb = 0.095 * k + 0.006 * k, zc0 = 0.002 * k;
          const beltF = (x, y, z) => ell2(x, z - zc0, bx * 1.02, (z - zc0 > 0 ? bzf : bzb) * 1.02);
          for (const a of [-2.25, -1.45, -0.62, 0.62, 1.45, 2.25, Math.PI]) {
            const P = (u, v) => { const aa = a + (u - 0.5) * 0.012 * k / bx; return [Math.sin(aa) * (bx + 0.04 * k), beltY + (0.5 - v) * 0.024 * k, zc0 + Math.cos(aa) * ((Math.cos(aa) > 0 ? bzf : bzb) + 0.04 * k)]; };
            add(slabGeo(beltF, P, 2, 4, 0.0015 * k, 0.0018 * k, { w: 0.012 * k, h: 0.024 * k }), trouserM);
          }
        }
      }
      if (jeans) for (const s of [1, -1]) {      // back patch pockets with their topstitching
        const x0 = s * 0.072 * k, y0 = waistTop - 0.075 * k, pw = 0.125 * k, pH = 0.145 * k;
        const P = (u, v) => [x0 + (u - 0.5) * pw * (1 - 0.1 * v), y0 - v * pH - (v > 0.75 ? (1 - Math.abs(u - 0.5) * 2) * (v - 0.75) / 0.25 * 0.022 * k : 0), -0.24 * k];
        add(slabGeo(trouserF, P, 6, 8, 0.0004 * k, 0.0016 * k, { w: pw, h: pH }), trouserM);
        const rim = [];
        for (const [u, v] of [[0.03, 0.02], [0.03, 0.5], [0.03, 0.75], [0.5, 1], [0.97, 0.75], [0.97, 0.5], [0.97, 0.02]]) rim.push(P(u, v));
        stitchAlong(curveOn(trouserF, rim, 40, 0.0021 * k), trouserM, [0]);
      }
    }

    const body = new THREE.Group();
    const bandG = (y0, y1, rx, rz, zc, a0, a1, th, flare) => {      // a partial collar band, a0..a1 around from the front
        const NA = 28, pos = [], idx = [], uv = [];
        for (let side = 0; side < 2; side++) for (let j = 0; j <= 1; j++) for (let i = 0; i <= NA; i++) {
          const a = lerp(a0, a1, i / NA), o = side ? -th : 0, yy = lerp(y0, y1 + 0.012 * k * Math.pow(Math.sin(a / 2), 2) - 0.01 * k * Math.pow(Math.cos(a / 2), 2), j);
          const fl = (flare || 0) * (1 - j); pos.push(Math.sin(a) * (rx + o + fl), yy, zc + Math.cos(a) * (rz + o + fl)); uv.push(a * rx, yy);
        }
        const Wd = NA + 1;
        for (let side = 0; side < 2; side++) for (let i = 0; i < NA; i++) { const a = side * 2 * Wd + i, b = a + Wd; if (side) idx.push(a, a + 1, b, b, a + 1, b + 1); else idx.push(a, b, a + 1, b, b + 1, a + 1); }
        for (let i = 0; i < NA; i++) { const a = Wd + i, b = 3 * Wd + i; idx.push(a, b, a + 1, b, b + 1, a + 1); }     // the top edge
        // both windings: a thin band is seen from outside and inside, and neither side may cull
        const n0 = idx.length, nv0 = pos.length / 3; pos.push(...pos); uv.push(...uv);
        for (let q = 0; q < n0; q += 3) idx.push(idx[q] + nv0, idx[q + 2] + nv0, idx[q + 1] + nv0);
        // UVs in metres: a cloth with a weave map needs them on every piece, or the merged garment loses them all
        const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.setIndex(idx); g.computeVertexNormals();
        return g;
      };
    // the torso's field in the body group's own (unleaned) frame, for pieces laid on the chest
    const torsoU = torsoLean ? (x, y, z) => { const q = leanV(V3(x, y, z)); return torsoF(q.x, q.y, q.z); } : torsoF;
    const quad = (c00, c10, c01, c11, zOut) => (u, v) => {         // a bilinear patch over the chest, its guides out in front
      const x = lerp(lerp(c00[0], c10[0], u), lerp(c01[0], c11[0], u), v), yf = lerp(lerp(c00[1], c10[1], u), lerp(c01[1], c11[1], u), v);
      return [x, Yl(yf), frontZ(yf) + (zOut || 0.05 * k)];
    };
    // belt with a buckle when the shirt is tucked
    if (!jacket && tucked) {
      const beltY = 0.598;
      const belt = new THREE.Mesh(loft([ring([beltY - 0.009, 0.157, 0.103 + bk, 0.095, 0.002], hw, 0.006 * k), ring([beltY + 0.009, 0.157, 0.103 + bk, 0.095, 0.002], hw, 0.006 * k)],
        { seg: 32, per: 2, n: 2.3, capStart: 'flat', capEnd: 'flat' }), K.mat('p-belt', { color: 0x2b1c12, roughness: 0.5, clearcoat: 0.2 }, true));
      body.add(belt);
      const bz = (0.103 + bk + 0.008) * k;
      const buckle = LOW ? new THREE.Mesh(new THREE.BoxGeometry(0.06 * k, 0.042 * k, 0.008 * k), K.finish.chrome()) : TXT.roundedBox(0.06 * k * (role === 'resident' && shoeStyle === 'western' ? 1.3 : 1), 0.042 * k, 0.008 * k, 0.004 * k, K.finish.chrome());
      buckle.position.set(0, Yl(beltY), bz); body.add(buckle);
    }
    // collar, placket and buttons for button shirts, the V and tie for a suit
    if (shirtKind === 'plaid' || shirtKind === 'button' || shirtKind === 'work' || shirtKind === 'polo') {
      body.add(new THREE.Mesh(bandG(Yl(0.846), Yl(0.866), neckR + 0.006 * k, neckR * 0.97 + 0.006 * k, -0.012 * k, 0.3, Math.PI * 2 - 0.3, 0.003 * k), shirtM));
      // the fall of the collar: a band folded over the stand, flaring at the back and sides
      body.add(new THREE.Mesh(bandG(Yl(0.843), Yl(0.869), neckR + 0.012 * k, neckR * 0.97 + 0.012 * k, -0.012 * k, 0.55, Math.PI * 2 - 0.55, 0.003 * k, 0.019 * k), shirtM));
      /* COLLAR POINTS WITH THICKNESS (2026-11-15): they were flat extruded cards set at an angle in
       * front of the neck, and at a near crop they floated as grey panes. Each is a slab of cloth laid
       * on the chest, rolled up at its top where it turns over the stand, its edges rounded. */
      if (!LOW) for (const s of [1, -1]) {
        const P = quad([s * 0.01 * k, 0.851], [s * 0.048 * k, 0.848], [s * 0.007 * k, 0.838], [s * 0.032 * k, 0.808]);
        body.add(new THREE.Mesh(slabGeo(torsoU, P, 5, 6, 0.0032 * k, 0.0024 * k, { w: 0.045 * k, h: 0.045 * k, bulge: (u, v) => 0.0045 * k * Math.pow(1 - v, 2) }), shirtM));
      } else for (const s of [1, -1]) {
        const pt = TXT.extrude([[0, 0], [s * 0.04 * k, -0.004 * k], [s * 0.024 * k, -0.042 * k], [s * 0.004 * k, -0.011 * k]], 0.003 * k, shirtM, { bevel: false });
        pt.position.set(s * 0.01 * k, Yl(0.862), frontZ(0.84) - 0.001 * k); pt.rotation.set(-0.5, s * 0.25, 0); body.add(pt);
      }
      const btnM = K.mat('p-btn', { color: 0xe9e4d8, roughness: 0.3 });
      for (let b = 0; b < (shirtKind === 'polo' ? 2 : 6); b++) {
        const yf = 0.82 - b * 0.036; if (yf < hemY + 0.01) break;
        const bt = new THREE.Mesh(new THREE.CylinderGeometry(0.0055 * k, 0.0055 * k, 0.003 * k, 10), btnM);
        bt.rotation.x = Math.PI / 2; bt.position.set(0, Yl(yf), frontZ(yf) + 0.0025 * k); body.add(bt);
      }
      // the placket: a raised strip the buttons sit on
      const pl = [];
      for (let yf = 0.835; yf >= hemY + 0.004; yf -= 0.02) pl.push({ p: [0, Yl(yf), frontZ(yf) - 0.001 * k], rx: 0.017 * k, ry: 0.0022 * k });
      if (pl.length > 2 && shirtKind !== 'polo') body.add(new THREE.Mesh(loft(pl, { seg: 8, per: 1, n: 4, ref: [1, 0, 0], capStart: 'flat', capEnd: 'flat' }), shirtM));
      // chest pockets with flaps, never under a vest: the conformed vest of 2026-11-08 sits 5 mm off the shirt and
      // the flaps, which stand proud of it, came through as two dark slots on the chest (they did under the shell too)
      const underVest = o.vest === true || (o.vest === 'auto' || o.vest == null) && role === 'worker';
      // a patch pocket is a slab of the same cloth sewn on, a flap a thicker slab over its mouth with a button
      const flapped = shirtKind === 'plaid' || shirtKind === 'work';
      if ((flapped || shirtKind === 'button') && !underVest) for (const s of (flapped ? [1, -1] : [1])) {
        const cx = s * 0.085 * k, pw = 0.052 * k;
        if (LOW) { const pk = TXT.roundedBox(0.075 * k, 0.014 * k, 0.008 * k, 0.003 * k, shirtM); pk.position.set(cx, Yl(0.755), frontZ(0.755) + 0.0005 * k); body.add(pk); continue; }
        const pocket = (u, v) => { const yb = 0.704 - (shirtKind === 'work' ? 0.008 * (1 - Math.abs(u - 0.5) * 2) * smooth((v - 0.8) / 0.2) : 0); return quad([cx - pw, 0.768], [cx + pw, 0.768], [cx - pw, yb], [cx + pw, yb])(u, v); };
        body.add(new THREE.Mesh(slabGeo(torsoU, pocket, 6, 7, 0.0003 * k, 0.0012 * k, { w: 2 * pw, h: 0.07 * k }), shirtM));
        if (flapped) {
          const fw = pw + 0.003 * k;
          const flap = (u, v) => { const tip = 0.012 * (1 - Math.abs(u - 0.5) * 2) * v; return quad([cx - fw, 0.773], [cx + fw, 0.773], [cx - fw, 0.75 - tip], [cx + fw, 0.75 - tip])(u, v); };
          body.add(new THREE.Mesh(slabGeo(torsoU, flap, 6, 4, 0.0017 * k, 0.0022 * k, { w: 2 * fw, h: 0.03 * k, bulge: (u, v) => 0.0008 * k * v }), shirtM));
          const q = onF(torsoU, [cx, Yl(0.745), frontZ(0.745) + 0.05 * k], 0.0045 * k);
          const bt = new THREE.Mesh(new THREE.CylinderGeometry(0.0045 * k, 0.0045 * k, 0.0022 * k, 10), btnM);
          bt.position.set(q[0], q[1], q[2]); bt.quaternion.setFromUnitVectors(V3(0, 1, 0), V3(q[3], q[4], q[5])); body.add(bt);
        }
      }
    } else if (shirtKind === 'tee' && !jacket) {
      const neck = new THREE.Mesh(new THREE.TorusGeometry(1, 0.07, 6, 36), shirtM);
      neck.rotation.x = Math.PI / 2 - 0.2; neck.scale.set(neckR + 0.006 * k, neckR * 0.97 + 0.006 * k, 0.065 * k); neck.position.set(0, Yl(0.853), -0.006 * k); body.add(neck);
    }
    if (jacket) {
      /* the shirt V, the tie and the lapels follow the jacket's front surface row by row */
      const strip = (rows, mat) => {
        const pos = [], idx = [];
        rows.forEach(([yf, x0, x1, dz], i) => {
          for (let j = 0; j <= 2; j++) {
            const x = lerp(x0, x1, j / 2);
            const hwid = ringAt(yf, 0).rx, bow = 1 - Math.pow(Math.min(1, Math.abs(x) / hwid), 2.2);
            pos.push(x, Yl(yf), frontZ(yf) * Math.pow(Math.max(0, bow), 1 / 2.2) + dz);
          }
          if (i > 0) for (let j = 0; j < 2; j++) { const a0 = (i - 1) * 3 + j, b0 = i * 3 + j; idx.push(a0, a0 + 1, b0, b0, a0 + 1, b0 + 1); }
        });
        const g = new THREE.BufferGeometry();
        g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
        return new THREE.Mesh(g, mat);
      };
      const ys = []; for (let y = 0.852; y >= 0.69; y -= 0.012) ys.push(+y.toFixed(3));
      const vw = (yf) => 0.056 * k * clamp01((yf - 0.69) / 0.16);
      const white = K.mat('p-shirt-white2', { color: capAlb(0xf3f1ec), roughness: 0.7, side: THREE.DoubleSide });
      body.add(strip(ys.map((y) => [y, -vw(y), vw(y), 0.0035 * k]), white));
      const tieM = K.mat('p-tie', { color: tie, roughness: 0.45, sheen: 0.6, sheenColor: 0xffffff, side: THREE.DoubleSide }, true);
      const tw2 = (yf) => yf > 0.835 ? 0.011 * k : lerp(0.03, 0.009, (yf - 0.7) / 0.135) * k;
      const tys = ys.filter((y) => y >= 0.7).concat([0.69]);
      body.add(strip(tys.map((y) => [y, -tw2(y) * (y < 0.7 ? 0.1 : 1), tw2(y) * (y < 0.7 ? 0.1 : 1), 0.0055 * k]), tieM));
      body.add(new THREE.Mesh(bandG(Yl(0.846), Yl(0.872), neckR + 0.0045 * k, neckR * 0.97 + 0.0045 * k, -0.012 * k, 0.1, Math.PI * 2 - 0.1, 0.003 * k), K.mat('p-shirt-white', { color: capAlb(0xf3f1ec), roughness: 0.7 })));
      body.add(new THREE.Mesh(bandG(Yl(0.838), Yl(0.862), neckR + 0.011 * k, neckR * 0.97 + 0.011 * k, -0.012 * k, 0.8, Math.PI * 2 - 0.8, 0.005 * k), shirtM));
      const knot = TXT.roundedBox(0.024 * k, 0.02 * k, 0.012 * k, 0.005 * k, tieM);
      knot.position.set(0, Yl(0.846), frontZ(0.846) + 0.004 * k); body.add(knot);
      // LAPELS WITH A ROLL AND AN EDGE (2026-11-15): they were one-sided strips; a lapel is the jacket's own
      // cloth turned back, so it is a slab laid on the jacket's front, rolled up along its inner edge
      const lap = LOW ? K.mat('p-lapel', { color: new THREE.Color(shirtM.color).multiplyScalar(0.8).getHex(), roughness: 0.5, side: THREE.DoubleSide }) : cloth('suit', new THREE.Color(shirtM.color).multiplyScalar(0.86).getHex());
      const lapW = (y) => (0.012 + 0.03 * clamp01((0.852 - y) / 0.06) * clamp01((y - 0.69) / 0.1)) * k;
      if (LOW) for (const sd of [1, -1]) body.add(strip(ys.map((y) => { const x = vw(y), lw = lapW(y);
        return sd > 0 ? [y, x, x + lw, 0.005 * k] : [y, -x - lw, -x, 0.005 * k]; }), lap));
      else for (const sd of [1, -1]) {
        const P = (u, v) => { const yf = lerp(0.852, 0.692, v), x = sd * (vw(yf) + 0.001 * k + u * lapW(yf)); return [x, Yl(yf), frontZ(yf) + 0.05 * k]; };
        body.add(new THREE.Mesh(slabGeo(torsoU, P, 4, 14, 0.0022 * k, 0.003 * k, { w: 0.04 * k, h: 0.16 * k, bulge: (u, v) => 0.0035 * k * Math.pow(1 - u, 2) * (1 - v * 0.6) }), lap));
      }
      const bt = new THREE.Mesh(new THREE.SphereGeometry(0.008 * k, 10, 6), K.mat('p-sbtn', { color: 0x151515, roughness: 0.3 }));
      bt.scale.z = 0.5; bt.position.set(0, Yl(0.655), frontZ(0.655) + 0.004 * k); body.add(bt);
      const pocket = (x, yf, w, h, th) => {
        if (LOW) { const pk = TXT.roundedBox(0.1 * k, 0.012 * k, 0.01 * k, 0.003 * k, shirtM); pk.position.set(x, Yl(yf), frontZ(yf) * 0.94); body.add(pk); return; }
        const P = (u, v) => { const y = Yl(yf) - v * h; return [x + (u - 0.5) * w, y, frontZ(yf) + 0.05 * k]; };
        body.add(new THREE.Mesh(slabGeo(torsoU, P, 6, 3, 0.0005 * k, th, { w, h, bulge: (u, v) => 0.001 * k * v }), shirtM));
      };
      pocket(0.1 * k, 0.6, 0.12 * k, 0.045 * k, 0.0025 * k); pocket(-0.1 * k, 0.6, 0.12 * k, 0.045 * k, 0.0025 * k);
      pocket(0.095 * k, 0.775, 0.085 * k, 0.016 * k, 0.0016 * k);       // the breast pocket's welt
    }

    // hi-vis vest for workers
    const vest = o.vest === true || (o.vest === 'auto' || o.vest == null) && role === 'worker';
    if (vest) {
      const hv = cloth('hivis', pick(r, [0xc8f02a, 0xf06a1c, 0xd4f230]));
      const refl = K.mat('p-refl', { color: 0xcfd3d6, roughness: 0.25, metalness: 0.6, emissive: 0x303234, emissiveIntensity: 0.3 });
      // THE VEST CLEARS THE SHIRT IT IS WORN OVER, measured (weekly pass 2026-10-22). It was laid a
      // fixed 1.3 cm off the torso table, and an untucked shirt's hem stands further out than that
      // over the hips and the seat, so the shirt broke through the vest's lower edge as a ragged pale
      // fringe on every untucked worker (nos. 54 to 57). Each ring now walks its own superellipse
      // against the shirt's torso field (never the sleeves, which a vest leaves outside its armholes)
      // and grows until every point clears it, capped so a leaning pose the vest does not follow
      // can't balloon it. SUPERSEDED 2026-11-08 by the per-vertex push below, which keeps the clearance
      // and drops the whole-ring growth that stood the vest off the chest.
      // THE VEST IS WORN, NOT STOOD IN (weekly pass 2026-11-08). The rings above, grown as whole rings to clear
      // the widest point of the shirt, made a straight-sided shell that stood off the chest and flared off the
      // hips like a skirt; the emissive term flattened it to one tone. Every panel round of nos. 69, 70 and 71
      // named it ("a rigid shell standing off the torso", "a box vest with a flat orange side", "conform the
      // vest"). So each ring starts at the torso, a V neck is cut in its front, soft drape folds are laid in,
      // and then EACH VERTEX is pushed out of the shirt's torso field to a fabric's clearance, so it follows the
      // body and the shirt where the shirt is and never a ring's widest point. The bands take the same folds and
      // the vest's own push and then lift a band's thickness, so they lie on it and never cut into it.
      const yTop = Yl(0.8), vD = 0.075 * k, vW = 0.085 * k, vFold = 0.0022 * k;
      const conform = (geo, m, vneck, lift) => {
        geo.computeVertexNormals();
        const Pp = geo.attributes.position, Nn = geo.attributes.normal;
        for (let i = 0; i < Pp.count; i++) {
          let x = Pp.getX(i), y = Pp.getY(i), z = Pp.getZ(i);
          if (Math.abs(Nn.getY(i)) > 0.9) continue;                       // the flat cap inside the body
          let nx = Nn.getX(i), nz = Nn.getZ(i); const nl = Math.hypot(nx, nz) || 1; nx /= nl; nz /= nl;
          if (vneck && z > 0) { const t = Math.max(0, 1 - Math.abs(x) / vW); y = Math.min(y, yTop - vD * t); }
          const th = Math.atan2(x, z), u = (y - Yl(0.585)) / (yTop - Yl(0.585));
          const f = vFold * (0.6 * Math.sin(th * 9 + ph[0] + y * 14 / k) + 0.4 * Math.sin(y * 60 / k + th * 3 + ph[1])) * (0.5 + 0.5 * (1 - u));
          x += nx * f; z += nz * f;
          for (let it = 0; it < 8; it++) { const d = torsoF(x, y, z); if (d >= m) break; const push = m - d + 0.0004 * k; x += nx * push; z += nz * push; }
          if (lift) { x += nx * lift; z += nz * lift; }   // a band rides the vest's own surface, a band's thickness out
          Pp.setXYZ(i, x, y, z);
        }
        Pp.needsUpdate = true; geo.computeVertexNormals();
        return geo;
      };
      const vr = [0.585, 0.62, 0.66, 0.7, 0.74, 0.775, 0.8].map((yf) => ringAt(yf, 0.002 * k));
      body.add(new THREE.Mesh(conform(loft(vr, { seg: 48, per: 3, n: 2.2, capStart: 'flat' }), 0.005 * k, true), hv));
      for (const yf of [0.635, 0.695]) body.add(new THREE.Mesh(conform(loft([ringAt(yf - 0.01, 0.002 * k), ringAt(yf + 0.01, 0.002 * k)], { seg: 48, per: 2, n: 2.2 }), 0.005 * k, false, 0.0025 * k), refl));
      // shoulder straps laid over the shirt's own shoulder: each point pushed out of the field
      const settle = (p, m) => { for (let i = 0; i < 12; i++) { const d = shirtF(p[0], p[1], p[2]); if (d > m) break; p[1] += (m - d) + 0.001; } return p; };
      for (const s of [1, -1]) {
        const pts = [[s * 0.1 * k, Yl(0.79), frontZ(0.79) + 0.008 * k], [s * 0.108 * k, Yl(0.82), 0.05 * k], [s * 0.112 * k, Yl(0.83), -0.01 * k],
          [s * 0.108 * k, Yl(0.815), -0.07 * k], [s * 0.1 * k, Yl(0.79), -0.108 * k]];
        const st = loft(pts.map((p, i) => ({ p: i === 0 || i === 4 ? p : settle(p, 0.006 * k), rx: 0.032 * k, ry: 0.005 * k })), { seg: 10, per: 4, n: 3, ref: [1, 0, 0] });
        body.add(new THREE.Mesh(st, hv));
      }
    }

    /* SHOES */
    for (const s of [1, -1]) {
      const L = leg[s];
      const sh = shoe(k, shoeStyle, shoeUpper, soleM, laceM);
      const foot = new THREE.Group(); foot.add(sh);
      const ay = L.ankle.y;
      let pitch = 0;
      if (ay > ankleH + 0.004 * k) {
        const Lt = 0.19 * k;
        let best = 0, err = 1e9;
        for (let a = 0; a < 1.2; a += 0.005) {
          const ty = ay + (-ankleH) * Math.cos(a) - Lt * Math.sin(a);
          if (Math.abs(ty) < err) { err = Math.abs(ty); best = a; }
        }
        pitch = best;
      } else if (L.t.z > 0.2 && pose !== 'kneel') pitch = -0.12;   // a kneel's planted foot stays flat
      foot.position.set(L.ankle.x, L.ankle.y, L.ankle.z);
      sh.position.y = -ankleH;
      foot.rotation.x = pitch; foot.rotation.y = s * 0.08;
      G.add(foot);
    }

    /* ARMS: skin below the sleeve, the hand at the wrist */
    for (const s of [1, -1]) {
      const A = arm[s], S = S0[s], E = Ecl[s], Wr = Wrl[s], Ud = A_UD[s], Fd = A_FD[s];
      const at = (a, b, t) => a.clone().lerp(b, t).toArray();
      const m1 = 1 + 0.14 * mass;
      const armPts = [
        // the two rings under the sleeve stay a little thinner than the arm below it, so an arm
        // swung forward (pose read) never pokes skin through the sleeve cap
        { p: S.clone().addScaledVector(Ud, 0.03 * k).toArray(), rx: 0.029 * k * m1, ry: 0.031 * k * m1 },
        { p: at(S, E, 0.3), rx: 0.036 * k * m1, ry: 0.038 * k * m1 },
        { p: at(S, E, 0.72), rx: 0.04 * k * m1, ry: 0.042 * k * m1 },
        { p: E.toArray(), rx: 0.035 * k * m1, ry: 0.037 * k * m1 },
        { p: at(E, Wr, 0.25), rx: 0.039 * k * m1, ry: 0.036 * k * m1 },
        { p: at(E, Wr, 0.7), rx: 0.031 * k, ry: 0.027 * k },
        { p: Wr.toArray(), rx: 0.026 * k, ry: 0.019 * k }];
      if (cover < 1) G.add(new THREE.Mesh(loft(armPts, { seg: LOW ? 8 : 14, per: 3, ref: [0, 0, 1], capStart: 'flat', capEnd: 'flat' }), skin));
      else G.add(new THREE.Mesh(loft(armPts.slice(-2), { seg: 14, per: 2, ref: [0, 0, 1], capEnd: 'flat' }), skin));   // the wrist
      if (jacket) {     // white shirt cuff shows past the jacket sleeve
        const c = loft([{ p: Wr.clone().addScaledVector(Fd, -0.03 * k).toArray(), rx: 0.031 * k, ry: 0.028 * k }, { p: Wr.clone().addScaledVector(Fd, -0.002 * k).toArray(), rx: 0.03 * k, ry: 0.027 * k }], { seg: 14, per: 2, ref: [0, 0, 1], capEnd: 'flat' });
        G.add(new THREE.Mesh(c, K.mat('p-shirt-white', { color: capAlb(0xf3f1ec), roughness: 0.7 })));
      }
      const hp = A.hand === 'point' || A.press ? 'point' : A.hand === 'hip' || A.hand === 'grip' ? 'fist' : 'relax';
      const hnd = hand(k * (fem ? 0.86 : 0.93) * (1 + 0.05 * mass), s, skin, hp, nailM);
      hnd.quaternion.copy(new THREE.Quaternion().setFromUnitVectors(V3(0, -1, 0), Fd));
      if (A.hand === 'point') hnd.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(V3(0, 1, 0), -s * Math.PI / 2 + s * 0.2));
      if (A.hand === 'hip') hnd.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(V3(0, 1, 0), s * 0.3));
      if (A.hand === 'shade') hnd.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(V3(0, 1, 0), s * Math.PI / 2));
      if (A.hand === 'relax') hnd.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(V3(0, 1, 0), -s * 0.25));
      if (A.hand === 'grip') hnd.quaternion.copy(handQuat(Fd, s, A.palm));   // the palm turned about the forearm to the grip's side
      // a closed hand is turned about the forearm, so the root of its palm no longer lines up with the wrist's
      // section and a ring showed at the wrist at a near crop; it is sunk into the wrist instead
      hnd.position.copy(Wr).addScaledVector(Fd, A.hand === 'grip' && !A.press ? -0.014 * k : 0.004 * k);
      if (A.press && hnd.userData.tip) { hnd.updateMatrix(); A.tipAt = hnd.userData.tip.clone().applyMatrix4(hnd.matrix); }
      G.add(hnd);
    }

    /* NECK and HEAD */
    const Hh = 0.117 * k * (fem ? 0.97 : 1), Wd = 0.074 * k * (fem ? 0.95 : 1) * lerp(0.96, 1.05, r()) * (1 + 0.05 * mass), D = 0.098 * k * (fem ? 0.97 : 1);
    const headC = leanV(V3(0, H + lift - Hh - 0.01 * k, 0.004 * k));
    const neckTop = headC.clone().add(V3(0, -Hh * 0.45, -0.022 * k));
    const nb0 = leanV(V3(0, Yl(0.835), -0.012 * k)), nb1 = leanV(V3(0, Yl(0.862), -0.012 * k));
    const neck = loft([{ p: nb0.toArray(), rx: neckR * 1.12, ry: neckR * 1.08 },
                       { p: nb1.toArray(), rx: neckR, ry: neckR * 0.97 },
                       { p: neckTop.toArray(), rx: neckR * 0.95, ry: neckR * 0.95 }], { seg: 20, per: 3, ref: [1, 0, 0] });
    G.add(new THREE.Mesh(neck, skin));
    const head = new THREE.Group();
    const pivot = new THREE.Group(); pivot.position.copy(neckTop); G.add(pivot);
    head.position.copy(headC).sub(neckTop); pivot.add(head);
    pivot.rotation.set(headPitch + torsoLean, headYaw, 0, 'YXZ');
    const hg = headGeo(Wd, Hh, D, fem);
    head.add(new THREE.Mesh(hg, LOW ? skin : faceM));
    const surf = (ux, uy) => headShape(ux, uy, Math.sqrt(Math.max(0, 1 - ux * ux - uy * uy)), Wd, Hh, D, fem);
    const hatKind = o.hat && o.hat !== 'auto' ? o.hat
      : role === 'worker' ? 'hard'
      : role === 'official' ? (r() < 0.15 ? 'cowboy' : 'none')
      : (() => { const q = r(); return q < 0.25 ? 'cowboy' : q < 0.45 ? 'cap' : 'none'; })();
    // hair style by seed; a hat presses it flat
    const hs = r();
    let style = fem ? (hs < 0.42 ? 'long' : hs < 0.62 ? 'bob' : hs < 0.82 ? 'bun' : 'curlyLong')
      : (hs < 0.3 ? 'crop' : hs < 0.5 ? 'side' : hs < 0.64 ? 'curly' : hs < 0.76 ? 'buzz' : hs < 0.88 ? 'recede' : 'bald');
    if (hatKind !== 'none') { if (!fem) style = style === 'bald' ? 'bald' : 'tight'; else if (style === 'curlyLong' || hatKind === 'hard') style = hatKind === 'hard' ? 'bun' : 'long'; }
    const longHair = style === 'long' || style === 'bob' || style === 'curlyLong';
    /* EARS WITH THEIR FOLDS (2026-11-15). An ear was a squashed sphere with a torus on it. It is a
     * shell: the helix rolled over along the rim from the front of the top round to the lobe, the
     * antihelix inside it forking at the top, the bowl of the concha behind the canal, the tragus in
     * front of it and a soft lobe below, the whole standing a little off the skull and turned back. */
    if (!longHair) for (const s of [1, -1]) {
      const ear = new THREE.Group();
      const E = (x, y, z) => [x * k, y * k, z * k];        // ear frame: x out from the skull, y up, z forward
      const plate = new THREE.Mesh(new THREE.SphereGeometry(1, LOW ? 8 : 16, LOW ? 6 : 12), earM);
      plate.scale.set(0.0042 * k, 0.026 * k, 0.0145 * k); plate.position.set(0.001 * k, 0.002 * k, -0.002 * k); ear.add(plate);
      if (!LOW) {
        const helix = [E(0.001, 0.012, 0.009), E(0.0035, 0.024, 0.004), E(0.005, 0.029, -0.004), E(0.0055, 0.025, -0.0125), E(0.0055, 0.013, -0.0165), E(0.005, 0.0, -0.016), E(0.0045, -0.012, -0.012), E(0.004, -0.019, -0.007)];
        ear.add(new THREE.Mesh(loft(helix.map((p, i) => ({ p, rx: (0.0028 - 0.0002 * Math.abs(i - 3)) * k, ry: (0.0032 - 0.0002 * Math.abs(i - 3)) * k })), { seg: 8, per: 3, capStart: 'dome', capEnd: 'dome', ref: [1, 0, 0] }), earM));
        const anti = [E(0.004, -0.004, -0.009), E(0.0052, 0.006, -0.0105), E(0.0055, 0.015, -0.008), E(0.005, 0.021, -0.002)];
        ear.add(new THREE.Mesh(loft(anti.map((p, i) => ({ p, rx: 0.0022 * k, ry: (0.0026 - i * 0.0003) * k })), { seg: 7, per: 3, capStart: 'dome', capEnd: 'dome', ref: [1, 0, 0] }), earM));
        const crus = [E(0.0052, 0.015, -0.008), E(0.0048, 0.017, 0.0)];
        ear.add(new THREE.Mesh(loft(crus.map((p) => ({ p, rx: 0.0016 * k, ry: 0.0018 * k })), { seg: 6, per: 2, capStart: 'dome', capEnd: 'dome', ref: [1, 0, 0] }), earM));
        const blobE = (p, sc) => { const m = new THREE.Mesh(new THREE.SphereGeometry(1, 10, 8), earM); m.position.set(...p); m.scale.set(...sc.map((v) => v * k)); ear.add(m); };
        blobE(E(0.0035, -0.018, -0.004), [0.0042, 0.0075, 0.0068]);     // the lobe
        blobE(E(0.004, -0.004, 0.0065), [0.0028, 0.004, 0.0028]);       // the tragus
        blobE(E(0.0018, 0.0, -0.0025), [0.0018, 0.0075, 0.0055]);       // the concha's floor, sunk behind the rims
      }
      ear.position.set(s * Wd * 0.93, -Hh * 0.08, -D * 0.1);
      if (s < 0) ear.scale.x = -1;
      ear.rotation.set(-0.12, -s * 0.32, 0);
      head.add(ear);
    }
    // eyes: sclera, iris and pupil caps, lids that give the almond, a lash line, brows
    const irisC = pick(r, [0x22150d, 0x2e1e11, 0x3a2919, 0x262f36, 0x2f3b24, 0x404c56]);
    // a brow is darker than the hair it goes with, and never paler than the skin under it: a blonde or
    // grey head's brows lerped toward the skin printed as two pale bands across the forehead
    // and on deep skin a fair head's brows still sit darker than the skin (2026-11-15: a blond rung on the
    // L* 46 skin printed tan brows paler than the forehead), so the brow is held under 55 percent of it
    const browC = new THREE.Color(hairC).lerp(new THREE.Color(0x221710), 0.72).lerp(new THREE.Color(skinC), 0.08);
    { const lum = (c) => 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b, cap = 0.55 * lum(new THREE.Color(skinC)); if (lum(browC) > cap) browC.multiplyScalar(cap / lum(browC)); }
    const browM = K.mat('p-brow', { color: browC.getHex(), roughness: 0.95 });
    if (LOW) {
      for (const s of [1, -1]) {
        const p = surf(s * 0.33, 0.07);
        const e = new THREE.Mesh(new THREE.SphereGeometry(0.009 * k, 8, 6), K.mat('p-eyelow', { color: 0x2a211c, roughness: 0.4 }));
        e.position.set(p[0], p[1], p[2] - 0.006 * k); e.scale.set(1.2, 0.6, 1); head.add(e);
      }
    } else {
      /* EYES THAT ARE WET AND AT REST (2026-11-15, "dead stare"). The iris sat on the eyeball's own sphere,
       * so its highlight was the sclera's and the eye read as painted; the lids stood wide open round a
       * fully shown iris, which is a stare. Now the cornea bulges a millimetre over the iris as its own
       * glossy dome, so it catches the sky; the iris darkens at its rim; the white is shaded toward its
       * corners; a wet line of tear lies along the lower lid; the upper lid covers the top of the iris
       * and carries its crease, and the lower lid rides up a little with the smile. */
      // EYES THAT DON'T GLOW (2026-11-15): a near white sclera under a mirror coat caught the sky and, at a
      // deck's scale, the two eyes printed as pale lit dots. A white of the eye in a face is a dim
      // ivory in the brow's shadow, and its wet sheen is soft, so the coat is half and rougher.
      const sclera = K.mat('p-eyew', { color: 0x9c8f82, roughness: 0.38, clearcoat: 0.25, clearcoatRoughness: 0.2, vertexColors: true, envMapIntensity: 0.45 }, true);
      const iris = K.mat('p-iris-' + irisC.toString(16), { color: irisC, roughness: 0.25, clearcoat: 0.35, clearcoatRoughness: 0.15, vertexColors: true, envMapIntensity: 0.4 }, true);
      const pupil = K.mat('p-pupil', { color: 0x060504, roughness: 0.25, clearcoat: 0.35, clearcoatRoughness: 0.15, envMapIntensity: 0.4 }, true);
      const lashM = K.mat('p-lash', { color: new THREE.Color(hairC).multiplyScalar(0.45).getHex(), roughness: 0.7 });
      const wetM = K.mat('p-eye-wet', { color: new THREE.Color(skinC).lerp(new THREE.Color(0xc87c78), 0.5).getHex(), roughness: 0.06, clearcoat: 1, clearcoatRoughness: 0.02 }, true);
      // the upper lid sits under the brow's overhang, so it is a shade deeper and a touch redder than the face
      const lidM = skinMat('p-skin-lid', { color: new THREE.Color(skinC).multiplyScalar(0.84).lerp(new THREE.Color(0x8a4a44), 0.06).getHex() });
      const R = 0.0118 * k;
      // the white: shaded toward its corners and a touch pink there, as a real one is
      const scG = new THREE.SphereGeometry(R, 20, 12), scC = [];
      for (let i = 0; i < scG.attributes.position.count; i++) {
        const fz = smooth(scG.attributes.position.getZ(i) / R * 1.2), up = smooth(scG.attributes.position.getY(i) / R * 2 + 0.6), l = (0.6 + 0.4 * fz) * (1 - 0.25 * up);
        scC.push(l * (1 + 0.04 * (1 - fz)), l * (1 - 0.02 * (1 - fz)), l * (1 - 0.04 * (1 - fz)));
      }
      scG.setAttribute('color', new THREE.Float32BufferAttribute(scC, 3));
      // the cornea's dome over the iris: a cap of a smaller sphere meeting the eyeball at the iris's rim
      const aI = 0.45, Rc = R * 0.62, aC = Math.asin(Math.sin(aI) * R / Rc), zC = R * Math.cos(aI) - Rc * Math.cos(aC);
      const dome = (a1, rr, rings) => {
        const gg = new THREE.SphereGeometry(Rc * rr, 28, rings, 0, Math.PI * 2, 0, a1); gg.rotateX(Math.PI / 2); gg.translate(0, 0, zC);
        const cc = [];
        for (let i = 0; i < gg.attributes.position.count; i++) {
          const px = gg.attributes.position.getX(i), py = gg.attributes.position.getY(i), rad = Math.hypot(px, py) / (Rc * Math.sin(aC));
          const ang = Math.atan2(py, px), fleck = 0.88 + 0.12 * Math.sin(ang * 23) * Math.sin(ang * 7 + 1.3);
          const l = (rad > 0.82 ? lerp(1, 0.45, smooth((rad - 0.82) / 0.18)) : lerp(1.15, 1, smooth(rad / 0.6))) * fleck;
          cc.push(l, l, l);
        }
        gg.setAttribute('color', new THREE.Float32BufferAttribute(cc, 3));
        return gg;
      };
      for (const s of [1, -1]) {
        const p = surf(s * 0.33, 0.065);
        const C = V3(p[0] - s * 0.001 * k, p[1], p[2] - 0.64 * R);
        const eye = new THREE.Group(); eye.position.copy(C); eye.rotation.y = s * 0.1; head.add(eye);
        eye.add(new THREE.Mesh(scG, sclera));
        const ei = new THREE.Mesh(dome(aC, 1, 6), iris); ei.rotation.y = -s * 0.1; eye.add(ei);
        const pu = new THREE.SphereGeometry(Rc * 1.003, 16, 3, 0, Math.PI * 2, 0, aC * 0.4); pu.rotateX(Math.PI / 2); pu.translate(0, 0, zC);
        const ep = new THREE.Mesh(pu, pupil); ep.rotation.y = -s * 0.1; eye.add(ep);
        // lids: two sheets on a sphere just over the eyeball, meeting at the corners; the upper covers the iris's top
        const aM = 1.12, up = (a) => { const t = Math.abs(a + s * 0.12) / aM; return t >= 1 ? 0 : 0.31 * Math.pow(Math.cos(t * Math.PI / 2), 0.62) + 0.02; };
        const dn = (a) => { const t = Math.abs(a - s * 0.1) / aM; return t >= 1 ? 0 : -(0.27 * Math.pow(Math.cos(t * Math.PI / 2), 0.9) + 0.02); };
        const sheet = (edge, far, rr, crease) => {
          const NA = 18, NB = 6, pos = [], idx = [];
          for (let j = 0; j <= NB; j++) for (let i = 0; i <= NA; i++) {
            const a = lerp(-1.35, 1.35, i / NA), t = j / NB, be = lerp(edge(Math.max(-aM, Math.min(aM, a))), far, Math.pow(t, 1.4));
            const inA = Math.abs(a) < aM ? 1 : 0;
            // the lid's thickness at its margin, and on the upper lid the crease where it folds under the brow
            const rad = R * (rr + 0.06 * (1 - t) * inA - (crease ? 0.045 * Math.exp(-Math.pow((t - 0.42) / 0.12, 2)) * Math.cos(a * 0.9) : 0) + (crease ? 0.03 * smooth((t - 0.55) / 0.3) : 0));
            pos.push(rad * Math.cos(be) * Math.sin(a), rad * Math.sin(be), rad * Math.cos(be) * Math.cos(a));
          }
          for (let j = 0; j < NB; j++) for (let i = 0; i < NA; i++) { const a = j * (NA + 1) + i, b = a + NA + 1; idx.push(a, b, a + 1, b, b + 1, a + 1); }
          const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
          const nn = g.attributes.normal, pp = g.attributes.position;
          if (nn.getX(9) * pp.getX(9) + nn.getY(9) * pp.getY(9) + nn.getZ(9) * pp.getZ(9) < 0) { const ix = g.index.array; for (let q = 0; q < ix.length; q += 3) { const t = ix[q]; ix[q] = ix[q + 1]; ix[q + 1] = t; } g.computeVertexNormals(); }
          return g;
        };
        eye.add(new THREE.Mesh(sheet(up, 1.3, 1.1, true), lidM));
        eye.add(new THREE.Mesh(sheet(dn, -1.2, 1.07, false), skin));
        const margin = (edge, rr, rad, mat, fwd) => {
          const pts = [];
          for (let i = 0; i <= 12; i++) { const a = lerp(-aM * 0.97, aM * 0.97, i / 12), be = edge(a); const q = R * rr;
            pts.push({ p: [q * Math.cos(be) * Math.sin(a), q * Math.sin(be) + fwd, q * Math.cos(be) * Math.cos(a)], rx: rad * Math.sin(Math.PI * (0.08 + 0.84 * i / 12)), ry: rad * Math.sin(Math.PI * (0.08 + 0.84 * i / 12)) }); }
          return new THREE.Mesh(loft(pts, { seg: 5, per: 1, capStart: 'dome', capEnd: 'dome', ref: [0, 0, 1] }), mat);
        };
        eye.add(margin(up, 1.14, 0.0016 * k, lidM, 0));
        eye.add(margin(up, 1.17, 0.0008 * k, lashM, 0.0004 * k));
        eye.add(margin(dn, 1.1, 0.0009 * k, skin, 0));
        eye.add(margin((a) => dn(a) + 0.035, 1.03, 0.00055 * k, wetM, 0));      // the tear line on the lower lid
        eye.add(margin(dn, 1.12, 0.0004 * k, lashM, -0.0003 * k));               // the lower lashes, sparse and fine
      }
      /* BROWS LIE IN THE SKIN (2026-11-15): a round tube read as a painted stroke with its own highlight.
       * A brow is short hair lying flat, so it is a flat stroke sunk at its edges into the ridge, with a
       * thinner one over its upper half for the hairs that lie across, thick at the inner end. */
      for (const s of [1, -1]) for (let st = 0; st < 2; st++) {
        const pts = [], t0 = st ? 0.06 : 0, t1 = st ? 0.82 : 1, dy = st ? 0.006 : 0;
        for (let i = 0; i <= 8; i++) {
          const t = lerp(t0, t1, i / 8), ux = lerp(0.1, 0.6, t), uy = 0.185 + 0.05 * Math.sin(Math.PI * Math.min(1, t * 1.25)) - 0.03 * t + dy * (1 - 0.6 * t);
          // ON the skin along its normal, half sunk. A +z offset left the outer end, where the brow
          // ridge turns toward the temple, standing proud of the skin with its own shadow, which
          // read as a sticker (weekly pass 2026-10-03, no. 36 to 38's "mask-like", "crude" face).
          const q = surf(s * ux, uy), e = 0.01, qa = surf(s * ux + e, uy), qb = surf(s * ux - e, uy), qc = surf(s * ux, uy + e), qd = surf(s * ux, uy - e);
          const nrm = V3(qa[0] - qb[0], qa[1] - qb[1], qa[2] - qb[2]).cross(V3(qc[0] - qd[0], qc[1] - qd[1], qc[2] - qd[2])).normalize();
          if (nrm.z < 0) nrm.negate();
          const off = (st ? 0.00005 : -0.0001) * k;
          pts.push({ p: [q[0] + nrm.x * off, q[1] + nrm.y * off, q[2] + nrm.z * off], rx: 0.0006 * k, ry: lerp(fem ? 0.0024 : 0.0031, 0.0009, t) * k * (st ? 0.55 : 1) });
        }
        head.add(new THREE.Mesh(loft(pts, { seg: 6, per: 2, capStart: 'dome', capEnd: 'dome', ref: [0, 0, 1] }), browM));
      }
      // lips: a patch that lies on the sculpted mouth, a shade deeper than the skin; the corners turn up
      // with the mouth line, the upper lip is darker than the lower (it faces down), the parting darkest
      const lipC = new THREE.Color(skinC).multiplyScalar(0.84).lerp(new THREE.Color(0x8f4a48), fem ? 0.3 : 0.2);
      const lipM = skinMat('p-lip-' + lipC.getHexString(), { color: lipC.getHex(), roughness: 0.55, clearcoat: 0.08, clearcoatRoughness: 0.45, vertexColors: true });
      const lift = (x) => 0.03 * Math.pow(Math.min(1.3, Math.abs(x) / 0.22), 2);
      const topL = (x) => -0.445 - 0.06 * Math.pow(Math.abs(x) / 0.21, 2) + 0.008 * Math.exp(-Math.pow((Math.abs(x) - 0.055) / 0.03, 2)) + lift(x);
      const botL = (x) => -0.595 + 0.075 * Math.pow(Math.abs(x) / 0.21, 2) + lift(x);
      const NXL = 20, NYL = 12, lp = [], li = [], lc = [];
      for (let j = 0; j <= NYL; j++) for (let i = 0; i <= NXL; i++) {
        const x = lerp(-0.21, 0.21, i / NXL), y = lerp(topL(x), botL(x), j / NYL), q = surf(x, y);
        lp.push(q[0], q[1], q[2] + 0.0005 * k);
        const mo = y - (-0.515 + lift(x)), part = Math.exp(-Math.pow(mo / 0.012, 2)), edge = Math.pow(Math.abs(x) / 0.21, 4);
        const l = (mo > 0 ? 0.86 : 1.02) * (1 - 0.5 * part) * (1 - 0.25 * edge);
        lc.push(l, l * 0.98, l * 0.98);
      }
      for (let j = 0; j < NYL; j++) for (let i = 0; i < NXL; i++) { const a = j * (NXL + 1) + i, b = a + NXL + 1; li.push(a, b, a + 1, b, b + 1, a + 1); }
      const lg = new THREE.BufferGeometry(); lg.setAttribute('position', new THREE.Float32BufferAttribute(lp, 3)); lg.setAttribute('color', new THREE.Float32BufferAttribute(lc, 3)); lg.setIndex(li); lg.computeVertexNormals();
      head.add(new THREE.Mesh(lg, lipM));
    }
    // hair
    if (style !== 'bald') {
      const hT = hairThickness(style, k, ph[0]), hatted = hatKind !== 'none';
      // under a hat the crown is pressed flat, so no hair can come through the hat
      head.add(new THREE.Mesh(shellGeo(hg, hatted ? (ux, uy, uz) => Math.min(hT(ux, uy, uz), lerp(0.009, 0.0035, smooth((uy - 0.1) / 0.3)) * k) : hT, hT.tone), hairM));
      if (longHair) head.add(new THREE.Mesh(curtainGeo(Wd, Hh, D, k, style === 'bob' ? 0.95 : 1.75 + 0.35 * r(), style === 'curlyLong', ph[1], headPitch, [neckTop.y - headC.y, neckTop.z - headC.z]), hairM));
      if (style === 'bun') {
        const bg = new THREE.SphereGeometry(1, LOW ? 10 : 20, LOW ? 8 : 14), bc = [];
        for (let i = 0; i < bg.attributes.position.count; i++) { const q = bg.attributes.position, v = 0.78 + 0.14 * (0.5 + 0.5 * q.getY(i)) + 0.08 * Math.sin(Math.atan2(q.getX(i), q.getZ(i)) * 5 + q.getY(i) * 3); bc.push(v, v * 0.985, v * 0.97); }
        bg.setAttribute('color', new THREE.Float32BufferAttribute(bc, 3));
        const bun = new THREE.Mesh(bg, hairM);
        if (hatKind === 'none') { bun.scale.set(0.036 * k, 0.03 * k, 0.034 * k); bun.position.set(0, Hh * 0.55, -D * 0.9); }
        else { bun.scale.set(0.03 * k, 0.026 * k, 0.03 * k); bun.position.set(0, -Hh * 0.3, -D * 1.02); }
        head.add(bun);
      }
    }
    // facial hair on some men: a shell over the jaw or the lip
    if (!fem && r() < 0.32) {
      const full = r() < 0.5;
      const beard = (ux, uy, uz) => {
        if (uz < -0.35) return -0.002;
        const ax = Math.abs(ux);
        const lipGap = g2(ux, uy + 0.52, 0.2, 0.06);
        const mo = 1 - Math.max(Math.abs(uy + 0.415) / 0.045, ax / 0.24);
        if (full) {
          /* THE CHEEK LINE (weekly pass 2026-10-16). It sat at -0.08 - 0.18 * (1 - ax), which climbs
           * to the cheekbone at the side and to the nose at the middle, so a full beard covered half
           * the face and met the sideburn as one shell: at full size a mask. A beard's cheek line
           * runs from the foot of the sideburn down to the corner of the mouth, and the moustache
           * is its own patch over the lip, so the two are drawn apart and the larger wins. */
          const line = lerp(-0.47, -0.12, clamp01((ax - 0.24) / 0.64));
          const m = Math.min(line - uy, uz + 0.3);
          const jaw = m < 0 ? -0.002 : 0.0055 * k * smooth(m / 0.15) * (1 - 0.9 * lipGap) - (lipGap > 0.5 ? 0.004 : 0);
          return Math.max(jaw, mo < 0 ? -0.002 : 0.0045 * k * smooth(mo / 0.3));
        }
        return mo < 0 ? -0.002 : 0.0035 * k * smooth(mo / 0.3);
      };
      head.add(new THREE.Mesh(shellGeo(hg, beard, (ux, uy, uz) => 0.8 + 0.1 * Math.sin(ux * 41 + uy * 23) * Math.sin(uy * 37 + uz * 19)), hairM));
    }
    if (hatKind !== 'none') {
      let hatC = hatKind === 'hard' ? pick(r, [0xf2f0ea, 0xf2c200, 0xf07a1a, 0xf2f0ea])
        : hatKind === 'cowboy' ? pick(r, [0xd9c69a, 0x2a2420, 0xc2b49a, 0x6b4e34, 0xe0d2a8])
        : pick(r, [0x1f2b44, 0x7a1f25, 0x3f4a3a, 0x6e6656, 0x2a2a2a, 0xb05a22]);
      // `hatColor` sets it (no. 61's judges asked for "a dark cloth" cap and the frame had no way to give
      // one). The seeded pick is still drawn first, so a person's other choices don't move. The cap's pale
      // stone was the brightest thing beside the face, where the mannequin read lives; a worn khaki took it.
      if (o.hatColor != null) hatC = o.hatColor;
      const hm = hatKind === 'hard' ? K.mat('p-hard', { color: capAlb(hatC, 0.75), roughness: 0.3, clearcoat: 0.8, clearcoatRoughness: 0.2 }, true)
        : K.mat('p-hat', { color: capAlb(hatC), roughness: hatKind === 'cowboy' && (hatC === 0xd9c69a || hatC === 0xe0d2a8) ? 0.85 : 0.75 });
      head.add(hat(hatKind, Wd * 1.03, D * 1.03, Hh * (hatKind === 'cowboy' ? 0.36 : hatKind === 'cap' ? 0.32 : 0.36), hm, r, Hh));
    }
    // the body pieces lean with the torso, about the hips
    const bodyPivot = new THREE.Group(); bodyPivot.position.y = pivY; body.position.y = -pivY;
    bodyPivot.add(body); bodyPivot.rotation.x = torsoLean; G.add(bodyPivot);
    const M = mergeByMaterial(G);
    M.userData.height = H; M.userData.role = role; M.userData.pose = pose;
    // COORDINATES FOR A SEATED OR GRIPPING PERSON, published only when asked (weekly pass 2026-11-12). K.make
    // recentres a model's footprint unless it publishes attach points, and a person's default call must
    // land where it always has, so only sit_drive and `hands` keep their origin and say where things are.
    if (pose === 'sit_drive' || gripAt) {
      const hipC = leg[1].hip.clone().add(leg[-1].hip).multiplyScalar(0.5);
      let seatY = hipC.y;
      M.traverse((m) => {
        if (!m.isMesh || (m.material !== trouserM && m.material !== AOM.get(trouserM))) return;
        const pa = m.geometry.attributes.position;
        for (let i = 0; i < pa.count; i++) {
          if (Math.abs(pa.getX(i)) < hipX && Math.abs(pa.getZ(i) - hipC.z) < 0.06 * k) seatY = Math.min(seatY, pa.getY(i));
        }
      });
      head.updateWorldMatrix(true, false);
      M.userData.attach = {
        hip: hipC.toArray(), seat: [0, seatY, hipC.z], eye: head.localToWorld(V3(0, 0, D)).toArray(),
        hands: [1, -1].map((s) => arm[s].hand === 'grip'
          ? (arm[s].press && arm[s].tipAt
            ? { grip: arm[s].grip.toArray(), press: true, tip: arm[s].tipAt.toArray(), reached: arm[s].tipAt.toArray(), short: +arm[s].tipAt.distanceTo(arm[s].grip).toFixed(3) }
            : { grip: arm[s].grip.toArray(), reached: Wrl[s].clone().add(arm[s].grip).sub(arm[s].wt).toArray(), short: +arm[s].short.toFixed(3) }) : null),
      };
    }
    return M;
  }
  /* ---- a crowd ------------------------------------------------------------------------- */
  K.define('crowd', {
    size: [8, 1.9, 5.3],
    options: { seed: 1, n: 12, detail: 'auto', area: [8, 5], roles: ['resident'], poses: ['stand', 'stand', 'stand', 'walk', 'walk', 'hands_on_hips', 'look_up'], face: null },
    note: 'N seeded people over area [w, d] (centred), min 0.65 m apart. face: [x, z] a point they turn toward, in the frame of the crowd itself (kept in place, not recentred), else roughly +z.',
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
      // `face` is a point in the crowd's own frame, so K.make must not recentre the frame under it
      if (o.face) G.userData.keepOrigin = true;
      return G;
    },
  });
}
