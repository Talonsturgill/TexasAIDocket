"""The publication's social cover: Texas carved out of the public record.

This is a small, deterministic software render, not a screenshot or a network asset.
The county seams and silhouette use the same Albers projection and TopoJSON as
the site's map. Every county has the same material and height: this is a brand
sculpture, not a map of activity, coverage, risk or physical terrain.

Geometry uses the standard library; type uses the site's already required,
pinned Pillow dependency so variable fonts use their actual editorial weights.
The site keeps building offline without a browser or a new dependency.
"""
from __future__ import annotations

import math

from PIL import Image, ImageDraw, ImageFont

import mark
import texas_map
import theme

W, H = 1200, 630
SS = 2
# A conservative profile-card crop, narrower than the supplied LinkedIn
# screenshot. The publication name and sculpture must survive both this and
# the full-width post preview.
FEATURED_ASPECT = 8 / 5


def colours() -> dict:
    return {name: theme._rgb(value) for name, value in theme.tokens()["colour"].items()}


def mix(a, b, amount):
    return tuple(round(x + (y - x) * amount) for x, y in zip(a, b))


class Surface:
    """Supersampled polygon drawing, downsampled once after all the geometry."""

    def __init__(self, colour):
        self.w, self.h = W * SS, H * SS
        self.rgb = bytearray(bytes(colour) * (self.w * self.h))

    def polygon(self, points, colour):
        points = [(x * SS, y * SS) for x, y in points]
        low = max(0, math.floor(min(y for _, y in points)))
        high = min(self.h, math.ceil(max(y for _, y in points)))
        edges = list(zip(points, points[1:] + points[:1]))
        for row in range(low, high):
            y = row + 0.5
            hits = sorted(ax + (y - ay) * (bx - ax) / (by - ay)
                          for (ax, ay), (bx, by) in edges
                          if (ay <= y < by) or (by <= y < ay))
            ink = bytes(colour(row / SS) if callable(colour) else colour)
            for left, right in zip(hits[::2], hits[1::2]):
                a, b = max(0, math.ceil(left - 0.5)), min(self.w, math.ceil(right - 0.5))
                if b > a:
                    offset = (row * self.w + a) * 3
                    self.rgb[offset:offset + (b - a) * 3] = ink * (b - a)

    def line(self, points, colour, width=1):
        for (ax, ay), (bx, by) in zip(points, points[1:]):
            length = math.hypot(bx - ax, by - ay)
            if not length:
                continue
            dx, dy = -(by - ay) * width / (2 * length), (bx - ax) * width / (2 * length)
            self.polygon([(ax + dx, ay + dy), (bx + dx, by + dy),
                          (bx - dx, by - dy), (ax - dx, ay - dy)], colour)

    def pixels(self) -> bytes:
        out = bytearray(W * H * 3)
        # SS is deliberately fixed at two. Four integer samples have the same
        # result on every Python platform; there is no host-dependent filter.
        for y in range(H):
            top, bottom = y * 2 * self.w * 3, (y * 2 + 1) * self.w * 3
            for x in range(W):
                a, b, dest = top + x * 6, bottom + x * 6, (y * W + x) * 3
                for ch in range(3):
                    out[dest + ch] = (self.rgb[a + ch] + self.rgb[a + 3 + ch]
                                      + self.rgb[b + ch] + self.rgb[b + 3 + ch]) // 4
        return bytes(out)


def geometry():
    """Fit the real county geometry to the sculpted object, retaining north up."""
    counties = texas_map.county_rings()
    points = [p for _, _, rings in counties for ring in rings for p in ring]
    minx, maxx = min(x for x, _ in points), max(x for x, _ in points)
    miny, maxy = min(y for _, y in points), max(y for _, y in points)
    scale = min(460 / (maxx - minx), 450 / (maxy - miny))

    def local(point):
        return ((point[0] - minx) * scale, (point[1] - miny) * scale)

    rings = [(name, [[local(p) for p in ring] for ring in paths])
             for _, name, paths in counties]
    boundary = [[local(p) for p in arc] for arc in texas_map.state_outline()]
    return rings, boundary


def project(point, height=0):
    x, y = point
    return 588 + x + y * 0.075, 159 + y * 0.83 - x * 0.075 - height


def pixels() -> bytes:
    c = colours()
    canvas = Surface(c["night"])
    counties, boundary = geometry()

    # A dark work surface and a pool of light under the object. Concentric
    # polygons interpolate two existing grounds, rather than adding a new hue.
    for radius in range(350, 70, -4):
        amount = (350 - radius) / 280 * 0.46
        ellipse = [(861 + math.cos(t * math.tau / 80) * radius,
                    340 + math.sin(t * math.tau / 80) * radius * 0.66)
                   for t in range(80)]
        canvas.polygon(ellipse, mix(c["night"], c["panel"], amount))

    # The folio has actual edge thickness and shared vanishing directions.
    # Recessed rules are physical document furniture, not invented readings.
    sheet = [(-9, 39), (475, 39), (475, 439), (-9, 439)]
    for height, material in ((0, "flag_blue"), (7, "deep"), (14, "flag_blue"), (21, "deep")):
        top = [project(p, height) for p in sheet]
        lower = [project(p, height - 5) for p in sheet]
        canvas.polygon([top[2], top[3], lower[3], lower[2]], mix(c[material], c["dust"], 0.16))
        canvas.polygon([top[1], top[2], lower[2], lower[1]], mix(c[material], c["night"], 0.2))
        canvas.polygon(top, c[material])
        canvas.line(top + top[:1], mix(c[material], c["dust"], 0.25), 0.7)

    inset = [(8, 54), (457, 54), (457, 421), (8, 421), (8, 54)]
    canvas.line([project(p, 22) for p in inset], mix(c["deep"], c["dust"], 0.32), 0.7)
    # Register lines on the exposed foot of the folio stay subordinate to the
    # sculpture. No fake map pins, numeric labels or data-shaped decorations.
    for y, length in ((388, 103), (398, 77), (408, 91)):
        canvas.line([project((30, y), 23), project((30 + length, y), 23)],
                    mix(c["deep"], c["dust"], 0.42), 1)

    # Soft contact shadow: the small offset layers sit below the raised edge.
    for offset in range(14, 0, -2):
        shadow = mix(c["deep"], c["night"], 0.82 - offset * 0.02)
        for _, rings in counties:
            for ring in rings:
                canvas.polygon([(x + offset * 0.5, y + offset)
                                for x, y in (project(p, 22) for p in ring)], shadow)

    # Side faces are lit from upper left. Only state-boundary edges are
    # extruded; internal county borders are incisions in one solid plate.
    for arc in boundary:
        for a, b in zip(arc, arc[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            length = math.hypot(dx, dy)
            if not length:
                continue
            light = 0.12 + 0.17 * abs((dx + dy) / (length * math.sqrt(2)))
            material = mix(c["flag_blue"], c["dust"], light)
            canvas.polygon([project(a, 25), project(b, 25),
                            project(b, 57), project(a, 57)], material)

    def stone(y):
        return mix(c["limestone"], c["dust"], max(0, min(0.42, (y - 90) / 900)))

    for _, rings in counties:
        for ring in rings:
            canvas.polygon([project(p, 57) for p in ring], stone)
    seam = mix(c["dust"], c["deep"], 0.34)
    for _, rings in counties:
        for ring in rings:
            canvas.line([project(p, 57) for p in ring], seam, 0.62)
    # A narrow bevel catches the same key light as the upper surface.
    for arc in boundary:
        canvas.line([project(p, 57) for p in arc], c["limestone"], 1.35)
        canvas.line([project(p, 56) for p in arc], mix(c["dust"], c["limestone"], 0.4), 0.6)

    # Quiet publication rules sit well inside common preview crops.
    canvas.line([(104, 548), (1096, 548)], mix(c["line"], c["dust"], 0.24), 0.8)
    canvas.line([(104, 548), (145, 548)], c["dusk_gold"], 2)
    canvas.polygon([(104, 58), (152, 58), (152, 106), (104, 106)], c["flag_blue"])
    canvas.polygon(mark.star_points(128, 82, 16), c["flag_white"])
    return canvas.pixels()


def font(filename, size):
    """Real variable instances, not synthetic bold or a silent default weight."""
    path = texas_map.REPO_ROOT / "assets" / "fonts" / filename
    # Optional RAQM changes glyph placement on otherwise identical installs.
    # This fixed Latin masthead uses the layout engine available on every host.
    face = ImageFont.truetype(str(path), round(size * SS), layout_engine=ImageFont.Layout.BASIC)
    if filename.endswith("-Var.ttf"):
        settings = {b"Weight": 650 if filename.startswith("Fraunces") else 500,
                    b"Optical Size": 72}
        face.set_variation_by_axes([settings.get(axis["name"], axis["default"])
                                    for axis in face.get_variation_axes()])
    return face


def lettering(background: bytes, lines) -> bytes:
    image = Image.frombytes("RGB", (W, H), background).resize((W * SS, H * SS),
                                                           Image.Resampling.BICUBIC)
    draw = ImageDraw.Draw(image)
    c = colours()
    for filename, text, size, left, baseline, colour in lines:
        draw.text((left * SS, baseline * SS), text, font=font(filename, size),
                  fill=c[colour], anchor="ls")
    return image.resize((W, H), Image.Resampling.LANCZOS).tobytes()
