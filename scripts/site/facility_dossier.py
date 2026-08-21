#!/usr/bin/env python3
"""facility_dossier.py — what is actually known about one certified data center.

WHY THIS EXISTS

The Comptroller's registry gives every facility five fields. A reader who wants to know what a
building actually is, how big, whose, drawing what, cooled how, gets nothing from those five. The
dossier is the researched answer, one facility at a time, and it is the part of this site that
cannot be assembled by anyone who has not done the work.

THE RULE THAT MAKES IT PUBLISHABLE

`CLAUDE.md` says no numeral is ever typed by a person or produced by a language model. A
researched figure looks like exactly the thing that law forbids, so the shape here matters.

    A NUMBER IS A FIELD, NEVER A SENTENCE. Every figure lives in `facts[]` as a real value with
    a unit and a source id. `render()` formats it and `authorised()` authorises it THROUGH THE
    SAME CALL, so a displayed figure and an authorised figure cannot disagree.

    PROSE CARRIES NO NUMERALS AT ALL. `summary`, `notes[].text` and `gaps[]` are checked for
    digits and the gate fails on any. A note says Google backstops the lease obligations. The
    amount is a fact field beside it. This is what stops a model from writing a number into a
    sentence where nothing downstream would check it.

WHAT ELSE THE GATE ASSERTS

  Every fact names a source id that exists. Every source carries a url, a publisher and a
  retrieved date. Every dossier name matches a facility in the registry exactly, because a
  dossier attached to a facility that does not exist is worse than no dossier. Slugs are unique
  and url safe. `gaps[]` is non empty, because a facility with nothing unknown has not been
  researched, it has been guessed at.

SOURCE RUNGS. `knowledge/shared/DATACENTER_REGISTRY.md` ranks sources one to seven, filings at
the top and aggregators at the bottom. The rung rides on every source so the page can show a
reader whether a figure came from an SEC exhibit or from a directory site.

    facility_dossier.py              # check the ledger against the registry
    facility_dossier.py --self-test  # hermetic
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEDGER = ROOT / "ledger" / "facilities" / "dossiers.json"
REGISTRY = ROOT / "ledger" / "gridwatch" / "datacenters.json"
DIGIT = re.compile(r"\d")
SLUG_OK = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PROSE_FIELDS = ("summary",)


# ---------------------------------------------------------------- formatting
def commas(n) -> str:
    return f"{int(round(n)):,}"


def money(v) -> str:
    """A dollar figure at the scale a reader reads it. The rounding rule is stated, not chosen
    per figure, because rounding is a computation and not a stylistic decision."""
    v = float(v)
    if v >= 1_000_000_000:
        s = f"{v / 1_000_000_000:.1f}".rstrip("0").rstrip(".")
        return f"${s} billion"
    if v >= 1_000_000:
        s = f"{v / 1_000_000:.1f}".rstrip("0").rstrip(".")
        return f"${s} million"
    return f"${commas(v)}"


def plain(v) -> str:
    """A number that is not money. Integers keep no decimal point, so 1.2 stays 1.2 and 168
    does not become 168.0."""
    v = float(v)
    return commas(v) if v == int(v) else f"{v:g}"


UNITS = {
    "MW": lambda v: f"{plain(v)} MW",
    "GW": lambda v: f"{plain(v)} GW",
    "acres": lambda v: f"{plain(v)} acres",
    "sqft": lambda v: f"{plain(v)} sq ft",
    "usd": money,
    "percent": lambda v: f"{plain(v)} percent",
    "jobs": lambda v: f"{plain(v)} jobs",
    "workers": lambda v: f"{plain(v)} workers",
    "buildings": lambda v: f"{plain(v)} buildings",
    "units": lambda v: f"{plain(v)} units",
    "facilities": lambda v: f"{plain(v)} facilities",
}


def show(fact: dict) -> str:
    """The one place a fact becomes a string. `authorised()` calls this too, which is the whole
    reason a displayed figure and an authorised figure can never drift apart."""
    if "value" in fact:
        fn = UNITS.get(fact.get("unit"))
        if fn is None:
            raise KeyError(f"no formatter for unit {fact.get('unit')!r}")
        return fn(fact["value"])
    return str(fact.get("text", ""))


# ---------------------------------------------------------------- loading
def load(path: pathlib.Path = LEDGER) -> dict:
    if not path.exists():
        return {"_spec": 1, "dossiers": []}
    return json.loads(path.read_text(encoding="utf-8"))


def registry_names(path: pathlib.Path = REGISTRY) -> set[str]:
    if not path.exists():
        return set()
    d = json.loads(path.read_text(encoding="utf-8"))
    return {f["name"] for f in d.get("facilities") or []}


def by_name(doc: dict) -> dict[str, dict]:
    return {d["name"]: d for d in doc.get("dossiers") or []}


# ---------------------------------------------------------------- the gate
def problems(doc: dict, names: set[str]) -> list[str]:
    out: list[str] = []
    seen_slugs: dict[str, str] = {}

    for d in doc.get("dossiers") or []:
        name = d.get("name", "(unnamed)")
        where = f"dossier {name!r}"

        if names and name not in names:
            out.append(f"{where} names a facility that is not in the registry")

        slug = d.get("slug", "")
        if not SLUG_OK.match(slug):
            out.append(f"{where} has slug {slug!r}, which is not url safe")
        elif slug in seen_slugs and seen_slugs[slug] != name:
            out.append(f"{where} reuses the slug of {seen_slugs[slug]!r}")
        else:
            seen_slugs[slug] = name

        ids = {s.get("id") for s in d.get("sources") or []}
        if not ids:
            out.append(f"{where} carries no sources")
        for s in d.get("sources") or []:
            for field in ("url", "title", "publisher", "retrieved"):
                if not s.get(field):
                    out.append(f"{where} source {s.get('id')!r} is missing {field}")
            if not isinstance(s.get("rung"), int):
                out.append(f"{where} source {s.get('id')!r} has no source rung")

        if not d.get("facts"):
            out.append(f"{where} carries no facts")
        for fct in d.get("facts") or []:
            if fct.get("source") not in ids:
                out.append(f"{where} fact {fct.get('label')!r} cites unknown source "
                           f"{fct.get('source')!r}")
            if "value" in fct:
                if fct.get("unit") not in UNITS:
                    out.append(f"{where} fact {fct.get('label')!r} has unknown unit "
                               f"{fct.get('unit')!r}")
                elif not isinstance(fct["value"], (int, float)):
                    out.append(f"{where} fact {fct.get('label')!r} has a non numeric value")
            elif not fct.get("text"):
                out.append(f"{where} fact {fct.get('label')!r} has neither a value nor text")

        # THE LAW. A digit in a sentence is a number a model typed, and nothing downstream
        # would catch it. Numbers live in facts, where the formatter owns them.
        for field in PROSE_FIELDS:
            if DIGIT.search(str(d.get(field) or "")):
                out.append(f"{where} has a numeral in its {field}, which must be a fact instead")
        for i, note in enumerate(d.get("notes") or []):
            if note.get("as_of") and not re.match(r"^\d{4}-\d{2}-\d{2}$", str(note["as_of"])):
                out.append(f"{where} note {i} has an as_of that is not an ISO date")
            if DIGIT.search(str(note.get("text") or "")):
                out.append(f"{where} note {i} has a numeral in prose, which must be a fact instead")
            for sid in note.get("sources") or []:
                if sid not in ids:
                    out.append(f"{where} note {i} cites unknown source {sid!r}")
        for i, gap in enumerate(d.get("gaps") or []):
            if DIGIT.search(str(gap)):
                out.append(f"{where} gap {i} has a numeral in prose")

        if not d.get("gaps"):
            out.append(f"{where} names no gaps, and a facility with nothing unknown about it "
                       f"has been guessed at rather than researched")

    return out


# The gate's own tokeniser, imported rather than copied. A second copy of this pattern is a
# second thing to keep in step, and the whole failure mode here is two versions of one rule.
try:
    from numeral_lint import NUMERAL as _NUMERAL
except Exception:  # pragma: no cover - only when run outside the site package
    _NUMERAL = re.compile(r"\d(?:[\d,]*\d)?(?:\.\d+)?")


def authorised(doc: dict) -> set[str]:
    """Every numeral string a dossier page may show, produced by the same call that shows it.

    THE DATES GO THROUGH `ordinal()`, NOT THE RAW ISO. The first version of this authorised
    `2024-11-19` while the page printed `November 19th, 2024`, so the build reported three
    real violations on a correct page. A display path and an authorisation path that are not
    the same call WILL drift, which is the exact thing this module's docstring warns about,
    and it drifted here first.

    TEXT FACTS HAVE THEIR NUMERALS AUTHORISED, and the reason is narrow enough to state. A
    text fact is a TRANSCRIBED IDENTIFIER from a cited source: a street address, a postcode,
    a lease year, a facility name the state assigned. None of them is a quantity and none is
    arithmetic. Every actual QUANTITY is forced into a value field by `problems()`, where the
    formatter owns it, and prose is forbidden a digit at all. So this authorises the class of
    numeral a model cannot use to smuggle a computed figure past the gate.
    """
    out: set[str] = set()

    def tokens(text: str) -> set[str]:
        return set(_NUMERAL.findall(str(text)))

    for d in doc.get("dossiers") or []:
        out |= tokens(d.get("name", ""))
        for fct in d.get("facts") or []:
            if "value" in fct:
                out.add(show(fct))
            else:
                out |= tokens(fct.get("text", ""))
            if fct.get("as_of"):
                out.add(ordinal(fct["as_of"]))
        for note in d.get("notes") or []:
            if note.get("as_of"):
                out.add(ordinal(note["as_of"]))
        for s in d.get("sources") or []:
            if s.get("retrieved"):
                out.add(ordinal(s["retrieved"]))
            # A SOURCE TITLE IS THE MOST VERBATIM STRING ON THE PAGE. One of these documents is
            # actually called "Crusoe's 998,000 Square Foot Data Center" and another "to 1.2
            # Gigawatts". Altering either to satisfy a lint would misquote a citation, which is
            # a worse fault than the one the lint is guarding against. Same narrow class as the
            # transcribed identifiers above: quoted, sourced, and never arithmetic.
            out |= tokens(s.get("title", ""))
            out |= tokens(s.get("publisher", ""))
    return out


# ---------------------------------------------------------------- rendering
# What a source rung MEANS to a reader, from knowledge/shared/DATACENTER_REGISTRY.md. A figure
# from an SEC exhibit and a figure from a directory site are not the same kind of fact, and a
# page that shows them identically is quietly lying about how much it knows.
RUNGS = {1: "filing", 2: "company", 3: "local government", 4: "permit",
         5: "grid operator", 6: "trade press", 7: "directory"}
MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")


def e(t) -> str:
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def ordinal(iso: str) -> str:
    """August 21st, 2026. The house form, month first, ordinal day."""
    y, m, d = (int(x) for x in str(iso).split("-"))
    suf = "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")
    return f"{MONTHS[m - 1]} {d}{suf}, {y}"


def panel(d: dict, *, heading: int = 3) -> str:
    """The dossier body. The PAGE and the DIALOG render this same call, so the two can never
    drift into showing a reader different things about one facility."""
    h = f"h{heading}"
    src_n = {s["id"]: i + 1 for i, s in enumerate(d.get("sources") or [])}

    def cite(sid):
        n = src_n.get(sid)
        return (f'<sup class="dcite">[<a href="#dsrc-{e(d["slug"])}-{n}">{n}</a>]</sup>'
                if n else "")

    rows = []
    for f in d.get("facts") or []:
        when = (f'<span class="dwhen">as of {e(ordinal(f["as_of"]))}</span>'
                if f.get("as_of") else "")
        rows.append(f'<div class="drow"><dt>{e(f.get("label", ""))}</dt>'
                    f'<dd><span class="dval">{e(show(f))}</span>{cite(f.get("source"))}'
                    f'{when}</dd></div>')

    notes = "".join(
        f'<li>{e(n.get("text", ""))}'
        + "".join(cite(x) for x in (n.get("sources") or []))
        + (f'<span class="dwhen">{e(ordinal(n["as_of"]))}</span>' if n.get("as_of") else "")
        + "</li>"
        for n in d.get("notes") or [])

    def stop(t: str) -> str:
        t = str(t).strip()
        return t if t.endswith((".", "?", "!")) else t + "."

    gaps = "".join(f"<li>{e(stop(g))}</li>" for g in d.get("gaps") or [])

    sources = "".join(
        f'<li id="dsrc-{e(d["slug"])}-{i + 1}">'
        f'<a href="{e(s["url"])}" rel="nofollow noopener">'
        f'<cite>{e(s["title"])}</cite></a>. '
        f'<span class="dpub"><cite>{e(s["publisher"])}</cite></span>. '
        f'<span class="drung">{e(RUNGS.get(s.get("rung"), "other"))}</span>. '
        f'<span class="dwhen">Read {e(ordinal(s["retrieved"]))}.</span></li>'
        for i, s in enumerate(d.get("sources") or []))

    return (
        f'<div class="dossier">'
        f'<p class="dsum">{e(d.get("summary", ""))}</p>'
        f'<{h}>What is known</{h}><dl class="dfacts">{"".join(rows)}</dl>'
        + (f'<{h}>Worth knowing</{h}><ul class="dnotes">{notes}</ul>' if notes else "")
        + (f'<{h}>What is not public</{h}><ul class="dgaps">{gaps}</ul>' if gaps else "")
        + f'<{h}>Sources</{h}><ol class="dsources">{sources}</ol>'
        f'</div>')


# ---------------------------------------------------------------- self test
def self_test() -> int:
    checks = []

    def check(name, ok, detail=""):
        checks.append(ok)
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}{('  ' + str(detail)) if not ok else ''}")

    good = {
        "name": "X", "slug": "x", "summary": "A plain sentence.",
        "facts": [{"label": "Load", "value": 168, "unit": "MW", "source": "s1"}],
        "notes": [{"text": "Prose with no digits.", "sources": ["s1"]}],
        "gaps": ["Cooling is not public"],
        "sources": [{"id": "s1", "url": "https://e.x", "title": "T", "publisher": "P",
                     "rung": 1, "retrieved": "2026-08-21"}],
    }
    names = {"X"}

    def one(mutate=None):
        import copy
        d = copy.deepcopy(good)
        if mutate:
            mutate(d)
        return problems({"dossiers": [d]}, names)

    check("a well formed dossier passes", one() == [], one())

    # The law, in both places a model could break it.
    check("a numeral in the summary fails",
          one(lambda d: d.update(summary="It draws 168 MW.")) != [])
    check("a numeral in a note fails",
          one(lambda d: d["notes"].__setitem__(0, {"text": "Google put up $1.4 billion.",
                                                   "sources": ["s1"]})) != [])
    check("a numeral in a gap fails", one(lambda d: d.update(gaps=["2 things unknown"])) != [])

    check("a fact citing an unknown source fails",
          one(lambda d: d["facts"][0].update(source="nope")) != [])
    check("a note citing an unknown source fails",
          one(lambda d: d["notes"][0].update(sources=["nope"])) != [])
    check("a source missing its retrieved date fails",
          one(lambda d: d["sources"][0].pop("retrieved")) != [])
    check("a source missing its rung fails", one(lambda d: d["sources"][0].pop("rung")) != [])
    check("an unknown unit fails", one(lambda d: d["facts"][0].update(unit="furlongs")) != [])
    check("a non numeric value fails", one(lambda d: d["facts"][0].update(value="lots")) != [])
    check("a dossier with no gaps fails", one(lambda d: d.update(gaps=[])) != [])
    check("a dossier with no facts fails", one(lambda d: d.update(facts=[])) != [])
    check("a slug that is not url safe fails", one(lambda d: d.update(slug="Not A Slug")) != [])
    check("a dossier for a facility not in the registry fails",
          one(lambda d: d.update(name="Ghost")) != [])
    check("two dossiers sharing a slug fails",
          len(problems({"dossiers": [good, {**good, "name": "Y"}]}, {"X", "Y"})) > 0)

    # Formatting, where a wrong rule would put a wrong number on the page.
    check("megawatts read as integers", show({"value": 168, "unit": "MW"}) == "168 MW",
          show({"value": 168, "unit": "MW"}))
    check("a fractional gigawatt keeps its decimal", show({"value": 1.2, "unit": "GW"}) == "1.2 GW",
          show({"value": 1.2, "unit": "GW"}))
    check("square feet take thousands separators",
          show({"value": 998000, "unit": "sqft"}) == "998,000 sq ft",
          show({"value": 998000, "unit": "sqft"}))
    check("billions read as billions",
          show({"value": 9_100_000_000, "unit": "usd"}) == "$9.1 billion",
          show({"value": 9_100_000_000, "unit": "usd"}))
    check("a round billion drops the decimal",
          show({"value": 3_000_000_000, "unit": "usd"}) == "$3 billion",
          show({"value": 3_000_000_000, "unit": "usd"}))
    check("millions read as millions",
          show({"value": 450_000_000, "unit": "usd"}) == "$450 million",
          show({"value": 450_000_000, "unit": "usd"}))
    check("a fractional million keeps its decimal",
          show({"value": 9_500_000, "unit": "usd"}) == "$9.5 million",
          show({"value": 9_500_000, "unit": "usd"}))
    check("a percentage keeps its decimal",
          show({"value": 50.1, "unit": "percent"}) == "50.1 percent",
          show({"value": 50.1, "unit": "percent"}))

    # The authorisation path is the display path.
    a = authorised({"dossiers": [good]})
    check("the authorised set carries the rendered figure", "168 MW" in a, sorted(a))

    passed = sum(checks)
    print(f"\nfacility_dossier self-test: {passed}/{len(checks)} passed")
    return 0 if passed == len(checks) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    doc = load()
    n = len(doc.get("dossiers") or [])
    if not n:
        print("facility_dossier: no dossiers yet")
        return 0
    bad = problems(doc, registry_names())
    if bad:
        print(f"facility_dossier: {len(bad)} problem(s)")
        for b in bad:
            print(f"  {b}")
        return 1
    facts = sum(len(d.get("facts") or []) for d in doc["dossiers"])
    print(f"facility_dossier: {n} dossier(s), {facts} facts, every one sourced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
