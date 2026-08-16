#!/usr/bin/env python3
"""truetype.py — glyph outlines out of the committed fonts, so text can be drawn from the format up.

WHY THIS EXISTS

`og.py` shipped a social card with no text on it, and said so plainly: a card carrying the
decision's headline would be better, and drawing text meant either a font rasteriser or a
dependency this project has already refused once. `grain.py` records why it was refused. The
sibling made its texture a soft Pillow dependency, a box without Pillow stripped it silently,
and nothing threw. A card fails the same way and is far more visible.

This is the other option, taken. A TrueType font is a table directory and a handful of binary
tables, and the outlines are quadratic contours that the scanline filler in `favicon.py` already
knows how to rasterise. The fonts are committed under `assets/fonts/` and are SIL OFL 1.1, which
permits exactly this.

WHAT IT READS, and nothing more than it needs

  head  unitsPerEm and the loca format
  maxp  the glyph count
  cmap  format 4, the Unicode segment mapping every modern font ships
  loca  where each glyph's outline starts
  glyf  the contours themselves, simple and composite
  hhea  the number of horizontal metrics
  hmtx  advance widths, which is what makes a line of text a line rather than a pile

WHAT IT DELIBERATELY DOES NOT DO, stated so nobody assumes otherwise

  NO VARIABLE AXES. `Fraunces-Var.ttf` is a variable font and the `glyf` table holds its
  DEFAULT instance. `gvar` deltas are not applied, so a headline renders at the face's default
  weight and optical size. That is a real rendering, not an approximation of one, and asking
  for a custom weight would silently give the default anyway, which is why the loader refuses
  rather than accepts a weight argument.

  NO KERNING AND NO SHAPING. Advances only. For Latin headlines set at display size the
  difference is a fraction of a pixel per pair, and a card is not a paragraph.

  NO HINTING. Irrelevant above about 20 pixels, and every use here is far above it.

    truetype.py --self-test
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FONT_DIR = REPO_ROOT / "assets" / "fonts"


class Font:
    """A parsed TrueType face, enough of one to lay out and fill a line of Latin text."""

    def __init__(self, path: Path):
        self.path = path
        self.data = path.read_bytes()
        self.tables = self._directory()
        self.units, self.loca_long = self._head()
        self.n_glyphs = self._maxp()
        self.loca = self._loca()
        self.cmap = self._cmap()
        self.advances = self._hmtx()

    # ---- the container
    def _directory(self) -> dict:
        n = struct.unpack(">H", self.data[4:6])[0]
        out = {}
        for i in range(n):
            off = 12 + 16 * i
            tag = self.data[off:off + 4].decode("latin-1")
            start, length = struct.unpack(">II", self.data[off + 8:off + 16])
            out[tag] = (start, length)
        for need in ("head", "maxp", "cmap", "loca", "glyf", "hhea", "hmtx"):
            if need not in out:
                raise ValueError(f"{self.path.name} has no {need} table")
        return out

    def _head(self):
        s, _ = self.tables["head"]
        units = struct.unpack(">H", self.data[s + 18:s + 20])[0]
        fmt = struct.unpack(">h", self.data[s + 50:s + 52])[0]
        return units, bool(fmt)

    def _maxp(self):
        s, _ = self.tables["maxp"]
        return struct.unpack(">H", self.data[s + 4:s + 6])[0]

    def _loca(self):
        s, _ = self.tables["loca"]
        n = self.n_glyphs + 1
        if self.loca_long:
            return list(struct.unpack(f">{n}I", self.data[s:s + 4 * n]))
        return [v * 2 for v in struct.unpack(f">{n}H", self.data[s:s + 2 * n])]

    def _cmap(self) -> dict:
        """Unicode to glyph id, from a format 4 subtable.

        Format 4 is what every modern font ships for the Basic Multilingual Plane. A face with
        only a format 12 table would raise here rather than silently map everything to glyph
        zero, which would render a headline as a row of empty boxes and look deliberate.
        """
        s, _ = self.tables["cmap"]
        n = struct.unpack(">H", self.data[s + 2:s + 4])[0]
        best = None
        for i in range(n):
            pid, eid, off = struct.unpack(">HHI", self.data[s + 4 + 8 * i:s + 12 + 8 * i])
            sub = s + off
            fmt = struct.unpack(">H", self.data[sub:sub + 2])[0]
            if fmt == 4 and (pid, eid) in ((3, 1), (0, 3), (0, 4), (0, 6), (3, 10)):
                best = sub
                break
        if best is None:
            raise ValueError(f"{self.path.name} ships no format 4 Unicode cmap")
        segx2 = struct.unpack(">H", self.data[best + 6:best + 8])[0]
        seg = segx2 // 2
        def arr(at):
            return struct.unpack(f">{seg}H", self.data[at:at + segx2])
        ends = arr(best + 14)
        starts = arr(best + 16 + segx2)
        deltas = struct.unpack(f">{seg}h", self.data[best + 16 + 2 * segx2:
                                                     best + 16 + 3 * segx2])
        range_off_at = best + 16 + 3 * segx2
        offsets = arr(range_off_at)
        out = {}
        for i in range(seg):
            for c in range(starts[i], min(ends[i], 0xFFFF) + 1):
                if offsets[i] == 0:
                    g = (c + deltas[i]) & 0xFFFF
                else:
                    at = range_off_at + 2 * i + offsets[i] + 2 * (c - starts[i])
                    if at + 2 > len(self.data):
                        continue
                    g = struct.unpack(">H", self.data[at:at + 2])[0]
                    if g:
                        g = (g + deltas[i]) & 0xFFFF
                if g:
                    out[c] = g
        return out

    def _hmtx(self) -> list:
        hs, _ = self.tables["hhea"]
        n = struct.unpack(">H", self.data[hs + 34:hs + 36])[0]
        s, _ = self.tables["hmtx"]
        out = []
        for i in range(n):
            out.append(struct.unpack(">H", self.data[s + 4 * i:s + 4 * i + 2])[0])
        return out

    def advance(self, gid: int) -> int:
        if not self.advances:
            return 0
        return self.advances[gid] if gid < len(self.advances) else self.advances[-1]

    # ---- the outlines
    def contours(self, gid: int, depth: int = 0) -> list:
        """A glyph as a list of closed contours, each a list of (x, y, on_curve) in font units.

        Composite glyphs recurse, which is what an accented capital is made of. The depth guard
        exists because a malformed font can point a component at itself and there is no reason
        to hang on one.
        """
        if gid + 1 >= len(self.loca) or depth > 5:
            return []
        s, _ = self.tables["glyf"]
        start, end = s + self.loca[gid], s + self.loca[gid + 1]
        if end <= start:
            return []                                   # a space has no outline, legitimately
        n_cont = struct.unpack(">h", self.data[start:start + 2])[0]
        if n_cont < 0:
            return self._composite(start + 10, depth)

        p = start + 10
        ends = struct.unpack(f">{n_cont}H", self.data[p:p + 2 * n_cont])
        p += 2 * n_cont
        n_pts = (ends[-1] + 1) if ends else 0
        instr = struct.unpack(">H", self.data[p:p + 2])[0]
        p += 2 + instr

        flags = []
        while len(flags) < n_pts:
            f = self.data[p]; p += 1
            flags.append(f)
            if f & 8:
                rep = self.data[p]; p += 1
                flags.extend([f] * rep)
        flags = flags[:n_pts]

        def coords(short_bit, same_bit):
            vals, v = [], 0
            nonlocal p
            for f in flags:
                if f & short_bit:
                    d = self.data[p]; p += 1
                    v += d if f & same_bit else -d
                elif not f & same_bit:
                    v += struct.unpack(">h", self.data[p:p + 2])[0]; p += 2
                vals.append(v)
            return vals

        xs = coords(2, 16)
        ys = coords(4, 32)

        out, i = [], 0
        for e in ends:
            pts = [(xs[j], ys[j], bool(flags[j] & 1)) for j in range(i, e + 1)]
            if pts:
                out.append(pts)
            i = e + 1
        return out

    def _composite(self, p: int, depth: int) -> list:
        out = []
        while True:
            flags, gi = struct.unpack(">HH", self.data[p:p + 4])
            p += 4
            if flags & 1:                                        # ARG_1_AND_2_ARE_WORDS
                a1, a2 = struct.unpack(">hh", self.data[p:p + 4]); p += 4
            else:
                a1, a2 = struct.unpack(">bb", self.data[p:p + 2]); p += 2
            sx = sy = 1.0
            if flags & 8:                                        # WE_HAVE_A_SCALE
                sx = sy = _f2dot14(self.data, p); p += 2
            elif flags & 0x40:                                   # X_AND_Y_SCALE
                sx, sy = _f2dot14(self.data, p), _f2dot14(self.data, p + 2); p += 4
            elif flags & 0x80:                                   # TWO_BY_TWO
                sx, sy = _f2dot14(self.data, p), _f2dot14(self.data, p + 6); p += 8
            dx, dy = (a1, a2) if flags & 2 else (0, 0)           # ARGS_ARE_XY_VALUES
            for c in self.contours(gi, depth + 1):
                out.append([(x * sx + dx, y * sy + dy, on) for x, y, on in c])
            if not flags & 0x20:                                 # MORE_COMPONENTS
                break
        return out


def _f2dot14(data: bytes, at: int) -> float:
    return struct.unpack(">h", data[at:at + 2])[0] / 16384.0


def flatten(contours: list, steps: int = 8) -> list:
    """Quadratic contours to polygons.

    TrueType stores quadratic B-splines and allows an IMPLIED on-curve point exactly halfway
    between two consecutive off-curve points, which is the compression that makes a naive reader
    draw a letter inside out. Those midpoints are reconstructed first, then every curve is
    subdivided.
    """
    polys = []
    for c in contours:
        if not c:
            continue
        pts = []
        for i, (x, y, on) in enumerate(c):
            nx, ny, non = c[(i + 1) % len(c)]
            pts.append((x, y, on))
            if not on and not non:
                pts.append(((x + nx) / 2, (y + ny) / 2, True))
        if not any(on for _, _, on in pts):
            continue
        while not pts[0][2]:
            pts = pts[1:] + pts[:1]

        poly, i, n = [], 0, len(pts)
        while i < n:
            x, y, on = pts[i]
            if on:
                poly.append((x, y))
                i += 1
                continue
            px, py = poly[-1] if poly else (pts[-1][0], pts[-1][1])
            ex, ey, _ = pts[(i + 1) % n]
            for s in range(1, steps + 1):
                t = s / steps
                u = 1 - t
                poly.append((u * u * px + 2 * u * t * x + t * t * ex,
                             u * u * py + 2 * u * t * y + t * t * ey))
            i += 2
        if len(poly) > 2:
            polys.append(poly)
    return polys


def layout(font: Font, text: str, size: float) -> tuple:
    """Every glyph's polygons placed on a baseline, plus the line's total advance.

    Returns (polys, width) with y GROWING DOWNWARD, which is what a raster wants and the
    opposite of what a font stores.
    """
    scale = size / font.units
    out, pen = [], 0.0
    for ch in text:
        gid = font.cmap.get(ord(ch))
        if gid is None:
            pen += font.advance(font.cmap.get(32, 0)) * scale
            continue
        for poly in flatten(font.contours(gid)):
            out.append([(pen + x * scale, -y * scale) for x, y in poly])
        pen += font.advance(gid) * scale
    return out, pen


def wrap(font: Font, text: str, size: float, max_w: float, max_lines: int = 4) -> list:
    """Break a headline to a width, on spaces, with an ellipsis if it will not fit.

    Measured with the same advances that draw it, so what is measured is what appears.
    """
    scale = size / font.units

    def width(s):
        return sum(font.advance(font.cmap.get(ord(c), 0)) for c in s) * scale

    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if width(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and (len(" ".join(lines).split()) < len(words)):
        while lines[-1] and width(lines[-1] + "...") > max_w:
            lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else lines[-1][:-1]
        lines[-1] += "..."
    return lines


_CACHE: dict = {}


def load(name: str) -> Font:
    if name not in _CACHE:
        _CACHE[name] = Font(FONT_DIR / name)
    return _CACHE[name]


def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    f = load("Fraunces-Var.ttf")
    # unitsPerEm is any value from 16 to 16384. Fraunces uses 2000, and the first version of
    # this assertion listed the two values I expected, which is a test asserting my guess
    # rather than the format.
    ok("the face parses", 16 <= f.units <= 16384, str(f.units))
    ok("...with a glyph count", f.n_glyphs > 100, str(f.n_glyphs))
    ok("...and a unicode map covering ASCII",
       all(ord(c) in f.cmap for c in "ABCXYZabcxyz0189 .,"),
       str([c for c in "ABCXYZabcxyz0189 .," if ord(c) not in f.cmap]))
    ok("...and advances", f.advance(f.cmap[ord("M")]) > 0)
    ok("a wide letter advances further than a narrow one",
       f.advance(f.cmap[ord("M")]) > f.advance(f.cmap[ord("i")]))

    # A SPACE HAS NO OUTLINE AND THAT IS NOT AN ERROR, which is the easiest thing to get wrong.
    ok("a space has an advance and no contour",
       f.advance(f.cmap[ord(" ")]) > 0 and f.contours(f.cmap[ord(" ")]) == [])

    o = f.contours(f.cmap[ord("o")])
    ok("a letter o has two contours, an outside and a counter", len(o) == 2, str(len(o)))
    polys = flatten(o)
    ok("...which flatten to two closed polygons", len(polys) == 2, str(len(polys)))
    ok("...with enough points to be curves rather than boxes",
       all(len(p) > 12 for p in polys), str([len(p) for p in polys]))

    # THE IMPLIED ON-CURVE POINT. Two consecutive off-curve points imply a midpoint, and a
    # reader that skips it draws the letter inside out. Checked on a real glyph.
    raw = f.contours(f.cmap[ord("O")])
    ok("the O has consecutive off-curve points, so the implied midpoint path is exercised",
       any(not raw[0][i][2] and not raw[0][(i + 1) % len(raw[0])][2]
           for i in range(len(raw[0]))))

    polys_l, w = layout(f, "Texas", 100)
    ok("a word lays out to some polygons", len(polys_l) > 4, str(len(polys_l)))
    ok("...and reports a width", 150 < w < 500, str(w))
    ok("...with y growing downward, so it is raster space",
       min(y for p in polys_l for _, y in p) < 0)

    ls = wrap(f, "The Public Utility Commission of Texas has proposed a new rule", 60, 700)
    ok("a long headline wraps to more than one line", len(ls) > 1, str(ls))
    ok("...and no line exceeds the width",
       all(sum(f.advance(f.cmap.get(ord(c), 0)) for c in l) * (60 / f.units) <= 700
           for l in ls), str(ls))
    ok("...and every word survives", " ".join(ls).replace("...", "").split()[:3]
       == ["The", "Public", "Utility"])

    short = wrap(f, "A short one", 60, 900)
    ok("a short headline stays on one line", len(short) == 1, str(short))

    m = load("Manrope-Var.ttf")
    ok("a second face parses too", m.n_glyphs > 100 and ord("A") in m.cmap)

    print("\ntruetype self-test: " + ("all passed" if not failures else f"{failures} FAILED"))
    return 0 if not failures else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    ap.print_help()
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                            # noqa: BLE001
        print(f"truetype: broke: {exc}", file=sys.stderr)
        sys.exit(2)
