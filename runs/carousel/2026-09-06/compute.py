#!/usr/bin/env python3
"""compute.py — every numeral carousel no. 17 puts in front of a reader.

THE LAW THIS FILE EXISTS FOR. No numeral on a slide, in the caption or in the first comment is
ever typed by a person or produced by a language model. It is quoted from a source, or it is
computed here from the claims file, and either way it can be recomputed from the same inputs.

WHAT THIS DECK ACTUALLY COUNTS, and it is one thing. The deck's whole argument turns on the
size of a list. The program publishes a set of requirements a private school must meet, and the
deck says how many there are and what none of them asks about. That count is not quoted
anywhere. It is a COUNT THE DECK COMPUTED over a set of claims, which makes it a fresh factual
assertion in the largest type on the page, and it is exactly the shape of the defect
`aggregate_check` exists for.

So it is counted here, from the claims file, and the claim ids it was counted over are named.

THE TRAP THIS FILE GUARDS, and the fact checker found it rather than the code. The program's
page carries a SECOND list under the same heading, five criteria for a provider of a pre-K or
kindergarten program. A count taken off the page rather than off the four private-school claims
would return nine, and nine would be wrong in a way no gate downstream could see. The count here
is over an explicit, named set of four claim ids and never over the page.

Reads  out/2026-09-06/claims.json
Writes out/2026-09-06/computed.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path

RUN = "2026-09-06"
ROOT = Path(__file__).resolve().parents[2]
CLAIMS = ROOT / "out" / RUN / "claims.json"
OUT = ROOT / "out" / RUN / "computed.json"

# The four private-school requirements, named as claim ids rather than counted off the page.
# See the docstring: the page carries a second list and counting the page returns nine.
REQUIREMENT_CLAIMS = ["c2", "c3", "c4", "c5"]

# The words the deck asserts appear nowhere in the requirements. Held here so the assertion on
# the frame and the test behind it are the same list.
NOT_ASKED_ABOUT = ["curriculum", "instruction", "instructional", "teaching",
                   "teacher", "teachers", "software", "tutor"]


def claims_by_id(doc: dict) -> dict:
    return {c["id"]: c for c in doc["claims"]}


def main() -> int:
    doc = json.loads(CLAIMS.read_text(encoding="utf-8"))
    C = claims_by_id(doc)

    # ---- the count the deck prints ---------------------------------------------------------
    requirements = [C[i] for i in REQUIREMENT_CLAIMS]
    n_requirements = len(requirements)

    # ---- and the assertion made about them, tested rather than asserted ---------------------
    # Every requirement quote is searched for every word the frame says is absent. This is the
    # arithmetic under an ABSENCE, and running it here is what stops the frame from being a
    # sentence nobody checked.
    joined = " ".join(c["quote"].lower() for c in requirements)
    hits = sorted({w for w in NOT_ASKED_ABOUT if re.search(rf"\b{re.escape(w)}\b", joined)})
    assert not hits, f"a requirement quote names {hits}, so the frame's absence claim is false"

    # ---- the transfer, PARSED OUT OF THE QUOTE rather than retyped --------------------------
    # Reading it out of c8's own string is what makes it impossible for the numeral on the frame
    # and the numeral in the claim to drift apart.
    m = re.search(r"\$([\d,]+) per child", C["c8"]["quote"])
    assert m, "c8's quote no longer carries a per child figure in the expected shape"
    per_child_printed = "$" + m.group(1)
    per_child_value = int(m.group(1).replace(",", ""))

    # ---- the school year the transfer belongs to, also parsed -------------------------------
    m2 = re.search(r"for the (\d{4}-\d{2}) school year", C["c8"]["quote"])
    assert m2, "c8's quote no longer names a school year"
    school_year = m2.group(1)

    # ---- the two performance figures the school publishes, parsed from c11 ------------------
    # Neither is this project's number and neither is presented as one. They are quoted so the
    # frame can print them as somebody else's claim and the absence beside them can be exact.
    assert "twice as fast" in C["c11"]["quote"]
    m3 = re.search(r"top (\d+)% nationwide", C["c11"]["quote"])
    assert m3, "c11's quote no longer carries a top percentile in the expected shape"
    top_percentile_printed = "top " + m3.group(1) + "%"

    # ---- the dates, each verbatim in a source, and NO interval between them ------------------
    # An interval is arithmetic and would have to be computed. The deck prints none, so none is
    # computed here, and this comment is the record of that being a decision.
    m4 = re.search(r"opened on ([A-Z][a-z]+ \d{1,2}, \d{4})", C["c7"]["quote"])
    assert m4, "c7's quote no longer carries an opening date"
    application_opened = m4.group(1)

    m5 = re.search(r"(August \d{1,2}-September \d{1,2}, \d{4})", C["c19"]["quote"])
    assert m5, "c19's quote no longer carries the board's meeting span"
    board_met = m5.group(1)

    out = {
        "run": RUN,
        "note": ("Carousel no. 17 prints one computed numeral and every other figure on it is "
                 "quoted. The computed one is the size of the program's private-school "
                 "requirement list, counted over four named claim ids rather than off the page, "
                 "because the page carries a second list under the same heading."),
        "requirements": {
            "count": n_requirements,
            "from_claims": REQUIREMENT_CLAIMS,
            "words_tested_for_and_absent": NOT_ASKED_ABOUT,
            "quotes": [c["quote"] for c in requirements],
        },
        "transfer": {
            "printed": per_child_printed,
            "value": per_child_value,
            "school_year": school_year,
            "from_claim": "c8",
        },
        "school_performance_claim": {
            "rate_phrase": "twice as fast",
            "percentile_printed": top_percentile_printed,
            "from_claim": "c11",
            "sourced_on_its_own_page": False,
            "absence": "a2",
        },
        "dates": {
            "application_period_opened": application_opened,
            "board_met": board_met,
            "intervals_computed": [],
        },
    }
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"computed: {n_requirements} requirement(s) over {REQUIREMENT_CLAIMS}, "
          f"transfer {per_child_printed} for {school_year}, "
          f"{len(NOT_ASKED_ABOUT)} absent word(s) tested and none found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
