/* kit/interior.js, see assets/js/txkit.js for the conventions.
 *
 * The rooms decisions are made in: a commissioners court dais, the lectern the public speaks
 * from, the rows it sits in, the office the paperwork lives in, and the server row the paperwork
 * is about. Interior frames stand in a room built by TXT.interior; these models furnish it.
 * Every model: metres, y up, base on y = 0, FRONT faces +z (a dais faces its audience, a chair
 * faces the way its sitter looks, a rack shows its server fronts).
 */
export function install(K, THREE, TXT) {
  const TAU = Math.PI * 2;

  /* ---- local materials and textures (cached here, keyed by our own strings) ---------------- */
  const MATS = new Map();
  function mat(key0, params, physical) {
    const key = K.matKey(key0, params, physical);
    if (MATS.has(key)) return MATS.get(key);
    const P = Object.assign({ roughness: 0.8, metalness: 0 }, params || {});
    const m = physical ? new THREE.MeshPhysicalMaterial(P) : new THREE.MeshStandardMaterial(P);
    MATS.set(key, m);
    return m;
  }
  const TEX = new Map();
  function ltex(key, paint, opts, size, linear) {
    const k = key + '|' + JSON.stringify(opts || {});
    if (TEX.has(k)) return TEX.get(k);
    const W = (size && size[0]) || 512, H = (size && size[1]) || W;
    const c = document.createElement('canvas'); c.width = W; c.height = H;
    paint(c.getContext('2d'), W, H, K.rng(31 + key.length * 7 + (opts && opts.seed ? opts.seed * 101 : 0)), opts || {});
    const t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8;
    if (!linear) t.colorSpace = THREE.SRGBColorSpace;
    TEX.set(k, t);
    return t;
  }
  const css = (hex) => '#' + new THREE.Color(hex).getHexString();
  function shadeCss(hex, k) {
    const c = new THREE.Color(hex);
    return 'rgb(' + [c.r, c.g, c.b].map((v) => Math.max(0, Math.min(255, Math.round(v * 255 * k)))).join(',') + ')';
  }

  // Straight grained veneer: grain runs along U. Tileable both ways.
  function paintVeneer(x, W, H, r, o) {
    const base = o.color || '#6b4426';
    x.fillStyle = base; x.fillRect(0, 0, W, H);
    // soft figure bands
    for (let i = 0; i < 18; i++) {
      const y0 = r() * H, h = 10 + r() * 60;
      x.fillStyle = r() < 0.5 ? 'rgba(30,14,4,' + (0.04 + r() * 0.08) + ')' : 'rgba(255,215,160,' + (0.03 + r() * 0.06) + ')';
      for (const off of [-H, 0, H]) x.fillRect(0, y0 + off, W, h);
    }
    for (let i = 0; i < 170; i++) {
      const y0 = r() * H, a = 1.5 + r() * 9, f = 1 + Math.floor(r() * 3), ph = r() * TAU;
      x.strokeStyle = r() < 0.65 ? 'rgba(35,16,4,' + (0.06 + r() * 0.16) + ')' : 'rgba(255,225,180,' + (0.03 + r() * 0.07) + ')';
      x.lineWidth = 0.6 + r() * 2.4;
      for (const off of [-H, 0, H]) {
        x.beginPath();
        for (let px = 0; px <= W; px += 8) {
          const y = y0 + off + a * Math.sin(px / W * TAU * f + ph) + a * 0.35 * Math.sin(px / W * TAU * (f + 2) + ph * 1.7);
          if (px) x.lineTo(px, y); else x.moveTo(px, y);
        }
        x.stroke();
      }
    }
    for (let i = 0; i < 2600; i++) { x.fillStyle = 'rgba(25,12,3,' + (0.08 + r() * 0.16) + ')'; x.fillRect(r() * W, r() * H, 2 + r() * 7, 1); }
  }
  // Upholstery weave, near white so the material colour carries the hue.
  function paintWeave(x, W, H, r) {
    x.fillStyle = '#e6e6e6'; x.fillRect(0, 0, W, H);
    for (let y = 0; y < H; y += 4) for (let xx = 0; xx < W; xx += 4) {
      const k = ((xx / 4 + y / 4) % 2 ? 0.9 : 1.0) * (0.9 + r() * 0.12);
      const v = Math.round(225 * k); x.fillStyle = 'rgb(' + v + ',' + v + ',' + v + ')'; x.fillRect(xx, y, 4, 4);
    }
  }
  // Chair mesh (alpha): a woven grid, open cells.
  function paintMesh(x, W, H) {
    x.fillStyle = '#000'; x.fillRect(0, 0, W, H); x.fillStyle = '#fff';
    const p = 8;
    for (let y = 0; y < H; y += p) x.fillRect(0, y, W, 3);
    for (let xx = 0; xx < W; xx += p) x.fillRect(xx, 0, 3, H);
  }
  // Paper edges: many fine sheet lines along U.
  function paintSheets(x, W, H, r) {
    x.fillStyle = '#f2f0ea'; x.fillRect(0, 0, W, H);
    for (let y = 0; y < H; y += 2) { x.fillStyle = 'rgba(0,0,0,' + (0.03 + r() * 0.12) + ')'; x.fillRect(0, y, W, 1); }
  }
  // A printed page: margins, a heading bar, paragraphs of grey text lines. No legible words.
  function paintPage(x, W, H, r, o) {
    x.fillStyle = o.paper || '#f4f2ec'; x.fillRect(0, 0, W, H);
    const m = W * 0.12;
    let y = H * 0.09;
    x.fillStyle = 'rgba(30,30,35,0.8)'; x.fillRect(m, y, W * (0.35 + r() * 0.25), H * 0.018); y += H * 0.05;
    while (y < H * 0.9) {
      const lines = 3 + Math.floor(r() * 6);
      for (let i = 0; i < lines && y < H * 0.9; i++) {
        const len = i === lines - 1 ? 0.3 + r() * 0.4 : 0.92 + r() * 0.08;
        x.fillStyle = 'rgba(40,40,45,' + (0.45 + r() * 0.15) + ')';
        x.fillRect(m, y, (W - 2 * m) * len, H * 0.0075); y += H * 0.019;
      }
      y += H * 0.02;
    }
    x.fillStyle = 'rgba(40,40,45,0.5)'; x.fillRect(W / 2 - 8, H * 0.95, 16, H * 0.007);
  }
  // A screen: a generic app, no words and no numerals. kind: doc | sheet | chart | dash
  function paintScreen(x, W, H, r, o) {
    const kind = o.kind || 'doc', dark = !!o.dark;
    const bg = dark ? '#1d2127' : '#f3f4f6', panel = dark ? '#262b33' : '#ffffff', ink = dark ? 'rgba(220,225,232,' : 'rgba(40,46,56,';
    x.fillStyle = bg; x.fillRect(0, 0, W, H);
    x.fillStyle = dark ? '#14171b' : '#e3e6ea'; x.fillRect(0, 0, W, H * 0.06);                 // title bar
    ['#ec6a5e', '#f4bf4f', '#61c554'].forEach((c, i) => { x.fillStyle = c; x.beginPath(); x.arc(W * 0.02 + i * W * 0.022, H * 0.03, H * 0.011, 0, TAU); x.fill(); });
    x.fillStyle = dark ? '#1a1e23' : '#eceef1'; x.fillRect(0, H * 0.06, W * 0.18, H);           // sidebar
    for (let i = 0; i < 9; i++) { x.fillStyle = ink + (i === 2 ? 0.8 : 0.35) + ')'; x.fillRect(W * 0.02, H * (0.11 + i * 0.055), W * (0.08 + r() * 0.07), H * 0.012); }
    x.fillStyle = '#3b6fd8'; x.fillRect(0, H * (0.1 + 2 * 0.055) - H * 0.012, W * 0.004, H * 0.035);
    const X0 = W * 0.21, X1 = W * 0.97;
    if (kind === 'doc') {
      x.fillStyle = panel; x.fillRect(X0 + W * 0.08, H * 0.1, X1 - X0 - W * 0.16, H * 0.95);
      let y = H * 0.16; x.fillStyle = ink + '0.85)'; x.fillRect(X0 + W * 0.13, y, W * 0.3, H * 0.022); y += H * 0.06;
      while (y < H * 0.95) { const n = 3 + Math.floor(r() * 4);
        for (let i = 0; i < n; i++) { x.fillStyle = ink + '0.4)'; x.fillRect(X0 + W * 0.13, y, (X1 - X0 - W * 0.26) * (i === n - 1 ? 0.5 : 0.97), H * 0.011); y += H * 0.028; }
        y += H * 0.03; }
    } else if (kind === 'sheet') {
      x.fillStyle = panel; x.fillRect(X0, H * 0.1, X1 - X0, H * 0.86);
      const cw = (X1 - X0) / 9, rh = H * 0.04;
      for (let j = 0; j < 21; j++) for (let i = 0; i < 9; i++) {
        const yy = H * 0.1 + j * rh, xx = X0 + i * cw;
        if (j === 0 || i === 0) { x.fillStyle = dark ? '#303640' : '#e8ebef'; x.fillRect(xx, yy, cw, rh); }
        else if (r() < 0.7) { x.fillStyle = ink + '0.35)'; x.fillRect(xx + cw * (i > 2 ? 0.35 : 0.08), yy + rh * 0.38, cw * (i > 2 ? 0.55 : 0.7) * (0.6 + r() * 0.4), rh * 0.26); }
      }
      x.strokeStyle = dark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.1)'; x.lineWidth = 1;
      for (let j = 0; j <= 21; j++) { x.beginPath(); x.moveTo(X0, H * 0.1 + j * rh); x.lineTo(X1, H * 0.1 + j * rh); x.stroke(); }
      for (let i = 0; i <= 9; i++) { x.beginPath(); x.moveTo(X0 + i * cw, H * 0.1); x.lineTo(X0 + i * cw, H * 0.94); x.stroke(); }
      x.strokeStyle = '#2f7d4f'; x.lineWidth = 3; x.strokeRect(X0 + cw * 3, H * 0.1 + rh * 5, cw, rh);
    } else {
      // chart / dash: cards, a line chart, a bar chart
      const card = (cx, cy, cw, ch) => { x.fillStyle = panel; x.fillRect(cx, cy, cw, ch); };
      const cw = (X1 - X0 - W * 0.03) / 4;
      for (let i = 0; i < 4; i++) { card(X0 + i * (cw + W * 0.01), H * 0.1, cw, H * 0.14);
        x.fillStyle = ink + '0.35)'; x.fillRect(X0 + i * (cw + W * 0.01) + W * 0.012, H * 0.13, cw * 0.4, H * 0.012);
        x.fillStyle = ink + '0.85)'; x.fillRect(X0 + i * (cw + W * 0.01) + W * 0.012, H * 0.17, cw * (0.3 + r() * 0.3), H * 0.035); }
      card(X0, H * 0.27, (X1 - X0) * 0.62, H * 0.68);
      const gx0 = X0 + W * 0.02, gx1 = X0 + (X1 - X0) * 0.62 - W * 0.02, gy0 = H * 0.33, gy1 = H * 0.9;
      x.strokeStyle = dark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.07)'; x.lineWidth = 1;
      for (let j = 0; j < 6; j++) { const yy = gy0 + (gy1 - gy0) * j / 5; x.beginPath(); x.moveTo(gx0, yy); x.lineTo(gx1, yy); x.stroke(); }
      const series = (col, off) => { x.strokeStyle = col; x.lineWidth = 3; x.beginPath(); let v = 0.5 + off;
        for (let i = 0; i <= 40; i++) { v = Math.max(0.08, Math.min(0.95, v + (r() - 0.45) * 0.08)); const xx = gx0 + (gx1 - gx0) * i / 40, yy = gy1 - (gy1 - gy0) * v; if (i) x.lineTo(xx, yy); else x.moveTo(xx, yy); } x.stroke(); };
      series('#3b82f6', 0); series('#e0a33f', -0.25);
      const bx0 = X0 + (X1 - X0) * 0.64; card(bx0, H * 0.27, X1 - bx0, H * 0.68);
      for (let i = 0; i < 7; i++) { const bh = H * (0.1 + r() * 0.4); x.fillStyle = i === 3 ? '#e0a33f' : '#3b82f6';
        x.fillRect(bx0 + W * 0.02 + i * (X1 - bx0 - W * 0.04) / 7, H * 0.9 - bh, (X1 - bx0 - W * 0.04) / 7 * 0.6, bh); }
    }
  }

  const M = {
    veneer: (col) => uvm(mat('veneer' + col, { color: 0xffffff, roughness: 0.58, map: ltex('veneer', paintVeneer, { color: css(col) }) }), 1.2),
    fabric: (col) => uvm(mat('fabric' + col, { color: col, roughness: 0.95, map: ltex('weave', paintWeave, {}, [256, 256]) }), 0.3),
    leather: (col) => mat('leather' + col, { color: col, roughness: 0.46, clearcoat: 0.25, clearcoatRoughness: 0.5 }, true),
    plastic: (col) => mat('plastic' + col, { color: col != null ? col : 0x1b1c1e, roughness: 0.55 }),
    chrome: () => mat('chrome', { color: 0xd9dde0, metalness: 1, roughness: 0.14 }),
    alu: (col) => mat('alu' + col, { color: col != null ? col : 0xbfc2c5, metalness: 0.9, roughness: 0.32 }),
    steel: (col) => mat('steel' + col, { color: col, metalness: 0.35, roughness: 0.48 }),
    brass: () => mat('brass', { color: 0xc9a25a, metalness: 1, roughness: 0.28 }),
    bronze: () => mat('bronze', { color: 0x8a6436, metalness: 1, roughness: 0.38 }),
    black: () => mat('blackmatte', { color: 0x141416, roughness: 0.6 }),
    rubber: () => mat('rubber', { color: 0x1a1a1b, roughness: 0.85 }),
  };
  function uvm(m, metres) { m.userData.uvm = metres; return m; }

  /* ---- geometry helpers ------------------------------------------------------------------ */
  function rbox(w, h, d, r, material, x, y0, z, parent, seg) {
    const m = TXT.roundedBox(w, h, d, r, material, { segments: seg || 2 });
    if (material.userData.uvm) K.uvBox(m.geometry, material.userData.uvm);
    m.position.set(x || 0, (y0 || 0) + h / 2, z || 0);
    if (parent) parent.add(m);
    return m;
  }
  function box(w, h, d, material, x, y0, z, parent) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), material);
    if (material.userData && material.userData.uvm) K.uvBox(m.geometry, material.userData.uvm);
    m.position.set(x || 0, (y0 || 0) + h / 2, z || 0);
    if (parent) parent.add(m);
    return m;
  }
  function cyl(rt, rb, h, material, x, y0, z, seg, parent) { return K.cyl(rt, rb, h, material, x, y0, z, seg || 20, parent); }
  function deform(geo, fn) {
    const p = geo.attributes.position, v = new THREE.Vector3();
    for (let i = 0; i < p.count; i++) { v.fromBufferAttribute(p, i); fn(v); p.setXYZ(i, v.x, v.y, v.z); }
    p.needsUpdate = true; smoothNormals(geo); return geo;
  }
  // Weld by position and average face normals: smooth shading across a deformed rounded box.
  function smoothNormals(geo) {
    const p = geo.attributes.position, idx = geo.index;
    const key = (i) => Math.round(p.getX(i) * 1e4) + ',' + Math.round(p.getY(i) * 1e4) + ',' + Math.round(p.getZ(i) * 1e4);
    const acc = new Map(), keys = new Array(p.count);
    for (let i = 0; i < p.count; i++) { keys[i] = key(i); if (!acc.has(keys[i])) acc.set(keys[i], new THREE.Vector3()); }
    const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3(), n = new THREE.Vector3();
    const tri = idx ? idx.count / 3 : p.count / 3;
    for (let t = 0; t < tri; t++) {
      const i0 = idx ? idx.getX(t * 3) : t * 3, i1 = idx ? idx.getX(t * 3 + 1) : t * 3 + 1, i2 = idx ? idx.getX(t * 3 + 2) : t * 3 + 2;
      a.fromBufferAttribute(p, i0); b.fromBufferAttribute(p, i1); c.fromBufferAttribute(p, i2);
      n.subVectors(c, b).cross(a.clone().sub(b));
      acc.get(keys[i0]).add(n); acc.get(keys[i1]).add(n); acc.get(keys[i2]).add(n);
    }
    const nor = new Float32Array(p.count * 3);
    for (let i = 0; i < p.count; i++) { const v = acc.get(keys[i]).clone().normalize(); nor[i * 3] = v.x; nor[i * 3 + 1] = v.y; nor[i * 3 + 2] = v.z; }
    geo.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
    return geo;
  }
  function tube(pts, r, material, seg, radial, parent) {
    const m = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts.map((p) => new THREE.Vector3(p[0], p[1], p[2]))),
      seg || 32, r, radial || 8, false), material);
    if (parent) parent.add(m);
    return m;
  }
  function lathe(profile, material, seg, parent) {
    const m = new THREE.Mesh(new THREE.LatheGeometry(profile.map((p) => new THREE.Vector2(p[0], p[1])), seg || 48), material);
    if (parent) parent.add(m);
    return m;
  }
  /* Merge a built group into one mesh per material (world transforms relative to the group). */
  function bake(group) {
    group.updateMatrixWorld(true);
    const inv = new THREE.Matrix4().copy(group.matrixWorld).invert();
    const by = new Map();
    group.traverse((m) => {
      if (!m.isMesh) return;
      const g = (m.geometry.index ? m.geometry.toNonIndexed() : m.geometry.clone());
      g.applyMatrix4(new THREE.Matrix4().multiplyMatrices(inv, m.matrixWorld));
      if (!by.has(m.material)) by.set(m.material, []);
      by.get(m.material).push(g);
    });
    const out = [];
    for (const [material, gs] of by) {
      let n = 0; gs.forEach((g) => { n += g.attributes.position.count; });
      const pos = new Float32Array(n * 3), nor = new Float32Array(n * 3), uv = new Float32Array(n * 2);
      let o = 0;
      gs.forEach((g) => {
        pos.set(g.attributes.position.array, o * 3);
        if (!g.attributes.normal) g.computeVertexNormals();
        nor.set(g.attributes.normal.array, o * 3);
        if (g.attributes.uv) uv.set(g.attributes.uv.array, o * 2);
        o += g.attributes.position.count; g.dispose();
      });
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
      geo.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
      geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
      out.push({ geo, material });
    }
    return out;
  }
  // Instance a baked part list at matrices.
  function instanceBaked(parts, matrices, parent) {
    parts.forEach(({ geo, material }) => {
      const im = new THREE.InstancedMesh(geo, material, matrices.length);
      matrices.forEach((M4, i) => im.setMatrixAt(i, M4));
      im.instanceMatrix.needsUpdate = true;
      parent.add(im);
    });
  }
  const mat4 = (x, y, z, ry, s) => new THREE.Matrix4().compose(new THREE.Vector3(x, y, z),
    new THREE.Quaternion().setFromEuler(new THREE.Euler(0, ry || 0, 0)), new THREE.Vector3(s || 1, s || 1, s || 1));
  // Recentre a group's contents so the footprint centre is the origin and the base is y = 0.
  function centre(g) {
    const bb = new THREE.Box3().setFromObject(g), c = new THREE.Vector3(); bb.getCenter(c);
    const inner = new THREE.Group(); while (g.children.length) inner.add(g.children[0]);
    inner.position.set(-c.x, -bb.min.y, -c.z); g.add(inner); return g;
  }

  /* ---- shared parts ---------------------------------------------------------------------- */
  // Gooseneck microphone. Base at origin, the head leans toward -z (the talker).
  function gooseneck(parent, x, y, z, ry, o) {
    o = o || {};
    const g = new THREE.Group(); g.position.set(x, y, z); g.rotation.y = ry || 0;
    const blk = M.black(), h = o.h || 0.34;
    if (o.base !== false) {
      lathe([[0, 0], [0.045, 0], [0.047, 0.006], [0.042, 0.018], [0.03, 0.024], [0.012, 0.026], [0, 0.026]], blk, 32, g);
      cyl(0.008, 0.008, 0.004, mat('micbtn', { color: 0x2a2a2c, roughness: 0.4 }), 0.0, 0.024, 0.026, 16, g).rotation.x = 0;
      const led = cyl(0.004, 0.004, 0.003, mat('redled', { color: 0x220000, emissive: 0xff2a1a, emissiveIntensity: 2.2 }), 0.02, 0.022, 0.022, 10, g);
      led.rotation.x = -0.4;
    }
    const pts = [[0, 0.02, 0], [0, h * 0.45, 0.004], [0, h * 0.8, -0.02], [0, h * 0.95, -0.07], [0, h, -0.13]];
    const neck = tube(pts, 0.0048, mat('gooseneck', { color: 0x1e1e20, roughness: 0.35, metalness: 0.5 }), 48, 10, g);
    neck.name = 'neck';
    // head along the last tangent
    const head = new THREE.Group(); head.position.set(0, h, -0.13);
    const dir = new THREE.Vector3(0, h - h * 0.95, -0.13 + 0.07).normalize();
    head.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
    cyl(0.0085, 0.0075, 0.07, mat('michead', { color: 0x2b2c2e, metalness: 0.6, roughness: 0.35 }), 0, -0.02, 0, 20, head);
    const ring = new THREE.Mesh(new THREE.TorusGeometry(0.0088, 0.0018, 8, 24), mat('micring', { color: 0x300000, emissive: 0xff2616, emissiveIntensity: 1.6 }));
    ring.rotation.x = Math.PI / 2; ring.position.y = 0.047; head.add(ring);
    const foam = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 14), mat('micfoam', { color: 0x1a1a1b, roughness: 1 }));
    foam.scale.set(0.016, 0.03, 0.016); foam.position.y = 0.072; head.add(foam);
    g.add(head);
    parent.add(g);
    return g;
  }

  /* The chair: task (fabric), mesh, or executive (leather, high back). Front faces +z. */
  function makeChair(o, r) {
    const g = new THREE.Group();
    const style = o.style || 'task';
    const exec = style === 'exec';
    const cover = exec ? M.leather(o.color != null ? o.color : 0x2a1f19) : M.fabric(o.color != null ? o.color : 0x2d3440);
    const shell = M.plastic(0x19191b);
    const baseMat = exec ? M.alu(0xc7c9cc) : M.plastic(0x1c1c1e);
    // five star base
    for (let k = 0; k < 5; k++) {
      const piv = new THREE.Group(); piv.rotation.y = k * TAU / 5 + TAU / 20;
      const leg = TXT.roundedBox(0.29, 0.034, 0.048, 0.012, baseMat, { segments: 2 });
      deform(leg.geometry, (v) => { const t = (v.x + 0.145) / 0.29; v.z *= 1 - 0.35 * t; v.y *= 1 - 0.3 * t; v.y -= 0.03 * t; });
      leg.position.set(0.165, 0.098, 0); piv.add(leg);
      rbox(0.036, 0.03, 0.03, 0.008, M.plastic(0x1c1c1e), 0.305, 0.045, 0, piv);
      for (const s of [-1, 1]) {
        const wh = cyl(0.025, 0.025, 0.012, M.rubber(), 0.315, 0, s * 0.013, 20, piv);
        wh.rotation.x = Math.PI / 2; wh.position.y = 0.025;
      }
      g.add(piv);
    }
    lathe([[0, 0.07], [0.052, 0.07], [0.056, 0.09], [0.05, 0.125], [0.034, 0.13], [0, 0.13]], baseMat, 32, g);
    // gas lift: telescoping shroud, chrome piston
    lathe([[0, 0.13], [0.034, 0.13], [0.034, 0.2], [0.031, 0.205], [0.031, 0.27], [0.028, 0.275], [0.028, 0.32], [0, 0.32]], M.plastic(0x202022), 32, g);
    cyl(0.014, 0.014, 0.08, M.chrome(), 0, 0.32, 0, 20, g);
    // mechanism, knob, lever
    rbox(0.2, 0.045, 0.22, 0.01, M.plastic(0x222224), 0, 0.37, 0, g);
    const knob = cyl(0.028, 0.028, 0.04, M.plastic(0x222224), 0, 0.375, 0.13, 24, g); knob.rotation.x = Math.PI / 2; knob.position.y = 0.39;
    const lever = K.bar([0.1, 0.39, 0.05], [0.2, 0.385, 0.08], 0.005, M.plastic(0x222224), 8, g);
    rbox(0.03, 0.018, 0.02, 0.006, M.plastic(0x222224), 0.205, 0.376, 0.082, g);
    void lever;
    // seat shell and cushion (waterfall front, slight dish)
    rbox(0.48, 0.022, 0.45, 0.01, shell, 0, 0.408, 0.01, g);
    const sw = exec ? 0.54 : 0.5, sd = exec ? 0.5 : 0.48;
    const seat = TXT.roundedBox(sw, 0.085, sd, 0.036, cover, { segments: 4 });
    deform(seat.geometry, (v) => {
      if (v.z > 0.08) v.y -= (v.z - 0.08) * (v.z - 0.08) * 1.3;
      if (v.y > 0) v.y -= 0.014 * Math.max(0, 1 - (v.x / (sw / 2)) ** 2) * Math.max(0, 1 - (v.z / (sd / 2)) ** 2);
    });
    if (cover.map) K.uvBox(seat.geometry, 0.3);
    seat.position.set(0, 0.43 + 0.0425, 0.02); g.add(seat);
    // backrest
    const backY = 0.53, tilt = -0.12;
    const back = new THREE.Group(); back.position.set(0, backY, -0.25); back.rotation.x = tilt; g.add(back);
    if (style === 'mesh') {
      const bw = 0.48, bh = 0.6;
      const bend = (v) => { v.z += 0.55 * v.x * v.x + 0.028 * Math.exp(-(((v.y - 0.17) / 0.1) ** 2)); };
      const outline = [];
      for (let i = 0; i <= 40; i++) {
        const a = i / 40 * TAU, rx = bw / 2, ry = bh / 2;
        const cx = Math.cos(a), cy = Math.sin(a);
        const px = Math.sign(cx) * Math.pow(Math.abs(cx), 0.45) * rx, py = Math.sign(cy) * Math.pow(Math.abs(cy), 0.45) * ry + bh / 2;
        const v = new THREE.Vector3(px, py, 0); bend(v); outline.push([v.x, v.y, v.z]);
      }
      tube(outline, 0.014, M.plastic(0x19191b), 120, 10, back);
      const pg = new THREE.PlaneGeometry(bw - 0.02, bh - 0.02, 16, 16); pg.translate(0, bh / 2, 0);
      const mt = ltex('chairmesh', paintMesh, {}, [128, 128], true); const mt2 = mt; mt2.repeat.set(24, 30);
      deform(pg, bend);
      const panel = new THREE.Mesh(pg, mat('meshback', { color: 0x1d1e20, roughness: 0.7, alphaMap: mt2, alphaTest: 0.5, side: THREE.DoubleSide }));
      back.add(panel);
      // lumbar pad
      const lum = TXT.roundedBox(0.34, 0.07, 0.025, 0.012, M.plastic(0x222224), { segments: 2 });
      deform(lum.geometry, (v) => { v.z += 0.55 * v.x * v.x; }); lum.position.set(0, 0.17, 0.035); back.add(lum);
    } else {
      const pieces = exec ? [[0.52, 0.8, 0.1, 0.0]] : [[0.46, 0.5, 0.075, 0.0]];
      pieces.forEach(([w, h, d, y0]) => {
        const pc = TXT.roundedBox(w, h, d, exec ? 0.05 : 0.032, cover, { segments: exec ? 6 : 4 });
        deform(pc.geometry, (v) => {
          v.z += 0.5 * v.x * v.x;
          v.z += 0.02 * Math.exp(-(((v.y + (exec ? 0.18 : 0.08)) / 0.1) ** 2));
          if (exec) {
            // narrower shoulders toward the top, channel stitching as soft grooves
            const t = (v.y + h / 2) / h; v.x *= 1 - 0.14 * t * t;
            if (v.z > 0.01) { const ph = (v.y + h / 2) / (h / 5); const gv = Math.abs(ph - Math.round(ph)); v.z -= 0.012 * Math.exp(-((gv / 0.08) ** 2)) * (Math.abs(v.x) < w / 2 - 0.05 ? 1 : 0); }
          }
        });
        if (cover.map) K.uvBox(pc.geometry, 0.3);
        pc.position.set(0, y0 + h / 2, 0); back.add(pc);
      });
      const shellBack = TXT.roundedBox(exec ? 0.5 : 0.44, exec ? 0.78 : 0.48, 0.03, 0.012, shell, { segments: 2 });
      deform(shellBack.geometry, (v) => { v.z += 0.5 * v.x * v.x; });
      shellBack.position.set(0, (exec ? 0.39 : 0.25), -0.05); back.add(shellBack);
    }
    // spine from the mechanism to the back
    rbox(0.07, 0.024, 0.2, 0.008, M.plastic(0x1c1c1e), 0, 0.382, -0.17, g);
    const spine = rbox(0.07, 0.3, 0.024, 0.008, M.plastic(0x1c1c1e), 0, 0.37, -0.29, g); spine.rotation.x = tilt;
    // arms
    if (o.arms !== false) {
      for (const s of [-1, 1]) {
        const ax = s * (sw / 2 + 0.035);
        rbox(0.06, 0.02, 0.06, 0.006, baseMat, s * (sw / 2 - 0.0), 0.388, -0.02, g);
        rbox(0.028, 0.23, 0.05, 0.01, baseMat, ax, 0.39, -0.02, g);
        rbox(0.075, 0.032, 0.27, 0.014, exec ? M.leather(0x1e1814) : M.plastic(0x202022), ax, 0.62, 0.0, g, 3);
      }
    }
    return g;
  }

  /* ================================================================================== DAIS */
  K.define('hearing_dais', {
    size: [10.5, 1.6, 4],
    options: { seats: 5, curve: 7, wood: 0x6b4426, carpet: 0x3b3f47, chairs: true, mics: true, plates: true, steps: true },
    note: 'Commissioners court or council dais: a raised millwork bench, concave toward the audience (curve = front radius in metres, 0 = straight), raised panel modesty front with pilasters, a transaction ledge with blank brass nameplates, gooseneck microphones and high back leather chairs on a carpeted riser. seats 3 to 9.',
    make(o, r) {
      const n = Math.max(3, Math.min(9, Math.round(o.seats || 5)));
      const Rf = o.curve == null ? 7 : o.curve, curved = Rf > 0.5;
      const pitch = 1.5, half = n * pitch / 2;
      const wood = M.veneer(o.wood != null ? o.wood : 0x6b4426), darkWood = M.veneer(new THREE.Color(o.wood != null ? o.wood : 0x6b4426).multiplyScalar(0.55).getHex());
      const carpet = mat('carpet' + (o.carpet || 0x3b3f47), { color: o.carpet != null ? o.carpet : 0x3b3f47, roughness: 1, map: ltex('weave', paintWeave, {}, [256, 256]) });
      const g = new THREE.Group();
      const H = 1.1, riser = 0.3, ledgeD = 0.36;
      // arc position s along the front, depth rr behind it
      const P = (s, rr) => {
        if (!curved) return { x: s, z: -rr, rot: 0 };
        const a = s / Rf; return { x: (Rf + rr) * Math.sin(a), z: Rf - (Rf + rr) * Math.cos(a), rot: -a };
      };
      // an extruded band between depths r0 and r1, arc range s0..s1, from y0 to y0 + h
      function band(s0, s1, r0, r1, y0, h, material) {
        const pts = [], N = curved ? 64 : 1;
        for (let i = 0; i <= N; i++) { const p = P(s0 + (s1 - s0) * i / N, r0); pts.push(new THREE.Vector2(p.x, -p.z)); }
        for (let i = N; i >= 0; i--) { const p = P(s0 + (s1 - s0) * i / N, r1); pts.push(new THREE.Vector2(p.x, -p.z)); }
        const geo = new THREE.ExtrudeGeometry(new THREE.Shape(pts), { depth: h, bevelEnabled: true, bevelThickness: 0.006, bevelSize: 0.006, bevelSegments: 2, curveSegments: 4 });
        geo.rotateX(-Math.PI / 2); geo.translate(0, y0, 0);
        geo.computeVertexNormals();
        K.uvBox(geo, 1.2);
        const m = new THREE.Mesh(geo, material); g.add(m); return m;
      }
      // riser platform and its carpet
      band(-half - 0.12, half + 0.12, 0.2, 2.9, 0, riser - 0.012, darkWood);
      band(-half - 0.1, half + 0.1, 0.22, 2.88, riser - 0.012, 0.01, carpet);
      // the front: one faceted millwork section per seat
      for (let i = 0; i < n; i++) {
        const sC = -half + pitch * (i + 0.5);
        const A = P(sC - pitch / 2, 0), B = P(sC + pitch / 2, 0);
        const chord = Math.hypot(B.x - A.x, B.z - A.z);
        const f = new THREE.Group(); f.position.set((A.x + B.x) / 2, 0, (A.z + B.z) / 2); f.rotation.y = P(sC, 0).rot; g.add(f);
        box(chord + 0.01, 0.09, 0.3, mat('toe', { color: 0x151312, roughness: 0.8 }), 0, 0, -0.2, f);           // recessed toe kick
        box(chord + 0.01, H - 0.09, 0.05, wood, 0, 0.09, -0.025, f);                                             // carcass face
        box(chord, 0.035, 0.05, wood, 0, 0.09, 0.012, f);                                                        // base rail
        rbox(chord, 0.045, 0.03, 0.01, wood, 0, H - 0.1, 0.012, f);                                              // top rail
        const pw = chord / 2 - 0.16;
        for (const sx of [-1, 1]) {
          const cx = sx * chord / 4;
          [[0.2, 0.17], [0.44, 0.52]].forEach(([y0, ph]) => {
            const panel = rbox(pw, ph, 0.024, 0.01, wood, cx, y0, 0.004, f);
            deform(panel.geometry, (v) => { if (v.z > 0) { const ex = Math.min(1, (pw / 2 - Math.abs(v.x)) / 0.05), ey = Math.min(1, (ph / 2 - Math.abs(v.y)) / 0.05); v.z -= 0.009 * (1 - Math.min(ex, ey)); } });
            K.uvBox(panel.geometry, 1.2);
            // bolection molding
            const mw = 0.022;
            box(pw + 2 * mw, mw, 0.02, wood, cx, y0 - mw, 0.01, f); box(pw + 2 * mw, mw, 0.02, wood, cx, y0 + ph, 0.01, f);
            box(mw, ph, 0.02, wood, cx - pw / 2 - mw / 2, y0, 0.01, f); box(mw, ph, 0.02, wood, cx + pw / 2 + mw / 2, y0, 0.01, f);
          });
        }
        // pilaster at this facet's left joint (and the right end)
        const pil = (x) => { rbox(0.1, H - 0.1, 0.05, 0.012, wood, x, 0.09, 0.02, f, 2); rbox(0.13, 0.05, 0.07, 0.01, wood, x, 0.09, 0.02, f); };
        pil(-chord / 2); if (i === n - 1) pil(chord / 2);
        // end returns close the carcass
        if (i === 0 || i === n - 1) box(0.05, H, ledgeD, wood, (i === 0 ? -1 : 1) * (chord / 2 + 0.02), 0, -ledgeD / 2, f);
        // knee space side panel behind (under the work surface)
        box(0.03, 1.0 - riser, 0.55, darkWood, chord / 2 - 0.02, riser, -0.7, f);
      }
      // transaction ledge and the work surface behind it (continuous, follow the curve)
      band(-half - 0.04, half + 0.04, -0.07, ledgeD - 0.02, H, 0.045, wood);
      band(-half, half, ledgeD - 0.04, 0.95, 0.99, 0.035, wood);
      if (o.steps !== false) {
        for (let k = 0; k < 2; k++) band(-half - 0.12 - 0.3 * (k + 1), -half - 0.12 - 0.3 * k + 0.001, 0.6, 1.8, 0, riser * (2 - k) / 3, darkWood);
      }
      // per seat furniture
      for (let i = 0; i < n; i++) {
        const sC = -half + pitch * (i + 0.5);
        if (o.plates !== false) {
          const p = P(sC + (r() - 0.5) * 0.1, 0.05);
          const plate = new THREE.Group(); plate.position.set(p.x, H + 0.045, p.z); plate.rotation.y = p.rot; g.add(plate);
          const prof = [[-0.035, 0], [0.035, 0], [0.0, 0.075]];
          const blk = new THREE.Mesh(new THREE.ExtrudeGeometry(new THREE.Shape(prof.map((q) => new THREE.Vector2(q[0], q[1]))), { depth: 0.3, bevelEnabled: true, bevelThickness: 0.003, bevelSize: 0.003, bevelSegments: 2 }), darkWood);
          blk.geometry.rotateY(Math.PI / 2); blk.geometry.translate(-0.15, 0, 0); K.uvBox(blk.geometry, 1.2); plate.add(blk);
          const face = TXT.roundedBox(0.27, 0.062, 0.003, 0.0012, mat('plateBrass', { color: 0xc8a45e, metalness: 1, roughness: 0.22 }), { segments: 1 });
          face.position.set(0, 0.036, 0.018); face.rotation.x = -Math.atan2(0.035, 0.075); plate.add(face);
        }
        const pm = P(sC + 0.25, 0.46);
        if (o.mics !== false) gooseneck(g, pm.x, 1.025, pm.z, pm.rot, { h: 0.36 });
        // paper and a water glass on the work surface
        const pp = P(sC - 0.2, 0.62);
        const paper = box(0.216, 0.004, 0.279, mat('paperTop', { color: 0xffffff, roughness: 0.9, map: ltex('page', paintPage, {}, [256, 330]) }), pp.x, 1.025, pp.z, g);
        paper.rotation.y = pp.rot + (r() - 0.5) * 0.3;
        if (r() < 0.7) {
          const gp = P(sC + 0.5, 0.55);
          lathe([[0, 0], [0.032, 0], [0.036, 0.12], [0.034, 0.12], [0.03, 0.004], [0, 0.004]], mat('glassCup', { color: 0xdfe8ea, transparent: true, opacity: 0.35, roughness: 0.05, metalness: 0.1 }), 32, g).position.set(gp.x, 1.025, gp.z);
        }
        if (o.chairs !== false) {
          const pc = P(sC + (r() - 0.5) * 0.2, 1.1 + r() * 0.15);
          const ch = makeChair({ style: 'exec', color: 0x2a1e17 }, r);
          ch.position.set(pc.x, riser, pc.z); ch.rotation.y = pc.rot + (r() - 0.5) * 0.25; g.add(ch);
        }
      }
      return centre(g);
    },
  });

  /* ================================================================================ PODIUM */
  K.define('podium', {
    size: [0.66, 1.52, 0.56],
    options: { wood: 0x6b4426, seal: true, mic: true },
    note: 'Speaker lectern: a raked veneer body wider at the top, sloped reading desk with a book stop, raised front panel with an optional blank round seal, plinth, and a gooseneck microphone. The speaker stands at -z.',
    make(o, r) {
      const g = new THREE.Group();
      const wood = M.veneer(o.wood != null ? o.wood : 0x6b4426);
      const W = 0.6;
      // side profile in (z, y): audience face raked forward, reading desk falling toward the speaker at -z
      const prof = [[-0.2, 0.08], [0.2, 0.08], [0.26, 1.2], [0.2, 1.205], [-0.24, 1.085], [-0.245, 1.07], [-0.2, 0.2]];
      const geo = new THREE.ExtrudeGeometry(new THREE.Shape(prof.map((p) => new THREE.Vector2(p[0], p[1]))),
        { depth: W, bevelEnabled: true, bevelThickness: 0.008, bevelSize: 0.008, bevelSegments: 2 });
      geo.rotateY(-Math.PI / 2); geo.translate(W / 2, 0, 0); geo.computeVertexNormals(); K.uvBox(geo, 1.2);
      g.add(new THREE.Mesh(geo, wood));
      const rake = Math.atan2(0.06, 1.12);
      const front = new THREE.Group(); front.position.set(0, 0.08, 0.2 + 0.006); front.rotation.x = rake; g.add(front);
      const pw = W - 0.14, ph = 0.74;
      rbox(pw, ph, 0.02, 0.008, wood, 0, 0.14, 0.004, front);
      const mw = 0.022;
      box(pw + 2 * mw, mw, 0.018, wood, 0, 0.14 - mw, 0.006, front); box(pw + 2 * mw, mw, 0.018, wood, 0, 0.14 + ph, 0.006, front);
      box(mw, ph, 0.018, wood, -pw / 2 - mw / 2, 0.14, 0.006, front); box(mw, ph, 0.018, wood, pw / 2 + mw / 2, 0.14, 0.006, front);
      if (o.seal !== false) { const s = sealDisc({ d: 0.3, finish: 'gold' }); s.position.set(0, 0.55, 0.016); front.add(s); }
      // crown moulding under the desk edge and the plinth
      rbox(W + 0.03, 0.035, 0.05, 0.01, wood, 0, 1.13, 0.245, g);
      rbox(0.7, 0.08, 0.52, 0.01, M.veneer(new THREE.Color(o.wood != null ? o.wood : 0x6b4426).multiplyScalar(0.5).getHex()), 0, 0, 0.0, g);
      const deskAng = Math.atan2(0.12, 0.5);
      rbox(W + 0.02, 0.03, 0.025, 0.008, wood, 0, 1.075, -0.245, g);
      const note = box(0.216, 0.002, 0.279, mat('paperTop', { color: 0xffffff, roughness: 0.9, map: ltex('page', paintPage, {}, [256, 330]) }), 0, 0, 0, null);
      note.position.set(0.02, 1.142, -0.02); note.rotation.x = -deskAng; note.rotation.y = 0.04; g.add(note);
      if (o.mic !== false) {
        const mg = gooseneck(g, 0, 0, 0, 0, { h: 0.34, base: false });
        mg.position.set(0.0, 1.2, 0.215); mg.rotation.x = -0.2;
        rbox(0.05, 0.02, 0.04, 0.006, M.black(), 0, 1.19, 0.215, g);
      }
      return g;
    },
  });

  // a round plaque: rope rim, raised ring, blank field; faces +z, centre at origin
  function sealDisc(o) {
    const d = o.d || 0.9, R = d / 2, g = new THREE.Group();
    const metal = o.finish === 'wood' ? M.veneer(0x5c3a20) : o.finish === 'gold'
      ? mat('sealGold', { color: 0xd4af62, metalness: 1, roughness: 0.3 }) : M.bronze();
    const field = o.finish === 'wood' ? M.veneer(0x70482a) : o.finish === 'gold'
      ? mat('sealGoldField', { color: 0xc7a257, metalness: 1, roughness: 0.55 }) : mat('bronzeField', { color: 0x7a5732, metalness: 1, roughness: 0.62 });
    const t = Math.max(0.012, d * 0.035);
    // body: lathe profile in (radius, height along +z)
    const prof = [[0, t * 0.55], [R * 0.62, t * 0.55], [R * 0.64, t * 0.8], [R * 0.66, t * 0.8], [R * 0.68, t * 0.55], [R * 0.84, t * 0.55],
                  [R * 0.86, t * 0.95], [R * 0.9, t * 0.95], [R * 0.92, t * 0.6], [R * 0.99, t * 0.5], [R, t * 0.2], [R, 0], [0, 0]];
    const body = lathe(prof.map((p) => [p[0], p[1]]), metal, 96, null);
    body.rotation.x = Math.PI / 2; g.add(body);   // lathe y -> +z
    const inner = new THREE.Mesh(new THREE.CircleGeometry(R * 0.62, 64), field); inner.position.z = t * 0.551; g.add(inner);
    const band = new THREE.Mesh(new THREE.RingGeometry(R * 0.68, R * 0.84, 96), field); band.position.z = t * 0.551; g.add(band);
    // rope moulding on the rim
    const rope = new THREE.TorusGeometry(R * 0.955, t * 0.28, 10, 360);
    deform(rope, (v) => { const a = Math.atan2(v.y, v.x); const rr = Math.hypot(v.x, v.y); const tw = Math.sin(a * 90 + Math.atan2(v.z, rr - R * 0.955) * 1) * t * 0.06;
      const k = (rr + tw) / rr; v.x *= k; v.y *= k; });
    const ropeM = new THREE.Mesh(rope, metal); ropeM.position.z = t * 0.62; g.add(ropeM);
    // a ring of small stars in the legend band
    if (o.stars !== false) {
      const star = []; for (let i = 0; i < 10; i++) { const a = i / 10 * TAU + Math.PI / 2, rr = i % 2 ? 0.4 : 1; star.push(new THREE.Vector2(Math.cos(a) * rr, Math.sin(a) * rr)); }
      const sg = new THREE.ExtrudeGeometry(new THREE.Shape(star), { depth: 0.25, bevelEnabled: false });
      const sm = R * 0.035, list = [];
      const ns = 24;
      for (let i = 0; i < ns; i++) { const a = i / ns * TAU; const m4 = new THREE.Matrix4().compose(new THREE.Vector3(Math.cos(a) * R * 0.76, Math.sin(a) * R * 0.76, t * 0.55),
        new THREE.Quaternion().setFromEuler(new THREE.Euler(0, 0, a - Math.PI / 2)), new THREE.Vector3(sm, sm, sm * 0.5)); list.push(m4); }
      const im = new THREE.InstancedMesh(sg, metal, ns); list.forEach((m4, i) => im.setMatrixAt(i, m4)); g.add(im);
    }
    return g;
  }

  K.define('seal_plaque', {
    size: [0.9, 0.9, 0.04],
    options: { d: 0.9, finish: 'bronze', stars: true, backer: false },
    note: 'A round seal plaque for a wall: rope moulded rim, raised rings, a ring of small stars in the legend band and a BLANK centre field. finish bronze | gold | wood. Faces +z, lowest point at y = 0; raise it to hang it (position.y = centre height - d / 2). backer adds a square walnut board behind.',
    make(o) {
      const d = o.d || 0.9, g = new THREE.Group();
      const s = sealDisc({ d, finish: o.finish || 'bronze', stars: o.stars });
      s.position.set(0, d / 2 + (o.backer ? 0.08 : 0), o.backer ? 0.025 : 0); g.add(s);
      if (o.backer) rbox(d + 0.16, d + 0.16, 0.025, 0.008, M.veneer(0x4a2e1a), 0, 0, 0.0, g);
      return g;
    },
  });

  /* ====================================================================== PUBLIC SEATING */
  function stackChair(color, frameMat) {
    const g = new THREE.Group();
    const fab = M.fabric(color);
    const legs = [[-0.21, 0.2], [0.21, 0.2], [-0.2, -0.2], [0.2, -0.2]];
    legs.forEach(([x, z]) => { K.bar([x, 0.012, z * 1.12], [x * 0.96, 0.44, z], 0.011, frameMat, 7, g); cyl(0.013, 0.013, 0.012, M.rubber(), x, 0, z * 1.12, 10, g); });
    K.bar([-0.2, 0.44, 0.2], [0.2, 0.44, 0.2], 0.011, frameMat, 7, g); K.bar([-0.2, 0.44, -0.2], [0.2, 0.44, -0.2], 0.011, frameMat, 7, g);
    K.bar([-0.2, 0.44, 0.2], [-0.2, 0.44, -0.2], 0.011, frameMat, 7, g); K.bar([0.2, 0.44, 0.2], [0.2, 0.44, -0.2], 0.011, frameMat, 7, g);
    // back uprights, curved back
    for (const s of [-1, 1]) K.bar([s * 0.2, 0.44, -0.2], [s * 0.19, 0.88, -0.27], 0.011, frameMat, 7, g);
    const seat = TXT.roundedBox(0.46, 0.06, 0.45, 0.025, fab, { segments: 3 });
    deform(seat.geometry, (v) => { if (v.z > 0.1) v.y -= (v.z - 0.1) ** 2 * 1.2; }); K.uvBox(seat.geometry, 0.3);
    seat.position.set(0, 0.48, 0.005); g.add(seat);
    const back = TXT.roundedBox(0.44, 0.3, 0.05, 0.022, fab, { segments: 3 });
    deform(back.geometry, (v) => { v.z += 0.45 * v.x * v.x; }); K.uvBox(back.geometry, 0.3);
    back.position.set(0, 0.72, -0.25); back.rotation.x = -0.14; g.add(back);
    return g;
  }
  function pew(len, wood) {
    const g = new THREE.Group();
    for (const s of [-1, 1]) {
      const prof = [[-0.3, 0], [0.26, 0], [0.26, 0.44], [0.2, 0.46], [-0.18, 0.46], [-0.26, 0.92], [-0.3, 0.95], [-0.33, 0.92]];
      const e = new THREE.Mesh(new THREE.ExtrudeGeometry(new THREE.Shape(prof.map((p) => new THREE.Vector2(p[0], p[1]))), { depth: 0.05, bevelEnabled: true, bevelThickness: 0.006, bevelSize: 0.006, bevelSegments: 2 }), wood);
      e.geometry.rotateY(-Math.PI / 2); e.geometry.computeVertexNormals(); K.uvBox(e.geometry, 1.2);
      e.position.set(s * len / 2 + (s > 0 ? 0.05 : 0), 0, 0); g.add(e);
    }
    rbox(len, 0.04, 0.44, 0.012, wood, 0, 0.42, 0.02, g);
    const back = rbox(len, 0.42, 0.03, 0.01, wood, 0, 0.48, -0.24, g); back.rotation.x = -0.18;
    rbox(len, 0.05, 0.08, 0.012, wood, 0, 0.88, -0.32, g);
    box(len, 0.12, 0.02, wood, 0, 0.28, 0.2, g);
    return g;
  }
  K.define('public_seating', {
    size: [5.6, 0.95, 2.9],
    options: { rows: 3, perRow: 8, aisle: true, type: 'chairs', color: 0x3a4658, frame: 'chrome', wood: 0x6b4426 },
    note: 'Rows of public seating facing +z (toward the dais): padded stacking chairs on chrome or black tube frames, or wooden pews (type: pews). A centre aisle splits each row. Instanced; a few chairs sit slightly askew.',
    make(o, r) {
      const rows = Math.max(1, o.rows || 3), per = Math.max(1, o.perRow || 8), aisle = o.aisle !== false;
      const g = new THREE.Group(), pitch = 0.56, rowP = 0.95;
      // with an aisle, the chairs split into two blocks either side of it, the extra one of an odd row on the right
      const xs = [];
      if (aisle) {
        const nl = Math.floor(per / 2), nr = per - nl;
        for (let i = 0; i < nl; i++) xs.push(-0.45 - (nl - 1 - i) * pitch - pitch / 2);
        for (let i = 0; i < nr; i++) xs.push(0.45 + i * pitch + pitch / 2);
      } else for (let i = 0; i < per; i++) xs.push((i - (per - 1) / 2) * pitch);
      if (o.type === 'pews') {
        const wood = M.veneer(o.wood != null ? o.wood : 0x6b4426);
        const lenSide = (per / (aisle ? 2 : 1)) * pitch;
        for (let j = 0; j < rows; j++) {
          const z = (j - (rows - 1) / 2) * -rowP;
          if (aisle) for (const s of [-1, 1]) { const p = pew(lenSide, wood); p.position.set(s * (lenSide / 2 + 0.45), 0, z); g.add(p); }
          else { const p = pew(lenSide, wood); p.position.set(0, 0, z); g.add(p); }
        }
        return g;
      }
      const frame = o.frame === 'black' ? M.plastic(0x1c1c1e) : M.chrome();
      const proto = stackChair(o.color != null ? o.color : 0x3a4658, frame);
      const parts = bake(proto), list = [];
      for (let j = 0; j < rows; j++) for (let i = 0; i < per; i++) {
        const z = (j - (rows - 1) / 2) * -rowP;
        const askew = r() < 0.2;
        list.push(mat4(xs[i] + (r() - 0.5) * 0.03 + (askew ? (r() - 0.5) * 0.08 : 0), 0, z + (r() - 0.5) * 0.03 + (askew ? r() * 0.1 : 0),
          (r() - 0.5) * 0.04 + (askew ? (r() - 0.5) * 0.3 : 0)));
      }
      instanceBaked(parts, list, g);
      return g;
    },
  });

  /* ===================================================================== OFFICE FURNITURE */
  K.define('office_chair', {
    size: [0.66, 1.0, 0.66],
    options: { style: 'task', color: 0x2d3440, arms: true },
    note: 'Swivel office chair facing +z: five star base on twin wheel casters, telescoping gas lift, tilt mechanism with knob and lever, waterfall seat, curved backrest with lumbar, T arms. style task (fabric) | mesh | exec (high back leather on polished aluminium).',
    make(o, r) { return makeChair(o, r); },
  });

  function pull(parent, x, y, z, w, material) {
    K.bar([x - w / 2, y, z + 0.028], [x + w / 2, y, z + 0.028], 0.005, material, 12, parent).rotation.z = Math.PI / 2;
    for (const s of [-1, 1]) K.bar([x + s * w / 2, y, z], [x + s * w / 2, y, z + 0.03], 0.0045, material, 10, parent);
  }
  K.define('desk', {
    size: [1.52, 0.76, 0.76],
    options: { w: 1.52, d: 0.76, h: 0.76, pedestal: 'right', wood: 0x5e3b22, pulls: 'brushed' },
    note: 'Office desk (60 x 30 in): bevelled veneer top, drawer pedestal (left | right | both | none) with a pencil drawer and a file drawer, bar pulls, recessed toe kick, a panel leg and a modesty panel, and a cable grommet. Drawers face +z, so the sitter is at +z facing -z.',
    make(o, r) {
      const W = o.w || 1.52, D = o.d || 0.76, Hh = o.h || 0.76;
      const g = new THREE.Group();
      const wood = M.veneer(o.wood != null ? o.wood : 0x5e3b22), metal = o.pulls === 'black' ? M.black() : M.alu(0xa9acaf);
      rbox(W, 0.032, D, 0.008, wood, 0, Hh - 0.032, 0, g, 3);
      const side = o.pedestal || 'right';
      const peds = side === 'both' ? [-1, 1] : side === 'left' ? [-1] : side === 'right' ? [1] : [];
      const pw = 0.42, top = Hh - 0.032;
      for (const s of [-1, 1]) {
        const x = s * (W / 2 - (peds.includes(s) ? pw / 2 : 0.018) - 0.01);
        if (peds.includes(s)) {
          box(pw, top - 0.07, D - 0.04, wood, x, 0.07, 0, g);
          box(pw - 0.04, 0.07, D - 0.1, mat('toe', { color: 0x151312, roughness: 0.8 }), x, 0, 0, g);
          // drawers face the sitter at -z
          const fz = -(D - 0.04) / 2;
          const hs = [0.16, 0.13, top - 0.07 - 0.3 - 0.012];
          let y = top - 0.006;
          const ajar = Math.floor(r() * 4);
          hs.forEach((hh, k) => {
            y -= hh; const out = ajar === k ? 0.04 : 0;
            rbox(pw - 0.012, hh - 0.006, 0.02, 0.004, wood, x, y + 0.003, fz - 0.01 - out, g);
            pull(g, x, y + hh - Math.min(0.05, hh / 2), fz - 0.02 - out, 0.13, metal);
          });
          y -= 0; // done
        } else {
          box(0.036, top, D - 0.04, wood, x, 0, 0, g);
        }
      }
      // modesty panel toward +z, and centre pencil drawer
      box(W - 0.06, top - 0.3, 0.02, wood, 0, 0.3, D / 2 - 0.06, g);
      const cw = W - (peds.length === 2 ? 2 * pw : peds.length ? pw + 0.05 : 0.08) - 0.04;
      const cx = peds.length === 1 ? -peds[0] * (pw - 0.05) / 2 : 0;
      rbox(cw, 0.07, 0.02, 0.004, wood, cx, top - 0.078, -(D - 0.04) / 2 - 0.01, g);
      pull(g, cx, top - 0.043, -(D - 0.04) / 2 - 0.02, 0.2, metal);
      // grommet
      const gr = new THREE.Mesh(new THREE.TorusGeometry(0.03, 0.005, 8, 32), M.black()); gr.rotation.x = Math.PI / 2;
      gr.position.set(W * 0.3, Hh + 0.001, D / 2 - 0.1); g.add(gr);
      const hole = new THREE.Mesh(new THREE.CircleGeometry(0.03, 32), mat('holeDark', { color: 0x050505, roughness: 1 })); hole.rotation.x = -Math.PI / 2;
      hole.position.set(W * 0.3, Hh + 0.0008, D / 2 - 0.1); g.add(hole);
      g.rotation.y = Math.PI; const out = new THREE.Group(); out.add(g);
      return out;
    },
  });

  K.define('conference_table', {
    size: [4.8, 1.0, 2.8],
    options: { seats: 8, shape: 'boat', wood: 0x5e3b22, chairs: true, chairStyle: 'task', chairColor: 0x262b33 },
    note: 'Boardroom table (shape boat | rect) with a bevelled veneer top, two panel bases on plinths, a flush power and data box, and office chairs pulled up around it (seats 4 to 14, ends seated at 8 and up), each a little askew.',
    make(o, r) {
      const seats = Math.max(4, Math.min(14, o.seats || 8));
      const ends = seats >= 8 ? 2 : 0, perSide = Math.ceil((seats - ends) / 2);
      const L = Math.max(2.2, perSide * 0.8 + 0.8), Wd = 1.2;
      const g = new THREE.Group();
      const wood = M.veneer(o.wood != null ? o.wood : 0x5e3b22), top = 0.74;
      const pts = [];
      if (o.shape === 'rect') {
        const rr = 0.08, hx = L / 2, hz = Wd / 2;
        const corners = [[hx - rr, hz - rr, 0], [-hx + rr, hz - rr, Math.PI / 2], [-hx + rr, -hz + rr, Math.PI], [hx - rr, -hz + rr, 1.5 * Math.PI]];
        corners.forEach(([cx, cz, a0]) => { for (let i = 0; i <= 8; i++) { const a = a0 + i / 8 * Math.PI / 2; pts.push(new THREE.Vector2(cx + Math.cos(a) * rr, cz + Math.sin(a) * rr)); } });
      } else {
        const N = 96;
        for (let i = 0; i < N; i++) {
          const a = i / N * TAU, c = Math.cos(a), s = Math.sin(a);
          // superellipse lengthwise, bulged in the middle (boat)
          const x = Math.sign(c) * Math.pow(Math.abs(c), 0.28) * L / 2;
          const w = Wd / 2 * (1 - 0.2 * (x / (L / 2)) ** 2);
          pts.push(new THREE.Vector2(x, Math.sign(s) * Math.pow(Math.abs(s), 0.9) * w));
        }
      }
      const geo = new THREE.ExtrudeGeometry(new THREE.Shape(pts), { depth: 0.035, bevelEnabled: true, bevelThickness: 0.008, bevelSize: 0.008, bevelSegments: 3, curveSegments: 6 });
      geo.rotateX(-Math.PI / 2); geo.translate(0, top - 0.043, 0); geo.computeVertexNormals(); K.uvBox(geo, 1.2);
      g.add(new THREE.Mesh(geo, wood));
      // apron under the top edge (dark)
      for (const s of [-1, 1]) {
        const bx = s * L * 0.28;
        rbox(0.1, top - 0.1, 0.72, 0.01, wood, bx, 0.06, 0, g);
        rbox(0.2, 0.06, 0.82, 0.01, mat('toe', { color: 0x151312, roughness: 0.8 }), bx, 0, 0, g);
        box(0.3, 0.04, 0.8, wood, bx, top - 0.083, 0, g);
      }
      box(L * 0.56, 0.12, 0.03, wood, 0, top - 0.2, 0, g);
      // power and data box
      rbox(0.34, 0.006, 0.13, 0.003, M.alu(0x8e9296), 0, top, 0, g);
      box(0.3, 0.001, 0.004, M.black(), 0, top + 0.006, 0.0, g);
      if (o.chairs !== false) {
        const style = o.chairStyle || 'task', col = o.chairColor != null ? o.chairColor : 0x262b33;
        const place = (x, z, ry) => { const c = makeChair({ style, color: col }, r); const out = 0.05 + r() * 0.2;
          c.position.set(x + Math.sin(ry) * -out, 0, z + Math.cos(ry) * -out); c.rotation.y = ry + (r() - 0.5) * 0.35; g.add(c); };
        for (let i = 0; i < perSide; i++) {
          const x = (i - (perSide - 1) / 2) * 0.8;
          const hz = o.shape === 'rect' ? Wd / 2 : Wd / 2 * (1 - 0.2 * (x / (L / 2)) ** 2);
          place(x, hz + 0.3, Math.PI);
          if (i < seats - ends - perSide) place(x, -hz - 0.3, 0);
        }
        if (ends) { place(L / 2 + 0.3, 0, -Math.PI / 2); place(-L / 2 - 0.3, 0, Math.PI / 2); }
      }
      return g;
    },
  });

  /* ============================================================================ DEVICES */
  function screenMat(kind, dark, seed) {
    const t = ltex('screen', paintScreen, { kind, dark, seed }, [1024, 640]);
    return mat('screen|' + kind + dark + seed, { color: 0x0a0a0a, roughness: 0.18, metalness: 0.1, emissive: 0xffffff, emissiveMap: t, emissiveIntensity: 0.95 });
  }
  K.define('laptop', {
    size: [0.31, 0.23, 0.26],
    options: { open: 110, finish: 'silver', screen: 'doc', dark: false },
    note: '14 in aluminium laptop at true size: unibody base, recessed keyboard with every key, glass trackpad, hinge, thin lid with a lit display (screen doc | sheet | chart | dash | off; no legible text) and a camera dot. open is the lid angle in degrees.',
    make(o, r) {
      const g = new THREE.Group();
      const shell = o.finish === 'space' ? M.alu(0x5a5d62) : M.alu(0xc4c7ca);
      const Wb = 0.312, Db = 0.221, Tb = 0.0125;
      rbox(Wb, Tb, Db, 0.004, shell, 0, 0, 0, g, 3);
      // keyboard well and keys
      box(0.272, 0.0008, 0.112, M.black(), 0, Tb - 0.0006, -0.035, g);
      const kg = TXT.roundedBox(1, 1, 1, 0.18, null, { segments: 1 });
      const keyMat = mat('keycap', { color: 0x18191b, roughness: 0.5 });
      const mats = [];
      const pitch = 0.0191, kw = 0.0158;
      const rowsDef = [[14, 0.5], [14, 1], [14, 1], [13, 1], [12, 1], [0, 1]];
      let zRow = -0.035 - 0.112 / 2 + 0.008;
      rowsDef.forEach(([count, hk], ri) => {
        const kh = kw * hk;
        const zc = zRow + kh / 2;
        if (ri === 5) {
          // bottom row: modifiers, space, arrows
          const widths = [1, 1, 1, 1.25, 5, 1.25, 1, 1, 1];
          let x = -0.272 / 2 + 0.004;
          widths.forEach((w) => { const ww = pitch * w - (pitch - kw); mats.push(new THREE.Matrix4().compose(new THREE.Vector3(x + ww / 2, Tb + 0.0006, zc), new THREE.Quaternion(), new THREE.Vector3(ww, 0.0016, kh))); x += pitch * w; });
        } else {
          const extra = (0.268 - count * pitch) / 2;
          for (let k = 0; k < count; k++) {
            let ww = kw, x = -0.268 / 2 + k * pitch + kw / 2;
            if (ri >= 2 && (k === 0 || k === count - 1)) { ww = kw + extra * 2; x += k === 0 ? 0 : extra * 2; }
            else if (ri >= 2) x += extra * 2;
            mats.push(new THREE.Matrix4().compose(new THREE.Vector3(x, Tb + 0.0006, zc), new THREE.Quaternion(), new THREE.Vector3(ww, 0.0016, kh)));
          }
        }
        zRow += kh + (pitch - kw);
      });
      const im = new THREE.InstancedMesh(kg, keyMat, mats.length); mats.forEach((m4, i) => im.setMatrixAt(i, m4)); g.add(im);
      // trackpad and front notch
      rbox(0.13, 0.0006, 0.08, 0.008, mat('trackpad', { color: 0xb7babd, metalness: 0.6, roughness: 0.25 }), 0, Tb - 0.0001, 0.058, g, 2).material = o.finish === 'space' ? mat('trackpadS', { color: 0x55585c, metalness: 0.6, roughness: 0.25 }) : mat('trackpad', { color: 0xb7babd, metalness: 0.6, roughness: 0.25 });
      // hinge barrel
      const hinge = cyl(0.0055, 0.0055, 0.24, mat('hinge', { color: 0x2a2b2d, metalness: 0.5, roughness: 0.4 }), 0, 0, 0, 24, null);
      hinge.rotation.z = Math.PI / 2; hinge.position.set(0, Tb, -Db / 2 + 0.006); g.add(hinge);
      // lid, pivoting on the back edge
      const lid = new THREE.Group(); lid.position.set(0, Tb, -Db / 2 + 0.006);
      const ang = ((o.open != null ? o.open : 110) - 90) * Math.PI / 180;
      lid.rotation.x = -ang; g.add(lid);
      const Hl = 0.215;
      rbox(Wb, Hl, 0.0055, 0.004, shell, 0, 0.002, -0.0035, lid, 3);
      box(Wb - 0.004, Hl - 0.004, 0.0008, mat('bezel', { color: 0x0b0b0c, roughness: 0.15 }), 0, 0.004, 0.0, lid);
      if (o.screen !== 'off') {
        const scr = new THREE.Mesh(new THREE.PlaneGeometry(0.296, 0.185), screenMat(o.screen || 'doc', !!o.dark, o.seed || 1));
        scr.position.set(0, 0.004 + 0.012 + 0.185 / 2, 0.0006); lid.add(scr);
      }
      cyl(0.0012, 0.0012, 0.0004, mat('cam', { color: 0x050507, roughness: 0.1 }), 0, 0, 0, 12, null).position.set(0, 0.211, 0.0008);
      const cam = new THREE.Mesh(new THREE.CircleGeometry(0.0013, 16), mat('cam', { color: 0x050507, roughness: 0.1 })); cam.position.set(0, 0.2105, 0.0006); lid.add(cam);
      // rubber feet
      [[-0.13, -0.09], [0.13, -0.09], [-0.13, 0.09], [0.13, 0.09]].forEach(([x, z]) => cyl(0.006, 0.006, 0.001, M.rubber(), x, -0.0008, z, 12, g));
      return centre(g);
    },
  });

  K.define('monitor', {
    size: [0.62, 0.52, 0.2],
    options: { inches: 27, screen: 'chart', dark: true, finish: 'black' },
    note: 'Desktop monitor (27 in default) on a stand: thin bezel front with a lit display (screen chart | dash | doc | sheet | off; no legible text), a bulged rear housing with vents, a slim neck and a flat base. Faces +z.',
    make(o) {
      const g = new THREE.Group();
      const diag = (o.inches || 27) * 0.0254, sw = diag * 16 / Math.hypot(16, 9), sh = diag * 9 / Math.hypot(16, 9);
      const body = o.finish === 'silver' ? M.alu(0xbfc2c5) : M.plastic(0x1a1b1d);
      const y0 = 0.1;
      const head = new THREE.Group(); head.position.set(0, y0 + (sh + 0.03) / 2, 0); head.rotation.x = -0.06; g.add(head);
      rbox(sw + 0.012, sh + 0.03, 0.012, 0.004, body, 0, -(sh + 0.03) / 2, 0, head, 2);
      box(sw + 0.004, sh + 0.004, 0.0006, mat('bezel', { color: 0x0b0b0c, roughness: 0.15 }), 0, -(sh + 0.03) / 2 + 0.024, 0.0062, head);
      if (o.screen !== 'off') {
        const scr = new THREE.Mesh(new THREE.PlaneGeometry(sw, sh), screenMat(o.screen || 'chart', o.dark !== false, 3));
        scr.position.set(0, -(sh + 0.03) / 2 + 0.026 + sh / 2, 0.0066); head.add(scr);
      }
      const led = new THREE.Mesh(new THREE.CircleGeometry(0.0015, 12), mat('pwrled', { color: 0x001100, emissive: 0xffffff, emissiveIntensity: 1.2 }));
      led.position.set(sw / 2 - 0.02, -(sh + 0.03) / 2 + 0.008, 0.0065); head.add(led);
      const rear = TXT.roundedBox(sw * 0.7, sh * 0.72, 0.045, 0.02, body, { segments: 3 });
      rear.position.set(0, -0.01, -0.028); head.add(rear);
      // stand
      const neck = rbox(0.06, 0.3, 0.018, 0.006, body, 0, 0, 0, null, 2);
      neck.position.set(0, y0 + 0.14, -0.07); neck.rotation.x = 0.12; g.add(neck);
      const base = TXT.roundedBox(0.25, 0.012, 0.19, 0.03, body, { segments: 3 });
      base.position.set(0, 0.006, -0.04); g.add(base);
      rbox(0.07, 0.03, 0.05, 0.008, body, 0, 0.01, -0.06, g);
      return centre(g);
    },
  });

  /* ========================================================================== PAPERWORK */
  function paperStack(parent, x, y, z, h, rot, r, cover) {
    const w = 0.216, d = 0.279;
    const side = ltex('sheets', paintSheets, {}, [64, 256]).clone(); side.needsUpdate = true; side.repeat.set(1, Math.max(1, h / 0.01));
    const sideM = mat('paperSide' + Math.round(h * 1000), { color: 0xffffff, roughness: 0.95, map: side });
    const topM = cover != null ? mat('cover' + cover, { color: cover, roughness: 0.8 }) : mat('paperTop', { color: 0xffffff, roughness: 0.9, map: ltex('page', paintPage, {}, [256, 330]) });
    // several sub stacks, never perfectly aligned
    let yy = y; const parts = Math.max(1, Math.round(h / 0.012));
    for (let k = 0; k < parts; k++) {
      const hh = h / parts, last = k === parts - 1;
      const m = new THREE.Mesh(new THREE.BoxGeometry(w, hh, d), [sideM, sideM, last ? topM : sideM, sideM, sideM, sideM]);
      m.position.set(x + (r() - 0.5) * 0.008, yy + hh / 2, z + (r() - 0.5) * 0.008); m.rotation.y = rot + (r() - 0.5) * 0.05;
      parent.add(m); yy += hh;
    }
    return yy;
  }
  function binder(parent, x, y, z, rot, col, thick) {
    const b = new THREE.Group(); b.position.set(x, y, z); b.rotation.y = rot; parent.add(b);
    const c = mat('binder' + col, { color: col, roughness: 0.45 });
    const t = thick || 0.05, w = 0.29, d = 0.3;
    rbox(w, 0.003, d, 0.0012, c, 0.004, 0, 0, b, 1);
    rbox(w, 0.003, d, 0.0012, c, 0.004, t - 0.003, 0, b, 1);
    rbox(0.006, t, d, 0.0025, c, -w / 2 + 0.003, 0, 0, b, 1);
    // pages inside
    const pages = new THREE.Mesh(new THREE.BoxGeometry(w - 0.03, t - 0.012, 0.28), mat('paperSideB', { color: 0xf0eee8, roughness: 0.95, map: ltex('sheets', paintSheets, {}, [64, 256]) }));
    pages.position.set(0.004, t / 2, 0); b.add(pages);
    // clear spine pocket
    box(0.001, t * 0.7, 0.18, mat('spineLabel', { color: 0xf5f3ee, roughness: 0.6 }), -w / 2 - 0.0005, t * 0.15, 0.02, b);
    return y + t;
  }
  function clipped(parent, x, y, z, rot, r) {
    const top = paperStack(parent, x, y, z, 0.012, rot, r, 0xe8e4d8);
    const clip = new THREE.Group(); clip.position.set(x, top, z); clip.rotation.y = rot; parent.add(clip);
    // binder clip on the top edge (-z edge of the page)
    const prof = [[-0.012, 0], [0.012, 0], [0.004, 0.018], [-0.004, 0.018]];
    const body = new THREE.Mesh(new THREE.ExtrudeGeometry(new THREE.Shape(prof.map((p) => new THREE.Vector2(p[0], p[1]))), { depth: 0.05, bevelEnabled: true, bevelThickness: 0.001, bevelSize: 0.001, bevelSegments: 1 }),
      mat('clipBlack', { color: 0x121213, roughness: 0.3, metalness: 0.4 }));
    body.geometry.rotateY(Math.PI / 2); body.geometry.rotateX(Math.PI / 2); body.geometry.translate(-0.025, -0.006, 0);
    body.position.set(0, -0.006, -0.279 / 2 + 0.006); clip.add(body);
    for (const s of [-1, 1]) {
      tube([[s * 0.02, 0.006, -0.279 / 2], [s * 0.02, 0.012, -0.279 / 2 + 0.03], [0, 0.013, -0.279 / 2 + 0.045], [-s * 0.02, 0.012, -0.279 / 2 + 0.03], [-s * 0.02, 0.006, -0.279 / 2]].map((p) => [p[0] * 0.9, p[1] + (s > 0 ? 0.001 : 0), p[2]]),
        0.0011, M.chrome(), 32, 6, clip);
    }
    return top + 0.012;
  }
  K.define('document_stack', {
    size: [0.75, 0.2, 0.45],
    options: { count: 5 },
    note: 'Paperwork on a surface: ragged paper stacks with printed top pages (grey text lines, nothing legible), 3 ring binders stacked with blank spine pockets, and a report with a black binder clip. count = number of piles (1 to 8); seed varies the mix, colours and angles.',
    make(o, r) {
      const n = Math.max(1, Math.min(8, o.count || 5));
      const g = new THREE.Group();
      const cols = [0x1f2a44, 0x16181b, 0xe9e7e1, 0x6b1f23, 0x2d4a3a, 0x3a3f48];
      for (let i = 0; i < n; i++) {
        const x = (i % 4 - 1.5) * 0.24 + (r() - 0.5) * 0.04, z = (Math.floor(i / 4) - 0.5 * (n > 4 ? 1 : 0)) * 0.34 + (r() - 0.5) * 0.04;
        const kind = i === 0 ? 'binders' : i === 1 ? 'report' : ['paper', 'paper', 'binders', 'report'][Math.floor(r() * 4)];
        const rot = (r() - 0.5) * 0.5;
        if (kind === 'paper') { let y = paperStack(g, x, 0, z, 0.02 + r() * 0.07, rot, r); if (r() < 0.5) clipped(g, x + 0.01, y, z, rot + (r() - 0.5) * 0.3, r); }
        else if (kind === 'binders') { let y = 0; const k = 1 + Math.floor(r() * 3); for (let j = 0; j < k; j++) y = binder(g, x + (r() - 0.5) * 0.02, y, z, rot + (r() - 0.5) * 0.2, cols[Math.floor(r() * cols.length)], [0.035, 0.05, 0.065][Math.floor(r() * 3)]); }
        else { let y = paperStack(g, x, 0, z, 0.01 + r() * 0.02, rot, r); clipped(g, x, y, z, rot + (r() - 0.5) * 0.2, r); }
      }
      return centre(g);
    },
  });

  K.define('filing_cabinet', {
    size: [0.38, 1.33, 0.67],
    options: { drawers: 4, color: 0xc9c1ad, lateral: false },
    note: 'Vertical steel filing cabinet (letter, 4 drawers default, 2 to 5): baked enamel body, drawer fronts with recessed pull handles and label holders, a lock cylinder, a recessed kick base. lateral: true makes a 36 in wide lateral file. One drawer may sit ajar by seed.',
    make(o, r) {
      const n = Math.max(2, Math.min(5, o.drawers || 4));
      const W = o.lateral ? 0.91 : 0.38, D = o.lateral ? 0.47 : 0.67, dh = o.lateral ? 0.36 : 0.31, H = 0.05 + n * dh + 0.03;
      const g = new THREE.Group();
      const paint = mat('cabinet' + (o.color || 0xc9c1ad), { color: o.color != null ? o.color : 0xc9c1ad, roughness: 0.42, metalness: 0.25 });
      const dark = mat('toe', { color: 0x151312, roughness: 0.8 });
      box(W - 0.02, 0.05, D - 0.04, dark, 0, 0, -0.01, g);
      rbox(W, H - 0.05, D, 0.006, paint, 0, 0.05, 0, g, 2);
      rbox(W + 0.006, 0.012, D + 0.006, 0.005, paint, 0, H - 0.012, 0.0, g, 2);
      const ajar = r() < 0.5 ? Math.floor(r() * n) : -1;
      const chrome = M.chrome();
      for (let k = 0; k < n; k++) {
        const y = 0.06 + k * dh, out = k === ajar ? 0.05 + r() * 0.08 : 0;
        const fr = rbox(W - 0.012, dh - 0.008, 0.022, 0.005, paint, 0, y, D / 2 + 0.003 + out, g, 2); void fr;
        if (out) box(W - 0.05, dh - 0.03, out, mat('drawerIn', { color: 0x3d3b37, roughness: 0.7 }), 0, y + 0.02, D / 2 - out / 2, g);
        // recessed pull: dark cavity with a chrome lip
        const py = y + dh * 0.62, pz = D / 2 + 0.016 + out;
        box(0.13, 0.03, 0.004, mat('pullCavity', { color: 0x1c1b19, roughness: 0.6 }), 0, py - 0.015, pz, g);
        rbox(0.15, 0.012, 0.022, 0.004, chrome, 0, py + 0.012, pz + 0.004, g, 2);
        // label holder with a card
        rbox(0.085, 0.036, 0.004, 0.0015, chrome, 0, py + 0.045, pz, g, 1);
        box(0.075, 0.026, 0.001, mat('labelCard', { color: 0xf1ede2, roughness: 0.9 }), 0, py + 0.05, pz + 0.0025, g);
      }
      const lock = cyl(0.011, 0.011, 0.012, chrome, 0, 0, 0, 20, null); lock.rotation.x = Math.PI / 2;
      lock.position.set(W / 2 - 0.04, H - 0.04, D / 2 + 0.008); g.add(lock);
      return g;
    },
  });

  /* ============================================================================== FLAGS */
  function star5(x, cx, cy, R) {
    x.beginPath();
    for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? R * 0.382 : R; x.lineTo(cx + Math.cos(a) * rr, cy + Math.sin(a) * rr); }
    x.closePath(); x.fill();
  }
  function paintUS(x, W, H) {
    for (let i = 0; i < 13; i++) { x.fillStyle = i % 2 ? '#f4f1ea' : '#b22234'; x.fillRect(0, i * H / 13, W, H / 13 + 1); }
    const cw = W * 0.4, ch = H * 7 / 13; x.fillStyle = '#3c3b6e'; x.fillRect(0, 0, cw, ch);
    x.fillStyle = '#f4f1ea';
    for (let j = 0; j < 9; j++) { const cnt = j % 2 ? 5 : 6; for (let i = 0; i < cnt; i++) {
      const cx = cw / 12 * (2 * i + 1 + (j % 2)), cy = ch / 10 * (j + 1); star5(x, cx, cy, ch * 0.0616 * 1.0); } }
    weaveOver(x, W, H);
  }
  function paintTX(x, W, H) {
    x.fillStyle = '#f4f1ea'; x.fillRect(0, 0, W, H / 2);
    x.fillStyle = '#bf0d3e'; x.fillRect(0, H / 2, W, H / 2);
    x.fillStyle = '#002868'; x.fillRect(0, 0, W / 3, H);
    x.fillStyle = '#f4f1ea'; star5(x, W / 6, H / 2, (W / 3) * 0.375);
    weaveOver(x, W, H);
  }
  function weaveOver(x, W, H) {
    x.fillStyle = 'rgba(0,0,0,0.035)'; for (let y = 0; y < H; y += 3) x.fillRect(0, y, W, 1);
    for (let xx = 0; xx < W; xx += 3) x.fillRect(xx, 0, 1, H);
    // hem stitches on the free edges
    x.strokeStyle = 'rgba(0,0,0,0.25)'; x.setLineDash([6, 5]); x.lineWidth = 2;
    x.strokeRect(6, 6, W - 12, H - 12); x.setLineDash([]);
  }
  function paintFringe(x, W, H, r) {
    x.clearRect(0, 0, W, H);
    for (let i = 0; i < W; i += 3) { const len = H * (0.85 + r() * 0.15); const v = 0.75 + r() * 0.35;
      x.fillStyle = 'rgba(' + Math.round(222 * v) + ',' + Math.round(178 * v) + ',' + Math.round(86 * v) + ',1)'; x.fillRect(i, 0, 2, len); }
    x.fillStyle = 'rgb(200,160,70)'; x.fillRect(0, 0, W, H * 0.12);
  }
  // one indoor flag on a floor stand; the flag drapes toward +x, then is turned by `turn`
  function flagOnStand(kind, r, turn) {
    const g = new THREE.Group();
    const poleH = 2.44, Hf = 1.22, Lf = 1.83, top = poleH - 0.06;
    const brass = M.brass();
    const pole = mat('oakPole', { color: 0xffffff, roughness: 0.35, map: ltex('veneer', paintVeneer, { color: '#7a5431' }) });
    // stand: weighted bell base, three short feet
    lathe([[0, 0.015], [0.2, 0.015], [0.205, 0.03], [0.17, 0.05], [0.08, 0.1], [0.04, 0.17], [0.035, 0.24], [0.05, 0.25], [0.028, 0.27], [0, 0.27]], brass, 64, g);
    for (let k = 0; k < 3; k++) { const a = k * TAU / 3; cyl(0.03, 0.03, 0.015, M.rubber(), Math.cos(a) * 0.16, 0, Math.sin(a) * 0.16, 16, g); }
    const pg = new THREE.CylinderGeometry(0.0165, 0.0165, poleH - 0.26, 24); K.uvBox(pg, 1.2);
    const pm = new THREE.Mesh(pg, pole); pm.position.y = 0.26 + (poleH - 0.26) / 2; g.add(pm);
    cyl(0.021, 0.021, 0.04, brass, 0, 1.2, 0, 24, g);     // joint ferrule
    // finial: ferrule and a flat spear head
    lathe([[0, poleH], [0.022, poleH], [0.024, poleH + 0.02], [0.016, poleH + 0.05], [0.02, poleH + 0.07], [0.012, poleH + 0.09], [0, poleH + 0.09]], brass, 32, g);
    const sp = [[0, 0], [0.045, 0.07], [0.012, 0.2], [0, 0.23], [-0.012, 0.2], [-0.045, 0.07]];
    const spear = new THREE.Mesh(new THREE.ExtrudeGeometry(new THREE.Shape(sp.map((p) => new THREE.Vector2(p[0], p[1]))), { depth: 0.006, bevelEnabled: true, bevelThickness: 0.004, bevelSize: 0.004, bevelSegments: 2 }), brass);
    spear.position.set(0, poleH + 0.085, -0.003); spear.rotation.y = turn + Math.PI / 2; g.add(spear);
    // the cloth: arc length preserved, droops from the pole, pleats that run down the fall
    const NS = 44, NT = 30, fringe = 0.07;
    const th0 = 1.3 + (r() - 0.5) * 0.15, k = 2.2 + r() * 0.8, ph = r() * TAU;
    function point(s, t) {
      // s along the fly (0 at the pole), t down the hoist (0 at the top); both may exceed 1 for fringe
      const steps = 24; let x = 0.019, y = top - t * Hf, z = 0;
      const thT = th0 * (1 - 0.35 * t);
      for (let i = 0; i < steps; i++) {
        const u = (i + 0.5) / steps * s, th = thT * Math.pow(Math.max(0, 1 - u), 1.6) + 0.05;
        x += Math.sin(th) * Lf * s / steps; y -= Math.cos(th) * Lf * s / steps;
      }
      // folds take up length: the fall is foreshortened and the pleats deepen toward the fly
      x = 0.019 + (x - 0.019) * 0.72; y = top - t * Hf - ((top - t * Hf) - y) * 0.42;
      const amp = 0.11 * Math.pow(Math.min(s, 1.05), 0.7);
      z = amp * Math.sin(TAU * k * t + ph + s * 1.2) + 0.03 * Math.sin(TAU * 1.3 * t + ph * 0.7) * s;
      x += amp * 0.35 * Math.cos(TAU * k * t + ph);
      // gather toward the pole low on the hoist
      return new THREE.Vector3(x * (1 - 0.15 * t * (1 - s)), y, z);
    }
    function sheet(s0, s1, t0, t1, ns, nt, material, uvf) {
      const pos = [], uv = [], idx = [];
      for (let j = 0; j <= nt; j++) for (let i = 0; i <= ns; i++) {
        const s = s0 + (s1 - s0) * i / ns, t = t0 + (t1 - t0) * j / nt, p = point(s, t);
        pos.push(p.x, p.y, p.z); const q = uvf(i / ns, j / nt); uv.push(q[0], q[1]);
      }
      for (let j = 0; j < nt; j++) for (let i = 0; i < ns; i++) {
        const a = j * (ns + 1) + i, b = a + 1, c = a + ns + 1, d = c + 1; idx.push(a, c, b, b, c, d);
      }
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); geo.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
      geo.setIndex(idx); geo.computeVertexNormals();
      return new THREE.Mesh(geo, material);
    }
    const cloth = new THREE.Group(); cloth.rotation.y = turn; g.add(cloth);
    const flagTex = ltex(kind === 'us' ? 'flagUS' : 'flagTX', kind === 'us' ? paintUS : paintTX, {}, [1024, 683]);
    const fm = mat('flag' + kind, { color: 0xffffff, roughness: 0.62, map: flagTex, side: THREE.DoubleSide, sheen: 0.6, sheenRoughness: 0.5, sheenColor: 0xffffff }, true);
    cloth.add(sheet(0, 1, 0, 1, NS, NT, fm, (u, v) => [u, 1 - v]));
    const fr = ltex('fringe', paintFringe, {}, [512, 64]);
    const frM = mat('fringe', { color: 0xffffff, roughness: 0.5, metalness: 0.3, map: fr, alphaTest: 0.45, side: THREE.DoubleSide });
    const frRep = fr; void frRep;
    cloth.add(sheet(1, 1 + fringe / Lf, 0, 1, 2, NT, frM, (u, v) => [v * 12, 1 - u]));     // fly edge
    cloth.add(sheet(0, 1 + fringe / Lf, 1, 1 + fringe / Hf, NS, 2, frM, (u, v) => [u * 18, 1 - v]));   // bottom edge
    // pole sleeve
    const sl = new THREE.Mesh(new THREE.CylinderGeometry(0.024, 0.024, Hf, 24, 1, true), mat('sleeve' + kind, { color: kind === 'us' ? 0xf0ede6 : 0x0c2c66, roughness: 0.7 }));
    sl.position.y = top - Hf / 2; g.add(sl);
    // cord and tassels from the finial
    const cordM = mat('cord', { color: 0xd4ac5a, metalness: 0.4, roughness: 0.5 });
    const ca = turn + Math.PI + 0.5;
    const cx = Math.cos(ca) * 0.03, cz = -Math.sin(ca) * 0.03;
    for (const [dx, len] of [[0.0, 0.55], [0.03, 0.65]]) {
      tube([[0, top + 0.02, 0], [cx * 2 + dx, top - 0.1, cz * 2], [cx * 3 + dx, top - len * 0.6, cz * 3], [cx * 3 + dx * 1.2, top - len, cz * 3]], 0.004, cordM, 32, 6, g);
      const ts = lathe([[0, 0], [0.012, 0.005], [0.02, 0.03], [0.024, 0.09], [0.028, 0.12], [0, 0.12]], mat('tassel', { color: 0xd8b060, roughness: 0.7, metalness: 0.2 }), 24, null);
      ts.rotation.x = Math.PI; ts.position.set(cx * 3 + dx * 1.2, top - len + 0.005, cz * 3); g.add(ts);
      lathe([[0, 0], [0.012, 0.0], [0.016, 0.02], [0.01, 0.035], [0, 0.035]], brass, 20, g).position.set(cx * 3 + dx * 1.2, top - len - 0.02, cz * 3);
    }
    return g;
  }
  K.define('flags_pair', {
    size: [2.2, 2.55, 1.2],
    options: { spacing: 1.0, order: 'us-left' },
    note: 'The United States and Texas flags on indoor floor stands: oak poles with brass spear finials and bell bases, 4 x 6 ft cloth draped as real geometry (arc length preserved, pleats along the fall), gold fringe on the free edges, gold cords and tassels. Facing the audience (+z) the US flag stands on the viewer\'s left, which is its own right, as flag code places it.',
    make(o, r) {
      const g = new THREE.Group(), sp = o.spacing || 1.0;
      const us = flagOnStand('us', r, -0.35 - Math.PI * 0.08); us.position.x = -sp / 2; g.add(us);
      const tx = flagOnStand('tx', r, -0.5 - Math.PI * 0.05); tx.position.x = sp / 2; g.add(tx);
      if (o.order === 'us-right') { us.position.x = sp / 2; tx.position.x = -sp / 2; }
      return g;
    },
  });

  /* ========================================================================== SERVER ROW */
  // One rack's face: a painted atlas of servers plus an LED emissive layer.
  function rackLayout(r) {
    const units = [];
    let u = 42;
    const take = (n, type) => { if (u - n < 0) return; units.push({ top: u, n, type }); u -= n; };
    take(1, 'patch'); take(1, 'switch'); take(1, 'switch'); take(1, 'blank');
    while (u > 2) {
      const p = r();
      if (p < 0.34) take(2, 'server2'); else if (p < 0.62) take(1, 'server1'); else if (p < 0.72) take(4, 'storage');
      else if (p < 0.8) take(1, 'blank'); else if (p < 0.86) take(2, 'blank'); else take(2, 'gpu');
    }
    while (u > 0) take(1, 'blank');
    return units;
  }
  function paintRack(x, W, H, r, o) {
    const layout = o.layout, Upx = H / 42, emissive = o.emissive;
    x.fillStyle = emissive ? '#000' : '#101113'; x.fillRect(0, 0, W, H);
    const led = (cx, cy, col, rr) => { if (!emissive) { x.fillStyle = '#2a2d31'; x.fillRect(cx - rr, cy - rr, rr * 2, rr * 2); return; }
      const g = x.createRadialGradient(cx, cy, 0, cx, cy, rr * 2.5); g.addColorStop(0, col); g.addColorStop(0.4, col); g.addColorStop(1, 'rgba(0,0,0,0)');
      x.fillStyle = g; x.fillRect(cx - rr * 3, cy - rr * 3, rr * 6, rr * 6); };
    const green = '#4dff7a', blue = '#58a8ff', amber = '#ffb13b', white = '#e8f2ff';
    layout.forEach(({ top, n, type }) => {
      const y0 = (42 - top) * Upx + 1, h = n * Upx - 2;
      if (!emissive) {
        const face = type === 'blank' ? '#15171a' : type === 'gpu' ? '#23262b' : type === 'storage' ? '#2b2e33' : type === 'switch' ? '#1c1f24' : type === 'patch' ? '#17191c' : '#2f3238';
        x.fillStyle = face; x.fillRect(4, y0, W - 8, h);
        x.fillStyle = 'rgba(255,255,255,0.06)'; x.fillRect(4, y0, W - 8, 1.5);
        x.fillStyle = 'rgba(0,0,0,0.5)'; x.fillRect(4, y0 + h - 1.5, W - 8, 1.5);
        // ears
        x.fillStyle = '#3a3d42'; x.fillRect(0, y0, 10, h); x.fillRect(W - 10, y0, 10, h);
      }
      if (type === 'blank') {
        if (!emissive) { x.fillStyle = 'rgba(0,0,0,0.5)'; for (let i = 20; i < W - 20; i += 7) for (let j = y0 + 4; j < y0 + h - 4; j += 6) x.fillRect(i, j, 3, 2); }
      } else if (type === 'server1') {
        const bays = 8, bw = (W * 0.62) / bays;
        for (let i = 0; i < bays; i++) { const bx = 16 + i * bw;
          if (!emissive) { x.fillStyle = '#1a1c20'; x.fillRect(bx, y0 + 3, bw - 3, h - 6); x.fillStyle = '#4a4e55'; x.fillRect(bx + 2, y0 + 5, bw - 7, 3); }
          led(bx + bw - 7, y0 + h - 6, r() < 0.8 ? green : blue, 1.4); }
        if (!emissive) { x.fillStyle = 'rgba(0,0,0,0.55)'; for (let i = W * 0.7; i < W - 22; i += 5) x.fillRect(i, y0 + 4, 2.5, h - 8); }
        led(W - 18, y0 + h / 2, blue, 2);
      } else if (type === 'server2') {
        const bays = 24, bw = (W * 0.86) / bays;
        for (let i = 0; i < bays; i++) { const bx = 18 + i * bw;
          if (!emissive) { x.fillStyle = '#16181b'; x.fillRect(bx, y0 + 4, bw - 2, h - 8); x.fillStyle = '#50545b'; x.fillRect(bx + 1, y0 + 6, bw - 4, 2.5); x.fillStyle = '#2c2f34'; x.fillRect(bx + 1, y0 + h * 0.5, bw - 4, h * 0.3); }
          const on = r(); led(bx + bw / 2 - 1, y0 + h - 8, on < 0.85 ? green : on < 0.95 ? blue : amber, 1.3); }
        led(W - 16, y0 + 8, blue, 2); led(W - 16, y0 + 16, green, 1.5);
      } else if (type === 'storage') {
        for (let j = 0; j < 3; j++) for (let i = 0; i < 4; i++) {
          const bx = 16 + i * (W - 32) / 4, by = y0 + 3 + j * (h - 6) / 3, bw = (W - 32) / 4 - 4, bh = (h - 6) / 3 - 3;
          if (!emissive) { x.fillStyle = '#1b1d21'; x.fillRect(bx, by, bw, bh); x.fillStyle = 'rgba(0,0,0,0.5)'; for (let k = bx + 6; k < bx + bw - 20; k += 5) x.fillRect(k, by + 3, 2, bh - 6); x.fillStyle = '#5a5e65'; x.fillRect(bx + bw - 16, by + 3, 10, bh - 6); }
          led(bx + bw - 10, by + bh - 5, r() < 0.9 ? blue : amber, 1.4);
        }
      } else if (type === 'gpu') {
        if (!emissive) { x.fillStyle = 'rgba(0,0,0,0.6)'; for (let i = 16; i < W - 16; i += 6) for (let j = y0 + 4; j < y0 + h - 4; j += 6) { x.beginPath(); x.arc(i, j, 2, 0, TAU); x.fill(); }
          x.fillStyle = '#6c7078'; x.fillRect(W / 2 - 30, y0 + h / 2 - 3, 60, 6); }
        led(W - 20, y0 + 6, green, 1.8); led(28, y0 + 6, white, 1.4);
      } else if (type === 'switch' || type === 'patch') {
        const ports = 24;
        for (let row = 0; row < 2; row++) for (let i = 0; i < ports; i++) {
          const bx = 22 + i * (W * 0.72) / ports + Math.floor(i / 6) * 3, by = y0 + 3 + row * (h - 6) / 2;
          if (!emissive) { x.fillStyle = '#050506'; x.fillRect(bx, by + 1, (W * 0.72) / ports - 3, (h - 6) / 2 - 2); }
          if (type === 'switch' && r() < 0.75) led(bx + 2, by + 2, r() < 0.8 ? green : amber, 0.9);
        }
        if (type === 'switch') for (let i = 0; i < 4; i++) { if (!emissive) { x.fillStyle = '#6f737a'; x.fillRect(W * 0.8 + i * 12, y0 + 5, 9, h - 10); } led(W * 0.8 + i * 12 + 4, y0 + 3, green, 0.9); }
      }
    });
  }
  K.define('server_row', {
    size: [4.2, 2.5, 2.4],
    options: { racks: 6, doors: false, containment: true, tray: true, floor: true },
    note: 'A data hall row: 42U racks (0.6 x 2.0 x 1.2 m) with servers, storage shelves, GPU nodes and top of rack switches painted per rack (status LEDs glow), mounting rails, blanking panels and patch cords; overhead ladder tray with a yellow fibre raceway; hot aisle containment panels above the rear; perforated cold aisle floor tiles in front. doors: true adds perforated front doors. Fronts face +z.',
    make(o, r) {
      const n = Math.max(1, Math.min(12, o.racks || 6));
      const g = new THREE.Group(), RW = 0.6, RH = 2.0, RD = 1.2;
      const blackPC = mat('rackBlack', { color: 0x151618, roughness: 0.5, metalness: 0.35 });
      const rail = mat('rackRail', { color: 0x2a2c30, roughness: 0.45, metalness: 0.6 });
      const variants = Math.min(n, 4), faces = [];
      for (let v = 0; v < variants; v++) {
        const rr = K.rng((o.seed || 1) * 31 + v * 7), layout = rackLayout(rr);
        const map = ltex('rackface', (x, W, H) => paintRack(x, W, H, K.rng(v + 3), { layout }), { v, s: o.seed || 1 }, [384, 1536]);
        const em = ltex('rackled', (x, W, H) => paintRack(x, W, H, K.rng(v + 3), { layout, emissive: true }), { v, s: o.seed || 1 }, [384, 1536]);
        faces.push({ layout, m: mat('rackface' + v + '|' + (o.seed || 1), { color: 0xffffff, roughness: 0.45, metalness: 0.4, map, emissive: 0xffffff, emissiveMap: em, emissiveIntensity: 2.4 }) });
      }
      const x0 = -(n - 1) * RW / 2;
      for (let i = 0; i < n; i++) {
        const x = x0 + i * RW, f = faces[i % variants];
        const rk = new THREE.Group(); rk.position.x = x; g.add(rk);
        // frame: sides, top, plinth, corner posts
        box(0.015, RH - 0.1, RD, blackPC, -RW / 2 + 0.0075, 0.1, 0, rk); if (i === n - 1) box(0.015, RH - 0.1, RD, blackPC, RW / 2 - 0.0075, 0.1, 0, rk);
        rbox(RW, 0.04, RD, 0.006, blackPC, 0, RH - 0.04, 0, rk, 1);
        box(RW - 0.02, 0.1, RD - 0.04, blackPC, 0, 0, 0, rk);
        for (const sx of [-1, 1]) for (const sz of [-1, 1]) box(0.03, RH - 0.14, 0.03, blackPC, sx * (RW / 2 - 0.03), 0.1, sz * (RD / 2 - 0.03), rk);
        // 19 in rails and the face
        const fz = RD / 2 - 0.07;
        for (const sx of [-1, 1]) box(0.04, 1.87, 0.02, rail, sx * 0.243, 0.1, fz, rk);
        const face = new THREE.Mesh(new THREE.PlaneGeometry(0.482, 1.87), f.m); face.position.set(0, 0.1 + 1.87 / 2, fz + 0.012); rk.add(face);
        // handles on servers: small pulls either side
        const handles = [];
        f.layout.forEach(({ top, n: un, type }) => {
          if (type === 'blank' || type === 'patch') return;
          const yc = 0.1 + (top - un / 2) * 0.04445;
          for (const sx of [-1, 1]) handles.push(new THREE.Matrix4().makeTranslation(sx * 0.225, yc, fz + 0.025));
        });
        const hg = new THREE.BoxGeometry(0.012, 0.028, 0.022);
        const him = new THREE.InstancedMesh(hg, mat('handle', { color: 0x9da1a6, metalness: 0.8, roughness: 0.35 }), handles.length);
        handles.forEach((m4, k) => him.setMatrixAt(k, m4)); rk.add(him);
        // patch cords off the switches to the left rail
        const cordCols = [0x2b6fd6, 0xe0c341, 0x9aa0a6, 0x2b6fd6, 0xd94a3a];
        for (let k = 0; k < 6; k++) {
          const y = 0.1 + (41 - (k % 2)) * 0.04445 + 0.02, xs = -0.15 + k * 0.035;
          tube([[xs, y, fz + 0.02], [xs - 0.02, y - 0.03, fz + 0.08], [-0.2, y - 0.06 - k * 0.01, fz + 0.07], [-0.24, y - 0.1 - k * 0.012, fz + 0.03]], 0.0028,
            mat('cord' + k, { color: cordCols[k % cordCols.length], roughness: 0.5 }), 16, 5, rk);
        }
        // rear: cable bundles and vertical PDUs (the hot aisle side)
        for (const sx of [-1, 1]) {
          box(0.05, 1.7, 0.05, mat('pdu', { color: 0x202225, roughness: 0.5 }), sx * 0.22, 0.2, -RD / 2 + 0.08, rk);
          tube([[sx * 0.15, RH - 0.05, -RD / 2 + 0.1], [sx * 0.16, 1.2, -RD / 2 + 0.06], [sx * 0.14, 0.4, -RD / 2 + 0.1]], 0.025, mat('bundle', { color: 0x2f4f8a, roughness: 0.55 }), 24, 10, rk);
        }
        if (o.doors) {
          const perf = ltex('perfdoor', (x, W, H) => { x.fillStyle = '#fff'; x.fillRect(0, 0, W, H); x.fillStyle = '#000';
            for (let j = 0; j < H; j += 8) for (let k = (j / 8) % 2 ? 4 : 0; k < W; k += 8) { x.beginPath(); x.arc(k, j, 2.8, 0, TAU); x.fill(); } }, {}, [128, 128], true);
          const pp = perf; pp.repeat.set(20, 60);
          const door = new THREE.Mesh(new THREE.PlaneGeometry(RW - 0.06, RH - 0.2), mat('door', { color: 0x151618, metalness: 0.5, roughness: 0.4, alphaMap: pp, alphaTest: 0.5, side: THREE.DoubleSide }));
          door.position.set(0, 0.1 + (RH - 0.2) / 2, RD / 2 + 0.005); rk.add(door);
          box(0.02, RH - 0.2, 0.02, blackPC, RW / 2 - 0.04, 0.1, RD / 2 + 0.01, rk);
        }
      }
      const L = n * RW;
      if (o.tray !== false) {
        // ladder tray over the fronts, yellow raceway over the rears
        const ty = RH + 0.35;
        for (const sz of [-0.2, 0.2]) box(L + 0.3, 0.06, 0.01, blackPC, 0, ty, RD / 2 - 0.3 + sz, g);
        const rungs = []; for (let k = 0; k <= Math.floor((L + 0.3) / 0.3); k++) rungs.push(new THREE.Matrix4().makeTranslation(-L / 2 - 0.15 + k * 0.3, ty + 0.02, RD / 2 - 0.3));
        const rim = new THREE.InstancedMesh(new THREE.BoxGeometry(0.02, 0.012, 0.4), blackPC, rungs.length); rungs.forEach((m4, k) => rim.setMatrixAt(k, m4)); g.add(rim);
        for (let k = 0; k < 5; k++) tube([[-L / 2 - 0.15, ty + 0.045, RD / 2 - 0.42 + k * 0.05], [L / 2 + 0.15, ty + 0.045, RD / 2 - 0.42 + k * 0.05]], 0.012 + k % 2 * 0.004, mat('trayCable' + (k % 3), { color: [0x2b6fd6, 0x7c8087, 0x303236][k % 3], roughness: 0.6 }), 4, 8, g);
        const yel = mat('fiberDuct', { color: 0xe8b81c, roughness: 0.45 });
        rbox(L + 0.3, 0.1, 0.3, 0.01, yel, 0, ty - 0.05, -0.1, g, 2);
        for (let k = 0; k < n; k += 2) { const x = x0 + k * RW; tube([[x, ty - 0.03, -0.1], [x, ty - 0.2, -0.15], [x, RH + 0.02, -0.25]], 0.035, yel, 12, 12, g); }
        for (let k = 0; k <= Math.ceil(n / 2); k++) { const x = -L / 2 + k * (L / Math.ceil(n / 2)); K.bar([x, ty, RD / 2 - 0.3], [x, RH + 1.0, RD / 2 - 0.3], 0.008, rail, 8, g); K.bar([x, ty - 0.05, -0.1], [x, RH + 1.0, -0.1], 0.008, rail, 8, g); }
      }
      if (o.containment !== false) {
        const poly = mat('polycarb', { color: 0xdfe6ea, transparent: true, opacity: 0.22, roughness: 0.15, metalness: 0.0, side: THREE.DoubleSide });
        const pn = new THREE.Mesh(new THREE.PlaneGeometry(L, 0.9), poly); pn.position.set(0, RH + 0.45, -RD / 2 + 0.01); g.add(pn);
        for (let k = 0; k <= n; k++) box(0.03, 0.9, 0.03, mat('contFrame', { color: 0x8d9196, metalness: 0.6, roughness: 0.4 }), -L / 2 + k * RW, RH, -RD / 2 + 0.01, g);
        box(L, 0.03, 0.03, mat('contFrame', { color: 0x8d9196, metalness: 0.6, roughness: 0.4 }), 0, RH + 0.9, -RD / 2 + 0.01, g);
      }
      if (o.floor !== false) {
        const tileM = mat('floorTile', { color: 0xb9bcbf, roughness: 0.6, metalness: 0.2 });
        const perfM = mat('floorPerf', { color: 0xffffff, roughness: 0.5, metalness: 0.3, map: ltex('perftile', (x, W, H) => {
          x.fillStyle = '#b4b7ba'; x.fillRect(0, 0, W, H); x.fillStyle = '#2a2c2e';
          for (let j = 14; j < H - 10; j += 9) for (let k = 14; k < W - 10; k += 9) x.fillRect(k, j, 5, 5);
          x.strokeStyle = '#6e7174'; x.lineWidth = 4; x.strokeRect(2, 2, W - 4, H - 4); }, {}, [256, 256]) });
        const cols = Math.ceil(L / 0.6) + 1;
        for (let k = 0; k < cols; k++) for (let j = 0; j < 2; j++) {
          const perfd = j === 0 && k % 2 === 0;
          const t = box(0.598, 0.012, 0.598, perfd ? perfM : tileM, -cols * 0.3 + 0.3 + k * 0.6, 0, RD / 2 + 0.3 + j * 0.6, g);
        }
      }
      return centre(g);
    },
  });
}
