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
STRICT_REQUIRED = ("claims", "render", "qa", "assembly", "score", "dossiers", "caption")

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

    def artifact(name: str, rel: str, read):
        p = d / rel
        if not p.exists():
            out.append(Row(name, ABSENT, f"{rel} not written yet"))
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

    board = d / "storyboard.md"
    out.append(Row("dossiers", PASS if board.exists() else ABSENT,
                   f"{len(board.read_text(encoding='utf-8')):,} chars planned" if board.exists()
                   else "storyboard.md not written yet"))
    cap = d / "caption.txt"
    out.append(Row("caption", PASS if cap.exists() else ABSENT,
                   f"{len(cap.read_text(encoding='utf-8').split()):,} words"
                   if cap.exists() else "caption.txt not written yet"))
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
    val = s.get("score") or s.get("total") or s.get("weighted")
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
    """Write the fresh block in, replacing any previous one. Idempotent by construction."""
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
