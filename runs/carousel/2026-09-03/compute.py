#!/usr/bin/env python3
"""compute.py — every figure this deck publishes that is not quoted from a claim.

THE LAW THIS FILE EXISTS FOR. No numeral in published copy is produced by a language model. A
figure reaches a slide by being quoted verbatim from a claim in claims.json, or by being computed
here from figures that were. Arithmetic, ratios, rounding and unit handling all happen in Python.

Every value below carries the claim ids it was derived from, so `aggregate_check.py` can hold the
deck to it and a reader can redo it.

Run: python3 out/2026-09-03/compute.py
Writes: out/2026-09-03/computed.json
"""
from __future__ import annotations

import json
import pathlib
from decimal import Decimal, ROUND_HALF_UP

RUN = pathlib.Path(__file__).resolve().parent
OUT = RUN / "computed.json"

# ---------------------------------------------------------------- quoted inputs
# Each of these is READ OFF a verbatim quote in claims.json. Nothing here is remembered or
# estimated, and the quote each came from is named beside it.
RMAX_PFLOPS = Decimal("34.82")     # c3, c4  "Linpack Performance (Rmax) 34.82 PFlop/s"
RPEAK_PFLOPS = Decimal("51.16")    # c3      "Theoretical Peak (Rpeak) 51.16 PFlop/s"
CORES = 110960                     # c5      "Cores: 110,960"
NODES = 95                         # c6      "95 NVIDIA DGX nodes"
GPUS = 760                         # c6      "760 NVIDIA H200 graphics processing units"
UNIVERSITIES = 12                  # c9      "our 12 universities and eight state agencies"
STATE_AGENCIES = 8                 # c9      same quote, spelled "eight"
WORLD_RANK = 66                    # c2      "Ranked No. 66 in the world"


def pct(num: Decimal, den: Decimal, places: str = "0.1") -> str:
    """A percentage with a STATED rounding rule, because rounding is a computation."""
    return str((num / den * 100).quantize(Decimal(places), rounding=ROUND_HALF_UP))


def main() -> int:
    values = []

    # 1. What fraction of its own theoretical peak the machine actually measured.
    #    This is the honest way to draw "how fast is it" without a bar chart of one number,
    #    and both ends come off the same TOP500 row so the comparison is like for like.
    values.append({
        "key": "measured_share_of_peak_pct",
        "value": pct(RMAX_PFLOPS, RPEAK_PFLOPS),
        "unit": "percent",
        "what": "the measured Linpack result as a share of the theoretical peak",
        "from_claims": ["c3"],
        "how": "34.82 divided by 51.16, times 100, rounded half up to one decimal place",
        "kind": "measured",
    })

    # 2. The shortfall the same two numbers describe, stated as the gap rather than the share,
    #    because a frame that draws the gap should print the gap.
    values.append({
        "key": "peak_minus_measured_pflops",
        "value": str(RPEAK_PFLOPS - RMAX_PFLOPS),
        "unit": "PFlop/s",
        "what": "theoretical peak less the measured Linpack result",
        "from_claims": ["c3"],
        "how": "51.16 less 34.82",
        "kind": "measured",
    })

    # DELIBERATELY NOT COMPUTED, and this is the interesting half of the file.
    #
    # GPUS PER NODE, CORES PER NODE. 760 divided by 95 is exactly 8, and it is arithmetic no
    # source performed. Printing it asserts a UNIFORM distribution across the nodes, which is a
    # claim about the machine's architecture that neither the list nor either newsroom makes.
    # The division is true and the sentence it licenses is not.
    #
    # TWELVE PLUS EIGHT. The chancellor names 12 universities and eight state agencies. They are
    # different kinds of institution, nothing in the record adds them, and a single total would
    # invent a set the deck could then count against. Both treatments that reached this run named
    # it independently, which is why it is written down here rather than just left out.
    #
    # THE TWO COMPOUND COUNTS. c18 says approximately 10.4 million on the project's own use cases
    # page and c19 says more than 10 million in about a week. Nothing in the record joins them,
    # so nothing here averages, reconciles or ranges them. The deck prints both with their own
    # attributions or it prints one.

    # 6. How many places ahead of it there are on the list. Rank 66 means 65 machines above.
    values.append({
        "key": "machines_ranked_above",
        "value": str(WORLD_RANK - 1),
        "unit": "machines",
        "what": "how many systems the June 2026 list places above this one",
        "from_claims": ["c2"],
        "how": "66 less 1, since a rank counts the machine itself",
        "kind": "measured",
    })

    doc = {
        "run": "2026-09-03",
        "deck": 14,
        "note": ("Every value here is computed from a figure quoted verbatim in claims.json. "
                 "No numeral in this deck was typed by a model."),
        "inputs": {
            "rmax_pflops": str(RMAX_PFLOPS), "rpeak_pflops": str(RPEAK_PFLOPS),
            "cores": CORES, "nodes": NODES, "gpus": GPUS,
            "universities": UNIVERSITIES, "state_agencies": STATE_AGENCIES,
            "world_rank": WORLD_RANK,
        },
        "values": values,
    }
    OUT.write_text(json.dumps(doc, indent=2) + "\n")
    for v in values:
        print(f"  {v['key']:32s} {v['value']:>10s} {v['unit']}")
    print(f"computed: {len(values)} value(s) -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
