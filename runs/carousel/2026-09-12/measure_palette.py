#!/usr/bin/env python3
"""measure_palette.py — the CIELAB distance from each proposed token to the last eight decks.

WHY THIS IS CODE. Both treatment directors estimated their dE by eye and both said, in as many
words, that the run had to measure it. They were right to refuse: a colour distance is arithmetic
and the compute-not-generate law covers it exactly like a numeral on a frame.

WHY THE METRIC IS CALIBRATED FIRST. Carousel no. 20 established that a bare dE is meaningless
without knowing what a random colour scores. Against the 81 hexes in this window, a random
colour's nearest neighbour has a median dE of about 29, and only about one in ten falls under
about 10. So this prints the calibration alongside the measurement, and a token under the tenth
percentile is a real collision rather than a number that merely looks small.

    python3 out/<run>/measure_palette.py --tokens name=#RRGGBB name=#RRGGBB ...
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXCLUSIONS = HERE / "palette_exclusions.json"


def hex_to_rgb(h: str) -> tuple[float, float, float]:
    h = h.strip().lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _f(t: float) -> float:
    return t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116


def rgb_to_lab(r: float, g: float, b: float) -> tuple[float, float, float]:
    def lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = lin(r), lin(g), lin(b)
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047
    y = (0.2126729 * r + 0.7151522 * g + 0.0721750 * b) / 1.00000
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883
    fx, fy, fz = _f(x), _f(y), _f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def lab(h: str):
    return rgb_to_lab(*hex_to_rgb(h))


def de76(a, b) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def nearest(h: str, pool: list[str]) -> tuple[str, float]:
    la = lab(h)
    best, bd = None, 1e9
    for p in pool:
        d = de76(la, lab(p))
        if d < bd:
            best, bd = p, d
    return best, bd


def calibrate(pool: list[str], n: int = 20000, seed: int = 20260911):
    """What a RANDOM colour scores against this pool. Without it a dE is a number with no scale."""
    rng = random.Random(seed)
    ds = []
    for _ in range(n):
        h = "#%02X%02X%02X" % (rng.randrange(256), rng.randrange(256), rng.randrange(256))
        ds.append(nearest(h, pool)[1])
    ds.sort()
    return {"n": n, "seed": seed,
            "p10": round(ds[n // 10], 2), "p25": round(ds[n // 4], 2),
            "median": round(ds[n // 2], 2), "p75": round(ds[3 * n // 4], 2)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", nargs="+", required=True, help="name=#RRGGBB")
    ap.add_argument("--out", default=str(HERE / "palette_measured.json"))
    args = ap.parse_args()

    pool = json.loads(EXCLUSIONS.read_text())
    cal = calibrate(pool)
    print(f"calibration against {len(pool)} hexes from the last eight decks: "
          f"a random colour's nearest neighbour is p10 {cal['p10']}, median {cal['median']}")
    print()

    rows = []
    for t in args.tokens:
        name, _, h = t.partition("=")
        near, d = nearest(h, pool)
        L, a, b = lab(h)
        verdict = ("COLLISION" if d < cal["p10"] else
                   "close" if d < cal["p25"] else "clear")
        rows.append({"token": name, "hex": h.upper(), "nearest_prior": near,
                     "dE76": round(d, 2), "L*": round(L, 1), "verdict": verdict})
        print(f"  {name:14s} {h.upper()}  L* {L:5.1f}   nearest {near}  dE {d:6.2f}   {verdict}")

    # A deck's tokens must also be tellable apart from EACH OTHER, which no prior run measured.
    print()
    worst = None
    for i, x in enumerate(rows):
        for y in rows[i + 1:]:
            d = de76(lab(x["hex"]), lab(y["hex"]))
            if worst is None or d < worst[2]:
                worst = (x["token"], y["token"], d)
    if worst:
        print(f"  closest pair INSIDE this deck: {worst[0]} and {worst[1]} at dE {worst[2]:.2f}")

    # The reserved red is reserved. A token that reads as it has spent a colour with no door.
    RESERVED = "#BF0A30"
    print()
    for r in rows:
        d = de76(lab(r["hex"]), lab(RESERVED))
        r["dE_to_reserved_red"] = round(d, 2)
        if d < 20:
            print(f"  WARN {r['token']} is dE {d:.2f} from the reserved red {RESERVED}")
    print(f"  every token measured against the reserved red {RESERVED}")

    Path(args.out).write_text(json.dumps(
        {"calibration": cal, "pool_size": len(pool), "tokens": rows,
         "closest_pair_inside_deck": {"a": worst[0], "b": worst[1], "dE76": round(worst[2], 2)}
         if worst else None}, indent=1) + "\n", encoding="utf-8")
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
