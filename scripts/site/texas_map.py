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
    pad = 18.0
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

    return (
        f'<svg class="txmap" viewBox="0 0 {VIEW_W:g} {VIEW_H:g}" role="img" '
        f'aria-labelledby="{idprefix}-t" preserveAspectRatio="xMidYMid meet">'
        f'<title id="{idprefix}-t">{title}. '
        f'{n_lit} of {len(counties)} counties carry an item.</title>'
        f'<g>{"".join(paths)}</g></svg>'
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
