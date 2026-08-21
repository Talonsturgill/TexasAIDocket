#!/usr/bin/env python3
"""link_check.py — the markup a reader never sees, and nobody was reading.

TWO FAULTS THAT SHIPPED, BOTH INVISIBLE TO EVERY OTHER GATE

    A DOUBLED CANONICAL. `page()` prefixes the site to whatever canonical it is handed, and five
    call sites handed it an absolute URL. Every facility page and every company page published
    `https://texasaidocket.com/https://texasaidocket.com/...` as its canonical and its og:url.
    A canonical is markup, not copy, so the house style lint never read it, and it resolves to
    a real page in a browser so nothing broke visibly.

    AN ORPHAN. `registry-changes` shipped with nothing on the site linking to it. It was in the
    sitemap and reachable by URL, which is exactly enough to look fine and to be unread.

WHAT IT CHECKS

Every canonical is the site followed by one path, with no second scheme in it, and it matches the
page's own location on disk. Every page that is in the sitemap is reachable by following links
from the home page, or is named in the allowlist below with a reason.

    link_check.py                 # check docs/
    link_check.py --self-test     # hermetic
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
SITE = "https://texasaidocket.com"

CANON = re.compile(r'<link\s+rel="canonical"\s+href="([^"]*)"', re.I)
OGURL = re.compile(r'<meta\s+property="og:url"\s+content="([^"]*)"', re.I)
HREF = re.compile(r'\bhref="([^"#?]+)', re.I)

# Pages that are deliberately not linked from anywhere. Each needs a reason, because an orphan
# with no reason is the fault this gate exists for.
UNLINKED = {
    "404.html": "the not found page, served by the host and never linked",
    "scan/watch/index.html":
        "reached only by the token in a requester's own link. Linking it would publish a page "
        "that is meaningless without one, and the scanner promises nothing about a requester is "
        "stored or published",
}


def canonical_problems(docs: Path) -> list[str]:
    out = []
    for f in sorted(docs.rglob("index.html")):
        html = f.read_text(encoding="utf-8", errors="replace")
        rel = f.parent.relative_to(docs).as_posix()
        want = f"{SITE}/" + ("" if rel == "." else rel + "/")
        for name, pat in (("canonical", CANON), ("og:url", OGURL)):
            m = pat.search(html)
            if not m:
                continue
            got = m.group(1)
            if got.count("://") > 1:
                out.append(f"{rel or 'home'}: {name} carries two schemes, {got}")
            elif got != want:
                out.append(f"{rel or 'home'}: {name} is {got}, expected {want}")
    return out


def reachable(docs: Path) -> set[str]:
    """Every page reachable by following hrefs from the home page."""
    seen, queue = set(), ["index.html"]
    while queue:
        cur = queue.pop()
        if cur in seen:
            continue
        seen.add(cur)
        f = docs / cur
        if not f.exists():
            continue
        base = Path(cur).parent
        for href in HREF.findall(f.read_text(encoding="utf-8", errors="replace")):
            if "://" in href or href.startswith("mailto:"):
                continue
            t = (base / href).as_posix()
            t = re.sub(r"/{2,}", "/", t).lstrip("./")
            if t.endswith("/") or not Path(t).suffix:
                t = t.rstrip("/") + "/index.html"
            t = Path(t).as_posix().lstrip("/")
            try:
                t = Path(t).resolve().relative_to(Path(".").resolve()).as_posix()
            except Exception:
                pass
            if t.endswith(".html"):
                queue.append(t)
    return seen


def orphan_problems(docs: Path) -> list[str]:
    got = reachable(docs)
    out = []
    for f in sorted(docs.rglob("*.html")):
        rel = f.relative_to(docs).as_posix()
        if rel in got or rel in UNLINKED:
            continue
        out.append(f"{rel} is in the site and nothing links to it")
    return out


def self_test() -> int:
    import tempfile
    checks = []

    def ok(n, c, x=""):
        checks.append(bool(c))
        print(f"  {'ok  ' if c else 'FAIL'}  {n}{'' if c else '  ' + str(x)}")

    def site(pages):
        d = Path(tempfile.mkdtemp())
        for rel, html in pages.items():
            p = d / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(html, encoding="utf-8")
        return d

    def pg(canon, body=""):
        return (f'<link rel="canonical" href="{canon}">'
                f'<meta property="og:url" content="{canon}">{body}')

    d = site({"index.html": pg(f"{SITE}/", '<a href="a/">a</a>'),
              "a/index.html": pg(f"{SITE}/a/")})
    ok("a correct canonical passes", canonical_problems(d) == [], canonical_problems(d))
    ok("...and nothing is orphaned", orphan_problems(d) == [], orphan_problems(d))

    # THE DEFECT, replayed exactly.
    d2 = site({"index.html": pg(f"{SITE}/", '<a href="a/">a</a>'),
               "a/index.html": pg(f"{SITE}/{SITE}/a/")})
    ok("a doubled canonical fails", canonical_problems(d2) != [], canonical_problems(d2))
    ok("...and the report says it carries two schemes",
       "two schemes" in " ".join(canonical_problems(d2)))

    d3 = site({"index.html": pg(f"{SITE}/", '<a href="a/">a</a>'),
               "a/index.html": pg(f"{SITE}/b/")})
    ok("a canonical pointing at the wrong page fails", canonical_problems(d3) != [])

    # THE ORPHAN, replayed.
    d4 = site({"index.html": pg(f"{SITE}/"), "lost/index.html": pg(f"{SITE}/lost/")})
    ok("a page nothing links to fails", orphan_problems(d4) != [], orphan_problems(d4))
    ok("...and it is named in the report", "lost" in " ".join(orphan_problems(d4)))

    d5 = site({"index.html": pg(f"{SITE}/"), "404.html": pg(f"{SITE}/404.html")})
    ok("the allowlisted page is not reported", orphan_problems(d5) == [], orphan_problems(d5))

    d6 = site({"index.html": pg(f"{SITE}/", '<a href="a/">a</a>'),
               "a/index.html": pg(f"{SITE}/a/", '<a href="../b/">b</a>'),
               "b/index.html": pg(f"{SITE}/b/")})
    ok("reachability follows a link two hops deep", orphan_problems(d6) == [], orphan_problems(d6))

    passed = sum(checks)
    print(f"\nlink_check self-test: {passed}/{len(checks)} passed")
    return 0 if passed == len(checks) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--docs", default=str(DOCS))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    docs = Path(a.docs)
    if not docs.exists():
        print("link_check: no docs/ built yet, nothing to check")
        return 0
    found = canonical_problems(docs) + orphan_problems(docs)
    if not found:
        n = sum(1 for _ in docs.rglob("*.html"))
        print(f"links: every canonical resolves and every one of {n} page(s) is reachable")
        return 0
    print(f"link_check: {len(found)} problem(s)\n", file=sys.stderr)
    for p in found:
        print(f"  - {p}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
