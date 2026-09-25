"""Measure the nine SHIPPED slides at 432 px. Never planned, never asserted.

The run's own measurement was never copied into this folder, so this recomputes it from the
shipped frames beside it, by the same method as 2026-09-23's measure.py: box downsample to
432 by 540 and CIE L* from linearised sRGB. It reads what shipped, not a scratch render, so the
figures describe the deck a reader receives.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent


def L(rgb):
    s = np.asarray(rgb, float) / 255.0
    s = np.where(s <= 0.04045, s / 12.92, ((s + 0.055) / 1.055) ** 2.4)
    Y = 0.2126 * s[..., 0] + 0.7152 * s[..., 1] + 0.0722 * s[..., 2]
    return np.where(Y > 0.008856, 116 * np.cbrt(Y) - 16, 903.3 * Y)


def slide(n):
    for ext in ("png", "webp"):
        p = HERE / f"slide-{n:02d}.{ext}"
        if p.exists():
            return p
    raise FileNotFoundError(f"slide-{n:02d} is not in {HERE}")


rows = []
for n in range(1, 10):
    a = np.asarray(Image.open(slide(n)).convert("RGB").resize((432, 540), Image.BOX), float)
    lum = L(a)
    rows.append({"slide": n,
                 "median_L": round(float(np.median(lum)), 1),
                 "p05_L": round(float(np.percentile(lum, 5)), 1),
                 "p95_L": round(float(np.percentile(lum, 95)), 1),
                 "range_L": round(float(np.percentile(lum, 95) - np.percentile(lum, 5)), 1)})
med = [r["median_L"] for r in rows]
out = {"at_px": 432,
       "per_frame": rows,
       "deck_median_L": round(float(np.median(med)), 1),
       "arc": med,
       "max_adjacent_step_L": round(float(max(abs(med[i + 1] - med[i]) for i in range(8))), 1),
       "spread_L": round(float(max(med) - min(med)), 1)}
(HERE / "measurements.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
