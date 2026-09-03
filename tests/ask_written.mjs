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
const failed = [];
const ok = (l, c, d = "") => {
  if (c) { pass++; return; }
  fail++;
  failed.push(`${l}${d ? "  " + d : ""}`);
  console.log(`  FAIL  ${failed[failed.length - 1]}`);
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
// THE CEILING IS FORTY FIVE SECONDS ON THE PUBLISHED PAGE, which is right for a hang guard and
// impossible for a suite: three ceiling cases would cost well over two minutes of waiting.
// Eight is what it used to be, so these sections keep testing the same behaviour at the same
// timings and only the number moves. Nothing on the real page sets this.
const pinCeiling = (pg) => pg.addInitScript(() => { window.__ASK_CEILING_MS__ = 8000; });
await pinCeiling(page);

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
    : /demo day/.test(q)
      ? [{ limited: "site" }]
    : /why one more/.test(q)
      ? [{ capped: true }]
    : /when did it close/.test(q)
      ? [{ stage: "Reading the record" },
         { sentence: "The comment window has closed." },
         { withheld: "numeral" }]
    : /why does it matter/.test(q)
      ? [{ stage: "Reading the record" },
         { sentence: "The body that decides sets the deadline and the rules." },
         { sentence: "Want the dates it moved on?" },
         { done: true }]
    : /instrument citation/.test(q)
      ? [{ stage: "Reading the record" },
         // THE GRID HAD NOTHING TO CITE AND THE MODEL SAID SO OUT LOUD, in the answer:
         // "...the water record, actually that citation belongs to the grid watch". Every
         // block has an id and the three preamble instruments had none.
         { sentence: "The highest peak was 90352.7 MW on August 20th, 2026, [[grid]]." },
         { sentence: "Statewide storage is 77.01 percent full, [[water]]." },
         { done: true }]
    : /stacked citations/.test(q)
      ? [{ stage: "Reading the record" },
         // Three decisions in one clause, none of which carries an identifier, so all three
         // render "the docket" and the reader sees it three times in a row.
         // Real ids, all three of which carry no identifier of their own, so all three render
         // "the docket". A made up id renders as its raw slug and would test nothing.
         { sentence: "Three counties carry one, [[tx-2026-0007]] [[tx-2026-0009]] "
                     + "[[tx-2026-0012]]." },
         { done: true }]
    : /surveillance ordinance/.test(q)
      ? [{ stage: "Reading the record" },
         // THE SENTENCE AN OWNER GOT BACK, verbatim in shape. The model names the identifier
         // and then cites it, so the label and the prose are the same eight characters.
         { sentence: "Austin City Council adopted Ordinance 20260423-029 creating City Code "
                     + "Chapter 2-19 on surveillance technology, [[tx-2026-0043]]." },
         { sentence: "A second one names no number at all, [[tx-2026-0044]]." },
         { done: true }]
    : /what is happening in Dallas/.test(q)
      ? [{ stage: "Reading the record" },
         { sentence: "Construction there is registered at $3.61 billion, [[county-dallas]]." },
         { sentence: "One data center sits on the register, [[facility-bexar-1]]." },
         { sentence: "The reservoir nearest it is [[water-lake-travis]]." },
         { done: true }]
    : /why did the PUCT/.test(q)
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
/* THE RESTING PLACEHOLDER IS READ, NOT SPELLED. It was written out here as a literal once, so
   the page had three copies of one sentence and rewording it turned this suite red for a
   change that was correct. What the reset case means is that the field goes back to how it
   shipped, so that is what gets captured. */
const resting = await page.getAttribute("#askq", "placeholder");
ok("the field invites a question", resting.length > 4 && !/follow-up/i.test(resting), resting);
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
  /* The box arms on FOCUS now, so this stands in for Cloudflare's loader either way: when
     the box appends the script tag, call the callback it registered. */
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

head("B. typing renders nothing at all, which is the point");
// The engine used to rewrite a panel on every keystroke. The owner: "very distracting". The
// answer arrives at the PRESS now and nowhere else, so a reader is looking at one thing.
await page.fill("#askq", "what can I still comment on");
await page.waitForTimeout(250);
ok("the thread stays empty while typing",
   ((await page.textContent("#askthread")) || "").trim().length === 0);
ok("and it sent nothing to do it", seen.length === 0, `${seen.length} requests`);

// ------------------------------------------------------------------ asking
head("C. pressing enter hands it to the written lane");

// AN EXPLANATORY QUESTION, because a lookup no longer leaves the page at all. "who decides
// the ERCOT transmission rule" was here and the classifier now answers it from the record in
// under half a second, which is the improvement and also means it can no longer exercise the
// written lane. A "why" is what the model is for.
await page.fill("#askq", "why did the PUCT delay the comment deadline");
await page.press("#askq", "Enter");
await page.waitForSelector(".askfrom", { timeout: 8000 });

ok("exactly one request went out", seen.length === 1, `${seen.length}`);
ok("and it carried only the question", seen[0].messages.length === 1,
  JSON.stringify(seen[0].messages));
ok("the question is read back", (await page.locator(".askturn").first().textContent())
  .includes("PUCT"));
const reply = await page.locator(".askreply").first().textContent();
ok("every sentence landed",
  reply.includes("Public Utility Commission") && reply.includes("Want the dates"), reply);
ok("the citation became a link to the decision",
  (await page.locator(".askreply a.cite").first().getAttribute("href")) === "item/tx-2026-0001/");
// tx-2026-0001 is "PUCT Project 58000, rulemaking to update ERCOT transmission cost recovery,
// comment deadline reached". The identifier is what a reader can look up, and the rest of that
// sentence is what the answer already said.
ok("...and it reads as the decision's identifier, not as its whole title",
  (await page.locator(".askreply a.cite").first().textContent()) === "Project 58000",
  await page.locator(".askreply a.cite").first().textContent());
ok("...while the full title is still there to hover",
  /PUCT Project 58000/.test(await page.locator(".askreply a.cite").first().getAttribute("title")));
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
  const box = document.querySelector("#ask");
  const f = document.querySelector("#ask form");
  const t = document.querySelector("#askthread");
  const br = box.getBoundingClientRect();
  const fr = f.getBoundingClientRect();
  const tr = t.getBoundingClientRect();
  const bs = getComputedStyle(box);
  const ts = getComputedStyle(t);
  return {
    asking: document.body.classList.contains("asking"),
    phone: matchMedia("(max-width:37.5rem)").matches,
    fromBottom: Math.round(innerHeight - fr.bottom),
    onScreen: fr.top > 0 && fr.bottom <= innerHeight + 2,
    threadAbove: tr.bottom <= fr.top + 4,
    threadHasText: t.textContent.trim().length > 0,
    box: { top: Math.round(br.top), bottom: Math.round(br.bottom),
           display: bs.display, position: bs.position },
    thread: { top: Math.round(tr.top), bottom: Math.round(tr.bottom), hidden: t.hidden,
              display: ts.display, overflowY: ts.overflowY, flex: ts.flex },
    form: { top: Math.round(fr.top), bottom: Math.round(fr.bottom) },
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
// EXPLANATORY, so it reaches the written lane. A lookup is answered from the page now and
// the page does not offer follow-ups, the model does.
await page.fill("#askq", "why does it matter who decides it");
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
// EXPLANATORY, so it reaches the worker. "one more" was here and the classifier now answers
// it from the page, so it never got as far as the cap it was written to test.
await page.fill("#askq", "why one more comment window matters");
await page.press("#askq", "Enter");
await page.waitForTimeout(600);
const capped = await page.locator(".askreply").last().textContent();
ok("it says the written answers are spent", capped.includes("last written answer"), capped);
// THE HALF IT USED TO POINT AT DOES NOT EXIST. "Typing still searches the whole record
// instantly and for nothing" described a local answer lane that was deleted on the owner's
// instruction, so the page was making a promise nothing behind it kept. What is left that a
// reader can actually use is the record itself and the answers already on screen.
ok("and points at something that still exists",
   /record itself is open/.test(capped) && !/Typing/i.test(capped), capped);

// ------------------------------------------------------------------ daily allowance
head("H2. a full demo day ends without blaming the reader");
await page.fill("#askq", "what made this a full demo day");
await page.press("#askq", "Enter");
await page.waitForTimeout(600);
const limited = await page.locator(".askreply").last().textContent();
ok("the daily allowance is named", /today's allowance/.test(limited), limited);
ok("the copy keeps the record open", /record itself is open/.test(limited), limited);
ok("and says nothing about an address or rate limiter", !/\b(?:IP|address|rate limit)\b/i.test(limited),
  limited);

/* THE PHONE THREAD HAS ITS OWN SCROLLER. The live page kept `scrollTop` at zero while the
   second answer streamed, because `park()` moved the window and the mobile stylesheet moved
   the conversation into `#askthread`. A short answer cannot distinguish those two routes,
   so this is measured only after the real sequence above has made the thread overflow. */
const liveEnd = await page.evaluate(() => {
  const t = document.getElementById("askthread");
  return {
    overflow: t.scrollHeight > t.clientHeight + 20,
    remaining: Math.round(t.scrollHeight - t.clientHeight - t.scrollTop),
    scrollTop: Math.round(t.scrollTop),
  };
});
ok("the phone conversation is long enough to exercise its scroller", liveEnd.overflow,
   JSON.stringify(liveEnd));
ok("the streamed conversation follows its live end", liveEnd.overflow && liveEnd.remaining < 32,
   JSON.stringify(liveEnd));

/* EARN THE STATE THAT START OVER HAS TO CLEAR. Resetting after an answer with no offer proves
   nothing about the stale accessible name, because the control already says Ask. */
await page.fill("#askq", "why does it matter who decides it");
await page.press("#askq", "Enter");
await page.waitForFunction(() => document.querySelector('button[type="submit"]')
  .getAttribute("aria-label") === "Use the suggested question", null, { timeout: 8000 });
ok("the reset probe really has a suggested question",
  (await page.getAttribute('button[type="submit"]', "aria-label")) ===
    "Use the suggested question");

// ------------------------------------------------------------------ reset
head("I. start over puts it back");
await page.click(".askagain");
await page.waitForTimeout(200);
ok("the thread is gone", await page.locator("#askthread").isHidden());
ok("the note is back", await page.locator(".asknote").isVisible());
ok("the starters are back", await page.locator(".chips").isVisible());
ok("the placeholder is back",
  (await page.getAttribute("#askq", "placeholder")) === resting,
  await page.getAttribute("#askq", "placeholder"));
ok("the submit control is named for a fresh question again",
  (await page.getAttribute('button[type="submit"]', "aria-label")) === "Ask",
  await page.getAttribute('button[type="submit"]', "aria-label"));
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

head("K4. the instruments can be cited, and a stack of them is not read three times");
/* Every one of the 322 blocks has an id. The grid, the reservoirs and the weather live in the
   preamble, which every question gets whether it asked or not, and for a while that meant they
   had no id at all. The model is told to cite what it says, found nothing for a grid figure,
   reached for the nearest thing and corrected itself in front of the reader. */
await page.fill("#askq", "give me an instrument citation");
await page.press("#askq", "Enter");
await page.waitForSelector(".askfrom", { timeout: 12000 });
{
  const cited = Object.fromEntries(await page.locator("a.cite").evaluateAll(
    (as) => as.map((a) => [a.getAttribute("href"), a.textContent])));
  ok("the grid watch is citable and links to its own page",
     cited["grid/"] === "the ERCOT grid watch", JSON.stringify(cited));
  ok("and so is the reservoir record", cited["water/"] === "the water record",
     JSON.stringify(cited));
}
await page.fill("#askq", "show me stacked citations");
await page.press("#askq", "Enter");
await page.waitForSelector(".askfrom", { timeout: 12000 });
{
  const reply = (await page.locator(".askreply").last().textContent()) || "";
  ok("three citations that read the same are rendered once",
     (reply.match(/the docket/g) || []).length === 1, reply.slice(0, 140));
  ok("...and the one that survives is still a link",
     (await page.locator(".askreply").last().locator("a.cite").count()) === 1);
}

head("K3. a citation may not repeat a name the sentence already used");
/* Moving from the full title to a short identifier fixed the long stutter and left a short
   one, and the page is the only place that can see both halves. Whether a name repeats depends
   on the sentence the model wrote, which nothing upstream knows. */
await page.fill("#askq", "what is the surveillance ordinance");
await page.press("#askq", "Enter");
await page.waitForSelector(".askfrom", { timeout: 12000 });
{
  const cited = await page.locator("a.cite").evaluateAll(
    (as) => as.map((a) => [a.getAttribute("href"), a.textContent]));
  const byHref = Object.fromEntries(cited);
  ok("a citation whose identifier is already in the sentence names its source instead",
     byHref["item/tx-2026-0043/"] === "the docket", JSON.stringify(cited));
  ok("...while one the sentence did not name keeps its own label",
     (byHref["item/tx-2026-0044/"] || "").length > 0
     && byHref["item/tx-2026-0044/"] !== undefined, JSON.stringify(cited));
  const reply = (await page.locator(".askreply").last().textContent()) || "";
  ok("and the identifier appears once in the sentence, not twice",
     (reply.match(/20260423-029/g) || []).length === 1, reply.slice(0, 160));
}

head("K2. a citation to something that is not a decision");
// LAST IN THE SEQUENTIAL FLOW ON PURPOSE. Every section above reads the
// state the previous answer left behind, the follow-up offer sitting in
// the field and the count of exchanges on screen, so a question inserted
// among them fails five assertions that are about something else
// entirely. This one adds an exchange, so it goes after the last section
// that counts them.
// Three quarters of what the record now holds is not a decision. The renderer hardcoded /item/<id>/ and read titles out of the decision index, so
// a dossier reached a reader as the literal string "facility-bexar-1" pointing at a page that
// does not exist. The map that fixes it is built in ask_pack, where the names are, and this
// asserts it arrived on the page rather than that the function exists.
await page.fill("#askq", "what is happening in Dallas");
await page.press("#askq", "Enter");
await page.waitForSelector(".askfrom", { timeout: 8000 });
const cites = page.locator(".askturn").first().locator("xpath=..").locator("a.cite");
const hrefs = await page.locator("a.cite").evaluateAll(
  (as) => as.map((a) => [a.getAttribute("href"), a.textContent]));
const byHref = Object.fromEntries(hrefs);
// A CITATION READS AS ATTRIBUTION, NOT AS THE THING'S DESCRIPTION. Rendering the title made
// every citation repeat the sentence it followed, three times out of three in one answer an
// owner ran. What ships now is the identifier where the record gives one and the source where
// it does not, so the link text can never be the sentence again.
// WHERE A COUNTY'S CITATION POINTS IS A BRANCH, AND THIS ASSERTED ONE SIDE OF IT. `cites` in
// ask_pack sends a county to its OWN place page when the site publishes one and to the register
// when it does not, which is the better link and the entire reason the branch exists. Dallas had
// no place page when this line was written, so `construction/` looked like the rule rather than
// like the fallback it is. On August 27th the record admitted items filed in Dallas and Denton,
// both counties got pages, and the citation correctly moved to `place/county-dallas/`. A green
// test went red because the product got better, which is a stale gate rather than a defect.
//
// So the RULE is what is checked. A citation labelled as the register exists, and it points at
// either legitimate target. Neither side is hardcoded, so the next county to earn a page costs
// nobody an afternoon.
const countyCite = hrefs.find(([, t]) => t === "the construction register");
ok("a county's construction cites the register it came from",
  !!countyCite && /^(construction\/|place\/county-[a-z-]+\/)$/.test(countyCite[0] ?? ""),
  JSON.stringify(hrefs));
ok("a data center cites its own name, which is what the register calls it",
  byHref["facility/bexar-1/"] === "Bexar 1", JSON.stringify(hrefs));
ok("a reservoir cites its own daily record rather than repeating the lake",
  byHref["water/reservoir/travis/"] === "the water record", JSON.stringify(hrefs));
ok("and no citation is long enough to be mistaken for a sentence",
  hrefs.every(([, t]) => (t || "").length <= 40), JSON.stringify(hrefs));
ok("and no citation was left rendering as its raw id",
  !hrefs.some(([, t]) => /^(facility|county|water)-/.test(t)), JSON.stringify(hrefs));

head("L. nothing threw across any of that");
// Let the page finish anything it defers on scroll before asking.
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
await page.waitForTimeout(600);
ok("clean console", errs.length === 0, errs.join(" | "));

console.log("");
// ------------------------------------------------------------------ the screen
head("I2. on a phone the box takes the screen, and gives it back");
{
  const ph = await b.newPage({ viewport: { width: 390, height: 780 } });
  await pinCeiling(ph);
  await ph.route("**://challenges.cloudflare.com/**", (r) => r.abort());
  await ph.goto(URL_);
  await ph.waitForTimeout(400);
  await ph.evaluate(() => scrollTo(0, 600));
  await ph.waitForTimeout(150);
  await ph.evaluate(() => {
    document.getElementById("askq").addEventListener("pointerdown", () => {
      window.__askTapY = window.pageYOffset;
    }, { capture: true, once: true });
  });

  /* TAPPED, NOT FOCUSED PROGRAMMATICALLY. `focus()` skips pointerdown, and a browser scrolls a
     focused input into view BEFORE the focus handler runs, so the position the box remembers
     would be the one the browser had just moved them to rather than the one they were reading.
     A phone user taps. Clicking fires the same pointerdown a tap does, and that is where the
     scroll position is captured. */
  await ph.click("#askq");
  await ph.waitForTimeout(350);
  const on = await ph.evaluate(() => {
    const vis = (s) => { const e = document.querySelector(s); return e ? e.offsetParent !== null : false; };
    const r = document.getElementById("ask").getBoundingClientRect();
    return { asking: document.body.classList.contains("asking"),
             hero: vis(".hero"), nav: vis(".masthead"), chips: vis(".chips"),
             covers: Math.round(r.height) >= innerHeight - 4,
             closeSeen: vis(".askclose") };
  });
  ok("focusing the field takes the screen", on.asking && on.covers, JSON.stringify(on));
  ok("the hero and the nav are gone", !on.hero && !on.nav, JSON.stringify(on));

  const prompts = await ph.evaluate(() => {
    const form = document.querySelector("#ask form").getBoundingClientRect();
    const buttons = Array.from(document.querySelectorAll("#ask .chips button"))
      .map((el) => el.getBoundingClientRect());
    return {
      count: buttons.length,
      minHeight: Math.round(Math.min(...buttons.map((r) => r.height))),
      aboveComposer: buttons.length > 0 && buttons[buttons.length - 1].bottom <= form.top - 4,
    };
  });
  ok("the suggested questions are thumb sized", prompts.count > 0 && prompts.minHeight >= 43,
     JSON.stringify(prompts));
  ok("the suggestions sit above the composer they can fill", prompts.aboveComposer,
     JSON.stringify(prompts));

  /* EVERY SELECTOR THE FULL SCREEN RULE HIDES MUST MATCH SOMETHING.
     The rule named `.sitefoot`, which matches nothing on any page here, so the footer stayed
     under the box in full screen mode and the owner found it on a phone. The probe that was
     meant to catch it read `document.querySelector(".sitefoot")` as null and treated null as
     "not visible", which is the most reassuring possible reading of "you are asking about an
     element that does not exist".
     So presence and visibility are checked SEPARATELY. A missing element fails as loudly as a
     visible one, because a check whose subject does not exist is worse than no check. */
  const covered = await ph.evaluate(() => {
    const out = {};
    for (const sel of [".sky", ".masthead", ".hero", "footer.site"]) {
      const el = document.querySelector(sel);
      out[sel] = el === null ? "MISSING" : (el.offsetParent !== null ? "VISIBLE" : "hidden");
    }
    return out;
  });
  for (const [sel, state] of Object.entries(covered)) {
    ok(`${sel} exists on the page at all`, state !== "MISSING", state);
    ok(`...and is hidden while the box has the screen`, state === "hidden", state);
  }
  ok("and there is a visible way out", on.closeSeen, JSON.stringify(on));

  // WHAT THE AGENT IS DOING IS THE ONLY THING LEFT. Owner: "we want to make it so that they
  // can just see what's happening as far as what the agent's doing, not everything else".
  await ph.evaluate(() => {
    const real = window.fetch;
    window.fetch = function (u, o) {
      if (String(u).includes("/answer")) {
        const enc = new TextEncoder();
        return Promise.resolve(new Response(new ReadableStream({ start(c) {
          c.enqueue(enc.encode(JSON.stringify({ stage: "Reading the record" }) + "\n"));
          setTimeout(() => c.enqueue(enc.encode(JSON.stringify({
            sentence: "The first checked sentence arrived."
          }) + "\n")), 180);
        } }),
          { status: 200, headers: { "content-type": "application/x-ndjson" } }));
      }
      return real(u, o);
    };
    window.turnstile = { render: (el, o) => { setTimeout(() => o.callback("t"), 5); return 1; },
                         reset: () => {} };
    /* This page focused the field before the stub was installed, so the real loader has
       already registered its callback and then been aborted. Invoke that registered path;
       otherwise the assertion below is still looking at the pre-request token wait rather
       than at a sentence arriving from the stream. */
    if (window.askTurnstileReady) window.askTurnstileReady();
  });
  await ph.fill("#askq", "why does the deadline keep moving");
  await ph.press("#askq", "Enter");
  await ph.waitForTimeout(800);
  const mid = await ph.evaluate(() => {
    const vis = (s) => { const e = document.querySelector(s); return e ? e.offsetParent !== null : false; };
    return { stage: (document.querySelector(".askstage") || {}).textContent || "",
             answer: (document.querySelector(".askreply p") || {}).textContent || "",
             rail: !!document.querySelector(".askstagebar"),
             question: (document.querySelector(".askturn") || {}).textContent || "",
             questionHeight: Math.round(document.querySelector(".askturn")
               .getBoundingClientRect().height),
             chips: vis(".chips"), note: vis(".asknote"), hero: vis(".hero") };
  });
  ok("while verified sentences arrive, it keeps saying what it is doing",
     /Checking each sentence against the record/.test(mid.stage) &&
       /first checked sentence/.test(mid.answer), JSON.stringify(mid));
  ok("the activity surface carries a progress rail", mid.rail, JSON.stringify(mid));
  ok("the question is still read back", mid.question.length > 0, JSON.stringify(mid));
  ok("a one line question stays a compact message", mid.questionHeight < 96,
     JSON.stringify(mid));
  ok("and nothing else is competing for the eye",
     !mid.chips && !mid.note && !mid.hero, JSON.stringify(mid));

  // THE WAY BACK PUTS THE READER WHERE THEY WERE. Hiding the page collapses it, so without
  // remembering the offset the browser returns them to the top, which feels like losing
  // their place because it is.
  await ph.click("#askclose");
  // THE RESTORE RETRIES FOR HALF A SECOND, because the page regains its height in stages and
  // an early scroll is clamped. Measuring inside that window reads a position still on its way.
  await ph.waitForTimeout(900);
  const off = await ph.evaluate(() => ({
    asking: document.body.classList.contains("asking"), y: Math.round(scrollY),
    expected: Math.round(window.__askTapY) }));
  ok("closing hands the screen back", !off.asking, JSON.stringify(off));
  ok("...and puts them back where they were", Math.abs(off.y - off.expected) < 40,
     JSON.stringify(off));

  /* A STARTER TAKES THE SCREEN TOO, and this is the exact press the owner made.
     Immersion hung off the field's FOCUS, and a starter is a button that never focuses the
     field, so the answer rendered inline with the hero, the footer and every section still
     there, and the box grew past the viewport and scrolled off the top. */
  /* START OVER FIRST. The box is still in its answering state from the question above, and
     `.answering` hides the starters, so a click on one waits forever for something that is
     deliberately not there. */
  await ph.click(".askagain");
  await ph.waitForTimeout(400);
  await ph.click(".chips [data-ask]");
  await ph.waitForTimeout(900);
  const viaChip = await ph.evaluate(() => {
    const vis = (s) => { const e = document.querySelector(s); return e ? e.offsetParent !== null : false; };
    const r = document.getElementById("ask").getBoundingClientRect();
    return { asking: document.body.classList.contains("asking"),
             fits: Math.round(r.top) === 0 && Math.round(r.height) <= innerHeight + 1,
             hero: vis(".hero"), footer: vis("footer.site"),
             answered: !!(document.querySelector(".askreply") || {}).textContent };
  });
  ok("a starter answers", viaChip.answered, JSON.stringify(viaChip));
  ok("...and takes the screen like a typed question",
     viaChip.asking && viaChip.fits, JSON.stringify(viaChip));
  ok("...with nothing else left on it",
     !viaChip.hero && !viaChip.footer, JSON.stringify(viaChip));

  await ph.close();
}

// A LAPTOP HAS ROOM FOR CONTEXT, so none of that applies there.
{
  const wide = await b.newPage({ viewport: { width: 1280, height: 800 } });
  await pinCeiling(wide);
  await wide.route("**://challenges.cloudflare.com/**", (r) => r.abort());
  await wide.goto(URL_);
  await wide.waitForTimeout(400);
  await wide.focus("#askq");
  await wide.waitForTimeout(300);
  const g = await wide.evaluate(() => {
    const h = document.querySelector(".hero");
    return { asking: document.body.classList.contains("asking"),
             hero: h ? h.offsetParent !== null : false };
  });
  ok("a laptop is not thrown into full screen", !g.asking, JSON.stringify(g));
  ok("and keeps its context", g.hero, JSON.stringify(g));
  await wide.close();
}

// ------------------------------------------------------------------ the ceiling
head("J. the ceiling, which is a hang guard and not a budget");
/* A STREAM THAT NEVER CLOSES, patched into the page itself.
   `route.fulfill` always ENDS the response, so a stubbed body arrives complete and the stream
   finishes in under a second, which tests the happy path wearing a hang's clothes. A real
   socket that holds open cannot be reached either, because `route.continue` refuses to cross
   from https to http.
   So the page's own `fetch` hands back a ReadableStream that emits a stage and a sentence and
   then simply never closes, which is the exact shape of a model that stalls mid-answer, and it
   is what a ceiling has to survive. */
await page.evaluate(() => {
  const real = window.fetch;
  window.fetch = function (u, o) {
    if (String(u).includes("/answer")) {
      const enc = new TextEncoder();
      return Promise.resolve(new Response(new ReadableStream({
        start(c) {
          c.enqueue(enc.encode(JSON.stringify({ stage: "Reading the record" }) + "\n"));
          c.enqueue(enc.encode(JSON.stringify({ sentence: "The first part arrived." }) + "\n"));
          // and never c.close()
        },
      }), { status: 200, headers: { "content-type": "application/x-ndjson" } }));
    }
    return real(u, o);
  };
});
await page.click(".askagain").catch(() => {});
await page.waitForTimeout(200);
const t0 = Date.now();
await page.fill("#askq", "why does the deadline keep moving");
await page.press("#askq", "Enter");
await page.waitForSelector(".askfrom", { timeout: 15000 });
const took = Date.now() - t0;

ok("it closed the answer inside the ceiling", took < 11000, `${took}ms`);
ok("...and not before the work had a chance", took > 7000, `${took}ms`);
const cutText = (await page.textContent(".askreply")) || "";
// IT CUTS, IT DOES NOT DISCARD. Throwing away what arrived would trade a slow answer for no
// answer, which is not what a ceiling is for.
ok("what did arrive is still on screen", /The first part arrived/.test(cutText),
   cutText.slice(0, 90));
// NO CLOCK IN THE COPY AND NOTHING ASKING THE READER TO ASK FOR LESS. Owner, on seeing the
// old line twice in one sitting: "that is a horrible thing to say to someone."
ok("and it says the answer ran long, without naming a budget the reader did not set",
   /ran long and stops here/i.test(cutText), cutText.slice(-90));
ok("...and never tells them to ask a narrower question",
   !/narrower/i.test(cutText), cutText.slice(-90));
ok("the box is usable again", !(await page.getAttribute("#askq", "disabled")));

head("J1. a slow first solve is rescued by the retry, not met with a dead end");
/* THE COLD START, WHERE THE SOLVE OUTLASTS THE FIRST WAIT. Focus arms the check, so from the
   second question on a token is earned while the reader reads. On the first it starts at a
   caret landing in an empty field, and a solve can outrun the six seconds the page waits.
   What saves it is the retry: the wait expires, the page posts without a token, the worker
   refuses it, and the second wait catches the token that was always coming. This locks that
   path down, because an owner met "That did not get through" on every new chat and the
   obvious story was that this budget was too short. It was not. The widget was in Managed
   mode and Cloudflare was demanding a click, so no token existed to wait for. */
{
  const cold = await b.newPage();
  await cold.route("**://challenges.cloudflare.com/**", (r) => r.abort());
  const asked = [];
  /* THE STUB REFUSES A MISSING TOKEN, BECAUSE THE WORKER DOES. worker.js answers
     403 {"error":"finish the human check first"} when there is no token, and a stub that
     answers 200 regardless tests the happy path wearing the failure's clothes. A first version
     of this did exactly that and passed against the six second budget it was written to catch,
     which is the fourth time in a day a test here has been green against broken code. */
  await cold.route("**/answer", async (route) => {
    const tok = JSON.parse(route.request().postData()).turnstile_token;
    asked.push(tok);
    if (!tok) {
      await route.fulfill({ status: 403, contentType: "application/json",
        body: JSON.stringify({ error: "finish the human check first" }) });
      return;
    }
    await route.fulfill({ status: 200, contentType: "application/x-ndjson",
      body: JSON.stringify({ sentence: "The Public Utility Commission decides it." }) + "\n"
          + JSON.stringify({ done: true }) + "\n" });
  });
  await cold.addInitScript(() => {
    // Eight seconds, which is past the six a repeat question gets and well inside what a real
    // solve can take on a cold tab. The old budget failed here every time.
    /* RESET DISCARDS THE SOLVE, BECAUSE THE REAL ONE DOES. turnstile.reset throws away a
       challenge in progress and starts a fresh one. A stub whose reset is a no-op leaves the
       original callback pending, so it fires anyway and the retry succeeds, which is how a
       first version of this test passed against the exact bug it was written for. */
    let pending = null, solves = 0;
    window.turnstile = {
      render: (el, o) => {
        window.__askSolve = () => {
          solves += 1;
          if (pending) clearTimeout(pending);
          pending = setTimeout(() => o.callback("t"), 8000);
        };
        window.__askSolve();
        return 1;
      },
      reset: () => { window.__askResets = (window.__askResets || 0) + 1; window.__askSolve(); },
    };
    setTimeout(function poke() {
      if (window.askTurnstileReady) window.askTurnstileReady(); else setTimeout(poke, 10);
    }, 10);
  });
  await cold.goto(URL_);
  await cold.waitForTimeout(300);
  await cold.fill("#askq", "who decides the ERCOT transmission rule");
  await cold.press("#askq", "Enter");
  await cold.waitForSelector(".askfrom", { timeout: 25000 }).catch(() => {});
  const reply = ((await cold.textContent(".askreply")) || "").trim();
  ok("the retry answered it", /Public Utility Commission/.test(reply),
     JSON.stringify(reply));
  /* HOW MANY POSTS IT TAKES IS THE MACHINE'S BUSINESS, NOT THIS TEST'S.
     On a slow runner the first wait expires and the page posts without a token, is refused,
     and the retry carries the token that was always coming. On a fast one the token lands
     inside the first wait and there is a single post. Both are correct and this test exists
     for the first, so asserting the FIRST post carried a token contradicted its own name and
     went red on CI while passing here. What has to hold either way is that the request which
     succeeded carried one. */
  ok("...and the request that succeeded carried a token",
     asked.length > 0 && asked[asked.length - 1] === "t", JSON.stringify(asked));
  ok("...so the reader never met a dead end", !/did not get through/i.test(reply), reply);
  /* A RESET IS CORRECT AFTER A TOKEN IS SPENT AND WRONG BEFORE ONE EXISTS.
     spendToken calls turnstile.reset, which DISCARDS a challenge in progress. Once the token
     has gone to the worker it is used up and re-arming immediately is the whole reason the
     next question does not wait. Calling it when no token was ever sent throws away a solve
     that is still running, which is the failure this asserts against.
     An earlier version of this assertion demanded ZERO resets, which is wrong: the successful
     path resets exactly once, after the send. It went red against correct code. */
  const resets = await cold.evaluate(() => window.__askResets || 0);
  ok("...and it re-armed once, after the token was spent rather than before it existed",
     resets === 1, String(resets));
  ok("...and it took at most one refused attempt to get there",
     asked.filter((t) => !t).length <= 1, JSON.stringify(asked));
  await cold.close();
}

head("J2. a token that lands after the ceiling may not blank the page");
/* THE SEQUENCE AN OWNER HIT ON THE FIRST QUESTION OF A SESSION, reproduced through the path
   that actually produces it, which is the Turnstile wait and not the stream.
   The ceiling is armed at the PRESS, so it is running while the token is still being earned.
   The first question of a session is the one that genuinely waits, because nothing has been
   earned yet, and a slow solve pushes that wait past eight seconds. Then:
     the ceiling fires, drops the stage element and writes "that one did not come back"
     the token finally lands, and the very next line is stage("Reading the record")
     stage sees no answer started and no sentences said, so it believes it may speak
     it finds no stage element, and CLEARS THE BODY to make one
   The ending is gone, and the next drop takes the stage line with it. The reader is looking at
   nothing. Reported as "the eight seconds didn't return anything, then went blank the first
   time around", and "the first time around" is the whole clue: later questions reuse a token
   earned while the reader was reading, so only the first one can be slow enough. */
{
  const slow = await b.newPage();
  // NOT pinCeiling here. This page sets its own, lower, below, and two init scripts writing the
  // same global in order is a thing a reader has to run in their head to understand.
  await slow.route("**://challenges.cloudflare.com/**", (r) => r.abort());
  /* THREE SECONDS, NOT THE SUITE'S EIGHT, and the number is the whole premise.
     This case needs a token that lands AFTER the ceiling has spoken. `waitForToken` gives up
     after six seconds now, for an owner who watched the box sit there, so a token can never
     arrive later than that and a ceiling at eight can never fire first. The order the bug needs
     became unreachable, the test started measuring a race instead, and CI went red on the
     assertion while the same code passed here. Pinning this page lower puts the ceiling at
     three and the token at four and a half, which is the order this is about. */
  await slow.addInitScript(() => { window.__ASK_CEILING_MS__ = 3000; });
  await slow.addInitScript(() => {
    window.turnstile = { render: (el, o) => { setTimeout(() => o.callback("t"), 4500); return 1; },
                         reset: () => {} };
    /* THE PAGE ONLY CALLS render FROM THE TURNSTILE SCRIPT'S ONLOAD, and that script is
       aborted here, so nothing invokes it and the stub sits unused. A first version of this
       test missed that, the token never arrived at all, the ceiling's message was never
       overwritten, and the test passed against the broken code it was written to catch. */
    setTimeout(function poke() {
      if (window.askTurnstileReady) window.askTurnstileReady(); else setTimeout(poke, 10);
    }, 10);
    const real = window.fetch;
    window.fetch = function (u, o) {
      // Never resolves, so only the ceiling and the token can write anything at all.
      if (String(u).includes("/answer")) return new Promise(() => {});
      return real(u, o);
    };
  });
  await slow.goto(URL_);
  await slow.waitForTimeout(300);
  await slow.fill("#askq", "why does the deadline keep moving");
  await slow.evaluate(() => { window.__askPressedAt = performance.now(); });
  await slow.press("#askq", "Enter");
  /* WAIT FOR THE ENDING, THEN WAIT PAST THE TOKEN, AND ONLY THEN LOOK.
     Both halves are needed and the first version had only one. Waiting for "an ending appeared"
     fires at three seconds, which is BEFORE the token lands at four and a half, so it read the
     correct message a second and a half before the bug overwrites it and passed against code
     that was broken. Waiting a fixed number of seconds instead is a bet on how several timers
     interleave on whatever machine is running, which is what put a red on CI and a green here.
     So: block until the ceiling has spoken, which is the state this is about, then block until
     the token is certainly in and processed, then assert what survived. */
  await slow.waitForFunction(() => {
    var r = document.querySelector(".askreply");
    return (((r && r.textContent) || "").trim()).length > 0
      && !!document.querySelector(".askfrom");
  }, null, { timeout: 25000 }).catch(() => {});
  await slow.waitForFunction(() => (performance.now() - window.__askPressedAt) > 7000,
                             null, { timeout: 25000 }).catch(() => {});
  const text = ((await slow.textContent(".askreply")) || "").trim();
  ok("the reader is not left looking at nothing", text.length > 0, JSON.stringify(text));
  ok("and what stands is an ending rather than a status line",
     !/^Reading the record$|^Passing the human check$/i.test(text), JSON.stringify(text));
  ok("the box is usable again", !(await slow.getAttribute("#askq", "disabled")));
  await slow.close();
}

if (fail) {
  /* guards_local prints only a failed step's tail. Repeat the exact assertions here so a
     failure near the beginning cannot be hidden by the later section headings. */
  console.log("\nFailed assertions:");
  failed.forEach((line) => console.log(`  FAIL  ${line}`));
}
console.log(fail === 0 ? `ask_written: all passed, ${pass} checks`
                       : `ask_written: FAILED, ${fail} of ${pass + fail}`);
await b.close();
process.exit(fail ? 1 : 0);
