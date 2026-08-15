#!/usr/bin/env python3
"""schema.py — the record as structured data, so a machine can read what a person reads.

WHY THIS EXISTS

Every one of the 148 built pages shipped the same two blocks, `WebSite` and `Organization`,
and nothing else. Five distinct types across the whole site, three of them on one page. The
sibling ships twenty, including 208 question and answer pairs, 122 articles, 69 breadcrumb
trails and a `Report` per decision carrying its own citations.

That gap is invisible from the page, which is how a build wave was marked complete over it.
Nothing renders differently, nothing throws, and the site simply does not say in machine
readable form any of what it says in prose.

It matters twice over. Search engines build rich results, breadcrumbs and dataset entries out
of exactly these blocks, and answer engines ingest them as the cleanest statement of what a
page asserts. A record whose whole argument is that it is checkable should be the easiest
record on the internet for a machine to check.

WHAT IS EMITTED, AND WHY EACH TYPE IS THE HONEST ONE

  Organization    one node at `/#org`, referenced by `@id` everywhere else. Repeating the
                  publisher object on 151 pages, which is what we did, builds no graph at all.
  Dataset         the record itself, at `/record/#dataset`. This is what Google Dataset Search
                  reads, and the docket is a genuine dataset with a licence and a schema.
  Report          one per tracked decision, `isPartOf` the dataset, carrying its citations,
                  the body that decides, where it applies and the span it covers.
  FAQPage         the questions a reader actually arrives with, answered from the record.
  BreadcrumbList  the trail, on every page that has one.
  CollectionPage  the hubs, so a listing is not mistaken for an article.

NO `NewsArticle`, DELIBERATELY. The sibling ships 122 because its item pages are written
articles. These are a RECORD. `Report` plus `Dataset` is what a tracked decision actually is,
and wearing `NewsArticle` to catch a rich result would be a small lie told to a machine, which
is the same as telling it to a reader.

`FAQPage` IS EMITTED WITH ITS EYES OPEN, and this reverses an earlier call in this repo that
was right about its own facts. `docket_dataset_ld` carried the note that `Dataset` is "the one
structured-data type with a documented, currently operating consumer" and that FAQ rich results
were retired. **That is true and it stays true.** Google cut FAQ rich results back to
well-known government and health sites in 2023, and this site is not one, so nothing here
should be justified by a rich result it will not get.

It is emitted for the other consumer, which is the one the owner actually asked about. Answer
engines and model crawlers read `FAQPage` as the cleanest available statement of what a page
asserts, question paired to answer, with no layout to strip. 633 pairs computed from a
fact-checked record is the most machine-legible form this record has. The honest summary is
that this buys ingestion quality rather than a blue-link decoration, and if that ever stops
being true the block should come out rather than be re-justified.

EVERY ANSWER IS COMPUTED, NEVER WRITTEN

An FAQ answer is published copy and the compute-not-generate law owns it. The question shapes
are a fixed list and each answer is assembled from named ledger fields and from arithmetic done
here in Python. No model writes one. A model writing an answer would be writing a claim, and a
claim in this project needs a claim-id and a fetched source.

The house rules apply to every sentence below: no first person, no colons or semicolons, no em
dashes, ordinal dates, "can't" rather than "cannot".

WHAT THIS FILE CANNOT DO. Check itself. JSON-LD lives inside a `<script>` and
`house_style_check` strips those before linting, for a good reason of its own, so the prose
here is the largest unlinted surface on the site until `schema_check.py` reads it. That gate is
not optional and ships with this.

    schema.py --self-test
"""
from __future__ import annotations

import argparse
import datetime as _dt
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Schema.org's own vocabulary for a body that decides. `type` in the ledger is our filing
# word; this is the public one, and the mapping is here rather than in the ledger so a
# vocabulary change never rewrites the record.
DECIDER_TYPE = {
    "state-agency": "GovernmentOrganization",
    "federal-agency": "GovernmentOrganization",
    "legislature": "GovernmentOrganization",
    "court": "GovernmentOrganization",
    "city": "GovernmentOrganization",
    "county": "GovernmentOrganization",
    "special-district": "GovernmentOrganization",
    "utility": "Organization",
    "company": "Organization",
    "university": "CollegeOrUniversity",
    "nonprofit": "Organization",
}

LICENSE = "https://creativecommons.org/licenses/by/4.0/"


class Ctx:
    """What the builder knows and this module needs, passed in rather than imported.

    `site_build` imports this file, so this file importing it back would be a cycle. The three
    label functions are passed rather than reimplemented because each one is a house rule with
    a written reason, and a second copy is how a URL and a heading drift apart.
    """

    def __init__(self, *, site_url, site_name, topic_label, room_label, ordinal):
        self.site_url = site_url.rstrip("/")
        self.site_name = site_name
        self.topic_label = topic_label
        self.room_label = room_label
        self.ordinal = ordinal

    def url(self, path: str = "") -> str:
        return f"{self.site_url}/{path.lstrip('/')}" if path else f"{self.site_url}/"


# ------------------------------------------------------------------ small computed helpers
def _date(s: str):
    try:
        return _dt.date.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def _dates(it: dict) -> list:
    out = [(_date(k.get("date")), k) for k in it.get("key_dates") or []]
    return sorted([(d, k) for d, k in out if d], key=lambda p: p[0])


def _counties(it: dict) -> list:
    return sorted((it.get("geography") or {}).get("counties") or [])


def _sources(it: dict) -> list:
    """Distinct sources behind an item, in first-seen order, deduplicated by URL.

    Deduplicated because a claim set of six routinely rests on three documents, and a citation
    list that repeats one URL four times tells a machine the record is thinner than it is.
    """
    seen, out = set(), []
    for c in it.get("claims") or []:
        u = c.get("source_url")
        if u and u not in seen:
            seen.add(u)
            out.append(c)
    return out


def source_titles(items: list) -> set:
    """Every source title in the record, which is QUOTED MATERIAL and never linted.

    `house_style_check` strips `<blockquote>` and `<cite>` before it reads a page, because
    rewriting a source's own words to fit house style is falsifying a quotation, which is a
    far worse failure than an inconsistent dash. **A document's TITLE is the document's own
    words by exactly the same argument.** The Federal Register really did name a notice
    "Proposed Information Collection; ATUS Artificial Intelligence (AI) Questions", and the
    Southwest Power Pool really is joined to the Association of Electric Companies of Texas by
    an em dash in the title of the thing that was fetched. Neither is ours to tidy.

    So the exemption is DERIVED FROM THE RECORD rather than declared. A span is exempt only if
    it appears verbatim as a `source_title` on a claim, which means it cannot be used to smuggle
    a sentence this project wrote past the punctuation rules.
    """
    return {c["source_title"] for it in items for c in (it.get("claims") or [])
            if c.get("source_title")}


def strip_quoted(text: str, titles: set) -> str:
    """`text` with every verbatim source title removed, for linting the rest.

    Longest first, so a title that contains another is not left in fragments.
    """
    for t in sorted(titles, key=len, reverse=True):
        text = text.replace(t, " ")
    return text


def authorised_numerals(it: dict, today: str) -> set:
    """Every numeral a generated sentence about this item is allowed to state.

    DERIVED FROM THE LEDGER, NEVER FROM THE GENERATOR. That distinction is the whole value.
    Building the allow-list from the same code that writes the sentence would be circular and
    would prove nothing, so this reads the record's own fields and the counts of its own
    collections. If the generator ever computed nineteen counties where the record holds
    twenty two, nineteen would not be in this set.

    It is the same discipline the ask lane arrived at, written down in its worklog: a machine
    may state a number only if that number was in what it was given.

    WHAT THIS PROVES, said exactly. That every figure traces to a value in the record or to a
    sanctioned count over it. It does NOT prove the arithmetic chose the right operation, which
    is what the self-test's own assertions are for. Two different questions, two mechanisms.
    """
    out: set[str] = set()

    def add(n):
        out.add(str(n))

    for d, k in _dates(it):
        add(d.year), add(d.day), add(d.month)
        add(f"{d.day:02d}"), add(f"{d.month:02d}")
        # The gap to today, which is what "in three days" and "tomorrow" are rendered from.
        now = _date(today)
        if now:
            add(abs((d - now).days))
    counties = _counties(it)
    for n in (len(counties), max(0, len(counties) - 4)):
        add(n)
    srcs = _sources(it)
    add(len(srcs))
    add(sum(1 for c in srcs if str(c.get("source_type", "")).startswith("primary")))
    # THE DAY THE RECORD WAS LAST CHECKED, which one generated sentence states and which is
    # not in key_dates. Missing it made a correctly rendered date look invented.
    lv = _date(it.get("last_verified"))
    if lv:
        add(lv.year), add(lv.day), add(lv.month)
        add(f"{lv.day:02d}"), add(f"{lv.month:02d}")

    # Numerals already inside ledger prose. `summary` and `public_access.how` are reader copy
    # and are gated by the page's own numeral lint, so a figure quoted out of them is one the
    # record already stands behind.
    for field in (it.get("summary"), (it.get("public_access") or {}).get("how"),
                  it.get("title"), *[k.get("note") for k in it.get("key_dates") or []]):
        if field:
            out |= set(numerals_in(field))
    return out


# ONE TOKENISER FOR THE WHOLE PROJECT, borrowed rather than written again.
#
# This file had its own, `\d[\d,]*(?:\.\d+)?%?`, and it was wrong in the exact way
# `numeral_lint` had already documented and fixed: a token that may contain a comma but need not
# END on a digit swallows the sentence's punctuation. "Room 170, Austin" came back as the token
# "170," which then matched the identical figure nowhere, so a correctly rendered address looked
# like an invented number.
#
# The lesson is not "fix the regex". It is that there was a second regex at all. `numeral_lint`
# owns what a numeral is, so it is imported, and the two halves of every comparison are now
# incapable of disagreeing.
import numeral_lint as _nl                                                        # noqa: E402


def numerals_in(text: str) -> list:
    return _nl.NUMERAL.findall(text or "")


def _plural(n: int, one: str, many: str) -> str:
    return one if n == 1 else many


def _spell(n: int) -> str:
    """Small counts as words, so a sentence does not open on a digit.

    Every one of these is still a COMPUTED value. Spelling a number the code counted is a
    rendering rule, the same as rounding, and not a numeral anybody typed.
    """
    words = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
             "ten", "eleven", "twelve")
    return words[n] if 0 <= n < len(words) else str(n)


# ------------------------------------------------------------------ the nodes
def org_node(ctx: Ctx) -> dict:
    """The publisher, defined once. Everything else points at this by `@id`."""
    return {
        "@type": "Organization",
        "@id": ctx.url("#org"),
        "name": ctx.site_name,
        "url": ctx.url(),
        "description": "A public, fact-checked record of decisions about artificial "
                       "intelligence in Texas.",
    }


def dataset_node(ctx: Ctx, items: list, today: str) -> dict:
    """The record as a dataset, which is what it is and what Dataset Search reads."""
    spans = [d for it in items for d, _ in _dates(it)]
    node = {
        "@type": "Dataset",
        "@id": ctx.url("record/#dataset"),
        "name": f"{ctx.site_name}, the tracked record",
        "description": "Every tracked decision about artificial intelligence in Texas, with "
                       "the body that decides, the dates that matter, whether the public has "
                       "a way in, and a fetched source behind every fact.",
        "url": ctx.url("record/"),
        "license": LICENSE,
        "isAccessibleForFree": True,
        "inLanguage": "en-US",
        "creator": {"@id": ctx.url("#org")},
        "publisher": {"@id": ctx.url("#org")},
        "dateModified": today,
        "keywords": ["Texas", "artificial intelligence", "data centers", "ERCOT",
                     "public records", "state policy"],
        "spatialCoverage": {"@type": "State", "name": "Texas"},
        "distribution": [{
            "@type": "DataDownload",
            "encodingFormat": "application/json",
            "contentUrl": ctx.url("docket.json"),
        }],
        "variableMeasured": [
            {"@type": "PropertyValue", "name": "status",
             "description": "Whether the decision is pending, decided or withdrawn."},
            {"@type": "PropertyValue", "name": "public_access",
             "description": "Whether a member of the public has a dated way to take part."},
            {"@type": "PropertyValue", "name": "claims",
             "description": "Each fact with its verbatim quote and the source it was "
                            "fetched from."},
        ],
    }
    if spans:
        node["temporalCoverage"] = f"{min(spans).isoformat()}/{max(spans).isoformat()}"
    return node


def report_node(ctx: Ctx, it: dict, today: str) -> dict:
    """One tracked decision, with everything the record holds about it."""
    ds = _dates(it)
    url = ctx.url(f"item/{it['id']}/")
    dec = it.get("decider") or {}
    node = {
        "@context": "https://schema.org",
        "@type": "Report",
        "@id": url + "#report",
        "headline": it["title"],
        "name": it["title"],
        "description": it["summary"],
        "url": url,
        "identifier": it["id"],
        "inLanguage": "en-US",
        "license": LICENSE,
        "isAccessibleForFree": True,
        "author": {"@id": ctx.url("#org")},
        "publisher": {"@id": ctx.url("#org")},
        "isPartOf": {"@id": ctx.url("record/#dataset")},
        "dateModified": it.get("last_verified") or today,
        "keywords": sorted({ctx.topic_label(it["topic"]), "Texas",
                            "artificial intelligence"} | ({dec["name"]} if dec.get("name")
                                                          else set())),
        "about": {"@type": "Thing", "name": it["title"], "description": it["summary"]},
    }
    if ds:
        node["datePublished"] = ds[0][0].isoformat()
        node["temporalCoverage"] = f"{ds[0][0].isoformat()}/{ds[-1][0].isoformat()}"

    if dec.get("name"):
        node["mentions"] = [{
            "@type": DECIDER_TYPE.get(dec.get("type"), "Organization"),
            "name": dec["name"],
        }]

    node["spatialCoverage"] = _spatial(it)

    cites = [{"@type": "CreativeWork", "name": c.get("source_title") or c["source_url"],
              "url": c["source_url"]}
             for c in _sources(it) if c.get("source_url")]
    if cites:
        node["citation"] = cites
    return node


def _spatial(it: dict):
    """Where the decision applies, as Place nodes rather than as a sentence.

    A county list is the most machine useful thing this record holds about geography and it
    renders today only as prose in a chip row. Twenty two counties on one transmission line is
    twenty two places a query could match.
    """
    g = it.get("geography") or {}
    if g.get("statewide"):
        return {"@type": "State", "name": "Texas"}
    out = []
    if g.get("metro"):
        out.append({"@type": "Place", "name": g["metro"],
                    "containedInPlace": {"@type": "State", "name": "Texas"}})
    for c in _counties(it):
        out.append({"@type": "AdministrativeArea", "name": f"{c} County",
                    "containedInPlace": {"@type": "State", "name": "Texas"}})
    if not out:
        return {"@type": "State", "name": "Texas"}
    return out[0] if len(out) == 1 else out


# ------------------------------------------------------------------ the questions
def qa_pairs(ctx: Ctx, it: dict, today: str) -> list:
    """The questions a reader arrives with, answered from the record and nothing else.

    A FIXED LIST OF SHAPES. Every answer is assembled from named fields and from arithmetic
    done here, so the whole set is reproducible from the ledger and none of it is written.

    A question whose answer the record does not hold is DROPPED rather than answered vaguely.
    "No information is available" is a sentence that helps nobody and it would be the most
    repeated sentence on the site.
    """
    t = it["title"]
    now = _date(today) or _dt.date.today()
    ds = _dates(it)
    g = it.get("geography") or {}
    dec = (it.get("decider") or {}).get("name")
    pa = it.get("public_access") or {}
    out = []

    def add(q, a):
        if a:
            out.append((q, a))

    add(f"What is {t}?", it["summary"])

    if dec:
        add(f"Who decides {t}?",
            f"{dec} decides. The record names the deciding body for every entry it carries.")

    # CAN THE PUBLIC TAKE PART. The most consequential answer on the page, so it is built from
    # the room the schema assigned rather than from a guess, and `contact_only` is worded to
    # claim only what that room actually means. Saying "no formal process" there was wrong on
    # real items and is a fault this project already paid for once.
    room, how = pa.get("room"), (pa.get("how") or "").strip()
    if room == "open_comment":
        add(f"Can the public comment on {t}?",
            how or "A comment window is open. The item page carries the filing route.")
    elif room == "open_meeting":
        add(f"Can the public take part in {t}?",
            how or "A public meeting is scheduled where testimony is possible.")
    elif room == "contact_only":
        add(f"Can the public take part in {t}?",
            (how + " " if how else "")
            + "No dated public window is on the record. The deciding body is named and "
              "reachable.")
    elif room == "closed":
        add(f"Can the public take part in {t}?",
            how or "No public participation route is open for this decision.")

    # WHERE. Counties are counted rather than listed past a handful, because a sentence naming
    # twenty two of them is not an answer anybody reads.
    counties = _counties(it)
    if g.get("statewide"):
        add(f"Where in Texas does {t} apply?", "It applies statewide.")
    elif g.get("metro") and not counties:
        add(f"Where in Texas does {t} apply?", f"It applies in the {g['metro']} area.")
    elif counties:
        n = len(counties)
        named = ", ".join(counties[:4])
        rest = "" if n <= 4 else f", and {_spell(n - 4) if n - 4 < 13 else n - 4} more"
        where = f"{named} {_plural(n, 'County', 'Counties')}{rest}"
        if g.get("metro"):
            where += f", in the {g['metro']} area"
        add(f"Where in Texas does {t} apply?", f"It covers {where}.")

    status = it.get("status")
    if status:
        add(f"Has {t} been decided?", {
            "pending": "It is pending. No final decision is on the record.",
            "decided": "It has been decided. The dates on the item page carry when.",
            "withdrawn": "It was withdrawn.",
        }.get(status, f"Its status on the record is {status}."))

    # WHAT HAPPENS NEXT. The next dated thing in the future, computed against today.
    ahead = [(d, k) for d, k in ds if d > now]
    if ahead:
        d, k = ahead[0]
        days = (d - now).days
        when = "tomorrow" if days == 1 else f"in {_spell(days) if days < 13 else days} days"
        # THE KIND, NOT THE NOTE. A `key_dates` note is free text and is not gated as reader
        # copy anywhere, so notes run long: embedding one produced answers of 33 words against
        # a 30 word backstop. The kind is short, always present and always true, and the note
        # itself is on the item page where a reader who wants the detail already is.
        add(f"What happens next with {t}?",
            f"A {k.get('kind', 'step').replace('_', ' ')} is set for "
            f"{ctx.ordinal(d)}, {when}.")
    elif ds:
        d, k = ds[-1]
        add(f"What happens next with {t}?",
            f"No future date is on the record. The last dated step was a "
            f"{k.get('kind', 'step').replace('_', ' ')} on {ctx.ordinal(d)}.")

    if ds:
        first, _ = ds[0]
        add(f"When did {t} start?",
            f"The earliest date on its record is {ctx.ordinal(first)}, {first.year}.")

    topic = it.get("topic")
    if topic:
        add(f"What kind of decision is {t}?",
            f"It is filed under {ctx.topic_label(topic).lower()}"
            + (f", decided by {dec}." if dec else "."))

    srcs = _sources(it)
    if srcs:
        names = sorted({c.get("source_title") for c in srcs if c.get("source_title")})
        n = len(srcs)
        primary = sum(1 for c in srcs if str(c.get("source_type", "")).startswith("primary"))
        line = (f"{_spell(n).capitalize()} {_plural(n, 'source', 'sources')} back it"
                + (f", {_spell(primary)} of them primary" if primary else "") + ".")
        if names:
            line += " " + ", ".join(names[:4]) + "."
        add(f"What sources back {t}?", line)

    if g.get("on_ercot") is not None:
        add(f"Is {t} on the ERCOT grid?",
            "Yes. It sits inside the ERCOT interconnection." if g["on_ercot"]
            else "No. It sits outside the ERCOT interconnection.")

    add(f"When was {t} last checked?",
        f"Every fact on it was last verified against its source on "
        f"{ctx.ordinal(_date(it['last_verified']))}, {it['last_verified'][:4]}."
        if _date(it.get("last_verified")) else None)

    return out


def faq_node(ctx: Ctx, it: dict, today: str) -> dict | None:
    pairs = qa_pairs(ctx, it, today)
    if not pairs:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "@id": ctx.url(f"item/{it['id']}/") + "#faq",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}}
                       for q, a in pairs],
    }


def breadcrumbs(ctx: Ctx, trail: list) -> dict:
    """`trail` is [(name, path)], site root first, current page last."""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n,
                             "item": ctx.url(p)} for i, (n, p) in enumerate(trail)],
    }


def collection_node(ctx: Ctx, *, name: str, path: str, description: str, count: int) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": name,
        "description": description,
        "url": ctx.url(path),
        "isPartOf": {"@id": ctx.url("#org")},
        "mainEntity": {"@type": "ItemList", "numberOfItems": count},
    }


def item_nodes(ctx: Ctx, it: dict, today: str) -> list:
    """Everything an item page emits, in a stable order so the build stays byte identical."""
    out = [report_node(ctx, it, today)]
    f = faq_node(ctx, it, today)
    if f:
        out.append(f)
    out.append(breadcrumbs(ctx, [(ctx.site_name, ""), ("The record", "record/"),
                                 (it["title"], f"item/{it['id']}/")]))
    return out


# ------------------------------------------------------------------ self-test
def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import json
    import site_build as sb

    ctx = Ctx(site_url=sb.SITE_URL, site_name=sb.SITE_NAME, topic_label=sb.topic_label,
              room_label=sb.room_label, ordinal=sb.ordinal)
    items = json.loads((REPO_ROOT / "ledger" / "docket.json").read_text())["items"]
    today = "2026-08-15"

    ok("the record loads", len(items) > 10, str(len(items)))

    # ---- the graph joins up
    org = org_node(ctx)
    ds = dataset_node(ctx, items, today)
    ok("the organization has a stable id", org["@id"].endswith("/#org"))
    ok("the dataset points at the organization",
       ds["creator"]["@id"] == org["@id"] and ds["publisher"]["@id"] == org["@id"])
    ok("the dataset carries a licence and a distribution",
       ds["license"] == LICENSE and ds["distribution"][0]["contentUrl"].endswith("docket.json"))
    ok("...and a temporal span computed from the record", "/" in ds.get("temporalCoverage", ""))

    r = report_node(ctx, items[2], today)
    ok("a report is part of the dataset", r["isPartOf"]["@id"] == ds["@id"])
    ok("...and authored by the organization", r["author"]["@id"] == org["@id"])
    ok("...and carries its citations", len(r.get("citation", [])) >= 1, str(r.get("citation")))
    ok("...deduplicated by url",
       len({c["url"] for c in r.get("citation", [])}) == len(r.get("citation", [])))
    ok("...and names the deciding body as a government organization",
       r["mentions"][0]["@type"] == "GovernmentOrganization", str(r.get("mentions")))
    ok("...and its counties as places",
       isinstance(r["spatialCoverage"], list) and len(r["spatialCoverage"]) > 5,
       str(type(r["spatialCoverage"])))

    # ---- NO NewsArticle anywhere. The type is the claim, and these are a record.
    every = [n for it in items for n in item_nodes(ctx, it, today)]
    ok("nothing is marked as a news article",
       not any(n.get("@type") == "NewsArticle" for n in every))

    # ---- the questions
    pairs = qa_pairs(ctx, items[2], today)
    ok("an item yields a useful question set", len(pairs) >= 7, str(len(pairs)))
    ok("...with no duplicate questions", len({q for q, _ in pairs}) == len(pairs))
    ok("...and no empty answer", all(a and a.strip() for _, a in pairs))
    ok("every item yields at least four questions",
       min(len(qa_pairs(ctx, it, today)) for it in items) >= 4,
       str(min((len(qa_pairs(ctx, it, today)), it["id"]) for it in items)))

    # THE HOUSE RULES, on every generated sentence. This is the surface no other gate reads.
    #
    # Linted with the source TITLES stripped first, on `house_style_check`'s own reasoning: a
    # quotation is never rewritten to fit house style, and a document's title is the document's
    # own words. Four real answers carry a semicolon or a dash for that reason and every one of
    # them is a federal notice or an organisation naming itself.
    titles = source_titles(items)
    raw = [a for it in items for _, a in qa_pairs(ctx, it, today)]
    answers = [strip_quoted(a, titles) for a in raw]
    quests = [q for it in items for q, _ in qa_pairs(ctx, it, today)]
    ok(f"no em or en dash in {len(answers)} generated answers",
       not any("—" in a or "–" in a for a in answers),
       next((a for a in answers if "—" in a or "–" in a), ""))
    ok("no semicolon in a generated answer", not any(";" in a for a in answers),
       next((a for a in answers if ";" in a), ""))
    # THE EXEMPTION IS NARROW AND IS PROVED SO. It may only ever remove a span that really is
    # in the record, never a sentence this file wrote.
    ok("the quoted exemption is derived from the record and not declared",
       len(titles) > 20 and all(any(t == c.get("source_title")
                                    for it in items for c in (it.get("claims") or []))
                                for t in list(titles)[:5]), str(len(titles)))
    ok("...and it does not exempt our own prose",
       ";" in strip_quoted("our own sentence; written here", titles))
    ok("no first person in a generated answer",
       not any(w in f" {a.lower()} " for a in answers
               for w in (" i ", " we ", " our ", " us ", " my ")),
       next((a for a in answers if " we " in f" {a.lower()} "), ""))
    ok("never \"cannot\"", not any("cannot" in a.lower() for a in answers))
    ok("no answer opens with And or But",
       not any(a.lstrip().startswith(("And ", "But ")) for a in answers))
    # A QUESTION IS COPY TOO, and it is the half a reader sees in a search result.
    ok("every question ends in a question mark", all(q.rstrip().endswith("?") for q in quests))

    # ---- determinism, which site_fresh_check requires
    ok("two runs produce identical nodes",
       json.dumps(item_nodes(ctx, items[3], today), sort_keys=True)
       == json.dumps(item_nodes(ctx, items[3], today), sort_keys=True))
    ok("...and every node is JSON serialisable", bool(json.dumps(every)))

    # ---- the breadcrumb
    b = breadcrumbs(ctx, [("A", ""), ("B", "record/"), ("C", "item/x/")])
    ok("the breadcrumb is positioned from one",
       [e["position"] for e in b["itemListElement"]] == [1, 2, 3])
    ok("...and its last entry is the page itself",
       b["itemListElement"][-1]["item"].endswith("/item/x/"))

    # ---- the drop rule: a bare item must not produce invented answers
    bare = {"id": "x", "title": "A bare item", "summary": "A summary.", "topic": "state-policy",
            "status": "pending", "decider": {}, "geography": {}, "key_dates": [],
            "public_access": {}, "claims": [], "last_verified": "2026-08-01"}
    bp = qa_pairs(ctx, bare, today)
    ok("an item with no sources is not asked about its sources",
       not any("sources back" in q for q, _ in bp))
    ok("...and no geography answer is invented",
       not any("Where in Texas" in q for q, _ in bp), str([q for q, _ in bp]))
    ok("...but what the record does hold is still answered", len(bp) >= 3, str(len(bp)))

    print("\nschema self-test: " + ("all passed" if not failures else f"{failures} FAILED"))
    return 0 if not failures else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    ap.print_help()
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                            # noqa: BLE001
        print(f"schema: broke: {exc}", file=sys.stderr)
        sys.exit(2)
