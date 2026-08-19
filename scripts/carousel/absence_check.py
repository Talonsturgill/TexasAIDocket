#!/usr/bin/env python3
"""absence_check.py — an absence must be scoped to a document that was fetched.

WHY THIS EXISTS. The compute-not-generate law is enforced on numerals and on nothing else.

`claims_check` proves claims are fetched and quoted. `copy_sync_check` proves the slide says
what copy.json says, and copy.json said it. `aggregate_check` reads numerals. Not one of them
asks whether a NOUN, or a NEGATIVE, came from a source. So a sentence about what a document
does NOT say is the cheapest thing in this whole pipeline to invent, and it is also the most
damaging, because it reads as diligence.

WHAT WENT THROUGH THAT HOLE

  2026-08-16  s6  a Texas county judge renamed "ITS EXECUTIVE"
  2026-08-16  s3  a hook reading "Four signatures" over four rows carrying no signature
  2026-08-18  s7  "One platform, no vendor named", on the frame that then PRINTED a product
                  name, "MAP", one line above the word platform
  2026-08-18  s2  a filled dot inside Harris County for a claim that carries no coordinates
  2026-08-19  s3  three invented Batch Zero categories under a c2 attribution chip. It
                  survived four scoring passes, every gate in the suite, and a pixel review
  2026-08-19  s6  "The Data Center Coalition has not published a statement of its own", which
                  nothing was fetched to support, INTRODUCED BY THE FIX for the one above

THE TELL, which is what makes this checkable at all.

Every HONEST absence in these decks names the document it is scoped to. "not named in the
source". "The calendar names no docket against it." "It states no total." Every FABRICATED one
is scoped to nothing at all: "has not published a statement of its own" names no document,
because there was no document.

So this does not try to decide whether an absence is true. It asks whether the frame says WHERE
it looked. An absence with no document behind it is the signature, and it is the one part of
this a machine can see.

WARN, NOT FAIL, and the reason matters. Deciding whether a sentence is properly scoped is a
judgement, and a gate that hard-fails a correct editorial decision is a gate somebody switches
off, which is written into TECHNIQUE_LIBRARY and into coherence_check for the same reason. The
one case this DOES fail is unambiguous: a frame that asserts an absence while citing no claim
at all has nothing behind it by construction.

Measured against the three shipped decks it raises three warnings, and all three are on frames
that carried a documented absence defect. That is the calibration, not a hope.

    absence_check.py --date 2026-08-19
    absence_check.py --run 2026-08-18        # a shipped run under runs/carousel/
    absence_check.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# A sentence asserting that something is absent, missing, unnamed or did not happen.
NEGATION = re.compile(
    r"\b(?:no|none|never|nobody|nothing|unnamed|neither|nor)\b|\bnot\b|\bn't\b", re.I)

# A word naming a fetched thing.
_DOC = (r"source|sources|release|notice|letter|calendar|filing|filings|record|records|page|"
        r"document|documents|statement|statements|report|feed|docket|dockets|schedule|site|"
        r"announcement|minutes|agenda|study|survey|plan|memo|order|transcript|list|register")

# IT MUST BE A DOCUMENT SOMEBODY OPENED, and one word decides it.
#
# The first draft matched the bare noun and let the real fabrication through, because "has not
# published a statement of its own" CONTAINS the word statement. That statement is the thing
# being said not to exist. An INDEFINITE document is not a place anybody looked.
#
# So a doc word counts as scope unless an indefinite article governs it. Every honest absence in
# the shipped decks satisfies this: "the source", "the commission's own calendar", "The campus
# page", and "ERCOT market notice M-A080326-01", which carries no article at all because it is a
# named document with an identifier, and that is the strongest scoping of the four.
DOC_WORD = re.compile(r"\b(?:" + _DOC + r")\b", re.I)
INDEFINITE = re.compile(r"\b(?:a|an|any|some|no|another)\s+(?:[a-z]+\s+){0,2}$", re.I)


def scoped(text: str) -> bool:
    """True when the text names a document somebody actually opened."""
    for m in DOC_WORD.finditer(text or ""):
        before = text[max(0, m.start() - 40):m.start()]
        if INDEFINITE.search(before):
            continue          # "a statement", "no docket" -- the absent thing, not the source
        yes = re.search(r"\b(?:the|its|this|that|their|our|each)\s+(?:[a-z]+\s+){0,3}$", before, re.I)
        poss = re.search(r"[A-Za-z]+'s\s+(?:[a-z]+\s+){0,2}$", before)
        named = re.search(r"\b[A-Z][A-Za-z]{1,}\s+(?:[a-z]+\s+){0,2}$", before)
        if yes or poss or named:
            return True
    return False


# Furniture that carries a negation without asserting anything about the world.
FURNITURE = re.compile(r"^\s*(?:\d+\s*/\s*\d+|c\d+(?:[ ,]+c\d+)*)\s*$", re.I)


def slide_no(name: str) -> int | None:
    m = re.search(r"(\d+)", str(name or ""))
    return int(m.group(1)) if m else None


def rendered_by_slide(report: dict) -> dict:
    """Slide number to all the text that frame actually printed."""
    out = {}
    for s in report.get("slides") or []:
        n = slide_no(s.get("file") or s.get("png"))
        if n is None:
            continue
        parts = [str(t.get("text", "")) for t in (s.get("text_nodes") or [])]
        out[n] = " ".join(p for p in parts if not FURNITURE.match(p))
    return out


def copy_by_slide(copy: dict) -> dict:
    out = {}
    for sid, s in (copy.get("slides") or {}).items():
        n = slide_no(sid)
        if n is None or not isinstance(s, dict):
            continue
        parts = []
        for k, v in s.items():
            if k == "claims":
                continue
            if isinstance(v, str):
                parts.append(v)
            elif isinstance(v, list):
                parts += [x for x in v if isinstance(x, str)]
        out[n] = " ".join(parts)
    return out


def claims_of(copy: dict, n: int) -> list:
    for sid, s in (copy.get("slides") or {}).items():
        if slide_no(sid) == n and isinstance(s, dict):
            return list(s.get("claims") or [])
    return []


def sentences(text: str) -> list:
    return [p.strip() for p in re.split(r"(?<=[.?!])\s+", text or "") if p.strip()]


def check(copy: dict, report: dict | None) -> tuple:
    fails, warns, stats = [], [], {"absences": 0, "scoped": 0, "slides": 0}
    rendered = rendered_by_slide(report or {})
    authored = copy_by_slide(copy)
    for n in sorted(set(list(rendered) + list(authored))):
        stats["slides"] += 1
        # Prefer what the frame PRINTED. A frame can be scoped by an attribution line that
        # lives in the slide HTML and never entered copy.json, which is exactly how slide 3 of
        # 2026-08-19 is scoped: its kicker cites the ERCOT market notice by name.
        seen = rendered.get(n) or authored.get(n, "")
        scope_pool = " ".join(x for x in (rendered.get(n, ""), authored.get(n, "")) if x)
        for sent in sentences(authored.get(n, "")):
            if not NEGATION.search(sent) or FURNITURE.match(sent):
                continue
            stats["absences"] += 1
            ids = claims_of(copy, n)
            if not ids:
                fails.append(
                    f"slide {n}: {sent[:90]!r} asserts an absence and the frame cites no claim "
                    f"at all, so there is no document behind it by construction")
                continue
            if scoped(scope_pool):
                stats["scoped"] += 1
                continue
            warns.append(
                f"slide {n}: {sent[:90]!r} asserts an absence and nothing on the frame names "
                f"the document it looked in. Every honest absence in this project's shipped "
                f"decks names one ('not named in the source', 'the calendar names no docket "
                f"against it'). Both fabricated ones named nothing. Scope it or drop it")
    return fails, warns, stats


def load(date: str, shipped: bool) -> tuple:
    base = (REPO_ROOT / "runs" / "carousel" / date) if shipped else (REPO_ROOT / "out" / date)
    cp = base / "copy.json"
    rp = (base / "render_report.json") if shipped else (base / "render" / "render_report.json")
    if not cp.exists():
        raise SystemExit(f"absence_check: no copy.json at {cp}")
    report = json.loads(rp.read_text(encoding="utf-8")) if rp.exists() else {}
    return json.loads(cp.read_text(encoding="utf-8")), report


def run(date: str, shipped: bool = False, quiet: bool = False) -> int:
    copy, report = load(date, shipped)
    fails, warns, stats = check(copy, report)
    for w in warns:
        print(f"  warn  {w}", file=sys.stderr)
    if fails:
        print(f"\nabsence_check: {len(fails)} unsupported absence(s)\n", file=sys.stderr)
        for f in fails:
            print(f"  - {f}", file=sys.stderr)
        return 1
    if not quiet:
        print(f"absence_check: {stats['slides']} slide(s), {stats['absences']} absence(s), "
              f"{stats['scoped']} scoped to a named document")
    return 0


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    bad = 0

    def ok(label, cond, extra=""):
        nonlocal bad
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            bad += 1

    def deck(text, ids=("c1",)):
        return {"slides": {"S1": {"dek": text, "claims": list(ids)}}}

    # THE REAL 2026-08-19 FABRICATION. Scoped to nothing.
    f, w, s = check(deck("The Data Center Coalition has not published a statement of its own."), None)
    ok("an absence naming no document is CAUGHT",
       any("names the document it looked in" in x for x in w), str(w))

    # THE REAL HONEST ONES from the same deck. Each names where it looked.
    for good in ("It names no company, no county and no project in the release.",
                 "Public comment deadline, on the commission's own calendar. No docket is named "
                 "against it.",
                 "The campus page lists these pairings. It states no total."):
        f, w, s = check(deck(good), None)
        ok(f"a scoped absence passes: {good[:44]!r}", not w and not f, str(w + f))

    # A frame asserting an absence while citing nothing at all.
    f, w, s = check(deck("Nobody was told.", ids=()), None)
    ok("an absence on a frame citing NO claim is a hard FAIL",
       any("cites no claim" in x for x in f), str(f))

    # Copy with no negation raises nothing.
    f, w, s = check(deck("ERCOT recorded the letter on August 3rd."), None)
    ok("copy with no absence in it raises nothing", not f and not w, str(f + w))

    # Furniture carrying a claim stamp is not an absence.
    f, w, s = check({"slides": {"S1": {"labels": ["c3, c4, c19"], "claims": ["c3"]}}}, None)
    ok("a claim-id footer is not read as an absence", not f and not w, str(f + w))

    # THE SCOPE MAY COME FROM THE RENDER, not only from copy.json. This is the 2026-08-19
    # slide 3 case: the sentence is in copy.json and the attribution that scopes it is a
    # kicker in the slide HTML.
    d = deck("No service provider was to be told by August 7th.")
    rep = {"slides": [{"file": "slide-01.html",
                       "text_nodes": [{"text": "ERCOT market notice M-A080326-01"}]}]}
    f, w, s = check(d, rep)
    ok("an absence scoped by an attribution line in the RENDER passes", not w and not f, str(w + f))

    # ...and the same sentence with nothing naming a document anywhere still warns.
    f, w, s = check(d, {"slides": [{"file": "slide-01.html", "text_nodes": [{"text": "August 7th"}]}]})
    ok("...and the same sentence scoped nowhere still warns", bool(w), str(w))

    # CALIBRATION against the shipped decks. Recorded so a later change that makes this noisy
    # shows up as a number rather than as a feeling.
    for date, ceiling in (("2026-08-16", 2), ("2026-08-18", 3), ("2026-08-19", 3)):
        base = REPO_ROOT / "runs" / "carousel" / date
        if not (base / "copy.json").exists():
            continue
        c, r = load(date, True)
        f, w, s = check(c, r)
        ok(f"{date}: no hard fail on a shipped deck", not f, str(f))
        ok(f"{date}: warnings stay at or under {ceiling}", len(w) <= ceiling,
           f"{len(w)} warnings: {w}")

    print("\nabsence_check self-test: " + ("all passed" if not bad else f"{bad} FAILED"))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date")
    ap.add_argument("--run", help="a shipped run under runs/carousel/")
    ap.add_argument("--all", action="store_true", help="every shipped run")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.all:
        rc = 0
        for d in sorted((REPO_ROOT / "runs" / "carousel").glob("2*")):
            if (d / "copy.json").exists():
                print(f"--- {d.name} ---")
                rc |= run(d.name, shipped=True)
        return rc
    if a.run:
        return run(a.run, shipped=True)
    if not a.date:
        ap.error("--date, --run, --all or --self-test")
    return run(a.date)


if __name__ == "__main__":
    raise SystemExit(main())
