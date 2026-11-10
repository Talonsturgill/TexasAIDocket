#!/usr/bin/env python3
"""A ONE TIME census, 2026-11-10, by the weekly machine pass. Not a gate and not re-run as one.

    python3 knowledge/carousel/audits/2026-11-10-plan-relief-census.py

The question: does a plan relief (a dossier `projection: orthographic_relief`, a TXBENCH height
field seen straight down) get read as a chart, a keyboard, a UI tray or a card more often than a
spatial frame does? The queue's relief-plate-reads-as-a-tray reached repeat 3 on no. 73, whose two
count reliefs (64 and 8 tray fronts, 860 cells with eight raised) were charged as a keyboard, a chart
or a waffle in all three panel rounds at casts far above print_ban's floor, and the judges' cure was
a raking three quarter camera. The doctrine had ordered "parallel projection for any quantity".

It reads every shipped storyboard from 2026-10-17 (the physical render routes) to the date given,
and every round's judge files, and counts a frame as charged when a judge's ranked defect for that
slide uses one of the chart-like words below. A word match finds a lower bound, never an exact count.
Writes knowledge/carousel/audits/2026-11-10-plan-relief-census.json beside itself.
"""
import glob
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SINCE, UNTIL = "2026-10-17", (sys.argv[1] if len(sys.argv) > 1 else "2026-11-10")
WORDS = re.compile(r"\b(chart|keyboard|grille|tray|dials?|UI|card|slider|waffle|blinds|dashboard|"
                   r"printed grid|ladder|mosaic|diagram)\b", re.I)
GRID = re.compile(r"(\bin plan\b|straight down|seen from above|\brows? of\b|\d+ (columns|rows)|\bby \d+\b|"
                  r"\bcells?\b|\bfield of\b|\bpockets\b|\bbays\b|\bbores\b|\btiles\b)", re.I)
DEFECT = re.compile(r'"slide"\s*:\s*(\d+)[^{}]*?"(?:defect|problem|issue|what)"\s*:\s*"([^"]*)"')


def main() -> int:
    tally = {"plan_relief_repeated_units": [0, 0], "plan_relief_other": [0, 0], "spatial": [0, 0]}
    charged_frames = []
    for d in sorted(glob.glob(str(REPO / "runs" / "carousel" / "2026-*"))):
        day = os.path.basename(d)
        if not (SINCE <= day <= UNTIL) or not os.path.exists(os.path.join(d, "storyboard.md")):
            continue
        kind = {}
        for b in re.split(r"\n(?=slide: \d+)", open(os.path.join(d, "storyboard.md"), encoding="utf-8").read()):
            m = re.match(r"slide: (\d+)", b)
            if not m or "depth:" not in b:
                continue
            s = re.search(r'subject: "?([^\n]*)', b)
            subj = s.group(1) if s else ""
            kind[int(m.group(1))] = (("plan_relief_repeated_units" if GRID.search(subj) else "plan_relief_other")
                                     if "orthographic_relief" in b else "spatial", subj[:120])
        hit = {}
        for f in glob.glob(os.path.join(d, "scores", "*", "score*.json")) + [os.path.join(d, "score.json")]:
            if os.path.exists(f):
                for m in DEFECT.finditer(open(f, encoding="utf-8").read()):
                    n, w = int(m.group(1)), WORDS.search(m.group(2))
                    if n in kind and w:
                        hit.setdefault(n, set()).add(w.group(0).lower())
        for n, (k, subj) in kind.items():
            tally[k][0] += 1
            if n in hit:
                tally[k][1] += 1
                charged_frames.append({"run": day, "slide": n, "kind": k, "words": sorted(hit[n]), "subject": subj})
    out = {"since": SINCE, "until": UNTIL, "computed_by": Path(__file__).name,
           "tally": {k: {"frames": t, "charged_chart_like": h, "share": round(h / t, 3) if t else None}
                     for k, (t, h) in tally.items()},
           "charged": charged_frames}
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    for k, v in out["tally"].items():
        print(f"{k}: {v['charged_chart_like']} of {v['frames']} charged as a chart-like object ({v['share']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
