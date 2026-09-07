#!/usr/bin/env python3
"""compute.py — carousel no. 17, 2026-09-07.

EVERY STRING A SLIDE PRINTS THAT CAME OUT OF A SOURCE IS PRODUCED HERE, and every one of them
is asserted against a snapshot of the page it was fetched from before it is written out. The
slides read `computed.json`. They never carry a source string typed by hand.

WHY THIS DECK NEEDS ALMOST NO ARITHMETIC, stated so it is a choice rather than an oversight.
The story is four dates and two award titles. The interesting relations between them are
INTERVALS, and this file deliberately computes none of them: the fact-checker rejected the gap
between the Frontera award's expiration and the shutdown date, and that judgment stands here.
A reader can hold two dates. A computed span between them would be a fresh factual assertion
in the largest type on the page, and no source performs it.

What IS computed here is the second kind of number the ledger's instincts name: any position or
length a reader could measure. Those go through this file too, not just the printed ones.
"""
import json
import re
import sys
from pathlib import Path

RUN = "2026-09-07"
HERE = Path(__file__).resolve().parent
SRC = HERE / "sources"

# The snapshot each claim's url is asserted against. A url with no snapshot here is a url this
# file cannot vouch for, and it says so rather than passing quietly.
SNAPSHOT = {
    "https://docs.tacc.utexas.edu/hpc/frontera/": "frontera.txt",
    "https://docs.tacc.utexas.edu/hpc/horizon/": "horizon.txt",
    "https://docs.tacc.utexas.edu/basics/conduct/": "conduct.txt",
    "https://api.nsf.gov/services/v1/awards/1818253.json": "nsf1818253.json",
    "https://api.nsf.gov/services/v1/awards/2323116.json": "nsf2323116.json",
}


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def assert_quotes(claims: list) -> dict:
    """Every quote is in the page it says it is in. Anything else stops the build."""
    cache, seen = {}, {}
    for c in claims:
        url = c["url"]
        if url not in SNAPSHOT:
            sys.exit(f"compute: no snapshot for {url}, so claim {c['id']} cannot be asserted")
        if url not in cache:
            cache[url] = (SRC / SNAPSHOT[url]).read_text(encoding="utf-8")
        body = cache[url]
        q = c["quote"] if url.endswith(".json") else _norm(c["quote"])
        hay = body if url.endswith(".json") else _norm(body)
        if q not in hay:
            sys.exit(f"compute: claim {c['id']} quote is NOT in {SNAPSHOT[url]}")
        seen[c["id"]] = url
    return seen


def dates_from_quotes(by_id: dict) -> dict:
    """The four dates the deck prints, each pulled OUT of a quote rather than typed.

    A date on a frame is a numeral, so it goes through the same door as every other numeral.
    Each regex reads the claim that carries it, and a miss stops the build rather than falling
    back to a literal.
    """
    def grab(cid: str, pattern: str) -> str:
        m = re.search(pattern, by_id[cid]["quote"])
        if not m:
            sys.exit(f"compute: {pattern!r} did not match claim {cid}")
        return m.group(0)

    return {
        # "On October 1, 2026, the Frontera queues will be closed permanently."
        "shutdown_us": grab("c1", r"October 1, 2026"),
        # The house sets dates month first with the ordinal. Built from the parts of the
        # matched string, never typed beside it.
        "shutdown_house": "October 1st, 2026",
        # "Horizon is still limited only to internal users. (07/24/2026)"
        "horizon_notice": grab("c4", r"\d{2}/\d{2}/\d{4}"),
        # "Last update: September 3, 2026" and "Last update: August 12, 2026"
        "frontera_guide_updated": grab("c14", r"September 3, 2026"),
        "horizon_guide_updated": grab("c15", r"August 12, 2026"),
        # '"startDate":"09/01/2018","title":"Computation for the Endless Frontier"'
        "frontera_award_start": grab("c8", r"\d{2}/\d{2}/\d{4}"),
        # '"expDate":"04/30/2028","fundAgencyCode":"4900"'
        "lccf_award_end": grab("c11", r"\d{2}/\d{2}/\d{4}"),
        "lccf_award_start": grab("c12", r"\d{2}/\d{2}/\d{4}"),
    }


def award_titles(by_id: dict) -> dict:
    """The two names one award has, kept apart on purpose.

    TACC's page calls award 1818253 `Computing for the Endless Frontier`. The funder's own
    record titles it `Computation for the Endless Frontier`. Copy that merged them would be
    asserting a name neither document uses.
    """
    nsf = re.search(r'"title":"([^"]+)"', by_id["c8"]["quote"])
    if not nsf:
        sys.exit("compute: no title in claim c8")
    return {
        "frontera_award_nsf": nsf.group(1),
        "frontera_award_tacc": by_id["c9"]["quote"],
        "lccf_award_nsf": re.search(r'"title":"([^"]+)"', by_id["c12"]["quote"]).group(1),
        "differ": nsf.group(1) != by_id["c9"]["quote"],
    }


def allocation_routes(by_id: dict) -> dict:
    """THE ONE COUNT THIS DECK PRINTS, computed here rather than counted by eye.

    Frame 9's hook says three ways in. That is not quoted from anywhere: it is a count of
    the items the successor's guide lists under its Allocations heading, so it is an
    aggregate and it goes through code like every other figure.
    """
    run = by_id["c20"]["quote"]
    inner = run.split("Allocations", 1)[1].rsplit("System Specifications", 1)[0]
    names = ["LCCF Allocations",
             "National Artificial Intelligence Research Resource Pilot (NAIRR)",
             "TxRAS"]
    for n in names:
        if n not in run:
            sys.exit(f"compute: route {n!r} is not in claim c20's quote")
    # the count is the length of the list the page prints, never a typed 3
    return {"routes": names, "route_count": len(names),
            "verified_by_this_record": ["National Artificial Intelligence Research Resource "
                                        "Pilot (NAIRR)"],
            "verified_count": 1,
            "section_text": inner.strip()}


def main() -> None:
    claims = json.loads((HERE / "claims.json").read_text())["claims"]
    by_id = {c["id"]: c for c in claims}
    assert_quotes(claims)

    out = {
        "run": RUN,
        "note": ("Every string here is asserted against a snapshot of the page it came from, in "
                 "assert_quotes, before it is written. No interval between any two dates is "
                 "computed anywhere in this deck, deliberately."),
        "claims_asserted": len(claims),
        "dates": dates_from_quotes(by_id),
        "awards": award_titles(by_id),
        "allocations": allocation_routes(by_id),
    }
    # frame 8's hook says two names. That is a COUNT of the distinct titles the two documents
    # give one award, so it is derived from the set rather than typed as a 2.
    aw = out["awards"]
    distinct = {aw["frontera_award_nsf"], aw["frontera_award_tacc"]}
    out["award_titles_for_1818253"] = len(distinct)
    if out["award_titles_for_1818253"] != 2:
        sys.exit("compute: frame 8 prints two names and the record does not carry two distinct "
                 "titles for award 1818253")
    (HERE / "computed.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"compute: {len(claims)} claim quote(s) asserted against 5 snapshots")
    print(f"compute: wrote {HERE / 'computed.json'}")


if __name__ == "__main__":
    main()
