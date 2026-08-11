#!/usr/bin/env python3
"""site_fresh_check.py — prove the published site is exactly what the ledgers produce.

WHAT THIS CATCHES THAT NOTHING ELSE DOES

`site_build.py --self-test` proves two fresh builds agree with each other. That is determinism,
and it is not the same property. This proves the site CURRENTLY COMMITTED matches a fresh build,
which catches two things determinism cannot:

  A HAND EDIT. Somebody, or some run, changed a file under docs/ directly. The output then says
  something the ledgers do not, and every claim this project makes about its own provenance is
  false from that moment on.

  A STALE BUILD. The ledgers moved and the site did not. The page is telling a reader something
  that was true last week, which is the quieter and more likely failure.

This is the guarantee behind "docs/ is generated, never hand-edited" in CLAUDE.md. Without it
that sentence is an intention.

    site_fresh_check.py
    site_fresh_check.py --today 2026-08-11

EXIT CODES
    0  the site matches           1  it does not, or the build failed
"""
from __future__ import annotations

import argparse
import datetime as _dt
import filecmp
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import site_build                                                  # noqa: E402

DOCS = REPO_ROOT / "docs"


def compare(committed: Path, fresh: Path) -> tuple[list, list, list]:
    def rel(root):
        return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}

    a, b = rel(committed), rel(fresh)
    missing = sorted(b - a)          # a fresh build produces these and the site lacks them
    extra = sorted(a - b)            # the site carries these and a fresh build does not
    changed = sorted(p for p in (a & b)
                     if not filecmp.cmp(committed / p, fresh / p, shallow=False))
    return missing, extra, changed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--today", default=_dt.date.today().isoformat())
    ap.add_argument("--docs", default=str(DOCS))
    a = ap.parse_args()

    committed = Path(a.docs)
    if not committed.exists():
        print("site_fresh_check: no docs/ committed yet, nothing to compare")
        return 0

    with tempfile.TemporaryDirectory() as td:
        fresh = Path(td) / "fresh"
        site_build.build(fresh, a.today)
        missing, extra, changed = compare(committed, fresh)

    if not (missing or extra or changed):
        n = sum(1 for _ in committed.rglob("*") if _.is_file())
        print(f"site is fresh: {n} file(s) match a rebuild byte for byte")
        return 0

    print("site_fresh_check: the published site is NOT what the ledgers produce\n",
          file=sys.stderr)
    for label, rows, why in (
        ("CHANGED", changed, "the committed file differs from a fresh build"),
        ("EXTRA", extra, "present in docs/ but no build produces it, which means a hand edit"),
        ("MISSING", missing, "a fresh build produces it and docs/ does not, so the site is stale"),
    ):
        if rows:
            print(f"  {label}  ({why})", file=sys.stderr)
            for p in rows[:20]:
                print(f"    {p}", file=sys.stderr)
            if len(rows) > 20:
                print(f"    ...and {len(rows) - 20} more", file=sys.stderr)
    print("\n  Fix: rebuild with scripts/site/site_build.py and commit the result. Never edit "
          "docs/ by hand.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                       # noqa: BLE001
        print(f"site_fresh_check: broke: {exc}", file=sys.stderr)
        sys.exit(1)
