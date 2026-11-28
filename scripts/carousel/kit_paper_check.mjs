#!/usr/bin/env node
/* kit_paper_check.mjs: the count check for the kit's paper section (assets/js/kit/interior.js, installPaper), the
 * wrapped_ream and ream_pile the weekly machine pass lifted on 2026-11-27 from carousel no. 89's chassis.
 *
 *   node scripts/carousel/kit_paper_check.mjs              exit 0 when every check holds
 *   node scripts/carousel/kit_paper_check.mjs --self-test  replays the defects it exists for and must see them fail
 *
 * WHY. A ream pile is a figure: no. 89 drew one sheet per million dollars, and its frame 5 printed the ratio of two
 * piles' projected heights to four places. So a pile's height must be EXACTLY its sheets x 0.1 mm. The chassis's
 * wrapped ream modelled its folded end flaps as boxes 0.4 mm proud of its top, and frame 5 laid three loose sheets ON
 * the counted block, so each drawn pile stood taller than its count. And the engine's surface pass speckled every paper
 * material that did not opt out (queue surface-pass-speckles-paper). This proves, for piles across the sizes no. 89
 * drew and every top and face option, that the count, the split and the height agree, that face turns the end or the
 * side to +z, and that every material opts out of the surface pass; the self-test replays the proud flap, the three
 * extra sheets and a missing opt-out, and must see each one reported.
 *
 * It runs in node with three.js and no browser: textures are stubbed, because the check is about where geometry is.
 * The render proof is examples/kit/build.py.
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath, pathToFileURL } from 'url';

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const THREE = await import(pathToFileURL(path.join(REPO, 'assets', 'js', 'three.module.min.js')).href);
const SRC = fs.readFileSync(path.join(REPO, 'assets', 'js', 'kit', 'interior.js'), 'utf8');
const SHEET = 0.0001;   // 20 lb bond, the drawing rule the models declare

function installerBody(src) {
  const a = src.indexOf('function installPaper(K, THREE, TXT, H) {');
  if (a < 0) throw new Error('installPaper not found in assets/js/kit/interior.js');
  const open = src.indexOf('{', a);
  let depth = 0;
  for (let i = open; i < src.length; i++) {
    if (src[i] === '{') depth++;
    else if (src[i] === '}') { depth--; if (depth === 0) return src.slice(open + 1, i); }
  }
  throw new Error('installPaper is not closed');
}

function rng(seed) { let t = seed >>> 0 || 1; return () => { t = (t + 0x6D2B79F5) >>> 0; let r = Math.imul(t ^ (t >>> 15), 1 | t); r ^= r + Math.imul(r ^ (r >>> 7), 61 | r); return ((r ^ (r >>> 14)) >>> 0) / 4294967296; }; }

function kit(body) {
  const K = { registry: {} };
  K.define = (n, spec) => { K.registry[n] = spec; };
  K.make = (n, o) => {
    const s = K.registry[n], opts = Object.assign({ seed: 1 }, s.options, o || {});
    const g = s.make(opts, rng(opts.seed * 7919 + n.length * 131)); g.userData.kit = n; return g;
  };
  const H = {
    ltex: () => null,
    mat: (key, p, phys) => { const m = phys ? new THREE.MeshPhysicalMaterial(p) : new THREE.MeshStandardMaterial(p); m.name = key; return m; },
  };
  new Function('K', 'THREE', 'TXT', 'H', body)(K, THREE, {}, H);
  return K;
}

function check(body) {
  const K = kit(body), bad = [];
  for (const n of [1, 3, 4, 499, 500, 501, 1000, 1947, 4286]) {
    for (const top of ['torn', 'block', 'wrapped']) {
      for (const face of ['end', 'side']) {
        const p = K.make('ream_pile', { sheets: n, top, face, seed: n % 7 + 1 }), u = p.userData, tag = `ream_pile ${n} ${top} ${face}`;
        if (u.sheets !== n || u.reams * 500 + u.loose !== n) bad.push(`${tag}: holds ${u.reams} reams and ${u.loose} loose, not ${n} sheets`);
        if (p.children.length !== u.reams + (u.loose ? 1 : 0)) bad.push(`${tag}: drew ${p.children.length} pieces for ${u.reams} reams and ${u.loose} loose`);
        const bb = new THREE.Box3().setFromObject(p), want = n * SHEET;
        if (Math.abs(bb.min.y) > 1e-6) bad.push(`${tag}: base at y ${bb.min.y.toExponential(2)}, not on the ground`);
        if (Math.abs(bb.max.y - want) > 1e-6) bad.push(`${tag}: drawn ${(bb.max.y * 1000).toFixed(3)} mm tall for ${n} sheets (${(want * 1000).toFixed(3)} mm), so the picture is not its count`);
        if (Math.abs(u.top - want) > 1e-6) bad.push(`${tag}: userData.top ${u.top} is not ${want}`);
        p.traverse((m) => {
          if (!m.isMesh) return;
          for (const mt of [].concat(m.material)) if (!mt.userData || mt.userData.txSurface !== false) bad.push(`${tag}: material ${mt.name || '?'} takes the surface pass, which speckles paper`);
        });
      }
    }
  }
  for (const face of ['end', 'side']) {
    const s = new THREE.Box3().setFromObject(K.make('wrapped_ream', { face })).getSize(new THREE.Vector3());
    if (face === 'end' ? !(s.z > s.x) : !(s.x > s.z)) bad.push(`wrapped_ream face ${face} does not turn its ${face} to +z (x ${s.x.toFixed(3)}, z ${s.z.toFixed(3)})`);
  }
  return [...new Set(bad)];
}

const body = installerBody(SRC);
if (process.argv.includes('--self-test')) {
  const must = (needle) => { if (!body.includes(needle)) { console.error('self-test: a replay anchor moved; update it: ' + needle); process.exit(2); } return needle; };
  // no. 89's chassis: folded end flaps as boxes standing 0.4 mm proud of the wrapped ream's top
  const a1 = must('wrap.position.y = sh + bh / 2; body.add(wrap);');
  const proud = check(body.replace(a1, a1 + ' const fl = new THREE.Mesh(new THREE.BoxGeometry(W * 0.98, 0.0008, D * 0.36), top); fl.position.set(0, h + 0.0004, D * 0.31); body.add(fl);'));
  // no. 89's frame 5: three loose sheets laid on top of the counted block rather than counted in it
  const a2 = must('const top = block(body, n - fan, 0);');
  const extra = check(body.replace(a2, 'const top = block(body, n, 0);'));
  // a paper material that does not opt out of the surface pass
  const a3 = must('m.userData.txSurface = false;');
  const speck = check(body.replace(a3, ''));
  const clean = check(body);
  const cases = [
    ['the proud end flaps of no. 89\'s chassis are reported', proud.some((m) => /so the picture is not its count/.test(m))],
    ['three sheets laid on the counted block are reported', extra.some((m) => /so the picture is not its count/.test(m))],
    ['a paper material taking the surface pass is reported', speck.some((m) => /takes the surface pass/.test(m))],
    ['the shipped models are clean', clean.length === 0],
  ];
  cases.forEach(([n, ok]) => console.log((ok ? 'ok   ' : 'FAIL ') + n));
  if (clean.length) clean.slice(0, 12).forEach((m) => console.log('     ' + m));
  process.exit(cases.every((c) => c[1]) ? 0 : 1);
}
const bad = check(body);
bad.slice(0, 40).forEach((m) => console.log('FAIL ' + m));
console.log(bad.length ? `kit_paper_check: ${bad.length} problem(s)` : 'kit_paper_check: wrapped_ream and ream_pile hold their count, face and surface opt-out');
process.exit(bad.length ? 1 : 0);
