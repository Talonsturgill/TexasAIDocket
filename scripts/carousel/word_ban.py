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
  - a sentence of three words or more found inside a claim's verbatim quote or a source's own
    title, which is how a quotation a slide sets without quote marks, or a document page a
    canvas draws line by line, keeps its words. Two words are not enough, because a label such
    as "THE GAP" is the house's however many sources happen to say it

WHERE IT RUNS
  - the caption, through caption_check's post-level rules, while the caption room writes it
  - every surface of a run, through shipped_check's `banned words` gate and `--run` here:
      the caption and the first comment
      the document title LinkedIn prints over the carousel, and any other top-level title,
        hook, subtitle or story line copy.json carries
      every slide string copy.json holds, its machinery keys aside
      every word the render report says a slide printed, a canvas's drawn text included,
        because a short label set straight into a slide's HTML reaches no manifest and
        copy_sync_check lets a short unauthored string through by design
      each claim's own sentence, which the web edition's claim by claim verification prints
      the web edition in ledger/articles/, its section kicker included
  - the record, through docket_build's `banned words` gate, on any item a run verified after
    SINCE, its claims' own sentences included, and any movement note dated after it

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
# Top-level copy.json strings a reader is shown. site_context.article_title reads the first two
# and carries `hook`, `subtitle` and `story` onto the deck's page record.
COPY_TOP_FIELDS = ("document_title", "title", "hook", "subtitle", "story")
# A passage at least this long found inside a source's own words is the source's.
CONTAINED_MIN_WORDS = 3


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
    `quotes` are verbatim quotations. A sentence of CONTAINED_MIN_WORDS or more found inside
    either is the source's sentence, which covers a quotation or a title broken across lines."""
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
    theirs = [_squash(q) for q in (*quotes, *sources) if q and q.strip()]
    out = []
    for m in rx.finditer(text):
        if any(a <= m.start() and m.end() <= b for a, b in spans):
            continue
        sentence = next((s.group(0) for s in SENTENCE.finditer(text)
                         if s.start() <= m.start() < s.end()), "")
        said = _squash(sentence).strip(" .!?")
        if len(said.split()) >= CONTAINED_MIN_WORDS and any(said in q for q in theirs):
            continue
        around = text[max(0, m.start() - 40):m.end() + 40].replace("\n", " ").strip()
        out.append(f"{m.group(0)!r} in \"...{around}...\"")
    return out


def _strings(node, path="", skip=frozenset()):
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            if k not in skip:
                yield from _strings(v, f"{path}.{k}" if path else str(k), skip)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _strings(v, f"{path}[{i}]", skip)


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _claim_rows(d: Path) -> list:
    raw = _load(d / "claims.json")
    rows = raw.get("claims") if isinstance(raw, dict) else raw
    return [c for c in rows or [] if isinstance(c, dict)]


def _source_words(d: Path) -> tuple:
    """(sources, quotes) from the run's claims.json: what the sources wrote, not the house."""
    sources, quotes = [], []
    for c in _claim_rows(d):
        for f in SOURCE_FIELDS:
            v = c.get(f)
            if isinstance(v, str) and v.strip():
                (quotes if f in ("quote", "verbatim_quote") else sources).append(v)
    return tuple(sources), tuple(quotes)


def article_text(article: dict) -> list:
    """(where, text) for every reader-facing string of a web edition, per ledger/articles/README.

    The section prints in the page's kicker. The claim sentences the page's verification block
    prints come from the run's claims.json, and `check` reads them there."""
    out = []
    section = article.get("section")
    if isinstance(section, str):
        out.append(("section", section))
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


def _bounded_in(needle: str, hay: str) -> bool:
    """`needle` inside `hay` on word boundaries, so "the gap" is not found in "the gaping"."""
    return bool(needle) and re.search(rf"(?<!\w){re.escape(needle)}(?!\w)", hay) is not None


def rendered(d: Path, authored: str = "") -> list:
    """(where, text) for every string the committed render report says a slide printed that the
    authored slide strings do not already carry: a label set straight into the HTML, a canvas's
    drawn text. Furniture the design marked decorative is skipped, and so is a node another node
    on the same slide already contains, which is how a line split across spans arrives."""
    rep = next((r for r in (_load(d / "render_report.json"),
                            _load(d / "render" / "render_report.json")) if isinstance(r, dict)),
               None)
    if rep is None:
        return []
    have = _squash(authored)
    out = []
    for i, rec in enumerate(rep.get("slides") or [], start=1):
        if not isinstance(rec, dict):
            continue
        m = re.search(r"(\d+)", str(rec.get("file") or ""))
        n = rec.get("n") or (int(m.group(1)) if m else i)
        said = [str(t.get("text") or "") for t in rec.get("text_nodes") or []
                if isinstance(t, dict) and not t.get("decorative")]
        said += [str(t.get("text") or "") for t in rec.get("canvas_text") or []
                 if isinstance(t, dict)]
        by_form = {}
        for s in said:
            if s.strip():
                by_form.setdefault(_squash(s), s)
        kept = []
        for form in sorted(by_form, key=len, reverse=True):
            if _bounded_in(form, have) or any(_bounded_in(form, k) for k in kept):
                continue
            kept.append(form)
            out.append((f"rendered slide {n}", by_form[form]))
    return out


def check(d: Path, banned: list | None = None, articles: Path = ARTICLES) -> list | None:
    """Every banned word on a run's published surfaces. None when the run has no copy to read."""
    copy = _load(d / "copy.json")
    if copy is None:
        return None
    import copy_sync_check  # the one list of copy.json slide keys that are machinery, not copy
    banned = banned if banned is not None else words()
    sources, quotes = _source_words(d)
    surfaces = []
    caption = d / "caption.txt"
    surfaces.append(("caption", caption.read_text(encoding="utf-8") if caption.exists()
                     else str(copy.get("caption") or "")))
    for key in COPY_TOP_FIELDS:
        value = copy.get(key)
        if isinstance(value, str) and value.strip():
            surfaces.append((key.replace("_", " "), value))
    comment = d / "first_comment.txt"
    if comment.exists():
        surfaces.append(("first comment", comment.read_text(encoding="utf-8")))
    slides = list(_strings(copy.get("slides") or {}, "slides", copy_sync_check.META_KEYS))
    surfaces += slides
    surfaces += rendered(d, " ".join(s for _, s in slides))
    surfaces += [(f"claim {c.get('id', '?')}", str(c.get("text") or "")) for c in _claim_rows(d)]
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
    ok("...and so is a line of it a canvas drew, without its full stop",
       not hits("identified a pattern of incomplete", quotes=(quote,), banned=banned))
    ok("...and a line of a source's title broken across two",
       not hits("applications amid regulatory gap", sources=(title,), banned=banned))
    ok("...but a two word label is the house's, whatever a source says (Codex, PR 379)",
       len(hits("THE GAP", quotes=("The gap is widening.",), banned=banned)) == 1)
    ok("a word boundary decides containment, so 'the gap' is not inside 'the gaping'",
       not _bounded_in("the gap", "the gaping hole") and _bounded_in("the gap", "mind the gap"))

    with tempfile.TemporaryDirectory() as t:
        d, arts = Path(t) / "2026-09-28", Path(t) / "articles"
        d.mkdir()
        arts.mkdir()
        (d / "claims.json").write_text(json.dumps({"claims": [
            {"id": "c1", "source_title": title, "quote": quote,
             "text": "Council staff describe a pattern of incomplete filings."},
            {"id": "c2", "quote": quote,
             "text": "Staff identified a pattern of incomplete applications."}]}))
        (d / "copy.json").write_text(json.dumps({
            "caption": "", "document_title": "Why it matters", "slides": {
                "S1": {"headline": "Four filings, one pattern",
                       "notes": "planning residue about the gap, never rendered"},
                "S2": {"body": "Nine days apart."}}}))
        (d / "render_report.json").write_text(json.dumps({"slides": [
            {"file": "slide-01.html",
             "text_nodes": [{"text": "Four filings, one pattern", "decorative": False},
                            {"text": "THE GAP", "decorative": False},
                            {"text": "The gap", "decorative": False},
                            {"text": "a gap in the masthead rule", "decorative": True}],
             "canvas_text": [{"text": "identified a pattern of incomplete", "fn": "fillText"}]},
            {"file": "slide-02.html",
             "text_nodes": [{"text": "Nine days apart.", "decorative": False}],
             "canvas_text": [{"text": "Here is why it matters", "fn": "fillText"}]}]}))
        (d / "caption.txt").write_text("The council voted. Here is why it matters.\n")
        (d / "first_comment.txt").write_text(f"Sources.\n{title}, KGNS.\nhttps://example.com/gap\n")
        (arts / "2026-09-28.json").write_text(json.dumps({
            "section": "Pattern watch",
            "dek": {"text": "The gap in the calendar."}, "introduction": [{"text": "Clean."}],
            "sections": [{"heading": "What changed", "paragraphs": [{"text": "Nothing."}]}],
            "related": [{"id": "tx-1", "label": "The record"}]}))
        found = check(d, banned, arts)
        expected = ("caption", "document title", "slides.S1.headline", "rendered slide 1",
                    "rendered slide 2", "claim c1", "web edition section", "web edition dek")
        ok("a run's caption, document title, slide string, rendered label, canvas line, claim "
           "sentence, section kicker and dek are each caught once",
           len(found) == len(expected)
           and all(sum(f.startswith(e + ":") for f in found) == 1 for e in expected),
           "\n".join(found))
        ok("...and a source title, a URL, planning notes, decorative furniture, a claim sentence "
           "a source wrote and a drawn line of a quote are not", not any(
               f.startswith(("first comment", "claim c2")) or "planning residue" in f
               or "masthead" in f or (f.startswith("rendered slide 1") and "incomplete" in f)
               for f in found), "\n".join(found))
        (d / "render_report.json").unlink()
        (d / "render").mkdir()
        (d / "render" / "render_report.json").write_text(json.dumps({"slides": [
            {"file": "slide-01.html", "text_nodes": [{"text": "THE GAP", "decorative": False}]}]}))
        ok("an out/<date> run directory's render/render_report.json is read the same way",
           any(f.startswith("rendered slide 1") for f in check(d, banned, arts)))
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
