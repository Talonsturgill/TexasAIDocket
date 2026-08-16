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

// THE NETWORK IS CUT AFTER LOAD. The page promises the reader that the BOX sends nothing
// anywhere; this is that promise, tested rather than asserted. Every request after the
// document itself fails, and the box must still answer every question.
//
// WHAT THIS ASSERTION IS ACTUALLY FOR, narrowed 2026-08-16 on the owner's call, in the run
// that first tripped it. The promise the reader is given is about the ASK LANE: typing a
// question sends nothing, so the box works on a phone with no signal in a county meeting
// room. It was never a promise that the page loads no pictures.
//
// It read as the wider promise only because it had never been tested against a page that
// carried one. `runs/carousel/` was empty until the first deck shipped, so the front page
// emitted no external reference at all and the assertion passed vacuously for its whole
// life. The first shipped carousel put its cover on the front page from the repository's
// own raw host and turned a green suite red overnight.
//
// So the media host is excluded BY NAME and nothing else is. An analytics beacon, a font
// CDN, a third-party script or any request the ask box itself makes still fails this, which
// is the whole of what the promise was protecting.
const MEDIA_HOST = "https://raw.githubusercontent.com/Talonsturgill/TexasAIDocket/";
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
await page.goto("file://" + path.join(SITE, "index.html"));
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

// THE TYPED PATH, not just the exposed function. This is what a reader actually does.
await page.fill("#askq", "What can I still comment on?");
await page.waitForFunction(() => {
  const a = document.querySelector("#ask .answer");
  return a && !a.hidden && a.textContent.trim().length > 0;
}, null, { timeout: 5000 }).catch(() => {});
const typed = (await page.textContent("#ask .answer")) || "";
check("typing a question renders an answer into the page", typed.trim().length > 0,
      JSON.stringify(typed.slice(0, 80)));

const openCount = idx.items.filter((i) => i.window === "open").length;
check("the open-window answer agrees with the index it shipped with",
      new RegExp(`\\b${openCount}\\b`).test(typed) ||
      /nothing is open/i.test(typed),
      `index says ${openCount} open; answer said: ${typed.slice(0, 120)}`);

// A starter chip must do what it says.
await page.click("#ask .chips button");
const chipped = (await page.textContent("#ask .answer")) || "";
check("a starter chip answers when clicked", chipped.trim().length > 0);

check("still no request left the page after every interaction", external.length === 0,
      external.join(", "));

// THE GATE CAN STILL GO RED, PROVED RATHER THAN ASSERTED. Narrowing an assertion is exactly
// where a suite quietly stops testing anything, so the exclusion is exercised against a host
// it does not cover. If this ever stops catching the beacon, the narrowing above has widened
// into "no request is ever checked" and the promise is gone with it.
const beacon = "https://analytics.example.com/collect?q=test";
await page.evaluate((u) => fetch(u).catch(() => {}), beacon);
await page.waitForTimeout(150);
check("...and a request to any other host is still caught",
      external.some((u) => u.startsWith("https://analytics.example.com/")),
      external.join(", ") || "nothing was caught, so the exclusion is too wide");

await browser.close();
console.log(failures ? `\nask_engine: ${failures} FAILED` : "\nask_engine: all passed");
process.exit(failures ? 1 : 0);
