/* kit/civic.js — the public realm of Texas: the buildings its decisions are made in and the
 * street furniture those decisions pay for. See assets/js/txkit.js for the conventions.
 *
 * Everything here is built through one local Builder that bakes transforms into geometry and
 * merges every part that shares a material into one mesh, so a courthouse with four hundred
 * window parts is a dozen draw calls. Textured materials get box UVs in metres after the
 * transform, so a brick is a brick's size on every face.
 *
 * Flags and sign faces are COLOUR AND GEOMETRY, never text: the Texas flag is a blue hoist
 * stripe, a white star, white over red; the stop sign legend is drawn as stroked paths. */
export function install(K, THREE, TXT) {
  const V3 = THREE.Vector3, PI = Math.PI;

  // K.make merges only { seed: 1 } under the caller's options, so each model's own defaults are
  // merged here: every option has a default and K.make(name) always works.
  function def(name, spec) {
    const make = spec.make, defaults = spec.options || {};
    K.define(name, Object.assign({}, spec, { make(o, r) { return make(Object.assign({}, defaults, o), r); } }));
  }

  /* ================================ materials ================================ */
  const MC = new Map();
  function mat(key, P, phys) {
    if (!MC.has(key)) {
      const p = Object.assign({ roughness: 0.8, metalness: 0 }, P);
      MC.set(key, phys ? new THREE.MeshPhysicalMaterial(p) : new THREE.MeshStandardMaterial(p));
    }
    return MC.get(key);
  }
  // a K.tex surface: white base, the map carries the colour, UVs in metres by the Builder
  function tmat(tex, color, rough, extra) {
    const key = 't|' + tex + '|' + color + '|' + rough + '|' + JSON.stringify(extra || {});
    if (!MC.has(key)) {
      const map = K.tex(tex, { color });
      const m = new THREE.MeshStandardMaterial(Object.assign({ color: 0xffffff, roughness: rough, metalness: 0, map }, extra || {}));
      m.userData.uvm = map.userData.metres;
      MC.set(key, m);
    }
    return MC.get(key);
  }
  // a local canvas surface (granite, asphalt, standing seam, faces), cached by key
  const CT = new Map();
  function ctex(key, W, H, paint, metres) {
    if (CT.has(key)) return CT.get(key);
    const c = document.createElement('canvas'); c.width = W; c.height = H;
    paint(c.getContext('2d'), W, H);
    const t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
    t.userData.metres = metres || 1;
    CT.set(key, t);
    return t;
  }
  function cmat(key, tex, rough, extra) {
    if (!MC.has(key)) {
      const m = new THREE.MeshStandardMaterial(Object.assign({ color: 0xffffff, roughness: rough, metalness: 0, map: tex }, extra || {}));
      m.userData.uvm = tex.userData.metres;
      MC.set(key, m);
    }
    return MC.get(key);
  }
  function hash(n) { let s = n >>> 0 || 1; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  function rgb(hex, k) {
    const c = parseInt(hex.slice(1), 16), f = (v) => Math.max(0, Math.min(255, Math.round(v * k)));
    return 'rgb(' + f(c >> 16) + ',' + f((c >> 8) & 255) + ',' + f(c & 255) + ')';
  }
  function speckle(x, W, H, r, a) {
    const im = x.getImageData(0, 0, W, H), d = im.data;
    for (let i = 0; i < d.length; i += 4) { const k = 1 + (r() - 0.5) * 2 * a; d[i] *= k; d[i + 1] *= k; d[i + 2] *= k; }
    x.putImageData(im, 0, 0);
  }
  // cut granite ashlar, 2.4 m tile: 0.6 m courses of 1.2 m blocks, pink Texas granite speckle
  function granite(color) {
    return ctex('granite|' + color, 512, 512, (x, W, H) => {
      const r = hash(7331);
      x.fillStyle = rgb(color, 0.82); x.fillRect(0, 0, W, H);
      const rows = 4, h = H / rows, per = 2, w = W / per;
      for (let j = 0; j < rows; j++) {
        const off = (j % 2) * w / 2;
        for (let i = -1; i <= per; i++) { x.fillStyle = rgb(color, 0.9 + r() * 0.16); x.fillRect(i * w + off + 2, j * h + 2, w - 4, h - 4); }
      }
      for (let i = 0; i < 9000; i++) {
        const k = r(); x.fillStyle = k < 0.45 ? 'rgba(40,30,30,0.35)' : k < 0.8 ? 'rgba(255,240,230,0.3)' : 'rgba(150,70,60,0.35)';
        x.fillRect(r() * W, r() * H, 1 + r() * 2, 1 + r() * 2);
      }
      speckle(x, W, H, r, 0.05);
    }, 2.4);
  }
  // asphalt: aggregate, a few tar snakes (crack seal), 4 m tile
  function asphaltTex(tone) {
    return ctex('asph|' + tone, 1024, 1024, (x, W, H) => {
      const r = hash(4242);
      x.fillStyle = rgb(tone, 1); x.fillRect(0, 0, W, H);
      for (let i = 0; i < 60000; i++) { const g = 40 + r() * 120; x.fillStyle = 'rgba(' + g + ',' + g + ',' + (g - 4) + ',' + (0.1 + r() * 0.25) + ')'; x.fillRect(r() * W, r() * H, 1 + r() * 2.5, 1 + r() * 2.5); }
      for (let i = 0; i < 14; i++) {  // big soft patches: oil, patching, sun bleach
        const gx = r() * W, gy = r() * H, rad = 60 + r() * 220, gr = x.createRadialGradient(gx, gy, 0, gx, gy, rad);
        const dark = r() < 0.6; gr.addColorStop(0, dark ? 'rgba(10,10,12,0.16)' : 'rgba(200,200,195,0.08)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
        x.fillStyle = gr; x.fillRect(0, 0, W, H);
      }
      x.strokeStyle = 'rgba(12,12,14,0.85)'; x.lineCap = 'round';
      for (let i = 0; i < 5; i++) {       // tar snakes: the Texas crack seal
        x.lineWidth = 5 + r() * 5; let px = r() * W, py = r() * H; x.beginPath(); x.moveTo(px, py);
        for (let k = 0; k < 10; k++) { px += (r() - 0.5) * 160; py += (r() - 0.3) * 90; x.lineTo(px, py); }
        x.stroke();
      }
      speckle(x, W, H, r, 0.08);
    }, 4);
  }
  // standing seam metal roof: ribs every 0.45 m, 1.8 m tile (u across the slope)
  function seamTex(color) {
    return ctex('seam|' + color, 256, 256, (x, W, H) => {
      const r = hash(99);
      x.fillStyle = rgb(color, 1); x.fillRect(0, 0, W, H);
      const n = 4, w = W / n;
      for (let i = 0; i < n; i++) {
        const g = x.createLinearGradient(i * w, 0, i * w + w, 0);
        g.addColorStop(0, rgb(color, 0.78)); g.addColorStop(0.08, rgb(color, 1.12)); g.addColorStop(0.2, rgb(color, 0.98));
        g.addColorStop(0.9, rgb(color, 1.02)); g.addColorStop(1, rgb(color, 0.86));
        x.fillStyle = g; x.fillRect(i * w, 0, w, H);
      }
      speckle(x, W, H, r, 0.05);
    }, 1.8);
  }

  // shared finishes
  const F = {
    glass: () => K.finish.glass(),
    glass2: () => mat('glass2', { color: 0x3a4750, metalness: 0.25, roughness: 0.05, clearcoat: 1, clearcoatRoughness: 0.04, envMapIntensity: 1.5 }, true),
    blind: () => mat('blind', { color: 0xa39c8e, metalness: 0.1, roughness: 0.25, clearcoat: 1, clearcoatRoughness: 0.05, envMapIntensity: 1.2 }, true),
    lit: () => mat('litroom', { color: 0x6a5a44, emissive: 0xffc98a, emissiveIntensity: 0.18, roughness: 0.1, clearcoat: 1, clearcoatRoughness: 0.04 }, true),
    tintGlass: () => mat('tintglass', { color: 0x1f3440, metalness: 0.45, roughness: 0.04, clearcoat: 1, clearcoatRoughness: 0.03, envMapIntensity: 1.9 }, true),
    alum: () => mat('alum', { color: 0xbfc3c6, metalness: 0.8, roughness: 0.38 }),
    bronze: () => mat('bronzeal', { color: 0x3b3029, metalness: 0.55, roughness: 0.45 }),
    black: () => mat('blackpc', { color: 0x1d1e20, metalness: 0.3, roughness: 0.5 }),
    whiteTrim: () => mat('whitetrim', { color: 0xe9e5dc, roughness: 0.55 }),
    door: () => mat('doorwood', { color: 0x4a2f1f, roughness: 0.55 }),
    castStone: (c) => tmat('limestone', c || '#dcd0b4', 0.85),
    roofDeck: () => mat('roofdeck', { color: 0x9a9890, roughness: 0.95 }),
    concrete: () => tmat('concrete', '#b2ada3', 0.92),
    paint: (c) => mat('paint|' + c, { color: c, roughness: 0.5, metalness: 0.1 }),
    gold: () => mat('gold', { color: 0xd8ab4c, metalness: 1, roughness: 0.25 }),
    galv: () => K.finish.galvanized(),
  };

  /* ================================ the Builder ================================ */
  function Builder() {
    const buckets = new Map(), boxes = new Map(), stack = [new THREE.Matrix4()], tv = new V3();
    const tmpM = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), one = new V3(1, 1, 1);
    const B = {
      get M() { return stack[stack.length - 1]; },
      push(x, y, z, ry) {
        q.setFromEuler(e.set(0, ry || 0, 0));
        stack.push(B.M.clone().multiply(new THREE.Matrix4().compose(new V3(x || 0, y || 0, z || 0), q, one)));
      },
      pop() { stack.pop(); },
      // add a geometry at local (x,y,z) with rotation (rx,ry,rz) under the current frame
      geo(g, m, x, y, z, rx, ry, rz, ownUV) {
        q.setFromEuler(e.set(rx || 0, ry || 0, rz || 0, 'YXZ'));
        tmpM.compose(new V3(x || 0, y || 0, z || 0), q, one);
        g.applyMatrix4(B.M.clone().multiply(tmpM));
        if (m.userData.uvm) {
          if (ownUV) { const uv = g.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) / m.userData.uvm, uv.getY(i) / m.userData.uvm); }
          else K.uvBox(g, m.userData.uvm);
        }
        if (!buckets.has(m)) buckets.set(m, []);
        buckets.get(m).push(g);
        return g;
      },
      // box with its BASE at y0, centred on x and z
      box(m, w, h, d, x, y0, z, ry) { B.boxc(m, w, h, d, x, (y0 || 0) + h / 2, z, 0, ry || 0, 0); },
      // box centred at (x,y,z) with rotation
      // boxes are the bulk of every building: recorded as a transform and baked from one template
      boxc(m, w, h, d, x, y, z, rx, ry, rz) {
        q.setFromEuler(e.set(rx || 0, ry || 0, rz || 0, 'YXZ'));
        tmpM.compose(tv.set(x || 0, y || 0, z || 0), q, one).premultiply(B.M);
        B.inst(m, UBT, x, y, z, rx, ry, rz, w, h, d, true);
      },
      // an instance of a cached template geometry, baked at flush (no per-copy objects)
      inst(m, T, x, y, z, rx, ry, rz, sx, sy, sz, done) {
        if (!done) { q.setFromEuler(e.set(rx || 0, ry || 0, rz || 0, 'YXZ')); tmpM.compose(tv.set(x || 0, y || 0, z || 0), q, one).premultiply(B.M); }
        if (!boxes.has(m)) boxes.set(m, new Map());
        const MM = boxes.get(m); if (!MM.has(T)) MM.set(T, []);
        const L = MM.get(T), el = tmpM.elements;
        for (let i = 0; i < 16; i++) L.push(el[i]);
        L.push(sx || 1, sy || 1, sz || 1);
      },
      rbox(m, w, h, d, rad, x, y0, z, ry, seg) {
        const t = TXT.roundedBox(w, h, d, rad, m, { segments: seg || 2 });
        return B.geo(t.geometry, m, x, (y0 || 0) + h / 2, z, 0, ry || 0, 0);
      },
      cyl(m, rt, rb, h, x, y0, z, seg, open) {
        return B.geo(new THREE.CylinderGeometry(rt, rb, h, seg || 20, 1, !!open), m, x, (y0 || 0) + h / 2, z);
      },
      // a bar between two points in the current frame
      bar(m, a, b, rad, seg) {
        const A = new V3(a[0], a[1], a[2]), Bv = new V3(b[0], b[1], b[2]), len = A.distanceTo(Bv);
        const g = new THREE.CylinderGeometry(rad, rad, len, seg || 8);
        const qq = new THREE.Quaternion().setFromUnitVectors(new V3(0, 1, 0), Bv.clone().sub(A).normalize());
        const mm = new THREE.Matrix4().compose(A.clone().add(Bv).multiplyScalar(0.5), qq, one);
        g.applyMatrix4(B.M.clone().multiply(mm));
        if (m.userData.uvm) K.uvBox(g, m.userData.uvm);
        if (!buckets.has(m)) buckets.set(m, []);
        buckets.get(m).push(g);
        return g;
      },
      lathe(m, prof, seg, x, y0, z) { return B.geo(new THREE.LatheGeometry(prof.map(p => new THREE.Vector2(p[0], p[1])), seg || 24), m, x, y0, z); },
      tube(m, pts, rad, segs, radial) {
        const c = new THREE.CatmullRomCurve3(pts.map(p => new V3(p[0], p[1], p[2])));
        return B.geo(new THREE.TubeGeometry(c, segs || 24, rad, radial || 8, false), m);
      },
      // an extruded 2D shape standing in the local xy plane, depth along +z starting at z
      extrude(m, shape, depth, x, y, z, ry, curveSeg) {
        const g = new THREE.ExtrudeGeometry(shape, { depth, bevelEnabled: false, curveSegments: curveSeg || 14 });
        return B.geo(g, m, x, y, z, 0, ry || 0, 0);
      },
      // planar polygons with UVs in metres along each face's own axes
      poly(m, faces) { return B.geo(polyGeo(faces), m, 0, 0, 0, 0, 0, 0, true); },
      flush(group) {
        boxes.forEach((MM, m) => { if (!buckets.has(m)) buckets.set(m, []); MM.forEach((L, T) => buckets.get(m).push(bakeBoxes(L, m.userData.uvm, T))); });
        buckets.forEach((list, m) => { const mesh = new THREE.Mesh(mergeGeos(list), m); group.add(mesh); });
        buckets.clear(); boxes.clear();
        return group;
      },
    };
    return B;
  }
  // templates: geometry baked once, instanced by transform. key -> {P, N, U, I, nv, ni}
  const TPL = new Map();
  function tplOf(g) {
    if (!g.index) { const n = g.attributes.position.count, ix = new Uint32Array(n); for (let i = 0; i < n; i++) ix[i] = i; g.setIndex(new THREE.BufferAttribute(ix, 1)); }
    if (!g.attributes.normal) g.computeVertexNormals();
    const P = g.attributes.position.array, U = g.attributes.uv ? g.attributes.uv.array : new Float32Array(P.length / 3 * 2);
    return { P, N: g.attributes.normal.array, U, I: g.index.array, nv: P.length / 3, ni: g.index.count };
  }
  function tpl(key, make) { if (!TPL.has(key)) TPL.set(key, tplOf(make())); return TPL.get(key); }
  const UBT = tplOf(new THREE.BoxGeometry(1, 1, 1));
  function bakeBoxes(L, uvm, T) {
    const UP = T.P, UN = T.N, UU = T.U, UI = T.I, NV = T.nv, NI = T.ni;
    const nb = L.length / 19, pos = new Float32Array(nb * NV * 3), nor = new Float32Array(nb * NV * 3), uv = new Float32Array(nb * NV * 2), idx = new Uint32Array(nb * NI);
    for (let b = 0; b < nb; b++) {
      const o = b * 19, w = L[o + 16], h = L[o + 17], d = L[o + 18];
      const e0 = L[o], e1 = L[o + 1], e2 = L[o + 2], e4 = L[o + 4], e5 = L[o + 5], e6 = L[o + 6], e8 = L[o + 8], e9 = L[o + 9], e10 = L[o + 10];
      for (let v = 0; v < NV; v++) {
        const px = UP[v * 3] * w, py = UP[v * 3 + 1] * h, pz = UP[v * 3 + 2] * d, k = (b * NV + v) * 3;
        const X = e0 * px + e4 * py + e8 * pz + L[o + 12], Y = e1 * px + e5 * py + e9 * pz + L[o + 13], Z = e2 * px + e6 * py + e10 * pz + L[o + 14];
        let nx = UN[v * 3], ny = UN[v * 3 + 1], nz = UN[v * 3 + 2];
        if (w !== h || h !== d) { nx /= w; ny /= h; nz /= d; const l = Math.hypot(nx, ny, nz) || 1; nx /= l; ny /= l; nz /= l; }
        const NX = e0 * nx + e4 * ny + e8 * nz, NY = e1 * nx + e5 * ny + e9 * nz, NZ = e2 * nx + e6 * ny + e10 * nz;
        pos[k] = X; pos[k + 1] = Y; pos[k + 2] = Z; nor[k] = NX; nor[k + 1] = NY; nor[k + 2] = NZ;
        const t = (b * NV + v) * 2;
        if (uvm) {
          const ax = Math.abs(NX), ay = Math.abs(NY), az = Math.abs(NZ);
          if (ay >= ax && ay >= az) { uv[t] = X / uvm; uv[t + 1] = Z / uvm; }
          else if (ax >= az) { uv[t] = Z / uvm; uv[t + 1] = Y / uvm; }
          else { uv[t] = X / uvm; uv[t + 1] = Y / uvm; }
        } else { uv[t] = UU[v * 2]; uv[t + 1] = UU[v * 2 + 1]; }
      }
      for (let i = 0; i < NI; i++) idx[b * NI + i] = UI[i] + b * NV;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
    g.setAttribute('uv', new THREE.BufferAttribute(uv, 2)); g.setIndex(new THREE.BufferAttribute(idx, 1));
    return g;
  }
  function mergeGeos(list) {
    let nv = 0, ni = 0;
    list.forEach((g) => {
      if (!g.index) { const n = g.attributes.position.count, idx = new Uint32Array(n); for (let i = 0; i < n; i++) idx[i] = i; g.setIndex(new THREE.BufferAttribute(idx, 1)); }
      if (!g.attributes.normal) g.computeVertexNormals();
      nv += g.attributes.position.count; ni += g.index.count;
    });
    const pos = new Float32Array(nv * 3), nor = new Float32Array(nv * 3), uv = new Float32Array(nv * 2), idx = new Uint32Array(ni);
    let vo = 0, io = 0;
    list.forEach((g) => {
      const P = g.attributes.position, N = g.attributes.normal, U = g.attributes.uv, I = g.index.array, n = P.count;
      pos.set(P.array.subarray(0, n * 3), vo * 3); nor.set(N.array.subarray(0, n * 3), vo * 3);
      if (U) uv.set(U.array.subarray(0, n * 2), vo * 2);
      for (let k = 0; k < I.length; k++) idx[io + k] = I[k] + vo;
      vo += n; io += I.length; g.dispose();
    });
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
    geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
    geo.setIndex(new THREE.BufferAttribute(idx, 1));
    geo.computeBoundingSphere();
    return geo;
  }
  // faces: array of point lists [[x,y,z],...] (planar, convex, counter clockwise seen from outside)
  function polyGeo(faces) {
    const pos = [], uv = [];
    faces.forEach((f) => {
      const P = f.map(p => new V3(p[0], p[1], p[2]));
      const t = P[1].clone().sub(P[0]).normalize();
      const n = P[1].clone().sub(P[0]).cross(P[2].clone().sub(P[0])).normalize();
      const b = n.clone().cross(t);
      const U = P.map(p => [p.clone().sub(P[0]).dot(t), p.clone().sub(P[0]).dot(b)]);
      for (let i = 1; i < P.length - 1; i++) {
        [0, i, i + 1].forEach((k) => { pos.push(P[k].x, P[k].y, P[k].z); uv.push(U[k][0], U[k][1]); });
      }
    });
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
    g.computeVertexNormals();
    return g;
  }
  // a hip roof over a w x d rectangle from eave height 0, ridge at h (pyramid when w == d)
  function hipRoof(B, m, w, d, h, x, y, z) {
    const hw = w / 2, hd = d / 2, rr = Math.max(0, (w - d) / 2), rz = Math.max(0, (d - w) / 2);
    const p = (a, b, c) => [x + a, y + b, z + c];
    const A = p(-hw, 0, hd), Bp = p(hw, 0, hd), C = p(hw, 0, -hd), D = p(-hw, 0, -hd);
    const R1 = p(-rr, h, -rz), R2 = p(rr, h, -rz), R3 = p(rr, h, rz), R4 = p(-rr, h, rz);
    // front (+z), right (+x), back, left; each listed CCW from outside, starting on the eave
    const faces = [[A, Bp, R3, R4], [Bp, C, R2, R3], [C, D, R1, R2], [D, A, R4, R1]]
      .map(f => f.filter((v, i, arr) => arr.findIndex(u => u[0] === v[0] && u[1] === v[1] && u[2] === v[2]) === i));
    B.poly(m, faces);
  }
  // a gable roof: ridge along z (length len from z0 forward), span w, rise h, at eave height y
  function gableRoof(B, m, w, len, h, x, y, z0) {
    const hw = w / 2, z1 = z0 + len;
    B.poly(m, [
      [[x + hw, y, z1], [x + hw, y, z0], [x, y + h, z0], [x, y + h, z1]],
      [[x - hw, y, z0], [x - hw, y, z1], [x, y + h, z1], [x, y + h, z0]],
    ]);
  }
  // shapes
  function archPath(s, hw, y0, hr, first) {
    if (first) s.moveTo(-hw, y0);
    s.lineTo(hw, y0); s.lineTo(hw, hr); s.absarc(0, hr, hw, 0, PI, false); s.lineTo(-hw, y0);
    return s;
  }
  function archShape(w, hr) { return archPath(new THREE.Shape(), w / 2, 0, hr, true); }
  // an arch-topped ring of width t around an opening w wide with spring line hr (open at the bottom)
  function archU(w, hr, t) {
    const o = w / 2 + t, i = w / 2, s = new THREE.Shape();
    s.moveTo(o, 0); s.lineTo(o, hr); s.absarc(0, hr, o, 0, PI, false); s.lineTo(-o, 0);
    s.lineTo(-i, 0); s.lineTo(-i, hr); s.absarc(0, hr, i, PI, 0, true); s.lineTo(i, 0); s.lineTo(o, 0);
    return s;
  }
  // a solid wall panel ww x hh with an arched opening w wide, spring line hr, centred at x = 0
  function archWall(ww, hh, w, hr) {
    const s = new THREE.Shape(), i = w / 2;
    s.moveTo(-ww / 2, 0); s.lineTo(-i, 0); s.lineTo(-i, hr); s.absarc(0, hr, i, PI, 0, true);
    s.lineTo(i, 0); s.lineTo(ww / 2, 0); s.lineTo(ww / 2, hh); s.lineTo(-ww / 2, hh); s.lineTo(-ww / 2, 0);
    return s;
  }
  function pointedShape(w, hr, rise) {  // a Gothic lancet: two arcs meeting at a point
    const s = new THREE.Shape(), hw = w / 2, rad = (hw * hw + rise * rise) / (2 * hw);
    s.moveTo(-hw, 0); s.lineTo(hw, 0); s.lineTo(hw, hr);
    const a0 = Math.atan2(rise, hw - rad);       // from centre (-rad+hw, hr)
    s.absarc(hw - rad, hr, rad, 0, a0, false);
    s.absarc(-hw + rad, hr, rad, PI - a0, PI, false);
    s.lineTo(-hw, 0);
    return s;
  }
  function triShape(w, h) { const s = new THREE.Shape(); s.moveTo(-w / 2, 0); s.lineTo(w / 2, 0); s.lineTo(0, h); s.lineTo(-w / 2, 0); return s; }

  /* ================================ windows ================================ */
  /* In a FACADE FRAME: x along the wall, y up, the wall face at z = 0, +z outward. The pane sits
   * proud of the wall and a surround projects further, so the glass reads as set back in a
   * reveal. `M` = { frame, glass:[mats], trim, sill }. */
  function rectWin(B, M, r, x, y0, w, h, o) {
    o = o || {};
    const tw = o.tw != null ? o.tw : 0.16, td = o.td != null ? o.td : 0.2, f = o.f || 0.055;
    const g = M.glass[Math.floor(r() * M.glass.length)];
    const blind = o.noBlind ? 0 : (r() < 0.35 ? 0.2 + r() * 0.45 : 0);
    if (blind) { B.box(F.blind(), w, h * blind, 0.02, x, y0 + h * (1 - blind), 0.03); B.box(g, w, h * (1 - blind), 0.02, x, y0, 0.03); }
    else B.box(g, w, h, 0.02, x, y0, 0.03);
    const fd = 0.07, fz = 0.045;
    B.box(M.frame, w, f, fd, x, y0, fz); B.box(M.frame, w, f, fd, x, y0 + h - f, fz);
    B.box(M.frame, f, h, fd, x - w / 2 + f / 2, y0, fz); B.box(M.frame, f, h, fd, x + w / 2 - f / 2, y0, fz);
    const cols = o.cols || 1, rows = o.rows != null ? o.rows : 2;
    for (let i = 1; i < cols; i++) B.box(M.frame, f * 0.7, h, fd * 0.8, x - w / 2 + (w * i) / cols, y0, fz);
    for (let j = 1; j < rows; j++) B.box(M.frame, w, f * (j === 1 && rows === 2 ? 1.2 : 0.6), fd * 0.8, x, y0 + (h * j) / rows, fz + 0.01);
    if (M.trim && tw > 0) {
      B.box(M.trim, tw, h + 0.02, td, x - w / 2 - tw / 2, y0, td / 2);
      B.box(M.trim, tw, h + 0.02, td, x + w / 2 + tw / 2, y0, td / 2);
      const hh = o.headH || tw * 1.6;
      B.box(M.trim, w + 2 * tw + (o.headX || 0.14), hh, td + 0.04, x, y0 + h, (td + 0.04) / 2);
      if (o.keystone) B.box(M.trim, 0.28, hh + 0.12, td + 0.08, x, y0 + h - 0.06, (td + 0.08) / 2);
      if (o.cap) B.box(M.trim, w + 2 * tw + 0.34, 0.1, td + 0.14, x, y0 + h + hh, (td + 0.14) / 2);
    }
    if (M.sill) B.box(M.sill, w + 2 * tw + 0.12, 0.09, td + 0.1, x, y0 - 0.09, (td + 0.1) / 2);
  }
  function archWin(B, M, r, x, y0, w, h, o) {
    o = o || {};
    const hr = h - w / 2, tw = o.tw != null ? o.tw : 0.2, td = o.td != null ? o.td : 0.22, f = o.f || 0.06;
    const g = M.glass[Math.floor(r() * M.glass.length)];
    const kk = w.toFixed(3) + '|' + hr.toFixed(3);
    B.inst(g, tpl('ag|' + kk, () => new THREE.ShapeGeometry(archShape(w, hr), 16)), x, y0, 0.035);
    // frame: the arch ring, a transom at the spring line and a centre mullion
    B.inst(M.frame, tpl('ar|' + kk + '|' + f, () => {
      const ring = new THREE.Shape(); archPath(ring, w / 2, 0, hr, true);
      ring.holes.push(archPath(new THREE.Path(), w / 2 - f, f, hr, true));
      return new THREE.ExtrudeGeometry(ring, { depth: 0.07, bevelEnabled: false, curveSegments: 14 }); }), x, y0, 0.01);
    B.box(M.frame, w, f, 0.075, x, y0 + hr - f / 2, 0.045);
    if (o.mullion !== false) B.box(M.frame, f * 0.8, hr + w / 2 - 0.02, 0.07, x, y0, 0.045);
    if (h > 2.4 && o.meet !== false) B.box(M.frame, w, f, 0.075, x, y0 + hr * 0.5, 0.045);
    if (M.trim && tw > 0) {
      B.inst(M.trim, tpl('au|' + kk + '|' + tw + '|' + td, () => new THREE.ExtrudeGeometry(archU(w, hr, tw), { depth: td, bevelEnabled: false, curveSegments: 14 })), x, y0, 0);
      if (o.keystone !== false) B.box(M.trim, 0.3, tw + 0.2, td + 0.06, x, y0 + h - 0.05, (td + 0.06) / 2);
    }
    if (M.sill) B.box(M.sill, w + 2 * tw + 0.14, 0.1, td + 0.1, x, y0 - 0.1, (td + 0.1) / 2);
  }
  // a pair of panelled doors under a glazed transom, in a facade frame
  function doors(B, x, y0, w, h, o) {
    o = o || {};
    const dm = o.mat || F.door(), fr = o.frame || F.whiteTrim(), leaf = w / 2 - 0.04;
    B.box(mat('doorshadow', { color: 0x17130f, roughness: 0.9 }), w + 0.1, h + 0.05, 0.02, x, y0, 0.01);
    [-1, 1].forEach((s) => {
      const cx = x + s * (leaf / 2 + 0.02);
      B.box(dm, leaf, h, 0.06, cx, y0, 0.04);
      // raised panels and a glazed upper light
      B.box(dm, leaf - 0.2, h * 0.3, 0.03, cx, y0 + 0.15, 0.08);
      B.box(o.glazed === false ? dm : F.glass(), leaf - 0.2, h * 0.45, 0.03, cx, y0 + h * 0.45 + 0.05, 0.075);
      B.box(F.gold(), 0.03, 0.26, 0.05, cx - s * (leaf / 2 - 0.1), y0 + 0.95, 0.1);
    });
    B.box(fr, w + 0.24, 0.12, 0.1, x, y0 + h, 0.05);
    B.box(fr, 0.12, h, 0.1, x - w / 2 - 0.06, y0, 0.05); B.box(fr, 0.12, h, 0.1, x + w / 2 + 0.06, y0, 0.05);
  }
  // a stair of n risers from the ground to `top`, w wide, running out toward +z from z0
  function stairs(B, m, w, top, z0, o) {
    o = o || {};
    const n = Math.max(2, Math.round(top / 0.165)), rh = top / n, tr = o.tread || 0.32;
    for (let i = 0; i < n; i++) B.box(m, w, rh * (n - i), tr + 0.02, o.x || 0, 0, z0 + i * tr + tr / 2);
    if (o.cheek) {
      const run = n * tr;
      [-1, 1].forEach((s) => {
        const cx = (o.x || 0) + s * (w / 2 + o.cheek / 2), sh = new THREE.Shape();
        sh.moveTo(0, 0); sh.lineTo(run + 0.25, 0); sh.lineTo(run + 0.25, 0.5); sh.lineTo(0.3, top + 0.55); sh.lineTo(0, top + 0.55); sh.lineTo(0, 0);
        B.geo(new THREE.ExtrudeGeometry(sh, { depth: o.cheek, bevelEnabled: false }), o.cheekMat || m, cx - o.cheek / 2, 0, z0, 0, -PI / 2, 0);
      });
    }
    if (o.rail) {
      const run = n * tr;
      [-1, 1].forEach((s) => {
        const rx = (o.x || 0) + s * (w / 2 - 0.25);
        B.bar(o.rail, [rx, top + 0.9, z0 - 0.2], [rx, 0.9 + rh, z0 + run - tr], 0.022, 8);
        for (let k = 0; k <= 2; k++) { const t = k / 2, zz = z0 + t * (run - tr), yy = top - t * (top - rh); B.bar(o.rail, [rx, yy, zz], [rx, yy + 0.9, zz], 0.02, 6); }
      });
    }
    return n * tr;
  }
  // balustrade from x0 to x1 in a facade frame at height y0, top at y0 + h
  function balustrade(B, m, x0, x1, y0, z, h, o) {
    o = o || {};
    const L = x1 - x0, sp = o.spacing || 0.3, n = Math.max(1, Math.floor(L / sp));
    B.box(m, L, 0.14, 0.34, (x0 + x1) / 2, y0, z);
    B.box(m, L + 0.06, 0.13, 0.4, (x0 + x1) / 2, y0 + h - 0.13, z);
    const bh = h - 0.27, prof = [[0, 0], [0.075, 0], [0.075, 0.05], [0.05, 0.09], [0.085, 0.3], [0.04, 0.6], [0.055, 0.68], [0.07, 0.72], [0.07, 1], [0, 1]].map(p => [p[0] * (h / 0.95), p[1] * bh]);
    const every = o.posts || 3.2;
    let last = x0;
    for (let i = 0; i < n; i++) {
      const bx = x0 + (i + 0.5) * (L / n);
      if (bx - last > every) { B.box(m, 0.4, bh, 0.4, bx, y0 + 0.14, z); last = bx; continue; }
      B.inst(m, tpl('bal|' + h, () => new THREE.LatheGeometry(prof.map(p => new THREE.Vector2(p[0], p[1])), 8)), bx, y0 + 0.14, z);
    }
    B.box(m, 0.42, bh, 0.42, x0 + 0.21, y0 + 0.14, z); B.box(m, 0.42, bh, 0.42, x1 - 0.21, y0 + 0.14, z);
  }
  // a Classical column standing on y0: plinth, torus base, tapering shaft, bell capital, abacus
  function column(B, m, x, y0, z, h, rad, o) {
    o = o || {};
    const pl = rad * 0.28, ab = rad * 0.3;
    B.box(m, rad * 2.7, pl, rad * 2.7, x, y0, z);
    const sh = h - pl - ab;
    const prof = [[0, 0], [rad * 1.25, 0], [rad * 1.28, rad * 0.12], [rad * 1.12, rad * 0.26], [rad * 1.05, rad * 0.3], [rad, rad * 0.42],
      [rad * 0.97, sh * 0.35], [rad * 0.86, sh * 0.86], [rad * 0.9, sh * 0.88], [rad * 0.88, sh * 0.9],
      [rad * (o.corinth ? 0.92 : 0.95), sh * 0.92], [rad * (o.corinth ? 1.25 : 1.1), sh - 0.02], [rad * 1.2, sh], [0, sh]];
    B.inst(m, tpl('col|' + rad + '|' + sh.toFixed(3) + '|' + !!o.corinth, () => new THREE.LatheGeometry(prof.map(p => new THREE.Vector2(p[0], p[1])), 20)), x, y0 + pl, z);
    if (o.corinth) { // acanthus bands: two rings of lobes read as a Corinthian bell at distance
      for (let k = 0; k < 8; k++) {
        const a = (k / 8) * PI * 2;
        B.boxc(m, rad * 0.32, rad * 0.62, rad * 0.22, x + Math.cos(a) * rad * 1.02, y0 + pl + sh - rad * 0.55, z + Math.sin(a) * rad * 1.02, -0.25, -a + PI / 2, 0);
      }
    }
    B.box(m, rad * 2.6, ab, rad * 2.6, x, y0 + pl + sh, z);
  }
  // pediment in a facade frame: base at y0, span w, rise h, projecting from z0 to z1
  function pediment(B, wall, trim, w, h, y0, z0, z1) {
    B.extrude(wall, triShape(w - 0.3, h - 0.18), z1 - z0 - 0.25, 0, y0, z0);
    const ang = Math.atan2(h, w / 2), sl = Math.hypot(w / 2, h) + 0.25;
    [-1, 1].forEach((s) => B.boxc(trim, sl, 0.42, z1 - z0 + 0.15, s * w / 4, y0 + h / 2 + 0.05, (z0 + z1) / 2, 0, 0, -s * ang));
    B.box(trim, w + 0.3, 0.28, z1 - z0 + 0.2, 0, y0 - 0.02, (z0 + z1) / 2 + 0.05);
  }
  // dentil course: small blocks along a facade line
  function dentils(B, m, x0, x1, y, z, o) {
    const sp = (o && o.sp) || 0.28, n = Math.floor((x1 - x0) / sp);
    for (let i = 0; i < n; i++) B.box(m, sp * 0.5, 0.16, 0.14, x0 + (i + 0.5) * sp, y, z);
  }
  // clock dial, cream enamel with black bars, no numerals: cached canvas
  function dialTex() {
    return ctex('dial', 256, 256, (x, W) => {
      const c = W / 2;
      x.fillStyle = '#efe9d8'; x.beginPath(); x.arc(c, c, c - 2, 0, PI * 2); x.fill();
      x.strokeStyle = '#1b1b1b'; x.lineWidth = 10; x.beginPath(); x.arc(c, c, c - 8, 0, PI * 2); x.stroke();
      x.lineWidth = 2; x.beginPath(); x.arc(c, c, c - 30, 0, PI * 2); x.stroke();
      for (let i = 0; i < 60; i++) {
        const a = (i / 60) * PI * 2, big = i % 5 === 0, r0 = c - 14, r1 = big ? c - 40 : c - 24;
        x.lineWidth = big ? 9 : 2; x.beginPath(); x.moveTo(c + Math.cos(a) * r0, c + Math.sin(a) * r0); x.lineTo(c + Math.cos(a) * r1, c + Math.sin(a) * r1); x.stroke();
      }
    }, 1);
  }
  // a clock face in a facade frame centred at (x, y), radius rad
  function clock(B, r, x, y, rad, trim) {
    const dm = mat('dialm', { map: dialTex(), roughness: 0.45 });
    const g = new THREE.CircleGeometry(rad, 40);
    const uv = g.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i), 1 - uv.getY(i));
    B.geo(g, dm, x, y, 0.06);
    B.geo(new THREE.TorusGeometry(rad + 0.08, 0.11, 8, 40), trim, x, y, 0.06);
    const hands = F.black(), hr = r() * PI * 2, mr = r() * PI * 2;
    B.boxc(hands, 0.09, rad * 0.55, 0.03, x + Math.sin(hr) * rad * 0.25, y + Math.cos(hr) * rad * 0.25, 0.1, 0, 0, -hr);
    B.boxc(hands, 0.06, rad * 0.85, 0.03, x + Math.sin(mr) * rad * 0.38, y + Math.cos(mr) * rad * 0.38, 0.12, 0, 0, -mr);
  }

  /* ================================ flags ================================ */
  function starPath(x, cx, cy, R) {
    x.beginPath();
    for (let i = 0; i < 10; i++) { const a = -PI / 2 + (i * PI) / 5, rr = i % 2 ? R * 0.382 : R; x.lineTo(cx + Math.cos(a) * rr, cy + Math.sin(a) * rr); }
    x.closePath();
  }
  function flagTex(kind) {
    return ctex('flag|' + kind, 768, 512, (x, W, H) => {
      if (kind === 'texas') {           // Tex. Gov't Code 3100.002: blue third at the hoist, white over red
        x.fillStyle = '#002868'; x.fillRect(0, 0, W / 3, H);
        x.fillStyle = '#ffffff'; x.fillRect(W / 3, 0, W, H / 2);
        x.fillStyle = '#bf0a30'; x.fillRect(W / 3, H / 2, W, H / 2);
        // the star's circumscribed diameter is three fourths of the blue stripe's width
        x.fillStyle = '#ffffff'; starPath(x, W / 6, H / 2, (W / 3) * 0.375); x.fill();
      } else if (kind === 'us') {
        for (let i = 0; i < 13; i++) { x.fillStyle = i % 2 ? '#ffffff' : '#b22234'; x.fillRect(0, (i * H) / 13, W, H / 13 + 1); }
        const ch = (H * 7) / 13, cw = H * 0.76;
        x.fillStyle = '#3c3b6e'; x.fillRect(0, 0, cw, ch);
        x.fillStyle = '#ffffff';
        for (let j = 0; j < 9; j++) { const n = j % 2 ? 5 : 6; for (let i = 0; i < n; i++) {
          const sx = (cw / 12) * (1 + 2 * i + (j % 2)), sy = (ch / 10) * (1 + j); starPath(x, sx, sy, H * 0.0616 * 0.5 * 0.9); x.fill(); } }
      } else {                           // a municipal flag: plain field, a disc device, no lettering
        x.fillStyle = kind; x.fillRect(0, 0, W, H);
        x.fillStyle = '#f2efe6'; x.beginPath(); x.arc(W / 2, H / 2, H * 0.28, 0, PI * 2); x.fill();
        x.fillStyle = kind; starPath(x, W / 2, H / 2, H * 0.2); x.fill();
      }
      const r = hash(kind.length * 31);
      speckle(x, W, H, r, 0.03);
    }, 1);
  }
  function flagMat(kind) {
    const key = 'flagm|' + kind;
    if (!MC.has(key)) MC.set(key, new THREE.MeshStandardMaterial({ map: flagTex(kind), roughness: 0.82, side: THREE.DoubleSide }));
    return MC.get(key);
  }
  // a flag flying toward +x from a hoist at the origin (top edge at y = 0), gently waving
  function flagMesh(kind, fw, r) {
    const g = new THREE.PlaneGeometry(fw, fw * 2 / 3, 28, 12);
    g.translate(fw / 2, -fw / 3, 0);
    const p = g.attributes.position, ph = r() * PI * 2, amp = fw * (0.06 + r() * 0.04);
    for (let i = 0; i < p.count; i++) {
      const t = p.getX(i) / fw, yy = p.getY(i) / fw;
      p.setZ(i, amp * t * Math.sin(t * 7.5 - ph + yy * 1.4) + amp * 0.4 * Math.sin(t * 15 - ph * 2) * t);
      p.setY(i, p.getY(i) - fw * 0.07 * t * t);
      p.setX(i, p.getX(i) * (1 - 0.04 * t));
    }
    g.computeVertexNormals();
    const m = new THREE.Mesh(g, flagMat(kind));
    return m;
  }
  /* a flagpole group: tapered satin aluminium, gold ball, halyard, cleat, concrete base.
   * flags top first, e.g. ['us','texas'] (the Texas flag flies below the US flag on one pole) */
  function flagpoleGroup(r, o) {
    const G = new THREE.Group(), B = Builder();
    const h = o.height, rb = 0.055 + h * 0.0035, rt = rb * 0.55;
    const pole = mat('flagpole', { color: 0xc9cdd1, metalness: 0.9, roughness: 0.3 });
    B.cyl(F.concrete(), 0.42, 0.45, 0.14, 0, 0, 0, 24);
    B.cyl(pole, rb * 1.8, rb * 1.9, 0.18, 0, 0.14, 0, 24);                    // flash collar
    B.cyl(pole, rt, rb, h, 0, 0.14, 0, 24);
    B.cyl(pole, rt * 1.3, rt * 1.3, 0.12, 0, h + 0.14, 0, 16);                 // revolving truck
    B.geo(new THREE.SphereGeometry(rt * 1.9, 20, 14), F.gold(), 0, h + 0.26 + rt * 1.7, 0);
    const fw = o.flag || Math.max(0.9, h * 0.19), kinds = o.flags;
    // halyard: two lines down the pole to a cleat
    const hal = mat('halyard', { color: 0xdedbd2, roughness: 0.7 });
    B.bar(hal, [rt + 0.02, h + 0.1, 0.02], [rb + 0.02, 1.25, 0.02], 0.006, 4);
    B.bar(hal, [rt + 0.02, h + 0.1, -0.02], [rb + 0.02, 1.25, -0.02], 0.006, 4);
    B.box(F.alum(), 0.04, 0.2, 0.05, rb + 0.02, 1.15, 0);
    B.flush(G);
    let y = h + 0.02;
    kinds.forEach((k) => {
      const f = flagMesh(k, fw, r); f.position.set(rt + 0.03, y, 0); f.rotation.y = o.fly || 0; G.add(f);
      y -= fw * 2 / 3 + 0.3;
    });
    return G;
  }

  /* ================================ street furniture ================================ */
  // the cobra head luminaire at the local origin (the arm enters from -x), hanging below
  function cobraHead(B) {
    const housing = mat('cobra', { color: 0x9ea3a6, metalness: 0.55, roughness: 0.4 });
    const g = new THREE.SphereGeometry(1, 28, 12, 0, PI * 2, 0, PI / 2); g.scale(0.4, 0.13, 0.19);
    B.geo(g, housing, 0.36, 0, 0);
    B.geo(new THREE.CylinderGeometry(0.075, 0.085, 0.3, 16), housing, -0.08, 0.02, 0, 0, 0, PI / 2);
    B.boxc(housing, 0.28, 0.12, 0.16, 0.02, 0.02, 0, 0, 0, 0);
    const lens = new THREE.SphereGeometry(1, 24, 8, 0, PI * 2, PI / 2, PI / 2); lens.scale(0.32, 0.06, 0.15);
    B.geo(lens, mat('cobralens', { color: 0xe8ecef, emissive: 0xfff1d6, emissiveIntensity: 0.12, roughness: 0.2, metalness: 0.1 }), 0.4, 0, 0);
    B.box(housing, 0.8, 0.03, 0.39, 0.36, -0.015, 0);                              // the door rim
    B.cyl(mat('photocell', { color: 0x2b2e33, roughness: 0.4 }), 0.045, 0.045, 0.07, 0.3, 0.12, 0, 12); // photocell
  }

  def('streetlight', {
    size: [0.7, 10.2, 3.0],
    options: { height: 9.1, reach: 2.4, finish: 'galvanized' },
    note: 'TxDOT cobra head on a davit arm: tapered galvanized pole on a breakaway base at the origin, the arm reaching +z',
    make(o, r) {
      const G = new THREE.Group(), B = Builder();
      const h = o.height, reach = o.reach, steel = o.finish === 'bronze' ? F.bronze() : F.galv();
      B.cyl(F.concrete(), 0.34, 0.36, 0.3, 0, 0, 0, 24);                          // foundation
      [-1, 1].forEach(sx => [-1, 1].forEach(sz => { B.cyl(steel, 0.018, 0.018, 0.12, sx * 0.17, 0.3, sz * 0.17, 6); B.cyl(steel, 0.035, 0.035, 0.03, sx * 0.17, 0.35, sz * 0.17, 6); }));
      B.rbox(mat('tbase', { color: 0xa7abad, metalness: 0.6, roughness: 0.45 }), 0.42, 0.62, 0.42, 0.02, 0, 0.3, 0);
      B.cyl(steel, 0.1, 0.105, 0.04, 0, 0.92, 0, 24);
      const bend = 1.1, top = h - 0.25;
      B.cyl(steel, 0.075, 0.105, top - bend - 0.96, 0, 0.96, 0, 24);
      // the davit: a quarter bend into a slightly rising arm toward +z
      const pts = [];
      for (let i = 0; i <= 10; i++) { const a = (i / 10) * (PI / 2); pts.push([0, top - bend + Math.sin(a) * bend, bend - Math.cos(a) * bend]); }
      pts.push([0, top + 0.08, reach - 0.25]);
      B.tube(steel, pts, 0.074, 40, 16);
      B.push(0, top + 0.1, reach - 0.3, -PI / 2);
      cobraHead(B);
      B.pop();
      B.box(steel, 0.12, 0.2, 0.012, 0, 2.6, 0.1);                                  // pole tag plate
      return B.flush(G);
    },
  });

  /* A traffic signal head, backplate facing +z: 3 x 12 in sections, visors, a retroreflective
   * yellow border on the backplate (TxDOT). lit: 0 red, 1 yellow, 2 green. */
  function signalHead(B, x, y, z, lit, housing) {
    const bp = mat('backplate', { color: 0x151617, roughness: 0.6 }), refl = mat('reflborder', { color: 0xf2c200, roughness: 0.35, emissive: 0x2a2000, emissiveIntensity: 0.3 });
    B.box(refl, 0.66, 1.4, 0.012, x, y - 1.32, z - 0.135);
    B.box(bp, 0.6, 1.34, 0.016, x, y - 1.29, z - 0.125);
    B.rbox(housing, 0.36, 1.12, 0.26, 0.03, x, y - 1.24, z, 0, 2);
    const cols = [0xd2231a, 0xf6a600, 0x10b36a];
    for (let i = 0; i < 3; i++) {
      const cy = y - 0.33 - i * 0.355, on = i === lit;
      const lm = mat('lens|' + i + '|' + on, on ? { color: cols[i], emissive: cols[i], emissiveIntensity: 1.6, roughness: 0.2 }
        : { color: new THREE.Color(cols[i]).multiplyScalar(0.18).getHex(), roughness: 0.15, metalness: 0.2 });
      B.geo(new THREE.CircleGeometry(0.15, 28), lm, x, cy, z + 0.135);
      B.geo(new THREE.CylinderGeometry(0.17, 0.17, 0.3, 20, 1, true, PI * 0.325, PI * 1.35), mat('visor', { color: 0x141516, roughness: 0.6, side: THREE.DoubleSide }), x, cy + 0.01, z + 0.28, PI / 2, 0, 0);
    }
    B.cyl(housing, 0.035, 0.035, 0.2, x, y - 0.1, z, 10);
  }

  def('traffic_signal', {
    size: [12.3, 10.5, 1.2],
    options: { arm: 12, heads: 3, finish: 'auto', luminaire: true, lit: 'auto' },
    note: 'Mast arm signal: the pole stands at the origin (its footprint), arm over +x, heads facing +z; street blade and a ped head on the pole',
    make(o, r) {
      const G = new THREE.Group(), B = Builder();
      const fin = o.finish === 'auto' ? (r() < 0.5 ? 'galvanized' : 'bronze') : o.finish;
      const steel = fin === 'bronze' ? F.bronze() : F.galv();
      const housing = r() < 0.55 ? mat('sighouse', { color: 0xe3b61b, roughness: 0.45 }) : mat('sighouseb', { color: 0x1e1f21, roughness: 0.5 });
      const L = o.arm, px = 0, ah = 6.4, lit = o.lit === 'auto' ? [0, 2, 2, 1][Math.floor(r() * 4)] : o.lit;
      B.push(px, 0, 0, 0);
      B.cyl(F.concrete(), 0.55, 0.58, 0.35, 0, 0, 0, 28);
      B.cyl(steel, 0.5 * 0.62, 0.5 * 0.62, 0.05, 0, 0.35, 0, 24);                 // base plate
      for (let i = 0; i < 8; i++) { const a = (i / 8) * PI * 2 + 0.2; B.cyl(steel, 0.03, 0.03, 0.14, Math.cos(a) * 0.26, 0.38, Math.sin(a) * 0.26, 6); }
      const ptop = o.luminaire ? 10.2 : 7.6;
      B.cyl(steel, 0.14, 0.2, ptop - 0.4, 0, 0.4, 0, 28);
      B.cyl(steel, 0.12, 0.12, 0.05, 0, ptop, 0, 20);
      // mast arm: tapered, rising slightly, clamped at a flange plate
      B.box(steel, 0.12, 0.7, 0.6, 0.2, ah - 0.35, 0);
      const arm = new THREE.CylinderGeometry(0.075, 0.15, L - 0.2, 24);
      B.geo(arm, steel, (L - 0.2) / 2 + 0.25, ah + (L - 0.2) / 2 * 0.03, 0, 0, 0, -PI / 2 + 0.03);
      B.cyl(steel, 0.08, 0.08, 0.02, L + 0.05, ah + L * 0.03, 0, 16);
      // heads, spaced toward the far end
      const n = o.heads;
      for (let i = 0; i < n; i++) {
        const hx = L * (0.42 + (0.55 * i) / Math.max(1, n - 1)), yy = ah + hx * 0.03 - 0.1;
        B.box(steel, 0.08, 0.18, 0.08, hx, yy, 0);
        signalHead(B, hx, yy, 0.05, lit, housing);
      }
      // street name blade on the arm: blank green, white border
      const bx = L * 0.2, by = ah + bx * 0.03 - 0.25;
      B.box(mat('blade-w', { color: 0xf1f1ec, roughness: 0.4 }), 2.3, 0.48, 0.02, bx, by - 0.44, 0.1);
      B.box(mat('blade-g', { color: 0x0f6b3c, roughness: 0.4 }), 2.24, 0.42, 0.024, bx, by - 0.41, 0.1);
      B.box(steel, 0.05, 0.3, 0.05, bx - 0.8, by - 0.1, 0.1); B.box(steel, 0.05, 0.3, 0.05, bx + 0.8, by - 0.1, 0.1);
      // luminaire on top of the pole
      if (o.luminaire) {
        const pts = []; for (let i = 0; i <= 8; i++) { const a = (i / 8) * (PI / 2); pts.push([0.9 - Math.cos(a) * 0.9, ptop - 0.9 + Math.sin(a) * 0.9, 0]); }
        pts.push([2.6, ptop + 0.05, 0]);
        B.tube(steel, pts, 0.055, 30, 12);
        B.push(2.6, ptop + 0.06, 0, 0); cobraHead(B); B.pop();
      }
      // pedestrian head and push button facing +z on the pole
      B.rbox(housing, 0.42, 0.46, 0.22, 0.02, 0, 2.7, 0.3, 0, 2);
      B.box(mat('pedface', { color: 0x221c16, emissive: 0xff8a1a, emissiveIntensity: 1.2, roughness: 0.3 }), 0.3, 0.32, 0.02, 0, 2.77, 0.42);
      B.box(mat('pedcowl', { color: 0x141516, roughness: 0.6 }), 0.44, 0.05, 0.18, 0, 3.12, 0.48);
      B.rbox(mat('pushb', { color: 0x2a2b2d, roughness: 0.5 }), 0.12, 0.18, 0.06, 0.01, 0.12, 1.02, 0.2, 0, 1);
      B.cyl(mat('pushbtn', { color: 0xd0d3d5, metalness: 0.9, roughness: 0.2 }), 0.025, 0.025, 0.02, 0.12, 1.1, 0.24, 12);
      B.pop();
      return B.flush(G);
    },
  });

  // STOP legend and white border on a red octagon, drawn as paths (no text rendering)
  function stopTex() {
    return ctex('stopface', 512, 512, (x, W) => {
      const oct = (rad) => { x.beginPath(); for (let i = 0; i < 8; i++) { const a = PI / 8 + (i * PI) / 4; x.lineTo(W / 2 + Math.cos(a) * rad, W / 2 + Math.sin(a) * rad); } x.closePath(); };
      x.fillStyle = '#f4f2ec'; oct(W / 2 / Math.cos(PI / 8)); x.fill();
      x.fillStyle = '#b3141b'; oct((W / 2 - 14) / Math.cos(PI / 8)); x.fill();
      // 10 in legend on a 30 in sign: a third of the height, strokes of about a fifth of that
      const h = W / 3, lw = h * 0.19, w = h * 0.6, gap = h * 0.13, tot = 4 * w + 3 * gap, x0 = (W - tot) / 2, y = (W - h) / 2;
      x.strokeStyle = '#f7f5ef'; x.fillStyle = '#f7f5ef'; x.lineWidth = lw; x.lineCap = 'butt';
      let cx = x0;
      { const R = (h - lw) / 4, mx = cx + w / 2;     // S
        x.beginPath(); x.arc(mx, y + lw / 2 + R, R, -0.12 * PI, 0.5 * PI, true); x.stroke();
        x.beginPath(); x.arc(mx, y + h - lw / 2 - R, R, -0.5 * PI, 0.88 * PI, false); x.stroke(); }
      cx += w + gap;
      x.fillRect(cx, y, w, lw); x.fillRect(cx + w / 2 - lw / 2, y, lw, h);   // T
      cx += w + gap;
      x.beginPath(); x.ellipse(cx + w / 2, y + h / 2, w / 2 - lw / 2, h / 2 - lw / 2, 0, 0, PI * 2); x.stroke();   // O
      cx += w + gap;
      x.fillRect(cx, y, lw, h);                           // P
      { const R2 = (h * 0.56 - lw) / 2; x.beginPath(); x.moveTo(cx, y + lw / 2); x.lineTo(cx + w - lw / 2 - R2, y + lw / 2);
        x.arc(cx + w - lw / 2 - R2, y + lw / 2 + R2, R2, -PI / 2, PI / 2, false); x.lineTo(cx, y + lw / 2 + 2 * R2); x.stroke(); }
      speckle(x, W, W, hash(5), 0.03);
    }, 1);
  }

  def('stop_sign', {
    size: [0.9, 3.3, 0.3],
    options: { blades: true, size: 0.762, post: 'square' },
    note: 'R1-1 stop sign, 30 in, bottom at 7 ft on a perforated square post; optional blank street blades on top',
    make(o, r) {
      const G = new THREE.Group(), B = Builder(), s = o.size, by = 2.13;
      const post = mat('perfpost', { color: 0xaeb2b4, metalness: 0.8, roughness: 0.45 });
      B.box(post, 0.05, by + s + (o.blades ? 0.62 : 0.05), 0.05, 0, 0, 0);
      for (let k = 0; k < 20; k++) B.box(mat('perfhole', { color: 0x25272a, roughness: 0.8 }), 0.012, 0.012, 0.052, 0, 0.3 + k * 0.1, 0);
      B.cyl(F.concrete(), 0.14, 0.16, 0.06, 0, 0, 0, 16);
      // octagon: face and aluminium blank behind
      const oct = new THREE.Shape(), R = s / 2 / Math.cos(PI / 8);
      for (let i = 0; i <= 8; i++) { const a = PI / 8 + (i * PI) / 4; if (i === 0) oct.moveTo(Math.cos(a) * R, Math.sin(a) * R); else oct.lineTo(Math.cos(a) * R, Math.sin(a) * R); }
      B.extrude(mat('signback', { color: 0xb9bdc0, metalness: 0.75, roughness: 0.4 }), oct, 0.003, 0, by + s / 2, 0.028);
      const face = new THREE.ShapeGeometry(oct);
      const uv = face.attributes.uv, p = face.attributes.position;
      for (let i = 0; i < uv.count; i++) uv.setXY(i, p.getX(i) / (2 * R * Math.cos(PI / 8)) + 0.5, p.getY(i) / (2 * R * Math.cos(PI / 8)) + 0.5);
      const fm = mat('stopfm', { map: stopTex(), roughness: 0.38, metalness: 0.05 });
      B.geo(face, fm, 0, by + s / 2, 0.0315);
      [by + 0.12, by + s - 0.12].forEach(yy => B.geo(new THREE.CylinderGeometry(0.012, 0.012, 0.01, 8), K.finish.chrome(), 0, yy, 0.036, PI / 2, 0, 0));
      if (o.blades) {
        const bw = mat('blade-w', { color: 0xf1f1ec, roughness: 0.4 }), bg = mat('blade-g', { color: 0x0f6b3c, roughness: 0.4 }), top = by + s + 0.1;
        B.box(post, 0.1, 0.06, 0.1, 0, top - 0.04, 0);
        B.box(bw, 1.22, 0.23, 0.012, 0, top + 0.02, 0); B.box(bg, 1.18, 0.19, 0.016, 0, top + 0.04, 0);
        B.box(bw, 0.012, 0.23, 1.22, 0, top + 0.3, 0); B.box(bg, 0.016, 0.19, 1.18, 0, top + 0.32, 0);
        B.box(post, 0.1, 0.06, 0.1, 0, top + 0.26, 0);
      }
      return B.flush(G);
    },
  });

  // a park bench's cast iron end frame in the yz plane (front +z), extruded along x
  function benchEnd() {
    const s = new THREE.Shape();
    s.moveTo(0.26, 0); s.lineTo(0.3, 0); s.lineTo(0.24, 0.42); s.lineTo(0.3, 0.62); s.lineTo(0.32, 0.66); s.lineTo(0.24, 0.66);
    s.lineTo(0.2, 0.58); s.lineTo(0.02, 0.5); s.lineTo(-0.2, 0.52); s.lineTo(-0.27, 0.86); s.lineTo(-0.32, 0.86); s.lineTo(-0.27, 0.48);
    s.lineTo(-0.3, 0); s.lineTo(-0.25, 0); s.lineTo(-0.2, 0.36); s.lineTo(0.17, 0.36); s.lineTo(0.26, 0);
    return s;
  }
  function bench(B, r, x, z, ry, len) {
    B.push(x, 0, z, ry || 0);
    const iron = mat('castiron', { color: 0x1e211f, metalness: 0.45, roughness: 0.55 });
    const wood = tmat('wood', ['#8a6440', '#7a5536', '#9a7048'][Math.floor(r() * 3)], 0.7);
    [-1, 1].forEach((s) => {
      B.geo(new THREE.ExtrudeGeometry(benchEnd(), { depth: 0.05, bevelEnabled: false }), iron, s * (len / 2 - 0.1) - 0.025, 0, 0, 0, PI / 2, 0);
    });
    for (let i = 0; i < 5; i++) B.rbox(wood, len, 0.035, 0.075, 0.01, 0, 0.45, 0.2 - i * 0.092, 0, 1);
    for (let i = 0; i < 3; i++) {
      const t = i / 2, yy = 0.56 + t * 0.26, zz = -0.22 - t * 0.055;
      B.geo(TXT.roundedBox(len, 0.075, 0.035, 0.01, wood, { segments: 1 }).geometry, wood, 0, yy, zz, -0.2, 0, 0);
    }
    B.box(iron, len - 0.2, 0.03, 0.03, 0, 0.3, 0.0);
    B.pop();
  }

  def('bench', {
    size: [1.8, 0.86, 0.66],
    options: { length: 1.8 },
    note: 'Park bench: cast iron ends, five seat slats and three back slats in stained hardwood',
    make(o, r) { const G = new THREE.Group(), B = Builder(); bench(B, r, 0, 0, 0, o.length); return B.flush(G); },
  });

  def('bus_stop', {
    size: [5.2, 2.8, 2.2],
    options: { length: 4.0, finish: 'auto' },
    note: 'Transit shelter: dark bronze frame, glass back and one end, sloped roof, bench, stop sign pole with a blank panel',
    make(o, r) {
      const G = new THREE.Group(), B = Builder(), L = o.length, D = 1.5, H = 2.45;
      const fr = (o.finish === 'auto' ? r() < 0.5 : o.finish === 'bronze') ? F.bronze() : mat('shelterblk', { color: 0x2a2d31, metalness: 0.5, roughness: 0.45 });
      const pane = mat('shelterglass', { color: 0x9fb2b8, metalness: 0.1, roughness: 0.04, transparent: true, opacity: 0.28, clearcoat: 1, envMapIntensity: 1.5 }, true);
      B.box(F.concrete(), L + 1.6, 0.12, D + 1.0, 0.4, 0, 0.1);
      const x0 = -L / 2, z0 = -D / 2;
      [[x0, z0], [-x0, z0], [x0, -z0 + 0.1], [-x0, -z0 + 0.1]].forEach(([px, pz]) => B.box(fr, 0.08, H + (pz < 0 ? 0.1 : 0) - 0.12, 0.08, px, 0.12, pz));
      // back wall glass in three bays, and one end panel
      for (let i = 0; i < 3; i++) {
        const bx = x0 + (L / 3) * (i + 0.5);
        B.box(pane, L / 3 - 0.06, 1.95, 0.012, bx, 0.3, z0);
        if (i) B.box(fr, 0.05, H - 0.2, 0.06, x0 + (L / 3) * i, 0.12, z0);
      }
      B.box(fr, L, 0.05, 0.06, 0, 0.27, z0); B.box(fr, L, 0.06, 0.06, 0, 2.25, z0);
      B.box(pane, 0.012, 1.95, D - 0.1, -x0, 0.3, 0.05); B.box(fr, 0.06, 0.05, D, -x0, 0.27, 0.05); B.box(fr, 0.06, 0.06, D, -x0, 2.25, 0.05);
      // roof: a thin panel sloping to the back, with a fascia band
      B.geo(new THREE.BoxGeometry(L + 0.5, 0.06, D + 0.6), mat('shelterroof', { color: 0xc5c9cc, metalness: 0.6, roughness: 0.35 }), 0, H + 0.08, 0.1, 0.06, 0, 0);
      B.geo(new THREE.BoxGeometry(L + 0.54, 0.2, 0.08), fr, 0, H + 0.02, 0.1 + (D + 0.6) / 2, 0, 0, 0);
      bench(B, r, -0.3, -0.35, 0, 1.9);
      // a litter receptacle and the stop pole with a blank route panel
      B.cyl(mat('litter', { color: 0x24272a, metalness: 0.4, roughness: 0.55 }), 0.26, 0.26, 0.9, L / 2 + 0.55, 0.12, 0.25, 24);
      B.cyl(mat('litterlid', { color: 0x1a1c1e, metalness: 0.4, roughness: 0.5 }), 0.28, 0.28, 0.06, L / 2 + 0.55, 1.02, 0.25, 24);
      const px = L / 2 + 0.6, pz = D / 2 + 0.35;
      B.cyl(F.galv(), 0.03, 0.03, 3.2, px, 0.12, pz, 12);
      const pc = ['#e35d1f', '#1c5aa6', '#12805c'][Math.floor(r() * 3)];
      B.rbox(mat('stoppanel|' + pc, { color: pc, roughness: 0.4 }), 0.46, 0.62, 0.02, 0.02, px, 2.5, pz + 0.04, 0, 1);
      B.box(mat('stoppanelw', { color: 0xf3f2ee, roughness: 0.4 }), 0.38, 0.18, 0.024, px, 2.58, pz + 0.045);
      B.rbox(mat('schedule', { color: 0x2b2e31, metalness: 0.4, roughness: 0.5 }), 0.3, 0.42, 0.06, 0.01, px, 1.35, pz + 0.05, 0, 1);
      B.box(F.glass(), 0.24, 0.34, 0.02, px, 1.39, pz + 0.08);
      return B.flush(G);
    },
  });

  def('flagpole', {
    size: [2.4, 10.4, 0.9],
    options: { height: 9.1, flags: ['texas'], flag: 0 },
    note: 'Satin aluminium flagpole, gold ball, halyard; flags as colour and geometry. flags: ["us","texas"] flies both on one pole',
    make(o, r) {
      const G = flagpoleGroup(r, { height: o.height, flags: o.flags, flag: o.flag || 0 });
      return G;
    },
  });

  /* ================================ the road ================================ */
  def('road', {
    size: [30, 0.2, 18.6],
    options: { length: 30, lanes: 2, oneWay: false, sidewalk: true, parkway: 1.2 },
    note: 'Road segment along x: asphalt lanes (3.6 m) with MUTCD markings, curb and gutter, parkway, sidewalks',
    make(o, r) {
      const G = new THREE.Group(), B = Builder();
      const L = o.length, n = Math.max(1, o.lanes | 0), lw = 3.6, rw = n * lw, top = 0.06, curbH = 0.15;
      const asph = cmat('asphm', asphaltTex('#4a4a4b'), 0.9);
      B.box(asph, L, top, rw, 0, 0, 0);
      const paint = mat('roadpaint', { color: 0xeeeeea, roughness: 0.55 }), yel = mat('roadyel', { color: 0xe8b21c, roughness: 0.55 });
      const my = top, lineT = 0.004;
      // lane lines: 10 ft dashes on 40 ft cycles for same direction, double yellow centre when two way
      const two = !o.oneWay && n >= 2, half = two ? Math.floor(n / 2) : 0;
      for (let i = 1; i < n; i++) {
        const z = -rw / 2 + i * lw;
        if (two && i === half) { B.box(yel, L, lineT, 0.1, 0, my, z - 0.1); B.box(yel, L, lineT, 0.1, 0, my, z + 0.1); continue; }
        for (let xx = -L / 2 + ((r() * 12) % 12); xx < L / 2 - 3; xx += 12.2) B.box(paint, 3.05, lineT, 0.1, xx + 1.5, my, z);
      }
      B.box(paint, L, lineT, 0.15, 0, my, -rw / 2 + 0.75); B.box(paint, L, lineT, 0.15, 0, my, rw / 2 - 0.75);
      // curb and gutter (TxDOT 6 in curb, 2 ft gutter pan in concrete), then parkway and sidewalk
      const conc = F.concrete(), sw = o.sidewalk ? 1.5 : 0, pk = o.sidewalk ? o.parkway : 0;
      [-1, 1].forEach((s) => {
        B.box(conc, L, top, 0.6, 0, 0, s * (rw / 2 + 0.3));
        B.rbox(conc, L, top + curbH, 0.16, 0.03, 0, 0, s * (rw / 2 + 0.68), 0, 1);
        if (o.sidewalk) {
          const sz = s * (rw / 2 + 0.76 + pk + sw / 2);
          for (let xx = -L / 2; xx < L / 2 - 0.01; xx += 1.5) B.box(conc, 1.49, top + curbH - 0.02, sw, xx + 0.75, 0, sz);
          if (pk > 0) B.box(mat('parkdirt', { color: 0x5b5237, roughness: 1 }), L, 0.03, pk, 0, 0, s * (rw / 2 + 0.76 + pk / 2));
        }
      });
      // a storm inlet on one side, a manhole in a lane
      B.box(mat('inlet', { color: 0x2a2826, roughness: 0.8 }), 1.5, 0.02, 0.12, L * 0.2, top + 0.02, rw / 2 + 0.7);
      B.cyl(mat('manhole', { color: 0x3c3a37, metalness: 0.6, roughness: 0.55 }), 0.32, 0.32, 0.012, -L * 0.18, top, -lw * 0.5 + (n > 1 ? 0 : 0.6), 28);
      return B.flush(G);
    },
  });

  /* ================================ building helpers ================================ */
  const pick = (r, arr) => arr[Math.floor(r() * arr.length) % arr.length];
  // four facades of a W x D block: calls fn(i, width) inside a frame whose +z is that face's normal
  function eachFace(B, W, D, fn) {
    for (let i = 0; i < 4; i++) {
      const ry = (i * PI) / 2, half = i % 2 ? W / 2 : D / 2;
      B.push(Math.sin(ry) * half, 0, Math.cos(ry) * half, ry); fn(i, i % 2 ? D : W); B.pop();
    }
  }
  // a curtain wall strip in a facade frame: glass with mullions every sp and transoms at rows
  function curtain(B, x0, x1, y0, h, sp, frame, glass, rows, z) {
    z = z || 0; const L = x1 - x0, n = Math.max(1, Math.round(L / sp)), rw = rows || 1;
    B.box(glass, L, h, 0.04, (x0 + x1) / 2, y0, z + 0.02);
    for (let i = 0; i <= n; i++) B.box(frame, 0.07, h, 0.16, x0 + (i * L) / n, y0, z + 0.08);
    for (let j = 0; j <= rw; j++) B.box(frame, L, 0.08, 0.14, (x0 + x1) / 2, y0 + (j * h) / rw - (j === rw ? 0.08 : 0), z + 0.07);
  }
  // an aluminium storefront bay with a pair of glass doors centred at dx (null for none)
  function storefront(B, x0, x1, y0, h, frame, glass, dx, z) {
    z = z || 0; const L = x1 - x0, n = Math.max(1, Math.round(L / 1.6));
    B.box(glass, L, h, 0.03, (x0 + x1) / 2, y0, z + 0.02);
    B.box(frame, L, 0.12, 0.16, (x0 + x1) / 2, y0, z + 0.08); B.box(frame, L, 0.1, 0.16, (x0 + x1) / 2, y0 + h - 0.1, z + 0.08);
    B.box(frame, L, 0.08, 0.14, (x0 + x1) / 2, y0 + 2.3, z + 0.08);
    for (let i = 0; i <= n; i++) {
      const xx = x0 + (i * L) / n;
      if (dx != null && Math.abs(xx - dx) < 0.95) continue;
      B.box(frame, 0.07, h, 0.16, xx, y0, z + 0.08);
    }
    if (dx != null) {
      [-0.9, 0, 0.9].forEach(o => B.box(frame, 0.1, 2.3, 0.18, dx + o, y0, z + 0.09));
      [-0.45, 0.45].forEach(o => { B.box(frame, 0.8, 0.1, 0.1, dx + o, y0 + 2.18, z + 0.1); B.box(frame, 0.8, 0.18, 0.1, dx + o, y0, z + 0.1);
        B.box(K.finish.chrome(), 0.03, 0.9, 0.05, dx + o - Math.sign(o) * 0.3, y0 + 0.75, z + 0.18); });
    }
  }
  // a packaged rooftop HVAC unit
  function rtu(B, x, y, z, ry) {
    B.push(x, y, z, ry || 0);
    const m = mat('rtu', { color: 0xc4c6c2, metalness: 0.45, roughness: 0.5 });
    B.box(F.galv(), 2.6, 0.18, 1.7, 0, 0, 0);
    B.rbox(m, 2.4, 1.15, 1.5, 0.03, 0, 0.18, 0, 0, 1);
    B.cyl(mat('fangrille', { color: 0x2a2c2e, metalness: 0.5, roughness: 0.6 }), 0.42, 0.42, 0.06, 0.5, 1.33, 0, 20);
    for (let i = 0; i < 6; i++) B.box(mat('louv', { color: 0x8d908e, metalness: 0.4, roughness: 0.6 }), 1.1, 0.03, 0.02, -0.5, 0.35 + i * 0.13, 0.76);
    B.pop();
  }
  // coping on a parapet top around a W x D block at height y
  function coping(B, m, W, D, y) {
    B.box(m, W + 0.1, 0.12, 0.35, 0, y, D / 2 - 0.12); B.box(m, W + 0.1, 0.12, 0.35, 0, y, -D / 2 + 0.12);
    B.box(m, 0.35, 0.12, D, W / 2 - 0.12, y, 0); B.box(m, 0.35, 0.12, D, -W / 2 + 0.12, y, 0);
  }
  // a dome of radius R and height H standing at y0: lathe, ribs, and rows of small lights
  function dome(B, m, R, H, y0, o) {
    o = o || {};
    const prof = []; const N = 28, e = o.ogee || 1;
    for (let i = 0; i <= N; i++) { const t = (i / N) * (PI / 2); prof.push([Math.max(0.001, R * Math.pow(Math.cos(t), e)), H * Math.sin(t)]); }
    B.lathe(m, prof, o.seg || 48, 0, y0, 0);
    const ribs = o.ribs || 16, rm = o.ribMat || m;
    for (let k = 0; k < ribs; k++) {
      const a = (k / ribs) * PI * 2, pts = [];
      for (let i = 0; i <= 12; i++) { const t = (i / 12) * (PI / 2) * 0.97, rr = R * Math.pow(Math.cos(t), e) + 0.04 * R; pts.push([Math.cos(a) * rr, y0 + H * Math.sin(t) + 0.02, Math.sin(a) * rr]); }
      B.tube(rm, pts, o.ribR || R * 0.022, 24, 5);
    }
    (o.lights || []).forEach(([tt, n, sz, gm]) => {
      const t = tt * PI / 2, rr = R * Math.pow(Math.cos(t), e);
      for (let k = 0; k < n; k++) {
        const a = ((k + 0.5) / n) * PI * 2;
        B.boxc(gm, sz, sz * 1.3, 0.12, Math.cos(a) * (rr + 0.02), y0 + H * Math.sin(t), Math.sin(a) * (rr + 0.02), -t * 0.9, -a + PI / 2, 0);
      }
    });
  }
  // a colonnade ring: n columns at radius rad
  function colonnade(B, m, n, rad, y0, h, cr, corinth) {
    for (let k = 0; k < n; k++) { const a = (k / n) * PI * 2; column(B, m, Math.cos(a) * rad, y0, Math.sin(a) * rad, h, cr, { corinth }); }
  }

  /* ================================ county courthouse ================================ */
  def('county_courthouse', {
    size: [50, 42, 50],
    options: { style: 'auto', storeys: 3, square: true },
    note: 'Texas county courthouse on its square: raised granite base, 2 to 3 storeys, central clock tower; style "classical" (porticos, dome) or "romanesque" (arched entries, turrets, pyramidal tower)',
    make(o, r) {
      const G = new THREE.Group(), B = Builder();
      const style = o.style === 'auto' ? (r() < 0.5 ? 'classical' : 'romanesque') : o.style, rom = style === 'romanesque';
      const n = Math.max(2, Math.min(3, o.storeys | 0)), W = 26 + Math.round(r() * 3) * 1.2;
      const hb = 1.6, hs = 4.7, Hw = hb + n * hs;
      const wallKind = rom ? pick(r, ['sandstone', 'brick', 'limestone']) : pick(r, ['limestone', 'limestone', 'buffbrick']);
      const wall = wallKind === 'brick' ? tmat('brick', '#9c4c33', 0.9) : wallKind === 'buffbrick' ? tmat('brick', '#c9a774', 0.88)
        : wallKind === 'sandstone' ? tmat('limestone', '#a5664b', 0.92) : tmat('limestone', pick(r, ['#d8c9a6', '#d2c29f', '#ddd0b3']), 0.86);
      const trim = F.castStone(rom ? (wallKind === 'limestone' ? '#b98f6e' : '#d9c7a2') : '#e2d8bf');
      const base = cmat('gran|' + rom, granite(rom ? '#8f5f52' : '#a79d92'), 0.7);
      const roofM = cmat('croof|' + style, seamTex(rom ? pick(r, ['#7c3326', '#50605a', '#6d7072']) : '#6f9b86'), 0.45, { metalness: 0.45 });
      const domeM = rom ? roofM : pick(r, [mat('patina', { color: 0x6f9f8b, metalness: 0.3, roughness: 0.5 }), mat('silverdome', { color: 0xbfc0bb, metalness: 0.7, roughness: 0.35 }), mat('gilt', { color: 0xc9a153, metalness: 0.9, roughness: 0.3 })]);
      const frame = pick(r, [F.whiteTrim(), F.whiteTrim(), F.bronze(), mat('grnframe', { color: 0x2e4034, roughness: 0.5 })]);
      const WM = { frame, glass: [F.glass(), F.glass2(), F.glass(), F.lit()], trim, sill: trim };
      const pw = Math.round(W * 0.38), pp = 1.6, pd = 3.2;

      // the block, its raised base and floor lines
      B.box(base, W + 0.6, hb, W + 0.6, 0, 0, 0);
      B.box(wall, W, Hw - hb, W, 0, hb, 0);
      B.box(trim, W + 0.8, 0.22, W + 0.8, 0, hb - 0.05, 0);
      for (let k = 1; k < n; k++) B.box(trim, W + 0.18, 0.24, W + 0.18, 0, hb + k * hs - 0.12, 0);
      if (!rom) B.box(F.roofDeck(), W - 0.4, 0.4, W - 0.4, 0, Hw, 0);

      eachFace(B, W, W, (fi, Fw) => {
        const sp = (Fw / 2 - pw / 2) / 3, ww = Math.min(1.35, sp * 0.52);
        // pavilion and its base
        B.box(wall, pw, Hw - hb, pp, 0, hb, pp / 2);
        B.box(base, pw + 0.6, hb, pp + 0.3, 0, 0, (pp + 0.3) / 2);
        B.box(trim, pw + 0.8, 0.22, pp + 0.4, 0, hb - 0.05, (pp + 0.4) / 2);
        for (let k = 1; k < n; k++) B.box(trim, pw + 0.18, 0.24, pp + 0.09, 0, hb + k * hs - 0.12, pp / 2);
        // side bays
        for (let k = 0; k < n; k++) {
          const y0 = hb + k * hs + 1.0, wh = hs - 2.0, top = k === n - 1;
          for (let j = 0; j < 3; j++) [-1, 1].forEach((s) => {
            const x = s * (pw / 2 + sp * (j + 0.5));
            if (top) archWin(B, WM, r, x, y0, ww, wh + 0.35, { tw: 0.18 });
            else rectWin(B, WM, r, x, y0, ww, wh, { keystone: k === 0 || rom, cap: !rom && k > 0, headH: rom ? 0.42 : 0.3, rows: 2, cols: 2 });
          });
        }
        // corner quoins, or giant pilasters
        if (rom || r() < 0.3) {
          for (let y = hb + 0.2, q = 0; y < Hw - 0.6; y += 0.62, q++) [-1, 1].forEach((s) => {
            const w = q % 2 ? 0.55 : 0.9; B.box(trim, w, 0.5, 0.08, s * (Fw / 2 - w / 2), y, 0.04);
            B.box(trim, w * 0.9, 0.5, 0.08, s * (pw / 2 - w * 0.45), y, pp + 0.04);
          });
        } else {
          for (let j = 0; j <= 3; j++) [-1, 1].forEach((s) => {
            const x = s * (pw / 2 + sp * j + (j === 0 ? 0.45 : j === 3 ? -0.35 : 0));
            B.box(trim, 0.6, Hw - hb - hs - 0.6, 0.16, x, hb + hs + 0.05, 0.08);
            B.box(trim, 0.8, 0.34, 0.28, x, Hw - 0.9, 0.14);
          });
        }
        // entablature and cornice with dentils, on the face and around the pavilion
        B.box(trim, Fw + 0.3, 0.6, 0.2, 0, Hw - 0.6, 0.1);
        B.box(trim, Fw + 1.0, 0.4, 0.62, 0, Hw, 0.31);
        dentils(B, trim, -Fw / 2, -pw / 2, Hw - 0.17, 0.27); dentils(B, trim, pw / 2, Fw / 2, Hw - 0.17, 0.27);
        B.box(trim, pw + 0.3, 0.6, pp + 0.2, 0, Hw - 0.6, pp / 2 + 0.1);
        B.box(trim, pw + 1.0, 0.4, pp + 0.62, 0, Hw, (pp + 0.62) / 2);
        if (!rom) {
          balustrade(B, trim, -Fw / 2 - 0.3, -pw / 2 - 0.4, Hw + 0.4, 0.15, 1.0);
          balustrade(B, trim, pw / 2 + 0.4, Fw / 2 + 0.3, Hw + 0.4, 0.15, 1.0);
          // the portico: giant Corinthian columns, entablature, pediment, a stair to the raised floor
          B.box(base, pw + 0.8, hb, pd + 0.3, 0, 0, pp + (pd + 0.3) / 2);
          B.box(trim, pw + 1.0, 0.2, pd + 0.4, 0, hb - 0.05, pp + (pd + 0.4) / 2);
          const ch = Hw - 1.2 - hb, zc = pp + pd - 0.75;
          for (let i = 0; i < 4; i++) {
            const x = -pw / 2 + 0.95 + (i * (pw - 1.9)) / 3;
            column(B, trim, x, hb, zc, ch, 0.46, { corinth: true });
            B.box(trim, 0.75, ch, 0.14, x, hb, pp + 0.07);
          }
          B.box(trim, pw + 0.5, 1.2, pd + 0.2, 0, Hw - 1.2, pp + (pd + 0.2) / 2 - 0.05);
          B.box(trim, pw + 1.1, 0.4, pd + 0.7, 0, Hw, pp + (pd + 0.7) / 2 - 0.1);
          dentils(B, trim, -pw / 2 - 0.2, pw / 2 + 0.2, Hw - 0.17, pp + pd + 0.2);
          pediment(B, wall, trim, pw + 1.1, 2.7, Hw + 0.4, 0, pp + pd + 0.25);
          gableRoof(B, cmat('leadroof', seamTex('#7d7f7c'), 0.5, { metalness: 0.4 }), pw + 1.3, pp + pd + 0.5, 2.75, 0, Hw + 0.42, -0.1);
          // a round window in the tympanum
          B.geo(new THREE.TorusGeometry(0.55, 0.13, 8, 28), trim, 0, Hw + 1.45, pp + pd + 0.02);
          B.geo(new THREE.CircleGeometry(0.55, 28), F.glass(), 0, Hw + 1.45, pp + pd - 0.02);
          B.push(0, 0, pp, 0);
          doors(B, 0, hb, 1.9, 3.0, { frame: trim });
          archWin(B, { frame, glass: [F.glass()], trim, sill: null }, r, 0, hb + 3.15, 1.9, 1.2, { tw: 0.2, mullion: true });
          for (let k = 1; k < n; k++) [-1, 0, 1].forEach(xx => {
            const y0 = hb + k * hs + 1.0;
            if (k === n - 1) archWin(B, WM, r, xx * pw / 3.3, y0, ww, hs - 1.65, { tw: 0.16 });
            else rectWin(B, WM, r, xx * pw / 3.3, y0, ww, hs - 2.0, { cap: true, rows: 2, cols: 2 });
          });
          [-1, 1].forEach(xx => rectWin(B, WM, r, xx * pw / 3.3, hb + 1.0, ww, hs - 2.0, { keystone: true, rows: 2, cols: 2 }));
          B.pop();
          stairs(B, trim, pw - 1.4, hb, pp + pd + 0.15, { cheek: 0.6, cheekMat: base, rail: F.black() });
        } else {
          // Romanesque: a gabled pavilion over a deep round-arched entry porch
          B.extrude(wall, triShape(pw, 4.6), pp, 0, Hw + 0.4, 0);
          const ang = Math.atan2(4.6, pw / 2), sl = Math.hypot(pw / 2, 4.6) + 0.3;
          [-1, 1].forEach(s => B.boxc(trim, sl, 0.35, 0.55, s * pw / 4, Hw + 0.4 + 2.3 + 0.1, pp + 0.02, 0, 0, -s * ang));
          B.cyl(trim, 0.08, 0.3, 1.2, 0, Hw + 5.0, pp - 0.2, 10);
          gableRoof(B, roofM, pw + 0.5, W * 0.35 + pp + 0.35, 4.75, 0, Hw + 0.4, -W * 0.35);
          // triple arched window in the gable
          B.push(0, 0, pp, 0); [-1, 0, 1].forEach(k => archWin(B, WM, r, k * 1.05, Hw + 0.9, 0.8, k ? 1.7 : 2.3, { tw: 0.1, mullion: false, meet: false, keystone: false })); B.pop();
          B.push(0, 0, pp, 0);
          const aw = 3.4, ahr = 2.7, ph = 5.4, pwid = pw * 0.66;
          B.box(base, pwid + 0.4, hb, 2.9, 0, 0, 1.45);
          B.extrude(wall, archWall(pwid, ph, aw, ahr), 2.6, 0, hb, 0);
          B.extrude(trim, archU(aw, ahr, 0.55), 0.14, 0, hb, 2.6);
          B.box(trim, pwid + 0.3, 0.35, 2.9, 0, hb + ph, 1.3);
          B.extrude(wall, triShape(pwid, 1.8), 2.6, 0, hb + ph + 0.35, 0);
          [-1, 1].forEach(s => B.boxc(trim, Math.hypot(pwid / 2, 1.8) + 0.2, 0.28, 2.9, s * pwid / 4, hb + ph + 0.35 + 0.95, 1.3, 0, 0, -s * Math.atan2(1.8, pwid / 2)));
          gableRoof(B, roofM, pwid + 0.5, 2.9, 1.95, 0, hb + ph + 0.36, -0.1);
          [-1, 1].forEach(s => { B.cyl(trim, 0.26, 0.26, ahr, s * (aw / 2 + 0.3), hb, 2.75, 16); B.box(trim, 0.7, 0.35, 0.7, s * (aw / 2 + 0.3), hb + ahr, 2.75); });
          doors(B, 0, hb, 2.0, 3.1, { frame: trim });
          archWin(B, { frame, glass: [F.glass()], trim: null, sill: null }, r, 0, hb + 3.2, 2.0, 1.0 + 0.2, { tw: 0 });
          for (let k = 1; k < n; k++) [-1, 1].forEach(xx => {
            const y0 = hb + k * hs + 1.0;
            if (k === n - 1) archWin(B, WM, r, xx * pw / 3.4, y0, ww, hs - 1.65, { tw: 0.18 });
            else rectWin(B, WM, r, xx * pw / 3.4, y0, ww, hs - 2.0, { keystone: true, headH: 0.42, rows: 2, cols: 2 });
          });
          [-1, 1].forEach(xx => rectWin(B, WM, r, xx * (pwid / 2 + 0.9), hb + 1.0, 0.7, hs - 2.2, { keystone: true, rows: 2 }));
          B.pop();
          stairs(B, trim, pwid - 0.4, hb, pp + 2.9, { cheek: 0.5, cheekMat: base, rail: F.black() });
        }
      });

      if (rom) {
        hipRoof(B, roofM, W + 0.9, W + 0.9, 6.0, 0, Hw + 0.4, 0);
        // corner turrets with conical roofs
        [[1, 1], [1, -1], [-1, 1], [-1, -1]].forEach(([sx, sz]) => {
          const cx = sx * W / 2, cz = sz * W / 2, tr = 1.7, th = Hw + 2.6;
          B.cyl(base, tr + 0.3, tr + 0.3, hb, cx, 0, cz, 32);
          B.cyl(wall, tr, tr, th - hb, cx, hb, cz, 32);
          for (let k = 1; k < n; k++) B.cyl(trim, tr + 0.1, tr + 0.1, 0.24, cx, hb + k * hs - 0.12, cz, 32);
          B.cyl(trim, tr + 0.35, tr + 0.2, 0.45, cx, th, cz, 32);
          B.cyl(roofM, 0.02, tr + 0.4, 5.6, cx, th + 0.45, cz, 32);
          B.cyl(F.black(), 0.03, 0.06, 1.3, cx, th + 5.9, cz, 8);
          const a = Math.atan2(sx, sz);
          B.push(cx, 0, cz, a);
          for (let k = 0; k < n; k++) archWin(B, WM, r, 0, hb + k * hs + 1.2, 0.7, hs - 2.1, { tw: 0.12, td: 0.14, mullion: false });
          archWin(B, WM, r, 0, Hw + 0.6, 0.55, 1.4, { tw: 0.1, mullion: false, meet: false });
          B.pop();
        });
        // the tower: a tall shaft, clocks, an open belfry, corner pinnacles and a steep pyramid
        const ts = 7.2, t0 = Hw + 0.4, t1 = t0 + 11, t2 = t1 + 4.2;
        B.box(wall, ts, t2 - t0, ts, 0, t0, 0);
        B.box(trim, ts + 0.3, 0.3, ts + 0.3, 0, t0 + 5.2, 0);
        B.box(trim, ts + 0.5, 0.4, ts + 0.5, 0, t1, 0);
        B.box(trim, ts + 0.8, 0.5, ts + 0.8, 0, t2, 0);
        eachFace(B, ts, ts, () => {
          clock(B, r, 0, t0 + 8.2, 1.55, trim);
          [-1, 1].forEach(s => { B.geo(new THREE.ShapeGeometry(archShape(1.3, 2.3), 12), mat('belfry', { color: 0x0e0c0b, roughness: 1 }), s * 1.25, t1 + 0.5, 0.02);
            B.extrude(trim, archU(1.3, 2.3, 0.22), 0.16, s * 1.25, t1 + 0.5, 0);
            for (let k = 0; k < 5; k++) B.boxc(F.door(), 1.25, 0.06, 0.3, s * 1.25, t1 + 0.8 + k * 0.42, 0.05, 0.6, 0, 0); });
          archWin(B, WM, r, 0, t0 + 1.6, 0.9, 2.6, { tw: 0.18, mullion: false });
        });
        [[1, 1], [1, -1], [-1, 1], [-1, -1]].forEach(([sx, sz]) => {
          const cx = sx * (ts / 2), cz = sz * (ts / 2);
          B.cyl(wall, 0.65, 0.65, 4.8, cx, t1 - 0.6, cz, 20);
          B.cyl(trim, 0.8, 0.75, 0.3, cx, t2 + 0.2, cz, 20);
          B.cyl(roofM, 0.02, 0.8, 3.2, cx, t2 + 0.5, cz, 20);
        });
        hipRoof(B, roofM, ts + 0.9, ts + 0.9, 9.5, 0, t2 + 0.5, 0);
        B.cyl(F.gold(), 0.02, 0.08, 2.2, 0, t2 + 9.9, 0, 8);
        B.geo(new THREE.SphereGeometry(0.22, 16, 10), F.gold(), 0, t2 + 10.2, 0);
      } else {
        // classical tower: a square clock stage, a colonnaded round drum, a ribbed dome, a lantern
        const ts = 7.6, t0 = Hw + 0.4, t1 = t0 + 6.6;
        B.box(wall, ts, t1 - t0, ts, 0, t0, 0);
        B.box(trim, ts + 0.3, 0.5, ts + 0.3, 0, t1 - 0.5, 0);
        B.box(trim, ts + 0.9, 0.35, ts + 0.9, 0, t1, 0);
        eachFace(B, ts, ts, () => {
          clock(B, r, 0, t0 + 3.6, 1.55, trim);
          [-1, 1].forEach(s => { B.box(trim, 0.55, t1 - t0 - 0.6, 0.14, s * (ts / 2 - 0.4), t0, 0.07); B.geo(new THREE.SphereGeometry(0.35, 14, 10), trim, s * (ts / 2 - 0.1), t1 + 0.7, 0.2); B.cyl(trim, 0.3, 0.3, 0.35, s * (ts / 2 - 0.1), t1 + 0.35, 0.2, 12); });
          balustrade(B, trim, -ts / 2 + 0.6, ts / 2 - 0.6, t1 + 0.35, 0.2, 0.9);
        });
        const d0 = t1 + 0.6, dh = 4.2;
        B.cyl(trim, 3.55, 3.6, 0.5, 0, d0 - 0.25, 0, 40);
        B.cyl(wall, 2.55, 2.55, dh, 0, d0, 0, 40);
        for (let k = 0; k < 8; k++) { const a = ((k + 0.5) / 8) * PI * 2; B.push(Math.cos(a) * 2.55, 0, Math.sin(a) * 2.55, PI / 2 - a); B.geo(new THREE.ShapeGeometry(archShape(0.9, 2.2), 10), F.glass2(), 0, d0 + 0.6, 0.02); B.pop(); }
        colonnade(B, trim, 12, 3.05, d0, dh, 0.19, true);
        B.cyl(trim, 3.45, 3.45, 0.7, 0, d0 + dh, 0, 40);
        B.cyl(trim, 3.2, 3.5, 0.3, 0, d0 + dh + 0.7, 0, 40);
        dome(B, domeM, 3.05, 3.4, d0 + dh + 1.0, { ribs: 12, ribMat: trim, ogee: 1.15 });
        const l0 = d0 + dh + 4.2;
        B.cyl(trim, 0.75, 0.75, 1.9, 0, l0, 0, 20);
        colonnade(B, trim, 6, 0.95, l0, 1.9, 0.09, false);
        B.cyl(trim, 1.15, 1.15, 0.25, 0, l0 + 1.9, 0, 20);
        dome(B, domeM, 1.0, 0.9, l0 + 2.15, { ribs: 6, ribMat: trim, ribR: 0.03 });
        B.geo(new THREE.SphereGeometry(0.3, 16, 12), F.gold(), 0, l0 + 3.35, 0);
        B.cyl(F.gold(), 0.02, 0.07, 1.6, 0, l0 + 3.5, 0, 8);
      }

      if (o.square) {
        // the courthouse square: a ring walk, a walk to every door, a flag on the lawn
        const conc = F.concrete(), R = W / 2 + 11.5;
        [-1, 1].forEach(s => { B.box(conc, 2 * R + 2.4, 0.07, 2.4, 0, 0, s * R); B.box(conc, 2.4, 0.07, 2 * R - 2.4, s * R, 0, 0); });
        eachFace(B, W, W, () => { const z0 = rom ? pp + 2.9 + 1.6 : pp + pd + 0.15 + 3.2; B.box(conc, 3.4, 0.07, R - W / 2 - z0, 0, 0, z0 + (R - W / 2 - z0) / 2); });
        B.flush(G);
        const fp = flagpoleGroup(r, { height: 12.2, flags: ['us', 'texas'] });
        fp.position.set(W / 2 + 6.5, 0, W / 2 + 7.5); G.add(fp);
        // a granite monument and two benches on the lawn
        const B2 = Builder();
        B2.rbox(base, 2.2, 1.2, 0.6, 0.05, -W / 2 - 6, 0, W / 2 + 7, 0.3, 2);
        bench(B2, r, -7, R - 2.0, 0, 1.8); bench(B2, r, 7, R - 2.0, 0, 1.8);
        B2.flush(G);
        return G;
      }
      return B.flush(G);
    },
  });

  /* ================================ the Texas State Capitol ================================ */
  // an arcade wall: ww wide, hh tall, with n round-arched openings w wide springing at hr
  function arcadeShape(ww, hh, n, w, hr) {
    const s = new THREE.Shape(), sp = ww / n;
    s.moveTo(-ww / 2, 0);
    for (let i = 0; i < n; i++) {
      const cx = -ww / 2 + sp * (i + 0.5);
      s.lineTo(cx - w / 2, 0); s.lineTo(cx - w / 2, hr); s.absarc(cx, hr, w / 2, PI, 0, true); s.lineTo(cx + w / 2, 0);
    }
    s.lineTo(ww / 2, 0); s.lineTo(ww / 2, hh); s.lineTo(-ww / 2, hh); s.lineTo(-ww / 2, 0);
    return s;
  }
  /* One run of the Capitol's elevation in a facade frame, x0 to x1: a rusticated ground storey
   * of round arched windows, two principal floors under pedimented caps between giant Corinthian
   * pilasters, an attic storey, the main cornice and a parapet. Heights from the real building:
   * the walls stand about 24 m to the top of the parapet. */
  function capitolRun(B, C, r, x0, x1, o) {
    o = o || {};
    const L = x1 - x0, mid = (x0 + x1) / 2, nb = Math.max(1, Math.round(L / 4.4)), sp = L / nb;
    for (let y = 0.9, k = 0; y < 5.9; y += 0.72, k++) B.box(C.rust, L, 0.63, 0.1, mid, y, 0.05);
    B.box(C.trim, L + 0.1, 0.9, 0.3, mid, 0, 0.15);
    for (let j = 0; j < nb; j++) {
      const x = x0 + sp * (j + 0.5);
      archWin(B, C.W, r, x, 1.8, 1.55, 3.4, { tw: 0.24, td: 0.3 });
      rectWin(B, C.W, r, x, 7.6, 1.6, 3.5, { cap: true, headH: 0.4, rows: 2, cols: 2, td: 0.24 });
      rectWin(B, C.W, r, x, 14.1, 1.55, 3.1, { cap: true, rows: 2, cols: 2, td: 0.22 });
      rectWin(B, C.W, r, x, 20.3, 1.25, 1.55, { tw: 0.12, rows: 1, cols: 2, noBlind: true });
    }
    for (let j = 0; j <= nb; j++) {
      const x = x0 + sp * j;
      B.box(C.trim, 0.72, 12.5, 0.22, x, 6.7, 0.11);
      B.box(C.trim, 0.98, 0.55, 0.36, x, 18.8, 0.18);
      B.box(C.trim, 0.6, 3.1, 0.14, x, 19.95, 0.07);
    }
    B.box(C.trim, L, 0.5, 0.38, mid, 6.1, 0.19);
    B.box(C.trim, L, 0.62, 0.3, mid, 19.35, 0.15);
    B.box(C.trim, L + 0.4, 0.55, 0.95, mid, 23.2, 0.47);
    dentils(B, C.trim, x0, x1, 23.04, 0.32);
    if (!o.noParapet) {
      B.box(C.wall, L, 1.45, 0.55, mid, 23.75, 0.0);
      B.box(C.trim, L + 0.2, 0.18, 0.7, mid, 25.2, 0.0);
    }
  }
  function goddess(B, m, y0) {
    // the Goddess of Liberty: robed, a sword lowered in her left hand, the Lone Star raised in her right
    B.lathe(m, [[0, 0], [0.62, 0], [0.66, 0.12], [0.52, 0.5], [0.45, 1.5], [0.36, 2.3], [0.3, 2.62], [0.36, 2.85], [0.33, 3.05], [0.14, 3.22], [0, 3.25]], 20, 0, y0, 0);
    B.geo(new THREE.SphereGeometry(0.2, 16, 12), m, 0, y0 + 3.45, 0);
    B.geo(new THREE.SphereGeometry(0.24, 14, 8, 0, PI * 2, 0, PI / 2), m, 0, y0 + 3.5, -0.02);
    B.bar(m, [-0.3, y0 + 2.95, 0], [-0.5, y0 + 2.05, 0.15], 0.08, 8);
    B.bar(m, [-0.52, y0 + 2.5, 0.2], [-0.56, y0 + 1.1, 0.24], 0.035, 6);
    B.bar(m, [0.3, y0 + 2.95, 0], [0.45, y0 + 3.7, 0.02], 0.08, 8);
    B.bar(m, [0.45, y0 + 3.7, 0.02], [0.5, y0 + 4.35, 0.04], 0.07, 8);
    const st = new THREE.Shape();
    for (let i = 0; i <= 10; i++) { const a = PI / 2 + (i * PI) / 5, rr = i % 2 ? 0.13 : 0.34; if (i === 0) st.moveTo(Math.cos(a) * rr, Math.sin(a) * rr); else st.lineTo(Math.cos(a) * rr, Math.sin(a) * rr); }
    B.extrude(F.gold(), st, 0.06, 0.52, y0 + 4.62, 0.0);
  }

  def('capitol', {
    size: [174, 92.2, 96],
    options: {},
    note: 'The Texas State Capitol, Austin: Sunset Red granite, 172 m long, the dome to the Goddess at 92 m. Origin at the rotunda; the south front faces +z',
    make(o, r) {
      const G = new THREE.Group(), B = Builder();
      const wall = cmat('capwall', granite('#c08a76'), 0.72), trim = cmat('captrim', granite('#caa08c'), 0.66);
      const rust = cmat('caprust', granite('#b48270'), 0.8);
      const W = { frame: mat('capframe', { color: 0x3a2e26, roughness: 0.5 }), glass: [F.glass(), F.glass2(), F.blind(), F.glass()], trim, sill: trim };
      const C = { wall, trim, rust, W };
      const roofM = cmat('caproof', seamTex('#76706a'), 0.5, { metalness: 0.4 });
      // the dome and drum are cast iron painted to match the granite
      const dm = mat('capdome', { color: 0xcfa894, roughness: 0.55, metalness: 0.05 }), dt = mat('capdomet', { color: 0xdcbba8, roughness: 0.5 });
      const DW = { frame: mat('capframe', { color: 0x3a2e26, roughness: 0.5 }), glass: [F.glass2(), F.glass()], trim: dt, sill: dt };

      // masses: the long east-west range, the central north-south range, the end pavilions
      B.box(wall, 136, 23.75, 30, 0, 0, 0);
      B.box(wall, 50, 23.75, 80, 0, 0, 0);
      [-1, 1].forEach(sx => B.box(wall, 18, 23.75, 48, sx * 77, 0, 0));
      B.box(mat('capapron', { color: 0x9c948a, roughness: 0.9 }), 176, 0.12, 52, 0, 0, 0);
      B.box(mat('capapron', { color: 0x9c948a, roughness: 0.9 }), 54, 0.12, 84, 0, 0, 0);
      [-1, 1].forEach((sz) => {
        const ry = sz > 0 ? 0 : PI;
        B.push(0, 0, sz * 40, ry); capitolRun(B, C, r, -25, -13.6); capitolRun(B, C, r, 13.6, 25); B.pop();
        B.push(0, 0, sz * 15, ry); capitolRun(B, C, r, -68, -25); capitolRun(B, C, r, 25, 68); B.pop();
        [-1, 1].forEach((sx) => {
          B.push(sx * 77, 0, sz * 24, ry); capitolRun(B, C, r, -9, 9, { noParapet: true });
          pediment(B, wall, trim, 18.8, 3.9, 23.75, -0.6, 1.1);
          gableRoof(B, roofM, 19.0, 1.9, 3.95, 0, 23.77, -0.7);
          B.pop();
          B.push(sx * 25, 0, sz * 27.5, sx * PI / 2); capitolRun(B, C, r, -12.5, 12.5); B.pop();
          B.push(sx * 68, 0, sz * 19.5, -sx * PI / 2); capitolRun(B, C, r, -4.5, 4.5); B.pop();
        });
      });
      [-1, 1].forEach(sx => { B.push(sx * 86, 0, 0, sx * PI / 2); capitolRun(B, C, r, -24, 24);
        pediment(B, wall, trim, 16, 3.3, 25.35, -0.6, 0.9); B.pop(); });
      // roofs behind the parapets
      hipRoof(B, roofM, 136, 29, 4.2, 0, 25.3, 0);
      hipRoof(B, roofM, 49, 79, 6.5, 0, 25.3, 0);
      [-1, 1].forEach(sx => hipRoof(B, roofM, 17.4, 47, 4.6, sx * 77, 23.8, 0));

      // the south portico: an arcade, a two storey Corinthian order, entablature and pediment
      B.push(0, 0, 40, 0);
      B.box(rust, 28, 1.3, 7.2, 0, 0, 3.6);
      B.extrude(rust, arcadeShape(27, 4.9, 3, 3.2, 2.6), 6.4, 0, 1.3, 0);
      B.extrude(trim, archU(3.2, 2.6, 0.4), 0.12, -9, 1.3, 6.4); B.extrude(trim, archU(3.2, 2.6, 0.4), 0.12, 0, 1.3, 6.4); B.extrude(trim, archU(3.2, 2.6, 0.4), 0.12, 9, 1.3, 6.4);
      doors(B, 0, 1.3, 2.4, 3.6, { frame: trim });
      [-9, 9].forEach(x => doors(B, x, 1.3, 2.0, 3.2, { frame: trim }));
      B.box(trim, 28.2, 0.55, 7.3, 0, 6.2, 3.55);
      const cxs = [-12.4, -10.6, -4.4, -2.6, 2.6, 4.4, 10.6, 12.4];
      cxs.forEach(x => column(B, trim, x, 6.75, 5.7, 14.8, 0.62, { corinth: true }));
      cxs.forEach(x => B.box(trim, 1.0, 14.8, 0.25, x, 6.75, 0.12));
      balustrade(B, trim, -13.8, -1.6, 6.75, 6.7, 1.05); balustrade(B, trim, 1.6, 13.8, 6.75, 6.7, 1.05);
      B.box(trim, 28.4, 1.7, 7.2, 0, 21.55, 3.6);
      B.box(trim, 29.2, 0.55, 7.8, 0, 23.25, 3.7);
      dentils(B, trim, -14.4, 14.4, 23.08, 7.4);
      pediment(B, wall, trim, 29.2, 5.6, 23.8, -0.5, 7.6);
      gableRoof(B, roofM, 29.4, 8.4, 5.65, 0, 23.82, -0.7);
      // the Lone Star in the tympanum
      const st = new THREE.Shape();
      for (let i = 0; i <= 10; i++) { const a = PI / 2 + (i * PI) / 5, rr = i % 2 ? 0.62 : 1.6; if (i === 0) st.moveTo(Math.cos(a) * rr, Math.sin(a) * rr); else st.lineTo(Math.cos(a) * rr, Math.sin(a) * rr); }
      B.extrude(trim, st, 0.18, 0, 25.9, 7.12);
      stairs(B, trim, 20, 1.3, 7.2, { cheek: 1.2, cheekMat: rust });
      B.pop();
      // a plainer north front: pediment over the central range
      B.push(0, 0, -40, PI); pediment(B, wall, trim, 24, 4.4, 23.75, -0.6, 1.2); gableRoof(B, roofM, 24.2, 2.0, 4.45, 0, 23.77, -0.7);
      doors(B, 0, 0.9, 2.4, 3.6, { frame: trim }); stairs(B, trim, 10, 0.9, 0.1, { cheek: 0.8, cheekMat: rust }); B.pop();

      // the rotunda: an octagonal base, two drums, the attic, the dome, the lantern, the Goddess
      B.geo(new THREE.CylinderGeometry(19.5, 19.5, 5.4, 8), wall, 0, 23.8 + 2.7, 0, 0, PI / 8, 0);
      B.geo(new THREE.CylinderGeometry(20.1, 20.1, 0.5, 8), trim, 0, 29.4, 0, 0, PI / 8, 0);
      const t1 = 29.65;
      B.cyl(dm, 16.8, 16.8, 10.2, 0, t1, 0, 72);
      for (let k = 0; k < 24; k++) {
        const a = (k / 24) * PI * 2, a2 = ((k + 0.5) / 24) * PI * 2;
        B.push(Math.cos(a) * 16.8, 0, Math.sin(a) * 16.8, PI / 2 - a); archWin(B, DW, r, 0, t1 + 2.0, 1.5, 5.0, { tw: 0.2 }); B.pop();
        B.push(Math.cos(a2) * 16.8, 0, Math.sin(a2) * 16.8, PI / 2 - a2); B.box(dt, 0.8, 9.4, 0.3, 0, t1 + 0.4, 0.1); B.box(dt, 1.0, 0.5, 0.45, 0, t1 + 9.6, 0.15); B.pop();
      }
      B.cyl(dt, 17.4, 17.4, 1.2, 0, t1 + 10.2, 0, 72); B.cyl(dt, 17.9, 17.6, 0.45, 0, t1 + 11.4, 0, 72);
      const t2 = t1 + 11.85;
      B.cyl(dm, 14.6, 14.6, 8.2, 0, t2, 0, 72);
      B.cyl(dt, 16.6, 16.6, 0.4, 0, t2, 0, 72);
      colonnade(B, dt, 24, 15.9, t2 + 0.4, 7.8, 0.42, true);
      for (let k = 0; k < 24; k++) { const a = ((k + 0.5) / 24) * PI * 2; B.push(Math.cos(a) * 14.6, 0, Math.sin(a) * 14.6, PI / 2 - a); archWin(B, DW, r, 0, t2 + 1.6, 1.3, 4.6, { tw: 0.16 }); B.pop(); }
      B.cyl(dt, 16.7, 16.7, 1.3, 0, t2 + 8.2, 0, 72); B.cyl(dt, 17.1, 16.8, 0.45, 0, t2 + 9.5, 0, 72);
      const ta = t2 + 9.95;
      B.cyl(dm, 15.2, 15.2, 2.3, 0, ta, 0, 72);
      for (let k = 0; k < 24; k++) { const a = ((k + 0.5) / 24) * PI * 2; B.push(Math.cos(a) * 15.2, 0, Math.sin(a) * 15.2, PI / 2 - a);
        B.geo(new THREE.CircleGeometry(0.45, 18), F.glass2(), 0, ta + 1.15, 0.03); B.geo(new THREE.TorusGeometry(0.5, 0.09, 6, 18), dt, 0, ta + 1.15, 0.05); B.pop(); }
      B.cyl(dt, 15.6, 15.4, 0.4, 0, ta + 2.3, 0, 72);
      const d0 = ta + 2.7;
      dome(B, dm, 15.0, 20.5, d0, { ribs: 24, ribMat: dt, ogee: 1.3, seg: 72, ribR: 0.22, lights: [[0.22, 24, 0.95, F.glass2()], [0.5, 24, 0.75, F.glass2()], [0.74, 12, 0.6, F.glass2()]] });
      const l0 = d0 + 20.3;
      B.cyl(dt, 3.9, 3.9, 0.9, 0, l0, 0, 40);
      B.cyl(dm, 2.8, 2.8, 5.0, 0, l0 + 0.9, 0, 40);
      for (let k = 0; k < 8; k++) { const a = ((k + 0.5) / 8) * PI * 2; B.push(Math.cos(a) * 2.8, 0, Math.sin(a) * 2.8, PI / 2 - a); B.geo(new THREE.ShapeGeometry(archShape(1.0, 2.9), 10), F.glass2(), 0, l0 + 1.5, 0.03); B.pop(); }
      colonnade(B, dt, 16, 3.45, l0 + 0.9, 5.0, 0.2, true);
      B.cyl(dt, 3.9, 3.9, 0.7, 0, l0 + 5.9, 0, 40);
      dome(B, dm, 3.3, 2.5, l0 + 6.6, { ribs: 8, ribMat: dt, ribR: 0.07 });
      B.lathe(dt, [[0, 0], [1.2, 0], [1.1, 0.4], [0.75, 1.4], [0.62, 3.4], [0.9, 3.65], [0.9, 3.9], [0, 3.9]], 24, 0, l0 + 8.9, 0);
      goddess(B, mat('goddess', { color: 0xd6cdbd, roughness: 0.45, metalness: 0.25 }), l0 + 12.8);
      B.flush(G);
      return G;
    },
  });
}
