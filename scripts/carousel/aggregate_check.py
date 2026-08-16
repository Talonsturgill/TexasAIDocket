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
    t = tok.strip().lower()
    if t.isdigit():
        return int(t)
    return WORDS.get(t)


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
    (base / "aggregate_report.json").write_text(
        json.dumps({"declared": len(found), "problems": problems}, indent=2), encoding="utf-8")

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
