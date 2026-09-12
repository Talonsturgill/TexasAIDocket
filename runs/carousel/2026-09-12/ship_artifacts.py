#!/usr/bin/env python3
"""ship_artifacts.py — copy this run's artifacts into runs/carousel/2026-09-12/.

WHY A SCRIPT. The shipped run directory is what the site, the email, the archive page and every
future gate read, and `shipped_check.py` holds it to a shape. A hand copy leaves out the one file
nobody remembers, which on 2026-08-19 was the render report and on 2026-08-21 was the storyboard.
This lists the shape once and fails loudly if a source is missing.

It does NOT touch anything already under `runs/` for another date. CLAUDE.md puts overwriting a
shipped run artifact on the short list of things that stop and ask.

    python3 out/2026-09-12/ship_artifacts.py
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[1]
DATE = RUN.name
DEST = ROOT / "runs" / "carousel" / DATE

# (source, destination name). A source that does not exist is a failure, never a skip.
FILES = [
    (RUN / "claims.json", "claims.json"),
    (RUN / "computed.json", "computed.json"),
    (RUN / "aggregates.json", "aggregates.json"),
    (RUN / "aggregate_report.json", "aggregate_report.json"),
    (RUN / "quantifiers.json", "quantifiers.json"),
    (RUN / "quantifier_report.json", "quantifier_report.json"),
    (RUN / "label_report.json", "label_report.json"),
    (RUN / "numeral_report.json", "numeral_report.json"),
    (RUN / "verbatim_report.json", "verbatim_report.json"),
    (RUN / "figures.json", "figures.json"),
    (RUN / "copy.json", "copy.json"),
    (RUN / "caption.txt", "caption.txt"),
    (RUN / "first_comment.txt", "first_comment.txt"),
    (RUN / "storyboard.md", "storyboard.md"),
    (RUN / "measurements.json", "measurements.json"),
    (RUN / "palette_measured.json", "palette_measured.json"),
    (RUN / "palette_exclusions.json", "palette_exclusions.json"),
    (RUN / "compute.py", "compute.py"),
    (RUN / "inject_computed.py", "inject_computed.py"),
    (RUN / "build_copy.py", "build_copy.py"),
    (RUN / "measure.py", "measure.py"),
    (RUN / "measure_palette.py", "measure_palette.py"),
    (RUN / "update_ledgers.py", "update_ledgers.py"),
    (RUN / "ship_artifacts.py", "ship_artifacts.py"),
    (RUN / "render" / "render_report.json", "render_report.json"),
    (RUN / "render" / "machine_qa.json", "machine_qa.json"),
    (RUN / "final" / "assemble_report.json", "assemble_report.json"),
    (RUN / "final" / "carousel.pdf", "carousel.pdf"),
    (RUN / "final" / "contact_sheet.png", "contact_sheet.png"),
]


def main() -> int:
    if not DEST.exists():
        DEST.mkdir(parents=True)
    missing = [str(s) for s, _ in FILES if not s.exists()]
    if missing:
        print("ship_artifacts: MISSING source(s), nothing copied:")
        for m in missing:
            print("  ", m)
        return 1

    for src, name in FILES:
        shutil.copy2(src, DEST / name)

    # the nine frames, their renders and their thumbs
    (DEST / "slides").mkdir(exist_ok=True)
    (DEST / "thumbs").mkdir(exist_ok=True)
    n_html = n_png = n_thumb = 0
    for i in range(1, 10):
        h = RUN / "slides" / f"slide-{i:02d}.html"
        p = RUN / "render" / f"slide-{i:02d}.png"
        t = RUN / "final" / "thumbs" / f"slide-{i:02d}-thumb.png"
        if not (h.exists() and p.exists() and t.exists()):
            print(f"ship_artifacts: frame {i} is incomplete, stopping")
            return 1
        shutil.copy2(h, DEST / f"slide-{i:02d}.html")
        shutil.copy2(h, DEST / "slides" / f"slide-{i:02d}.html")
        shutil.copy2(p, DEST / f"slide-{i:02d}.png")
        shutil.copy2(t, DEST / "thumbs" / f"slide-{i:02d}-thumb.png")
        n_html += 1; n_png += 1; n_thumb += 1

    # the fetched source snapshots, which are what makes a claim re-checkable a year from now
    src_dir = RUN / "sources"
    n_src = 0
    if src_dir.is_dir():
        (DEST / "sources").mkdir(exist_ok=True)
        for f in sorted(src_dir.iterdir()):
            if f.is_file():
                shutil.copy2(f, DEST / "sources" / f.name)
                n_src += 1

    # the scout findings, SPLIT one file per beat, which is how every prior run shipped them
    # and what the archive reader looks for. The run holds them in one file because six agents
    # returning JSON into one place is easier to reconcile, and the shipped shape is the older one.
    import json
    scouts = RUN / "scouts.json"
    n_beat = 0
    if scouts.exists():
        shutil.copy2(scouts, DEST / "scouts.json")
        doc = json.loads(scouts.read_text(encoding="utf-8"))
        for beat, body in (doc.get("beats") or {}).items():
            out = {"run_date": doc.get("run_date"), "beat": beat, "findings": body}
            (DEST / f"scout-{beat}.json").write_text(
                json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            n_beat += 1

    print(f"ship_artifacts: {len(FILES)} file(s), {n_html} slide html, {n_png} png, "
          f"{n_thumb} thumb(s), {n_src} source snapshot(s), {n_beat} scout beat(s) -> {DEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
