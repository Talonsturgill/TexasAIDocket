#!/usr/bin/env python3
"""ask_eval.py — a gold set for the ask box, built from the record and never typed.

WHY THIS EXISTS

Every tuning decision about this box was being made by argument. Is the router accurate. Is a
change to the scorer an improvement or a regression. Is a cheaper model as good. None of those
had a number behind them, and a search box with no eval is a search box tuned by whoever spoke
last.

IT COSTS NOTHING TO RUN. Every case here is scored against the deterministic router in the
page, in a browser, with no model call anywhere. That is a deliberate constraint and not a
limitation: the part of this system that decides WHICH decision answers a question is pure
code, and it is the part that most needs measuring.

THE CASES ARE GENERATED FROM THE RECORD, WHICH IS THE ONLY WAY THIS STAYS HONEST

A hand written gold set rots the moment the record moves, and worse, it gets written by the
same person holding the same assumptions as the scorer. Every case below is derived from what
`ledger/docket.json` actually contains, so the set grows with the record and a case can never
name a decision that is not there.

IT IS NOT DERIVED FROM THE CATALOGUE, and that is the important half. The catalogue is what the
router matches against. Scoring the router on the catalogue's own questions measures whether a
lookup table can find its own keys, which is not a question anybody needed answered. These
cases come from the ITEMS: their titles, the distinctive phrases in their summaries, their
counties and deciders. A reader types what they know about a decision, not the label somebody
filed it under.

THE NEGATIVES MATTER MORE THAN THE POSITIVES

A box that answers everything scores perfectly on recall and is worthless. `nonsense` cases
share nothing with the record and the only correct response is no route at all. This is the
regression that already happened once here: the engine answered "what is the airspeed velocity
of an unladen swallow" with a confident item about air quality permits, because "air" had
entered the vocabulary. That is the single worst thing this box can do, so it is measured.

    ask_eval.py --self-test
    ask_eval.py --out out/ask_eval/gold.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

LEDGER = REPO_ROOT / "ledger" / "docket.json"

# Words that carry no signal about WHICH decision is meant. A query trimmed to these is a query
# about nothing, and a case built from one would score the router on noise.
NOISE = {
    "the", "and", "for", "from", "with", "this", "that", "are", "was", "were", "has", "have",
    "had", "will", "its", "it", "a", "an", "of", "to", "in", "on", "at", "by", "or", "as",
    "is", "be", "been", "not", "no", "new", "county", "texas", "state", "city", "public",
    "commission", "department", "board", "council", "court", "office", "district",
}

# A NONSENSE CASE HAS TO SHARE NOTHING, and proving that is part of building it. These are
# checked against the record's own vocabulary at build time, so a phrase that quietly becomes
# meaningful as the record grows is dropped from the set rather than silently scored as a
# false positive forever. The swallow is here because it is the one that actually shipped.
NONSENSE = [
    "what is the airspeed velocity of an unladen swallow",
    "how do i bake sourdough bread overnight",
    "who won the world cup in nineteen eighty six",
    "recipe for banana bread with walnuts",
    "what time does the pharmacy close on sunday",
    "how tall is mount kilimanjaro in metres",
    "best way to train for a marathon",
    "lyrics to a song about a lonely astronaut",
]


def words(text: str) -> list[str]:
    return [w for w in re.sub(r"[^a-z0-9 ]+", " ", (text or "").lower()).split() if w]


def content_words(text: str, least: int = 4) -> list[str]:
    return [w for w in words(text) if len(w) >= least and w not in NOISE]


def load_items(path: Path | None = None) -> list[dict]:
    p = path or LEDGER
    return json.loads(p.read_text(encoding="utf-8"))["items"]


def vocabulary(items: list[dict]) -> set[str]:
    """Every content word the record uses anywhere. A nonsense case may share none of it."""
    v: set[str] = set()
    for it in items:
        v.update(content_words(it.get("title", "")))
        v.update(content_words(it.get("summary", "")))
        d = (it.get("decider") or {}).get("name", "")
        v.update(content_words(d))
    return v


def distinctive(items: list[dict], it: dict, n: int = 4) -> list[str]:
    """The words in this item that fewest OTHER items also use.

    A phrase case built from common words tests nothing: "data center power" matches twenty
    decisions and the router is right to be unsure. Rarity is what makes a case decidable, and
    it is computed against the record rather than guessed.
    """
    here = set(content_words(it.get("title", "")) + content_words(it.get("summary", "")))
    df: dict[str, int] = {}
    for other in items:
        seen = set(content_words(other.get("title", "")) + content_words(other.get("summary", "")))
        for w in here & seen:
            df[w] = df.get(w, 0) + 1
    return [w for w, _ in sorted(df.items(), key=lambda kv: (kv[1], kv[0]))[:n]]


def build(items: list[dict]) -> list[dict]:
    """Every case, each carrying the kind it belongs to so failures are readable by kind."""
    vocab = vocabulary(items)
    cases: list[dict] = []

    for it in items:
        iid, title = it.get("id"), it.get("title") or ""
        if not iid or not title:
            continue

        # THE TITLE, TRIMMED THE WAY A PERSON TYPES. Nobody types a filing headline in full, so
        # the case is its content words, which is what somebody who half remembers it would
        # give you. The full title would test string equality and pass forever.
        tw = content_words(title)
        if len(tw) >= 3:
            cases.append({"kind": "title", "q": " ".join(tw[:6]), "item": iid})

        # A DISTINCTIVE PHRASE from the body. This is the case that most resembles a real
        # question: somebody remembers a detail and not the headline.
        rare = distinctive(items, it)
        if len(rare) >= 3:
            cases.append({"kind": "phrase", "q": " ".join(rare[:3]), "item": iid})

        # THE COUNTY, WITH THE WORD, because the record's own rule is that "county" decides
        # between a county and the city that shares its name.
        geo = it.get("geography") or {}
        for c in (geo.get("counties") or [])[:1]:
            cases.append({"kind": "county", "q": f"{c} county", "view": "by_county", "arg": c})

        d = (it.get("decider") or {}).get("name")
        if d:
            cases.append({"kind": "decider", "q": d, "view": "by_decider", "arg": d})

        t = it.get("topic")
        if t:
            cases.append({"kind": "topic_item", "q": t.replace("-", " "), "view": "by_topic",
                          "arg": t})

    # THE NEGATIVES, EACH PROVED TO SHARE NOTHING WITH THE RECORD. A phrase that stops being
    # nonsense because the record grew into it is dropped here rather than scored forever as a
    # failure the router cannot fix.
    for q in NONSENSE:
        shared = sorted(set(content_words(q)) & vocab)
        if shared:
            continue
        cases.append({"kind": "nonsense", "q": q, "item": None, "expect_none": True})

    # Deduplicated on the query text. A county named by four decisions is one case, not four,
    # and counting it four times would weight the score by how busy a county is.
    seen: set[str] = set()
    out: list[dict] = []
    for c in cases:
        if c["q"] in seen:
            continue
        seen.add(c["q"])
        out.append(c)
    return out


def summarise(cases: list[dict]) -> dict:
    by: dict[str, int] = {}
    for c in cases:
        by[c["kind"]] = by.get(c["kind"], 0) + 1
    return {"total": len(cases), "by_kind": dict(sorted(by.items()))}


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    fails = 0

    def ok(label, cond, extra=""):
        nonlocal fails
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + str(extra)}")
        if not cond:
            fails += 1

    fake = [
        {"id": "x-1", "title": "Palo Pinto hyperscale substation energisation approved",
         "topic": "power-and-the-grid", "status": "decided",
         "decider": {"name": "Palo Pinto County Commissioners Court"},
         "geography": {"counties": ["Palo Pinto"]},
         "summary": "The court approved an energisation schedule for a hyperscale substation."},
        {"id": "x-2", "title": "Groundwater district denies a cooling withdrawal permit",
         "topic": "land-water-and-permitting", "status": "decided",
         "decider": {"name": "Middle Trinity Groundwater Conservation District"},
         "geography": {"counties": ["Erath"]},
         "summary": "The district denied a withdrawal permit sought for evaporative cooling."},
    ]
    cases = build(fake)
    kinds = {c["kind"] for c in cases}

    ok("a title becomes a case", any(c["kind"] == "title" for c in cases))
    ok("...trimmed to what a person would actually type",
       all(len(c["q"].split()) <= 6 for c in cases if c["kind"] == "title"))
    ok("...and it keeps the word that identifies the item",
       any("hyperscale" in c["q"] or "energisation" in c["q"]
           for c in cases if c["kind"] == "title" and c["item"] == "x-1"))
    ok("a distinctive phrase becomes a case", "phrase" in kinds)
    ok("a county case carries the word county, which is what disambiguates it",
       all(c["q"].endswith(" county") for c in cases if c["kind"] == "county"))
    ok("a decider becomes a case", any(c["view"] == "by_decider" for c in cases if "view" in c))

    # THE NEGATIVES ARE THE POINT. A record that has grown into a phrase must drop it.
    ok("nonsense that shares nothing with the record is kept",
       any(c["kind"] == "nonsense" for c in cases))
    grown = fake + [{"id": "x-3", "title": "Sourdough bakery zoning", "topic": "state-policy",
                     "decider": {"name": "City"}, "geography": {},
                     "summary": "A bakery asked about overnight sourdough bread production."}]
    qs = {c["q"] for c in build(grown) if c["kind"] == "nonsense"}
    ok("...and a phrase the record grew into is dropped rather than scored forever",
       "how do i bake sourdough bread overnight" not in qs, sorted(qs))

    ok("every case names either an item or a view, never neither",
       all(("item" in c) or ("view" in c) for c in cases))
    ok("queries are unique, so a busy county is not counted four times",
       len({c["q"] for c in cases}) == len(cases))

    # And against the real record, which is the set that will actually be run.
    if LEDGER.is_file():
        real = build(load_items())
        s = summarise(real)
        ok("the real record produces a set worth running", s["total"] > 100, s)
        ok("...with negatives in it", s["by_kind"].get("nonsense", 0) >= 4, s["by_kind"])
        print(f"\n  built from the record: {json.dumps(s['by_kind'])}, {s['total']} cases")

    print(f"\nask_eval self-test: {'all passed' if not fails else str(fails) + ' FAILED'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--out", help="write the gold set here as JSON")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    cases = build(load_items())
    blob = json.dumps({"cases": cases, "summary": summarise(cases)}, indent=1)
    if a.out:
        p = Path(a.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(blob + "\n", encoding="utf-8")
        print(f"{len(cases)} case(s) -> {a.out}")
    else:
        print(blob)
    return 0


if __name__ == "__main__":
    sys.exit(main())
