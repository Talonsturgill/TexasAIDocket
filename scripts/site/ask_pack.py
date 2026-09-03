#!/usr/bin/env python3
"""ask_pack.py — the published record, rendered as prose for one prompt.

WHAT THIS IS. The written answer lane publishes the whole record, plus a complete index of what
it holds. The worker always sends the index and retrieves only the bodies a question needs. The
data center bodies live in a sibling field so the bounded retrieval-off fallback cannot overflow
one context. Normal retrieval still sees every body and every sourced facility fact.

WHY PROSE AND NOT THE JSON. Three reasons, and the third is the one that keeps being
rediscovered.

  1. JSON spends a quarter of its bytes on keys, braces and quotes, and every one of those is
     paid on every question.
  2. Fields the model never uses can be dropped. Claims carry a source url, a source title, a
     source type and a fetch date, which together are 35 percent of the claims payload and
     57 percent of the ledger. An answer cites a decision and never a raw url, so none of it
     belongs in a prompt. Only 95 distinct urls exist across 234 claims, so most of that
     weight was the same link written out again.
  3. THE MODEL IMITATES WHAT IT IS SHOWN. This is why the pack is written in the house voice
     rather than as labelled fields. A pack full of colons produces answers full of colons,
     and this house bans colons in published copy, so the checker would then refuse the
     model's own reply. Same for dates. The pack writes "July 9th, 2026" because a pack full
     of ISO stamps produces answers full of ISO stamps.

SIZE IS A HARD GATE, NOT A WARNING. The index is paid on every question. The core pack is the
bounded retrieval-off fallback. Raising either ceiling is never a fix for a red build.

The authorised numeral list is derived FROM THIS TEXT by ask_corpus, so the guard's promise is
exact: the model may state a number only if that number was in what it was shown. Feeds are
summarised to their current reading and never pasted in whole. docs/weather.json alone is
231,769 bytes of time series, and authorising all of it would admit nearly every small number
that exists, at which point an invented figure passes by coincidence.
"""

import argparse
import datetime as _dt
import json
import os
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import docket_build as dk                                          # noqa: E402
import facility_dossier as fd                                      # noqa: E402

LEDGER = Path(REPO) / "ledger" / "docket.json"
DOCS = Path(REPO) / "docs"

# TWO CEILINGS, BECAUSE THE ONE THAT USED TO MEASURE THE BILL STOPPED MEASURING ANYTHING.
#
# There was one number here and its comment priced it at about 11 cents a cold question,
# because the whole pack went into every question. Wave 3 made that false and left the comment
# standing. The pack is now sent to NOBODY. What every question pays for is the index plus a
# slice capped in the worker, so the index is the number that bills and the pack is the number
# that does not.
#
# Keeping the ceiling on the pack alone measures the wrong thing in both directions. It blocks
# work for a cost nobody pays, which is what it did when the dossiers and the register were
# added and it went red at 331,000 characters over a bill that had not moved. And it lets the
# index grow without limit for a cost everybody pays.
#
# THE PACK CEILING now guards one thing, which is the ASK_RETRIEVAL=off escape hatch. That
# sends the whole pack, so this is the size of the worst question the box can be asked to
# answer with retrieval switched off, about 100,000 tokens, roughly 20 cents. It is a
# break-glass and it is allowed to be expensive. It is not allowed to be unbounded.
MAX_CHARS = 420_000

# THE INDEX CEILING is where the money is. Every question carries the whole index whatever it
# asked, which is the safety property this design is built on and the reason it can never be a
# slice. At roughly 4 characters a token 40,000 is about 10,000 tokens a question. It is
# CACHED, so a repeat question reads it at a tenth of the price, and a cold one pays in full.
#
# Raising this is a real decision about a real bill, unlike the number above it. The way to
# make room is to roll a family up rather than to index it line by line, which is what the
# construction register and the reservoirs already do, and what a family arriving later should
# do before this number is touched.
MAX_INDEX_CHARS = 40_000

# The facility bodies remain complete for normal retrieval. They are carried beside the core
# pack because one hundred fifty dossiers no longer fit inside its retrieval-off context bound.
# A second field costs no model tokens until the retriever chooses one of its blocks.
FACILITY_PACK_MARK = "THE DATA CENTER DOSSIERS."

MONTHS = ("January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December")

TOPIC_WORDS = {
    "power-and-the-grid": "power and the grid",
    "data-centers": "data centers",
    "state-policy": "state policy",
    "surveillance-and-policing": "surveillance and policing",
    "health-and-education": "health and education",
    "land-water-and-permitting": "land, water and permitting",
    "research-and-science": "research and science",
    "defense-and-federal": "defense and federal",
}

KIND_WORDS = {
    "filed": "filed",
    "comment_opens": "comments opened",
    "comment_closes": "comments close",
    "decided": "decided",
    "effective": "takes effect",
    "hearing": "hearing",
    "meeting": "meeting",
}

ROOM_WORDS = {
    "open_comment": "an open comment room",
    "open_meeting": "an open meeting",
    "hearing": "a hearing",
    "none": "no public room",
}


def ordinal(n: int) -> str:
    """1 -> 1st. The house writes dates month first with the ordinal, always."""
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }"


def longdate(iso: str) -> str:
    """2026-07-09 -> July 9th, 2026.

    Rendered rather than passed through because the model copies the shape it is shown, and
    an ISO stamp in an answer is a house style violation on a reader facing surface. The
    numerals survive the change: 2026-07-09 and July 9th, 2026 normalise to the same set.
    """
    try:
        d = _dt.date.fromisoformat(iso)
    except (TypeError, ValueError):
        return str(iso)
    return f"{MONTHS[d.month - 1]} {ordinal(d.day)}, {d.year}"


_URL = __import__("re").compile(r"\s*\(?\bhttps?://\S+\)?")


def deurl(text: str) -> str:
    """Ledger prose with its links taken out.

    The model is told never to write a bare url, so showing it one is downside with a token
    bill attached. Where a url is the whole point of a sentence the surrounding words already
    say where to look, which is what a reader needs.
    """
    return _URL.sub("", text or "").replace(" ,", ",").replace("  ", " ").strip()


def _sentences(parts: list) -> str:
    """Join non-empty fragments into sentences, each ending in a full stop."""
    out = []
    for p in parts:
        if not p:
            continue
        p = p.strip()
        if not p.endswith((".", "?", "!")):
            p += "."
        out.append(p)
    return " ".join(out)


def where(geo: dict) -> str:
    """An item's place, in words.

    Areas are NOT read off the item. The site derives them from the gazetteer and so does the
    engine, so a third derivation here is a third thing to drift.
    """
    counties = geo.get("counties") or []
    bits = []
    if geo.get("statewide"):
        bits.append("This one is statewide")
    elif counties:
        named = ", ".join(counties[:-1]) + " and " + counties[-1] if len(counties) > 1 \
            else counties[0]
        bits.append(f"The counties named are {named}")
    else:
        bits.append("No county is named on the record and it is not marked statewide")
    if geo.get("on_ercot"):
        bits.append("It sits on the ERCOT grid")
    return _sentences(bits)


def tally(items: list, today: str) -> str:
    """The counts, computed here rather than left for the model to do by hand.

    A COUNTING QUESTION IS THE ONE A RECORD PRODUCT SHOULD BE BEST AT AND A MODEL IS WORST AT.
    Asked how many decisions involve data centers, the answer came back empty: 58 records were
    in front of it, 19 of them carry that topic, and counting instances scattered through
    150,000 characters is exactly the arithmetic a language model gets wrong or declines.

    So the arithmetic is done in Python, from the same list the pages are built from, and the
    model is handed the result. Nothing here is a new fact. Every line is a count of records
    already below, which is why it can be checked by reading the rest of the pack.
    """
    from collections import Counter
    topics = Counter(it["topic"] for it in items)
    statuses = Counter(it["status"] for it in items)
    deciders = Counter(it["decider"]["name"] for it in items)
    open_now = [it for it in items if dk.window_state(it, today) == "open"]
    counties = Counter(c for it in items
                       for c in ((it.get("geography") or {}).get("counties") or []))
    statewide = sum(1 for it in items if ((it.get("geography") or {}).get("statewide")))
    ercot = sum(1 for it in items if ((it.get("geography") or {}).get("on_ercot")))

    lines = [
        f"The record holds {len(items)} decisions in total",
        "By topic, " + ", ".join(
            f"{TOPIC_WORDS.get(k, k.replace('-', ' '))} {v}"
            for k, v in sorted(topics.items(), key=lambda x: (-x[1], x[0]))),
        "By status, " + ", ".join(f"{k} {v}" for k, v in sorted(statuses.items())),
        f"{statewide} are statewide and {ercot} sit on the ERCOT grid",
        f"{len(counties)} counties are named across the record",
        "The deciders appearing more than once are " + ", ".join(
            f"{k} {v}" for k, v in sorted(deciders.items(), key=lambda x: (-x[1], x[0]))
            if v > 1),
    ]
    if open_now:
        lines.append(
            f"{len(open_now)} public windows are open today, which are "
            + ", ".join(f"[[{it['id']}]] closing "
                        f"{longdate(((it.get('public_access') or {}).get('closes')))}"
                        for it in open_now))
    else:
        lines.append("No public window is open today")
    return "THE COUNTS, computed from the records below.\n" + _sentences(lines)


# WHY THE HEADER BELOW SAYS WHAT A LINE CARRIES, AND WHY THAT REASONING IS HERE.
#
# It used to say a line "names what exists and never the detail", which was false: a line lists
# the topic, the decider, the status and every county. A reader asking which decisions were in
# Erath County was told the record did not answer that, while Erath sat in the county list on
# that very line. The model had been told to disregard the field holding the answer, so it went
# hunting through fourteen retrieved bodies for a county name buried in prose.
#
# THE FIRST FIX PUT THAT STORY IN THE PROMPT and it does not belong there. A prompt is read
# literally, the discarded rule was quoted inside it in the past tense, and the example carried
# a live citation the page would render. This file's own doctrine is that the model writes what
# it reads, which is an argument against showing it the wrong rule at all, however it is
# framed. It is also paid for on every question forever.
#
# So the prompt states what is true and this comment holds why.
INDEX_HEAD = """THE INDEX. Everything the record holds, in four sections.

Every decision, one line each, in the order they are filed. Each line carries the decision's
title, then its topic, its decider, its status, the counties it names or that it is statewide,
whether it sits on the ERCOT grid, and whether a public window is open, and it ends with the id
to cite it by.

Then the data center dossiers, the construction register and the reservoirs, each ROLLED UP
rather than listed, because a hundred and fifty dossiers, sixty one counties and a hundred and
thirty eight reservoirs read better as one block carrying all of their names than as hundreds
of lines. The construction and reservoir lines carry the figure itself, so a question about how
full a reservoir is or how many projects a county has is answered from the line. The dossier
block is grouped by county, so a question about which data centers sit in a named county is
answered from the block and the full dossier for the ones a question needs is retrieved below.
Dossiers whose filing publishes no county are printed together at the end of the block.

ANSWER FROM THESE LINES WHENEVER THEY CARRY WHAT WAS ASKED. A question about which decisions
name a county, who decided something, what is open, what a decision is called, how full a
reservoir is or how much construction a county has is answered here, completely, and looking
for it in the full text below is the slower way to get it wrong.

The full text of whatever is most likely to answer this question follows below, and it is a
SLICE. Something appearing here with no text below is still real and still carried by this
record. Never state a figure, a date or a quote for it beyond what its line says, because the
line is all there is to go on.

This index is a list. It is not a model for how to write, so do not answer in this shape."""


def index_line(it: dict, today: str) -> str:
    """One decision, compressed to what tells a reader whether it is the one they mean.

    ID, title, topic, decider, status, place, window. Nothing else, and no figures beyond the
    closing date of a window that is open, because a line is not evidence and a number on it
    would authorise itself for an item whose body the model was never shown.
    """
    geo = it.get("geography") or {}
    pa = it.get("public_access") or {}
    dec = it.get("decider") or {}
    counties = geo.get("counties") or []

    bits = [TOPIC_WORDS.get(it["topic"], it["topic"].replace("-", " ")),
            dec.get("name", "not recorded"),
            it.get("status", "unknown")]
    if geo.get("statewide"):
        bits.append("statewide")
    elif counties:
        bits.append(" and ".join(counties) if len(counties) < 3
                    else ", ".join(counties[:-1]) + " and " + counties[-1])
    if geo.get("on_ercot"):
        bits.append("on the ERCOT grid")

    state = dk.window_state(it, today)
    if state == "open":
        closes = pa.get("closes")
        bits.append(f"open until {longdate(closes)}" if closes else "open now")
    elif state == "closed":
        bits.append("window closed")

    # THE ID GOES LAST, AND IT IS NOT COSMETIC. The page renders a citation as the decision's
    # NAME, so "[[id]] is the PUCT Docket 59315 application" reaches a reader as "PUCT Docket
    # 59315 is the PUCT Docket 59315 application". Telling the model not to do that in the
    # instructions did not stop it, because this file was showing it "[[id]] Title" on sixty
    # nine lines and the pack's own rule is that the model writes what it reads. So the shape
    # it is shown is now the shape that reads correctly, which is the name and then its
    # citation. Instructions lose to examples and the examples are here.
    return f"{it['title'].rstrip('.')}. " + ", ".join(bits) + f". [[{it['id']}]]"


def index(items: list, today: str, extra=()) -> str:
    """The whole index, which is the block the model always gets whatever else it does not.

    THIS IS THE SAFETY PROPERTY OF RETRIEVING AT ALL. A retrieval chatbot's worst failure is
    not missing a passage, it is answering as though the missing thing does not exist, and a
    reader has no way to see that happen. Handing over the complete list of what EXISTS costs
    a fraction of the bodies and deletes that failure rather than mitigating it. It also lets
    retrieval be generous, because being wrong about which bodies to send is now recoverable.
    """
    parts = [INDEX_HEAD, "\n".join(index_line(it, today) for it in items)]
    parts.extend(x for x in (extra or ()) if x)
    return "\n\n".join(parts)


def item_prose(it: dict, today: str) -> str:
    """One decision, as the model should read it.

    No colons and no semicolons, because the house bans both in published copy and the model
    writes what it reads. No first person for the same reason.
    """
    geo = it.get("geography") or {}
    pa = it.get("public_access") or {}
    dec = it.get("decider") or {}
    state = dk.window_state(it, today)

    head = f"[[{it['id']}]] {it['title']}"

    facts = [
        f"The topic is {TOPIC_WORDS.get(it['topic'], it['topic'].replace('-', ' '))}",
        f"The decider is {dec.get('name', 'not recorded')}, "
        f"a {str(dec.get('type', 'body')).replace('-', ' ')}",
        f"Its status is {it.get('status', 'unknown')}",
    ]

    dates = []
    for kd in it.get("key_dates") or []:
        kind = KIND_WORDS.get(kd.get("kind"), str(kd.get("kind", "")).replace("_", " "))
        note = (kd.get("note") or "").strip().rstrip(".")
        line = f"{longdate(kd.get('date'))}, {kind}"
        if note:
            line += f", {note}"
        dates.append(line)

    access = []
    room = ROOM_WORDS.get(pa.get("room"), pa.get("room"))
    if room:
        access.append(f"Public access is {room}")
    if state == "open":
        closes = pa.get("closes")
        access.append(f"The window is open now and closes {longdate(closes)}" if closes
                      else "The window is open now")
    elif state == "closed":
        access.append("The window has closed")
    if pa.get("how"):
        access.append(deurl(pa["how"]).rstrip("."))

    claims = []
    for c in it.get("claims") or []:
        # Only the assertion and the words the source actually used. The url, the source
        # title, the source type and the fetch date are the checker's business and the
        # page's, never the prompt's.
        text = (c.get("text") or "").strip().rstrip(".")
        quote = (c.get("verbatim_quote") or "").strip()
        if not text:
            continue
        claims.append(f"{text}, quoted as \"{quote}\"" if quote else text)

    body = [
        _sentences(facts),
        deurl(it.get("summary") or ""),
        where(geo),
        _sentences(dates) if dates else "",
        _sentences(access) if access else "",
        _sentences(claims) if claims else "",
        f"Last verified {longdate(it.get('last_verified'))}, "
        f"confidence {it.get('confidence', 'not recorded')}",
    ]
    return head + "\n" + "\n".join(b for b in body if b)


def _feed(name: str, docs_dir=None):
    path = (Path(docs_dir) if docs_dir else DOCS) / f"{name}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def instruments(docs_dir=None) -> str:
    """The two daily instruments, at their CURRENT reading only.

    Never the series. A reading a day for a year is thousands of numerals that no question
    needs and that would authorise almost any figure a model cared to invent. Direction of
    travel comes from the previous reading and nothing further back.

    Neither of these ever carries a verdict. The grid watch publishes measured load, modeled
    load and the derived residual, and never a reliability call, because a unit trip can
    produce an emergency on a day the numbers looked comfortable. That rule is in CLAUDE.md,
    it does not bend, and it is enforced again in the worker's checker.
    """
    out = []

    grid = _feed("gridwatch", docs_dir)
    if grid and grid.get("readings"):
        r = grid["readings"][-1]
        prev = grid["readings"][-2] if len(grid["readings"]) > 1 else None
        lines = [
            f"ERCOT grid watch, measured for {longdate(r.get('date'))}, [[grid]]",
            f"Peak load reached {r.get('peak_load_mw')} MW in hour ending "
            f"{r.get('peak_hour_ending')}",
            f"Mean load across the day was {r.get('mean_load_mw')} MW and the minimum was "
            f"{r.get('min_load_mw')} MW in hour ending {r.get('min_hour_ending')}",
            f"The load factor was {r.get('load_factor')}",
            f"Capacity at the peak was {r.get('capacity_at_peak_mw')} MW, leaving a reserve "
            f"of {r.get('reserve_at_peak_mw')} MW",
            f"The day ahead forecast peak was {r.get('forecast_peak_mw')} MW, off by "
            f"{r.get('peak_forecast_error_mw')} MW at the peak, with a mean absolute error "
            f"of {r.get('mean_absolute_forecast_error_mw')} MW across the day",
            f"Energy served was {r.get('energy_mwh')} MWh across {r.get('hours_measured')} "
            f"measured hours",
        ]
        fuels = r.get("fuel_energy_mwh") or {}
        if fuels:
            lines.append("Energy by fuel, in MWh, was " + ", ".join(
                f"{k} {v}" for k, v in sorted(fuels.items())))
        if not r.get("verified", True):
            lines.append("This reading is UNVERIFIED and no number was carried forward from "
                         "the day before")
        if prev:
            lines.append(f"For direction of travel only, the previous reading was "
                         f"{longdate(prev.get('date'))} with a peak of "
                         f"{prev.get('peak_load_mw')} MW")
        out.append(_sentences(lines))

    water = _feed("waterwatch", docs_dir)
    if water and water.get("readings"):
        r = water["readings"][-1]
        prev = water["readings"][-2] if len(water["readings"]) > 1 else None
        lines = [
            f"Texas reservoir storage, measured for {longdate(r.get('date'))}, [[water]]",
            f"Statewide storage was {r.get('storage_af')} acre feet against a conservation "
            f"capacity of {r.get('capacity_af')} acre feet, which is "
            f"{r.get('percent_full')} percent full",
            f"That covers {r.get('reservoir_count')} reservoirs",
        ]
        for label, key in (("no conservation pool", "excluded_no_conservation_pool"),
                           ("outside the state", "excluded_out_of_state")):
            names = r.get(key) or []
            if names:
                lines.append(f"Excluded as {label}, {', '.join(names)}")
        if not r.get("verified", True):
            lines.append("This reading is UNVERIFIED and no number was carried forward")
        if prev:
            lines.append(f"For direction of travel only, the previous reading was "
                         f"{longdate(prev.get('date'))} at {prev.get('percent_full')} "
                         f"percent full")
        out.append(_sentences(lines))

    return "\n\n".join(out)


# ---------------------------------------------------------------------------
# THE RECORD STOPS MEANING ONLY DECISIONS.
#
# Everything above this line answers off docket.json. Everything the site publishes BESIDE the
# docket was invisible to the ask box, which is most of what it publishes: 54 facility
# dossiers, a construction register of 650 projects, 119 reservoirs grouped into metros, and a
# settled grid day with its fuel mix. A reader asking how full Lake Travis is, or who is
# building in Abilene, was told the record does not carry it. The record carries all of it.
#
# WHY THESE BECOME BLOCKS RATHER THAN MORE PREAMBLE. The preamble is sent on every question
# whatever was asked. A block is sent only when it is retrieved. Anything numerous and
# individually askable therefore has to be a block or it is a tax on every other question, and
# anything a question needs regardless of its subject has to be preamble or it is missing when
# it matters. That is the whole rule and it decides every placement below.
#
# WHY THE NUMBERS ARRIVE AS SENTENCES AND NOT AS ROWS. Retrieval over text answers numeric
# questions badly, measured at 41 percent against an oracle ceiling near 75. The failure is
# structural rather than a tuning problem, because the answer to "how much construction is in
# Dallas County" is a SUM and no retrieved row contains a sum. So the arithmetic is done here,
# in Python, from the same files the pages are built from, exactly as `tally` has always done
# it for the decisions. The model is handed a result rather than a table to add up.
#
# It is also what keeps the numeral law intact. Every figure below was computed from data, so
# the answer time check authorises it for free, and no figure a reader ever sees was typed.

# THE METRO DISPLAY NAMES ARE THE WATER PAGE'S, IMPORTED AND NOT COPIED. Two spellings of
# "Beaumont and Port Arthur" on one site is the kind of drift nobody notices until a
# reader asks about the one this file invented.
from waterwatch_page import METRO_NAMES, reservoir_label

FACILITIES = Path(REPO) / "ledger" / "facilities" / "dossiers.json"
PROJECTS = Path(REPO) / "ledger" / "facilities" / "projects.json"

# The units the dossiers actually use, read off the data rather than guessed at. An unmapped
# unit falls through as itself, which is the safe direction, and the self-test fails if the
# ledger starts using one nothing here has a word for.
UNIT_WORDS = {
    "MW": ("megawatt", "megawatts"),
    "GW": ("gigawatt", "gigawatts"),
    "MVA": ("megavolt ampere", "megavolt amperes"),
    "kV": ("kilovolt", "kilovolts"),
    "sqft": ("square foot", "square feet"),
    "acres": ("acre", "acres"),
    "miles": ("mile", "miles"),
    "feet": ("foot", "feet"),
    "buildings": ("building", "buildings"),
    "warehouses": ("warehouse", "warehouses"),
    "offices": ("office", "offices"),
    "stories": ("story", "stories"),
    "data_halls": ("data hall", "data halls"),
    "workers": ("worker", "workers"),
    "units": ("unit", "units"),
    "facilities": ("facility", "facilities"),
    "roles": ("role", "roles"),
    "options": ("option", "options"),
    "reactors": ("reactor", "reactors"),
    "entities": ("entity", "entities"),
    "tenants": ("tenant", "tenants"),
    "utility_feeds": ("utility feed", "utility feeds"),
    "building_order": ("building", "buildings"),
    "facility_order": ("facility", "facilities"),
    "percent": ("percent", "percent"),
    "jobs": ("job", "jobs"),
    "years": ("year", "years"),
    "months": ("month", "months"),
    "gallons": ("gallon", "gallons"),
    "gallons_per_day": ("gallon per day", "gallons per day"),
    "gpm": ("gallon per minute", "gallons per minute"),
    "exahashes_per_second": ("exahash per second", "exahashes per second"),
    "usd": ("dollar", "dollars"),
    "usd_per_kwh": ("dollar per kilowatt hour", "dollars per kilowatt hour"),
}


def _ledger(path: Path):
    """A ledger this pack can live without.

    The dossiers and the register are written by a different lane on a different cadence. A run
    that finds one missing should build a smaller pack, not fail. Every caller below treats an
    empty return as "that family has nothing today" and emits no block and no index line, so
    the model is never told something exists that it was not shown.
    """
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return None


def money(n) -> str:
    """A sum of money, in the shape an answer should say it.

    ONE FORM ONLY, AND THIS IS NOT A STYLE CHOICE. The answer time check authorises the exact
    numerals the model was shown. Writing $43,415,000,000 here and letting the model round it
    to 43.42 billion would get that sentence refused, and the reader would see a stop where the
    record had the figure. Writing it the way it should be read authorises the reading.
    """
    try:
        return fd.money(n)
    except (TypeError, ValueError):
        return ""


def _shown_number(value, unit: str) -> str:
    if unit in {"gallons", "gallons_per_day"}:
        return fd.scaled(value)
    return f"{value:,.0f}" if isinstance(value, (int, float)) and float(value).is_integer() \
        else f"{value:,}"


def _quantity(value, unit: str, *, attributive=False) -> str:
    """One quantity in the plain words the answer engine should copy."""
    if unit == "usd":
        return fd.money(value)
    if unit in {"building_order", "facility_order"}:
        return fd.one_quantity(value, unit)
    shown = _shown_number(value, unit)
    if unit == "usd_per_kwh":
        return f"${shown} per kilowatt hour"
    singular, plural = UNIT_WORDS[unit]
    word = singular if attributive or float(value) == 1 else plural
    return f"{shown} {word}"


def _fact(f: dict) -> str:
    """One dossier fact, as a sentence assembled from its structured quantity fields."""
    label = (f.get("label") or "").strip().rstrip(".")
    if not label:
        return ""
    if f.get("text"):
        return f"{label} is {str(f['text']).strip().rstrip('.')}"
    shape = fd.numeric_shape(f)
    if not shape or shape == "mixed":
        return ""
    unit = f.get("unit") or ""
    if shape == "value":
        core = _quantity(f["value"], unit, attributive=bool(f.get("attributive")))
    elif shape == "range":
        singular, plural = UNIT_WORDS[unit]
        core = (f"{_shown_number(f['minimum'], unit)} to "
                f"{_shown_number(f['maximum'], unit)} {plural}")
    elif shape == "alternatives":
        shown = [_quantity(value, unit) for value in f["alternatives"]]
        core = shown[0] if len(shown) == 1 else ", ".join(shown[:-1]) + ", or " + shown[-1]
    else:
        shown = [_quantity(q["value"], q["unit"], attributive=bool(q.get("attributive")))
                 for q in f["quantities"]]
        core = shown[0] if len(shown) == 1 else ", ".join(shown[:-1]) + " and " + shown[-1]

    bits = [str(f.get("prefix") or "").strip(), fd.QUALIFIERS.get(f.get("qualifier"), ""),
            core, str(f.get("suffix") or "").strip()]
    shown = " ".join(x for x in bits if x)
    if f.get("date"):
        shown += f" {f.get('date_intro', 'in')} {fd.date_context(f['date'])}"
    return f"{label} is {shown}".strip()


def facility_prose(d: dict) -> str:
    """One data centre, as the model should read it.

    THE SUMMARY GOES ON THE SECOND LINE ON PURPOSE. The worker's splitter reads a block's first
    two lines as its head and searches that separately from the body, so what a facility IS
    ranks against a reader who half remembers a company or a town, while the facts underneath
    still answer the reader who remembers a megawatt figure. That is two views of one block for
    the price of putting the sentences in the right order.
    """
    name = (d.get("name") or "").strip()
    lines = [f"[[facility-{d['slug']}]] {name}, a data center on the Texas register",
             deurl((d.get("summary") or "").strip())]
    facts = [s for s in (_fact(f) for f in (d.get("facts") or [])) if s]
    if facts:
        lines.append(_sentences(facts))
    notes = [deurl(str(n.get("text") or "").strip()) for n in (d.get("notes") or [])]
    notes = [n for n in notes if n]
    if notes:
        lines.append(" ".join(notes))
    gaps = [str(g).strip().rstrip(".") for g in (d.get("gaps") or []) if str(g).strip()]
    if gaps:
        lines.append("What the record does not carry for this one. " + _sentences(gaps))
    return "\n".join(x for x in lines if x)


def _facility_county(d: dict) -> str | None:
    """The county named in the dossier's Location fact, or None if the filing does not name one.

    A hundred and twenty five of one hundred and fifty dossiers publish no location, because the
    state's filing does not require one and the record publishes only what was filed. This reads
    what is there and does not guess.
    """
    import re as _re
    for f in (d.get("facts") or []):
        if (f.get("label") or "").strip() == "Location":
            text = (f.get("text") or "").strip()
            m = _re.search(r",\s*([A-Za-z][A-Za-z .'-]*?County)\b", text)
            return m.group(1) if m else None
    return None


def facility_index_entry(d: dict) -> str:
    """One dossier in the rolled up index, as a name and the id to cite it by.

    THE DOSSIERS ARE ROLLED UP, THE WAY THE CONSTRUCTION REGISTER AND THE RESERVOIRS ALREADY
    ARE, 2026-09-03. They were the last family still indexed a full line each, at eighty two
    characters against sixteen for a rolled county, and one hundred fifty of them carried the
    index four hundred and fifty characters past its ceiling once this run's five admissions
    landed. `MAX_INDEX_CHARS` says in as many words that a family arriving later should roll up
    before that number is touched, and this is that family.

    WHY THE ID STAYS THOUGH THE RESERVOIR AND COUNTY HEADS DROP THEIRS. A reservoir's body sits
    in the core pack, which every question carries, so its id rides along whether or not the
    reservoir is retrieved. A dossier body sits in `facility_pack`, which the retrieval-off
    escape hatch does NOT send, so a dossier is citable only from the index whenever its body is
    not retrieved. The index's own contract, stated in `INDEX_HEAD`, is that a line with no text
    below is still real and the line is all there is to go on, and a citation needs the id.
    """
    return f"{(d.get('name') or '').strip().rstrip('.')} [[facility-{d['slug']}]]"


# Kept as an alias because callers outside this module import the older name. The dossier index
# is now built by county in the wrapping block rather than one line per dossier, so this returns
# the entry rather than a line.
facility_index_line = facility_index_entry


def facility_index_block(dossiers: list) -> str:
    """The dossiers as a rolled up index block, GROUPED BY COUNTY where the county is on file.

    A county grouping IS the location evidence, and this shape exists because dropping the
    location detail from the flat list broke a real class of question. The measured case, from a
    review of the first attempt at this roll-up: "What data centers are in Taylor County?" is
    answered by eight Lancium Abilene dossiers, all of them carrying `Location: Abilene, Taylor
    County`. The flat "name and id" list said Abilene but never the county, so retrieval matched
    six unrelated bodies on other words and the assembled prompt named Taylor County zero times.

    A dossier whose filing publishes no county goes into an unlocated group, printed at the end.
    A hundred and twenty five of one hundred and fifty dossiers sit there today, because the
    state's certification does not require a location and the record publishes what was filed.
    Grouping only what is named is what makes this honest rather than inventing a county.

    Cost: about two hundred forty characters over the flat "name and id" list, well under the
    ceiling and worth it. This is the shape the review recommended, in as many words: "keep a
    compact location-bearing roll-up, such as grouping dossier names and IDs by county."
    """
    from collections import defaultdict
    by_county: dict[str | None, list] = defaultdict(list)
    for d in dossiers:
        by_county[_facility_county(d)].append(d)
    parts: list[str] = []
    for county in sorted(c for c in by_county if c):
        entries = ", ".join(facility_index_entry(d) for d in by_county[county])
        parts.append(f"In {county}, {entries}.")
    if by_county.get(None):
        entries = ", ".join(facility_index_entry(d) for d in by_county[None])
        parts.append(f"With no county on file, {entries}.")
    return " ".join(parts)


def familyOf(block_id: str) -> str:
    """Which family a block belongs to, read off its id and nothing else.

    THE SAME RULE THE WORKER USES, and the worker's copy is the one that decides retrieval, in
    `workers/ask/retrieve.js`. This one exists so the self-test can check that the families the
    builder emitted are the families the cut produces. Two implementations that agree today is
    the failure this repo keeps relearning under new names, so they are asserted against each
    other in `workers/ask/test.js` rather than trusted.
    """
    import re as _re
    if _re.fullmatch(r"tx-\d{4}-\d{4}", block_id):
        return "tx"
    return block_id.split("-", 1)[0] if "-" in block_id else block_id


def _slug(name: str) -> str:
    return __import__("re").sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-")


def construction(rows: list):
    """The construction register, rolled up by county.

    SIX HUNDRED AND FIFTY ROWS DO NOT BECOME SIX HUNDRED AND FIFTY BLOCKS. That is 162,000
    characters, more than this entire pack, and it would still answer "how much is being built
    in Dallas County" wrongly, because that answer is a sum and no row carries a sum. Rolled up
    by county it is sixty one blocks, the sums are already taken, and the rows that made them
    are still on the published page for anybody who wants to check the arithmetic.

    NO PROJECT IS NAMED AS A PLAN. A registration is a filing, not a promise, and the register
    records what was filed. Every line below is a count, a sum or a date the state published.
    """
    from collections import Counter, defaultdict
    by_county = defaultdict(list)
    for r in rows:
        c = (r.get("county") or "").strip()
        if c:
            by_county[c].append(r)

    blocks, lines = [], []
    for county in sorted(by_county):
        rs = by_county[county]
        costs = [r["cost"] for r in rs if isinstance(r.get("cost"), (int, float)) and r["cost"]]
        total = sum(costs)
        cities = [c for c, _ in Counter(
            (r.get("city") or "").strip() for r in rs if (r.get("city") or "").strip()
        ).most_common(4)]
        biggest = sorted((r for r in rs if isinstance(r.get("cost"), (int, float))),
                         key=lambda r: -r["cost"])[:3]
        statuses = Counter((r.get("status") or "unknown").strip() for r in rs)
        years = sorted({(r.get("start") or "")[:4] for r in rs
                        if (r.get("start") or "")[:4].isdigit()
                        and (r.get("start") or "")[:4] != "1900"})

        body = [f"{len(rs)} registered construction projects sit in {county} County",
                f"Their declared cost adds to {money(total)}" if total else
                "None of them declares a cost"]
        if cities:
            body.append("The cities named are " + ", ".join(cities))
        if years:
            body.append(f"The filings run from {years[0]} to {years[-1]}"
                        if len(years) > 1 else f"Every filing starts in {years[0]}")
        body.append("By status, " + ", ".join(
            f"{k} {v}" for k, v in sorted(statuses.items(), key=lambda x: (-x[1], x[0]))))
        named = [f"{(r.get('facility') or r.get('project') or '').strip()} at "
                 f"{money(r['cost'])}" for r in biggest if r.get("cost")]
        if named:
            body.append("The largest by declared cost are " + ", ".join(named))
        blocks.append(f"[[county-{_slug(county)}]] Construction registered in {county} County\n"
                      + _sentences(body))
        lines.append(f"{county} {len(rs)}")

    total = sum(r["cost"] for r in rows
                if isinstance(r.get("cost"), (int, float)) and r["cost"])
    head = (f"THE CONSTRUCTION REGISTER. {len(rows)} projects the state has registered, "
            f"declaring {money(total)} across {len(by_county)} counties. "
            f"A registration is a filing and not a promise, so a project here is something "
            f"somebody told the state they would build. "
            f"Each county has a block of its own below, cited as its own id. "
            f"By county, " + ", ".join(lines) + ".")
    return blocks, head


def reservoirs(feed: dict):
    """Reservoir storage, by metro and by named reservoir.

    A READER'S WATER QUESTION IS ABOUT THEIR OWN TAP. Statewide percent full is the right
    headline and the wrong answer to "how is Austin doing" or "how full is Lake Travis", and the
    feed already carries both levels because the water page publishes them. Nothing here is a
    new measurement. It is the same reading, read at the level somebody actually asks about.

    WHICH RESERVOIRS FEED WHICH METRO IS NOT IN THE PUBLISHED FEED. The collector rolls the
    municipal tags into counts and the names do not survive that. Reconstructing the mapping
    here would be a THIRD derivation of something the collector already decided, which is the
    failure this repo keeps relearning under new names, so it is not reconstructed. A metro
    block says how many reservoirs it draws on and a reservoir block stands on its own.

    PERCENT FULL IS STORAGE OVER CAPACITY, COMPUTED HERE, never the publisher's own field. That
    has been the water page's rule since it was written and an answer may not be built on a
    different one, or two surfaces of this site would publish different numbers for one lake.

    NO VERDICT, in either direction. Storage is a measurement. Whether it is enough is a call
    this record does not make, and the answer time checker refuses the sentence if it tries.
    """
    readings = (feed or {}).get("readings") or []
    if not readings:
        return [], ""
    r = readings[-1]
    metros = r.get("metros") or {}
    pools = r.get("reservoirs") or {}
    if not metros and not pools:
        return [], ""
    day = longdate(r.get("date"))

    blocks, metro_lines = [], []
    for key in sorted(metros):
        m = metros[key] or {}
        name = METRO_NAMES.get(key, key.replace("_", " ").title())
        pct = m.get("percent_full")
        body = [f"{name} draws on {m.get('reservoirs')} reservoirs",
                f"Their combined storage is {m.get('storage_af'):,.0f} acre feet against a "
                f"conservation capacity of {m.get('capacity_af'):,.0f} acre feet, which is "
                f"{pct} percent full" if m.get("storage_af") is not None else "",
                "Which reservoirs those are is not in the published feed, so this block does "
                "not name them",
                f"Measured for {day}"]
        blocks.append(f"[[water-{_slug(key)}]] Reservoir storage for the {name} metro\n"
                      + _sentences([x for x in body if x]))
        if pct is not None:
            metro_lines.append(f"{name} {pct} percent")

    # THE NAME A READER SAW IS THE NAME THIS HAS TO USE. TWDB's keys are names with the spaces
    # taken out, so the feed says "AlanHenry" and "SamRayburn", and 48 of the 119 are like that.
    # The water page has always spaced them back out for display, so the page teaches a reader
    # "Alan Henry" and the pack was offering the model "AlanHenry". Nothing tokenises those the
    # same, so those 48 reservoirs were unfindable by anybody who had read the page they came
    # from. The gold set caught it the day it started scoring reservoirs, which is what it is
    # for. The splitter is the page's own, imported and not copied.
    pool_lines = []
    for key in sorted(pools):
        p = pools[key] or {}
        cap, sto = p.get("capacity_af"), p.get("storage_af")
        if not cap or sto is None:
            continue
        name = reservoir_label(key)
        pct = round(100.0 * sto / cap, 1)
        blocks.append(
            f"[[water-lake-{_slug(key)}]] {name} reservoir\n"
            + _sentences([
                f"{name} holds {sto:,.0f} acre feet against a conservation capacity of "
                f"{cap:,.0f} acre feet, which is {pct} percent full",
                f"Measured for {day}"]))
        pool_lines.append((name, pct))

    head = [f"RESERVOIR STORAGE, measured for {day} and read off the same statewide reading "
            f"above. Percent full is storage over conservation capacity. Every metro and every "
            f"reservoir has a block of its own below, cited as its own id."]
    if metro_lines:
        head.append("By metro, " + ", ".join(metro_lines) + ".")
    # ROLLED UP RATHER THAN INDEXED LINE BY LINE, which is what the ceiling note at the top of
    # this file says to do before the ceiling itself is touched. Naming all 119 reservoirs WITH
    # a percentage each cost 2,947 characters of an index every question pays for, and the same
    # figures sit in each reservoir's own retrievable block and roll up into the metro line
    # directly above. The NAMES stay, in full, because a name is what makes a block findable and
    # dropping those would leave 119 ids nothing points at.
    #
    # The extremes stay too, with their figures. They are the one comparison the enumeration
    # actually bought, they cannot be recovered from the metro roll-up, and answering "which is
    # lowest" should not cost 119 retrievals.
    if pool_lines:
        head.append("Reservoir by reservoir, " + ", ".join(n for n, _ in pool_lines) + ".")
        ranked = sorted(pool_lines, key=lambda x: x[1])
        head.append("Lowest, " + ", ".join(f"{n} {v} percent" for n, v in ranked[:3])
                    + ". Fullest, "
                    + ", ".join(f"{n} {v} percent" for n, v in reversed(ranked[-3:])) + ".")
    return blocks, " ".join(head)


# HOW MANY SETTLED DAYS MAY BE NAMED, and this number is the whole of the argument.
#
# "Never the series" is the older rule and it is right about what it was written against, which
# was a reading a day for a year and twenty four figures inside each one. That is thousands of
# numerals no question needs, and every one of them is authorised for a model to write the
# moment it is shown.
#
# What it was NOT written against is "what has the peak done this week", which is a fair
# question, which the site's own grid page answers, and which cannot be answered from one day.
# So the rule keeps its teeth and gets a number. A fortnight of daily peaks is 14 numerals with
# a date attached to each, the hourly arrays stay out entirely, and the ceiling is asserted in
# the self-test so a feed that starts keeping a year cannot quietly widen this.
GRID_DAYS = 14


def grid_series(feed: dict) -> str:
    """The recent settled days, at their peaks only.

    NOT THE HOURLY SERIES, and not the whole feed either. See GRID_DAYS above for why there is
    a number here rather than a prohibition. The peak is what a week question is asking about,
    and the day it fell on is what makes the answer checkable against the page.
    """
    rs = ((feed or {}).get("readings") or [])[-GRID_DAYS:]
    if len(rs) < 2:
        return ""
    days = ", ".join(f"{longdate(x.get('date'))} at {x.get('peak_load_mw')} MW"
                     for x in rs if x.get("peak_load_mw") is not None)
    if not days:
        return ""
    peaks = [x for x in rs if x.get("peak_load_mw") is not None]
    top = max(peaks, key=lambda x: x["peak_load_mw"])
    return _sentences([
        f"The grid watch holds {len(rs)} settled days, which are {days}, [[grid]]",
        f"The highest peak among them was {top['peak_load_mw']} MW on "
        f"{longdate(top.get('date'))}",
        "These are measured days and none of them is a forecast of another one",
    ])


def weather(feed: dict) -> str:
    """Heat and rain against the long run normal, at the one anchor station.

    ONE STATION AND IT SAYS SO. This is not a statewide climate figure and a reader should
    never be able to read it as one.
    """
    n = (feed or {}).get("normals") or {}
    rs = (feed or {}).get("readings") or []
    if not n or not rs:
        return ""
    last = rs[-1]
    bits = [f"Weather at the anchor station, {n.get('station_name')}, station "
            f"{n.get('station')}, which is one station and not a statewide figure"]
    if last.get("date"):
        got = [f"a high of {last['tmax_f']} F" if last.get("tmax_f") is not None else "",
               f"a low of {last['tmin_f']} F" if last.get("tmin_f") is not None else "",
               f"{last['prcp_in']} inches of rain" if last.get("prcp_in") is not None else ""]
        got = [g for g in got if g]
        if got:
            bits.append(f"The most recent day it holds is {longdate(last['date'])} with "
                        + ", ".join(got[:-1]) + " and " + got[-1] if len(got) > 1
                        else f"The most recent day it holds is {longdate(last['date'])} with "
                             + got[0])
    bits.append(f"It holds {len(rs)} days in all, [[weather]]")
    base = n.get("base_period") or []
    if len(base) == 2:
        bits.append(f"Normals are the {base[0]} to {base[1]} base period")
    return _sentences(bits)


SYSTEM = """You answer questions about the Texas AI Docket, a public record of artificial
intelligence in Texas, from the record given to you below and from nothing else.

WHAT THE RECORD HOLDS. Four things, and a question may want any of them or several at once.
The DECISIONS, which are what a public body decided and when. The DATA CENTERS on the state
register, one dossier each. The CONSTRUCTION the state has registered, totalled by county. And
RESERVOIR STORAGE, by metro and by reservoir. The daily grid and water readings sit above the
index. Somebody asking what is happening in their county is asking about all of it.

WHAT YOU MAY SAY. Only what the record states. Every figure you write must appear in the
record exactly as you write it. Everything you name must be something the record carries. If
the record does not answer the question, say so plainly and say what it does carry instead.
A short true answer beats a long one that reaches.

CITING. Write the id in double square brackets, like [[tx-2026-0001]] for a decision,
[[facility-bexar-1]] for a data center, [[county-dallas]] for a county's construction, and
[[water-lake-travis]] for a reservoir. Never write a bare url.

THE PAGE TURNS THAT INTO A SHORT LINK, either the thing's identifier, like "Docket 59315", or
the source it came from, like "the water record". It is never long.

PUT THE CITATION AFTER WHAT YOU SAY, NOT WHERE THE SUBJECT GOES. Write "No groundwater district
decided that, [[tx-2026-0060]]" and not "The record for [[tx-2026-0060]] doesn't mention it".
Write "Comments close September 4th, 2026, [[tx-2026-0002]]." Write "Two decisions cover it,
[[tx-2026-0003]] and [[tx-2026-0076]]." Say the thing, then cite it.

WHAT YOU MAY NEVER SAY. No verdict on grid reliability. Not a shortfall prediction, not an
all clear, not a blackout call, not a judgement about whether the grid can carry a load. A
unit trip can produce an emergency on a day the numbers looked comfortable, and per site
large load metering is confidential, so that call is not the record's to make. State the
measured figures and stop. The same applies to reservoir storage and to any forecast of what
a decider will decide.

PUNCTUATION. No colons. No semicolons. Write two sentences instead. No em dashes and no en
dashes, and a range reads "X to Y". No emojis. Straight quotes only.

WORDS. Write "can't" and never "cannot". Never open a sentence with "And" or "But". No first
person, so no "I", no "we", no "let me". Dates take the month first with the ordinal, like
"August 11th, 2026", never "11 August" and never a bare "August 11".

THE FIRST PERSON CREEPS BACK IN WHEN YOU DECLINE SOMETHING, and a sentence carrying it is cut
before a reader sees it, so the decline arrives half finished. "I can't help with that" and
"we only track Texas AI decisions" are both stopped. Turning down a question off this record
reads "That is outside what this record covers. It tracks decisions about artificial
intelligence in Texas." Name the record, not yourself.

COMMAS. Keep them sparse. No comma after a coordinating conjunction or a relative pronoun,
and no hedge fenced off by a pair of commas. Write "A data center needs electricity. Most
cooling designs need water too", never "A data center needs electricity and, in most cooling
designs, water". When a sentence needs a comma to hold together, split it into two sentences
instead.

HOW TO SOUND. Like a person who knows the record, talking to someone who asked a fair
question. Not like an assistant. Skip the throat clearing, so no "Great question", no
"Certainly", no "I'd be happy to". Answer first.

WHEN ONE DETAIL IS MISSING, ASK FOR IT AND STOP. Somebody asking whether their county is
affected has not told you the county. The answer to that is "Which county are you in?" and
nothing else. Do not explain why it can't be answered yet, do not list every county on the
record, and do not restate the question back. One short question, then stop.

WRITE TO THE READER, NOT ABOUT THE RECORD. Say "you" and address them directly. The rule
against first person rules out "I" and "we", and it does NOT mean falling back on the passive
voice, which is what makes an answer read like a machine. "Tell the county and the record can
be checked against it" is the passive doing the work of a pronoun. "Which county are you in?"
is the same question asked by somebody who is actually listening.

Close by offering the one obvious next question, phrased as an offer, like "Want the dates it
moved on?" That offer is loaded into the reader's own field for them, so make it a real
question this record can answer.
"""


def families(docs_dir=None):
    """The three families that are not the decisions, built once.

    THE BLOCKS AND THE INDEX LINES ARE BUILT TOGETHER, ONE CALL EACH, because they have to
    agree. A family with an index line and no blocks tells the model something exists that it
    can never be shown, and a family with blocks and no line is invisible until retrieval
    happens to guess right. Each builder returns both or neither.

    IT IS A FUNCTION SO THAT TWO CALLERS CANNOT DISAGREE. `build` needs the blocks to write the
    pack and `cite_map` needs them to name the links, and the second one used to reach into the
    first one's published output for a copy. Ids drifting between the prompt and the page is a
    citation to a page that does not exist, which is the whole failure the map exists to stop.
    """
    dossiers = (_ledger(FACILITIES) or {}).get("dossiers") or []
    projects = (_ledger(PROJECTS) or {}).get("projects") or []
    county_blocks, county_head = construction(projects)
    water_blocks, water_head = reservoirs(_feed("waterwatch", docs_dir) or {})
    return dossiers, county_blocks, county_head, water_blocks, water_head


def cite_map(today: str = None, places=frozenset(), docs_dir=None) -> dict:
    """Every citable id, with the name and the link the page should render it as.

    Called by site_build, which is the only thing that reads it and the only thing that knows
    which counties have a page of their own. See `cites` for why `places` is passed in.
    """
    today = today or _dt.date.today().isoformat()
    dossiers, county_blocks, _ch, water_blocks, _wh = families(docs_dir)
    return cites(dk.load(LEDGER), dossiers, county_blocks, water_blocks, places=places)


def build(today: str = None, docs_dir=None) -> dict:
    today = today or _dt.date.today().isoformat()
    items = dk.load(LEDGER)

    dossiers, county_blocks, county_head, water_blocks, water_head = families(docs_dir)

    parts = [
        f"THE TEXAS AI DOCKET, as it stood on {longdate(today)}. "
        f"It tracks {len(items)} decisions. It also carries the daily instruments, "
        f"{len(dossiers)} data center dossiers, the state construction register and "
        f"reservoir storage, all of which are below and all of which can be asked about.",
    ]
    parts.append(tally(items, today))
    inst = instruments(docs_dir)
    if inst:
        parts.append("THE DAILY INSTRUMENTS.\n\n" + inst)

    # THE SERIES AND THE WEATHER ARE PREAMBLE, NOT BLOCKS, and the rule that decides it is the
    # one at the top of the section above. Twelve peaks and one station's last reading are
    # small, and the question they answer, what has this week looked like, arrives without
    # naming anything a retriever could match on. A block nobody retrieves is a block nobody
    # reads.
    series = grid_series(_feed("gridwatch", docs_dir) or {})
    if series:
        parts.append("THE SETTLED GRID DAYS.\n\n" + series)
    wx = weather(_feed("weather", docs_dir) or {})
    if wx:
        parts.append("THE WEATHER RECORD.\n\n" + wx)

    parts.append("THE DECISIONS.")
    parts.extend(item_prose(it, today) for it in items)
    parts.extend(county_blocks)
    parts.extend(water_blocks)

    pack = "\n\n".join(parts)
    facility_pack = ("\n\n".join(
        [FACILITY_PACK_MARK, DECISIONS_MARK]
        + [facility_prose(d) for d in dossiers]
    ) if dossiers else "")
    idx = index(items, today, extra=[
        ("THE DATA CENTER DOSSIERS. Every dossier the record holds, rolled up rather than listed, "
         "grouped by the county its filing names, each as its name and the id to cite it by, and "
         "the full dossier for the ones this question needs is below. "
         + facility_index_block(dossiers)) if dossiers else "",
        county_head,
        water_head,
    ])
    return {
        "generated": today,
        "system": SYSTEM,
        # THE WHOLE RECORD, STILL PUBLISHED WHOLE, and it stays that way even though the worker
        # now sends a slice of it. This file is fetched by a worker that is deployed by hand,
        # by pasting, and the site rebuilds itself every day without asking anybody. Dropping a
        # field the live worker reads would take the ask box down the morning after a run, with
        # nothing in this repo to show for it. ASK_RETRIEVAL=off sends this bounded core plus
        # the complete index. Facility bodies stay available to normal retrieval below.
        "pack": pack,
        # THE COMPLETE FACILITY BODIES. Kept beside the core rather than inside it so the
        # retrieval-off escape hatch remains bounded. The worker indexes both fields and can
        # still send any full dossier body a normal question retrieves.
        "facility_pack": facility_pack,
        # THE INDEX, which is what makes sending a slice safe rather than merely cheaper. Every
        # decision gets a line whatever the retriever thinks, so the model always knows what
        # EXISTS and the retrieval failure that a reader cannot see, answering as though the
        # missing item is not there, is designed out instead of managed.
        "index": idx,
        "index_chars": len(idx),
        "chars": len(pack) + len(facility_pack),
        "items": len(items),
        # WHAT THE PACK ACTUALLY HOLDS, BY FAMILY. `items` counts decisions and used to count
        # everything, because for two years the two were the same number. They are not any
        # more, and a test asserting the split returned `items` blocks was the first thing to
        # notice. Both are published rather than one replacing the other, since the worker
        # deployed today still reads `items` and a field vanishing under a live worker is the
        # failure this file is most careful about.
        "blocks": len(items) + len(dossiers) + len(county_blocks) + len(water_blocks),
        # THE CITATION MAP IS NOT PUBLISHED HERE, and it was, for one commit. Only the page
        # reads it and only site_build knows which counties have a page of their own, so a copy
        # in this file could only ever be the version that did not know. Two maps that can
        # disagree is worse than one map in the place that has the facts. `cites` below is the
        # function, and site_build calls it with what it knows.
        "families": {
            "tx": len(items), "facility": len(dossiers),
            "county": len(county_blocks), "water": len(water_blocks),
        },
        # WHAT THE ANSWER CACHE ROTATES ON, and the date was not enough.
        #
        # The worker keys a cached answer on the pack's `generated` date, so an answer written
        # this morning is served all day. That is right when the pack only changes at the daily
        # rebuild. It changed four times in one afternoon while the prompt was being fixed, and
        # every one of those readers kept getting answers written against the version before,
        # including the citation stutter that had just been fixed twice.
        #
        # A digest of what the model is actually shown. Change the instructions, the index or a
        # decision, and the key moves with it.
        "version": __import__("hashlib").sha256(
            (SYSTEM + idx + pack + facility_pack).encode("utf-8")).hexdigest()[:16],
    }


# THE SPLIT CONTRACT, WRITTEN DOWN ON THE SIDE THAT PRODUCES THE PACK.
#
# The worker cuts `pack` back into a preamble and one block per decision, because shipping the
# bodies a second time in the same JSON would double a file the record already fills. That cut
# is only safe while the shape below holds, so the shape is asserted here rather than assumed
# there, and `workers/ask/test.js` runs the same assertions from the other side.
#
#   1  the preamble runs to the line "THE DECISIONS." and nothing above it starts with "[["
#   2  every decision block starts at the beginning of a line with "[[<id>]] "
#   3  blocks are separated by a blank line
#   4  ids are unique and there are exactly as many blocks as decisions
# WHAT A CITATION READS AS, which is not the same thing as what it points at.
#
# The link's TEXT was the thing's own title. That is right when a title is a name and wrong
# when it is a sentence, and 65 of 69 decision titles here are sentences. So the model wrote a
# paraphrase, the renderer appended the title, and a reader got the same fact twice in a breath:
#
#   "Houston ISD has carried an artificial intelligence board policy to a second reading,
#    still pending, Houston ISD carried an artificial intelligence board policy to a second
#    reading."
#
# All three citations in that answer did it. The cap on this text has now been wrong in both
# directions: at 44 characters nearly every citation was a fragment ending in an ellipsis, and
# at 170 it repeats the sentence it follows. Neither is a tuning problem. A title that is a
# sentence cannot be inlined after a paraphrase of itself at any length.
#
# A CITATION SHOULD READ AS ATTRIBUTION. Its identifier where the record gives one, because
# "PUCT Docket 59315" is what the thing is CALLED and a reader can look it up. Where there is
# none, the source it came from, which is what a citation is for. The link still goes exactly
# where it went, and the full title still rides along as the tooltip, so nothing a reader can
# reach is lost. What is lost is the sentence being said twice.
_IDENT = __import__("re").compile(
    r"\b((?:Docket|Project|Ordinance|Chapter|Contract|Case|Rule|Bill|Order|Resolution)"
    r"\s+[A-Z0-9][A-Za-z0-9.\-]*)")

# The source, per family, for the ones with no identifier of their own. Written the way a
# reader would name it out loud, because it lands mid sentence.
SOURCE = {
    "tx": "the docket",
    "county": "the construction register",
    "water": "the water record",
    "facility": "the data center register",
}

# A NAME SHORT ENOUGH TO BE A NAME. Four decision titles are shaped like one and every dossier
# is, "Bexar 1" and "Nexus Data Centers". Above this they are descriptions, and a description
# is the thing that stutters.
_NAME_MAX = 30


# WHOSE NAME MAY STAND AS ITS OWN CITATION, and for two families it never can.
#
# A reservoir block is titled "Sam Rayburn reservoir" and any sentence citing it has just said
# "Sam Rayburn", so the name is the subject repeated rather than a source. The same is true of
# a county's construction. A dossier is different: its name is what the state register calls
# it, it is the only handle the thing has, and it links to a page of its own.
_NAMES_ITSELF = {"tx", "facility"}


def cite_label(family: str, title: str, name: str = "") -> str:
    """The words a citation shows. See the note above for why it is not the title."""
    m = _IDENT.search(title or "")
    if m:
        return m.group(1)
    if family in _NAMES_ITSELF:
        short = (name or (title or "").split(",")[0]).strip()
        if short and len(short) <= _NAME_MAX:
            return short
    return SOURCE.get(family, "the record")


# WHERE A CITATION GOES, AND WHAT IT READS AS.
#
# The page renders [[id]] as a link under the thing's own name. It used to build that from the
# docket index and hardcode /item/<id>/, which was right while every citable thing was a
# decision. A dossier cited that way reached a reader as the literal string
# "facility-nexus-data-centers", linking to a page that does not exist.
#
# So the pack publishes the map, because the pack is where the names are. The alternative is
# the page deriving a name by unpicking a slug, which gets "b-a-steinhagen" wrong on the first
# try and gets it wrong silently.
#
# NOT EVERY FAMILY HAS A PAGE PER ITEM AND THE MAP SAYS SO RATHER THAN GUESSING. Fifty four
# dossiers have one each. Sixty one counties of construction have twenty four between them, so
# they point at the register, which is where their rows are published. Reservoirs have no page
# of their own at all and point at the water record.
#
# `places` IS PASSED IN AND IS NEVER READ OFF DISK, and the first version of this did read it
# off disk, by listing docs/place/. That is the previous build's output, so the answer depended
# on what was already on the filesystem: building into docs/ wipes it first and found zero
# county pages, building into a temp directory found twenty four, and the same commit produced
# two different sites. site_fresh_check caught it, which is what that gate is for, and it
# caught it after the merge rather than before.
#
# The authority is site_build.all_places, a pure function of the docket, which is what CREATES
# those pages. Asking the thing that makes them beats counting what it made last time.
# THE INSTRUMENTS ARE CITABLE, and for a while they were the only thing here that was not.
#
# The grid, the reservoirs and the weather live in the preamble, because they are small and
# every question gets them whether it asked or not. That was the right call and it left them
# with no id, while all 322 blocks below have one. The model is told to cite what it says, and
# for a grid figure there was nothing to cite, so it reached for the nearest thing and then
# corrected itself IN THE PUBLISHED ANSWER:
#
#   "the highest peak was 90352.7 MW on August 20th, 2026, the water record, actually that
#    citation belongs to the grid watch, not a reservoir"
#
# A reader watched the machine think. Nothing downstream could catch it either, because every
# sentence was true and every numeral was authorised.
#
# THE IDS GO MID LINE, NEVER AT THE START OF ONE. The worker splits the pack on a line opening
# with "[[", so an instrument id at the head of a line would be cut out of the preamble and
# handed over as a block with no body. The split contract's self-test asserts exactly that and
# the tally has always placed its citations this way.
INSTRUMENT_CITES = {
    "grid": ["the ERCOT grid watch", "grid/", "ERCOT grid watch"],
    "water": ["the water record", "water/", "Texas reservoir storage"],
    # The weather has no page of its own, so this cited `data/`. That page is gone with the
    # record download, and the front page is where the reading actually appears.
    "weather": ["the weather record", "", "Weather at the anchor station"],
}


def cites(items: list, dossiers: list, county_blocks: list, water_blocks: list,
          places: set = frozenset()) -> dict:
    """Every citable id, as [what the link says, where it goes, what it is].

    The first element is the LABEL and it is not the title. See `cite_label` for why.
    """
    out = dict(INSTRUMENT_CITES)
    for it in items:
        out[it["id"]] = [cite_label("tx", it["title"]), f"item/{it['id']}/", it["title"]]
    for d in dossiers:
        name = (d.get("name") or "").strip()
        out[f"facility-{d['slug']}"] = [cite_label("facility", name, name),
                                        f"facility/{d['slug']}/", name]
    for b in county_blocks:
        bid = b[2:b.index("]]")]
        name = b[b.index("]]") + 2:b.index("\n")].strip()
        out[bid] = [cite_label("county", name),
                    f"place/{bid}/" if bid in places else "construction/", name]
    for b in water_blocks:
        bid = b[2:b.index("]]")]
        name = b[b.index("]]") + 2:b.index("\n")].strip()
        href = (f"water/reservoir/{bid.removeprefix('water-lake-')}/"
                if bid.startswith("water-lake-") else "water/")
        out[bid] = [cite_label("water", name), href, name]
    return out


def _places() -> set:
    """The county pages the site actually publishes, read off the built directory.

    ASSERTED RATHER THAN ASSUMED, because it is 24 of the 61 counties the construction register
    names and the gap is not visible from either ledger. Guessing the other way round would
    publish thirty seven citations pointing at pages that do not exist.
    """
    d = DOCS / "place"
    if not d.is_dir():
        return set()
    return {x.name for x in d.iterdir() if x.is_dir()}


def block_ids(pack: dict) -> list:
    """Every id the pack can be cited by, cut the way the worker cuts it.

    The worker splits both published body fields on the same fence to decide what to send, and
    ask_corpus needs the same list to decide what may be cited. Deriving it a second way from
    the ledgers is how a family ends up indexed and then refused at the answer checker.
    """
    fence = "\n\n" + DECISIONS_MARK + "\n\n"
    texts = [pack.get("pack") or "", pack.get("facility_pack") or ""]
    # THE INSTRUMENTS ARE CITABLE AND HAVE NO BLOCK, so a cut that only reads below the fence
    # misses them and the worker refuses a true citation to the grid watch. They are listed
    # here rather than derived, because there is nothing below the fence to derive them from.
    joined = "\n".join(texts)
    out = [k for k in INSTRUMENT_CITES if "[[" + k + "]]" in joined]
    for text in texts:
        if fence not in text:
            continue
        for block in text.split(fence, 1)[1].split("\n\n"):
            b = block.strip()
            if b.startswith("[[") and "]]" in b:
                out.append(b[2:b.index("]]")])
    return out


DECISIONS_MARK = "THE DECISIONS."


def self_test() -> int:
    ok = [True]

    def check(label, cond, detail=""):
        print(f"  {'PASS' if cond else 'FAIL'}  {label}{'  ' + detail if detail else ''}")
        if not cond:
            ok[0] = False

    print("dates")
    for iso, want in (("2026-07-09", "July 9th, 2026"), ("2026-08-01", "August 1st, 2026"),
                      ("2026-08-02", "August 2nd, 2026"), ("2026-08-03", "August 3rd, 2026"),
                      ("2026-08-11", "August 11th, 2026"), ("2026-08-12", "August 12th, 2026"),
                      ("2026-08-13", "August 13th, 2026"), ("2026-08-21", "August 21st, 2026")):
        check(f"{iso} reads {want}", longdate(iso) == want, longdate(iso))

    print("data center units")
    dossier_doc = _ledger(FACILITIES) or {}
    ledger_units = set()
    for dossier in dossier_doc.get("dossiers") or []:
        for fact in dossier.get("facts") or []:
            if fact.get("unit"):
                ledger_units.add(fact["unit"])
            ledger_units.update(q.get("unit") for q in (fact.get("quantities") or [])
                                if q.get("unit"))
    unmapped_units = sorted(ledger_units - set(UNIT_WORDS))
    check("every dossier unit has plain Ask wording", not unmapped_units, str(unmapped_units))
    check("gpm reads as gallons per minute",
          _quantity(1200, "gpm") == "1,200 gallons per minute",
          _quantity(1200, "gpm"))
    check("a power price reads as dollars per kilowatt hour",
          _quantity(0.047, "usd_per_kwh") == "$0.047 per kilowatt hour",
          _quantity(0.047, "usd_per_kwh"))
    money_values = (1_234, 9_500_000, 450_000_000, 3_000_000_000, 9_100_000_000)
    money_mismatches = [(value, _quantity(value, "usd"), fd.money(value))
                        for value in money_values
                        if _quantity(value, "usd") != fd.money(value)]
    check("Ask dollar formatting matches the facility formatter",
          not money_mismatches, str(money_mismatches))
    check("facility order keeps its ordinal in Ask",
          _quantity(1, "facility_order") == "1st facility",
          _quantity(1, "facility_order"))
    check("range, alternatives and context stay in facility prose",
          _fact({"label": "Cooling water", "minimum": 1_000_000,
                 "maximum": 2_000_000, "unit": "gallons"})
          == "Cooling water is 1 million to 2 million gallons"
          and _fact({"label": "Density", "alternatives": [25, 45, 65], "unit": "MW"})
          == "Density is 25 megawatts, 45 megawatts, or 65 megawatts")

    p = build()
    main_text = p["pack"]
    facility_text = p.get("facility_pack") or ""
    text = main_text + ("\n\n" + facility_text if facility_text else "")

    print("the record is all there")
    items = dk.load(LEDGER)
    check("every decision is in the pack", p["items"] == len(items), f"{p['items']} items")
    missing = [it["id"] for it in items if f"[[{it['id']}]]" not in main_text]
    check("every decision is citable by id", not missing, str(missing[:3]))

    print("the house voice, because the model writes what it reads")
    # A colon inside a quoted source is the source's and is left alone, so the check runs on
    # the pack with quoted spans removed. Clock times and ratios are numbers, not punctuation.
    #
    # THE INDEX IS CHECKED WITH IT. It is a separate field and it is a third of what the model
    # reads on every question, so leaving it out of these checks would mean two thirds of the
    # prompt keeping the house voice and one third teaching the model out of it.
    import re  # noqa: E402
    voiced = text + "\n\n" + p["index"]
    unquoted = re.sub(r'"[^"]*"', '""', voiced)
    unquoted = re.sub(r"\d{1,2}:\d{2}", "", unquoted)
    check("no colons outside a quoted source", ":" not in unquoted,
          repr(unquoted[max(0, unquoted.find(":") - 60):unquoted.find(":") + 20])
          if ":" in unquoted else "")
    check("no semicolons outside a quoted source", ";" not in unquoted,
          repr(unquoted[max(0, unquoted.find(";") - 60):unquoted.find(";") + 20])
          if ";" in unquoted else "")
    # Dashes and curly quotes get the same exemption, and for a stronger reason than the
    # colon does. Every one of them in this pack is inside a verbatim_quote, which is a
    # source's own words. "A verbatim quote is never touched" is a house rule, so the right
    # move is to leave them and let the checker catch the model if it copies the habit, not
    # to edit what somebody actually said.
    check("no em or en dashes outside a quoted source", not set("–—") & set(unquoted),
          repr(unquoted[max(0, min(unquoted.find(c) for c in "–—" if c in unquoted) - 50):][:90])
          if set("–—") & set(unquoted) else "")
    check("no curly quotes outside a quoted source", not set("‘’“”") & set(unquoted))
    check("no bare url reached the pack", "http" not in voiced,
          repr(voiced[max(0, voiced.find("http") - 50):voiced.find("http") + 40])
          if "http" in voiced else "")
    # The prompt has to NAME what it forbids, so "cannot" appears inside the rule banning it.
    # Same exemption, same reason.
    sys_unquoted = re.sub(r'"[^"]*"', '""', SYSTEM)
    check("the system prompt keeps its own rules",
          not (set("–—‘’“”") & set(sys_unquoted)) and "cannot" not in sys_unquoted)

    print("no verdict may be modelled by example")
    for banned in ("blackout", "will be approved", "is likely to pass"):
        check(f"the pack never says {banned!r}", banned not in text.lower())

    print("the instruments are current, never the series")
    grid = _feed("gridwatch")   # the repo's committed docs/, which is what a self-test reads
    if grid and len(grid.get("readings") or []) > GRID_DAYS:
        # A day older than the window proves the whole series leaked in. This used to read
        # "only the current and previous", which was the rule before a week question was
        # answerable at all, and GRID_DAYS carries the reasoning that replaced it.
        older = grid["readings"][-(GRID_DAYS + 1)].get("peak_load_mw")
        check(f"no settled day older than the last {GRID_DAYS} is shown",
              str(older) not in text, f"found {older}")
    peaks = [r.get("peak_load_mw") for r in (grid or {}).get("readings") or []]
    check(f"at most {GRID_DAYS} daily peaks reach the pack",
          sum(1 for x in peaks if x is not None and str(x) in text) <= GRID_DAYS,
          f"{sum(1 for x in peaks if x is not None and str(x) in text)}")
    check("no hourly array reached the pack",
          "hour_ending" not in text and "load_mw" not in text)

    print("the index, which is what makes sending a slice safe")
    idx = p["index"]
    check("every decision has a line in the index",
          all(f"[[{it['id']}]]" in idx for it in items),
          str([it["id"] for it in items if f"[[{it['id']}]]" not in idx][:3]))
    # THE INDEX CARRIES DECISIONS LINE BY LINE AND ROLLS THE OTHER THREE FAMILIES UP, so this
    # counts what earns its own line rather than what exists. A decision is something a reader
    # hunts one at a time, and its line carries seven fields no rollup could fold together. The
    # dossiers joined that rollup on 2026-09-03, once a hundred and fifty of them at a full line
    # each pushed the index past the ceiling: a dossier line was only ever a name and an id, and
    # names and ids are exactly what a rollup carries. So decisions get one line each here, and
    # the dossier, county and reservoir families each get one.
    dec_lines = [l for l in idx.splitlines() if l.rstrip().endswith("]]")]
    check("the index has exactly one line per decision, plus one rolled line per other family",
          len(dec_lines) == p["families"]["tx"],
          f'{len(dec_lines)} of {p["families"]["tx"]}')
    # THE ROLLUP DID NOT COST CITATION, which is the property that made the change safe rather
    # than merely cheaper. A dossier body sits in `facility_pack`, which the retrieval-off hatch
    # never sends, so a dossier is citable only from the index whenever its body is not
    # retrieved. Every dossier id must therefore still appear in the index though the dossiers no
    # longer each hold a line, and that is the thing this asserts, not the line count.
    _dossiers = (_ledger(FACILITIES) or {}).get("dossiers") or []
    missing_fac = [d["slug"] for d in _dossiers if f"[[facility-{d['slug']}]]" not in idx]
    check("every dossier is still citable from the index, though rolled onto one line",
          not missing_fac, str(missing_fac[:3]))

    # THE ROLLED HEAD MUST CARRY LOCATION EVIDENCE, and this is what the first version of the
    # roll-up got wrong. Dropping the location detail from the flat list made the always-sent
    # index name no county at all, so a question like "What data centers are in Taylor County?"
    # matched no dossier on the county string and the assembled prompt named the county zero
    # times. Grouping by county fixes it. Asserting the property directly, rather than trusting
    # the shape, catches the next accidental drop of it too.
    counties = {_facility_county(d) for d in _dossiers} - {None}
    missing_county = [c for c in counties if f"In {c}," not in idx]
    check("every county the dossiers name is present in the rolled head",
          not missing_county, str(sorted(missing_county)[:3]))
    # WHAT AN INDEX LINE IS ALLOWED TO PUT IN A READER'S HANDS.
    #
    # The worker authorises the numerals in what it actually sent, so every figure on a line
    # becomes sayable for an item whose body the model was never shown. That is correct for an
    # IDENTIFIER, which is the whole point of naming the thing, and wrong for a MEASUREMENT,
    # which is a claim about the world that only a body carries the evidence for.
    #
    # Docket numbers live in titles, so the line cannot be figure free without being useless.
    # The two checkable properties are that a line never INVENTS a number the record does not
    # already contain, and that no measurement rides on one.
    import re as _re  # noqa: E402
    line_nums = set()
    for line in idx.splitlines():
        if line.rstrip().endswith("]]"):
            line_nums |= set(_re.findall(r"\d[\d,]*(?:\.\d+)?",
                                        _re.sub(r"\[\[[^\]]+\]\]\s*$", "", line)))
    pack_nums = set(_re.findall(r"\d[\d,]*(?:\.\d+)?", text))
    check("the index never introduces a number the record does not carry",
          line_nums <= pack_nums, str(sorted(line_nums - pack_nums)[:3]))
    units = [u for u in (" MW", " MWh", "acre feet", "percent", "kWh", " GW")
             if any(u in l for l in idx.splitlines() if l.rstrip().endswith("]]"))]
    check("no measurement rides on an index line, only identifiers and a closing date",
          not units, str(units))
    check("the index is a fraction of the bodies it stands in for",
          p["index_chars"] < p["chars"] // 4,
          f"{p['index_chars']} against {p['chars']}")

    print("the split contract, which the worker cuts on")
    # The worker cuts both body fields on the same fence. That cut is only safe while each
    # field keeps its preamble above the fence and whole blocks below it.
    fence = "\n\n" + DECISIONS_MARK + "\n\n"
    sections = [("core", main_text), ("facility", facility_text)]
    blocks = []
    ids_by_section = {}
    for label, section in sections:
        check(f"the {label} pack carries the {DECISIONS_MARK!r} mark once",
              section.count(fence) == 1, str(section.count(fence)))
        pre, _, rest = section.partition(fence)
        check(f"nothing above the {label} mark could be mistaken for a block",
              not any(line.startswith("[[") for line in pre.splitlines()))
        cut = [b for b in rest.split("\n\n") if b.strip()]
        ids_by_section[label] = [b[2:b.index("]]")] for b in cut
                                 if b.startswith("[[") and "]]" in b]
        blocks.extend(cut)
    check("every block below the mark starts with an id at the start of a line",
          all(b.startswith("[[") for b in blocks),
          str([b[:40] for b in blocks if not b.startswith("[[")][:2]))
    # THE PACK IS FOUR FAMILIES NOW AND THIS USED TO ASSERT IT WAS ONE. It read "as many
    # blocks as decisions", which was true for as long as the decisions were all there was, and
    # went red the day the dossiers arrived. The contract it was really guarding is that every
    # block the builder emits comes back out of the cut whole, with its own id, and that is
    # what it asserts now, family by family, so a family losing its blocks is still caught.
    check("there are exactly as many blocks as the pack says it holds",
          len(blocks) == p["blocks"], f"{len(blocks)} blocks, {p['blocks']} declared")
    ids = [b[2:b.index("]]")] for b in blocks]
    check("the decisions come out first, in the record's own order",
          ids_by_section["core"][:len(items)] == [it["id"] for it in items])
    check("every facility body is in the facility field",
          len(ids_by_section["facility"]) == p["families"]["facility"],
          str(len(ids_by_section["facility"])))
    check("every id is unique", len(set(ids)) == len(ids),
          f"{len(ids) - len(set(ids))} repeated")
    check("every id is one the page's citation pattern can render",
          all(__import__("re").fullmatch(r"[a-z0-9-]+", i) for i in ids),
          str([i for i in ids if not __import__("re").fullmatch(r"[a-z0-9-]+", i)][:3]))
    fams = {}
    for i in ids:
        fams[familyOf(i)] = fams.get(familyOf(i), 0) + 1
    check("and every family is present in the count the pack publishes",
          fams == {k: v for k, v in p["families"].items() if v}, f"{fams} against {p['families']}")
    check("no body contains a blank line, which would split it in two",
          not any("\n\n" in b for b in blocks))

    # THE CITATION MAP IS A PURE FUNCTION OF WHAT IT IS HANDED, and for one commit it was not.
    # It decided which counties have a page of their own by LISTING docs/place/, which is the
    # previous build's output. Building into docs/ wipes that first and found none, building
    # into a temp directory found twenty four, and the same commit produced two different
    # sites. site_fresh_check went red on main, which is late.
    #
    # This is the same check that gate makes, made here, where it costs a second instead of
    # three minutes. If a county href ever stops tracking the `places` argument exactly, some
    # filesystem is being read again.
    print("the citation map answers to its arguments and to nothing else")
    none = cite_map(p["generated"], places=frozenset())
    one = cite_map(p["generated"], places={"county-bexar"})
    counties = [k for k in none if k.startswith("county-")]
    check("with no place pages, every county points at the register",
          counties and all(none[k][1] == "construction/" for k in counties),
          str([none[k][1] for k in counties if none[k][1] != "construction/"][:3]))
    check("naming one place page moves exactly that one county and no other",
          one["county-bexar"][1] == "place/county-bexar/"
          and sum(1 for k in counties if one[k][1] != "construction/") == 1,
          str(sorted(k for k in counties if one[k][1] != "construction/")))
    check("and the names never move, whatever the pages do",
          all(none[k][0] == one[k][0] for k in none))

    print("size, which is a bill and not a warning")
    approx = round(len(main_text) / 4)
    check(f"the index is under its ceiling of {MAX_INDEX_CHARS} chars, which is the one "
          f"every question pays for", len(p["index"]) <= MAX_INDEX_CHARS,
          f"{p['index_chars']:,}")
    check(f"the core pack is under its ceiling of {MAX_CHARS} chars",
          len(main_text) <= MAX_CHARS,
          f"{len(main_text)} chars, roughly {approx} tokens")

    print()
    print("ask_pack self-test clean" if ok[0] else "ask_pack self-test FAILED")
    return 0 if ok[0] else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--date", help="ISO date")
    ap.add_argument("--print", action="store_true", help="write every body field to stdout")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    p = build(args.date)
    if args.print:
        print(p["pack"])
        if p.get("facility_pack"):
            print("\n\n" + p["facility_pack"])
        return 0
    print(f"ask pack: {p['items']} decisions, {len(p['pack'])} core chars, "
          f"roughly {round(len(p['pack']) / 4)} tokens, ceiling {MAX_CHARS}")
    print(f"  facility bodies {len(p.get('facility_pack') or ''):,} chars, "
          f"total published bodies {p['chars']:,}")
    print(f"  index {p['index_chars']:,} chars, roughly {round(p['index_chars'] / 4)} tokens "
          f"on EVERY question, ceiling {MAX_INDEX_CHARS:,}")
    print("  blocks " + ", ".join(f"{k} {v}" for k, v in sorted(p["families"].items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
