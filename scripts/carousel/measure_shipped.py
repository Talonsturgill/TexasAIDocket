#!/usr/bin/env python3
"""measure_shipped.py — write a run's measurements.json from the frames it SHIPPED.

    python3 scripts/carousel/measure_shipped.py --run 2026-09-27
    python3 scripts/carousel/measure_shipped.py --check              the newest shipped deck
    python3 scripts/carousel/measure_shipped.py --check --run 2026-09-27
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

`--check` recomputes and compares, and writes nothing. CI runs it on the newest shipped deck, the
latest run directory with a copy.json as `shipped_check` defines it, because `shipped_check` reads
the committed file and a frame re-rendered after the file was written would leave the two agreeing
about bytes a reader never receives (Codex, PR 378).

EXIT CODES: 0 written or matching, 1 refused or stale (no run directory, no copy.json, a frame
copy.json names is missing, or the committed file disagrees with the frames).
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


def lstar(rgb):
    s = np.asarray(rgb, float) / 255.0
    s = np.where(s <= 0.04045, s / 12.92, ((s + 0.055) / 1.055) ** 2.4)
    y = 0.2126 * s[..., 0] + 0.7152 * s[..., 1] + 0.0722 * s[..., 2]
    return np.where(y > 0.008856, 116 * np.cbrt(y) - 16, 903.3 * y)


def frames(d: Path) -> list:
    """The shipped frames in order, exactly the set the site serves.

    The count is copy.json's `slides`, taken the way `site_context` takes it, never inferred from
    the files present: a deck missing its last frame, or holding a stale frame past its end, would
    otherwise measure as a different deck from the one a reader receives (Codex, PR 378). Each
    frame is its WebP, else its PNG. `site_context` resolves them in that order, ship_images deletes
    a webp that misses the quality floor and deletes a png once its webp clears it, so both exist
    only after `--keep` or an interrupted cleanup, and then a reader receives the WebP. A file past
    the deck's count is ignored, as the site ignores it."""
    cp = d / "copy.json"
    if not cp.exists():
        raise ValueError(f"no copy.json in {d}, so the deck's slide count is unknown")
    planned = json.loads(cp.read_text(encoding="utf-8")).get("slides")
    n = len(planned) if isinstance(planned, (list, dict)) else 0
    if n == 0:
        raise ValueError(f"{cp} names no slides")
    out, missing = [], []
    for i in range(1, n + 1):
        for ext in ("webp", "png"):
            p = d / f"slide-{i:02d}.{ext}"
            if p.exists():
                out.append(p)
                break
        else:
            missing.append(f"slide-{i:02d}")
    if missing:
        raise ValueError(f"{d} is missing {', '.join(missing)} of the {n} slides copy.json names")
    return out


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


def newest_shipped() -> Path | None:
    runs = sorted(p for p in RUNS.glob("2*") if (p / "copy.json").exists()) if RUNS.exists() else []
    return runs[-1] if runs else None


def check(d: Path) -> list:
    """What is wrong with d's committed measurements.json against its frames. Empty when it matches."""
    f = d / "measurements.json"
    if not f.exists():
        return [f"{d.name}: no measurements.json. Run measure_shipped.py --run {d.name}"]
    want = json.dumps(measure(d), indent=1) + "\n"
    if f.read_text(encoding="utf-8") == want:
        return []
    have = json.loads(f.read_text(encoding="utf-8"))
    new = json.loads(want)
    out = [f"{d.name}: measurements.json does not match the shipped frames. Run measure_shipped.py "
           f"--run {d.name} after the last frame change, and correct any prose that printed the old "
           f"figures"]
    if have.get("arc") != new.get("arc"):
        out.append(f"  arc committed {have.get('arc')}, measured {new.get('arc')}")
    return out


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

    def deck(d, n):
        (d / "copy.json").write_text(json.dumps({"slides": {str(i): {} for i in range(1, n + 1)}}))

    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        deck(d, 3)
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
        Image.new("RGB", (1080, 1350), (9, 9, 9)).save(d / "slide-04.png")
        ok("a stale frame past copy.json's count is ignored, as the site ignores it",
           len(frames(d)) == 3 and len(measure(d)["arc"]) == 3)
        (d / "slide-03.png").unlink()
        try:
            frames(d)
            ok("a deck missing a frame copy.json names is refused", False, "frames() returned")
        except ValueError:
            ok("a deck missing a frame copy.json names is refused", True)
    with tempfile.TemporaryDirectory() as t:
        Image.new("RGB", (1080, 1350), (9, 9, 9)).save(Path(t) / "slide-01.png")
        try:
            frames(Path(t))
            ok("a directory with no copy.json is refused", False, "frames() returned")
        except ValueError:
            ok("a directory with no copy.json is refused", True)

    # --check SEES A FRAME CHANGED AFTER THE FILE WAS WRITTEN, and a missing file.
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        deck(d, 2)
        for n, v in ((1, 40), (2, 200)):
            Image.new("RGB", (1080, 1350), (v, v, v)).save(d / f"slide-{n:02d}.png")
        ok("--check reports a missing measurements.json", len(check(d)) == 1)
        write(d)
        ok("--check passes a file written from the frames in front of it", check(d) == [])
        Image.new("RGB", (1080, 1350), (90, 90, 90)).save(d / "slide-02.png")
        ok("--check fails once a frame is re-rendered after the file was written", len(check(d)) == 2)

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
    ap.add_argument("--check", action="store_true",
                    help="recompute and compare, writing nothing; the newest shipped deck by default")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.check:
        d = RUNS / a.run if a.run else newest_shipped()
        if d is None or not d.is_dir():
            print(f"measure_shipped: no run directory to check ({d})", file=sys.stderr)
            return 1
        try:
            problems = check(d)
        except ValueError as e:
            problems = [f"{d.name}: {e}"]
        for line in problems:
            print(line)
        if not problems:
            print(f"measure_shipped: {d.name}'s measurements.json matches its shipped frames")
        return 1 if problems else 0
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
