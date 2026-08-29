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
// Nothing matched, but the reader half remembered one word. A few bodies are cheap enough that
// guessing beats refusing to guess, and the index carries the rest of the answer anyway.
//
// SIX AND TWO, BOTH MEASURED. This path decides the whole answer for any question whose words
// are each common inside the family that should answer them, which is most questions naming a
// place: "bexar county construction" leaves one informative word per family and one does not
// clear the corroboration bar anywhere. Three items in one round sent the leading family and
// one token seat to each of the others, and the decisions could not be found at a depth of
// one. Two rounds of the top three families took the whole gold set from 94.8 percent found to
// 96.3. Three rounds bought 0.2 more for 200 tokens a question and four bought 0.2 again, so
// the line is where the curve flattens rather than where the number stops rising.
const FLOOR_N = 6;
const FLOOR_DEPTH = 2;

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
 * Cut every published body field with one parser.
 *
 * Facility dossiers moved beside the bounded core once the complete registry no longer fit
 * inside the retrieval-off context. Normal retrieval still needs one item list, and an older
 * pack without the sibling field must keep working during a site and worker rollout.
 */
export function splitRecord(pack) {
  const core = splitPack(pack?.pack);
  const facilities = splitPack(pack?.facility_pack);
  return { preamble: core.preamble, coreItems: core.items,
    items: [...core.items, ...facilities.items] };
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

// WHICH FAMILY A BLOCK BELONGS TO, read off its id and nothing else.
//
// The record used to be one kind of thing. It is now four: the decisions, the data center
// dossiers, the construction register rolled up by county, and reservoir storage. They are
// asked about in the same sentence often enough that splitting them into separate boxes would
// be worse than useless, and they cannot share one BM25 index, which is the finding that made
// this function necessary rather than tidy.
export function familyOf(id) {
  const s = String(id || "");
  if (/^tx-\d{4}-\d{4}$/.test(s)) return "tx";
  const cut = s.indexOf("-");
  return cut > 0 ? s.slice(0, cut) : s;
}

// HOW THE SLICE IS SHARED OUT, and the numbers are sizes rather than preferences.
//
// A decision block averages 2,708 characters, a dossier 1,609, a county rollup 390 and a
// reservoir 212. Six decisions used to cost 16,248 characters. The shares below cost about
// 14,600 for eight blocks across four families, so a wider question is now answered from more
// of the record for slightly less money. The decisions keep the largest share because they are
// the record's spine and because they are the only family a reader can ask about by id.
const SHARE = { tx: 4, facility: 2, county: 1, water: 1 };
const BREADTH_SHARE = { tx: 8, facility: 4, county: 3, water: 3 };
// A family this file has never heard of, which is what a new ledger looks like on the day it
// ships. It gets a seat rather than silence, because the alternative is data that is in the
// pack, in the index, and unreachable by every question.
const SHARE_DEFAULT = 1;
const BREADTH_DEFAULT = 2;

/**
 * Choose the bodies, one family at a time, then fuse.
 *
 * WHY NOT ONE INDEX OVER EVERYTHING, which is what this was and what it stopped being able to
 * be. Adding the other families took the corpus from 69 documents to 322, and BM25's two
 * corpus-wide statistics both broke on the way.
 *
 * IDF stopped meaning what it means. "County" appears in 136 of 322 blocks now, so its
 * informativeness fell below the floor and the word was discarded as boilerplate. It IS
 * boilerplate among sixty one blocks each titled "Construction registered in X County". It is
 * not boilerplate among the decisions, and discarding it there cost the county questions half
 * their recall in a single build, measured: 100 percent found and 60 first, down to 86.7 and
 * 30.
 *
 * Average document length stopped meaning what it means. Length normalisation at b=0.75 scores
 * a document against the corpus mean, and the mean is now dragged down by 138 reservoir blocks
 * of 212 characters, so every decision looks bloated and is penalised for it.
 *
 * Both are the same mistake, which is treating four kinds of document as one population. So
 * each family is indexed, scored and corroborated against its OWN population, where its own
 * boilerplate is common and its own lengths are comparable, and only the survivors are fused.
 *
 * THE SHARES ARE ALSO WHAT MAKES A WIDE QUESTION WORK, which is the reason this was built. Ask
 * what is happening in Dallas County and the honest answer draws on a decision, a construction
 * total and a data center, and a single ranked list hands back six blocks from whichever family
 * happened to word things closest. It returned exactly one.
 */
/**
 * How much this question is ABOUT a family, as against about one block inside it.
 *
 * THE SIGNAL PER FAMILY INDEXING THROWS AWAY, and it has to be put back somewhere else.
 *
 * Indexing each family separately was right and it fixed what it was meant to fix: within the
 * counties, "county" and "construction" appear in all sixty one blocks, so they carry nothing
 * about WHICH county and are correctly discarded there. The trouble is that they carry almost
 * everything about which FAMILY, and discarding them left nothing to tell the four apart.
 *
 * The measurement was blunt. "Bexar county construction" put the Bexar construction block
 * first 4.9 percent of the time. It was in the slice nearly always, so the old decisions-only
 * gold set could never see it, and the model was handed three decisions to read before the
 * block that actually answered the question.
 *
 * So a word common to a whole family is read here as EVIDENCE FOR THAT FAMILY, which is the
 * same fact the within-family pass reads as noise. Both readings are correct and they are
 * about different questions.
 *
 * Weighted by the term's GLOBAL informativeness so that "the" and "in", which are also in every
 * block of every family, contribute nothing to any of them.
 */
function affinity(query, group, globalIdx, n) {
  const seen = new Set();
  let total = 0;
  for (const w of askTokens(query)) {
    if (w.length <= 2 || askFrame.has(w) || seen.has(w)) continue;
    seen.add(w);
    const gdf = globalIdx.df[w] || 0;
    if (!gdf) continue;
    // The corpus wide inverse document frequency, the same shape BM25 uses, so a word most of
    // the record carries is worth little wherever it is concentrated.
    const idf = Math.log(1 + (n - gdf + 0.5) / (gdf + 0.5));
    let inFamily = 0;
    for (const it of group) if (askTokens(it.text).includes(w)) inFamily += 1;
    total += idf * (inFamily / group.length);
  }
  return total;
}

export function pickItems(query, items, opts = {}) {
  const breadth = opts.breadth ?? wantsBreadth(query);
  const want = opts.top ?? (breadth ? BREADTH_N : TOP_N);
  const need = breadth ? 1 : 2;

  const known = new Set(items.map((it) => it.id));
  const pinned = pinnedIds(query, known);

  // Strangeness stays GLOBAL, and that is not an oversight. It asks whether the record has ever
  // used a word, and the record is all four families. A reservoir teaching the corpus the word
  // "storage" is the corpus learning it.
  const globalIdx = askIndex(items.map((it) => ({ id: it.id, summary: it.text })));
  const strange = strangeness(query, globalIdx);

  const families = new Map();
  for (const it of items) {
    const f = familyOf(it.id);
    if (!families.has(f)) families.set(f, []);
    families.get(f).push(it);
  }

  const lists = [];
  const terms = {};
  const score = {};
  const spare = [];
  for (const [family, group] of families) {
    const bodyIdx = askIndex(group.map((it) => ({ id: it.id, summary: it.text })));
    const headIdx = askIndex(group.map((it) => ({ id: it.id, summary: it.head })));

    // A HIT ON NOTHING BUT COMMON WORDS IS NOT A HIT, AND FUSING IT IS WORSE THAN IGNORING IT.
    //
    // BM25 returns any document with a score above zero, and a word most of the family uses
    // scores just above zero everywhere. Left in, those hits do not merely pad the list, they
    // WIN it. "Erath county" put the one decision naming Erath first in the body list and
    // nowhere in the title list, while twenty eight decisions matched "county" in both, and
    // reciprocal rank fusion correctly preferred what both lists agreed on. It was agreement
    // about a word that means nothing.
    //
    // So each list is cut to the hits carrying at least one word that family does not use
    // everywhere, BEFORE they are fused. The threshold is that family's own, computed by the
    // retriever, so no stopword list has to be maintained as the record grows.
    const evidence = (list) => list.filter((h) => h.terms >= 1);
    const rawBody = askBm25(bodyIdx, query);
    const rawHead = askBm25(headIdx, query);
    const body = evidence(rawBody);
    const head = evidence(rawHead);
    // A FILTER THAT SILENCES A WHOLE FAMILY HAS STOPPED FILTERING AND STARTED DELETING.
    //
    // Its job is to keep a coincidental hit on a common word from WINNING the fusion, and
    // within one family that judgement is sound. It has one blind spot, which is a question
    // whose every word is that family's own boilerplate. "Data centers" is two words and the
    // decisions family uses both of them in nineteen decisions, so both fall under the
    // informativeness floor, so no decision carries a single informative term, so the family
    // returns nothing at all for the question it is best placed to answer.
    //
    // The unfiltered order is kept for that case only. It is never fused and never competes,
    // and it is drawn on by the floor below, which only runs when nothing anywhere corroborated
    // and the question used no word the record has never heard.
    const mute = !body.length && !head.length && (rawBody.length || rawHead.length);

    // Corroboration is a fact about the match, so it is read off the lists rather than off the
    // fused order, which has thrown the term counts away along with the magnitudes.
    for (const h of [...body, ...head]) {
      terms[h.id] = Math.max(terms[h.id] || 0, h.terms);
    }

    const fusedRows = askFuse([body, head]);
    for (const r of fusedRows) score[r.id] = r.score;
    const fused = fusedRows.map((r) => r.id);
    const strong = fused.filter((id) => (terms[id] || 0) >= need);
    const share = breadth
      ? (BREADTH_SHARE[family] ?? BREADTH_DEFAULT)
      : (SHARE[family] ?? SHARE_DEFAULT);
    lists.push({ family, take: strong.slice(0, share), strong, fused,
                 affinity: affinity(query, group, globalIdx, items.length),
                 muted: mute ? askFuse([rawBody, rawHead]).map((r) => r.id) : [] });
    // WHAT A FAMILY DID NOT USE GOES BACK IN THE POT. A question about one decision should
    // still get six decisions, and it would get four if a share nothing matched were simply
    // lost. The leftovers are queued in each family's own rank order and drawn on below only
    // after every family has had its share.
    spare.push(...strong.slice(share));
  }

  const chosen = [];
  const push = (id) => { if (id && !chosen.includes(id)) chosen.push(id); };
  pinned.forEach(push);

  // BY EVIDENCE, NOT BY FAMILY ORDER, and it was by family order and that was a real bug.
  //
  // Each family kept its share and then they were interleaved in the order the families
  // happened to be built, which is the decisions first because that is the order the pack
  // writes them. So slot one went to a decision on every question that matched one at all,
  // whatever the question was about. "Bexar county construction" put the county's construction
  // block first 4.9 percent of the time. It was IN the slice almost always, which is why the
  // decisions-only gold set never saw this, and it was almost never the thing the model read
  // first.
  //
  // Reciprocal rank fusion scores are 1/(k+rank) and carry no magnitude from the BM25 pass
  // underneath, which is the whole reason this file fuses instead of adding. That makes them
  // comparable ACROSS families, where the BM25 scores are not. An item its family ranked in
  // both the body view and the head view scores about twice one ranked in a single view, so
  // ordering by that score puts the block with two kinds of evidence ahead of the block with
  // one, whatever family either came from. Corroborating term count breaks a tie, since it
  // counts words of the question and means the same thing everywhere.
  // ROUND ROBIN ACROSS FAMILIES, THE FAMILY THIS QUESTION IS MOST ABOUT GOING FIRST.
  //
  // Round robin rather than one sorted list, because the reciprocal rank scores are 1/(k+rank)
  // and every family's best hit therefore ties with every other family's best hit. Sorting on
  // a tie is sorting on nothing, and what broke it in practice was the order the families were
  // built in, which is the decisions first because that is the order the pack writes them.
  //
  // Affinity orders the families and the within-family rank orders each family's own entries,
  // so the block most likely to answer leads and the rest of the slice still spans everything
  // that matched. A question that names no family strongly leaves the affinities close and the
  // fused score breaks the tie, which is the old behaviour and the right one there.
  const ordered = [...lists].sort((a, b) => (b.affinity - a.affinity)
    || ((score[b.take[0]] || 0) - (score[a.take[0]] || 0))
    || (a.family < b.family ? -1 : 1));
  const depth = Math.max(0, ...ordered.map((l) => l.take.length));
  for (let i = 0; i < depth; i++) {
    for (const l of ordered) if (l.take[i]) push(l.take[i]);
  }
  spare.slice(0, Math.max(0, want - chosen.length)).forEach(push);

  const corroborated = lists.reduce((n, l) => n + l.strong.length, 0);
  const ranked = lists.reduce((n, l) => n + l.fused.length, 0);

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
  //
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
  //
  // THE FLOOR IS DEPTH FIRST AND THEN ONE SEAT EACH, and it was tried the other way round.
  //
  // Depth is what a county question needs. "Erath county" corroborates nowhere, lands here, and
  // wants the three decisions that ranked best, which are three items from ONE family. Handing
  // it one from each family instead cost the county set 40 points of recall in a single run,
  // measured, 100 percent found down to 60.
  //
  // A seat each is what a topic question needs. "Data centers" is two words and both of them
  // are boilerplate inside the two families that should answer it, so nothing anywhere clears
  // the bar and this path decides the whole answer. Filling it depth first handed back three
  // dossiers and no decision, for a record holding nineteen decisions about data centers.
  //
  // Both are right about their own question and neither generalises, so the floor does depth
  // first and then tops up with one representative from every family that matched and was
  // left out. It costs a few hundred characters, because a block outside the decisions is
  // small, and it is the difference between a wide question being answered widely and being
  // answered by whichever family worded things closest.
  //
  // AND THIS PATH IS ORDERED BY AFFINITY TOO, which it was not, and that is where the whole
  // 4.9 percent lived. "Bexar county construction" corroborates NOWHERE, because within each
  // family the only informative word left is "bexar" and one word does not clear the bar, so
  // every family's strong list is empty and this floor decides the entire answer. It was
  // filling depth first from the families in build order, which is the decisions, so the
  // county's own construction block came fifth on a question naming it twice.
  if (chosen.length < FLOOR_N && strange.unknown === 0) {
    const weak = [...lists]
      .sort((a, b) => (b.affinity - a.affinity) || (a.family < b.family ? -1 : 1))
      .map((l) => (l.fused.length ? l.fused : l.muted)
        .filter((id) => !l.strong.includes(id)));
    outer:
    for (let i = 0; i < FLOOR_DEPTH; i++) {
      for (const w of weak) {
        if (chosen.length >= FLOOR_N) break outer;
        if (w[i]) push(w[i]);
      }
    }
    const seated = new Set(chosen.map(familyOf));
    for (const w of weak) {
      if (w.length && !seated.has(familyOf(w[0]))) {
        seated.add(familyOf(w[0]));
        push(w[0]);
      }
    }
  }

  return { chosen: chosen.slice(0, Math.max(want, pinned.length)),
           corroborated, ranked, pinned, strange };
}

const SLICE_HEAD =
  "WHAT IS MOST LIKELY TO ANSWER THIS QUESTION, in full. It may be decisions or data center " +
  "dossiers or a county's construction or reservoirs. It is often several of those at once. " +
  "A question about a place is usually about more than one of them. The index above lists " +
  "everything the record holds and this is a slice of it. Something indexed above and absent " +
  "here is still real and still citable. Nothing about it beyond its index line is known to " +
  "you. Cite it and say what its line says and stop there.";

const NO_SLICE =
  "NOTHING MATCHES THIS QUESTION closely enough to send its full text. The index above is " +
  "the whole record. Answer from the counts and the index. If the record does not carry this " +
  "say so plainly and name what it does carry instead.";

// HOW MANY CANDIDATES GO TO THE RERANKER, and why more than are ever sent.
//
// Retrieval already puts the right block in the candidate set 98.2 percent of the time and
// puts it FIRST 88.8 percent of the time, measured over the whole gold set. The gap is not a
// recall problem and no amount of BM25 tuning closes it, because BM25 is a bag of words and
// the question of which of twenty plausible blocks actually answers a sentence is not a bag of
// words question. Twenty is where the ceiling is: widening past it moves the 98.2 by nothing
// worth paying for.
const RERANK_N = 20;

// THE MODEL THAT DOES IT, and it is on the platform this worker already runs on.
//
// A cross encoder reads the question and one block TOGETHER and scores the pair, which is the
// thing BM25 structurally cannot do. bge-reranker-base is small enough to run at the edge.
//
// IT IS FREE AT THIS VOLUME AND THAT IS CHECKED, not assumed. Cloudflare bills Workers AI in
// neurons, this model costs 283 neurons per million input tokens, and every account gets
// 10,000 neurons a day. A rerank here sends the question plus twenty blocks, on the order of
// 6,000 tokens, so the whole 200 call monthly cap costs under two neurons of the roughly
// 300,000 free ones a month. Cohere's hosted reranker was the other candidate at $2 per
// thousand searches, which is also small, and it loses on being a second vendor, a second key
// and a second thing that can be down.
const RERANK_MODEL = "@cf/baai/bge-reranker-base";

/**
 * Reorder the candidates by reading each one against the question.
 *
 * IT MAY ONLY REORDER AND MAY NEVER DROP. Everything it is given comes back, because the
 * caller has already decided what is affordable and the slice cap decides what fits. A
 * reranker that also filtered would be a second opinion on a question it was not asked, and
 * the one thing this box must never do is answer as though a block it did not send is not
 * there.
 *
 * EVERY FAILURE RETURNS null AND THE ORIGINAL ORDER STANDS. No AI binding, a model error, a
 * timeout, a response shape this does not recognise. The binding in particular is added by
 * hand in the dashboard, the same way this worker is deployed, so the case where it is absent
 * is not exotic, it is what the first paste looks like. The box has to work then, slightly
 * worse, rather than not work.
 */
export async function rerank(query, cands, env) {
  if (!env?.AI?.run || !query || cands.length < 2) return null;
  try {
    const out = await env.AI.run(RERANK_MODEL, {
      query: String(query),
      // THE HEAD AND THE TOP OF THE BODY, AND NOT FOUR THOUSAND CHARACTERS OF IT.
      //
      // This sent up to 4,000 characters per block, so twenty candidates was up to 80,000
      // characters going over the wire and through a model BEFORE the answering call could
      // start. That is latency added to every question, in series, ahead of the part a reader
      // is waiting on, and the ceiling started firing on ordinary questions the day the
      // binding went live.
      //
      // A cross encoder is deciding which of twenty blocks answers a sentence. It does not
      // need the whole block to do that. The head is what the block IS and the first few lines
      // are what it says, which is where a reservoir's percentage and a county's total both
      // sit. Seven hundred characters is about a tenth of the payload and keeps the part that
      // decides.
      contexts: cands.map((c) => ({ text: (c.head + "\n" + c.text).slice(0, 700) })),
      top_k: cands.length,
    });
    const rows = Array.isArray(out) ? out : (out?.response ?? out?.result?.response);
    if (!Array.isArray(rows) || !rows.length) return null;
    const order = [];
    for (const r of rows) {
      const i = typeof r === "number" ? r : r?.id ?? r?.index;
      if (Number.isInteger(i) && i >= 0 && i < cands.length && !order.includes(i)) order.push(i);
    }
    if (!order.length) return null;
    // ANYTHING THE RERANKER DID NOT MENTION KEEPS ITS OLD PLACE AT THE BACK, so a partial
    // response degrades into the retrieval order rather than into a shorter list.
    for (let i = 0; i < cands.length; i++) if (!order.includes(i)) order.push(i);
    return order.map((i) => cands[i].id);
  } catch {
    return null;
  }
}

/**
 * The candidates a rerank should read, in retrieval order.
 *
 * Separate from `assemble` because the rerank is a network call and `assemble` is not, and
 * making the whole assembly async to accommodate one optional step would have rippled through
 * every call site and every test for no gain. The caller does this, awaits the rerank, and
 * hands the result back to `assemble` as an order.
 */
export function candidates(pack, turns, env) {
  const { items } = splitRecord(pack);
  if (!items.length || !pack.index) return [];
  const byId = new Map(items.map((it) => [it.id, it]));
  const query = queryOf(turns);
  // BREADTH MODE IS THE WIDE NET, and asking for twenty without it returned six.
  //
  // `top` caps the result and the per-family shares decide what fills it, so a normal question
  // yields four decisions, two dossiers, one county and one reservoir whatever `top` says.
  // Handing a reranker six candidates and asking it to find the best six is not reranking.
  // Breadth mode already means the thing wanted here, which is a lower corroboration bar and a
  // bigger share for every family, and it exists because survey questions needed exactly this
  // shape. Reusing it beats a second set of numbers that would drift from these.
  const picked = pickItems(query, items, { top: RERANK_N, breadth: true });
  return picked.chosen.map((id) => byId.get(id)).filter(Boolean);
}

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
export function assemble(pack, turns, env, order) {
  const off = String(env?.ASK_RETRIEVAL ?? "").trim().toLowerCase() === "off";
  const { preamble, coreItems, items } = splitRecord(pack);
  const bodies = items.reduce((n, it) => n + it.chars, 0);
  const index = pack.index || "";
  const hasFacilityField = !!String(pack.facility_pack || "").trim();

  // NO INDEX MEANS AN OLDER PACK. A worker deployed ahead of a site rebuild would otherwise
  // send a slice with nothing standing in for the rest, which is the exact failure the index
  // exists to prevent. Send everything instead, and say why in the mode.
  const wholeText = pack.pack + (hasFacilityField && index ? "\n\n" + index : "");
  const sentWholeItems = hasFacilityField ? coreItems : items;
  const sendWhole = (why) => ({
    blocks: [
      { type: "text", text: pack.system },
      { type: "text", text: wholeText, cache_control: { type: "ephemeral" } },
    ],
    mode: `whole (${why})`, chosen: sentWholeItems.map((it) => it.id),
    shown: sentWholeItems.length, of: items.length,
    chars: pack.system.length + wholeText.length,
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
  // WIDE WHEN A RERANKER IS COMING, NARROW WHEN ONE IS NOT. Reranking twenty and keeping six
  // is the whole point, and retrieving twenty with nothing to reorder them would just pay for
  // fourteen bodies nobody asked for.
  const wide = Array.isArray(order) && order.length ? { top: RERANK_N } : {};
  let picked = pickItems(query, items, wide);
  const latest = queryOf(turns, 1);
  if (!picked.chosen.length && latest && latest !== query) {
    const retry = pickItems(latest, items, wide);
    if (retry.chosen.length) picked = retry;
  }
  const byId = new Map(items.map((it) => [it.id, it]));
  // AN ORDER FROM THE RERANKER REPLACES THE RETRIEVAL ORDER AND NOTHING ELSE. It is filtered
  // against what retrieval actually chose, so a reranker returning an id from some other
  // conversation, or a stale one, cannot smuggle a block into the prompt that this question's
  // retrieval never selected.
  const known = new Set(picked.chosen);
  const reranked = Array.isArray(order) && order.length
    ? order.filter((id) => known.has(id) && byId.has(id))
    : null;
  // RERANK TWENTY, SEND THE USUAL NUMBER. The wide candidate set exists so the reranker has
  // something to choose FROM, and sending all of it would be paying for fourteen extra bodies
  // to get a better order on six. The character cap below would not have caught this on its
  // own: twenty blocks is about 54,000 characters against a 60,000 cap, so the slice would
  // have quadrupled and still passed every gate.
  const keep = wantsBreadth(queryOf(turns)) ? BREADTH_N : TOP_N;
  const chosen = reranked && reranked.length
    ? reranked.slice(0, Math.max(keep, picked.pinned.length))
    : picked.chosen;
  const { corroborated, pinned } = picked;

  // THE CAP IS WHAT CUTS TWENTY BACK TO WHAT FITS, and it is already here. A reranked list
  // arrives best first, so taking bodies until the character cap bites keeps the best ones and
  // drops the tail, which is exactly what reranking twenty and sending six means.
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
  const allBodies = pack.pack.length + String(pack.facility_pack || "").length;
  if (assembled >= pack.system.length + allBodies) return sendWhole("slice is no smaller");

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
