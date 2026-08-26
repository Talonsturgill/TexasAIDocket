#!/usr/bin/env python3
"""dossier_check.py — is the deck PLANNED, or is it nine slides of intention?

WHY THIS EXISTS

There is a sequencing hole that no amount of reviewing can close, and it produced the same defect
in the sibling product for six consecutive scored runs without once being fixed.

    The design doctrine asks for a generous quiet zone on every slide, correctly.
    The cheapest place to spend that licence is the bottom band of a top-loaded composition.
    The dossier then WRITES that empty bottom into the plan.
    The pixel critics grade each slide against ITS OWN dossier, so a slide that executed a bad
      plan passes its acceptance checklist with full marks.
    The only reviewer positioned to see it is the scorer, at the ship gate, with no budget left
      to rebuild four slides.

So every run it became a note in the field log instead of a fix. **A reviewer graded against the
plan can never catch a bad plan.** The render-time frame balance check in `qa.py` catches the
defect in the output, which is much earlier. This catches it in the PLAN, which is earlier still
and where the repair costs one paragraph instead of four rebuilds.

It reads `out/<date>/storyboard.md` and holds every dossier to the spec in
`knowledge/carousel/SLIDE_DOSSIER_SPEC.md`, which is the file this gate exists to make real:

    every slide has one, numbered, no gaps          a plan with a hole is not a plan
    the three bands are all answered                the spec says all three must have an answer
    the bottom band names something modeled         THE DEFECT ABOVE
    the jobs are distinct                           the spec says two alike means one is cuttable
    structure is reasoned, not a word               the spec says "centered" is not an answer
    every numeral says where it came from           the compute-not-generate law, at plan time
    acceptance items are checkable by looking       a vague item always passes
    `data-breather` matches a declared breather     the attribute may RATIFY a plan, never invent

WHAT IT IS NOT

It cannot tell you the plan is good. It can tell you a plan exists, covers the frame, and commits
to something a critic can grade. That is the whole of what a machine can honestly say here, and
the reason the directors room is three agents rather than a form.

    dossier_check.py --date 2026-08-12
    dossier_check.py --self-test

Exit 0 clean, 1 the plan has holes, 2 the checker could not run.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:                                                     # pragma: no cover
    print("dossier_check: PyYAML missing (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]

# The bottom band clears only by naming something with MODELED TONE in it. Flat furniture is the
# defect wearing a costume: a hairline rule and a caption across the bottom is still an empty
# bottom, and it is what a plan reaches for when it wants to look answered.
#
# MATCHED ON WORD BOUNDARIES, NOT AS SUBSTRINGS, and the sibling paid for that lesson twice. Bare
# "ground" is deliberately absent, because "the ground plane is left flat" describes the exact
# defect being hunted, and as a substring "ground" also matched "background" and cleared every
# slide with a background. The modeled ways of treating a ground are named explicitly instead.
# Word boundaries also stop "lit" matching "facility" and "3d" matching an identifier.
MODELED = (
    "anchor", "terrain", "gradient", "graded", "foreground", "relief", "hillshade", "fog",
    "haze", "atmosphere", "shadow", "light", "lit", "texture", "grain", "stipple", "dither",
    "contour", "particle", "mesh", "extrud", "depth", "volumetric", "ramp", "wash", "glow",
    "mass", "silhouette", "topograph", "noise", "scatter", "hatch", "caliche", "dust", "heat",
    "horizon", "scale bar", "leader line", "tick",
)
_MODELED_RE = re.compile("|".join(r"(?<![a-z])" + re.escape(h) + r"(?![a-z])" for h in MODELED))

# Furniture that does NOT clear the bottom band on its own.
FLAT_ONLY = ("plate", "hairline", "rule", "caption", "footer", "label", "chip", "counter",
             "logo", "wordmark", "page number")

# Emptiness described as a plan. Naming the band and then leaving it is the defect stated aloud.
EMPTY_WORDS = ("empty", "blank", "nothing", "unused", "left clear", "left open", "negative space",
               "breathing room", "dead space", "untouched", "bare")

# A bottom band plan shorter than this is a gesture, not a plan. Set from the spec's own example
# paragraphs rather than from our corpus, since no deck has shipped and measuring an empty corpus
# would produce a number that means nothing.
THIN_PLAN = 60

# The spec names these as required. Nested keys use dots.
REQUIRED = ("job", "composition.structure", "composition.bands", "composition.focal",
            "art.technique", "art.why_this_technique", "art.palette", "art.value_structure",
            "acceptance")

# An acceptance item that is a judgement rather than an observation. These always pass, which is
# the same as not being on the list.
VAGUE = ("well composed", "looks good", "looks great", "balanced", "clean", "nice", "beautiful",
         "professional", "polished", "on brand", "strong", "effective", "clear and legible",
         "visually appealing", "reads well")

MIN_ACCEPTANCE = 3


def dig(d: dict, dotted: str):
    cur = d
    for part in dotted.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def text_of(v) -> str:
    """Flatten a field to prose, so a plan written as a list reads the same as one written flat."""
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    if isinstance(v, list):
        return " ".join(text_of(x) for x in v)
    if isinstance(v, dict):
        return " ".join(f"{k} {text_of(x)}" for k, x in v.items())
    return str(v)


def parse_dossiers(raw: str) -> dict[int, dict]:
    """Read every dossier out of the storyboard.

    Fenced yaml blocks are the spec's own format. A whole-file parse is the fallback, because a
    storyboard written as one document is a reasonable thing to produce and a gate that refuses
    it teaches people to stop running the gate.
    """
    out: dict[int, dict] = {}
    blocks = re.findall(r"```(?:yaml|yml)\s*\n(.*?)```", raw, re.S | re.I)
    docs = []
    for b in blocks:
        try:
            d = yaml.safe_load(b)
        except yaml.YAMLError:
            continue
        docs.extend(d if isinstance(d, list) else [d])
    if not docs:
        try:
            d = yaml.safe_load(raw)
            docs = d if isinstance(d, list) else ([d] if isinstance(d, dict) else [])
        except yaml.YAMLError:
            docs = []
    for i, d in enumerate(docs, start=1):
        if not isinstance(d, dict):
            continue
        if "slides" in d and isinstance(d["slides"], list):
            for j, s in enumerate(d["slides"], start=1):
                if isinstance(s, dict):
                    out[int(s.get("slide") or j)] = s
            continue
        try:
            n = int(d.get("slide") or i)
        except (TypeError, ValueError):
            n = i
        out[n] = d
    return out


def bottom_clause(bands: str) -> str:
    """The part of the bands plan that talks about the bottom of the frame.

    Sentence-level rather than whole-field, because a rich top and middle would otherwise vouch
    for an empty bottom. That substitution is the whole defect: the plan reads full, and the band
    a reader's eye finishes on is the one nobody planned.
    """
    hits = []
    for part in re.split(r"(?<=[.;])\s+|\n+", bands):
        if re.search(r"(?<![a-z])(bottom|lower|base|floor|foot)(?![a-z])", part, re.I):
            hits.append(part.strip())
    return " ".join(hits)


# WHERE THE LIGHT IS, SAID TWICE. 2026-08-26.
#
# `composition.focal` and `art.value_structure` both name where the frame's light sits, in two
# fields four lines apart, and nothing compared them. Slide 2's focal said "the lit half of the
# sheet to the RIGHT of the mullion shadow" while its own value_structure said "Lightest is the
# lit wedge at the sheet's upper LEFT. Darkest is the shade core at the LOWER RIGHT". The code
# puts the light upper left. The focal line survived three review rounds and two reported
# repairs, because a pixel critic grades the render against the focal line and a craft critic
# reads the value_structure, and neither one reads both.
#
# This is the tautology lesson in reverse. `distinct_shapes` could not be false; these two fields
# could always disagree and nothing ever asked. A plan that contradicts itself is worse than a
# thin plan, because each half licenses a different frame.
_SIDE = {"left": "L", "right": "R"}
_LEVEL = {"upper": "U", "top": "U", "head": "U", "lower": "D", "bottom": "D", "foot": "D"}


def _light_words(text: str, mapping: dict) -> set:
    """The direction words in the clause about LIGHT, never the one about shade.

    A value_structure names both poles in one paragraph, so reading the whole of it would find
    every word and agree with anything. Only the lightest clause is read: from "Lightest"/"lit"
    up to the first sentence that turns to the dark half.
    """
    low = re.sub(r"\s+", " ", text.lower())
    m = re.search(r"\b(lightest|lit)\b", low)
    if not m:
        return set()
    tail = low[m.start():]
    stop = re.search(r"\b(darkest|darker|shade core|shadow core|in shade)\b", tail)
    clause = tail[:stop.start()] if stop else tail
    return {v for k, v in mapping.items() if re.search(rf"(?<![a-z]){k}(?![a-z])", clause)}


def light_disagreement(focal: str, value_structure: str) -> str:
    """The axis the two fields disagree on, or "" when they agree or one of them is silent."""
    if not focal.strip() or not value_structure.strip():
        return ""
    for axis, mapping in (("horizontally", _SIDE), ("vertically", _LEVEL)):
        a, b = _light_words(focal, mapping), _light_words(value_structure, mapping)
        # Only a CLEAN disagreement counts. A field naming both sides is describing a sweep, and
        # a field naming none is silent. Neither is a contradiction.
        if len(a) == 1 and len(b) == 1 and a != b:
            return axis
    return ""


def check_slide(n: int, d: dict, breather_rendered: bool | None) -> list[str]:
    fails = []
    for field in REQUIRED:
        if not text_of(dig(d, field)).strip():
            fails.append(f"slide {n}: missing `{field}`, which the dossier spec requires")

    structure = text_of(dig(d, "composition.structure")).strip()
    if structure and len(structure.split()) < 6:
        fails.append(f"slide {n}: `composition.structure` is \"{structure}\". The spec says a "
                     f"word is not an answer. Say why this content wants this organisation")

    bands = text_of(dig(d, "composition.bands"))
    if bands:
        named = {w: bool(re.search(rf"(?<![a-z]){w}(?![a-z])", bands, re.I))
                 for w in ("top", "middle|centre|center|mid", "bottom|lower|base|floor|foot")}
        for label, seen in zip(("top", "middle", "bottom"), named.values()):
            if not seen:
                fails.append(f"slide {n}: the bands plan never says what occupies the {label} "
                             f"third. The spec says all three must have an answer")

        bottom = bottom_clause(bands)
        if bottom:
            low = bottom.lower()
            if any(w in low for w in EMPTY_WORDS) and not _MODELED_RE.search(low):
                fails.append(f"slide {n}: the bottom third is planned as emptiness. This is the "
                             f"dead lower zone, and a critic grading against this plan will pass "
                             f"it: \"{bottom[:90]}\"")
            elif len(bottom) < THIN_PLAN:
                fails.append(f"slide {n}: the bottom third gets {len(bottom)} characters of plan. "
                             f"That is a gesture, not a treatment: \"{bottom}\"")
            elif not _MODELED_RE.search(low):
                furniture = [f for f in FLAT_ONLY if f in low]
                why = (f" It names only flat furniture ({', '.join(furniture)})."
                       if furniture else "")
                fails.append(f"slide {n}: the bottom third names nothing with modeled tone in "
                             f"it.{why} Flat furniture across the bottom is an empty bottom with "
                             f"a caption on it")

    focal = text_of(dig(d, "composition.focal"))
    vstru = text_of(dig(d, "art.value_structure"))
    axis = light_disagreement(focal, vstru)
    if axis:
        fails.append(f"slide {n}: `composition.focal` and `art.value_structure` put the light in "
                     f"opposite places {axis}. One of them describes a frame this deck does not "
                     f"render, and a critic grading against the wrong one will pass a fault. "
                     f"focal: \"{focal.strip()[:80]}\" / value_structure: \"{vstru.strip()[:80]}\"")

    acc = dig(d, "acceptance")
    items = acc if isinstance(acc, list) else ([acc] if isinstance(acc, str) else [])
    items = [str(x).strip() for x in items if str(x).strip()]
    if items and len(items) < MIN_ACCEPTANCE:
        fails.append(f"slide {n}: {len(items)} acceptance item(s). The pixel critic grades against "
                     f"this list, so a short list is a lenient critic. At least {MIN_ACCEPTANCE}")
    for it in items:
        low = it.lower()
        if any(v in low for v in VAGUE):
            fails.append(f"slide {n}: acceptance item \"{it}\" is a judgement, not something "
                         f"checkable by looking. It will always pass")

    numerals = dig(d, "numerals")
    if isinstance(numerals, list):
        for i, entry in enumerate(numerals, start=1):
            if isinstance(entry, dict) and (entry.get("value_from") or entry.get("computed_by")):
                continue
            fails.append(f"slide {n}: numeral {i} says neither `value_from` nor `computed_by`. "
                         f"Every figure traces to a claim or to the code that computed it")

    declared = bool(d.get("breather") or d.get("is_breather"))
    if breather_rendered is not None:
        if breather_rendered and not declared:
            fails.append(f"slide {n}: the slide carries `data-breather` but the dossier does not "
                         f"declare it a breather. The attribute may ratify a plan, never invent "
                         f"one, or a slide can excuse itself from the frame balance gate")
        if declared and not breather_rendered:
            fails.append(f"slide {n}: the dossier declares a breather but the slide does not "
                         f"carry `data-breather`, so the rest beat was planned and not built")
    return fails


def check(dossiers: dict[int, dict], expected: int | None,
          breathers: dict[int, bool] | None) -> list[str]:
    fails: list[str] = []
    if not dossiers:
        return ["no dossiers found. Write one per slide before any code, per the spec"]

    have = sorted(dossiers)
    if expected:
        for n in range(1, expected + 1):
            if n not in dossiers:
                fails.append(f"slide {n} rendered but has no dossier. A slide planned while it is "
                             f"being coded gets argued for rather than judged")
    for n in have[1:]:
        if n - 1 not in dossiers and not expected:
            fails.append(f"the dossiers jump from {max(x for x in have if x < n)} to {n}")

    seen: dict[str, int] = {}
    for n in have:
        job = re.sub(r"[^a-z0-9]+", " ", text_of(dossiers[n].get("job")).lower()).strip()
        if not job:
            continue
        if job in seen:
            fails.append(f"slides {seen[job]} and {n} have the same job. The spec says one of "
                         f"them is cuttable, and nine slides doing one job is one drawing nine "
                         f"times")
        else:
            seen[job] = n

    for n in have:
        fails.extend(check_slide(n, dossiers[n],
                                 (breathers or {}).get(n) if breathers is not None else None))
    return fails


def run(date: str, out_root: Path) -> int:
    d = out_root / date
    board = d / "storyboard.md"
    if not board.exists():
        print(f"dossier_check: {board} is missing. The dossiers come before the code.",
              file=sys.stderr)
        return 2

    dossiers = parse_dossiers(board.read_text(encoding="utf-8"))

    expected, breathers = None, None
    rep = d / "render" / "render_report.json"
    if rep.exists():
        try:
            report = json.loads(rep.read_text(encoding="utf-8"))
            slides = report.get("slides") or []
            expected = len(slides)
            breathers = {}
            for i, rec in enumerate(slides, start=1):
                n = rec.get("n") or rec.get("slide") or i
                breathers[int(n)] = bool(rec.get("breather"))
        except (json.JSONDecodeError, ValueError):
            pass

    fails = check(dossiers, expected, breathers)
    if not fails:
        extra = "" if breathers is not None else ", breather cross-check skipped (no render yet)"
        print(f"dossiers: {len(dossiers)} slide(s) planned, every band answered{extra}")
        return 0

    print(f"dossiers: {len(fails)} problem(s) in the plan\n")
    for f in fails:
        print(f"  {f}")
    print("\n  Fix the PLAN, not the gate. This runs before any code because that is the only\n"
          "  place these cost a paragraph. A pixel critic grades each slide against its own\n"
          "  dossier, so a bad plan executed faithfully passes every review after this one.")
    return 1


def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    def good(n=1, **over):
        d = {
            "slide": n,
            "job": f"slide {n} shows the thing only slide {n} shows",
            "composition": {
                "structure": "the figure sits on the horizon line so the reader reads the "
                             "scale before the number",
                "bands": "The top third carries the hook over open sky. The middle third holds "
                         "the county mesh. The bottom third carries a graded caliche foreground "
                         "with the scale bar sitting on it and the terrain falling away to the "
                         "right.",
                "focal": "the peak figure, pulled by the only warm value in the frame",
            },
            "art": {"technique": "hillshade over a county mesh",
                    "why_this_technique": "the claim is about where, so the where must be drawn",
                    "palette": "Big Bend dusk, sampled from the ridgeline at last light",
                    "value_structure": "lightest at the horizon, darkest in the foreground mass"},
            "acceptance": ["the peak figure is legible at 432px against the ember band",
                           "the transmission line reads as a line over terrain, not a crack",
                           "the trough label lands on the trough, within 24px"],
        }
        for k, v in over.items():
            if v is None:
                d.pop(k, None)
            elif isinstance(v, dict) and isinstance(d.get(k), dict):
                d[k] = {**d[k], **v}
            else:
                d[k] = v
        return d

    ok("a complete dossier passes", check({1: good()}, 1, None) == [], str(check({1: good()}, 1, None)))

    # THE DEFECT, in the three costumes it actually wears.
    empty = good(composition={"bands": "The top third carries the hook. The middle third holds "
                                       "the map. The bottom third is left empty as a quiet zone "
                                       "to let the frame breathe and rest the eye."})
    f = check({1: empty}, 1, None)
    ok("a bottom third planned as emptiness is CAUGHT", len(f) == 1 and "dead lower zone" in f[0],
       str(f))

    furniture = good(composition={"bands": "The top third carries the hook over open sky. The "
                                           "middle third holds the county mesh. The bottom third "
                                           "carries the hairline rule, the caption and the page "
                                           "counter across a flat plate."})
    f = check({1: furniture}, 1, None)
    ok("a bottom third of flat furniture is CAUGHT", len(f) == 1 and "modeled tone" in f[0], str(f))
    ok("...and it names the furniture it found", "hairline" in f[0], str(f))

    thin = good(composition={"bands": "Top, the hook. Middle, the map. Bottom, a rule."})
    f = check({1: thin}, 1, None)
    ok("a one-clause bottom plan is CAUGHT", len(f) == 1 and "gesture" in f[0], str(f))

    # THE SUBSTITUTION THAT MAKES THE WHOLE FIELD USELESS, and the reason the bottom is read as
    # its own clause: a lavish top must not vouch for an unplanned bottom.
    lavish = good(composition={"bands": "The top third carries a graded atmospheric wash with "
                                        "terrain relief, hillshade, fog and a lit horizon behind "
                                        "the hook. The middle third holds the mesh. The bottom "
                                        "third is left blank."})
    f = check({1: lavish}, 1, None)
    ok("a rich top third cannot vouch for an empty bottom", len(f) == 1, str(f))

    # The substring trap the sibling shipped twice.
    bg = good(composition={"bands": "Top, the hook. Middle, the mesh. The bottom third is bare, "
                                    "sitting on the background colour with nothing else on it."})
    f = check({1: bg}, 1, None)
    ok("\"background\" does not clear a bare bottom band", len(f) == 1, str(f))
    ok("...and 'lit' is not matched inside 'facility'",
       not _MODELED_RE.search("the facility is drawn flat"))

    # A missing band.
    twoband = good(composition={"bands": "The top third carries the hook. The middle third holds "
                                         "the county mesh with graded terrain behind it."})
    f = check({1: twoband}, 1, None)
    ok("a bands plan that never mentions the bottom is CAUGHT",
       any("bottom third" in x for x in f), str(f))

    # The spec's own rules.
    f = check({1: good(composition={"structure": "centered"})}, 1, None)
    ok("\"centered\" is refused as a structure", any("not an answer" in x for x in f), str(f))

    f = check({1: good(1), 2: good(2, job="slide 1 shows the thing only slide 1 shows")}, 2, None)
    ok("two slides with the same job are CAUGHT", any("same job" in x for x in f), str(f))

    f = check({1: good(acceptance=["the deck looks good", "well composed", "on brand"])}, 1, None)
    ok("vague acceptance items are CAUGHT", len([x for x in f if "judgement" in x]) == 3, str(f))

    f = check({1: good(acceptance=["the peak figure is legible at 432px"])}, 1, None)
    ok("a one-item acceptance list is CAUGHT", any("lenient critic" in x for x in f), str(f))

    f = check({1: good(numerals=[{"value_from": "c4"}, {"note": "about 8.9 gigawatts"}])}, 1, None)
    ok("a numeral with no source is CAUGHT", any("value_from" in x for x in f), str(f))
    f = check({1: good(numerals=[{"value_from": "c4"}, {"computed_by": "peak / approved"}])},
              1, None)
    ok("...and a sourced or computed numeral passes", f == [], str(f))

    for field in ("job", "art", "acceptance"):
        f = check({1: good(**{field: None})}, 1, None)
        ok(f"a missing `{field}` is CAUGHT", any("missing" in x for x in f), str(f))

    # Coverage, both ways.
    ok("a rendered slide with no dossier is CAUGHT",
       any("no dossier" in x for x in check({1: good(1)}, 2, None)))
    ok("no dossiers at all is CAUGHT", check({}, 3, None) != [])

    # The breather escape hatch, which must only ever ratify.
    f = check({1: good()}, 1, {1: True})
    ok("an undeclared breather attribute is CAUGHT", any("data-breather" in x for x in f), str(f))
    f = check({1: good(breather=True)}, 1, {1: True})
    ok("a declared and built breather passes", f == [], str(f))
    f = check({1: good(breather=True)}, 1, {1: False})
    ok("a breather planned but not built is CAUGHT", any("not carry" in x for x in f), str(f))
    f = check({1: good()}, 1, None)
    ok("the breather check is skipped, not guessed, before the render", f == [], str(f))

    # Parsing the real artifact shape.
    board = ("# Storyboard\n\nSome prose.\n\n```yaml\nslide: 1\njob: a\n```\n\n"
             "```yaml\nslide: 2\njob: b\n```\n")
    got = parse_dossiers(board)
    ok("fenced yaml blocks are read", sorted(got) == [1, 2], str(got))
    ok("...and a whole-file yaml document is read too",
       sorted(parse_dossiers("- slide: 1\n  job: a\n- slide: 2\n  job: b\n")) == [1, 2])

    # THE TWO FIELDS THAT NAME THE LIGHT (2026-08-26). Slide 2 shipped them inverted for three
    # rounds and two reported repairs, because a pixel critic grades against the focal line and a
    # craft critic reads the value_structure, and neither one reads both.
    _f_bad = ("The lit half of the sheet to the right of the mullion shadow, the frame's one "
              "large bright area.")
    _v = ("Lightest is the lit wedge at the sheet's upper left. Darkest is the shade core at the "
          "LOWER RIGHT, where the bracket doubles the occlusion.")
    ok("a focal that inverts its own value_structure is CAUGHT",
       light_disagreement(_f_bad, _v) == "horizontally", light_disagreement(_f_bad, _v))
    _f_ok = "The lit upper LEFT of the sheet, running from the head down through the first rows."
    ok("...and the corrected pair agrees", light_disagreement(_f_ok, _v) == "",
       light_disagreement(_f_ok, _v))
    ok("the DARK clause of value_structure is not read as its light clause",
       light_disagreement("The lit band at the upper left of the sheet.",
                          "Lightest is the sheet's upper left. Darkest is the lower right.") == "")
    ok("a focal naming no direction is not a disagreement",
       light_disagreement("The reflected far case's bond sheet, roughly 200 by 150.", _v) == "")
    ok("a value_structure naming no direction is not a disagreement",
       light_disagreement(_f_bad, "Lightest is the two sheets at bond. Darkest is the case lip.") == "")
    ok("an empty field is not a disagreement",
       light_disagreement("", _v) == "" and light_disagreement(_f_bad, "") == "")
    ok("a focal naming BOTH sides is a sweep, not a contradiction",
       light_disagreement("lit from the left edge across to the right margin", _v) == "")
    ok("a vertical inversion is caught on its own axis",
       light_disagreement("The lit strip along the bottom edge of the sheet.",
                          "Lightest is the sheet's upper rail. Darkest is the floor below it.")
       == "vertically")
    _bad_slide = good(composition={"focal": _f_bad}, art={"value_structure": _v})
    ok("check() surfaces it as a slide level failure",
       any("opposite places" in f for f in check({1: _bad_slide}, 1, None)),
       str(check({1: _bad_slide}, 1, None)))

    if failures:
        print(f"\ndossier_check self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print(f"\ndossier_check self-test: all passed (thin plan under {THIN_PLAN} chars, "
          f"{MIN_ACCEPTANCE} acceptance items minimum)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date")
    ap.add_argument("--out", default=str(REPO_ROOT / "out"))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.date:
        print("dossier_check: pass --date or --self-test", file=sys.stderr)
        return 2
    return run(a.date, Path(a.out))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                            # noqa: BLE001
        print(f"dossier_check: broke: {exc}", file=sys.stderr)
        sys.exit(2)
