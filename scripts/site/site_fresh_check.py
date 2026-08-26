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

WHY THE DATE COMES FROM THE COMMITTED SITE AND NOT FROM THE CLOCK

The question this asks is "does docs/ say anything the ledgers do not". It is NOT "was docs/
built today". Those are different, and conflating them broke the deploy.

The site stamps its own build date, in the footer a reader sees and in the sitemap a crawler
reads. Rebuilding against the CURRENT date therefore reports every page as changed the moment
UTC rolls past midnight, even though not one byte of the record moved. That is exactly what
happened: the pages workflow passed `--today $(date -u +%F)`, the committed site said August
11th, the rebuild said August 12th, and a gate meant to catch a hand-edited page instead
refused to publish a perfectly correct one, every day, forever.

So the rebuild uses the date the committed site was BUILT with, read from the instrument
series the build publishes.
Content equality is then the only thing being tested, which is the only thing this gate was
ever about. Pass `--today` explicitly to compare against a specific date instead.

    site_fresh_check.py
    site_fresh_check.py --today 2026-08-11

EXIT CODES
    0  the site matches           1  it does not, or the build failed
"""
from __future__ import annotations

import argparse
import difflib
import filecmp
import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import site_build                                                  # noqa: E402

DOCS = REPO_ROOT / "docs"


# THE FILES THAT CARRY THE BUILD'S OWN STAMP. Each is written by the same build that stamped
# every page, with the same `today`, so any of them answers the question and they cannot
# disagree without the build having half finished.
#
# IT READ `docket.json` UNTIL 2026-08-23 AND THAT FILE IS NO LONGER PUBLISHED. Removing the
# record download took the freshness proof's clock with it, and this gate went red on a change
# that had nothing to do with freshness. That is the gate working: it said it could not find a
# date rather than rebuilding against today and reporting all 368 pages as drifted. A list is
# what it should have read from in the first place, because a proof that depends on one file
# continuing to exist is a proof with a single point of silence.
STAMPED = ("gridwatch.json", "waterwatch.json", "weather.json")


def built_with(docs: Path) -> str | None:
    """The date the committed site was built with, taken from the series it publishes.

    Each file in `STAMPED` carries `_spec.generated`, written by the same build that stamped
    every page. Reading it back is how the rebuild reproduces the committed site rather than a
    differently dated one. The first one present answers; only a site missing all of them has
    nothing to reproduce against.
    """
    for name in STAMPED:
        f = docs / name
        if not f.exists():
            continue
        try:
            spec = json.loads(f.read_text(encoding="utf-8")).get("_spec") or {}
        except (json.JSONDecodeError, OSError):
            continue
        d = spec.get("generated")
        if isinstance(d, str) and len(d) == 10:
            return d
    return None


def compare(committed: Path, fresh: Path) -> tuple[list, list, list]:
    def rel(root):
        return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}

    a, b = rel(committed), rel(fresh)
    missing = sorted(b - a)          # a fresh build produces these and the site lacks them
    extra = sorted(a - b)            # the site carries these and a fresh build does not
    changed = sorted(p for p in (a & b)
                     if not filecmp.cmp(committed / p, fresh / p, shallow=False))
    return missing, extra, changed


def first_difference(committed: Path, fresh: Path, changed: list[str],
                     lines: int = 24) -> tuple[str, list[str]] | None:
    """The first changed TEXT file, as a unified diff, capped at `lines` lines.

    A gate that names a file and stops is a gate that turns every recurrence into a research
    project, and on a runner the fresh build is gone the moment the job ends. The first file is
    enough: these differences come in one shape at a time, and twenty four lines of context is
    the difference between reading the answer and pushing again to look for it.

    Binary output is skipped rather than dumped, because a webp rendered a byte differently
    tells a reader nothing they can act on and would bury the text file behind it.
    """
    for p in changed:
        try:
            a = (committed / p).read_text(encoding="utf-8").splitlines()
            b = (fresh / p).read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        d = list(difflib.unified_diff(a, b, fromfile="committed", tofile="fresh", n=1))
        if not d:
            continue
        if len(d) > lines:
            d = d[:lines] + [f"...and {len(d) - lines} more diff line(s)"]
        return p, d
    return None


def self_test() -> int:
    """Two properties, and the second one is why this file has a self-test at all."""
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    with tempfile.TemporaryDirectory() as td:
        built = Path(td) / "built"
        site_build.build(built, "2026-08-11")

        ok("the site records the date it was built with", built_with(built) == "2026-08-11",
           str(built_with(built)))

        # THE REGRESSION THIS EXISTS FOR. A site built yesterday is still a correct site
        # today. Checking it against the current date reported every page as changed and
        # refused to deploy a perfectly good build, every day, until somebody looked.
        fresh = Path(td) / "same"
        site_build.build(fresh, built_with(built))
        missing, extra, changed = compare(built, fresh)
        ok("a rebuild at the site's own date is byte identical",
           not (missing or extra or changed), f"{len(changed)} changed")

        later = Path(td) / "later"
        site_build.build(later, "2026-08-12")
        _, _, changed_by_date = compare(built, later)
        ok("...while a rebuild at a DIFFERENT date differs, which is the trap",
           bool(changed_by_date), "if this passes, the date stamp vanished and the note "
                                 "above is now wrong")

        # AND IT MUST STILL BITE. A gate that cannot go red proves nothing.
        (built / "services" / "index.html").write_text("hand edited", encoding="utf-8")
        _, _, edited = compare(built, fresh)
        ok("a hand edited page is still caught", "services/index.html" in edited,
           str(edited))

        (built / "planted.html").write_text("x", encoding="utf-8")
        _, extra2, _ = compare(built, fresh)
        ok("a file no build produces is still caught", "planted.html" in extra2)

        (fresh / "orphan.html").write_text("x", encoding="utf-8")
        missing2, _, _ = compare(built, fresh)
        ok("a file the build produces and the site lacks is still caught",
           "orphan.html" in missing2)

        # AND IT SAYS WHAT DIFFERS, not only where. The hand edit above is still in place, so
        # the diff of it is the one this asks for. A binary file is offered FIRST so the skip
        # is exercised rather than assumed: a webp whose bytes moved tells a reader nothing and
        # would bury the text file behind it.
        (built / "planted.bin").write_bytes(b"\xff\xfe\x00")
        (fresh / "planted.bin").write_bytes(b"\xff\xfe\x01")
        found = first_difference(built, fresh, ["planted.bin", "services/index.html"])
        ok("...and the report says WHAT differs, not only where",
           found is not None and found[0] == "services/index.html"
           # `-`, because the hand edit is on the COMMITTED side and the fresh build is what
           # the page should say. Asserting `+` here passed nothing and was the first thing
           # this check caught, which is the argument for writing it at all.
           and any(ln.startswith("-") and "hand edited" in ln for ln in found[1]),
           str(found)[:200])

    ok("an unbuilt site reports no date rather than guessing one",
       built_with(Path("/nonexistent")) is None)

    if failures:
        print(f"\nsite_fresh_check self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\nsite_fresh_check self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--today", help="compare against this date instead of the site's own")
    ap.add_argument("--docs", default=str(DOCS))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        return self_test()

    committed = Path(a.docs)
    if not committed.exists():
        print("site_fresh_check: no docs/ committed yet, nothing to compare")
        return 0

    today = a.today or built_with(committed)
    if not today:
        print("site_fresh_check: the committed site carries no build date in any of "
              f"{', '.join(STAMPED)}, "
              "so there is nothing to reproduce it against", file=sys.stderr)
        return 1

    # THE DIFF IS TAKEN BEFORE THE TEMP DIRECTORY GOES AWAY, WHICH IS WHY IT IS IN HERE.
    #
    # This gate named a file and stopped, and a filename is not a finding. On 2026-08-26 it
    # reported `datacenters/index.html` on a runner while passing on the machine that built the
    # page, and working out WHICH BYTES differ meant pushing to CI to look, which is the one
    # thing this repository's own rules ask a session not to do repeatedly. The fresh build lives
    # in a TemporaryDirectory that is deleted on the way out of this block, so a diff taken after
    # the report has nothing left to read. It is captured here and printed below.
    with tempfile.TemporaryDirectory() as td:
        fresh = Path(td) / "fresh"
        site_build.build(fresh, today)
        missing, extra, changed = compare(committed, fresh)
        detail = first_difference(committed, fresh, changed)

    if not (missing or extra or changed):
        n = sum(1 for _ in committed.rglob("*") if _.is_file())
        print(f"site is fresh: {n} file(s) match a rebuild byte for byte "
              f"(rebuilt as of {today})")
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
    if detail:
        print(f"\n  WHAT DIFFERS in {detail[0]}, committed against fresh", file=sys.stderr)
        for line in detail[1]:
            print(f"    {line.rstrip()}", file=sys.stderr)
    print("\n  Fix: rebuild with scripts/site/site_build.py and commit the result. Never edit "
          "docs/ by hand.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                       # noqa: BLE001
        print(f"site_fresh_check: broke: {exc}", file=sys.stderr)
        sys.exit(1)
