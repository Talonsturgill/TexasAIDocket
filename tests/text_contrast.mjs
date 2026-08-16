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
import { MEASURE } from './lib/contrast.mjs';

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

/* TWO CONTEXTS, AND THE PHONE ONE IS NOT OPTIONAL.
 *
 * This walked one 1100px desktop window, and a desktop window cannot see two whole classes of
 * text on this site. A `max-width` media query can repaint any ground it likes, so a rule that
 * is fine wide and dark-on-dark narrow was never in scope. Worse, the county map's readout and
 * its reset control are built only when `'ontouchstart' in window` is true, so on a desktop
 * context they do not exist in the DOM at all. That is the phone-only furniture the last
 * fortnight of work added, over a live map, and the gate that is supposed to guarantee every
 * word on this site is legible had never once looked at it.
 *
 * `isMobile` is what makes the narrow query apply the way a phone applies it, and `hasTouch` is
 * what makes the touch-gated code build itself. Both, or the pass is theatre. */
const CONTEXTS = [
  { name: 'desktop', opts: { viewport: { width: 1100, height: 900 } } },
  { name: 'phone', opts: { viewport: { width: 390, height: 844 }, hasTouch: true,
                           isMobile: true, deviceScaleFactor: 3 } },
];


const bad = [];
let measured = 0, skippedImage = 0, skippedHidden = 0;
const perContext = {};
for (const { name, opts } of CONTEXTS) {
  const ctx = await browser.newContext(opts);
  const p = await ctx.newPage();
  let seen = 0;
  for (const f of files) {
    await p.goto('file://' + f);
    await p.waitForTimeout(30);
    const { rows, skipped } = await p.evaluate(MEASURE);
    seen += rows.length;
    skippedImage += skipped.image;
    skippedHidden += skipped.hidden;
    const rel = f.slice(resolve(SITE).length + 1);
    for (const r of rows) {
      if (r.got + 0.005 < r.need) {
        bad.push(`[${name}] ${rel} ${r.sel} ${r.got} < ${r.need}  "${r.text}"`);
      }
    }
  }
  await ctx.close();
  perContext[name] = seen;
  measured += seen;
}
await browser.close();

/* A GATE THAT MEASURED NOTHING IS NOT A PASSING GATE, AND NEITHER IS ONE WHERE A WHOLE CONTEXT
   MEASURED NOTHING. A phone pass that silently built no pages would land here as a healthy
   total, because the desktop pass alone clears any threshold written against the total. */
for (const { name } of CONTEXTS) {
  ok(`text was measured on every page in the ${name} context `
     + `(${perContext[name]} runs across ${files.length} pages)`,
     perContext[name] > files.length * 3, `only ${perContext[name]} runs found`);
}
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
