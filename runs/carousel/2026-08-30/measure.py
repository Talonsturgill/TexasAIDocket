#!/usr/bin/env python3
"""The run's own luminance record, measured off the rendered PNGs.

WHY THIS EXISTS. `shipped_check`'s `measured figures` gate reads `measurements.json` and asks,
of the shipped bytes, whether every `L*` figure the run's prose prints is a number the run
actually measured. That gate had never run on a deck here, because nothing wrote the file it
reads, so a registered gate reported clean by being unreachable. That is the same shape the
file's own docstring warns about two gates further down.

Every number below is computed from the pixels. Nothing is typed and nothing is carried over
from a previous deck, which is the defect the gate exists for: a value with one home, surfaces
that keep their own copy, and nothing in between checking they agree.
"""
from __future__ import annotations

import json
import statistics as st
from pathlib import Path

from PIL import Image

RUN = Path(__file__).resolve().parent
RENDER = RUN / "render"


def lstar(v: int) -> float:
    """CIE L* from an sRGB grey level, through the linear-light step rather than around it."""
    c = v / 255.0
    c = c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 116 * (c ** (1 / 3)) - 16 if c > 0.008856 else 903.3 * c


# A lookup, so the transfer function runs 256 times rather than once per pixel.
LUT = [lstar(v) for v in range(256)]

frames = []
for p in sorted(RENDER.glob("slide-0*.png")):
    im = Image.open(p).convert("L")
    W, H = im.size
    # Downsampled to a fixed grid so the figure does not move with the render's own resolution.
    small = im.resize((270, 338), Image.BOX)
    vals = [LUT[v] for v in small.getdata()]
    third = small.crop((0, int(338 * 2 / 3), 270, 338))
    bot = [LUT[v] for v in third.getdata()]
    frames.append({
        "frame": int(p.stem.split("-")[1]),
        "median_lstar": round(st.median(vals), 1),
        "mean_lstar": round(st.fmean(vals), 1),
        "stdev_lstar": round(st.pstdev(vals), 1),
        "bottom_third_median_lstar": round(st.median(bot), 1),
        "bottom_third_stdev_lstar": round(st.pstdev(bot), 1),
    })

med = [f["median_lstar"] for f in frames]
out = {
    "run": RUN.name,
    "note": ("Measured off the rendered PNGs by measure.py. L* from sRGB grey through the "
             "linear-light step. Sampled on a fixed 270 by 338 grid so the figure does not "
             "move with the render's resolution."),
    "frames": frames,
    "per_frame_median_lstar": med,
    "deck_median_lstar": round(st.median(med), 1),
    "value_range_lstar": round(max(med) - min(med), 1),
    "darkest_frame": frames[med.index(min(med))]["frame"],
    "lightest_frame": frames[med.index(max(med))]["frame"],
}
(RUN / "measurements.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(f"measure: {len(frames)} frame(s), median L* {out['deck_median_lstar']}, "
      f"range {out['value_range_lstar']} from frame {out['darkest_frame']} to "
      f"{out['lightest_frame']}")
