#!/usr/bin/env python3
"""compute.py — every numeral and every measurable length in carousel no. 21.

THE LAW. No numeral this project publishes is typed by a person or produced by a language model.
Arithmetic, unit conversion, percentages, ratios, deltas, rankings, date maths and rounding all
happen here, and the frames read `computed.json`.

THE INSTINCT, which is broader than the law. Any position or length a reader could MEASURE goes
through here, not only the ones that carry a printed number.

THE DEBT THIS FILE PAYS, inherited from carousel no. 19 and no. 20. Two frames of no. 19 held
hand-synced literals that had drifted from their compute.py and four scoring panels did not see
it, because a literal that is merely WRONG looks exactly like a literal that is right. No frame
in this deck retypes a value: `inject_computed.py` writes the block below into each frame in
place of a marker, so there is no number in a frame to go stale.

WHAT IS DIFFERENT ABOUT THIS DECK. Its story is a COUNT, and the fact checker refused to supply
one. Its words:

    "The count is not in the source and a count produced by a language model is forbidden by the
     compute-not-generate law. Have code grep the PDF text if you want the figure."

So this file greps. Every count below is taken either out of a verified claim quote or out of the
committed source snapshots in `sources/`, which are the bytes actually fetched on 2026-09-11.
Nothing here is read off a screen and retyped.
"""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOC = json.loads((HERE / "claims.json").read_text(encoding="utf-8"))
CLAIMS = {c["id"]: c for c in DOC["claims"]}
SOURCES = HERE / "sources"

ATTACHMENT = "sboe-113-26-attachment.txt"
ITEM = "sboe-item3-second-reading.txt"
RELEASE = "sboe-news-release.txt"


def q(cid: str) -> str:
    """The verified quote for a claim, whitespace normalised. Raises on an unknown id."""
    return re.sub(r"\s+", " ", CLAIMS[cid]["quote"]).strip()


def pull(cid: str, pattern: str, label: str) -> str:
    """Lift a substring out of a claim's own quote. Raises rather than falling back."""
    m = re.search(pattern, q(cid))
    if not m:
        raise SystemExit(
            f"compute.py: {label} is no longer in {cid}'s quote. The quote reads:\n  {q(cid)}\n"
            f"Fix the claim or fix this pattern. Do NOT retype the value here.")
    return m.group(1)


def snapshot(name: str) -> str:
    """The bytes fetched on 2026-09-11, normalised the one way every count below uses.

    Line-break hyphenation is repaired first: the attachment's text layer splits 'artificial /
    intelligence' across a page break and drops the hyphen in 'decision- / making'. A count taken
    before that repair undercounts, which is exactly the shape of error this file exists to stop.
    """
    raw = (SOURCES / name).read_text(encoding="utf-8", errors="replace")
    raw = re.sub(r"Page \d+ of \d+", " ", raw)
    raw = re.sub(r"-\s*\n\s*", "", raw)          # hyphen split across a line
    return re.sub(r"\s+", " ", raw).strip()


ATT_TEXT = snapshot(ATTACHMENT)
ITEM_TEXT = snapshot(ITEM)
REL_TEXT = snapshot(RELEASE)


def occurrences(text: str, term: str) -> int:
    return len(re.findall(re.escape(term), text, flags=re.I))


# ----------------------------------------------------------------- the figures the source prints

# The credit value, as the course text's own words. Kept as a STRING because the document writes
# it in words and a frame that printed 0.5 would be quoting nobody.
CREDIT_WORDS = pull("c13", r"awarded (one-half credit) for successful completion", "the credit value")

# The effective date rule, lifted out of the motion rather than retyped beside it.
EFFECTIVE_DAYS = int(pull("c3", r"effective date of (\d+) days after filing", "the effective-date interval"))

# The implementation school year, out of the course text's own subsection (a).
_YEAR_SPAN = pull("c12", r"beginning with the (\d{4}-\d{4}) school year", "the implementation school year")
YEAR_FROM, YEAR_TO = (int(v) for v in _YEAR_SPAN.split("-"))
# House style: a range reads "X to Y" and never "X-Y". Built here so no frame types the dash.
SCHOOL_YEAR = f"{YEAR_FROM} to {YEAR_TO}"

# The board item's own date line, parsed rather than read off a calendar.
_ITEM_DATE = pull("c5", r"^([A-Z][a-z]+ \d{1,2}, \d{4}) COMMITTEE", "the item's date line")
ITEM_DATE = dt.datetime.strptime(_ITEM_DATE, "%B %d, %Y").date()


def ordinal(n: int) -> str:
    return f"{n}{'th' if 11 <= n % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


# House style: month first, with the ordinal. Never a bare "September 4".
ITEM_DATE_LONG = f"{ITEM_DATE.strftime('%B')} {ordinal(ITEM_DATE.day)}, {ITEM_DATE.year}"
ITEM_DATE_SHORT = f"{ITEM_DATE.strftime('%B').upper()} {ordinal(ITEM_DATE.day).upper()}"

# The bill the rule implements, out of the item's own summary.
HOUSE_BILL = pull("c6", r"House Bill \(HB\) (\d+), 89th Texas Legislature", "the house bill number")
LEGISLATURE = pull("c6", r"(\d+)th Texas Legislature", "the legislature ordinal")
SESSION_YEAR = int(pull("c6", r"Texas Legislature, Regular Session, (\d{4})", "the session year"))

# ------------------------------------------------------------------- the counts, all from bytes

# THE THREE EXPECTATIONS. Not typed. A claim counts as carrying machine language when its own
# verified quote contains one of these stems, and the set is declared here so it can be argued
# with rather than assumed.
MACHINE_STEMS = ("artificial intelligence", "algorithm", "automated", "robot-advisor")
EXPECTATION_CLAIMS = ("c14", "c15", "c16")

MACHINE_EXPECTATIONS = sorted(
    cid for cid in EXPECTATION_CLAIMS
    if any(s in q(cid).lower() for s in MACHINE_STEMS))
N_MACHINE_EXPECTATIONS = len(MACHINE_EXPECTATIONS)

# The chapters they sit in, lifted out of each claim's own subsection identifier.
CHAPTERS = sorted({int(re.match(r"\(d\)\((\d+)\)", CLAIMS[cid]["subsection"]).group(1))
                   for cid in MACHINE_EXPECTATIONS})
N_CHAPTERS = len(CHAPTERS)

# Which of the three actually says "artificial intelligence", which is the distinction the fact
# checker insisted on and the reason no frame may call all three AI expectations.
AI_WORDED = [cid for cid in MACHINE_EXPECTATIONS if "artificial intelligence" in q(cid).lower()]
N_AI_WORDED = len(AI_WORDED)

# Term counts over the whole eight page course text, not over the part the deck quotes.
DOC_TERMS = {t: occurrences(ATT_TEXT, t)
             for t in ("artificial intelligence", "artificial", "algorithm", "automated",
                       "robot", "machine learning")}

# The knowledge statements the course text declares, counted from its own numbering. The document
# runs (1) to (10) and skips (6), so the COUNT and the HIGHEST NUMBER are different figures and
# the frames must not confuse them.
# THE CHARACTER CLASS DROPPED A WHOLE CHAPTER, and the frame built on it published a hole in
# the standards that does not exist. `(6) Budgeting: Spending and Planning.` carries a COLON,
# which `[A-Za-z ,\-&]` excluded, so the heading never matched, (6) never entered this list, and
# `knowledge_missing` came back as [6]. A review bot read the committed snapshot and found it.
#
# The lesson is not "add a colon to the class". It is that an enumeration parsed out of prose
# must be VALIDATED AGAINST ITS OWN SEQUENCE rather than trusted, because a regex that misses one
# heading looks exactly like a document that skips one number. The assertion below is what makes
# the difference visible: a gap in a printed sequence is now a thing this file refuses to report
# without saying so, instead of a finding it hands to a frame.
KNOWLEDGE_NUMBERS = sorted({int(n) for n, _ in re.findall(
    r"\((\d+)\)\s+([A-Z][^()]{8,120}?)\.\s*The student", ATT_TEXT)})
N_KNOWLEDGE = len(KNOWLEDGE_NUMBERS)
KNOWLEDGE_HIGHEST = max(KNOWLEDGE_NUMBERS) if KNOWLEDGE_NUMBERS else 0
KNOWLEDGE_MISSING = [n for n in range(1, KNOWLEDGE_HIGHEST + 1) if n not in KNOWLEDGE_NUMBERS]

# A GAP IS EXTRAORDINARY AND A PARSER MISS IS ORDINARY, so a reported gap has to be corroborated
# before any frame is allowed to draw it. The document prints each missing number somewhere even
# when this pattern does not match its heading, so if the bare "(N)" token IS in the text, the gap
# is this parser's and not the document's, and that is a defect rather than a finding.
_FALSE_GAPS = [n for n in KNOWLEDGE_MISSING if re.search(r"\(%d\)\s+[A-Z]" % n, ATT_TEXT)]
if _FALSE_GAPS:
    raise SystemExit(
        "compute.py: the heading parser reports chapter(s) %s missing, but the document prints "
        "them. That is this parser failing to match a heading, not the standard skipping a "
        "number, and a frame built on it would publish a hole that does not exist. Fix the "
        "pattern. Do NOT publish the gap." % _FALSE_GAPS)

# THE DOCUMENT'S OWN SIZE, measured off the fetched file rather than read off a screen. The fact
# checker refused to give a page count and was right to: it observed one and a model-observed
# count is a model-produced numeral. A count taken by code from the bytes is a different thing.
#
# IT IS READ FROM A COMMITTED MANIFEST RATHER THAN FROM THE PDF, and that is the repair for a
# real defect a review bot found. The first version read `HERE/tmp/sboe_pfl.pdf`, which lives
# under `out/` and is gitignored, so on the fresh checkout this run's handoff is written for it
# would have silently become None and slide 3 would have divided by a null page count and drawn
# no page boxes at all. The count is measured by code at fetch time, written into
# `sources/MANIFEST.json`, and committed beside the snapshot it describes.
#
# It RAISES rather than defaulting, because a missing provenance file is a broken run and an
# unusable value that renders is worse than one that stops.
_MANIFEST = SOURCES / "MANIFEST.json"
if not _MANIFEST.exists():
    raise SystemExit(f"compute.py: {_MANIFEST} is missing. The page count is measured at fetch "
                     f"time and committed; it is not re-derived from a file out/ throws away.")
_MAN = json.loads(_MANIFEST.read_text(encoding="utf-8"))["snapshots"]
if "pdf_pages" not in _MAN.get(ATTACHMENT, {}):
    raise SystemExit(f"compute.py: {_MANIFEST} carries no pdf_pages for {ATTACHMENT}. A frame "
                     f"reads this; it may not be None.")
PAGE_COUNT = int(_MAN[ATTACHMENT]["pdf_pages"])

# Words in the whole standard, counted the one way the stipple field on frame 3 draws them.
DOC_WORDS = len(re.findall(r"[A-Za-z][A-Za-z'-]*", ATT_TEXT))

# The machine's whole footprint in the document. Four TERMS, and the number of TIMES they occur,
# which are different figures and no frame may confuse them. "artificial intelligence" is two
# words and one term, which is exactly why "five words" would have been wrong.
FOOTPRINT_TERMS = ("artificial intelligence", "algorithm", "automated", "robot")
FOOTPRINT = {t: occurrences(ATT_TEXT, t) for t in FOOTPRINT_TERMS}
N_FOOTPRINT_TERMS = len([t for t, n in FOOTPRINT.items() if n])
N_FOOTPRINT_OCCURRENCES = sum(FOOTPRINT.values())
FOOTPRINT_SHARE_PER_10K = (round(N_FOOTPRINT_OCCURRENCES / DOC_WORDS * 10000, 1)
                           if DOC_WORDS else None)

# WHERE THE MACHINE ACTUALLY SITS IN THE DOCUMENT. Frame 3 lifts five points out of a field of
# one dot per word, and a point placed where it looked good would be a drawing about nothing. Each
# occurrence's position is its own word index over the document's word count, so the five marks
# land where the terms land.
_WORDS = [m for m in re.finditer(r"[A-Za-z][A-Za-z'-]*", ATT_TEXT)]
def _word_index_at(char_pos: int) -> int:
    lo, hi = 0, len(_WORDS)
    while lo < hi:
        mid = (lo + hi) // 2
        if _WORDS[mid].start() < char_pos:
            lo = mid + 1
        else:
            hi = mid
    return lo

FOOTPRINT_POSITIONS = []
for _t in FOOTPRINT_TERMS:
    for _m in re.finditer(re.escape(_t), ATT_TEXT, flags=re.I):
        _wi = _word_index_at(_m.start())
        FOOTPRINT_POSITIONS.append({
            "term": _t,
            "word_index": _wi,
            "fraction": round(_wi / DOC_WORDS, 5) if DOC_WORDS else None,
        })
FOOTPRINT_POSITIONS.sort(key=lambda d: d["word_index"])


# WHAT THE CLAUSE SENDS A STUDENT TO, AND WHAT IT SENDS THEM WITH, both parsed out of c14's own
# quote rather than transcribed beside it. Frame 4 draws one lit slot per evaluation and one line
# per instrument, so both counts are assertions the frame makes in its largest elements. The first
# build hand-typed the list and counted the transcription, which is the defect a review bot named:
# omitting, duplicating or keeping a stale item would have rendered and passed.
def _split_list(fragment: str) -> list[str]:
    """A comma list ending 'and X', with the Oxford comma the document uses."""
    parts = [p.strip() for p in re.split(r",\s*", fragment) if p.strip()]
    if parts:
        parts[-1] = re.sub(r"^and\s+", "", parts[-1]).strip()
    return [p for p in parts if p]

_C14 = q("c14")
_m = re.search(r"using (.+?) to evaluate (.+?)\s*\(E, S\);", _C14)
if not _m:
    raise SystemExit("compute.py: c14's quote no longer has the shape 'using ... to evaluate "
                     "... (E, S);'. Frame 4 draws one slot per evaluation, so this may not be "
                     "guessed at. The quote reads:\n  " + _C14)
INSTRUMENTS = _split_list(_m.group(1))
EVALUATIONS = _split_list(_m.group(2))
N_INSTRUMENTS = len(INSTRUMENTS)
N_EVALUATIONS = len(EVALUATIONS)

# THE ABSENCE, counted rather than asserted. Every one of these must be zero for the deck's
# counter-image frame to stand, and this file raises if any is not.
ABSENCE_TERMS = ("artificial", "algorithm", "automated", "machine learning", "technolog")
RELEASE_HITS = {t: occurrences(REL_TEXT, t) for t in ABSENCE_TERMS}
RELEASE_HITS["AI"] = len(re.findall(r"\bAI\b", REL_TEXT))
if any(RELEASE_HITS.values()):
    raise SystemExit(
        "compute.py: the release snapshot is no longer silent about technology. "
        f"{ {k: v for k, v in RELEASE_HITS.items() if v} }. The deck's counter-image frame rests "
        "on this absence and must be rebuilt rather than relabelled.")
N_RELEASE_HITS = sum(RELEASE_HITS.values())

# The release's own summary of the standards, and its length, which is the whole counter-image.
RELEASE_SUMMARY = q("c22")
RELEASE_SUMMARY_WORDS = len(RELEASE_SUMMARY.split())
# The two words the three expectations are inside of.
AND_MORE = pull("c22", r"(and more)\.$", "the release's closing phrase")

# ------------------------------------------------------------------------------- frame geometry

# THE COLUMN RULE. The three chapter cards on frame 5 are laid out from one gutter constant so no
# frame types an x. Width is the content box, not the canvas.
CANVAS_W, CANVAS_H = 1080, 1350
MARGIN = 80
CONTENT_W = CANVAS_W - 2 * MARGIN
GUTTER = 28
CARD_W = (CONTENT_W - GUTTER * (N_CHAPTERS - 1)) // N_CHAPTERS
CARD_X = [MARGIN + i * (CARD_W + GUTTER) for i in range(N_CHAPTERS)]

# THE SPINE. Frame 4 draws every knowledge statement the document declares as one row, so the row
# pitch is a function of the count rather than a number somebody liked.
SPINE_TOP, SPINE_BOTTOM = 330, 1140
SPINE_PITCH = (SPINE_BOTTOM - SPINE_TOP) / (KNOWLEDGE_HIGHEST - 1) if KNOWLEDGE_HIGHEST > 1 else 0
SPINE_Y = {n: round(SPINE_TOP + SPINE_PITCH * (n - 1), 2) for n in range(1, KNOWLEDGE_HIGHEST + 1)}
SPINE_MARKED = [SPINE_Y[n] for n in CHAPTERS]

OUT = {
    "run": "2026-09-11",
    "deck": 21,
    "docket_item": DOC["docket_item"],

    "credit_words": CREDIT_WORDS,
    "effective_days": EFFECTIVE_DAYS,
    "school_year": SCHOOL_YEAR,
    "school_year_from": YEAR_FROM,
    "school_year_to": YEAR_TO,
    "item_date_iso": ITEM_DATE.isoformat(),
    "item_date_long": ITEM_DATE_LONG,
    "item_date_short": ITEM_DATE_SHORT,
    "house_bill": HOUSE_BILL,
    "legislature": LEGISLATURE,
    "session_year": SESSION_YEAR,

    "machine_expectations": MACHINE_EXPECTATIONS,
    "n_machine_expectations": N_MACHINE_EXPECTATIONS,
    "chapters": CHAPTERS,
    "n_chapters": N_CHAPTERS,
    "ai_worded": AI_WORDED,
    "n_ai_worded": N_AI_WORDED,
    "machine_stems": list(MACHINE_STEMS),

    "doc_terms": DOC_TERMS,
    "page_count": PAGE_COUNT,
    "instruments": INSTRUMENTS,
    "n_instruments": N_INSTRUMENTS,
    "evaluations": EVALUATIONS,
    "n_evaluations": N_EVALUATIONS,
    "doc_words": DOC_WORDS,
    "footprint": FOOTPRINT,
    "footprint_terms": list(FOOTPRINT_TERMS),
    "n_footprint_terms": N_FOOTPRINT_TERMS,
    "n_footprint_occurrences": N_FOOTPRINT_OCCURRENCES,
    "footprint_share_per_10k": FOOTPRINT_SHARE_PER_10K,
    "footprint_positions": FOOTPRINT_POSITIONS,
    "knowledge_numbers": KNOWLEDGE_NUMBERS,
    "n_knowledge": N_KNOWLEDGE,
    "knowledge_highest": KNOWLEDGE_HIGHEST,
    "knowledge_missing": KNOWLEDGE_MISSING,

    "release_hits": RELEASE_HITS,
    "n_release_hits": N_RELEASE_HITS,
    "release_summary_words": RELEASE_SUMMARY_WORDS,
    "and_more": AND_MORE,

    "canvas_w": CANVAS_W, "canvas_h": CANVAS_H, "margin": MARGIN,
    "content_w": CONTENT_W, "gutter": GUTTER, "card_w": CARD_W, "card_x": CARD_X,
    "spine_top": SPINE_TOP, "spine_bottom": SPINE_BOTTOM,
    "spine_pitch": round(SPINE_PITCH, 3), "spine_y": SPINE_Y, "spine_marked": SPINE_MARKED,
}

if __name__ == "__main__":
    (HERE / "computed.json").write_text(json.dumps(OUT, indent=1) + "\n", encoding="utf-8")
    print(f"compute.py: wrote computed.json")
    print(f"  machine expectations {N_MACHINE_EXPECTATIONS} {MACHINE_EXPECTATIONS}"
          f" in chapters {CHAPTERS}")
    print(f"  of those, {N_AI_WORDED} says 'artificial intelligence' in as many words: {AI_WORDED}")
    print(f"  course text term counts {DOC_TERMS}")
    print("  the five marks land at word " + ", ".join(str(d["word_index"]) for d in FOOTPRINT_POSITIONS))
    print(f"  document {PAGE_COUNT} page(s), {DOC_WORDS} words; the machine's footprint is "
          f"{N_FOOTPRINT_OCCURRENCES} occurrence(s) of {N_FOOTPRINT_TERMS} term(s) {FOOTPRINT}")
    print(f"  knowledge statements {N_KNOWLEDGE}, numbered to {KNOWLEDGE_HIGHEST},"
          f" missing {KNOWLEDGE_MISSING}")
    print(f"  release technology hits {N_RELEASE_HITS} {RELEASE_HITS}")
    print(f"  release summary {RELEASE_SUMMARY_WORDS} words, ending '{AND_MORE}'")
    print(f"  c14 sends the student with {N_INSTRUMENTS} instrument(s) to evaluate "
          f"{N_EVALUATIONS} thing(s): {EVALUATIONS}")
    print(f"  item date line {ITEM_DATE_LONG}, effective {EFFECTIVE_DAYS} days after filing,"
          f" implemented {SCHOOL_YEAR}")
