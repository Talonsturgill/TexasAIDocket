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
// A ONE PIXEL SWEEP THROUGH THE BAND WHERE THE NAV ACTUALLY BREAKS. The coarse list
// above steps 460 to 500 in one jump and the nav takes a second row at 461 and 462, so
// the assertion that it is one row "at every width" was green and false. A checker that
// samples cannot find a fault narrower than its own step.
const NAV_SWEEP = Array.from({length: 121}, (_, i) => 440 + i);

const PREINSTALLED = process.env.PLAYWRIGHT_CHROMIUM || "/opt/pw-browsers/chromium";
const browser = await chromium.launch(
  fs.existsSync(PREINSTALLED) ? { executablePath: PREINSTALLED } : {});

// ONE PAGE PER LAYOUT, not all fifty-five. The item pages are the same shape as each other
// and so are the place pages, so sweeping every one of them multiplies the runtime by forty
// and finds nothing the representative does not. A layout that stops being represented here
// is the thing to watch for, which is why the list names shapes rather than URLs.
// NAMED PAGES MUST EXIST. The `.filter(existsSync)` below is here so a site built without
// the videos feed still runs, and it silently swallowed `counties/index.html` for weeks
// after that page was merged into the docket. A list that quietly shrinks is a coverage
// report that lies, so the drop is now printed.
const pages = [
  "index.html",             // hero, map, ask box, stat row
  "record/index.html",      // the long list
  "grid/index.html",        // chart and figures
  "water/index.html",       // the widest table on the site
  "about/index.html",       // plain prose
  "services/index.html",    // marketing layout
  "data/index.html",        // link list
].filter((f) => { const ok = fs.existsSync(path.join(SITE, f));
                 if (!ok) console.log(`  ..    NOT BUILT, skipped: ${f}`);
                 return ok; })
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

const pg = await browser.newPage({ viewport: { width: 1200, height: 900 } });
/* A 90-STEP SEARCH FOR THE WRAP WIDTH USED TO RUN HERE, and it was already dead before it was
   deleted: it stepped the viewport from 1200 to 300 loading the front page at each stop, and
   assigned the answer to a variable nothing read after the note that printed it was replaced
   by the assertion below. Its companion `starAt` had no caller at all. Both are gone. The wrap
   width is not searched for any more because the nav does not wrap at any width. */
/* THE NAV IS ONE ROW AT EVERY WIDTH, and that is now an assertion rather than a note.
   It used to wrap below 460, which put a single ABOUT alone on a second line under seven
   siblings. That does not read as a navigation, it reads as a rendering fault, and it was
   reported as one: tabs missing on a phone. Below 28.75rem the row scrolls sideways instead.
   ASSERTED TOGETHER WITH REACHABILITY, because a row that never wraps is trivially achievable
   by clipping the overflow, and that would lose four sections with no visible symptom. So the
   last link has to be scrollable INTO view, not merely present in the DOM. */
const navRow = [];
for (const w of [...new Set([1440, 1024, 768, 600, 500, 460, 440, 412, 390, 360, 320, 300,
                            ...NAV_SWEEP])].sort((a, b) => b - a)) {
  await pg.setViewportSize({ width: w, height: 900 });
  await pg.goto("file://" + path.join(SITE, "index.html"));
  const r = await pg.evaluate(async () => {
    const nav = document.querySelector("nav.main");
    const as = [...nav.querySelectorAll("a")];
    const rows = new Set(as.map((a) => Math.round(a.getBoundingClientRect().top))).size;
    nav.scrollLeft = nav.scrollWidth;
    await new Promise((r) => requestAnimationFrame(r));
    const last = as[as.length - 1].getBoundingClientRect();
    const box = nav.getBoundingClientRect();
    return { rows, n: as.length, reached: last.right <= box.right + 1 && last.left >= box.left - 1 };
  });
  if (r.rows > 1) navRow.push(`${w}px wraps to ${r.rows} rows`);
  if (!r.reached) navRow.push(`${w}px cannot scroll to the last of ${r.n} links`);
}
check("the nav is one row at every width, and every section can be reached",
      navRow.length === 0, navRow.slice(0, 4).join(" | "));

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
    // THE NAV LINKS, NOT THE NAV BOX. The bar is full width, so comparing against its
    // container calls every mark a collision. What a reader actually sees is the glow
    // behind LINK TEXT, and that is what the mark used to be deleted to avoid.
    const links = [...document.querySelectorAll("nav.main a")].filter((a) => {
      const c = a.getBoundingClientRect();
      return !(sb.right < c.left || sb.left > c.right || sb.bottom < c.top || sb.top > c.bottom);
    }).map((a) => `nav:${a.textContent.trim()}`);
    return { shown, hits: [".hero h1", ".hero .tele"].filter(hit).concat(links) };
  });
};
const wrong = [];
// THE MARK IS NEVER HIDDEN NOW, AT ANY WIDTH. It used to be deleted below 30rem because its
// glow sat in the wrapped navigation, which is a position problem answered with a position.
// The old rule here encoded the old compromise: it permitted hiding wherever a collision
// existed, so a stylesheet that hid the mark on every phone passed. Both halves are asserted
// instead: shown everywhere, and touching nothing anywhere.
for (const w of [1440, 1180, 1024, 896, 834, 768, 700, 680, 640, 600, 560, 540, 500, 480,
                 460, 440, 414, 400, 390, 375, 360, 340, 320, 300, 280]) {
  const r = await collideAt(w);
  if (!r.shown) wrong.push(`${w}px the mark is hidden`);
  if (r.hits.length) wrong.push(`${w}px overlaps ${r.hits.join(",")}`);
}
check("the mark is shown at every width and lands on nothing",
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

// AND READABLE IS NOT ENOUGH: IT HAS TO BE THERE.
//
// The check above multiplies font size by scale and asks whether the glyphs are big enough.
// It never asked whether they were inside the drawing, so the fix that stepped the type up
// for phones pushed the residual axis off the left edge and stayed green. "-2,500" rendered
// as "500", because the part that fell off was "2,". A published figure showing a different
// number from the one computed is the failure this project exists to prevent, and it shipped
// behind a passing legibility test.
// A HAIR OF CLEARANCE IS NOT CLEARANCE, and this check learned that the expensive way.
//
// It passed here and failed on the CI runner, on the same commit and the same bytes, with
// "320px cut -2,500". Neither machine was wrong. The gutter was a constant of 108 measured
// when the longest label was shorter, and the day the residual ceiling reached 2,500 the
// negative label wanted 100.4 units of the 100 the gutter left. Under half a unit of overlap
// decided by which fonts a machine happens to have, and the runner's are what a reader with a
// web font still loading is looking at.
//
// So the tolerance runs the other way now. A label has to clear the drawing by MARGIN units,
// not merely fail to be outside it, and the gutter is computed from the labels rather than
// typed. A pass this close to the edge is a failure waiting for a different machine.
const MARGIN = 2;
const cut = [];
for (const w of [280, 300, 320, 360, 375, 390, 414, 440, 480, 540, 600, 680, 768, 900, 1180]) {
  await pg.setViewportSize({ width: w, height: 900 });
  await pg.goto("file://" + path.join(SITE, "grid", "index.html"));
  const r = await pg.evaluate((margin) => {
    const svg = document.querySelector("svg.loadshape");
    if (!svg) return null;
    const vb = svg.viewBox.baseVal;
    const T = [...svg.querySelectorAll("text")].filter((t) => t.textContent.trim());
    const out = [];
    for (const t of T) {
      const b = t.getBBox();
      if (b.x < margin || b.x + b.width > vb.width - margin ||
          b.y < 0 || b.y + b.height > vb.height)
        out.push(`cut ${t.textContent} (x ${b.x.toFixed(1)} to ` +
                 `${(b.x + b.width).toFixed(1)} of ${vb.width})`);
    }
    for (let i = 0; i < T.length; i++) for (let j = i + 1; j < T.length; j++) {
      const a = T[i].getBBox(), c = T[j].getBBox();
      if (!(a.x + a.width <= c.x || c.x + c.width <= a.x ||
            a.y + a.height <= c.y || c.y + c.height <= a.y))
        out.push(`${T[i].textContent} on ${T[j].textContent}`);
    }
    return out;
  }, MARGIN);
  if (r && r.length) cut.push(`${w}px ${r[0]}`);
}
check(`every chart label clears the drawing by ${MARGIN} units and lands on no other`,
      cut.length === 0, cut.slice(0, 4).join(" | "));

// THE MAP UNDER A THUMB, ON A DEVICE THAT HAS ONE.
//
// A phone has no hover, so before this the only way to ask the map what a county was, was to
// commit to it, load its page and come back. Dragging now names each county as the thumb
// crosses it. Three things have to hold together and any two without the third is a defect:
// the readout has to fill, the drag must NOT navigate on release, and a plain tap must still
// open the county. Take away the third and the map has lost its only job on a phone; take away
// the second and looking around throws the reader onto a county page.
const touch = await browser.newContext({
  viewport: { width: 412, height: 839 }, hasTouch: true, isMobile: true, deviceScaleFactor: 2,
});
const tp = await touch.newPage();
await tp.goto("file://" + path.join(SITE, "index.html"));
await tp.waitForTimeout(400);
// `behavior:'instant'`, because the stylesheet sets `scroll-behavior:smooth` and a measurement
// taken during the glide reads the old position. That cost a debugging round.
await tp.evaluate(() => {
  const m = document.querySelector("svg.txmap");
  scrollTo({ top: m.getBoundingClientRect().top + scrollY - 110, behavior: "instant" });
});
await tp.waitForTimeout(400);
const bb = await (await tp.$("svg.txmap")).boundingBox();
const cdp = await touch.newCDPSession(tp);
const named = new Set();
const y = bb.y + bb.height * 0.5;
await cdp.send("Input.dispatchTouchEvent",
               { type: "touchStart", touchPoints: [{ x: bb.x + bb.width * 0.25, y }] });
for (let f = 0.25; f <= 0.85; f += 0.025) {
  await cdp.send("Input.dispatchTouchEvent",
                 { type: "touchMove", touchPoints: [{ x: bb.x + bb.width * f, y }] });
  await tp.waitForTimeout(30);
  const t = await tp.evaluate(() => document.getElementById("mapread").textContent.trim());
  if (t) named.add(t);
}
const urlBeforeRelease = tp.url();
await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
await tp.waitForTimeout(350);
check("a thumb dragged across the map names the counties it crosses",
      named.size >= 6, `${named.size} named`);
check("...and says what each one holds",
      [...named].some((t) => /\d+ decisions? on the record/.test(t)) &&
      [...named].some((t) => /Nothing on the record/.test(t)),
      [...named].slice(0, 2).join(" | "));
check("...and releasing the drag does not navigate", tp.url() === urlBeforeRelease, tp.url());

const lit = await tp.$("svg.txmap a.cl");
const lb = await lit.boundingBox();
await cdp.send("Input.dispatchTouchEvent",
               { type: "touchStart", touchPoints: [{ x: lb.x + lb.width / 2, y: lb.y + lb.height / 2 }] });
await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
await tp.waitForTimeout(700);
check("...while a plain tap still opens the county",
      tp.url().includes("/place/county-"), tp.url());
await touch.close();

await browser.close();

if (failures) { console.error(`\nresponsive: ${failures} FAILED`); process.exit(1); }
console.log("\nresponsive: all passed");
