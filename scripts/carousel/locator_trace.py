#!/usr/bin/env python3
"""locator_trace.py — where in a document a frame says something is, is itself a claim.

WHY THIS EXISTS. 2026-08-28, deck no. 10, and the six instances are named below.

A figure cannot reach a frame without going through the run's `compute.py`, which refuses
anything that is not in a claim's quote. A NAMED PLACE IN A DOCUMENT reaches a frame by being
typed into the slide HTML, and until this file nothing stood in between.

    2026-08-28  s3  ORDERING PARAGRAPH 1
    2026-08-28  s3  CONDITION 1
    2026-08-28  s5  FINDINGS OF FACT
    2026-08-28  s8  ORDERING PARAGRAPH 6
    ...six instances across those four eyebrows and the source block.

ALL OF THEM WERE TRUE, which is exactly why this needs a gate rather than more care. Checked
against the order text the run had already fetched, line 658 is `V. Ordering Paragraphs`, its
paragraph 1 is the approval followed by `Condition 1:`, line 750 is `6. The Commission denies
all other motions`, and line 317 is `III. Findings of Fact`. The frames were right and the
claims file did not carry what they were asserting, so a reader had no way to check any of it
and the next deck's guess would have shipped the same way.

Four gates and one judge looked at that deck, and only the judge saw it. `numeral_lint` reads
published site copy, not slide strings. `copy_sync_check` asks whether `copy.json` and the
render agree, which they did. `aggregate_check` asks whether a NUMERAL traces, and
`ORDERING PARAGRAPH 6` reaches a frame as an eyebrow rather than as a figure.

THE ONE DESIGN NOTE THAT MATTERS, AND IT WAS LEARNED THE HARD WAY

**This reads the RENDER, never `copy.json`.** A sweep over `copy.json` reports the 2026-08-28
deck clean, because `copy.json` does not carry the eyebrow strings at all. Three of the six
instances, on slides 4, 5 and 8, are invisible to it. A gate whose subject is what a reader
receives has to read what was drawn, which is GATE_LESSONS 35 in a different costume: get the
form from the renderer, not from your idea of it.

WHAT COUNTS AS A LOCATOR, MEASURED RATHER THAN LISTED

The first cut matched a structure word with an optional number, and on the ten shipped decks it
raised 29 candidates of which 25 were the ordinary English words `item`, `condition`, `section`
and `schedule` in running prose. A gate that cries wolf 25 times teaches a run to scroll past
the 26th, so the shape is narrower and each half is justified by the corpus:

  NUMBERED   a structure word followed by a number. `Ordering Paragraph 6`, `Condition 1`,
             `Item 33`, `Section 25.521`. This is unambiguous. Nobody writes "item 33" meaning
             anything but the thirty third item of something.
  NAMED      `ordering paragraph`, `findings of fact`, `conclusions of law`, with or without a
             number. These three phrases are never ordinary English and one of them is the
             2026-08-28 slide 5 instance, which carries no number at all.

The number is consumed WHOLE, dots included. The first cut read `16 TAC Section 25.521` as
`section 25` and would have reported a locator the frame does not contain, which is the
`\\d{1,4}` reading `2,600 streamlines` as `600` from GATE_LESSONS 16. A gate that misreports is
worse than one that misses, because the run then hunts for something that was never there.

WHAT CARRIES A LOCATOR, AND WHY `text` IS NOT ON THE LIST

    quote          the source's own words, checked against the fetched document
    source_title   the citation. A locator IS a citation, and this is where one lives

`text` is deliberately excluded. It is the deck's own sentence describing the claim, written by
the same hand that types the slide, so accepting it would let a deck satisfy the gate by saying
the thing twice. That was a judge's refinement on the proposal and the corpus supports it: it
costs nothing on the 2026-08-28 deck, where all twelve locators trace through `source_title`,
and it is the difference between provenance and repetition.

Requiring `quote` ALONE was considered and rejected by measurement. A locator names where in a
document a sentence sits, so it is almost never inside the sentence: eight of the 2026-08-28
deck's twelve tokens are carried by `source_title` and by nothing else. A gate that refuses the
honest route teaches a run that the honest route fails, GATE_LESSONS 16.

A DOCKET OR CONTROL NUMBER IS NOT THIS GATE'S BUSINESS. `Docket 59220` is a numeral on a frame
and `aggregate_check` already owns every numeral on a frame. Two checkers for one string is how
they drift.

MEASURED ON EVERY SHIPPED DECK, quote and source_title as carriers, run 2026-08-28:

    2026-08-16   0 tokens             2026-08-23   0 tokens
    2026-08-18   0 tokens             2026-08-25   1 token,   0 untraced
    2026-08-19   0 tokens             2026-08-26   0 tokens
    2026-08-20   2 tokens, 0 untraced 2026-08-27   1 token,   1 untraced
    2026-08-21   0 tokens             2026-08-28  13 tokens,  0 untraced
    2026-08-22   6 tokens, 1 untraced

Both historical findings are real and neither is a false alarm. 2026-08-27's sources block calls
a Brazos County notice a `Section 312.207` notice and no claim in that run says so, which is
this exact defect a day earlier. 2026-08-22's caption says `Item 33` where that deck's claims
carry it only in `text`. Its `Section 25.521` traces, because the claim quotes `§25.521` and the
symbol is normalised to the word.

Registered CURRENT in `shipped_check`, for the reason that file already writes down about
`aggregates`: judging published work by a rule written after it is how a suite teaches a run to
ignore it. The newest deck must be clean and an older deck reports as a note.

    locator_trace.py --date 2026-08-28
    locator_trace.py --run 2026-08-28
    locator_trace.py --all
    locator_trace.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

# The fields on a claim that may CARRY a locator. See the docstring for why `text` is absent.
CARRIERS = ("quote", "source_title")

# Structure words that need a number before they are a locator.
NUMBERED = (r"ordering paragraphs?|paragraphs?|findings? of fact|conclusions? of law"
            r"|conditions?|sections?|exhibits?|items?|attachments?|appendix|appendices"
            r"|schedules?|articles?|clauses?")

# Phrases that are a locator standing alone, because none of them is ordinary English.
NAMED = r"ordering paragraphs?|findings? of fact|conclusions? of law"

LOCATOR = re.compile(
    rf"\b(?:(?P<h1>{NUMBERED})\s+(?:nos?\.?\s*)?(?P<n>\d[\d.]*\d|\d)|(?P<h2>{NAMED}))\b",
    re.I)

# `§25.521` is how a Texas rule proposal writes `Section 25.521`, and 2026-08-22's claim quote
# uses the symbol while its frame spells the word. One spelling, normalised on both sides.
SECTION_SIGN = re.compile(r"§\s*")


def normalise(s: str) -> str:
    return re.sub(r"\s+", " ", SECTION_SIGN.sub("section ", str(s or ""))).strip()


def head_of(word: str) -> str:
    """`Findings of Fact` and `finding of fact` are one head. `Conditions` and `Condition` too."""
    w = re.sub(r"\s+", " ", word.strip().lower())
    for plural, single in (("findings of fact", "finding of fact"),
                           ("conclusions of law", "conclusion of law"),
                           ("appendices", "appendix")):
        if w == plural:
            return single
    lead, _, rest = w.partition(" ")
    if lead.endswith("s") and not lead.endswith("ss"):
        lead = lead[:-1]
    return (lead + (" " + rest if rest else "")).strip()


def tokens(text: str) -> list:
    """[(head, number_or_None, surface)] for every locator in one string. One tokeniser, used on
    the frame and on the claims, because a repo whose rule is that a thing written twice is wrong
    in both places should not carry two of these. GATE_LESSONS 34."""
    out = []
    for m in LOCATOR.finditer(normalise(text)):
        head = head_of(m.group("h1") or m.group("h2"))
        out.append((head, m.group("n"), re.sub(r"\s+", " ", m.group(0)).strip()))
    return out


def heads_agree(frame_head: str, claim_head: str) -> bool:
    """`Paragraph 6` on a frame is satisfied by `Ordering Paragraph 6` in the citation, and the
    other way round. A qualifier dropped in a two word eyebrow is a typographic choice, not a
    different assertion, and refusing it would fail a correct frame."""
    return frame_head == claim_head or frame_head.endswith(" " + claim_head) \
        or claim_head.endswith(" " + frame_head)


def carried(claims) -> list:
    cs = claims.get("claims") if isinstance(claims, dict) and "claims" in claims else claims
    out = []
    for c in (cs or []):
        if not isinstance(c, dict):
            continue
        for k in CARRIERS:
            out += tokens(c.get(k))
    return out


def traces(tok, carried_tokens) -> bool:
    head, num, _surface = tok
    for chead, cnum, _cs in carried_tokens:
        if not heads_agree(head, chead):
            continue
        if num is None or num == cnum:
            return True
    return False


def frame_strings(run_dir: Path) -> list:
    """Every string this run PUBLISHED, asked for rather than listed.

    `aggregate_check.surfaces` owns the list of published surfaces, and it owns it because a
    hand-kept copy in an adapter fell behind it twice in two days. This asks it, then adds the
    render's own text nodes, which are the thing `copy.json` cannot answer for.
    """
    import aggregate_check as ag
    sf = ag.surfaces(run_dir)
    out = []
    rep = sf.get("report") or {}
    for slide in (rep.get("slides") or []):
        for node in (slide.get("text_nodes") or []):
            t = node.get("text")
            if t:
                out.append((str(slide.get("file") or "frame"), str(t)))
    for name in ("caption", "comment", "title"):
        if sf.get(name):
            out.append((name, str(sf[name])))
    return out


def check(strings: list, claims) -> tuple:
    """(fails, warns, stats). `strings` is [(where, text)]."""
    have = carried(claims)
    fails, seen, n = [], set(), 0
    for where, text in strings:
        for tok in tokens(text):
            n += 1
            head, num, surface = tok
            key = (head, num)
            if traces(tok, have) or key in seen:
                continue
            seen.add(key)
            fails.append(
                f"{where}: {surface!r} is printed and no claim's quote or source_title says "
                f"so. A place in a document is a claim about that document in the way a number "
                f"is. Put the locator in the claim's source_title, where a reader can check it, "
                f"or take it off the frame. It being TRUE is not the question, because every "
                f"one of the six that shipped on 2026-08-28 was true")
    return fails, [], {"tokens": n, "carried": len(have)}


def load(date: str, shipped: bool) -> Path:
    base = (REPO_ROOT / "runs" / "carousel" / date) if shipped else (REPO_ROOT / "out" / date)
    if not (base / "claims.json").exists():
        raise SystemExit(f"locator_trace: need claims.json under {base}")
    return base


def run(date: str, shipped: bool = False) -> int:
    d = load(date, shipped)
    claims = json.loads((d / "claims.json").read_text(encoding="utf-8"))
    fails, _w, stats = check(frame_strings(d), claims)
    for f in fails:
        print(f"  FAIL  {f}", file=sys.stderr)
    print(f"locator_trace: {stats['tokens']} locator(s) on published surfaces, "
          f"{stats['carried']} carried by claims, {len(fails)} untraced")
    return 1 if fails else 0


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    bad = 0

    def ok(label, cond, extra=""):
        nonlocal bad
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            bad += 1

    # THE SIX INSTANCES, as they were on 2026-08-28 before the data was repaired. The claims
    # below are that run's own c8 and c15 with the locator stripped out of the source_title,
    # which is exactly the state the deck shipped four rounds in.
    BEFORE = {"claims": [
        {"id": "c8", "quote": "Crusoe and Ensign must ensure that the Crusoe Two Load fully "
                              "curtails its consumption",
         "source_title": "PUCT Docket 59220, Order issued July 24th 2026, filed as item 69"},
        {"id": "c15", "quote": "The Commission denies all other motions and any other requests",
         "source_title": "PUCT Docket 59220, Order issued July 24th 2026, filed as item 69"},
        {"id": "c3", "quote": "Goodnight owns and operates GOODNIT1",
         "source_title": "PUCT Docket 59220, Order issued July 24th 2026, filed as item 69"}]}
    SHIPPED = [("slide-03.html", "PUCT DOCKET 59220, ORDER, ORDERING PARAGRAPH 1"),
               ("slide-03.html", "CONDITION 1"),
               ("slide-05.html", "PUCT DOCKET 59220, ORDER, FINDINGS OF FACT"),
               ("slide-08.html", "PUCT DOCKET 59220, ORDER, ORDERING PARAGRAPH 6")]
    f, _w, s = check(SHIPPED, BEFORE)
    ok("the four 2026-08-28 locators are CAUGHT before the data was repaired", len(f) == 4,
       f"{len(f)}: {[x.split(':')[1][:34] for x in f]}")
    ok("...and the message names the string on the frame",
       any("ORDERING PARAGRAPH 6" in x for x in f), str(f))
    ok("...and the tokeniser read every one of them", s["tokens"] == 4, str(s))

    # ...and the repair. The locator moved into the claim's source_title, which is the fix the
    # run actually made, and the gate goes green on it.
    AFTER = json.loads(json.dumps(BEFORE))
    AFTER["claims"][0]["source_title"] += ", Ordering Paragraph 1, Condition 1"
    AFTER["claims"][1]["source_title"] += ", Ordering Paragraph 6"
    AFTER["claims"][2]["source_title"] += ", Findings of Fact 3"
    f, _w, _s = check(SHIPPED, AFTER)
    ok("...and putting each locator in its claim's source_title clears every one", not f, str(f))

    # A BARE HEADING IS SATISFIED BY A NUMBERED ONE, and by nothing else. Slide 5 printed
    # FINDINGS OF FACT with no number and the claims carry Findings of Fact 3 and 5.
    f, _w, _s = check([("s5", "FINDINGS OF FACT")], {"claims": [
        {"source_title": "Order, Findings of Fact 3"}]})
    ok("a bare heading traces to a numbered one in the citation", not f, str(f))
    f, _w, _s = check([("s5", "CONCLUSIONS OF LAW")], {"claims": [
        {"source_title": "Order, Findings of Fact 3"}]})
    ok("...and a DIFFERENT bare heading does not", len(f) == 1, str(f))

    # THE NUMBER IS PART OF THE ASSERTION. `Ordering Paragraph 6` is not satisfied by a claim
    # citing paragraph 1, and a substring test would have said it was.
    f, _w, _s = check([("s8", "ORDERING PARAGRAPH 6")], {"claims": [
        {"source_title": "Order, Ordering Paragraph 1"}]})
    ok("a WRONG paragraph number is caught", len(f) == 1, str(f))
    f, _w, _s = check([("s8", "ITEM 6")], {"claims": [{"source_title": "filed as item 69"}]})
    ok("`item 6` is not carried by `item 69` (a substring test would say it was)",
       len(f) == 1, str(f))

    # THE NUMBER IS CONSUMED WHOLE. Reading `16 TAC Section 25.521` as `section 25` is the
    # GATE_LESSONS 16 defect, where a gate named a number the slide does not contain.
    ok("a dotted rule number is one token",
       tokens("16 TAC Section 25.521, proposed") == [("section", "25.521", "Section 25.521")],
       str(tokens("16 TAC Section 25.521, proposed")))
    ok("the section symbol is one spelling of the word",
       tokens("proposes new §25.521 relating to")
       == [("section", "25.521", "section 25.521")],
       str(tokens("proposes new §25.521 relating to")))

    # ORDINARY ENGLISH IS NOT A LOCATOR. Every one of these is a real string off a shipped deck
    # and the first cut of this gate reported all of them.
    for line in ("The schedule gives each block a length.",
                 "The letter's condition is on approval.",
                 "The board item calls this phase early work.",
                 "Sources, in the order the deck uses them."):
        ok(f"not a locator: {line[:40]!r}", not tokens(line), str(tokens(line)))

    # `text` IS NOT A CARRIER. The deck's own sentence about the claim cannot satisfy the gate,
    # because it is written by the hand that types the slide.
    f, _w, _s = check([("s1", "ITEM 33")], {"claims": [
        {"text": "Item 33 was filed August 3rd, 2026.", "quote": "8/3/2026 Helen Bryant PC"}]})
    ok("a locator carried ONLY by the claim's own `text` does not trace", len(f) == 1, str(f))

    # THE SUBJECT IS THE RENDER. This is the note the 2026-08-28 run paid for: a sweep over
    # copy.json reports that deck clean, because copy.json does not carry the eyebrows at all.
    # Proved here on the real artifact rather than asserted.
    newest = None
    for p in sorted((REPO_ROOT / "runs" / "carousel").glob("2*")):
        if (p / "claims.json").exists() and (p / "render_report.json").exists():
            newest = p
    if newest is not None:
        cp = newest / "copy.json"
        copy_text = cp.read_text(encoding="utf-8") if cp.exists() else ""
        rendered = frame_strings(newest)
        only_in_render = [t for w, s in rendered for t in tokens(s)
                          if t[2].lower() not in copy_text.lower()]
        ok(f"{newest.name}: the render carries locators copy.json does not, so reading the "
           f"render is the whole gate", bool(only_in_render),
           f"found {sorted({t[2] for t in only_in_render})}")
        cl = json.loads((newest / "claims.json").read_text(encoding="utf-8"))
        f, _w, s = check(rendered, cl)
        ok(f"{newest.name}: the newest shipped deck is clean", not f, str(f))
        ok(f"{newest.name}: and the gate was not silent about it", s["tokens"] > 0, str(s))

        # AND IT CAN STILL GO RED ON THE REAL ARTIFACT. Strip the locators back out of the
        # source_titles and the shipped deck fails, which is the state it was in for four rounds.
        stripped = json.loads(json.dumps(cl))
        for c in stripped["claims"]:
            c["source_title"] = re.sub(
                r",\s*(?:Ordering Paragraph|Findings of Fact|Conclusions of Law|Condition)"
                r"[^,]*", "", c.get("source_title") or "", flags=re.I)
        f2, _w, _s = check(rendered, stripped)
        ok(f"{newest.name}: with the repair undone the same deck goes RED", bool(f2),
           "the gate cannot go red on the artifact it was written for")

    print("\nlocator_trace self-test: " + ("all passed" if not bad else f"{bad} FAILED"))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date")
    ap.add_argument("--run")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.all:
        rc = 0
        for d in sorted((REPO_ROOT / "runs" / "carousel").glob("2*")):
            if (d / "claims.json").exists():
                print(f"--- {d.name} ---")
                rc |= run(d.name, shipped=True)
        return rc
    if a.run:
        return run(a.run, shipped=True)
    if not a.date:
        ap.error("--date, --run, --all or --self-test")
    return run(a.date)


if __name__ == "__main__":
    raise SystemExit(main())
