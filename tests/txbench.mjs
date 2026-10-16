import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../assets/js/txbench.js', import.meta.url), 'utf8');
function render(overrides = {}, deck = {light: {az: 300, el: 25}}) {
  let pixels;
  const messages = [];
  const world = {console: {error: value => messages.push(value)},
    TXDECK: {deck: () => deck}, performance: {now: () => 0}};
  vm.createContext(world);
  vm.runInContext(source, world);
  const context = {canvas: {width: 128, height: 128},
    createImageData: (w, h) => ({data: new Uint8ClampedArray(w * h * 4)}),
    save() {}, restore() {}, setTransform() {}, putImageData(image) { pixels = image.data; }};
  const options = {x: 0, y: 0, w: 64, h: 64, scale: 2,
    height: (x, y) => x > 20 && x < 43 && y > 18 && y < 46 ? 8 : 0,
    material: (x, y) => x > 20 && x < 43 && y > 18 && y < 46 ? 1 : 0,
    albedo: (x, y, m) => m ? [0.7, 0.48, 0.18] : [0.018, 0.025, 0.033],
    spec: {1: [0.5, 40]}, ...overrides};
  world.TXBENCH.relief(context, options);
  return {pixels, proof: JSON.parse(messages.at(-1).split('TXBENCH: RELIEF ')[1])};
}
const first = render();
assert.deepEqual(first.pixels, render().pixels, 'same geometry and light reproduce the same pixels');
assert.equal(first.proof.materials, 2);
assert.equal(first.proof.height_range, 8);
assert.ok(first.proof.cast_fraction > 0.01, 'raised geometry casts into the carrier');
assert.notDeepEqual(first.pixels, render({}, {light: {az: 120, el: 25}}).pixels,
  'the declared light changes the actual shaded image');
assert.throws(() => render({light: {azDeg: 120, elDeg: 25}}), /differs from the chassis/);
assert.throws(() => render({height: () => NaN}), /invalid height/);
assert.throws(() => render({material: () => 256}), /invalid height or material/);
assert.throws(() => render({w: 0}), /positive bounds/);
for (const bounds of [{x: 1000}, {y: 1000}, {x: -1}, {y: -1}, {w: 65}, {h: 65}, {x: NaN}]) {
  assert.throws(() => render(bounds), /visible canvas/, 'invisible or clipped buffers cannot claim coverage');
}
for (const scale of [0, -1, Infinity, NaN]) {
  assert.throws(() => render({scale}), /finite scale/);
}
assert.equal(render({height: () => 0}).proof.height_range, 0,
  'flat art reports zero depth instead of claiming a physical render');
assert.equal(render({height: () => 0}).proof.cast_fraction, 0,
  'a flat carrier never counts its own pixels as cast shadows');
assert.equal(render({keyMask: () => 0}).proof.cast_fraction, 0,
  'window-masked ambient light has no visible key cast');
assert.equal(render({keyColor: [0, 0, 0]}).proof.cast_fraction, 0,
  'a black key has no visible cast');
assert.equal(render({shadow: 0}).proof.cast_fraction, 0,
  'a disabled shadow contributes no visible cast');
console.log('txbench: deterministic pixels, actual cast shadows, light inheritance and invalid geometry checks passed');
