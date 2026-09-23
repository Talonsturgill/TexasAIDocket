"""Measure the nine SHIPPED PNGs at 432 px. Never planned, never asserted.

Every number in the artwork ledger's value block comes from here, which is the
compute-not-generate law applied to the deck's own description of itself.
"""
import json, numpy as np
from pathlib import Path
from PIL import Image

def L(rgb):
    s = np.asarray(rgb, float) / 255.0
    s = np.where(s <= 0.04045, s / 12.92, ((s + 0.055) / 1.055) ** 2.4)
    Y = 0.2126 * s[..., 0] + 0.7152 * s[..., 1] + 0.0722 * s[..., 2]
    return np.where(Y > 0.008856, 116 * np.cbrt(Y) - 16, 903.3 * Y)

rows = []
for n in range(1, 10):
    a = np.asarray(Image.open(f"out/2026-09-23/render/slide-{n:02d}.png")
                   .convert("RGB").resize((432, 540), Image.BOX), float)
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
Path("out/2026-09-23/measurements.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
