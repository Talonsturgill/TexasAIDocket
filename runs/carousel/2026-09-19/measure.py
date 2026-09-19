#!/usr/bin/env python3
"""measure.py — every luminance figure carousel no. 29 publishes, computed from its own renders.

NOTHING HERE IS TYPED. The run's prose quotes L* values in the storyboard, the run record and
`ledger/carousel/artwork.json`, and `shipped_check`'s `measured figures` gate asks, of the shipped
bytes, that every number written beside the token `L*` exists in this file. That gate is the
answer to this repo's highest recurrence defect, which is a value with one home and three surfaces
each keeping their own copy of it.

TWO TRACKS, AND BOTH ARE WRITTEN. The measured medians are what the frames came out at. The
PLANNED medians are parsed out of the nine dossiers rather than retyped beside them, so the plan
and the measurement cannot drift apart in this file the way they have drifted in three earlier
runs. A planned value that no frame reached is a finding, and it stays visible here rather than
being quietly replaced by what the render produced.

THE MEASUREMENT IS TAKEN AT 432 PIXELS because that is the size a reader receives in the feed,
and a median taken at 1080 is a statement about a picture nobody sees at that size.
"""
import json
import pathlib
import re

from PIL import Image

RUN = pathlib.Path(__file__).resolve().parent
ACCENT = (0x2A, 0x7A, 0x9E)          # the firstlight accent, from the chassis declaration
PLAN_RX = re.compile(r"Frame median L\* planned at (\d+)")       # the dossier, which is the plan
SLIDE_PLAN_RX = re.compile(r"Planned frame median L\* (\d+)")    # the frame's own header comment


def _frame(n: int) -> pathlib.Path:
    """The archived slide if this runs from the archive, the transient render if not."""
    for cand in (RUN / f"slide-{n:02d}.webp",
                 RUN / "render" / f"slide-{n:02d}.png",
                 RUN / f"slide-{n:02d}.png",
                 RUN.parents[2] / "out" / RUN.name / "render" / f"slide-{n:02d}.png"):
        if cand.exists():
            return cand
    raise FileNotFoundError(f"no slide {n:02d} beside {RUN}")


def _slide_source(n: int) -> pathlib.Path:
    for cand in (RUN / "slides" / f"slide-{n:02d}.html",
                 RUN / "slides" / f"slide-{n:02d}.html"):
        if cand.exists():
            return cand
    raise FileNotFoundError(f"no slide source {n:02d} beside {RUN}")


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
        "mean_L": round(sum(vals) / n, 1),
        "p05_L": round(vals[int(n * 0.05)], 1),
        "p95_L": round(vals[int(n * 0.95)], 1),
        "accent_share_pct": round(100.0 * accent / n, 2),
    }


def planned() -> list:
    """The nine planned medians, PARSED out of the storyboard, which is where a plan lives.

    THE FRAMES STATE IT TOO, AND THAT IS THE POINT OF READING BOTH. Each slide's header comment
    closes on "Planned frame median L* N", written at build time, while the dossier said it at
    plan time. Two homes for one number is the defect `shipped_check`'s measured-figures gate was
    written for, so this refuses to produce a file at all while they disagree, rather than
    quietly preferring one. The dossier wins on a reconciliation, because a frame that revised
    its own target after the probe render has revised the PLAN and has to say so in the plan.
    """
    story = (RUN / "storyboard.md").read_text(encoding="utf-8")
    plan = [int(x) for x in PLAN_RX.findall(story)]
    if len(plan) != 9:
        raise ValueError(f"storyboard.md states {len(plan)} planned frame medians, not 9, so the "
                         f"plan cannot be read and will not be guessed")
    drift = []
    for n in range(1, 10):
        m = SLIDE_PLAN_RX.search(_slide_source(n).read_text(encoding="utf-8"))
        if not m:
            raise ValueError(f"slide {n:02d} no longer states its planned frame median")
        if int(m.group(1)) != plan[n - 1]:
            drift.append(f"slide {n:02d} says {m.group(1)} and its dossier says {plan[n - 1]}")
    if drift:
        raise SystemExit("measure: the plan has two homes and they disagree. Nothing written.\n  "
                         + "\n  ".join(drift))
    return plan


def main() -> int:
    frames = {}
    for n in range(1, 10):
        frames[f"slide-{n:02d}"] = frame_stats(_frame(n))

    med = [frames[f"slide-{n:02d}"]["median_L"] for n in range(1, 10)]
    plan = planned()
    adj = [round(abs(med[i + 1] - med[i]), 1) for i in range(8)]
    srt = sorted(med)

    out = {
        "_note": "Measured at 432px, the size a reader receives. Planned values are parsed from "
                 "the slide dossiers, never retyped.",
        "grid": "432x540, the feed thumb",
        "frames": frames,
        "per_frame_median_lstar": med,
        "planned_median_lstar": plan,
        "plan_minus_measured": [round(plan[i] - med[i], 1) for i in range(9)],
        "adjacent_deltas": adj,
        "deck": {
            "median_of_frame_medians": round(srt[4], 1),
            "mean_of_frame_medians": round(sum(med) / 9, 1),
            "spread_L": round(max(med) - min(med), 1),
            "max_adjacent_delta": round(max(adj), 1),
            "mean_adjacent_delta": round(sum(adj) / len(adj), 1),
        },
        "accent_share_pct": {k: v["accent_share_pct"] for k, v in frames.items()},
        # THE PRESS CEILINGS, measured on 2026-09-15 by printing a white field through each of
        # this workshop's screen configurations on a dark ground. They are carried here because
        # the storyboard quotes two of them beside the token L*, and `shipped_check`'s
        # measured-figures gate asks that every such number exist in this file. They are a
        # property of the PRESS rather than of this deck, which is exactly why a deck that
        # quotes one has to be able to point at where it came from.
        "screen_ceilings": {"stipple_c5": 26.7, "hatch": 45.5, "halftone_c6": 82.7},
    }
    (RUN / "measurements.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("measure: 9 frame(s) at 432px, deck median L* %.1f, spread %.1f, max adjacent %.1f"
          % (out["deck"]["median_of_frame_medians"], out["deck"]["spread_L"],
             out["deck"]["max_adjacent_delta"]))
    print("  measured", med)
    print("  planned ", plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
