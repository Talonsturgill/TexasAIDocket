#!/usr/bin/env python3
"""construction_check.py — how many frames are the same OBJECT, measured on the pixels.

THE DEFECT THIS EXISTS FOR, and it cost deck 13 its ship.

Three judges scored that deck and the craft lens put `artwork_craft` at 5.5, which is what held
it under the bar. The reason was one sentence and all three judges reached some version of it:

    "One primitive, a lighter rectangle holding type seated on granite under a two-part contact
     shadow, carries five of nine frames, and the detail budget is front-loaded exactly opposite
     to the argument, which ends on frames 7 to 9."

`bespoke_check` was already running and reported a median pairwise similarity of 0.377, a WARN.
It did not catch this and it was not going to, because **it compares the drawing CODE and a judge
reads the drawn OBJECT.** Two frames can share no tokens and still present the same thing: a pale
axis-aligned rectangle carrying type on a darker ground. Deck 13's closest code pair was 0.77 and
its five repeated frames were not that pair.

So this measures the outcome. It renders nothing and plans nothing. It looks at the PNGs a reader
receives and asks one question per frame: is the brightest thing on this frame a solid rectangle?

HOW IT MEASURES

    ground      the frame's own median luminance at thumbnail scale, so a light deck and a dark
                deck are asked the same question about themselves
    bright      pixels clearly above that ground, which is what a reader's eye goes to first
    blob        the largest connected bright region
    fill        that region's area divided by its bounding box. A solid rectangle is 1.0. A
                microphone, a sawn arris, a course of masonry are all far below it.

A frame counts as PLATED when its biggest bright region fills at least `FILL` of its own bounding
box and covers at least `AREA` of the frame. Both are needed: fill alone would convict a small
bright chip, and area alone would convict any frame with a large lit passage.

VALIDATED AGAINST THE HUMAN FINDING, which is the only reason to trust it. Run over deck 13 it
returns frames 2, 6, 7, 8 and 9. That is the craft judge's list, arrived at from pixels rather
than from taste, with no frame added and none missed.

    2 0.895   6 1.000   7 0.937   8 0.708   9 0.856      plated
    1 0.083   3 0.065   4 0.455   5 none                 not

THE THRESHOLD IS THE JUDGE'S OWN LINE. Five of nine is what a panel called the deck's real craft
problem, so a majority of the deck sharing one primitive is the fail. Under half is a register,
which is a good thing and what a deck is supposed to have.

WHAT THIS DOES NOT DO. It has no opinion about which primitive a deck picks, only about how much
of the deck one primitive carries. A deck of nine plates and a deck of nine anything-elses fail
alike. It also cannot see a repeated primitive that is DARK on a light ground, which is a real
blind spot and is stated rather than papered over: every deck this project has shipped is dark
ground with light objects, and widening it before there is a light deck to measure would be
fitting a threshold to no data.

    construction_check.py --render-dir out/<date>/render
    construction_check.py --self-test

Exit 0 clean, 1 one primitive carries the deck, 2 could not run.
"""
from __future__ import annotations

import argparse
import sys
from collections import deque
from pathlib import Path

THUMB = (216, 270)     # half the feed thumb. The primitive is a large shape; this is plenty.
ABOVE = 34.0           # luminance above the frame's own median that reads as "the bright thing"
FILL = 0.68            # of its bounding box. A solid rectangle is 1.0.
AREA = 0.02            # of the frame, so a bright chip is not a plate
FAIL_SHARE = 0.5       # a majority of the deck sharing one primitive is the fail


def _luma(img):
    import numpy as np
    a = np.asarray(img.convert("RGB").resize(THUMB)).astype(float)
    return 0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]


def plated(png: Path):
    """(fill, area) of the frame's largest bright region, or None if it has none."""
    import numpy as np
    from PIL import Image
    g = _luma(Image.open(png))
    bright = g > (float(np.median(g)) + ABOVE)
    if bright.sum() < 200:
        return None
    seen = np.zeros_like(bright, bool)
    best: list = []
    h, w = bright.shape
    for sy in range(0, h, 3):
        for sx in range(0, w, 3):
            if not bright[sy, sx] or seen[sy, sx]:
                continue
            q, pix = deque([(sy, sx)]), []
            seen[sy, sx] = True
            while q:
                y, x = q.popleft()
                pix.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and bright[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        q.append((ny, nx))
            if len(pix) > len(best):
                best = pix
    if not best:
        return None
    ys = [p[0] for p in best]
    xs = [p[1] for p in best]
    box = (max(ys) - min(ys) + 1) * (max(xs) - min(xs) + 1)
    return len(best) / box, len(best) / bright.size


def check(render_dir: Path):
    # a shipped run carries webp, a live run carries png, and this reads whichever is there
    pngs = sorted(render_dir.glob("slide-*.png")) or sorted(render_dir.glob("slide-*.webp"))
    if not pngs:
        return 2, [f"no rendered slides in {render_dir}"], []
    rows = []
    for p in pngs:
        m = plated(p)
        rows.append((p.name, m))
    hits = [n for n, m in rows if m and m[0] >= FILL and m[1] >= AREA]
    share = len(hits) / len(rows)
    problems = []
    if share >= FAIL_SHARE:
        problems.append(
            f"{len(hits)} of {len(rows)} frames are one primitive, a solid bright rectangle on a "
            f"darker ground: {', '.join(hits)}. A majority of the deck built from one object is "
            f"the finding that held deck 13 under the bar, and no code-similarity number sees it, "
            f"because two frames can share no tokens and draw the same thing. Spend the detail "
            f"budget where the argument ENDS rather than where it starts")
    return (1 if problems else 0), problems, rows


def self_test() -> int:
    """Both directions, on shapes rather than on a fixture deck."""
    import numpy as np
    from PIL import Image
    import tempfile

    fails = 0

    def ok(label, cond):
        nonlocal fails
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}")
        if not cond:
            fails += 1

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        # nine frames, each a big pale rectangle on a dark ground: one drawing nine times
        for i in range(1, 10):
            a = np.full((270, 216, 3), 30, np.uint8)
            a[60:200, 30:190] = 210
            Image.fromarray(a).save(d / f"slide-{i:02d}.png")
        code, probs, rows = check(d)
        ok("nine plates is one primitive carrying the deck", code == 1 and probs)
        ok("...and it names how many and which", "9 of 9" in probs[0])

        # the same deck with six frames redrawn as a thin diagonal: not a plate
        for i in range(1, 7):
            a = np.full((270, 216, 3), 30, np.uint8)
            for k in range(200):
                a[40 + k, 20 + k // 2] = 230
                a[40 + k, 21 + k // 2] = 230
            Image.fromarray(a).save(d / f"slide-{i:02d}.png")
        code, probs, rows = check(d)
        ok("a deck where the primitive carries a minority passes", code == 0 and not probs)

        # a bright chip is not a plate, however solid it is
        for i in range(1, 10):
            a = np.full((270, 216, 3), 30, np.uint8)
            a[10:16, 10:16] = 240
            Image.fromarray(a).save(d / f"slide-{i:02d}.png")
        code, probs, rows = check(d)
        ok("a small solid chip is not a plate, so area is load bearing", code == 0)

    print("construction_check self-test: " + ("all passed" if not fails else f"{fails} FAILED"))
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--render-dir")
    ap.add_argument("--date")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    rd = Path(a.render_dir) if a.render_dir else Path("out") / (a.date or "") / "render"
    if not rd.is_dir():
        print(f"construction_check: not a directory: {rd}", file=sys.stderr)
        return 2
    code, problems, rows = check(rd)
    for name, m in rows:
        if m is None:
            print(f"  ----  {name}  no bright region against its own ground")
        else:
            mark = "PLATE" if (m[0] >= FILL and m[1] >= AREA) else "  .  "
            print(f"  {mark} {name}  fill {m[0]:.3f}  area {m[1]:.3f}")
    if code == 2:
        print("construction_check: " + problems[0], file=sys.stderr)
        return 2
    if problems:
        print("\nconstruction_check: " + problems[0])
        return 1
    hits = sum(1 for _, m in rows if m and m[0] >= FILL and m[1] >= AREA)
    print(f"\nconstruction_check: {hits} of {len(rows)} frames share the plate primitive, "
          f"under the {FAIL_SHARE:.0%} line. The deck is a register rather than a repeat")
    return 0


if __name__ == "__main__":
    sys.exit(main())
