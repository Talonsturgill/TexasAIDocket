// contact: the way to send this desk a message without being told where it lands, driven in a
// real browser. Everything that matters here happens at READ TIME. Whether the icon opens a
// dialog or navigates, what leaves the page when Send is pressed, whether a failure loses what
// somebody wrote, and whether the thing works at all with no script: no build-time lint can
// see any of it.
//
// THE ADDRESS IS THE POINT. The dialog posts to FormSubmit's opaque alias for the mailbox, so
// a reader sends a message and a scraper reading the source finds a hash. `house_style_check`
// proves the address is in none of the published bytes; this proves the route still works
// without it, and that nothing of ours goes out in the body either.
//
// THE ENDPOINT IS STUBBED, deliberately. These assert what the PAGE does with an answer. Really
// posting would mail the desk on every run and make the suite depend on somebody else's uptime.
//
//     SITE=docs node tests/contact.mjs

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

// OVER HTTP, not file://. The contact icon's no-script href is a relative path two levels up,
// and file:// resolves that differently from the way anybody is served.
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
// REDUCED MOTION, for the reason written into docket_calendar.mjs: this site decorates every
// page with infinite animations, and Playwright's actionability loop is measured in frames.
const CTX = { viewport: { width: 1280, height: 900 }, reducedMotion: "reduce" };

console.log("=== the message goes out, and nothing of ours goes with it ===");
{
  const p = await browser.newPage(CTX);
  const sent = [];
  await p.route("**/formsubmit.co/**", async (route) => {
    sent.push({ url: route.request().url(), body: route.request().postData() });
    await route.fulfill({ status: 200, contentType: "application/json",
                          body: '{"success":"true"}' });
  });
  await p.goto(`${ORIGIN}/record/`, { waitUntil: "domcontentloaded" });
  ok("the dialog is shut on arrival",
     !(await p.evaluate(() => document.getElementById("contactbox").open)));

  await p.evaluate(() => document.getElementById("contactopen").scrollIntoView());
  await p.click("#contactopen");
  await p.waitForFunction(() => document.getElementById("contactbox").open, null,
                          { timeout: 5000 });
  ok("the icon opens it rather than following its own href", p.url().endsWith("/record/"),
     p.url());
  ok("...with the message box focused, so a keyboard can start typing",
     await p.evaluate(() => document.activeElement && document.activeElement.id === "contactmsg"));
  // MODAL, NOT MERELY OPEN. `showModal` is what gives focus trapping, escape to close and an
  // inert background; `open` alone gives a box floating over a live page.
  ok("...and modal, so the page behind it is inert",
     await p.evaluate(() => document.getElementById("contactbox").matches(":modal")));

  await p.fill("#contactmsg", "A question about a docket item.");
  await p.fill("#contactmail", "reader@example.com");
  await p.click("#contactsend");
  await p.waitForFunction(
    () => /reached the desk/.test(document.getElementById("contactstatus").textContent),
    null, { timeout: 5000 });
  ok("sending says so in words", true);
  ok("...to the ajax endpoint, which is what keeps the reader on the page",
     sent.length === 1 && sent[0].url.includes("/ajax/"),
     JSON.stringify(sent.map((s) => s.url)));

  const body = JSON.parse(sent[0].body);
  ok("...carrying the message, and the address the READER chose to give",
     body.message.includes("docket item") && body.email === "reader@example.com",
     JSON.stringify(body));
  ok("...under a subject that tells this route from the other two in the inbox",
     /message from the site/.test(body._subject), body._subject);
  // THE WHOLE PROMISE, asserted on the bytes that left. Exactly one address goes out and it
  // is the one the reader typed; anything else in there came from this side. Stated that way
  // rather than by naming the domains to look for, which is the same reasoning the gate in
  // house_style_check settled on and keeps the domain out of this file too.
  const addrs = (sent[0].body.match(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g) || []);
  ok("...and the only address in it is the reader's own",
     addrs.length === 1 && addrs[0] === "reader@example.com", JSON.stringify(addrs));

  await p.waitForFunction(() => !document.getElementById("contactbox").open, null,
                          { timeout: 5000 });
  ok("...then it closes itself, so there is nothing left to dismiss", true);
  await p.close();
}

console.log("\n=== a send that fails keeps what was written ===");
{
  const p = await browser.newPage(CTX);
  await p.route("**/formsubmit.co/**", (route) => route.abort());
  await p.goto(`${ORIGIN}/`, { waitUntil: "domcontentloaded" });
  await p.evaluate(() => document.getElementById("contactopen").scrollIntoView());
  await p.click("#contactopen");
  await p.waitForFunction(() => document.getElementById("contactbox").open, null,
                          { timeout: 5000 });
  await p.fill("#contactmsg", "Something worth keeping.");
  await p.click("#contactsend");
  await p.waitForFunction(
    () => /did not send/.test(document.getElementById("contactstatus").textContent),
    null, { timeout: 5000 });
  const r = await p.evaluate(() => ({
    open: document.getElementById("contactbox").open,
    kept: document.getElementById("contactmsg").value,
    canRetry: !document.getElementById("contactsend").disabled }));
  // Losing somebody's message AND telling them it failed is two bad things where one would do.
  ok("it stays open, keeps the message and can be tried again",
     r.open && r.kept === "Something worth keeping." && r.canRetry, JSON.stringify(r));
  await p.close();
}

console.log("\n=== with no script at all ===");
{
  // THE DEEPEST PAGE ON THE SITE, because the icon's fallback href is relative and a depth
  // that resolves at the root can still be wrong two levels down.
  const ctx = await browser.newContext({ javaScriptEnabled: false,
                                         viewport: { width: 1280, height: 900 } });
  const p = await ctx.newPage();
  await p.goto(`${ORIGIN}/place/county-bexar/`, { waitUntil: "domcontentloaded" });
  const href = await p.getAttribute("#contactopen", "href");
  ok("the icon is a real link, not a control waiting for script", !!href, String(href));
  await p.click("#contactopen");
  await p.waitForLoadState("domcontentloaded");
  ok("...and it lands on a form that reaches the same mailbox",
     p.url().includes("/services/") && (await p.locator("form.leadform").count()) > 0, p.url());
  ok("...which publishes no address and no mailto of its own",
     !/mailto:|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/.test(await p.content()));
  await ctx.close();
}

console.log("\n=== the row it sits in ===");
{
  const p = await browser.newPage({ viewport: { width: 390, height: 844 },
                                    reducedMotion: "reduce" });
  await p.goto(`${ORIGIN}/`, { waitUntil: "domcontentloaded" });
  const row = await p.evaluate(() => [...document.querySelectorAll(".socials a")].map((a) => {
    const r = a.getBoundingClientRect();
    const svg = a.querySelector("svg");
    return { label: a.getAttribute("aria-label"), href: a.getAttribute("href"),
             w: Math.round(r.width), h: Math.round(r.height),
             drawn: !!a.querySelector("svg path") &&
                    svg.getBoundingClientRect().width > 8 };
  }));
  // A MARK THAT DID NOT DRAW IS AN EMPTY BUTTON. The only visible content of every one of these
  // is a path, so a typo in one leaves a reader a blank square with a tooltip.
  ok("every icon is a thumb sized target with a mark that actually drew",
     row.length >= 4 && row.every((x) => x.w >= 44 && x.h >= 44 && x.drawn),
     JSON.stringify(row));
  ok("...and each one names where it goes, since none of them has visible text",
     row.every((x) => (x.label || "").length > 3), JSON.stringify(row.map((x) => x.label)));
  // The profiles open away from here; the contact control stays. `target` on the second would
  // open a blank tab and lose the reader.
  const tgt = await p.evaluate(() => [...document.querySelectorAll(".socials a")]
    .map((a) => [a.id, a.getAttribute("target")]));
  ok("the profiles open in a new tab and the contact control does not",
     tgt.every(([id, t]) => (id === "contactopen" ? t === null : t === "_blank")),
     JSON.stringify(tgt));
  await p.close();
}

console.log(fails ? `\ncontact: ${fails} FAILED` : "\ncontact: all passed");
await browser.close();
server.close();
process.exit(fails ? 1 : 0);
