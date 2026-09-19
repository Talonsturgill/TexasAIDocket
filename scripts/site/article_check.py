#!/usr/bin/env python3
"""Reject a shipped carousel without a source-bound, standalone web edition."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from site_context import REPO_ROOT, load_runs
from site_pages.article_edition import load_edition, render


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", help="Check one shipped date; otherwise check the archive")
    args = parser.parse_args()
    runs = load_runs()
    if args.date:
        runs = [run for run in runs if run["date"] == args.date]
        if not runs:
            print(f"article_check: no shipped run for {args.date}", file=sys.stderr)
            return 1
    items = json.loads((REPO_ROOT / "ledger/docket.json").read_text())["items"]
    errors = []
    for run in runs:
        try:
            render(run, run["date"], items, load_edition(run))
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            errors.append(f'{run["date"]}: {exc}')
    if errors:
        print("article_check: FAIL\n" + "\n".join(errors), file=sys.stderr)
        return 1
    print(f"article_check: {len(runs)} complete, source-bound web editions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
