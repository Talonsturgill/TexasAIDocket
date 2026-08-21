#!/usr/bin/env python3
"""ask_pack.py — the published record, rendered as prose for one prompt.

WHAT THIS IS. The written answer lane puts the WHOLE record in front of the model and asks it
to answer from that. This file is that record. There is no retrieval, no embedding step, no
chunking and no similarity threshold, because the record fits in one context with room over.
The largest single source of wrong answers in a retrieval chatbot is retrieving the wrong
passage, and a record this size lets that failure mode be deleted rather than managed.

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

SIZE IS A HARD GATE, NOT A WARNING. Every token here is paid on every question asked, forever.
Raising the ceiling is a decision with a bill attached and never a fix for a red build.

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

LEDGER = Path(REPO) / "ledger" / "docket.json"
DOCS = Path(REPO) / "docs"

# The ceiling, in characters of rendered prose. Chosen from what the record actually needs
# today with headroom for growth, not from what it happens to measure. At roughly 4 chars a
# token this is about 55,000 tokens, which at Sonnet 5 intro rates is about 11 cents a cold
# question. Crossing it is a budget decision for the owner and a conversation, never a number
# to nudge upward to make CI green.
MAX_CHARS = 220_000

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


INDEX_HEAD = """THE INDEX. Every decision the record holds, one line each, in the order they
are filed. A line names what exists and never the detail. The full text of the decisions most
likely to answer this question follows below, and it is a SLICE, so an item appearing here with
no text below is still a real item this record carries.

If the answer lies in an item whose full text is not below, say the record carries it, cite it
by id and say what the line above states. Never state a figure, a date or a quote for an item
whose full text is not below, because the line is all there is to go on.

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

    return f"[[{it['id']}]] {it['title'].rstrip('.')}. " + ", ".join(bits) + "."


def index(items: list, today: str) -> str:
    """The whole index, which is the block the model always gets whatever else it does not.

    THIS IS THE SAFETY PROPERTY OF RETRIEVING AT ALL. A retrieval chatbot's worst failure is
    not missing a passage, it is answering as though the missing thing does not exist, and a
    reader has no way to see that happen. Handing over the complete list of what EXISTS costs
    a fraction of the bodies and deletes that failure rather than mitigating it. It also lets
    retrieval be generous, because being wrong about which bodies to send is now recoverable.
    """
    return INDEX_HEAD + "\n\n" + "\n".join(index_line(it, today) for it in items)


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
            f"ERCOT grid watch, measured for {longdate(r.get('date'))}",
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
            f"Texas reservoir storage, measured for {longdate(r.get('date'))}",
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


SYSTEM = """You answer questions about the Texas AI Docket, a public record of decisions
about artificial intelligence in Texas, from the record given to you below and from nothing
else.

WHAT YOU MAY SAY. Only what the record states. Every figure you write must appear in the
record exactly as you write it. Every decision you name must be one the record carries. If
the record does not answer the question, say so plainly and say what it does carry instead.
A short true answer beats a long one that reaches.

CITING. Write a decision's id in double square brackets, like [[tx-2026-0001]]. The page
turns that into a link. Never write a bare url.

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


def build(today: str = None, docs_dir=None) -> dict:
    today = today or _dt.date.today().isoformat()
    items = dk.load(LEDGER)

    parts = [
        f"THE TEXAS AI DOCKET, as it stood on {longdate(today)}. "
        f"It tracks {len(items)} decisions.",
    ]
    parts.append(tally(items, today))
    inst = instruments(docs_dir)
    if inst:
        parts.append("THE DAILY INSTRUMENTS.\n\n" + inst)
    parts.append("THE DECISIONS.")
    parts.extend(item_prose(it, today) for it in items)

    pack = "\n\n".join(parts)
    idx = index(items, today)
    return {
        "generated": today,
        "system": SYSTEM,
        # THE WHOLE RECORD, STILL PUBLISHED WHOLE, and it stays that way even though the worker
        # now sends a slice of it. This file is fetched by a worker that is deployed by hand,
        # by pasting, and the site rebuilds itself every day without asking anybody. Dropping a
        # field the live worker reads would take the ask box down the morning after a run, with
        # nothing in this repo to show for it. It is also the escape hatch: ASK_RETRIEVAL=off
        # sends this instead of a slice, one dashboard variable away, no deploy.
        "pack": pack,
        # THE INDEX, which is what makes sending a slice safe rather than merely cheaper. Every
        # decision gets a line whatever the retriever thinks, so the model always knows what
        # EXISTS and the retrieval failure that a reader cannot see, answering as though the
        # missing item is not there, is designed out instead of managed.
        "index": idx,
        "index_chars": len(idx),
        "chars": len(pack),
        "items": len(items),
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

    p = build()
    text = p["pack"]

    print("the record is all there")
    items = dk.load(LEDGER)
    check("every decision is in the pack", p["items"] == len(items), f"{p['items']} items")
    missing = [it["id"] for it in items if f"[[{it['id']}]]" not in text]
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
    if grid and len(grid.get("readings") or []) > 2:
        # Only the last two readings may appear. A third proves the series leaked in.
        third = grid["readings"][-3].get("peak_load_mw")
        check("only the current and previous grid readings are shown",
              str(third) not in text, f"found {third}")
    check("no hourly array reached the pack",
          "hour_ending" not in text and "load_mw" not in text)

    print("the index, which is what makes sending a slice safe")
    idx = p["index"]
    check("every decision has a line in the index",
          all(f"[[{it['id']}]]" in idx for it in items),
          str([it["id"] for it in items if f"[[{it['id']}]]" not in idx][:3]))
    check("the index has exactly one line per decision, plus its header",
          len([l for l in idx.splitlines() if l.startswith("[[")]) == len(items),
          str(len([l for l in idx.splitlines() if l.startswith("[[")])))
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
        if line.startswith("[["):
            line_nums |= set(_re.findall(r"\d[\d,]*(?:\.\d+)?",
                                        _re.sub(r"^\[\[[^\]]+\]\]", "", line)))
    pack_nums = set(_re.findall(r"\d[\d,]*(?:\.\d+)?", text))
    check("the index never introduces a number the record does not carry",
          line_nums <= pack_nums, str(sorted(line_nums - pack_nums)[:3]))
    units = [u for u in (" MW", " MWh", "acre feet", "percent", "kWh", " GW")
             if any(u in l for l in idx.splitlines() if l.startswith("[["))]
    check("no measurement rides on an index line, only identifiers and a closing date",
          not units, str(units))
    check("the index is a fraction of the bodies it stands in for",
          p["index_chars"] < p["chars"] // 4,
          f"{p['index_chars']} against {p['chars']}")

    print("the split contract, which the worker cuts on")
    # The worker cuts the pack back into a preamble and one block per decision rather than
    # being handed the bodies a second time in the same JSON. That cut is only safe while this
    # shape holds. workers/ask/test.js asserts the same thing from the other side.
    fence = "\n\n" + DECISIONS_MARK + "\n\n"
    check(f"the pack carries the {DECISIONS_MARK!r} mark once, fenced by blank lines",
          text.count(fence) == 1, str(text.count(fence)))
    pre, _, rest = text.partition(fence)
    check("nothing above the mark could be mistaken for a decision block",
          not any(l.startswith("[[") for l in pre.splitlines()))
    blocks = [b for b in rest.split("\n\n") if b.strip()]
    check("every block below the mark starts with an id at the start of a line",
          all(b.startswith("[[") for b in blocks),
          str([b[:40] for b in blocks if not b.startswith("[[")][:2]))
    check("there are exactly as many blocks as decisions",
          len(blocks) == len(items), f"{len(blocks)} blocks, {len(items)} decisions")
    ids = [b[2:b.index("]]")] for b in blocks]
    check("and the ids are unique and in the record's order",
          ids == [it["id"] for it in items])
    check("no decision body contains a blank line, which would split it in two",
          all("\n\n" not in item_prose(it, p["generated"]) for it in items))

    print("size, which is a bill and not a warning")
    approx = round(len(text) / 4)
    check(f"the pack is under its ceiling of {MAX_CHARS} chars", len(text) <= MAX_CHARS,
          f"{len(text)} chars, roughly {approx} tokens")

    print()
    print("ask_pack self-test clean" if ok[0] else "ask_pack self-test FAILED")
    return 0 if ok[0] else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--date", help="ISO date")
    ap.add_argument("--print", action="store_true", help="write the pack to stdout")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    p = build(args.date)
    if args.print:
        print(p["pack"])
        return 0
    print(f"ask pack: {p['items']} decisions, {p['chars']} chars, "
          f"roughly {round(p['chars'] / 4)} tokens, ceiling {MAX_CHARS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
