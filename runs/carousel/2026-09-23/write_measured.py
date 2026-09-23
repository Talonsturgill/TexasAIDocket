#!/usr/bin/env python3
"""write_measured.py — compose this run's L* prose FROM measurements.json.

Every luminance printed in this run's prose has to exist in `measurements.json`, because
shipped_check's `measured figures` gate asks the shipped bytes rather than trusting whatever
wrote them. Its docstring calls it the highest recurrence defect in this repo, four times over,
and the shape is always the same: a value with one home, surfaces that keep their own copy, and
nothing in between checking they agree.

So the prose does not get to TYPE a luminance. It carries a token, this file substitutes the
measured value, and a rewrite that changes the art and re-runs measure.py changes the prose with
it. The tokens are deliberately not the old numbers as literal strings, which is exactly how the
previous writer went silently dead.

    {{MAX_STEP_L}}   the largest adjacent median step across the nine frames
    {{SPREAD_L}}     max minus min over the nine medians
    {{MEDIAN_L:n}}   frame n's own median

Run it after measure.py and before anything reads the storyboard.
"""
import json
import re
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
M = json.loads((RUN / "measurements.json").read_text(encoding="utf-8"))
med = [f["median_L"] for f in M["per_frame"]]

VALUES = {
    "MAX_STEP_L": M["max_adjacent_step_L"],
    "SPREAD_L": M["spread_L"],
}
for i, v in enumerate(med, 1):
    VALUES[f"MEDIAN_L:{i}"] = v


def render(text: str) -> str:
    def sub(m):
        key = m.group(1)
        if key not in VALUES:
            raise SystemExit(f"write_measured: no measured figure named {key}")
        return f"{VALUES[key]:g}"
    return re.sub(r"\{\{([A-Z_]+(?::\d+)?)\}\}", sub, text)


def main() -> int:
    targets = [RUN / "storyboard.md"]
    n = 0
    for p in targets:
        if not p.exists():
            continue
        before = p.read_text(encoding="utf-8")
        after = render(before)
        if after != before:
            p.write_text(after, encoding="utf-8")
            n += 1
    print(f"write_measured: {n} file(s) composed from measurements.json, "
          f"max step {VALUES['MAX_STEP_L']:g} L*, spread {VALUES['SPREAD_L']:g} L*")
    return 0


if __name__ == "__main__":
    sys.exit(main())
