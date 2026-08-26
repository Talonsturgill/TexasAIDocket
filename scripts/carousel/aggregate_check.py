#!/usr/bin/env python3
"""aggregate_check.py — re-derive every number a slide invents by adding other numbers up.

THE GAP THIS FILLS, AND WHY IT IS THE GAP THIS PROJECT CANNOT LEAVE OPEN

The law is that every numeral is produced by code, from data, and can be recomputed from the same
inputs. `claims_check` proves each claim carries a source. `numeral_lint` proves each published
figure traces to a computation. Neither of them looks at the arithmetic performed ON TOP of the
claims, and that arithmetic is where a slide invents a fresh factual assertion out of verified
parts.

A slide reading "FIVE PUCT FILINGS, JULY 22 TO 31" is not quoting anything. It is a count and a
span the deck computed, and if the count is wrong it is wrong in the largest type on the page.
In the sibling product exactly that shipped: a slide printed FIVE where the answer was four,
because a federal notice had been counted as a state posting, and slide 09 of the same deck said
four. `qa.py` passed. `copy_sync_check` passed. `claims_check` passed. A human caught it by
reading. The same run's fact-checker had already rejected an "eight days" span for this very
class of error, so the machine knew the failure mode and rendered one anyway.

The general shape: **every on-slide string that aggregates verified claims into a NEW number is
itself an unverified claim.** A count, a span, a duration, a ratio. This is the gate that
re-derives them.

HOW IT WORKS

1. DETECT. Scan the text the browser actually laid out, `render_report.json`, for four shapes.
   Not the source HTML: what matters is what a reader sees after the layout ran.
2. REQUIRE a declaration for each detection in `out/<date>/aggregates.json`, naming the claim ids
   the number was computed from.
3. RE-DERIVE from those ids and fail when the arithmetic disagrees with the slide.

An undeclared aggregate fails. That is the point: the deck must say where each invented number
came from, and "I did not notice it was an aggregate" is exactly how the sibling's five got
rendered.

THE THREE ROUTES A DECLARATION MAY TAKE, and the third was added 2026-08-18

    from_claims   a tally, one claim id per unit counted        FIVE PUCT FILINGS
    computed_by   code over data, naming the code and the input 254 counties, len() of a topojson
    quoted_from   a figure THE SOURCE WROTE, plus the exact     two schools, four hours
                  string it appears in

Run No.2 had five figures of the third kind and only two routes to declare them, so it declared
them all through `computed_by`, whose name asserts the opposite of what happened and whose only
check is that the prose runs to three words. The honest route was the unchecked one. `quoted_from`
takes a claim id and the quoted string, and verifies BOTH: the string must occur in that claim,
and the declared value must be a numeral inside that string. A `computed_by` that describes
quoting is now refused and told where to go, so the workaround cannot be reused.

    aggregate_check.py --date 2026-08-12
    aggregate_check.py --self-test
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Number words, because a slide sets "FOUR FILINGS" far more often than "4 FILINGS". Through
# twenty, which is past any count a single deck has ever legitimately printed.
WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20,
}
# `\d{1,4}` was wrong and the end-to-end proof is what caught it. On a slide reading
# "2,600 streamlines" it matched the "600" and reported `600 streamlines`, so the gate named a
# number the slide does not contain. **A gate that misreports a figure is worse than one that
# misses it**, because the run then goes looking for a number that was never there. Thousands
# separators are consumed as part of the token.
NUM = r"(?:\d{1,3}(?:,\d{3})+|\d{1,4}|" + "|".join(WORDS) + r")"

# THE FOUR SHAPES. Each is a number the deck computed rather than quoted.
#
# `count`     a tally of things              FIVE PUCT FILINGS
# `duration`  an elapsed quantity of time    21 DAYS, THREE WEEKS EARLIER
# `span`      a range between two dates      JULY 22 TO 31
# `ratio`     a part of a whole              4 OF 9 COUNTIES
#
# Deliberately greedy about what counts as an aggregate and deliberately quiet about how to
# declare one. A false positive costs one line in aggregates.json. A false negative is the
# sibling's FIVE.
MONTHS = ("January|February|March|April|May|June|July|August|September|October|November|December"
          "|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec")
SHAPES = {
    "ratio": re.compile(rf"\b({NUM})\s+of\s+({NUM})\b", re.I),
    "span": re.compile(rf"\b(?:{MONTHS})\s+\d{{1,2}}(?:st|nd|rd|th)?\s+to\s+"
                       rf"(?:(?:{MONTHS})\s+)?\d{{1,2}}(?:st|nd|rd|th)?\b", re.I),
    "duration": re.compile(rf"\b({NUM})\s+(day|days|week|weeks|month|months|year|years|"
                           rf"hour|hours)\b", re.I),
    "count": re.compile(rf"\b({NUM})\s+([a-z][a-z-]{{2,}}(?:\s+[a-z][a-z-]{{2,}}){{0,3}}?s)\b",
                        re.I),
}

# Strings that LOOK like an aggregate and are not, because they are quoted from a source or are
# part of the site's own furniture. Each is a specific thing, never a pattern, so the exemption
# cannot widen quietly.
EXEMPT = re.compile(
    r"\b(?:"
    r"claim c\d+"                      # a citation
    r"|\d{4}"                          # a bare year
    r"|senate bill|house bill|sb \d+|hb \d+"    # bill numbers
    r"|project \d+|docket \d+|control number \d+"
    r"|section \d+|chapter \d+"
    r")\b", re.I)

# THE SLIDE COUNTER, which is furniture and not a claim. Every deck carries "01 / 09" or "slide
# one of nine" on every slide, and before this the gate raised one finding per slide for it: nine
# findings a run, forever, none of them real. **A gate that cries wolf nine times a deck teaches
# the run to scroll past the tenth**, which is the one that matters.
#
# Matched narrowly on purpose. The second number must be the SLIDE COUNT, and there must be no
# noun after it. "4 of 9 counties" is a real aggregate and stays one.
def is_slide_counter(text: str, m: re.Match, kind: str, n_slides: int | None) -> bool:
    if kind != "ratio" or not n_slides:
        return False
    if to_int(m.group(2)) != n_slides:
        return False
    tail = text[m.end():m.end() + 24].strip()
    return not re.match(r"[a-z]", tail, re.I)


def to_int(tok: str) -> int | None:
    """A token `NUM` matched, as an integer.

    THE DEFECT, 2026-08-21. `NUM` was taught to consume a thousands separator in August, after
    "2,600 streamlines" was reported as `600`. This function was not, so it read `1,400` with
    `str.isdigit()`, got False, fell through to the number words and returned None.

    What that cost is bigger than it looks. `_rederive_quoted` builds its token list from this,
    so a quoted figure at or above 1,000 produced an EMPTY list and the gate reported that "the
    quoted string carries no numeral at all" about a string whose numeral is in it. **No figure
    of four digits or more could be declared through `quoted_from` at all**, which is most of
    the figures a source actually writes down. Slide 4's `more than 1,400 loads` hit it and was
    routed through `computed_by` instead, and the run wrote it up rather than editing the engine
    it was running.

    A gate that misreports a figure is worse than one that misses it, and a gate that refuses
    the honest route teaches a run that the shortcut passes. This is both at once.
    """
    t = tok.strip().lower().replace(",", "")
    if t.isdigit():
        return int(t)
    return WORDS.get(tok.strip().lower())


def detect(text: str, n_slides: int | None = None) -> list[dict]:
    """Every aggregate shape in one rendered string.

    `n_slides` lets the slide counter be recognised as furniture. It is optional so the shape
    detectors stay testable on a bare string, and absent it nothing is exempted, which is the
    safe direction.
    """
    if EXEMPT.search(text):
        return []
    found = []
    for kind, rx in SHAPES.items():
        for m in rx.finditer(text):
            if is_slide_counter(text, m, kind, n_slides):
                continue
            found.append({"kind": kind, "phrase": m.group(0).strip()})
        if kind in ("ratio", "span") and found:
            # A ratio or a span already explains the numbers inside it, so a count detected in
            # the same string would be the same figure reported twice.
            break
    return found


def scan_report(report: dict) -> list[dict]:
    out = []
    n_slides = len(report.get("slides") or [])
    for i, slide in enumerate(report.get("slides") or []):
        name = slide.get("slide") or slide.get("file") or f"slide {i + 1}"
        for node in slide.get("text_nodes") or []:
            # FURNITURE THE DESIGN HAS ALREADY DECLARED. render.py records a `decorative` flag
            # for exactly this, and until 2026-08-16 nothing here read it.
            #
            # The coordinates footer in the form the design doctrine asks for, "30 degrees 33
            # minutes N", reads as a span to the shape detectors. It produced four findings on
            # every slide, thirty six for the deck, none of them real. That run worked around it
            # by printing decimal degrees, which is a worse footer than the doctrine asks for,
            # and wrote the gate up as a proposal.
            #
            # The argument is the same one already written above for the slide counter: a gate
            # that cries wolf nine times a deck teaches the run to scroll past the tenth. This
            # exemption is narrower than that one, because a designer had to mark the element
            # rather than the gate guessing from a pattern.
            if node.get("decorative"):
                continue
            txt = (node.get("text") or "").strip()
            if not txt:
                continue
            for d in detect(txt, n_slides):
                out.append({"slide": name, "text": txt, **d})
    return out


def _norm(s: str) -> str:
    """Whitespace collapsed, case folded, smart quotes and dashes flattened.

    A declaration is copied out of a claim by hand, so the difference between the two is
    usually a line break or a curly apostrophe. Failing on that would teach a run that the
    gate is fussy rather than that the source disagrees, and a gate people route around is
    worse than none (GATE_LESSONS 15, the slide counter that cried wolf nine times a deck).
    """
    s = (s or "").replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"')
    s = s.replace("—", "-").replace("–", "-")
    return re.sub(r"\s+", " ", s).strip().casefold()


def _rederive_quoted(decl: dict, claims: dict, cid: str) -> tuple[bool, str]:
    """A figure the SOURCE wrote, checked against the claim that carries it. See rederive()."""
    stated = decl.get("value")
    if not isinstance(stated, (int, float)):
        return False, "a quoted aggregate must declare the numeric `value` the source states"
    quote = str(decl.get("quote") or "").strip()
    if not quote:
        return False, ("`quoted_from` names claim %s and no `quote`. The claim id alone does not "
                       "say WHICH string in it carries the number, so nothing can be checked" % cid)
    by_id = {c.get("id"): c for c in (claims.get("claims") or []) if isinstance(c, dict)}
    claim = by_id.get(cid)
    if claim is None:
        return False, (f"`quoted_from` cites {cid!r}, which is not in the claims file "
                       f"(ids present: {sorted(by_id)[:8]})")
    haystack = _norm(" ".join(str(claim.get(k) or "") for k in ("quote", "text")))
    if _norm(quote) not in haystack:
        return False, (f"the declared quote {quote[:60]!r} does not occur in claim {cid}. A "
                       f"figure is only quoted if the claim actually contains the string it "
                       f"came from; claim {cid} reads {str(claim.get('quote') or claim.get('text'))[:80]!r}")
    toks = [to_int(m.group(1)) for m in re.finditer(rf"\b({NUM})\b", quote, re.I)]
    if stated not in [t for t in toks if t is not None]:
        return False, (f"the declaration says {stated} and the quoted string carries "
                       f"{[t for t in toks if t is not None] or 'no numeral at all'}. A quoted "
                       f"figure must be the number the source wrote, not a number derived from it")
    return True, ""


def rederive(decl: dict, claims: dict) -> tuple[bool, str]:
    """Recompute the declared aggregate from what it says it came from.

    TWO LEGITIMATE ORIGINS, and the first version of this only knew one. A count can be a tally
    of CLAIMS, which is the sibling's FIVE PUCT FILINGS and is checked by counting the ids. It
    can equally be code computing over DATA: 254 counties is `len()` of the committed topojson,
    and there are not 254 claims behind it, nor should there be.

    The end-to-end proof is what surfaced this. Every self-test here was green while the gate
    refused a slide whose number was computed exactly the way CLAUDE.md's law requires, which
    would have taught the first real run that the honest route fails and the shortcut passes.

    A `computed_by` declaration names the code and the input. It is not weaker than the claim
    route, it is the other half of the same rule, and it still refuses a bare assertion: a
    declaration with neither `from_claims` nor `computed_by` fails.
    """
    ids = decl.get("from_claims") or []
    computed_by = str(decl.get("computed_by") or decl.get("how") or "").strip()

    # THE THIRD ORIGIN (2026-08-18), and the run that earned it wrote the argument itself.
    #
    # A figure can be neither counted nor computed. It can be QUOTED: the source says "two
    # Future 2 schools" and "the first four hours", and the deck repeats the number the source
    # wrote. The `count` rule wants one claim id per unit counted, so "two schools" would have
    # to name two claims, which is a lie in the shape the rule expects. Run No.2 therefore
    # declared five quoted figures through `computed_by`, a field whose name says the opposite
    # of what happened, and whose only check is that the prose is three words long. So the
    # honest route was the unchecked one and the note carried the whole burden.
    #
    # `quoted_from` is that route, and it is STRICTLY STRONGER than what it replaces, not a
    # relaxation. It names the claim and the exact string, and both are verified: the string
    # must actually occur in that claim, and the declared value must be a numeral inside that
    # string. A quoted figure the source does not contain now fails, where before it passed on
    # a sentence nobody read.
    quoted_from = str(decl.get("quoted_from") or "").strip()
    if quoted_from:
        return _rederive_quoted(decl, claims, quoted_from)
    if re.search(r"\bquot(?:ed|ing)\s+(?:verbatim\s+)?from\b", computed_by, re.I):
        return False, (
            "`computed_by` says the figure was QUOTED, which means it was not computed. Declare "
            "it with `quoted_from` (the claim id) and `quote` (the exact string in that claim "
            "carrying the number) so the gate can check the source really says it, instead of "
            "reading a sentence nobody verifies")

    if computed_by:
        if not isinstance(decl.get("value"), (int, float)):
            return False, "a computed aggregate must declare the numeric `value` it produced"
        if len(computed_by.split()) < 3:
            return False, (f"`computed_by` reads {computed_by!r}, which names no input. Say what "
                           f"was computed and from which file or field, so somebody can re-run it")
        return True, ""
    if not ids:
        return False, ("declares neither `from_claims` nor `computed_by`. Every number the deck "
                       "computes traces to the claims it counted or to the code that produced it")
    known = {c.get("id") for c in (claims.get("claims") or [])}
    missing = [i for i in ids if i not in known]
    if missing:
        return False, f"cites claim id(s) not in the claims file: {missing}"

    kind, stated = decl.get("kind"), decl.get("value")
    if kind == "count":
        got = len(ids)
        if got != stated:
            return False, (f"the slide says {stated} and it names {got} claim id(s). "
                           f"One of those is wrong, and the slide is the one a reader sees")
        # THE NOUN HAS TO MEAN WHAT IT SAYS, and this is the defect that got past this gate.
        #
        # On 2026-08-19 slide 5 was headlined "Three figures, three sources." and declared
        # `from_claims: [c6, c8, c9]`. Three ids, so `got == stated` and the gate passed it. But
        # c6 and c8 carry the SAME url, the signed directive letter, so the slide published three
        # figures drawn from TWO documents, directly above its own footer printing "the letter"
        # twice. A reader counts two before they finish the frame.
        #
        # A count of CLAIMS is not a count of sources, documents, publishers, filings or counties.
        # `from_claims` re-derives the first and says nothing about the rest, so when the phrase
        # names one of those, the tally is taken over the DISTINCT values the claims carry.
        # The scorer caught this one. A gate that only ever re-derives the number it was handed is
        # the exact shape of defect it exists to catch.
        noun_field = {
            "source": "url", "sources": "url",
            "document": "url", "documents": "url",
            "publisher": "publisher", "publishers": "publisher",
        }
        phrase = str(decl.get("phrase") or "").lower()
        for noun, field in noun_field.items():
            if re.search(rf"(?<![a-z]){re.escape(noun)}(?![a-z])", phrase):
                by_id = {c.get("id"): c for c in (claims.get("claims") or [])
                         if isinstance(c, dict)}
                vals = set()
                for cid in ids:
                    c = by_id.get(cid) or {}
                    v = c.get(field) or c.get("source_" + field) or c.get("source_url")
                    if v:
                        vals.add(str(v).strip())
                if vals and len(vals) != stated:
                    return False, (
                        f"the phrase counts {noun!r}, so it is a tally of distinct {field}(s) and "
                        f"not of claim ids. The claims named carry {len(vals)} distinct {field}(s) "
                        f"and the slide says {stated}. Either the slide is wrong or the phrase "
                        f"names the wrong thing")
                break
        return True, ""
    if kind == "ratio":
        whole = decl.get("of")
        if not isinstance(whole, int) or whole <= 0:
            return False, "a ratio must declare 'of', the size of the whole, as a positive int"
        if len(ids) != stated:
            return False, f"the numerator says {stated} and it names {len(ids)} claim id(s)"
        if stated > whole:
            return False, f"{stated} of {whole} is not a ratio"
        return True, ""
    if kind in ("duration", "span"):
        a, b = decl.get("from_date"), decl.get("to_date")
        if not (a and b):
            return False, f"a {kind} must declare from_date and to_date, both ISO"
        try:
            days = (_dt.date.fromisoformat(b) - _dt.date.fromisoformat(a)).days
        except ValueError:
            return False, f"from_date {a!r} or to_date {b!r} is not an ISO date"
        if days < 0:
            return False, f"to_date {b} is before from_date {a}"
        if kind == "duration" and stated != days:
            return False, (f"the slide says {stated} and {a} to {b} is {days} day(s). "
                           f"An off-by-one here is usually an inclusive count of days")
        return True, ""
    return False, f"unknown kind {kind!r}"


def check(report: dict, declared: dict, claims: dict) -> list[str]:
    problems = []
    found = scan_report(report)
    decls = {d.get("phrase", "").strip().lower(): d for d in (declared.get("aggregates") or [])}

    for f in found:
        key = f["phrase"].strip().lower()
        d = decls.get(key)
        if d is None:
            problems.append(
                f"{f['slide']}: \"{f['phrase']}\" is a computed {f['kind']} and nothing declares "
                f"it. Add it to aggregates.json with the claim ids it was counted from, or "
                f"reword the slide so it stops asserting a number the deck invented")
            continue
        okd, why = rederive(d, claims)
        if not okd:
            problems.append(f"{f['slide']}: \"{f['phrase']}\" does not re-derive. {why}")

    # A declaration for something no slide says is a leftover from an earlier draft, and a
    # leftover is how a stale number gets reused next run.
    seen = {f["phrase"].strip().lower() for f in found}
    for key, d in decls.items():
        if key not in seen:
            problems.append(f"aggregates.json declares \"{d.get('phrase')}\" and no slide says "
                            f"it. Remove it rather than leaving it to be reused")
    return problems


def receipt(found: list, declared: dict, problems: list) -> dict:
    """The receipt this check leaves behind, with each side counted separately.

    `declared` used to hold `len(found)`, which is the number of numeric PHRASES IN THE RENDER
    rather than the number of DECLARATIONS, and the two differ whenever one declared phrase is
    printed twice. On 2026-08-26 slide 7 set "One says AI." as its display line and its note said
    "One says" again, so eight occurrences covered seven declarations and `gate_status` printed
    "8 declared and re-derived" over an aggregates.json holding 7. Two of three judges read that
    row as a discrepancy and nearly logged it as a defect.

    Nothing was wrong except the label. **A gate that misreports a figure costs more than one that
    misses it**, because the run then hunts for something that was never there. Both numbers are
    written now and each is named for the side it counted.
    """
    return {
        "declared": len({d.get("phrase", "").strip().lower()
                         for d in (declared.get("aggregates") or []) if isinstance(d, dict)}),
        "found": len(found),
        "distinct_phrases": len({f["phrase"].strip().lower() for f in found}),
        "problems": problems,
    }


def run(date: str, out_root: Path = None) -> int:
    base = Path(out_root or (REPO_ROOT / "out")) / date
    rp, ap, cp = (base / "render" / "render_report.json",
                  base / "aggregates.json", base / "claims.json")
    if not rp.exists():
        print(f"aggregate_check: no render report at {rp}", file=sys.stderr)
        return 2
    report = json.loads(rp.read_text(encoding="utf-8"))
    claims = json.loads(cp.read_text(encoding="utf-8")) if cp.exists() else {"claims": []}
    declared = json.loads(ap.read_text(encoding="utf-8")) if ap.exists() else {"aggregates": []}

    problems = check(report, declared, claims)
    found = scan_report(report)

    # A RECEIPT, written whether it passed or failed, so a later reader can tell that this ran
    # against THIS render. `aggregates.json` is an INPUT the run authors before the check, and a
    # status row built from an input says only that somebody wrote a file. The end-to-end proof
    # caught exactly that: the gate block carried a stale aggregates row telling the run to
    # re-run the check, and re-running it could never clear the row, because a check does not
    # rewrite its own input. **Inputs precede the render. Reports describe it.**
    #
    # AND IT COUNTS BOTH SIDES SEPARATELY, since 2026-08-26. `declared` used to hold `len(found)`,
    # which is the number of numeric PHRASES IN THE RENDER, not the number of DECLARATIONS. Those
    # two differ whenever one declared phrase is printed twice, which is ordinary: that deck's
    # slide 7 set "One says AI." as its display line and "One says" appeared again in its note, so
    # the render carried 8 occurrences of 7 declared phrases. The status block then read "8
    # declared and re-derived" over an aggregates.json holding 7, and two of three judges read the
    # row as a discrepancy and nearly logged it as a defect.
    #
    # Nothing was wrong except the label, and a gate that misreports a figure costs more than one
    # that misses it, because the run then hunts for something that was never there. Both counts
    # are written now and each is named for what it counted.
    (base / "aggregate_report.json").write_text(
        json.dumps(receipt(found, declared, problems), indent=2), encoding="utf-8")

    if problems:
        print(f"aggregate_check: {len(problems)} problem(s)\n")
        for p in problems:
            print(f"  - {p}")
        print("\n  Every number the deck computes from other numbers is a fresh claim.")
        return 1
    print(f"aggregates: clean ({len(found)} computed figure(s), all re-derived)")
    return 0


def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    ok("a count in words is detected", detect("FOUR PUCT FILINGS")[0]["kind"] == "count")

    # THE NOUN RULE, replaying the 2026-08-19 defect this gate passed.
    #
    # Slide 5 said "three sources" and named three claim ids, two of which shared one url. The
    # tally matched the id count and the gate went green over a published miscount.
    _two_docs = {"claims": [
        {"id": "c6", "url": "https://gov.texas.gov/letter.pdf", "publisher": "Office of the Governor"},
        {"id": "c8", "url": "https://gov.texas.gov/letter.pdf", "publisher": "Office of the Governor"},
        {"id": "c9", "url": "https://gov.texas.gov/release", "publisher": "Office of the Governor"},
    ]}
    _bad = {"phrase": "three sources", "kind": "count", "value": 3,
            "from_claims": ["c6", "c8", "c9"]}
    okd, why = rederive(_bad, _two_docs)
    ok("THE REAL DEFECT: 'three sources' over two distinct urls fails", not okd, why)
    ok("...and the message names the real count", "2 distinct url" in why, why)
    _good = {"phrase": "two documents", "kind": "count", "value": 2,
             "computed_by": "distinct source_url over claims c6, c8 and c9"}
    ok("...while the corrected 'two documents' passes", rederive(_good, _two_docs)[0])
    _pub = {"phrase": "three publishers", "kind": "count", "value": 3,
            "from_claims": ["c6", "c8", "c9"]}
    ok("'publishers' is tallied over publishers, not ids", not rederive(_pub, _two_docs)[0])
    # A count whose noun names none of those still re-derives against the claim ids, unchanged.
    _plain = {"phrase": "three filings", "kind": "count", "value": 3,
              "from_claims": ["c6", "c8", "c9"]}
    ok("a noun the rule does not name still counts claim ids",
       rederive(_plain, _two_docs)[0], str(rederive(_plain, _two_docs)))
    ok("...and in digits", detect("4 PUCT FILINGS")[0]["kind"] == "count")
    ok("a duration is detected", detect("21 DAYS LEFT")[0]["kind"] == "duration")
    ok("a ratio is detected", detect("4 of 9 counties")[0]["kind"] == "ratio")
    ok("a span is detected", detect("July 22nd to 31st")[0]["kind"] == "span")
    # BOTH OF THESE WERE FOUND BY THE END TO END PROOF, on a real render, with every self-test
    # in this file already green. Running the gates on artifacts is not the same as running them
    # on fixtures, and the fixtures had been written by the same hand as the detector.
    #
    # `\d{1,4}` matched the "600" inside "2,600 streamlines" and the gate reported a figure the
    # slide does not contain. A gate that MISREPORTS a number is worse than one that misses it,
    # because the run then goes hunting for a number that was never there.
    got = detect("A flow field of 2,600 streamlines")
    ok("a thousands separator is part of the number, not a new one",
       got and got[0]["phrase"].startswith("2,600"), str(got))

    # And the slide counter. Every deck carries one on every slide, so before this the gate
    # raised nine findings a run, forever, none of them real.
    ok("the slide counter is furniture, not a claim", not detect("slide one of four", 4))
    # Written as `not detect(...) or True` on the first pass, which is a test that
    # cannot fail. An always-green assertion is the same decoration this file exists
    # to argue against, so it asserts the real thing: the ratio shape requires the
    # word "of", so a slash counter never matched it in the first place.
    ok("...and the numeric form never matched the ratio shape at all",
       detect("01 / 04", 4) == [])
    ok("...but only when the second number IS the slide count",
       detect("four of nine", 4) != [])
    ok("...and only when no noun follows it, so a real ratio survives",
       detect("4 of 9 counties", 9) != [])
    ok("...and with no slide count known, nothing is exempted, which is the safe direction",
       detect("slide one of four") != [])

    # THE DECORATIVE MARKER, which existed and was not being read. The coordinates footer in the
    # form the design doctrine asks for produced four findings on every slide, thirty six for the
    # 2026-08-16 deck, and that run printed decimal degrees instead to get past it.
    footer = "GRIMES COUNTY 30 degrees 33 minutes N 95 degrees 59 minutes W"
    ok("the doctrine's coordinates footer does read as an aggregate on its own",
       detect(footer) != [], "if this goes quiet the exemption below proves nothing")
    marked = {"slides": [{"file": "slide-01.png",
                          "text_nodes": [{"text": footer, "decorative": True}]}]}
    ok("...and a node the design marked decorative is not scanned", scan_report(marked) == [])
    unmarked = {"slides": [{"file": "slide-01.png",
                            "text_nodes": [{"text": footer, "decorative": False}]}]}
    ok("...while the same string unmarked is still reported", scan_report(unmarked) != [])

    # The exemption must not swallow a real figure that happens to share a node with furniture.
    real = {"slides": [{"file": "slide-01.png", "text_nodes": [
        {"text": footer, "decorative": True},
        {"text": "4 of 9 counties carry an item", "decorative": False}]}]}
    ok("...and a real aggregate beside decorative furniture still lands",
       len(scan_report(real)) == 1, str(scan_report(real)))

    ok("a bare year is not an aggregate", not detect("filed in 2026"))
    ok("a bill number is not an aggregate", not detect("Senate Bill 6 was referred"))
    ok("a docket number is not an aggregate", not detect("PUCT Project 58482 opened"))
    ok("a citation is not an aggregate", not detect("three filings, claim c4"))
    ok("prose with no figure is quiet", not detect("The commission considered the proposal"))

    claims = {"claims": [{"id": f"c{i}"} for i in range(1, 6)]}
    report = {"slides": [{"slide": "slide-04", "text_nodes": [{"text": "FIVE PUCT FILINGS"}]}]}

    # THE SIBLING'S ACTUAL FAILURE. A slide printed five where the answer was four, and every
    # other gate passed. Undeclared is the state that shipped it.
    ok("an undeclared aggregate fails, which is the case that shipped",
       any("nothing declares it" in p for p in check(report, {"aggregates": []}, claims)))

    good = {"aggregates": [{"phrase": "FIVE PUCT FILINGS", "kind": "count",
                            "value": 5, "from_claims": ["c1", "c2", "c3", "c4", "c5"]}]}
    ok("...and a declaration that re-derives passes", not check(report, good, claims))

    # The exact arithmetic error: five stated, four actually counted.
    wrong = {"aggregates": [{"phrase": "FIVE PUCT FILINGS", "kind": "count",
                             "value": 5, "from_claims": ["c1", "c2", "c3", "c4"]}]}
    ok("caught: the slide says five and names four claims",
       any("names 4 claim" in p for p in check(report, wrong, claims)))

    ghost = {"aggregates": [{"phrase": "FIVE PUCT FILINGS", "kind": "count", "value": 5,
                             "from_claims": ["c1", "c2", "c3", "c4", "c9"]}]}
    ok("caught: a claim id that is not in the claims file",
       any("not in the claims file" in p for p in check(report, ghost, claims)))

    dur_report = {"slides": [{"slide": "s2", "text_nodes": [{"text": "21 DAYS"}]}]}
    dur_ok = {"aggregates": [{"phrase": "21 DAYS", "kind": "duration", "value": 21,
                              "from_date": "2026-08-01", "to_date": "2026-08-22",
                              "from_claims": ["c1"]}]}
    ok("a duration that matches its dates passes", not check(dur_report, dur_ok, claims))
    dur_bad = {"aggregates": [{"phrase": "21 DAYS", "kind": "duration", "value": 21,
                               "from_date": "2026-08-01", "to_date": "2026-08-21",
                               "from_claims": ["c1"]}]}
    ok("caught: an off-by-one in a day count",
       any("is 20 day" in p for p in check(dur_report, dur_bad, claims)))
    dur_rev = {"aggregates": [{"phrase": "21 DAYS", "kind": "duration", "value": 21,
                               "from_date": "2026-08-22", "to_date": "2026-08-01",
                               "from_claims": ["c1"]}]}
    ok("caught: a range that runs backwards",
       any("is before" in p for p in check(dur_report, dur_rev, claims)))

    ratio_report = {"slides": [{"slide": "s3", "text_nodes": [{"text": "4 of 9 counties"}]}]}
    # The declaration keys on the phrase the DETECTOR reports, which for a ratio is the figure
    # itself rather than the noun after it. The failure message prints that phrase verbatim so an
    # author copies it rather than guessing, and this fixture uses it for the same reason.
    ratio_bad = {"aggregates": [{"phrase": "4 of 9", "kind": "ratio", "value": 4,
                                 "of": 3, "from_claims": ["c1", "c2", "c3", "c4"]}]}
    ok("caught: a numerator larger than its whole",
       any("is not a ratio" in p for p in check(ratio_report, ratio_bad, claims)))

    stale = {"aggregates": [{"phrase": "FIVE PUCT FILINGS", "kind": "count", "value": 5,
                             "from_claims": ["c1", "c2", "c3", "c4", "c5"]},
                            {"phrase": "NINE COUNTIES", "kind": "count", "value": 9,
                             "from_claims": ["c1"]}]}
    ok("caught: a declaration no slide says, left from an earlier draft",
       any("no slide says it" in p for p in check(report, stale, claims)))

    ok("an empty deck is clean rather than an error",
       not check({"slides": []}, {"aggregates": []}, claims))

    # THE QUOTED ROUTE (2026-08-18). Run No.2's own figures, verbatim: c2 says "the launch of
    # two Future 2 schools" and the slide printed "Two schools". Before this the only way to
    # declare that was `computed_by`, which is a free text field the gate reads three words of.
    qc = {"claims": [
        {"id": "c2", "text": "Houston ISD announced a launch of two schools.",
         "quote": 'with the launch of two Future 2 schools, C. Martinez and Gregg'},
        {"id": "c3", "text": "The first four hours follow the standard curriculum.",
         "quote": "The first four hours of school follow the standard NES curriculum"}]}
    qr = {"slides": [{"slide": "slide-02", "text_nodes": [{"text": "Two schools"}]}]}
    qgood = {"aggregates": [{"phrase": "Two schools", "kind": "count", "value": 2,
                             "quoted_from": "c2", "quote": "the launch of two Future 2 schools"}]}
    ok("a quoted figure declared with quoted_from passes", not check(qr, qgood, qc),
       str(check(qr, qgood, qc))[:160])

    def qbad(**over):
        d = dict(qgood["aggregates"][0]); d.update(over)
        for k, v in list(d.items()):
            if v is None:
                d.pop(k)
        return check(qr, {"aggregates": [d]}, qc)

    ok("caught: a quote the claim does not contain",
       any("does not occur in claim c2" in p for p in
           qbad(quote="the launch of two hundred Future 2 schools")))
    ok("caught: a value that is not the number the source wrote",
       any("the quoted string carries" in p for p in qbad(value=7)))
    ok("caught: a quoted_from naming a claim that does not exist",
       any("not in the claims file" in p for p in qbad(quoted_from="c99")))
    ok("caught: a claim id with no quote, which checks nothing",
       any("does not say WHICH string" in p for p in qbad(quote=None)))
    ok("a curly apostrophe in the claim is not a disagreement",
       not check(qr, {"aggregates": [dict(qgood["aggregates"][0],
                                          quote="the launch of two Future 2 schools")]},
                 {"claims": [dict(qc["claims"][0],
                                  quote="with the  launch of two Future 2 schools")]}))

    # THE THOUSANDS SEPARATOR (2026-08-21). `NUM` consumes it, `to_int` did not, so every
    # figure at or above 1,000 came back None and the token list collapsed to empty. The gate
    # then said the quoted string carried "no numeral at all" about a string that reads 1,400.
    ok("a token carrying a thousands separator parses", to_int("1,400") == 1400,
       repr(to_int("1,400")))
    ok("...and a bare four digit token still does", to_int("1400") == 1400)
    ok("...and a number word still does", to_int("Four") == 4)
    ok("...and a token that is not a number is still None",
       to_int("loads") is None and to_int("") is None)
    kc = {"claims": [{"id": "c17", "text": "Kodiak reported more than 1,400 loads since February.",
                      "quote": "more than 1,400 loads"}]}
    kr = {"slides": [{"slide": "slide-04",
                      "text_nodes": [{"text": "More than 1,400 loads since February."}]}]}
    kd = {"aggregates": [{"phrase": "1,400 loads", "kind": "count", "value": 1400,
                          "quoted_from": "c17", "quote": "more than 1,400 loads"}]}
    ok("a quoted figure of four digits re-derives through quoted_from",
       not check(kr, kd, kc), str(check(kr, kd, kc))[:200])
    ok("...and the wrong value for it is still CAUGHT",
       any("the quoted string carries" in p for p in
           check(kr, {"aggregates": [dict(kd["aggregates"][0], value=400)]}, kc)),
       str(check(kr, {"aggregates": [dict(kd["aggregates"][0], value=400)]}, kc))[:200])

    # AND THE WORKAROUND ITSELF. This is the declaration run No.2 actually shipped, word for
    # word. It passed. It must not again, and the message has to name the route that replaces it.
    ok("caught: the 2026-08-18 workaround, a quoted figure declared as computed_by",
       any("Declare it with `quoted_from`" in p for p in check(qr, {"aggregates": [
           {"phrase": "Two schools", "kind": "count", "value": 2,
            "computed_by": "quoted from claim c2, which reads 'the launch of two Future 2 "
                           "schools'. Not counted by this deck"}]}, qc)))
    ok("...and an honest computed_by that merely mentions counting quoted names still passes",
       not check(qr, {"aggregates": [
           {"phrase": "Two schools", "kind": "count", "value": 2,
            "computed_by": "len() over the campus list in assets/houston_future2.json"}]}, qc))

    # ---- THE RECEIPT, AND THE 2026-08-26 MISLABEL -------------------------------------
    #
    # `declared` held len(found), which counts render occurrences. A declared phrase printed twice
    # made the receipt say 8 over an aggregates.json holding 7, and the status block printed it as
    # "8 declared and re-derived". Nothing was wrong and two of three judges nearly logged it as a
    # defect. The fixture below is that deck's own shape, not an invented one.
    twice_found = [{"phrase": "Two lists", "kind": "count", "slide": "slide-07"},
                   {"phrase": "One says", "kind": "count", "slide": "slide-07"},
                   {"phrase": "One says", "kind": "count", "slide": "slide-07"}]
    twice_decl = {"aggregates": [{"phrase": "Two lists"}, {"phrase": "One says"}]}
    r = receipt(twice_found, twice_decl, [])
    ok("the receipt counts declarations on the declaration side", r["declared"] == 2, str(r))
    ok("...and render occurrences on the render side", r["found"] == 3, str(r))
    ok("...and says how many of those were distinct", r["distinct_phrases"] == 2, str(r))
    ok("...so the two counts can differ without either being wrong",
       r["declared"] != r["found"])
    # The real artifact, which is the only fixture carrying the shape nobody wrote down.
    real_decl = REPO_ROOT / "runs" / "carousel" / "2026-08-26" / "held" / "aggregates.json"
    if real_decl.exists():
        rd = json.loads(real_decl.read_text(encoding="utf-8"))
        ok("the 2026-08-26 deck really declared 7", receipt([], rd, [])["declared"] == 7,
           str(receipt([], rd, [])))
    else:
        ok("the 2026-08-26 aggregates file is present to replay the mislabel against", False)

    if failures:
        print(f"\naggregate_check self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print(f"\naggregate_check self-test: all passed ({len(SHAPES)} aggregate shapes)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date")
    ap.add_argument("--out", default=str(REPO_ROOT / "out"),
                    help="run scratch root, so every gate takes the same flags")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.date:
        return run(a.date, Path(a.out))
    ap.error("give --date or --self-test")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                        # noqa: BLE001
        print(f"aggregate_check: broke: {exc}", file=sys.stderr)
        sys.exit(2)
