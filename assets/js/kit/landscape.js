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
      const n = kind === 'juniper' ? 3600 : 2600;
      for (let i = 0; i < n; i++) {
        const a = r() * TAU, d = Math.pow(r(), 0.7) * N * 0.46 * (0.78 + 0.22 * Math.sin(a * 5 + 1.3)), px = N / 2 + Math.cos(a) * d, py = N / 2 + Math.sin(a) * d;
        const c = pal[Math.min(3, Math.floor(r() * 3 + (1 - py / N) * 1.4))], k = 0.8 + r() * 0.35;
        x.fillStyle = 'rgb(' + Math.round(c[0] * k) + ',' + Math.round(c[1] * k) + ',' + Math.round(c[2] * k) + ')';
        x.beginPath();
        if (kind === 'juniper') x.ellipse(px, py, 2.5 + r() * 3.5, 1.8 + r() * 2.5, r() * 3, 0, TAU);
        else x.ellipse(px, py, 3.5 + r() * 4.5, 2 + r() * 2.2, r() * 3, 0, TAU);
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
    const k = o.k || 0.62, c = lump(seed, o.detail || 0, o.rx * k, o.ry * k * 0.9, o.rz * k, 0.5); c.translate(0, o.cy, 0); parts.push(c);
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
    // flat: three grass fields mixed by noise; dry: sun cured patches; swale: the greener hollows;
    // thin: the grey, rock strewn soil of the slopes; duff: the dark litter under a brake or motte
    summer: { flat: [0x919266, 0x7d8456, 0xa39d70], dry: 0xb8a878, swale: 0x66703f, thin: 0x9a9380, duff: 0x55503c, brake: 0x5a5e44, rock: 0xbcb7aa },
    spring: { flat: [0x7a8a48, 0x6c7d40, 0x8e9656], dry: 0xa39c62, swale: 0x4f6630, thin: 0x8c866a, duff: 0x4a4632, brake: 0x3e4d2e, rock: 0xbdb6a4 },
    winter: { flat: [0xa89a74, 0x98906c, 0xb4a782], dry: 0xbfae84, swale: 0x7a7656, thin: 0x9c937a, duff: 0x55503c, brake: 0x46503a, rock: 0xc0b9a8 },
  };
  function hillHeight(o, seed) {
    const S = o.size, relief = o.relief, nA = noise2(seed), nB = noise2(seed + 1), nC = noise2(seed + 2);
    const lam = S * 0.32, step = o.step || Math.max(3, relief / 5.5), rim = clamp(o.rim != null ? o.rim : 0.42, 0.1, 0.9);
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
      /* THE RIM (2026-09-24, second pass). The hills used to rise out of TXT.ground over the outer
       * 15 % of the block and meet it along a hard, visible line. They now settle over `rim` of the
       * half width (42 % by default, 84 m on a 400 m block) through a double smoothstep, so the
       * foot of the last hill is a long gentle apron, and the colour goes to the ground's own. */
      const rr = Math.pow(Math.pow(Math.abs(x) / (S / 2), 4) + Math.pow(Math.abs(z) / (S / 2), 4), 0.25);
      const edge = 1 - rr + (nC(x / (S * 0.08) + 40, z / (S * 0.08) + 40) - 0.5) * 0.1;
      const m0 = smooth(0.0, rim, edge), m = m0 * m0 * (3 - 2 * m0);
      return { y: m * (y + 0.6) - (1 - m) * 0.12, m, step };
    };
  }
  /* The terrain's own grass map: short blades, straw and grey green, soil between, seen from above.
   * A multiplier on the vertex colour (its linear mean is stored so the rim can match TXT.ground). */
  function hillGrassTex() {
    const t = canvasTex('hct-grass2', 512, (x, N, r) => {
      const n1 = tileNoise(811, 8), n2 = tileNoise(813, 32);
      pixelPaint(x, N, (i, j) => { const u = i / N, v = j / N, k = 0.78 + (n1(u * 8, v * 8) - 0.5) * 0.06 + (n2(u * 32, v * 32) - 0.5) * 0.12;
        return [210 * k, 204 * k, 186 * k]; });
      for (let i = 0; i < 9000; i++) {                       // blades, clumped
        const cx = r() * N, cy = r() * N, a = r() * TAU, l = 3 + r() * 9, w = 0.8 + r() * 1.1, q = r();
        const c = q < 0.45 ? [236, 222, 176] : q < 0.8 ? [196, 204, 168] : q < 0.93 ? [150, 146, 118] : [96, 88, 72];
        const k = 0.85 + r() * 0.3;
        x.strokeStyle = 'rgba(' + Math.round(c[0] * k) + ',' + Math.round(c[1] * k) + ',' + Math.round(c[2] * k) + ',0.75)';
        x.lineWidth = w; x.beginPath(); x.moveTo(cx, cy); x.lineTo(cx + Math.cos(a) * l, cy + Math.sin(a) * l); x.stroke();
      }
      for (let i = 0; i < 260; i++) {                        // grit and small stones
        const cx = r() * N, cy = r() * N, s = 0.8 + r() * 2.2;
        x.fillStyle = r() < 0.5 ? 'rgba(236,230,214,0.8)' : 'rgba(70,62,50,0.55)'; x.beginPath(); x.ellipse(cx, cy, s, s * 0.7, r() * 3, 0, TAU); x.fill();
      }
    });
    if (t.userData.meanLin == null) {
      const c = t.image, d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data, lin = (v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
      let s = [0, 0, 0], n = 0;
      for (let i = 0; i < d.length; i += 64) { s[0] += lin(d[i]); s[1] += lin(d[i + 1]); s[2] += lin(d[i + 2]); n++; }
      t.userData.meanLin = s.map((v) => v / n);
    }
    return t;
  }
  /* ---- trees on the terrain: the kit's own live oak and Ashe juniper, in three levels of detail
   * (2026-09-24, second pass). The first pass drew every tree as a dozen leaf cards round a dark
   * core, and at any distance a reader could see it was a dark round blob. Trees now come from
   * kit/trees.js: a few seeded variants are grown ONCE per kit and cached, then instanced.
   *   L0  the whole tree, every cluster and all its wood (the nearest two or three);
   *   L1  its clusters thinned on a grid and each grown to cover its cell, the twigs dropped;
   *   L2  a camera facing billboard baked from the same tree (see bakeImpostor).
   * A triangle budget decides how far out each level reaches. Without kit/trees.js installed, the
   * old card crowns are drawn instead. */
  /* ---- far trees: billboards BAKED FROM THE KIT'S OWN TREE (2026-09-24, second pass). One
   * camera facing card, two triangles, carrying a picture of the very variant drawn near: the tree is
   * rendered once, unlit (albedo and its canopy occlusion only), side on and orthographic, by a
   * small offscreen renderer that is then released. Each card is lit by a normal pointing out
   * toward the viewer, so the scene's sun shades it as a volume. Four cheaper tries came
   * first and are recorded so nobody makes them again: leaf clusters thinned to a coarse grid
   * read as shredded flat cards, a smooth hull over the clusters read as a pillow, and a crown
   * painted in canvas blobs read as a sponge cut out of cardboard, and three fixed crossed cards
   * showed a dark slit wherever one card was edge on. */
  let BAKER = null;                                   // one context for every bake of a build
  function bakerDone() { if (BAKER) { BAKER.dispose(); if (BAKER.forceContextLoss) BAKER.forceContextLoss(); BAKER = null; } }
  function bakeImpostor(src, W, H, px) {
    const w = px, h = Math.max(64, Math.round(px * H / W / 32) * 32);
    try {
      if (!BAKER) BAKER = new THREE.WebGLRenderer({ canvas: document.createElement('canvas'), alpha: true, antialias: true, premultipliedAlpha: false, preserveDrawingBuffer: true });
      const ren = BAKER, cv = ren.domElement;
      ren.setPixelRatio(1); ren.setSize(w, h, false);
      ren.outputColorSpace = THREE.SRGBColorSpace; ren.toneMapping = THREE.NoToneMapping; ren.setClearColor(0x2a3320, 0);
      const sc = new THREE.Scene(), swap = [], basic = new Map();
      src.traverse((m) => { if (!m.isMesh) return; const s = m.material;
        if (!basic.has(s)) basic.set(s, new THREE.MeshBasicMaterial({ map: s.map || null, color: s.color ? s.color.clone() : 0xffffff, alphaTest: s.alphaTest || 0, side: s.side, vertexColors: !!s.vertexColors }));
        swap.push([m, s]); m.material = basic.get(s); });
      const par = src.parent; sc.add(src);
      const cam = new THREE.OrthographicCamera(-W / 2, W / 2, H, 0, -200, 200); cam.position.set(0, 0, 50); cam.lookAt(0, 0, 0);
      ren.render(sc, cam);
      sc.remove(src); if (par) par.add(src);
      swap.forEach(([m, s]) => { m.material = s; }); basic.forEach((b) => b.dispose());
      const out = document.createElement('canvas'); out.width = w; out.height = h; out.getContext('2d').drawImage(cv, 0, 0);
      const t = new THREE.CanvasTexture(out); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4;
      return t;
    } catch (e) { bakerDone(); return null; }
  }
  /* A billboard turns about its own vertical axis to face the camera, in the vertex shader, so no
   * card is ever seen edge on (three FIXED crossed cards were tried first: from any direction one
   * of them shows as a dark vertical slit through the crown). Its normal is a hemisphere facing the
   * viewer, so the sun still models it as a volume, and its shadow pass turns it to face the light,
   * so it casts the tree's whole silhouette. */
  const BBV = `
    vec4 bbBase = modelMatrix * instanceMatrix * vec4(0.0, 0.0, 0.0, 1.0);
    float bbSx = length((modelMatrix * instanceMatrix)[0].xyz), bbSy = length((modelMatrix * instanceMatrix)[1].xyz);
    vec3 bbRight = normalize(vec3(viewMatrix[0][0], 0.0, viewMatrix[2][0]) + vec3(1e-5, 0.0, 0.0));
    vec3 bbWorld = bbBase.xyz + bbRight * position.x * bbSx + vec3(0.0, position.y * bbSy, 0.0);
    vec4 mvPosition = viewMatrix * vec4(bbWorld, 1.0);
    gl_Position = projectionMatrix * mvPosition;`;
  function billboardify(m, withNormal) {
    m.onBeforeCompile = (sh) => {
      sh.vertexShader = sh.vertexShader.replace('#include <project_vertex>', BBV + (withNormal ? `
    vBBuv = vec2(position.x / bbHalfW, (position.y - bbCy) / (0.5 * bbH)); vBBright = bbRight;` : ''))
        .replace('void main() {', 'uniform float bbHalfW, bbCy, bbH;\n' + (withNormal ? 'varying vec2 vBBuv; varying vec3 vBBright;\n' : '') + 'void main() {');
      sh.uniforms.bbHalfW = { value: m.userData.bb[0] }; sh.uniforms.bbCy = { value: m.userData.bb[1] }; sh.uniforms.bbH = { value: m.userData.bb[2] };
      // the normal is a hemisphere facing the viewer, evaluated per pixel (per vertex it showed the card's diagonal)
      if (withNormal) sh.fragmentShader = sh.fragmentShader.replace('void main() {', 'varying vec2 vBBuv; varying vec3 vBBright;\nvoid main() {')
        .replace('#include <normal_fragment_begin>', THREE.ShaderChunk.normal_fragment_begin.replace('normal *= faceDirection;', '') + `
      {
        float bu = clamp(vBBuv.x, -1.0, 1.0), bv = vBBuv.y + 0.35;
        vec3 bR = normalize(vBBright), bF = normalize(cross(bR, vec3(0.0, 1.0, 0.0)));
        vec3 nW = normalize(bR * bu * 0.9 + vec3(0.0, bv, 0.0) + bF * sqrt(max(0.05, 1.0 - bu * bu)));
        normal = normalize((viewMatrix * vec4(nW, 0.0)).xyz);
      }`);
    };
    m.customProgramCacheKey = () => 'txbillboard' + (withNormal ? 'n' : 'd') + m.userData.bb.join(',');
    return m;
  }
  function impostorMat(key, tex, W, H, cy) {
    const m = M('hct-imp-' + key, { color: new THREE.Color(0.78, 0.8, 0.84), map: tex, alphaTest: 0.5, roughness: 0.9, side: THREE.DoubleSide });   // the unlit bake reads brighter than a lit, self shadowed crown
    if (!m.userData.bb) { m.userData.bb = [W / 2, H * cy, H]; billboardify(m, true); }
    if (!m.userData.depth) {
      const d = new THREE.MeshDepthMaterial({ map: tex, alphaTest: 0.5, side: THREE.DoubleSide, depthPacking: THREE.RGBADepthPacking });
      d.userData.bb = m.userData.bb; billboardify(d, false); m.userData.depth = d;
    }
    return m;
  }
  // one upright card of width W and height H standing on y = 0, turned to the camera by its material
  function impostorGeo(W, H) { const g = new THREE.PlaneGeometry(W, H); g.translate(0, H / 2, 0); return g; }
  const TREEKIT = new Map();
  function treeKit(name, seed, spec) {
    const key = name + '|' + seed;
    if (TREEKIT.has(key)) return TREEKIT.get(key);
    let src = null;
    try { if (K.registry[name]) src = K.make(name, { seed }); } catch (e) { src = null; }
    if (!src) { TREEKIT.set(key, null); return null; }
    src.updateMatrixWorld(true);
    const woods = [], fols = [];
    src.traverse((m) => { if (m.isInstancedMesh) fols.push(m); else if (m.isMesh) woods.push(m); });
    const I = new THREE.Matrix4();
    const triOf = (geo) => (geo.index ? geo.index.count : geo.attributes.position.count) / 3;
    // clusters: [matrix, colour, centre, size]
    const cl = [];
    fols.forEach((f) => { for (let i = 0; i < f.count; i++) { const Mx = new THREE.Matrix4(); f.getMatrixAt(i, Mx); Mx.premultiply(f.matrixWorld);
      const c = new THREE.Color(1, 1, 1); if (f.instanceColor) f.getColorAt(i, c);
      const p = new THREE.Vector3().setFromMatrixPosition(Mx), s = new THREE.Vector3().setFromMatrixScale(Mx);
      cl.push({ f, M: Mx, c, p, s: (s.x + s.z) / 2 }); } });
    const box = new THREE.Box3(); cl.forEach((c) => box.expandByPoint(c.p));
    const ctr = box.getCenter(new THREE.Vector3()), size = box.getSize(new THREE.Vector3());
    // wood thinned by the width of each triangle (area over longest edge): twigs go first
    function thinWood(minW) {
      return woods.map((w) => {
        const G = w.geometry, P = G.attributes.position, idx = G.index ? G.index.array : null, n = idx ? idx.length : P.count, keep = [];
        const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3(), e = new THREE.Vector3(), f2 = new THREE.Vector3();
        for (let t = 0; t < n; t += 3) {
          const i0 = idx ? idx[t] : t, i1 = idx ? idx[t + 1] : t + 1, i2 = idx ? idx[t + 2] : t + 2;
          a.fromBufferAttribute(P, i0); b.fromBufferAttribute(P, i1); c.fromBufferAttribute(P, i2);
          const area = e.subVectors(b, a).cross(f2.subVectors(c, a)).length() / 2, L = Math.max(a.distanceTo(b), b.distanceTo(c), c.distanceTo(a));
          if (area / Math.max(1e-6, L) > minW) keep.push(i0, i1, i2);
        }
        const g2 = new THREE.BufferGeometry(); Object.keys(G.attributes).forEach((k) => g2.setAttribute(k, G.attributes[k])); g2.setIndex(keep);
        return { geo: g2, mat: w.material, locals: [w.matrixWorld.clone()], cols: null };
      });
    }
    // clusters thinned on a grid of `cellM` metres, the outermost kept per cell and grown to cover it
    function thinFol(cellM, grow) {
      const bins = new Map();
      cl.forEach((c) => { const k = Math.floor(c.p.x / cellM) + ',' + Math.floor(c.p.y / cellM) + ',' + Math.floor(c.p.z / cellM), d = c.p.distanceTo(ctr), b = bins.get(k);
        if (!b || d > b.d) bins.set(k, { c, d }); });
      const byF = new Map();
      bins.forEach(({ c }) => { if (!byF.has(c.f)) byF.set(c.f, { locals: [], cols: [] }); const L = byF.get(c.f);
        const k = Math.max(1, (cellM * grow) / Math.max(0.2, c.s)); L.locals.push(c.M.clone().multiply(new THREE.Matrix4().makeScale(k, k, k))); L.cols.push(c.c); });
      return [...byF.entries()].map(([f, L]) => ({ geo: f.geometry, mat: f.material, locals: L.locals, cols: L.cols }));
    }
    const L0 = woods.map((w) => ({ geo: w.geometry, mat: w.material, locals: [w.matrixWorld.clone()], cols: null }))
      .concat(fols.map((f) => { const L = cl.filter((c) => c.f === f); return { geo: f.geometry, mat: f.material, locals: L.map((c) => c.M), cols: L.map((c) => c.c) }; }));
    const L1 = thinWood(spec.wood1).concat(thinFol(spec.cell1, 1.05));
    const sb = new THREE.Box3().setFromObject(src), W = Math.max(sb.max.x - sb.min.x, sb.max.z - sb.min.z) * 1.02, Ht = sb.max.y + 0.1;
    const tex = bakeImpostor(src, W, Ht, spec.px);
    const L2 = tex ? [{ geo: impostorGeo(W, Ht), mat: impostorMat(key, tex, W, Ht, spec.cy), locals: [I.clone()], cols: null, bb: true }] : L1;
    const cost = (L) => L.reduce((s, p) => s + triOf(p.geo) * p.locals.length, 0);
    const kit = { lods: [L0, L1, L2], cost: [cost(L0), cost(L1), cost(L2)], height: box.max.y, width: Math.max(size.x, size.z) };
    TREEKIT.set(key, kit);
    return kit;
  }
  const TREESPEC = {
    live_oak: { cell1: 1.7, wood1: 0.05, px: 512, cy: 0.62 },
    ashe_juniper: { cell1: 0.95, wood1: 0.035, px: 256, cy: 0.45 },
  };
  // Place trees: list of {sp, v, x, y, z, ry, sx, sy, sz, tint, d}; returns the triangles spent.
  function plantTrees(g, trees, budget) {
    const kits = {}, out = new Map();
    let fixed = 0;
    for (const sp of Object.keys(TREESPEC)) { kits[sp] = [1, 2, 3].map((v) => treeKit(sp, v, TREESPEC[sp])); if (kits[sp].some((k) => !k)) { bakerDone(); return -1; } }
    bakerDone();
    trees.sort((a, b) => a.d - b.d);
    let far = 0; trees.forEach((t) => { far += kits[t.sp][t.v].cost[2]; });
    // too many trees for the budget even far: thin the farthest half first, evenly
    let i = trees.length - 1; const rr = TXT.rng(trees.length * 17 + 3);
    for (let pass = 0; pass < 6 && far > budget * 0.9; pass++)
      for (i = trees.length - 1; i > trees.length * 0.2 && far > budget * 0.9; i--)
        if (!trees[i].drop && rr() < 0.5) { far -= kits[trees[i].sp][trees[i].v].cost[2]; trees[i].drop = true; }
    let spent = 0, n0 = 0;
    const Mp = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), s = new THREE.Vector3(), p = new THREE.Vector3();
    for (const t of trees) {
      if (t.drop) continue;
      const kit = kits[t.sp][t.v]; far -= kit.cost[2];
      let L = t.d < t.r0 && n0 < 2 ? 0 : t.d < t.r1 ? 1 : 2;
      while (L < 2 && spent + kit.cost[L] + far > budget) L++;
      if (L === 0) n0++;
      spent += kit.cost[L]; g.userData.treeStats = g.userData.treeStats || { lod: [0, 0, 0], cost: {} };
      g.userData.treeStats.lod[L]++; g.userData.treeStats.cost[t.sp] = kit.cost;
      e.set(0, t.ry, 0); q.setFromEuler(e); s.set(t.sx, t.sy, t.sz); p.set(t.x, t.y, t.z); Mp.compose(p, q, s);
      kit.lods[L].forEach((part) => {
        if (!out.has(part)) out.set(part, { part, M: [], C: [] });
        const O = out.get(part);
        part.locals.forEach((lm, j) => { O.M.push(Mp.clone().multiply(lm)); const c = part.cols ? part.cols[j].clone() : new THREE.Color(1, 1, 1); O.C.push(c.multiply(t.tint)); });
      });
    }
    out.forEach(({ part, M: Ms, C }) => {
      const im = new THREE.InstancedMesh(part.geo, part.mat, Ms.length);
      Ms.forEach((m, k) => im.setMatrixAt(k, m));
      if (part.cols || part.mat.vertexColors || true) C.forEach((c, k) => im.setColorAt(k, c));
      im.instanceMatrix.needsUpdate = true; if (im.instanceColor) im.instanceColor.needsUpdate = true;
      im.castShadow = true; im.receiveShadow = !part.bb; im.frustumCulled = false;
      if (part.bb) im.customDepthMaterial = part.mat.userData.depth;
      g.add(im);
    });
    return spent;
  }

  /* ---- limestone ledges along the contours (2026-09-24, second pass) ------------------------
   * The first pass laid pale boxes on the risers and they read as slabs floating on a lawn. A
   * Hill Country ledge is the edge of a bed of Glen Rose limestone: a thin, broken, grey band that
   * follows a contour where the slope steepens, its top a rough tread flush with the soil above,
   * its lip overhanging a shadowed undercut, its foot buried in the slope below, talus under it.
   * So the contours of the built mesh are traced (marching squares) at the level of each riser,
   * kept where the slope is steep, and a profile is swept along them. */
  function traceContours(Y, NV, cell, S, level, keep) {
    const segs = [], id = (t, i, j) => t * NV * NV + j * NV + i;
    const pt = (i0, j0, i1, j1) => { const a = Y[j0 * NV + i0] - level, b = Y[j1 * NV + i1] - level, t = a / (a - b);
      return [-S / 2 + (i0 + (i1 - i0) * t) * cell, -S / 2 + (j0 + (j1 - j0) * t) * cell]; };
    for (let j = 0; j < NV - 1; j++) for (let i = 0; i < NV - 1; i++) {
      const a = Y[j * NV + i] > level, b = Y[j * NV + i + 1] > level, c = Y[(j + 1) * NV + i + 1] > level, d = Y[(j + 1) * NV + i] > level;
      if (a === b && b === c && c === d) continue;
      if (!keep(i, j)) continue;
      const E = [];
      if (a !== b) E.push([id(0, i, j), pt(i, j, i + 1, j)]);
      if (b !== c) E.push([id(1, i + 1, j), pt(i + 1, j, i + 1, j + 1)]);
      if (d !== c) E.push([id(0, i, j + 1), pt(i, j + 1, i + 1, j + 1)]);
      if (a !== d) E.push([id(1, i, j), pt(i, j, i, j + 1)]);
      if (E.length === 2) segs.push([E[0], E[1]]);
      else if (E.length === 4) { segs.push([E[0], E[1]]); segs.push([E[2], E[3]]); }
    }
    // chain the segments through their shared edge crossings
    const at = new Map();
    segs.forEach((s, k) => s.forEach((e) => { if (!at.has(e[0])) at.set(e[0], []); at.get(e[0]).push(k); }));
    const used = new Uint8Array(segs.length), chains = [];
    for (let k0 = 0; k0 < segs.length; k0++) {
      if (used[k0]) continue;
      used[k0] = 1;
      const chain = [segs[k0][0], segs[k0][1]];
      for (const dir of [1, 0]) {
        let end = dir ? chain[chain.length - 1] : chain[0];
        for (;;) {
          const nx = (at.get(end[0]) || []).find((k) => !used[k]);
          if (nx == null) break;
          used[nx] = 1; const s = segs[nx], other = s[0][0] === end[0] ? s[1] : s[0];
          if (dir) chain.push(other); else chain.unshift(other);
          end = other;
        }
      }
      chains.push(chain.map((e) => e[1]));
    }
    return chains;
  }
  function resample(pts, stepM) {
    // one Chaikin pass, then even spacing
    let q = [pts[0]];
    for (let i = 0; i < pts.length - 1; i++) { const a = pts[i], b = pts[i + 1];
      q.push([a[0] * 0.75 + b[0] * 0.25, a[1] * 0.75 + b[1] * 0.25], [a[0] * 0.25 + b[0] * 0.75, a[1] * 0.25 + b[1] * 0.75]); }
    q.push(pts[pts.length - 1]);
    const out = [q[0]]; let acc = 0;
    for (let i = 1; i < q.length; i++) {
      let a = q[i - 1]; const b = q[i]; let L = Math.hypot(b[0] - a[0], b[1] - a[1]);
      while (acc + L >= stepM) { const t = (stepM - acc) / L; a = [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]; out.push(a); L -= stepM - acc; acc = 0; }
      acc += L;
    }
    return out;
  }

  K.define('hill_country_terrain', {
    size: [800, 60, 800],
    options: { size: 800, relief: 60, ledges: true, trees: 1, season: 'summer', segments: 0, ground: 0x6d7a3c, rim: 0.42, near: null, budget: 400000, rocks: 1 },
    note: 'Central Texas Hill Country: rolling stair-stepped limestone hills, thin broken limestone ledges along the contours with talus below, Ashe juniper brakes and live oak mottes (the kit\'s own trees.js models, three levels of detail), grass by slope and hollow with sun cured patches and rock strewn slopes. size 200 to 2000 m, relief in metres. The block settles into TXT.ground over `rim` of its half width and takes `ground` (that plane\'s colour) at its edge. `near` [x, z] in model space is where the viewer stands (default: the middle of the front edge); detail and rocks gather there. `budget` caps triangles. Middle ground and far distance; never call TXT.contact on it. userData.heightAt(x, z) seats things on it.',
    make(o, r) {
      o = Object.assign({ size: 800, relief: 60, ledges: true, trees: 1, season: 'summer', segments: 0, ground: 0x6d7a3c, rim: 0.42, near: null, budget: 400000, rocks: 1 }, o);
      o.size = clamp(o.size, 200, 2000);
      const S = o.size, g = new THREE.Group(), seed = 1000 + o.seed * 31;
      const Hf = hillHeight(o, seed);
      const seg = o.segments || Math.round(clamp(S / 3.6, 160, 220));
      const NV = seg + 1, cell = S / seg;
      const MK = new Float32Array(NV * NV);
      let vi = 0;
      const geo = heightfield(S, S, seg, seg, (x, z) => { const h = Hf(x, z); MK[vi++] = h.m; return h.y; });
      const P = geo.attributes.position, N = geo.attributes.normal, Y = new Float32Array(P.count);
      for (let i = 0; i < P.count; i++) Y[i] = P.getY(i);
      const near = o.near ? [o.near[0], o.near[1]] : [0, S / 2 * 0.92];
      const dNear = (x, z) => Math.hypot(x - near[0], z - near[1]);
      // the height of the MESH (its own two triangles per cell), so whatever sits on it sits exactly
      const hAt = (x, z) => {
        const fx = clamp((x + S / 2) / cell, 0, seg - 1e-6), fz = clamp((z + S / 2) / cell, 0, seg - 1e-6), ix = Math.floor(fx), iz = Math.floor(fz), tx = fx - ix, tz = fz - iz;
        const a = iz * NV + ix, d = a + 1, b = a + NV, c = b + 1;
        const y = tx + tz <= 1 ? Y[a] + (Y[d] - Y[a]) * tx + (Y[b] - Y[a]) * tz : Y[c] + (Y[b] - Y[c]) * (1 - tx) + (Y[d] - Y[c]) * (1 - tz);
        const m = (MK[a] * (1 - tx) + MK[d] * tx) * (1 - tz) + (MK[b] * (1 - tx) + MK[c] * tx) * tz;
        return { y, m };
      };
      const slopeAt = (x, z) => { const e = cell, a = hAt(x + e, z).y - hAt(x - e, z).y, b = hAt(x, z + e).y - hAt(x, z - e).y;
        return { s: Math.hypot(a, b) / (2 * e), gx: a / (2 * e), gz: b / (2 * e) }; };
      const nBr = noise2(seed + 8);
      const brakeAt = (x, z) => smooth(0.46, 0.66, fbm(nBr, x / 45 + 30, z / 45, 3));

      /* ---- tree placement first, so the ground under a motte or a brake can take its shade -- */
      const trees = [], shade = new Float32Array(P.count);
      const tint = (k) => new THREE.Color(0.9 + r() * 0.16, 0.9 + r() * 0.16, 0.88 + r() * 0.14).multiplyScalar(k);
      if (o.trees > 0) {
        const area = S * S, r0 = 32, r1 = o.detail || 280;
        const nJ = Math.round(Math.min(1800, area / 320) * o.trees), nO = Math.round(Math.min(110, area / 5200) * o.trees), nY = Math.round(Math.min(700, area / 900) * o.trees);
        const clear = (x, z) => dNear(x, z) < 7;   // never a tree on the viewer's own spot
        let tries = 0, cJ = 0;
        while (cJ < nJ && tries < nJ * 40) {                    // Ashe juniper: singly and in brakes
          tries++;
          const x = (r() - 0.5) * S, z = (r() - 0.5) * S, H = hAt(x, z);
          if (H.m < 0.25 || clear(x, z)) continue;
          const sl = slopeAt(x, z).s;
          if (sl > 0.6) continue;
          const p = 0.06 + brakeAt(x, z) * 0.95 + smooth(0.05, 0.3, sl) * 0.3;
          if (r() > p) continue;
          const h = 0.65 + r() * 0.55, w = h * (1.0 + r() * 0.5);
          trees.push({ sp: 'ashe_juniper', v: Math.floor(r() * 3), x, y: H.y - 0.12, z, ry: r() * TAU, sx: w, sy: h, sz: w * (0.85 + r() * 0.3), tint: tint(0.9 + r() * 0.2), d: dNear(x, z), r0, r1, R: 2.6 * w });
          cJ++;
        }
        tries = 0; let cY = 0;
        while (cY < nY && tries < nY * 20) {                    // young cedar and brush: the understory
          tries++;
          // brush is only worth drawing where it can be seen: within the detail radius of the viewer
          const d = Math.sqrt(r()) * r1, a = r() * TAU, x = near[0] + Math.cos(a) * d, z = near[1] + Math.sin(a) * d;
          if (Math.abs(x) > S / 2 || Math.abs(z) > S / 2 || clear(x, z)) continue;
          const H = hAt(x, z);
          if (H.m < 0.3 || slopeAt(x, z).s > 0.6) continue;
          if (r() > 0.25 + brakeAt(x, z) * 0.75) continue;
          const h = 0.2 + r() * 0.25;
          trees.push({ sp: 'ashe_juniper', v: Math.floor(r() * 3), x, y: H.y - 0.08, z, ry: r() * TAU, sx: h * (1 + r() * 0.5), sy: h, sz: h * (1 + r() * 0.5), tint: tint(0.95 + r() * 0.2), d: dNear(x, z), r0: 0, r1: 45, R: 0 });
          cY++;
        }
        tries = 0; let cO = 0;
        while (cO < nO && tries < nO * 60) {                    // live oak mottes: three to seven grown together
          tries++;
          const x = (r() - 0.5) * S * 0.9, z = (r() - 0.5) * S * 0.9, H = hAt(x, z);
          if (H.m < 0.3 || slopeAt(x, z).s > 0.16) continue;
          const n = 3 + Math.floor(r() * 5);
          for (let k = 0; k < n; k++) {
            const a = r() * TAU, rad = Math.sqrt(r()) * 9 * Math.sqrt(n / 4), xx = x + Math.cos(a) * rad, zz = z + Math.sin(a) * rad, hh = hAt(xx, zz);
            if (hh.m < 0.25 || clear(xx, zz)) continue;
            const w = 0.55 + r() * 0.4, h = w * (0.85 + r() * 0.3);
            trees.push({ sp: 'live_oak', v: Math.floor(r() * 3), x: xx, y: hh.y - 0.2, z: zz, ry: r() * TAU, sx: w, sy: h, sz: w * (0.85 + r() * 0.3), tint: tint(0.92 + r() * 0.16), d: dNear(xx, zz), r0, r1, R: 8.5 * w });
          }
          cO++;
        }
        // shade and litter under each crown, soft edged, on the vertex colours
        trees.forEach((t) => { if (!t.R) return;
          const i0 = Math.max(0, Math.floor((t.x - t.R + S / 2) / cell)), i1 = Math.min(seg, Math.ceil((t.x + t.R + S / 2) / cell));
          const j0 = Math.max(0, Math.floor((t.z - t.R + S / 2) / cell)), j1 = Math.min(seg, Math.ceil((t.z + t.R + S / 2) / cell));
          for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) { const x = -S / 2 + i * cell, z = -S / 2 + j * cell, d = Math.hypot(x - t.x, z - t.z) / t.R;
            if (d < 1) shade[j * NV + i] = Math.max(shade[j * NV + i], 1 - smooth(0.45, 1, d)); } });
      }

      /* ---- the ground's colour: grass mixed by noise, sun cured patches, green hollows, the thin
       * grey soil of the slopes, litter under the trees, and the rim melting into TXT.ground ---- */
      const C = new Float32Array(P.count * 3);
      const pal = SEASON[o.season] || SEASON.summer, flats = pal.flat.map(col), cDry = col(pal.dry), cSw = col(pal.swale), cTh = col(pal.thin),
        cDuff = col(pal.duff), cB = col(pal.brake), cR = col(pal.rock), nP = noise2(seed + 7), nQ = noise2(seed + 9), nD = noise2(seed + 11), tmp = new THREE.Color();
      const gtex = hillGrassTex(), ml = gtex.userData.meanLin;
      // TXT.ground's albedo is its colour times about 0.97; the terrain's is vertex times this map
      const cRim = col(o.ground); cRim.r *= 0.97 / ml[0]; cRim.g *= 0.97 / ml[1]; cRim.b *= 0.97 / ml[2];
      const k2 = Math.max(1, Math.round(6 / cell));
      for (let i = 0; i < P.count; i++) {
        const x = P.getX(i), z = P.getZ(i), y = Y[i], ny = N.getY(i), slope = 1 - ny, ix = i % NV, iz = (i - ix) / NV;
        const pn = fbm(nP, x / 60, z / 60, 3);
        mix3(tmp, flats[0], flats[1], smooth(0.3, 0.7, pn));
        mix3(tmp, tmp, flats[2], smooth(0.55, 0.8, fbm(nQ, x / 25, z / 25, 2)) * 0.6);
        // sun cured patches, larger on the crests
        const dry = smooth(0.52, 0.68, fbm(nD, x / 80, z / 80, 4) + 0.12 * smooth(0.4, 1, y / o.relief));
        mix3(tmp, tmp, cDry, dry * 0.75);
        // hollows and swales: where the ground sits below its neighbours, greener and darker
        const iA = Math.max(0, ix - k2), iB = Math.min(seg, ix + k2), jA = Math.max(0, iz - k2), jB = Math.min(seg, iz + k2);
        const cav = (Y[iz * NV + iA] + Y[iz * NV + iB] + Y[jA * NV + ix] + Y[jB * NV + ix]) / 4 - y;
        mix3(tmp, tmp, cSw, smooth(0.08, 0.7, cav) * 0.8);
        // thin, rock strewn soil on the slopes, grey with pale grit
        mix3(tmp, tmp, cTh, smooth(0.06, 0.24, slope) * 0.8);
        mix3(tmp, tmp, cR, smooth(0.3, 0.6, slope) * 0.5);
        mix3(tmp, tmp, cB, brakeAt(x, z) * 0.35 * (1 - dry));
        mix3(tmp, tmp, cDuff, shade[i] * 0.75);
        tmp.multiplyScalar(0.94 + 0.12 * smooth(0, o.relief, y));
        mix3(tmp, cRim, tmp, smooth(0.02, 0.8, MK[i]));
        C[i * 3] = tmp.r; C[i * 3 + 1] = tmp.g; C[i * 3 + 2] = tmp.b;
      }
      geo.setAttribute('color', new THREE.BufferAttribute(C, 3));
      const uv = geo.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * S / 6, uv.getY(i) * S / 6);
      const tm = M('hct-ground2', { color: 0xffffff, roughness: 0.97, vertexColors: true, map: gtex, envMapIntensity: 0.6 });
      const ground = new THREE.Mesh(geo, tm); ground.receiveShadow = true; ground.userData.txGround = true; g.add(ground);
      let spent = geo.index ? geo.index.count / 3 : P.count / 3;

      /* ---- ledges -------------------------------------------------------------------------- */
      const stoneSpots = [];
      if (o.ledges) {
        const H0 = hillHeight(Object.assign({}, o), seed)(0, 0).step;
        const levels = [];
        for (let k = 0; (k + 0.58) * H0 < o.relief * 1.2; k++) levels.push((k + 0.58) * H0 + 0.6, (k + 0.84) * H0 + 0.6);
        const keepCell = (i, j) => { const a = j * NV + i; if (MK[a] < 0.75) return false;
          const s = Math.hypot(Y[a + 1] - Y[a], Y[a + NV] - Y[a]) / cell; return s > 0.34; };
        const nL = noise2(seed + 21), Pp = [], Cc = [], Uu = [], Ix = [];
        const base = [col(0xa9a8a2), col(0x9a9993), col(0xb6b2a6), col(0x8f8e88)], cc = new THREE.Color();
        let nPts = 0;
        // trace every level first: the sample spacing is set so the ledges take at most a fifth of the budget
        const traced = [], apron = []; let Lsum = 0;
        levels.forEach((lev, li) => traceContours(Y, NV, cell, S, lev, keepCell).forEach((chain, ci) => {
          if (chain.length < 3) return; traced.push([li, ci, chain]);
          for (let k = 1; k < chain.length; k++) Lsum += Math.hypot(chain[k][0] - chain[k - 1][0], chain[k][1] - chain[k - 1][1]); }));
        const STEP = Math.max(1.1, 12 * 0.6 * Lsum / (0.15 * o.budget));
        traced.forEach(([li, ci, chain]) => {
          {
            const pts = resample(chain, STEP);
            if (pts.length < 4) return;
            // runs: broken where a slow noise says the bed is buried
            let arc = 0; const on = [];
            pts.forEach((p, k) => { if (k) arc += STEP; const ph = li * 37.1 + ci * 3.3;
              on.push({ p, arc, g: nL(arc / 16 + ph, li * 5.3) > (li % 2 ? 0.5 : 0.36), t: nL(arc / 5 + ph + 90, li * 2.1 + 40) }); });
            const runs = []; let cur = null;
            on.forEach((q) => { if (q.g) { if (!cur) { cur = []; runs.push(cur); } cur.push(q); } else cur = null; });
            runs.forEach((run) => {
              if (run.length < 4) return;
              const thick = (li % 2 ? 0.55 : 1) * (0.9 + r() * 0.5), tone = base[Math.floor(r() * base.length)], startV = nPts;
              const L = run[run.length - 1].arc - run[0].arc;
              run.forEach((q, k) => {
                const [x, z] = q.p, sl = slopeAt(x, z), gl = Math.hypot(sl.gx, sl.gz) || 1, nx = sl.gx / gl, nz = sl.gz / gl;   // downhill: minus the gradient
                const dx = -nx, dz = -nz, yc = hAt(x, z).y;
                const end = smooth(0, 2.4, Math.min(q.arc - run[0].arc, L - (q.arc - run[0].arc)));
                const h = (0.6 + 2.2 * q.t * q.t) * thick * end, s = Math.max(0.25, sl.s);
                const a = clamp(0.8 * h / s + 0.3, 0.35, 1.6);   // a wider tread lifted off gentle slopes like a rug
                const yT = yc + 0.8 * h;
                const prof = [
                  [-a, Math.min(yT - 0.1, hAt(x - dx * a, z - dz * a).y - 0.3), 0.72],
                  [-a * 0.45, yT - 0.04 - 0.08 * h, 0.8],
                  [0.08, yT, 0.95], [0.08, yT, 1.0],           // the lip, twice: one normal on the tread, one on the face
                  [0.04, yT - 0.3 * h, 0.7],
                  [-0.2 * h - 0.06, yT - 0.5 * h, 0.32],      // the undercut, in its own shadow
                  [-0.06, yc - 0.12, 0.62],
                  [0.35, hAt(x + dx * 0.35, z + dz * 0.35).y - 0.3, 0.5],
                ];
                let vv = 0;
                prof.forEach((pr, pi) => {
                  const ox = pr[0];
                  Pp.push(x + dx * ox, pr[1], z + dz * ox);
                  if (pi) vv += Math.hypot(prof[pi][0] - prof[pi - 1][0], prof[pi][1] - prof[pi - 1][1]);
                  Uu.push(q.arc / 2, vv / 2);
                  const k3 = pr[2] * (0.88 + 0.24 * nL(q.arc / 3 + 7, pi * 1.7));
                  cc.copy(tone).multiplyScalar(k3); Cc.push(cc.r, cc.g, cc.b);
                });
                nPts += prof.length;
                if (h > 0.3) apron.push([x + dx * (1.2 + h), z + dz * (1.2 + h), 2 + 2.2 * h]);
                if (h > 0.5 && r() < 0.45 * o.rocks) {        // talus: blocks fallen from the lip
                  const off = 0.5 + r() * 2.6;
                  const k = 0.12 + r() * 0.3 * h; stoneSpots.push([x + dx * off, hAt(x + dx * off, z + dz * off).y - k * 0.45, z + dz * off, k]);
                }
              });
              const NP = 8;
              for (let k = 0; k < run.length - 1; k++) for (let pi = 0; pi < NP - 1; pi++) {
                if (pi === 2) continue;                        // the split lip
                const a0 = startV + k * NP + pi, b0 = a0 + NP;
                Ix.push(a0, b0, a0 + 1, a0 + 1, b0, b0 + 1);
              }
            });
          }
        });
        // the apron of weathered rock and thin soil under each ledge, paler and greyer, on the ground colour
        const cAp = col(pal.thin).lerp(col(pal.rock), 0.45);
        apron.forEach(([ax, az, rad]) => {
          const i0 = Math.max(0, Math.floor((ax - rad + S / 2) / cell)), i1 = Math.min(seg, Math.ceil((ax + rad + S / 2) / cell));
          const j0 = Math.max(0, Math.floor((az - rad + S / 2) / cell)), j1 = Math.min(seg, Math.ceil((az + rad + S / 2) / cell));
          for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) {
            const d = Math.hypot(-S / 2 + i * cell - ax, -S / 2 + j * cell - az) / rad; if (d >= 1) continue;
            const k = (1 - smooth(0.25, 1, d)) * 0.8, q = (j * NV + i) * 3;
            C[q] += (cAp.r - C[q]) * k; C[q + 1] += (cAp.g - C[q + 1]) * k; C[q + 2] += (cAp.b - C[q + 2]) * k;
          }
        });
        geo.attributes.color.needsUpdate = true;
        if (Ix.length) {
          const lg = new THREE.BufferGeometry();
          lg.setAttribute('position', new THREE.Float32BufferAttribute(Pp, 3)); lg.setAttribute('color', new THREE.Float32BufferAttribute(Cc, 3));
          lg.setAttribute('uv', new THREE.Float32BufferAttribute(Uu, 2)); lg.setIndex(Ix); lg.computeVertexNormals();
          const lm = M('hct-ledge2', { color: 0xffffff, roughness: 0.9, vertexColors: true, map: limeTex(), side: THREE.DoubleSide });
          const ledge = new THREE.Mesh(lg, lm); ledge.castShadow = true; ledge.receiveShadow = true; g.add(ledge);
          spent += Ix.length / 3;
        }
      }
      // loose rock on the thin soil of the slopes, gathered toward the viewer where it can be seen
      if (o.rocks > 0) {
        const want = Math.round(1000 * o.rocks); let tries = 0, n = 0;
        while (n < want && tries < want * 30) {
          tries++;
          const d = Math.pow(r(), 1.8) * S * 0.7, a = r() * TAU, x = near[0] + Math.cos(a) * d, z = near[1] + Math.sin(a) * d;
          if (Math.abs(x) > S / 2 || Math.abs(z) > S / 2) continue;
          const H = hAt(x, z); if (H.m < 0.35) continue;
          const sl = slopeAt(x, z).s; if (r() > smooth(0.08, 0.3, sl) + 0.04) continue;
          const k = (0.08 + Math.pow(r(), 2.5) * 0.4) * (1 + d / 300); stoneSpots.push([x, H.y - k * 0.5, z, k]); n++;
        }
      }
      if (stoneSpots.length) { stones(r, stoneSpots, 'hct-lime', [0x8e8b84, 0x7f7c76, 0x9a968c, 0x74726c], g, true); spent += stoneSpots.length * 20; }

      /* ---- trees ----------------------------------------------------------------------------- */
      if (trees.length) {
        const got = plantTrees(g, trees, Math.max(20000, o.budget - spent));
        if (got < 0) legacyTrees(g, trees, r);
      }
      g.userData.heightAt = (x, z) => (Math.abs(x) < S / 2 && Math.abs(z) < S / 2 ? hAt(x, z).y : Hf(x, z).y);   // callers can seat things on it
      return g;
    },
  });
  // the first pass's card crowns, kept for a kit without kit/trees.js
  function legacyTrees(g, trees, r) {
    const J = { rx: 0.32, ry: 0.5, rz: 0.32, cy: 0.5, cards: 18, ao: 0.4 }, O = { rx: 0.62, ry: 0.3, rz: 0.62, cy: 0.66, cards: 26, ao: 0.4 };
    const jCard = crownGeo(r, J), oCard = crownGeo(r, O), oCore = coreGeo(1234, Object.assign({ trunk: 0.045, detail: 1, k: 0.5 }, O));
    const coreM = M('hct-core', { color: 0x3a4a2c, roughness: 0.95, vertexColors: true });
    const jl = [], jc = [], ol = [], oc = [];
    trees.forEach((t) => { if (t.sp === 'live_oak') { const h = 9 * t.sy; ol.push({ x: t.x, y: t.y, z: t.z, ry: t.ry, sx: h * 1.4, sy: h, sz: h * 1.4 }); oc.push(t.tint); }
      else { const h = 6.5 * t.sy; jl.push({ x: t.x, y: t.y, z: t.z, ry: t.ry, sx: h * 0.9, sy: h, sz: h * 0.9 }); jc.push(t.tint); } });
    if (jl.length) g.add(instanced(jCard, leafMat('juniper'), jl, jc));
    if (ol.length) { g.add(instanced(oCard, leafMat('oak'), ol, oc)); g.add(instanced(oCore, coreM, ol, oc)); }
  }

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
        const jt = n3(u * 96, v * 6); if (jt > 0.76) k *= 1 - (jt - 0.76) * 0.7;      // joints
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
          uv[(i * rows + k) * 2] = th * Rr / 70; uv[(i * rows + k) * 2 + 1] = y / 24;
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
    options: { length: 60, width: 4.2, curve: 0.25, centerGrass: true, verge: 2.6, ground: 0x6d7a3c },
    note: 'A pale caliche ranch road running along z: a crowned bed, two packed wheel tracks, a weedy centre strip, graded berms of loose gravel and grass verges that sink into TXT.ground. curve bows it sideways (fraction of length/4).',
    make(o, r) {
      o = Object.assign({ length: 60, width: 4.2, curve: 0.25, centerGrass: true, verge: 2.6, ground: 0x6d7a3c }, o);
      const g = new THREE.Group(), L = o.length, W = o.width, V = o.verge, seed = 5000 + o.seed * 13;
      const n1 = noise2(seed), n2 = noise2(seed + 1);
      const centre = (t) => [o.curve * L * 0.25 * (1 - Math.pow(2 * t - 1, 2)) - o.curve * L * 0.125 + (n1(t * 4, 2) - 0.5) * 0.6, L / 2 - t * L];
      const cRoad = col(0xebe2ca), cTrack = col(0xf4eddb), cLoose = col(0xddd1b3), cVerge = col(0x7a8045), cEdge = col(o.ground), cMid = col(0x9d9464);
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
    options: { length: 80, lanes: 2, surface: 'asphalt', gantry: true, overpass: false, embank: 0.6, ground: 0x6d7a3c },
    note: 'A divided highway along z: two carriageways of 3.66 m lanes, 3 m outside and 1.2 m inside shoulders with rumble strips, white edge and 3 m / 9 m skip lines, yellow inside edge lines, an F-shape concrete median barrier, grassed side slopes. gantry adds an overhead truss with blank green panels over the right carriageway; overpass adds a crossing bridge on round columns and bent caps with MSE walled approaches.',
    make(o, r) {
      o = Object.assign({ length: 80, lanes: 2, surface: 'asphalt', gantry: true, overpass: false, embank: 0.6, ground: 0x6d7a3c }, o);
      const g = new THREE.Group(), L = o.length, E = o.embank, LW = 3.66, SI = 1.2, SO = 3.0, MED = 0.9;
      const CW = SI + o.lanes * LW + SO;                         // one carriageway
      const half = MED / 2 + CW;                                 // edge of pavement
      const slope = 4 * E + 3;                                   // side slope and ditch
      // ---- earthwork: grassed side slopes and a shallow ditch
      const cG = col(0x74783f), cG2 = col(0x828548), cEdge = col(o.ground);
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
    options: { length: 40, width: 30, bed: 9, bank: 1.8, water: 'shallow', ground: 0x6d7a3c },
    note: 'A Hill Country creek running along z: flat limestone bedrock with stepped ledges and potholes, gravel bars, slabs, grassy banks that rise 1 to 2.5 m and sink back into TXT.ground at the sides. water: dry, shallow (clear pools over the rock) or full. Built above grade, since nothing can be cut into the ground plane.',
    make(o, r) {
      o = Object.assign({ length: 40, width: 30, bed: 9, bank: 1.8, water: 'shallow', ground: 0x6d7a3c }, o);
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
      const cRock = col(0xe4dccb), cRockD = col(0xc8bfac), cGrav = col(0xcfc8b8), cBankRock = col(0xd6cdb8), cGrass = col(0x6f7a3e), cGrass2 = col(0x87874a), cEdge = col(o.ground), cMud = col(0x7a6a52), tmp = new THREE.Color();
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
    options: { width: 300, water: 200, land: 60, bluff: 3.5, drawdown: 1.2, ramp: true, ground: 0x6d7a3c },
    note: 'A reservoir shore: land at -z rising to a low bluff and sinking back into TXT.ground, a pale drawdown band of cracked mud and rock (the bathtub ring of a Texas lake in drought), and a wide reflective water plane toward +z with waves. ramp adds a grooved concrete boat ramp with curbs running into the water. The water surface stands at y = 0.35.',
    make(o, r) {
      o = Object.assign({ width: 300, water: 200, land: 60, bluff: 3.5, drawdown: 1.2, ramp: true, ground: 0x6d7a3c }, o);
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
      const cBed = col(0x6f6553), cMud = col(0xd3c9b2), cCrack = col(0xbdb39c), cRock = col(0xc7bfae), cGrass = col(0x72793f), cGrass2 = col(0x8a8a4c), cEdge = col(o.ground), cWet = col(0x6b5d48);
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

  /* ---- cotton (2026-09-24, second pass). The first pass drew bare sticks carrying white cones.
   * A Texas cotton plant at harvest is a knee to waist high (0.7 to 1.0 m), bushy, dark reddish
   * brown, zigzag branched shrub: a main stem, fruiting branches that leave it alternately, longest
   * at the bottom so the plant is a rough pyramid, and at each branch node an open boll, four or
   * five lumpy locks of lint bursting from a dried brown bur with its bracts curled back. Before
   * defoliation the same frame carries broad, lobed green leaves, green bolls, cream and pink
   * flowers. The plant is two geometries: `solid` (stems, bolls, burs, vertex coloured) and
   * `cards` (leaves, alpha tested, from an atlas), instanced together. */
  // a stick between two points: a three sided tapered prism (6 triangles), coloured
  function twig(a, b, r0, r1, c) {
    const A = new THREE.Vector3(a[0], a[1], a[2]), B = new THREE.Vector3(b[0], b[1], b[2]), L = A.distanceTo(B);
    const g = new THREE.CylinderGeometry(r1, r0, L, 3, 1, true).toNonIndexed();
    g.translate(0, L / 2, 0);
    g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), B.clone().sub(A).normalize()));
    g.translate(A.x, A.y, A.z);
    return paintGeo(g, c);
  }
  // an open boll: ONE lobed ball, four or five locks pushed out round its equator and a softer
  // crown (an octahedron subdivided once, 32 triangles, smooth), over a dark bur whose three
  // bracts curl back. Four octahedra per boll were tried first and read as faceted diamonds.
  function openBoll(rng, s, lite) {
    const parts = [], n = 4 + (rng() < 0.4 ? 1 : 0), ph = rng() * TAU;
    const g = lite ? new THREE.OctahedronGeometry(1, 0) : new THREE.IcosahedronGeometry(1, 1), p = g.attributes.position, v = new THREE.Vector3();
    const lobeAt = new Float32Array(p.count);
    for (let i = 0; i < p.count; i++) {
      v.set(p.getX(i), p.getY(i), p.getZ(i)).normalize();
      const phi = Math.atan2(v.z, v.x), eq = 1 - Math.abs(v.y), lb = Math.cos(n * (phi + ph));
      const k = 1 + 0.3 * eq * Math.max(-0.5, lb) + (v.y > 0 ? 0.1 : -0.12);
      lobeAt[i] = eq * (0.5 - 0.5 * lb);
      p.setXYZ(i, v.x * s * 1.25 * k, v.y * s * 0.95 * k + s * 0.2, v.z * s * 1.25 * k);
    }
    // the grooves between the locks and the underside carry their own occlusion
    const sg = smoothNormals(g), C = new Float32Array(sg.attributes.position.count * 3), cw = col([0xf6f4ee, 0xf1eee4, 0xebe5d6][Math.floor(rng() * 3)]), tmpc = new THREE.Color();
    for (let i = 0; i < sg.attributes.position.count; i++) {
      const y = sg.attributes.position.getY(i) - s * 0.2, lo = smooth(0.1 * s, -0.9 * s, y);
      tmpc.copy(cw).multiplyScalar((1 - 0.4 * lobeAt[i] * lobeAt[i]) * (1 - 0.38 * lo)); C[i * 3] = tmpc.r; C[i * 3 + 1] = tmpc.g; C[i * 3 + 2] = tmpc.b;
    }
    sg.setAttribute('color', new THREE.BufferAttribute(C, 3)); parts.push(sg);
    if (!lite) {
      const P = [], Cc = [], cb = col(0x3a281c), cl = col(0x6b4a32);
      for (let k = 0; k < 3; k++) {
        const a = k / 3 * TAU + rng(), ca = Math.cos(a), sa = Math.sin(a), ta = a + 0.5;
        const tip = [Math.cos(a + 0.25) * s * 1.5, -s * 0.45, Math.sin(a + 0.25) * s * 1.5];
        [[0, -s * 0.2, 0], [ca * s * 0.8, -s * 0.1, sa * s * 0.8], tip, [0, -s * 0.2, 0], tip, [Math.cos(ta) * s * 0.8, -s * 0.1, Math.sin(ta) * s * 0.8]]
          .forEach((q, i) => { P.push(q[0], q[1], q[2]); const c = i === 2 || i === 4 ? cl : cb; Cc.push(c.r, c.g, c.b); });
      }
      const b = new THREE.BufferGeometry(); b.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); b.setAttribute('color', new THREE.Float32BufferAttribute(Cc, 3));
      b.computeVertexNormals(); parts.push(b);
    }
    return mergeGeos(parts);
  }
  function greenBoll(rng, s) {
    const g = new THREE.OctahedronGeometry(1, 0), p = g.attributes.position;
    for (let i = 0; i < p.count; i++) p.setXYZ(i, p.getX(i) * s * 0.8, p.getY(i) * s * 1.15, p.getZ(i) * s * 0.8);
    return paintGeo(smoothNormals(g), rng() < 0.5 ? 0x5f7b36 : 0x6d8a3e);
  }
  function flower(rng, s) {                               // a cup of five petals, cream on day one, pink on day two
    const P = [], C = [], c = col(rng() < 0.6 ? 0xf2e8c4 : 0xd98aa6);
    for (let k = 0; k < 5; k++) { const a = k / 5 * TAU, b = a + TAU / 5;
      [[0, 0, 0], [Math.cos(a) * s, s * 0.8, Math.sin(a) * s], [Math.cos(b) * s, s * 0.8, Math.sin(b) * s]].forEach((v) => { P.push(v[0], v[1], v[2]); C.push(c.r, c.g, c.b); }); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); g.setAttribute('color', new THREE.Float32BufferAttribute(C, 3));
    g.computeVertexNormals(); return g;
  }
  // leaf atlas: left half a broad lobed green cotton leaf, right half the same leaf dried and curled
  function cottonLeafTex() {
    return canvasTex('cotton-leaf', 256, (x, N, r) => {
      x.clearRect(0, 0, N, N);
      const leaf = (ox, green) => {
        const cx = ox + N / 4, cy = N * 0.55, R = N * 0.2;
        x.save(); x.translate(cx, cy);
        if (!green) x.scale(0.7, 0.85);
        x.beginPath();
        for (let i = 0; i <= 60; i++) {                      // five lobes, palmate, the stem notch at the bottom
          const t = i / 60, a = Math.PI / 2 + (t - 0.5) * TAU * 0.92, lobe = 0.6 + 0.4 * Math.pow(0.5 + 0.5 * Math.cos(5 * Math.PI * (t - 0.5)), 0.7);
          const rr = R * lobe * (green ? 1 : 0.8 + 0.2 * r());
          x.lineTo(Math.cos(a) * rr, -Math.sin(a) * rr);
        }
        x.closePath();
        const gr = x.createRadialGradient(0, 0, 2, 0, 0, R);
        if (green) { gr.addColorStop(0, '#5f7f38'); gr.addColorStop(1, '#46642a'); } else { gr.addColorStop(0, '#6b4a30'); gr.addColorStop(1, '#3f2a1c'); }
        x.fillStyle = gr; x.fill();
        x.strokeStyle = green ? 'rgba(160,190,110,0.55)' : 'rgba(40,26,18,0.6)'; x.lineWidth = 1.4;
        for (let k = 0; k < 5; k++) { const a = -Math.PI / 2 + (k - 2) * 0.62; x.beginPath(); x.moveTo(0, R * 0.25); x.lineTo(Math.cos(a) * R * 0.85, Math.sin(a) * R * 0.85); x.stroke(); }
        x.restore();
      };
      leaf(0, true); leaf(N / 2, false);
    });
  }
  // one leaf card: a quad of side s, its base at the origin, pointing along +x and tilted up by `tilt`
  function leafCard(s, tilt, ry, dry, pos) {
    const u0 = dry ? 0.5 : 0, u1 = dry ? 1 : 0.5, P = [], U = [], Nn = [];
    const q = [[0, -s / 2], [s, -s / 2], [s, s / 2], [0, s / 2]];
    [0, 1, 2, 0, 2, 3].forEach((k) => { const [lx, lz] = q[k]; P.push(lx, 0, lz); U.push(u0 + (lz / s + 0.5) * (u1 - u0), 0.15 + 0.85 * lx / s); Nn.push(0, 1, 0); });
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(U, 2)); g.setAttribute('normal', new THREE.Float32BufferAttribute(Nn, 3));
    g.rotateZ(tilt); g.rotateY(ry); g.translate(pos[0], pos[1], pos[2]);
    const n = g.attributes.normal; for (let i = 0; i < n.count; i++) { const v = new THREE.Vector3(n.getX(i), Math.abs(n.getY(i)) + 0.5, n.getZ(i)).normalize(); n.setXYZ(i, v.x, v.y, v.z); }
    return paintGeo(g, dry ? 0xd8d0c4 : 0xffffff);
  }
  /* The tangle: what a sparse 3D skeleton can't give a row is its density, the mass of fine
   * zigzag twigs and dried leaf that closes it. Alpha tested cards painted with that tangle carry
   * it (2 triangles each), crossed round the stem at several heights; the 3D stem, branches and
   * bolls sit in and on them. Left half of the atlas: defoliated, brown. Right half: green. */
  function tangleTex() {
    return canvasTex('cotton-tangle', 512, (x, N, r) => {
      x.clearRect(0, 0, N, N);
      for (let half = 0; half < 2; half++) {
        const ox = half * N / 2, W = N / 2, green = half === 1;
        x.save(); x.beginPath(); x.rect(ox, 0, W, N); x.clip();
        const twig = (x0, y0, a, len, w, depth) => {
          let px = x0, py = y0, aa = a;
          x.strokeStyle = green ? 'rgb(' + (70 + r() * 30) + ',' + (96 + r() * 30) + ',' + (46 + r() * 16) + ')' : 'rgb(' + (58 + r() * 30) + ',' + (38 + r() * 18) + ',' + (28 + r() * 12) + ')';
          x.lineWidth = w; x.lineCap = 'round'; x.beginPath(); x.moveTo(px, py);
          const segs = 3 + Math.floor(r() * 3);
          for (let k = 0; k < segs; k++) { aa += (k % 2 ? 1 : -1) * (0.35 + r() * 0.3); const l = len / segs; px += Math.cos(aa) * l; py -= Math.sin(aa) * l; x.lineTo(px, py);
            if (depth > 0 && r() < 0.6) { x.stroke(); twig(px, py, aa + (r() < 0.5 ? 0.9 : -0.9), len * 0.45, w * 0.6, depth - 1); x.beginPath(); x.moveTo(px, py); x.strokeStyle = green ? 'rgb(76,100,50)' : 'rgb(62,40,30)'; x.lineWidth = w; }
            if (!green && r() < 0.35) { x.save(); x.fillStyle = 'rgb(' + (46 + r() * 26) + ',' + (32 + r() * 14) + ',' + (24 + r() * 10) + ')'; x.beginPath(); x.ellipse(px, py, 3 + r() * 5, 2 + r() * 3, r() * 3, 0, TAU); x.fill(); x.restore(); }
          }
          x.stroke();
        };
        const cx = ox + W / 2;
        for (let i = 0; i < 26; i++) { const y0 = N * (0.35 + r() * 0.6), side = r() < 0.5 ? -1 : 1; twig(cx + (r() - 0.5) * W * 0.12, y0, Math.PI / 2 + side * (0.5 + r() * 0.7), W * (0.2 + r() * 0.25), 2 + r() * 2, 2); }
        if (green) for (let i = 0; i < 70; i++) {            // leaves: broad, lobed, overlapping, lit above
          const px = ox + W * (0.12 + r() * 0.76), py = N * (0.1 + r() * 0.75), s = 9 + r() * 14, k = 0.75 + r() * 0.4, t = 1 - py / N;
          x.fillStyle = 'rgb(' + Math.round((52 + 30 * t) * k) + ',' + Math.round((74 + 34 * t) * k) + ',' + Math.round((34 + 12 * t) * k) + ')';
          x.beginPath(); for (let j = 0; j <= 20; j++) { const a = j / 20 * TAU, rr = s * (0.7 + 0.3 * Math.abs(Math.cos(a * 2.5))); x.lineTo(px + Math.cos(a) * rr, py + Math.sin(a) * rr * 0.8); } x.fill();
        } else for (let i = 0; i < 6; i++) {                 // a little lint caught in the twigs
          const px = ox + W * (0.2 + r() * 0.6), py = N * (0.2 + r() * 0.6), s = 3 + r() * 4;
          x.fillStyle = 'rgb(214,208,196)'; x.beginPath(); x.ellipse(px, py, s, s * 0.8, 0, 0, TAU); x.fill();
        }
        x.restore();
      }
    });
  }
  // one tangle card: w wide, h tall, standing on its bottom edge at `pos`, turned ry, leaning `lean`
  function tangleCard(w, h, ry, lean, pos, green) {
    const u0 = green ? 0.5 : 0, u1 = green ? 1 : 0.5, P = [], U = [], Nn = [];
    const q = [[-w / 2, 0], [w / 2, 0], [w / 2, h], [-w / 2, h]];
    [0, 1, 2, 0, 2, 3].forEach((k) => { const [lx, ly] = q[k]; P.push(lx, ly, 0); U.push(u0 + (lx / w + 0.5) * (u1 - u0), 0.02 + 0.6 * ly / h);
      Nn.push(0, 0, 1); });
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3));
    g.setAttribute('uv', new THREE.Float32BufferAttribute(U, 2)); g.setAttribute('normal', new THREE.Float32BufferAttribute(Nn, 3));
    g.rotateX(lean); g.rotateY(ry); g.translate(pos[0], pos[1], pos[2]);
    // normals out from the plant's axis and up, so a bush of cards shades as one volume
    const p = g.attributes.position, n = g.attributes.normal, v = new THREE.Vector3();
    for (let i = 0; i < p.count; i++) { v.set(p.getX(i), 0, p.getZ(i)); if (v.lengthSq() < 1e-6) v.set(Math.sin(ry), 0, Math.cos(ry)); v.normalize(); v.y = 0.6 + p.getY(i) * 0.8; v.normalize(); n.setXYZ(i, v.x, v.y, v.z); }
    return paintGeo(g, 0xffffff);
  }
  function cottonPlant(rng, growth, lite) {
    const solid = [], cards = [], leaves = [];
    const gk = clamp(growth / 0.8, 0, 1), H = lerp(0.2, 0.8, gk) * (0.85 + rng() * 0.3);
    const open = growth >= 0.88, green = !open;
    const stemC = open ? 0x4a2e22 : 0x5f6f38, twigC = open ? 0x5a3828 : 0x62783a;
    const sp = [[0, -0.02, 0]];
    for (let k = 1; k <= (lite ? 1 : 3); k++) sp.push([(rng() - 0.5) * 0.04, H * k / (lite ? 1.4 : 3), (rng() - 0.5) * 0.04]);
    for (let k = 0; k < sp.length - 1; k++) solid.push(twig(sp[k], sp[k + 1], lerp(0.013, 0.005, k / 3), lerp(0.013, 0.005, (k + 1) / 3), stemC));
    // the tangle: cards crossed round the stem, widest low, as the plant is
    const nc = lite ? 3 : Math.round(lerp(3, 7, gk));
    for (let k = 0; k < nc; k++) {
      const t = k / nc, w = H * (0.8 - 0.35 * t) * (0.85 + rng() * 0.3), h = H * (0.5 + rng() * 0.25);
      cards.push(tangleCard(w, h, k * 2.1 + rng() * 0.6, (rng() - 0.5) * 0.35, [(rng() - 0.5) * 0.05, H * (0.05 + 0.3 * t), (rng() - 0.5) * 0.05], green));
    }
    const nb = lite ? 0 : Math.round(lerp(2, 6, gk)), bs = 0.026 + rng() * 0.006;
    const node = (p, t) => {
      if (open) { if (rng() < 0.9) solid.push(place(openBoll(rng, bs * (0.85 + rng() * 0.3), lite), p[0], p[1] - bs * 0.2, p[2], rng() * TAU)); }
      else if (growth > 0.55) {
        const u = rng();
        if (growth > 0.72 && t < 0.4 && u < (growth - 0.7) * 2.2) solid.push(place(openBoll(rng, bs, lite), p[0], p[1], p[2], rng() * TAU));
        else if (t > 0.6 && u < 0.3 && !lite) solid.push(place(flower(rng, 0.03), p[0], p[1] + 0.02, p[2]));
        else if (u < 0.7) solid.push(place(greenBoll(rng, 0.022), p[0], p[1] - 0.01, p[2]));
      }
      if (green && !lite) for (let j = 0; j < 2; j++) leaves.push(leafCard(0.12 + rng() * 0.06, 0.2 + rng() * 0.4, rng() * TAU, false, p));
    };
    let az = rng() * TAU;
    for (let b = 0; b < nb; b++) {
      const t = 0.18 + 0.72 * b / Math.max(1, nb - 1) + (rng() - 0.5) * 0.06, y = H * t;
      az += 2.36 + (rng() - 0.5) * 0.4;
      const L = (0.12 + 0.3 * Math.pow(1 - t, 0.8)) * (H / 0.9) * (0.8 + rng() * 0.4);
      const d1 = [Math.cos(az), 0.35 + rng() * 0.2, Math.sin(az)], zz = az + (rng() < 0.5 ? 0.5 : -0.5), d2 = [Math.cos(zz), 0.3, Math.sin(zz)];
      const n1 = [d1[0] * L * 0.55, y + d1[1] * L * 0.55, d1[2] * L * 0.55], n2 = [n1[0] + d2[0] * L * 0.45, n1[1] + d2[1] * L * 0.45, n1[2] + d2[2] * L * 0.45];
      solid.push(twig([0, y, 0], n1, 0.006, 0.004, twigC)); solid.push(twig(n1, n2, 0.004, 0.0025, twigC));
      node(n1, t); node(n2, t);
    }
    if (lite && open) for (let k = 0; k < 5; k++) { const a = rng() * TAU, rr = H * (0.12 + rng() * 0.22), y = H * (0.25 + rng() * 0.5);
      solid.push(place(openBoll(rng, bs * 1.1, true), Math.cos(a) * rr, y, Math.sin(a) * rr)); }
    if (!lite && !open) node(sp[sp.length - 1], 1);          // a boll on the bare stem tip read as a lollipop
    if (green && !lite) for (let k = 0; k < 5; k++) leaves.push(leafCard(0.1 + rng() * 0.06, 0.3 + rng() * 0.5, rng() * TAU, false, [0, H * (0.8 + rng() * 0.18), 0]));
    return { solid: mergeGeos(solid), cards: cards.length ? mergeGeos(cards) : null, leaves: leaves.length ? mergeGeos(leaves) : null };
  }
  // a row's canopy core: the dense tangle a row closes into, textured with twigs and lint (or leaves)
  function hedgeTex(kind) {
    return canvasTex('hedge-' + kind, 256, (x, N, r) => {
      const green = kind !== 'open';
      x.fillStyle = green ? 'rgb(66,88,44)' : 'rgb(118,90,70)'; x.fillRect(0, 0, N, N);
      for (let i = 0; i < 700; i++) {                      // twigs
        const px = r() * N, py = r() * N, a = r() * TAU, l = 6 + r() * 18;
        x.strokeStyle = green ? 'rgba(' + (60 + r() * 50) + ',' + (84 + r() * 50) + ',' + (40 + r() * 20) + ',0.8)' : 'rgba(' + (40 + r() * 50) + ',' + (26 + r() * 30) + ',' + (18 + r() * 20) + ',0.8)';
        x.lineWidth = 1 + r() * 2;
        for (let dx = -N; dx <= N; dx += N) for (let dy = -N; dy <= N; dy += N) { x.beginPath(); x.moveTo(px + dx, py + dy); x.lineTo(px + dx + Math.cos(a) * l, py + dy + Math.sin(a) * l); x.stroke(); }
      }
      const nb = kind === 'open' ? 900 : kind === 'split' ? 60 : 0;
      for (let i = 0; i < nb; i++) {                       // bolls: four or five locks, a shadow under
        const px = r() * N, py = r() * N, s = 2.4 + r() * 2;
        for (let dx = -N; dx <= N; dx += N) for (let dy = -N; dy <= N; dy += N) {
          x.fillStyle = 'rgba(40,26,18,0.35)'; x.beginPath(); x.ellipse(px + dx + 1, py + dy + 1.5, s * 1.4, s * 1.1, 0, 0, TAU); x.fill();
          for (let k = 0; k < 4; k++) { const a = k / 4 * TAU + r(); const q = 225 + r() * 30;
            x.fillStyle = 'rgb(' + q + ',' + q + ',' + (q - 8) + ')'; x.beginPath(); x.ellipse(px + dx + Math.cos(a) * s * 0.6, py + dy + Math.sin(a) * s * 0.6, s * 0.75, s * 0.65, a, 0, TAU); x.fill(); }
        }
      }
    });
  }
  // the soil of a cotton field at harvest: clods, the grey of a dry crust, and lint blown off the bolls
  function fieldSoilTex(lint) {
    return canvasTex('fieldsoil-' + (lint ? 'lint' : 'bare'), 512, (x, N, r) => {
      const n1 = tileNoise(901, 16), n2 = tileNoise(907, 64), n3 = tileNoise(911, 128);
      pixelPaint(x, N, (i, j) => { const u = i / N, v = j / N;
        const k = 0.86 + (n1(u * 16, v * 16) - 0.5) * 0.12 + (n2(u * 64, v * 64) - 0.5) * 0.16 + (n3(u * 128, v * 128) - 0.5) * 0.14;
        return [232 * k, 226 * k, 218 * k]; });
      for (let i = 0; i < 1400; i++) {                     // clods: a lit top, a shadow under
        const px = r() * N, py = r() * N, s = 1.5 + r() * 4;
        x.fillStyle = 'rgba(40,28,20,0.35)'; x.beginPath(); x.ellipse(px + 1, py + 1.5, s, s * 0.7, 0, 0, TAU); x.fill();
        x.fillStyle = 'rgba(255,246,236,0.22)'; x.beginPath(); x.ellipse(px, py, s * 0.8, s * 0.55, 0, 0, TAU); x.fill();
      }
      if (lint) for (let i = 0; i < 90; i++) { const px = r() * N, py = r() * N, s = 1.2 + r() * 2.5;
        x.fillStyle = 'rgba(255,255,252,0.9)'; x.beginPath(); x.ellipse(px, py, s, s * 0.7, r() * 3, 0, TAU); x.fill(); }
    });
  }
  // the linear mean of a map, per channel: what a surface multiplied by it averages to
  function texMeanLin(t) {
    if (t.userData.meanLin) return t.userData.meanLin;
    const c = t.image, d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data, lin = (v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    const s = [0, 0, 0]; let n = 0;
    for (let i = 0; i < d.length; i += 64) { s[0] += lin(d[i]); s[1] += lin(d[i + 1]); s[2] += lin(d[i + 2]); n++; }
    return (t.userData.meanLin = s.map((v) => v / n));
  }
  function sorghumPlant(rng, growth) {
    const parts = [], H = lerp(0.3, 1.2, clamp(growth / 0.7, 0, 1)) * (0.78 + rng() * 0.4);
    const ripe = growth >= 0.85, headed = growth >= 0.6;
    parts.push(stem(H, 0.011, 0.007, ripe ? 0x5f6a3a : 0x4f6c32, 5));
    for (let k = 0; k < 7; k++) {
      const y = H * (0.08 + 0.78 * k / 7), dry = ripe && k < 2;
      const lf = leafStrip(0.55 + rng() * 0.2 - k * 0.03, 0.055, 0.8, 1.5, 3, dry ? 0x8f8055 : 0x3f5f29, dry ? 0xb4a16c : (ripe ? 0x7c8a46 : 0x68893c));
      place(lf, 0, y, 0, k * 2.4 + rng() * 0.7, 0.25 + rng() * 0.25); parts.push(lf);
    }
    if (headed) {
      const hc = ripe ? [0x6a2c1c, 0x7a331f, 0x5e2a1b, 0x844024][Math.floor(rng() * 4)] : 0x8fa05a;
      const hd = lump(Math.floor(rng() * 1e5), 1, 0.034, 0.085, 0.034, 0.8); hd.translate(0, 0.08, 0);
      parts.push(place(paintGeo(hd, hc), 0, H, 0, rng() * TAU, (rng() - 0.5) * 0.35));
    }
    return mergeGeos(parts);
  }

  /* ======================================================================================
   * crop_rows: a field block of cotton or sorghum on bedded rows
   * ====================================================================================== */
  K.define('crop_rows', {
    size: [20, 1.4, 30],
    options: { crop: 'cotton', growth: 1, width: 20, length: 30, row: 1.02, soil: 0x8a5d40, ground: 0x6d7a3c, near: null, budget: 400000, verge: true },
    note: 'A field block of bedded rows running along z, 40 inch rows on raised beds of South Plains red soil. crop: cotton (growth 0.3 young, 0.7 green and leafy with flowers and a few open bolls, 1 defoliated at harvest: knee to waist high, bushy dark brown plants with lumpy open bolls, rows closing into a white flecked brown carpet) or sorghum (growth 1 ripe rust heads). width x length is the planted block; round it a packed turn row (5 m at the ends, 3 m at the sides) and a grassy verge melting into TXT.ground (`ground` is that plane\'s colour; verge:false leaves bare soil). `near` [x, z] in model space is where the viewer stands (default: the middle of the front, +z, edge): whole plants gather there, simpler plants further off, and past the triangle `budget` each row is its canopy alone, which is how a field reads at a distance anyway.',
    make(o, r) {
      o = Object.assign({ crop: 'cotton', growth: 1, width: 20, length: 30, row: 1.02, soil: 0x8a5d40, ground: 0x6d7a3c, near: null, budget: 400000, verge: true }, o);
      const g = new THREE.Group(), W = o.width, L = o.length, sp = o.row, seed = 9000 + o.seed * 3;
      const cotton = o.crop !== 'sorghum', open = cotton && o.growth >= 0.88;
      const nS = noise2(seed), nV = noise2(seed + 5), rows = Math.max(1, Math.floor(W / sp)), x0 = -(rows - 1) * sp / 2;
      const MX = 3, MZ = 5, WT = W + 2 * MX, LT = L + 2 * MZ;
      const near = o.near ? [o.near[0], o.near[1]] : [0, L / 2];
      // beds 15 to 20 cm high with flat tops, feathering out at the block edge into the turn row
      const inBlock = (x, z) => smooth(0, 0.9, Math.min(W / 2 + 0.45 - Math.abs(x), L / 2 + 0.6 - Math.abs(z)));
      const outer = (x, z) => Math.min(WT / 2 - Math.abs(x), LT / 2 - Math.abs(z)) + (nV(x * 0.35 + 3, z * 0.35) - 0.5) * 1.2;
      const bedAt = (x, z) => {
        const u = (x - x0) / sp, f = u - Math.round(u);
        const bed = 0.04 + 0.15 * Math.pow(Math.pow(Math.cos(Math.PI * f), 2), 0.55) + (nS(x * 1.2, z * 1.2) - 0.5) * 0.025;
        const turn = 0.035 + (nS(x * 0.5 + 20, z * 0.5) - 0.5) * 0.03;
        return lerp(lerp(-0.03, turn, smooth(0, 1.2, outer(x, z))), bed, inBlock(x, z));
      };
      const segX = Math.min(Math.round(WT * 6), 720), segZ = Math.round(clamp(30000 / segX, 8, LT * 1.6));
      const geo = heightfield(WT, LT, segX, segZ, bedAt);
      const soilTex = cotton ? fieldSoilTex(open) : detailTex('soil'), ml = texMeanLin(soilTex);
      const P = geo.attributes.position, C = new Float32Array(P.count * 3), cs = col(o.soil), cd = col(o.soil).multiplyScalar(0.7), ct = col(o.soil).lerp(col(0xa89478), 0.35).multiplyScalar(1.05);
      const cRim = col(o.ground); cRim.r *= 0.97 / ml[0]; cRim.g *= 0.97 / ml[1]; cRim.b *= 0.97 / ml[2];
      const cVerge = cRim.clone().lerp(col(0x9a8f5c).multiplyScalar(0.97 / ((ml[0] + ml[1] + ml[2]) / 3)), 0.35), tmp = new THREE.Color();
      for (let i = 0; i < P.count; i++) {
        const x = P.getX(i), z = P.getZ(i), y = P.getY(i), ib = inBlock(x, z), e = outer(x, z);
        mix3(tmp, cd, cs, smooth(0.05, 0.17, y)); tmp.multiplyScalar(0.9 + fbm(nS, x * 0.3, z * 0.3, 2) * 0.2);
        const turn = ct.clone().multiplyScalar(0.92 + fbm(nV, x * 0.2, z * 0.2, 2) * 0.16);
        // tyre tracks along the turn rows at the ends
        const dz = Math.abs(z) - L / 2; if (dz > 0.8 && (Math.abs(dz - 1.8) < 0.22 || Math.abs(dz - 3.4) < 0.22)) turn.multiplyScalar(0.82);
        mix3(tmp, turn, tmp, ib);
        if (o.verge) mix3(tmp, cRim, tmp, smooth(0.2, 2.6, e)), mix3(tmp, tmp, cVerge, (1 - smooth(1.2, 2.4, e)) * smooth(0, 0.6, e) * 0.5);
        C[i * 3] = tmp.r; C[i * 3 + 1] = tmp.g; C[i * 3 + 2] = tmp.b;
      }
      geo.setAttribute('color', new THREE.BufferAttribute(C, 3));
      const uv = geo.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * WT / 1.6, uv.getY(i) * LT / 1.6);
      const soil = new THREE.Mesh(geo, M('crop-soil-' + (cotton ? (open ? 'lint' : 'bare') : 'sorg'), { color: 0xffffff, vertexColors: true, map: soilTex, roughness: 0.96 }));
      soil.userData.txGround = true; soil.receiveShadow = true; g.add(soil);
      let spent = segX * segZ * 2;

      // the verge: bunch grass and weeds along the field's edge, where the viewer can see them
      if (o.verge) {
        const spots = [];
        for (let i = 0; i < 2600 && spots.length < 700; i++) {
          const side = r(), t = r() - 0.5, e = Math.pow(r(), 0.7) * 2.3;
          const x = side < 0.5 ? t * WT : (side < 0.75 ? -1 : 1) * (WT / 2 - e), z = side < 0.5 ? (side < 0.25 ? -1 : 1) * (LT / 2 - e) : t * LT;
          if (Math.hypot(x - near[0], z - near[1]) > 45 + r() * 20) continue;
          const ee = outer(x, z); if (ee < 0.15 || ee > 2.4) continue;
          spots.push([x, bedAt(x, z) - 0.02, z, 0.6 + r() * 0.6]);
        }
        if (spots.length) { tuftField(r, spots, { key: 'verge', blades: 9, height: 0.42, spread: 0.1, width: 0.011, lean: 0.4, colors: [0x4d4a2c, 0x9b8f58, 0xcdbb84], variants: 3 }, g); spent += spots.length * 45; }
      }

      if (!cotton) {                                        // sorghum: every plant, as before
        const variants = [], VN = 4;
        for (let v = 0; v < VN; v++) variants.push({ geo: sorghumPlant(r, o.growth), list: [], cols: [] });
        // the plant spacing opens up only when the triangle budget can't carry a plant every 20 cm
        const tp = variants.reduce((s2, V) => s2 + V.geo.attributes.position.count / 3, 0) / VN;
        const step = Math.max(0.2, rows * L * tp / Math.max(1, (o.budget - spent) * 0.96));
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
        variants.forEach((V) => { g.add(instanced(V.geo, pm, V.list, V.cols)); });
        g.userData.heightAt = bedAt;
        return g;
      }

      /* ---- cotton ---------------------------------------------------------------------------- */
      const gk = clamp(o.growth / 0.8, 0, 1), Hp = lerp(0.2, 0.8, gk), withHedge = o.growth >= 0.45;
      const hedgeRes = withHedge ? 0.12 * o.budget : 0;
      // the plants: whole near the viewer, simple further off, none past the budget
      const VN = 6, full = [], lite = [];
      for (let v = 0; v < VN; v++) { full.push(cottonPlant(r, o.growth, false)); lite.push(cottonPlant(r, o.growth, true)); }
      const triOf = (P2) => (P2.solid.attributes.position.count + (P2.cards ? P2.cards.attributes.position.count : 0) + (P2.leaves ? P2.leaves.attributes.position.count : 0)) / 3;
      const cF = full.reduce((s, p) => s + triOf(p), 0) / VN, cL = lite.reduce((s, p) => s + triOf(p), 0) / VN;
      const step = 0.3, spots = [];
      for (let k = 0; k < rows; k++) {
        const x = x0 + k * sp;
        for (let z = -L / 2 + 0.25; z < L / 2 - 0.2; z += step * (0.8 + r() * 0.4)) {
          if (r() < 0.05) continue;
          spots.push({ x: x + (r() - 0.5) * 0.08, z, d: Math.hypot(x - near[0], z - near[1]), v: Math.floor(r() * VN), ry: r() * TAU, s: 0.85 + r() * 0.3 * (0.6 + 0.4 * nS(x * 0.2 + 9, z * 0.2)) });
        }
      }
      spots.sort((a, b) => a.d - b.d);
      const left = Math.max(0, o.budget - spent - hedgeRes), rF = o.detail || 16;
      let nF = 0; while (nF < spots.length && spots[nF].d < rF && (nF + 1) * cF < left * 0.8) nF++;
      const nL = Math.min(spots.length - nF, Math.floor((left - nF * cF) / cL));
      const dF = nF ? spots[nF - 1].d : 0, dL = nF + nL > 0 ? spots[nF + nL - 1].d : 0;
      const buckets = [];
      const put = (P2, key, sp2) => { if (!buckets[key]) buckets[key] = { P: P2, list: [], cols: [] }; const B = buckets[key];
        B.list.push({ x: sp2.x, y: bedAt(sp2.x, sp2.z) - 0.02, z: sp2.z, ry: sp2.ry, s: sp2.s, sy: sp2.s * (0.9 + r() * 0.2) });
        B.cols.push(new THREE.Color().setScalar(0.85 + r() * 0.25)); };
      spots.forEach((sp2, i) => {
        // the edges of each band are thinned at random, so no line marks where the detail changes
        if (i < nF) { if (sp2.d > dF * 0.8 && r() < smooth(dF * 0.8, dF, sp2.d) * 0.5) put(lite[sp2.v], 'l' + sp2.v, sp2); else put(full[sp2.v], 'f' + sp2.v, sp2); }
        else if (i < nF + nL) { if (sp2.d < dL * 0.85 || r() > smooth(dL * 0.85, dL, sp2.d)) put(lite[sp2.v], 'l' + sp2.v, sp2); }
      });
      const sm = foliageMat('cotton-solid', { roughness: 0.85 }), lm = foliageMat('cotton-leaf', { map: cottonLeafTex(), alphaTest: 0.5, roughness: 0.8 }),
        tm = foliageMat('cotton-tangle', { map: tangleTex(), alphaTest: 0.45, roughness: 0.9 });
      Object.keys(buckets).forEach((k) => { const B = buckets[k];
        g.add(instanced(B.P.solid, sm, B.list, B.cols));
        if (B.P.cards) g.add(instanced(B.P.cards, tm, B.list, B.cols));
        if (B.P.leaves) g.add(instanced(B.P.leaves, lm, B.list, B.cols)); });
      spent += nF * cF + nL * cL;
      /* The canopy of each row where whole plants stop: a low rounded mound along the bed textured
       * with twigs and lint (or leaves), under the simple plants and alone past them, which is how a
       * row reads from a distance. It rises over 7 m from the edge of the whole plant radius, never under a
       * whole plant, where it read as a tarpaulin. */
      if (withHedge) {
        const kind = open ? 'open' : o.growth > 0.72 ? 'split' : 'green';
        const rowLen = rows * L, hs = clamp(rowLen * 14 / hedgeRes, 0.25, 4);
        const Pp = [], Cc = [], Uu = [], Ix = [], wH = 0.42 * Math.min(1, 0.6 + gk * 0.4), hH = Hp * (open ? 0.62 : 0.7), dIn = dF * 0.95;
        const prof = [[-1, 0.0, 0.75], [-0.9, 0.38, 0.9], [-0.65, 0.75, 1.05], [-0.25, 0.97, 1.2], [0.25, 0.97, 1.2], [0.65, 0.75, 1.05], [0.9, 0.38, 0.9], [1, 0.0, 0.75]];
        const NP = prof.length;
        let nv = 0;
        for (let k = 0; k < rows; k++) {
          const x = x0 + k * sp; let run = -1, prevOn = false;
          for (let z = -L / 2 + 0.15; z <= L / 2 - 0.15 + 1e-6; z += hs) {
            const d = Math.hypot(x - near[0], z - near[1]), f = dIn > 0 ? smooth(dIn, dIn + 7, d) : 1;
            if (f <= 0) { prevOn = false; continue; }
            const hh = hH * f * (0.75 + 0.45 * fbm(nS, x * 0.7 + 50, z * 1.3, 2)), ww = wH * (0.85 + 0.3 * nS(x + 7, z * 0.9));
            let arc = 0;
            prof.forEach((pr, pi) => {
              const xx = x + pr[0] * ww * (1 + (nS(z * 4.1 + pi, x * 3) - 0.5) * 0.3), yy = bedAt(x, z) + pr[1] * hh * (1 + (nS(z * 3.3 + pi * 1.7, x * 2 + 11) - 0.5) * 0.5) - (pi === 0 || pi === NP - 1 ? 0.05 : 0);
              if (pi) arc += Math.hypot((pr[0] - prof[pi - 1][0]) * ww, (pr[1] - prof[pi - 1][1]) * hh);
              Pp.push(xx, yy, z + (pi % 2 ? 0.04 : -0.04)); Uu.push(arc / 1.0, z / 1.0); const kk = pr[2]; Cc.push(kk, kk, kk);
            });
            if (prevOn) for (let pi = 0; pi < NP - 1; pi++) { const a = nv - NP + pi, b = nv + pi; Ix.push(a, b, a + 1, a + 1, b, b + 1); }   // wound so the normals face out
            nv += NP; prevOn = true;
          }
        }
        if (Ix.length) {
          const hg = new THREE.BufferGeometry();
          hg.setAttribute('position', new THREE.Float32BufferAttribute(Pp, 3)); hg.setAttribute('color', new THREE.Float32BufferAttribute(Cc, 3));
          hg.setAttribute('uv', new THREE.Float32BufferAttribute(Uu, 2)); hg.setIndex(Ix); hg.computeVertexNormals();
          const hm = new THREE.Mesh(hg, M('cotton-hedge-' + kind, { color: 0xffffff, map: hedgeTex(kind), vertexColors: true, roughness: 0.95 }));
          hm.castShadow = true; hm.receiveShadow = true; g.add(hm);
          spent += Ix.length / 3;
        }
      }
      g.userData.heightAt = bedAt;
      g.userData.plants = { full: nF, lite: nL, rows, triFull: Math.round(cF), triLite: Math.round(cL), fullRadius: +dF.toFixed(1), liteRadius: +dL.toFixed(1) };
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
      const prof = kind === 'bluebonnet' ? [[0, 0], [0.022, 0.02], [0.026, 0.15], [0.025, 0.32], [0.022, 0.5], [0.017, 0.68], [0.011, 0.84], [0.004, 0.96], [0, 1]] : [[0, 0], [0.01, 0.05], [0.017, 0.3], [0.021, 0.55], [0.019, 0.8], [0.009, 0.96], [0, 1]];
      const lg = new THREE.LatheGeometry(prof.map((p) => new THREE.Vector2(p[0], p[1] * spikeH)), 7).toNonIndexed();
      const p = lg.attributes.position, cc = new Float32Array(p.count * 3), cA = col(fl[Math.floor(rng() * 3)]), cW = col(0xf4f2ea), cG = col(0x6f8a3a), c = new THREE.Color();
      const nf = noise2(Math.floor(rng() * 1e4));
      for (let i = 0; i < p.count; i++) {
        const t = p.getY(i) / spikeH, k = 1 + (nf(p.getX(i) * 160 + t * 40, p.getZ(i) * 160 + t * 13) - 0.5) * 1.1;
        p.setX(i, p.getX(i) * k); p.setZ(i, p.getZ(i) * k);
        if (kind === 'bluebonnet') { mix3(c, cA, cW, smooth(0.72, 0.84, t)); if (t > 0.93) mix3(c, c, cG, 0.4); }
        else { mix3(c, cG, cA, smooth(0.25, 0.6, t)); }
        cc[i * 3] = c.r; cc[i * 3 + 1] = c.g; cc[i * 3 + 2] = c.b;
      }
      lg.setAttribute('color', new THREE.BufferAttribute(cc, 3)); smoothNormals(lg); lg.translate(tx, ty, tz); parts.push(lg);
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
      const count = Math.round(W * D * (flow ? 4.2 : 5.2) * o.density);
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
        const nFl = Math.round(W * D * 2.4 * o.density);
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
