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
from caption_check import long_sentences  # noqa: E402
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
    out.extend(long_sentence_problems(edition))
    return out


def long_sentence_problems(edition) -> list[str]:
    """The 30 word backstop, on the edition BEFORE it is rendered.

    `house_style_check` applies this to the built site and `caption_check.check` does not apply
    it at all, so an edition whose prose passed `check()` was reported clean here while carrying
    sentences the site gate would refuse. This file said the edition had been "linted against the
    house rules", which was a claim about a wider surface than it measured. GATE_LESSONS' oldest
    shape, written into a gate three days old.

    THE SPAN IS EXPANDED RATHER THAN STRIPPED, which is the one thing to get right. Elsewhere in
    this file a `[text](c12)` span is replaced by a space, correctly, because judging a source's
    own words against the house comma rules would be judging the source. A reader still READS
    those words, so a sentence's LENGTH has to count them or the backstop measures a sentence
    nobody is shown.
    """
    out = []
    for path, text in prose_fields(edition):
        if path.endswith(".id") or ".claims" in path:
            continue
        prose = SPAN.sub(r"\1", TOKEN.sub("", text))
        for problem in long_sentences(prose):
            out.append(f"{path}: {problem}")
    return out

SPAN_ID = re.compile(r"\[([^\]]+)\]\(c(\d+)\)")
NUMERAL = re.compile(r"\d[\d,]*(?:\.\d+)?")


def span_numeral_problems(date: str, edition) -> list[str]:
    """Every numeral inside a claim bound span appears in that claim's own words.

    The binding check upstream asks only whether the span's claim id is LISTED. It never compares
    the label against the quote, so an edition can bind `[57](c18)` to a claim that says 39 and
    publish, with the source-binding gate green, because the id is real and the id is all anybody
    looked at. A numeral is exactly the thing that gets mistyped and exactly the thing this
    project promises is never typed.

    THE TOKENS ARE STRIPPED FIRST. A label carrying `{{date:c9}}` or `{{number:c12}}` is already
    expanded from the claim at render time, which is the mechanism this check WANTS. Reading the
    digits out of the token's own name and demanding they appear in the quote would fail three
    archived editions for doing the right thing, which is the measurement this file already got
    wrong once today by judging a wider surface than it read.

    A claims file that is absent is not a finding here. `load_edition` and the binding check
    already answer for a run whose claims cannot be read.
    """
    path = REPO_ROOT / "runs/carousel" / date / "claims.json"
    if not path.exists():
        return []
    doc = json.loads(path.read_text(encoding="utf-8"))
    claims = doc["claims"] if isinstance(doc, dict) else doc
    by_id = {c["id"]: c for c in claims}
    out = []
    for field, text in prose_fields(edition):
        if field.endswith(".id") or ".claims" in field:
            continue
        for label, cid in SPAN_ID.findall(text):
            claim = by_id.get(f"c{cid}")
            if claim is None:
                continue
            said = f'{claim.get("quote") or ""} {claim.get("text") or ""}'.replace(",", "")
            for numeral in NUMERAL.findall(TOKEN.sub("", label)):
                if numeral.replace(",", "") not in said:
                    out.append(f'{field}: "{label}" binds c{cid} and prints {numeral}, which is '
                               f"not in that claim's own words. Bind the numeral to the claim it "
                               f"came from, or expand it from the claim with a token")
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
        for problem in span_numeral_problems(run["date"], edition):
            errors.append(f'{run["date"]} {problem}')
    if errors:
        print("article_check: FAIL\n" + "\n".join(errors), file=sys.stderr)
        return 1
    print(f"article_check: {len(runs)} complete, source-bound web editions, "
          f"{linted} linted against the house rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
