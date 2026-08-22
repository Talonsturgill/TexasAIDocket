/* table_fit.mjs — a data table's columns fit what is actually in them.
 *
 * WHY THIS EXISTS
 *
 * The facility filings panel shipped with the construction register's column template, because
 * it reuses that table's class. The register puts a county or a company name in the first
 * column and this table puts a four digit year there, so 6.5rem went to "2019" and the project
 * name got 150px and wrapped to three lines, with a hand's width of empty gutter beside it on
 * every row.
 *
 * A HUNDRED AND TEN CHECKS SAID YES. The markup is valid. Every numeral traces to a
 * computation. The house style gate reads text and has no opinion about where text lands.
 * `site_fresh_check` proves the page is exactly what the ledgers produce, which it was.
 * `css_tokens` proves every var() resolves, and every one did. `responsive` proves nothing
 * overflows sideways, and nothing did, because wrapping is how the browser AVOIDS overflow.
 * Not one of them knows what a column is. GATE_LESSONS entry 62 ("A table wrapped to three lines beside an empty gutter and 110 checks said yes").
 *
 * WHAT IT ASSERTS, and the reason it is a measurement rather than a taste
 *
 *   EVERY COLUMN CLEARS ITS OWN CONTENT BY A MARGIN. For each grid table it measures every
 *   column's widest natural (nowrap) content and compares it against the track the template
 *   actually resolved to. A track under its content plus five percent is a fault, and so is any
 *   cell that has already wrapped. Both are defects with a number attached rather than opinions
 *   about density.
 *
 *   THE MARGIN IS NOT DECORATION. The two chromium builds on this machine measure the same
 *   string about four percent apart, so a table that fits by two pixels fits in one browser and
 *   wraps in the other, and a gate asserting the hairline fit reports whichever binary it
 *   happened to launch. Asserting headroom instead makes the verdict a property of the design.
 *
 *   A genuinely tight table is left alone. Where the natural total exceeds the row, wrapping is
 *   the correct thing for a browser to do and this says nothing. A gate that called a correct
 *   product a violation is how a gate gets switched off.
 *
 * AT SEVERAL WIDTHS, above the breakpoint where these tables restack to two columns on purpose.
 * The fault that prompted this gate sat at the boundary: a hundred pixels of text in a hundred
 * and four pixel track, so it wrapped at one window size and fitted at another sixteen pixels
 * narrower. One width would have been a coin toss reported as a verdict.
 *
 *     python3 scripts/site/site_build.py --out /tmp/site
 *     SITE=/tmp/site node tests/table_fit.mjs
 */

import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";
import http from "node:http";

const PREINSTALLED = process.env.PLAYWRIGHT_CHROMIUM || "/opt/pw-browsers/chromium";
const LAUNCH = fs.existsSync(PREINSTALLED) ? { executablePath: PREINSTALLED } : {};
const SITE = path.resolve(process.env.SITE || "docs");

let failures = 0;
const check = (label, cond, extra = "") => {
  console.log(`  ${cond ? "ok  " : "FAIL"}  ${label}${cond ? "" : "  " + extra}`);
  if (!cond) failures++;
};

// EVERY PAGE THAT CARRIES ONE, found rather than listed, so a new surface using the class is
// covered the day it ships instead of the day somebody remembers to add it here.
const walk = (dir) => fs.readdirSync(dir, { withFileTypes: true }).flatMap((d) =>
  d.isDirectory() ? walk(path.join(dir, d.name))
  : d.name === "index.html" ? [path.join(dir, d.name)] : []);
const pages = walk(SITE).filter((f) => fs.readFileSync(f, "utf8").includes("cbrow"));

check(`the class is on the site at all (${pages.length} pages)`, pages.length > 0,
      "no page carries .cbrow, so this gate would pass by finding nothing");

// OVER HTTP, NOT file://. The first cut of this gate loaded pages off disk, and the web font
// did not resolve the same way, so every column measured about four percent narrow, nothing
// looked like it wrapped, and the gate reported a clean pass over a table that wraps on the
// served site. A gate measuring a font nobody is served is worse than no gate. Same pattern as
// tests/contact.mjs, for the same reason.
const TYPES = { ".css": "text/css", ".png": "image/png", ".svg": "image/svg+xml",
                ".woff2": "font/woff2", ".json": "application/json", ".xml": "application/xml" };
const server = http.createServer((rq, rs) => {
  let f = path.join(SITE, decodeURIComponent(rq.url.split("?")[0]));
  if (!f.startsWith(SITE)) { rs.writeHead(403).end(); return; }
  try { if (fs.statSync(f).isDirectory()) f = path.join(f, "index.html"); fs.statSync(f); }
  catch { rs.writeHead(404).end("no"); return; }
  rs.writeHead(200, { "content-type": TYPES[path.extname(f)] || "text/html; charset=utf-8" });
  fs.createReadStream(f).pipe(rs);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const ORIGIN = `http://127.0.0.1:${server.address().port}`;

const browser = await chromium.launch(LAUNCH);
const page = await browser.newPage({ viewport: { width: 1280, height: 1200 } });

// THE MEASUREMENT. A hidden nowrap clone of each cell, in that cell's own computed font, gives
// the width the text WANTS. The browser is the only thing that can answer that honestly, which
// is the whole reason this check lives here and not in a Python lint over the markup.
// FONTS FIRST. `goto` resolves on load and a web font can still be swapping, and the fallback's
// metrics are not the ones the reader gets. Measured too early this gate saw a cell that fits in
// a font nobody is served, reported nothing, and looked exactly like a pass.
const measureOn = async (pg) => {
  await pg.evaluate(() => document.fonts.ready);
  return await pg.evaluate(() => {
  // THE MEASUREMENT IS ONLY WORTH ANYTHING IN THE FONT THE READER GETS. A fallback mono is
  // narrower than JetBrains Mono, and measured in one this gate reported that everything fits
  // while the served page wrapped. That is the exact failure this file exists to prevent,
  // committed by the file itself, so the font is asserted rather than assumed.
  const wantFont = (el) => {
    const fam = getComputedStyle(el).fontFamily.split(",")[0].replace(/["']/g, "").trim();
    return { fam, loaded: document.fonts.check(`${getComputedStyle(el).fontSize} "${fam}"`) };
  };
  const out = [];
  for (const table of document.querySelectorAll(".cbtable")) {
    const rows = [...table.querySelectorAll(".cbrow")];
    if (!rows.length) continue;
    const cs = getComputedStyle(rows[0]);
    const gap = parseFloat(cs.columnGap) || 0;
    const tracks = cs.gridTemplateColumns.split(" ").map(parseFloat);
    const cols = tracks.length;
    const natural = new Array(cols).fill(0);
    let wrapped = null;
    for (const r of rows) {
      const line = parseFloat(getComputedStyle(r).lineHeight) || 0;
      [...r.children].forEach((c, i) => {
        const probe = document.createElement("span");
        probe.style.cssText = "position:absolute;visibility:hidden;white-space:nowrap";
        probe.style.font = getComputedStyle(c).font;
        probe.style.letterSpacing = getComputedStyle(c).letterSpacing;
        probe.textContent = c.textContent;
        document.body.appendChild(probe);
        const w = probe.getBoundingClientRect().width;
        probe.remove();
        if (i < cols && w > natural[i]) natural[i] = w;
        // A CELL WRAPPED when it renders taller than one line of its own text. Empty spacer
        // cells render at zero and are not wraps.
        if (!wrapped && line && c.getBoundingClientRect().height > line * 1.5) {
          wrapped = { col: i, text: c.textContent.trim().slice(0, 46) };
        }
      });
    }
    out.push({
      cls: table.className,
      rowW: Math.round(rows[0].getBoundingClientRect().width),
      needed: Math.round(natural.reduce((a, b) => a + b, 0) + gap * (cols - 1)),
      cols: natural.map((n) => Math.round(n)),
      tracks: tracks.map((n) => Math.round(n)),
      gaps: Math.round(gap * (cols - 1)),
      font: wantFont(rows[0]),
      wrapped,
    });
  }
  return out;
  });
};
const measure = () => measureOn(page);

const WIDTHS = [1280, 1120, 960, 800];
// FIVE PERCENT, because the two chromium builds installed here measure the same string about
// four percent apart, and a reader's machine is a third instrument again. Below this a pass is
// a statement about the browser that ran the gate.
const MARGIN = 1.05;
let looked = 0;
const reported = new Set();
for (const w of WIDTHS) {
await page.setViewportSize({ width: w, height: 1200 });
for (const f of pages) {
  await page.goto(ORIGIN + "/" + path.relative(SITE, f));
  for (const t of await measure()) {
    looked++;
    if (!t.font.loaded) {
      check(`${path.relative(SITE, f)} is measured in the font it is served in`, false,
            `"${t.font.fam}" has not loaded, so every width below is a fallback's and this `
            + `gate would pass a table that wraps for a reader. Serve the page over HTTP, or `
            + `check the @font-face URL resolves from this page's directory.`);
      continue;
    }
    // A GENUINELY FULL ROW IS NOT A FAULT. Where the content cannot fit, wrapping is the right
    // thing for a browser to do and this says nothing. A gate that calls a correct product a
    // violation is how a gate gets switched off.
    if (t.needed > t.rowW) continue;

    // HEADROOM, NOT A HAIRLINE FIT. Measured in the two chromium builds on this machine, the
    // same string differs by about four percent, so "it fits by two pixels" is a verdict about
    // the measuring instrument. A column is sound when its track clears its widest content by a
    // margin wider than that disagreement, and the room to give it is already there.
    const rel = path.relative(SITE, f);
    const tight = t.cols
      .map((n, i) => ({ i, n, track: t.tracks[i] }))
      .filter((c) => c.n > 0 && c.track < c.n * MARGIN);
    // ONE LINE PER TABLE, not one per width. The same template is wrong at every width it is
    // wrong at, and four copies of one finding reads as four faults.
    const key = `${rel} ${t.cls}`;
    if ((!tight.length && !t.wrapped) || reported.has(key)) continue;
    reported.add(key);
    check(`${rel} .${t.cls.split(" ").pop()} gives every column room for what is in it`, false,
          t.wrapped
            ? `at ${w}px, "${t.wrapped.text}" wrapped in column ${t.wrapped.col + 1}, and every `
              + `column's widest string totals ${t.needed}px inside a ${t.rowW}px row. The space `
              + `is there. Columns want ${t.cols.join("/")}px and have ${t.tracks.join("/")}px.`
            : `at ${w}px, column${tight.length > 1 ? "s" : ""} `
              + tight.map((c) => `${c.i + 1} holds ${c.n}px in a ${c.track}px track`).join(", ")
              + `, under the ${Math.round((MARGIN - 1) * 100)}% margin two browsers disagree by. `
              + `The row has ${Math.max(0, t.rowW - t.needed)}px unused. Widen it there.`);
  }
}
}
check(`no table wraps with room to spare, at ${WIDTHS.join(", ")}px`, reported.size === 0,
      `${reported.size} table(s) above`);
check(`every table on those pages was measured (${looked})`, looked > 0,
      "the pages carry the class and no .cbtable was found, so the selector has drifted");

// THE GATE CAN GO RED, proven on tables built to be wrong rather than on a promise. In their OWN
// page, because the published pages carry a content security policy that refuses an inline style
// element, and a fixture whose stylesheet never applied would measure a one column table and
// agree with itself.
const fixture = await browser.newPage({ viewport: { width: 900, height: 400 } });
const at = async (html) => {
  await fixture.setContent(html);
  return await measureOn(fixture);
};

const [bad] = await at(`<style>
  .cbtable{width:600px} .cbrow{display:grid;grid-template-columns:30rem 1fr 4rem 4rem;
  column-gap:14px;font:12px monospace;line-height:18px}</style>
  <div class="cbtable"><div class="cbrow"><span>2019</span>
  <span>A project name long enough to wrap in a narrow column</span>
  <span>x</span><span>y</span></div></div>`);
check("the check bites on a table whose space went to the wrong column",
      bad && bad.wrapped && bad.needed <= bad.rowW, JSON.stringify(bad));

const [tight] = await at(`<style>
  .cbtable{width:200px} .cbrow{display:grid;grid-template-columns:3rem 1fr;
  column-gap:14px;font:12px monospace;line-height:18px}</style>
  <div class="cbtable"><div class="cbrow"><span>2019</span>
  <span>A project name far too long for two hundred pixels no matter how it is split</span>
  </div></div>`);
check("...and stays quiet when the row is genuinely too narrow for the content",
      tight && tight.wrapped && tight.needed > tight.rowW, JSON.stringify(tight));

const [wide] = await at(`<style>
  .cbtable{width:600px} .cbrow{display:grid;grid-template-columns:4rem 1fr;
  column-gap:14px;font:12px monospace;line-height:18px}</style>
  <div class="cbtable"><div class="cbrow"><span>2019</span><span>Short</span></div></div>`);
check("...and reports no wrap at all when nothing wrapped", wide && !wide.wrapped,
      JSON.stringify(wide));

await fixture.close();
await browser.close();
server.close();

if (failures) { console.error(`\ntable_fit: ${failures} FAILED`); process.exit(1); }
console.log("\ntable_fit: all passed");
