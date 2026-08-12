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
import { existsSync, readdirSync } from 'node:fs';
import { join, resolve } from 'node:path';

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
// are chosen from the layout, not at random, so a failure names a place on the page. Declared
// here because both the register comparison below and the ground checks after it use them.
const spots = {
  'top left gutter': [8, 120],
  'top right gutter': [1430, 120],
  'right of the headline': [1380, 640],
  'left gutter, mid hero': [8, 640],
};

/* ---------- A READER ON A LIGHT MACHINE MUST GET THE SAME PAGE ---------- */
//
// THE GAP THAT LET THE PINK SHIP TWICE. Every check in this file opened the page with
// `colorScheme: 'dark'`, so a whole second register was never once looked at by anything. The
// owner opened the live site on a light machine and asked why the background was pink. It was:
// the dusk atmosphere rendered over cream paper with `mix-blend-mode: multiply`, and multiply
// takes the darker of the two, so the only thing a red veil can do to cream is stain it. Measured
// at #F0E4D7, twelve points of red over green, spread across a soft field the width of the page.
//
// This is the same fault as a branch that only renders at two records: a mode nothing ever opens
// is a mode nothing ever checks. So before anything else, the light machine is asked what it gets.
{
  const lightCtx = await browser.newContext({
    colorScheme: 'light', viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1,
  });
  const lp = await lightCtx.newPage();
  await lp.goto(page_url);
  await lp.waitForTimeout(1200);
  // CONTENT COMES OFF, because the thing under test is the GROUND. The accent is Capitol granite
  // and the headline wears it on purpose, so an unhidden scan finds #DD8B60 at 82 points of red
  // over green and reports the design as a fault. Leaving it in would mean choosing a ceiling
  // loose enough to ignore the type, which is a ceiling loose enough to ignore a stain.
  await lp.addStyleTag({ content: 'body > header, body > main, body > footer { visibility: hidden }' +
                                  ' body::before { display: none }' });
  await lp.waitForTimeout(300);
  // COMPARED AGAINST THE DARK RENDER, not held to an absolute warmth ceiling. Two attempts at a
  // ceiling found the accent on the headline and then the Lone Star's halo, both of which are
  // Capitol granite and warm because they are supposed to be. There is no number that separates
  // "warm on purpose" from "stained" without knowing which is which. The question the site
  // actually has to answer is narrower and has no magic number in it: does a reader on a light
  // machine get the same page? So both are rendered and the grounds are compared.
  await p.addStyleTag({ content: 'body > header, body > main, body > footer { visibility: hidden }' +
                                 ' body::before { display: none }' });
  await p.waitForTimeout(300);
  const lightIm = decodePNG(await lp.screenshot());
  const darkIm = decodePNG(await p.screenshot());
  // A patch mean, because the film grain is +/- 26 per pixel and a single point compares noise.
  const patch = (im, cx, cy) => {
    let r = 0, g = 0, b = 0, n = 0;
    for (let y = cy - 4; y <= cy + 4; y++) for (let x = cx - 4; x <= cx + 4; x++) {
      const c = px(im, x, y); r += c[0]; g += c[1]; b += c[2]; n++;
    }
    return [r / n, g / n, b / n];
  };
  const drift = [];
  for (const [where, [x, y]] of Object.entries(spots)) {
    const a = patch(lightIm, Math.min(x, 1430), y), d = patch(darkIm, Math.min(x, 1430), y);
    const delta = Math.max(...[0, 1, 2].map(i => Math.abs(a[i] - d[i])));
    if (delta > 8) drift.push(`${where} off by ${delta.toFixed(0)}`);
  }
  ok('a reader on a light machine gets the same page', drift.length === 0, drift.join(', '));
  // The register itself, asked of the browser rather than inferred from pixels. If a future edit
  // reinstates the automatic switch, this is the line that says so in one word.
  const lightBg = await lp.evaluate(() => getComputedStyle(document.body).backgroundColor);
  const darkBg = await p.evaluate(() => getComputedStyle(document.body).backgroundColor);
  ok('...and it is the dusk register, the one the design was drawn in', lightBg === darkBg,
     `light ${lightBg}, dark ${darkBg}`);
  await lightCtx.close();
  // The dark page had its content hidden for the comparison, so it is reloaded before
  // the ground checks below, which read a page a reader would actually see.
  await p.reload();
  await p.waitForTimeout(1200);
}

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

/* ---------- and it must not have a visible edge ---------- */
//
// THE SECOND BUG THIS FILE EXISTS FOR. The corrected sky was the right colour and had a hard
// horizontal seam across it. Every warm layer is anchored to the bottom of a fixed-height box and
// reached its maximum exactly where `overflow:hidden` cut it, so at a scroll of 800 the brightest
// row of the horizon measured rgb(58,40,37) with rgb(8,6,15) directly beneath it. A 106 step drop
// over one pixel, right across the page. Nothing above catches it: the ground is night at both
// ends of the cut, no token is wrong, and the checks above sample points rather than looking for
// a discontinuity between them.
//
// The first repair moved the layers up instead of letting them run into the fade, which relocated
// the same edge rather than removing it, so this scans rather than spot-checks.
//
// CONTENT IS HIDDEN FIRST, with `visibility` so the layout and therefore the sky's height are
// untouched. Type, rules and card borders are all legitimate hard edges, and leaving them in
// would mean choosing a threshold loose enough to ignore them, which is a threshold loose enough
// to ignore a seam. With the page emptied, every edge left belongs to the weather.
//
// ROWS ARE AVERAGED ACROSS THE WIDTH before comparing. The film grain is +/- 26 per channel, so
// neighbouring pixels differ by more than a seam does; averaging a few hundred of them removes
// the noise and leaves the gradient. A real gradient moves by a fraction of a step per row.
const SEAM_STEP = 12;              // summed across channels, on the row average
// `body::before` is the 2px reading-position rail and `body::after` is the film grain. The rail is
// chrome and a deliberate hard edge, so it comes off. The grain STAYS: it is part of the surface
// and it is what makes the averaging necessary in the first place, so hiding it would be testing a
// page nobody sees.
await p.addStyleTag({ content: 'body > header, body > main, body > footer { visibility: hidden }' +
                               ' body::before { display: none }' });
await p.evaluate(() => window.scrollTo({ top: 500, behavior: 'instant' }));
await p.waitForTimeout(600);

const sky = decodePNG(await p.screenshot());
const rowAvg = y => {
  let r = 0, g = 0, b = 0, n = 0;
  for (let x = 0; x < sky.w; x += 3) { const c = px(sky, x, y); r += c[0]; g += c[1]; b += c[2]; n++; }
  return [r / n, g / n, b / n];
};
let worst = 0, worstY = 0;
let prev = rowAvg(1);
for (let y = 2; y < sky.h - 1; y++) {
  const cur = rowAvg(y);
  const step = Math.abs(cur[0] - prev[0]) + Math.abs(cur[1] - prev[1]) + Math.abs(cur[2] - prev[2]);
  if (step > worst) { worst = step; worstY = y; }
  prev = cur;
}
ok('the atmosphere has no visible edge',
   worst < SEAM_STEP,
   `largest step ${worst.toFixed(1)} at row ${worstY}, ceiling ${SEAM_STEP}`);

/* ---------- and the signals mean what the front page says they mean ---------- */
//
// THE THIRD BUG, AND THE ONE NO STATIC CHECK CAN REACH. The front page tells a reader that green
// means a door is open to them. The home page's deadline cards were green. The record page and all
// thirteen item pages painted the same open items in `--accent`, the generic link colour, so the
// site contradicted its own instruction on fourteen of twenty seven pages.
//
// Nothing caught it, and nothing was going to. Every token held its authored value, all 62
// contrast pairings passed, and the CSS was valid. The defect was WHICH token reached the element,
// which is visible only after the cascade has run. So this asks the browser for the computed
// colour of every open-state indicator on a real page and requires it to be the same colour the
// promise is made about.
const openPage = 'file://' + resolve(SITE, 'record', 'index.html');
const p2 = await ctx.newPage();
await p2.goto(openPage);
await p2.waitForTimeout(400);

const sig = await p2.evaluate(() => {
  const root = getComputedStyle(document.documentElement);
  const tok = n => root.getPropertyValue(n).trim();
  // Resolve a hex token to the rgb() string the browser reports, by asking the browser.
  const probe = document.createElement('span');
  document.body.appendChild(probe);
  const asRGB = hex => { probe.style.color = hex; return getComputedStyle(probe).color; };
  const out = { open: asRGB(tok('--sig-open')), accent: asRGB(tok('--accent')), rooms: [], clocks: [] };
  document.querySelectorAll('.rooms.open_comment, .rooms.open_meeting').forEach(el => {
    out.rooms.push({ text: getComputedStyle(el).color,
                     dot: getComputedStyle(el, '::before').backgroundColor });
  });
  document.querySelectorAll('.clock:not(.soon) .days').forEach(el => {
    out.clocks.push(getComputedStyle(el).color);
  });
  probe.remove();
  return out;
});

ok('the record page has open items to check', sig.rooms.length > 0, `${sig.rooms.length} found`);
ok('...and the open signal is not simply the link colour', sig.open !== sig.accent,
   `both ${sig.open}`);
const wrongDot = sig.rooms.filter(r => r.dot !== sig.open);
const wrongWord = sig.rooms.filter(r => r.text !== sig.open);
ok('every open room indicator is the green the front page promises',
   wrongDot.length === 0 && wrongWord.length === 0,
   `${wrongDot.length} dots and ${wrongWord.length} labels off, first dot ${sig.rooms[0]?.dot}`);
const wrongClock = sig.clocks.filter(c => c !== sig.open);
ok('...and so is every countdown that still has time on it',
   wrongClock.length === 0, `${wrongClock.length} of ${sig.clocks.length}, first ${wrongClock[0]}`);

/* ---------- and it holds on EVERY page, not the three anybody looked at ---------- */
//
// THE FOURTH BUG, AND THE ONE THAT GENERALISES. The clearance under the sticky bar was written as
// `main > h1:first-child`. Every item page wraps its title in an `<article>`, so the rule matched
// the pages that had been opened and silently missed all thirteen that had not, and their titles
// sat against the navigation. Styling by document shape fails exactly this way: somebody adds a
// wrapper and a rule stops applying with nothing to report it.
//
// So the last pass is a sweep. It opens every page the build produced and checks the two things
// that are true of all of them, at a phone width as well as a laptop, because a layout that only
// holds at one viewport is the same bug wearing different clothes.
const pages = [];
{
  const walk = (dir) => {
    for (const ent of readdirSync(dir, { withFileTypes: true })) {
      const full = join(dir, ent.name);
      if (ent.isDirectory()) walk(full);
      else if (ent.name.endsWith('.html')) pages.push(full);
    }
  };
  walk(resolve(SITE));
}
ok('the sweep found the whole site', pages.length >= 20, `${pages.length} pages`);

const MIN_CLEARANCE = 12;          // px between the sticky bar and the first heading
const tooTight = [], overflowing = [], strayMark = [];
for (const width of [1440, 390]) {
  const sweep = await browser.newContext({
    colorScheme: 'dark', viewport: { width, height: 900 }, deviceScaleFactor: 1,
  });
  const sp = await sweep.newPage();
  for (const file of pages) {
    await sp.goto('file://' + file);
    const r = await sp.evaluate(() => {
      const bar = document.querySelector('.masthead');
      const h = document.querySelector('main h1, main h2');
      const barBottom = bar ? bar.getBoundingClientRect().bottom : 0;
      const mark = document.querySelector('.sky .lonestar');
      return {
        gap: h ? Math.round(h.getBoundingClientRect().top - barBottom) : null,
        overflow: Math.round(document.documentElement.scrollWidth - document.documentElement.clientWidth),
        markShown: !!mark && getComputedStyle(mark).display !== 'none',
        isHome: document.body.classList.contains('home'),
      };
    });
    const name = file.slice(resolve(SITE).length + 1);
    if (r.gap !== null && r.gap < MIN_CLEARANCE) tooTight.push(`${name}@${width} ${r.gap}px`);
    if (r.overflow > 1) overflowing.push(`${name}@${width} +${r.overflow}px`);
    // THE MARK IS THE FRONT PAGE'S ALONE, AND ONLY WHERE THERE IS SKY TO PUT IT IN. Both halves
    // of that were already written down as comments and neither was true: a 210 pixel star sat
    // over the grid chart and the record's cards on inner pages, and the rule meant to remove it
    // on a phone was a class less specific than the rule that turns it on, so it stayed in the
    // wrapped navigation on every narrow screen. Specificity beats a media query. A comment
    // stating a rule does not make the rule hold, which is the whole argument for this file.
    if (r.markShown && (!r.isHome || width <= 736)) strayMark.push(`${name}@${width}`);
  }
  await sweep.close();
}
ok(`every page clears the sticky bar (${pages.length} pages, two widths)`,
   tooTight.length === 0, `${tooTight.length} too tight: ${tooTight.slice(0, 3).join(', ')}`);
ok('...and no page scrolls sideways',
   overflowing.length === 0, `${overflowing.length}: ${overflowing.slice(0, 3).join(', ')}`);
ok('...and the mark appears on the front page only, and not on a phone',
   strayMark.length === 0, `${strayMark.length}: ${strayMark.slice(0, 4).join(', ')}`);

await browser.close();

if (failures) {
  console.error(`\npage_ground: ${failures} FAILED`);
  process.exit(1);
}
console.log(`\npage_ground: all passed (night ground, warm horizon, no seam, green means open, ` +
            `and ${pages.length} pages hold at two widths)`);
