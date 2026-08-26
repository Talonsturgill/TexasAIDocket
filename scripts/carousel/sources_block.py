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

THE SECOND DEFECT, 2026-08-21, WHICH IS THIS FILE LYING ABOUT ITSELF

For a whole run this was invoked as `--run 2026-08-21`. There is no `--run`. Argparse matches an
unambiguous prefix, so it set the run DIRECTORY to the string `2026-08-21`, which is not a path
that exists. `check()` then found no printed ids, concluded that every printed id resolves,
printed `sources block: clean, every claim id the deck prints resolves to a document` and exited
0, every single time it was asked, including immediately after slide 6 gained two claim ids that
the block did not list. `shipped_check` caught the real state one step later.

**A checker whose empty case is indistinguishable from its clean case is worse than no checker,
because it is trusted.** CLAUDE.md's rule is to run a gate by exit code rather than by reading
its last line, and here the exit code was 0, the last line was reassuring, and the gate had never
been pointed at the run at all. An exit code proves nothing about a checker handed the wrong path.

Three things changed, and each one is a way the same silence was possible.

  1. `allow_abbrev=False`. A flag this script does not have is an error rather than a guess.
  2. A run directory that does not exist is a FAILURE, not an empty clean run.
  3. A deck that prints no claim id at all is a FAILURE. Every deck this project has shipped
     cites its sources on the frames, so zero printed ids means the copy was not read.

And `--build` or `--check` is now required, because with neither this did something that looked
like both.

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


# THE SHAPES THE CLAIMS FILE HAS ACTUALLY SHIPPED IN. The 2026-08-16 run wrote `url` and
# `source_title`, the 2026-08-18 run wrote `url`, `source_publisher` and `published_date`, and
# this run writes `source_url`, `document` and `published`. A checker that knows only today's
# names reports a KeyError on history and gets read as a broken run rather than a naming drift.
URL_KEYS = ("source_url", "url")
TITLE_KEYS = ("document", "source_title", "source_publisher", "publisher")
DATE_KEYS = ("published", "published_date", "retrieved")


def field(claim: dict, keys) -> str | None:
    for k in keys:
        v = claim.get(k)
        if v:
            return v
    return None


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


def provenance_line(docs: list[dict], fetched: "str | list[str]") -> str:
    """The first line of the source block, COUNTED and never asserted.

    Until 2026-08-25 this read "Sources, all primary and fetched <date>". That run's own claims
    file typed seven of its twelve documents `secondary_reported`, so the one line whose entire
    job is telling a reader how good the evidence is overstated exactly that, on the surface a
    sceptic checks first. The compute-not-generate law says a numeral is produced by code from
    data. A statement ABOUT the evidence grade is the same kind of claim and gets the same
    treatment.

    `docs` is one claim per distinct document, not per claim id, because a reader counts
    documents.

    THE WORD "ALL" IS ALSO A CLAIM, and it was the next one to go wrong. `build` passed the
    LATEST retrieved date into a sentence beginning "all fetched", which is true only while a
    run fetches everything on one day. The 2026-08-25 run re-opened after midnight to fetch a
    San Angelo ordinance a scorer proved the deck needed, and the block would have told a
    reader that all twelve of its documents were fetched on the 26th when eleven were fetched
    on the 25th. Nothing would have caught it: every id resolved, every claim carried a date,
    and the gate reads ids rather than adverbs. `fetched` now takes the whole set of distinct
    dates and the sentence is built from how many there are.
    """
    # SINGULAR AND PLURAL, because this line is PUBLISHED COPY and it shipped "one news reports"
    # into the first comment of the 2026-08-26 deck. Every name here was written plural on the
    # assumption a deck cites more than one of each kind, and the first deck to cite exactly one
    # news report published the disagreement on the surface whose whole job is looking careful.
    # The self-test below asserts both halves, which is why the one/two case is in it.
    NAME = {"primary_official": ("official record", "official records"),
            "primary_corporate": ("company filing", "company filings"),
            "secondary_reported": ("news report", "news reports"),
            "data": ("published dataset", "published data"),
            "unstated": ("document of unstated type", "documents of unstated type")}
    kinds: dict[str, int] = {}
    for d in docs:
        k = d.get("source_type") or "unstated"
        kinds[k] = kinds.get(k, 0) + 1
    def _n(i: int) -> str:
        words = "one two three four five six seven eight nine ten eleven twelve".split()
        return words[i - 1] if 1 <= i <= len(words) else str(i)
    parts = [f"{_n(v)} {(NAME.get(k) or (k, k))[0 if v == 1 else 1]}" for k, v in
             sorted(kinds.items(), key=lambda kv: (-kv[1], kv[0]))]
    grade = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]
    days = sorted({fetched} if isinstance(fetched, str) else set(fetched))
    if not days:
        raise SystemExit("sources_block: provenance_line was given no fetch date")
    # Built from the parsed parts rather than by cutting up ordinal_date's output. The first
    # version of this sliced the formatted string on its spaces and commas and shipped
    # "August 25th and 26th,, 2026", which is what string surgery on a formatted date earns.
    def ymd(iso):
        y, m, d = (int(x) for x in iso.split("-"))
        return y, m, d
    def day(iso):
        _, _, d = ymd(iso)
        return f"{d}{ORDINALS.get(d, 'th')}"
    if len(days) == 1:
        when = f"all fetched {ordinal_date(days[0])}"
    elif len(days) == 2:
        (y0, m0, _), (y1, m1, _) = ymd(days[0]), ymd(days[1])
        if (y0, m0) == (y1, m1):
            when = f"fetched {MONTHS[m0 - 1]} {day(days[0])} and {day(days[1])}, {y0}"
        elif y0 == y1:
            when = (f"fetched {MONTHS[m0 - 1]} {day(days[0])} and "
                    f"{MONTHS[m1 - 1]} {day(days[1])}, {y0}")
        else:
            when = f"fetched {ordinal_date(days[0])} and {ordinal_date(days[1])}"
    else:
        when = f"fetched between {ordinal_date(days[0])} and {ordinal_date(days[-1])}"
    return f"Sources, {grade}, {when}."


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
        groups.setdefault(field(by_id[cid], URL_KEYS), []).append(cid)

    retrieved = sorted({by_id[c].get("retrieved") for c in wanted if by_id[c].get("retrieved")})
    if not retrieved:
        raise SystemExit("sources_block: no claim carries a retrieved date")

    lines = [provenance_line([by_id[ids[0]] for ids in groups.values()], retrieved)]
    for url, ids in groups.items():
        c = by_id[ids[0]]
        title = field(c, TITLE_KEYS)
        if not title:
            raise SystemExit(f"sources_block: {c['id']} has no document title. Add a `document` "
                             f"field to claims.json for {url}")
        when = field(c, DATE_KEYS)
        lines.append(f"{title}, {ordinal_date(when)}. {' '.join(ids)}"
                     if when else f"{title}. {' '.join(ids)}")
        lines.append(url)
    lines.append("Day counts computed in compute.py from the source dates above.")
    return "\n".join(lines) + "\n"


# THE ONE RUN THAT SHIPPED BEFORE THIS RULE EXISTED.
#
# The 2026-08-16 deck prints nineteen claim ids its sources block never listed. That block was
# posted as a comment under a published deck, so rewriting the file here would not reach a single
# reader. It would only make a gate green about a comment that still says what it said.
#
# History keeps what was published. Exempt BY NAME, one date, never a date range and never a
# "before" comparison, so a new run can never fall into the exemption by accident. This is the
# same call email_check made on the 2026-08-18 caption's missing hashtags the same day.
SHIPPED_BEFORE_THE_RULE = {"2026-08-16"}


def check(run_dir: Path) -> list[str]:
    """Every id the deck prints must resolve in the block on disk. This is the whole gate.

    THE EXISTENCE TEST COMES BEFORE THE EXEMPTION, deliberately. The exemption is keyed on the
    directory NAME, so checking it first meant any path at all ending in the exempt date passed
    without anything being read, which is the same hole one level down.
    """
    if not run_dir.is_dir():
        return [f"{run_dir} is not a directory, so nothing was read and nothing was checked. "
                f"This is the 2026-08-21 defect: `--run` prefix-matched `--run-dir`, the bare "
                f"date became the path, and the gate reported clean for a whole run"]
    if run_dir.name in SHIPPED_BEFORE_THE_RULE:
        return []
    if not (run_dir / "copy.json").exists() or not (run_dir / "claims.json").exists():
        # No deck copy means no printed claim ids, so there is nothing here to resolve. The
        # LIBRARY says not applicable; the CLI refuses, because an operator who typed --check
        # asked about a deck. See main().
        return []
    copy, claims = load(run_dir)
    path = run_dir / "first_comment.txt"
    if not path.exists():
        return [f"{path} does not exist. The deck prints claim ids and gives a reader nowhere "
                f"to resolve them"]
    text = path.read_text(encoding="utf-8")
    listed = set(ID_LINE.findall(text))
    wanted = deck_claim_ids(copy)
    problems = []
    if not wanted:
        # ZERO IS NOT CLEAN. Every deck this project has shipped prints its claim ids on the
        # frames, so an empty set means copy.json was not read rather than that the deck cites
        # nothing, and reporting it as a pass is what this file spent a run doing.
        return [f"{run_dir / 'copy.json'} names no claim id on any slide. A deck that cites "
                f"nothing is a defect, and an empty set of printed ids trivially resolves, so "
                f"this gate would otherwise report clean having checked nothing"]
    absent = [c for c in wanted if c not in listed]
    if absent:
        problems.append("the deck prints " + " ".join(absent) + " and the sources block does not "
                        "list them, so a reader cannot reach the document")
    by_id = {c["id"]: c for c in claims}
    for cid in sorted(listed, key=lambda c: int(c[1:])):
        if cid not in by_id:
            problems.append(f"the sources block lists {cid}, which is not a verified claim")
            continue
        if (field(by_id[cid], URL_KEYS) or "\x00") not in text:
            problems.append(f"{cid} is listed but its source url is not in the block")
    return problems


def self_test() -> int:
    fails = 0

    def ok(label, cond, extra=""):
        nonlocal fails
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            fails += 1

    # THE PROVENANCE LINE IS COUNTED (2026-08-25), both directions.
    _mix = {"claims": [
        {"id": "c1", "url": "https://a.example/1", "document": "A", "source_type": "primary_official",
         "retrieved": "2026-08-25", "quote": "the first quoted span here", "text": "a"},
        {"id": "c2", "url": "https://b.example/2", "document": "B", "source_type": "secondary_reported",
         "retrieved": "2026-08-25", "quote": "the second quoted span here", "text": "b"},
        {"id": "c3", "url": "https://c.example/3", "document": "C", "source_type": "secondary_reported",
         "retrieved": "2026-08-25", "quote": "the third quoted span here", "text": "c"}]}
    _line = provenance_line(_mix["claims"], "2026-08-25")
    ok("the provenance line counts the source types it actually holds",
       "two news reports" in _line and "one official record" in _line, _line)
    # AND THE SINGULAR IS ASSERTED, because the line above used to read "one official recordS"
    # and this assertion encoded the bug rather than catching it. A self-test written against
    # the current output rather than against the intended output freezes whatever shipped.
    ok("...and a single source of a kind is not pluralised",
       "one official records" not in _line and "one news reports" not in _line, _line)
    ok("...and never claims they are all primary",
       "all primary" not in _line, _line)
    ok("...and a single grade reads as one clause",
       provenance_line([_mix["claims"][0]], "2026-08-25").count(" and ") == 0,
       provenance_line([_mix["claims"][0]], "2026-08-25"))

    # THE WORD "ALL" IS COUNTED TOO (2026-08-26). A run that re-opens across midnight to fetch
    # one more source has two fetch dates, and the sentence used to take the later one and put
    # "all" in front of it.
    _d2 = [_mix["claims"][0], _mix["claims"][1]]
    ok("one fetch date still reads 'all fetched'",
       "all fetched August 25th, 2026." in provenance_line(_d2, ["2026-08-25"]),
       provenance_line(_d2, ["2026-08-25"]))
    ok("two dates in one month name both days and drop 'all'",
       provenance_line(_d2, ["2026-08-25", "2026-08-26"]).endswith(
           "fetched August 25th and 26th, 2026."),
       provenance_line(_d2, ["2026-08-25", "2026-08-26"]))
    ok("...and never doubles the comma the formatted date already carries",
       ",," not in provenance_line(_d2, ["2026-08-25", "2026-08-26"]))
    ok("two dates across months name both months",
       provenance_line(_d2, ["2026-08-25", "2026-09-02"]).endswith(
           "fetched August 25th and September 2nd, 2026."),
       provenance_line(_d2, ["2026-08-25", "2026-09-02"]))
    ok("two dates across years carry both years",
       provenance_line(_d2, ["2026-12-30", "2027-01-02"]).endswith(
           "fetched December 30th, 2026 and January 2nd, 2027."),
       provenance_line(_d2, ["2026-12-30", "2027-01-02"]))
    ok("three or more dates read as a span",
       "fetched between August 25th, 2026 and August 27th, 2026." in
       provenance_line(_d2, ["2026-08-25", "2026-08-26", "2026-08-27"]),
       provenance_line(_d2, ["2026-08-25", "2026-08-26", "2026-08-27"]))
    ok("a bare string is still accepted, so older callers keep working",
       provenance_line(_d2, "2026-08-25") == provenance_line(_d2, ["2026-08-25"]))

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

        # THE EXEMPTION IS ONE NAMED DATE, and a run outside it still fails.
        ok("the exemption names exactly the one run that predates the rule",
           SHIPPED_BEFORE_THE_RULE == {"2026-08-16"}, str(SHIPPED_BEFORE_THE_RULE))
        (d / "first_comment.txt").write_text("Sources.\n")
        ok("...and a run outside it still fails on an unresolved id", check(d) != [])

        # THE EXEMPT RUN IS SKIPPED, and it has to be a directory that EXISTS to be skipped.
        # The old assertion here passed a path under /nonexistent and proved the opposite of
        # what it claimed: any typo ending in the exempt date was silently clean.
        exempt = Path(td) / "2026-08-16"
        exempt.mkdir()
        for f_ in ("copy.json", "claims.json", "first_comment.txt"):
            (exempt / f_).write_text((d / f_).read_text())
        ok("...while the exempt run, which exists, is skipped whole", check(exempt) == [],
           str(check(exempt)))

        # ---- THE 2026-08-21 DEFECT, all three ways it read as clean --------------------
        ghost = Path(td) / "2026-08-21"          # the bare date, taken as a path by --run
        ok("a run directory that does not exist is CAUGHT rather than reported clean",
           any("is not a directory" in p for p in check(ghost)), str(check(ghost)))
        ok("...and an exempt-looking path that does not exist is caught too, because the "
           "existence test runs before the exemption",
           check(Path(td) / "nope" / "2026-08-16") != [])

        # A deck that prints no claim id at all.
        empty = Path(td) / "empty"
        empty.mkdir()
        (empty / "copy.json").write_text(json.dumps({"slides": {"S1": {"claims": []}}}))
        (empty / "claims.json").write_text(json.dumps({"claims": []}))
        (empty / "first_comment.txt").write_text("Sources.\n")
        ok("a deck that prints no claim id at all is CAUGHT",
           any("names no claim id" in p for p in check(empty)), str(check(empty)))

        # AND THE COMMAND LINE. `--run` is the flag that did not exist, and argparse used to
        # take it as a prefix of --run-dir. Run by exit code, which is the whole lesson.
        import subprocess
        me = [sys.executable, str(Path(__file__).resolve())]
        r = subprocess.run(me + ["--run", "2026-08-21", "--check"],
                           capture_output=True, text=True)
        ok("`--run` is refused at the command line rather than prefix-matched", r.returncode != 0,
           f"exit {r.returncode}: {r.stdout[-160:]}{r.stderr[-160:]}")
        r = subprocess.run(me + ["--run-dir", str(ghost), "--check"],
                           capture_output=True, text=True)
        ok("...and a run directory that does not exist exits non-zero", r.returncode != 0,
           f"exit {r.returncode}: {r.stdout[-160:]}")
        r = subprocess.run(me + ["--run-dir", str(d)], capture_output=True, text=True)
        ok("...and neither --build nor --check is refused", r.returncode != 0,
           f"exit {r.returncode}")

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
    # allow_abbrev=False. `--run 2026-08-21` prefix-matched `--run-dir` for a whole run and the
    # gate reported clean on a path that does not exist. A flag this script does not have is now
    # an error, which is the only version of that story that ends at the command line.
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], allow_abbrev=False)
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
    if not (a.build or a.check):
        ap.error("one of --build or --check is required. With neither this did something that "
                 "looked like both, and on 2026-08-21 that read as a pass")
    run_dir = Path(a.run_dir) if a.run_dir else REPO_ROOT / "out" / a.date
    if not run_dir.is_dir():
        print(f"sources_block: {run_dir} is not a directory. Nothing was checked",
              file=sys.stderr)
        return 2
    if a.check and not (run_dir / "copy.json").exists():
        print(f"sources_block: {run_dir / 'copy.json'} does not exist, so which claim ids the "
              f"deck prints is unknown and nothing was checked", file=sys.stderr)
        return 2
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
