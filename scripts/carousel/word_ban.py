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
  - a passage inside straight double quotes, the only quotation mark the house sets, which may
    break across a line but not across a blank line
  - a URL, which is an address and not prose. Legistar files its items under `/Matters/`
  - a source's own title, publisher or attribution as the run's claims.json records it, in any
    field sources_block.TITLE_KEYS prints, which is how a report titled "...amid regulatory gap"
    or a publisher named Pattern Energy reaches the first comment
  - a sentence of three words or more found inside a claim's verbatim quote or a source's own
    title, which is how a quotation a slide sets without quote marks, or a document page a
    canvas draws line by line, keeps its words. Two words are not enough, because a label such
    as "THE GAP" is the house's however many sources happen to say it. A slide and a web edition
    block count only the claims they cite, and a claim's own sentence only its own quote and
    title, since each prints beside that evidence. A surface citing nothing counts every claim

WHERE IT RUNS
  - the caption, through caption_check's post-level rules, while the caption room writes it
  - every surface of a run, through shipped_check's `banned words` gate and `--run` here:
      the caption and the first comment
      the document title LinkedIn prints over the carousel, and any other top-level title,
        hook, subtitle or story line copy.json carries
      every slide string copy.json holds, its machinery keys aside
      every word the render report says a slide printed, text the design marked decorative
        and a canvas's drawn text included, and every string a slide's own CSS prints through
        `content`, because a short label set straight into a slide's
        HTML reaches no manifest and copy_sync_check lets a short unauthored string through
      each claim's own sentence, which the web edition's claim by claim verification prints
      the web edition in ledger/articles/, its section kicker included
  - the record, through docket_build's `banned words` gate, on any item a run verified after
    SINCE, its claims' own sentences included, and any movement note dated after it. A record
    field cites no single claim, so it counts every claim its item carries

WHAT IT CAN'T SEE, stated so nobody reads "every printed word" as more than it is. Lettering the
3D kit strokes as paths never reaches the render report. Today that is one thing, the town name
a water tower paints on its tank, which defaults to TEXAS. The kit draws it that way on purpose,
so qa.py's canvas text warning doesn't fire on art. Reading it needs a channel in render.py,
which is a protected path, so the fix waits for a maintainer and is written up in
knowledge/carousel/UPGRADE_BACKLOG.md (Codex, PR 379). Until then a water tower's name is the
director's to choose, and a banned word there is theirs to refuse.

render.py also keeps only the report's `text_window` characters of each string, 320 today, so a
word past that is unread. No string in the 35 shipped decks has reached it. One that does is a
finding, and the fix it names is splitting or shortening it. The backlog has the render.py fix.

Canvas text is also capped. render.py stops recording after 500 fillText and strokeText calls,
repeats included, and says nothing when it does, so a label drawn after a dense chart's 500th
tick goes unread. The report can't show the cap was hit, so nothing here can fail closed on it,
and the backlog has the render.py fix (Codex, PR 379).

SINCE is 2026-09-27, the last deck shipped before the rule. Nothing published on or before it is
judged as a failure, because published copy is not rewritten without the owner. shipped_check and
`--run` both still measure those decks and print what they find as notes.

EXIT CODES: 0 clean, or a deck on or before SINCE whatever it carries. 1 a banned word on a later
deck. 2 nothing to read.
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

# A straight-quoted passage may break across a line, never across a blank line, so one stray mark
# can't carry the exemption into the paragraphs after it, whatever the line ending (Codex, PR 379).
QUOTED = re.compile(r'"(?:[^"\n]|\n(?![ \t\r]*\n))*"')
URL = re.compile(r"https?://\S+|www\.\S+")
SENTENCE = re.compile(r"[^.!?\n]+[.!?]?")
# The claim fields that carry a source's own quotation. Its title fields are sources_block's
# TITLE_KEYS, the ones the first comment prints, so the two files can't disagree about a title.
QUOTE_FIELDS = ("quote", "verbatim_quote")
# Top-level copy.json strings a reader is shown. site_context.article_title reads the first two
# and carries `hook`, `subtitle` and `story` onto the deck's page record.
COPY_TOP_FIELDS = ("document_title", "title", "hook", "subtitle", "story")
# A passage at least this long found inside a source's own words is the source's.
CONTAINED_MIN_WORDS = 3
# Two nodes on one line closer than this, in ems, touch with no space between them. The narrowest
# space in assets/fonts is Instrument Serif's, 0.17 em.
ABUT_EM = 0.1


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


def _found_at(text: str, *, sources: tuple = (), quotes: tuple = (),
              banned: list | None = None) -> list:
    """(word, the words around it, offset) for each banned word in `text` the house wrote.

    `sources` are passages that are a source's own words wherever they appear, a title say.
    `quotes` are verbatim quotations. A sentence of CONTAINED_MIN_WORDS or more found inside
    either is the source's sentence, which covers a quotation or a title broken across lines.
    Both are matched on word boundaries, so "a pattern emerged" is not found inside "Data
    pattern emerged" and a source named "Data Gap" is not found inside "Metadata Gap" (Codex,
    PR 379)."""
    rx = matcher(banned if banned is not None else words())
    spans = [m.span() for m in QUOTED.finditer(text)] + [m.span() for m in URL.finditer(text)]
    low = text.lower()
    for s in sources:
        parts = s.lower().split()
        if not parts:
            continue
        # whitespace in the title matches any whitespace in the text, a line break included,
        # so a title set across two lines is still the source's (Codex, PR 379)
        title = r"\s+".join(re.escape(w) for w in parts)
        if all(rx.fullmatch(re.sub(r"^\W+|\W+$", "", w)) for w in parts):
            # a title that is nothing but banned words, "Gap" say, is the source's only where it
            # stands alone, a line or a comma-separated part of one, as the first comment prints
            # it. Anywhere else it is the house's word (Codex, PR 379)
            spans += [m.span(1) for m in re.finditer(
                rf"(?:^|(?<=[\n,]))[ \t]*({title})(?=[ \t]*(?:[,.\n]|$))", low)]
        elif len(" ".join(parts)) >= 4:
            spans += [m.span() for m in re.finditer(rf"(?<!\w){title}(?!\w)", low)]
    theirs = [_squash(q) for q in (*quotes, *sources) if q and q.strip()]
    out = []
    for m in rx.finditer(text):
        if any(a <= m.start() and m.end() <= b for a, b in spans):
            continue
        # a word is a token with a letter or digit in it, so "THE / PATTERN" is two (Codex, PR 379)
        if sum(1 for t in _passage(text, m.start(), theirs).split()
               if re.search(r"\w", t)) >= CONTAINED_MIN_WORDS:
            continue
        around = text[max(0, m.start() - 40):m.end() + 40].replace("\n", " ").strip()
        out.append((m.group(0), around, m.start()))
    return out


def _passage(text: str, at: int, theirs: list) -> str:
    """The longest run of sentences around offset `at`, on its line, that a source says
    verbatim, squashed, or "" when its own sentence isn't one. A full stop inside the run, as in
    "U.S. gap remains", doesn't cut a quotation short (Codex, PR 379)."""
    sents = list(SENTENCE.finditer(text))
    i = next((k for k, s in enumerate(sents) if s.start() <= at < s.end()), None)
    if i is None:
        return ""

    def said(lo, hi):
        return _squash(text[sents[lo].start():sents[hi].end()]).strip(" .!?")

    def theirs_has(lo, hi):
        return any(_bounded_in(said(lo, hi), q) for q in theirs)

    def joined(k):
        return "\n" not in text[sents[k].end():sents[k + 1].start()]

    if not theirs_has(i, i):
        return ""
    lo = hi = i
    while lo > 0 and joined(lo - 1) and theirs_has(lo - 1, hi):
        lo -= 1
    while hi + 1 < len(sents) and joined(hi) and theirs_has(lo, hi + 1):
        hi += 1
    return said(lo, hi)


def _found(text: str, *, sources: tuple = (), quotes: tuple = (),
           banned: list | None = None) -> list:
    """(word, the words around it) for each banned word in `text` the house wrote."""
    return [(w, a) for w, a, _ in _found_at(text, sources=sources, quotes=quotes, banned=banned)]


def _say(word: str, around: str) -> str:
    return f"{word!r} in \"...{around}...\""


def hits(text: str, *, sources: tuple = (), quotes: tuple = (), banned: list | None = None) -> list:
    """Each banned word in `text` that the house wrote, with the words around it. See `_found`."""
    return [_say(w, a) for w, a in _found(text, sources=sources, quotes=quotes, banned=banned)]


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


def claim_rows(path: Path) -> list:
    """The claims in a claims.json, in either shape a run writes."""
    raw = _load(Path(path))
    rows = raw.get("claims") if isinstance(raw, dict) else raw
    return [c for c in rows or [] if isinstance(c, dict)]


def _claim_rows(d: Path) -> list:
    return claim_rows(d / "claims.json")


def claim_words(c: dict) -> tuple:
    """(sources, quotes) one claim carries: its source's title, publisher, attribution and
    verbatim quotation. The title fields are sources_block's, so a claim whose only title is a
    publisher such as Pattern Energy keeps it, as the first comment prints it (Codex, PR 379)."""
    import sources_block  # TITLE_KEYS, the title fields the first comment prints

    def got(fields):
        return tuple(str(c[f]) for f in fields if isinstance(c.get(f), str) and c[f].strip())
    return got((*sources_block.TITLE_KEYS, "attribution")), got(QUOTE_FIELDS)


def evidence_of(rows) -> tuple:
    """(sources, quotes) across `rows`, for a surface that cites none of them in particular."""
    sources, quotes = [], []
    for c in rows:
        s, q = claim_words(c)
        sources += s
        quotes += q
    return tuple(sources), tuple(quotes)


def _source_words(d: Path) -> tuple:
    return evidence_of(_claim_rows(d))


def article_text(article: dict) -> list:
    """(where, text, claim ids) for every reader-facing string of a web edition, per
    ledger/articles/README. A block's ids are the claims it cites. The section, which prints in
    the page's kicker, a heading and a related label cite none. The claim sentences the page's
    verification block prints come from the run's claims.json, and `check` reads them there."""
    out = []
    section = article.get("section")
    if isinstance(section, str):
        out.append(("section", section, ()))
    dek = article.get("dek")
    if isinstance(dek, dict):
        out.append(("dek", str(dek.get("text") or ""), dek.get("claims") or ()))
    for i, p in enumerate(article.get("introduction") or []):
        if isinstance(p, dict):
            out.append((f"introduction[{i}]", str(p.get("text") or ""), p.get("claims") or ()))
    for i, sec in enumerate(article.get("sections") or []):
        if not isinstance(sec, dict):
            continue
        out.append((f"sections[{i}].heading", str(sec.get("heading") or ""), ()))
        for j, p in enumerate(sec.get("paragraphs") or []):
            if isinstance(p, dict):
                out.append((f"sections[{i}].paragraphs[{j}]", str(p.get("text") or ""),
                            p.get("claims") or ()))
    for i, r in enumerate(article.get("related") or []):
        if isinstance(r, dict):
            out.append((f"related[{i}].label", str(r.get("label") or ""), ()))
    return out


def _bounded_in(needle: str, hay: str) -> bool:
    """`needle` inside `hay` on word boundaries, so "the gap" is not found in "the gaping"."""
    return bool(needle) and re.search(rf"(?<!\w){re.escape(needle)}(?!\w)", hay) is not None


def _text_lines(nodes: list) -> list:
    """The visual lines of a slide's recorded DOM text, each {"text", "parts", "x0", "right",
    "top", "bottom"}, where a part is (start, end, node text).

    render.py records an element that has text of its own, with its whole flattened text and the
    indices of its recorded ancestors in `anc`. A node an ancestor already holds is read there,
    in context, and skipped here. The outermost nodes that sit side by side on one line are read
    together, which is how a name set in two styled spans arrives as the one name it is (Codex,
    PR 379). A report without `anc` finds ancestors by box instead, and a node without a box is
    read alone."""
    def box(t):
        return tuple(float(t.get(k) or 0) for k in ("x", "y", "w", "h"))

    def inside(a, b):
        ax, ay, aw, ah = box(a)
        bx, by, bw, bh = box(b)
        return aw > 0 and bw > 0 and bx <= ax and by <= ay and ax + aw <= bx + bw \
            and ay + ah <= by + bh

    tops = []
    for i, t in enumerate(nodes):
        text = " ".join(str(t.get("text") or "").split())
        if not text:
            continue
        if "anc" in t:
            above = [nodes[a] for a in t.get("anc") or []
                     if isinstance(a, int) and 0 <= a < len(nodes)]
        else:
            above = [u for j, u in enumerate(nodes) if j != i and inside(t, u)]
        if any(_bounded_in(_squash(text), _squash(str(u.get("text") or ""))) for u in above):
            continue
        tops.append((text, t))
    lines = []
    for text, t in sorted(tops, key=lambda pair: box(pair[1])[0]):
        x, y, w, h = box(t)
        fs = float(t.get("font_px") or 0) or h
        for ln in lines:
            if (w > 0 and h > 0 and ln["h"] > 0
                    and abs(y + h / 2 - ln["cy"]) <= 0.5 * max(h, ln["h"])
                    and -2 <= x - ln["right"] <= 1.2 * max(fs, ln["fs"])):
                if x - ln["right"] < ABUT_EM * max(fs, ln["fs"]):
                    ln["touch"].append(len(ln["text"]))
                start = len(ln["text"]) + 1
                ln["text"] += " " + text
                ln["parts"].append((start, start + len(text), text))
                ln["right"], ln["fs"] = x + w, max(fs, ln["fs"])
                ln["top"], ln["bottom"] = min(ln["top"], y), max(ln["bottom"], y + h)
                break
        else:
            lines.append({"text": text, "parts": [(0, len(text), text)], "x0": x, "right": x + w,
                          "top": y, "bottom": y + h, "cy": y + h / 2, "h": h, "fs": fs,
                          "touch": []})
    return lines


def _text_blocks(nodes: list) -> list:
    """[(text, parts, touch)], one per block of lines stacked in one column, joined by line breaks.

    A name whose two styled spans stack or wrap onto the next line is still one name, so a line
    that starts just under the one above it, overlapping it across, joins that line's block
    (Codex, PR 379). Just under includes a little above its bottom edge, because a box is as
    tall as its line height and lines set closer than that overlap by up to half a line. A
    line break lets a source's title and a straight-quoted passage run on, as `_found_at` reads
    them, and it still ends a sentence, so the three word rule for a quotation stays a rule
    about one line. Columns never join, because they don't overlap."""
    blocks = []
    for ln in sorted(_text_lines(nodes), key=lambda l: (l["top"], l["x0"])):
        h = ln["bottom"] - ln["top"]
        for b in blocks:
            last = b["last"]
            gap = ln["top"] - last["bottom"]
            lh = last["bottom"] - last["top"]
            if (h > 0 and lh > 0
                    and -0.5 * min(h, lh) <= gap <= 0.8 * max(h, lh)
                    and ln["x0"] < last["right"] and ln["right"] > last["x0"]):
                start = len(b["text"]) + 1
                b["text"] += "\n" + ln["text"]
                b["parts"] += [(start + a, start + e, pt) for a, e, pt in ln["parts"]]
                b["touch"] += [start + t for t in ln["touch"]]
                b["last"] = ln
                break
        else:
            blocks.append({"text": ln["text"], "parts": list(ln["parts"]),
                           "touch": list(ln["touch"]), "last": ln})
    return [(b["text"], b["parts"], b["touch"]) for b in blocks]


CSS_CONTENT = re.compile(r"(?<![\w-])content\s*:\s*([^;}]*)")
CSS_STRING = re.compile(r'"((?:\\.|[^"\\])*)"|\'((?:\\.|[^\'\\])*)\'')


def css_content(html: str) -> list:
    """Each string a stylesheet's `content` property prints, adjacent strings joined as CSS joins
    them. A ::before or ::after label never reaches render.py's report, so it is read from the
    slide's own HTML (Codex, PR 379)."""
    out = []
    for m in CSS_CONTENT.finditer(html):
        joined = "".join(a or b for a, b in CSS_STRING.findall(m.group(1)))
        if joined.strip():
            out.append(joined)
    return out


def rendered(d: Path, judged: dict, evidence, banned: list | None = None) -> list:
    """(where, word, around) for each banned word the committed render report says a slide
    printed: a label set straight into the HTML, furniture the design marked decorative, a
    canvas's drawn text. Decorative text is printed text, and the ban grants furniture nothing.

    DOM text is read a line at a time, see `_text_lines`, and canvas text a call at a time.
    `judged` maps a slide number to [(squashed text, {words it was flagged for})] for that
    slide's authored strings, and `evidence(n)` is the (sources, quotes) slide n cites. A word
    found in a rendered string that one of its own slide's judged strings holds, and was already
    flagged for, adds nothing. Held where the word was exempt, it is judged on its own words, so
    the label "THE GAP" beside a quotation of the gap is the house's (Codex, PR 379)."""
    rep = next((r for r in (_load(d / "render_report.json"),
                            _load(d / "render" / "render_report.json")) if isinstance(r, dict)),
               None)
    if rep is None:
        return []
    window = rep.get("text_window") or 0
    out = []
    for i, rec in enumerate(rep.get("slides") or [], start=1):
        if not isinstance(rec, dict):
            continue
        m = re.search(r"(\d+)", str(rec.get("file") or ""))
        n = rec.get("n") or (int(m.group(1)) if m else i)
        sources, quotes = evidence(n)
        nodes = [t for t in rec.get("text_nodes") or [] if isinstance(t, dict)]
        units = _text_blocks(nodes)
        drawn = dict.fromkeys(str(t.get("text") or "") for t in rec.get("canvas_text") or []
                              if isinstance(t, dict))
        units += [(c, [(0, len(c), c)], []) for c in drawn if c.strip()]
        page = d / "slides" / Path(str(rec.get("file") or "")).name
        if rec.get("file") and page.is_file():
            units += [(c, [(0, len(c), c)], [])
                      for c in dict.fromkeys(css_content(page.read_text(encoding="utf-8")))]
        # render.py keeps TEXT_WINDOW characters of each string, and a banned word past that is
        # a word no gate can read. None of 3,136 nodes in 35 decks has reached it, so the gate
        # fails closed on one rather than passing what it can't see (Codex, PR 379). The length
        # is the string as recorded. A DOM string is collapsed before it is cut, so a cut just
        # after a space keeps the space, and a canvas string is cut raw, so collapsing either
        # again would measure a cut string short of the window.
        for cut in [str(t.get("text") or "") for t in nodes] + list(drawn):
            if window and len(cut) >= window:
                out.append((f"rendered slide {n}", None, cut[:60]))
        own, seen = judged.get(n, []), set()
        for text, parts, touch in units:
            if _squash(text) in seen:
                continue
            seen.add(_squash(text))
            found = _found_at(text, sources=sources, quotes=quotes, banned=banned)
            if touch:
                # Two nodes that touch may be one word in two styles, "PAT" and "TERN". The spaced
                # reading above keeps each node's own words, and this one adds a word only where
                # it runs across a join, since a node's box can hold a trailing space the report
                # trims (Codex, PR 379)
                tight, cuts, prev = "", [], 0
                for t in touch:
                    tight += text[prev:t]
                    cuts.append(len(tight))
                    prev = t + 1
                tight += text[prev:]
                found += [f for f in _found_at(tight, sources=sources, quotes=quotes,
                                               banned=banned)
                          if any(f[2] < c < f[2] + len(f[0]) for c in cuts)]
            for w, around, at in found:
                part = next((pt for a, b, pt in parts if a <= at < b), text)
                if not any(w.lower() in flagged and _bounded_in(_squash(part), other)
                           for other, flagged in own):
                    out.append((f"rendered slide {n}", w, around))
    return out


def check(d: Path, banned: list | None = None, articles: Path = ARTICLES) -> list | None:
    """Every banned word on a run's published surfaces. None when the run has no copy to read.

    A QUOTATION IS THE SOURCE'S ONLY WHERE THE SURFACE CITES THAT SOURCE (Codex, PR 379). A slide
    and a web edition block each name the claims they rest on, and only those claims' quotes and
    titles can exempt their words. A surface that cites nothing, the caption, the first comment,
    a heading, is measured against every claim the run carries."""
    copy = _load(d / "copy.json")
    if copy is None:
        return None
    import copy_sync_check  # the machinery keys, the slide shapes and the claim ids a slide cites
    banned = banned if banned is not None else words()
    rows = _claim_rows(d)
    by_id = {str(c.get("id")): c for c in rows}
    everything = _source_words(d)

    def cited(ids) -> tuple:
        own = [claim_words(by_id[str(i)]) for i in ids or () if str(i) in by_id]
        if not own:
            return everything
        return (tuple(x for s, _ in own for x in s), tuple(x for _, q in own for x in q))

    out = []

    def judge(where, text, evidence=everything):
        found = _found(text, sources=evidence[0], quotes=evidence[1], banned=banned)
        out.extend((where, w, a) for w, a in found)
        return found

    caption = d / "caption.txt"
    judge("caption", caption.read_text(encoding="utf-8") if caption.exists()
          else str(copy.get("caption") or ""))
    for key in COPY_TOP_FIELDS:
        value = copy.get(key)
        if isinstance(value, str) and value.strip():
            judge(key.replace("_", " "), value)
    comment = d / "first_comment.txt"
    if comment.exists():
        judge("first comment", comment.read_text(encoding="utf-8"))
    judged, slide_evidence = {}, {}
    for key, slide in copy_sync_check.normalize_slides(copy.get("slides")).items():
        n = copy_sync_check.slide_no(key)
        evidence = slide_evidence[n] = cited(copy_sync_check.claim_ids_in(slide))
        for where, text in _strings(slide, f"slides.{key}", copy_sync_check.META_KEYS):
            flagged = {w.lower() for w, _ in judge(where, text, evidence)}
            judged.setdefault(n, []).append((_squash(text), flagged))
    out.extend(rendered(d, judged, lambda n: slide_evidence.get(n, everything), banned=banned))
    # A claim's sentence is printed beside its own evidence, so only that claim's own title and
    # quotation can make the sentence the source's.
    for c in rows:
        judge(f"claim {c.get('id', '?')}", str(c.get("text") or ""), claim_words(c))
    article = _load(articles / f"{d.name}.json")
    if isinstance(article, dict):
        for where, text, ids in article_text(article):
            judge(f"web edition {where}", text, cited(ids))
    return [f"{where}: {_say(w, a)}. The owner banned it on 2026-09-27 (config/brand.yaml "
            f"banned_words). Say the specific thing instead" if w is not None else
            f"{where}: \"{a}...\" runs past the characters the render report keeps, so the "
            f"owner's banned words can't be read in the rest of it. Split it across two "
            f"elements or shorten it" for where, w, a in out]


def exit_code(run_date: str, found: list) -> int:
    """1 for a banned word on a deck dated after SINCE. A deck on or before it shipped before the
    rule, so what it finds is a note and the answer is 0, as shipped_check reads the same deck
    (Codex, PR 379)."""
    return 1 if found and run_date > SINCE else 0


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
    ok("...so the house's 'A pattern emerged.' is not inside a source's 'Data pattern emerged' "
       "(Codex, PR 379)",
       len(hits("A pattern emerged.", quotes=("Data pattern emerged in the report.",),
                banned=banned)) == 1)
    ok("...and a source named Data Gap is not found inside the house's 'Metadata Gap'",
       len(hits("The Metadata Gap report.", sources=("Data Gap",), banned=banned)) == 1)
    ok("a source's title set across a line break is still the source's (Codex, PR 379)",
       not hits("Pattern\nEnergy filed the request.", sources=("Pattern Energy",),
                banned=banned))
    ok("a source named only a banned word keeps it where it stands alone, as the first comment "
       "prints it, and nowhere else (Codex, PR 379)",
       not hits("Gap, September 3rd. c1\nGap. c2\nSOURCES\nGAP", sources=("Gap",), banned=banned)
       and len(hits("Mind the gap, the council said.", sources=("Gap",), banned=banned)) == 1
       and len(hits("The matters before council.", sources=("Matters",), banned=banned)) == 1)
    ok("a full stop inside a quotation doesn't cut it short, so 'U.S. gap remains' is the "
       "source's (Codex, PR 379)",
       not hits("U.S. gap remains", quotes=("U.S. gap remains",), banned=banned)
       and len(hits("U.S. gap remains", banned=banned)) == 1)
    ok("a quotation broken across a line keeps its words (Codex, PR 379)",
       not hits('The memo says "a pattern\nof late filings" twice.', banned=banned))
    ok("...but a stray mark never carries the exemption past a blank line, CRLF included",
       len(hits('A stray " mark.\n\nThe gap is ours. "Quoted."', banned=banned)) == 1
       and len(hits('A stray " mark.\r\n\r\nThe gap is ours. "Quoted."', banned=banned)) == 1)
    ok("a lone punctuation mark is not a word, so 'THE / PATTERN' stays a two word label "
       "(Codex, PR 379)",
       len(hits("THE / PATTERN", quotes=("the / pattern of filings",), banned=banned)) == 1)
    ok("a CSS content string is read, adjacent strings joined, and align-content is not one",
       css_content('<style>.k::before{content:"THE " \'PATTERN\'} .r{align-content:center}'
                   '.q::after{content: "\\201C"}</style>') == ["THE PATTERN", "\\201C"])
    ok("--run fails a deck dated after the rule and notes one on or before it (Codex, PR 379)",
       exit_code("2026-09-28", ["x"]) == 1 and exit_code("2026-09-27", ["x"]) == 0
       and exit_code("2026-09-28", []) == 0)

    with tempfile.TemporaryDirectory() as t:
        d, arts = Path(t) / "2026-09-28", Path(t) / "articles"
        d.mkdir()
        arts.mkdir()
        (d / "claims.json").write_text(json.dumps({"claims": [
            {"id": "c1", "source_title": title, "quote": quote,
             "text": "Council staff describe a pattern of incomplete filings."},
            {"id": "c2", "quote": quote,
             "text": "Staff identified a pattern of incomplete applications."},
            {"id": "c3", "source_publisher": "Pattern Energy", "quote": "The farm is online.",
             "text": "The wind farm is online."},
            {"id": "c4", "quote": "The vote was nine to two.", "text": quote}]}))
        (d / "copy.json").write_text(json.dumps({
            "caption": "", "document_title": "Why it matters", "slides": {
                "S1": {"headline": "Four filings, one pattern", "claims": ["c1"],
                       "notes": "planning residue about the gap, never rendered"},
                "S2": {"body": 'The memo says "the gap is widening."', "claims": ["c3"]},
                "S3": {"body": quote, "claims": ["c1"]},
                "S4": {"body": quote, "claims": ["c3"]},
                "S5": {"body": "The request went in on Monday.", "claims": ["c3"]},
                "S6": {"body": "The request went in on Tuesday.", "claims": ["c3"]}}}))
        (d / "render_report.json").write_text(json.dumps({"text_window": 320, "slides": [
            {"file": "slide-01.html",
             "text_nodes": [{"text": "Four filings, one pattern", "decorative": False},
                            {"text": "one pattern", "decorative": False},
                            {"text": "THE GAP", "decorative": False},
                            {"text": "The gap", "decorative": False},
                            {"text": "texasaidocket.com", "decorative": True}],
             "canvas_text": [{"text": "identified a pattern of incomplete", "fn": "fillText"}]},
            {"file": "slide-02.html",
             "text_nodes": [{"text": 'The memo says "the gap is widening."', "decorative": False},
                            {"text": "THE GAP", "decorative": False}],
             "canvas_text": [{"text": "identified a pattern of incomplete", "fn": "fillText"}]},
            {"file": "slide-03.html",
             "text_nodes": [{"text": "THE PATTERN", "decorative": True}],
             "canvas_text": [{"text": "Here is why it matters", "fn": "fillText"}]},
            # A publisher's name set in two spans, the same name inside a recorded parent, and a
            # house label elsewhere on the frame. Slide 5 cites c3, Pattern Energy's claim, and
            # its own copy flags nothing, so no authored string can stand in for these nodes.
            {"file": "slide-05.html", "text_nodes": [
                {"text": "Pattern", "x": 100, "y": 1000, "w": 120, "h": 30, "font_px": 28,
                 "anc": []},
                {"text": "Energy", "x": 232, "y": 1000, "w": 110, "h": 30, "font_px": 28,
                 "anc": []},
                {"text": "Pattern Energy filed the request.", "x": 100, "y": 1100, "w": 600,
                 "h": 30, "font_px": 28, "anc": []},
                {"text": "Pattern", "x": 100, "y": 1100, "w": 120, "h": 30, "font_px": 28,
                 "anc": [2]},
                {"text": "THE PATTERN", "x": 700, "y": 200, "w": 200, "h": 40, "font_px": 36,
                 "anc": []}]},
            # The same name in two spans stacked in one column, again set closer than its line
            # height so the two boxes overlap, and a label in the last column.
            {"file": "slide-06.html", "text_nodes": [
                {"text": "Pattern", "x": 100, "y": 500, "w": 140, "h": 40, "font_px": 36,
                 "anc": []},
                {"text": "Energy", "x": 100, "y": 545, "w": 140, "h": 40, "font_px": 36,
                 "anc": []},
                {"text": "Pattern", "x": 400, "y": 500, "w": 140, "h": 43, "font_px": 36,
                 "anc": []},
                {"text": "Energy", "x": 400, "y": 532, "w": 140, "h": 43, "font_px": 36,
                 "anc": []},
                {"text": "THE PATTERN", "x": 700, "y": 500, "w": 240, "h": 40, "font_px": 36,
                 "anc": []}]},
            # One word set in two touching spans, a label whose box holds its trailing space,
            # and two words a real space apart.
            {"file": "slide-08.html", "text_nodes": [
                {"text": "PAT", "x": 100, "y": 300, "w": 60, "h": 40, "font_px": 36, "anc": []},
                {"text": "TERN", "x": 160, "y": 300, "w": 80, "h": 40, "font_px": 36, "anc": []},
                {"text": "THE GAP", "x": 100, "y": 700, "w": 150, "h": 40, "font_px": 36,
                 "anc": []},
                {"text": "IS CLEAR", "x": 250, "y": 700, "w": 150, "h": 40, "font_px": 36,
                 "anc": []},
                {"text": "GA", "x": 100, "y": 1000, "w": 50, "h": 40, "font_px": 36, "anc": []},
                {"text": "P PLAN", "x": 160, "y": 1000, "w": 120, "h": 40, "font_px": 36,
                 "anc": []}]},
            # A clean string cut at the report's window, the same cut landing just after a space,
            # which render.py keeps, a canvas string cut raw with a double space in it, and one a
            # character short of the window.
            {"file": "slide-07.html", "text_nodes": [
                {"text": ("Nine days apart. " * 19)[:320], "anc": []},
                {"text": ("Ten days apart. " * 21)[:320], "anc": []},
                {"text": ("Ten days apart. " * 20)[:319], "anc": []}],
             "canvas_text": [{"text": ("Two  spaces here. " * 30)[:320], "fn": "fillText"}]}]}))
        (d / "slides").mkdir()
        (d / "slides" / "slide-08.html").write_text(
            '<style>.k::before{content:"THE " "PATTERN"} .r{align-content:center}</style>')
        (d / "caption.txt").write_text("The council voted. Here is why it matters.\n")
        (d / "first_comment.txt").write_text(
            f"Sources.\n{title}, KGNS.\nPattern Energy, September 20th.\nhttps://example.com/gap\n")
        (arts / "2026-09-28.json").write_text(json.dumps({
            "section": "Pattern watch",
            "dek": {"text": "The gap in the calendar.", "claims": ["c1"]},
            "introduction": [{"text": quote, "claims": ["c1"]}],
            "sections": [{"heading": "What changed",
                          "paragraphs": [{"text": quote, "claims": ["c3"]}]}],
            "related": [{"id": "tx-1", "label": "The record"}]}))
        found = check(d, banned, arts)
        where = {}
        for f in found:
            where[f.split(": ", 1)[0]] = where.get(f.split(": ", 1)[0], 0) + 1
        ok("every surface is read, each word reported once, and nothing exempt is reported. "
           "Slide 1's label, slide 2's label beside a quotation of it, slide 3's decorative "
           "label and canvas line, and claim c4 quoting c1's evidence as its own are caught. "
           "A source title, a publisher, a URL, planning notes, clean furniture, a line of a "
           "quote, a quotation and claim c2's own evidence are not. c1's quote exempts a slide "
           "and a paragraph that cite c1, and not slide 4, a canvas line on slide 2 or a "
           "paragraph that cite c3. On slide 5 a publisher's name split across two spans and "
           "a span inside its parent keep their words, and the label beside them does not. On "
           "slide 6 the name stacked in one column keeps its words, set loose or with its boxes "
           "overlapping, and the last column's label does not. On slide 7 a string cut at the "
           "report's window fails closed, a cut just after a space and a canvas string with a "
           "double space included, and one a character short of it passes. On slide 8 a word "
           "set in two touching spans, a label beside touching text and a ::before label its CSS "
           "prints are caught, and two words a space apart are not joined (Codex, PR 379)",
           where == {"caption": 1, "document title": 1, "slides.S1.headline": 1,
                     "slides.S4.body": 1, "rendered slide 1": 1, "rendered slide 2": 2,
                     "rendered slide 3": 2, "rendered slide 5": 1, "rendered slide 6": 1,
                     "rendered slide 7": 3, "rendered slide 8": 3, "claim c1": 1, "claim c4": 1,
                     "web edition section": 1, "web edition dek": 1,
                     "web edition sections[0].paragraphs[0]": 1}, "\n".join(found))
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
    before = not exit_code(a.run, ["a deck dated after the rule"])
    for f in found:
        print(f"word_ban: {'note, ' if before else ''}{f}")
    print(f"word_ban: {len(found)} banned word(s) on {a.run}'s published surfaces"
          + (f", each a note because the deck shipped on or before {SINCE}"
             if before and found else ""))
    return exit_code(a.run, found)


if __name__ == "__main__":
    sys.exit(main())
