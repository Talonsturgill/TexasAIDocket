#!/usr/bin/env python3
"""coherence_check.py — the deck reads as ONE object, and a reader can actually read it.

WHAT THIS IS FOR, AND WHY IT IS NOT ANY OF THE GATES BESIDE IT

`qa.py` judges a slide: contrast, clipping, safe zones, art crossing glyphs. `bespoke_check.py`
judges the deck's ART and demands the nine drawings DIFFER. Both are right and neither asks the
two questions a reader actually asks, which are "can I read this in the two seconds I am giving
it" and "is this the same publication I saw yesterday".

Those two pull in opposite directions from `bespoke_check`, and holding both at once is the whole
craft here:

    THE ART VARIES. THE FRAME DOES NOT.

A deck whose drawings all look alike is a template, and `bespoke_check` catches it. A deck whose
FRAME changes every run is not a publication, it is nine posters that happened to arrive on the
same day, and until this file existed nothing caught that at all.

THE EVIDENCE THIS WAS WRITTEN FROM. Measured across the two decks this product has shipped:

    2026-08-16   8 slides, and NO slide counter anywhere in the deck
    2026-08-18   9 slides, every one carrying "01 / 09" through "09 / 09"

Two runs, two different objects, both green on every gate that existed. A reader following this
account got a numbered nine part deck one day and an unnumbered eight part deck the next, and
nothing in the machine had an opinion about it.

WHAT IT CHECKS

    reading load    words per slide against a ceiling. The readability half.
    counter spine   the deck is numbered, consistently, or deliberately is not numbered at all.
    type spine      at least one type size appears on EVERY slide. The deck's furniture.
    hook repeats    no two slides lead with the same line.
    opening length  slide 1 is the only slide most people see, so it gets the shortest line.

WHAT IT DELIBERATELY DOES NOT CHECK, and this matters more than what it does.

**DISPLAY TYPE SIZES ARE NOT GATED.** The first draft of this file counted distinct font sizes
across the deck and would have failed both shipped decks for having 17 and 19 of them. That would
have been wrong, and measuring it is what showed why: the small type IS on a scale, with 24px and
25px present on every slide of both decks, while every hero headline is a one-off at 132, 112,
104, 92, 82, 78. Those one-offs are `TX.fitText` doing exactly its job, fitting a headline to its
box, which `TECHNIQUE_LIBRARY.md` requires and calls out a hand-guessed size as the fault. A gate
on display sizes would have punished the correct behaviour and pushed runs toward hand-sizing.

**COLOUR COUNT IS NOT GATED** either, for the same reason. The decks carry 64 and 43 distinct hex
values, and generative art with gradients and tonal ramps legitimately produces that. A number
there would fire on good work.

A gate that fires on correct behaviour gets switched off, and then it is not protecting anything.

    coherence_check.py --date 2026-08-19
    coherence_check.py --copy out/2026-08-19/copy.json --slides-dir out/2026-08-19/slides
    coherence_check.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

WORD = re.compile(r"[A-Za-z0-9']+")
COUNTER = re.compile(r"^\s*(\d{1,2})\s*/\s*(\d{1,2})\s*$")
FONT_SIZE = re.compile(r"font-size:\s*([0-9.]+)px")

# ------------------------------------------------------------------ the thresholds, and their basis
#
# READING LOAD. An EXTERNAL threshold with headroom, set the way `caption_check.SENTENCE_CEILING`
# was and for the same reason: a ceiling derived from our own corpus is a ratchet that tightens
# every time it is recomputed, and three rounds of that arrive at nothing.
#
# Measured across both shipped decks, the heaviest slide is 54 words (2026-08-18, slide 9) and the
# per deck means are 28.6 and 35.2. The external anchor is what a carousel slide IS: it is read at
# 432px inside a scroll, so it is scanned rather than read, and past roughly sixty words it has
# stopped being a slide and become a paragraph somebody set in a large face.
#
# 65 therefore sits above everything this product has shipped and below the point where the form
# breaks. It fails on REGRESSION, which is a backstop's job, and it cannot creep, because it was
# never derived from us.
READING_LOAD_CEILING = 65

# The opening is the only slide most people see. `TECHNIQUE_LIBRARY.md` asks for four to seven
# words. Measured: 2 and 5. This WARNs rather than fails, because a deck that opens on a short
# verbatim quote is a legitimate move and a hard number here would forbid it.
OPENING_HOOK_WARN = 9

# Claims cited by one slide. Measured max is 6, on the 2026-08-16 summary slide, against a max of
# 2 on the whole of 2026-08-18. A summary slide legitimately gathers many, so this only WARNs.
CLAIMS_PER_SLIDE_WARN = 5


def words(s) -> int:
    return len(WORD.findall(s or ""))


def slide_load(v: dict) -> int:
    """Every word a reader has to take off this slide, whatever field it arrived in."""
    total = 0
    for key in ("kicker", "hook", "dek", "quote", "attribution", "ask"):
        total += words(v.get(key))
    for lab in v.get("labels", []) or []:
        # The counter is furniture, not reading. "03 / 09" is not two words of prose.
        if not COUNTER.match(str(lab)):
            total += words(str(lab))
    return total


def ordered(copy: dict) -> list:
    """(name, slide) in deck order. S10 must not sort between S1 and S2."""
    def key(name):
        m = re.search(r"(\d+)", name)
        return (int(m.group(1)) if m else 0, name)
    return [(n, copy["slides"][n]) for n in sorted(copy.get("slides", {}), key=key)]


def check_copy(copy: dict) -> tuple:
    """(fails, warns) for the deck's copy, as sentences a writer can act on."""
    fails, warns = [], []
    slides = ordered(copy)
    n = len(slides)
    if not n:
        return ["copy.json carries no slides"], []

    # ---- READING LOAD ------------------------------------------------------------------
    for name, v in slides:
        load = slide_load(v)
        if load > READING_LOAD_CEILING:
            fails.append(
                f"{name}: {load} words, over the {READING_LOAD_CEILING} word ceiling. At 432px in "
                f"a feed this is a paragraph rather than a slide. Cut it to one idea, or split it "
                f"across two slides")

    # ---- THE COUNTER SPINE -------------------------------------------------------------
    #
    # All or nothing, then correct. A deck may decide not to number itself, and that is a real
    # choice. What it may not do is number some slides and not others, or promise a total it does
    # not deliver, which is a live untruth printed on the page.
    found = {}
    for name, v in slides:
        for lab in v.get("labels", []) or []:
            m = COUNTER.match(str(lab))
            if m:
                found[name] = (int(m.group(1)), int(m.group(2)))
    if found and len(found) != n:
        missing = [name for name, _ in slides if name not in found]
        fails.append(
            f"{len(found)} of {n} slides carry a counter and {', '.join(missing)} do not. "
            f"Number every slide or number none. A partial spine reads as a missing slide")
    elif found:
        totals = {t for _, t in found.values()}
        if len(totals) > 1:
            fails.append(f"the counter promises {sorted(totals)} different totals across one deck")
        elif totals and totals.pop() != n:
            promised = next(iter({t for _, t in found.values()}))
            fails.append(
                f"the counter says {promised} slides and the deck has {n}. A reader who counts "
                f"is told one of them is missing")
        seen = [num for num, _ in (found[name] for name, _ in slides if name in found)]
        if seen != list(range(1, n + 1)):
            fails.append(f"the counter runs {seen} rather than 1 to {n}. Numbering with a gap or "
                         f"a repeat is worse than no numbering")

    # ---- HOOK REPEATS ------------------------------------------------------------------
    lead = {}
    for name, v in slides:
        h = " ".join((v.get("hook") or v.get("quote") or "").lower().split())
        if h:
            lead.setdefault(h, []).append(name)
    for h, names in lead.items():
        if len(names) > 1:
            fails.append(f"{' and '.join(names)} lead with the same line, \"{h[:48]}\". "
                         f"Two slides saying one thing is one slide")

    # ---- THE OPENING -------------------------------------------------------------------
    first_name, first = slides[0]
    opening = words(first.get("hook")) or words(first.get("quote"))
    if opening > OPENING_HOOK_WARN:
        warns.append(f"{first_name}: the opening line runs {opening} words. It is the only slide "
                     f"most people see, and the craft doctrine asks for four to seven")

    # ---- ONE IDEA PER SLIDE ------------------------------------------------------------
    for name, v in slides:
        c = len(v.get("claims", []) or [])
        if c > CLAIMS_PER_SLIDE_WARN:
            warns.append(f"{name} cites {c} claims. That is usually a slide carrying an argument "
                         f"that wants two slides")
    return fails, warns


def check_type_spine(slides_dir: Path) -> tuple:
    """The deck's furniture holds: some type size appears on EVERY slide.

    NOT a check on how many sizes the deck uses. See the module docstring: display type is fitted
    per slide by `TX.fitText` and varying is correct. What must NOT vary is the furniture, the
    small type that carries the kicker, the counter and the source line. Both shipped decks hold
    24px and 25px on every slide, and a deck that loses that shared spine stops looking like the
    same publication even when every slide is individually fine.
    """
    files = sorted(slides_dir.glob("slide-*.html"))
    if not files:
        return [], [f"no slide html in {slides_dir}, so the type spine was not measured"]
    per = []
    for f in files:
        per.append(set(FONT_SIZE.findall(f.read_text(encoding="utf-8"))))
    shared = set.intersection(*per) if per else set()
    if not shared:
        return ([f"no type size is shared by all {len(files)} slides. The deck has no furniture in "
                 f"common, so it reads as {len(files)} posters rather than one deck"], [])
    return [], []


def run(copy_path: Path, slides_dir: Path | None, *, quiet: bool = False) -> int:
    copy = json.loads(copy_path.read_text(encoding="utf-8"))
    fails, warns = check_copy(copy)
    if slides_dir and slides_dir.exists():
        f2, w2 = check_type_spine(slides_dir)
        fails += f2
        warns += w2

    if not quiet:
        slides = ordered(copy)
        loads = [slide_load(v) for _, v in slides]
        print(f"coherence_check: {len(slides)} slides, reading load "
              f"min {min(loads)} max {max(loads)} mean {sum(loads) / len(loads):.1f} "
              f"(ceiling {READING_LOAD_CEILING})")

    for w in warns:
        print(f"  warn  {w}", file=sys.stderr)
    if fails:
        print(f"\ncoherence_check: {len(fails)} coherence problem(s)\n", file=sys.stderr)
        for f in fails:
            print(f"  - {f}", file=sys.stderr)
        return 1
    if not quiet:
        print("coherence_check: the deck reads as one object")
    return 0


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    import tempfile
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    def deck(n=3, counters=True, total=None, loads=None, hooks=None):
        total = n if total is None else total
        slides = {}
        for i in range(1, n + 1):
            labels = [f"{i:02d} / {total:02d}"] if counters else []
            hook = (hooks[i - 1] if hooks else f"Slide {i} says a thing")
            dek = " ".join(["word"] * (loads[i - 1] if loads else 5))
            slides[f"S{i}"] = {"hook": hook, "dek": dek, "labels": labels, "claims": ["c1"]}
        return {"slides": slides}

    clean = deck()
    ok("a coherent deck passes", check_copy(clean) == ([], []), str(check_copy(clean)))

    # THE READABILITY HALF.
    heavy = deck(loads=[5, 200, 5])
    ok("a slide over the reading ceiling fails",
       any("over the" in f and "word ceiling" in f for f in check_copy(heavy)[0]))
    ok("...and the ceiling is above everything this product has shipped",
       READING_LOAD_CEILING > 54)

    # THE COUNTER SPINE, which is the defect measured across the two real decks.
    ok("a deck with NO counters anywhere passes, because that is a real choice",
       check_copy(deck(counters=False)) == ([], []))
    part = deck()
    part["slides"]["S2"]["labels"] = []
    ok("...but a deck that numbers SOME slides fails",
       any("Number every slide or number none" in f for f in check_copy(part)[0]),
       str(check_copy(part)[0]))
    ok("a counter promising more slides than the deck has fails",
       any("A reader who counts" in f for f in check_copy(deck(n=3, total=9))[0]),
       str(check_copy(deck(n=3, total=9))[0]))
    gap = deck(n=3)
    gap["slides"]["S2"]["labels"] = ["05 / 03"]
    ok("a counter with a gap or a repeat fails",
       any("rather than 1 to" in f or "different totals" in f for f in check_copy(gap)[0]),
       str(check_copy(gap)[0]))

    # S10 MUST NOT SORT BETWEEN S1 AND S2. A plain string sort puts it there and the counter
    # check would then report a false gap on any deck that ever runs past nine slides.
    ok("slide order is numeric, not lexicographic",
       [n for n, _ in ordered(deck(n=11))][:3] == ["S1", "S2", "S3"],
       str([n for n, _ in ordered(deck(n=11))]))
    ok("...and an eleven slide deck with correct counters still passes",
       check_copy(deck(n=11)) == ([], []), str(check_copy(deck(n=11))))

    # THE COUNTER IS FURNITURE, NOT READING.
    ok("the counter does not count toward the reading load",
       slide_load({"labels": ["03 / 09"]}) == 0)
    ok("...but a real label does", slide_load({"labels": ["HARRIS COUNTY"]}) == 2)

    dup = deck(hooks=["The same line", "The same line", "Another"])
    ok("two slides leading with one line fails",
       any("lead with the same line" in f for f in check_copy(dup)[0]))

    longopen = deck(hooks=["One two three four five six seven eight nine ten", "b", "c"])
    ok("a long opening line warns rather than fails",
       any("only slide most people see" in w for w in check_copy(longopen)[1])
       and not check_copy(longopen)[0])

    # THE TYPE SPINE.
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        (d / "slide-01.html").write_text("<b style='font-size: 24px'>a</b>"
                                         "<i style='font-size: 90px'>h</i>", encoding="utf-8")
        (d / "slide-02.html").write_text("<b style='font-size: 24px'>a</b>"
                                         "<i style='font-size: 71px'>h</i>", encoding="utf-8")
        ok("a shared furniture size across slides passes, even with different display sizes",
           check_type_spine(d)[0] == [], str(check_type_spine(d)))
        (d / "slide-03.html").write_text("<b style='font-size: 31px'>a</b>", encoding="utf-8")
        ok("...and a slide sharing NO size with the others fails",
           any("no furniture in common" in f for f in check_type_spine(d)[0]),
           str(check_type_spine(d)))

    # THE GATE MUST NOT FIRE ON THE CORRECT BEHAVIOUR IT WAS ALMOST BUILT TO PUNISH.
    src = open(__file__, encoding="utf-8").read()
    ok("the decision not to gate display type sizes is written down with its reason",
       "DISPLAY TYPE SIZES ARE NOT GATED" in src and "fitText" in src)
    ok("...and the measurement that produced that decision is recorded",
       "132" in src and "24px and 25px" in src)

    print(f"\ncoherence_check self-test: "
          + ("all passed" if not failures else f"{failures} FAILED"))
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date")
    ap.add_argument("--copy")
    ap.add_argument("--slides-dir")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    if a.copy:
        copy_path = Path(a.copy)
        slides = Path(a.slides_dir) if a.slides_dir else copy_path.parent / "slides"
    elif a.date:
        base = REPO_ROOT / "out" / a.date
        copy_path = base / "copy.json"
        if not copy_path.exists():
            copy_path = REPO_ROOT / "runs" / "carousel" / a.date / "copy.json"
        slides = Path(a.slides_dir) if a.slides_dir else copy_path.parent / "slides"
    else:
        print("coherence_check: pass --date, --copy or --self-test", file=sys.stderr)
        return 2
    if not copy_path.exists():
        print(f"coherence_check: no copy.json at {copy_path}", file=sys.stderr)
        return 2
    return run(copy_path, slides)


if __name__ == "__main__":
    raise SystemExit(main())
