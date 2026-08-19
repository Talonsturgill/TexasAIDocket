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
  const body = JSON.parse(route.request().postData());
  seen.push(body);
  /* DISPATCH ON WHAT WAS ASKED, NOT ON HOW MANY HAVE BEEN ASKED. Keying off the request count
     meant every section that added or removed a question silently shifted which canned reply
     the next section got, and the failure looked like a page bug rather than a fixture one. */
  const q = body.messages[body.messages.length - 1].content;
  const lines =
    /list everything/.test(q)
      ? [{ stage: "Reading the record" },
         { sentence: "Four comment windows are open right now." },
         { long: true }]
    : /one more/.test(q)
      ? [{ capped: true }]
    : /when did it close/.test(q)
      ? [{ stage: "Reading the record" },
         { sentence: "The comment window has closed." },
         { withheld: "numeral" }]
    : /who decides/.test(q)
      ? [{ stage: "Reading the record" },
         { sentence: "The Public Utility Commission of Texas decides it." },
         { sentence: "See [[tx-2026-0001]] for the filings." },
         { sentence: "Want the dates it moved on?" },
         { done: true }]
    : [{ stage: "Reading the record" },
       { sentence: "The Public Utility Commission of Texas decides it." },
       { done: true }];
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
ok("the note names the model", note.includes("Model in training"), note);
ok("and stays to one short line", note.trim().length < 40, note);
// Booking lives on the services page. A calendar link under the ask box is an offer made to
// somebody who came to read a record, at the moment they are reading it.
ok("no booking link under the field",
  (await page.locator(".asknote a").count()) === 0);
ok("feedback is offered instead", await page.locator("#askfbopen").isVisible());
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
ok("and the placeholder now carries the suggested follow-up",
  (await page.getAttribute("#askq", "placeholder")) === "Show me the dates it moved on.",
  await page.getAttribute("#askq", "placeholder"));

head("D. the box takes the screen while it answers");
ok("the starters step aside", await page.locator(".chips").isHidden());
ok("the note steps aside", await page.locator(".asknote").isHidden());
ok("the engine's live list steps aside", await page.locator("#ask .answer").isHidden());

// THE FIELD STAYS DOWN AND THE TALK GROWS ABOVE IT.
//
// Nothing here measured scroll, so the box was free to throw the page anywhere on submit and
// this suite stayed green. It did: it scrolled the QUESTION to just under the masthead, which
// on a page where the box sits partway down put the composer near the TOP of the screen on the
// first press. Asking a question moved the one control the reader was using.
//
// The two things that make it feel like every chat they have used are measured directly, at a
// real viewport, after a real streamed answer.
// SETTLE FIRST. The park is a SMOOTH scroll, so measuring the instant the answer lands reads a
// position the page is still travelling through. The first version of this assertion did
// exactly that and reported the composer 25px below the fold while the scroll it was racing
// was already aimed at the right place. Wait for the page to stop moving, then measure.
await page.waitForFunction(() => {
  const y = Math.round(scrollY);
  if (window.__lastY === y) { return true; }
  window.__lastY = y;
  return false;
}, null, { timeout: 4000, polling: 120 });

const seat = await page.evaluate(() => {
  const f = document.querySelector("#ask form");
  const t = document.querySelector("#askthread");
  const fr = f.getBoundingClientRect();
  return {
    fromBottom: Math.round(innerHeight - fr.bottom),
    onScreen: fr.top > 0 && fr.bottom <= innerHeight + 2,
    threadAbove: t.getBoundingClientRect().bottom <= fr.top + 4,
    threadHasText: t.textContent.trim().length > 0,
  };
});
ok(`the field is parked near the bottom, ${seat.fromBottom}px up from it`,
   seat.onScreen && seat.fromBottom >= 0 && seat.fromBottom < 140,
   JSON.stringify(seat));
ok("the talk sits above it rather than below", seat.threadAbove && seat.threadHasText,
   JSON.stringify(seat));

head("E. the closing offer waits in the field");
ok("it is suggested in the placeholder, not in a button",
  (await page.getAttribute("#askq", "placeholder")) === "Show me the dates it moved on.",
  await page.getAttribute("#askq", "placeholder"));
ok("no chip is rendered any more", (await page.locator(".asknext").count()) === 0);
ok("the field itself is still empty", (await page.inputValue("#askq")) === "");
ok("and the control says what it will do",
  (await page.getAttribute('button[type="submit"]', "aria-label")) ===
    "Use the suggested question");

// The arrow accepts rather than sends, which is the whole two-press design.
await page.click('button[type="submit"]');
await page.waitForTimeout(150);
ok("pressing the arrow loads it into the field",
  (await page.inputValue("#askq")) === "Show me the dates it moved on.",
  await page.inputValue("#askq"));
ok("but does NOT send it", seen.length === 1, `${seen.length} requests`);
ok("the placeholder goes back to normal",
  (await page.getAttribute("#askq", "placeholder")) === "Ask a follow-up");

head("F. writing your own question puts the suggestion away");
// Earn a real suggestion rather than setting the placeholder by hand, which would leave the
// client's own state untouched and test nothing.
await page.fill("#askq", "who decides it then");
await page.press("#askq", "Enter");
await page.waitForSelector(".askfrom", { timeout: 8000 });
ok("a fresh answer suggests again",
  (await page.getAttribute("#askq", "placeholder")) === "Show me the dates it moved on.",
  await page.getAttribute("#askq", "placeholder"));
await page.fill("#askq", "something else entirely");
await page.waitForTimeout(120);
ok("typing dismisses it",
  (await page.getAttribute("#askq", "placeholder")) === "Ask a follow-up",
  await page.getAttribute("#askq", "placeholder"));
ok("and the control goes back to sending",
  (await page.getAttribute('button[type="submit"]', "aria-label")) === "Ask");
await page.fill("#askq", "");

// ------------------------------------------------------------------ cut
head("G. an answer the guard cut");
await page.fill("#askq", "when did it close");
await page.press("#askq", "Enter");
await page.waitForSelector(".askstop", { timeout: 8000 });
// Indexed from the END, not from a fixed position. Adding a question to an earlier section
// used to shift every index after it and the failure looked like a page bug.
const last = seen[seen.length - 1];
ok("the follow-up carried the whole conversation", last.messages.length >= 3,
  JSON.stringify(last.messages.map((m) => m.role)));
/* Only what the reader SAW goes back. A sentence withheld from them must not be one the model
   can build on either, or a refused claim re-enters on the next question. */
ok("and only guard approved text went back",
  last.messages[1].content === "The Public Utility Commission of Texas decides it. " +
    "See [[tx-2026-0001]] for the filings. Want the dates it moved on?",
  last.messages[1].content);
ok("the cut is explained in words",
  (await page.locator(".askstop").textContent()).includes("figure the record does not carry"),
  await page.locator(".askstop").textContent());
ok("no chip is invented for a cut answer", (await page.locator(".asknext").count()) === 0);
ok("every exchange is still on screen", (await page.locator(".askturn").count()) === 3,
  String(await page.locator(".askturn").count()));

// ------------------------------------------------------------------ capped
head("H. the month running out says so in this page's own words");
await page.fill("#askq", "one more");
await page.press("#askq", "Enter");
await page.waitForTimeout(600);
const capped = await page.locator(".askreply").last().textContent();
ok("it says the written answers are spent", capped.includes("last written answer"), capped);
ok("and points at the half that still works", capped.includes("Typing still searches"), capped);

// ------------------------------------------------------------------ reset
head("I. start over puts it back");
await page.click(".askagain");
await page.waitForTimeout(200);
ok("the thread is gone", await page.locator("#askthread").isHidden());
ok("the note is back", await page.locator(".asknote").isVisible());
ok("the starters are back", await page.locator(".chips").isVisible());
ok("the placeholder is back",
  (await page.getAttribute("#askq", "placeholder")) === "Ask about any AI decision in Texas");
ok("and the next question starts a fresh conversation",
  (await page.evaluate(() => document.querySelectorAll(".askturn").length)) === 0);

// ------------------------------------------------------------------ feedback
head("J. feedback, which is the point of saying the model is in training");
let sent = null;
await page.route("**/formsubmit.co/**", async (route) => {
  sent = JSON.parse(route.request().postData());
  await route.fulfill({ status: 200, contentType: "application/json",
                        body: JSON.stringify({ success: "true" }) });
});
// Reopen a conversation so there is an exchange available to attach.
await page.fill("#askq", "who decides the ERCOT transmission rule");
await page.press("#askq", "Enter");
await page.waitForSelector(".askfrom", { timeout: 8000 });

ok("feedback is still reachable after an answer",
  await page.locator(".askfrom button", { hasText: "Send feedback" }).isVisible());
await page.locator(".askfrom button", { hasText: "Send feedback" }).click();
await page.waitForTimeout(200);
ok("the dialog opens", await page.locator("#askfb").isVisible());
ok("the attach row appears once there is an exchange",
  await page.locator("#askfbattachrow").isVisible());
const ctx = await page.locator("#askfbctxview").textContent();
ok("and what would be attached is shown before sending",
  ctx.includes("who decides") && ctx.includes("Public Utility Commission"), ctx.slice(0, 90));

await page.fill("#askfbtext", "it missed the comment deadline");
await page.click("#askfbsend");
await page.waitForTimeout(400);
ok("the note reaches the forwarder", sent && sent.feedback === "it missed the comment deadline",
  JSON.stringify(sent));
ok("the exchange rides along when ticked", sent && sent.exchange.includes("Public Utility"),
  (sent && sent.exchange || "").slice(0, 60));
ok("and it is labelled so two products stay sortable",
  sent && sent._subject.includes("Texas AI Docket"), sent && sent._subject);
ok("the reader is thanked", (await page.locator("#askfbmsg").textContent()).includes("Thanks"),
  await page.locator("#askfbmsg").textContent());

// Unticking has to actually withhold it, or the checkbox is decoration.
await page.waitForTimeout(1800);
await page.locator(".askfrom button", { hasText: "Send feedback" }).click();
await page.waitForTimeout(200);
await page.uncheck("#askfbattach");
ok("unticking hides the preview too", await page.locator("#askfbctxview").isHidden());
await page.fill("#askfbtext", "second note");
await page.click("#askfbsend");
await page.waitForTimeout(400);
ok("nothing is attached when the box is unticked", sent && sent.exchange === "",
  JSON.stringify(sent && sent.exchange));

head("K. an answer that ran out of room");
await page.click(".askagain");
await page.waitForTimeout(200);
await page.fill("#askq", "list everything");
await page.press("#askq", "Enter");
await page.waitForSelector(".askstop", { timeout: 8000 });
const longMsg = await page.locator(".askstop").last().textContent();
ok("it says the answer was too long", longMsg.includes("ran longer than the space"), longMsg);
ok("the sentence that did land is still shown",
  (await page.locator(".askreply").last().textContent()).includes("Four comment windows"));
// The whole point. A fragment like "under the Paperw" reaching a reader is worse than a
// visible stop, because a truncation and the record ending there look identical.
ok("and no fragment was published",
  !(await page.locator(".askreply").last().textContent()).match(/[a-z]{3}$/m) ||
  (await page.locator(".askreply").last().textContent()).includes("right now."));

head("L. nothing threw across any of that");
// Let the page finish anything it defers on scroll before asking.
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
await page.waitForTimeout(600);
ok("clean console", errs.length === 0, errs.join(" | "));

console.log("");
console.log(fail === 0 ? `ask_written: all passed, ${pass} checks`
                       : `ask_written: FAILED, ${fail} of ${pass + fail}`);
await b.close();
process.exit(fail ? 1 : 0);
