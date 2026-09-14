#!/usr/bin/env python3
"""scene_bounds.py — the subject the plan named, and whether the camera put it in the frame.

THE DEFECT THIS EXISTS FOR (2026-09-14, carousel no. 24, frame 1)

The cover's whole argument was true scale: a 130 m data hall broadside with one 1.70 m person
beside it, so a reader could measure the building against a body. Its first cut placed that
person at world X -13 at Z 9. The frame's own camera is `f: 820` at a 1080 px canvas, and
`TXSCENE.project` is `x = w/2 + f * X / Z`, so she rendered at x -644. **She was 644 px off the
left edge of the picture and the frame's entire argument was missing.**

`layout_check --require`, `qa.py`, `plan_render_check`, `craft_floor`, `bespoke_check` and a
pixel critic all passed it. Two of the three scoring judges found it independently, on a round
that was already carrying three other frames, and closing it cost three scoring rounds.

**Every gate in this suite measures what IS inside the declared rect. Not one asks whether a
thing the dossier NAMED is inside it at all.** A frame with a person missing is not a frame with
a defect in it; it is a different frame, and every measurement taken of it is correct.

WHY THIS IS CHECKABLE AT ALL, WHICH IS THE QUESTION THAT DECIDED THE SHAPE

`render_report.json` carries text nodes, canvas variance and canvas means, and no object
geometry whatsoever. There is nothing in it that could answer this, and finding a 44 px stippled
figure in a night scene by reading the PNG is a detector this project can neither calibrate on 13
slides nor defend when it misreports. Both routes were refused.

The slide HTML answers it exactly, because the deck draws in metres on a declared camera:

    var cam = { w: W, h: H, eye: 1.65, horizon: 940, f: 820, ... };
    var hand = TXFIG.figure({ pose: "stand", height: 1.70 });
    S.sprite(hand, { X: -9.2, Z: 27, ... });

Every term is a literal in the source. So the projection is arithmetic on committed text, it is
the SAME arithmetic the engine runs (`assets/js/txscene.js`), and it needs no model, no
dependency and no pixels. The gate reads the slides this run archived.

WHY FIGURES AND NOTHING ELSE

A figure is the one object whose real size is declared at the call site (`height:` in metres,
defaulting to 1.7) rather than built inside `TXOBJ`, and it is the object a scale argument is
made of. It is also never scatter: the same deck legitimately places a mesquite at X -58 Z 62,
which projects to x -227 and is off the frame on purpose and harms nothing. Widening this to
every sprite would fire on that, and a gate that fires on a correct decision gets switched off.

WHAT IT CANNOT SEE, SAID HERE SO NOBODY INFERS A GUARANTEE

  - A placement whose X or Z is computed at draw time (a crowd scattered by an rng, a figure
    positioned off a variable this file cannot resolve). Those are REPORTED BY NAME and counted,
    never silently skipped, because a checker whose empty case prints its clean line is not a
    checker. GATE_LESSONS 51.
  - A figure inside the canvas but underneath the type reserve, which is a different question.
  - Whether the figure was DRAWN. This reads the plan of the picture, not the picture.

THE SECOND QUESTION, AND WHY IT REPORTS RATHER THAN FAILS

The same three numbers give the figure's rendered height, `f * height / Z`. Dossier acceptance
items state that height in pixels, and on this same deck three of them were unreachable when
they were written: frame 6 asked for figures "between 92 and 108 px" behind a fence its own
dossier puts at Z 11, where no standing 1.7 m figure can be smaller than 127 px. The shipped
render is 174, 153 and 143 px, so the frame missed its own acceptance item by 60 per cent and
every gate was green.

That half PRINTS AND DECIDES NOTHING, and the reason is that it compares a computed number to a
sentence. A `sit` or `lean` pose draws shorter than its declared height, a band may be describing
one figure of three, and the corpus that could calibrate it is 13 slides. `verbatim_check`'s
style-group discovery is the precedent and its wording is the right one: a detector too noisy to
fail on is not too noisy to read. The findings go in the run record, not in an exit code.

    scene_bounds.py --date 2026-09-14        the run in out/
    scene_bounds.py --run 2026-09-14         a shipped run under runs/carousel/
    scene_bounds.py --all                    every shipped run that archived its slides
    scene_bounds.py --self-test
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS = REPO_ROOT / "runs" / "carousel"
OUT = REPO_ROOT / "out"

# A standing body is about half a metre across the shoulders. HALF the width is used as the
# horizontal margin, and 0.5 m of it rather than 0.25, because this decides whether a figure is
# ENTIRELY outside the frame and every metre of doubt should keep a finding from being raised.
# At the 2026-09-14 cover's own camera that margin is 46 px against a miss of 644, so the
# question this gate answers is never close to the margin.
BODY_HALF_WIDTH_M = 0.5

# The engine's own default, read from assets/js/txfig.js line "var H = o.height || 1.7".
DEFAULT_FIGURE_HEIGHT_M = 1.7

NUM = r"-?\d+(?:\.\d+)?(?:[eE]-?\d+)?"


# --------------------------------------------------------------------------- reading the slide
def script_only(src: str) -> str:
    """Blank everything outside a <script> block, preserving every byte offset.

    THIS IS NOT TIDINESS AND IT COST A MEASUREMENT. The first cut ran the JS stripper over the
    whole HTML file, and an apostrophe in the slide's own prose ("the operator's") opened a
    string that swallowed the rest of the document. Two slides came back with no camera and no
    figure and the gate said so honestly, which is the only reason it was found rather than
    passing. The body of a slide is prose and the scene is script, so read the script.
    """
    out = [" " if c != "\n" else "\n" for c in src]
    for m in re.finditer(r"<script[^>]*>(.*?)</script\s*>", src, re.S | re.I):
        for i in range(m.start(1), m.end(1)):
            out[i] = src[i]
    return "".join(out)


def strip_js(src: str) -> str:
    """Blank comments and string bodies, preserving every byte offset.

    Offsets are preserved on purpose. The brace walk below runs on the stripped text and the
    findings quote the original, so the two must stay in register. Blanking rather than deleting
    is `aggregate_check`'s own fix for the same problem one gate over.
    """
    src = script_only(src)
    out: list[str] = []
    i, n, mode = 0, len(src), None
    while i < n:
        c = src[i]
        if mode is None:
            if src.startswith("//", i):
                mode, i = "line", i + 2
                out.append("  ")
                continue
            if src.startswith("/*", i):
                mode, i = "block", i + 2
                out.append("  ")
                continue
            if c in "\"'`":
                mode, i = c, i + 1
                out.append(" ")
                continue
            out.append(c)
            i += 1
        elif mode == "line":
            out.append("\n" if c == "\n" else " ")
            if c == "\n":
                mode = None
            i += 1
        elif mode == "block":
            if src.startswith("*/", i):
                mode, i = None, i + 2
                out.append("  ")
                continue
            out.append("\n" if c == "\n" else " ")
            i += 1
        else:
            if c == "\\":
                out.append("  ")
                i += 2
                continue
            if c == mode:
                mode = None
            out.append(" ")
            i += 1
    return "".join(out)


def _object_at(src: str, i: int) -> str:
    """src[i] is '{'. Return the whole balanced literal."""
    depth = 0
    for j in range(i, len(src)):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return src[i:j + 1]
    return src[i:]


def _enclosing_object(src: str, at: int) -> str | None:
    depth = 0
    for k in range(at, -1, -1):
        if src[k] == "}":
            depth += 1
        elif src[k] == "{":
            if depth == 0:
                return _object_at(src, k)
            depth -= 1
    return None


def _key(obj: str, name: str) -> float | None:
    m = re.search(r"\b" + name + r"\s*:\s*(" + NUM + r")\s*[,}]", obj)
    return float(m.group(1)) if m else None


def cameras(src: str) -> list[dict]:
    """Every `TXSCENE.create` camera literal in the file, by its own three keys.

    A camera is the object carrying `horizon`, `eye` and `f` together. Matching on the three keys
    rather than on the variable name is deliberate: the decks spell it `cam`, `CAM` and inline
    inside the `create` call, and a name list would have to grow every time a writer picked a
    different word.
    """
    found, seen = [], set()
    for m in re.finditer(r"\bhorizon\s*:", src):
        obj = _enclosing_object(src, m.start())
        if not obj or obj in seen:
            continue
        h, e, f = _key(obj, "horizon"), _key(obj, "eye"), _key(obj, "f")
        if h is None or e is None or f is None:
            continue
        seen.add(obj)
        found.append({"horizon": h, "eye": e, "f": f,
                      "w": _key(obj, "w"), "h": _key(obj, "h")})
    return found


def canvas_size(src: str) -> tuple[float, float]:
    """`var W = 1080, H = 1350;` as the deck writes it, falling back to the house canvas."""
    w = re.search(r"\bW\s*=\s*(" + NUM + r")\b", src)
    h = re.search(r"\bH\s*=\s*(" + NUM + r")\b", src)
    return (float(w.group(1)) if w else 1080.0, float(h.group(1)) if h else 1350.0)


def figures(src: str) -> dict[str, dict]:
    """Variable name to declared figure. `var hand = TXFIG.figure({ height: 1.70, pose: ... })`."""
    out: dict[str, dict] = {}
    for m in re.finditer(r"\b(\w+)\s*=\s*TXFIG\.figure\s*\(\s*\{", src):
        obj = _object_at(src, m.end() - 1)
        # The POSE is recorded and deliberately not acted on. `strip_js` blanks its string value,
        # so all this can know is whether one was given, and a `sit` figure draws shorter than
        # its declared height. That is the whole reason the band half reports rather than fails.
        out[m.group(1)] = {
            "height": _key(obj, "height") or DEFAULT_FIGURE_HEIGHT_M,
            "declared_height": _key(obj, "height") is not None,
            "pose_given": bool(re.search(r"\bpose\s*:", obj)),
            "seat": _key(obj, "seat"),
        }
    return out


def _scalars(src: str) -> dict[str, float]:
    """`var DX = 0.4;` and the like, for placements written as `X: DX + 0.5`."""
    out: dict[str, float] = {}
    for m in re.finditer(r"\b(\w+)\s*=\s*(" + NUM + r")\s*[,;]", src):
        out.setdefault(m.group(1), float(m.group(2)))
    return out


def _points(src: str) -> dict[str, tuple[float, float]]:
    """`var RATER = { X: -2.1, Z: 8.4 };`, for placements written as `X: RATER.X`."""
    out: dict[str, tuple[float, float]] = {}
    for m in re.finditer(r"\b(\w+)\s*=\s*\{", src):
        obj = _object_at(src, m.end() - 1)
        x, z = _key(obj, "X"), _key(obj, "Z")
        if x is not None and z is not None:
            out.setdefault(m.group(1), (x, z))
    return out


def _resolve(expr: str, scalars: dict[str, float], points: dict[str, tuple[float, float]],
             axis: str) -> float | None:
    # `axis` selects the member of a named point, `RATER.X` against `RATER.Z`. It is read from
    # the expression itself below rather than from this argument, which is kept because the two
    # call sites read better naming which coordinate they are asking for.
    """A placement coordinate as written, or None when it is computed at draw time.

    Three forms and no more: a literal, a named point's axis, and either of those plus or minus a
    literal. Anything else is UNRESOLVED and is reported as such. Guessing at a fourth form is how
    a checker starts answering a question it was not asked.
    """
    e = expr.strip()
    m = re.fullmatch(r"(" + NUM + r")", e)
    if m:
        return float(m.group(1))
    m = re.fullmatch(r"(\w+)\.(X|Z)", e)
    if m and m.group(1) in points:
        return points[m.group(1)][0 if m.group(2) == "X" else 1]
    m = re.fullmatch(r"(\w+)", e)
    if m and m.group(1) in scalars:
        return scalars[m.group(1)]
    m = re.fullmatch(r"(.+?)\s*([+-])\s*(" + NUM + r")", e)
    if m:
        base = _resolve(m.group(1), scalars, points, axis)
        if base is not None:
            return base + (float(m.group(3)) if m.group(2) == "+" else -float(m.group(3)))
    return None


def _tables(src: str) -> list[tuple[str, list[list[str]], str]]:
    """Array-of-rows placement tables: `[[f1, -3.6, 8.2, ...], ...].forEach(function (p) {...})`.

    Carousel no. 24's frame 6 places its three figures this way, which is the frame carrying the
    unreachable acceptance band, so a parser that could not read it would have been blind on the
    one frame the second half of this gate exists for. The row INDICES are read out of the
    forEach body rather than assumed: `S.sprite(p[0], { X: p[1], Z: p[2] })` says which column is
    the sprite and which are the coordinates, so this resolves a binding rather than guessing a
    convention.
    """
    out = []
    for m in re.finditer(r"\[\s*\[", src):
        arr = _bracket_at(src, m.start())
        if arr is None:
            continue
        tail = src[m.start() + len(arr):]
        fe = re.match(r"\s*\.\s*forEach\s*\(\s*function\s*\(\s*(\w+)\s*\)\s*\{", tail)
        if not fe:
            continue
        var = fe.group(1)
        body = _object_at(tail, tail.index("{", fe.end() - 1))
        rows = [r for r in _split_top(arr) if r.strip().startswith("[")]
        out.append((var, rows, body))
    return out


def _bracket_at(src: str, i: int) -> str | None:
    depth = 0
    for j in range(i, len(src)):
        if src[j] == "[":
            depth += 1
        elif src[j] == "]":
            depth -= 1
            if depth == 0:
                return src[i:j + 1]
    return None


def _split_top(text: str) -> list[str]:
    """Split on commas at depth zero. Rows of a table, arguments of a call."""
    text = text.strip()
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]
    parts, depth, cur = [], 0, []
    for c in text:
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        if c == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(c)
    if "".join(cur).strip():
        parts.append("".join(cur))
    return [p.strip() for p in parts]


def placements(src: str, figs: dict[str, dict]) -> tuple[list[dict], list[str]]:
    """Every `S.sprite(<figure>, { X: .., Z: .. })` in the file, resolved or named as unresolved.

    `S.shadow` is deliberately NOT read. It draws the same figure's ground shadow from the same
    coordinates, so reading both would double every finding and say nothing new.
    """
    scalars, points = _scalars(src), _points(src)
    resolved: list[dict] = []
    unresolved: list[str] = []

    tables = _tables(src)
    for var, rows, body in tables:
        m = re.search(r"\.\s*sprite\s*\(\s*" + re.escape(var) + r"\s*\[\s*(\d+)\s*\]\s*,\s*\{",
                      body)
        if not m:
            continue
        si = int(m.group(1))
        opts = _object_at(body, m.end() - 1)
        xi = re.search(r"\bX\s*:\s*" + re.escape(var) + r"\s*\[\s*(\d+)\s*\]", opts)
        zi = re.search(r"\bZ\s*:\s*" + re.escape(var) + r"\s*\[\s*(\d+)\s*\]", opts)
        if not (xi and zi):
            continue
        for row in rows:
            cells = _split_top(row)
            if si >= len(cells) or cells[si].strip() not in figs:
                continue
            name = cells[si].strip()
            x = _resolve(cells[int(xi.group(1))], scalars, points, "X") \
                if int(xi.group(1)) < len(cells) else None
            z = _resolve(cells[int(zi.group(1))], scalars, points, "Z") \
                if int(zi.group(1)) < len(cells) else None
            if x is None or z is None:
                unresolved.append(f"{name} placed from a table row this gate cannot read")
            else:
                resolved.append({"name": name, "X": x, "Z": z, **figs[name]})

    for m in re.finditer(r"\b\w*\.\s*sprite\s*\(\s*([\w.\[\]]+)\s*,\s*\{", src):
        target = m.group(1)
        obj = _object_at(src, m.end() - 1)
        base = target.split("[")[0].split(".")[0]
        if target not in figs:
            # a figure reached through a variable (`f.sprite`, `p[0]`) is a placement this gate
            # can see EXISTS and cannot resolve. Reported, never dropped.
            if base not in figs and re.search(r"\b(fig|figure|crowd|person|people)\b", target, re.I):
                unresolved.append(f"{target} is a figure reached indirectly")
            continue
        xs = re.search(r"\bX\s*:\s*([^,}]+)", obj)
        zs = re.search(r"\bZ\s*:\s*([^,}]+)", obj)
        if not (xs and zs):
            unresolved.append(f"{target} placed with no literal X and Z")
            continue
        x = _resolve(xs.group(1), scalars, points, "X")
        z = _resolve(zs.group(1), scalars, points, "Z")
        if x is None or z is None:
            unresolved.append(f"{target} placed at X {xs.group(1).strip()} "
                              f"Z {zs.group(1).strip()}, computed at draw time")
        else:
            resolved.append({"name": target, "X": x, "Z": z, **figs[target]})
    return resolved, unresolved


def indirect_figures(src: str) -> int:
    """`TXFIG.figure(...)` built inline inside an array or a loop, never bound to a name."""
    named = len(re.findall(r"\b\w+\s*=\s*TXFIG\.figure\s*\(", src))
    return len(re.findall(r"\bTXFIG\.(?:figure|crowd)\s*\(", src)) - named


# --------------------------------------------------------------------------- the arithmetic
def project_x(cam: dict, X: float, Z: float, w: float) -> float:
    """assets/js/txscene.js: `return [w / 2 + f * X / Z, horizon - f * (Y - eye) / Z]`."""
    return w / 2.0 + cam["f"] * X / max(0.05, Z)


def ground_y(cam: dict, Z: float) -> float:
    """assets/js/txscene.js: `horizon + f * eye / Math.max(0.05, Z)`."""
    return cam["horizon"] + cam["f"] * cam["eye"] / max(0.05, Z)


def height_px(cam: dict, h_m: float, Z: float) -> float:
    return cam["f"] * h_m / max(0.05, Z)


def box_of(cam: dict, p: dict, w: float) -> tuple[float, float, float, float]:
    x = project_x(cam, p["X"], p["Z"], w)
    half = cam["f"] * BODY_HALF_WIDTH_M / max(0.05, p["Z"])
    feet = ground_y(cam, p["Z"])
    head = feet - height_px(cam, p["height"], p["Z"])
    return x - half, head, x + half, feet


def outside(box: tuple[float, float, float, float], w: float, h: float) -> str:
    x0, y0, x1, y1 = box
    if x1 < 0:
        return f"{-x1:.0f} px past the left edge"
    if x0 > w:
        return f"{x0 - w:.0f} px past the right edge"
    if y1 < 0:
        return f"{-y1:.0f} px above the top edge"
    if y0 > h:
        return f"{y0 - h:.0f} px below the bottom edge"
    return ""


# --------------------------------------------------------------------------- the second question
BAND = re.compile(r"between\s+(\d+)\s+and\s+(\d+)\s*px", re.I)


def declared_bands(dossier: dict) -> list[tuple[str, int, int]]:
    """Acceptance items that state a pixel band for a figure. Prose in, two integers out."""
    out = []
    for item in (dossier.get("acceptance") or []):
        if not isinstance(item, str):
            continue
        if not re.search(r"\bfigure|\bperson\b|\bpeople\b", item, re.I):
            continue
        m = BAND.search(item)
        if m:
            out.append((item, int(m.group(1)), int(m.group(2))))
    return out


# --------------------------------------------------------------------------- the gate
def check_slide(path: Path, dossier: dict | None) -> dict:
    raw = path.read_text(encoding="utf-8")
    src = strip_js(raw)
    figs = figures(src)
    cams = cameras(src)
    w, h = canvas_size(src)
    res, unres = placements(src, figs)
    n_indirect = indirect_figures(src)
    if n_indirect > 0:
        unres.append(f"{n_indirect} figure(s) built inline, never bound to a name")

    out = {"slide": path.name, "figures": len(figs), "resolved": [], "unresolved": unres,
           "outside": [], "bands": [], "cameras": len(cams)}

    if not figs and n_indirect == 0:
        return out
    if len(cams) != 1:
        out["unresolved"].append(
            f"{len(cams)} camera literal(s) in this slide, so a projection cannot be taken from "
            f"it; {len(res)} figure placement(s) go unchecked")
        return out
    cam = cams[0]

    for p in res:
        box = box_of(cam, p, w)
        px = height_px(cam, p["height"], p["Z"])
        rec = {**p, "x": project_x(cam, p["X"], p["Z"], w), "px": px}
        out["resolved"].append(rec)
        why = outside(box, w, h)
        if why:
            out["outside"].append(
                f"{path.name}: the {p['height']:.2f} m figure placed at X {p['X']} Z {p['Z']} "
                f"projects to x {rec['x']:.0f} on an f {cam['f']:.0f} camera, which is {why} of "
                f"a {w:.0f} px frame. The plan named a subject the camera does not include.")

    for item, lo, hi in declared_bands(dossier or {}):
        if not out["resolved"]:
            continue
        got = sorted(round(r["px"]) for r in out["resolved"])
        if not any(lo <= g <= hi for g in got):
            out["bands"].append(
                f"{path.name}: acceptance asks for {lo} to {hi} px and this slide's own camera "
                f"and placements give {', '.join(str(g) for g in got)} px  ({item[:72]})")
    return out


def check_deck(slides_dir: Path, storyboard: Path | None) -> tuple[list[dict], dict]:
    dossiers: dict[int, dict] = {}
    if storyboard and storyboard.exists():
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        try:
            from dossier_check import parse_dossiers  # noqa: PLC0415
            dossiers = parse_dossiers(storyboard.read_text(encoding="utf-8"))
        except Exception:  # a storyboard this parser cannot read is not this gate's finding
            dossiers = {}
    reports = []
    for f in sorted(slides_dir.glob("slide-*.html")):
        n = int(re.search(r"(\d+)", f.name).group(1))
        reports.append(check_slide(f, dossiers.get(n)))
    totals = {
        "slides": len(reports),
        "figures": sum(r["figures"] for r in reports),
        "resolved": sum(len(r["resolved"]) for r in reports),
        "unresolved": sum(len(r["unresolved"]) for r in reports),
        "outside": sum(len(r["outside"]) for r in reports),
        "bands": sum(len(r["bands"]) for r in reports),
    }
    return reports, totals


def problems(run_dir: Path) -> list[str]:
    """The adapter shipped_check calls. Only the fatal half, and only when there are slides."""
    slides = run_dir / "slides"
    if not slides.is_dir() or not any(slides.glob("slide-*.html")):
        return []
    reports, _ = check_deck(slides, run_dir / "storyboard.md")
    return [f for r in reports for f in r["outside"]]


def run(slides: Path, storyboard: Path | None, label: str) -> int:
    if not slides.is_dir():
        print(f"scene_bounds: ABSENT. {slides} is not a directory, so nothing was read and "
              f"nothing is certified", file=sys.stderr)
        return 2
    if not any(slides.glob("slide-*.html")):
        print(f"scene_bounds: ABSENT. {slides} archives no slide HTML, so the scene geometry "
              f"of this deck cannot be read at all", file=sys.stderr)
        return 2
    reports, t = check_deck(slides, storyboard)

    for r in reports:
        for line in r["unresolved"]:
            print(f"  unresolved  {r['slide']}: {line}")
    for r in reports:
        for line in r["bands"]:
            print(f"  band        {line}")

    if t["outside"]:
        print(f"\nscene_bounds: {t['outside']} figure placement(s) outside the frame in "
              f"{label}\n", file=sys.stderr)
        for r in reports:
            for line in r["outside"]:
                print(f"  - {line}", file=sys.stderr)
        return 1

    if t["figures"] == 0 and t["unresolved"] == 0:
        print(f"scene_bounds: {label}, {t['slides']} slide(s) and NO FIGURE in any of them, so "
              f"this gate had nothing to measure and certifies nothing")
        return 0
    print(f"scene_bounds: {label}, {t['slides']} slide(s), {t['resolved']} figure placement(s) "
          f"resolved and inside the frame, {t['unresolved']} unresolved, {t['bands']} "
          f"acceptance band(s) the plan's own camera cannot reach")
    return 0


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    bad = 0

    def ok(label, cond, extra=""):
        nonlocal bad
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            bad += 1

    # ---------------------------------------------------------------- THE DEFECT, REPLAYED
    # Carousel no. 24's cover as it was FIRST CUT: the one figure at X -13, Z 9, on the frame's
    # own f 820 camera. This is the fixture the gate exists for and it must go red on it.
    defect = """
    <script>
      var W = 1080, H = 1350;
      var cam = { w: W, h: H, eye: 1.65, horizon: 940, f: 820, fogZ: 1e9,
                  light: { az: -68, el: 14 } };
      var hand = TXFIG.figure({ pose: "stand", height: 1.70, hold: "clipboard" });
      TXINK.print(cx, { draw: function (a) {
        var S = TXSCENE.create(a, Object.assign({ sky: "#000000" }, cam));
        S.shadow(hand, { X: -13, Z: 9, ink: "#000", alpha: 0.85 });
        S.sprite(hand, { X: -13, Z: 9, inks: { ink: "#FFFAF0" }, fade: false });
      }});
    </script>"""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "slides"
        d.mkdir()
        (d / "slide-01.html").write_text(defect, encoding="utf-8")
        rep = check_slide(d / "slide-01.html", None)
        ok("the 2026-09-14 cover's first cut is CAUGHT", len(rep["outside"]) == 1,
           f"reported {rep['outside']}")
        ok("...and the miss is measured at x -644, which is what the engine's own projection "
           "gives", rep["resolved"] and abs(rep["resolved"][0]["x"] + 644.4) < 1.0,
           str(rep["resolved"]))
        ok("...and it is named as past the LEFT edge",
           bool(rep["outside"]) and "left edge" in rep["outside"][0], str(rep["outside"]))

        # THE REPAIRED FRAME, which is the half that proves the gate is not simply always red.
        (d / "slide-01.html").write_text(defect.replace("X: -13, Z: 9", "X: -9.2, Z: 27"),
                                         encoding="utf-8")
        rep2 = check_slide(d / "slide-01.html", None)
        ok("the shipped repair at X -9.2 Z 27 is CLEAN", not rep2["outside"], str(rep2["outside"]))
        ok("...and it measures 51.6 px tall, the figure's real rendered height",
           rep2["resolved"] and abs(rep2["resolved"][0]["px"] - 51.63) < 0.1,
           str(rep2["resolved"]))

        # AND THE MIDDLE REPAIR, which round 2 of the panel caught: in frame, wrong size.
        (d / "slide-01.html").write_text(defect.replace("X: -13, Z: 9", "X: -1.5, Z: 9"),
                                         encoding="utf-8")
        rep3 = check_slide(d / "slide-01.html", None)
        ok("a figure moved INTO the frame at the wrong depth is not an outside-frame finding",
           not rep3["outside"], str(rep3["outside"]))
        ok("...and the band half sees it at 155 px against a declared 38 to 52",
           bool(check_slide(d / "slide-01.html",
                            {"acceptance": ["one human figure is present and is between 38 and "
                                            "52 px tall"]})["bands"]))

    # ---------------------------------------------------------------- THE EMPTY CASES
    # GATE_LESSONS 51: a checker whose empty case prints its clean line is not a checker.
    with tempfile.TemporaryDirectory() as td:
        empty = Path(td) / "slides"
        empty.mkdir()
        ok("a slides directory that does not exist is ABSENT and not clean",
           run(Path(td) / "nope", None, "fixture") == 2)
        ok("a slides directory with no slide HTML is ABSENT and not clean",
           run(empty, None, "fixture") == 2)
        (empty / "slide-01.html").write_text("<script>var W = 1080;</script>", encoding="utf-8")
        rep = check_slide(empty / "slide-01.html", None)
        ok("a slide with no figure in it reports NO FIGURE rather than a pass",
           rep["figures"] == 0 and not rep["outside"] and not rep["unresolved"])

    # ---------------------------------------------------------------- UNRESOLVED IS NOT CLEAN
    crowd = """<script>
      var W = 1080, H = 1350;
      var cam = { w: W, h: H, eye: 1.15, horizon: 560, f: 700, light: { az: -28, el: 62 } };
      var crowd = [1,2,3].map(function (i) {
        return { sprite: TXFIG.figure({ pose: "walk", height: 1.7 }), X: R() * 9, Z: 6 + i };
      });
      crowd.forEach(function (f) { S.sprite(f.sprite, { X: f.X, Z: f.Z, inks: k }); });
    </script>"""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "slides"
        d.mkdir()
        (d / "slide-01.html").write_text(crowd, encoding="utf-8")
        rep = check_slide(d / "slide-01.html", None)
        ok("a crowd scattered at draw time is REPORTED as unresolved, never dropped",
           len(rep["unresolved"]) >= 1, str(rep))

    # ---------------------------------------------------------------- THE PROJECTION ITSELF
    # Pinned against assets/js/txscene.js rather than against this file's own arithmetic. If the
    # engine's projection ever moves, this is the assertion that goes red.
    js = (REPO_ROOT / "assets" / "js" / "txscene.js").read_text(encoding="utf-8")
    ok("txscene.js still projects x as w / 2 + f * X / Z",
       "w / 2 + f * X / Z" in js,
       "the engine's projection moved and this gate's arithmetic is now a guess")
    ok("txscene.js still puts the ground at horizon + f * eye / Z",
       "horizon + f * eye / Math.max(0.05, Z)" in js)
    ok("txfig.js still defaults a figure to 1.7 m",
       "o.height || 1.7" in (REPO_ROOT / "assets" / "js" / "txfig.js").read_text(encoding="utf-8"),
       f"the default this gate assumes is {DEFAULT_FIGURE_HEIGHT_M}")

    # ---------------------------------------------------------------- THE REAL CORPUS
    # A fixture written beside a detector agrees with it. GATE_LESSONS 16, and the reason every
    # assertion above is paired with one against work that actually shipped.
    shipped = [d for d in sorted(RUNS.glob("*/slides")) if any(d.glob("slide-*.html"))]
    ok("there are shipped decks with archived slide HTML to measure", len(shipped) >= 10,
       f"{len(shipped)} found, so this gate is nearly inert")
    fired = {d.parent.name: problems(d.parent) for d in shipped}
    noisy = {k: v for k, v in fired.items() if v}
    ok("no shipped deck places a figure outside its own frame", not noisy, str(noisy))

    totals = {}
    for d in shipped:
        _, totals[d.parent.name] = check_deck(d, d.parent / "storyboard.md")
    resolved = sum(t["resolved"] for t in totals.values())
    ok("...and the gate resolved real placements while finding none, rather than resolving none",
       resolved >= 8, f"{resolved} placements resolved across {len(shipped)} decks")

    # THE CORPUS PIN. A parser that quietly stops reading a construction is this gate's own
    # likeliest failure and it already happened once, here, before it shipped: the HTML body's
    # apostrophes swallowed two whole slides. So the counts on the deck this gate was built for
    # are nailed down, and a parser that goes quiet turns red instead of turning clean.
    t24 = totals.get("2026-09-14", {})
    ok("carousel no. 24 resolves all six of its figure placements, three of them from the "
       "table on frame 6", t24.get("resolved") == 6, str(t24))
    ok("...and frame 6's unreachable acceptance band is still reported",
       t24.get("bands") == 1, str(t24))
    ok("...with nothing on that deck left unresolved", t24.get("unresolved") == 0, str(t24))

    # THE APOSTROPHE, which is that defect as a fixture rather than as a paragraph.
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "slides"
        d.mkdir()
        (d / "slide-01.html").write_text(
            "<body><p class=dek>the grid operator's own notice</p>" + defect + "</body>",
            encoding="utf-8")
        rep = check_slide(d / "slide-01.html", None)
        ok("prose apostrophes outside the script do not blind the parser",
           len(rep["outside"]) == 1, f"{rep}")

    print("\nscene_bounds self-test:", "clean" if not bad else f"{bad} FAILURE(S)")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], allow_abbrev=False)
    ap.add_argument("--date", help="a run in out/<date>/")
    ap.add_argument("--run", help="a shipped run under runs/carousel/<date>/")
    ap.add_argument("--all", action="store_true", help="every shipped run")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        return self_test()
    if a.all:
        rc = 0
        for d in sorted(RUNS.glob("*/slides")):
            if any(d.glob("slide-*.html")):
                rc |= min(1, run(d, d.parent / "storyboard.md", d.parent.name))
        return rc
    if a.run:
        base = RUNS / a.run
        return run(base / "slides", base / "storyboard.md", a.run)
    if a.date:
        base = OUT / a.date
        return run(base / "slides", base / "storyboard.md", a.date)
    ap.error("one of --date, --run, --all or --self-test")
    return 2


if __name__ == "__main__":
    sys.exit(main())
