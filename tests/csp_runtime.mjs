/**
 * csp_runtime.mjs — what the BROWSER refuses, not what a regex can find.
 *
 * WHY THIS EXISTS, WRITTEN BY THE FAULT THAT CAUSED IT
 *
 * `scripts/site/csp.py` audits the policy statically. It reads `<script src>`, `<img src>`,
 * `<iframe src>` and `<form action>`, which are resource ATTRIBUTES, and it passed on a site it
 * had broken. Twice over, on the same day:
 *
 *   The ask box posts to a Worker named in a `data-endpoint` attribute and reached from a JS
 *   string. Neither is a resource attribute, so the static audit could not see the target, the
 *   allowlist never carried that origin, and every submitted question was refused in production
 *   while the checker reported clean.
 *
 *   Two pages merged carrying a policy older than their own scripts. Those scripts were blocked
 *   outright. The page still rendered, so nothing looked wrong from the outside.
 *
 * The shared cause is that a static reader sees what it knows how to parse, and a reader's
 * browser enforces the whole policy against everything the page actually does. So this asks the
 * browser. It loads each page in Chromium and records every `securitypolicyviolation` the page
 * fires, which is the same event the browser dispatches when it refuses a script, a style, a
 * font, an image, a frame or a fetch, including ones no parser here knows to look for.
 *
 * WHAT IT CANNOT DO, SO NOBODY READS IT AS MORE THAN IT IS. A `connect-src` violation fires when
 * the fetch HAPPENS, and the ask box fetches on submit rather than on load. A passive page load
 * therefore proves the load-time directives and says nothing about `connect-src`. That half is
 * checked separately, by comparing every endpoint the page DECLARES against the policy it
 * carries, which is done here rather than in the browser because triggering a real submit would
 * put traffic on somebody's Worker every time this runs.
 *
 *     SITE=docs node tests/csp_runtime.mjs
 *
 * Exit 0 clean, 1 a violation, 2 could not run.
 */
import pw from '/opt/node22/lib/node_modules/playwright/index.js'; const { chromium } = pw;
import { readFileSync, existsSync, readdirSync, statSync } from 'node:fs';
import { resolve, join } from 'node:path';

const SITE = process.env.SITE || 'docs';
if (!existsSync(resolve(SITE, 'index.html'))) {
  console.error(`csp_runtime: no site at ${SITE}. Build it first.`);
  process.exit(2);
}

/** Every built page, so a fault on a page nobody thought to sample still lands. */
function pages(dir, out = []) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) pages(p, out);
    else if (name.endsWith('.html')) out.push(p);
  }
  return out;
}

/** The origins a page says it will talk to, from the two places they actually live. */
function declaredEndpoints(html) {
  const out = new Set();
  const pat = /data-endpoint="(https:\/\/[^"]+)"|fetch\(\s*['"](https:\/\/[^'"]+)/g;
  let m;
  while ((m = pat.exec(html))) {
    const url = m[1] || m[2];
    try { out.add(new URL(url).origin); } catch { /* not a url, not our problem */ }
  }
  return [...out];
}

const all = pages(resolve(SITE)).sort();
// SAMPLED FOR THE BROWSER PASS, EXHAUSTIVE FOR THE STATIC ONE. Launching a page in Chromium
// costs about a second and this site has hundreds; the pages that differ STRUCTURALLY are the
// ones with their own shell or their own scripts, and every other page is the same chrome with
// different words in it. The endpoint check below runs over all of them, because it is cheap.
const structural = ['index.html', 'record/index.html', 'scan/index.html',
                    // The watch page belongs on this list more than any other: it is the only
                    // page on the site whose whole job is to fetch, repeatedly, so it is the
                    // one a connect-src mistake silently kills. It was added with the page.
                    'scan/watch/index.html', 'videos/index.html',
                    'articles/index.html', 'grid/index.html', 'topic/index.html',
                    'place/index.html', 'questions/index.html', '404.html'];
const sample = structural.map(r => resolve(SITE, r)).filter(existsSync);

let failures = 0;
const say = (ok, label, extra = '') => {
  console.log(`  ${ok ? 'ok  ' : 'FAIL'}  ${label}${ok ? '' : '  ' + extra}`);
  if (!ok) failures++;
};

// ---------------------------------------------------------------- the browser pass
// Same launch every other suite in this directory uses. A bare `chromium.launch()`
// looks for the headless shell, which this image does not ship.
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const ctx = await browser.newContext();

for (const file of sample) {
  const rel = file.slice(resolve(SITE).length + 1);
  const page = await ctx.newPage();
  const violations = [];
  // The event the browser fires when it REFUSES something. This is the ground truth the static
  // audit is an approximation of.
  await page.addInitScript(() => {
    window.__csp = [];
    document.addEventListener('securitypolicyviolation', e => {
      window.__csp.push(`${e.effectiveDirective} refused ${e.blockedURI || 'inline'}`);
    });
  });
  page.on('pageerror', () => { /* a page error is not a policy violation, and is not ours */ });
  try {
    await page.goto('file://' + file, { waitUntil: 'load', timeout: 30000 });
    // Give a deferred or async block its chance to be refused.
    await page.waitForTimeout(400);
    violations.push(...await page.evaluate(() => window.__csp || []));
  } catch (e) {
    say(false, `${rel} loads`, String(e.message).split('\n')[0].slice(0, 90));
    await page.close();
    continue;
  }
  // `file://` HAS NO ORIGIN THE WAY https DOES, so a same-origin subresource reads as a refusal
  // of `self` and would report on every page. Those are an artefact of loading from disk and not
  // something a reader would ever meet, so only ABSOLUTE refusals count here.
  const real = violations.filter(v => !v.endsWith('refused ') && !/refused file:/.test(v));
  say(real.length === 0, `${rel} loads with nothing refused`, real.slice(0, 3).join('; '));
  await page.close();
}
await browser.close();

// ---------------------------------------------------------------- the endpoint pass
// Every page, because it is a string comparison and costs nothing. This is the half that catches
// the fault that shipped: an origin the page will talk to that its own policy does not carry.
let checked = 0, missing = 0;
for (const file of all) {
  const html = readFileSync(file, 'utf8');
  const m = html.match(/<meta http-equiv="Content-Security-Policy" content="([^"]*)">/);
  const eps = declaredEndpoints(html);
  if (!eps.length) continue;
  checked++;
  const rel = file.slice(resolve(SITE).length + 1);
  if (!m) { say(false, `${rel} declares an endpoint but carries no policy`); missing++; continue; }
  const connect = (m[1].match(/(?:^|; )connect-src ([^;]*)/) || [, ''])[1];
  for (const origin of eps) {
    if (!connect.includes(origin)) {
      say(false, `${rel} will fetch ${origin}`, `connect-src does not allow it, so the browser refuses it`);
      missing++;
    }
  }
}
say(missing === 0, `every declared endpoint is allowed by its own page (${checked} page(s) declare one)`);

console.log(`\ncsp_runtime: ${failures ? `${failures} FAILED` : 'all passed'}`);
process.exit(failures ? 1 : 0);
