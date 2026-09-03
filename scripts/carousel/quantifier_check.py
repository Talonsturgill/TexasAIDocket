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


def surfaces(run: Path) -> list:
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
    return out


def check(run: Path, ledger=_UNSET) -> list:
    if ledger is _UNSET:
        ledger = CAPTIONS_LEDGER
    problems = []
    figs = {}
    fp = run / "figures.json"
    if fp.exists():
        figs = json.loads(fp.read_text())
    claims = []
    cp = run / "claims.json"
    if cp.exists():
        claims = json.loads(cp.read_text())["claims"]
    surf = surfaces(run)
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
        (d / "claims.json").write_text(json.dumps({"claims": [
            {"id": "c44", "docket_item": "tx-2026-0041", "quote": "We did prohibit evaporative "
             "cooling systems", "text": "Wichita Falls attached a condition."}]}))
        (d / "figures.json").write_text(json.dumps({"force_unstated": {
            "value": 5, "from_items": ["tx-2026-0028", "tx-2026-0041"]}}))
        (d / "render/render_report.json").write_text(json.dumps({"slides": [
            {"file": "slide-06.html", "text_nodes": [{"text":
             "San Angelo wrote three of the five. On five of the fifteen no source says either way."}]}]}))
        bad = check(d, ledger=None)
        if not any("SOURCE SILENCE" in p for p in bad):
            print("SELF-TEST FAILED: the gate passed 'no source says either way', which hard "
                  "failed this deck twice"); return 1
        (d / "caption.txt").write_text("Four abatements never got a vote. On five no source says "
                                       "either way.\n")
        if len([p for p in check(d, ledger=None) if "SOURCE SILENCE" in p]) < 2:
            print("SELF-TEST FAILED: the gate found the frame and not the caption, which is the "
                  "whole defect: a repair that lands on the surface that was named and no other")
            return 1
        (d / "render/render_report.json").write_text(json.dumps({"slides": [
            {"file": "slide-06.html", "text_nodes": [{"text":
             "San Angelo wrote three of the five. On five more the record carries no date the "
             "action takes effect."}]}]}))
        (d / "caption.txt").write_text("Four abatements never got a vote.\n")
        left = [p for p in check(d, ledger=None) if "SOURCE SILENCE" in p]
        if left:
            print("SELF-TEST FAILED: the gate refused the repaired measurement wording, which "
                  "would teach a run to ignore it. " + "; ".join(left)); return 1
        # the universal rule, and the claim that refutes it
        (d / "render/render_report.json").write_text(json.dumps({"slides": [
            {"file": "slide-03.html", "text_nodes": [{"text": "Nothing speaks to all five items."}]}]}))
        if not any("declares no set" in p for p in check(d, ledger=None)):
            print("SELF-TEST FAILED: an undeclared universal passed"); return 1
        (d / "quantifiers.json").write_text(json.dumps({"quantifiers": [
            {"phrase": "all five items", "figures_key": "force_unstated", "about": "sources"}]}))
        if not any("claims.json speaks to" in p for p in check(d, ledger=None)):
            print("SELF-TEST FAILED: a declared universal about sources passed while a claim "
                  "spoke to one of its members"); return 1
    print("quantifier_check self-test: refuses source silence on every surface at once, passes "
          "the measurement, and catches a universal the claims file refutes")
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
    (d / "quantifier_report.json").write_text(
        json.dumps({"surfaces": len(surfaces(d)), "problems": probs}, indent=1) + "\n")
    if probs:
        print(f"quantifier_check: {len(probs)} quantifier(s) the record does not support\n")
        for p in probs:
            print("  - " + p + "\n")
        print("  A quantifier is a claim about a SET. Name the set, or print the measurement.")
        return 1
    print(f"quantifier_check: {len(surfaces(d))} published string(s), every universal names its set")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
