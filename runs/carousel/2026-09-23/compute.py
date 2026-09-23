#!/usr/bin/env python3
"""Every figure this deck draws, EXTRACTED from claims.json rather than typed.

EVERY FIGURE THIS DECK DRAWS IS PULLED OUT OF A CLAIM'S `quote` by a regular expression
anchored on the words around it, so the value on a frame and the value in the source are the
same string by construction. If a quote changes, this raises rather than quietly publishing
yesterday's number.

THE HALT'S DATE COMES FROM c24. The Tribune's quote says the order came "on Monday" and the
story is dated 2026-09-21. The date is read from that claim's `published` field and asserted to
be a Monday, so the day in the quote and the date on the page have to agree or this raises. Both
clocks on frame 7, the 49 and the 28, descend from it.

WHAT THIS FILE REFUSES TO COMPUTE, and the refusals are the argument.

1. NO SHARE OF THE QUEUE IN MEGAWATTS. c8 gives 474 gigawatts of requests and c23 gives
   "approximately 90%" of the NEW requests being data centers. Those are two different denominators,
   the whole queue and the new arrivals, and multiplying them would publish a gigawatt figure
   nobody measured. The two are carried separately, each saying what it counts.

2. NO MEGAWATTS PER ENGINE. 76 MW (c16) over about 40 units (c17) is a division the source
   does not perform, "approximately 40" is not a count, and the quotient would be a per unit
   rating no document states. The engines are drawn as a COUNT and the megawatts as a
   SEPARATE quantity, and nothing on any frame divides one by the other.

3. NO TOTAL OF ANY TWO PROJECTS. This refusal once covered an Odessa supply contract beside
   the Kodiak one. Its claims were fetched from a host whose robots file refuses this fetcher,
   no permitted source was found, and they were dropped on 2026-09-23 with the frame that drew
   them. The refusal stands for the next deck that is tempted to add unlike arrangements.

4. NO COUNT OF PERMITS AFFECTED. The record holds exactly one data center permit by number
   and its program is not established. A deck that counted "the permits this reaches" would
   be publishing the thing the fact check refused.

WHAT IT DOES COMPUTE. Two date spans, from dates that are inside quotes, by the calendar.
"""
import json
import pathlib
import re
from datetime import date

HERE = pathlib.Path(__file__).resolve().parent
doc = json.loads((HERE / "claims.json").read_text(encoding="utf-8"))
C = {c["id"]: c for c in doc["claims"]}

RUN_DATE = date(2026, 9, 23)


def grab(cid, pattern, label):
    m = re.search(pattern, C[cid]["quote"])
    if not m:
        raise SystemExit("compute: %s not found in %s's quote" % (label, cid))
    return m.group(1)


def num(cid, pattern, label):
    return int(grab(cid, pattern, label).replace(",", ""))


# ------------------------------------------------------------------ the queue, as stated
queue_gw = num("c8", r"over ([\d,]+) gigawatts", "474 gigawatts")
peak_multiple = grab("c8", r"more than (five) times", "five times")
dc_share = num("c23", r"Approximately (\d+)% of the new power requests", "90 percent")

# --------------------------------------------------------- the one behind-the-meter project
btm_mw = num("c16", r"(\d+) megawatts of behind-the-meter", "76 megawatts")
btm_units = num("c17", r"approximately (\d+) reciprocating", "about 40 units")
btm_quarter = grab("c18", r"begin in the (fourth) quarter of 2026", "fourth quarter")

# ------------------------------------------------------------------------- the two clocks
# THE HALT'S DATE COMES FROM c24 NOW. The Tribune's quote says the order came "on Monday" and the
# story is dated 2026-09-21. The date is read from the claim's own `published` field and ASSERTED
# to be a Monday, so the day in the quote and the date on the page have to agree or this fails.
_c24 = C["c24"]
assert "on Monday" in _c24["quote"], "c24's quote no longer dates the order"
halt_issued = date.fromisoformat(_c24["published"])
assert halt_issued.weekday() == 0, f"c24 says Monday and {halt_issued} is not one"
# THE AUDIT'S YEAR IS THE HALT'S YEAR, stated rather than typed a second time. c9's quote is
# "ordering ERCOT on Aug. 3", from the Tribune's September 21st account of this year's sequence,
# and it carries the day and not the year. The year is the one date already in the record.
audit_ordered = date(halt_issued.year, 8,
    int(re.search(r"on Aug\. (\d+)", C["c9"]["quote"]).group(1)))
report_back = date(
    int(re.search(r"October \d+, (\d{4})", C["c4"]["quote"]).group(1)), 10,
    int(re.search(r"October (\d+),", C["c4"]["quote"]).group(1)))

days_audit_to_halt = (halt_issued - audit_ordered).days
days_halt_to_report = (report_back - halt_issued).days
days_left_to_report = (report_back - RUN_DATE).days

FIGURES = {
    "_note": ("Every value here is extracted from a claim's verbatim quote by compute.py, which "
              "is executed at build time rather than copied. A numeral in this deck's prose or "
              "artwork that is not in this file is a numeral nothing computed."),

    "queue": {
        "gigawatts": queue_gw, "unit": "GW", "basis": "measured", "from": ["c8"],
        "said_by": "ERCOT, as the Texas Tribune reported it on August 3rd",
        "label": "gigawatts of requests to connect to the Texas grid",
        "peak_multiple_words": peak_multiple,
        "peak_note": ("c8 says more than five times the record peak and gives no peak figure, so "
                      "the multiple is carried AS THE SOURCE'S OWN WORD and no peak is computed "
                      "from it."),
    },
    "data_center_share": {
        "percent": dc_share, "basis": "measured", "from": ["c23"],
        "said_by": "the Governor, as the Texas Tribune reported it on August 3rd",
        "counts": "the NEW power requests, not the whole queue",
        "no_multiply": ("474 GW is the whole queue and 90 percent is of the new requests. Two "
                        "denominators. Nothing here multiplies them and no frame may."),
    },

    "behind_the_meter": {
        "megawatts": btm_mw, "units": btm_units, "quarter_words": btm_quarter,
        "basis": "measured", "from": ["c16", "c17", "c18"],
        "said_by": "Kodiak Gas Services",
        "label": "megawatts a West Texas data center takes without touching the grid",
        "no_division": ("76 over about 40 is a per unit rating no document states, and "
                        "approximately 40 is not a count. Nothing divides these."),
    },
    "clocks": {
        "audit_ordered": audit_ordered.isoformat(),
        "halt_issued": halt_issued.isoformat(),
        "report_back": report_back.isoformat(),
        "days_audit_to_halt": days_audit_to_halt,
        "days_halt_to_report": days_halt_to_report,
        "days_left_to_report": days_left_to_report,
        "basis": "measured",
        "from": ["c9", "c4", "c24"],
        "how": ("The audit date is read out of c9's quote, the report back date out of c4's, and "
                "the halt's date out of c24's published field, asserted to be the Monday c24's "
                "quote names. The spans are calendar differences."),
    },
}

if __name__ == "__main__":
    out = HERE / "figures.json"
    out.write_text(json.dumps(FIGURES, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", out)
    for k in ("queue", "data_center_share", "behind_the_meter", "clocks"):
        print(" ", k, json.dumps({a: b for a, b in FIGURES[k].items()
                                  if isinstance(b, (int, float, str)) and len(str(b)) < 40}))
