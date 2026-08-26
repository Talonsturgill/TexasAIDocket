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
#
# A DECIMAL POINT IS PART OF THE NUMBER, 2026-08-26. Without the lookbehind and the optional
# fraction, "8.0 gallons per square foot" matched as "0 gallons", and the gate then asked the
# run to declare a figure of zero that appears nowhere. The lookbehind refuses a digit run that
# a digit or a point already leads, so the fractional half of a decimal can never be read as a
# whole number on its own. Same lesson as the thousands separator below: a token the pattern
# cuts in half is a number the report describes wrongly, and a wrong number in a gate's own
# output is worse than silence, because somebody goes looking for it.
NUM = r"(?:(?<![\d.])\d{1,3}(?:,\d{3})+|(?<![\d.])\d{1,4}(?:\.\d+)?|" + "|".join(WORDS) + r")"

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
    # "N of the M" as well as "N of M", since 2026-08-25. English writes a ratio over a known set
    # with the article far more often than without it, and this pattern could not see it: a deck
    # printing "three of the nine" asserted a ratio no computation had to back, and passed. The
    # article is optional rather than a second pattern so one declaration covers both forms.
    "ratio": re.compile(rf"\b({NUM})\s+of\s+(?:the\s+)?({NUM})\b", re.I),
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
#
# AND EACH EXEMPTS ITS OWN SPAN, NOT THE WHOLE LINE. 2026-08-26.
#
# `detect()` opened with `if EXEMPT.search(text): return []`, so ONE bare year anywhere in a
# string exempted every figure in it. The first comment's head reads "Sources, ten official
# records and ten news reports, fetched August 25th and 26th, 2026", and the 2026 at the end
# silently exempted both counts at the front. Round 9's integrity judge found them by reading
# the file rather than by running the gate, and was right that they match the count shape: they
# do, and the gate threw them away before testing.
#
# The same veto was live on every frame. Any line carrying a year, a bill number or a claim
# citation had all its figures exempted, which is most citation lines in this deck. Exemption is
# by OVERLAP now, so "claim c9" still stops c9 being read as a count and stops nothing else.
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

    THE SAME DEFECT AGAIN AT THE DECIMAL POINT (2026-08-26). `NUM` was taught to consume a
    fraction so "8.0 gallons per square foot" stops matching as "0 gallons", and this returned
    None for "8.0" for exactly the reason it returned None for "1,400": `str.isdigit()` is False.
    A figure a source WROTE DOWN as a decimal could not be declared through `quoted_from`, and
    a water cap is written that way by every ordinance that has one. Returns an int when the
    value is whole so nothing downstream that compares against an integer changes.
    """
    t = tok.strip().lower().replace(",", "")
    if t.isdigit():
        return int(t)
    try:
        v = float(t)
    except ValueError:
        return WORDS.get(tok.strip().lower())
    return int(v) if v.is_integer() else v


def detect(text: str, n_slides: int | None = None) -> list[dict]:
    """Every aggregate shape in one rendered string.

    `n_slides` lets the slide counter be recognised as furniture. It is optional so the shape
    detectors stay testable on a bare string, and absent it nothing is exempted, which is the
    safe direction.
    """
    exempt = [(m.start(), m.end()) for m in EXEMPT.finditer(text)]

    def is_exempt(a, b):
        return any(a < e and b > st for st, e in exempt)

    raw = []
    for kind, rx in SHAPES.items():
        for m in rx.finditer(text):
            if is_slide_counter(text, m, kind, n_slides):
                continue
            if is_exempt(m.start(), m.end()):
                continue
            raw.append({"kind": kind, "phrase": m.group(0).strip(),
                        "start": m.start(), "end": m.end()})
    # A ratio or a span already explains the numbers INSIDE ITS OWN SPAN, so a count or a
    # duration overlapping one is the same figure reported twice. Until 2026-08-25 this was a
    # `break` out of the shape loop, which suppressed every later shape ANYWHERE in the string:
    # "Four of the eight came in the last 21 days" reported the ratio and silently exempted the
    # 21, on a gate whose entire purpose is that an undeclared number cannot reach a frame. The
    # suppression is by overlap now, which is what the comment always claimed it was.
    def over(a, bs):
        return any(a["start"] < b["end"] and a["end"] > b["start"] for b in bs)
    covers = [r for r in raw if r["kind"] in ("ratio", "span")]
    durs = [r for r in raw if r["kind"] == "duration"]
    found = []
    for r in raw:
        if r["kind"] in ("count", "duration") and over(r, covers):
            continue
        # "21 days" satisfies the count shape too, because days is a plural noun. Precedence runs
        # ratio and span, then duration, then count, so one figure is reported once.
        if r["kind"] == "count" and over(r, durs):
            continue
        found.append({"kind": r["kind"], "phrase": r["phrase"]})
    return found


# The nouns a coordinates footer and a compass bearing are built from. These are the ONLY
# thing the decorative flag still exempts besides a date span, because they are furniture the
# design doctrine asks for in words and no computation stands behind them.
FURNITURE_NOUN = re.compile(r"\b(degrees|minutes|seconds|arcminutes|arcseconds)\b", re.I)


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
            # NARROWED 2026-08-26. `continue` here exempted the WHOLE NODE, and two numbers
            # rode out on that: slide 3's "154 DAYS" and slide 8's "3 AGENDAS", both set in
            # 19 to 22px attribution type, both fully legible, neither declared, and the gate
            # printed "clean (14 computed figures, all re-derived)" over the pair of them.
            # A reader does not know a node was marked decorative.
            #
            # The original exemption is still right about what it was written for: a
            # coordinates footer set as "30 degrees 33 minutes N" reads as four aggregates on
            # every slide and none is real. So the exemption keeps its subject and loses its
            # reach. On a decorative node a SPAN and the coordinate nouns stay exempt, and a
            # count, a ratio or a duration is checked exactly as it would be anywhere else.
            decorative = bool(node.get("decorative"))
            txt = (node.get("text") or "").strip()
            if not txt:
                continue
            for d in detect(txt, n_slides):
                if decorative and (d.get("kind") == "span"
                                   or FURNITURE_NOUN.search(d.get("phrase") or "")):
                    continue
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


def _structural(decl: dict) -> tuple[bool, str]:
    """The arithmetic a declaration carries in itself, independent of any claim id.

    A ratio states a numerator and an `of`. A duration or a span states two ISO dates. Both can
    be re-derived from the declaration alone, so both are checked whatever route the declaration
    took. Only the COUNT's claim tally needs the `computed_by` exemption, because a count over
    data legitimately has no claim per unit.
    """
    kind, stated = decl.get("kind"), decl.get("value")
    if kind == "ratio":
        whole = decl.get("of")
        if not isinstance(whole, int) or whole <= 0:
            return False, "a ratio must declare 'of', the size of the whole, as a positive int"
        if not isinstance(stated, (int, float)) or stated > whole:
            return False, f"{stated} of {whole} is not a ratio"
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
                           f"A duration is the arithmetic, not a label on it")
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
        # `computed_by` IS NOT AN ESCAPE HATCH, and until 2026-08-26 it was. This branch returned
        # True here, before any of the arithmetic below ran, so a declaration carrying a
        # `computed_by` string got two weak checks and no re-derivation at all. A judge read the
        # gate rather than its output and said so plainly: with every one of twenty entries
        # carrying `computed_by`, "all re-derived" meant twenty prose notes of three words or
        # more were present.
        #
        # The exemption it was built for is real and it is narrow. A COUNT computed over data
        # has no reason to name one claim per unit counted: 254 counties is a len() over a
        # topojson and there are not 254 claims, nor should there be. That exemption is kept.
        # Everything that can be checked WITHOUT claim ids is now checked anyway.
        ok, why = _structural(decl)
        return (True, "") if ok else (False, why)
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


def scan_caption(text: str) -> list[dict]:
    """Every aggregate shape in the CAPTION, which is the surface most people actually read.

    WHY THIS EXISTS. 2026-08-26.

    This gate read `render_report.json` and nothing else, so it judged nine frames and left the
    caption unread. The caption is the copy a reader meets first, it is longer than any frame,
    and it is written in prose, which is where a stray computation is easiest to slip in.

    A judge found one: "Zoning in May, the sewer in June, the water two weeks after that." Two
    weeks is a date delta over c43's June 2nd sewer ordinance and c32's June 16th water
    ordinance. No claim states an interval, `figures.json` holds both dates and computes no gap,
    and nothing declared it. The figure was TRUE, which is exactly why it is worth catching: a
    model doing correct arithmetic in published copy is still the model acting as the
    calculator, and CLAUDE.md names this case in words. The compliant version of that sentence
    was already on the frame beside it, reading "the water on June 16th".

    The caption has no slide counter, so `n_slides` is None and nothing is exempted as furniture.
    Hashtags are stripped first, because #FortWorth is a tag and not a sentence.
    """
    body = re.sub(r"(?m)^\s*#\S+(\s+#\S+)*\s*$", " ", text)
    out = []
    for line in body.splitlines():
        for d in detect(line.strip(), None):
            out.append({"slide": "caption.txt", "text": line.strip(), **d})
    return out


def scan_comment(text: str) -> list[dict]:
    """Every aggregate shape in the FIRST COMMENT, which is the fourth published surface.

    WHY THIS EXISTS. 2026-08-26.

    Round 9's integrity judge found "Sources, ten official records and ten news reports" at the
    head of `first_comment.txt`: two computed counts, on the surface LinkedIn shows directly under
    the post, matching this gate's own `count` shape, and unreachable by it. Both were correct,
    which is the point. A correct number nothing checks is one edit away from a wrong number
    nothing checks.

    That is the third time in two days that this gate learned a surface late. The caption, then
    the document title, now this. The docstring on `surfaces()` argues the fix belongs to the
    class rather than the instance, and this is the class: EVERY surface a reader can see.

    The source lines themselves are stripped first. Each is a citation with a date and a claim
    id, and a date is not a computed figure. Only the prose head is read.
    """
    head = []
    for line in (text or "").splitlines():
        line = line.strip()
        if not line or line.startswith("http") or re.search(r"\bc\d+\s*$", line):
            continue
        head.append(line)
    return [{"slide": "first_comment.txt", "text": ln, **d}
            for ln in head for d in detect(ln, None)]


def scan_title(title: str) -> list[dict]:
    """Every aggregate shape in the DOCUMENT TITLE, which is the third published surface.

    WHY THIS EXISTS. 2026-08-26.

    Round 8 recut the cover and the title stopped being a slide string. `copy.json` still carried
    it, the PDF still printed it, the email still used it as its subject, and nothing scanned it
    any more, because this gate reads the render report and the render report holds frames. The
    title in front of it was "Fifteen ways to take up a data center", which is a count of the
    acting bodies, and after the recut it was a computed figure on a published surface with no
    declaration behind it and no check able to notice.

    That is the caption defect one surface over, one round later. The lesson the caption fix
    should have carried and did not is that the fix belongs to the CLASS: every surface a reader
    can see is scanned, and a new surface is scanned the day it appears rather than the round
    after a judge finds a number on it.

    A title has no slide counter, so `n_slides` is None and nothing is exempted as furniture.
    """
    title = (title or "").strip()
    return [{"slide": "document_title", "text": title, **d}
            for d in detect(title, None)] if title else []


def check(report: dict, declared: dict, claims: dict, caption: str = "",
          title: str = "", comment: str = "") -> list[str]:
    problems = []
    found = (scan_report(report) + (scan_caption(caption) if caption else [])
             + (scan_title(title) if title else [])
             + (scan_comment(comment) if comment else []))
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


def surfaces(base: Path) -> dict:
    """The published surfaces this gate reads, from one directory, named ONCE.

    WHY THIS FUNCTION EXISTS. 2026-08-26.

    This gate has three callers: `run()` here, `shipped_check.g_aggregates`, and the run's own
    declaration generator. Each one used to open the surface files itself, so every time the gate
    learned a new surface, three call sites had to learn it too, and they did not. The caption was
    added and `g_aggregates` kept reading the render alone, which turned a caption-only figure
    into a phantom leftover declaration. The comment recording that fix is still in that adapter,
    and one day later the document title did exactly the same thing to the same adapter.

    Twice is a habit. The list of surfaces lives here now, and a caller that wants them asks. A
    new surface is one edit, in one place, and every caller gets it without being told.

    `base` is a run directory in either shape: `out/<date>/` with `render/render_report.json`
    under it, or `runs/carousel/<date>/` with the report at the top level.
    """
    rp = base / "render" / "render_report.json"
    if not rp.exists():
        rp = base / "render_report.json"
    cap = base / "caption.txt"
    com = base / "first_comment.txt"
    cop = base / "copy.json"
    title = ""
    if cop.exists():
        try:
            title = json.loads(cop.read_text(encoding="utf-8")).get("document_title") or ""
        except (ValueError, OSError):
            title = ""
    return {
        "report_path": rp,
        "report": json.loads(rp.read_text(encoding="utf-8")) if rp.exists() else None,
        "caption": cap.read_text(encoding="utf-8") if cap.exists() else "",
        "title": title,
        "comment": com.read_text(encoding="utf-8") if com.exists() else "",
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

    sf = surfaces(base)
    caption, title, comment = sf["caption"], sf["title"], sf["comment"]
    problems = check(report, declared, claims, caption, title, comment)
    found = (scan_report(report) + (scan_caption(caption) if caption else [])
             + (scan_title(title) if title else [])
             + (scan_comment(comment) if comment else []))

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
    # A CITATION IS NOT AN AGGREGATE, AND IT IS NOT A PARDON FOR ONE EITHER (2026-08-26).
    # This case used to assert that "three filings, claim c4" was clean, which was true only
    # because "claim c4" vetoed the whole string. "three filings" is a count and always was.
    ok("a citation is not read as an aggregate", not detect("claim c4"))
    ok("...and a real count beside one is still caught",
       [d["phrase"] for d in detect("three filings, claim c4")] == ["three filings"],
       str(detect("three filings, claim c4")))
    ok("a bare year does not pardon the figures beside it",
       [d["phrase"] for d in detect("ten official records and ten news reports, 2026")]
       == ["ten official records", "ten news reports"],
       str(detect("ten official records and ten news reports, 2026")))
    ok("...and the year itself is still not a figure",
       not detect("fetched August 25th and 26th, 2026"),
       str(detect("fetched August 25th and 26th, 2026")))
    ok("a bill number pardons nothing either",
       [d["phrase"] for d in detect("four counties, Senate Bill 6")] == ["four counties"],
       str(detect("four counties, Senate Bill 6")))
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
    # A RATIO DOES NOT EXEMPT THE REST OF ITS SENTENCE (2026-08-25).
    both = detect("Four of the eight came in the last 21 days.")
    ok("a ratio and an unrelated duration in one string are BOTH reported, once each",
       [f["kind"] for f in both] == ["ratio", "duration"], str(both))
    inside = detect("four of the eight bodies acted")
    ok("...but a count inside the ratio's own span is still suppressed",
       [f["kind"] for f in inside] == ["ratio"], str(inside))

    # A RATIO WRITTEN WITH THE ARTICLE (2026-08-25), all three directions.
    ok("a ratio written with the article is detected",
       any(f["phrase"].lower() == "two of the eight"
           for f in detect("Two of the eight stop nothing")),
       str(detect("Two of the eight stop nothing")))
    ok("...and the bare form still is",
       any(f["kind"] == "ratio" and f["phrase"].lower() == "4 of 9"
           for f in detect("4 of 9 bodies declined")),
       str(detect("4 of 9 bodies declined")))
    ok("...and an article with no second number is not a ratio",
       not any(f["kind"] == "ratio" for f in detect("two of the commissioners spoke")),
       str(detect("two of the commissioners spoke")))

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

    # THE CAPTION IS A PUBLISHED SURFACE (2026-08-26). This gate read the render and nothing
    # else, and a judge found by hand a date delta in the caption that no gate could reach.
    _cap = ("Zoning in May, the sewer in June, the water two weeks after that.\n\n"
            "#BrazoriaCounty #SanAngelo #FortWorth\n")
    _hits = scan_caption(_cap)
    ok("a duration in the caption is seen", any(h["phrase"] == "two weeks" for h in _hits), str(_hits))
    ok("...and it is attributed to caption.txt, not to a slide",
       all(h["slide"] == "caption.txt" for h in _hits))
    ok("a hashtag line is not read as copy",
       not any("FortWorth" in h.get("text", "") for h in _hits), str(_hits))
    ok("a caption with no computed number is clean",
       not scan_caption("The council decides. The commission only recommends.\n"))
    ok("the compliant version of the same sentence passes",
       not any(h["kind"] == "duration"
               for h in scan_caption("the sewer in June, the water on June 16th.")),
       str(scan_caption("the sewer in June, the water on June 16th.")))
    ok("check() reads the caption when it is given one",
       any("caption.txt" in p for p in check({"slides": []}, {"aggregates": []},
                                             {"claims": []}, _cap)))
    ok("...and is unchanged when it is not",
       not check({"slides": []}, {"aggregates": []}, {"claims": []}))

    # THE DOCUMENT TITLE IS A PUBLISHED SURFACE (2026-08-26). It prints on the PDF and carries
    # the email's subject, and after round 8's recut it stopped being a slide string, which took
    # it out of the render report and out of this gate's reach in the same move.
    _t = "Fifteen ways to take up a data center"
    ok("a count in the document title is seen",
       any(h["phrase"] == "Fifteen ways" for h in scan_title(_t)), str(scan_title(_t)))
    ok("...and it is attributed to the title, not to a slide",
       all(h["slide"] == "document_title" for h in scan_title(_t)))
    ok("a title with no computed number is clean",
       not scan_title("What the record holds"))
    ok("an empty title is not a finding", not scan_title("") and not scan_title(None))
    # ONE LIST OF SURFACES (2026-08-26). Three callers, one place they come from.
    import tempfile
    with tempfile.TemporaryDirectory() as _td:
        _b = Path(_td)
        (_b / "render").mkdir()
        (_b / "render" / "render_report.json").write_text(json.dumps({"slides": []}))
        (_b / "caption.txt").write_text("Two of the fifteen were approvals.\n")
        (_b / "copy.json").write_text(json.dumps({"document_title": _t}))
        _s = surfaces(_b)
        ok("surfaces() finds an out/<date> layout", _s["report"] == {"slides": []})
        ok("...its caption", "approvals" in _s["caption"])
        ok("...and its title", _s["title"] == _t)
        (_b / "render" / "render_report.json").unlink()
        (_b / "render_report.json").write_text(json.dumps({"slides": [1]}))
        ok("surfaces() also finds a runs/<date> layout, where the report is at the top level",
           surfaces(_b)["report"] == {"slides": [1]})
        (_b / "copy.json").write_text("{ not json")
        ok("an unreadable copy.json yields no title rather than raising",
           surfaces(_b)["title"] == "")
        (_b / "caption.txt").unlink()
        (_b / "copy.json").unlink()
        _s = surfaces(_b)
        ok("missing surfaces are empty strings, never None",
           _s["caption"] == "" and _s["title"] == "")

    ok("check() reads the title when it is given one",
       any("document_title" in p for p in check({"slides": []}, {"aggregates": []},
                                                {"claims": []}, "", _t)))
    ok("...and an undeclared title figure is named as undeclared, not silently passed",
       any("nothing declares" in p for p in check({"slides": []}, {"aggregates": []},
                                                  {"claims": []}, "", _t)))
    ok("a declared title figure that re-derives is clean",
       not check({"slides": []},
                 {"aggregates": [{"phrase": "Fifteen ways", "kind": "count", "value": 15,
                                  "computed_by": "out/2026-08-25/compute.py, restricted_count. "
                                                 "actions by a Texas local government"}]},
                 {"claims": []}, "", _t))

    # `computed_by` IS NOT AN ESCAPE HATCH (2026-08-26). It returned True before any arithmetic
    # ran, so a judge reading the gate rather than its output found that "all re-derived" meant a
    # prose note was present.
    _cb = "out/x/compute.py, some_figure over some_other"
    ok("a ratio with computed_by and a bad `of` now FAILS",
       not rederive({"kind": "ratio", "value": 9, "of": 4, "computed_by": _cb}, {"claims": []})[0])
    ok("...and one with no `of` at all FAILS",
       not rederive({"kind": "ratio", "value": 3, "computed_by": _cb}, {"claims": []})[0])
    ok("a duration with computed_by whose dates do not make its value FAILS",
       not rederive({"kind": "duration", "value": 99, "from_date": "2026-03-10",
                     "to_date": "2026-08-13", "computed_by": _cb}, {"claims": []})[0])
    ok("...and the same duration with the right value passes",
       rederive({"kind": "duration", "value": 156, "from_date": "2026-03-10",
                 "to_date": "2026-08-13", "computed_by": _cb}, {"claims": []})[0])
    ok("a COUNT computed over data still needs no claim per unit, which is the real exemption",
       rederive({"kind": "count", "value": 254,
                 "computed_by": "len() over assets/geo/counties.json"}, {"claims": []})[0])
    ok("a span with computed_by and a reversed pair FAILS",
       not rederive({"kind": "span", "value": 5, "from_date": "2026-08-13",
                     "to_date": "2026-03-10", "computed_by": _cb}, {"claims": []})[0])

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
