#!/usr/bin/env python3
"""lastmod.py — the date a page's content is current to, for the footer and the sitemap.

WHY THIS EXISTS

`sitemap.xml` stamped every url with the build date, so the record told Google that all 222
pages changed this morning. They did not. Google's stated position on this is not subtle: a
`lastmod` it finds unreliable is one it stops reading, and a site claiming everything changed
today has said once that the field is worthless. The signal meant to say "this page is worth
recrawling" was being spent on 222 pages that were not.

The page footer said it out loud too. "Revised August 19th, 2026" ran under every page,
including ones whose last real change was a week earlier.

WHERE THE DATE COMES FROM, AND THE VERSION THAT WAS WRONG

**The ledgers, and only the ledgers.** The first version of this file derived the date from git,
on the reasoning that `docs/` is committed so history already records when a page changed. That
is true and it is not usable, and the freshness gate caught it within one CI run.

`site_fresh_check` proves `docs/` is a pure deterministic function of the ledgers by rebuilding
into a temp dir and comparing bytes. A date read out of git makes the build a function of the
repository's SHAPE as well: clone depth, and on a pull request the synthetic merge commit that
`actions/checkout` puts at HEAD, which exists in no branch. The bytes built on a laptop with
full history and the bytes built on a runner disagreed about 218 pages, and neither was
corrupt. The law that makes it impossible for a run to break the live site is worth more than
a precise date, so the date gives way.

So every date below is a field this record already holds:

  item/<id>/       the item's own `last_verified`
  articles/<date>/ the date the article shipped
  the hubs         the newest `last_verified` in the record, because a hub renders counts and
                   an ordering that every item participates in, so any item moving moves it

WHAT CARRIES NO DATE AT ALL, WHICH IS THE HONEST HALF

`/services/`, `/scan/`, `/datacenters/` and `404` are prose about the project. No
ledger field says when their words last changed, and the build date is not that. They get no
`<lastmod>` and no footer stamp. `<lastmod>` is optional and a crawler treats an absent one as
"no claim", which is exactly right, where a wrong one is a claim that costs the whole field its
credibility. This is the compute-not-generate law in its usual form: where we cannot compute
something, we say nothing rather than publish an estimate dressed as a measurement.

`/about/` returned on 2026-08-30 as the stable explanation of the publication. Like the other
prose pages, no ledger field dates its words, so it carries no stamp.

    lastmod.py --self-test
"""
from __future__ import annotations

import datetime as _dt
import sys

# The token `page()` renders where the date goes, substituted once the date is known. A page is
# built before the build knows which of them have dates, and threading a date through twenty
# call sites to reach one line of footer is worse than one substitution at the end.
TOKEN = "%%REVISED%%"

# Hubs are views OF the record. They print counts, an ordering by deadline and a set of
# children, so any item changing changes them, and the newest verification in the record is
# their date. Matched by prefix against a path relative to `docs/`.
HUB_PREFIXES = ("index.html", "record/", "topic/", "place/", "sources/", "questions/",
                "articles/index.html")

# Prose about the project. No ledger field dates these, so they make no claim.
UNDATED_PREFIXES = ("about/", "services/", "scan/", "videos/", "404.html",
                    "grid/", "water/", "facility/", "company/", "registry-changes/",
                    "datacenters/")


def _newest(items: list) -> str | None:
    """The most recent verification in the record."""
    seen = [str(it.get("last_verified")) for it in items if it.get("last_verified")]
    return max(seen) if seen else None


def dates_for(paths, *, items: list, runs: list) -> dict[str, str]:
    """Path relative to `docs/` -> ISO date, for every page that has an honest one.

    A path absent from the result carries no date, which is a decision and not a gap.
    """
    by_id = {it["id"]: it for it in items}
    newest = _newest(items)
    run_dates = sorted((r["date"] for r in runs), reverse=True)
    out: dict[str, str] = {}

    for path in paths:
        if path.startswith(UNDATED_PREFIXES):
            continue
        if path.startswith("item/"):
            it = by_id.get(path.split("/")[1])
            if it and it.get("last_verified"):
                out[path] = str(it["last_verified"])
        elif path.startswith("articles/") and path != "articles/index.html":
            out[path] = path.split("/")[1]
        elif path == "articles/index.html":
            if run_dates:
                out[path] = run_dates[0]
        elif path.startswith(HUB_PREFIXES):
            if newest:
                out[path] = newest
    return out


def apply(text: str, iso: str | None, ordinal) -> str:
    """Put the real date where the token is, or take the whole stamp out."""
    if not iso:
        # The span is removed rather than left empty, so a page with no date has no orphaned
        # separator sitting in its colophon.
        return text.replace(f"<span>{TOKEN}</span>", "").replace(TOKEN, "")
    d = _dt.date.fromisoformat(iso)
    return text.replace(TOKEN, f"Revised {ordinal(d)}, {iso[:4]}")


def self_test() -> int:
    failures = 0

    def check(label, cond, got=""):
        nonlocal failures
        print(("  ok   " if cond else "  FAIL ") + label + ("" if cond else f"  ({got})"))
        if not cond:
            failures += 1

    items = [{"id": "tx-2026-0001", "last_verified": "2026-08-12"},
             {"id": "tx-2026-0002", "last_verified": "2026-08-18"}]
    runs = [{"date": "2026-08-19"}, {"date": "2026-08-16"}]
    paths = ["index.html", "record/index.html", "datacenters/index.html", "about/index.html",
             "services/index.html",
             "item/tx-2026-0001/index.html", "item/tx-2026-0002/index.html",
             "articles/index.html", "articles/2026-08-16/index.html",
             "topic/data-centers/index.html", "data/index.html", "404.html"]
    got = dates_for(paths, items=items, runs=runs)

    print("the date is the record's, never the build's")
    check("an item carries its own last_verified",
          got["item/tx-2026-0001/index.html"] == "2026-08-12",
          got.get("item/tx-2026-0001/index.html"))
    check("and a different item carries a different one",
          got["item/tx-2026-0002/index.html"] == "2026-08-18",
          got.get("item/tx-2026-0002/index.html"))
    check("an article is dated when it shipped",
          got["articles/2026-08-16/index.html"] == "2026-08-16",
          got.get("articles/2026-08-16/index.html"))
    check("a hub takes the newest verification in the record",
          got["record/index.html"] == "2026-08-18", got.get("record/index.html"))
    check("the front page is a hub too", got["index.html"] == "2026-08-18",
          got.get("index.html"))
    check("the articles index is dated by the newest article",
          got["articles/index.html"] == "2026-08-19", got.get("articles/index.html"))

    print("\nand prose about the project makes no claim at all")
    for p in ("about/index.html", "datacenters/index.html", "services/index.html", "data/index.html",
              "404.html"):
        check(f"{p} carries no date", p not in got, got.get(p, ""))

    print("\nthey are not all the same, which is the whole point")
    check("more than one distinct date", len(set(got.values())) > 1, str(sorted(set(got.values()))))

    print("\nthe stamp renders, or is removed cleanly")
    def ordinal(d):
        return f"{d.strftime('%B')} {d.day}th"
    out = apply("<p>x</p><span>" + TOKEN + "</span>", "2026-08-12", ordinal)
    check("a dated page prints it", out.endswith("<span>Revised August 12th, 2026</span>"), out)
    out = apply("<p>x</p><span>" + TOKEN + "</span>", None, ordinal)
    check("an undated page loses the whole span", out == "<p>x</p>", out)
    check("no token ever survives a build", TOKEN not in out, out)

    print("\nthe answer depends on the ledgers and on nothing else")
    # THE DEFECT THIS REPLACED. The first version read the date out of git, so the same
    # ledgers built different bytes on a laptop with full history than on a runner checking
    # out a synthetic merge commit, and `site_fresh_check` failed on 218 pages. The property
    # that matters is not "does not import subprocess", it is that the same inputs give the
    # same answer no matter where or when it runs.
    again = dates_for(list(reversed(paths)), items=list(reversed(items)),
                      runs=list(reversed(runs)))
    check("same ledgers give the same dates, in any order", again == got,
          str({k: v for k, v in again.items() if got.get(k) != v}))
    # A build an hour later, or on a different machine, sees the same record.
    check("and nothing in the answer is today's date",
          _dt.date.today().isoformat() not in set(got.values())
          or _newest(items) == _dt.date.today().isoformat())

    print("\nlastmod self-test: " + ("all passed" if not failures else f"{failures} FAILED"))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(self_test() if "--self-test" in sys.argv else
                     (print(__doc__.strip()) or 0))
