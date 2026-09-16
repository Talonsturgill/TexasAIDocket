#!/usr/bin/env python3
"""Measure each frame's median L* at 432 px and compare it against the band its own dossier
declared.

This exists because of what the 2026-09-16 panel found. The run computed all nine medians, wrote
them to measured_arc.json beside the storyboard, and never compared them to the nine bands the
storyboard had written for itself. Five of nine frames were outside their own declared band, three
of them by more than twenty points, while the storyboard still carried the sentence "every one of
the nine targets above is inside its own screen's measured range". A number on disk that nothing
reads is not a measurement, it is a file.

432 px is the size a reader actually receives in the feed, so it is the size the band is declared
at and the size this measures at. Run it after every render pass.

Exit 0 only if every frame is inside its band.
"""
import json
import pathlib
import subprocess
import sys

from PIL import Image

RUN = pathlib.Path(__file__).resolve().parent
RENDER = RUN / "render"

# Each frame's own declared band, lifted from its dossier in storyboard.md. (lo, hi); None is open.
BANDS = {
    1: (60.0, None),
    2: (55.0, None),
    3: (36.0, 52.0),
    4: (24.0, 36.0),
    5: (44.0, 60.0),
    6: (20.0, 32.0),
    7: (50.0, None),
    8: (34.0, 46.0),
    9: (None, 28.0),
}



def _frame(n: int) -> pathlib.Path:
    """The archived slide if this is running from the archive, the transient render if not.

    The shipped run carries slide-NN.webp at its top level; out/<date>/render/ holds the PNGs and
    is gitignored. A checker that only knows the second path cannot reproduce its own published
    figures from a fresh clone, which is the whole point of committing it.
    """
    for cand in (RUN / f"slide-{n:02d}.webp",
                 RUN / "render" / f"slide-{n:02d}.png",
                 RUN / f"slide-{n:02d}.png"):
        if cand.exists():
            return cand
    raise FileNotFoundError(f"no slide {n:02d} beside {RUN}")

def srgb_to_lstar(c: float) -> float:
    """One channel of sRGB (0..1) to linear, then Y to CIE L*."""
    c = c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return c


def median_lstar(path: pathlib.Path) -> float:
    im = Image.open(path).convert("RGB")
    # the feed size, which is the size the band is declared at
    im = im.resize((432, 540), Image.LANCZOS)
    vals = []
    for r, g, b in im.getdata():
        y = (
            0.2126 * srgb_to_lstar(r / 255.0)
            + 0.7152 * srgb_to_lstar(g / 255.0)
            + 0.0722 * srgb_to_lstar(b / 255.0)
        )
        vals.append(116.0 * (y ** (1.0 / 3.0)) - 16.0 if y > 0.008856 else 903.3 * y)
    vals.sort()
    n = len(vals)
    return round((vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2.0), 1)


def main() -> int:
    measured, problems = [], []
    for n in range(1, 10):
        png = _frame(n)
        m = median_lstar(png)
        measured.append(m)
        lo, hi = BANDS[n]
        bad = (lo is not None and m < lo) or (hi is not None and m > hi)
        band = f"{lo if lo is not None else '-'} to {hi if hi is not None else '-'}"
        print(f"{'FAIL' if bad else 'ok  '}  frame {n}  median L* {m:5.1f}   band {band}")
        if bad:
            problems.append((n, m, lo, hi))

    ordered = sorted(measured)
    deck_median = ordered[4]
    spread = round(max(measured) - min(measured), 1)
    print(f"\ndeck median L* {deck_median}   spread {spread}   (ledger_check caps the median at 60.0)")

    (RUN / "measured_arc.json").write_text(
        json.dumps({"measured": measured, "deck_median": deck_median, "spread": spread}, indent=1) + "\n"
    )

    if deck_median > 60.0:
        print("FAIL  the deck median is over ledger_check's LIGHT_L cap of 60.0")
        problems.append(("deck", deck_median, None, 60.0))

    if problems:
        print(f"\n{len(problems)} frame(s) outside the band their own dossier declared.")
        return 1
    print("\nevery frame is inside its own declared band.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
