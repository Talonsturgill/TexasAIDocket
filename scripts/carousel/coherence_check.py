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


BRAND_YAML = Path(__file__).resolve().parents[2] / "config" / "brand.yaml"
SITE_LINE = re.compile(r'class="tx-site"[^>]*>([^<]+)<')


def brand_site() -> str | None:
    """The one site string, read from config/brand.yaml rather than kept as a copy here.

    Reading it is the entire point. A constant in this file would be a fourth copy of the same
    fact and this gate exists because there were already three.

    It is `visual.constellation.site` specifically. A first draft of this function took the first
    line starting with `site:`, which is a different key several sections earlier with no value on
    it, so the function returned None and the gate passed on a deck carrying the wrong URL on all
    eight frames. A checker that cannot find its own input reports clean, which is the failure
    this repo keeps rediscovering.
    """
    if not BRAND_YAML.exists():
        return None
    try:
        import yaml  # type: ignore
        d = yaml.safe_load(BRAND_YAML.read_text(encoding="utf-8")) or {}
        v = (d.get("visual") or {}).get("constellation", {}).get("site")
        if isinstance(v, str) and v.strip():
            return v.strip()
    except Exception:
        pass
    # no yaml available: walk to constellation: and take the site: under it
    inside = False
    for line in BRAND_YAML.read_text(encoding="utf-8").splitlines():
        if re.match(r"^\s*constellation:\s*$", line):
            inside = True
            continue
        if inside and re.match(r"^\s{0,4}\S", line) and not line.strip().startswith("#"):
            if not re.match(r"^\s{4,}", line):
                inside = False
        if inside:
            m = re.match(r"^\s*site:\s*(.+)$", line)
            if m:
                v = m.group(1).split("#", 1)[0].strip().strip('"').strip("'")
                if v:
                    return v
    return None


def check_site_line(slides_dir: Path) -> tuple:
    """Every frame's footer prints the site brand.yaml names, and no other host.

    THE DEFECT. `config/brand.yaml` has carried the site string since the first deck and
    `frame.py` kept its own hardcoded copy of it. When the project moved to its own domain on
    2026-08-15, `docs/CNAME` and `site_build.SITE_URL` moved and the slide footer did not, so
    three published decks printed the OWNER'S PERSONAL GitHub Pages host across the bottom of
    every slide. Every gate was green for all three, because not one of them compared the
    rendered footer against the config that governs it.

    Same shape as the missing hashtags and the missing progress counter: a rule stated in
    config, a surface keeping its own copy, and nothing in between checking they agree.
    """
    want = brand_site()
    if not want:
        return [], ["config/brand.yaml names no visual.constellation.site, so the footer was not checked"]
    files = sorted(slides_dir.glob("slide-*.html"))
    if not files:
        return [], [f"no slide html in {slides_dir}, so the site line was not measured"]
    bad = []
    for f in files:
        got = SITE_LINE.findall(f.read_text(encoding="utf-8"))
        if not got:
            bad.append(f"{f.name} prints no site line, and the constellation fixes one on every frame")
        elif got[0].strip() != want:
            bad.append(f"{f.name} prints '{got[0].strip()}' and config/brand.yaml says '{want}'. "
                       f"The footer is published on every slide, so a stale copy here is a wrong "
                       f"URL on the whole deck")
    return bad, []


# ------------------------------------------------------------------ the constellation register
#
# THE DEFECT (2026-08-29, deck no. 11). `config/brand.yaml` lists seven elements under
# `visual.constellation` and calls them FIXED on every deck. Two of the panel's judges found,
# independently, that the five-pointed star mark and the county-first coordinates footer appeared
# on none of the nine frames. Nothing in the build could have caught it: `check_site_line` above
# asserts ONE of the seven against the config, and nothing asserts the other six or notices that
# they are unasserted.
#
# The fault is not that six rules were unenforced. It is that NOTHING SAID SO. A file that carries
# one enforced element beside six silent ones reads, to anyone auditing it, exactly like a file
# that enforces the constellation. GATE_LESSONS 49 is the entry for this: a checker covering four
# tenths of what it appears to cover is more dangerous than no checker, because the missing six
# produce confidence rather than doubt.
#
# So this does not check the deck. It checks the COVERAGE, against `config/carousel/constellation.yaml`,
# and it goes red on five states:
#
#   1. brand.yaml names a fixed element the register does not
#   2. the register names an element brand.yaml no longer has
#   3. an entry takes neither route
#   4. an entry's `enforced_by` names a function that does not exist in this module
#   5. an `unenforced` entry carries no reason or no date
#
# State 1 is the one it exists for: brand.yaml grows an eighth fixed element, nobody decides what
# to do about it, and the build says so on the next run instead of two judges saying so in round 5.
# State 4 is GATE_LESSONS 56, a marker check being only as good as its marker: `enforced_by` is a
# name somebody typed, and a name that resolves to nothing is a promise with no code behind it.
REGISTER = Path(__file__).resolve().parents[2] / "config" / "carousel" / "constellation.yaml"


def check_constellation() -> tuple:
    """Every element brand.yaml fixes is either enforced here or recorded as a dated debt."""
    try:
        import yaml  # type: ignore
    except ImportError:
        # NEVER A SKIP. A check that cannot run is the opposite of a check that is not needed,
        # and they must not share a report line. GATE_LESSONS 37.
        return (["the constellation register needs PyYAML and it is not installed, so the "
                 "coverage of brand.yaml's fixed elements was NOT checked"], [])
    if not BRAND_YAML.exists():
        return ([f"{BRAND_YAML} is missing, so nothing could be compared"], [])
    if not REGISTER.exists():
        return ([f"{REGISTER} is missing. It is the record of which of brand.yaml's fixed "
                 f"constellation elements this repo actually enforces"], [])
    brand = yaml.safe_load(BRAND_YAML.read_text(encoding="utf-8")) or {}
    fixed = ((brand.get("visual") or {}).get("constellation") or {})
    reg = (yaml.safe_load(REGISTER.read_text(encoding="utf-8")) or {}).get("elements") or {}
    if not fixed:
        return (["brand.yaml names no visual.constellation elements, so this gate is reading the "
                 "wrong file rather than finding nothing"], [])

    fails = []
    for key in sorted(set(fixed) - set(reg)):
        fails.append(
            f"config/brand.yaml fixes '{key}' on every deck and config/carousel/constellation.yaml "
            f"does not mention it, so nothing in this repo either enforces it or admits that it "
            f"does not. That is how the star mark and the coordinates footer reached round 5 of "
            f"2026-08-29 with two judges finding them by eye. Add an entry with enforced_by or "
            f"unenforced")
    for key in sorted(set(reg) - set(fixed)):
        fails.append(
            f"config/carousel/constellation.yaml carries '{key}' and brand.yaml no longer fixes "
            f"it. A register entry for a rule that was repealed reads exactly like coverage")
    for key in sorted(set(reg) & set(fixed)):
        entry = reg[key] if isinstance(reg[key], dict) else {}
        fn, un = entry.get("enforced_by"), entry.get("unenforced")
        if fn and un:
            fails.append(f"'{key}' claims both enforced_by and unenforced. It is one or the other")
        elif fn:
            if not callable(globals().get(str(fn))):
                fails.append(
                    f"'{key}' says it is enforced by {fn!r} and this module has no such function. "
                    f"A name nobody resolved is a promise with no code behind it")
        elif un:
            if not str(un).strip():
                fails.append(f"'{key}' is recorded unenforced with no reason. An unenforced "
                             f"element is a debt, and a debt with no reason is not recorded")
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(entry.get("since") or "")):
                fails.append(f"'{key}' is recorded unenforced with no `since` date. A debt with "
                             f"no date cannot be reviewed")
        else:
            fails.append(
                f"'{key}' has an entry with neither enforced_by nor unenforced. Silence in the "
                f"register is the same silence the register exists to end")
    return fails, []


def run(copy_path: Path, slides_dir: Path | None, *, quiet: bool = False) -> int:
    copy = json.loads(copy_path.read_text(encoding="utf-8"))
    fails, warns = check_copy(copy)
    # The register runs whether or not there is a render, because its subject is the config pair
    # and not the deck. A run that has not drawn anything yet can still be told that brand.yaml
    # grew an element nobody decided about.
    f0, w0 = check_constellation()
    fails += f0
    warns += w0
    if slides_dir and slides_dir.exists():
        f2, w2 = check_type_spine(slides_dir)
        fails += f2
        warns += w2
        f3, w3 = check_site_line(slides_dir)
        fails += f3
        warns += w3

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
    # ---- THE FOOTER, against config/brand.yaml -----------------------------------------
    # The red case is the real one: three decks shipped the owner's personal GitHub Pages host
    # on the bottom of every slide while brand.yaml named the domain. A gate that cannot go red
    # on that is not a gate, and the first draft of brand_site() returned None and passed.
    import tempfile
    want = brand_site()
    ok("brand.yaml resolves to a non-empty site string", bool(want), f"got {want!r}")
    ok("...and it is the domain rather than a github.io host",
       bool(want) and "github.io" not in want, f"got {want!r}")
    with tempfile.TemporaryDirectory() as d:
        dd = Path(d)
        (dd / "slide-01.html").write_text(f'<div class="tx-site">{want}</div>', encoding="utf-8")
        bad, _ = check_site_line(dd)
        ok("a frame printing the brand.yaml site passes", not bad, str(bad))
        (dd / "slide-02.html").write_text(
            '<div class="tx-site">talonsturgill.github.io/TexasAIDocket</div>', encoding="utf-8")
        bad, _ = check_site_line(dd)
        ok("a frame printing the old github.io host is CAUGHT", len(bad) == 1, str(bad))
        (dd / "slide-03.html").write_text("<div>no footer here</div>", encoding="utf-8")
        bad, _ = check_site_line(dd)
        ok("a frame printing no site line at all is CAUGHT", len(bad) == 2, str(bad))

    # ---- THE CONSTELLATION REGISTER ----------------------------------------------------
    #
    # The shipped pair first, because a gate that cannot go green on the real files is not
    # measuring the real files. Then each of the five red states, forced against the SHIPPED
    # brand.yaml rather than an invented one, by swapping the register for a temporary copy. A
    # fixture written on both sides would agree with itself, which is GATE_LESSONS 16.
    global REGISTER
    _real_register = REGISTER
    ok("the shipped brand.yaml and constellation.yaml agree",
       check_constellation()[0] == [], str(check_constellation()[0])[:400])
    try:
        import yaml as _yaml  # type: ignore
    except ImportError:
        _yaml = None
    ok("PyYAML is available, so the register was really parsed rather than skipped",
       _yaml is not None)
    if _yaml is not None:
        _brand_keys = sorted(((_yaml.safe_load(BRAND_YAML.read_text(encoding="utf-8")) or {})
                              .get("visual") or {}).get("constellation") or {})
        ok("brand.yaml still declares the constellation this register answers for",
           len(_brand_keys) >= 5, str(_brand_keys))
        _base = _yaml.safe_load(_real_register.read_text(encoding="utf-8"))

        def _with(elements):
            import tempfile as _tf
            fh = _tf.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8")
            fh.write(_yaml.safe_dump({"elements": elements}))
            fh.close()
            return Path(fh.name)

        def _red(label, elements, needle):
            global REGISTER
            p = _with(elements)
            REGISTER = p
            try:
                f = check_constellation()[0]
            finally:
                REGISTER = _real_register
                p.unlink()
            ok(label, any(needle in m for m in f), str(f)[:300])

        # 1. THE STATE THIS EXISTS FOR. brand.yaml fixes an element and nobody decided about it.
        _short = {k: v for k, v in _base["elements"].items() if k != _brand_keys[0]}
        _red(f"an element brand.yaml fixes with no register entry is CAUGHT ({_brand_keys[0]})",
             _short, "does not mention it")
        # 2. A register entry for a rule that was repealed reads exactly like coverage.
        _red("a register entry for an element brand.yaml no longer fixes is CAUGHT",
             dict(_base["elements"], made_up_element={"unenforced": "x", "since": "2026-08-29"}),
             "no longer fixes it")
        # 3. An entry that takes neither route.
        _red("an entry with neither enforced_by nor unenforced is CAUGHT",
             dict(_base["elements"], site={"note": "looks like an entry"}),
             "neither enforced_by nor unenforced")
        # 4. GATE_LESSONS 56. A name nobody resolved passes on a product without the feature.
        _red("an enforced_by naming a function this module does not have is CAUGHT",
             dict(_base["elements"], site={"enforced_by": "check_the_thing_i_wish_existed"}),
             "no such function")
        # 5. A debt with no date cannot be reviewed.
        _red("an unenforced entry with no since date is CAUGHT",
             dict(_base["elements"], mark={"unenforced": "a reason"}), "no `since` date")
        _red("...and one with an empty reason is CAUGHT",
             dict(_base["elements"], mark={"unenforced": "   ", "since": "2026-08-29"}),
             "no reason")
        # AND THE GREEN CASE ONE MORE TIME, through the same temporary-file path the red cases
        # use, so a pass cannot come from the swap machinery failing to take effect.
        _p = _with(_base["elements"])
        REGISTER = _p
        _f = check_constellation()[0]
        REGISTER = _real_register
        _p.unlink()
        ok("...and the unaltered register through the same path is still clean", _f == [], str(_f))
        # THE ENFORCED ROUTE POINTS AT REAL CODE, checked directly rather than inferred from the
        # green above, because "no entry used it" and "every entry resolved" look identical.
        _named = [v.get("enforced_by") for v in _base["elements"].values()
                  if isinstance(v, dict) and v.get("enforced_by")]
        ok("the register names at least one real enforcing function", len(_named) >= 2, str(_named))
        ok("...and every one of them resolves in this module",
           all(callable(globals().get(str(n))) for n in _named), str(_named))

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
