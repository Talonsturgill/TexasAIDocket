// The written answer lane behind texasaidocket.com.
//
// WHAT THIS IS FOR, AND WHAT IT IS NOT. The ask box on the front page answers most questions
// with no request at all: the index and the catalogue ship inside the page, and the engine in
// scripts/site/ask_answers.py routes every field read, filter, sort and count in the reader's
// own browser. That lane is free, instant, and works on a phone with no signal in a county
// meeting room. It is most of what the box does and this worker does not touch it.
//
// This is the other lane. SUBMITTING a question, by pressing enter or the arrow, calls a model
// and costs money every time.
//
// TYPING STILL COSTS NOTHING, and that is now an engineering fact rather than a promise made
// to a reader. The page used to say it under the field and the copy came off in #59, on the
// owner's call, because it was a sentence about plumbing sitting where somebody was deciding
// what to ask. The BEHAVIOUR is not up for the same review. A request per keystroke against a
// cap counted in calls a month is a bill, not a feature, and it would empty the month inside
// an afternoon.
//
// WHY A WORKER AND NOT A SERVER. It holds two secrets and forwards one call. The only thing it
// stores is an answer that has already been checked, which expires by itself. There is no
// schema to migrate, no project to pause and no row that can go stale. Cloudflare already
// serves the domain and Turnstile, so this adds a file rather than a vendor.
//
// WHAT MAKES IT HONEST. Nothing the model writes reaches a reader unchecked. Every sentence
// passes checks.js against the published record before it is sent, and a sentence that fails
// ends the answer there, visibly, with the reason named, rather than being quietly repaired.

import { answer, answerStream, dailySpendOf, effectiveEffort, effectiveModel, packInfo, probe,
         readerOf, spendOf, usageOf } from "./answer.js";

// LARGE ENOUGH TO SHOW THE PRODUCT OFF. Sixty five messages is thirty two full exchanges and
// one more question. Sixty four thousand characters lets those exchanges carry real answers,
// and the body has another thirty two KiB for JSON, tokens and future envelope fields. These
// are abuse boundaries, not product copy budgets.
export const REQUEST_LIMITS = Object.freeze({
  body_bytes: 96 * 1024,
  messages: 65,
  question_characters: 1200,
  message_characters: 8000,
  conversation_characters: 64000,
});
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

/** Read the real bytes, because Content-Length is optional and supplied by the caller. */
export async function payloadOf(request) {
  const declared = Number(request.headers.get("content-length"));
  if (Number.isFinite(declared) && declared > REQUEST_LIMITS.body_bytes) {
    return { error: "request too large", status: 413 };
  }

  let text = "", bytes = 0;
  if (request.body?.getReader) {
    const reader = request.body.getReader();
    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      bytes += value.byteLength;
      if (bytes > REQUEST_LIMITS.body_bytes) {
        try { await reader.cancel(); } catch { /* the rejection still stands */ }
        return { error: "request too large", status: 413 };
      }
      text += decoder.decode(value, { stream: true });
    }
    text += decoder.decode();
  } else {
    text = await request.text();
    bytes = new TextEncoder().encode(text).byteLength;
    if (bytes > REQUEST_LIMITS.body_bytes) return { error: "request too large", status: 413 };
  }

  try {
    return { payload: JSON.parse(text) };
  } catch {
    return { error: "invalid JSON", status: 400 };
  }
}

/** Validate rather than silently trim what the model is asked to remember. */
export function conversationOf(payload) {
  const raw = Array.isArray(payload?.messages) ? payload.messages
    : typeof payload?.question === "string" ? [{ role: "user", content: payload.question }]
    : [];
  if (!raw.length) return { error: "ask a question", status: 400 };
  if (raw.length > REQUEST_LIMITS.messages) {
    return { error: "That conversation is full. Start over to keep asking.", status: 413 };
  }

  const turns = [];
  let total = 0, expected = "user";
  for (const message of raw) {
    if (!message || !["user", "assistant"].includes(message.role)
        || typeof message.content !== "string" || !message.content.trim()) {
      return { error: "messages need a role and text", status: 400 };
    }
    if (message.role !== expected) {
      return { error: "messages must alternate user and assistant", status: 400 };
    }
    const content = message.content.trim();
    const ownLimit = message.role === "user"
      ? REQUEST_LIMITS.question_characters : REQUEST_LIMITS.message_characters;
    if (content.length > ownLimit) {
      return {
        error: message.role === "user"
          ? "That question is over 1,200 characters. Start a fresh follow-up for the rest."
          : "That conversation is full. Start over to keep asking.",
        status: 413,
      };
    }
    total += content.length;
    if (total > REQUEST_LIMITS.conversation_characters) {
      return { error: "That conversation is full. Start over to keep asking.", status: 413 };
    }
    turns.push({ role: message.role, content });
    expected = expected === "user" ? "assistant" : "user";
  }
  if (turns[turns.length - 1].role !== "user") {
    return { error: "the last message must be a question", status: 400 };
  }
  return { turns };
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
      const now = new Date().toISOString();
      const reader = await readerOf(request.headers.get("cf-connecting-ip"), env);
      return json({
        kv_binding: !!env.ASK_KV,
        anthropic_key: !!env.ANTHROPIC_API_KEY,
        turnstile_secret: !!env.TURNSTILE_SECRET,
        // Where the month stands, from the same function the cap gate reads, so enforcement
        // and diagnosis cannot disagree. The only other way to learn this was a reader
        // hitting the wall, which is the last person you want finding out.
        spend: await spendOf(env, now),
        limits: {
          request: REQUEST_LIMITS,
          daily: await dailySpendOf(env, now, reader),
        },
        // The model actually in use, not the variable. Reporting the variable and calling it
        // "(default)" when unset tells a debugger nothing about which model that resolved to,
        // which is the one question this endpoint exists to answer.
        model: effectiveModel(env),
        model_from: env.ASK_MODEL ? "ASK_MODEL variable" : "pinned in code",
        // How hard it is being asked to think, reported for the same reason the model is: the
        // variable name tells a debugger nothing about what it resolved to.
        effort: effectiveEffort(env),
        effort_from: env.ASK_EFFORT ? "ASK_EFFORT variable" : "default in code",
        // WHAT THE MONTH ACTUALLY COST, which is a different question from how many calls it
        // took. `cache_hit_rate` is the one to read: below about a fifth, the five minute cache
        // is charging 25 percent extra to write entries nobody comes back for, and the TTL is
        // the wrong length. `mean_first_ms` is the wait a reader feels before words appear.
        usage: await usageOf(env, new Date().toISOString()),
        // WHICH SHAPE THE PROMPT IS TAKING, and what it costs. Retrieval turns itself off
        // for a pack with no index or a record small enough to send whole, and both of those
        // are invisible from outside. Read `mode`: anything starting "whole" means the slice
        // is not happening and the reason is in the brackets.
        prompt: await packInfo(env),
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

    let read;
    try { read = await payloadOf(request); }
    catch { return json({ error: "invalid request" }, 400, env); }
    if (read.error) return json({ error: read.error }, read.status, env);
    const payload = read.payload;
    const conversation = conversationOf(payload);
    if (conversation.error) return json({ error: conversation.error }, conversation.status, env);
    const turns = conversation.turns;

    const ip = request.headers.get("cf-connecting-ip") || "";
    const human = await verifyTurnstile(payload.turnstile_token, env.TURNSTILE_SECRET, ip);
    if (!human) return json({ error: "finish the human check first" }, 403, env);
    const reader = await readerOf(ip, env);

    // Streamed by default. The guard checks a sentence at a time anyway, so a verified
    // sentence can be shown the moment it is complete rather than after the whole reply
    // lands, which is most of why the wait feels long. A client can still ask for it whole.
    if (payload.stream === false) {
      const out = await answer(turns, env, undefined, reader);
      return json(out.body, out.status, env);
    }
    return new Response(await answerStream(turns, env, undefined, reader), {
      headers: {
        "content-type": "application/x-ndjson; charset=utf-8",
        "cache-control": "no-store",
        ...corsFor(env),
      },
    });
  },
};
