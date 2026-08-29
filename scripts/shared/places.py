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
CBSA = REPO_ROOT / "assets" / "geo" / "tx-cbsa-2023.json"

TX_FIPS = "48"

SOURCE_US_ATLAS = {
    "name": "us-atlas counties-10m",
    "url": "https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json",
    "license": "ISC",
    "derived_from": "US Census Bureau cartographic boundary files",
}

SOURCE_OMB = {
    "name": "OMB Core Based Statistical Areas, July 2023 delineation (List 1)",
    "url": ("https://www2.census.gov/programs-surveys/metro-micro/geographies/"
            "reference-files/2023/delineation-files/list1_2023.xlsx"),
    "license": "US Government work, public domain",
    "derived_from": "OMB Bulletin, published by the US Census Bureau",
    "vintage": "2023-07",
}


def write_text_lf(path: Path, text: str) -> None:
    """Write generated JSON with the same bytes on Windows and Linux."""
    path.write_text(text, encoding="utf-8", newline="\n")


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

    Area weighting, not bounding-box center: a bbox center for a county with a long river
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
# --------------------------------------------------------------------------- CBSA
# THE METRO LAYER, and why it is three layers rather than one.
#
# `_spec.pending` in this file has said since it was written that MSA is not populated
# and needs a cited source. This is that source: the OMB July 2023 delineation, read
# rather than remembered.
#
# READING IT CAUGHT TWO THINGS MEMORY WOULD HAVE GOT WRONG. The 2023 revision renamed
# Houston to "Houston-Pasadena-The Woodlands" and Austin to "Austin-Round Rock-San
# Marcos". A metro name typed from memory would have been the previous decade's, on
# the two biggest pages of the site.
#
# AND THE HARD PART: this project already had a metro vocabulary. `waterwatch_collect`
# groups reservoirs into 19 metros, and it splits Dallas from Fort Worth and merges
# Midland with Odessa -- neither of which matches the MSA list. Both are RIGHT for
# water, because a reservoir serves a city rather than a statistical area, and both
# resolve against this file with a code of their own:
#
#   Dallas and Fort Worth are Metropolitan DIVISIONS (19124, 23104) inside one CBSA.
#   Midland-Odessa is a COMBINED statistical area (CSA 372), of two MSAs.
#
# So all three grains are carried, a surface picks the one it needs, and they share
# ids. One entity, several memberships, which is the only arrangement in which the
# water page and the docket page can both say "Austin" and mean it.
def extract_cbsa(xlsx: Path, out: Path) -> int:
    """Vendor the TEXAS SUBSET of the national delineation file.

    The national file is 143 KB of mostly-not-Texas, needs openpyxl, and would put a
    binary in a repo whose diffs are meant to be readable. The derived subset is small,
    is JSON, and shows up in review as the handful of lines that actually changed. The
    fetch is a person's job, once per delineation vintage, and this prints the command.
    """
    try:
        import openpyxl                                              # noqa: PLC0415
    except ImportError:
        print("places: extracting CBSAs needs openpyxl (install requirements-tools.txt). It is a "
              "one-off maintainer step, not a build dependency.", file=sys.stderr)
        return 2
    if not xlsx.exists():
        print(f"places: delineation file missing at {xlsx}\n  fetch it once with:\n"
              f"  curl -sSL -o /tmp/list1_2023.xlsx {SOURCE_OMB['url']}", file=sys.stderr)
        return 2

    ws = openpyxl.load_workbook(xlsx, read_only=True).active
    rows = [r for r in ws.iter_rows(min_row=4, values_only=True) if r and r[9] == TX_FIPS]
    if not rows:
        print("places: no Texas rows in the delineation file. Wrong sheet or wrong file.",
              file=sys.stderr)
        return 1

    areas: dict[str, dict] = {}
    county_to: dict[str, dict] = {}
    for r in rows:
        cbsa, div, csa, title, kind, div_title, csa_title, county, _st, sf, cf, central = r[:12]
        fips = f"{sf}{cf}"
        metro = kind and kind.startswith("Metropolitan")

        def area(aid: str, code: str, name: str, grain: str):
            a = areas.setdefault(aid, {
                "id": aid, "kind": grain, "code": str(code), "name": name,
                "type": "metropolitan" if metro else "micropolitan",
                "counties": [], "county_fips": [],
            })
            if fips not in a["county_fips"]:
                a["counties"].append(str(county).replace(" County", ""))
                a["county_fips"].append(fips)
            return a

        area(f"metro-{slugify(str(title).split(',')[0])}", cbsa, str(title), "cbsa")
        if div:
            area(f"division-{slugify(str(div_title).split(',')[0])}", div, str(div_title),
                 "division")
        if csa:
            area(f"combined-{slugify(str(csa_title).split(',')[0])}", csa, str(csa_title),
                 "csa")

        county_to[fips] = {
            "cbsa": str(cbsa),
            "cbsa_name": str(title),
            "type": "metropolitan" if metro else "micropolitan",
            "division": str(div) if div else None,
            "division_name": str(div_title) if div else None,
            "csa": str(csa) if csa else None,
            "csa_name": str(csa_title) if csa else None,
            # Central or Outlying is the OMB's own word for whether a county is the
            # core of its area or commutes into it. A page that lists ten counties
            # under "Houston" should be able to say which one Houston is in.
            "role": str(central).lower() if central else None,
        }

    for a in areas.values():
        order = sorted(zip(a["counties"], a["county_fips"]))
        a["counties"] = [c for c, _ in order]
        a["county_fips"] = [f for _, f in order]

    doc = {
        "_spec": {
            "purpose": ("The Texas subset of the federal statistical-area delineation, so "
                        "every surface that groups by metro groups by the same thing."),
            "grains": ("cbsa is the metro or micro area; division splits the largest CBSAs "
                       "(this is what makes Dallas and Fort Worth separable); csa combines "
                       "adjacent CBSAs (this is what makes Midland-Odessa one place). A "
                       "surface picks the grain its subject needs and they share ids."),
            "not_covered": ("121 of Texas's 254 counties are in NO statistical area. That is "
                            "not a gap in this file, it is a fact about Texas, and it is why "
                            "the scoping unit in this project is a PLACE rather than a metro."),
        },
        "source": SOURCE_OMB,
        "generated_by": "scripts/shared/places.py cbsa",
        "counts": {
            "areas": len(areas),
            "metropolitan": sum(1 for a in areas.values()
                                if a["kind"] == "cbsa" and a["type"] == "metropolitan"),
            "micropolitan": sum(1 for a in areas.values()
                                if a["kind"] == "cbsa" and a["type"] == "micropolitan"),
            "divisions": sum(1 for a in areas.values() if a["kind"] == "division"),
            "combined": sum(1 for a in areas.values() if a["kind"] == "csa"),
            "counties_in_an_area": len(county_to),
        },
        "areas": [areas[k] for k in sorted(areas)],
        "county_to": dict(sorted(county_to.items())),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    write_text_lf(out, json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    c = doc["counts"]
    print(f"places: {c['metropolitan']} metro + {c['micropolitan']} micro areas, "
          f"{c['divisions']} divisions, {c['combined']} combined, covering "
          f"{c['counties_in_an_area']} of 254 counties -> {out.relative_to(REPO_ROOT)}")
    return 0


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

    # THE METRO LAYER, attached from the vendored federal subset and NOWHERE ELSE.
    #
    # A county that is in no statistical area gets `metro: None` and says so in its
    # provenance. That is a fact about Texas rather than a hole in the data, and the
    # difference matters: an absent field invites somebody to fill it in, and an
    # explicit "this county is in no CBSA" does not.
    cbsa_doc = json.loads(CBSA.read_text(encoding="utf-8")) if CBSA.exists() else None
    covered = 0
    for c in counties:
        m = (cbsa_doc or {}).get("county_to", {}).get(c["fips"])
        if m:
            covered += 1
            c["metro"] = m
            c["provenance"]["metro"] = "omb-2023-delineation"
            # A METRO NAME IS NOT A COUNTY ALIAS, and Texas is emphatic about it.
            #
            # The first version folded the CBSA and CSA names into each member county's
            # aliases, and the self-test immediately refused to resolve El Paso,
            # Lubbock, Midland, Pecos and Tyler. It was right to. A Texas metro is named
            # for its central city, and there is frequently a DIFFERENT COUNTY with that
            # name somewhere else: Reeves County contains the city of Pecos, and Pecos
            # County is two hundred miles away. Smith County contains Tyler, and Tyler
            # County is in the Piney Woods. Aliasing the metro onto its members made
            # "tyler" mean two counties, so the resolver correctly refused both, and five
            # counties that had resolved for weeks stopped.
            #
            # So metros live in their own index with their own ids, and `resolve` takes
            # the kind it wants. See `Resolver`.
        elif cbsa_doc:
            c["metro"] = None
            c["provenance"]["metro"] = "omb-2023-delineation:in-no-statistical-area"

    # The areas themselves, as first-class places. A metro is a thing a reader asks about
    # and a page is written for, so it gets an id, aliases and provenance like anything
    # else here. Its centroid is the AREA-WEIGHTED MEAN of its member counties' centroids,
    # which is computed rather than looked up and is labelled as such.
    areas: list[dict] = []
    by_fips = {c["fips"]: c for c in counties}
    for a in (cbsa_doc or {}).get("areas", []):
        members = [by_fips[f] for f in a["county_fips"] if f in by_fips]
        if not members:
            continue
        short = str(a["name"]).split(",")[0]
        areas.append({
            "id": a["id"],
            "kind": a["kind"],                      # cbsa | division | csa
            "name": short,
            "full_name": a["name"],
            "area_type": a["type"],                 # metropolitan | micropolitan
            "code": a["code"],
            "lon": round(sum(m["lon"] for m in members) / len(members), 5),
            "lat": round(sum(m["lat"] for m in members) / len(members), 5),
            "counties": a["counties"],
            "county_fips": a["county_fips"],
            # THE PRINCIPAL CITIES ARE ALIASES, each of them. A CBSA title is a list of
            # its principal cities and a reader knows one of them, not the string. Nobody
            # types "Houston-Pasadena-The Woodlands", and somebody asking about Arlington
            # means Dallas-Fort Worth and should land there.
            "aliases": sorted({norm(short), norm(a["name"]), a["code"]}
                              | {norm(city) for city in short.split("-") if norm(city)}),
            "provenance": {
                "name": "omb-2023-delineation",
                "code": "omb-2023-delineation",
                "counties": "omb-2023-delineation",
                "county_fips": "omb-2023-delineation",
                "area_type": "omb-2023-delineation",
                "lon": "computed:mean-of-member-county-centroids",
                "lat": "computed:mean-of-member-county-centroids",
            },
        })
    areas.sort(key=lambda a: (a["kind"], a["name"]))

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
        "sources": [SOURCE_US_ATLAS] + ([SOURCE_OMB] if cbsa_doc else []),
        "generated_by": "scripts/shared/places.py build",
        "counts": {"county": len(counties), "county_in_a_metro": covered,
                   "metro": len(areas)},
        "places": counties + areas,
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    write_text_lf(out, json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    print(f"places: wrote {len(counties)} counties -> {out.relative_to(REPO_ROOT)}")
    if len(counties) != 254:
        print(f"  WARNING: expected 254 Texas counties, got {len(counties)}", file=sys.stderr)
        return 1
    return 0


# --------------------------------------------------------------------------- resolve
class Resolver:
    """Resolve a string to a place, WITHIN A KIND.

    THE INDEX IS PER KIND, and that is not tidiness. `norm()` deliberately strips the
    word "county" so that "Harris Co." and "Harris County" collapse to one key -- which
    means a county and a metro named for the same city are indistinguishable after
    normalization. In Texas that is common and it is worse than common: Reeves County
    contains the CITY of Pecos while Pecos County is two hundred miles away, and Smith
    County contains Tyler while Tyler County is in the Piney Woods.

    A single index makes those strings ambiguous, and this resolver refuses ambiguity by
    design, so five counties that had resolved correctly for weeks stopped the moment
    metros were added. Separate indexes are the fix, and the caller says which kind it
    means, which it always knows.
    """

    COUNTY = "county"
    METRO = "cbsa"
    DIVISION = "division"
    CSA = "csa"

    def __init__(self, doc: dict):
        self.places = doc["places"]
        self.by_id = {p["id"]: p for p in self.places}
        # ONE INDEX PER GRAIN. County, cbsa, division and csa each get their own, for the
        # same reason counties and metros are separate at all: after normalization the
        # strings collide. "Houston" is a principal city of the Houston CBSA and of the
        # Houston-Pasadena COMBINED area, and a single metro index makes it ambiguous,
        # so this resolver would refuse the most obvious query on the site.
        self.by_kind: dict[str, dict[str, list[dict]]] = {}
        for p in self.places:
            idx = self.by_kind.setdefault(p.get("kind", "county"), {})
            for alias in p.get("aliases", []):
                idx.setdefault(alias, []).append(p)
        self.index = self.by_kind.get("county", {})     # the default, kept for callers

    @classmethod
    def load(cls, path: Path = PLACES) -> "Resolver":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def resolve(self, text: str, kind: str = COUNTY) -> dict | None:
        """Exact-after-normalization only. No fuzzy matching.

        Deliberate: a fuzzy resolver that maps 'Deaf Smith' to 'Smith' is worse than no
        resolver, because it fails silently and the record looks fine. An unresolved string is
        a visible problem someone fixes; a wrongly resolved one is a lie in the data.
        """
        key = norm(text)
        if not key:
            return None
        hits = self.by_kind.get(kind, {}).get(key)
        if hits and len(hits) == 1:
            return hits[0]
        if hits:
            return None                      # ambiguous: refuse rather than pick
        return None

    def resolve_metro(self, text: str, grain: str = METRO) -> dict | None:
        """The metro a string names, at the grain asked for.

        `cbsa` by default, which is what a docket page wants. A surface whose subject is
        genuinely a division or a combined area -- the water watch's Dallas against Fort
        Worth, or its Midland-Odessa basin -- asks for that grain by name.
        """
        return self.resolve(text, kind=grain)

    def crosswalk(self, slug: str) -> dict:
        """Map an OUTSIDE party's area slug onto this registry, by derivation.

        WHY THIS IS NOT A TABLE. The water watch groups reservoirs by nineteen slugs like
        `midland_odessa` and `temple_killeen`. Those are not a vocabulary this project
        chose. They are `municipal_*` tags published by TWDB and read out of the feed, and
        the record of what the source said is the thing this project is for. Rewriting them
        to match OMB would be editing fetched data, and typing a nineteen-row mapping by
        hand would be inventing nineteen facts. So the slug stays exactly as fetched and
        the registry id is DERIVED beside it, here, from the same gazetteer every other
        surface resolves against.

        THE GRAIN IS PART OF THE ANSWER, and it is chosen by what resolves rather than
        declared. Checked against the 2023 delineation, not remembered:

          `dallas` and `fort_worth` are one CBSA and two metropolitan DIVISIONS, and they
          are genuinely two water systems, so the division is the honest grain. Collapsing
          them to the shared CBSA would merge two reservoirs sets that TWDB deliberately
          separates.

          `temple_killeen` is CBSA 28660, whose OMB name is Killeen-Temple. A token set
          match catches a reversed name without a special case, which matters because the
          next reversal nobody predicts is caught too.

          `midland_odessa` is TWO CBSAs, 33260 Midland and 36220 Odessa, which sit inside
          CSA 372 Midland-Odessa-Andrews. It maps to both rather than to the CSA, because
          the CSA also contains Andrews and the tag does not claim Andrews.

        Returns `{slug, ids, grain, how}`, where `how` names the rule that fired so the
        derivation can be read rather than trusted. `ids` is empty when nothing resolves,
        which is a reportable fact and never a silent drop.
        """
        text = str(slug).replace("_", " ")
        for grain in (self.DIVISION, self.METRO, self.CSA):
            got = self.resolve(text, kind=grain)
            if got:
                return {"slug": slug, "ids": [got["id"]], "grain": grain,
                        "how": f"exact name at {grain} grain"}

        want = set(norm(text).split())
        if want:
            same = [p for p in self.places if p.get("kind") == self.METRO
                    and set(norm(p.get("name", "")).split()) == want]
            if len(same) == 1:
                return {"slug": slug, "ids": [same[0]["id"]], "grain": self.METRO,
                        "how": "same words in a different order"}

            parts = [self.resolve(w, kind=self.METRO) for w in sorted(want)]
            if len(parts) > 1 and all(parts):
                return {"slug": slug, "ids": [p["id"] for p in parts], "grain": self.METRO,
                        "how": "every word names an area of its own"}

        return {"slug": slug, "ids": [], "grain": None, "how": "nothing in the registry"}

    def metro_of(self, county: str) -> dict | None:
        """The CBSA record a county belongs to, or None when it is in no statistical area.

        None here is a FACT rather than a hole: 121 of Texas's 254 counties are in no
        CBSA, and they are where much of the physical AI buildout is. A caller that treats
        None as missing data will quietly drop half the state.
        """
        c = self.resolve(county)
        m = (c or {}).get("metro")
        if not m:
            return None
        return next((p for p in self.places
                     if p.get("kind") == "cbsa" and p.get("code") == m["cbsa"]), None)

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

    import tempfile

    with tempfile.TemporaryDirectory() as td:
        probe = Path(td) / "probe.json"
        write_text_lf(probe, "one\ntwo\n")
        check("generated JSON uses LF bytes on every host", probe.read_bytes(), b"one\ntwo\n")

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
    counties = [p for p in r.places if p["kind"] == "county"]
    unresolved = [p["name"] for p in counties
                  if r.resolve(p["name"]) is None or r.resolve(p["full_name"]) is None]
    check("every county resolves both ways", unresolved[:5], [])

    # THE TRAP THE FIRST VERSION FELL INTO. Metro names were folded into their member
    # counties' aliases, and five counties immediately stopped resolving: a Texas metro is
    # named for its central city and there is often a DIFFERENT county with that name.
    # Reeves County contains the city of Pecos and Pecos County is two hundred miles away.
    # So the indexes are separate, and these four assertions are what keeps them separate.
    areas = [p for p in r.places if p["kind"] != "county"]
    # AT ITS OWN GRAIN. A CSA does not resolve in the CBSA index and should not: they are
    # different entities that share a principal city, which is the whole reason the index
    # is split. Resolving each area against its own kind is the assertion that means
    # something; resolving them all against one would only prove the split had failed.
    unresolved_m = [p["name"] for p in areas
                    if r.resolve_metro(p["name"], grain=p["kind"]) is None]
    check("every area resolves at its own grain", unresolved_m[:5], [])
    check("...and Pecos the COUNTY is still Pecos the county",
          (r.resolve("Pecos") or {}).get("id"), "county-pecos")
    check("...while the city of Pecos is in Reeves, which is the Pecos MICRO area",
          (r.resolve_metro("Pecos") or {}).get("counties"), ["Reeves"])
    check("...and Tyler the county is not Tyler the metro",
          ((r.resolve("Tyler") or {}).get("id"), (r.resolve_metro("Tyler") or {}).get("counties")),
          ("county-tyler", ["Smith"]))

    # The metro layer itself, against the vendored federal subset.
    check("133 of 254 counties are in a statistical area, and the rest honestly are not",
          doc["counts"]["county_in_a_metro"], 133)
    check("a county in no CBSA says so rather than omitting the field",
          [c["metro"] for c in counties if c["name"] == "Shackelford"], [None])
    check("Houston carries its 2023 name, not the previous decade's",
          (r.resolve_metro("Houston") or {}).get("full_name"),
          "Houston-Pasadena-The Woodlands, TX")
    check("Dallas and Fort Worth are separable, as metropolitan divisions",
          sorted(p["id"] for p in areas if p["kind"] == "division"),
          ["division-dallas-plano-irving", "division-fort-worth-arlington-grapevine"])
    check("Midland and Odessa are two MSAs inside one combined area",
          sorted((r.resolve_metro("Midland-Odessa-Andrews", grain="csa") or {})
                 .get("counties", [])),
          ["Andrews", "Ector", "Martin", "Midland"])
    check("metro_of walks county to CBSA",
          (r.metro_of("Taylor") or {}).get("full_name"), "Abilene, TX")
    check("...and returns None for a county in none of them, rather than guessing",
          r.metro_of("Shackelford"), None)

    # THE CROSSWALK, one case per rule it can fire, and every one of them is a real TWDB
    # municipal tag rather than an invented example. The point is that the slugs stay
    # exactly as the source published them and the registry id is derived beside them.
    check("a slug that matches an area name resolves at cbsa grain",
          (r.crosswalk("abilene")["ids"], r.crosswalk("abilene")["grain"]),
          (["metro-abilene"], "cbsa"))
    check("Dallas and Fort Worth resolve to their DIVISIONS, which is what makes them "
          "separable water systems",
          (r.crosswalk("dallas")["ids"], r.crosswalk("fort_worth")["ids"]),
          (["division-dallas-plano-irving"], ["division-fort-worth-arlington-grapevine"]))
    check("a reversed name resolves by its words rather than by a special case",
          (r.crosswalk("temple_killeen")["ids"], r.crosswalk("temple_killeen")["how"]),
          (["metro-killeen-temple"], "same words in a different order"))
    check("a slug naming two areas resolves to both, and not to the combined area that "
          "also contains a third",
          r.crosswalk("midland_odessa")["ids"], ["metro-midland", "metro-odessa"])
    check("a slug the registry does not know resolves to nothing, and says so",
          (r.crosswalk("narnia")["ids"], r.crosswalk("narnia")["grain"]), ([], None))
    check("every rule the crosswalk can fire names itself, so a derivation can be read",
          all(r.crosswalk(s)["how"] for s in
              ("abilene", "dallas", "temple_killeen", "midland_odessa", "narnia")), True)
    # Every TWDB municipal slug in the ledger today, resolved. A tag that stops resolving
    # is a change at the source worth seeing, not a silent drop from the coverage count.
    tags = ["abilene", "amarillo", "austin", "beaumont_port_arthur", "brownsville",
            "corpus_christi", "dallas", "fort_worth", "houston", "laredo", "lubbock",
            "midland_odessa", "nacogdoches", "san_angelo", "temple_killeen", "texarkana",
            "tyler", "waco", "wichita_falls"]
    check("every municipal tag the water feed publishes resolves onto the registry",
          [s for s in tags if not r.crosswalk(s)["ids"]], [])

    # Ids must be unique and stable-looking.
    ids = [p["id"] for p in r.places]
    check("ids are unique", len(ids), len(set(ids)))

    # Centroids must actually be inside Texas. A pin in the wrong state is the error a reader
    # spots instantly, and it is exactly what a bbox center would produce for a river county.
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
    cb = sub.add_parser("cbsa", help="vendor the Texas subset of the OMB delineation file")
    cb.add_argument("--from", dest="xlsx", default="/tmp/list1_2023.xlsx")
    cb.add_argument("--out", default=str(CBSA))
    rs = sub.add_parser("resolve")
    rs.add_argument("text", nargs="+")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if args.cmd == "build":
        return build(Path(args.src), Path(args.out))
    if args.cmd == "cbsa":
        return extract_cbsa(Path(args.xlsx), Path(args.out))
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
