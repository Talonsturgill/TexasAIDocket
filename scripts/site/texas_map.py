#!/usr/bin/env python3
"""texas_map.py — Texas drawn from real county geometry, lit by the record.

THE IDEA

Most policy sites decorate with a state silhouette. This one draws all 254 counties from the
same geodata the resolver uses, and lights the ones the docket actually touches. It is not an
ornament that happens to look like Texas. It is the record, rendered.

That matters for a reason beyond looks. A reader in Hood County sees Hood County. A reader who
sees the Permian lit and the Piney Woods dark has learned something true in one glance that a
paragraph would take a while to say. And because it is generated from `ledger/docket.json`, it
cannot flatter us: an empty docket draws an empty map.

WHAT THIS IS NOT. It is not a heat map and it carries no severity ramp. A county is lit or it is
not, at one intensity, exactly like the grid watch bar. Shading counties by "how bad" would be a
verdict, and the verdict is the thing this project does not publish.

    texas_map.py --self-test
    texas_map.py --out /tmp/tx.svg --lit Hood,Hill,Ector
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "shared"))

import places as _places                                          # noqa: E402

COUNTIES_SRC = REPO_ROOT / "assets" / "geo" / "tx-counties.topo.json"

# Albers equal-area conic, tuned for Texas rather than for the lower 48. Texas runs about
# 25.8N to 36.5N and 106.6W to 93.5W, so the standard parallels sit at a sixth in from each
# edge, which is the classic rule and keeps distortion even across the Panhandle and the Valley.
LAT0, LON0 = 31.2, -99.9
LAT1, LAT2 = 27.6, 35.0

# Coordinate precision in the emitted path data. Two decimals on a 1000-unit viewBox is roughly
# a tenth of a pixel at any size this renders at, and it cuts the file by more than half.
PRECISION = 2
VIEW_W, VIEW_H = 1000.0, 900.0
MARGIN = 18.0                     # the neatline inset, and the fit padding. One number, one job.

# Mean Earth radius, in statute miles. The projection above works on a unit sphere, so this is
# the only constant that turns projected units into a distance somebody can use.
EARTH_MI = 3958.7613

# Candidate scale bar lengths. The largest that fits inside a quarter of the sheet wins, so the
# bar is chosen by measurement rather than drawn to look about right.
SCALE_STEPS = (50, 100, 200, 250, 500)

# Whole degrees to tick on the neatline. Texas spans about 106.6W to 93.5W and 25.8N to 36.5N,
# so every second degree is dense enough to read as a graticule and sparse enough to stay quiet.
MERIDIANS = range(-106, -93, 2)
PARALLELS = range(26, 37, 2)


def albers(lon: float, lat: float) -> tuple[float, float]:
    """Albers equal-area conic. Returns unscaled x, y in projection units."""
    lon_r, lat_r = math.radians(lon), math.radians(lat)
    lon0_r, lat0_r = math.radians(LON0), math.radians(LAT0)
    lat1_r, lat2_r = math.radians(LAT1), math.radians(LAT2)

    n = 0.5 * (math.sin(lat1_r) + math.sin(lat2_r))
    c = math.cos(lat1_r) ** 2 + 2 * n * math.sin(lat1_r)
    rho0 = math.sqrt(c - 2 * n * math.sin(lat0_r)) / n
    rho = math.sqrt(c - 2 * n * math.sin(lat_r)) / n
    theta = n * (lon_r - lon0_r)
    # Y IS NEGATED HERE. In Albers, y grows northward; in SVG, y grows downward. Without this
    # the whole state renders upside down, with the Panhandle in the Gulf, and it renders
    # plausibly enough that only a check against known counties catches it.
    return rho * math.sin(theta), -(rho0 - rho * math.cos(theta))


def county_rings() -> list[tuple[str, str, list]]:
    """[(fips, name, [ring, ...]), ...] in projected units, straight from the TopoJSON."""
    topo = json.loads(COUNTIES_SRC.read_text(encoding="utf-8"))
    arcs = _places.decode_arcs(topo)
    out = []
    for geom in topo["objects"]["counties"]["geometries"]:
        props = geom.get("properties") or {}
        name = props.get("name") or ""
        fips = str(geom.get("id") or props.get("fips") or "")
        if not fips.startswith("48"):                 # Texas only; the atlas is national
            continue
        rings = [[albers(x, y) for x, y in ring]
                 for ring in _places.geometry_rings(geom, arcs)]
        out.append((fips, name, rings))
    out.sort(key=lambda r: r[0])                      # deterministic, so rebuilds are byte-equal
    return out


def fit(rings_by_county: list) -> tuple[float, float, float]:
    """Scale and offset that fit every ring into the viewBox with a small margin."""
    xs = [x for _, _, rings in rings_by_county for r in rings for x, _ in r]
    ys = [y for _, _, rings in rings_by_county for r in rings for _, y in r]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    pad = MARGIN
    scale = min((VIEW_W - 2 * pad) / (maxx - minx), (VIEW_H - 2 * pad) / (maxy - miny))
    # Centre what is left over, so the shape sits in the middle rather than in a corner.
    dx = pad + (VIEW_W - 2 * pad - (maxx - minx) * scale) / 2 - minx * scale
    dy = pad + (VIEW_H - 2 * pad - (maxy - miny) * scale) / 2 - miny * scale
    return scale, dx, dy


def path_d(rings: list, scale: float, dx: float, dy: float) -> str:
    """SVG path data, with repeated points dropped after rounding.

    Rounding first and de-duplicating second is what makes this small: adjacent source vertices
    frequently collapse onto the same rendered point at this precision, and emitting both costs
    bytes for a line nobody can see.
    """
    parts = []
    for ring in rings:
        pts, last = [], None
        for x, y in ring:
            p = (round(x * scale + dx, PRECISION), round(y * scale + dy, PRECISION))
            if p != last:
                pts.append(p)
                last = p
        if len(pts) < 3:
            continue
        if pts[0] == pts[-1]:
            pts.pop()
        parts.append("M" + "L".join(f"{x:g},{y:g}" for x, y in pts) + "Z")
    return "".join(parts)


# --------------------------------------------------------------------------- survey furniture
def great_circle_mi(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Haversine, in statute miles. The ground truth the scale bar is measured against."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_MI * math.asin(math.sqrt(a))


def units_per_mile(scale: float) -> float:
    """View units per statute mile, measured on the projection rather than assumed.

    Albers is EQUAL AREA, which means it does not preserve distance, so a single number cannot
    be right everywhere on the sheet. It is exact along the two standard parallels and drifts
    between and beyond them, which is why the caption says where the bar holds instead of
    implying it holds everywhere. Measuring across a degree of longitude at the reference
    latitude puts the sample between the standard parallels, where the error is smallest.
    """
    x1, _ = albers(LON0 - 0.5, LAT0)
    x2, _ = albers(LON0 + 0.5, LAT0)
    projected = abs(x2 - x1) * scale
    return projected / great_circle_mi(LON0 - 0.5, LAT0, LON0 + 0.5, LAT0)


def _crossing(fixed: float, lo: float, hi: float, target: float, axis: int,
              scale: float, dx: float, dy: float, along_lat: bool) -> float | None:
    """Where a graticule line crosses a neatline edge, by bisection.

    A meridian on a conic projection is a straight line that is not vertical, and a parallel is
    an arc. Neither meets a rectangular frame at a position you can compute from the corner, so
    the tick has to be placed where the line ACTUALLY crosses. Fifty bisections resolve it far
    below the rounding precision of the emitted path data.
    """
    def at(t: float) -> tuple[float, float]:
        x, y = albers(fixed, t) if along_lat else albers(t, fixed)
        return x * scale + dx, y * scale + dy

    a, b = lo, hi
    if (at(a)[axis] - target) * (at(b)[axis] - target) > 0:
        return None                                   # the line never reaches this edge
    for _ in range(50):
        m = (a + b) / 2
        if (at(a)[axis] - target) * (at(m)[axis] - target) <= 0:
            b = m
        else:
            a = m
    return (a + b) / 2


def graticule(scale: float, dx: float, dy: float) -> str:
    """Whole-degree ticks on the neatline, each placed where its own line crosses the frame."""
    left, right = MARGIN, VIEW_W - MARGIN
    top, bottom = MARGIN, VIEW_H - MARGIN
    out = [f'<rect class="frame" x="{left:g}" y="{top:g}" '
           f'width="{right - left:g}" height="{bottom - top:g}"/>']

    for lon in MERIDIANS:
        lat = _crossing(lon, 25.0, 37.5, bottom, 1, scale, dx, dy, along_lat=True)
        if lat is None:
            continue
        x = albers(lon, lat)[0] * scale + dx
        if not (left <= x <= right):
            continue
        out.append(f'<line class="tick" x1="{x:.1f}" y1="{bottom:g}" '
                   f'x2="{x:.1f}" y2="{bottom - 7:g}"/>')
        out.append(f'<text class="lab" x="{x:.1f}" y="{bottom - 11:g}" '
                   f'text-anchor="middle">{abs(lon)}°W</text>')

    for lat in PARALLELS:
        lon = _crossing(lat, -108.0, -92.0, left, 0, scale, dx, dy, along_lat=False)
        if lon is None:
            continue
        y = albers(lon, lat)[1] * scale + dy
        if not (top <= y <= bottom):
            continue
        out.append(f'<line class="tick" x1="{left:g}" y1="{y:.1f}" '
                   f'x2="{left + 7:g}" y2="{y:.1f}"/>')
        out.append(f'<text class="lab" x="{left + 11:g}" y="{y:.1f}" '
                   f'dominant-baseline="middle">{lat}°N</text>')
    return "".join(out)


def scale_bar(scale: float, dx: float, dy: float) -> tuple[str, int]:
    """A bar of a round number of miles, sized by the projection. Returns the SVG and the miles.

    Drawn as a survey checker: two alternating segments so a reader can halve it by eye, with
    end ticks. The LENGTH is computed from the projection, so the bar is a measurement of the
    drawing rather than a decoration placed near it.
    """
    upm = units_per_mile(scale)
    usable = (VIEW_W - 2 * MARGIN) * 0.28
    miles = SCALE_STEPS[0]
    for step in SCALE_STEPS:
        if step * upm <= usable:
            miles = step
    length = miles * upm

    # TOP LEFT, which is where a survey sheet puts it and, not by coincidence, the only large
    # empty field Texas's own shape leaves on a rectangular sheet: everything northwest of the
    # Panhandle is New Mexico and Oklahoma. The first version sat bottom left and collided with
    # the 26 degree parallel's label, which is what a scale bar looks like when it is placed by
    # eye rather than against the drawing it belongs to.
    x0 = MARGIN + 34
    y0 = MARGIN + 52
    half = length / 2
    return ("".join([
        f'<line class="scale" x1="{x0:.1f}" y1="{y0:.1f}" '
        f'x2="{x0 + length:.1f}" y2="{y0:.1f}"/>',
        # End and midpoint ticks. Three marks is the least that lets a reader halve the bar.
        f'<line class="scale" x1="{x0:.1f}" y1="{y0 - 4:.1f}" x2="{x0:.1f}" y2="{y0 + 4:.1f}"/>',
        f'<line class="scale" x1="{x0 + half:.1f}" y1="{y0 - 3:.1f}" '
        f'x2="{x0 + half:.1f}" y2="{y0 + 3:.1f}"/>',
        f'<line class="scale" x1="{x0 + length:.1f}" y1="{y0 - 4:.1f}" '
        f'x2="{x0 + length:.1f}" y2="{y0 + 4:.1f}"/>',
        f'<text class="lab" x="{x0:.1f}" y="{y0 - 9:.1f}">{miles} miles</text>',
    ]), miles)


def render(lit: set | None = None, *, title: str = "Texas counties in the record",
           idprefix: str = "txmap") -> str:
    """The whole map as one inline SVG.

    `lit` is a set of county NAMES (as the geodata spells them) or FIPS codes. Anything not lit
    is drawn in the faint field colour, which is the honest default: most of Texas is not in the
    record on most days, and the map should say so.
    """
    lit = {str(x).strip().lower() for x in (lit or set())}
    counties = county_rings()
    scale, dx, dy = fit(counties)

    n_lit = 0
    paths = []
    for fips, name, rings in counties:
        on = name.lower() in lit or fips in lit
        n_lit += 1 if on else 0
        d = path_d(rings, scale, dx, dy)
        if not d:
            continue
        cls = "c on" if on else "c"
        # The title element is what a screen reader announces, and it is also what a sighted
        # reader gets on hover with no JavaScript at all.
        paths.append(
            f'<path class="{cls}" d="{d}" data-fips="{fips}" data-county="{name}">'
            f"<title>{name} County</title></path>"
        )

    bar, miles = scale_bar(scale, dx, dy)
    return (
        f'<svg class="txmap" viewBox="0 0 {VIEW_W:g} {VIEW_H:g}" role="img" '
        f'aria-labelledby="{idprefix}-t" preserveAspectRatio="xMidYMid meet">'
        f'<title id="{idprefix}-t">{title}. '
        f'{n_lit} of {len(counties)} counties carry an item. '
        f'Albers equal-area conic, {miles} mile scale bar.</title>'
        f'<g>{"".join(paths)}</g>'
        # The furniture is drawn LAST so it sits over the counties, and it is drawn as a group
        # so the whole survey layer can be hidden in print with one selector.
        f'<g class="survey">{graticule(scale, dx, dy)}{bar}</g></svg>'
    )


def lit_from_docket(ledger: Path) -> set:
    """Every county named by any item in the record."""
    if not ledger.exists():
        return set()
    raw = json.loads(ledger.read_text(encoding="utf-8"))
    items = raw if isinstance(raw, list) else raw.get("items", [])
    out = set()
    for it in items:
        for c in (it.get("geography") or {}).get("counties") or []:
            out.add(str(c).strip())
    return out


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    failures = 0

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    counties = county_rings()
    check("all 254 Texas counties decode", len(counties) == 254, f"got {len(counties)}")

    scale, dx, dy = fit(counties)
    xs, ys = [], []
    for _, _, rings in counties:
        for r in rings:
            for x, y in r:
                xs.append(x * scale + dx)
                ys.append(y * scale + dy)
    check("every point lands inside the viewBox",
          min(xs) >= -0.5 and max(xs) <= VIEW_W + 0.5
          and min(ys) >= -0.5 and max(ys) <= VIEW_H + 0.5,
          f"x {min(xs):.1f}..{max(xs):.1f} y {min(ys):.1f}..{max(ys):.1f}")

    # Orientation, checked against three counties whose relative positions are not in doubt.
    by_name = {n: rings for _, n, rings in counties}
    def centre(nm):
        pts = [p for r in by_name[nm] for p in r]
        return (sum(p[0] for p in pts) / len(pts) * scale + dx,
                sum(p[1] for p in pts) / len(pts) * scale + dy)
    dallam = centre("Dallam")        # far northwest corner
    cameron = centre("Cameron")      # far south tip
    elpaso = centre("El Paso")       # far west
    check("north is up: Dallam sits above Cameron", dallam[1] < cameron[1])
    check("west is left: El Paso sits left of Cameron", elpaso[0] < cameron[0])

    svg = render(lit={"Hood", "Ector"})
    check("the SVG carries one path per county", svg.count("<path") == 254,
          f"got {svg.count('<path')}")
    n_on = svg.count('class="c on"')
    check("lit counties are marked", n_on == 2, f"got {n_on}")
    check("the accessible title counts what is lit", "2 of 254 counties" in svg)
    size = len(svg.encode("utf-8"))
    check(f"the map stays inline-able ({size // 1024} KB)", size < 120_000, f"{size} bytes")

    # Determinism is what lets the site claim a byte-equal rebuild.
    check("two renders are byte identical", render(lit={"Hood"}) == render(lit={"Hood"}))

    # Matching by FIPS must work as well as by name, since the ledger may carry either.
    check("FIPS lights the same county as its name",
          render(lit={"48221"}).count('class="c on"') == 1)

    # ---- THE SURVEY FURNITURE, and whether it tells the truth -----------------
    # A scale bar that is decorative is worse than none: it invites a reader to measure with it.
    # So the bar is checked the way a reader would use it, by measuring a known distance off the
    # drawing and comparing against the great circle. Albers is equal-area rather than
    # equidistant, so some error is expected and the tolerance says how much is acceptable
    # rather than pretending there is none.
    upm = units_per_mile(scale)
    check("the projection yields a positive scale", upm > 0, str(upm))
    by_pt = {n: [p for r in rings for p in r] for _, n, rings in counties}

    def centre_view(nm):
        pts = by_pt[nm]
        return (sum(p[0] for p in pts) / len(pts) * scale + dx,
                sum(p[1] for p in pts) / len(pts) * scale + dy)

    # El Paso to Jefferson is the longest span the state offers, so it is where an equal-area
    # projection's distance error is largest. If the bar holds here it holds anywhere on the
    # sheet.
    a, b = centre_view("El Paso"), centre_view("Jefferson")
    measured = math.dist(a, b) / upm
    truth = great_circle_mi(-106.29, 31.77, -94.15, 29.88)
    err = abs(measured - truth) / truth
    check("a distance measured off the map with the scale bar is within 2 percent",
          err < 0.02, f"{measured:.0f} mi measured, {truth:.0f} mi true, {err * 100:.1f}% off")

    svg_full = render(lit={"Hood"})
    check("the sheet carries a neatline", 'class="frame"' in svg_full)
    n_ticks = svg_full.count('class="tick"')
    check("the graticule ticks whole degrees", n_ticks >= 8, f"{n_ticks} ticks")
    check("...and every tick is labelled",
          svg_full.count("°W") + svg_full.count("°N") == n_ticks,
          f"{n_ticks} ticks, {svg_full.count('°W') + svg_full.count('°N')} labels")
    bar_svg, miles = scale_bar(scale, dx, dy)
    check("the scale bar is a round number of miles", miles in SCALE_STEPS, str(miles))
    check("...and it fits inside the sheet",
          miles * upm <= (VIEW_W - 2 * MARGIN) * 0.28,
          f"{miles * upm:.0f} units")
    check("...and the largest round number that fits was chosen",
          all(bigger * upm > (VIEW_W - 2 * MARGIN) * 0.28
              for bigger in SCALE_STEPS if bigger > miles))
    check("the projection is named where a reader can find it",
          "Albers equal-area conic" in svg_full)

    # NOTHING ON THE SHEET OVERLAPS ANYTHING ELSE. The scale bar sat bottom left in its first
    # version and printed "200 miles" straight through the 26 degree parallel's label. Both
    # elements were individually correct and the sheet was unreadable in that corner, which is
    # what placing furniture by eye buys. Boxes are approximate, deliberately generous, and
    # measured in the same units the SVG is drawn in.
    def label_boxes(svg: str) -> list:
        boxes = []
        for m_lab in re.finditer(
                r'class="lab" x="([\d.]+)" y="([\d.]+)"([^>]*)>([^<]+)<', svg):
            lx, ly = float(m_lab.group(1)), float(m_lab.group(2))
            attrs, text = m_lab.group(3), m_lab.group(4)
            # 11px mono, so roughly 6.6 units per character, and about 12 units tall.
            w, h = len(text) * 6.6, 12.0
            # `text-anchor` centres HORIZONTALLY. Testing for the bare word "middle" also
            # matched `dominant-baseline="middle"`, which centres vertically, so every parallel
            # label was shifted half its width to the left and the collision this check exists
            # to find fell outside the box. A broken gate reports clean, which is worse than no
            # gate, so the attribute is matched in full.
            if 'text-anchor="middle"' in attrs:
                lx -= w / 2
            boxes.append((lx, ly - h * 0.8, lx + w, ly + h * 0.2, text))
        return boxes

    boxes = label_boxes(svg_full)
    check("every label on the sheet was found", len(boxes) >= 9, str(len(boxes)))
    clashes = []
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
                clashes.append(f"{a[4]!r} over {b[4]!r}")
    check("no two labels on the sheet overlap", not clashes, "; ".join(clashes[:3]))

    # And the bar's own rule must not run through a label either, which the text check alone
    # would miss because the bar is a line rather than a string.
    bar_line = re.search(r'class="scale" x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)"', svg_full)
    if bar_line:
        bx1, by, bx2 = (float(bar_line.group(i)) for i in (1, 2, 3))
        hit = [t for x1, y1, x2, y2, t in boxes
               if y1 - 2 <= by <= y2 + 2 and x1 < bx2 and bx1 < x2 and t != f"{miles} miles"]
        check("the scale bar's rule does not run through a label", not hit, str(hit))
    # The graticule is placed by root-finding rather than by guessing at the corner, so a tick
    # that landed outside the frame would mean the crossing search is broken.
    for m_tick in re.finditer(r'class="tick" x1="([\d.]+)" y1="([\d.]+)"', svg_full):
        tx, ty = float(m_tick.group(1)), float(m_tick.group(2))
        if not (MARGIN - 0.5 <= tx <= VIEW_W - MARGIN + 0.5
                and MARGIN - 0.5 <= ty <= VIEW_H - MARGIN + 0.5):
            check("every graticule tick sits on the neatline", False, f"{tx},{ty}")
            break
    else:
        check("every graticule tick sits on the neatline", True)

    if failures:
        print(f"\ntexas_map self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\ntexas_map self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--lit", default="", help="comma separated county names or FIPS")
    ap.add_argument("--from-docket", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        return self_test()

    lit = {s for s in a.lit.split(",") if s.strip()}
    if a.from_docket:
        lit |= lit_from_docket(REPO_ROOT / "ledger" / "docket.json")
    svg = render(lit=lit)
    if a.out:
        Path(a.out).write_text(svg, encoding="utf-8")
        print(f"wrote {a.out}  {len(svg.encode()) // 1024} KB  {len(lit)} lit")
    else:
        sys.stdout.write(svg)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                      # noqa: BLE001
        print(f"texas_map: broke: {exc}", file=sys.stderr)
        sys.exit(2)
