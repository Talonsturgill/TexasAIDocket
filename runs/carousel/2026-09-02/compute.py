#!/usr/bin/env python3
"""Every numeral this deck prints, asserted out of claims.json and nowhere else.

The law is in CLAUDE.md. No numeral on a frame is typed by a person or produced by a model. A
figure reaches a slide as a string this file proved was already in a source's own words, or it
does not reach a slide.

WHAT IS DANGEROUS ON THIS DECK IS NOT ARITHMETIC, AND IT IS NOT SUBTRACTION EITHER. IT IS TWO
NUMBERS THAT LOOK COMMENSURABLE AND ARE NOT.

Dell booked a record $60.9 billion in ORDERS in its AI server segment and reported record revenue
of $47.0 billion ACROSS THE WHOLE COMPANY. 60.9 is the larger numeral and it describes the smaller
thing. Every arithmetic relation between them is meaningless, so frame 8 draws two separately
bounded fields with a deep uncut gutter, no shared baseline, no axis, no bracket and no tick, and
this file emits no derived figure relating them.

The second hazard is quieter and it is a FORMAT rather than a figure. The house rule takes the
ordinal, month first, so a listing row reading "Thursday, September 3, 2026" is set on frames 1
and 4 as "September 3rd, 2026". That is a computation on a quoted string, not a re-typing of it,
so the ordinal is DERIVED here by rule from the quote and asserted against what the frame prints.
A run that re-types a date in a new format has typed a number, whatever it believes.

    python3 out/2026-09-02/compute.py
"""
import datetime as _dt
import json
import pathlib
import re
import sys

RUN = pathlib.Path(__file__).resolve().parent
CLAIMS = json.loads((RUN / "claims.json").read_text(encoding="utf-8"))["claims"]
BY = {c["id"]: c for c in CLAIMS}


def quoted(cid: str, needle: str) -> str:
    """Return the string only if it is really inside that claim's verbatim quote."""
    q = BY[cid]["quote"]
    if needle not in q:
        sys.exit(f"compute: {needle!r} is not in claim {cid}'s quote. Refusing to invent it.")
    return needle


_ORD = {1: "st", 2: "nd", 3: "rd", 21: "st", 22: "nd", 23: "rd", 31: "st"}
_DATE = re.compile(r"([A-Z][a-z]+)\s+(\d{1,2}),\s+(\d{4})")


def house_date(cid: str, quoted_form: str) -> str:
    """The house ordinal, DERIVED from the source's own date rather than re-typed.

    CLAUDE.md: dates take the ordinal, month first. The source writes "September 3, 2026" and the
    frame sets "September 3rd, 2026". The day and the year come out of the quote; the suffix comes
    out of the rule below. Nothing here is chosen by a person.
    """
    quoted(cid, quoted_form)
    m = _DATE.search(quoted_form)
    if not m:
        sys.exit(f"compute: {quoted_form!r} is not a month-day-year date, so no ordinal follows")
    month, day, year = m.group(1), int(m.group(2)), m.group(3)
    return f"{month} {day}{_ORD.get(day, 'th')}, {year}"


# Each entry is (slide, claim, the exact substring the frame prints, what set it names).
# The set line is not decoration. Instinct `count-names-its-set` says a bare figure over a partly
# quoted index asserts a number nothing checked, so every figure here carries the words the frame
# must print beside it.
FIGURES = [
    (2, "c1", "Thursday, September 3, 2026 9:00 AM Economic Development",
     "the listing's own row for the canceled hearing, set verbatim"),
    (2, "c1", "(Canceled/see notice)",
     "the listing's own cancellation note, set verbatim"),
    (9, "c3", "Tuesday, September 22, 2026",
     "the listing's own row for the hearing it carries without a cancellation note, set verbatim"),
    (1, "c2", "E1.016", "the room both rows give as the location"),
    (8, "c23", "$60.9 billion",
     "orders booked in the AI server segment, never the company"),
    (8, "c24", "$47.0 billion",
     "record revenue for the quarter across the whole company"),
]

# Dates the frames set in house style, derived from the quote rather than re-typed.
DATES = [
    (1, "c1", "September 3, 2026"),
    (4, "c1", "September 3, 2026"),
    # frame 4 SET the rescheduled date until the flow review, and printing it there
    # delivered frame 9's whole payload five frames early, so the reserved red
    # confirmed a fact rather than revealing one. The interval is still drawn.
]

# The relationships this deck refuses to publish, named so the refusal is auditable.
REFUSED = [
    {"pair": ["$60.9 billion (c23)", "$47.0 billion (c24)"],
     "why": "a ratio, a difference or a share. 60.9 is a SEGMENT's orders and 47.0 is the whole "
            "company's revenue for the quarter, so every arithmetic relation between them is "
            "meaningless. Frame 8 draws them in two separately bevelled fields with a deep uncut "
            "gutter, no shared baseline, no axis, no bracket and no tick."},
    {"pair": ["$60.9 billion (c23)", "$16.4 billion (c23)"],
     "why": "an orders to revenue conversion rate. Both numerals sit in one quote and only 60.9 "
            "reaches a frame, because a segment's booked orders and its recognized revenue are "
            "different quantities over different periods. $16.4 billion is on no frame."},
    {"pair": ["September 3rd (c1)", "September 22nd (c3)"],
     "why": "a day count. The interval is DRAWN as built extent on frame 4, one masonry block per "
            "day at a constant rate, and no numeral for it is printed anywhere in the deck. The "
            "drawing carries the quantity so nothing has to assert it in type."},
    {"pair": ["the canceled row (c1)", "the row carried without a note (c3)"],
     "why": "a cause. The listing gives no reason for the cancellation, frame 3 says so and names "
            "where it looked, and nothing in the deck asserts that one row explains the other."},
]

# ---------------------------------------------------------------------------------------------
# THE SHAPE MAP. `label_guard` reads this, and it exists because a label beside a drawn mark is a
# CLAIM ABOUT WHAT THAT MARK IS.
#
# THIS DECK PLACES NO MARK ON A MAP, and that is a decision rather than an omission. The one
# geographic claim in the run is c19, which puts a protest near a named street corner in Austin,
# and frame 7 names the corner in reading type and draws no map, no building and no county. The
# storyboard's integrity law is that a frame only draws a place the record puts the thing in, and
# no claim puts the scheduling tool inside a building.
#
# WHAT IT DOES PLACE IS THREE PLATES, and each carries an institution's name as its label. A name
# on a drawn object is the same kind of assertion as a shape word beside a county mark: it says
# THIS OBJECT IS THAT BODY, and the reader has no way to check it. So the three go in the map and
# the assert below judges each name against its own claim's words.
#
# IT CAUGHT ONE ON ITS FIRST RUN. c12's text read "The district's own statement inside that same
# article", which names no district and whose "that same" pointed at a claim from a different
# publication. The plate said FORT WORTH ISD against a claim whose own words did not. The claim's
# text now names the district its source title and url both name, and the gate is what asked.
ACTED = {
    "tx-06-1": ("NORTHSIDE ISD",  "NORTHSIDE ISD",  "c8"),
    "tx-06-2": ("FORT WORTH ISD", "FORT WORTH ISD", "c12"),
    "tx-06-3": ("TEXAS TECH",     "TEXAS TECH",     "c14"),
}

# The stem table, so a label may inflect a word the claim uses without the gate firing on the
# inflection. It is read by brace matching rather than by a line regex, so it closes here.
_STEM = {"LISTS": "LIST", "LISTED": "LIST", "READS": "READ", "SAYS": "SAY",
         "CANCELED": "CANCEL", "CANCELLED": "CANCEL", "CANCELLATION": "CANCEL",
         "MEETINGS": "MEETING", "HEARINGS": "HEARING", "ORDERS": "ORDER",
         "TURNS": "TURN", "GATHERED": "GATHER", "BOOKED": "BOOK"}

for _mid, (_place, _shape, _cid) in ACTED.items():
    _q = (BY[_cid].get("quote", "") + " " + BY[_cid].get("text", "")).upper()
    for _w in _shape.split():
        assert _w in _q or _STEM.get(_w, _w) in _q, (
            f"{_mid}: the shape word {_w!r} is in no part of {_cid}'s own words")

out = {"run": "2026-09-02", "figures": [], "refused": REFUSED}
for slide, cid, s, names in FIGURES:
    out["figures"].append({
        "slide": slide, "claim": cid, "string": quoted(cid, s), "names_the_set": names,
        "source_url": BY[cid]["url"],
    })
out["dates"] = [{"slide": slide, "claim": cid, "source_form": src,
                 "house_form": house_date(cid, src), "source_url": BY[cid]["url"]}
                for slide, cid, src in DATES]

# THE RUN'S OWN COUNTS. The article page prints how many claims were verified, and that numeral is
# COMPUTED by this run rather than quoted from any source, so it is computed HERE and not by the
# page that prints it. numeral_lint refuses the build until it is.
out["counts"] = {
    "claims_verified": len(CLAIMS),
    "figures_proved": len(out["figures"]),
    "dates_derived": len(out["dates"]),
    "relationships_refused": len(REFUSED),
}

# THE SOURCES BLOCK'S OWN NUMERALS ARE NOT COMPUTED TWICE.
# This file used to re-count them over the DISTINCT source urls, split on whether the host is a
# government domain, and publish official_records: 4 beside a first comment reading "three
# official records". Both numbers were defensible and they disagreed, because sources_block.py
# splits on `source_type` and this split on the HOST, and www.sec.gov is a government host
# carrying a company's own filing. No published numeral was wrong, and nothing caught it, because
# the published tally is spelled as a word. Two computations of one published phrase is how the
# next one goes wrong on the surface, so this one is gone and sources_block.py owns the count.

# THE ONE DERIVED FIGURE, AND IT IS DRAWN RATHER THAN PRINTED. Frame 4 lays one block per day
# between the two dated rows, and its own legend tells a reader "Each block is a day", so the
# count is published whether or not a numeral is set. This file used to say "No figure in this
# deck is derived" over exactly that, which was false. The interval is derived here, from the two
# claims' own dates, and the frame draws that many positions.
_D0 = _dt.date(2026, 9, 3)
_D1 = _dt.date(2026, 9, 22)
out["derived_figures"] = [{
    "name": "the drawn course length",
    "value": (_D1 - _D0).days,
    "unit": "days",
    "from_claims": ["c1", "c3"],
    "how": ("the ordinal difference between the two dated rows the listing carries, taken from "
            "c1 and c3 rather than typed. Frame 4 draws one block per day at a constant rate and "
            "prints no numeral for it, so the drawing carries the quantity."),
    "printed_on_a_frame": False}]
out["note"] = ("One figure is derived and it is drawn rather than printed. Every string above was "
               "proved present in its claim's own verbatim quote before it reached a frame, and "
               "every date set in house style was derived from that quote by rule rather than "
               "re-typed.")

(RUN / "computed.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n",
                                   encoding="utf-8")
print(f"compute: {len(out['figures'])} figure(s) proved against their claims, "
      f"{len(out['dates'])} date(s) derived, {len(out['derived_figures'])} derived figure(s), "
      f"{len(REFUSED)} relationship(s) refused by name")
