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
    oak:     { base: '#4a4540', dark: '#141210', light: '#8a8278', kind: 'block' },   // live oak: dark, blocky furrows
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
    if (B.kind === 'block' || B.kind === 'scale' || B.kind === 'shag' || B.kind === 'shred') {
      /* a furrow field, per pixel: ridges run up the stem (warped so they wander and merge),
       * broken across by cracks at a per-ridge rhythm. Tileable: integer counts, periodic warps. */
      const P0 = { block: [11, [5, 9], 0.22, 0.09], scale: [15, [9, 15], 0.18, 0.07], shag: [18, [1, 3], 0.35, 0.05], shred: [22, [1, 2], 0.5, 0.03] }[B.kind];
      const nR = P0[0], cr = [], ph = [];
      for (let i = 0; i < nR; i++) { cr.push(P0[1][0] + Math.floor(r() * (P0[1][1] - P0[1][0] + 1))); ph.push(r()); }
      const wp = [r() * 6.28, r() * 6.28, r() * 6.28], im = x.createImageData(W, H), d = im.data;
      const ss = (e0, e1, v) => { const t = Math.max(0, Math.min(1, (v - e0) / (e1 - e0))); return t * t * (3 - 2 * t); };
      for (let yy = 0; yy < H; yy++) {
        const fy = yy / H;
        for (let xx = 0; xx < W; xx++) {
          const fx = xx / W;
          const u = fx * nR + P0[2] * (Math.sin(fy * 6.283 * 2 + wp[0] + fx * 6.283 * 3) + 0.5 * Math.sin(fy * 6.283 * 5 + wp[1] + fx * 6.283 * 7));
          const cell = ((Math.floor(u) % nR) + nR) % nR, f = u - Math.floor(u);
          const ridge = ss(0, 0.28, f) * ss(1, 0.72, f);
          const v = fy * cr[cell] + ph[cell] + 0.15 * Math.sin(fx * 6.283 * 2 + wp[2]), g = v - Math.floor(v);
          const crack = ss(0, P0[3], g) * ss(1, 1 - P0[3], g);
          let val = ridge * (0.35 + 0.65 * crack);
          val *= 0.82 + 0.18 * Math.sin(cell * 12.9 + ph[cell] * 20);
          const i4 = (yy * W + xx) * 4;
          if (bump) { const q = 20 + val * 220; d[i4] = d[i4 + 1] = d[i4 + 2] = q; }
          else {
            const c = val < 0.5 ? mix(dark, base, val * 2) : mix(base, light, (val - 0.5) * 2 * 0.8);
            d[i4] = c[0]; d[i4 + 1] = c[1]; d[i4 + 2] = c[2];
          }
          d[i4 + 3] = 255;
        }
      }
      x.putImageData(im, 0, 0);
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
      const m = new THREE.MeshStandardMaterial({ map: t, alphaTest: spec.alphaTest || 0.42, side: THREE.DoubleSide, roughness: spec.rough || 0.8,
        metalness: 0, color: 0xffffff, envMapIntensity: 0.4 });
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
        for (let i = 0; i < pts.length; i++) { const h = Math.max(0, pts[i].y); radii[i] *= 1 + S.flare * Math.exp(-h * 4.5); }
      }
      taperTube(pts, radii, radial, wood); tris += (pts.length - 1) * radial * 2;
      if (lvl === 0 && S.roots) {
        // buttress roots: short tapering tubes leaving the trunk foot and diving under the grade
        const nr = S.roots, r0 = rad * (1 + (S.flare || 0));
        for (let i = 0; i < nr; i++) {
          const a = (i + r() * 0.5) / nr * 6.283, dx = Math.cos(a), dz = Math.sin(a), L = r0 * (0.9 + r() * 0.8);
          const rp = [], rr = [];
          for (let k = 0; k <= 5; k++) {
            const t = k / 5;
            rp.push(new V3(p0.x + dx * (r0 * 0.2 + L * t), r0 * 0.55 * Math.pow(1 - t, 1.3) - 0.1 * t, p0.z + dz * (r0 * 0.2 + L * t)));
            rr.push(r0 * 0.42 * (1 - 0.55 * t));
          }
          taperTube(rp, rr, 8, wood); tris += 5 * 16;
        }
      }
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
      let ao = Math.min(1, 0.35 + 0.45 * hy + 0.35 * rad);
      if (list[i][5] != null) ao *= 0.72 + 0.28 * Math.max(0, Math.min(1, (list[i][5] + 0.3) * 1.4));
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
    const scored = list.map((c) => [c, Math.hypot(c[0] - ctr.x, (c[1] - ctr.y) * 1.3, c[2] - ctr.z) + (c[4] ? 100 : 0)]);
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
    /* THE CROWN ENVELOPE: a half-ellipsoid (centre [0, y0, 0], radii rx, ry, rz). Clusters outside
     * are drawn back onto it so the outline is the species' own, smooth dome or oval; clusters
     * under `base` are dropped so the understory is open and the limbs show; `hollow` thins the
     * deep interior, which nobody sees and every ray pays for. */
    /* THE SHELL: clusters sampled on the envelope itself, a layer `thick` deep, the bottom
     * flattened into a skirt, cut into masses by a clump field (low-frequency directional
     * noise) so the crown is lumps of foliage with dark gaps between, the way a crown reads. */
    if (S.shell) {
      const E = S.envelope, Sh = S.shell, ph = [];
      for (let i = 0; i < 6; i++) ph.push([r() * 6.283, 1 + Math.floor(r() * 3), r() - 0.5, r() - 0.5, r() - 0.5]);
      const clump = (v) => { let n = 0; for (const [p, f, a, b, c] of ph) n += Math.sin((v.x * a + v.y * b + v.z * c) * 6 * f + p); return n / ph.length; };
      let tries = 0, added = 0;
      while (tries++ < Sh.n * 6 && added < Sh.n) {
        const u = r() * 2 - 1, th = r() * 6.283, sq = Math.sqrt(1 - u * u);
        const v = new V3(sq * Math.cos(th), u, sq * Math.sin(th));
        if (v.y < -(Sh.skirt || 0.2)) continue;
        const cv = clump(v);
        if (cv < (Sh.gaps || -1)) continue;
        const dd = (1 - r() * (Sh.thick || 0.25)) * (1 + (Sh.lobe || 0) * cv);
        const x = (E.x || 0) + v.x * E.rx * dd, z = (E.z || 0) + v.z * E.rz * dd;
        const y = E.y0 + v.y * (v.y < 0 ? E.ry * (Sh.below || 0.35) : E.ry) * dd;
        const sz = Sh.size[0] + r() * (Sh.size[1] - Sh.size[0]);
        res.clusters.push([x, y, z, sz, 1, cv]); added++;
      }
    }
    if (S.envelope) {
      const E = S.envelope, keep = [];
      for (const c of res.clusters) {
        let dx = (c[0] - (E.x || 0)) / E.rx, dy = (c[1] - E.y0) / E.ry, dz = (c[2] - (E.z || 0)) / E.rz;
        if (dy < 0 && E.flatBottom) dy *= E.flatBottom;
        let d = Math.hypot(dx, dy, dz);
        if (d > 1) { const k = (0.94 + r() * 0.08) / d; c[0] = (E.x || 0) + (c[0] - (E.x || 0)) * k; c[1] = E.y0 + (c[1] - E.y0) * k; c[2] = (E.z || 0) + (c[2] - (E.z || 0)) * k; d = 1; }
        if (c[1] < (E.base != null ? E.base : -1e9)) continue;
        if (E.hollow && d < E.hollow && r() < 0.7) continue;
        keep.push(c);
      }
      res.clusters = keep;
    }
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
  const OAK_LEAF = { shape: 'ellipse', leaf: [21, 10], colors: ['#27361c', '#3d5226', '#52682f'], twig: '#3a3027', twigW: 3, density: 9, angle: 0.8, gloss: true, branchy: 2 };
  K.define('live_oak', {
    size: [18, 9, 18],
    options: { height: 9, spread: 18 },
    note: 'Options: height m, spread m across the crown. The Texas live oak: a short massive trunk with a root flare, four to six great limbs that leave low and run out nearly level, sinuous and dipping, secondary branches rising off their backs, and a broad low dome of small dark glossy leaf clusters with depth and sky gaps.',
    make(o, r) {
      const H = opt(o, 'height', 9), SP = opt(o, 'spread', 18), k = SP / 18, kh = H / 9;
      const trunkH = (1.9 + r() * 0.7) * Math.min(1.2, kh), nLimbs = 5 + Math.floor(r() * 3);
      const trunks = [{ at: [0, -0.15, 0], dir: [(r() - 0.5) * 0.3, 1, (r() - 0.5) * 0.3], len: trunkH + 0.15, rad: 0.46 * Math.max(0.6, k), az: r() * 6.3 }];
      const S = {
        trunks, flare: 0.45, roots: 6, floor: 1.9 * kh, minRad: 0.012,
        levels: [
          { step: 0.5, wander: 0.1, up: 0.04, taper: 0.72 },
          // the great limbs: leave the top of the trunk low, sweep out nearly level, sag, then lift
          { n: nLimbs, t0: 0.62, t1: 1.0, angle: 1.2, angleJit: 0.3, azStep: 6.283 / nLimbs, lenK: 8.8 * k / (trunkH + 0.3), radK: 0.62, shorten: 0,
            step: 0.55, wander: 0.24, up: 0.045, droop: 0.1, spread: 0.1, taper: 0.22, taperPow: 0.7 },
          // branches off the backs of the limbs, rising into the dome
          { n: 9, t0: 0.12, t1: 0.98, angle: 0.8, angleJit: 0.5, lenK: 0.36, radK: 0.5, shorten: 0.35, step: 0.4, wander: 0.3, up: 0.14, droop: 0.0, spread: 0.04, taper: 0.3 },
          // twigs
          { n: 4, t0: 0.25, t1: 1.0, angle: 0.8, angleJit: 0.5, lenK: 0.5, radK: 0.5, shorten: 0.3, step: 0.35, wander: 0.4, up: 0.06, taper: 0.35 },
        ],
        leaves: { per: 3, from: 0.2, size: [0.45 * Math.sqrt(k), 0.72 * Math.sqrt(k)], lift: 0.12 },
        // a broad low dome: twice as wide as it is tall, its skirt at the height the limbs sag to
        envelope: { rx: SP / 2, rz: SP / 2 * (0.88 + r() * 0.2), y0: 3.4 * kh, ry: H - 3.4 * kh, base: 2.1 * kh, hollow: 0.5, flatBottom: 3 },
        shell: { n: 1150, size: [0.62 * Math.sqrt(k), 0.95 * Math.sqrt(k)], thick: 0.22, skirt: 0.4, below: 0.3, gaps: -0.12, lobe: 0.2 },
      };
      const g = makeTree(S, r, { bark: 'oak', leafKey: 'oak', leaf: OAK_LEAF, cards: 11, colors: [0xfff0c8, 0xeee0b0, 0xfff6d4, 0xe2d8a8], fol: { squash: 0.8 } });
      return g;
    },
  });

  /* =======================================================================================
   * mesquite — Prosopis glandulosa
   * ===================================================================================== */
  const MESQ_LEAF = { shape: 'pinnate', leaf: [70, 5], leaflets: 13, colors: ['#5d7a38', '#7a974a', '#98b15e'], twig: '#2e241c', twigW: 3, density: 3, angle: 1.0, branchy: 2, alphaTest: 0.35 };
  K.define('mesquite', {
    size: [8, 6, 8],
    options: { height: 6, spread: 8, stems: null },
    note: 'Options: height m, spread m, stems (null = seeded 2 or 3). Honey mesquite: two or three thin, twisting, near-black stems leaning out from one base, zigzag branches arching over, and a flat, airy, feathery umbrella of lime-green bipinnate leaves with the sky and the limbs showing through.',
    make(o, r) {
      const H = opt(o, 'height', 6), SP = opt(o, 'spread', 8), k = SP / 8, kh = H / 6;
      const n = opt(o, 'stems', 2 + Math.floor(r() * 2)), trunks = [];
      for (let i = 0; i < n; i++) {
        const a = i / n * 6.283 + r() * 0.8, lean = 0.3 + r() * 0.35;
        trunks.push({ at: [Math.cos(a) * 0.08, -0.05, Math.sin(a) * 0.08], dir: [Math.cos(a) * Math.sin(lean), Math.cos(lean), Math.sin(a) * Math.sin(lean)], len: (2.0 + r() * 0.8) * kh, rad: 0.11 + r() * 0.06, az: a });
      }
      const S = {
        trunks, flare: 0.25, roots: 0, minRad: 0.008,
        levels: [
          { step: 0.3, wander: 0.45, up: 0.02, spread: 0.02, taper: 0.62 },
          { n: 3, t0: 0.6, t1: 1.0, angle: 0.7, angleJit: 0.5, lenK: 1.25 * k, radK: 0.72, shorten: 0.2, step: 0.35, wander: 0.5, up: 0.02, droop: 0.09, spread: 0.07, taper: 0.3 },
          { n: 5, t0: 0.2, t1: 1.0, angle: 0.95, angleJit: 0.5, lenK: 0.5, radK: 0.55, shorten: 0.3, step: 0.3, wander: 0.55, up: 0.02, droop: 0.06, taper: 0.35 },
          { n: 3, t0: 0.3, t1: 1.0, angle: 0.9, angleJit: 0.5, lenK: 0.5, radK: 0.5, shorten: 0.2, step: 0.25, wander: 0.5, droop: 0.04, taper: 0.4 },
        ],
        leaves: { per: 1, from: 0.6, size: [0.45, 0.7], lift: 0.05 },
        envelope: { rx: SP / 2, rz: SP / 2 * (0.85 + r() * 0.25), y0: H * 0.62, ry: H * 0.38, base: H * 0.42, flatBottom: 2.5 },
        shell: { n: 260, size: [0.5, 0.8], thick: 0.35, skirt: 0.3, below: 0.4, gaps: 0.02, lobe: 0.2 },
      };
      return makeTree(S, r, { bark: 'mesquite', leafKey: 'mesq', leaf: MESQ_LEAF, cards: 7, colors: [0xfff8e0, 0xf2f0d0, 0xffffff, 0xe8eac8], fol: { squash: 0.55, aoMin: 0.6 }, budget: 30000 });
    },
  });

  /* =======================================================================================
   * cedar_elm — Ulmus crassifolia
   * ===================================================================================== */
  const ELM_LEAF = { shape: 'ellipse', leaf: [17, 10], colors: ['#3a5528', '#50702f', '#678a3c'], twig: '#3b322a', twigW: 2.5, density: 9, angle: 1.1, serrate: true, branchy: 3 };
  K.define('cedar_elm', {
    size: [9, 12, 9],
    options: { height: 12, spread: 9 },
    note: 'Options: height m, spread m. Cedar elm: a straight grey scaly trunk, ascending limbs, slightly weeping outer twigs and an upright oval crown of small, rough, dark leaves, a little open, the commonest native street elm in Texas.',
    make(o, r) {
      const H = opt(o, 'height', 12), SP = opt(o, 'spread', 9), k = SP / 9, kh = H / 12;
      const tH = (3.0 + r() * 0.8) * kh;
      const S = {
        trunks: [{ at: [0, -0.1, 0], dir: [(r() - 0.5) * 0.1, 1, (r() - 0.5) * 0.1], len: tH + 0.1, rad: 0.24 * Math.max(0.6, kh), az: r() * 6.3 }],
        flare: 0.35, roots: 5, floor: 2.4 * kh, minRad: 0.01,
        levels: [
          { step: 0.5, wander: 0.06, up: 0.03, taper: 0.7 },
          { n: 5, t0: 0.7, t1: 1.0, angle: 0.5, angleJit: 0.3, lenK: 2.3 * kh, radK: 0.62, shorten: 0.1, step: 0.55, wander: 0.18, up: 0.04, droop: 0.05, spread: 0.02, taper: 0.25 },
          { n: 7, t0: 0.2, t1: 0.98, angle: 0.8, angleJit: 0.4, lenK: 0.42, radK: 0.5, shorten: 0.35, step: 0.4, wander: 0.3, up: 0.03, droop: 0.08, taper: 0.3 },
          { n: 4, t0: 0.3, t1: 1.0, angle: 0.8, angleJit: 0.5, lenK: 0.5, radK: 0.5, shorten: 0.3, step: 0.3, wander: 0.35, droop: 0.1, taper: 0.35 },
        ],
        leaves: { per: 2, from: 0.3, size: [0.5, 0.75], lift: 0.05 },
        envelope: { rx: SP / 2, rz: SP / 2 * (0.9 + r() * 0.15), y0: H * 0.6, ry: H * 0.42, base: H * 0.3, hollow: 0.5 },
        shell: { n: 900, size: [0.55, 0.85], thick: 0.25, skirt: 0.75, below: 0.8, gaps: -0.18, lobe: 0.14 },
      };
      return makeTree(S, r, { bark: 'elm', leafKey: 'elm', leaf: ELM_LEAF, cards: 10, colors: [0xfff4d8, 0xf0ecc8, 0xffffff, 0xe4e4c4] });
    },
  });

  /* =======================================================================================
   * ashe_juniper — Juniperus ashei, the Hill Country "cedar"
   * ===================================================================================== */
  const JUN_LEAF = { shape: 'scale', leaf: [38, 7], colors: ['#2c3c2a', '#3b4f34', '#4d633f'], twig: '#4a3a2e', twigW: 3, density: 5, angle: 0.7, berries: '#7c8fb0', branchy: 3, alphaTest: 0.4 };
  K.define('ashe_juniper', {
    size: [5, 6, 5],
    options: { height: 6, spread: 5 },
    note: 'Options: height m, spread m. Ashe juniper, the Hill Country cedar: several shaggy, shredding, reddish-grey stems from the ground, a dense irregular rounded-conical crown of dark blue-green scale foliage in ropey sprays carried nearly to the ground, a few frosted blue berries.',
    make(o, r) {
      const H = opt(o, 'height', 6), SP = opt(o, 'spread', 5), k = SP / 5, kh = H / 6;
      const n = 2 + Math.floor(r() * 3), trunks = [];
      for (let i = 0; i < n; i++) {
        const a = i / n * 6.283 + r(), lean = 0.12 + r() * 0.3;
        trunks.push({ at: [Math.cos(a) * 0.1, -0.05, Math.sin(a) * 0.1], dir: [Math.cos(a) * Math.sin(lean), Math.cos(lean), Math.sin(a) * Math.sin(lean)], len: (2.4 + r()) * kh, rad: 0.08 + r() * 0.06, az: a });
      }
      const S = {
        trunks, flare: 0.3, minRad: 0.008,
        levels: [
          { step: 0.35, wander: 0.25, up: 0.05, taper: 0.4 },
          { n: 7, t0: 0.1, t1: 1.0, angle: 0.8, angleJit: 0.4, lenK: 0.55 * k, radK: 0.55, shorten: 0.6, step: 0.3, wander: 0.35, up: 0.06, droop: 0.03, spread: 0.04, taper: 0.3 },
          { n: 4, t0: 0.3, t1: 1.0, angle: 0.7, angleJit: 0.4, lenK: 0.5, radK: 0.5, shorten: 0.3, step: 0.25, wander: 0.4, up: 0.04, taper: 0.35 },
        ],
        leaves: { per: 2, from: 0.3, size: [0.4, 0.6], lift: 0.05 },
        envelope: { rx: SP / 2, rz: SP / 2 * (0.85 + r() * 0.25), y0: H * 0.38, ry: H * 0.62, base: 0.35, flatBottom: 1.2, hollow: 0.45 },
        shell: { n: 1400, size: [0.42, 0.62], thick: 0.25, skirt: 0.6, below: 0.55, gaps: -0.25, lobe: 0.18 },
      };
      // a juniper narrows toward its top: pull the upper shell in
      const g = makeTree(Object.assign(S, { taperTop: true }), r, { bark: 'juniper', leafKey: 'juniper', leaf: JUN_LEAF, cards: 10, colors: [0xf2f6ee, 0xe4ecea, 0xffffff, 0xdce6dc] });
      return g;
    },
  });

  /* =======================================================================================
   * pecan — Carya illinoinensis, the state tree
   * ===================================================================================== */
  const PECAN_LEAF = { shape: 'pinnate', leaf: [120, 13], leaflets: 6, colors: ['#4c6a2a', '#668a34', '#84a444'], twig: '#3e3428', twigW: 3, density: 2, angle: 0.8, branchy: 2, alphaTest: 0.4 };
  K.define('pecan', {
    size: [16, 22, 16],
    options: { height: 22, spread: 16 },
    note: 'Options: height m, spread m. The pecan, Texas state tree: a tall, straight, grey, scaly trunk clear for five or six metres, big ascending scaffold limbs, and a high, open, rounded-oval crown of long compound yellow-green leaves.',
    make(o, r) {
      const H = opt(o, 'height', 22), SP = opt(o, 'spread', 16), k = SP / 16, kh = H / 22;
      const tH = (5.5 + r() * 1.5) * kh;
      const S = {
        trunks: [{ at: [0, -0.1, 0], dir: [(r() - 0.5) * 0.08, 1, (r() - 0.5) * 0.08], len: tH + 0.1, rad: 0.38 * Math.max(0.6, kh), az: r() * 6.3 }],
        flare: 0.35, roots: 6, floor: 5 * kh, minRad: 0.012,
        levels: [
          { step: 0.6, wander: 0.05, up: 0.03, taper: 0.75 },
          { n: 5, t0: 0.72, t1: 1.0, angle: 0.55, angleJit: 0.3, lenK: 1.65 * kh, radK: 0.6, shorten: 0.1, step: 0.7, wander: 0.16, up: 0.05, droop: 0.04, spread: 0.02, taper: 0.25 },
          { n: 8, t0: 0.2, t1: 0.98, angle: 0.75, angleJit: 0.4, lenK: 0.42, radK: 0.5, shorten: 0.35, step: 0.5, wander: 0.25, up: 0.04, droop: 0.05, taper: 0.3 },
          { n: 4, t0: 0.3, t1: 1.0, angle: 0.8, angleJit: 0.5, lenK: 0.5, radK: 0.5, shorten: 0.3, step: 0.4, wander: 0.3, droop: 0.05, taper: 0.35 },
        ],
        leaves: { per: 2, from: 0.3, size: [0.8, 1.2], lift: 0.05 },
        envelope: { rx: SP / 2, rz: SP / 2 * (0.9 + r() * 0.15), y0: H * 0.62, ry: H * 0.38, base: H * 0.33, hollow: 0.5, flatBottom: 1.4 },
        shell: { n: 950, size: [0.9, 1.35], thick: 0.25, skirt: 0.7, below: 0.7, gaps: -0.1, lobe: 0.2 },
      };
      return makeTree(S, r, { bark: 'pecan', leafKey: 'pecan', leaf: PECAN_LEAF, cards: 10, colors: [0xfff6d8, 0xf6f2c8, 0xffffff, 0xeae8c0] });
    },
  });

  /* =======================================================================================
   * crape_myrtle — Lagerstroemia, every Texas parking strip in July
   * ===================================================================================== */
  const CRAPE_LEAF = { shape: 'ellipse', leaf: [26, 14], colors: ['#35532a', '#4a6c30', '#5f823c'], twig: '#6a5040', twigW: 2.5, density: 7, angle: 0.9, gloss: true, branchy: 2 };
  const BLOOMS = { pink: ['#c8407a', '#e46c9e', '#f4a0c4'], white: ['#dcd8d0', '#f4f2ee', '#ffffff'], red: ['#9c1c30', '#c43048', '#e0506a'], lavender: ['#8a6aa8', '#a88ac4', '#c8b0dc'] };
  K.define('crape_myrtle', {
    size: [4.5, 5.5, 4.5],
    options: { height: 5.5, spread: 4.5, bloom: 'pink', stems: null },
    note: 'Options: height m, spread m, bloom pink|white|red|lavender (or false for none), stems (null = seeded 4 to 6). Crape myrtle: four to six smooth, sinuous, exfoliating stems in cinnamon, tan and grey patches rising in a vase, a rounded head of small glossy leaves, and crinkled flower panicles held above it.',
    make(o, r) {
      const H = opt(o, 'height', 5.5), SP = opt(o, 'spread', 4.5), k = SP / 4.5, kh = H / 5.5;
      const n = opt(o, 'stems', 4 + Math.floor(r() * 3)), trunks = [];
      for (let i = 0; i < n; i++) {
        const a = i / n * 6.283 + r() * 0.6, lean = 0.2 + r() * 0.2;
        trunks.push({ at: [Math.cos(a) * 0.12, -0.05, Math.sin(a) * 0.12], dir: [Math.cos(a) * Math.sin(lean), Math.cos(lean), Math.sin(a) * Math.sin(lean)], len: (2.6 + r() * 0.6) * kh, rad: 0.05 + r() * 0.03, az: a });
      }
      const S = {
        trunks, flare: 0.3, minRad: 0.006,
        levels: [
          { step: 0.3, wander: 0.22, up: 0.03, spread: 0.02, taper: 0.6 },
          { n: 4, t0: 0.55, t1: 1.0, angle: 0.5, angleJit: 0.3, lenK: 0.5 * kh, radK: 0.65, shorten: 0.2, step: 0.3, wander: 0.3, up: 0.06, spread: 0.03, taper: 0.35 },
          { n: 4, t0: 0.3, t1: 1.0, angle: 0.6, angleJit: 0.4, lenK: 0.5, radK: 0.5, shorten: 0.3, step: 0.2, wander: 0.35, up: 0.05, taper: 0.4 },
        ],
        leaves: { per: 2, from: 0.4, size: [0.35, 0.5], lift: 0.05 },
        envelope: { rx: SP / 2, rz: SP / 2 * (0.9 + r() * 0.15), y0: H * 0.66, ry: H * 0.34, base: H * 0.42, flatBottom: 2 },
        shell: { n: 520, size: [0.35, 0.55], thick: 0.3, skirt: 0.5, below: 0.8, gaps: -0.2, lobe: 0.15 },
      };
      const bloom = opt(o, 'bloom', 'pink');
      return makeTree(S, r, { bark: 'crape', leafKey: 'crape', leaf: CRAPE_LEAF, cards: 9, colors: [0xfff6e0, 0xf2f0d4, 0xffffff, 0xe6e8cc], budget: 36000,
        extra: bloom && BLOOMS[bloom] ? (g, res, rr) => {
          // panicles: on the upper shell, sitting proud of the leaves
          const top = res.clusters.filter((c) => c[1] > S.envelope.y0 - 0.2).sort(() => 0).filter(() => rr() < 0.55).slice(0, 150)
            .map((c) => [c[0] + (c[0]) * 0.04, c[1] + 0.15, c[2] + c[2] * 0.04, 0.32 + rr() * 0.12]);
          const spec = { shape: 'bloom', leaf: [60, 26], colors: BLOOMS[bloom], twig: '#6a5040', twigW: 2, density: 2, angle: 0.4, branchy: 1, alphaTest: 0.4, rough: 0.7 };
          foliage(g, top, leafMat('bloom|' + bloom, spec), 'bloom|geo', 6, [0xffffff, 0xf4f0f0, 0xfff4f8], rr, { squash: 1.1, aoMin: 0.75 });
        } : null });
    },
  });

  /* =======================================================================================
   * shrub — a clipped hedge or a mounded shrub: boxwood or yaupon holly
   * ===================================================================================== */
  const SHRUB_LEAF = {
    boxwood: { shape: 'ellipse', leaf: [14, 8], colors: ['#3c5a24', '#557a2c', '#6e9436'], twig: '#5a4a34', twigW: 2, density: 11, angle: 1.0, gloss: true, branchy: 3 },
    yaupon: { shape: 'ellipse', leaf: [16, 9], colors: ['#2c4222', '#3c5a2a', '#4e6e34'], twig: '#6a6258', twigW: 2, density: 9, angle: 1.0, gloss: true, branchy: 3, berries: '#c0281e' },
  };
  K.define('shrub', {
    size: [3, 1.2, 0.9],
    options: { kind: 'boxwood', form: 'hedge', length: 3, height: 1.2, depth: 0.9 },
    note: 'Options: kind boxwood|yaupon (yaupon carries red berries), form hedge|mound, length, height, depth m (a mound uses length as its diameter). A foundation hedge sheared flat with softly rounded shoulders, or a loose mounded shrub: thousands of small glossy leaves over a dark leafy core, a few stems showing at the foot. A hedge runs along x.',
    make(o, r) {
      const g = new THREE.Group();
      const kind = opt(o, 'kind', 'boxwood'), form = opt(o, 'form', 'hedge');
      const L = opt(o, 'length', 3), H = opt(o, 'height', 1.2), D = opt(o, 'depth', 0.9);
      const core = mat('shrubcore|' + kind, () => new THREE.MeshStandardMaterial({ color: kind === 'yaupon' ? 0x1c2a16 : 0x22341a, roughness: 0.95 }));
      const pts = [];
      if (form === 'hedge') {
        const c = TXT.roundedBox(L - 0.12, H - 0.16, D - 0.12, 0.18, core, { segments: 3 }); c.position.y = (H - 0.16) / 2 + 0.1; g.add(c);
        // clusters over the top and the four sides, shoulders rounded, the foot tucked in
        const area = [L * D, L * H, L * H, D * H, D * H], tot = area.reduce((a, b) => a + b, 0), N = 1500;
        for (let i = 0; i < N; i++) {
          let f = r() * tot, face = 0; while (f > area[face]) { f -= area[face]; face++; }
          let x, y, z;
          if (face === 0) { x = (r() - 0.5) * L; z = (r() - 0.5) * D; y = H; }
          else if (face < 3) { x = (r() - 0.5) * L; y = r() * H; z = (face === 1 ? 1 : -1) * D / 2; }
          else { z = (r() - 0.5) * D; y = r() * H; x = (face === 3 ? 1 : -1) * L / 2; }
          // round the shoulders and tuck the foot
          const sh = 0.2, dx = Math.max(0, Math.abs(x) - (L / 2 - sh)), dz = Math.max(0, Math.abs(z) - (D / 2 - sh)), dy = Math.max(0, y - (H - sh));
          const cut = Math.hypot(dx, dz, dy) > sh ? (Math.hypot(dx, dz, dy) - sh) : 0;
          if (cut > 0) { const s = sh / Math.hypot(dx, dz, dy); x = Math.sign(x) * ((L / 2 - sh) + dx * s); z = Math.sign(z) * ((D / 2 - sh) + dz * s); y = (H - sh) + dy * s * (dy > 0 ? 1 : 0) + (dy > 0 ? 0 : y - (H - sh)); }
          if (y < 0.25) { const t = y / 0.25; x *= 0.92 + 0.08 * t; z *= 0.8 + 0.2 * t; }
          pts.push([x + (r() - 0.5) * 0.05, Math.min(H, y) - 0.06, z + (r() - 0.5) * 0.05, 0.16 + r() * 0.08]);
        }
      } else {
        const R = L / 2;
        const c = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 16), core); c.scale.set(R * 0.85, H * 0.45, R * 0.85); c.position.y = H * 0.5; g.add(c);
        for (let i = 0; i < 1200; i++) {
          const u = r() * 1.2 - 0.2, th = r() * 6.283, sq = Math.sqrt(1 - u * u);
          const d = 0.9 + r() * 0.12;
          pts.push([sq * Math.cos(th) * R * d, H * 0.5 + u * H * 0.5 * d, sq * Math.sin(th) * R * d, 0.18 + r() * 0.1]);
        }
      }
      // a few stems at the foot
      const wood = { pos: [], nor: [], uv: [], idx: [] };
      for (let i = 0; i < Math.max(3, Math.round(L * 2)); i++) {
        const x = (r() - 0.5) * (form === 'hedge' ? L - 0.4 : L * 0.5), z = (r() - 0.5) * (form === 'hedge' ? D - 0.4 : L * 0.5);
        taperTube([new V3(x, -0.03, z), new V3(x + (r() - 0.5) * 0.1, 0.2, z + (r() - 0.5) * 0.1), new V3(x + (r() - 0.5) * 0.2, 0.45, z + (r() - 0.5) * 0.2)], [0.025, 0.02, 0.012], 5, wood);
      }
      g.add(woodMesh(wood, barkMat('elm')));
      foliage(g, pts, leafMat('shrub|' + kind, SHRUB_LEAF[kind]), 'shrub|geo', 9, [0xffffff, 0xf0f4e0, 0xf8f4dc], r, { squash: 0.9, aoMin: 0.62 });
      return g;
    },
  });

  /* =======================================================================================
   * palm — Washingtonia robusta, the Mexican fan palm of the Valley and Houston
   * ===================================================================================== */
  function fanTexture(dead) {
    return texture('fan|' + (dead ? 1 : 0), 1024, 512, (x, W, H, r) => {
      // polar leaf unrolled: u = around the fan (0..1), v = out from the hastula (0 at bottom row)
      x.clearRect(0, 0, W, H);
      const n = 36, c0 = dead ? [118, 92, 60] : [70, 102, 44], c1 = dead ? [160, 128, 86] : [104, 138, 60];
      for (let i = 0; i < n; i++) {
        const u0 = i / n * W, u1 = (i + 1) / n * W, cc = mix(c0, c1, r());
        const split = 0.45 + r() * 0.15, tip = 0.9 + r() * 0.1;
        // a segment: solid to the split, then a tapering, slightly ragged strap
        const g = x.createLinearGradient(u0, 0, u1, 0);
        g.addColorStop(0, css(cc, 0.78)); g.addColorStop(0.5, css(cc, 1.08)); g.addColorStop(1, css(cc, 0.78));
        x.fillStyle = g; x.beginPath();
        x.moveTo(u0, H); x.lineTo(u1, H);
        x.lineTo(u1, H * (1 - split)); x.lineTo((u0 + u1) / 2 + (u1 - u0) * 0.08, H * (1 - tip)); x.lineTo(u0 + (u1 - u0) * 0.1, H * (1 - split));
        x.closePath(); x.fill();
        // filaments hanging from the splits (robusta has few; a young leaf has more)
        if (r() < 0.4) { x.strokeStyle = css(cc, 0.9, 0.9); x.lineWidth = 1.5; x.beginPath(); x.moveTo(u1, H * (1 - split)); x.lineTo(u1 + (r() - 0.5) * 8, H * (1 - split - 0.25)); x.stroke(); }
        if (dead) { for (let k = 0; k < 6; k++) { x.fillStyle = 'rgba(60,40,20,0.25)'; x.fillRect(u0 + r() * (u1 - u0), H * r(), 2, 10 + r() * 30); } }
      }
      grain(x, W, H, 0.25);
    });
  }
  // one fan leaf, along +x from the origin (the hastula), lying roughly in the xz plane, pleated
  function fanGeo(segs, rings, R, spread, fold, droop) {
    const P = [], U = [], idx = [];
    const cols = segs * 2;
    for (let j = 0; j <= rings; j++) for (let i = 0; i <= cols; i++) {
      const t = i / cols, a = -spread + t * 2 * spread, rr = (j / rings) * R;
      const f = (i % 2 ? 1 : -1) * fold * (j / rings);
      // costapalmate: the midrib runs a third into the blade, so the blade arches along it
      const x = Math.cos(a) * rr, z = Math.sin(a) * rr;
      const y = f - droop * Math.pow(j / rings, 2) * (0.6 + 0.4 * Math.abs(Math.sin(a))) + 0.12 * R * (1 - Math.abs(a) / spread) * (j / rings);
      P.push(x, y, z); U.push(t, j / rings);
    }
    for (let j = 0; j < rings; j++) for (let i = 0; i < cols; i++) {
      const a = j * (cols + 1) + i, b = a + cols + 1;
      idx.push(a, a + 1, b, a + 1, b + 1, b);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(U, 2));
    g.setIndex(idx); g.computeVertexNormals();
    // lit as a sheet facing up: blend the pleat normals toward +y so the fold reads but never flips
    const n = g.attributes.normal;
    for (let i = 0; i < n.count; i++) { const v = new V3(n.getX(i), Math.abs(n.getY(i)) + 0.8, n.getZ(i)).normalize(); n.setXYZ(i, v.x, v.y, v.z); }
    return g;
  }
  K.define('palm', {
    size: [5, 16, 5],
    options: { height: 16, skirt: true, lean: null },
    note: 'Options: height m, skirt (the petticoat of dead fronds) bool, lean radians (null = seeded). Washingtonia robusta, the Mexican fan palm of the Rio Grande Valley and Houston: a tall, slender, ringed grey trunk flaring at the foot with a gentle curve, a brown petticoat of dead fronds hanging under the head, and a crown of about two dozen bright green costapalmate fans on long petioles, the young ones upright and the old ones drooping.',
    make(o, r) {
      const g = new THREE.Group();
      const H = opt(o, 'height', 16), lean = opt(o, 'lean', (r() - 0.5) * 0.12), az = r() * 6.283;
      // trunk: a curved, tapering tube, flared at the foot, rings in the bark
      const pts = [], radii = [], n = 24;
      for (let i = 0; i <= n; i++) {
        const t = i / n, y = t * H - 0.1;
        const off = Math.sin(t * 2.2) * lean * H * 0.35;
        pts.push(new V3(Math.cos(az) * off, y, Math.sin(az) * off));
        radii.push(0.19 + 0.2 * Math.exp(-t * H * 1.6) + 0.02 * (1 - t));
      }
      const wood = { pos: [], nor: [], uv: [], idx: [] };
      taperTube(pts, radii, 14, wood);
      g.add(woodMesh(wood, barkMat('palm')));
      const top = pts[n], head = top.clone().add(new V3(0, 0.3, 0));
      // the boot: a knot of old leaf bases at the head
      const boot = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.22, 1.1, 14), mat('palmboot', () => new THREE.MeshStandardMaterial({ color: 0x6e5a40, roughness: 0.95, map: TEXC.get('bark|palm') || null })));
      boot.position.copy(top).add(new V3(0, 0.2, 0)); g.add(boot);
      const green = mat('frond', () => oneFace(new THREE.MeshStandardMaterial({ map: fanTexture(false), alphaTest: 0.4, side: THREE.DoubleSide, roughness: 0.62, envMapIntensity: 0.6 })));
      const brown = mat('frond-dead', () => oneFace(new THREE.MeshStandardMaterial({ map: fanTexture(true), alphaTest: 0.4, side: THREE.DoubleSide, roughness: 0.9 })));
      const petM = mat('petiole', () => new THREE.MeshStandardMaterial({ color: 0x8a8a5a, roughness: 0.7 }));
      const fan = fanGeo(18, 5, 0.85, 1.9, 0.07, 0.28), dead = fanGeo(8, 3, 0.8, 1.6, 0.05, 0.1);
      const pet = new THREE.CylinderGeometry(0.018, 0.035, 1, 6); pet.translate(0, 0.5, 0); pet.rotateZ(-Math.PI / 2);   // along +x, length 1
      const live = 22 + Math.floor(r() * 6), deadN = opt(o, 'skirt', true) ? 46 : 8;
      const imF = new THREE.InstancedMesh(fan, green, live), imP = new THREE.InstancedMesh(pet, petM, live);
      const imD = new THREE.InstancedMesh(dead, brown, deadN);
      const Mx = new THREE.Matrix4(), M2 = new THREE.Matrix4(), q = new THREE.Quaternion(), c = new THREE.Color();
      for (let i = 0; i < live; i++) {
        // golden-angle around the head; elevation from upright (young) to drooping (old)
        const a = i * 2.39996 + r() * 0.3, t = i / live, el = 1.15 - t * 1.7 + (r() - 0.5) * 0.25, pl = 1.1 + r() * 0.5;
        const dir = new V3(Math.cos(a) * Math.cos(el), Math.sin(el), Math.sin(a) * Math.cos(el));
        q.setFromUnitVectors(new V3(1, 0, 0), dir);
        // keep the blade roughly face-up: roll about the petiole so its local y is as close to world up as it can be
        const upL = new V3(0, 1, 0).applyQuaternion(q), want = new V3(0, 1, 0).sub(dir.clone().multiplyScalar(dir.y)).normalize();
        const roll = Math.atan2(upL.clone().cross(want).dot(dir), upL.dot(want));
        const qr = new THREE.Quaternion().setFromAxisAngle(dir, roll + (r() - 0.5) * 0.4); q.premultiply(qr);
        Mx.compose(head, q, new V3(pl, 1, 1)); imP.setMatrixAt(i, Mx);
        const tip = head.clone().addScaledVector(dir, pl);
        const s = 0.9 + r() * 0.25;
        Mx.compose(tip, q, new V3(s, s, s)); imF.setMatrixAt(i, Mx);
        c.setRGB(0.85 + r() * 0.2, 0.9 + r() * 0.15, 0.8 + r() * 0.15); imF.setColorAt(i, c);
      }
      for (let i = 0; i < deadN; i++) {
        // the petticoat: dead fans hanging down against the trunk, overlapping like thatch
        const a = i * 2.39996 + r() * 0.4, ring = Math.floor(i / 12), y = head.y - 0.5 - ring * 0.75 - r() * 0.4;
        const dir = new V3(Math.cos(a) * 0.18, -1, Math.sin(a) * 0.18).normalize();
        q.setFromUnitVectors(new V3(1, 0, 0), dir);
        const out = new V3(Math.cos(a), 0, Math.sin(a));
        const upL = new V3(0, 1, 0).applyQuaternion(q), roll = Math.atan2(upL.clone().cross(out).dot(dir), upL.dot(out));
        q.premultiply(new THREE.Quaternion().setFromAxisAngle(dir, roll));
        const base = new V3(top.x + Math.cos(a) * 0.32, y, top.z + Math.sin(a) * 0.32), s = 0.9 + r() * 0.3;
        Mx.compose(base, q, new V3(s * 1.1, s, s * 0.8)); imD.setMatrixAt(i, Mx);
        c.setRGB(0.8 + r() * 0.3, 0.75 + r() * 0.3, 0.7 + r() * 0.25); imD.setColorAt(i, c);
      }
      [imF, imP, imD].forEach((m) => { m.instanceMatrix.needsUpdate = true; if (m.instanceColor) m.instanceColor.needsUpdate = true; g.add(m); });
      return g;
    },
  });
}
