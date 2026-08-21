/**
 * glyphs.mjs — every character the site draws exists in the font it is drawn with.
 *
 * WHY THIS EXISTS
 *
 * A missing glyph is not an error. The browser substitutes, and where nothing can substitute it
 * draws the last resort box, which in Chromium is a rectangle with the character's own codepoint
 * printed inside it in hexadecimal. It renders, it lays out, it does not warn, and no gate that
 * reads markup or reads a stylesheet can see it, because both halves are correct on their own:
 * the character is a real character and the font is a real font.
 *
 * It shipped on `registry-changes` as what was meant to be a right arrow in a CSS `content`
 * string, and rendered as a box with "92" beside it. The font was innocent. The stylesheet is
 * BUILT FROM A PYTHON STRING, and `content:"\\2192"` inside one is not a CSS escape, it is
 * Python's OCTAL escape: `\\21` is chr(17) and `92` is left as text. So the page shipped a
 * CONTROL CHARACTER in its copy.
 *
 * That is the worst hiding place available. The character appears in no source file's copy and in
 * no built page's markup. It exists only in the stylesheet, only at paint time, and only after
 * two escape languages have each had a turn at the same literal.
 *
 * So this checks two things, and the first one needs no font at all. NO CONTROL CHARACTER
 * REACHES PUBLISHED COPY, ever, whatever font it would be drawn in. And every character above
 * the ASCII range is one the face it is drawn with actually carries.
 *
 * WHY IT IS MEASURED IN A BROWSER
 *
 * The served fonts are woff2, whose tables are brotli compressed, and this repo has no
 * dependencies and is not getting one. The browser already has the decoder, and it is also the
 * only reader whose answer is the one a visitor gets.
 *
 * THE MEASUREMENT
 *
 * A character is drawn on a canvas three ways, and it is MISSING from the asked-for family if
 * either comparison says so.
 *
 *   Asked-for family versus a family that does not exist. Both fall back to the same system face
 *   when the asked-for family has no glyph, so identical pixels mean it supplied nothing.
 *
 *   Asked-for family versus a codepoint no font on earth carries, in that same family. A missing
 *   glyph can draw as the LAST RESORT BOX, and the box is drawn with the asked-for family's own
 *   metrics, so it does not match the plain fallback and the first comparison alone reads it as
 *   carried.
 *
 * The second half is here because the first half's control assertion failed on a CI runner and
 * passed on a developer machine. A container with no CJK font at all draws the box; a machine
 * with one draws the character. One measurement, two environments, opposite answers, and the
 * wrong one was the reassuring one. The instrument checks itself before every run for exactly
 * that reason, on a letter that must be carried and a character that must not be.
 *
 *   SITE=docs node tests/glyphs.mjs
 */
import { chromium } from 'playwright';
import { readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
import { pathToFileURL } from 'node:url';

const SITE = process.env.SITE || 'docs';
let failures = 0;
const ok = (name, cond, extra = '') => {
  if (!cond) failures++;
  console.log(`  ${cond ? 'ok  ' : 'FAIL'}  ${name}${cond ? '' : '  ' + extra}`);
};

function pages(dir, out = []) {
  for (const e of readdirSync(dir)) {
    const p = join(dir, e);
    if (statSync(p).isDirectory()) pages(p, out);
    else if (e.endsWith('.html')) out.push(p);
  }
  return out;
}

// The page under the pointer is irrelevant here, so one representative page per shape is enough
// to load the fonts. What matters is the CHARACTER SET, gathered from every page.
const all = pages(SITE).sort();

const browser = await chromium.launch();
const page = await browser.newPage();

// Every character the site draws, with the family it is drawn in. Collected from real computed
// styles rather than from the source, so a character inserted by CSS is collected too.
const wanted = new Map();       // family -> Set(char)
const control = [];             // every control character that reached published copy
for (const file of all) {
  await page.goto(pathToFileURL(join(process.cwd(), file)).href);
  await page.evaluate(() => document.fonts.ready);
  const found = await page.evaluate(() => {
    const out = [];
    const push = (fam, text) => {
      if (!text) return;
      out.push([fam, text]);
    };
    const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let n = walk.nextNode(); n; n = walk.nextNode()) {
      const el = n.parentElement;
      if (!el || el.closest('svg,script,style')) continue;
      push(getComputedStyle(el).fontFamily, n.nodeValue);
    }
    for (const el of document.querySelectorAll('*')) {
      if (el.closest('svg,script,style')) continue;
      for (const which of ['::before', '::after']) {
        const cs = getComputedStyle(el, which);
        const c = cs.content;
        if (!c || c === 'none' || c === 'normal') continue;
        const m = /^"(.*)"$/s.exec(c);
        if (m) push(cs.fontFamily, m[1]);
      }
    }
    return out;
  });
  for (const [fam, text] of found) {
    const first = fam.split(',')[0].trim().replace(/^["']|["']$/g, '');
    if (!wanted.has(first)) wanted.set(first, new Set());
    const set = wanted.get(first);
    for (const ch of text) {
      const cp = ch.codePointAt(0);
      // A control character is collected too, and it is judged by its own rule below. The first
      // version of this collected only above the ASCII range, which is exactly the window the
      // defect it was written for slipped through.
      if (cp > 0x7e) set.add(ch);
      else if (cp < 0x20 && ch !== '\n' && ch !== '\t') control.push([file, first, cp]);
    }
  }
}

// The instrument, and its own proof. `drawn` reports whether the named family supplied the glyph.
await page.goto(pathToFileURL(join(process.cwd(), all[0])).href);
await page.evaluate(() => document.fonts.ready);
// A codepoint in the last private use plane. Nothing carries it, so whatever a family draws for
// it IS that family's last resort box.
const NOTDEF = '\u{10FFFD}';
const drawn = (family, ch) => page.evaluate(([family, ch, notdef]) => {
  const shot = (fam, text) => {
    const c = document.createElement('canvas');
    c.width = 96; c.height = 96;
    const x = c.getContext('2d');
    x.font = `64px ${fam}`;
    x.fillStyle = '#000';
    x.fillText(text, 8, 72);
    return c.toDataURL();
  };
  const asked = `"${family}", "__no_such_family__"`;
  const mine = shot(asked, ch);
  if (mine === shot('"__no_such_family__"', ch)) return false;   // the fallback drew it, not us
  if (mine === shot(asked, notdef)) return false;                // our own last resort box
  return true;
}, [family, ch, NOTDEF]);

console.log('=== no control character reached the copy ===');
ok('published copy carries no control character', control.length === 0,
   control.map(([f, fam, cp]) => `${relative(SITE, f)} draws U+${cp.toString(16).padStart(4, '0').toUpperCase()} in ${fam}`).join('; '));

console.log('\n=== the instrument answers before it is trusted ===');
const fams = [...wanted.keys()];
ok('the site declares at least one family', fams.length > 0, JSON.stringify(fams));
ok('a letter the mono face carries is seen as carried',
   await drawn('JetBrains Mono', 'M'));
// A character no text face on this site carries. If this ever reads as carried the measurement
// has stopped measuring and every pass below is meaningless.
ok('a character no text face carries is seen as missing',
   !(await drawn('JetBrains Mono', '\u4e2d')));
// And one the mono face DOES carry, which the arrow turned out to be all along. An instrument
// that called it missing would have sent the next session looking at the font subset again.
ok('a symbol the mono face carries is seen as carried', await drawn('JetBrains Mono', '\u2192'));

// ONLY THE FACES THIS SITE SHIPS. A `<button>` on the videos page inherits the browser's own
// control font, which computes to Arial, and Arial carries the two triangles it draws on every
// machine a reader will use. Headless Chromium in a container has no Arial, so judging it here
// would fail a page that is correct everywhere it is actually read, and a gate that reports a
// correct product as a violation is how a gate gets switched off.
//
// The question this gate exists to answer is narrower and answerable: do the faces in
// `assets/fonts/web/` carry the characters this site draws in them. A family the project does
// not ship is not this gate's business.
const loaded = new Set(await page.evaluate(() => [...document.fonts].map((f) => f.family)));

console.log('\n=== every character the site draws, in the face it is drawn with ===');
let checked = 0;
let skipped = [];
for (const family of fams.sort()) {
  if (!loaded.has(family)) { skipped.push(family); continue; }
  const missing = [];
  for (const ch of [...wanted.get(family)].sort()) {
    checked++;
    if (!(await drawn(family, ch))) missing.push(`U+${ch.codePointAt(0).toString(16).toUpperCase()} ${ch}`);
  }
  ok(`${family} carries every character asked of it`, missing.length === 0, missing.join(', '));
}
ok('something above the ASCII range was actually examined', checked > 0, String(checked));
// A silent skip is how a gate stops covering what everyone believes it covers.
console.log(`  (${checked} character and face pair(s) across ${all.length} page(s))`);
if (skipped.length) {
  console.log(`  (not judged, because this project does not ship them: ${skipped.sort().join(', ')})`);
}

await browser.close();
if (failures) {
  console.error(`\nglyphs: ${failures} FAILED`);
  process.exit(1);
}
console.log('\nglyphs: all passed');
