// docket_calendar: the record by date, driven in a real browser.
//
// Everything interesting here happens at READ TIME. Which month is showing, what the stepper
// does at the ends of the range, whether the filter hides the right things, whether a shared
// link lands on the month it names: no build-time lint can see any of it.
//
// THE FIRST CHECK IS THE ONE THAT MATTERS MOST. Every month is in the document and readable
// with no script at all, because a calendar that is only a calendar when JavaScript runs is a
// record that some readers cannot browse. The script's whole job is to show one month at a
// time, which is a convenience.
//
//     SITE=docs node tests/docket_calendar.mjs

import { chromium } from "playwright";
/* Some environments ship a chromium whose build number does not match the npm package's
   pinned one. Where a preinstalled binary exists, use it rather than downloading a second
   copy; where it does not, let playwright resolve its own. Hardcoding either breaks the
   other, and this test has to run both on a dev container and on a CI runner. */
import fs from "node:fs";
import path from "node:path";
import http from "node:http";
const PREINSTALLED = process.env.PLAYWRIGHT_CHROMIUM || "/opt/pw-browsers/chromium";
const LAUNCH = fs.existsSync(PREINSTALLED) ? { executablePath: PREINSTALLED } : {};
const SITE = path.resolve(process.env.SITE || "docs");

let fails = 0;
const ok = (label, cond, extra = "") => {
  console.log(`  ${cond ? "ok  " : "FAIL"}  ${label}${cond ? "" : "  " + extra}`);
  if (!cond) fails++;
};

// OVER HTTP, not file://. The record page links a second stylesheet and the month anchors are
// real urls; file:// resolves both differently and would test a page nobody is served.
const TYPES = { ".css": "text/css", ".png": "image/png", ".svg": "image/svg+xml",
                ".woff2": "font/woff2", ".json": "application/json", ".xml": "application/xml" };
const server = http.createServer((rq, rs) => {
  let f = path.join(SITE, decodeURIComponent(rq.url.split("?")[0]));
  if (!f.startsWith(SITE)) { rs.writeHead(403).end(); return; }
  try { if (fs.statSync(f).isDirectory()) f = path.join(f, "index.html"); fs.statSync(f); }
  catch { rs.writeHead(404).end("no"); return; }
  rs.writeHead(200, { "content-type": TYPES[path.extname(f)] || "text/html" });
  fs.createReadStream(f).pipe(rs);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const ORIGIN = `http://127.0.0.1:${server.address().port}`;
const browser = await chromium.launch(LAUNCH);

// REDUCED MOTION, AND IT IS THE FIX FOR THE FLAKE THIS SUITE HAD. The site decorates every
// page with infinite animations, one of which shimmers a full width blurred layer that is not
// compositable, so a headless renderer with no GPU repaints and re-blurs it every frame.
// Playwright's actionability loop is measured in frames, so on this page a single `page.click`
// cost 426 to 875ms, measured, against loops below that gave it 400ms and swallowed the
// failure. Half the clicks in a walk were being dropped and the end of range assertion landed
// on whatever month it ran out of iterations on. With `reduce` the same click costs 49 to
// 215ms. This is not a workaround: it is the setting a CI runner should emulate anyway, the
// site honours it in its own stylesheet, and nothing this suite asserts is about motion.
const CTX_OPTS = { viewport: { width: 1280, height: 900 }, reducedMotion: "reduce" };

// ONE CONTEXT, ONE PAGE, REUSED. The first version opened a fresh context and reloaded a
// 330KB page for every section, which was most of a suite that ran for ten minutes. A test
// slow enough to be skipped is a test that is not run, so the cost is part of the design:
// a reload happens only where a FRESH DOCUMENT is the thing under test, and a viewport
// change is a resize rather than a new browser.
const CTX = await browser.newContext(CTX_OPTS);
const PAGE = await CTX.newPage();
// A FRESH DOCUMENT EVERY TIME, WHICH IS WHAT THIS FUNCTION ALWAYS CLAIMED TO GIVE. `goto` to a
// url that differs from the current one ONLY in its fragment is a SAME DOCUMENT navigation:
// nothing reloads, `hashchange` fires, and the startup path that reads the hash never runs.
// Proved by leaving a marker on `window` and watching it survive the goto. So every deep link
// check below was exercising the listener and reporting it as the cold parse. The counter
// makes each visit a different url, so a load is a load; the server ignores the query.
let visit = 0;
const load = async (hash = "") => {
  await PAGE.goto(`${ORIGIN}/record/?v=${++visit}${hash}`, { waitUntil: "load" });
  await PAGE.waitForFunction(() => !!document.getElementById("calprev"), null, { timeout: 8000 });
  return PAGE;
};
const open = async (opts = {}, hash = "") => {
  if (opts.javaScriptEnabled === false) {
    const ctx = await browser.newContext({ ...CTX_OPTS, ...opts });
    const p = await ctx.newPage();
    await p.goto(`${ORIGIN}/record/${hash}`, { waitUntil: "load" });
    return { p, ctx };
  }
  if (opts.viewport) await PAGE.setViewportSize(opts.viewport);
  else await PAGE.setViewportSize({ width: 1280, height: 900 });
  await load(hash);
  return { p: PAGE, ctx: { close: async () => {} } };
};

// REACHING A MONTH IS A TWO STEP MOVE NOW, and doing it hopefully is how a suite goes flaky.
// The tab click was wrapped in a catch, so when the sticky masthead happened to cover the
// toolbar after a previous scroll, the click timed out silently, the year view never opened,
// and the mini calendar that was supposed to be clicked next sat invisible until the full
// thirty second default expired. Scroll first, then assert the view actually changed, then
// click. A failure now says which step failed instead of timing out on the one after it.
async function openMonth(p, key) {
  await p.evaluate(() => window.scrollTo(0, 0));
  await p.click("#calvy", { timeout: 5000 });
  await p.waitForSelector(`a.mini[data-month="${key}"]`, { state: "visible", timeout: 5000 });
  await p.click(`a.mini[data-month="${key}"]`, { timeout: 5000 });
}

// A STEP IS A MONTH THAT CHANGED, NOT A CLICK THAT WAS ATTEMPTED. Every walk here used to be
// a fixed number of `click(...{timeout: 400}).catch(() => {})` calls, which on this page is
// below the cost of one click, so the loop dropped steps and then asserted where it had ended
// up. That is how "walking all the way back lands on the first month" reported 2025-04. The
// stepper's own end condition is the button going disabled, so use that rather than counting.
// The iteration cap is a runaway guard, not the mechanism: reaching it is a failure.
async function walk(p, id, cap) {
  const shown = () => p.evaluate(() => {
    const s = document.querySelector(".calmonth:not([hidden])");
    return s ? s.getAttribute("data-month") : null;
  });
  const seen = [];
  for (let i = 0; i < cap; i++) {
    const at = await shown();
    seen.push(at);
    if (await p.$eval(`#${id}`, (b) => b.disabled)) break;
    await p.click(`#${id}`);
    await p.waitForFunction((prev) => {
      const s = document.querySelector(".calmonth:not([hidden])");
      return !!s && s.getAttribute("data-month") !== prev;
    }, at, { timeout: 5000 });
  }
  return seen;
}

// TODAY IS THE BUILD'S TODAY, NOT THE RUNNER'S. `docs/` is committed, so the day this page
// marks is the day the site was last built, and a literal month written in here rots the whole
// suite on the first of the next one. Read it off the single cell the builder marked.
const todayMonth = (p) => p.evaluate(() => {
  const d = document.querySelector("#cal .calday.today");
  return d ? d.closest(".calmonth").getAttribute("data-month") : null;
});
let TODAY = null;

const state = (p) => p.evaluate(() => {
  const c = document.getElementById("cal");
  if (!c) return null;
  const panels = [...c.querySelectorAll(".calmonth")];
  const shown = panels.filter((x) => !x.hidden);
  return {
    panels: panels.length,
    shown: shown.length,
    showing: shown.length === 1 ? shown[0].getAttribute("data-month") : null,
    view: c.getAttribute("data-view"),
    tab: (c.querySelector('.caltab[aria-pressed="true"]') || {}).id || null,
    today: c.querySelectorAll(".calday.today").length,
    events: c.querySelectorAll(".calev").length,
    badLinks: [...c.querySelectorAll(".calev")].filter((a) => !/\/item\/[^/]+\/$/.test(
      a.getAttribute("href") || "")).length,
    prevOff: document.getElementById("calprev").disabled,
    nextOff: document.getElementById("calnext").disabled,
  };
});

console.log("=== with no script at all ===");
{
  const { p, ctx } = await open({ javaScriptEnabled: false });
  const s = await p.evaluate(() => {
    const c = document.getElementById("cal");
    const panels = [...c.querySelectorAll(".calmonth")];
    return { panels: panels.length,
             readable: panels.filter((x) => x.offsetParent !== null).length,
             anchors: c.querySelectorAll('a.mini.has[href^="#cal-"]').length,
             events: c.querySelectorAll(".calev").length };
  });
  ok("every month is in the document", s.panels > 1, String(s.panels));
  ok("...and every one of them is readable, not hidden behind a script",
     s.readable === s.panels, `${s.readable} of ${s.panels}`);
  ok("the rail entries are real anchors, so they still go somewhere", s.anchors > 1);
  ok("...and every dated moment is present", s.events > 100, String(s.events));
  await ctx.close();
}

console.log("\n=== with script, one month at a time ===");
{
  const { p, ctx } = await open();
  TODAY = await todayMonth(p);
  let s = await state(p);
  ok("exactly one month is showing", s.shown === 1, String(s.shown));
  ok("...and the month tab is the one lit", s.view === "month" && s.tab === "calvm",
     `${s.view}/${s.tab}`);
  ok("today is marked, so a reader is not counting columns", s.today === 1, String(s.today));
  ok("every event links to an item page", s.badLinks === 0, String(s.badLinks));

  const first = s.showing;
  await openMonth(p, "2026-06");
  await p.waitForTimeout(300);
  s = await state(p);
  ok("clicking a month in the rail shows that month", s.showing === "2026-06", s.showing);
  ok("...and it is the only one showing", s.shown === 1, String(s.shown));
  ok("...and the address bar carries it, so the view can be shared",
     p.url().endsWith("#cal-2026-06"), p.url());
  ok("the month it opened on was today's", !!TODAY && first === TODAY, `${first} vs ${TODAY}`);
  await ctx.close();
}

console.log("\n=== the stepper, which is the control a thumb uses ===");
{
  const { p, ctx } = await open();
  await p.click("#calnext"); await p.waitForTimeout(250);
  const a = await state(p);
  await p.click("#calprev"); await p.waitForTimeout(250);
  const b = await state(p);
  ok("next moves forward a month that exists", a.showing > "2026-08", a.showing);
  ok("...and prev comes back", b.showing === "2026-08", b.showing);

  // IT STOPS RATHER THAN WRAPPING. Wrapping off the end lands a reader five years away with
  // no way back using the button they just pressed.
  await walk(p, "calprev", 60);
  const s = await state(p);
  ok("walking off the front stops at the first month, it does not wrap", s.prevOff === true);
  ok("...and the panel is still a real month", !!s.showing, String(s.showing));
  // NOT SWALLOWED. This click is the thing the next line asserts on, so a click that never
  // landed has to be a failure here rather than a confusing failure one line down.
  await p.click("#calnow");
  await p.waitForFunction((m) => {
    const x = document.querySelector(".calmonth:not([hidden])");
    return !!x && x.getAttribute("data-month") === m;
  }, TODAY, { timeout: 5000 }).catch(() => {});
  ok("'this month' comes home", (await state(p)).showing === TODAY);
  await ctx.close();
}

console.log("\n=== only what I can still act on ===");
{
  const { p, ctx } = await open();
  const before = await p.evaluate(() =>
    [...document.querySelectorAll(".calmonth:not([hidden]) .calev")]
      .filter((x) => getComputedStyle(x).display !== "none").length);
  await p.click(".calswitch"); await p.waitForTimeout(300);
  const after = await p.evaluate(() => {
    const vis = [...document.querySelectorAll(".calmonth:not([hidden]) .calev")]
      .filter((x) => getComputedStyle(x).display !== "none");
    return { n: vis.length, allAct: vis.every((x) => x.classList.contains("act")) };
  });
  ok("the filter hides something", after.n < before, `${before} -> ${after.n}`);
  ok("...and what is left is only what can be acted on", after.allAct);
  ok("...and it leaves some of them, rather than emptying the month", after.n > 0, String(after.n));
  await p.click(".calswitch"); await p.waitForTimeout(300);
  const back = await p.evaluate(() =>
    [...document.querySelectorAll(".calmonth:not([hidden]) .calev")]
      .filter((x) => getComputedStyle(x).display !== "none").length);
  ok("turning it off puts everything back", back === before, `${back} vs ${before}`);
  await ctx.close();
}

console.log("\n=== a link into one month lands there ===");
{
  const { p, ctx } = await open({}, "#cal-2025-09");
  ok("a shared month opens on that month", (await state(p)).showing === "2025-09");
  await ctx.close();
}

console.log("\n=== on a phone ===");
{
  const { p, ctx } = await open({ viewport: { width: 390, height: 844 } });
  const s = await p.evaluate(() => {
    const w = document.documentElement.clientWidth;
    const off = [...document.querySelectorAll("#cal *")]
      .filter((el) => el.getBoundingClientRect().right > w + 1).length;
    const btn = [...document.querySelectorAll("#cal .calstep button")]
      .map((b) => Math.round(Math.min(b.getBoundingClientRect().width,
                                      b.getBoundingClientRect().height)));
    const day = document.querySelector(".calmonth:not([hidden]) .calday.full");
    return { off, btn, dayStatesItsDate: !!day && getComputedStyle(
      day.querySelector(".caldd")).display !== "none",
      scrollX: document.documentElement.scrollWidth > w };
  });
  ok("nothing in the calendar hangs off the side", s.off === 0, String(s.off));
  ok("...and the page does not scroll sideways", s.scrollX === false);
  ok("every stepper button is a thumb sized target", s.btn.every((n) => n >= 44),
     JSON.stringify(s.btn));
  ok("a day states its own date, since the column header is gone", s.dayStatesItsDate);
  await ctx.close();
}

// ===========================================================================================
// EVERY PATH, NOT A SAMPLE. The checks above prove the mechanism on one or two months. These
// walk all of them, because the failures this kind of thing actually has are the eighteenth
// month, the end of the range, and the third rapid tap.
console.log("\n=== every month, by every route ===");
{
  const { p, ctx } = await open();
  const all = await p.evaluate(() =>
    [...document.querySelectorAll(".calmonth")].map((x) => x.getAttribute("data-month")));

  let railBad = [];
  for (const k of all) {
    await openMonth(p, k);
    await p.waitForFunction(
      (m) => { const s = document.querySelector(".calmonth:not([hidden])");
               return s && s.getAttribute("data-month") === m; }, k, { timeout: 2000 })
      .catch(() => railBad.push(k));
    const s = await state(p);
    if (s.shown !== 1 || s.showing !== k) railBad.push(k);
  }
  ok(`every one of the ${all.length} months opens from the rail`, !railBad.length,
     [...new Set(railBad)].join(", "));

  // MEASURED IN THE PAGE, NOT ACROSS THE WIRE. The first version of this timed
  // `playwright.click`, which scrolls the target into view before it clicks, so it was
  // reporting the harness's scroll as the page's latency and calling a 37ms switch half a
  // second. What a thumb feels is dispatch to the next paint, and that is what this takes.
  const lat = await p.evaluate(async () => {
    const ms = [];
    for (const a of [...document.querySelectorAll("a.mini.has")]) {
      const t0 = performance.now();
      a.click();
      await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
      ms.push(performance.now() - t0);
    }
    ms.sort((x, y) => x - y);
    return { median: ms[Math.floor(ms.length / 2)], worst: ms[ms.length - 1] };
  });
  // A switch is a `hidden` toggle over panels the browser already parsed, so it belongs
  // inside a couple of frames. The ceiling is loose enough for a shared CI runner and tight
  // enough that work moving somewhere it should not be would show up here.
  ok("a month switch lands within a couple of frames",
     lat.median < 120, `median ${lat.median.toFixed(1)}ms`);
  ok("...and the slowest of them is not a different order of magnitude",
     lat.worst < 400, `worst ${lat.worst.toFixed(1)}ms`);

  // A DEEP LINK NEEDS A FRESH DOCUMENT, which is the one thing here that costs a reload. Four
  // of the eighteen rather than all of them: the two ends, the month it opens on, and one in
  // between. The path is identical for every month and the rail loop above already proved
  // each one resolves; what these check is the parse of the hash on a cold page.
  const sample = [all[0], all[Math.floor(all.length / 2)], all[all.length - 1], TODAY];
  let linkBad = [];
  for (const k of [...new Set(sample)]) {
    await load(`#cal-${k}`);
    const s = await state(p);
    if (s.showing !== k || s.shown !== 1) linkBad.push(`${k}->${s.showing}`);
  }
  // AND IT ARRIVES AT THE CALENDAR, not a screenful above it. The native anchor jump cannot
  // work here, because the panel it names is still hidden when the browser tries.
  await load("#cal-2026-06");
  // THE MONTH ITSELF, not the section that contains it. The first version of this check
  // asked whether `#cal` was on screen, which it is even when the rail fills the viewport and
  // the month the link named is a screenful below the fold. A check that passes for the wrong
  // reason is worse than no check: it says the thing was verified.
  const where = await p.evaluate(() => {
    const h = document.querySelector(".calmonth:not([hidden]) .calmh");
    const r = h.getBoundingClientRect();
    return { top: Math.round(r.top), vh: window.innerHeight,
             month: h.closest(".calmonth").getAttribute("data-month") };
  });
  ok("a shared month puts THAT month on screen, not just the calendar",
     where.month === "2026-06" && where.top >= 0 && where.top < where.vh,
     JSON.stringify(where));

  // THE SAME LINK, WITH THE MOTION A READER ACTUALLY HAS, because the suite runs the whole
  // rest of its work under `reduce` and that setting is not what most people browse with.
  //
  // The check above is the one that flaked, and this is where it came from. `html` carries
  // `scroll-behavior:smooth`, which `prefers-reduced-motion` turns to `auto`, so under `reduce`
  // the deep link is on screen on the first frame and under default motion the browser spends
  // about a second animating there. Measured, arriving at 0ms, 200ms, 500ms and 1000ms: the
  // panel sits at 1517, 1517, 1164 and then 0. Nothing is wrong with the page in either mode.
  // What was wrong was reading the answer while the browser was still travelling to it.
  //
  // Turning motion off for the suite is right and it leaves a hole exactly here, since this is
  // the ONE assertion in the file whose subject is where the viewport ends up. So it is asked
  // a second time in the mode that is not otherwise covered, and given the settle it needs
  // rather than a fixed sleep, which would be the same guess that flaked in the first place.
  {
    const mctx = await browser.newContext({ viewport: { width: 1280, height: 900 },
                                            reducedMotion: "no-preference" });
    const mp = await mctx.newPage();
    await mp.goto(`${ORIGIN}/record/?v=${++visit}#cal-2026-06`, { waitUntil: "load" });
    // SETTLED MEANS IT STOPPED MOVING, which is the only honest end condition for an animation
    // whose duration the browser picks. Two equal readings a frame apart, or the timeout.
    const landed = await mp.waitForFunction(() => {
      const h = document.querySelector(".calmonth:not([hidden]) .calmh");
      if (!h) return false;
      const y = Math.round(h.getBoundingClientRect().top);
      const prev = window.__lastY;
      window.__lastY = y;
      return prev === y && y >= 0 && y < window.innerHeight ? { top: y } : false;
    }, null, { timeout: 8000, polling: 100 }).then((h) => h.jsonValue()).catch(() => null);
    ok("...and it still arrives there when the reader has motion switched on",
       !!landed, landed ? "" : "never settled on screen within 8s");
    await mctx.close();
  }

  ok(`a month can be linked to directly (${[...new Set(sample)].length} sampled of ${all.length})`,
     !linkBad.length, linkBad.join(" "));
  await ctx.close();
}

console.log("\n=== stepping the whole range, both ways ===");
{
  const { p, ctx } = await open();
  const all = await p.evaluate(() =>
    [...document.querySelectorAll(".calmonth")].map((x) => x.getAttribute("data-month")));
  await openMonth(p, all[0]);
  await p.waitForTimeout(150);
  // NO DUPLICATE FILTER ANY MORE. `walked` used to be `seen` with consecutive repeats removed,
  // which is exactly the shape that hid a dropped click: a step that never happened shows up
  // as a repeat and the filter deletes the evidence. `walk` waits for the month to change, so
  // what comes back is the months it really visited and it can be compared as it stands.
  const walked = await walk(p, "calnext", all.length + 4);
  ok("stepping forward visits every month in order, once",
     JSON.stringify(walked) === JSON.stringify(all), walked.slice(0, 4).join(","));
  const end = await state(p);
  ok("...and stops at the last one rather than running off", end.nextOff === true);
  ok("...with the panel still real", end.showing === all[all.length - 1], end.showing);
  const back = await walk(p, "calprev", all.length + 4);
  ok("...and stepping back visits every month in order too",
     JSON.stringify(back) === JSON.stringify([...all].reverse()), back.slice(0, 4).join(","));
  const home = await state(p);
  ok("walking all the way back lands on the first month", home.showing === all[0], home.showing);
  ok("...and prev is spent", home.prevOff === true);
  await ctx.close();
}

console.log("\n=== the third rapid tap ===");
{
  const { p, ctx } = await open();
  // No waiting between clicks. A handler that races itself leaves two panels visible, or
  // leaves the rail pointing at a month the panel is not showing.
  //
  // FIRED IN THE PAGE, AND COUNTED, for the same reason the latency measurement above is. Five
  // concurrent `page.click` calls share one mouse, so they interleave: a mousedown on prev
  // followed by a mouseup on next fires the click on the pair's common ancestor and the button
  // never hears it. Measured, that delivered anywhere between two and five taps with nothing
  // rejected, and while the same five clicks were given 400ms on an animated page it delivered
  // NONE of them and the two assertions below passed on a calendar nobody had touched. Five
  // synchronous calls in one task is both deterministic and a harsher race than a thumb can
  // produce: the handlers run back to back with no frame in between.
  const taps = await p.evaluate(() => {
    let n = 0;
    ["calprev", "calnext"].forEach((id) => document.getElementById(id)
      .addEventListener("click", () => { n++; }));
    const next = document.getElementById("calnext"), prev = document.getElementById("calprev");
    [next, next, next, prev, next].forEach((b) => b.click());
    return n;
  });
  await p.waitForTimeout(400);
  ok("all five taps actually reached the stepper", taps === 5, String(taps));
  const s = await state(p);
  ok("five taps with no pause leave exactly one month showing", s.shown === 1, String(s.shown));
  ok("...and the month view is the one showing", s.view === "month", String(s.view));

  // The filter, toggled hard, in a month that has both kinds.
  await p.evaluate(() => {
    window.__flips = 0;
    document.getElementById("calacts")
      .addEventListener("click", () => { window.__flips++; });
  });
  for (let i = 0; i < 8; i++) await p.click(".calswitch");
  await p.waitForTimeout(300);
  const flips = await p.evaluate(() => window.__flips);
  ok("...and all eight flips of the filter reached it", flips === 8, String(flips));
  const on = await p.evaluate(() => document.getElementById("calacts").checked);
  const cls = await p.evaluate(() => document.getElementById("cal").classList.contains("acts"));
  ok("the filter and its box never disagree, however fast it is toggled", on === cls,
     `checked=${on} class=${cls}`);
  await ctx.close();
}

console.log("\n=== the filter, in every month ===");
{
  const { p, ctx } = await open();
  await p.click(".calswitch"); await p.waitForTimeout(200);
  const all = await p.evaluate(() =>
    [...document.querySelectorAll(".calmonth")].map((x) => x.getAttribute("data-month")));
  let leak = [], blank = [];
  for (const k of all) {
    await openMonth(p, k);
    await p.waitForTimeout(40);
    const r = await p.evaluate(() => {
      const m = document.querySelector(".calmonth:not([hidden])");
      const vis = [...m.querySelectorAll(".calev")]
        .filter((x) => getComputedStyle(x).display !== "none");
      return { n: vis.length, bad: vis.filter((x) => !x.classList.contains("act")).length,
               declared: Number(m.getAttribute("data-act")),
               says: !!m.querySelector(".caldays") };
    });
    if (r.bad) leak.push(k);
    // A month with nothing actionable must SAY so rather than render as an empty month.
    if (r.declared === 0 && r.n === 0 && !r.says) blank.push(k);
  }
  ok("no month leaks a closed item through the filter", !leak.length, leak.join(", "));
  ok("...and a month with nothing open still renders rather than going blank", !blank.length,
     blank.join(", "));
  await ctx.close();
}

// THREE VIEWS, and the one a reader lands on. A view switcher that opens on the wrong view,
// or leaves a control visible in a view it cannot act on, is the kind of thing that only ever
// shows up in front of somebody.
console.log("\n=== the three views ===");
{
  const p = await load();
  let s = await state(p);
  ok("it opens on the month, which is what a wall calendar is",
     s.view === "month" && s.tab === "calvm", `${s.view}/${s.tab}`);

  const seen = [];
  for (const [id, want] of [["calvy", "year"], ["calvl", "list"], ["calvm", "month"]]) {
    await p.click(`#${id}`);
    await p.waitForTimeout(120);
    const r = await p.evaluate(() => {
      const c = document.getElementById("cal");
      const vis = (sel) => {
        const el = c.querySelector(sel);
        return el ? getComputedStyle(el).display !== "none" : false;
      };
      return { view: c.getAttribute("data-view"), rail: vis(".calrail"),
               panels: vis(".calpanels"), list: vis(".callist"),
               paging: !document.querySelector(".calpage").hidden,
               pressed: [...c.querySelectorAll('.caltab[aria-pressed="true"]')].length };
    });
    seen.push(`${want}:${JSON.stringify(r)}`);
    const only = { month: r.panels && !r.rail && !r.list,
                   year: r.rail && !r.panels && !r.list,
                   list: r.list && !r.panels && !r.rail }[want];
    if (!only || r.view !== want || r.pressed !== 1) seen.push(`WRONG ${want}`);
    // Paging is the month's own control and has no meaning in the other two.
    if ((want === "month") !== r.paging) seen.push(`PAGING ${want}`);
  }
  ok("each view shows itself and hides the other two, with one tab lit",
     !seen.some((x) => x.startsWith("WRONG")), seen.filter((x) => x.startsWith("WRONG")).join(" "));
  ok("...and the pager is offered only where it can move something",
     !seen.some((x) => x.startsWith("PAGING")), seen.filter((x) => x.startsWith("PAGING")).join(" "));

  // Picking a month out of the year hands the reader back to the month.
  await openMonth(p, "2026-06"); await p.waitForTimeout(180);
  s = await state(p);
  ok("picking a month in the year view opens that month, in the month view",
     s.view === "month" && s.showing === "2026-06", `${s.view}/${s.showing}`);
}

console.log("\n=== every width the site is tested at ===");
{
  const WIDTHS = [320, 360, 390, 414, 480, 600, 768, 834, 1024, 1180, 1280, 1680];
  let bad = [];
  const p = await load();
  for (const w of WIDTHS) {
    await p.setViewportSize({ width: w, height: 900 });
    await p.waitForTimeout(60);
    const r = await p.evaluate(() => {
      const c = document.getElementById("cal");
      const vw = document.documentElement.clientWidth;
      const over = [...c.querySelectorAll("*")]
        .filter((el) => el.getBoundingClientRect().right > vw + 1).length;
      const shown = c.querySelectorAll(".calmonth:not([hidden])").length;
      return { over, shown, sideways: document.documentElement.scrollWidth > vw };
    });
    if (r.over || r.shown !== 1 || r.sideways) bad.push(`${w}px:${JSON.stringify(r)}`);
  }
  await p.setViewportSize({ width: 1280, height: 900 });
  ok(`nothing overflows and one month shows, at all ${WIDTHS.length} widths`, !bad.length,
     bad.slice(0, 3).join(" "));
}

console.log(fails ? `\ndocket_calendar: ${fails} FAILED` : "\ndocket_calendar: all passed");
await CTX.close();
await browser.close();
server.close();
process.exit(fails ? 1 : 0);
