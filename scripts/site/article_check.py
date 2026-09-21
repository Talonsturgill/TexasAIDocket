#!/usr/bin/env python3
"""Reject a shipped carousel without a source-bound, standalone web edition.

IT ALSO LINTS THE EDITION'S OWN PROSE, AND UNTIL 2026-09-21 NOTHING DID.

An integrity judge found a colon in a shipped edition's prose, which CLAUDE.md files under
"House rules that never bend", and the finding came with the reason nothing had caught it:
the edition is the one PUBLISHED surface whose prose no pre-merge gate reads. `caption_check`
is pointed at `caption.txt` and at the built site. `house_style_check` reads `docs/`, which
only exists after `site_build`, which runs after the deck has been scored. So a colon in an
edition sailed past a suite that was linting the caption sitting beside it.

The same rules, the same checker, on the same surface as everything else this project
publishes. Two things are stripped before judging, because neither is this project's prose:
`{{token:cNN}}` template tokens, whose colon is syntax, and `[span](cNN)` bracket contents,
which are the claim's own words and are checked for fidelity elsewhere.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "carousel"))
from caption_check import check as house_style  # noqa: E402
from site_context import REPO_ROOT, load_runs  # noqa: E402
from site_pages.article_edition import load_edition, render  # noqa: E402

TOKEN = re.compile(r"\{\{[^}]*\}\}")
SPAN = re.compile(r"\[([^\]]+)\]\(c\d+\)")


def prose_fields(node, path="edition"):
    """Every authored string in an edition, with the path that locates it."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "_spec":
                continue
            yield from prose_fields(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from prose_fields(value, f"{path}[{i}]")
    elif isinstance(node, str):
        yield path, node


def house_style_problems(edition) -> list[str]:
    """House-rule violations in the edition's OWN prose, claim words excluded."""
    out = []
    for path, text in prose_fields(edition):
        if path.endswith(".id") or ".claims" in path:
            continue
        prose = SPAN.sub(" ", TOKEN.sub(" ", text))
        for problem in house_style(prose):
            out.append(f"{path}: {problem}")
    return out

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
    linted = 0
    for run in runs:
        try:
            edition = load_edition(run)
            render(run, run["date"], items, edition)
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            errors.append(f'{run["date"]}: {exc}')
            continue
        linted += 1
        for problem in house_style_problems(edition):
            errors.append(f'{run["date"]} {problem}')
    if errors:
        print("article_check: FAIL\n" + "\n".join(errors), file=sys.stderr)
        return 1
    print(f"article_check: {len(runs)} complete, source-bound web editions, "
          f"{linted} linted against the house rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
