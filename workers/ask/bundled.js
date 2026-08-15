// GENERATED FILE. Do not edit.
//
// The ask worker's three modules flattened into one, so it can be deployed by pasting into
// the Cloudflare dashboard without a terminal. Regenerate with:
//
//   node workers/ask/bundle.mjs
//
// Edit checks.js, answer.js or worker.js instead. The tests run against those, and
// test-bundle.mjs runs the same assertions against this, so the two can't drift without
// something going red.

// ==========================================================================
// checks.js
// ==========================================================================

// What a written answer is allowed to say, enforced sentence by sentence.
//
// The model is told the rules in the prompt. This is what happens when it forgets, and it
// runs on every sentence before that sentence reaches a reader. A sentence that fails ends
// the answer there, visibly, with the reason named. Nothing is quietly repaired except
// punctuation, and the line between those two cases is drawn deliberately below.
//
// TWO KINDS OF RULE, AND THEY GET DIFFERENT TREATMENT.
//
//   A CLAIM ABOUT THE WORLD is refused. An unauthorised figure, a citation to a decision
//   that does not exist, a verdict on grid reliability. These end the answer. A smoothed
//   over wrong number is worse than a visible stop, because the reader can't see it happen.
//
//   A TYPING HABIT is rewritten. A semicolon is not a claim about anything, and ending an
//   answer over a punctuation mark punishes the reader for the model's typing. The rewrite
//   runs BEFORE the sentence is checked and before it is sent, so the text a reader sees is
//   the exact text that passed. There is no window in which a checked sentence is edited.
//
// This is numeral_lint moved from build time to answer time. The site's law is that every
// numeral it publishes was produced by code from data, and an answer written at read time is
// no exception to it.

// THE NUMERAL PATTERN, AND WHY IT LOOKS LIKE THIS. It is scripts/site/numeral_lint.py's
// NUMERAL, transcribed exactly. A thousands separator is part of the number and not a
// boundary in it, so 8,927 is ONE token. A checker that split on the comma would treat the
// digits either side of every separator in the record as separate authorised figures, which
// is most of the small numbers there are, and the gate would pass almost anything.
//
// tests/ask_written.mjs runs the same strings through both implementations. If this line and
// that file ever disagree, the build-time lint and the answer-time lint are measuring
// different things and one of them is lying.
const NUMERAL_RE = /\d(?:[\d,]*\d)?(?:\.\d+)?/g;

export function normalise(tok) {
  let t = String(tok).replace(/,/g, "");
  // Padding zeros go. The zero in FRONT of a decimal point does not: 0.8469 becoming .8469
  // leaves a token NUMERAL_RE can't match, so a model writing it back that way would slip
  // the figure past this gate entirely.
  t = /^0\./.test(t) ? "0" + t.replace(/^0+/, "") : (t.replace(/^0+/, "") || "0");
  if (t.includes(".")) t = t.replace(/0+$/, "").replace(/\.$/, "") || "0";
  return t;
}

export function numerals(text) {
  return (String(text).match(NUMERAL_RE) || []).map(normalise);
}

// A CALL ON WHETHER THE GRID HOLDS, in either direction. CLAUDE.md, and it does not bend:
// the grid watch publishes measured load, modeled load and the derived residual, and never a
// reliability verdict. A unit trip or a transmission constraint can produce an emergency on a
// day the numbers looked comfortable, and per site large load metering is confidential, so
// the call is not the record's to make in either direction.
//
// Each pattern targets a PREDICATE and never a noun, so mentioning a shortfall is fine and
// calling one is not. An all clear is as much a verdict as an alarm and is caught the same.
const VERDICT = [
  /\b(?:will|wo n't|won'?t|will not|going to|gonna)\s+(?:\w+\s+){0,2}?(?:hold|hold up|fail|run\s+short|be\s+enough|have\s+enough|keep\s+up)/i,
  /\bthere\s+(?:is|are|will\s+be)\s+(?:\w+\s+){0,2}?(?:enough|sufficient|adequate|plenty)\b/i,
  /\b(?:enough|sufficient|adequate|plenty\s+of)\s+(?:power|capacity|generation|supply|reserve|margin|headroom|water|storage)\b/i,
  /\b(?:the\s+grid|ercot|the\s+system|capacity|supply|reserves?|the\s+state|texas)\s+(?:is|are|will\s+be)\s+(?:\w+\s+){0,1}?(?:adequate|sufficient|fine|safe|secure|okay|ok|strained|at\s+risk)\b/i,
  /\ball\s+clear\b/i,
  /\bblack\s?outs?\b/i,
  /\brolling\s+outages?\b/i,
  /\b(?:no|little)\s+(?:risk|danger|chance)\s+of\b/i,
  /\b(?:we|you|texans?|ratepayers?)\s+(?:will|should|wo n't|won'?t|will not)\s+(?:\w+\s+){0,2}?(?:be fine|be okay|be ok|lose power|go dark|run out)/i,
  /\b(?:shortfall|shortage|outage|curtailment|emergency)\s+(?:is|will\s+be|of)\s+(?:\w+\s+){0,2}?(?:likely|coming|expected|certain|imminent|unlikely)\b/i,
  /\b(?:is|are|will\s+be)\s+(?:not\s+)?safe\b/i,
  // And the same refusal for the other instrument, and for guessing an outcome.
  /\b(?:reservoirs?|storage|the\s+drought)\s+(?:will|wo n't|won'?t)\s+(?:\w+\s+){0,2}?(?:recover|hold|last|run\s+out)/i,
  /\b(?:will|wo n't|won'?t|is\s+likely\s+to|expected\s+to)\s+(?:be\s+)?(?:approved|denied|adopted|rejected|pass|fail)\b/i,
];

// A SENTENCE THAT DECLINES TO MAKE THE CALL necessarily contains the words of the call it is
// declining to make. "The record doesn't say whether there will be enough capacity" trips the
// second pattern above and is exactly the sentence this box should write. Without the
// exemption the guard blocks its own correct refusal, which is how a safety check ends up
// teaching a model to answer instead of decline.
const DISCLAIMED =
  /\b(?:does\s+not|doesn'?t|do\s+not|don'?t|cannot|can'?t|could\s+not|couldn'?t|will\s+not|wo\s?n'?t|no\s+one|nobody)\s+(?:\w+\s+){0,2}?(?:say|says|state|states|publish|publishes|predict|predicts|forecast|forecasts|tell|know|answer|claim|make)\b/i;
const NO_SUCH_THING =
  /\bn(?:o|ot\s+a)\s+(?:public\s+)?(?:forecast|prediction|projection|verdict|guarantee|assurance|call)\b/i;

export function checkVerdict(text) {
  if (DISCLAIMED.test(text) || NO_SUCH_THING.test(text)) return { ok: true };
  for (const re of VERDICT) {
    const m = text.match(re);
    if (m) return { ok: false, reason: "verdict", hit: m[0].trim() };
  }
  return { ok: true };
}

const CITE_RE = /\[\[([^\]]+)\]\]/g;

export function checkCitations(text, slugs) {
  const unknown = [];
  for (const m of text.matchAll(CITE_RE)) {
    if (!slugs.has(m[1])) unknown.push(m[1]);
  }
  return unknown.length ? { ok: false, reason: "citation", unknown } : { ok: true };
}

export function checkNumerals(text, allowed) {
  // Citation ids carry digits (tx-2026-0001). They are checked as slugs, so stripping them
  // here stops a valid citation being read as an unauthorised figure.
  const prose = text.replace(CITE_RE, " ");
  const bad = numerals(prose).filter((n) => !allowed.has(n));
  return bad.length ? { ok: false, reason: "numeral", offending: bad } : { ok: true };
}

// FIRST PERSON, banned in published copy by CLAUDE.md. This box speaks for a record and not
// for itself, and "I think" from a record is a category error before it is a style problem.
//
// TWO PATTERNS, AND THE SPLIT IS NOT COSMETIC.
//
// EVERY CONTRACTION REQUIRES ITS APOSTROPHE. Writing we'?re, with the apostrophe optional,
// makes the pattern match "were". It also matches "well" for we'?ll and "wed" for we'?d. This
// record is mostly about weather, power and filings, so those are everyday words here and the
// guard would have refused ordinary true sentences.
//
// CASE MATTERS FOR EXACTLY TWO WORDS. "I" is first person and "i" alone is not a word worth
// catching. "us" is first person and "US" is a country that appears all over a docket about
// federal agencies. Folding case would refuse "the US Army Corps of Engineers".
const FIRST_PERSON_ANYCASE =
  /\b(?:me|my|mine|myself|we|we['’](?:re|ve|ll|d)|our|ours|ourselves|let['’]s)\b/i;
const FIRST_PERSON_EXACT = /\b(?:I|I['’](?:m|ve|ll|d)|us)\b/;

export function checkVoice(text) {
  // A quoted source may say "we" all it likes. Those are not this record's words, and
  // rewriting a quotation to fit house style would be falsifying it.
  const unquoted = String(text).replace(/"[^"]*"/g, '""');
  const m = unquoted.match(FIRST_PERSON_ANYCASE) || unquoted.match(FIRST_PERSON_EXACT);
  if (m) return { ok: false, reason: "voice", hit: m[0].trim() };
  return { ok: true };
}

// The composite the streaming loop calls. Cheapest and strictest first, so a failure names
// the most actionable cause.
export function checkSentence(text, { allowed, slugs }) {
  const c = checkCitations(text, slugs);
  if (!c.ok) return c;
  const n = checkNumerals(text, allowed);
  if (!n.ok) return n;
  const v = checkVoice(text);
  if (!v.ok) return v;
  return checkVerdict(text);
}

// HOW THE HOUSE PUNCTUATES, APPLIED TO A MACHINE THAT DOES NOT.
//
// Colons, semicolons, em dashes and en dashes are all banned in published copy here, and the
// first two more strictly than the sibling product bans them. The model is told in the
// prompt. This is the backstop, and it REWRITES rather than refusing, for the reason set out
// at the top of this file.
//
// Nothing here can touch a figure. Every rule either replaces a mark with another mark or
// lifts a letter to a capital. The one rule that goes near digits, a dash between two
// numbers, keeps both and leaves a hyphen, because turning 2024-2025 into "2024, 2025" would
// change what it says and this file's whole job is that nothing does.
const FILLER = [
  // Whole sentences carrying no content. Removed entirely.
  /^(?:great|good|excellent|interesting)\s+question[.!]?\s*/i,
  /^(?:certainly|absolutely|sure thing|sure|of course|indeed)[,.!]\s*/i,
  /^i hope (?:this|that) helps[.!]?\s*/i,
  /^happy to help[.!]?\s*/i,
  // Throat clearing in front of a real sentence. The clause goes and what follows is lifted
  // to a capital, meaning intact.
  /^(?:it'?s |it is )?(?:worth |important |also worth )?(?:noting|mentioning|pointing out) that\s+/i,
  /^(?:please )?(?:do )?note that\s+/i,
  /^to (?:be clear|answer your question|directly answer)[,:]?\s+/i,
  /^in (?:conclusion|summary|short)[,:]?\s+/i,
  /^at its core[,:]?\s+/i,
  /^that (?:being )?said[,:]?\s+/i,
];

export function plainly(text) {
  let t = String(text)
    // Straight quotes, the same rule the site builder enforces on itself.
    .replace(/[‘’]/g, "'")
    .replace(/[“”]/g, '"')
    .replace(/…/g, "...")
    // A dash between two numbers is a range. Both numbers survive.
    .replace(/(\d)\s*[—–]\s*(\d)/g, "$1-$2")
    .replace(/[,\s]*[—–]\s*/g, ", ")
    // A semicolon is a full stop that lost its nerve. Give it its nerve back.
    .replace(/;\s+([a-z])/g, (_, c) => ". " + c.toUpperCase())
    .replace(/;(?=\s)/g, ".")
    // A colon in prose is a label bolted onto a sentence that could have opened with the
    // thing itself. A clock time keeps its colon because that is a number, not punctuation.
    .replace(/(?<!\d):(?=\s)/g, ",")
    // "cannot" is never written here.
    .replace(/\bcannot\b/g, "can't")
    .replace(/\bCannot\b/g, "Can't")
    .replace(/,\s*,/g, ",")
    .replace(/,\s*([.!?])/g, "$1")
    .replace(/^[,\s]+/, "");
  for (const re of FILLER) {
    const before = t;
    t = t.replace(re, "");
    if (t !== before) t = t.charAt(0).toUpperCase() + t.slice(1);
  }
  // Never open a sentence with And or But. The clause survives, the conjunction goes.
  t = t.replace(/^(?:And|But)\s+([a-z])/, (_, c) => c.toUpperCase());
  return t;
}

export function splitSentences(buffer) {
  const parts = plainly(buffer).split(/(?<=[.!?])\s+/);
  const remainder = parts.pop() ?? "";
  return { sentences: parts, remainder };
}

// ==========================================================================
// answer.js
// ==========================================================================

// The written answer. One model call, the whole record in front of it, every sentence checked
// against that record before it reaches a reader.
//
// NO RETRIEVAL. The record is about 37,600 tokens, which fits in one context with room over,
// so there is no embedding step, no vector store, no chunking and no similarity threshold to
// tune. The largest single source of wrong answers in a retrieval chatbot is retrieving the
// wrong passage, and a record this size lets that failure mode be deleted rather than managed.
//
// THE PACK AND THE CORPUS ARE FETCHED, NOT BUNDLED. Both are rebuilt daily with the record and
// this worker is not. A worker carrying its own copy would answer from yesterday's docket the
// morning after a run and nothing would say so. Both are held at Cloudflare's edge for fifteen
// minutes, so answering does not pay a round trip to Pages for a file that changes once a day.

const SITE = "https://texasaidocket.com";
const PACK_URL = `${SITE}/ask-pack.json`;
const CORPUS_URL = `${SITE}/ask-corpus.json`;

// Pinned rather than left to a variable, so a deploy cannot silently change what answers.
// ASK_MODEL overrides it when a model is being trialled, and /_config reports which won.
const DEFAULT_MODEL = "claude-sonnet-5";
const DEFAULT_CAP = 200;
const MAX_TOKENS = 700;
const ANSWER_TTL = 60 * 60 * 24 * 7;

// EVERY KV KEY THIS WORKER WRITES CARRIES THIS.
//
// Not decoration. A sibling product runs the same design against a different record, and on
// 2026-08-15 both workers were pointed at ONE KV namespace by mistake. Two things went wrong
// at once and only one of them was about money.
//
// The spend counters merged, so a 200 ceiling and a 500 ceiling read the same number and each
// site's questions ate the other's budget. That is annoying.
//
// The answer caches merged too, and that is not annoying, it is a lie. The cache key is built
// from the pack date and the conversation, both packs are generated daily, so the SAME
// question asked on both sites on the SAME day produced the SAME key. This site could have
// served an answer about Cook Inlet gas storage under its own name.
//
// A prefix makes the collision impossible whatever namespace someone binds, which is the
// right place to fix it: a deploy time mistake should not be able to reach a reader.
const KV_PREFIX = "tx";

export function effectiveModel(env) {
  return env.ASK_MODEL || DEFAULT_MODEL;
}

export function capOf(env) {
  const raw = env.ASK_MONTHLY_CAP;
  if (raw === undefined || raw === null || raw === "") return DEFAULT_CAP;
  const n = Number(raw);
  return Number.isFinite(n) && n >= 0 ? Math.floor(n) : DEFAULT_CAP;
}

/**
 * The conversation, not just the latest line. A follow-up like "when does that close" only
 * means something with what came before it.
 *
 * ONLY GUARD APPROVED TEXT GOES BACK. The client sends its own thread, and what it stores for
 * the assistant's turns is the checked prefix and never the raw reply. A sentence a reader was
 * never shown must not be something the model can build on either, or a refused claim
 * re-enters through the back door on the next question.
 */
export function turnsOf(payload) {
  const raw = Array.isArray(payload?.messages) ? payload.messages
    : payload?.question ? [{ role: "user", content: payload.question }]
    : [];
  return raw
    .filter((m) => m && typeof m.content === "string" && m.content.trim())
    .map((m) => ({
      role: m.role === "assistant" ? "assistant" : "user",
      content: String(m.content).slice(0, 4000),
    }));
}

export function normaliseQuestion(q) {
  return String(q).toLowerCase().replace(/[^a-z0-9\s]/g, " ").replace(/\s+/g, " ").trim();
}

/**
 * The key covers the WHOLE conversation, not the latest question. "What about the other one"
 * means something different after every first question, so keying on the last message alone
 * would serve one thread's answer into another's. Follow-ups mostly miss, and that is correct.
 */
export async function cacheKey(turns, packDate) {
  const thread = turns.map((m) => m.role + ":" + normaliseQuestion(m.content)).join("\n");
  const digest = await crypto.subtle.digest("SHA-256",
    new TextEncoder().encode(`${packDate}\n${thread}`));
  const hex = [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
  return `a:${KV_PREFIX}:${packDate}:${hex.slice(0, 32)}`;
}

export function monthKey(nowISO) {
  return `spend:${KV_PREFIX}:${nowISO.slice(0, 7)}`;
}

/**
 * Where the month stands against its ceiling.
 *
 * The counter has always existed, because the cap is enforced by reading it. What did not
 * exist in the sibling until late was any way to LOOK at it, so the only signal that a month
 * was nearly spent was a reader hitting the wall. This reports the same number the gate reads,
 * so enforcement and diagnosis cannot disagree.
 *
 * A count of model calls, not dollars. Repeats served from KV never increment it. The dollar
 * figure is that count times the per question cost, and it is left to the reader rather than
 * hardcoded, because a rate that changes on 2026-08-31 would go stale in the one place nobody
 * would think to check.
 */
export async function spendOf(env, nowISO) {
  const cap = capOf(env);
  if (!env.ASK_KV) return { cap, spent: null, left: null, note: "no KV bound" };
  const key = monthKey(nowISO || new Date().toISOString());
  const spent = Number(await env.ASK_KV.get(key)) || 0;
  return { month: nowISO ? nowISO.slice(0, 7) : new Date().toISOString().slice(0, 7),
           cap, spent, left: Math.max(0, cap - spent) };
}

async function fetchJSON(url) {
  const r = await fetch(url, { cf: { cacheTtl: 900, cacheEverything: true } });
  if (!r.ok) throw new Error(`fetch failed ${r.status} for ${url}`);
  return r.json();
}

export const loadPack = (env) => fetchJSON(env.ASK_PACK_URL || PACK_URL);
export const loadCorpus = (env) => fetchJSON(env.ASK_CORPUS_URL || CORPUS_URL);

/**
 * The prompt, in two blocks, and the split is the whole of the caching.
 *
 * Block one is the instructions and is small. Block two is the record and is nearly all of the
 * tokens, and it carries the breakpoint. Caching is a BYTE EXACT PREFIX MATCH, so anything
 * that varies per request has to sit after the breakpoint or it invalidates everything above
 * it. The conversation is in messages, which is after both, so it never does.
 *
 * Five minute TTL rather than an hour. The write costs 1.25x and a read costs 0.1x, so caching
 * pays once more than about 22 percent of questions land inside the window. Every follow-up in
 * a conversation is inside it by construction, and the downside if nobody follows up is a
 * bounded 25 percent on an isolated question.
 */
export function systemBlocks(pack) {
  return [
    { type: "text", text: pack.system },
    { type: "text", text: pack.pack, cache_control: { type: "ephemeral" } },
  ];
}

function modelParams(env) {
  // No temperature, top_p or top_k. Sonnet 5 returns 400 on all three.
  return { model: effectiveModel(env), max_tokens: MAX_TOKENS };
}

const HEADERS = (env) => ({
  "content-type": "application/json",
  "x-api-key": env.ANTHROPIC_API_KEY,
  "anthropic-version": "2023-06-01",
});

/**
 * Is the key real and does the API answer this worker? /_config reports what is configured,
 * which is a different question from whether the configuration WORKS, and the second one is
 * the one that matters when an answer fails.
 *
 * Returns status and error TYPE only. Never a key, never a response body.
 */
export async function probe(env) {
  if (!env.ANTHROPIC_API_KEY) {
    return { ok: false, status: null, error_type: "no key", error_message: null };
  }
  try {
    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: HEADERS(env),
      body: JSON.stringify({
        ...modelParams(env), max_tokens: 4,
        messages: [{ role: "user", content: "hi" }],
      }),
    });
    const body = await r.json().catch(() => ({}));
    return {
      ok: r.ok,
      status: r.status,
      model: effectiveModel(env),
      error_type: body?.error?.type ?? null,
      error_message: body?.error?.message ?? null,
    };
  } catch (e) {
    return { ok: false, status: null, error_type: "fetch failed", error_message: String(e) };
  }
}

/**
 * Everything both paths need before either spends anything, and the cap gate itself.
 *
 * A CACHED ANSWER IS SERVED EVEN IN A SPENT MONTH. Turning off new spending should not blank a
 * question that has already been paid for and checked.
 */
async function preflight(turns, env, now) {
  if (!env.ANTHROPIC_API_KEY) return { stop: { error: "the answerer is not configured" }, status: 503 };
  const pack = await loadPack(env);
  const key = env.ASK_KV ? await cacheKey(turns, pack.generated) : null;

  if (key) {
    const hit = await env.ASK_KV.get(key);
    if (hit) return { cached: JSON.parse(hit) };
  }

  const cap = capOf(env);
  const mk = monthKey(now || new Date().toISOString());
  const spent = env.ASK_KV ? Number(await env.ASK_KV.get(mk)) || 0 : 0;
  if (spent >= cap) return { capped: true };

  const corpus = await loadCorpus(env);
  return {
    pack, key, mk, spent,
    ctx: {
      allowed: new Set(corpus.authorised_numerals),
      slugs: new Set(corpus.slugs),
    },
  };
}

/** The whole answer at once, for a client that cannot stream. */
export async function answer(turns, env, now) {
  const pre = await preflight(turns, env, now);
  if (pre.stop) return { status: pre.status, body: pre.stop };
  if (pre.cached) return { status: 200, body: pre.cached };
  if (pre.capped) return { status: 200, body: { capped: true } };

  const { pack, key, mk, spent, ctx } = pre;
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: HEADERS(env),
    body: JSON.stringify({
      ...modelParams(env),
      system: systemBlocks(pack),
      messages: turns,
    }),
  });
  if (!r.ok) {
    const b = await r.json().catch(() => ({}));
    return { status: 502, body: { error: b?.error?.message || "the answerer could not reply" } };
  }
  const body = await r.json();
  if (env.ASK_KV) {
    await env.ASK_KV.put(mk, String(spent + 1), { expirationTtl: 60 * 60 * 24 * 70 });
  }

  const raw = (body.content || []).filter((c) => c.type === "text").map((c) => c.text).join("");
  const out = verify(raw, ctx);
  if (env.ASK_KV && key) {
    await env.ASK_KV.put(key, JSON.stringify(out), { expirationTtl: ANSWER_TTL });
  }
  return { status: 200, body: out };
}

/**
 * Check a whole answer and return the accepted prefix.
 *
 * Cut at the first sentence that fails rather than quietly repaired. A reader seeing an answer
 * stop short, and being told why, is better served than one shown a smoothed over sentence
 * nobody verified.
 */
export function verify(text, { allowed, slugs }) {
  const { sentences, remainder } = splitSentences(String(text).trim());
  const all = remainder.trim() ? [...sentences, remainder] : sentences;
  const kept = [];
  for (const s of all) {
    const v = checkSentence(s, { allowed, slugs });
    if (!v.ok) return { text: kept.join(" "), withheld: true, reason: v.reason, sentence: s };
    kept.push(s.trim());
  }
  return { text: kept.join(" "), withheld: false };
}

/**
 * The streaming path, which is the default.
 *
 * The guard checks a sentence at a time anyway, so a verified sentence can be shown the moment
 * it is complete rather than after the whole reply lands, and that is most of why the wait
 * feels long. Nothing is shown first and checked later: a sentence reaching the page has
 * already passed.
 *
 * ndjson, one event per line: {stage} | {sentence} | {withheld} | {capped} | {error} | {done}
 */
export async function answerStream(turns, env, now) {
  const enc = new TextEncoder();
  const line = (o) => enc.encode(JSON.stringify(o) + "\n");

  return new ReadableStream({
    async start(controller) {
      const send = (o) => controller.enqueue(line(o));
      try {
        const pre = await preflight(turns, env, now);
        if (pre.stop) { send({ error: pre.stop.error }); controller.close(); return; }
        if (pre.capped) { send({ capped: true }); controller.close(); return; }
        if (pre.cached) {
          // Replay a paid-for answer as if it were arriving, so the reader sees one behaviour.
          for (const s of splitSentences(pre.cached.text + " ").sentences) send({ sentence: s });
          if (pre.cached.withheld) send({ withheld: pre.cached.reason });
          send({ done: true });
          controller.close();
          return;
        }

        const { pack, key, mk, spent, ctx } = pre;
        send({ stage: "Reading the record" });

        const r = await fetch("https://api.anthropic.com/v1/messages", {
          method: "POST",
          headers: HEADERS(env),
          body: JSON.stringify({
            ...modelParams(env),
            system: systemBlocks(pack),
            messages: turns,
            stream: true,
          }),
        });
        if (!r.ok || !r.body) {
          const b = await r.json().catch(() => ({}));
          send({ error: b?.error?.message || "the answerer could not reply" });
          controller.close();
          return;
        }
        if (env.ASK_KV) {
          await env.ASK_KV.put(mk, String(spent + 1), { expirationTtl: 60 * 60 * 24 * 70 });
        }

        const reader = r.body.getReader();
        const dec = new TextDecoder();
        let sse = "", prose = "", kept = [], stopped = null;

        outer:
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          sse += dec.decode(value, { stream: true });
          const lines = sse.split("\n");
          sse = lines.pop();
          for (const l of lines) {
            if (!l.startsWith("data:")) continue;
            let ev;
            try { ev = JSON.parse(l.slice(5).trim()); } catch { continue; }
            const piece = ev?.delta?.text;
            if (typeof piece !== "string") continue;
            prose += piece;
            const { sentences, remainder } = splitSentences(prose);
            prose = remainder;
            for (const s of sentences) {
              const v = checkSentence(s, ctx);
              if (!v.ok) { stopped = v; break outer; }
              kept.push(s.trim());
              send({ sentence: s.trim() });
            }
          }
        }

        // Whatever is left in the buffer is a final sentence with no trailing space.
        if (!stopped && prose.trim()) {
          const v = checkSentence(prose.trim(), ctx);
          if (v.ok) { kept.push(prose.trim()); send({ sentence: prose.trim() }); }
          else stopped = v;
        }

        if (stopped) send({ withheld: stopped.reason });
        else send({ done: true });

        if (env.ASK_KV && key) {
          await env.ASK_KV.put(key, JSON.stringify({
            text: kept.join(" "),
            withheld: !!stopped,
            reason: stopped?.reason ?? null,
          }), { expirationTtl: ANSWER_TTL });
        }
      } catch (e) {
        send({ error: "the answerer could not reply" });
        console.log("stream failed", String(e));
      }
      controller.close();
    },
  });
}

// ==========================================================================
// worker.js
// ==========================================================================

// The written answer lane behind texasaidocket.com.
//
// WHAT THIS IS FOR, AND WHAT IT IS NOT. The ask box on the front page answers most questions
// with no request at all: the index and the catalogue ship inside the page, and the engine in
// scripts/site/ask_answers.py routes every field read, filter, sort and count in the reader's
// own browser. That lane is free, instant, works on a phone with no signal in a county meeting
// room, and sends nothing anywhere. It is most of what the box does and this worker does not
// touch it.
//
// This is the other lane. SUBMITTING a question, by pressing enter or the arrow, calls a model
// and costs money every time. The page says so above the button, before the press. Typing
// still sends nothing and the page says that too. Neither statement may be weakened without
// changing what the code actually does.
//
// WHY A WORKER AND NOT A SERVER. It holds two secrets and forwards one call. The only thing it
// stores is an answer that has already been checked, which expires by itself. There is no
// schema to migrate, no project to pause and no row that can go stale. Cloudflare already
// serves the domain and Turnstile, so this adds a file rather than a vendor.
//
// WHAT MAKES IT HONEST. Nothing the model writes reaches a reader unchecked. Every sentence
// passes checks.js against the published record before it is sent, and a sentence that fails
// ends the answer there, visibly, with the reason named, rather than being quietly repaired.

const MAX_QUESTION = 400;
const DEFAULT_ORIGIN = "https://texasaidocket.com";

// Read from the environment rather than hardcoded. The site moved from a github.io subpath to
// its own domain on 2026-08-15, and a hardcoded origin is exactly the thing that would have
// needed a redeploy to follow it.
const corsFor = (env) => ({
  "access-control-allow-origin": env.ASK_ORIGIN || DEFAULT_ORIGIN,
  "access-control-allow-methods": "POST, OPTIONS",
  "access-control-allow-headers": "content-type",
  "access-control-max-age": "86400",
});

function json(body, status, env) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", ...corsFor(env) },
  });
}

async function verifyTurnstile(token, secret, ip) {
  if (!secret) return true; // not configured; /_config says so out loud
  if (!token) return false;
  const body = new FormData();
  body.append("secret", secret);
  body.append("response", token);
  if (ip) body.append("remoteip", ip);
  const r = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify",
    { method: "POST", body });
  const out = await r.json().catch(() => ({ success: false }));
  return out.success === true;
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") return new Response(null, { headers: corsFor(env) });

    const path = new URL(request.url).pathname.replace(/\/+$/, "");

    // A presence check. Booleans and non-secret values only, never a key, so this leaks
    // nothing an error message does not already imply.
    //
    // It exists because "the answerer is not configured" cannot say WHICH thing is missing
    // without printing secrets, and the alternative is asking a person to re-read a settings
    // page and taking their word for it. One request answers it instead.
    if (path === "/_config") {
      return json({
        kv_binding: !!env.ASK_KV,
        anthropic_key: !!env.ANTHROPIC_API_KEY,
        turnstile_secret: !!env.TURNSTILE_SECRET,
        // Where the month stands, from the same function the cap gate reads, so enforcement
        // and diagnosis cannot disagree. The only other way to learn this was a reader
        // hitting the wall, which is the last person you want finding out.
        spend: await spendOf(env),
        // The model actually in use, not the variable. Reporting the variable and calling it
        // "(default)" when unset tells a debugger nothing about which model that resolved to,
        // which is the one question this endpoint exists to answer.
        model: effectiveModel(env),
        model_from: env.ASK_MODEL ? "ASK_MODEL variable" : "pinned in code",
        origin: env.ASK_ORIGIN || `${DEFAULT_ORIGIN} (default)`,
        // Every name the worker can actually see, so a typo shows up as the wrong string
        // rather than as a missing one.
        visible: Object.keys(env).sort(),
      }, 200, env);
    }

    // Does the API actually answer this worker? /_config reports what is configured. This
    // reports whether it WORKS, which is a different question and the one that matters when
    // an answer fails.
    if (path === "/_probe") return json(await probe(env), 200, env);

    if (request.method !== "POST") return json({ error: "POST only" }, 405, env);
    if (path !== "/answer") return json({ error: "not found" }, 404, env);

    let payload;
    try {
      payload = await request.json();
    } catch {
      return json({ error: "invalid JSON" }, 400, env);
    }

    const turns = turnsOf(payload);
    if (!turns.length) return json({ error: "ask a question" }, 400, env);
    const question = turns[turns.length - 1].content;
    if (question.length > MAX_QUESTION) {
      return json({ error: `keep it under ${MAX_QUESTION} characters` }, 400, env);
    }

    const ip = request.headers.get("cf-connecting-ip") || "";
    const human = await verifyTurnstile(payload.turnstile_token, env.TURNSTILE_SECRET, ip);
    if (!human) return json({ error: "finish the human check first" }, 403, env);

    // Streamed by default. The guard checks a sentence at a time anyway, so a verified
    // sentence can be shown the moment it is complete rather than after the whole reply
    // lands, which is most of why the wait feels long. A client can still ask for it whole.
    if (payload.stream === false) {
      const out = await answer(turns, env);
      return json(out.body, out.status, env);
    }
    return new Response(await answerStream(turns, env), {
      headers: {
        "content-type": "application/x-ndjson; charset=utf-8",
        "cache-control": "no-store",
        ...corsFor(env),
      },
    });
  },
};
