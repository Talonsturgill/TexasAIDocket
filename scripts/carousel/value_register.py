#!/usr/bin/env python3
"""value_register.py — the faded look, measured off the frames, before a critic sees them.

    python3 scripts/carousel/value_register.py --render-dir out/<date>/render --probe --date <date>
    python3 scripts/carousel/value_register.py --render-dir out/<date>/render --date <date>
    python3 scripts/carousel/value_register.py --run runs/carousel/<date>
    python3 scripts/carousel/value_register.py --self-test

WHY THIS EXISTS

The owner, on October 4th, beside the sibling product's deck of the same morning, quoted in full
in knowledge/carousel/ILLUSTRATION_SYSTEM.md, THE STAGE: the sibling's art "wows me ... It's more
like bold. The Texas one, it's okay, but it's just more like faded colors and stuff."

Faded is a measurement, and it is not the one anybody guessed. Measured on every shipped frame of
the ten Texas decks from September 24th to October 4th and the twelve sibling decks from September
24th to October 5th, at 432 by 540 in CIE L* (measure_shipped.lstar), the colour is not the
difference: mean chroma was 11.5 here and 8.4 there. The VALUE is.

    share of the frame       Texas, 10 decks    sibling, 12 decks
    mid tones, L* 30 to 70        0.418              0.131
    near black, L* under 15       0.188              0.610
    deck median L*                 32.6               12.8

A Texas frame lived in the middle of the scale and a sibling frame lived at its ends: a dark field,
one lit thing, one bright edge. The cause was in the doctrine and the engine, not in any one run.
From September 24th the routine ordered "a photograph of a place at a time of day ... haze in the
distance", the daylight worlds fogged every ground toward a bright horizon haze, and chassis were
allowed a pale wash up to 0.55 over the art. Carousel no. 42 lifted the top of every frame by 0.35
and the bottom by 0.45 and shipped 0.698 of its pixels in the mid tones.

It also cost the run 44 minutes. That deck measured a median of L* 68.0, over the light deck line,
in a window that had already spent its one light deck on no. 38, and `ledger_check` only found out
at ship, after three panel rounds, so all nine frames were exposed down and judged again. This
gate asks both questions on the PROBE frame, in the first minute of the art build.

WHAT IT CHECKS

1. A probe frame: its mid tone share is at most PROBE_MID. Over the 107 sibling frames 2 exceed it
   (1.9 percent), both on the one deck of the twelve that was mostly snow plain. Over the 90 Texas
   frames 30 do.
2. A deck: the mean mid tone share of its frames is at most DECK_MID. All 12 sibling decks are
   under it (the highest 0.324) and 8 of the 10 Texas decks are over it (the lowest of those 0.406).
   The two that pass are the two darkest worlds Texas shipped, nightSodium on September 27th
   (0.143) and blueHour on September 26th (0.220).
3. The light deck cap, looked ahead. A frame or deck whose median reaches ledger_check's LIGHT_L,
   in a window of the seven previous decks that already holds LIGHT_CAP light decks, fails now
   rather than at ship.

What it does NOT check is taste. A deck can pass this and still be weak. It removes one measured
cause of weak, the one the owner named, and the critics and the panel judge the rest.

THE CURE is never a darker grade over the same frame, which only crushes a mid tone into a muddier
one. It is the world and the light: a staged world (`lastLight` or `floodlit` in txthree.js,
TXT.stage), a subject that fills the frame, the type on the dark field, and no pale wash over the
art. ILLUSTRATION_SYSTEM.md, THE BOLD TEST, is the doctrine.

The shipped-check adapter measures and reports decks dated on or before VALUE_SINCE without
failing them, because they were drawn under the earlier doctrine. Direct invocations still
return the measured result, including the historical calibration fixtures.

EXIT CODES: 0 within the register, 1 outside it or nothing to measure.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import measure_shipped as ms  # noqa: E402

REPO_ROOT = HERE.parents[1]
ARTWORK = REPO_ROOT / "ledger" / "carousel" / "artwork.json"

MID_LO, MID_HI = 30.0, 70.0   # the mid tones, in L*
DARK = 15.0                   # near black, in L*
PROBE_MID = 0.50              # the most of one probe frame that may sit in the mid tones
DECK_MID = 0.35               # the most of a deck, on the mean of its frames
VALUE_SINCE = "2026-10-07"    # last shipped deck before the staged-world upgrade reached main


def frame_stats(path: Path) -> dict:
    rgb = np.asarray(Image.open(path).convert("RGB").resize(ms.AT, Image.BOX), float)
    lum = ms.lstar(rgb)
    return {"frame": path.name,
            "median_L": round(float(np.median(lum)), 1),
            "mid": round(float(((lum >= MID_LO) & (lum <= MID_HI)).mean()), 3),
            "dark": round(float((lum < DARK).mean()), 3)}


def render_frames(render_dir: Path) -> list[Path]:
    return sorted(p for p in render_dir.glob("slide-*.png") if p.stem[6:].isdigit())


def light_window(art_path: Path = ARTWORK, before: str | None = None) -> tuple[int | None, list[str]]:
    """How many of the seven decks before this one already read light, by ledger_check's own rule,
    less the named waivers. Before `before` (a run date) when given, so a re-run of a shipped deck
    does not count itself. None, with the reason, when the ledger can't be read: an unknown window
    is never an empty one (Codex, PR 402)."""
    import ledger_check as lc
    try:
        art = json.loads(art_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, [f"{art_path}: {e}"]
    entries = sorted(art.get("entries", []), key=lambda e: e.get("date", ""))
    if before:
        entries = [e for e in entries if e.get("date", "") < before]
    light = [e["date"] for e in entries[-7:]
             if isinstance(e.get("value"), dict)
             and isinstance(e["value"].get("deck_median_L"), (int, float))
             and e["value"]["deck_median_L"] >= lc.LIGHT_L
             and e["date"] not in lc.LIGHT_CAP_WAIVED]
    return len(light), light


def judge(rows: list[dict], probe: bool, date: str | None, art_path: Path = ARTWORK) -> list[str]:
    import ledger_check as lc
    problems = []
    if not rows:
        return ["no frames to measure"]
    if probe:
        for r in rows:
            if r["mid"] > PROBE_MID:
                problems.append(
                    f"{r['frame']}: {r['mid']:.3f} of the frame sits in the mid tones (L* 30 to 70), over "
                    f"the probe's {PROBE_MID}. This is the faded look the owner rejected on 2026-10-04. "
                    f"Stage the deck in a dark world (lastLight or floodlit), let the subject fill the "
                    f"frame, and take any pale wash off the art. A darker grade over the same frame is "
                    f"not the cure")
    mean_mid = float(np.mean([r["mid"] for r in rows]))
    if not probe and mean_mid > DECK_MID:
        worst = sorted(rows, key=lambda r: -r["mid"])[:3]
        problems.append(
            f"the deck's frames hold {mean_mid:.3f} of their pixels in the mid tones on the mean, over "
            f"{DECK_MID}. The sibling's twelve decks hold 0.131. Worst: "
            + ", ".join(f"{r['frame']} {r['mid']:.2f}" for r in worst)
            + ". Re-light those frames in the deck's staged world rather than grading them down")
    # A PROBE FRAME IS JUDGED ALONE, its lightness as well as its mid tones (Codex, PR 402): the
    # median over a render folder that still holds a retried run's dark frames hid a light probe.
    if probe:
        light = [r for r in rows if r["median_L"] >= lc.LIGHT_L]
        median = max((r["median_L"] for r in light), default=0.0)
        subject = "probe frame " + ", ".join(r["frame"] for r in light)
    else:
        median = float(np.median([r["median_L"] for r in rows]))
        light = median >= lc.LIGHT_L
        subject = "deck"
    if light:
        n, which = light_window(art_path, date)
        if n is None:
            problems.append(
                f"the {subject} reads light, median L* {median:.1f} against ledger_check's line of "
                f"{lc.LIGHT_L}, and the light deck window can't be read ({which[0]}), so this gate "
                f"can't tell whether brand.yaml's cap of {lc.LIGHT_CAP} in eight is spent. Fix the "
                f"ledger or choose a dark world")
        elif n >= lc.LIGHT_CAP:
            problems.append(
                f"the {subject} reads light, median L* {median:.1f} against "
                f"ledger_check's line of {lc.LIGHT_L}, and the seven decks before it already hold "
                f"{n} light deck(s) ({', '.join(which)}) against brand.yaml's cap of {lc.LIGHT_CAP} in "
                f"eight. Ledger_check fails this at ship, which cost no. 42 forty four minutes. "
                f"Choose a dark world now")
    return problems


def report(rows, problems, probe, as_json):
    mean_mid = float(np.mean([r["mid"] for r in rows])) if rows else 0.0
    if as_json:
        print(json.dumps({"frames": rows, "mean_mid": round(mean_mid, 3), "problems": problems}, indent=1))
        return
    for r in rows:
        print(f"  {r['frame']:16} median L* {r['median_L']:5.1f}  mid {r['mid']:.3f}  near black {r['dark']:.3f}")
    print(f"  {'probe' if probe else 'deck'} mean mid tone share {mean_mid:.3f}")
    for p in problems:
        print(f"  FAIL  {p}")
    if not problems:
        print("  ok    within the register")


def self_test() -> int:
    failures = 0

    def check(label, cond):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}")
        failures += 0 if cond else 1

    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        # a faded frame: a soft gradient from L* about 45 to 65, the whole frame in the mid tones
        g = np.linspace(105, 165, 540)[:, None, None] * np.ones((540, 432, 3))
        Image.fromarray(g.astype(np.uint8)).save(t / "slide-01.png")
        # a bold frame: a near black field, a lit subject, one bright edge
        b = np.full((540, 432, 3), 10, np.uint8)
        b[300:470, 90:340] = 205
        b[300:306, 90:340] = 250
        Image.fromarray(b).save(t / "slide-02.png")
        faded, bold = frame_stats(t / "slide-01.png"), frame_stats(t / "slide-02.png")
        empty = t / "empty.json"
        empty.write_text(json.dumps({"entries": []}))
        check(f"a soft mid grey gradient is faded: {faded['mid']:.3f} in the mid tones",
              faded["mid"] > 0.9 and bool(judge([faded], True, None, empty)))
        check(f"a lit subject on a near black field is not: {bold['mid']:.3f} in the mid tones, "
              f"{bold['dark']:.3f} near black", bold["mid"] < 0.05 and not judge([bold], True, None, empty))
        check("a deck of both is held to its mean", judge([faded, bold], False, None, empty) != [])
        check("a deck of bold frames passes", judge([bold, bold], False, None, empty) == [])
        # the light deck cap, looked ahead: a white frame after a window already holding one
        w = np.full((540, 432, 3), 238, np.uint8)
        w[200:400, 150:300] = 20
        Image.fromarray(w).save(t / "slide-03.png")
        white = frame_stats(t / "slide-03.png")
        held = t / "held.json"
        held.write_text(json.dumps({"entries": [{"date": "2026-09-01", "value": {"deck_median_L": 81.0}}]}))
        check(f"a high key frame (median L* {white['median_L']}) after a spent light deck fails at the probe",
              any("reads light" in p for p in judge([white], True, "2026-09-05", held)))
        check("...and passes in a window with none spent",
              not any("reads light" in p for p in judge([white], True, "2026-09-05", empty)))
        check("a light probe frame beside two dark ones a retried run left in the folder still fails",
              any("reads light" in p for p in judge([bold, white, bold], True, "2026-09-05", held)))
        missing = t / "no-such-ledger.json"
        check("an unreadable light deck ledger fails a light probe closed",
              any("can't be read" in p for p in judge([white], True, "2026-09-05", missing)))
        check("...and never troubles a dark one, which doesn't ask it",
              judge([bold], True, "2026-09-05", missing) == [])
    # the calibration anchors, from the shipped decks this was measured on
    for date, should_fail in (("2026-10-04", True), ("2026-09-27", False)):
        d = ms.RUNS / date
        if (d / "copy.json").exists():
            rows = [frame_stats(p) for p in ms.frames(d)]
            got = bool([p for p in judge(rows, False, None, empty_ledger()) if "mid tones" in p])
            check(f"shipped deck {date} {'fails' if should_fail else 'passes'} on its mid tones "
                  f"({np.mean([r['mid'] for r in rows]):.3f})", got == should_fail)
    print(f"value_register self-test: {'all passed' if not failures else str(failures) + ' FAILED'}")
    return 1 if failures else 0


def empty_ledger() -> Path:
    p = Path(tempfile.mkdtemp()) / "empty.json"
    p.write_text(json.dumps({"entries": []}))
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--render-dir", type=Path)
    ap.add_argument("--run", type=Path, help="a shipped run directory, read as the site serves it")
    ap.add_argument("--probe", action="store_true", help="judge each frame alone, as the probe frame")
    ap.add_argument("--date", help="the run's date, so the light window excludes the run itself")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.run:
        paths = ms.frames(a.run)
        date = a.date or a.run.name
    elif a.render_dir:
        paths = render_frames(a.render_dir)
        date = a.date
    else:
        ap.error("give --render-dir or --run")
    rows = [frame_stats(p) for p in paths]
    problems = judge(rows, a.probe, date)
    report(rows, problems, a.probe, a.json)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
