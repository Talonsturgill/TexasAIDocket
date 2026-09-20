#!/usr/bin/env python3
"""measure.py — the deck's value structure, measured off the nine shipped PNGs.

NOTHING HERE IS PLANNED OR ASSERTED. Every figure is read off the rendered images at 432 px,
which is the size a reader meets the deck at, and the planned arc is read out of the storyboard's
own `Frame median L* planned at N` lines so the two can be compared without either being retyped.

WHY 432 px. ILLUSTRATION_SYSTEM.md's whole diagnosis was made at feed scale, and a value
structure measured at 1080 px is a measurement of a thing nobody sees.
"""
from __future__ import annotations
import json, re, statistics, sys
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
RUN = Path(__file__).resolve().parent
DATE = RUN.name


def lstar(img: Image.Image) -> np.ndarray:
    a = np.asarray(img.convert("L"), dtype=float) / 255.0
    lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    return np.where(lin > 0.008856, 116 * np.cbrt(lin) - 16, 903.3 * lin)


def main() -> int:
    render = RUN / "render"
    if not (render / "slide-01.png").exists():
        render = ROOT / "runs" / "carousel" / DATE / "render"
    med = []
    for i in range(1, 10):
        im = Image.open(render / f"slide-{i:02d}.png").resize((432, 540), Image.LANCZOS)
        med.append(round(float(np.median(lstar(im))), 1))

    board = (RUN / "storyboard.md")
    if not board.exists():
        board = ROOT / "runs" / "carousel" / DATE / "storyboard.md"
    # THE PHRASE WRAPS. yaml folds a long value_structure across lines, so three of the nine
    # planned figures sat with a newline between "planned" and "at 16." and a single line
    # regex found six. Whitespace is collapsed before the match rather than the storyboard
    # reflowed, because the plan is prose and prose wraps.
    flat = " ".join(board.read_text(encoding="utf-8").split())
    planned = [int(m) for m in re.findall(r"Frame median L\* planned at (\d+)\.", flat)]

    adj = [round(abs(med[i + 1] - med[i]), 1) for i in range(8)]
    out = {
        "_note": ("Measured at 432 px off the shipped PNGs by out/%s/measure.py. The planned arc "
                  "is read out of the storyboard's own lines rather than retyped, so a drift "
                  "between plan and print is visible without trusting either copy." % DATE),
        "grid": "432x540, the feed thumb",
        "per_frame_median_lstar": med,
        "planned_median_lstar": planned,
        "deck": {
            "median_of_frame_medians": round(statistics.median(med), 1),
            "spread_L": round(max(med) - min(med), 1),
            "max_adjacent_delta": max(adj),
            "mean_adjacent_delta": round(sum(adj) / len(adj), 2),
            "adjacent_deltas": adj,
        },
        "reference": {
            "this_repo_historical_median_adjacent_delta": 21.0,
            "sibling_median_adjacent_delta": 2.6,
            "source": ("knowledge/carousel/ILLUSTRATION_SYSTEM.md, THE DECK IS THE UNIT, which "
                       "measured nineteen decks here against the sibling's hundred and twenty "
                       "seven"),
        },
    }
    (RUN / "measurements.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("measured medians:", med)
    print("planned          :", planned)
    print("adjacent deltas  :", adj, " max", out["deck"]["max_adjacent_delta"],
          " mean", out["deck"]["mean_adjacent_delta"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
