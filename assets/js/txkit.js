/* txkit.js — THE KIT: the things Texas is made of, modelled once in 3D at TRUE SCALE.
 *
 * WHY THIS EXISTS (2026-09-24). Carousel no. 33 rendered every frame in the engine's world and
 * still scored 5.5 on artwork under three recalibrated judges, and the sibling product's scorer
 * gave it 5, for the same reasons each time: capsule people, box houses with black holes for
 * windows, a cream slab for a dock, a low-poly blob for a live oak, tufts on bare dirt. The world
 * was right. The THINGS in it were blockouts, because every run modelled its hero from scratch
 * against a deadline. A pump jack, a substation, a ranch house and a person each take real
 * knowledge of the object to model, and that knowledge belongs in one file a run can call.
 *
 *   import { init } from '@@ASSETS@@/js/txthree.js';
 *   import { initKit } from '@@ASSETS@@/js/txkit.js';
 *   const TXT = init(THREE), K = initKit(THREE, TXT);
 *   const house = K.make('ranch_house', { seed: 3, brick: 0x9a5a3c });
 *   house.position.set(0, 0, -12); TXT.add(R, house); TXT.contact(R, house);
 *   K.list()   // every model: name, family, size [w, h, d] in metres, options
 *
 * CONVENTIONS, every model, no exceptions:
 *   - METRES, y up, origin at the centre of the footprint ON THE GROUND (y = 0 is the base).
 *     K.make centres it, so a builder need not. Two exceptions keep their own origin: a spec
 *     declaring anchor: 'base' (a pole or mast, anchored at its foot), a model publishing
 *     coordinates in userData (heightAt, attach), and one built at caller-given coordinates
 *     (userData.keepOrigin). examples/kit/sizes.py measures all of this.
 *   - The model's FRONT faces +z. A person faces +z, a house's front door is on +z.
 *   - `seed` varies it deterministically: a row of houses is a row of different houses, and the
 *     same row next render. Every option has a default, so K.make(name) always works.
 *   - Real PBR materials through K.mat, shared and cached. Manufactured edges are bevelled
 *     (TXT.roundedBox). Surfaces that have a texture in life get one from K.tex, mapped in METRES
 *     through K.uvBox so a brick is a brick's size at any scale.
 *   - Repeats are instanced or merged. A model returns a THREE.Group with userData.kit = name.
 *   - It casts and receives shadows when added with TXT.add, and TXT.weather grimes it.
 *   - A material that carries a K.tex map takes a WHITE (or near white) base colour, because the
 *     map already carries the colour and the two multiply. Pass the colour to K.tex instead.
 *
 * Families live in assets/js/kit/<family>.js, each `export function install(K, THREE, TXT)`.
 */
import * as people from './kit/people.js';
import * as homes from './kit/homes.js';
import * as trees from './kit/trees.js';
import * as vehicles from './kit/vehicles.js';
import * as power from './kit/power.js';
import * as industry from './kit/industry.js';
import * as civic from './kit/civic.js';
import * as interior from './kit/interior.js';
import * as rural from './kit/rural.js';
import * as landscape from './kit/landscape.js';

const FAMILIES = { people, homes, trees, vehicles, power, industry, civic, interior, rural, landscape };

export function initKit(THREE, TXT) {
  const K = { THREE, TXT, registry: {} };

  /* ---- the registry ------------------------------------------------------------------- */
  K.define = function (name, spec) {
    if (K.registry[name]) throw new Error('txkit: ' + name + ' is defined twice');
    if (!spec || typeof spec.make !== 'function' || !Array.isArray(spec.size))
      throw new Error('txkit: ' + name + ' needs make() and size [w, h, d] in metres');
    K.registry[name] = spec;
  };
  K.make = function (name, opts) {
    const spec = K.registry[name];
    if (!spec) throw new Error('txkit: no model "' + name + '". K.list() names them all');
    const o = Object.assign({ seed: 1 }, spec.options || {}, opts || {});   // `options` are the defaults
    const g = spec.make(o, K.rng(o.seed * 7919 + name.length * 131));
    // THE FOOTPRINT IS CENTRED HERE, not in each builder, because builders that add a lean-to, a
    // yard or a row of bins off one side kept forgetting to. Two kinds keep their own origin: a
    // model declared anchor 'base' (a pole, mast or tower whose arm overhangs), one that
    // publishes coordinates (heightAt, attach points), which a shift would silently invalidate,
    // and one built at coordinates the caller gave it (userData.keepOrigin, as power_line sets
    // when it is handed `structures`).
    if (g.isGroup && spec.anchor !== 'base' && !g.userData.keepOrigin && !g.userData.heightAt && !g.userData.attach) {
      const bb = new THREE.Box3().setFromObject(g);
      const cx = (bb.min.x + bb.max.x) / 2, cz = (bb.min.z + bb.max.z) / 2;
      if (Math.abs(cx) > 0.01 || Math.abs(cz) > 0.01) g.children.forEach((c) => { c.position.x -= cx; c.position.z -= cz; });
    }
    g.userData.kit = name;
    return g;
  };
  K.list = function () {
    return Object.keys(K.registry).sort().map((n) => ({
      name: n, family: K.registry[n].family, size: K.registry[n].size,
      options: K.registry[n].options || {}, note: K.registry[n].note || '' }));
  };
  K.rng = function (seed) { return TXT.rng(seed >>> 0 || 1); };

  /* ---- materials, cached by key --------------------------------------------------------- */
  const MATS = new Map();
  /* THE ONE CACHE KEY every material cache in the kit uses: name, class and every parameter.
   * A cache keyed by name alone hands the first caller's material to every later caller who
   * named it the same, which is how a dusk skyline's lit windows leaked into a daytime one. */
  K.matKey = function (key, params, physical) {
    const norm = {};
    for (const [n, v] of Object.entries(params || {})) {
      norm[n] = v && v.isTexture ? 'tex:' + v.uuid : v && v.isColor ? 'col:' + v.getHexString() : v;
    }
    return key + '|' + (physical ? 'physical' : 'standard') + '|' + JSON.stringify(norm);
  };
  K.mat = function (key, params, physical) {
    // textures and colours by identity, never by value: serialising a texture's image cost about
    // a second per textured material (power builder, 2026-09-24). Normalised BEFORE stringify,
    // because JSON.stringify calls a texture's own toJSON before any replacer sees it.
    const k = K.matKey(key, params, physical);
    if (!MATS.has(k)) {
      const P = Object.assign({ roughness: 0.8, metalness: 0 }, params || {});
      MATS.set(k, physical ? new THREE.MeshPhysicalMaterial(P) : new THREE.MeshStandardMaterial(P));
    }
    return MATS.get(k);
  };
  // named finishes every family reaches for
  K.finish = {
    galvanized: () => K.mat('galv', { color: 0xa9adb0, metalness: 0.85, roughness: 0.42 }),
    steelPaint: (c) => K.mat('steelp', { color: c != null ? c : 0x8d9196, metalness: 0.35, roughness: 0.55 }),
    concrete:   () => K.mat('conc', { color: 0xa39f97, roughness: 0.92, map: K.tex('concrete') }),
    asphalt:    () => K.mat('asph', { color: 0x3b3c3e, roughness: 0.9 }),
    rubber:     () => K.mat('rubber', { color: 0x1c1c1e, roughness: 0.75 }),
    chrome:     () => K.mat('chrome', { color: 0xdfe3e6, metalness: 1, roughness: 0.12 }),
    glass:      (tint) => K.mat('glass', { color: tint != null ? tint : 0x28343c, metalness: 0.2,
                                          roughness: 0.04, clearcoat: 1, clearcoatRoughness: 0.03,
                                          envMapIntensity: 1.6 }, true),
    lamp:       (c, i) => K.mat('lamp', { color: 0x111111, emissive: c != null ? c : 0xffd28a,
                                         emissiveIntensity: i != null ? i : 3.5 }),
    porcelain:  () => K.mat('porc', { color: 0x6a4e3a, roughness: 0.25, metalness: 0 }),
  };

  /* ---- procedural textures, cached, tileable, 1 repeat = `metres` of real surface ------ */
  const TEX = new Map();
  const TEXSPEC = {
    // name: [metres one tile covers, painter]
    brick:      [1.0, paintBrick], shingle: [1.2, paintShingle], siding: [1.2, paintSiding],
    limestone:  [1.6, paintLimestone], concrete: [3.0, paintConcrete], corrugated: [1.0, paintCorrugated],
    bark:       [1.0, paintBark], wood: [1.2, paintWood], stucco: [2.0, paintStucco],
  };
  K.tex = function (name, opts) {
    const k = name + '|' + JSON.stringify(opts || {});
    if (TEX.has(k)) return TEX.get(k);
    const spec = TEXSPEC[name];
    if (!spec) throw new Error('txkit: no texture "' + name + '"');
    const N = 512, c = document.createElement('canvas'); c.width = c.height = N;
    spec[1](c.getContext('2d'), N, K.rng(97 + name.length), opts || {});
    const t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 8; t.userData.metres = spec[0];
    TEX.set(k, t);
    return t;
  };
  /* Box-project UVs in METRES so a texture's tile covers its real size on any face. Call on a
   * geometry after it is built and before it is merged. `metres` defaults to the texture's own. */
  K.uvBox = function (geo, metres) {
    const m = metres || 1, pos = geo.attributes.position, nor = geo.attributes.normal;
    if (!nor) geo.computeVertexNormals();
    const n = geo.attributes.normal, uv = new Float32Array(pos.count * 2);
    for (let i = 0; i < pos.count; i++) {
      const ax = Math.abs(n.getX(i)), ay = Math.abs(n.getY(i)), az = Math.abs(n.getZ(i));
      let u, v;
      if (ay >= ax && ay >= az) { u = pos.getX(i); v = pos.getZ(i); }
      else if (ax >= az) { u = pos.getZ(i); v = pos.getY(i); }
      else { u = pos.getX(i); v = pos.getY(i); }
      uv[i * 2] = u / m; uv[i * 2 + 1] = v / m;
    }
    geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
    return geo;
  };

  /* ---- geometry helpers ----------------------------------------------------------------- */
  // A mesh from geometry + material, positioned; the smallest useful constructor.
  K.mesh = function (geo, mat, x, y, z, parent) {
    const m = new THREE.Mesh(geo, mat); m.position.set(x || 0, y || 0, z || 0);
    if (parent) parent.add(m);
    return m;
  };
  // Box sitting ON y0 (base at y0), optional bevel radius r via TXT.roundedBox.
  K.box = function (w, h, d, mat, x, y0, z, r, parent) {
    const m = r ? TXT.roundedBox(w, h, d, r, mat) : new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
    m.position.set(x || 0, (y0 || 0) + h / 2, z || 0);
    if (parent) parent.add(m);
    return m;
  };
  // Cylinder standing on y0.
  K.cyl = function (rTop, rBot, h, mat, x, y0, z, seg, parent) {
    const m = new THREE.Mesh(new THREE.CylinderGeometry(rTop, rBot, h, seg || 24), mat);
    m.position.set(x || 0, (y0 || 0) + h / 2, z || 0);
    if (parent) parent.add(m);
    return m;
  };
  // A bar between two points (struts, braces, lattice members, conductors when straight).
  K.bar = function (a, b, r, mat, seg, parent) {
    const A = new THREE.Vector3(a[0], a[1], a[2]), B = new THREE.Vector3(b[0], b[1], b[2]);
    const len = A.distanceTo(B);
    const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, len, seg || 6), mat);
    m.position.copy(A).add(B).multiplyScalar(0.5);
    m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), B.clone().sub(A).normalize());
    if (parent) parent.add(m);
    return m;
  };
  // A hanging cable between two points with sag (catenary approximated by a parabola).
  K.cable = function (a, b, sag, r, mat, parent) {
    const pts = [];
    for (let i = 0; i <= 24; i++) {
      const t = i / 24;
      pts.push(new THREE.Vector3(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t - sag * 4 * t * (1 - t),
                                 a[2] + (b[2] - a[2]) * t));
    }
    const m = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 48, r, 5, false), mat);
    if (parent) parent.add(m);
    return m;
  };
  // Instanced copies of one geometry at [x,y,z,rotY,scale] entries.
  K.instances = function (geo, mat, list, parent) {
    const im = new THREE.InstancedMesh(geo, mat, list.length), M = new THREE.Matrix4(),
          q = new THREE.Quaternion(), e = new THREE.Euler(), s = new THREE.Vector3(), p = new THREE.Vector3();
    list.forEach((it, i) => {
      e.set(0, it[3] || 0, 0); q.setFromEuler(e); const k = it[4] || 1; s.set(k, k, k);
      p.set(it[0], it[1], it[2]); M.compose(p, q, s); im.setMatrixAt(i, M);
    });
    im.instanceMatrix.needsUpdate = true;
    if (parent) parent.add(im);
    return im;
  };
  /* Merge meshes that share ONE material into a single mesh (fewer draw calls). Takes meshes
   * already positioned inside `root` (a Group not yet transformed), returns the merged mesh. */
  K.merge = function (meshes, mat) {
    const parts = [];
    let total = 0, hasUV = true;
    meshes.forEach((m) => {
      m.updateMatrix();
      let g = m.geometry.index ? m.geometry.toNonIndexed() : m.geometry.clone();
      g.applyMatrix4(m.matrix);
      if (!g.attributes.normal) g.computeVertexNormals();
      if (!g.attributes.uv) hasUV = false;
      parts.push(g); total += g.attributes.position.count;
    });
    const pos = new Float32Array(total * 3), nor = new Float32Array(total * 3), uv = hasUV ? new Float32Array(total * 2) : null;
    let o = 0;
    parts.forEach((g) => {
      pos.set(g.attributes.position.array, o * 3); nor.set(g.attributes.normal.array, o * 3);
      if (uv) uv.set(g.attributes.uv.array, o * 2);
      o += g.attributes.position.count; g.dispose();
    });
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
    if (uv) geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
    return new THREE.Mesh(geo, mat);
  };

  for (const [fam, mod] of Object.entries(FAMILIES)) {
    if (typeof mod.install !== 'function') continue;
    const before = new Set(Object.keys(K.registry));
    mod.install(K, THREE, TXT);
    Object.keys(K.registry).forEach((n) => { if (!before.has(n)) K.registry[n].family = fam; });
  }
  return K;
}

/* ---- texture painters: tileable, deterministic, drawn in 512 px per tile ----------------- */
function jitter(r, a) { return (r() - 0.5) * 2 * a; }
function shade(hex, k) {
  const c = parseInt(hex.slice(1), 16), f = (v) => Math.max(0, Math.min(255, Math.round(v * k)));
  return 'rgb(' + f(c >> 16) + ',' + f((c >> 8) & 255) + ',' + f(c & 255) + ')';
}
function paintBrick(x, N, r, o) {
  // modular brick 0.203 x 0.057 m + 10 mm mortar => 16 courses per 1 m tile, 4.5 bricks per course
  const base = o.color || '#9a5a3c', mortar = o.mortar || '#b9b0a2';
  x.fillStyle = mortar; x.fillRect(0, 0, N, N);
  const rows = 15, h = N / rows, per = 5, w = N / per;
  for (let j = 0; j < rows; j++) {
    const off = (j % 2) * w / 2;
    for (let i = -1; i <= per; i++) {
      x.fillStyle = shade(base, 0.82 + r() * 0.3);
      x.fillRect(i * w + off + 3, j * h + 3, w - 6, h - 6);
    }
  }
  noise(x, N, r, 0.07);
}
function paintShingle(x, N, r, o) {
  const base = o.color || '#4a4643';
  x.fillStyle = shade(base, 0.7); x.fillRect(0, 0, N, N);
  const rows = 8, h = N / rows;
  for (let j = 0; j < rows; j++) {
    const tabs = 4, w = N / tabs, off = (j % 2) * w / 2;
    for (let i = -1; i <= tabs; i++) {
      x.fillStyle = shade(base, 0.8 + r() * 0.35);
      x.fillRect(i * w + off + 2, j * h, w - 4, h - 5);
    }
    x.fillStyle = 'rgba(0,0,0,0.35)'; x.fillRect(0, j * h + h - 5, N, 5);
  }
  noise(x, N, r, 0.12);
}
function paintSiding(x, N, r, o) {
  const base = o.color || '#d9d2c3', boards = 7, h = N / boards;
  for (let j = 0; j < boards; j++) {
    const g = x.createLinearGradient(0, j * h, 0, j * h + h);
    g.addColorStop(0, shade(base, 0.86)); g.addColorStop(0.15, shade(base, 1.02)); g.addColorStop(1, shade(base, 0.95));
    x.fillStyle = g; x.fillRect(0, j * h, N, h);
    x.fillStyle = 'rgba(0,0,0,0.28)'; x.fillRect(0, j * h, N, 3);
  }
  noise(x, N, r, 0.04);
}
function paintLimestone(x, N, r, o) {
  // Austin/Hill Country cut limestone: irregular ashlar courses, warm cream
  const base = o.color || '#cdbd98', mortar = '#a99d84';
  x.fillStyle = mortar; x.fillRect(0, 0, N, N);
  let y = 0;
  while (y < N) {
    const h = N / (5 + Math.floor(r() * 3)); let xx = -r() * 60;
    while (xx < N) { const w = 60 + r() * 140; x.fillStyle = shade(base, 0.85 + r() * 0.25); x.fillRect(xx + 3, y + 3, w - 6, h - 6); xx += w; }
    y += h;
  }
  noise(x, N, r, 0.1);
}
function paintConcrete(x, N, r, o) {
  x.fillStyle = o.color || '#a39f97'; x.fillRect(0, 0, N, N); noise(x, N, r, 0.1);
  for (let i = 0; i < 40; i++) { x.fillStyle = 'rgba(0,0,0,' + (0.02 + r() * 0.05) + ')';
    x.beginPath(); x.arc(r() * N, r() * N, 4 + r() * 40, 0, 6.3); x.fill(); }
}
function paintCorrugated(x, N, r, o) {
  const base = o.color || '#9fa4a6', ribs = 12, w = N / ribs;
  for (let i = 0; i < ribs; i++) {
    const g = x.createLinearGradient(i * w, 0, i * w + w, 0);
    g.addColorStop(0, shade(base, 0.72)); g.addColorStop(0.5, shade(base, 1.08)); g.addColorStop(1, shade(base, 0.72));
    x.fillStyle = g; x.fillRect(i * w, 0, w, N);
  }
  noise(x, N, r, 0.05);
}
function paintBark(x, N, r, o) {
  x.fillStyle = o.color || '#4b3f35'; x.fillRect(0, 0, N, N);
  for (let i = 0; i < 90; i++) { x.strokeStyle = 'rgba(0,0,0,' + (0.2 + r() * 0.3) + ')'; x.lineWidth = 2 + r() * 6;
    const x0 = r() * N; x.beginPath(); x.moveTo(x0, 0); x.bezierCurveTo(x0 + jitter(r, 30), N / 3, x0 + jitter(r, 30), 2 * N / 3, x0 + jitter(r, 20), N); x.stroke(); }
  noise(x, N, r, 0.12);
}
function paintWood(x, N, r, o) {
  const base = o.color || '#8a6a4a', boards = 6, w = N / boards;
  for (let i = 0; i < boards; i++) {
    x.fillStyle = shade(base, 0.8 + r() * 0.3); x.fillRect(i * w, 0, w, N);
    for (let k = 0; k < 14; k++) { x.strokeStyle = 'rgba(0,0,0,' + (0.05 + r() * 0.1) + ')'; x.lineWidth = 1 + r() * 2;
      const xx = i * w + r() * w; x.beginPath(); x.moveTo(xx, 0); x.lineTo(xx + jitter(r, 6), N); x.stroke(); }
    x.fillStyle = 'rgba(0,0,0,0.35)'; x.fillRect(i * w, 0, 3, N);
  }
}
function paintStucco(x, N, r, o) { x.fillStyle = o.color || '#d8cdb8'; x.fillRect(0, 0, N, N); noise(x, N, r, 0.08); }
function noise(x, N, r, a) {
  const im = x.getImageData(0, 0, N, N), d = im.data;
  for (let i = 0; i < d.length; i += 4) { const k = 1 + (r() - 0.5) * 2 * a; d[i] *= k; d[i + 1] *= k; d[i + 2] *= k; }
  x.putImageData(im, 0, 0);
}
