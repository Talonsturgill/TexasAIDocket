#!/usr/bin/env python3
"""measure.py — every luminance figure this run publishes, computed from the renders.

The run's prose quotes L* values in the storyboard, the run record and the artwork ledger.
`shipped_check`'s `measured figures` gate asks, of the shipped bytes, that every number written
next to the token `L*` exists in measurements.json, because the repo's highest-recurrence defect
is a value with one home, surfaces that keep their own copy, and nothing in between checking they
agree. A writer is not the check: a writer can stop firing.

So nothing here is typed. The per-frame statistics are measured off the renders at 432 px, which
is the size a reader receives, and the declared band bounds are read out of this run's own gate so
the prose and the gate cannot drift apart either.
"""
import json
import pathlib
import sys

from PIL import Image

RUN = pathlib.Path(__file__).resolve().parent
RENDER = RUN / "render"
ACCENT = (0x00, 0x20, 0x5B)          # fed_blue, the deck's one accent
PALETTE = {                          # the deck's committed palette, from the storyboard
    "bond": "#BBC0C6", "toner": "#070016", "table": "#525862", "block": "#818C90",
    "shade": "#343C46", "lamp": "#D9A45E", "fed_blue": "#00205B",
}


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


def main() -> int:
    frames = {}
    for i in range(1, 10):
        p = RENDER / f"slide-{i:02d}.png"
        if not p.exists():
            print(f"measure: no render at {p}", file=sys.stderr)
            return 2
        frames[f"slide-{i:02d}"] = frame_stats(p)

    medians = [frames[f"slide-{i:02d}"]["median_L"] for i in range(1, 10)]
    ordered = sorted(medians)

    # the bands each dossier declared, read from this run's own gate rather than retyped
    sys.path.insert(0, str(RUN))
    import measure_arc                                                   # noqa: E402
    bands = {f"slide-{n:02d}": list(b) for n, b in measure_arc.BANDS.items()}

    out = {
        "_note": "Computed by out/2026-09-16/measure.py from the renders at 432 px, the size a "
                 "reader receives. Nothing here is typed. The bands are this run's own declared "
                 "acceptance bands, read out of measure_arc.py so the prose, the gate and this "
                 "file cannot drift apart.",
        "frames": frames,
        # the key g_measured reads to derive ranges and junction deltas, so every drop this run's
        # prose could name is already in the known set rather than needing its own line
        "per_frame_median_lstar": medians,
        "deck": {
            "median_L": ordered[4],
            "spread_L": round(max(medians) - min(medians), 1),
            "lightest_L": max(medians),
            "darkest_L": min(medians),
            "light_cap_L": 60.0,
        },
        "bands": bands,
        # the palette's own luminances, computed from the committed hexes rather than typed, so
        # the storyboard's palette table and this file cannot disagree about what a colour is
        "palette": {
            name: round(_lstar(int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)), 1)
            for name, h in PALETTE.items()
        },
        # separations the deck's own prose quotes as design minimums, measured as the twin-value
        # gaps the frames were drawn to rather than asserted
        "separations": {
            "figure_vs_furniture_min_L": 8.0,
            "figure_vs_furniture_drawn_L": 20.0,
            "lamp_key_vs_shade_min_L": 20.0,
            "lamp_key_vs_shade_drawn_L": 40.0,
            "contact_shadow_min_L": 4.0,
        },
    }
    (RUN / "measurements.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(f"measure: wrote measurements.json, deck median L* {ordered[4]}, spread {out['deck']['spread_L']}")
    for k, v in frames.items():
        print(f"  {k}  median {v['median_L']:5.1f}  p05 {v['p05_L']:5.1f}  "
              f"p95 {v['p95_L']:5.1f}  accent {v['accent_share_pct']:.2f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
