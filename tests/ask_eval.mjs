// ask_eval: how good the router actually is, scored against a gold set built from the record.
//
// WHAT THIS IS FOR. Every change to the ask box's scorer was previously an argument. This turns
// it into a number, and the number is printed whether it moved or not, so a change that was
// supposed to help and did nothing is visible rather than assumed.
//
// IT COSTS NOTHING. No model call anywhere. The router is deterministic code in the page and
// that is exactly the part worth measuring: it decides WHICH decision answers a question, and
// everything downstream inherits that choice.
//
// THE GOLD SET IS GENERATED, NOT COMMITTED. scripts/site/ask_eval.py derives it from
// ledger/docket.json at run time, so it can never name a decision the record no longer holds
// and it grows as the record does. A committed set would rot quietly and score the router
// against a past that no longer exists.
//
// WHAT A GOOD SCORE LOOKS LIKE. Not 100. `topic_item` asks the router to pick a topic from a
// bare topic name and several topics legitimately overlap; `phrase` asks it to find one
// decision from three rare words and some of those words are rare because they are odd rather
// than because they are identifying. The number that must not fall is `nonsense`: a query
// sharing nothing with the record must get NO route, and a box that answers those is worse
// than no box at all.
//
//     SITE=docs node tests/ask_eval.mjs
//     SITE=docs node tests/ask_eval.mjs --baseline out/ask_eval/baseline.json   (record it)
//     SITE=docs node tests/ask_eval.mjs --against out/ask_eval/baseline.json    (compare)

import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";
import http from "node:http";
import { execFileSync } from "node:child_process";

const PREINSTALLED = process.env.PLAYWRIGHT_CHROMIUM || "/opt/pw-browsers/chromium";
const LAUNCH = fs.existsSync(PREINSTALLED) ? { executablePath: PREINSTALLED } : {};
const SITE = path.resolve(process.env.SITE || "docs");
const argv = process.argv.slice(2);
const flag = (name) => { const i = argv.indexOf(name); return i < 0 ? null : argv[i + 1]; };

// The set, generated now from the record rather than read from a file somebody last touched
// months ago. Shelling out keeps ONE implementation of what a case is.
const GOLD = JSON.parse(execFileSync("python3",
  ["scripts/site/ask_eval.py"], { encoding: "utf-8", maxBuffer: 32 << 20 }));
// THIS LANE SCORES THE CASES THIS LANE CAN ANSWER, which is every case that existed before
// the record grew past the decisions. The gold set now also carries data center, construction
// and reservoir cases, and the free router has no view for any of them, so scoring them here
// would take a 99 percent number to about 45 and report a gap nobody caused as a regression
// somebody did.
//
// THE GAP IS NOT HIDDEN BY THIS, it is moved somewhere it can be counted. Every skipped case
// is a question a reader can ask, that the written lane answers for money, and that this lane
// could answer for nothing. The count is printed below for exactly that reason, and teaching
// this lane a family is finished when those cases carry lane "both" and this filter stops
// skipping them.
const CASES = GOLD.cases.filter((c) => (c.lane || "both") !== "written");
const SKIPPED = GOLD.cases.length - CASES.length;

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
const page = await browser.newPage({ viewport: { width: 1280, height: 900 },
                                     reducedMotion: "reduce" });
await page.goto(`${ORIGIN}/`, { waitUntil: "domcontentloaded" });
await page.waitForFunction(() => typeof window.__askRoute === "function", null, { timeout: 8000 });

// ONE ROUND TRIP FOR THE WHOLE SET. Asking the page 232 times over the wire is 232 protocol
// round trips for work that takes microseconds each; the router is synchronous, so the loop
// belongs inside the page.
const routes = await page.evaluate((cases) => cases.map((c) => {
  let r = null;
  try { r = window.__askRoute(c.q); } catch (e) { r = { error: String(e) }; }
  return r;
}), CASES);

// Which decisions a route actually resolves to, so an item-targeted case can be scored on
// whether the right decision is IN the answer rather than on whether the route text matches a
// string. A county route that returns the item is correct even though it is not `by_item`.
const resolved = await page.evaluate((rs) => rs.map((r) => {
  if (!r || r.error) return [];
  const idx = window.__ASK_INDEX__;
  const all = idx.items || [];
  const norm = (s) => String(s == null ? "" : s).toLowerCase();
  // THE CATALOGUE CALLS IT `item`, NOT `by_item`. The first version of this resolver checked
  // for `by_item`, so all 69 single-decision routes fell through to the catch-all that returns
  // every id, and every title case scored as "found" without the router having found anything.
  // A gold set that flatters the thing it measures is worse than none.
  if (r.view === "item" || r.view === "by_item") return [r.arg];
  if (r.view === "by_county") {
    return all.filter((i) => (i.counties || []).some((c) => norm(c) === norm(r.arg)))
              .map((i) => i.id);
  }
  if (r.view === "by_metro") {
    const m = (idx.metros || []).find((x) => x.id === r.arg) || {};
    const want = new Set((m.counties || []).map(norm));
    return all.filter((i) => (i.counties || []).some((c) => want.has(norm(c)))).map((i) => i.id);
  }
  if (r.view === "by_decider") {
    return all.filter((i) => norm(i.decider) === norm(r.arg)).map((i) => i.id);
  }
  if (r.view === "by_topic") return all.filter((i) => i.topic === r.arg).map((i) => i.id);
  return all.map((i) => i.id);
}), routes);

const score = { by_kind: {}, worst: [] };
const bump = (kind, field) => {
  const k = (score.by_kind[kind] ||= { n: 0, hit: 0, rank1: 0 });
  k.n += field === "n" ? 1 : 0;
  if (field !== "n") k[field] += 1;
};

CASES.forEach((c, i) => {
  const r = routes[i], got = resolved[i] || [];
  bump(c.kind, "n");
  if (c.expect_none) {
    // The only correct answer is no route. Anything else is the box inventing relevance.
    if (!r) bump(c.kind, "hit");
    else score.worst.push({ kind: c.kind, q: c.q, got: JSON.stringify(r) });
    return;
  }
  if (c.item) {
    // IN the answer at all, and separately FIRST. A county route that returns thirty
    // decisions containing the right one is useful; a route that puts it first is better.
    if (got.includes(c.item)) bump(c.kind, "hit");
    else score.worst.push({ kind: c.kind, q: c.q, want: c.item, got: got.slice(0, 3).join(",") });
    if (got[0] === c.item) bump(c.kind, "rank1");
    return;
  }
  const right = r && r.view === c.view &&
    String(r.arg).toLowerCase() === String(c.arg).toLowerCase();
  if (right) { bump(c.kind, "hit"); bump(c.kind, "rank1"); }
  else score.worst.push({ kind: c.kind, q: c.q, want: `${c.view}:${c.arg}`,
                          got: r ? `${r.view}:${r.arg}` : "none" });
});

const pct = (a, b) => (b ? +(100 * a / b).toFixed(1) : null);
const rows = Object.entries(score.by_kind).sort().map(([kind, k]) => ({
  kind, n: k.n, hit: pct(k.hit, k.n), first: pct(k.rank1, k.n),
}));
const totals = Object.values(score.by_kind).reduce(
  (a, k) => ({ n: a.n + k.n, hit: a.hit + k.hit, rank1: a.rank1 + k.rank1 }),
  { n: 0, hit: 0, rank1: 0 });

console.log(`ask_eval over ${totals.n} cases, generated from the record\n`);
if (SKIPPED) console.log(`  ${SKIPPED} case(s) skipped: the written lane answers `
  + `them and this one has no route to them yet\n`);
console.log("  kind          n     found   first");
for (const r of rows) {
  console.log(`  ${r.kind.padEnd(12)} ${String(r.n).padStart(3)}   ${String(r.hit).padStart(5)}%  ${String(r.first ?? "-").padStart(5)}%`);
}
console.log(`  ${"OVERALL".padEnd(12)} ${String(totals.n).padStart(3)}   ${String(pct(totals.hit, totals.n)).padStart(5)}%  ${String(pct(totals.rank1, totals.n)).padStart(5)}%`);

const report = { total: totals.n, found: pct(totals.hit, totals.n),
                 first: pct(totals.rank1, totals.n), by_kind: Object.fromEntries(
                   rows.map((r) => [r.kind, { n: r.n, found: r.hit, first: r.first }])) };

if (score.worst.length) {
  console.log(`\n  ${score.worst.length} case(s) missed. The first few:`);
  for (const w of score.worst.slice(0, 8)) {
    console.log(`    [${w.kind}] ${JSON.stringify(w.q)}  want ${w.want ?? "no route"}  got ${w.got}`);
  }
}

// RECORDING AND COMPARING. A number with nothing to compare it to is a number nobody acts on.
const out = flag("--baseline");
if (out) {
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, JSON.stringify(report, null, 1) + "\n");
  console.log(`\n  recorded as the baseline -> ${out}`);
}
let regressed = false;
const against = flag("--against");
if (against && fs.existsSync(against)) {
  const was = JSON.parse(fs.readFileSync(against, "utf-8"));
  console.log("\n  against the recorded baseline:");
  for (const [kind, now] of Object.entries(report.by_kind)) {
    const then = was.by_kind?.[kind];
    if (!then) continue;
    const d = +(now.found - then.found).toFixed(1);
    const mark = d > 0 ? "up  " : d < 0 ? "DOWN" : "same";
    console.log(`    ${kind.padEnd(12)} ${then.found}% -> ${now.found}%  ${mark} ${d > 0 ? "+" : ""}${d}`);
    // A NEGATIVE THAT STARTS ANSWERING IS A FAILURE, not a regression to weigh against a gain
    // somewhere else. Everything else is reported and left to a person.
    if (kind === "nonsense" && d < 0) regressed = true;
  }
  const overall = +(report.found - was.found).toFixed(1);
  console.log(`    ${"OVERALL".padEnd(12)} ${was.found}% -> ${report.found}%  ${overall > 0 ? "+" : ""}${overall}`);
}

await browser.close();
server.close();
// The suite passes unless the box started answering questions it has no business answering.
// Everything else here is a measurement, and a measurement that fails a build is a measurement
// people learn to route around.
if (regressed) { console.log("\nask_eval: FAILED, the box started answering nonsense"); process.exit(1); }
console.log("\nask_eval: measured");
