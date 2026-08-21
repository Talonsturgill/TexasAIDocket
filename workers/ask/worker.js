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

import { answer, answerStream, capOf, effectiveEffort, effectiveModel, probe, spendOf,
         turnsOf, usageOf } from "./answer.js";

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
        // How hard it is being asked to think, reported for the same reason the model is: the
        // variable name tells a debugger nothing about what it resolved to.
        effort: effectiveEffort(env),
        effort_from: env.ASK_EFFORT ? "ASK_EFFORT variable" : "default in code",
        // WHAT THE MONTH ACTUALLY COST, which is a different question from how many calls it
        // took. `cache_hit_rate` is the one to read: below about a fifth, the five minute cache
        // is charging 25 percent extra to write entries nobody comes back for, and the TTL is
        // the wrong length. `mean_first_ms` is the wait a reader feels before words appear.
        usage: await usageOf(env, new Date().toISOString()),
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
