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
import html as _html
import json
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
BRAND = "Texas AI Docket"


def plain(value: str) -> str:
    """Visible text from one small HTML fragment."""
    return " ".join(_html.unescape(re.sub(r"<[^>]+>", " ", value)).split())


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
        # A url may carry no `lastmod`, and that is a decision rather than a gap. The pages of
        # prose about the project have no ledger field saying when their words changed, and an
        # absent element reads as "no claim" where a wrong one costs the field its credibility
        # everywhere. What is NOT allowed is more dates than urls, which would mean the two
        # lists cannot be paired at all.
        if len(mods) > len(locs):
            bad.append(f"sitemap.xml: {len(mods)} lastmod values for {len(locs)} urls")
        if not mods:
            bad.append("sitemap.xml: no url carries a lastmod at all")
        # THE DEFECT THIS FILE EXISTS FOR. Every url carrying the same date is the signature
        # of a build stamping `today` rather than deriving a date, and it is indistinguishable
        # from a correct sitemap by every other check.
        if len(mods) > 8 and len(set(mods)) == 1:
            bad.append(f"sitemap.xml: all {len(mods)} urls share one lastmod ({mods[0]}), "
                       "which is a build date rather than a revision date")
        # Sitemap paths are URL paths, never host filesystem paths. Keeping them POSIX-shaped
        # also makes planted article fixtures exercise the intended checks on Windows.
        built = {"" if p.parent == site else p.parent.relative_to(site).as_posix() + "/"
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
        for name in ("sitemap.xml", "sitemap-news.xml", "sitemap-video.xml"):
            if not re.search(rf"^Sitemap:\s+https?://[^\s]+/{re.escape(name)}\s*$", txt, re.M):
                bad.append(f"robots.txt: does not name {name}")
        if re.search(r"^Disallow:\s*/\s*$", txt, re.M):
            bad.append("robots.txt: disallows the whole site")

    # News and video carry fields the ordinary urlset cannot. They keep stable addresses even
    # when no recent article or complete film exists, so a submitted sitemap never disappears.
    for name, namespace in (("sitemap-news.xml", "sitemap-news/0.9"),
                            ("sitemap-video.xml", "sitemap-video/1.1")):
        path = site / name
        if not path.exists():
            bad.append(f"{name}: missing")
        elif namespace not in path.read_text(encoding="utf-8"):
            bad.append(f"{name}: does not declare the {namespace} namespace")

    # ---------------------------------------------------------------- every page
    title_pages: dict[str, list[str]] = {}
    for p in pages:
        rel = "/" + (p.parent.relative_to(site).as_posix() + "/"
                     if p.parent != site else "")
        html = p.read_text(encoding="utf-8")
        titles, descs, canons = TITLE.findall(html), DESC.findall(html), CANON.findall(html)
        if len(titles) < 1:
            bad.append(f"{rel}: no title")
        else:
            title_pages.setdefault(plain(titles[0]), []).append(rel)
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

    # Two pages with the same title ask a search engine to choose which one owns the query.
    # The facility and company pages did this for every name that appeared in both families.
    for title, rels in sorted(title_pages.items()):
        if title and len(rels) > 1:
            bad.append(f"title {title!r} is shared by {', '.join(rels)}")

    # ---------------------------------------------------------------- brand entity
    home = site / "index.html"
    home_html = home.read_text(encoding="utf-8") if home.exists() else ""
    home_h1 = plain((H1.findall(home_html) or [""])[0])
    if BRAND.casefold() not in home_h1.casefold():
        bad.append(f"/: the primary heading does not name {BRAND}")
    if '"logo":' not in home_html:
        bad.append("/: the Organization graph carries no logo")
    if not (site / "about" / "index.html").exists():
        bad.append("/about/: missing, leaving the publication with no stable entity page")

    # The Dispatch manifest is external input, but once it exists the delivered page must carry
    # the same titles without requiring a fetch and must describe each complete film as video.
    manifest_path = site / "videos" / "videos.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            bad.append("/videos/videos.json: does not parse")
            manifest = {}
        films = [v for v in (manifest.get("videos") or []) if isinstance(v, dict)
                 and all(v.get(k) for k in ("id", "title", "video", "poster", "date"))]
        if films:
            video_html = ((site / "videos" / "index.html").read_text(encoding="utf-8")
                          if (site / "videos" / "index.html").exists() else "")
            visible = plain(video_html)
            for film in films:
                if str(film["title"]) not in visible:
                    bad.append(f"/videos/: {film['title']!r} is absent from delivered HTML")
            if video_html.count('"@type":"VideoObject"') < len(films):
                bad.append(f"/videos/: {len(films)} complete film(s) but fewer VideoObject nodes")
            video_xml = ((site / "sitemap-video.xml").read_text(encoding="utf-8")
                         if (site / "sitemap-video.xml").exists() else "")
            if video_xml.count("<video:video>") < len(films):
                bad.append(f"sitemap-video.xml: {len(films)} complete film(s) but fewer entries")

    # ---------------------------------------------------------------- ownership tags
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

    def pg(desc="d" * 90, h1="<h1>H</h1>", head="", title="T"):
        return (f'<html><head><title>{title}</title>'
                f'<meta name="description" content="{desc}">'
                f'<link rel="canonical" href="https://x/">{head}</head>'
                f"<body>{h1}</body></html>")

    logo = '<script type="application/ld+json">{"@type":"Organization","logo":"x"}</script>'
    good_home = pg(h1=f"<h1>{BRAND}</h1>", head=logo, title=BRAND)
    good_robots = ("User-agent: *\nAllow: /\n"
                   "Sitemap: https://x/sitemap.xml\n"
                   "Sitemap: https://x/sitemap-news.xml\n"
                   "Sitemap: https://x/sitemap-video.xml\n")

    def run(pages=None, mods=None, robots=None, listed=None, *, add_about=True,
            specialists=True, feed=None):
        pages = dict(pages) if pages is not None else {
            "": good_home, "a/": pg(title="A")}
        if add_about:
            pages.setdefault("about/", pg(title="About"))
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            for rel, html in pages.items():
                (tmp / rel).mkdir(parents=True, exist_ok=True)
                (tmp / rel / "index.html").write_text(html)
            keys = list(pages) if listed is None else listed
            mods = mods or ["2026-08-1" + str(8 + i % 2) for i in range(len(keys))]
            locs = "".join(
                f"<url><loc>https://x/{r}</loc>"
                + (f"<lastmod>{m}</lastmod>" if m else "") + "</url>"
                for r, m in zip(keys, mods))
            (tmp / "sitemap.xml").write_text(f"<urlset>{locs}</urlset>")
            if specialists:
                (tmp / "sitemap-news.xml").write_text(
                    '<urlset xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"></urlset>')
                videos = [v for v in ((feed or {}).get("videos") or []) if isinstance(v, dict)]
                blocks = "".join("<video:video></video:video>" for _ in videos)
                (tmp / "sitemap-video.xml").write_text(
                    '<urlset xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">'
                    f'{blocks}</urlset>')
            if feed is not None:
                (tmp / "videos").mkdir(parents=True, exist_ok=True)
                (tmp / "videos" / "videos.json").write_text(json.dumps(feed))
            (tmp / "robots.txt").write_text(robots if robots is not None else good_robots)
            return findings(tmp)

    print("a clean build is called clean")
    check("no findings on a good site", run() == [], str(run()))

    print("\nand each defect that actually shipped is caught")
    ten = {f"p{i}/": pg() for i in range(10)} | {"": pg()}
    check("every url sharing one lastmod",
          any("share one lastmod" in f for f in run(ten, mods=["2026-08-19"] * 11)),
          str(run(ten, mods=["2026-08-19"] * 11)[:2]))
    check("a sitemap where no url carries a date at all",
          any("no url carries a lastmod" in f for f in
              run(mods=["", ""])), "")
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

    print("\nand the branded discovery surfaces are not inferred")
    check("the homepage h1 has to name the publication",
          any("primary heading does not name" in f for f in run(
              {"": pg(h1="<h1>AI is coming South.</h1>", head=logo, title="Home")})))
    check("the Organization graph has to name its logo",
          any("carries no logo" in f for f in run(
              {"": pg(h1=f"<h1>{BRAND}</h1>", title="Home")})))
    check("the stable about route cannot disappear again",
          any("stable entity page" in f for f in run(add_about=False)))
    check("specialist sitemap files cannot silently disappear",
          any("sitemap-news.xml: missing" in f for f in run(specialists=False)))
    duplicate = run({"": good_home, "a/": pg(title="Same"), "b/": pg(title="Same")})
    check("two pages cannot ask search to choose between the same title",
          any("title 'Same' is shared" in f for f in duplicate), str(duplicate))

    film = {"id": "film", "title": "A film", "video": "/film.mp4",
            "poster": "/poster.png", "date": "2026-08-19"}
    video_page = pg(h1="<h1>Videos</h1>", title="Videos")
    video_bad = run({"": good_home, "videos/": video_page}, feed={"videos": [film]})
    check("a film title has to exist in delivered HTML",
          any("absent from delivered HTML" in f for f in video_bad), str(video_bad))
    check("every complete film needs a VideoObject",
          any("fewer VideoObject" in f for f in video_bad), str(video_bad))

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
