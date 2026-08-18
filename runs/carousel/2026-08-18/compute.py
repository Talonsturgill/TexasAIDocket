#!/usr/bin/env python3
"""Every numeral this deck publishes that is not quoted verbatim from a source.

The law in CLAUDE.md: a numeral reaches published copy either quoted from a source or
computed by code from the record. Nothing on a slide is typed. Run this, read the JSON,
and copy nothing by hand.

A NOTE ON WHAT IS DELIBERATELY NOT COMPUTED HERE.

A treatment proposed publishing the instructional day as 510 minutes, the named blocks as
500 of them, and the difference of 10 as time the schedule does not describe. The arithmetic
runs. It is still not published, and this file is where that decision is recorded rather than
in a comment nobody reads.

c4 says the curriculum separates the day into three parts. c3 says the first four hours follow
the standard NES curriculum. NO SOURCE STATES THAT THOSE ARE DISJOINT. If the three parts are
the three c5 blocks and the four hours overlap them, adding them double counts, and the residual
is an artefact of the assumption rather than a fact about the day. A residual computed from an
unstated assumption is an inference wearing a measurement's clothes. The sibling product shipped
exactly that shape of error as a slide reading FIVE where the answer was four.

The rule this encodes: arithmetic is allowed to combine two figures only when a source states
the relationship between them. It never infers the relationship in order to do the arithmetic.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# --- inputs, each a figure quoted verbatim in claims.json ------------------------------
COURSEWORK_MIN = 60      # c5, the source writes this as the WORD "one hour"
EXPERIENCES_MIN = 110    # c5, "110 minutes"
WORKSHOP_MIN = 90        # c5, "90 minutes"

# Slide 5 draws three tiles at true relative length. The tiles are a drawing, so their pixel
# lengths are geometry rather than published numerals, but they are computed here so the
# proportion is provably true rather than eyeballed into the HTML.
TILE_TRACK_PX = 560      # the drawable width reserved for the longest tile on slide 5.
                         # Sized so the longest tile still clears the 80px safe margin from
                         # its own staggered start. The first render at 760 ran the 110
                         # minute tile off the right edge of the frame.

out = {}

longest = max(COURSEWORK_MIN, EXPERIENCES_MIN, WORKSHOP_MIN)

for key, minutes, claim_label in (
    ("coursework", COURSEWORK_MIN, "one hour"),
    ("experiences", EXPERIENCES_MIN, "110 minutes"),
    ("workshop", WORKSHOP_MIN, "90 minutes"),
):
    px = round(TILE_TRACK_PX * minutes / longest)
    out[f"tile_{key}_px"] = {
        "value": px,
        "label": "measured",
        "from": ["c5"],
        "how": f"{TILE_TRACK_PX} * {minutes} / {longest}, true proportion of the longest block",
        "published": False,      # geometry, never printed as text on the slide
        "source_writes_it_as": claim_label,
    }

# The ratio the drawing asserts, stated so a reviewer can check the tiles by measuring them.
out["tile_ratio_check"] = {
    "value": f"{COURSEWORK_MIN}:{EXPERIENCES_MIN}:{WORKSHOP_MIN}",
    "label": "measured",
    "from": ["c5"],
    "how": "the three block durations as the source gives them, for verifying tile lengths",
    "published": False,
}

# --- slide 4's stationing axis --------------------------------------------------------
# The terminus was TYPED at x=660 on the first build, which put the 4:00 p.m. boundary at
# 63 percent of a run whose true proportion is 81 percent, while the ten minute ticks beside
# it were drawn to scale. The frame promised a scale and then contradicted it. A drawn
# proportion is a published quantity, so it is computed here like any other.
AXIS_X0, AXIS_X1 = 84, 996            # the run's own end points in slide coordinates
DAY_START_MIN = 7 * 60 + 30           # 7:30 a.m., c4
INSTR_END_MIN = 16 * 60               # 4:00 p.m., c4
RUN_END_MIN   = 18 * 60               # 6:00 p.m., c4

run_total = RUN_END_MIN - DAY_START_MIN
instr_len = INSTR_END_MIN - DAY_START_MIN
out["axis_instruction_terminus_px"] = {
    "value": round(AXIS_X0 + (AXIS_X1 - AXIS_X0) * instr_len / run_total),
    "label": "measured",
    "from": ["c4"],
    "how": f"{AXIS_X0} + {AXIS_X1 - AXIS_X0} * {instr_len} / {run_total}, the 4:00 p.m. boundary at true position on the 7:30 a.m. to 6:00 p.m. run",
    "published": False,
}
out["axis_instruction_share"] = {
    "value": round(100 * instr_len / run_total, 1),
    "label": "measured",
    "from": ["c4"],
    "how": f"100 * {instr_len} / {run_total}, the share of the drawn run that is instruction",
    "published": False,
}

# --- what the deck REFUSES to compute, recorded on purpose -----------------------------
out["_not_computed"] = {
    "residual_minutes": {
        "why_not": (
            "c4 does not state that the three parts are disjoint from c3's first four hours, "
            "so summing them may double count and any residual is an artefact of that "
            "assumption. Not published in any form."
        )
    }
}

if __name__ == "__main__":
    path = HERE / "computed.json"
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    for k, v in out.items():
        if k.startswith("_"):
            continue
        print(f"{k:28} {v['value']!s:>12}   from {','.join(v['from'])}")
    print(f"\nwrote {path}")
