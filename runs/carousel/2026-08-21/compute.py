#!/usr/bin/env python3
"""compute.py — every numeral this deck may print that is not quoted from a source.

The law in CLAUDE.md: a numeral reaches published copy in exactly two ways, quoted from a source
or computed by code from the record. This file is the second way. It writes computed.json, and
`numeral_lint` and `aggregate_check` read it.

Nothing here is typed from memory. Every date is named with the claim it comes from, so a reader
of this file can trace any span back to a fetched document, and every span is `date - date`
rather than a number a model counted on its fingers.

It also RE-DERIVES the figures the slide builder emitted and refuses to agree with itself unless
they match. The builder and this file compute the same things from the same table by two paths,
and a run where the two disagree has a defect in one of them.
"""
import json
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent

RUN = date(2026, 8, 21)

# Dates that appear inside verified quotes or their datelines, each with its claim.
AURORA_DFW_HOU = date(2025, 5, 1)    # c23, the Dallas to Houston launch, dated May 1st 2025
AURORA_FTW_ELP = date(2025, 10, 28)  # c27, the Fort Worth to El Paso expansion
DMV_REQUIRED = date(2026, 5, 28)     # c10, the authorization became a live requirement
KODIAK_Q2 = date(2026, 6, 30)        # c16, 35 driverless trucks as of June 30th 2026
AURORA_GEN2 = date(2026, 7, 22)      # c30, the second generation launch
WAYMO_HOUSTON = date(2026, 8, 20)    # c11, Houston opened to anyone with the app
HEARING = date(2026, 8, 25)          # c1 and c36, the Senate Transportation public hearing

SEQ = [AURORA_DFW_HOU, AURORA_FTW_ELP, DMV_REQUIRED, KODIAK_Q2,
       AURORA_GEN2, WAYMO_HOUSTON, HEARING]

gaps = [(SEQ[i + 1] - SEQ[i]).days for i in range(len(SEQ) - 1)]
span_total = (SEQ[-1] - SEQ[0]).days
span_to_auth = (DMV_REQUIRED - AURORA_DFW_HOU).days
tail_days = span_total - span_to_auth
tail_marks = sum(1 for d in SEQ if (d - SEQ[0]).days >= span_to_auth)

# The tally on slide 4. LOADS is the FLOOR c17 states, and the drawing shows exactly that many
# so a reader can count them. The frame's own dek says the record says more.
LOADS = 1400                          # c17, "more than 1,400 loads"

# One claim per charge on the notice, each with its own quoted title, and the pages the
# absence record says it looked at. Both were integer literals, which made the cross check
# below compare two hand typed copies of one number and call the agreement a proof.
CHARGE_CLAIMS = ["c3", "c6", "c7"]

# The site prints the size of this run's verified set on the article page, and that is a
# computed figure like any other. It was reaching the page from len() in the builder and
# was in no run's computed.json, so numeral_lint refused it on a page the run had just
# written. A count of the record is part of the record.
CLAIMS_VERIFIED = len(json.loads((HERE / "claims.json").read_text())["claims"])
ABSENCE_PAGES = json.loads(
    (HERE / "claims.json").read_text())["absences"][0]["looked_at"]
TALLY_GROUPS = LOADS // 5

# Counted out of the committed topojson slide 6 draws from. It shipped as a typed string
# literal in the first render, on the one frame that loads the file it could be counted from.
# Walk up to the repo root rather than counting parents, because this file is read from
# out/<date>/ while the run is live and from runs/carousel/<date>/ once it has shipped, and
# those two sit at different depths.
REL = "assets/geo/tx-counties.topo.json"
TOPO = next(d / REL for d in HERE.parents if (d / REL).exists())
N_COUNTIES = len(json.loads(TOPO.read_text())["objects"]["counties"]["geometries"])

out = {
    "run_date": RUN.isoformat(),
    "source_dates": {
        "aurora_dallas_houston": AURORA_DFW_HOU.isoformat(),
        "aurora_fort_worth_el_paso": AURORA_FTW_ELP.isoformat(),
        "dmv_authorization_required": DMV_REQUIRED.isoformat(),
        "kodiak_q2": KODIAK_Q2.isoformat(),
        "aurora_second_generation": AURORA_GEN2.isoformat(),
        "waymo_houston_open": WAYMO_HOUSTON.isoformat(),
        "hearing": HEARING.isoformat(),
    },
    "gaps_days": gaps,
    "span_first_lane_to_hearing_days": span_total,
    "span_first_lane_to_authorization_days": span_to_auth,
    "tail_window_days": tail_days,
    "marks_in_tail_window": tail_marks,
    "tail_gaps_days": gaps[len(gaps) - (tail_marks - 1):],
    "marker_pads": len(SEQ),
    "lit_prisms": len(SEQ) - 1,
    "tally_marks": LOADS,
    "tally_groups": TALLY_GROUPS,
    "counties": N_COUNTIES,
    "charges_on_the_notice": len(CHARGE_CLAIMS),
    "claims_verified": CLAIMS_VERIFIED,
    "absence_pages": len(ABSENCE_PAGES),
}

# The builder emits the same figures on its own path. If the two ever disagree, one of them is
# wrong and the deck does not get to pick which.
values_path = HERE / "values.json"
if values_path.exists():
    values = json.loads(values_path.read_text(encoding="utf-8"))
    for k, v in values.items():
        if k in out and out[k] != v:
            raise SystemExit(
                "compute.py and the slide builder disagree on %r: %r against %r" % (k, out[k], v))

(HERE / "computed.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
print(json.dumps(out, indent=1))
