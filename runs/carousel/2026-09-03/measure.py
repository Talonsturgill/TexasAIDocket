#!/usr/bin/env python3
"""Measure every frame's luminance off the rendered PNG and write measurements.json.

WHY THIS EXISTS. `shipped_check`'s `measured figures` gate asks, of the shipped bytes, whether
every number this run printed next to the token L* is in the file the run measured. A figure with
one home and several surfaces keeping their own copy is the shape CLAUDE.md names three times, and
a WRITER that composes those surfaces is not a check, because a writer can go silently dead.

This run reached round 5 of its panel before anybody measured a luminance at all, and the value
arc it had been carrying since the plan was a guess: it claimed a deck median near 43 against a
measured 72.0, and it was wrong on one frame by a factor of four. So the file exists now, and it
is written from the pixels rather than from anything the run believes about itself.

Sampled on a fixed 270 by 338 grid so the figure does not move with the render's resolution.
"""
import json
import pathlib
import statistics

from PIL import Image

RUN = pathlib.Path(__file__).resolve().parent
REPO = RUN.parents[2]      # runs/carousel/<run>/ -> the repository root


def _lin(c: float) -> float:
    """One sRGB channel, 0 to 255, to linear light."""
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lstar(r: float, g: float, b: float) -> float:
    """CIE L* from an sRGB triple.

    EACH CHANNEL IS LINEARISED BEFORE THEY ARE COMBINED, and the first version of this did it the
    other way round: it took the luma of the three sRGB values and then applied the transfer
    function once to that. A review bot on PR 252 caught it and gave the falsifying case, pure
    blue, which the wrong order puts at L* 5.6 against a true 32.3.

    On this deck's own palette the error runs 0.0 to 1.7 because none of its colours is a
    saturated primary, so no figure moves far. It was still an arithmetic error inside a file
    whose whole job is that a number here is computed rather than guessed, which is the one thing
    this project promises about its numerals.
    """
    Y = 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)
    return 116 * (Y ** (1 / 3)) - 16 if Y > 0.008856 else 903.3 * Y


def candidates(n: int):
    """Every place frame `n` might be, best source first."""
    return [RUN / ("render/slide-%02d.png" % n),
            REPO / "out" / RUN.name / "render" / ("slide-%02d.png" % n),
            RUN / ("slide-%02d.png" % n),
            RUN / ("slide-%02d.webp" % n)]


def source_for(n: int) -> pathlib.Path:
    """The image for frame `n`, from the working render if it is here and the shipped frame if not.

    IT HAS TO RUN FROM A FRESH CHECKOUT (2026-09-03, PR 252). This read `render/slide-NN.png`
    and nothing else, and `render/` is scratch under `out/` that is never committed. So the one
    script certifying that a published figure was computed rather than typed could not be re-run
    by anybody holding only the repository, which is every reader the compute-not-generate law is
    written for. A measurement nobody else can reproduce is an assertion with a program attached.

    THE FALLBACK IS NOT THE SAME FILE AND THE FIGURES ARE NOT IDENTICAL. Eight of the nine
    shipped frames are WebP, so falling back crosses a lossy encoder. Measured here against the
    render PNGs, frame by frame, the medians move 0.000 to 0.253 L*, worst on frame 5, which at
    the tenth this file publishes reads 17.5 off the render and 17.8 off the shipped frame.

    So the order matters and the losing path is never silent. The committed figures came from the
    render PNGs, `read_from` in `measurements.json` records which file produced each one, and a
    reproduction off the shipped frames agrees to about three tenths of a point rather than
    exactly. Saying they match would be the kind of claim this project does not get to make.
    """
    for p in candidates(n):
        if p.exists():
            return p
    raise SystemExit("no image for frame %d, looked in %s"
                     % (n, ", ".join(str(c) for c in candidates(n))))


def label(p: pathlib.Path) -> str:
    """How a source file is named in the output, wherever it sits."""
    for base in (RUN, REPO):
        try:
            return p.relative_to(base).as_posix()
        except ValueError:
            continue
    return str(p)


def main() -> int:
    frames = []
    read_from = []
    for n in range(1, 10):
        src = source_for(n)
        read_from.append(label(src))
        im = Image.open(src).convert("RGB").resize((270, 338))
        px = list(im.getdata())
        ls = [lstar(r, g, b) for r, g, b in px]
        bottom = ls[len(ls) * 2 // 3:]
        frames.append({
            "frame": n,
            "median_lstar": round(statistics.median(ls), 1),
            "mean_lstar": round(statistics.fmean(ls), 1),
            "stdev_lstar": round(statistics.pstdev(ls), 1),
            "bottom_third_median_lstar": round(statistics.median(bottom), 1),
            "bottom_third_stdev_lstar": round(statistics.pstdev(bottom), 1),
        })
    doc = {"run": "2026-09-03",
           "note": "Measured off the rendered frames by measure.py. L* from sRGB grey through the "
                   "linear-light step. Sampled on a fixed 270 by 338 grid so the figure does not "
                   "move with the render's resolution.",
           "read_from": read_from,
           "frames": frames,
           "deck_median_lstar": round(statistics.median([f["median_lstar"] for f in frames]), 1)}
    (RUN / "measurements.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    for f in frames:
        print("frame %d  median %5.1f  mean %5.1f  sd %4.1f  bottom third %5.1f"
              % (f["frame"], f["median_lstar"], f["mean_lstar"], f["stdev_lstar"],
                 f["bottom_third_median_lstar"]))
    print("deck median L* %.1f" % doc["deck_median_lstar"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
