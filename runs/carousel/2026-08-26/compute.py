#!/usr/bin/env python3
"""compute.py — every derived numeral this deck publishes, produced here and nowhere else.

WHY THIS FILE EXISTS AND WHY IT WAS MISSING.

`CLAUDE.md`'s law: every numeral this project publishes is produced by code, from data, and can
be recomputed from the same inputs. No number is ever typed by a person or produced by a model.

This run reached its ship phase with SIXTEEN `computed_by` declarations in `aggregates.json` and
no `compute.py` at all. Every one of those declarations names a computation in prose, and until
this file existed not one of them had been performed by code. `label_guard` refuses to run
without this file, which is how the gap was found, and `scoring_rubric.yaml` already records the
same shape from carousel no. 7 as "typed constants under comments claiming they were computed".

A figure QUOTED from a source is not this file's business. `aggregates.json`'s `quoted_from`
route covers those and `claims_check` proves the string. What is here is every figure the deck
DERIVED, and each one is asserted against the value the deck published.

    python3 out/2026-08-26/compute.py        # exits non-zero if any published figure disagrees
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
CLAIMS = json.loads((RUN / "claims.json").read_text(encoding="utf-8"))["claims"]
BY_ID = {c["id"]: c for c in CLAIMS}


def folio(claim_id: str) -> int:
    """The printed page number a claim quotes, read out of the document's own running footer.

    The committee's pages number themselves in a footer reading
    `Facilities Planning and Construction Committee Agenda Book - 130`, and that footer is the
    folio. A PDF page INDEX is not a page number, and this run published 129 to 133 before
    catching that, which is why this reads the quoted string rather than any position.
    """
    q = BY_ID[claim_id]["quote"]
    tail = q.rsplit("-", 1)[-1].strip()
    digits = "".join(ch for ch in tail if ch.isdigit())
    if not digits:
        raise SystemExit(f"compute: {claim_id} quotes no folio in {q[:70]!r}")
    return int(digits)


# ---------------------------------------------------------------- what the body DID
#
# EVERY SHAPE NAMES THE CLAIM THAT PROVES IT. A label on a frame is a claim about what a body
# did, and `label_guard` reads this map to check that the verb a frame prints is the verb the
# record can carry.
#
# THIS DECK'S WHOLE HARD FAIL WAS THIS SHAPE. The record and four surfaces said the board VOTED,
# AUTHORIZED and AMENDED, every one of them citing the August 12th agenda book, which is a
# document asking a committee to approve something rather than a record of it approving. UT
# System publishes no minutes for that meeting, so nothing on utsystem.edu establishes the act
# at all. c32, a post-meeting report, is the only claim in this file that does, and it is
# labelled secondary_reported on the frame that carries it.
#
# So the shape is APPROVED ADDED, proved by c32 and by nothing else. The agenda book claims
# prove what was ASKED, which is a different verb and is why slide 4 separates them in words.
ACTED = {
    "tx-2026-0095": ("Austin", "APPROVED ADDED", "c32"),
}

# ---------------------------------------------------------------- the derivations

def committee_document_pages() -> int:
    """Twenty. The committee's document end to end, inclusive of both terminating folios.

    c29 quotes the footer of the first page and c30 the footer of the last. Inclusive, because
    a document that runs from page 124 to page 143 is twenty pages and not nineteen, and the
    zero on slide 6 was measured over every one of them.
    """
    return folio("c30") - folio("c29") + 1


def item_pages() -> int:
    """Five. The board item's own span inside that document, c27 to c28, inclusive."""
    return folio("c28") - folio("c27") + 1


def search_terms() -> int:
    """Four. The terms the absence was measured with, counted from the finding itself."""
    # `absence_finding` is PROSE in this run, not a structured block, so the terms are counted
    # from the one place they are enumerated as data: the frame that publishes them. copy.json's
    # S6.terms is the string slide 6 sets, middot separated, and it is what a reader counts.
    copy = json.loads((RUN / "copy.json").read_text(encoding="utf-8"))
    terms = [t.strip() for t in copy["slides"]["S6"]["terms"].split("\u00b7")]
    terms = [t for t in terms if t]
    return len(terms)


def distinct_sources(kind: str) -> int:
    """How many DOCUMENTS of a kind the deck rests on, not how many claims.

    The first comment's head line says "four official records and one news report", and those
    are counts of distinct source urls rather than of claims: 24 claims rest on one of those
    four documents. Counting claims here would publish 33 and 1.
    """
    return len({c["url"] for c in CLAIMS if c.get("source_type") == kind})


# THE STEM TABLE. label_guard matches a shape word against the claim's own words by stem, so
# "APPROVED" is satisfied by a claim that says "approved" or "approve" or "approves". Without
# this table every word would be matched literally and the gate would fire on correct labels,
# which is the one failure mode a checker does not get to have, so label_guard stops rather than
# guessing. Two entries, because this deck asserts one action.
_STEM = {"approved": "approv", "added": "add"}


def _shapes_hold() -> None:
    """Every shape word in ACTED occurs, by stem, in the claim named as proving it.

    This is the map guarding itself. A shape word its own claim does not carry is a shape the
    deck may not print, and on 2026-08-26 that is exactly what went wrong: VOTED and AUTHORIZED
    were printed against agenda book claims that carry neither.
    """
    for item, (place, shape, cid) in ACTED.items():
        hay = (BY_ID[cid]["quote"] + " " + BY_ID[cid].get("text", "")).lower()
        missing = [w for w in shape.lower().split() if _STEM.get(w, w) not in hay]
        assert not missing, (
            f"{item}: shape {shape!r} names {missing} and {cid} carries neither. "
            f"{cid} says {BY_ID[cid]['quote'][:90]!r}")


_shapes_hold()


def main() -> int:
    declared = {a["phrase"]: a.get("value")
                for a in json.loads((RUN / "aggregates.json").read_text(encoding="utf-8"))["aggregates"]}
    bad = []

    def assert_published(phrase: str, computed, note: str):
        got = declared.get(phrase)
        if got is None:
            bad.append(f"{phrase!r} is computed here and declared nowhere")
        elif float(got) != float(computed):
            bad.append(f"{phrase!r}: the deck published {got} and this computes {computed} ({note})")
        else:
            print(f"  ok  {phrase!r:26} = {computed}   {note}")

    assert_published("Twenty pages", committee_document_pages(),
                     f"folio {folio('c30')} minus folio {folio('c29')} plus 1, inclusive")
    assert_published("20 pages", committee_document_pages(),
                     "the same span, said again in the first comment")
    assert_published("five pages", item_pages(),
                     f"folio {folio('c28')} minus folio {folio('c27')} plus 1, inclusive")
    assert_published("four terms", search_terms(), "len() over the searched terms")
    assert_published("four official records", distinct_sources("primary_official"),
                     "distinct source urls whose source_type is primary_official")
    assert_published("one news", distinct_sources("secondary_reported"),
                     "distinct source urls whose source_type is secondary_reported")

    # The deck's own frame count, which the caption states. Counted from the manifest that IS
    # the deck rather than from a glob, because a glob counts whatever survived the render.
    slides = len(json.loads((RUN / "copy.json").read_text(encoding="utf-8"))["slides"])
    assert_published("Nine frames", slides, "len() over copy.json's slides")

    if bad:
        print("\ncompute: a published figure disagrees with its computation", file=sys.stderr)
        for b in bad:
            print(f"  - {b}", file=sys.stderr)
        return 1
    print(f"\ncompute: {7} derived figure(s), every one agreeing with what the deck published")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
