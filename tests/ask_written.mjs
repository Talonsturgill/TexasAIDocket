/* The lane that leaves the page, driven for real in a browser.
 *
 * tests/ask_engine.mjs covers the lane that sends nothing, which is most of what the box does.
 * This covers the other one. The worker is stubbed with canned ndjson, so everything below the
 * fetch is the client that ships: the streaming reader, the sentence rendering, the citation
 * links, the withheld line, the thread memory, and the growth from one field into a
 * conversation. Nothing below the network is mocked.
 *
 * Needs a built site: SITE=docs node tests/ask_written.mjs
 */
import { chromium } from "playwright";

const SITE = process.env.SITE || "docs";
const exe = process.env.PLAYWRIGHT_CHROMIUM || "/opt/pw-browsers/chromium";
const fs = await import("node:fs");
const path = await import("node:path");
const URL_ = "file://" + path.resolve(SITE) + "/index.html";

const b = await chromium.launch(fs.existsSync(exe) ? { executablePath: exe } : {});
let fail = 0, pass = 0;
const ok = (l, c, d = "") => {
  if (c) { pass++; return; }
  fail++; console.log(`  FAIL  ${l}${d ? "  " + d : ""}`);
};
const head = (t) => console.log("\n" + t);

const page = await b.newPage({ viewport: { width: 430, height: 900 }, deviceScaleFactor: 2 });
const errs = [];
page.on("pageerror", (e) => { if (!/turnstile/i.test(String(e))) errs.push(String(e)); });
page.on("console", (m) => {
  if (m.type() === "error" &&
      !/CORS|URL scheme|ERR_|font|turnstile|challenges\.cloudflare/i.test(m.text())) {
    errs.push(m.text());
  }
});
await page.route("**://challenges.cloudflare.com/**", (r) => r.abort());

// The worker, stubbed. Three turns: a clean answer with an offer, an answer the guard cut,
// and the month running out.
let seen = [];
await page.route("**/answer", async (route) => {
  seen.push(JSON.parse(route.request().postData()));
  const n = seen.length;
  const lines =
    n === 1 ? [{ stage: "Reading the record" },
               { sentence: "The Public Utility Commission of Texas decides it." },
               { sentence: "See [[tx-2026-0001]] for the filings." },
               { sentence: "Want the dates it moved on?" },
               { done: true }]
  : n === 2 ? [{ stage: "Reading the record" },
               { sentence: "The comment window has closed." },
               { withheld: "numeral" }]
  :           [{ capped: true }];
  await route.fulfill({
    status: 200, contentType: "application/x-ndjson",
    body: lines.map((l) => JSON.stringify(l)).join("\n") + "\n",
  });
});

await page.goto(URL_);
await page.waitForTimeout(400);

// ------------------------------------------------------------------ resting
head("A. at rest, before anyone has asked anything");
ok("the thread is not on screen", await page.locator("#askthread").isHidden());
ok("the note is", await page.locator(".asknote").isVisible());
const note = await page.locator(".asknote").textContent();
ok("it says typing sends nothing", note.includes("sends nothing anywhere"), note);
ok("and that pressing enter does send", note.includes("goes to a model"), note);
ok("the starters are offered", (await page.locator(".chips button").count()) > 0);
// The promise is only true if nothing has actually gone out yet.
ok("no request has been made", seen.length === 0);

head("B. typing answers in the page and still sends nothing");
await page.fill("#askq", "what can I still comment on");
await page.waitForTimeout(150);
ok("the engine answered", await page.locator("#ask .answer").isVisible());
ok("and it sent nothing to do it", seen.length === 0, `${seen.length} requests`);

// ------------------------------------------------------------------ asking
head("C. pressing enter hands it to the written lane");
// The widget the way Cloudflare drives it, with the network taken out.
await page.evaluate(() => {
  let cb = null;
  window.turnstile = {
    render: (el, o) => { cb = o.callback; setTimeout(() => cb("test-token"), 5); return 1; },
    // reset() must hand back a FRESH token, because the real one does and the box spends its
    // token on every send. A no-op reset leaves the second question waiting out the full
    // fifteen second fallback, which reads exactly like a page bug.
    reset: () => { setTimeout(() => cb && cb("test-token"), 5); },
  };
  /* The box arms on the FIRST SUBMIT now, not on focus, so askTurnstileReady does not exist
     yet. Stand in for Cloudflare's loader: when the box appends the script tag, call the
     callback it registered. */
  const realAppend = document.head.appendChild.bind(document.head);
  document.head.appendChild = function (node) {
    if (node.tagName === "SCRIPT" && /challenges\.cloudflare/.test(node.src || "")) {
      setTimeout(() => window.askTurnstileReady && window.askTurnstileReady(), 5);
      return node;
    }
    return realAppend(node);
  };
});
await page.waitForTimeout(60);

await page.fill("#askq", "who decides the ERCOT transmission rule");
await page.press("#askq", "Enter");
await page.waitForSelector(".askfrom", { timeout: 8000 });

ok("exactly one request went out", seen.length === 1, `${seen.length}`);
ok("and it carried only the question", seen[0].messages.length === 1,
  JSON.stringify(seen[0].messages));
ok("the question is read back", (await page.locator(".askturn").first().textContent())
  .includes("ERCOT"));
const reply = await page.locator(".askreply").first().textContent();
ok("every sentence landed",
  reply.includes("Public Utility Commission") && reply.includes("Want the dates"), reply);
ok("the citation became a link to the decision",
  (await page.locator(".askreply a.cite").first().getAttribute("href")) === "item/tx-2026-0001/");
ok("provenance appears", (await page.locator(".askfrom").textContent())
  .includes("Every figure checked"));
ok("the field is empty and ready", (await page.inputValue("#askq")) === "");
ok("and asks for a follow-up now",
  (await page.getAttribute("#askq", "placeholder")) === "Ask a follow-up");

head("D. the box takes the screen while it answers");
ok("the starters step aside", await page.locator(".chips").isHidden());
ok("the note steps aside", await page.locator(".asknote").isHidden());
ok("the engine's live list steps aside", await page.locator("#ask .answer").isHidden());

head("E. the closing offer becomes one press");
ok("the chip is offered", (await page.locator(".asknext").textContent()) === "Yes, show me");
await page.click(".asknext");
await page.waitForTimeout(150);
ok("pressing it loads the question",
  (await page.inputValue("#askq")) === "Show me the dates it moved on.",
  await page.inputValue("#askq"));
/* Two presses on purpose. Sending is the metered half and the note says so, so a chip that
   sent by itself would spend on a mis-tap and make that note false. */
ok("but does NOT send it", seen.length === 1, `${seen.length} requests`);
ok("the chip goes once taken up", (await page.locator(".asknext").count()) === 0);

// ------------------------------------------------------------------ cut
head("F. an answer the guard cut");
await page.fill("#askq", "when did it close");
await page.press("#askq", "Enter");
await page.waitForSelector(".askstop", { timeout: 8000 });
ok("the follow-up carried the whole conversation", seen[1].messages.length === 3,
  JSON.stringify(seen[1].messages.map((m) => m.role)));
/* Only what the reader SAW goes back. A sentence withheld from them must not be one the model
   can build on either, or a refused claim re-enters on the next question. */
ok("and only guard approved text went back",
  seen[1].messages[1].content === "The Public Utility Commission of Texas decides it. " +
    "See [[tx-2026-0001]] for the filings. Want the dates it moved on?",
  seen[1].messages[1].content);
ok("the cut is explained in words",
  (await page.locator(".askstop").textContent()).includes("figure the record does not carry"),
  await page.locator(".askstop").textContent());
ok("no chip is invented for a cut answer", (await page.locator(".asknext").count()) === 0);
ok("two exchanges are on screen", (await page.locator(".askturn").count()) === 2);

// ------------------------------------------------------------------ capped
head("G. the month running out says so in this page's own words");
await page.fill("#askq", "one more");
await page.press("#askq", "Enter");
await page.waitForTimeout(600);
const capped = await page.locator(".askreply").last().textContent();
ok("it says the written answers are spent", capped.includes("last written answer"), capped);
ok("and points at the half that still works", capped.includes("Typing still searches"), capped);

// ------------------------------------------------------------------ reset
head("H. start over puts it back");
await page.click(".askagain");
await page.waitForTimeout(200);
ok("the thread is gone", await page.locator("#askthread").isHidden());
ok("the note is back", await page.locator(".asknote").isVisible());
ok("the starters are back", await page.locator(".chips").isVisible());
ok("the placeholder is back",
  (await page.getAttribute("#askq", "placeholder")) === "Ask about any AI decision in Texas");
ok("and the next question starts a fresh conversation",
  (await page.evaluate(() => document.querySelectorAll(".askturn").length)) === 0);

head("I. nothing threw across any of that");
// Let the page finish anything it defers on scroll before asking.
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
await page.waitForTimeout(600);
ok("clean console", errs.length === 0, errs.join(" | "));

console.log("");
console.log(fail === 0 ? `ask_written: all passed, ${pass} checks`
                       : `ask_written: FAILED, ${fail} of ${pass + fail}`);
await b.close();
process.exit(fail ? 1 : 0);
