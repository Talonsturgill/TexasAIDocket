/* kit/landscape.js, see assets/js/txkit.js for the conventions.
 *
 * THE PLACE AROUND A SUBJECT. Judges kept writing "dead ground", "a void lot", "a flat brown
 * plane" and "a hard seam where the ground meets the sky". These models are the middle ground
 * and the far distance that make a frame read as Texas: Hill Country terrain, a mesa on the
 * horizon, a ranch road, a highway, a creek, a lake shore, a city skyline in haze, crop rows,
 * a pasture that is dense rather than tufted, and a grain elevator on the Panhandle horizon.
 *
 * GROUND CONTRACT. Everything here is built to sit ON TXT.ground (a plane at y = 0). A shape
 * that fades out at its rim dips a few centimetres BELOW y = 0 there, so it emerges from the
 * ground plane along a clean line instead of z-fighting with it over a band. Nothing is ever
 * cut below grade: the ground plane would cover it. A creek bed is therefore built between
 * raised banks, and a lake's water plane stands a little above y = 0.
 *
 * FAR THINGS. city_skyline and mesa are meant to sit kilometres away. The engine's camera far
 * plane is 1000 m and its FogExp2 swallows anything past about 1.5 km, so those two models
 * carry their own aerial perspective (option `aerial`) instead of the scene fog, and a frame
 * that places them far must raise R.camera.far (and call updateProjectionMatrix) past them.
 */
export function install(K, THREE, TXT) {
  /* ---- materials, cached here by KEY ALONE. K.mat keys by JSON.stringify(params), and a params
   * object holding a texture serialises that texture's whole canvas to a PNG data URL on every call,
   * which cost tens of milliseconds a call. Every key below is unique to its parameters. */
  const MC = new Map();
  function M(key, P, phys) {
    if (!MC.has(key)) { const Q = Object.assign({ roughness: 0.8, metalness: 0 }, P); MC.set(key, phys ? new THREE.MeshPhysicalMaterial(Q) : new THREE.MeshStandardMaterial(Q)); }
    return MC.get(key);
  }
  // cast concrete, pale and new enough to read as concrete under a warm sun, mapped in metres
  const concM = () => M('conc-pale', { color: 0xffffff, map: K.tex('concrete', { color: '#cfcac0' }), roughness: 0.9 });
  // K.box, then texture coordinates in metres whenever the material carries a map
  function box(w, h, d, mat, x, y0, z, r, parent) {
    const m = K.box(w, h, d, mat, x, y0, z, r, parent);
    if (mat && mat.map) K.uvBox(m.geometry, mat.map.userData.metres || 3);
    return m;
  }

  /* ---- local helpers ------------------------------------------------------------------- */
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
  const TAU = Math.PI * 2;

  // 2D value noise from a seed, non periodic, smooth; returns n(x, y) in 0..1
  function noise2(seed) {
    const R = TXT.rng(seed), P = new Uint8Array(512), V = new Float32Array(256);
    for (let i = 0; i < 256; i++) { P[i] = i; V[i] = R(); }
    for (let i = 255; i > 0; i--) { const j = Math.floor(R() * (i + 1)); const t = P[i]; P[i] = P[j]; P[j] = t; }
    for (let i = 0; i < 256; i++) P[i + 256] = P[i];
    const h = (x, y) => V[P[P[x & 255] + (y & 255)]];
    return function (x, y) {
      const xi = Math.floor(x), yi = Math.floor(y), fx = x - xi, fy = y - yi;
      const sx = fx * fx * (3 - 2 * fx), sy = fy * fy * (3 - 2 * fy);
      const a = h(xi, yi), b = h(xi + 1, yi), c = h(xi, yi + 1), d = h(xi + 1, yi + 1);
      return a + (b - a) * sx + (c - a) * sy + (a - b - c + d) * sx * sy;
    };
  }
  function fbm(n, x, y, oct, gain) {
    let s = 0, a = 0.5, f = 1, t = 0; gain = gain || 0.5;
    for (let i = 0; i < oct; i++) { s += a * n(x * f + i * 17.3, y * f - i * 9.1); t += a; f *= 2.03; a *= gain; }
    return s / t;
  }
  const col = (hex) => new THREE.Color(hex);   // sRGB hex -> linear working colour
  function mix3(out, a, b, t) { out.r = lerp(a.r, b.r, t); out.g = lerp(a.g, b.g, t); out.b = lerp(a.b, b.b, t); return out; }

  // canvas textures local to this family, cached per kit
  const TEXC = new Map();
  function canvasTex(key, N, paint, o) {
    if (TEXC.has(key)) return TEXC.get(key);
    const c = document.createElement('canvas'); c.width = c.height = N;
    paint(c.getContext('2d'), N, TXT.rng(key.length * 7919 + 13));
    const t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.colorSpace = (o && o.data) ? THREE.NoColorSpace : THREE.SRGBColorSpace;
    t.anisotropy = 8;
    TEXC.set(key, t);
    return t;
  }
  // per pixel painter over a tileable value lattice (period = N / cell)
  function pixelPaint(x, N, fn) {
    const im = x.createImageData(N, N), d = im.data;
    for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
      const p = (j * N + i) * 4, c = fn(i, j);
      d[p] = clamp(c[0], 0, 255); d[p + 1] = clamp(c[1], 0, 255); d[p + 2] = clamp(c[2], 0, 255); d[p + 3] = c[3] == null ? 255 : c[3];
    }
    x.putImageData(im, 0, 0);
  }
  function tileNoise(seed, period) {             // periodic value noise over [0, period)
    const R = TXT.rng(seed), L = new Float32Array(period * period);
    for (let i = 0; i < L.length; i++) L[i] = R();
    return function (x, y) {
      const xi = Math.floor(x), yi = Math.floor(y), fx = x - xi, fy = y - yi;
      const sx = fx * fx * (3 - 2 * fx), sy = fy * fy * (3 - 2 * fy);
      const x0 = ((xi % period) + period) % period, y0 = ((yi % period) + period) % period;
      const x1 = (x0 + 1) % period, y1 = (y0 + 1) % period;
      const a = L[y0 * period + x0], b = L[y0 * period + x1], c = L[y1 * period + x0], d = L[y1 * period + x1];
      return a + (b - a) * sx + (c - a) * sy + (a - b - c + d) * sx * sy;
    };
  }
  function tileNoise2(seed, px, py) {            // periodic, px across and py down
    const R = TXT.rng(seed), L = new Float32Array(px * py);
    for (let i = 0; i < L.length; i++) L[i] = R();
    return function (x, y) {
      const xi = Math.floor(x), yi = Math.floor(y), fx = x - xi, fy = y - yi;
      const sx = fx * fx * (3 - 2 * fx), sy = fy * fy * (3 - 2 * fy);
      const x0 = ((xi % px) + px) % px, y0 = ((yi % py) + py) % py, x1 = (x0 + 1) % px, y1 = (y0 + 1) % py;
      const a = L[y0 * px + x0], b = L[y0 * px + x1], c = L[y1 * px + x0], d = L[y1 * px + x1];
      return a + (b - a) * sx + (c - a) * sy + (a - b - c + d) * sx * sy;
    };
  }
  // A grey detail map (mean about 0.9) that multiplies vertex colour: tooth without a hue.
  function detailTex(kind) {
    return canvasTex('detail-' + kind, 256, (x, N, r) => {
      const n1 = tileNoise(11 + kind.length, 16), n2 = tileNoise(29, 64), n3 = tileNoise(5, 128);
      pixelPaint(x, N, (i, j) => {
        const u = i / N, v = j / N;
        let k = 0.9 + (n1(u * 16, v * 16) - 0.5) * 0.18 + (n2(u * 64, v * 64) - 0.5) * 0.16 + (n3(u * 128, v * 128) - 0.5) * 0.14;
        if (kind === 'grass') k += (n2(u * 64, v * 8) - 0.5) * 0.1;
        if (r() < 0.012) k *= 0.7;
        const g = 235 * k;
        return [g, g * 0.99, g * 0.96];
      });
    });
  }
  // A tangent space normal map of small waves: tileable, from a periodic height field.
  function waveNormalTex() {
    return canvasTex('waves', 256, (x, N) => {
      const n1 = tileNoise(71, 8), n2 = tileNoise(73, 24), n3 = tileNoise(79, 64);
      const H = (i, j) => { const u = i / N, v = j / N;
        return n1(u * 8, v * 8 * 0.6) * 0.5 + n2(u * 24, v * 24) * 0.35 + n3(u * 64, v * 64) * 0.15; };
      pixelPaint(x, N, (i, j) => {
        const dx = (H(i + 1, j) - H(i - 1, j)) * 3.2, dy = (H(i, j + 1) - H(i, j - 1)) * 3.2;
        const l = Math.hypot(dx, dy, 1);
        return [(-dx / l * 0.5 + 0.5) * 255, (-dy / l * 0.5 + 0.5) * 255, (1 / l * 0.5 + 0.5) * 255];
      });
    }, { data: true });
  }

  // Instancing with a full scale vector, a rotation about y (and optional tilt), and a colour.
  function instanced(geo, mat, list, colors) {
    const im = new THREE.InstancedMesh(geo, mat, Math.max(1, list.length));
    const M = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), s = new THREE.Vector3(), p = new THREE.Vector3();
    list.forEach((it, i) => {
      e.set(it.rx || 0, it.ry || 0, it.rz || 0, 'YXZ'); q.setFromEuler(e);
      s.set(it.sx || it.s || 1, it.sy || it.s || 1, it.sz || it.s || 1);
      p.set(it.x, it.y, it.z); M.compose(p, q, s); im.setMatrixAt(i, M);
      if (colors) im.setColorAt(i, colors[i]);
    });
    im.count = list.length;
    im.instanceMatrix.needsUpdate = true;
    if (im.instanceColor) im.instanceColor.needsUpdate = true;
    im.castShadow = true; im.receiveShadow = true;
    return im;
  }
  // Merge geometries (already transformed) into one; keeps position, normal, uv and color if all have them.
  function mergeGeos(list) {
    const parts = list.map((g) => (g.index ? g.toNonIndexed() : g));
    const has = (n) => parts.every((g) => g.attributes[n]);
    const keys = ['position', 'normal'].concat(has('uv') ? ['uv'] : [], has('color') ? ['color'] : []);
    const out = new THREE.BufferGeometry();
    keys.forEach((k) => {
      const size = parts[0].attributes[k].itemSize;
      let total = 0; parts.forEach((g) => { total += g.attributes[k].count; });
      const arr = new Float32Array(total * size); let o = 0;
      parts.forEach((g) => { const a = g.attributes[k]; for (let i = 0; i < a.count; i++) for (let c = 0; c < size; c++) arr[o++] = a.array[i * a.itemSize + c]; });
      out.setAttribute(k, new THREE.BufferAttribute(arr, size));
    });
    return out;
  }
  function paintGeo(g, c) {                       // a flat vertex colour over a geometry
    const n = g.attributes.position.count, a = new Float32Array(n * 3), C = col(c);
    for (let i = 0; i < n; i++) { a[i * 3] = C.r; a[i * 3 + 1] = C.g; a[i * 3 + 2] = C.b; }
    g.setAttribute('color', new THREE.BufferAttribute(a, 3));
    return g;
  }
  // An irregular smooth lump (a tree crown, a boulder): icosahedron displaced by noise.
  function lump(seed, detail, sx, sy, sz, rough) {
    let g = new THREE.IcosahedronGeometry(1, detail);
    const p = g.attributes.position, n = noise2(seed), v = new THREE.Vector3();
    for (let i = 0; i < p.count; i++) {
      v.set(p.getX(i), p.getY(i), p.getZ(i));
      const k = 1 + (n(v.x * 1.7 + 5, v.z * 1.7 + v.y * 1.3 + 5) - 0.5) * rough;
      p.setXYZ(i, v.x * k * sx, v.y * k * sy, v.z * k * sz);
    }
    return smoothNormals(g);
  }
  // a crown: a lump with a second, finer octave so the silhouette breaks up like foliage
  function roughLump(seed, sx, sy, sz, rough) {
    const g = new THREE.IcosahedronGeometry(1, 1), p = g.attributes.position, n = noise2(seed), v = new THREE.Vector3();
    for (let i = 0; i < p.count; i++) {
      v.set(p.getX(i), p.getY(i), p.getZ(i));
      const k = 1 + (n(v.x * 1.5 + 5, v.z * 1.5 + v.y * 1.3 + 5) - 0.5) * rough + (n(v.x * 5 + 30, v.y * 5 + v.z * 3) - 0.5) * rough * 0.6;
      p.setXYZ(i, v.x * k * sx, v.y * k * sy, v.z * k * sz);
    }
    return smoothNormals(g);
  }
  function smoothNormals(g) {                     // average normals over coincident corners
    const p = g.attributes.position, n = p.count, acc = new Map(), key = new Array(n);
    const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3();
    for (let i = 0; i < n; i++) key[i] = Math.round(p.getX(i) * 1e3) + ',' + Math.round(p.getY(i) * 1e3) + ',' + Math.round(p.getZ(i) * 1e3);
    for (let t = 0; t < n; t += 3) {
      a.fromBufferAttribute(p, t); b.fromBufferAttribute(p, t + 1); c.fromBufferAttribute(p, t + 2);
      const f = new THREE.Vector3().subVectors(c, b).cross(a.clone().sub(b));
      for (let j = 0; j < 3; j++) { const k = key[t + j], v = acc.get(k); if (v) v.add(f); else acc.set(k, f.clone()); }
    }
    const nor = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) { const v = acc.get(key[i]).clone().normalize(); nor[i * 3] = v.x; nor[i * 3 + 1] = v.y; nor[i * 3 + 2] = v.z; }
    g.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
    return g;
  }
  // A heightfield patch w x d (centred), segments sx x sz, height fn(x, z) -> y. Smooth normals.
  function heightfield(w, d, sx, sz, fn) {
    const g = new THREE.PlaneGeometry(w, d, sx, sz);
    g.rotateX(-Math.PI / 2);
    const p = g.attributes.position;
    for (let i = 0; i < p.count; i++) p.setY(i, fn(p.getX(i), p.getZ(i)));
    g.computeVertexNormals();
    return g;
  }
  // Aerial perspective for FAR models: their own exponential haze toward the scene fog colour,
  // with a rate set per model, capped so a silhouette always survives. Replaces the scene fog
  // on that material only (a FogExp2 tuned for a 200 m set would erase a skyline at 5 km).
  function aerial(mat, rate, cap) {
    mat.fog = true;
    const prev = mat.onBeforeCompile;
    mat.onBeforeCompile = (sh, r) => {
      if (prev) prev(sh, r);
      sh.uniforms.uAerial = { value: rate }; sh.uniforms.uAerialCap = { value: cap };
      sh.fragmentShader = sh.fragmentShader
        .replace('#include <fog_pars_fragment>', '#include <fog_pars_fragment>\nuniform float uAerial, uAerialCap;')
        .replace('#include <fog_fragment>', `#ifdef USE_FOG
          float aF = min(uAerialCap, 1.0 - exp(-uAerial * vFogDepth));
          gl_FragColor.rgb = mix(gl_FragColor.rgb, fogColor, aF);
        #endif`);
    };
    mat.customProgramCacheKey = () => 'aerial' + rate + '|' + cap;
    mat.needsUpdate = true;
    return mat;
  }
  // Physical water: reflective, fresnel, small waves from a normal map, optional vertex alpha.
  function waterMat(key, tint, opts) {
    opts = opts || {};
    const nm = waveNormalTex();
    const m = M('water-' + key, { color: tint, roughness: opts.rough != null ? opts.rough : 0.06, metalness: 0,
      ior: 1.333, specularIntensity: 1, clearcoat: 0.6, clearcoatRoughness: 0.08, envMapIntensity: 1.35,
      normalMap: nm, normalScale: new THREE.Vector2(opts.wave || 0.35, opts.wave || 0.35),
      transparent: !!opts.alpha, vertexColors: !!opts.alpha, depthWrite: !opts.alpha }, true);
    return m;
  }


  /* ---- foliage cards: the leafy silhouette a lump can't give -------------------------------
   * A crown is a dozen alpha tested cards scattered through an ellipsoid, each lit by a normal that
   * points out from the crown's centre, so the mass shades like a volume while its edge breaks up
   * into leaves. A dark core behind them stops the sky showing through. */
  function leafTex(kind) {
    return canvasTex('leaves-' + kind, 256, (x, N, r) => {
      x.clearRect(0, 0, N, N);
      const pal = kind === 'juniper' ? [[38, 52, 40], [48, 64, 46], [60, 78, 54], [72, 90, 62]]
        : kind === 'mesquite' ? [[70, 88, 52], [88, 104, 60], [104, 118, 70], [60, 76, 46]]
        : [[46, 60, 34], [60, 76, 40], [76, 92, 50], [92, 106, 60]];
      const n = kind === 'juniper' ? 1400 : 900;
      for (let i = 0; i < n; i++) {
        const a = r() * TAU, d = Math.sqrt(r()) * N * 0.47 * (0.75 + 0.25 * Math.sin(a * 5 + 1.3)), px = N / 2 + Math.cos(a) * d, py = N / 2 + Math.sin(a) * d;
        const c = pal[Math.min(3, Math.floor(r() * 3 + (1 - py / N) * 1.4))], k = 0.8 + r() * 0.35;
        x.fillStyle = 'rgb(' + Math.round(c[0] * k) + ',' + Math.round(c[1] * k) + ',' + Math.round(c[2] * k) + ')';
        x.beginPath();
        if (kind === 'juniper') x.ellipse(px, py, 2 + r() * 3, 1.5 + r() * 2.5, r() * 3, 0, TAU);
        else x.ellipse(px, py, 3 + r() * 4, 1.6 + r() * 2, r() * 3, 0, TAU);
        x.fill();
      }
      // a few twigs
      x.strokeStyle = 'rgba(40,32,24,0.7)'; x.lineWidth = 1.5;
      for (let i = 0; i < 6; i++) { x.beginPath(); x.moveTo(N / 2, N / 2); x.lineTo(N / 2 + (r() - 0.5) * N * 0.7, N / 2 + (r() - 0.5) * N * 0.7); x.stroke(); }
    });
  }
  function leafMat(kind) {
    const m = M('leafcard-' + kind, { color: 0xffffff, map: leafTex(kind), alphaTest: 0.5, roughness: 0.88, vertexColors: true, side: THREE.DoubleSide });
    if (!m.userData.fol) {
      m.userData.fol = true;
      const chunk = THREE.ShaderChunk.normal_fragment_begin.replace('normal *= faceDirection;', '');
      m.onBeforeCompile = (sh) => { sh.fragmentShader = sh.fragmentShader.replace('#include <normal_fragment_begin>', chunk); };
      m.customProgramCacheKey = () => 'foliage-noflip';
    }
    return m;
  }
  // crown geometry: `cards` quads in an ellipsoid of radii rx, ry, rz centred at cy, plus a core
  function crownGeo(rng, o) {
    const P = [], Nn = [], U = [], C = [], v = new THREE.Vector3(), q = new THREE.Quaternion(), e = new THREE.Euler();
    const corners = [[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]];
    const pushV = (x, y, z, u, w) => {
      P.push(x, y, z); U.push(u, w);
      const nx = x / o.rx, ny = (y - o.cy) / o.ry + 0.35, nz = z / o.rz; v.set(nx, ny, nz).normalize(); Nn.push(v.x, v.y, v.z);
      const k = lerp(o.ao || 0.5, 1.08, smooth(o.cy - o.ry, o.cy + o.ry, y)); C.push(k, k, k);
    };
    for (let i = 0; i < o.cards; i++) {
      let cx, cy, cz; do { cx = rng() * 2 - 1; cy = rng() * 2 - 1; cz = rng() * 2 - 1; } while (cx * cx + cy * cy + cz * cz > 1);
      cx *= o.rx * 0.62; cy = o.cy + cy * o.ry * 0.62; cz *= o.rz * 0.62;
      const sz = (o.rx + o.ry + o.rz) / 3 * (0.95 + rng() * 0.5);
      e.set(rng() * TAU, rng() * TAU, rng() * TAU); q.setFromEuler(e);
      corners.forEach((c) => { v.set(c[0] * sz, c[1] * sz, 0).applyQuaternion(q); pushV(cx + v.x, cy + v.y, cz + v.z, c[0] + 0.5, c[1] + 0.5); });
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(Nn, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(U, 2)); g.setAttribute('color', new THREE.Float32BufferAttribute(C, 3));
    return g;
  }
  // a dark core so a crown never shows sky through its middle; with a trunk when asked
  function coreGeo(seed, o) {
    const parts = [];
    const c = lump(seed, 0, o.rx * 0.62, o.ry * 0.55, o.rz * 0.62, 0.5); c.translate(0, o.cy, 0); parts.push(c);
    if (o.trunk) { const t = new THREE.CylinderGeometry(o.trunk * 0.7, o.trunk, o.cy, 6, 1, true).toNonIndexed(); t.translate(0, o.cy / 2, 0); parts.push(t); }
    const g = mergeGeos(parts), p = g.attributes.position, C = new Float32Array(p.count * 3);
    for (let i = 0; i < p.count; i++) { const k = p.getY(i) < o.cy - o.ry * 0.5 ? 0.55 : 0.8; C[i * 3] = k; C[i * 3 + 1] = k; C[i * 3 + 2] = k; }
    g.setAttribute('color', new THREE.BufferAttribute(C, 3));
    return g;
  }
  // natural limestone: pale, pitted, with dark lichen and fine bedding; 2 m a tile
  function limeTex() {
    return canvasTex('lime-natural', 512, (x, N, r) => {
      const n1 = tileNoise(701, 8), n2 = tileNoise(703, 32), n3 = tileNoise(709, 128), nb = tileNoise2(711, 4, 24);
      pixelPaint(x, N, (i, j) => { const u = i / N, v = j / N;
        let k = 0.9 + (n1(u * 8, v * 8) - 0.5) * 0.2 + (n2(u * 32, v * 32) - 0.5) * 0.12 + (n3(u * 128, v * 128) - 0.5) * 0.12;
        k -= (nb(u * 4, v * 24) - 0.5) * 0.12;                                      // bedding
        let rr = 226 * k, gg = 218 * k, bb = 196 * k;
        const li = n2(u * 32 + 7, v * 32 + 3); if (li > 0.7) { const t = (li - 0.7) * 2.5; rr -= 70 * t; gg -= 66 * t; bb -= 60 * t; }   // lichen
        return [rr, gg, bb]; });
      for (let i = 0; i < 900; i++) { x.fillStyle = 'rgba(70,60,48,' + (0.2 + r() * 0.35) + ')'; x.beginPath(); x.arc(r() * N, r() * N, 0.8 + r() * 2.6, 0, TAU); x.fill(); }   // solution pits
    });
  }

  /* ======================================================================================
   * hill_country_terrain
   * ====================================================================================== */
  const SEASON = {
    summer: { flat: [0x9c9463, 0x898a5a, 0xb2a676], slope: 0x6f7247, brake: 0x3c4a2d, rock: 0xd2c6a6, rim: 0x857d4c },
    spring: { flat: [0x7a8a48, 0x6c7d40, 0x8e9656], slope: 0x5d6b3a, brake: 0x34452a, rock: 0xd0c4a4, rim: 0x7c7d48 },
    winter: { flat: [0xa89a74, 0x98906c, 0xb4a782], slope: 0x7e765a, brake: 0x3f4a31, rock: 0xcfc3a5, rim: 0x8d8060 },
  };
  function hillHeight(o, seed) {
    const S = o.size, relief = o.relief, nA = noise2(seed), nB = noise2(seed + 1), nC = noise2(seed + 2);
    const lam = S * 0.32, step = o.step || Math.max(3, relief / 5.5);
    return function (x, z) {
      const u = x / lam, v = z / lam;
      let h = fbm(nA, u, v, 5, 0.48);                                  // rolling hills, 0..1
      h = Math.pow(clamp((h - 0.28) / 0.55, 0, 1), 1.25);
      const ridge = 1 - Math.abs(fbm(nB, u * 1.6, v * 1.6, 4) * 2 - 1); // drainage: valleys along noise zero lines
      h *= 0.55 + 0.45 * smooth(0.25, 0.8, ridge);
      let y = h * relief;
      // the Hill Country stair step: Glen Rose limestone erodes into flat treads and short risers
      const k = Math.floor(y / step), f = y / step - k;
      const t = (k + smooth(0.58, 0.96, f)) * step;
      y = lerp(y, t, o.ledges ? 0.72 : 0.0);
      y += (fbm(nC, x / 9, z / 9, 3) - 0.5) * 0.9;                     // small tooth
      // the rim: a noisy rounded square that falls to just under y = 0
      const rr = Math.pow(Math.pow(Math.abs(x) / (S / 2), 4) + Math.pow(Math.abs(z) / (S / 2), 4), 0.25);
      const edge = 1 - rr + (nC(x / (S * 0.08) + 40, z / (S * 0.08) + 40) - 0.5) * 0.12;
      const m = smooth(0.0, 0.3, edge);
      return { y: m * (y + 0.6) - (1 - m) * 0.4, m, step };
    };
  }
  K.define('hill_country_terrain', {
    size: [800, 60, 800],
    options: { size: 800, relief: 60, ledges: true, trees: 1, season: 'summer', segments: 0 },
    note: 'Central Texas Hill Country: rolling stair-stepped limestone hills, exposed ledges, juniper brakes and live oak mottes, grass by slope. size 200 to 2000 m, relief in metres. Rim dips 0.4 m under y=0 so it rises out of TXT.ground. Middle ground and far distance.',
    make(o, r) {
      o = Object.assign({ size: 800, relief: 60, ledges: true, trees: 1, season: 'summer', segments: 0 }, o);
      o.size = clamp(o.size, 200, 2000);
      const S = o.size, g = new THREE.Group(), seed = 1000 + o.seed * 31;
      const Hf = hillHeight(o, seed);
      const seg = o.segments || Math.round(clamp(S / 3.6, 160, 220));
      const MK = [];
      const geo = heightfield(S, S, seg, seg, (x, z) => { const h = Hf(x, z); MK.push(h.m); return h.y; });
      // colour by slope, by height, by the brake noise
      const P = geo.attributes.position, N = geo.attributes.normal, C = new Float32Array(P.count * 3);
      const pal = SEASON[o.season] || SEASON.summer, flats = pal.flat.map(col), cS = col(pal.slope), cB = col(pal.brake),
        cR = col(pal.rock), cRim = col(pal.rim), nP = noise2(seed + 7), nQ = noise2(seed + 8), tmp = new THREE.Color(), t2 = new THREE.Color();
      for (let i = 0; i < P.count; i++) {
        const x = P.getX(i), z = P.getZ(i), y = P.getY(i), ny = N.getY(i), slope = 1 - ny;
        const pn = fbm(nP, x / 60, z / 60, 3);
        mix3(tmp, flats[0], flats[1], smooth(0.3, 0.7, pn));
        mix3(tmp, tmp, flats[2], smooth(0.55, 0.8, fbm(nQ, x / 25, z / 25, 2)) * 0.6);
        mix3(tmp, tmp, cS, smooth(0.03, 0.12, slope));
        const brake = smooth(0.52, 0.66, fbm(nQ, x / 45 + 30, z / 45, 3)) * smooth(0.02, 0.08, slope);
        mix3(tmp, tmp, cB, brake * 0.85);
        mix3(tmp, tmp, cR, smooth(0.2, 0.42, slope) * 0.9);            // exposed limestone on risers
        // a touch lighter on crests, darker in hollows
        const kk = 0.92 + 0.16 * smooth(0, o.relief, y);
        tmp.multiplyScalar(kk);
        mix3(tmp, cRim, tmp, smooth(0.1, 0.8, MK[i]));
        C[i * 3] = tmp.r; C[i * 3 + 1] = tmp.g; C[i * 3 + 2] = tmp.b;
      }
      geo.setAttribute('color', new THREE.BufferAttribute(C, 3));
      const uv = geo.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * S / 7, uv.getY(i) * S / 7);
      const tm = M('hct-ground', { color: 0xffffff, roughness: 0.97, vertexColors: true, map: detailTex('grass'), envMapIntensity: 0.5 });
      const ground = new THREE.Mesh(geo, tm); ground.receiveShadow = true; g.add(ground);

      // sample helpers
      const hAt = (x, z) => Hf(x, z);
      const slopeAt = (x, z) => { const e = 2, a = hAt(x + e, z).y - hAt(x - e, z).y, b = hAt(x, z + e).y - hAt(x, z - e).y;
        return { s: Math.hypot(a, b) / (2 * e), gx: a, gz: b }; };

      // limestone ledges: slabs laid along the contour on the risers, half buried
      if (o.ledges) {
        const slabGeo = (() => {
          const b = new THREE.BoxGeometry(1, 1, 1, 6, 2, 3), p = b.attributes.position, n = noise2(seed + 55);
          for (let i = 0; i < p.count; i++) {
            const x = p.getX(i), y = p.getY(i), z = p.getZ(i);
            const k = 1 + (n(x * 4 + 3, z * 4 + y * 2) - 0.5) * 0.35;
            p.setXYZ(i, x * (1 + (n(y * 3, z * 5) - 0.5) * 0.25), y * k, z * k);
          }
          const g2 = b.toNonIndexed(); g2.computeVertexNormals(); K.uvBox(g2, 1);
          const u2 = g2.attributes.uv; for (let i = 0; i < u2.count; i++) u2.setXY(i, u2.getX(i) * 0.5, u2.getY(i) * 0.5);
          return g2;
        })();
        const lm = M('hct-ledge', { color: 0xffffff, roughness: 0.9, map: limeTex() });
        const list = [], cols = [], want = Math.round(170 * (S / 800) * (S / 800) * (o.relief / 60));
        let tries = 0;
        while (list.length < Math.min(want, 900) && tries < want * 60) {
          tries++;
          const x = (r() - 0.5) * S * 0.92, z = (r() - 0.5) * S * 0.92, H = hAt(x, z);
          if (H.m < 0.6) continue;
          const sl = slopeAt(x, z);
          if (sl.s < 0.28) continue;
          const len = 4 + r() * 9, ht = 1.0 + r() * 1.6, dp = 2 + r() * 2.5;
          list.push({ x, y: H.y - ht * 0.2, z, ry: Math.atan2(sl.gx, sl.gz) + Math.PI / 2 + (r() - 0.5) * 0.3,
            sx: len, sy: ht, sz: dp });
          cols.push(new THREE.Color().setScalar(0.85 + r() * 0.25));
        }
        if (list.length) g.add(instanced(slabGeo, lm, list, cols));
      }

      // trees: Ashe juniper singly and in brakes on slopes, live oak mottes on the flats
      if (o.trees > 0) {
        // shapes for a tree ONE unit tall; the instance scale is its height in metres
        const J = { rx: 0.34, ry: 0.5, rz: 0.34, cy: 0.52, cards: 12, ao: 0.45 }, O = { rx: 0.62, ry: 0.3, rz: 0.62, cy: 0.66, cards: 22, ao: 0.4 };
        const B = { rx: 0.6, ry: 0.42, rz: 0.6, cy: 0.42, cards: 5, ao: 0.55 };
        const jCard = crownGeo(r, J), oCard = crownGeo(r, O), bCard = crownGeo(r, B);
        const jCore = coreGeo(seed + 3, Object.assign({ trunk: 0.03 }, J)), oCore = coreGeo(seed + 4, Object.assign({ trunk: 0.045 }, O));
        const coreM = M('hct-core', { color: 0x2a3322, roughness: 0.95, vertexColors: true });
        const jl = [], jc = [], ol = [], oc = [], bl = [], bc = [];
        const area = S * S, nJ = Math.round(Math.min(2600, area / 220) * o.trees), nO = Math.round(Math.min(360, area / 1700) * o.trees), nB = Math.round(Math.min(5000, area / 110) * o.trees);
        const tint = (k) => new THREE.Color(0.86 + r() * 0.2, 0.86 + r() * 0.2, 0.84 + r() * 0.16).multiplyScalar(k);
        const nBr = noise2(seed + 8);
        let tries = 0;
        while (jl.length < nJ && tries < nJ * 30) {
          tries++;
          const x = (r() - 0.5) * S, z = (r() - 0.5) * S, H = hAt(x, z);
          if (H.m < 0.12) continue;
          const sl = slopeAt(x, z).s;
          if (sl > 0.45) continue;
          const brake = smooth(0.46, 0.66, fbm(nBr, x / 45 + 30, z / 45, 3));
          const p = 0.06 + brake * 0.9 + smooth(0.05, 0.25, sl) * 0.3;
          if (r() > p) continue;
          const h = 3.5 + r() * 3.5;
          jl.push({ x, y: H.y - 0.15, z, ry: r() * TAU, sx: h * (0.8 + r() * 0.5), sy: h, sz: h * (0.8 + r() * 0.5) });
          jc.push(tint(0.9 + r() * 0.2));
        }
        tries = 0;
        while (ol.length < nO && tries < nO * 40) {
          tries++;
          const x = (r() - 0.5) * S, z = (r() - 0.5) * S, H = hAt(x, z);
          if (H.m < 0.12 || slopeAt(x, z).s > 0.14) continue;
          const h = 7 + r() * 5;
          // a motte: two to four oaks grown together
          const n = 2 + Math.floor(r() * 3);
          for (let k = 0; k < n && ol.length < nO * 3; k++) {
            const xx = x + (r() - 0.5) * h * 1.2, zz = z + (r() - 0.5) * h * 1.2, hh = h * (0.75 + r() * 0.35);
            ol.push({ x: xx, y: hAt(xx, zz).y - 0.15, z: zz, ry: r() * TAU, sx: hh * (0.9 + r() * 0.3), sy: hh, sz: hh * (0.9 + r() * 0.3) });
            oc.push(tint(0.95 + r() * 0.2));
          }
        }
        tries = 0;
        while (bl.length < nB && tries < nB * 6) {           // understory: agarita, young cedar, mesquite
          tries++;
          const x = (r() - 0.5) * S, z = (r() - 0.5) * S, H = hAt(x, z);
          if (H.m < 0.2 || slopeAt(x, z).s > 0.5) continue;
          const h = 0.9 + r() * 1.6;
          bl.push({ x, y: H.y - 0.1, z, ry: r() * TAU, sx: h * (0.9 + r() * 0.6), sy: h, sz: h * (0.9 + r() * 0.6) });
          bc.push(tint(0.8 + r() * 0.3));
        }
        const add2 = (card, core, mat, list, cols) => { if (!list.length) return;
          g.add(instanced(card, mat, list, cols)); if (core) g.add(instanced(core, coreM, list, cols)); };
        add2(jCard, jCore, leafMat('juniper'), jl, jc);
        add2(oCard, oCore, leafMat('oak'), ol, oc);
        add2(bCard, null, leafMat('mesquite'), bl, bc);
      }
      g.userData.heightAt = (x, z) => Hf(x, z).y;   // callers can seat things on it
      return g;
    },
  });

  /* ---- shared: foliage that lights from above on both faces, blade tufts ---------------- */
  // A blade is a thin double sided card. Three flips a back face's normal, so a blade seen from
  // behind goes black. Foliage takes its light from its up-tilted normal on either face instead.
  function foliageMat(key, params) {
    const m = M('fol-' + key, Object.assign({ color: 0xffffff, roughness: 0.9, vertexColors: true, side: THREE.DoubleSide }, params || {}));
    if (!m.userData.fol) {
      m.userData.fol = true;
      const chunk = THREE.ShaderChunk.normal_fragment_begin.replace('normal *= faceDirection;', '');
      m.onBeforeCompile = (sh) => { sh.fragmentShader = sh.fragmentShader.replace('#include <normal_fragment_begin>', chunk); };
      m.customProgramCacheKey = () => 'foliage-noflip';
    }
    return m;
  }
  /* A tuft of curved, tapering blades, each three segments (five triangles). Normals lean up so a
   * field reads as a lit mass, not as a thousand facets. colors: [root, mid, tip] hex. */
  function tuftGeo(rng, o) {
    const blades = o.blades || 14, H = o.height || 0.6, spread = o.spread || 0.12, w0 = o.width || 0.012;
    const cR = col(o.colors[0]), cM = col(o.colors[1]), cT = col(o.colors[2]);
    const P = [], C = [], Nn = [];
    const up = new THREE.Vector3(0, 1, 0);
    for (let b = 0; b < blades; b++) {
      const a = rng() * TAU, lean = (o.lean || 0.35) * (0.4 + rng() * 0.9), h = H * (0.45 + rng() * 0.6), w = w0 * (0.7 + rng() * 0.6);
      const bx = Math.cos(a) * spread * Math.sqrt(rng()), bz = Math.sin(a) * spread * Math.sqrt(rng());
      const dx = Math.cos(a), dz = Math.sin(a), px = -dz, pz = dx;
      const pt = (t) => [bx + dx * lean * h * t * t, h * t * (1 - 0.18 * lean * t), bz + dz * lean * h * t * t];
      const ts = [0, 0.38, 0.72, 1], L = [], Rr = [];
      ts.forEach((t) => { const p = pt(t), ww = w * (1 - t * 0.85); L.push([p[0] - px * ww, p[1], p[2] - pz * ww]); Rr.push([p[0] + px * ww, p[1], p[2] + pz * ww]); });
      const tip = pt(1.0);
      const colAt = (t) => { const c = new THREE.Color(); if (t < 0.5) mix3(c, cR, cM, t * 2); else mix3(c, cM, cT, (t - 0.5) * 2);
        const k = 0.85 + rng() * 0.3; return [c.r * k, c.g * k, c.b * k]; };
      const tint = 0.85 + rng() * 0.3;
      const push = (v, t) => { P.push(v[0], v[1], v[2]); const c = colAt(t); C.push(c[0] * tint, c[1] * tint, c[2] * tint);
        const n = new THREE.Vector3(dx * 0.5 * (1 - t), 1, dz * 0.5 * (1 - t)).normalize(); Nn.push(n.x, n.y, n.z); };
      for (let s = 0; s < 2; s++) {
        push(L[s], ts[s]); push(Rr[s], ts[s]); push(L[s + 1], ts[s + 1]);
        push(Rr[s], ts[s]); push(Rr[s + 1], ts[s + 1]); push(L[s + 1], ts[s + 1]);
      }
      push(L[2], ts[2]); push(Rr[2], ts[2]); push(tip, 1);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3));
    g.setAttribute('normal', new THREE.Float32BufferAttribute(Nn, 3));
    g.setAttribute('color', new THREE.Float32BufferAttribute(C, 3));
    return g;
  }
  // A few tuft variants, instanced over a list of spots, with per instance tint.
  function tuftField(rng, spots, o, parent) {
    const variants = o.variants || 3, groups = [];
    for (let v = 0; v < variants; v++) groups.push({ geo: tuftGeo(rng, o), list: [], cols: [] });
    const mat = foliageMat(o.key || 'grass');
    spots.forEach((s) => {
      const G = groups[Math.floor(rng() * variants)];
      G.list.push({ x: s[0], y: s[1], z: s[2], ry: rng() * TAU, s: s[3] || 1, sy: (s[3] || 1) * (0.8 + rng() * 0.4) });
      G.cols.push(new THREE.Color().setScalar(0.85 + rng() * 0.3));
    });
    groups.forEach((G) => { if (G.list.length) { const im = instanced(G.geo, mat, G.list, G.cols); im.castShadow = false; parent.add(im); } });
  }
  // gravel and cobble: smooth small lumps, instanced
  function stones(rng, spots, key, colors, parent, angular) {
    let geo;
    if (angular) { geo = new THREE.IcosahedronGeometry(1, 0); const p = geo.attributes.position, n = noise2(Math.floor(rng() * 1e5));
      for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i), z = p.getZ(i), k = 0.7 + n(x * 2 + 4, y * 2 + z * 2 + 4) * 0.6; p.setXYZ(i, x * k, y * k * 0.6, z * k * 0.85); }
      geo.computeVertexNormals(); }
    else geo = lump(Math.floor(rng() * 1e5), 1, 1, 0.55, 0.8, 0.5);
    const m = M('stone-' + key, { color: 0xffffff, roughness: 0.85 });
    const list = [], cs = [];
    spots.forEach((s) => { const k = s[3] || 0.1; list.push({ x: s[0], y: s[1] + k * 0.12, z: s[2], ry: rng() * TAU, rx: (rng() - 0.5) * 0.4, sx: k * (0.8 + rng() * 0.5), sy: k, sz: k * (0.7 + rng() * 0.5) });
      cs.push(col(colors[Math.floor(rng() * colors.length)]).multiplyScalar(0.85 + rng() * 0.3)); });
    if (list.length) parent.add(instanced(geo, m, list, cs));
  }
  // A surface detail texture for gravel roads, painted speckle over a light base; multiplies colour.
  function gravelTex() {
    return canvasTex('gravel', 512, (x, N, r) => {
      const n1 = tileNoise(301, 32), n2 = tileNoise(307, 128);
      pixelPaint(x, N, (i, j) => { const u = i / N, v = j / N;
        const k = 0.93 + (n1(u * 32, v * 32) - 0.5) * 0.12 + (n2(u * 128, v * 128) - 0.5) * 0.1; const g = 240 * k; return [g, g * 0.985, g * 0.96]; });
      for (let i = 0; i < 2600; i++) {                       // pebbles: light tops, dark undersides
        const px = r() * N, py = r() * N, s = 0.7 + r() * 2.2, d = r() < 0.4;
        x.fillStyle = d ? 'rgba(90,78,62,' + (0.12 + r() * 0.2) + ')' : 'rgba(255,252,244,' + (0.25 + r() * 0.35) + ')';
        x.beginPath(); x.ellipse(px, py, s, s * (0.6 + r() * 0.4), r() * 3, 0, TAU); x.fill();
      }
    });
  }
  function asphaltTex() {
    return canvasTex('asphalt', 512, (x, N, r) => {
      const n1 = tileNoise(401, 16), n2 = tileNoise(409, 128);
      pixelPaint(x, N, (i, j) => { const u = i / N, v = j / N;
        const k = 0.9 + (n1(u * 16, v * 16) - 0.5) * 0.1 + (n2(u * 128, v * 128) - 0.5) * 0.22; const g = 230 * k; return [g, g, g * 1.01]; });
      for (let i = 0; i < 5000; i++) { const px = r() * N, py = r() * N, s = 0.6 + r() * 1.6;
        x.fillStyle = r() < 0.6 ? 'rgba(255,255,255,' + (0.12 + r() * 0.25) + ')' : 'rgba(0,0,0,' + (0.2 + r() * 0.3) + ')';
        x.fillRect(px, py, s, s); }
      for (let i = 0; i < 6; i++) {                          // sealed cracks: dark tar lines
        x.strokeStyle = 'rgba(10,10,12,0.5)'; x.lineWidth = 2 + r() * 2; x.beginPath();
        let px = r() * N, py = r() * N; x.moveTo(px, py);
        for (let k = 0; k < 8; k++) { px += (r() - 0.5) * 70; py += (r() - 0.3) * 60; x.lineTo(px, py); } x.stroke();
      }
    });
  }
  // Pale slip form concrete: faint horizontal lifts, vertical rain streaks. Covers 6 m.
  function slipformTex() {
    return canvasTex('slipform', 256, (x, N, r) => {
      const n1 = tileNoise(501, 16), n2 = tileNoise(503, 96), n3 = tileNoise2(509, 64, 2);
      pixelPaint(x, N, (i, j) => { const u = i / N, v = j / N;
        let k = 0.92 + (n1(u * 16, v * 16) - 0.5) * 0.08 + (n2(u * 96, v * 96) - 0.5) * 0.07;
        const st = n3(u * 64, v * 2); k -= st > 0.6 ? (st - 0.6) * 0.45 : 0;                  // rain streaks
        if (j % 32 < 1) k *= 0.93;                                                  // lifts, about 0.75 m
        const g = 238 * k; return [g, g * 0.985, g * 0.955]; });
    });
  }

  /* ---- far materials: own aerial haze, never grimed by TXT.weather ---------------------- */
  const FARM = new Map();
  function farMat(key, params, rate, cap, physical) {
    const k = key + '|' + rate + '|' + cap;
    if (FARM.has(k)) return FARM.get(k);
    const P = Object.assign({ roughness: 0.9, metalness: 0 }, params);
    const m = physical ? new THREE.MeshPhysicalMaterial(P) : new THREE.MeshStandardMaterial(P);
    if (rate > 0) aerial(m, rate, cap);
    FARM.set(k, m);
    return m;
  }
  const asGround = (obj) => { obj.traverse((m) => { if (m.isMesh) m.userData.txGround = true; }); return obj; };
  // cliff and talus rock: horizontal strata, vertical joints; tiles every 24 m
  function strataTex() {
    return canvasTex('strata', 512, (x, N, r) => {
      const n1 = tileNoise2(601, 4, 48), n2 = tileNoise(603, 64), n3 = tileNoise2(607, 96, 6);
      pixelPaint(x, N, (i, j) => { const u = i / N, v = j / N;
        let k = 0.86 + (n1(u * 4, v * 48) - 0.5) * 0.28 + (n2(u * 64, v * 64) - 0.5) * 0.14;
        const jt = n3(u * 96, v * 6); if (jt > 0.72) k *= 1 - (jt - 0.72) * 1.2;      // joints
        const g = 245 * k; return [g, g * 0.97, g * 0.93]; });
    });
  }

  /* ======================================================================================
   * mesa: a West Texas mesa or butte, caprock over a talus apron
   * ====================================================================================== */
  K.define('mesa', {
    size: [900, 90, 700],
    options: { kind: 'mesa', width: 500, height: 90, cap: 0.16, rock: 'red', aerial: 0.00022, scrub: 1 },
    note: 'A caprock mesa (or kind:"butte") with a vertical cap ledge, a soft slope under it and a gullied talus apron that meets the ground. Far distance: 1 to 8 km. aerial is its own haze rate per metre (0 = use the scene fog). rock: red (Permian, Caprock Canyons) or tan (Trans-Pecos).',
    make(o, r) {
      o = Object.assign({ kind: 'mesa', width: 500, height: 90, cap: 0.16, rock: 'red', aerial: 0.00022, scrub: 1 }, o);
      const g = new THREE.Group(), seed = 3000 + o.seed * 17;
      const H = o.height, butte = o.kind === 'butte';
      const R0 = butte ? Math.max(H * 0.55, 30) : o.width / 2;
      const nA = noise2(seed), nB = noise2(seed + 1), nG = noise2(seed + 2);
      const capT = H * o.cap, talusL = H * 2.1;
      const NT = 384;
      // plan shape: a lobed outline for a mesa, near round for a butte
      const rimR = (th) => {
        const c = Math.cos(th), s = Math.sin(th);
        const lobes = fbm(nA, c * 1.3 + 5, s * 1.3 + 5, 4);
        const e = butte ? 1 : (1 + 0.35 * c * c);                    // longer than deep
        return R0 * e * (0.72 + 0.55 * lobes) * (1 + (nB(th * 40, 3) - 0.5) * 0.035);
      };
      // radial profile: [offset from rim (m), height (m), gully weight, band]
      const prof = [];
      [0.0, 0.35, 0.6, 0.8, 0.93].forEach((f) => prof.push({ top: f }));
      prof.push({ d: 0, h: H, gw: 0, band: 0 });
      prof.push({ d: 0.6, h: H - capT * 0.35, gw: 0.05, band: 1 });
      prof.push({ d: 1.2, h: H - capT, gw: 0.1, band: 1 });
      const h1 = H - capT;
      for (let i = 1; i <= 4; i++) { const t = i / 4; prof.push({ d: 1.2 + capT * 0.9 * t, h: h1 - capT * 0.9 * Math.pow(t, 0.8), gw: 0.3, band: 2 }); }
      const h2 = h1 - capT * 0.9, d2 = 1.2 + capT * 0.9;
      for (let i = 1; i <= 16; i++) { const t = i / 16; prof.push({ d: d2 + talusL * t, h: h2 * Math.pow(1 - t, 1.9), gw: 1, band: 3 }); }
      prof.push({ d: d2 + talusL * 1.12, h: -0.5, gw: 1, band: 4 });
      const rows = prof.length, pos = new Float32Array(NT * rows * 3 + 3), colr = new Float32Array(NT * rows * 3 + 3), uv = new Float32Array(NT * rows * 2 + 2);
      const pal = o.rock === 'tan'
        ? { cap: 0xc9b58f, face: 0xb49c78, soft: 0xa58766, talus: 0x9c8466, foot: 0x8e7f5e }
        : { cap: 0xcdb892, face: 0xb07a58, soft: 0xa55f43, talus: 0x9a6248, foot: 0x8a6f52 };
      const cCap = col(pal.cap), cFace = col(pal.face), cSoft = col(pal.soft), cTal = col(pal.talus), cFoot = col(pal.foot), cTop = col(0x8c8458), tmp = new THREE.Color();
      for (let i = 0; i < NT; i++) {
        const th = i / NT * TAU, c = Math.cos(th), s = Math.sin(th), Rr = rimR(th);
        const gul = Math.pow(Math.abs(fbm(nG, th * 9 + fbm(nA, th * 3, 2, 2) * 3, 1.5, 3) * 2 - 1), 0.55);   // 0 in a gully, 1 on a spur
        for (let k = 0; k < rows; k++) {
          const P = prof[k]; let rad, y;
          if (P.top != null) { rad = Rr * P.top; y = H + (fbm(nB, c * P.top * 3, s * P.top * 3, 3) - 0.5) * H * 0.04 + 0.3 * (1 - P.top); }
          else {
            const t = P.d / (d2 + talusL);
            rad = Rr + P.d * (1 + (gul - 0.5) * 0.5 * P.gw);
            y = P.h;
            if (P.band >= 2 && P.band < 4) y *= 1 - (1 - gul) * 0.1 * P.gw * Math.sin(Math.PI * Math.min(1, t * 1.4));
            y += (nB(th * 60, P.d * 0.2) - 0.5) * 1.2 * P.gw;
          }
          const q = (i * rows + k) * 3;
          pos[q] = c * rad; pos[q + 1] = y; pos[q + 2] = s * rad;
          if (P.top != null) mix3(tmp, cTop, cCap, 0.35 + 0.3 * fbm(nA, c * 4 * P.top, s * 4 * P.top, 2));
          else if (P.band <= 1) tmp.copy(cCap).multiplyScalar(P.band ? 0.92 : 1.02);
          else if (P.band === 2) mix3(tmp, cFace, cSoft, (P.h > 0 ? (h1 - P.h) / (capT * 0.9) : 1));
          else { const t = (h2 - P.h) / h2; mix3(tmp, cSoft, cTal, smooth(0, 0.35, t)); mix3(tmp, tmp, cFoot, smooth(0.6, 1, t)); tmp.multiplyScalar(0.88 + gul * 0.18); }
          colr[q] = tmp.r; colr[q + 1] = tmp.g; colr[q + 2] = tmp.b;
          uv[(i * rows + k) * 2] = th * Rr / 24; uv[(i * rows + k) * 2 + 1] = y / 24;
        }
      }
      const idx = [];
      for (let i = 0; i < NT; i++) { const i2 = (i + 1) % NT;
        for (let k = 0; k < rows - 1; k++) { const a = i * rows + k, b = i2 * rows + k, c2 = i * rows + k + 1, d = i2 * rows + k + 1; idx.push(a, b, c2, b, d, c2); } }
      const cI = NT * rows; pos[cI * 3] = 0; pos[cI * 3 + 1] = H + 0.3; pos[cI * 3 + 2] = 0;   // centre of the top
      colr[cI * 3] = cTop.r; colr[cI * 3 + 1] = cTop.g; colr[cI * 3 + 2] = cTop.b;
      for (let i = 0; i < NT; i++) idx.push(cI, ((i + 1) % NT) * rows, i * rows);
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
      geo.setAttribute('color', new THREE.BufferAttribute(colr, 3));
      geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
      geo.setIndex(idx); geo.computeVertexNormals();
      const m = farMat('mesa', { color: 0xffffff, vertexColors: true, map: strataTex(), roughness: 0.95 }, o.aerial, 0.82);
      g.add(new THREE.Mesh(geo, m));
      // scrub dotted over the talus and the top: mesquite, juniper, creosote
      if (o.scrub > 0) {
        const sg = paintGeo(lump(seed + 9, 1, 1, 0.8, 1, 0.6), 0xffffff), list = [], cs = [];
        const n = Math.round(700 * o.scrub * (R0 / 250)), cols = [0x4a4f33, 0x57593a, 0x3f452d].map(col);
        for (let i = 0; i < n; i++) {
          const th = r() * TAU, onTop = r() < 0.3, Rr = rimR(th);
          let rad, y;
          if (onTop) { rad = Rr * Math.sqrt(r()) * 0.95; y = H; }
          else { const t = 0.15 + r() * 0.85; rad = Rr + d2 + talusL * t; y = h2 * Math.pow(1 - t, 1.9); }
          const s = 1.2 + r() * 2.2;
          list.push({ x: Math.cos(th) * rad, y: y + s * 0.3, z: Math.sin(th) * rad, ry: r() * TAU, sx: s, sy: s * 0.8, sz: s });
          cs.push(cols[Math.floor(r() * cols.length)].clone().multiplyScalar(0.8 + r() * 0.4));
        }
        const sm = farMat('mesa-scrub', { color: 0xffffff, roughness: 0.95 }, o.aerial, 0.82);
        g.add(instanced(sg, sm, list, cs));
        // fallen caprock blocks on the upper talus
        const bg = lump(seed + 11, 1, 1, 0.7, 1, 0.5), bl = [], bc = [];
        for (let i = 0; i < n * 0.4; i++) {
          const th = r() * TAU, t = Math.pow(r(), 1.6) * 0.6, Rr = rimR(th), rad = Rr + d2 + talusL * t, y = h2 * Math.pow(1 - t, 1.9), s = 1.5 + r() * 4;
          bl.push({ x: Math.cos(th) * rad, y: y + s * 0.2, z: Math.sin(th) * rad, ry: r() * TAU, rx: r() * 0.5, sx: s * 1.3, sy: s * 0.8, sz: s });
          bc.push(cCap.clone().multiplyScalar(0.75 + r() * 0.3));
        }
        const bm = farMat('mesa-block', { color: 0xffffff, roughness: 0.9 }, o.aerial, 0.82);
        g.add(instanced(bg, bm, bl, bc));
      }
      return asGround(g);
    },
  });

  /* ======================================================================================
   * city_skyline: a far skyline in haze, massed towers, plausible and not traced
   * ====================================================================================== */
  // facade textures (36 m tile: 9 floors of 4 m, 12 bays of 3 m) and a lit window mask
  function facadeTex(style) {
    return canvasTex('facade-' + style, 512, (x, N, r) => {
      const floors = 9, bays = 12, fh = N / floors, bw = N / bays;
      const S = { glass: ['#6f8394', '#8fa2b0', '#3c4a57'], dark: ['#3a434c', '#4c5761', '#1d2329'], stone: ['#cbbfa8', '#b9ab92', '#3a3a3c'],
                  brick: ['#a7765a', '#94664d', '#2e2a28'], white: ['#d8d6d0', '#c8c6c0', '#4a5460'] }[style];
      x.fillStyle = S[0]; x.fillRect(0, 0, N, N);
      for (let f = 0; f < floors; f++) for (let b = 0; b < bays; b++) {
        const k = 0.85 + r() * 0.3;
        if (style === 'glass' || style === 'dark') {
          const g = x.createLinearGradient(0, f * fh, 0, f * fh + fh);
          g.addColorStop(0, S[1]); g.addColorStop(1, S[0]);
          x.globalAlpha = 0.5 + r() * 0.5; x.fillStyle = g; x.fillRect(b * bw + 1, f * fh + 2, bw - 2, fh - 4); x.globalAlpha = 1;
          x.fillStyle = 'rgba(0,0,0,' + (0.05 + r() * 0.12 * k) + ')'; x.fillRect(b * bw + 1, f * fh + 2, bw - 2, fh - 4);
        } else {
          x.fillStyle = S[2]; x.globalAlpha = 0.8; x.fillRect(b * bw + bw * 0.22, f * fh + fh * 0.22, bw * 0.56, fh * 0.52); x.globalAlpha = 1;
        }
      }
      x.fillStyle = 'rgba(0,0,0,0.25)';
      for (let f = 0; f < floors; f++) x.fillRect(0, f * fh, N, style === 'glass' || style === 'dark' ? 3 : 2);   // spandrel lines
      if (style === 'glass' || style === 'dark') for (let b = 0; b < bays; b++) x.fillRect(b * bw, 0, 1.5, N);   // mullions
    });
  }
  function litTex(style, share) {
    return canvasTex('lit-' + style + share, 512, (x, N, r) => {
      const floors = 9, bays = 12, fh = N / floors, bw = N / bays, glass = style === 'glass' || style === 'dark';
      x.fillStyle = '#000'; x.fillRect(0, 0, N, N);
      for (let f = 0; f < floors; f++) {
        const rowOn = r() < 0.75;
        for (let b = 0; b < bays; b++) {
          if (!rowOn || r() > share) continue;
          const warm = r() < 0.7, k = 0.55 + r() * 0.45;
          x.fillStyle = warm ? 'rgba(255,' + Math.round(196 * k + 30) + ',' + Math.round(120 * k) + ',' + k + ')' : 'rgba(210,230,255,' + k * 0.8 + ')';
          if (glass) x.fillRect(b * bw + 1, f * fh + 4, bw - 2, fh - 8);
          else x.fillRect(b * bw + bw * 0.22, f * fh + fh * 0.22, bw * 0.56, fh * 0.52);
        }
      }
    });
  }
  const CITY = {
    // n towers, [min, max] height, cluster radius, styles with weights, landmark
    dallas:      { n: 30, h: [55, 280], rad: 520, styles: ['glass', 'glass', 'dark', 'stone', 'white'], tops: ['flat', 'pent', 'pyramid', 'slant', 'stepped', 'flat'], mark: 'ball', lowrise: 180 },
    houston:     { n: 44, h: [60, 300], rad: 640, styles: ['dark', 'glass', 'glass', 'stone', 'dark'], tops: ['flat', 'gable', 'slant', 'stepped', 'pent', 'flat', 'pyramid'], mark: null, lowrise: 240 },
    austin:      { n: 32, h: [45, 215], rad: 460, styles: ['glass', 'white', 'glass', 'stone'], tops: ['flat', 'pent', 'notch', 'slant', 'flat'], mark: 'dome', lowrise: 160 },
    san_antonio: { n: 20, h: [35, 150], rad: 420, styles: ['stone', 'brick', 'glass', 'white'], tops: ['flat', 'stepped', 'pent', 'pyramid'], mark: 'needle', lowrise: 200 },
  };
  K.define('city_skyline', {
    size: [2400, 300, 1400],
    options: { city: 'dallas', dusk: false, lit: 0.3, aerial: 0.00011, lowrise: true },
    note: 'A far skyline for dallas, houston, austin or san_antonio: massed towers with each city\'s broad character (Dallas: a mixed cluster and a ball topped observation tower; Houston: the tallest, densest dark glass; Austin: slender residential glass and a domed capitol; San Antonio: low masonry and a needle tower). dusk lights windows and aviation beacons. Place 2 to 10 km away and raise R.camera.far past it; aerial is its own haze rate per metre. Blank facades, no logos.',
    make(o, r) {
      o = Object.assign({ city: 'dallas', dusk: false, lit: 0.3, aerial: 0.00011, lowrise: true }, o);
      const C = CITY[o.city] || CITY.dallas, g = new THREE.Group();
      const byMat = new Map();
      const add = (geo, style) => { if (!byMat.has(style)) byMat.set(style, []); byMat.get(style).push(geo); };
      const nC = noise2(4000 + o.seed);
      const box = (w, h, d, x, y, z, ry) => { const b = new THREE.BoxGeometry(w, h, d); b.translate(0, h / 2, 0); if (ry) b.rotateY(ry); b.translate(x, y, z); return b; };
      const towers = [];
      // tower sites: dense core, height falls off with distance from the core; tallest near centre
      for (let i = 0; i < C.n; i++) {
        let x, z, tries = 0, ok = false;
        while (!ok && tries++ < 40) {
          const a = r() * TAU, d = C.rad * Math.pow(r(), 0.8);
          x = Math.cos(a) * d * 1.3; z = Math.sin(a) * d * 0.7;
          ok = towers.every((t) => Math.hypot(t.x - x, t.z - z) > (t.w + 30));
        }
        const core = 1 - Math.hypot(x / 1.3, z / 0.7) / C.rad;
        const h = lerp(C.h[0], C.h[1], Math.pow(clamp(core * 0.8 + r() * 0.5, 0, 1), 1.6));
        const w = clamp(h * (0.16 + r() * 0.14), 22, 62), d = w * (0.6 + r() * 0.6);
        towers.push({ x, z, h, w, d, style: C.styles[Math.floor(r() * C.styles.length)], top: C.tops[Math.floor(r() * C.tops.length)], ry: (r() < 0.25 ? (r() - 0.5) * 0.9 : 0) + 0.02 });
      }
      towers.sort((a, b) => b.h - a.h);
      if (o.city === 'austin') towers.forEach((t) => { t.w *= 0.8; t.d = Math.min(t.d, t.w * 1.1); });
      towers.forEach((t) => {
        const { x, z, h, w, d, ry } = t;
        let top = h;
        if (t.top === 'stepped') {
          const b1 = h * 0.72, b2 = h * 0.14, b3 = h * 0.14;
          add(box(w, b1, d, x, 0, z, ry), t.style); add(box(w * 0.78, b2, d * 0.78, x, b1, z, ry), t.style); add(box(w * 0.56, b3, d * 0.56, x, b1 + b2, z, ry), t.style);
          top = h;
        } else if (t.top === 'slant') {
          const b = new THREE.BoxGeometry(w, h, d, 1, 1, 1); b.translate(0, h / 2, 0);
          const p = b.attributes.position; for (let i = 0; i < p.count; i++) if (p.getY(i) > h - 1 && p.getX(i) < 0) p.setY(i, h - w * 0.55);
          b.computeVertexNormals(); if (ry) b.rotateY(ry); b.translate(x, 0, z); add(b, t.style);
        } else if (t.top === 'gable') {                 // a stepped gabled crown in the Dutch revival manner
          const b1 = h * 0.8; add(box(w, b1, d, x, 0, z, ry), t.style);
          for (let k = 0; k < 3; k++) add(box(w * (0.86 - k * 0.2), h * 0.06, d * 0.9, x, b1 + k * h * 0.06, z, ry), t.style);
          const sh = new THREE.Shape([new THREE.Vector2(-w * 0.26, 0), new THREE.Vector2(w * 0.26, 0), new THREE.Vector2(0, h * 0.1)].map((v) => v));
          const e = new THREE.ExtrudeGeometry(sh, { depth: d * 0.85, bevelEnabled: false }); e.translate(0, b1 + h * 0.18, -d * 0.425); if (ry) e.rotateY(ry); e.translate(x, 0, z); add(e, t.style);
          add(new THREE.CylinderGeometry(0.4, 0.8, h * 0.12, 6).translate(x, b1 + h * 0.34, z), t.style);
        } else if (t.top === 'pyramid') {
          add(box(w, h * 0.9, d, x, 0, z, ry), t.style);
          const c = new THREE.ConeGeometry(Math.min(w, d) * 0.72, h * 0.14, 4, 1); c.rotateY(Math.PI / 4 + (ry || 0)); c.scale(w / Math.min(w, d), 1, d / Math.min(w, d)); c.translate(x, h * 0.9 + h * 0.07, z); add(c, t.style);
          top = h * 1.04;
        } else if (t.top === 'notch') {                 // two horns, a crown cut in the middle
          add(box(w, h * 0.9, d, x, 0, z, ry), t.style);
          add(box(w * 0.22, h * 0.1, d, x - w * 0.39, h * 0.9, z, ry), t.style); add(box(w * 0.22, h * 0.1, d, x + w * 0.39, h * 0.9, z, ry), t.style);
        } else {
          add(box(w, h, d, x, 0, z, ry), t.style);
          if (t.top === 'pent') add(box(w * 0.5, h * 0.05, d * 0.5, x, h, z, ry), 'roof');
          else add(box(w * 0.3, 4, d * 0.3, x + w * 0.1, h, z, ry), 'roof');
        }
        // a podium at the base: lobbies, parking decks
        add(box(w * 1.6, 12 + r() * 10, d * 1.5, x, 0, z, ry), 'podium');
        t.topY = top;
      });
      // the landmark, generic and never traced
      const marks = [];
      if (C.mark === 'ball') {                           // an observation tower with a ball head
        const mx = C.rad * 0.9, mz = C.rad * 0.25;
        add(new THREE.CylinderGeometry(4.5, 6, 150, 16).translate(mx, 75, mz), 'concrete');
        add(new THREE.SphereGeometry(18, 24, 16).translate(mx, 162, mz), 'ball');
        marks.push([mx, 185, mz]);
      } else if (C.mark === 'dome') {                   // a domed capitol at the end of the avenue
        const mx = 0, mz = -C.rad * 0.95;
        add(box(90, 26, 60, mx, 0, mz), 'granite'); add(box(26, 24, 26, mx, 26, mz), 'granite');
        add(new THREE.CylinderGeometry(15, 15, 18, 28).translate(mx, 59, mz), 'granite');
        add(new THREE.SphereGeometry(15, 28, 14, 0, TAU, 0, Math.PI / 2).scale(1, 1.35, 1).translate(mx, 68, mz), 'granite');
        add(new THREE.CylinderGeometry(2.5, 3, 9, 12).translate(mx, 88, mz), 'granite');
        marks.push([mx, 96, mz]);
      } else if (C.mark === 'needle') {                 // a concrete needle with a top house
        const mx = -C.rad * 0.7, mz = C.rad * 0.3;
        add(new THREE.CylinderGeometry(5, 8.5, 175, 16).translate(mx, 87.5, mz), 'concrete');
        add(new THREE.CylinderGeometry(21, 16, 16, 24).translate(mx, 183, mz), 'glass');
        add(new THREE.CylinderGeometry(20, 21, 5, 24).translate(mx, 193.5, mz), 'concrete');
        add(new THREE.CylinderGeometry(0.8, 1.2, 30, 6).translate(mx, 211, mz), 'roof');
        marks.push([mx, 226, mz]);
      }
      // low rise: the city floor the towers stand on
      if (o.lowrise) {
        for (let i = 0; i < C.lowrise; i++) {
          const a = r() * TAU, dd = C.rad * (0.3 + 1.1 * Math.sqrt(r()));
          const x = Math.cos(a) * dd * 1.5, z = Math.sin(a) * dd * 0.8, h = 8 + Math.pow(r(), 2) * 35, w = 20 + r() * 40;
          add(box(w, h, w * (0.5 + r()), x, 0, z, r() < 0.2 ? r() : 0), r() < 0.5 ? 'stone' : (r() < 0.5 ? 'brick' : 'white'));
        }
      }
      // aviation beacons on the tall roofs
      towers.forEach((t) => { if (t.h > 150) marks.push([t.x, t.topY + 3, t.z]); });
      const rate = o.aerial, cap = 0.8, lit = o.dusk ? o.lit : 0;
      byMat.forEach((geos, style) => {
        geos.forEach((gg) => K.uvBox(gg, 36));
        const geo = mergeGeos(geos);
        let m;
        if (style === 'roof' || style === 'podium') m = farMat('sky-' + style + lit, { color: style === 'roof' ? 0x6d6e70 : 0x9d9990, roughness: 0.85, emissive: 0xffc88a, emissiveIntensity: style === 'podium' && lit ? 0.12 : 0 }, rate, cap);
        else if (style === 'concrete' || style === 'granite') m = farMat('sky-' + style, { color: style === 'granite' ? 0xd9b9a0 : 0xbdb8ae, roughness: 0.8 }, rate, cap);
        else if (style === 'ball') m = farMat('sky-ball', { color: 0x9aa4ab, roughness: 0.3, metalness: 0.7, emissive: 0xfff0d8, emissiveIntensity: lit ? 0.9 : 0 }, rate, cap);
        else {
          const glassy = style === 'glass' || style === 'dark';
          m = farMat('sky-' + style + '-' + lit, { color: 0xffffff, map: facadeTex(style), roughness: glassy ? 0.18 : 0.85, metalness: glassy ? 0.55 : 0,
            envMapIntensity: glassy ? 1.4 : 0.8, emissive: lit ? 0xffffff : 0x000000, emissiveMap: lit ? litTex(style, lit) : null, emissiveIntensity: lit ? 1.2 : 0 }, rate, cap);
        }
        g.add(new THREE.Mesh(geo, m));
      });
      if (o.dusk && marks.length) {
        const bm = farMat('beacon', { color: 0x220000, emissive: 0xff2a1a, emissiveIntensity: 6 }, rate * 0.6, 0.6);
        g.add(instanced(new THREE.SphereGeometry(1.6, 8, 6), bm, marks.map((p) => ({ x: p[0], y: p[1], z: p[2] }))));
      }
      return asGround(g);
    },
  });

  /* ---- a ribbon along a centre line: rows of cross sections ------------------------------
   * centre(t) -> [x, z], profile: array of { s (lateral m), h (m), c (THREE.Color) }, n rows. */
  function ribbon(centre, length, n, profile, hAt) {
    const cols = profile.length, pos = new Float32Array(n * cols * 3), clr = new Float32Array(n * cols * 3), uv = new Float32Array(n * cols * 2);
    let arc = 0, prev = null;
    for (let i = 0; i < n; i++) {
      const t = i / (n - 1), c = centre(t), c2 = centre(Math.min(1, t + 1e-3)), c1 = centre(Math.max(0, t - 1e-3));
      let tx = c2[0] - c1[0], tz = c2[1] - c1[1]; const L = Math.hypot(tx, tz); tx /= L; tz /= L;
      const nx = tz, nz = -tx;                                  // the lateral, to the right of travel
      if (prev) arc += Math.hypot(c[0] - prev[0], c[1] - prev[1]); prev = c;
      for (let k = 0; k < cols; k++) {
        const P = profile[k], q = (i * cols + k);
        const x = c[0] + nx * P.s, z = c[1] + nz * P.s;
        pos[q * 3] = x; pos[q * 3 + 1] = hAt ? hAt(P, t, arc, x, z) : P.h; pos[q * 3 + 2] = z;
        clr[q * 3] = P.c.r; clr[q * 3 + 1] = P.c.g; clr[q * 3 + 2] = P.c.b;
        uv[q * 2] = P.s; uv[q * 2 + 1] = arc;
      }
    }
    const idx = [];
    for (let i = 0; i < n - 1; i++) for (let k = 0; k < cols - 1; k++) {
      const a = i * cols + k, b = a + 1, c = a + cols, d = c + 1; idx.push(a, c, b, b, c, d);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    g.setAttribute('color', new THREE.BufferAttribute(clr, 3));
    g.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
    g.setIndex(idx); g.computeVertexNormals();
    return g;
  }
  const gauss = (x, w) => Math.exp(-(x * x) / (2 * w * w));

  /* ======================================================================================
   * caliche_road: a pale unpaved ranch road
   * ====================================================================================== */
  K.define('caliche_road', {
    size: [9, 0.3, 60],
    options: { length: 60, width: 4.2, curve: 0.25, centerGrass: true, verge: 2.6 },
    note: 'A pale caliche ranch road running along z: a crowned bed, two packed wheel tracks, a weedy centre strip, graded berms of loose gravel and grass verges that sink into TXT.ground. curve bows it sideways (fraction of length/4).',
    make(o, r) {
      o = Object.assign({ length: 60, width: 4.2, curve: 0.25, centerGrass: true, verge: 2.6 }, o);
      const g = new THREE.Group(), L = o.length, W = o.width, V = o.verge, seed = 5000 + o.seed * 13;
      const n1 = noise2(seed), n2 = noise2(seed + 1);
      const centre = (t) => [o.curve * L * 0.25 * (1 - Math.pow(2 * t - 1, 2)) - o.curve * L * 0.125 + (n1(t * 4, 2) - 0.5) * 0.6, L / 2 - t * L];
      const cRoad = col(0xebe2ca), cTrack = col(0xf4eddb), cLoose = col(0xddd1b3), cVerge = col(0x8a8250), cEdge = col(0x857d4c), cMid = col(0x9d9464);
      const prof = [];
      const S = [-W / 2 - V, -W / 2 - V * 0.6, -W / 2 - V * 0.3, -W / 2 - 0.35, -W / 2 - 0.1];
      S.forEach((s) => prof.push({ s }));
      for (let k = 0; k <= 22; k++) prof.push({ s: -W / 2 + W * k / 22 });
      S.slice().reverse().forEach((s) => prof.push({ s: -s }));
      const track = 0.86;                                         // half the track of a pickup
      prof.forEach((P) => {
        const a = Math.abs(P.s), inRoad = a <= W / 2 + 1e-6;
        const tr = gauss(a - track, 0.2);
        if (inRoad) {
          P.h = 0.07 + 0.07 * (1 - Math.pow(a / (W / 2), 2)) - 0.045 * tr;
          P.c = new THREE.Color(); mix3(P.c, cRoad, cTrack, tr);
          if (o.centerGrass) mix3(P.c, P.c, cMid, gauss(a, 0.28) * 0.75);
          mix3(P.c, P.c, cLoose, smooth(W / 2 - 0.5, W / 2, a));
        } else {
          const e = (a - W / 2) / V;
          P.h = e < 0.1 ? 0.1 : lerp(0.08, -0.08, smooth(0.08, 0.4, e));   // the grader berm, then down under the ground
          P.c = new THREE.Color(); mix3(P.c, cLoose, cVerge, smooth(0.03, 0.2, e)); mix3(P.c, P.c, cEdge, smooth(0.5, 1, e));
        }
      });
      const n = Math.round(L / 0.4);
      const geo = ribbon(centre, L, n, prof, (P, t, arc, x, z) => {
        const a = Math.abs(P.s), inRoad = a <= W / 2;
        let h = P.h + (n2(x * 0.6, z * 0.6) - 0.5) * (inRoad ? 0.03 : 0.06);
        if (inRoad) h -= smooth(0.72, 0.9, n2(x * 0.25 + 9, z * 0.25)) * 0.03 * gauss(a - track, 0.3);   // potholes in the tracks
        const endFade = Math.min(t, 1 - t) * L;                   // ends feather into the ground too
        return endFade < 0.01 ? Math.min(h, -0.02) : h;
      });
      const uv = geo.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) / 2.2, uv.getY(i) / 2.2);
      const m = M('caliche-road', { color: 0xffffff, vertexColors: true, map: gravelTex(), roughness: 0.93 });
      const mesh = new THREE.Mesh(geo, m); mesh.userData.txGround = true; g.add(mesh);
      // tufts on the verges and the centre strip, loose stones on the berms
      const tufts = [], rocks = [];
      for (let i = 0; i < L * 18; i++) {
        const t = r(), c = centre(t), c2 = centre(Math.min(1, t + 0.01)), tx = c2[0] - c[0], tz = c2[1] - c[1], l = Math.hypot(tx, tz), nx = tz / l, nz = -tx / l;
        const side = r() < 0.5 ? -1 : 1;
        let s, k;
        const pick = r();
        if (pick < 0.7) { s = side * (W / 2 + 0.2 + Math.pow(r(), 0.8) * V * 1.2); k = 0.7 + r() * 0.8; }
        else if (pick < 0.8 && o.centerGrass) { s = (r() - 0.5) * 0.45; k = 0.35 + r() * 0.35; }
        else { s = side * (W / 2 - 0.1 + r() * 0.45); rocks.push([c[0] + nx * s, 0.08, c[1] + nz * s, 0.03 + Math.pow(r(), 3) * 0.14]); continue; }
        tufts.push([c[0] + nx * s, 0.02, c[1] + nz * s, k]);
      }
      tuftField(r, tufts, { key: 'verge', blades: 16, height: 0.55, spread: 0.14, width: 0.011, lean: 0.4, colors: [0x5d5a38, 0x9c9160, 0xc9b98a] }, g);
      stones(r, rocks, 'caliche', [0xe8e2d2, 0xd6cdb6, 0xf0ebe0, 0xc4b99e], g, true);
      return g;
    },
  });

  /* ======================================================================================
   * highway: a divided Texas highway segment
   * ====================================================================================== */
  K.define('highway', {
    size: [40, 1, 80],
    options: { length: 80, lanes: 2, surface: 'asphalt', gantry: true, overpass: false, embank: 0.6 },
    note: 'A divided highway along z: two carriageways of 3.66 m lanes, 3 m outside and 1.2 m inside shoulders with rumble strips, white edge and 3 m / 9 m skip lines, yellow inside edge lines, an F-shape concrete median barrier, grassed side slopes. gantry adds an overhead truss with blank green panels over the right carriageway; overpass adds a crossing bridge on round columns and bent caps with MSE walled approaches.',
    make(o, r) {
      o = Object.assign({ length: 80, lanes: 2, surface: 'asphalt', gantry: true, overpass: false, embank: 0.6 }, o);
      const g = new THREE.Group(), L = o.length, E = o.embank, LW = 3.66, SI = 1.2, SO = 3.0, MED = 0.9;
      const CW = SI + o.lanes * LW + SO;                         // one carriageway
      const half = MED / 2 + CW;                                 // edge of pavement
      const slope = 4 * E + 3;                                   // side slope and ditch
      // ---- earthwork: grassed side slopes and a shallow ditch
      const cG = col(0x7d7a48), cG2 = col(0x8d8752), cEdge = col(0x857d4c);
      const eprof = [];
      [-half - slope, -half - slope * 0.7, -half - slope * 0.35, -half - 0.6, -half].forEach((s) => eprof.push({ s }));
      [half, half + 0.6, half + slope * 0.35, half + slope * 0.7, half + slope].forEach((s) => eprof.push({ s }));
      eprof.forEach((P) => { const e = (Math.abs(P.s) - half) / slope;
        P.h = e < 0.02 ? E - 0.02 : e < 0.1 ? E - 0.1 : lerp(E * 0.8, -0.08, smooth(0.1, 1, e));
        if (e > 0.6) P.h = lerp(-0.02, -0.08, (e - 0.6) / 0.4);
        P.c = new THREE.Color(); mix3(P.c, cG2, cG, smooth(0, 0.5, e)); mix3(P.c, P.c, cEdge, smooth(0.6, 1, e)); });
      // two strips (left and right), so the pavement box sits between them
      const straight = (t) => [0, L / 2 - t * L];
      const nE = noise2(6000 + o.seed);
      [eprof.slice(0, 5), eprof.slice(5)].forEach((pr) => {
        const geo = ribbon(straight, L, Math.round(L / 2), pr, (P, t, arc, x, z) => P.h + (Math.abs(P.s) > half + 0.7 ? (nE(x * 0.4, z * 0.4) - 0.5) * 0.12 : 0));
        const uv = geo.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) / 7, uv.getY(i) / 7);
        const m = new THREE.Mesh(geo, M('hw-slope', { color: 0xffffff, vertexColors: true, map: detailTex('grass'), roughness: 0.97 })); m.userData.txGround = true; g.add(m);
      });
      // ---- pavement: one slab, wheel paths darker by vertex colour, shoulders a lighter older mix
      const concrete = o.surface === 'concrete';
      const base = concrete ? col(0xd2cec4) : col(0x78777a), shoulder = concrete ? col(0xc6c1b6) : col(0x8b8987), polish = concrete ? col(0xb8b3a8) : col(0x5d5d60);
      const pprof = [];
      const xs = []; for (let k = 0; k <= 80; k++) xs.push(-half + 2 * half * k / 80);
      xs.forEach((s) => {
        const a = Math.abs(s) - MED / 2, P = { s, h: E + 0.02 * (1 - Math.abs(Math.abs(s) - (MED / 2 + CW / 2)) / (CW / 2)) };
        const c = new THREE.Color();
        const inLane = a > SI && a < SI + o.lanes * LW;
        if (!inLane) c.copy(shoulder);
        else { const u = (a - SI) % LW; const wp = gauss(u - 0.9, 0.28) + gauss(u - 2.75, 0.28); mix3(c, base, polish, clamp(wp, 0, 1) * 0.55); }
        P.c = c; pprof.push(P);
      });
      const pg = ribbon(straight, L, 3, pprof);
      const puv = pg.attributes.uv; for (let i = 0; i < puv.count; i++) puv.setXY(i, puv.getX(i) / 4, puv.getY(i) / 4);
      const pm = M('hw-pave-' + o.surface, { color: 0xffffff, vertexColors: true, map: concrete ? K.tex('concrete') : asphaltTex(), roughness: concrete ? 0.82 : 0.88 });
      const pave = new THREE.Mesh(pg, pm); g.add(pave);
      // pavement edge: the slab has a face down to the slope
      [-1, 1].forEach((sd) => { const e = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.3, L), pm); e.position.set(sd * (half - 0.1), E - 0.14, 0); g.add(e); });
      // ---- markings
      const white = M('hw-white', { color: 0xe9e7df, roughness: 0.55 }), yellow = M('hw-yellow', { color: 0xe0a82a, roughness: 0.55 });
      const lines = [], ylines = [];
      [-1, 1].forEach((sd) => {
        const inner = sd * (MED / 2 + SI), outer = sd * (MED / 2 + SI + o.lanes * LW);
        ylines.push(box(0.15, 0.006, L, yellow, inner, E + 0.02, 0));
        lines.push(box(0.2, 0.006, L, white, outer, E + 0.02, 0));
      });
      g.add(K.merge(lines, white)); g.add(K.merge(ylines, yellow));
      const dash = [], dashGeo = new THREE.BoxGeometry(0.15, 0.006, 3.05);
      [-1, 1].forEach((sd) => { for (let k = 1; k < o.lanes; k++) { const x = sd * (MED / 2 + SI + k * LW);
        for (let z = -L / 2 + 2; z < L / 2 - 1.5; z += 12.19) dash.push({ x, y: E + 0.023, z: z + 1.5 }); } });
      g.add(instanced(dashGeo, white, dash));
      // rumble strips: milled grooves across the shoulders
      const rum = [], rg = new THREE.BoxGeometry(0.4, 0.004, 0.18), rm = M('hw-rumble', { color: concrete ? 0x807c74 : 0x2b2b2e, roughness: 0.95 });
      [-1, 1].forEach((sd) => { const x = sd * (MED / 2 + SI + o.lanes * LW + 0.45); for (let z = -L / 2 + 0.3; z < L / 2; z += 0.3) rum.push({ x, y: E + 0.021, z }); });
      g.add(instanced(rg, rm, rum));
      // ---- F-shape median barrier, 0.81 m, cast in place, with a joint every 6 m and reflectors
      const bh = 0.81, fs = [[-0.305, 0], [-0.305, 0.075], [-0.21, 0.33], [-0.09, bh - 0.02], [-0.07, bh], [0.07, bh], [0.09, bh - 0.02], [0.21, 0.33], [0.305, 0.075], [0.305, 0]];
      const bgeo = new THREE.ExtrudeGeometry(new THREE.Shape(fs.map((p) => new THREE.Vector2(p[0], p[1]))), { depth: L, bevelEnabled: false, curveSegments: 1 });
      bgeo.translate(0, 0, -L / 2); bgeo.translate(0, E, 0); bgeo.computeVertexNormals(); K.uvBox(bgeo, 3);
      const bar = new THREE.Mesh(bgeo, concM()); g.add(bar);
      const joints = []; for (let z = -L / 2 + 6; z < L / 2; z += 6) joints.push({ x: 0, y: E, z });
      const jg = new THREE.ExtrudeGeometry(new THREE.Shape(fs.map((p) => new THREE.Vector2(p[0] * 1.01, p[1] * 0.999))), { depth: 0.012, bevelEnabled: false });
      g.add(instanced(jg, M('hw-joint', { color: 0x4d4b47, roughness: 0.9 }), joints));
      const refl = []; for (let z = -L / 2 + 3; z < L / 2; z += 12) refl.push({ x: 0, y: E + bh, z });
      g.add(instanced(new THREE.BoxGeometry(0.1, 0.07, 0.03).translate(0, 0.035, 0), M('hw-refl', { color: 0xe0a82a, roughness: 0.3, emissive: 0x402a00 }), refl));

      // ---- overhead sign gantry over the right carriageway
      if (o.gantry) {
        const steel = K.finish.galvanized(), gz = -L * 0.18, H = E + 5.8;
        const x0 = MED / 2 + 0.8, x1 = half + 1.6, span = x1 - x0;
        const truss = new THREE.Group();
        // columns: four chord box trusses on concrete footings
        [x0, x1].forEach((cx) => {
          box(1.1, 0.6, 1.1, concM(), cx, E - 0.3, gz, 0.03, truss);
          const cs = 0.3, parts = [];
          for (const dx of [-cs, cs]) for (const dz of [-cs, cs]) parts.push(K.bar([cx + dx, E + 0.3, gz + dz], [cx + dx, H + 0.9, gz + dz], 0.06, steel, 8));
          for (let y = E + 0.5; y < H + 0.8; y += 0.8) {
            parts.push(K.bar([cx - cs, y, gz - cs], [cx + cs, y + 0.8, gz - cs], 0.022, steel, 5));
            parts.push(K.bar([cx - cs, y, gz + cs], [cx + cs, y + 0.8, gz + cs], 0.022, steel, 5));
            parts.push(K.bar([cx - cs, y, gz - cs], [cx - cs, y + 0.8, gz + cs], 0.022, steel, 5));
            parts.push(K.bar([cx + cs, y, gz - cs], [cx + cs, y + 0.8, gz + cs], 0.022, steel, 5));
          }
          const bp = box(0.9, 0.04, 0.9, steel, cx, E + 0.3, gz); parts.push(bp);
          truss.add(K.merge(parts, steel));
        });
        // the horizontal: a box truss 1.2 m deep, 1.4 m tall, with a Warren lacing on every face
        const tb = H, th = 1.4, td = 0.6, parts = [];
        for (const yy of [tb, tb + th]) for (const dz of [-td, td]) parts.push(K.bar([x0 - 0.5, yy, gz + dz], [x1 + 0.5, yy, gz + dz], 0.07, steel, 10));
        const nb = Math.round(span / 1.2);
        for (let k = 0; k < nb; k++) {
          const xa = x0 + span * k / nb, xb = x0 + span * (k + 1) / nb;
          for (const dz of [-td, td]) parts.push(K.bar([xa, tb, gz + dz], [xb, tb + th, gz + dz], 0.028, steel, 5));
          parts.push(K.bar([xa, tb + th, gz - td], [xb, tb + th, gz + td], 0.024, steel, 5));
          parts.push(K.bar([xa, tb, gz - td], [xb, tb, gz + td], 0.024, steel, 5));
          parts.push(K.bar([xa, tb, gz - td], [xa, tb + th, gz - td], 0.024, steel, 5));
          parts.push(K.bar([xa, tb, gz + td], [xa, tb + th, gz + td], 0.024, steel, 5));
        }
        truss.add(K.merge(parts, steel));
        // blank guide sign panels: green retroreflective face, white border, aluminium backs, a catwalk below
        const green = M('hw-sign', { color: 0x0f5c34, roughness: 0.4, metalness: 0.05 }), border = M('hw-signb', { color: 0xecefea, roughness: 0.4 });
        const alu = M('hw-alu', { color: 0xb4b8bb, metalness: 0.7, roughness: 0.45 });
        const panels = [{ w: 5.2, h: 3.3, cx: x0 + span * 0.33 }, { w: 4.2, h: 3.0, cx: x0 + span * 0.76 }];
        panels.forEach((P) => {
          const y0 = tb - 0.25 - (3.3 - P.h) * 0.2;
          box(P.w, P.h, 0.06, alu, P.cx, y0 - 0.2, gz + td + 0.12, 0.01, truss);
          box(P.w - 0.02, P.h - 0.02, 0.02, border, P.cx, y0 - 0.19, gz + td + 0.16, 0, truss);
          box(P.w - 0.16, P.h - 0.16, 0.02, green, P.cx, y0 - 0.12, gz + td + 0.172, 0, truss);
          for (let k = 0; k < 3; k++) box(0.08, P.h + 0.3, 0.08, alu, P.cx - P.w * 0.4 + k * P.w * 0.4, y0 - 0.35, gz + td + 0.05, 0, truss);   // vertical hangers
        });
        const grate = M('hw-grate', { color: 0x8c9092, metalness: 0.6, roughness: 0.6 });
        box(span - 0.4, 0.05, 0.9, grate, (x0 + x1) / 2, tb - 0.75, gz + td + 0.6, 0, truss);
        const cr = []; for (let x = x0 + 0.4; x < x1 - 0.2; x += 1.5) cr.push(K.bar([x, tb - 0.7, gz + td + 1.05], [x, tb + 0.3, gz + td + 1.05], 0.02, steel, 5));
        cr.push(K.bar([x0 + 0.2, tb + 0.3, gz + td + 1.05], [x1 - 0.2, tb + 0.3, gz + td + 1.05], 0.025, steel, 6)); truss.add(K.merge(cr, steel));
        g.add(truss);
      }

      // ---- overpass: a crossing bridge on bents, with MSE walled approaches
      if (o.overpass) {
        const oz = L * 0.2, DW = 12.8, clear = 5.2, deckY = E + clear, gd = 1.4;      // girder depth
        const conc = concM(), dspan = half + 8, bridge = new THREE.Group();
        const deckTop = deckY + gd + 0.22;
        // deck slab and parapets (a TxDOT style slotted concrete rail)
        box(dspan * 2, 0.22, DW, conc, 0, deckY + gd, oz, 0.02, bridge);
        [-1, 1].forEach((sd) => {
          box(dspan * 2, 0.2, 0.45, conc, 0, deckTop, oz + sd * (DW / 2 - 0.22), 0.02, bridge);
          box(dspan * 2, 0.3, 0.3, conc, 0, deckTop + 0.55, oz + sd * (DW / 2 - 0.2), 0.04, bridge);
          const posts = []; for (let x = -dspan + 1; x < dspan; x += 2.4) posts.push(box(0.9, 0.36, 0.3, conc, x, deckTop + 0.2, oz + sd * (DW / 2 - 0.2)));
          bridge.add(K.merge(posts, conc));
          box(dspan * 2, gd * 0.9, 0.3, conc, 0, deckY + 0.1, oz + sd * (DW / 2 - 0.15), 0.03, bridge);   // fascia
        });
        // precast girders: bulb tee section extruded along x
        const gsec = [[-0.35, 0], [0.35, 0], [0.35, 0.18], [0.1, 0.3], [0.1, gd - 0.18], [0.55, gd - 0.1], [0.55, gd], [-0.55, gd], [-0.55, gd - 0.1], [-0.1, gd - 0.18], [-0.1, 0.3], [-0.35, 0.18]];
        const gg = new THREE.ExtrudeGeometry(new THREE.Shape(gsec.map((p) => new THREE.Vector2(p[0], p[1]))), { depth: dspan * 2, bevelEnabled: false });
        gg.rotateY(Math.PI / 2); gg.translate(-dspan, deckY, 0); K.uvBox(gg, 3);
        const gl = []; for (let k = 0; k < 5; k++) { const m = new THREE.Mesh(gg, conc); m.position.z = oz - DW / 2 + 1.4 + k * (DW - 2.8) / 4; gl.push(m); }
        bridge.add(K.merge(gl, conc));
        // bents: three round columns under a bent cap, at the median and beyond each shoulder
        [0, -(half + 2.5), half + 2.5].forEach((bx) => {
          box(1.3, 1.2, DW - 1, conc, bx, deckY - 1.2, oz, 0.05, bridge);
          for (let k = -1; k <= 1; k++) {
            const yb = bx === 0 ? E + 0.81 : 0, c = new THREE.Mesh(K.uvBox(new THREE.CylinderGeometry(0.46, 0.46, deckY - 1.2 - yb, 28), 3), conc);
            c.position.set(bx, yb + (deckY - 1.2 - yb) / 2, oz + k * (DW / 2 - 2)); bridge.add(c);
          }
        });
        // approaches: MSE panel walls on fill, falling to grade
        const ramp = 55, wallM = M('hw-mse', { color: 0xffffff, map: K.tex('concrete', { color: '#c9c3b8' }), roughness: 0.9 });
        [-1, 1].forEach((sd) => {
          const x0 = sd * dspan, x1 = sd * (dspan + ramp);
          const shape = new THREE.Shape([new THREE.Vector2(0, -0.2), new THREE.Vector2(ramp, -0.2), new THREE.Vector2(ramp, 0.0), new THREE.Vector2(0, deckTop - 0.02)]);
          const fg = new THREE.ExtrudeGeometry(shape, { depth: DW + 1.2, bevelEnabled: false }); fg.translate(0, 0, -(DW + 1.2) / 2);
          fg.translate(dspan, 0, 0); if (sd < 0) fg.rotateY(Math.PI);
          fg.translate(0, 0, oz); fg.computeVertexNormals(); K.uvBox(fg, 1.5);
          bridge.add(new THREE.Mesh(fg, wallM));
          // the road on top: asphalt skin and a coping
          const top = new THREE.Mesh(new THREE.BoxGeometry(ramp, 0.08, DW - 0.6), M('hw-ramp-asphalt', { color: 0xffffff, vertexColors: false, map: asphaltTex(), roughness: 0.88 }));
          top.position.set((x0 + x1) / 2, deckTop / 2 + 0.04, oz);
          top.rotation.z = sd > 0 ? -Math.atan2(deckTop, ramp) : Math.atan2(deckTop, ramp); top.scale.x = Math.hypot(ramp, deckTop) / ramp;
          bridge.add(top);
        });
        // the road across the deck
        const dtop = new THREE.Mesh(new THREE.BoxGeometry(dspan * 2, 0.06, DW - 0.9), M('hw-ramp-asphalt', { color: 0xffffff, vertexColors: false, map: asphaltTex(), roughness: 0.88 }));
        dtop.position.set(0, deckTop + 0.03, oz); bridge.add(dtop);
        g.add(bridge);
      }
      return g;
    },
  });

  /* ---- water surface over a bed: vertex alpha from depth, so shallows show their bottom -- */
  function waterSheet(w, d, sx, sz, level, bedAt, tint, shallow, key, cx, cz) {
    const geo = new THREE.PlaneGeometry(w, d, sx, sz); geo.rotateX(-Math.PI / 2); geo.translate(cx || 0, level, cz || 0);
    const p = geo.attributes.position, C = new Float32Array(p.count * 4), deep = col(tint), sh = col(shallow), c = new THREE.Color();
    for (let i = 0; i < p.count; i++) {
      const depth = level - bedAt(p.getX(i), p.getZ(i));
      const a = smooth(-0.02, 0.35, depth);
      mix3(c, sh, deep, smooth(0.0, 0.6, depth));
      C[i * 4] = c.r; C[i * 4 + 1] = c.g; C[i * 4 + 2] = c.b; C[i * 4 + 3] = depth < -0.05 ? 0 : 0.18 + 0.74 * a;
    }
    geo.setAttribute('color', new THREE.BufferAttribute(C, 4));
    const uv = geo.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * w / 6, uv.getY(i) * d / 6);
    const m = waterMat(key, 0xffffff, { alpha: true, wave: 0.28 });
    const mesh = new THREE.Mesh(geo, m); mesh.renderOrder = 2; mesh.userData.txGround = true;
    mesh.castShadow = false;
    return mesh;
  }

  /* ======================================================================================
   * creek: a Hill Country creek between low banks, limestone bedrock, gravel bars
   * ====================================================================================== */
  K.define('creek', {
    size: [30, 2, 40],
    options: { length: 40, width: 30, bed: 9, bank: 1.8, water: 'shallow' },
    note: 'A Hill Country creek running along z: flat limestone bedrock with stepped ledges and potholes, gravel bars, slabs, grassy banks that rise 1 to 2.5 m and sink back into TXT.ground at the sides. water: dry, shallow (clear pools over the rock) or full. Built above grade, since nothing can be cut into the ground plane.',
    make(o, r) {
      o = Object.assign({ length: 40, width: 30, bed: 9, bank: 1.8, water: 'shallow' }, o);
      const g = new THREE.Group(), L = o.length, W = o.width, B = o.bed, seed = 7000 + o.seed * 7;
      const nM = noise2(seed), nR = noise2(seed + 1), nS = noise2(seed + 2);
      const cx = (z) => (nM(z / 18 + 3, 1) - 0.5) * B * 0.9;                // the meander
      const hw = (z) => B / 2 * (0.8 + 0.4 * nM(z / 9, 7));                   // half width of the bed
      // the bed: flat rock shelves that step down along the flow, with potholes
      const bedAt = (x, z) => {
        const s = Math.abs(x - cx(z)), H = hw(z);
        let rock = 0.28 + Math.floor((z / L + 0.5) * 3 + nR(x * 0.08, z * 0.05) * 0.8) * 0.1;   // ledges across the channel
        rock += (fbm(nR, x * 0.3, z * 0.3, 3) - 0.5) * 0.1;
        rock -= smooth(0.68, 0.82, nS(x * 0.35, z * 0.35)) * 0.16;                           // potholes
        const bank = o.bank * (0.8 + 0.5 * nM(z / 12 + 20, 3));
        const t = (s - H) / 3.2;                                                                  // the bank face
        let y = t <= 0 ? rock + smooth(-0.35, 0, t) * 0.08 : lerp(rock, bank, smooth(0, 1, t));
        if (t > 0.6) { const e = (W / 2 - Math.abs(x)) / (W / 2 - H - 3.2 * 0.6 - Math.abs(cx(z)) + 0.01);
          y = lerp(-0.25, y, smooth(0, 0.7, clamp(e, 0, 1))); }
        y += t > 0.3 ? (fbm(nS, x * 0.2, z * 0.2, 3) - 0.5) * 0.35 : 0;
        return y;
      };
      const geo = heightfield(W, L, Math.round(W * 4), Math.round(L * 4), bedAt);
      const P = geo.attributes.position, N = geo.attributes.normal, C = new Float32Array(P.count * 3);
      const cRock = col(0xe4dccb), cRockD = col(0xc8bfac), cGrav = col(0xcfc8b8), cBankRock = col(0xd6cdb8), cGrass = col(0x7f7a45), cGrass2 = col(0x9a8f58), cEdge = col(0x857d4c), cMud = col(0x7a6a52), tmp = new THREE.Color();
      const levelW = o.water === 'full' ? 0.62 : o.water === 'shallow' ? 0.42 : -1;
      for (let i = 0; i < P.count; i++) {
        const x = P.getX(i), z = P.getZ(i), y = P.getY(i), slope = 1 - N.getY(i), s = Math.abs(x - cx(z)), H = hw(z);
        const t = (s - H) / 3.2;
        mix3(tmp, cRock, cRockD, fbm(nR, x * 0.5, z * 0.5, 3));
        if (t > -0.25) mix3(tmp, tmp, cGrav, smooth(-0.25, 0.1, t) * 0.8);
        if (t > 0.1) { mix3(tmp, cGrass, cGrass2, fbm(nS, x * 0.3, z * 0.3, 2)); mix3(tmp, tmp, cBankRock, smooth(0.25, 0.5, slope)); mix3(tmp, tmp, cGrav, 1 - smooth(0.1, 0.35, t)); }
        if (levelW > 0 && y < levelW + 0.04 && y > levelW - 0.12) mix3(tmp, tmp, cMud, 0.35);   // the wet line
        if (Math.abs(x) > W / 2 - 3) mix3(tmp, tmp, cEdge, smooth(W / 2 - 3, W / 2, Math.abs(x)));
        C[i * 3] = tmp.r; C[i * 3 + 1] = tmp.g; C[i * 3 + 2] = tmp.b;
      }
      geo.setAttribute('color', new THREE.BufferAttribute(C, 3));
      const uv = geo.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * W / 2.5, uv.getY(i) * L / 2.5);
      const bm = new THREE.Mesh(geo, M('creek-bed', { color: 0xffffff, vertexColors: true, map: limeTex(), roughness: 0.88 }));
      bm.userData.txGround = true; g.add(bm);
      // limestone slabs and ledge blocks, laid flat, a few tipped
      const lm = M('creek-slab', { color: 0xffffff, roughness: 0.86, map: limeTex() });
      const sg = (() => { const b = new THREE.BoxGeometry(1, 1, 1, 4, 1, 4), p = b.attributes.position, n = noise2(seed + 9);
        for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i), z = p.getZ(i), k = 0.8 + n(x * 3 + 5, z * 3 + 5) * 0.4; p.setXYZ(i, x * k, y, z * k); }
        const q = b.toNonIndexed(); q.computeVertexNormals(); return K.uvBox(q, 1); })();
      const slabs = [], sc = [];
      for (let i = 0; i < 70; i++) {
        const z = (r() - 0.5) * L * 0.95, side = r() < 0.6 ? (r() - 0.5) * 2 * hw(z) : (r() < 0.5 ? -1 : 1) * (hw(z) + r() * 1.6);
        const x = cx(z) + side, w = 0.6 + r() * 2.2, t = 0.12 + r() * 0.3;
        slabs.push({ x, y: bedAt(x, z) - t * 0.35, z, ry: r() * TAU, rx: (r() - 0.5) * 0.25, rz: (r() - 0.5) * 0.25, sx: w, sy: t, sz: w * (0.5 + r() * 0.6) });
        sc.push(new THREE.Color().setScalar(0.8 + r() * 0.3));
      }
      g.add(instanced(sg, lm, slabs, sc));
      // gravel bars on the inside of the bends, cobbles under the water
      const gr = [];
      for (let i = 0; i < 2200; i++) {
        const z = (r() - 0.5) * L, H = hw(z), s = (r() < 0.5 ? -1 : 1) * (H * (0.55 + r() * 0.6)), x = cx(z) + s;
        gr.push([x, bedAt(x, z) - 0.015, z, 0.02 + Math.pow(r(), 3.5) * 0.12]);
      }
      stones(r, gr, 'creek', [0xd8d4ca, 0xc2bdb1, 0xe6e2d8, 0xaca699, 0xcfc8b6], g);
      // bank grass: tall along the top, thinning at the edge
      const tf = [];
      for (let i = 0; i < W * L * 1.8; i++) {
        const x = (r() - 0.5) * W, z = (r() - 0.5) * L, s = Math.abs(x - cx(z)), t = (s - hw(z)) / 3.2;
        if (t < 0.35) continue;
        const e = (W / 2 - Math.abs(x)) / 3; if (r() > clamp(e, 0.1, 1)) continue;
        tf.push([x, bedAt(x, z) - 0.03, z, 0.7 + r() * 0.7]);
      }
      tuftField(r, tf, { key: 'bank', blades: 16, height: 0.6, spread: 0.15, width: 0.011, lean: 0.35, colors: [0x4f5231, 0x8a8a4e, 0xbcae78] }, g);
      if (levelW > 0) {
        // water only over the channel: a sheet following the meander (as wide as the model, alpha 0 on the banks)
        g.add(waterSheet(W - 1, L - 0.5, Math.round(W * 1.5), Math.round(L * 1.5), levelW, bedAt, 0x1d3a34, 0x5f7a6a, 'creek'));
      }
      g.userData.heightAt = bedAt;
      return g;
    },
  });

  /* ======================================================================================
   * reservoir_shore: a Texas lake shore, water toward +z, land rising behind
   * ====================================================================================== */
  K.define('reservoir_shore', {
    size: [300, 4, 260],
    options: { width: 300, water: 200, land: 60, bluff: 3.5, drawdown: 1.2, ramp: true },
    note: 'A reservoir shore: land at -z rising to a low bluff and sinking back into TXT.ground, a pale drawdown band of cracked mud and rock (the bathtub ring of a Texas lake in drought), and a wide reflective water plane toward +z with waves. ramp adds a grooved concrete boat ramp with curbs running into the water. The water surface stands at y = 0.35.',
    make(o, r) {
      o = Object.assign({ width: 300, water: 200, land: 60, bluff: 3.5, drawdown: 1.2, ramp: true }, o);
      const g = new THREE.Group(), W = o.width, D = o.land, seed = 8000 + o.seed * 11, level = 0.35;
      const nA = noise2(seed), nB = noise2(seed + 1);
      const shore = (x) => (fbm(nA, x / 40, 3, 3) - 0.5) * 22 + (nA(x / 9, 8) - 0.5) * 4;     // z of the waterline
      const rampX = W * 0.08;
      const hAt = (x, z) => {
        const zs = shore(x), u = zs - z;                                    // metres inland of the waterline
        let y;
        if (u < 0) y = level - Math.min(0.33, -u * 0.03);                   // lake bed, gently down
        else {
          const dd = o.drawdown * 6;                                        // the exposed band
          y = level + (u < dd ? u * (o.drawdown / dd) * 0.8 : o.drawdown * 0.8 + (o.bluff - o.drawdown * 0.8) * smooth(dd, dd + 14, u));
          y += smooth(dd, dd + 6, u) * (fbm(nB, x / 14, z / 14, 3) - 0.5) * 1.4;
          const back = D + zs - 8;                                          // falls to ground at the back edge
          y = lerp(y, -0.3, smooth(back - 22, back, u));
        }
        const e = (W / 2 - Math.abs(x)) / 25;                              // and at the ends
        if (u > 0) y = lerp(Math.min(y, level + 0.2), y, smooth(0, 1, e));
        if (o.ramp && Math.abs(x - rampX) < 5) { const rz = z; if (rz > zs - 10 && rz < zs + 14) y = Math.min(y, Math.max(y - 0.1, level + (zs - rz) * 0.13)); }
        return y;
      };
      const z0 = -D, z1 = 30;
      const geo = heightfield(W, z1 - z0, Math.round(W / 1.25), Math.round((z1 - z0) / 0.8), (x, z) => hAt(x, z));
      geo.translate(0, 0, (z0 + z1) / 2);
      // the heightfield was sampled around z = 0; resample at the translated positions
      const P = geo.attributes.position; for (let i = 0; i < P.count; i++) P.setY(i, hAt(P.getX(i), P.getZ(i)));
      geo.computeVertexNormals();
      const N = geo.attributes.normal, C = new Float32Array(P.count * 3), tmp = new THREE.Color();
      const cBed = col(0x6f6553), cMud = col(0xd3c9b2), cCrack = col(0xbdb39c), cRock = col(0xc7bfae), cGrass = col(0x827c46), cGrass2 = col(0x9b9157), cEdge = col(0x857d4c), cWet = col(0x6b5d48);
      for (let i = 0; i < P.count; i++) {
        const x = P.getX(i), z = P.getZ(i), y = P.getY(i), u = shore(x) - z, sl = 1 - N.getY(i);
        if (u < 0) tmp.copy(cBed);
        else if (u < o.drawdown * 6 + 2) { mix3(tmp, cMud, cCrack, nB(x * 0.8, z * 0.8)); mix3(tmp, cWet, tmp, smooth(0, 1.2, u)); mix3(tmp, tmp, cRock, smooth(0.5, 0.8, nA(x * 0.2, z * 0.2)) * 0.6); }
        else { mix3(tmp, cGrass, cGrass2, fbm(nA, x / 20, z / 20, 3)); mix3(tmp, tmp, cRock, smooth(0.15, 0.4, sl) * 0.8); mix3(tmp, cMud, tmp, smooth(o.drawdown * 6 + 2, o.drawdown * 6 + 5, u)); }
        if (y < 0.05 && u > 0) mix3(tmp, tmp, cEdge, 0.8);
        C[i * 3] = tmp.r; C[i * 3 + 1] = tmp.g; C[i * 3 + 2] = tmp.b;
      }
      geo.setAttribute('color', new THREE.BufferAttribute(C, 3));
      const uv = geo.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * W / 4, uv.getY(i) * (z1 - z0) / 4);
      const land = new THREE.Mesh(geo, M('res-land', { color: 0xffffff, vertexColors: true, map: detailTex('grass'), roughness: 0.95 }));
      land.userData.txGround = true; g.add(land);
      // the water: a wide plane, alpha only where it thins over the drawdown
      const WD = o.water;
      g.add(waterSheet(W, WD + 25, Math.round(W / 2.5), Math.round((WD + 25) / 2.5), level, (x, z) => (z < 30 ? hAt(x, z) : level - 0.4), 0x3a5360, 0x8d8a70, 'res', 0, WD / 2 - 12.5 + 0));
      // rock riprap and cobbles along the drawdown band
      const rk = [];
      for (let i = 0; i < W * 5; i++) { const x = (r() - 0.5) * W * 0.95, u = r() * (o.drawdown * 6 + 3) - 1, z = shore(x) - u;
        if (o.ramp && Math.abs(x - rampX) < 6) continue; rk.push([x, hAt(x, z) - 0.03, z, 0.04 + Math.pow(r(), 3) * 0.35]); }
      stones(r, rk, 'shore', [0xc9c3b4, 0xb2ab9b, 0xdad4c6, 0x9d9687], g, true);
      // grass on the land above the band
      const tf = [];
      for (let i = 0; i < 3200; i++) { const x = (r() - 0.5) * W * 0.6 + (r() < 0.5 ? 0 : (r() - 0.5) * W * 0.4), z = -r() * D * 0.7, u = shore(x) - z;
        if (u < o.drawdown * 6 + 3 || hAt(x, z) < 0.1) continue; if (o.ramp && Math.abs(x - rampX) < 6 && u < 22) continue; tf.push([x, hAt(x, z) - 0.03, z, 0.6 + r() * 0.7]); }
      tuftField(r, tf, { key: 'shore', blades: 14, height: 0.5, spread: 0.14, width: 0.011, lean: 0.35, colors: [0x4f5231, 0x8a8a4e, 0xbcae78] }, g);
      if (o.ramp) {
        const zs = shore(rampX), rl = 24, rw = 4.6, top = hAt(rampX, zs - 10);
        const ang = Math.atan2(top - (level - 1.2), rl), conc = M('res-ramp', { color: 0xffffff, map: K.tex('concrete'), roughness: 0.85 });
        const rampG = new THREE.Group();
        const slab = box(rw, 0.25, rl, conc, 0, -0.25, 0, 0.03); rampG.add(slab);
        const grooves = []; for (let k = 0; k < rl / 0.3; k++) grooves.push({ x: 0, y: 0.002, z: -rl / 2 + 0.15 + k * 0.3 });
        rampG.add(instanced(new THREE.BoxGeometry(rw - 0.2, 0.012, 0.05), M('res-groove', { color: 0x6f6b64, roughness: 0.95 }), grooves));
        [-1, 1].forEach((sd) => rampG.add(box(0.25, 0.22, rl, conc, sd * (rw / 2 + 0.12), -0.05, 0, 0.03)));
        rampG.rotation.x = ang; rampG.position.set(rampX, (top + level - 1.2) / 2 + 0.03, zs - 10 + rl / 2);
        g.add(rampG);
        // a parking apron at the head and two courtesy dock posts
        const ap = box(12, 0.2, 7, conc, rampX, top - 0.15, zs - 10 - 3.5, 0.03); g.add(ap);
        const post = M('res-post', { color: 0x6b5b48, roughness: 0.85, map: K.tex('wood', { color: '#7a6248' }) });
        for (let k = 0; k < 3; k++) { K.cyl(0.13, 0.13, 2.6, post, rampX + rw / 2 + 1.1, level - 1, zs - 2 + k * 3.2, 12, g); }
        const dock = box(1.4, 0.12, 9, M('res-dock', { color: 0xffffff, map: K.tex('wood', { color: '#8a7358' }), roughness: 0.8 }), rampX + rw / 2 + 1.4, level + 0.45, zs + 1.2, 0, g);
      }
      g.userData.heightAt = hAt;
      return g;
    },
  });

  /* ---- plant parts ------------------------------------------------------------------------ */
  // a curved strap leaf: base at the origin, arching out along +x, `segs` segments, coloured
  function leafStrip(len, wid, arch, droop, segs, c0, c1) {
    const P = [], C = [], A = col(c0), B = col(c1), c = new THREE.Color();
    const pt = (t) => [len * t, arch * len * t * (1 - t * droop), 0];
    const wAt = (t) => wid * Math.sin(Math.PI * Math.min(1, 0.15 + t * 0.95)) * (1 - t * 0.3);
    for (let s = 0; s < segs; s++) {
      const t0 = s / segs, t1 = (s + 1) / segs, p0 = pt(t0), p1 = pt(t1), w0 = wAt(t0), w1 = s === segs - 1 ? 0.0005 : wAt(t1);
      const q = [[p0[0], p0[1], -w0], [p0[0], p0[1], w0], [p1[0], p1[1], -w1], [p1[0], p1[1], w1]];
      [[0, 2, 1], [1, 2, 3]].forEach((tri) => tri.forEach((k) => { const v = q[k]; P.push(v[0], v[1], v[2]); mix3(c, A, B, k < 2 ? t0 : t1); C.push(c.r, c.g, c.b); }));
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); g.setAttribute('color', new THREE.Float32BufferAttribute(C, 3));
    g.computeVertexNormals();
    const n = g.attributes.normal; for (let i = 0; i < n.count; i++) { const v = new THREE.Vector3(n.getX(i), Math.abs(n.getY(i)) + 0.6, n.getZ(i)).normalize(); n.setXYZ(i, v.x, v.y, v.z); }
    return g;
  }
  const place = (geo, x, y, z, ry, rz, s) => { geo.rotateZ(rz || 0); geo.rotateY(ry || 0); if (s) geo.scale(s, s, s); geo.translate(x, y, z); return geo; };
  function stem(h, r0, r1, c, seg) { const g = new THREE.CylinderGeometry(r1, r0, h, seg || 4, 1, true); g.translate(0, h / 2, 0); return paintGeo(g.toNonIndexed(), c); }
  function blob(rng, rad, c, detail) { const g = lump(Math.floor(rng() * 1e5), detail || 0, rad, rad * 0.85, rad, 0.5); return paintGeo(g, c); }

  // an open boll: four puffed locks, an octahedron pushed out on its faces (8 triangles)
  function boll(rng, s) {
    const g = new THREE.OctahedronGeometry(1, 0), p = g.attributes.position;
    for (let i = 0; i < p.count; i++) p.setXYZ(i, p.getX(i) * s * 1.05, p.getY(i) * s * 0.78, p.getZ(i) * s * 0.92);
    return smoothNormals(g);
  }
  // a puff of lint: two octahedra turned 45 degrees and merged, smoothed round (16 triangles)
  function puff(rng, s) {
    const a = boll(rng, s), b = boll(rng, s * 0.9); b.rotateY(Math.PI / 4); b.rotateX(0.5);
    return mergeGeos([a, b]);
  }
  function cottonPlant(rng, growth) {
    const parts = [], H = lerp(0.2, 0.95, clamp(growth / 0.8, 0, 1)) * (0.85 + rng() * 0.3);
    const open = growth >= 0.88;
    const stemC = open ? 0x4a3a2c : 0x5d6b38;
    parts.push(stem(H, 0.011, 0.005, stemC, 4));
    const branches = open ? 5 : Math.round(lerp(2, 6, clamp(growth / 0.8, 0, 1)));
    for (let b = 0; b < branches; b++) {
      const y = H * (0.18 + 0.72 * b / branches), a = b * 2.4 + rng() * 0.8, len = (H - y) * 0.55 + 0.1, th = 0.75 + rng() * 0.35;
      const br = stem(len, 0.006, 0.003, stemC, 3); br.rotateZ(-th); br.rotateY(a); br.translate(0, y, 0); parts.push(br);
      const at = (f) => [Math.cos(a) * Math.sin(th) * len * f, y + Math.cos(th) * len * f, -Math.sin(a) * Math.sin(th) * len * f];
      if (open) {
        [0.55, 1.0].forEach((f) => { const t = at(f), s = 0.03 + rng() * 0.012;
          parts.push(place(paintGeo(puff(rng, s), rng() < 0.15 ? 0xe6dccb : 0xf6f4ee), t[0], t[1] + s * 0.5, t[2], rng() * TAU));
          parts.push(place(paintGeo(new THREE.OctahedronGeometry(s * 0.6, 0), 0x3a2c20), t[0], t[1] - s * 0.1, t[2])); });
        if (rng() < 0.45) { const t = at(0.4), lf = leafStrip(0.06, 0.03, -0.3, 1, 2, 0x4a3524, 0x6b4c30); place(lf, t[0], t[1], t[2], rng() * TAU, -1.0); parts.push(lf); }
      } else {
        for (let k = 0; k < 2; k++) { const t = at(0.5 + k * 0.5), lf = leafStrip(0.1 + rng() * 0.04, 0.06, 0.25, 1.2, 2, 0x3b5527, 0x5b7a36); place(lf, t[0], t[1], t[2], rng() * TAU, 0.15 - rng() * 0.4); parts.push(lf); }
        if (growth > 0.6 && rng() < 0.45) { const t = at(0.8); parts.push(place(paintGeo(new THREE.OctahedronGeometry(0.022, 0), rng() < 0.6 ? 0xf1e7c2 : 0xd98ca8), t[0], t[1] + 0.03, t[2])); }
      }
    }
    if (!open) for (let k = 0; k < 4; k++) { const lf = leafStrip(0.1 + rng() * 0.04, 0.06, 0.3, 1.3, 2, 0x3b5527, 0x587733); place(lf, 0, H * (0.8 + rng() * 0.2), 0, rng() * TAU, -0.1); parts.push(lf); }
    else parts.push(place(paintGeo(puff(rng, 0.035), 0xf6f3ec), 0, H + 0.02, 0));
    return mergeGeos(parts);
  }
  function sorghumPlant(rng, growth) {
    const parts = [], H = lerp(0.3, 1.25, clamp(growth / 0.7, 0, 1)) * (0.9 + rng() * 0.2);
    const ripe = growth >= 0.85, headed = growth >= 0.6;
    parts.push(stem(H, 0.012, 0.008, ripe ? 0x7d7c46 : 0x587536, 5));
    for (let k = 0; k < 7; k++) {
      const y = H * (0.08 + 0.78 * k / 7), dry = ripe && k < 2;
      const lf = leafStrip(0.5 + rng() * 0.2 - k * 0.03, 0.045, 0.7, 1.55, 3, dry ? 0x8f8055 : 0x3f5f29, dry ? 0xb4a16c : (ripe ? 0x7c8a46 : 0x68893c));
      place(lf, 0, y, 0, k * 2.4 + rng() * 0.7, 0.25 + rng() * 0.25); parts.push(lf);
    }
    if (headed) {
      const hc = ripe ? [0x7c3822, 0x8f4526, 0x6e3220, 0x9a5230][Math.floor(rng() * 4)] : 0x8fa05a;
      const hd = lump(Math.floor(rng() * 1e5), 1, 0.042, 0.11, 0.042, 0.7); hd.translate(0, 0.1, 0);
      parts.push(place(paintGeo(hd, hc), 0, H, 0, rng() * TAU, (rng() - 0.5) * 0.35));
    }
    return mergeGeos(parts);
  }

  /* ======================================================================================
   * crop_rows: a field block of cotton or sorghum on bedded rows
   * ====================================================================================== */
  K.define('crop_rows', {
    size: [20, 1.4, 30],
    options: { crop: 'cotton', growth: 1, width: 20, length: 30, row: 1.02, soil: 0x8a5d40 },
    note: 'A field block of bedded rows running along z, 40 inch rows on South Plains red soil. crop: cotton (growth 0.3 young, 0.7 green with flowers, 1 defoliated with open white bolls) or sorghum (growth 1 ripe rust heads). The block edge feathers into TXT.ground over a turn row.',
    make(o, r) {
      o = Object.assign({ crop: 'cotton', growth: 1, width: 20, length: 30, row: 1.02, soil: 0x8a5d40 }, o);
      const g = new THREE.Group(), W = o.width, L = o.length, sp = o.row, seed = 9000 + o.seed * 3;
      const nS = noise2(seed), rows = Math.floor(W / sp), x0 = -(rows - 1) * sp / 2;
      const bedAt = (x, z) => {
        const u = (x - x0) / sp, f = u - Math.round(u);
        let y = 0.05 + 0.09 * Math.pow(Math.cos(Math.PI * f), 2);
        y += (nS(x * 1.2, z * 1.2) - 0.5) * 0.03;
        const e = Math.min(W / 2 + 0.8 - Math.abs(x), L / 2 + 0.8 - Math.abs(z));
        return lerp(-0.04, y, smooth(0, 1.2, e));
      };
      const geo = heightfield(W + 2, L + 2, Math.round((W + 2) * 6), Math.round((L + 2) * 1.6), bedAt);
      const P = geo.attributes.position, C = new Float32Array(P.count * 3), cs = col(o.soil), cd = col(o.soil).multiplyScalar(0.72), ce = col(0x857d4c), tmp = new THREE.Color();
      for (let i = 0; i < P.count; i++) {
        const x = P.getX(i), z = P.getZ(i), y = P.getY(i);
        mix3(tmp, cd, cs, smooth(0.05, 0.13, y)); tmp.multiplyScalar(0.9 + fbm(nS, x * 0.3, z * 0.3, 2) * 0.2);
        const e = Math.min(W / 2 + 1 - Math.abs(x), L / 2 + 1 - Math.abs(z)); mix3(tmp, ce, tmp, smooth(0, 1, e));
        C[i * 3] = tmp.r; C[i * 3 + 1] = tmp.g; C[i * 3 + 2] = tmp.b;
      }
      geo.setAttribute('color', new THREE.BufferAttribute(C, 3));
      const uv = geo.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * (W + 2) / 2, uv.getY(i) * (L + 2) / 2);
      const soil = new THREE.Mesh(geo, M('crop-soil', { color: 0xffffff, vertexColors: true, map: detailTex('soil'), roughness: 0.96 }));
      soil.userData.txGround = true; g.add(soil);
      // the plants: a few variants, instanced down every row, with gaps where a seed failed
      const variants = [], VN = 4, step = o.crop === 'sorghum' ? 0.2 : 0.33;
      for (let v = 0; v < VN; v++) variants.push({ geo: o.crop === 'sorghum' ? sorghumPlant(r, o.growth) : cottonPlant(r, o.growth), list: [], cols: [] });
      for (let k = 0; k < rows; k++) {
        const x = x0 + k * sp;
        for (let z = -L / 2 + 0.3; z < L / 2 - 0.2; z += step * (0.8 + r() * 0.4)) {
          if (r() < 0.04) continue;
          const V = variants[Math.floor(r() * VN)], s = 0.85 + r() * 0.3 * (0.6 + 0.4 * nS(x * 0.2 + 9, z * 0.2));
          V.list.push({ x: x + (r() - 0.5) * 0.06, y: bedAt(x, z) - 0.02, z, ry: r() * TAU, s, sy: s * (0.9 + r() * 0.2) });
          V.cols.push(new THREE.Color().setScalar(0.85 + r() * 0.25));
        }
      }
      const pm = foliageMat('crop', { roughness: 0.85 });
      variants.forEach((V) => { const im = instanced(V.geo, pm, V.list, V.cols); g.add(im); });
      return g;
    },
  });

  /* ======================================================================================
   * pasture: tall mixed grass, dense, with bluebonnet and paintbrush drifts
   * ====================================================================================== */
  const PASTURE = {
    spring: { tufts: [[0x3f4a26, 0x6f7f3a, 0x9aa55a], [0x44502a, 0x7a8743, 0xa6ad66], [0x4a4a2a, 0x8b8a4d, 0xbcb07a]] },
    summer: { tufts: [[0x4d4a2c, 0x9b8f58, 0xcdbb84], [0x534c2e, 0xa89a62, 0xd8c690], [0x44472a, 0x7f7c47, 0xb3a472]] },
    fall:   { tufts: [[0x4a3a2a, 0x8a6a45, 0xb58a5a], [0x4d4a2c, 0x9b8f58, 0xcdbb84], [0x503a2c, 0x9a6448, 0xc08a62]] },
  };
  function flowerSpike(rng, kind) {
    // a raceme: stem, a tapering spike of florets, a few basal leaves
    const parts = [], H = kind === 'bluebonnet' ? 0.28 + rng() * 0.12 : 0.22 + rng() * 0.14;
    const n = 2 + Math.floor(rng() * 3);
    for (let s = 0; s < n; s++) {
      const a = rng() * TAU, lean = 0.15 + rng() * 0.2, h = H * (0.75 + rng() * 0.35), bx = Math.cos(a) * 0.04, bz = Math.sin(a) * 0.04;
      const st = stem(h * 0.55, 0.004, 0.003, 0x4f6a30, 3); st.rotateZ(lean * Math.cos(a)); st.rotateX(lean * Math.sin(a)); st.translate(bx, 0, bz); parts.push(st);
      const tx = bx + Math.sin(lean * Math.cos(a)) * -h * 0.55, tz = bz + Math.sin(lean * Math.sin(a)) * h * 0.55, ty = h * 0.53;
      const spikeH = h * 0.5, fl = kind === 'bluebonnet' ? [0x2d3f9a, 0x3a4fb4, 0x4a5cc4] : [0xd8431e, 0xe2582a, 0xc93a1c];
      const prof = kind === 'bluebonnet' ? [[0, 0], [0.022, 0.02], [0.026, 0.15], [0.025, 0.32], [0.022, 0.5], [0.017, 0.68], [0.011, 0.84], [0.004, 0.96], [0, 1]] : [[0, 0], [0.016, 0.05], [0.028, 0.3], [0.032, 0.55], [0.026, 0.8], [0.012, 0.95], [0, 1]];
      const lg = new THREE.LatheGeometry(prof.map((p) => new THREE.Vector2(p[0], p[1] * spikeH)), 8).toNonIndexed();
      const p = lg.attributes.position, cc = new Float32Array(p.count * 3), cA = col(fl[Math.floor(rng() * 3)]), cW = col(0xf4f2ea), cG = col(0x6f8a3a), c = new THREE.Color();
      const nf = noise2(Math.floor(rng() * 1e4));
      for (let i = 0; i < p.count; i++) {
        const t = p.getY(i) / spikeH, k = 1 + (nf(p.getX(i) * 160 + t * 40, p.getZ(i) * 160 + t * 13) - 0.5) * 1.1;
        p.setX(i, p.getX(i) * k); p.setZ(i, p.getZ(i) * k);
        if (kind === 'bluebonnet') { mix3(c, cA, cW, smooth(0.72, 0.84, t)); if (t > 0.93) mix3(c, c, cG, 0.4); }
        else { mix3(c, cG, cA, smooth(0.0, 0.3, t)); }
        cc[i * 3] = c.r; cc[i * 3 + 1] = c.g; cc[i * 3 + 2] = c.b;
      }
      lg.setAttribute('color', new THREE.BufferAttribute(cc, 3)); lg.computeVertexNormals(); lg.translate(tx, ty, tz); parts.push(lg);
    }
    for (let k = 0; k < 5; k++) { const lf = leafStrip(0.07 + rng() * 0.04, 0.02, 0.25, 1.4, 2, 0x3d5a28, 0x5e7d38); place(lf, 0, 0.01, 0, rng() * TAU, -0.2); parts.push(lf); }
    return mergeGeos(parts);
  }
  K.define('pasture', {
    size: [24, 0.9, 24],
    options: { width: 24, depth: 24, height: 0.65, density: 1, flowers: 'none', season: 'summer', drift: 0.5 },
    note: 'A block of tall mixed prairie grass (bunchgrass tufts with seed stalks), dense and instanced, thinning at its edges so it melts into TXT.ground. flowers: none, bluebonnet, paintbrush or mixed, in drifts; season: spring, summer or fall. The replacement for sparse tufts.',
    make(o, r) {
      o = Object.assign({ width: 24, depth: 24, height: 0.65, density: 1, flowers: 'none', season: 'summer', drift: 0.5 }, o);
      const g = new THREE.Group(), W = o.width, D = o.depth, seed = 9500 + o.seed * 19;
      const nD = noise2(seed), nF = noise2(seed + 1);
      const pal = (PASTURE[o.season] || PASTURE.summer).tufts;
      const flow = o.flowers !== 'none';
      const edgeK = (x, z) => smooth(0, Math.min(W, D) * 0.18, Math.min(W / 2 - Math.abs(x), D / 2 - Math.abs(z)));
      const count = Math.round(W * D * 5.2 * o.density);
      const groups = pal.map((c, i) => ({ geo: tuftGeo(r, { blades: 18, height: o.height * (i === 2 ? 1.15 : 1), spread: 0.16, width: 0.01, lean: 0.38, colors: c }), list: [], cols: [] }));
      // seed stalks: a few tall stems with a head, for the texture a real prairie has against the sky
      const stalk = (() => { const parts = []; for (let k = 0; k < 5; k++) { const h = o.height * (1.2 + r() * 0.5), a = r() * TAU, l = 0.08 + r() * 0.1;
        const st = stem(h, 0.003, 0.002, 0x8a7d50, 3); st.rotateZ(l * Math.cos(a)); st.rotateX(l * Math.sin(a)); parts.push(st);
        const hd = paintGeo(new THREE.CylinderGeometry(0.004, 0.009, 0.12, 4, 1).toNonIndexed(), 0xb8a676); hd.translate(0, h + 0.03, 0); hd.rotateZ(l * Math.cos(a)); hd.rotateX(l * Math.sin(a)); parts.push(hd); }
        return mergeGeos(parts); })();
      const stalks = [], stC = [];
      for (let i = 0; i < count; i++) {
        const x = (r() - 0.5) * W, z = (r() - 0.5) * D, e = edgeK(x, z);
        if (r() > e * 0.85 + 0.15) continue;
        const bloom = flow ? smooth(0.5 - o.drift * 0.2, 0.62, nF(x / 4, z / 4)) : 0;
        if (bloom > 0.5 && r() < 0.55) continue;                      // flowers crowd the grass out
        const G = groups[Math.floor(clamp(nD(x / 6, z / 6) * 3 + (r() - 0.5), 0, 2.999))];
        const s = (0.55 + e * 0.5) * (0.8 + r() * 0.4);
        G.list.push({ x, y: -0.02, z, ry: r() * TAU, s, sy: s * (0.85 + r() * 0.35) });
        G.cols.push(new THREE.Color().setScalar(0.82 + r() * 0.3));
        if (r() < 0.12) { stalks.push({ x, y: 0, z, ry: r() * TAU, s: s * 0.9 }); stC.push(new THREE.Color().setScalar(0.85 + r() * 0.3)); }
      }
      const gm = foliageMat('pasture');
      groups.forEach((G) => { const im = instanced(G.geo, gm, G.list, G.cols); im.castShadow = false; g.add(im); });
      if (stalks.length) g.add(instanced(stalk, gm, stalks, stC));
      if (flow) {
        const kinds = o.flowers === 'mixed' ? ['bluebonnet', 'bluebonnet', 'paintbrush'] : [o.flowers];
        const fv = []; kinds.forEach((k) => { for (let v = 0; v < 3; v++) fv.push({ kind: k, geo: flowerSpike(r, k), list: [], cols: [] }); });
        const nFl = Math.round(W * D * 3.4 * o.density);
        for (let i = 0; i < nFl; i++) {
          const x = (r() - 0.5) * W, z = (r() - 0.5) * D, e = edgeK(x, z), b = smooth(0.46 - o.drift * 0.2, 0.64, nF(x / 4, z / 4));
          if (r() > b * (0.3 + 0.7 * e)) continue;
          let V = fv[Math.floor(r() * fv.length)];
          if (o.flowers === 'mixed') { const pb = nF(x / 2.5 + 40, z / 2.5) > 0.6; V = fv[(pb ? 6 : 0) + Math.floor(r() * 3) % (pb ? 3 : 6)] || V; }
          const s = 0.8 + r() * 0.5;
          V.list.push({ x, y: -0.01, z, ry: r() * TAU, s }); V.cols.push(new THREE.Color().setScalar(0.85 + r() * 0.3));
        }
        const fm = foliageMat('flower', { roughness: 0.75 });
        fv.forEach((V) => { if (V.list.length) g.add(instanced(V.geo, fm, V.list, V.cols)); });
      }
      return g;
    },
  });

  /* ======================================================================================
   * grain_elevator: a Panhandle concrete slip form elevator with its headhouse
   * ====================================================================================== */
  K.define('grain_elevator', {
    size: [46, 58, 22],
    options: { bins: 5, rows: 2, height: 36, diameter: 7.3, headhouse: true, steelBins: 2, shed: true },
    note: 'A concrete slip form country elevator as on the Panhandle horizon: a double row of cylindrical bins with their interstices, a tall headhouse over the leg with small framed windows, a corrugated gallery along the bin tops, a caged ladder, a truck driveway shed with the dump, and corrugated steel bins with cone roofs beside it. Pale concrete with lift lines and rain streaks. Front (+z) is the driveway side.',
    make(o, r) {
      o = Object.assign({ bins: 5, rows: 2, height: 36, diameter: 7.3, headhouse: true, steelBins: 2, shed: true }, o);
      const g = new THREE.Group(), n = o.bins, rows = o.rows, H = o.height * (0.95 + r() * 0.1), Dm = o.diameter, R = Dm / 2, wall = 0.2;
      const tint = ['#d9d6ce', '#d2cdc2', '#dcd8cf', '#c9c3b7'][Math.floor(r() * 4)];
      const cm = M('ge-conc' + tint, { color: tint, roughness: 0.9, map: slipformTex() });
      const len = n * Dm, x0 = -len / 2 + R;
      const binParts = [];
      const cylUV = (geo, rad, h) => { const uv = geo.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * TAU * rad / 6, uv.getY(i) * h / 6); return geo; };
      for (let j = 0; j < rows; j++) for (let i = 0; i < n; i++) {
        const c = new THREE.Mesh(cylUV(new THREE.CylinderGeometry(R, R, H, 48, 1, true), R, H), cm);
        c.position.set(x0 + i * Dm, H / 2, (j - (rows - 1) / 2) * Dm); binParts.push(c);
      }
      g.add(K.merge(binParts, cm));
      // bin roofs: a flat deck over the whole block, with its parapet and a hatch on each bin
      const deckW = len, deckD = rows * Dm;
      box(deckW, 0.35, deckD - Dm + 2 * R * 0.7, cm, 0, H - 0.35, 0, 0.02, g);
      const caps = []; for (let j = 0; j < rows; j++) for (let i = 0; i < n; i++) {
        const cap = new THREE.Mesh(new THREE.CylinderGeometry(R + 0.02, R + 0.02, 0.4, 48), cm); cap.position.set(x0 + i * Dm, H - 0.2, (j - (rows - 1) / 2) * Dm); caps.push(cap);
        const hatch = box(0.9, 0.3, 0.9, K.finish.steelPaint(0x6f7479), x0 + i * Dm + R * 0.4, H, (j - (rows - 1) / 2) * Dm - R * 0.3, 0.02); g.add(hatch);
      }
      g.add(K.merge(caps, cm));
      // gallery: a long corrugated box along the top carrying the belt, on a steel frame
      const corr = M('ge-corr', { color: 0xffffff, map: K.tex('corrugated', { color: '#b7bcbd' }), metalness: 0.55, roughness: 0.5 });
      const gal = new THREE.Mesh(K.uvBox(new THREE.BoxGeometry(len + 1, 2.8, 3.2), 1), corr); gal.position.set(0, H + 1.4, 0); g.add(gal);
      box(len + 1.4, 0.2, 3.6, K.finish.steelPaint(0x5b6064), 0, H + 2.8, 0, 0.02, g);
      const gw = []; for (let x = -len / 2 + 2; x < len / 2; x += 3) gw.push(box(0.9, 0.5, 0.05, K.finish.glass(0x2a3238), x, H + 1.6, 1.62));
      g.add(K.merge(gw, K.finish.glass(0x2a3238)));
      // railing along the deck edges
      const rail = K.finish.galvanized(), rp = [];
      [-1, 1].forEach((sd) => { const z = sd * (deckD / 2 - 0.4);
        rp.push(K.bar([-len / 2, H + 1.05, z], [len / 2, H + 1.05, z], 0.025, rail, 6)); rp.push(K.bar([-len / 2, H + 0.55, z], [len / 2, H + 0.55, z], 0.02, rail, 6));
        for (let x = -len / 2; x <= len / 2; x += 1.8) rp.push(K.bar([x, H, z], [x, H + 1.05, z], 0.022, rail, 6)); });
      g.add(K.merge(rp, rail));
      // the headhouse: a tall box over one end, with small framed windows and a cap
      if (o.headhouse) {
        const hw = Dm * 1.25, hd = deckD * 0.8, hh = H * 0.55, hx = len / 2 - Dm * 0.9, top = H + hh;
        const hm = new THREE.Mesh(K.uvBox(new THREE.BoxGeometry(hw, hh + 1, hd), 6), cm); hm.position.set(hx, H - 1 + (hh + 1) / 2, 0); g.add(hm);
        box(hw + 0.5, 0.6, hd + 0.5, cm, hx, top, 0, 0.05, g);
        box(hw * 0.5, 3.2, hd * 0.45, corr, hx - hw * 0.1, top + 0.6, 0, 0.02, g);            // the head pulley house
        const frame = M('ge-frame', { color: 0x3c3f41, metalness: 0.4, roughness: 0.6 }), glz = K.finish.glass(0x2d3a40), fr = [], gz = [];
        for (let y = H + 3; y < top - 2; y += 4.2) for (const fx of [-hw * 0.25, hw * 0.25]) {
          fr.push(box(1.1, 1.3, 0.12, frame, hx + fx, y, hd / 2 + 0.02)); gz.push(box(0.9, 1.1, 0.06, glz, hx + fx, y + 0.1, hd / 2 + 0.07));
          fr.push(box(1.2, 0.1, 0.25, cm, hx + fx, y - 0.1, hd / 2 + 0.1));                          // sill
        }
        g.add(K.merge(fr, frame)); g.add(K.merge(gz, glz));
        // the load out spout: a steel pipe falling from the headhouse to the track side
        const spout = K.finish.steelPaint(0x7e8286);
        g.add(TXT.tube([[hx + hw / 2, top - 4, 1], [hx + hw / 2 + 3, top - 10, 2.5], [hx + hw / 2 + 5.5, 6.5, 4]], 0.28, spout, { segments: 40, radial: 12 }));
        // an antenna mast and a beacon
        g.add(K.bar([hx + hw * 0.3, top + 0.6, -hd * 0.3], [hx + hw * 0.3, top + 7, -hd * 0.3], 0.05, rail, 6));
      }
      // caged ladder up the front of the end bin
      const lx = -len / 2 + R, lz = deckD / 2 - Dm / 2 + R + 0.25, lad = [];
      [-0.22, 0.22].forEach((dx) => lad.push(K.bar([lx + dx, 0.4, lz], [lx + dx, H + 1, lz], 0.025, rail, 5)));
      for (let y = 0.6; y < H; y += 0.3) lad.push(K.bar([lx - 0.22, y, lz], [lx + 0.22, y, lz], 0.012, rail, 4));
      for (let y = 2.4; y < H; y += 1.2) { const hoop = new THREE.Mesh(new THREE.TorusGeometry(0.38, 0.015, 4, 16, Math.PI), rail); hoop.rotation.x = Math.PI / 2; hoop.rotation.z = Math.PI; hoop.position.set(lx, y, lz + 0.05); lad.push(hoop); }
      for (const a of [-0.6, 0, 0.6]) lad.push(K.bar([lx + Math.sin(a) * 0.38, 2.4, lz + Math.cos(a) * 0.38 + 0.05], [lx + Math.sin(a) * 0.38, H, lz + Math.cos(a) * 0.38 + 0.05], 0.012, rail, 4));
      g.add(K.merge(lad, rail));
      // the driveway shed: a steel frame lean to over the truck dump on the front
      if (o.shed) {
        const sx = -len * 0.1, sw = 9, sd = 7, sh = 6, frame = K.finish.steelPaint(0x6a6f72), sp = [];
        for (const dx of [-sw / 2, sw / 2]) for (const dz of [0.5, sd]) sp.push(box(0.3, sh, 0.3, frame, sx + dx, 0, deckD / 2 + dz));
        g.add(K.merge(sp, frame));
        const roof = new THREE.Mesh(K.uvBox(new THREE.BoxGeometry(sw + 1.2, 0.1, sd + 1), 1), corr);
        roof.position.set(sx, sh + 0.35, deckD / 2 + sd / 2 + 0.3); roof.rotation.x = -0.08; g.add(roof);
        box(sw - 0.5, 0.08, sd - 0.4, M('ge-grate', { color: 0x34373a, metalness: 0.6, roughness: 0.7 }), sx, 0.02, deckD / 2 + sd / 2 + 0.3, 0, g);  // the dump grate
        box(sw + 4, 0.15, sd + 6, concM(), sx, 0, deckD / 2 + sd / 2 + 1.5, 0.03, g);                              // the apron
        const dw = box(3.2, 4.2, 0.1, M('ge-door', { color: 0xffffff, map: K.tex('corrugated', { color: '#8f9496' }), metalness: 0.5, roughness: 0.55 }), sx, 0, deckD / 2 + 0.05, 0, g);
      }
      // corrugated steel bins with cone roofs, beside
      for (let k = 0; k < o.steelBins; k++) {
        const br = 5.5 + r() * 1.5, bh = 14 + r() * 4, bx = -len / 2 - br - 2.5 - k * (2 * br + 1.5), bz = (r() - 0.5) * 3;
        const sm = M('ge-steel', { color: 0xffffff, map: K.tex('corrugated', { color: '#c4c8c9' }), metalness: 0.7, roughness: 0.38 });
        const body = new THREE.Mesh(new THREE.CylinderGeometry(br, br, bh, 64, 1, true), sm);
        const uv = body.geometry.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getY(i) * bh * 1.3, uv.getX(i) * TAU * br / 8);  // ribs run round the bin
        body.position.set(bx, bh / 2, bz); g.add(body);
        const cone = new THREE.Mesh(new THREE.ConeGeometry(br + 0.3, br * 0.62, 64, 1, true), M('ge-roof', { color: 0xc9cdce, metalness: 0.75, roughness: 0.35 }));
        cone.position.set(bx, bh + br * 0.31, bz); g.add(cone);
        K.cyl(0.5, 0.6, 0.8, K.finish.steelPaint(0x9ca1a3), bx, bh + br * 0.6, bz, 16, g);
        K.cyl(br + 0.35, br + 0.35, 0.5, concM(), bx, 0, bz, 64, g);
        // stiffeners
        const st = []; for (let a = 0; a < 16; a++) { const t = a / 16 * TAU; st.push(box(0.12, bh, 0.08, sm, bx + Math.cos(t) * (br + 0.03), 0, bz + Math.sin(t) * (br + 0.03))); st[st.length - 1].rotation.y = -t; }
        g.add(K.merge(st, K.finish.galvanized()));
      }
      return g;
    },
  });
}
