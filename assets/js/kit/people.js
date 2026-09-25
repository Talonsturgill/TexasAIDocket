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
    } else if (kind === 'strands') {        // hair albedo: fine streaks along v
      x.fillStyle = '#ffffff'; x.fillRect(0, 0, N, N);
      for (let i = 0; i < 260; i++) {
        const px = r() * N, w = 1 + r() * 3, v = r();
        x.fillStyle = v < 0.7 ? 'rgba(0,0,0,' + (0.03 + r() * 0.08) + ')' : 'rgba(255,255,255,' + (0.02 + r() * 0.05) + ')';
        x.fillRect(px, 0, w, N); x.fillRect(px - N, 0, w, N);
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
  function cloth(kind, color, extra) {
    extra = extra || {};
    const nm = normTex('crumple'), ns = (s) => ({ normalMap: nm, normalScale: new THREE.Vector2(s * 0.3, s * 0.3) });
    if (kind === 'denim') return K.mat('p-denim', Object.assign({ color: 0xffffff, roughness: 0.9, map: clothTex('denim', color, 0, 0), sheen: 0.35, sheenColor: 0x8899bb, sheenRoughness: 0.7 }, ns(0.5)), true);
    if (kind === 'plaid') return K.mat('p-plaid', Object.assign({ color: 0xffffff, roughness: 0.88, map: clothTex('plaid', color, extra.b, extra.c), sheen: 0.3, sheenColor: 0xffffff, sheenRoughness: 0.8 }, ns(0.45)), true);
    if (kind === 'suit') return K.mat('p-suit', Object.assign({ color, roughness: 0.6, sheen: 0.5, sheenColor: 0x9a9a9a, sheenRoughness: 0.5 }, ns(0.22)), true);
    if (kind === 'hivis') return K.mat('p-hivis', Object.assign({ color, roughness: 0.7, emissive: color, emissiveIntensity: 0.12 }, ns(0.3)));
    return K.mat('p-cloth', Object.assign({ color, roughness: extra.rough || 0.86, sheen: 0.4, sheenColor: 0xffffff, sheenRoughness: 0.75 }, ns(0.45)), true);
  }

  /* ---- palettes ------------------------------------------------------------------------- */
  const SKIN = [0xf0d0b6, 0xe6b894, 0xd9a47c, 0xc98f64, 0xb37550, 0x9a6040, 0x7d4a2f, 0x5e3522, 0x4a2a1b];
  const HAIR = [0x1d1510, 0x2a1d14, 0x3b2a1c, 0x5a3d25, 0x7a5a38, 0x9a8468, 0x8c8a86, 0xc2bdb4, 0x121010];
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
    if (uz > -0.1) {
      const fz = smooth((uz + 0.1) / 0.5), ax = Math.abs(ux);
      let dz = 0;
      dz += (fem ? 0.045 : 0.07) * g2(ax, uy - 0.2, 0.55, 0.075) * (ax < 0.62 ? 1 : 0.4);    // brow ridge
      dz -= 0.02 * g2(ux, uy - 0.1, 0.06, 0.05);                                          // nose root
      dz -= 0.115 * g2(ax - 0.33, uy - 0.06, 0.15, 0.1);                                   // eye sockets
      const tn = Math.pow(clamp01((0.08 - uy) / 0.38), 1.3), below = uy < -0.3 ? Math.exp(-Math.pow((uy + 0.3) / 0.075, 2)) : 1;
      dz += (fem ? 0.18 : 0.21) * tn * below * g2(ux, 0, 0.06 + 0.045 * tn, 1);             // bridge to tip
      dz += 0.03 * g2(ux, uy + 0.27, 0.065, 0.05);                                         // tip
      dz += 0.035 * g2(ax - 0.09, uy + 0.3, 0.04, 0.04);                                    // alae
      dz -= 0.012 * g2(ax - 0.05, uy + 0.34, 0.022, 0.018);                                // nostrils
      dz -= 0.012 * g2(ux, uy + 0.41, 0.025, 0.04);                                        // philtrum
      dz += 0.05 * g2(ux, uy + 0.465, 0.19, 0.035);                                        // upper lip
      dz -= 0.03 * g2(ux, uy + 0.515, 0.2, 0.013);                                         // mouth line
      dz += (fem ? 0.05 : 0.042) * g2(ux, uy + 0.56, 0.16, 0.035);                         // lower lip
      dz -= 0.022 * g2(ax - 0.22, uy + 0.515, 0.04, 0.04);                                 // mouth corners
      dz -= 0.025 * g2(ux, uy + 0.655, 0.16, 0.035);                                       // under the lip
      dz += 0.06 * g2(ux, uy + 0.82, 0.3, 0.13);                                           // chin
      dz += 0.045 * g2(ax - 0.55, uy + 0.05, 0.16, 0.12);                                  // cheekbones
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
    const warm = 0.1 * g2(ax - 0.45, uy + 0.2, 0.2, 0.18) + 0.08 * g2(ux, uy + 0.22, 0.09, 0.12) + 0.05 * g2(ux, uy - 0.35, 0.3, 0.15);
    g -= warm * 0.9 * f; b -= warm * 1.1 * f;
    const sock = 0.1 * g2(ax - 0.33, uy - 0.08, 0.13, 0.08) * f;
    r -= sock * 0.9; g -= sock; b -= sock * 0.8;
    if (!fem) { const beard = 0.08 * smooth((-uy - 0.35) / 0.2) * smooth((uz + 0.35) / 0.3) * (1 - 0.8 * g2(ux, uy + 0.52, 0.2, 0.06)); r -= beard; g -= beard; b -= beard * 0.8; }
    const fade = smooth((uy + 0.95) / 0.2);               // back to exactly the body skin at the neck
    return [lerp(1, r, fade), lerp(1, g, fade), lerp(1, b, fade)];
  }
  const HEADS = new Map();
  function headGeo(W, Hh, D, fem) {
    const key = [W, Hh, D, fem, LOW].map((v) => (typeof v === 'number' ? v.toFixed(4) : v)).join('|');
    if (HEADS.has(key)) return HEADS.get(key);
    const NLON = LOW ? 24 : 62, NLAT = LOW ? 18 : 50;
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
    g.userData.dirs = dirs;
    HEADS.set(key, g);
    return g;
  }
  /* A shell grown off the head along its normals by thickness T(ux, uy, uz) metres. Where T is
   * negative the shell sinks under the skin, so a hairline or a beard edge tapers rather than
   * ending in a step; triangles entirely under the skin are dropped. */
  function shellGeo(head, T) {
    const p = head.attributes.position, n = head.attributes.normal, dirs = head.userData.dirs, idx = head.index.array;
    const cnt = p.count, out = new Float32Array(cnt * 3), th = new Float32Array(cnt);
    for (let i = 0; i < cnt; i++) {
      const t = T(dirs[i * 3], dirs[i * 3 + 1], dirs[i * 3 + 2]);
      th[i] = t;
      const tt = Math.max(t, -0.0015);
      out[i * 3] = p.getX(i) + n.getX(i) * tt; out[i * 3 + 1] = p.getY(i) + n.getY(i) * tt; out[i * 3 + 2] = p.getZ(i) + n.getZ(i) * tt;
    }
    const keep = [];
    for (let i = 0; i < idx.length; i += 3) if (th[idx[i]] > 0 || th[idx[i + 1]] > 0 || th[idx[i + 2]] > 0) keep.push(idx[i], idx[i + 1], idx[i + 2]);
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(out, 3));
    g.setAttribute('uv', head.attributes.uv.clone());
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
    return (ux, uy, uz) => {
      const az = Math.abs(Math.atan2(ux, uz));
      const m = uy - lineAt(tab, az);                 // > 0 inside the hair
      const top = smooth((uy - 0.35) / 0.55) * (1 - 0.35 * smooth((Math.abs(ux) - 0.5) / 0.4)), front = smooth(uz / 0.6) * smooth((uy - 0.35) / 0.35), crown = smooth((uy + 0.2) / 0.7);
      let T;
      switch (style) {
        case 'buzz': T = 0.0032; break;
        case 'tight': T = 0.004 + 0.002 * top; break;
        case 'side': T = 0.0045 + 0.004 * crown + 0.02 * top + 0.009 * front - 0.007 * g2(ux - 0.4, uy - 0.62, 0.045, 0.4) * smooth(uz / 0.3 + 0.3) + 0.004 * top * smooth(-ux / 0.4); break;
        case 'curly': T = 0.006 + 0.005 * crown + 0.016 * top + 0.003 * (Math.sin(ux * 31 + ph) * Math.sin(uy * 29 + ph * 2) + Math.sin(uz * 27 + uy * 13 + ph * 3)); break;
        case 'recede': T = 0.004 + 0.004 * top; break;
        case 'bun': T = 0.004 + 0.004 * top; break;
        case 'long': case 'bob': T = 0.007 + 0.004 * crown + 0.01 * top + 0.004 * front; break;
        case 'curlyLong': T = 0.012 + 0.016 * top + 0.004 * (Math.sin(ux * 27 + ph) * Math.sin(uy * 25 + ph * 2) + Math.sin(uz * 23 + ph * 3)); break;
        default: T = 0.004 + 0.004 * crown + 0.014 * top + 0.008 * front;      // crop
      }
      T *= k;
      // a continuous taper through the hairline, so the edge is cut by interpolation, not by the grid
      if (m < -0.06) return -0.002;
      return lerp(-0.002, T + 0.0006 * Math.sin(ux * 90 + uy * 40 + ph), smooth((m + 0.02) / (uz > 0.3 ? 0.22 : 0.12)));
    };
  }
  /* Hair that falls below the skull: a thick curved slab around the back and sides of the
   * head, open at the face, its lower edge layered. Rows run down, columns around. */
  function curtainGeo(W, Hh, D, k, len, curly, ph) {
    const NU = LOW ? 14 : 44, NV = LOW ? 6 : 22, th = (curly ? 0.034 : 0.024) * k;
    const yTop = 0.05 * Hh, pos = [], uv = [], idx = [];
    const a0 = 1.4, a1 = Math.PI * 2 - 1.4;                      // around the back
    const R = (a, y, s) => {                                      // outer radius factor
      const fl = smooth((-y) / (Hh * 1.2));
      return 1.05 + 0.1 * fl + (curly ? 0.1 : 0) * fl + s * 0.012 * Math.sin(a * 23 + ph) + (curly ? 0.04 * Math.sin(a * 11 + y * 60 + ph) : 0);
    };
    const bot = (a) => -len * Hh + 0.035 * k * Math.sin(a * 5 + ph) + 0.02 * k * Math.sin(a * 13 + ph * 2) - 0.04 * k * Math.cos(a - Math.PI) * (len > 1.3 ? 1 : 0);
    const put = (a, y, inner, v) => {
      const edge = smooth((a - a0) / 0.5) * smooth((a1 - a) / 0.5);
      const tt = th * (0.55 + 0.45 * edge) * (1 - 0.45 * v);
      const rr = R(a, y, 1) - (1 - edge) * 0.03 - (inner ? tt / (W * 1.1) : 0);
      const x = Math.sin(a) * W * rr, z = Math.cos(a) * D * rr * 0.97 - 0.1 * D * smooth(-y / Hh);
      pos.push(x, y, z); uv.push(a / (Math.PI * 2), -y / 0.25);
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
    g.setIndex(idx);
    g.computeVertexNormals();
    return g;
  }

  /* ---- hands -------------------------------------------------------------------------- */
  // Built hanging down -y with the palm facing -s*x (toward the body) and the thumb to +z.
  function hand(k, s, mat, pose) {
    const g = new THREE.Group();
    const L = 0.1 * k, B = 0.084 * k, T = 0.03 * k;
    const palm = loft([
      { p: [0, 0.012 * k, 0], rx: T * 0.42, ry: B * 0.34 },
      { p: [0, -0.03 * k, 0.002 * k], rx: T * 0.58, ry: B * 0.47 },
      { p: [-s * 0.003 * k, -0.07 * k, 0], rx: T * 0.52, ry: B * 0.5 },
      { p: [-s * 0.006 * k, -L + 0.004 * k, 0], rx: T * 0.42, ry: B * 0.47 }], { seg: 16, per: 3, n: 2.4, ref: [1, 0, 0], capStart: 'flat', capEnd: 'dome', domeK: 0.5 });
    g.add(new THREE.Mesh(palm, mat));
    const fl = [0.072, 0.082, 0.077, 0.062];
    if (LOW) {      // a mitten: the fingers as one curled blade
      g.add(new THREE.Mesh(loft([{ p: [0, -L + 0.01 * k, 0], rx: T * 0.38, ry: B * 0.45 }, { p: [-s * 0.022 * k, -L - 0.055 * k, 0], rx: T * 0.3, ry: B * 0.4 }],
        { seg: 12, capEnd: 'dome', ref: [1, 0, 0] }), mat));
    }
    for (let f = 0; f < (LOW ? 0 : 4); f++) {
      const zz = (0.029 - f * 0.0195) * k * (B / (0.084 * k));
      const len = fl[f] * k;
      // at rest the fingers curl more toward the little finger: a relaxed hand, not a paddle
      const curl = pose === 'point' ? (f === 0 ? 0.05 : 1.45) : pose === 'fist' ? 1.4 : 0.62 + f * 0.13;
      const ctrl = [];
      let px = -s * 0.006 * k, py = -L + 0.004 * k, a = 0.08;
      const rad = (0.0104 - f * 0.0006) * k;
      ctrl.push({ p: [px, py + 0.01 * k, zz], rx: rad * 1.05, ry: rad * 0.9 });
      const segs = [0.45, 0.31, 0.24];
      for (let j = 1; j <= 3; j++) {
        a += curl * (j === 1 ? 0.28 : j === 2 ? 0.4 : 0.32);
        const seg = len * segs[j - 1];
        py -= Math.cos(a) * seg; px += -s * Math.sin(a) * seg;
        ctrl.push({ p: [px, py, zz * (1 - j * 0.06)], rx: rad * (1 - j * 0.1), ry: rad * 0.85 * (1 - j * 0.1) });
      }
      g.add(new THREE.Mesh(loft(ctrl, { seg: 7, per: 2, capStart: 'flat', capEnd: 'dome', ref: [0, 0, 1] }), mat));
    }
    // thumb from the heel of the palm, forward and down, resting along the index finger
    const th = [[-s * 0.004, -0.02, 0.028], [-s * 0.012, -0.045, 0.05], [-s * 0.022, -0.07, 0.058], [-s * 0.032, -0.088, 0.056]]
      .map((q, i) => ({ p: q.map((v) => v * k), rx: (0.0125 - i * 0.0011) * k, ry: (0.0105 - i * 0.001) * k }));
    if (pose === 'point' || pose === 'fist') th.forEach((t, i) => { t.p[0] -= s * 0.012 * k * i; t.p[2] -= 0.008 * k * i; });
    g.add(new THREE.Mesh(loft(th, { seg: 8, per: 2, capStart: 'flat', capEnd: 'dome' }), mat));
    return g;
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
               hat: 'auto', vest: 'auto', skin: null, shirt: null, trousers: null, detail: 'full' },
    note: 'Articulated adult 1.60 to 1.90 m by seed, slim to heavy. role resident|worker|official; pose stand|walk|point|hands_on_hips|look_up; toward -1|1 for point; hat auto|none|cap|cowboy|hard; build auto|male|female. Shirt and trousers are single distance-field garments with folds; hair has volume by style.',
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
    const skin = K.mat('p-skin', { color: skinC, roughness: 0.6, sheen: 0.25, sheenColor: 0xff9f86, sheenRoughness: 0.5, clearcoat: 0.04, clearcoatRoughness: 0.5 }, true);
    const hairC = pick(r, HAIR);
    const hairM = K.mat('p-hair', { color: new THREE.Color(hairC).multiplyScalar(1.12).getHex(), roughness: 0.55, map: clothTex('strands', 0, 0, 0),
      sheen: 0.55, sheenColor: 0xfff1e0, sheenRoughness: 0.45 }, true);
    const faceM = K.mat('p-face', { color: skinC, roughness: 0.6, sheen: 0.25, sheenColor: 0xff9f86, sheenRoughness: 0.5, clearcoat: 0.04, clearcoatRoughness: 0.5, vertexColors: true }, true);
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
      if (shirtKind === 'plaid') { const pl = pick(r, PLAIDS); shirtM = cloth('plaid', pl[0], { b: pl[1], c: pl[2] }); }
      else shirtM = cloth('cloth', o.shirt != null ? o.shirt : shirtKind === 'work' ? pick(r, [0x6d7f8f, 0x8a7a5c, 0x3f4f5f, 0xb0a58a]) : pick(r, SHIRTS));
      jeans = role === 'worker' ? r() < 0.7 : r() < 0.65;
      if (o.trousers != null) jeans = false;
      trouserM = o.trousers != null ? cloth('cloth', o.trousers, { rough: 0.9 }) : jeans ? cloth('denim', pick(r, DENIM)) : cloth('cloth', pick(r, KHAKI), { rough: 0.9 });
    }
    const shoeStyle = role === 'official' ? 'dress' : role === 'worker' ? 'work' : pick(r, ['sneaker', 'sneaker', 'western', 'boot']);
    const shoeUpper = shoeStyle === 'sneaker' ? K.mat('p-sneak', { color: pick(r, [0xe8e6e0, 0x2a2c30, 0x5a6470, 0xb8b2a6]), roughness: 0.78, sheen: 0.3, sheenColor: 0xffffff, sheenRoughness: 0.8 }, true)
      : shoeStyle === 'dress' ? K.mat('p-dress', { color: 0x151312, roughness: 0.3, clearcoat: 0.7, clearcoatRoughness: 0.25 }, true)
      : shoeStyle === 'work' ? K.mat('p-work', { color: pick(r, [0x7a5530, 0x5a3e24, 0x8f6a3e]), roughness: 0.72, sheen: 0.3, sheenColor: 0xd8b890, sheenRoughness: 0.7 }, true)
      : K.mat('p-leather', { color: pick(r, [0x5a3a22, 0x3a2416, 0x7a4c2a, 0x2a1d16]), roughness: 0.48, clearcoat: 0.35, clearcoatRoughness: 0.45 }, true);
    const soleM = shoeStyle === 'sneaker' ? K.mat('p-sole', { color: 0xefece6, roughness: 0.65 }) : shoeStyle === 'work' ? K.mat('p-lug', { color: 0x2a211b, roughness: 0.8 }) : K.mat('p-dsole', { color: 0x3a2a1e, roughness: 0.6 });
    const laceM = shoeStyle === 'sneaker' ? K.mat('p-lace', { color: 0xf1efe9, roughness: 0.85 }) : shoeStyle === 'dress' ? K.mat('p-lace-d', { color: 0x141210, roughness: 0.7 }) : K.mat('p-lace-w', { color: 0xa08058, roughness: 0.85 });

    /* SKELETON (y from the ground, before the stance lift). */
    const Y = (f) => f * H;
    const shoulderX = 0.178 * k * bw, hipX = 0.086 * k * hw;
    const upperArm = 0.305 * k, foreArm = 0.25 * k, thigh = 0.43 * k, shin = 0.425 * k;
    const hipY = Y(0.52);
    const n3 = (x, y, z) => V3(x, y, z).normalize();
    const arm = {}, leg = {};
    let headPitch = 0, headYaw = 0, torsoLean = 0;
    for (const s of [1, -1]) {
      arm[s] = { u: n3(s * 0.13, -1, 0.02), f: n3(s * 0.06, -1, 0.2), hand: 'relax' };
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
      if (r() < 0.6) arm[s] = { u: n3(s * 0.55, 0.15, 0.55), f: n3(-s * 0.75, 0.45, -0.1), hand: 'shade' };
    }
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
        let fold = 0;
        if (dk > -0.08 * k && dk < 0.08 * k) fold += 0.0026 * k * Math.exp(-Math.pow(dk / (0.045 * k), 2)) * Math.max(0, -I.c) * Math.sin(dk * 170 / k + I.s * 1.5 + ph[1]);
        if (de < 0.13 * k) fold += 0.0038 * k * (1 - de / (0.13 * k)) * (0.6 + 0.4 * I.c) * Math.sin(de * 150 / k + I.s * 1.2 + ph[2]);
        if (jeans && I.along < 0.2 * k && I.c > 0) fold += 0.0014 * k * I.c * Math.sin((I.along + I.s * 0.05) * 160 / k) * (1 - I.along / (0.2 * k));
        d -= fold + 0.0009 * k * noise(x, y, z, 13);
        // hem: a plane, lower at the back
        d = Math.max(d, (x - hemP[0]) * tilt.x + (y - hemP[1]) * tilt.y + (z - hemP[2]) * tilt.z);
        return d;
      };
      L.trTube = f;
    }
    const crotchY = Yl(0.5);
    const trouserF = (x, y, z) => {
      let d = seatRaw(x, y, z) - 0.0006 * k * noise(x, y, z, 12);
      const ks = 0.04 * k * smooth((y - crotchY) / (0.06 * k));
      const a = leg[1].trTube.lb(x, y, z) < d + ks ? leg[1].trF(x, y, z) : 1, b = leg[-1].trTube.lb(x, y, z) < d + ks ? leg[-1].trF(x, y, z) : 1;
      d = smin(d, smin(a, b, 0.008 * k), ks);
      return Math.max(d, y - waistTop);
    };

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
      if (!tucked && !jacket && u < 0.14 * k) {              // the hem hangs in soft vertical drapes
        const th = Math.atan2(x, zz);
        fold += 0.004 * k * Math.pow(1 - u / (0.14 * k), 2) * Math.sin(th * 5 + ph[0]);
      }
      if (tucked && u > 0.012 * k && u < 0.09 * k) {         // blousing above the belt
        const th = Math.atan2(x, zz), b = Math.sin(Math.PI * (u - 0.012 * k) / (0.078 * k));
        fold += b * (0.0028 * k + 0.0014 * k * Math.sin(th * 7 + ph[1]));
      }
      const side = smooth((Math.abs(x) / (0.16 * k) - 0.62) / 0.3);
      const yw = Yl(0.63);
      if (Math.abs(yy - yw) < 0.09 * k) fold += fa * 0.0016 * k * side * Math.exp(-Math.pow((yy - yw) / (0.035 * k), 2)) * Math.sin((yy - yw) * 150 / k + ph[2]);
      fold += fa * 0.0011 * k * noise(x, yy, zz, 11);
      d -= fold;
      // the hem, with a little life in it
      const hem = hemAbs + (tucked ? 0 : 0.0025 * k * Math.sin(Math.atan2(x, zz) * 3 + ph[3]));
      return Math.max(d, hem - yy);
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
      const famp = (0.0028 + 0.0045 * Math.min(1, bend * 1.6)) * k;
      sleeveF[s] = (x, y, z) => {
        let d = f(x, y, z);
        if (d > 0.03 * k) return d;
        const I = f.info, de = I.along - elbowA, dc = cutA - I.along;
        let fold = 0;
        if (Math.abs(de) < 0.12 * k) fold += famp * Math.exp(-Math.pow(de / (0.055 * k), 2)) * (0.3 + 0.7 * Math.max(0, I.c)) * Math.sin(de * 180 / k + I.s * 1.3 + ph[0]);
        if (cover >= 1 && dc < 0.1 * k) fold += 0.0022 * k * (1 - dc / (0.1 * k)) * Math.sin(dc * 150 / k + I.s * 1.1 + ph[3]);
        if (cover < 1 && dc < 0.07 * k) fold += (sleeves === 'rolled' ? 0.006 : 0.004) * k * smooth(1 - dc / (0.05 * k));   // the opening flares, the roll thickens
        if (I.along > 0.01 * k && I.along < 0.03 * k) fold -= 0.0011 * k * Math.exp(-Math.pow((I.along - 0.02 * k) / (0.004 * k), 2));   // shoulder seam
        d -= fold + 0.0009 * k * noise(x, y, z, 12);
        return Math.max(d, (x - cp.p[0]) * cp.d[0] + (y - cp.p[1]) * cp.d[1] + (z - cp.p[2]) * cp.d[2]);
      };
      sleeveF[s].tube = f;
    }
    const armpitY = Math.min(S0[1].y, S0[-1].y) - 0.065 * k;
    const neckC = leanV(V3(0, Yl(0.85), -0.012 * k));
    const clrLo = hemAbs - 0.005 * k, clrHi = Math.max(hemAbs + 0.1 * k, Yl(0.63));
    const clr = 0.011 * k, vY0 = Yl(0.69);
    const shirtF = (x, y, z) => {
      let d = torsoF(x, y, z);
      for (const t of traps) if (t.lb(x, y, z) < d + 0.035 * k) d = smin(d, t(x, y, z), 0.035 * k);
      const ka = 0.024 * k * smooth((y - armpitY) / (0.07 * k));
      if (sleeveF[1].tube.lb(x, y, z) < d + ka) d = smin(d, sleeveF[1](x, y, z), ka);
      if (sleeveF[-1].tube.lb(x, y, z) < d + ka) d = smin(d, sleeveF[-1](x, y, z), ka);
      if (!tucked && y > clrLo && y < clrHi) d = Math.min(d, Math.max(trouserF(x, y, z) - clr, hemAbs - y, y - clrHi));
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
    const hG = LOW ? 0.03 * k : 0.0158 * k;
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
    G.add(new THREE.Mesh(sdfMesh(shirtF, [bb.min.x, bb.min.y, bb.min.z, bb.max.x, bb.max.y, bb.max.z], hG, shirtU), shirtM));
    const trU = {
      region: (x, y, z) => { const a = leg[1].trF(x, y, z), b = leg[-1].trF(x, y, z), c = seatRaw(x, y, z); return c < a && c < b ? 0 : a < b ? 1 : -1; },
      uv: (x, y, z, reg, out) => {
        if (reg === 0) { out[0] = Math.atan2(x, z) * 0.15; out[1] = y; out[2] = Math.PI * 2 * 0.15; }
        else cyl(leg[reg].trTube, 0.07, x, y, z, out);
      },
    };
    bb.makeEmpty();
    for (const s of [1, -1]) { grow(leg[s].hip, 0.13 * k); grow(leg[s].knee, 0.09 * k); grow(leg[s].ankle, 0.1 * k); }
    grow(V3(0, waistTop, 0), 0.19 * k);
    bb.max.y = waistTop + 0.01 * k;
    G.add(new THREE.Mesh(sdfMesh(trouserF, [bb.min.x, bb.min.y, bb.min.z, bb.max.x, bb.max.y, bb.max.z], hG * 1.14, trU), trouserM));

    const body = new THREE.Group();
    const bandG = (y0, y1, rx, rz, zc, a0, a1, th, flare) => {      // a partial collar band, a0..a1 around from the front
        const NA = 28, pos = [], idx = [];
        for (let side = 0; side < 2; side++) for (let j = 0; j <= 1; j++) for (let i = 0; i <= NA; i++) {
          const a = lerp(a0, a1, i / NA), o = side ? -th : 0, yy = lerp(y0, y1 + 0.012 * k * Math.pow(Math.sin(a / 2), 2) - 0.01 * k * Math.pow(Math.cos(a / 2), 2), j);
          const fl = (flare || 0) * (1 - j); pos.push(Math.sin(a) * (rx + o + fl), yy, zc + Math.cos(a) * (rz + o + fl));
        }
        const Wd = NA + 1;
        for (let side = 0; side < 2; side++) for (let i = 0; i < NA; i++) { const a = side * 2 * Wd + i, b = a + Wd; if (side) idx.push(a, a + 1, b, b, a + 1, b + 1); else idx.push(a, b, a + 1, b, b + 1, a + 1); }
        for (let i = 0; i < NA; i++) { const a = Wd + i, b = 3 * Wd + i; idx.push(a, b, a + 1, b, b + 1, a + 1); }     // the top edge
        // both windings: a thin band is seen from outside and inside, and neither side may cull
        const n0 = idx.length, nv0 = pos.length / 3; pos.push(...pos);
        for (let q = 0; q < n0; q += 3) idx.push(idx[q] + nv0, idx[q + 2] + nv0, idx[q + 1] + nv0);
        const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
        return g;
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
      for (const s of [1, -1]) {        // collar points folded down on the chest
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
      if (shirtKind === 'plaid' || shirtKind === 'work') for (const s of [1, -1]) {   // chest pockets with flaps
        const pk = TXT.roundedBox(0.075 * k, 0.014 * k, 0.008 * k, 0.003 * k, shirtM);
        pk.position.set(s * 0.085 * k, Yl(0.755), frontZ(0.755) + 0.0005 * k); body.add(pk);
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
      const white = K.mat('p-white2', { color: 0xf3f1ec, roughness: 0.7, side: THREE.DoubleSide });
      body.add(strip(ys.map((y) => [y, -vw(y), vw(y), 0.0035 * k]), white));
      const tieM = K.mat('p-tie', { color: tie, roughness: 0.45, sheen: 0.6, sheenColor: 0xffffff, side: THREE.DoubleSide }, true);
      const tw2 = (yf) => yf > 0.835 ? 0.011 * k : lerp(0.03, 0.009, (yf - 0.7) / 0.135) * k;
      const tys = ys.filter((y) => y >= 0.7).concat([0.69]);
      body.add(strip(tys.map((y) => [y, -tw2(y) * (y < 0.7 ? 0.1 : 1), tw2(y) * (y < 0.7 ? 0.1 : 1), 0.0055 * k]), tieM));
      body.add(new THREE.Mesh(bandG(Yl(0.846), Yl(0.872), neckR + 0.0045 * k, neckR * 0.97 + 0.0045 * k, -0.012 * k, 0.1, Math.PI * 2 - 0.1, 0.003 * k), K.mat('p-white', { color: 0xf3f1ec, roughness: 0.7 })));
      body.add(new THREE.Mesh(bandG(Yl(0.838), Yl(0.862), neckR + 0.011 * k, neckR * 0.97 + 0.011 * k, -0.012 * k, 0.8, Math.PI * 2 - 0.8, 0.005 * k), shirtM));
      const knot = TXT.roundedBox(0.024 * k, 0.02 * k, 0.012 * k, 0.005 * k, tieM);
      knot.position.set(0, Yl(0.846), frontZ(0.846) + 0.004 * k); body.add(knot);
      const lap = K.mat('p-lapel', { color: new THREE.Color(shirtM.color).multiplyScalar(0.8).getHex(), roughness: 0.5, side: THREE.DoubleSide });
      for (const sd of [1, -1]) body.add(strip(ys.map((y) => { const x = vw(y); const lw = (0.012 + 0.03 * clamp01((0.852 - y) / 0.06) * clamp01((y - 0.69) / 0.1)) * k;
        return sd > 0 ? [y, x, x + lw, 0.005 * k] : [y, -x - lw, -x, 0.005 * k]; }), lap));
      const bt = new THREE.Mesh(new THREE.SphereGeometry(0.008 * k, 10, 6), K.mat('p-sbtn', { color: 0x151515, roughness: 0.3 }));
      bt.scale.z = 0.5; bt.position.set(0, Yl(0.655), frontZ(0.655) + 0.004 * k); body.add(bt);
      const pocket = (x, yf) => { const pk = TXT.roundedBox(0.1 * k, 0.012 * k, 0.01 * k, 0.003 * k, shirtM); pk.position.set(x, Yl(yf), frontZ(yf) * 0.94); body.add(pk); };
      pocket(0.1 * k, 0.58); pocket(-0.1 * k, 0.58);
    }

    // hi-vis vest for workers
    const vest = o.vest === true || (o.vest === 'auto' || o.vest == null) && role === 'worker';
    if (vest) {
      const hv = cloth('hivis', pick(r, [0xc8f02a, 0xf06a1c, 0xd4f230]));
      const refl = K.mat('p-refl', { color: 0xcfd3d6, roughness: 0.25, metalness: 0.6, emissive: 0x303234, emissiveIntensity: 0.3 });
      const vr = [0.585, 0.62, 0.66, 0.7, 0.74, 0.775, 0.8].map((yf) => ringAt(yf, 0.013 * k));
      body.add(new THREE.Mesh(loft(vr, { seg: 32, per: 3, n: 2.2, capStart: 'flat' }), hv));
      for (const yf of [0.635, 0.695]) body.add(new THREE.Mesh(loft([ringAt(yf - 0.01, 0.016 * k), ringAt(yf + 0.01, 0.016 * k)], { seg: 32, per: 2, n: 2.2 }), refl));
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
      } else if (L.t.z > 0.2) pitch = -0.12;
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
        { p: S.clone().addScaledVector(Ud, 0.03 * k).toArray(), rx: 0.034 * k * m1, ry: 0.036 * k * m1 },
        { p: at(S, E, 0.3), rx: 0.04 * k * m1, ry: 0.042 * k * m1 },
        { p: at(S, E, 0.72), rx: 0.04 * k * m1, ry: 0.042 * k * m1 },
        { p: E.toArray(), rx: 0.035 * k * m1, ry: 0.037 * k * m1 },
        { p: at(E, Wr, 0.25), rx: 0.039 * k * m1, ry: 0.036 * k * m1 },
        { p: at(E, Wr, 0.7), rx: 0.031 * k, ry: 0.027 * k },
        { p: Wr.toArray(), rx: 0.026 * k, ry: 0.019 * k }];
      if (cover < 1) G.add(new THREE.Mesh(loft(armPts, { seg: LOW ? 8 : 14, per: 3, ref: [0, 0, 1], capStart: 'flat', capEnd: 'flat' }), skin));
      else G.add(new THREE.Mesh(loft(armPts.slice(-2), { seg: 14, per: 2, ref: [0, 0, 1], capEnd: 'flat' }), skin));   // the wrist
      if (jacket) {     // white shirt cuff shows past the jacket sleeve
        const c = loft([{ p: Wr.clone().addScaledVector(Fd, -0.03 * k).toArray(), rx: 0.031 * k, ry: 0.028 * k }, { p: Wr.clone().addScaledVector(Fd, -0.002 * k).toArray(), rx: 0.03 * k, ry: 0.027 * k }], { seg: 14, per: 2, ref: [0, 0, 1], capEnd: 'flat' });
        G.add(new THREE.Mesh(c, K.mat('p-white', { color: 0xf3f1ec, roughness: 0.7 })));
      }
      const hp = A.hand === 'point' ? 'point' : A.hand === 'hip' ? 'fist' : 'relax';
      const hnd = hand(k * (fem ? 0.86 : 0.93) * (1 + 0.05 * mass), s, skin, hp);
      hnd.quaternion.copy(new THREE.Quaternion().setFromUnitVectors(V3(0, -1, 0), Fd));
      if (A.hand === 'point') hnd.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(V3(0, 1, 0), -s * Math.PI / 2 + s * 0.2));
      if (A.hand === 'hip') hnd.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(V3(0, 1, 0), s * 0.3));
      if (A.hand === 'shade') hnd.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(V3(0, 1, 0), s * Math.PI / 2));
      if (A.hand === 'relax') hnd.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(V3(0, 1, 0), -s * 0.25));
      hnd.position.copy(Wr).addScaledVector(Fd, 0.004 * k);
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
    // ears, under long hair they are not built at all
    if (!longHair) for (const s of [1, -1]) {
      const ear = new THREE.Mesh(new THREE.SphereGeometry(1, LOW ? 6 : 12, LOW ? 4 : 9), skin);
      ear.scale.set(0.008 * k, 0.028 * k, 0.018 * k); ear.position.set(s * Wd * 0.93, -Hh * 0.08, -D * 0.1); ear.rotation.set(-0.15, s * 0.22, 0);
      head.add(ear);
      if (!LOW) {
        const rim = new THREE.Mesh(new THREE.TorusGeometry(1, 0.22, 6, 18, Math.PI * 1.45), skin);
        rim.scale.set(0.016 * k, 0.025 * k, 0.016 * k); rim.position.set(s * (Wd * 0.93 + 0.004 * k), -Hh * 0.06, -D * 0.1);
        rim.rotation.set(0, s * Math.PI / 2 + s * 0.22, -Math.PI * 0.2); head.add(rim);
      }
    }
    // eyes: sclera, iris and pupil caps, lids that give the almond, a lash line, brows
    const irisC = pick(r, [0x2a1a10, 0x3b2615, 0x4a3520, 0x2f3b45, 0x3b4a2c, 0x5a6a78]);
    const browM = K.mat('p-brow', { color: new THREE.Color(hairC).lerp(new THREE.Color(skinC), 0.35).getHex(), roughness: 0.85 });
    if (LOW) {
      for (const s of [1, -1]) {
        const p = surf(s * 0.33, 0.07);
        const e = new THREE.Mesh(new THREE.SphereGeometry(0.009 * k, 8, 6), K.mat('p-eyelow', { color: 0x2a211c, roughness: 0.4 }));
        e.position.set(p[0], p[1], p[2] - 0.006 * k); e.scale.set(1.2, 0.6, 1); head.add(e);
      }
    } else {
      const sclera = K.mat('p-eyew', { color: 0xd9d0c4, roughness: 0.25, clearcoat: 1, clearcoatRoughness: 0.05 }, true);
      const iris = K.mat('p-iris-' + irisC.toString(16), { color: irisC, roughness: 0.3, clearcoat: 1, clearcoatRoughness: 0.03 }, true);
      const pupil = K.mat('p-pupil', { color: 0x060504, roughness: 0.2, clearcoat: 1, clearcoatRoughness: 0.03 }, true);
      const lashM = K.mat('p-lash', { color: new THREE.Color(hairC).multiplyScalar(0.5).getHex(), roughness: 0.7 });
      const R = 0.0118 * k;
      for (const s of [1, -1]) {
        const p = surf(s * 0.33, 0.065);
        const C = V3(p[0] - s * 0.001 * k, p[1], p[2] - 0.64 * R);
        const eye = new THREE.Group(); eye.position.copy(C); eye.rotation.y = s * 0.1; head.add(eye);
        eye.add(new THREE.Mesh(new THREE.SphereGeometry(R, 16, 10), sclera));
        const ir = new THREE.SphereGeometry(R * 1.004, 20, 4, 0, Math.PI * 2, 0, 0.45); ir.rotateX(Math.PI / 2);
        const ei = new THREE.Mesh(ir, iris); ei.rotation.y = -s * 0.1; eye.add(ei);
        const pu = new THREE.SphereGeometry(R * 1.007, 14, 2, 0, Math.PI * 2, 0, 0.2); pu.rotateX(Math.PI / 2);
        const ep = new THREE.Mesh(pu, pupil); ep.rotation.y = -s * 0.1; eye.add(ep);
        // lids: two sheets on a sphere just over the eyeball, meeting at the corners
        const aM = 1.12, up = (a) => { const t = Math.abs(a + s * 0.12) / aM; return t >= 1 ? 0 : 0.36 * Math.pow(Math.cos(t * Math.PI / 2), 0.65) + 0.02; };
        const dn = (a) => { const t = Math.abs(a - s * 0.1) / aM; return t >= 1 ? 0 : -(0.33 * Math.pow(Math.cos(t * Math.PI / 2), 0.85) + 0.02); };
        const sheet = (edge, far, rr) => {
          const NA = 16, NB = 4, pos = [], idx = [];
          for (let j = 0; j <= NB; j++) for (let i = 0; i <= NA; i++) {
            const a = lerp(-1.35, 1.35, i / NA), be = lerp(edge(Math.max(-aM, Math.min(aM, a))), far, Math.pow(j / NB, 1.4)), rad = R * (rr + 0.05 * (1 - j / NB) * (Math.abs(a) < aM ? 1 : 0));
            pos.push(rad * Math.cos(be) * Math.sin(a), rad * Math.sin(be), rad * Math.cos(be) * Math.cos(a));
          }
          for (let j = 0; j < NB; j++) for (let i = 0; i < NA; i++) { const a = j * (NA + 1) + i, b = a + NA + 1; idx.push(a, b, a + 1, b, b + 1, a + 1); }
          const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
          const nn = g.attributes.normal, pp = g.attributes.position;
          if (nn.getX(9) * pp.getX(9) + nn.getY(9) * pp.getY(9) + nn.getZ(9) * pp.getZ(9) < 0) { const ix = g.index.array; for (let q = 0; q < ix.length; q += 3) { const t = ix[q]; ix[q] = ix[q + 1]; ix[q + 1] = t; } g.computeVertexNormals(); }
          return g;
        };
        eye.add(new THREE.Mesh(sheet(up, 1.3, 1.1), skin));
        eye.add(new THREE.Mesh(sheet(dn, -1.2, 1.07), skin));
        const margin = (edge, rr, rad, mat, fwd) => {
          const pts = [];
          for (let i = 0; i <= 12; i++) { const a = lerp(-aM * 0.97, aM * 0.97, i / 12), be = edge(a); const q = R * rr;
            pts.push({ p: [q * Math.cos(be) * Math.sin(a), q * Math.sin(be) + fwd, q * Math.cos(be) * Math.cos(a)], rx: rad * Math.sin(Math.PI * (0.08 + 0.84 * i / 12)), ry: rad * Math.sin(Math.PI * (0.08 + 0.84 * i / 12)) }); }
          return new THREE.Mesh(loft(pts, { seg: 5, per: 1, capStart: 'dome', capEnd: 'dome', ref: [0, 0, 1] }), mat);
        };
        eye.add(margin(up, 1.14, 0.0016 * k, skin, 0));
        eye.add(margin(up, 1.17, 0.00075 * k, lashM, 0.0004 * k));
        eye.add(margin(dn, 1.1, 0.0009 * k, skin, 0));
      }
      // brows follow the ridge, thick at the inner end
      for (const s of [1, -1]) {
        const pts = [];
        for (let i = 0; i <= 8; i++) {
          const t = i / 8, ux = lerp(0.1, 0.6, t), uy = 0.185 + 0.05 * Math.sin(Math.PI * Math.min(1, t * 1.25)) - 0.03 * t;
          const q = surf(s * ux, uy);
          pts.push({ p: [q[0], q[1], q[2] + 0.0012 * k], rx: 0.0011 * k, ry: lerp(fem ? 0.0026 : 0.0034, 0.001, t) * k });
        }
        head.add(new THREE.Mesh(loft(pts, { seg: 8, per: 2, capStart: 'dome', capEnd: 'dome', ref: [0, 0, 1] }), browM));
      }
      // lips: a patch that lies on the sculpted mouth, a shade deeper than the skin
      const lipC = new THREE.Color(skinC).multiplyScalar(0.84).lerp(new THREE.Color(0x9a5450), fem ? 0.2 : 0.1);
      const lipM = K.mat('p-lip-' + lipC.getHexString(), { color: lipC.getHex(), roughness: 0.4, clearcoat: 0.3, clearcoatRoughness: 0.3 }, true);
      const topL = (x) => -0.445 - 0.06 * Math.pow(Math.abs(x) / 0.21, 2) + 0.008 * Math.exp(-Math.pow((Math.abs(x) - 0.055) / 0.03, 2));
      const botL = (x) => -0.595 + 0.075 * Math.pow(Math.abs(x) / 0.21, 2);
      const NXL = 16, NYL = 8, lp = [], li = [];
      for (let j = 0; j <= NYL; j++) for (let i = 0; i <= NXL; i++) {
        const x = lerp(-0.21, 0.21, i / NXL), y = lerp(topL(x), botL(x), j / NYL), q = surf(x, y);
        lp.push(q[0], q[1], q[2] + 0.0005 * k);
      }
      for (let j = 0; j < NYL; j++) for (let i = 0; i < NXL; i++) { const a = j * (NXL + 1) + i, b = a + NXL + 1; li.push(a, b, a + 1, b, b + 1, a + 1); }
      const lg = new THREE.BufferGeometry(); lg.setAttribute('position', new THREE.Float32BufferAttribute(lp, 3)); lg.setIndex(li); lg.computeVertexNormals();
      head.add(new THREE.Mesh(lg, lipM));
    }
    // hair
    if (style !== 'bald') {
      const hT = hairThickness(style, k, ph[0]), hatted = hatKind !== 'none';
      // under a hat the crown is pressed flat, so no hair can come through the hat
      head.add(new THREE.Mesh(shellGeo(hg, hatted ? (ux, uy, uz) => Math.min(hT(ux, uy, uz), lerp(0.009, 0.0035, smooth((uy - 0.1) / 0.3)) * k) : hT), hairM));
      if (longHair) head.add(new THREE.Mesh(curtainGeo(Wd, Hh, D, k, style === 'bob' ? 0.95 : 1.75 + 0.35 * r(), style === 'curlyLong', ph[1]), hairM));
      if (style === 'bun') {
        const bun = new THREE.Mesh(new THREE.SphereGeometry(1, LOW ? 10 : 20, LOW ? 8 : 14), hairM);
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
        if (full) {
          const m = Math.min(-0.08 - uy - 0.18 * (1 - ax), uz + 0.3);
          return m < 0 ? -0.002 : 0.0055 * k * smooth(m / 0.15) * (1 - 0.9 * lipGap) - (lipGap > 0.5 ? 0.004 : 0);
        }
        const mo = 1 - Math.max(Math.abs(uy + 0.415) / 0.045, ax / 0.24);
        return mo < 0 ? -0.002 : 0.0035 * k * smooth(mo / 0.3);
      };
      head.add(new THREE.Mesh(shellGeo(hg, beard), hairM));
    }
    if (hatKind !== 'none') {
      const hatC = hatKind === 'hard' ? pick(r, [0xf2f0ea, 0xf2c200, 0xf07a1a, 0xf2f0ea])
        : hatKind === 'cowboy' ? pick(r, [0xd9c69a, 0x2a2420, 0xc2b49a, 0x6b4e34, 0xe0d2a8])
        : pick(r, [0x1f2b44, 0x7a1f25, 0x3f4a3a, 0xe8e4dc, 0x2a2a2a, 0xb05a22]);
      const hm = hatKind === 'hard' ? K.mat('p-hard', { color: hatC, roughness: 0.3, clearcoat: 0.8, clearcoatRoughness: 0.2 }, true)
        : K.mat('p-hat', { color: hatC, roughness: hatKind === 'cowboy' && (hatC === 0xd9c69a || hatC === 0xe0d2a8) ? 0.85 : 0.75 });
      head.add(hat(hatKind, Wd * 1.03, D * 1.03, Hh * (hatKind === 'cowboy' ? 0.36 : hatKind === 'cap' ? 0.32 : 0.36), hm, r));
    }
    // the body pieces lean with the torso, about the hips
    const bodyPivot = new THREE.Group(); bodyPivot.position.y = pivY; body.position.y = -pivY;
    bodyPivot.add(body); bodyPivot.rotation.x = torsoLean; G.add(bodyPivot);
    const M = mergeByMaterial(G);
    M.userData.height = H; M.userData.role = role; M.userData.pose = pose;
    return M;
  }
  /* ---- a crowd ------------------------------------------------------------------------- */
  K.define('crowd', {
    size: [7.5, 1.9, 4.2],
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
