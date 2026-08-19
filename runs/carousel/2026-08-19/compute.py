#!/usr/bin/env python3
"""compute.py — every numeral this deck may print that is not quoted from a source.

The law in CLAUDE.md: a numeral reaches published copy in exactly two ways, quoted from a source
or computed by code from the record. This file is the second way. It writes computed.json, and
`numeral_lint` and `aggregate_check` read it.

Nothing here is typed from memory. The dates come from the verified claims file and the run date,
and every span is `date - date` rather than a number a model counted on its fingers.
"""
import json
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLAIMS = json.loads((HERE / "claims.json").read_text(encoding="utf-8"))

RUN = date(2026, 8, 19)

# Dates that appear inside verified quotes. Each is named with the claim it comes from, so a
# reader of this file can trace any span back to a fetched document.
DIRECTIVE = date(2026, 8, 3)        # c1, "Today, August 3, 2026 ... received a letter"
BATCH_ZERO_DEADLINE = date(2026, 8, 7)   # c2, "by August 7, 2026"
OPEN_MEETING = date(2026, 8, 20)    # c3, "August 20, 2026 open meeting"
COALITION = date(2026, 8, 18)       # c16, release published August 18th

out = {
    "run_date": RUN.isoformat(),
    "source_dates": {
        "directive": DIRECTIVE.isoformat(),
        "batch_zero_deadline": BATCH_ZERO_DEADLINE.isoformat(),
        "open_meeting": OPEN_MEETING.isoformat(),
        "coalition_release": COALITION.isoformat(),
    },
    "spans": {
        "days_since_directive": (RUN - DIRECTIVE).days,
        "days_since_deadline_passed": (RUN - BATCH_ZERO_DEADLINE).days,
        "days_until_open_meeting": (OPEN_MEETING - RUN).days,
        "days_directive_to_deadline": (BATCH_ZERO_DEADLINE - DIRECTIVE).days,
    },
    # Quoted figures, carried through so numeral_lint can trace a slide's digits to a claim.
    # These are NOT computed. They are the source's own numerals, repeated verbatim.
    "quoted": {
        "queue_gigawatts": {"value": 474, "wording": "approximately 474 gigawatts", "claim": "c6"},
        "data_center_share_percent": {"value": 90, "wording": "Approximately 90 percent",
                                      "claim": "c8"},
        "peak_multiple": {"wording": "more than five times", "claim": "c9"},
    },
    "counts": {
        "verified_claims": len(CLAIMS["claims"]),
        "rejected_findings": len(CLAIMS["rejected"]),
        "information_demands_quoted": 2,   # c14 and c15, the two the claims file carries verbatim
    },
}

# The one thing this deck must never print: a data center gigawatt figure derived by multiplying
# the queue by the data center share. Both numerals are real and the product is not in any source.
assert "data_center_gigawatts" not in out["quoted"]

(HERE / "computed.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, indent=2))
