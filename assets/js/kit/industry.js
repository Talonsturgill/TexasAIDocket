/* kit/industry.js, see assets/js/txkit.js for the conventions.
 *
 * The industrial things Texas is made of: the hyperscale data hall and its generator yard (this
 * project's most frequent subject), the genset, mechanical and natural draft cooling towers, the
 * elevated water tank, the beam pumping unit, the tank battery, the tilt wall distribution
 * warehouse, the ISO container, the air cooled chiller and the server rack.
 *
 * Everything here is modelled from the real object's standard dimensions: a 40 ft ISO box is
 * 12.192 x 2.438 x 2.591 m, a 42U rack is 0.6 x 2.0 x 1.07 m with 44.45 mm units, a 400 bbl
 * stock tank is 12 ft across and 20 ft tall, a conventional pumping unit's horsehead arc is
 * centred on the saddle bearing so the bridle always hangs plumb over the well.
 *
 * LOCAL CONVENTIONS. Materials that carry a canvas texture are cached here by an explicit key,
 * never through K.mat, because K.mat keys its cache on JSON.stringify(params) and a Texture's
 * toJSON encodes its whole canvas to a data URL on every call. Lettering (the water tower's
 * town name) is drawn as stroked paths from a block font below, never with fillText, so no
 * art string is mistaken for slide copy by render.py's canvas text probe.
 */
export function install(K, THREE, TXT) {
  const TAU = Math.PI * 2, D2R = Math.PI / 180;
  const BEFORE = new Set(Object.keys(K.registry));
  const V3 = THREE.Vector3;
  const pick = (r, a) => a[Math.min(a.length - 1, Math.floor(r() * a.length))];
  const rr = (r, a, b) => a + (b - a) * r();

  /* ---- materials, cached by explicit key ------------------------------------------------ */
  const MAT = new Map();
  function lmat(key, make) { if (!MAT.has(key)) MAT.set(key, make()); return MAT.get(key); }
  function std(key, p) {
    return lmat('s|' + key, () => new THREE.MeshStandardMaterial(Object.assign({ roughness: 0.8, metalness: 0 }, p)));
  }
  const hex = (c) => (c >>> 0).toString(16);
  const paint = (c, rough, metal) => std('paint' + hex(c) + '|' + (rough || 0.5) + '|' + (metal != null ? metal : 0.3),
    { color: c, roughness: rough || 0.5, metalness: metal != null ? metal : 0.3 });
  const galv = () => std('galv', { color: 0xa9adb0, metalness: 0.85, roughness: 0.42 });
  const darkSteel = () => std('darksteel', { color: 0x2b2d30, metalness: 0.5, roughness: 0.55 });
  const blackPaint = () => std('blackpaint', { color: 0x1d1e20, metalness: 0.2, roughness: 0.6 });
  const rubber = () => std('rubber', { color: 0x1a1a1b, roughness: 0.78 });
  const chrome = () => std('chrome', { color: 0xdfe3e6, metalness: 1, roughness: 0.14 });
  const hole = () => std('hole', { color: 0x070808, roughness: 0.95 });
  const glass = (t) => lmat('glass' + hex(t || 0x2a3640), () => new THREE.MeshPhysicalMaterial({
    color: t || 0x2a3640, metalness: 0.15, roughness: 0.05, clearcoat: 1, clearcoatRoughness: 0.04,
    envMapIntensity: 1.5 }));
  const lamp = (c, i) => std('lamp' + hex(c) + '|' + i, { color: 0x111111, emissive: c, emissiveIntensity: i });
  const concrete = (c) => lmat('conc' + (c || ''), () => new THREE.MeshStandardMaterial({
    color: 0xffffff, roughness: 0.93, map: K.tex('concrete', { color: c || '#aaa69d' }) }));
  const gravel = () => lmat('gravel', () => new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1,
    map: ctex('gravel', 256, 256, paintGravel), bumpMap: ctex('gravelB', 256, 256, (x, w, h) => paintGravel(x, w, h, true), true),
    bumpScale: 2 }));
  const asphalt = () => lmat('asph', () => new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.92,
    map: ctex('asph', 256, 256, (x, w, h) => { x.fillStyle = '#3d3e40'; x.fillRect(0, 0, w, h); speckle(x, w, h, 7, 0.12); }) }));

  /* ---- canvas textures (painted once, cached, tileable) --------------------------------- */
  const TEX = new Map();
  function ctex(key, w, h, painter, data, clamp) {
    if (TEX.has(key)) return TEX.get(key);
    const c = document.createElement('canvas'); c.width = w; c.height = h;
    painter(c.getContext('2d'), w, h);
    const t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = clamp ? THREE.ClampToEdgeWrapping : THREE.RepeatWrapping;
    if (!data) t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 8;
    TEX.set(key, t);
    return t;
  }
  function rgb(c, k) {
    const f = (v) => Math.max(0, Math.min(255, Math.round(v * k)));
    return 'rgb(' + f((c >> 16) & 255) + ',' + f((c >> 8) & 255) + ',' + f(c & 255) + ')';
  }
  function speckle(x, w, h, seed, a) {
    const r = K.rng(seed), im = x.getImageData(0, 0, w, h), d = im.data;
    for (let i = 0; i < d.length; i += 4) { const k = 1 + (r() - 0.5) * 2 * a; d[i] *= k; d[i + 1] *= k; d[i + 2] *= k; }
    x.putImageData(im, 0, 0);
  }
  function paintGravel(x, w, h, bump) {
    const r = K.rng(311);
    x.fillStyle = bump ? '#444' : '#8e877b'; x.fillRect(0, 0, w, h);
    for (let i = 0; i < 2600; i++) {
      const px = r() * w, py = r() * h, s = 1.5 + r() * 3.5, k = 0.7 + r() * 0.5;
      x.fillStyle = bump ? rgb(0xffffff, 0.4 + r() * 0.6) : rgb(pick(r, [0x9b9385, 0xb3aa98, 0x7d766c, 0xa89d8a]), k);
      x.beginPath(); x.ellipse(px, py, s, s * (0.6 + r() * 0.4), r() * 3, 0, TAU); x.fill();
    }
  }
  /* LOUVRE: 5 blades per tile, tile = 0.5 m. Each blade's top lip catches the sky, its face
   * falls into the shadow of the blade above, and the gap between reads nearly black. */
  function louvreMat(c, key) {
    key = key || '';
    return lmat('louvre' + hex(c) + key, () => new THREE.MeshStandardMaterial({
      color: 0xffffff, roughness: 0.5, metalness: 0.45,
      map: ctex('louvreC' + hex(c), 128, 256, (x, w, h) => {
        const n = 5, p = h / n;
        for (let j = 0; j < n; j++) {
          const y = j * p, g = x.createLinearGradient(0, y, 0, y + p);
          g.addColorStop(0, rgb(c, 0.16)); g.addColorStop(0.16, rgb(c, 0.22)); g.addColorStop(0.2, rgb(c, 1.12));
          g.addColorStop(0.32, rgb(c, 0.98)); g.addColorStop(0.85, rgb(c, 0.66)); g.addColorStop(1, rgb(c, 0.42));
          x.fillStyle = g; x.fillRect(0, y, w, p);
        }
        speckle(x, w, h, 5, 0.04);
      }),
      bumpMap: ctex('louvreB', 128, 256, (x, w, h) => {
        const n = 5, p = h / n;
        for (let j = 0; j < n; j++) {
          const y = j * p, g = x.createLinearGradient(0, y, 0, y + p);
          g.addColorStop(0, '#000'); g.addColorStop(0.18, '#000'); g.addColorStop(0.21, '#fff'); g.addColorStop(1, '#555');
          x.fillStyle = g; x.fillRect(0, y, w, p);
        }
      }, true),
      bumpScale: 3 }));
  }
  /* INSULATED METAL PANEL: 1 m panels, a joint every metre, fine striations between. Tile 2 m. */
  function panelMat(c, horizontal) {
    return lmat('imp' + hex(c) + (horizontal ? 'h' : 'v'), () => {
      const paintIt = (x, w, h, bump) => {
        x.save();
        if (horizontal) { x.translate(w, 0); x.rotate(Math.PI / 2); }
        const r = K.rng(77);
        x.fillStyle = bump ? '#808080' : rgb(c, 1); x.fillRect(0, 0, w, h);
        for (let p = 0; p < 2; p++) {
          const x0 = p * w / 2;
          for (let s = 1; s < 12; s++) {                            // shallow striations
            x.fillStyle = bump ? 'rgba(255,255,255,0.35)' : 'rgba(255,255,255,0.06)';
            x.fillRect(x0 + s * w / 24, 0, 2, h);
          }
          if (!bump) { x.fillStyle = rgb(c, 0.95 + r() * 0.07); x.globalAlpha = 0.35; x.fillRect(x0 + 4, 0, w / 2 - 8, h); x.globalAlpha = 1; }
          x.fillStyle = bump ? '#000' : rgb(c, 0.55); x.fillRect(x0, 0, 3, h);   // the joint
          x.fillStyle = bump ? '#fff' : rgb(c, 1.08); x.fillRect(x0 + 3, 0, 2, h);
        }
        x.restore();
        if (!bump) speckle(x, w, h, 9, 0.025);
      };
      return new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.42, metalness: 0.35,
        map: ctex('impC' + hex(c) + horizontal, 256, 256, (x, w, h) => paintIt(x, w, h, false)),
        bumpMap: ctex('impB' + horizontal, 256, 256, (x, w, h) => paintIt(x, w, h, true), true), bumpScale: 1.2 });
    });
  }
  /* CONDENSER COIL: aluminium fins over copper, a fine vertical grain; tile 0.25 m. */
  function coilMat() {
    return lmat('coil', () => new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.45, metalness: 0.6,
      map: ctex('coilC', 128, 128, (x, w, h) => {
        x.fillStyle = '#7f878b'; x.fillRect(0, 0, w, h);
        for (let i = 0; i < w; i += 2) { x.fillStyle = i % 4 ? '#aab1b4' : '#5a6064'; x.fillRect(i, 0, 1, h); }
        for (let j = 0; j < h; j += 16) { x.fillStyle = 'rgba(150,90,60,0.35)'; x.fillRect(0, j + 7, w, 2); }
      }) }));
  }
  /* FAN GUARD: concentric wire rings and eight spokes, alpha tested. */
  function guardMat() {
    return lmat('guard', () => new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.4, metalness: 0.7,
      side: THREE.DoubleSide, alphaTest: 0.35,
      map: ctex('guardC', 256, 256, (x, w, h) => {
        x.clearRect(0, 0, w, h); x.strokeStyle = '#b7bbbd'; x.lineWidth = 2.6;
        for (let rad = 14; rad < 126; rad += 9.5) { x.beginPath(); x.arc(128, 128, rad, 0, TAU); x.stroke(); }
        x.lineWidth = 4;
        for (let s = 0; s < 8; s++) { const a = s * TAU / 8; x.beginPath(); x.moveTo(128, 128);
          x.lineTo(128 + Math.cos(a) * 126, 128 + Math.sin(a) * 126); x.stroke(); }
        x.beginPath(); x.arc(128, 128, 125, 0, TAU); x.lineWidth = 5; x.stroke();
        x.fillStyle = '#9a9ea0'; x.beginPath(); x.arc(128, 128, 16, 0, TAU); x.fill();
      }, false, true) }));
  }
  /* CHAIN LINK: 50 mm diamonds, galvanized wire. Mipmapped alpha fades to the grey veil a real
   * fence is at distance; it casts no shadow of its own (a solid slab of shadow would lie). */
  function chainMat() {
    return lmat('chain', () => new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.45, metalness: 0.7,
      side: THREE.DoubleSide, transparent: true, depthWrite: false,
      map: ctex('chainC', 128, 128, (x, w, h) => {
        x.clearRect(0, 0, w, h); x.strokeStyle = 'rgba(190,195,198,0.95)'; x.lineWidth = 3.2;
        const n = 4, s = w / n;
        for (let i = -n; i <= 2 * n; i++) {
          x.beginPath(); x.moveTo(i * s, 0); x.lineTo(i * s + h, h); x.stroke();
          x.beginPath(); x.moveTo(i * s, 0); x.lineTo(i * s - h, h); x.stroke();
        }
      }) }));
  }
  const noShadow = lmat('noShadowDepth', () => new THREE.MeshDepthMaterial({ alphaTest: 2 }));
  /* SECTIONAL OVERHEAD DOOR: one door per 0..1 UV, five ribbed panels. */
  function sectionalMat(c) {
    return lmat('sect' + hex(c), () => new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.5, metalness: 0.3,
      map: ctex('sectC' + hex(c), 256, 256, (x, w, h) => {
        x.fillStyle = rgb(c, 1); x.fillRect(0, 0, w, h);
        const n = 5, p = h / n;
        for (let j = 0; j < n; j++) {
          const g = x.createLinearGradient(0, j * p, 0, j * p + p);
          g.addColorStop(0, rgb(c, 0.7)); g.addColorStop(0.06, rgb(c, 1.05)); g.addColorStop(0.5, rgb(c, 0.97)); g.addColorStop(1, rgb(c, 0.88));
          x.fillStyle = g; x.fillRect(0, j * p, w, p);
          x.fillStyle = rgb(c, 0.92); x.fillRect(0, j * p + p * 0.48, w, 2);
        }
        x.fillStyle = rgb(c, 0.6); x.fillRect(0, 0, 3, h); x.fillRect(w - 3, 0, 3, h);
        speckle(x, w, h, 13, 0.03);
      }) }));
  }

  /* ---- geometry helpers ------------------------------------------------------------------ */
  function grp(parent) { const g = new THREE.Group(); if (parent) parent.add(g); return g; }
  // centred box with optional Euler rotation
  function cbox(w, h, d, mat, x, y, z, parent, rot) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
    m.position.set(x || 0, y || 0, z || 0);
    if (rot) m.rotation.set(rot[0] || 0, rot[1] || 0, rot[2] || 0);
    if (parent) parent.add(m);
    return m;
  }
  // box standing on y0; metres => UVs in metres for a tiled map; bevel => rounded edges
  function tbox(w, h, d, mat, x, y0, z, parent, metres, bevel) {
    const m = K.box(w, h, d, mat, x, y0, z, bevel, parent);
    if (metres) K.uvBox(m.geometry, metres);
    return m;
  }
  function cyl(rt, rb, h, mat, x, y0, z, seg, parent, open) {
    const m = new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, seg || 20, 1, !!open), mat);
    m.position.set(x || 0, (y0 || 0) + h / 2, z || 0);
    if (parent) parent.add(m);
    return m;
  }
  // horizontal cylinder, centred, along 'x' or 'z'
  function hcyl(r, len, mat, x, y, z, axis, seg, parent, open) {
    const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, len, seg || 20, 1, !!open), mat);
    m.position.set(x, y, z);
    if (axis === 'z') m.rotation.x = Math.PI / 2; else m.rotation.z = Math.PI / 2;
    if (parent) parent.add(m);
    return m;
  }
  function bar(a, b, r, mat, parent, seg) { return K.bar(a, b, r, mat, seg || 8, parent); }
  // square section member between two points (structural steel), cross section w x t
  function sbar(a, b, w, t, mat, parent, roll) {
    const A = new V3(a[0], a[1], a[2]), B = new V3(b[0], b[1], b[2]), L = A.distanceTo(B);
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, L, t), mat);
    m.position.copy(A).add(B).multiplyScalar(0.5);
    m.quaternion.setFromUnitVectors(new V3(0, 1, 0), B.clone().sub(A).normalize());
    if (roll) m.rotateY(roll);
    if (parent) parent.add(m);
    return m;
  }
  // a pipe run along a polyline with an elbow ball at every bend
  function pipe(pts, r, mat, parent, low) {
    for (let i = 0; i < pts.length - 1; i++) bar(pts[i], pts[i + 1], r, mat, parent, low ? 8 : 12);
    for (let i = 1; i < pts.length - 1; i++) {
      const s = new THREE.Mesh(new THREE.SphereGeometry(r * 1.08, low ? 8 : 12, low ? 5 : 8), mat);
      s.position.set(pts[i][0], pts[i][1], pts[i][2]); parent.add(s);
    }
  }
  // flange: a short fat disc on a pipe axis
  function flange(r, x, y, z, axis, mat, parent) {
    const f = hcyl(r, 0.04, mat, x, y, z, axis, 16, parent);
    if (axis === 'y') { f.rotation.set(0, 0, 0); }
    return f;
  }
  // a gate valve: body, bonnet and handwheel, on a horizontal pipe along `axis`
  function valve(r, x, y, z, axis, mat, wheelMat, parent) {
    const g = grp(parent); g.position.set(x, y, z);
    if (axis === 'z') g.rotation.y = Math.PI / 2;
    hcyl(r * 1.5, r * 3, mat, 0, 0, 0, 'x', 16, g);
    flange(r * 1.9, -r * 1.6, 0, 0, 'x', mat, g); flange(r * 1.9, r * 1.6, 0, 0, 'x', mat, g);
    cyl(r * 0.9, r * 1.2, r * 3, mat, 0, r * 1.2, 0, 12, g);
    cyl(r * 0.18, r * 0.18, r * 2, galv(), 0, r * 4, 0, 8, g);
    const w = new THREE.Mesh(new THREE.TorusGeometry(r * 1.5, r * 0.16, 6, 20), wheelMat || mat);
    w.rotation.x = Math.PI / 2; w.position.y = r * 5.4; g.add(w);
    return g;
  }
  // a guard rail along a polyline: posts at most `sp` apart, a top and a knee rail
  function railing(parent, pts, h, mat, sp, r) {
    sp = sp || 1.8; r = r || 0.022;
    for (let i = 0; i < pts.length - 1; i++) {
      const a = pts[i], b = pts[i + 1];
      const L = Math.hypot(b[0] - a[0], b[2] - a[2]), n = Math.max(1, Math.ceil(L / sp));
      for (let k = 0; k <= n; k++) {
        if (k === 0 && i > 0) continue;
        const t = k / n, x = a[0] + (b[0] - a[0]) * t, y = a[1] + (b[1] - a[1]) * t, z = a[2] + (b[2] - a[2]) * t;
        bar([x, y, z], [x, y + h, z], r, mat, parent, 6);
      }
      bar([a[0], a[1] + h, a[2]], [b[0], b[1] + h, b[2]], r, mat, parent, 6);
      bar([a[0], a[1] + h * 0.5, a[2]], [b[0], b[1] + h * 0.5, b[2]], r * 0.8, mat, parent, 6);
    }
  }
  // a straight stair flight from bottom point to top point, `wd` wide, with rails both sides
  function stair(parent, a, b, wd, mat, treadMat) {
    const dx = b[0] - a[0], dz = b[2] - a[2], run = Math.hypot(dx, dz), rise = b[1] - a[1];
    const ux = dx / run, uz = dz / run, nx = -uz, nz = ux, ang = -Math.atan2(dz, dx);
    const n = Math.max(2, Math.round(rise / 0.19));
    for (const s of [-1, 1]) {
      const ox = nx * s * wd / 2, oz = nz * s * wd / 2;
      sbar([a[0] + ox, a[1] - 0.1, a[2] + oz], [b[0] + ox, b[1] - 0.1, b[2] + oz], 0.02, 0.24, mat, parent);
      bar([a[0] + ox, a[1] + 0.95, a[2] + oz], [b[0] + ox, b[1] + 0.95, b[2] + oz], 0.02, mat, parent, 6);
      bar([a[0] + ox, a[1] + 0.5, a[2] + oz], [b[0] + ox, b[1] + 0.5, b[2] + oz], 0.016, mat, parent, 6);
      const posts = Math.max(2, Math.ceil(Math.hypot(run, rise) / 1.6));
      for (let k = 0; k <= posts; k++) {
        const t = k / posts, x = a[0] + dx * t + ox, y = a[1] + rise * t, z = a[2] + dz * t + oz;
        bar([x, y - 0.1, z], [x, y + 0.95, z], 0.02, mat, parent, 6);
      }
    }
    for (let i = 0; i < n; i++) {
      const t = (i + 0.5) / n;
      cbox(run / n + 0.03, 0.035, wd - 0.05, treadMat || mat, a[0] + dx * t, a[1] + rise * (i + 1) / n - 0.02, a[2] + dz * t, parent, [0, ang, 0]);
    }
  }
  // a caged ladder up the face of something, rungs every 0.3 m, facing +z from x, z
  function ladder(parent, x, y0, y1, z, mat, cage, rotY) {
    const g = grp(parent); g.position.set(x, 0, z); g.rotation.y = rotY || 0;
    bar([-0.22, y0, 0.18], [-0.22, y1 + 1.1, 0.18], 0.025, mat, g, 6);
    bar([0.22, y0, 0.18], [0.22, y1 + 1.1, 0.18], 0.025, mat, g, 6);
    for (let y = y0 + 0.3; y < y1; y += 0.3) bar([-0.22, y, 0.18], [0.22, y, 0.18], 0.013, mat, g, 5);
    for (let y = y0 + 0.6; y < y1; y += 1.5) { bar([-0.22, y, 0.18], [-0.22, y, 0.02], 0.015, mat, g, 5); bar([0.22, y, 0.18], [0.22, y, 0.02], 0.015, mat, g, 5); }
    if (cage && y1 - y0 > 3) {
      for (let y = y0 + 2.3; y <= y1 + 1.0; y += 0.9) {
        const hoop = new THREE.Mesh(new THREE.TorusGeometry(0.36, 0.012, 4, 16, Math.PI), mat);
        hoop.rotation.x = -Math.PI / 2; hoop.rotation.z = Math.PI; hoop.position.set(0, y, 0.18); hoop.scale.set(1, 1.1, 1); g.add(hoop);
      }
      for (let k = 0; k < 5; k++) { const a = Math.PI * (k + 0.5) / 5;
        bar([Math.cos(a) * 0.36, y0 + 2.3, 0.18 + Math.sin(a) * 0.4], [Math.cos(a) * 0.36, y1 + 1.0, 0.18 + Math.sin(a) * 0.4], 0.01, mat, g, 4); }
    }
    return g;
  }

  /* ---- merging: one mesh per material, so a hero costs a handful of draw calls --------- */
  function collect(root) {
    root.updateMatrixWorld(true);
    const inv = new THREE.Matrix4().copy(root.matrixWorld).invert(), parts = [], keep = [];
    root.traverse((o) => {
      if (!o.isMesh) return;
      if (o.isInstancedMesh || o.userData.keep) { keep.push(o); return; }
      let g = o.geometry.index ? o.geometry.toNonIndexed() : o.geometry.clone();
      g.applyMatrix4(new THREE.Matrix4().multiplyMatrices(inv, o.matrixWorld));
      parts.push({ mat: o.material, geo: g });
    });
    return { parts, keep };
  }
  function emit(parts, out) {
    const by = new Map();
    parts.forEach((p) => { if (!by.has(p.mat)) by.set(p.mat, []); by.get(p.mat).push(p.geo); });
    for (const [mat, geos] of by) {
      let n = 0; geos.forEach((g) => { n += g.attributes.position.count; });
      const pos = new Float32Array(n * 3), nor = new Float32Array(n * 3), uv = new Float32Array(n * 2);
      let o = 0;
      geos.forEach((g) => {
        if (!g.attributes.normal) g.computeVertexNormals();
        pos.set(g.attributes.position.array, o * 3); nor.set(g.attributes.normal.array, o * 3);
        if (g.attributes.uv) uv.set(g.attributes.uv.array, o * 2);
        o += g.attributes.position.count; g.dispose();
      });
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
      geo.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
      geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
      geo.computeBoundingSphere(); geo.computeBoundingBox();
      const m = new THREE.Mesh(geo, mat);
      if (mat === chainMat()) m.customDepthMaterial = noShadow;
      out.add(m);
    }
    return out;
  }
  // bake a freshly built group (identity transform) into one mesh per material
  function bake(root) {
    const { parts, keep } = collect(root), out = new THREE.Group();
    emit(parts, out);
    keep.forEach((o) => { o.updateMatrixWorld(true); o.matrixWorld.decompose(o.position, o.quaternion, o.scale); out.add(o); });
    return out;
  }
  // stamp copies of a template group's parts at [x, y, z, rotY] placements into a parts list
  function stamp(tpl, places, into) {
    const { parts } = collect(tpl), M = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), one = new V3(1, 1, 1);
    places.forEach((p) => {
      e.set(0, p[3] || 0, 0); q.setFromEuler(e); M.compose(new V3(p[0], p[1], p[2]), q, one);
      parts.forEach((pt) => into.push({ mat: pt.mat, geo: pt.geo.clone().applyMatrix4(M) }));
    });
    parts.forEach((pt) => pt.geo.dispose());
    return into;
  }

  /* Instanced copies of a template: one InstancedMesh per material, far cheaper to build than a
   * stamp for a yard or a roof of identical units. Instances are not grimed by TXT.weather. */
  function instanced(tpl, places, out) {
    const g = bake(tpl), M = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), one = new V3(1, 1, 1);
    g.children.forEach((m) => {
      const im = new THREE.InstancedMesh(m.geometry, m.material, places.length);
      places.forEach((p, i) => { e.set(0, p[3] || 0, 0); q.setFromEuler(e); M.compose(new V3(p[0], p[1], p[2]), q, one); im.setMatrixAt(i, M); });
      im.instanceMatrix.needsUpdate = true; im.computeBoundingSphere(); im.computeBoundingBox();
      if (m.customDepthMaterial) im.customDepthMaterial = m.customDepthMaterial;
      out.add(im);
    });
    return out;
  }

  /* ---- a stroked block font, so lettering is geometry of the art and not canvas text ----- */
  const GLYPH = {
    A: [[[0, 6], [0, 1.6], [1.4, 0], [2.6, 0], [4, 1.6], [4, 6]], [[0, 3.6], [4, 3.6]]],
    B: [[[0, 3], [3, 3], [4, 4], [4, 5], [3, 6], [0, 6], [0, 0], [2.8, 0], [3.8, 0.9], [3.8, 2.1], [3, 3]]],
    C: [[[4, 1.2], [3, 0], [1, 0], [0, 1], [0, 5], [1, 6], [3, 6], [4, 4.8]]],
    D: [[[0, 0], [0, 6], [2.6, 6], [4, 4.6], [4, 1.4], [2.6, 0], [0, 0]]],
    E: [[[4, 0], [0, 0], [0, 6], [4, 6]], [[0, 3], [3.2, 3]]],
    F: [[[4, 0], [0, 0], [0, 6]], [[0, 3], [3.2, 3]]],
    G: [[[4, 1.2], [3, 0], [1, 0], [0, 1], [0, 5], [1, 6], [3, 6], [4, 5], [4, 3.3], [2.2, 3.3]]],
    H: [[[0, 0], [0, 6]], [[4, 0], [4, 6]], [[0, 3], [4, 3]]],
    I: [[[2, 0], [2, 6]], [[0.9, 0], [3.1, 0]], [[0.9, 6], [3.1, 6]]],
    J: [[[4, 0], [4, 5], [3, 6], [1, 6], [0, 5]]],
    K: [[[0, 0], [0, 6]], [[4, 0], [0, 3.6]], [[1.4, 2.4], [4, 6]]],
    L: [[[0, 0], [0, 6], [4, 6]]],
    M: [[[0, 6], [0, 0], [2, 3.2], [4, 0], [4, 6]]],
    N: [[[0, 6], [0, 0], [4, 6], [4, 0]]],
    O: [[[1, 0], [3, 0], [4, 1], [4, 5], [3, 6], [1, 6], [0, 5], [0, 1], [1, 0]]],
    P: [[[0, 6], [0, 0], [3, 0], [4, 1], [4, 2.2], [3, 3.2], [0, 3.2]]],
    Q: [[[1, 0], [3, 0], [4, 1], [4, 5], [3, 6], [1, 6], [0, 5], [0, 1], [1, 0]], [[2.4, 4.3], [4.2, 6.2]]],
    R: [[[0, 6], [0, 0], [3, 0], [4, 1], [4, 2.2], [3, 3.2], [0, 3.2]], [[2, 3.2], [4, 6]]],
    S: [[[4, 1], [3, 0], [1, 0], [0, 1], [0, 2], [1, 3], [3, 3], [4, 4], [4, 5], [3, 6], [1, 6], [0, 5]]],
    T: [[[0, 0], [4, 0]], [[2, 0], [2, 6]]],
    U: [[[0, 0], [0, 5], [1, 6], [3, 6], [4, 5], [4, 0]]],
    V: [[[0, 0], [2, 6], [4, 0]]],
    W: [[[0, 0], [0.9, 6], [2, 2.4], [3.1, 6], [4, 0]]],
    X: [[[0, 0], [4, 6]], [[4, 0], [0, 6]]],
    Y: [[[0, 0], [2, 3], [4, 0]], [[2, 3], [2, 6]]],
    Z: [[[0, 0], [4, 0], [0, 6], [4, 6]]],
    '-': [[[0.8, 3], [3.2, 3]]], '.': [[[1.8, 5.8], [2.2, 5.8]]],
  };
  // draw `txt` centred at (cx, cy) with cap height `ch` px
  function strokeText(x, txt, cx, cy, ch, color, weight) {
    const u = ch / 6, adv = 5.6 * u, sp = 3.2 * u;
    let wdt = 0; for (const c of txt) wdt += c === ' ' ? sp : adv; wdt -= 1.6 * u;
    let px = cx - wdt / 2;
    x.strokeStyle = color; x.lineWidth = u * (weight || 1.25); x.lineCap = 'square'; x.lineJoin = 'miter';
    for (const c of txt.toUpperCase()) {
      const g = GLYPH[c];
      if (g) for (const line of g) { x.beginPath(); line.forEach((p, i) => (i ? x.lineTo : x.moveTo).call(x, px + p[0] * u, cy - ch / 2 + p[1] * u)); x.stroke(); }
      px += c === ' ' ? sp : adv;
    }
    return wdt;
  }
  function starPath(x, cx, cy, R) {
    x.beginPath();
    for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rad = i % 2 ? R * 0.382 : R;
      x.lineTo(cx + Math.cos(a) * rad, cy + Math.sin(a) * rad); }
    x.closePath();
  }

  /* ---- shared parts ---------------------------------------------------------------------- */
  // An axial condenser fan as seen from above: shroud ring, guard, hub and five blades. Top at y = h.
  function fanUnit(parent, x, y0, z, rad, h, shroudMat, low) {
    const g = grp(parent); g.position.set(x, y0, z);
    const seg = low ? 16 : 28;
    cyl(rad + 0.03, rad + 0.03, h, shroudMat, 0, 0, 0, seg, g, true);
    if (!low) { const lip = new THREE.Mesh(new THREE.TorusGeometry(rad + 0.04, 0.035, 4, seg), shroudMat);
      lip.rotation.x = Math.PI / 2; lip.position.y = h; g.add(lip); }
    const th = new THREE.Mesh(new THREE.CircleGeometry(rad, seg), hole()); th.rotation.x = -Math.PI / 2; th.position.y = 0.03; g.add(th);
    cyl(rad * 0.16, rad * 0.2, 0.18, darkSteel(), 0, h * 0.35, 0, low ? 8 : 14, g, low);
    for (let b = 0; b < (low ? 4 : 5); b++) {
      const bl = cbox(rad * 0.78, 0.012, rad * 0.3, std('fanblade', { color: 0x3b3e40, metalness: 0.4, roughness: 0.5 }), 0, h * 0.42, 0, g);
      bl.geometry.translate(rad * 0.52, 0, 0);
      bl.rotation.set(0, b * TAU / 5, 0); bl.rotateX(0.32);
    }
    const guard = new THREE.Mesh(new THREE.CircleGeometry(rad + 0.02, seg), guardMat());
    guard.rotation.x = -Math.PI / 2; guard.position.y = h + 0.02; g.add(guard);
    return g;
  }
  // a chain link fence run from a to b (x, z), height h, with barbed outriggers
  function fenceRun(parent, a, b, h, barbed) {
    const post = galv(), L = Math.hypot(b[0] - a[0], b[1] - a[1]), n = Math.max(1, Math.ceil(L / 3.05));
    const ux = (b[0] - a[0]) / L, uz = (b[1] - a[1]) / L;
    for (let k = 0; k <= n; k++) {
      const x = a[0] + (b[0] - a[0]) * k / n, z = a[1] + (b[1] - a[1]) * k / n;
      const end = k === 0 || k === n;
      cyl(end ? 0.05 : 0.036, end ? 0.05 : 0.036, h, post, x, 0, z, 8, parent);
      cyl(0.09, 0.13, 0.08, concrete(), x, 0, z, 8, parent);
      if (barbed) bar([x, h, z], [x - uz * 0.4, h + 0.4, z + ux * 0.4], 0.018, post, parent, 5);
    }
    bar([a[0], h - 0.03, a[1]], [b[0], h - 0.03, b[1]], 0.021, post, parent, 6);
    bar([a[0], 0.08, a[1]], [b[0], 0.08, b[1]], 0.01, post, parent, 4);
    const fab = new THREE.Mesh(new THREE.PlaneGeometry(L, h - 0.05), chainMat());
    fab.position.set((a[0] + b[0]) / 2, (h - 0.05) / 2 + 0.03, (a[1] + b[1]) / 2);
    fab.rotation.y = -Math.atan2(uz, ux);
    const uv = fab.geometry.attributes.uv;
    for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * L / 0.2, uv.getY(i) * (h - 0.05) / 0.2);
    parent.add(fab);
    if (barbed) for (let s = 1; s <= 3; s++) {
      const off = s * 0.13;
      bar([a[0] - uz * off, h + off, a[1] + ux * off], [b[0] - uz * off, h + off, b[1] + ux * off], 0.006, post, parent, 3);
    }
  }
  // a 53 ft dry van trailer, nose at -z, doors at +z, body 16.15 x 2.6 x 4.1 m
  function trailer(parent, x, z, rotY, c, r) {
    const g = grp(parent); g.position.set(x, 0, z); g.rotation.y = rotY || 0;
    const body = paint(c, 0.45, 0.2), L = 16.15, W = 2.59;
    tbox(W, 2.85, L, body, 0, 1.2, 0, g, 0, 0.04);
    for (let k = -L / 2 + 0.4; k < L / 2; k += 0.62) {           // the side posts
      cbox(0.02, 2.8, 0.06, body, W / 2 + 0.01, 2.62, k, g); cbox(0.02, 2.8, 0.06, body, -W / 2 - 0.01, 2.62, k, g);
    }
    cbox(W + 0.04, 0.12, L, galv(), 0, 1.2, 0, g);                         // bottom rail
    cbox(W + 0.04, 0.08, L, galv(), 0, 4.03, 0, g);                        // top rail
    cbox(W - 0.1, 0.18, L - 2, darkSteel(), 0, 1.02, 0, g);                // crossmembers
    // tandem axles at the rear, landing gear forward
    for (const az of [L / 2 - 2.2, L / 2 - 3.45]) for (const s of [-1, 1]) {
      const t = hcyl(0.5, 0.56, rubber(), s * 0.82, 0.5, az, 'x', 20, g);
      hcyl(0.28, 0.58, galv(), s * 0.82, 0.5, az, 'x', 14, g);
    }
    cbox(W - 0.2, 0.25, 4.2, darkSteel(), 0, 0.95, L / 2 - 2.8, g);
    for (const s of [-1, 1]) { cbox(0.1, 1.0, 0.1, galv(), s * 0.8, 0.55, -L / 2 + 3.6, g); cbox(0.3, 0.05, 0.3, galv(), s * 0.8, 0.04, -L / 2 + 3.6, g); }
    cbox(W, 0.3, 0.1, std('bumper', { color: 0x222222, metalness: 0.4, roughness: 0.5 }), 0, 0.95, L / 2 + 0.1, g);
    for (const s of [-1, 1]) cbox(0.08, 0.08, 0.02, lamp(0xff2a10, 1.2), s * 1.0, 1.0, L / 2 + 0.16, g);
    return g;
  }

  /* ======================================================================================
   * SHIPPING CONTAINER. 40 ft ISO dry box, 12.192 x 2.591 x 2.438 m (high cube 2.896).
   * Length runs along z with the cargo doors on +z, the end a reader recognises.
   * ==================================================================================== */
  const CONTAINER_COLOURS = [0x1f5f8b, 0x8a3324, 0x2e5a3c, 0x7a7d80, 0xc2571d, 0x9e2b25, 0x2a3f6b, 0xd9d4c7, 0x6a3b2a, 0x3f6e7a];
  // corrugated wall: a trapezoid profile along `len`, height h, in the xy plane facing +z
  function corrugated(len, h, pitch, depth, mat, flat) {
    const n = Math.max(1, Math.round(len / pitch)), p = len / n, prof = [];
    const f = flat || 0.26;
    for (let i = 0; i < n; i++) {
      const x0 = -len / 2 + i * p;
      prof.push([x0, 0], [x0 + p * f, 0], [x0 + p * 0.5 - p * 0.02, depth], [x0 + p * (0.5 + f) - p * 0.02, depth], [x0 + p - p * 0.04, 0]);
    }
    prof.push([len / 2, 0]);
    const P = [], U = [];
    for (let i = 0; i < prof.length - 1; i++) {
      const a = prof[i], b = prof[i + 1];
      P.push(a[0], 0, a[1], b[0], 0, b[1], b[0], h, b[1], a[0], 0, a[1], b[0], h, b[1], a[0], h, a[1]);
      U.push(a[0], 0, b[0], 0, b[0], h, a[0], 0, b[0], h, a[0], h);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(U, 2));
    g.computeVertexNormals();
    return new THREE.Mesh(g, mat);
  }
  K.define('shipping_container', {
    size: [2.44, 2.59, 12.3],
    options: { color: null, highCube: false, doorsOpen: false, rust: 0.5 },
    note: '40 ft ISO dry container, corrugated walls, corner castings, cargo doors with four locking bars on +z. Seeded paint.',
    make(o, r) {
      const root = new THREE.Group();
      const c = o.color != null ? o.color : pick(r, CONTAINER_COLOURS);
      const L = 12.192, W = 2.438, H = o.highCube ? 2.896 : 2.591;
      const body = paint(c, 0.62, 0.25), frame = paint(c, 0.55, 0.3);
      const rustM = std('ctrust', { color: 0x5c3a22, roughness: 0.9 });
      // side walls: vertical trapezoid corrugation, pitch 0.278 m, 36 mm deep
      const side = corrugated(L - 0.3, H - 0.3, 0.278, 0.036, body);
      for (const s of [-1, 1]) {
        const m = side.clone(); m.rotation.y = s * Math.PI / 2; m.position.set(s * (W / 2 - 0.05), 0.16, 0);
        if (s < 0) m.rotation.y = -Math.PI / 2;
        root.add(m);
      }
      // front (blind) end, corrugated, at -z facing -z
      const fe = corrugated(W - 0.3, H - 0.3, 0.3, 0.05, body); fe.rotation.y = Math.PI; fe.position.set(0, 0.16, -L / 2 + 0.08); root.add(fe);
      // roof: shallow transverse dimples, a slab and a lip
      tbox(W - 0.12, 0.03, L - 0.2, body, 0, H - 0.08, 0, root);
      for (let z = -L / 2 + 0.4; z < L / 2 - 0.3; z += 0.46) cbox(W - 0.3, 0.012, 0.18, body, 0, H - 0.045, z, root);
      // floor and cross members
      tbox(W - 0.1, 0.16, L - 0.1, darkSteel(), 0, 0.0, 0, root);
      // the frame: corner posts, top and bottom side rails, end rails
      for (const sx of [-1, 1]) for (const sz of [-1, 1]) tbox(0.15, H - 0.2, 0.15, frame, sx * (W / 2 - 0.075), 0.1, sz * (L / 2 - 0.075), root, 0, 0.01);
      for (const sx of [-1, 1]) {
        tbox(0.1, 0.16, L - 0.3, frame, sx * (W / 2 - 0.05), H - 0.16, 0, root, 0, 0.01);
        tbox(0.12, 0.18, L - 0.3, frame, sx * (W / 2 - 0.06), 0.02, 0, root, 0, 0.01);
      }
      for (const sz of [-1, 1]) { tbox(W - 0.2, 0.18, 0.14, frame, 0, H - 0.18, sz * (L / 2 - 0.07), root, 0, 0.01);
        tbox(W - 0.2, 0.2, 0.14, frame, 0, 0.02, sz * (L / 2 - 0.07), root, 0, 0.01); }
      // forklift-free: gooseneck tunnel hint and corner castings with their oval holes
      const cast = std('casting', { color: 0x2d2e30, metalness: 0.5, roughness: 0.6 });
      for (const sx of [-1, 1]) for (const sz of [-1, 1]) for (const y of [0, H - 0.118]) {
        tbox(0.178, 0.118, 0.162, cast, sx * (W / 2 - 0.089), y, sz * (L / 2 - 0.081), root, 0, 0.008);
        const hol = new THREE.Mesh(new THREE.CircleGeometry(0.03, 12), hole()); hol.scale.set(1.9, 1, 1);
        hol.position.set(sx * (W / 2 + 0.001), y + 0.06, sz * (L / 2 - 0.081)); hol.rotation.y = sx * Math.PI / 2; root.add(hol);
        const h2 = hol.clone(); h2.rotation.y = 0; h2.position.set(sx * (W / 2 - 0.089), y + 0.06, sz * (L / 2 + 0.001));
        if (sz < 0) h2.rotation.y = Math.PI; root.add(h2);
      }
      // cargo doors at +z: two leaves, horizontal door corrugation, 4 locking bars with cams and handles
      const dz = L / 2 - 0.01, doorH = H - 0.4, leafW = (W - 0.3) / 2;
      for (const s of [-1, 1]) {
        const leaf = grp(root);
        const hingeX = s * (W / 2 - 0.15);
        leaf.position.set(hingeX, 0.2, dz);
        const open = o.doorsOpen ? s * 1.75 : 0;
        leaf.rotation.y = open;
        const cx = -s * leafW / 2;
        tbox(leafW, doorH, 0.04, frame, cx, 0, 0, leaf, 0, 0.012);
        for (let k = 0; k < 5; k++) {
          const y = 0.25 + k * (doorH - 0.5) / 4;
          cbox(leafW - 0.16, 0.2, 0.03, body, cx, y, 0.03, leaf, [0.0, 0, 0]);
        }
        for (const bx of [0.3, 0.8]) {                                   // two locking bars per leaf
          const px = cx + (-s) * (bx - leafW / 2) * -1;
          const lx = -s * bx;
          bar([lx, -0.02, 0.08], [lx, doorH + 0.02, 0.08], 0.017, galv(), leaf, 8);
          for (const y of [0.35, doorH - 0.35]) cbox(0.08, 0.1, 0.05, galv(), lx, y, 0.06, leaf);
          cbox(0.06, 0.06, 0.08, galv(), lx, -0.05, 0.06, leaf); cbox(0.06, 0.06, 0.08, galv(), lx, doorH + 0.05, 0.06, leaf);
          // handle, lying flat against the door at 1.1 m, swung toward the leaf's centre
          bar([lx, 1.05, 0.09], [lx + s * 0.34 * -1, 1.05, 0.11], 0.012, galv(), leaf, 6);
          cbox(0.05, 0.1, 0.04, galv(), lx + s * -0.34, 1.05, 0.1, leaf);
        }
        for (const y of [0.2, doorH * 0.5, doorH - 0.2]) hcyl(0.03, 0.14, galv(), -s * 0.02, y, 0.03, 'y', 8, leaf);
        // gasket shadow line
        cbox(0.02, doorH, 0.02, rubber(), -s * (leafW - 0.01), doorH / 2, 0.01, leaf);
      }
      // door header: the CSC plate and a little rust at the sill
      cbox(0.24, 0.13, 0.01, std('cscplate', { color: 0xb8b6ad, metalness: 0.6, roughness: 0.4 }), -0.55, 1.6, dz + 0.06, root);
      if (o.rust > 0) {
        const nR = Math.floor(4 + o.rust * 10);
        for (let i = 0; i < nR; i++) {
          const zz = rr(r, -L / 2 + 0.3, L / 2 - 0.3), s = r() < 0.5 ? -1 : 1, w = rr(r, 0.08, 0.5) * o.rust;
          const m = new THREE.Mesh(new THREE.PlaneGeometry(w, rr(r, 0.03, 0.12)), rustM);
          m.position.set(s * (W / 2 + 0.002), rr(r, 0.2, 0.28), zz); m.rotation.y = s * Math.PI / 2; root.add(m);
          if (r() < 0.5) { const st = new THREE.Mesh(new THREE.PlaneGeometry(0.02, rr(r, 0.2, 0.9)), rustM);
            st.position.set(s * (W / 2 + 0.003), H - 0.4 - rr(r, 0, 0.3), zz); st.rotation.y = s * Math.PI / 2; root.add(st); }
        }
      }
      if (o.doorsOpen) tbox(W - 0.3, H - 0.4, 0.02, hole(), 0, 0.2, dz - 0.3, root);
      return bake(root);
    },
  });

  /* ======================================================================================
   * GENSET. A containerised 2 to 3 MW diesel generator: a sound attenuated enclosure on a
   * double wall belly tank, radiator discharge louvres on +x, intake louvres and personnel doors
   * down both long sides, a residential silencer and a stack with a rain cap on the roof.
   * ==================================================================================== */
  const GENSET_COLOURS = [0xe8e6df, 0xdcd9d0, 0xc8ccce, 0xe0d6bd, 0xd4a82a, 0xb9bdbd];
  function buildGenset(o, r) {
    const root = new THREE.Group(), low = o.lod === 'low';
    const col = o.color != null ? o.color : pick(r, GENSET_COLOURS);
    const skin = paint(col, 0.42, 0.28), trim = paint(col === 0xd4a82a ? 0x2a2a2a : col, 0.5, 0.28);
    const tankCol = r() < 0.55 ? col : 0x34373a, tank = paint(tankCol, 0.55, 0.3);
    const L = 12.2, W = 2.9, TK = 1.25, EH = 3.05, pad = o.pad ? 0.2 : 0;
    const bv = (v) => (low ? 0 : v), SG = low ? 12 : 28;
    const y1 = pad + TK, y2 = y1 + EH;
    if (o.pad) tbox(L + 1.4, pad, W + 1.4, concrete(), 0, 0, 0, root, 3);
    // the belly tank, with its welded top lip, fill box, vents and lifting lugs
    tbox(L + 0.2, TK, W + 0.34, tank, 0, pad, 0, root, 0, bv(0.05));
    tbox(L + 0.26, 0.05, W + 0.4, tank, 0, y1 - 0.05, 0, root);
    for (const x of [-L / 2 + 0.4, -L / 2 + 4.2, L / 2 - 4.2, L / 2 - 0.4]) tbox(0.08, TK - 0.15, 0.03, tank, x, pad + 0.05, (W + 0.34) / 2, root);
    tbox(0.6, 0.42, 0.34, tank, -3.6, pad + 0.6, W / 2 + 0.3, root, 0, bv(0.02));        // fill spill box
    tbox(0.64, 0.04, 0.38, tank, -3.6, pad + 1.02, W / 2 + 0.3, root);
    if (!low) {
      cyl(0.09, 0.09, 0.04, chrome(), -2.6, pad + 0.7, W / 2 + 0.19, 16, root).rotation.x = Math.PI / 2;   // level gauge
      for (const sx of [-1, 1]) for (const sz of [-1, 1]) tbox(0.16, 0.2, 0.05, tank, sx * (L / 2 - 0.2), pad + TK - 0.3, sz * (W / 2 + 0.2), root);
    }
    if (!low) for (const sx of [-0.5, 0.35]) {                                         // tank vents to the roof
      const x = sx * L;
      pipe([[x, y1, -W / 2 - 0.1], [x, y2 + 0.5, -W / 2 - 0.1]], 0.035, galv(), root);
      const cap = new THREE.Mesh(new THREE.SphereGeometry(0.09, 12, 6, 0, TAU, 0, Math.PI / 2), galv());
      cap.position.set(x, y2 + 0.5, -W / 2 - 0.1); root.add(cap);
    }
    // the enclosure, its roof cap with a drip edge, and standing seams every 1.22 m
    tbox(L, EH, W, skin, 0, y1, 0, root, 0, bv(0.035));
    tbox(L + 0.12, 0.09, W + 0.12, trim, 0, y2, 0, root, 0, bv(0.02));
    for (let x = -L / 2 + 0.61; x < L / 2 - 0.2; x += 1.22) for (const s of [-1, 1])
      cbox(0.05, EH - 0.12, 0.028, skin, x, y1 + EH / 2, s * (W / 2 + 0.014), root);
    // each long side: doors and intake louvres (the radiator bay at +x stays blank)
    const doorAt = [-5.0, -2.1, 0.8], louvAt = [-3.55, -0.65, 2.3];
    function door(parent, x, sz) {
      const dw = 0.95, dh = 2.15, y0 = y1 + 0.28, z = sz * (W / 2 + 0.03);
      cbox(dw + 0.1, 0.05, 0.03, trim, x, y0 + dh + 0.02, z, parent);
      cbox(0.05, dh, 0.03, trim, x - dw / 2 - 0.02, y0 + dh / 2, z, parent);
      cbox(0.05, dh, 0.03, trim, x + dw / 2 + 0.02, y0 + dh / 2, z, parent);
      cbox(dw - 0.02, dh - 0.02, 0.02, skin, x, y0 + dh / 2, z - sz * 0.002, parent);
      cbox(dw - 0.02, 0.01, 0.025, hole(), x, y0 + 0.005, z, parent);
      if (!low) {
        for (const hy of [0.25, dh / 2, dh - 0.25]) cyl(0.02, 0.02, 0.14, chrome(), x - sz * dw / 2 * 0 - dw / 2 + 0.02, y0 + hy - 0.07, z + sz * 0.02, 8, parent);
        cbox(0.05, 0.16, 0.03, chrome(), x + dw / 2 - 0.12, y0 + 1.05, z + sz * 0.025, parent);
        cbox(0.13, 0.03, 0.03, chrome(), x + dw / 2 - 0.17, y0 + 1.0, z + sz * 0.045, parent);
        // an upper vent on the door, and a warning placard
        louvrePanel(parent, x, y0 + dh - 0.45, z + sz * 0.012, 0.6, 0.35, sz, 0x9fa3a5, true);
        cbox(0.24, 0.16, 0.005, std('placard', { color: 0xf1efe8, roughness: 0.6 }), x, y0 + 1.45, z + sz * 0.015, parent);
        cbox(0.24, 0.05, 0.006, std('placardR', { color: 0xc8261e, roughness: 0.6 }), x, y0 + 1.505, z + sz * 0.016, parent);
        cbox(0.22, 0.12, 0.08, std('wallpack', { color: 0x3a3b3c, metalness: 0.4, roughness: 0.5 }), x, y0 + dh + 0.2, z + sz * 0.05, parent);
        cbox(0.18, 0.02, 0.06, lamp(0xfff1d0, 0.6), x, y0 + dh + 0.14, z + sz * 0.06, parent);
      }
    }
    for (const sz of [-1, 1]) {
      doorAt.forEach((x) => door(root, sz > 0 ? x : -x - 0.9, sz));
      louvAt.forEach((x) => louvrePanel(root, sz > 0 ? x : -x - 0.9, y1 + 0.35, sz * (W / 2 + 0.02), 1.3, 2.3, sz, col, low));
    }
    // radiator end, +x: a discharge grille of angled blades over the dark core
    const rx = L / 2 + 0.02;
    cbox(0.04, EH - 0.4, W - 0.4, coilMat(), rx - 0.12, y1 + EH / 2, 0, root);
    const rg = grp(root); rg.position.set(rx, y1 + 0.2, 0); rg.rotation.y = Math.PI / 2;
    louvrePanel(rg, 0, 0, 0, W - 0.3, EH - 0.4, 1, col, low, 0.13);
    // control end, -x: a door and conduit stub ups
    const ce = grp(root); ce.position.set(-L / 2 - 0.02, 0, 0); ce.rotation.y = -Math.PI / 2;
    door(ce, 0, 0);
    if (!low) for (const z of [-0.8, -0.5, 0.9]) pipe([[-L / 2 - 0.12, 0, z], [-L / 2 - 0.12, y1 + 0.4, z]], 0.045, galv(), root);
    cbox(0.3, 0.5, 1.0, trim, -L / 2 - 0.15, y1 + 0.4, -0.65, root);
    // the roof: silencer(s) on saddles, a flex from the engine, the stack and its rain cap
    const two = o.stacks != null ? o.stacks === 2 : r() < 0.5;
    const silM = r() < 0.5 ? std('silBlack', { color: 0x2a2a2a, metalness: 0.5, roughness: 0.55 }) : std('silAlu', { color: 0xbfc2c3, metalness: 0.75, roughness: 0.38 });
    const zs = two ? [-0.62, 0.62] : [0];
    for (const z of zs) {
      const sx = 0.2, sl = 4.4, sr = two ? 0.42 : 0.55, sy = y2 + 0.09 + 0.35 + sr;
      hcyl(sr, sl, silM, sx, sy, z, 'x', SG, root);
      for (const e of [-1, 1]) {
        const cone = new THREE.Mesh(new THREE.CylinderGeometry(sr * 0.35, sr, 0.35, SG), silM);
        cone.rotation.z = -e * Math.PI / 2; cone.position.set(sx + e * (sl / 2 + 0.175), sy, z); root.add(cone);
        if (!low) hcyl(sr + 0.03, 0.05, silM, sx + e * (sl / 2 - 0.1), sy, z, 'x', SG, root);
      }
      for (const e of [-1, 1]) { tbox(0.18, 0.35 + sr * 0.35, sr * 1.4, silM, sx + e * sl * 0.3, y2 + 0.09, z, root); }
      pipe([[sx - sl / 2 - 0.35, sy, z], [sx - sl / 2 - 0.8, sy, z], [sx - sl / 2 - 0.8, y2 + 0.09, z]], sr * 0.34, silM, root, low);
      hcyl(sr * 0.42, 0.25, galv(), sx - sl / 2 - 0.8, y2 + 0.3, z, 'y', 16, root).rotation.set(0, 0, 0);
      const stx = sx + sl / 2 + 0.35, stTop = sy + 2.4;
      pipe([[stx, sy, z], [stx + 0.4, sy, z], [stx + 0.4, stTop, z]], sr * 0.36, silM, root, low);
      // rain cap: a hinged flapper, propped a little open
      const cap = new THREE.Mesh(new THREE.CylinderGeometry(sr * 0.42, sr * 0.42, 0.02, low ? 10 : 20), silM);
      cap.position.set(stx + 0.4 - sr * 0.1, stTop + 0.07, z); cap.rotation.z = 0.35; root.add(cap);
      if (!low) cyl(sr * 0.41, sr * 0.41, 0.04, silM, stx + 0.4, stTop - 0.02, z, 20, root);
    }
    if (!low) for (const sx of [-1, 1]) for (const sz of [-1, 1]) {
      const eye = new THREE.Mesh(new THREE.TorusGeometry(0.06, 0.018, 6, 12), galv());
      eye.position.set(sx * (L / 2 - 0.3), y2 + 0.15, sz * (W / 2 - 0.2)); root.add(eye);
    }
    return root;
  }
  /* A louvre panel: a frame of width w and height h standing on (x, y0) at face z, facing sz.
   * Real angled blades over a dark plenum at high detail; a textured plate at low detail. */
  function louvrePanel(parent, x, y0, z, w, h, sz, col, low, pitch) {
    const fr = paint(col, 0.45, 0.3);
    const g = grp(parent); g.position.set(x, y0, z); if (sz < 0) g.rotation.y = Math.PI;
    cbox(w + 0.08, 0.05, 0.05, fr, 0, h + 0.025, 0.02, g); cbox(w + 0.08, 0.05, 0.05, fr, 0, -0.025, 0.02, g);
    cbox(0.05, h, 0.05, fr, -w / 2 - 0.015, h / 2, 0.02, g); cbox(0.05, h, 0.05, fr, w / 2 + 0.015, h / 2, 0.02, g);
    if (low) {
      const p = new THREE.Mesh(new THREE.PlaneGeometry(w, h), louvreMat(col));
      const uv = p.geometry.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * w / 0.5, uv.getY(i) * h / 0.5);
      p.position.set(0, h / 2, 0.012); g.add(p);
      return g;
    }
    cbox(w, h, 0.01, hole(), 0, h / 2, -0.04, g);
    const p = pitch || 0.1, n = Math.floor(h / p);
    for (let i = 0; i < n; i++) cbox(w, p * 1.25, 0.008, fr, 0, (i + 0.5) * (h / n), 0.0, g, [0.72, 0, 0]);
    if (w > 1.0) cbox(0.03, h, 0.05, fr, 0, h / 2, 0.0, g);
    return g;
  }
  K.define('genset', {
    size: [13.6, 8.05, 4.3],
    options: { color: null, stacks: null, pad: true, lod: 'high' },
    note: 'Containerised 2 to 3 MW diesel genset: 12.2 m sound attenuated enclosure on a belly tank, radiator louvres on +x, personnel doors and intake louvres on both sides, roof silencer and stack. lod:"low" for a yard of them.',
    make(o, r) { return bake(buildGenset(o, r)); },
  });

  /* ======================================================================================
   * CHILLER. An air cooled screw chiller, 11 x 2.3 x 2.5 m: V coils under two rows of fans,
   * a louvred compressor section, a control panel on the -x end, all on a channel base.
   * ==================================================================================== */
  function buildChiller(o, r, low) {
    const root = new THREE.Group();
    const col = o.color != null ? o.color : pick(r, [0xc9c4b5, 0xbfc3c4, 0xd6d3c8, 0xa9b0b3]);
    const skin = paint(col, 0.45, 0.25), frame = darkSteel();
    const n = o.fans || 6, L = n * 1.9 + 0.7, W = 2.26, H = 2.5, cy = 1.25;
    tbox(L, 0.2, W, frame, 0, 0, 0, root);                                            // channel base
    for (const s of [-1, 1]) cbox(L, 0.14, 0.02, frame, 0, 0.1, s * (W / 2 + 0.01), root);
    // lower section: louvred panels over compressors, a couple removed to show the machinery
    for (const s of [-1, 1]) {
      const nb = n;
      for (let i = 0; i < nb; i++) {
        const x = -L / 2 + 0.35 + (i + 0.5) * (L - 0.7) / nb, open = false;
        if (open) continue;
        louvrePanel(root, x, 0.25, s * (W / 2), (L - 0.7) / nb - 0.06, cy - 0.3, s, col, true);
      }
    }
    tbox(L - 0.1, cy - 0.25, W - 0.3, hole(), 0, 0.2, 0, root);
    if (!low) {                                                                        // what shows through
      for (const x of [-L / 2 + 2.6, -L / 2 + 4.2]) {
        hcyl(0.26, 0.9, std('compr', { color: 0x4b5a63, metalness: 0.4, roughness: 0.5 }), x, 0.65, W / 2 - 0.45, 'x', 18, root);
        cyl(0.08, 0.08, 0.5, std('copper', { color: 0xa0613a, metalness: 0.9, roughness: 0.35 }), x + 0.3, 0.8, W / 2 - 0.4, 10, root);
      }
      hcyl(0.3, L * 0.55, blackPaint(), -L * 0.05, 0.62, W / 2 - 0.95, 'x', 20, root);   // insulated evaporator
    }
    // V coils: two inclined coil faces per side meeting at the fan deck
    const coilH = H - cy - 0.05;
    for (const s of [-1, 1]) {
      const c = new THREE.Mesh(new THREE.PlaneGeometry(L - 0.5, coilH / Math.cos(0.3)), coilMat());
      const uv = c.geometry.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * (L - 0.5) / 0.25, uv.getY(i) * coilH / 0.25);
      c.position.set(0, cy + coilH / 2, s * (W / 2 - 0.2)); c.rotation.set(s * 0.18, s < 0 ? Math.PI : 0, 0); root.add(c);
    }
    tbox(L - 0.4, coilH, W - 0.9, hole(), 0, cy, 0, root);
    // corner posts, vertical dividers between fan bays
    for (const sx of [-1, 1]) for (const sz of [-1, 1]) tbox(0.08, H - 0.2, 0.08, skin, sx * (L / 2 - 0.04), 0.2, sz * (W / 2 - 0.04), root);
    for (let i = 0; i <= n; i++) for (const sz of [-1, 1]) tbox(0.06, coilH, 0.05, skin, -L / 2 + 0.35 + i * (L - 0.7) / n, cy, sz * (W / 2 - 0.1), root);
    for (const sz of [-1, 1]) tbox(L, 0.08, 0.1, skin, 0, cy - 0.04, sz * (W / 2 - 0.05), root);
    // fan deck and two rows of fans
    tbox(L, 0.08, W, skin, 0, H - 0.08, 0, root);
    const fr = 0.43;
    for (let i = 0; i < n; i++) for (const sz of [-0.53, 0.53]) {
      const x = -L / 2 + 0.35 + (i + 0.5) * (L - 0.7) / n;
      fanUnit(root, x, H - 0.06, sz, fr, 0.28, skin);
    }
    // end panels, control box with two doors, lifting holes
    for (const s of [-1, 1]) tbox(0.04, H - 0.28, W - 0.1, skin, s * (L / 2 - 0.02), 0.2, 0, root);
    const cb = tbox(0.45, 1.8, W - 0.3, skin, -L / 2 - 0.22, 0.25, 0, root, 0, 0.02);
    if (!low) {
      for (const z of [-0.45, 0.45]) {
        cbox(0.02, 1.6, 0.86, skin, -L / 2 - 0.45, 1.15, z, root);
        cbox(0.04, 0.14, 0.03, chrome(), -L / 2 - 0.47, 1.2, z + 0.34 * Math.sign(z), root);
      }
      cbox(0.02, 0.12, 0.2, std('screen', { color: 0x0e1a22, emissive: 0x2a8f6a, emissiveIntensity: 0.4 }), -L / 2 - 0.47, 1.6, -0.45, root);
      pipe([[L / 2 - 0.3, 0.7, W / 2 + 0.05], [L / 2 + 0.3, 0.7, W / 2 + 0.05], [L / 2 + 0.3, 0.0, W / 2 + 0.05]], 0.1, std('chwpipe', { color: 0x2e3f58, metalness: 0.3, roughness: 0.5 }), root);
      pipe([[L / 2 - 0.3, 0.7, W / 2 - 0.45], [L / 2 + 0.6, 0.7, W / 2 - 0.45], [L / 2 + 0.6, 0.0, W / 2 - 0.45]], 0.1, std('chwpipe', { color: 0x2e3f58, metalness: 0.3, roughness: 0.5 }), root);
      for (const z of [W / 2 + 0.05, W / 2 - 0.45]) flange(0.15, L / 2 - 0.05, 0.7, z, 'x', galv(), root);
      cbox(0.24, 0.16, 0.005, std('placard', { color: 0xf1efe8, roughness: 0.6 }), -L / 2 + 1.0, 1.5, W / 2 + 0.01, root);
    }
    return root;
  }
  K.define('chiller', {
    size: [13.3, 2.76, 2.5],
    options: { color: null, fans: 6 },
    note: 'Air cooled screw chiller: V condenser coils under two rows of guarded fans, louvred compressor base, control panel on -x, chilled water nozzles on +x.',
    make(o, r) { return bake(buildChiller(o, r, false)); },
  });

  /* ======================================================================================
   * SERVER RACK. 42U, 0.6 x 2.0 x 1.07 m, black. Seeded equipment: 1U and 2U servers with
   * drive bays, a 4U storage shelf, a top of rack switch with patch cords, blanking panels.
   * LEDs are an instanced unlit layer; userData.tick(t) blinks them for animation.
   * ==================================================================================== */
  const RU = 0.04445;
  function faceAtlas() {
    // rows of 64 px: 0 server1U, 1 server2U (128 px), 3 storage (256 px), 7 switch, 8 blank, 9 patch
    return ctex('rackAtlas', 1024, 1024, (x, w) => {
      x.fillStyle = '#121314'; x.fillRect(0, 0, w, 1024);
      const bays = (y0, hh, cols, rows, dark) => {
        const bw = (w - 180) / cols, bh = hh / rows;
        for (let c = 0; c < cols; c++) for (let rr2 = 0; rr2 < rows; rr2++) {
          const bx = 90 + c * bw, by = y0 + rr2 * bh;
          x.fillStyle = dark ? '#1b1d1f' : '#26292c'; x.fillRect(bx + 2, by + 3, bw - 4, bh - 6);
          x.fillStyle = '#3a3e42'; x.fillRect(bx + 2, by + 3, bw - 4, 3);
          x.fillStyle = '#0c0d0e'; for (let k = 0; k < 6; k++) x.fillRect(bx + 8 + k * 6, by + bh / 2 - 6, 3, 12);
          x.fillStyle = '#7d8388'; x.fillRect(bx + bw - 16, by + bh / 2 - 5, 8, 10);
        }
      };
      // 1U server: ears, 10 drive bays
      x.fillStyle = '#1c1e20'; x.fillRect(0, 0, w, 64); bays(4, 56, 10, 1);
      x.fillStyle = '#2c2f33'; x.fillRect(0, 0, 80, 64); x.fillRect(w - 80, 0, 80, 64);
      // 2U server: 24 small bays in two rows and a bezel grille
      x.fillStyle = '#18191b'; x.fillRect(0, 64, w, 128); bays(70, 116, 12, 2, true);
      x.fillStyle = '#2c2f33'; x.fillRect(0, 64, 80, 128); x.fillRect(w - 80, 64, 80, 128);
      // 4U storage: 4 rows of 3.5 in drives
      x.fillStyle = '#16171a'; x.fillRect(0, 192, w, 256); bays(200, 240, 6, 4);
      x.fillStyle = '#2c2f33'; x.fillRect(0, 192, 80, 256); x.fillRect(w - 80, 192, 80, 256);
      // switch: 48 ports in two rows, 6 uplinks
      x.fillStyle = '#1e2022'; x.fillRect(0, 448, w, 64);
      for (let c = 0; c < 24; c++) for (let rr2 = 0; rr2 < 2; rr2++) {
        const px = 110 + c * 30 + Math.floor(c / 6) * 8, py = 454 + rr2 * 27;
        x.fillStyle = '#6a7075'; x.fillRect(px, py, 24, 22); x.fillStyle = '#060607'; x.fillRect(px + 3, py + 4, 18, 15);
      }
      for (let c = 0; c < 6; c++) { x.fillStyle = '#7d8388'; x.fillRect(880 + (c % 3) * 36, 456 + Math.floor(c / 3) * 27, 30, 22); x.fillStyle = '#070707'; x.fillRect(884 + (c % 3) * 36, 460 + Math.floor(c / 3) * 27, 22, 14); }
      // blanking panel
      x.fillStyle = '#141516'; x.fillRect(0, 512, w, 64); x.fillStyle = '#1d1f21'; for (let i = 0; i < 64; i += 8) x.fillRect(0, 512 + i, w, 2);
      // patch panel: 24 keystones with coloured boots
      x.fillStyle = '#1a1b1d'; x.fillRect(0, 576, w, 64);
      for (let c = 0; c < 24; c++) { const px = 110 + c * 33; x.fillStyle = '#e8e8e2'; x.fillRect(px, 590, 26, 30); x.fillStyle = '#0a0a0a'; x.fillRect(px + 4, 596, 18, 16); }
    });
  }
  K.define('server_rack', {
    size: [0.6, 2.03, 1.07],
    options: { door: false, leds: true, fill: 0.85, blink: true },
    note: '42U rack, black steel, seeded servers, storage, switch, patch panel and blanks; perforated door optional; LEDs are an unlit instanced layer and userData.tick(t) blinks them.',
    make(o, r) {
      const root = new THREE.Group();
      const W = 0.6, H = 2.0, D = 1.07, blk = std('rackBlack', { color: 0x151618, metalness: 0.45, roughness: 0.5 });
      // frame: plinth, side panels, top with cable brush ports, four vertical rails
      tbox(W, 0.1, D, blk, 0, 0, 0, root);
      for (const s of [-1, 1]) tbox(0.02, H - 0.1, D, blk, s * (W / 2 - 0.01), 0.1, 0, root, 0, 0.004);
      tbox(W, 0.04, D, blk, 0, H - 0.04, 0, root, 0, 0.006);
      for (const z of [-0.25, 0.2]) cbox(0.25, 0.005, 0.08, rubber(), 0, H + 0.0025, z, root);
      for (const sx of [-1, 1]) for (const sz of [-1, 1]) tbox(0.03, H - 0.14, 0.03, blk, sx * 0.235, 0.1, sz * (D / 2 - 0.08), root);
      for (const sx of [-1, 1]) for (const sz of [-1, 1]) cyl(0.02, 0.025, 0.05, galv(), sx * 0.24, -0.0, sz * 0.46, 10, root);
      tbox(W - 0.06, H - 0.14, 0.01, hole(), 0, 0.1, -D / 2 + 0.06, root);              // deep interior
      // equipment, stacked from the bottom up
      const atlas = faceAtlas();
      const faceM = lmat('rackFace', () => new THREE.MeshStandardMaterial({ color: 0xffffff, map: atlas, roughness: 0.55, metalness: 0.4 }));
      const types = [['s1', 1, 0, 64], ['s2', 2, 64, 128], ['st', 4, 192, 256], ['sw', 1, 448, 64], ['bl', 1, 512, 64], ['pp', 1, 576, 64]];
      const T = Object.fromEntries(types.map((t) => [t[0], t]));
      const leds = [];
      const face = (t, y) => {
        const hh = t[1] * RU - 0.001;
        const p = new THREE.Mesh(new THREE.PlaneGeometry(0.482, hh), faceM);
        const uv = p.geometry.attributes.uv, v0 = 1 - (t[2] + t[3]) / 1024, v1 = 1 - t[2] / 1024;
        for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i), uv.getY(i) > 0.5 ? v1 : v0);
        p.position.set(0, y + hh / 2, D / 2 - 0.06); root.add(p);
        tbox(0.44, hh - 0.002, 0.7, blk, 0, y + 0.001, D / 2 - 0.42, root);
      };
      let u = 0; const top = 42;
      const plan = [];
      plan.push(['pp', 41], ['sw', 40], ['bl', 39]);
      while (u < 38) {
        const k = r();
        if (r() > o.fill) { plan.push(['bl', u]); u += 1; continue; }
        if (k < 0.45) { plan.push(['s1', u]); u += 1; }
        else if (k < 0.85 && u + 2 <= 38) { plan.push(['s2', u]); u += 2; }
        else if (u + 4 <= 38) { plan.push(['st', u]); u += 4; }
        else { plan.push(['s1', u]); u += 1; }
      }
      plan.forEach(([k, uu]) => {
        const t = T[k], y = 0.12 + uu * RU;
        face(t, y);
        if (k === 's1' || k === 's2' || k === 'st') {
          const rows = t[1] === 1 ? 1 : 2;
          for (let rw = 0; rw < rows; rw++) leds.push([-0.215, y + (rw + 0.5) * t[1] * RU / rows, 'g']);
          leds.push([0.205, y + t[1] * RU * 0.5, r() < 0.12 ? 'a' : 'b']);
          const nb = k === 's1' ? 10 : k === 's2' ? 12 : 6;
          for (let b = 0; b < nb; b++) if (r() < 0.8) leds.push([-0.198 + (b + 0.85) * (0.482 - 0.176) / nb, y + t[1] * RU * (k === 'st' ? 0.12 : 0.28), 'g']);
        }
        if (k === 'sw') for (let p = 0; p < 24; p++) if (r() < 0.75) leds.push([-0.137 + p * 0.0145 + Math.floor(p / 6) * 0.004, y + 0.036, 'g']);
      });
      // patch cords from the switch looping into the side managers
      const cordCols = [0x2f6fd1, 0xe0b52a, 0x3b9e4f, 0xd9dcdc, 0xc0392b];
      const ySw = 0.12 + 40 * RU + 0.015, yPp = 0.12 + 41 * RU + 0.02;
      for (let p = 0; p < 16; p++) {
        const x0 = -0.137 + p * 0.0145 * 1.5, side = p < 8 ? -1 : 1, c = cordCols[p % cordCols.length];
        const m = std('cord' + hex(c), { color: c, roughness: 0.55 });
        root.add(TXT.tube([[x0, ySw, D / 2 - 0.05], [x0 * 0.8, ySw - 0.02, D / 2 - 0.0], [side * 0.26, ySw - 0.05 - p * 0.004, D / 2 - 0.02], [side * 0.27, ySw - 0.35 - p * 0.02, D / 2 - 0.04]], 0.0028, m, { segments: 16, radial: 4 }));
        root.add(TXT.tube([[x0, yPp, D / 2 - 0.05], [x0 * 0.9, yPp + 0.03, D / 2 + 0.0], [side * 0.26, yPp + 0.02, D / 2 - 0.02], [side * 0.27, yPp - 0.3 - p * 0.02, D / 2 - 0.04]], 0.0028, m, { segments: 16, radial: 4 }));
      }
      for (const s of [-1, 1]) tbox(0.05, H - 0.3, 0.1, blk, s * 0.27, 0.15, D / 2 - 0.08, root);  // vertical cable managers
      // LEDs, unlit, instanced, per instance colour; tick(t) blinks the activity ones
      if (o.leds && leds.length) {
        const geo = new THREE.PlaneGeometry(0.0032, 0.0032);
        const im = new THREE.InstancedMesh(geo, lmat('ledBasic', () => new THREE.MeshBasicMaterial({ color: 0xffffff, toneMapped: false })), leds.length);
        const M = new THREE.Matrix4(), col = new THREE.Color();
        const C = { g: 0x39ff7a, b: 0x3aa8ff, a: 0xffa020 };
        leds.forEach((l, i) => { M.makeTranslation(l[0], l[1], D / 2 - 0.058); im.setMatrixAt(i, M); im.setColorAt(i, col.setHex(C[l[2]]).multiplyScalar(r() < 0.8 ? 1.6 : 0.05)); });
        im.instanceMatrix.needsUpdate = true; im.instanceColor.needsUpdate = true;
        im.userData.keep = true; im.castShadow = false;
        root.add(im);
        const seed = o.seed;
        root.userData.tick = function (t) {
          if (!o.blink) return;
          leds.forEach((l, i) => { const on = l[2] === 'g' ? ((Math.sin(t * 17 + i * 12.9898 + seed) * 43758.5453) % 1 + 1) % 1 > 0.35 : true;
            im.setColorAt(i, col.setHex(C[l[2]]).multiplyScalar(on ? 1.6 : 0.05)); });
          im.instanceColor.needsUpdate = true;
        };
      }
      // the door: perforated steel, hinged left, with a swing handle
      if (o.door) {
        const perf = lmat('perf', () => new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 0.5, roughness: 0.5, side: THREE.DoubleSide,
          alphaTest: 0.5, map: ctex('perfC', 128, 128, (x, w) => { x.fillStyle = '#1a1b1d'; x.fillRect(0, 0, w, w);
            x.globalCompositeOperation = 'destination-out';
            for (let j = 0; j < 8; j++) for (let i = 0; i < 8; i++) { x.beginPath(); x.arc(i * 16 + (j % 2) * 8 + 4, j * 16 + 8, 5.2, 0, TAU); x.fill(); }
            x.globalCompositeOperation = 'source-over'; }) }));
        const dp = new THREE.Mesh(new THREE.PlaneGeometry(W - 0.1, H - 0.3), perf);
        const uv = dp.geometry.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * (W - 0.1) / 0.05, uv.getY(i) * (H - 0.3) / 0.05);
        dp.position.set(0, H / 2 + 0.05, D / 2 + 0.01); root.add(dp);
        for (const s of [-1, 1]) cbox(0.05, H - 0.2, 0.02, blk, s * (W / 2 - 0.025), H / 2 + 0.05, D / 2 + 0.01, root);
        for (const y of [0.15, H - 0.05]) cbox(W, 0.05, 0.02, blk, 0, y, D / 2 + 0.01, root);
        cbox(0.03, 0.16, 0.03, chrome(), W / 2 - 0.05, 1.1, D / 2 + 0.03, root);
      }
      return bake(root);
    },
  });

  installBig(K, THREE, TXT, { std, paint, galv, darkSteel, blackPaint, rubber, chrome, hole, glass, lamp, concrete, gravel, asphalt,
    ctex, rgb, speckle, louvreMat, panelMat, coilMat, guardMat, chainMat, sectionalMat, grp, cbox, tbox, cyl, hcyl, bar, sbar, pipe,
    flange, valve, railing, stair, ladder, collect, emit, bake, stamp, strokeText, starPath, fanUnit, fenceRun, trailer, louvrePanel,
    buildGenset, buildChiller, lmat, pick, rr, TAU, D2R, instanced });
  // K.make merges only { seed: 1 } over the caller's options, so each model's own defaults are applied here
  for (const n of Object.keys(K.registry)) {
    if (BEFORE.has(n)) continue;
    const spec = K.registry[n], make = spec.make;
    spec.make = (o, r) => {
      const g = make(Object.assign({}, spec.options || {}, o), r);
      // origin at the centre of the footprint, on the ground
      const bb = new THREE.Box3().setFromObject(g), cx = (bb.min.x + bb.max.x) / 2, cz = (bb.min.z + bb.max.z) / 2;
      if (Math.abs(cx) > 0.01 || Math.abs(cz) > 0.01) g.children.forEach((c) => { c.position.x -= cx; c.position.z -= cz; c.updateMatrix(); });
      return g;
    };
  }
}

/* The site scale models live below, sharing the helpers above through `H`. */
function installBig(K, THREE, TXT, H) {
  const { std, paint, galv, darkSteel, blackPaint, rubber, chrome, hole, glass, lamp, concrete, gravel, asphalt,
    ctex, rgb, speckle, louvreMat, panelMat, coilMat, chainMat, sectionalMat, grp, cbox, tbox, cyl, hcyl, bar, sbar, pipe,
    flange, valve, railing, stair, ladder, collect, emit, bake, stamp, strokeText, starPath, fanUnit, fenceRun, trailer,
    louvrePanel, buildGenset, lmat, pick, rr, TAU, D2R, instanced } = H;
  const V3 = THREE.Vector3;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const glassT = (tint) => lmat('glassT' + (tint || 0), () => new THREE.MeshPhysicalMaterial({ color: tint || 0x3c4d58,
    metalness: 0.1, roughness: 0.04, clearcoat: 1, clearcoatRoughness: 0.03, transparent: true, opacity: 0.5, envMapIntensity: 1.6 }));
  const flatPlane = (w, d, mat, x, y, z, parent, metres) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, d), mat); m.rotation.x = -Math.PI / 2; m.position.set(x, y, z);
    if (metres) { const uv = m.geometry.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * w / metres, uv.getY(i) * d / metres); }
    parent.add(m); return m;
  };
  const wallPlane = (w, h, mat, x, y0, z, rotY, parent, mu, mv) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat); m.position.set(x, y0 + h / 2, z); m.rotation.y = rotY || 0;
    if (mu) { const uv = m.geometry.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * w / mu, uv.getY(i) * h / (mv || mu)); }
    parent.add(m); return m;
  };
  // A curtain wall: glass over a lit interior, mullions, a spandrel at each floor, a sill.
  function curtainWall(parent, x, y0, z, w, h, rotY, floors, mullion, interior) {
    const g = grp(parent); g.position.set(x, y0, z); g.rotation.y = rotY || 0;
    const mul = std('mullion', { color: 0x2f3337, metalness: 0.7, roughness: 0.35 });
    if (interior !== false) {
      const depth = 5;
      tbox(w, h, 0.05, std('intBack', { color: 0x4a4540, roughness: 0.9 }), 0, 0, -depth, g);
      for (let f = 0; f < floors; f++) {
        const fy = f * h / floors;
        tbox(w, 0.25, depth, std('intFloor', { color: 0x6b6258, roughness: 0.8 }), 0, fy, -depth / 2, g);
        tbox(w, 0.05, depth, std('intCeil', { color: 0xd8d4cc, roughness: 0.9 }), 0, fy + h / floors - 0.45, -depth / 2, g);
        for (let lx = -w / 2 + 1.2; lx < w / 2 - 0.6; lx += 2.4) for (const lz of [-1.2, -3.4])
          cbox(1.2, 0.03, 0.3, lamp(0xfff4dc, 1.8), lx, fy + h / floors - 0.47, lz, g);
        for (let lx = -w / 2 + 1.5; lx < w / 2 - 1; lx += 3.1) tbox(1.4, 0.75, 0.7, std('desk', { color: 0x3b3a38, roughness: 0.7 }), lx, fy + 0.25, -2.2, g);
      }
      for (const s of [-1, 1]) tbox(0.05, h, depth, std('intBack', { color: 0x4a4540, roughness: 0.9 }), s * w / 2, 0, -depth / 2, g);
    }
    wallPlane(w, h, glassT(), 0, 0, 0.0, 0, g);
    const nv = Math.round(w / mullion);
    for (let i = 0; i <= nv; i++) cbox(0.07, h, 0.16, mul, -w / 2 + i * w / nv, h / 2, 0.05, g);
    for (let f = 0; f <= floors; f++) {
      const fy = f * h / floors;
      cbox(w, f === 0 || f === floors ? 0.12 : 0.9, 0.14, f === 0 || f === floors ? mul : std('spandrel', { color: 0x30363b, metalness: 0.5, roughness: 0.3 }), 0, fy, 0.05, g);
      if (f < floors) cbox(w, 0.06, 0.15, mul, 0, fy + (h / floors) * 0.55, 0.05, g);
    }
    return g;
  }

  /* ======================================================================================
   * DATA CENTER. A hyperscale data hall: a long low insulated metal panel box on a precast
   * plinth, louvred intake bays between pilasters, dry coolers in rows on a white membrane
   * roof, a yard of containerised gensets with their stacks along the front, bulk diesel
   * tanks, a glazed office entry, truck docks on the +x end, a perimeter security fence.
   * ==================================================================================== */
  K.define('data_center', {
    size: [227, 16.2, 111.4],
    options: { length: 180, depth: 70, height: 14, gensets: null, fence: true, color: null, panels: null, site: true },
    note: 'Hyperscale data hall: length 100 to 300 m, IMP walls with louvred intake bays, rooftop dry cooler rows, a front genset yard with stacks and bulk fuel tanks, glazed office, docks on +x, security fence. Front (+z) is the generator yard.',
    make(o, r) {
      const L = clamp(o.length, 100, 300), D = clamp(o.depth, 40, 120), Hh = clamp(o.height, 12, 16);
      const root = new THREE.Group(), parts = [];
      const col = o.color != null ? o.color : pick(r, [0xdfe1e0, 0xd3d0c8, 0xc4c8ca, 0xe6e2d8, 0xb7bcbf]);
      const horiz = o.panels ? o.panels === 'horizontal' : r() < 0.5;
      const accent = pick(r, [0x4a5055, 0x6b7176, 0x8b9094, 0x3c4a57]);
      const louvCol = pick(r, [0x5d6266, 0x74797c, 0x4c5156]);
      const yardD = 20, frontM = 8, backM = 12, sideM = 24;
      const Dt = D + yardD + frontM + backM, zb0 = -Dt / 2 + backM, zb1 = zb0 + D, zc = (zb0 + zb1) / 2;
      const Hroof = Hh - 1.0;
      // site: concrete apron, gen yard slab, asphalt drive, gravel verges
      if (o.site) {
        tbox(L + 8, 0.08, D + 8, concrete('#b0aca3'), 0, 0, zc, root, 3);
        tbox(L - 30, 0.1, yardD, concrete('#aba79e'), -15, 0, zb1 + 4 + yardD / 2 - 4, root, 3);
        tbox(14, 0.06, frontM + yardD + 4, asphalt(), L / 2 - 12, 0, zb1 + (frontM + yardD + 4) / 2 - 2, root, 0);
        tbox(sideM - 2, 0.06, 40, asphalt(), L / 2 + sideM / 2 - 1, 0, zc - 4, root, 0);
      }
      // the hall: plinth, IMP walls, parapet with coping, membrane roof with walkway pads
      tbox(L + 0.12, 1.4, D + 0.12, concrete('#9f9b92'), 0, 0, zc, root, 3);
      const body = K.box(L, Hh - 1.4, D, panelMat(col, horiz), 0, 1.4, zc, 0, root);
      K.uvBox(body.geometry, 2);
      tbox(L + 0.3, 0.25, D + 0.3, paint(accent, 0.45, 0.4), 0, Hh - 0.25, zc, root, 0, 0.04);
      const roofM = std('tpo', { color: 0xdedcd4, roughness: 0.75 });
      tbox(L - 0.6, 0.05, D - 0.6, roofM, 0, Hroof, zc, root);
      // pilasters every bay, louvre banks in most bays, on the front and back long walls
      const bays = Math.max(6, Math.round(L / 9.6)), bw = L / bays;
      for (const s of [-1, 1]) {
        const zf = s > 0 ? zb1 : zb0;
        for (let i = 0; i <= bays; i++) tbox(0.7, Hh - 1.4 - 0.3, 0.3, paint(col, 0.5, 0.3), -L / 2 + i * bw, 1.4, zf + s * 0.15, root);
        for (let i = 0; i < bays; i++) {
          const cx = -L / 2 + (i + 0.5) * bw;
          if (s > 0 && cx > L / 2 - 40) continue;                                   // office end stays clean
          if ((i + (s > 0 ? 0 : 1)) % 4 === 3) continue;
          const lh = Hh - 6.2, ly = 3.4;
          wallPlane(bw - 1.3, lh, louvreMat(louvCol, 'dc'), cx, ly, zf + s * 0.04, s > 0 ? 0 : Math.PI, root, 0.5);
          for (const yy of [ly - 0.08, ly + lh]) cbox(bw - 1.1, 0.16, 0.14, paint(accent, 0.45, 0.4), cx, yy + 0.08, zf + s * 0.07, root);
          for (let m = 1; m < 3; m++) cbox(0.1, lh, 0.1, paint(accent, 0.45, 0.4), cx - (bw - 1.3) / 2 + m * (bw - 1.3) / 3, ly + lh / 2, zf + s * 0.06, root);
        }
      }
      // -x end: a full louvre wall; +x end: the docks
      wallPlane(D - 8, Hh - 5.5, louvreMat(louvCol, 'dc'), -L / 2 - 0.04, 3, zc, -Math.PI / 2, root, 0.5);
      for (let i = 0; i <= 6; i++) cbox(0.14, Hh - 5.5, 0.12, paint(accent, 0.45, 0.4), -L / 2 - 0.07, 3 + (Hh - 5.5) / 2, zc - (D - 8) / 2 + i * (D - 8) / 6, root);
      const nd = 3;
      for (let i = 0; i < nd; i++) {
        const dz = zc - 14 + i * 4.6, dx = L / 2;
        const dm = wallPlane(3.0, 3.0, sectionalMat(0xd9dcdc), dx + 0.06, 1.25, dz, Math.PI / 2, root);
        cbox(0.3, 3.3, 0.35, rubber(), dx + 0.2, 1.25 + 1.6, dz - 1.65, root); cbox(0.3, 3.3, 0.35, rubber(), dx + 0.2, 1.25 + 1.6, dz + 1.65, root);
        cbox(0.3, 0.45, 3.6, rubber(), dx + 0.2, 1.25 + 3.2, dz, root);
        for (const s of [-1, 1]) cbox(0.14, 0.45, 0.28, rubber(), dx + 0.08, 0.95, dz + s * 1.0, root);
        cbox(1.2, 0.08, 3.8, paint(accent, 0.45, 0.4), dx + 0.6, 5.3, dz, root);
        cbox(0.18, 0.1, 0.25, darkSteel(), dx + 0.15, 4.9, dz + 2.1, root);
      }
      trailer(root, L / 2 + 8.3, zc - 14 + 4.6, Math.PI / 2, pick(r, [0xe9e9e6, 0xd9d8d2]), r);
      // the office entry: two storeys of curtain wall at the +x front corner, a canopy
      const ox0 = L / 2 - 36, ox1 = L / 2 - 2, oz1 = zb1 + 10, oH = 9;
      tbox(ox1 - ox0, 0.6, oz1 - zb1, concrete('#9f9b92'), (ox0 + ox1) / 2, 0, (zb1 + oz1) / 2, root, 3);
      curtainWall(root, (ox0 + ox1) / 2, 0.6, oz1, ox1 - ox0 - 0.6, oH - 1.4, 0, 2, 1.55);
      curtainWall(root, ox1, 0.6, (zb1 + oz1) / 2, oz1 - zb1 - 0.6, oH - 1.4, Math.PI / 2, 2, 1.55);
      curtainWall(root, ox0, 0.6, (zb1 + oz1) / 2, oz1 - zb1 - 0.6, oH - 1.4, -Math.PI / 2, 2, 1.55, false);
      tbox(ox1 - ox0 + 0.8, 0.8, oz1 - zb1 + 0.8, paint(accent, 0.45, 0.4), (ox0 + ox1) / 2, oH - 0.8, (zb1 + oz1) / 2 + 0.2, root, 0, 0.04);
      tbox(ox1 - ox0 - 1, 0.1, oz1 - zb1 - 1, roofM, (ox0 + ox1) / 2, oH, (zb1 + oz1) / 2, root);
      const ex = ox0 + 9;
      tbox(8, 0.35, 4.5, paint(accent, 0.45, 0.4), ex, 4.2, oz1 + 2.2, root, 0, 0.03);
      for (const s of [-1, 1]) cyl(0.12, 0.12, 3.6, paint(accent, 0.45, 0.4), ex + s * 3.6, 0.6, oz1 + 4.1, 12, root);
      cbox(7.6, 0.02, 4.2, lamp(0xfff1d8, 0.6), ex, 4.19, oz1 + 2.2, root);
      for (let b = 0; b < 5; b++) cyl(0.11, 0.11, 0.95, paint(0xd8b24a, 0.5, 0.2), ex - 4 + b * 2, 0.06, oz1 + 5.2, 12, root);
      // rooftop: rows of dry coolers on dunnage, stamped from one template
      const tpl = new THREE.Group();
      const unitL = 7.2, unitW = 2.2, unitH = 2.1, cm = paint(0xd3d4d2, 0.45, 0.3);
      for (const s of [-1, 1]) sbar([-unitL / 2 - 0.3, 0.25, s * 0.8], [unitL / 2 + 0.3, 0.25, s * 0.8], 0.2, 0.3, darkSteel(), tpl);
      tbox(unitL, 0.25, unitW, cm, 0, 0.4, 0, tpl);
      for (const s of [-1, 1]) {
        const c = new THREE.Mesh(new THREE.PlaneGeometry(unitL - 0.3, unitH - 0.3), coilMat());
        const uv = c.geometry.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * (unitL - 0.3) / 0.25, uv.getY(i) * (unitH - 0.3) / 0.25);
        c.position.set(0, 0.65 + (unitH - 0.3) / 2, s * (unitW / 2 - 0.12)); c.rotation.set(s * 0.14, s > 0 ? 0 : Math.PI, 0); tpl.add(c);
      }
      tbox(unitL - 0.4, unitH - 0.3, unitW - 0.6, hole(), 0, 0.65, 0, tpl);
      for (const sx of [-1, 1]) tbox(0.06, unitH, unitW, cm, sx * (unitL / 2 - 0.03), 0.4, 0, tpl);
      for (let i = 0; i <= 4; i++) for (const s of [-1, 1]) tbox(0.07, unitH - 0.2, 0.06, cm, -unitL / 2 + i * unitL / 4, 0.55, s * (unitW / 2 - 0.05), tpl);
      tbox(unitL, 0.08, unitW, cm, 0, 0.4 + unitH, 0, tpl);
      for (let i = 0; i < 4; i++) fanUnit(tpl, -unitL / 2 + (i + 0.5) * unitL / 4, 0.48 + unitH, 0, 0.78, 0.32, cm, true);
      const rows = Math.max(2, Math.floor((D - 12) / 10.5)), per = Math.floor((L - 14) / 8.6);
      const places = [];
      for (let j = 0; j < rows; j++) {
        const z = zc - (rows - 1) * 10.5 / 2 + j * 10.5;
        for (let i = 0; i < per; i++) {
          const x = -L / 2 + 7 + (i + 0.5) * (L - 14) / per;
          if (x > L / 2 - 40 && j === rows - 1) continue;
          places.push([x, Hroof + 0.05, z, 0]);
        }
        // walkway pads between the rows, and a pipe rack feeding them
        if (j < rows - 1) tbox(L - 16, 0.03, 1.2, std('pad', { color: 0xb9b8b1, roughness: 0.85 }), 0, Hroof + 0.05, z + 5.25, root);
        for (const s of [-1, 1]) sbar([-L / 2 + 6, Hroof + 0.5, z + s * 1.7], [L / 2 - 6, Hroof + 0.5, z + s * 1.7], 0.28, 0.28,
          std('dcpipe', { color: 0x6f7a80, metalness: 0.5, roughness: 0.45 }), root);
      }
      instanced(tpl, places, root);
      for (const [x, z] of [[-L / 2 + 20, zb0 + 4], [L / 2 - 30, zb0 + 4], [0, zb0 + 4]]) {
        tbox(5, 3.2, 3.5, paint(col, 0.5, 0.3), x, Hroof, z, root, 0, 0.03);
        wallPlane(3, 2, louvreMat(louvCol, 'dc'), x, Hroof + 0.6, z + 1.77, 0, root, 0.5);
      }
      tbox(1.2, 0.5, 1.2, paint(accent, 0.45, 0.4), -L / 2 + 12, Hroof, zb1 - 5, root);
      railing(root, [[-L / 2 + 10.5, Hroof, zb1 - 6.5], [-L / 2 + 13.5, Hroof, zb1 - 6.5], [-L / 2 + 13.5, Hroof, zb1 - 3.5], [-L / 2 + 10.5, Hroof, zb1 - 3.5], [-L / 2 + 10.5, Hroof, zb1 - 6.5]], 1.07, paint(0xd8b24a, 0.5, 0.2), 1.5);
      ladder(root, -L / 2 + 30, 0, Hroof, zb0 - 0.05, galv(), true, Math.PI);
      for (let x = -L / 2 + bw * 2; x < L / 2 - 20; x += bw * 4) for (const zz of [zb0 - 0.2]) pipe([[x, Hh - 0.3, zz], [x, 0.3, zz]], 0.1, paint(accent, 0.45, 0.4), root);
      // the generator yard: gensets side by side, radiators outward, stacks up
      const gcol = pick(r, [0xe8e6df, 0xdcd9d0, 0xc8ccce]);
      const gtpl = buildGenset({ lod: 'low', pad: false, color: gcol, stacks: 1 }, K.rng(o.seed * 31 + 7));
      const yx0 = -L / 2 + 6, yx1 = L / 2 - 42, pitch = 4.7;
      const ng = o.gensets != null ? o.gensets : Math.floor((yx1 - yx0) / pitch);
      const gpl = [];
      for (let i = 0; i < ng; i++) gpl.push([yx0 + (i + 0.5) * (yx1 - yx0) / ng, 0.1, zb1 + 4.2 + 6.8, -Math.PI / 2]);
      instanced(gtpl, gpl, root);
      // a cable tray bridge from the yard into the hall, on bents
      const tray = galv();
      for (let x = yx0; x <= yx1; x += 9) { bar([x, 0.1, zb1 + 2.4], [x, 6.4, zb1 + 2.4], 0.1, tray, root, 8); sbar([x, 6.4, zb1 + 2.4], [x, 6.4, zb1 + 0.05], 0.18, 0.18, tray, root); }
      for (const s of [-1, 1]) sbar([yx0, 6.5, zb1 + 2.4 + s * 0.45], [yx1, 6.5, zb1 + 2.4 + s * 0.45], 0.05, 0.15, tray, root);
      tbox(yx1 - yx0, 0.05, 0.9, tray, (yx0 + yx1) / 2, 6.4, zb1 + 2.4, root);
      for (let i = 0; i < 18; i++) { const x = yx0 + 0.3; bar([yx0 - 1.2 + i * 0.0, 0.1, zb1 + 12], [yx0 - 1.2, 1.0, zb1 + 12], 0.1, paint(0xd8b24a, 0.5, 0.2), root, 10); break; }
      for (let x = yx0 - 1.5; x < yx1 + 2; x += 3.5) cyl(0.11, 0.11, 1.1, paint(0xd8b24a, 0.5, 0.2), x, 0, zb1 + yardD + 0.3, 12, root);
      // bulk fuel: two double wall horizontal tanks on saddles, a containment curb, a stair
      for (let t = 0; t < 2; t++) {
        const tx = -L / 2 - 7 - t * 5.5, tz = zb1 + 9, tl = 13, tr = 1.6;
        const tm = paint(0xe6e4dc, 0.4, 0.3);
        hcyl(tr, tl, tm, tx, 1.0 + tr, tz, 'z', 36, root);
        for (const e of [-1, 1]) { const cap = new THREE.Mesh(new THREE.SphereGeometry(tr, 36, 12, 0, TAU, 0, Math.PI * 0.18), tm);
          cap.scale.set(1, 1, 1); cap.rotation.x = e * Math.PI / 2; cap.position.set(tx, 1.0 + tr, tz + e * (tl / 2 - tr * 0.95)); root.add(cap); }
        for (const e of [-0.32, 0.32]) tbox(2.6, 1.0 + tr * 0.4, 0.4, concrete(), tx, 0, tz + e * tl, root, 3);
        cyl(0.3, 0.3, 0.5, tm, tx, 1.0 + tr * 2 - 0.1, tz - 3, 16, root);
        pipe([[tx + 0.5, 1 + tr * 2, tz + 3], [tx + 0.5, 1 + tr * 2 + 1.2, tz + 3]], 0.05, galv(), root);
      }
      tbox(15, 0.6, 18, concrete('#a5a198'), -L / 2 - 9.7, 0, zb1 + 9, root, 3);
      stair(root, [-L / 2 - 2.2, 0.6, zb1 + 0.6], [-L / 2 - 2.2, 4.2, zb1 + 5.2], 0.9, galv());
      // a guard booth at the gate
      const gx = L / 2 - 12, gz = zb1 + yardD + frontM - 3;
      tbox(3, 2.8, 2.4, paint(col, 0.5, 0.3), gx + 9, 0, gz - 2, root, 0, 0.03);
      for (const s of [-1, 1]) wallPlane(2.2, 1.2, glass(), gx + 9 + s * 0.0, 1.1, gz - 2 + 1.21, 0, root);
      tbox(3.4, 0.2, 2.8, paint(accent, 0.45, 0.4), gx + 9, 2.8, gz - 2, root);
      // light poles along the yard
      for (let x = yx0 + 10; x < yx1; x += 36) {
        cyl(0.1, 0.14, 11, galv(), x, 0, zb1 + yardD + 2, 10, root);
        cbox(0.7, 0.18, 0.45, darkSteel(), x, 11.05, zb1 + yardD + 1.7, root);
        cbox(0.6, 0.02, 0.36, lamp(0xfff0cf, 0.8), x, 10.95, zb1 + yardD + 1.7, root);
      }
      // the perimeter fence with a gate gap on the drive
      if (o.fence) {
        const fx = L / 2 + sideM - 1, fz0 = -Dt / 2 + 1, fz1 = Dt / 2 - 1, fh = 2.4;
        const gap0 = L / 2 - 20, gap1 = L / 2 - 4;
        const f = grp(root);
        fenceRun(f, [-fx, fz1], [gap0, fz1], fh, true);
        fenceRun(f, [gap1, fz1], [fx, fz1], fh, true);
        fenceRun(f, [fx, fz1], [fx, fz0], fh, true);
        fenceRun(f, [fx, fz0], [-fx, fz0], fh, true);
        fenceRun(f, [-fx, fz0], [-fx, fz1], fh, true);
        for (const gxp of [gap0, gap1]) cyl(0.09, 0.09, 2.9, galv(), gxp, 0, fz1, 10, f);
      }
      const out = bake(root);
      emit(parts, out);
      return out;
    },
  });

  /* ======================================================================================
   * COOLING TOWER, mechanical draft crossflow: a row of cells on a concrete cold water basin,
   * louvred air inlets down both long faces, FRP casing, hot water basin covers along the deck
   * edges, a flared fan stack per cell with its fan inside, handrails, a switchback stair.
   * ==================================================================================== */
  K.define('cooling_tower', {
    size: [48.5, 13.6, 15.3],
    options: { cells: 4, cell: 11, color: null },
    note: 'Mechanical draft crossflow cooling tower: cells in a row along x, louvred inlets on +z and -z, FRP casing, fan stacks with fans, deck rails, stair on +x.',
    make(o, r) {
      const root = new THREE.Group();
      const n = clamp(Math.round(o.cells), 1, 12), c = o.cell, L = n * c, W = 12.5, Hd = 9.6, bH = 1.0;
      const col = o.color != null ? o.color : pick(r, [0xb9bec0, 0xc9c2b0, 0x9aa7ad, 0xc0c4bd]);
      const frp = lmat('frp' + col, () => new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.6, metalness: 0.05,
        map: K.tex('corrugated', { color: '#' + col.toString(16).padStart(6, '0') }) }));
      const stackM = paint(col, 0.55, 0.05), steel = paint(0xd4ad2c, 0.5, 0.25);
      tbox(L + 1.6, bH, W + 1.6, concrete('#a8a49b'), 0, 0, 0, root, 3);
      tbox(L + 1.3, 0.05, W + 1.3, std('water', { color: 0x2b3a3c, metalness: 0.2, roughness: 0.08 }), 0, bH - 0.3, 0, root);
      const inH = 4.6;
      for (const s of [-1, 1]) {
        wallPlane(L, inH, louvreMat(0x8e9496, 'ct'), 0, bH + 0.1, s * W / 2, s > 0 ? 0 : Math.PI, root, 0.7);
        const up = tbox(L, Hd - bH - inH - 0.1, 0.12, frp, 0, bH + inH + 0.1, s * W / 2, root);
        K.uvBox(up.geometry, 1);
        for (let i = 0; i <= n; i++) tbox(0.3, Hd - bH, 0.3, stackM, -L / 2 + i * c, bH, s * (W / 2 + 0.1), root);
        tbox(L, 0.2, 0.2, stackM, 0, bH + inH, s * (W / 2 + 0.08), root);
        for (let i = 0; i < n; i++) for (const f of [1 / 3, 2 / 3]) tbox(0.1, inH, 0.12, stackM, -L / 2 + (i + f) * c, bH + 0.1, s * (W / 2 + 0.06), root);
      }
      for (const s of [-1, 1]) { const e = tbox(0.12, Hd - bH, W, frp, s * L / 2, bH, 0, root); K.uvBox(e.geometry, 1); }
      tbox(L + 0.4, 0.3, W + 0.4, paint(0x6d7275, 0.7, 0.2), 0, Hd, 0, root);
      // hot water basin covers along the deck edges, a header with a valve into each cell
      for (const s of [-1, 1]) for (let i = 0; i < n; i++) tbox(c - 0.4, 0.35, 1.5, frp, -L / 2 + (i + 0.5) * c, Hd + 0.3, s * (W / 2 - 1.0), root);
      const pm = std('ctpipe', { color: 0x3f5f78, metalness: 0.35, roughness: 0.45 });
      pipe([[-L / 2 - 1.2, 0, -W / 2 - 1.4], [-L / 2 - 1.2, Hd + 1.5, -W / 2 - 1.4], [L / 2 - 2, Hd + 1.5, -W / 2 - 1.4]], 0.45, pm, root);
      for (let i = 0; i < n; i++) {
        const x = -L / 2 + (i + 0.5) * c;
        pipe([[x, Hd + 1.5, -W / 2 - 1.4], [x, Hd + 1.5, -W / 2 + 0.2], [x, Hd + 0.7, -W / 2 + 0.2]], 0.3, pm, root);
        valve(0.3, x + 1.2, Hd + 1.5, -W / 2 - 1.4, 'x', pm, std('vwheel', { color: 0xc03a2b, roughness: 0.5 }), root);
      }
      for (let x = -L / 2 + 2; x < L / 2 - 1; x += 8) bar([x, 0, -W / 2 - 1.4], [x, Hd + 1.05, -W / 2 - 1.4], 0.15, steel, root, 8);
      // fan stacks: a flared velocity recovery cylinder, ribs, a fan inside
      const fr = Math.min(c, W) * 0.36;
      for (let i = 0; i < n; i++) {
        const x = -L / 2 + (i + 0.5) * c, y0 = Hd + 0.3;
        const prof = [[fr + 0.05, 0], [fr + 0.05, 0.3], [fr - 0.05, 1.3], [fr + 0.1, 2.6], [fr + 0.5, 3.4], [fr + 0.6, 3.5]];
        const pts = prof.map((p) => new THREE.Vector2(p[0], p[1])), g = new THREE.LatheGeometry(pts, 48);
        const st = new THREE.Mesh(g, lmat('stackDS' + col, () => { const m = stackM.clone(); m.side = THREE.DoubleSide; return m; }));
        st.position.set(x, y0, 0); root.add(st);
        for (let k = 0; k < 16; k++) { const a = k * TAU / 16;
          sbar([x + Math.cos(a) * (fr + 0.1), y0, Math.sin(a) * (fr + 0.1)], [x + Math.cos(a) * (fr + 0.66), y0 + 3.45, Math.sin(a) * (fr + 0.66)], 0.08, 0.14, stackM, root, -a); }
        const disc = new THREE.Mesh(new THREE.CircleGeometry(fr, 40), hole()); disc.rotation.x = -Math.PI / 2; disc.position.set(x, y0 + 0.2, 0); root.add(disc);
        cyl(0.5, 0.6, 0.6, darkSteel(), x, y0 + 0.5, 0, 16, root);
        for (let b = 0; b < 8; b++) {
          const bl = cbox(fr - 0.7, 0.05, 0.7, std('ctblade', { color: 0x566067, metalness: 0.3, roughness: 0.45 }), 0, 0, 0);
          bl.geometry.translate((fr - 0.7) / 2 + 0.55, 0, 0);
          bl.position.set(x, y0 + 0.9, 0); bl.rotation.set(0, b * TAU / 8 + i, 0); bl.rotateX(0.25); root.add(bl);
        }
        sbar([x - fr, y0 + 1.1, 0], [x + fr, y0 + 1.1, 0], 0.2, 0.3, darkSteel(), root);
        tbox(1.4, 0.8, 1.0, paint(0x4b5d6a, 0.5, 0.3), x + fr + 1.3, Hd + 0.3, 0, root, 0, 0.03);   // gearbox motor
      }
      railing(root, [[-L / 2, Hd + 0.3, -W / 2], [L / 2, Hd + 0.3, -W / 2], [L / 2, Hd + 0.3, W / 2], [-L / 2, Hd + 0.3, W / 2], [-L / 2, Hd + 0.3, -W / 2]], 1.07, steel, 2.0);
      // switchback stair on +x
      const sx = L / 2 + 0.2, hh = (Hd + 0.3) / 2, run = hh / Math.tan(40 * D2R);
      stair(root, [sx + 0.7, 0, W / 2 - 0.6], [sx + 0.7, hh, W / 2 - 0.6 - run], 0.9, steel);
      tbox(2.6, 0.08, 1.4, galv(), sx + 1.3, hh - 0.08, W / 2 - 1.3 - run, root);
      stair(root, [sx + 1.9, hh, W / 2 - 1.3 - run - 0.1 + 0.8 - 0.8], [sx + 1.9, Hd + 0.3, W / 2 - 1.3], 0.9, steel);
      tbox(2.6, 0.08, 1.4, galv(), sx + 1.3, Hd + 0.22, W / 2 - 0.6, root);
      for (const [px, pz, py] of [[sx + 2.5, W / 2 - 0.7 - run - 1.2, hh], [sx + 2.5, W / 2 - 0.1, Hd + 0.3]]) bar([px, 0, pz], [px, py, pz], 0.06, steel, root, 8);
      railing(root, [[sx + 2.6, hh, W / 2 - 0.6 - run], [sx + 2.6, hh, W / 2 - 2.0 - run], [sx, hh, W / 2 - 2.0 - run]], 1.07, steel);
      return bake(root);
    },
  });

  /* ======================================================================================
   * HYPERBOLIC COOLING TOWER, natural draft: a reinforced concrete hyperboloid shell with its
   * throat at about 78 percent of the height, raker columns in a lattice of Vs under the shell,
   * the ring beam, a cold water basin, the fill showing dark through the columns.
   * ==================================================================================== */
  function streakTex() {
    return ctex('streak', 512, 512, (x, w, h) => {
      const r = K.rng(4242);
      x.fillStyle = '#b8b3a8'; x.fillRect(0, 0, w, h);
      for (let j = 0; j < h; j += 32) { x.fillStyle = 'rgba(0,0,0,0.05)'; x.fillRect(0, j, w, 2); x.fillStyle = 'rgba(255,255,255,0.04)'; x.fillRect(0, j + 2, w, 2); }
      for (let i = 0; i < 220; i++) {
        const sx = r() * w, len = 40 + r() * 460, a = 0.03 + r() * 0.12, sw = 1 + r() * 7;
        const g = x.createLinearGradient(0, 0, 0, len); g.addColorStop(0, 'rgba(40,36,30,' + a + ')'); g.addColorStop(1, 'rgba(40,36,30,0)');
        x.fillStyle = g; x.save(); x.translate(sx, r() * h); x.fillRect(0, 0, sw, len); x.translate(0, -h); x.fillRect(0, 0, sw, len); x.restore();
      }
      speckle(x, w, h, 17, 0.06);
    });
  }
  K.define('hyperbolic_cooling_tower', {
    size: [125, 150.7, 125],
    options: { height: 150, plume: false },
    note: 'Natural draft hyperbolic cooling tower in weathered concrete, 120 m and up (default 150): hyperboloid shell, V raker columns, basin, dark fill inside. plume:true adds a soft vapour plume.',
    make(o, r) {
      const root = new THREE.Group();
      const Ht = Math.max(100, o.height), a = 0.23 * Ht, Rb = 0.39 * Ht, y0 = 0.78 * Ht, ys = 0.072 * Ht;
      const b = (y0 - ys) / Math.sqrt((Rb / a) ** 2 - 1);
      const rad = (y) => a * Math.sqrt(1 + ((y - y0) / b) ** 2);
      const t = 0.45, N = 60, prof = [];
      for (let i = 0; i <= N; i++) { const y = ys + (Ht - ys) * i / N; prof.push([rad(y) + (i === 0 ? 0.9 : 0), y]); }
      const lip = [[rad(Ht) + 0.9, Ht - 1.6], [rad(Ht) + 0.9, Ht], [rad(Ht) - t - 0.2, Ht]];
      const outerPts = prof.slice(0, N).concat(lip);
      const innerPts = prof.slice().reverse().map((p) => [p[0] - t, p[1]]);
      const shellM = lmat('shellConc', () => new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.93, map: streakTex() }));
      const innerM = std('shellIn', { color: 0x4a4740, roughness: 0.95 });
      const seg = 144;
      function lathe(pts, mat, flip) {
        const g = new THREE.LatheGeometry(pts.map((p) => new THREE.Vector2(p[0], p[1])), seg);
        const uv = g.attributes.uv, pos = g.attributes.position;
        for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * TAU * Rb * 0.72 / 24, pos.getY(i) / 24);
        const m = new THREE.Mesh(g, mat); if (flip) m.material = mat; root.add(m); return m;
      }
      lathe(outerPts, shellM);
      lathe(innerPts.concat([[rad(ys) - t, ys]]), lmat('shellInDS', () => { const m = innerM.clone(); m.side = THREE.BackSide; return m; }));
      // ring beam and raker columns: pairs leaning both ways form the V lattice
      const rb = new THREE.Mesh(new THREE.TorusGeometry(rad(ys) - t / 2, 0.9, 8, seg), concrete('#a8a399')); rb.rotation.x = Math.PI / 2; rb.position.y = ys; root.add(rb);
      const nc = 44, colM = concrete('#a39e94');
      for (let i = 0; i < nc; i++) {
        const ang = i * TAU / nc, top = rad(ys) - t / 2, bot = Rb + 1.2, d = Math.PI / nc;
        for (const s of [-1, 1]) {
          const a0 = ang, a1 = ang + s * d;
          bar([Math.cos(a0) * bot, 0, Math.sin(a0) * bot], [Math.cos(a1) * top, ys, Math.sin(a1) * top], 0.45, colM, root, 8);
        }
        cyl(0.9, 1.1, 0.6, colM, Math.cos(ang) * bot, 0, Math.sin(ang) * bot, 8, root);
      }
      // basin wall, water, the fill deck and its supports inside
      const bw = new THREE.Mesh(new THREE.CylinderGeometry(Rb + 4, Rb + 4, 1.4, seg, 1, true), concrete('#a8a49b'));
      bw.position.y = 0.7; root.add(bw);
      const wr = new THREE.Mesh(new THREE.RingGeometry(Rb + 3.6, Rb + 4, seg), concrete('#a8a49b')); wr.rotation.x = -Math.PI / 2; wr.position.y = 1.4; root.add(wr);
      const water = new THREE.Mesh(new THREE.CircleGeometry(Rb + 3.6, seg), std('ctwater', { color: 0x2c3a3b, metalness: 0.3, roughness: 0.06 }));
      water.rotation.x = -Math.PI / 2; water.position.y = 0.9; root.add(water);
      cyl(rad(ys + 3) - 1, rad(ys + 3) - 1, 3.2, std('fill', { color: 0x1f2120, roughness: 1 }), 0, ys - 1.5, 0, 72, root);
      for (let i = 0; i < 36; i++) { const ang = i * TAU / 36 + 0.05, rr0 = rad(ys) * 0.85;
        cyl(0.35, 0.35, ys - 1.5, colM, Math.cos(ang) * rr0, 0, Math.sin(ang) * rr0, 6, root); }
      // aircraft warning lamps and a service ladder track up the outside
      for (let i = 0; i < 4; i++) { const ang = i * TAU / 4 + 0.4, R = rad(Ht) + 1.0;
        cbox(0.4, 0.5, 0.4, lamp(0xff2a1a, 3), Math.cos(ang) * R, Ht + 0.25, Math.sin(ang) * R, root); }
      if (o.plume) {
        const pm = lmat('plume', () => new THREE.MeshStandardMaterial({ color: 0xf2f0ec, roughness: 1, transparent: true, opacity: 0.2, depthWrite: false }));
        for (let i = 0; i < 70; i++) {
          const k = i / 70, rr1 = rad(Ht) * (0.55 + k * 0.9) * (0.6 + r() * 0.5);
          const s = new THREE.Mesh(new THREE.IcosahedronGeometry(rr1, 2), pm);
          s.position.set((r() - 0.3) * rad(Ht) * 0.6 + k * Ht * 0.9, Ht + 6 + k * Ht * 0.55 + (r() - 0.5) * 12, (r() - 0.5) * rad(Ht) * 0.8);
          s.scale.set(1, 0.7, 1); s.userData.keep = true; s.castShadow = false; root.add(s);
        }
      }
      return bake(root);
    },
  });

  /* ======================================================================================
   * WATER TOWER. The Texas elevated tank. 'legs': a spheroid tank on six battered tubular legs
   * with struts and rod bracing, a central riser, a balcony, a conical roof with finial.
   * 'pedestal': a fluted steel column carrying a bowl. The town band is painted on the tank.
   * ==================================================================================== */
  function nameTex(name, star, ink, paintC) {
    return ctex('wtname|' + name + '|' + star + '|' + ink + '|' + paintC, 2048, 256, (x, w, h) => {
      x.fillStyle = rgb(paintC, 1); x.fillRect(0, 0, w, h);
      speckle(x, w, h, 23, 0.03);
      const inkS = rgb(ink, 1);
      for (const cx of [0, w * 0.5, w]) {                      // back (wrapping at the seam) and front
        let tw = 0;
        if (name) tw = strokeText(x, name, cx + (star ? 60 : 0), h * 0.5, h * 0.44, inkS, 1.35);
        if (star) { starPath(x, cx + (name ? 60 - tw / 2 - 125 : 0), h * 0.5, h * 0.3); x.fillStyle = inkS; x.fill(); }
      }
    });
  }
  const TX_COLOURS = [0xe9eae6, 0xdfe7ec, 0xd9e3e8, 0xefe9da, 0xc9dbe6];
  K.define('water_tower', {
    size: [18.8, 41.2, 21.4],
    options: { style: 'legs', name: 'TEXAS', star: true, color: null, ink: 0x1e3a6b, antennas: true },
    note: 'Texas elevated water tank, 45 m. style "legs" (spheroid on six legs, balcony, riser) or "pedestal" (fluted column and bowl). name paints the town band front and back ("" for none), star adds a lone star.',
    make(o, r) {
      const root = new THREE.Group();
      const col = o.color != null ? o.color : pick(r, TX_COLOURS);
      const pm = paint(col, 0.42, 0.2);
      const band = (o.name || o.star) ? lmat('wtband' + o.name + o.star + col + o.ink, () => new THREE.MeshStandardMaterial({
        color: 0xffffff, roughness: 0.42, metalness: 0.2, map: nameTex(o.name || '', !!o.star, o.ink, col) })) : pm;
      const legs = o.style !== 'pedestal';
      let yT, R, shellH;
      function tankLathe(prof, mat, phiStart) {
        const g = new THREE.LatheGeometry(prof.map((p) => new THREE.Vector2(p[0], p[1])), 96, phiStart || 0);
        const m = new THREE.Mesh(g, mat); root.add(m); return m;
      }
      if (legs) {
        yT = 32; R = 7.8; shellH = 3.2;
        const bot = [], top = [];
        for (let i = 0; i <= 16; i++) { const a = -Math.PI / 2 + (i / 16) * Math.PI / 2; bot.push([Math.cos(a) * R + 0.001, yT + Math.sin(a) * 5.2]); }
        tankLathe(bot, pm);
        // the shell band carries the lettering; u = 0.5 faces +z with phiStart = pi
        const sh = new THREE.LatheGeometry([new THREE.Vector2(R, yT), new THREE.Vector2(R, yT + shellH)], 128, Math.PI);
        root.add(new THREE.Mesh(sh, band));
        for (let i = 0; i <= 12; i++) { const a = (i / 12) * Math.PI / 2; top.push([Math.cos(a) * R + 0.001, yT + shellH + Math.sin(a) * 3.6]); }
        tankLathe(top, pm);
        cyl(0.35, 0.5, 0.9, pm, 0, yT + shellH + 3.5, 0, 16, root);
        cyl(0.55, 0.55, 0.08, pm, 0, yT + shellH + 4.35, 0, 16, root);
        cyl(0.04, 0.04, 1.6, galv(), 0, yT + shellH + 4.4, 0, 6, root);
        // legs: six, battered in from 9.5 m at grade to the shell at R
        const nL = 6, legs0 = [], legM = pm;
        for (let i = 0; i < nL; i++) {
          const a = i * TAU / nL + Math.PI / 6, b0 = [Math.cos(a) * 9.6, 0, Math.sin(a) * 9.6], b1 = [Math.cos(a) * (R - 0.1), yT, Math.sin(a) * (R - 0.1)];
          bar(b0, b1, 0.42, legM, root, 16); legs0.push([b0, b1]);
          cyl(0.9, 1.1, 0.6, concrete(), b0[0], 0, b0[2], 12, root);
        }
        const at = (i, t) => { const [p, q] = legs0[i % nL]; return [p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, p[2] + (q[2] - p[2]) * t]; };
        const tiers = [0, 0.36, 0.7, 1.0];
        for (let k = 1; k < tiers.length; k++) for (let i = 0; i < nL; i++) {
          if (k < tiers.length - 1) bar(at(i, tiers[k]), at(i + 1, tiers[k]), 0.16, legM, root, 10);
          bar(at(i, tiers[k - 1] + (k === 1 ? 0.02 : 0)), at(i + 1, tiers[k] - 0.02), 0.03, galv(), root, 5);
          bar(at(i + 1, tiers[k - 1] + (k === 1 ? 0.02 : 0)), at(i, tiers[k] - 0.02), 0.03, galv(), root, 5);
        }
        cyl(0.9, 0.9, yT - 4.8, pm, 0, 0, 0, 24, root);                                   // central riser
        cyl(1.4, 1.4, 1.2, concrete(), 0, 0, 0, 20, root);
        // balcony at the shell's foot: deck ring, rail, brackets
        const deck = new THREE.Mesh(new THREE.RingGeometry(R, R + 0.9, 96), galv()); deck.rotation.x = -Math.PI / 2; deck.position.y = yT - 0.05; root.add(deck);
        const rail = [], rr2 = R + 0.88;
        for (let i = 0; i <= 48; i++) { const a = i * TAU / 48; rail.push([Math.cos(a) * rr2, yT - 0.05, Math.sin(a) * rr2]); }
        railing(root, rail, 1.07, galv(), 1.5, 0.02);
        for (let i = 0; i < 24; i++) { const a = i * TAU / 24; sbar([Math.cos(a) * R, yT - 0.9, Math.sin(a) * R], [Math.cos(a) * (R + 0.85), yT - 0.08, Math.sin(a) * (R + 0.85)], 0.05, 0.05, galv(), root); }
        // ladder up one leg to the balcony, and over the roof
        const la = legs0[1];
        ladder(root, (la[0][0] + la[1][0]) / 2 * 0.9, 2.5, yT - 0.2, (la[0][2] + la[1][2]) / 2 * 0.9, galv(), true, Math.atan2(la[0][0], la[0][2]));
      } else {
        // pedestal: fluted column 6.4 m across, flaring into a bowl
        yT = 30; R = 10.5; shellH = 4.2;
        const colH = 26, cr = 3.2, fl = 24;
        const cg = new THREE.CylinderGeometry(cr, cr * 1.18, colH, fl * 8, 8, true);
        const pos = cg.attributes.position;
        for (let i = 0; i < pos.count; i++) {
          const x = pos.getX(i), z = pos.getZ(i), ang = Math.atan2(z, x), k = 1 - 0.045 * Math.pow(Math.abs(Math.cos(ang * fl / 2)), 0.6);
          pos.setX(i, x * k); pos.setZ(i, z * k);
        }
        cg.computeVertexNormals();
        const cm = new THREE.Mesh(cg, pm); cm.position.y = colH / 2; root.add(cm);
        cyl(cr * 1.3, cr * 1.3, 0.5, concrete(), 0, 0, 0, 32, root);
        tbox(1.0, 2.2, 0.3, paint(0x5a5f63, 0.5, 0.3), 0, 0.3, cr * 1.13, root, 0, 0.02);     // access door
        const cone = []; for (let i = 0; i <= 14; i++) { const t = i / 14; cone.push([cr + (R - cr) * Math.pow(t, 0.85), colH + (yT - colH) * t + 0.4 * Math.sin(t * Math.PI)]); }
        tankLathe(cone, pm);
        const sh = new THREE.LatheGeometry([new THREE.Vector2(R, yT), new THREE.Vector2(R, yT + shellH)], 128, Math.PI);
        root.add(new THREE.Mesh(sh, band));
        const roof = []; for (let i = 0; i <= 10; i++) { const t = i / 10; roof.push([R * (1 - t) + 0.001, yT + shellH + 2.2 * Math.sin(t * Math.PI / 2)]); }
        tankLathe(roof, pm);
        const rail = []; for (let i = 0; i <= 24; i++) { const a = i * TAU / 24; rail.push([Math.cos(a) * 2.4, yT + shellH + 2.1, Math.sin(a) * 2.4]); }
        railing(root, rail, 1.07, galv(), 1.5, 0.02);
        cyl(0.5, 0.5, 0.8, pm, 0, yT + shellH + 2.1, 0, 16, root);
      }
      // antennas: sector panels on a ring near the top, cable runs
      if (o.antennas && r() < 0.8) {
        const ay = legs ? yT + shellH + 0.6 : yT + shellH + 0.2, aR = legs ? R - 0.6 : R - 1.2;
        for (let i = 0; i < 9; i++) {
          const a = (Math.floor(i / 3) * TAU / 3) + (i % 3 - 1) * 0.12 + 0.5;
          const m = tbox(0.3, 1.8, 0.12, std('antenna', { color: 0xdcdcd6, roughness: 0.6 }), Math.cos(a) * aR, ay, Math.sin(a) * aR, root, 0, 0.03);
          m.rotation.y = -a + Math.PI / 2;
        }
      }
      return bake(root);
    },
  });

  /* ======================================================================================
   * PUMP JACK. A conventional (Class I) beam pumping unit, about a 228 size with an 86 to 100
   * inch stroke: skid, four leg samson post, walking beam, horsehead whose face is an arc
   * centred on the saddle bearing, bridle and carrier bar, polished rod into the stuffing box,
   * equalizer and pitman arms, crank arms with counterweights, gear reducer, belt guard,
   * electric prime mover. `crank` in degrees poses it; the beam is solved from the linkage.
   * ==================================================================================== */
  K.define('pump_jack', {
    size: [12, 7.4, 3],
    options: { crank: 40, color: null, head: null, guard: null },
    note: 'Conventional beam pumping unit, true linkage: crank (degrees) poses crank, pitmans, beam, horsehead, bridle and polished rod together. Well on +x, prime mover on -x, side profile faces +z.',
    make(o, r) {
      const root = new THREE.Group();
      const col = o.color != null ? o.color : pick(r, [0x5e6b52, 0x3e5b74, 0x7e8488, 0x8e3a2c, 0x33404b, 0x6c6a4a]);
      const headC = o.head != null ? o.head : (r() < 0.45 ? col : pick(r, [0x1f2224, 0xd6a824, 0xa33b28]));
      const P = paint(col, 0.55, 0.35), HP = paint(headC, 0.5, 0.35), steel = darkSteel();
      const ox = -0.6;                                           // shifts the unit so the footprint centres
      const S = [1.2 + ox, 6.3], A = 3.8, C = 3.0, E = 0.4, Kc = [-1.9 + ox, 2.2], Rk = 1.05;
      const xw = S[0] + A;
      const tailAt = (phi) => [S[0] + Math.cos(phi) * -C - Math.sin(phi) * -E, S[1] + Math.sin(phi) * -C + Math.cos(phi) * -E];
      const T0 = tailAt(0), Lp = Math.hypot(T0[0] - Kc[0], T0[1] - Kc[1]);
      const th = (o.crank || 0) * D2R, pin = [Kc[0] + Rk * Math.cos(th), Kc[1] + Rk * Math.sin(th)];
      const f = (phi) => { const t = tailAt(phi); return Math.hypot(t[0] - pin[0], t[1] - pin[1]) - Lp; };
      let lo = -0.6, hi = 0.6;
      for (let i = 0; i < 50; i++) { const m = (lo + hi) / 2; if (f(lo) * f(m) <= 0) hi = m; else lo = m; }
      const phi = (lo + hi) / 2, T = tailAt(phi);
      // pad and skid: two I beam rails with cross members
      tbox(9.4, 0.25, 3.0, concrete('#aba79e'), -1.0 + ox, 0, 0, root, 3);
      const ib = (x0, x1, z, h, w) => {
        tbox(x1 - x0, 0.03, w, P, (x0 + x1) / 2, 0.25, z, root); tbox(x1 - x0, 0.03, w, P, (x0 + x1) / 2, 0.25 + h - 0.03, z, root);
        tbox(x1 - x0, h - 0.06, 0.02, P, (x0 + x1) / 2, 0.28, z, root);
      };
      for (const z of [-0.75, 0.75]) ib(-5.4 + ox, 3.0 + ox, z, 0.36, 0.22);
      for (let x = -5.2 + ox; x <= 2.9 + ox; x += 1.35) tbox(0.16, 0.3, 1.3, P, x, 0.28, 0, root);
      // samson post: four legs, bracing, the ladder and a small platform
      const top = [S[0], S[1] - 0.55];
      const legs = [[S[0] + 1.1, 0.61, 0.95], [S[0] + 1.1, 0.61, -0.95], [S[0] - 1.55, 0.61, 0.9], [S[0] - 1.55, 0.61, -0.9]];
      legs.forEach((l) => sbar([l[0], l[1], l[2]], [top[0] + (l[0] > S[0] ? 0.12 : -0.12), top[1], Math.sign(l[2]) * 0.26], 0.2, 0.2, P, root));
      for (const t of [0.35, 0.65]) {
        const at = (l) => [l[0] + (top[0] - l[0]) * t, l[1] + (top[1] - l[1]) * t, l[2] + (Math.sign(l[2]) * 0.26 - l[2]) * t];
        sbar(at(legs[0]), at(legs[1]), 0.08, 0.08, P, root); sbar(at(legs[2]), at(legs[3]), 0.08, 0.08, P, root);
        sbar(at(legs[0]), at(legs[2]), 0.07, 0.07, P, root); sbar(at(legs[1]), at(legs[3]), 0.07, 0.07, P, root);
      }
      tbox(0.7, 0.35, 0.8, P, top[0], top[1] - 0.1, 0, root, 0, 0.02);                // saddle bearing block
      ladder(root, S[0] + 0.62, 0.61, top[1] - 0.6, 1.02, galv(), false, Math.PI / 2 - 0.28);
      // the walking beam group, rotated about the saddle
      const beam = grp(root); beam.position.set(S[0], S[1], 0); beam.rotation.z = phi;
      const bl0 = -C - 0.35, bl1 = A - 0.9, bh = 0.85;
      tbox(bl1 - bl0, 0.045, 0.34, P, (bl0 + bl1) / 2, bh / 2 - 0.045, 0, beam); tbox(bl1 - bl0, 0.045, 0.34, P, (bl0 + bl1) / 2, -bh / 2, 0, beam);
      tbox(bl1 - bl0, bh - 0.09, 0.025, P, (bl0 + bl1) / 2, -bh / 2 + 0.045, 0, beam);
      for (let x = bl0 + 0.4; x < bl1; x += 0.9) for (const s of [-1, 1]) cbox(0.02, bh - 0.1, 0.15, P, x, 0, s * 0.085, beam);
      hcyl(0.22, 0.6, steel, 0, -bh / 2 - 0.12, 0, 'z', 20, beam);                    // centre bearing
      // equalizer and tail bearing
      hcyl(0.18, 0.5, steel, -C, -E, 0, 'z', 18, beam);
      tbox(0.45, 0.28, 1.85, P, -C, -E - 0.2, 0, beam, 0, 0.02);
      // horsehead: an arc face of radius A about the saddle, from +13 deg to -32 deg
      const hs = new THREE.Shape(), a1 = 13 * D2R, a2 = -32 * D2R;
      hs.moveTo(A - 1.45, bh / 2);
      for (let i = 0; i <= 24; i++) { const a = a1 + (a2 - a1) * i / 24; hs.lineTo(Math.cos(a) * A, Math.sin(a) * A); }
      hs.quadraticCurveTo(A - 1.0, -1.35, A - 1.45, -bh / 2);
      hs.lineTo(A - 1.45, bh / 2);
      const hg = new THREE.ExtrudeGeometry(hs, { depth: 0.46, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.03, bevelSegments: 2, curveSegments: 12 });
      hg.translate(0, 0, -0.23);
      beam.add(new THREE.Mesh(hg, HP));
      // the face plate with its rope grooves (two flanges proud of the face)
      for (const s of [-1, 0, 1]) {
        const pts = []; for (let i = 0; i <= 24; i++) { const a = a1 + (a2 - a1) * i / 24; pts.push(new THREE.Vector2(Math.cos(a) * (A + (s ? 0.06 : 0.015)), Math.sin(a) * (A + (s ? 0.06 : 0.015)))); }
        const fs = new THREE.Shape(pts.concat(pts.slice().reverse().map((p) => p.clone().multiplyScalar((A - 0.03) / p.length()))));
        const fg = new THREE.ExtrudeGeometry(fs, { depth: s ? 0.025 : 0.55, bevelEnabled: false, curveSegments: 4 });
        fg.translate(0, 0, s ? s * 0.27 - 0.0125 : -0.275);
        beam.add(new THREE.Mesh(fg, HP));
      }
      tbox(0.4, 0.5, 0.5, HP, A - 1.7, -0.25, 0, beam, 0, 0.02);                    // head latch
      // bridle: two wire ropes over the face, dropping plumb at xw
      const wire = std('wire', { color: 0x6a6c6c, metalness: 0.8, roughness: 0.4 });
      const hang0 = S[1] - 2.35, wrapped = A * (a1 + phi), Lrope = (S[1] - hang0) + A * a1;
      const carrierY = S[1] - (Lrope - wrapped);
      for (const z of [-0.14, 0.14]) {
        const pts = [];
        for (let i = 0; i <= 10; i++) { const a = (a1 + phi) - (a1 + phi) * i / 10; pts.push([S[0] + Math.cos(a) * (A + 0.03), S[1] + Math.sin(a) * (A + 0.03), z]); }
        pts.push([xw + 0.03, carrierY + 0.12, z]);
        pipe(pts, 0.013, wire, root);
      }
      tbox(0.16, 0.12, 0.5, steel, xw, carrierY, 0, root, 0, 0.01);                   // carrier bar
      cyl(0.05, 0.05, 0.12, steel, xw, carrierY + 0.12, 0, 12, root);                  // rod clamp
      cyl(0.019, 0.019, carrierY + 0.4 - 1.25, chrome(), xw, 1.25, 0, 12, root);     // polished rod
      // wellhead: casing head, tubing spool, pumping tee, stuffing box, flowline
      const wh = std('wellhead', { color: 0x6d7275, metalness: 0.5, roughness: 0.5 });
      tbox(1.4, 0.1, 1.4, concrete(), xw, 0, 0, root, 3);
      cyl(0.17, 0.17, 0.45, wh, xw, 0, 0, 20, root); flange(0.26, xw, 0.45, 0, 'y', wh, root);
      cyl(0.12, 0.12, 0.35, wh, xw, 0.47, 0, 20, root); flange(0.2, xw, 0.82, 0, 'y', wh, root);
      cyl(0.08, 0.08, 0.25, wh, xw, 0.84, 0, 16, root);
      hcyl(0.075, 0.5, wh, xw, 0.98, 0.22, 'z', 16, root);
      valve(0.075, xw, 0.98, 0.55, 'z', wh, std('vwheel', { color: 0xc03a2b, roughness: 0.5 }), root);
      pipe([[xw, 0.98, 0.7], [xw, 0.98, 1.4], [xw, 0.15, 1.4], [xw - 3, 0.15, 1.4]], 0.05, wh, root);
      cyl(0.09, 0.07, 0.18, wh, xw, 1.09, 0, 16, root);
      for (const s of [-1, 1]) bar([xw, 1.18, 0], [xw + s * 0.2, 1.18, 0], 0.012, wh, root, 6);
      cyl(0.075, 0.075, 0.22, wh, xw, 1.12, 0, 16, root);
      // gear reducer on its base, the crank arms and counterweights, the pitmans
      const gx = Kc[0], gy = Kc[1];
      tbox(1.7, gy - 0.9 - 0.61, 1.2, P, gx - 0.2, 0.61, 0, root, 0, 0.02);           // sub base
      const box = tbox(1.9, 1.05, 1.0, P, gx - 0.25, gy - 0.9, 0, root, 0, 0.12);     // reducer housing
      tbox(2.0, 0.08, 1.1, P, gx - 0.25, gy - 0.28, 0, root, 0, 0.02);                // split line flange
      hcyl(0.42, 1.0, P, gx, gy, 0, 'z', 24, root);
      hcyl(0.1, 1.9, steel, gx, gy, 0, 'z', 16, root);                                 // crankshaft
      hcyl(0.3, 0.96, P, gx - 0.95, gy - 0.5, 0, 'z', 20, root);
      for (const s of [-1, 1]) {
        const z = s * 0.72;
        const arm = grp(root); arm.position.set(gx, gy, z); arm.rotation.z = th;
        tbox(Rk + 0.45, 0.34, 0.1, P, (Rk + 0.45) / 2 - 0.2, -0.17, 0, arm, 0, 0.02);
        hcyl(0.16, 0.14, P, 0, 0, 0, 'z', 20, arm);
        // counterweights: two heavy slabs on the arm's outer face, outboard of the shaft
        for (const [x0, w] of [[-0.55, 0.62], [0.1, 0.5]]) {
          const cs = new THREE.Shape();
          cs.moveTo(x0, -0.5); cs.lineTo(x0 + w, -0.42); cs.lineTo(x0 + w, 0.42); cs.lineTo(x0, 0.5); cs.lineTo(x0, -0.5);
          const cg = new THREE.ExtrudeGeometry(cs, { depth: 0.22, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.02, bevelSegments: 1 });
          const m = new THREE.Mesh(cg, P); m.rotation.z = Math.PI; m.position.z = s > 0 ? 0.05 : -0.27; arm.add(m);
        }
        hcyl(0.07, 0.25, steel, Rk, 0, s * 0.08, 'z', 14, arm);                     // wrist pin
        // pitman arm: from the wrist pin up to the equalizer end
        const pz = s * 0.84;
        sbar([pin[0], pin[1], pz], [T[0], T[1] - 0.15, pz], 0.14, 0.2, P, root);
        hcyl(0.1, 0.18, steel, T[0], T[1] - 0.15, pz, 'z', 14, root);
      }
      // brake: drum on the input shaft, lever up the side
      hcyl(0.34, 0.12, steel, gx - 0.95, gy - 0.5, -0.62, 'z', 24, root);
      bar([gx - 1.4, 0.61, -0.95], [gx - 1.25, 2.0, -0.95], 0.03, paint(0xd8b24a, 0.5, 0.2), root, 6);
      // prime mover: a TEFC electric motor on a slide base, belt guard over the V belts
      const mx = -4.55 + ox, my = 0.95;
      tbox(1.3, 0.2, 1.0, P, mx, 0.61, 0, root);
      const mm = std('motor', { color: 0x2f4f6d, metalness: 0.35, roughness: 0.5 });
      hcyl(0.34, 0.8, mm, mx, my + 0.12, -0.05, 'z', 24, root);
      for (let k = 0; k < 14; k++) { const a = k * TAU / 14; cbox(0.05, 0.02, 0.72, mm, mx + Math.cos(a) * 0.36, my + 0.12 + Math.sin(a) * 0.36, -0.05, root, [0, 0, a]); }
      hcyl(0.3, 0.14, mm, mx, my + 0.12, -0.52, 'z', 24, root);
      tbox(0.3, 0.25, 0.2, mm, mx, my + 0.42, 0.1, root, 0, 0.02);
      const gp = [gx - 0.95, gy - 0.5], mp = [mx, my + 0.12];
      const guardC = o.guard != null ? o.guard : (r() < 0.5 ? col : 0xd8a322);
      const bg = new THREE.Shape(), gl = Math.hypot(gp[0] - mp[0], gp[1] - mp[1]), ga = Math.atan2(gp[1] - mp[1], gp[0] - mp[0]);
      bg.absarc(0, 0, 0.32, Math.PI / 2, -Math.PI / 2, false); bg.lineTo(gl, -0.6); bg.absarc(gl, 0, 0.6, -Math.PI / 2, Math.PI / 2, false); bg.lineTo(0, 0.32);
      const bgg = new THREE.ExtrudeGeometry(bg, { depth: 0.22, bevelEnabled: true, bevelThickness: 0.015, bevelSize: 0.015, bevelSegments: 1, curveSegments: 16 });
      const bgm = new THREE.Mesh(bgg, paint(guardC, 0.5, 0.3)); bgm.position.set(mp[0], mp[1], 0.52); bgm.rotation.z = ga; root.add(bgm);
      // controller on a stand, conduit to the motor
      tbox(0.6, 0.8, 0.3, std('panelGrey', { color: 0x9da2a4, metalness: 0.4, roughness: 0.5 }), -6.0 + ox, 1.0, 1.3, root, 0, 0.02);
      for (const s of [-1, 1]) bar([-6.0 + ox + s * 0.25, 0, 1.3], [-6.0 + ox + s * 0.25, 1.1, 1.3], 0.03, galv(), root, 6);
      pipe([[-6.0 + ox, 1.0, 1.3], [-6.0 + ox, 0.4, 1.3], [mx, 0.4, 0.55], [mx, my + 0.3, 0.2]], 0.02, galv(), root);
      tbox(0.34, 0.24, 0.02, std('placard', { color: 0xf1efe8, roughness: 0.6 }), -6.0 + ox, 1.3, 1.46, root);
      return bake(root);
    },
  });

  /* ======================================================================================
   * OIL TANK BATTERY. Stock tanks (400 bbl: 12 ft across, 20 ft tall) in a row inside a steel
   * containment wall, a walkway across the tops with a stair, thief hatches and vents, a
   * load line manifold, a heater treater, a two phase separator and a combustor outside.
   * ==================================================================================== */
  K.define('oil_tank', {
    size: [36.9, 7.75, 13.5],
    options: { tanks: 4, color: null },
    note: 'Permian tank battery: stock tanks in a steel containment wall with walkway and stair, thief hatches, vents, load line manifold; heater treater, separator and combustor alongside.',
    make(o, r) {
      const root = new THREE.Group();
      const n = clamp(Math.round(o.tanks), 1, 10), R = 1.83, H = 6.1, pitch = 4.5;
      const col = o.color != null ? o.color : pick(r, [0xb9a27b, 0x46543f, 0x2d2e2e, 0xd9d4c4, 0x8a6b4a, 0x6b7a82]);
      const TM = paint(col, 0.6, 0.25), steel = paint(0xb7b9b6, 0.5, 0.5);
      const L = n * pitch, zc = -1.5;
      // containment: a steel ring wall on a gravel pad, a liner floor
      tbox(L + 13, 0.15, 13.5, gravel(), 3.2, 0, 0, root, 2);
      const cw = std('contain', { color: 0x6f6a5f, metalness: 0.4, roughness: 0.6 });
      const x0 = -L / 2 - 1.4, x1 = L / 2 + 1.4, z0 = zc - 3.2, z1 = zc + 3.4;
      for (const [a, b] of [[[x0, z0], [x1, z0]], [[x1, z0], [x1, z1]], [[x1, z1], [x0, z1]], [[x0, z1], [x0, z0]]]) {
        const len = Math.hypot(b[0] - a[0], b[1] - a[1]);
        const m = tbox(len, 0.9, 0.06, cw, (a[0] + b[0]) / 2, 0.15, (a[1] + b[1]) / 2, root);
        m.rotation.y = -Math.atan2(b[1] - a[1], b[0] - a[0]);
        for (let k = 0; k <= Math.ceil(len / 2); k++) { const t = k / Math.ceil(len / 2);
          const p = cbox(0.1, 0.9, 0.14, cw, a[0] + (b[0] - a[0]) * t, 0.6, a[1] + (b[1] - a[1]) * t, root); p.rotation.y = m.rotation.y; }
      }
      tbox(x1 - x0 - 0.1, 0.02, z1 - z0 - 0.1, std('liner', { color: 0x2a2b2c, roughness: 0.7 }), (x0 + x1) / 2, 0.15, (z0 + z1) / 2, root);
      // tanks: shell courses, roof cone, thief hatch, vent, manway, ladder gauge board
      for (let i = 0; i < n; i++) {
        const x = -L / 2 + (i + 0.5) * pitch;
        tbox(R * 2.2, 0.2, R * 2.2, concrete(), x, 0.15, zc, root, 3).geometry;
        cyl(R, R, H, TM, x, 0.35, zc, 48, root);
        for (let k = 1; k < 3; k++) { const ring = new THREE.Mesh(new THREE.TorusGeometry(R + 0.005, 0.012, 4, 48), TM); ring.rotation.x = Math.PI / 2; ring.position.set(x, 0.35 + k * H / 3, zc); root.add(ring); }
        const cone = new THREE.Mesh(new THREE.CylinderGeometry(0.2, R + 0.03, 0.35, 48), TM); cone.position.set(x, 0.35 + H + 0.175, zc); root.add(cone);
        cyl(0.26, 0.26, 0.28, TM, x + 0.6, 0.35 + H + 0.1, zc + 0.5, 16, root);            // thief hatch
        cyl(0.3, 0.3, 0.05, TM, x + 0.6, 0.35 + H + 0.38, zc + 0.5, 16, root);
        pipe([[x - 0.5, 0.35 + H + 0.2, zc], [x - 0.5, 0.35 + H + 1.0, zc], [x - 0.8, 0.35 + H + 1.2, zc]], 0.05, TM, root); // gooseneck vent
        hcyl(0.32, 0.12, TM, x, 0.95, zc + R + 0.03, 'z', 20, root);                       // manway
        for (let k = 0; k < 12; k++) { const a = k * TAU / 12; cyl(0.015, 0.015, 0.05, galv(), x + Math.cos(a) * 0.28, 0.95 + Math.sin(a) * 0.28 - 0.025, zc + R + 0.1, 5, root).rotation.x = Math.PI / 2; }
        // bottom outlet with a valve to the load line
        pipe([[x + 0.8, 0.6, zc + R - 0.2], [x + 0.8, 0.6, zc + R + 0.9], [x + 0.8, 0.45, zc + R + 0.9]], 0.05, steel, root);
        valve(0.05, x + 0.8, 0.6, zc + R + 0.55, 'z', steel, std('vwheel', { color: 0xc03a2b, roughness: 0.5 }), root);
        // equalizer line to the next tank
        if (i < n - 1) pipe([[x + R - 0.1, 5.2, zc - 0.5], [x + pitch - R + 0.1, 5.2, zc - 0.5]], 0.06, steel, root);
        // gauge board
        cbox(0.1, H - 0.5, 0.05, galv(), x - 1.3, 0.35 + H / 2, zc + R - 0.55, root, [0, 0.6, 0]);
      }
      // load line manifold along the front, the truck load connection outside the wall
      pipe([[-L / 2 + 0.5, 0.45, zc + R + 0.9], [L / 2 + 0.5, 0.45, zc + R + 0.9], [L / 2 + 0.5, 0.45, z1 + 0.8], [L / 2 + 0.5, 1.0, z1 + 0.8]], 0.07, steel, root);
      valve(0.07, L / 2 + 0.5, 1.0, z1 + 1.05, 'z', steel, std('vwheel', { color: 0xc03a2b, roughness: 0.5 }), root);
      // walkway across the tops: grating deck on brackets, rails, a stair down the -x end
      const wy = 0.35 + H + 0.05, wz = zc - R - 0.45;
      tbox(L, 0.06, 0.9, galv(), 0, wy, wz, root);
      for (let i = 0; i < n; i++) sbar([-L / 2 + (i + 0.5) * pitch, wy - 0.6, zc - R], [-L / 2 + (i + 0.5) * pitch, wy, wz - 0.4], 0.08, 0.08, galv(), root);
      for (let i = 0; i < n - 1; i++) { const x = -L / 2 + (i + 1) * pitch; tbox(1.4, 0.06, 0.9, galv(), x, wy, zc, root); }
      railing(root, [[-L / 2 - 0.2, wy, wz - 0.45], [L / 2, wy, wz - 0.45], [L / 2, wy, wz + 0.45]], 1.07, galv(), 1.5);
      const run = (wy - 0.15) / Math.tan(42 * D2R);
      stair(root, [-L / 2 - 0.6 - run, 0.15, wz], [-L / 2 - 0.6, wy, wz], 0.8, galv());
      tbox(0.9, 0.06, 0.9, galv(), -L / 2 - 0.2, wy, wz, root);
      for (const x of [-L / 2 - 0.6, -L / 2 - 0.6 - run * 0.5]) bar([x, 0.15, wz - 0.4], [x, wy * (x === -L / 2 - 0.6 ? 1 : 0.5), wz - 0.4], 0.04, galv(), root, 6);
      // heater treater: vertical vessel, fire tube box and stack, ladder
      const hx = L / 2 + 4.2, hz = zc + 0.6, VM = paint(pick(r, [0xd9d4c4, col, 0xb4b8b8]), 0.55, 0.25);
      cyl(0.95, 0.95, 6.4, VM, hx, 0.35, hz, 36, root);
      const hcap = new THREE.Mesh(new THREE.SphereGeometry(0.95, 36, 10, 0, TAU, 0, Math.PI / 2), VM); hcap.scale.y = 0.4; hcap.position.set(hx, 6.75, hz); root.add(hcap);
      for (let k = 0; k < 4; k++) { const a = k * TAU / 4 + 0.4; bar([hx + Math.cos(a) * 0.85, 0.15, hz + Math.sin(a) * 0.85], [hx + Math.cos(a) * 0.85, 0.5, hz + Math.sin(a) * 0.85], 0.07, VM, root, 8); }
      tbox(0.8, 0.8, 0.9, VM, hx, 1.0, hz + 1.2, root, 0, 0.03);
      pipe([[hx + 0.3, 1.6, hz + 1.2], [hx + 0.3, 7.6, hz + 1.2]], 0.14, darkSteel(), root);
      cyl(0.2, 0.2, 0.15, darkSteel(), hx + 0.3, 7.6, hz + 1.2, 12, root);
      ladder(root, hx - 0.96, 0.4, 6.4, hz, galv(), true, -Math.PI / 2);
      pipe([[hx - 0.3, 5.5, hz - 0.8], [hx - 0.3, 5.5, zc - 0.5], [L / 2 - pitch / 2 + R - 0.1, 5.5, zc - 0.5]], 0.06, steel, root);
      // two phase separator on legs
      const sx = L / 2 + 7.2, sz = zc - 0.6;
      cyl(0.46, 0.46, 3.2, VM, sx, 0.9, sz, 28, root);
      for (const e of [0, 1]) { const c = new THREE.Mesh(new THREE.SphereGeometry(0.46, 28, 8, 0, TAU, 0, Math.PI / 2), VM); c.scale.y = 0.45; c.rotation.x = e * Math.PI; c.position.set(sx, e ? 0.9 : 4.1, sz); root.add(c); }
      for (let k = 0; k < 3; k++) { const a = k * TAU / 3; bar([sx + Math.cos(a) * 0.55, 0.15, sz + Math.sin(a) * 0.55], [sx + Math.cos(a) * 0.4, 1.2, sz + Math.sin(a) * 0.4], 0.05, VM, root, 6); }
      pipe([[sx, 4.3, sz], [sx, 4.7, sz], [hx, 4.7, sz], [hx, 4.7, hz - 0.95]], 0.05, steel, root);
      pipe([[sx + 0.46, 2.0, sz], [sx + 2.4, 2.0, sz], [sx + 2.4, 0.2, sz]], 0.05, steel, root);
      valve(0.05, sx + 1.3, 2.0, sz, 'x', steel, std('vwheel', { color: 0xc03a2b, roughness: 0.5 }), root);
      // combustor: a tall insulated stack on a skid, off the pad corner
      const fx = L / 2 + 8.8, fz = zc + 3.8;
      tbox(1.6, 0.2, 1.6, darkSteel(), fx, 0.15, fz, root);
      cyl(0.45, 0.5, 6.5, std('combust', { color: 0x9a9d9b, metalness: 0.5, roughness: 0.5 }), fx, 0.35, fz, 24, root);
      cyl(0.5, 0.45, 0.4, darkSteel(), fx, 6.85, fz, 24, root);
      for (const s of [-1, 1]) bar([fx + s * 0.4, 0.4, fz], [fx + s * 2.4, 0.15, fz + s * 0.4], 0.04, galv(), root, 5);
      // a lease sign on posts
      tbox(0.9, 0.6, 0.03, std('leaseSign', { color: 0xf0eee6, roughness: 0.6 }), x0 - 1.2, 1.1, z1 + 0.6, root);
      for (const s of [-1, 1]) bar([x0 - 1.2 + s * 0.35, 0.15, z1 + 0.58], [x0 - 1.2 + s * 0.35, 1.7, z1 + 0.58], 0.03, galv(), root, 5);
      return bake(root);
    },
  });

  /* ======================================================================================
   * WAREHOUSE. A tilt wall concrete distribution building: painted panels with reveals, a
   * parapet, clerestory glazing, a glazed corner office, a row of dock doors with seals,
   * bumpers and lights on +z, a concrete truck court with trailers at some doors.
   * ==================================================================================== */
  K.define('warehouse', {
    size: [156, 13.4, 126],
    options: { length: 150, depth: 80, height: 12.8, docks: null, trucks: true, color: null },
    note: 'Tilt wall distribution warehouse: painted concrete panels with reveals and accent band, clerestory glazing, glazed office corner at +x, dock doors with seals along +z, truck court with trailers.',
    make(o, r) {
      const root = new THREE.Group();
      const L = clamp(o.length, 60, 360), D = clamp(o.depth, 40, 200), Hh = o.height, court = 40;
      const zb0 = -(D + court) / 2, zb1 = zb0 + D;
      const col = o.color != null ? o.color : pick(r, [0xd8d4ca, 0xcfcbc1, 0xe2dfd6, 0xc9c6bd, 0xdad3c4]);
      const acc = pick(r, [0x5a6670, 0x2f4f6b, 0x7b3b2e, 0x3d5a4a, 0x8c8f91]);
      const wallM = lmat('tilt' + col, () => new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.88,
        map: K.tex('concrete', { color: '#' + col.toString(16).padStart(6, '0') }) }));
      const revM = std('reveal' + col, { color: new THREE.Color(col).multiplyScalar(0.55).getHex(), roughness: 0.9 });
      const accM = paint(acc, 0.7, 0.05);
      tbox(L + 6, 0.08, D + 6, concrete('#b0aca3'), 0, 0, (zb0 + zb1) / 2, root, 3);
      tbox(L + 6, 0.08, court, concrete('#a9a59c'), 0, 0, zb1 + court / 2 + 3, root, 3);
      const body = K.box(L, Hh, D, wallM, 0, 0, (zb0 + zb1) / 2, 0, root); K.uvBox(body.geometry, 3);
      tbox(L - 0.4, 0.05, D - 0.4, std('tpo', { color: 0xdedcd4, roughness: 0.75 }), 0, Hh - 0.9, (zb0 + zb1) / 2, root);
      // panel joints every 9.1 m, horizontal reveals, accent band at the parapet
      const pw = 9.1;
      const faces = [[L, zb1, 0, 1], [L, zb0, Math.PI, -1]];
      for (const [len, z, rot, s] of faces) {
        const np = Math.round(len / pw);
        for (let i = 1; i < np; i++) cbox(0.04, Hh, 0.02, revM, -len / 2 + i * len / np, Hh / 2, z + s * 0.01, root);
        for (const y of [Hh - 1.6, Hh - 1.3, 4.6]) cbox(len, 0.05, 0.02, revM, 0, y, z + s * 0.01, root);
        cbox(len, 0.9, 0.03, accM, 0, Hh - 0.5, z + s * 0.012, root);
        // clerestory windows in alternate panels
        for (let i = 0; i < np; i += 2) {
          const cx = -len / 2 + (i + 0.5) * len / np;
          if (s > 0 && cx > L / 2 - 24) continue;
          wallPlane(3.6, 1.2, glass(), cx, Hh - 3.6, z + s * 0.03, rot, root);
          cbox(3.7, 0.08, 0.1, std('mullion', { color: 0x2f3337, metalness: 0.7, roughness: 0.35 }), cx, Hh - 3.64, z + s * 0.05, root);
          cbox(3.7, 0.06, 0.08, std('mullion', { color: 0x2f3337, metalness: 0.7, roughness: 0.35 }), cx, Hh - 2.37, z + s * 0.05, root);
          for (const e of [-1.8, 0, 1.8]) cbox(0.06, 1.2, 0.08, std('mullion', { color: 0x2f3337, metalness: 0.7, roughness: 0.35 }), cx + e, Hh - 3.0, z + s * 0.05, root);
        }
      }
      for (const s of [-1, 1]) {
        const x = s * L / 2, np = Math.round(D / pw);
        for (let i = 1; i < np; i++) cbox(0.02, Hh, 0.04, revM, x + s * 0.01, Hh / 2, zb0 + i * D / np, root);
        for (const y of [Hh - 1.6, Hh - 1.3, 4.6]) cbox(0.02, 0.05, D, revM, x + s * 0.01, y, (zb0 + zb1) / 2, root);
        cbox(0.03, 0.9, D, accM, x + s * 0.012, Hh - 0.5, (zb0 + zb1) / 2, root);
      }
      // dock doors along +z: 2.7 x 3.0 m at 1.2 m dock height, 3.96 m centres
      const docks = o.docks != null ? o.docks : Math.floor((L - 36) / 3.96);
      const dx0 = -L / 2 + 6;
      for (let i = 0; i < docks; i++) {
        const x = dx0 + (i + 0.5) * 3.96, open = r() < 0.18;
        wallPlane(2.74, 3.05, open ? hole() : sectionalMat(pick(r, [0xe4e5e3, 0xdadcdb])), x, 1.22, zb1 + 0.03, 0, root);
        cbox(0.28, 3.4, 0.3, rubber(), x - 1.55, 1.22 + 1.7, zb1 + 0.15, root); cbox(0.28, 3.4, 0.3, rubber(), x + 1.55, 1.22 + 1.7, zb1 + 0.15, root);
        cbox(3.4, 0.4, 0.3, rubber(), x, 1.22 + 3.25, zb1 + 0.15, root);
        for (const e of [-1, 1]) cbox(0.25, 0.45, 0.14, rubber(), x + e * 0.95, 0.95, zb1 + 0.07, root);
        cbox(1.9, 0.06, 0.06, galv(), x, 1.2, zb1 + 0.05, root);
        cbox(0.16, 0.12, 0.22, darkSteel(), x + 1.6, 4.7, zb1 + 0.1, root);
        if (i % 3 === 1) bar([x + 1.95, 0, zb1 + 0.6], [x + 1.95, 1.1, zb1 + 0.6], 0.1, paint(0xd8b24a, 0.5, 0.2), root, 10);
      }
      if (o.trucks) {
        for (let i = 0; i < docks; i++) if (r() < 0.38) trailer(root, dx0 + (i + 0.5) * 3.96, zb1 + 8.3, 0, pick(r, [0xecece8, 0xe0dfd8, 0xd8d8d2, 0xcfd2d4]), r);
      }
      // painted stall lines on the court
      for (let i = 0; i <= docks; i++) cbox(0.12, 0.01, 12, std('stripe', { color: 0xe8e2c6, roughness: 0.7 }), dx0 + i * 3.96, 0.09, zb1 + 12, root);
      // glazed two storey office at the +x front corner, entry canopy
      const ow = 22, ox = L / 2 - ow / 2 - 1;
      curtainWall(root, ox, 0.2, zb1 + 0.25, ow, 8.0, 0, 2, 1.52);
      curtainWall(root, L / 2 + 0.25, 0.2, zb1 - 8, 15, 8.0, Math.PI / 2, 2, 1.52);
      tbox(ow + 1, 1.2, 0.6, accM, ox, 8.2, zb1 + 0.3, root, 0, 0.03);
      tbox(7, 0.3, 3, accM, ox - 4, 3.6, zb1 + 1.7, root, 0, 0.03);
      for (const e of [-1, 1]) bar([ox - 4 + e * 3.2, 0, zb1 + 3], [ox - 4 + e * 3.2, 3.6, zb1 + 3], 0.1, accM, root, 10);
      // downspouts, wall packs, skylights and a few rooftop units
      for (let x = -L / 2 + 12; x < L / 2 - 26; x += 24) pipe([[x, Hh - 0.3, zb1 + 0.12], [x, 0.3, zb1 + 0.12]], 0.09, accM, root);
      for (let i = 0; i < Math.floor(L / 18); i++) for (let j = 0; j < Math.floor(D / 22); j++)
        tbox(1.2, 0.4, 2.4, std('skylight', { color: 0xd9dfe2, metalness: 0.1, roughness: 0.2 }), -L / 2 + (i + 0.5) * L / Math.floor(L / 18), Hh - 0.9, zb0 + (j + 0.5) * D / Math.floor(D / 22), root);
      for (let i = 0; i < 4; i++) tbox(3.2, 1.5, 2.0, paint(0xbfc1bf, 0.5, 0.3), L / 2 - 12 - i * 7, Hh - 0.9, zb1 - 8, root, 0, 0.04);
      return bake(root);
    },
  });
}
