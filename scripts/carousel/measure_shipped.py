#!/usr/bin/env python3
"""measure_shipped.py — write a run's measurements.json from the frames it SHIPPED.

    python3 scripts/carousel/measure_shipped.py --run 2026-09-27
    python3 scripts/carousel/measure_shipped.py --self-test

WHY THIS EXISTS

`shipped_check --self-test` asserts that every registered gate runs on the newest deck, and the
`measured figures` gate has nothing to read without `runs/carousel/<date>/measurements.json`. So a
deck that ships without the file turns CI red after the deck is finished. Nothing in the routine
said to write it, and every run since 2026-09-20 wrote its own `measure.py` beside the frames,
each one copied from the run before with its docstring changed. On 2026-09-26 and 2026-09-27 the
run found out from a red CI job, after the round cap, and paid a push and a CI cycle to add it.
The backlog had named the same gap on 2026-09-08.

This is that script, once. The method is the one the 2026-09-24, 2026-09-26 and 2026-09-27 runs
shipped: each SHIPPED frame box-downsampled to 432 by 540, CIE L* from linearised sRGB, and the
median, 5th and 95th percentiles per frame. It reads what shipped, not a scratch render, so the
figures describe the deck a reader receives. Its self-test reproduces those three runs' own
files byte for byte, so the lift changed nothing about what a run measures.

EXIT CODES: 0 written, 1 refused (no run directory, no frames, or a gap in the frame numbers).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS = REPO_ROOT / "runs" / "carousel"
AT = (432, 540)
FRAME = re.compile(r"^slide-(\d{2})\.(png|webp)$")


def lstar(rgb):
    s = np.asarray(rgb, float) / 255.0
    s = np.where(s <= 0.04045, s / 12.92, ((s + 0.055) / 1.055) ** 2.4)
    y = 0.2126 * s[..., 0] + 0.7152 * s[..., 1] + 0.0722 * s[..., 2]
    return np.where(y > 0.008856, 116 * np.cbrt(y) - 16, 903.3 * y)


def frames(d: Path) -> list:
    """The shipped frames in order, each in the format the site serves: WebP, else PNG.

    `site_context` resolves webp then png per slide. ship_images deletes a webp that misses the
    quality floor and deletes a png once its webp clears it, so both exist only after `--keep` or
    an interrupted cleanup, and then a reader receives the WebP (Codex, PR 378)."""
    found = {}
    for p in d.iterdir():
        m = FRAME.match(p.name)
        if m and (int(m.group(1)) not in found or m.group(2) == "webp"):
            found[int(m.group(1))] = p
    if not found:
        raise ValueError(f"no slide-NN.png or slide-NN.webp in {d}")
    nums = sorted(found)
    if nums != list(range(1, len(nums) + 1)):
        raise ValueError(f"frame numbers in {d} are {nums}, not 1 to {len(nums)}")
    return [found[n] for n in nums]


def measure(d: Path) -> dict:
    rows = []
    for n, p in enumerate(frames(d), 1):
        lum = lstar(np.asarray(Image.open(p).convert("RGB").resize(AT, Image.BOX), float))
        rows.append({"slide": n,
                     "median_L": round(float(np.median(lum)), 1),
                     "p05_L": round(float(np.percentile(lum, 5)), 1),
                     "p95_L": round(float(np.percentile(lum, 95)), 1),
                     "range_L": round(float(np.percentile(lum, 95) - np.percentile(lum, 5)), 1)})
    med = [r["median_L"] for r in rows]
    steps = [abs(med[i + 1] - med[i]) for i in range(len(med) - 1)]
    return {"at_px": AT[0],
            "per_frame": rows,
            "deck_median_L": round(float(np.median(med)), 1),
            "arc": med,
            "max_adjacent_step_L": round(float(max(steps)), 1) if steps else 0.0,
            "spread_L": round(float(max(med) - min(med)), 1)}


def write(d: Path) -> Path:
    out = d / "measurements.json"
    out.write_text(json.dumps(measure(d), indent=1) + "\n", encoding="utf-8")
    return out


def self_test() -> int:
    failures = 0

    def ok(name, cond, detail=""):
        nonlocal failures
        print(("ok    " if cond else "FAIL  ") + name + ("" if cond else f"  {detail}"))
        failures += 0 if cond else 1

    # The CIE anchors: black is 0, white is 100, and 18 percent grey sits near 50.
    ok("black reads L* 0", abs(float(lstar([[0, 0, 0]])[0]) - 0.0) < 1e-9)
    ok("white reads L* 100", abs(float(lstar([[255, 255, 255]])[0]) - 100.0) < 1e-6)
    ok("sRGB 119 grey reads L* 50 to within 0.3", abs(float(lstar([[119, 119, 119]])[0]) - 50.0) < 0.3)

    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        for n, v in ((1, 0), (2, 119), (3, 255)):
            Image.new("RGB", (1080, 1350), (v, v, v)).save(d / f"slide-{n:02d}.png")
        m = measure(d)
        ok("three flat frames give an arc of 0, about 50 and 100",
           m["arc"][0] == 0.0 and abs(m["arc"][1] - 50.0) < 0.3 and m["arc"][2] == 100.0, str(m["arc"]))
        ok("...a spread of 100 and a largest step of about 50",
           m["spread_L"] == 100.0 and abs(m["max_adjacent_step_L"] - 50.0) < 0.3, str(m))
        Image.new("RGB", (1080, 1350), (255, 255, 255)).save(d / "slide-02.webp")
        ok("a WebP wins over a PNG of the same number, as the site serves it",
           frames(d)[1].suffix == ".webp")
        (d / "slide-03.png").unlink()
        Image.new("RGB", (1080, 1350), (9, 9, 9)).save(d / "slide-04.png")
        try:
            frames(d)
            ok("a gap in the frame numbers is refused", False, "frames() returned")
        except ValueError:
            ok("a gap in the frame numbers is refused", True)
    with tempfile.TemporaryDirectory() as t:
        try:
            frames(Path(t))
            ok("a directory with no frames is refused", False, "frames() returned")
        except ValueError:
            ok("a directory with no frames is refused", True)

    # THE LIFT CHANGED NOTHING. These three runs shipped a measure.py of their own, by this
    # method, and each wrote the measurements.json that is committed beside its frames.
    for date in ("2026-09-24", "2026-09-26", "2026-09-27"):
        d = RUNS / date
        f = d / "measurements.json"
        if not f.exists():
            ok(f"{date} is present to compare against", False, f"no {f}")
            continue
        got = json.dumps(measure(d), indent=1) + "\n"
        ok(f"{date}: reproduces the committed measurements.json byte for byte",
           got == f.read_text(encoding="utf-8"))

    print(f"\nmeasure_shipped self-test: {'all passed' if not failures else f'{failures} FAILED'}")
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", help="the run date, e.g. 2026-09-27")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.run:
        print("measure_shipped: pass --run <date> or --self-test", file=sys.stderr)
        return 1
    d = RUNS / a.run
    if not d.is_dir():
        print(f"measure_shipped: no run directory {d}", file=sys.stderr)
        return 1
    try:
        out = write(d)
    except ValueError as e:
        print(f"measure_shipped: {e}", file=sys.stderr)
        return 1
    m = json.loads(out.read_text(encoding="utf-8"))
    print(f"measure_shipped: wrote {out.relative_to(REPO_ROOT)}, {len(m['per_frame'])} frame(s) at "
          f"{m['at_px']} px, deck median L* {m['deck_median_L']}, arc {m['arc']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
