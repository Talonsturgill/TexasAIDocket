#!/usr/bin/env python3
"""grain.py — the film grain the whole site is laid over, as a data URI.

WHY GRAIN AT ALL

A flat dark background is the single loudest tell of a page nobody designed. Real ink on real
paper, a photograph, a film frame, a printed chart: all of them have noise, and an eye that has
looked at any of those reads a perfectly smooth field as a screen rather than a surface. One
tiled 110 pixel noise square at low opacity, blended over everything, is what separates a page
that looks made from a page that looks defaulted. It costs about 4 KB and no layout work.

WHY THIS IS WRITTEN BY HAND AND NOT BY PILLOW

The sibling product generates the same texture with Pillow and treats it as a soft dependency,
and its own source carries the note that a build on a box without Pillow shipped every page with
the grain silently stripped. That is this project's least favourite kind of failure: the page
still renders, nothing throws, and the thing that was supposed to be there simply is not.

A PNG is a signature, three chunks and a CRC. Writing it with `zlib` and `struct` from the
standard library removes the dependency entirely, so the texture cannot go missing, and it makes
the output byte-stable, which `site_fresh_check` requires.

WHY THE RANDOMNESS IS OUR OWN

`random.Random` is seeded and repeatable, but its guarantees are about a Python version rather
than about forever. A sixteen line LCG with published constants is repeatable for as long as
integers behave, and the byte-equality gate is a promise this file should not be able to break.

    grain.py --self-test
    grain.py --write /tmp/grain.png
"""
from __future__ import annotations

import argparse
import base64
import struct
import sys
import zlib

# Numerical Recipes' LCG constants. Chosen because they are published, tiny, and produce a
# perfectly adequate speckle. This is a texture, not a cryptographic anything.
_A, _C, _M = 1664525, 1013904223, 2 ** 32

SIZE = 110          # tile edge. Large enough that the repeat is invisible, small enough to be
                    # cheap. The sibling product landed on the same number independently.
STRENGTH = 26       # peak deviation from mid grey. Above about 32 the texture reads as dirt.
SEED = 11


def _noise(size: int, strength: int, seed: int) -> bytes:
    """One greyscale plane of seeded speckle, centred on mid grey."""
    out = bytearray(size * size)
    state = seed & 0xFFFFFFFF
    span = strength * 2 + 1
    for i in range(size * size):
        state = (_A * state + _C) % _M
        # The high bits of an LCG are the good ones. The low bits cycle short and would band.
        out[i] = 128 + (state >> 16) % span - strength
    return bytes(out)


def _chunk(kind: bytes, data: bytes) -> bytes:
    return (struct.pack(">I", len(data)) + kind + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))


def png(size: int = SIZE, strength: int = STRENGTH, seed: int = SEED) -> bytes:
    """A greyscale PNG of seeded noise, built from the format up."""
    plane = _noise(size, strength, seed)
    # Colour type 0 is greyscale, bit depth 8. Each scanline is prefixed with its filter byte,
    # and filter 0 means none, which is right for noise: every predictor makes noise LARGER.
    raw = b"".join(b"\x00" + plane[y * size:(y + 1) * size] for y in range(size))
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 0, 0, 0, 0))
            + _chunk(b"IDAT", zlib.compress(raw, 9))
            + _chunk(b"IEND", b""))


def data_uri(size: int = SIZE, strength: int = STRENGTH, seed: int = SEED) -> str:
    return "data:image/png;base64," + base64.b64encode(png(size, strength, seed)).decode()


def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    blob = png()
    ok("it is a PNG", blob.startswith(b"\x89PNG\r\n\x1a\n"))
    ok("...with a header, a data chunk and a terminator",
       b"IHDR" in blob and b"IDAT" in blob and blob.endswith(b"IEND\xae\x42\x60\x82"))

    # THE DIMENSIONS ARE READ BACK OUT OF THE FILE, not trusted from the arguments, because a
    # struct format typo produces a file that still parses as a PNG and renders as nothing.
    w, h, depth, ctype = struct.unpack(">IIBB", blob[16:26])
    ok("the header declares the right size", (w, h) == (SIZE, SIZE), f"{w}x{h}")
    ok("...at 8 bit greyscale", (depth, ctype) == (8, 0), f"depth {depth} type {ctype}")

    # Every chunk's CRC has to check out, or a browser drops the image and the page silently
    # loses its texture, which is the exact failure this module exists to make impossible.
    pos, checked = 8, 0
    while pos < len(blob):
        n = struct.unpack(">I", blob[pos:pos + 4])[0]
        kind = blob[pos + 4:pos + 8]
        body = blob[pos + 8:pos + 8 + n]
        want = struct.unpack(">I", blob[pos + 8 + n:pos + 12 + n])[0]
        if zlib.crc32(kind + body) & 0xFFFFFFFF != want:
            ok(f"chunk {kind.decode()} CRC", False)
            break
        checked += 1
        pos += 12 + n
    else:
        ok(f"every chunk's CRC verifies ({checked} chunks)", True)

    # The pixels have to be noise CENTRED ON MID GREY. An overlay blend of a field that is not
    # centred darkens or lightens the whole site, which looks like a palette bug rather than a
    # texture bug and is very hard to trace back to here.
    plane = _noise(SIZE, STRENGTH, SEED)
    mean = sum(plane) / len(plane)
    ok("the texture is centred on mid grey", abs(mean - 128) < 1.0, f"mean {mean:.2f}")
    ok("...and stays inside its stated strength",
       min(plane) >= 128 - STRENGTH and max(plane) <= 128 + STRENGTH,
       f"{min(plane)}..{max(plane)}")
    ok("...and actually varies", len(set(plane)) > STRENGTH, f"{len(set(plane))} distinct values")

    # DETERMINISM IS A HARD REQUIREMENT. docs/ has to be byte-identical to a rebuild, and this
    # texture is embedded in the stylesheet, so a wobble here fails the freshness gate on every
    # build with no obvious cause.
    ok("two builds are byte identical", png() == blob)
    ok("...and a different seed is a different texture", png(seed=12) != blob)

    uri = data_uri()
    ok("the data URI is well formed", uri.startswith("data:image/png;base64,"))
    ok("the texture stays cheap", len(uri) < 24_000, f"{len(uri)} bytes")

    if failures:
        print(f"\ngrain self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print(f"\ngrain self-test: all passed ({len(uri):,} byte data URI, no dependencies)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--write", help="write the tile to a file, to look at it")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.write:
        with open(a.write, "wb") as fh:
            fh.write(png())
        print(f"wrote {a.write}")
        return 0
    sys.stdout.write(data_uri())
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                        # noqa: BLE001
        print(f"grain: broke: {exc}", file=sys.stderr)
        sys.exit(2)
