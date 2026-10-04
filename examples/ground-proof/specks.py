"""Counts the blue violet specks at the louvre blade ends of carousel no. 37's generators, at each
sun bias tried, so the README's account of the bias cap can be checked rather than believed.

A speck pixel is blue over red by more than 4 levels at a mid luma (45 to 200). The count is taken
inside the louvre region of a frame and reported as the number ADDED over the uncapped render, the
one the item 2 graders saw. Frame 6's region is its right louvre panel and door, frame 1's the band
of the left generator row.

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

RUNS = {
    "06": ((1700, 1500, 2160, 2100), [
        ("5 mm", "i12b/0929/slide-06.png"),
        ("1 cm", "probe/cap0.01_2026-09-29_slide-06/render/slide-06.png"),
        ("2 cm", "i12c/0929/slide-06.png")]),
    "01": ((0, 1000, 2160, 2200), [
        ("5 mm", "i12b/0929/slide-01.png"),
        ("1 cm", "probe/cap0.01_2026-09-29_slide-01/render/slide-01.png"),
        ("2 cm", "i12c/0929/slide-01.png"),
        ("5 cm", "probe/capx0.05_f1/render/slide-01.png"),
        ("2 cm on a 4096 map", "probe/map4k_f1/render/slide-01.png")]),
}


def count(path, box):
    a = np.asarray(Image.open(path).convert("RGB"), dtype=np.int16)[box[1]:box[3], box[0]:box[2]]
    r, b = a[..., 0], a[..., 2]
    luma = a.sum(axis=2) / 3
    return int(((b > r + 4) & (luma > 45) & (luma < 200)).sum())


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
        base = count(a.root / f"i12f/0929/slide-{frame}.png", box)
        out[frame] = {name: count(a.root / p, box) - base for name, p in runs}
        print(f"frame {int(frame)}: " + ", ".join(f"{v} at {k}" for k, v in out[frame].items()))
    if a.json:
        a.json.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
