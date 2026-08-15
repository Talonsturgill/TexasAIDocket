#!/usr/bin/env python3
"""indexnow.py — tell the engines a page changed, instead of waiting to be crawled.

WHY

A crawler reaches a small site on its own schedule, which for a new domain is measured in days
to weeks. This record's most perishable content is a comment window with a close date on it, so
a decision that lands on Monday and closes on Friday is worth nothing if it is indexed the
following month.

IndexNow inverts that. One POST names the changed URLs and they are queued for fetch in minutes.

WHO ACTUALLY HONOURS IT, said accurately rather than optimistically. Bing, Yandex, Seznam and
Naver share one IndexNow pool, and Bing's index is what several answer engines are built on.
**Google does not participate** and has said so. So this does not touch the engine the owner
named, and pretending otherwise would be exactly the unverifiable claim this project refuses.
What reaches Google faster is the sitemap, the feeds and the internal linking, which are the
other waves of this work.

THE KEY IS A COMMITTED CONSTANT, NOT A GENERATED ONE. IndexNow verifies ownership by fetching
`https://<host>/<key>.txt` and matching its contents to the key in the request. A key generated
at build time would change on every build, so the file served and the key submitted would drift
apart within one deploy, and every submission would fail verification. It is public by design:
it proves control of the host, it is not a secret, and it grants nothing but the right to say
"this page changed".

FAILS SOFT, DELIBERATELY. A refused submission must never fail a deploy. The site being live is
the product and a crawl hint is a courtesy on top of it, so every network path here reports and
returns zero unless `--strict` is passed.

    indexnow.py --dry-run            # print what would be sent
    indexnow.py --since 2026-08-01   # only urls whose lastmod is on or after
    indexnow.py                      # submit every url in the sitemap
    indexnow.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS = REPO_ROOT / "docs"
ENDPOINT = "https://api.indexnow.org/IndexNow"

# Generated once, committed, and never rotated without also changing the file the build writes.
# Hex only and 32 characters, which is what the protocol accepts.
KEY = "b7d41f6a2c8e45739af0d51e6c3b8a92"
KEY_FILE = f"{KEY}.txt"

# The protocol's own ceiling on one request.
MAX_URLS = 10_000


def key_file_contents() -> str:
    """What is served at /<key>.txt. The key and nothing else, which is the whole spec."""
    return KEY + "\n"


def sitemap_urls(sitemap: Path | None = None, since: str | None = None) -> list:
    """Every url in the built sitemap, optionally only those changed on or after `since`."""
    sm = sitemap or (DOCS / "sitemap.xml")
    xml = sm.read_text(encoding="utf-8")
    out = []
    for block in re.findall(r"<url>(.*?)</url>", xml, re.S):
        loc = re.search(r"<loc>(.*?)</loc>", block)
        if not loc:
            continue
        if since:
            mod = re.search(r"<lastmod>(\d{4}-\d{2}-\d{2})", block)
            if not mod or mod.group(1) < since:
                continue
        out.append(loc.group(1))
    return out


def payload(host: str, urls: list) -> dict:
    return {
        "host": host,
        "key": KEY,
        "keyLocation": f"https://{host}/{KEY_FILE}",
        "urlList": urls[:MAX_URLS],
    }


def submit(host: str, urls: list, *, dry: bool = False, strict: bool = False) -> int:
    if not urls:
        print("indexnow: nothing to submit")
        return 0
    body = payload(host, urls)
    if dry:
        print(f"indexnow: would submit {len(body['urlList'])} url(s) for {host}")
        for u in body["urlList"][:10]:
            print(f"  {u}")
        if len(body["urlList"]) > 10:
            print(f"  ... and {len(body['urlList']) - 10} more")
        return 0
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8",
                 "User-Agent": f"{host} IndexNow submitter"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"indexnow: {r.status} for {len(body['urlList'])} url(s)")
            return 0
    except (urllib.error.URLError, OSError) as exc:
        # FAILS SOFT. The site is live either way and a crawl hint is not worth a red deploy.
        print(f"indexnow: submission did not go through ({exc}). The site is published and "
              f"this is a courtesy on top of it.", file=sys.stderr)
        return 1 if strict else 0


def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    ok("the key is 32 hex characters, which is what the protocol accepts",
       len(KEY) == 32 and re.fullmatch(r"[0-9a-f]{32}", KEY) is not None, KEY)
    ok("the served file is the key and nothing else",
       key_file_contents().strip() == KEY)
    ok("the key file is named for the key",
       KEY_FILE == f"{KEY}.txt")

    b = payload("example.com", ["https://example.com/a/", "https://example.com/b/"])
    ok("the payload names the host", b["host"] == "example.com")
    ok("...and where the key can be verified",
       b["keyLocation"] == f"https://example.com/{KEY_FILE}")
    ok("...and carries the urls", len(b["urlList"]) == 2)
    ok("a submission is capped at the protocol's ceiling",
       len(payload("h", [f"u{i}" for i in range(MAX_URLS + 50)])["urlList"]) == MAX_URLS)

    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as fh:
        fh.write('<urlset><url><loc>https://x/a/</loc><lastmod>2026-08-10</lastmod></url>'
                 '<url><loc>https://x/b/</loc><lastmod>2026-08-01</lastmod></url>'
                 '<url><loc>https://x/c/</loc></url></urlset>')
    sm = Path(fh.name)
    try:
        ok("every url is read out of the sitemap", len(sitemap_urls(sm)) == 3)
        ok("...and `since` keeps only what changed on or after it",
           sitemap_urls(sm, since="2026-08-05") == ["https://x/a/"],
           str(sitemap_urls(sm, since="2026-08-05")))
        ok("...treating an entry with no lastmod as not known to have changed",
           "https://x/c/" not in sitemap_urls(sm, since="2026-08-05"))
    finally:
        sm.unlink()

    ok("nothing is submitted for an empty list", submit("h", [], dry=True) == 0)
    ok("a dry run sends no request", submit("h", ["u"], dry=True) == 0)

    real = DOCS / "sitemap.xml"
    if real.exists():
        ok("the real sitemap parses to something", len(sitemap_urls(real)) > 50,
           str(len(sitemap_urls(real))))
        ok("...and the key file is served beside it", (DOCS / KEY_FILE).exists(),
           f"{KEY_FILE} is not in docs/, so every submission would fail verification")

    print("\nindexnow self-test: " + ("all passed" if not failures else f"{failures} FAILED"))
    return 0 if not failures else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--since", metavar="YYYY-MM-DD")
    ap.add_argument("--host", default="texasaidocket.com")
    ap.add_argument("--strict", action="store_true",
                    help="fail the run if the submission does not go through")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    try:
        urls = sitemap_urls(since=a.since)
    except OSError as exc:
        print(f"indexnow: cannot read the sitemap ({exc})", file=sys.stderr)
        return 2
    return submit(a.host, urls, dry=a.dry_run, strict=a.strict)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                            # noqa: BLE001
        print(f"indexnow: broke: {exc}", file=sys.stderr)
        sys.exit(2)
