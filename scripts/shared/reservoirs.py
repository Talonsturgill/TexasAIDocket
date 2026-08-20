#!/usr/bin/env python3
"""reservoirs.py — where each Texas reservoir actually is, committed once and never guessed.

WHY THIS FILE EXISTS AT ALL

The water watch ledger is a TIME SERIES. Every line is one day of storage and capacity per
reservoir, and that is exactly what a daily record should hold. What it deliberately does not
hold is the one fact about a reservoir that never changes from one day to the next, which is
where it sits on the ground. Writing a gauge's latitude into 119 records a day, forever, would
be storing a constant in a series and paying for it every morning.

So the geography is lifted out and committed once, on the same pattern `tx-places.json` already
uses here: a derived asset with a build step, checked rather than trusted.

THE SOURCE IS OUR OWN ARCHIVE, WHICH IS THE POINT

TWDB publishes `gauge_location` beside every reservoir in the same payload the collector already
fetches, and `waterwatch_collect` already writes that payload to `ledger/gridwatch/raw` verbatim
before parsing a single field out of it. So this needs no new request to anybody: it reads the
archive this project already keeps. One fetch a day stays one fetch a day.

WHY THE BUILD MERGES RATHER THAN REPLACES

`places.py build` can rebuild from zero because its source is a committed atlas that will still
be there in a year. This source is a directory of dated snapshots, and a snapshot directory is
the kind of thing somebody eventually prunes. A build that replaces would then quietly drop
every reservoir whose only payload had aged out, and the map would lose pins for a reason that
has nothing to do with water.

So the build is a UNION of what is committed and what the payloads say, and the CI check is
IDEMPOTENCE rather than reproduction from zero: rebuild, and require that nothing changed. That
catches the two failures that matter, a hand-edited coordinate and a source that has started
saying something new, and it survives the archive being thinned.

A COORDINATE THAT CHANGES IS AN ERROR, NOT AN UPDATE. A gauge does not move. If the source
returns a different position for a reservoir already on file, the build fails and says so
rather than picking one, because "which of these two is right" is not a question a build step
gets to answer on its own.

    reservoirs.py --self-test
    reservoirs.py build
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW = REPO_ROOT / "ledger" / "gridwatch" / "raw"
ASSET = REPO_ROOT / "assets" / "geo" / "tx-reservoirs.json"

# Texas, generously bounded. This is a SANITY RAIL rather than a definition: it exists so a
# coordinate that lands in the Atlantic fails the self-test instead of drawing a pin off the
# side of the map. The real question of whether a reservoir is in Texas is answered by TWDB's
# own `texas` tag, which is how Elephant Butte is caught.
TX_BBOX = (-107.0, 25.5, -93.0, 36.8)

# Five decimals is about a metre. The map this feeds is a thousand units across a state a
# thousand miles wide, so one unit is well over a kilometre and four decimals would do. Five
# costs nothing and leaves the file useful for something other than this map.
PRECISION = 5


def _spec(rec: dict) -> dict | None:
    """One reservoir's permanent facts, or None when the payload carries no usable position."""
    g = (rec.get("gauge_location") or {}).get("coordinates")
    if not g or len(g) != 2:
        return None
    try:
        lon, lat = float(g[0]), float(g[1])
    except (TypeError, ValueError):
        return None
    return {
        # The FULL NAME is a label and never a figure. It is here so a pin can announce "Lake
        # Abilene" rather than the payload's own key, which is a slug with the spaces taken out.
        "name": str(rec.get("full_name") or rec.get("short_name") or "").strip(),
        "lon": round(lon, PRECISION),
        "lat": round(lat, PRECISION),
        # TWDB'S OWN TAG, carried rather than inferred. It is the single field that keeps
        # Elephant Butte Lake out of a Texas water total, and the collector already trusts it
        # for exactly that. Two places reading one tag beats two places guessing.
        "texas": "texas" in (rec.get("tags") or []),
    }


def from_payloads(paths: list[Path] | None = None) -> dict[str, dict]:
    """Every reservoir position the raw archive knows, keyed by the payload's own name."""
    found: dict[str, dict] = {}
    for p in sorted(paths if paths is not None else RAW.glob("*-water.json.gz")):
        try:
            with gzip.open(p, "rb") as fh:
                doc = json.loads(fh.read().decode("utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(doc, dict):
            continue
        for key, rec in doc.items():
            if not isinstance(rec, dict):
                continue
            spec = _spec(rec)
            if spec:
                found[key] = spec
    return found


def load(path: Path = ASSET) -> dict[str, dict]:
    """The committed positions, or {} when the asset is absent.

    RETURNS {} RATHER THAN RAISING, because a missing asset must cost the map and nothing else.
    The water page's job is the numbers, and a page that refuses to render its figures because a
    drawing has no coordinates has traded the thing a reader came for against decoration.
    """
    if not path.exists():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return {}
    return doc.get("reservoirs") or {}


def merge(committed: dict[str, dict], found: dict[str, dict]) -> tuple[dict[str, dict], list[str]]:
    """The union, and every disagreement between the two. A gauge does not move."""
    out = dict(committed)
    conflicts = []
    for key, spec in found.items():
        prior = out.get(key)
        if prior and (prior.get("lon"), prior.get("lat")) != (spec["lon"], spec["lat"]):
            conflicts.append(f"{key}: committed {prior.get('lon')},{prior.get('lat')} "
                             f"vs source {spec['lon']},{spec['lat']}")
            continue
        out[key] = spec
    return dict(sorted(out.items())), conflicts


def document(reservoirs: dict[str, dict]) -> str:
    """The asset's bytes. Sorted keys and a trailing newline, so a diff is a real diff."""
    doc = {
        "_spec": 1,
        "source": "waterdatafortexas.org recent-conditions.json, archived under "
                  "ledger/gridwatch/raw by waterwatch_collect",
        "note": "Gauge positions, which do not change. Storage and capacity are not here: "
                "those move daily and live in ledger/gridwatch/water.jsonl. Built by "
                "scripts/shared/reservoirs.py, never hand-edited.",
        "count": len(reservoirs),
        "reservoirs": reservoirs,
    }
    return json.dumps(doc, indent=1, sort_keys=False, ensure_ascii=False) + "\n"


def build(write: bool = True) -> tuple[str, list[str]]:
    """Rebuild the asset from the archive. Returns the bytes it should hold and any conflict."""
    merged, conflicts = merge(load(), from_payloads())
    text = document(merged)
    if write and not conflicts:
        ASSET.parent.mkdir(parents=True, exist_ok=True)
        ASSET.write_text(text, encoding="utf-8")
    return text, conflicts


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    failures = 0

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    held = load()
    check("the asset is committed and holds reservoirs", bool(held), f"{len(held)} entries")

    if held:
        # THE TAG IS CHECKED AGAINST THE GEOMETRY, in both directions, which is worth more
        # than either alone. TWDB's `texas` tag is the field the whole exclusion rests on, and
        # nothing else in this project ever asks whether it is telling the truth. Here the
        # coordinates can answer: everything tagged Texas has to land in Texas, and the one
        # thing not tagged Texas has to land outside it. The first version of this check ran
        # the box over every entry and went red on Elephant Butte, which is New Mexico doing
        # exactly what it should.
        def inbox(v):
            return (TX_BBOX[0] <= v["lon"] <= TX_BBOX[2]
                    and TX_BBOX[1] <= v["lat"] <= TX_BBOX[3])

        stray = [k for k, v in held.items() if v["texas"] and not inbox(v)]
        check("every reservoir tagged Texas lands inside Texas", not stray, str(stray[:5]))
        outside = [k for k, v in held.items() if not v["texas"] and inbox(v)]
        check("nothing tagged out of state lands inside Texas anyway", not outside,
              str(outside[:5]))
        check("every entry carries a name a pin can announce",
              all(v.get("name") for v in held.values()),
              str([k for k, v in held.items() if not v.get("name")][:5]))
        # THE ELEPHANT BUTTE ASSERTION, said here as well as in the collector. This asset is
        # the one thing that puts a dot on a map, so it is the last place an out of state
        # reservoir could sneak into a Texas drawing after the ledger already excluded it.
        eb = held.get("ElephantButte")
        check("Elephant Butte is present and marked as not Texas",
              eb is not None and eb["texas"] is False, str(eb))
        check("...and it really is the only one so marked",
              [k for k, v in held.items() if not v["texas"]] == ["ElephantButte"],
              str([k for k, v in held.items() if not v["texas"]]))

    # IDEMPOTENCE, which is what CI checks and therefore what has to be true here first.
    text, conflicts = build(write=False)
    check("the source and the committed asset agree on every position", not conflicts,
          "; ".join(conflicts[:3]))
    check("a rebuild changes nothing",
          not ASSET.exists() or text == ASSET.read_text(encoding="utf-8"))

    # A MOVED GAUGE IS REFUSED RATHER THAN RESOLVED.
    moved, conf = merge({"X": {"name": "X", "lon": -99.0, "lat": 31.0, "texas": True}},
                        {"X": {"name": "X", "lon": -98.0, "lat": 31.0, "texas": True}})
    check("a position that disagrees with the record is a conflict, not an update",
          len(conf) == 1 and moved["X"]["lon"] == -99.0, str(conf))
    fresh, conf2 = merge({}, {"Y": {"name": "Y", "lon": -99.0, "lat": 31.0, "texas": True}})
    check("a reservoir the asset has never seen is simply added",
          not conf2 and "Y" in fresh)
    # PRUNING THE ARCHIVE MUST NOT PRUNE THE MAP.
    kept, _ = merge({"Z": {"name": "Z", "lon": -99.0, "lat": 31.0, "texas": True}}, {})
    check("a reservoir whose payload has aged out keeps its pin", "Z" in kept)

    check("a payload with no coordinates yields no entry rather than a zero point",
          _spec({"full_name": "Nowhere", "tags": ["texas"]}) is None)
    check("a payload with a broken coordinate is dropped the same way",
          _spec({"full_name": "Bad", "gauge_location": {"coordinates": ["x", "y"]}}) is None)

    if failures:
        print(f"\nreservoirs self-test: {failures} FAILED")
        return 1
    print("\nreservoirs self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", nargs="?", choices=["build"], help="rebuild the asset")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.command == "build":
        text, conflicts = build()
        if conflicts:
            print("reservoirs: the source disagrees with the committed record, nothing written",
                  file=sys.stderr)
            for c in conflicts:
                print(f"  {c}", file=sys.stderr)
            return 1
        print(f"reservoirs: {json.loads(text)['count']} positions -> "
              f"{ASSET.relative_to(REPO_ROOT)}")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
