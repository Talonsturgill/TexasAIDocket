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
  // and the open camera again, now under a roof the frame built: a cab, a canopy. Inside, not a void.
  const Rr = TXT.setup(cv, { w: 540, h: 675, fog: [W.haze, W.fogDensity], exposure: W.exposure, tone: W.tone, fov: 40 });
  TXT.frame(Rr, { from: [0, 1.6, 0], look: [0, 0, -0.01] });
  TXT.sky(Rr, W);
  TXT.rig(Rr, { key: Object.assign({}, W.rig.key, { pos: [4, 8, 4] }), ambient: W.rig.ambient });
  TXT.ground(Rr, { surface: 'caliche', size: 900, tile: 5 });
  const roof = new T.Mesh(new T.BoxGeometry(3, 0.1, 3), new T.MeshStandardMaterial({ color: 0x333333 }));
  roof.position.set(0, 2.4, 0); Rr.scene.add(roof);
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
  // a roof whose parent group is hidden: the renderer draws neither, so it is no roof (Codex, PR 369)
  const Rh = world(40);
  TXT.frame(Rh, { from: [0, 1.6, 0], look: [0, 0, -0.01] });
  dress(Rh, [4, 8, 4]);
  const shed = new T.Group(); shed.visible = false;
  const lid = new T.Mesh(new T.BoxGeometry(3, 0.1, 3), new T.MeshStandardMaterial({ color: 0x333333 }));
  lid.position.set(0, 2.4, 0); shed.add(lid); Rh.scene.add(shed);
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
  // a roof at zero opacity: a ray still meets it and the pixels show nothing, so it is no roof
  const Rg = world(40);
  TXT.frame(Rg, { from: [0, 1.6, 0], look: [0, 0, -0.01] }); dress(Rg, [4, 8, 4]);
  const glass = new T.Mesh(new T.BoxGeometry(3, 0.1, 3), new T.MeshStandardMaterial({ transparent: true, opacity: 0 }));
  glass.position.set(0, 2.4, 0); Rg.scene.add(glass);
  const glassErrors = await capture(() => TXT.snapshot(Rg));
  // an option that once skipped the check is ignored: the kept snapshot is always judged
  const Rs = world(40);
  TXT.frame(Rs, { from: [0, 30, 0], look: [0, 0, -0.01] }); dress(Rs, [20, 40, 20]);
  const optErrors = await capture(() => TXT.snapshot(Rs, { skyCheck: false }));
  // THE CAMERA'S LAYERS (Codex, PR 369). The renderer draws only what shares a layer with the
  // camera, and a ray, a room or a dome it doesn't draw answers nothing. First the whole world on
  // layer 1 and a roof on layer 0, which the camera never shows: looking down, that is a top-down
  // frame. Then the same roof moved onto layer 1, where it is a roof, and the kept frame withdraws.
  const Rl = world(40);
  TXT.frame(Rl, { from: [0, 1.6, 0], look: [0, 0, -0.01] }); dress(Rl, [4, 8, 4]);
  Rl.scene.traverse((o) => o.layers.set(1)); Rl.camera.layers.set(1);
  const lid1 = new T.Mesh(new T.BoxGeometry(3, 0.1, 3), new T.MeshStandardMaterial({ color: 0x333333 }));
  lid1.position.set(0, 2.4, 0); Rl.scene.add(lid1);
  const layerErrors = await capture(async () => { await TXT.snapshot(Rl); lid1.layers.set(1); await TXT.snapshot(Rl); });
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
  return { sky: TXT.skyInFrame(R.camera), marker: TXT.NO_SKY, roomErrors: before, roofErrors,
           crossErrors, domeErrors, glassErrors, optErrors, layerErrors, veilErrors, wallErrors,
           orthoSky: TXT.skyInFrame(oc), orthoErrors, zoomSky: TXT.skyInFrame(Rz.camera), zoomErrors,
           outsideErrors, rollSky: TXT.skyInFrame(Rt.camera), rollErrors, hiddenErrors, previewErrors,
           shown: TXT.SKY_SHOWN };
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
  await page.waitForFunction(() => window.__result != null, null, { timeout: 120000 });
  const result = await page.evaluate(() => window.__result);
  await page.close();
  return { result, consoleErrors, pageErrors };
}

console.log(`txworld: the engine at ${ENGINE}`);
for (const [size, surface] of [[900, true], [12000, false]]) {
  const h = await run(`horizon_${size}`, HORIZON(size, surface));
  check(`${size} m ground: the world renders with no page error and no shader error`,
        !h.result.error && h.pageErrors.length === 0 && h.consoleErrors.length === 0,
        JSON.stringify({ error: h.result.error, page: h.pageErrors, console: h.consoleErrors.slice(0, 3) }));
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
check('a roof under a hidden parent is no roof: looking down beneath it IS flagged',
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
check('a roof at zero opacity is no roof: looking down beneath it IS flagged',
      Array.isArray(g.result.glassErrors) && g.result.glassErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify(g.result.glassErrors));
check('there is no option to skip the check: skyCheck false on the kept snapshot is still judged',
      Array.isArray(g.result.optErrors) && g.result.optErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify(g.result.optErrors));
{
  const le = Array.isArray(g.result.layerErrors) ? g.result.layerErrors : [];
  check('a roof on a layer the camera doesn\'t render is no roof, and the same roof on its layer is',
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
check('a camera under a roof the frame built looks down from inside, and is NOT flagged',
      Array.isArray(g.result.roofErrors) && !g.result.roofErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify(g.result.roofErrors));
check('...and the engine says so on the console, in the words print_ban reads',
      g.consoleErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')) && g.result.marker === 'TXT: NO SKY IN FRAME',
      JSON.stringify(g.consoleErrors));

await browser.close();
console.log(failures ? `\ntxworld: ${failures} FAILED` : '\ntxworld: all passed');
process.exit(failures ? 1 : 0);
