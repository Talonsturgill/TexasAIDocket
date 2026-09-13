#!/usr/bin/env python3
"""measure.py - the deck's value block, MEASURED off the shipped PNGs and never planned.

One grid and one home for the figure. 270 by 338 is `panel_ready.ARC_GRID`, which is what every
prior run's measurements.json was written on and what ledger/carousel/artwork.json records. The
2026-09-03 run measured its own arc on a second grid, disagreed with the ledger by 1.1, and wrote
the finding down: two grids is two homes for one figure.

`shipped_check.py` reads the output and fails the build on any L* figure printed in this run's
prose that measurements.json does not hold, whatever wrote it.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

RUN = Path(__file__).resolve().parent
GRID = (270, 338)                      # panel_ready.ARC_GRID, not a second opinion
LIGHT_L = 60.0                         # the light-deck line the artwork ledger keeps a cap on


def median_L(png: Path) -> float:
    im = Image.open(png).convert("RGB").resize(GRID, Image.LANCZOS)
    a = np.asarray(im, dtype=float) / 255.0
    a = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    Y = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
    L = np.where(Y > 0.008856, 116 * np.cbrt(Y) - 16, 903.3 * Y)
    return round(float(np.median(L)), 1)


def main() -> int:
    pngs = sorted((RUN / "render").glob("slide-0*.png"))
    if len(pngs) != 9:
        print(f"measure: {len(pngs)} render(s), expected 9", file=sys.stderr)
        return 1
    per = [median_L(p) for p in pngs]
    deck = round(float(np.median(per)), 1)
    out = {
        "date": RUN.name,
        "measured_on": "the nine shipped PNGs resampled to 270 by 338, panel_ready.ARC_GRID",
        "per_slide_median_L": per,
        "deck_median_L": deck,
        "darkest_frame": {"slide": per.index(min(per)) + 1, "L": min(per)},
        "brightest_frame": {"slide": per.index(max(per)) + 1, "L": max(per)},
        "light_cap_note": (f"LIGHT_L is {LIGHT_L} and this deck measures {deck}, so it "
                           f"{'adds to' if deck >= LIGHT_L else 'does not add to'} the light count"),
    }
    (RUN / "measurements.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
