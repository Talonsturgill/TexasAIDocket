#!/usr/bin/env python3
"""sources_block.py — build the deck's published sources block, and prove it resolves.

THE DEFECT THIS EXISTS FOR, 2026-08-19

`first_comment.txt` is the only place a reader can turn a claim id printed on a slide back into
a document. The 2026-08-19 deck printed sixteen ids across its eight frames. The sources block
listed seven. Nine resolved to nothing, including all three claims the run had added that day and
four of the five on the closing slide, which is the frame that asks a reader to act.

Nothing caught it. `claims_check` proves every claim is fetched and quoted. `copy_sync_check`
proves the slides say what the copy says. `aggregate_check` proves the numerals trace. Not one of
them looks at the sources block, because it is prose in a text file rather than a rendered slide,
and the block was written by hand early in the run and never revisited when the deck's copy moved.

That is the same shape as the run's other two failures the same day. A rule stated somewhere real,
a surface that drifted away from it, and nothing in between.

WHY IT GROUPS BY DOCUMENT RATHER THAN LISTING SIXTEEN IDS

A reader wants the document. Sixteen lines that name the same PDF five times is a worse answer to
"where did this come from" than six lines that each name a document and the ids it carries. It is
also shorter, which matters where this gets posted.

WHAT IS AUTHORED AND WHAT IS NOT

The document titles are authored, once, in `claims.json` as a `document` field, because the name of
a source is a fact about the source and belongs beside it rather than in a formatter. Everything
else here is assembled: which ids the deck prints comes from `copy.json`, the grouping and the
ordering come from the claims file, and the retrieval date comes from the claims themselves. No
count and no date in the output is typed here.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

ORDINALS = {1: "st", 2: "nd", 3: "rd", 21: "st", 22: "nd", 23: "rd", 31: "st"}
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]
ID_LINE = re.compile(r"\bc\d+\b")


def ordinal_date(iso: str) -> str:
    """`2026-08-19` to `August 19th, 2026`. House style, month first, ordinal day."""
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{MONTHS[m - 1]} {d}{ORDINALS.get(d, 'th')}, {y}"


def load(run_dir: Path) -> tuple[dict, list[dict]]:
    copy = json.loads((run_dir / "copy.json").read_text(encoding="utf-8"))
    raw = json.loads((run_dir / "claims.json").read_text(encoding="utf-8"))
    claims = raw["claims"] if isinstance(raw, dict) and "claims" in raw else raw
    return copy, claims


def deck_claim_ids(copy: dict) -> list[str]:
    """Every claim id the deck prints, in slide order then id order within a slide."""
    out: list[str] = []
    for key in sorted(copy["slides"], key=lambda s: int(s[1:])):
        for cid in copy["slides"][key].get("claims", []):
            if cid not in out:
                out.append(cid)
    return sorted(out, key=lambda c: int(c[1:]))


def build(run_dir: Path) -> str:
    copy, claims = load(run_dir)
    by_id = {c["id"]: c for c in claims}
    wanted = deck_claim_ids(copy)

    missing = [c for c in wanted if c not in by_id]
    if missing:
        raise SystemExit("sources_block: the deck prints ids that are not in claims.json, "
                         + " ".join(missing))

    groups: dict[str, list[str]] = {}
    for cid in wanted:
        groups.setdefault(by_id[cid]["source_url"], []).append(cid)

    retrieved = sorted({by_id[c].get("retrieved") for c in wanted if by_id[c].get("retrieved")})
    if not retrieved:
        raise SystemExit("sources_block: no claim carries a retrieved date")

    lines = [f"Sources, all primary and fetched {ordinal_date(retrieved[-1])}."]
    for url, ids in groups.items():
        c = by_id[ids[0]]
        title = c.get("document")
        if not title:
            raise SystemExit(f"sources_block: {c['id']} has no document title. Add a `document` "
                             f"field to claims.json for {url}")
        lines.append(f"{title}, {ordinal_date(c['published'])}. {' '.join(ids)}")
        lines.append(url)
    lines.append("Day counts computed in compute.py from the source dates above.")
    return "\n".join(lines) + "\n"


def check(run_dir: Path) -> list[str]:
    """Every id the deck prints must resolve in the block on disk. This is the whole gate."""
    copy, claims = load(run_dir)
    path = run_dir / "first_comment.txt"
    if not path.exists():
        return [f"{path} does not exist. The deck prints claim ids and gives a reader nowhere "
                f"to resolve them"]
    text = path.read_text(encoding="utf-8")
    listed = set(ID_LINE.findall(text))
    wanted = deck_claim_ids(copy)
    problems = []
    absent = [c for c in wanted if c not in listed]
    if absent:
        problems.append("the deck prints " + " ".join(absent) + " and the sources block does not "
                        "list them, so a reader cannot reach the document")
    by_id = {c["id"]: c for c in claims}
    for cid in sorted(listed, key=lambda c: int(c[1:])):
        if cid not in by_id:
            problems.append(f"the sources block lists {cid}, which is not a verified claim")
            continue
        if by_id[cid]["source_url"] not in text:
            problems.append(f"{cid} is listed but its source url is not in the block")
    return problems


def self_test() -> int:
    fails = 0

    def ok(label, cond, extra=""):
        nonlocal fails
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            fails += 1

    ok("a date takes the ordinal, month first", ordinal_date("2026-08-19") == "August 19th, 2026",
       ordinal_date("2026-08-19"))
    ok("...and the irregular ones are right",
       [ordinal_date(f"2026-08-0{d}") for d in (1, 2, 3)]
       == ["August 1st, 2026", "August 2nd, 2026", "August 3rd, 2026"])
    ok("...and the teens are all th", ordinal_date("2026-08-11") == "August 11th, 2026")

    copy = {"slides": {"S2": {"claims": ["c3", "c1"]}, "S1": {"claims": ["c1"]}}}
    ok("the deck's ids come out sorted and deduped", deck_claim_ids(copy) == ["c1", "c3"],
       str(deck_claim_ids(copy)))

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "copy.json").write_text(json.dumps(
            {"slides": {"S1": {"claims": ["c1", "c2"]}, "S2": {"claims": ["c3"]}}}))
        (d / "claims.json").write_text(json.dumps({"claims": [
            {"id": "c1", "source_url": "https://a.example/doc", "published": "2026-08-03",
             "retrieved": "2026-08-19", "document": "A notice"},
            {"id": "c2", "source_url": "https://a.example/doc", "published": "2026-08-03",
             "retrieved": "2026-08-19", "document": "A notice"},
            {"id": "c3", "source_url": "https://b.example/rel", "published": "2026-08-18",
             "retrieved": "2026-08-19", "document": "A release"},
        ]}))
        built = build(d)
        ok("two claims on one document collapse to one line", built.count("https://a.example/doc") == 1,
           built)
        ok("...and that line carries both ids", "c1 c2" in built, built)
        ok("...and the second document gets its own line", "https://b.example/rel" in built)

        (d / "first_comment.txt").write_text(built)
        ok("the block it just built passes its own check", check(d) == [], str(check(d)))

        # THE REAL DEFECT, replayed. The deck grew a claim and the block did not.
        (d / "copy.json").write_text(json.dumps(
            {"slides": {"S1": {"claims": ["c1", "c2"]}, "S2": {"claims": ["c3"]},
                        "S3": {"claims": ["c4"]}}}))
        (d / "claims.json").write_text(json.dumps({"claims": json.loads(
            (d / "claims.json").read_text())["claims"] + [
            {"id": "c4", "source_url": "https://c.example/cal", "published": "2026-08-19",
             "retrieved": "2026-08-19", "document": "A calendar"}]}))
        probs = check(d)
        ok("an id the deck prints and the block omits is CAUGHT", len(probs) == 1, str(probs))
        ok("...and it names the id", probs and "c4" in probs[0], str(probs))
        ok("...and rebuilding fixes it",
           (lambda t: (d / "first_comment.txt").write_text(t) or check(d) == [])(build(d)),
           str(check(d)))

        # A block naming a claim the run never verified is the other direction.
        (d / "first_comment.txt").write_text(build(d) + "c99 something nobody fetched\n")
        probs = check(d)
        ok("an id in the block that is not a verified claim is CAUGHT",
           any("c99" in p for p in probs), str(probs))

        # A document with no title is a build error rather than a silent blank.
        (d / "claims.json").write_text(json.dumps({"claims": [
            {"id": "c1", "source_url": "https://a.example/doc", "published": "2026-08-03",
             "retrieved": "2026-08-19"}]}))
        (d / "copy.json").write_text(json.dumps({"slides": {"S1": {"claims": ["c1"]}}}))
        try:
            build(d)
            ok("a claim with no document title refuses to build", False, "no error raised")
        except SystemExit as e:
            ok("a claim with no document title refuses to build", "document" in str(e), str(e))

    print("\nsources_block self-test: " + ("all passed" if not fails else f"{fails} FAILED"))
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date", help="run date, for out/<date>/")
    ap.add_argument("--run-dir")
    ap.add_argument("--build", action="store_true", help="write first_comment.txt")
    ap.add_argument("--check", action="store_true", help="fail if any printed id does not resolve")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not (a.date or a.run_dir):
        ap.error("one of --date or --run-dir is required")
    run_dir = Path(a.run_dir) if a.run_dir else REPO_ROOT / "out" / a.date
    if a.build:
        text = build(run_dir)
        (run_dir / "first_comment.txt").write_text(text, encoding="utf-8")
        print(text, end="")
        print(f"\nsources block: {len(deck_claim_ids(load(run_dir)[0]))} claim id(s) across "
              f"{text.count('http')} document(s)", file=sys.stderr)
        return 0
    problems = check(run_dir)
    if problems:
        print("sources_block: the published sources block does not resolve what the deck prints.",
              file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        return 1
    print(f"sources block: clean, every claim id the deck prints resolves to a document")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
