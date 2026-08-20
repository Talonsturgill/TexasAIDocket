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

// ONE CONTEXT, ONE PAGE, REUSED. The first version opened a fresh context and reloaded a
// 330KB page for every section, which was most of a suite that ran for ten minutes. A test
// slow enough to be skipped is a test that is not run, so the cost is part of the design:
// a reload happens only where a FRESH DOCUMENT is the thing under test, and a viewport
// change is a resize rather than a new browser.
const CTX = await browser.newContext({ viewport: { width: 1280, height: 900 } });
const PAGE = await CTX.newPage();
const load = async (hash = "") => {
  await PAGE.goto(`${ORIGIN}/record/${hash}`, { waitUntil: "load" });
  await PAGE.waitForFunction(() => !!document.getElementById("calprev"), null, { timeout: 8000 });
  return PAGE;
};
const open = async (opts = {}, hash = "") => {
  if (opts.javaScriptEnabled === false) {
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, ...opts });
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
  ok("the month it opened on was today's", first === "2026-08", first);
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
  for (let i = 0; i < 30; i++) await p.click("#calprev", { timeout: 400 }).catch(() => {});
  await p.waitForTimeout(250);
  const s = await state(p);
  ok("walking off the front stops at the first month, it does not wrap", s.prevOff === true);
  ok("...and the panel is still a real month", !!s.showing, String(s.showing));
  await p.click("#calnow", { timeout: 400 }).catch(() => {}); await p.waitForTimeout(200);
  ok("'this month' comes home", (await state(p)).showing === "2026-08");
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
  const sample = [all[0], all[Math.floor(all.length / 2)], all[all.length - 1], "2026-08"];
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
  const seen = [];
  for (let i = 0; i < all.length + 4; i++) {
    seen.push((await state(p)).showing);
    await p.click("#calnext", { timeout: 400 }).catch(() => {});
    await p.waitForTimeout(30);
  }
  const walked = seen.filter((v, i) => v !== seen[i - 1]);
  ok("stepping forward visits every month in order, once",
     JSON.stringify(walked) === JSON.stringify(all), walked.slice(0, 4).join(","));
  const end = await state(p);
  ok("...and stops at the last one rather than running off", end.nextOff === true);
  ok("...with the panel still real", end.showing === all[all.length - 1], end.showing);
  for (let i = 0; i < all.length + 4; i++) { await p.click("#calprev", { timeout: 400 }).catch(() => {});
                                             await p.waitForTimeout(25); }
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
  await Promise.all([p.click("#calnext", { timeout: 400 }), p.click("#calnext", { timeout: 400 }),
                     p.click("#calnext", { timeout: 400 }), p.click("#calprev", { timeout: 400 }),
                     p.click("#calnext", { timeout: 400 })]).catch(() => {});
  await p.waitForTimeout(400);
  const s = await state(p);
  ok("five taps with no pause leave exactly one month showing", s.shown === 1, String(s.shown));
  ok("...and the month view is the one showing", s.view === "month", String(s.view));

  // The filter, toggled hard, in a month that has both kinds.
  for (let i = 0; i < 8; i++) { await p.click(".calswitch", { timeout: 400 }).catch(() => {}); }
  await p.waitForTimeout(300);
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
