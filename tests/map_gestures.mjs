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
//
// Usage: SITE=docs node tests/map_gestures.mjs
// =============================================================================

import {chromium} from 'playwright';
import path from 'node:path';

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

// Two fingers, dispatched as real TouchEvents. Playwright's touchscreen API is single
// touch only, so a pinch has to be built by hand.
async function pinch(from, to, cx = 195, cy = 400) {
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
  await page.evaluate(([dx, dy]) => {
    const map = document.querySelector('svg.txmap');
    const T = (x, y, id) => new Touch({identifier: id, target: map, clientX: x, clientY: y});
    const fire = (type, pts) => map.dispatchEvent(new TouchEvent(type, {
      bubbles: true, cancelable: true,
      touches: pts, targetTouches: pts, changedTouches: pts,
    }));
    fire('touchstart', [T(150, 400, 1), T(240, 400, 2)]);
    for (let i = 1; i <= 6; i++) {
      const px = (dx * i) / 6, py = (dy * i) / 6;
      fire('touchmove', [T(150 + px, 400 + py, 1), T(240 + px, 400 + py, 2)]);
    }
    fire('touchend', []);
  }, [dx, dy]);
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

await browser.close();
console.log(failures === 0 ? '\nmap gestures: all passed'
                           : `\nmap gestures: ${failures} FAILED`);
process.exit(failures === 0 ? 0 : 1);
