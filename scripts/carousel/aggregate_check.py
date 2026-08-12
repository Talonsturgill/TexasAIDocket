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
NUM = r"(?:\d{1,4}|" + "|".join(WORDS) + r")"

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


def to_int(tok: str) -> int | None:
    t = tok.strip().lower()
    if t.isdigit():
        return int(t)
    return WORDS.get(t)


def detect(text: str) -> list[dict]:
    """Every aggregate shape in one rendered string."""
    if EXEMPT.search(text):
        return []
    found = []
    for kind, rx in SHAPES.items():
        for m in rx.finditer(text):
            found.append({"kind": kind, "phrase": m.group(0).strip()})
        if kind in ("ratio", "span") and found:
            # A ratio or a span already explains the numbers inside it, so a count detected in
            # the same string would be the same figure reported twice.
            break
    return found


def scan_report(report: dict) -> list[dict]:
    out = []
    for i, slide in enumerate(report.get("slides") or []):
        name = slide.get("slide") or slide.get("file") or f"slide {i + 1}"
        for node in slide.get("text_nodes") or []:
            txt = (node.get("text") or "").strip()
            if not txt:
                continue
            for d in detect(txt):
                out.append({"slide": name, "text": txt, **d})
    return out


def rederive(decl: dict, claims: dict) -> tuple[bool, str]:
    """Recompute the declared aggregate from the claim ids it names."""
    ids = decl.get("from_claims") or []
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


def run(date: str) -> int:
    base = REPO_ROOT / "out" / date
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
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.date:
        return run(a.date)
    ap.error("give --date or --self-test")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                        # noqa: BLE001
        print(f"aggregate_check: broke: {exc}", file=sys.stderr)
        sys.exit(2)
