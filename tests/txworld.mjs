/* txworld.mjs — the engine's world, rendered in Chromium and measured in pixels.
 *
 * WHY THIS EXISTS. On 2026-09-26 a judge of carousel no. 34 named the horizon band in every one of
 * five rounds, as sea in the first two, and no gate saw it. The cause was in the engine rather than
 * any deck. three.js mixes fog in after tone mapping, with a fog colour that is never tone mapped,
 * while the sky dome IS tone mapped. So a fully fogged ground printed the raw haze, a flat strip
 * about 40 levels darker than the sky right above it, with a hard edge on the horizon. The fix, PR
 * 368, mixes every fogged material toward the sky's own horizon colour in its view direction, tone
 * mapped the same way (txthree.js, installSkyFog).
 *
 * A fix that is not measured does not hold, which this repo has learned twice. So this renders a
 * world through the real engine in a real browser, reads the pixels across the horizon and fails
 * on a step. It looks toward the sun in golden hour, where the old mismatch was worst, because
 * there the sky above the horizon carries the glow and the old fog below it did not.
 *
 * It also proves the other half: a frame that calls TXT.sky and points its camera at the ground
 * says so on the console (TXT.NO_SKY), which print_ban.py reads off the render report.
 *
 *     node tests/txworld.mjs
 *     TXWORLD_ENGINE=/path/to/old/txthree.js node tests/txworld.mjs    # prove it goes red
 */
import { chromium } from 'playwright';
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const ASSETS = join(ROOT, 'assets', 'js');
const ENGINE = process.env.TXWORLD_ENGINE ? resolve(process.env.TXWORLD_ENGINE) : join(ASSETS, 'txthree.js');
// The largest row to row step allowed across the horizon, in levels of 255 on the mean of a wide
// strip. Measured on 2026-09-26: the engine before the fix steps 26.6 levels here, on the horizon
// row itself, and the fixed engine 2.5.
const MAX_STEP = 6;
// The least the lower band may change when the ground is hidden, in levels of 255. Measured on
// 2026-09-26: 37.2 and 18.8 through this engine, 24.4 and 44.0 through the one before PR 368, for
// the 900 m and the 12 km ground. A ground that never rendered changes it by nothing.
const MIN_GROUND_DIFF = 5;

let failures = 0;
const check = (label, cond, extra = '') => {
  console.log(`  ${cond ? 'ok  ' : 'FAIL'}  ${label}${cond ? '' : '  ' + extra}`);
  if (!cond) failures++;
};

const page_html = (scene) => `<!doctype html><html><head><meta charset="utf-8">
<style>html,body{margin:0;background:#000}canvas{display:block;width:540px;height:675px}</style></head>
<body><canvas id="c" width="1080" height="1350"></canvas>
<script type="module">
  const T = await import(${JSON.stringify(pathToFileURL(join(ASSETS, 'three.module.min.js')).href)});
  const TXT = (await import(${JSON.stringify(pathToFileURL(ENGINE).href)})).init(T) || window.TXT;
  window.__result = null;
  try { window.__result = await (${scene})(T, TXT, document.getElementById('c')); }
  catch (e) { window.__result = { error: String(e && e.stack || e) }; }
</script></body></html>`;

// Toward the sun in golden hour, a level camera at 2 m, a caliche ground: the horizon sits at
// mid frame, and the step across it is measured on the middle three fifths of the width. Run twice:
// a 900 m caliche ground whose edge lies inside the far plane, and a 12 km ground like no. 34's
// frame 1, which the default 1 km far plane cuts off a few rows under the horizon. The 12 km one is
// the flat ground: a 12 km surface ground, viewed from 2 m, shows a step about 40 rows under the
// horizon and a dark foreground on every engine measured, the one before the fix included, which is
// a different defect from the one this test holds (2026-09-26).
const HORIZON = (size, surface) => `async (T, TXT, cv) => {
  const W = Object.assign({}, TXT.worlds.goldenHour);
  const R = TXT.setup(cv, { w: 540, h: 675, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 40 });
  const s = TXT.sunDir(W), az = new T.Vector3(s.x, 0, s.z).normalize();
  TXT.frame(R, { from: [0, 2, 0], look: [az.x * 100, 2, az.z * 100] });
  TXT.sky(R, W);
  TXT.rig(R, { key: Object.assign({}, W.rig.key, { pos: [s.x * 60, Math.max(s.y * 60, 6), s.z * 60] }),
               fill: W.rig.fill, ambient: W.rig.ambient });
  const G = TXT.ground(R, ${surface ? `{ surface: 'caliche', size: ${size}, tile: 5 }` : `{ size: ${size} }`});
  const shot = await TXT.snapshot(R);
  const gl = R.renderer.getContext(), Wd = gl.drawingBufferWidth, H = gl.drawingBufferHeight;
  const x0 = Math.floor(Wd * 0.2), x1 = Math.floor(Wd * 0.8), n = x1 - x0, mid = Math.floor(H / 2);
  const buf = new Uint8Array(n * 4), rows = [];
  for (let y = mid - 90; y <= mid + 90; y++) {
    gl.readPixels(x0, y, n, 1, gl.RGBA, gl.UNSIGNED_BYTE, buf);
    let sum = 0; for (let i = 0; i < buf.length; i += 4) sum += (buf[i] + buf[i + 1] + buf[i + 2]) / 3;
    rows.push(sum / n);
  }
  let step = 0, at = 0;
  for (let i = 1; i < rows.length; i++) { const d = Math.abs(rows[i] - rows[i - 1]); if (d > step) { step = d; at = i; } }
  // THE GROUND IS REALLY THERE (Codex, PR 369): without it the dome alone is a smooth, non-black frame
  // and every check above would pass having measured no seam. A ray through the lower band must meet
  // the ground plane, and the band's pixels must change when the ground is hidden.
  const band = (y0, y1) => { const out = new Uint8Array(n * 4 * (y1 - y0)); gl.readPixels(x0, y0, n, y1 - y0, gl.RGBA, gl.UNSIGNED_BYTE, out); return out; };
  const withGround = band(mid - 90, mid - 30);
  const rc = new T.Raycaster(); rc.setFromCamera(new T.Vector2(0, ((mid - 60) + 0.5) / H * 2 - 1), R.camera);
  const groundHit = rc.intersectObject(G, true).length > 0;
  G.visible = false; R.renderer.render(R.scene, R.camera);
  const without = band(mid - 90, mid - 30);
  G.visible = true; R.renderer.render(R.scene, R.camera);
  let diff = 0, cnt = 0;
  for (let i = 0; i < withGround.length; i += 4) { for (let c = 0; c < 3; c++) diff += Math.abs(withGround[i + c] - without[i + c]); cnt += 3; }
  return { ok: shot.ok, step, at: at - 90, top: rows[rows.length - 1], bottom: rows[0],
           chunk: T.ShaderChunk.fog_fragment.includes('txSkyFog'), far: R.camera.far,
           groundHit, groundDiff: diff / cnt };
}`;

// The same world with the camera looking straight down at the ground: no sky in frame.
const GROUND_ONLY = `async (T, TXT, cv) => {
  const W = Object.assign({}, TXT.worlds.goldenHour);
  // A closed shelter around a camera at 1.6 m: a roof and four walls, 3 by 3 by 2.6 m. Covers all
  // of the sky above the camera, where an interior covers 0.8 and a carport roof alone 0.59.
  const shelter = (mat) => {
    const S = new T.Group(), m = mat || new T.MeshStandardMaterial({ color: 0x333333 });
    const p = (w, h, d, x, y, z) => { const b = new T.Mesh(new T.BoxGeometry(w, h, d), m); b.position.set(x, y, z); S.add(b); };
    p(3, 0.1, 3, 0, 2.6, 0); p(0.1, 2.6, 3, -1.5, 1.3, 0); p(0.1, 2.6, 3, 1.5, 1.3, 0);
    p(3, 2.6, 0.1, 0, 1.3, -1.5); p(3, 2.6, 0.1, 0, 1.3, 1.5);
    return S;
  };
  const R = TXT.setup(cv, { w: 540, h: 675, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 40 });
  TXT.frame(R, { from: [0, 40, 0], look: [0, 0, -0.01] });
  TXT.sky(R, W);
  TXT.rig(R, { key: Object.assign({}, W.rig.key, { pos: [20, 40, 20] }), ambient: W.rig.ambient });
  TXT.ground(R, { surface: 'caliche', size: 900, tile: 5 });
  await TXT.snapshot(R);
  // the same camera over a deliberate interior is a room, and the test's question 3 accepts it
  const Rm = TXT.setup(cv, { w: 540, h: 675, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 40 });
  TXT.frame(Rm, { from: [0, 3, 0], look: [0, 0, -0.01] });
  TXT.sky(Rm, W); TXT.interior(Rm, {});
  TXT.rig(Rm, { key: Object.assign({}, W.rig.key, { pos: [2, 6, 2] }), ambient: W.rig.ambient });
  const before = window.__roomErrors = [];
  const orig = console.error; console.error = (...a) => { before.push(String(a[0])); orig.apply(console, a); };
  await TXT.snapshot(Rm);
  console.error = orig;
  // and the open camera again, now inside a shelter the frame built, walls and a roof: inside, not a void
  const Rr = TXT.setup(cv, { w: 540, h: 675, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 40 });
  TXT.frame(Rr, { from: [0, 1.6, 0], look: [0, 0, -0.01] });
  TXT.sky(Rr, W);
  TXT.rig(Rr, { key: Object.assign({}, W.rig.key, { pos: [4, 8, 4] }), ambient: W.rig.ambient });
  TXT.ground(Rr, { surface: 'caliche', size: 900, tile: 5 });
  Rr.scene.add(shelter());
  const roofErrors = [];
  const orig2 = console.error; console.error = (...a) => { roofErrors.push(String(a[0])); orig2.apply(console, a); };
  await TXT.snapshot(Rr);
  console.error = orig2;
  // an orthographic camera pitched 5 degrees down: its rays are parallel and every one points under
  // the horizon, so it shows no sky (Codex, PR 369: the first cut-off let anything under 11.5 through)
  const Ro = TXT.setup(cv, { w: 540, h: 675, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 40 });
  TXT.frame(Ro, { from: [0, 30, 0], look: [0, 30, -100] });
  TXT.sky(Ro, W);
  TXT.rig(Ro, { key: Object.assign({}, W.rig.key, { pos: [20, 40, 20] }), ambient: W.rig.ambient });
  TXT.ground(Ro, { surface: 'caliche', size: 900, tile: 5 });
  const oc = new T.OrthographicCamera(-40, 40, 50, -50, 0.1, 2000);
  oc.position.set(0, 30, 0); oc.lookAt(0, 30 - 100 * Math.tan(5 * Math.PI / 180), -100); oc.updateMatrixWorld();
  Ro.camera = oc;
  const orthoErrors = [];
  const orig3 = console.error; console.error = (...a) => { orthoErrors.push(String(a[0])); orig3.apply(console, a); };
  await TXT.snapshot(Ro);
  console.error = orig3;
  // a 50 degree camera zoomed out to 0.5 and pitched 45 degrees down: three.js projects a field of
  // 2 atan(tan(25) / 0.5), about 86 degrees, so no sky reaches the frame. Dividing the angle by the
  // zoom made it 100 degrees and found sky (Codex, PR 369).
  const Rz = TXT.setup(cv, { w: 540, h: 675, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 50 });
  TXT.frame(Rz, { from: [0, 30, 0], look: [0, 0, -30] });
  TXT.sky(Rz, W);
  TXT.rig(Rz, { key: Object.assign({}, W.rig.key, { pos: [20, 40, 20] }), ambient: W.rig.ambient });
  TXT.ground(Rz, { surface: 'caliche', size: 900, tile: 5 });
  Rz.camera.zoom = 0.5; Rz.camera.updateProjectionMatrix();
  const zoomErrors = [];
  const orig4 = console.error; console.error = (...a) => { zoomErrors.push(String(a[0])); orig4.apply(console, a); };
  await TXT.snapshot(Rz);
  console.error = orig4;
  // a room built with TXT.interior and a camera that has left it, looking straight down at the
  // ground 40 m away: the room is in the scene and not in the frame, so it exempts nothing
  // (Codex, PR 369: the first cut exempted any frame that had called TXT.interior).
  const Rx = TXT.setup(cv, { w: 540, h: 675, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 40 });
  TXT.frame(Rx, { from: [40, 30, 40], look: [40, 0, 40.01] });
  TXT.sky(Rx, W); TXT.interior(Rx, {});
  TXT.rig(Rx, { key: Object.assign({}, W.rig.key, { pos: [42, 40, 42] }), ambient: W.rig.ambient });
  const outsideErrors = [];
  const orig5 = console.error; console.error = (...a) => { outsideErrors.push(String(a[0])); orig5.apply(console, a); };
  await TXT.snapshot(Rx);
  console.error = orig5;
  const capture = async (fn) => {
    const out = [], orig = console.error;
    console.error = (...a) => { out.push(String(a[0])); orig.apply(console, a); };
    try { await fn(); } finally { console.error = orig; }
    return out;
  };
  const world = (fov) => {
    const Rn = TXT.setup(cv, { w: 540, h: 675, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov });
    return Rn;
  };
  const dress = (Rn, key) => {
    TXT.sky(Rn, W);
    TXT.rig(Rn, { key: Object.assign({}, W.rig.key, { pos: key }), ambient: W.rig.ambient });
    TXT.ground(Rn, { surface: 'caliche', size: 900, tile: 5 });
  };
  // a portrait camera rolled 90 degrees and pitched 18 down: its short side now runs vertically,
  // half of 32.5 degrees, so every corner ray is under the horizon. Reading pitch alone found 0.054
  // sky in it (Codex, PR 369).
  const Rt = world(40);
  Rt.camera.up.set(1, 0, 0);
  TXT.frame(Rt, { from: [0, 30, 0], look: [0, 30 - 100 * Math.tan(18 * Math.PI / 180), -100] });
  dress(Rt, [20, 40, 20]);
  const rollErrors = await capture(() => TXT.snapshot(Rt));
  // a shelter whose parent group is hidden: the renderer draws none of it, so it is no shelter
  // (Codex, PR 369)
  const Rh = world(40);
  TXT.frame(Rh, { from: [0, 1.6, 0], look: [0, 0, -0.01] });
  dress(Rh, [4, 8, 4]);
  const shed = new T.Group(); shed.visible = false;
  shed.add(shelter()); Rh.scene.add(shed);
  const hiddenErrors = await capture(() => TXT.snapshot(Rh));
  // a preview pointed at the ground, then the kept frame at the horizon, on the same renderer: its
  // last snapshot is its verdict, so the kept one withdraws the preview's line (Codex, PR 369)
  const Rp = world(40);
  TXT.frame(Rp, { from: [0, 30, 0], look: [0, 0, -0.01] });
  dress(Rp, [20, 40, 20]);
  const previewErrors = await capture(async () => {
    await TXT.snapshot(Rp);
    TXT.frame(Rp, { from: [0, 2, 0], look: [0, 2, -100] });
    await TXT.snapshot(Rp);
  });
  // a preview at the ground on one renderer, and the kept frame at the horizon on another: the page's
  // last snapshot is its verdict, so the kept one withdraws the preview's line (Codex, PR 369)
  const Ra = world(40), Rb = world(40);
  TXT.frame(Ra, { from: [0, 30, 0], look: [0, 0, -0.01] }); dress(Ra, [20, 40, 20]);
  TXT.frame(Rb, { from: [0, 2, 0], look: [0, 2, -100] }); dress(Rb, [20, 40, 20]);
  const crossErrors = await capture(async () => { await TXT.snapshot(Ra); await TXT.snapshot(Rb); });
  // a dome hidden before the kept snapshot: the camera faces the horizon and the sky is not drawn
  const Rd = world(40);
  TXT.frame(Rd, { from: [0, 2, 0], look: [0, 2, -100] });
  const dome = TXT.sky(Rd, W);
  TXT.rig(Rd, { key: Object.assign({}, W.rig.key, { pos: [20, 40, 20] }), ambient: W.rig.ambient });
  TXT.ground(Rd, { surface: 'caliche', size: 900, tile: 5 });
  dome.visible = false;
  const domeErrors = await capture(() => TXT.snapshot(Rd));
  // a shelter at zero opacity: a ray still meets it and the pixels show nothing, so it is no shelter
  const Rg = world(40);
  TXT.frame(Rg, { from: [0, 1.6, 0], look: [0, 0, -0.01] }); dress(Rg, [4, 8, 4]);
  Rg.scene.add(shelter(new T.MeshStandardMaterial({ transparent: true, opacity: 0 })));
  const glassErrors = await capture(() => TXT.snapshot(Rg));
  // an option that once skipped the check is ignored: the kept snapshot is always judged
  const Rs = world(40);
  TXT.frame(Rs, { from: [0, 30, 0], look: [0, 0, -0.01] }); dress(Rs, [20, 40, 20]);
  const optErrors = await capture(() => TXT.snapshot(Rs, { skyCheck: false }));
  // THE CAMERA'S LAYERS (Codex, PR 369). The renderer draws only what shares a layer with the
  // camera, and a ray, a room or a dome it doesn't draw answers nothing. First the whole world on
  // layer 1 and a shelter on layer 0, which the camera never shows: looking down, that is a top-down
  // frame. Then the same shelter moved onto layer 1, where it is a shelter, and the kept frame
  // withdraws.
  const Rl = world(40);
  TXT.frame(Rl, { from: [0, 1.6, 0], look: [0, 0, -0.01] }); dress(Rl, [4, 8, 4]);
  Rl.scene.traverse((o) => o.layers.set(1)); Rl.camera.layers.set(1);
  const hut = shelter(); Rl.scene.add(hut);
  const layerErrors = await capture(async () => {
    await TXT.snapshot(Rl); hut.traverse((o) => o.layers.set(1)); await TXT.snapshot(Rl); });
  // a dome on a layer the camera doesn't render: facing the horizon, the frame shows no sky
  const Rv = world(40);
  TXT.frame(Rv, { from: [0, 2, 0], look: [0, 2, -100] }); dress(Rv, [20, 40, 20]);
  Rv.scene.traverse((o) => { if (!(o.userData && o.userData.txSky)) o.layers.set(1); }); Rv.camera.layers.set(1);
  const veilErrors = await capture(() => TXT.snapshot(Rv));
  // a room on a layer the camera doesn't render: a camera standing in it, looking down, shows no room
  const Rw = world(40);
  TXT.frame(Rw, { from: [0, 3, 0], look: [0, 0, -0.01] });
  TXT.sky(Rw, W); TXT.interior(Rw, {});
  TXT.rig(Rw, { key: Object.assign({}, W.rig.key, { pos: [2, 6, 2] }), ambient: W.rig.ambient });
  Rw.scene.traverse((o) => o.layers.set(1)); Rw.room.traverse((o) => o.layers.set(0)); Rw.camera.layers.set(1);
  const wallErrors = await capture(() => TXT.snapshot(Rw));
  const cover = (Rn) => (typeof TXT.enclosure === 'function' ? TXT.enclosure(Rn) : -1);
  const shelterCover = cover(Rr);
  return { sky: TXT.skyInFrame(R.camera), marker: TXT.NO_SKY, roomErrors: before, roofErrors,
           crossErrors, domeErrors, glassErrors, optErrors, layerErrors, veilErrors, wallErrors,
           shelterCover,
           orthoSky: TXT.skyInFrame(oc), orthoErrors, zoomSky: TXT.skyInFrame(Rz.camera), zoomErrors,
           outsideErrors, rollSky: TXT.skyInFrame(Rt.camera), rollErrors, hiddenErrors, previewErrors,
           shown: TXT.SKY_SHOWN };
}`;

// What counts as inside, what a hit is, the rooms, the verdicts after the pixels: the second page,
// so neither page runs near the harness's time limit on a slower CI runner.
const ENCLOSURE = `async (T, TXT, cv) => {
  const W = Object.assign({}, TXT.worlds.goldenHour);
  // A closed shelter around a camera at 1.6 m: a roof and four walls, 3 by 3 by 2.6 m. Covers all
  // of the sky above the camera, where an interior covers 0.8 and a carport roof alone 0.59.
  const shelter = (mat) => {
    const S = new T.Group(), m = mat || new T.MeshStandardMaterial({ color: 0x333333 });
    const p = (w, h, d, x, y, z) => { const b = new T.Mesh(new T.BoxGeometry(w, h, d), m); b.position.set(x, y, z); S.add(b); };
    p(3, 0.1, 3, 0, 2.6, 0); p(0.1, 2.6, 3, -1.5, 1.3, 0); p(0.1, 2.6, 3, 1.5, 1.3, 0);
    p(3, 2.6, 0.1, 0, 1.3, -1.5); p(3, 2.6, 0.1, 0, 1.3, 1.5);
    return S;
  };
  const capture = async (fn) => {
    const out = [], orig = console.error;
    console.error = (...a) => { out.push(String(a[0])); orig.apply(console, a); };
    try { await fn(); } finally { console.error = orig; }
    return out;
  };
  const world = (fov) => {
    const Rn = TXT.setup(cv, { w: 540, h: 675, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov });
    return Rn;
  };
  const dress = (Rn, key) => {
    TXT.sky(Rn, W);
    TXT.rig(Rn, { key: Object.assign({}, W.rig.key, { pos: key }), ambient: W.rig.ambient });
    TXT.ground(Rn, { surface: 'caliche', size: 900, tile: 5 });
  };
  const cover = (Rn) => (typeof TXT.enclosure === 'function' ? TXT.enclosure(Rn) : -1);
  // A ROOF, A LAMP, A ROOM FAR BELOW: SOMETHING BUILT IS NOT AN INTERIOR (Codex, PR 369). One ray
  // straight up took each of the first two for a roof, and the third was "looked into" from 300 m.
  // A carport roof alone, 3 by 3 m and 0.8 m over the camera, covers 0.59 of the sky above it.
  const Rc = world(40);
  TXT.frame(Rc, { from: [0, 1.6, 0], look: [0, 0, -0.01] }); dress(Rc, [4, 8, 4]);
  const carport = new T.Mesh(new T.BoxGeometry(3, 0.1, 3), new T.MeshStandardMaterial({ color: 0x333333 }));
  carport.position.set(0, 2.4, 0); Rc.scene.add(carport);
  const carportErrors = await capture(() => TXT.snapshot(Rc));
  const carportCover = cover(Rc);
  // a lamp head 5 m over the camera, straight up, where the old single ray met it
  const Rq = world(40);
  TXT.frame(Rq, { from: [0, 1.6, 0], look: [0, 0, -0.01] }); dress(Rq, [4, 8, 4]);
  const lamp = new T.Mesh(new T.BoxGeometry(0.3, 0.1, 0.6), new T.MeshStandardMaterial({ color: 0x333333 }));
  lamp.position.set(0, 6.6, 0); Rq.scene.add(lamp);
  const lampErrors = await capture(() => TXT.snapshot(Rq));
  // a room 300 m straight below the camera: its footprint is a fraction of a percent of the frame
  const Rf = world(40);
  TXT.frame(Rf, { from: [0, 300, 0], look: [0, 0, -0.01] });
  TXT.sky(Rf, W); TXT.interior(Rf, {});
  TXT.rig(Rf, { key: Object.assign({}, W.rig.key, { pos: [2, 6, 2] }), ambient: W.rig.ambient });
  const farErrors = await capture(() => TXT.snapshot(Rf));
  // A SHELTER WHOSE MATERIAL SLOTS DON'T SHOW (Codex, PR 369): every box carries one opaque slot
  // (its +x face) and five invisible ones, so from inside only the left wall's inner face renders.
  const Rk = world(40);
  TXT.frame(Rk, { from: [0, 1.6, 0], look: [0, 0, -0.01] }); dress(Rk, [4, 8, 4]);
  const slots = [new T.MeshStandardMaterial({ color: 0x333333 })].concat(
    [0, 1, 2, 3, 4].map(() => new T.MeshStandardMaterial({ transparent: true, opacity: 0 })));
  const hollow = shelter(); hollow.traverse((o) => { if (o.isMesh) o.material = slots; });
  Rk.scene.add(hollow);
  const slotErrors = await capture(() => TXT.snapshot(Rk));
  const slotCover = cover(Rk);
  // A SHELL THE FAR PLANE CLIPS (Codex, PR 369): walls and a roof 8 m out, a camera whose far plane
  // is 5 m, so the shell is in no pixel the renderer draws
  const Rn = world(40);
  TXT.frame(Rn, { from: [0, 1.6, 0], look: [0, 0, -0.01] }); dress(Rn, [4, 8, 4]);
  const shell = shelter(); shell.scale.set(16 / 3, 8 / 2.6, 16 / 3); Rn.scene.add(shell);
  Rn.camera.far = 5; Rn.camera.updateProjectionMatrix();
  const farPlaneErrors = await capture(() => TXT.snapshot(Rn));
  // A SHELTER A CLIPPING PLANE CUTS AWAY: the renderer's own plane removes everything above 2 m
  const Rp2 = world(40);
  TXT.frame(Rp2, { from: [0, 1.6, 0], look: [0, 0, -0.01] }); dress(Rp2, [4, 8, 4]);
  Rp2.scene.add(shelter());
  Rp2.renderer.clippingPlanes = [new T.Plane(new T.Vector3(0, -1, 0), 2)];
  const clipErrors = await capture(() => TXT.snapshot(Rp2));
  Rp2.renderer.clippingPlanes = [];
  // A FRAME THAT BUILDS ONLY A ROOM IS HELD TO ITS ROOM (Codex, PR 369): no TXT.sky at all. Inside,
  // facing its back wall, it prints the room's clean verdict. The same room hidden before the kept
  // snapshot, or seen from 300 m straight above, prints the no-room line.
  const roomOnly = (from, look) => {
    const Rn2 = world(40);
    TXT.frame(Rn2, { from, look }); TXT.interior(Rn2, {});
    TXT.rig(Rn2, { key: Object.assign({}, W.rig.key, { pos: [2, 6, 2] }), ambient: W.rig.ambient });
    return Rn2;
  };
  const Ri = roomOnly([0, 1.6, 4], [0, 1.6, -5]);
  const roomOnlyErrors = await capture(() => TXT.snapshot(Ri));
  const Rj = roomOnly([0, 1.6, 4], [0, 1.6, -5]); Rj.room.visible = false;
  const roomHiddenErrors = await capture(() => TXT.snapshot(Rj));
  const Ro2 = roomOnly([0, 300, 0], [0, 0, -0.01]);
  const roomFarErrors = await capture(() => TXT.snapshot(Ro2));
  // A RENDER THAT COMES OUT BLACK (Codex, PR 369): exposure 0 at the horizon. TXT.snapshot returns ok
  // false and the frame would fall back to a 2D design, so the verdict is no render, never clean.
  const Rb2 = world(40);
  TXT.frame(Rb2, { from: [0, 2, 0], look: [0, 2, -100] }); dress(Rb2, [20, 40, 20]);
  Rb2.renderer.toneMappingExposure = 0;
  let blackShot = null;
  const blackErrors = await capture(async () => { blackShot = await TXT.snapshot(Rb2); });
  // A SHELTER OF CUTOUTS (Codex, PR 369): alpha-tested boxes whose texture is clear everywhere draw
  // nothing, and neither do boxes whose alphaMap is black. The same boxes with an opaque texture are
  // a shelter, which proves the test reads the texel and not only the material.
  const card = (fill) => {
    const c = document.createElement('canvas'); c.width = c.height = 8;
    const x = c.getContext('2d'); x.clearRect(0, 0, 8, 8);
    if (fill) { x.fillStyle = fill; x.fillRect(0, 0, 8, 8); }
    return new T.CanvasTexture(c);
  };
  const cutoutCase = async (mat) => {
    const Rc2 = world(40);
    TXT.frame(Rc2, { from: [0, 1.6, 0], look: [0, 0, -0.01] }); dress(Rc2, [4, 8, 4]);
    Rc2.scene.add(shelter(mat));
    return { errors: await capture(() => TXT.snapshot(Rc2)), cover: cover(Rc2) };
  };
  const clearCut = await cutoutCase(new T.MeshStandardMaterial({ map: card(null), alphaTest: 0.5 }));
  const blackMask = await cutoutCase(new T.MeshStandardMaterial({ color: 0x333333, alphaMap: card('#000'), alphaTest: 0.5 }));
  const solidCut = await cutoutCase(new T.MeshStandardMaterial({ map: card('#555'), alphaTest: 0.5 }));
  // A WIREFRAME SHELTER (Codex, PR 369): its edges are drawn and its faces aren't, so it is no shelter
  const wire = await cutoutCase(new T.MeshStandardMaterial({ color: 0x333333, wireframe: true }));
  // A CUTOUT REDRAWN BETWEEN SNAPSHOTS (Codex, PR 369): an opaque texture for the preview, then the
  // same canvas cleared with needsUpdate before the kept snapshot. The kept frame draws no shelter.
  // A SHELTER WHOSE RGBA VERTEX COLOURS ARE CLEAR (Codex, PR 369): transparent, with every vertex's
  // alpha at 0, so no fragment shows. The same shelter with alpha 1 is a shelter.
  const tinted = async (alpha) => {
    const hut = shelter(new T.MeshStandardMaterial({ color: 0xffffff, vertexColors: true, transparent: true }));
    hut.traverse((o) => {
      if (!o.isMesh) return;
      const n = o.geometry.attributes.position.count, c = new Float32Array(n * 4);
      for (let i = 0; i < n; i++) { c[i * 4] = c[i * 4 + 1] = c[i * 4 + 2] = 0.3; c[i * 4 + 3] = alpha; }
      o.geometry.setAttribute('color', new T.BufferAttribute(c, 4));
    });
    const Rt2 = world(40);
    TXT.frame(Rt2, { from: [0, 1.6, 0], look: [0, 0, -0.01] }); dress(Rt2, [4, 8, 4]);
    Rt2.scene.add(hut);
    return { errors: await capture(() => TXT.snapshot(Rt2)), cover: cover(Rt2) };
  };
  const clearVerts = await tinted(0), solidVerts = await tinted(1);
  const redraw = await (async () => {
    const tex = card('#555');
    const Rc3 = world(40);
    TXT.frame(Rc3, { from: [0, 1.6, 0], look: [0, 0, -0.01] }); dress(Rc3, [4, 8, 4]);
    Rc3.scene.add(shelter(new T.MeshStandardMaterial({ map: tex, alphaTest: 0.5 })));
    const errors = await capture(async () => {
      await TXT.snapshot(Rc3);
      tex.image.getContext('2d').clearRect(0, 0, 8, 8); tex.needsUpdate = true;
      await TXT.snapshot(Rc3);
    });
    return { errors, cover: cover(Rc3) };
  })();
  return { carportErrors, carportCover, lampErrors, farErrors,
           slotErrors, slotCover, farPlaneErrors, clipErrors, roomOnlyErrors, roomHiddenErrors, roomFarErrors,
           blackOk: blackShot && blackShot.ok, blackErrors, clearCut, blackMask, solidCut, wire, redraw,
           clearVerts, solidVerts };
}`;

// What the shader samples, the dome an orthographic camera reaches, the sky something solid hides,
// and a room turned on its axis (Codex, PR 369): the third page, so no page nears the time limit.
const SAMPLED = `async (T, TXT, cv) => {
  const W = Object.assign({}, TXT.worlds.goldenHour);
  const shelter = (mat) => {
    const S = new T.Group(), m = mat || new T.MeshStandardMaterial({ color: 0x333333 });
    const p = (w, h, d, x, y, z) => { const b = new T.Mesh(new T.BoxGeometry(w, h, d), m); b.position.set(x, y, z); S.add(b); };
    p(3, 0.1, 3, 0, 2.6, 0); p(0.1, 2.6, 3, -1.5, 1.3, 0); p(0.1, 2.6, 3, 1.5, 1.3, 0);
    p(3, 2.6, 0.1, 0, 1.3, -1.5); p(3, 2.6, 0.1, 0, 1.3, 1.5);
    return S;
  };
  const capture = async (fn) => {
    const out = [], orig = console.error;
    console.error = (...a) => { out.push(String(a[0])); orig.apply(console, a); };
    try { await fn(); } finally { console.error = orig; }
    return out;
  };
  const world = (fov) => TXT.setup(cv, { w: 540, h: 675, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov });
  const dress = (Rn, key) => {
    TXT.sky(Rn, W);
    TXT.rig(Rn, { key: Object.assign({}, W.rig.key, { pos: key }), ambient: W.rig.ambient });
    TXT.ground(Rn, { surface: 'caliche', size: 900, tile: 5 });
  };
  const cover = (Rn) => (typeof TXT.enclosure === 'function' ? TXT.enclosure(Rn) : -1);
  // WHAT THE GPU DRAWS: a plane in the material, over a red clear colour, on a context of its own.
  // A pixel that stays red was discarded.
  const gcv = document.createElement('canvas'); gcv.width = gcv.height = 16;
  const gr = new T.WebGLRenderer({ canvas: gcv, preserveDrawingBuffer: true, antialias: false });
  gr.setClearColor(0xff0000, 1);
  const gcam = new T.OrthographicCamera(-1, 1, 1, -1, 0.1, 10); gcam.position.z = 2;
  const draws = (mat) => {
    const s = new T.Scene(); s.add(new T.Mesh(new T.PlaneGeometry(4, 4), mat));
    gr.render(s, gcam);
    const gl = gr.getContext(), px = new Uint8Array(4);
    gl.readPixels(8, 8, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
    return !(px[0] === 255 && px[1] === 0 && px[2] === 0);
  };
  const data = (Arr, type, fmt, lanes, vals, o) => {
    const d = new Arr(16 * lanes);
    for (let i = 0; i < 16; i++) for (let k = 0; k < lanes; k++) d[i * lanes + k] = vals[k];
    const t = new T.DataTexture(d, 4, 4, fmt, type); Object.assign(t, o || {}); t.needsUpdate = true;
    return t;
  };
  const H = T.DataUtils.toHalfFloat;
  const mask = (t) => new T.MeshStandardMaterial({ color: 0x333333, alphaMap: t, alphaTest: 0.5 });
  const TEXELS = {
    half04:  () => mask(data(Uint16Array, T.HalfFloatType, T.RGBAFormat, 4, [H(0.4), H(0.4), H(0.4), H(1)])),
    half06:  () => mask(data(Uint16Array, T.HalfFloatType, T.RGBAFormat, 4, [H(0.6), H(0.6), H(0.6), H(1)])),
    u16mask: () => mask(data(Uint16Array, T.UnsignedShortType, T.RGBAFormat, 4, [40000, 40000, 40000, 65535])),
    u16map:  () => new T.MeshStandardMaterial({ color: 0x333333, alphaTest: 0.5,
                     map: data(Uint16Array, T.UnsignedShortType, T.RGBAFormat, 4, [100, 100, 100, 100]) }),
    srgb180: () => mask(data(Uint8Array, T.UnsignedByteType, T.RGBAFormat, 4, [180, 180, 180, 255], { colorSpace: T.SRGBColorSpace })),
    lin180:  () => mask(data(Uint8Array, T.UnsignedByteType, T.RGBAFormat, 4, [180, 180, 180, 255])),
    red255:  () => mask(data(Uint8Array, T.UnsignedByteType, T.RedFormat, 1, [255])),
  };
  const texels = {};
  for (const [k, make] of Object.entries(TEXELS)) {
    const Rc = world(40);
    TXT.frame(Rc, { from: [0, 1.6, 0], look: [0, 0, -0.01] }); dress(Rc, [4, 8, 4]);
    Rc.scene.add(shelter(make()));
    const errors = await capture(() => TXT.snapshot(Rc));
    texels[k] = { errors, cover: cover(Rc), gpu: draws(make()) };
  }
  // AN ORTHOGRAPHIC FRUSTUM 200 m TALL, pitched 5 degrees down: its rays start across its whole near
  // plane, and the upper rows start high enough to meet the dome above its horizon
  const Ro = world(40);
  TXT.frame(Ro, { from: [0, 30, 0], look: [0, 30, -100] }); dress(Ro, [20, 40, 20]);
  const tall = new T.OrthographicCamera(-80, 80, 100, -100, 0.1, 2000);
  tall.position.set(0, 30, 0); tall.lookAt(0, 30 - 100 * Math.tan(5 * Math.PI / 180), -100); tall.updateMatrixWorld();
  Ro.camera = tall;
  const tallErrors = await capture(() => TXT.snapshot(Ro));
  const tallSky = TXT.skyInFrame(tall, Ro);
  // A WALL ACROSS THE WHOLE SKY: a camera at 2 m facing the horizon and a solid wall 10 m ahead
  // filling the frame. Then the same wall as half-opaque glass, and as a cutout that draws nothing,
  // each of which the sky shows through.
  const walled = async (mat) => {
    const Rw = world(40);
    TXT.frame(Rw, { from: [0, 2, 0], look: [0, 2, -100] }); dress(Rw, [20, 40, 20]);
    const wall = new T.Mesh(new T.BoxGeometry(400, 400, 1), mat); wall.position.set(0, 0, -10); Rw.scene.add(wall);
    const errors = await capture(() => TXT.snapshot(Rw));
    return { errors, sky: TXT.skyInFrame(Rw.camera, Rw), cover: cover(Rw) };
  };
  const clear = () => { const c = document.createElement('canvas'); c.width = c.height = 8; return new T.CanvasTexture(c); };
  const solidWall = await walled(new T.MeshStandardMaterial({ color: 0x555555 }));
  const glassWall = await walled(new T.MeshStandardMaterial({ color: 0x555555, transparent: true, opacity: 0.5 }));
  const cutWall = await walled(new T.MeshStandardMaterial({ map: clear(), alphaTest: 0.5 }));
  // A ROOM TURNED 45 DEGREES and a camera 3 m over the ground in front of its open side, looking
  // straight down: inside the room's world box, outside its floor, with no wall in the frame
  const Rt = world(40);
  TXT.frame(Rt, { from: [6.5, 3, 6.5], look: [6.5, 0, 6.49] });
  TXT.sky(Rt, W); TXT.interior(Rt, {}); Rt.room.rotation.y = Math.PI / 4;
  TXT.rig(Rt, { key: Object.assign({}, W.rig.key, { pos: [8, 8, 8] }), ambient: W.rig.ambient });
  const turnedErrors = await capture(() => TXT.snapshot(Rt));
  const turnedShare = TXT.roomShare(Rt);
  // ...and the same turned room with only a room, the camera inside it facing its back wall
  const th = Math.PI / 4, turn = (x, z) => [x * Math.cos(th) + z * Math.sin(th), -x * Math.sin(th) + z * Math.cos(th)];
  const Ri = world(40);
  const [cx, cz] = turn(0, 3), [bx, bz] = turn(0, -5);
  TXT.frame(Ri, { from: [cx, 1.6, cz], look: [bx, 1.6, bz] });
  TXT.interior(Ri, {}); Ri.room.rotation.y = th;
  TXT.rig(Ri, { key: Object.assign({}, W.rig.key, { pos: [2, 6, 2] }), ambient: W.rig.ambient });
  const turnedInErrors = await capture(() => TXT.snapshot(Ri));
  const turnedInShare = TXT.roomShare(Ri);
  return { texels, tallErrors, tallSky, solidWall, glassWall, cutWall,
           turnedErrors, turnedShare, turnedInErrors, turnedInShare };
}`;

// What the GPU filters and hashes (Codex, PR 369): the fourth page. A mipmapped cutout is read at
// the level this frame samples it at, and an alpha-hashed surface counts by the share of it that draws.
const FILTERED = `async (T, TXT, cv) => {
  const W = Object.assign({}, TXT.worlds.goldenHour);
  const shelter = (mat) => {
    const S = new T.Group(), m = mat || new T.MeshStandardMaterial({ color: 0x333333 });
    const p = (w, h, d, x, y, z) => { const b = new T.Mesh(new T.BoxGeometry(w, h, d), m); b.position.set(x, y, z); S.add(b); };
    p(3, 0.1, 3, 0, 2.6, 0); p(0.1, 2.6, 3, -1.5, 1.3, 0); p(0.1, 2.6, 3, 1.5, 1.3, 0);
    p(3, 2.6, 0.1, 0, 1.3, -1.5); p(3, 2.6, 0.1, 0, 1.3, 1.5);
    return S;
  };
  const capture = async (fn) => {
    const out = [], orig = console.error;
    console.error = (...a) => { out.push(String(a[0])); orig.apply(console, a); };
    try { await fn(); } finally { console.error = orig; }
    return out;
  };
  const world = (fov) => TXT.setup(cv, { w: 540, h: 675, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov });
  const dress = (Rn, key) => {
    TXT.sky(Rn, W);
    TXT.rig(Rn, { key: Object.assign({}, W.rig.key, { pos: key }), ambient: W.rig.ambient });
    TXT.ground(Rn, { surface: 'caliche', size: 900, tile: 5 });
  };
  const cover = (Rn) => (typeof TXT.enclosure === 'function' ? TXT.enclosure(Rn) : -1);
  // WHAT THE GPU DRAWS: the share of a plane in the material that isn't discarded, over red, on a
  // 128 by 128 context of its own
  const gcv = document.createElement('canvas'); gcv.width = gcv.height = 128;
  const gr = new T.WebGLRenderer({ canvas: gcv, preserveDrawingBuffer: true, antialias: false });
  gr.setClearColor(0xff0000, 1);
  const gcam = new T.OrthographicCamera(-1, 1, 1, -1, 0.1, 10); gcam.position.z = 2;
  const drawnShare = (mat, copies = 1, geo) => {
    const s = new T.Scene();
    for (let i = 0; i < copies; i++) s.add(new T.Mesh(geo || new T.PlaneGeometry(2, 2), i ? mat.clone() : mat));
    gr.render(s, gcam);
    const gl = gr.getContext(), px = new Uint8Array(128 * 128 * 4);
    gl.readPixels(0, 0, 128, 128, gl.RGBA, gl.UNSIGNED_BYTE, px);
    let n = 0; for (let i = 0; i < px.length; i += 4) if (!(px[i] === 255 && px[i + 1] === 0 && px[i + 2] === 0)) n++;
    return n / (128 * 128);
  };
  // AN ALPHA-HASHED SHELTER: opaque in three's terms, and a fraction of it equal to its alpha drawn
  const hashed = async (opacity) => {
    const make = () => new T.MeshStandardMaterial({ color: 0x333333, alphaHash: true, opacity });
    const Rh = world(40);
    TXT.frame(Rh, { from: [0, 1.6, 0], look: [0, 0, -0.01] }); dress(Rh, [4, 8, 4]);
    Rh.scene.add(shelter(make()));
    const errors = await capture(() => TXT.snapshot(Rh));
    return { errors, cover: cover(Rh), gpu: drawnShare(make()) };
  };
  const hash02 = await hashed(0.2), hash095 = await hashed(0.95);
  // THE KIT'S PERFORATED STEEL (industry.js), 128 texels to 5 cm with a third of it holes, as a wall
  // across the whole frame of a camera facing the horizon, at 40 m and at 2 m
  const perf = () => {
    const c = document.createElement('canvas'); c.width = c.height = 128;
    const x = c.getContext('2d'), TAU = Math.PI * 2;
    x.fillStyle = '#1a1b1d'; x.fillRect(0, 0, 128, 128);
    x.globalCompositeOperation = 'destination-out';
    for (let j = 0; j < 8; j++) for (let i = 0; i < 8; i++) { x.beginPath(); x.arc(i * 16 + (j % 2) * 8 + 4, j * 16 + 8, 5.2, 0, TAU); x.fill(); }
    const t = new T.CanvasTexture(c);
    t.wrapS = t.wrapT = T.RepeatWrapping; t.colorSpace = T.SRGBColorSpace; t.anisotropy = 8;
    t.repeat.set(400 / 0.05, 400 / 0.05);
    return t;
  };
  // the sky the pixels show: those that change when the dome is hidden, and the engine's own verdict
  const perfWall = async (dist) => {
    const Rp = world(40);
    TXT.frame(Rp, { from: [0, 2, 0], look: [0, 2, -100] });
    const dome = TXT.sky(Rp, W);
    TXT.rig(Rp, { key: Object.assign({}, W.rig.key, { pos: [20, 40, 20] }), ambient: W.rig.ambient });
    TXT.ground(Rp, { surface: 'caliche', size: 900, tile: 5 });
    const wall = new T.Mesh(new T.PlaneGeometry(400, 400), new T.MeshStandardMaterial({
      color: 0xffffff, metalness: 0.5, roughness: 0.5, side: T.DoubleSide, alphaTest: 0.5, map: perf() }));
    wall.position.set(0, 0, -dist); Rp.scene.add(wall);
    const errors = await capture(() => TXT.snapshot(Rp));
    const gl = Rp.renderer.getContext(), Wd = gl.drawingBufferWidth, Hd = gl.drawingBufferHeight;
    const read = () => { Rp.renderer.render(Rp.scene, Rp.camera); const b = new Uint8Array(Wd * Hd * 4); gl.readPixels(0, 0, Wd, Hd, gl.RGBA, gl.UNSIGNED_BYTE, b); return b; };
    const shown = read(); dome.visible = false; const hidden = read(); dome.visible = true; read();
    let n = 0;
    for (let i = 0; i < shown.length; i += 4)
      if (Math.max(Math.abs(shown[i] - hidden[i]), Math.abs(shown[i + 1] - hidden[i + 1]), Math.abs(shown[i + 2] - hidden[i + 2])) > 8) n++;
    return { errors, sky: TXT.skyInFrame(Rp.camera, Rp), gpuSky: n / (Wd * Hd) };
  };
  const perfFar = await perfWall(40), perfNear = await perfWall(2);
  // EIGHT COINCIDENT ALPHA-HASHED SHELTERS at 0.2: three.js hashes the same local points alike, so
  // they discard the same fragments and draw a fifth, where independent draws would make 83 percent
  const stacked = await (async () => {
    const make = () => new T.MeshStandardMaterial({ color: 0x333333, alphaHash: true, opacity: 0.2 });
    const Rh = world(40);
    TXT.frame(Rh, { from: [0, 1.6, 0], look: [0, 0, -0.01] }); dress(Rh, [4, 8, 4]);
    for (let i = 0; i < 8; i++) Rh.scene.add(shelter(make()));
    const errors = await capture(() => TXT.snapshot(Rh));
    return { errors, cover: cover(Rh), gpu: drawnShare(make(), 8) };
  })();
  // A SUPPLIED MIP CHAIN: level 0 clear, every smaller level solid, as three.js uploads it in place
  // of the image. Near, the wall is magnified onto level 0 and the sky shows through. Far, it is
  // minified onto the solid levels and hides the sky.
  const mipped = () => {
    const mips = [];
    for (let n = 128, i = 0; n >= 1; n >>= 1, i++) {
      const d = new Uint8Array(n * n * 4);
      for (let k = 0; k < n * n; k++) { d[k * 4] = d[k * 4 + 1] = d[k * 4 + 2] = 90; d[k * 4 + 3] = i ? 255 : 0; }
      mips.push({ data: d, width: n, height: n });
    }
    const t = new T.DataTexture(mips[0].data, 128, 128, T.RGBAFormat, T.UnsignedByteType);
    t.mipmaps = mips; t.generateMipmaps = false;
    t.minFilter = T.NearestMipmapNearestFilter; t.magFilter = T.NearestFilter;
    t.wrapS = t.wrapT = T.RepeatWrapping; t.repeat.set(1000, 1000); t.needsUpdate = true;
    return t;
  };
  const mipWall = async (dist) => {
    const Rm = world(40);
    TXT.frame(Rm, { from: [0, 2, 0], look: [0, 2, -100] });
    const dome = TXT.sky(Rm, W);
    TXT.rig(Rm, { key: Object.assign({}, W.rig.key, { pos: [20, 40, 20] }), ambient: W.rig.ambient });
    TXT.ground(Rm, { surface: 'caliche', size: 900, tile: 5 });
    const wall = new T.Mesh(new T.PlaneGeometry(400, 400), new T.MeshStandardMaterial({ color: 0xffffff, alphaTest: 0.5, map: mipped() }));
    wall.position.set(0, 0, -dist); Rm.scene.add(wall);
    const errors = await capture(() => TXT.snapshot(Rm));
    const gl = Rm.renderer.getContext(), Wd = gl.drawingBufferWidth, Hd = gl.drawingBufferHeight;
    const read = () => { Rm.renderer.render(Rm.scene, Rm.camera); const b = new Uint8Array(Wd * Hd * 4); gl.readPixels(0, 0, Wd, Hd, gl.RGBA, gl.UNSIGNED_BYTE, b); return b; };
    const shown = read(); dome.visible = false; const hidden = read(); dome.visible = true; read();
    let n = 0;
    for (let i = 0; i < shown.length; i += 4)
      if (Math.max(Math.abs(shown[i] - hidden[i]), Math.abs(shown[i + 1] - hidden[i + 1]), Math.abs(shown[i + 2] - hidden[i + 2])) > 8) n++;
    return { errors, sky: TXT.skyInFrame(Rm.camera, Rm), gpuSky: n / (Wd * Hd) };
  };
  const mipFar = await mipWall(40), mipNear = await mipWall(2);
  // AN ALPHAMAP ON UV CHANNEL 2: its uv2 points at a solid texel and its uv at a clear one, so the
  // GPU draws the shelter solid. Read through uv it would be clear.
  const channel = async (ch) => {
    const tex = new T.DataTexture(new Uint8Array([255, 0, 255, 255, 255, 255, 255, 255]), 2, 1, T.RGBAFormat, T.UnsignedByteType);
    tex.channel = ch; tex.needsUpdate = true;
    const geo = (g) => {
      const n = g.attributes.uv.count, uv = g.attributes.uv;
      for (let i = 0; i < n; i++) uv.setXY(i, 0.25, 0.5);
      g.setAttribute('uv2', new T.BufferAttribute(new Float32Array(n * 2).map((_, k) => (k % 2 ? 0.5 : 0.75)), 2));
      return g;
    };
    const make = () => new T.MeshStandardMaterial({ color: 0x333333, alphaMap: tex, alphaTest: 0.5 });
    const S = new T.Group(), m = make();
    const p = (w, h, d, x, y, z) => { const b = new T.Mesh(geo(new T.BoxGeometry(w, h, d)), m); b.position.set(x, y, z); S.add(b); };
    p(3, 0.1, 3, 0, 2.6, 0); p(0.1, 2.6, 3, -1.5, 1.3, 0); p(0.1, 2.6, 3, 1.5, 1.3, 0);
    p(3, 2.6, 0.1, 0, 1.3, -1.5); p(3, 2.6, 0.1, 0, 1.3, 1.5);
    const Rc = world(40);
    TXT.frame(Rc, { from: [0, 1.6, 0], look: [0, 0, -0.01] }); dress(Rc, [4, 8, 4]);
    Rc.scene.add(S);
    const errors = await capture(() => TXT.snapshot(Rc));
    return { errors, cover: cover(Rc), gpu: drawnShare(make(), 1, geo(new T.PlaneGeometry(2, 2))) };
  };
  const uv2 = await channel(2), uv0 = await channel(0);
  return { hash02, hash095, perfFar, perfNear, stacked, mipFar, mipNear, uv2, uv0 };
}`;

// What a blend covers and what a sprite hides (Codex, PR 369): the fifth page.
const BLENDED = `async (T, TXT, cv) => {
  const W = Object.assign({}, TXT.worlds.goldenHour);
  const shelter = (mat) => {
    const S = new T.Group(), m = mat || new T.MeshStandardMaterial({ color: 0x333333 });
    const p = (w, h, d, x, y, z) => { const b = new T.Mesh(new T.BoxGeometry(w, h, d), m); b.position.set(x, y, z); S.add(b); };
    p(3, 0.1, 3, 0, 2.6, 0); p(0.1, 2.6, 3, -1.5, 1.3, 0); p(0.1, 2.6, 3, 1.5, 1.3, 0);
    p(3, 2.6, 0.1, 0, 1.3, -1.5); p(3, 2.6, 0.1, 0, 1.3, 1.5);
    return S;
  };
  const capture = async (fn) => {
    const out = [], orig = console.error;
    console.error = (...a) => { out.push(String(a[0])); orig.apply(console, a); };
    try { await fn(); } finally { console.error = orig; }
    return out;
  };
  const world = (fov) => TXT.setup(cv, { w: 540, h: 675, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov });
  const dress = (Rn, key) => {
    TXT.sky(Rn, W);
    TXT.rig(Rn, { key: Object.assign({}, W.rig.key, { pos: key }), ambient: W.rig.ambient });
    TXT.ground(Rn, { surface: 'caliche', size: 900, tile: 5 });
  };
  const cover = (Rn) => (typeof TXT.enclosure === 'function' ? TXT.enclosure(Rn) : -1);
  // WHAT A BLEND COVERS ON THE GPU: a black plane in the material over red, where the red that is left
  // is the share of the pixel the plane doesn't cover
  const gcv = document.createElement('canvas'); gcv.width = gcv.height = 16;
  const gr = new T.WebGLRenderer({ canvas: gcv, preserveDrawingBuffer: true, antialias: false });
  gr.setClearColor(0xff0000, 1);
  const gcam = new T.OrthographicCamera(-1, 1, 1, -1, 0.1, 10); gcam.position.z = 2;
  const blendCover = (mat) => {
    const s = new T.Scene(); s.add(new T.Mesh(new T.PlaneGeometry(4, 4), mat));
    gr.render(s, gcam);
    const gl = gr.getContext(), px = new Uint8Array(4);
    gl.readPixels(8, 8, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
    return 1 - px[0] / 255;
  };
  const veiled = async (opacity) => {
    const make = () => new T.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity });
    const Rv = world(40);
    TXT.frame(Rv, { from: [0, 1.6, 0], look: [0, 0, -0.01] }); dress(Rv, [4, 8, 4]);
    Rv.scene.add(shelter(make()));
    const errors = await capture(() => TXT.snapshot(Rv));
    return { errors, cover: cover(Rv), gpu: blendCover(make()) };
  };
  const veil001 = await veiled(0.01), veil09 = await veiled(0.9);
  // A SPRITE ACROSS THE SKY: a camera at 2 m facing the horizon and a sprite 400 m across, 10 m out,
  // in an opaque texture, then in a clear one
  const card = (fill) => {
    const c = document.createElement('canvas'); c.width = c.height = 8;
    const x = c.getContext('2d'); x.clearRect(0, 0, 8, 8);
    if (fill) { x.fillStyle = fill; x.fillRect(0, 0, 8, 8); }
    return new T.CanvasTexture(c);
  };
  const sprited = async (fill) => {
    const Rs = world(40);
    TXT.frame(Rs, { from: [0, 2, 0], look: [0, 2, -100] });
    const dome = TXT.sky(Rs, W);
    TXT.rig(Rs, { key: Object.assign({}, W.rig.key, { pos: [20, 40, 20] }), ambient: W.rig.ambient });
    TXT.ground(Rs, { surface: 'caliche', size: 900, tile: 5 });
    const sp = new T.Sprite(new T.SpriteMaterial({ map: card(fill) }));
    sp.scale.set(400, 400, 1); sp.position.set(0, 2, -10); Rs.scene.add(sp);
    const errors = await capture(() => TXT.snapshot(Rs));
    const gl = Rs.renderer.getContext(), Wd = gl.drawingBufferWidth, Hd = gl.drawingBufferHeight;
    const read = () => { Rs.renderer.render(Rs.scene, Rs.camera); const b = new Uint8Array(Wd * Hd * 4); gl.readPixels(0, 0, Wd, Hd, gl.RGBA, gl.UNSIGNED_BYTE, b); return b; };
    const shown = read(); dome.visible = false; const hidden = read(); dome.visible = true; read();
    let n = 0;
    for (let i = 0; i < shown.length; i += 4)
      if (Math.max(Math.abs(shown[i] - hidden[i]), Math.abs(shown[i + 1] - hidden[i + 1]), Math.abs(shown[i + 2] - hidden[i + 2])) > 8) n++;
    return { errors, sky: TXT.skyInFrame(Rs.camera, Rs), gpuSky: n / (Wd * Hd) };
  };
  const spriteSolid = await sprited('#555'), spriteClear = await sprited(null);
  return { veil001, veil09, spriteSolid, spriteClear };
}`;

// What draws over what (Codex, PR 372): the sixth page. Coincident hashed surfaces blend every
// survivor, a hit that skips the depth test paints over the wall in front of it, and a sprite that
// keeps its size on screen keeps its mip level.
const OVERLAID = `async (T, TXT, cv) => {
  const W = Object.assign({}, TXT.worlds.goldenHour);
  const shelter = (mat) => {
    const S = new T.Group(), m = mat || new T.MeshStandardMaterial({ color: 0x333333 });
    const p = (w, h, d, x, y, z) => { const b = new T.Mesh(new T.BoxGeometry(w, h, d), m); b.position.set(x, y, z); S.add(b); };
    p(3, 0.1, 3, 0, 2.6, 0); p(0.1, 2.6, 3, -1.5, 1.3, 0); p(0.1, 2.6, 3, 1.5, 1.3, 0);
    p(3, 2.6, 0.1, 0, 1.3, -1.5); p(3, 2.6, 0.1, 0, 1.3, 1.5);
    return S;
  };
  const capture = async (fn) => {
    const out = [], orig = console.error;
    console.error = (...a) => { out.push(String(a[0])); orig.apply(console, a); };
    try { await fn(); } finally { console.error = orig; }
    return out;
  };
  const world = (fov) => TXT.setup(cv, { w: 540, h: 675, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov });
  const dress = (Rn, key) => {
    TXT.sky(Rn, W);
    TXT.rig(Rn, { key: Object.assign({}, W.rig.key, { pos: key }), ambient: W.rig.ambient });
    TXT.ground(Rn, { surface: 'caliche', size: 900, tile: 5 });
  };
  const cover = (Rn) => (typeof TXT.enclosure === 'function' ? TXT.enclosure(Rn) : -1);
  // WHAT TWO COINCIDENT HASHED AND BLENDED PLANES COVER ON THE GPU: black over red, the red left in
  // each pixel is the share they don't cover, averaged over a 128 by 128 frame
  const gcv = document.createElement('canvas'); gcv.width = gcv.height = 128;
  const gr = new T.WebGLRenderer({ canvas: gcv, preserveDrawingBuffer: true, antialias: false });
  gr.setClearColor(0xff0000, 1);
  const gcam = new T.OrthographicCamera(-1, 1, 1, -1, 0.1, 10); gcam.position.z = 2;
  const meanCover = (make, copies) => {
    const s = new T.Scene();
    for (let i = 0; i < copies; i++) s.add(new T.Mesh(new T.PlaneGeometry(2, 2), make()));
    gr.render(s, gcam);
    const gl = gr.getContext(), px = new Uint8Array(128 * 128 * 4);
    gl.readPixels(0, 0, 128, 128, gl.RGBA, gl.UNSIGNED_BYTE, px);
    let sum = 0; for (let i = 0; i < px.length; i += 4) sum += 1 - px[i] / 255;
    return sum / (128 * 128);
  };
  const hashBlend = () => new T.MeshBasicMaterial({ color: 0x000000, alphaHash: true, transparent: true, opacity: 0.5, depthWrite: false });
  const twin = await (async () => {
    const Rh = world(40);
    TXT.frame(Rh, { from: [0, 1.6, 0], look: [0, 0, -0.01] }); dress(Rh, [4, 8, 4]);
    Rh.scene.add(shelter(hashBlend())); Rh.scene.add(shelter(hashBlend()));
    const errors = await capture(() => TXT.snapshot(Rh));
    return { errors, cover: cover(Rh), gpu: meanCover(hashBlend, 2) };
  })();
  // A SPRITE WITH depthTest OFF, 3 m behind a room's back wall and wide enough to fill the frame: it
  // is drawn after the walls and paints over them. The same sprite depth-tested stays behind the wall.
  const overlay = async (depthTest) => {
    const Ri = world(40);
    TXT.frame(Ri, { from: [0, 1.6, 4], look: [0, 1.6, -5] }); TXT.interior(Ri, {});
    TXT.rig(Ri, { key: Object.assign({}, W.rig.key, { pos: [2, 6, 2] }), ambient: W.rig.ambient });
    const sp = new T.Sprite(new T.SpriteMaterial({ color: 0x00ff00, depthTest, toneMapped: false }));
    sp.scale.set(60, 60, 1); sp.position.set(0, 1.6, -8); Ri.scene.add(sp);
    const errors = await capture(() => TXT.snapshot(Ri));
    const gl = Ri.renderer.getContext(), px = new Uint8Array(4);
    gl.readPixels(Math.floor(gl.drawingBufferWidth / 2), Math.floor(gl.drawingBufferHeight / 2), 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
    return { errors, share: TXT.roomShare(Ri), centre: Array.from(px.slice(0, 3)) };
  };
  const over = await overlay(false), under = await overlay(true);
  // A SPRITE THAT DOESN'T ATTENUATE, 400 m out and scaled to fill the frame, over a supplied mip chain
  // clear at level 0 and solid below: on screen it is magnified onto the clear level, so the sky shows
  const chain = () => {
    const mips = [];
    for (let n = 128, i = 0; n >= 1; n >>= 1, i++) {
      const d = new Uint8Array(n * n * 4);
      for (let k = 0; k < n * n; k++) { d[k * 4] = d[k * 4 + 1] = d[k * 4 + 2] = 90; d[k * 4 + 3] = i ? 255 : 0; }
      mips.push({ data: d, width: n, height: n });
    }
    const t = new T.DataTexture(mips[0].data, 128, 128, T.RGBAFormat, T.UnsignedByteType);
    t.mipmaps = mips; t.generateMipmaps = false;
    t.minFilter = T.NearestMipmapNearestFilter; t.magFilter = T.NearestFilter; t.needsUpdate = true;
    return t;
  };
  const steady = await (async () => {
    const Rs = world(40);
    TXT.frame(Rs, { from: [0, 2, 0], look: [0, 2, -100] });
    const dome = TXT.sky(Rs, W);
    TXT.rig(Rs, { key: Object.assign({}, W.rig.key, { pos: [20, 40, 20] }), ambient: W.rig.ambient });
    TXT.ground(Rs, { surface: 'caliche', size: 900, tile: 5 });
    const sp = new T.Sprite(new T.SpriteMaterial({ map: chain(), alphaTest: 0.5, sizeAttenuation: false }));
    sp.scale.set(2, 2, 1); sp.position.set(0, 2, -400); Rs.scene.add(sp);
    const errors = await capture(() => TXT.snapshot(Rs));
    const gl = Rs.renderer.getContext(), Wd = gl.drawingBufferWidth, Hd = gl.drawingBufferHeight;
    const read = () => { Rs.renderer.render(Rs.scene, Rs.camera); const b = new Uint8Array(Wd * Hd * 4); gl.readPixels(0, 0, Wd, Hd, gl.RGBA, gl.UNSIGNED_BYTE, b); return b; };
    const shown = read(); dome.visible = false; const hidden = read(); dome.visible = true; read();
    let n = 0;
    for (let i = 0; i < shown.length; i += 4)
      if (Math.max(Math.abs(shown[i] - hidden[i]), Math.abs(shown[i + 1] - hidden[i + 1]), Math.abs(shown[i + 2] - hidden[i + 2])) > 8) n++;
    return { errors, sky: TXT.skyInFrame(Rs.camera, Rs), gpuSky: n / (Wd * Hd) };
  })();
  return { twin, over, under, steady };
}`;

// What draws over what, and the step a pixel takes (Codex, PR 373): the seventh page. The renderer's
// own order decides what a pixel shows once a depth test is off: a pane in front of a sprite with the
// test off blends back over it, an opaque backdrop drawn before the walls is drawn over by them, and
// coincident hashed overlays with the test off survive as one. The GPU reads a texture's level off the
// step a pixel takes across a surface, so a sprite and a wall seen wide keep one level edge to edge,
// and a texture repeated more one way than the other is read at the larger step.
const ORDERED = `async (T, TXT, cv) => {
  const W = Object.assign({}, TXT.worlds.goldenHour);
  const capture = async (fn) => {
    const out = [], orig = console.error;
    console.error = (...a) => { out.push(String(a[0])); orig.apply(console, a); };
    try { await fn(); } finally { console.error = orig; }
    return out;
  };
  const world = (fov) => TXT.setup(cv, { w: 540, h: 675, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov });
  const room = (ceiling) => {
    const Ri = world(40);
    TXT.frame(Ri, { from: [0, 1.6, 4], look: [0, 1.6, -5] }); TXT.interior(Ri, { ceiling });
    TXT.rig(Ri, { key: Object.assign({}, W.rig.key, { pos: [2, 6, 2] }), ambient: W.rig.ambient });
    return Ri;
  };
  const pixels = (Rn) => {
    Rn.renderer.render(Rn.scene, Rn.camera);
    const gl = Rn.renderer.getContext(), b = new Uint8Array(gl.drawingBufferWidth * gl.drawingBufferHeight * 4);
    gl.readPixels(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight, gl.RGBA, gl.UNSIGNED_BYTE, b);
    return b;
  };
  const centre = (Rn, b) => {
    const gl = Rn.renderer.getContext(), c = (Math.floor(gl.drawingBufferHeight / 2) * gl.drawingBufferWidth + Math.floor(gl.drawingBufferWidth / 2)) * 4;
    return [b[c], b[c + 1], b[c + 2]];
  };
  // A PANE IN FRONT OF A SPRITE WITH depthTest OFF: the green sprite, 3 m behind the back wall, paints
  // over the wall, and the blue pane at 0.6 inside the room, the nearer of the two transparent things,
  // is drawn after it and blends back over it. Every pixel is 0.6 pane, and the pane is in the room.
  const pane = await (async () => {
    const Ri = room(false);
    const sp = new T.Sprite(new T.SpriteMaterial({ color: 0x00ff00, depthTest: false, toneMapped: false }));
    sp.scale.set(60, 60, 1); sp.position.set(0, 1.6, -8); Ri.scene.add(sp);
    const pn = new T.Mesh(new T.PlaneGeometry(6, 6),
      new T.MeshBasicMaterial({ color: 0x0000ff, transparent: true, opacity: 0.6, toneMapped: false, side: T.DoubleSide }));
    pn.position.set(0, 1.6, 1); Ri.scene.add(pn);
    const errors = await capture(() => TXT.snapshot(Ri));
    const b = pixels(Ri);
    let blue = 0; for (let i = 2; i < b.length; i += 4) blue += b[i] / 255;
    return { errors, share: TXT.roomShare(Ri), blue: blue / (b.length / 4) };
  })();
  // AN OPAQUE BACKDROP WITH depthTest OFF, 3 m behind the back wall. At renderOrder -1 the renderer
  // draws it before the walls, which draw over it, and at renderOrder 1 after them, over them.
  const backdrop = async (order) => {
    const Ri = room(false);
    const bd = new T.Mesh(new T.PlaneGeometry(60, 60), new T.MeshBasicMaterial({ color: 0x00ff00, depthTest: false, toneMapped: false }));
    bd.position.set(0, 1.6, -8); bd.renderOrder = order; Ri.scene.add(bd);
    const errors = await capture(() => TXT.snapshot(Ri));
    return { errors, share: TXT.roomShare(Ri), centre: centre(Ri, pixels(Ri)) };
  };
  const before = await backdrop(-1), after = await backdrop(1);
  // FOUR COINCIDENT HASHED OVERLAYS WITH depthTest OFF, black at 0.5, 3 m behind the back wall of a
  // room with a ceiling. They paint over the room and share one threshold, so in half the pixels all
  // four draw and cover 1 - 0.5^4 of it, and the GPU's cover is read off how far they darken each pixel.
  const hashed = await (async () => {
    const Ri = room(true), veils = [];
    for (let i = 0; i < 4; i++) {
      const m = new T.Mesh(new T.PlaneGeometry(60, 60), new T.MeshBasicMaterial({ color: 0x000000, alphaHash: true,
        transparent: true, opacity: 0.5, depthWrite: false, depthTest: false, toneMapped: false }));
      m.position.set(0, 1.6, -8); Ri.scene.add(m); veils.push(m);
    }
    const errors = await capture(() => TXT.snapshot(Ri));
    const b = pixels(Ri), share = TXT.roomShare(Ri);
    veils.forEach((m) => { m.visible = false; });
    const plain = pixels(Ri), bare = TXT.roomShare(Ri);
    veils.forEach((m) => { m.visible = true; });
    let cover = 0, n = 0;
    for (let i = 0; i < b.length; i += 4) {
      const s = plain[i] + plain[i + 1] + plain[i + 2];
      if (s > 60) { cover += 1 - (b[i] + b[i + 1] + b[i + 2]) / s; n++; }
    }
    return { errors, bare, share, gpuCover: n ? cover / n : -1 };
  })();
  // SEEN WIDE: a 90 degree lens over a chain clear at level 0 and solid below, repeated so a pixel steps
  // 1.14 texels across the card, which is level 0.19 and the clear level. The GPU samples that level
  // edge to edge, so the whole card is clear and the upper half of the frame is sky.
  const chain = (ru, rv) => {
    const mips = [];
    for (let n = 128, i = 0; n >= 1; n >>= 1, i++) {
      const d = new Uint8Array(n * n * 4);
      for (let k = 0; k < n * n; k++) { d[k * 4] = d[k * 4 + 1] = d[k * 4 + 2] = 90; d[k * 4 + 3] = i ? 255 : 0; }
      mips.push({ data: d, width: n, height: n });
    }
    const t = new T.DataTexture(mips[0].data, 128, 128, T.RGBAFormat, T.UnsignedByteType);
    t.mipmaps = mips; t.generateMipmaps = false; t.wrapS = t.wrapT = T.RepeatWrapping; t.repeat.set(ru, rv);
    t.minFilter = T.NearestMipmapNearestFilter; t.magFilter = T.NearestFilter; t.needsUpdate = true;
    return t;
  };
  const wide = async (make) => {
    const Rs = world(90);
    TXT.frame(Rs, { from: [0, 2, 0], look: [0, 2, -100] });
    const dome = TXT.sky(Rs, W);
    TXT.rig(Rs, { key: Object.assign({}, W.rig.key, { pos: [20, 40, 20] }), ambient: W.rig.ambient });
    TXT.ground(Rs, { surface: 'caliche', size: 900, tile: 5 });
    Rs.scene.add(make());
    const errors = await capture(() => TXT.snapshot(Rs));
    const shown = pixels(Rs); dome.visible = false; const hidden = pixels(Rs); dome.visible = true; pixels(Rs);
    let n = 0;
    for (let i = 0; i < shown.length; i += 4)
      if (Math.max(Math.abs(shown[i] - hidden[i]), Math.abs(shown[i + 1] - hidden[i + 1]), Math.abs(shown[i + 2] - hidden[i + 2])) > 8) n++;
    return { errors, sky: TXT.skyInFrame(Rs.camera, Rs), gpuSky: n / (shown.length / 4) };
  };
  // a sprite that doesn't attenuate, 4 by 4 at 50 m: 2700 pixels across, 128 texels repeated 24 times
  const sprite = await wide(() => {
    const sp = new T.Sprite(new T.SpriteMaterial({ map: chain(24, 24), alphaTest: 0.5, sizeAttenuation: false }));
    sp.scale.set(4, 4, 1); sp.position.set(0, 2, -50); return sp;
  });
  // a wall 40 m square facing the camera 10 m out, the same 2700 pixels and 24 repeats
  const wall = await wide(() => {
    const m = new T.Mesh(new T.PlaneGeometry(40, 40), new T.MeshBasicMaterial({ map: chain(24, 24), alphaTest: 0.5, side: T.DoubleSide }));
    m.position.set(0, 2, -10); return m;
  });
  // ...repeated 48 times across and 12 up: a pixel steps 2.28 texels across and 0.57 up, and the GPU
  // reads the larger step, level 1.19, the solid one, so the wall hides the sky
  const skewed = await wide(() => {
    const m = new T.Mesh(new T.PlaneGeometry(40, 40), new T.MeshBasicMaterial({ map: chain(48, 12), alphaTest: 0.5, side: T.DoubleSide }));
    m.position.set(0, 2, -10); return m;
  });
  // TWO TRANSPARENT WALLS ACROSS THE SKY, the near one at 0.5 and the far one solid, which renderOrder
  // draws after it: the near one writes its depth first, so the far one fails its depth test behind
  // it and the sky shows through the near one at half. Taken nearest first, the far one hid it all.
  const layered = await (async () => {
    const Rs = world(40);
    TXT.frame(Rs, { from: [0, 2, 0], look: [0, 2, -100] });
    const dome = TXT.sky(Rs, W);
    TXT.rig(Rs, { key: Object.assign({}, W.rig.key, { pos: [20, 40, 20] }), ambient: W.rig.ambient });
    TXT.ground(Rs, { surface: 'caliche', size: 900, tile: 5 });
    const near = new T.Mesh(new T.PlaneGeometry(200, 200), new T.MeshBasicMaterial({ color: 0x202020, transparent: true, opacity: 0.5 }));
    const far = new T.Mesh(new T.PlaneGeometry(400, 400), new T.MeshBasicMaterial({ color: 0x202020, transparent: true, opacity: 1 }));
    near.position.set(0, 2, -20); far.position.set(0, 2, -40); far.renderOrder = 1;
    Rs.scene.add(near, far);
    const errors = await capture(() => TXT.snapshot(Rs));
    const shown = pixels(Rs); dome.visible = false; const hidden = pixels(Rs); dome.visible = true; pixels(Rs);
    let n = 0;
    for (let i = 0; i < shown.length; i += 4)
      if (Math.max(Math.abs(shown[i] - hidden[i]), Math.abs(shown[i + 1] - hidden[i + 1]), Math.abs(shown[i + 2] - hidden[i + 2])) > 8) n++;
    return { errors, sky: TXT.skyInFrame(Rs.camera, Rs), gpuSky: n / (shown.length / 4) };
  })();
  return { pane, before, after, hashed, sprite, wall, skewed, layered };
}`;

// Inside one draw, and the samples an anisotropic texture takes (Codex, PR 374): the eighth page. An
// instanced draw runs instance by instance, so a later instance paints over an earlier one whatever
// faces the ray meets. SwiftShader, which renders every deck here, reads an anisotropic texture's
// stretch off the area its two pixel steps span, so a footprint stretched along a diagonal of the
// screen is sampled fine and many times, where comparing the steps' lengths read it as round.
const STEPPED = `async (T, TXT, cv) => {
  const W = Object.assign({}, TXT.worlds.goldenHour);
  const capture = async (fn) => {
    const out = [], orig = console.error;
    console.error = (...a) => { out.push(String(a[0])); orig.apply(console, a); };
    try { await fn(); } finally { console.error = orig; }
    return out;
  };
  const world = (fov) => TXT.setup(cv, { w: 540, h: 675, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov });
  const pixels = (Rn) => {
    Rn.renderer.render(Rn.scene, Rn.camera);
    const gl = Rn.renderer.getContext(), b = new Uint8Array(gl.drawingBufferWidth * gl.drawingBufferHeight * 4);
    gl.readPixels(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight, gl.RGBA, gl.UNSIGNED_BYTE, b);
    return b;
  };
  // TWO INSTANCES OF ONE PLANE WITH depthTest OFF, the first red and 3 m behind a room's back wall, the
  // second blue and inside the room. The plane has four 40 m segments, and every ray meets the first
  // instance on its last segment and the second on its first, so taken face by face the red one came
  // last. The renderer draws instance 0 and then instance 1, and the room is blue.
  const instanced = await (async () => {
    const Ri = world(40);
    TXT.frame(Ri, { from: [0, 1.6, 4], look: [0, 1.6, -5] }); TXT.interior(Ri, {});
    TXT.rig(Ri, { key: Object.assign({}, W.rig.key, { pos: [2, 6, 2] }), ambient: W.rig.ambient });
    const im = new T.InstancedMesh(new T.PlaneGeometry(160, 40, 4, 1),
      new T.MeshBasicMaterial({ transparent: true, depthTest: false, toneMapped: false }), 2);
    const m = new T.Matrix4();
    im.setMatrixAt(0, m.makeTranslation(-60, 1.6, -8)); im.setMatrixAt(1, m.makeTranslation(60, 1.6, 0));
    im.setColorAt(0, new T.Color(1, 0, 0)); im.setColorAt(1, new T.Color(0, 0, 1));
    im.instanceMatrix.needsUpdate = true; im.instanceColor.needsUpdate = true;
    Ri.scene.add(im);
    const errors = await capture(() => TXT.snapshot(Ri));
    const b = pixels(Ri), gl = Ri.renderer.getContext();
    const c = (Math.floor(gl.drawingBufferHeight / 2) * gl.drawingBufferWidth + Math.floor(gl.drawingBufferWidth / 2)) * 4;
    return { errors, share: TXT.roomShare(Ri), centre: [b[c], b[c + 1], b[c + 2]] };
  })();
  // A WALL 10 M OUT UNDER A CHAIN CLEAR AT LEVEL 0 AND SOLID BELOW, its texture turned 45 degrees and
  // repeated 32 times more one way than the other. So the steps one pixel across and one up are as
  // long as each other and nearly parallel, 18.4 texels. SwiftShader takes the stretch as the longer
  // step squared over the area they span, 16 at this anisotropy, and samples 16 times at level 0.19,
  // the clear one. Comparing the steps' lengths read level 4.2, the solid one.
  const chain = (aniso) => {
    const mips = [];
    for (let n = 128, i = 0; n >= 1; n >>= 1, i++) {
      const d = new Uint8Array(n * n * 4);
      for (let k = 0; k < n * n; k++) { d[k * 4] = d[k * 4 + 1] = d[k * 4 + 2] = 90; d[k * 4 + 3] = i ? 255 : 0; }
      mips.push({ data: d, width: n, height: n });
    }
    const t = new T.DataTexture(mips[0].data, 128, 128, T.RGBAFormat, T.UnsignedByteType);
    t.mipmaps = mips; t.generateMipmaps = false; t.wrapS = t.wrapT = T.RepeatWrapping;
    t.repeat.set(1506, 1506 / 32); t.rotation = Math.PI / 4;
    t.minFilter = T.LinearMipmapLinearFilter; t.magFilter = T.LinearFilter; t.anisotropy = aniso; t.needsUpdate = true;
    return t;
  };
  const skewed = async (aniso) => {
    const Rs = world(40);
    TXT.frame(Rs, { from: [0, 2, 0], look: [0, 2, -100] });
    const dome = TXT.sky(Rs, W);
    TXT.rig(Rs, { key: Object.assign({}, W.rig.key, { pos: [20, 40, 20] }), ambient: W.rig.ambient });
    TXT.ground(Rs, { surface: 'caliche', size: 900, tile: 5 });
    const wall = new T.Mesh(new T.PlaneGeometry(40, 40), new T.MeshBasicMaterial({ map: chain(aniso), alphaTest: 0.5, side: T.DoubleSide }));
    wall.position.set(0, 2, -10); Rs.scene.add(wall);
    const errors = await capture(() => TXT.snapshot(Rs));
    const shown = pixels(Rs); dome.visible = false; const hidden = pixels(Rs); dome.visible = true; pixels(Rs);
    let n = 0;
    for (let i = 0; i < shown.length; i += 4)
      if (Math.max(Math.abs(shown[i] - hidden[i]), Math.abs(shown[i + 1] - hidden[i + 1]), Math.abs(shown[i + 2] - hidden[i + 2])) > 8) n++;
    const caps = Rs.renderer.capabilities;
    return { errors, sky: TXT.skyInFrame(Rs.camera, Rs), gpuSky: n / (shown.length / 4), max: caps.getMaxAnisotropy() };
  };
  const aniso = await skewed(16), iso = await skewed(1);
  return { instanced, aniso, iso };
}`;

// THE GRASS LETS THE LIGHT THROUGH, AND IS MORE THAN ONE TUFT (2026-10-03). Carousel no. 39's craft
// judge named "one repeated tuft sprite" in every round, and a field seen into the sun printed black
// stubble on two frames for three rounds. A field at eye height in golden hour, looked at into the sun
// and away from it: the grass pixels are the ones that change when the field is hidden. Measured on
// 2026-10-03 through the engine before this, into the sun 52.6 and away 88.5, a ratio of 0.59; through
// this one 85.3 and 89.8, 0.95.
const GRASS = `async (T, TXT, cv) => {
  const W = Object.assign({}, TXT.worlds.goldenHour);
  const field = async (into) => {
    const R = TXT.setup(cv, { w: 540, h: 675, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 40 });
    const s = TXT.sunDir(W), az = new T.Vector3(s.x, 0, s.z).normalize().multiplyScalar(into ? 1 : -1);
    TXT.frame(R, { from: [0, 1.6, 0], look: [az.x * 40, 0.2, az.z * 40] });
    TXT.sky(R, W);
    TXT.rig(R, { key: Object.assign({}, W.rig.key, { pos: [s.x * 60, Math.max(s.y * 60, 6), s.z * 60] }),
                 fill: W.rig.fill, ambient: W.rig.ambient });
    TXT.ground(R, { surface: 'caliche', size: 900, tile: 5 });
    const G = TXT.scatter(R, { kind: 'grass', count: 9000, area: [-25, -25, 25, 25], seed: 5, scale: [0.35, 0.7], nearRadius: 6 });
    await TXT.snapshot(R);
    const gl = R.renderer.getContext(), Wd = gl.drawingBufferWidth, H = gl.drawingBufferHeight;
    const read = () => { const b = new Uint8Array(Wd * H * 4); gl.readPixels(0, 0, Wd, H, gl.RGBA, gl.UNSIGNED_BYTE, b); return b; };
    const withG = read();
    G.visible = false; R.renderer.render(R.scene, R.camera);
    const bare = read();
    let sum = 0, n = 0;
    for (let i = 0; i < withG.length; i += 4) {
      if (Math.abs(withG[i] - bare[i]) + Math.abs(withG[i + 1] - bare[i + 1]) + Math.abs(withG[i + 2] - bare[i + 2]) > 12) {
        sum += 0.2126 * withG[i] + 0.7152 * withG[i + 1] + 0.0722 * withG[i + 2]; n++;
      }
    }
    const parts = G.isGroup ? G.children : [G];
    return { lum: n ? sum / n : 0, px: n, tufts: new Set(parts.map((c) => c.geometry.uuid)).size,
             placed: parts.reduce((a, c) => a + c.count, 0), instanced: parts.every((c) => c.isInstancedMesh) };
  };
  return { into: await field(true), away: await field(false) };
}`;

// THE SKY ABOVE A SUNSET IS NOT MAUVE (2026-10-03). The sun's glow was ADDED in its own orange over a
// dim blue sky, which raised the red and left the blue, so looking at the sun the sky printed rose and
// then mauve: blue hour measured hue 8, 356 and 343 at saturation 0.20 to 0.28 in the bands from 6 to
// 40 percent of the frame over the horizon, and golden hour hue 5 at 0.13. Carousel no. 39's chassis
// had to switch the glow nearly off. The bands are read here as mean colours, toward the sun.
const SKYHUE = `async (T, TXT, cv) => {
  const out = {};
  for (const name of ['blueHour', 'goldenHour']) {
    const W = Object.assign({}, TXT.worlds[name]);
    const R = TXT.setup(cv, { w: 540, h: 675, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 50 });
    const s = TXT.sunDir(W), az = new T.Vector3(s.x, 0, s.z).normalize();
    TXT.frame(R, { from: [0, 1.6, 0], look: [az.x * 100, 1.6 + 100 * Math.tan(12 * Math.PI / 180), az.z * 100] });
    TXT.sky(R, W);
    TXT.rig(R, { key: Object.assign({}, W.rig.key, { pos: [s.x * 60, Math.max(s.y * 60, 6), s.z * 60] }),
                 fill: W.rig.fill, ambient: W.rig.ambient });
    TXT.ground(R, { surface: 'caliche', size: 900, tile: 5 });
    await TXT.snapshot(R);
    const gl = R.renderer.getContext(), Wd = gl.drawingBufferWidth, H = gl.drawingBufferHeight;
    const b = new Uint8Array(Wd * H * 4); gl.readPixels(0, 0, Wd, H, gl.RGBA, gl.UNSIGNED_BYTE, b);
    const v = new T.Vector3(az.x * 5000, 1.6, az.z * 5000).project(R.camera);
    const hy = Math.round((v.y * 0.5 + 0.5) * H);
    out[name] = [[0.06, 0.14], [0.14, 0.26], [0.26, 0.40]].map(([a, z]) => {
      let r = 0, g = 0, bl = 0, n = 0;
      for (let y = hy + Math.round(a * H); y < Math.min(H, hy + Math.round(z * H)); y++)
        for (let x = Math.floor(Wd * 0.1); x < Math.floor(Wd * 0.9); x += 2) { const i = (y * Wd + x) * 4; r += b[i]; g += b[i + 1]; bl += b[i + 2]; n++; }
      return [a, z, r / n, g / n, bl / n];
    });
  }
  return out;
}`;

const PREINSTALLED = process.env.CHROME_PATH || process.env.PLAYWRIGHT_CHROMIUM || '/opt/pw-browsers/chromium';
const browser = await chromium.launch(Object.assign(
  { args: ['--allow-file-access-from-files', '--enable-unsafe-swiftshader', '--force-color-profile=srgb'] },
  existsSync(PREINSTALLED) ? { executablePath: PREINSTALLED } : {}));
const scratch = join(ROOT, 'out', 'txworld');
mkdirSync(scratch, { recursive: true });

// A STAGED WORLD (2026-10-04): the subject lit, the ground beside it and the world behind it gone to
// the dark (TXT.stage). A 6 x 3 x 2.4 m box on a concrete ground in lastLight, from 23 m at 1.6 m,
// with a building 60 m straight behind it, a flat pad under it and a field off to the left, which is
// land cover and never the subject. Rendered staged, then with stage:false on the same camera, then
// the same scene in goldenHour, which has no stage and must not get one. Every sampled point is found
// on screen first and reported off screen as null, so no check can pass on a point it never read.
const STAGE = `async (T, TXT, cv) => {
  const shoot = async (name, staged, cab) => {
    const W = Object.assign({}, TXT.worlds[name]);
    const R = TXT.setup(cv, { w: 540, h: 675, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 36 });
    const eye = [14, 1.6, 18];
    TXT.frame(R, { from: eye, look: [0, 1.3, 0] });
    TXT.sky(R, W);
    const s = TXT.sunDir(W);
    TXT.rig(R, { key: Object.assign({}, W.rig.key, { pos: [s.x * 60, Math.max(s.y * 60, 6), s.z * 60] }),
                 rim: W.rig.rim, fill: W.rig.fill, ambient: W.rig.ambient });
    TXT.ground(R, { surface: 'concrete', size: 900, tile: 3 });
    const mat = (c) => new T.MeshStandardMaterial({ color: c, roughness: 0.7 });
    const pad = new T.Mesh(new T.BoxGeometry(40, 0.1, 40), mat(0x8f8b84)); pad.position.set(0, -0.045, 0); TXT.add(R, pad);
    const field = new T.Mesh(new T.BoxGeometry(60, 1.0, 60), mat(0x6d6a3c)); field.position.set(-60, 0.5, -10); TXT.add(R, field);
    const box = new T.Mesh(new T.BoxGeometry(6, 3, 2.4), mat(0xd8d0c0)); box.name = 'subject'; box.position.set(0, 1.5, 0); TXT.add(R, box);
    const dh = new T.Vector3(-eye[0], 0, -eye[2]).normalize();
    const far = new T.Mesh(new T.BoxGeometry(30, 24, 10), mat(0xd0c8b8)); far.position.set(dh.x * 60, 12, dh.z * 60);
    far.lookAt(eye[0], 12, eye[2]); TXT.add(R, far);
    if (cab) {   // the camera in a cab: a hood below the lens and a roof above it, one object around the eye
      const c = new T.Group(), hood = new T.Mesh(new T.BoxGeometry(2.4, 1.0, 2.4), mat(0x2a2c30)), roof = hood.clone();
      hood.position.set(eye[0] + dh.x * 1.6, 0.8, eye[2] + dh.z * 1.6); roof.position.set(eye[0], 3.2, eye[2]);
      c.add(hood, roof); TXT.add(R, c);
    }
    const shot = await TXT.snapshot(R, staged ? {} : { stage: false });
    const gl = R.renderer.getContext(), Wd = gl.drawingBufferWidth, H = gl.drawingBufferHeight;
    const px = new Uint8Array(Wd * H * 4); gl.readPixels(0, 0, Wd, H, gl.RGBA, gl.UNSIGNED_BYTE, px);
    const lin = (c) => { c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
    const L = (i) => { const y = 0.2126 * lin(px[i]) + 0.7152 * lin(px[i + 1]) + 0.0722 * lin(px[i + 2]);
      return y > 0.008856 ? 116 * Math.cbrt(y) - 16 : 903.3 * y; };
    let mid = 0, dark = 0, n = 0;
    for (let i = 0; i < px.length; i += 16) { const l = L(i); n++; if (l < 15) dark++; else if (l <= 70) mid++; }
    const patch = (nx, ny) => { const x = Math.round((nx + 1) / 2 * Wd), y = Math.round((ny + 1) / 2 * H);
      if (x < 6 || y < 6 || x >= Wd - 6 || y >= H - 6) return null; let t = 0, k = 0;
      for (let dy = -4; dy <= 4; dy++) for (let dx = -4; dx <= 4; dx++) { t += L(((y + dy) * Wd + x + dx) * 4); k++; }
      return t / k; };
    const at = (p) => { const v = new T.Vector3(p[0], p[1], p[2]).project(R.camera); return v.z < 1 ? patch(v.x, v.y) : null; };
    // the ground 15 m behind the subject and 8 m to its side, clear of the box on screen
    const side = new T.Vector3(dh.z, 0, -dh.x);
    const beside = at([dh.x * 15 + side.x * 8, 0, dh.z * 15 + side.z * 8]);
    return { ok: shot.ok, mid: mid / n, dark: dark / n, box: at([0, 1.5, 1.2]), beside,
             behind: at([dh.x * 55, 16, dh.z * 55]), staged: R._txStaged || null };
  };
  return { staged: await shoot('lastLight', true), plain: await shoot('lastLight', false),
           golden: await shoot('goldenHour', true), cab: await shoot('lastLight', true, true) };
}`;

async function run(name, scene) {
  const file = join(scratch, `${name}.html`);
  writeFileSync(file, page_html(scene));
  const page = await browser.newPage({ viewport: { width: 540, height: 675 }, deviceScaleFactor: 2 });
  const consoleErrors = [], pageErrors = [];
  page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text()); });
  page.on('pageerror', (e) => pageErrors.push(String(e)));
  await page.goto(pathToFileURL(file).href, { waitUntil: 'load' });
  // != null, never !== null: before the module runs, __result is undefined, and a wait on !== null
  // passed at once on a slower browser and read nothing (found on the headless shell CI uses).
  await page.waitForFunction(() => window.__result != null, null, { timeout: 300000 });
  const result = await page.evaluate(() => window.__result);
  await page.close();
  return { result, consoleErrors, pageErrors };
}

console.log(`txworld: the engine at ${ENGINE}`);
for (const [size, surface] of [[900, true], [12000, false]]) {
  const h = await run(`horizon_${size}`, HORIZON(size, surface));
  const other = h.consoleErrors.filter((e) => !e.startsWith('TXT: SKY IN FRAME'));
  check(`${size} m ground: the world renders with no page error and no shader error`,
        !h.result.error && h.pageErrors.length === 0 && other.length === 0,
        JSON.stringify({ error: h.result.error, page: h.pageErrors, console: other.slice(0, 3) }));
  check(`${size} m ground: ...and its snapshot prints the engine's clean verdict, one line`,
        h.consoleErrors.length === 1 && h.consoleErrors[0].startsWith('TXT: SKY IN FRAME'),
        JSON.stringify(h.consoleErrors));
  check(`${size} m ground: the render is a real frame, not black`, h.result.ok === true, JSON.stringify(h.result));
  check(`${size} m ground: no step across the horizon, the largest row to row change is ` +
        `${(h.result.step || 0).toFixed(1)} levels (at ${h.result.at} rows from mid frame), under ${MAX_STEP}`,
        h.result.step < MAX_STEP, JSON.stringify(h.result));
  check(`${size} m ground: the fog is the sky, the fog chunk mixes toward txSkyFog`, h.result.chunk === true);
  check(`${size} m ground: the ground is really under the lower band, a ray there meets it`,
        h.result.groundHit === true, JSON.stringify(h.result));
  check(`${size} m ground: ...and hiding it changes the band by ${(h.result.groundDiff || 0).toFixed(1)} levels, ` +
        `over ${MIN_GROUND_DIFF}`, h.result.groundDiff > MIN_GROUND_DIFF, JSON.stringify(h.result));
}

const g = await run('ground_only', GROUND_ONLY);
const e = await run('enclosure', ENCLOSURE);
check('the enclosure page renders with no page error and no scene error',
      !e.result.error && e.pageErrors.length === 0, JSON.stringify({ error: e.result.error, page: e.pageErrors }));
check('a camera looking straight down shows no sky', g.result.sky === 0, JSON.stringify(g.result));
check('an orthographic camera pitched 5 degrees down shows no sky, and says so',
      g.result.orthoSky === 0 && Array.isArray(g.result.orthoErrors) &&
      g.result.orthoErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify({ orthoSky: g.result.orthoSky, orthoErrors: g.result.orthoErrors }));
check('a camera zoomed out to 0.5 and pitched 45 degrees down shows no sky, and says so',
      g.result.zoomSky === 0 && Array.isArray(g.result.zoomErrors) &&
      g.result.zoomErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify({ zoomSky: g.result.zoomSky, zoomErrors: g.result.zoomErrors }));
check('a portrait camera rolled 90 degrees and pitched 18 down shows no sky, and says so',
      g.result.rollSky === 0 && Array.isArray(g.result.rollErrors) &&
      g.result.rollErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify({ rollSky: g.result.rollSky, rollErrors: g.result.rollErrors }));
check('a shelter under a hidden parent is no shelter: looking down inside it IS flagged',
      Array.isArray(g.result.hiddenErrors) &&
      g.result.hiddenErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify(g.result.hiddenErrors));
{
  const pe = Array.isArray(g.result.previewErrors) ? g.result.previewErrors : [];
  const tag = (e) => (e.match(/\[r\d+\]/) || [''])[0];
  check('a preview at the ground is withdrawn by the same renderer\'s kept snapshot at the horizon',
        pe.length === 2 && pe[0].startsWith('TXT: NO SKY IN FRAME') && g.result.shown === 'TXT: SKY IN FRAME' &&
        pe[1].startsWith('TXT: SKY IN FRAME') && tag(pe[0]) !== '' && tag(pe[0]) === tag(pe[1]),
        JSON.stringify(pe));
}
{
  const ce = Array.isArray(g.result.crossErrors) ? g.result.crossErrors : [];
  const tag = (e) => (e.match(/\[r\d+\]/) || [''])[0];
  check('a preview at the ground on one renderer is withdrawn by the kept snapshot on another',
        ce.length === 2 && ce[0].startsWith('TXT: NO SKY IN FRAME') && ce[1].startsWith('TXT: SKY IN FRAME') &&
        tag(ce[0]) !== '' && tag(ce[1]) !== '' && tag(ce[0]) !== tag(ce[1]), JSON.stringify(ce));
}
check('a sky dome hidden before the kept snapshot is no sky: the frame IS flagged',
      Array.isArray(g.result.domeErrors) && g.result.domeErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify(g.result.domeErrors));
check('a shelter at zero opacity is no shelter: looking down inside it IS flagged',
      Array.isArray(g.result.glassErrors) && g.result.glassErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify(g.result.glassErrors));
check('there is no option to skip the check: skyCheck false on the kept snapshot is still judged',
      Array.isArray(g.result.optErrors) && g.result.optErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify(g.result.optErrors));
{
  const le = Array.isArray(g.result.layerErrors) ? g.result.layerErrors : [];
  check('a shelter on a layer the camera doesn\'t render is no shelter, and the same shelter on its layer is',
        le.length === 2 && le[0].startsWith('TXT: NO SKY IN FRAME') && le[1].startsWith('TXT: SKY IN FRAME'),
        JSON.stringify(le));
}
check('a sky dome on a layer the camera doesn\'t render is no sky: the frame IS flagged',
      Array.isArray(g.result.veilErrors) && g.result.veilErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify(g.result.veilErrors));
check('a room on a layer the camera doesn\'t render is no room: looking down inside it IS flagged',
      Array.isArray(g.result.wallErrors) && g.result.wallErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify(g.result.wallErrors));
check('a room the camera has left exempts nothing: looking down 40 m away IS flagged',
      Array.isArray(g.result.outsideErrors) &&
      g.result.outsideErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify(g.result.outsideErrors));
check('a deliberate interior looked down on is a room, and is NOT flagged',
      Array.isArray(g.result.roomErrors) && !g.result.roomErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify(g.result.roomErrors));
check(`a camera inside a shelter the frame built looks down from inside, and is NOT flagged ` +
      `(it covers ${g.result.shelterCover} of the sky above the camera)`,
      g.result.shelterCover >= 0.8 && Array.isArray(g.result.roofErrors) &&
      !g.result.roofErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify({ cover: g.result.shelterCover, errors: g.result.roofErrors }));
check(`a carport roof alone is not an interior: looking down beneath it IS flagged ` +
      `(it covers ${(e.result.carportCover || 0).toFixed(2)} of the sky above the camera)`,
      e.result.carportCover < 0.8 && Array.isArray(e.result.carportErrors) &&
      e.result.carportErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify({ cover: e.result.carportCover, errors: e.result.carportErrors }));
check('a lamp head straight over the camera is no roof: looking down beneath it IS flagged',
      Array.isArray(e.result.lampErrors) && e.result.lampErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify(e.result.lampErrors));
check(`a shelter whose boxes show one material slot in six is no shelter: the frame IS flagged ` +
      `(it covers ${(e.result.slotCover || 0).toFixed(2)} of the sky above the camera)`,
      e.result.slotCover < 0.8 && Array.isArray(e.result.slotErrors) &&
      e.result.slotErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify({ cover: e.result.slotCover, errors: e.result.slotErrors }));
check('a shell 8 m out, past a 5 m far plane, is in no pixel and is no shelter: the frame IS flagged',
      Array.isArray(e.result.farPlaneErrors) && e.result.farPlaneErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify(e.result.farPlaneErrors));
check('a shelter a clipping plane cuts away is no shelter: the frame IS flagged',
      Array.isArray(e.result.clipErrors) && e.result.clipErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify(e.result.clipErrors));
check('a frame that builds only a room and faces its back wall prints the room\'s clean verdict',
      Array.isArray(e.result.roomOnlyErrors) && e.result.roomOnlyErrors.length === 1 &&
      e.result.roomOnlyErrors[0].startsWith('TXT: ROOM IN FRAME'), JSON.stringify(e.result.roomOnlyErrors));
check('...the same room hidden before the kept snapshot prints the no-room line',
      Array.isArray(e.result.roomHiddenErrors) && e.result.roomHiddenErrors.some((e) => e.startsWith('TXT: NO ROOM IN FRAME')),
      JSON.stringify(e.result.roomHiddenErrors));
check('...and so does the room seen from 300 m straight above',
      Array.isArray(e.result.roomFarErrors) && e.result.roomFarErrors.some((e) => e.startsWith('TXT: NO ROOM IN FRAME')),
      JSON.stringify(e.result.roomFarErrors));
check('a render that comes out black prints no render, never a clean verdict',
      e.result.blackOk === false && Array.isArray(e.result.blackErrors) && e.result.blackErrors.length === 1 &&
      e.result.blackErrors[0].startsWith('TXT: NO RENDER IN FRAME'),
      JSON.stringify({ ok: e.result.blackOk, errors: e.result.blackErrors }));
{
  const cc = e.result.clearCut || {}, bm = e.result.blackMask || {}, sc = e.result.solidCut || {};
  const flagged = (r) => Array.isArray(r.errors) && r.errors.some((e) => e.startsWith('TXT: NO SKY IN FRAME'));
  check(`a shelter of alpha-tested cutouts with a clear texture draws nothing and is no shelter ` +
        `(it covers ${cc.cover} of the sky above the camera)`, cc.cover === 0 && flagged(cc), JSON.stringify(cc));
  check(`...nor is one whose alphaMap is black (it covers ${bm.cover})`, bm.cover === 0 && flagged(bm), JSON.stringify(bm));
  check(`...while the same cutouts with an opaque texture are a shelter (they cover ${sc.cover})`,
        sc.cover >= 0.8 && !flagged(sc), JSON.stringify(sc));
  const wf = e.result.wire || {}, rd = e.result.redraw || {};
  const cv2 = e.result.clearVerts || {}, sv2 = e.result.solidVerts || {};
  check(`a transparent shelter whose vertex alpha is 0 shows nothing and is no shelter (it covers ${cv2.cover})`,
        cv2.cover === 0 && flagged(cv2), JSON.stringify(cv2));
  check(`...while the same shelter at vertex alpha 1 is one (it covers ${sv2.cover})`,
        sv2.cover >= 0.8 && !flagged(sv2), JSON.stringify(sv2));
  check(`a wireframe shelter draws its edges and not its faces, and is no shelter (it covers ${wf.cover})`,
        wf.cover === 0 && flagged(wf), JSON.stringify(wf));
  check('a cutout cleared between the preview and the kept snapshot is no shelter in the kept frame',
        Array.isArray(rd.errors) && rd.errors.length === 2 && rd.errors[0].startsWith('TXT: SKY IN FRAME') &&
        rd.errors[1].startsWith('TXT: NO SKY IN FRAME') && rd.cover === 0, JSON.stringify(rd));
}
check('a room 300 m straight below the camera is no interior shot: the frame IS flagged',
      Array.isArray(e.result.farErrors) && e.result.farErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify(e.result.farErrors));
check('...and the engine says so on the console, in the words print_ban reads',
      g.consoleErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')) && g.result.marker === 'TXT: NO SKY IN FRAME',
      JSON.stringify(g.consoleErrors));

const x = await run('sampled', SAMPLED);
check('the sampled page renders with no page error and no scene error',
      !x.result.error && x.pageErrors.length === 0, JSON.stringify({ error: x.result.error, page: x.pageErrors }));
{
  // Each cutout shelter is a shelter exactly when the GPU draws its material (Codex, PR 369). The
  // first reader divided every stored value by 255, which read the half floats, the 16-bit textures
  // three.js never uploads, the sRGB alphaMap and the red alphaMap all wrong.
  const tx = x.result.texels || {};
  const flagged = (r) => Array.isArray(r.errors) && r.errors.some((e) => e.startsWith('TXT: NO SKY IN FRAME'));
  const says = {
    half04: 'a half-float alphaMap at 0.4, under alphaTest 0.5',
    half06: 'a half-float alphaMap at 0.6',
    u16mask: 'a 16-bit alphaMap three.js never uploads, which samples a green of 0',
    u16map: 'a 16-bit map three.js never uploads, which samples an alpha of 1 and draws black',
    srgb180: 'an sRGB alphaMap whose green of 180 decodes to 0.46',
    lin180: 'the same alphaMap read linear, 0.71',
    red255: 'a red alphaMap, which samples a green of 0',
  };
  const expect = { half04: false, half06: true, u16mask: false, u16map: true, srgb180: false, lin180: true, red255: false };
  for (const k of Object.keys(expect)) {
    const r = tx[k] || {};
    const wall = r.cover >= 0.8;
    check(`${says[k]}: the GPU ${expect[k] ? 'draws it' : 'discards it'}, and the shelter ` +
          `${expect[k] ? 'is one' : 'is none'} (it covers ${r.cover})`,
          r.gpu === expect[k] && wall === expect[k] && flagged(r) === !expect[k], JSON.stringify(r));
  }
}
check(`an orthographic frustum 200 m tall pitched 5 degrees down shows sky in its upper rows ` +
      `(${(x.result.tallSky || 0).toFixed(3)} of the frame), and says so`,
      x.result.tallSky > 0 && Array.isArray(x.result.tallErrors) && x.result.tallErrors.length === 1 &&
      x.result.tallErrors[0].startsWith('TXT: SKY IN FRAME'),
      JSON.stringify({ sky: x.result.tallSky, errors: x.result.tallErrors }));
{
  const sw = x.result.solidWall || {}, gw = x.result.glassWall || {}, cw = x.result.cutWall || {};
  check(`a solid wall filling the frame hides the sky: facing the horizon behind it IS flagged ` +
        `(sky ${sw.sky}, cover ${sw.cover})`,
        sw.sky === 0 && Array.isArray(sw.errors) && sw.errors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
        JSON.stringify(sw));
  check(`...while the sky shows through the same wall as half-opaque glass (sky ${gw.sky})`,
        gw.sky > 0 && Array.isArray(gw.errors) && gw.errors.length === 1 && gw.errors[0].startsWith('TXT: SKY IN FRAME'),
        JSON.stringify(gw));
  check(`...and through it as a cutout that draws nothing (sky ${cw.sky})`,
        cw.sky > 0 && Array.isArray(cw.errors) && cw.errors.length === 1 && cw.errors[0].startsWith('TXT: SKY IN FRAME'),
        JSON.stringify(cw));
}
check(`a room turned 45 degrees is measured on its own floor: looking down on the ground in front of ` +
      `its open side IS flagged (the room fills ${x.result.turnedShare} of the frame)`,
      x.result.turnedShare < 0.5 && Array.isArray(x.result.turnedErrors) &&
      x.result.turnedErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify({ share: x.result.turnedShare, errors: x.result.turnedErrors }));
check(`...while the same turned room, from inside facing its back wall, is a room ` +
      `(it fills ${x.result.turnedInShare} of the frame)`,
      x.result.turnedInShare >= 0.5 && Array.isArray(x.result.turnedInErrors) && x.result.turnedInErrors.length === 1 &&
      x.result.turnedInErrors[0].startsWith('TXT: ROOM IN FRAME'),
      JSON.stringify({ share: x.result.turnedInShare, errors: x.result.turnedInErrors }));

const f = await run('filtered', FILTERED);
check('the filtered page renders with no page error and no scene error',
      !f.result.error && f.pageErrors.length === 0, JSON.stringify({ error: f.result.error, page: f.pageErrors }));
{
  // AN ALPHA-HASHED SHELTER (Codex, PR 369) is drawn where its alpha clears three's hash threshold,
  // so a fifth of one at opacity 0.2 draws. The first cut took it for opaque and every ray for covered.
  const h2 = f.result.hash02 || {}, h9 = f.result.hash095 || {};
  const flagged = (r) => Array.isArray(r.errors) && r.errors.some((e) => e.startsWith('TXT: NO SKY IN FRAME'));
  check(`an alpha-hashed shelter at opacity 0.2: the GPU draws ${(h2.gpu || 0).toFixed(2)} of it, the shelter ` +
        `covers ${(h2.cover || 0).toFixed(2)} of the sky above the camera, and looking down inside it IS flagged`,
        Math.abs(h2.gpu - 0.2) < 0.06 && Math.abs(h2.cover - 0.2) < 0.06 && flagged(h2), JSON.stringify(h2));
  check(`...while at opacity 0.95 the GPU draws ${(h9.gpu || 0).toFixed(2)} of it and it covers ` +
        `${(h9.cover || 0).toFixed(2)}, an interior`,
        Math.abs(h9.gpu - 0.95) < 0.06 && h9.cover >= 0.8 && !flagged(h9), JSON.stringify(h9));
  // A MIPMAPPED CUTOUT (Codex, PR 369): the kit's perforated steel at 40 m draws as a solid sheet, no
  // sky in its pixels, and at 2 m its holes show the sky. The first cut read the base texel at any
  // distance and found sky through the far wall's holes.
  const pf = f.result.perfFar || {}, pn = f.result.perfNear || {};
  check(`the kit's perforated steel across the frame at 40 m: the pixels show ${(pf.gpuSky || 0).toFixed(4)} ` +
        `sky, the engine reads ${pf.sky}, and the frame IS flagged`,
        pf.gpuSky < 0.001 && pf.sky === 0 && Array.isArray(pf.errors) &&
        pf.errors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')), JSON.stringify(pf));
  check(`...while at 2 m its holes show ${(pn.gpuSky || 0).toFixed(3)} sky in the pixels, the engine reads ` +
        `${(pn.sky || 0).toFixed(3)}, and the frame shows its sky`,
        pn.gpuSky > 0.05 && pn.sky > 0.05 && Array.isArray(pn.errors) && pn.errors.length === 1 &&
        pn.errors[0].startsWith('TXT: SKY IN FRAME'), JSON.stringify(pn));
}

{
  // COINCIDENT HASHED SURFACES share their discards (Codex, PR 369), a SUPPLIED MIP CHAIN is the one
  // the GPU samples (Codex, PR 369), and a texture on UV CHANNEL 2 reads uv2 (Codex, PR 369).
  const st = f.result.stacked || {}, mf = f.result.mipFar || {}, mn = f.result.mipNear || {};
  const u2 = f.result.uv2 || {}, u0 = f.result.uv0 || {};
  const flagged = (r) => Array.isArray(r.errors) && r.errors.some((e) => e.startsWith('TXT: NO SKY IN FRAME'));
  check(`eight coincident alpha-hashed shelters at 0.2: the GPU draws ${(st.gpu || 0).toFixed(2)} of them, they cover ` +
        `${(st.cover || 0).toFixed(2)}, and looking down inside them IS flagged`,
        Math.abs(st.gpu - 0.2) < 0.06 && Math.abs(st.cover - 0.2) < 0.06 && flagged(st), JSON.stringify(st));
  check(`a wall whose supplied mip chain is clear at level 0 and solid below: at 40 m the pixels show ` +
        `${(mf.gpuSky || 0).toFixed(4)} sky, the engine reads ${mf.sky}, and the frame IS flagged`,
        mf.gpuSky < 0.001 && mf.sky === 0 && flagged(mf), JSON.stringify(mf));
  check(`...while at 2 m it is magnified onto the clear level: the pixels show ${(mn.gpuSky || 0).toFixed(3)} sky, ` +
        `the engine reads ${(mn.sky || 0).toFixed(3)}, and the frame shows its sky`,
        mn.gpuSky > 0.3 && mn.sky > 0.3 && Array.isArray(mn.errors) && mn.errors.length === 1 &&
        mn.errors[0].startsWith('TXT: SKY IN FRAME'), JSON.stringify(mn));
  check(`an alphaMap on UV channel 2 reads uv2: the GPU draws ${u2.gpu ? 'it' : 'none of it'}, and the shelter covers ` +
        `${(u2.cover || 0).toFixed(2)}, an interior`,
        u2.gpu === 1 && u2.cover >= 0.8 && !flagged(u2), JSON.stringify(u2));
  check(`...while the same alphaMap on channel 0 reads uv's clear texel: the GPU draws ${(u0.gpu || 0).toFixed(2)} of it, ` +
        `it covers ${(u0.cover || 0).toFixed(2)}, and the frame IS flagged`,
        u0.gpu === 0 && u0.cover === 0 && flagged(u0), JSON.stringify(u0));
}

const bl = await run('blended', BLENDED);
check('the blended page renders with no page error and no scene error',
      !bl.result.error && bl.pageErrors.length === 0, JSON.stringify({ error: bl.result.error, page: bl.pageErrors }));
{
  // A BLENDED SHELL COVERS BY ITS ALPHA (Codex, PR 369), and A SPRITE HIDES WHAT IS BEHIND IT (Codex,
  // PR 369). The first counted any shell above opacity 0.001 as a wall, and the second cast through
  // every sprite.
  const v1 = bl.result.veil001 || {}, v9 = bl.result.veil09 || {};
  const ss = bl.result.spriteSolid || {}, sc = bl.result.spriteClear || {};
  const flagged = (r) => Array.isArray(r.errors) && r.errors.some((e) => e.startsWith('TXT: NO SKY IN FRAME'));
  check(`a shelter blended at opacity 0.01 covers ${(v1.gpu || 0).toFixed(3)} of a pixel on the GPU and ` +
        `${(v1.cover || 0).toFixed(3)} of the sky above the camera, and looking down inside it IS flagged`,
        Math.abs(v1.gpu - 0.01) < 0.01 && Math.abs(v1.cover - 0.01) < 0.01 && flagged(v1), JSON.stringify(v1));
  check(`...while at 0.9 it covers ${(v9.gpu || 0).toFixed(2)} on the GPU and ${(v9.cover || 0).toFixed(2)} of the sky, an interior`,
        Math.abs(v9.gpu - 0.9) < 0.02 && Math.abs(v9.cover - 0.9) < 0.02 && !flagged(v9), JSON.stringify(v9));
  check(`an opaque sprite across the frame hides the sky: the pixels show ${(ss.gpuSky || 0).toFixed(4)} sky, ` +
        `the engine reads ${ss.sky}, and the frame IS flagged`,
        ss.gpuSky < 0.001 && ss.sky === 0 && flagged(ss), JSON.stringify(ss));
  check(`...while a clear one doesn't: the pixels show ${(sc.gpuSky || 0).toFixed(3)} sky, the engine reads ` +
        `${(sc.sky || 0).toFixed(3)}, and the frame shows its sky`,
        sc.gpuSky > 0.3 && sc.sky > 0.3 && Array.isArray(sc.errors) && sc.errors.length === 1 &&
        sc.errors[0].startsWith('TXT: SKY IN FRAME'), JSON.stringify(sc));
}

const ov = await run('overlaid', OVERLAID);
check('the overlaid page renders with no page error and no scene error',
      !ov.result.error && ov.pageErrors.length === 0, JSON.stringify({ error: ov.result.error, page: ov.pageErrors }));
{
  // A SHARED HASH STILL BLENDS EVERY SURVIVOR, A DEPTH-DISABLED SPRITE PAINTS OVER THE WALL, and A
  // SPRITE THAT KEEPS ITS SIZE KEEPS ITS MIP LEVEL (Codex, PR 372).
  const tw = ov.result.twin || {}, o1 = ov.result.over || {}, o0 = ov.result.under || {}, st = ov.result.steady || {};
  const flagged = (r) => Array.isArray(r.errors) && r.errors.some((e) => e.startsWith('TXT: NO SKY IN FRAME'));
  check(`two coincident shelters hashed and blended at 0.5 cover ${(tw.gpu || 0).toFixed(3)} on the GPU and ` +
        `${(tw.cover || 0).toFixed(3)} of the sky above the camera, where one merged draw made 0.25`,
        Math.abs(tw.gpu - 0.375) < 0.03 && Math.abs(tw.cover - 0.375) < 0.03 && flagged(tw), JSON.stringify(tw));
  check(`a sprite with depthTest off behind a room's back wall paints over it: the centre pixel is ` +
        `${JSON.stringify(o1.centre)}, the room fills ${(o1.share || 0).toFixed(2)} of the frame, and the frame IS flagged`,
        Array.isArray(o1.centre) && o1.centre[1] > 200 && o1.centre[0] < 60 && o1.share < 0.5 &&
        Array.isArray(o1.errors) && o1.errors.some((e) => e.startsWith('TXT: NO ROOM IN FRAME')), JSON.stringify(o1));
  check(`...while the same sprite depth-tested stays behind the wall: the room fills ${(o0.share || 0).toFixed(2)}`,
        Array.isArray(o0.centre) && !(o0.centre[1] > 200 && o0.centre[0] < 60) && o0.share >= 0.5 &&
        Array.isArray(o0.errors) && o0.errors.length === 1 && o0.errors[0].startsWith('TXT: ROOM IN FRAME'), JSON.stringify(o0));
  check(`a sprite that doesn't attenuate, 400 m out over a chain clear at level 0, is magnified onto that ` +
        `level: the pixels show ${(st.gpuSky || 0).toFixed(3)} sky, the engine reads ${(st.sky || 0).toFixed(3)}, and the frame shows its sky`,
        st.gpuSky > 0.3 && st.sky > 0.3 && Array.isArray(st.errors) && st.errors.length === 1 &&
        st.errors[0].startsWith('TXT: SKY IN FRAME'), JSON.stringify(st));
}

const od = await run('ordered', ORDERED);
check('the ordered page renders with no page error and no scene error',
      !od.result.error && od.pageErrors.length === 0, JSON.stringify({ error: od.result.error, page: od.pageErrors }));
{
  // THE RENDERER'S OWN ORDER, and THE STEP A PIXEL TAKES (Codex, PR 373).
  const r = od.result, pn = r.pane || {}, b0 = r.before || {}, b1 = r.after || {}, hs = r.hashed || {};
  const sp = r.sprite || {}, wl = r.wall || {}, sk = r.skewed || {}, ly = r.layered || {};
  const said = (x, v) => Array.isArray(x.errors) && x.errors.length === 1 && x.errors[0].startsWith(v);
  const green = (c) => Array.isArray(c) && c[1] > 200 && c[0] < 60 && c[2] < 60;
  check(`a pane at 0.6 in front of a sprite with depthTest off blends back over it: the pixels are ` +
        `${(pn.blue || 0).toFixed(3)} pane, the room fills ${(pn.share || 0).toFixed(3)}, and the frame is a room`,
        Math.abs(pn.blue - 0.6) < 0.02 && Math.abs(pn.share - pn.blue) < 0.03 && said(pn, 'TXT: ROOM IN FRAME'), JSON.stringify(pn));
  check(`an opaque backdrop with depthTest off drawn before the walls is drawn over by them: the centre pixel is ` +
        `${JSON.stringify(b0.centre)}, the room fills ${(b0.share || 0).toFixed(2)}, and the frame is a room`,
        !green(b0.centre) && b0.share >= 0.5 && said(b0, 'TXT: ROOM IN FRAME'), JSON.stringify(b0));
  check(`...while drawn after them it paints over them: the centre pixel is ${JSON.stringify(b1.centre)}, ` +
        `the room fills ${(b1.share || 0).toFixed(2)}, and the frame IS flagged`,
        green(b1.centre) && b1.share < 0.5 && said(b1, 'TXT: NO ROOM IN FRAME'), JSON.stringify(b1));
  check(`four coincident hashed overlays at 0.5 with depthTest off share one threshold: the GPU's cover is ` +
        `${(hs.gpuCover || 0).toFixed(3)}, the room fills ${(hs.share || 0).toFixed(3)} of ${(hs.bare || 0).toFixed(3)}, ` +
        `and the frame is a room`,
        Math.abs(hs.gpuCover - 0.469) < 0.04 && Math.abs(hs.share - hs.bare * (1 - hs.gpuCover)) < 0.04 &&
        said(hs, 'TXT: ROOM IN FRAME'), JSON.stringify(hs));
  check(`a sprite that doesn't attenuate, seen through a 90 degree lens, keeps the clear level edge to edge: ` +
        `the pixels show ${(sp.gpuSky || 0).toFixed(3)} sky and the engine reads ${(sp.sky || 0).toFixed(3)}`,
        sp.gpuSky > 0.45 && Math.abs(sp.sky - sp.gpuSky) < 0.05 && said(sp, 'TXT: SKY IN FRAME'), JSON.stringify(sp));
  check(`a wall seen through the same lens keeps it too: the pixels show ${(wl.gpuSky || 0).toFixed(3)} sky ` +
        `and the engine reads ${(wl.sky || 0).toFixed(3)}`,
        wl.gpuSky > 0.45 && Math.abs(wl.sky - wl.gpuSky) < 0.05 && said(wl, 'TXT: SKY IN FRAME'), JSON.stringify(wl));
  check(`...while repeated 48 times across and 12 up it is read at the larger step, the solid level: the pixels ` +
        `show ${(sk.gpuSky || 0).toFixed(4)} sky, the engine reads ${(sk.sky || 0).toFixed(3)}, and the frame IS flagged`,
        sk.gpuSky < 0.01 && sk.sky === 0 && said(sk, 'TXT: NO SKY IN FRAME'), JSON.stringify(sk));
  check(`a solid wall drawn after a half-clear one in front of it fails its depth test behind it: the pixels ` +
        `show the sky in ${(ly.gpuSky || 0).toFixed(3)} of the frame, the engine reads ${(ly.sky || 0).toFixed(3)} ` +
        `through the half-clear one, and the frame shows its sky`,
        ly.gpuSky > 0.4 && Math.abs(ly.sky - ly.gpuSky / 2) < 0.04 && said(ly, 'TXT: SKY IN FRAME'), JSON.stringify(ly));
}

const st = await run('stepped', STEPPED);
check('the stepped page renders with no page error and no scene error',
      !st.result.error && st.pageErrors.length === 0, JSON.stringify({ error: st.result.error, page: st.pageErrors }));
{
  // INSIDE ONE DRAW, and THE SAMPLES AN ANISOTROPIC TEXTURE TAKES (Codex, PR 374).
  const r = st.result, im = r.instanced || {}, an = r.aniso || {}, is = r.iso || {};
  const said = (x, v) => Array.isArray(x.errors) && x.errors.length === 1 && x.errors[0].startsWith(v);
  check(`an instanced draw runs instance by instance: the centre pixel is ${JSON.stringify(im.centre)}, the later ` +
        `instance, the room fills ${(im.share || 0).toFixed(2)}, and the frame is a room`,
        Array.isArray(im.centre) && im.centre[2] > 200 && im.centre[0] < 60 && im.share >= 0.5 &&
        said(im, 'TXT: ROOM IN FRAME'), JSON.stringify(im));
  check(`an anisotropic texture stretched along a diagonal is sampled at its fine level: the pixels show ` +
        `${(an.gpuSky || 0).toFixed(3)} sky, the engine reads ${(an.sky || 0).toFixed(3)}, and the frame shows its sky`,
        an.max >= 16 && an.gpuSky > 0.45 && Math.abs(an.sky - an.gpuSky) < 0.05 && said(an, 'TXT: SKY IN FRAME'), JSON.stringify(an));
  check(`...while the same wall without anisotropy is read at the longer step, the solid level: the pixels show ` +
        `${(is.gpuSky || 0).toFixed(4)} sky, the engine reads ${(is.sky || 0).toFixed(3)}, and the frame IS flagged`,
        is.gpuSky < 0.01 && is.sky === 0 && said(is, 'TXT: NO SKY IN FRAME'), JSON.stringify(is));
}

const gr = await run('grass', GRASS);
check('the grass page renders with no page error and no scene error',
      !gr.result.error && gr.pageErrors.length === 0, JSON.stringify({ error: gr.result.error, page: gr.pageErrors }));
{
  const a = gr.result.into || {}, b = gr.result.away || {};
  const ratio = b.lum ? a.lum / b.lum : 0;
  check(`grass seen into a low sun is lit through its blades: ${(a.lum || 0).toFixed(1)} into the sun against ` +
        `${(b.lum || 0).toFixed(1)} away from it, a ratio of ${ratio.toFixed(2)}, at least 0.80 (0.59 before)`,
        ratio >= 0.8 && a.px > 10000 && b.px > 10000, JSON.stringify(gr.result));
  check(`the field draws from ${a.tufts} tufts, at least 3, every one instanced, and keeps all ${a.placed} it placed`,
        a.tufts >= 3 && a.instanced === true && a.placed === b.placed && a.placed > 1000, JSON.stringify(gr.result));
}

const sh = await run('skyhue', SKYHUE);
check('the sky hue page renders with no page error and no scene error',
      !sh.result.error && sh.pageErrors.length === 0, JSON.stringify({ error: sh.result.error, page: sh.pageErrors }));
{
  const hs = (r, g, b) => { r /= 255; g /= 255; b /= 255; const mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn;
    if (!d) return [0, 0]; let h = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4;
    h *= 60; if (h < 0) h += 360; return [h, d / mx]; };
  // rose to mauve: from violet through magenta and pink to red, at a saturation a reader sees as colour
  const mauve = ([h, sat]) => sat >= 0.12 && (h >= 285 || h <= 12);
  for (const name of ['blueHour', 'goldenHour']) {
    const bands = (sh.result[name] || []).map(([a, z, r, g, b]) => ({ a, z, hs: hs(r, g, b) }));
    const bad = bands.filter((x) => mauve(x.hs));
    check(`${name}, looking at the sun, prints no rose or mauve between 6 and 40 percent of the frame over the ` +
          `horizon: ${bands.map((x) => `${Math.round(x.hs[0])} at ${x.hs[1].toFixed(2)}`).join(', ')}`,
          bands.length === 3 && bad.length === 0, JSON.stringify(sh.result[name]));
  }
}

const sg = await run('stage', STAGE);
check('the stage page renders with no page error and no scene error',
      !sg.result.error && sg.pageErrors.length === 0, JSON.stringify({ error: sg.result.error, page: sg.pageErrors }));
{
  const a = sg.result.staged || {}, b = sg.result.plain || {}, g = sg.result.golden || {};
  const st = a.staged || {};
  check(`a staged world stages its snapshot on the subject, never the pad or the field: it took ` +
        `${JSON.stringify(st.subject)} and laid ${st.pool ? 'a' : 'no'} pool, the fog from ${(st.near || 0).toFixed(1)} m to ${(st.far || 0).toFixed(1)} m`,
        st.subject === 'subject' && st.pool === true && st.near > 22 && st.near < 30, JSON.stringify(st));
  check(`staged, ${(a.mid * 100).toFixed(1)} percent of the frame sits in the mid tones and ${(a.dark * 100).toFixed(1)} ` +
        `is near black, against ${(b.mid * 100).toFixed(1)} and ${(b.dark * 100).toFixed(1)} unstaged`,
        a.mid < 0.3 && a.dark > 0.4 && b.mid - a.mid > 0.15, JSON.stringify({ a, b }));
  const num = (x) => typeof x === 'number' && x >= 0;
  const f = (x) => (num(x) ? x.toFixed(1) : String(x));
  check(`the subject keeps its light: L* ${f(a.box)} staged against ${f(b.box)}`,
        num(a.box) && num(b.box) && a.box > 50 && a.box >= b.box * 0.85, JSON.stringify({ a: a.box, b: b.box }));
  check(`the ground behind it, off to the side, goes to the dark: L* ${f(a.beside)} staged against ${f(b.beside)}`,
        num(a.beside) && num(b.beside) && b.beside > 20 && a.beside < b.beside * 0.5, JSON.stringify({ a: a.beside, b: b.beside }));
  check(`the building 60 m behind it goes to the sky: L* ${f(a.behind)} staged against ${f(b.behind)}`,
        num(a.behind) && num(b.behind) && b.behind > 20 && a.behind < b.behind * 0.6, JSON.stringify({ a: a.behind, b: b.behind }));
  const cb = (sg.result.cab || {}).staged || {};
  check(`a camera standing in a cab never stages on the cab: it took ${JSON.stringify(cb.subject)}`,
        cb.subject === 'subject', JSON.stringify(cb));
  check(`a world without a stage is never staged: goldenHour reads ${JSON.stringify(g.staged)}`,
        g.staged === null && g.ok, JSON.stringify(g));
}

await browser.close();
console.log(failures ? `\ntxworld: ${failures} FAILED` : '\ntxworld: all passed');
process.exit(failures ? 1 : 0);
