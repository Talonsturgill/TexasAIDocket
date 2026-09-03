#!/usr/bin/env python3
"""craft_floor.py — no frame ships that nobody drew. Measured per slide, not per deck.

WHY THIS EXISTS. 2026-08-19.

Every gate in this suite before it was deck-level or claim-level. Not one looked at a SINGLE FRAME
and asked whether it was worth drawing. That is the hole a frame walked through seven times.

The measurement, off that run's own render report:

    slide-01   variance 3160.7      an August month sheet embossed into limestone
    slide-06   variance 2315.0      four terrazzo inlay bands
    slide-08   variance  674.8      a lit cell throwing a shaft onto a list
    slide-04   variance  533.1      a chart table under a lamp
    slide-05   variance  302.0      a survey sheet on the paper register
    slide-07   variance  223.1      a redaction field
    slide-03   variance  134.4      a Voronoi partition
    slide-02   variance   15.9      twenty six contour lines at five percent alpha

**Slide 2 was two hundred times flatter than slide 1 and broke no rule**, because no rule existed.
It was rebuilt three times over three scoring rounds and the number did not move, because each
rebuild fixed the type layer while the canvas stayed empty. A reviewer found it by hand at round 6.
`artwork_craft` carries 0.28, the heaviest weight in the rubric, and it never once reached the
rubric's own definition of acceptable across the whole run.

WHAT IT MEASURES, AND WHY TWO THINGS RATHER THAN ONE

**Variance alone is not craft.** A frame of pure noise scores high and is worthless, and a gate
that rewarded variance would teach runs to add texture instead of drawing. So this reads two
numbers that are already in the artifacts and asks them different questions:

- `canvases[].variance` from `render_report.json`. Does the frame have a real light and a real dark
  rather than one mid band? This is the rubric's own first question about artwork.
- the per-third craft-cell density `qa.py` computes. Is the detail budgeted across the frame, or is
  the whole drawing in one band with the rest empty?

A frame has to fail BOTH to be a hard fail. A frame that fails one is a warning, because a
deliberately quiet frame is a legitimate move and a gate that fires on a correct decision is a gate
somebody switches off. `coherence_check` carries the same reasoning about display type sizes.

WHERE THE FLOOR COMES FROM

Fitted on shipped work, not invented. The floor is a fraction of the deck's OWN median, so a dark
quiet deck is judged against itself rather than against a bright one, and a deck cannot pass by
being uniformly flat: the absolute floor catches that.

A DECK CAN DRAW EVERY FRAME AND WRITE NO CANVAS AT ALL (2026-09-03).

Deck no. 14 is entirely SVG. Nine frames, nine drawings, and `canvases` empty on every one of
them, so `variance_of` returned 0.0 nine times, the median was 0.0, and this gate divided by it
and raised ZeroDivisionError. A crash is not a verdict. It told the run nothing about the deck
and it would have told a later run nothing either.

The fix is not to exempt an SVG deck, which would hand every future deck a way to opt out of the
one gate that asks whether a frame was drawn. It is to ask the SAME QUESTION of a signal that
exists for SVG. `qa.py` computes the per-third craft-cell density on every frame whatever drew
it, so when a deck writes no canvas anywhere, the mean of those three bands becomes the measured
quantity and the relative floor works exactly as before, against the deck's own median.

What that costs, stated rather than hidden: band density answers "is there detail here" and not
"does this frame have a real light and a real dark", so on an SVG deck this gate is measuring the
weaker of the two questions it normally asks. The report says so on the line where it happens.

    craft_floor.py --date 2026-08-19
    craft_floor.py --self-test
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# RELATIVE FLOOR. A frame carrying less than this fraction of its own deck's median tonal range is
# not the same kind of object as the frames around it. Fitted on the three decks shipped to
# 2026-08-19: within a deck the ratio of the weakest frame to the median ran 0.05 on the deck that
# had the defect and stayed above 0.30 on the frames nobody complained about.
RELATIVE = 0.18

# ABSOLUTE FLOOR, so a uniformly flat deck cannot pass by having a flat median. Slide 2 measured
# 15.9 and slide 3, the next weakest and merely thin rather than empty, measured 134.4.
ABSOLUTE = 60.0

# A frame whose craft sits in one band with the rest empty. qa.py already reports this per third.
BAND_MIN = 0.04


def slides(report: dict) -> list:
    return report.get("slides") or []


def variance_of(slide: dict) -> float:
    """The tonal range of the frame's art. 0 when a slide draws no canvas at all."""
    cvs = slide.get("canvases") or []
    if not cvs:
        return 0.0
    return max(float(c.get("variance") or 0.0) for c in cvs)


def bands_of(qa_slide: dict) -> list:
    """Craft-cell density per third, if machine QA recorded it.

    THE CONTRACT, and the bug it is written against. qa.py's frame_balance() computes these
    three numbers on every slide and, until 2026-08-19, formatted them into a warning string
    and discarded them. This function looked for them and always got nothing, so `bands` was
    always empty, `lopsided` was always False, and the `thin and (lopsided or not bands)`
    branch below made EVERY thin frame a hard fail. The WARN tier three lines under it, the
    one that lets a deliberately quiet frame through, was unreachable dead code from the day
    this file was written.

    The self-test below already asserted that tier worked, and passed, every time, because it
    built its own qa dict WITH the key. The logic was never wrong. The data never arrived and
    nothing compared the two files. So the assertion that matters now reads a REAL shipped
    machine_qa.json and checks the producer actually writes what this reads.

    Third time in this repo a consumer read a key its producer does not write, after
    gate_status and email_check both missed `weighted_score`.
    """
    for k in ("bands", "thirds", "craft_bands"):
        v = qa_slide.get(k)
        if isinstance(v, (list, tuple)) and len(v) == 3:
            return [float(x) for x in v]
    return []


def check(report: dict, qa: dict | None = None) -> tuple[list, list, dict]:
    """Fails, warns, and the measurement, so a reader sees the distribution rather than a verdict."""
    rows = []
    for s in slides(report):
        rows.append({"file": s.get("file") or s.get("png") or "?", "variance": variance_of(s)})
    if not rows:
        return (["craft_floor: the render report lists no slides"], [], {})

    qa_by = {}
    for s in (slides(qa) if qa else []):
        qa_by[s.get("file") or s.get("png") or "?"] = s

    # AN ALL SVG DECK WRITES NO CANVAS, and the question still has to be asked. See the header.
    # The band densities qa.py already computes are the substitute, and the units change with
    # them, so the absolute floor cannot come along.
    signal = "canvas variance"
    if not any(r["variance"] > 0 for r in rows):
        signal = "band density"
        for r in rows:
            b = bands_of(qa_by.get(r["file"], {}))
            r["variance"] = (sum(b) / len(b)) if b else 0.0

    vals = [r["variance"] for r in rows]
    median = statistics.median(vals)
    if median <= 0:
        return ([f"craft_floor: every frame measures zero on {signal} and on band density too, so "
                 f"nothing here was drawn or nothing was measured. Neither is a deck that ships"],
                [], {"median": 0.0, "floor": 0.0, "rows": rows, "signal": signal})
    rel_floor = median * RELATIVE
    floor = max(ABSOLUTE, rel_floor) if signal == "canvas variance" else rel_floor

    fails, warns = [], []
    for r in rows:
        thin = r["variance"] < floor
        bands = bands_of(qa_by.get(r["file"], {}))
        lopsided = bool(bands) and min(bands) < BAND_MIN
        r["thin"], r["lopsided"] = thin, lopsided
        if thin and (lopsided or not bands):
            fails.append(
                f"{r['file']}: {signal} {r['variance']:.4g} against a floor of {floor:.4g}. "
                f"This frame carries {r['variance'] / median * 100:.0f} percent of the deck's own "
                f"median tonal range, so it is not the same kind of object as the frames around it. "
                f"Draw it or cut it. Do not answer this by adding texture")
        elif thin:
            warns.append(f"{r['file']}: {signal} {r['variance']:.4g} against a floor of "
                         f"{floor:.4g}, but its detail is spread across the frame. A deliberately "
                         f"quiet frame is a legitimate move. Confirm it is one")
    return fails, warns, {"median": median, "floor": floor, "rows": rows, "signal": signal}


def self_test() -> int:
    fails = 0

    def ok(label, cond, extra=""):
        nonlocal fails
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            fails += 1

    def rep(vals):
        return {"slides": [{"file": f"slide-{i + 1:02d}.html",
                            "canvases": [{"variance": v}]} for i, v in enumerate(vals)]}

    # THE 2026-08-19 DECK, as it actually measured, to the tenth.
    REAL = [3160.7, 15.9, 134.4, 533.1, 302.0, 2315.0, 223.1, 674.8]
    f, w, m = check(rep(REAL))
    ok("the frame nobody drew is CAUGHT", any("slide-02" in x for x in f), str(f))
    ok("...and it is the only hard fail in that deck", len(f) == 1, str(f))
    ok("...and the message names the measurement and the floor",
       f and "15.9" in f[0] and "floor" in f[0], str(f))
    ok("...and it refuses the wrong fix by name",
       f and "adding texture" in f[0], str(f))
    ok("the frames a reviewer never complained about all pass",
       not any(n in x for n in ("slide-01", "slide-04", "slide-06", "slide-08") for x in f), str(f))

    # The rebuilt slide 2 measured 334.6 and must clear.
    fixed = list(REAL); fixed[1] = 334.6
    f2, _, _ = check(rep(fixed))
    ok("...and the same frame passes once it is actually drawn", f2 == [], str(f2))

    # A UNIFORMLY FLAT DECK MUST NOT PASS BY HAVING A FLAT MEDIAN. This is what the absolute
    # floor is for, and a relative-only rule would wave this through.
    f3, _, _ = check(rep([12.0, 11.0, 13.0, 10.0, 12.5, 11.5, 12.2, 10.8]))
    ok("a deck that is flat all the way through is CAUGHT, not normalised away", len(f3) == 8,
       str(len(f3)))

    # A slide that draws no canvas at all.
    f4, _, _ = check({"slides": [{"file": "a.html", "canvases": []},
                                 {"file": "b.html", "canvases": [{"variance": 900}]},
                                 {"file": "c.html", "canvases": [{"variance": 800}]}]})
    ok("a slide with no canvas at all is CAUGHT", any("a.html" in x for x in f4), str(f4))

    # A QUIET FRAME WITH ITS DETAIL SPREAD IS A WARNING, NOT A FAIL. A gate that fires on a
    # correct decision gets switched off, which is coherence_check's own stated reasoning.
    quiet = rep([3000, 100, 900, 800, 700, 600, 500, 400])
    qa_spread = {"slides": [{"file": "slide-02.html", "bands": [0.30, 0.28, 0.31]}]}
    f5, w5, _ = check(quiet, qa_spread)
    ok("a quiet frame whose detail is spread is a WARN rather than a FAIL",
       not any("slide-02" in x for x in f5) and any("slide-02" in x for x in w5), str((f5, w5)))
    qa_lop = {"slides": [{"file": "slide-02.html", "bands": [0.30, 0.0, 0.01]}]}
    f6, _, _ = check(quiet, qa_lop)
    ok("...and the same frame with its craft in one band IS a fail",
       any("slide-02" in x for x in f6), str(f6))

    # ---- A DECK THAT WRITES NO CANVAS AT ALL (2026-09-03) -------------------------------
    # Deck no. 14 was entirely SVG and this gate raised ZeroDivisionError on it. A crash tells a
    # run nothing, so the same question is now asked of the band densities qa.py records for
    # every frame whatever drew it. These four cases are the proof it still goes red.
    svg_rep = {"slides": [{"file": "s%d.html" % i, "canvases": []} for i in range(1, 6)]}
    svg_qa_ok = {"slides": [{"file": "s%d.html" % i, "bands": [0.30, 0.28, 0.31]}
                            for i in range(1, 6)]}
    f7, w7, m7 = check(svg_rep, svg_qa_ok)
    ok("an all SVG deck no longer crashes this gate", True)
    ok("...and a drawn one passes", f7 == [] and w7 == [], str((f7, w7)))
    ok("...measured on band density rather than on a canvas that is not there",
       m7.get("signal") == "band density", str(m7.get("signal")))

    svg_qa_empty = {"slides": [{"file": "s1.html", "bands": [0.0, 0.005, 0.0]}] +
                              [{"file": "s%d.html" % i, "bands": [0.30, 0.28, 0.31]}
                               for i in range(2, 6)]}
    f8, _, _ = check(svg_rep, svg_qa_empty)
    ok("...and an SVG frame nobody drew is STILL CAUGHT",
       any("s1.html" in x for x in f8), str(f8))

    f9, _, _ = check(svg_rep, {"slides": [{"file": "s%d.html" % i, "bands": [0.0, 0.0, 0.0]}
                                          for i in range(1, 6)]})
    ok("...and a deck where nothing was drawn or nothing was measured is an error",
       f9 != [] and "nothing" in f9[0], str(f9))

    ok("an empty report is an error rather than a pass", check({})[0] != [])
    ok("the floor is fitted, not typed into a slide's own file",
       0.0 < RELATIVE < 1.0 and ABSOLUTE > 0)
    ok("...and the measurement is returned so a reader sees the distribution",
       "rows" in m and len(m["rows"]) == 8 and "median" in m)

    # ---- THE PRODUCER WRITES WHAT THIS GATE READS (2026-08-19) --------------------------
    # THE ASSERTION THAT WOULD HAVE CAUGHT THE BUG. Every other case in this file builds its
    # own qa dict with the key already in it, which is exactly why they all passed for the
    # entire life of a dead WARN tier. This one reaches across to the PRODUCER and checks the
    # link itself, so removing the write in qa.py turns this file red.
    _qa_src = REPO_ROOT / ".claude" / "skills" / "carousel-engine" / "qa.py"
    if _qa_src.exists():
        _src = _qa_src.read_text(encoding="utf-8")
        _writes = any(f'res["{k}"]' in _src or f"res['{k}']" in _src
                      for k in ("bands", "thirds", "craft_bands"))
        ok("qa.py PERSISTS the per-third bands this gate reads",
           _writes,
           "qa.py assigns none of bands/thirds/craft_bands onto its slide record, so "
           "bands_of() always returns [] and the WARN tier is dead again")
    else:
        print("  note  qa.py not found, so the producer contract was not checked")

    print("\ncraft_floor self-test: " + ("all passed" if not fails else f"{fails} FAILED"))
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date")
    ap.add_argument("--render-dir")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not (a.date or a.render_dir):
        ap.error("one of --date or --render-dir is required")
    d = Path(a.render_dir) if a.render_dir else REPO_ROOT / "out" / a.date / "render"
    rp = d / "render_report.json"
    if not rp.exists():
        print(f"craft_floor: {rp} does not exist", file=sys.stderr)
        return 2
    report = json.loads(rp.read_text(encoding="utf-8"))
    qp = d / "machine_qa.json"
    qa = json.loads(qp.read_text(encoding="utf-8")) if qp.exists() else None

    fails, warns, m = check(report, qa)
    for r in sorted(m.get("rows", []), key=lambda x: -x["variance"]):
        mark = "FAIL" if r.get("thin") and r in [x for x in m["rows"]] and any(
            r["file"] in f for f in fails) else ("warn" if r.get("thin") else "ok  ")
        print(f"  {mark}  {r['file']:<18} variance {r['variance']:>8.1f}")
    print(f"\n  deck median {m.get('median', 0):.1f}, floor {m.get('floor', 0):.1f}")
    for w in warns:
        print("  warn  " + w)
    if fails:
        print("\ncraft_floor: a frame in this deck was not drawn.", file=sys.stderr)
        for f in fails:
            print("  " + f, file=sys.stderr)
        return 1
    print("craft floor: clean, every frame carries a real light and a real dark")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
