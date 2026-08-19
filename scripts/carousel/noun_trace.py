#!/usr/bin/env python3
"""noun_trace.py — a named thing on a slide has to come from a source.

WHY THIS EXISTS. The other half of the integrity hole `absence_check.py` closed.

The compute-not-generate law is enforced on numerals and on nothing else. `absence_check` now
requires a NEGATIVE to name the document it looked in. This is the positive case: a proper
noun, an organisation, an office or a place printed on a frame is a claim about the world in
exactly the way a number is, and nothing has ever asked where it came from.

WHAT WENT THROUGH THIS HOLE

  2026-08-16  s6  a Texas county judge renamed "ITS EXECUTIVE". The office is executive in
                  function, so a paraphrase read as a description and shipped as a title.
  2026-08-16      a summary asserting the State Affairs charge names SB 6, where none of its
                  five quotes carried the string
  2026-08-18  s2  a filled dot inside HARRIS COUNTY for a claim that carries no coordinates.
                  The deck's own grammar says filled means the source states it.
  2026-08-18  s7  "MAP", a product name, one line above the word platform, on the frame whose
                  entire claim is that no product is named
  2026-08-19  s6  "The Data Center Coalition has not published a statement of its own"

WHAT IT CHECKS, AND THE TWO SHAPES IT DELIBERATELY SEPARATES

  TITLE CASE      two or more capitalised words. This is how a name is written in prose, and
                  it is the highest-signal shape in the deck.
  ALL CAPS        only when it names a place the gazetteer knows. This is the important
                  carve-out and it took a measurement to find.

A deck sets design annotations in all caps: SCALE FIGURE, AT TRUE SCALE, THE ROOF, SAME HUE.
Those are typographic labels, not assertions about the world, and matching every all-caps run
raised thirty candidates on one deck and buried the real one. But HARRIS COUNTY is all caps AND
a real defect. Resolving all-caps runs against `assets/geo/tx-places.json` keeps the place and
drops the label, without a hand-maintained denylist that would go stale the moment a deck
invents a new annotation.

WARN, NEVER FAIL, for the same reason as `absence_check`. A copywriter legitimately writes a
short form the claim spells out in full, and a gate that fires on a correct decision gets
switched off. What it does is put the list in front of a reader who can check it in seconds.

MEASURED ON THE THREE SHIPPED DECKS

    2026-08-16   Elon Musk, The House Committee, State Affairs
    2026-08-18   HARRIS COUNTY, Agenda Ready
    2026-08-19   The Coalition

Two of those six are documented defects in the run records, one is a shorthand this project
introduced itself, and the rest are short forms worth a second look. That ratio is why this
warns rather than fails.

    noun_trace.py --date 2026-08-19
    noun_trace.py --all
    noun_trace.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLACES = REPO_ROOT / "assets" / "geo" / "tx-places.json"

TITLE = re.compile(r"\b[A-Z][a-z]+(?:\s+(?:of|the|and|for)\s+[A-Z][a-z]+|\s+[A-Z][a-z]+)+")
CAPS = re.compile(r"\b[A-Z][A-Z ]{3,}[A-Z]\b")

MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December")

# A capitalised pair whose second word is a month is a date construction, not a name:
# "Checked August", "Announced February". The date itself is checked by aggregate_check.
DATEISH = re.compile(r"\b[A-Z][a-z]+\s+(?:" + "|".join(MONTHS) + r")\b")

CLAIM_FIELDS = ("text", "quote", "verbatim_quote", "publisher", "document", "title", "url",
                "source", "source_title")


def places() -> set:
    if not PLACES.exists():
        return set()
    return {p["name"] for p in (json.loads(PLACES.read_text(encoding="utf-8")).get("places") or [])
            if len(p.get("name", "")) > 4}


def corpus(claims) -> str:
    cs = claims.get("claims") if isinstance(claims, dict) and "claims" in claims else claims
    return " ".join(str(c.get(k, "")) for c in (cs or []) if isinstance(c, dict)
                    for k in CLAIM_FIELDS).lower()


def candidates(text: str, gaz: set) -> list:
    out = []
    for m in TITLE.findall(text or ""):
        m = m.strip()
        if m and not DATEISH.fullmatch(m):
            out.append(m)
    for c in CAPS.findall(text or ""):
        c = c.strip()
        if any(g.upper() in c for g in gaz):
            out.append(c)
    return out


def check(copy: dict, claims) -> tuple:
    gaz = places()
    corp = corpus(claims)
    seen, warns = set(), []
    for sid, s in (copy.get("slides") or {}).items():
        if not isinstance(s, dict):
            continue
        for k, v in s.items():
            if k == "claims":
                continue
            vals = [v] if isinstance(v, str) else (v if isinstance(v, list) else [])
            for val in vals:
                if not isinstance(val, str):
                    continue
                for m in candidates(val, gaz):
                    if m.lower() in corp or m in seen:
                        continue
                    seen.add(m)
                    warns.append(
                        f"{sid}.{k}: {m!r} is printed on a frame and appears in no claim's "
                        f"text, quote, publisher or document. A named thing is a claim about "
                        f"the world in the way a number is. Either it traces to a source or "
                        f"it is the deck's own words for something the source called "
                        f"differently, and only a reader can tell which")
    return [], warns, {"named": len(seen)}


def load(date: str, shipped: bool):
    base = (REPO_ROOT / "runs" / "carousel" / date) if shipped else (REPO_ROOT / "out" / date)
    cp, cl = base / "copy.json", base / "claims.json"
    if not (cp.exists() and cl.exists()):
        raise SystemExit(f"noun_trace: need copy.json and claims.json under {base}")
    return json.loads(cp.read_text(encoding="utf-8")), json.loads(cl.read_text(encoding="utf-8"))


def run(date: str, shipped: bool = False) -> int:
    copy, claims = load(date, shipped)
    fails, warns, stats = check(copy, claims)
    for w in warns:
        print(f"  warn  {w}", file=sys.stderr)
    print(f"noun_trace: {len(warns)} named thing(s) with no claim behind them")
    return 1 if fails else 0


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    bad = 0

    def ok(label, cond, extra=""):
        nonlocal bad
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            bad += 1

    CL = [{"text": "ERCOT told providers the date would not hold.",
           "quote": "will not notify", "publisher": "ERCOT", "url": "https://ercot.com/x"}]

    def deck(s):
        return {"slides": {"S1": {"dek": s, "claims": ["c1"]}}}

    # A NAME NOT IN ANY CLAIM.
    _f, w, _s = check(deck("The Data Center Coalition said so."), CL)
    ok("a named organisation in no claim is CAUGHT", len(w) == 1, str(w))

    # ...and one that IS in a claim passes.
    _f, w, _s = check(deck("ERCOT told providers the date would not hold."), CL)
    ok("a name the claims carry passes", not w, str(w))

    # DESIGN LABELS IN ALL CAPS ARE NOT NAMES. This is the carve-out the measurement forced:
    # matching every all-caps run raised thirty candidates on 2026-08-16 and buried the real one.
    _f, w, _s = check(deck("SCALE FIGURE AT TRUE SCALE THE ROOF SAME HUE"), CL)
    ok("all-caps design annotations are NOT treated as names", not w, str(w))

    # ...but an all-caps PLACE is, which is the 2026-08-18 slide 2 defect.
    _f, w, _s = check(deck("HARRIS COUNTY"), CL)
    ok("an all-caps place the gazetteer knows IS caught", len(w) == 1, str(w))

    # A date construction is not a name.
    _f, w, _s = check(deck("Checked August 19th. Announced February 3rd."), CL)
    ok("'Checked August' and 'Announced February' are not names", not w, str(w))

    # CALIBRATION against the shipped decks, asserted so drift shows up as a number.
    expect = {"2026-08-16": 3, "2026-08-18": 2, "2026-08-19": 1}
    for date, ceiling in expect.items():
        base = REPO_ROOT / "runs" / "carousel" / date
        if not (base / "copy.json").exists():
            continue
        c, cl = load(date, True)
        _f, w, _s = check(c, cl)
        ok(f"{date}: at or under {ceiling} untraced name(s)", len(w) <= ceiling,
           f"{len(w)}: {[x.split(': ')[1][:40] for x in w]}")
        ok(f"{date}: never a hard fail", not _f, str(_f))

    ok("the gazetteer loaded", bool(places()))

    print("\nnoun_trace self-test: " + ("all passed" if not bad else f"{bad} FAILED"))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date")
    ap.add_argument("--run")
    ap.add_argument("--all", action="store_true")
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
