#!/usr/bin/env python3
"""livecheck.py — the published site answers, checked against the published site.

WHY THIS EXISTS

Every gate in this repository proves the BUILD is correct. `site_fresh_check` proves `docs/`
is what the ledgers produce, `house_style_check` reads the built pages, `seo_check` reads the
built sitemap. Not one of them opens the live URL.

So the whole suite is green in the one case that matters most: the site is dark. A lapsed
domain, a clobbered `CNAME`, an expired registration, a Pages project unpublished, a DNS
record edited by hand. None of those touch a byte in this repository and every check would go
on passing while nobody could read the record at all.

**THIS SHAPE HAS ALREADY HAPPENED HERE.** `GATE_LESSONS` entry 10: a merge left the live site
on the previous build with every gate green, because a `GITHUB_TOKEN` push does not start a
workflow and no run had begun. The fix was a two-hourly deploy backstop, which re-deploys
blindly and never looks at the result. This looks at the result.

WHAT IT ASSERTS, AND THE SPLIT BETWEEN LOUD AND QUIET

  EXIT 1, THE SITE IS DARK. It did not answer, it answered with an error, it answered with
  something that is not our front page, or the sitemap it serves does not parse. Every one of
  these means a reader cannot use the record right now, and every one needs a person.

  EXIT 2, THE SITE IS BEHIND. It answers and holds together, but the record it serves is older
  than the record in this repository. That is a deploy that has not landed yet, which is
  normal for a few minutes after a merge and a problem after a day. It is worth attention and
  it is not worth waking anybody, so it never returns 1.

The split is the same one `gridwatch_pagecheck` makes and for the same reason. A check that
cries wolf about a deploy still in flight is a check somebody turns off.

    livecheck.py                 # check the live site
    livecheck.py --url https://...
    livecheck.py --self-test     # hermetic, no network
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "ledger" / "docket.json"

# Read from the committed CNAME rather than typed here. CLAUDE.md's public URL rule exists
# because four separate surfaces kept their own copy of this string and three went stale.
CNAME = REPO_ROOT / "docs" / "CNAME"

TITLE = re.compile(r"<title>(.*?)</title>", re.S)
UA = "texasaidocket.com liveness check"


def site_url() -> str:
    host = CNAME.read_text(encoding="utf-8").strip() if CNAME.exists() else ""
    if not host:
        raise SystemExit("livecheck: docs/CNAME is missing or empty, so there is no site to check")
    return f"https://{host}"


def get(url: str, timeout: int = 30) -> tuple[int, bytes]:
    """The status and the body, with an error response treated as an answer rather than a raise.

    A 404 from Pages and a refused connection are different faults and a reader meets them
    differently, so the caller gets to tell them apart.
    """
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read() if hasattr(e, "read") else b""


def findings(fetch, expect_title: str, ledger_items: int) -> tuple[list[str], list[str]]:
    """`(dark, behind)`. `fetch` takes a path and returns `(status, bytes)`.

    THE SEAM IS THE FETCHER, so the self-test can hand over a site that is broken in one exact
    way without a network or a fixture server. A checker that can only be tested against the
    real thing is a checker whose failure paths are never tested at all.
    """
    dark: list[str] = []
    behind: list[str] = []

    status, body = fetch("/")
    if status != 200:
        dark.append(f"the front page answered {status}")
        return dark, behind                      # nothing below is meaningful if this failed
    html = body.decode("utf-8", "replace")
    got = (TITLE.findall(html) or [""])[0]
    if expect_title.lower() not in got.lower():
        # Not a byte comparison. The title carries a tagline that may be edited, and this is
        # asking whether the page served is OURS, which the site name answers.
        dark.append(f"the front page is not ours, its title reads {got[:60]!r}")

    status, body = fetch("/sitemap.xml")
    if status != 200:
        dark.append(f"the sitemap answered {status}")
    else:
        try:
            root = ET.fromstring(body)
        except ET.ParseError as exc:
            dark.append(f"the sitemap does not parse ({exc})")
        else:
            n = len(root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url"))
            if not n:
                dark.append("the sitemap carries no urls")

    status, body = fetch("/docket.json")
    if status != 200:
        dark.append(f"the record answered {status}")
    else:
        try:
            served = len(json.loads(body).get("items") or [])
        except (json.JSONDecodeError, AttributeError) as exc:
            dark.append(f"the published record does not parse ({exc})")
        else:
            if served < ledger_items:
                behind.append(f"the site serves {served} decisions and this repository holds "
                              f"{ledger_items}, so a deploy has not landed")
    return dark, behind


def report(url: str) -> int:
    items = len(json.loads(LEDGER.read_text(encoding="utf-8"))["items"])
    try:
        dark, behind = findings(lambda p: get(url + p),
                                expect_title="Texas AI Docket", ledger_items=items)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"  live: {url} could not be reached ({exc})", file=sys.stderr)
        print("livecheck: THE SITE IS DARK")
        return 1
    for line in dark:
        print(f"  live: {line}", file=sys.stderr)
    for line in behind:
        print(f"  live: {line}")
    if dark:
        print(f"livecheck: THE SITE IS DARK, {len(dark)} problem(s) at {url}")
        return 1
    if behind:
        print(f"livecheck: the site is up and behind, {len(behind)} note(s)")
        return 2
    print(f"livecheck: {url} is up, serves our front page, its sitemap and {items} decisions")
    return 0


def self_test() -> int:
    failures = 0

    def check(label, cond, got=""):
        nonlocal failures
        print(("  ok   " if cond else "  FAIL ") + label + ("" if cond else f"  ({got})"))
        if not cond:
            failures += 1

    good_html = b"<html><head><title>Texas AI Docket \xc2\xb7 Every AI decision</title></head></html>"
    good_map = (b'<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                b"<url><loc>https://x/</loc></url></urlset>")
    good_rec = b'{"items":[{"id":"a"},{"id":"b"}]}'

    def site(**broken):
        pages = {"/": (200, good_html), "/sitemap.xml": (200, good_map),
                 "/docket.json": (200, good_rec)}
        pages.update(broken)
        return lambda p: pages.get(p, (404, b""))

    print("a healthy site is called healthy")
    dark, behind = findings(site(), "Texas AI Docket", 2)
    check("nothing dark", dark == [], str(dark))
    check("nothing behind", behind == [], str(behind))

    print("\nand every way the site can be dark is caught")
    d, _ = findings(site(**{"/": (404, b"")}), "Texas AI Docket", 2)
    check("the front page 404s", any("answered 404" in x for x in d), str(d))
    d, _ = findings(site(**{"/": (200, b"<html><head><title>GitHub Pages</title></head></html>")}),
                    "Texas AI Docket", 2)
    check("the domain serves somebody else's page",
          any("is not ours" in x for x in d), str(d))
    d, _ = findings(site(**{"/sitemap.xml": (200, b"<urlset><broken")}), "Texas AI Docket", 2)
    check("the sitemap does not parse", any("does not parse" in x for x in d), str(d))
    d, _ = findings(site(**{"/sitemap.xml": (200, b'<urlset xmlns="http://www.sitemaps.org/'
                                                  b'schemas/sitemap/0.9"></urlset>')}),
                    "Texas AI Docket", 2)
    check("the sitemap is empty", any("no urls" in x for x in d), str(d))
    d, _ = findings(site(**{"/docket.json": (500, b"")}), "Texas AI Docket", 2)
    check("the record 500s", any("record answered 500" in x for x in d), str(d))
    d, _ = findings(site(**{"/docket.json": (200, b"not json")}), "Texas AI Docket", 2)
    check("the record does not parse", any("record does not parse" in x for x in d), str(d))

    print("\na front page that fails stops the run, since nothing after it is meaningful")
    d, _ = findings(site(**{"/": (503, b""), "/sitemap.xml": (500, b"")}), "Texas AI Docket", 2)
    check("one finding, not a cascade", len(d) == 1, str(d))

    print("\nbehind is not dark, which is the whole point of the split")
    d, b = findings(site(), "Texas AI Docket", 61)
    check("a stale deploy is not dark", d == [], str(d))
    check("...it is reported as behind", any("has not landed" in x for x in b), str(b))
    check("and a site AHEAD of the repo is neither, since a merge may have just landed",
          findings(site(), "Texas AI Docket", 1) == ([], []))

    print("\nthe url comes from the committed CNAME, never from a typed string")
    check("CNAME is the source", site_url() == "https://" + CNAME.read_text().strip(), site_url())

    print("\nlivecheck self-test: " + ("all passed" if not failures else f"{failures} FAILED"))
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default=None)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    return report(a.url or site_url())


if __name__ == "__main__":
    raise SystemExit(main())
