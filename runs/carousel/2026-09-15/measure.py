#!/usr/bin/env python3
"""measure.py — the deck's value block, MEASURED off the rendered PNGs and never planned.

One grid and one home for the figure. 270 by 338 is `panel_ready.ARC_GRID`, which is what every
prior run's `measurements.json` was written on and what `ledger/carousel/artwork.json` records.
The 2026-09-03 run measured its own arc on a second grid, disagreed with the ledger by 1.1, and
wrote the finding down. Two grids is two homes for one figure.

`shipped_check.py` reads the output and fails the build on any L* figure printed in this run's
prose that `measurements.json` does not hold, whatever wrote it. So every value sentence in the
storyboard, the run record and the artwork ledger comes from here.

WHAT THIS RUN ADDS, and it is a repair rather than an addition. `panel_ready` compares each
dossier's planned frame median against the render and fails past one Munsell step, ten L*. Four
prior runs planned high and rendered dark, by 16, 19, 10 and 18 L* respectively, because on night
paper the PAPER is most of the frame and the paper's own L* is about six. So this script prints
the plan beside the measurement for every frame, in one table, the moment a render exists. A miss
found here costs a re-render of one frame. The same miss found at `panel_ready` costs the round
that was about to be scored.

ITS CLOSING ADVICE SAYS FIX THE ART, NOT THE PLAN, AND THIS RUN DID THE OTHER THING. Carousel
no. 25 rewrote its arc, and the reason is written into the storyboard header rather than left
here as an exception: a white field printed through this deck's stipple comes off the press at a
mean of 63 of 255, so that screen's highest reachable frame median is L* 27 and the plan had
asked a stipple frame for 40. Fixing the art cannot clear a miss the press cannot print. What it
CAN clear, and did on the same day, is a frame that came out dark because nothing was drawn in
it, which is what frame 3 was and why it was rebuilt rather than re-planned. The advice above is
right for every other case and is left exactly as it stands.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

RUN = Path(__file__).resolve().parent
GRID = (270, 338)                      # panel_ready.ARC_GRID, not a second opinion
LIGHT_L = 60.0                         # the light-deck line the artwork ledger keeps a cap on
DEV = 2                                # the frames render at 2x, so one CSS px is two rows
ACCENT = (0x2F, 0x7D, 0x57)            # the checker's green pencil, this deck's one accent
ACCENT_TOL = 26                        # per channel, so the print's contour plate does not hide it


def _lstar(rgb: np.ndarray) -> np.ndarray:
    a = rgb / 255.0
    a = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    Y = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
    return np.where(Y > 0.008856, 116 * np.cbrt(Y) - 16, 903.3 * Y)


def frame_stats(png: Path) -> dict:
    im = Image.open(png).convert("RGB").resize(GRID, Image.LANCZOS)
    a = np.asarray(im, dtype=float)
    L = _lstar(a)
    d = np.abs(a - np.array(ACCENT, dtype=float))
    accent = float((d.max(axis=2) <= ACCENT_TOL).mean() * 100.0)
    return {
        "median_L": round(float(np.median(L)), 1),
        "p05_L": round(float(np.percentile(L, 5)), 1),
        "p95_L": round(float(np.percentile(L, 95)), 1),
        "accent_share_pct": round(accent, 2),
    }


def planned(storyboard: Path) -> dict:
    """Each dossier's declared frame median, read the way panel_ready reads it.

    The qualifier and the number have to be in one sentence, because a reader stops at the
    sentence end and so does the gate. A dossier with no such sentence is reported as None
    rather than guessed at, so an eight-of-nine plan reads as an incomplete plan.
    """
    if not storyboard.exists():
        return {}
    text = storyboard.read_text(encoding="utf-8")
    # The same three patterns panel_ready.py uses, so the plan has one reading and not two.
    block_re = re.compile(r"```ya?ml\s*\nslide:\s*(\d+)\b(.*?)```", re.S)
    vs_re = re.compile(r"^[ \t]*value_structure:(.*?)(?=^[ \t]{0,4}[A-Za-z_][\w]*:)", re.S | re.M)
    fm_re = re.compile(r"\b(?:planned\s+)?frame(?:'s)?\s+median\s+L\*|\bplanned\s+median\s+L\*", re.I)
    num_re = re.compile(r"-?\d+(?:\.\d+)?")
    out: dict[str, float | None] = {}
    for n, blk in block_re.findall(text):
        key = f"slide-{int(n):02d}"
        out[key] = None
        vs = vs_re.search(blk)
        if not vs:
            continue
        seg = vs.group(1)
        m = fm_re.search(seg)
        if not m:
            continue
        # The number in the SAME SENTENCE as the phrase. A reader stops at the sentence end.
        sentence = re.split(r"(?<=[.!?])\s", seg[m.end():])[0]
        num = num_re.search(sentence)
        if num:
            out[key] = float(num.group(0))
    return out


def main() -> int:
    render = RUN / "render"
    pngs = sorted(render.glob("slide-*.png"))
    if not pngs:
        print("measure: no renders yet", file=sys.stderr)
        return 2
    plan = planned(RUN / "storyboard.md")
    frames = {}
    for p in pngs:
        frames[p.stem] = frame_stats(p)

    meds = [f["median_L"] for f in frames.values()]
    accented = [k for k, f in frames.items() if f["accent_share_pct"] >= 0.10]
    out = {
        "grid": list(GRID),
        "frames": frames,
        "deck": {
            "median_of_frame_medians": round(float(np.median(meds)), 1),
            "darkest_frame": min(frames, key=lambda k: frames[k]["median_L"]),
            "lightest_frame": max(frames, key=lambda k: frames[k]["median_L"]),
            "spread_L": round(max(meds) - min(meds), 1),
            "light_frames": [k for k, f in frames.items() if f["median_L"] >= LIGHT_L],
            "accented_frames": accented,
            "accent_frame_count": len(accented),
        },
    }

    print(f"{'frame':<10} {'planned':>8} {'measured':>9} {'miss':>6} {'p05':>6} {'p95':>6} {'accent%':>8}")
    worst = 0.0
    for k in sorted(frames):
        f = frames[k]
        pl = plan.get(k)
        miss = None if pl is None else round(f["median_L"] - pl, 1)
        if miss is not None:
            worst = max(worst, abs(miss))
        print(f"{k:<10} {('-' if pl is None else pl):>8} {f['median_L']:>9} "
              f"{('-' if miss is None else miss):>6} {f['p05_L']:>6} {f['p95_L']:>6} "
              f"{f['accent_share_pct']:>8}")
    # THE PRESS'S OWN CEILING, folded in so the figures this run's prose prints have ONE home.
    # `screen_ceilings.json` is measured by printing a white field through each of this deck's
    # screen configurations and reading the press back. It is what the arc was re-derived from,
    # so it belongs in the file `shipped_check` asks.
    sc = RUN / "screen_ceilings.json"
    if sc.exists():
        out["screen_ceilings"] = json.loads(sc.read_text(encoding="utf-8"))

    out["deck"]["worst_plan_miss_L"] = round(worst, 1)
    out["deck"]["plan_complete"] = len(plan) == len(frames) and all(v is not None for v in plan.values())
    json.dump(out, open(RUN / "measurements.json", "w"), indent=2)

    print(f"\ndeck median of frame medians {out['deck']['median_of_frame_medians']}, "
          f"spread {out['deck']['spread_L']}, accent on {len(accented)} frame(s)")
    if not out["deck"]["plan_complete"]:
        print("PLAN INCOMPLETE: a frame median is declared for some frames and not others, which "
              "panel_ready reports as a plan for part of a deck rather than compares.")
    elif worst > 10.0:
        print(f"WORST PLAN MISS {worst} L*, over one Munsell step. panel_ready will refuse this "
              f"deck. Fix the ART to hit the plan rather than the plan to match the art.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
