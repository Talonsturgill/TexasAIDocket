#!/usr/bin/env python3
"""measure.py — the deck's value arc, measured off the shipped PNGs.

Every prior deck here missed its own planned arc, and every one of them recorded the miss
rather than the plan. This writes what the renders actually are, on the same fixed grid the
prior runs used, so the ledger carries a measurement and never an intention.
"""
import json
from pathlib import Path
from PIL import Image
import numpy as np

RUN = "2026-09-04"
ROOT = Path(__file__).resolve().parents[2]
REN = ROOT / "out" / RUN / "render"

def lstar(png):
    im = Image.open(png).convert("RGB").resize((270, 338), Image.LANCZOS)
    a = np.asarray(im, dtype=float) / 255.0
    a = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    Y = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
    L = np.where(Y > 0.008856, 116 * np.cbrt(Y) - 16, 903.3 * Y)
    return L

out = {"run": RUN, "measured_on": "the nine shipped PNGs resampled to 270 by 338, the grid every prior run used", "per_frame": []}
Ls = []
for p in sorted(REN.glob("slide-0*.png")):
    L = lstar(p)
    med = float(np.median(L))
    Ls.append(med)
    out["per_frame"].append({"file": p.name, "median_L": round(med, 1),
                             "mean_L": round(float(L.mean()), 1),
                             "p05": round(float(np.percentile(L, 5)), 1),
                             "p95": round(float(np.percentile(L, 95)), 1)})
arr = np.array(Ls)
out["deck_median_L"] = round(float(np.median(arr)), 1)
out["mean_L"] = round(float(arr.mean()), 1)
out["sd_L"] = round(float(arr.std()), 1)
out["range_L"] = [round(float(arr.min()), 1), round(float(arr.max()), 1)]
out["planned"] = [24, 18, 21, 13, 88, 32, 28, 17, 25]
out["planned_deck_median"] = 24
(ROOT / "out" / RUN / "measurements.json").write_text(json.dumps(out, indent=2) + "\n")
print("per frame median L*:", [f["median_L"] for f in out["per_frame"]])
print("deck median", out["deck_median_L"], "against a plan of", out["planned_deck_median"])
print("range", out["range_L"], "sd", out["sd_L"])
