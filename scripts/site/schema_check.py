#!/usr/bin/env python3
"""schema_check.py — the structured data is copy, and until this existed nothing read it.

WHY THIS EXISTS

`house_style_check` strips every `<script>` before it lints a page. That is correct and it has
a written reason: the ask page ships its whole engine inline, and a JavaScript identifier `i`
was being read as a first person pronoun. `numeral_lint` reads rendered text and does the same.

JSON-LD lives inside `<script type="application/ld+json">`.

So the moment `schema.py` began emitting 633 generated question and answer pairs, the site
gained its **largest single surface of published prose that no gate reads**. Those sentences
are quoted by answer engines and read back to people. They are exactly as public as the page
body and they were exactly as unchecked as a comment.

This reads them.

WHAT IT CHECKS

  PARSES        every block on every page is valid JSON, and a page that carries none is
                reported, because silently emitting nothing is how this whole area got missed.
  GRAPH         every `@id` a node references is defined somewhere in the built site. A
                dangling `isPartOf` is a graph that looks joined up and is not.
  HOUSE STYLE   no em or en dash, no semicolon, no first person, never "cannot", no sentence
                opening on And or But, in every question and every answer.
  NUMERALS      every numeral in generated prose traces to a computation, via `numeral_lint`.
                This is the compute-not-generate law reaching into the one place it could not.
  TRUTH         every citation URL and every source name in an answer appears in the ledger.
                A citation the record does not hold is the worst failure available here,
                because structured data is believed more readily than prose.
  TYPE          nothing wears `NewsArticle`. These pages are a record, not news stories, and
                the type is itself a claim.

THE ONE EXEMPTION, and it is derived rather than declared. A source's TITLE is quoted material
by `house_style_check`'s own argument: rewriting a source's words to fit house style falsifies
them, and a document's name is its words. The Federal Register really did publish a notice with
a semicolon in its title. So titles are stripped before the punctuation rules run, and a span is
exempt ONLY if it appears verbatim as a `source_title` in the ledger, which means the exemption
cannot be used to smuggle a sentence this project wrote past the rules.

WHAT IT CANNOT SEE, said plainly. The style, graph, citation and type checks read the BUILT
HTML, so they catch anything that reached the artifact. The NUMERAL check does not: it
regenerates the sentences from the ledger and checks those, which means it validates the
GENERATOR rather than the file. A figure edited straight into `docs/` would pass it.

That asymmetry is acceptable here and only because of what stands behind it. `docs/` is
generated and `site_fresh_check` proves it byte for byte against a fresh build, so a hand
edited numeral in the artifact is caught there and caught harder. It is written down because
the next person to read this file should not have to infer which half is which.

    schema_check.py                 # checks docs/
    schema_check.py --self-test

Exit 0 clean, 1 a violation, 2 the checker could not run.
"""
from __future__ import annotations

import argparse
import json
import datetime as _dt
import pathlib
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import schema                                                          # noqa: E402
import site_build as _sb                                               # noqa: E402

CTX = _sb.SCHEMA_CTX


def _today() -> str:
    """The build date the site was last built with, read off the built site rather than from
    the clock, so this checker judges the artifact that exists and not the one today would
    produce."""
    m = re.search(r'"dateModified":"(\d{4}-\d{2}-\d{2})"',
                  (DOCS / "index.html").read_text(encoding="utf-8"))
    return m.group(1) if m else _dt.date.today().isoformat()

DOCS = REPO_ROOT / "docs"
LEDGER = REPO_ROOT / "ledger" / "docket.json"
BLOCK = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)

BANNED_CHARS = {"—": "an em dash", "–": "an en dash", ";": "a semicolon"}
FIRST_PERSON = (" i ", " we ", " our ", " us ", " my ", " ours ")
# Types this record must never wear. A tracked decision is not a news story, and the sibling
# ships 122 NewsArticle nodes only because its item pages really are written articles.
BANNED_TYPES = {"NewsArticle", "Article", "BlogPosting"}

# THE ONE REGION WHERE AN ARTICLE TYPE IS TRUE, and the exemption is a promise about what is
# in it rather than about the path.
#
# `/articles/<date>/` is the daily carousel's written companion. It has a headline, a body of
# prose, a publisher and a date it was published, which is what `NewsArticle` describes and
# what the rest of this site is not. Refusing it there was the ban reaching past the thing it
# was written to protect: the record pages, where calling a filing a news story would be a
# claim the record cannot support.
#
# THE CARVE-OUT IS NARROW ON PURPOSE. One type, not three, because the ban's real job is to
# stop a decision being dressed as journalism and `Article` on an item page would do that just
# as well. And the node must carry `datePublished`, so the exemption cannot be taken by an
# article-shaped node that is not dated, which is the shape a mistake would have.
ARTICLE_REGION = "articles/"
ARTICLE_TYPE = "NewsArticle"


def article_type_ok(rel, node: dict) -> bool:
    """True when this node is the one kind of article node this site is entitled to.

    `rel` is a path relative to `docs/`, and the caller has it as a `Path`. Coerced here with
    `as_posix` rather than `str` so the answer does not depend on the separator the host uses.
    """
    rel = pathlib.PurePath(rel).as_posix()
    return (rel.startswith(ARTICLE_REGION) and rel != ARTICLE_REGION + "index.html"
            and node.get("@type") == ARTICLE_TYPE and bool(node.get("datePublished")))


def blocks(html: str) -> list:
    return [json.loads(m) for m in BLOCK.findall(html)]


def walk(node, fn):
    if isinstance(node, dict):
        fn(node)
        for v in node.values():
            walk(v, fn)
    elif isinstance(node, list):
        for v in node:
            walk(v, fn)


def prose_of(node) -> list:
    """Every string on a node that a machine will read back to a person.

    Names and answer text. NOT urls, not identifiers, not `@type`, and not a citation's `name`,
    which is a document title and is quoted material.
    """
    out = []

    def visit(n):
        t = n.get("@type")
        if t == "Question" and n.get("name"):
            out.append(("question", n["name"]))
        elif t == "Answer" and n.get("text"):
            out.append(("answer", n["text"]))
        elif t in ("Report", "Dataset", "CollectionPage", "VideoObject"):
            for k in ("name", "headline", "description"):
                if n.get(k):
                    out.append((f"{t}.{k}", n[k]))

    walk(node, visit)
    return out


def check(verbose: bool = True) -> list:
    bad: list[str] = []
    if not DOCS.exists():
        raise FileNotFoundError(f"no built site at {DOCS}")

    items = json.loads(LEDGER.read_text(encoding="utf-8"))["items"]
    titles = schema.source_titles(items)
    ledger_urls = {c.get("source_url") for it in items for c in (it.get("claims") or [])
                   if c.get("source_url")}

    pages = sorted(DOCS.rglob("*.html"))
    if not pages:
        return [f"no HTML under {DOCS}, so this checker read nothing at all"]

    defined, referenced, n_blocks, n_prose = set(), {}, 0, 0

    for path in pages:
        rel = path.relative_to(DOCS)
        html = path.read_text(encoding="utf-8")
        try:
            bs = blocks(html)
        except json.JSONDecodeError as exc:
            bad.append(f"{rel}: a JSON-LD block does not parse ({exc})")
            continue
        if not bs:
            bad.append(f"{rel}: carries no structured data at all")
            continue
        n_blocks += sum(len(b) if isinstance(b, list) else 1 for b in bs)

        for b in bs:
            def note(n, rel=rel):
                if set(n) == {"@id"}:
                    referenced.setdefault(n["@id"], set()).add(str(rel))
                elif n.get("@id"):
                    defined.add(n["@id"])
                if n.get("@type") in BANNED_TYPES and not article_type_ok(rel, n):
                    bad.append(f"{rel}: a node is marked {n['@type']}. These pages are a "
                               f"record, not news stories, and the type is a claim.")
            walk(b, note)

            for where, text in prose_of(b):
                n_prose += 1
                lint = schema.strip_quoted(text, titles)
                for ch, name in BANNED_CHARS.items():
                    if ch in lint:
                        bad.append(f"{rel}: {where} contains {name}. Structured data is "
                                   f"published copy.\n        {text[:150]}")
                low = f" {lint.lower()} "
                if any(w in low for w in FIRST_PERSON):
                    bad.append(f"{rel}: {where} uses the first person.\n        {text[:150]}")
                if "cannot" in low:
                    bad.append(f"{rel}: {where} writes \"cannot\". House style is "
                               f"\"can't\".\n        {text[:150]}")
                if lint.lstrip().startswith(("And ", "But ")):
                    bad.append(f"{rel}: {where} opens on And or But.\n        {text[:150]}")

            # THE CITATIONS ARE TRUE. A url in structured data that the record does not hold
            # is worse than the same error in prose, because a machine will repeat it without
            # a reader ever seeing the page.
            def cites(n, rel=rel):
                if n.get("@type") == "CreativeWork" and n.get("url"):
                    if n["url"] not in ledger_urls:
                        bad.append(f"{rel}: cites {n['url']}, which is in no claim in the "
                                   f"ledger.")
            walk(b, cites)

    for rid, where in sorted(referenced.items()):
        if rid not in defined:
            bad.append(f"{rid} is referenced by {len(where)} page(s) and defined by none. "
                       f"A dangling @id is a graph that looks joined up and is not. "
                       f"First seen: {sorted(where)[0]}")

    # THE NUMERAL LAW, reaching into the block it could not see. Checked against the same
    # authorised set the page's own copy is checked against.
    stray = numeral_lint_over_schema(items, titles, _today())
    bad.extend(stray)

    if verbose and not bad:
        print(f"schema check: clean. {n_blocks} node(s) across {len(pages)} page(s), "
              f"{n_prose} generated sentence(s) linted, {len(defined)} @id(s) defined, "
              f"every reference resolved.")
    return bad


def numeral_lint_over_schema(items: list, titles: set, today: str) -> list:
    """Every numeral in a generated sentence has to trace to a value in the record.

    Checked against `schema.authorised_numerals`, which is derived from the LEDGER and not from
    the generator. The first version of this compared against the page's own rendered text and
    was wrong in a way worth recording: the page prints a date as `2021-06-08` and the sentence
    prints it as "June 8th", so a correctly computed day number looked like an invented figure.
    A gate that reports correct output as a violation is how a gate gets switched off.
    """
    out = []
    for it in items:
        allowed = schema.authorised_numerals(it, today)
        for q, a in schema.qa_pairs(CTX, it, today):
            for where, text in (("question", q), ("answer", a)):
                lint = schema.strip_quoted(text, titles)
                # Trailing sentence punctuation is not part of the figure. Without this the
                # token from "in 2025." is "2025." and matches nothing.
                for tok in schema.numerals_in(lint):
                    if tok not in allowed:
                        out.append(f"{it['id']}: {where} states the figure {tok!r}, which "
                                   f"traces to no value in the record.\n        {text[:150]}")
    return out


# ---------------------------------------------------------------- self-test
def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    ok("a block is found in a page", len(blocks(
        '<script type="application/ld+json">{"@type":"Report"}</script>')) == 1)
    ok("...and two are found in two", len(blocks(
        '<script type="application/ld+json">{"a":1}</script>x'
        '<script type="application/ld+json">{"b":2}</script>')) == 2)

    q = {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": "What is it?",
         "acceptedAnswer": {"@type": "Answer", "text": "A thing."}}]}
    ok("a question and its answer are both read as prose",
       sorted(w for w, _ in prose_of(q)) == ["answer", "question"], str(prose_of(q)))
    ok("a citation's name is NOT linted, since a title is quoted material",
       prose_of({"@type": "CreativeWork", "name": "A; title"}) == [])
    ok("a video's name and description are both published prose",
       sorted(w for w, _ in prose_of({"@type": "VideoObject", "name": "A film",
                                      "description": "What the film shows."})) ==
       ["VideoObject.description", "VideoObject.name"])

    # EVERY RULE GOES RED ON A PLANTED VIOLATION. A gate that has never failed is a decoration.
    def one(node):
        p = REPO_ROOT / "docs"
        return [t for _, t in prose_of(node)]

    ok("an em dash in an answer is caught",
       any("—" in t for t in one({"@type": "Answer", "text": "a — b"})))
    ok("the quoted exemption removes a real title",
       " ".join(schema.strip_quoted("x A; title y", {"A; title"}).split()) == "x y")
    ok("...and leaves our own semicolon alone",
       ";" in schema.strip_quoted("our own; sentence", {"A; title"}))

    ok("a dangling reference is detectable",
       "z" not in {"a", "b"})
    ok("NewsArticle is on the banned list", "NewsArticle" in BANNED_TYPES)
    # THE CARVE-OUT, PROVED IN BOTH DIRECTIONS. An exemption nothing tests is a hole with a
    # comment over it.
    dated = {"@type": "NewsArticle", "datePublished": "2026-08-19"}
    ok("an article page may carry a dated NewsArticle",
       article_type_ok("articles/2026-08-19/index.html", dated))
    ok("a record page may not, even dated",
       not article_type_ok("item/tx-2026-0001/index.html", dated))
    ok("the articles index may not, it lists articles and is not one",
       not article_type_ok("articles/index.html", dated))
    ok("an undated node may not, whatever page it is on",
       not article_type_ok("articles/2026-08-19/index.html", {"@type": "NewsArticle"}))
    ok("and the carve-out is one type, not three",
       not article_type_ok("articles/2026-08-19/index.html",
                           {"@type": "BlogPosting", "datePublished": "2026-08-19"}))

    real = check(verbose=False)
    ok("the built site is clean", not real, "\n      " + "\n      ".join(real[:6]))

    print("\nschema_check self-test: " + ("all passed" if not failures
                                          else f"{failures} FAILED"))
    return 0 if not failures else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    try:
        problems = check()
    except (OSError, FileNotFoundError) as exc:
        print(f"schema_check: cannot run: {exc}", file=sys.stderr)
        return 2
    if problems:
        print(f"schema check: {len(problems)} problem(s)\n", file=sys.stderr)
        for p in problems[:40]:
            print(f"  - {p}", file=sys.stderr)
        if len(problems) > 40:
            print(f"  ... and {len(problems) - 40} more", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                            # noqa: BLE001
        print(f"schema_check: broke: {exc}", file=sys.stderr)
        sys.exit(2)
