#!/usr/bin/env python3
"""compute.py — every numeral carousel no. 15 puts in front of a reader.

THE LAW THIS FILE EXISTS FOR. No numeral on a slide, in the caption or in the first
comment is ever typed by a person or produced by a language model. It is quoted from a
source or it is computed here, from the claims file, and it can be recomputed from the
same inputs. A thousands separator is a computation. A span in days is a computation. A
count over a set is a computation, and the set it counted has to be nameable.

Reads  out/2026-09-04/claims.json
Writes out/2026-09-04/computed.json
"""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

RUN = "2026-09-04"
ROOT = Path(__file__).resolve().parents[2]
CLAIMS = ROOT / "out" / RUN / "claims.json"
OUT = ROOT / "out" / RUN / "computed.json"

TODAY = dt.date(2026, 9, 4)


def claims_by_id() -> dict:
    d = json.loads(CLAIMS.read_text())
    return {c["id"]: c for c in d["claims"]}


def group(n: int) -> str:
    """A thousands separator is a formatting decision made by code, not by a writer."""
    return f"{n:,}"


def months_between(a: dt.date, b: dt.date) -> int:
    return (b.year - a.year) * 12 + (b.month - a.month)


def main() -> int:
    C = claims_by_id()

    # --- the one measured quantity the deck sets against the adjectives -----------------
    # Pulled out of the quoted data row itself rather than retyped, so the numeral on the
    # slide and the numeral in the claim cannot drift apart.
    row = C["c26"]["quote"]
    may_in = int(re.search(r'"value":"(\d+)"', row).group(1))

    # --- the five performance facts the account does not publish -----------------------
    # NAMED, because a bare count over an unnamed set is a number nothing checked. Each
    # entry is one claim that establishes one absence by quoting the nearest thing the
    # page does say.
    absences = [
        ("an accuracy, match or error rate", "c18"),
        ("a count of images captured", "c19"),
        ("a retention period for the images", "c20"),
        ("a decision to deploy", "c21"),
        ("a date range for the assessment", "c22"),
    ]
    asked = len(absences)
    published = 0

    # --- the three characterisations the account DOES publish --------------------------
    # NAMED for the same reason as the absences above. Each is a quoted string the frame
    # seats and attributes, and each is a characterisation rather than a measurement, which
    # is the distinction the frame exists to draw.
    characterisations = [
        ("exceeded expectations, said by CBP's Biometrics Program Office", "c7"),
        ("high-quality facial images, said by the president of NEC NSS", "c9"),
        ("and it did just that, the line that closes the division director's quotation", "c31"),
    ]
    quoted = len(characterisations)

    # --- spans, all inclusive of neither endpoint's arithmetic being done by hand -------
    request = dt.date(2025, 10, 1)          # c2, the month CBP asked
    at_bridge = dt.date(2026, 5, 1)         # c5, the month the partners arrived
    account = dt.date(2026, 9, 1)           # the account's own publication date
    dallas = dt.date(2026, 9, 8)            # c24, MatterAgendaDate

    # --- what the ARTICLE PAGE counts, computed here so it is the run's own figure ----
    # The site's article page prints the number of claims it renders, and `numeral_lint` refused
    # the build because that count came from neither a claim's quote nor this file. It is a real
    # computation over this run's own claims file, so it belongs here rather than in an allow
    # list on the site side, which is the shape `_run_numerals` itself warns about twice.
    claims_blob = json.loads(CLAIMS.read_text(encoding="utf-8"))
    claims_verified = len(claims_blob["claims"])
    findings_rejected = len(claims_blob.get("rejected") or [])

    out = {
        "run": RUN,
        "generated_by": "out/2026-09-04/compute.py",
        "values": {
            "may_inbound_pedestrians": {
                "value": may_in,
                "display": group(may_in),
                "label": "measured",
                "from": ["c26"],
                "means": "pedestrians recorded ENTERING the United States at the Progreso "
                         "port of entry in May 2026. It is not a count of the people the "
                         "cameras watched, who were walking the other way.",
            },
            "outbound_series_months": {
                "value": 0,
                "display": "0",
                "label": "measured",
                "from": ["c25"],
                "means": "months of published federal outbound pedestrian counts at this "
                         "port. The dataset's own description states no comparable data is "
                         "collected on outbound crossings.",
            },
            "performance_facts_asked": {
                "value": asked,
                "display": str(asked),
                "label": "measured",
                "from": [cid for _, cid in absences],
                "means": "performance facts a reader would need, each one established as "
                         "absent by its own claim: " + "; ".join(n for n, _ in absences),
            },
            "characterisations_quoted": {
                "value": quoted,
                "display": str(quoted),
                "label": "measured",
                "from": [cid for _, cid in characterisations],
                "means": "quotations the account publishes about how the test went, each "
                         "one a characterisation rather than a measurement: "
                         + "; ".join(n for n, _ in characterisations),
            },
            "performance_facts_published": {
                "value": published,
                "display": str(published),
                "label": "measured",
                "from": [cid for _, cid in absences],
                "means": "how many of those five the account publishes.",
            },
            "claims_verified": {
                "value": claims_verified,
                "display": str(claims_verified),
                "label": "measured",
                "from": [c["id"] for c in claims_blob["claims"]],
                "means": "claims this run fetched and verified, counted over claims.json. The "
                         "site's article page prints this count beside the list it renders.",
            },
            "findings_rejected": {
                "value": findings_rejected,
                "display": str(findings_rejected),
                "label": "measured",
                "from": [],
                "means": "scout findings the fact check refused, counted over claims.json's "
                         "rejected list. Each carries its own reason in that file.",
            },
            "months_request_to_account": {
                "value": months_between(request, account),
                "display": str(months_between(request, account)),
                "label": "measured",
                "from": ["c2"],
                "means": "whole months from the month CBP asked to the month the account "
                         "published.",
            },
            "months_bridge_to_account": {
                "value": months_between(at_bridge, account),
                "display": str(months_between(at_bridge, account)),
                "label": "measured",
                "from": ["c5"],
                "means": "whole months from the month the partners were at the bridge to "
                         "the month the account published.",
            },
            "days_to_dallas": {
                "value": (dallas - TODAY).days,
                "display": str((dallas - TODAY).days),
                "label": "measured",
                "from": ["c24"],
                "means": "days from this run's date to the Dallas briefing.",
            },
        },
        "absences": [{"what": n, "claim": cid} for n, cid in absences],
        "characterisations": [{"what": n, "claim": cid} for n, cid in characterisations],
    }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    for k, v in out["values"].items():
        print(f"  {k:34s} {v['display']:>10s}  [{v['label']}]  from {','.join(v['from'])}")
    print(f"computed: {len(out['values'])} value(s) -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
