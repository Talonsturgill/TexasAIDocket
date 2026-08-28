// Does the worker put the right decision in front of the model?
//
// WHAT THIS MEASURES, AND WHY IT IS A DIFFERENT QUESTION FROM tests/ask_eval.mjs. That file
// scores the BROWSER lane, which routes a reader to an answer the page computes locally. This
// one scores the WORKER lane, which chooses which decision bodies go in the prompt. Both use
// the same retriever and they are asked different things, so a change that helps one can hurt
// the other and nothing but two numbers would show it.
//
// IT COSTS NOTHING AND NEEDS NO BROWSER. No model call, no page, no Playwright. The retriever
// is pure code and the pack is built from the record by the same script the site publishes.
//
// THE MEASUREMENT THAT MATTERS IS RECALL, NOT PRECISION. Sending a body that turns out to be
// irrelevant costs tokens. Failing to send the right one costs an answer. And the index means
// a miss degrades to "the record carries one about that" rather than to a confident invention,
// which is the whole reason retrieval was allowed in here at all.
//
//     node tests/ask_worker_retrieval.mjs
//     node tests/ask_worker_retrieval.mjs --against tests/fixtures/ask_worker_baseline.json
//     node tests/ask_worker_retrieval.mjs --baseline tests/fixtures/ask_worker_baseline.json

import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { assemble, familyOf, pickItems, splitPack, queryOf, wantsBreadth, pinnedIds, strangeness }
  from "../workers/ask/retrieve.js";
import { askIndex } from "../workers/ask/retriever.js";

const argv = process.argv.slice(2);
const flag = (n) => { const i = argv.indexOf(n); return i < 0 ? null : argv[i + 1]; };
const PYTHON = process.env.TEXAS_AI_DOCKET_PYTHON
  || (process.platform === "win32" ? "python" : "python3");

let fail = 0, pass = 0;
const ok = (label, cond, detail = "") => {
  if (cond) { pass++; return; }
  fail++;
  console.log(`  FAIL  ${label}${detail ? "  " + detail : ""}`);
};
const head = (t) => console.log("\n" + t);

// Built now from the record, never read from a file somebody last touched months ago. Same
// reason ask_eval.mjs shells out for its cases: one implementation of what the pack is.
const PACK = JSON.parse(execFileSync(PYTHON,
  ["-c", "import sys,json; sys.path.insert(0,'scripts/site'); import ask_pack; " +
         "p=ask_pack.build(); json.dump(p, sys.stdout)"],
  { encoding: "utf-8", maxBuffer: 64 << 20 }));
const GOLD = JSON.parse(execFileSync(PYTHON, ["scripts/site/ask_eval.py"],
  { encoding: "utf-8", maxBuffer: 32 << 20 }));
const LEDGER = JSON.parse(fs.readFileSync("ledger/docket.json", "utf-8"));
const ITEMS_RAW = Array.isArray(LEDGER) ? LEDGER : LEDGER.items;
const byId = new Map(ITEMS_RAW.map((it) => [it.id, it]));

// ---------------------------------------------------------------- the split contract
head("A. the pack cuts back into its parts, which is the whole of the plumbing");
const { preamble, items } = splitPack(PACK.pack);
// THE PACK IS FOUR FAMILIES NOW AND THIS SECTION ASSERTED IT WAS ONE. `PACK.items` still
// counts decisions, because a live worker reads it and a field vanishing under one is the
// failure this repo is most careful about, so the count of everything is `PACK.blocks`.
ok("every block comes back out of the cut",
  items.length === PACK.blocks, `${items.length} of ${PACK.blocks}`);
ok("the ids survive the cut intact",
  items.every((it) => /^[a-z0-9-]+$/.test(it.id)),
  JSON.stringify(items.filter((it) => !/^[a-z0-9-]+$/.test(it.id)).slice(0, 2)));
ok("the decisions come out first, in the record's own order",
  JSON.stringify(items.slice(0, ITEMS_RAW.length).map((i) => i.id))
  === JSON.stringify(ITEMS_RAW.map((i) => i.id)));
// THE FAMILIES THE BUILDER DECLARED ARE THE FAMILIES THE CUT PRODUCES, which is the assertion
// that catches a family silently losing its blocks. familyOf is the worker's own, so the two
// sides cannot drift into disagreeing about what a family is.
const cut = {};
for (const it of items) cut[familyOf(it.id)] = (cut[familyOf(it.id)] || 0) + 1;
ok("and every family the builder declared is present in the count it declared",
  JSON.stringify(cut) === JSON.stringify(
    Object.fromEntries(Object.entries(PACK.families).filter(([, n]) => n))),
  `${JSON.stringify(cut)} against ${JSON.stringify(PACK.families)}`);
// A RESERVOIR BLOCK IS 175 CHARACTERS AND A DECISION IS 2,708, so one floor across both is
// either useless or wrong. What this is really guarding is a block arriving empty, which is
// what a builder emitting a header and no body looks like.
ok("no block loses its text", items.every((it) => it.chars > 120),
  JSON.stringify(items.filter((it) => it.chars <= 120).slice(0, 2)));
ok("the preamble stops before the first decision",
  preamble.includes("THE COUNTS")
  && !preamble.split("\n").some((l) => l.startsWith("[[")),
  preamble.split("\n").filter((l) => l.startsWith("[["))[0] || preamble.slice(-60));
ok("nothing is dropped between the preamble and the blocks",
  preamble.length + items.reduce((n, i) => n + i.chars, 0) > PACK.chars * 0.97);
// A PACK THAT LOST ITS SHAPE MUST NOT CUT INTO A HALF EMPTY PROMPT. It has to look unsplit, so
// assemble() falls back to sending everything rather than sending a fragment of it.
ok("a pack without the mark refuses to split rather than guessing",
  splitPack("no mark here at all").items.length === 0);

// ---------------------------------------------------------------- the index is complete
head("B. the model always knows what exists, whatever the retriever thinks");
ok("every decision has a line in the index",
  ITEMS_RAW.every((it) => PACK.index.includes(`[[${it.id}]]`)),
  JSON.stringify(ITEMS_RAW.filter((it) => !PACK.index.includes(`[[${it.id}]]`))
    .map((i) => i.id).slice(0, 3)));
const nonsenseAsm = assemble(PACK, [{ role: "user", content: "sourdough starter recipe" }], {});
ok("...even when nothing at all is retrieved",
  ITEMS_RAW.every((it) => nonsenseAsm.blocks.some((b) => b.text.includes(`[[${it.id}]]`))));
ok("and a question matching nothing sends no bodies rather than three random ones",
  nonsenseAsm.mode === "index only", nonsenseAsm.mode);

// ---------------------------------------------------------------- the prompt's shape
head("C. three blocks, one breakpoint, and it is in the only place it can be");
const asm = assemble(PACK, [{ role: "user", content: "what is open for comment" }], {});
ok("three blocks", asm.blocks.length === 3, String(asm.blocks.length));
ok("the instructions come first", asm.blocks[0].text === PACK.system);
ok("exactly one cache breakpoint",
  asm.blocks.filter((b) => b.cache_control).length === 1);
// CACHING IS A BYTE EXACT PREFIX MATCH. A breakpoint after the slice would be a cache write on
// every question and a read on almost none, which is the 25 percent surcharge dressed as an
// optimisation that the usage counters were added to detect.
ok("...and it sits on the last block that is the same for every question",
  !!asm.blocks[1].cache_control && !asm.blocks[2].cache_control);
ok("the cached prefix clears the 1024 token minimum a cache entry needs",
  (asm.blocks[0].text.length + asm.blocks[1].text.length) / 4 > 1024,
  String(Math.round((asm.blocks[0].text.length + asm.blocks[1].text.length) / 4)));
ok("the slice names itself as a slice, so the model does not read it as the whole record",
  asm.blocks[2].text.startsWith("WHAT IS MOST LIKELY TO ANSWER THIS QUESTION"));
// TWO QUESTIONS, ONE CACHE ENTRY. If the stable blocks differed by a byte between questions
// nothing above the breakpoint would ever be read back.
const asm2 = assemble(PACK, [{ role: "user", content: "who decides transmission lines" }], {});
ok("two different questions share the cached prefix byte for byte",
  asm.blocks[0].text === asm2.blocks[0].text && asm.blocks[1].text === asm2.blocks[1].text);
ok("...and differ in the block after it", asm.blocks[2].text !== asm2.blocks[2].text);

// ---------------------------------------------------------------- the escape hatches
head("D. the ways it goes back to sending everything");
const off = assemble(PACK, [{ role: "user", content: "anything" }], { ASK_RETRIEVAL: "off" });
ok("ASK_RETRIEVAL=off sends the whole pack, one dashboard variable and no deploy",
  off.mode === "whole (off)" && off.blocks.length === 2, off.mode);
ok("...and it is the whole pack, not a large slice of it",
  off.blocks[1].text === PACK.pack);
// A WORKER DEPLOYED AHEAD OF A SITE REBUILD reads yesterday's pack, which has no index. A
// slice with nothing standing in for the rest is the one shape this design must never take.
const noIndex = assemble({ ...PACK, index: "" }, [{ role: "user", content: "water" }], {});
ok("a pack with no index sends everything rather than a slice with no safety net",
  noIndex.mode === "whole (no index)", noIndex.mode);
const cutAt = PACK.pack.indexOf("\n\n[[", PACK.pack.indexOf("\n\nTHE DECISIONS.\n\n") + 20);
const tiny = { ...PACK, pack: PACK.pack.slice(0, cutAt) };
ok("a record small enough not to need retrieving is not retrieved",
  assemble(tiny, [{ role: "user", content: "water" }], {}).mode === "whole (fits)",
  assemble(tiny, [{ role: "user", content: "water" }], {}).mode);

// A RECORD IN THE GAP BETWEEN THE TWO THRESHOLDS. The size where sending everything gets
// cheaper is not the size where retrieval starts being worth doing, and between them a breadth
// question asking for fourteen bodies plus the whole index adds up to more than the record it
// is a slice of. Comparing the two assembled sizes closes that without anybody keeping two
// numbers in step.
const gapPack = { ...PACK,
  pack: PACK.pack.slice(0, PACK.pack.indexOf("\n\n[[", PACK.chars / 3)) };
const gap = assemble(gapPack, [{ role: "user", content: "how many decisions involve water" }], {});
ok("a slice that would not be smaller than the whole record is not sent",
  gap.chars <= gapPack.system.length + gapPack.pack.length,
  `${gap.mode}, ${gap.chars} against ${gapPack.system.length + gapPack.pack.length}`);

// ---------------------------------------------------------------- reading the question
head("E. what counts as the question");
ok("a follow-up carries the turn it is a follow-up to",
  queryOf([{ role: "user", content: "the Oncor line" },
           { role: "assistant", content: "..." },
           { role: "user", content: "what about the dates" }]).includes("Oncor"));
ok("...and the assistant's own words are not part of the question",
  !queryOf([{ role: "user", content: "a" }, { role: "assistant", content: "ZZZZ" }])
    .includes("ZZZZ"));
ok("a long conversation stops dragging its opening subject through every later answer",
  !queryOf([{ role: "user", content: "OPENER" }, { role: "user", content: "b" },
            { role: "user", content: "c" }, { role: "user", content: "d" }])
    .includes("OPENER"));
ok("an id typed out is honoured exactly, with no scorer getting a vote",
  pinnedIds("tell me about tx-2026-0043", new Set(["tx-2026-0043"]))[0] === "tx-2026-0043");
ok("...and an id the record does not hold is not pinned",
  pinnedIds("tx-2026-9999", new Set(["tx-2026-0043"])).length === 0);
ok("a survey question is recognised as wanting breadth",
  wantsBreadth("how many decisions involve water") && wantsBreadth("list every data center"));
ok("...and a question about one decision is not",
  !wantsBreadth("what did the groundwater district decide"));

// ------------------------------------------------ context that helps, and context that does not
head("E3. an earlier turn may add to a question and may not take it over");
const ids = (turns) => assemble(PACK, turns, {}).chosen;
const county = ITEMS_RAW.find((it) => ((it.geography || {}).counties || []).length)
  .geography.counties[0];
const inCounty = ITEMS_RAW.filter((it) => ((it.geography || {}).counties || []).includes(county))
  .map((it) => it.id);
// A REAL CONVERSATION THAT BROKE. The record carries the county and not the company, so the
// joined query carries a word pointing off the record and the second question, which is
// perfectly answerable on its own, got nothing. An earlier turn can only ADD words, so a
// joined query finding nothing where the latest turn alone finds something is context getting
// in the way rather than helping.
const poisoned = ids([{ role: "user", content: "anything about NVIDIA" },
                      { role: "assistant", content: "..." },
                      { role: "user", content: `${county} county` }]);
ok("a follow-up survives an earlier turn the record has never heard of",
  poisoned.some((id) => inCounty.includes(id)), `${county}: ${poisoned.join(" ")}`);
ok("...and the same question alone finds the same thing",
  ids([{ role: "user", content: `${county} county` }]).some((id) => inCounty.includes(id)));
// AND THE FALLBACK MUST NOT UNDO WHAT CONTEXT IS FOR. It only fires when the joined query
// found nothing at all, so a follow-up that works because of its earlier turn still does.
const followed = ids([{ role: "user", content: "the Oncor 765 kV transmission line" },
                      { role: "assistant", content: "..." },
                      { role: "user", content: "and the dates" }]);
ok("a follow-up that only makes sense next to its earlier turn still does",
  followed.length > 0 && followed.some((id) =>
    (byId.get(id)?.title || "").toLowerCase().includes("oncor")), followed.join(" "));

// ------------------------------------------------ words the record has never used
head("E2. a word the record has never heard is evidence, and every scorer threw it away");
// BM25 cannot use it. A term in no document contributes nothing to any score, so "marathon"
// and "sourdough" are silently dropped and whatever else was in the sentence decides. This is
// the mirror of the bug wave 2 found, where an UNSEEN word scored as the most distinctive word
// there is. Same mistake read the other way round, opposite correction.
const bodyIdx = askIndex(items.map((it) => ({ id: it.id, summary: it.text })));
const str = (q) => strangeness(q, bodyIdx);
ok("a question built out of the record is not strange at all",
  str("groundwater withdrawal permit evaporative cooling").unknown === 0,
  JSON.stringify(str("groundwater withdrawal permit evaporative cooling")));
// THE RECORD SAYS "withdrawals" AND A READER TYPES "withdrawal". There is no stemmer here, so
// without a near form check that is a word nothing has ever used, and in a two word question
// it is half the evidence against answering at all.
ok("...and neither is one that differs from the record by an s",
  str("withdrawal permits").unknown === 0, JSON.stringify(str("withdrawal permits")));
// AND ONE WORD IS ENOUGH TO COUNT. Three quarters of "best way to train for a marathon" is
// familiar to this record, because "best" is in one decision, "way" is in five and "trains" is
// in one, all by accident. Only "marathon" is telling the truth about what the question is
// about, which is why this is not weighed by count. A ratio was tried and let the coincidences
// outvote the one word that meant anything.
ok("a question about something else carries a word that says so",
  str("best way to train for a marathon").unknown === 1,
  JSON.stringify(str("best way to train for a marathon")));
ok("...and one about nothing at all is entirely unknown",
  str("sourdough starter overnight proofing").ratio === 1,
  JSON.stringify(str("sourdough starter overnight proofing")));
// THE FRAME IS NEITHER EVIDENCE FOR NOR AGAINST. Counting "how" and "the" as unknown would make
// every real question look strange, and counting them as known would make every fake one look
// familiar. They are not counted at all.
ok("the grammar of a question is neither evidence for nor against it",
  str("what is the and with for").known === 0 && str("what is the and with for").unknown === 0,
  JSON.stringify(str("what is the and with for")));

// ---------------------------------------------------------------- recall, measured
head("T2. an order may reorder the slice and may not add to it");
{
  const q = [{ role: "user", content: "what is open for comment" }];
  const plain = assemble(PACK, q, {});
  // THE ORDER IS FILTERED AGAINST WHAT RETRIEVAL CHOSE. A reranker returning an id from
  // somewhere else, or a stale one from another question, must not be able to put a block in
  // front of the model that this question's retrieval never selected.
  const smuggled = assemble(PACK, q, {}, ["tx-2026-0044", ...plain.chosen]);
  ok("an id retrieval did not choose cannot enter the prompt through the order",
    !smuggled.chosen.includes("tx-2026-0044") || plain.chosen.includes("tx-2026-0044"),
    JSON.stringify(smuggled.chosen.slice(0, 3)));
  ok("an empty order leaves the retrieval order exactly as it was",
    JSON.stringify(assemble(PACK, q, {}, []).chosen) === JSON.stringify(plain.chosen));
  ok("and a nonsense order does too, rather than emptying the slice",
    JSON.stringify(assemble(PACK, q, {}, ["not-an-id"]).chosen)
    === JSON.stringify(plain.chosen));
}

head("F. recall against the gold set, which is the number this file exists for");
const kinds = {};
const record = (kind, hit, first) => {
  const k = kinds[kind] || (kinds[kind] = { n: 0, hit: 0, first: 0 });
  k.n++; if (hit) k.hit++; if (first) k.first++;
};

// A case naming ONE decision is scored on whether that decision's body was sent. A case naming
// a county, a decider or a topic is scored on whether ANY decision carrying it was sent, which
// is what those questions are actually asking for.
const matches = (c, id) => {
  // A CASE NAMING A BLOCK OUTSIDE THE DOCKET IS SCORED ON THE ID AND NOTHING ELSE, and until
  // this line existed every such case scored zero. `byId` is built from ledger/docket.json, so
  // the lookup below returned undefined for every dossier, county and reservoir and the
  // function said false. The families were in the pack, in the index and in the slice, and the
  // harness reported on none of them while printing a number that read like coverage.
  if (c.item && !/^tx-\d{4}-\d{4}$/.test(c.item)) return c.item === id;
  const it = byId.get(id);
  if (!it) return false;
  if (c.item) return c.item === id;
  if (c.view === "by_county") {
    return ((it.geography || {}).counties || []).includes(c.arg);
  }
  if (c.view === "by_decider") return (it.decider || {}).name === c.arg;
  if (c.view === "by_topic") return it.topic === c.arg;
  return false;
};

let sliceChars = 0, cases = 0, nonsenseAnswered = [];
for (const c of GOLD.cases) {
  const a = assemble(PACK, [{ role: "user", content: c.q }], {});
  sliceChars += a.blocks[a.blocks.length - 1].text.length;
  cases++;
  if (c.expect_none) {
    const clean = a.mode === "index only";
    record("nonsense", clean, clean);
    if (!clean) nonsenseAnswered.push(`${c.q} -> ${a.chosen.join(" ")}`);
    continue;
  }
  const hit = a.chosen.some((id) => matches(c, id));
  record(c.kind, hit, a.chosen.length ? matches(c, a.chosen[0]) : false);
}

const rows = Object.entries(kinds).sort();
const tot = rows.reduce((t, [, k]) => ({ n: t.n + k.n, hit: t.hit + k.hit,
                                         first: t.first + k.first }), { n: 0, hit: 0, first: 0 });
const pct = (a, b) => b ? +(100 * a / b).toFixed(1) : 0;
const now = { by_kind: {}, total: { n: tot.n, sent: pct(tot.hit, tot.n),
                                    first: pct(tot.first, tot.n) } };
console.log("");
console.log("  kind          n     sent    first");
for (const [kind, k] of rows) {
  now.by_kind[kind] = { n: k.n, sent: pct(k.hit, k.n), first: pct(k.first, k.n) };
  console.log(`  ${kind.padEnd(12)} ${String(k.n).padStart(3)}   ` +
              `${String(pct(k.hit, k.n)).padStart(5)}%  ${String(pct(k.first, k.n)).padStart(5)}%`);
}
console.log(`  ${"OVERALL".padEnd(12)} ${String(tot.n).padStart(3)}   ` +
            `${String(now.total.sent).padStart(5)}%  ${String(now.total.first).padStart(5)}%`);

// ---------------------------------------------------------------- what it costs
head("G. the token bill, which is why any of this was built");
const whole = PACK.system.length + PACK.pack.length;
const meanSlice = Math.round(sliceChars / cases);
const meanTotal = PACK.system.length + preamble.length + PACK.index.length + meanSlice;
now.tokens = { whole: Math.round(whole / 4), mean: Math.round(meanTotal / 4),
               cached: Math.round((PACK.system.length + preamble.length +
                                   PACK.index.length) / 4) };
console.log(`  the whole pack        ${String(now.tokens.whole).padStart(6)} tokens`);
console.log(`  a mean question       ${String(now.tokens.mean).padStart(6)} tokens   ` +
            `${(whole / meanTotal).toFixed(1)}x smaller`);
console.log(`  of which cacheable    ${String(now.tokens.cached).padStart(6)} tokens   ` +
            `${pct(now.tokens.cached, now.tokens.mean)}% of it`);
ok("a mean question is a fraction of the whole record",
  meanTotal < whole / 3, `${Math.round(meanTotal / 4)} against ${Math.round(whole / 4)}`);
ok("and most of what remains is the part that caches",
  now.tokens.cached > now.tokens.mean / 2);

// ---------------------------------------------------------------- the one hard failure
head("H. the regression that is not allowed");
// EVERYTHING ELSE HERE PRINTS AND LEAVES THE JUDGEMENT TO A PERSON, for the reason set out in
// ask_eval.mjs: a measurement that fails a build is a measurement people learn to route around.
// This one fails. A question sharing nothing with the record must not drag bodies into the
// prompt, because those bodies are what a model reaches for when it decides to be helpful.
ok("a question sharing nothing with the record sends no decision at all",
  nonsenseAnswered.length === 0, nonsenseAnswered.slice(0, 2).join(" | "));

// ---------------------------------------------------------------- baselines
const against = flag("--against");
if (against && fs.existsSync(against)) {
  const was = JSON.parse(fs.readFileSync(against, "utf-8"));
  head("I. against the recorded baseline");
  const move = (label, a, b) => {
    const d = +(a - b).toFixed(1);
    console.log(`  ${label.padEnd(22)} ${String(b).padStart(6)} -> ${String(a).padStart(6)}` +
                `  ${d === 0 ? "same" : (d > 0 ? "+" : "") + d}`);
  };
  move("sent", now.total.sent, was.total.sent);
  move("first", now.total.first, was.total.first);
  move("mean tokens", now.tokens.mean, was.tokens.mean);
}
const baseline = flag("--baseline");
if (baseline) {
  fs.mkdirSync(path.dirname(baseline), { recursive: true });
  fs.writeFileSync(baseline, JSON.stringify(now, null, 1) + "\n");
  console.log(`\n  baseline written to ${baseline}`);
}

console.log("");
console.log(fail === 0 ? `ask_worker_retrieval: all passed, ${pass} checks`
                       : `ask_worker_retrieval FAILED, ${fail} of ${pass + fail}`);
process.exit(fail ? 1 : 0);
