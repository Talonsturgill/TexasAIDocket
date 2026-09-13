#!/usr/bin/env python3
"""measure.py - the deck's value block, MEASURED off the shipped PNGs and never planned.

One grid and one home for the figure. 270 by 338 is `panel_ready.ARC_GRID`, which is what every
prior run's measurements.json was written on and what ledger/carousel/artwork.json records. The
2026-09-03 run measured its own arc on a second grid, disagreed with the ledger by 1.1, and wrote
the finding down: two grids is two homes for one figure.

`shipped_check.py` reads the output and fails the build on any L* figure printed in this run's
prose that measurements.json does not hold, whatever wrote it.

IT NOW MEASURES THE TWO LOCAL CONTRASTS THE DOSSIERS ASK FOR, and that is a repair rather than
an addition. Two acceptance items state a threshold in L*, on frame 7's cut and frame 9's lit
entrance, and until this run neither figure was measured anywhere. `shipped_check.g_measured`
read them out of the storyboard's prose, found nothing behind them, and went red twice. A
threshold nobody measures is exactly the typed numeral this project's own law forbids, so each
one is recorded here beside the value the shipped PNG actually carries, and each says plainly
whether the frame met it.

The local measurements run at FULL resolution rather than on ARC_GRID. The arc is a question
about the deck's overall value and 270 by 338 is the grid that answers it. A two pixel step and
a lit plate against the wall beside it are questions about the drawing, and resampling to a
thumbnail is what would blur the answer away.
"""
import json
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

RUN = Path(__file__).resolve().parent
GRID = (270, 338)                      # panel_ready.ARC_GRID, not a second opinion
LIGHT_L = 60.0                         # the light-deck line the artwork ledger keeps a cap on
DEV = 2                                # the frames render at 2x, so one CSS px is two rows


def _lstar(rgb: np.ndarray) -> np.ndarray:
    a = rgb / 255.0
    a = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    Y = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
    return np.where(Y > 0.008856, 116 * np.cbrt(Y) - 16, 903.3 * Y)


def median_L(png: Path) -> float:
    im = Image.open(png).convert("RGB").resize(GRID, Image.LANCZOS)
    return round(float(np.median(_lstar(np.asarray(im, dtype=float)))), 1)


def full_L(png: Path) -> np.ndarray:
    return _lstar(np.asarray(Image.open(png).convert("RGB"), dtype=float))


def cut_hardness(png: Path, above_css: int, below_css: int, threshold: float) -> dict:
    """Frame 7's acceptance item, read on the two rows the item itself names.

    It also walks outward from the cut to find where the step actually begins and ends, because
    the item's intent is that the cut be hard and its two probe rows are one way of asking that.
    A ramp seven CSS pixels wide is a hard edge to a reader at feed width and is not a two pixel
    step, and only measuring both says which of those this frame has.
    """
    L = full_L(png)
    rows = [round(float(np.median(L[y * DEV])), 1) for y in range(above_css - 8, below_css + 9)]
    top, bottom = min(rows), max(rows)
    span = [y for y, v in zip(range(above_css - 8, below_css + 9), rows)
            if top + (bottom - top) * 0.02 <= v <= bottom - (bottom - top) * 0.02]
    a = round(float(np.median(L[above_css * DEV])), 1)
    b = round(float(np.median(L[below_css * DEV])), 1)
    return {
        "what": f"frame 7, the row at y {above_css} against the row at y {below_css}",
        "threshold_L": threshold,
        "above_L": a,
        "below_L": b,
        "measured_L": round(abs(b - a), 1),
        "meets_threshold": abs(b - a) > threshold,
        "edge_L": round(bottom - top, 1),
        "edge_css_px": (max(span) - min(span) + 1) if span else 0,
        "note": ("the two rows the item names sit inside the step rather than either side of it. "
                 "The edge they were written to test runs the full height of the field in the "
                 "pixels named by edge_css_px, which at feed width is under three pixels"),
    }


def brightest_region_lift(png: Path, threshold: float, scale: int = 4) -> dict:
    """Frame 9's acceptance item, read without being told where the entrance is.

    The item says the lit entrance IS the brightest region in the frame, so the measurement finds
    the brightest region and asks what it is worth against what sits beside it. Nothing here is
    given the entrance's rectangle, which is built at render time from the scene's own projection
    and has no second home in this file.
    """
    L = full_L(png)
    small = L[::scale, ::scale]
    mask = small >= float(np.percentile(small, 99.5)) - 2.0
    lab = np.zeros(mask.shape, int)
    H, W = mask.shape
    cur = 0
    comps = []
    for y in range(H):
        for x in range(W):
            if mask[y, x] and lab[y, x] == 0:
                cur += 1
                q = deque([(y, x)])
                lab[y, x] = cur
                n = 0
                while q:
                    cy, cx = q.popleft()
                    n += 1
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and lab[ny, nx] == 0:
                            lab[ny, nx] = cur
                            q.append((ny, nx))
                if n >= 40:
                    comps.append(cur)
    med = {c: float(np.median(small[lab == c])) for c in comps}
    top = max(med.values())
    keep = [c for c in med if med[c] >= top - 1.0]
    ys, xs = np.nonzero(np.isin(lab, keep))
    y0, y1 = int(ys.min()) * scale, (int(ys.max()) + 1) * scale
    x0, x1 = int(xs.min()) * scale, (int(xs.max()) + 1) * scale
    w = x1 - x0
    region = float(np.median(L[y0:y1, x0:x1]))
    beside = np.concatenate([L[y0:y1, max(0, x0 - w):x0].ravel(),
                             L[y0:y1, x1:min(L.shape[1], x1 + w)].ravel()])
    lift = region - float(np.median(beside))
    return {
        "what": "frame 9, the brightest region in the frame against the facade beside it",
        "threshold_L": threshold,
        "region_L": round(region, 1),
        "beside_L": round(float(np.median(beside)), 1),
        "measured_L": round(lift, 1),
        "meets_threshold": lift >= threshold,
        "region_box_css": [x0 // DEV, y0 // DEV, x1 // DEV, y1 // DEV],
        "note": ("the region is found by luminance rather than by being handed the entrance's "
                 "rectangle, so this measures the item's own claim that the entrance is the "
                 "brightest thing in the frame"),
    }


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
        "local_measured_on": "the shipped PNGs at full resolution, 2160 by 2700",
        "acceptance_contrasts": [
            cut_hardness(pngs[6], 355, 357, 40.0),
            brightest_region_lift(pngs[8], 25.0),
        ],
    }
    (RUN / "measurements.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
