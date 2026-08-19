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

# An acceptance item asserting a string is present. The quoted group is what must be rendered.
REQUIRED_STR = re.compile(
    r"\b(?:read(?:s|ing)?|carr(?:y|ies|ying)|say(?:s|ing)?|print(?:s|ing)?|set)\b[^\"']{0,40}"
    r"[\"']([^\"']{3,60})[\"']", re.I)

# An acceptance item asserting a string is absent. TWO orders, because acceptance lines are
# written both ways and the first draft of this file only matched one of them:
#   "no legend label names 'base load'"        negation BEFORE the quote
#   "the phrase 'flag red' appears nowhere"    negation AFTER it
FORBIDDEN_BEFORE = re.compile(
    r"\b(?:no|never|nowhere|not)\b[^\"']{0,60}[\"']([^\"']{3,60})[\"']", re.I)
FORBIDDEN_AFTER = re.compile(
    r"[\"']([^\"']{3,60})[\"'][^\"']{0,40}"
    r"\b(?:appears? nowhere|appears? on no|is absent|does not appear|never appears|"
    r"appears nowhere)\b", re.I)


def forbidden_needles(item: str) -> list:
    seen = []
    for rx in (FORBIDDEN_BEFORE, FORBIDDEN_AFTER):
        for m in rx.finditer(item):
            v = m.group(1).strip()
            if len(v.split()) >= 2 and v not in seen:
                seen.append(v)
    return seen

# Words that mean the item is about judgement rather than about a countable thing.
PROSE_ONLY = ("read as", "reads as", "feel", "judged", "at thumb", "by eye", "looks")


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


def check(storyboard: str, slides_dir: Path, report: dict) -> tuple:
    fails, warns, stats = [], [], {"checkable": 0, "prose": 0, "slides": 0}
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
                    needle = m.group(1).strip()
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
              f"acceptance items carry a machine-checkable assertion, and every one holds")
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
acceptance:
  - "the differing words are marked in pecos and nothing else on the frame is"
  - "the frame carries 'One office' as its display line"
  - "the phrase 'flag red' appears nowhere on the frame"
```
"""
    REPORT = {"slides": [{"file": "slide-05.html",
                          "text_nodes": [{"text": "One office. The same day. Two wordings."}]}]}

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
                          "text_nodes": [{"text": "One office. The same day. it is flag red here"}]}]}
        (dd / "slide-05.html").write_text(GOOD, encoding="utf-8")
        f, w, s = check(SB, dd, R3)
        ok("an acceptance item forbidding a string the frame prints is CAUGHT",
           any("appears nowhere" in x for x in f), str(f))

        # COVERAGE: a slide whose whole list is unfalsifiable.
        SB2 = SB.replace('  - "the differing words are marked in pecos and nothing else on the frame is"\n', "") \
                .replace("""  - "the frame carries 'One office' as its display line"\n""", "") \
                .replace("""  - "the phrase 'flag red' appears nowhere on the frame"\n""",
                         '  - "the composition reads as balanced at thumb"\n')
        (dd / "slide-05.html").write_text(GOOD, encoding="utf-8")
        f, w, s = check(SB2, dd, REPORT)
        ok("a deck whose acceptance list nothing could fail is WARNED",
           any("could contradict" in x for x in w), str(w))

    # The palette map is READ from the storyboard, never held as a constant here.
    ok("the palette is read from the storyboard rather than typed into this file",
       palette_map(SB) == {"tower": "#16151C", "pecos": "#8E4B3A", "paper": "#F6F1E4"},
       str(palette_map(SB)))
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
