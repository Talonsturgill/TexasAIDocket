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

**NO TEXT ON THE CARD, and that is a real limitation stated rather than hidden.** A card with
the decision's headline on it would be better, and drawing text here would mean either a font
rasteriser written from scratch or a dependency this project has already refused once. What
`grain.py` recorded is that the sibling made its texture a soft Pillow dependency, a box without
Pillow stripped it silently, and nothing threw. A card is more visible than a texture and would
fail the same way.

So this ships the strongest thing that is honestly buildable from the format up: a branded card
that is unmistakably this record. Per-decision cards carrying the headline are worth doing and
are written down in the worklog as the follow-up they are, not pretended at here.

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


def png() -> bytes:
    rgb = pixels()
    stride = W * 3
    raw = b"".join(b"\x00" + rgb[y * stride:(y + 1) * stride] for y in range(H))
    import struct
    return (b"\x89PNG\r\n\x1a\n"
            + favicon._chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
            + favicon._chunk(b"IDAT", zlib.compress(raw, 9))
            + favicon._chunk(b"IEND", b""))


def files() -> dict:
    return {"og.png": png()}


ALT = ("The Texas AI Docket. The Lone Star on the flag's blue hoist, beside the record's own "
       "dusk ground.")


def head_html(prefix: str, site_url: str, site_name: str, title: str, desc: str) -> str:
    """The social tags, beyond the four the page already had.

    `og:image` IS AN ABSOLUTE URL, always. A relative one is the single most common way a card
    silently fails: every scraper resolves it against its own base and most simply give up.
    """
    img = f"{site_url.rstrip('/')}/og.png"
    return (f'<meta property="og:image" content="{img}">\n'
            f'<meta property="og:image:width" content="{W}">\n'
            f'<meta property="og:image:height" content="{H}">\n'
            f'<meta property="og:image:alt" content="{ALT}">\n'
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

    h = head_html("", "https://example.com", "A Name", "T", "D")
    ok("the image url is absolute", 'content="https://example.com/og.png"' in h)
    ok("...and its box is declared, so a client does not guess",
       f'content="{W}"' in h and f'content="{H}"' in h)
    ok("the card is announced as a large summary", 'summary_large_image' in h)
    ok("...and carries alt text", 'og:image:alt' in h)

    ok("two builds agree byte for byte", png() == png())

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
