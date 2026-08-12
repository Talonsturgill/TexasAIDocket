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

const browser = await chromium.launch({
  // The environment ships a chromium that may not match the npm package's pinned
  // build. Point at the installed one rather than downloading a second copy.
  executablePath: process.env.PLAYWRIGHT_CHROMIUM || "/opt/pw-browsers/chromium",
});
const page = await browser.newPage();

// THE NETWORK IS CUT AFTER LOAD. The page promises the reader that nothing is sent anywhere;
// this is that promise, tested rather than asserted. Every request after the document itself
// fails, and the box must still answer every question.
const external = [];
await page.route("**/*", (route) => {
  const url = route.request().url();
  if (url.startsWith("file://")) return route.continue();
  external.push(url);
  return route.abort();
});

await page.goto("file://" + path.join(SITE, "ask", "index.html"));
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
  for (const m of text.match(NUM) || []) {
    const n = Number(m.replace(/,/g, ""));
    // Claim totals and day counts legitimately exceed the item count; item counts cannot.
    if (/\bitems?\b/.test(text.slice(Math.max(0, text.indexOf(m) - 4), text.indexOf(m) + 24))
        && n > itemCount) {
      overclaimed.push(`${entry.q} -> ${m} (record holds ${itemCount})`);
    }
  }
}

check(`every catalogued question is answered (${cat.length} asked)`, empty.length === 0,
      empty.slice(0, 3).join(" | "));
check("no answer claims more items than the record holds", overclaimed.length === 0,
      overclaimed.slice(0, 3).join(" | "));

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

await browser.close();
console.log(failures ? `\nask_engine: ${failures} FAILED` : "\nask_engine: all passed");
process.exit(failures ? 1 : 0);
