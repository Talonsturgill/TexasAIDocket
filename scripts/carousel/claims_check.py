#!/usr/bin/env python3
"""claims_check.py — the contract between the fact-checker and everything downstream.

WHY THIS EXISTS, BEFORE IT HAS EVER BEEN NEEDED

The fact-checker is an AGENT. It is given a schema in `.claude/agents/carousel-fact-checker.md`
and asked to return JSON, and nothing about that arrangement guarantees it returns the same shape
twice. In the sibling product it drifted, and the drift is worth reading in full because it is
the argument for this file:

  - the container was named `claims`, `verified_claims`, `docket_claims`, and twice the story's
    own codename
  - the same field appeared as `claim`, `text` and `statement`
  - the source appeared as `source_url`, `url` and `evidence_url`
  - one run nested the url, the outlet and the date inside an `evidence` object
  - four runs recorded no per-slide copy at all

None of it was visible, because nothing downstream read the file closely enough to complain. The
site published anyway and **the verification record rendered empty on 14 of 18 decks.** The whole
promise of this project is that every fact traces to a fetched source, and for fourteen decks the
page that demonstrates it was blank.

Texas has shipped zero decks, which is exactly when to install this. A gate written after the
drift is archaeology. A gate written before it is a contract.

WHAT IT IS STRICT ABOUT, AND WHAT IT LEAVES ALONE

Strict about the handful of fields the public site depends on, quiet about everything else. The
fact-checker should stay free to record MORE than the minimum, because the extra is often what a
later run needs. It is not free to record less, or to rename what it records.

    claims_check.py --date 2026-08-12
    claims_check.py --file out/2026-08-12/claims.json
    claims_check.py --self-test

Exit 0 clean, 1 on a hard failure, 2 if the file cannot be read at all.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# THE CONTAINER. One name, and the alternatives are named here so the error can say "you called
# it verified_claims and it is called claims" rather than "missing key".
CONTAINER = "claims"
CONTAINER_ALIASES = ("verified_claims", "docket_claims", "facts", "findings", "verified")

# THE FIELDS THE SITE ACTUALLY READS. Each maps to the aliases seen in the wild, so a rename is
# reported as a rename. `text` is what the record states, `quote` is the verbatim string that
# proves it, and those two are not interchangeable: the whole gate rests on them being separate.
REQUIRED = {
    "id": ("claim_id", "cid", "ref"),
    "text": ("claim", "statement", "assertion"),
    "quote": ("verbatim", "verbatim_quote", "excerpt", "snippet"),
    "url": ("source_url", "evidence_url", "link", "source"),
    "source_type": ("type", "kind", "source_kind"),
    "retrieved": ("retrieved_at", "fetched", "date", "accessed"),
}

# The source taxonomy. A press release is evidence of a press release, and the agent is told so;
# this is where that distinction stops being advice and becomes a schema.
SOURCE_TYPES = {
    "primary_official",     # a filing, a statute, an agency page, a docket entry
    "primary_corporate",    # the company's own announcement. A claim, not a decision.
    "secondary_reported",   # a news report about one of the above
    "data",                 # a dataset or an API response
}

ID_RE = re.compile(r"^c\d+$")
# A claim id has to be stable and referenceable, because slides and captions cite it.

MIN_QUOTE_WORDS = 4
# Below this a "quote" is a fragment that cannot be searched for in the source, which makes it
# unverifiable by the next person, which is the same as not having one.


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check(doc: dict) -> list[str]:
    """Every problem, phrased so somebody can fix it without opening this file."""
    problems: list[str] = []

    if not isinstance(doc, dict):
        return ["the file is not a JSON object"]

    if CONTAINER not in doc:
        found = [k for k in CONTAINER_ALIASES if k in doc]
        if found:
            problems.append(
                f"the claim list is called {found[0]!r} and it must be called {CONTAINER!r}. "
                f"Everything downstream reads {CONTAINER!r}, so a rename here publishes an empty "
                f"verification record rather than failing")
        else:
            problems.append(f"no {CONTAINER!r} key. Keys present: {sorted(doc)[:8]}")
        return problems

    claims = doc[CONTAINER]
    if not isinstance(claims, list):
        return [f"{CONTAINER!r} is {type(claims).__name__}, and it must be a list"]

    # An empty claims file is legitimate but it is never silent: an empty run is one of the three
    # declared causes and has to be a decision rather than an accident.
    if not claims:
        problems.append("the claim list is empty. That is a legitimate outcome and it is never "
                        "an accident: say so explicitly in the run record")

    seen_ids: set[str] = set()
    for i, c in enumerate(claims):
        where = f"claim {i}"
        if not isinstance(c, dict):
            problems.append(f"{where} is {type(c).__name__}, not an object")
            continue
        cid = c.get("id")
        if isinstance(cid, str):
            where = f"claim {cid}"

        for field, aliases in REQUIRED.items():
            if field in c and str(c[field]).strip():
                continue
            wrong = [a for a in aliases if a in c]
            if wrong:
                problems.append(f"{where}: field is called {wrong[0]!r} and must be {field!r}")
            else:
                problems.append(f"{where}: no {field!r}")

        if isinstance(cid, str) and cid:
            if not ID_RE.match(cid):
                problems.append(f"{where}: id must look like c1, c2. Slides cite it")
            if cid in seen_ids:
                problems.append(f"{where}: duplicate id. A citation would be ambiguous")
            seen_ids.add(cid)

        st = c.get("source_type")
        if st and st not in SOURCE_TYPES:
            problems.append(f"{where}: source_type {st!r} is not one of {sorted(SOURCE_TYPES)}")

        q = c.get("quote")
        if isinstance(q, str) and q.strip() and len(q.split()) < MIN_QUOTE_WORDS:
            problems.append(
                f"{where}: the quote is {len(q.split())} words. Under {MIN_QUOTE_WORDS} it cannot "
                f"be searched for in the source, which is the same as not having one")

        # THE ONE THAT MATTERS MOST. `text` is what the record will state and `quote` is the
        # string that proves it. If they are identical the fact-checker has copied the source
        # into the claim rather than verifying a statement against it, and the distinction the
        # whole gate rests on has quietly collapsed.
        t = c.get("text")
        if isinstance(t, str) and isinstance(q, str) and t.strip() and t.strip() == q.strip():
            problems.append(f"{where}: text and quote are identical. One states what the record "
                            f"claims, the other proves it. Identical means nothing was verified")

        u = c.get("url")
        if isinstance(u, str) and u.strip() and not u.startswith(("http://", "https://")):
            problems.append(f"{where}: url {u[:40]!r} is not a fetchable address")

        r = c.get("retrieved")
        if isinstance(r, str) and r.strip():
            try:
                _dt.date.fromisoformat(r.strip())
            except ValueError:
                problems.append(f"{where}: retrieved {r!r} is not an ISO date")

    # REJECTIONS ARE PART OF THE RECORD. The agent is told that rejecting is the job, so a run
    # that rejected nothing is either a suspiciously clean day or an agent that stopped checking.
    # Reported, never failed: a genuinely clean day exists.
    rej = doc.get("rejected")
    if rej is None:
        problems.append("no 'rejected' key. Rejecting is the job, and the reasons are how a "
                        "reader tells an unreachable page from a wrong claim")
    elif isinstance(rej, list):
        for i, r in enumerate(rej):
            if isinstance(r, dict) and not str(r.get("reason", "")).strip():
                problems.append(f"rejection {i}: no reason. 'Could not verify' is not a reason")

    return problems


def run(path: Path) -> int:
    try:
        doc = load(path)
    except FileNotFoundError:
        print(f"claims_check: no file at {path}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"claims_check: {path} is not valid JSON: {exc}", file=sys.stderr)
        return 2

    problems = check(doc)
    n = len(doc.get(CONTAINER) or []) if isinstance(doc.get(CONTAINER), list) else 0
    if problems:
        print(f"claims_check: {len(problems)} problem(s) in {path}\n")
        for p in problems:
            print(f"  - {p}")
        print("\n  The deck is built from this file only. Fix it before Phase 6.")
        return 1
    print(f"claims: clean ({n} verified claim(s), {len(doc.get('rejected') or [])} rejected)")
    return 0


def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    good = {
        "claims": [{
            "id": "c1",
            "text": "The commission set a comment deadline of September 4th, 2026.",
            "quote": "Comments are due no later than September 4, 2026",
            "url": "https://interchange.puc.texas.gov/Documents/58482",
            "source_type": "primary_official",
            "retrieved": "2026-08-12",
            "confidence": "high",
        }],
        "rejected": [{"finding": "a 500 MW figure", "reason": "the filing says 380 MW"}],
    }
    ok("a well formed claims file passes", not check(good), str(check(good))[:110])

    # EVERY DRIFT THE SIBLING ACTUALLY SUFFERED, replayed. This is the list from eighteen runs,
    # and each one shipped silently at the time.
    import copy as _copy                                             # noqa: PLC0415
    for name, mutate in [
        ("the container renamed to verified_claims",
         lambda d: {"verified_claims": d["claims"], "rejected": d["rejected"]}),
        ("the container renamed to a codename",
         lambda d: {"stargate_claims": d["claims"], "rejected": d["rejected"]}),
        ("text renamed to claim",
         lambda d: _swap(d, "text", "claim")),
        ("text renamed to statement",
         lambda d: _swap(d, "text", "statement")),
        ("url renamed to source_url",
         lambda d: _swap(d, "url", "source_url")),
        ("url renamed to evidence_url",
         lambda d: _swap(d, "url", "evidence_url")),
        ("the source nested inside an evidence object",
         lambda d: _nest(d)),
        ("the quote missing entirely",
         lambda d: _drop(d, "quote")),
        ("the retrieved date missing",
         lambda d: _drop(d, "retrieved")),
    ]:
        broken = mutate(_copy.deepcopy(good))
        ok(f"caught: {name}", bool(check(broken)))

    # The narrower faults, which are about quality rather than shape.
    bad_id = _copy.deepcopy(good); bad_id["claims"][0]["id"] = "claim-one"
    ok("caught: an id a slide cannot cite", bool(check(bad_id)))
    dup = _copy.deepcopy(good); dup["claims"].append(dict(dup["claims"][0]))
    ok("caught: two claims sharing an id", any("duplicate" in p for p in check(dup)))
    short = _copy.deepcopy(good); short["claims"][0]["quote"] = "due soon"
    ok("caught: a quote too short to find in the source", bool(check(short)))
    same = _copy.deepcopy(good); same["claims"][0]["quote"] = same["claims"][0]["text"]
    ok("caught: text and quote identical, so nothing was verified",
       any("identical" in p for p in check(same)))
    badtype = _copy.deepcopy(good); badtype["claims"][0]["source_type"] = "press_release"
    ok("caught: a source type outside the taxonomy", bool(check(badtype)))
    badurl = _copy.deepcopy(good); badurl["claims"][0]["url"] = "interchange.puc.texas.gov"
    ok("caught: a url nobody can fetch", bool(check(badurl)))
    baddate = _copy.deepcopy(good); baddate["claims"][0]["retrieved"] = "August 12th"
    ok("caught: a retrieved date that is not ISO", bool(check(baddate)))
    norej = _copy.deepcopy(good); del norej["rejected"]
    ok("caught: no rejection record at all", bool(check(norej)))
    blankrej = _copy.deepcopy(good); blankrej["rejected"] = [{"finding": "x", "reason": " "}]
    ok("caught: a rejection with no reason", bool(check(blankrej)))
    ok("an empty claim list is reported, not passed silently",
       bool(check({"claims": [], "rejected": []})))
    ok("a file that is not an object fails rather than throwing", bool(check(["c1"])))

    if failures:
        print(f"\nclaims_check self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print(f"\nclaims_check self-test: all passed ({len(REQUIRED)} required fields, "
          f"every sibling drift replayed)")
    return 0


def _swap(d: dict, old: str, new: str) -> dict:
    for c in d["claims"]:
        c[new] = c.pop(old)
    return d


def _drop(d: dict, field: str) -> dict:
    for c in d["claims"]:
        c.pop(field, None)
    return d


def _nest(d: dict) -> dict:
    for c in d["claims"]:
        c["evidence"] = {"url": c.pop("url"), "outlet": "PUCT", "date": c.get("retrieved")}
    return d


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date", help="check out/<date>/claims.json")
    ap.add_argument("--file", help="check this file")
    ap.add_argument("--out", default=str(REPO_ROOT / "out"),
                    help="run scratch root, so every gate takes the same flags")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.file:
        return run(Path(a.file))
    if a.date:
        return run(Path(a.out) / a.date / "claims.json")
    ap.error("give --date, --file or --self-test")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                        # noqa: BLE001
        print(f"claims_check: broke: {exc}", file=sys.stderr)
        sys.exit(2)
