"""Counts the blue violet specks at the louvre blade ends of carousel no. 37's generators, at each
sun bias tried, so the README's account of the bias cap can be checked rather than believed.

A speck pixel is one whose blue minus red rose by more than 12 levels over the uncapped render, the
one the item 2 graders saw. A shadow lit only by a dusk sky turns a cream jamb bluer, and a pixel
can turn bluer without turning blue, which is why the first count of this, blue over red alone,
read frame 6 as cleared at 2 cm while a blind grader still saw "blue-grey speckled dashes" there.
The count is taken over the louvre panels only: frame 6's two panels and frame 1's left row of
units, which keeps out frame 1's pad, whose contact shadow the cap seats on purpose.

It reads, under --root:

    i12f/0929/slide-0N.png    items 1 and 2 as graded, before the cap
    i12b/0929/slide-0N.png    the same with a 5 mm cap
    i12c/0929/slide-0N.png    the same with the 2 cm cap the engine ships
    probe/<name>/render/slide-0N.png

where each probe is runs/carousel/2026-09-29/slides/slide-0N.html rendered with
`o.shadow.bias = -X / (c.far - c.near)` set on every shadow casting DirectionalLight just before
`TXT.snapshot`: `cap0.01_2026-09-29_slide-0N` at X = 0.01, `cap0.02_2026-09-29_slide-01` at 0.02,
`capx0.05_f1` at 0.05, and `map4k_f1` with the engine's own 2 cm cap and `o.shadow.mapSize` set to
4096. The 2 cm probe must come out identical to i12c, or the probes measured something else.

    python3 examples/ground-proof/specks.py --root <scratch> [--json out.json]
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

BLUER = 12      # levels of blue minus red gained over the uncapped render
RUNS = {
    "06": ((950, 1550, 2100, 2050), [
        ("5 mm", "i12b/0929/slide-06.png"),
        ("1 cm", "probe/cap0.01_2026-09-29_slide-06/render/slide-06.png"),
        ("2 cm", "i12c/0929/slide-06.png")]),
    "01": ((0, 1150, 1050, 1900), [
        ("5 mm", "i12b/0929/slide-01.png"),
        ("1 cm", "probe/cap0.01_2026-09-29_slide-01/render/slide-01.png"),
        ("2 cm", "i12c/0929/slide-01.png"),
        ("5 cm", "probe/capx0.05_f1/render/slide-01.png"),
        ("2 cm on a 4096 map", "probe/map4k_f1/render/slide-01.png")]),
}


def blue_minus_red(path, box):
    a = np.asarray(Image.open(path).convert("RGB"), dtype=np.int16)[box[1]:box[3], box[0]:box[2]]
    return a[..., 2] - a[..., 0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()
    same = np.array_equal(np.asarray(Image.open(a.root / "probe/cap0.02_2026-09-29_slide-01/render/slide-01.png")),
                          np.asarray(Image.open(a.root / "i12c/0929/slide-01.png")))
    if not same:
        raise SystemExit("the 2 cm probe and the engine's 2 cm render differ, so the probes measured something else")
    out = {}
    for frame, (box, runs) in RUNS.items():
        base = blue_minus_red(a.root / f"i12f/0929/slide-{frame}.png", box)
        out[frame] = {name: int(((blue_minus_red(a.root / p, box) - base) > BLUER).sum()) for name, p in runs}
        print(f"frame {int(frame)}: " + ", ".join(f"{v} at {k}" for k, v in out[frame].items()))
    if a.json:
        a.json.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
