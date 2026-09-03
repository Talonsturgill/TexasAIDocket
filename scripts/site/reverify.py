#!/usr/bin/env python3
"""reverify.py — the re-check is a DIFF, and only the exceptions are worth a model.

WHY THIS EXISTS

Phase 3 of the daily routine said "for each item on the worklist, fetch one primary source and
update it", and that ran inside the model's own context. Every due page came back in full, every
run, whether or not one character had moved. With 69 items on a two day leash that is about 34
pages pulled into a context window each day to confirm that nothing happened.

The work itself is not a judgment. A claim here carries a `verbatim_quote` and the `source_url`
it came from, so the question "is this still true" is, on the overwhelming majority of days:

    fetch(source_url) -> is verbatim_quote still in the text?

That is a string containment test. It needs no model, and putting one in the loop costs real
money to be told nothing changed.

WHAT THIS DOES AND DELIBERATELY DOES NOT DO

It answers the cheap question for every due claim and hands back a worklist of only the ones
that need reading. Three outcomes matter and they are not the same kind of thing:

  UNCHANGED   the quote is still on the page. Nothing to decide. `--apply` stamps it.
  MISSING     the page answered and the quote is NOT on it any more. Something moved, and what
              it means is exactly the judgment this script must not make.
  UNREACHABLE the page did not answer. That is a fact about the record's certainty rather than
              about the world, and it is never stamped as a successful check.

**It never edits a claim, a quote, a status or a date.** The only field it writes is
`last_verified`, and only for an item whose every claim came back UNCHANGED. Anything else is
left exactly as it was, for the routine to read. A script that could rewrite a quote to make a
check pass is the one thing this project cannot have.

THE DEDUPE IS NOT AN OPTIMISATION, IT IS MOST OF THE SAVING

314 claims in the committed record cite 124 distinct urls. 61 percent of a naive per-claim fetch
is the same page again. Fetching per URL rather than per claim is free to write and is the single
largest win available here.

CONDITIONAL REQUESTS, AND WHY THE CACHE IS COMMITTED

Each url's ETag, Last-Modified and body hash are kept in `ledger/reverify.json`, so the next run
asks the server "has this changed" rather than "give me this". A 304 is a definitive unchanged
for almost no bytes.

That file is COMMITTED, and the reason is a fault this project has already had twice. A cache in
a container that is reclaimed when the run ends is not a cache, it is a slower first request. The
sibling scanner lost its whole no-repeat ledger that way and nothing went red for weeks.

WHAT IT ACTUALLY SAVES, MEASURED AGAINST THE COMMITTED RECORD ON 2026-08-25

Asserting a saving would be the same sin as asserting a figure, so here is the run:

    314 claims behind 124 urls, every one reachable, 96 seconds
    222 claims confirmed unchanged by code            zero model tokens
     92 claims this check cannot read                 handed over as before
     33 of 69 items stamped outright, 47 percent
     42 of 124 urls will send a conditional request next run

**The 92 are not a failure and they are not going away.** 30 are PDFs and most of the rest are
javascript portals and consent walls that serve a shell to a plain fetch. Those pages were always
going to need reading. The honest claim is that this removes about half the phase on day one and
grows, because every quote it locates is remembered, not that it removes the phase.

RUN IT BY EXIT CODE.

    0  every due claim is confirmed unchanged. There is nothing here for a model to read.
    1  at least one claim needs a person or a model. The report says which and why.
    2  the run could not be made, so nothing is known and nothing was stamped.

An exit of 1 is the normal, healthy signal on a day when the world moved. It is not a failure.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import html
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "ledger" / "docket.json"
CACHE = REPO_ROOT / "ledger" / "reverify.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import docket_staleness as ds  # noqa: E402
import docket_build as dk  # noqa: E402  the numeral machinery, one definition

UA = ("TexasAIDocket/1.0 re-verification (+https://texasaidocket.com) "
      "one conditional request per source per two days")
TIMEOUT = 30

UNCHANGED, MISSING, UNREACHABLE, UNREADABLE = (
    "unchanged", "missing", "unreachable", "unreadable")

# A SOURCE THIS CHECK CANNOT READ IS NOT A SOURCE THAT CHANGED, and telling them apart is the
# difference between a useful report and a boy who cried wolf. The first version had one bucket
# for both and reported 92 of 314 claims as missing on its very first run against the real
# record. Almost none of them had moved. 30 were PDFs, whose bytes flatten to nothing a quote
# can be found in, and most of the rest were javascript rendered portals and consent walls that
# serve a shell to a plain fetch. A phase handed 92 false alarms reads none of them.
PDF_HINT = (".pdf",)


# --------------------------------------------------------------------------- text
_TAG = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
_ANY = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def flatten(raw: bytes) -> str:
    """Page bytes to comparable text.

    THE QUOTE WAS TAKEN OFF A RENDERED PAGE AND THE FETCH RETURNS MARKUP, so a raw `in` test
    fails on any quote whose words are split by a tag, which is most of them once a source puts
    a case number in a `<strong>`. Tags out, entities decoded, whitespace collapsed, and the
    comparison happens on what a reader would have seen.

    A FEED ESCAPES ITS HTML INSIDE ITS XML, AND ONE PASS CANNOT READ THAT (2026-09-03).
    An RSS description is markup carried as text, so the bytes hold
    `&lt;strong&gt;Project&lt;/strong&gt; 58482`. The strip runs first and finds no tag to
    strip, the unescape runs second and turns it into a literal `<strong>Project</strong> 58482`
    sitting in the flattened text. The quote a reader would take off that feed, `Project 58482`,
    can therefore NEVER match, however many runs re-check it.

    Measured on the PUCT calendar feed, which this record tracks as an item of its own. Three
    claims across `tx-2026-0024` and `tx-2026-0002` reported as unreadable on every run for that
    reason alone, and a phase handed a permanent false alarm learns to skim the report.

    So the strip and the unescape run TWICE, and the second pass removes the markup the first
    revealed. The cost is a page that deliberately DISPLAYS escaped markup as visible content,
    where the second strip removes text a reader can see. That is rare, and it fails toward a
    missed match rather than a false one, which is the cheaper of the two errors here.
    """
    t = raw.decode("utf-8", "replace")
    # TWICE, and the docstring above says why. One pass cannot read a feed whose HTML is escaped
    # inside its XML, because the strip runs before the unescape that reveals the markup.
    for _ in range(2):
        t = _TAG.sub(" ", t)
        t = _ANY.sub(" ", t)
        t = html.unescape(t)
    # A non-breaking space is a space to a reader and a different codepoint to `in`.
    t = t.replace(" ", " ").replace("’", "'").replace("“", '"').replace("”", '"')
    return _WS.sub(" ", t).strip()


def norm_quote(q: str) -> str:
    q = q.replace(" ", " ").replace("’", "'").replace("“", '"').replace("”", '"')
    return _WS.sub(" ", q).strip()


# --------------------------------------------------------------------------- fetch
def fetch(url: str, cached: dict, opener=None) -> tuple[str, bytes | None, dict]:
    """`(state, body, meta)`. `state` is one of the three outcomes, body is None unless 200.

    The conditional headers are sent only when the cache actually holds them, because an
    `If-None-Match: None` is a header that makes every request unconditional and looks like it
    is doing the opposite.
    """
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    if cached.get("etag"):
        req.add_header("If-None-Match", cached["etag"])
    if cached.get("last_modified"):
        req.add_header("If-Modified-Since", cached["last_modified"])
    op = opener or urllib.request.urlopen
    try:
        with op(req, timeout=TIMEOUT) as r:
            body = r.read()
            meta = {"etag": r.headers.get("ETag"),
                    "last_modified": r.headers.get("Last-Modified"),
                    "hash": hashlib.sha256(body).hexdigest()}
            return UNCHANGED, body, meta
    except urllib.error.HTTPError as e:
        if e.code == 304:
            # THE SERVER SAID SO, which is the cheapest and the most certain answer available.
            return UNCHANGED, None, dict(cached)
        return UNREACHABLE, None, {"status": e.code}
    except Exception as e:  # noqa: BLE001  a refusal, a timeout and a bad tls all mean the same
        return UNREACHABLE, None, {"status": type(e).__name__}


# --------------------------------------------------------------------------- the check
def check(items: list, cache: dict, opener=None) -> tuple[list, dict, dict]:
    """Every claim on `items`, one fetch per distinct url. Returns (findings, fresh cache, stats)."""
    by_url: dict[str, list] = {}
    for it in items:
        for c in (it.get("claims") or []):
            u = c.get("source_url")
            if u:
                by_url.setdefault(u, []).append((it, c))

    fresh, findings = dict(cache), []
    stats = {"urls": len(by_url), "claims": sum(len(v) for v in by_url.values()),
             "not_modified": 0, "fetched": 0, "unreachable": 0, "unreadable": 0}

    for url, pairs in sorted(by_url.items()):
        prior = cache.get(url) or {}
        state, body, meta = fetch(url, prior, opener)

        if state == UNREACHABLE:
            stats["unreachable"] += 1
            for it, c in pairs:
                findings.append({"item": it["id"], "claim": c["id"], "url": url,
                                 "state": UNREACHABLE, "why": str(meta.get("status"))})
            continue

        if body is None:
            # A 304. Every quote behind this url is unchanged and no text was read at all.
            stats["not_modified"] += 1
            fresh[url] = prior
            for it, c in pairs:
                findings.append({"item": it["id"], "claim": c["id"], "url": url,
                                 "state": UNCHANGED, "why": "304"})
            continue

        stats["fetched"] += 1
        proven = set(prior.get("proven") or [])
        meta["proven"] = sorted(proven)
        fresh[url] = meta

        if url.lower().endswith(PDF_HINT) or body[:5] == b"%PDF-":
            stats["unreadable"] += 1
            for it, c in pairs:
                findings.append({"item": it["id"], "claim": c["id"], "url": url,
                                 "state": UNREADABLE, "why": "a PDF, which this check can't read"})
            continue
        # THE BYTES CAN BE IDENTICAL AND THAT IS STILL NOT THE ANSWER. A matching hash proves
        # the page did not move, which proves the quote is still on it, so the containment test
        # is skipped. A DIFFERENT hash proves nothing either way, because a page that changed
        # its footer still carries the quote, so that case is read rather than assumed.
        # THE HASH SHORT CIRCUIT ONLY SERVES A CLAIM THAT WAS ALREADY PROVEN HERE, and getting
        # that wrong handed out proof this check had never established. The rule read "an
        # unchanged hash proves the page did not move, which proves the quote is still on it",
        # and the second half only follows if the quote was on it to begin with. For a claim
        # never located, an unchanged page proves the quote is still ABSENT. So a page that had
        # not moved marked every claim behind it found, added them to `proven`, and the run
        # after that reported them as real changes. tx-2026-0015-c2 is the one that showed it:
        # its stored quote is a pipe delimited digest the routine composed rather than anything
        # that appears on the page, so it can never be located, and it was proven anyway.
        prior_proven = set(prior.get("proven") or [])
        same = bool(prior.get("hash")) and prior["hash"] == meta["hash"]
        text = flatten(body)
        for it, c in pairs:
            q = norm_quote(c.get("verbatim_quote") or "")
            was = c["id"] in prior_proven
            found = bool(q) and ((same and was) or q in text)
            if found:
                proven.add(c["id"])
                findings.append({"item": it["id"], "claim": c["id"], "url": url,
                                 "state": UNCHANGED,
                                 "why": "hash" if (same and was) else "quote"})
            elif was:
                # THIS CHECK HAS FOUND THIS QUOTE ON THIS PAGE BEFORE, so it is readable, and
                # the quote going missing now is a real change rather than a format it cannot
                # parse. Authority earned on a previous run rather than assumed on this one.
                findings.append({"item": it["id"], "claim": c["id"], "url": url,
                                 "state": MISSING, "why": "the quote was here before and is gone"})
            else:
                findings.append({"item": it["id"], "claim": c["id"], "url": url,
                                 "state": UNREADABLE,
                                 "why": "the quote is not in the fetched text, and this check "
                                        "has never found it here, so it claims nothing"})
        meta["proven"] = sorted(proven)
    return findings, fresh, stats


# --------------------------------------------------------------------------- the movement line
def ordinal(d: _dt.date) -> str:
    n = d.day
    suf = "th" if 11 <= n <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{d:%B} {n}{suf}"


def movement_line(item: dict, today: _dt.date) -> str:
    """What an unchanged check writes into the item's own log.

    THE ROUTINE REQUIRES A LINE EVERY TIME, INCLUDING WHEN NOTHING MOVED, and it is right to:
    a reader who sees six dated lines saying the window is still open knows somebody looked six
    times, and a reader who sees one date does not.

    WRITTEN FROM THE ITEM'S OWN FIELDS RATHER THAN BY A MODEL, which is a feature and not a
    compromise. This sentence is the same sentence every time by nature, so a model writing it
    is a model paid to paraphrase, and paraphrase is exactly where a stray number or a softened
    fact enters a record whose whole promise is that neither does.

    IT HAS TO CLEAR `gate_narration`, which governs history notes as reader copy. That gate
    refuses first person, "unverified", "could not be verified" and any sentence about the
    machine's own work, so this names the DECISION and never the check. It also has to clear
    `house_style_check`, so it stays well under the thirty word backstop and takes the ordinal.
    """
    pa = item.get("public_access") or {}
    close = pa.get("closes")
    if close:
        try:
            shut = ds.parse_date(close)
        except Exception:  # noqa: BLE001  a malformed date is not this script's to correct
            shut = None
        if shut:
            # OPEN OR SHUT IS DERIVED FROM THE DATE, NEVER ASSERTED. The first version read the
            # close date and said "the comment window is still open, closing August 11th" on
            # August 25th, which is a sentence that contradicts its own second half. Four of the
            # ten items carrying a close date had already closed, so this would have written
            # four false statements into the public record on its first real run.
            #
            # docket_build says it in one line, "open or shut is derived, never stored", and
            # this code had the date in its hand and asserted the wrong half anyway.
            if shut >= today:
                return f"The comment window is still open, closing {ordinal(shut)}."
            return f"The comment window closed on {ordinal(shut)}."
    status = (item.get("status") or "").strip().lower()
    if status == "decided":
        return "Checked and unchanged. The decision still stands as decided."
    if status == "withdrawn":
        return "Checked and unchanged. The withdrawal still stands."
    return f"Checked and unchanged. Still {status or 'open'}, with no dated movement."


def apply(items: list, findings: list, today: _dt.date) -> list:
    """Stamp only the items whose EVERY claim came back unchanged. Returns the ids stamped.

    THE UNIT IS THE ITEM AND NOT THE CLAIM, deliberately. `last_verified` is a statement about
    the whole item, so stamping it while one of its four claims is unreachable would publish a
    date that says more than was actually checked.
    """
    state: dict[str, set] = {}
    for f in findings:
        state.setdefault(f["item"], set()).add(f["state"])
    clean = {i for i, s in state.items() if s == {UNCHANGED}}
    stamped = []
    for it in items:
        if it["id"] not in clean:
            continue
        it["last_verified"] = today.isoformat()
        # THE SHAPE IS THE RECORD'S, NOT A STRING. History entries are {date, note}, and the
        # movement gate looks for an entry whose date equals last_verified. Appending a plain
        # string stamped 55 items whose log the gate could not see, and it said so.
        # `checked` MARKS A NOTE THIS CHECK WROTE, and it is what makes the numeral gate below
        # possible. A movement note written by the research path legitimately states a figure
        # the record USED to hold, which is why history sits outside `gate_numerals` at all. A
        # note written here states only what was still true, so it may be held to a much harder
        # rule, and the marker is how the two are told apart without guessing from the prose.
        it.setdefault("history", []).append(
            {"date": today.isoformat(), "note": movement_line(it, today), "checked": True})
        stamped.append(it["id"])
    return stamped


# --------------------------------------------------------------------------- report
def report(findings: list, stats: dict, stamped: list | None) -> int:
    """THE THREE KINDS ARE PRINTED APART, because they are three different jobs.

    A `missing` is a lead. An `unreadable` is a page this check has no opinion about and never
    did. Printing them in one list taught a reader to skim the whole thing, which is how a real
    change hides among ninety pages that were only ever PDFs.
    """
    groups = {k: [f for f in findings if f["state"] == k]
              for k in (MISSING, UNREACHABLE, UNREADABLE)}
    # THE HEADLINE COUNTS REQUESTS AND THE SECTIONS COUNT CLAIMS, stated apart because mixing
    # them printed "13 were not readable" above a section headed "(92)". Two numbers for one
    # word, and the smaller one was the count of PDF urls while the larger was the count of
    # claims nobody could check. A reader reconciling those two is a reader not reading either.
    print(f"reverify: {stats['urls']} url(s) behind {stats['claims']} claim(s). "
          f"{stats['not_modified']} answered 304, {stats['fetched']} sent a body, "
          f"{stats['unreachable']} did not answer.")
    if stamped is not None:
        print(f"          {len(stamped)} item(s) stamped as checked and unchanged.")
    if not any(groups.values()):
        print("          every quote is still where it was. Nothing here needs reading.")
        return 0

    for state, header in (
            (MISSING, "SOMETHING MOVED. The quote was on this page before and is not now"),
            (UNREACHABLE, "THE SOURCE DID NOT ANSWER, so nothing about it is confirmed"),
            (UNREADABLE, "THIS CHECK CANNOT READ THESE, and claims nothing either way")):
        rows = groups[state]
        if not rows:
            continue
        print(f"\n  {header} ({len(rows)}):\n")
        for f in sorted(rows, key=lambda x: x["item"]):
            print(f"    {f['item']:14} {f['claim']}")
            print(f"                   {f['why']}")
            print(f"                   {f['url']}")
    return 1


# --------------------------------------------------------------------------- the note gate
def check_notes(items: list) -> list:
    """Every `checked` note may be re-worded freely and may not gain a figure.

    WHY THIS EXISTS. `gate_numerals` reads reader copy with `include_history=False`, on purpose
    and for a good reason: a movement line's job is often to say what the record USED to hold,
    and that figure is by definition in no current claim quote. So history notes are the one
    piece of published reader copy no numeral check reads.

    That was safe while this script wrote them, because it can only emit what it read out of the
    item. It stops being safe the moment a run re-words them, which is exactly what the routine
    is now told to do, because then a model is writing into the one place a model's numbers are
    not checked. This project's central law is that no number is ever produced by a language
    model, so the re-wording needs its own gate rather than the general exemption.

    THE BASELINE IS RECOMPUTED RATHER THAN STORED. `movement_line` is a pure function of the
    item, so the deterministic sentence this run would have written can be derived at check
    time from the same fields. That means no run artifact, and it means this runs in CI against
    what was committed rather than only inside the routine that wrote it. A gate that can only
    run in the process it is guarding is a convention.

    The rule is deliberately narrow. A re-worded note may use any figure the deterministic line
    used, and any figure the item's own claims quote. It may not introduce one from anywhere
    else, which leaves the run free to write a better sentence and not free to invent a number.
    """
    bad = []
    for it in items:
        allowed = set(dk._quoted_numerals(it))
        for h in (it.get("history") or []):
            if not isinstance(h, dict) or not h.get("checked"):
                continue
            try:
                when = ds.parse_date(h.get("date"))
            except Exception:  # noqa: BLE001
                bad.append(f'{it["id"]}: a checked note carries no readable date')
                continue
            base = set(dk._prose_numerals(movement_line(it, when)))
            for got in dk._prose_numerals(str(h.get("note") or "")):
                if got not in base and got not in allowed:
                    bad.append(
                        f'{it["id"]} {h["date"]}: the note states "{got}", which is in no claim '
                        f"quote and in nothing this check established. Re-wording may not add a "
                        f"figure")
    return bad


# --------------------------------------------------------------------------- the cache
CACHE_SPEC = 1


def load_cache() -> dict:
    """The url map, out of its envelope. A missing or unreadable cache is an empty one.

    An unreadable cache is not an error worth stopping for. The worst it costs is one run of
    unconditional requests, and the alternative is a re-verification phase that refuses to run
    because a cache file got truncated.
    """
    if not CACHE.is_file():
        return {}
    try:
        return json.loads(CACHE.read_text(encoding="utf-8")).get("sources") or {}
    except (json.JSONDecodeError, OSError, AttributeError):
        return {}


def save_cache(sources: dict, today: _dt.date) -> None:
    CACHE.write_text(json.dumps(
        {"_spec": {"version": CACHE_SPEC, "generated": today.isoformat(),
                   "note": "One row per source url. ETag and Last-Modified drive the next "
                           "conditional request, hash short circuits the text comparison, and "
                           "proven records which claim quotes have been located here, which is "
                           "what tells a real change apart from a page this check cannot read."},
         "sources": dict(sorted(sources.items()))}, indent=2) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- self-test
def self_test() -> int:  # noqa: C901
    fails = 0

    def ok(label, cond, detail=""):
        nonlocal fails
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}" + (f"  {detail}" if not cond else ""))
        if not cond:
            fails += 1

    class Resp:
        def __init__(self, body, headers=None):
            self._b, self.headers = body, headers or {}

        def read(self):
            return self._b

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def server(pages):
        """`pages` maps url to bytes, an int status, or a `304` sentinel."""
        def op(req, timeout=None):
            v = pages[req.full_url]
            if v == 304:
                raise urllib.error.HTTPError(req.full_url, 304, "nm", {}, None)
            if isinstance(v, int):
                raise urllib.error.HTTPError(req.full_url, v, "err", {}, None)
            return Resp(v, {"ETag": '"e1"'})
        return op

    today = _dt.date(2026, 8, 25)
    quote = "Rulemaking to Update Wholesale Transmission Cost Recovery"

    def item(iid, url, q, status="open", closes=None):
        it = {"id": iid, "status": status, "last_verified": "2026-08-20",
              "claims": [{"id": iid + "-c1", "verbatim_quote": q, "source_url": url}]}
        if closes:
            it["public_access"] = {"closes": closes}
        return it

    print("the quote is found through the markup a reader never sees")
    page = f"<html><body><p>x <strong>{quote}</strong> y</p></body></html>".encode()
    it = item("tx-1", "https://a/", quote)
    f, _, _ = check([it], {}, server({"https://a/": page}))
    ok("a quote split by a tag is still found", all(x["state"] == UNCHANGED for x in f), str(f))

    # A FEED THAT ESCAPES ITS HTML INSIDE ITS XML (2026-09-03). The PUCT calendar feed carries
    # its descriptions as escaped markup, so one strip-then-unescape pass leaves literal tags in
    # the flattened text and a reader's own quote can never match. Three claims in this record
    # reported unreadable on every run for that alone.
    feed = (b"<rss><channel><item><title>Public Comment Deadline</title>"
            b"<description>&lt;strong&gt;Project&lt;/strong&gt; 58482&lt;br /&gt;"
            b"&lt;strong&gt;Commissioners Hearing Room 7-100&lt;/strong&gt;</description>"
            b"</item></channel></rss>")
    ok("escaped markup inside a feed does not survive into the text",
       "<strong>" not in flatten(feed), flatten(feed))
    ok("...so a quote a reader would take off the feed is found",
       "Project 58482" in flatten(feed), flatten(feed))
    ok("...and a quote that is genuinely not there is still not found",
       "Project 99999" not in flatten(feed), flatten(feed))

    print("\nand each outcome is told apart from the others")
    # AUTHORITY IS EARNED. With no record of ever having found this quote here, the honest
    # answer is that the check has no opinion, not that the world moved.
    gone = item("tx-2", "https://b/", "a line that is not there")
    f, _, _ = check([gone], {}, server({"https://b/": page}))
    ok("a quote never seen here is UNREADABLE, not MISSING",
       f[0]["state"] == UNREADABLE, str(f))
    f, fresh2, _ = check([gone], {"https://b/": {"proven": ["tx-2-c1"]}},
                         server({"https://b/": page}))
    ok("...and once it HAS been found here, its absence is MISSING",
       f[0]["state"] == MISSING, str(f))
    # IT STAYS PROVEN, and that is the point rather than an oversight. `proven` records that
    # this page is readable and that this quote was once located on it. Both stay true after the
    # quote is removed, so every later absence is a real change too. Forgetting would hand the
    # page back its immunity the moment it changed, which is the one moment it should lose it.
    ok("...and it stays proven, so the next absence is a change too",
       "tx-2-c1" in fresh2["https://b/"]["proven"], str(fresh2))
    f, fresh3, _ = check([item("tx-2b", "https://b/", quote)], {}, server({"https://b/": page}))
    ok("a quote found here is recorded as proven",
       "tx-2b-c1" in fresh3["https://b/"]["proven"], str(fresh3))

    print("\nan unchanged page does not prove a quote it never carried")
    # THE HASH SHORT CIRCUIT GRANTED PROOF IT HAD NEVER ESTABLISHED. A page that had not moved
    # marked every claim behind it found, including ones whose quote is not on it at all, and
    # the run after that reported those as real changes.
    absent = item("tx-2z", "https://k/", "a line that is not on this page")
    prior = {"https://k/": {"hash": __import__("hashlib").sha256(page).hexdigest()}}
    f, fresh4, _ = check([absent], prior, server({"https://k/": page}))
    ok("an unproven claim is not waved through by a matching hash",
       f[0]["state"] == UNREADABLE, str(f))
    ok("...and it is not written into proven",
       "tx-2z-c1" not in (fresh4["https://k/"].get("proven") or []), str(fresh4))
    present = item("tx-2y", "https://k/", quote)
    pri2 = {"https://k/": {"hash": __import__("hashlib").sha256(page).hexdigest(),
                           "proven": ["tx-2y-c1"]}}
    f, _, _ = check([present], pri2, server({"https://k/": page}))
    ok("...while a proven claim still short circuits on the hash",
       f[0]["state"] == UNCHANGED and f[0]["why"] == "hash", str(f))

    print("\na PDF is never read, and is never reported as a change")
    f, _, st = check([item("tx-2c", "https://x/f.pdf", quote)], {},
                     server({"https://x/f.pdf": b"%PDF-1.7 binary"}))
    ok("a PDF is UNREADABLE", f[0]["state"] == UNREADABLE, str(f))
    ok("...counted as unreadable rather than fetched-and-changed", st["unreadable"] == 1, str(st))
    f, _, _ = check([item("tx-2d", "https://x/nosuffix", quote)], {},
                    server({"https://x/nosuffix": b"%PDF-1.7 binary"}))
    ok("...detected by its bytes when the url does not say pdf",
       f[0]["state"] == UNREADABLE, str(f))
    f, _, _ = check([item("tx-3", "https://c/", quote)], {}, server({"https://c/": 404}))
    ok("a 404 is UNREACHABLE and never unchanged", f[0]["state"] == UNREACHABLE, str(f))
    f, _, st = check([item("tx-4", "https://d/", quote)], {"https://d/": {"etag": '"e1"'}},
                     server({"https://d/": 304}))
    ok("a 304 is unchanged and reads no body", f[0]["state"] == UNCHANGED and st["fetched"] == 0,
       str(st))

    print("\none fetch per url, however many claims sit behind it")
    two = {"id": "tx-5", "status": "open", "claims": [
        {"id": "tx-5-c1", "verbatim_quote": quote, "source_url": "https://e/"},
        {"id": "tx-5-c2", "verbatim_quote": "y", "source_url": "https://e/"}]}
    hits = []

    def counting(req, timeout=None):
        hits.append(req.full_url)
        return Resp(page, {"ETag": '"e1"'})
    f, _, st = check([two], {}, counting)
    ok("two claims on one url are one request", len(hits) == 1 and st["claims"] == 2, str(hits))

    print("\nthe stamp is an ITEM level statement, so one bad claim withholds it")
    mixed = {"id": "tx-6", "status": "open", "last_verified": "2026-08-20", "claims": [
        {"id": "tx-6-c1", "verbatim_quote": quote, "source_url": "https://f/"},
        {"id": "tx-6-c2", "verbatim_quote": quote, "source_url": "https://g/"}]}
    f, _, _ = check([mixed], {}, server({"https://f/": page, "https://g/": 500}))
    stamped = apply([mixed], f, today)
    ok("an item with one unreachable source is NOT stamped", stamped == [], str(stamped))
    ok("...and its last_verified is untouched", mixed["last_verified"] == "2026-08-20")

    clean = item("tx-7", "https://h/", quote)
    f, _, _ = check([clean], {}, server({"https://h/": page}))
    stamped = apply([clean], f, today)
    ok("a wholly unchanged item IS stamped", stamped == ["tx-7"], str(stamped))
    ok("...with today's date", clean["last_verified"] == "2026-08-25")
    ok("...and one movement line", len(clean["history"]) == 1, str(clean.get("history")))

    print("\nthe movement line clears the gates that govern reader copy")
    import docket_build as db
    lines = [movement_line(item("x", "u", "q", status="open", closes="2026-09-01"), today),
             movement_line(item("x", "u", "q", status="open", closes="2026-08-11"), today),
             movement_line(item("x", "u", "q", status="decided"), today),
             movement_line(item("x", "u", "q", status="withdrawn"), today),
             movement_line(item("x", "u", "q", status=""), today)]
    # A CLOSE DATE IN THE PAST IS A CLOSED WINDOW. The cases below all used a future date, so
    # every one of them passed while the function said "still open, closing August 11th" on
    # August 25th. Four of the ten items carrying a close date were already shut.
    shut_line = movement_line(item("x", "u", "q", closes="2026-08-11"), today)
    open_line = movement_line(item("x", "u", "q", closes="2026-09-30"), today)
    ok("a window whose date has passed is reported closed",
       "closed on" in shut_line and "still open" not in shut_line, shut_line)
    ok("...and one still ahead is reported open",
       "still open" in open_line, open_line)
    ok("...and neither contradicts its own date",
       ordinal(_dt.date(2026, 8, 11)) in shut_line
       and ordinal(_dt.date(2026, 9, 30)) in open_line, shut_line + " | " + open_line)

    ok("every form is narration clean", not any(db.NARRATION.search(x) for x in lines),
       str([x for x in lines if db.NARRATION.search(x)]))
    # THE ENTRY IS {date, note} AND THE GATE READS THE DATE FIELD, so the note carries no date
    # of its own. This used to assert an ordinal in every line, which passed while the note was
    # a plain string carrying a prefix the record's own shape has no room for.
    ok("the entry carries the date as a field, not in the prose",
       clean["history"][-1] == {"date": "2026-08-25", "note": movement_line(clean, today),
                                "checked": True},
       str(clean["history"][-1]))
    ok("...and is marked as one this check wrote, which is what scopes the note gate",
       clean["history"][-1]["checked"] is True)
    ok("an ordinal appears only where a real date is named",
       ordinal(_dt.date(2026, 8, 11)) in shut_line, shut_line)
    ok("every form stays under the thirty word backstop",
       all(len(x.split()) <= 30 for x in lines), str([len(x.split()) for x in lines]))
    ok("no form carries a colon, a semicolon or a dash",
       not any(re.search(r"[:;–—]", x) for x in lines), str(lines))

    print("\na re-worded note may improve the sentence and may not add a figure")
    # THE FIXTURE CARRIES A CHECKED NOTE, asserted first, because the live record has none yet
    # and `--check-notes` reported "0 checked note(s), every figure traceable" against it. A
    # gate with nothing in scope prints the same clean line as a gate that passed.
    def noted(note, quote="the filing index stands at 67 filings"):
        return {"id": "tx-9", "status": "decided", "last_verified": "2026-08-25",
                "claims": [{"id": "tx-9-c1", "verbatim_quote": quote,
                            "source_url": "https://q/"}],
                "history": [{"date": "2026-08-25", "note": note, "checked": True}]}

    scope = noted(movement_line({"id": "tx-9", "status": "decided"}, today))
    ok("the fixture is in scope at all",
       any(h.get("checked") for h in scope["history"]), str(scope["history"]))
    ok("the deterministic sentence passes its own gate", not check_notes([scope]))
    ok("a re-worded sentence with no new figure passes",
       not check_notes([noted("Nothing moved. The decision entered on the record still "
                              "stands as it was written.")]))
    ok("a figure the claims quote is allowed",
       not check_notes([noted("Checked. The filing index still stands at 67 filings.")]))
    bad = check_notes([noted("Checked. The index is now at 71 filings.")])
    ok("a figure from nowhere is refused", bool(bad), str(bad))
    ok("...and the message names the figure", bad and '"71"' in bad[0], str(bad))
    # THE EXEMPTION SURVIVES FOR THE PATH IT WAS EARNED IN. A research note recording what the
    # record used to hold carries no marker and this gate has no opinion about it.
    research = noted("The filing index moved from 5782 to 5790.")
    research["history"][0].pop("checked")
    ok("an unmarked research note keeps the old exemption", not check_notes([research]))

    print("\nand the check never edits what it is checking")
    # PROVED BY BEHAVIOUR AND NOT BY GREPPING THIS FILE'S OWN SOURCE. The first version of this
    # block searched the source for `verbatim_quote"] =`, which passes for any assignment
    # written with different spacing, through a variable, or through dict.update, and whose
    # failure label rendered as "nothing assigns ] =" because it was slicing on a quote
    # character. An assertion nobody can read the output of is one nobody checks.
    import copy
    before = copy.deepcopy(clean)
    f2, _, _ = check([clean], {}, server({"https://h/": page}))
    apply([clean], f2, _dt.date(2026, 8, 26))
    ok("no claim is touched, quote and url included",
       clean["claims"] == before["claims"], str(clean["claims"]))
    ok("the status is left exactly as it was", clean["status"] == before["status"])
    changed = {k for k in clean if clean[k] != before.get(k)}
    ok("only last_verified and the movement log move",
       changed <= {"last_verified", "history"}, str(changed))

    print("\nreverify self-test: " + ("all passed" if not fails else f"{fails} FAILED"))
    return 1 if fails else 0


# --------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--today")
    ap.add_argument("--apply", action="store_true",
                    help="stamp the items whose every claim came back unchanged")
    ap.add_argument("--check-notes", action="store_true",
                    help="hold every re-worded `checked` note to the figures it may use")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    if a.check_notes:
        try:
            items = json.loads(LEDGER.read_text(encoding="utf-8"))["items"]
        except Exception as e:  # noqa: BLE001
            print(f"reverify: the record could not be read ({e})", file=sys.stderr)
            return 2
        bad = check_notes(items)
        n = sum(1 for i in items for h in (i.get("history") or [])
                if isinstance(h, dict) and h.get("checked"))
        if bad:
            print(f"reverify: {len(bad)} re-worded note(s) state a figure nothing established\n",
                  file=sys.stderr)
            for b in bad:
                print(f"  {b}", file=sys.stderr)
            return 1
        print(f"reverify: {n} checked note(s), every figure traceable")
        return 0

    today = _dt.date.fromisoformat(a.today) if a.today else _dt.date.today()
    try:
        record = json.loads(LEDGER.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        print(f"reverify: the record could not be read ({e})", file=sys.stderr)
        return 2
    items = record["items"]
    # THE ENVELOPE IS NOT DECORATION. port_audit requires every ledger to carry `_spec`, and it
    # is right to: a bare map has no way to say which shape it is, so the day this file gains a
    # field there is nothing for a reader to switch on.
    cache = load_cache()

    due, _, _ = ds.select(items, today, None)
    ids = {r["id"] for r in due}
    work = [i for i in items if i["id"] in ids]
    if not work:
        print("reverify: nothing is due.")
        return 0

    findings, fresh, stats = check(work, cache)
    stamped = None
    if a.apply:
        stamped = apply(work, findings, today)
        record["items"] = items
        LEDGER.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
    save_cache(fresh, today)
    return report(findings, stats, stamped)


if __name__ == "__main__":
    raise SystemExit(main())
