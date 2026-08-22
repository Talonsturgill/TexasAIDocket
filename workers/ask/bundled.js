// GENERATED FILE. Do not edit.
//
// The ask worker's three modules flattened into one, so it can be deployed by pasting into
// the Cloudflare dashboard without a terminal. Regenerate with:
//
//   node workers/ask/bundle.mjs
//
// Edit the modules instead. `node workers/ask/bundle.mjs --check` goes red when this file is
// not what they produce, and workers/ask/test.js runs it, so a stale paste-file cannot pass CI.

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
// retriever.js
// ==========================================================================

// GENERATED FILE. Do not edit.
//
// The one retriever, emitted by scripts/site/ask_retrieval.py, which is where the reasoning
// and the tests live. The browser lane gets the same source inlined into the page. Two copies
// that agree today is the failure this repo keeps relearning, so neither is hand written and
// `python3 scripts/site/ask_retrieval.py --self-test` goes red when they drift.
//
// Regenerate with:
//
//   python3 scripts/site/ask_retrieval.py --write-worker

/* ---------------------------------------------------------------- shared retriever
   Generated by scripts/site/ask_retrieval.py. Do not edit in place: it is embedded in the
   page AND in the worker, and a hand edit to one of them is the two lanes disagreeing about
   which decision a question is about. */
function askTokens(s) {
  return String(s == null ? "" : s).toLowerCase()
    .replace(/[^a-z0-9 ]+/g, " ").split(/\s+/).filter(Boolean);
}

/* THE DOCUMENT IS THE WHOLE DECISION, not just its title. Everything a reader might remember
   about it goes in: what it is called, what it says, who decided it, where it is, what it is
   filed under. A field they half remember is the field they will type. */
function askDoc(it) {
  return [it.title, it.summary, it.decider, (it.counties || []).join(" "),
          String(it.topic || "").replace(/-/g, " "), it.status].filter(Boolean).join(" ");
}

/* Built once per page load, not per keystroke. 69 decisions of a few hundred words each is a
   few milliseconds; doing it on every character is what made the previous scorer visible on a
   mid range phone. */
function askIndex(items) {
  var docs = [], df = {}, total = 0;
  items.forEach(function (it) {
    var tf = {}, n = 0;
    askTokens(askDoc(it)).forEach(function (w) {
      if (w.length < 2) return;
      tf[w] = (tf[w] || 0) + 1; n += 1;
    });
    Object.keys(tf).forEach(function (w) { df[w] = (df[w] || 0) + 1; });
    docs.push({ id: it.id, tf: tf, len: n });
    total += n;
  });
  return { docs: docs, df: df, N: docs.length || 1,
           avg: docs.length ? total / docs.length : 1 };
}

/* BM25. `idf` is the Robertson form with the +1 that keeps a term appearing in EVERY document
   at zero rather than negative: a word every decision uses says nothing about which one is
   meant, and a negative score would actively push the right answer down. */
/* The frame of a question, dropped from the QUERY and never from the documents. The reasoning,
   which is long and is not a reader's to download, is in scripts/site/ask_retrieval.py under
   THE FRAME OF A QUESTION. Short version: IDF cannot tell "how" from a rare topical word, and
   "how" is in nearly every question a person types. "may" is absent because it is a month. */
var askFrame = new Set(("what which who whom whose when where why how whether " +
  "is are was were be been being am do does did done doing " +
  "can could will would shall should must ought " +
  "have has had having " +
  "the and but for nor yet so than that this these those there here " +
  "about above across after against along among around before behind below beneath beside " +
  "between beyond during except from inside into near onto outside over through throughout " +
  "under underneath until upon with within without " +
  "all any both each either few many more most much neither none once only other some such " +
  "her hers him his its our ours she her their theirs them they you your yours mine my " +
  "tell tells told say says said know knows get gets got give gives show shows " +
  "want wants need needs please thanks thank hello " +
  "anything something everything nothing anyone someone everyone " +
  "just also very really still even ever never always").split(" "));

function askBm25(idx, query) {
  var qs = askTokens(query).filter(function (w) {
    return w.length > 2 && !askFrame.has(w);
  });
  if (!qs.length) return [];
  var out = [];
  idx.docs.forEach(function (d) {
    /* WHAT MATCHED, NOT ONLY HOW WELL. A score alone cannot tell one repeated common word from
       two independent rare ones, and those mean completely different things about whether the
       reader meant this decision. `terms` counts DISTINCT query words present and `rarest` is
       the smallest document frequency among them, so a caller can insist on corroboration
       rather than on a number that both cases can reach. */
    var s = 0, terms = 0, rarest = Infinity;
    qs.forEach(function (w) {
      var f = d.tf[w] || 0;
      if (!f) return;
      var n = idx.df[w] || 0;
      var idf = Math.log(1 + (idx.N - n + 0.5) / (n + 0.5));
      s += idf * (f * (1.2 + 1)) / (f + 1.2 * (1 - 0.75 + 0.75 * (d.len / idx.avg)));
      /* ONLY A DISCRIMINATING WORD CORROBORATES. Counting every match made "best way to train
         for a marathon" look corroborated, because "best", "way" and "for" are all in a record
         about anything. A word most decisions use cannot be evidence for one of them, and the
         threshold is the corpus's own, so it never needs a stopword list somebody maintains. */
      if (idf >= 1.0) terms += 1;
      if (n && n < rarest) rarest = n;
    });
    if (s > 0) out.push({ id: d.id, score: s, terms: terms,
                          rarest: rarest === Infinity ? 0 : rarest });
  });
  out.sort(function (a, b) { return b.score - a.score || (a.id < b.id ? -1 : 1); });
  return out;
}

/* RECIPROCAL RANK FUSION. Each list contributes 1/(k + rank) for whatever it ranked, so a
   decision both lists like beats one that either loves. Magnitudes are discarded on purpose:
   see the note in ask_retrieval.py about adding scores from unrelated scales. */
function askFuse(lists) {
  var acc = {};
  lists.forEach(function (list) {
    (list || []).forEach(function (row, i) {
      var id = row && row.id;
      if (!id) return;
      acc[id] = (acc[id] || 0) + 1 / (60 + i + 1);
    });
  });
  return Object.keys(acc).map(function (id) { return { id: id, score: acc[id] }; })
    .sort(function (a, b) { return b.score - a.score || (a.id < b.id ? -1 : 1); });
}

// ==========================================================================
// retrieve.js
// ==========================================================================

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
  const sendWhole = (why) => ({
    blocks: [
      { type: "text", text: pack.system },
      { type: "text", text: pack.pack, cache_control: { type: "ephemeral" } },
    ],
    mode: `whole (${why})`, chosen: items.map((it) => it.id), shown: items.length,
    of: items.length, chars: pack.system.length + pack.pack.length,
  });

  if (off) return sendWhole("off");
  if (!index) return sendWhole("no index");
  if (!items.length) return sendWhole("unsplit");
  if (bodies <= WHOLE_UNDER) return sendWhole("fits");

  // THE CONVERSATION FIRST, THEN THE QUESTION ON ITS OWN IF THAT FOUND NOTHING.
  //
  // Reading the last few turns together is what makes "and the dates?" mean anything. It also
  // means an earlier turn can poison a later one. Ask about NVIDIA, which this record does not
  // carry, then ask about Bexar County, which it does, and the joined query carries a word
  // pointing off the record while the second question on its own does not.
  //
  // An earlier turn can only ever ADD words. So a joined query that finds nothing, where the
  // latest turn alone would have found something, is context getting in the way rather than
  // helping, and the second pass costs one more BM25 sweep over 69 documents.
  const query = queryOf(turns);
  let picked = pickItems(query, items, {});
  const latest = queryOf(turns, 1);
  if (!picked.chosen.length && latest && latest !== query) {
    const retry = pickItems(latest, items, {});
    if (retry.chosen.length) picked = retry;
  }
  const { chosen, corroborated, pinned } = picked;
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

  // RETRIEVAL MAY NEVER COST MORE THAN NOT RETRIEVING, and without this line it can. The index
  // is paid on every question and the size where sending everything gets cheaper is a
  // different number from the size where retrieval starts being worth doing. On a record just
  // over the second, a breadth question asking for fourteen bodies plus the whole index adds
  // up to more than the record it is a slice of.
  //
  // That gap is not reachable today at 187,030 characters of bodies and it is exactly the kind
  // of thing that becomes reachable while nobody is looking. Comparing the two assembled sizes
  // is unconditional and makes the guarantee one nobody has to keep two thresholds apart to
  // maintain.
  const assembled = pack.system.length + preamble.length + index.length + slice.length;
  if (assembled >= pack.system.length + pack.pack.length) return sendWhole("slice is no smaller");

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
    chars: assembled,
  };
}

// ==========================================================================
// answer.js
// ==========================================================================

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

// ==========================================================================
// worker.js
// ==========================================================================

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
