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
  TXT.ground(R, ${surface ? `{ surface: 'caliche', size: ${size}, tile: 5 }` : `{ size: ${size} }`});
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
  return { ok: shot.ok, step, at: at - 90, top: rows[rows.length - 1], bottom: rows[0],
           chunk: T.ShaderChunk.fog_fragment.includes('txSkyFog'), far: R.camera.far };
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
  return { sky: TXT.skyInFrame(R.camera), marker: TXT.NO_SKY, roomErrors: before, roofErrors,
           orthoSky: TXT.skyInFrame(oc), orthoErrors };
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
}

const g = await run('ground_only', GROUND_ONLY);
check('a camera looking straight down shows no sky', g.result.sky === 0, JSON.stringify(g.result));
check('an orthographic camera pitched 5 degrees down shows no sky, and says so',
      g.result.orthoSky === 0 && Array.isArray(g.result.orthoErrors) &&
      g.result.orthoErrors.some((e) => e.startsWith('TXT: NO SKY IN FRAME')),
      JSON.stringify({ orthoSky: g.result.orthoSky, orthoErrors: g.result.orthoErrors }));
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
