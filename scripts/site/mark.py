#!/usr/bin/env python3
"""mark.py — the Lone Star, computed from the statute rather than drawn by eye.

WHY THIS FILE EXISTS

The mark was a path typed into a source file:

    M12 1.6l2.9 7.5 8 .4-6.2 5.1 2.1 7.8L12 18l-6.8 4.4 2.1-7.8L1.1 9.5l8-.4z

Approximately a star. Its points are not equidistant from its center, its inner vertices are not
on a common circle, and it sits in a block that is very nearly square. Every one of those is a
small wrongness, and small wrongnesses in a mark are what "amateur" means: nobody can name the
fault, everybody can see it.

None of it needed to be guessed. THE TEXAS FLAG IS SPECIFIED IN LAW, in Government Code
sec. 3100.001, and the specification is complete:

  - the flag is a rectangle whose width is two thirds its length
  - a blue vertical stripe at the hoist, one third the length of the flag
  - a white regular five pointed star centered in that stripe, ONE POINT UP, sized so that a
    circle passing through its five points has a diameter three quarters the width of the stripe

So the mark is computed from those four sentences. This is the same law the rest of the project
runs on, applied to geometry: a numeral nobody typed can be checked, and this one is checked
against the statute in `self_test`.

THE FACETS ARE THE CAPITOL, NOT A BEVEL EFFECT

A flat fill at 30 pixels reads as clip art. The design doctrine already names the reference that
fixes it: the star inlaid in the floor of the Capitol rotunda, cut from stone in wedges that catch
the light differently on either side of each point. So each point is split along its own axis into
two facets, lit from the upper left. It is the same geometry, cut the way the real one is cut, and
it is why the mark reads as an object rather than a sticker.

    mark.py --self-test
    mark.py --svg > /tmp/mark.svg
"""
from __future__ import annotations

import argparse
import math
import sys

# Texas Government Code sec. 3100.001. Four numbers, and every proportion below comes from them.
FLAG_W_OVER_L = 2 / 3           # the flag's width is two thirds its length
HOIST_OVER_L = 1 / 3            # the blue stripe is one third the flag's length
STAR_CIRCLE_OVER_HOIST = 3 / 4  # the circle through the five points, against the stripe's width
POINTS = 5

# A REGULAR five pointed star, so the inner radius is not a taste. Joining every second vertex of
# a regular pentagon produces the pentagram, and the ratio its inner vertices land at is
# cos(2pi/5)/cos(pi/5), which is 1/phi squared. Anything else is a five pointed shape that is not
# this star, and at small sizes the difference reads as "off" long before anybody can name it.
INNER_OVER_OUTER = math.cos(2 * math.pi / POINTS) / math.cos(math.pi / POINTS)

# The drawing space. 300 units of length keeps every derived value a clean decimal at the
# precision emitted, which is what makes two builds byte identical.
VIEW_L = 300.0
VIEW_W = VIEW_L * FLAG_W_OVER_L
HOIST_W = VIEW_L * HOIST_OVER_L
STAR_R = (HOIST_W * STAR_CIRCLE_OVER_HOIST) / 2
PRECISION = 2


def star_points(cx: float, cy: float, r: float, inner: float | None = None) -> list:
    """The ten vertices of a regular five pointed star, one point up.

    SVG's y axis grows downward, so "up" is -90 degrees. Getting this wrong yields a star resting
    on a point instead of standing on two, which is the single most recognisable way to draw this
    flag incorrectly.
    """
    inner = r * INNER_OVER_OUTER if inner is None else inner
    out = []
    for i in range(POINTS * 2):
        radius = r if i % 2 == 0 else inner
        angle = -math.pi / 2 + i * math.pi / POINTS
        out.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return out


def _pt(p) -> str:
    return f"{round(p[0], PRECISION):g},{round(p[1], PRECISION):g}"


def star_path(cx: float, cy: float, r: float) -> str:
    return "M" + "L".join(_pt(p) for p in star_points(cx, cy, r)) + "Z"


def star_facets(cx: float, cy: float, r: float) -> list:
    """Each point cut into two wedges, the way the rotunda inlay is cut.

    A point runs from one inner vertex, out to the tip, and back to the next inner vertex. The cut
    is the line from the center to the tip, so each wedge is center, inner vertex, tip. Ten wedges,
    alternating which side of the point's own axis they fall on, which is what lets the two sides
    take different light.
    """
    v = star_points(cx, cy, r)
    c = (cx, cy)
    out = []
    for i in range(POINTS):
        tip = v[2 * i]
        before = v[(2 * i - 1) % (POINTS * 2)]
        after = v[(2 * i + 1) % (POINTS * 2)]
        out.append(("lit", [c, before, tip]))
        out.append(("shade", [c, tip, after]))
    return out


def flag_svg(idprefix: str = "mk", *, facets: bool = True) -> str:
    """The whole flag, drawn to the statute, as the wordmark's mark."""
    cx, cy = HOIST_W / 2, VIEW_W / 2
    band = VIEW_W / 2                       # the white and red stripes are of equal width
    wedges = ""
    if facets:
        wedges = "".join(
            f'<path class="f-{kind}" d="M{"L".join(_pt(p) for p in tri)}Z"/>'
            for kind, tri in star_facets(cx, cy, STAR_R))
    return (
        f'<svg class="lonestar-mark" viewBox="0 0 {VIEW_L:g} {VIEW_W:g}" '
        f'role="img" aria-label="The Texas flag" focusable="false">'
        # The fly, white over red, each stripe half the flag's width.
        f'<rect class="m-white" x="{HOIST_W:g}" y="0" '
        f'width="{VIEW_L - HOIST_W:g}" height="{band:g}"/>'
        f'<rect class="m-red" x="{HOIST_W:g}" y="{band:g}" '
        f'width="{VIEW_L - HOIST_W:g}" height="{band:g}"/>'
        f'<rect class="m-blue" x="0" y="0" width="{HOIST_W:g}" height="{VIEW_W:g}"/>'
        f'<path class="m-star" d="{star_path(cx, cy, STAR_R)}"/>'
        f'{wedges}'
        f'</svg>')


def star_svg(idprefix: str = "mk", *, facets: bool = True) -> str:
    """The star alone, on a 24 unit box, for the places a whole flag is too much.

    The footer colophon and the sky both want the shape without the stripes.
    """
    r = 11.0
    wedges = ""
    if facets:
        wedges = "".join(
            f'<path class="f-{kind}" d="M{"L".join(_pt(p) for p in tri)}Z"/>'
            for kind, tri in star_facets(12, 12, r))
    return (f'<svg class="{idprefix}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
            f'<path class="m-star" d="{star_path(12, 12, r)}"/>{wedges}</svg>')


def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    # ---- the statute ---------------------------------------------------------
    ok("the flag's width is two thirds its length",
       abs(VIEW_W / VIEW_L - 2 / 3) < 1e-12, f"{VIEW_W}/{VIEW_L}")
    ok("the blue stripe is one third the flag's length",
       abs(HOIST_W / VIEW_L - 1 / 3) < 1e-12, f"{HOIST_W}/{VIEW_L}")
    ok("a circle through the five points is three quarters the stripe's width",
       abs((STAR_R * 2) / HOIST_W - 3 / 4) < 1e-12, f"{STAR_R * 2}/{HOIST_W}")

    # ---- the star is REGULAR, which the typed path was not --------------------
    cx, cy = HOIST_W / 2, VIEW_W / 2
    v = star_points(cx, cy, STAR_R)
    outer = [math.dist((cx, cy), v[i]) for i in range(0, 10, 2)]
    inner = [math.dist((cx, cy), v[i]) for i in range(1, 10, 2)]
    ok("all five points are the same distance from the center",
       max(outer) - min(outer) < 1e-9, f"{min(outer):.6f} to {max(outer):.6f}")
    ok("...and so are all five inner vertices",
       max(inner) - min(inner) < 1e-9, f"{min(inner):.6f} to {max(inner):.6f}")
    ok("...and the inner radius is the pentagram's, one over phi squared",
       abs(INNER_OVER_OUTER - 1 / ((1 + 5 ** 0.5) / 2) ** 2) < 1e-12,
       f"{INNER_OVER_OUTER:.9f}")
    # ONE POINT UP. A star resting on a point is the most recognisable way to draw this wrong.
    top = min(v, key=lambda p: p[1])
    ok("one point faces up", abs(top[0] - cx) < 1e-9 and abs(top[1] - (cy - STAR_R)) < 1e-9,
       str(top))
    ok("...and it stands on two, not on one",
       sum(1 for p in v[::2] if abs(p[1] - max(q[1] for q in v[::2])) < 1e-9) == 2)

    # ---- the facets ----------------------------------------------------------
    f = star_facets(cx, cy, STAR_R)
    ok("every point is cut into two wedges", len(f) == POINTS * 2, str(len(f)))
    ok("...half lit and half shaded",
       sum(1 for k, _ in f if k == "lit") == POINTS
       and sum(1 for k, _ in f if k == "shade") == POINTS)
    ok("...and each wedge is a triangle from the center",
       all(len(tri) == 3 and tri[0] == (cx, cy) for _, tri in f))

    # ---- what ships ----------------------------------------------------------
    svg = flag_svg()
    ok("the mark carries the flag's three fields",
       all(c in svg for c in ("m-blue", "m-white", "m-red")))
    ok("...and the star over them", "m-star" in svg and svg.index("m-blue") < svg.index("m-star"))
    ok("the mark is announced as what it is", 'aria-label="The Texas flag"' in svg)
    ok("the star alone is available for the places a flag is too much",
       "m-star" in star_svg() and "m-blue" not in star_svg())
    ok("both stay small", len(flag_svg()) < 4_000 and len(star_svg()) < 3_000,
       f"{len(flag_svg())} and {len(star_svg())} bytes")
    ok("two builds are byte identical", flag_svg() == svg and star_svg() == star_svg())
    # The thing this file replaced. If the typed path comes back, it comes back on purpose.
    ok("no hand-typed star path survives", "M12 1.6l2.9 7.5" not in svg + star_svg())

    if failures:
        print(f"\nmark self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print(f"\nmark self-test: all passed (statutory geometry, {POINTS * 2} facets)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--svg", action="store_true")
    ap.add_argument("--star", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    sys.stdout.write(star_svg() if a.star else flag_svg())
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                        # noqa: BLE001
        print(f"mark: broke: {exc}", file=sys.stderr)
        sys.exit(2)
