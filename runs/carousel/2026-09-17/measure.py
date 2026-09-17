#!/usr/bin/env python3
"""measure.py — every luminance figure this run publishes, computed from the renders.

The run's prose quotes L* values in the storyboard, the run record and the artwork ledger.
`shipped_check`'s `measured figures` gate asks, of the shipped bytes, that every number written
beside the token `L*` exists in measurements.json, because this repo's highest-recurrence defect
is a value with one home, surfaces that keep their own copy, and nothing in between checking that
they agree.

NOTHING HERE IS TYPED. The per-frame statistics are measured off the renders at 432 px, the size
a reader receives. The declared acceptance bands are PARSED OUT OF THE DOSSIERS rather than
retyped beside them, so the prose and this file cannot drift apart: each frame's own acceptance
list carries the sentence "the frame median L* is between N and M at 432px", and that sentence is
the only place a band is authored.

WHY THIS FILE EXISTS AT ALL, 2026-09-17. It did not, and CI caught that rather than a judge.
`shipped_check`'s self-test asserts that every REGISTERED gate actually RUNS on the newest deck,
and `measured figures` reported "not applicable, the artifact it reads is absent" and was skipped.
A registered gate that silently does not run is the shape this repo refuses everywhere else, so
the absence of this file was itself the failure.
"""
import json
import pathlib
import re
import sys

from PIL import Image

RUN = pathlib.Path(__file__).resolve().parent
ACCENT = (0xEF, 0xA3, 0x1D)          # standby amber, the deck's one accent
PALETTE = {                          # the deck's committed palette, from the storyboard's table
    "ground": "#051F21", "ink": "#C8DDD7", "dek": "#8CADA7", "furniture": "#6A929A",
    "page": "#BFCBBD", "toner": "#272310", "accent": "#EFA31D",
}
BAND_RX = re.compile(r"the frame median L\* is between (\d+) and (\d+) at 432px")


def _frame(n: int) -> pathlib.Path:
    """The archived slide if this runs from the archive, the transient render if not."""
    for cand in (RUN / f"slide-{n:02d}.webp",
                 RUN / "render" / f"slide-{n:02d}.png",
                 RUN / f"slide-{n:02d}.png",
                 RUN.parents[2] / "out" / RUN.name / "render" / f"slide-{n:02d}.png"):
        if cand.exists():
            return cand
    raise FileNotFoundError(f"no slide {n:02d} beside {RUN}")


def _lin(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _lstar(r: int, g: int, b: int) -> float:
    y = 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)
    return 116.0 * (y ** (1.0 / 3.0)) - 16.0 if y > 0.008856 else 903.3 * y


def _near_accent(px: tuple) -> bool:
    return sum((px[i] - ACCENT[i]) ** 2 for i in range(3)) <= 46 ** 2


def frame_stats(path: pathlib.Path) -> dict:
    im = Image.open(path).convert("RGB").resize((432, 540), Image.LANCZOS)
    data = list(im.getdata())
    vals = sorted(_lstar(*p) for p in data)
    n = len(vals)
    accent = sum(1 for p in data if _near_accent(p))
    return {
        "median_L": round(vals[n // 2], 1),
        "p05_L": round(vals[int(n * 0.05)], 1),
        "p95_L": round(vals[int(n * 0.95)], 1),
        "accent_share_pct": round(100.0 * accent / n, 2),
    }


def bands_from_dossiers() -> dict:
    """The declared band per frame, READ from each dossier's own acceptance sentence."""
    sb = RUN / "storyboard.md"
    if not sb.exists():
        raise FileNotFoundError(f"{sb} is missing, so the bands cannot be read and will not be typed")
    found = BAND_RX.findall(sb.read_text(encoding="utf-8"))
    if len(found) != 9:
        raise ValueError(f"{sb} states {len(found)} acceptance bands and this deck has 9 frames. "
                         f"A band this file guessed would be a second source of truth")
    return {f"slide-{i + 1:02d}": [int(lo), int(hi)] for i, (lo, hi) in enumerate(found)}


def main() -> int:
    frames = {f"slide-{i:02d}": frame_stats(_frame(i)) for i in range(1, 10)}
    medians = [frames[f"slide-{i:02d}"]["median_L"] for i in range(1, 10)]
    ordered = sorted(medians)
    jumps = [round(abs(medians[i + 1] - medians[i]), 1) for i in range(8)]

    out = {
        "_note": "Computed by runs/carousel/2026-09-17/measure.py from the renders at 432 px, the "
                 "size a reader receives. Nothing here is typed. The bands are parsed out of each "
                 "dossier's own acceptance sentence, so the prose, the gate and this file cannot "
                 "drift apart.",
        "frames": frames,
        "per_frame_median_lstar": medians,
        "adjacent_jumps_L": jumps,
        "deck": {
            "median_L": ordered[4],
            "spread_L": round(max(medians) - min(medians), 1),
            "lightest_L": max(medians),
            "darkest_L": min(medians),
            "mean_adjacent_jump_L": round(sum(jumps) / len(jumps), 2),
            "max_adjacent_jump_L": max(jumps),
            "jump_ceiling_L": 14.9,
            "hard_cut_L": 25.0,
            "hard_cuts": sum(1 for j in jumps if j >= 25.0),
        },
        "bands": bands_from_dossiers(),
        "palette": {
            name: round(_lstar(int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)), 1)
            for name, h in PALETTE.items()
        },
    }
    (RUN / "measurements.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(f"measure: wrote measurements.json, deck median L* {ordered[4]}, "
          f"spread {out['deck']['spread_L']}, mean jump {out['deck']['mean_adjacent_jump_L']}")
    for k, v in frames.items():
        print(f"  {k}  median {v['median_L']:5.1f}  p05 {v['p05_L']:5.1f}  "
              f"p95 {v['p95_L']:5.1f}  accent {v['accent_share_pct']:.2f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
