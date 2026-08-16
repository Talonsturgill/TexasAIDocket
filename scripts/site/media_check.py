#!/usr/bin/env python3
"""media_check.py — every image the published site points at actually exists.

WHY THIS EXISTS, AND THE RUN THAT PAID FOR IT

On 2026-08-16 the first shipped deck put two broken images on the live article page and dropped
two more slides entirely, and nobody found out until the owner opened the page and said so.

The chain, because each link was individually behaving correctly:

  1 `ship_images` encoded eight slides and two of them, the stipple paper register and the
    hachured soil section, came in under its 40 dB quality floor. It refused them. That was the
    RIGHT call and it printed PROBLEM and exited 1.
  2 The run shipped anyway, so the deck reached `runs/` with eight PNGs and six WebPs.
  3 `site_build` counted `slide-*.webp`, got six, and generated image URLs BY INDEX from that
    count. Slides 03 and 06 did not exist and rendered broken; 07 and 08 were never emitted.
    The homepage said "6 slides" for an eight slide deck.
  4 Every gate in the suite stayed green, because not one of them opened the page and asked
    whether the things it references are there.

**A gate that checks the builder's intent is not a gate that checks the product.** The suite
proved the site was byte-identical to what the builders produce, and both the builders and the
comparison were consistent about publishing a broken image.

WHAT IT CHECKS

Against the BUILT SITE, never against the code that built it:

  - every local image, stylesheet, script and font a page references resolves to a real file
  - every remote image served from this project's own repository resolves to a file in the repo
  - every shipped run named in `runs/` has one image per slide its `copy.json` plans
  - every article page carries the deck's words, not only its pictures, because a page that is
    eight images and a title publishes nothing indexable and nothing a screen reader can read

    media_check.py                      check docs/
    media_check.py --site /tmp/site     check a build somewhere else
    media_check.py --self-test          prove it can go red

EXIT 0 clean, 1 something the site points at is not there, 2 the checker could not run.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS = REPO_ROOT / "docs"
RUNS = REPO_ROOT / "runs" / "carousel"

# This project's own media host. A URL here is a file in this repository, so it is checkable
# without the network and a miss is a certainty rather than a guess.
RAW_PREFIX = "https://raw.githubusercontent.com/Talonsturgill/TexasAIDocket/main/"

REF = re.compile(r'(?:src|href)\s*=\s*"([^"]+)"', re.IGNORECASE)

# Extensions worth resolving. A page link to another page is checked by the link checker in
# site_build's own self-test; this file is about ASSETS, where a miss is silent.
ASSET_SUFFIXES = {".webp", ".png", ".jpg", ".jpeg", ".svg", ".gif", ".css", ".js",
                  ".woff2", ".woff", ".ttf", ".ico", ".json", ".txt", ".xml", ".pdf"}

# A page whose whole content is pictures. Set from the shortest article the sibling product
# publishes, well under it, so this catches "images only" and never argues about house style.
MIN_ARTICLE_WORDS = 150

TAGS = re.compile(r"<[^>]+>")
SCRIPTY = re.compile(r"<(script|style)\b.*?</\1>", re.DOTALL | re.IGNORECASE)


def visible_words(markup: str) -> int:
    text = html.unescape(TAGS.sub(" ", SCRIPTY.sub(" ", markup)))
    return len(text.split())


def findings(site: Path, repo: Path = REPO_ROOT) -> list[str]:
    out: list[str] = []
    if not site.is_dir():
        return [f"no built site at {site}"]

    pages = sorted(site.rglob("*.html"))
    if not pages:
        return [f"no pages under {site}"]

    for page in pages:
        rel = page.relative_to(site)
        markup = page.read_text(encoding="utf-8", errors="replace")
        for raw in REF.findall(markup):
            ref = html.unescape(raw).split("#")[0].split("?")[0]
            if not ref:
                continue

            if ref.startswith(RAW_PREFIX):
                target = repo / ref[len(RAW_PREFIX):]
                if not target.exists():
                    out.append(f"{rel}: points at {ref[len(RAW_PREFIX):]}, which is not in "
                               f"the repository. A reader gets a broken image")
                continue

            if ref.startswith(("http://", "https://", "mailto:", "data:", "tel:", "//")):
                continue
            if Path(ref).suffix.lower() not in ASSET_SUFFIXES:
                continue
            base = site if ref.startswith("/") else page.parent
            if not (base / ref.lstrip("/")).resolve().exists():
                out.append(f"{rel}: points at {ref}, which is not in the built site")

    # EVERY SLIDE OF EVERY SHIPPED DECK HAS AN IMAGE. Checked against the run's own manifest,
    # which is what the deck IS, rather than against whichever files happen to have survived.
    if RUNS.is_dir():
        for d in sorted(x for x in RUNS.iterdir() if x.is_dir()):
            try:
                planned = json.loads((d / "copy.json").read_text("utf-8")).get("slides")
            except Exception:                                        # noqa: BLE001
                continue
            n = len(planned) if isinstance(planned, (list, dict)) else 0
            for i in range(1, n + 1):
                if not any((d / f"slide-{i:02d}.{x}").exists() for x in ("webp", "png")):
                    out.append(f"runs/carousel/{d.name}: slide-{i:02d} is planned in copy.json "
                               f"and has no webp and no png")

    # AN ARTICLE PAGE PUBLISHES ITS WORDS. Images carry no text to a search engine, a screen
    # reader, or a reader on a slow connection with images off.
    for page in sorted(site.glob("articles/*/index.html")):
        words = visible_words(page.read_text(encoding="utf-8", errors="replace"))
        if words < MIN_ARTICLE_WORDS:
            out.append(f"articles/{page.parent.name}/: {words} words of text. The deck's own "
                       f"copy is in its copy.json and belongs on the page, or this publishes "
                       f"pictures and nothing a reader or an index can use")
    return out


def self_test() -> int:
    import tempfile
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    with tempfile.TemporaryDirectory() as td:
        site = Path(td) / "site"
        (site / "articles" / "2026-01-01").mkdir(parents=True)
        (site / "img").mkdir()
        (site / "img" / "there.png").write_text("x", encoding="utf-8")
        words = " ".join(["word"] * (MIN_ARTICLE_WORDS + 20))

        good = f'<html><body><img src="../../img/there.png"><p>{words}</p></body></html>'
        (site / "articles" / "2026-01-01" / "index.html").write_text(good, encoding="utf-8")
        (site / "index.html").write_text('<img src="img/there.png">', encoding="utf-8")
        ok("a site whose assets all resolve is clean", findings(site) == [],
           str(findings(site)))

        # THE DEFECT OF 2026-08-16, in both of its halves.
        (site / "index.html").write_text('<img src="img/missing.png">', encoding="utf-8")
        f = findings(site)
        ok("a local image that is not there is CAUGHT", any("missing.png" in x for x in f),
           str(f))
        (site / "index.html").write_text('<img src="img/there.png">', encoding="utf-8")

        (site / "index.html").write_text(
            f'<img src="{RAW_PREFIX}runs/carousel/2026-01-01/slide-03.webp">', encoding="utf-8")
        f = findings(site)
        ok("...and so is one served from this project's own repository",
           any("slide-03.webp" in x for x in f), str(f))
        (site / "index.html").write_text('<img src="img/there.png">', encoding="utf-8")

        thin = '<html><body><img src="../../img/there.png"><h1>A title</h1></body></html>'
        (site / "articles" / "2026-01-01" / "index.html").write_text(thin, encoding="utf-8")
        f = findings(site)
        ok("an article page that is pictures and a title is CAUGHT",
           any("words of text" in x for x in f), str(f))
        (site / "articles" / "2026-01-01" / "index.html").write_text(good, encoding="utf-8")

        ok("...and the same page with its words is clean again", findings(site) == [],
           str(findings(site)))

        # A page link is not an asset, or every relative link becomes a false finding and the
        # gate gets switched off inside a week.
        (site / "index.html").write_text(
            '<a href="record/">The record</a><img src="img/there.png">', encoding="utf-8")
        ok("a link to another page is not treated as a missing asset", findings(site) == [],
           str(findings(site)))

        (site / "index.html").write_text(
            '<img src="https://example.com/elsewhere.png">', encoding="utf-8")
        ok("an image on somebody else's host is not guessed at", findings(site) == [],
           str(findings(site)))

    # AND AGAINST THE REAL SITE, because this file exists to protect that one.
    if DOCS.is_dir():
        real = findings(DOCS)
        ok("the published site points at nothing that is missing", real == [],
           " | ".join(real[:4]))

    if failures:
        print(f"\nmedia_check self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\nmedia_check self-test: all passed (the gate can go red)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--site", default=str(DOCS))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        return self_test()

    found = findings(Path(a.site))
    if not found:
        print(f"media: clean, every reference in {a.site} resolves")
        return 0
    print(f"media: {len(found)} broken reference(s)", file=sys.stderr)
    for f in found:
        print(f"  - {f}", file=sys.stderr)
    print("\n  A reader sees a broken image for every one of these. Fix the builder, never "
          "docs/.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                         # noqa: BLE001
        print(f"media_check: broke: {exc}", file=sys.stderr)
        sys.exit(2)
