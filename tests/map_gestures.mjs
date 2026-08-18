#!/usr/bin/env node
// =============================================================================
// MAP GESTURES — the county map has to move like a map on a phone.
//
// THE PROBLEM THIS IS FOR, in the owner's words: on a phone you cannot see which
// county you are tapping, because it is under your finger. A county in the
// Panhandle is a few millimetres of glass.
//
// The readout already names what is under the thumb. This is the other half:
// pinch to zoom, two fingers to move, and a way back out.
//
// WHY A BROWSER AND NOT A UNIT TEST. The whole thing is touch events, a live
// viewBox and a bounding box. There is no part of it that can be checked without
// a layout engine, and a test that mocked all three would be testing the mock.
//
// WHAT IT ASSERTS
//   the one finger picker still works and is not eaten by the gesture layer
//   a spread zooms IN and a pinch zooms OUT
//   zoom anchors on the fingers rather than the centre of the drawing
//   two fingers move the view
//   the clamps hold, so the map can neither be zoomed out past Texas nor panned off the glass
//   the reset control appears only once the view has moved, and returns it
//   the readout and the reset control are legible, which no page sweep can reach
//
// Usage: SITE=docs node tests/map_gestures.mjs
// =============================================================================

import {chromium} from 'playwright';
import path from 'node:path';
import {MEASURE} from './lib/contrast.mjs';

const SITE = process.env.SITE || 'docs';
let failures = 0;
const ok = (label, cond, detail = '') => {
  if (cond) console.log(`  ok   ${label}`);
  else { failures++; console.log(`  FAIL ${label}${detail ? `\n       ${detail}` : ''}`); }
};

const browser = await chromium.launch();
// A PHONE, declared as one. The whole feature is behind `'ontouchstart' in window`, so a
// desktop context would silently exercise nothing and report green.
const ctx = await browser.newContext({
  viewport: {width: 390, height: 844}, hasTouch: true, isMobile: true,
  deviceScaleFactor: 3,
});
const page = await ctx.newPage();
await page.goto('file://' + path.resolve(SITE, 'record/index.html'));
await page.waitForTimeout(400);

const vb = () => page.$eval('svg.txmap', (s) =>
  s.getAttribute('viewBox').split(/[ ,]+/).map(Number));

const HOME = await vb();
ok(`the map starts at its full extent, ${HOME[2].toFixed(0)} wide`, HOME[2] > 0);
ok('the touch layer is live on a phone context',
   await page.evaluate(() => 'ontouchstart' in window));

// WHERE THE FINGERS ACTUALLY LAND, and it has been wrong twice.
//
// First it was a hardcoded (195, 400), which is above the map: the drawing started around
// y=502. The handler runs anyway, because the events are dispatched straight at the element,
// so every zoom assertion in here was passing on a gesture performed off the drawing.
//
// Then it was measured once at load and reused, which is the same fault with a longer fuse.
// READ LIVE, NEVER CACHED. This measured the box once at load and reused it all the way
// down the file, which is a bug that waits for the page to get longer. `page.click` scrolls
// its target into view, so the moment the reset control sat below the fold the click moved
// the page, the cached coordinates pointed at where the map used to be, and the anchoring
// assertion compared a stale client point against a live `getScreenCTM`. It reported 840
// units of drift on a map that had not drifted at all.
//
// A layout measurement is only true at the instant it is taken. Every finger position here
// is computed at the moment it is used.
const boxNow = () => page.$eval('svg.txmap', (s) => {
  const r = s.getBoundingClientRect();
  return {left: r.left, top: r.top, w: r.width, h: r.height};
});
const AT = async (fx, fy) => {
  const b = await boxNow();
  return [b.left + b.w * fx, b.top + b.h * fy];
};
{
  const b = await boxNow();
  const [mx, my] = await AT(0.5, 0.5);
  ok(`the fingers land on the drawing, centre (${mx.toFixed(0)}, ${my.toFixed(0)})`,
     my > b.top && my < b.top + b.h && mx > b.left && mx < b.left + b.w);
}

// The SVG user-space point under a client point, asked of the browser rather than derived,
// because `preserveAspectRatio` letterboxes and a hand-rolled ratio would not know it.
const userAt = (x, y) => page.evaluate(([x, y]) => {
  const m = document.querySelector('svg.txmap');
  const p = new DOMPoint(x, y).matrixTransform(m.getScreenCTM().inverse());
  return {x: p.x, y: p.y};
}, [x, y]);

// Two fingers, dispatched as real TouchEvents. Playwright's touchscreen API is single
// touch only, so a pinch has to be built by hand.
async function pinch(from, to, cx, cy) {
  if (cx === undefined || cy === undefined) [cx, cy] = await AT(0.5, 0.5);
  await page.evaluate(([from, to, cx, cy]) => {
    const map = document.querySelector('svg.txmap');
    const T = (x, y, id) => new Touch({identifier: id, target: map, clientX: x, clientY: y});
    const fire = (type, pts) => map.dispatchEvent(new TouchEvent(type, {
      bubbles: true, cancelable: true,
      touches: pts, targetTouches: pts, changedTouches: pts,
    }));
    fire('touchstart', [T(cx - from / 2, cy, 1), T(cx + from / 2, cy, 2)]);
    for (let i = 1; i <= 6; i++) {
      const d = from + (to - from) * (i / 6);
      fire('touchmove', [T(cx - d / 2, cy, 1), T(cx + d / 2, cy, 2)]);
    }
    fire('touchend', []);
  }, [from, to, cx, cy]);
  await page.waitForTimeout(60);
}

async function twoFingerDrag(dx, dy) {
  await page.evaluate(([dx, dy, ax, ay]) => {
    const map = document.querySelector('svg.txmap');
    const T = (x, y, id) => new Touch({identifier: id, target: map, clientX: x, clientY: y});
    const fire = (type, pts) => map.dispatchEvent(new TouchEvent(type, {
      bubbles: true, cancelable: true,
      touches: pts, targetTouches: pts, changedTouches: pts,
    }));
    fire('touchstart', [T(ax - 45, ay, 1), T(ax + 45, ay, 2)]);
    for (let i = 1; i <= 6; i++) {
      const px = (dx * i) / 6, py = (dy * i) / 6;
      fire('touchmove', [T(ax - 45 + px, ay + py, 1), T(ax + 45 + px, ay + py, 2)]);
    }
    fire('touchend', []);
  }, [dx, dy, ...(await AT(0.5, 0.5))]);
  await page.waitForTimeout(60);
}

// ---- ZOOM IN
await pinch(60, 260);
const zoomed = await vb();
ok(`a spread zooms in, ${HOME[2].toFixed(0)} to ${zoomed[2].toFixed(0)} wide`,
   zoomed[2] < HOME[2] * 0.9, `viewBox width went ${HOME[2]} -> ${zoomed[2]}`);
ok('...keeping the drawing\'s aspect ratio',
   Math.abs(zoomed[2] / zoomed[3] - HOME[2] / HOME[3]) < 0.01);

// ---- THE RESET CONTROL APPEARS ONLY ONCE THERE IS SOMETHING TO RESET
ok('the reset control is showing now the view has moved',
   await page.$eval('#mapreset', (b) => !b.hidden));

// ---- ZOOM ANCHORS ON THE FINGERS.
//
// The header has claimed this since the file was written and nothing asserted it, because
// every pinch in here was centred. A zoom anchored on the middle of the drawing and a zoom
// anchored on the fingers produce the SAME viewBox when the fingers are in the middle, so a
// centred test cannot tell a working implementation from a broken one. That is the whole
// point of the feature: on a phone you are pinching to see the county under your thumb, and
// a centre-anchored zoom throws it off the glass.
//
// So: pinch well off centre, and check the map point that was under the fingers is still
// under them. Loosely passing that is not enough either, so it is also compared against what
// a centre-anchored zoom would have produced. The observed answer has to be nearer the
// finger than the centre by a wide margin, or the assertion is measuring nothing.
await page.click('#mapreset');
await page.waitForTimeout(80);
{
  const [ax, ay] = await AT(0.22, 0.27);
  const before = await userAt(ax, ay);
  const home = await vb();
  await pinch(70, 250, ax, ay);
  const after = await userAt(ax, ay);
  const now = await vb();

  const drift = Math.hypot(after.x - before.x, after.y - before.y);
  // What a centre-anchored zoom of the same magnitude would have left under the same finger.
  const k = home[2] / now[2];
  const centred = {
    x: home[0] + home[2] / 2 + (before.x - (home[0] + home[2] / 2)) / k,
    y: home[1] + home[3] / 2 + (before.y - (home[1] + home[3] / 2)) / k,
  };
  const centredDrift = Math.hypot(centred.x - before.x, centred.y - before.y);

  ok(`the point under the fingers stays under them, ${drift.toFixed(1)} user units of drift`,
     drift < 6, `map point ${before.x.toFixed(1)},${before.y.toFixed(1)} moved to `
                + `${after.x.toFixed(1)},${after.y.toFixed(1)}`);
  ok(`...and that is anchoring, not luck (a centred zoom would have moved it `
     + `${centredDrift.toFixed(0)})`,
     centredDrift > 20 && drift < centredDrift / 4,
     `observed drift ${drift.toFixed(1)} vs centred ${centredDrift.toFixed(1)}: the two are `
     + `too close to tell apart, so this pinch is not far enough off centre to be a test`);
}
await page.click('#mapreset');
await page.waitForTimeout(80);
await pinch(60, 260);

// ---- PAN
const before = await vb();
await twoFingerDrag(-70, 0);
const panned = await vb();
ok('two fingers move the view sideways', Math.abs(panned[0] - before[0]) > 1,
   `x went ${before[0]} -> ${panned[0]}`);
ok('...without changing the zoom', Math.abs(panned[2] - before[2]) < 0.5);

// ---- CLAMPS. Both of these are ways to end up looking at nothing.
await twoFingerDrag(4000, 4000);
const shoved = await vb();
ok('the map cannot be shoved off the glass',
   shoved[0] >= HOME[0] - 0.5 && shoved[1] >= HOME[1] - 0.5
   && shoved[0] + shoved[2] <= HOME[0] + HOME[2] + 0.5
   && shoved[1] + shoved[3] <= HOME[1] + HOME[3] + 0.5,
   `viewBox ${shoved.join(' ')} outside home ${HOME.join(' ')}`);

for (let i = 0; i < 4; i++) await pinch(300, 30);
const out = await vb();
ok('...and cannot be zoomed out past the whole state',
   out[2] <= HOME[2] + 0.5, `${out[2]} wider than home ${HOME[2]}`);

for (let i = 0; i < 5; i++) await pinch(30, 400);
const deep = await vb();
ok('...and cannot be zoomed in past the limit',
   deep[2] >= HOME[2] / 8 - 0.5, `${deep[2]} is past the 8x cap`);

// ---- RESET
await page.click('#mapreset');
await page.waitForTimeout(80);
const home2 = await vb();
ok('the reset control puts the whole state back',
   Math.abs(home2[2] - HOME[2]) < 0.5 && Math.abs(home2[0] - HOME[0]) < 0.5,
   `${home2.join(' ')} vs ${HOME.join(' ')}`);
ok('...and hides itself again', await page.$eval('#mapreset', (b) => b.hidden));

// ---- THE ONE FINGER PICKER STILL WORKS, which is the thing the gesture layer could break.
const box = await page.$eval('svg.txmap', (s) => {
  const r = s.getBoundingClientRect();
  return {x: r.x, y: r.y, w: r.width, h: r.height};
});
await page.touchscreen.tap(box.x + box.w / 2, box.y + box.h / 2);
await page.waitForTimeout(120);
const read = await page.$eval('#mapread', (el) => el.textContent.trim());
ok('one finger still names the county under it', /County/.test(read), `readout: "${read}"`);

// ---- AND ZOOMING IN MAKES A COUNTY BIGGER TO HIT, which is the whole point.
const smallest = await page.$$eval('svg.txmap path.c', (ps) => {
  let m = Infinity;
  for (const p of ps) { const b = p.getBoundingClientRect(); if (b.width) m = Math.min(m, b.width); }
  return m;
});
await pinch(60, 300);
const smallestZoomed = await page.$$eval('svg.txmap path.c', (ps) => {
  let m = Infinity;
  for (const p of ps) { const b = p.getBoundingClientRect(); if (b.width) m = Math.min(m, b.width); }
  return m;
});
ok(`zooming grows the smallest county, ${smallest.toFixed(1)}px to `
   + `${smallestZoomed.toFixed(1)}px`, smallestZoomed > smallest);

// ---- AND BOTH CONTROLS ARE LEGIBLE, which nothing on this site was checking.
//
// text_contrast.mjs sweeps every page for exactly this, and these two are the one pair of
// controls it structurally cannot reach. The readout is EMPTY until a finger has named a
// county, and the reset button is `hidden` until the view has moved, so a sweep of the page
// at rest finds no text in one and declines the other as hidden, truthfully, forever. They
// are only real in the state this file spends its whole length getting into.
//
// Same maths, same compositing, same floors, imported rather than retyped.
//
// GETTING BOTH REAL AT ONCE takes some care. Two fingers deliberately blank the readout,
// because a gesture is not a pick, so the pinch that summons the reset button is also what
// empties the thing beside it. The order that leaves both live is pinch, then tap. The tap
// has to land on a county that is NOT a link, or it navigates and measures the next page.
// The map is zoomed several times over by this point, so most counties have been carried off
// the glass and their centres are coordinates no finger can reach. `elementFromPoint` answers
// null out there, so the point has to be inside the drawing AND inside the window, and it has
// to be the topmost thing at that point rather than merely overlapping it.
const quiet = await page.$$eval('svg.txmap path.c', (ps) => {
  const box = document.querySelector('svg.txmap').getBoundingClientRect();
  const inside = (x, y) =>
    x > Math.max(box.left, 0) + 2 && x < Math.min(box.right, innerWidth) - 2 &&
    y > Math.max(box.top, 0) + 2 && y < Math.min(box.bottom, innerHeight) - 2;
  for (const p of ps) {
    if (p.closest('a')) continue;
    const b = p.getBoundingClientRect();
    if (b.width < 6 || b.height < 6) continue;
    const x = b.x + b.width / 2, y = b.y + b.height / 2;
    if (!inside(x, y)) continue;
    const hit = document.elementFromPoint(x, y);
    if (hit && hit.closest('path.c') === p) return {x, y};
  }
  return null;
});
ok('there is a county on the record with nothing filed against it, to tap without navigating',
   quiet !== null);
await page.touchscreen.tap(quiet.x, quiet.y);
await page.waitForTimeout(120);

const {rows, skipped} = await page.evaluate(MEASURE, ['#mapread', '#mapreset']);
ok('both phone-only map controls were found with text in them to measure',
   rows.length === 2, `measured ${rows.length} of 2, `
   + `${skipped.absent} absent or empty, ${skipped.hidden} hidden, ${skipped.image} over an image`);
for (const r of rows) {
  ok(`${r.sel} is legible on its ground, ${r.got} against a floor of ${r.need}`,
     r.got + 0.005 >= r.need, `"${r.text}"`);
}

await browser.close();
console.log(failures === 0 ? '\nmap gestures: all passed'
                           : `\nmap gestures: ${failures} FAILED`);
process.exit(failures === 0 ? 0 : 1);
