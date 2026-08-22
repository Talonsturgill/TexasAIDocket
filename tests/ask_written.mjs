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
ok("a county's construction cites the register it came from",
  byHref["construction/"] === "the construction register", JSON.stringify(hrefs));
ok("a data center cites its own name, which is what the register calls it",
  byHref["facility/bexar-1/"] === "Bexar 1", JSON.stringify(hrefs));
ok("a reservoir cites the water record rather than repeating the lake",
  byHref["water/"] === "the water record", JSON.stringify(hrefs));
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
  await ph.route("**://challenges.cloudflare.com/**", (r) => r.abort());
  await ph.goto(URL_);
  await ph.waitForTimeout(400);
  await ph.evaluate(() => scrollTo(0, 600));
  await ph.waitForTimeout(150);

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
          c.enqueue(enc.encode(JSON.stringify({ stage: "Reading the record" }) + "\n")); } }),
          { status: 200, headers: { "content-type": "application/x-ndjson" } }));
      }
      return real(u, o);
    };
    window.turnstile = { render: (el, o) => { setTimeout(() => o.callback("t"), 5); return 1; },
                         reset: () => {} };
  });
  await ph.fill("#askq", "why does the deadline keep moving");
  await ph.press("#askq", "Enter");
  await ph.waitForTimeout(800);
  const mid = await ph.evaluate(() => {
    const vis = (s) => { const e = document.querySelector(s); return e ? e.offsetParent !== null : false; };
    return { stage: (document.querySelector(".askstage") || {}).textContent || "",
             question: (document.querySelector(".askturn") || {}).textContent || "",
             chips: vis(".chips"), note: vis(".asknote"), hero: vis(".hero") };
  });
  ok("while it works, it says what it is doing", mid.stage.trim().length > 0, JSON.stringify(mid));
  ok("the question is still read back", mid.question.length > 0, JSON.stringify(mid));
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
    asking: document.body.classList.contains("asking"), y: Math.round(scrollY) }));
  ok("closing hands the screen back", !off.asking, JSON.stringify(off));
  ok("...and puts them back where they were", Math.abs(off.y - 600) < 40, JSON.stringify(off));

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
head("J. the eight second ceiling");
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
ok("and it says the rest was cut for time", /cut at eight seconds/i.test(cutText),
   cutText.slice(-90));
ok("the box is usable again", !(await page.getAttribute("#askq", "disabled")));

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
  await slow.route("**://challenges.cloudflare.com/**", (r) => r.abort());
  await slow.addInitScript(() => {
    // Nine and a half seconds, which is past the eight second ceiling and inside the suite's
    // patience. A real solve on a bad connection is the same shape.
    window.turnstile = { render: (el, o) => { setTimeout(() => o.callback("t"), 9500); return 1; },
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
  await slow.press("#askq", "Enter");
  // Past the ceiling, past the token, and past whatever the token's arrival sets going.
  // Past the ceiling at eight seconds and past the token at nine and a half, which is the
  // window where the ending gets overwritten.
  await slow.waitForTimeout(13000);
  const text = ((await slow.textContent(".askreply")) || "").trim();
  ok("the reader is not left looking at nothing", text.length > 0, JSON.stringify(text));
  ok("and what stands is an ending rather than a status line",
     !/^Reading the record$|^Passing the human check$/i.test(text), JSON.stringify(text));
  ok("the box is usable again", !(await slow.getAttribute("#askq", "disabled")));
  await slow.close();
}

console.log(fail === 0 ? `ask_written: all passed, ${pass} checks`
                       : `ask_written: FAILED, ${fail} of ${pass + fail}`);
await b.close();
process.exit(fail ? 1 : 0);
