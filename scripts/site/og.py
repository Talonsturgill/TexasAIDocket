#!/usr/bin/env python3
"""og.py — the card a shared link becomes.

WHY THIS EXISTS

The site declared four Open Graph tags and none of them was an image. Every link to this record
pasted into Slack, iMessage, LinkedIn or X rendered as a bare blue string. The sibling ships
eleven tags including a card with its dimensions and alt text, and the difference is whether a
shared link looks like a publication or like somebody's stray URL.

WHAT IT DRAWS, AND WHAT IT DELIBERATELY DOES NOT

The flag's hoist on the record's own ground: the dusk field this site is set on, a band of flag
blue, and the Lone Star. Geometry only.

**THE HEADLINE IS ON THE CARD**, set in the record's own display face, and it got there without
a dependency. The first version of this file shipped a card with no text and said plainly that
one with the decision's headline would be better but needed either a font rasteriser or the
dependency `grain.py` had already refused. `truetype.py` is that rasteriser: the fonts are
committed, they are OFL licensed, and a glyph is quadratic contours the scanline filler here
already knew how to fill.

So every decision gets its own card carrying its own headline, and the site card is the same
drawing with the site's name on it.

THE BACKGROUND IS COMPUTED ONCE. A card is 756,000 pixels and 58 of them in a Python loop would
add minutes to a build that already takes forty seconds, twice over because `site_fresh_check`
rebuilds. The ground, the band and the star are identical on every card, so they are rendered
once into a template and each card copies it and paints only where a glyph actually falls.

THE SIZE IS THE SPEC. 1200 by 630 is what every consumer crops to, and declaring
`og:image:width` and `og:image:height` is what stops a client guessing and reserving the wrong
box while it loads.

    og.py --self-test
    og.py --write /tmp/og.png
"""
from __future__ import annotations

import argparse
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import favicon                                                         # noqa: E402
import grain                                                           # noqa: E402
import mark                                                            # noqa: E402
import truetype                                                        # noqa: E402

W, H = 1200, 630

# The record's own ground and the statutory flag colours, the same values the page is set in.
GROUND = (0x14, 0x10, 0x20)          # Big Bend at dusk, the site's base
BLUE = favicon.BLUE                  # PMS 281 as derived in brand.yaml
WHITE = favicon.WHITE

# The hoist panel: a vertical band on the left, the flag's own proportion. The star sits in it
# at the size the statute gives it, so the card is the same geometry as the tab icon and the
# wordmark rather than a third drawing of the same idea.
BAND_W = int(W * 0.34)
STAR_R = (BAND_W * 0.75) / 2 * 0.62


def _grain_plane() -> bytes:
    """The site's own film grain, tiled, so the card's field is the page's field.

    Two thirds of this card is the dusk ground and a perfectly flat field is the loudest tell
    of an image nobody designed, which is the same argument `grain.py` makes for the site
    itself. Reusing that generator rather than writing a second noise source means the card and
    the page are textured identically, and it costs one tile.
    """
    return grain._noise(grain.SIZE, grain.STRENGTH, grain.SEED)


def pixels() -> bytes:
    """The card as raw RGB, drawn as flat regions with one antialiased star."""
    star = favicon.coverage(
        size=H, poly=mark.star_points(BAND_W / 2 * (H / H), H / 2, STAR_R), box=H)
    full = favicon.SS * favicon.SS
    g, gs = _grain_plane(), grain.SIZE
    out = bytearray(W * H * 3)
    for y in range(H):
        row = y * W * 3
        for x in range(W):
            i = row + x * 3
            base = BLUE if x < BAND_W else GROUND
            if x >= BAND_W:
                # The grain, at a fraction of its page strength. It reads as surface at arm's
                # length and disappears in a timeline thumbnail, which is the right amount.
                d = (g[(y % gs) * gs + (x % gs)] - 128) // 7
                base = tuple(min(255, max(0, c + d)) for c in base)
            if x < H:                       # the star's coverage plane is H wide
                c = star[y * H + x]
                if c:
                    for ch in range(3):
                        out[i + ch] = base[ch] + (WHITE[ch] - base[ch]) * c // full
                    continue
            out[i], out[i + 1], out[i + 2] = base
    return bytes(out)


_BG = None

TEXT_LEFT = BAND_W + 70
TEXT_TOP = 150
TEXT_W = W - TEXT_LEFT - 70
TITLE_SIZE = 58
LINE = 76


def _background() -> bytearray:
    global _BG
    if _BG is None:
        _BG = bytearray(pixels())
    return bytearray(_BG)


_GLYPH: dict = {}


def _glyph_cov(face, ch: str, size: float):
    """One character's antialiased coverage, rasterised once and kept.

    THE WIN THIS EXISTS FOR. 58 headlines are about 3,000 glyph instances drawn from roughly
    sixty distinct characters, and the first version rasterised every instance. That put seven
    minutes on CI, where the build already runs twice under `site_fresh_check`. A letter is the
    same shape everywhere it appears, so it is filled once and stamped after that.

    Returned as (width, height, x offset, y offset, coverage counts) with the offsets relative
    to the pen position on the baseline.
    """
    key = (id(face), ch, size)
    hit = _GLYPH.get(key)
    if hit is not None:
        return hit
    gid = face.cmap.get(ord(ch))
    polys = truetype.flatten(face.contours(gid)) if gid is not None else []
    scale = size / face.units
    polys = [[(x * scale, -y * scale) for x, y in poly] for poly in polys]
    if not polys:
        out = (0, 0, 0, 0, [])
        _GLYPH[key] = out
        return out
    xs = [x for p in polys for x, _ in p]
    ys = [y for p in polys for _, y in p]
    ox, oy = int(min(xs)) - 1, int(min(ys)) - 1
    bw, bh = int(max(xs)) - ox + 2, int(max(ys)) - oy + 2
    ss = favicon.SS
    counts = [0] * (bw * bh)
    edges = [[(x - ox, y - oy) for x, y in poly] for poly in polys]
    for sy in range(bh * ss):
        y = (sy + 0.5) / ss
        hits = []
        for poly in edges:
            n = len(poly)
            for i in range(n):
                ax, ay = poly[i]
                bx, by = poly[(i + 1) % n]
                if (ay <= y < by) or (by <= y < ay):
                    hits.append(ax + (y - ay) / (by - ay) * (bx - ax))
        if not hits:
            continue
        hits.sort()
        row = (sy // ss) * bw
        for k in range(0, len(hits) - 1, 2):
            xa, xb = hits[k], hits[k + 1]
            sa, sb = max(0, int(xa * ss)), min(bw * ss, int(xb * ss) + 1)
            for sx in range(sa, sb):
                if xa <= (sx + 0.5) / ss < xb:
                    counts[row + sx // ss] += 1
    out = (bw, bh, ox, oy, counts)
    _GLYPH[key] = out
    return out


def _draw_text(buf: bytearray, face, text: str, size: float, left: float, baseline: float,
               colour) -> None:
    """Stamp a line of cached glyphs onto the card.

    THE PEN LANDS ON A WHOLE PIXEL. A cached glyph carries no sub-pixel phase, so the advance is
    rounded when it is stamped. At display size that is a spacing difference nobody can see, and
    it is deterministic, which `site_fresh_check` requires of every byte in `docs/`.
    """
    full = favicon.SS * favicon.SS
    pen = left
    scale = size / face.units
    for ch in text:
        gid = face.cmap.get(ord(ch))
        bw, bh, ox, oy, counts = _glyph_cov(face, ch, size)
        if bw:
            gx, gy = int(pen) + ox, int(baseline) + oy
            for yy in range(bh):
                py = gy + yy
                if not 0 <= py < H:
                    continue
                row = yy * bw
                base = py * W
                for xx in range(bw):
                    c = counts[row + xx]
                    if not c:
                        continue
                    px = gx + xx
                    if not 0 <= px < W:
                        continue
                    i = (base + px) * 3
                    for k in range(3):
                        buf[i + k] += (colour[k] - buf[i + k]) * min(c, full) // full
        pen += (face.advance(gid) if gid is not None
                else face.advance(face.cmap.get(32, 0))) * scale


def card(headline: str) -> bytes:
    """One card, with a headline set in the record's display face."""
    buf = _background()
    face = truetype.load("Fraunces-Var.ttf")
    lines = truetype.wrap(face, headline, TITLE_SIZE, TEXT_W, max_lines=4)
    for i, line in enumerate(lines):
        _draw_text(buf, face, line, TITLE_SIZE, TEXT_LEFT, TEXT_TOP + i * LINE, WHITE)
    return _encode(bytes(buf))


def _encode(rgb: bytes) -> bytes:
    stride = W * 3
    raw = b"".join(b"\x00" + rgb[y * stride:(y + 1) * stride] for y in range(H))
    import struct
    return (b"\x89PNG\r\n\x1a\n"
            + favicon._chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
            + favicon._chunk(b"IDAT", zlib.compress(raw, 9))
            + favicon._chunk(b"IEND", b""))


def png() -> bytes:
    """The site card: the same drawing with the record's own name on it."""
    return card("The Texas AI Docket")


def files(items: list | None = None, runs: list | None = None) -> dict:
    """The site card, plus one per decision and one per article.

    THE ARTICLES USED TO SHARE THE SITE CARD. Every decision got its own headline on a card
    and the three pages carrying actual writing got the generic one, so a link to an article
    posted anywhere looked like a link to the front page. Same drawing, same rasteriser, the
    article's own headline on it.
    """
    out = {"og.png": png()}
    for it in items or []:
        out[f"og/{it['id']}.png"] = card(it["title"])
    for r in runs or []:
        out[f"og/article-{r['date']}.png"] = card(r["title"])
    return out


ALT = ("The Texas AI Docket. The Lone Star on the flag's blue hoist, beside the record's own "
       "dusk ground.")


def head_html(prefix: str, site_url: str, site_name: str, title: str, desc: str,
              image: str = "og.png", alt: str | None = None) -> str:
    """The social tags, beyond the four the page already had.

    `og:image` IS AN ABSOLUTE URL, always. A relative one is the single most common way a card
    silently fails: every scraper resolves it against its own base and most simply give up.
    """
    img = f"{site_url.rstrip('/')}/{image}"
    return (f'<meta property="og:image" content="{img}">\n'
            f'<meta property="og:image:width" content="{W}">\n'
            f'<meta property="og:image:height" content="{H}">\n'
            f'<meta property="og:image:alt" content="{alt or ALT}">\n'
            f'<meta property="og:site_name" content="{site_name}">\n'
            f'<meta property="og:locale" content="en_US">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n'
            f'<meta name="twitter:image" content="{img}">')


def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    import struct
    p = png()
    ok("the card has the png signature", p.startswith(b"\x89PNG\r\n\x1a\n"))
    ok("...at the size every consumer crops to",
       struct.unpack(">II", p[16:24]) == (W, H), str(struct.unpack(">II", p[16:24])))
    ok("...and every chunk's CRC checks out", favicon._png_crcs_ok(p))

    px = pixels()

    def at(x, y):
        i = (y * W + x) * 3
        return tuple(px[i:i + 3])

    ok("the hoist band is flag blue", at(10, 10) == BLUE, str(at(10, 10)))
    ok("the field beside it is the record's own ground, within the grain's swing",
       all(abs(a - b) <= 6 for a, b in zip(at(W - 10, 10), GROUND)), str(at(W - 10, 10)))
    ok("the star is drawn in white", at(int(BAND_W / 2), H // 2) == WHITE,
       str(at(int(BAND_W / 2), H // 2)))
    ok("the star sits inside the band, not across the card",
       all(abs(a - b) <= 6 for a, b in zip(at(BAND_W + 40, H // 2), GROUND)),
       str(at(BAND_W + 40, H // 2)))
    # Measured inside the BAND only, where the ground is flat, so the grain on the right
    # cannot make this assertion pass by itself.
    mids = sum(1 for y in range(H) for x in range(BAND_W)
               if at(x, y) not in (BLUE, WHITE))
    ok("its edges are antialiased rather than stepped", mids > 200, str(mids))
    ok("...and the field carries the site's own grain",
       len({at(W - 5, y) for y in range(0, H, 7)}) > 3)

    # THE HEADLINE IS ACTUALLY ON THE CARD, checked by counting ink where the text sits rather
    # than by trusting that the call returned. A rasteriser that silently draws nothing is the
    # exact failure this replaced a dependency to avoid.
    blank = _background()
    lit = card("PUCT Docket 59315, Oncor application for a 765 kV transmission line")
    import zlib as _z
    ok("a headline card differs from the empty one", lit != _encode(bytes(blank)))

    buf = _background()
    face = truetype.load("Fraunces-Var.ttf")
    _draw_text(buf, face, "Texas", TITLE_SIZE, TEXT_LEFT, TEXT_TOP, WHITE)

    def px(b, x, y):
        i = (y * W + x) * 3
        return tuple(b[i:i + 3])

    painted = sum(1 for y in range(TEXT_TOP - 60, TEXT_TOP + 10)
                  for x in range(TEXT_LEFT, TEXT_LEFT + 300)
                  if px(buf, x, y) != px(blank, x, y))
    ok("glyphs put ink on the card", painted > 500, str(painted))
    ok("...only inside the text area, never over the star",
       all(px(buf, x, y) == px(blank, x, y)
           for y in range(H // 2 - 20, H // 2 + 20) for x in range(0, BAND_W, 7)))
    ok("...and the ink is antialiased rather than a hard stencil",
       len({px(buf, x, TEXT_TOP - 30) for x in range(TEXT_LEFT, TEXT_LEFT + 300)}) > 8)

    ok("a long headline wraps instead of running off the card",
       len(truetype.wrap(face, "The Public Utility Commission of Texas has proposed a new "
                               "rule governing demand management for large loads",
                         TITLE_SIZE, TEXT_W, 4)) > 1)

    ok("every card is the same size whatever the headline",
       len(_encode(bytes(_background()))) > 0
       and __import__("struct").unpack(">II", card("A")[16:24]) == (W, H))

    h = head_html("", "https://example.com", "A Name", "T", "D")
    ok("the image url is absolute", 'content="https://example.com/og.png"' in h)
    ok("...and its box is declared, so a client does not guess",
       f'content="{W}"' in h and f'content="{H}"' in h)
    ok("the card is announced as a large summary", 'summary_large_image' in h)
    ok("...and carries alt text", 'og:image:alt' in h)

    ok("two builds agree byte for byte", png() == png())
    ok("...and so does a decision's card", card("A title") == card("A title"))
    ok("a different headline makes a different card", card("A") != card("B"))

    print("\nog self-test: " + ("all passed" if not failures else f"{failures} FAILED"))
    return 0 if not failures else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--write", metavar="PATH")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.write:
        Path(a.write).write_bytes(png())
        print(f"  {a.write}  {len(png())} bytes")
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                            # noqa: BLE001
        print(f"og: broke: {exc}", file=sys.stderr)
        sys.exit(2)
