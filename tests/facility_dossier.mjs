// facility_dossier: the researched dossiers, read the way a reader reads them.
//
// THE FIRST CHECK IS THE ONE THAT MATTERS MOST, same as the calendar. Every dossier is a real
// page at its own url. The dialog is a convenience layered on top, and if the fetch fails, the
// script is off, or the browser has no <dialog>, the anchor still navigates and the reader
// still gets the whole thing. Nothing here is reachable only through script.
//
// The expected link count is COMPUTED from the two ledgers rather than typed. The registry
// carries repeated names on purpose, a second row being a re-certification, so a hardcoded
// number was wrong the moment one facility held two rows. It did, immediately.
//
//     SITE=docs node tests/facility_dossier.mjs

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

const reg = JSON.parse(fs.readFileSync("ledger/gridwatch/datacenters.json", "utf8")).facilities;
const doss = JSON.parse(fs.readFileSync("ledger/facilities/dossiers.json", "utf8")).dossiers;
const have = new Set(doss.map((d) => d.name));
const EXPECT = reg.filter((r) => have.has(r.name)).length;

// WHERE THE ROSTER LIVES. The certified roster sat on /grid/ until the data centers tab took
// it, and this suite kept three copies of that path: the page it opens, the base it resolves
// hrefs against, and the phone block. The first would have gone red and the other two would
// have kept passing against a page with no roster on it, which is a suite disagreeing with
// itself. One name, used three times.
const ROSTER = "/datacenters/";

const browser = await chromium.launch(LAUNCH);

// ---------------------------------------------------------------- the page, with no script
{
  const ctx = await browser.newContext({ javaScriptEnabled: false });
  const p = await ctx.newPage();
  const r = await p.goto(`${ORIGIN}/facility/${doss[0].slug}/`, { waitUntil: "domcontentloaded" });
  ok("a dossier page serves with script disabled", r.status() === 200, String(r.status()));
  const n = await p.$$eval(".drow", (e) => e.length);
  ok("...and its facts are in the document", n > 0, `${n} rows`);
  const src = await p.$$eval(".dsources li", (e) => e.length);
  ok("...and so are its sources", src > 0, `${src} sources`);
  await ctx.close();
}

// ---------------------------------------------------------------- the roster links
{
  const p = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errs = [];
  p.on("pageerror", (e) => errs.push(String(e)));
  await p.goto(`${ORIGIN}${ROSTER}`, { waitUntil: "domcontentloaded" });
  const n = await p.$$eval("a.dosslink", (a) => a.length);
  ok("every registry row with a dossier is a link", n === EXPECT, `${n} of ${EXPECT}`);

  // Every link resolves. A dossier whose page was never built is a 404 a reader finds first.
  const hrefs = await p.$$eval("a.dosslink", (a) => [...new Set(a.map((x) => x.getAttribute("href")))]);
  let dead = [];
  for (const h of hrefs) {
    const res = await p.request.get(new URL(h, `${ORIGIN}${ROSTER}`).href);
    if (!res.ok()) dead.push(h);
  }
  ok("every dossier link resolves", dead.length === 0, dead.join(", "));

  await p.click("a.dosslink");
  const opened = await p
    .waitForFunction(() => {
      const d = document.getElementById("dossdlg");
      return d && d.open && d.querySelector(".drow");
    }, null, { timeout: 8000 })
    .then(() => true)
    .catch(() => false);
  ok("clicking a facility opens the dialog with its facts", opened);

  const seen = await p.evaluate(() => {
    const d = document.getElementById("dossdlg");
    return {
      facts: d.querySelectorAll(".drow").length,
      sources: d.querySelectorAll(".dsources li").length,
      gaps: d.querySelectorAll(".dgaps li").length,
      rungs: d.querySelectorAll(".drung").length,
      through: !!d.querySelector(".dossmore a"),
      styled: getComputedStyle(d).padding === "0px",
    };
  });
  ok("the dialog carries facts", seen.facts > 0, JSON.stringify(seen));
  ok("...and the sources behind them", seen.sources > 0, JSON.stringify(seen));
  ok("...and what is not public", seen.gaps > 0, JSON.stringify(seen));
  ok("...and a rung on every source", seen.rungs === seen.sources, JSON.stringify(seen));
  ok("...and a way through to the full page", seen.through, JSON.stringify(seen));
  ok("the second stylesheet reached the dialog", seen.styled, JSON.stringify(seen));

  await p.keyboard.press("Escape");
  ok("escape closes it", await p.evaluate(() => !document.getElementById("dossdlg").open));
  ok("no page errors", errs.length === 0, errs.slice(0, 2).join(" | "));
  await p.close();
}

// ---------------------------------------------------------------- the phone
{
  const p = await browser.newPage({ viewport: { width: 390, height: 780 }, isMobile: true, hasTouch: true });
  await p.goto(`${ORIGIN}${ROSTER}`, { waitUntil: "domcontentloaded" });
  await p.click("a.dosslink");
  await p.waitForFunction(() => document.getElementById("dossdlg")?.open, null, { timeout: 8000 }).catch(() => {});
  const m = await p.evaluate(() => {
    const d = document.getElementById("dossdlg");
    const r = d.getBoundingClientRect();
    return {
      w: Math.round(r.width), vw: innerWidth,
      over: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      cols: getComputedStyle(document.querySelector(".drow")).gridTemplateColumns,
    };
  });
  ok("the dialog takes the phone screen", m.w <= m.vw + 1 && m.w > m.vw - 40, JSON.stringify(m));
  ok("nothing scrolls sideways behind it", m.over <= 0, JSON.stringify(m));
  ok("a fact stacks to one column", !m.cols.trim().includes(" "), JSON.stringify(m));
  await p.close();
}

await browser.close();
server.close();
console.log(fails ? `\nfacility_dossier: ${fails} FAILED` : "\nfacility_dossier: all passed");
process.exit(fails ? 1 : 0);
