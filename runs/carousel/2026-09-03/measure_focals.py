#!/usr/bin/env python3
"""Measure each frame's value extreme off the rendered PNG, and check the declared focal against it.

WHY THIS EXISTS, AND WHY ITS FIRST VERSION WAS THE FAULT IT WAS WRITTEN TO END.

The storyboard's VALUE ARC claimed to be "measured off the rendered PNGs and never asserted from
this line" and was a guess, wrong on one frame by a factor of four. Round 3 replaced it. Round 4's
craft judge then found four MORE of the same kind in the same file, the focal shares, untouched,
and its one sentence fix was to generate every measurable field rather than type it.

**So round 4 wrote a script, and round 5's craft judge read the script.** It opened the PNG,
computed a scale factor from its width, NEVER USED IT AGAIN, and returned `(w * h) / FRAME` over
nine hardcoded rectangles. Arithmetic on typed constants, under a docstring asserting pixel
measurement. That is the same defect one level up: not a number claiming to be measured, but a
MEASUREMENT PROGRAM claiming to be one.

WHAT THIS DOES INSTEAD, AND WHAT IT STILL CANNOT DO

Every dossier here declares its focal as a value extreme, in words like "carrying the frame's
light extreme" or "the frame's dark extreme". That is a claim about PIXELS and it is checkable
without knowing which object the designer meant.

    the extreme      the frame's own 2nd or 98th percentile L*, computed from the render
    the extreme area the share of the frame within EXTREME_BAND of it, computed from the render
    the declared     the share of the rectangle the dossier names, which is still authored

The first two are read out of the file. The third is a declaration, and this script now says so
in as many words rather than dressing it as a measurement. Where the two disagree badly the
script prints WIDE, because a dossier calling a 3 percent object the frame's light extreme when
28 percent of the frame sits at that value has described something other than what it drew.

**What this still cannot do is decide which object the designer meant.** Round 5's integrity
judge found the declared rectangles are BOUNDING BOXES rather than the objects inside them, so
slide 6's two slots measure 5.7 percent as a bounding box and about 1.3 as drawn. That is a real
finding and it is not closed here. The right fix is the one both judges named: have each frame
emit its focal geometry from `getBBox()` of the elements it actually drew, and generate the
dossier from that. This script is the honest half that can be built from outside the frames.
"""
import json
import pathlib
import statistics
import sys

from PIL import Image

RUN = pathlib.Path(__file__).resolve().parent
REPO = RUN.parents[2]      # runs/carousel/<run>/ -> the repository root
EXTREME_BAND = 8.0      # L* within this of the frame's percentile counts as at the extreme
WIDE = 12.0             # declared and measured differing by more than this is worth printing

# What each dossier DECLARES, as the rectangle it names and the extreme it claims. The rectangle
# is authored, which this file now states rather than implies.
DECLARED = {
    1: ("the agreement region where the two sheets cross", (150, 200, 890, 730), "dark"),
    2: ("the inked run, from the origin to the measured figure", (120, 694, 556, 192), "dark"),
    3: ("the lattice of 95 apertures", (150, 470, 780, 430), "light"),
    4: ("the flush portion of the sheet carrying the quotation", (86, 186, 908, 700), "light"),
    5: ("the punched opening", (92, 424, 896, 592), "light"),
    6: ("the two verb slots taken as one pair", (84, 324, 220, 380), "light"),
    7: ("the lit status plate", (100, 560, 880, 300), "light"),
    8: ("the two courses of leaves", (96, 330, 888, 350), "light"),
    9: ("the open registration area", (446, 484, 154, 304), "light"),
}
FRAME = 1080 * 1350


def _lin(c: float) -> float:
    """One sRGB channel, 0 to 255, to linear light."""
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lstar(r: float, g: float, b: float) -> float:
    """CIE L* from an sRGB triple.

    EACH CHANNEL IS LINEARISED BEFORE THEY ARE COMBINED, and the first version of this did it the
    other way round: it took the luma of the three sRGB values and then applied the transfer
    function once to that. A review bot on PR 252 caught it and gave the falsifying case, pure
    blue, which the wrong order puts at L* 5.6 against a true 32.3.

    On this deck's own palette the error runs 0.0 to 1.7 because none of its colours is a
    saturated primary, so no figure moves far. It was still an arithmetic error inside a file
    whose whole job is that a number here is computed rather than guessed, which is the one thing
    this project promises about its numerals.
    """
    Y = 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)
    return 116 * (Y ** (1 / 3)) - 16 if Y > 0.008856 else 903.3 * Y


def candidates(n: int):
    """Every place frame `n` might be, best source first."""
    return [RUN / ("render/slide-%02d.png" % n),
            REPO / "out" / RUN.name / "render" / ("slide-%02d.png" % n),
            RUN / ("slide-%02d.png" % n),
            RUN / ("slide-%02d.webp" % n)]


def source_for(n: int) -> pathlib.Path:
    """The image for frame `n`, from the working render if it is here and the shipped frame if not.

    IT HAS TO RUN FROM A FRESH CHECKOUT (2026-09-03, PR 252). `render/` is scratch under `out/`
    and is never committed, so a reader holding only the repository could not reproduce a single
    figure in `focals.json`. See the longer note in `measure.py`, which had the identical defect
    and was written the same afternoon, which is the useful half of the finding: eight of the nine
    shipped frames are WebP, so a reproduction off them agrees to about three tenths of a point
    rather than exactly, and `read_from` on every row records which file produced that row.
    """
    for p in candidates(n):
        if p.exists():
            return p
    print("no image for slide %d, looked in %s"
          % (n, ", ".join(str(c) for c in candidates(n))), file=sys.stderr)
    raise SystemExit(1)


def label(p: pathlib.Path) -> str:
    """How a source file is named in the output, wherever it sits."""
    for base in (RUN, REPO):
        try:
            return p.relative_to(base).as_posix()
        except ValueError:
            continue
    return str(p)


def main() -> int:
    rows = []
    read_from = []
    for n, (what, (x, y, w, h), end) in sorted(DECLARED.items()):
        src = source_for(n)
        read_from.append(label(src))
        im = Image.open(src).convert("RGB").resize((270, 338))
        ls = [lstar(r, g, b) for r, g, b in im.getdata()]
        ls.sort()
        # THE FRAME'S OWN EXTREME, read out of the file rather than assumed from the palette.
        idx = int(len(ls) * (0.98 if end == "light" else 0.02))
        peak = ls[min(idx, len(ls) - 1)]
        at_extreme = sum(1 for v in ls if abs(v - peak) <= EXTREME_BAND)
        measured = at_extreme / len(ls) * 100.0
        declared = (w * h) / FRAME * 100.0
        rows.append({
            "slide": n, "what": what, "extreme": end,
            "read_from": read_from[-1],
            "declared_rect": [x, y, w, h],
            "declared_share_pct": round(declared, 1),
            "measured_extreme_L": round(peak, 1),
            "measured_extreme_area_pct": round(measured, 1),
            "median_L": round(statistics.median(ls), 1),
            "wide": abs(declared - measured) > WIDE,
        })
    (RUN / "focals.json").write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
    print("slide  declared  measured   L*    at the frame's %s extreme" % "own")
    for r in rows:
        print("  %d    %6.1f%%  %6.1f%%  %5.1f  %s%s"
              % (r["slide"], r["declared_share_pct"], r["measured_extreme_area_pct"],
                 r["measured_extreme_L"], r["what"], "   WIDE" if r["wide"] else ""))
    print("\ndeclared is AUTHORED, from the rectangle the dossier names.")
    print("measured is READ OUT OF THE PNG, the share of the frame within %.0f L* of its own"
          % EXTREME_BAND)
    print("  %s percentile. WIDE marks a frame where the two disagree by more than %.0f points."
          % ("98th or 2nd", WIDE))
    print("written to %s" % (RUN / "focals.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
