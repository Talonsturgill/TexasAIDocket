// scan_watch: the page that watches a run, driven in a real browser against a stubbed
// endpoint, because everything it does happens at read time and no build-time lint can reach
// it. The stub is the point: these assert what the PAGE does with an answer, not what the
// scanner returns, and the scanner is checked on its own side.
//
// Four properties matter more than the rest and each has a check here.
//
//   IT SENDS THE TOKEN AND NOTHING ELSE. This is the one page on the site that makes a
//   request, so what leaves it is checked rather than assumed.
//   IT PHONES NO OTHER HOST. Same reason the ask box proves it phones nobody at all.
//   THE FEED ONLY GROWS. Each poll returns every row again, and rebuilding the list would
//   move or drop a line under a reader mid sentence.
//   IT STOPS. A bad token, a stopped run and a run that outlasts the page all end with a
//   sentence rather than with the page asking forever against somebody else's bill.
//
//     SITE=docs node tests/scan_watch.mjs

import pw from '/opt/node22/lib/node_modules/playwright/index.js'; const { chromium } = pw;
import path from 'node:path';
import http from 'node:http';
import { createReadStream, statSync } from 'node:fs';
// RESOLVED, not used raw. SITE is a relative path everywhere else in this directory, and a
// relative one makes an invalid file:// url rather than a wrong page, so the failure is loud
// but it is loud about the wrong thing.
const SITE = path.resolve(process.env.SITE || "docs");
let fails = 0;
const ok = (label, cond, extra="") => {
  console.log(`  ${cond ? "ok  " : "FAIL"}  ${label}${cond ? "" : "  " + extra}`);
  if (!cond) fails++;
};
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });

async function run(token, replies) {
  const p = await b.newPage({ viewport:{width:900,height:900} });
  let calls = 0, sentTokens = [], i = 0;
  await p.route("**/result", async route => {
    calls++;
    const body = JSON.parse(route.request().postData() || "{}");
    sentTokens.push(body.token);
    const r = replies[Math.min(i++, replies.length-1)];
    await route.fulfill({ status: r.code || 200, contentType: "application/json",
                          body: JSON.stringify(r.body) });
  });
  const other = [];
  p.on("request", r => { if (!r.url().startsWith("file://") && !r.url().includes("/result")) other.push(r.url()); });
  await p.goto(`file://${SITE}/scan/watch/index.html${token ? "?t=" + token : ""}`, {waitUntil:"load"});
  await p.waitForTimeout(900);
  const out = await p.evaluate(() => ({
    state: document.getElementById("wstate").textContent.trim(),
    feed: [...document.querySelectorAll("#wfeed li")].map(e => e.textContent.trim()),
    chain: [...document.querySelectorAll("#wchain li")].map(e => e.dataset.state || ""),
    done: document.getElementById("wdone").hidden ? null : document.getElementById("wdone").textContent.trim(),
    help: !document.getElementById("whelp").hidden,
  }));
  await p.close();
  return { ...out, calls, sentTokens, other };
}

console.log("=== no token in the link ===");
let r = await run("", [{body:{}}]);
ok("says the link is missing its token", /link you were given/i.test(r.state), r.state);
ok("...and asks the scanner nothing", r.calls === 0, String(r.calls));

console.log("=== a run in flight ===");
r = await run("abc123def456", [{body:{status:"running", progress:[
  {phase:"footprint", note:"Read the site and pulled the operations."},
  {phase:"industry",  note:"Looking for what the trade has published."}]}}]);
ok("sends the token from the link, and only that", r.sentTokens[0] === "abc123def456", JSON.stringify(r.sentTokens));
ok("renders every line of the feed", r.feed.length === 2, JSON.stringify(r.feed));
ok("marks the finished stage done and the current one live",
   r.chain[0] === "done" && r.chain[1] === "live", JSON.stringify(r.chain));
ok("nothing is requested from any other host", r.other.length === 0, JSON.stringify(r.other.slice(0,2)));

console.log("=== the feed only grows ===");
r = await run("tok", [
  {body:{status:"running", progress:[{phase:"footprint", note:"one"}]}},
  {body:{status:"running", progress:[{phase:"footprint", note:"one"},{phase:"industry", note:"two"}]}},
  {body:{status:"done", headline:"Two places worth a look.", progress:[
    {phase:"footprint",note:"one"},{phase:"industry",note:"two"},{phase:"critic",note:"three"}]}}]);
await new Promise(r2 => setTimeout(r2, 100));
ok("a line already read is never duplicated", new Set(r.feed).size === r.feed.length, JSON.stringify(r.feed));

console.log("=== finished ===");
r = await run("tok", [{body:{status:"done", headline:"Two places worth a look.", progress:[
  {phase:"critic", note:"Checked and passed."}]}}]);
ok("says it finished", /finished/i.test(r.state), r.state);
ok("...and leaves no station pulsing, because nothing is still running",
   r.chain.every(c => c !== "live"), JSON.stringify(r.chain));
ok("shows the headline it was given", r.done === "Two places worth a look.", String(r.done));
ok("...and says where the report goes", r.help);

console.log("=== a bad token ===");
r = await run("nope", [{code:404, body:{error:"not found"}}]);
ok("a link that matches no scan says so", /does not match a scan/i.test(r.state), r.state);

console.log("=== a run that stopped ===");
r = await run("tok", [{body:{status:"failed", progress:[]}}]);
ok("a stopped run is stated, not spun on", /stopped before it finished/i.test(r.state), r.state);

// THE SEAM. Everything above tests the watch page given a token. This tests where the token
// comes from, which is the join nobody was checking: the form posts, the gatekeeper answers,
// and the requester has to LAND on the page that watches. Before 2026-08-20 that join did not
// exist, the form said "we got it" and the run happened where nobody could see it.
console.log("=== the form hands the requester over ===");
{
  const TYPES = { ".html":"text/html", ".css":"text/css", ".js":"text/javascript",
                  ".svg":"image/svg+xml", ".json":"application/json", ".woff2":"font/woff2",
                  ".png":"image/png", ".webp":"image/webp", ".ico":"image/x-icon",
                  ".xml":"application/xml", ".txt":"text/plain" };
  const server = http.createServer((rq, rs) => {
    let f = path.join(SITE, decodeURIComponent(rq.url.split("?")[0]));
    if (!f.startsWith(SITE)) { rs.writeHead(403).end(); return; }
    try { if (statSync(f).isDirectory()) f = path.join(f, "index.html"); statSync(f); }
    catch { rs.writeHead(404).end("no"); return; }
    rs.writeHead(200, { "content-type": TYPES[path.extname(f)] || "application/octet-stream" });
    createReadStream(f).pipe(rs);
  });
  await new Promise(r => server.listen(0, "127.0.0.1", r));
  const origin = `http://127.0.0.1:${server.address().port}`;

  const p = await b.newPage({ viewport:{width:900,height:900} });
  let sent = null, hitResult = 0;
  const other = [];
  await p.route("**/request", async route => {
    sent = JSON.parse(route.request().postData() || "{}");
    await route.fulfill({ status:200, contentType:"application/json",
      body: JSON.stringify({ token: "a".repeat(32), status: "queued", cached: false }) });
  });
  await p.route("**/result", route => { hitResult++; route.fulfill({ status:200,
    contentType:"application/json", body: JSON.stringify({status:"queued", progress:[]}) }); });
  p.on("request", r => {
    const u = r.url();
    if (!u.startsWith("file://") && !u.includes("/request") && !u.includes("/result")
        && !u.includes("challenges.cloudflare.com")) other.push(u);
  });

  // OVER HTTP, not file://, and this section alone. The handoff navigates to `watch/?t=`,
  // which is a DIRECTORY url, and a directory url serves index.html on a web server and a
  // file listing on file://. Testing the join over file:// would assert the address bar and
  // prove nothing about the page, which is the half that matters.
  await p.goto(`${origin}/scan/`, {waitUntil:"load"});
  await p.fill("#start form.leadform [name=website]", "https://www.Example.com/about");
  await p.fill("#start form.leadform [name=email]", "someone@example.com");
  await p.click("#start form.leadform button[type=submit]");
  await p.waitForURL(/scan\/watch\//, { timeout: 8000 }).catch(() => {});
  await p.waitForTimeout(1500);

  ok("the form posts the url the reader typed", sent && sent.url === "https://www.Example.com/about",
     JSON.stringify(sent));
  ok("...and the requester LANDS on the page that watches, carrying the token",
     /\/scan\/watch\/\?t=a{32}$/.test(p.url()), p.url());
  ok("...and that page immediately starts asking about that scan", hitResult > 0);
  ok("nothing is posted to the mail fallback when the gatekeeper answered",
     !other.some(u => u.includes("formsubmit")), other.join(" "));

  const st = await p.evaluate(() => document.getElementById("wstate")?.textContent.trim() || "");
  ok("...and it says the run is queued rather than showing an empty page", /queued/i.test(st), st);
  await p.close();
  await new Promise(r => server.close(r));
}

console.log(fails ? `\nwatch: ${fails} FAILED` : "\nwatch: all passed");
await b.close();
process.exit(fails ? 1 : 0);
