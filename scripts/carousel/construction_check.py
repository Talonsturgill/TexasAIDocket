#!/usr/bin/env python3
"""construction_check.py — how many frames trigger one bright-region proxy.

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

CALIBRATED AGAINST ONE HUMAN FINDING. Run over deck 13 it returns frames 2, 6, 7, 8 and 9. That
is the craft judge's list, arrived at from pixels rather than from taste, with no frame added and
none missed.

    2 0.895   6 1.000   7 0.937   8 0.708   9 0.856      plated
    1 0.083   3 0.065   4 0.455   5 none                 not

That agreement earns the measurement a place in the report. It does not make the measurement an
object classifier or a ship gate. On 2026-09-18 it counted a lit records-room wall and a car scene
as the same white document plate, because a connected bright blob can fill a rectangle-shaped
bounding box without being a rectangle or the same object. Four actual document facsimiles were
the deck's visual register and sat under half; the two false positives turned that into six of
nine and blocked an otherwise completed run.

THE THRESHOLD IS THE JUDGE'S OWN REPORTING LINE. Five of nine is what that panel called the
deck's craft problem, so a majority is still the point worth surfacing. It is ADVISORY because
the detector measures bright-region fill, not object identity. `bespoke_check` and the scoring
panel remain the gates for a genuinely repeated drawing.

WHAT THIS DOES NOT DO. It has no opinion about object identity. A deck of nine unrelated bright
scenes can trigger the proxy just as nine plates can, while a repeated primitive that is DARK on
a light ground is invisible to it. Those are real blind spots and are stated rather than papered
over: every deck this project has shipped is dark ground with light objects, and widening the
measurement before there is a light deck to test would be fitting a threshold to no data.

    construction_check.py --render-dir out/<date>/render
    construction_check.py --self-test

Exit 0 clean or advisory, 2 could not run. `check()` returns ADVISORY internally so callers can
preserve and label the measurement without turning it into a ship-stopper.
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
REPORT_SHARE = 0.5     # a majority is the panel-derived point worth surfacing for review
ADVISORY = 3           # measured and reported, but not a reliable object-identity verdict


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
    if share >= REPORT_SHARE:
        problems.append(
            f"{len(hits)} of {len(rows)} frames trigger the solid-bright-region proxy: "
            f"{', '.join(hits)}. A majority was the line behind the deck 13 craft finding, but "
            f"this measurement does not establish that the frames depict the same object. "
            f"Review those frames where the argument ends rather than treating the proxy as an "
            f"object classifier")
    return (ADVISORY if problems else 0), problems, rows


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
        ok("nine plates produces the construction advisory", code == ADVISORY and probs)
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
        print("\nconstruction_check advisory: " + problems[0])
        print("The bright-region measurement stays visible, but object identity remains a "
              "panel and bespoke-check judgment.")
        return 0
    hits = sum(1 for _, m in rows if m and m[0] >= FILL and m[1] >= AREA)
    print(f"\nconstruction_check: {hits} of {len(rows)} frames trigger the bright-region proxy, "
          f"under the {REPORT_SHARE:.0%} reporting line. The deck is a register rather than a "
          f"repeat")
    return 0


if __name__ == "__main__":
    sys.exit(main())
