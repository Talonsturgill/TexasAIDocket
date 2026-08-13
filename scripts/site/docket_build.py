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

  5 STALENESS   two bands. Past 45 days an item is due for a re-check; past 120 it is a HARD
                FAIL, because publishing a four month old item as current is a false claim.
  6 DEADLINES   close dates must parse. Whether a window is OPEN is never stored, it is derived
                from the date on every build, so it cannot rot between runs.

NOTHING HERE WAITS ON SOMEONE TO READ A REPORT. The gates are the reviewer: an item enters the
public record when it passes them and stays out when it does not. That is why a warning nobody
would read is either promoted to a failure or replaced by derived state.

    docket_build.py --self-test              prove every gate can go red
    docket_build.py --validate               run the gates against ledger/docket.json
    docket_build.py --promote SEED --out F   admit what passes, write it, hold the rest
    docket_build.py --project                emit the render projection to stdout

EXIT CODES
    0  clean            1  a gate failed            2  the tool itself broke
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "ledger" / "docket.json"

# The house rules live with the caption linter, because they govern every surface and that is
# where they were first written down. Imported once at module scope rather than inside the gate:
# an insert per call left one duplicate path entry per invocation, and it also hid the
# dependency from the wiring gate, which reads imports.
sys.path.insert(0, str(REPO_ROOT / "scripts" / "carousel"))
import caption_check                                               # noqa: E402

SPEC_VERSION = 1

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
    r"(?:could|couldn't|can't) be verified|not verified|unverified|"
    r"i |i'm |we |we're |our |us )",
    re.IGNORECASE,
)

# Any digit run, with thousands separators, decimals and a trailing percent. Ordinals in dates
# ("August 11th") are handled by the date-form exemption below.
NUMERAL = re.compile(r"\d[\d,]*(?:\.\d+)?%?")

# House style writes dates as "August 11th". Those ordinals are not published figures and must
# not be forced into a claim quote.
DATE_ORDINAL = re.compile(
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|"
    r"December)\s+\d{1,2}(?:st|nd|rd|th)\b",
    re.IGNORECASE,
)
# A bare four-digit year in prose is a date, not a measurement.
YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
# A statute or docket citation is an identifier, not a measurement: SB 6, HB 149, Project 58482,
# Chapter 2054, Section 39.151, Docket 59315.
CITATION = re.compile(
    r"\b(?:SB|HB|SJR|HJR)\s*\d+[A-Za-z]?\b|"
    r"\b(?:Projects?|Dockets?|Control Numbers?|Chapters?|Sections?|Subchapters?|"
    r"Articles?|Rules?|Items?)\s*"
    r"(?:No\.?\s*)?[\d.]+[A-Za-z]?\b|"
    r"\b\d{1,3}(?:st|nd|rd|th)\s+Legislature\b|"
    r"\b\d+R\b",
    re.IGNORECASE,
)

# A dotted number in this domain is a statute section, never a measurement: 2054.702, 39.151,
# 36.116. It needs its own rule because a RANGE leaves the second number bare, and stripping
# "Sections 2054.701 through 2054.705" with CITATION alone catches the first and not the second.
# The bare 2054 then reads as a year, leaving a stray 705 that looks like a published figure.
DOTTED_SECTION = re.compile(r"\b\d{1,4}\.\d{1,4}[A-Za-z]?\b")

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
# a docket about data centres and the grid they are ordinary English words that are frequently
# followed by a figure. Case-insensitively, "Building 500 megawatts of new gas capacity was
# approved" had its 500 stripped before the numeral gate ever saw it, and the gate reported
# clean. An exemption that swallows a published figure is worse than no exemption, because the
# law this file enforces is that no numeral reaches a reader unquoted and uncomputed.
#
# The identifier must also start with a DIGIT. "Room" followed by a word is prose.
PLACE_NUMBER = re.compile(r"\b(?:Rooms?|Suites?)\s+(?:No\.?\s*)?\d[\dA-Za-z]*(?:-[\dA-Za-z]+)*\b",
                          re.IGNORECASE)

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


def _reader_text(item: dict) -> str:
    parts = [str(item.get(f, "")) for f in READER_COPY_FIELDS]
    for outer, inner in READER_COPY_NESTED:
        parts.append(str((item.get(outer) or {}).get(inner, "")))
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


def _prose_numerals(text: str) -> list:
    """Numerals in prose, minus dates, years and citations, which are identifiers not figures."""
    # Order matters. Dotted sections go before YEAR, or "2054.705" loses its "2054" to the
    # year rule and leaves a bare "705" that reads as a published figure.
    stripped = ITEM_ID.sub(" ", text)
    stripped = DATE_ORDINAL.sub(" ", stripped)
    stripped = CITATION.sub(" ", stripped)
    stripped = PLACE_NUMBER.sub(" ", stripped)
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
        for field in ("id", "title", "summary", "topic", "decider", "geography",
                      "status", "key_dates", "public_access", "claims", "last_verified"):
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
    """
    r = Result("numerals")
    checked = 0
    for it in items:
        who = it.get("id", "?")
        allowed = _quoted_numerals(it)
        for got in _prose_numerals(_reader_text(it)):
            checked += 1
            if got not in allowed:
                r.fail(f"{who}: numeral '{got}' appears in reader copy but in no claim quote. "
                       f"Quote it or cut it")
    if r.status == "PASS":
        r.note(f"{checked} numeral(s) in copy, all traceable to a quote")
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
    if r.status == "PASS":
        r.note(f"{len(items)} item(s) keep the house rules")
    return r


def gate_staleness(items: list, today: str,
                   warn_days: int = 45, fail_days: int = 120) -> Result:
    """Two bands, and the outer one is a HARD FAIL.

    A warning nobody reads is a warning that does nothing. Past `fail_days` an item has not been
    re-checked in four months and is being published as current anyway, which is the record
    quietly becoming untrue. The build stops rather than shipping it.

    The warn band is what a re-verification pass should be picking up first.
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


GATES = {
    "schema": gate_schema, "claims": gate_claims, "numerals": gate_numerals,
    "narration": gate_narration, "house style": gate_house_style,
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


def run_gates(items: list, today: str) -> tuple[int, list]:
    results = [g(items) for g in GATES.values()]
    results += [g(items, today) for g in DATED_GATES.values()]
    bad = sum(1 for r in results if r.status == "FAIL")
    return bad, results


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
    expect("numerals exempts a hearing room",
           gate_numerals([base(summary="Meetings are held in Commissioners Hearing Room 7-100.")]),
           "PASS")
    # THE EXEMPTION MUST NOT SWALLOW A REAL FIGURE. These three passed the gate while the place
    # rule also matched "Building" and "Floor", which are ordinary words in a docket about data
    # centres and the grid. An exemption wide enough to hide a published megawatt figure defeats
    # the one law this file exists to enforce.
    expect("...but 'Building' before a figure is prose, not an address",
           gate_numerals([base(summary="Building 500 megawatts of gas capacity was approved.")]),
           "FAIL")
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
    expect("staleness warns in the first band",
           gate_staleness([base(last_verified="2026-06-15")], today), "WARN")
    expect("staleness FAILS past the outer band",
           gate_staleness([base(last_verified="2025-12-01")], today), "FAIL")

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

    if failures:
        print(f"\ndocket_build self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\ndocket_build self-test: all passed (every gate can go red)")
    return 0


# --------------------------------------------------------------------------- promote
def promote(seed_path: Path, today: str, out: Path | None = None,
            require_primary: bool = True) -> int:
    """THE GATES ARE THE REVIEWER.

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
    """
    items = load(seed_path)
    admitted, held = [], []
    for it in items:
        bad, results = run_gates([it], today)
        reasons = [l for r in results if r.status == "FAIL" for l in r.lines]
        if bad:
            held.append((it.get("id"), reasons[0]))
            continue
        if it.get("confidence") != "high":
            held.append((it.get("id"), f"confidence is '{it.get('confidence')}'"))
            continue
        kinds = {c.get("source_type") for c in it.get("claims", [])}
        if require_primary and not (kinds & {"primary_official", "primary_corporate"}):
            held.append((it.get("id"),
                         "no primary source; every claim is journalism"))
            continue
        admitted.append(it)

    print(f"admitted {len(admitted)} of {len(items)}; held {len(held)}")
    for i, why in held:
        print(f"  HELD  {i}: {why}")

    if out:
        bad, results = run_gates(admitted, today)
        if bad:
            print("\nrefusing to write: the admitted set does not pass as a whole",
                  file=sys.stderr)
            report(results)
            return 1
        payload = {
            "_spec": {"version": SPEC_VERSION, "generated": today,
                      "gates": sorted(list(GATES) + list(DATED_GATES))},
            "items": admitted,
        }
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8")
        try:
            shown = out.resolve().relative_to(REPO_ROOT)
        except ValueError:
            shown = out
        print(f"\nwrote {shown} with {len(admitted)} item(s)")
    return 0


# --------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--project", action="store_true")
    ap.add_argument("--promote", metavar="FILE")
    ap.add_argument("--out", metavar="FILE",
                    help="with --promote, write the admitted set here")
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--today", default=_dt.date.today().isoformat())
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if args.promote:
        return promote(Path(args.promote), args.today,
                       Path(args.out) if args.out else None)

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
