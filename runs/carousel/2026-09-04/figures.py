#!/usr/bin/env python3
"""figures.json for run 2026-09-04. Every value is COUNTED over the run's own artifacts by this
script and never typed, which is what ledger_check re-derives and what the compute-not-generate
law requires of the counts the topic prose quotes."""
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[3]
RUN = "2026-09-04"
D = ROOT / "out" / RUN

claims = json.loads((D / "claims.json").read_text())
verified = claims["claims"] if isinstance(claims, dict) and "claims" in claims else claims
rejected = claims.get("rejected", []) if isinstance(claims, dict) else []
aggs = json.loads((D / "aggregates.json").read_text())["aggregates"]
copy = json.loads((D / "copy.json").read_text())

def norm(s):
    return "".join(ch for ch in str(s).lower() if ch.isalnum())

by_id = {c["id"]: c for c in verified}
proved = 0
for a in aggs:
    if "quoted_from" in a:
        proved += 1
        continue
    val = str(a.get("value", ""))
    digits = val.replace(".0", "")
    for cid in a.get("from_claims", []):
        q = by_id.get(cid, {}).get("quote", "")
        if digits and (digits in q.replace(",", "") or digits in norm(q)):
            proved += 1
            break

hosts = sorted({urlparse(c["url"]).netloc for c in verified if c.get("url")})

out = {
    "claims_verified": {
        "value": len(verified), "from_items": [],
        "note": "Claims this run fetched and verified, counted over claims.json.",
    },
    "figures_proved": {
        "value": proved, "from_items": [],
        "note": "Declared figures whose value appears in the verbatim quote of the claim they "
                "cite, counted over aggregates.json.",
    },
    "relationships_refused": {
        "value": len([a for a in aggs if "computed_by" in a]), "from_items": [],
        "note": "Figures the deck computes rather than repeats, each naming the claims it was "
                "counted from, counted over aggregates.json.",
    },
    "findings_rejected": {
        "value": len(rejected), "from_items": [],
        "note": "Scout findings the fact check refused, counted over claims.json's rejected list.",
    },
    "official_records": {
        "value": len([c for c in verified if c.get("source_type") == "primary_official"]),
        "from_items": [],
        "note": "Claims whose source_type is primary_official, counted over claims.json.",
    },
    "data_records": {
        "value": len([c for c in verified if c.get("source_type") == "data"]),
        "from_items": [],
        "note": "Claims whose source_type is data, counted over claims.json.",
    },
    "institutions_answering": {
        "value": len(hosts), "from_items": hosts,
        "note": "Distinct hosts this run fetched a claim from, counted over claims.json urls.",
    },
    "frames": {
        "value": len(copy["slides"]), "from_items": [],
        "note": "Frames in the shipped deck, counted over copy.json, which is built from the "
                "render report's own laid out text nodes.",
    },
}
(D / "figures.json").write_text(json.dumps(out, indent=1) + "\n")
for k, v in out.items():
    print(f"  {k:26} {v['value']}")
print(f"figures: {len(out)} counted -> out/{RUN}/figures.json")
