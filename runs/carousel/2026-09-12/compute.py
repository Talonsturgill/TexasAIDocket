#!/usr/bin/env python3
"""compute.py — every numeral and every measurable length in carousel no. 22.

THE LAW. No numeral this project publishes is typed by a person or produced by a language model.
Arithmetic, unit conversion, percentages, ratios, deltas, rankings, date maths and rounding all
happen here, and the frames read `computed.json` through `inject_computed.py`.

THE INSTINCT, broader than the law and carried at 0.80 in `ledger/carousel/instincts.json`. Any
position or length a reader could MEASURE goes through here, not only the ones that carry a
printed number.

WHERE EACH VALUE COMES FROM. Every figure below is lifted OUT OF A VERIFIED CLAIM QUOTE by a
regular expression, or computed from two of them, or read out of the committed source snapshots
in `sources/`, which are the bytes actually fetched on 2026-09-12. Nothing is retyped from a
screen. `pull()` raises rather than falling back, so a claim whose wording changes breaks the
build instead of silently publishing a stale number.

ONE FIGURE IS DELIBERATELY ABSENT. The university's release carries "more than 428,000 vehicle
interactions per year". The claims file rejects it on meaning rather than on sourcing: the
release defines no unit, names no source, and the figure does not survive being set beside the
same release's own lane mile count. It is not computed here and no frame may print it.
"""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOC = json.loads((HERE / "claims.json").read_text(encoding="utf-8"))
CLAIMS = {c["id"]: c for c in DOC["claims"]}
RUN_DATE = dt.date(2026, 9, 12)


def q(cid: str) -> str:
    """The verified quote for a claim, whitespace normalised. Raises on an unknown id."""
    return re.sub(r"\s+", " ", CLAIMS[cid]["quote"]).strip()


def pull(cid: str, pattern: str, label: str) -> str:
    """Lift a substring out of a claim's own quote. Raises rather than falling back."""
    m = re.search(pattern, q(cid))
    if not m:
        raise SystemExit(
            f"compute.py: {label} is no longer in {cid}'s quote. The quote reads:\n  {q(cid)}\n"
            f"Fix the claim or fix this pattern. Do NOT retype the value here.")
    return m.group(1)


def ordinal(d: dt.date) -> str:
    """House style. Month first, with the ordinal. 'September 24th'."""
    n = d.day
    suf = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{d:%B} {n}{suf}"


def main() -> None:
    C: dict[str, object] = {}

    # ---------------------------------------------------------------- the network's size
    # The university's own figure, and the two federal totals it sits between. The deck prints
    # all three side by side rather than picking one, because they count different things and
    # saying so is the honest move. c12 and c13 are HM-60 table rows, so the figure taken is the
    # LAST field of the row, which the table's own header calls TOTAL LANE MILES.
    C["lane_miles_university"] = pull("c2", r"([\d,]+) lane miles", "the university's lane miles")
    C["lane_miles_fed_2024"] = q("c12").rstrip().split("|")[-1].strip()
    C["lane_miles_fed_2023"] = q("c13").rstrip().split("|")[-1].strip()

    # The ORDER of the three, computed rather than asserted, because the deck says the
    # university's figure sits between the two federal years and that is a comparison.
    as_int = lambda s: int(s.replace(",", ""))
    lo, mid, hi = (as_int(C["lane_miles_fed_2023"]), as_int(C["lane_miles_university"]),
                   as_int(C["lane_miles_fed_2024"]))
    C["university_sits_between"] = bool(lo < mid < hi)
    if not C["university_sits_between"]:
        raise SystemExit("compute.py: the three lane mile figures no longer order as the deck says.")

    # ---------------------------------------------------------------- the score
    C["good_score"] = pull("c9", r"score of (\d+) or above", "the good or better threshold")

    # ---------------------------------------------------------------- the measured results
    C["map50_low"] = pull("c18", r"ranging from (\d+\.\d+) to", "the low mAP50")
    C["map50_high"] = pull("c18", r"ranging from [\d.]+ to (\d+\.\d+)", "the high mAP50")
    C["f1_unet"] = pull("c19", r"improved F1 from (\d+\.\d+) to", "U-Net's F1")
    C["f1_model"] = pull("c19", r"improved F1 from [\d.]+ to (\d+\.\d+)", "the model's F1")
    C["f1_thin_unet"] = pull("c20", r"with F1 from (\d+\.\d+) to", "U-Net's thin crack F1")
    C["f1_thin_model"] = pull("c20", r"with F1 from [\d.]+ to (\d+\.\d+)", "the model's thin crack F1")

    # The two gains, computed, and the fact that the thin crack gain is the larger one. The deck
    # asserts that ordering, so the ordering is computed and the build breaks if it flips.
    gain_all = round(float(C["f1_model"]) - float(C["f1_unet"]), 3)
    gain_thin = round(float(C["f1_thin_model"]) - float(C["f1_thin_unet"]), 3)
    C["f1_gain"] = f"{gain_all:.3f}"
    C["f1_thin_gain"] = f"{gain_thin:.3f}"
    C["thin_gain_is_larger"] = bool(gain_thin > gain_all)
    if not C["thin_gain_is_larger"]:
        raise SystemExit("compute.py: the thin crack gain is no longer the larger one.")

    # The bar lengths frames draw for those two pairs, in px, so no frame reasons about a length.
    # A bar is BAR_PX long at F1 1.000 and every bar below is that fraction of it.
    BAR_PX = 620
    for k in ("f1_unet", "f1_model", "f1_thin_unet", "f1_thin_model"):
        C[f"bar_{k}"] = round(float(C[k]) * BAR_PX)
    C["bar_full_px"] = BAR_PX

    # ---------------------------------------------------------------- the dates
    # The commission's remaining meetings, read out of c25's own run of table cells, and the
    # first that falls after the run date. Nothing about which meeting is next is typed.
    cells = re.findall(r"(\d{2})/(\d{2})/(\d{2}) \((\d{1,2}):(\d{2}) ([ap])\.m\.\)", q("c25"))
    if not cells:
        raise SystemExit("compute.py: c25 no longer carries a run of commission meeting cells.")
    meetings = []
    for mm, dd, yy, hh, mi, ap in cells:
        h = int(hh) % 12 + (12 if ap == "p" else 0)
        meetings.append((dt.date(2000 + int(yy), int(mm), int(dd)), h, int(mi)))
    meetings.sort()
    ahead = [m for m in meetings if m[0] > RUN_DATE]
    if not ahead:
        raise SystemExit("compute.py: every commission meeting on the calendar has passed.")
    nxt, hour, minute = ahead[0]
    C["commission_date"] = ordinal(nxt)
    C["commission_time"] = f"{hour if hour <= 12 else hour - 12} {'in the morning' if hour < 12 else 'in the afternoon'}"
    C["commission_days_away"] = (nxt - RUN_DATE).days
    C["commission_meetings_left"] = len(ahead)
    # The agenda posts this many days before it, from c24's own words, which spell the number.
    WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
             "eight": 8, "nine": 9, "ten": 10}
    C["agenda_lead_days"] = WORDS[pull("c24", r"posted (\w+) days prior", "the agenda lead")]
    C["agenda_posts_on"] = ordinal(nxt - dt.timedelta(days=C["agenda_lead_days"]))
    C["agenda_already_due"] = bool((nxt - dt.timedelta(days=C["agenda_lead_days"])) <= RUN_DATE)

    # The item's own date, from the docket entry this deck is built on.
    # The same numbers as words, because a bare digit inside running prose on a frame reads as
    # a figure the reader should weigh and these two are just counts of days and meetings.
    NUM = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
           8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}
    C["agenda_lead_words"] = NUM[C["agenda_lead_days"]]
    C["commission_meetings_left_words"] = NUM[C["commission_meetings_left"]]

    C["item_date"] = ordinal(dt.date(2026, 8, 24))
    C["run_date"] = ordinal(RUN_DATE)

    # ---------------------------------------------------------------- the team
    # Five names across two quotes, counted rather than typed. c3 names the two leads and c28
    # names the three others, so the count is the sum of two regex results over claim quotes.
    # \w is unicode aware, which the first draft of this pattern was not: it spelled out an
    # accent list and lost Jelena Tesic on the one letter the list happened to miss.
    NAME = r"([A-Z]\w+ [A-Z]\w+), Ph\.D\."
    leads = re.findall(NAME, q("c3"))
    others = re.findall(NAME, q("c28"))
    C["team_leads"] = len(leads)
    C["team_others"] = len(others)
    C["team_total"] = len(leads) + len(others)
    if C["team_total"] != 5:
        raise SystemExit(
            f"compute.py: the team count came out at {C['team_total']} rather than five. "
            f"leads={leads} others={others}. Fix the pattern, never the number.")

    # ---------------------------------------------------------------- the deck itself
    C["deck_no"] = 22
    C["slides"] = 9
    C["counters"] = [f"{i:02d} / {C['slides']:02d}" for i in range(1, C["slides"] + 1)]

    (HERE / "computed.json").write_text(json.dumps(C, indent=1, ensure_ascii=False) + "\n")
    for k, v in C.items():
        print(f"  {k:28} {v}")


if __name__ == "__main__":
    main()
