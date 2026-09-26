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
           blackOk: blackShot && blackShot.ok, blackErrors, clearCut, blackMask, solidCut, wire, redraw };
}`;

const PREINSTALLED = process.env.CHROME_PATH || process.env.PLAYWRIGHT_CHROMIUM || '/opt/pw-browsers/chromium';
const browser = await chromium.launch(Object.assign(
  { args: ['--allow-file-access-from-files', '--enable-unsafe-swiftshader', '--force-color-profile=srgb'] },
  existsSync(PREINSTALLED) ? { executablePath: PREINSTALLED } : {}));
const scratch = join(ROOT, 'out', 'txworld');
mkdirSync(scratch, { recursive: true });

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

await browser.close();
console.log(failures ? `\ntxworld: ${failures} FAILED` : '\ntxworld: all passed');
process.exit(failures ? 1 : 0);
