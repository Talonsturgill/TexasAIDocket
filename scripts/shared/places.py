#!/usr/bin/env python3
"""places.py — the canonical Texas place record, and the resolver that reads it.

WHY THIS EXISTS
Texas is 30 million people across 254 counties, and at that volume entity drift is the failure
that quietly destroys the record: "City of Houston", "Houston" and "COH" becoming three
entities breaks every count, every facet and every per-metro filter at once, and it breaks them
silently.

So a place is not a string here. It is a record with a stable id, and everything that names a
location resolves to one before it is stored.

    places.py build            # rebuild assets/geo/tx-places.json from source geodata
    places.py resolve "Midland County"
    places.py --self-test

THE PROVENANCE RULE
Every field carries where it came from. A field this program did not compute or read from a
cited source is not written at all, because a plausible-looking county seat nobody checked is
worse than an absent one: the absence gets fixed, the guess gets cited. This is the same law
as CLAUDE.md's "numbers are computed, never generated," applied to facts about places.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLACES = REPO_ROOT / "assets" / "geo" / "tx-places.json"
COUNTIES_SRC = REPO_ROOT / "assets" / "geo" / "tx-counties.topo.json"

TX_FIPS = "48"

SOURCE_US_ATLAS = {
    "name": "us-atlas counties-10m",
    "url": "https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json",
    "license": "ISC",
    "derived_from": "US Census Bureau cartographic boundary files",
}


# --------------------------------------------------------------------------- topojson
def decode_arcs(topo: dict) -> list[list[tuple[float, float]]]:
    """TopoJSON stores arcs delta-encoded against a quantized grid. Undo both."""
    tr = topo.get("transform")
    out = []
    for arc in topo["arcs"]:
        pts, x, y = [], 0, 0
        for dx, dy in arc:
            x += dx
            y += dy
            if tr:
                pts.append((x * tr["scale"][0] + tr["translate"][0],
                            y * tr["scale"][1] + tr["translate"][1]))
            else:
                pts.append((float(x), float(y)))
        out.append(pts)
    return out


def ring_points(arc_ids: list[int], arcs: list[list[tuple[float, float]]]) -> list[tuple[float, float]]:
    """A ring is a list of arc indices; a negative index means traverse that arc backwards."""
    pts: list[tuple[float, float]] = []
    for idx in arc_ids:
        seg = arcs[~idx][::-1] if idx < 0 else arcs[idx]
        pts.extend(seg[1:] if pts else seg)
    return pts


def polygon_centroid(rings: list[list[tuple[float, float]]]) -> tuple[float, float, float]:
    """Area-weighted centroid over a polygon's rings, and its absolute area.

    Area weighting, not bounding-box centre: a bbox centre for a county with a long river
    boundary lands outside the county, and a pin outside its own county is the kind of error a
    reader spots instantly.
    """
    cx = cy = area2 = 0.0
    for ring in rings:
        if len(ring) < 3:
            continue
        a = 0.0
        rx = ry = 0.0
        for i in range(len(ring) - 1):
            x0, y0 = ring[i]
            x1, y1 = ring[i + 1]
            cross = x0 * y1 - x1 * y0
            a += cross
            rx += (x0 + x1) * cross
            ry += (y0 + y1) * cross
        if a == 0:
            continue
        area2 += a
        cx += rx
        cy += ry
    if area2 == 0:
        flat = [p for r in rings for p in r]
        if not flat:
            return 0.0, 0.0, 0.0
        return (sum(p[0] for p in flat) / len(flat),
                sum(p[1] for p in flat) / len(flat), 0.0)
    return cx / (3 * area2), cy / (3 * area2), abs(area2 / 2)


def geometry_rings(geom: dict, arcs) -> list[list[tuple[float, float]]]:
    if geom["type"] == "Polygon":
        return [ring_points(r, arcs) for r in geom["arcs"]]
    if geom["type"] == "MultiPolygon":
        return [ring_points(r, arcs) for poly in geom["arcs"] for r in poly]
    return []


# --------------------------------------------------------------------------- ids
def slugify(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s


def norm(text: str) -> str:
    """Normalize a user or scout string for matching: fold case, strip accents and
    punctuation, drop the noise words that make one place look like three."""
    s = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(
        r"\b(county|co|city of|town of|the|municipality|tx|texas|usa|united states)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# --------------------------------------------------------------------------- build
def build(src: Path, out: Path) -> int:
    if not src.exists():
        print(f"places: source geodata missing at {src}\n"
              f"  fetch it once with:\n"
              f"  curl -sSL -o /tmp/counties-10m.json {SOURCE_US_ATLAS['url']}\n"
              f"  then run: places.py build --from /tmp/counties-10m.json", file=sys.stderr)
        return 2

    topo = json.loads(src.read_text(encoding="utf-8"))
    arcs = decode_arcs(topo)

    counties = []
    for geom in topo["objects"]["counties"]["geometries"]:
        fips = str(geom.get("id", ""))
        if not fips.startswith(TX_FIPS) or len(fips) != 5:
            continue
        name = geom.get("properties", {}).get("name", "").strip()
        rings = geometry_rings(geom, arcs)
        lon, lat, area = polygon_centroid(rings)
        counties.append({
            "id": f"county-{slugify(name)}",
            "kind": "county",
            "name": name,
            "full_name": f"{name} County",
            "fips": fips,
            "lon": round(lon, 5),
            "lat": round(lat, 5),
            "_area_deg2": area,
            "aliases": sorted({norm(name), norm(f"{name} County"), fips}),
            "provenance": {
                "name": "us-atlas",
                "fips": "us-atlas",
                "lon": "computed:area-weighted-centroid",
                "lat": "computed:area-weighted-centroid",
            },
        })

    counties.sort(key=lambda c: c["name"])
    for c in counties:
        c.pop("_area_deg2", None)

    doc = {
        "_spec": {
            "purpose": (
                "The canonical Texas place record. Every location string stored anywhere in "
                "this project resolves to an id in here before it is written, so that counts, "
                "facets and per-metro filters cannot silently fracture across spellings."),
            "id_rule": (
                "Stable forever. An id is never reused and never renamed; a place that changes "
                "name gains an alias and keeps its id."),
            "provenance_rule": (
                "Every field records where it came from. A field that was neither computed "
                "here nor read from a cited source is NOT WRITTEN. A plausible county seat "
                "nobody checked is worse than an absent one, because the absence gets fixed "
                "and the guess gets cited."),
            "pending": (
                "county_seat, population, ERCOT weather zone, ERCOT load zone, MSA and "
                "physiographic region are NOT yet populated. Each needs a cited source. The "
                "self-test fails if any of them is ever written without provenance."),
            "record_schema": {
                "id": "stable slug, e.g. county-midland",
                "kind": "county | city | metro | region | zone",
                "name": "display name",
                "fips": "5-digit county FIPS, counties only",
                "lon/lat": "area-weighted centroid, computed",
                "aliases": "normalized strings that resolve to this record",
                "provenance": "field name -> source",
            },
        },
        "sources": [SOURCE_US_ATLAS],
        "generated_by": "scripts/shared/places.py build",
        "counts": {"county": len(counties)},
        "places": counties,
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"places: wrote {len(counties)} counties -> {out.relative_to(REPO_ROOT)}")
    if len(counties) != 254:
        print(f"  WARNING: expected 254 Texas counties, got {len(counties)}", file=sys.stderr)
        return 1
    return 0


# --------------------------------------------------------------------------- resolve
class Resolver:
    def __init__(self, doc: dict):
        self.places = doc["places"]
        self.by_id = {p["id"]: p for p in self.places}
        self.index: dict[str, list[dict]] = {}
        for p in self.places:
            for alias in p.get("aliases", []):
                self.index.setdefault(alias, []).append(p)

    @classmethod
    def load(cls, path: Path = PLACES) -> "Resolver":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def resolve(self, text: str) -> dict | None:
        """Exact-after-normalization only. No fuzzy matching.

        Deliberate: a fuzzy resolver that maps 'Deaf Smith' to 'Smith' is worse than no
        resolver, because it fails silently and the record looks fine. An unresolved string is
        a visible problem someone fixes; a wrongly resolved one is a lie in the data.
        """
        key = norm(text)
        if not key:
            return None
        hits = self.index.get(key)
        if hits and len(hits) == 1:
            return hits[0]
        if hits:
            return None                      # ambiguous: refuse rather than pick
        return None

    def candidates(self, text: str, limit: int = 5) -> list[dict]:
        """Suggestions for an unresolved string, to make the failure actionable."""
        key = norm(text)
        if not key:
            return []
        out = [p for a, ps in self.index.items() if key and key in a for p in ps]
        seen, uniq = set(), []
        for p in out:
            if p["id"] not in seen:
                seen.add(p["id"])
                uniq.append(p)
        return uniq[:limit]


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    failures = 0

    def check(label: str, got, want):
        nonlocal failures
        ok = got == want
        print(f"  {'ok  ' if ok else 'FAIL'}  {label}")
        if not ok:
            failures += 1
            print(f"        got {got!r} want {want!r}", file=sys.stderr)

    # Normalization is the whole defense against entity drift, so test it hardest.
    check("norm folds 'City of Houston'", norm("City of Houston"), "houston")
    check("norm folds 'HOUSTON, TX'", norm("HOUSTON, TX"), "houston")
    check("norm folds 'Harris County'", norm("Harris County"), "harris")
    check("norm folds 'Harris Co.'", norm("Harris Co."), "harris")
    check("norm keeps multiword names", norm("Deaf Smith County"), "deaf smith")
    check("norm strips accents", norm("Bexar Countý"), "bexar")
    check("slugify", slugify("Deaf Smith"), "deaf-smith")

    # Centroid maths against a unit square, where the answer is known by construction.
    sq = [[(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0), (0.0, 0.0)]]
    cx, cy, area = polygon_centroid(sq)
    check("centroid of a 2x2 square, x", round(cx, 6), 1.0)
    check("centroid of a 2x2 square, y", round(cy, 6), 1.0)
    check("area of a 2x2 square", round(area, 6), 4.0)

    if not PLACES.exists():
        print("  SKIP  place file not built yet, run: places.py build")
        return 1 if failures else 0

    doc = json.loads(PLACES.read_text(encoding="utf-8"))
    r = Resolver(doc)
    check("254 Texas counties", doc["counts"]["county"], 254)

    # Every county must resolve from its bare name and its 'X County' form.
    unresolved = [p["name"] for p in r.places
                  if r.resolve(p["name"]) is None or r.resolve(p["full_name"]) is None]
    check("every county resolves both ways", unresolved[:5], [])

    # Ids must be unique and stable-looking.
    ids = [p["id"] for p in r.places]
    check("ids are unique", len(ids), len(set(ids)))

    # Centroids must actually be inside Texas. A pin in the wrong state is the error a reader
    # spots instantly, and it is exactly what a bbox centre would produce for a river county.
    outside = [p["name"] for p in r.places
               if not (-107.0 <= p["lon"] <= -93.0 and 25.0 <= p["lat"] <= 37.0)]
    check("every centroid falls inside Texas", outside[:5], [])

    # THE PROVENANCE LAW: no field may exist without a recorded source.
    unsourced = []
    for p in r.places:
        prov = p.get("provenance", {})
        for field in p:
            if field in ("id", "kind", "aliases", "provenance", "full_name"):
                continue
            if field not in prov:
                unsourced.append(f"{p['id']}.{field}")
    check("no field lacks provenance", unsourced[:5], [])

    # The resolver must REFUSE rather than guess.
    check("refuses an unknown place", r.resolve("Nowhere Parish"), None)
    check("refuses empty input", r.resolve(""), None)
    got = r.resolve("Midland County")
    check("resolves a real county", got["id"] if got else None, "county-midland")
    check("resolves by FIPS", (r.resolve("48329") or {}).get("name"), "Midland")

    if failures:
        print(f"\nplaces self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\nplaces self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    b = sub.add_parser("build")
    b.add_argument("--from", dest="src", default=str(COUNTIES_SRC))
    b.add_argument("--out", default=str(PLACES))
    rs = sub.add_parser("resolve")
    rs.add_argument("text", nargs="+")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if args.cmd == "build":
        return build(Path(args.src), Path(args.out))
    if args.cmd == "resolve":
        r = Resolver.load()
        text = " ".join(args.text)
        hit = r.resolve(text)
        if hit:
            print(json.dumps(hit, indent=1, ensure_ascii=False))
            return 0
        print(f"unresolved: {text!r}", file=sys.stderr)
        cands = r.candidates(text)
        if cands:
            print("  did you mean: " + ", ".join(c["full_name"] for c in cands),
                  file=sys.stderr)
        return 1
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
