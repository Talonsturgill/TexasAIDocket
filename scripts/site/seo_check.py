#!/usr/bin/env python3
"""seo_check.py — the record is findable, proved against the built site.

WHY THIS EXISTS

The site was invisible in Google and every check in the repository was green, because
nothing checked the things that decide whether a page is findable. The structured data was
strong, the sitemap was valid, `robots.txt` was permissive, and none of that is what was
wrong. What was wrong was in the details no gate was looking at:

  - all 222 urls stamped the same `lastmod`, the build date, every day. A `lastmod` that is
    always today tells a crawler the field is worthless, and it stops being read.
  - the three article pages, the only reporting on the site, carried no article schema, no
    publication date, `og:type` of website, and the generic site card.
  - one of them shipped a twenty-five character description, which is what a search result
    would have had to sell itself with.

Each check below is one of those. This is a GATE, so it is run by exit code. A report that
prints advice on failure and one clean line on success reads the same either way under
`tail -1`, and that has shipped a red gate in this repository before.

WHAT IT DELIBERATELY DOES NOT FAIL ON

The verification tokens being unset. DNS verification needs no tag on the page, so an empty
token is a legitimate finished state, and a gate that calls a correct product a violation is
a gate somebody switches off. It is reported and it does not fail.

    seo_check.py                 # gate the built site at docs/
    seo_check.py --site /tmp/x   # gate a build somewhere else
    seo_check.py --self-test     # prove each check can go red
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

TITLE = re.compile(r"<title>(.*?)</title>", re.S)
DESC = re.compile(r'<meta name="description" content="(.*?)">', re.S)
CANON = re.compile(r'<link rel="canonical" href="(.*?)">')
OGTYPE = re.compile(r'<meta property="og:type" content="(.*?)">')
OGIMG = re.compile(r'<meta property="og:image" content="(.*?)">')
H1 = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
LOC = re.compile(r"<loc>(.*?)</loc>")
LASTMOD = re.compile(r"<lastmod>(.*?)</lastmod>")
VERIFY = re.compile(r'<meta name="(google-site-verification|msvalidate\.01)" content="(.*?)">')

# A description short enough to be useless and long enough to be truncated. Google renders
# roughly 155 characters and has no minimum, but a description under 50 is not a sentence
# that sells a page, and one over 200 is one nobody will read the end of.
DESC_MIN, DESC_MAX = 50, 200


def findings(site: Path) -> list[str]:
    """Every way the built site at `site` is harder to find than it should be."""
    bad: list[str] = []
    pages = sorted(site.rglob("index.html"))
    if not pages:
        return [f"{site}: no pages, so nothing was checked"]

    # ---------------------------------------------------------------- the sitemap
    sm = site / "sitemap.xml"
    if not sm.exists():
        bad.append("sitemap.xml: missing")
    else:
        xml = sm.read_text(encoding="utf-8")
        locs, mods = LOC.findall(xml), LASTMOD.findall(xml)
        if len(locs) != len(mods):
            bad.append(f"sitemap.xml: {len(locs)} urls but {len(mods)} lastmod values")
        # THE DEFECT THIS FILE EXISTS FOR. Every url carrying the same date is the signature
        # of a build stamping `today` rather than deriving a date, and it is indistinguishable
        # from a correct sitemap by every other check.
        if len(mods) > 8 and len(set(mods)) == 1:
            bad.append(f"sitemap.xml: all {len(mods)} urls share one lastmod ({mods[0]}), "
                       "which is a build date rather than a revision date")
        built = {"" if p.parent == site else str(p.parent.relative_to(site)) + "/"
                 for p in pages}
        listed = {u.split("/", 3)[3] if u.count("/") > 2 else "" for u in locs}
        for missing in sorted(built - listed):
            bad.append(f"sitemap.xml: does not list /{missing}")
        for ghost in sorted(listed - built):
            bad.append(f"sitemap.xml: lists /{ghost}, which was not built")

    # ---------------------------------------------------------------- robots
    rb = site / "robots.txt"
    if not rb.exists():
        bad.append("robots.txt: missing")
    else:
        txt = rb.read_text(encoding="utf-8")
        if "Sitemap:" not in txt:
            bad.append("robots.txt: does not name the sitemap")
        if re.search(r"^Disallow:\s*/\s*$", txt, re.M):
            bad.append("robots.txt: disallows the whole site")

    # ---------------------------------------------------------------- every page
    for p in pages:
        rel = "/" + (str(p.parent.relative_to(site)) + "/" if p.parent != site else "")
        html = p.read_text(encoding="utf-8")
        titles, descs, canons = TITLE.findall(html), DESC.findall(html), CANON.findall(html)
        if len(titles) < 1:
            bad.append(f"{rel}: no title")
        if len(canons) != 1:
            bad.append(f"{rel}: {len(canons)} canonical tags, want exactly 1")
        if len(descs) != 1:
            bad.append(f"{rel}: {len(descs)} meta descriptions, want exactly 1")
        else:
            d = descs[0]
            if not DESC_MIN <= len(d) <= DESC_MAX:
                bad.append(f"{rel}: description is {len(d)} characters, want "
                           f"{DESC_MIN} to {DESC_MAX} ({d[:48]!r})")
        # A page with no h1 gives a crawler no heading to rank the page's subject on. More
        # than one and there is no single subject to rank.
        if len(H1.findall(html)) != 1:
            bad.append(f"{rel}: {len(H1.findall(html))} h1 headings, want exactly 1")
        if OGIMG.findall(html) and not OGIMG.findall(html)[0].startswith("http"):
            bad.append(f"{rel}: og:image is not absolute, so most scrapers drop it")

        # ------------------------------------------------------------ articles
        if rel.startswith("/articles/") and rel != "/articles/":
            if '"@type":"NewsArticle"' not in html.replace(" ", ""):
                bad.append(f"{rel}: an article with no NewsArticle schema")
            if '"@type":"BreadcrumbList"' not in html.replace(" ", ""):
                bad.append(f"{rel}: an article with no breadcrumb trail")
            got = (OGTYPE.findall(html) or [""])[0]
            if got != "article":
                bad.append(f"{rel}: og:type is {got!r}, want 'article'")
            img = (OGIMG.findall(html) or [""])[0]
            if img.endswith("/og.png"):
                bad.append(f"{rel}: shares the site card instead of carrying its own")
            elif img:
                # A card named in the head and absent from the build is a broken share
                # everywhere the link is posted, and nothing on the page looks wrong.
                name = img.split("/", 3)[-1]
                if not (site / name).exists():
                    bad.append(f"{rel}: og:image names {name}, which was not built")

    # ---------------------------------------------------------------- ownership tags
    home = site / "index.html"
    for kind, value in (VERIFY.findall(home.read_text(encoding="utf-8"))
                        if home.exists() else []):
        if not value.strip():
            bad.append(f"/: {kind} is present and empty, which reads as done and is not")
    return bad


def report(site: Path) -> int:
    bad = findings(site)
    home = (site / "index.html")
    seen = dict(VERIFY.findall(home.read_text(encoding="utf-8"))) if home.exists() else {}
    for kind in ("google-site-verification", "msvalidate.01"):
        if kind not in seen:
            # NOT A FAILURE. DNS verification leaves no tag on the page, so this is a note
            # about which method is in use and never a reason to stop a build.
            print(f"  note: no {kind} tag, so verification is by DNS or not yet done")
    for line in bad:
        print(f"  seo: {line}", file=sys.stderr)
    print(f"seo_check: {'clean' if not bad else str(len(bad)) + ' problem(s)'} "
          f"across {len(list(site.rglob('index.html')))} page(s)")
    return 1 if bad else 0


def self_test() -> int:
    """Every check goes red against the defect it exists for.

    A self-test proves the checker CAN fail. Only the checker proves the product is clean,
    so this is the smaller half and `guards.yml` runs both.
    """
    import tempfile
    failures = 0

    def check(label, cond, got=""):
        nonlocal failures
        print(("  ok   " if cond else "  FAIL ") + label + ("" if cond else f"  ({got})"))
        if not cond:
            failures += 1

    def pg(desc="d" * 90, h1="<h1>H</h1>", head=""):
        return ('<html><head><title>T</title>'
                f'<meta name="description" content="{desc}">'
                f'<link rel="canonical" href="https://x/">{head}</head>'
                f"<body>{h1}</body></html>")

    def run(pages=None, mods=None, robots="User-agent: *\nAllow: /\nSitemap: https://x/s.xml\n",
            listed=None):
        pages = pages if pages is not None else {"": pg(), "a/": pg()}
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            for rel, html in pages.items():
                (tmp / rel).mkdir(parents=True, exist_ok=True)
                (tmp / rel / "index.html").write_text(html)
            keys = list(pages) if listed is None else listed
            mods = mods or ["2026-08-1" + str(8 + i % 2) for i in range(len(keys))]
            locs = "".join(f"<url><loc>https://x/{r}</loc><lastmod>{m}</lastmod></url>"
                           for r, m in zip(keys, mods))
            (tmp / "sitemap.xml").write_text(f"<urlset>{locs}</urlset>")
            (tmp / "robots.txt").write_text(robots)
            return findings(tmp)

    print("a clean build is called clean")
    check("no findings on a good site", run() == [], str(run()))

    print("\nand each defect that actually shipped is caught")
    ten = {f"p{i}/": pg() for i in range(10)} | {"": pg()}
    check("every url sharing one lastmod",
          any("share one lastmod" in f for f in run(ten, mods=["2026-08-19"] * 11)),
          str(run(ten, mods=["2026-08-19"] * 11)[:2]))
    check("a sitemap that misses a built page",
          any("does not list" in f for f in run(listed=[""])), str(run(listed=[""])))
    got = run({"": pg(), "a/": pg(desc="August 7th came and went.")})
    check("a description too short to sell the page",
          any("description is 25 characters" in f for f in got), str(got))

    art_head = ('<meta property="og:type" content="website">'
                '<meta property="og:image" content="https://x/og.png">')
    got = run({"": pg(), "articles/2026-08-19/": pg(head=art_head)})
    check("an article with no NewsArticle schema",
          any("no NewsArticle schema" in f for f in got), str(got))
    check("an article whose og:type still says website",
          any("want 'article'" in f for f in got), str(got))
    check("an article sharing the site card",
          any("shares the site card" in f for f in got), str(got))
    check("an article with no breadcrumb trail",
          any("no breadcrumb trail" in f for f in got), str(got))
    got = run({"": pg(), "articles/2026-08-19/": pg(
        head='<meta property="og:type" content="article">'
             '<meta property="og:image" content="https://x/og/gone.png">'
             '<script>{"@type":"NewsArticle"}{"@type":"BreadcrumbList"}</script>')})
    check("an article naming a card the build never wrote",
          any("which was not built" in f for f in got), str(got))

    check("a page with two h1 headings",
          any("2 h1 headings" in f for f in run({"": pg(), "a/": pg(h1="<h1>A</h1><h1>B</h1>")})))
    check("a page with no h1 at all",
          any("0 h1 headings" in f for f in run({"": pg(), "a/": pg(h1="<p>x</p>")})))
    check("a robots.txt that blocks the site",
          any("disallows the whole site" in f for f in
              run(robots="User-agent: *\nDisallow: /\nSitemap: https://x/s.xml\n")))
    check("a robots.txt that never names the sitemap",
          any("does not name the sitemap" in f for f in run(robots="User-agent: *\nAllow: /\n")))
    check("an empty verification tag",
          any("reads as done and is not" in f for f in run(
              {"": pg(head='<meta name="google-site-verification" content="">')})))
    check("an og:image that is not absolute",
          any("not absolute" in f for f in run(
              {"": pg(head='<meta property="og:image" content="og.png">')})))

    print("\nseo_check self-test: " + ("all passed" if not failures else f"{failures} FAILED"))
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", default=str(REPO_ROOT / "docs"))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    return self_test() if a.self_test else report(Path(a.site))


if __name__ == "__main__":
    raise SystemExit(main())
