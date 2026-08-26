#!/usr/bin/env python3
"""plan_render_check.py — the plan has to describe the frame that shipped.

WHY THIS EXISTS. Three runs, roughly fifteen incidents, one mechanism.

`dossier_check.py` proves a plan EXISTS and is well formed. It says so in its own docstring:
it validates FORMAT, never CORRESPONDENCE. A pixel critic then grades each frame against that
plan. So a plan that was never executed, or that went stale after a rewrite, passes every
review that comes after it, and the only reader who ever notices is a scorer at the ship gate
with no budget left to rebuild a slide.

WHAT SHIPPED THROUGH THAT HOLE

  2026-08-16  slide 2   the declared palette was never drawn. The state fill was not the oak
                        the plan named, so at feed size the silhouette was a stain.
  2026-08-16  slide 8   the declared focal, a ground line, was an unstroked colour change, and
                        its lit cut face and depth scale were never drawn at all.
  2026-08-16  s4 and s6 two acceptance items were satisfiable by rendering NOTHING.
  2026-08-18  slide 5   all five acceptance items passed while the frame read as a Gantt chart
                        that contradicted its own caption.
  2026-08-18  slide 9   printed a word its own first acceptance item forbids.
  2026-08-19  slide 5   THE WORST ONE. The dossier says the words that differ between the two
                        wordings are marked in pecos. Five scoring passes shipped uniform ink,
                        on the frame the whole deck turns on.
  2026-08-19  slide 3   the dossier demanded at least two empty swatches. The frame shipped
                        three NAMED categories, and the categories were fabricated.
  2026-08-19  slide 2   the dossier states the rate holds at 46 pixels per day, measured. Both
                        bars shipped 9px short, encoding 3.80 and 15.80 days.
  2026-08-19  slide 7   the dossier's hook and dek never shipped in any form.

THE FIFTH KIND, ADDED 2026-08-21, AND THE DEFECT IS THE WHOLE ARGUMENT FOR IT

`build_slides.py` refused that run's build. `_footer_fit` did its job exactly, naming a slide 9
byline 72px too wide for its frame, and it printed that to a stream the caller had suppressed
with `>/dev/null 2>&1` and never read the exit code of. The PREVIOUS build's HTML was still in
`out/<date>/slides/`, so the renderer rendered it, every gate in the suite passed on it, and
three scoring judges graded a deck that had never been built. Two repairs the run believed it
had shipped existed only in `storyboard.md`.

This file passed too, because none of the four kinds above reads the words. It compared
palettes and acceptance items on a frame whose display copy was a day stale.

  DECLARED    every string the dossier's `type:` block declares must be on the frame. `hook`
              and `dek` FAIL, because those are the deck's assertions and the reader's first
              two lines. Everything else the block declares WARNS, because that is furniture
              and a byline, where the difference is usually one character of punctuation that
              was repaired on the frame and not back in the plan.

Replayed across every deck this project has shipped it is silent on 2026-08-20 and 2026-08-21,
and it names real drift on two older ones: 2026-08-19 slide 3 planned "No provider was to be
told by the 7th" and shipped "No service provider was to be told by the 7th", and slide 6
planned "the sector's membership body" and shipped "the Data Center Coalition".

WHAT THIS CHECKS, AND WHAT IT DELIBERATELY DOES NOT

A machine cannot read a frame and say whether it is good. It CAN read a plan, pull out the
assertions that are about something countable, and go and look. Four kinds, chosen because
they are the four that actually broke:

  PALETTE     `art.palette` names colour tokens in prose. The storyboard defines those tokens
              as hex once. Every token a slide's palette NAMES must appear in that slide's
              rendered source. This is the 2026-08-16 slide 2 and 2026-08-19 slide 5 defect,
              and it is the cheapest true statement in the whole dossier to verify.

  REQUIRED    an acceptance item that says a frame READS or CARRIES a quoted string. The
              string has to be in the rendered text.

  FORBIDDEN   an acceptance item that says a quoted string appears NOWHERE. It has to be
              absent from the rendered text.

  COVERAGE    a slide whose entire acceptance list contains nothing checkable. This is the
              2026-08-16 and 2026-08-18 defect in its general form: a list of items that no
              render could ever fail is not a test, it is a description. This WARNS rather
              than fails, because plenty of true acceptance items are genuinely about
              judgement and should stay prose.

THE HONEST LIMIT, stated because a gate that oversells itself is worse than no gate. This
proves a declared colour was used SOMEWHERE on the frame, not that it was used on the right
element. Slide 5's pecos could satisfy this by tinting one hairline. It closes the distance
between "the plan said pecos and the frame has no pecos in it at all", which is what actually
shipped five times, and it does not close the distance to "marked correctly".

THE HONEST LIMIT ON `DECLARED`, which is a different one and is worth its own paragraph. It can
only compare a string the PLAN declares. The 2026-08-21 defect had two halves and this catches
one of them: slide 4's dek is declared under `type:` and slide 9's source line is not declared
anywhere, so a source line that names the wrong body is still invisible here. The coverage
count is printed on success for that reason, and a deck whose dossiers declare no display
string at all FAILS rather than reporting clean, because a comparison that compared nothing is
the shape `sources_block` shipped for a whole run behind an exit code of 0.

    plan_render_check.py --date 2026-08-19
    plan_render_check.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# A `name #RRGGBB` pair in the storyboard's palette section. One definition, read never typed.
PALETTE_DEF = re.compile(r"`([a-z][a-z ]*?) (#[0-9A-Fa-f]{6})`")

# A QUOTED STRING, AND AN APOSTROPHE IS NOT ONE. 2026-08-26.
#
# The first draft wrote the delimiters as `["\']...["\']`, which accepts a `"` opened and a `'`
# closed, and lets a POSSESSIVE open a quote. Slide 7's acceptance line reading "all four title
# cells carry their applicant\'s name, because the county\'s own matter titles hold four" was
# therefore read as requiring the frame to print the string `s name, because the county`, and the
# gate failed a correct frame over a plan sentence that quotes nothing at all.
#
# Two rules fix the class. The marks must MATCH, via a backreference. And a mark glued to a word
# character on the inside is punctuation in a word, never a delimiter: `\w'` cannot open and `'\w`
# cannot close. Double quotes are unaffected, which is what every real quoted acceptance item
# here uses.
_Q = r"(?<!\w)([\"'])([^\"']{3,60})\1(?!\w)"

# An acceptance item asserting a string is present. Group 2 is what must be rendered.
REQUIRED_STR = re.compile(
    r"\b(?:read(?:s|ing)?|carr(?:y|ies|ying)|say(?:s|ing)?|print(?:s|ing)?|set)\b[^\"']{0,40}"
    + _Q, re.I)

# An acceptance item asserting a string is absent. TWO orders, because acceptance lines are
# written both ways and the first draft of this file only matched one of them:
#   "no legend label names 'base load'"        negation BEFORE the quote
#   "the phrase 'flag red' appears nowhere"    negation AFTER it
FORBIDDEN_BEFORE = re.compile(
    r"\b(?:no|never|nowhere|not)\b[^\"']{0,60}" + _Q, re.I)
FORBIDDEN_AFTER = re.compile(
    _Q + r"[^\"']{0,40}"
    r"\b(?:appears? nowhere|appears? on no|is absent|does not appear|never appears|"
    r"appears nowhere)\b", re.I)


def forbidden_needles(item: str) -> list:
    seen = []
    for rx in (FORBIDDEN_BEFORE, FORBIDDEN_AFTER):
        for m in rx.finditer(item):
            v = m.group(2).strip()
            if len(v.split()) >= 2 and v not in seen:
                seen.append(v)
    return seen

# Words that mean the item is about judgement rather than about a countable thing.
PROSE_ONLY = ("read as", "reads as", "feel", "judged", "at thumb", "by eye", "looks")


# THE LIBRARY A DOSSIER NAMES MUST BE IN THE SLIDE. 2026-08-26.
#
# Round 10's craft judge read slide 1's dossier, which declared "Zdog scene, rounded extrusion
# with a real depth axis" and argued for it at length on the ground that "Zdog has never shipped
# on this product", then opened slide-01.html and found it loads noise.js and nothing else and
# builds the whole case out of axis-aligned fillRects. No Zdog, no depth axis, no three quarter
# camera. It had stood for three rounds and every gate was green, because the one artifact a
# craft judge grades a frame against is the one artifact nothing checked.
#
# This is cheap and certain: a dossier that names a drawing library by name is making a claim
# about the slide's own <script> tags, and those are readable. Named narrowly, one entry per
# library this engine can actually load, so the check cannot widen into taste.
LIBRARIES = {
    "zdog": "zdog",
    "d3": "d3",
    "topojson": "topojson",
    "three.js": "three",
    "threejs": "three",
    "taichi": "taichi",
    "matter": "matter",
    "rough": "rough",
}


def declared_libraries(body: str) -> list:
    """Library names a dossier's art block claims, lowercased.

    ONLY the `technique` field, which is the DECLARATION. The rationale beside it is discussion,
    and reading it turned this gate's own repair into a new finding: the corrected slide 1 block
    explains that the frame draws "no Zdog, no depth axis and no three quarter view", and a gate
    reading that prose recorded a claim to both Zdog and three.js. Prose about what did not ship
    is not a claim that it did.

    `technique` is written as a one line quoted scalar and `section()` only reads block scalars,
    so both forms are read here.
    """
    m = re.search(r'^\s*technique:\s*"([^"]*)"', body, re.M)
    low = ((m.group(1) if m else "") + " " + section(body, "technique")).lower()
    return sorted({k for k in LIBRARIES if re.search(rf"(?<![a-z.]){re.escape(k)}(?![a-z])", low)})


def slide_sources(html: str) -> str:
    """Every src the slide loads, plus its inline script, as one lowercased haystack."""
    return " ".join(re.findall(r"<script[^>]*>", html, re.I)).lower() + " " + html.lower()

def parse_dossiers(storyboard: str) -> dict:
    """Slide number to its YAML-ish block. Same fenced form dossier_check reads."""
    out = {}
    for n, body in re.findall(r"```yaml\s*\nslide:\s*(\d+)\s*\n(.*?)```", storyboard, re.S):
        out[int(n)] = body
    return out


def palette_map(storyboard: str) -> dict:
    """Token name to hex, from the storyboard's own palette section.

    Read, never typed. A constant here would be a second copy of a fact that already has a
    home, which is the shape that put the wrong URL on three decks.
    """
    out = {}
    for name, hexv in PALETTE_DEF.findall(storyboard):
        name = name.strip().lower()
        if " " not in name:
            out[name] = hexv.upper()
    return out


def section(body: str, key: str) -> str:
    """The prose under `key: >` in one dossier block."""
    m = re.search(rf"^  {re.escape(key)}:\s*>\s*\n((?:    .*\n)+)", body, re.M)
    return m.group(1) if m else ""


def acceptance_items(body: str) -> list:
    m = re.search(r"^acceptance:\s*\n((?:  - .*\n)+)", body, re.M)
    if not m:
        return []
    return [re.sub(r'^\s*-\s*"?|"?\s*$', "", ln).strip()
            for ln in m.group(1).splitlines() if ln.strip().startswith("- ")]


def rendered_text(report: dict, n: int) -> str:
    for s in report.get("slides") or []:
        if f"{n:02d}" in str(s.get("file", "")):
            return " ".join(str(t.get("text", "")) for t in (s.get("text_nodes") or []))
    return ""


def rendered_nodes(report: dict, n: int) -> list:
    for s in report.get("slides") or []:
        if f"{n:02d}" in str(s.get("file", "")):
            return [str(t.get("text", "")) for t in (s.get("text_nodes") or []) if t.get("text")]
    return []


# The two keys whose drift is an assertion drifting. Everything else `type:` declares is
# furniture or a byline and warns. Named here rather than inferred, and the list is the FAIL
# severity only: every key the block declares is compared, so a dossier that invents a key name
# is examined rather than skipped. That is GATE_LESSONS 39, where `copy_sync_check` selected by
# an allowlist of key names and could not see twelve of one deck's nineteen keys.
ASSERTING_KEYS = ("hook", "dek")

# `key: "value"` and `key: ["a", "b"]` inside the `type:` block. Two spaces of indent, which is
# the form SLIDE_DOSSIER_SPEC.md prints and every dossier that has ever declared one has used.
TYPE_SCALAR = re.compile(r'^  ([a-z_][a-z_0-9]*):\s*"(.*)"\s*$')
TYPE_LIST = re.compile(r'^  ([a-z_][a-z_0-9]*):\s*\[(.*)\]\s*$')


def squash(s: str) -> str:
    """Case folded with EVERY space removed, and the reason is measured rather than guessed.

    `render.py` joins a text node's child spans with no separator, so a hook broken across two
    spans for line control comes back from the render report as "August 7thcame and went." A
    substring test that collapses whitespace instead of removing it reports that correct frame
    as a missing hook. Replayed over the five shipped decks, collapsing produced 14 false
    failures on 2026-08-16 alone and removing produces none.
    """
    s = (s or "").replace('\\"', '"').replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", "", s).lower()


def declared_strings(body: str) -> list:
    """[(key, string)] the dossier's `type:` block says will be on the frame."""
    m = re.search(r"^type:\s*\n(.*?)(?=^\S|\Z)", body, re.S | re.M)
    if not m:
        return []
    out = []
    for line in m.group(1).splitlines():
        sm = TYPE_SCALAR.match(line)
        if sm:
            out.append((sm.group(1), sm.group(2)))
            continue
        lm = TYPE_LIST.match(line)
        if lm:
            for v in re.findall(r'"([^"]*)"', lm.group(2)):
                out.append((lm.group(1), v))
    # A one or two character label is furniture a squash test cannot distinguish from noise.
    return [(k, v) for k, v in out if len(v.strip()) >= 3]


def nearest(needle: str, nodes: list) -> str:
    """The rendered string closest to what the plan declared, so the message names the drift.

    A failure reading "the plan says X and the frame does not print it" sends a run looking at
    nine frames. One reading "the frame prints Y instead" is one edit. This is diagnostic and
    decides nothing: the pass or fail was already settled by the exact test above it.
    """
    import difflib
    best, score = "", 0.0
    for node in nodes:
        r = difflib.SequenceMatcher(None, squash(needle), squash(node)).ratio()
        if r > score:
            best, score = node, r
    return best if score >= 0.5 else ""


def check(storyboard: str, slides_dir: Path, report: dict) -> tuple:
    fails, warns, stats = [], [], {"checkable": 0, "prose": 0, "slides": 0,
                                   "declared": 0, "silent_slides": []}
    pal = palette_map(storyboard)
    dossiers = parse_dossiers(storyboard)
    if not dossiers:
        return ([], ["plan_render_check: no fenced slide dossiers found, nothing compared"], stats)
    if not pal:
        warns.append("plan_render_check: the storyboard defines no `name #HEX` palette, so the "
                     "declared-colour check could not run")

    for n, body in sorted(dossiers.items()):
        stats["slides"] += 1
        html_p = slides_dir / f"slide-{n:02d}.html"
        html = html_p.read_text(encoding="utf-8").upper() if html_p.exists() else ""
        text = rendered_text(report, n)

        # ---- PALETTE: a colour the plan names must be somewhere on the frame ----------
        prose = section(body, "palette").lower()
        for token, hexv in pal.items():
            if not re.search(rf"\b{re.escape(token)}\b", prose):
                continue
            if html and hexv not in html:
                fails.append(
                    f"slide {n}: the dossier's palette names {token} ({hexv}) and the frame "
                    f"does not contain that colour anywhere. A declared colour that was never "
                    f"drawn is the 2026-08-19 slide 5 defect, where the plan said the differing "
                    f"words are marked in pecos and five passes shipped uniform ink")

        # ---- DECLARED: the words the plan says will be on the frame -------------------
        # THE 2026-08-21 DEFECT. A refused build left the previous build's HTML on disk, the
        # renderer rendered it, and the plan's repaired copy never reached a pixel.
        nodes = rendered_nodes(report, n)
        declared = declared_strings(body)
        if not declared:
            stats["silent_slides"].append(n)
        for key, want in declared:
            stats["declared"] += 1
            if not text:
                continue
            stats["compared"] = stats.get("compared", 0) + 1
            if squash(want) in squash(text):
                continue
            near = nearest(want, nodes)
            instead = f" The frame prints {near!r} in its place." if near else ""
            where = "FAIL" if key in ASSERTING_KEYS else "warn"
            msg = (f"slide {n}: the dossier declares {key} as {want!r} and the render does not "
                   f"carry that string.{instead} A plan the frame did not execute is what let a "
                   f"refused build ship stale HTML to three scoring judges on 2026-08-21")
            (fails if where == "FAIL" else warns).append(msg)

        # ---- THE DECLARED LIBRARY HAS TO BE IN THE SLIDE ------------------------------
        if html:
            hay = slide_sources(html)
            for lib in declared_libraries(body):
                token = LIBRARIES[lib]
                if not re.search(rf"(?<![a-z]){re.escape(token)}(?![a-z])", hay):
                    fails.append(
                        f"slide {n}: the dossier's art block names {lib} and slide-{n:02d}.html "
                        f"never loads it. A technique nobody executed is a plan a craft critic "
                        f"grades the frame against, and slide 1 carried a Zdog scene it never "
                        f"drew for three rounds with every gate green")

        # ---- ACCEPTANCE: the items that assert something countable --------------------
        checkable_here = 0
        for item in acceptance_items(body):
            low = item.lower()
            if any(p in low for p in PROSE_ONLY):
                stats["prose"] += 1
                continue
            hit = False
            for needle in forbidden_needles(item):
                hit = True
                if text and needle.lower() in text.lower():
                    fails.append(
                        f"slide {n}: an acceptance item says {needle!r} appears nowhere on this "
                        f"frame, and the render prints it")
            if not hit:
                for m in REQUIRED_STR.finditer(item):
                    needle = m.group(2).strip()
                    if len(needle.split()) < 2:
                        continue
                    hit = True
                    if text and needle.lower() not in text.lower():
                        fails.append(
                            f"slide {n}: an acceptance item says the frame carries {needle!r} "
                            f"and the render does not print it")
            if hit:
                checkable_here += 1
                stats["checkable"] += 1
            else:
                stats["prose"] += 1
        if acceptance_items(body) and checkable_here == 0:
            stats.setdefault("blind_slides", []).append(n)

    # A COMPARISON THAT COMPARED NOTHING IS NOT A CLEAN COMPARISON. Both halves fail, and
    # neither is a warning, because the failure mode of this whole class of gate is that its
    # empty case and its clean case print the same line. 2026-08-18's dossiers carry no `type:`
    # block at all, so this gate would have reported that deck clean on a question it never
    # asked. SLIDE_DOSSIER_SPEC.md has required `type.hook` and `type.dek` since it was written.
    if stats["declared"] == 0:
        fails.append(
            "not one dossier in this storyboard declares a display string under `type:`, so "
            "nothing the reader will actually read was compared against the frames. "
            "knowledge/carousel/SLIDE_DOSSIER_SPEC.md requires `type.hook` and `type.dek`")
    elif not stats.get("compared"):
        fails.append(
            f"the storyboard declares {stats['declared']} display string(s) and the render "
            f"report carries no text for any slide, so none of them was compared. A render "
            f"report that describes no frames is a build that did not happen")
    elif stats["silent_slides"]:
        warns.append(
            f"slide(s) {', '.join(str(x) for x in stats['silent_slides'])} declare no display "
            f"string under `type:`, so their words were compared against nothing")

    # COVERAGE, reported ONCE for the deck rather than once per frame. Eight identical warnings
    # is noise, and a warning a reader learns to scroll past protects nothing.
    total = stats["checkable"] + stats["prose"]
    if total and stats["checkable"] == 0:
        warns.append(
            f"not one of this deck's {total} acceptance items asserts anything a render could "
            f"contradict. They are written as prose about the frame rather than as claims about "
            f"it, so no gate could check them even in principle and the pixel critic is the only "
            f"reader they have. This is how 2026-08-18's slide 5 passed all five of its own items "
            f"while reading as a Gantt chart that contradicted its own caption. "
            f"knowledge/carousel/SLIDE_DOSSIER_SPEC.md says how to write a checkable one")
    elif stats.get("blind_slides"):
        warns.append(
            f"slide(s) {', '.join(str(x) for x in stats['blind_slides'])} carry no acceptance "
            f"item a render could contradict")
    return fails, warns, stats


def run(date: str, quiet: bool = False) -> int:
    out = REPO_ROOT / "out" / date
    sb = out / "storyboard.md"
    rp = out / "render" / "render_report.json"
    if not sb.exists():
        print(f"plan_render_check: no storyboard at {sb}", file=sys.stderr)
        return 1
    report = json.loads(rp.read_text(encoding="utf-8")) if rp.exists() else {}
    fails, warns, stats = check(sb.read_text(encoding="utf-8"), out / "slides", report)
    for w in warns:
        print(f"  warn  {w}", file=sys.stderr)
    if fails:
        print(f"\nplan_render_check: {len(fails)} frame(s) do not match their own plan\n",
              file=sys.stderr)
        for f in fails:
            print(f"  - {f}", file=sys.stderr)
        return 1
    if not quiet:
        total = stats["checkable"] + stats["prose"]
        print(f"plan_render_check: {stats['slides']} slide(s), {stats['checkable']} of {total} "
              f"acceptance items carry a machine-checkable assertion, and every one holds. "
              f"{stats.get('compared', 0)} of {stats['declared']} declared display string(s) "
              f"were found on their own frame")
    return 0


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    bad = 0

    def ok(label, cond, extra=""):
        nonlocal bad
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            bad += 1

    SB = """
Palette line: `tower #16151C` and `pecos #8E4B3A` and `paper #F6F1E4`.

```yaml
slide: 5
job: >
  the inversion
composition:
  focal: >
    the marked words
art:
  palette: >
    paper ground with ink type. The words that differ between the two wordings are marked in
    pecos, which clears contrast on paper.
type:
  hook: "One office. The same day."
  dek: "Two wordings."
  labels: ["05 / 09", "PARALLAX"]
acceptance:
  - "the differing words are marked in pecos and nothing else on the frame is"
  - "the frame carries 'One office' as its display line"
  - "the phrase 'flag red' appears nowhere on the frame"
```
"""
    REPORT = {"slides": [{"file": "slide-05.html",
                          "text_nodes": [{"text": "One office. The same day."},
                                         {"text": "Two wordings."},
                                         {"text": "05 / 09"}, {"text": "PARALLAX"}]}]}

    import tempfile
    with tempfile.TemporaryDirectory() as d:
        dd = Path(d)

        # THE REAL 2026-08-19 DEFECT. The plan says pecos, the frame has none.
        (dd / "slide-05.html").write_text(
            "<style>.q{color:#23202B}</style><div>One office. The same day. Two wordings.</div>",
            encoding="utf-8")
        f, w, s = check(SB, dd, REPORT)
        ok("a frame whose plan declares pecos and draws none is CAUGHT",
           any("pecos" in x and "does not contain" in x for x in f), str(f))

        # ...and the repaired frame passes.
        GOOD = ("<style>.d{color:#8E4B3A}.p{background:#F6F1E4}</style>"
                "<div>One office. The same day. Two wordings.</div>")
        (dd / "slide-05.html").write_text(GOOD, encoding="utf-8")
        f, w, s = check(SB, dd, REPORT)
        ok("...and the same frame with pecos actually drawn passes", not f, str(f))
        ok("the checkable acceptance items were counted", s["checkable"] >= 1, str(s))

        # A REQUIRED string the render does not print.
        R2 = {"slides": [{"file": "slide-05.html",
                          "text_nodes": [{"text": "Something else entirely."}]}]}
        f, w, s = check(SB, dd, R2)
        ok("an acceptance item naming a string the frame does not print is CAUGHT",
           any("does not print it" in x for x in f), str(f))

        # A FORBIDDEN string the render does print. 2026-08-18 slide 9 shape.
        R3 = {"slides": [{"file": "slide-05.html",
                          "text_nodes": [{"text": "One office. The same day."},
                                         {"text": "Two wordings. it is flag red here"},
                                         {"text": "05 / 09"}, {"text": "PARALLAX"}]}]}
        (dd / "slide-05.html").write_text(GOOD, encoding="utf-8")
        f, w, s = check(SB, dd, R3)
        ok("an acceptance item forbidding a string the frame prints is CAUGHT",
           any("appears nowhere" in x for x in f), str(f))

        # ---- DECLARED, the 2026-08-21 defect and every way it can go wrong ------------
        (dd / "slide-05.html").write_text(GOOD, encoding="utf-8")

        # THE DEFECT ITSELF. The plan carries a repaired hook and the frame is the stale build.
        STALE = {"slides": [{"file": "slide-05.html",
                             "text_nodes": [{"text": "One office. The same week."},
                                            {"text": "Two wordings."},
                                            {"text": "05 / 09"}, {"text": "PARALLAX"}]}]}
        f, w, s = check(SB, dd, STALE)
        ok("a hook that lives only in the plan is CAUGHT",
           any("declares hook" in x for x in f), str(f))
        ok("...and the failure names what the frame printed instead",
           any("The same week." in x for x in f), str(f))

        # A DEK is an assertion and fails. A LABEL is furniture and warns, because the drift
        # there is a comma repaired on the frame and not in the plan, which is what 2026-08-21
        # slide 5's byline actually is.
        NODEK = {"slides": [{"file": "slide-05.html",
                             "text_nodes": [{"text": "One office. The same day."},
                                            {"text": "05 / 09"}, {"text": "PARALLAX"}]}]}
        f, w, s = check(SB, dd, NODEK)
        ok("a dek that never reached the frame is CAUGHT",
           any("declares dek" in x for x in f), str(f))
        NOLABEL = {"slides": [{"file": "slide-05.html",
                               "text_nodes": [{"text": "One office. The same day."},
                                              {"text": "Two wordings."},
                                              {"text": "05 / 09"}, {"text": "ORTHOGRAPHIC"}]}]}
        f, w, s = check(SB, dd, NOLABEL)
        ok("a label that drifted WARNS rather than failing",
           not f and any("declares labels" in x for x in w), f"fails={f} warns={w}")

        # A HOOK BROKEN ACROSS TWO SPANS is what render.py actually returns, with no space at
        # the join. Measured on 2026-08-19 slide 1, which shipped correctly and reads
        # "August 7thcame and went." in the report. A gate that fails that is a gate nobody runs.
        SPLIT = {"slides": [{"file": "slide-05.html",
                             "text_nodes": [{"text": "One office.The same day."},
                                            {"text": "Two wordings."},
                                            {"text": "05 / 09"}, {"text": "PARALLAX"}]}]}
        f, w, s = check(SB, dd, SPLIT)
        ok("...and a hook the renderer joined without a space still passes", not f, str(f))

        # THE EMPTY CASE IS NOT THE CLEAN CASE. 2026-08-18's dossiers declare no `type:` block.
        SB_NOTYPE = re.sub(r"type:\n(?:  .*\n)+", "", SB)
        f, w, s = check(SB_NOTYPE, dd, REPORT)
        ok("a storyboard that declares no display string at all FAILS",
           any("declares a display string" in x for x in f), str(f))
        f, w, s = check(SB, dd, {"slides": []})
        ok("...and declared strings with nothing rendered to compare them to FAILS",
           any("none of them was compared" in x for x in f), str(f))

        # COVERAGE: a slide whose whole list is unfalsifiable.
        SB2 = SB.replace('  - "the differing words are marked in pecos and nothing else on the frame is"\n', "") \
                .replace("""  - "the frame carries 'One office' as its display line"\n""", "") \
                .replace("""  - "the phrase 'flag red' appears nowhere on the frame"\n""",
                         '  - "the composition reads as balanced at thumb"\n')
        (dd / "slide-05.html").write_text(GOOD, encoding="utf-8")
        f, w, s = check(SB2, dd, REPORT)
        ok("a deck whose acceptance list nothing could fail is WARNED",
           any("could contradict" in x for x in w), str(w))

    # AGAINST THE REAL ARTIFACT, not only against a fixture this file wrote. GATE_LESSONS 50:
    # a checker that classifies a thing must assert its classification against the thing. The
    # `type:` block is written by hand every run, so the day a storyboard spells it differently
    # this parser starts finding nothing and would otherwise report every deck clean forever.
    shipped = sorted((REPO_ROOT / "runs" / "carousel").glob("2*")) \
        if (REPO_ROOT / "runs" / "carousel").is_dir() else []
    newest = next((p for p in reversed(shipped) if (p / "storyboard.md").exists()), None)
    if newest is not None:
        ds = parse_dossiers((newest / "storyboard.md").read_text(encoding="utf-8"))
        keys = {k for b in ds.values() for k, _v in declared_strings(b)}
        ok(f"the newest shipped storyboard ({newest.name}) declares display strings this "
           f"parser can read", {"hook", "dek"} <= keys, f"found keys {sorted(keys)}")

    # The palette map is READ from the storyboard, never held as a constant here.
    ok("the palette is read from the storyboard rather than typed into this file",
       palette_map(SB) == {"tower": "#16151C", "pecos": "#8E4B3A", "paper": "#F6F1E4"},
       str(palette_map(SB)))
    # THE DECLARED LIBRARY (2026-08-26). Slide 1 carried a Zdog scene it never drew, for three
    # rounds, with every gate green, because nothing read the dossier against the slide.
    _zdog = ('art:\n  technique: "Zdog scene, rounded extrusion with a real depth axis"\n'
             '  why_this_technique: >\n    Zdog builds it natively in vector.\n')
    ok("a dossier naming Zdog is seen to name it", declared_libraries(_zdog) == ["zdog"],
       str(declared_libraries(_zdog)))
    ok("...and a slide loading only noise.js does not satisfy it",
       "zdog" not in slide_sources('<script src="@@ASSETS@@/js/noise.js"></script>'))
    ok("...while a slide that loads it does",
       "zdog" in slide_sources('<script src="@@ASSETS@@/js/zdog.dist.js"></script>'))
    ok("a dossier naming no library declares none",
       declared_libraries('art:\n  technique: "flat elevation, axis aligned rects"\n') == [])
    ok("d3 and topojson are each their own claim",
       declared_libraries('art:\n  technique: "d3 geoAlbers over topojson counties"\n')
       == ["d3", "topojson"])
    ok("a word merely containing a library name is not a claim",
       declared_libraries('art:\n  technique: "three quarter camera on a threaded rod"\n') == [])

    # A POSSESSIVE IS NOT A QUOTE (2026-08-26). The loose delimiters failed a correct frame.
    _poss = ("all four title cells carry their applicant's name, because the county's own "
             "matter titles hold four")
    ok("a possessive apostrophe does not open a required string",
       not [m.group(2) for m in REQUIRED_STR.finditer(_poss)],
       str([m.group(2) for m in REQUIRED_STR.finditer(_poss)]))
    ok("...and a real single quoted needle is still read",
       [m.group(2) for m in REQUIRED_STR.finditer("the frame carries 'base load' at the foot")]
       == ["base load"])
    ok("...and a double quoted needle is still read",
       [m.group(2) for m in REQUIRED_STR.finditer('the frame reads "two public hearings" plainly')]
       == ["two public hearings"])
    ok("mismatched marks are not a quote",
       not [m.group(2) for m in REQUIRED_STR.finditer("""the frame carries "base load' here""")])
    ok("a possessive does not create a forbidden needle either",
       not forbidden_needles("no cell carries the county's own internal matter number"))
    ok("...while a real forbidden needle still fires",
       forbidden_needles("no legend label names 'base load'") == ["base load"])

    ok("no hex literal for a brand colour is hardcoded in this module",
       not re.search(r"#(16151C|8E4B3A|D9CDB4|B98D46|4E6B62|EFE9DA)",
                     Path(__file__).read_text(encoding="utf-8").split("def self_test")[0], re.I))

    print("\nplan_render_check self-test: " + ("all passed" if not bad else f"{bad} FAILED"))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.date:
        ap.error("--date or --self-test")
    return run(a.date)


if __name__ == "__main__":
    raise SystemExit(main())
