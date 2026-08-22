// The written answer. One model call, the whole record in front of it, every sentence checked
// against that record before it reaches a reader.
//
// RETRIEVAL, AND THE ONE THING IT IS NOT ALLOWED TO COST. The whole record used to go in the
// system block. It no longer fits with room to spare: the pack sits at 86 percent of a ceiling
// whose crossing is a hard build failure, and the record grows every day. So retrieve.js sends
// the bodies a question needs and the COMPLETE INDEX of everything the record holds, which
// means the model always knows what exists even for an item whose text it was not given. The
// worst failure of a retrieval chatbot, answering as though the missing thing is not there,
// is designed out rather than mitigated. See retrieve.js for the reasoning and the numbers.
//
// No embedding step, no vector store, no second service. The retriever is BM25 over the
// bodies fused with BM25 over the titles, generated from scripts/site/ask_retrieval.py, which
// is the same source the page's own lane embeds. One implementation, never two.
//
// THE PACK AND THE CORPUS ARE FETCHED, NOT BUNDLED. Both are rebuilt daily with the record and
// this worker is not. A worker carrying its own copy would answer from yesterday's docket the
// morning after a run and nothing would say so. Both are held at Cloudflare's edge for fifteen
// minutes, so answering does not pay a round trip to Pages for a file that changes once a day.

import { checkSentence, numerals, splitSentences } from "./checks.js";
import { assemble } from "./retrieve.js";

const SITE = "https://texasaidocket.com";
const PACK_URL = `${SITE}/ask-pack.json`;
const CORPUS_URL = `${SITE}/ask-corpus.json`;

// Pinned rather than left to a variable, so a deploy cannot silently change what answers.
// ASK_MODEL overrides it when a model is being trialled, and /_config reports which won.
const DEFAULT_MODEL = "claude-sonnet-5";
const DEFAULT_CAP = 200;
// Raised from 700 on 2026-08-15, after an eval cut two answers mid word. "under the Paperw"
// and "The record only sh" both reached a reader. The questions that hit it were the ones
// worth asking, three open comment windows and a survey of data center projects, because an
// answer that has to name several decisions is exactly the answer that runs long.
//
// Output is the cheap half. At Sonnet 5 rates 1,400 tokens is about 1.4 cents against roughly
// 10 cents of input on every question, so the ceiling was buying almost nothing and costing
// the answers a reader most needs.
const MAX_TOKENS = 1400;
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
// served the other record's answer, about another state's infrastructure, under its own name,
// and a reader would have had no way to tell.
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
  // THE DATE IS WHAT MAKES THIS KEY EXPIRE. Without it every day shares one key, so a reader
  // gets an answer about a record that has since changed and nothing ever says so. A pack with
  // no `generated` is a broken pack and it has never shipped, but the same missing fallback
  // was found twice in this file on the same afternoon, once in usageKey and once here, so it
  // is closed rather than argued about. Today's date keeps the daily rotation.
  const day = packDate || new Date().toISOString().slice(0, 10);
  const thread = turns.map((m) => m.role + ":" + normaliseQuestion(m.content)).join("\n");
  const digest = await crypto.subtle.digest("SHA-256",
    new TextEncoder().encode(`${day}\n${thread}`));
  const hex = [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
  return `a:${KV_PREFIX}:${day}:${hex.slice(0, 32)}`;
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
 * The prompt, and the split is the whole of the caching.
 *
 * Three blocks now rather than two. The instructions, then the counts and the complete index
 * of every decision, then the bodies this question actually needs. The breakpoint sits at the
 * end of the second, because caching is a BYTE EXACT PREFIX MATCH and anything that varies per
 * request has to live after it. The conversation is in messages, after all three, so it never
 * invalidates anything.
 *
 * The instructions alone would be under the 1,024 token minimum a cache entry needs. With the
 * index they are comfortably over it, which is the second reason the breakpoint goes there.
 *
 * Five minute TTL rather than an hour. The write costs 1.25x and a read costs 0.1x, so caching
 * pays once more than about 22 percent of questions land inside the window. Every follow-up in
 * a conversation is inside it by construction, and the downside if nobody follows up is a
 * bounded 25 percent on an isolated question.
 */
export function systemBlocks(pack, turns, env) {
  return assemble(pack, turns, env).blocks;
}

/**
 * WHAT THE MODEL MAY STATE A NUMBER FROM, narrowed to what it was actually handed.
 *
 * ask-corpus.json authorises every numeral in the WHOLE pack, and while the whole pack was
 * what went in the prompt those were the same set. They are not the same set any more. Reading
 * the published list after retrieval would authorise figures out of decisions the model never
 * saw, which is exactly the confident nonsense the guard exists to stop, and it would be the
 * retrieval quietly weakening a promise that had nothing to do with it.
 *
 * So the list is read off the assembled prompt. The promise is the one ask_corpus.py always
 * made, kept exactly, and now strictly tighter than the published file:
 *
 *     THE MODEL MAY STATE A NUMBER ONLY IF THAT NUMBER WAS IN WHAT IT WAS SHOWN.
 *
 * Same tokeniser as numeral_lint and as the page, because tests/ask_written.mjs runs strings
 * through both and goes red if they ever disagree.
 *
 * SLUGS ARE NOT NARROWED THE SAME WAY, and that is deliberate. Every decision has a line in the
 * index whatever the retriever thought, so every id really was shown and every one stays
 * citable. Naming an item the record holds is the honest answer when its body is not below.
 */
export function allowedNumerals(blocks) {
  const seen = new Set();
  for (const b of blocks) for (const n of numerals(b.text || "")) seen.add(n);
  return seen;
}

/**
 * EFFORT, AND WHY IT IS MEDIUM RATHER THAN LOW.
 *
 * On Sonnet 5 an omitted `thinking` still runs ADAPTIVE thinking, and `output_config.effort`
 * defaults to `high`. So every question was thinking hard about a lookup over a record already
 * sitting in front of it, and a reader was waiting through it on the one part of this page that
 * talks back. That much was worth fixing and still is.
 *
 * LOW WAS A STEP TOO FAR, AND AN EVAL SESSION SHOWED IT. The reasoning for low was that the
 * record is in context so there is nothing to work out about where the answer lives. That is
 * true of the RECORD and false of a DECISION. Asked which decisions are in Erath County, with
 * the right decision's full text in the prompt, it answered "the record does not answer that".
 * Erath is one of twenty two counties listed inside that decision, and finding a name in a list
 * inside a document is work. Low is the budget for a lookup and this is not one.
 *
 * The same session showed the softer half of it. Asked what a groundwater district decided
 * about evaporative cooling, it correctly said no groundwater district did, while holding in
 * its prompt the Wichita Falls permit that BANS evaporative cooling. Right answer, and it never
 * made the connection sitting in front of it.
 *
 * Medium rather than high, because high is where the original complaint came from and nothing
 * here needs a model to deliberate over prose it can see. ASK_EFFORT moves it either way. An
 * unrecognised value falls back rather than reaching the API, because a typo in a dashboard
 * variable should not 400 every question.
 */
const EFFORT = new Set(["low", "medium", "high", "xhigh", "max"]);
const DEFAULT_EFFORT = "medium";

export function effectiveEffort(env) {
  const want = String(env?.ASK_EFFORT ?? "").trim().toLowerCase();
  return EFFORT.has(want) ? want : DEFAULT_EFFORT;
}

export function modelParams(env) {
  // No temperature, top_p or top_k. Sonnet 5 returns 400 on all three.
  return {
    model: effectiveModel(env),
    max_tokens: MAX_TOKENS,
    output_config: { effort: effectiveEffort(env) },
  };
}

/**
 * WHAT A QUESTION ACTUALLY COST, which nothing here could answer before.
 *
 * The call counter has always existed because the cap is enforced by reading it, and it says
 * nothing about tokens, cache or time. So the two questions that decide every tuning choice
 * were both unanswerable: is the prompt cache being READ or only written, and how long does a
 * reader wait before the first sentence appears.
 *
 * THE CACHE ONE IS NOT ACADEMIC. A write costs 1.25x and a read 0.1x, so caching only pays once
 * more than about a fifth of questions land inside the window. Below that it is a 25 percent
 * surcharge dressed as an optimisation, and there was no way to tell which was happening.
 *
 * TIME TO FIRST SENTENCE, not total time. The guard releases a sentence the moment it passes,
 * so what a reader experiences is the wait before anything appears, and total time is a number
 * about the model rather than about them.
 *
 * READ MODIFY WRITE, AND NOT ATOMIC. Two questions answered in the same instant can lose one
 * increment. At a cap of a few hundred calls a month that is a rounding error against what the
 * counters are for, and the alternative is a Durable Object for a diagnostic. Said out loud
 * here rather than discovered later in a total that does not tie out.
 */
export function usageKey(nowISO) {
  // THE FALLBACK IS THE WHOLE POINT OF THIS LINE. worker.js calls answerStream(turns, env)
  // with no third argument, because `now` exists for tests to pin a month. monthKey has always
  // written `monthKey(now || new Date().toISOString())` and this did not, so every real
  // request wrote its usage to `use:tx:undefin` while /_config read `use:tx:2026-08` and
  // honestly reported zero.
  //
  // Nine questions were answered before anyone noticed, because the counter is a diagnostic
  // and a broken diagnostic looks exactly like a quiet month. The spend counter was never
  // affected, which is why the cap kept working and hid it.
  return `use:${KV_PREFIX}:${String(nowISO || new Date().toISOString()).slice(0, 7)}`;
}

export function emptyUsage() {
  return { calls: 0, input: 0, cache_read: 0, cache_write: 0, output: 0,
           first_ms: 0, first_n: 0 };
}

export async function usageOf(env, nowISO) {
  if (!env?.ASK_KV) return { note: "no KV bound" };
  const raw = await env.ASK_KV.get(usageKey(nowISO));
  const u = { ...emptyUsage(), ...(raw ? JSON.parse(raw) : {}) };
  const cached = u.cache_read + u.cache_write;
  return {
    ...u,
    // The number the 5 minute TTL decision rests on. Null rather than zero when nothing has
    // been cached yet, because "no data" and "never read" are different answers.
    cache_hit_rate: cached ? +(u.cache_read / cached).toFixed(3) : null,
    mean_first_ms: u.first_n ? Math.round(u.first_ms / u.first_n) : null,
  };
}

export async function recordUsage(env, usage, firstMs, nowISO) {
  if (!env?.ASK_KV || !usage) return;
  try {
    const key = usageKey(nowISO);
    const raw = await env.ASK_KV.get(key);
    const u = { ...emptyUsage(), ...(raw ? JSON.parse(raw) : {}) };
    u.calls += 1;
    u.input += usage.input_tokens || 0;
    u.cache_read += usage.cache_read_input_tokens || 0;
    u.cache_write += usage.cache_creation_input_tokens || 0;
    u.output += usage.output_tokens || 0;
    if (Number.isFinite(firstMs)) { u.first_ms += firstMs; u.first_n += 1; }
    await env.ASK_KV.put(key, JSON.stringify(u), { expirationTtl: 60 * 60 * 24 * 400 });
  } catch (e) {
    // A diagnostic must never be able to fail an answer.
    console.log("usage not recorded", String(e));
  }
}

/**
 * WHAT THE PROMPT ACTUALLY LOOKS LIKE TODAY, which nothing could answer from outside.
 *
 * Retrieval is the kind of change that works in a test and quietly stops working in
 * production, because the two things that turn it off, a pack with no index and a record small
 * enough to send whole, are both invisible from here. /_config reports what is configured and
 * /_probe reports whether the API answers. This reports which shape the prompt is taking and
 * what it costs, from the same functions that build it, so enforcement and diagnosis cannot
 * disagree.
 *
 * Never fails the endpoint. A worker that cannot describe itself must still answer questions.
 */
export async function packInfo(env) {
  try {
    const pack = await loadPack(env);
    const sample = assemble(pack, [{ role: "user", content: "what is open for comment" }], env);
    const t = (n) => Math.round(n / 4);
    return {
      generated: pack.generated,
      decisions: pack.items,
      indexed: !!pack.index,
      mode: sample.mode,
      shown: `${sample.shown} of ${sample.of}`,
      // Tokens, roughly, at four characters each. Both numbers or neither: the saving is the
      // only reason retrieval is here and a number without its comparison is decoration.
      whole_tokens: t(pack.system.length + pack.pack.length),
      question_tokens: t(sample.chars),
      cached_tokens: t(sample.blocks.filter((b) => b.cache_control || b === sample.blocks[0])
        .reduce((n, b) => n + b.text.length, 0)),
      retrieval_from: env.ASK_RETRIEVAL ? "ASK_RETRIEVAL variable" : "on unless the pack is small",
    };
  } catch (e) {
    return { error: String(e && e.message ? e.message : e) };
  }
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
  // ASSEMBLED ONCE, HERE, and the guard is built from the same object that gets sent. Building
  // the prompt in one place and the allow-list in another is how the two come to describe
  // different bytes, and the whole promise of the numeral gate is that they describe the same
  // ones. Retrieval also costs a few milliseconds of BM25 and there is no reason to pay twice.
  const prompt = assemble(pack, turns, env);
  return {
    pack, key, mk, spent, prompt,
    ctx: {
      allowed: allowedNumerals(prompt.blocks),
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

  const { key, mk, spent, ctx, prompt } = pre;
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: HEADERS(env),
    body: JSON.stringify({
      ...modelParams(env),
      system: prompt.blocks,
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
  // No first-sentence time on this path: nothing is shown until the whole reply lands, so the
  // wait a reader feels IS the whole call and there is no earlier moment to record.
  await recordUsage(env, body.usage, NaN, now);

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

        const { key, mk, spent, ctx, prompt } = pre;
        const startedAt = Date.now();
        // WHAT IT IS ACTUALLY DOING, not a reassuring noise. The reader is told how much of
        // the record is being read closely, which is the honest description of a slice and
        // the thing that would look like a lie if the stage line kept saying "the record".
        send({ stage: prompt.shown && prompt.shown < prompt.of
                 ? `Reading ${prompt.shown} of ${prompt.of} decisions closely`
                 : "Reading the record",
               shown: prompt.shown, of: prompt.of });

        const r = await fetch("https://api.anthropic.com/v1/messages", {
          method: "POST",
          headers: HEADERS(env),
          body: JSON.stringify({
            ...modelParams(env),
            system: prompt.blocks,
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
        let sse = "", prose = "", kept = [], stopped = null, ranLong = false;
        // USAGE ARRIVES IN TWO PLACES ON A STREAM. `message_start` carries the input side,
        // including the two cache counters, and `message_delta` carries the output count as it
        // finishes. Neither is in the text events, so both are collected as they pass rather
        // than asked for at the end.
        let usage = null, firstMs = NaN;

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
            // The model says why it stopped, and it is the only thing that can. A trailing
            // fragment looks identical whether the model simply did not end on a full stop or
            // whether it was cut off in the middle of a word.
            if (ev?.delta?.stop_reason === "max_tokens") ranLong = true;
            if (ev?.type === "message_start" && ev.message?.usage) usage = { ...ev.message.usage };
            if (ev?.type === "message_delta" && ev.usage) usage = { ...(usage || {}), ...ev.usage };
            const piece = ev?.delta?.text;
            if (typeof piece !== "string") continue;
            prose += piece;
            const { sentences, remainder } = splitSentences(prose);
            prose = remainder;
            for (const s of sentences) {
              const v = checkSentence(s, ctx);
              if (!v.ok) { stopped = v; break outer; }
              // The moment the reader stops waiting, which is what latency means here.
              if (!Number.isFinite(firstMs)) firstMs = Date.now() - startedAt;
              kept.push(s.trim());
              send({ sentence: s.trim() });
            }
          }
        }

        // Whatever is left in the buffer is a final sentence with no trailing space, UNLESS
        // the model ran out of room, in which case it is half a sentence and possibly half a
        // word. Publishing that is worse than saying the answer was too long for the space,
        // because a reader cannot tell a truncation from the record simply stopping there.
        if (!stopped && prose.trim() && !ranLong) {
          const v = checkSentence(prose.trim(), ctx);
          if (v.ok) { kept.push(prose.trim()); send({ sentence: prose.trim() }); }
          else stopped = v;
        }

        if (stopped) send({ withheld: stopped.reason });
        else if (ranLong) send({ long: true });
        else send({ done: true });

        if (env.ASK_KV && key) {
          await env.ASK_KV.put(key, JSON.stringify({
            text: kept.join(" "),
            withheld: !!stopped,
            reason: stopped?.reason ?? null,
          }), { expirationTtl: ANSWER_TTL });
        }
        await recordUsage(env, usage, firstMs, now);
      } catch (e) {
        send({ error: "the answerer could not reply" });
        console.log("stream failed", String(e));
      }
      controller.close();
    },
  });
}
