#!/usr/bin/env python3
"""compute.py — every numeral carousel no. 16 puts in front of a reader, and the geometry
that draws the one quantity this deck draws.

THE LAW THIS FILE EXISTS FOR. No numeral on a slide, in the caption or in the first comment is
ever typed by a person or produced by a language model. It is quoted from a source or it is
computed here, from the claims file, and it can be recomputed from the same inputs.

THIS DECK IS UNUSUALLY THIN ON ARITHMETIC AND THAT IS THE POINT. The record publishes five
import shares and two award figures and nothing else numeric. Every printed numeral in this deck
is therefore QUOTED. What is computed here is not a printed number at all, it is the AREA of the
five stipple fields on slide 1, which is the only place this deck turns a quantity into a
drawing.

Reads  out/2026-09-05/claims.json
Writes out/2026-09-05/computed.json
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

RUN = "2026-09-05"
ROOT = Path(__file__).resolve().parents[2]
CLAIMS = ROOT / "out" / RUN / "claims.json"
OUT = ROOT / "out" / RUN / "computed.json"


def claims_by_id() -> dict:
    return {c["id"]: c for c in json.loads(CLAIMS.read_text())["claims"]}


def main() -> int:
    C = claims_by_id()

    # ---- the five import shares, PARSED OUT OF THE QUOTE rather than retyped ---------------
    # c18's quote is the USGS import-sources line. Reading the figures out of the quote is what
    # makes it impossible for the numeral on the slide and the numeral in the claim to drift.
    # The document carries a superscript footnote on China which extracts as "China,8 71%", so
    # the pattern tolerates the marker rather than the quote being tidied to remove it.
    q18 = C["c18"]["quote"]
    pairs = re.findall(r"([A-Z][a-z]+),(?:\d+)?\s*(\d+)%", q18)
    other = re.search(r"other,\s*(\d+)%", q18)
    shares = [(name, int(pct)) for name, pct in pairs]
    if other:
        shares.append(("Other", int(other.group(1))))

    assert [n for n, _ in shares] == ["China", "Malaysia", "Japan", "Estonia", "Other"], shares
    assert [p for _, p in shares] == [71, 13, 5, 5, 6], shares

    # ---- slide 1 geometry, the only quantity this deck draws -------------------------------
    # Area is proportional to the share. A stipple field's visual weight is its area, so the
    # radius of each field goes as the square root, which is the whole reason this is computed
    # rather than eyeballed: a radius drawn proportional to the share would overstate China by
    # the square of its lead.
    #
    # THE LARGEST FIELD MUST EXCEED THE SUM OF THE OTHER FOUR, which is slide 1's own acceptance
    # item, and that is a property of the shares rather than of the drawing. Asserted here so
    # the acceptance item is checkable against this file rather than against an opinion.
    total = sum(p for _, p in shares)
    biggest = max(p for _, p in shares)
    assert biggest > (total - biggest), "the cover's premise fails on these shares"

    # A reference area in square design pixels for the 71 field, chosen so the field spans most
    # of the middle band at 1080 wide without touching the safe margins.
    REF_AREA_71 = 250_000.0
    unit = REF_AREA_71 / 71.0
    fields = []
    for name, pct in shares:
        area = unit * pct
        fields.append({
            "name": name,
            "pct": pct,
            "area_px2": round(area, 1),
            "equiv_radius_px": round(math.sqrt(area / math.pi), 2),
        })

    # Particle counts per field at one density, so the stipple is a measured population rather
    # than a look. Density is per 1000 square px.
    DENSITY_PER_KPX2 = 46.0
    for f in fields:
        f["particles"] = int(round(f["area_px2"] / 1000.0 * DENSITY_PER_KPX2))

    out = {
        "run": RUN,
        "note": (
            "Every printed numeral in this deck is quoted from a claim. Nothing here is printed. "
            "These are the areas and particle counts that draw the five import shares on slide 1."
        ),
        "shares_from_c18": shares,
        "slide1_fields": fields,
        "slide1_density_per_kpx2": DENSITY_PER_KPX2,
        "printed_numerals": {
            "71%": "c18", "13%": "c18", "5%": "c18", "6%": "c18",
            "$2.9 million": "c2", "$2.88 million": "c3",
            "three-year": "c2",
        },
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"computed.json: {len(fields)} field(s), largest {biggest}% "
          f"exceeds the other four combined at {total - biggest}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
