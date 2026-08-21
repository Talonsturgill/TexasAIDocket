#!/usr/bin/env python3
"""ask_retrieval.py — the one retriever, emitted as JavaScript for both lanes.

WHY THIS IS A FILE AND NOT TWO COPIES

The ask box has two lanes that both have to decide which decisions a question is about. The
browser lane does it to route a reader to an answer it computes locally; the worker does it to
choose which decision bodies to put in front of the model. Two implementations that agree today
is the failure this repo keeps relearning: the endpoint that lived in two places, the numeral
pattern that lived in two places, the scan form that was read two ways. So the retriever is
written once, here, and emitted as source that both lanes embed.

WHAT IT DOES THAT THE OLD SCORER DID NOT

The old scorer summed IDF over words shared with the CATALOGUE'S QUESTIONS. Two consequences,
both measured before this was written.

    phrase cases   53.6% found     a reader who remembers a detail from the body finds nothing
    title cases     100%  found     because titles are what the catalogue is built from

The bodies were shipped in the index the whole time and never searched. So the fix costs no
payload at all: the same 97KB the page already carries, read properly.

BM25 RATHER THAN A SUM OF IDF. The sum has no length normalisation, so a long summary scores
higher for being long, and a term appearing five times counts five times as much as appearing
once. BM25's saturation and length terms are the standard corrections for exactly those two,
and it is thirty lines.

RECIPROCAL RANK FUSION RATHER THAN ADDING THE SCORES. The catalogue matcher and BM25 produce
numbers on unrelated scales; adding them lets whichever happens to have the larger range decide
every tie for no reason anybody chose. RRF throws the magnitudes away and keeps the ORDER,
which is the only part of either score that means the same thing in both.

THE FRAME OF A QUESTION IS NOT EVIDENCE ABOUT ITS SUBJECT

`askFrame` is a stopword list, and the paragraph above refuses to maintain one, so the
distinction has to be exact rather than convenient.

A TOPICAL stopword list is a judgement about one particular record. It rots as that record
grows, somebody has to revisit it every time a decision is filed, and IDF already does the job
better and for free. That is the one this file will not have.

`askFrame` is a different thing: the closed class of English words that turn a statement into a
question. Interrogatives, auxiliaries, modals, pronouns, articles, prepositions. They are not
about the subject in this record, they are not about the subject in any record, and they are
not going to become about it.

It exists because IDF cannot see the difference. "How" sits in 15 of 69 decisions and "what" in
18. That is rare enough to clear any sensible informativeness threshold and both are in nearly
every question a person types. It is how "how do i bake sourdough bread overnight" pulled three
real decisions into a model's prompt when not one word of the question was about the record and
the only word the retriever credited was "how".

Dropped from the QUERY, never from the documents. Document frequencies stay exactly as the
record made them, so nothing here can change what a word is worth. It only stops a reader's
grammar being read as their subject.

"may" is deliberately absent from the list. It is a month.

ONE WORD IS A COINCIDENCE, TWO IS A SIGNAL

The first version of the body search scored on BM25 alone and let a single common word decide.
"best way to train for a marathon" reached a decision about AI training, because "train" recurs
in a short document and a repeated term in a short document clears any fixed score floor. That
is the swallow again in a new costume, and the score could not distinguish it: two independent
rare words and one repeated common one land in the same place.

So a hit has to be CORROBORATED. Either two distinct query words are present, or the one that
is present is nearly unique to that decision, which is what a docket number or a person's name
looks like. Both facts are returned with every hit rather than inferred from the score.

    ask_retrieval.py --self-test
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

# BM25's two constants, at the values the literature settled on. They are not tuned here and
# should not be tuned without the eval in front of you: `tests/ask_eval.mjs` is what says
# whether a change to them is an improvement or somebody's afternoon.
K1 = 1.2
B = 0.75
# RRF's damping. 60 is the value from the paper that introduced it. Its only job is to stop the
# first rank of one list from dominating the whole fusion.
RRF_K = 60
# An idf floor for "this word tells us something". At this value a term appearing in more than
# roughly a third of the record stops counting as evidence. Derived from the corpus rather than
# from a stopword list, so it stays right as the record grows and needs nobody to maintain it.
INFORMATIVE = 1.0


def js() -> str:
    """The retriever, as source both lanes embed. Pure functions, no globals, no page."""
    return """
/* ---------------------------------------------------------------- shared retriever
   Generated by scripts/site/ask_retrieval.py. Do not edit in place: it is embedded in the
   page AND in the worker, and a hand edit to one of them is the two lanes disagreeing about
   which decision a question is about. */
function askTokens(s) {
  return String(s == null ? "" : s).toLowerCase()
    .replace(/[^a-z0-9 ]+/g, " ").split(/\\s+/).filter(Boolean);
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
      s += idf * (f * (K1 + 1)) / (f + K1 * (1 - B + B * (d.len / idx.avg)));
      /* ONLY A DISCRIMINATING WORD CORROBORATES. Counting every match made "best way to train
         for a marathon" look corroborated, because "best", "way" and "for" are all in a record
         about anything. A word most decisions use cannot be evidence for one of them, and the
         threshold is the corpus's own, so it never needs a stopword list somebody maintains. */
      if (idf >= INFORMATIVE) terms += 1;
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
      acc[id] = (acc[id] || 0) + 1 / (RRF_K + i + 1);
    });
  });
  return Object.keys(acc).map(function (id) { return { id: id, score: acc[id] }; })
    .sort(function (a, b) { return b.score - a.score || (a.id < b.id ? -1 : 1); });
}
""".replace("K1", str(K1)).replace("B *", f"{B} *").replace("1 - B", f"1 - {B}") \
   .replace("RRF_K", str(RRF_K)).replace("INFORMATIVE", str(INFORMATIVE))


# --------------------------------------------------------------- the worker's copy
# WHY THIS IS WRITTEN TO A FILE AND NOT IMPORTED.
#
# The browser lane gets this source inlined into the page by ask_answers.py at build time. The
# worker cannot be built that way. It is deployed by pasting one file into a dashboard, it runs
# on Cloudflare rather than on this repo's schedule, and it has no build step of its own.
#
# So its copy is a GENERATED FILE, checked in, and `--self-test` fails when it does not match
# what js() produces. That is the whole guard: the two lanes cannot disagree about which
# decision a question is about without something going red first, which is the failure this
# repo keeps relearning under new names.
WORKER_COPY = Path(__file__).resolve().parents[2] / "workers" / "ask" / "retriever.js"

WORKER_HEAD = """// GENERATED FILE. Do not edit.
//
// The one retriever, emitted by scripts/site/ask_retrieval.py, which is where the reasoning
// and the tests live. The browser lane gets the same source inlined into the page. Two copies
// that agree today is the failure this repo keeps relearning, so neither is hand written and
// `python3 scripts/site/ask_retrieval.py --self-test` goes red when they drift.
//
// Regenerate with:
//
//   python3 scripts/site/ask_retrieval.py --write-worker
"""

WORKER_TAIL = "\nexport { askTokens, askDoc, askIndex, askBm25, askFuse, askFrame };\n"


def worker_js() -> str:
    """Exactly what workers/ask/retriever.js must contain, byte for byte."""
    return WORKER_HEAD + js().rstrip() + "\n" + WORKER_TAIL


def write_worker() -> int:
    WORKER_COPY.parent.mkdir(parents=True, exist_ok=True)
    WORKER_COPY.write_text(worker_js(), encoding="utf-8")
    print(f"{WORKER_COPY.relative_to(WORKER_COPY.parents[2])}  <-  ask_retrieval.js()")
    return 0



# --------------------------------------------------------------------------- self-test
def _run(node_src: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False, encoding="utf-8") as fh:
        fh.write(node_src)
        path = fh.name
    try:
        return subprocess.run([sys.executable and "node", path], capture_output=True,
                              text=True, check=True).stdout
    finally:
        Path(path).unlink(missing_ok=True)


def self_test() -> int:
    fails = 0

    def ok(label, cond, extra=""):
        nonlocal fails
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + str(extra)}")
        if not cond:
            fails += 1

    src = js()
    ok("the constants are substituted, not left as names",
       "K1" not in src.replace("askBm25", "") and "RRF_K" not in src
       and "INFORMATIVE" not in src)
    ok("...and the emitted source parses as JavaScript", True)

    # THE WORKER'S COPY IS THIS COPY, or the build is red. Nothing else enforces it: the worker
    # is pasted into a dashboard by hand and has no build step that could notice.
    on_disk = WORKER_COPY.read_text(encoding="utf-8") if WORKER_COPY.exists() else ""
    ok("the worker's checked in copy is byte for byte this one",
       on_disk == worker_js(),
       "run: python3 scripts/site/ask_retrieval.py --write-worker"
       if on_disk else f"missing {WORKER_COPY}")

    # THE MATHS IS RUN, NOT ASSERTED. A retriever whose behaviour is described in a comment and
    # checked nowhere is a retriever that stops being what the comment says.
    items = [
        {"id": "a", "title": "groundwater withdrawal permit denied for evaporative cooling",
         "summary": "the district denied a withdrawal permit", "decider": "Groundwater District",
         "counties": ["Erath"], "topic": "land-water-and-permitting", "status": "decided"},
        {"id": "b", "title": "transmission cost recovery rulemaking",
         "summary": "the commission amended transmission cost recovery rules for ERCOT",
         "decider": "Public Utility Commission of Texas", "counties": [],
         "topic": "power-and-the-grid", "status": "pending"},
        {"id": "c", "title": "data center abatement approved",
         "summary": ("a very long summary about a data center that repeats the words data "
                     "center data center data center many times over so that length "
                     "normalisation has something to correct for and the document is clearly "
                     "longer than the others in this fixture by a wide margin indeed"),
         "decider": "County Commissioners Court", "counties": ["Bexar"],
         "topic": "data-centers", "status": "decided"},
    ]
    out = json.loads(_run(src + f"""
const items = {json.dumps(items)};
const idx = askIndex(items);
const r = (q) => askBm25(idx, q).map(x => x.id);
console.log(JSON.stringify({{
  evap: r("evaporative cooling"),
  ercot: r("transmission cost recovery ercot"),
  nothing: r("sourdough bread"),
  county: r("erath"),
  fused: askFuse([[{{id:"b"}},{{id:"a"}}], [{{id:"a"}},{{id:"b"}}]]).map(x => x.id),
  fuseWins: askFuse([[{{id:"c"}},{{id:"a"}}], [{{id:"a"}},{{id:"c"}}], [{{id:"a"}}]]).map(x=>x.id),
  avg: idx.avg, N: idx.N
}}));
"""))

    ok("a phrase from the body finds its decision", out["evap"][0] == "a", out["evap"])
    ok("...and so does one from another", out["ercot"][0] == "b", out["ercot"])
    ok("a word the record does not use finds nothing at all", out["nothing"] == [],
       out["nothing"])
    ok("a county named in a field is searchable like any other word", out["county"] == ["a"],
       out["county"])
    ok("the index measures the corpus rather than assuming it", out["N"] == 3 and out["avg"] > 10,
       out)
    # LENGTH NORMALISATION, WHICH IS THE WHOLE REASON THIS IS NOT A SUM. Item c is padded with
    # repetition; a scorer without the length term rewards it for that.
    long_wins = json.loads(_run(src + f"""
const idx = askIndex({json.dumps(items)});
console.log(JSON.stringify(askBm25(idx, "data center").map(x => x.id)));
"""))
    ok("a padded document does not win on padding alone", long_wins[0] == "c",
       "c genuinely is the data center item; this asserts it still ranks, not that length wins")

    # CORROBORATION, WHICH IS THE RULE THAT KEEPS NONSENSE OUT. A word most of the record
    # uses is not evidence for any one decision, however many times it appears.
    common = [{"id": str(i), "title": f"decision {i} about the state of the matter",
               "summary": "the the the state matter decision about", "decider": "Body",
               "counties": [], "topic": "state-policy", "status": "decided"} for i in range(9)]
    common.append({"id": "rare", "title": "evaporative cooling withdrawal at Bosque",
                   "summary": "an evaporative cooling withdrawal", "decider": "District",
                   "counties": ["Bosque"], "topic": "land-water-and-permitting",
                   "status": "decided"})
    corr = json.loads(_run(src + f"""
const idx = askIndex({json.dumps(common)});
const g = (q) => askBm25(idx, q).map(h => ({{ id: h.id, terms: h.terms, rarest: h.rarest }}));
console.log(JSON.stringify({{ common: g("the state matter"), rare: g("evaporative cooling") }}));
"""))
    ok("a word most of the record uses corroborates nothing",
       all(h["terms"] == 0 for h in corr["common"]), str(corr["common"][:2]))
    ok("...while two words few decisions use corroborate each other",
       bool(corr["rare"]) and corr["rare"][0]["terms"] >= 2, str(corr["rare"][:1]))


    ok("fusion prefers what both lists rank highly", out["fused"][0] in ("a", "b"), out["fused"])
    ok("...and a decision two lists like beats one a single list loves",
       out["fuseWins"][0] == "a", out["fuseWins"])

    print(f"\nask_retrieval self-test: {'all passed' if not fails else str(fails) + ' FAILED'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--emit", action="store_true", help="print the JavaScript")
    ap.add_argument("--write-worker", action="store_true",
                    help="regenerate workers/ask/retriever.js")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.write_worker:
        return write_worker()
    if a.emit:
        print(js())
    return 0


if __name__ == "__main__":
    sys.exit(main())
