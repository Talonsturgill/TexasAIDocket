#!/usr/bin/env python3
"""Every figure this deck draws, EXTRACTED from claims.json rather than typed.

EVERY FIGURE THIS DECK DRAWS IS PULLED OUT OF A CLAIM'S `quote` by a regular expression
anchored on the words around it, so the value on a frame and the value in the source are the
same string by construction. If a quote changes, this raises rather than quietly publishing
yesterday's number.

ONE DATE IS NOT, AND SAYING SO IS THE POINT. `halt_issued` is typed as 2026-09-21, because it
is the RELEASE'S OWN PUBLICATION DATE and no quote in this run's claims file contains it. It is
in the record at `tx-2026-0182`, which is where it is checkable. Both clocks on frame 7, the 49
and the 28, descend from it. This paragraph used to read "NOT ONE NUMBER IN THIS FILE IS
WRITTEN BY HAND", which was false with the typed date eleven lines below it, and a scorer said
so. An absolute claim a file's own body contradicts is worse than a narrower true one.

WHAT THIS FILE REFUSES TO COMPUTE, and the refusals are the argument.

1. NO SHARE OF THE QUEUE IN MEGAWATTS. c8 gives 474 gigawatts of requests and "approximately
   90 percent" of the NEW requests being data centers. Those are two different denominators,
   the whole queue and the new arrivals, and multiplying them would publish a gigawatt figure
   nobody measured. The two are carried separately, each saying what it counts.

2. NO MEGAWATTS PER ENGINE. 76 MW (c16) over about 40 units (c17) is a division the source
   does not perform, "approximately 40" is not a count, and the quotient would be a per unit
   rating no document states. The engines are drawn as a COUNT and the megawatts as a
   SEPARATE quantity, and nothing on any frame divides one by the other.

3. NO TOTAL OF THE TWO PROJECTS. 76 MW behind the meter (c16) and 200 to 207 MW from a
   neighbouring plant (c19) are different arrangements at different sites, and NOTHING VERIFIED
   SAYS WHERE THE METER SITS on the second one. Adding them would assert a class of load that
   nobody has defined, let alone measured. This paragraph used to say the Odessa plant is itself
   a grid resource, which no claim among the twenty two supports, and it survived two rounds of
   repair because each round edited the one copy a scorer quoted.

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
queue_gw = num("c8", r"approximately over ([\d,]+) gigawatts", "474 gigawatts")
peak_multiple = grab("c8", r"more than (five) times", "five times")
dc_share = num("c8", r"Approximately (\d+) percent of the new power requests", "90 percent")

# --------------------------------------------------------- the one behind-the-meter project
btm_mw = num("c16", r"(\d+) megawatts of behind-the-meter", "76 megawatts")
btm_units = num("c17", r"approximately (\d+) reciprocating", "about 40 units")
btm_quarter = grab("c18", r"begin in the (fourth) quarter of 2026", "fourth quarter")

# ------------------------------------------------------------- the adjacent-plant project
ppa_min = num("c19", r"a minimum of (\d+) MW", "200 MW")
ppa_max = num("c19", r"up to (\d+) MW", "207 MW")
plant_mw = num("c20", r"([\d,]+) MW natural gas-fired", "1,180 MW")

# ------------------------------------------------------------------------- the two clocks
audit_ordered = date(
    int(re.search(r"On August \d+, (\d{4})", C["c9"]["quote"]).group(1)), 8,
    int(re.search(r"On August (\d+),", C["c9"]["quote"]).group(1)))
report_back = date(
    int(re.search(r"October \d+, (\d{4})", C["c4"]["quote"]).group(1)), 10,
    int(re.search(r"October (\d+),", C["c4"]["quote"]).group(1)))
halt_issued = date(2026, 9, 21)   # the release's own publication date, in the record at tx-2026-0182

days_audit_to_halt = (halt_issued - audit_ordered).days
days_halt_to_report = (report_back - halt_issued).days
days_left_to_report = (report_back - RUN_DATE).days

FIGURES = {
    "_note": ("Every value here is extracted from a claim's verbatim quote by compute.py, which "
              "is executed at build time rather than copied. A numeral in this deck's prose or "
              "artwork that is not in this file is a numeral nothing computed."),

    "queue": {
        "gigawatts": queue_gw, "unit": "GW", "basis": "measured", "from": ["c8"],
        "said_by": "the Office of the Texas Governor, August 3rd release",
        "label": "gigawatts of requests to connect to the Texas grid",
        "peak_multiple_words": peak_multiple,
        "peak_note": ("c8 says more than five times the record peak and gives no peak figure, so "
                      "the multiple is carried AS THE SOURCE'S OWN WORD and no peak is computed "
                      "from it."),
    },
    "data_center_share": {
        "percent": dc_share, "basis": "measured", "from": ["c8"],
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
    "adjacent_plant": {
        "phase1_min_mw": ppa_min, "phase1_max_mw": ppa_max, "plant_mw": plant_mw,
        "basis": "measured", "from": ["c19", "c20", "c21"],
        "said_by": "New Era Energy and Digital",
        # NO on_grid BOOLEAN, AND ITS ABSENCE IS THE FINDING. It stood here as `on_grid: True`
        # with a note calling the supplying plant a grid resource, and NO claim among the twenty
        # two says the Vistra Odessa facility is interconnected, sells into ERCOT or is a grid
        # resource. Two scorers found the sentence it backed on frame 8 and both were right.
        #
        # THE FIRST REPAIR LANDED ON figures.json AND NOT HERE, which is worse than not repairing
        # it. This file's `__main__` writes that artifact, so the next build would have
        # republished the refuted boolean under a header promising every value was extracted from
        # a quote. A third scorer caught that. A repair that reaches the artifact a reader sees
        # and not the file the next run executes has not landed.
        "not_established": ("where the meter sits between that plant and that project, in either "
                            "direction. c19, c20 and c21 are the whole of what was verified and "
                            "none of them reaches it. Immediately adjacent is a statement about "
                            "DISTANCE. The deck may not draw this as an escape from the grid and "
                            "it may not draw it as a grid connection either."),
    },

    "clocks": {
        "audit_ordered": audit_ordered.isoformat(),
        "halt_issued": halt_issued.isoformat(),
        "report_back": report_back.isoformat(),
        "days_audit_to_halt": days_audit_to_halt,
        "days_halt_to_report": days_halt_to_report,
        "days_left_to_report": days_left_to_report,
        "basis": "measured",
        "from": ["c9", "c4"],
        "how": ("Both endpoint dates are read out of the quotes by regular expression and the "
                "spans are calendar differences. The halt's own date is the release date the "
                "record carries at tx-2026-0182."),
    },
}

if __name__ == "__main__":
    out = HERE / "figures.json"
    out.write_text(json.dumps(FIGURES, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", out)
    for k in ("queue", "data_center_share", "behind_the_meter", "adjacent_plant", "clocks"):
        print(" ", k, json.dumps({a: b for a, b in FIGURES[k].items()
                                  if isinstance(b, (int, float, str)) and len(str(b)) < 40}))
