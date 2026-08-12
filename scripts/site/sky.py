#!/usr/bin/env python3
"""sky.py — the atmosphere the site sits under, and the mark in it.

WHY A PAGE NEEDS WEATHER

The sibling product's home page has an aurora over it: drifting veils of green and violet, a
star field, a meteor every few seconds, and the Big Dipper drawn in gold. None of it is
information. All of it is the reason that page reads as designed and a flat dark rectangle reads
as a default. The lesson ports. The aurora does not.

WHAT TEXAS GETS INSTEAD, AND WHY IT IS NOT A COPY

**Big Bend at dusk**, which was already the base register and had never been drawn.

  - A HORIZON GLOW low on the page, ember into gold, because the thing you actually see out
    there is the sun going down behind the Chisos and the bottom of the sky staying lit long
    after the top has gone.
  - HEAT SHIMMER instead of aurora curtains. The aurora is vertical, cold and northern. The
    equivalent Texas phenomenon is horizontal, warm and low: air off hot ground, banding and
    sliding sideways just above the skyline.
  - A DENSE STAR FIELD, which is earned rather than decorative. Big Bend is a certified
    International Dark Sky Park and has among the least light pollution left in the lower 48,
    so a Texas night sky is genuinely one of the darkest and busiest skies in the country. That
    is the fact the star field is drawing.
  - THE LONE STAR as the mark in the sky, where the sibling puts its constellation. One star,
    not a pattern, which is the whole point of the thing: statutory, geometric, and the one
    Texas device that is not costume.

No longhorn, no rope, no sunset silhouette of a windmill. The atmosphere is a real place at a
real hour, and the mark is the state's own geometry.

    sky.py --self-test
    sky.py --svg > /tmp/star.svg
"""
from __future__ import annotations

import argparse
import sys

# The star field. Positions are FIXED rather than random, because the sky is part of the
# stylesheet and the stylesheet has to be byte-identical on every rebuild. Hand-placed in a
# loose scatter with no visible grid, denser toward the top where the eye reads sky.
#
# (x%, y%, radius px, alpha) and nothing else. Two dozen is the number where it stops reading as
# "some dots" and starts reading as a sky, without the stylesheet paying for a hundred gradients.
STARS = [
    (4, 8, 1.0, 0.55), (11, 21, 1.4, 0.70), (17, 5, 1.0, 0.45), (23, 33, 1.1, 0.50),
    (29, 14, 1.6, 0.75), (34, 27, 1.0, 0.40), (41, 7, 1.2, 0.60), (46, 19, 1.0, 0.48),
    (52, 31, 1.5, 0.68), (57, 11, 1.0, 0.42), (63, 24, 1.3, 0.62), (68, 4, 1.0, 0.50),
    (73, 17, 1.1, 0.44), (79, 29, 1.6, 0.72), (84, 9, 1.0, 0.46), (88, 22, 1.2, 0.58),
    (93, 13, 1.0, 0.52), (97, 26, 1.4, 0.64), (8, 37, 1.0, 0.38), (38, 40, 1.1, 0.36),
    (60, 38, 1.0, 0.34), (86, 36, 1.2, 0.40), (20, 44, 1.0, 0.30), (71, 46, 1.1, 0.32),
]

# The five-pointed star, on a 24 unit box. The same path the wordmark uses, because the mark in
# the sky and the mark in the masthead being the same shape is most of what makes a mark.
STAR_PATH = "M12 1.6l2.9 7.5 8 .4-6.2 5.1 2.1 7.8L12 18l-6.8 4.4 2.1-7.8L1.1 9.5l8-.4z"


def star_field_css() -> str:
    """The star field as one `background-image`, which is cheaper than 24 elements."""
    return ",\n".join(
        f"radial-gradient({r}px {r}px at {x}% {y}%,rgba(244,238,225,{a}),transparent 60%)"
        for x, y, r, a in STARS)


def lone_star_svg(idprefix: str = "sky") -> str:
    """The Lone Star, with a halo and four diffraction spikes, for the top right of the sky.

    Drawn rather than set as a glyph because it carries a glow and spikes that no font gives,
    and because scintillation has to ride on ONE subgroup. Animating the halo's blur or shadow
    would repaint a large area every frame for a twinkle nobody asked to pay for.
    """
    return (
        f'<svg class="lonestar" viewBox="0 0 200 200" aria-hidden="true" focusable="false">'
        f'<defs>'
        f'<radialGradient id="{idprefix}-halo">'
        f'<stop offset="0%" stop-color="var(--gold)" stop-opacity=".55"/>'
        f'<stop offset="45%" stop-color="var(--gold)" stop-opacity=".13"/>'
        f'<stop offset="100%" stop-color="var(--gold)" stop-opacity="0"/>'
        f'</radialGradient>'
        f'</defs>'
        # The glow and the spikes twinkle together. The star itself never flickers, because a
        # mark that flickers stops being a mark.
        f'<g class="twinkle">'
        f'<circle cx="100" cy="100" r="86" fill="url(#{idprefix}-halo)"/>'
        f'<path d="M100 14V186M14 100H186" stroke="var(--gold)" stroke-opacity=".22" '
        f'stroke-width="1.2"/>'
        f'<path d="M52 52L148 148M148 52L52 148" stroke="var(--gold)" stroke-opacity=".1" '
        f'stroke-width="1"/>'
        f'</g>'
        f'<g transform="translate(100 100) scale(2.6) translate(-12 -12)">'
        f'<path d="{STAR_PATH}" fill="var(--star)"/>'
        f'</g>'
        f'</svg>')


def sky_markup(idprefix: str = "sky") -> str:
    """The whole atmosphere, as one element the page drops in behind everything.

    `aria-hidden` throughout: none of this is information, and a screen reader announcing a
    decorative sky before the headline would be a real cost for zero gain.
    """
    return (
        f'<div class="sky" aria-hidden="true">'
        f'<div class="stars"></div>'
        f'<div class="shimmer"></div>'
        f'<div class="shimmer s2"></div>'
        f'<div class="veil v1"></div><div class="veil v2"></div><div class="veil v3"></div>'
        f'<div class="horizon"></div>'
        f'{lone_star_svg(idprefix)}'
        f'</div>')


def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    ok("the sky is dense enough to read as one", len(STARS) >= 20, str(len(STARS)))
    ok("every star is inside the frame",
       all(0 <= x <= 100 and 0 <= y <= 100 for x, y, _, _ in STARS))
    ok("...and none is opaque enough to compete with the mark",
       all(a <= 0.8 for _, _, _, a in STARS))
    # A GRID READS AS A GRID. Two stars sharing a coordinate, or evenly spaced columns, is the
    # tell that turns a sky back into a texture swatch.
    ok("no two stars sit at the same point", len({(x, y) for x, y, _, _ in STARS}) == len(STARS))
    gaps = sorted(x for x, _, _, _ in STARS)
    deltas = {round(b - a) for a, b in zip(gaps, gaps[1:])}
    ok("...and they are not evenly spaced", len(deltas) > 3, str(sorted(deltas)))

    css = star_field_css()
    ok("the field compiles to one background-image",
       css.count("radial-gradient") == len(STARS) and "\n" in css)
    ok("...and stays cheap", len(css) < 3_000, f"{len(css)} bytes")

    svg = lone_star_svg()
    ok("the mark is the same star the wordmark uses", STAR_PATH in svg)
    ok("...and it carries a halo and spikes", "halo" in svg and "stroke" in svg)
    ok("...and only the glow twinkles, never the star",
       svg.index('class="twinkle"') < svg.index("scale(2.6)"))
    ok("the sky is hidden from assistive tech", 'aria-hidden="true"' in sky_markup())

    m = sky_markup()
    for part in ("stars", "shimmer", "veil v1", "horizon", "lonestar"):
        ok(f"the sky carries its {part.split()[0]} layer", part in m)

    # THE TRAP THIS FILE EXISTS TO AVOID. Scanned over what RENDERS, never over the prose that
    # explains what is being avoided: the first version read this module's own docstring, which
    # says in as many words that there is no longhorn and no windmill, and failed the build for
    # saying so. A comment draws nothing.
    import re as _re                                                # noqa: PLC0415
    kitsch = _re.findall(r"\b(longhorn|cowhide|rope|lasso|boots?|spur|windmill|cactus|"
                         r"aurora|polaris|dipper)\b", m + svg, _re.IGNORECASE)
    ok("no costume, and no borrowed northern sky", not kitsch, str(sorted(set(kitsch))))

    ok("two builds are byte identical", sky_markup() == m and star_field_css() == css)

    if failures:
        print(f"\nsky self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print(f"\nsky self-test: all passed ({len(STARS)} stars, {len(css):,} bytes of field)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--svg", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    sys.stdout.write(lone_star_svg() if a.svg else sky_markup())
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                        # noqa: BLE001
        print(f"sky: broke: {exc}", file=sys.stderr)
        sys.exit(2)
