/* kit/trees.js, see assets/js/txkit.js for the conventions.
 *
 * The trees of a Texas frame: the live oak, the mesquite, the cedar elm, the Ashe juniper, the
 * pecan, the crape myrtle, a clipped shrub or hedge, and the Washingtonia palm.
 *
 * HOW A TREE IS MADE HERE. A seeded grower lays a skeleton species by species (trunk, scaffold
 * limbs, branches, twigs, each with its own angle, droop, wander and taper). The wood is ONE merged
 * mesh of tapered tubes, parallel-transported so nothing twists, with a species bark painted in
 * metres and a root flare. The foliage is CLUSTERS: each a ball of crossed cards cut from a painted
 * atlas of that species' leaf sprays, instanced along the outer twigs, shaded by a canopy occlusion
 * term (dark inside and underneath, lit at the crown) in the instance colour, so a canopy has depth
 * and gaps and never reads as a blob. Every card is lit with one normal on both faces.
 */
export function install(K, THREE, TXT) {
  const V3 = THREE.Vector3;

  /* ---- small helpers -------------------------------------------------------------------- */
  const MC = new Map();
  function mat(key, make) { if (!MC.has(key)) MC.set(key, make()); return MC.get(key); }
  function hashStr(s) { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
  function canvas(N, M) { const c = document.createElement('canvas'); c.width = N; c.height = M || N; return c; }
  function rgb(h) { const c = parseInt(h.slice(1), 16); return [c >> 16, (c >> 8) & 255, c & 255]; }
  function css(a, k, al) {
    const f = (v) => Math.max(0, Math.min(255, Math.round(v * (k == null ? 1 : k))));
    return al == null ? 'rgb(' + f(a[0]) + ',' + f(a[1]) + ',' + f(a[2]) + ')' : 'rgba(' + f(a[0]) + ',' + f(a[1]) + ',' + f(a[2]) + ',' + al + ')';
  }
  function mix(a, b, t) { return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]; }
  const opt = (o, k, d) => (o[k] != null ? o[k] : d);
  function oneFace(m) {
    m.onBeforeCompile = (sh) => {
      sh.fragmentShader = sh.fragmentShader.replace('#include <normal_fragment_begin>',
        THREE.ShaderChunk.normal_fragment_begin.replace('float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;', 'float faceDirection = 1.0;'));
    };
    return m;
  }
  const TEXC = new Map();
  function texture(key, W, H, paint, srgb) {
    if (TEXC.has(key)) return TEXC.get(key);
    const c = canvas(W, H), x = c.getContext('2d');
    paint(x, W, H, K.rng(hashStr(key)));
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8;
    t.colorSpace = srgb === false ? THREE.NoColorSpace : THREE.SRGBColorSpace;
    TEXC.set(key, t); return t;
  }
  const GRAIN = new Map();
  function grain(x, W, H, amt) {
    if (!GRAIN.has(amt)) {
      const c = canvas(256), gx = c.getContext('2d'), im = gx.createImageData(256, 256), d = im.data, rr = K.rng(hashStr('g' + amt));
      for (let i = 0; i < d.length; i += 4) { const k = 128 + (rr() - 0.5) * 2 * amt * 128; d[i] = d[i + 1] = d[i + 2] = k; d[i + 3] = 255; }
      gx.putImageData(im, 0, 0); GRAIN.set(amt, c);
    }
    x.save(); x.globalCompositeOperation = 'overlay'; x.fillStyle = x.createPattern(GRAIN.get(amt), 'repeat'); x.fillRect(0, 0, W, H); x.restore();
  }

  /* ---- bark: one painter, species by parameter. 512 px covers 1 m around x 1 m up ------- */
  const BARKS = {
    oak:     { base: '#4f4a44', dark: '#1f1c19', light: '#7c766c', kind: 'block' },   // live oak: dark, blocky furrows
    mesquite:{ base: '#3e342c', dark: '#171210', light: '#6a5a4a', kind: 'shag' },    // near black, shaggy strips
    elm:     { base: '#6c6760', dark: '#2e2b27', light: '#9a948a', kind: 'scale' },   // grey, scaly
    juniper: { base: '#6d5e50', dark: '#2e241d', light: '#a08c78', kind: 'shred' },   // shredding reddish grey strips
    pecan:   { base: '#6a6058', dark: '#2a2521', light: '#958a7e', kind: 'scale' },
    crape:   { base: '#b39a80', dark: '#7a6450', light: '#dccab4', kind: 'mottle' },  // smooth, exfoliating patches
    palm:    { base: '#7a7166', dark: '#3a342e', light: '#a39a8c', kind: 'ring' },
  };
  function barkMat(name) {
    return mat('bark|' + name, () => {
      const B = BARKS[name];
      const col = texture('bark|' + name, 512, 512, (x, W, H, r) => paintBark(x, W, H, r, B, false));
      const bmp = texture('barkb|' + name, 512, 512, (x, W, H, r) => paintBark(x, W, H, r, B, true), false);
      return new THREE.MeshStandardMaterial({ color: 0xffffff, map: col, bumpMap: bmp, bumpScale: name === 'crape' ? 0.6 : 3.0, roughness: name === 'crape' ? 0.7 : 0.95 });
    });
  }
  function paintBark(x, W, H, r, B, bump) {
    const base = rgb(B.base), dark = rgb(B.dark), light = rgb(B.light);
    const P = (c) => (bump ? 'rgb(' + Math.round((c[0] + c[1] + c[2]) / 3) + ',' + Math.round((c[0] + c[1] + c[2]) / 3) + ',' + Math.round((c[0] + c[1] + c[2]) / 3) + ')' : css(c));
    const lum = (k) => (bump ? [255 * k, 255 * k, 255 * k] : null);
    x.fillStyle = bump ? '#606060' : css(base); x.fillRect(0, 0, W, H);
    const wrapRect = (px, py, w, h, style) => { x.fillStyle = style; for (const ox of [-W, 0, W]) for (const oy of [-H, 0, H]) x.fillRect(px + ox, py + oy, w, h); };
    if (B.kind === 'block' || B.kind === 'scale') {
      // plates between furrows: columns of blocks, offset, with dark cracks
      const cols = B.kind === 'block' ? 9 : 13;
      for (let c = 0; c < cols; c++) {
        let y = -r() * 60;
        const cx = c * W / cols;
        while (y < H) {
          const h = (B.kind === 'block' ? 40 : 24) + r() * (B.kind === 'block' ? 70 : 40), w = W / cols * (0.7 + r() * 0.25);
          const c1 = mix(base, r() < 0.5 ? light : dark, r() * 0.45);
          wrapRect(cx + (r() - 0.5) * 6, y, w, h - 5, bump ? P(lum(0.55 + r() * 0.35)) : css(c1));
          y += h;
        }
      }
      for (let c = 0; c <= cols; c++) {
        const cx = c * W / cols; x.strokeStyle = bump ? '#000' : css(dark); x.lineWidth = B.kind === 'block' ? 7 : 4;
        for (const ox of [-W, 0, W]) { x.beginPath(); x.moveTo(cx + ox, 0); for (let y = 0; y <= H; y += 32) x.lineTo(cx + ox + (r() - 0.5) * 12, y); x.stroke(); }
      }
    } else if (B.kind === 'shag' || B.kind === 'shred') {
      for (let i = 0; i < 160; i++) {
        const px = r() * W, w = 3 + r() * (B.kind === 'shag' ? 10 : 14), c1 = mix(base, r() < 0.5 ? light : dark, r() * 0.7);
        x.strokeStyle = bump ? P(lum(0.3 + r() * 0.6)) : css(c1); x.lineWidth = w;
        for (const ox of [-W, 0, W]) { x.beginPath(); x.moveTo(px + ox, -10); x.bezierCurveTo(px + ox + (r() - 0.5) * 30, H / 3, px + ox + (r() - 0.5) * 30, 2 * H / 3, px + ox + (r() - 0.5) * 10, H + 10); x.stroke(); }
      }
    } else if (B.kind === 'mottle') {
      for (let i = 0; i < 90; i++) {
        const px = r() * W, py = r() * H, rw = 10 + r() * 50, rh = 20 + r() * 90, c1 = mix(base, r() < 0.5 ? light : dark, 0.3 + r() * 0.6);
        x.fillStyle = bump ? P(lum(0.45 + r() * 0.2)) : css(c1);
        for (const ox of [-W, 0, W]) for (const oy of [-H, 0, H]) { x.beginPath(); x.ellipse(px + ox, py + oy, rw, rh, 0, 0, 6.3); x.fill(); }
      }
    } else if (B.kind === 'ring') {
      for (let y = 0; y < H; y += 14 + r() * 10) {
        x.fillStyle = bump ? '#202020' : css(dark, 1, 0.6); x.fillRect(0, y, W, 3 + r() * 3);
        x.fillStyle = bump ? '#a0a0a0' : css(light, 1, 0.25); x.fillRect(0, y + 4, W, 4);
      }
      for (let i = 0; i < 60; i++) { x.fillStyle = bump ? '#303030' : css(dark, 1, 0.3); x.fillRect(r() * W, r() * H, 2 + r() * 4, 20 + r() * 50); }
    }
    grain(x, W, H, bump ? 0.5 : 0.3);
  }

  /* ---- leaf atlases: 2 x 2 sprays of one species on a transparent 1024 canvas ------------ */
  function leafMat(name, spec) {
    return mat('leaf|' + name, () => {
      const t = texture('leaf|' + name, 1024, 1024, (x, W, H, r) => paintSprays(x, W, H, r, spec));
      t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
      const m = new THREE.MeshStandardMaterial({ map: t, alphaTest: spec.alphaTest || 0.42, side: THREE.DoubleSide, roughness: spec.rough || 0.62,
        metalness: 0, color: 0xffffff });
      return oneFace(m);
    });
  }
  /* A spray: a twig from the bottom centre of its cell, side twigs, leaves along each. `spec`:
   * leaf [length, width] in px, shape 'ellipse'|'lance'|'needle'|'scale'|'pinnate'|'bloom',
   * colours [dark, mid, light], twig colour, density (leaves per twig), spread. */
  function paintSprays(x, W, H, r, S) {
    x.clearRect(0, 0, W, H);
    const cells = 2, cw = W / cells;
    const cols = S.colors.map(rgb);
    for (let cy = 0; cy < cells; cy++) for (let cx = 0; cx < cells; cx++) {
      x.save(); x.beginPath(); x.rect(cx * cw + 2, cy * cw + 2, cw - 4, cw - 4); x.clip();
      const ox = cx * cw + cw / 2, oy = cy * cw + cw * 0.97;
      const twigs = [];
      const main = [[ox, oy]];
      let a = -Math.PI / 2 + (r() - 0.5) * 0.4, px = ox, py = oy;
      for (let i = 0; i < 8; i++) { a += (r() - 0.5) * 0.35; px += Math.cos(a) * cw * 0.11; py += Math.sin(a) * cw * 0.11; main.push([px, py]); }
      twigs.push(main);
      for (let i = 1; i < main.length - 1; i++) {
        const nb = S.branchy || 2;
        for (let k = 0; k < nb; k++) {
          const side = (i + k) % 2 ? 1 : -1, bl = cw * (0.12 + r() * 0.22) * (1 - i / main.length * 0.5);
          let ba = Math.atan2(main[i + 1][1] - main[i][1], main[i + 1][0] - main[i][0]) + side * (0.5 + r() * 0.6), bx = main[i][0], by = main[i][1];
          const tw = [[bx, by]];
          for (let j = 0; j < 4; j++) { ba += (r() - 0.5) * 0.3; bx += Math.cos(ba) * bl / 4; by += Math.sin(ba) * bl / 4; tw.push([bx, by]); }
          twigs.push(tw);
        }
      }
      // twigs
      x.lineCap = 'round';
      twigs.forEach((tw, ti) => {
        x.strokeStyle = S.twig; x.lineWidth = ti === 0 ? S.twigW || 5 : (S.twigW || 5) * 0.55;
        x.beginPath(); x.moveTo(tw[0][0], tw[0][1]); tw.forEach((p) => x.lineTo(p[0], p[1])); x.stroke();
      });
      // leaves
      twigs.forEach((tw) => {
        for (let i = 1; i < tw.length; i++) {
          const [x0, y0] = tw[i - 1], [x1, y1] = tw[i], along = Math.atan2(y1 - y0, x1 - x0);
          const n = S.density;
          for (let k = 0; k < n; k++) {
            const t = (k + r()) / n, lx = x0 + (x1 - x0) * t, ly = y0 + (y1 - y0) * t;
            const side = (k % 2 ? 1 : -1), ang = along + side * (S.angle || 0.9) + (r() - 0.5) * 0.6;
            leaf(x, lx, ly, ang, S, cols, r);
          }
        }
        const e = tw[tw.length - 1], p = tw[tw.length - 2];
        leaf(x, e[0], e[1], Math.atan2(e[1] - p[1], e[0] - p[0]) + (r() - 0.5) * 0.3, S, cols, r);
      });
      x.restore();
    }
  }
  function leaf(x, lx, ly, ang, S, cols, r) {
    const L = S.leaf[0] * (0.75 + r() * 0.5), Wd = S.leaf[1] * (0.75 + r() * 0.5);
    const c = mix(cols[0], r() < 0.5 ? cols[1] : cols[2], r());
    x.save(); x.translate(lx, ly); x.rotate(ang);
    if (S.shape === 'pinnate') {
      // a rachis with pairs of leaflets (pecan, mesquite)
      x.strokeStyle = S.twig; x.lineWidth = 1.5; x.beginPath(); x.moveTo(0, 0); x.lineTo(L, 0); x.stroke();
      const n = S.leaflets || 7;
      for (let i = 0; i < n; i++) {
        const t = (i + 0.7) / n, cc = mix(c, cols[r() < 0.5 ? 1 : 2], r() * 0.4);
        for (const s of [-1, 1]) {
          x.save(); x.translate(L * t, 0); x.rotate(s * (0.9 - t * 0.4));
          const g = x.createLinearGradient(0, -Wd, 0, Wd); g.addColorStop(0, css(cc, 1.15)); g.addColorStop(1, css(cc, 0.8));
          x.fillStyle = g; x.beginPath(); x.ellipse(Wd * 1.2, 0, Wd * 1.25, Wd * 0.42, 0, 0, 6.3); x.fill(); x.restore();
        }
      }
      x.fillStyle = css(c); x.beginPath(); x.ellipse(L + Wd, 0, Wd * 1.2, Wd * 0.45, 0, 0, 6.3); x.fill();
    } else if (S.shape === 'scale') {
      // juniper: ropey branchlets of scale leaves, forking
      x.strokeStyle = css(c); x.lineCap = 'round';
      for (let k = 0; k < 3; k++) {
        const a2 = (k - 1) * 0.5 + (r() - 0.5) * 0.3; x.lineWidth = Wd * (0.8 + r() * 0.4);
        x.beginPath(); x.moveTo(0, 0); x.lineTo(Math.cos(a2) * L, Math.sin(a2) * L); x.stroke();
        x.strokeStyle = css(c, 1.2, 0.8); x.lineWidth = Wd * 0.3;
        x.beginPath(); x.moveTo(0, -Wd * 0.2); x.lineTo(Math.cos(a2) * L, Math.sin(a2) * L - Wd * 0.2); x.stroke();
        x.strokeStyle = css(c);
      }
      if (S.berries && r() < 0.12) { x.fillStyle = S.berries; x.beginPath(); x.arc(L * 0.6, 0, Wd * 0.8, 0, 6.3); x.fill(); }
    } else if (S.shape === 'bloom') {
      // a panicle of crinkled florets: many small overlapping discs over a cone
      for (let i = 0; i < 60; i++) {
        const t = r(), rad = (1 - t) * Wd;
        const fx = t * L, fy = (r() - 0.5) * 2 * rad, fc = mix(cols[0], cols[r() < 0.5 ? 1 : 2], r());
        x.fillStyle = css(fc, 0.85 + r() * 0.3); x.beginPath(); x.arc(fx, fy, 3 + r() * 5, 0, 6.3); x.fill();
      }
    } else {
      const g = x.createLinearGradient(0, -Wd, 0, Wd);
      g.addColorStop(0, css(c, S.gloss ? 1.35 : 1.12)); g.addColorStop(0.5, css(c, 1.0)); g.addColorStop(1, css(c, 0.72));
      x.fillStyle = g; x.beginPath();
      if (S.shape === 'lance') { x.moveTo(0, 0); x.quadraticCurveTo(L * 0.4, -Wd, L, 0); x.quadraticCurveTo(L * 0.4, Wd, 0, 0); }
      else if (S.shape === 'needle') { x.ellipse(L / 2, 0, L / 2, Wd / 2, 0, 0, 6.3); }
      else { x.ellipse(L * 0.55, 0, L * 0.5, Wd / 2, 0, 0, 6.3); }
      x.fill();
      if (S.serrate) { x.strokeStyle = css(c, 0.7); x.lineWidth = 1; x.setLineDash([2, 2]); x.stroke(); x.setLineDash([]); }
      x.strokeStyle = css(c, 0.7, 0.7); x.lineWidth = 1; x.beginPath(); x.moveTo(0, 0); x.lineTo(L * 0.95, 0); x.stroke();
      if (S.berries && r() < 0.08) { x.fillStyle = S.berries; x.beginPath(); x.arc(L * 0.2, Wd * 0.9, Wd * 0.45, 0, 6.3); x.fill(); }
    }
    x.restore();
  }

  /* ---- a foliage cluster: crossed cards in a ball, normals radial ------------------------ */
  const CLUSTERS = new Map();
  function clusterGeo(key, nCards, flat) {
    if (CLUSTERS.has(key)) return CLUSTERS.get(key);
    const r = K.rng(hashStr(key)), P = [], N = [], U = [];
    for (let i = 0; i < nCards; i++) {
      const s = 0.75 + r() * 0.5;                                 // card size (cluster radius = 1)
      const c = new V3((r() - 0.5) * 0.9, (r() - 0.5) * 0.9 * (flat || 1), (r() - 0.5) * 0.9);
      // orientation: random, biased so the spray faces out and up
      const nrm = c.clone().add(new V3((r() - 0.5), 0.6 + r() * 0.8, (r() - 0.5))).normalize();
      const tan = new V3(r() - 0.5, r() - 0.5, r() - 0.5).cross(nrm).normalize(), bit = nrm.clone().cross(tan);
      const cell = Math.floor(r() * 4), u0 = (cell % 2) * 0.5, v0 = Math.floor(cell / 2) * 0.5;
      // the spray's twig is at the bottom of its cell: put that end toward the cluster centre
      const toC = c.clone().negate().normalize();
      const up = bit.clone().multiplyScalar(-Math.sign(bit.dot(toC)) || 1);
      const corners = [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([a, b]) => c.clone().addScaledVector(tan, a * s * 0.5).addScaledVector(up, b * s * 0.5 + s * 0.3));
      const uvs = [[u0, 1 - v0 - 0.5], [u0 + 0.5, 1 - v0 - 0.5], [u0 + 0.5, 1 - v0], [u0, 1 - v0]];
      for (const tri of [[0, 1, 2], [0, 2, 3]]) for (const k of tri) {
        const p = corners[k]; P.push(p.x, p.y, p.z);
        const n = p.clone().normalize().multiplyScalar(0.8).add(new V3(0, 0.45, 0)).normalize(); N.push(n.x, n.y, n.z);
        U.push(uvs[k][0], uvs[k][1]);
      }
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3));
    g.setAttribute('normal', new THREE.Float32BufferAttribute(N, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(U, 2));
    CLUSTERS.set(key, g);
    return g;
  }

  /* ---- tapered tubes, parallel transport, UVs in metres ---------------------------------- */
  function taperTube(pts, radii, radial, out, barkM) {
    const n = pts.length; if (n < 2) return;
    const T = [], Nn = [], Bn = [];
    for (let i = 0; i < n; i++) {
      const a = pts[Math.max(0, i - 1)], b = pts[Math.min(n - 1, i + 1)];
      T.push(b.clone().sub(a).normalize());
    }
    let ref = Math.abs(T[0].y) < 0.9 ? new V3(0, 1, 0) : new V3(1, 0, 0);
    Nn.push(ref.clone().cross(T[0]).normalize()); Bn.push(T[0].clone().cross(Nn[0]));
    for (let i = 1; i < n; i++) {
      const axis = T[i - 1].clone().cross(T[i]); let nn = Nn[i - 1].clone();
      if (axis.lengthSq() > 1e-10) { axis.normalize(); nn.applyAxisAngle(axis, Math.acos(Math.max(-1, Math.min(1, T[i - 1].dot(T[i]))))); }
      Nn.push(nn); Bn.push(T[i].clone().cross(nn));
    }
    let along = 0;
    const base = out.pos.length / 3;
    for (let i = 0; i < n; i++) {
      if (i) along += pts[i].distanceTo(pts[i - 1]);
      const rr = radii[i], circ = Math.PI * 2 * Math.max(rr, 0.02);
      for (let j = 0; j <= radial; j++) {
        const a = j / radial * Math.PI * 2, ca = Math.cos(a), sa = Math.sin(a);
        const nx = Nn[i].x * ca + Bn[i].x * sa, ny = Nn[i].y * ca + Bn[i].y * sa, nz = Nn[i].z * ca + Bn[i].z * sa;
        out.pos.push(pts[i].x + nx * rr, pts[i].y + ny * rr, pts[i].z + nz * rr);
        out.nor.push(nx, ny, nz);
        out.uv.push(j / radial * Math.max(1, Math.round(circ / 0.5)) * 0.5, along);
      }
    }
    for (let i = 0; i < n - 1; i++) for (let j = 0; j < radial; j++) {
      const a = base + i * (radial + 1) + j, b = a + radial + 1;
      out.idx.push(a, b, a + 1, b, b + 1, a + 1);
    }
  }
  function woodMesh(out, m) {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(out.pos, 3));
    g.setAttribute('normal', new THREE.Float32BufferAttribute(out.nor, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(out.uv, 2));
    g.setIndex(out.idx);
    return new THREE.Mesh(g, m);
  }

  /* ---- the grower ------------------------------------------------------------------------
   * S = { trunks: [{ at:[x,z], dir:[x,y,z], len, rad }], levels: [ per depth {
   *   n (children per parent), t0, t1 (where on the parent), angle (rad from the parent),
   *   lenK, radK, step (m), wander, up (toward sky), droop (toward ground, grows along the branch),
   *   spread (pull away from the trunk axis), taper (end radius / start radius) } ],
   *   leaves: { per (clusters per terminal twig), from (t), size [min,max], key, cards } } */
  function grow(S, r) {
    const wood = { pos: [], nor: [], uv: [], idx: [] }, clusters = [], tips = [];
    let tris = 0;
    function perp(d) { const a = Math.abs(d.y) < 0.9 ? new V3(0, 1, 0) : new V3(1, 0, 0); const u = a.clone().cross(d).normalize(); return [u, d.clone().cross(u).normalize()]; }
    function branch(p0, d0, len, rad, lvl, az0) {
      const L = S.levels[lvl], nSteps = Math.max(2, Math.ceil(len / L.step));
      const pts = [p0.clone()], radii = [rad];
      let p = p0.clone(), d = d0.clone().normalize();
      for (let i = 1; i <= nSteps; i++) {
        const t = i / nSteps;
        const out = new V3(p.x, 0, p.z); if (out.lengthSq() > 1e-6) out.normalize();
        d.add(new V3((r() - 0.5) * L.wander, (r() - 0.5) * L.wander * 0.6, (r() - 0.5) * L.wander))
         .add(new V3(0, (L.up || 0) - (L.droop || 0) * t, 0)).addScaledVector(out, L.spread || 0).normalize();
        p = p.clone().addScaledVector(d, len / nSteps);
        if (S.floor != null && p.y < S.floor) { p.y = S.floor; d.y = Math.abs(d.y) * 0.5; d.normalize(); }
        pts.push(p); radii.push(rad * (1 - (1 - L.taper) * Math.pow(t, L.taperPow || 1)));
      }
      const radial = rad > 0.25 ? 14 : rad > 0.1 ? 10 : rad > 0.04 ? 7 : rad > 0.018 ? 5 : 4;
      if (lvl === 0 && S.flare) {
        // root flare: fatten the first metre and add buttress roots running into the ground
        for (let i = 0; i < pts.length; i++) { const h = pts[i].y; radii[i] *= 1 + S.flare * Math.exp(-h * 3.2); }
      }
      taperTube(pts, radii, radial, wood); tris += (pts.length - 1) * radial * 2;
      const at = (t) => { const f = t * (pts.length - 1), i = Math.min(pts.length - 2, Math.floor(f)), k = f - i;
        return [pts[i].clone().lerp(pts[i + 1], k), pts[i + 1].clone().sub(pts[i]).normalize(), radii[i] + (radii[i + 1] - radii[i]) * k]; };
      if (lvl + 1 < S.levels.length) {
        const C = S.levels[lvl + 1], n = Math.max(0, Math.round(C.n * (0.8 + r() * 0.4)));
        let az = az0 != null ? az0 : r() * 6.283;
        for (let k = 0; k < n; k++) {
          const t = C.t0 + (C.t1 - C.t0) * (n === 1 ? 0.5 + (r() - 0.5) * 0.4 : (k + r() * 0.7) / n);
          const [bp, bd, br] = at(t);
          az += C.azStep || 2.4;
          const [u, v] = perp(bd), w = u.clone().multiplyScalar(Math.cos(az)).addScaledVector(v, Math.sin(az));
          const ang = C.angle + (r() - 0.5) * (C.angleJit || 0.3);
          const cd = bd.clone().multiplyScalar(Math.cos(ang)).addScaledVector(w, Math.sin(ang)).normalize();
          const cl = len * C.lenK * (1 - t * (C.shorten || 0.4)) * (0.8 + r() * 0.4);
          branch(bp, cd, cl, Math.max(S.minRad || 0.008, br * C.radK), lvl + 1);
        }
      }
      if (lvl + 1 >= S.levels.length || (S.leaves.onLevels && S.leaves.onLevels.includes(lvl))) {
        const Lf = S.leaves, per = Lf.per;
        for (let k = 0; k < per; k++) {
          const t = Lf.from + (1 - Lf.from) * (per === 1 ? 1 : k / (per - 1));
          const [q] = at(Math.min(1, t));
          const sz = Lf.size[0] + r() * (Lf.size[1] - Lf.size[0]);
          clusters.push([q.x + (r() - 0.5) * sz * 0.4, q.y + sz * (Lf.lift != null ? Lf.lift : 0.25), q.z + (r() - 0.5) * sz * 0.4, sz]);
        }
        tips.push(pts[pts.length - 1]);
      }
    }
    S.trunks.forEach((T, i) => branch(new V3(T.at[0], T.at[1] || 0, T.at[2] != null ? T.at[2] : T.at[1] || 0), new V3(...T.dir), T.len, T.rad, 0, T.az));
    return { wood, clusters, tips, tris };
  }
  // the canopy occlusion term and the instanced foliage
  function foliage(g, list, lm, geoKey, cards, colors, r, o) {
    o = o || {};
    const geo = clusterGeo(geoKey, cards, o.flat);
    const im = new THREE.InstancedMesh(geo, lm, list.length);
    const box = new THREE.Box3(); list.forEach(([x, y, z, s]) => box.expandByPoint(new V3(x, y, z)));
    const ctr = new V3(); box.getCenter(ctr); const size = new V3(); box.getSize(size);
    const Mx = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), sc = new V3(), p = new V3(), c = new THREE.Color();
    const cols = colors.map((h) => new THREE.Color(h));
    list.forEach(([x, y, z, s], i) => {
      e.set((r() - 0.5) * 0.6, r() * 6.283, (r() - 0.5) * 0.6); q.setFromEuler(e); sc.set(s, s * (o.squash || 0.85), s); p.set(x, y, z);
      Mx.compose(p, q, sc); im.setMatrixAt(i, Mx);
      const hy = size.y > 0.01 ? (y - box.min.y) / size.y : 1;
      const rad = Math.hypot(x - ctr.x, z - ctr.z) / (Math.max(size.x, size.z) / 2 + 1e-3);
      const ao = Math.min(1, 0.35 + 0.45 * hy + 0.35 * rad);
      const base = cols[Math.floor(r() * cols.length)].clone().lerp(cols[Math.floor(r() * cols.length)], r());
      const j = (0.86 + r() * 0.28) * (o.aoMin != null ? o.aoMin + (1 - o.aoMin) * ao : 0.42 + 0.58 * ao);
      c.copy(base).multiplyScalar(j); im.setColorAt(i, c);
    });
    im.instanceMatrix.needsUpdate = true; im.instanceColor.needsUpdate = true;
    g.add(im);
    return im;
  }
  function tri(g) { let t = 0; g.traverse((m) => { if (m.isMesh) t += (m.geometry.index ? m.geometry.index.count : m.geometry.attributes.position.count) / 3 * (m.isInstancedMesh ? m.count : 1); }); return t; }
  // thin the cluster list to a triangle budget, keeping the outer shell before the interior
  function budgetClusters(list, cards, woodTris, budget, ctr) {
    const perCl = cards * 2, max = Math.floor((budget - woodTris) / perCl);
    if (list.length <= max) return list;
    const scored = list.map((c) => [c, Math.hypot(c[0] - ctr.x, (c[1] - ctr.y) * 1.3, c[2] - ctr.z)]);
    scored.sort((a, b) => b[1] - a[1]);
    // keep the outer 70% of the budget from the shell, the rest sampled from the interior evenly
    const keep = scored.slice(0, Math.floor(max * 0.75)).map((s) => s[0]);
    const rest = scored.slice(Math.floor(max * 0.75)), need = max - keep.length;
    for (let i = 0; i < need; i++) keep.push(rest[Math.floor(i * rest.length / need)][0]);
    return keep;
  }

  /* a generic species builder: grow, bark, foliage, budget */
  function makeTree(S, r, spec) {
    const g = new THREE.Group();
    const res = grow(S, r);
    const wood = woodMesh(res.wood, barkMat(spec.bark));
    g.add(wood);
    const woodTris = res.wood.idx.length / 3;
    const ctr = new V3(); res.clusters.forEach((c) => ctr.add(new V3(c[0], c[1], c[2]))); ctr.multiplyScalar(1 / Math.max(1, res.clusters.length));
    const list = budgetClusters(res.clusters, spec.cards, woodTris, spec.budget || 38500, ctr);
    foliage(g, list, leafMat(spec.leafKey, spec.leaf), spec.leafKey + '|geo', spec.cards, spec.colors, r, spec.fol);
    if (spec.extra) spec.extra(g, res, r);
    return g;
  }

  /* =======================================================================================
   * live_oak — Quercus virginiana (fusiformis in the Hill Country)
   * ===================================================================================== */
  const OAK_LEAF = { shape: 'ellipse', leaf: [34, 16], colors: ['#27361c', '#3d5226', '#52682f'], twig: '#3a3027', twigW: 4, density: 5, angle: 0.8, gloss: true, branchy: 2 };
  K.define('live_oak', {
    size: [18, 9, 18],
    options: { height: 'metres (9)', spread: 'metres across the crown (18)' },
    note: 'The Texas live oak: a short massive trunk with a root flare, four to six great limbs that leave low and run out nearly level, sinuous and dipping, secondary branches rising off their backs, and a broad low dome of small dark glossy leaf clusters with depth and sky gaps.',
    make(o, r) {
      const H = opt(o, 'height', 9), SP = opt(o, 'spread', 18), k = SP / 18, kh = H / 9;
      const trunkH = 1.6 + r() * 1.0, nLimbs = 4 + Math.floor(r() * 3);
      const trunks = [{ at: [0, 0, 0], dir: [(r() - 0.5) * 0.2, 1, (r() - 0.5) * 0.2], len: trunkH * kh, rad: 0.45 * Math.max(0.6, k), az: r() * 6.3 }];
      const S = {
        trunks, flare: 0.9, floor: 0.4, minRad: 0.012,
        levels: [
          { step: 0.5, wander: 0.08, up: 0.05, taper: 0.8 },
          // the great limbs: leave the top of the trunk at a shallow rise, run out, dip
          { n: nLimbs, t0: 0.72, t1: 1.0, angle: 1.05, angleJit: 0.35, azStep: 6.283 / nLimbs, lenK: 3.6 * k / (trunkH * kh / 2), radK: 0.62, shorten: 0,
            step: 0.6, wander: 0.22, up: 0.035, droop: 0.12, spread: 0.06, taper: 0.28, taperPow: 0.8 },
          // branches off the limbs, rising and fanning
          { n: 7, t0: 0.18, t1: 0.95, angle: 0.8, angleJit: 0.5, lenK: 0.55, radK: 0.55, shorten: 0.5, step: 0.45, wander: 0.28, up: 0.1, droop: 0.02, spread: 0.05, taper: 0.3 },
          // twigs
          { n: 4, t0: 0.3, t1: 1.0, angle: 0.75, angleJit: 0.5, lenK: 0.45, radK: 0.5, shorten: 0.3, step: 0.4, wander: 0.35, up: 0.08, taper: 0.35 },
        ],
        leaves: { per: 2, from: 0.45, size: [0.75 * Math.sqrt(k), 1.15 * Math.sqrt(k)], lift: 0.15 },
      };
      const g = makeTree(S, r, { bark: 'oak', leafKey: 'oak', leaf: OAK_LEAF, cards: 11, colors: [0xffffff, 0xeef4e0, 0xf6f0d6, 0xdde8cc], fol: { squash: 0.8 } });
      return g;
    },
  });
}
