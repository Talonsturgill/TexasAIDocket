#!/usr/bin/env python3
"""probe_L.py — the measured L* of a rect on a RENDERED frame, at the size the gate judges it.

WHY THIS EXISTS. `data-contacts` is a claim that an object sits on a ground, and qa.py proves it
by measuring the shadow rect against the ground rect at 432px and requiring 4.0 L* between them.
Three rounds of this run placed those rects by reading the drawing code and reasoning about where
the dark part must be, and all three were wrong in a different way each time: one pair straddled a
flat floor, one was inverted because the ground gradient ran the other way, and one was washed out
by a type reserve laid down AFTER the shadow.

The common defect is that the rects were derived from the SOURCE and the gate reads the PIXELS.
Anything drawn later moves the answer, and there are eight drawing passes on some of these frames.
So this samples the shipped PNG at the gate's own scale and prints what is actually there.

    python3 out/<run>/probe_L.py --png out/<run>/render/slide-05.png \
        --rect 126,1196,44,20 --rect 268,1196,44,20
    python3 out/<run>/probe_L.py --png ... --scan-column 1150,1340,10 --x 80,120
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

DESIGN_W, DESIGN_H = 1080, 1350
GATE_W = 432                      # qa.py judges contacts at feed width


def to_lab_L(r: float, g: float, b: float) -> float:
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    y = 0.2126729 * lin(r) + 0.7151522 * lin(g) + 0.0721750 * lin(b)
    return 116 * (y ** (1 / 3)) - 16 if y > 216 / 24389 else 24389 / 27 * y


def mean_L(img: Image.Image, rect) -> float:
    """Mean L* over a rect given in DESIGN px, measured on the gate-width image."""
    s = img.width / DESIGN_W
    x, y, w, h = [v * s for v in rect]
    box = (max(0, int(x)), max(0, int(y)),
           min(img.width, int(x + w)), min(img.height, int(y + h)))
    if box[2] <= box[0] or box[3] <= box[1]:
        return float("nan")
    crop = img.crop(box).convert("RGB")
    px = list(crop.getdata())
    return sum(to_lab_L(*p) for p in px) / len(px)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", required=True)
    ap.add_argument("--rect", action="append", default=[], help="x,y,w,h in design px")
    ap.add_argument("--scan-column", help="y0,y1,step -- walk a column and print L* down it")
    ap.add_argument("--x", help="x0,w for --scan-column")
    args = ap.parse_args()

    img = Image.open(args.png)
    img = img.resize((GATE_W, round(GATE_W * DESIGN_H / DESIGN_W)), Image.LANCZOS)

    for r in args.rect:
        rect = [float(v) for v in r.split(",")]
        print(f"  rect {r:26s} L* {mean_L(img, rect):6.2f}")

    if args.scan_column:
        y0, y1, step = [int(v) for v in args.scan_column.split(",")]
        x0, w = [int(v) for v in (args.x or "80,120").split(",")]
        for y in range(y0, y1, step):
            print(f"  y {y:5d}  L* {mean_L(img, [x0, y, w, step]):6.2f}")

    if len(args.rect) == 2:
        a = mean_L(img, [float(v) for v in args.rect[0].split(",")])
        b = mean_L(img, [float(v) for v in args.rect[1].split(",")])
        print(f"\n  dL {b - a:+.2f}  (qa.py wants the GROUND at least 4.0 L* above the SHADOW)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
