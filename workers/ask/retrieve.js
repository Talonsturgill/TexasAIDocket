// Which decisions go in front of the model, and which the model is only told exist.
//
// WHY THIS EXISTS AT ALL. The written lane put the WHOLE record in the system block. That was
// the right call and it had a shelf life: the pack is at 86 percent of a ceiling whose
// crossing is a hard build failure, and the registry work adds decisions faster than anything
// removes them. Cost was never the problem. At 200 calls a month the whole pack costs under
// $30. The ceiling is the problem, and it arrives on a date nobody chose.
//
// THE FAILURE THIS DESIGN REFUSES TO INHERIT. A retrieval chatbot's worst failure is not
// missing a passage. It is answering as though the missing thing does not exist, confidently,
// with a reader who has no way to see it happen. So the model is ALWAYS given the complete
// index of what the record holds, and only the BODIES are a slice. It can say "the record
// carries one about that" for an item whose text it never saw, which is both the honest answer
// and the thing a plain vector search cannot do.
//
// That property is also what lets retrieval be generous rather than precise. Sending a body
// that turns out to be irrelevant costs tokens. Failing to send one costs nothing worse than
// an index line, because the index line is still there.
//
// THE RETRIEVER IS NOT WRITTEN HERE. It is retriever.js, generated from
// scripts/site/ask_retrieval.py, the same source the page embeds. Two implementations that
// agree today is the failure this repo keeps relearning under new names.

import { askBm25, askFuse, askIndex, askTokens, askFrame } from "./retriever.js";

// The pack's own shape, asserted on the producing side by ask_pack.py's self-test and on this
// side by workers/ask/test.js. Both run in CI. A cut this file makes on a shape the builder
// stopped emitting would be a silent half empty prompt, so neither side takes it on trust.
export const DECISIONS_MARK = "THE DECISIONS.";
const FENCE = "\n\n" + DECISIONS_MARK + "\n\n";

// HOW MANY BODIES, and why two numbers rather than one.
//
// Six covers a question about a decision, a county, a decider or a date, which is nearly all
// of them. A survey question is a different shape and needs breadth more than depth, so it
// gets more of them and a lower bar to clear.
const TOP_N = 6;
const BREADTH_N = 14;
// Nothing matched, but the reader half remembered one word. Three bodies is cheap enough that
// guessing beats refusing to guess, and the index carries the rest of the answer anyway.
const FLOOR_N = 3;

// THE HARD CAP ON A SLICE, in characters, about 15,000 tokens. Only a breadth question can
// approach it. It is here so that a pathological query cannot quietly rebuild the whole pack.
const MAX_BODY_CHARS = 60_000;

// WHEN RETRIEVAL TURNS ITSELF OFF. Below this the whole record is cheaper to send than to
// reason about, and choosing wrongly costs more than the tokens choosing saves. This is not a
// threshold anybody maintains. It is the point where the slice stops being a saving, and if
// the record ever shrinks past it the worker goes back to sending everything on its own.
const WHOLE_UNDER = 40_000;

/**
 * Cut the pack back into a preamble and one block per decision.
 *
 * NOT SHIPPED PRE-SPLIT, DELIBERATELY. Publishing the bodies a second time inside the same
 * JSON would double a file the record already fills, and the split is exact: ask_pack.py
 * fences the mark with blank lines and every block opens with its id at the start of a line.
 * Both facts are asserted in that file's self-test and again in this worker's.
 */
export function splitPack(packText) {
  const text = String(packText || "");
  const at = text.indexOf(FENCE);
  if (at < 0) return { preamble: text, items: [] };
  const preamble = text.slice(0, at);
  const items = [];
  for (const block of text.slice(at + FENCE.length).split("\n\n")) {
    const b = block.trim();
    if (!b.startsWith("[[")) continue;
    const close = b.indexOf("]]");
    if (close < 0) continue;
    const id = b.slice(2, close);
    const firstBreak = b.indexOf("\n");
    const title = (firstBreak < 0 ? b.slice(close + 2) : b.slice(close + 2, firstBreak)).trim();
    // The identity of a decision is its title and the line of facts under it. Retrieval reads
    // that separately from the body, so a question that names WHAT a decision is beats one
    // that happens to brush a phrase buried in a claim quote.
    const lines = b.split("\n");
    items.push({ id, title, head: lines.slice(0, 2).join(" "), text: b, chars: b.length });
  }
  return { preamble, items };
}

/**
 * The question, as the retriever should read it.
 *
 * ALL THE RECENT USER TURNS, NOT ONLY THE LAST. "What about the dates?" retrieves nothing on
 * its own and everything when read next to the turn before it. Three is enough for a follow-up
 * without letting a long conversation drag its opening subject through every later answer.
 */
export function queryOf(turns, keep = 3) {
  return (turns || []).filter((t) => t && t.role === "user")
    .slice(-keep).map((t) => String(t.content || "")).join(" ");
}

// A QUESTION ABOUT THE RECORD RATHER THAN ABOUT A DECISION. "How many", "which ones", "list
// them". These want breadth and they want the counts, and the counts are in the preamble which
// every question gets. What they additionally need is more bodies and a lower bar, because the
// evidence for "all the ones in Bexar County" is spread across many items by definition.
const BREADTH =
  /\b(?:how many|how much|which ones|which decisions|list|all (?:of|the)|every|each|count|total|across the record|compare|breakdown|so far|altogether|overall|summar(?:y|ise|ize))\b/i;

export function wantsBreadth(q) {
  return BREADTH.test(String(q || ""));
}

// AN ID TYPED OUT IS NOT A GUESS. A reader who writes tx-2026-0043, or pastes a citation from
// an earlier answer, has named the decision exactly and no scorer should get a vote.
const ID_RE = /\b(tx-\d{4}-\d{4})\b/gi;

export function pinnedIds(query, known) {
  const out = [];
  for (const m of String(query || "").matchAll(ID_RE)) {
    const id = m[1].toLowerCase();
    if (known.has(id) && !out.includes(id)) out.push(id);
  }
  return out;
}

/**
 * How much of this question has the record never heard of?
 *
 * A WORD THE RECORD HAS NEVER USED IS THE ONLY EVIDENCE AGAINST a question being about the
 * record, and it is thrown away by every scorer here. BM25 cannot use it: a term in no
 * document contributes nothing to any score, so "marathon" and "sourdough" are silently
 * dropped and whatever else was in the sentence decides. That is the mirror of the bug wave 2
 * found, where an UNSEEN word was scored as the most distinctive word there is. It is the same
 * mistake read the other way round, and it wants the opposite correction.
 *
 * Counted on the frame stripped query, so "how" and "the" are neither evidence for nor
 * against anything.
 *
 * GENEROUS ABOUT WHAT COUNTS AS KNOWN, DELIBERATELY, because of what being wrong costs on each
 * side. There is no stemmer here, so the record's "withdrawals" leaves a reader's "withdrawal"
 * looking like a word nothing has ever used. In a five word question that is noise. In
 * "withdrawal permits" it is half the sentence, and a real reader gets refused over an "s".
 *
 * So a word counts as known if the record uses the SAME word in the other number. Singular and
 * plural, and nothing further.
 *
 * THE LINE IS AT INFLECTION AND IT WAS DRAWN BY MEASUREMENT. A first version also folded "ed",
 * "ing", "al" and "ion", which is derivation rather than inflection, and it read "train" as
 * known because the record contains "training". Those are two different words. One is what a
 * model does and the other is what a person does before a marathon, and folding them handed
 * "best way to train for a marathon" three real decisions again, which is the case this whole
 * rule exists to refuse. Recall fell 99.6 to 99.1 in the same move.
 *
 * Loose is the safe direction here in a way it is not in the scorer, since this measure only
 * ever REFUSES to guess, so being loose makes it refuse less often. That is an argument for
 * generosity, not for having no line. The scoring is untouched and still matches whole words.
 */
function knownish(w, idx) {
  if (idx.df[w]) return true;
  // The other number of the same word, both directions. "withdrawal" against a record that
  // says "withdrawals", and "counties" against one that says "county".
  const forms = [w + "s", w + "es"];
  if (w.endsWith("s")) forms.push(w.slice(0, -1));
  if (w.endsWith("es")) forms.push(w.slice(0, -2));
  if (w.endsWith("ies")) forms.push(w.slice(0, -3) + "y");
  if (w.endsWith("y")) forms.push(w.slice(0, -1) + "ies");
  return forms.some((f) => f.length > 2 && idx.df[f]);
}

export function strangeness(query, idx) {
  var known = 0, unknown = 0;
  for (const w of askTokens(query)) {
    if (w.length <= 2 || askFrame.has(w)) continue;
    if (knownish(w, idx)) known += 1; else unknown += 1;
  }
  return { known, unknown, ratio: (known + unknown) ? unknown / (known + unknown) : 0 };
}

/**
 * Choose the bodies.
 *
 * TWO VIEWS FUSED, NOT ONE SEARCH. The body view finds a decision by something a reader
 * remembers reading in it. The head view finds one by what it IS, which is what somebody
 * typing a half remembered title or a decider's name is doing. They rank differently and both
 * are right about different questions, so reciprocal rank fusion keeps the order both agree on
 * and throws away two magnitudes that were never on the same scale.
 *
 * CORROBORATION SETS THE BAR, NOT THE SCORE. One word shared with a decision is a coincidence
 * and two is a signal, which is the rule wave 2 measured into the browser lane after "best way
 * to train for a marathon" reached a grant about robot safety. Here it decides how many bodies
 * are worth paying for rather than whether to answer at all, so an uncorroborated best guess
 * still gets a floor of a few, unless something in the question points off the record entirely.
 * The index covers whatever the guess misses.
 */
export function pickItems(query, items, opts = {}) {
  const breadth = opts.breadth ?? wantsBreadth(query);
  const want = opts.top ?? (breadth ? BREADTH_N : TOP_N);
  const need = breadth ? 1 : 2;

  const known = new Set(items.map((it) => it.id));
  const pinned = pinnedIds(query, known);

  const bodyIdx = askIndex(items.map((it) => ({ id: it.id, summary: it.text })));
  const headIdx = askIndex(items.map((it) => ({ id: it.id, summary: it.head })));

  // A HIT ON NOTHING BUT COMMON WORDS IS NOT A HIT, AND FUSING IT IS WORSE THAN IGNORING IT.
  //
  // BM25 returns any document with a score above zero, and a word most of the record uses
  // scores just above zero everywhere. Left in, those hits do not merely pad the list, they
  // WIN it. "Erath county" put the one decision naming Erath first in the body list and
  // nowhere in the title list, while twenty eight decisions matched "county" in both, and
  // reciprocal rank fusion correctly preferred what both lists agreed on. It was agreement
  // about a word that means nothing.
  //
  // So each list is cut to the hits carrying at least one word the record does not use
  // everywhere, BEFORE they are fused. The threshold is the corpus's own, computed by the
  // retriever, so no stopword list has to be maintained as the record grows.
  const evidence = (list) => list.filter((h) => h.terms >= 1);
  const body = evidence(askBm25(bodyIdx, query));
  const head = evidence(askBm25(headIdx, query));

  // Corroboration is a fact about the match, so it is read off the lists rather than off the
  // fused order, which has thrown the term counts away along with the magnitudes.
  const terms = {};
  for (const h of [...body, ...head]) {
    terms[h.id] = Math.max(terms[h.id] || 0, h.terms);
  }

  const fused = askFuse([body, head]);
  const strong = fused.filter((r) => (terms[r.id] || 0) >= need).map((r) => r.id);
  const weak = fused.filter((r) => !strong.includes(r.id)).map((r) => r.id);

  const chosen = [];
  const push = (id) => { if (id && !chosen.includes(id)) chosen.push(id); };
  pinned.forEach(push);
  strong.slice(0, want).forEach(push);
  // ONE RARE WORD IS ENOUGH TO SHOW THE MODEL A BODY, though it was not enough to name a
  // decision as the answer in the page's own lane. The size of the claim sets the evidence.
  // Naming one decision out of sixty nine is a claim about the world. Putting its text in a
  // prompt is a guess that costs 2,700 characters and that the index makes harmless if it is
  // wrong, because the model can still see every decision that exists. A reader who half
  // remembers one distinctive word is a real reader and refusing to guess for them is worse
  // than guessing. What does NOT clear the bar is a hit on words the whole record uses, which
  // is filtered out above and is the difference between a guess and a coincidence.
  //
  // UNLESS SOMETHING IN THE QUESTION POINTS SOMEWHERE ELSE. "Best way to train for a marathon"
  // survives every rule above, because "best" is in one decision and "way" is in five, both by
  // accident, and a coincidence with two halves looks exactly like a signal. What tells them
  // apart is the word no scorer was looking at: "marathon" is in no decision at all, and BM25
  // cannot use that, because a term in no document contributes nothing to any score.
  //
  // WHAT THIS COSTS, SAID OUT LOUD. It also refuses to guess for "anything about NVIDIA in
  // Sherman" when the record has the county and not the company. That reader still gets an
  // answer, from the index, naming the decision and what its line says, because every decision
  // is indexed whatever the retriever decided. A degraded answer is the right side to fail on.
  // The other way round puts three unrelated real decisions in front of a model that has been
  // asked about running, and a plausible answer assembled out of real text is the one thing
  // downstream cannot catch.
  // ONE UNKNOWN WORD IS ENOUGH TO STOP THE GUESS, and a ratio was tried first and was wrong.
  // "Best way to train for a marathon" is three quarters familiar to this record, because
  // "best" is in one decision, "way" is in five and "trains" is in one, all by accident. Only
  // "marathon" points anywhere else, and it is right and the other three are noise. Weighing
  // them by count lets the coincidences outvote the one word that is actually telling you
  // something, which is the shape of every bug in this retriever's history.
  //
  // This bites ONLY where the strong list is already empty, so it never touches a question with
  // two corroborating words in one decision, which is nearly every real one. What it refuses is
  // the intersection of thin evidence and a word pointing elsewhere.
  const strange = strangeness(query, bodyIdx);
  if (chosen.length < FLOOR_N && strange.unknown === 0) {
    weak.slice(0, FLOOR_N - chosen.length).forEach(push);
  }

  return { chosen: chosen.slice(0, Math.max(want, pinned.length)),
           corroborated: strong.length, ranked: fused.length, pinned, strange };
}

const SLICE_HEAD =
  "THE DECISIONS MOST LIKELY TO ANSWER THIS QUESTION, in full. The index above lists every " +
  "decision the record holds and this is a slice of it. An item indexed above and absent " +
  "here is still real and still citable. Nothing about it beyond its index line is known to " +
  "you. Cite it and say what its line says and stop there.";

const NO_SLICE =
  "NO DECISION MATCHES THIS QUESTION closely enough to send its full text. The index above is " +
  "the whole record. Answer from the counts and the index. If the record does not carry this " +
  "say so plainly and name what it does carry instead.";

/**
 * The three blocks, in the order the cache wants them.
 *
 *   1  the instructions                          stable forever
 *   2  the preamble, the counts and the index    stable for a day, and CACHED
 *   3  the bodies this question needs            different every time, not cached
 *
 * The breakpoint sits at the end of block 2 because caching is a byte exact prefix match, so
 * anything that varies per question has to live after it. Blocks 1 and 2 together are well
 * over the 1,024 token minimum a cache entry needs, which block 1 alone would not be.
 */
export function assemble(pack, turns, env) {
  const off = String(env?.ASK_RETRIEVAL ?? "").trim().toLowerCase() === "off";
  const { preamble, items } = splitPack(pack.pack);
  const bodies = items.reduce((n, it) => n + it.chars, 0);
  const index = pack.index || "";

  // NO INDEX MEANS AN OLDER PACK. A worker deployed ahead of a site rebuild would otherwise
  // send a slice with nothing standing in for the rest, which is the exact failure the index
  // exists to prevent. Send everything instead, and say why in the mode.
  const whole = off || !index || !items.length || bodies <= WHOLE_UNDER;
  if (whole) {
    const why = off ? "off" : !index ? "no index" : !items.length ? "unsplit" : "fits";
    return {
      blocks: [
        { type: "text", text: pack.system },
        { type: "text", text: pack.pack, cache_control: { type: "ephemeral" } },
      ],
      mode: `whole (${why})`, chosen: items.map((it) => it.id), shown: items.length,
      of: items.length, chars: pack.pack.length,
    };
  }

  const query = queryOf(turns);
  const { chosen, corroborated, pinned } = pickItems(query, items, {});
  const byId = new Map(items.map((it) => [it.id, it]));

  const sent = [];
  let used = 0;
  for (const id of chosen) {
    const it = byId.get(id);
    if (!it) continue;
    if (used + it.chars > MAX_BODY_CHARS && sent.length) break;
    sent.push(it);
    used += it.chars;
  }

  const slice = sent.length
    ? SLICE_HEAD + "\n\n" + sent.map((it) => it.text).join("\n\n")
    : NO_SLICE;

  return {
    blocks: [
      { type: "text", text: pack.system },
      { type: "text", text: preamble + "\n\n" + index,
        cache_control: { type: "ephemeral" } },
      { type: "text", text: slice },
    ],
    mode: sent.length ? "slice" : "index only",
    chosen: sent.map((it) => it.id),
    shown: sent.length, of: items.length, corroborated, pinned,
    chars: pack.system.length + preamble.length + index.length + slice.length,
  };
}
