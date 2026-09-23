#!/usr/bin/env python3
"""figure_bearing.py — THE ARTWORK CARRIES THE DATA.

WHY THIS EXISTS. 2026-09-20, the owner, on four consecutive shipped decks:

    "it keeps doing that faded look, doesnt seems like its making each run bespoke on its own
     ... the alaska one juts seems miles ahead as far as the actual coherence of the artwork,
     like it earns its way on scren, and is relevant to the story, the texas one seems
     uncoordinated still and random on the art"

THE MEASUREMENT THAT FOUND IT, because four earlier guesses about this were wrong.

Ground chroma, tonal range, ink mass and mass-under-blur were measured across 59 shipped decks of
the reference corpus and the Texas decks that keep frame PNGs. THEY ARE INDISTINGUISHABLE. Median ground chroma
0.0214 against 0.0215. Median tonal range 0.63 against 0.66. "Faded" is not a colour-space defect
and it is not a contrast defect, and any fix aimed at the palette would have been the fifth wrong
guess. The difference is not in how the frames are coloured. It is in WHAT THEY DRAW.

    The reference corpus computes its numbers and DRAWS THEM.
    This repo computed its numbers and drew a PICTURE NEXT TO THEM.

The upstream product's DESIGN_DOCTRINE section 6.3 is the rule this repo never had:

    "The field carries the data: parameters of the generative system ARE numbers from the story
     (particle count = megawatts; contour interval = years; stipple density = population). State
     the mapping in the dossier; the critic verifies it."
    "... zero anchors = wallpaper = fail."

and its SLIDE_DOSSIER_SPEC carries it as REQUIRED FIELD 8, "Data-in-art mapping", which the decks
that use it carry on all nine frames.

This repo's PRIMARY IMAGE LAW says instead that "a subject is a THING. A bus, a courthouse, a pump
jack, a person at a desk." That is a rule about DRAWING WELL and it is silent on whether the
drawing carries the argument. Seven of the ten layouts in THE TEN LAYOUTS are scene layouts that
can satisfy it while encoding nothing. So a run could pass every gate in this repo with nine
beautifully lit rooms that a reader learns nothing from, and that is what shipped:

    2026-09-17   6 of 9 frames carried no numeral at all
    2026-09-18   4 of 9
    2026-09-19   2 of 9
    2026-09-20   6 of 9

WHY IT IS A GATE AT THE STORYBOARD AND NOT ONLY AT THE RENDER. The score history says quality is
set at CONCEPTION and cannot be polished in afterwards:

    2026-09-14   7.118 in 1 round      2026-09-17   6.856 in 5 rounds
    2026-09-15   7.578 in 1 round      2026-09-18   6.800 in 6 rounds
    2026-09-16   7.492 in 1 round      2026-09-20   6.968 in 5 rounds

More rounds produced WORSE decks. A frame conceived as wallpaper is not rescued by five rounds of
better lighting, and a gate that only runs after the render can only ask for a redraw the loop
will not do. So this refuses a STORYBOARD, before a frame is drawn and while changing it is cheap,
and then verifies at the render that the declaration was executed rather than written.

WHAT IT ASKS OF A FRAME. One key, in the frame's dossier:

    data_in_art:
      figure: small_systems_of_all      # resolves in figures.json, or a claim's computed value
      drives: bar height                # the GEOMETRY the value sets, named as a drawn parameter

and at the render, that the value reaches the drawing rather than only the copy.

WHAT IT DELIBERATELY DOES NOT DO. It does not judge whether the mapping is a good idea, and it
never will, because that is the panel's job and a checker that grades taste gets ignored. It
asserts the mapping EXISTS, RESOLVES to a computed figure, and IS EXECUTED. GATE_LESSONS' oldest
shape is a rule stated in prose with nothing in between checking it, and section 6.3 of another
repo's doctrine is prose until this file reads it.

    figure_bearing.py --date 2026-09-20            storyboard and render
    figure_bearing.py --date 2026-09-20 --plan     storyboard only, before any frame is drawn
    figure_bearing.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

CONFIG = REPO / "config" / "carousel" / "figure_bearing.json"

# A `drives:` clause has to name a thing a renderer can set. This list is the grammar of drawn
# geometry rather than a vocabulary test: "it evokes the shortage" is not a parameter and
# "column height" is. Prose that names none of these is a mapping nobody can verify.
GEOMETRY_WORDS = (
    "height", "width", "length", "radius", "diameter", "angle", "rotation", "count", "number of",
    "spacing", "pitch", "density", "opacity", "alpha", "position", "offset", "scale",
    "area", "extent", "span", "thickness", "weight", "stroke", "size", "repeat", "rows",
    "columns", "marks", "dots", "bars", "ticks", "segments", "interval", "step", "fill level",
    "depth", "elevation", "coordinate", "bearing", "distance", "arc", "sweep", "gap", "margin",
    "x position", "y position", "x offset", "y offset",
)

# Matched on WORD BOUNDARIES, and the self-test is why. A bare "x" and "y" were in the list above
# until they matched the y in "the sense that the system is strained", which is precisely the
# mood-as-parameter clause this check exists to refuse. A substring test on a one letter token
# passes everything, silently, which is the shape of a gate that reports clean forever.
GEOMETRY_RE = re.compile(r"\b(" + "|".join(re.escape(w) for w in GEOMETRY_WORDS) + r")\b", re.I)


def names_geometry(drives: str) -> bool:
    return bool(GEOMETRY_RE.search(str(drives)))



def load_config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def computed_values(run_dir: Path) -> dict[str, list[float]]:
    """Every name a dossier may point `figure:` at, WITH THE NUMBER BEHIND IT.

    ONLY NAMES THAT RESOLVE TO A NUMBER (2026-09-20, review). The first cut read `computed_values`
    as a per-claim dict, which is not this repo's schema: it is a TOP LEVEL LIST of `{id, label,
    value, ...}` records, `v1` to `v7`, beside a `claims` list of `c1` to `c26` that carry text
    and no value. So the gate collected the CLAIM ids, accepted `figure: c1`, found no number for
    it, and `render_problems` returned nothing and skipped the render check IN SILENCE. Six frames
    declaring `c1` through `c6` would have made this gate green with no data in the art at all,
    which is the exact hole it exists to close.

    Both halves come from one function now. The first cut had two readers of the same files that
    could disagree about what existed, and one of them calling a figure real while the other could
    not price it is what produced the silent skip.
    """
    out: dict[str, list[float]] = {}

    def add(name, val):
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            return
        out.setdefault(str(name), []).append(float(val))

    fp = run_dir / "figures.json"
    if fp.exists():
        try:
            doc = json.loads(fp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            doc = {}
        if isinstance(doc, dict):
            for k, v in doc.items():
                if k.startswith("_"):
                    continue
                if isinstance(v, dict):
                    for kk in ("value", "of", "count", "n"):
                        add(k, v.get(kk))
                    # DOTTED NAMES RESOLVE (2026-09-23). figures.json is a block per story
                    # thread, `behind_the_meter: {units: 40, megawatts: 76}`, and dossiers name
                    # `behind_the_meter.units`. That name resolved to nothing, so `keys` came
                    # back empty, the membership test above is skipped on an empty set, and
                    # `render_problems` found no number and returned clean. Every figure in the
                    # 2026-09-23 storyboard was checked at the plan and at no render at all.
                    for kk, vv in v.items():
                        if not str(kk).startswith("_"):
                            add(f"{k}.{kk}", vv)
                else:
                    add(k, v)

    cp = run_dir / "claims.json"
    if cp.exists():
        try:
            doc = json.loads(cp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            doc = None
        for rec in _computed_records(doc):
            rid = rec.get("id") or rec.get("name") or rec.get("key")
            if rid is not None:
                add(rid, rec.get("value"))
    return out


def _computed_records(doc) -> list[dict]:
    """The computed value records. Top level list first, because that is this repo's shape."""
    out: list[dict] = []
    if not isinstance(doc, dict):
        return out
    cv = doc.get("computed_values") or doc.get("computed")
    if isinstance(cv, list):
        out += [r for r in cv if isinstance(r, dict)]
    elif isinstance(cv, dict):
        out += [{"id": k, "value": (v.get("value") if isinstance(v, dict) else v)}
                for k, v in cv.items()]
    # a per claim dict is still honoured, because another surface here may write one
    for c in doc.get("claims") or []:
        if isinstance(c, dict) and isinstance(c.get("computed_values"), dict):
            out += [{"id": k, "value": (v.get("value") if isinstance(v, dict) else v)}
                    for k, v in c["computed_values"].items()]
    return out


def computed_keys(run_dir: Path) -> set[str]:
    return set(computed_values(run_dir))


def figure_values(run_dir: Path) -> dict[str, list[float]]:
    return computed_values(run_dir)


def declaration(frame: dict) -> dict | None:
    """The frame's data_in_art clause, under any spelling this repo has used."""
    for k in ("data_in_art", "data_in_art_mapping", "figure_in_art", "data_mapping"):
        v = frame.get(k)
        if isinstance(v, dict):
            return v
        if isinstance(v, list) and v and isinstance(v[0], dict):
            return v[0]
    return None


def frame_problems(n: int, frame: dict, keys: set[str]) -> tuple[bool, list[str]]:
    """(is this frame figure bearing, why not)."""
    d = declaration(frame)
    if d is None:
        return False, []                      # silent: the deck-level count reports the shortfall
    probs = []
    fig = d.get("figure") or d.get("from") or d.get("value")
    drives = d.get("drives") or d.get("parameter") or d.get("sets")
    if not fig:
        probs.append(f"frame {n}: data_in_art names no `figure`. A mapping without a source is "
                     f"a sentence about the art rather than a property of it")
    elif keys and str(fig) not in keys:
        probs.append(f"frame {n}: data_in_art figure '{fig}' resolves to no COMPUTED NUMBER. A "
                     f"claim id carries text and a computed value carries a number, and only a "
                     f"number can set a geometry. Available: "
                     f"{', '.join(sorted(keys)) or '(none)'}")
    if not drives:
        probs.append(f"frame {n}: data_in_art names no `drives`. Say which drawn parameter the "
                     f"value sets, or no reviewer can check the drawing against it")
    elif not names_geometry(drives):
        probs.append(f"frame {n}: data_in_art drives '{drives}', which names no drawn geometry. "
                     f"A parameter a renderer can set reads like 'bar height' or 'mark count', "
                     f"never like a description of the mood the figure creates")
    return (not probs and bool(fig) and bool(drives)), probs


def render_problems(n: int, frame: dict, slides_dir: Path,
                    values: dict[str, list[float]]) -> list[str]:
    """Did the declared value reach the DRAWING, or only the copy?

    A figure stated in a headline and nowhere else is the exact defect this gate exists for, so
    the value has to appear outside the frame's text content. Text nodes are stripped before the
    search rather than the number being searched for twice, because a value that is both drawn
    and written is correct and must not be reported.
    """
    d = declaration(frame)
    if not d:
        return []
    fig = str(d.get("figure") or d.get("from") or d.get("value") or "")
    vals = values.get(fig)
    if not vals:
        return []                             # nothing numeric to look for; the plan check stands
    p = slides_dir / f"slide-{n:02d}.html"
    if not p.exists():
        return []
    raw = p.read_text(encoding="utf-8", errors="replace")
    # WHAT COUNTS AS THE DRAWING. Script and style bodies, and every tag attribute. NOT the text
    # between tags, because a figure a reader reads in a headline is exactly the frame this gate
    # is here to refuse. The first cut of this stripped every text node including script bodies,
    # so it deleted the only place drawing code can live and reported every frame as unexecuted;
    # the self-test caught it, which is the reason a gate carries one.
    parts = re.findall(r"<(?:script|style)[^>]*>(.*?)</(?:script|style)>", raw, re.S | re.I)
    parts += re.findall(r"<[^>]+>", raw)
    body = "\n".join(parts)
    probs = []
    for v in vals:
        lit = f"{int(v)}" if float(v).is_integer() else f"{v}"
        if _value_reaches_the_drawing(body, lit):
            return []
    probs.append(f"frame {n}: the declared figure '{fig}' ({', '.join(str(v) for v in vals)}) "
                 f"never reaches the drawing. It is absent from the code, or it is bound to a "
                 f"name nothing reads, which is a frame that kept the number and replaced the "
                 f"art. Use the value: derive a height, a count, a radius or a spacing from it")
    return probs


def _value_reaches_the_drawing(body: str, lit: str) -> bool:
    """Is the literal USED, or merely present?

    A LEXICAL CHECK CANNOT PROVE THE PIXELS and this one does not claim to. What it can refuse is
    the cheapest false pass, named in review on 2026-09-20: a generated frame keeps `var ACTIVE =
    4749` at the top, the artwork underneath is replaced by an unrelated room, and the old check
    reported the figure as drawn because the numeral was somewhere in the file.

    So an occurrence that is ONLY a binding counts only when something reads that binding. Any
    other occurrence, an argument, an arithmetic expression, a property, is a use. The panel and
    the pixel critic still judge whether the geometry is any good, which is theirs to judge and
    was never going to be a regex's.
    """
    hit = False
    for m in re.finditer(rf"(?<![\w.$]){re.escape(lit)}(?![\w.$])", body):
        hit = True
        pre = body[max(0, m.start() - 120):m.start()]
        bind = re.search(r"(?:var|let|const)\s+([A-Za-z_$][\w$]*)\s*=\s*$", pre)
        if bind is None:
            return True                       # used in an expression, a call, an assignment to a
        name = bind.group(1)                  # property: this is the ordinary case
        reads = len(re.findall(rf"(?<![\w.$]){re.escape(name)}(?![\w$])", body))
        if reads >= 2:                        # the binding itself, plus at least one read
            return True
    return False and hit


def check(dossiers: dict[int, dict], keys: set[str], minimum: int,
          slides_dir: Path | None = None,
          values: dict[str, list[float]] | None = None,
          distinct: int = 3) -> list[str]:
    """The floor scales DOWN to a short deck and never up.

    A nine frame deck answers to the configured floor. A five frame deck, which is what the
    degradation ladder produces, answers to five of five, and the three frame reference in
    `examples/figure-bearing/` to three of three. That is strictly HARDER per frame than six of
    nine, so shipping fewer frames is not a way around this. Without it the gate asked a three
    frame reference for six of three, which is a gate that cannot be satisfied and therefore a
    gate that gets switched off.
    """
    minimum = min(minimum, len(dossiers))
    distinct = min(distinct, len(dossiers))
    bearing, probs = 0, []
    for n in sorted(dossiers):
        ok, why = frame_problems(n, dossiers[n], keys)
        probs.extend(why)
        if ok:
            bearing += 1
            if slides_dir is not None:
                rp = render_problems(n, dossiers[n], slides_dir, values or {})
                probs.extend(rp)
                if rp:
                    bearing -= 1
    # THE CHEAPEST WAY TO PASS THIS GATE WITHOUT DOING IT is to declare one figure driving one
    # parameter on six frames, which is a deck that draws the same bar six times and has engaged
    # the story's numbers exactly once. A gate with a known trivial pass is a gate that will be
    # trivially passed, so the deck has to touch more than one number.
    used = []
    for n in sorted(dossiers):
        d = declaration(dossiers[n])
        if d and (d.get("figure") or d.get("from") or d.get("value")):
            used.append(str(d.get("figure") or d.get("from") or d.get("value")))
    if bearing >= minimum and len(set(used)) < distinct:
        probs.append(
            f"THE DECK ENGAGES {len(set(used))} FIGURE(S) AND NEEDS {distinct}. "
            f"{bearing} frames declare a mapping and they draw {sorted(set(used))}. One figure "
            f"drawn six ways is one number the artwork knows, and the deck has more than one "
            f"number in it. Reach a different figure on at least {distinct} frames")
    if bearing < minimum:
        probs.insert(0,
            f"THE ARTWORK DOES NOT CARRY THE DATA. {bearing} of {len(dossiers)} frames map a "
            f"computed figure onto drawn geometry, and this deck needs {minimum}. A frame whose "
            f"image encodes nothing is wallpaper with good lighting, however well it is drawn. "
            f"Give each short frame a `data_in_art:` naming a figure from figures.json and the "
            f"parameter it sets, and DRAW THAT, before the frame is rendered")
    return probs


def run(date: str, out_root: Path, plan_only: bool) -> int:
    run_dir = out_root / date
    board = run_dir / "storyboard.md"
    if not board.exists():
        print(f"figure_bearing: no storyboard at {board}", file=sys.stderr)
        return 1
    import dossier_check
    dossiers = dossier_check.parse_dossiers(board.read_text(encoding="utf-8"))
    if not dossiers:
        print(f"figure_bearing: no dossiers parsed from {board}", file=sys.stderr)
        return 1
    cfg = load_config()
    minimum = int(cfg["min_figure_bearing_frames"])
    keys = computed_keys(run_dir)
    slides = None if plan_only else (run_dir / "slides")
    if slides is not None and not slides.exists():
        slides = None
    probs = check(dossiers, keys, minimum, slides, figure_values(run_dir),
                  int(cfg.get("min_distinct_figures", 3)))
    if probs:
        print(f"figure_bearing: FAIL, {len(probs)} problem(s) in {board}\n", file=sys.stderr)
        for p in probs:
            print(f"  - {p}", file=sys.stderr)
        print("\n  knowledge/carousel/ILLUSTRATION_SYSTEM.md, 'THE ARTWORK CARRIES THE DATA', "
              "is the standard.", file=sys.stderr)
        return 1
    n = sum(1 for k in dossiers if frame_problems(k, dossiers[k], keys)[0])
    print(f"figure_bearing: ok, {n} of {len(dossiers)} frames draw a computed figure")
    return 0


def self_test() -> int:
    """Replays the defect and every way this gate could pass while being wrong."""
    fails = []

    def ok(label: str, cond: bool, detail: str = "") -> None:
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}" + (f"  [{detail}]" if not cond else ""))
        if not cond:
            fails.append(label)

    keys = {"small_systems_of_all", "texas_rank_of_five", "c12", "returned_87"}
    FIGS = ["small_systems_of_all", "texas_rank_of_five", "c12", "returned_87"]

    # THE DEFECT ITSELF: nine well drawn frames, none of them encoding anything.
    wallpaper = {n: {"slide": n, "layout": "FULL_BLEED",
                     "primary_image": "a pump house at ten to five"} for n in range(1, 10)}
    probs = check(wallpaper, keys, 6)
    ok("nine frames with no mapping fail", bool(probs), "passed")
    ok("...and the message names the count and the requirement",
       any("0 of 9" in p and "needs 6" in p for p in probs), str(probs[:1]))

    good = {n: {"slide": n, "data_in_art": {"figure": FIGS[n % len(FIGS)],
                                            "drives": "bar height"}} for n in range(1, 10)}
    ok("nine mapped frames pass", not check(good, keys, 6))

    six = dict(good)
    for n in (7, 8, 9):
        six[n] = {"slide": n}
    ok("six of nine meets a six-frame floor", not check(six, keys, 6))
    ok("...and five of nine does not", bool(check({**six, 6: {"slide": 6}}, keys, 6)))

    # DOTTED NAMES, 2026-09-23. A figures.json block per thread resolves `block.field`, and a
    # frame that declares one and never uses its value is refused at the render rather than
    # passed in silence because the name looked up nothing.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        rd = Path(td)
        (rd / "figures.json").write_text(json.dumps(
            {"_note": "x", "behind_the_meter": {"units": 40, "megawatts": 76, "basis": "measured"}}))
        vals = computed_values(rd)
        ok("a dotted figure name resolves to its number",
           vals.get("behind_the_meter.units") == [40.0], str(vals))
        (rd / "slides").mkdir()
        fr = {"slide": 1, "data_in_art": {"figure": "behind_the_meter.units", "drives": "the count of sets"}}
        (rd / "slides" / "slide-01.html").write_text(
            "<script>const UNITS = 40; for (let i = 0; i < UNITS; i++) add(i);</script>")
        ok("...and a frame that loops over it passes the render check",
           render_problems(1, fr, rd / "slides", vals) == [])
        (rd / "slides" / "slide-01.html").write_text("<script>draw(room);</script><h1>40 of them</h1>")
        ok("...and a frame that only WRITES it is refused rather than skipped",
           bool(render_problems(1, fr, rd / "slides", vals)))

    # A FIGURE THE BUILD DID NOT COMPUTE is the law this repo already had, applied to art.
    typed = dict(good)
    typed[3] = {"slide": 3, "data_in_art": {"figure": "about_nine_thousand", "drives": "bar height"}}
    probs = check(typed, keys, 6)
    ok("a figure absent from figures.json fails",
       any("no COMPUTED NUMBER" in p for p in probs), str(probs[:1]))

    # THE MAPPING HAS TO NAME GEOMETRY. This is the half a prose rule cannot hold.
    mood = dict(good)
    mood[4] = {"slide": 4, "data_in_art": {"figure": "c12",
                                           "drives": "the sense that the system is strained"}}
    probs = check(mood, keys, 6)
    ok("a `drives` naming no drawn parameter fails",
       any("names no drawn geometry" in p for p in probs), str(probs[:1]))
    for word in ("mark count", "column height", "stipple density", "arc sweep"):
        got = check({**good, 4: {"slide": 4,
                                 "data_in_art": {"figure": "c12", "drives": word}}}, keys, 6)
        ok(f"...and '{word}' is accepted", not got, str(got[:1]))

    # HALF A DECLARATION IS NOT A DECLARATION.
    for missing, needle in (({"drives": "bar height"}, "names no `figure`"),
                            ({"figure": "c12"}, "names no `drives`")):
        probs = check({**good, 2: {"slide": 2, "data_in_art": missing}}, keys, 6)
        ok(f"a mapping missing one half fails ({needle})",
           any(needle in p for p in probs), str(probs[:1]))

    # THE RENDER HALF: a declaration the drawing never executed.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        sl = Path(td)
        vals = {f: [3579.0 + i] for i, f in enumerate(FIGS)}
        for n in range(1, 10):
            v = vals[FIGS[n % len(FIGS)]][0]
            (sl / f"slide-{n:02d}.html").write_text(
                f"<html><body><canvas></canvas><script>bar({int(v)}*0.4)</script></body></html>",
                encoding="utf-8")
        ok("a value used in the drawing passes the render check",
           not check(good, keys, 6, sl, vals))

        v5 = int(vals[FIGS[5 % len(FIGS)]][0])
        (sl / "slide-05.html").write_text(
            f"<html><body><h1>{v5} of them serve fewer than 3,301 people.</h1>"
            "<script>drawRoom()</script></body></html>", encoding="utf-8")
        probs = check(good, keys, 6, sl, vals)
        ok("a value only WRITTEN on the frame fails the render check",
           any("never reaches the drawing" in p for p in probs), str(probs[:2]))

        # A frame that draws the value AND writes it is correct and must not be reported.
        (sl / "slide-05.html").write_text(
            f"<html><body><h1>{v5} systems</h1><script>bar({v5})</script></body></html>",
            encoding="utf-8")
        ok("...and a value both drawn and written is not reported",
           not check(good, keys, 6, sl, vals))

    # ONE FIGURE DRAWN SIX WAYS IS ONE NUMBER THE ARTWORK KNOWS.
    same = {n: {"slide": n, "data_in_art": {"figure": "c12", "drives": "bar height"}}
            for n in range(1, 10)}
    probs = check(same, keys, 6)
    ok("one figure on every frame is refused", bool(probs), "it passed")
    ok("...and the message says how many figures the deck engages",
       any("ENGAGES 1 FIGURE" in p for p in probs), str(probs[:1]))
    two = dict(same)
    two[1] = {"slide": 1, "data_in_art": {"figure": "returned_87", "drives": "mark count"}}
    ok("two distinct figures is still refused", bool(check(two, keys, 6)))
    three = dict(two)
    three[2] = {"slide": 2, "data_in_art": {"figure": "texas_rank_of_five",
                                            "drives": "ring radius"}}
    ok("...and three distinct figures passes", not check(three, keys, 6),
       str(check(three, keys, 6)[:1]))
    ok("the distinct rule does not fire on a deck already under the frame floor",
       not any("ENGAGES" in p for p in check({1: same[1]}, keys, 6)))

    # THE FLOOR SCALES TO A SHORT DECK, AND ONLY DOWNWARDS.
    three = {n: {"slide": n, "data_in_art": {"figure": FIGS[n], "drives": "mark count"}}
             for n in range(0, 3)}
    ok("a three frame deck with all three mapped passes", not check(three, keys, 6))
    two_of_three = dict(three)
    two_of_three[2] = {"slide": 2}
    ok("...and two of three does not", bool(check(two_of_three, keys, 6)))
    ok("...so a short deck is HARDER per frame, never a way around the floor",
       bool(check({**{n: {"slide": n} for n in range(0, 5)},
                   0: three[0], 1: three[1], 2: three[2]}, keys, 6)))

    # ONLY NAMES THAT RESOLVE TO A NUMBER. A claim id carries text and cannot set a geometry,
    # and accepting one made the render check skip in silence.
    import tempfile as _t2
    with _t2.TemporaryDirectory() as td:
        rd = Path(td)
        (rd / "claims.json").write_text(json.dumps({
            "claims": [{"id": "c1", "text": "a sentence"}, {"id": "c2", "text": "another"}],
            "computed_values": [{"id": "v1", "value": 4749}, {"id": "v2", "value": 3579},
                                {"id": "v3", "value": 87}],
        }), encoding="utf-8")
        got = computed_keys(rd)
        ok("a top level computed_values LIST is read", {"v1", "v2", "v3"} <= got, str(sorted(got)))
        ok("...and claim ids are NOT offered as figures", not ({"c1", "c2"} & got), str(sorted(got)))
        ok("...and each carries its number", computed_values(rd).get("v1") == [4749.0],
           str(computed_values(rd).get("v1")))
        probs = check({n: {"slide": n, "data_in_art": {"figure": f"c{n}", "drives": "bar height"}}
                       for n in range(1, 10)}, got, 6)
        ok("a deck declaring claim ids is refused",
           any("no COMPUTED NUMBER" in p for p in probs), str(probs[:1]))

    # THE VALUE HAS TO BE USED, not merely present. A frame that keeps `var ACTIVE = 4749` and
    # replaces the artwork underneath used to pass on lexical presence alone.
    for label, body, want in (
        ("used through a binding", "<script>var A = 4749; bar(A / 50)</script>", True),
        ("used in an expression",  "<script>bar(4749 * 0.4)</script>", True),
        ("a binding nothing reads", "<script>var A = 4749;</script><script>room()</script>", False),
        ("absent entirely",        "<script>room()</script>", False),
    ):
        ok(f"render check: {label}", _value_reaches_the_drawing(body, "4749") is want)

    # THE CONFIG IS REAL AND THE FLOOR IS THE ONE IN IT.
    try:
        cfg = load_config()
        ok("config/carousel/figure_bearing.json carries a floor",
           isinstance(cfg.get("min_figure_bearing_frames"), int))
        ok("...and the floor is derived rather than asserted",
           bool(cfg.get("derived_from")), "no derived_from")
    except Exception as exc:                                    # noqa: BLE001
        ok("config loads", False, str(exc))

    # AND IT REFUSES THE DECKS THAT ACTUALLY SHIPPED. A gate whose self-test only exercises
    # fixtures has never been pointed at the product, which is GATE_LESSONS' recurring shape.
    import dossier_check
    for date, want in (("2026-09-17", True), ("2026-09-20", True)):
        d = REPO / "runs" / "carousel" / date
        if not (d / "storyboard.md").exists():
            continue
        ds = dossier_check.parse_dossiers((d / "storyboard.md").read_text(encoding="utf-8"))
        got = bool(check(ds, computed_keys(d), int(load_config()["min_figure_bearing_frames"])))
        ok(f"the shipped {date} deck is refused", got is want, "it passed")

    print(f"\nfigure_bearing self-test: {'FAIL' if fails else 'ok'}, {len(fails)} failure(s)")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date")
    ap.add_argument("--out-root", default=None,
                    help="defaults to runs/carousel, so a shipped deck can be re-judged")
    ap.add_argument("--plan", action="store_true",
                    help="storyboard only, for use before a frame is drawn")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.date:
        ap.error("--date or --self-test")
    root = Path(a.out_root) if a.out_root else (REPO / "runs" / "carousel")
    if not (root / a.date).exists() and (REPO / "out" / a.date).exists():
        root = REPO / "out"
    return run(a.date, root, a.plan)


if __name__ == "__main__":
    sys.exit(main())
