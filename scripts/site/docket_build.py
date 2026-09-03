#!/usr/bin/env python3
"""docket_build.py — the docket's schema, its gates, and the projection the site renders from.

WHY THIS FILE EXISTS

The docket is the thing this whole project is for: a public record of AI decisions in Texas that
a reader can check. Its value is entirely in being right, so the schema is enforced in code and
the gates are hard fails rather than warnings.

The four gates, and what each one is actually protecting:

  1 SCHEMA      shape, enums and required fields. Catches a malformed item before it renders.
  2 CLAIMS      every factual assertion traces to a fetched source AND carries a verbatim quote.
                This is what makes "if it is not in the claims file, it does not exist" real.
  3 NUMERALS    no numeral appears in reader copy unless it appears in a claim's verbatim quote.
                This is the compute-not-generate law at the docket layer. A model that writes
                "about 8.9 gigawatts" into a summary fails the build.
  4 NARRATION   reader copy never talks about the machine that produced it, and never uses first
                person. The record describes the world; it does not narrate its own work.

Plus two freshness gates:

  5 STALENESS   two bands, matching the selector's own two day leash. Past 2 days an item is
                due for a re-check; past 6 it is a HARD
                FAIL, because publishing a four month old item as current is a false claim.
  6 DEADLINES   close dates must parse. Whether a window is OPEN is never stored, it is derived
                from the date on every build, so it cannot rot between runs.

NOTHING HERE WAITS ON SOMEONE TO READ A REPORT. The gates are the reviewer: an item enters the
public record when it passes them and stays out when it does not. That is why a warning nobody
would read is either promoted to a failure or replaced by derived state.

    docket_build.py --self-test              prove every gate can go red
    docket_build.py --validate               run the gates against ledger/docket.json
    docket_build.py --promote SEED           admit and append what passes atomically
    docket_build.py --project                emit the render projection to stdout

EXIT CODES
    0  clean            1  a gate failed            2  the tool itself broke
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "ledger" / "docket.json"

# The house rules live with the caption linter, because they govern every surface and that is
# where they were first written down. Imported once at module scope rather than inside the gate:
# an insert per call left one duplicate path entry per invocation, and it also hid the
# dependency from the wiring gate, which reads imports.
sys.path.insert(0, str(REPO_ROOT / "scripts" / "carousel"))
import caption_check                                               # noqa: E402

# EVERY FIELD AN ITEM MUST CARRY. Named rather than written inline in the validator, because
# `schema_contract.py` checks the record's shape against this exact list. Two copies of a
# required-field list is one of them going stale, and the stale one is always the check.
REQUIRED_FIELDS = ("id", "title", "summary", "topic", "decider", "geography",
                   "status", "key_dates", "public_access", "claims", "last_verified")

# THE VERSION OF THE RECORD'S SHAPE, AND THE RULE THAT GOVERNS IT.
#
# `ledger/docket.json` is the record, and ten modules here parse it. The site build, this
# build, the calendar, the map, the staleness gate and the four ask builders among them. A
# version number is the only way a reader of the shape can tell whether its parser still
# works, and it is worse than useless if nothing obliges it to move: a number that asserts
# stability nothing is tracking leaves a caller more confident and no safer.
#
# It said "published as open data under CC BY and meant to be parsed by other people" until
# 2026-08-23, when the record stopped being published as a file. The rule below did not change
# with that, because the callers that would break are the ones that were always here.
#
# **BREAKING, so this must rise:**
#   - a field in REQUIRED_FIELDS is removed, or stops being required
#   - any published field changes type
#   - a value is removed from TOPICS, STATUSES or ROOMS
#
# **NOT BREAKING, so this stays put:**
#   - a new field is added, anywhere
#   - a value is ADDED to TOPICS, STATUSES or ROOMS. A consumer switching on the values it
#     knows still works and simply meets one it does not. Bumping for every new beat would
#     make the number rise so often that nobody would read it, which costs more than it buys.
#     (Owner's call, 2026-08-20.)
#
# An integer and not semver, on the same call. `_spec.generated` already answers "did the
# content change", so this has exactly one question left to answer, which is "will my code
# still work". An integer answers it, and a minor and patch split only earns its keep beside
# a changelog people actually follow.
#
# `scripts/site/schema_contract.py` enforces all of the above against
# `config/schema_contract.json`, so this constant cannot be a promise nobody keeps.
# VERSION 2, 2026-09-03. `geography.on_ercot` widened from a boolean to a boolean or null, and
# the reason is a defect a review bot found on PR 252 rather than a new beat.
#
# The field had two states and the record has three. `tx-2026-0118` is a federal request for
# comment on derivatives with compute as the underlier. It is nationwide, it concerns a market
# rather than a facility, and it names no state, so it is neither on the ERCOT grid nor off it.
# Stored `false`, the site printed a reader a plain "No. It sits outside the ERCOT
# interconnection", which is a confident answer to a question that does not apply.
#
# So `false` was carrying two meanings, "measured to be off ERCOT" and "the question does not
# apply here", and only the first is something this project can stand behind. Null is the third
# state and the page suppresses the question rather than answering it wrongly. That is the same
# rule the compute-not-generate law states for numerals, applied to a flag: where it is neither
# measured nor modelled, it is not published.
#
# A consumer reading this field must now handle null. That is a break, it is deliberate, and the
# version is what says so out loud.
SPEC_VERSION = 2

# --------------------------------------------------------------------------- vocabularies
# Deliberately closed sets. An open vocabulary drifts, and a drifted topic list silently
# breaks every per-topic view and every dedupe check that depends on it.

TOPICS = {
    "data-centers",
    "power-and-the-grid",
    "state-policy",
    "land-water-and-permitting",
    "defense-and-federal",
    "research-and-science",
    "health-and-education",
    "surveillance-and-policing",
}

DECIDER_TYPES = {
    "state-agency", "legislature", "governor", "county", "city",
    "school-district", "court", "federal", "special-district",
}

STATUSES = {"open", "pending", "decided", "withdrawn", "unknown"}

# The four rooms. This taxonomy is the product: it answers "can a Texan still act on this, how,
# and by when" in one field, and it refuses to leave the question unanswered.
ROOMS = {
    "open_comment",   # a formal comment window is open and has a close date
    "open_meeting",   # a public meeting or hearing where testimony is possible
    "contact_only",   # no formal process, but the decider is identified and reachable
    "closed",         # decided, or no public participation mechanism exists
}

DATE_KINDS = {
    "filed", "introduced", "passed", "signed", "effective", "ordered", "hearing",
    "comment_opens", "comment_closes", "decided", "statutory_deadline", "expires",
    "withdrawn",
}

SOURCE_TYPES = {"primary_official", "primary_corporate", "journalism"}

CONFIDENCES = {"high", "medium", "low"}

# --------------------------------------------------------------------------- copy rules

# Fields a reader actually sees. The numeral and narration gates apply to these and only these:
# a claim's verbatim quote is the source's words and must never be rewritten to satisfy a linter.
READER_COPY_FIELDS = ("title", "summary")

# public_access.how is reader copy too. It renders on the item page and tells somebody how to
# actually file a comment, which makes it the most consequential sentence on the page. It was
# outside every copy gate until 2026-08-12, and the hole surfaced the honest way: the house
# punctuation rule found a colon there that no gate had ever looked at.
READER_COPY_NESTED = (("public_access", "how"),)

# Machine narration. The record describes the world, it does not describe its own production.
NARRATION = re.compile(
    r"\b(this (?:item|record|entry|docket)|we (?:found|could not|were unable|searched|fetched)|"
    r"our (?:research|search|analysis)|the (?:search|scan|crawl) (?:found|turned up|returned)|"
    r"no page (?:anyone|we) could reach|as of this writing|at the time of writing|"
    # THE NEGATED FORM IS THE ONE PEOPLE ACTUALLY WRITE, and this branch missed it. It read
    # "could be verified", so "the date could not be verified" walked past a gate whose whole
    # subject it is, on the one word that makes it narration rather than a fact. The separate
    # "not verified" alternative did not catch it either, because the string is "not BE
    # verified". Found on 2026-08-18 while checking that the widened gate could go red, which
    # is the argument for testing that a gate BITES rather than that it passes.
    r"(?:could|couldn't|can't|would|cannot)(?:\s+not)?\s+be verified|not verified|unverified|"
    r"i |i'm |we |we're |our |us )",
    re.IGNORECASE,
)

# Any digit run, with thousands separators, decimals and a trailing percent. Ordinals in dates
# ("August 11th") are handled by the date-form exemption below.
NUMERAL = re.compile(r"\d[\d,]*(?:\.\d+)?%?")

# House style writes dates as "August 11th". Those ordinals are not published figures and must
# not be forced into a claim quote.
#
# A DATE CAN NAME MORE THAN ONE DAY, and this read only the first of them until 2026-08-18. A
# board that meets over two days is written "August 12th and 13th, 2026", the pattern matched
# "August 12th", and the numeral gate then read the surviving "13" as a figure with no claim
# behind it. Nothing was wrong with the sentence. The checker could only recognise a date with
# exactly one day in it, and every extra day a real meeting ran was reported as an untraceable
# number. Ranges are covered by the same tail, which is why "to" and "through" are in it:
# house style writes a range as "X to Y" and that is a date, not a subtraction.
DATE_ORDINAL = re.compile(
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|"
    r"December)\s+\d{1,2}(?:st|nd|rd|th)"
    r"(?:\s*(?:,|and|to|through)\s*\d{1,2}(?:st|nd|rd|th))*\b",
    re.IGNORECASE,
)
# A bare four-digit year in prose is a date, not a measurement.
YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
# A statute or docket citation is an identifier, not a measurement: SB 6, HB 149, Project 58482,
# Chapter 2054, Section 39.151, Docket 59315.
CITATION = re.compile(
    r"\b(?:SB|HB|SJR|HJR)\s*\d+[A-Za-z]?\b|"
    # The Texas Administrative Code, cited the way Texas cites it. The leading figure is the
    # TITLE number, which is as much an identifier as the section after it.
    r"\b\d{1,2}\s+(?:Texas Administrative Code|TAC)\s+(?:(?:Section|Sec\.?|§)\s*)?[\d.]+[A-Za-z]?\b|"
    # THE CONTINUATION IS PART OF THE CITATION. "Sections 2054.701 through 2054.705" names two
    # sections, and a rule that only reaches the first leaves the second to be rescued by
    # something else. That something else used to be a bare dotted pattern, and the cost of it
    # is recorded below.
    r"\b(?:Projects?|Dockets?|Control Numbers?|Chapters?|Sections?|Subchapters?|"
    r"Articles?|Rules?|Items?)\s*"
    r"(?:No\.?\s*)?[\d.]+[A-Za-z]?"
    r"(?:\s*(?:through|thru|to|and|,)\s*(?:No\.?\s*)?[\d.]+[A-Za-z]?)*\b|"
    r"\b\d{1,3}(?:st|nd|rd|th)\s+Legislature\b|"
    r"\b\d+R\b",
    re.IGNORECASE,
)

# A dotted number in this domain is USUALLY a statute section: 2054.702, 39.151, 36.116. It
# needs a rule of its own because a citation can put one somewhere CITATION's anchor word does
# not reach.
#
# THIS PATTERN WAS `\d{1,4}\.\d{1,4}` AND THAT IS EVERY DECIMAL NUMBER THERE IS. It was written
# to rescue the second half of "Sections 2054.701 through 2054.705", and it also silently
# exempted "8.0 gallons per square foot", "22.61 inches of rain" and "5.30 gigawatts at peak"
# from the one law this file exists to enforce. A published measurement with a decimal point in
# it was never checked against a source, on any item, since the gate was written. Nothing
# reported it because an over-wide exemption has no symptom: the gate goes green.
#
# The range is CITATION's job now, where the anchor word is. What is left here is the statute
# shape this domain actually uses, which carries THREE digits after the point. Every measurement
# in this record carries one or two. That is a discriminator rather than a law, so it is written
# down: a statute section with two decimal digits needs its anchor word to be exempt.
DOTTED_SECTION = re.compile(r"\b\d{1,4}\.\d{3}[A-Za-z]?\b")

# This record's own item ids. One item's copy pointing at another is a cross reference, and the
# id carries a year and a sequence number that mean nothing as figures. It is stripped FIRST,
# because the year rule would otherwise eat the "2026" out of "tx-2026-0010" and leave a bare
# "0010" that reads like a published quantity.
ITEM_ID = re.compile(r"\btx-\d{4}-\d{4}\b", re.IGNORECASE)

# A room or suite number is an address. "Commissioners Hearing Room 7-100" is where a person
# physically goes to be heard, and the hyphen makes it read as a range to any numeral rule that
# has not been told otherwise.
#
# "Building" AND "Floor" WERE HERE AND HAD TO COME OUT. They are ordinary English words, and in
# a docket about data centers and the grid they are ordinary English words that are frequently
# followed by a figure. Case-insensitively, "Building 500 megawatts of new gas capacity was
# approved" had its 500 stripped before the numeral gate ever saw it, and the gate reported
# clean. An exemption that swallows a published figure is worse than no exemption, because the
# law this file enforces is that no numeral reaches a reader unquoted and uncomputed.
#
# The identifier must also start with a DIGIT. "Room" followed by a word is prose.
PLACE_NUMBER = re.compile(r"\b(?:Rooms?|Suites?)\s+(?:No\.?\s*)?\d[\dA-Za-z]*(?:-[\dA-Za-z]+)*\b",
                          re.IGNORECASE)

# THE REST OF THE ADDRESS, on the same principle and under the same warning.
#
# `public_access.how` is the field that tells a Texan where to go and who to call, and it is
# reader copy, so the numeral gate reads it. Almost everything a useful `how` contains is a
# LOCATOR: a street number, a post box, a mail code, a zip, a phone, a time on a clock. None of
# those is a measurement, none was computed, and quoting a source saying "1001 Preston Street"
# to justify printing "1001 Preston Street" is a ritual rather than a check. The record already
# accepted this argument once for a room number.
#
# EVERY ONE OF THESE IS ANCHORED TO THE WORD THAT SAYS WHAT THE NUMBER IS, which is what keeps
# it from becoming the "Building" mistake above. A bare five digit pattern would exempt a zip
# and also 12500, so the zip has to be preceded by TX or Texas. A bare hyphenated pattern would
# exempt an ordinance number and also a vote of 4-1, so the identifier has to be preceded by
# Ordinance, Resolution, Permit or their siblings. `_self_test` holds a negative case for each.
STREET = re.compile(
    r"\b\d{1,6}\s+(?:[NSEW]\.?\s+|North\s+|South\s+|East\s+|West\s+)?"
    r"[A-Z][\w.'-]*(?:\s+[A-Z][\w.'-]*){0,4}\s+"
    r"(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Way|Highway|Hwy|"
    r"Parkway|Pkwy|Circle|Cir|Court|Ct|Plaza|Place|Pl|Trail|Trl)\b\.?(?:\s+\d{1,5}\b)?")
PO_BOX = re.compile(r"\bP\.?\s?O\.?\s*Box\s+\d+\b", re.IGNORECASE)
MAIL_CODE = re.compile(r"\bMC[-\s]?\d{2,4}\b")
# Anchored to the state, so it cannot swallow a bare five figure quantity.
ZIP_CODE = re.compile(r"\b(?:TX|Texas|postal\s+code|zip(?:\s+code)?)\s*,?\s*"
                      r"\d{5}(?:-\d{4})?\b", re.IGNORECASE)
# A North American number, with or without the area code, plus the three digit city line.
PHONE = re.compile(r"\b(?:\d{3}[-.]\d{3}[-.]\d{4}|\d{3}[-.]\d{4}|3-1-1)\b")
# A COLON IS A CLOCK. A POINT IS ONLY A CLOCK WITH A MARKER BESIDE IT, because "5.30" on its
# own is a decimal and "5.30 gigawatts at peak" is exactly the figure this gate exists to catch.
CLOCK = re.compile(
    r"\b\d{1,2}:\d{2}\s*(?:[ap]\.?\s?m\.?)?"
    r"|\b\d{1,2}[.:]\d{2}\s*[ap]\.?\s?m\.?"
    r"|\b\d{1,2}[.:]\d{2}\s+in\s+the\s+(?:morning|afternoon|evening)"
    r"|\b\d{1,2}\s*[ap]\.\s?m\.", re.IGNORECASE)
# An instrument's own file number. The anchor word is the point: without it this pattern would
# exempt every hyphenated pair of figures on the page, including a council vote.
INSTRUMENT_ID = re.compile(
    r"\b(?:Ordinance|Ordinances|Resolution|Resolutions|Order|Orders|Permit|Permits|Docket|"
    r"Project|Contract|Agreement|Zone|File|Case|Application|Chapter|Section|Article|"
    r"Division|Matter|Item)\s+(?:No\.?\s*|Number\s*|Numbers\s*)?"
    r"[A-Z]{0,5}[-\s]?\d[\dA-Za-z]*(?:[-.][\dA-Za-z]+)*\b", re.IGNORECASE)
# The same thing written as a bare token, which only reads as an identifier because it leads
# with letters: ORD-2026-08, AI05-26, PSDTX1704, WQ0016885001.
CODED_ID = re.compile(r"\b[A-Z]{2,6}-?\d[\dA-Za-z]*(?:-[\dA-Za-z]+)*\b")

LOCATORS = (STREET, PO_BOX, MAIL_CODE, ZIP_CODE, PHONE, CLOCK, INSTRUMENT_ID, CODED_ID)

ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# --------------------------------------------------------------------------- result plumbing
class Result:
    def __init__(self, name: str):
        self.name, self.status, self.lines = name, "PASS", []

    def fail(self, msg: str):
        self.status = "FAIL"
        self.lines.append(msg)

    def warn(self, msg: str):
        if self.status == "PASS":
            self.status = "WARN"
        self.lines.append(msg)

    def note(self, msg: str):
        self.lines.append(msg)


# ---------------------------------------------------------------------------- geography
# THE ITEMS THAT WERE UNLOCATABLE WHILE PASSING A LOCATABILITY CHECK.
#
# The rule here used to read
#
#     if not (statewide or counties or on_ercot):  fail("Every item is somewhere")
#
# and three items passed it on `on_ercot: true` alone, with no county and not statewide.
# **ERCOT serves about ninety percent of the state's load.** "On the ERCOT grid" is barely
# narrower than "in Texas", it is a PROPERTY of an item rather than a PLACE, and it is not
# something a reader can filter by. So those three appear on no county page, light no
# county on the map, and would appear on no metro page either, while the gate that exists
# to prevent exactly that reported clean.
#
# It is the shape `knowledge/shared/GATE_LESSONS.md` keeps collecting: **a rule satisfied
# by a value that does not carry the meaning the rule is about.** `on_ercot` stays in the
# schema because it is a true and useful fact. It no longer counts as a location.
#
# The second half is entity resolution. Twenty-two county names sit in the record as free
# strings and nothing has ever checked they are real Texas counties. They all happen to
# resolve today. A typo would be stored, would light nothing on the map, and would say so
# to nobody, which is the silent-failure mode `places.py` was written against.
#
# THE BACKLOG IS A RATCHET. `ledger/docket.json` belongs to the `daily` actor, so a
# maintainer session cannot fill these in; the routine does it during re-verify. A hard
# fail on day one would block every run until a lane it does not own was cleared by hand.
# So the three known items are named here, they are the only ones exempt, and the list can
# only shrink. A fourth unlocatable item fails immediately.
GEOGRAPHY_BACKLOG = {
    "tx-2026-0001": "ERCOT large-load interconnection, admitted before geography was checked",
    "tx-2026-0002": "ERCOT large-load queue, same",
    "tx-2026-0007": "ERCOT planning docket, same",
}

# THE OTHER RATCHET, same reason and same lane. One item points a reader at an item that
# fact checking culled. See `gate_cross_references`. Written as item -> the id it names, so
# a second dangling pointer from the SAME item still fails.
XREF_BACKLOG = {
    "tx-2026-0006": "tx-2026-0010",
}


def _resolver():
    """The place resolver, or None when the gazetteer is unreadable.

    A missing gazetteer must not silently switch off county resolution, so the caller
    turns None into a failure rather than a skip.
    """
    try:
        sys.path.insert(0, str(REPO_ROOT / "scripts" / "shared"))
        import places                                                # noqa: PLC0415
        return places.Resolver.load()
    except Exception:                                                # noqa: BLE001
        return None


def _geography_problems(who: str, item: dict) -> list:
    out = []
    g = item.get("geography") or {}
    counties = g.get("counties") or []
    item_id = str(item.get("id", ""))

    if not (g.get("statewide") or counties):
        if item_id not in GEOGRAPHY_BACKLOG:
            out.append(
                f"{who}: geography names no county and is not statewide, so this item is on "
                f"no county page, lights no county on the map and belongs to no metro. "
                f"`on_ercot` does NOT count: ERCOT carries about ninety percent of the "
                f"state's load, so it is a property rather than a place. Name the counties.")

    res = _resolver()
    if counties and res is None:
        out.append(f"{who}: the places gazetteer could not be read, so county names went "
                   f"unchecked. That is a stop rather than a skip.")
    elif counties:
        unresolved = [c for c in counties if res.resolve(c) is None]
        for c in unresolved:
            hint = ", ".join(p["full_name"] for p in res.candidates(c)[:3])
            out.append(f"{who}: county {c!r} is not a Texas county this project knows. It "
                       f"would be stored, light nothing on the map and tell nobody."
                       + (f" Did you mean {hint}?" if hint else ""))

        # METRO IS DERIVED, NEVER TYPED. The compute-not-generate law, applied to a field
        # a well-meaning editor would otherwise fill in by hand.
        derived = sorted({m["full_name"] for c in counties
                          if (m := res.metro_of(c)) is not None})
        declared = g.get("metro")
        if declared is not None and declared != (derived[0] if len(derived) == 1 else derived):
            out.append(f"{who}: geography.metro is {declared!r} and the counties compute to "
                       f"{derived!r}. The metro is derived from the counties by "
                       f"`places.metro_of`, never typed.")
    return out


def _reader_text(item: dict, *, include_history: bool = True) -> str:
    """The prose this project WROTE for a reader, which is what the copy gates govern.

    HISTORY NOTES ARE READER COPY AND WERE OUTSIDE EVERY GATE UNTIL 2026-08-18, which is the
    same hole `public_access.how` sat in until 2026-08-12 and it opened for the same reason: the
    field was not rendered, so nobody asked whether it was governed. Now that the movement log
    renders on the item page it is the most-read prose on it after the summary.

    `include_history` is FALSE for exactly one caller, the numeral gate, and the reason is
    structural rather than convenient. A movement line's whole job is to say what the record
    used to hold, "the filing index moved from 5782 to 5790". The old figure is by definition
    no longer in any current claim quote, because the claim was updated to the new one. Holding
    the log to the numeral gate would make the one sentence a movement log exists to write
    unwriteable, and would push a run toward "the index moved" with no figures at all, which is
    worse copy and a weaker record. The old value's provenance is this file's own git history.
    """
    parts = [str(item.get(f, "")) for f in READER_COPY_FIELDS]
    for outer, inner in READER_COPY_NESTED:
        parts.append(str((item.get(outer) or {}).get(inner, "")))
    if include_history:
        for h in item.get("history") or []:
            if isinstance(h, dict):
                parts.append(str(h.get("note", "")))
    # A key date's note ALSO renders, on the timeline, and is NOT folded in here. It is not
    # ungoverned any more. `gate_house_style` reads it directly and applies the construction
    # rules to it, and the reason it is checked over there rather than folded in over here is
    # that this text is what the COMMA CEILING is measured against. That ceiling is a measured
    # number calibrated on running prose, a key date note is a label fragment, and adding
    # fragments to the measurement moves a number that was measured on something else. The
    # split, and the numeral gate question still open on those notes, are written out in full
    # at `gate_house_style`.
    return " ".join(parts)


def _quoted_numerals(item: dict) -> set:
    """Every numeral this item is entitled to use in prose.

    Two sources, and both satisfy the law:

      QUOTED    it appears in a claim's verbatim quote, so a source said it.
      COMPUTED  it is derived from the record itself, so code produced it. "across 22
                counties" is legitimate when geography.counties holds 22 entries, because
                that numeral IS the computation. Forcing it into a quote would be the law
                misread as "no numerals unless somebody else typed them first".
    """
    out = set()
    for c in item.get("claims", []):
        for m in NUMERAL.findall(str(c.get("verbatim_quote", ""))):
            out.add(m.replace(",", "").rstrip("%"))
    g = item.get("geography") or {}
    counties = g.get("counties") or []
    if counties:
        out.add(str(len(counties)))
    out.add(str(len(item.get("claims") or [])))
    out.add(str(len(item.get("key_dates") or [])))
    return out


# A NAME WITH A NUMBER IN IT, and the number is part of the name.
#
# "NewsChannel 6" is a broadcaster. "ABC13" is a station. "Interstate 35" is a road. The numeral
# is not a measurement and forcing it into a claim quote would be the law misread, the same
# misreading `_quoted_numerals` already names for computed figures.
#
# THE EXEMPTION IS EARNED, NOT DECLARED, which is the only reason it is allowed to exist. The
# obvious fix here is an allowlist of station names, and an allowlist is a hole with a list
# attached to it: the moment somebody adds "Channel 12" to it, "Channel 12" is authorised on
# every page of the site whether or not any source ever mentioned it. So nothing is listed.
# The candidate span is found structurally, and then it has to MATCH A NAME THIS ITEM'S OWN
# EVIDENCE ALREADY CARRIES, which is exactly the shape of `schema.list_answer_ok`, where the
# comma exemption is checked against the counties the record actually holds.
#
# What the evidence carries, for this purpose: the host of every source URL, every source
# title, the deciding body's name, and the item's own title. "NewsChannel 6" is authorised on
# tx-2026-0041 because that item cites `newschannel6now.com`. "NewsChannel 9" is not authorised
# anywhere, because nothing in the record is called that.
NAME_NUMBER = re.compile(r"\b([A-Z][A-Za-z&.'’-]*(?:\s+[A-Z][A-Za-z&.'’-]*)*)\s*(\d[\d,]*)\b")


def _squash(s: str) -> str:
    """Lowercase alphanumerics only, so a host, a headline and a sentence compare as names."""
    return re.sub(r"[^a-z0-9]+", "", str(s).lower())


def _name_evidence(item: dict) -> str:
    """Every name this item's record carries, squashed into one haystack."""
    parts = [str(item.get("title", "")), str((item.get("decider") or {}).get("name", ""))]
    for c in item.get("claims", []):
        parts.append(str(c.get("source_title", "")))
        # The host, with its dots gone, is where a broadcaster's own number usually lives.
        # `newschannel6now.com` squashes to `newschannel6nowcom`, which carries `newschannel6`.
        parts.append(str(c.get("source_url", "")))
    return " ".join(_squash(p) for p in parts)


def _name_numerals(item: dict, text: str) -> set:
    """Numerals in `text` that sit inside a name this item's own evidence already carries.

    EVERY SUFFIX OF THE CAPITALISED RUN IS TRIED, SHORTEST FIRST, and that is not a detail. The
    pattern is greedy by necessity, because a name can be several words, so "Date NewsChannel 6"
    hands back "Date NewsChannel" as the candidate and `datenewschannel6` matches nothing. The
    name is the tail of that run, not the whole of it, and which tail is not knowable from the
    sentence. Trying each one costs nothing and keeps the test a membership check against the
    record rather than a guess about where a proper noun starts.

    It does NOT loosen the exemption. A longer or shorter window still has to match a name the
    evidence carries, so a sentence can only ever authorise a numeral the record already knows
    is part of a name.
    """
    hay = _name_evidence(item)
    out = set()
    for name, num in NAME_NUMBER.findall(text):
        words = name.split()
        for i in range(len(words) - 1, -1, -1):
            probe = _squash(" ".join(words[i:]) + num)
            if probe and probe in hay:
                out.add(num.replace(",", "").rstrip("%"))
                break
    return out


def _prose_numerals(text: str) -> list:
    """Numerals in prose, minus dates, years and citations, which are identifiers not figures."""
    # Order matters. Dotted sections go before YEAR, or "2054.705" loses its "2054" to the
    # year rule and leaves a bare "705" that reads as a published figure.
    stripped = ITEM_ID.sub(" ", text)
    stripped = DATE_ORDINAL.sub(" ", stripped)
    stripped = CITATION.sub(" ", stripped)
    stripped = PLACE_NUMBER.sub(" ", stripped)
    # The locators go before DOTTED_SECTION, or "5.30 in the afternoon" loses its "5.30" to the
    # section rule and the clock pattern never sees a time to strip.
    for pat in LOCATORS:
        stripped = pat.sub(" ", stripped)
    stripped = DOTTED_SECTION.sub(" ", stripped)
    stripped = YEAR.sub(" ", stripped)
    return [m.replace(",", "").rstrip("%") for m in NUMERAL.findall(stripped)]


# --------------------------------------------------------------------------- gates
def gate_schema(items: list) -> Result:
    r = Result("schema")
    seen_ids = set()
    for n, it in enumerate(items):
        who = it.get("id") or f"item[{n}]"
        if not isinstance(it, dict):
            r.fail(f"{who}: not an object")
            continue
        for field in REQUIRED_FIELDS:
            if field not in it:
                r.fail(f"{who}: missing required field '{field}'")
        if it.get("id") in seen_ids:
            r.fail(f"{who}: duplicate id")
        seen_ids.add(it.get("id"))

        if it.get("topic") not in TOPICS:
            r.fail(f"{who}: topic '{it.get('topic')}' is not in the vocabulary")
        if it.get("status") not in STATUSES:
            r.fail(f"{who}: status '{it.get('status')}' is not in the vocabulary")
        if it.get("confidence") and it["confidence"] not in CONFIDENCES:
            r.fail(f"{who}: confidence '{it['confidence']}' is not in the vocabulary")

        d = it.get("decider") or {}
        if d.get("type") not in DECIDER_TYPES:
            r.fail(f"{who}: decider.type '{d.get('type')}' is not in the vocabulary")
        if not str(d.get("name", "")).strip():
            r.fail(f"{who}: decider.name is empty. Every decision has a decider")

        pa = it.get("public_access") or {}
        if pa.get("room") not in ROOMS:
            r.fail(f"{who}: public_access.room '{pa.get('room')}' is not one of the four rooms")
        if pa.get("room") == "open_comment" and not pa.get("closes"):
            r.fail(f"{who}: room is open_comment but no close date is set. "
                   f"An open window a reader cannot date is not actionable")

        for kd in it.get("key_dates", []):
            if kd.get("kind") not in DATE_KINDS:
                r.fail(f"{who}: key_dates kind '{kd.get('kind')}' is not in the vocabulary")
            if not ISO_DATE.match(str(kd.get("date", ""))):
                r.fail(f"{who}: key_dates date '{kd.get('date')}' is not ISO yyyy-mm-dd")
            if "canceled" in kd and not isinstance(kd["canceled"], bool):
                r.fail(f"{who}: key_dates canceled must be true or false, not "
                       f"{kd['canceled']!r}")
            # A CANCELED SITTING HAS TO BE A FIELD, NOT A SENTENCE.
            #
            # TCEQ called off two August 2026 hearings and the record kept the original dates
            # with "since canceled" in the note, which is correct history. The site then had to
            # decide whether a date was still a door, and the only thing carrying that fact was
            # prose. `next_door` read the note with a regex to avoid publishing two canceled
            # hearings as live doors, and a regex over a sentence a person writes is exactly the
            # generated-not-computed shape this project refuses everywhere else.
            #
            # So the flag is the truth and this gate keeps the sentence honest against it. Say
            # canceled in the note and the field must agree. The reverse is deliberately NOT
            # required: a canceled date may carry any note or none.
            if (re.search(r"\bcancell?ed\b", str(kd.get("note") or ""), re.I)
                    and not kd.get("canceled")):
                r.fail(f"{who}: the {kd.get('kind')} on {kd.get('date')} describes itself as "
                       f"canceled in its note but carries no canceled flag. The site decides "
                       f"whether a date is still a door, and it may not do that by reading "
                       f"prose")

        if not ISO_DATE.match(str(it.get("last_verified", ""))):
            r.fail(f"{who}: last_verified '{it.get('last_verified')}' is not ISO yyyy-mm-dd")

        for problem in _geography_problems(who, it):
            r.fail(problem)
    if r.status == "PASS":
        r.note(f"{len(items)} item(s) conform")
    return r


def gate_claims(items: list) -> Result:
    r = Result("claims")
    total = 0
    for it in items:
        who = it.get("id", "?")
        claims = it.get("claims") or []
        if not claims:
            r.fail(f"{who}: no claims. If it is not in the claims file, it does not exist")
        ids = set()
        for c in claims:
            total += 1
            cid = c.get("id", "?")
            if cid in ids:
                r.fail(f"{who}: duplicate claim id '{cid}'")
            ids.add(cid)
            if not str(c.get("verbatim_quote", "")).strip():
                r.fail(f"{who}/{cid}: no verbatim quote. A claim without the source's own "
                       f"words cannot be checked")
            url = str(c.get("source_url", ""))
            if not url.startswith(("http://", "https://")):
                r.fail(f"{who}/{cid}: source_url is not a URL")
            if c.get("source_type") not in SOURCE_TYPES:
                r.fail(f"{who}/{cid}: source_type '{c.get('source_type')}' is not in the "
                       f"vocabulary")
    if r.status == "PASS":
        r.note(f"{total} claim(s), each with a quote and a source")
    return r


def gate_numerals(items: list) -> Result:
    """THE LAW, at the docket layer.

    Every numeral in reader copy must appear in some claim's verbatim quote. Dates, years and
    statute or docket citations are exempt because they are identifiers, not measurements.

    KEY DATE NOTES ARE IN THIS GATE AS OF 2026-08-18, and getting them in was the whole reason
    `_name_numerals` exists. They render under their own date on the timeline, so they are read
    exactly as much as the summary is, and they sat outside this gate because one of them says
    "NewsChannel 6" and a broadcaster's name is not a measurement. The fix for that is not to
    keep the notes out and it is not a list of station names. It is a rule that asks the
    record whether the thing is a name, which is what `_name_numerals` does.

    THEY ARE CHECKED SEPARATELY RATHER THAN CONCATENATED ONTO THE SUMMARY, because the name
    exemption is scoped to the text it was earned in. A broadcaster this item cites is not a
    licence for that figure to appear anywhere else in the item's copy, where nothing has
    established it as a name.
    """
    r = Result("numerals")
    checked = 0
    for it in items:
        who = it.get("id", "?")
        allowed = _quoted_numerals(it)
        for got in _prose_numerals(_reader_text(it, include_history=False)):
            checked += 1
            if got not in allowed:
                r.fail(f"{who}: numeral '{got}' appears in reader copy but in no claim quote. "
                       f"Quote it or cut it")
        for kd in (it.get("key_dates") or []):
            note = str(kd.get("note") or "")
            ok = allowed | _name_numerals(it, note)
            for got in _prose_numerals(note):
                checked += 1
                if got not in ok:
                    r.fail(f"{who}: key date {kd.get('date', '?')}: numeral '{got}' appears in "
                           f"the note but in no claim quote and in no name the record carries. "
                           f"Quote it or cut it")
    if r.status == "PASS":
        r.note(f"{checked} numeral(s) in copy, all traceable to a quote or a name")
    return r


def gate_narration(items: list) -> Result:
    r = Result("narration")
    for it in items:
        who = it.get("id", "?")
        m = NARRATION.search(_reader_text(it))
        if m:
            r.fail(f"{who}: reader copy narrates the machine or uses first person "
                   f"({m.group(0).strip()!r}). The record describes the world, not its own work")
    if r.status == "PASS":
        r.note("no machine narration in reader copy")
    return r


def gate_cross_references(items: list, known_ids: set | None = None) -> Result:
    """An item this record points a reader at has to exist.

    FOUND BY THE NUMERAL GATE, WHICH IS NOT WHAT THE NUMERAL GATE IS FOR. Item
    tx-2026-0006 tells a reader "See item tx-2026-0010 for that page's statutory basis",
    and there is no tx-2026-0010. Ids run 0001 to 0025 with gaps, because fact checking
    culled the ones that could not be sourced, and this pointer survived the cull.

    Nothing caught it and three things nearly should have. The link checker reads `href`
    attributes and this is prose, so there is no link to be broken. The claims gate checks
    that every claim has a source, and this sentence is not a claim. The numeral gate saw
    it only because `0010` is a numeral, and it reported a stray digit rather than a
    broken promise, which is a diagnosis one step short of the disease.

    The general shape, for `GATE_LESSONS.md`: **a reference is a dependency even when it
    is not a link.** Prose that names another record is asserting that record exists, and
    only a checker that knows the id space can tell whether it does.

    RATCHETED, like the geography backlog and for the same reason. `ledger/docket.json`
    belongs to `daily`, so a maintainer session cannot rewrite that sentence. Blocking
    every build until the routine next runs would take the whole site down over one
    dangling pointer, which is a worse outcome than the pointer. The one known break is
    named, it is the only exemption, and a second one fails immediately.
    """
    known = {i.get("id") for i in items} | (known_ids or set())
    r = Result("cross references")
    dangling = 0
    for it in items:
        who = it.get("id", "?")
        for ref in sorted(set(ITEM_ID.findall(_reader_text(it)))):
            if ref in known or ref == who:
                continue
            dangling += 1
            if XREF_BACKLOG.get(who) == ref:
                r.note(f"{who}: points at {ref}, which does not exist. Known break, "
                       f"awaiting the routine's re-verify phase")
                continue
            r.fail(f"{who}: reader copy points at item {ref} and no such item is in the "
                   f"record. Name an item that exists, or say the thing instead of "
                   f"pointing at it")
    if r.status == "PASS" and not dangling:
        r.note(f"every item reference in {len(items)} item(s) resolves")
    return r


def gate_house_style(items: list) -> Result:
    """The house punctuation and voice rules, applied to the record's own prose.

    The site already runs this over the BUILT pages, which catches anything a page builder
    writes. It could not catch anything the RECORD carries, because a bad sentence in a summary
    is copy this project wrote just as much as a paragraph in a builder is. A rule enforced on
    one and not the other is a rule with a door in it.

    A claim's verbatim quote is never checked. Rewriting a quotation to fit house style would
    be falsifying it, which is far worse than an inconsistent date, and `_reader_text` already
    excludes quotes by construction.
    """
    r = Result("house style")
    for it in items:
        who = it.get("id", "?")
        text = _reader_text(it)
        for problem in caption_check.check(text):
            r.fail(f"{who}: {problem}")
        rate = caption_check.rate_problem(text, caption_check.SITE_COMMA_CEILING)
        if rate:
            r.fail(f"{who}: {rate}")
        # A KEY DATE NOTE IS COPY, AND IT IS CHECKED ON CONSTRUCTION ONLY.
        #
        # It renders on the timeline under the date it belongs to, so a reader reads it, and
        # until 2026-08-18 no gate on either layer read it. That is the hole the movement log
        # sat in and it opened the same way, by the field being written before anybody asked
        # what governs it.
        #
        # THE SPLIT IS DELIBERATE AND THE COMMA CEILING IS THE HALF LEFT OUT. That ceiling is a
        # MEASURED number, 3.97, taken by counting the commas in this project's running prose
        # and cutting ten percent. What it means depends entirely on what was measured to
        # produce it. A key date note is a label fragment, "Regular City Council meeting,
        # 9:00 AM, item scheduled for discussion and action", where both commas are structural
        # and there is no sentence to split at. Folding fragments into the measurement while
        # keeping a threshold calibrated on sentences would fail pages for a reason that has
        # nothing to do with whether the prose breathes, which is the exact error CLAUDE.md
        # names when it says the rate is measured on running prose and not on whole-page text.
        # Fragments can have their own ceiling when somebody measures fragments.
        #
        # THE NUMERAL GATE IS NOT LEFT OUT. It reads these notes over in `gate_numerals`, and
        # the two findings that stood in the way were both the checker's fault rather than the
        # copy's. "August 12th and 13th" was a date `DATE_ORDINAL` could only half read, fixed
        # at that pattern. "NewsChannel 6" is a broadcaster's name, answered by `_name_numerals`
        # asking the record whether the thing is a name instead of carrying a list of stations.
        for kd in (it.get("key_dates") or []):
            for problem in caption_check.check(str(kd.get("note") or "")):
                r.fail(f"{who}: key date {kd.get('date', '?')}: {problem}")
            m = NARRATION.search(str(kd.get("note") or ""))
            if m:
                r.fail(f"{who}: key date {kd.get('date', '?')}: narrates the machine or uses "
                       f"first person ({m.group(0).strip()!r})")
    if r.status == "PASS":
        r.note(f"{len(items)} item(s) keep the house rules, key date notes included")
    return r


def gate_staleness(items: list, today: str,
                   warn_days: int = 2, fail_days: int = 6) -> Result:
    """Two bands, and the outer one is a HARD FAIL.

    THE BANDS WERE 45 AND 120 DAYS UNTIL 2026-08-18. That was the loosest gate in this repo by
    a wide margin, and it was enforcing nothing: the selector called an item due after 3 days
    while this gate stayed silent for six more weeks, so an item could rot for a month and a
    half with every gate green. Owner's call, and it is right: re-verification is the product,
    so the gate that enforces it should be the strict one.

    The bands now match `docket_staleness.LEASH_DAYS`. Past two days an item is DUE and the
    build warns. Past six, three times the leash, it is being published as current when nobody
    has looked at it in most of a week, and the build stops.

    WHY THE HARD BAND IS NOT ALSO TWO DAYS, which is the obvious thing to ask. A run that
    re-verifies everything drops every item to zero and the gate is silent, so at two days both
    bands would fire together and the warn band would never be seen. Worse, a single source
    outage on one item would block the whole publication, deck included, on a day when 30 other
    items were verified perfectly. Six days is far tighter than anything this gate has ever
    enforced and still leaves a run two more attempts to reach a source that was down.
    """
    r = Result("staleness")
    t = _dt.date.fromisoformat(today)
    aged = []
    for it in items:
        try:
            age = (t - _dt.date.fromisoformat(str(it.get("last_verified")))).days
        except ValueError:
            continue
        aged.append((it.get("id"), age))
    for i, age in sorted(aged, key=lambda x: -x[1]):
        if age > fail_days:
            r.fail(f"{i}: not re-verified in {age} days, past the {fail_days} day limit. "
                   f"Re-verify it or drop it; publishing it as current is a false claim")
        elif age > warn_days:
            r.warn(f"{i}: not re-verified in {age} days, due for a re-check")
    if r.status == "PASS":
        r.note(f"all items verified within {warn_days} days")
    return r


def gate_deadlines(items: list, today: str) -> Result:
    """Only checks that a close date is parseable.

    Whether a window is OPEN is never stored, it is derived at render time from the date (see
    `window_state`). Storing it would let the record go stale between runs and tell a reader a
    door is open after it locked. Derived state cannot rot.
    """
    r = Result("deadlines")
    for it in items:
        pa = it.get("public_access") or {}
        closes = pa.get("closes")
        if closes:
            try:
                _dt.date.fromisoformat(str(closes))
            except ValueError:
                r.fail(f"{it.get('id')}: public_access.closes '{closes}' is not ISO yyyy-mm-dd")
    if r.status == "PASS":
        r.note("every close date parses; open or shut is derived, never stored")
    return r


def window_state(item: dict, today: str) -> str:
    """DERIVED, never stored. 'open', 'closed', or 'none'.

    This is the compute-not-generate principle applied to state rather than to numbers. The
    ledger records what KIND of access exists and when it ends; whether it is open right now is
    arithmetic, done fresh on every build.
    """
    pa = item.get("public_access") or {}
    if pa.get("room") != "open_comment":
        return "none"
    closes = pa.get("closes")
    if not closes:
        return "none"
    try:
        return "open" if _dt.date.fromisoformat(str(closes)) >= _dt.date.fromisoformat(today) \
            else "closed"
    except ValueError:
        return "none"


# The day the routine was told to write a dated line every time it checks an item, unchanged
# included. Items stamped before this are exempt, and that exemption is not laziness: writing a
# line for a check nobody recorded would be inventing an observation, on the one surface whose
# entire promise is that it does not. The log starts here and grows forward.
MOVEMENT_RULE_DATE = "2026-08-18"


def gate_movement(items: list) -> Result:
    """A re-verification stamp with no movement line beside it.

    THE RULE WAS WRITTEN INTO THE ROUTINE AND ENFORCED BY NOTHING, and it took one day to be
    broken. On 2026-08-19 four items arrived on `main` carrying `last_verified: 2026-08-19` and
    no history entry for that date. Some run had looked at them, advanced the stamp, and thrown
    the observation away, which is precisely the defect the movement log was opened to fix.

    That is the same shape as the email a run hand-wrote past a builder nothing checked. A rule
    that lives only in a prompt is a suggestion, and the fix is the same both times: make the
    artifact prove it.

    WHAT IS CHECKED IS NOT "DID SOMETHING CHANGE". It is that a stamp and a line agree, which is
    a fact about the file and needs no previous version to judge. `last_verified` says somebody
    looked on that date, so the log has to carry a line saying what they saw. "Checked and
    unchanged" is the answer on most days and it is a fact about the decision, not filler.
    """
    r = Result("movement")
    checked = 0
    for it in items:
        lv = str(it.get("last_verified") or "")
        if lv < MOVEMENT_RULE_DATE:
            continue
        checked += 1
        dates = {str(h.get("date")) for h in (it.get("history") or []) if isinstance(h, dict)}
        if lv not in dates:
            r.fail(f"{it.get('id', '?')}: last_verified is {lv} and the movement log carries no "
                   f"line for that date. A stamp with no line beside it is a check a reader "
                   f"cannot see. Write what was observed, including that nothing changed")
    if r.status == "PASS":
        r.note(f"{checked} item(s) checked since {MOVEMENT_RULE_DATE}, every stamp with a line")
    return r


GATES = {
    "schema": gate_schema, "claims": gate_claims, "numerals": gate_numerals,
    "narration": gate_narration, "house style": gate_house_style,
    "cross references": gate_cross_references, "movement": gate_movement,
}
DATED_GATES = {"staleness": gate_staleness, "deadlines": gate_deadlines}


# --------------------------------------------------------------------------- projection
def project(items: list, today: str) -> dict:
    """The render-ready shape. Every count here is COMPUTED, which is what lets the site
    publish a numeral at all."""
    t = _dt.date.fromisoformat(today)
    by_topic, by_county, by_room, by_status = {}, {}, {}, {}
    # THE PLACE INDEX, and it is deliberately two indexes rather than one.
    #
    # A metro index alone would drop 121 of Texas's 254 counties, which is not an edge
    # case: Shackelford, Childress and most of the Permian outside Midland-Odessa are in
    # no statistical area, and that is exactly where the physical buildout is. So an item
    # lands in `by_metro` when its counties are in one, and every touched county lands in
    # `unmetroed_counties` when they are not, and no item falls between them.
    by_metro: dict[str, dict] = {}
    unmetroed: dict[str, int] = {}
    res = _resolver()
    actionable = []
    for it in items:
        by_topic[it["topic"]] = by_topic.get(it["topic"], 0) + 1
        by_status[it["status"]] = by_status.get(it["status"], 0) + 1
        room = it["public_access"]["room"]
        by_room[room] = by_room.get(room, 0) + 1
        for c in (it.get("geography") or {}).get("counties") or []:
            by_county[c] = by_county.get(c, 0) + 1
            m = res.metro_of(c) if res else None
            if m:
                slot = by_metro.setdefault(m["id"], {
                    "id": m["id"], "name": m["name"], "full_name": m["full_name"],
                    "code": m["code"], "area_type": m["area_type"],
                    "counties": m["counties"], "items": [], "touched_counties": [],
                })
                if it["id"] not in slot["items"]:
                    slot["items"].append(it["id"])
                if c not in slot["touched_counties"]:
                    slot["touched_counties"].append(c)
            else:
                unmetroed[c] = unmetroed.get(c, 0) + 1
        closes = (it.get("public_access") or {}).get("closes")
        if room == "open_comment" and closes:
            try:
                days = (_dt.date.fromisoformat(str(closes)) - t).days
            except ValueError:
                continue
            if days >= 0:
                actionable.append({"id": it["id"], "title": it["title"],
                                   "closes": closes, "days_left": days})
    actionable.sort(key=lambda a: a["days_left"])
    return {
        "generated": today,
        "counts": {
            "items": len(items),
            "claims": sum(len(i.get("claims") or []) for i in items),
            "by_topic": dict(sorted(by_topic.items())),
            "by_status": dict(sorted(by_status.items())),
            "by_room": dict(sorted(by_room.items())),
            "counties_touched": len(by_county),
            "metros_touched": len(by_metro),
            # The size of what a metro view would MISS, published rather than hidden.
            # It is the same instinct as the grid watch publishing the size of what is
            # not public: a per-city page that quietly omitted these counties would be
            # a more confident and less honest page.
            "counties_touched_outside_any_metro": len(unmetroed),
        },
        "by_county": dict(sorted(by_county.items())),
        "by_metro": {k: by_metro[k] for k in sorted(by_metro)},
        "unmetroed_counties": dict(sorted(unmetroed.items())),
        "actionable_now": actionable,
    }


# --------------------------------------------------------------------------- io
def load(path: Path) -> list:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    return raw.get("items", [])


def load_record(path: Path) -> dict:
    """Read the published record without silently accepting a seed-shaped file.

    `load()` deliberately accepts either a list or an object because candidate batches use
    both shapes. Promotion is about to REPLACE the live ledger, so that convenience would be
    dangerous there: a malformed object could otherwise read as an empty record and make an
    apparently safe append erase everything. The write path therefore requires the canonical
    object with an item list before it computes a replacement.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("items"), list):
        raise ValueError(f"{path} is not a docket record object with an items list")
    return raw


def _atomic_write_text(path: Path, text: str, *, replace=os.replace) -> None:
    """Durably prepare `text`, then expose it at `path` in one filesystem operation.

    The temporary file sits beside the ledger so `os.replace` cannot cross a filesystem. It is
    removed if writing, flushing or replacing fails, while the old ledger remains at its old
    path. Preserve the target's mode rather than replacing a public record with NamedTemporary
    File's private default.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = (path.stat().st_mode & 0o777) if path.exists() else 0o644
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=path.parent,
                prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, mode)
        replace(temporary, path)
        temporary = None
        # The replacement itself is atomic. Syncing the directory as well makes the rename
        # durable across a sudden machine loss where the platform supports directory fsync.
        try:
            directory = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        except OSError:
            pass
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


# Gates whose FAIL is LOUD BUT DOES NOT STOP A REBUILD. Exactly one, and the reason is the
# same one the `backlog` docstring below already argues: a hard fail must not take the site
# down over work in a lane the build cannot do for itself.
#
# STALENESS IS ABOUT THE AGE OF THE INPUT, NOT THE CORRECTNESS OF THE OUTPUT. A schema error, a
# broken cross reference or an untraceable numeral all mean the page this build would produce is
# WRONG, so refusing to build is right. An item last verified seven days ago produces a page
# that is perfectly correct and merely old. Refusing to rebuild on that freezes the site in an
# even older state than the one being complained about, and takes the deck down with it, which
# is the punishment landing on the reader instead of on the run.
#
# Enforcement is not weakened. `--validate` still counts this and still exits non-zero, CI still
# goes red, and the routine still has to clear it before it can ship. What changes is only that
# a stale record can still be REBUILT while it is being fixed.
NON_BLOCKING_FOR_BUILD = {"staleness"}


def run_gates(items: list, today: str, *, blocking_only: bool = False) -> tuple[int, list]:
    """Returns (count of FAILs that matter to the caller, all results).

    `blocking_only` is for the site builder. Everything else, including `--validate`, counts
    every FAIL, so nothing is quietly downgraded.
    """
    results = [g(items) for g in GATES.values()]
    results += [g(items, today) for g in DATED_GATES.values()]
    bad = sum(1 for r in results if r.status == "FAIL"
              and not (blocking_only and r.name in NON_BLOCKING_FOR_BUILD))
    return bad, results


def backlog(items: list) -> list:
    """What the ratchets are currently letting through, in one line each.

    A RATCHET NOBODY SEES IS AN EXEMPTION. Both backlogs here exist because the record
    belongs to the `daily` actor and a maintainer session cannot fill them, so a hard fail
    would take the site down over work in a lane it does not own. That is the right call
    and it has a failure mode: a green build says nothing, the exemption stops being a
    debt, and the ratchet becomes the standard. So every build prints what is outstanding,
    whether or not anything failed.
    """
    known = {i.get("id") for i in items}
    out = []
    for it in items:
        who = it.get("id", "?")
        if who in GEOGRAPHY_BACKLOG:
            out.append(f"{who}: no county and not statewide ({GEOGRAPHY_BACKLOG[who]})")
        for ref in sorted(set(ITEM_ID.findall(_reader_text(it)))):
            if ref not in known and ref != who:
                out.append(f"{who}: points at {ref}, which is not in the record")
    return out


def report(results: list) -> None:
    for r in results:
        print(f"  [{r.status}] {r.name}")
        for line in r.lines[:12]:
            print(f"         {line}")
        if len(r.lines) > 12:
            print(f"         ...and {len(r.lines) - 12} more")


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    """Prove each gate can go red. A gate that cannot fail proves nothing about what it guards."""
    failures = 0

    def base(**over):
        it = {
            "id": "tx-2026-0001",
            "title": "PUCT opens Project 58482 on large load demand management",
            "summary": "The commission proposed a new rule. Comments close September 4th.",
            "topic": "power-and-the-grid",
            "decider": {"name": "Public Utility Commission of Texas", "type": "state-agency"},
            "geography": {"statewide": True, "counties": [], "metro": None, "on_ercot": True},
            "status": "open",
            "key_dates": [{"date": "2026-09-04", "kind": "comment_closes", "note": ""}],
            "public_access": {"room": "open_comment", "how": "File a comment.",
                              "url": "https://interchange.puc.texas.gov/", "closes": "2026-09-04"},
            "claims": [{
                "id": "tx-2026-0001-c1",
                "text": "The project number is 58482.",
                "verbatim_quote": "Project No. 58482, 12 filing(s), demand management",
                "source_url": "https://interchange.puc.texas.gov/search/filings/",
                "source_title": "PUCT Interchange", "source_type": "primary_official",
                "fetched": "2026-08-11"}],
            "last_verified": "2026-08-11",
            "confidence": "high",
        }
        it.update(over)
        return it

    def expect(label, result, want):
        nonlocal failures
        ok = result.status == want
        print(f"  {'ok  ' if ok else 'FAIL'}  {label} -> {result.status}")
        if not ok:
            failures += 1
            for line in result.lines[:3]:
                print(f"        {line}", file=sys.stderr)

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    today = "2026-08-11"

    expect("schema passes a well-formed item", gate_schema([base()]), "PASS")
    expect("schema catches an unknown topic",
           gate_schema([base(topic="ai-stuff")]), "FAIL")
    expect("schema catches an unknown room",
           gate_schema([base(public_access={"room": "maybe", "how": "", "url": None})]), "FAIL")
    expect("schema catches open_comment with no close date",
           gate_schema([base(public_access={"room": "open_comment", "how": "x", "url": None})]),
           "FAIL")
    expect("schema catches a bad date kind",
           gate_schema([base(key_dates=[{"date": "2026-09-04", "kind": "someday"}])]), "FAIL")
    expect("schema catches a non-ISO date",
           gate_schema([base(key_dates=[{"date": "Sept 4 2026", "kind": "hearing"}])]), "FAIL")

    # A CANCELED SITTING IS A FIELD, AND THE PROSE MAY NOT DISAGREE WITH IT.
    # The site decides whether a date is still a door a reader can walk through. It read the
    # note with a regex to keep two canceled TCEQ hearings off that list, which worked and was
    # the generated-not-computed shape refused everywhere else here. The flag is the truth now
    # and this keeps the sentence honest against it.
    expect("schema catches a note saying canceled while the flag does not",
           gate_schema([base(key_dates=[{"date": "2026-09-04", "kind": "hearing",
                                         "note": "public meeting, since canceled"}])]), "FAIL")
    expect("...and passes once the flag agrees",
           gate_schema([base(key_dates=[{"date": "2026-09-04", "kind": "hearing",
                                         "canceled": True,
                                         "note": "public meeting, since canceled"}])]), "PASS")
    expect("...and a canceled date needs no note at all",
           gate_schema([base(key_dates=[{"date": "2026-09-04", "kind": "hearing",
                                         "canceled": True, "note": ""}])]), "PASS")
    expect("...while the flag must be a boolean, not a reason string",
           gate_schema([base(key_dates=[{"date": "2026-09-04", "kind": "hearing",
                                         "canceled": "yes"}])]), "FAIL")
    # THE FIXTURE'S ID MATTERS HERE, and it caught this test the moment the ratchet
    # landed: `base()` uses tx-2026-0001, which is one of the three backlogged items, so
    # the exemption swallowed the assertion and a test that had checked something for
    # weeks started passing for the wrong reason. Any id outside the backlog restores it.
    expect("schema catches an item that is nowhere",
           gate_schema([base(id="tx-2026-9999",
                             geography={"statewide": False, "counties": []})]), "FAIL")
    expect("...and `on_ercot` alone does NOT rescue it, being a property and not a place",
           gate_schema([base(id="tx-2026-9999",
                             geography={"statewide": False, "counties": [],
                                        "on_ercot": True})]), "FAIL")
    expect("...while a backlogged item is exempt, so the routine is not blocked out of a "
           "lane it does not own",
           gate_schema([base(id="tx-2026-0001",
                             geography={"statewide": False, "counties": [],
                                        "on_ercot": True})]), "PASS")
    expect("a county that is not a Texas county is refused",
           gate_schema([base(geography={"statewide": False, "counties": ["Taylr"]})]), "FAIL")
    expect("...and a real one is accepted",
           gate_schema([base(geography={"statewide": False, "counties": ["Taylor"]})]), "PASS")
    expect("a hand-typed metro that disagrees with the counties is refused",
           gate_schema([base(geography={"statewide": False, "counties": ["Taylor"],
                                        "metro": "Dallas-Fort Worth-Arlington, TX"})]), "FAIL")
    expect("schema catches a duplicate id",
           gate_schema([base(), base()]), "FAIL")
    expect("schema catches a missing decider name",
           gate_schema([base(decider={"name": "", "type": "state-agency"})]), "FAIL")

    expect("claims passes a sourced claim", gate_claims([base()]), "PASS")
    expect("claims catches an item with no claims", gate_claims([base(claims=[])]), "FAIL")
    expect("claims catches a claim with no quote", gate_claims([base(claims=[
        {"id": "c1", "text": "x", "verbatim_quote": "", "source_url": "https://a.b",
         "source_type": "primary_official"}])]), "FAIL")
    expect("claims catches a claim with no URL", gate_claims([base(claims=[
        {"id": "c1", "text": "x", "verbatim_quote": "q", "source_url": "see the filing",
         "source_type": "primary_official"}])]), "FAIL")

    expect("numerals passes a figure that is quoted", gate_numerals([base()]), "PASS")
    expect("numerals catches an invented figure",
           gate_numerals([base(summary="The queue holds 474 gigawatts of requests.")]), "FAIL")
    expect("numerals exempts an ordinal date",
           gate_numerals([base(summary="Comments close September 4th.")]), "PASS")
    # THE KEY DATE NOTE IS IN THIS GATE, and the name exemption is what let it in. Four cases,
    # and the last two are the ones that keep the exemption honest: it has to be EARNED against
    # a name the item's own evidence carries, and it must not travel to another item.
    _bcast = [{"id": "c1", "text": "t", "verbatim_quote": "A conditional use request was "
                                                          "approved.",
               "source_url": "https://www.newschannel6now.com/2026/08/11/datanovax/",
               "source_title": "DataNovaX data center approved", "source_type": "journalism",
               "fetched": "2026-08-11"}]
    expect("numerals reaches a key date note",
           gate_numerals([base(key_dates=[{"date": "2026-09-04", "kind": "reported",
                                           "note": "The plant draws 900 megawatts"}])]), "FAIL")
    expect("...and a two day date in one is still a date",
           gate_numerals([base(key_dates=[{"date": "2026-09-04", "kind": "hearing",
                                           "note": "Board sits September 4th and 5th"}])]),
           "PASS")
    expect("...and a broadcaster's own number is a name, not a figure",
           gate_numerals([base(claims=_bcast,
                               key_dates=[{"date": "2026-09-04", "kind": "reported",
                                           "note": "Date NewsChannel 6 reported the "
                                                   "approval"}])]), "PASS")
    expect("...but only on an item whose evidence carries that name",
           gate_numerals([base(key_dates=[{"date": "2026-09-04", "kind": "reported",
                                           "note": "Date NewsChannel 6 reported the "
                                                   "approval"}])]), "FAIL")
    expect("...and an invented station is refused on the item that cites the real one",
           gate_numerals([base(claims=_bcast,
                               key_dates=[{"date": "2026-09-04", "kind": "reported",
                                           "note": "Date NewsChannel 9 reported the "
                                                   "approval"}])]), "FAIL")
    expect("numerals exempts a bare year",
           gate_numerals([base(summary="The rule took effect in 2025.")]), "PASS")
    expect("numerals exempts a bill citation",
           gate_numerals([base(summary="The rule implements SB 6 of the 89th Legislature.")]),
           "PASS")
    expect("numerals exempts a docket citation",
           gate_numerals([base(summary="Filed under Project 58482 at the commission.")]), "PASS")
    # A doubled backslash in the CITATION pattern once let this through while every other
    # citation case still passed, because the other cases match an earlier alternative.
    expect("numerals exempts a PLURAL statute citation",
           gate_numerals([base(summary="Sections 2054.701 through 2054.705 conflict.")]),
           "PASS")
    expect("numerals exempts a cross reference to another item",
           gate_numerals([base(summary="See item tx-2026-0010 for the statutory basis.")]),
           "PASS")

    # CROSS REFERENCES. The numeral gate exempts an item id, correctly, because an id is an
    # identifier and not a figure. Nothing then checked that the id names anything. This
    # test's own fixture used tx-2026-0010, which is the very id the live record points at
    # and does not have, so the suite demonstrated the hole while asserting the exemption.
    two = [base(id="tx-2026-9999"), base(id="tx-2026-9998")]
    expect("cross references passes a pointer to an item that exists",
           gate_cross_references([base(id="tx-2026-9999",
                                       summary="See item tx-2026-9998 for more."), two[1]]),
           "PASS")
    expect("cross references catches a pointer to an item that does not",
           gate_cross_references([base(id="tx-2026-9999",
                                       summary="See item tx-2026-0010 for more.")]), "FAIL")
    expect("cross references does not trip on an item naming itself",
           gate_cross_references([base(id="tx-2026-9999",
                                       summary="Item tx-2026-9999 is this one.")]), "PASS")
    # THE RATCHET, BOTH WAYS. The one known break is exempt and nothing else is, including
    # a second break from the same item.
    expect("cross references exempts the one item on the backlog",
           gate_cross_references([base(id="tx-2026-0006",
                                       summary="See item tx-2026-0010 for more.")]), "PASS")
    expect("...and does not exempt a different dangling id from that same item",
           gate_cross_references([base(id="tx-2026-0006",
                                       summary="See item tx-2026-0011 for more.")]), "FAIL")
    expect("...and does not exempt that id when another item names it",
           gate_cross_references([base(id="tx-2026-9999",
                                       summary="See item tx-2026-0010 for more.")]), "FAIL")

    # THE BACKLOG IS VISIBLE. An exemption that reports nothing on a green build is not a
    # debt, it is a decision nobody revisits.
    check("backlog says nothing about a clean record",
          not backlog([base(id="tx-2026-9999")]))
    check("backlog names an exempted geography gap",
          any("tx-2026-0001" in ln for ln in backlog([base(id="tx-2026-0001",
                                                          geography={"on_ercot": True})])))
    check("backlog names an exempted dangling pointer",
          any("tx-2026-0010" in ln for ln in backlog(
              [base(id="tx-2026-0006", summary="See item tx-2026-0010 for more.")])))
    expect("numerals exempts a hearing room",
           gate_numerals([base(summary="Meetings are held in Commissioners Hearing Room 7-100.")]),
           "PASS")
    # THE EXEMPTION MUST NOT SWALLOW A REAL FIGURE. These three passed the gate while the place
    # rule also matched "Building" and "Floor", which are ordinary words in a docket about data
    # centers and the grid. An exemption wide enough to hide a published megawatt figure defeats
    # the one law this file exists to enforce.
    expect("...but 'Building' before a figure is prose, not an address",
           gate_numerals([base(summary="Building 500 megawatts of gas capacity was approved.")]),
           "FAIL")

    # THE REST OF THE ADDRESS. Each locator gets a case that must pass and a case that must
    # still fail, because the whole risk in widening this gate is a pattern that also matches a
    # measurement. Written as pairs so a future edit that loosens one is visible against the
    # negative beside it.
    for label, allowed, forbidden in [
        ("a street address",
         "Comments are heard at 1001 Preston Street, Houston.",
         "The campus will draw 1001 acre feet a year."),
        ("a post box",
         "Write to the Office of the Chief Clerk, P.O. Box 13087, Austin.",
         "The plant is rated 13087 horsepower."),
        ("a mail code",
         "Address it to MC-105 at the commission.",
         "The site sits on 105 acres."),
        ("a zip code",
         "The office is in Austin, Texas 78711-3087.",
         "The award totalled 78711 dollars."),
        ("a phone number",
         "The education program takes questions at 800-687-4040.",
         "The county granted 687 permits."),
        ("a time on a clock",
         "The hearing begins at 5:30 p.m. in the courtroom.",
         "The line carries 5.30 gigawatts at peak."),
        ("an instrument's file number",
         "The council adopted Ordinance No. 2026-078 that evening.",
         "The council approved it 4-1 that evening."),
        ("a coded permit number",
         "The application covers permit PSDTX1704 and its greenhouse gas twin.",
         "The turbines add 1704 megawatts to the site."),
    ]:
        expect(f"numerals exempts {label}", gate_numerals([base(summary=allowed)]), "PASS")
        expect(f"...and still catches a figure shaped like {label}",
               gate_numerals([base(summary=forbidden)]), "FAIL")

    # A DECIMAL MEASUREMENT IS A MEASUREMENT. `DOTTED_SECTION` used to read `\d{1,4}\.\d{1,4}`,
    # which is every decimal number there is, so these three were exempt from the day the gate
    # was written and nothing ever reported it. An over-wide exemption has no symptom.
    for figure in ("The ordinance caps fill at 8.0 gallons per square foot.",
                   "The station has recorded 22.61 inches of rain this year.",
                   "The line carries 5.30 gigawatts at peak."):
        expect(f"numerals catches an unquoted decimal: {figure.split()[-4]}",
               gate_numerals([base(summary=figure)]), "FAIL")
    expect("...while a statute section keeps its exemption",
           gate_numerals([base(summary="The rule amends 16 TAC 25.194 for large loads.")]),
           "PASS")
    expect("...and so does the far end of a cited range",
           gate_numerals([base(summary="It amends Sections 2054.701 through 2054.705 as well.")]),
           "PASS")
    # 37, not 12: the fixture's own claim quote reads "Project No. 58482, 12 filing(s)", so a 12
    # here is legitimately allowed and the case would pass for the wrong reason.
    expect("...and so is 'Floor' before a figure",
           gate_numerals([base(summary="Floor 37 percent of the load is served this way.")]),
           "FAIL")
    expect("...and a room number must actually be a number",
           gate_numerals([base(summary="Room enough for 40 more turbines.")]), "FAIL")
    expect("numerals allows a count COMPUTED from the record",
           gate_numerals([base(summary="The corridor crosses 3 counties.",
                               geography={"statewide": False, "counties": ["A", "B", "C"]})]),
           "PASS")
    expect("...but not a count that does not match the record",
           gate_numerals([base(summary="The corridor crosses 9 counties.",
                               geography={"statewide": False, "counties": ["A", "B", "C"]})]),
           "FAIL")

    expect("narration passes clean copy", gate_narration([base()]), "PASS")
    expect("narration catches first person",
           gate_narration([base(summary="We could not find a filing.")]), "FAIL")
    expect("narration catches machine talk",
           gate_narration([base(summary="This item is unverified.")]), "FAIL")
    expect("narration catches search narration",
           gate_narration([base(summary="No page anyone could reach lists the figure.")]),
           "FAIL")
    # THE NEGATED FORM, which this gate read past until 2026-08-18. Its branch was written
    # "could be verified" and the sentence somebody actually writes is "could not be verified",
    # so the one word that turns a fact into narration was the one word that let it through.
    expect("narration catches the negated verification phrase",
           gate_narration([base(summary="The meeting date could not be verified.")]), "FAIL")

    expect("house style passes clean copy", gate_house_style([base()]), "PASS")
    expect("house style catches a colon in a summary",
           gate_house_style([base(summary="The order sets one condition: file by the date.")]),
           "FAIL")
    expect("house style catches a semicolon in a summary",
           gate_house_style([base(summary="The rule is proposed; comments are open.")]), "FAIL")
    # The nested field is the one a reader acts on, and it is the field a writer forgets is
    # checked. A gate that reads the summary and not the instruction has a door in it.
    expect("house style reaches public_access.how",
           gate_house_style([base(public_access={
               "room": "open_comment", "how": "File under the project number; attach a PDF.",
               "url": None, "closes": "2026-09-04"})]), "FAIL")
    expect("house style catches a bare date",
           gate_house_style([base(summary="Comments close September 4.")]), "FAIL")

    # A STAMP WITH NO LINE BESIDE IT. Four items reached main in exactly this state one day
    # after the rule was written, because the rule lived in a prompt and nothing read the file.
    expect("movement passes a stamp that carries its line",
           gate_movement([base(last_verified="2026-08-19",
                               history=[{"date": "2026-08-19", "note": "Checked and unchanged."}])]),
           "PASS")
    expect("...and catches a stamp with no line for that date",
           gate_movement([base(last_verified="2026-08-19", history=[])]), "FAIL")
    expect("...and a line for the WRONG date does not satisfy it",
           gate_movement([base(last_verified="2026-08-19",
                               history=[{"date": "2026-08-18", "note": "Checked."}])]), "FAIL")
    # The exemption, and it is load bearing. Backfilling a check nobody recorded would be
    # inventing an observation, so items stamped before the rule are left alone.
    expect("...but an item stamped before the rule is exempt, never backfilled",
           gate_movement([base(last_verified="2026-08-11", history=[])]), "PASS")
    # THE KEY DATE NOTE, which renders on the timeline and was outside every gate on both
    # layers until 2026-08-18. Three cases, and the third is the point of the other two: the
    # construction rules apply to a fragment exactly as they apply to a sentence, and the comma
    # ceiling does not, because that number was measured on running prose and a label fragment
    # is not running prose. A note whose commas are structural has to keep passing or the split
    # was not made.
    expect("house style reaches a key date note",
           gate_house_style([base(key_dates=[
               {"date": "2026-08-21", "kind": "hearing",
                "note": "Open meeting — the board sits"}])]), "FAIL")
    expect("...and catches narration in one",
           gate_house_style([base(key_dates=[
               {"date": "2026-08-21", "kind": "hearing",
                "note": "Open meeting, the date could not be verified"}])]), "FAIL")
    expect("...and leaves a comma dense fragment alone",
           gate_house_style([base(key_dates=[
               {"date": "2026-08-21", "kind": "hearing",
                "note": "Regular City Council meeting, 9:00 AM, item scheduled for "
                        "discussion and action"}])]), "PASS")
    # A DATE CAN NAME TWO DAYS. The ordinal pattern read only the first, so the numeral gate
    # reported the second as a figure with no claim behind it. Nothing was wrong with the copy.
    expect("a two day date is a date, not a stray figure",
           gate_numerals([base(summary="The board meets in Austin on August 12th and 13th, "
                                       "2026.")]), "PASS")
    expect("house style catches an em dash",
           gate_house_style([base(summary="The rule is open — comments close soon.")]),
           "FAIL")
    expect("house style catches the parenthetical comma",
           gate_house_style([base(
               summary="A site needs power and, in most designs, water.")]), "FAIL")
    # A ratio and a clock time are the two colons that are not punctuation. Failing them would
    # push a writer to rephrase a correct figure, which is the gate making the copy worse.
    expect("house style allows a clock time",
           gate_house_style([base(summary="The hearing starts at 9:30 in the morning.")]),
           "PASS")

    expect("staleness passes a fresh item", gate_staleness([base()], today), "PASS")
    # today is 2026-08-11 here, so every fixture date sits before it. The bands are the whole
    # reason this gate exists, so they are asserted at their exact edges rather than left to
    # whatever the defaults happen to be.
    expect("an item inside the two day leash passes",
           gate_staleness([base(last_verified="2026-08-09")], today), "PASS")
    expect("the day it goes past the leash it warns, not fails",
           gate_staleness([base(last_verified="2026-08-08")], today), "WARN")
    expect("six days is still the warn band",
           gate_staleness([base(last_verified="2026-08-05")], today), "WARN")
    expect("seven days is the hard band",
           gate_staleness([base(last_verified="2026-08-04")], today), "FAIL")
    expect("staleness FAILS far past the outer band",
           gate_staleness([base(last_verified="2025-12-01")], today), "FAIL")

    # THE DISTINCTION THE BUILDER DEPENDS ON. A stale record is loud everywhere and stops only
    # the ship, never the rebuild. Anything that would make the OUTPUT wrong still stops both.
    stale_only = [base(last_verified="2025-12-01")]
    n_all, _ = run_gates(stale_only, today)
    n_block, _ = run_gates(stale_only, today, blocking_only=True)
    check("a stale record fails validate", n_all >= 1, str(n_all))
    check("...and does NOT stop a rebuild", n_block == 0, str(n_block))

    broken = [base(last_verified=today, topic="not-a-real-topic")]
    n_all_b, _ = run_gates(broken, today)
    n_block_b, _ = run_gates(broken, today, blocking_only=True)
    check("a record that would render WRONG fails validate", n_all_b >= 1, str(n_all_b))
    check("...and DOES stop a rebuild", n_block_b >= 1, str(n_block_b))

    expect("deadlines passes a parseable close date", gate_deadlines([base()], today), "PASS")
    expect("deadlines catches an unparseable close date", gate_deadlines(
        [base(public_access={"room": "open_comment", "how": "x", "url": None,
                             "closes": "Sept 4"})], today), "FAIL")

    # Derived state: the same item reads open before its date and closed after, with no edit.
    live = base()
    ws_open = window_state(live, "2026-08-11")
    ws_shut = window_state(live, "2026-09-05")
    ok = ws_open == "open" and ws_shut == "closed"
    print(f"  {'ok  ' if ok else 'FAIL'}  window_state derives open then closed from one record")
    if not ok:
        failures += 1

    proj = project([base()], today)
    ok = (proj["counts"]["items"] == 1 and proj["counts"]["claims"] == 1
          and proj["actionable_now"][0]["days_left"] == 24)
    print(f"  {'ok  ' if ok else 'FAIL'}  projection computes counts and days_left")
    if not ok:
        failures += 1

    # PROMOTION IS ONE ATOMIC, IDEMPOTENT MERGE.
    #
    # The old command stopped after reporting what passed. A run then copied JSON into the live
    # ledger by hand, outside every guarantee this file had just established. These fixtures
    # exercise the actual write boundary: preserve the published prefix, append only a new id,
    # leave the seed alone, make a rerun byte-identical, ignore a historical seed copy instead
    # of overwriting its published item, and leave both inputs untouched on a combined failure.
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        seed = tmp / "seed.json"
        published = tmp / "ledger.json"

        older = base(id="tx-2026-0999")
        admitted_item = base(
            id="tx-2026-0998",
            summary="The commission proposed a new rule. See item tx-2026-0999 for the "
                    "earlier filing. Comments close September 4th.")
        seed.write_text(json.dumps([admitted_item], indent=1) + "\n", encoding="utf-8")
        published.write_text(json.dumps(
            {"_spec": {"version": SPEC_VERSION, "generated": today, "gates": []},
             "items": [older]}, indent=1) + "\n", encoding="utf-8")
        seed_before = seed.read_bytes()

        rc = promote(seed, today, ledger_path=published)
        merged = load_record(published)["items"]
        check("promote appends an item whose reference resolves in the published ledger",
              rc == 0 and merged == [older, admitted_item])
        check("...without changing any published item", merged[0] == older)
        check("...and without changing the candidate seed", seed.read_bytes() == seed_before)

        ledger_once = published.read_bytes()
        rc = promote(seed, today, ledger_path=published)
        check("a second promotion is byte-identical", rc == 0 and
              published.read_bytes() == ledger_once)

        # A reused id is a historical candidate copy, not permission to revise the record.
        collision = base(id=older["id"], title="A seed copy must never replace this title")
        seed.write_text(json.dumps([collision], indent=1) + "\n", encoding="utf-8")
        collision_seed = seed.read_bytes()
        collision_ledger = published.read_bytes()
        rc = promote(seed, today, ledger_path=published)
        check("a published-id collision never overwrites the ledger", rc == 0 and
              published.read_bytes() == collision_ledger)
        check("...and the historical seed copy stays available", seed.read_bytes() == collision_seed)

        # Each row passes by itself; only the combined schema sees that two new rows reuse an
        # id. That failure must happen before the atomic write and leave both files untouched.
        duplicate_a = base(id="tx-2026-0997")
        duplicate_b = base(id="tx-2026-0997", title="A different item using the same id")
        seed.write_text(json.dumps([duplicate_a, duplicate_b], indent=1) + "\n",
                        encoding="utf-8")
        failed_seed = seed.read_bytes()
        failed_ledger = published.read_bytes()
        rc = promote(seed, today, ledger_path=published)
        check("combined validation refuses duplicate candidate ids", rc == 1)
        check("...and a refused merge leaves the ledger byte-identical",
              published.read_bytes() == failed_ledger)
        check("...and leaves the seed byte-identical", seed.read_bytes() == failed_seed)

        # A filesystem failure at the final boundary has the same rollback property. Inject
        # only the replace operation; the production path still uses os.replace.
        atomic_target = tmp / "atomic.json"
        atomic_target.write_text("before\n", encoding="utf-8")

        def refuse_replace(_source, _target):
            raise OSError("planted replacement failure")

        raised = False
        try:
            _atomic_write_text(atomic_target, "after\n", replace=refuse_replace)
        except OSError:
            raised = True
        check("an atomic replacement failure is raised", raised)
        check("...leaves the old target byte-identical",
              atomic_target.read_text(encoding="utf-8") == "before\n")
        check("...and cleans up its prepared temporary file",
              not list(tmp.glob(".atomic.json.*.tmp")))

    if failures:
        print(f"\ndocket_build self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\ndocket_build self-test: all passed (every gate can go red)")
    return 0


# --------------------------------------------------------------------------- promote
def promote(seed_path: Path, today: str, ledger_path: Path = LEDGER,
            require_primary: bool = True) -> int:
    """THE GATES ARE THE REVIEWER, AND THE WRITE IS ONE TRANSACTION.

    Nothing here waits on somebody to read a report. An item enters the public record when it
    passes every gate and clears the admission bar below, and it stays out otherwise. The held
    items are printed so the reason is on the record, not so that a person can override it.

    The admission bar, deliberately stricter than the gates:
      - every gate passes
      - confidence is high
      - at least one claim cites a PRIMARY source, not journalism alone

    That last rule is the one doing the real work. Journalism is fine for finding an item and
    fine as corroboration, but a public record whose entries rest on headlines is a clippings
    file. A held item is not lost: it stays in the seed with its reason, and a later pass that
    finds the primary source promotes it automatically.

    Rows whose ids already exist in the ledger are historical candidate copies. They are not
    candidates for an update: the published item wins even when the seed copy differs. New ids
    that clear admission are appended in seed order, the entire combined record is gated, and
    only then is the ledger atomically replaced. The seed is never written here, making a rerun
    both safe and byte-identical when nothing new clears the bar.
    """
    if not ledger_path.exists():
        print(f"promotion: ledger does not exist at {ledger_path}", file=sys.stderr)
        return 2

    record = load_record(ledger_path)
    published = record["items"]
    published_by_id = {it.get("id"): it for it in published if it.get("id")}
    items = load(seed_path)
    provisional, admitted, held, historical = [], [], [], []
    for it in items:
        item_id = it.get("id")
        if item_id and item_id in published_by_id:
            historical.append((item_id, it != published_by_id[item_id]))
            continue
        _, results = run_gates([it], today)
        # Cross references are a COLLECTION property. A candidate may correctly point at a
        # published item or at another candidate that clears the same pass, so judging it in
        # isolation would hold a valid row. Decide every item-local gate first, then resolve
        # references against the published ids plus the whole provisional admitted set.
        local_failures = [r for r in results
                          if r.status == "FAIL" and r.name != "cross references"]
        reasons = [line for result in local_failures for line in result.lines]
        if local_failures:
            held.append((item_id, reasons[0] if reasons else "a gate failed"))
            continue
        if it.get("confidence") != "high":
            held.append((item_id, f"confidence is '{it.get('confidence')}'"))
            continue
        kinds = {c.get("source_type") for c in it.get("claims", [])}
        if require_primary and not (kinds & {"primary_official", "primary_corporate"}):
            held.append((item_id, "no primary source; every claim is journalism"))
            continue
        provisional.append(it)

    provisional_ids = {it.get("id") for it in provisional if it.get("id")}
    reference_ids = set(published_by_id) | provisional_ids
    for it in provisional:
        references = gate_cross_references([it], known_ids=reference_ids)
        if references.status == "FAIL":
            held.append((it.get("id"), references.lines[0]))
        else:
            admitted.append(it)

    candidates = len(items) - len(historical)
    print(f"admitted {len(admitted)} of {candidates} seed-only candidate(s); "
          f"held {len(held)}; already published {len(historical)}")
    for i, why in held:
        print(f"  HELD  {i}: {why}")
    changed_history = [item_id for item_id, differs in historical if differs]
    if changed_history:
        print(f"  PUBLISHED  {len(changed_history)} historical seed copy/copies differ; "
              "the ledger wins and is never overwritten")
        for item_id in changed_history[:8]:
            print(f"             {item_id}")
        if len(changed_history) > 8:
            print(f"             ...and {len(changed_history) - 8} more")

    combined = published + admitted
    bad, results = run_gates(combined, today)
    if bad:
        print("\nrefusing promotion: the combined ledger does not pass every gate",
              file=sys.stderr)
        report(results)
        return 1

    if not admitted:
        print("\nledger unchanged: no new item cleared admission")
        return 0

    payload = dict(record)
    spec = dict(record.get("_spec") or {})
    spec.update({"version": SPEC_VERSION, "generated": today,
                 "gates": sorted(list(GATES) + list(DATED_GATES))})
    payload["_spec"] = spec
    payload["items"] = combined
    text = json.dumps(payload, indent=1, ensure_ascii=False) + "\n"
    _atomic_write_text(ledger_path, text)
    try:
        shown = ledger_path.resolve().relative_to(REPO_ROOT)
    except ValueError:
        shown = ledger_path
    print(f"\npromoted {len(admitted)} new item(s) into {shown}; "
          f"ledger now holds {len(combined)}; seed unchanged")
    return 0


# --------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--project", action="store_true")
    ap.add_argument("--promote", metavar="FILE")
    ap.add_argument("--ledger", default=str(LEDGER),
                    help="record to validate, project or atomically promote into")
    ap.add_argument("--today", default=_dt.date.today().isoformat())
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if args.promote:
        return promote(Path(args.promote), args.today, Path(args.ledger))

    path = Path(args.ledger)
    if not path.exists():
        print(f"docket: no ledger at {path}", file=sys.stderr)
        return 2
    items = load(path)

    if args.project:
        print(json.dumps(project(items, args.today), indent=2, ensure_ascii=False))
        return 0

    print(f"docket  {path}")
    bad, results = run_gates(items, args.today)
    report(results)
    print("\ndocket: FAILED" if bad else "\ndocket: clean")
    return 1 if bad else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                  # noqa: BLE001
        print(f"docket_build: broke: {exc}", file=sys.stderr)
        sys.exit(2)
