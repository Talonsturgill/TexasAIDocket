// Every control gets a red case.
//
// The half that matters most is the set of sentences that must NOT trip a guard. A guard
// that blocks its own correct refusal teaches the model to answer instead of decline, which
// is the exact outcome the rule exists to prevent, and it fails silently: the answer looks
// fine, it just stopped saying "the record doesn't say".
//
// Run: node workers/ask/test.js

import {
  checkCitations, checkNumerals, checkSentence, checkVerdict, checkVoice,
  normalise, numerals, plainly, splitSentences,
} from "./checks.js";
import { rerank } from "./retrieve.js";

let fail = 0, pass = 0;
const ok = (label, cond, detail = "") => {
  if (cond) { pass++; return; }
  fail++;
  console.log(`  FAIL  ${label}${detail ? "  " + detail : ""}`);
};
const head = (t) => console.log("\n" + t);

// ---------------------------------------------------------------- numerals
head("A. numerals tokenise the way numeral_lint does");
ok("a thousands separator is inside the number, not a break in it",
  JSON.stringify(numerals("peak was 8,927 MW")) === JSON.stringify(["8927"]),
  JSON.stringify(numerals("peak was 8,927 MW")));
ok("a big one survives too",
  numerals("1,781,547.9 MWh")[0] === "1781547.9", numerals("1,781,547.9 MWh")[0]);
ok("a decimal survives", numerals("76.5 percent")[0] === "76.5");
ok("the zero in front of a decimal is kept",
  normalise("0.8469") === "0.8469", normalise("0.8469"));
ok("padding zeros still go", normalise("07") === "7");
ok("trailing zeros after a point still go", normalise("76.50") === "76.5");
ok("a padded date authorises the day a person writes",
  numerals("2026-07-09").includes("9"), JSON.stringify(numerals("2026-07-09")));

head("B. the numeral gate");
const allowed = new Set(["87648.5", "76.5", "58", "2026"]);
ok("an authorised figure passes",
  checkNumerals("Peak load reached 87648.5 MW.", allowed).ok);
ok("an invented figure is refused",
  !checkNumerals("Peak load reached 91234.6 MW.", allowed).ok);
ok("and the reason is named",
  checkNumerals("Peak load reached 91234.6 MW.", allowed).reason === "numeral");
ok("a citation's digits are not read as a figure",
  checkNumerals("See [[tx-2026-0001]] for the filing.", allowed).ok,
  JSON.stringify(checkNumerals("See [[tx-2026-0001]] for the filing.", allowed)));
ok("a model may write 8927 having been shown 8,927",
  checkNumerals("Peak was 8927 MW.", new Set(["8927"])).ok);

// ---------------------------------------------------------------- citations
head("C. the citation gate");
const slugs = new Set(["tx-2026-0001", "tx-2026-0002"]);
ok("a real decision passes", checkCitations("See [[tx-2026-0001]].", slugs).ok);
ok("an invented one is refused", !checkCitations("See [[tx-2026-9999]].", slugs).ok);
ok("and it says which",
  checkCitations("See [[tx-2026-9999]].", slugs).unknown[0] === "tx-2026-9999");
ok("prose with no citation passes", checkCitations("No filings are listed.", slugs).ok);

// ---------------------------------------------------------------- verdict
head("D. the verdict gate, which is the one that does not bend");
for (const s of [
  "The grid will hold through the summer.",
  "There is enough capacity to serve the forecast peak.",
  "ERCOT is safe this week.",
  "Expect rolling outages in August.",
  "There is no risk of a shortfall.",
  "Texans will be fine.",
  "A blackout is unlikely.",
  "The reservoirs will recover by spring.",
  "The rule will be approved.",
  "All clear on reserves.",
]) {
  ok(`refused: ${s}`, !checkVerdict(s).ok, JSON.stringify(checkVerdict(s)));
}

head("E. and it must NOT block its own correct refusal");
// The failure mode this half exists for. Each of these contains the words of the call it is
// declining to make, so a naive guard eats exactly the sentence the box should be writing.
for (const s of [
  "The record doesn't say whether there will be enough capacity.",
  "The record can't tell you whether the grid will hold.",
  "No one publishes a forecast of whether reserves are adequate.",
  "There is no public prediction of a shortfall.",
  "The docket doesn't state whether the rule will be approved.",
  "Per site large load metering is confidential, so the record doesn't answer that.",
  "Measured peak load was 87648.5 MW, and the record makes no call beyond that.",
]) {
  ok(`allowed: ${s}`, checkVerdict(s).ok, JSON.stringify(checkVerdict(s)));
}

// ---------------------------------------------------------------- voice
head("F. first person, banned in published copy");
for (const s of ["I think the filing is open.", "We track 58 decisions.",
                 "Let me pull that up.", "That is our record."]) {
  ok(`refused: ${s}`, !checkVoice(s).ok, JSON.stringify(checkVoice(s)));
}
head("G. and it must not fire inside an ordinary word");
// This record is mostly about the weather, so "we" inside a word is not hypothetical.
for (const s of [
  "The weather station recorded a maximum of 104 degrees.",
  "However, the comment window has closed.",
  "Power and the grid is the topic.",
  "The lower reservoir is at 44.77 percent.",
  "Owners were notified.",
  "Somewhere between the two filings.",
  // The three that a lazy apostrophe would have eaten.
  "The comment period was well attended.",
  "They wed the two dockets into one project.",
  "Filings were accepted through August 11th, 2026.",
  // And the country, which is not the first person plural.
  "The US Army Corps of Engineers is the decider.",
]) {
  ok(`allowed: ${s}`, checkVoice(s).ok, JSON.stringify(checkVoice(s)));
}
ok("a quoted source may say we",
  checkVoice('The filing says "we are aligned with the thought".').ok,
  JSON.stringify(checkVoice('The filing says "we are aligned with the thought".')));

// ---------------------------------------------------------------- punctuation
head("H. punctuation is repaired, never refused");
ok("a colon becomes a comma",
  plainly("The status is this: pending.") === "The status is this, pending.",
  plainly("The status is this: pending."));
ok("a clock time keeps its colon",
  plainly("The meeting is at 9:15 tomorrow.").includes("9:15"),
  plainly("The meeting is at 9:15 tomorrow."));
ok("a semicolon becomes a full stop and a capital",
  plainly("It filed; the window closed.") === "It filed. The window closed.",
  plainly("It filed; the window closed."));
ok("an em dash becomes a comma",
  !plainly("The rule — filed in July — is pending.").includes("—"));
ok("a dash between numbers stays a range, both numbers intact",
  plainly("The 2024–2025 window").includes("2024-2025"),
  plainly("The 2024–2025 window"));
ok("cannot becomes can't", plainly("The record cannot say.") === "The record can't say.",
  plainly("The record cannot say."));
ok("curly quotes are straightened", !plainly("the “filing”").includes("“"));
ok("throat clearing is dropped and the sentence keeps its capital",
  plainly("Great question! The window closed.") === "The window closed.",
  plainly("Great question! The window closed."));
ok("a sentence may not open with And",
  plainly("And the window closed.") === "The window closed.",
  plainly("And the window closed."));
ok("a sentence may not open with But",
  plainly("But the window closed.") === "The window closed.",
  plainly("But the window closed."));

head("I. nothing in the repair may touch a figure");
// The one rule that goes near digits is the range. Everything else must leave numbers alone,
// because this file's entire job is that a published figure is the one the record holds.
for (const s of ["Peak load reached 87,648.5 MW at hour ending 17.",
                 "Storage was 24,142,425 acre feet, 76.5 percent full.",
                 "The load factor was 0.8469."]) {
  const before = numerals(s).join(",");
  const after = numerals(plainly(s)).join(",");
  ok(`figures survive the repair: ${s.slice(0, 40)}`, before === after,
    `${before} -> ${after}`);
}

// ---------------------------------------------------------------- composite
head("J. the composite, in the order a failure should be reported");
const ctx = { allowed: new Set(["87648.5", "58", "2026", "1"]), slugs };
ok("a clean sentence passes",
  checkSentence("Peak load reached 87648.5 MW, per [[tx-2026-0001]].", ctx).ok,
  JSON.stringify(checkSentence("Peak load reached 87648.5 MW, per [[tx-2026-0001]].", ctx)));
ok("a bad citation is reported as citation, not as numeral",
  checkSentence("See [[tx-2026-9999]] for 87648.5 MW.", ctx).reason === "citation");
ok("a bad figure is reported as numeral",
  checkSentence("Peak load reached 99999.1 MW.", ctx).reason === "numeral");
ok("first person is reported as voice",
  checkSentence("We track 58 decisions.", ctx).reason === "voice");
ok("a verdict is reported as verdict",
  checkSentence("The grid will hold.", ctx).reason === "verdict");

head("K. streaming splits on sentences and holds the remainder");
const s1 = splitSentences("The window closed. Peak was 87648.5 MW. Want the");
ok("complete sentences come out", s1.sentences.length === 2, JSON.stringify(s1.sentences));
ok("the partial one is held back", s1.remainder === "Want the", JSON.stringify(s1.remainder));
ok("repair happens before the split, so what is checked is what is sent",
  splitSentences("It filed; the window closed. Next").sentences[0] === "It filed.",
  JSON.stringify(splitSentences("It filed; the window closed. Next")));

// ------------------------------------------------------- KV key namespacing
head("L. every KV key is namespaced to this site");
// The regression this pins actually happened. Two workers running the same design were
// pointed at one KV namespace, and the answer caches merged: the same question asked on both
// sites on the same day built the same key, so one site could serve the other's answer under
// its own name. A shared spend counter was the lesser half of it.
const { cacheKey, monthKey } = await import("./answer.js");
ok("the month key names the site",
  monthKey("2026-08-15T00:00:00Z") === "spend:tx:2026-08",
  monthKey("2026-08-15T00:00:00Z"));
const k = await cacheKey([{ role: "user", content: "what is open now" }], "2026-08-15");
ok("the answer key names the site", k.startsWith("a:tx:2026-08-15:"), k);
// THE KEY MOVES WHEN THE PROMPT MOVES, which a date could not do. The pack changed four times
// in one afternoon while the prompt was being fixed, and readers kept getting answers written
// against the version before, including a citation stutter that had been fixed twice by then.
// It looked like the fix had not worked. The answers were simply old.
const vA = await cacheKey([{ role: "user", content: "what is open now" }], "a63b2bff4953ccb1");
const vB = await cacheKey([{ role: "user", content: "what is open now" }], "ffffffffffffffff");
ok("the same question against a different pack version is a different key", vA !== vB);
ok("and the same question on a different day is a different key",
  k !== await cacheKey([{ role: "user", content: "what is open now" }], "2026-08-16"));
ok("spendOf still reports a bare month, not the prefixed key",
  (await (await import("./answer.js")).spendOf(
    { ASK_MONTHLY_CAP: "200", ASK_KV: { get: async () => "7" } },
    "2026-08-15T00:00:00Z")).month === "2026-08");

// ---------------------------------------------------------------- effort
head("M. how hard it is asked to think, and what happens to a typo");
const { effectiveEffort } = await import("./answer.js");
// MEDIUM, not low. Low could not find a county inside a twenty two county list in a decision
// it had been given, and answered "the record does not answer that" instead.
ok("medium by default, because finding a name in a list is work",
  effectiveEffort({}) === "medium", effectiveEffort({}));
ok("ASK_EFFORT moves it", effectiveEffort({ ASK_EFFORT: "high" }) === "high"
  && effectiveEffort({ ASK_EFFORT: "low" }) === "low");
ok("...and is read case and space insensitively, the way a dashboard field gets typed",
  effectiveEffort({ ASK_EFFORT: " MEDIUM " }) === "medium");
// A TYPO MUST NOT REACH THE API. `output_config.effort` is validated server side, so an
// unrecognised value is a 400 on every question: a mistyped dashboard field would take the ask
// box down rather than make it slower.
ok("a value the API would refuse falls back instead of shipping",
  effectiveEffort({ ASK_EFFORT: "maximum" }) === "medium");
ok("...and so does an empty one", effectiveEffort({ ASK_EFFORT: "" }) === "medium");
ok("...and a missing env object does not throw", effectiveEffort(undefined) === "medium");
// THE SHAPE THE API ACTUALLY WANTS. `effort` lives inside `output_config`, not at the top
// level, and nothing else here would notice if it were sent flat: the request would simply be
// refused, on every question, with the box looking broken rather than misconfigured.
const { modelParams } = await import("./answer.js");
const mp = modelParams({});
ok("effort is sent inside output_config, where the API reads it",
  mp.output_config?.effort === "medium", JSON.stringify(mp));
ok("...and not at the top level, where it would be ignored or refused",
  mp.effort === undefined, JSON.stringify(mp));
// Sonnet 5 returns 400 on all three of these. They have never been sent; this is the guard
// against somebody adding one back for a determinism that model does not offer.
ok("no sampling parameters ride along",
  ["temperature", "top_p", "top_k"].every((k) => !(k in mp)), JSON.stringify(mp));

// ---------------------------------------------------------------- usage
head("N. what a question cost, which nothing could report before");
const { emptyUsage, recordUsage, usageKey, usageOf } = await import("./answer.js");
ok("the usage key names the site, like every other key here",
  usageKey("2026-08-21T00:00:00Z") === "use:tx:2026-08", usageKey("2026-08-21T00:00:00Z"));

// A KV stub that actually stores, so accumulation is exercised rather than asserted.
const store = new Map();
const KV = { get: async (k) => store.get(k) ?? null, put: async (k, v) => { store.set(k, v); } };
await recordUsage({ ASK_KV: KV }, {
  input_tokens: 12, cache_read_input_tokens: 0, cache_creation_input_tokens: 47000,
  output_tokens: 300 }, 900, "2026-08-21T00:00:00Z");
await recordUsage({ ASK_KV: KV }, {
  input_tokens: 12, cache_read_input_tokens: 47000, cache_creation_input_tokens: 0,
  output_tokens: 200 }, 500, "2026-08-21T00:00:00Z");
const u = await usageOf({ ASK_KV: KV }, "2026-08-21T00:00:00Z");
ok("two questions accumulate rather than overwrite", u.calls === 2, JSON.stringify(u));
ok("...and the two cache counters are kept apart",
  u.cache_write === 47000 && u.cache_read === 47000, JSON.stringify(u));
// THE NUMBER THE TTL DECISION RESTS ON. One write and one read is a hit rate of a half, which
// is well over the ~0.22 where a five minute cache starts paying for itself.
ok("...so the hit rate is computed, not guessed", u.cache_hit_rate === 0.5,
  String(u.cache_hit_rate));
ok("time to first sentence is a mean over the calls that had one",
  u.mean_first_ms === 700, String(u.mean_first_ms));
// A month with nothing cached must not report a hit rate of zero, which reads as "never read"
// when it means "nothing has happened yet".
ok("no data reads as no data, not as a miss",
  (await usageOf({ ASK_KV: { get: async () => null, put: async () => {} } },
                 "2026-09-01T00:00:00Z")).cache_hit_rate === null);
ok("with no KV bound it says so rather than inventing zeroes",
  (await usageOf({}, "2026-08-21T00:00:00Z")).note === "no KV bound");
// A DIAGNOSTIC MUST NEVER FAIL AN ANSWER. If KV throws, the question still gets answered.
let threw = false;
try {
  await recordUsage({ ASK_KV: { get: async () => { throw new Error("kv down"); },
                                put: async () => {} } },
                    { input_tokens: 1 }, 10, "2026-08-21T00:00:00Z");
} catch { threw = true; }
ok("a broken counter cannot take the answer down with it", !threw);
ok("and an empty rollup is all zeroes rather than undefined",
  Object.values(emptyUsage()).every((v) => v === 0));

// ------------------------------------------- what the model was shown, and only that
head("O. retrieval may not weaken the promise it inherited");
const { allowedNumerals, systemBlocks } = await import("./answer.js");
const { splitPack, queryOf } = await import("./retrieve.js");

// A pack in miniature, with the shape ask_pack.py emits and asserts. Two things it has to be
// rather than merely look like.
//
// BIG ENOUGH THAT RETRIEVAL TURNS ITSELF ON. Below the size where a slice stops saving
// anything, assemble() correctly sends the whole record and this section would measure nothing.
//
// AND ENOUGH DECISIONS TO BE A CORPUS AT ALL. The retriever decides what counts as an
// informative word from the record's own document frequencies, so in a fixture of three
// documents a word in one of them appears in a third of everything and rightly scores as
// telling you very little. Three items measured the threshold rather than the retrieval.
const filler = (word) => (word + " ").repeat(700);
const SUBJECTS = [
  ["0001", "evaporative cooling", "8111", "alpha"],
  ["0002", "transmission recovery", "8222", "beta"],
  ["0003", "groundwater withdrawal", "8333", "gamma"],
  ["0004", "curtailment reporting", "8444", "delta"],
  ["0005", "interconnection queueing", "8555", "epsilon"],
  ["0006", "abatement agreements", "8666", "zeta"],
  ["0007", "biometric identifiers", "8777", "eta"],
  ["0008", "procurement disclosure", "8888", "theta"],
  ["0009", "reservoir accounting", "8999", "iota"],
  ["0010", "spectrum licensing", "9111", "kappa"],
  ["0011", "telemetry standards", "9222", "lambda"],
  ["0012", "weatherisation credits", "9333", "mu"],
];
const body = ([n, subject, mw, pad]) =>
  `[[tx-2026-${n}]] A decision about ${subject}\nThe topic is power and the grid. ` +
  `Its status is decided.\nThe ${subject} was measured at ${mw} MW. ${filler(pad)}`;
const FAKE = {
  generated: "2026-08-21",
  system: "INSTRUCTIONS. Answer from the record.",
  index: "THE INDEX.\n" + SUBJECTS.map(([n, subject]) =>
    `[[tx-2026-${n}]] ${subject}. decided.`).join("\n"),
  pack: `THE COUNTS. It tracks ${SUBJECTS.length} decisions.\n\nTHE DECISIONS.\n\n` +
        SUBJECTS.map(body).join("\n\n"),
};

// THE PROMISE ask_corpus.py MADE AND RETRIEVAL COULD HAVE QUIETLY BROKEN. The published
// authorised list covers every numeral in the WHOLE pack. While the whole pack was the prompt
// those were the same set. Reading the published list after retrieval would authorise figures
// out of decisions the model never saw, which is the confident nonsense the gate exists to
// stop, arriving through the gate itself.
const blocks = systemBlocks(FAKE, [{ role: "user", content: "evaporative cooling" }], {});
ok("a record this size is retrieved over rather than sent whole", blocks.length === 3,
  String(blocks.length));
const allow = allowedNumerals(blocks);
ok("the allow-list is read off the assembled prompt, not off the whole record",
  allow.has("8111") && !allow.has("8222") && !allow.has("8333"),
  JSON.stringify([...allow].sort()));
ok("...so a figure from a decision that was not sent is refused",
  !checkNumerals("The transmission recovery was measured at 8222 MW.", allow).ok);
ok("...and one from a decision that was sent passes",
  checkNumerals("The evaporative cooling was measured at 8111 MW.", allow).ok);
// The counts paragraph is in every prompt, so a count is always sayable. That is the point of
// putting it above the breakpoint rather than treating it as one more retrievable passage.
ok("the counts sit above the breakpoint, so a count is authorised on every question",
  allow.has("12") && blocks[1].text.includes("It tracks 12 decisions"));

// A SLUG IS NOT NARROWED THE SAME WAY, deliberately. Every decision has a line in the index
// whatever the retriever thought, so every id really was shown and naming one is honest.
ok("every decision stays citable, because every decision is indexed",
  SUBJECTS.every(([n]) => blocks.some((b) => b.text.includes(`[[tx-2026-${n}]]`))));
ok("...and the slice really is a slice, not the whole record under another name",
  blocks[2].text.includes("8111") && !blocks[2].text.includes("8333"));

head("P. the pack cuts back into its parts the way ask_pack.py promises");
const cut = splitPack(FAKE.pack);
ok("every block comes back out", cut.items.length === SUBJECTS.length,
  String(cut.items.length));
ok("the preamble stops at the mark", cut.preamble === "THE COUNTS. It tracks 12 decisions.",
  JSON.stringify(cut.preamble));
ok("each block keeps its id and its whole text",
  cut.items[0].id === "tx-2026-0001" && cut.items[0].text.includes("measured at 8111 MW"));
// A SHAPE CHANGE ON THE BUILDER'S SIDE MUST NOT PRODUCE A HALF EMPTY PROMPT. If the mark is
// gone the cut fails loudly by returning nothing, and assemble() falls back to the whole pack.
ok("a pack that lost its mark returns no items rather than guessing",
  splitPack("THE COUNTS. Nothing else.").items.length === 0);
ok("...and assemble sends everything when that happens",
  systemBlocks({ ...FAKE, pack: "no mark" },
               [{ role: "user", content: "x" }], {}).length === 2);

head("P2. the block headers keep the house voice, because the model writes what it reads");
// ask_pack.py bans colons, semicolons and dashes in the record and gates it in a self-test,
// for the stated reason that a pack full of colons produces answers full of colons and the
// checker then refuses the model's own reply. These two strings are the LAST thing in the
// prompt and no Python gate can reach them, so the same rules are enforced here.
for (const [name, copy] of [["the slice header", blocks[2].text.split("\n\n")[0]],
                            ["the empty slice header",
                             systemBlocks(FAKE, [{ role: "user", content: "zzzz qqqq" }], {})[2]
                               .text]]) {
  ok(`${name} carries no colon or semicolon`, !/[:;]/.test(copy), copy.slice(0, 60));
  ok(`${name} carries no em or en dash`, !/[\u2013\u2014]/.test(copy));
  ok(`${name} keeps its commas sparse, like the record it introduces`,
    (copy.match(/,/g) || []).length / (copy.split(/\s+/).length / 100) < 6.2,
    String(((copy.match(/,/g) || []).length /
            (copy.split(/\s+/).length / 100)).toFixed(1)));
  ok(`${name} does not speak in the first person`, !/\b(?:I|we|our|us)\b/.test(copy));
}

head("Q. a follow-up is read next to the turn it follows");
ok("the earlier user turn is part of the question",
  queryOf([{ role: "user", content: "the Oncor line" },
           { role: "assistant", content: "..." },
           { role: "user", content: "and the dates" }]).includes("Oncor"));
ok("...and the answerer's own words never are",
  !queryOf([{ role: "user", content: "a" },
            { role: "assistant", content: "ZZZ" }]).includes("ZZZ"));

head("R. end to end, because the wiring is what the unit tests cannot see");
// EVERYTHING ABOVE TESTS A FUNCTION. This tests the REQUEST, which is the only thing the API
// ever sees, and it is where a correct assembler and a correct guard get joined up wrongly.
// Nothing else here would notice systemBlocks being built and then the old whole-pack field
// being sent, or the guard being handed the published allow-list instead of the narrowed one.
const { answer: answerWhole } = await import("./answer.js");
const FAKE_CORPUS = {
  slugs: SUBJECTS.map(([n]) => `tx-2026-${n}`),
  // Deliberately the WHOLE record's numerals, which is what the published file carries. If the
  // worker reads this instead of the assembled prompt, the next assertion goes green wrongly
  // and a figure out of an unsent decision reaches a reader.
  authorised_numerals: ["3", "12", "8111", "8222", "8333", "8444", "8555", "8666",
                        "8777", "8888", "8999", "9111", "9222", "9333"],
};
let sentBody = null;
const realFetch = globalThis.fetch;
globalThis.fetch = async (url, init) => {
  const u = String(url);
  if (u.endsWith("/pack.json")) return { ok: true, json: async () => FAKE };
  if (u.endsWith("/corpus.json")) return { ok: true, json: async () => FAKE_CORPUS };
  sentBody = JSON.parse(init.body);
  return { ok: true, json: async () => ({
    // One true sentence about what was retrieved, then one about a decision that was not.
    content: [{ type: "text", text: "The evaporative cooling was measured at 8111 MW. " +
                                     "The groundwater withdrawal was measured at 8333 MW." }],
    usage: { input_tokens: 10, output_tokens: 20 },
  }) };
};
const ENV = { ANTHROPIC_API_KEY: "test", ASK_PACK_URL: "https://x/pack.json",
              ASK_CORPUS_URL: "https://x/corpus.json" };
const out = await answerWhole([{ role: "user", content: "evaporative cooling" }], ENV,
                              "2026-08-21T00:00:00Z");
globalThis.fetch = realFetch;

ok("the request carries three system blocks", sentBody?.system?.length === 3,
  JSON.stringify(sentBody?.system?.length));
ok("...with exactly one cache breakpoint, on the block that repeats",
  sentBody.system.filter((b) => b.cache_control).length === 1 && !!sentBody.system[1].cache_control);
ok("...and it is not the whole record under another name",
  sentBody.system.map((b) => b.text).join("").length < FAKE.pack.length / 2,
  `${sentBody.system.map((b) => b.text).join("").length} against ${FAKE.pack.length}`);
ok("the sentence about what was retrieved is kept",
  out.body.text.includes("8111"), JSON.stringify(out.body));
// THE ASSERTION THIS WHOLE SECTION EXISTS FOR. 8333 is in the published allow-list and is NOT
// in the prompt. If the worker reads the published file, this sentence is published.
ok("the sentence about a decision that was not sent is withheld",
  out.body.withheld === true && out.body.reason === "numeral", JSON.stringify(out.body));
ok("...and the answer stops there rather than being quietly repaired",
  !out.body.text.includes("8333"), JSON.stringify(out.body.text));

head("R2. the counters land where /_config looks, called the way the worker calls it");
// THE BUG THIS PINS SHIPPED AND RAN FOR NINE QUESTIONS. worker.js calls answerStream(turns,
// env) with no third argument, and usageKey had no fallback for that, so every real request
// wrote to `use:tx:undefin` while /_config read `use:tx:2026-08` and truthfully said zero.
//
// The old test called recordUsage with an explicit timestamp. It exercised the function and
// never the CALL SITE, which is the only place the argument was missing. So this one omits
// `now` exactly as the worker does, and reads the counter back through usageOf the way
// /_config does, with no shared timestamp to paper over a mismatch.
const liveStore = new Map();
const LIVE_KV = { get: async (k) => liveStore.get(k) ?? null,
                  put: async (k, v) => { liveStore.set(k, v); } };
{
  const realFetch2 = globalThis.fetch;
  globalThis.fetch = async (url, init) => {
    const u = String(url);
    if (u.endsWith("/pack.json")) return { ok: true, json: async () => FAKE };
    if (u.endsWith("/corpus.json")) return { ok: true, json: async () => FAKE_CORPUS };
    return { ok: true, json: async () => ({
      content: [{ type: "text", text: "The record holds 12 decisions." }],
      usage: { input_tokens: 900, cache_read_input_tokens: 400,
               cache_creation_input_tokens: 0, output_tokens: 30 },
    }) };
  };
  // No third argument. This is the line worker.js runs.
  await answerWhole([{ role: "user", content: "evaporative cooling" }],
                    { ...ENV, ASK_KV: LIVE_KV });
  globalThis.fetch = realFetch2;
}
const liveUsage = await usageOf({ ASK_KV: LIVE_KV }, new Date().toISOString());
ok("a request with no pinned clock still counts",
  liveUsage.calls === 1, JSON.stringify(liveUsage));
ok("...and its tokens are readable, not stranded under another key",
  liveUsage.input === 900 && liveUsage.cache_read === 400, JSON.stringify(liveUsage));
ok("...and no key anywhere is built on an undefined",
  ![...liveStore.keys()].some((k) => k.includes("undefin")),
  [...liveStore.keys()].join(", "));

head("T. the reranker, which may reorder and may never invent");
{
  const cands = [
    { id: "tx-2026-0001", head: "a", text: "alpha" },
    { id: "tx-2026-0002", head: "b", text: "beta" },
    { id: "county-dallas", head: "c", text: "gamma" },
  ];
  // NO BINDING IS THE NORMAL CASE ON A FRESH PASTE. This worker is deployed by pasting one
  // file into a dashboard and the AI binding is added there separately, so the first deploy of
  // this change will not have one. It has to answer anyway.
  ok("no AI binding reorders nothing and throws nothing",
    (await rerank("q", cands, {})) === null);
  ok("neither does a single candidate, which has no order to change",
    (await rerank("q", cands.slice(0, 1), { AI: { run: async () => [{ id: 0 }] } })) === null);
  ok("a model that throws leaves retrieval standing",
    (await rerank("q", cands, { AI: { run: async () => { throw new Error("503"); } } })) === null);
  ok("so does a response shape this does not recognise",
    (await rerank("q", cands, { AI: { run: async () => ({ nope: true }) } })) === null);

  const fake = (rows) => ({ AI: { run: async () => ({ response: rows }) } });
  ok("a full ranking is applied in the order the reranker gave",
    JSON.stringify(await rerank("q", cands, fake([{ id: 2 }, { id: 0 }, { id: 1 }])))
    === JSON.stringify(["county-dallas", "tx-2026-0001", "tx-2026-0002"]));
  // A PARTIAL ANSWER DEGRADES INTO THE RETRIEVAL ORDER, never into a shorter list. Dropping
  // what the reranker did not mention would let a truncated response silently shrink the slice.
  ok("what it did not rank keeps its old place at the back",
    JSON.stringify(await rerank("q", cands, fake([{ id: 2 }])))
    === JSON.stringify(["county-dallas", "tx-2026-0001", "tx-2026-0002"]));
  ok("an out of range index is discarded rather than crashing",
    JSON.stringify(await rerank("q", cands, fake([{ id: 99 }, { id: 1 }])))
    === JSON.stringify(["tx-2026-0002", "tx-2026-0001", "county-dallas"]));
}

head("S. the file that actually gets deployed is the one the tests ran against");
// bundled.js is pasted into a dashboard by hand. Nothing else compares it to the modules, so a
// stale one would ship the previous design with every assertion above passing.
const { execFileSync } = await import("node:child_process");
let bundleFresh = true, bundleWhy = "";
try {
  execFileSync("node", ["workers/ask/bundle.mjs", "--check"], { stdio: "pipe" });
} catch (e) {
  bundleFresh = false;
  bundleWhy = String(e.stderr || e.message).trim();
}
ok("bundled.js is what the five modules produce", bundleFresh, bundleWhy);

console.log("");
console.log(fail === 0 ? `checks clean, ${pass} assertions`
                       : `checks FAILED, ${fail} of ${pass + fail}`);
process.exit(fail ? 1 : 0);
