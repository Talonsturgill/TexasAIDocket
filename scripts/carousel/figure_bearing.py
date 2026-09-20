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


def computed_keys(run_dir: Path) -> set[str]:
    """Every name a dossier may legitimately point `figure:` at.

    figures.json is the run's own computed values. claims.json carries `computed_values` for the
    same reason the numeral gate reads it: a figure may be computed once and named in either
    place, and a gate that knows only one of them teaches runs to route around it.
    """
    keys: set[str] = set()
    fp = run_dir / "figures.json"
    if fp.exists():
        try:
            doc = json.loads(fp.read_text(encoding="utf-8"))
            if isinstance(doc, dict):
                keys |= {k for k in doc if not k.startswith("_")}
        except json.JSONDecodeError:
            pass
    cp = run_dir / "claims.json"
    if cp.exists():
        try:
            doc = json.loads(cp.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            doc = None
        for claim in _claim_list(doc):
            cid = claim.get("id") or claim.get("claim_id")
            if cid:
                keys.add(str(cid))
            cv = claim.get("computed_values") or claim.get("computed") or {}
            if isinstance(cv, dict):
                keys |= set(cv)
    return keys


def _claim_list(doc) -> list[dict]:
    if isinstance(doc, dict):
        for k in ("claims", "items", "records"):
            if isinstance(doc.get(k), list):
                return [c for c in doc[k] if isinstance(c, dict)]
        return [v for v in doc.values() if isinstance(v, dict)]
    if isinstance(doc, list):
        return [c for c in doc if isinstance(c, dict)]
    return []


def figure_values(run_dir: Path) -> dict[str, list[float]]:
    """The numbers behind each name, so the render check can look for them in the drawing."""
    out: dict[str, list[float]] = {}
    fp = run_dir / "figures.json"
    if fp.exists():
        try:
            doc = json.loads(fp.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            doc = {}
        if isinstance(doc, dict):
            for k, v in doc.items():
                if k.startswith("_"):
                    continue
                vals = []
                if isinstance(v, dict):
                    for kk in ("value", "of", "count", "n"):
                        if isinstance(v.get(kk), (int, float)):
                            vals.append(float(v[kk]))
                elif isinstance(v, (int, float)):
                    vals.append(float(v))
                if vals:
                    out[k] = vals
    return out


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
        probs.append(f"frame {n}: data_in_art figure '{fig}' is in neither figures.json nor any "
                     f"claim's computed values. A figure the build did not compute is a number "
                     f"somebody typed, which this repo's oldest law forbids")
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
        s = f"{int(v)}" if float(v).is_integer() else f"{v}"
        if re.search(rf"(?<![\d.]){re.escape(s)}(?![\d.])", body):
            return []
    probs.append(f"frame {n}: the declared figure '{fig}' ({', '.join(str(v) for v in vals)}) "
                 f"does not appear in the frame's code outside its text. It was WRITTEN on the "
                 f"frame and not DRAWN by it, which is the declaration passing while the art it "
                 f"describes was never made")
    return probs


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

    # A FIGURE THE BUILD DID NOT COMPUTE is the law this repo already had, applied to art.
    typed = dict(good)
    typed[3] = {"slide": 3, "data_in_art": {"figure": "about_nine_thousand", "drives": "bar height"}}
    probs = check(typed, keys, 6)
    ok("a figure absent from figures.json fails",
       any("computed values" in p for p in probs), str(probs[:1]))

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
           any("WRITTEN on the frame and not DRAWN" in p for p in probs), str(probs[:2]))

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
