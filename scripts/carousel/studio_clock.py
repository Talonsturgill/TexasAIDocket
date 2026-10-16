#!/usr/bin/env python3
"""Record real studio checkpoints without resetting the clock across compaction."""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECKPOINTS = ("wake", "record_done", "audition_done", "art_done", "review_done", "panel_done", "package_done")


def stamp(path: Path, checkpoint: str, now: dt.datetime | None = None) -> dict:
    if checkpoint not in CHECKPOINTS:
        raise ValueError("unknown studio checkpoint")
    doc = json.loads(path.read_text()) if path.exists() else {"version": 1, "checkpoints": {}}
    points = doc["checkpoints"]
    if checkpoint in points:
        return doc
    if checkpoint != "wake" and "wake" not in points:
        raise ValueError("record wake before later checkpoints")
    now = now or dt.datetime.now(dt.timezone.utc)
    points[checkpoint] = now.astimezone(dt.timezone.utc).isoformat()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.new")
    temporary.write_text(json.dumps(doc, indent=2) + "\n")
    temporary.replace(path)
    return doc


def elapsed(doc: dict, require_complete: bool = False) -> dict:
    points = doc["checkpoints"]
    if require_complete:
        missing = [name for name in CHECKPOINTS if name not in points]
        if missing:
            raise ValueError("timing report missing checkpoints: " + ", ".join(missing))
    wake = dt.datetime.fromisoformat(points["wake"])
    return {name: round((dt.datetime.fromisoformat(value) - wake).total_seconds() / 60, 2)
            for name, value in points.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True)
    parser.add_argument("--checkpoint", choices=CHECKPOINTS)
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    dt.date.fromisoformat(args.date)
    path = ROOT / "out" / args.date / "studio_clock.json"
    try:
        doc = stamp(path, args.checkpoint) if args.checkpoint else json.loads(path.read_text())
        if args.report:
            print(json.dumps({"elapsed_minutes_from_wake": elapsed(doc, require_complete=True)}, indent=2))
        else:
            print(f"studio_clock: {args.checkpoint} recorded")
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"studio_clock: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
