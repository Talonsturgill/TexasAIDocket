#!/usr/bin/env python3
"""favicon.py — the mark in the browser tab, computed from the same statute as the wordmark.

WHY THIS EXISTS

The site shipped no icon of any kind, so every tab showed the browser's generic globe, and a
reader with the docket open beside a dozen other tabs had nothing to find it by. A tab icon is
the smallest piece of identity a site has and the one a returning reader uses most.

WHAT IT DRAWS, AND WHY IT IS A CROP RATHER THAN THE WHOLE FLAG

The wordmark is `mark.flag_svg()`, the whole Texas flag, which is a 3:2 rectangle. A tab icon is
a SQUARE, and letterboxing a 3:2 flag into one leaves the mark a third smaller with dead bands
above and below, at a size where every pixel is already scarce.

So this is the HOIST: the blue field and the white star. That is the part of the flag that is
square croppable and instantly Texas, and the crop is principled rather than eyeballed. The
statute makes the hoist one third of the flag's length and the flag's width two thirds of it, so
the hoist is 1:2, and the star's circumscribed circle is three quarters of the hoist's width.
Cropping that 1:2 hoist to a square ABOUT THE STAR yields a square the width of the hoist with
the star at three quarters of it, which is 12.5 percent clear on every side. That is a good icon
proportion and nobody chose it: it falls out of Government Code sec. 3100.001, the same as every
other number in `mark.py`.

NO FACETS HERE, deliberately, and this is the one place the mark is drawn flat. `mark.py` cuts
each point into a lit and a shaded wedge because a flat fill at 30 pixels reads as clip art. At
SIXTEEN pixels the facets are sub-pixel: they do not read as stone, they read as a smudge across
the star's middle, and they cost the one thing a favicon has, which is a crisp silhouette. An
identity that is a different drawing at each size is not an identity, so the flat star is used at
every size rather than only at the small ones.

WHY THIS IS WRITTEN BY HAND AND NOT BY PILLOW

Exactly `grain.py`'s argument, and it applies harder here. That file records the sibling's
failure: Pillow was a soft dependency, a build on a box without it shipped every page with the
grain silently stripped, and nothing threw. A favicon that goes missing that way puts the generic
globe back with a green build, which is the defect this file exists to end. A PNG is a signature,
three chunks and a CRC. An ICO is a fourteen byte header and a directory. Both are cheap enough
from `zlib` and `struct` that a dependency is not worth the risk, and the standard library keeps
the output byte-stable, which `site_fresh_check` requires of every file in `docs/`.

WHAT SHIPS, and why each one is needed

  favicon.svg          modern browsers prefer it and it is sharp at every zoom and density
  favicon.ico          16 and 32, for the browsers and bookmark stores that still ask, and for
                       the automatic /favicon.ico request a browser makes with no link at all
  apple-touch-icon.png 180 square, for an iOS home screen

NOT ROUNDED, on purpose. iOS applies its own mask to a touch icon, so an icon that arrives with
its corners already cut gets them cut twice and reads as a shrunken sticker inside its own tile.

    favicon.py --self-test
    favicon.py --write /tmp/icons
"""
from __future__ import annotations

import argparse
import math
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import mark                                                            # noqa: E402

# THE CROP, all of it derived. The square is the hoist's width, and the star keeps the size the
# statute gives it, so the icon is the flag's own geometry rather than a redrawing of it.
BOX = mark.HOIST_W                       # 100 units: the hoist's width, and the icon's edge
STAR_R = mark.STAR_R                     # 37.5 units: three quarters of the hoist, halved
CENTER = BOX / 2

# Government Code sec. 3100.001 names Pantone 281 and the flag white. These are `brand.yaml`'s
# stated derivations of them, repeated here as the ONE place a raster needs literal channels.
BLUE = (0x00, 0x20, 0x5B)
WHITE = (0xFF, 0xFF, 0xFF)

# Supersampling for the raster edge. The star is nothing but diagonals, and a hard threshold at
# 16 pixels turns them into stair steps that no amount of good geometry survives. Four is
# sixteen samples a pixel, which is past the point more of them are visible.
SS = 4

ICO_SIZES = (16, 32, 48)
APPLE_SIZE = 180


def star_polygon(box: float = BOX, r: float = STAR_R) -> list:
    """The ten vertices, from mark.py, so the icon can never drift from the wordmark."""
    return mark.star_points(box / 2, box / 2, r)


# ---------------------------------------------------------------- the vector
def svg(box: float = BOX) -> str:
    """The SVG favicon. Self contained, no CSS, since nothing styles a file a browser fetches
    for a tab: the fills have to be IN it, which is why this cannot reuse the wordmark's markup."""
    d = mark.star_path(box / 2, box / 2, STAR_R)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {box:g} {box:g}" '
            f'width="{box:g}" height="{box:g}">'
            f'<title>Texas AI Docket</title>'
            f'<rect width="{box:g}" height="{box:g}" fill="#{BLUE[0]:02X}{BLUE[1]:02X}{BLUE[2]:02X}"/>'
            f'<path d="{d}" fill="#{WHITE[0]:02X}{WHITE[1]:02X}{WHITE[2]:02X}"/>'
            f'</svg>')


# ---------------------------------------------------------------- the raster
def coverage(size: int, poly: list, box: float = BOX, ss: int = SS) -> list:
    """Per pixel coverage of the polygon, 0 to ss*ss, by supersampled scanline fill.

    Scanline rather than a point in polygon test per sample: the intersections of one horizontal
    line with ten edges is ten pieces of arithmetic, and testing every sample against every edge
    is that same work multiplied by the width of the image.

    EVEN-ODD, which is what a five pointed star needs. The pentagram's arms overlap at the
    centre under a nonzero rule and under even-odd they do not, and this polygon is the outline
    rather than the pentagram, so the two agree here. Even-odd is named anyway, because the day
    somebody passes the pentagram in, the rule that was assumed becomes the bug.
    """
    scale = size / box
    pts = [(x * scale, y * scale) for x, y in poly]
    n = len(pts)
    w = size * ss
    counts = [0] * (size * size)
    for sy in range(w):
        y = (sy + 0.5) / ss
        xs = []
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            if (y1 <= y < y2) or (y2 <= y < y1):
                xs.append(x1 + (y - y1) / (y2 - y1) * (x2 - x1))
        if not xs:
            continue
        xs.sort()
        row = (sy // ss) * size
        for k in range(0, len(xs) - 1, 2):
            xa, xb = xs[k], xs[k + 1]
            sa = max(0, int(math.floor(xa * ss)))
            sb = min(w, int(math.ceil(xb * ss)))
            for sx in range(sa, sb):
                if xa <= (sx + 0.5) / ss < xb:
                    counts[row + sx // ss] += 1
    return counts


def pixels(size: int) -> bytes:
    """The icon as raw RGB, the star composited over the blue field at its own coverage."""
    cov = coverage(size, star_polygon())
    full = SS * SS
    out = bytearray(size * size * 3)
    for i, c in enumerate(cov):
        # Straight linear blend in sRGB. Correct compositing would work in linear light, and at
        # this scale between one dark and one light value the difference is under a level on an
        # edge pixel, which is invisible and not worth a gamma table nobody can check.
        for ch in range(3):
            out[i * 3 + ch] = BLUE[ch] + (WHITE[ch] - BLUE[ch]) * c // full
    return bytes(out)


def _chunk(kind: bytes, data: bytes) -> bytes:
    return (struct.pack(">I", len(data)) + kind + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))


def png(size: int) -> bytes:
    """A truecolour PNG of the icon. Colour type 2, 8 bits, no alpha: the field is opaque, and
    an alpha channel would only be a fourth plane of 255s for a browser to decode."""
    rgb = pixels(size)
    stride = size * 3
    raw = b"".join(b"\x00" + rgb[y * stride:(y + 1) * stride] for y in range(size))
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
            + _chunk(b"IDAT", zlib.compress(raw, 9))
            + _chunk(b"IEND", b""))


def ico(sizes=ICO_SIZES) -> bytes:
    """An ICO carrying PNG images, one per size.

    PNG inside ICO rather than the older BMP form. Every browser since Vista reads it, the BMP
    form needs a doubled height and an upside down bitmap plus an AND mask nothing uses, and
    getting any of that subtly wrong yields an icon that renders inverted on one browser only.
    """
    images = [png(s) for s in sizes]
    head = struct.pack("<HHH", 0, 1, len(images))
    offset = len(head) + 16 * len(images)
    entries, blob = b"", b""
    for s, data in zip(sizes, images):
        # 0 in the size byte means 256. Not reachable from ICO_SIZES, encoded correctly anyway.
        entries += struct.pack("<BBBBHHII", s % 256, s % 256, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
        blob += data
    return head + entries + blob


def files() -> dict:
    """Everything this module contributes to the built site, path to bytes."""
    return {
        "favicon.svg": svg().encode("utf-8"),
        "favicon.ico": ico(),
        "apple-touch-icon.png": png(APPLE_SIZE),
    }


def head_html(prefix: str) -> str:
    """The head links, at the relative depth of the page asking.

    THE ICO IS DECLARED FIRST AND THE SVG SECOND. A browser takes the last icon it understands,
    so this order gives an SVG capable browser the vector and leaves everything else on the ICO.
    Reversed, Chrome takes the ICO and the vector is never used.
    """
    b = f"#{BLUE[0]:02X}{BLUE[1]:02X}{BLUE[2]:02X}"
    return (f'<link rel="icon" href="{prefix}favicon.ico" sizes="32x32">\n'
            f'<link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">\n'
            f'<link rel="apple-touch-icon" href="{prefix}apple-touch-icon.png">\n'
            f'<meta name="theme-color" content="{b}">')


# ---------------------------------------------------------------- self-test
def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    # THE CROP IS THE STATUTE'S, not a taste. If mark.py is ever re-derived these move with it.
    ok("the icon's edge is the hoist's width", BOX == mark.HOIST_W, f"{BOX} vs {mark.HOIST_W}")
    ok("the star keeps the size the statute gives it", STAR_R == mark.STAR_R)
    ok("...which leaves it three quarters of the box",
       abs((STAR_R * 2) / BOX - 0.75) < 1e-12, f"{(STAR_R * 2) / BOX}")
    ok("the star is centred in the square",
       all(abs(sum(c[i] for c in star_polygon()) / 10 - CENTER) < 1e-9 for i in (0, 1)))

    # ---- the vector
    s = svg()
    ok("the svg carries its own namespace", 'xmlns="http://www.w3.org/2000/svg"' in s)
    ok("...and its own fills, since nothing styles a favicon",
       "#00205B" in s and "#FFFFFF" in s)
    ok("...and no CSS class the page would have had to supply", "class=" not in s)
    ok("the svg is small enough to be cheap", len(s) < 1_000, str(len(s)))

    # ---- the raster geometry, checked by sampling the pixels rather than trusting the fill
    px = pixels(32)

    def at(x, y):
        i = (y * 32 + x) * 3
        return tuple(px[i:i + 3])

    ok("the centre of the star is white", at(16, 16) == WHITE, str(at(16, 16)))
    ok("the corners are blue", all(at(x, y) == BLUE for x, y in
                                  ((0, 0), (31, 0), (0, 31), (31, 31))),
       str([at(0, 0), at(31, 0), at(0, 31), at(31, 31)]))
    # ONE POINT UP is the flag's most recognisable failure mode, so it is checked on the raster
    # and not only on the geometry: the top row of the star's column is lighter than the bottom,
    # because a point occupies the top centre and a notch occupies the bottom centre.
    top_col = sum(sum(at(16, y)) for y in range(4, 8))
    bot_col = sum(sum(at(16, y)) for y in range(24, 28))
    ok("one point faces up, measured on the pixels", top_col > bot_col, f"{top_col} vs {bot_col}")

    # THE EDGE IS ANTIALIASED. Without this the diagonals stair step, and the check is that some
    # pixel is neither of the two source colours.
    mids = [1 for i in range(0, len(px), 3)
            if tuple(px[i:i + 3]) not in (BLUE, WHITE)]
    ok("the diagonals are antialiased rather than stepped", len(mids) > 20, str(len(mids)))

    # ---- the containers
    p = png(16)
    ok("the png has the signature", p.startswith(b"\x89PNG\r\n\x1a\n"))
    ok("...and declares its own size", struct.unpack(">II", p[16:24]) == (16, 16))
    ok("...and ends with IEND", p.endswith(b"IEND\xae\x42\x60\x82"))
    ok("...and every chunk's CRC checks out", _png_crcs_ok(p))

    i = ico()
    n = struct.unpack("<H", i[4:6])[0]
    ok("the ico is an icon directory", i[:4] == b"\x00\x00\x01\x00")
    ok(f"...holding all {len(ICO_SIZES)} sizes", n == len(ICO_SIZES), str(n))
    ok("...and every entry points at a real png inside it", _ico_entries_ok(i))

    # ---- what the page is told
    h = head_html("../")
    ok("the head links carry the page's own prefix", h.count("../") == 3, h)
    ok("...the ico is declared before the svg, so a modern browser takes the vector",
       h.index("favicon.ico") < h.index("favicon.svg"))
    ok("...and the tab colour is the flag's blue", 'content="#00205B"' in h)
    ok("a root page gets bare names", "../" not in head_html(""))

    # ---- byte stability, which site_fresh_check requires of everything in docs/
    ok("two builds of the ico agree byte for byte", ico() == ico())
    ok("...and of the apple icon", png(APPLE_SIZE) == png(APPLE_SIZE))
    ok("three files ship", sorted(files()) ==
       ["apple-touch-icon.png", "favicon.ico", "favicon.svg"], str(sorted(files())))

    print("\nfavicon self-test: " + ("all passed" if not failures else f"{failures} FAILED"))
    return 0 if not failures else 1


def _png_crcs_ok(data: bytes) -> bool:
    i = 8
    while i < len(data):
        ln = struct.unpack(">I", data[i:i + 4])[0]
        kind = data[i + 4:i + 8]
        body = data[i + 8:i + 8 + ln]
        want = struct.unpack(">I", data[i + 8 + ln:i + 12 + ln])[0]
        if zlib.crc32(kind + body) & 0xFFFFFFFF != want:
            return False
        i += 12 + ln
    return True


def _ico_entries_ok(data: bytes) -> bool:
    n = struct.unpack("<H", data[4:6])[0]
    for k in range(n):
        off = 6 + 16 * k
        size, length, at = data[off], *struct.unpack("<II", data[off + 8:off + 16])
        img = data[at:at + length]
        if not img.startswith(b"\x89PNG\r\n\x1a\n"):
            return False
        w, h = struct.unpack(">II", img[16:24])
        if w != h or (size % 256) != (w % 256):
            return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--write", metavar="DIR", help="write the icon set into DIR")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.write:
        d = Path(a.write)
        d.mkdir(parents=True, exist_ok=True)
        for name, blob in files().items():
            (d / name).write_bytes(blob)
            print(f"  {name}  {len(blob)} bytes")
        return 0
    # A GATE INVOKED WITH NO ARGUMENTS EXITS 2 AND NEVER RUNS SILENTLY.
    ap.print_help()
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                            # noqa: BLE001
        print(f"favicon: broke: {exc}", file=sys.stderr)
        sys.exit(2)
