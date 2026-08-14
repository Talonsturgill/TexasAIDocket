/* text_contrast.mjs — every word on the site is legible against the ground it actually lands on.
 *
 * WHY THIS EXISTS
 *
 * scripts/site/theme.py already measures contrast, and it measures the wrong thing. It pairs a
 * foreground TOKEN against a ground TOKEN, which is the right check for `--ink` on the page and
 * useless the moment a rule composites a new ground out of two tokens. The topic chip a reader
 * is standing on did exactly that: the label was `--on-accent` on `--accent-deep`, a pairing the
 * token gate measures and passes at 4.52, and the count numeral beside it sat in a well of
 * `color-mix(in srgb,#000 24%,transparent)` laid over that same ember. No token names that
 * colour, so no pairing existed for it, and it shipped at 2.93 with the suite green.
 *
 * The mistake underneath was mechanical and worth naming, because it will recur. Every other
 * chip on that row is light ink on a dark ground, where mixing black into the well RAISES
 * contrast. The current one is dark ink on a light ground, where the same mix LOWERS it. One
 * declaration, two grounds, opposite outcomes, and the only way to see it is to ask the browser
 * what colour the pixel behind the glyph ended up being.
 *
 * So this walks the built pages, and for every run of visible text composites the whole
 * ancestor background stack down to the page ground the way a browser does, then measures the
 * glyph colour against THAT. It is the reader's copy of the question, not the stylesheet's.
 *
 * WHAT IT DELIBERATELY DOES NOT DO
 *
 * It does not measure text over a background IMAGE or gradient, because there is no single
 * ground to measure against and guessing one would be worse than declining. Those are skipped
 * and COUNTED, and the count is printed on success, so a run that covered almost nothing cannot
 * read as a run that found nothing. page_ground.mjs is the check that holds those surfaces, by
 * sampling real pixels.
 *
 * Usage: SITE=/tmp/site node tests/text_contrast.mjs
 */
import { chromium } from 'playwright';
import { readdirSync, statSync, existsSync } from 'node:fs';
import { resolve, join } from 'node:path';

const SITE = process.env.SITE || 'docs';

/* WCAG 1.4.3. Large text is 24px, or 18.66px at 700 or heavier, and gets 3.0 instead of 4.5. */
const AA_BODY = 4.5;
const AA_LARGE = 3.0;

let failures = 0;
const ok = (label, cond, extra = '') => {
  console.log(`  ${cond ? 'ok  ' : 'FAIL'}  ${label}${cond || !extra ? '' : `\n        ${extra}`}`);
  if (!cond) failures++;
};

function pages(dir, out = []) {
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    if (statSync(full).isDirectory()) pages(full, out);
    else if (name.endsWith('.html')) out.push(full);
  }
  return out;
}

if (!existsSync(SITE)) {
  console.error(`text_contrast: no site at ${SITE}. Build one first.`);
  process.exit(2);
}
const files = pages(resolve(SITE)).sort();
/* A SUITE THAT FINDS NO PAGES MUST NOT PASS. This is the shape of failure that has shipped here
   before: a sweep pointed at the wrong directory reports zero problems, truthfully. */
if (files.length < 10) {
  console.error(`text_contrast: found only ${files.length} page(s) under ${SITE}. Refusing to pass.`);
  process.exit(2);
}

const PREINSTALLED = process.env.CHROME_PATH || process.env.PLAYWRIGHT_CHROMIUM
  || '/opt/pw-browsers/chromium';
const browser = await chromium.launch(
  existsSync(PREINSTALLED) ? { executablePath: PREINSTALLED } : {});
const ctx = await browser.newContext({ viewport: { width: 1100, height: 900 } });
const p = await ctx.newPage();

/* The measurement runs inside the page, because compositing needs the live computed styles of
   every ancestor and shipping that tree out one element at a time is slow enough to matter over
   fifty-odd pages. */
const MEASURE = () => {
  const relLum = ([r, g, b]) => {
    const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const ratio = (a, b) => {
    const x = relLum(a), y = relLum(b);
    const [hi, lo] = x > y ? [x, y] : [y, x];
    return (hi + 0.05) / (lo + 0.05);
  };
  /* THE BROWSER IS THE ONLY HONEST PARSER OF A CSS COLOUR, so it does the parsing.
     The first version of this scraped four numbers out of the computed string with
     /[\d.]+/g, which is correct for `rgb(180, 102, 79)` and silently wrong for
     `color(srgb 1 1 1 / 0.34)`, the form Chrome hands back for anything built with
     `color-mix()`. Those channels are 0 to 1, not 0 to 255, so a white well parsed as
     rgb(1,1,1) and the gate reported a legible numeral as 2.42 against its ground. It very
     nearly talked me into "fixing" a colour that was already right.
     Painting one pixel and reading it back cannot make that mistake, in any colour syntax
     this browser accepts, including ones that do not exist yet. `getImageData` returns
     unpremultiplied channels, so a 34 percent white comes back as 255,255,255 at 0.34. */
  const cv = document.createElement('canvas');
  cv.width = cv.height = 1;
  const cx = cv.getContext('2d', { willReadFrequently: true });
  const parse = s => {
    if (!s) return null;
    cx.clearRect(0, 0, 1, 1);
    cx.fillStyle = '#000';
    cx.fillStyle = s;           /* an unparseable value leaves the previous fill in place */
    cx.fillRect(0, 0, 1, 1);
    const d = cx.getImageData(0, 0, 1, 1).data;
    return [d[0], d[1], d[2], d[3] / 255];
  };
  const over = (fg, bg) => [0, 1, 2].map(i => fg[i] * fg[3] + bg[i] * (1 - fg[3]));

  /* THE GROUND UNDER AN ELEMENT is every ancestor background composited bottom up, starting at
     the browser's own white and ending at the nearest painted layer. Anything that paints an
     image or a gradient anywhere in that stack is not a colour and is declined, not guessed. */
  const groundOf = el => {
    const stack = [];
    for (let n = el; n; n = n.parentElement) {
      const cs = getComputedStyle(n);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') return null;
      const c = parse(cs.backgroundColor);
      if (c && c[3] > 0) stack.push(c);
      if (c && c[3] >= 0.999) break;
    }
    let ground = [255, 255, 255];
    for (const layer of stack.reverse()) ground = over(layer, ground);
    return ground;
  };

  const hidden = el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || Number(cs.opacity) === 0) return true;
    const r = el.getBoundingClientRect();
    /* The visually-hidden pattern this site uses parks a label off-canvas at -9999px. It is
       read aloud and never seen, so it has no ground and no contrast question. */
    if (r.width < 2 || r.height < 2 || r.right < -1000 || r.bottom < -1000) return true;
    return false;
  };

  const rows = [], skipped = { image: 0, hidden: 0 };
  const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  for (let t = walk.nextNode(); t; t = walk.nextNode()) {
    if (!t.nodeValue || !t.nodeValue.trim()) continue;
    const el = t.parentElement;
    if (!el || seen.has(el)) continue;
    seen.add(el);
    /* SVG text carries `fill`, not `color`, and lives on drawings this suite has no ground for.
       responsive.mjs holds the chart labels. */
    if (el.closest('svg')) continue;
    if (hidden(el)) { skipped.hidden++; continue; }
    const ground = groundOf(el);
    if (!ground) { skipped.image++; continue; }
    const cs = getComputedStyle(el);
    const fg = parse(cs.color);
    if (!fg) continue;
    const size = parseFloat(cs.fontSize);
    const weight = Number(cs.fontWeight) || 400;
    const large = size >= 24 || (size >= 18.66 && weight >= 700);
    rows.push({
      text: t.nodeValue.trim().slice(0, 42),
      sel: el.tagName.toLowerCase() + (el.className && typeof el.className === 'string'
        ? '.' + el.className.trim().split(/\s+/).join('.') : ''),
      got: Math.round(ratio(over(fg, ground), ground) * 100) / 100,
      need: large ? 3.0 : 4.5,
    });
  }
  return { rows, skipped };
};

const bad = [];
let measured = 0, skippedImage = 0, skippedHidden = 0;
for (const f of files) {
  await p.goto('file://' + f);
  await p.waitForTimeout(30);
  const { rows, skipped } = await p.evaluate(MEASURE);
  measured += rows.length;
  skippedImage += skipped.image;
  skippedHidden += skipped.hidden;
  const rel = f.slice(resolve(SITE).length + 1);
  for (const r of rows) {
    if (r.got + 0.005 < r.need) bad.push(`${rel} ${r.sel} ${r.got} < ${r.need}  "${r.text}"`);
  }
}
await browser.close();

/* A GATE THAT MEASURED NOTHING IS NOT A PASSING GATE. */
ok(`text was measured on every page (${measured} runs across ${files.length} pages)`,
   measured > files.length * 3, `only ${measured} runs found`);
ok('every run of text clears its contrast floor against the ground it lands on',
   bad.length === 0, `${bad.length} under floor:\n        ${bad.slice(0, 12).join('\n        ')}`);
/* NO SILENT CAPS. What this gate declined to measure is printed whether it passed or failed,
   because "clean" over three elements and "clean" over three thousand read identically. */
console.log(`  ..    declined ${skippedImage} run(s) over an image or gradient ground, ` +
            `and ${skippedHidden} hidden`);

if (failures) {
  console.error(`\ntext_contrast: ${failures} FAILED`);
  process.exit(1);
}
console.log(`\ntext_contrast: all passed (${measured} runs of text, each against its own ` +
            `composited ground)`);
