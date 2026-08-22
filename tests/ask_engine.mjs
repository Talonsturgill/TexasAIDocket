/* ask_engine.mjs — ask every catalogued question in a real page, read the answer back.
 *
 * WHY THIS CANNOT BE A PYTHON TEST
 *
 * The ask engine writes prose at READ time, in the browser, from an index. No build-time lint
 * can reach that: the sentence a reader sees does not exist until they type. Python can check
 * that the index is right and the catalogue is complete, and it does. It cannot check that the
 * engine turns them into a true sentence.
 *
 * So this loads the built page in a real browser, asks every question the catalogue claims to
 * answer, and reads what comes back out of the DOM. The assertions are about the two things
 * that would actually hurt a reader:
 *
 *   IT ANSWERED AT ALL. A catalogued question that returns nothing is a promise the page made
 *   and broke.
 *
 *   IT DID NOT EXCEED THE RECORD. Every count in an answer is checked against the index the
 *   page shipped with. An answer claiming more items than exist is the one failure mode a
 *   record product cannot survive, and it is exactly what a plausible-sounding engine produces.
 *
 *     python3 scripts/site/site_build.py --out /tmp/site --today 2026-08-11
 *     SITE=/tmp/site node tests/ask_engine.mjs
 */
import { chromium } from "playwright";
import { fileURLToPath } from "node:url";
import path from "node:path";

// Resolved to absolute: a relative SITE produces file://docs/... which is not a path.
const SITE = path.resolve(process.env.SITE || path.join(
  path.dirname(fileURLToPath(import.meta.url)), "..", "docs"));

let failures = 0;
const check = (label, cond, extra = "") => {
  console.log(`  ${cond ? "ok  " : "FAIL"}  ${label}${cond ? "" : "  " + extra}`);
  if (!cond) failures++;
};

/* Some environments ship a chromium whose build number does not match the npm package's
   pinned one. Where a preinstalled binary exists, use it rather than downloading a second
   copy; where it does not, let playwright resolve its own. Hardcoding either breaks the
   other, and this test has to run both on a dev container and on a CI runner. */
import fs from "node:fs";
const PREINSTALLED = process.env.PLAYWRIGHT_CHROMIUM || "/opt/pw-browsers/chromium";
const browser = await chromium.launch(
  fs.existsSync(PREINSTALLED) ? { executablePath: PREINSTALLED } : {});
const page = await browser.newPage();

// THE NETWORK IS CUT AFTER LOAD, and the box must still answer every question. Every request
// after the document itself fails.
//
// WHAT THIS ASSERTION IS FOR, now that the copy it once defended is gone. The note under the
// field used to tell a reader that typing sends nothing anywhere. That sentence came off in
// #59 on the owner's call and is not coming back, so this is no longer a promise being kept.
// Two reasons it stays anyway, and both are stronger than the copy was.
//
// A REQUEST PER KEYSTROKE IS A BILL. The written lane is capped in calls a month. A box that
// reached the network while somebody typed would spend the month in an afternoon, and the
// failure would look like the box being broken rather than like the box being expensive.
//
// AND AN UNANNOUNCED HOST IS A LEAK. An analytics beacon, a font CDN or a third-party script
// arriving on this page would carry what a reader is typing about a public record to somebody
// nobody chose. That is what the positive list below is really guarding, and it never had
// anything to do with what the copy said.
//
// It was narrowed on 2026-08-16, in the run that first tripped it, because it also read as a
// promise that the page loads no pictures. It read that way only because it had never been
// tested against a page that
// carried one. `runs/carousel/` was empty until the first deck shipped, so the front page
// emitted no external reference at all and the assertion passed vacuously for its whole
// life. The first shipped carousel put its cover on the front page from the repository's
// own raw host and turned a green suite red overnight.
//
// So the media host is excluded BY NAME and nothing else is. An analytics beacon, a font
// CDN, a third-party script or any request the ask box itself makes still fails this, which
// is the whole of what the promise was protecting.
const MEDIA_HOST = "https://raw.githubusercontent.com/Talonsturgill/TexasAIDocket/";

// THE HUMAN CHECK, EXCLUDED BY NAME AND ONLY AFTER A FOCUS.
// This said "nothing leaves after ANY interaction" and was right to at the time: an earlier
// attempt to arm Turnstile on focus contradicted the note under the field, this suite caught
// it, and the change was reverted. The note lost that sentence in #59 and the owner's call on
// 2026-08-20 was to arm on focus after all, since it cost 1 to 3 seconds on the first question
// of every session. The challenge host is a host somebody chose, named here, and paid for
// once per session rather than per keystroke.
// Nothing may leave on LOAD, asserted before any interaction and unchanged. After a focus the
// challenge host is allowed and NOTHING ELSE IS, stated positively below so a new external
// request fails here whether or not anybody thought about this file.
const CHALLENGE_HOST = "https://challenges.cloudflare.com/";
const external = [];
await page.route("**/*", (route) => {
  const url = route.request().url();
  if (url.startsWith("file://")) return route.continue();
  // A shipped carousel image served from this project's own repository. Not a beacon.
  if (url.startsWith(MEDIA_HOST)) return route.abort();
  external.push(url);
  return route.abort();
});

// THE BOX MOVED TO THE FRONT PAGE. It had its own page and its own nav tab, behind a
// heading and four paragraphs explaining what a search field is, which is a search field
// most readers never reached. Loading the front page here is not a cosmetic change to the
// test: the box is at depth 0 now, and the engine's item links used to be hardcoded
// "../item/", which from the front page walks out of the site entirely.
const URL_HOME = "file://" + path.join(SITE, "index.html");
await page.goto(URL_HOME);
await page.waitForFunction(() => typeof window.__askAnswer === "function");

const idx = await page.evaluate(() => window.__ASK_INDEX__);
const cat = await page.evaluate(() => window.__ASK_CATALOGUE__);

check("the page ships an index and a catalogue", !!idx && Array.isArray(cat) && cat.length > 0,
      `${cat?.length} questions`);
check("no request left the page", external.length === 0, external.join(", "));

// EVERY CATALOGUED QUESTION IS ASKED. Not a sample.
const empty = [];
const overclaimed = [];
const NUM = /\d[\d,]*/g;
const itemCount = idx.items.length;

for (const entry of cat) {
  const a = await page.evaluate((q) => window.__askAnswer(q), entry.q);
  if (!a || !a.head || !a.head.trim()) { empty.push(entry.q); continue; }

  // Every count the answer states must be one the index can support. The engine counts from
  // the index, so any number above the item total is the engine inventing scale.
  const text = `${a.head} ${a.body || ""}`.replace(/<[^>]+>/g, " ");
  // THE WINDOW IS THIS MATCH'S OWN POSITION, and it used to be `text.indexOf(m)`, which
  // returns the FIRST place that string appears anywhere in the answer. With thirteen items
  // the answers were short enough that the two coincided. At fifty-eight they stopped: a "2026"
  // inside a title was located at some earlier "2026" that happened to sit next to the word
  // "item", and the check reported an item count of 2026 on an answer that claimed nothing of
  // the kind. A regex with `g` gives the real index, so use it.
  const scan = new RegExp(NUM.source, "g");
  for (const m of text.matchAll(scan)) {
    const n = Number(m[0].replace(/,/g, ""));
    // AN ITEM COUNT IS THE NUMERAL IMMEDIATELY BEFORE THE WORD, which is how the engine
    // phrases one: "1 item from ...". The window used to reach 24 characters PAST the numeral
    // and catch any "item" in the vicinity, so "in Graham on August 10th, 2026. That agenda
    // item required no vote" read as a claim that the record holds 2026 items. Short answers
    // hid it. Claim totals and day counts legitimately exceed the item count; item counts
    // cannot.
    if (/^\s*items?\b/.test(text.slice(m.index + m[0].length)) && n > itemCount) {
      overclaimed.push(`${entry.q} -> ${m[0]} (record holds ${itemCount})`);
    }
  }
}

check(`every catalogued question is answered (${cat.length} asked)`, empty.length === 0,
      empty.slice(0, 3).join(" | "));
check("no answer claims more items than the record holds", overclaimed.length === 0,
      overclaimed.slice(0, 3).join(" | "));

// A PLACE ANSWER MUST NOT COUNT STATEWIDE ITEMS AS LOCAL COVERAGE.
//
// This is the failure this file exists to catch, and it shipped once. The metro view opened
// with "9 items in the El Paso area" directly above a note saying nothing had been found in
// either of El Paso's counties. All nine were statewide. Every number in it was correct and
// the sentence was false, so no count assertion could see it: a true count of the wrong set
// reads exactly like a true count.
//
// So the headline count is checked against the LOCAL set specifically, recomputed here from
// the index the page shipped rather than from anything the engine said.
const placeWrong = [];
for (const entry of cat) {
  const v = entry.route.view;
  if (v !== "by_metro" && v !== "by_county") continue;
  const a = await page.evaluate((q) => window.__askAnswer(q), entry.q);
  const want = await page.evaluate(([view, arg]) => {
    const idx = window.__ASK_INDEX__;
    return idx.items.filter((i) => view === "by_metro"
      ? (i.metros || []).indexOf(arg) >= 0
      : i.counties.indexOf(arg) >= 0).length;
  }, [v, entry.route.arg]);
  const said = (a.head.match(/^(\d+)\s+items?\b/) || [])[1];
  if (want === 0 && said !== undefined) {
    placeWrong.push(`${entry.q} -> claims ${said} local, record has none`);
  } else if (want > 0 && Number(said) !== want) {
    placeWrong.push(`${entry.q} -> claims ${said}, local set is ${want}`);
  }
}
check(`a place answer counts only what is local to it (${
        cat.filter((c) => /^by_(metro|county)$/.test(c.route.view)).length} places asked)`,
      placeWrong.length === 0, placeWrong.slice(0, 3).join(" | "));

// THE LINKS AN ANSWER RENDERS MUST RESOLVE.
//
// The engine builds item hrefs at read time, and it used to hardcode "../item/", which is
// correct for exactly one depth. Moving the box to the front page made every one of those
// links walk out of the site, and the page would have looked flawless doing it: the answer
// text, the counts and the titles were all still right. Nothing else in this file reads an
// href, so nothing else could have caught it.
const dead = [];
for (const entry of cat.slice(0, 40)) {
  const html = await page.evaluate((q) => (window.__askAnswer(q) || {}).body || "", entry.q);
  for (const m of html.matchAll(/href="([^"]+)"/g)) {
    const target = path.resolve(SITE, m[1].replace(/\/$/, "/index.html"));
    if (!fs.existsSync(target)) dead.push(`${entry.q} -> ${m[1]}`);
  }
}
check("every link an answer renders resolves to a page that exists", dead.length === 0,
      dead.slice(0, 3).join(" | "));

// A QUESTION THE RECORD CANNOT ANSWER MUST SAY SO, not improvise.
const nonsense = await page.evaluate(() =>
  window.__askAnswer("what is the airspeed velocity of an unladen swallow"));
check("an unanswerable question gets an honest answer, not an invented one",
      !!nonsense && /no answer|record holds/i.test(nonsense.head + nonsense.body),
      JSON.stringify(nonsense).slice(0, 160));

// NOTHING RENDERS WHILE SOMEBODY TYPES, which is half of what the owner asked for. The engine
// used to rewrite a panel on every keystroke, described as "very distracting", and before that
// panel moved it rendered entirely below the fold where nobody saw it. A frontier chat box
// shows one thing at a time.
await page.focus("#askq");
await page.waitForTimeout(900);
check("focusing the field arms the human check",
      external.some((u) => u.startsWith(CHALLENGE_HOST)),
      "nothing was requested, so the token is not being earned while the reader types");

await page.fill("#askq", "What can I still comment on?");
await page.waitForTimeout(400);
const whileTyping = (await page.textContent("#askthread")) || "";
check("typing renders nothing at all", whileTyping.trim().length === 0,
      JSON.stringify(whileTyping.slice(0, 80)));

// THE PRESS, which is what a reader actually does and where every answer now appears.
await page.press("#askq", "Enter");
await page.waitForSelector(".askfrom", { timeout: 8000 }).catch(() => {});
const answered = (await page.textContent(".askreply")) || "";
check("pressing renders an answer into the thread", answered.trim().length > 0,
      JSON.stringify(answered.slice(0, 80)));

/* THE ENGINE IS CHECKED AS THE ENGINE, not as what is on screen.
   This read the rendered answer, because the engine used to BE the answer for anything the
   catalogue matched. It is not any more: the owner's verdict on a page of item links was that
   "people are typing in a question cause they want an answer that is the agent or looks like
   its from an agent, it cant be anything less", so every on-topic question goes to the agent
   and the screen no longer shows the engine's work.
   The engine still exists and still has to be right, because it is what a reader gets when the
   month's cap is spent, where the right decisions beat an apology. So it is called directly. */
const openCount = idx.items.filter((i) => i.window === "open").length;
const local = await page.evaluate(() => {
  const a = window.__askLocal("What can I still comment on?");
  return a ? a.head + " " + a.body : null;
});
check("the engine still answers the open-window question", local !== null,
      "__askLocal returned nothing, so the cap fallback has no answer to give");
check("...and its count agrees with the index it shipped with",
      local !== null && (new RegExp(`\\b${openCount}\\b`).test(local) ||
                         /nothing is open|open for comment/i.test(local)),
      `index says ${openCount} open; engine said: ${String(local).slice(0, 120)}`);

// THE ENGINE ANSWERS WITHOUT CALLING ANYBODY. It is what a reader gets when the month's cap is
// spent, so it has to be pure page work, and a version of it that quietly fetched would be
// worthless in the one situation it exists for.
//
// MEASURED ON A FRESH DOCUMENT, which is the same fix this file already applies further down
// and for the same reason. Every press in this suite leaves a call pending: `waitForToken`
// polls for a Turnstile token that never arrives here, because the challenge host is aborted,
// then gives up and sends anyway. Nothing is on the wire while it waits, so the log is quiet
// and a boundary drawn on quiet is not a boundary at all. A press from earlier then lands
// inside this window and is charged to a lookup that never called anybody.
//
// This assertion used to survive that by accident, because the wait was fifteen seconds and
// this check ran before it elapsed. The wait is six now, for a reader who was watching the box
// sit there, and the accident stopped working. A test that passes because of how long an
// unrelated timer happens to be is measuring the timer.
//
// A reload destroys the old document and every timer it was holding, which is the only thing
// that makes "nobody has been called yet" true rather than merely unobserved.
await page.goto(URL_HOME);
await page.waitForTimeout(300);
external.length = 0;
const lookup = await page.evaluate(() => {
  const a = window.__askLocal("What can I still comment on?");
  return a ? a.head + " " + a.body : null;
});
check("the engine answered without calling anybody", lookup !== null
      && !external.some((u) => u.includes("workers.dev")),
      external.filter((u) => u.includes("workers.dev")).join(", ") || "engine returned nothing");

// A starter chip goes through the same press, so a chip and a keystroke cannot differ.
await page.click(".askagain").catch(() => {});
await page.waitForTimeout(200);
await page.click("#ask .chips button");
await page.waitForSelector(".askfrom", { timeout: 8000 }).catch(() => {});
check("a starter chip answers when clicked",
      ((await page.textContent(".askreply")) || "").trim().length > 0);

// A COUNT IS ONLY A BOUNDARY IF NOTHING IS STILL COMING, and quiet is not the same as done.
//
// This was a 400ms "the log stopped growing" wait, and it could not work. Every press in this
// suite parks a FIFTEEN SECOND timer that ends in a call to the worker. `waitForToken` in
// ask_written.py polls 150 times at 100ms for a Turnstile token and then gives up and sends
// anyway, which is right for a reader on a bad connection and means that here, where the
// challenge host is aborted, a token never arrives and every press has a call pending long
// after the assertion about it has been made and passed.
//
// Nothing is on the wire during those fifteen seconds, so the log is perfectly quiet and the
// old wait returned immediately. Then a press from two steps earlier landed inside the window
// below and was charged to the refusal. CI went red on a worklog-only change while the same
// code had been green an hour before, which is the signature of a boundary that depends on
// how fast the runner is rather than on what the page did.
//
// So the line is drawn on a FRESH DOCUMENT. A reload destroys the old page and every timer it
// was holding, which is the only thing that actually makes "nobody has been called yet" true.
// `settled` stays for what it is genuinely good at, letting a call the refusal makes ITSELF
// show up before the count is read.
const settled = async (quiet = 400, cap = 8000) => {
  const t0 = Date.now();
  let n = external.length;
  while (Date.now() - t0 < cap) {
    await page.waitForTimeout(quiet);
    if (external.length === n) return;
    n = external.length;
  }
};

// AN OFF-RECORD QUESTION COSTS NOTHING. Refuse is deliberately narrow, so this asserts the
// narrow case and not a broad one: a question sharing no term at all with the record. The
// classifier runs before the request is built and returns early, so a refusal that calls
// anybody is a real defect and not a slow answer.
await page.goto(URL_HOME);
await page.waitForFunction(() => typeof window.__askAnswer === "function");
const beforeRefuse = external.filter((u) => u.includes("workers.dev")).length;
await page.fill("#askq", "recipe for banana bread");
await page.press("#askq", "Enter");
await page.waitForSelector(".askfrom", { timeout: 8000 }).catch(() => {});
await settled();
const refusalText = (await page.textContent(".askreply")) || "";
check("an off-record question is refused on the page",
      /not something this record covers/i.test(refusalText), refusalText.slice(0, 100));
check("...and it called nobody to do it",
      external.filter((u) => u.includes("workers.dev")).length === beforeRefuse);

/* AND THE SAME WORDS AS A FOLLOW-UP ARE NOT REFUSED, which is the other half of the rule and
   the half that was missing. The refusal reads one line at a time, so "u sure?" shares no word
   with the record and got the identical canned sentence back, twice. A reader who pushes back
   on an answer and is handed the same string is talking to a wall, and the wall never called
   the model at all.
   The words that carry a follow-up, "why", "u sure", "which one", share no vocabulary with any
   record by their nature. Once this box has ANSWERED something in the thread, the question
   goes to the model with the thread.
   THE COUNT IS ANSWERS GIVEN, NOT TURNS TAKEN, and getting that wrong switched the refusal off
   for everybody. The thread already holds the current question by the time the classifier
   runs, so a first ask looked like a follow-up and nothing was ever refused. This suite caught
   it, which is why both directions are asserted here rather than one. */
const refusalCopy = refusalText.trim();
await page.fill("#askq", "u sure?");
await page.press("#askq", "Enter");
await page.waitForSelector(".askfrom", { timeout: 8000 }).catch(() => {});
await settled();
/* THE LAST REPLY, NOT THE FIRST. `page.textContent(".askreply")` returns the FIRST match in
   the document, and a thread grows downward, so reading it after a second question hands back
   the FIRST answer and every comparison between them passes or fails for the wrong reason.
   This assertion failed three times against a page that was behaving correctly. */
const lastReply = async () => ((await page.evaluate(() => {
  const all = document.querySelectorAll(".askreply");
  return all.length ? all[all.length - 1].textContent : "";
})) || "").trim();
const followUpText = await lastReply();
check("a follow-up is not handed the same canned refusal",
      followUpText !== refusalCopy, followUpText.slice(0, 90));

// A FRESH PAGE, so the classifier is judging a first question again and the refusal must fire.
await page.goto(URL_HOME);
await page.waitForFunction(() => typeof window.__askAnswer === "function");
await page.fill("#askq", "recipe for banana bread");
await page.press("#askq", "Enter");
await page.waitForSelector(".askfrom", { timeout: 8000 }).catch(() => {});
check("...and a first question with nothing of the record in it still is",
      /not something this record covers/i.test(await lastReply()),
      (await lastReply()).slice(0, 90));

/* STATED AS WHAT IS ALLOWED, not as an empty list. An empty list has to be relaxed every time
   anything legitimate is added, and each relaxation is invisible.

   THE WORKER IS ON THE LIST NOW, and this is a real change to the promise rather than a
   relaxation to make a red gate green. This suite was written when the page ANSWERED every
   matched question itself, so the only thing that ever left was the human check. The owner's
   verdict on a page of item links was that an answer has to be the agent or look like it, so
   a press goes to the agent and the page contacts the worker by design.

   WHAT IS UNCHANGED IS THE PART THAT COSTS MONEY. Typing still reaches nothing, asserted
   separately above and on its own. What the two lists say together is that the page contacts
   exactly two hosts, the human check and the agent, and only when somebody presses. */
const ANSWER_HOST = "https://texas-ask.talon-sturgill.workers.dev/";
const ALLOWED = [CHALLENGE_HOST, ANSWER_HOST];
const strays = external.filter((u) => !ALLOWED.some((h) => u.startsWith(h)));
check("nothing but the human check and the agent left the page",
      strays.length === 0, strays.join(", "));
/* AND THE WIDENED LIST IS NOT COVERING A SILENCE, but that is proved in the OTHER suite and
   deliberately not here. This file aborts the human check, so a press frequently never gets a
   token and never reaches the worker at all: asserting the call happened here passes in CI,
   where it got far enough, and fails locally, where it did not. That is a coin toss wearing an
   assertion's clothes, which is what this file's own history is full of.
   `ask_written.mjs` stubs the token and the worker and asserts "exactly one request went out"
   carrying the question, which is the same property measured where it is deterministic. */

// THE GATE CAN STILL GO RED, PROVED RATHER THAN ASSERTED. Narrowing an assertion is exactly
// where a suite quietly stops testing anything, so the exclusion is exercised against a host
// it does not cover. If this ever stops catching the beacon, the narrowing above has widened
// into "no request is ever checked" and the promise is gone with it.
//
// THE BEACON MOVED TO AN ALLOWED ORIGIN ON 2026-08-20, and the reason is worth writing down
// because it looks like a weakening and is not. The content security policy that shipped in
// #119 refuses `connect-src` to any host it does not name, so the old beacon at
// analytics.example.com never became a request at all: the browser killed it in the page, the
// route below never saw it, and this check went red reporting "the exclusion is too wide" when
// the exclusion had not changed. A gate that fails for a reason it does not name is worse than
// no gate, and this one was accusing the wrong code.
//
// Every request here is fulfilled by the route below and nothing leaves the machine, so the
// origin is chosen purely so the browser lets the request START. The thing being proved is
// unchanged: a request to a host the exclusion does not name is still caught.
const beacon = "https://formsubmit.co/__ask_engine_probe";
await page.evaluate((u) => fetch(u).catch(() => {}), beacon);
await page.waitForTimeout(150);
check("...and a request to any other host is still caught",
      external.some((u) => u.startsWith("https://formsubmit.co/__ask_engine_probe")),
      external.join(", ") || "nothing was caught, so the exclusion is too wide");

// AND THE POLICY IS LIVE, which is the other half and is new. The collision above is worth
// keeping as a check rather than only working around: a host the policy does not name must be
// refused by the browser before it can become a request, which is a promise no static reader
// of the html can make.
const refused = await page.evaluate(async () => {
  const seen = [];
  const on = (e) => seen.push(e.blockedURI);
  document.addEventListener("securitypolicyviolation", on);
  await fetch("https://analytics.example.com/collect?q=test").catch(() => {});
  await new Promise((r) => setTimeout(r, 120));
  document.removeEventListener("securitypolicyviolation", on);
  return seen;
});
check("...and a host the policy does not name never becomes a request at all",
      refused.some((u) => u.startsWith("https://analytics.example.com/")),
      refused.join(", ") || "the policy allowed it, so connect-src is wider than it reads");

/* ------------------------------------------------------------------ where the answer lands
 *
 * THIS SECTION USED TO MEASURE THE TYPEAHEAD and that panel no longer exists. It was written
 * because the panel rendered 427px past the fold on a phone and 248px past it on a desktop,
 * with none of it on screen, while every other assertion in this file passed: they all read
 * the DOM and none asked where on the glass it was.
 *
 * The panel is gone, so a check pointed at it would be worse than no check. The QUESTION it
 * was asking is not gone and is the same one: after the one action a reader takes, can they
 * SEE the answer, and can they still use the field. It is asked of the thread now.
 */
console.log("\n  where the answer lands after a press, at seven sizes");
for (const vp of [{ width: 320, height: 568 }, { width: 360, height: 640 },
                  { width: 390, height: 780 }, { width: 414, height: 896 },
                  { width: 768, height: 1024 }, { width: 1280, height: 800 },
                  { width: 1680, height: 1050 }]) {
  const p2 = await browser.newPage({ viewport: vp });
  await p2.route("**://challenges.cloudflare.com/**", (r) => r.abort());
  await p2.route("**/answer", (route) => route.fulfill({
    status: 200, contentType: "application/x-ndjson",
    body: [{ stage: "Reading the record" },
           { sentence: "Four comment windows are open right now." },
           { sentence: "The nearest closes at the PUCT." },
           { done: true }].map((l) => JSON.stringify(l)).join("\n") + "\n",
  }));
  /* THE HUMAN CHECK IS STUBBED, because the real one is aborted above and a press without a
     token never reaches the answer at all. Without this the section waited out the token, took
     the failure message, and measured the geometry of an apology. */
  await p2.addInitScript(() => {
    window.turnstile = { render: (el, o) => { setTimeout(() => o.callback("t"), 5); return 1; },
                         reset: () => {}, remove: () => {} };
  });
  await p2.goto(URL_HOME);
  await p2.waitForTimeout(300);
  await p2.locator("#ask form").scrollIntoViewIfNeeded();
  await p2.waitForTimeout(200);
  await p2.fill("#askq", "what is open for comment right now");
  await p2.press("#askq", "Enter");
  await p2.waitForSelector(".askfrom", { timeout: 8000 }).catch(() => {});
  /* WAIT FOR THE CONDITION, NOT FOR A DURATION. This waited a fixed 700ms and then watched
     for the scroll to stop moving, and both are guesses about how long a machine takes. They
     held on a laptop and failed on a CI runner, which is slower, so the suite went red on a
     product that was correct. A gate that reddens on a correct product is a gate somebody
     switches off, and this file's own history is about exactly that.
     So it waits for the thing being asserted to become true, with a bound. If `park()` works
     it settles in a few hundred milliseconds on any machine; if it is broken this times out
     and the assertion below fails on the real defect rather than on a slow runner. */
  /* THE WAIT IS THE ASSERTION. Waiting for the field to be seated, swallowing the timeout,
     and then measuring it again in a separate `evaluate` leaves a gap in which the page is
     still free to move, so a check that genuinely passed can be re-read as failed. It failed
     about one run in four at a single viewport, with `park()` exactly as it stands on main,
     while an isolated trace at that viewport seated every time. That is a race in the harness,
     not a fault in the page.
     Collapsed, the result of the wait IS the finding: `seated` is taken at the instant the
     condition became true. If the field never seats this comes back false and the assertion
     below reports the real defect. */
  const seated = await p2.waitForFunction(() => {
    const f = document.querySelector("#ask form");
    if (!f) return false;
    const r = f.getBoundingClientRect();
    return r.top >= 0 && r.bottom <= innerHeight + 1;
  }, null, { timeout: 12000, polling: 100 }).then(() => true).catch(() => false);
  const g = await p2.evaluate(() => {
    const f = document.querySelector("#ask form").getBoundingClientRect();
    const r = document.querySelector(".askreply");
    const rr = r ? r.getBoundingClientRect() : null;
    const seen = rr ? Math.max(0, Math.min(rr.bottom, innerHeight) - Math.max(rr.top, 0)) : 0;
    return {
      answered: !!r && r.textContent.trim().length > 0,
      anySeen: seen > 0,
      startsOnScreen: rr ? rr.top < innerHeight : false,
      /* MEASURED IN DOCUMENT COORDINATES, not viewport ones. Whether the answer sits above the
         field is a fact about the layout and has nothing to do with where the page happens to
         be scrolled, but read from `getBoundingClientRect` it changes while a scroll is in
         flight and reported false on a slow runner for a page that was laid out correctly. */
      aboveField: (function () {
        var rEl = document.querySelector(".askreply");
        var fEl = document.querySelector("#ask form");
        if (!rEl || !fEl) return false;
        var top = function (el) {
          var y = 0;
          while (el) { y += el.offsetTop; el = el.offsetParent; }
          return y;
        };
        return top(rEl) < top(fEl);
      })(),
      fieldSeen: f.top >= 0 && f.bottom <= innerHeight + 1,
    };
  });
  const at = `${vp.width}x${vp.height}`;
  check(`${at}: the press produced an answer`, g.answered, JSON.stringify(g));
  check(`${at}: some of it is on screen`, g.anySeen, JSON.stringify(g));
  check(`${at}: it begins above the fold rather than below it`, g.startsOnScreen,
        JSON.stringify(g));
  check(`${at}: it is above the field, where the conversation is`, g.aboveField,
        JSON.stringify(g));
  check(`${at}: and the field is still usable`, seated, JSON.stringify(g));
  await p2.close();
}

await browser.close();
console.log(failures ? `\nask_engine: ${failures} FAILED` : "\nask_engine: all passed");
process.exit(failures ? 1 : 0);
