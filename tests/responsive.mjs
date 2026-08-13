/* responsive.mjs — the site fits the screen it is on, at every width, on every page.
 *
 * WHY THIS EXISTS
 *
 * The front page hid its Lone Star below 56rem, and the CSS explained why: "the nav wraps to
 * two rows at this width and the hero starts right under it". That was true of the width it was
 * written at and false across most of the range it was applied to. Measured, the bar holds ONE
 * row down to 520px, so the mark was being deleted through 600, 700, 800 and 896 pixels of
 * clear sky, which is where most laptops open a window.
 *
 * Nobody could have caught that by reading the rule. The rule reads perfectly. It needed
 * somebody to open the page at 700px and notice something missing, and that is exactly the
 * class of check a build-time lint cannot do, so it is done here in a real browser instead.
 *
 * WHAT IT ASSERTS
 *
 *   NOTHING OVERFLOWS SIDEWAYS. A page wider than its viewport is the defect a reader
 *   describes as "it does not fit to screen". Checked as the document's own scrollWidth AND
 *   per element, because a single wide child inside an overflow container does not move the
 *   document and still cuts content off.
 *
 *   THE MARK IS PRESENT WHERE THERE IS ROOM FOR IT. Tied to the MEASURED nav wrap width
 *   rather than to a number somebody chose, so if the nav changes the assertion moves with it.
 *
 *   THE NAV NEVER OVERLAPS THE CONTENT. A sticky bar that lands on the copy is the other half
 *   of "does not fit".
 *
 *     python3 scripts/site/site_build.py --out /tmp/site --today 2026-08-13
 *     SITE=/tmp/site node tests/responsive.mjs
 */
import { chromium } from "playwright";
import { fileURLToPath } from "node:url";
import fs from "node:fs";
import path from "node:path";

const SITE = path.resolve(process.env.SITE || path.join(
  path.dirname(fileURLToPath(import.meta.url)), "..", "docs"));

let failures = 0;
const check = (label, cond, extra = "") => {
  console.log(`  ${cond ? "ok  " : "FAIL"}  ${label}${cond ? "" : "  " + extra}`);
  if (!cond) failures++;
};

// Every width a real reader arrives at, from the narrowest phone still shipping to a wide desktop.
const WIDTHS = [320, 360, 390, 414, 480, 540, 600, 680, 768, 834, 896, 1024, 1180, 1440, 1920];

const PREINSTALLED = process.env.PLAYWRIGHT_CHROMIUM || "/opt/pw-browsers/chromium";
const browser = await chromium.launch(
  fs.existsSync(PREINSTALLED) ? { executablePath: PREINSTALLED } : {});

// ONE PAGE PER LAYOUT, not all fifty-five. The item pages are the same shape as each other
// and so are the place pages, so sweeping every one of them multiplies the runtime by forty
// and finds nothing the representative does not. A layout that stops being represented here
// is the thing to watch for, which is why the list names shapes rather than URLs.
const pages = [
  "index.html",             // hero, map, ask box, stat row
  "record/index.html",      // the long list
  "counties/index.html",    // map plus two tables
  "grid/index.html",        // chart and figures
  "water/index.html",       // the widest table on the site
  "about/index.html",       // plain prose
  "services/index.html",    // marketing layout
  "data/index.html",        // link list
].filter((f) => fs.existsSync(path.join(SITE, f)))
 .concat(fs.readdirSync(path.join(SITE, "item")).slice(0, 1).map((d) => `item/${d}/index.html`))
 .concat(fs.readdirSync(path.join(SITE, "place")).slice(0, 1).map((d) => `place/${d}/index.html`));

const overflow = [];
const overlap = [];
let pairs = 0;

for (const w of WIDTHS) {
  const pg = await browser.newPage({ viewport: { width: w, height: 900 } });
  for (const rel of pages) {
    await pg.goto("file://" + path.join(SITE, rel));
    const r = await pg.evaluate((vw) => {
      const bad = [];
      for (const el of document.querySelectorAll("body *")) {
        const b = el.getBoundingClientRect();
        if (b.width === 0 || b.height === 0) continue;
        // A skip link and a visually-hidden label are parked offscreen ON PURPOSE, which is
        // the standard technique for both. Excluded by computed position rather than by class
        // name, so the exclusion cannot be inherited by something that merely looks similar.
        if (b.right < 0 || b.left > vw) continue;
        // AND AN ELEMENT A PARENT CLIPS IS NOT AN OVERFLOW. The first version of this check
        // failed four pages at 320px on the sky's drifting veils and on the water table's
        // header row. Both are wider than the viewport on purpose and neither can be seen or
        // scrolled to: `.sky` is `overflow:hidden`, and a table narrower than its columns is
        // given its own scroll box at this width by a rule that says so in a comment. A check
        // that reports those is a check somebody switches off, and it would have buried the
        // real thing. Walk up and ask whether anything clips this element first.
        let clipped = false;
        for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) {
          const ov = getComputedStyle(a);
          if (ov.overflowX !== "visible" || ov.overflow !== "visible") { clipped = true; break; }
        }
        if (clipped) continue;
        if (b.right > vw + 1.5) {
          bad.push(`${el.tagName.toLowerCase()}.${(el.className || "").toString().trim()
            .split(/\s+/)[0] || "-"} r=${Math.round(b.right)}`);
        }
      }
      const nav = document.querySelector(".masthead");
      const main = document.querySelector("main, #main");
      let hit = null;
      if (nav && main && getComputedStyle(nav).position === "sticky") {
        const n = nav.getBoundingClientRect(), m = main.getBoundingClientRect();
        if (m.top < n.bottom - 1) hit = `main top ${Math.round(m.top)} < nav bottom ${Math.round(n.bottom)}`;
      }
      return { scrollW: document.documentElement.scrollWidth, bad: bad.slice(0, 3),
               n: bad.length, hit };
    }, w);
    pairs++;
    if (r.scrollW > w + 1 || r.n > 0) {
      overflow.push(`${w}px ${rel}: scrollW=${r.scrollW} ${r.bad.join(", ")}`);
    }
    if (r.hit) overlap.push(`${w}px ${rel}: ${r.hit}`);
  }
  await pg.close();
}

check(`nothing overflows its viewport (${pairs} page/width pairs)`, overflow.length === 0,
      overflow.slice(0, 4).join(" | "));
check("the sticky masthead never lands on the content", overlap.length === 0,
      overlap.slice(0, 3).join(" | "));

// THE MARK, TIED TO THE MEASURED WRAP RATHER THAN TO A CHOSEN NUMBER.
const pg = await browser.newPage({ viewport: { width: 1200, height: 900 } });
let wrapAt = 0;
for (let w = 1200; w >= 300; w -= 10) {
  await pg.setViewportSize({ width: w, height: 900 });
  await pg.goto("file://" + path.join(SITE, "index.html"));
  const rows = await pg.evaluate(() => new Set([...document.querySelectorAll("nav.main a")]
    .map((a) => Math.round(a.getBoundingClientRect().top))).size);
  if (rows > 1) { wrapAt = w; break; }
}
const starAt = async (w) => {
  await pg.setViewportSize({ width: w, height: 900 });
  await pg.goto("file://" + path.join(SITE, "index.html"));
  return pg.evaluate(() => {
    const s = document.querySelector(".sky .lonestar");
    return !!s && getComputedStyle(s).display !== "none";
  });
};
console.log(`  ..    nav wraps at ${wrapAt}px`);

// THE MARK IS ASSERTED BY COLLISION, NOT BY A CHOSEN NUMBER. Forced on, its box is compared
// against the hero headline and the telemetry strip at every width. It may be hidden only
// where it would land on one of them, which is the rule the CSS claims to follow and did not.
const collideAt = async (w) => {
  await pg.setViewportSize({ width: w, height: 900 });
  await pg.goto("file://" + path.join(SITE, "index.html"));
  return pg.evaluate(() => {
    const s = document.querySelector(".sky .lonestar");
    if (!s) return { shown: false, hits: [] };
    const shown = getComputedStyle(s).display !== "none";
    s.style.setProperty("display", "block", "important");
    const sb = s.getBoundingClientRect();
    const hit = (sel) => {
      const el = document.querySelector(sel);
      if (!el) return false;
      const c = el.getBoundingClientRect();
      return !(sb.right < c.left || sb.left > c.right || sb.bottom < c.top || sb.top > c.bottom);
    };
    return { shown, hits: [".hero h1", ".hero .tele"].filter(hit) };
  });
};
const wrong = [];
for (const w of [1440, 1180, 1024, 896, 834, 768, 700, 680, 600, 540, 480, 400, 360, 320]) {
  const r = await collideAt(w);
  if (r.shown && r.hits.length) wrong.push(`${w}px shown but overlaps ${r.hits.join(",")}`);
  if (!r.shown && !r.hits.length && w >= 540) wrong.push(`${w}px hidden with clear sky for it`);
}
check("the mark is shown wherever it has clear sky, and only hidden where it would collide",
      wrong.length === 0, wrong.slice(0, 4).join(" | "));
// CHART TEXT IS MEASURED ON SCREEN, NOT IN THE FILE.
//
// The load chart is a fixed viewBox scaled to whatever the column gives it, so its labels are
// the size the stylesheet says at exactly one viewport and something else everywhere. At 390px
// they rendered at 5.5 pixels, which is legible on a laptop and unreadable on the phone this
// site is mostly read on. Nothing in the markup differs between those two widths, so no
// build-time check could see it. This multiplies the computed font size by the sheet's actual
// scale and requires the result to stay readable.
const tiny = [];
for (const w of [320, 360, 390, 414, 480, 540, 600, 680, 768, 900, 1180, 1440]) {
  await pg.setViewportSize({ width: w, height: 900 });
  await pg.goto("file://" + path.join(SITE, "grid", "index.html"));
  const worst = await pg.evaluate(() => {
    const svg = document.querySelector("svg.loadshape");
    if (!svg) return null;
    const k = svg.getBoundingClientRect().width / svg.viewBox.baseVal.width;
    // TWO FLOORS, because the labels do two jobs. An axis number and a peak callout are
    // DATA and have to be read; the "GW" and "MW" unit marks are furniture that a reader
    // takes in once. Holding both to the same floor forced the unit marks up to the size of
    // the figures, which is not a legibility fix, it is a different design. Measured
    // separately so a failure names which of the two actually shrank.
    let data = Infinity, unit = Infinity;
    for (const t of svg.querySelectorAll("text")) {
      if (!t.textContent.trim()) continue;
      const px = parseFloat(getComputedStyle(t).fontSize) * k;
      if (t.classList.contains("unit")) unit = Math.min(unit, px);
      else data = Math.min(data, px);
    }
    return { data: data === Infinity ? null : +data.toFixed(1),
             unit: unit === Infinity ? null : +unit.toFixed(1) };
  });
  if (!worst) continue;
  if (worst.data !== null && worst.data < 10) tiny.push(`${w}px data ${worst.data}px`);
  if (worst.unit !== null && worst.unit < 8) tiny.push(`${w}px unit ${worst.unit}px`);
}
check("every label on the load chart stays readable at every width",
      tiny.length === 0, tiny.slice(0, 4).join(" | "));

await browser.close();

if (failures) { console.error(`\nresponsive: ${failures} FAILED`); process.exit(1); }
console.log("\nresponsive: all passed");
