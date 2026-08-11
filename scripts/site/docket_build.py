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


def _reader_text(item: dict) -> str:
    return " ".join(str(item.get(f, "")) for f in READER_COPY_FIELDS)


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
    stripped = DATE_ORDINAL.sub(" ", text)
    stripped = CITATION.sub(" ", stripped)
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

        g = it.get("geography") or {}
        if not (g.get("statewide") or g.get("counties") or g.get("on_ercot")):
            r.fail(f"{who}: geography names no county, not statewide, and not the ERCOT "
                   f"region. Every item is somewhere")
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
    "narration": gate_narration,
}
DATED_GATES = {"staleness": gate_staleness, "deadlines": gate_deadlines}


# --------------------------------------------------------------------------- projection
def project(items: list, today: str) -> dict:
    """The render-ready shape. Every count here is COMPUTED, which is what lets the site
    publish a numeral at all."""
    t = _dt.date.fromisoformat(today)
    by_topic, by_county, by_room, by_status = {}, {}, {}, {}
    actionable = []
    for it in items:
        by_topic[it["topic"]] = by_topic.get(it["topic"], 0) + 1
        by_status[it["status"]] = by_status.get(it["status"], 0) + 1
        room = it["public_access"]["room"]
        by_room[room] = by_room.get(room, 0) + 1
        for c in (it.get("geography") or {}).get("counties") or []:
            by_county[c] = by_county.get(c, 0) + 1
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
        },
        "by_county": dict(sorted(by_county.items())),
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
    expect("schema catches an item that is nowhere",
           gate_schema([base(geography={"statewide": False, "counties": []})]), "FAIL")
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
