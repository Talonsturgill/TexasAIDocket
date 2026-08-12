#!/usr/bin/env python3
"""house_style_check.py — the house rules, checked against the site that actually shipped.

WHY THE BUILT SITE AND NOT THE SOURCE

The copy a reader sees is assembled from f-strings across several builders and from fields in
the ledger. Grepping the Python finds the literals and misses everything the record supplied,
and grepping the ledger finds the record and misses the prose around it. The rendered page is
the only place the whole sentence exists.

Run against the real `docs/` this found four violations in copy written the same day the rules
were restated: two "cannot", a "we", and an "ours". They were invisible in review because every
one of them reads perfectly well. That is the entire argument for a lint.

THE RULE THAT MAKES THIS CORRECT: A QUOTE IS NEVER LINTED

Every claim in this record carries the source's own words, verbatim, and that is the mechanism
the whole product rests on. A source writes "July 31" and uses a curly apostrophe and cites a
range as "7-100". Rewriting any of that to fit house style would be falsifying a quotation,
which is a far worse failure than an inconsistent date.

So house style governs OUR prose and stops at the quotation mark. `<blockquote>` and `<cite>`
are stripped before checking, along with SVG geometry and markup attributes. If a violation is
reported here it is in a sentence this project wrote and can freely rewrite.

    house_style_check.py                 # checks docs/
    house_style_check.py --self-test
"""
from __future__ import annotations

import argparse
import html as _html
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "carousel"))

import caption_check                                               # noqa: E402

DOCS = REPO_ROOT / "docs"

MAIN = re.compile(r"<main\b[^>]*>(.*)</main>", re.DOTALL | re.IGNORECASE)
# Quoted material and its attribution. Stripped, never linted. See the module docstring.
QUOTED = re.compile(r"<(blockquote|cite)\b.*?</\1>", re.DOTALL | re.IGNORECASE)
SVG = re.compile(r"<svg\b.*?</svg>", re.DOTALL | re.IGNORECASE)
# Script and style CONTENT, not just their tags. Stripping tags alone leaves the code between
# them, and the ask page ships its whole engine and index inline: the lint then read a
# JavaScript identifier "i" as a first-person pronoun. Code is not reader-facing copy.
CODE = re.compile(r"<(script|style)\b.*?</\1>", re.DOTALL | re.IGNORECASE)
# TEXT IN THE READER'S VOICE, not the record's. The ask box's starter questions are phrased the
# way a person types them, which includes "What can I still comment on?". The no-first-person
# rule exists so the record does not speak as "we"; it was never meant to stop the page quoting
# the reader back to themselves. Marked explicitly at the source rather than inferred, so the
# exemption is a decision somebody made and can be found.
READER_VOICE = re.compile(r'<([a-z]+)\b[^>]*\bdata-voice="reader"[^>]*>.*?</\1>',
                          re.DOTALL | re.IGNORECASE)
TAG = re.compile(r"<[^>]+>")


def our_prose(page_html: str) -> str:
    """What this project wrote, with everything it merely reproduced taken out."""
    m = MAIN.search(page_html)
    body = m.group(1) if m else page_html
    body = READER_VOICE.sub(" ", QUOTED.sub(" ", CODE.sub(" ", SVG.sub(" ", body))))
    return _html.unescape(TAG.sub(" ", body))


def check_site(docs: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for page in sorted(docs.rglob("*.html")):
        try:
            text = page.read_text(encoding="utf-8")
        except OSError:
            continue
        problems = caption_check.check(our_prose(text))
        if problems:
            out[str(page.relative_to(docs))] = problems
    return out


def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    page = """<html><body><header>nav</header><main>
      <p>The commission set the hearing for August 11th.</p>
      <div class="claim">
        <blockquote>Comments are due August 21 and cannot be filed late.</blockquote>
        <cite>PUCT, Project 58000, retrieved 2026-08-11</cite>
      </div>
      <svg><text>40-60</text></svg>
    </main><footer>cannot</footer></body></html>"""

    prose = our_prose(page)
    ok("our own sentence survives the strip", "August 11th" in prose)
    ok("a quoted passage is removed before linting", "cannot be filed late" not in prose, prose)
    ok("...and so is its attribution", "Project 58000" not in prose)
    ok("SVG geometry is not prose", "40-60" not in prose)
    coded = our_prose('<main><p>Filed August 11th.</p>'
                      '<script>for (var i = 0; i < n; i++) { we.cannot(x); }</script>'
                      '<style>.a { width: 40-60px }</style></main>')
    ok("inline script is not prose", "cannot" not in coded and " i " not in f" {coded} ",
       coded)
    ok("inline style is not prose", "40-60" not in coded)
    ok("...and the sentence beside the code still is", "August 11th" in coded)
    voiced = our_prose('<main><p>Filed August 11th.</p>'
                       '<div data-voice="reader"><button>What can I comment on?</button></div>'
                       '</main>')
    ok("text marked as the reader's own voice is exempt", "What can I" not in voiced, voiced)
    ok("...and only what is marked", "August 11th" in voiced)
    ok("an unmarked first person is still caught",
       any("first person" in p for p in
           caption_check.check(our_prose("<main><p>What can I comment on?</p></main>"))))
    ok("the footer is outside main and not checked", "cannot" not in prose)
    ok("a clean page reports nothing", not caption_check.check(prose),
       str(caption_check.check(prose)))

    # THE GATE MUST GO RED. A violation in OUR prose is caught even when a quote nearby holds
    # the identical text legitimately.
    bad = page.replace("<p>The commission set the hearing for August 11th.</p>",
                       "<p>The hearing is August 11 and we cannot verify it.</p>")
    probs = caption_check.check(our_prose(bad))
    ok("a bare date in our own prose fails", any("ordinal" in p for p in probs), str(probs))
    ok('"cannot" in our own prose fails', any("can't" in p for p in probs))
    ok("first person in our own prose fails", any("first person" in p for p in probs))
    ok("...while the identical words inside the quote stay exempt",
       len([p for p in probs if "can't" in p]) == 1,
       "the quote's 'cannot' must not be counted a second time")

    ok("a page with no main element is still checked rather than skipped",
       bool(our_prose("<html><body><p>Filed August 11.</p></body></html>").strip()))

    if failures:
        print(f"\nhouse_style_check self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\nhouse_style_check self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--docs", default=str(DOCS))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    docs = Path(a.docs)
    if not docs.exists():
        print("house_style_check: no docs/ built yet, nothing to check")
        return 0

    found = check_site(docs)
    pages = sum(1 for _ in docs.rglob("*.html"))
    if not found:
        print(f"house style: clean across {pages} page(s)")
        return 0

    n = sum(len(v) for v in found.values())
    print(f"house_style_check: {n} violation(s) in copy this project wrote\n", file=sys.stderr)
    for page, problems in found.items():
        print(f"  {page}", file=sys.stderr)
        for p in problems:
            print(f"    - {p}", file=sys.stderr)
    print("\n  Quoted source text is exempt and was not checked. Everything above is a "
          "sentence\n  this project wrote and can rewrite. Fix it in the builder, not in "
          "docs/.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                       # noqa: BLE001
        print(f"house_style_check: broke: {exc}", file=sys.stderr)
        sys.exit(1)
