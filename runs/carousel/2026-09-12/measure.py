#!/usr/bin/env python3
"""measure.py — read the deck's own pixels and answer the questions the plan asserts.

WHY THIS EXISTS FOR THIS DECK IN PARTICULAR. `ledger_check.check_register` counts light decks
over the last eight entries off `deck_median_L`, MEASURED ON THE SHIPPED PNGS. The window this
deck joins already holds 2026-09-09 at 71.1 against a LIGHT_L of 60.0 and a LIGHT_CAP of 1, and
September 3rd's waiver rolls out of the window with it. **So a paper register is available here
if and only if this deck measures under 60**, and two ledger entries in a row record a run that
declared a value band and did not measure it until round three.

It also answers the per frame assertions the dossiers make, so a pixel critic is grading against
numbers rather than against adjectives:

    median L*        per frame and for the deck, in CIELAB, off the rendered PNG
    p05 and p95      the real dark and the real light, which is what value structure means
    accent share     the fraction of the frame within 12 dE of #9A3B2A, so the accent law is
                     counted rather than asserted

    python3 out/<run>/measure.py --render-dir out/<run>/render
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

ACCENT = "#9A3B2A"
ACCENT_TOL = 12.0        # dE76 inside which a pixel counts as the accent


def srgb_to_lab(arr: np.ndarray) -> np.ndarray:
    """arr is HxWx3 uint8. Returns HxWx3 float L*, a*, b*."""
    c = arr.astype(np.float64) / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = lin[..., 0], lin[..., 1], lin[..., 2]
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047
    y = (0.2126729 * r + 0.7151522 * g + 0.0721750 * b) / 1.00000
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883

    def f(t):
        return np.where(t > 216 / 24389, np.cbrt(t), (24389 / 27 * t + 16) / 116)

    fx, fy, fz = f(x), f(y), f(z)
    return np.stack([116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)], axis=-1)


def hex_lab(h: str) -> np.ndarray:
    h = h.lstrip("#")
    rgb = np.array([[[int(h[i:i + 2], 16) for i in (0, 2, 4)]]], dtype=np.uint8)
    return srgb_to_lab(rgb)[0, 0]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--render-dir", required=True)
    args = ap.parse_args()
    rd = Path(args.render_dir)
    acc = hex_lab(ACCENT)

    frames, medians = {}, []
    for png in sorted(rd.glob("slide-*.png")):
        im = Image.open(png).convert("RGB")
        # Measure at feed width. A deck is judged at 432 px and so is its value.
        im = im.resize((432, round(432 * im.height / im.width)), Image.LANCZOS)
        lab = srgb_to_lab(np.asarray(im))
        L = lab[..., 0]
        d = np.sqrt(((lab - acc) ** 2).sum(axis=-1))
        frames[png.stem] = {
            "median_L": round(float(np.median(L)), 1),
            "p05_L": round(float(np.percentile(L, 5)), 1),
            "p95_L": round(float(np.percentile(L, 95)), 1),
            "accent_share_pct": round(float((d < ACCENT_TOL).mean() * 100), 2),
        }
        medians.append(frames[png.stem]["median_L"])

    deck_median = round(float(np.median(medians)), 1) if medians else None
    accent_frames = [k for k, v in frames.items() if v["accent_share_pct"] >= 0.10]
    out = {
        "frames": frames,
        "deck_median_L": deck_median,
        "light_L_threshold": 60.0,
        "under_light_threshold": (deck_median is not None and deck_median < 60.0),
        "accent_frames": sorted(accent_frames),
        "accent_frame_count": len(accent_frames),
    }
    (rd.parent / "measurements.json").write_text(json.dumps(out, indent=1) + "\n")

    for k in sorted(frames):
        v = frames[k]
        print(f"  {k}  median {v['median_L']:5.1f}  p05 {v['p05_L']:5.1f}  "
              f"p95 {v['p95_L']:5.1f}  accent {v['accent_share_pct']:5.2f}%")
    print(f"\n  deck median L* {deck_median}  "
          f"{'UNDER' if out['under_light_threshold'] else 'OVER'} the 60.0 light threshold")
    print(f"  accent on {len(accent_frames)} frame(s): {', '.join(sorted(accent_frames)) or 'none'}")


if __name__ == "__main__":
    main()
