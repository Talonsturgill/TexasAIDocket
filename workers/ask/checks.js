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
