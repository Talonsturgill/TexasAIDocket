#!/usr/bin/env python3
"""word_ban.py — the words the owner banned never reach a published surface.

    python3 scripts/carousel/word_ban.py --run 2026-09-28     every surface that run publishes
    python3 scripts/carousel/word_ban.py --text <file>        one draft, a caption say
    python3 scripts/carousel/word_ban.py --self-test

WHY THIS EXISTS

The owner, 2026-09-27: "on both automations ban the words 'gap' and 'matters' and 'pattern'".
The list is `brand.banned_words` in config/brand.yaml, which is `human` lane, so no run can
shorten it, and this file never types a word of it. Each is matched as a whole word in any case,
so "Singapore" is not "gap", and "matter" in "no matter" or "subject matter" is not "matters".
A compound counts, because "wage-gap" still prints the word.

WHAT IS EXEMPT, because it is somebody else's words and a quotation is never rewritten:
  - a passage inside straight double quotes, the only quotation mark the house sets
  - a URL, which is an address and not prose. Legistar files its items under `/Matters/`
  - a source's own title, document name or attribution as the run's claims.json records it,
    which is how a report titled "...amid regulatory gap" reaches the first comment
  - a sentence the run's claims.json carries inside a claim's verbatim quote

WHERE IT RUNS
  - the caption, through caption_check's post-level rules, while the caption room writes it
  - every surface of a run, through shipped_check's `banned words` gate and `--run` here: the
    caption, the first comment, the document title LinkedIn prints over the carousel, every
    slide string and the web edition in ledger/articles/
  - the record, through docket_build's `banned words` gate, on any item a run verified after
    SINCE and any movement note dated after it

SINCE is 2026-09-27, the last deck shipped before the rule. Nothing published on or before it is
judged as a failure, because published copy is not rewritten without the owner. shipped_check
still measures those decks and prints what it finds as a note.

EXIT CODES: 0 clean, 1 a banned word on a surface, 2 nothing to read.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
BRAND = REPO_ROOT / "config" / "brand.yaml"
RUNS = REPO_ROOT / "runs" / "carousel"
ARTICLES = REPO_ROOT / "ledger" / "articles"
SINCE = "2026-09-27"

QUOTED = re.compile(r'"[^"\n]*"')
URL = re.compile(r"https?://\S+|www\.\S+")
SENTENCE = re.compile(r"[^.!?\n]+[.!?]?")
# The claim fields that carry a source's own words rather than the house's.
SOURCE_FIELDS = ("source_title", "document", "attribution", "quote", "verbatim_quote")


def words(path: Path = BRAND) -> list:
    """The banned words, from brand.yaml. Never a literal in this file."""
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    listed = (doc.get("brand") or {}).get("banned_words")
    if not isinstance(listed, list) or not all(isinstance(w, str) and w.strip() for w in listed):
        raise ValueError(f"{path} has no brand.banned_words list, which is where the owner's "
                         f"banned words live")
    return [w.strip() for w in listed]


def matcher(banned: list) -> re.Pattern:
    alternatives = "|".join(re.escape(w) for w in sorted(banned, key=len, reverse=True))
    return re.compile(rf"\b(?:{alternatives})\b", re.I)


def _squash(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def hits(text: str, *, sources: tuple = (), quotes: tuple = (), banned: list | None = None) -> list:
    """Each banned word in `text` that the house wrote, with the words around it.

    `sources` are passages that are a source's own words wherever they appear, a title say.
    `quotes` are verbatim quotations. A sentence found inside one is the source's sentence."""
    rx = matcher(banned if banned is not None else words())
    spans = [m.span() for m in QUOTED.finditer(text)] + [m.span() for m in URL.finditer(text)]
    low = text.lower()
    for s in sources:
        s = s.strip().lower()
        if len(s) < 4:
            continue
        start = low.find(s)
        while start != -1:
            spans.append((start, start + len(s)))
            start = low.find(s, start + 1)
    squashed_quotes = [_squash(q) for q in quotes if q and q.strip()]
    out = []
    for m in rx.finditer(text):
        if any(a <= m.start() and m.end() <= b for a, b in spans):
            continue
        sentence = next((s.group(0) for s in SENTENCE.finditer(text)
                         if s.start() <= m.start() < s.end()), "")
        if sentence.strip() and any(_squash(sentence).strip(" .!?") in q for q in squashed_quotes):
            continue
        around = text[max(0, m.start() - 40):m.end() + 40].replace("\n", " ").strip()
        out.append(f"{m.group(0)!r} in \"...{around}...\"")
    return out


def _strings(node, path=""):
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from _strings(v, f"{path}.{k}" if path else str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _strings(v, f"{path}[{i}]")


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _source_words(d: Path) -> tuple:
    """(sources, quotes) from the run's claims.json: what the sources wrote, not the house."""
    raw = _load(d / "claims.json")
    rows = raw.get("claims") if isinstance(raw, dict) else raw
    sources, quotes = [], []
    for c in rows or []:
        if not isinstance(c, dict):
            continue
        for f in SOURCE_FIELDS:
            v = c.get(f)
            if isinstance(v, str) and v.strip():
                (quotes if f in ("quote", "verbatim_quote") else sources).append(v)
    return tuple(sources), tuple(quotes)


def article_text(article: dict) -> list:
    """(where, text) for every reader-facing string of a web edition, per ledger/articles/README."""
    out = []
    dek = article.get("dek")
    if isinstance(dek, dict):
        out.append(("dek", str(dek.get("text") or "")))
    for i, p in enumerate(article.get("introduction") or []):
        if isinstance(p, dict):
            out.append((f"introduction[{i}]", str(p.get("text") or "")))
    for i, s in enumerate(article.get("sections") or []):
        if not isinstance(s, dict):
            continue
        out.append((f"sections[{i}].heading", str(s.get("heading") or "")))
        for j, p in enumerate(s.get("paragraphs") or []):
            if isinstance(p, dict):
                out.append((f"sections[{i}].paragraphs[{j}]", str(p.get("text") or "")))
    for i, r in enumerate(article.get("related") or []):
        if isinstance(r, dict):
            out.append((f"related[{i}].label", str(r.get("label") or "")))
    return out


def check(d: Path, banned: list | None = None, articles: Path = ARTICLES) -> list | None:
    """Every banned word on a run's published surfaces. None when the run has no copy to read."""
    copy = _load(d / "copy.json")
    if copy is None:
        return None
    banned = banned if banned is not None else words()
    sources, quotes = _source_words(d)
    surfaces = []
    caption = d / "caption.txt"
    surfaces.append(("caption", caption.read_text(encoding="utf-8") if caption.exists()
                     else str(copy.get("caption") or "")))
    title = copy.get("document_title")
    if isinstance(title, str) and title.strip():
        surfaces.append(("document title", title))
    comment = d / "first_comment.txt"
    if comment.exists():
        surfaces.append(("first comment", comment.read_text(encoding="utf-8")))
    for where, s in _strings(copy.get("slides") or {}, "slides"):
        surfaces.append((where, s))
    article = _load(articles / f"{d.name}.json")
    if isinstance(article, dict):
        surfaces += [(f"web edition {w}", t) for w, t in article_text(article)]
    out = []
    for where, text in surfaces:
        for h in hits(text, sources=sources, quotes=quotes, banned=banned):
            out.append(f"{where}: {h}. The owner banned it on 2026-09-27 (config/brand.yaml "
                       f"banned_words). Say the specific thing instead")
    return out


def self_test() -> int:
    failures = 0

    def ok(name, cond, detail=""):
        nonlocal failures
        print(("ok    " if cond else "FAIL  ") + name + ("" if cond else f"  {detail}"))
        failures += 0 if cond else 1

    banned = words()
    ok("the list is brand.yaml's, and it carries the three words the owner named",
       {"gap", "matters", "pattern"} <= {w.lower() for w in banned}, str(banned))
    for text in ("The gap between the two filings is nine days.", "Why it matters for Austin.",
                 "A pattern of late filings.", "Two GAPS in the record.", "PATTERNS repeat.",
                 "The wage-gap figure."):
        ok(f"caught: {text}", len(hits(text, banned=banned)) == 1, str(hits(text, banned=banned)))
    for text in ("Singapore filed first.", "No matter what the council decides.",
                 "The subject matter of the hearing.", "It matter-of-factly says so.",
                 'The report says "the gap is widening" in its first line.',
                 "https://webapi.legistar.com/v1/elpasotexas/Matters/15758",
                 "The patterned glass facade."):
        ok(f"kept: {text}", not hits(text, banned=banned), str(hits(text, banned=banned)))
    title = "Council moves to freeze data center applications amid regulatory gap"
    ok("a source's own title is the source's words",
       not hits(f"{title}, KGNS, September 3rd.", sources=(title,), banned=banned))
    ok("...and the house's sentence beside it is still judged",
       len(hits(f"{title}, KGNS. The gap is ours.", sources=(title,), banned=banned)) == 1)
    quote = "Staff identified a pattern of incomplete applications in the second quarter."
    ok("a sentence a claim quotes verbatim is the source's sentence",
       not hits("Staff identified a pattern of incomplete applications.", quotes=(quote,),
                banned=banned))

    with tempfile.TemporaryDirectory() as t:
        d, arts = Path(t) / "2026-09-28", Path(t) / "articles"
        d.mkdir()
        arts.mkdir()
        (d / "claims.json").write_text(json.dumps({"claims": [
            {"id": "c1", "source_title": title, "quote": quote}]}))
        (d / "copy.json").write_text(json.dumps({"caption": "", "document_title": "Why it matters",
                                                 "slides": {
            "S1": {"headline": "Four filings, one pattern"}, "S2": {"body": "Nine days apart."}}}))
        (d / "caption.txt").write_text("The council voted. Here is why it matters.\n")
        (d / "first_comment.txt").write_text(f"Sources.\n{title}, KGNS.\nhttps://example.com/gap\n")
        (arts / "2026-09-28.json").write_text(json.dumps({
            "dek": {"text": "The gap in the calendar."}, "introduction": [{"text": "Clean."}],
            "sections": [{"heading": "What changed", "paragraphs": [{"text": "Nothing."}]}],
            "related": [{"id": "tx-1", "label": "The record"}]}))
        found = check(d, banned, arts)
        ok("a run's caption, document title, slide and web edition are each caught",
           len(found) == 4 and any(f.startswith("caption") for f in found)
           and any(f.startswith("document title") for f in found)
           and any("slides.S1.headline" in f for f in found)
           and any(f.startswith("web edition dek") for f in found), "\n".join(found))
        ok("...and the first comment's source title and URL are not", not any(
            f.startswith("first comment") for f in found), "\n".join(found))
        (d / "copy.json").unlink()
        ok("a directory with no copy.json has nothing to read", check(d, banned, arts) is None)

    print(f"\nword_ban self-test: {'all passed' if not failures else f'{failures} FAILED'}")
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", help="a run date, e.g. 2026-09-28")
    ap.add_argument("--text", help="a file of copy to judge, a caption draft say")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.text:
        found = hits(Path(a.text).read_text(encoding="utf-8"))
        for f in found:
            print(f"word_ban: {f}")
        print(f"word_ban: {len(found)} banned word(s) in {a.text}")
        return 1 if found else 0
    if not a.run:
        print("word_ban: pass --run <date>, --text <file> or --self-test", file=sys.stderr)
        return 2
    found = check(RUNS / a.run)
    if found is None:
        print(f"word_ban: no copy.json under runs/carousel/{a.run}", file=sys.stderr)
        return 2
    for f in found:
        print(f"word_ban: {f}")
    print(f"word_ban: {len(found)} banned word(s) on {a.run}'s published surfaces")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
