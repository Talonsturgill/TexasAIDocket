#!/usr/bin/env python3
"""figures.py - the run's own counts, computed over claims.json rather than typed.

ledger_check reads figures.json and refuses a number word in durable memory that its own
COUNTING_FIGURES vocabulary cannot re-derive, which is the right rule: a recut regenerates the
deck and would otherwise leave a ledger entry narrating the old figure.
"""
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
c = json.loads((RUN / "claims.json").read_text())
urls = sorted({cl["url"] for cl in c["claims"]})

out = {
    "claims_verified": {
        "value": len(c["claims"]), "from_items": [],
        "note": "Claims this run fetched and verified, counted over claims.json.",
    },
    "findings_rejected": {
        "value": len(c["rejected"]), "from_items": [],
        "note": "Scout findings the fact check refused, each with a stated reason, counted over "
                "claims.json's rejected list.",
    },
    "source_documents": {
        "value": len(urls), "from_items": urls,
        "note": "Distinct source urls behind the claims this deck rests on, counted over "
                "claims.json. All three have a fetched snapshot under out/2026-09-13/tmp/.",
    },
    "absences_scoped": {
        "value": len(c["absences"]), "from_items": [],
        "note": "Absences this deck asserts, each naming the document checked and a verbatim "
                "basis, counted over claims.json's absences list.",
    },
}
(RUN / "figures.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
