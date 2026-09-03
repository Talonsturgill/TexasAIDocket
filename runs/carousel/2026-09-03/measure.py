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


def lstar(y: float) -> float:
    y = y / 255.0
    y = y / 12.92 if y <= 0.04045 else ((y + 0.055) / 1.055) ** 2.4
    return 116 * (y ** (1 / 3)) - 16 if y > 0.008856 else 903.3 * y


def main() -> int:
    frames = []
    for n in range(1, 10):
        im = Image.open(RUN / "render" / ("slide-%02d.png" % n)).convert("RGB").resize((270, 338))
        px = list(im.getdata())
        ls = [lstar(0.2126 * r + 0.7152 * g + 0.0722 * b) for r, g, b in px]
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
           "note": "Measured off the rendered PNGs by measure.py. L* from sRGB grey through the "
                   "linear-light step. Sampled on a fixed 270 by 338 grid so the figure does not "
                   "move with the render's resolution.",
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
