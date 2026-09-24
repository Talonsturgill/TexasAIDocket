/* kit/vehicles.js, see assets/js/txkit.js for the conventions.
 *
 * Every vehicle is built the way a body shop would describe it: a SIDE PROFILE of the body,
 * with the wheel arches cut into it, extruded across the width with rounded edges; a glass
 * greenhouse with tumblehome; pillars, seams, handles, mirrors, lamps, grille and bumpers as
 * their own parts; and real wheels (tyre with tread and sidewall, rim with spokes, hub, lugs,
 * brake disc) inside dark wheelhouses. Metres, y up, front at +z, origin on the ground at the
 * centre of the footprint. Paint is clearcoat physical material, glass is K.finish.glass.
 */
export function install(K, THREE, TXT) {
  const pick = (r, arr) => arr[Math.floor(r() * arr.length) % arr.length];
  const clamp01 = (t) => Math.max(0, Math.min(1, t));

  /* ---- materials ---------------------------------------------------------------------- */
  // realistic car colours, weighted the way a Texas parking lot is (white, black, grey, silver first)
  const PAINTS = [
    [0xf0f0ec, 0], [0xf0f0ec, 0], [0xeceae4, 0], [0x0f1012, 0], [0x0f1012, 0], [0xb4b8bc, 1], [0xb4b8bc, 1],
    [0x5c6066, 1], [0x5c6066, 1], [0x7c1416, 1], [0x1b2f4f, 1], [0xa39478, 1], [0x2e3a30, 1], [0x6e2a1a, 1], [0x2b4a6e, 1],
  ];
  const paint = (c, metallic) => K.mat('v-paint', {
    color: c, metalness: metallic ? 0.55 : 0.02, roughness: metallic ? 0.34 : 0.3,
    clearcoat: 1, clearcoatRoughness: 0.035 }, true);
  const seededPaint = (r, o) => {
    if (o.color != null) return paint(o.color, o.metallic != null ? o.metallic : 1);
    const p = pick(r, PAINTS); return paint(p[0], p[1]);
  };
  const M = {
    trim: () => K.mat('v-trim', { color: 0x16171a, roughness: 0.62 }),
    satin: () => K.mat('v-satin', { color: 0x1d1f22, roughness: 0.4, metalness: 0.2 }),
    well: () => K.mat('v-well', { color: 0x0b0b0c, roughness: 0.95 }),
    chrome: () => K.finish.chrome(),
    alloy: () => K.mat('v-alloy', { color: 0xc3c7cb, metalness: 0.9, roughness: 0.28 }),
    darkAlloy: () => K.mat('v-dalloy', { color: 0x3a3d41, metalness: 0.8, roughness: 0.35 }),
    steelWheel: () => K.mat('v-steelw', { color: 0xd9d9d4, metalness: 0.3, roughness: 0.45 }),
    rubber: () => K.mat('v-tyre', { color: 0x1a1a1b, roughness: 0.86 }),
    brake: () => K.mat('v-brake', { color: 0x55575a, metalness: 0.7, roughness: 0.55 }),
    glass: () => K.finish.glass(0x1a232a),
    lens: () => K.mat('v-lens', { color: 0xe9eef2, metalness: 0.95, roughness: 0.08 }),
    drl: () => K.mat('v-drl', { color: 0xffffff, emissive: 0xfff4e0, emissiveIntensity: 1.6, roughness: 0.3 }),
    tail: () => K.mat('v-tail', { color: 0x8c0f13, roughness: 0.18, clearcoat: 1, clearcoatRoughness: 0.05,
                                  emissive: 0x5a0000, emissiveIntensity: 0.35 }, true),
    amber: () => K.mat('v-amber', { color: 0xd98a1a, roughness: 0.2, emissive: 0x6a3a00, emissiveIntensity: 0.3 }),
    plate: () => K.mat('v-plate', { color: 0xe8e6de, roughness: 0.5 }),
    frame: () => K.mat('v-frame', { color: 0x1b1c1e, roughness: 0.7, metalness: 0.3 }),
  };

  /* ---- a side profile, extruded across the width ------------------------------------------
   * cmds in (z, y): ['m',z,y] ['l',z,y] ['q',cz,cy,z,y] ['arch',cz,R,axleY] (cuts a wheel arch
   * into a bottom edge running toward +z at the current height). The shape's X becomes +z. */
  function shapeOf(cmds) {
    const s = new THREE.Shape();
    let cy = 0;
    for (const c of cmds) {
      if (c[0] === 'm') { s.moveTo(c[1], c[2]); cy = c[2]; }
      else if (c[0] === 'l') { s.lineTo(c[1], c[2]); cy = c[2]; }
      else if (c[0] === 'q') { s.quadraticCurveTo(c[1], c[2], c[3], c[4]); cy = c[4]; }
      else if (c[0] === 'arch') {
        const [, cz, R, ay] = c, A = Math.asin(Math.max(-1, Math.min(1, (cy - ay) / R)));
        s.lineTo(cz - R * Math.cos(A), cy);
        s.absarc(cz, ay, R, Math.PI - A, A, true);
        s.lineTo(cz + R * Math.cos(A), cy);
      }
    }
    s.closePath();
    return s;
  }
  /* Inset a closed polygon by d (miter offset along the vertex bisectors), so that a bevel of
   * size d grown back out lands the surface exactly on the profile that was asked for. */
  function insetShape(shape, d) {
    let pts = shape.getPoints(24);
    pts = pts.filter((p, i) => i === 0 || p.distanceTo(pts[i - 1]) > 1e-4);
    if (pts.length > 2 && pts[0].distanceTo(pts[pts.length - 1]) < 1e-4) pts.pop();
    let area = 0; pts.forEach((p, i) => { const q = pts[(i + 1) % pts.length]; area += p.x * q.y - q.x * p.y; });
    const sg = area > 0 ? 1 : -1, n = pts.length, out = [];
    for (let i = 0; i < n; i++) {
      const a = pts[(i - 1 + n) % n], p = pts[i], c = pts[(i + 1) % n];
      const e1 = new THREE.Vector2(p.x - a.x, p.y - a.y).normalize(), e2 = new THREE.Vector2(c.x - p.x, c.y - p.y).normalize();
      const n1 = new THREE.Vector2(e1.y * sg, -e1.x * sg), n2 = new THREE.Vector2(e2.y * sg, -e2.x * sg);   // outward
      const k = Math.max(0.35, 1 + n1.dot(n2));
      out.push(new THREE.Vector2(p.x - d * (n1.x + n2.x) / k, p.y - d * (n1.y + n2.y) / k));
    }
    return new THREE.Shape(out);
  }
  /* Smooth normals across faces that meet at under `deg` degrees, hard edges elsewhere: the
   * extruded hood curve and wheel arches shade as one surface, the panel edges stay crisp. */
  function creaseNormals(g, deg) {
    const p = g.attributes.position, n = p.count / 3, cos = Math.cos((deg || 34) * Math.PI / 180);
    const fn = new Float32Array(n * 3), A = new THREE.Vector3(), B = new THREE.Vector3(), C = new THREE.Vector3();
    for (let f = 0; f < n; f++) {
      A.fromBufferAttribute(p, f * 3); B.fromBufferAttribute(p, f * 3 + 1); C.fromBufferAttribute(p, f * 3 + 2);
      const nn = C.sub(B).cross(A.sub(B)); const l = nn.length() || 1; fn[f * 3] = nn.x / l; fn[f * 3 + 1] = nn.y / l; fn[f * 3 + 2] = nn.z / l;
    }
    const key = (i) => Math.round(p.getX(i) * 1e4) + ',' + Math.round(p.getY(i) * 1e4) + ',' + Math.round(p.getZ(i) * 1e4);
    const map = new Map();
    for (let i = 0; i < p.count; i++) { const k = key(i); if (!map.has(k)) map.set(k, []); map.get(k).push(i); }
    const out = new Float32Array(p.count * 3);
    for (const list of map.values()) for (const i of list) {
      const f = (i / 3) | 0; let x = 0, y = 0, z = 0;
      for (const j of list) { const g2 = (j / 3) | 0;
        if (fn[f * 3] * fn[g2 * 3] + fn[f * 3 + 1] * fn[g2 * 3 + 1] + fn[f * 3 + 2] * fn[g2 * 3 + 2] >= cos) { x += fn[g2 * 3]; y += fn[g2 * 3 + 1]; z += fn[g2 * 3 + 2]; } }
      const l = Math.hypot(x, y, z) || 1; out[i * 3] = x / l; out[i * 3 + 1] = y / l; out[i * 3 + 2] = z / l;
    }
    g.setAttribute('normal', new THREE.BufferAttribute(out, 3));
    return g;
  }
  function sideExtrude(cmds, width, bevel, mat, o) {
    o = o || {};
    const b = Math.min(bevel, width * 0.3), bs = b * (o.sizeK != null ? o.sizeK : 0.6);
    const g = new THREE.ExtrudeGeometry(bs > 0 ? insetShape(shapeOf(cmds), bs) : shapeOf(cmds), { depth: Math.max(0.001, width - 2 * b), bevelEnabled: b > 0,
      bevelThickness: b, bevelSize: bs, bevelSegments: o.bevelSeg || 4, curveSegments: o.curveSeg || 16 });
    g.translate(0, 0, -(width - 2 * b) / 2);
    g.rotateY(-Math.PI / 2);
    if (o.deform) {
      const p = g.attributes.position;
      for (let i = 0; i < p.count; i++) { const v = o.deform(p.getX(i), p.getY(i), p.getZ(i)); p.setXYZ(i, v[0], v[1], v[2]); }
      g.computeBoundingBox(); g.computeBoundingSphere();
    }
    creaseNormals(g, o.crease || 34);
    const m = new THREE.Mesh(g, mat);
    if (o.x) m.position.x = o.x;
    return m;
  }
  // plan-view rounding: pull the sides in toward the nose and tail
  const planRound = (zf, zr, inset, reach) => (x, y, z) => {
    const f = Math.max(clamp01((z - (zf - reach)) / reach), clamp01(((zr + reach) - z) / reach));
    return [x * (1 - inset * f * f), y, z];
  };
  // glass greenhouse with tumblehome; returns { mesh, hw(y) } where hw is the half width at y
  function greenhouse(cmds, halfW, belt, roof, tumble, mat, bevel) {
    const hw = (y) => halfW * (1 - tumble * clamp01((y - belt) / (roof - belt)));
    const mesh = sideExtrude(cmds, halfW * 2, bevel != null ? bevel : 0.03, mat,
      { deform: (x, y, z) => [x * (1 - tumble * clamp01((y - belt) / (roof - belt))), y, z] });
    return { mesh, hw };
  }
  // a thin flat part on a body side at x (sign s), from a polygon in (z, y)
  function sidePane(pts, x, thick, mat, bevel, xAt) {
    const s = new THREE.Shape(); pts.forEach((p, i) => (i ? s.lineTo(p[0], p[1]) : s.moveTo(p[0], p[1])));
    const b = bevel != null ? bevel : Math.min(0.006, thick * 0.4);
    const g = new THREE.ExtrudeGeometry(s, { depth: Math.max(0.0005, thick - 2 * b), bevelEnabled: b > 0, bevelThickness: b, bevelSize: b, bevelSegments: 2, curveSegments: 6 });
    g.translate(0, 0, -(thick - 2 * b) / 2); g.rotateY(-Math.PI / 2);
    if (xAt) { const p = g.attributes.position; for (let i = 0; i < p.count; i++) p.setX(i, p.getX(i) + xAt(p.getY(i))); g.computeBoundingSphere(); }
    const m = new THREE.Mesh(g, mat); m.position.x = x; return m;
  }
  // polygon offset (convex, either winding): grow by d
  function grow(pts, d) {
    const n = pts.length, cx = pts.reduce((a, p) => a + p[0], 0) / n, cy = pts.reduce((a, p) => a + p[1], 0) / n;
    return pts.map((p) => { const dx = p[0] - cx, dy = p[1] - cy, l = Math.hypot(dx, dy) || 1; return [p[0] + dx / l * d * 1.2, p[1] + dy / l * d * 1.2]; });
  }
  // a framed window on a flat side: black gasket, then glass just proud of it
  function sideWindow(G, pts, x, sgn, frameMat) {
    G.add(sidePane(grow(pts, 0.025), x + sgn * 0.004, 0.012, frameMat || M.trim()));
    G.add(sidePane(pts, x + sgn * 0.011, 0.008, M.glass(), 0.003));
  }
  // rounded boxes at the segment count their size needs: 2 for trim, 3 for a panel
  const RB = (w, h, d, r, mat) => TXT.roundedBox(w, h, d, r, mat, { segments: Math.max(w, h, d) > 1.5 ? 3 : 2 });
  const box = (w, h, d, mat, x, y0, z, r, parent) => {
    const m = r ? RB(w, h, d, r, mat) : new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
    m.position.set(x || 0, (y0 || 0) + h / 2, z || 0);
    if (parent) parent.add(m);
    return m;
  };
  /* Merge every mesh under root that shares a material (one draw call per material). */
  function mergeByMaterial(root) {
    root.updateMatrixWorld(true);
    const inv = new THREE.Matrix4().copy(root.matrixWorld).invert(), groups = new Map();
    root.traverse((m) => { if (m.isMesh && !m.isInstancedMesh) { if (!groups.has(m.material)) groups.set(m.material, []); groups.get(m.material).push(m); } });
    const out = new THREE.Group();
    for (const [mat, list] of groups) {
      const parts = list.map((m) => {
        const g = m.geometry.index ? m.geometry.toNonIndexed() : m.geometry.clone();
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
    root.traverse((m) => { if (m.isInstancedMesh) out.add(m.clone()); });
    return out;
  }

  const bar = (a, b, r, mat, parent, seg) => K.bar(a, b, r, mat, seg || 10, parent);

  /* ---- wheels --------------------------------------------------------------------------- */
  const WHEELS = new Map();
  // Returns a Group with the wheel's axis on x, outer face toward +x, centred on the origin.
  function wheelParts(R, w, style, rimR) {
    const key = [R, w, style, rimR].join('|');
    if (WHEELS.has(key)) return WHEELS.get(key);
    const seg = style === 'truck' || style === 'steel' ? 32 : 40;
    const rr = rimR || R * 0.62, hw = w / 2;
    // tyre: sidewalls with a bulge, a shoulder, a tread with three grooves
    const pr = [[rr - 0.01, -hw + 0.02], [rr + 0.02, -hw], [R - 0.045, -hw - 0.006], [R - 0.012, -hw + 0.01], [R, -hw + 0.03],
      [R, -hw * 0.45], [R - 0.012, -hw * 0.42], [R - 0.012, -hw * 0.3], [R, -hw * 0.27], [R, -0.012], [R - 0.012, -0.009], [R - 0.012, 0.009], [R, 0.012],
      [R, hw * 0.27], [R - 0.012, hw * 0.3], [R - 0.012, hw * 0.42], [R, hw * 0.45],
      [R, hw - 0.03], [R - 0.012, hw - 0.01], [R - 0.045, hw + 0.006], [rr + 0.02, hw], [rr - 0.01, hw - 0.02]];
    const tyre = new THREE.LatheGeometry(pr.map((p) => new THREE.Vector2(p[0], p[1])), seg);
    tyre.rotateZ(-Math.PI / 2);
    // rim lip and barrel (seen through the spokes)
    const lip = new THREE.LatheGeometry([[rr - 0.03, -hw + 0.03], [rr - 0.012, hw - 0.03], [rr + 0.004, hw - 0.012], [rr - 0.004, hw - 0.004], [rr - 0.03, hw - 0.012]]
      .map((p) => new THREE.Vector2(p[0], p[1])), seg);
    lip.rotateZ(-Math.PI / 2);
    // dark dish behind the spokes, with the brake disc
    const dish = new THREE.CylinderGeometry(rr - 0.015, rr - 0.015, 0.01, seg); dish.rotateZ(Math.PI / 2); dish.translate(hw - 0.12, 0, 0);
    const disc = new THREE.CylinderGeometry(rr * 0.78, rr * 0.78, 0.03, 32); disc.rotateZ(Math.PI / 2); disc.translate(hw - 0.09, 0, 0);
    const face = [];
    if (style === 'steel' || style === 'truck') {
      // pressed steel wheel: a dished face with hand holes and a hub pilot
      const pf = [[rr - 0.015, hw - 0.03], [rr * 0.82, hw - 0.05], [rr * 0.62, hw - 0.075], [rr * 0.36, hw - 0.08], [rr * 0.3, hw - 0.055], [0.001, hw - 0.05]];
      const f = new THREE.LatheGeometry(pf.map((p) => new THREE.Vector2(p[0], p[1])).reverse(), seg); f.rotateZ(-Math.PI / 2); face.push(f);
      const holes = [];
      const nh = style === 'truck' ? 10 : 5;
      for (let i = 0; i < nh; i++) {
        const a = (i / nh) * Math.PI * 2, h = new THREE.CylinderGeometry(rr * 0.09, rr * 0.09, 0.01, 12);
        h.rotateZ(Math.PI / 2); h.translate(hw - 0.066, Math.cos(a) * rr * 0.72, Math.sin(a) * rr * 0.72); holes.push(h);
      }
      WHEELS.set(key, { tyre, lip, dish, disc, face, holes, hubR: rr * 0.3, hw, rr, style });
    } else {
      // alloy: spokes from hub to lip, a hub cap and lug nuts
      const n = style === 'six' ? 6 : 5;
      for (let i = 0; i < n; i++) {
        const a = (i / n) * Math.PI * 2;
        const sp = new THREE.BoxGeometry(0.03, rr * 0.8, rr * 0.2, 1, 3, 1);
        // taper the spoke toward the hub and dish it back toward the rim
        const p = sp.attributes.position;
        for (let j = 0; j < p.count; j++) {
          const t = (p.getY(j) + rr * 0.4) / (rr * 0.8);
          p.setZ(j, p.getZ(j) * (0.55 + 0.45 * t)); p.setX(j, p.getX(j) - t * 0.035);
        }
        sp.computeVertexNormals();
        sp.translate(hw - 0.035, rr * 0.5, 0); sp.rotateX(a); face.push(sp);
      }
      const hub = new THREE.CylinderGeometry(rr * 0.24, rr * 0.27, 0.05, 32); hub.rotateZ(-Math.PI / 2); hub.translate(hw - 0.04, 0, 0); face.push(hub);
      WHEELS.set(key, { tyre, lip, dish, disc, face, holes: [], hubR: rr * 0.24, hw, rr, style });
    }
    return WHEELS.get(key);
  }
  function wheel(R, w, style, rimMat, rimR) {
    const P = wheelParts(R, w, style, rimR), g = new THREE.Group();
    g.add(new THREE.Mesh(P.tyre, M.rubber()));
    g.add(new THREE.Mesh(P.lip, rimMat));
    g.add(new THREE.Mesh(P.dish, M.well()));
    g.add(new THREE.Mesh(P.disc, M.brake()));
    P.face.forEach((f) => g.add(new THREE.Mesh(f, rimMat)));
    P.holes.forEach((h) => g.add(new THREE.Mesh(h, M.well())));
    // lug nuts
    const nl = P.style === 'truck' ? 10 : P.style === 'six' ? 6 : 5;
    for (let i = 0; i < nl; i++) {
      const a = (i / nl) * Math.PI * 2 + 0.3, nut = new THREE.Mesh(new THREE.CylinderGeometry(0.011, 0.011, 0.025, 6), M.chrome());
      nut.rotation.z = Math.PI / 2; nut.position.set(P.hw - (P.style === 'steel' || P.style === 'truck' ? 0.05 : 0.02), Math.cos(a) * P.hubR * 0.72, Math.sin(a) * P.hubR * 0.72);
      g.add(nut);
    }
    return g;
  }
  // an axle: two wheels (or duals) at track width, with a dark wheelhouse between the arches
  function axle(G, z, R, w, track, style, rimMat, o) {
    o = o || {};
    for (const s of [1, -1]) {
      const n = o.dual ? 2 : 1;
      for (let d = 0; d < n; d++) {
        const wg = wheel(R, w, style, rimMat, o.rimR);
        const inner = d === 1;
        wg.position.set(s * (track / 2 - (inner ? w + 0.03 : 0)), R, z);
        if (s < 0) wg.rotation.y = Math.PI;
        if (inner) wg.rotation.y += Math.PI;    // the inner dual faces in: its dish meets the outer's
        if (o.steer && s) wg.rotation.y += o.steer;
        G.add(wg);
      }
    }
    if (o.well !== false) {
      const wl = new THREE.Mesh(new THREE.CylinderGeometry(R + 0.03, R + 0.03, o.wellW || track - w * (o.dual ? 2.2 : 1.1), 32), M.well());
      wl.rotation.z = Math.PI / 2; wl.position.set(0, R + (o.wellLift || 0.02), z); G.add(wl);
    }
  }

  /* ---- small parts ---------------------------------------------------------------------- */
  // a door seam: a dark hairline standing on a flat body side
  function seam(G, x, z0, y0, z1, y1) {
    for (const s of [1, -1]) {
      const a = [s * (x + 0.0015), y0, z0], b = [s * (x + 0.0015), y1, z1];
      const len = Math.hypot(y1 - y0, z1 - z0);
      const m = new THREE.Mesh(new THREE.BoxGeometry(0.003, len, 0.005), M.well());
      m.position.set(a[0], (y0 + y1) / 2, (z0 + z1) / 2); m.rotation.x = -Math.atan2(z1 - z0, y1 - y0);
      G.add(m);
    }
  }
  function handle(G, x, y, z, mat) {
    for (const s of [1, -1]) box(0.022, 0.028, 0.15, mat || M.satin(), s * (x + 0.01), y, z, 0.01, G);
  }
  function mirror(G, x, y, z, mat, big) {
    for (const s of [1, -1]) {
      const w = big ? 0.2 : 0.18, h = big ? 0.25 : 0.12;
      bar([s * (x - 0.02), y + 0.02, z], [s * (x + 0.1), y + 0.04, z - 0.02], 0.018, M.trim(), G);
      const head = RB(w, h, 0.09, 0.03, mat); head.position.set(s * (x + 0.1 + w / 2), y + 0.05 + h / 2 - 0.03, z - 0.03); G.add(head);
      const gl = RB(w - 0.03, h - 0.03, 0.01, 0.005, K.finish.chrome()); gl.position.set(s * (x + 0.1 + w / 2), y + 0.05 + h / 2 - 0.03, z - 0.076); G.add(gl);
    }
  }
  /* Snap to a body surface: returns f(x, y) = the z where a ray along -dir*z first meets the
   * meshes (the nose when dir = 1, the tail when dir = -1). Parts are placed ON the body this way,
   * never guessed at, so a bevel or a curved nose can never swallow a lamp. */
  const RC = new THREE.Raycaster();
  function snapper(meshes, dir, fallback) {
    meshes.forEach((m) => m.updateMatrixWorld(true));
    return (x, y) => {
      RC.set(new THREE.Vector3(x, y, dir * 200), new THREE.Vector3(0, 0, -dir));
      const h = RC.intersectObjects(meshes, false)[0];
      return h ? h.point.z : fallback;
    };
  }
  // a lamp: housing, a mirrored reflector behind a lens, a lit strip. z may be a snapper.
  function lamp(G, w, h, x, y, z, kind, dir) {
    dir = dir || 1;
    for (const s of [1, -1]) {
      const body = RB(w, h, 0.05, Math.min(w, h) * 0.3, kind === 'tail' ? M.tail() : kind === 'amber' ? M.amber() : M.lens());
      const zz = typeof z === 'function' ? z(s * x, y) + dir * 0.012 : z;
      body.position.set(s * x, y, zz); G.add(body);
      if (kind === 'head') {
        const strip = RB(w * 0.85, Math.max(0.012, h * 0.12), 0.02, 0.005, M.drl());
        strip.position.set(s * x, y - h * 0.32, zz + dir * 0.02); G.add(strip);
      }
    }
  }
  // a licence plate
  function plate(G, y, z, dir) {
    const p = RB(0.305, 0.152, 0.01, 0.01, M.plate()); p.position.set(0, y, z); G.add(p);
    const t = RB(0.24, 0.05, 0.004, 0.002, K.mat('v-platetext', { color: 0x1f3050, roughness: 0.5 })); t.position.set(0, y, z + dir * 0.006); G.add(t);
  }
  // a text panel: canvas-painted sign (school bus, fleet lettering)
  const SIGNS = new Map();
  function signMat(text, fg, bg, w, h) {
    const k = text + fg + bg + w + h;
    if (SIGNS.has(k)) return SIGNS.get(k);
    const c = document.createElement('canvas'); c.width = 512; c.height = Math.round(512 * h / w);
    const x = c.getContext('2d'); if (bg) { x.fillStyle = bg; x.fillRect(0, 0, c.width, c.height); }
    x.fillStyle = fg; x.textAlign = 'center'; x.textBaseline = 'middle';
    let fs = c.height * 0.72; x.font = '900 ' + fs + 'px Arial, Helvetica, sans-serif';
    while (x.measureText(text).width > c.width * 0.9 && fs > 8) { fs -= 2; x.font = '900 ' + fs + 'px Arial, Helvetica, sans-serif'; }
    x.fillText(text, c.width / 2, c.height / 2 + fs * 0.04);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    const m = new THREE.MeshStandardMaterial({ map: t, roughness: 0.4, transparent: !bg, alphaTest: bg ? 0 : 0.4 });
    SIGNS.set(k, m); return m;
  }
  function sign(text, fg, bg, w, h, mat) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat || signMat(text, fg, bg, w, h));
    return m;
  }

  /* =========================================================================================
   * PICKUP: Texas full-size crew cab, 5.5 ft bed. 5.89 x 2.03 x 1.96 m, wheelbase 3.68 m.
   * ========================================================================================= */
  K.define('pickup', {
    size: [2.4, 1.96, 5.89],
    options: { seed: 1, color: null, metallic: null, trim: 'auto' },
    note: 'Full-size crew-cab pickup (F-150 / Silverado class), 5.5 ft bed. trim chrome|work|dark; color hex for paint.',
    make(o, r) {
      const G = new THREE.Group(), P = seededPaint(r, o);
      const L = 5.89, W = 2.03, hw = W / 2, zf = L / 2, zr = -L / 2;
      const trim = o.trim && o.trim !== 'auto' ? o.trim : pick(r, ['chrome', 'chrome', 'work', 'dark']);
      const bright = trim === 'chrome' ? M.chrome() : trim === 'work' ? M.trim() : M.satin();
      const R = 0.405, fz = zf - 0.95, rz = fz - 3.68, ay = R;
      // cab and front end
      const cab = G.add(sideExtrude([['m', -0.34, 0.54], ['arch', fz, R + 0.05, ay], ['l', 2.66, 0.54], ['l', 2.8, 0.6], ['l', 2.9, 0.68],
        ['q', 2.95, 0.74, 2.95, 0.9], ['l', 2.94, 1.16], ['q', 2.93, 1.29, 2.78, 1.3], ['l', 1.25, 1.365], ['l', 1.08, 1.375], ['l', -0.34, 1.385]],
      W, 0.06, P, { deform: planRound(2.9, -9, 0.04, 0.5) })).children.slice(-1)[0];
      const nose = snapper([cab], 1, zf);
      // bed sides with the rear arch, a floor, a front wall and the tailgate
      for (const s of [1, -1]) G.add(sideExtrude([['m', zr + 0.02, 0.56], ['arch', rz, R + 0.05, ay], ['l', -0.4, 0.56], ['l', -0.4, 1.33], ['l', zr + 0.02, 1.33]], 0.09, 0.03, P, { x: s * (hw - 0.045) }));
      box(W - 0.16, 0.04, 2.5, K.mat('v-liner', { color: 0x1f2022, roughness: 0.9 }), 0, 0.62, (zr - 0.4) / 2 + 0.02, 0, G);
      box(W - 0.1, 0.72, 0.06, P, 0, 0.6, -0.42, 0.02, G);
      for (const s of [1, -1]) box(0.11, 0.035, 2.52, M.trim(), s * (hw - 0.05), 1.33, (zr - 0.4) / 2 + 0.01, 0.012, G);   // bed rail caps
      const tg = RB(W - 0.02, 0.72, 0.07, 0.03, P); tg.position.set(0, 0.6 + 0.36, zr + 0.035); G.add(tg);
      box(0.3, 0.05, 0.02, bright, 0, 1.2, zr - 0.002, 0.01, G);                   // tailgate handle
      box(W - 0.3, 0.04, 0.02, M.trim(), 0, 1.3, zr - 0.002, 0.01, G);
      plate(G, 0.52, zr - 0.08, -1);
      for (const s of [1, -1]) { const tl = RB(0.09, 0.36, 0.06, 0.02, M.tail()); tl.position.set(s * (hw - 0.05), 1.12, zr + 0.01); G.add(tl); }
      // rear bumper with step pads
      const rb = RB(W, 0.22, 0.22, 0.05, bright); rb.position.set(0, 0.5, zr - 0.02); G.add(rb);
      box(0.5, 0.02, 0.12, M.trim(), 0, 0.61, zr - 0.06, 0.005, G);
      // greenhouse, roof and pillars
      const belt = 1.38, roof = 1.94;
      const gh = greenhouse([['m', 1.1, belt - 0.02], ['l', 0.22, roof - 0.04], ['l', -0.26, roof - 0.03], ['l', -0.31, belt - 0.02]], hw - 0.13, belt, roof, 0.1, M.glass());
      G.add(gh.mesh);
      const rf = sideExtrude([['m', 0.3, roof - 0.07], ['q', 0.1, roof + 0.01, -0.1, roof + 0.015], ['l', -0.34, roof], ['l', -0.34, roof - 0.07]], (gh.hw(roof) + 0.02) * 2, 0.04, P);
      G.add(rf);
      for (const s of [1, -1]) {
        bar([s * (gh.hw(belt) + 0.012), belt, 1.12], [s * (gh.hw(roof) + 0.012), roof - 0.06, 0.26], 0.042, P, G);    // A
        const bp = RB(0.012, roof - belt, 0.11, 0.004, M.trim());                                          // B, black
        bp.position.set(s * (gh.hw((belt + roof) / 2) + 0.004), (belt + roof) / 2, 0.06); bp.rotation.z = -s * 0.1 * (hw - 0.13) / (roof - belt); G.add(bp);
        bar([s * (gh.hw(belt) + 0.012), belt, -0.3], [s * (gh.hw(roof) + 0.012), roof - 0.03, -0.29], 0.045, P, G);   // C
        bar([s * (gh.hw(roof) + 0.012), roof - 0.03, 0.2], [s * (gh.hw(roof) + 0.012), roof - 0.03, -0.29], 0.03, P, G);
        // window trim along the belt
        box(0.02, 0.025, 1.42, bright === M.chrome() ? bright : M.trim(), s * (gh.hw(belt) + 0.012), belt - 0.02, 0.4, 0.008, G);
      }
      // doors: seams, handles
      seam(G, hw, 1.2, 0.58, 1.1, belt); seam(G, hw, 0.08, 0.56, 0.08, belt); seam(G, hw, -0.3, 0.56, -0.3, belt);
      seam(G, hw, 1.2, 0.58, 0.08, 0.58);
      handle(G, hw, 1.16, 0.22, bright); handle(G, hw, 1.16, -0.2, bright);
      mirror(G, hw, 1.4, 1.02, trim === 'chrome' ? M.chrome() : trim === 'work' ? M.trim() : P, true);
      // front: bumper, grille, headlights, fog lamps, tow hooks
      const fb = RB(W - 0.02, 0.3, 0.26, 0.06, bright); fb.position.set(0, 0.55, zf - 0.06); G.add(fb);
      box(W - 0.5, 0.1, 0.08, M.trim(), 0, 0.46, zf + 0.04, 0.02, G);
      const gw = 1.34, gh2 = 0.5;
      const nz = nose(0, 0.98);
      const gs = RB(gw + 0.1, gh2 + 0.1, 0.06, 0.04, bright); gs.position.set(0, 0.75 + gh2 / 2, nz + 0.01); G.add(gs);
      box(gw, gh2, 0.05, M.well(), 0, 0.75, nz + 0.03, 0.01, G);
      for (let i = 0; i < 4; i++) box(gw - 0.02, 0.035, 0.035, bright, 0, 0.8 + i * 0.12, nz + 0.06, 0.012, G);
      const vb = RB(0.035, gh2 - 0.02, 0.035, 0.012, bright); vb.position.set(0, 0.75 + gh2 / 2, nz + 0.06); G.add(vb);
      const badge = RB(0.2, 0.08, 0.02, 0.02, M.chrome()); badge.position.set(0, 1.0, nz + 0.085); G.add(badge);
      lamp(G, 0.27, 0.22, hw - 0.19, 1.04, nose, 'head');
      lamp(G, 0.12, 0.06, hw - 0.25, 0.55, zf + 0.07, 'amber');
      for (const s of [1, -1]) box(0.05, 0.04, 0.08, K.mat('v-hook', { color: 0x9a1b1b, roughness: 0.5 }), s * 0.5, 0.42, zf + 0.03, 0.01, G);
      plate(G, 0.56, zf + 0.08, 1);
      // running boards
      for (const s of [1, -1]) box(0.16, 0.05, 1.78, M.trim(), s * (hw - 0.02), 0.4, 0.44, 0.02, G);
      // underbody so the ground never shows through: frame rails, fuel tank, spare, diff housings
      box(W - 0.35, 0.22, L - 1.2, M.frame(), 0, 0.32, -0.1, 0.02, G);
      bar([0, R, rz - 0.2], [0, R, rz + 0.2], 0.12, M.frame(), G);
      axle(G, fz, R, 0.275, W - 0.3, trim === 'work' ? 'steel' : 'six', trim === 'work' ? M.steelWheel() : trim === 'dark' ? M.darkAlloy() : M.alloy(), { rimR: 0.24 });
      axle(G, rz, R, 0.275, W - 0.3, trim === 'work' ? 'steel' : 'six', trim === 'work' ? M.steelWheel() : trim === 'dark' ? M.darkAlloy() : M.alloy(), { rimR: 0.24 });
      return G;
    },
  });

  /* =========================================================================================
   * SEDAN: mid-size four door (Camry class). 4.88 x 1.84 x 1.44 m, wheelbase 2.82 m.
   * ========================================================================================= */
  K.define('sedan', {
    size: [2.05, 1.44, 4.88],
    options: { seed: 1, color: null, metallic: null },
    note: 'Mid-size four-door sedan, 4.88 m. Seeded paint from a realistic palette.',
    make(o, r) {
      const G = new THREE.Group(), P = seededPaint(r, o);
      const L = 4.88, W = 1.84, hw = W / 2, zf = L / 2, zr = -L / 2, R = 0.335, fz = zf - 0.97, rz = fz - 2.82;
      const body = sideExtrude([['m', zr + 0.12, 0.24], ['arch', rz, R + 0.035, R], ['arch', fz, R + 0.035, R], ['l', zf - 0.2, 0.24],
        ['q', zf - 0.02, 0.26, zf, 0.44], ['q', zf + 0.01, 0.68, zf - 0.1, 0.76], ['q', zf - 0.45, 0.84, 1.3, 0.87], ['l', 0.98, 0.92],
        ['l', -1.4, 0.97], ['q', -1.6, 1.0, -2.2, 1.0], ['q', zr + 0.02, 0.99, zr, 0.84], ['l', zr + 0.01, 0.44], ['q', zr + 0.01, 0.25, zr + 0.12, 0.24]],
      W, 0.09, P, { deform: planRound(zf, zr, 0.08, 0.55), sizeK: 0.7 }); G.add(body);
      const nose = snapper([body], 1, zf), tail = snapper([body], -1, zr);
      const belt = 0.95, roof = 1.44;
      const gh = greenhouse([['m', 1.0, belt - 0.03], ['q', 0.55, 1.22, 0.12, roof - 0.04], ['q', -0.4, roof, -0.9, roof - 0.05], ['q', -1.2, 1.28, -1.45, belt - 0.0]],
        hw - 0.1, belt, roof, 0.2, M.glass(), 0.04);
      G.add(gh.mesh);
      // roof skin over the glass
      G.add(sideExtrude([['m', 0.14, roof - 0.07], ['q', -0.4, roof + 0.012, -0.92, roof - 0.045], ['l', -0.98, roof - 0.1]], (gh.hw(roof) + 0.012) * 2, 0.035, P));
      for (const s of [1, -1]) {
        const x = (y) => s * (gh.hw(y) + 0.01);
        TXT_tube(G, [[x(belt), belt, 1.0], [x(1.2), 1.2, 0.58], [x(roof - 0.05), roof - 0.055, 0.16]], 0.035, P);   // A
        const bp = RB(0.012, roof - belt - 0.04, 0.09, 0.004, M.trim());
        bp.position.set(s * (gh.hw(1.19) + 0.004), 1.19, -0.12); bp.rotation.z = -s * 0.2 * (hw - 0.1) / (roof - belt); G.add(bp);
        // C pillar panel: the body closes the greenhouse behind the rear door glass
        G.add(sidePane([[-0.95, belt - 0.02], [-0.86, roof - 0.07], [-0.9, roof - 0.05], [-1.45, belt - 0.02]], 0, 0.02, P, 0.006, (y) => s * (gh.hw(y) + 0.006)));
        box(0.018, 0.02, 2.0, M.chrome(), s * (gh.hw(belt) + 0.01), belt - 0.02, -0.2, 0.006, G);
      }
      seam(G, hw, 1.02, 0.3, 0.98, belt); seam(G, hw, -0.1, 0.28, -0.1, belt); seam(G, hw, -0.95, 0.3, -0.85, belt);
      handle(G, hw, 0.84, 0.1, P); handle(G, hw, 0.85, -0.78, P);
      mirror(G, hw, 0.95, 0.86, P, false);
      // nose: grille, lamps; tail: lamps, plate, diffuser
      const gr = RB(0.95, 0.2, 0.04, 0.05, M.satin()); gr.position.set(0, 0.5, nose(0, 0.5) + 0.005); G.add(gr);
      box(0.6, 0.05, 0.03, M.chrome(), 0, 0.63, nose(0, 0.65) + 0.004, 0.02, G);
      lamp(G, 0.34, 0.11, hw - 0.25, 0.66, nose, 'head');
      lamp(G, 0.36, 0.1, hw - 0.22, 0.85, tail, 'tail', -1);
      box(1.2, 0.08, 0.04, M.satin(), 0, 0.3, tail(0, 0.34) - 0.005, 0.02, G);
      plate(G, 0.62, tail(0, 0.62) - 0.008, -1); plate(G, 0.4, nose(0, 0.4) + 0.008, 1);
      box(W - 0.3, 0.12, L - 1.0, M.frame(), 0, 0.14, 0, 0.02, G);
      axle(G, fz, R, 0.235, W - 0.24, 'five', M.alloy(), { rimR: 0.23 });
      axle(G, rz, R, 0.235, W - 0.24, 'five', M.alloy(), { rimR: 0.23 });
      return G;
    },
  });
  function TXT_tube(G, pts, r, mat) { const t = TXT.tube(pts, r, mat, { segments: 24, radial: 10 }); G.add(t); return t; }

  /* =========================================================================================
   * SUV: full-size (Tahoe class). 5.35 x 2.06 x 1.93 m, wheelbase 3.07 m.
   * ========================================================================================= */
  K.define('suv', {
    size: [2.4, 1.93, 5.35],
    options: { seed: 1, color: null, metallic: null, rack: true },
    note: 'Full-size SUV, 5.35 m, roof rails. Seeded paint.',
    make(o, r) {
      const G = new THREE.Group(), P = seededPaint(r, o);
      const L = 5.35, W = 2.06, hw = W / 2, zf = L / 2, zr = -L / 2, R = 0.4, fz = zf - 0.95, rz = fz - 3.07;
      const body = sideExtrude([['m', zr + 0.08, 0.46], ['arch', rz, R + 0.05, R], ['arch', fz, R + 0.05, R], ['l', zf - 0.15, 0.46],
        ['q', zf - 0.02, 0.5, zf, 0.62], ['l', zf, 1.1], ['q', zf - 0.02, 1.24, zf - 0.2, 1.25], ['l', 1.1, 1.32],
        ['l', zr + 0.1, 1.34], ['q', zr, 1.34, zr, 1.2], ['l', zr, 0.56], ['q', zr, 0.46, zr + 0.08, 0.46]],
      W, 0.07, P, { deform: planRound(zf, zr, 0.05, 0.45) }); G.add(body);
      const nose = snapper([body], 1, zf), tail = snapper([body], -1, zr);
      const belt = 1.34, roof = 1.9;
      const gh = greenhouse([['m', 1.12, belt - 0.02], ['l', 0.2, roof - 0.04], ['l', zr + 0.22, roof - 0.03], ['l', zr + 0.1, belt - 0.02]], hw - 0.1, belt, roof, 0.1, M.glass());
      G.add(gh.mesh);
      G.add(sideExtrude([['m', 0.26, roof - 0.07], ['q', 0.1, roof + 0.01, -0.1, roof + 0.012], ['l', zr + 0.24, roof], ['l', zr + 0.18, roof - 0.07]], (gh.hw(roof) + 0.015) * 2, 0.04, P));
      for (const s of [1, -1]) {
        const x = (y) => s * (gh.hw(y) + 0.012);
        bar([x(belt), belt, 1.14], [x(roof), roof - 0.06, 0.24], 0.04, P, G);
        for (const [z, m] of [[0.02, M.trim()], [-1.06, M.trim()]]) {
          const bp = RB(0.012, roof - belt, 0.1, 0.004, m); bp.position.set(s * (gh.hw((belt + roof) / 2) + 0.004), (belt + roof) / 2, z);
          bp.rotation.z = -s * 0.1 * (hw - 0.1) / (roof - belt); G.add(bp);
        }
        // D pillar, body colour, wide at the tail
        G.add(sidePane([[zr + 0.1, belt - 0.02], [zr + 0.2, roof - 0.04], [zr + 0.55, roof - 0.04], [zr + 0.62, belt - 0.02]], 0, 0.02, P, 0.006, (y) => s * (gh.hw(y) + 0.008)));
        box(0.02, 0.025, 3.7, M.chrome(), s * (gh.hw(belt) + 0.012), belt - 0.02, -0.7, 0.008, G);
        if (o.rack !== false) {
          box(0.05, 0.04, 2.6, M.satin(), s * (gh.hw(roof) - 0.12), roof + 0.01, -0.95, 0.015, G);
          for (const z of [0.2, -2.1]) box(0.06, 0.06, 0.12, M.satin(), s * (gh.hw(roof) - 0.12), roof - 0.02, z, 0.015, G);
        }
      }
      seam(G, hw, 1.2, 0.5, 1.12, belt); seam(G, hw, 0.02, 0.48, 0.02, belt); seam(G, hw, -1.1, 0.48, -1.06, belt);
      handle(G, hw, 1.2, 0.2, M.chrome()); handle(G, hw, 1.2, -0.9, M.chrome());
      mirror(G, hw, 1.38, 1.02, P, false);
      const nz = nose(0, 0.95);
      const gs = RB(1.3, 0.46, 0.06, 0.04, M.chrome()); gs.position.set(0, 0.95, nz + 0.01); G.add(gs);
      box(1.22, 0.38, 0.05, M.well(), 0, 0.76, nz + 0.025, 0.01, G);
      box(1.24, 0.05, 0.04, M.chrome(), 0, 0.93, nz + 0.05, 0.015, G);
      lamp(G, 0.3, 0.14, hw - 0.2, 1.08, nose, 'head');
      const fb = RB(W - 0.04, 0.26, 0.2, 0.06, M.satin()); fb.position.set(0, 0.56, zf - 0.02); G.add(fb);
      lamp(G, 0.12, 0.44, hw - 0.08, 1.08, tail, 'tail', -1);
      const rb = RB(W - 0.04, 0.24, 0.2, 0.06, M.satin()); rb.position.set(0, 0.55, zr + 0.03); G.add(rb);
      plate(G, 0.88, tail(0, 0.88) - 0.008, -1); plate(G, 0.52, zf + 0.09, 1);
      box(0.9, 0.05, 0.02, M.chrome(), 0, 1.05, tail(0, 1.05) - 0.008, 0.015, G);
      const hgl = RB(1.5, 0.42, 0.02, 0.05, M.glass()); hgl.position.set(0, 1.6, tail(0, 1.6) - 0.006); G.add(hgl);
      for (const s of [1, -1]) box(0.14, 0.05, 2.2, M.satin(), s * (hw - 0.03), 0.38, 0.1, 0.02, G);
      box(W - 0.35, 0.2, L - 1.2, M.frame(), 0, 0.28, 0, 0.02, G);
      axle(G, fz, R, 0.275, W - 0.28, 'six', M.alloy(), { rimR: 0.26 });
      axle(G, rz, R, 0.275, W - 0.28, 'six', M.alloy(), { rimR: 0.26 });
      return G;
    },
  });

  /* =========================================================================================
   * DELIVERY VAN: high-roof cargo van (Transit / Sprinter class). 5.98 x 2.05 x 2.72 m.
   * ========================================================================================= */
  K.define('delivery_van', {
    size: [2.5, 2.72, 5.98],
    options: { seed: 1, color: null, lettering: null },
    note: 'High-roof cargo van, 5.98 m, sliding side door, twin rear doors. White by default most seeds; lettering draws a fleet name on the sides.',
    make(o, r) {
      const G = new THREE.Group();
      const P = o.color != null ? paint(o.color, 0) : r() < 0.7 ? paint(0xf2f2ee, 0) : seededPaint(r, {});
      const L = 5.98, W = 2.05, hw = W / 2, zf = L / 2, zr = -L / 2, R = 0.36, fz = zf - 0.86, rz = fz - 3.75, top = 2.72;
      const body = sideExtrude([['m', zr + 0.05, 0.46], ['arch', rz, R + 0.05, R], ['arch', fz, R + 0.05, R], ['l', zf - 0.1, 0.46],
        ['q', zf, 0.5, zf, 0.7], ['l', zf - 0.02, 0.95], ['q', zf - 0.1, 1.1, zf - 0.55, 1.2], ['l', 1.95, 1.3], ['l', 1.22, 2.26],
        ['q', 1.1, top - 0.02, 0.85, top], ['l', zr + 0.12, top], ['q', zr, top, zr, top - 0.14], ['l', zr, 0.56], ['q', zr, 0.46, zr + 0.05, 0.46]],
      W, 0.09, P, { deform: planRound(zf, zr, 0.05, 0.5) }); G.add(body);
      const nose = snapper([body], 1, zf), tail = snapper([body], -1, zr);
      // unpainted lower cladding and a rub strip along each side
      for (const s of [1, -1]) {
        box(0.02, 0.16, 3.0, M.trim(), s * (hw + 0.004), 0.47, (fz + rz) / 2, 0.008, G);
        box(0.02, 0.06, 4.9, M.trim(), s * (hw + 0.006), 0.98, -0.2, 0.01, G);
      }
      // windscreen, raked, proud of the body line; cab side windows
      const ws = sideExtrude([['m', 1.99, 1.33], ['l', 1.24, 2.25], ['l', 1.2, 2.2], ['l', 1.94, 1.29]], W - 0.18, 0.02, M.glass());
      ws.position.set(0, 0.012, 0.012); G.add(ws);
      for (const s of [1, -1]) {
        sideWindow(G, [[1.86, 1.4], [1.25, 2.12], [1.12, 2.12], [1.02, 2.0], [1.02, 1.4]], s * hw, s);
      }
      // seams: cab door, sliding door and its track, rear doors
      seam(G, hw, 1.96, 0.5, 1.96, 1.3); seam(G, hw, 0.98, 0.5, 0.98, 2.2);
      seam(G, hw, 0.9, 0.5, 0.9, 2.2); seam(G, hw, -0.55, 0.5, -0.55, 2.2);
      for (const s of [1, -1]) box(0.02, 0.025, 1.6, M.trim(), s * (hw + 0.01), 1.9, -0.7, 0.008, G);   // slide track
      box(0.004, 2.0, 0.004, M.well(), 0, 0.55, zr - 0.001, 0, G);                                        // rear door split
      for (const s of [1, -1]) { box(0.02, 0.2, 0.05, M.satin(), s * 0.08, 1.2, zr - 0.01, 0.008, G); sideWindow2(G, s); }
      handle(G, hw, 1.2, 1.6, M.satin()); handle(G, hw, 1.2, 0.72, M.satin());
      mirror(G, hw, 1.4, 1.75, M.trim(), true);
      // nose: a big black grille and swept lamps, bumpers in unpainted black
      const nz = nose(0, 0.82);
      const gs = RB(1.1, 0.34, 0.06, 0.06, M.trim()); gs.position.set(0, 0.82, nz + 0.01); G.add(gs);
      for (let i = 0; i < 3; i++) box(1.0, 0.02, 0.03, M.satin(), 0, 0.71 + i * 0.1, nz + 0.04, 0.008, G);
      lamp(G, 0.32, 0.18, hw - 0.2, 0.95, nose, 'head');
      const fb = RB(W - 0.02, 0.3, 0.2, 0.06, M.trim()); fb.position.set(0, 0.53, zf - 0.03); G.add(fb);
      const rb = RB(W - 0.02, 0.22, 0.16, 0.05, M.trim()); rb.position.set(0, 0.5, zr + 0.02); G.add(rb);
      lamp(G, 0.1, 0.5, hw - 0.07, 1.05, tail, 'tail', -1);
      lamp(G, 0.2, 0.05, 0.25, top - 0.2, tail, 'tail', -1);
      plate(G, 0.75, zr - 0.005, -1); plate(G, 0.52, zf + 0.08, 1);
      function sideWindow2(G2, s) { sideWindowRear(G2, s); }
      function sideWindowRear(G2, s) {
        const pts = [[zr + 0.02, 1.45], [zr + 0.02, 2.2], [zr + 0.02, 2.2]];
        void pts;
        const gl = RB(0.8, 0.6, 0.02, 0.05, M.glass()); gl.position.set(s * 0.46, 1.8, zr - 0.012); G2.add(gl);
        const fr = RB(0.86, 0.66, 0.012, 0.06, M.trim()); fr.position.set(s * 0.46, 1.8, zr - 0.004); G2.add(fr);
      }
      if (o.lettering) for (const s of [1, -1]) {
        const sg = sign(o.lettering, '#1d2b44', null, 2.1, 0.42); sg.position.set(s * (hw + 0.004), 1.7, -1.75); sg.rotation.y = s * Math.PI / 2; G.add(sg);
      }
      box(W - 0.4, 0.25, L - 1.2, M.frame(), 0, 0.2, 0, 0.02, G);
      axle(G, fz, R, 0.235, W - 0.26, 'steel', M.steelWheel(), { rimR: 0.21 });
      axle(G, rz, R, 0.235, W - 0.26, 'steel', M.steelWheel(), { rimR: 0.21 });
      return G;
    },
  });

  /* =========================================================================================
   * SCHOOL BUS: Type C conventional, 72 passenger. 11.2 x 2.44 x 3.2 m. National School Bus
   * Glossy Yellow, black rub rails and window frames, stop arm on the driver's side.
   * ========================================================================================= */
  K.define('school_bus', {
    size: [2.9, 3.2, 11.2],
    options: { seed: 1, whiteRoof: 'auto', stopArm: false, district: null },
    note: 'Type C school bus (conventional hood), 11.2 m, dual rear wheels, 11 windows a side, stop arm (stopArm:true deploys it).',
    make(o, r) {
      const G = new THREE.Group();
      const Y = paint(0xf4ab00, 0), blk = M.trim();
      const L = 11.2, W = 2.44, hw = W / 2, zf = L / 2, zr = -L / 2, R = 0.51, fz = zf - 1.15, rz = fz - 6.1;
      const white = o.whiteRoof === 'auto' ? r() < 0.5 : !!o.whiteRoof;
      const bodyF = 3.95, floor = 0.95, top = 3.18;
      // body: a box with a big rounded roof, the rear arch cut in
      G.add(sideExtrude([['m', zr, 0.72], ['arch', rz, R + 0.07, R], ['l', bodyF - 0.3, 0.72], ['arch', fz, R + 0.08, R], ['l', bodyF, 0.72],
        ['l', bodyF, 1.88], ['l', bodyF - 0.16, 2.62], ['l', bodyF - 0.16, top - 0.3], ['q', bodyF - 0.16, top, bodyF - 0.46, top], ['l', zr + 0.3, top], ['q', zr, top, zr, top - 0.3]], W, 0.16, Y, { sizeK: 1, bevelSeg: 6 }));
      if (white) G.add(sideExtrude([['m', bodyF - 0.28, top - 0.1], ['l', zr + 0.28, top - 0.1], ['l', zr + 0.28, top + 0.004], ['l', bodyF - 0.28, top + 0.004]], W - 0.36, 0.06, paint(0xf2f1ec, 0)));
      // hood: narrower, with fenders over the front wheels
      const hood = sideExtrude([['m', bodyF - 0.02, 0.8], ['arch', fz, R + 0.08, R], ['l', zf - 0.25, 0.8], ['l', zf - 0.12, 0.85], ['l', zf - 0.1, 1.55],
        ['q', zf - 0.12, 1.7, zf - 0.35, 1.72], ['l', bodyF - 0.02, 1.86]], 2.3, 0.1, Y); G.add(hood);
      const nose = snapper([hood], 1, zf);
      // windscreen and front cap
      const ws = sideExtrude([['m', bodyF + 0.02, 1.92], ['l', bodyF - 0.135, 2.6], ['l', bodyF - 0.155, 2.6], ['l', bodyF, 1.92]], W - 0.3, 0.02, M.glass());
      G.add(ws);
      const cpost = RB(0.05, 0.72, 0.03, 0.01, blk); cpost.position.set(0, 2.26, bodyF - 0.06); cpost.rotation.x = -0.22; G.add(cpost);
      const cap = sign('SCHOOL BUS', '#111111', '#f4ab00', 1.2, 0.26); cap.position.set(0, 2.86, bodyF - 0.16 + 0.004); G.add(cap);
      const capR = sign('SCHOOL BUS', '#111111', '#f4ab00', 1.2, 0.26); capR.position.set(0, 2.84, zr - 0.012); capR.rotation.y = Math.PI; G.add(capR);
      // eight-way warning lamps, front and rear
      for (const z of [bodyF - 0.15, zr - 0.01]) for (const s of [1, -1]) {
        const d = z > 0 ? 1 : -1;
        for (const [x, m] of [[0.95, M.tail()], [0.72, M.amber()]]) {
          const hood = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.05, 24), blk); hood.rotation.x = Math.PI / 2; hood.position.set(s * x, 2.86, z); G.add(hood);
          const l = new THREE.Mesh(new THREE.SphereGeometry(0.085, 20, 10, 0, Math.PI * 2, 0, Math.PI / 2), m); l.rotation.x = d * Math.PI / 2; l.position.set(s * x, 2.86, z + d * 0.02); G.add(l);
        }
      }
      // rub rails: three black bands down both sides and across the tail
      for (const y of [1.02, 1.42, 1.8]) {
        for (const s of [1, -1]) box(0.035, 0.07, bodyF - zr - 0.3, blk, s * (hw + 0.012), y, (bodyF + zr) / 2 - 0.05, 0.012, G);
        box(W - 0.24, 0.07, 0.035, blk, 0, y, zr - 0.012, 0.012, G);
      }
      // passenger windows: split sash, black frames
      const nWin = 11, wz0 = 2.95, pitch = 0.74;
      for (let i = 0; i < nWin; i++) {
        const z1 = wz0 - i * pitch, z0 = z1 - 0.62;
        for (const s of [1, -1]) {
          if (s < 0 && i === 0) continue;            // the entry door is here on the curb side
          sideWindow(G, [[z0, 1.92], [z1, 1.92], [z1, 2.52], [z0, 2.52]], s * hw, s);
          box(0.03, 0.035, 0.62, blk, s * (hw + 0.018), 2.2, (z0 + z1) / 2, 0.008, G);        // sash rail
        }
      }
      // driver's window and the entry door (curb side, right, -x)
      sideWindow(G, [[bodyF - 0.72, 1.92], [bodyF - 0.12, 1.92], [bodyF - 0.12, 2.52], [bodyF - 0.72, 2.52]], hw, 1);
      for (const [z0, z1] of [[bodyF - 0.82, bodyF - 0.48], [bodyF - 0.46, bodyF - 0.12]]) {
        sideWindow(G, [[z0, 1.0], [z1, 1.0], [z1, 1.65], [z0, 1.65]], -hw, -1);
        sideWindow(G, [[z0, 1.72], [z1, 1.72], [z1, 2.55], [z0, 2.55]], -hw, -1);
      }
      // rear: emergency door with its window, tail lamps, the lettering, bumper
      sideWindowRearBus();
      function sideWindowRearBus() {
        const fr = RB(0.9, 1.9, 0.02, 0.03, blk); fr.position.set(0, 0.75 + 0.95, zr - 0.006); G.add(fr);
        const dp = RB(0.84, 1.84, 0.02, 0.02, Y); dp.position.set(0, 1.7, zr - 0.014); G.add(dp);
        const gl = RB(0.7, 0.8, 0.02, 0.04, M.glass()); gl.position.set(0, 2.1, zr - 0.024); G.add(gl);
        box(0.3, 0.04, 0.04, M.chrome(), 0.2, 1.5, zr - 0.03, 0.01, G);
        for (const s of [1, -1]) { const g2 = RB(0.5, 0.8, 0.02, 0.04, M.glass()); g2.position.set(s * 0.8, 2.1, zr - 0.012); G.add(g2); }
      }
      lamp(G, 0.2, 0.2, 0.95, 1.2, zr - 0.01, 'tail', -1); lamp(G, 0.2, 0.2, 0.95, 1.45, zr - 0.01, 'amber', -1);
      box(W + 0.04, 0.26, 0.18, blk, 0, 0.55, zr - 0.05, 0.03, G);
      box(2.3, 0.28, 0.2, blk, 0, 0.55, zf - 0.1, 0.03, G);
      plate(G, 0.95, zr - 0.02, -1);
      // grille and headlamps on the hood nose
      const gz = nose(0, 1.12);
      const gg = RB(1.0, 0.62, 0.05, 0.04, blk); gg.position.set(0, 1.12, gz + 0.01); G.add(gg);
      for (let i = 0; i < 6; i++) box(0.94, 0.02, 0.03, M.satin(), 0, 0.87 + i * 0.1, gz + 0.035, 0.005, G);
      lamp(G, 0.2, 0.2, 0.8, 1.2, nose, 'head');
      // stop arm on the driver's side (+x), folded flat unless deployed
      const arm = new THREE.Group();
      const oct = []; for (let i = 0; i < 8; i++) { const a = (i + 0.5) / 8 * Math.PI * 2; oct.push([Math.cos(a) * 0.23, Math.sin(a) * 0.23]); }
      const octM = TXT.extrude(oct, 0.012, K.mat('v-stopred', { color: 0xb3121a, roughness: 0.35 }), { bevel: false });
      arm.add(octM);
      const st = sign('STOP', '#ffffff', '#b3121a', 0.34, 0.12); st.position.z = 0.013; arm.add(st);
      const st2 = sign('STOP', '#ffffff', '#b3121a', 0.34, 0.12); st2.position.z = -0.001; st2.rotation.y = Math.PI; arm.add(st2);
      const pivot = new THREE.Group(); pivot.position.set(hw + 0.04, 1.62, bodyF - 0.95); G.add(pivot);
      arm.rotation.y = Math.PI / 2; arm.position.set(0, 0, -0.25);
      if (o.stopArm) { arm.rotation.y = 0; arm.position.set(0.28, 0, 0); }
      pivot.add(arm);
      // crossover mirrors on the fenders, west coast mirrors at the windscreen
      for (const s of [1, -1]) {
        bar([s * 1.0, 1.72, zf - 0.5], [s * 1.2, 2.05, zf - 0.3], 0.015, blk, G);
        const cm = new THREE.Mesh(new THREE.SphereGeometry(0.11, 20, 12), M.chrome()); cm.scale.z = 0.5; cm.position.set(s * 1.22, 2.1, zf - 0.28); G.add(cm);
        bar([s * hw, 2.2, bodyF - 0.1], [s * (hw + 0.25), 2.2, bodyF - 0.05], 0.015, blk, G);
        box(0.18, 0.38, 0.06, blk, s * (hw + 0.32), 2.0, bodyF - 0.05, 0.03, G);
      }
      if (o.district) for (const s of [1, -1]) {
        const d = sign(o.district, '#111111', null, 3.6, 0.26); d.position.set(s * (hw + 0.004), 2.72, -0.8); d.rotation.y = s * Math.PI / 2; G.add(d);
      }
      box(W - 0.4, 0.3, L - 1.6, M.frame(), 0, 0.42, -0.4, 0.02, G);
      axle(G, fz, R, 0.28, 2.1, 'truck', M.steelWheel(), { rimR: 0.29, wellW: 1.4 });
      axle(G, rz, R, 0.28, 2.1, 'truck', M.steelWheel(), { rimR: 0.29, dual: true, wellW: 1.0 });
      return G;
    },
  });

  /* =========================================================================================
   * SEMI TRUCK: sleeper tractor coupled to a 53 ft dry van. About 21.9 x 2.6 x 4.1 m.
   * ========================================================================================= */
  K.define('semi_truck', {
    size: [2.9, 4.1, 21.9],
    options: { seed: 1, color: null, trailer: true, trailerColor: 0xeeeeea, lettering: null },
    note: 'Class 8 sleeper tractor (long hood, chrome stacks and tanks) with a 53 ft dry van; trailer:false for bobtail. Origin at the centre of the coupled footprint.',
    make(o, r) {
      const G = new THREE.Group(), T = new THREE.Group();
      const P = o.color != null ? paint(o.color, 1) : paint(pick(r, [0xf0f0ec, 0x0f1012, 0x7c1416, 0x1b2f4f, 0x5c6066, 0x2e5a3a, 0xb4b8bc]), 1);
      const W = 2.44, hw = W / 2, R = 0.52;
      // tractor, local z: front bumper at 0, going back negative
      const steer = -1.35, d1 = -5.95, d2 = -7.28;
      // hood with the steer arch
      T.add(sideExtrude([['m', -1.95, 1.02], ['arch', steer, R + 0.1, R], ['l', -0.2, 1.02], ['l', -0.05, 1.05], ['l', 0.0, 1.9],
        ['q', -0.05, 2.08, -0.35, 2.1], ['l', -1.95, 2.26]], 2.14, 0.12, P, { sizeK: 0.9 }));
      // cab and sleeper with the roof fairing up to trailer height
      T.add(sideExtrude([['m', -4.75, 1.18], ['l', -1.92, 1.18], ['l', -1.92, 2.28], ['l', -2.3, 3.02], ['q', -2.45, 3.12, -2.7, 3.12],
        ['q', -3.2, 3.2, -3.5, 3.9], ['l', -4.68, 3.98], ['q', -4.75, 3.98, -4.75, 3.85]], W, 0.1, P, { sizeK: 0.8 }));
      const ws = sideExtrude([['m', -1.9, 2.3], ['l', -2.28, 3.02], ['l', -2.32, 3.0], ['l', -1.95, 2.28]], W - 0.2, 0.02, M.glass());
      ws.position.set(0, 0, 0.02); T.add(ws);
      for (const s of [1, -1]) {
        sideWindow(T, [[-2.0, 2.3], [-2.3, 2.92], [-2.95, 2.92], [-2.95, 2.3]], s * hw, s);
        sideWindow(T, [[-3.9, 2.55], [-3.55, 2.55], [-3.55, 2.75], [-3.9, 2.75]], s * hw, s);   // sleeper bunk window
        // side fairings under the cab and the steps
        box(0.06, 0.7, 2.2, P, s * (hw - 0.02), 0.5, -3.55, 0.03, T);
        for (const y of [0.55, 0.85]) box(0.3, 0.04, 0.5, M.chrome(), s * (hw - 0.1), y, -2.2, 0.01, T);
        // chrome fuel tank
        const tk = new THREE.Mesh(new THREE.CylinderGeometry(0.33, 0.33, 1.25, 36), M.chrome()); tk.rotation.x = Math.PI / 2; tk.position.set(s * (hw - 0.25), 0.72, -2.9); T.add(tk);
        for (const z of [-2.5, -3.3]) { const st = new THREE.Mesh(new THREE.TorusGeometry(0.335, 0.012, 6, 36), M.frame()); st.position.set(s * (hw - 0.25), 0.72, z); T.add(st); }
        // exhaust stack behind the sleeper, with a heat shield
        const stack = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 3.3, 24), M.chrome()); stack.position.set(s * (hw - 0.12), 2.35, -4.88); T.add(stack);
        const shield = new THREE.Mesh(new THREE.CylinderGeometry(0.115, 0.115, 1.0, 24), K.mat('v-shield', { color: 0x9da2a6, metalness: 0.9, roughness: 0.4 })); shield.position.set(s * (hw - 0.12), 2.2, -4.88); T.add(shield);
        // air cleaner canister beside the cowl
        const ac = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.8, 28), M.chrome()); ac.position.set(s * 1.12, 1.9, -1.75); T.add(ac);
        // mud flaps
        box(0.6, 0.62, 0.02, M.trim(), s * 0.93, 0.12, d2 - 0.75, 0, T);
        // fenders over the drive tandem (quarter fenders)
        box(0.66, 0.03, 0.6, M.chrome(), s * 0.93, 1.1, d1 + 0.45, 0.01, T);
      }
      seam(T, hw, -1.98, 1.2, -1.98, 2.3); seam(T, hw, -3.1, 1.2, -3.1, 2.9);
      handle(T, hw, 1.9, -2.9, M.chrome());
      mirror(T, hw, 2.3, -1.95, M.chrome(), true);
      // grille, bumper, headlamps, cab marker lamps
      const gr = RB(1.1, 0.95, 0.06, 0.05, M.chrome()); gr.position.set(0, 1.45, 0.01); T.add(gr);
      box(1.0, 0.86, 0.04, M.well(), 0, 1.02, 0.035, 0.01, T);
      for (let i = 0; i < 9; i++) box(0.98, 0.02, 0.02, M.chrome(), 0, 1.07 + i * 0.09, 0.05, 0.005, T);
      const fb = RB(2.4, 0.42, 0.3, 0.08, M.chrome()); fb.position.set(0, 0.72, 0.05); T.add(fb);
      lamp(T, 0.26, 0.18, 0.84, 1.5, 0.012, 'head');
      for (let i = -2; i <= 2; i++) { const m = RB(0.08, 0.04, 0.05, 0.015, M.amber()); m.position.set(i * 0.25, 3.14, -2.62); T.add(m); }
      // frame rails, fifth wheel, back of cab bits
      box(0.95, 0.28, 7.3, M.frame(), 0, 0.82, -3.8, 0.02, T);
      box(1.2, 0.12, 1.1, M.frame(), 0, 1.1, -6.2, 0.03, T);
      const deck = RB(2.3, 0.05, 0.4, 0.02, M.frame()); deck.position.set(0, 1.22, -4.95); T.add(deck);
      axle(T, steer, R, 0.3, 2.06, 'truck', M.alloy(), { rimR: 0.3, wellW: 1.4 });
      axle(T, d1, R, 0.28, 2.3, 'truck', M.alloy(), { rimR: 0.3, dual: true, well: false });
      axle(T, d2, R, 0.28, 2.3, 'truck', M.alloy(), { rimR: 0.3, dual: true, well: false });
      G.add(T);
      if (o.trailer !== false) {
        const TR = new THREE.Group(), TP = paint(o.trailerColor != null ? o.trailerColor : 0xeeeeea, 0);
        const tf = -5.1, tl = 16.15, tb = tf - tl, TW = 2.59, thw = TW / 2, fl = 1.24, tt = 4.1;
        const bx = RB(TW, tt - fl, tl, 0.05, TP); bx.position.set(0, (fl + tt) / 2, tf - tl / 2); TR.add(bx);
        // side panel seams, the logistic posts of a plate van
        const post = K.mat('v-post', { color: 0xc9ccd0, metalness: 0.6, roughness: 0.35 });
        const posts = [];
        for (let z = tf - 0.6; z > tb + 0.4; z -= 1.22) for (const s of [1, -1]) posts.push(K.box(0.012, tt - fl - 0.3, 0.05, post, s * (thw + 0.004), fl + 0.15, z));
        TR.add(K.merge(posts, post));
        for (const s of [1, -1]) {
          box(0.05, 0.12, tl, post, s * (thw + 0.01), fl, tf - tl / 2, 0.01, TR);                 // bottom rail
          box(0.04, 0.06, tl, post, s * (thw + 0.005), tt - 0.06, tf - tl / 2, 0.01, TR);          // top rail
          for (let z = tf - 1.5; z > tb + 1; z -= 3) { const ml = RB(0.04, 0.05, 0.08, 0.01, M.amber()); ml.position.set(s * (thw + 0.02), fl + 0.2, z); TR.add(ml); }
          // side skirt
          box(0.02, 0.62, 7.0, K.mat('v-skirt', { color: 0xd8d8d4, roughness: 0.5 }), s * (thw - 0.08), fl - 0.64, tf - 6.2, 0.005, TR);
          // landing gear
          box(0.1, fl - 0.1, 0.1, M.frame(), s * 0.75, 0.1, tf - 3.4, 0.01, TR);
          box(0.3, 0.05, 0.3, M.frame(), s * 0.75, 0.05, tf - 3.4, 0.01, TR);
        }
        // rear doors: hinges, lock rods, lamps, underride guard
        const rz0 = tb - 0.005;
        box(0.006, tt - fl - 0.2, 0.01, M.well(), 0, fl + 0.1, rz0, 0, TR);
        for (const x of [-1.1, -0.75, 0.75, 1.1]) {
          box(0.028, tt - fl - 0.35, 0.03, M.chrome(), x, fl + 0.15, rz0 - 0.02, 0.01, TR);
          box(0.12, 0.06, 0.05, post, x, fl + 1.1, rz0 - 0.03, 0.01, TR);
        }
        for (const s of [1, -1]) for (const y of [fl + 0.4, fl + 1.4, fl + 2.4]) box(0.14, 0.1, 0.04, post, s * (thw - 0.07), y, rz0 - 0.02, 0.01, TR);
        lamp(TR, 0.1, 0.18, thw - 0.25, fl - 0.1, rz0 - 0.02, 'tail', -1);
        for (let i = -1; i <= 1; i++) { const m = RB(0.08, 0.04, 0.04, 0.01, M.tail()); m.position.set(i * 0.2, tt - 0.12, rz0 - 0.02); TR.add(m); }
        box(2.3, 0.14, 0.12, M.frame(), 0, 0.46, tb + 0.15, 0.02, TR);
        for (const s of [1, -1]) box(0.1, 0.62, 0.1, M.frame(), s * 0.7, 0.5, tb + 0.25, 0.01, TR);
        // floor frame and the slider tandem
        box(1.0, 0.3, tl - 1, M.frame(), 0, fl - 0.3, tf - tl / 2, 0.02, TR);
        axle(TR, tb + 1.9, R, 0.28, 2.3, 'truck', M.alloy(), { rimR: 0.3, dual: true, well: false });
        axle(TR, tb + 3.12, R, 0.28, 2.3, 'truck', M.alloy(), { rimR: 0.3, dual: true, well: false });
        if (o.lettering) for (const s of [1, -1]) {
          const lg = sign(o.lettering, '#1d2b44', null, 9, 1.1); lg.position.set(s * (thw + 0.012), 2.7, tf - tl / 2); lg.rotation.y = s * Math.PI / 2; TR.add(lg);
        }
        G.add(TR);
      }
      // centre the coupled footprint on the origin
      const zmin = o.trailer !== false ? -21.25 : -7.9, zmax = 0.25;
      G.children.forEach((c) => { c.position.z -= (zmin + zmax) / 2; });
      return G;
    },
  });

  /* =========================================================================================
   * UTILITY BUCKET TRUCK: medium-duty conventional cab, service body with compartments,
   * insulated articulating boom and a fibreglass bucket. About 9.6 x 2.5 x 3.6 m stowed.
   * ========================================================================================= */
  K.define('utility_bucket_truck', {
    size: [2.9, 3.6, 9.6],
    options: { seed: 1, boom: 0, swing: 0, color: 0xf0f0ec, lettering: null },
    note: 'Lineman bucket truck. boom 0 (stowed) to 1 (raised about 11 m platform height); swing rotates the turret (radians). Outriggers go down when raised.',
    make(o, r) {
      const G = new THREE.Group(), P = paint(o.color != null ? o.color : 0xf0f0ec, 0);
      const W = 2.44, hw = W / 2, R = 0.5, zf = 4.8, steer = 3.7, rear = -1.5, zr = -4.8;
      // hood
      G.add(sideExtrude([['m', 2.05, 0.95], ['arch', steer, R + 0.1, R], ['l', zf - 0.15, 0.95], ['l', zf, 1.0], ['l', zf, 1.6],
        ['q', zf - 0.02, 1.76, zf - 0.3, 1.78], ['l', 2.05, 1.92]], 2.2, 0.12, P, { sizeK: 0.9 }));
      // cab
      G.add(sideExtrude([['m', 0.9, 1.05], ['l', 2.08, 1.05], ['l', 2.08, 1.95], ['l', 1.8, 2.72], ['q', 1.72, 2.82, 1.55, 2.82], ['l', 0.95, 2.82], ['q', 0.9, 2.82, 0.9, 2.72]], W, 0.1, P));
      const ws = sideExtrude([['m', 2.1, 1.98], ['l', 1.83, 2.7], ['l', 1.79, 2.7], ['l', 2.05, 1.96]], W - 0.2, 0.02, M.glass()); G.add(ws);
      for (const s of [1, -1]) sideWindow(G, [[1.95, 1.98], [1.76, 2.62], [1.02, 2.62], [1.02, 1.98]], s * hw, s);
      seam(G, hw, 2.0, 1.1, 2.0, 1.95); seam(G, hw, 1.0, 1.1, 1.0, 2.65);
      handle(G, hw, 1.85, 1.2, M.satin());
      mirror(G, hw, 2.0, 1.95, M.trim(), true);
      const gr = RB(1.0, 0.55, 0.05, 0.04, M.chrome()); gr.position.set(0, 1.22, zf + 0.01); G.add(gr);
      box(0.92, 0.48, 0.04, M.well(), 0, 0.99, zf + 0.03, 0.01, G);
      for (let i = 0; i < 5; i++) box(0.9, 0.018, 0.02, M.chrome(), 0, 1.03 + i * 0.1, zf + 0.05, 0.005, G);
      lamp(G, 0.24, 0.16, 0.8, 1.3, zf + 0.012, 'head');
      box(2.4, 0.3, 0.26, M.trim(), 0, 0.7, zf - 0.02, 0.05, G);
      for (let i = -1; i <= 1; i++) { const m = RB(0.08, 0.04, 0.04, 0.015, M.amber()); m.position.set(i * 0.3, 2.84, 1.62); G.add(m); }
      // amber light bar on the cab roof
      const lb = RB(1.2, 0.1, 0.25, 0.04, M.amber()); lb.position.set(0, 2.9, 1.3); G.add(lb);
      // service body: compartments either side of a flat bed, doors with handles and hinges
      const sb0 = 0.75, cH = 1.1, cD = 0.5, sy = 0.95;
      for (const s of [1, -1]) {
        const cb = RB(cD, cH, sb0 - zr, 0.03, P); cb.position.set(s * (hw - cD / 2), sy + cH / 2, (sb0 + zr) / 2); G.add(cb);
        const doors = [[sb0 - 0.05, 0.1], [-0.1, -0.9], [-2.15, -3.0], [-3.1, zr + 0.05]];
        for (const [a, b] of doors) {
          seam(G, hw, a, sy + 0.05, a, sy + cH - 0.05); seam(G, hw, b, sy + 0.05, b, sy + cH - 0.05);
          box(0.02, 0.03, 0.14, M.chrome(), s * (hw + 0.01), sy + cH * 0.6, (a + b) / 2, 0.01, G);
        }
        box(0.04, 0.03, sb0 - zr, M.satin(), s * (hw + 0.005), sy + cH - 0.02, (sb0 + zr) / 2, 0.01, G);
        // rear wheel opening cut: a dark arch face over the dual wheels
        box(0.02, 0.4, 1.35, M.well(), s * (hw + 0.004), sy, rear, 0.01, G);
        // outrigger boxes behind the cab and at the tail
        const legY = (o.boom || 0) > 0.02 ? 0.02 : 0.45;
        for (const z of [0.6, zr + 0.35]) {
          box(0.15, 0.5, 0.2, K.mat('v-outrig', { color: 0x2b2d30, roughness: 0.6, metalness: 0.4 }), s * (hw + 0.1), legY + 0.35, z, 0.02, G);
          box(0.1, sy - legY, 0.1, M.frame(), s * (hw + 0.1), legY, z, 0.01, G);
          box(0.35, 0.04, 0.35, M.frame(), s * (hw + 0.1), legY - 0.02, z, 0.01, G);
        }
      }
      box(W - 2 * cD, 0.08, sb0 - zr, K.mat('v-tread', { color: 0x9a9da1, metalness: 0.8, roughness: 0.4 }), 0, sy + 0.25, (sb0 + zr) / 2, 0.01, G);
      box(W, 0.2, 0.15, M.trim(), 0, 0.72, zr - 0.05, 0.03, G);
      lamp(G, 0.12, 0.12, hw - 0.12, 1.2, zr - 0.02, 'tail', -1);
      if (o.lettering) for (const s of [1, -1]) {
        const lg = sign(o.lettering, '#16325c', null, 2.6, 0.32); lg.position.set(s * (hw + 0.012), sy + cH * 0.8, -1.9); lg.rotation.y = s * Math.PI / 2; G.add(lg);
      }
      // aerial device: turret behind the cab, lower boom (steel), upper boom (insulated), bucket
      const boomM = paint(0xf2f2ee, 0), fg = K.mat('v-fibre', { color: 0xf2c200, roughness: 0.4, clearcoat: 0.6, clearcoatRoughness: 0.3 }, true);
      const turret = new THREE.Group(); turret.position.set(0, sy + 0.3, 0.2); turret.rotation.y = o.swing || 0; G.add(turret);
      const ped = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.4, 0.6, 32), K.mat('v-ped', { color: 0x2b2d30, metalness: 0.5, roughness: 0.5 })); ped.position.y = 0.3; turret.add(ped);
      const k = clamp01(o.boom || 0);
      const lowA = k * 0.95;                                       // lower boom elevation, pointing rearward
      const absUp = Math.PI + (2.4 - Math.PI) * k;                 // upper boom: folded flat (pi) to 42 deg up, reaching forward
      const lower = new THREE.Group(); lower.position.y = 0.75; lower.rotation.x = lowA; turret.add(lower);
      const lb2 = RB(0.34, 0.3, 4.1, 0.05, boomM); lb2.position.set(0, 0, -2.0); lower.add(lb2);
      bar([0, -0.12, -0.25], [0, -0.1, -1.7], 0.07, M.chrome(), lower);
      const elbow = new THREE.Group(); elbow.position.set(0, 0, -4.0); lower.add(elbow);
      const knuckle = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.72, 24), boomM); knuckle.rotation.z = Math.PI / 2; knuckle.position.x = 0.18; elbow.add(knuckle);
      const upper = new THREE.Group(); upper.rotation.x = absUp - lowA; elbow.add(upper);
      // the insulated upper boom rides beside the lower, so it can fold flat over it
      const ub = RB(0.28, 0.26, 4.1, 0.06, fg); ub.position.set(0.34, 0, -2.05); upper.add(ub);
      const band = RB(0.3, 0.28, 0.5, 0.06, M.trim()); band.position.set(0.34, 0, -0.5); upper.add(band);
      // the platform: a fibreglass bucket kept level whatever the booms do
      const bk = new THREE.Group(); bk.position.set(0.34, 0, -4.15); upper.add(bk);
      const lv = new THREE.Group(); lv.rotation.x = -absUp; bk.add(lv);
      const bucket = RB(0.62, 1.05, 0.62, 0.07, fg); bucket.position.set(0, -0.35, 0.4); lv.add(bucket);
      const rim = RB(0.66, 0.06, 0.66, 0.03, M.trim()); rim.position.set(0, 0.18, bucket.position.z); lv.add(rim);
      if (k > 0.3) {       // a lineman in the bucket
        const man = K.registry.person ? K.make('person', { seed: 7, role: 'worker', pose: 'look_up' }) : null;
        if (man) { man.position.set(0, -0.85, bucket.position.z); lv.add(man); }
      }
      // boom rest post at the tail when stowed
      box(0.12, 1.05, 0.12, M.frame(), 0, sy + 0.3, zr + 0.3, 0.01, G);
      box(0.4, 0.06, 0.2, M.frame(), 0, sy + 1.33, zr + 0.3, 0.01, G);
      box(0.95, 0.28, 9.0, M.frame(), 0, 0.62, 0, 0.02, G);
      axle(G, steer, R, 0.28, 2.06, 'truck', M.steelWheel(), { rimR: 0.29, wellW: 1.4 });
      axle(G, rear, R, 0.28, 2.3, 'truck', M.steelWheel(), { rimR: 0.29, dual: true, wellW: 1.0 });
      return G;
    },
  });

  // every vehicle is returned merged by material (one draw call each); option-driven poses are already applied
  for (const n of ['pickup', 'sedan', 'suv', 'delivery_van', 'school_bus', 'semi_truck', 'utility_bucket_truck']) {
    const spec = K.registry[n], mk = spec.make;
    spec.make = (o, r) => mergeByMaterial(mk(o, r));
  }
}
