#!/usr/bin/env node
/* kit_hot_check.mjs: the geometry check for the kit's hot section (assets/js/kit/industry.js, installHot), the
 * turbine_blade and turbine_blisk the weekly machine pass lifted on 2026-11-26 from carousel no. 88's chassis.
 *
 *   node scripts/carousel/kit_hot_check.mjs              exit 0 when every check holds
 *   node scripts/carousel/kit_hot_check.mjs --self-test  replays the defect it exists for and must see it fail
 *
 * THE DEFECT. No. 88's chassis blisk published userData.bladeAt(i) as (sin a, 0, cos a) * R while it built blade i
 * by rotating a pivot through -a, so every published tip was the built blade mirrored in x, and a frame placing an
 * accent by bladeAt landed on the wrong blade (queue blisk-bladeAt-mirrored). The kit model derives the tip and the
 * blade from one basis and throws at make() if they disagree. This script proves both halves: the built model's
 * published points sit on the geometry it drew, and a copy of the model with the old mirrored tip is refused.
 *
 * It runs in node with three.js and no browser: the canvas texture painter is replaced by a stub, because the
 * check is about where geometry is, never what it looks like. The render proof is examples/kit/build.py.
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath, pathToFileURL } from 'url';

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const THREE = await import(pathToFileURL(path.join(REPO, 'assets', 'js', 'three.module.min.js')).href);
const SRC = fs.readFileSync(path.join(REPO, 'assets', 'js', 'kit', 'industry.js'), 'utf8');

function installerBody(src) {
  const a = src.indexOf('function installHot(K, THREE, TXT, H) {');
  if (a < 0) throw new Error('installHot not found in assets/js/kit/industry.js');
  const open = src.indexOf('{', a);
  let depth = 0;
  for (let i = open; i < src.length; i++) {
    if (src[i] === '{') depth++;
    else if (src[i] === '}') { depth--; if (depth === 0) return src.slice(open + 1, i); }
  }
  throw new Error('installHot is not closed');
}

function kit(body) {
  const K = { registry: {} };
  K.define = (n, spec) => { K.registry[n] = spec; };
  K.mat = (key, p) => new THREE.MeshStandardMaterial(Object.assign({}, p, { map: null }));
  K.make = (n, o) => { const s = K.registry[n]; return s.make(Object.assign({ seed: 1 }, s.options, o || {})); };
  const TXT = {
    roundedBox: (w, h, d, r, m) => new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m),
    lathe: (prof, m, o) => new THREE.Mesh(new THREE.LatheGeometry(prof.map((p) => new THREE.Vector2(p[0], p[1])), (o && o.segments) || 64), m),
  };
  const H = { ctex: () => null, speckle: () => {} };
  new Function('K', 'THREE', 'TXT', 'H', body)(K, THREE, TXT, H);
  return K;
}

function nearest(mesh, p) {
  mesh.updateMatrixWorld(true);
  const a = mesh.geometry.attributes.position, v = new THREE.Vector3();
  let best = Infinity;
  for (let i = 0; i < a.count; i++) { v.fromBufferAttribute(a, i).applyMatrix4(mesh.matrixWorld); best = Math.min(best, v.distanceTo(p)); }
  return best;
}

function check(body) {
  const K = kit(body), bad = [];
  // the blisk: every published tip lies in the direction its own built blade does, and a flagged leading edge faces up
  const d = K.make('turbine_blisk', { flag: 0 });
  d.updateMatrixWorld(true);
  const blades = [];
  d.traverse((m) => { if (m.isMesh && m.geometry.type === 'BufferGeometry' && !m.geometry.parameters) blades.push(m); });
  const nb = K.registry.turbine_blisk.options.blades;
  if (blades.length !== nb) bad.push(`turbine_blisk built ${blades.length} blades, options say ${nb}`);
  blades.forEach((m, i) => {
    const c = new THREE.Box3().setFromObject(m).getCenter(new THREE.Vector3()).setY(0).normalize();
    const t = d.userData.bladeAt(i).setY(0).normalize();
    if (c.dot(t) < 0.98) bad.push(`turbine_blisk bladeAt(${i}) points away from blade ${i} (dot ${c.dot(t).toFixed(3)})`);
  });
  const mid = d.userData.midY, le = d.userData.leAt(0, 0.5);
  if (!(le.y > mid)) bad.push(`turbine_blisk leading edge sits under the disc's mid plane (${le.y.toFixed(4)} <= ${mid.toFixed(4)}), so a flag faces the ground`);
  // the blade: leAt is on the drawn surface, the flaw notches the leading edge back, the root stands on the ground
  const b = K.make('turbine_blade', { flaw: 0.55 }), plain = K.make('turbine_blade', {});
  const foil = (g) => g.children.find((m) => m.isMesh && m.geometry.type === 'BufferGeometry' && !m.geometry.parameters && m.geometry.index && m.geometry.attributes.uv);
  for (const f of [0.2, 0.5, 0.8]) { const e = nearest(foil(plain), plain.userData.leAt(f)); if (e > 1e-5) bad.push(`turbine_blade leAt(${f}) is ${e.toExponential(2)} m off the airfoil it drew`); }
  const back = b.userData.flawAt.x - plain.userData.leAt(0.55).x;
  if (!(back > 0)) bad.push(`turbine_blade flaw did not push the leading edge back (shift ${back.toExponential(2)} m)`);
  const bb = new THREE.Box3().setFromObject(b);
  if (Math.abs(bb.min.y) > 0.002) bad.push(`turbine_blade base is at y ${bb.min.y.toFixed(4)}, not on the ground`);
  const want = K.registry.turbine_blade.size, got = bb.getSize(new THREE.Vector3()).toArray();
  got.forEach((v, k) => { if (v > want[k] * 1.1 + 0.005) bad.push(`turbine_blade measures ${v.toFixed(3)} m on axis ${k}, declared ${want[k]}`); });
  return bad;
}

const body = installerBody(SRC);
if (process.argv.includes('--self-test')) {
  // replay no. 88's mirrored tip inside the kit model: publish the tip with x negated, as the chassis did
  const needle = 'tips.push(A.leAt(1).clone().lerp(A.teAt(1), 0.5).applyMatrix4(B));';
  if (!body.includes(needle)) { console.error('self-test: the tip line moved; update the replay'); process.exit(2); }
  const mirrored = body.replace(needle, 'tips.push(A.leAt(1).clone().lerp(A.teAt(1), 0.5).applyMatrix4(B).multiply(new THREE.Vector3(-1, 1, 1)));');
  let refused = false;
  try { check(mirrored); } catch (e) { refused = /is built away from bladeAt/.test(String(e.message)); }
  const upside = check(body.replace('new THREE.Vector3(0, -1, 0), tang', 'new THREE.Vector3(0, 1, 0), tang'));
  const flat = check(body.replace('if (s < 0.22) a += flawD', 'if (false) a += flawD'));
  const clean = check(body);
  const cases = [
    ['the mirrored tip of no. 88 is refused at make()', refused],
    ['a blisk whose leading edges face the ground is reported', upside.some((m) => /faces the ground/.test(m))],
    ['a flaw that notches nothing is reported', flat.some((m) => /flaw did not push/.test(m))],
    ['the shipped model is clean', clean.length === 0],
  ];
  cases.forEach(([n, ok]) => console.log((ok ? 'ok   ' : 'FAIL ') + n));
  if (clean.length) clean.forEach((m) => console.log('     ' + m));
  process.exit(cases.every((c) => c[1]) ? 0 : 1);
}
const bad = check(body);
bad.forEach((m) => console.log('FAIL ' + m));
console.log(bad.length ? `kit_hot_check: ${bad.length} problem(s)` : 'kit_hot_check: turbine_blade and turbine_blisk hold');
process.exit(bad.length ? 1 : 0);
