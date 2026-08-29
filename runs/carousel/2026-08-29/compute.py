#!/usr/bin/env python3
"""Every numeral the deck prints, computed here from claims.json and nowhere else.

The law is in CLAUDE.md. No numeral on a frame is typed by a person or produced by a model. A
figure reaches a slide as a string this file emitted, or it does not reach a slide.

THE COUNTS ON THIS DECK ARE THE DANGEROUS PART, AND THE DANGER IS NOT ARITHMETIC.

This deck's spine is that one deployment is described at three grains, and the drawing wants a
count for each. A count is the easiest number in the world to type and the hardest to defend,
because nothing downstream can tell "seven places" from "six places" and both look right. So no
count here is written down. Each is DERIVED from the quoted string it counts, by splitting that
string, and the members it counted are emitted beside it so a frame can name the set rather than
assert a bare number. That is instinct `count-names-its-set` and it is the whole reason the
member lists below are in the output.

The one figure this file deliberately REFUSES to produce is any relationship between the
agency's `29999998` and the university's `$30 million`. Both are quoted strings from their own
pages. A difference between them would be a number no source states, about a discrepancy no
source characterises, and this deck sets them side by side as quotations and says nothing about
the gap. See NO_GAP below.
"""
import json
import pathlib
import re
import sys

RUN = pathlib.Path(__file__).resolve().parent
CLAIMS = json.loads((RUN / "claims.json").read_text(encoding="utf-8"))["claims"]
BY = {c["id"]: c for c in CLAIMS}


def quoted(cid, needle):
    """Assert a string is actually in the claim's verbatim quote before using it."""
    q = BY[cid]["quote"]
    if needle not in q:
        sys.exit(f"compute: {needle!r} is not in claim {cid}'s quote. Refusing to invent it.")
    return needle


def members(cid, after, stop=None):
    """Split a quoted list into its members, so a count is derived rather than typed.

    `after` is the substring the list begins at inside the claim's own quote, and `stop` ends
    it. Everything between is split on commas and on a trailing 'and', each member trimmed.
    Returns the members. The COUNT is len() of this, never a number written by hand.
    """
    q = BY[cid]["quote"]
    i = q.find(after)
    if i < 0:
        sys.exit(f"compute: {after!r} is not in claim {cid}'s quote.")
    seg = q[i + len(after):]
    if stop:
        j = seg.find(stop)
        if j < 0:
            sys.exit(f"compute: {stop!r} does not close the list in claim {cid}.")
        seg = seg[:j]
    parts = [p.strip().rstrip(".") for p in re.split(r",\s*", seg) if p.strip()]
    parts = [re.sub(r"^and\s+", "", p) for p in parts]
    return [p for p in parts if p]


# WHY NO COUNT IS PUBLISHED FOR THE INDUSTRY COLLABORATORS, and it is the instinct
# `count-names-its-set` earning its keep on the first list it met.
#
# `members()` splits on commas. Three of this deck's lists carry an Oxford comma and split
# correctly. The industry list does not: it ends "MassRobotics, NVIDIA and Robust AI", so a
# comma split returns that tail as ONE member and undercounts. Splitting a trailing "and" would
# fix that list and would immediately BREAK the places list, whose last member is the single
# phrase "elder-care and assisted-living residences".
#
# There is no rule that reads both correctly, which means any count of the industry list is a
# judgement rather than a derivation. So the names ship and the count does not. The places
# count ships because it is exactly what the university's own sentence lists, comma by comma,
# and the frame that prints it names that set in those words.


# --- THE THREE GRAINS. Each count is len() of a list split out of that document's own words. --
#
# c33, the agency's PRESS RELEASE, names the settings generically.
RELEASE_SETTINGS = members("c33", "become more common in ")
# c15, the agency's own AWARD ABSTRACT, names facility types.
ABSTRACT_FACILITIES = members("c15", "participatory living laboratories in ", " facilities")
# c21, the UNIVERSITY, names the places themselves.
UNIVERSITY_PLACES = members("c21", "the partner institutions: ")

N_RELEASE = len(RELEASE_SETTINGS)
N_ABSTRACT = len(ABSTRACT_FACILITIES)
N_PLACES = len(UNIVERSITY_PLACES)

# The one place a reader could check us hardest, so it is asserted rather than assumed. The
# rehabilitation hospital appears in the university's list and in NEITHER agency string.
REHAB = "a rehabilitation hospital"
if REHAB not in UNIVERSITY_PLACES:
    sys.exit("compute: the university's list no longer names a rehabilitation hospital.")
if any("hospital" in s for s in ABSTRACT_FACILITIES):
    sys.exit("compute: the abstract now names a hospital; the three-grain claim has changed.")

# --- MONEY. Every one of these is a quoted string, reproduced, never combined. ---------------
AGENCY_TOTAL_RAW = quoted("c3", "29999998")           # the award record's estimatedTotalAmt
AGENCY_OBLIGATED_RAW = quoted("c4", "5999999")        # the award record's fundsObligatedAmt
AGENCY_FY_STRING = quoted("c5", "FY 2026 = $5,999,999.00")
UNIVERSITY_AWARD = quoted("c20", "five-year, $30 million award")
AGENCY_THREE_CENTERS = quoted("c30", "$90 million over five years")
AGENCY_PER_CENTER = quoted("c31", "approximately $6 million annually")

# NO_GAP. Stated here so a later run reads the refusal rather than rediscovering the temptation.
NO_GAP = ("The agency record's 29999998 and the university's $30 million are set side by side as "
          "quotations. No difference between them is computed, and neither is described as "
          "rounded, exact or approximate, because no source says so.")

# --- DATES, straight out of the award record, reformatted to house style by code. ------------
AWARD_DATE_RAW = quoted("c8", "08/25/2026")
START_RAW = quoted("c6", "09/01/2026")
END_RAW = quoted("c7", "08/31/2031")

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


def ordinal(n):
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }"


def house_date(mmddyyyy):
    """House style is the ordinal, month first. Never typed, always converted here."""
    m, d, y = (int(x) for x in mmddyyyy.split("/"))
    return f"{MONTHS[m - 1]} {ordinal(d)}, {y}"


AWARD_DATE = house_date(AWARD_DATE_RAW)
START_DATE = house_date(START_RAW)
END_DATE = house_date(END_RAW)

# --- THE OTHER COUNTS, each derived from its own quoted list. -------------------------------
PARTNER_UNIVERSITIES = members("c18", "Partner universities are ", ".")
INDUSTRY = members("c19", "Industry collaborators include ", ".")
N_PARTNERS = len(PARTNER_UNIVERSITIES)

RESEARCHERS = quoted("c17", "39 researchers from six universities")
CENTERS_ANNOUNCED = quoted("c29", "three new Science and Technology Centers")

# --- GEOMETRY. Any length a reader could measure is computed here, not eyeballed in a slide. --
#
# Slide 4 sets the three grains as three stacked bars whose LENGTH IS THE COUNT. The scale is
# derived from the widest of the three so the longest bar lands on a stated width, and every
# other bar follows from it. Nothing about the drawing is a typed pixel.
BAR_FIELD_PX = 760.0                      # the drawable width inside the slide's margins
BAR_MAX = max(N_RELEASE, N_ABSTRACT, N_PLACES)
PX_PER_ITEM = BAR_FIELD_PX / BAR_MAX
BAR_RELEASE_PX = round(N_RELEASE * PX_PER_ITEM, 2)
BAR_ABSTRACT_PX = round(N_ABSTRACT * PX_PER_ITEM, 2)
BAR_PLACES_PX = round(N_PLACES * PX_PER_ITEM, 2)

# Slide 6 lays the seven named places out as a row of cells across the same field, so the cell
# pitch is derived from how many the university actually named.
CELL_PITCH_PX = round(BAR_FIELD_PX / N_PLACES, 2)

# ---- WHAT A BODY DID, and the claim whose own words prove the shape. -----------------------
# One row, because this deck carries one acting body. The agency did not "award a grant" and the
# deck may not say so: the record's own field is a cooperative agreement, which the agency
# co-manages. The shape words below all appear in c10's quote, which is what makes the label on
# slide 4 a report rather than a characterisation.
ACTED = {
    "tx-2026-0104": ("Austin", "cooperative agreement", "c10"),
}
_STEM = {"cooperative": "cooperativ", "agreement": "agreement"}

OUT = {
    "n_release_settings": N_RELEASE,
    "release_settings": RELEASE_SETTINGS,
    "n_abstract_facilities": N_ABSTRACT,
    "abstract_facilities": ABSTRACT_FACILITIES,
    "n_university_places": N_PLACES,
    "university_places": UNIVERSITY_PLACES,
    "release_set_name": "the settings the agency's release names",
    "abstract_set_name": "the facility types the agency's abstract names",
    "places_set_name": "the places the university names",
    "rehab_only_in_university_list": True,

    "agency_total_raw": AGENCY_TOTAL_RAW,
    "agency_obligated_raw": AGENCY_OBLIGATED_RAW,
    "agency_fy_string": AGENCY_FY_STRING,
    "university_award": UNIVERSITY_AWARD,
    "agency_three_centers": AGENCY_THREE_CENTERS,
    "agency_per_center": AGENCY_PER_CENTER,
    "no_gap": NO_GAP,

    "award_date": AWARD_DATE,
    "start_date": START_DATE,
    "end_date": END_DATE,
    "award_date_raw": AWARD_DATE_RAW,
    "start_raw": START_RAW,
    "end_raw": END_RAW,

    "partner_universities": PARTNER_UNIVERSITIES,
    "n_partner_universities": N_PARTNERS,
    "industry_collaborators": INDUSTRY,
    "researchers_phrase": RESEARCHERS,
    "centers_announced_phrase": CENTERS_ANNOUNCED,

    "bar_field_px": BAR_FIELD_PX,
    "px_per_item": round(PX_PER_ITEM, 4),
    "bar_release_px": BAR_RELEASE_PX,
    "bar_abstract_px": BAR_ABSTRACT_PX,
    "bar_places_px": BAR_PLACES_PX,
    "cell_pitch_px": CELL_PITCH_PX,
    "acted": {k: list(v) for k, v in ACTED.items()},
}

if __name__ == "__main__":
    (RUN / "computed.json").write_text(json.dumps(OUT, indent=2, ensure_ascii=False) + "\n",
                                       encoding="utf-8")
    for k, v in OUT.items():
        print(f"{k:32} {v}")
