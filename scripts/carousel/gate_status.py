#!/usr/bin/env python3
"""gate_status.py — print the run's gate block from the artifacts, so no sentence can contradict
what is on disk.

WHY THIS EXISTS

Three failures in the sibling product, each one a tighter version of the last, and the third is
the one that explains the design.

**A sentence stood in for an artifact.** A hand-written build reconciliation claimed "qa.py PASS,
zero warns" while `machine_qa.json` on disk said WARN with five. The scorer had to catch it. The
same run's completion gate then false-flagged a perfectly valid caption report because it tested
the file with a 200 byte size threshold and the valid file was 196 bytes. Both are one mistake:
**a human sentence or a byte count standing in for the artifact.** So this parses JSON and never
measures it, and checks binaries by magic bytes rather than by length.

**Printing "do not hand-write these lines" was not enough.** A later run pasted the block once,
ran four more render rounds under it, and shipped a record contradicting its own artifacts on four
rows. Hence `--verify-pasted`, which regenerates and diffs, so staleness is a check rather than a
habit.

**Making staleness a check was not enough either.** The run after that broke the same instinct
twice, at high confidence, and its scorer read a record claiming twenty-nine QA warnings on a deck
measuring twenty. The check only ran at the completion gate, after every reader it could have
protected, and the refresh itself was a hand copy-paste, which is the one step a re-render cannot
do for you. Hence `--sync`, which writes the fresh block into the run record itself. It is
idempotent, so "run it again after every round" is a rule with no cost to obey, and **a rule with
a cost is a rule that gets skipped at the exact moment it matters.**

WHAT THIS ONE ADDS

A row can be true and still be a lie. `machine_qa.json` says PASS, correctly, about the render it
was run on, and then four slides get re-rendered and nobody re-runs it. The artifact is now
answering a question about a deck that no longer exists, and it will keep saying PASS forever.

So every row is compared against the mtime of the newest rendered slide, and an artifact older
than the render it claims to describe is reported **STALE**, not PASS. That is the row a pasted
block and a parsed artifact are equally blind to.

    gate_status.py --date 2026-08-12
    gate_status.py --date 2026-08-12 --sync runs/carousel/2026-08-12/RUN_RECORD.md
    gate_status.py --date 2026-08-12 --verify-pasted runs/carousel/2026-08-12/RUN_RECORD.md
    gate_status.py --date 2026-08-12 --strict         # the ship gate: absent means it never ran
    gate_status.py --self-test

Exit 0 every row passes, 1 a row failed or a pasted block is stale, 2 the checker could not run.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

BEGIN = "<!-- gate-status:begin -->"
END = "<!-- gate-status:end -->"

# Magic bytes, because a file's size says nothing about whether it is the thing it claims to be.
# A 196 byte JSON file is valid and a 4 MB truncated PNG is not.
MAGIC = {".pdf": b"%PDF", ".png": b"\x89PNG\r\n\x1a\n", ".webp": b"RIFF", ".jpg": b"\xff\xd8\xff"}

PASS, WARN, FAIL, ABSENT, STALE = "PASS", "WARN", "FAIL", "ABSENT", "STALE"
BAD = (FAIL, STALE)

# ABSENT is not a failure MID-RUN, because artifacts appear as the phases produce them, and a
# gate that fails at Phase 8 for not having a score yet is a gate that gets ignored by Phase 9.
# At the SHIP gate it is a different fact entirely: an absent artifact means the phase that
# writes it never ran. `--strict` is that reading, and the end-to-end proof is what found the
# gap. Everything self-tested green while a run with no claims file and no score could have
# printed a clean block on its way out the door.
STRICT_REQUIRED = ("claims", "render", "qa", "assembly", "score", "dossiers", "caption",
                   "craft floor", "plan vs render", "absences", "completion")

# WHICH ROWS THE STALENESS RULE APPLIES TO, and the end-to-end proof is what forced this list to
# exist. The rule was applied to every artifact, and it is only true of artifacts that DESCRIBE
# the render.
#
# claims.json is written in Phase 6. The dossiers are Phase 9. The caption is Phase 10. The art
# is built in Phase 11. **Every one of those legitimately predates the render in every run that
# has ever gone right**, so marking them stale would have painted three rows red on every single
# run, forever. A row that is always red is ignored exactly as fast as one that is always green,
# and it would have taught the first real run to stop reading the block.
#
# The rows below are the ones a re-render actually invalidates: the QA of the render, the numbers
# scanned out of the render, the package assembled from it, and the score given to it.
RENDER_DEPENDENT = ("qa", "aggregates", "assembly", "score")


class Row:
    __slots__ = ("name", "status", "detail")

    def __init__(self, name: str, status: str, detail: str = ""):
        self.name, self.status, self.detail = name, status, detail

    def line(self) -> str:
        return f"| {self.name:<14} | {self.status:<6} | {self.detail} |".rstrip()


def load(p: Path):
    """Parse it. Never measure it."""
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def magic_ok(p: Path) -> bool:
    want = MAGIC.get(p.suffix.lower())
    if not want:
        return p.exists()
    try:
        with p.open("rb") as fh:
            return fh.read(len(want)) == want
    except OSError:
        return False


def newest_render(d: Path) -> float:
    """When the deck a row claims to describe was last drawn."""
    pngs = list((d / "render").glob("slide-*.png"))
    return max((p.stat().st_mtime for p in pngs), default=0.0)


def staleness(p: Path, drawn: float) -> bool:
    """True when this artifact predates the render, so it is answering about an older deck."""
    if not drawn or not p.exists():
        return False
    # One second of slack: a gate run in the same instant as the render is not stale, and some
    # filesystems round mtimes to the second.
    return p.stat().st_mtime + 1.0 < drawn


def rows_for(d: Path) -> list[Row]:
    drawn = newest_render(d)
    out: list[Row] = []

    def artifact(name: str, rel: str, read, produced_by: str = ""):
        """One row, read from the artifact a gate WROTE.

        `produced_by` names the command that writes it, and an ABSENT row prints it. A run that
        reads "label_report.json not written yet" has to go looking for what writes it, and the
        two 2026-08-26 gates were exactly the case where looking was expensive: they are the
        newest checks here and neither is named in a workflow, because .github/workflows belongs
        to the human actor. A row that names its own producer is also the reference that makes
        them reachable to port_audit, which fails a script no workflow, prompt or other script
        names, on the grounds that a gate nothing invokes is a gate nothing runs.
        """
        p = d / rel
        if not p.exists():
            out.append(Row(name, ABSENT, f"{rel} not written yet"
                                         + (f". Run {produced_by}" if produced_by else "")))
            return
        data = load(p)
        if data is None:
            out.append(Row(name, FAIL, f"{rel} is unparseable"))
            return
        if name in RENDER_DEPENDENT and staleness(p, drawn):
            out.append(Row(name, STALE, f"{rel} predates the newest render, so it describes a "
                                        f"deck that no longer exists. Re-run it"))
            return
        out.append(read(data))

    artifact("claims", "claims.json", lambda c: _claims(c))
    artifact("render", "render/render_report.json", lambda r: _render(r))
    artifact("qa", "render/machine_qa.json", lambda q: _qa(q))
    artifact("aggregates", "aggregate_report.json", lambda a: _aggr(a))
    artifact("assembly", "final/assemble_report.json", lambda a: _assembly(a, d))
    artifact("score", "score.json", lambda s: _score(s))

    # THE LABEL ROW, ADDED 2026-08-26. A gate nothing reports on is a gate nothing runs, which
    # GATE_LESSONS.md lists as a fault that has shipped here with every check passing. CI cannot
    # take this one, because .github/workflows belongs to the human actor and a run that can edit
    # its own CI can switch off the gate that judges it. The run record's gate table is the one
    # place a run cannot quietly skip, so the row goes here.
    artifact("labels", "label_report.json", lambda r: _labels(r),
             "scripts/carousel/label_guard.py <run-dir>")
    artifact("quantifiers", "quantifier_report.json", lambda r: _quant(r),
             "scripts/carousel/quantifier_check.py <run-dir>")

    board = d / "storyboard.md"
    out.append(Row("dossiers", PASS if board.exists() else ABSENT,
                   f"{len(board.read_text(encoding='utf-8')):,} chars planned" if board.exists()
                   else "storyboard.md not written yet"))
    cap = d / "caption.txt"
    out.append(Row("caption", PASS if cap.exists() else ABSENT,
                   f"{len(cap.read_text(encoding='utf-8').split()):,} words"
                   if cap.exists() else "caption.txt not written yet"))

    # TWO ROWS ADDED 2026-08-19, and they are here because the run record's gate table is the one
    # place a run cannot quietly skip. Both answer questions no other row asked.
    #
    # `craft floor` is the per-frame one. Every other row is deck-level or claim-level, and that
    # is how a frame at canvas variance 15.9, beside another at 3160, shipped seven times breaking
    # no rule. `completion` is the one that refuses to let a run call itself finished under the
    # threshold, because a score is a judgment a run can reason about and an exit code is not.
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    rr = d / "render" / "render_report.json"
    if not rr.exists():
        out.append(Row("craft floor", ABSENT, "nothing rendered yet"))
    else:
        try:
            import craft_floor
            qp = d / "render" / "machine_qa.json"
            cf, cw, cm = craft_floor.check(
                json.loads(rr.read_text(encoding="utf-8")),
                json.loads(qp.read_text(encoding="utf-8")) if qp.exists() else None)
            detail = (f"{len(cm.get('rows', []))} frame(s), median {cm.get('median', 0):.0f}, "
                      f"floor {cm.get('floor', 0):.0f}")
            out.append(Row("craft floor",
                           FAIL if cf else (WARN if cw else PASS),
                           detail + (f", {len(cf)} frame(s) NOT DRAWN" if cf else
                                     f", {len(cw)} quiet" if cw else "")))
        except Exception as exc:                       # noqa: BLE001
            out.append(Row("craft floor", FAIL, f"could not be measured ({exc})"))

    # THE PLAN AGAINST THE RENDER, and the absences against their documents. Both are in this
    # table rather than only in a log, because the two defects they exist for are the two that
    # appeared in all three shipped runs and were found by a judge every single time.
    sb = d / "storyboard.md"
    if not (rr.exists() and sb.exists()):
        out.append(Row("plan vs render", ABSENT, "nothing rendered yet"))
    else:
        try:
            import plan_render_check
            pf, pw, ps = plan_render_check.check(
                sb.read_text(encoding="utf-8"), d / "slides",
                json.loads(rr.read_text(encoding="utf-8")))
            tot = ps.get("checkable", 0) + ps.get("prose", 0)
            out.append(Row("plan vs render",
                           FAIL if pf else (WARN if pw else PASS),
                           f"{ps.get('checkable', 0)} of {tot} acceptance item(s) checkable" +
                           (f", {len(pf)} frame(s) off plan" if pf else "")))
        except Exception as exc:                       # noqa: BLE001
            out.append(Row("plan vs render", FAIL, f"could not be measured ({exc})"))

    # CAN A TEXAN TELL WHERE THIS HAPPENED AND WHAT TO DO NEXT. Never a FAIL, by design: a
    # statewide story names no county and the rubric scores that 7, not 0. It is here so the
    # profile is VISIBLE in the run record, because this is the one finding that appeared in
    # every round of every panel and was never once attacked.
    cj0 = d / "copy.json"
    if not cj0.exists():
        out.append(Row("texan", ABSENT, "no copy yet"))
    else:
        try:
            import texan_check
            _tf, tw, tp = texan_check.check(json.loads(cj0.read_text(encoding="utf-8")))
            out.append(Row("texan", WARN if tw else PASS, texan_check.render(tp)))
        except Exception as exc:                       # noqa: BLE001
            out.append(Row("texan", WARN, f"could not be measured ({exc})"))

    cj = d / "copy.json"
    if not cj.exists():
        out.append(Row("absences", ABSENT, "no copy yet"))
    else:
        try:
            import absence_check
            af, aw, as_ = absence_check.check(
                json.loads(cj.read_text(encoding="utf-8")),
                json.loads(rr.read_text(encoding="utf-8")) if rr.exists() else None)
            out.append(Row("absences",
                           FAIL if af else (WARN if aw else PASS),
                           f"{as_.get('scoped', 0)} of {as_.get('absences', 0)} scoped to a "
                           f"named document" + (f", {len(aw)} unscoped" if aw else "")))
        except Exception as exc:                       # noqa: BLE001
            out.append(Row("absences", FAIL, f"could not be measured ({exc})"))

    # ABSENT UNTIL THERE IS A SCORE TO JUDGE, for the reason stated at the top of this file: a row
    # that is red at Phase 8 for not having a Phase 16 artifact is a row every later phase learns
    # to ignore. Once a score exists this row is FAIL or nothing, and --strict already treats an
    # absent required artifact as the phase never having run.
    if not (d / "score.json").exists():
        out.append(Row("completion", ABSENT, "not scored yet"))
    else:
        try:
            import run_complete
            probs = run_complete.check(d, run_complete.threshold())
            out.append(Row("completion", PASS if not probs else FAIL,
                           "the deck shipped" if not probs else
                           "THE DECK DID NOT SHIP, so this run is not done"))
        except Exception as exc:                       # noqa: BLE001
            out.append(Row("completion", FAIL, f"could not be judged ({exc})"))
    return out


def _claims(c) -> Row:
    items = c.get("claims") or c.get("verified_claims") or []
    n = len(items) if isinstance(items, list) else 0
    return Row("claims", PASS if n else FAIL,
               f"{n} verified claim(s)" if n else "no claims survived verification")


def _render(r) -> Row:
    slides = r.get("slides") or []
    warns = sum(len(s.get("overflow_warnings") or []) for s in slides)
    miss = sum(len(s.get("fonts_missing") or []) for s in slides)
    overflow = sum(1 for s in slides if s.get("body_overflow"))
    bits = [f"{len(slides)} slide(s)"]
    if warns:
        bits.append(f"{warns} overflow warning(s)")
    if miss:
        bits.append(f"{miss} missing font(s)")
    if overflow:
        bits.append(f"{overflow} body overflow(s)")
    bad = miss or overflow
    return Row("render", FAIL if bad else (WARN if warns else PASS), ", ".join(bits))


def _qa(q) -> Row:
    f, w = int(q.get("fails") or 0), int(q.get("warns") or 0)
    if not f and not w:
        n = len(q.get("slides") or [])
        return Row("qa", PASS, f"{n} slide(s), zero fails, zero warns")
    return Row("qa", FAIL if f else WARN, f"{f} fail(s), {w} warn(s)")


def _quant(r) -> Row:
    """Reads quantifier_check's receipt. Every universal on every surface names its set.

    THE DEFECT: rounds 13 and 14 each hard failed on a scope word in prose sitting on top of a
    correctly computed number, and each repair landed on the frame that was named and on no other
    surface. This row exists so the gate table shows the whole surface list was read, not one.
    """
    probs = r.get("problems") or []
    return Row("quantifiers", FAIL if probs else PASS,
               (f"{len(probs)} quantifier(s) the record does not support: {probs[0][:90]}"
                if probs else
                f"{r.get('surfaces', 0)} published string(s) read from one list, every universal "
                f"names its set"))


def _labels(r) -> Row:
    """Reads label_guard's receipt. Every label beside a claim id is the shape the record proves.

    THE DEFECT: on 2026-08-25 frame 3 printed BRAZORIA / CONDITIONS SET / C40 while compute.py
    guarded "resolution adopted" for that item against c40's own words, and passed, because the
    guard runs over the map and the reader reads the frame.
    """
    probs = r.get("problems") or []
    return Row("labels", FAIL if probs else PASS,
               (f"{len(probs)} label(s) the record does not support: {probs[0][:90]}"
                if probs else
                f"{r.get('checked', 0)} claim id(s) checked, every label beside one traces to the "
                f"shape its claim proves"))


def _aggr(a) -> Row:
    """Reads aggregate_check's RECEIPT, not the declaration it checked.

    `aggregates.json` is an input the run authors before the check runs, so a row built from it
    reports only that somebody wrote a file. Worse, it can never clear a STALE flag, because a
    check does not rewrite its own input, so the block ends up telling the run to re-run
    something that re-running cannot fix. The end-to-end proof is what surfaced that.
    """
    n = a.get("declared")
    if n is None:
        decl = a.get("aggregates") or []
        n = len(decl) if isinstance(decl, list) else 0
    probs = a.get("problems") or []
    return Row("aggregates", FAIL if probs else PASS,
               f"{len(probs)} problem(s)" if probs else f"{n} declared and re-derived")


def _assembly(a, d: Path) -> Row:
    mode = a.get("pdf_mode")
    pdf = Path(a.get("pdf") or "")
    if not pdf.is_absolute():
        pdf = d / pdf
    if not magic_ok(pdf):
        return Row("assembly", FAIL, f"{pdf.name} is not a PDF by its magic bytes")
    detail = f"{a.get('slides')} slide(s), {a.get('pdf_mb')} MB, {mode}"
    return Row("assembly", PASS if mode == "vector" else WARN,
               detail + ("" if mode == "vector" else ", raster fallback"))


def _score(s) -> Row:
    # THE SCORER'S OWN FIELD NAME FIRST. `weighted_score` is what this repo's rubric writes and it
    # was missing from this list, so the status block printed "None, below threshold" on a run that
    # had a perfectly good 6.82 in score.json. email_check carries the identical fix and the
    # identical comment: a check that cannot find the number it checks still prints a row, and a
    # row that says None reads as a run that produced nothing rather than as a lookup that missed.
    val = next((s[k] for k in
                ("weighted_score", "score", "weighted_total", "total", "weighted") if k in s), None)
    ship = s.get("ship")
    hard = s.get("hard_fails") or []
    if hard:
        return Row("score", FAIL, f"{val}, hard fail: {', '.join(map(str, hard))}")
    return Row("score", PASS if ship is not False else FAIL,
               f"{val}" + ("" if ship is not False else ", below threshold"))


def block(rows: list[Row]) -> str:
    body = "\n".join(r.line() for r in rows)
    return (f"{BEGIN}\n"
            f"| gate | status | detail |\n"
            f"|---|---|---|\n"
            f"{body}\n"
            f"{END}")


def extract(text: str) -> str | None:
    m = re.search(re.escape(BEGIN) + r".*?" + re.escape(END), text, re.S)
    return m.group(0) if m else None


def sync(record: Path, fresh: str) -> str:
    """Write the fresh block in, replacing any previous one. Idempotent by construction.

    IT REFUSES A TARGET THAT IS NOT PROSE, and that check is the whole reason this docstring is
    longer than the function. On 2026-08-26 a run reached for `--sync` and could not remember
    which file it took, so it passed `ledger/docket.json`, the public record. This function
    appended a markdown table to the end of it and reported success. The file stopped being valid
    JSON, and it went into a commit, because a gate row that says PASS about the artifact it just
    corrupted is not a row anybody re-reads.

    Nothing downstream caught it either. `site_fresh_check` would have, on the next build, and by
    then the damage was two commits deep. So the refusal lives HERE, at the write, which is the
    only place that knows both what it is about to do and to what.
    """
    if record.suffix.lower() not in (".md", ".markdown", ".txt"):
        raise SystemExit(
            f"gate_status --sync writes a MARKDOWN block and {record.name} is not markdown. It "
            f"takes the run record, runs/carousel/<date>/RUN_RECORD.md. On 2026-08-26 this was "
            f"handed ledger/docket.json and appended a gate table to the public record, which "
            f"stopped being valid JSON and was committed twice before anything noticed.")
    text = record.read_text(encoding="utf-8") if record.exists() else ""
    if extract(text) is not None:
        new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: fresh, text, count=1,
                     flags=re.S)
    else:
        new = (text.rstrip() + "\n\n## Gate status\n\n" + fresh + "\n") if text else fresh + "\n"
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(new, encoding="utf-8")
    return new


def run(date: str, out_root: Path, sync_to: str | None, verify: str | None,
        strict: bool = False) -> int:
    d = out_root / date
    if not d.exists():
        print(f"gate_status: {d} does not exist", file=sys.stderr)
        return 2

    rows = rows_for(d)
    fresh = block(rows)

    if verify:
        rec = Path(verify)
        if not rec.exists():
            print(f"gate_status: {rec} does not exist", file=sys.stderr)
            return 2
        pasted = extract(rec.read_text(encoding="utf-8"))
        if pasted is None:
            print(f"gate_status: {rec} carries no gate block. Write one with --sync.",
                  file=sys.stderr)
            return 1
        if pasted.strip() != fresh.strip():
            print("gate_status: THE PASTED BLOCK IS STALE. The record and the artifacts "
                  "disagree.\n")
            print("  on disk now:")
            for line in fresh.splitlines():
                print(f"    {line}")
            print("\n  in the record:")
            for line in pasted.splitlines():
                print(f"    {line}")
            print("\n  Run --sync. Do not retype it: retyping is how it went stale.")
            return 1
        print("gate_status: the pasted block matches the artifacts")
        return 0

    if sync_to:
        sync(Path(sync_to), fresh)
        print(f"gate_status: wrote the block into {sync_to}")
    else:
        print(fresh)

    bad = [r for r in rows if r.status in BAD]
    missing = [r for r in rows if strict and r.status == ABSENT and r.name in STRICT_REQUIRED]
    if missing:
        print(f"\ngate_status: {len(missing)} artifact(s) the ship gate requires were never "
              f"written: {', '.join(r.name for r in missing)}.\n  An absent artifact at ship "
              f"means the phase that writes it did not run.", file=sys.stderr)
    if bad:
        print(f"\ngate_status: {len(bad)} row(s) not passing: "
              f"{', '.join(r.name for r in bad)}", file=sys.stderr)
    return 1 if (bad or missing) else 0


def self_test() -> int:
    import tempfile
    import os
    import time
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    def status_of(rows, name):
        for r in rows:
            if r.name == name:
                return r.status
        return None

    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "2026-08-12"
        (d / "render").mkdir(parents=True)
        (d / "final").mkdir(parents=True)

        (d / "render" / "slide-01.png").write_bytes(MAGIC[".png"] + b"x" * 40)
        drawn = newest_render(d)
        ok("the render's own mtime is found", drawn > 0)

        # THE 196 BYTE LESSON. A valid artifact that is small must not be judged by its length.
        small = d / "claims.json"
        small.write_text(json.dumps({"claims": [{"id": "c1"}, {"id": "c2"}]}), encoding="utf-8")
        ok("a small but valid artifact passes, because it is parsed and not measured",
           status_of(rows_for(d), "claims") == PASS and small.stat().st_size < 200)

        (d / "render" / "machine_qa.json").write_text(
            json.dumps({"slides": [{"file": "slide-01.png"}], "fails": 0, "warns": 0}),
            encoding="utf-8")
        ok("a clean qa artifact reads PASS", status_of(rows_for(d), "qa") == PASS)

        # THE HAND-WRITTEN SENTENCE. The artifact says WARN with five; nothing may say otherwise.
        (d / "render" / "machine_qa.json").write_text(
            json.dumps({"slides": [{}], "fails": 0, "warns": 5}), encoding="utf-8")
        rows = rows_for(d)
        ok("qa WARN with five is reported as WARN with five", status_of(rows, "qa") == WARN)
        ok("...and the count is in the detail, so no sentence can round it away",
           any("5 warn" in r.detail for r in rows if r.name == "qa"))

        (d / "render" / "machine_qa.json").write_text(
            json.dumps({"slides": [{}], "fails": 2, "warns": 1}), encoding="utf-8")
        ok("a qa fail is a FAIL", status_of(rows_for(d), "qa") == FAIL)

        # THE ROW THIS FILE ADDS. A true artifact describing a deck that no longer exists.
        (d / "render" / "machine_qa.json").write_text(
            json.dumps({"slides": [{}], "fails": 0, "warns": 0}), encoding="utf-8")
        ok("qa passes before the re-render", status_of(rows_for(d), "qa") == PASS)
        time.sleep(0.01)
        later = time.time() + 60
        os.utime(d / "render" / "slide-01.png", (later, later))
        ok("...and after four slides are re-rendered under it, the same PASS reads STALE",
           status_of(rows_for(d), "qa") == STALE)
        os.utime(d / "render" / "machine_qa.json", (later + 1, later + 1))
        ok("...and re-running the gate clears it", status_of(rows_for(d), "qa") == PASS)

        # ...but ONLY for artifacts the render invalidates. claims.json is written in Phase 6,
        # the dossiers in Phase 9, the caption in Phase 10, and the art is built in Phase 11, so
        # all three legitimately predate the render in every run that goes right. Marking them
        # stale would paint three rows red on every run forever, and a row that is always red is
        # ignored exactly as fast as one that is always green. The end-to-end proof found this.
        os.utime(d / "claims.json", (1, 1))
        (d / "storyboard.md").write_text("planned", encoding="utf-8")
        (d / "caption.txt").write_text("a caption", encoding="utf-8")
        os.utime(d / "storyboard.md", (1, 1))
        os.utime(d / "caption.txt", (1, 1))
        rows = rows_for(d)
        ok("a claims file older than the render is NOT stale, because it precedes the art",
           status_of(rows, "claims") == PASS, status_of(rows, "claims"))
        ok("...and neither are the dossiers or the caption",
           status_of(rows, "dossiers") == PASS and status_of(rows, "caption") == PASS)

        # Magic bytes, not length.
        (d / "final" / "deck.pdf").write_bytes(b"NOT A PDF" + b"x" * 100000)
        (d / "final" / "assemble_report.json").write_text(
            json.dumps({"pdf": "final/deck.pdf", "pdf_mode": "vector", "slides": 9,
                        "pdf_mb": 4.1}), encoding="utf-8")
        os.utime(d / "final" / "assemble_report.json", (later + 1, later + 1))
        ok("a large file that is not a PDF is a FAIL, whatever it weighs",
           status_of(rows_for(d), "assembly") == FAIL)
        (d / "final" / "deck.pdf").write_bytes(MAGIC[".pdf"] + b"-1.7\nx")
        os.utime(d / "final" / "assemble_report.json", (later + 1, later + 1))
        ok("...and a tiny real PDF passes", status_of(rows_for(d), "assembly") == PASS)

        (d / "final" / "assemble_report.json").write_text(
            json.dumps({"pdf": "final/deck.pdf", "pdf_mode": "raster", "slides": 9,
                        "pdf_mb": 4.1}), encoding="utf-8")
        os.utime(d / "final" / "assemble_report.json", (later + 1, later + 1))
        ok("a raster fallback is a WARN, not a silent pass",
           status_of(rows_for(d), "assembly") == WARN)

        # An unparseable artifact is a failure, never an absence.
        (d / "claims.json").write_text("{not json", encoding="utf-8")
        ok("an unparseable artifact is a FAIL, not an ABSENT",
           status_of(rows_for(d), "claims") == FAIL)
        (d / "claims.json").write_text(json.dumps({"claims": [{"id": "c1"}]}), encoding="utf-8")
        os.utime(d / "claims.json", (later + 1, later + 1))

        # A missing artifact says so rather than passing.
        ok("an artifact never written is ABSENT", status_of(rows_for(d), "score") == ABSENT)

        # ...and ABSENT is tolerated mid-run but refused at the ship gate. Found by the
        # end-to-end proof: every self-test was green while a run with no claims file and no
        # score could still print a clean block on its way out the door.
        ok("mid-run, an absent artifact does not fail the block",
           run("2026-08-12", Path(td), None, None, strict=False) == 0)
        ok("...but --strict refuses it, because absent at ship means the phase never ran",
           run("2026-08-12", Path(td), None, None, strict=True) == 1)

        # --sync and --verify-pasted, which are the two halves of the staleness fix.
        rec = Path(td) / "RUN_RECORD.md"
        rec.write_text("# Run record\n\nSome prose about the run.\n", encoding="utf-8")
        fresh = block(rows_for(d))
        sync(rec, fresh)
        ok("--sync writes the block into a record that had none",
           extract(rec.read_text(encoding="utf-8")) == fresh)
        ok("...and keeps the prose that was already there",
           "Some prose about the run." in rec.read_text(encoding="utf-8"))

        before = rec.read_text(encoding="utf-8")
        sync(rec, fresh)
        ok("--sync is idempotent, so running it after every round costs nothing",
           rec.read_text(encoding="utf-8") == before)

        # THE PASTE-ONCE-THEN-RE-RENDER FAILURE, replayed.
        (d / "render" / "machine_qa.json").write_text(
            json.dumps({"slides": [{}], "fails": 0, "warns": 29}), encoding="utf-8")
        os.utime(d / "render" / "machine_qa.json", (later + 2, later + 2))
        stale_now = block(rows_for(d))
        ok("a record pasted before four more rounds no longer matches the artifacts",
           extract(rec.read_text(encoding="utf-8")) != stale_now)
        sync(rec, stale_now)
        ok("...and --sync brings it back into agreement",
           extract(rec.read_text(encoding="utf-8")) == stale_now)

        ok("a record with no block at all is detectable",
           extract("# Run record\n\nnothing here\n") is None)

    if failures:
        print(f"\ngate_status self-test: {failures} FAILED", file=sys.stderr)
        return 1
    # THE FIELD NAME THIS REPO ACTUALLY WRITES. Missing from the lookup, so a real score
    # rendered as "None, below threshold".
    ok("the score row reads this repo's own weighted_score field",
       "6.82" in _score({"weighted_score": 6.82, "ship": False}).detail,
       _score({"weighted_score": 6.82, "ship": False}).detail)
    ok("...and a held run still says it is below the threshold",
       "below threshold" in _score({"weighted_score": 6.82, "ship": False}).detail)
    ok("...and a shipped run reads PASS",
       _score({"weighted_score": 7.4, "ship": True}).status == PASS)
    ok("...and the older field names still work",
       "7.1" in _score({"total": 7.1, "ship": True}).detail)

    print("\ngate_status self-test: all passed (artifacts parsed, binaries checked by magic "
          "bytes, nothing measured by length)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date")
    ap.add_argument("--out", default=str(REPO_ROOT / "out"))
    ap.add_argument("--sync", metavar="RECORD", help="write the fresh block into this file")
    ap.add_argument("--verify-pasted", metavar="RECORD", dest="verify",
                    help="diff the block in this file against the artifacts")
    ap.add_argument("--strict", action="store_true",
                    help="ship gate: an artifact that was never written is a failure")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.date:
        print("gate_status: pass --date or --self-test", file=sys.stderr)
        return 2
    return run(a.date, Path(a.out), a.sync, a.verify, a.strict)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                            # noqa: BLE001
        print(f"gate_status: broke: {exc}", file=sys.stderr)
        sys.exit(2)
