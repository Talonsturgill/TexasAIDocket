/* page_ground.mjs — is the page actually the colour it says it is?
 *
 * WHY THIS EXISTS
 *
 * The owner looked at the site and asked whether the background was supposed to be pink. It
 * was not. Every token was correct in isolation and every contrast pairing passed, and the
 * page still rendered as mauve, because the bug was in the COMPOSITE: warm veils screening
 * over a violet ground at 9 percent lightness. Warm light over a violet ground is the
 * definition of mauve. No check that reads tokens can see that, and no contrast gate cares,
 * because mauve at the right luminance passes contrast perfectly.
 *
 * So this measures what a reader's eye actually receives: it renders the page and samples the
 * ground where no content sits.
 *
 * NO IMAGE LIBRARY. The PNG decoder below is about sixty lines and uses Node's own zlib, for
 * the same reason scripts/site/grain.py writes a PNG by hand. A test that silently skips when
 * a dependency is missing is a test that reports green on the day it stops running.
 *
 *     SITE=docs node tests/page_ground.mjs
 */
import { chromium } from 'playwright';
import { inflateSync } from 'node:zlib';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';

/* ---------- a PNG decoder, only as far as we need one ---------- */
function decodePNG(buf) {
  if (buf.readUInt32BE(0) !== 0x89504e47) throw new Error('not a PNG');
  let pos = 8, w = 0, h = 0, depth = 0, ctype = 0;
  const idat = [];
  while (pos < buf.length) {
    const len = buf.readUInt32BE(pos);
    const kind = buf.toString('ascii', pos + 4, pos + 8);
    const body = buf.subarray(pos + 8, pos + 8 + len);
    if (kind === 'IHDR') {
      w = body.readUInt32BE(0); h = body.readUInt32BE(4);
      depth = body[8]; ctype = body[9];
    } else if (kind === 'IDAT') idat.push(body);
    else if (kind === 'IEND') break;
    pos += 12 + len;
  }
  if (depth !== 8 || (ctype !== 2 && ctype !== 6)) {
    throw new Error(`unsupported PNG: depth ${depth}, colour type ${ctype}`);
  }
  const bpp = ctype === 6 ? 4 : 3;
  const raw = inflateSync(Buffer.concat(idat));
  const stride = w * bpp;
  const out = Buffer.alloc(h * stride);
  // Undo the per-scanline filters. Five of them, and every one is needed: the encoder picks
  // per line and a viewer that skips any of them produces plausible-looking garbage.
  for (let y = 0; y < h; y++) {
    const filter = raw[y * (stride + 1)];
    const src = raw.subarray(y * (stride + 1) + 1, (y + 1) * (stride + 1));
    for (let x = 0; x < stride; x++) {
      const a = x >= bpp ? out[y * stride + x - bpp] : 0;
      const b = y > 0 ? out[(y - 1) * stride + x] : 0;
      const c = (x >= bpp && y > 0) ? out[(y - 1) * stride + x - bpp] : 0;
      let v = src[x];
      if (filter === 1) v += a;
      else if (filter === 2) v += b;
      else if (filter === 3) v += (a + b) >> 1;
      else if (filter === 4) {
        const p = a + b - c, pa = Math.abs(p - a), pb = Math.abs(p - b), pc = Math.abs(p - c);
        v += (pa <= pb && pa <= pc) ? a : (pb <= pc ? b : c);
      }
      out[y * stride + x] = v & 0xff;
    }
  }
  return { w, h, bpp, data: out };
}

const px = (im, x, y) => {
  const i = y * im.w * im.bpp + x * im.bpp;
  return [im.data[i], im.data[i + 1], im.data[i + 2]];
};

function hsl([r, g, b]) {
  r /= 255; g /= 255; b /= 255;
  const mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2;
  if (mx === mn) return [0, 0, l];
  const d = mx - mn;
  const s = l > 0.5 ? d / (2 - mx - mn) : d / (mx + mn);
  let hDeg;
  if (mx === r) hDeg = ((g - b) / d + (g < b ? 6 : 0));
  else if (mx === g) hDeg = (b - r) / d + 2;
  else hDeg = (r - g) / d + 4;
  return [hDeg * 60, s, l];
}

/* ---------- the standard the ground is held to ---------- */
//
// A NIGHT PAGE IS NEARLY BLACK. The site argues its own star field is earned because Big Bend
// is a certified Dark Sky Park, and a ground at 9 percent lightness contradicts that in the
// most visible way available. The sibling product measured against sits at 3 percent. These
// are the bands the corrected ladder actually renders at, with room to move and not much.
const MAX_LIGHT = 0.075;      // above this a hue becomes plainly visible in a dark field
const MAX_SAT = 0.55;         // a trace of violet is the register. A colour is not.
// The hue arc to stay out of at any real saturation. This is the mauve the page shipped as.
const BANNED_HUE = [300, 350];
const MAX_BANNED_SAT = 0.22;

const SITE = process.env.SITE || 'docs';
const page_url = 'file://' + resolve(SITE, 'index.html');
if (!existsSync(resolve(SITE, 'index.html'))) {
  console.error(`page_ground: no site at ${SITE}. Build it first.`);
  process.exit(2);
}

let failures = 0;
const ok = (label, cond, extra = '') => {
  console.log(`  ${cond ? 'ok  ' : 'FAIL'}  ${label}${cond ? '' : '  ' + extra}`);
  if (!cond) failures++;
};

const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || undefined,
});
const ctx = await browser.newContext({
  colorScheme: 'dark', viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1,
});
const p = await ctx.newPage();
await p.goto(page_url);
await p.waitForTimeout(1200);

// Sample where no content sits: the outer gutters and the strip above the fold's copy. Points
// are chosen from the layout, not at random, so a failure names a place on the page.
const spots = {
  'top left gutter': [8, 120],
  'top right gutter': [1430, 120],
  'right of the headline': [1380, 640],
  'left gutter, mid hero': [8, 640],
};

for (const [where, [x, y]] of Object.entries(spots)) {
  const im = decodePNG(await p.screenshot());
  const rgb = px(im, x, y);
  const [h, s, l] = hsl(rgb);
  const hex = '#' + rgb.map(v => v.toString(16).padStart(2, '0')).join('').toUpperCase();
  const inBanned = h >= BANNED_HUE[0] && h <= BANNED_HUE[1];
  ok(`${where} is night, not a colour`,
     l <= MAX_LIGHT && s <= MAX_SAT,
     `${hex} light ${(l * 100).toFixed(0)}% sat ${(s * 100).toFixed(0)}%`);
  ok(`...and ${where} is not pink`,
     !(inBanned && s > MAX_BANNED_SAT),
     `${hex} hue ${h.toFixed(0)} sat ${(s * 100).toFixed(0)}%`);
}

// THE WARMTH STILL HAS TO BE THERE. A page that passes the checks above by having no
// atmosphere at all has failed differently: the whole point is a dusk sky, not a black
// rectangle. So the bottom of the sky must be measurably warmer than the top.
const im = decodePNG(await p.screenshot({ fullPage: false }));
const top = px(im, 720, 60), low = px(im, 720, 880);
const warmth = c => c[0] - c[2];             // red minus blue, so positive is warm
ok('the horizon is warmer than the sky above it',
   warmth(low) > warmth(top),
   `top r-b ${warmth(top)}, horizon r-b ${warmth(low)}`);

await browser.close();

if (failures) {
  console.error(`\npage_ground: ${failures} FAILED`);
  process.exit(1);
}
console.log('\npage_ground: all passed (the page renders as night, and the horizon is warm)');
