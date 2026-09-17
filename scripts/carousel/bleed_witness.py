#!/usr/bin/env python3
"""bleed_witness.py — a declared bleed has to be drawn, and the drawing is in the slide's source.

THE DEFECT THIS EXISTS FOR (2026-09-17, carousel no. 27, frames 2, 4, 5 and 7)

Four of nine dossiers declared a bleed the frame never makes, and the whole suite was green.

    frame 4   `bleeds: [left, right, bottom]`   N.sheet ends at y 1198, 152 px inside the frame
    frame 5   `bleeds: [right, bottom]`         N.sheet ends at y 1100, 250 px inside
    frame 7   `bleeds: [left, right, bottom]`   N.sheet ends at y 1202, 148 px inside
    frame 2   `bleeds: [top]`                   N.panel starts at y 392, a hard edge 392 px in,
                                                and bleeds left and right undeclared

`layout_check` reads `primary_image.bleeds` and measures it against `primary_image.rect`, and
both of those are typed by the planner into the same yaml block. **The gate and the declaration
agreed with each other and not with the pixels**, which GATE_LESSONS calls the most dangerous
shape a check can have. Two craft judges found all four by reading the `N.sheet` call and
subtracting, across four scoring rounds, on a deck that shipped at 6.856 against an 8.0 bar. A
round 5 judge asked for this gate in one sentence: *"read each frame's drawn geometry back out of
its own source and fail the build when it disagrees with the dossier."*

The harm is mechanical and not aesthetic. `ROTATION["min_bleed_frames"]` requires four bleeding
frames on a deck, counted off the declarations. A deck can satisfy the image law with declarations
alone and draw no bleed at all, which is what carousel no. 27 came within one frame of doing.

WHY THE SOURCE AND NOT THE PIXELS

The bottom row of frame 4 is not flat ground. It is the reading table, drawn by `N.surface`, and
a pixel reading of that edge says "something is drawn here" and is correct. The claim under test
is narrower: THE PRIMARY IMAGE runs off that edge. No detector can recover which drawn thing is
the subject from a rendered frame, and one calibrated on 27 decks would misreport. The source
answers it exactly, because these decks draw their sheets and panels as literal boxes in frame
coordinates. `scene_bounds.py` established the route on this repo's own slides and this file
imports its readers rather than writing a second copy of them.

WHAT A BOX IS, AND THE TWO RULES THAT DECIDE ANYTHING

A BOX is any call in the slide's own script whose object literal carries numeric `x`, `y`, `w`
and `h` at its top level, after `var NAME = <number>` constants are folded in. That is a
DENYLIST-free selector, deliberately, because a list of primitive names is a gate that sleeps the
day a deck chassis invents a name nobody wrote down (GATE_LESSONS 39). The chassis is written
fresh for every deck and `N.sheet` is 27 decks old.

  REACHES an edge.   x <= 0, y <= 0, x + w >= W, y + h >= H. The same predicate `layout_check`
                     applies to the declared rect, so the two cannot disagree about what a bleed
                     is. This is what WITNESSES a declared bleed.
  CROSSES an edge.   strictly past it. x < 0, y < 0, x + w > W, y + h > H. This is what makes a
                     frame CHECKABLE at all, and the asymmetry is the whole design. A box drawn
                     PAST an edge proves the frame composes its image in box coordinates that run
                     off the canvas, so the absence of a box at another edge is evidence. A box
                     that stops exactly on an edge proves nothing either way.

A FRAME IS UNRESOLVED, and decides nothing, when no box crosses any edge. Those are the frames
whose image is a projected scene, a path or a gradient, which this file cannot see and does not
pretend to. On carousel no. 27 that is five of nine, and the count is PRINTED on success as well
as on failure, so a run that covered almost nothing can never read as a run that found nothing
(GATE_LESSONS 26, 51).

A FRAME IS ALSO UNRESOLVED when any box call in it carries x, y, w and h that this file could
not resolve to numbers, because the box it could not read might be the one that makes the bleed.
Those calls are NAMED AND COUNTED rather than dropped.

A BOX REACHING ALL FOUR EDGES IS THE GROUND AND IS EXCLUDED. A box covering the whole canvas
witnesses every edge trivially, so it witnesses nothing, and letting it count would turn the
first `fillRect` of every frame into a blanket bleed certificate.

METRES ARE NOT PIXELS, AND THIS FILE LEARNED THAT BY INVENTING THREE FAILURES

The first cut was run over all 27 shipped decks before it was wired to anything, and it reported
carousels 22, 24 and 25 as declaring bleeds they missed **by 1078.75, 1079.70 and 1348.48 px**.
Every one was wrong. The engine draws scenes in metres on a projected camera, so a 2.50 m gantry
part and a 0.60 m desk screen parse as boxes two pixels across sitting off the left edge. A gate
that misreports a figure is worse than one that misses it, and an invented failure at a confident
number is the most persuasive shape a false finding takes (GATE_LESSONS 16 and 27).

Three guards, each one structural rather than a size threshold, and each with its own self-test
case kept verbatim from the deck that produced it:

  a part is not a placement    an object literal inside an ARRAY describes what a thing is made
                               of, in the model's own space. Only a DIRECT object argument of a
                               call says where to draw it, in the space that call draws in.
  a world anchor is metres     a call carrying `X` or `Z` at the top level of one of its
                               arguments is a scene call. Those names are copied from
                               `assets/js/txscene.js` and the self-test reads that file and
                               asserts the copy still holds, because a name list nothing checks
                               is a guard that sleeps.
  sub-pixel is not pixel space a box under one unit in either dimension is not a box in a space
                               whose quantum is the pixel. One is not a tuned threshold, it is
                               the unit the coordinate space is counted in.

Run back over the corpus with all three in force, the gate is clean on every deck before no. 27
and red on exactly the four frames three judges found by eye.

WHAT IT CANNOT SEE, STATED SO NOBODY INFERS A GUARANTEE

  - A frame whose primary image bleeds one edge through a projected plane while ALSO drawing a
    crossing box. That is a false positive and it is the one this file can produce. Every finding
    names the call and the line it measured, so the misreading is visible in the message itself.
    **The answer if it happens is to make the dossier describe the drawing, not to widen this
    gate.** A declared bleed is a claim about the picture and the picture is what a reader gets.
  - Whether the box was DRAWN. This reads the plan of the picture in its own source, not the
    picture. `layout_check`'s detail and silhouette measurements read the pixels.
  - Geometry computed at draw time. Reported by name, never skipped.

    bleed_witness.py --run-dir out/<date>            a live run
    bleed_witness.py --run-dir runs/carousel/<date>  a shipped run
    bleed_witness.py --date <date>                   maps to out/<date>
    bleed_witness.py --run <date>                    maps to runs/carousel/<date>
    bleed_witness.py --all                           every shipped run that archived its slides
    bleed_witness.py --self-test

Exit 0 clean, 1 findings, 2 could not run.
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS = REPO_ROOT / "runs" / "carousel"
OUT = REPO_ROOT / "out"

W, H = 1080, 1350
EDGES = ("top", "left", "right", "bottom")

NUM = r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?"
IDENT = r"[A-Za-z_$][A-Za-z0-9_$]*"

# THE ENGINE'S WORLD COORDINATES, copied from assets/js/txscene.js, where a placement is
# `{ X: <metres right of the camera axis>, Z: <metres away> }`. A call carrying either at the top
# level of one of its arguments is drawing in METRES and none of its boxes are frame boxes.
# `self_test` parses that file and asserts the copy still holds, because a copy nothing checks is
# the oldest shape in GATE_LESSONS and a name list nothing checks is the second oldest.
WORLD_KEYS = ("X", "Z")


def _mod(name: str):
    """Load a sibling carousel module by path, the way every gate here does."""
    spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parent / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# --------------------------------------------------------------------------- reading the source
def _blank_nested(obj: str) -> str:
    """Blank everything below the object's own top level, preserving byte offsets.

    A key lookup over the whole literal reads into nested objects and function bodies, and
    `N.panel(cx, {x: PX, ..., content: function (g, r) { ... r.x ... }})` is exactly the shape
    that would be misread. Depth 1 is the object's own keys and nothing else.
    """
    out = list(obj)
    depth = 0
    for i, c in enumerate(obj):
        if c == "{":
            depth += 1
            if depth > 1:
                out[i] = " "
        elif c == "}":
            if depth > 1:
                out[i] = " "
            depth -= 1
        elif depth > 1:
            out[i] = "\n" if c == "\n" else " "
    return "".join(out)


def _direct_object_args(args: str) -> list[str]:
    """Every object literal that is a DIRECT argument of the call, and never one inside an array.

    THIS RULE IS A CORRECTION THIS GATE HAD TO MAKE TO ITSELF, and the corpus is what made it.
    The first cut took the first `{` in the argument list, and on carousel no. 24's frame 1 that
    was a part of an MRI scanner:

        TXSCENE.sprite([{ type: "rect", x: -1.25, y: 0, w: 2.50, h: 1.88, fill: "ink" }, ...],
                       { kind: "mri" })

    Those numbers are METRES IN WORLD SPACE. Read as frame pixels they make a 2.5 px box, so the
    gate reported a correct frame as declaring a bleed it missed "by 1078.75 px", on two shipped
    decks. A gate that misreports a figure is worse than one that misses it (GATE_LESSONS 16),
    and an invented failure at a confident number is the most persuasive shape a false finding
    takes (GATE_LESSONS 27).

    The discriminator is structural rather than a size threshold, which is what makes it safe. An
    object literal handed straight to a call SAYS WHERE TO DRAW THE THING, in the space the call
    draws in. An object literal inside an array is a PART OF THE THING, in whatever space the
    model is built in, and a model's own space is never the canvas.
    """
    out: list[str] = []
    depth_p = depth_b = 0
    i = 0
    while i < len(args):
        c = args[i]
        if c == "(":
            depth_p += 1
        elif c == ")":
            depth_p -= 1
        elif c == "[":
            depth_b += 1
        elif c == "]":
            depth_b -= 1
        elif c == "{":
            obj = _object_at_local(args, i)
            if depth_p == 1 and depth_b == 0:
                out.append(obj)
            i += len(obj)
            continue
        i += 1
    return out


def _object_at_local(src: str, i: int) -> str:
    depth = 0
    for j in range(i, len(src)):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return src[i:j + 1]
    return src[i:]


def constants(stripped: str) -> dict[str, float]:
    """Names bound EXACTLY ONCE to a plain number in this script, and nothing else.

    `var PX = -60, PY = 392, PW = 1200, PH = 704;` is how this deck's frame 2 places its panel,
    so a reader that refuses variables cannot see the frame the panel defect lives on. A name
    assigned twice, or assigned anything that is not a bare numeral, is NOT resolved: a reader
    that guesses at a value it cannot follow is worse than one that says it could not follow it.
    """
    assigns: dict[str, list[str]] = {}
    for m in re.finditer(r"(?<![.\w$])(" + IDENT + r")\s*(?:[-+*/%|&^]|<<|>>)?=(?!=)([^;,\n]*)", stripped):
        assigns.setdefault(m.group(1), []).append(m.group(2).strip())
    out: dict[str, float] = {}
    for name, vals in assigns.items():
        if len(vals) != 1:
            continue
        v = vals[0].strip().rstrip(")").strip()
        if re.fullmatch(NUM, v):
            out[name] = float(v)
    return out


def _value(obj_top: str, key: str, consts: dict[str, float]) -> tuple[float | None, str | None]:
    """(number, unresolved-text). One of the two is always None."""
    m = re.search(r"(?<![\w$.])" + key + r"\s*:\s*([^,}]+)", obj_top)
    if not m:
        return None, None
    raw = m.group(1).strip()
    if re.fullmatch(NUM, raw):
        return float(raw), None
    if re.fullmatch(IDENT, raw) and raw in consts:
        return consts[raw], None
    return None, raw


def boxes(src: str) -> tuple[list[dict], list[dict]]:
    """(resolved boxes, unreadable box calls) from one slide's HTML.

    A box call is any `name(...)` whose argument list holds an object literal carrying all four
    of x, y, w and h at its own top level. Comments, strings and everything outside `<script>`
    are blanked by `scene_bounds` first, with byte offsets preserved, so a line number quoted
    here is a line number in the file.
    """
    sb = _mod("scene_bounds")
    stripped = sb.strip_js(src)
    consts = constants(stripped)
    good: list[dict] = []
    bad: list[dict] = []
    for m in re.finditer(r"(?<![\w$.])(" + IDENT + r"(?:\.\w+)*)\s*\(", stripped):
        name, open_i = m.group(1), m.end() - 1
        depth, close = 0, None
        for j in range(open_i, len(stripped)):
            if stripped[j] == "(":
                depth += 1
            elif stripped[j] == ")":
                depth -= 1
                if depth == 0:
                    close = j
                    break
        if close is None:
            continue
        args = stripped[open_i:close + 1]
        line = stripped.count("\n", 0, m.start()) + 1
        direct = _direct_object_args(args)
        if any(re.search(r"(?<![\w$.])[" + "".join(WORLD_KEYS) + r"]\s*:", _blank_nested(o))
               for o in direct):
            continue                                  # a world anchor, so this call is in metres
        for obj in direct:
            top = _blank_nested(obj)
            vals, misses = {}, []
            for key in ("x", "y", "w", "h"):
                v, raw = _value(top, key, consts)
                if v is not None:
                    vals[key] = v
                elif raw is not None:
                    misses.append(f"{key}: {raw}")
            if len(vals) + len(misses) < 4:
                continue                              # not a box call at all
            if not misses and (vals["w"] < 1 or vals["h"] < 1):
                # SUB-PIXEL IS NOT PIXEL SPACE. `S.rectBox({X: DX, Z: DZ}, {x: -0.30, y: 1.16,
                # w: 0.60, h: 0.36})` on carousel no. 24's frame 5 is a 0.60 m screen on a desk,
                # and read as frame pixels it is a box that crosses the left edge and misses the
                # bottom by 1348 px. One pixel is the quantum of the space this gate measures in,
                # so a box smaller than one in either dimension is not a box in it.
                continue
            if misses:
                bad.append({"call": name, "line": line, "unresolved": misses})
            else:
                good.append({"call": name, "line": line, "x": vals["x"], "y": vals["y"],
                             "w": vals["w"], "h": vals["h"]})
    return good, bad


# --------------------------------------------------------------------------- the two predicates
def reaches(b: dict) -> set[str]:
    """The same predicate layout_check applies to the declared rect. Touching counts."""
    e = set()
    if b["y"] <= 0:
        e.add("top")
    if b["x"] <= 0:
        e.add("left")
    if b["x"] + b["w"] >= W:
        e.add("right")
    if b["y"] + b["h"] >= H:
        e.add("bottom")
    return e


def crosses(b: dict) -> set[str]:
    """Strictly past the edge. This is what makes a frame checkable, never what witnesses."""
    e = set()
    if b["y"] < 0:
        e.add("top")
    if b["x"] < 0:
        e.add("left")
    if b["x"] + b["w"] > W:
        e.add("right")
    if b["y"] + b["h"] > H:
        e.add("bottom")
    return e


def frame_report(src: str) -> dict:
    """One frame's drawn geometry, with the reason it is or is not checkable."""
    good, bad = boxes(src)
    ground = [b for b in good if reaches(b) == set(EDGES)]
    drawn = [b for b in good if reaches(b) != set(EDGES)]
    crossing = [b for b in drawn if crosses(b)]
    witnessed: dict[str, list[dict]] = {}
    for b in drawn:
        for e in reaches(b):
            witnessed.setdefault(e, []).append(b)
    rep = {"boxes": drawn, "ground": ground, "unreadable": bad, "crossing": crossing,
           "witnessed": witnessed, "checkable": False, "why": ""}
    if bad:
        rep["why"] = (f"{len(bad)} box call(s) place their geometry at draw time and could not "
                      f"be read here: " +
                      "; ".join(f"{b['call']} line {b['line']} ({', '.join(b['unresolved'])})"
                                for b in bad))
        return rep
    if not crossing:
        rep["why"] = ("no drawn box runs past a frame edge, so this frame composes its image "
                      "with something this file cannot read (a projected scene, a path, a "
                      "gradient) and nothing here is evidence about its bleeds")
        return rep
    rep["checkable"] = True
    return rep


# --------------------------------------------------------------------------- the deck
def find_slides(run_dir: Path) -> dict[int, Path]:
    d = run_dir / "slides"
    out: dict[int, Path] = {}
    if d.is_dir():
        for p in sorted(d.glob("slide-*.html")):
            m = re.search(r"slide-(\d+)", p.name)
            if m:
                out[int(m.group(1))] = p
    return out


def check(run_dir: Path) -> tuple[int, list[str], list[dict]]:
    """(code, problems, rows). Rows are per-frame, plus notes and warnings for the deck."""
    run_dir = Path(run_dir)
    board = run_dir / "storyboard.md"
    if not board.exists():
        return 2, [f"no storyboard.md in {run_dir}"], []
    slides = find_slides(run_dir)
    if not slides:
        return 2, [f"{run_dir} archives no slide HTML under slides/, so there is no drawn "
                   f"geometry to read and this gate CANNOT RUN. That is not a skip"], []
    dossiers = _mod("dossier_check").parse_dossiers(board.read_text(encoding="utf-8"))
    declared = {n: d for n, d in dossiers.items()
                if isinstance(d, dict) and isinstance(d.get("primary_image"), dict)
                and isinstance(d["primary_image"].get("bleeds"), list)}
    if not declared:
        return 0, [], [{"note": "no dossier declares `primary_image.bleeds`, so the illustration "
                                "system was not in force on this deck and nothing was measured"}]

    problems: list[str] = []
    rows: list[dict] = []
    checkable = 0
    for n in sorted(declared):
        want = {str(b).strip().lower() for b in declared[n]["primary_image"]["bleeds"]}
        want &= set(EDGES)
        if n not in slides:
            rows.append({"note": f"slide {n} declares bleeds and no slide-{n:02d}.html was "
                                 f"archived, so its drawing could not be read"})
            continue
        rep = frame_report(slides[n].read_text(encoding="utf-8"))
        row = {"frame": n, "declared": want, "checkable": rep["checkable"],
               "witnessed": set(rep["witnessed"]), "boxes": len(rep["boxes"]),
               "why": rep["why"]}
        rows.append(row)
        if not rep["checkable"]:
            continue
        checkable += 1
        for e in sorted(want - set(rep["witnessed"])):
            near = sorted(rep["boxes"], key=lambda b: -abs(b["w"] * b["h"]))[:1]
            b = near[0] if near else None
            where = ""
            if b:
                stop = {"top": b["y"], "left": b["x"], "right": b["x"] + b["w"],
                        "bottom": b["y"] + b["h"]}[e]
                lim = {"top": 0, "left": 0, "right": W, "bottom": H}[e]
                where = (f" The largest box on the frame is {b['call']} at line {b['line']}, "
                         f"[{b['x']:g}, {b['y']:g}, {b['x'] + b['w']:g}, {b['y'] + b['h']:g}], "
                         f"and its {e} edge stops at {stop:g} against the frame's {lim:g}, "
                         f"{abs(lim - stop):g} px short.")
            problems.append(
                f"slide {n}: `bleeds` declares {e} and no box this frame draws reaches the {e} "
                f"edge.{where} The declaration and `layout_check` agree with each other and not "
                f"with the drawing, and the deck's bleed count is being met on paper")
        for e in sorted(set(rep["witnessed"]) - want):
            rows.append({"note": f"warning: slide {n}: a drawn box reaches the {e} edge and "
                                 f"`bleeds` does not say so ("
                                 + ", ".join(f"{b['call']} line {b['line']}"
                                             for b in rep['witnessed'][e]) + ")"})
    rows.append({"note": f"{checkable} of {len(declared)} frame(s) draw a box past an edge and "
                         f"are checkable here. The rest are reported above and decided nothing"})
    return (1 if problems else 0), problems, rows


# --------------------------------------------------------------------------- shipped_check hook
def problems(run_dir: Path) -> list[str] | None:
    """The adapter shipped_check calls. None when the gate could not run at all."""
    code, probs, _rows = check(Path(run_dir))
    if code == 2:
        return None
    return probs


# --------------------------------------------------------------------------- self-test
SHEET_FIXTURE = """<!doctype html>
<html><body>
<p>The clinician's own note, an apostrophe that used to swallow the document.</p>
<canvas id="art"></canvas>
<script>
  var W = 1080, H = 1350;
  var cx = document.getElementById("art").getContext("2d");
  cx.fillRect(0, 0, W, H);
  // N.sheet(cx, { x: -112, y: 366, w: 1304, h: 9999 });  a commented call is not a drawing
  N.sheet(cx, { x: -112, y: 366, w: 1304, h: %(SH)s, rot: 0.005, seed: 29 });
  N.tooth(cx, { x: 0, y: 366, w: 1080, h: 730, cell: 6 });
</script>
</body></html>
"""

PANEL_FIXTURE = """<!doctype html><html><body><canvas id="art"></canvas><script>
  var PX = -60, PY = %(PY)s, PW = 1200, PH = 704;
  N.panel(cx, { x: PX, y: PY, w: PW, h: PH, content: function (g, r) {
      g.fillRect(r.x, r.y, r.w, r.h);
      var inner = { x: 40, y: 40, w: 100, h: 100 };
  } });
</script></body></html>
"""

# THE TWO FALSE POSITIVES THIS GATE PRODUCED ON ITS FIRST RUN OVER THE CORPUS, kept verbatim
# from the decks that produced them. Both were convincing and both were wrong, and neither
# fixture would have been written by anyone reasoning from the rule (GATE_LESSONS 16).
METRES_IN_AN_ARRAY = """<!doctype html><html><body><canvas id="art"></canvas><script>
  var scanner = TXSCENE.sprite([
    { type: "rect", x: -1.25, y: 0.00, w: 2.50, h: 1.88, fill: "ink", r: 0.24 },
    { type: "rect", x: -0.46, y: 1.62, w: 0.92, h: 0.06, fill: "paper" }
  ], { kind: "mri" });
  N.sheet(cx, { x: -112, y: 366, w: 1304, h: 832 });
</script></body></html>
"""

METRES_ON_AN_ANCHOR = """<!doctype html><html><body><canvas id="art"></canvas><script>
  var DX = 0.4, DZ = 3.1;
  var sc = S.rectBox({ X: DX, Z: DZ }, { x: -0.30, y: 1.16, w: 0.60, h: 0.36 });
  N.sheet(cx, { x: -112, y: 366, w: 1304, h: 832 });
</script></body></html>
"""

SCENE_FIXTURE = """<!doctype html><html><body><canvas id="art"></canvas><script>
  var cam = { w: 1080, h: 1350, eye: 1.65, horizon: 940, f: 820 };
  var S = TXSCENE.create(cx, cam);
  S.sprite(TXFIG.figure({ pose: "stand", height: 1.70 }), { X: -9.2, Z: 27 });
  N.tooth(cx, { x: 60, y: 600, w: 1020, h: 500, cell: 6 });
</script></body></html>
"""

DRAWTIME_FIXTURE = """<!doctype html><html><body><canvas id="art"></canvas><script>
  var t = Date.now();
  N.sheet(cx, { x: -112, y: 366, w: 1304, h: rowHeight(t), rot: 0 });
  N.panel(cx, { x: -40, y: 200, w: 1200, h: 400, content: function () {} });
</script></body></html>
"""

GROUND_FIXTURE = """<!doctype html><html><body><canvas id="art"></canvas><script>
  N.wash(cx, { x: 0, y: 0, w: 1080, h: 1350, seed: 3 });
  N.tooth(cx, { x: 40, y: 560, w: 1000, h: 540, cell: 6 });
</script></body></html>
"""


def self_test() -> int:
    """Replays the 2026-09-17 defect on the numbers that shipped, in both directions."""
    import tempfile

    fails = 0

    def ok(label, cond, extra=""):
        nonlocal fails
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + str(extra)[:400]}")
        if not cond:
            fails += 1

    # ---- the readers, on the exact strings that shipped
    g, b = boxes(SHEET_FIXTURE % {"SH": 832})
    ok("the sheet call is read at its shipped numbers",
       len(g) == 2 and any(x["call"] == "N.sheet" and x["x"] == -112 and x["y"] == 366
                           and x["w"] == 1304 and x["h"] == 832 for x in g), g)
    ok("...and the COMMENTED sheet with h 9999 was not read as a drawing",
       not any(x["h"] == 9999 for x in g), g)
    ok("...and the prose apostrophe above the script did not swallow the file", b == [], b)
    g2, _ = boxes(PANEL_FIXTURE % {"PY": 392})
    ok("a box placed off `var PX = -60, PY = 392, ...` is folded and read",
       len(g2) == 1 and g2[0]["x"] == -60 and g2[0]["y"] == 392 and g2[0]["w"] == 1200, g2)
    ok("...and the nested `{x: 40, y: 40, w: 100, h: 100}` inside its content function was NOT "
       "read as the panel's geometry", all(x["w"] != 100 for x in g2), g2)

    # ---- METRES ARE NOT PIXELS. Both of these read as a box crossing the left edge and missing
    # the bottom by a thousand pixels, and both were reported as failures on shipped decks
    # before the guards below existed.
    gm, _ = boxes(METRES_IN_AN_ARRAY)
    ok("a part inside an array is a MODEL and is not read as a placement",
       [round(x["w"]) for x in gm] == [1304], gm)
    ga, _ = boxes(METRES_ON_AN_ANCHOR)
    ok("a box on a world anchor {X, Z} is in metres and is not read as a placement",
       [round(x["w"]) for x in ga] == [1304], ga)
    js = (REPO_ROOT / "assets" / "js" / "txscene.js")
    ok(f"the world keys {WORLD_KEYS} are still what {js.name} reads a placement off",
       js.exists() and all(re.search(r"o\." + k + r"\b", js.read_text()) for k in WORLD_KEYS),
       "the copy in WORLD_KEYS has drifted from the engine, so the metre guard is asleep")

    # ---- the two predicates, which are the whole design
    sheet = {"call": "N.sheet", "line": 1, "x": -112, "y": 366, "w": 1304, "h": 832}
    ok("the shipped sheet REACHES left and right and not bottom",
       reaches(sheet) == {"left", "right"}, reaches(sheet))
    flush = {"call": "x", "line": 1, "x": 0, "y": 0, "w": W, "h": 400}
    ok("a box flush on an edge REACHES it and does not CROSS it",
       "left" in reaches(flush) and crosses(flush) == set(), (reaches(flush), crosses(flush)))

    def deck(d: Path, frames: dict[int, str], bleeds: dict[int, list[str]]):
        (d / "slides").mkdir(parents=True, exist_ok=True)
        for n, html in frames.items():
            (d / "slides" / f"slide-{n:02d}.html").write_text(html)
        parts = ["# Storyboard\n\nProse.\n"]
        for n in sorted(frames):
            parts.append(
                "```yaml\nslide: %d\nlayout: DOCUMENT\njob: a job\nprimary_image:\n"
                "  subject: \"a subject\"\n  rect: [0, 0, 1080, 1350]\n  bleeds: [%s]\n"
                "accent: none\n```\n" % (n, ", ".join(bleeds.get(n, []))))
        (d / "storyboard.md").write_text("\n".join(parts))

    scratch = REPO_ROOT / "out" / "bleed_witness"
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as td:
        root = Path(td)

        # (a) THE DEFECT, replayed on carousel no. 27's own numbers.
        d = root / "asshipped"
        deck(d, {4: SHEET_FIXTURE % {"SH": 832}, 2: PANEL_FIXTURE % {"PY": 392}},
             {4: ["left", "right", "bottom"], 2: ["top"]})
        code, probs, rows = check(d)
        ok("frame 4's declared bottom bleed against a sheet ending at 1198 FAILS",
           code == 1 and any("slide 4" in p and "declares bottom" in p and "152 px short" in p
                             for p in probs), probs)
        ok("frame 2's declared top bleed against a panel starting at 392 FAILS",
           any("slide 2" in p and "declares top" in p and "392 px short" in p for p in probs),
           probs)
        ok("...and frame 2's undeclared left and right are WARNINGS rather than failures",
           sum(1 for r in rows if "reaches the left edge" in r.get("note", "")
               or "reaches the right edge" in r.get("note", "")) == 2
           and not any("does not say so" in p for p in probs), rows)
        ok("...and the message names the call and the line it measured",
           all("N." in p and "line" in p for p in probs), probs)

        # (b) THE SAME DECK WITH THE DRAWING CORRECTED. This is the half that proves the gate
        # is measuring the geometry and not the declaration: only the numbers moved.
        d2 = root / "fixed"
        deck(d2, {4: SHEET_FIXTURE % {"SH": 984}, 2: PANEL_FIXTURE % {"PY": -20}},
             {4: ["left", "right", "bottom"], 2: ["top", "left", "right"]})
        code, probs, rows = check(d2)
        ok("a sheet drawn to y 1350 and a panel drawn to y -20 PASS unchanged declarations",
           code == 0 and not probs, probs)
        ok("...and both frames are reported as checkable rather than waved through",
           any("2 of 2 frame(s) draw a box past an edge" in r.get("note", "") for r in rows),
           rows)

        # (c) THE THREE WAYS A FRAME DECIDES NOTHING, each named and counted.
        d3 = root / "unresolved"
        deck(d3, {1: SCENE_FIXTURE, 3: GROUND_FIXTURE, 5: DRAWTIME_FIXTURE},
             {1: ["left", "right", "bottom"], 3: ["left", "right", "bottom"],
              5: ["left", "right", "bottom"]})
        code, probs, rows = check(d3)
        ok("a projected scene frame is UNRESOLVED and raises nothing", code == 0, probs)
        whys = {r["frame"]: r["why"] for r in rows if "frame" in r}
        ok("...and says the frame composes its image with something it cannot read",
           "projected scene" in whys.get(1, ""), whys)
        ok("a box covering the whole frame is the ground and witnesses nothing",
           "cannot read" in whys.get(3, ""), whys)
        ok("geometry placed at draw time is NAMED rather than silently skipped",
           "rowHeight(t)" in whys.get(5, "") and "N.sheet" in whys.get(5, ""), whys)
        ok("...and the deck note says how few frames were actually checked",
           any("0 of 3 frame(s)" in r.get("note", "") for r in rows), rows)

        # (d) THE GATE CANNOT RUN is not a skip. GATE_LESSONS 37.
        d4 = root / "noslides"
        deck(d4, {1: SCENE_FIXTURE}, {1: []})
        (d4 / "slides" / "slide-01.html").unlink()
        code, probs, _ = check(d4)
        ok("a run that archived no slide HTML exits 2 and says it CANNOT RUN",
           code == 2 and any("CANNOT RUN" in p for p in probs), probs)

        # (e) a deck from before the illustration system measures nothing and says so
        d5 = root / "nobleeds"
        (d5 / "slides").mkdir(parents=True)
        (d5 / "slides" / "slide-01.html").write_text(SCENE_FIXTURE)
        (d5 / "storyboard.md").write_text("# Storyboard\n\n```yaml\nslide: 1\njob: a job\n```\n")
        code, probs, rows = check(d5)
        ok("a deck that declares no bleeds at all is out of scope, not clean",
           code == 0 and any("not in force" in r.get("note", "") for r in rows), rows)

    # ---- the shipped deck this gate was written for, if it is still on disk
    live = RUNS / "2026-09-17"
    if (live / "slides").is_dir():
        code, probs, _ = check(live)
        named = {int(re.search(r"slide (\d+)", p).group(1)) for p in probs if "slide " in p}
        ok("replayed against carousel no. 27 as it shipped, it names frames 2, 4, 5 and 7",
           code == 1 and named == {2, 4, 5, 7}, (named, probs[:2]))
    else:
        ok("carousel no. 27 is on disk to replay against", False,
           f"{live}/slides is missing, so the founding defect was not replayed")

    print(f"bleed_witness --self-test: {'PASS' if not fails else str(fails) + ' FAILED'}")
    return 1 if fails else 0


# --------------------------------------------------------------------------- cli
def run(run_dir: Path, label: str) -> int:
    code, probs, rows = check(run_dir)
    if code == 2:
        for p in probs:
            print(f"bleed_witness: CANNOT RUN. {p}")
        return 2
    for r in rows:
        if "frame" in r:
            state = "checked" if r["checkable"] else "unresolved"
            print(f"  frame {r['frame']:02d}  {state:<10} declared "
                  f"{sorted(r['declared']) or '[]'}  drawn {sorted(r['witnessed']) or '[]'}"
                  + ("" if r["checkable"] else f"  ({r['why'][:110]})"))
    for r in rows:
        if "note" in r:
            print(f"  {r['note']}")
    for p in probs:
        print(f"  PROBLEM  {p}")
    print(f"bleed_witness: {label}, {len(probs)} problem(s)")
    return 1 if probs else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run-dir")
    ap.add_argument("--date")
    ap.add_argument("--run")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.all:
        worst = 0
        for d in sorted(p for p in RUNS.iterdir() if p.is_dir()):
            if not (d / "slides").is_dir():
                continue
            worst = max(worst, min(1, run(d, d.name)))
        return worst
    if a.run_dir:
        return run(Path(a.run_dir), str(a.run_dir))
    if a.date:
        return run(OUT / a.date, a.date)
    if a.run:
        return run(RUNS / a.run, a.run)
    ap.error("one of --run-dir, --date, --run, --all or --self-test")
    return 2


if __name__ == "__main__":
    sys.exit(main())
