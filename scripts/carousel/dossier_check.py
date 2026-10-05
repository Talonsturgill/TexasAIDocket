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
    print("dossier_check: PyYAML missing (install requirements.txt)", file=sys.stderr)
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


# THE CRAFT PLAN (2026-10-03, the sibling product's, on the owner's instruction to give this deck
# its updates). The judges' art complaints are mostly decided in PLANNING and never written down, so
# the panel was the first to notice them. On October 2nd the craft judge named a featureless dark
# slab of coping and a bare wall, each the largest thing in its frame, a hero "under a tenth of the
# frame height on 2, 3, 4, 9", and repeated compositions. So the storyboard now declares, before
# any code, one row per frame:
#
#   ## CRAFT PLAN
#   | slide | shot | largest object, and how it is modelled |
#   |---|---|---|
#   | 01 | MEDIUM, eye level, horizon on the upper third | the parapet coping, limestone weathered dark at its joints, raking west light and grime where it meets the roof |
#   ...
#   Showstopper frame: 06, the vial at macro scale against the city in haze
#   Tonal arc: dark and quiet 01 to 03, lifts to the brightest on 06, settles on 09
#
# THE SHOT IS WHAT IS COUNTED, AND THAT IS THE ADAPTATION. The sibling holds each DRAWING TECHNIQUE
# to three frames. This deck is one hero in one material under one rig, rendered on six frames or
# more, so a technique cap would fight its own law. What ILLUSTRATION_SYSTEM.md says varies is the
# camera and the state of the hero, so each row opens with one of SHOTS and no shot carries more
# than CRAFT_PLAN_MAX_SHARE frames. A closed word list is deliberate: the sibling's free-text
# technique families took seven review rounds to stop misreading, and a camera distance is a fact
# the plan can state in one word.
CRAFT_PLAN_FROM = "2026-10-03"
CRAFT_PLAN_MAX_SHARE = 3
SHOTS = ("AERIAL", "WIDE", "MEDIUM", "CLOSE", "MACRO")
CRAFT_PLAN_HEAD_RE = re.compile(r"^##\s+CRAFT PLAN\b.*$", re.M)
_SHOT_RE = re.compile(r"^\s*(" + "|".join(SHOTS) + r")\b", re.I)

# The third cell has to say HOW the largest object is modelled, not only name it. A word list is
# crude and deliberately so: it asks for a treatment to be named at all. The sibling's list, with
# the words this deck's render uses for the same thing (weathering, grime, a kit model).
MODELLING_RE = re.compile(
    r"\b(lit|light|lighting|key[- ](?:lit|light|lighting)|rim[- ]?(?:lit|light|lighting)|raking|lee|"
    r"shad(?:e|ed|ing|ow|ows)|cast|contact|occlu\w*|specular|gloss\w*|matte|material|pbr|metal\w*|"
    r"resin|glass|depth|relief|textur\w*|grain|gradient|graded|glow|bevel\w*|emboss\w*|"
    r"model(?:l)?ed|model(?:l)?ing|volume\w*|extru\w*|three\.js|3d|aerial perspective|haze|fog|"
    r"weather\w*|grime|dirt\w*|dust\w*|worn|wear|patina|lichen|rust\w*|stain\w*|mottl\w*|"
    r"roughness|bump|normal map|kit|k\.make|txt\.weather|txt\.contact)\b", re.I)

# The cell reads "object, treatment". The treatment is what follows the object, from the first
# separator on, so an object whose own name is a treatment word ("the glass", "a light pole") is
# not read as its own modelling. No separator means only an object was named.
_TREATMENT_SEP_RE = re.compile(
    r",|;|:|\(|\s(?=(?:with|as|by|under|through|lit|drawn|rendered|model(?:l)?ed|"
    r"shaded|carved|weathered|cast|casting|on a|in a|in an)\s)", re.I)

# What makes depth, for the showstopper frame. Stricter than MODELLING_RE.
DEPTH_RE = re.compile(
    r"\b(depth|3d|pbr|three\.js|webgl|perspective|parallax|occlu\w*|cast shadow|contact shadow|"
    r"shadow|aerial|haze|fog|atmospheric|volum\w*|foreground|background|layered|horizon|sky|"
    r"distance|recession|recedes?|macro|bokeh|depth of field)\b", re.I)

_NEGATION_RE = re.compile(r"\b(no|not|without|none|zero|never|lacks?|lacking|avoids?|"
                          r"avoiding|nor|free of|omit\w*|skip\w*|n't)\b|n't\b|"
                          r"\w-free\b|\w-less\b|\b(?:shadow|depth|texture|detail|"
                          r"feature|shape|form|tone)less\b", re.I)
_CLAUSE_SPLIT_RE = re.compile(r"[,;:().]|\s(?:but|while|whereas|although|though)\s", re.I)

# A Tonal arc line that declares none is not an arc. An explicit "no arc" always fails, and a
# uniform-tone phrase fails only when the line describes no progression.
TONAL_ARC_PROGRESSION_RE = re.compile(
    r"\b(then|lifts?|rises?|climbs?|builds?|peaks?|brightens?|darkens?|brightest|"
    r"darkest|ramps?|drops?|falls?|opens?|closes?|until|towards?|settles?)\b|\bto (?:a |the )?"
    r"(?:bright|dark|light|peak|high|low)", re.I)
TONAL_ARC_NONE_RE = re.compile(
    r"^\s*(?:no|none|n/?a|tbd|todo)\b|\bno (?:tonal )?arc\b|\bwithout (?:a |any )?arc\b", re.I)
TONAL_ARC_DENIED_RE = re.compile(
    r"\b(?:same|one|single|uniform|constant|even|flat|identical|unchanging|unchanged|"
    r"unvaried|invariant|monotone|monotonous) (?:tones?|values?|key|tonality)\b|"
    r"\b(?:tones?|values?|tonality) (?:stays?|remains?|is|are) (?:the )?"
    r"(?:same|constant|uniform|flat|identical|unchanged)\b", re.I)


def _affirms(rx, text: str) -> bool:
    """True when `rx` names something in a clause nothing negates, so "no shading", "depth is not
    used" and "shadow-free" deny rather than affirm. The sibling learned each case from review."""
    return any(rx.search(c) and not _NEGATION_RE.search(c) for c in _CLAUSE_SPLIT_RE.split(text))


def _treatment(obj: str) -> str:
    """The modelling text after the object, or "" when either half is missing."""
    m = _TREATMENT_SEP_RE.search(obj)
    if not m or not re.search(r"[A-Za-z0-9]", obj[:m.start()]):
        return ""
    return obj[m.start():].strip(" ,;:(")


def craft_plan_fails(text: str, slide_nos: list) -> list[str]:
    """Every hole in the storyboard's `## CRAFT PLAN`, as one line each."""
    m = CRAFT_PLAN_HEAD_RE.search(text)
    if not m:
        return ["deck: no '## CRAFT PLAN' section. Before the build, declare each frame's shot and "
                "its largest object with how that object is modelled, the showstopper frame and "
                "the tonal arc (knowledge/carousel/SLIDE_DOSSIER_SPEC.md, THE CRAFT PLAN)"]
    nxt = re.search(r"^##\s", text[m.end():], re.M)
    block = text[m.end(): m.end() + nxt.start()] if nxt else text[m.end():]
    rows, dupes = {}, []
    for line in block.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and re.fullmatch(r"\d{1,2}", cells[0]):
            n = int(cells[0])
            if n in rows:
                dupes.append(n)
            rows[n] = (cells[1], cells[2])
    fails = []
    if dupes:
        fails.append("deck: the CRAFT PLAN has more than one row for slide(s) %s. Keep one row per "
                     "frame and edit it in place" % ", ".join("%02d" % n for n in sorted(set(dupes))))
    missing = [n for n in slide_nos if n not in rows]
    if missing:
        fails.append("deck: the CRAFT PLAN has no row for slide(s) %s"
                     % ", ".join("%02d" % n for n in missing))
    stale = sorted(set(rows) - set(slide_nos))
    if stale:
        fails.append("deck: the CRAFT PLAN has row(s) for slide(s) %s, which the storyboard doesn't "
                     "have. Remove them" % ", ".join("%02d" % n for n in stale))
    share: dict = {}
    for n, (shot, obj) in sorted(rows.items()):
        sm = _SHOT_RE.match(shot)
        if not sm:
            fails.append("deck: CRAFT PLAN slide %02d opens its shot with '%s'. Open it with one of "
                         "%s, then say the rest" % (n, shot[:30], ", ".join(SHOTS)))
        else:
            share.setdefault(sm.group(1).upper(), []).append(n)
        if not obj:
            fails.append("deck: CRAFT PLAN slide %02d names no largest object" % n)
        elif not _treatment(obj) or not _affirms(MODELLING_RE, _treatment(obj)):
            fails.append(
                "deck: CRAFT PLAN slide %02d names its largest object ('%s') and not how it is "
                "modelled. Write the object, then after a comma its material, light and contact "
                "and where it is weathered. The largest thing drawn with the least care is the "
                "judges' most repeated art complaint" % (n, obj[:60]))
    for shot, ns in sorted(share.items()):
        if len(ns) > CRAFT_PLAN_MAX_SHARE:
            fails.append(
                "deck: the CRAFT PLAN puts %d frames at %s (%s), over the %d allowed. One hero in "
                "one world is the law, so the camera is what varies. Move the extra frames closer "
                "or further" % (len(ns), shot, ", ".join("%02d" % n for n in sorted(ns)),
                                CRAFT_PLAN_MAX_SHARE))
    dm = re.search(r"^\s*[-*]?\s*Showstopper frame:\s*(\d{1,2})", block, re.M | re.I)
    if not dm:
        fails.append("deck: the CRAFT PLAN names no 'Showstopper frame: NN', the one frame planned "
                     "to pass THE SHOWSTOPPER TEST outright")
    elif int(dm.group(1)) not in slide_nos:
        fails.append("deck: the CRAFT PLAN's showstopper frame %s is not a slide in this storyboard"
                     % dm.group(1))
    else:
        dn = int(dm.group(1))
        rest = block[dm.end():].split("\n", 1)[0]
        row = rows.get(dn, ("", ""))
        if not (_affirms(DEPTH_RE, rest) or _affirms(DEPTH_RE, row[0]) or _affirms(DEPTH_RE, _treatment(row[1]))):
            fails.append("deck: the CRAFT PLAN names %02d as the showstopper frame and neither that "
                         "line nor its row says what makes its depth (haze, a horizon, contact "
                         "and cast shadow, occlusion, foreground against background)" % dn)
    ta = re.search(r"^\s*[-*]?\s*Tonal arc:\s*(\S.{10,})$", block, re.M | re.I)
    if not ta:
        fails.append("deck: the CRAFT PLAN names no 'Tonal arc:' line. A deck that strobes light to "
                     "dark to light was named by a judge on October 2nd")
    elif TONAL_ARC_NONE_RE.search(ta.group(1)) or (
            TONAL_ARC_DENIED_RE.search(ta.group(1))
            and not TONAL_ARC_PROGRESSION_RE.search(ta.group(1))):
        fails.append("deck: the CRAFT PLAN's 'Tonal arc:' declares no arc ('%s'). Say where the "
                     "deck is darkest, where it lifts and where it peaks" % ta.group(1)[:60])
    return fails


# THE ACCEPTANCE FLOOR (weekly machine pass, 2026-10-05). The pixel critic grades a frame against
# its dossier's acceptance list, and three decks running the critics said the lists would pass a
# frame missing the thing it was planned around: no. 41 (2026-10-03, rounds 1 and 2, every frame),
# no. 42 (2026-10-04, frames 2, 6, 7 and 9, "a 28 px bus passes") and no. 43 (2026-10-05, slides
# 4, 5, 7, 8 and 9, "no chair, no window structure, no lamp pool"). The instinct
# `acceptance-items-need-a-floor`, learned 2026-08-16, had been confirmed on ten dates by then and
# had never been checked by anything. Every item had a CEILING ("under a fifth of the frame",
# "within 24px", "under eight percent") or no bound at all, so rendering less always passed.
#
# Two things are now asked of each frame's list, and both are floors:
#   1. it names the CRAFT PLAN's largest object for that frame, affirmatively. The plan already
#      promises how that object is modelled, and a list that never mentions it lets the frame
#      drop it (no. 43's slide 8 planned the tower and listed only the skyline and the horizon).
#   2. one item sets a lower bound on a visible SIZE, in px or as a share of the frame, on the
#      art rather than the type: "the bus stands at least 180 px tall at 432px", "the vial owns at
#      least a third of the frame height". Rendering it small or not at all then fails it.
# A word list matches the object, deliberately crude, the way MODELLING_RE is: it asks that the
# object be named at all. Dated, so it binds the runs after the pass and never the deck that was
# mid-panel when it shipped, nor a shipped run re-checked under its own date.
ACCEPTANCE_FLOOR_FROM = "2026-10-06"

_OBJ_STOP = frozenset(
    "the a an and of with in on at to its it's their his her one two three four five six seven "
    "eight nine ten eleven twelve each every all some its frame scene world image picture thing "
    "object near far left right front back side behind beyond over under across along end "
    "small large big tall long wide square full half same other again more most few".split())
_FLOOR_WORD = (r"(?:at least|no less than|not less than|no smaller than|no shorter than|"
               r"a minimum of|minimum of|more than|over|above)")
_FRACTION = (r"(?:\d+(?:\.\d+)?\s*(?:percent|%)|(?:a |an |one )?(?:third|quarter|half|fifth|sixth|"
             r"tenth|two thirds|three quarters|two fifths))")
_SIZE_FLOOR_RE = re.compile(
    r"\b" + _FLOOR_WORD + r"\s+(?:\d+(?:\.\d+)?\s*(?:px|pixels?)\b|" + _FRACTION + r")"
    r"|\b\d+(?:\.\d+)?\s*(?:px|pixels?|percent|%)[^,;.]{0,40}?\bor (?:more|taller|wider|larger|"
    r"higher|bigger)\b", re.I)
# A size floor has to say WHAT dimension it bounds, or "at least 24px from the edge" (a margin)
# would count as a size.
_DIMENSION_RE = re.compile(r"\b(tall|wide|high|height|width|across|diameter|long|deep|size|"
                           r"area|of the frame|frame'?s)\b", re.I)
# A floor on the TYPE is not a floor on the art. Frames this defect hit had type that read fine.
_TYPE_RE = re.compile(r"\b(hook|dek|label|labels|type|text|caption|footer|counter|headline|"
                      r"letter\w*|glyph\w*|word\w*|numeral\w*|font)\b", re.I)
_ITEM_NEG = re.compile(r"\b(?:no|not|nothing|never|without|none|neither|nor)\b|n't\b", re.I)


def _stem(w: str) -> str:
    w = w.lower()
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        return w[:-1]
    return w


def _object_words(obj: str) -> set:
    """The content words of the CRAFT PLAN's largest object, the part before its treatment."""
    m = _TREATMENT_SEP_RE.search(obj)
    head = obj[:m.start()] if m and re.search(r"[A-Za-z]", obj[:m.start()]) else obj
    return {_stem(w) for w in re.findall(r"[a-z][a-z\-]+", head.lower().replace("'s", ""))
            if len(w) > 2 and w not in _OBJ_STOP}


def _items(d: dict) -> list[str]:
    acc = dig(d, "acceptance")
    items = acc if isinstance(acc, list) else ([acc] if isinstance(acc, str) else [])
    return [str(x).strip() for x in items if str(x).strip()]


# A negation can follow the object as well as precede it: "the vial is absent from the frame"
# (Codex, PR 404). Read the four words after it for a negator or an absence word.
_ITEM_ABSENT = re.compile(r"\b(?:absent|missing|gone|omitted|removed|hidden|dropped|cut)\b|out of (?:the )?frame", re.I)


def _item_names(it: str, words: set) -> bool:
    """True when `it` names one of `words` with no negator in the three words before it and no
    negator or absence word in the four after it."""
    toks = re.findall(r"[A-Za-z][A-Za-z\-']*", it)
    for i, t in enumerate(toks):
        if _stem(t.replace("'s", "").replace("'", "")) in words:
            before, after = " ".join(toks[max(0, i - 3):i]), " ".join(toks[i + 1:i + 5])
            if not _ITEM_NEG.search(before) and not _ITEM_NEG.search(after) and not _ITEM_ABSENT.search(after):
                return True
    return False


def _names_object(items: list[str], words: set) -> bool:
    """True when some item names one of `words` affirmatively (see `_item_names`)."""
    return any(_item_names(it, words) for it in items)


def has_size_floor(items: list[str], words: set | None = None) -> bool:
    """True when some item, read clause by clause, bounds a visible size of the ART from below.
    With `words`, the item carrying the floor must also name the CRAFT PLAN's largest object, so
    a floor on the bench can't vouch for a vial one pixel tall (Codex, PR 404)."""
    for it in items:
        if words and not _item_names(it, words):
            continue
        for c in _CLAUSE_SPLIT_RE.split(it):
            if _SIZE_FLOOR_RE.search(c) and _DIMENSION_RE.search(c) and not _TYPE_RE.search(c):
                return True
    return False


def craft_rows(text: str) -> dict:
    """slide number -> the CRAFT PLAN's largest object cell, or {} when there is no plan."""
    m = CRAFT_PLAN_HEAD_RE.search(text)
    if not m:
        return {}
    nxt = re.search(r"^##\s", text[m.end():], re.M)
    block = text[m.end(): m.end() + nxt.start()] if nxt else text[m.end():]
    rows = {}
    for line in block.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and re.fullmatch(r"\d{1,2}", cells[0]):
            rows[int(cells[0])] = cells[2]
    return rows


def acceptance_floor_fails(text: str, dossiers: dict[int, dict]) -> list[str]:
    """Every frame whose acceptance list a frame missing its subject would pass."""
    rows, fails = craft_rows(text), []
    for n in sorted(dossiers):
        items = _items(dossiers[n])
        if not items:
            continue                       # check_slide already reports a missing list
        obj = rows.get(n, "")
        words = _object_words(obj) if obj else set()
        if words and not _names_object(items, words):
            fails.append(
                f"slide {n}: the acceptance list never names the CRAFT PLAN's largest object "
                f"(\"{obj[:60]}\"), so a frame that drops it passes. Add an item that the frame "
                f"fails if that object is missing or unmodelled")
        if not has_size_floor(items, words):
            fails.append(
                f"slide {n}: no acceptance item sets a FLOOR on a visible size of the largest object, so rendering the "
                f"subject small, or not at all, passes. Add one in px or as a share of the frame, "
                f"on the art and not the type, e.g. \"the bus stands at least 180 px tall at "
                f"432px\" or \"the vial owns at least a third of the frame height\"")
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
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date) and date >= CRAFT_PLAN_FROM and dossiers:
        fails.extend(craft_plan_fails(board.read_text(encoding="utf-8"), sorted(dossiers)))
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date) and date >= ACCEPTANCE_FLOOR_FROM and dossiers:
        fails.extend(acceptance_floor_fails(board.read_text(encoding="utf-8"), dossiers))
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

    # THE CRAFT PLAN (2026-10-03). A good plan, then each hole the gate exists for.
    rows = [("01", "MEDIUM, eye level, horizon on the upper third",
             "the parapet coping, limestone weathered dark at its joints with grime where it meets the roof"),
            ("02", "WIDE, seated eye in the consult room",
             "the desk, walnut veneer worn at the edge, window light raking across it"),
            ("03", "CLOSE, the monitor at bench height", "the monitor, matte bezel with a contact shadow on the bench"),
            ("04", "CLOSE, the page from above at 40 degrees", "the printed page, paper grain lit from the window"),
            ("05", "MEDIUM, along the coping", "the two tape rules, vinyl with a soft specular sheen"),
            ("06", "MACRO, the vial's base", "the vial, glass with condensation and its flies in contact with the food"),
            ("07", "MEDIUM, the tray at eye level", "the vial tray, cardboard with worn corners and a cast shadow"),
            ("08", "WIDE, the city behind the vial", "the coping again, weathered and lit raking from the west"),
            ("09", "AERIAL, the roof from a drone at 40 m", "the roof, gravel ballast with dirt at the drains")]

    def plan(rs=rows, extra="Showstopper frame: 06, the vial at macro scale against the city in haze\n"
                            "Tonal arc: dark and quiet 01 to 03, lifts to the brightest on 06, settles on 09\n"):
        return ("## The world\nprose\n\n## CRAFT PLAN\n| slide | shot | largest object |\n|---|---|---|\n"
                + "".join(f"| {a} | {b} | {c} |\n" for a, b, c in rs) + extra + "\n## Next\n")
    nine = list(range(1, 10))
    ok("craft plan: a complete plan passes", craft_plan_fails(plan(), nine) == [],
       str(craft_plan_fails(plan(), nine)))
    ok("craft plan: no section at all fails", any("no '## CRAFT PLAN'" in f for f in craft_plan_fails("# x", nine)))
    f = craft_plan_fails(plan(rows[:8]), nine)
    ok("craft plan: a frame with no row fails", any("no row for slide(s) 09" in x for x in f), str(f))
    f = craft_plan_fails(plan(rows + [("10", "WIDE, x", "a thing, lit")]), nine)
    ok("craft plan: a row for a frame the storyboard lacks fails", any("10" in x and "doesn't" in x for x in f), str(f))
    f = craft_plan_fails(plan(rows + [("03", "WIDE, again", "the monitor, lit")]), nine)
    ok("craft plan: two rows for one frame fail", any("more than one row" in x for x in f), str(f))
    bad = [(a, b, "the parapet coping") if a == "01" else (a, b, c) for a, b, c in rows]
    f = craft_plan_fails(plan(bad), nine)
    ok("craft plan: a largest object named with no modelling fails, the October 2nd slab",
       any("slide 01" in x and "not how it is modelled" in x for x in f), str(f))
    bad = [(a, b, "the glass") if a == "06" else (a, b, c) for a, b, c in rows]
    ok("craft plan: an object whose own name is a treatment word is not its own modelling",
       any("slide 06" in x for x in craft_plan_fails(plan(bad), nine)))
    bad = [(a, b, "the wall, no shading and no texture") if a == "04" else (a, b, c) for a, b, c in rows]
    ok("craft plan: a negated treatment is no treatment", any("slide 04" in x for x in craft_plan_fails(plan(bad), nine)))
    bad = [(a, "WIDE" + b[b.index(","):], c) if a in ("01", "03", "05") else (a, b, c) for a, b, c in rows]
    f = craft_plan_fails(plan(bad), nine)
    ok("craft plan: one shot on more than three frames fails", any("5 frames at WIDE" in x for x in f), str(f))
    bad = [(a, "eye level" + b[b.index(","):], c) if a == "02" else (a, b, c) for a, b, c in rows]
    ok("craft plan: a shot that opens with no shot word fails",
       any("slide 02 opens its shot" in x for x in craft_plan_fails(plan(bad), nine)))
    f = craft_plan_fails(plan(extra="Tonal arc: dark 01 to 03, then lifts to a peak on 06\n"), nine)
    ok("craft plan: no showstopper frame fails", any("Showstopper frame" in x for x in f), str(f))
    f = craft_plan_fails(plan(extra="Showstopper frame: 12, in haze\nTonal arc: dark 01, then lifts to 06\n"), nine)
    ok("craft plan: a showstopper frame that is not a slide fails", any("not a slide" in x for x in f), str(f))
    f = craft_plan_fails(plan(extra="Showstopper frame: 06\nTonal arc: one tone throughout\n"), nine)
    ok("craft plan: a tonal arc that declares one tone fails", any("declares no arc" in x for x in f), str(f))
    f = craft_plan_fails(plan(extra="Showstopper frame: 06\nTonal arc: flat tone through 03, then lifts to a peak on 06\n"), nine)
    ok("craft plan: a flat stretch inside a real arc passes", f == [], str(f))

    # THE ACCEPTANCE FLOOR (weekly pass 2026-10-05). The replayed defect first: no. 43's slide 3,
    # its CRAFT PLAN row and acceptance list verbatim, which the pixel critics said would pass a
    # frame with no chair and no window structure. It names neither the desks nor any size.
    n43 = ("## CRAFT PLAN\n| slide | shot | largest object, and how it is modelled |\n|---|---|---|\n"
           "| 03 | MEDIUM, seated eye 1.2 m across a nurses' station | three desks end to end under six "
           "monitors, veneer tops worn at the edge, six screens glowing dusk gold, mesh chairs |\n")
    n43_acc = ["exactly six monitors stand on the station and all six screens glow dusk gold",
               "each leader ends within 24px of the screen it names",
               "the room stands in TXT.interior and the snapshot reports ROOM IN FRAME",
               "the frame's median L* at 432px is between 6 and 22"]
    f = acceptance_floor_fails(n43, {3: good(3, acceptance=n43_acc)})
    ok("floor: no. 43 slide 3's list is CAUGHT for never naming its largest object",
       any("largest object" in x for x in f), str(f))
    ok("floor: no. 43 slide 3's list is CAUGHT for setting no size floor",
       any("FLOOR" in x for x in f), str(f))
    fixed = n43_acc + ["the three desks run end to end and their tops span at least half the "
                       "frame width at 432px"]
    f = acceptance_floor_fails(n43, {3: good(3, acceptance=fixed)})
    ok("floor: the same list with the desks named and a floor on their width passes", f == [], str(f))
    row = "## CRAFT PLAN\n| slide | shot | largest object |\n|---|---|---|\n| 01 | CLOSE, x | the vial, glass lit from behind |\n"
    def floor(items):
        return acceptance_floor_fails(row, {1: good(1, acceptance=items)})
    base = ["the vial stands on the bench with a contact shadow", "the frame's median L* at 432px is between 20 and 40"]
    ok("floor: a share of the frame from below passes",
       floor(base + ["the vial owns at least a third of the frame height"]) == [])
    ok("floor: px from below with 'or taller' passes",
       floor(base + ["the vial reads 180 px tall or taller at 432px"]) == [])
    ok("floor: a ceiling alone is CAUGHT, 'under a fifth of the frame height'",
       any("FLOOR" in x for x in floor(base + ["the worker stands under a fifth of the frame height"])))
    ok("floor: a margin is not a size, 'at least 24px from the edge' is CAUGHT",
       any("FLOOR" in x for x in floor(base + ["the vial sits at least 24px from the edge"])))
    ok("floor: a floor on the TYPE is not a floor on the art",
       any("FLOOR" in x for x in floor(base + ["the hook is at least 90 px tall"])))
    ok("floor: a count with no size is CAUGHT, 'at least four palms'",
       any("FLOOR" in x for x in floor(base + ["at least four palms stand on the boulevard"])))
    f = floor(["no vial is in the frame", "the bench is at least half the frame width"])
    ok("floor: an object named only to deny it is CAUGHT", any("largest object" in x for x in f), str(f))
    f = floor(["the vial is absent from the frame", "the vial owns at least a third of the frame height"])
    ok("floor: a negation AFTER the object is read too, 'the vial is absent'",
       not _item_names("the vial is absent from the frame", {"vial"}) and _item_names("the vial owns at least a third of the frame height", {"vial"}), str(f))
    f = floor(["the vial is visible", "the bench owns at least half the frame width"])
    ok("floor: a floor on another object does not vouch for the largest one",
       any("FLOOR" in x for x in f), str(f))
    # the date gate: the deck mid-panel on the pass's own day and every shipped run keep their verdict
    import contextlib, io, tempfile
    with tempfile.TemporaryDirectory() as td:
        board = ("```yaml\n" + yaml.safe_dump(good(3, acceptance=n43_acc)) + "```\n\n" + n43)
        verdicts = {}
        for day in ("2026-10-05", ACCEPTANCE_FLOOR_FROM):
            (Path(td) / day).mkdir()
            (Path(td) / day / "storyboard.md").write_text(board, encoding="utf-8")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                run(day, Path(td))
            verdicts[day] = "FLOOR" in buf.getvalue()
        ok("floor: binds from %s and not on the day the pass shipped" % ACCEPTANCE_FLOOR_FROM,
           verdicts[ACCEPTANCE_FLOOR_FROM] and not verdicts["2026-10-05"], str(verdicts))

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
