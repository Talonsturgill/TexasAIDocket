#!/usr/bin/env python3
"""A quantifier is a claim about a set, and this deck's sets are measurements.

THE DEFECT THIS EXISTS FOR, twice in two rounds.

2026-08-25 round 13 hard failed frame 3 for printing "Nothing in their sources says the action
binds". The bucket that sentence describes, `force_unstated`, is a MEASUREMENT: acting items that
carry no `effective` key date at all. It is not a claim about what sources say, and c44 in the
same run's claims file is a source saying which way for Wichita Falls, on a fact frame 8 of the
same deck prints.

The frame was repaired. Round 14 hard failed the run again, twice, for the SAME sentence on frame
6's foot and in the caption. Both judges' one sentence fix was the same: every repair in this loop
lands on the frame that was named and on no other surface.

So this gate reads EVERY PUBLISHED SURFACE AT ONCE, from one list, and the list is the point.

  1. SOURCE SILENCE is banned outright on any published surface. This product's buckets are
     measurements about the record's key dates, and it has hard failed twice for dressing one as a
     claim about what sources say. A run that genuinely needs to say the sources are silent has to
     prove it claim by claim, and that proof does not fit on a slide. Print the measurement.

  2. A UNIVERSAL over a set noun ("every step", "all items", "not one of them") must name the
     figures.json key it ranges over, in out/<date>/quantifiers.json, and every id in that key's
     `from_items` is then checked against claims.json: if a claim speaks to one of them and the
     sentence says nothing does, the gate fails with the claim id in hand.

  3. THE LEDGER'S first_line MUST BE THE SHIPPED FIRST LINE. It is stored verbatim so the next
     run's caption critic can catch a sentence skeleton, so a stale one disarms the only gate it
     feeds. Round 14 found it holding the pre-repair wording.

  4. AN EXCLUSIVE COUNT OVER A DOCUMENT ("in one sentence", "only once") is a universal over that
     document's sentences, and it is re-derived by sweeping the fetched text. Added 2026-09-24,
     see EXCLUSIVE below.

THE WEB EDITION IS A PUBLISHED SURFACE, AND UNTIL 2026-09-24 THIS GATE DID NOT READ IT.

The paragraph above says every published surface, from one list. The list held the frames, the
caption and the first comment. `ledger/articles/<date>.json` is rendered at `/articles/<date>/`
and it was not on it, so the one surface written in long prose, where a universal is easiest to
slip in, was the one this gate never read. Measured that day over the committed editions:
"Neither document announces a completed enforcement action" (2026-09-19) and "none of them
contains another" (2026-09-21) are prose universals no gate had looked at, and the same words on
a frame would have had to name their set. Carousel no. 33's round 2 integrity judge then hard
failed the edition for "A person enters in one sentence", which the fetched draft refutes in seven
other sentences. GATE_LESSONS 79 is this shape: the rule had a gate, pointed at one surface.

The edition's `[words](cNN)` spans are stripped before judging, exactly as `article_check` strips
them for house style, because they are the claim's own words and a universal a source wrote is
the source's claim, carried by its id. What is judged is the prose a run wrote around them.

Run it by EXIT CODE. 0 clean, 1 a quantifier the record does not support, 2 could not run.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# THE CAPTION LEDGER IS A DEFAULT RATHER THAN A CALLER'S RESPONSIBILITY, and it was the second
# on 2026-09-03. `check(run, ledger=None)` meant a caller that forgot the second argument got a
# gate with its first-line test silently switched off, and `shipped_check` forgot it, so the
# sweep across every published deck ran two thirds of this gate and reported the whole of it
# clean. The CLI passed `Path("ledger/carousel/captions.json")`, relative to the working
# directory, which is its own way to reach the same wrong answer from a different directory.
#
# So the path is anchored to the repo and it is the default. A caller that wants the ledger out
# of the picture, which is the self-test and nothing else, passes `ledger=None` and says so.
CAPTIONS_LEDGER = REPO_ROOT / "ledger" / "carousel" / "captions.json"
_UNSET = object()

# Sentences asserting what sources do or do not say about a set. Each of these shipped.
SOURCE_SILENCE = [
    (re.compile(r"\bno sources?\b", re.I), "no source"),
    (re.compile(r"\bnothing in [^.]{0,30}\bsources?\b", re.I), "nothing in their sources"),
    (re.compile(r"\bsources?\s+(?:say|says|said)\s+(?:nothing|neither|either way)\b", re.I),
     "sources say neither"),
    (re.compile(r"\bsources?\s+(?:are\s+)?silent\b", re.I), "sources silent"),
    (re.compile(r"\bthe sources leave\b", re.I), "the sources leave"),
    (re.compile(r"\bsays? either way\b", re.I), "says either way"),
]
# A universal quantifier standing next to a set noun.
UNIVERSAL = re.compile(
    r"\b(every|all|neither|none|not one|no other|every other)\b[^.;]{0,44}?"
    r"\b(step|steps|item|items|action|actions|record|records|source|sources|door|doors|"
    r"body|bodies|them|these|five|fifteen|seventeen)\b", re.I)


# THE EXCLUSIVE COUNT, added 2026-09-24 on carousel no. 33's round 2 hard fail.
#
#     "A person enters in one sentence."
#
# That is `ledger/articles/2026-09-24.json` as committed in 3dcc68ea. It says the draft names a
# person in ONE sentence and in no other, which is a universal negative over every sentence of a
# 403,014 character document. The run's fact check had established something narrower, that the
# operator sentence is absent from one section, and the edition widened it. Swept with `sweep()`
# below, the fetched draft names an operator in five sentences and a Remote Pilot in Command in
# three, eight in all.
#
# None of the gates above could see it. It carries no set noun for UNIVERSAL, no source word for
# SOURCE_SILENCE, and `aggregate_check` sets a count of one aside as the pronoun on purpose. It is
# still a figure, "one", printed about a document, and the law is that a published figure is
# recomputed from committed inputs. So the declaration for one of these is a SWEEP, and this gate
# runs it: the fetched text, the terms swept for, and the number of sentences that name them.
#
# Only forms that assert exactly ONE are matched, so the asserted count is never parsed out of
# prose. Measured once, 2026-09-24, over every frame, caption, first comment and web edition of
# the shipped corpus: 3,537 strings and zero matches, so this adds no finding to work that has
# already shipped. The one match anywhere in the repository's history is the defect.
EXCLUSIVE = re.compile(
    r"\b(?:in|by)\s+(?:one|a single|only one|just one|exactly one)\s+(?:sentence|passage|place)\b"
    r"|\b(?:only|just)\s+once\b"
    r"|\b(?:appears?|occurs?|is named|is mentioned)\s+once\b", re.I)

ARTICLES = REPO_ROOT / "ledger" / "articles"
# A claim's own words, and the template tokens an edition fills in at build. Same two patterns
# `scripts/site/article_check.py` strips before it judges the edition's prose.
_SPAN = re.compile(r"\[([^\]]+)\]\(c\d+\)")
_TOKEN = re.compile(r"\{\{[^}]*\}\}")


class EditionUnreadable(RuntimeError):
    """A web edition exists and could not be read. Never an edition with nothing in it."""


def _edition_prose(node, path: str = "edition"):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "_spec":
                continue
            yield from _edition_prose(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from _edition_prose(value, f"{path}[{i}]")
    elif isinstance(node, str) and not (path.endswith(".id") or ".claims" in path):
        yield path, _SPAN.sub(" ", _TOKEN.sub(" ", node))


def web_edition(run: Path, articles: Path | None = None) -> list:
    """The run's web edition, as (where, prose) pairs. Empty when the run has none."""
    p = (ARTICLES if articles is None else Path(articles)) / f"{run.name}.json"
    if not p.exists():
        return []
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise EditionUnreadable(f"{p} exists and could not be read: {exc}") from exc
    return [(f"web edition {p.name} {path}", text) for path, text in _edition_prose(doc)]


def sweep(text: str, terms: list) -> list:
    """The sentences of a fetched text that name any of the terms, plural forms included."""
    flat = re.sub(r"\s+", " ", text)
    sents = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[])", flat)
    rx = re.compile(r"\b(?:" + "|".join(re.escape(str(t)) for t in terms) + r")(?:s|es)?\b", re.I)
    return [s for s in sents if rx.search(s)]


def exclusive_problem(where: str, phrase: str, d: dict | None) -> str | None:
    """Why a declared exclusive count does not re-derive, or None when it does."""
    head = f"{where} prints the exclusive count {phrase!r}"
    if d is None:
        return (f"{head} and quantifiers.json declares nothing for it. It says a document names "
                f"something in ONE place and no other, which is a universal over every sentence "
                f"of that document. Sweep the fetched text for the noun first, then declare "
                f"`swept: {{text, terms, sentences}}`, or say what the fact check established")
    sw = d.get("swept")
    if not isinstance(sw, dict) or not sw.get("terms") or not sw.get("text"):
        return (f"{head} and its declaration carries no `swept` block naming the fetched `text` "
                f"and the `terms` swept for. An exclusive count is re-derived, never asserted")
    if sw.get("sentences") != 1:
        return (f"{head}, which asserts one, and its sweep declares {sw.get('sentences')!r}")
    tp = Path(sw["text"])
    tp = tp if tp.is_absolute() else REPO_ROOT / tp
    if not tp.exists():
        return (f"{head} and the swept text {sw['text']} is not there, so the count can't be "
                f"re-derived. A published figure is recomputed from committed inputs, so archive "
                f"the fetched text with the run rather than pointing at scratch")
    found = sweep(tp.read_text(encoding="utf-8", errors="replace"), list(sw["terms"]))
    if len(found) != 1:
        shown = "; ".join(repr(s[:90]) for s in found[:3])
        return (f"{head} and {len(found)} sentences of {sw['text']} name "
                f"{', '.join(map(str, sw['terms']))}. First: {shown}")
    return None


def surfaces(run: Path, articles: Path | None = None) -> list:
    """EVERY published surface, from ONE list. Three callers have kept their own before."""
    out = []
    # BOTH LAYOUTS. A live run writes `render/render_report.json` under its scratch directory and
    # `ship_images` archives the same file at the RUN ROOT. This looked only under `render/`, so
    # against every shipped deck it read `caption.txt` and `first_comment.txt` and NO SLIDE TEXT
    # AT ALL. Measured on 2026-09-03: two published frames carried findings this gate exists to
    # catch, a banned source silence claim and an undeclared universal, and its receipt said two
    # surfaces checked and clean. A gate reading two files out of eleven is the "wired to nothing"
    # shape this project keeps finding, and this one was reporting a pass while doing it.
    rep = run / "render/render_report.json"
    if not rep.exists():
        rep = run / "render_report.json"
    if rep.exists():
        for sl in (json.loads(rep.read_text()).get("slides") or []):
            for n in (sl.get("text_nodes") or []):
                out.append((sl.get("file", "?"), n.get("text", "")))
    for name in ("caption.txt", "first_comment.txt"):
        f = run / name
        if f.exists():
            out.append((name, f.read_text(encoding="utf-8")))
    out.extend(web_edition(run, articles))
    return out


def check(run: Path, ledger=_UNSET, articles: Path | None = None) -> list:
    if ledger is _UNSET:
        ledger = CAPTIONS_LEDGER
    problems = []
    try:
        surf = surfaces(run, articles)
    except EditionUnreadable as exc:
        return [f"quantifier_check could not read the web edition, so the one surface written "
                f"in long prose was not checked at all: {exc}"]
    figs = {}
    fp = run / "figures.json"
    if fp.exists():
        figs = json.loads(fp.read_text())
    claims = []
    cp = run / "claims.json"
    if cp.exists():
        claims = json.loads(cp.read_text())["claims"]
    if not surf:
        return ["quantifier_check found no published surface, so it checked nothing"]

    for where, text in surf:
        flat = re.sub(r"\s+", " ", text)
        for rx, label in SOURCE_SILENCE:
            m = rx.search(flat)
            if not m:
                continue
            problems.append(
                f"{where} asserts SOURCE SILENCE: {label!r} in "
                f"{flat[max(0, m.start() - 40):m.end() + 40].strip()!r}. This deck's buckets are "
                f"measurements about the record's key dates, not claims about what sources say, "
                f"and this exact construction hard failed rounds 13 and 14. Print the "
                f"measurement, for example that the record carries no date the action takes "
                f"effect.")

    decl = {}
    qp = run / "quantifiers.json"
    if qp.exists():
        decl = {d["phrase"].strip().lower(): d for d in json.loads(qp.read_text())["quantifiers"]}
    by_item = {}
    for c in claims:
        by_item.setdefault(c.get("docket_item"), []).append(c["id"])
    for where, text in surf:
        flat = re.sub(r"\s+", " ", text)
        for m in UNIVERSAL.finditer(flat):
            phrase = m.group(0).strip().lower()
            # THE DECLARATION IS MATCHED ON THE SENTENCE, not on the regex's own span. The
            # pattern's noun list is lazy, so it stops at the first set noun and a run declaring
            # "all five items" would never match a span reading "all five". A declaration is a
            # human sentence and it is looked for inside the human sentence.
            around = flat[max(0, m.start() - 10):m.end() + 40].lower()
            d = decl.get(phrase) or next(
                (v for k, v in decl.items() if k in around), None)
            if d is None:
                problems.append(
                    f"{where} prints the universal {m.group(0).strip()!r} and "
                    f"quantifiers.json declares no set for it. A quantifier is a claim about a "
                    f"set, so the set is named, the same way every numeral names its computation")
                continue
            key = d.get("figures_key")
            items = ((figs.get(key) or {}).get("from_items")) or d.get("from_items") or []
            if d.get("about") == "sources":
                spoken = [i for i in items if by_item.get(i)]
                if spoken:
                    problems.append(
                        f"{where} says {m.group(0).strip()!r} about {key}, and claims.json speaks "
                        f"to " + ", ".join(f"{i} ({'/'.join(by_item[i])})" for i in spoken))
    # THE EXCLUSIVE COUNT, on every surface the same list reads. Declared by the phrase, and a
    # declaration here must carry the sweep that re-derives it. See EXCLUSIVE above.
    for where, text in surf:
        flat = re.sub(r"\s+", " ", text)
        for m in EXCLUSIVE.finditer(flat):
            phrase = m.group(0).strip().lower()
            around = flat[max(0, m.start() - 10):m.end() + 40].lower()
            d = decl.get(phrase) or next((v for k, v in decl.items() if k in around), None)
            why = exclusive_problem(where, m.group(0).strip(), d)
            if why:
                problems.append(why)
    if ledger and ledger.exists() and (run / "caption.txt").exists():
        first = (run / "caption.txt").read_text(encoding="utf-8").strip().split("\n")[0].strip()
        led = json.loads(ledger.read_text())
        rows = led.get("captions") or led.get("entries") or []
        row = next((r for r in rows if r.get("date") == run.name), None)
        if row and (row.get("first_line") or "").strip() != first:
            problems.append(
                f"ledger/carousel/captions.json stores first_line "
                f"{(row.get('first_line') or '')[:60]!r} and the shipped caption opens "
                f"{first[:60]!r}. It is stored VERBATIM so the next run's critic can catch a "
                f"sentence skeleton, so a stale one disarms the only gate it feeds")
    return problems


def self_test() -> int:
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "2026-08-25"; (d / "render").mkdir(parents=True)
        # AN EMPTY ARTICLES ROOT, so these cases never read the real ledger's edition for a
        # date that happens to match the fixture's name.
        arts = Path(td) / "articles"; arts.mkdir()
        (d / "claims.json").write_text(json.dumps({"claims": [
            {"id": "c44", "docket_item": "tx-2026-0041", "quote": "We did prohibit evaporative "
             "cooling systems", "text": "Wichita Falls attached a condition."}]}))
        (d / "figures.json").write_text(json.dumps({"force_unstated": {
            "value": 5, "from_items": ["tx-2026-0028", "tx-2026-0041"]}}))
        (d / "render/render_report.json").write_text(json.dumps({"slides": [
            {"file": "slide-06.html", "text_nodes": [{"text":
             "San Angelo wrote three of the five. On five of the fifteen no source says either way."}]}]}))
        bad = check(d, ledger=None, articles=arts)
        if not any("SOURCE SILENCE" in p for p in bad):
            print("SELF-TEST FAILED: the gate passed 'no source says either way', which hard "
                  "failed this deck twice"); return 1
        (d / "caption.txt").write_text("Four abatements never got a vote. On five no source says "
                                       "either way.\n")
        if len([p for p in check(d, ledger=None, articles=arts) if "SOURCE SILENCE" in p]) < 2:
            print("SELF-TEST FAILED: the gate found the frame and not the caption, which is the "
                  "whole defect: a repair that lands on the surface that was named and no other")
            return 1
        (d / "render/render_report.json").write_text(json.dumps({"slides": [
            {"file": "slide-06.html", "text_nodes": [{"text":
             "San Angelo wrote three of the five. On five more the record carries no date the "
             "action takes effect."}]}]}))
        (d / "caption.txt").write_text("Four abatements never got a vote.\n")
        left = [p for p in check(d, ledger=None, articles=arts) if "SOURCE SILENCE" in p]
        if left:
            print("SELF-TEST FAILED: the gate refused the repaired measurement wording, which "
                  "would teach a run to ignore it. " + "; ".join(left)); return 1
        # the universal rule, and the claim that refutes it
        (d / "render/render_report.json").write_text(json.dumps({"slides": [
            {"file": "slide-03.html", "text_nodes": [{"text": "Nothing speaks to all five items."}]}]}))
        if not any("declares no set" in p for p in check(d, ledger=None, articles=arts)):
            print("SELF-TEST FAILED: an undeclared universal passed"); return 1
        (d / "quantifiers.json").write_text(json.dumps({"quantifiers": [
            {"phrase": "all five items", "figures_key": "force_unstated", "about": "sources"}]}))
        if not any("claims.json speaks to" in p for p in check(d, ledger=None, articles=arts)):
            print("SELF-TEST FAILED: a declared universal about sources passed while a claim "
                  "spoke to one of its members"); return 1

    # ---- THE WEB EDITION AND THE EXCLUSIVE COUNT, 2026-09-24 ----------------------------------
    #
    # The strings are carousel no. 33's own. DEFECT is `ledger/articles/2026-09-24.json` paragraph
    # sections[0].paragraphs[2] as committed in 3dcc68ea, which a round 2 integrity judge hard
    # failed. REPAIRED is the same paragraph as the run fixed it in 58767a5c. Quoted rather than
    # read from git, because CI checks out one commit and a self-test that needs history is a
    # self-test that cannot run there.
    C18 = ("[If the pod is unable to automatically identify the delivery target and evaluate its "
           "suitability, an image is sent to an operator for real-time evaluation](c18).")
    DEFECT = ("A person enters in one sentence. " + C18 + " The draft gives no figure for how "
              "often that happens. The sentence sits in its section on visual effects rather "
              "than in its description of flight operations.")
    REPAIRED = (C18 + " The draft gives no figure for how often that happens. The sentence sits "
                "in its section on visual effects rather than in its description of flight "
                "operations. People appear elsewhere in the draft too. It says [the Remote Pilot "
                "in Command has the ability to command flight termination](c33) if an aircraft "
                "flies outside its operating area.")
    fails = []

    def expect(label, cond, got):
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}" + ("" if cond else f"  [{got}]"))
        if not cond:
            fails.append(label)

    def edition(root, date, para):
        (root / f"{date}.json").write_text(json.dumps({
            "_spec": {"version": 1}, "dek": {"text": "A dek.", "claims": ["c1"]},
            "sections": [{"heading": "The pod judges the spot", "paragraphs": [
                {"text": para, "claims": ["c18", "c33"]}]}]}), encoding="utf-8")

    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "2026-09-24"; (d / "render").mkdir(parents=True)
        arts = Path(td) / "articles"; arts.mkdir()
        (d / "render/render_report.json").write_text(json.dumps({"slides": [
            {"file": "slide-01.html", "text_nodes": [{"text": "The pod picks the spot"}]}]}))
        ok_frames = check(d, ledger=None, articles=arts)
        expect("a deck with no web edition and clean frames is clean", not ok_frames, ok_frames)

        edition(arts, "2026-09-24", DEFECT)
        got = check(d, ledger=None, articles=arts)
        expect("the web edition is READ: carousel no. 33's 'in one sentence' is caught",
               any("web edition" in p and "exclusive count" in p for p in got), got)
        edition(arts, "2026-09-24", REPAIRED)
        got = check(d, ledger=None, articles=arts)
        expect("...and the paragraph the run repaired it to is clean", not got, got)

        # THE CLAIM'S OWN WORDS ARE NOT JUDGED, the run's prose around them is. Both strings are
        # 2026-09-21's own edition: the first is a source's universal inside its span, the second
        # is prose the run wrote.
        edition(arts, "2026-09-24", "The briefing answered its own automated ticketing line by "
                "saying [there is a human in the loop for all actions](c14).")
        got = check(d, ledger=None, articles=arts)
        expect("a universal inside a claim's own [span](cNN) is the source's, and not reported",
               not got, got)
        edition(arts, "2026-09-24", "Three counts appear in the reporting and none of them "
                "contains another.")
        got = check(d, ledger=None, articles=arts)
        expect("...and the same kind of universal in the run's own prose IS reported",
               any("declares no set" in p and "web edition" in p for p in got), got)

        (arts / "2026-09-24.json").write_text("{ not json", encoding="utf-8")
        got = check(d, ledger=None, articles=arts)
        expect("an edition that exists and can't be read is a finding, never a clean pass",
               any("could not read the web edition" in p for p in got), got)

        # THE SWEEP. The fetched text is a fixture shaped like the draft: the operator sentence
        # and one more that names an operator, which is the refutation in miniature.
        edition(arts, "2026-09-24", DEFECT)
        src = Path(td) / "draft.txt"
        src.write_text("The pod descends. If the pod is unable to identify the target, an image "
                       "is sent to an operator for real-time evaluation. Flights are planned in "
                       "advance.\nThe operators monitor each flight from the operations center.",
                       encoding="utf-8")
        for label, swept, needle in (
                ("a declaration with no sweep is refused", None, "no `swept` block"),
                ("a sweep over a text that is not there can't re-derive",
                 {"text": str(Path(td) / "absent.txt"), "terms": ["operator"], "sentences": 1},
                 "is not there"),
                ("a sweep that declares a count other than the phrase's is refused",
                 {"text": str(src), "terms": ["operator"], "sentences": 2}, "asserts one"),
                ("THE DEFECT: the draft names an operator in two sentences, so 'one' is refuted",
                 {"text": str(src), "terms": ["operator"], "sentences": 1}, "2 sentences")):
            (d / "quantifiers.json").write_text(json.dumps({"quantifiers": [
                dict({"phrase": "in one sentence"}, **({"swept": swept} if swept else {}))]}))
            got = check(d, ledger=None, articles=arts)
            expect(label, any(needle in p for p in got), got)
        src.write_text("The pod descends. If the pod is unable to identify the target, an image "
                       "is sent to an operator for real-time evaluation. Flights are planned in "
                       "advance.", encoding="utf-8")
        got = check(d, ledger=None, articles=arts)
        expect("...and a sweep that really does find one sentence clears it", not got, got)
        (d / "quantifiers.json").unlink()
        for phrase in ("It is named only once in the draft.", "The word appears once.",
                       "The draft says it in a single passage."):
            edition(arts, "2026-09-24", phrase)
            got = check(d, ledger=None, articles=arts)
            expect(f"the exclusive form {phrase!r} is caught",
                   any("exclusive count" in p for p in got), got)
        for phrase in ("One sentence says the pod evaluates the spot.",
                       "It happens at once.", "Only one metro is named first."):
            edition(arts, "2026-09-24", phrase)
            got = check(d, ledger=None, articles=arts)
            expect(f"...and {phrase!r}, which counts no passage of a document, is not",
                   not any("exclusive count" in p for p in got), got)
    if fails:
        print(f"SELF-TEST FAILED: {len(fails)} web edition or exclusive count case(s)")
        return 1
    print("quantifier_check self-test: refuses source silence on every surface at once, passes "
          "the measurement, catches a universal the claims file refutes, reads the web edition, "
          "and re-derives an exclusive count by sweeping the fetched text")
    return 0


def main(argv):
    if "--self-test" in argv:
        return self_test()
    args = [a for a in argv[1:] if not a.startswith("-")]
    if not args:
        print("usage: quantifier_check.py <run-dir> | --self-test", file=sys.stderr); return 2
    d = Path(args[0])
    if not d.is_dir():
        print(f"not a directory: {d}", file=sys.stderr); return 2
    probs = check(d)
    try:
        n_surf = len(surfaces(d))
    except EditionUnreadable:
        n_surf = 0                       # `check` has already reported it as a problem
    (d / "quantifier_report.json").write_text(
        json.dumps({"surfaces": n_surf, "problems": probs}, indent=1) + "\n")
    if probs:
        print(f"quantifier_check: {len(probs)} quantifier(s) the record does not support\n")
        for p in probs:
            print("  - " + p + "\n")
        print("  A quantifier is a claim about a SET. Name the set, or print the measurement.")
        return 1
    print(f"quantifier_check: {n_surf} published string(s), every universal names its set")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
