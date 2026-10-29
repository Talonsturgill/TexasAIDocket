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
              A url the crawl boundary refuses is reported here too, WITHOUT A REQUEST.

THE BOUNDARY IS ASKED BEFORE ANY REQUEST (2026-10-01). Until this date the script fetched every
due url without asking anything, and on September 29th, 30th and October 1st it fetched
docs.tacc.utexas.edu, a host the registry excludes whole, and public.destinyhosted.com, whose
robots.txt is `User-agent: *` / `Disallow: /` on one line, then stamped four items checked on
the strength of those refused requests. Two runs withdrew the stamps by hand and wrote the
defect up as a proposal. A url is now refused, never requested, when any of three things says so:

  1. `crawl_boundary.forbidden(url)`, the registry's own boundary, the one reader of it.
  2. the citing item's own `unreachable` block measuring a `robots` boundary on that host.
  3. the host's live robots.txt, read with its directives split apart first, because Python's
     `urllib.robotparser` reads a robots file written on a single line as allowing everything,
     which is exactly how the September 30th helper fetched the Hays County agenda. The groups
     that bind are `*`, this project's own token, `ClaudeBot` and `anthropic-ai`.

A robots.txt that answers 4xx states no rule, which is the convention every crawler follows. One
that answers 5xx or does not answer is read as refusing, because a boundary nobody could read is
not a boundary that allows.

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

That first pass left PDFs, javascript portals and consent walls for manual reading. The reader
now uses the existing document parser for PDFs with extractable text. Scanned or damaged files
remain unconfirmed. Redirect targets must pass the same source policy as the original URL,
and a conditional response retains only quote evidence already earned from readable content.

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
import os
import subprocess
import re
import sys
import urllib.error
import urllib.request
from urllib.parse import urlsplit
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "ledger" / "docket.json"
CACHE = REPO_ROOT / "ledger" / "reverify.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import docket_staleness as ds  # noqa: E402
import docket_build as dk  # noqa: E402  the numeral machinery, one definition
sys.path.insert(0, str(REPO_ROOT / "scripts" / "shared"))
import crawl_boundary  # noqa: E402  the one reader of the registry's boundary
import fetch_doc  # noqa: E402  shared redirect-safe HTTP transport

UA = ("TexasAIDocket/1.0 re-verification (+https://texasaidocket.com) "
      "one conditional request per source per two days")
TIMEOUT = 30

UNCHANGED, MISSING, UNREACHABLE, UNREADABLE = (
    "unchanged", "missing", "unreachable", "unreadable")

# A SOURCE THIS CHECK CANNOT READ IS NOT A SOURCE THAT CHANGED, and telling them apart is the
# difference between a useful report and a boy who cried wolf. The first version had one bucket
# for both and reported 92 of 314 claims as missing on its very first run against the real
# record. Almost none of them had moved. PDFs now use the shared text extractor; a damaged or
# scanned PDF and a javascript portal with no readable quote still carry no confirmation.
PDF_HINT = (".pdf",)


# --------------------------------------------------------------------------- text
_TAG = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
_ANY = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")
# A FEED, SNIFFED OFF THE PAYLOAD. The second flatten pass is right for a document that escapes
# its HTML inside an XML text node and wrong for one that displays escaped markup to a reader, so
# it is gated on this rather than run on everything. Sniffed rather than taken from a content type
# header, because a server that mislabels its feed is exactly the case this has to survive.
_FEED = re.compile(r"<\?xml\b|<(rss|feed|rdf:RDF)\b", re.I)


def _looks_like_feed(text: str) -> bool:
    """True when the first bytes look like RSS, Atom or a bare XML document."""
    return bool(_FEED.search(text[:2048]))


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

    So the strip and the unescape run twice ON A FEED, and the second pass removes the markup the
    first revealed.

    ONLY ON A FEED, and the first version of this ran the second pass on everything. Its docstring
    said the cost was "a missed match rather than a false one, which is the cheaper of the two
    errors here", and that was wrong in the direction that matters. A review bot on PR 252 named
    the case: an ordinary page that DISPLAYS escaped markup as visible content, a code sample
    reading `<strong>Project</strong> 58482`. One pass flattens it to exactly what a reader sees,
    and a claim quoting that is correctly confirmed. Two passes flatten it to `Project 58482`, so
    the reader's own quote goes MISSING and a claim quoting a string that is nowhere on the page
    gets CONFIRMED instead. The second is a false verification stamp, which is the expensive error
    and the one this file exists to prevent.

    The second pass is what a feed needs and only a feed needs, because only a feed puts its HTML
    inside an XML text node. So it is gated on the payload looking like one, sniffed off the first
    bytes rather than trusted from a header a server can get wrong.
    """
    t = raw.decode("utf-8", "replace")
    passes = 2 if _looks_like_feed(t) else 1
    for _ in range(passes):
        t = _TAG.sub(" ", t)
        t = _ANY.sub(" ", t)
        t = html.unescape(t)
    # A non-breaking space is a space to a reader and a different codepoint to `in`, and a
    # non-breaking hyphen is a hyphen. The record stores the plain one because the mono face
    # carries no U+2011 (tests/glyphs.mjs, tx-2026-0213-c3).
    t = t.replace(" ", " ").replace("‑", "-").replace("’", "'").replace("“", '"').replace("”", '"')
    return _WS.sub(" ", t).strip()


def norm_quote(q: str) -> str:
    q = q.replace(" ", " ").replace("‑", "-").replace("’", "'").replace("“", '"').replace("”", '"')
    return _WS.sub(" ", q).strip()


def claim_fingerprint(claim: dict) -> str:
    """Bind source evidence to the complete claim, including its quote and citation."""
    return hashlib.sha256(json.dumps(claim, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


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
    try:
        # The first URL's allowance does not allow a redirect to a restricted host.
        # Keep conditional requests and cache handling here, but share fetch_doc's
        # per-redirect policy check so an access challenge is never requested.
        op = opener or fetch_doc.boundary_opener(crawl_boundary.rules())
        with op(req, timeout=TIMEOUT) as r:
            body = r.read()
            meta = {"etag": r.headers.get("ETag"),
                    "last_modified": r.headers.get("Last-Modified"),
                    "hash": hashlib.sha256(body).hexdigest()}
            return UNCHANGED, body, meta
    except fetch_doc.Refused as e:
        return UNREACHABLE, None, {"status": str(e)}
    except urllib.error.HTTPError as e:
        if e.code == 304:
            # THE SERVER SAID SO, which is the cheapest and the most certain answer available.
            return UNCHANGED, None, dict(cached)
        return UNREACHABLE, None, {"status": e.code}
    except Exception as e:  # noqa: BLE001  a refusal, a timeout and a bad tls all mean the same
        return UNREACHABLE, None, {"status": type(e).__name__}


# --------------------------------------------------------------------------- the boundary
# The robots groups that bind this project. Its own token, the wildcard, and the two agent names
# the registry treats as naming this project when a host refuses them.
ROBOTS_AGENTS = ("*", "texasaidocket", "claudebot", "anthropic-ai")
_DIRECTIVE = re.compile(r"(?i)\b(user-agent|disallow|allow|crawl-delay|sitemap)\s*:")


def robots_rules(text: str) -> list[tuple[str, str]]:
    """`(kind, path)` pairs that bind this project, from a robots.txt body.

    THE DIRECTIVES ARE SPLIT APART BEFORE ANYTHING IS PARSED. A file served as one line,
    `User-agent: * Disallow: /`, is read by `urllib.robotparser` as a user agent named
    `* Disallow: /` and no rule at all, which is a refusal read as permission.
    """
    flat = _DIRECTIVE.sub(lambda m: "\n" + m.group(1) + ":", text.replace("\r", "\n"))
    groups: list[tuple[list[str], list[tuple[str, str]]]] = []
    agents: list[str] = []
    rules: list[tuple[str, str]] = []
    last_was_agent = False
    for raw in flat.split("\n"):
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        key, val = (x.strip() for x in line.split(":", 1))
        key = key.lower()
        if key == "user-agent":
            if not last_was_agent and (agents or rules):
                groups.append((agents, rules))
                agents, rules = [], []
            agents.append(val.lower())
            last_was_agent = True
        elif key in ("allow", "disallow"):
            rules.append((key, val))
            last_was_agent = False
        else:
            last_was_agent = False
    if agents or rules:
        groups.append((agents, rules))
    out: list[tuple[str, str]] = []
    for ags, rs in groups:
        if any(a == "*" or any(a.startswith(t) for t in ROBOTS_AGENTS if t != "*") for a in ags):
            out.extend(rs)
    return out


def robots_refuses(rules: list[tuple[str, str]], path: str) -> bool:
    """Longest match wins and an empty `Disallow:` refuses nothing, as RFC 9309 has it."""
    best_len, verdict = -1, False
    for kind, rule in rules:
        if not rule:
            continue
        pat = re.escape(rule).replace(r"\*", ".*")
        if pat.endswith(r"\$"):
            pat = pat[:-2] + "$"
        if re.match(pat, path, re.I) and len(rule) > best_len:
            best_len, verdict = len(rule), kind == "disallow"
    return verdict


class Boundary:
    """Asks, per url and before any request, whether this project may fetch it.

    Returns the reason as a string when it may not, and None otherwise. None carries the same
    caveat `crawl_boundary.forbidden` states: it is the absence of a refusal this code could
    read, which is all a fetcher can honestly act on.
    """

    def __init__(self, opener=None, registry=None):
        self.op = opener or urllib.request.urlopen
        self.registry = crawl_boundary.rules() if registry is None else registry
        self.robots: dict[str, list | str] = {}

    def _robots(self, scheme: str, host: str):
        key = f"{scheme}://{host}"
        if key not in self.robots:
            req = urllib.request.Request(key + "/robots.txt", headers={"User-Agent": UA})
            try:
                with self.op(req, timeout=TIMEOUT) as r:
                    body = r.read().decode("utf-8", "replace")
                self.robots[key] = robots_rules(body)
            except urllib.error.HTTPError as e:
                self.robots[key] = ([] if 400 <= e.code < 500 else
                                    f"its robots.txt answered {e.code}, so it is read as refusing")
            except Exception as e:  # noqa: BLE001
                self.robots[key] = (f"its robots.txt did not answer ({type(e).__name__}), "
                                    f"so it is read as refusing")
        return self.robots[key]

    def __call__(self, url: str, items: list) -> str | None:
        why = crawl_boundary.forbidden(url, self.registry)
        if why:
            return why
        try:
            parts = urlsplit(url)
            host = (parts.hostname or "").lower()
        except ValueError:
            return "the url can't be parsed, so it is not fetched"
        for it in items:
            block = it.get("unreachable")
            if (isinstance(block, dict) and block.get("boundary") == "robots"
                    and host in [str(h).lower() for h in (block.get("hosts") or [])]):
                return f"{host} refuses this project in robots.txt, measured {block.get('checked')}"
        rules = self._robots(parts.scheme or "https", host)
        if isinstance(rules, str):
            return f"{host}: {rules}"
        path = (parts.path or "/") + (("?" + parts.query) if parts.query else "")
        if robots_refuses(rules, path):
            return f"{host} disallows this path to this project in robots.txt"
        return None


# --------------------------------------------------------------------------- the check
def check(items: list, cache: dict, opener=None, gate=None) -> tuple[list, dict, dict]:
    """Every claim on `items`, one fetch per distinct url. Returns (findings, fresh cache, stats)."""
    by_url: dict[str, list] = {}
    for it in items:
        for c in (it.get("claims") or []):
            u = c.get("source_url")
            if u:
                by_url.setdefault(u, []).append((it, c))

    fresh, findings = dict(cache), []
    stats = {"urls": len(by_url), "claims": sum(len(v) for v in by_url.values()),
             "not_modified": 0, "fetched": 0, "unreachable": 0, "unreadable": 0,
             "refused": 0}
    gate = gate or Boundary(opener)

    for url, pairs in sorted(by_url.items()):
        prior = cache.get(url) or {}
        # NEVER REQUESTED. A refused url withholds the stamp exactly as an unreachable one does,
        # because nothing about the page was read.
        why = gate(url, [it for it, _ in pairs])
        if why:
            stats["refused"] += 1
            for it, c in pairs:
                findings.append({"item": it["id"], "claim": c["id"], "url": url,
                                 "state": UNREACHABLE,
                                 "why": f"not requested. The crawl boundary refuses it: {why}"})
            continue
        # A 304 only preserves evidence bound to the complete current claim and body.
        # Cached validators also exist for unreadable PDFs and challenge pages.
        # Ask for the body when any quote has never been located on this source.
        prior_proofs = prior.get("proofs") or {}
        proven_before = {c["id"] for _, c in pairs
                         if prior_proofs.get(c["id"]) == {
                             "claim_sha256": claim_fingerprint(c),
                             "body_sha256": prior.get("hash")}}
        request_cache = prior if all(c["id"] in proven_before for _, c in pairs) else {
            key: value for key, value in prior.items() if key not in ("etag", "last_modified")}
        state, body, meta = fetch(url, request_cache, opener)

        if state == UNREACHABLE:
            stats["unreachable"] += 1
            for it, c in pairs:
                findings.append({"item": it["id"], "claim": c["id"], "url": url,
                                 "state": UNREACHABLE, "why": str(meta.get("status"))})
            continue

        if body is None:
            # A valid conditional response retains prior proof; it creates none.
            stats["not_modified"] += 1
            fresh[url] = prior
            for it, c in pairs:
                was = c["id"] in proven_before
                findings.append({"item": it["id"], "claim": c["id"], "url": url,
                                 "state": UNCHANGED if was else UNREADABLE,
                                 "why": "304" if was else
                                 "a 304 can't confirm a quote never located on this page"})
            continue

        stats["fetched"] += 1
        proven = set(prior.get("proven") or [])
        meta["proven"] = sorted(proven)
        proofs = dict(prior_proofs)
        meta["proofs"] = proofs
        fresh[url] = meta

        if url.lower().endswith(PDF_HINT) or body[:5] == b"%PDF-":
            try:
                extracted, _, characters = fetch_doc.pdf_text(body)
                text = norm_quote(extracted) if characters else ""
            except Exception:  # damaged or scanned source is not proof of a changed claim
                text = ""
            if not text:
                stats["unreadable"] += 1
                for it, c in pairs:
                    findings.append({"item": it["id"], "claim": c["id"], "url": url,
                                     "state": UNREADABLE,
                                     "why": "the PDF yielded no readable text"})
                continue
        else:
            text = flatten(body)
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
        same = bool(prior.get("hash")) and prior["hash"] == meta["hash"]
        for it, c in pairs:
            q = norm_quote(c.get("verbatim_quote") or "")
            fingerprint = claim_fingerprint(c)
            was = (prior_proofs.get(c["id"]) or {}).get("claim_sha256") == fingerprint
            current = c["id"] in proven_before
            found = bool(q) and ((same and current) or q in text)
            if found:
                proven.add(c["id"])
                proofs[c["id"]] = {"claim_sha256": fingerprint,
                                   "body_sha256": meta["hash"]}
                findings.append({"item": it["id"], "claim": c["id"], "url": url,
                                 "state": UNCHANGED,
                                 "why": "hash" if (same and current) else "quote"})
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
          f"{stats['unreachable']} did not answer, {stats.get('refused', 0)} refused by the "
          f"crawl boundary and never requested.")
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
def _note_numbers(item: dict, entry: dict) -> set[str]:
    """The existing numeric allowance, evaluated against one item snapshot."""
    when = ds.parse_date(entry.get("date"))
    return set(dk._quoted_numerals(item)) | set(dk._prose_numerals(movement_line(item, when)))


class HistoricalNoteProof:
    """Replay unchanged published history against its original canonical introduction.

    This proves publication provenance, not the truth of a withdrawn claim. GitHub event
    boundaries identify approved history; local use verifies the fetched main against origin.
    """
    def __init__(self, repo: Path = REPO_ROOT):
        self.repo, self.ref, self.main = repo, None, {}
        self.records, self.proofs, self.targets = {}, {}, set()
        self.scanned = False
        try:
            remote = self.git("remote", "get-url", "origin").removesuffix(".git")
            if remote not in ("https://github.com/Talonsturgill/TexasAIDocket",
                              "git@github.com:Talonsturgill/TexasAIDocket"):
                return
            if self.git("rev-parse", "--is-shallow-repository") != "false":
                return
            main = self.git("rev-parse", "refs/remotes/origin/main")
            if os.environ.get("GITHUB_ACTIONS") == "true":
                if os.environ.get("GITHUB_REPOSITORY") != "Talonsturgill/TexasAIDocket":
                    return
                event_path = os.environ.get("GITHUB_EVENT_PATH")
                event = json.loads(Path(event_path).read_text()) if event_path else {}
                if (event.get("repository") or {}).get("full_name") != "Talonsturgill/TexasAIDocket":
                    return
                event_name = os.environ.get("GITHUB_EVENT_NAME")
                if event_name == "pull_request":
                    base = (event.get("pull_request") or {}).get("base") or {}
                    if (base.get("repo") or {}).get("full_name") != "Talonsturgill/TexasAIDocket" or base.get("ref") != "main":
                        return
                    ref = base.get("sha")
                elif event_name == "push" and event.get("ref") == "refs/heads/main":
                    ref = event.get("before")
                elif event_name == "workflow_dispatch" and os.environ.get("GITHUB_REF") == "refs/heads/main":
                    ref = os.environ.get("GITHUB_SHA")
                else:
                    return
            else:
                ref = self.remote_main()
                if ref != main:
                    return
            if not isinstance(ref, str) or not re.fullmatch(r"[0-9a-f]{40}", ref):
                return
            self.git("merge-base", "--is-ancestor", ref, main)
            self.ref = ref
            body = json.loads(self.git("show", ref + ":ledger/docket.json"))
            self.main = {item["id"]: item for item in body["items"]}
        except (OSError, ValueError, subprocess.SubprocessError):
            self.ref = None

    def git(self, *args: str) -> str:
        return subprocess.check_output(["git", *args], cwd=self.repo, text=True,
                                       stderr=subprocess.DEVNULL, timeout=30).strip()

    def remote_main(self) -> str:
        rows = self.git("ls-remote", "origin", "refs/heads/main").splitlines()
        return rows[0].split()[0] if len(rows) == 1 else ""

    def prefix_problem(self, item: dict) -> str | None:
        if not self.ref:
            return "canonical published history could not be established"
        if item["id"] not in self.main:
            return None
        published = self.main[item["id"]].get("history", [])
        if item.get("history", [])[:len(published)] != published:
            return "published history must remain an exact unchanged prefix"
        return None

    def scan(self) -> None:
        """One structurally complete first-parent traversal for all requested entries."""
        if self.scanned or not self.ref:
            return
        self.scanned = True
        pending = set(self.targets)
        ids = {key[0] for key in pending}
        try:
            commits = self.git("log", "--first-parent", "--reverse", "--format=%H",
                               self.ref, "--", "ledger/docket.json").splitlines()
            for sha in commits:
                body = json.loads(self.git("show", sha + ":ledger/docket.json"))
                # Cache only the relevant item snapshots, not every full ledger version.
                record = {item["id"]: item for item in body["items"] if item["id"] in ids}
                self.records[sha] = record
                for key in list(pending):
                    iid, index = key
                    snapshot = record.get(iid, {})
                    prefix = self.main[iid].get("history", [])[:index + 1]
                    if snapshot.get("history", [])[:index + 1] != prefix:
                        continue
                    # This is its first structural appearance. A failed proof cannot be
                    # laundered through a later deletion and reintroduction of the note.
                    pending.remove(key)
                    self.proofs[key] = None
                    entry = prefix[-1]
                    if set(dk._prose_numerals(str(entry.get("note", "")))) <= _note_numbers(snapshot, entry):
                        self.proofs[key] = {"commit": sha,
                                            "blob": self.git("rev-parse", sha + ":ledger/docket.json")}
                if not pending:
                    break
        except (OSError, ValueError, KeyError, subprocess.SubprocessError):
            return

    def prove(self, item: dict, index: int) -> dict | None:
        if self.prefix_problem(item) or index >= len(self.main.get(item["id"], {}).get("history", [])):
            return None
        self.scan()
        return self.proofs.get((item["id"], index))


def check_notes(items: list, *, historical=None, diagnostics: list | None = None) -> list:
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
    An unchanged published note may instead replay that same rule against its original
    canonical-main introduction snapshot. Corrections do not rewrite historical publication.
    """
    bad = []
    archive = historical or HistoricalNoteProof()
    pending = []
    for it in items:
        prefix_problem = archive.prefix_problem(it)
        if prefix_problem:
            bad.append(f'{it["id"]}: {prefix_problem}')
        allowed = set(dk._quoted_numerals(it))
        for index, h in enumerate(it.get("history") or []):
            if not isinstance(h, dict) or not h.get("checked"):
                continue
            try:
                when = ds.parse_date(h.get("date"))
            except Exception:
                bad.append(f'{it["id"]}: a checked note carries no readable date')
                continue
            base = set(dk._prose_numerals(movement_line(it, when)))
            missing = [got for got in dk._prose_numerals(str(h.get("note") or ""))
                       if got not in base and got not in allowed]
            if missing:
                pending.append((it, index, h, missing))
    archive.targets.update((it["id"], index) for it, index, _, _ in pending
                           if it["id"] in archive.main
                           and index < len(archive.main[it["id"]].get("history", [])))
    for it, index, h, missing in pending:
        proof = archive.prove(it, index)
        if proof:
            if diagnostics is not None:
                diagnostics.append({"item": it["id"], "ordinal": index, "date": h["date"], **proof})
            continue
        for got in missing:
            bad.append(f'{it["id"]} {h["date"]}: the note states "{got}", which is in no claim '
                       f"quote and in nothing this check established. Re-wording may not add a figure")
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
                           "proven records which claim quotes have been located here. Each "
                           "proof binds the complete claim digest to the body hash that "
                           "contained its quote; legacy entries require a new body."},
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
            v = pages.get(req.full_url, 404)
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

    # AND AN ORDINARY PAGE THAT SHOWS ESCAPED MARKUP TO A READER KEEPS IT (2026-09-03, PR 252).
    # The second pass is right for a feed and wrong here. Run on everything it deleted text a
    # reader can see AND confirmed a quote that is nowhere on the page, which is a false
    # verification stamp rather than a missed one.
    # IT CARRIES ITS OWN NAME rather than rebinding `page`. Written as `page` it silently
    # replaced the shared fixture every later case reads, and eleven cases below then ran
    # against a page that does not carry `quote` at all. The suite crashed on the first one
    # that indexed a key an unstamped item never grows, which is luck rather than a check.
    shown = (b"<html><body><p>The docket line reads "
             b"&lt;strong&gt;Project&lt;/strong&gt; 58482 in the source.</p></body></html>")
    ok("escaped markup a READER SEES survives on an ordinary page",
       "<strong>Project</strong> 58482" in flatten(shown), flatten(shown))
    ok("...and the stripped form, which is on no page, is NOT confirmed",
       "Project 58482" not in flatten(shown), flatten(shown))
    ok("a feed is told from a page by its own first bytes, not by a header",
       _looks_like_feed(feed.decode()) and not _looks_like_feed(shown.decode()))
    ok("...and the shared fixture still carries the quote the later cases look for",
       quote in flatten(page), flatten(page))

    print("\nand each outcome is told apart from the others")
    # AUTHORITY IS EARNED. With no record of ever having found this quote here, the honest
    # answer is that the check has no opinion, not that the world moved.
    gone = item("tx-2", "https://b/", "a line that is not there")
    f, _, _ = check([gone], {}, server({"https://b/": page}))
    ok("a quote never seen here is UNREADABLE, not MISSING",
       f[0]["state"] == UNREADABLE, str(f))
    f, fresh2, _ = check([gone], {"https://b/": {"proven": ["tx-2-c1"], "hash": "previous",
                         "proofs": {"tx-2-c1": {"claim_sha256": claim_fingerprint(gone["claims"][0]),
                                                 "body_sha256": "previous"}}}},
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
    pri2["https://k/"]["proofs"] = {"tx-2y-c1": {
        "claim_sha256": claim_fingerprint(present["claims"][0]),
        "body_sha256": pri2["https://k/"]["hash"]}}
    f, _, _ = check([present], pri2, server({"https://k/": page}))
    ok("...while a proven claim still short circuits on the hash",
       f[0]["state"] == UNCHANGED and f[0]["why"] == "hash", str(f))

    print("\nPDF text is checked; unreadable files never confirm or erase a claim")
    f, _, st = check([item("tx-2c", "https://x/f.pdf", quote)], {},
                     server({"https://x/f.pdf": b"%PDF-1.7 binary"}))
    ok("a PDF is UNREADABLE", f[0]["state"] == UNREADABLE, str(f))
    ok("...counted as unreadable rather than fetched-and-changed", st["unreadable"] == 1, str(st))
    f, _, _ = check([item("tx-2d", "https://x/nosuffix", quote)], {},
                    server({"https://x/nosuffix": b"%PDF-1.7 binary"}))
    ok("...detected by its bytes when the url does not say pdf",
       f[0]["state"] == UNREADABLE, str(f))
    pdf_item = item("tx-pdf", "https://x/document.pdf", quote)
    pdf_body = fetch_doc._tiny_pdf(quote)
    f, pdf_cache, _ = check([pdf_item], {}, server({"https://x/document.pdf": pdf_body}))
    ok("an extracted PDF quote is confirmed and recorded as proven",
       f[0]["state"] == UNCHANGED and f[0]["why"] == "quote"
       and pdf_item["claims"][0]["id"] in pdf_cache["https://x/document.pdf"]["proven"], str(f))
    f, _, _ = check([pdf_item], pdf_cache,
                    server({"https://x/document.pdf": fetch_doc._tiny_pdf("A different statement.")}))
    ok("a previously proven PDF quote that disappears is a real change",
       f[0]["state"] == MISSING, str(f))
    f, _, _ = check([pdf_item], pdf_cache,
                    server({"https://x/document.pdf": fetch_doc._tiny_pdf("")}))
    ok("a PDF without extractable text withholds the stamp without claiming a change",
       f[0]["state"] == UNREADABLE and apply([pdf_item], f, today) == [], str(f))
    f, _, _ = check([item("tx-3", "https://c/", quote)], {}, server({"https://c/": 404}))
    ok("a 404 is UNREACHABLE and never unchanged", f[0]["state"] == UNREACHABLE, str(f))
    unchanged_item = item("tx-4", "https://d/", quote)
    f, _, st = check([unchanged_item],
                     {"https://d/": {"etag": '"e1"', "hash": "previous", "proven": ["tx-4-c1"],
                      "proofs": {"tx-4-c1": {"claim_sha256": claim_fingerprint(unchanged_item["claims"][0]),
                                              "body_sha256": "previous"}}}},
                     server({"https://d/": 304}))
    ok("a 304 is unchanged and reads no body", f[0]["state"] == UNCHANGED and st["fetched"] == 0,
       str(st))
    unproven = item("tx-unproven-304", "https://d/", quote)
    f, _, _ = check([unproven], {"https://d/": {"etag": '"e1"'}},
                    server({"https://d/": 304}))
    ok("an unsolicited 304 never proves an unlocated quote or stamps its item",
       f[0]["state"] == UNREADABLE and apply([unproven], f, today) == [], str(f))
    sent_headers = []

    def body_for_unproven(req, timeout=None):
        sent_headers.append(dict(req.header_items()))
        return server({"https://d/": page})(req, timeout)

    f, _, _ = check([unproven], {"https://d/": {"etag": '"e1"', "last_modified": "old"}},
                    body_for_unproven, gate=lambda url, items: None)
    ok("an unlocated quote requests a body without validators and earns actual proof",
       f[0]["state"] == UNCHANGED and f[0]["why"] == "quote"
       and "If-none-match" not in sent_headers[0]
       and "If-modified-since" not in sent_headers[0], str(sent_headers))

    # Reusing an ID does not reuse evidence for a different claim or quote.
    for field, value in (("text", "Revised claim text"), ("verbatim_quote", "An absent quote"),
                         ("source_title", "Revised title"), ("fetched", "2026-08-26"),
                         ("source_url", "https://changed.example/")):
        changed = json.loads(json.dumps(present))
        changed["claims"][0][field] = value
        f, _, _ = check([changed], pri2, server({changed["claims"][0]["source_url"]: 304}),
                        gate=lambda url, items: None)
        ok(f"same-ID edit to {field} invalidates a conditional proof",
           f[0]["state"] == UNREADABLE and apply([changed], f, today) == [], str(f))
    f, _, _ = check([gone], fresh2, server({"https://b/": 304}),
                    gate=lambda url, items: None)
    ok("a 304 cannot revive a quote absent from the cached body",
       f[0]["state"] == UNREADABLE and apply([gone], f, today) == [], str(f))
    f, _, _ = check([present], {"https://k/": {"etag": '"old"', "hash": pri2["https://k/"]["hash"],
                                               "proven": ["tx-2y-c1"]}},
                    server({"https://k/": 304}), gate=lambda url, items: None)
    ok("legacy ID-only cache entries cannot authorize a verification stamp",
       f[0]["state"] == UNREADABLE, str(f))

    print("\none fetch per url, however many claims sit behind it")
    two = {"id": "tx-5", "status": "open", "claims": [
        {"id": "tx-5-c1", "verbatim_quote": quote, "source_url": "https://e/"},
        {"id": "tx-5-c2", "verbatim_quote": "y", "source_url": "https://e/"}]}
    hits = []

    def counting(req, timeout=None):
        hits.append(req.full_url)
        return Resp(page, {"ETag": '"e1"'})
    f, _, st = check([two], {}, counting)
    # The host's robots.txt is asked once as well, since 2026-10-01, and is not the page.
    pages_hit = [h for h in hits if not h.endswith("/robots.txt")]
    ok("two claims on one url are one request", len(pages_hit) == 1 and st["claims"] == 2,
       str(hits))
    ok("...and the host's robots.txt is asked once", hits.count("https://e/robots.txt") == 1,
       str(hits))

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

    # THE BOUNDARY, ASKED BEFORE ANY REQUEST (2026-10-01). Each case replays a real refused
    # fetch that stamped an item: docs.tacc.utexas.edu (registry, whole host) and
    # public.destinyhosted.com (a one line robots.txt), on September 29th, 30th and October 1st.
    print("\na url the boundary refuses is never requested and never stamped")
    asked: list[str] = []

    def spy(pages):
        inner = server(pages)

        def op(req, timeout=None):
            asked.append(req.full_url)
            return inner(req, timeout)
        return op

    one_line = b"User-agent: * Disallow: /"
    ok("a robots.txt on one line is read as refusing every path",
       robots_refuses(robots_rules(one_line.decode()), "/agenda_publish.cfm"),
       str(robots_rules(one_line.decode())))
    ok("...where urllib.robotparser would have read it as allowing",
       robots_rules("User-agent: *\nDisallow:") == [("disallow", "")]
       and not robots_refuses(robots_rules("User-agent: *\nDisallow:"), "/x"))
    named = "User-agent: Googlebot\nAllow: /\n\nUser-agent: ClaudeBot\nDisallow: /\n"
    ok("a ClaudeBot disallow binds this project", robots_refuses(robots_rules(named), "/a"))
    ok("a group for another crawler does not",
       not robots_refuses(robots_rules("User-agent: Googlebot\nDisallow: /\n"), "/a"))
    ok("the longest rule wins",
       not robots_refuses(robots_rules("User-agent: *\nDisallow: /p\nAllow: /p/ok\n"), "/p/ok/1"))

    asked.clear()
    agenda = "https://public.destinyhosted.com/agenda_publish.cfm?id=1"
    hays = item("tx-h", agenda, quote, status="decided")
    f3, _, st3 = check([hays], {}, spy({
        "https://public.destinyhosted.com/robots.txt": one_line, agenda: page}))
    ok("the refused page is not requested", agenda not in asked, str(asked))
    ok("...it is reported unreachable, so the stamp is withheld",
       [x["state"] for x in f3] == [UNREACHABLE] and apply([hays], f3, today) == [], str(f3))
    ok("...and counted as refused", st3.get("refused") == 1, str(st3))

    asked.clear()
    tacc = "https://docs.tacc.utexas.edu/hpc/frontera/"
    fr = item("tx-t", tacc, quote, status="decided")
    f4, _, _ = check([fr], {}, spy({tacc: page}))
    ok("a host the registry excludes is never requested, robots.txt included",
       not any("tacc.utexas.edu" in u for u in asked), str(asked))
    ok("...and the item is not stamped", apply([fr], f4, today) == [], str(f4))

    asked.clear()
    measured = item("tx-m", "https://m.example/a", quote)
    measured["unreachable"] = {"hosts": ["m.example"], "boundary": "robots",
                               "checked": "2026-09-28"}
    f5, _, _ = check([measured], {}, spy({"https://m.example/a": page}))
    ok("an item's own measured robots boundary refuses the request",
       "https://m.example/a" not in asked and f5[0]["state"] == UNREACHABLE, str(f5))

    asked.clear()
    f6, _, _ = check([item("tx-5xx", "https://s.example/a", quote)], {},
                     spy({"https://s.example/robots.txt": 503, "https://s.example/a": page}))
    ok("a robots.txt that answers 5xx is read as refusing",
       "https://s.example/a" not in asked and f6[0]["state"] == UNREACHABLE, str(f6))
    f7, _, _ = check([item("tx-404", "https://n.example/a", quote)], {},
                     server({"https://n.example/a": page}))
    ok("a robots.txt that answers 404 states no rule, and the page is read",
       f7[0]["state"] == UNCHANGED, str(f7))

    print("\nredirects obey the same source policy without changing cache semantics")
    import io
    from email.message import Message
    from unittest.mock import patch
    from urllib.response import addinfourl

    redirect_hits, redirect_pages = [], {}

    class RedirectFixture(urllib.request.HTTPSHandler):
        def https_open(self, req):
            redirect_hits.append((req.full_url, dict(req.header_items())))
            code, headers, payload = redirect_pages[req.full_url]
            message = Message()
            for key, value in headers.items():
                message[key] = value
            response = addinfourl(io.BytesIO(payload), message, req.full_url, code)
            response.msg = "fixture"
            return response

    build_opener = urllib.request.build_opener
    source, target = "https://source.example/notice", "https://target.example/notice"
    redirect_pages[source] = (302, {"Location": target}, b"")
    redirect_pages[target] = (200, {"ETag": '"new"'}, page)
    candidate = item("tx-redirect", source, quote)
    prior = {source: {"etag": '"old"', "last_modified": "Tue, 20 Oct 2026 00:00:00 GMT",
                      "hash": "original", "proven": ["tx-redirect-c1"]}}
    prior[source]["proofs"] = {"tx-redirect-c1": {
        "claim_sha256": claim_fingerprint(candidate["claims"][0]), "body_sha256": "original"}}
    with patch.object(urllib.request, "build_opener",
                      side_effect=lambda *handlers: build_opener(*handlers, RedirectFixture())), \
            patch.object(fetch_doc, "robots_refusal", return_value="robots refuses target"):
        refused, retained, _ = check([candidate], prior, gate=lambda url, items: None)
    ok("a refused redirect is never requested or confirmed",
       [url for url, _ in redirect_hits] == [source]
       and refused[0]["state"] == UNREACHABLE
       and "robots refuses target" in refused[0]["why"], str(refused))
    ok("a refused redirect preserves the cache and withholds the item stamp",
       retained == prior and apply([candidate], refused, today) == [])

    redirect_hits.clear()
    with patch.object(urllib.request, "build_opener",
                      side_effect=lambda *handlers: build_opener(*handlers, RedirectFixture())), \
            patch.object(fetch_doc, "robots_refusal", return_value=None):
        allowed, updated, _ = check([candidate], prior, gate=lambda url, items: None)
    ok("an allowed redirect still verifies the actual quote and its provenance",
       allowed[0]["state"] == UNCHANGED and allowed[0]["why"] == "quote"
       and updated[source]["etag"] == '"new"'
       and "tx-redirect-c1" in updated[source]["proven"], str(allowed))
    ok("conditional headers survive an allowed redirect",
       len(redirect_hits) == 2 and all(headers.get("If-none-match") == '"old"'
                                     and headers.get("If-modified-since") == prior[source]["last_modified"]
                                     for _, headers in redirect_hits), str(redirect_hits))

    redirect_pages[target] = (304, {}, b"")
    with patch.object(urllib.request, "build_opener",
                      side_effect=lambda *handlers: build_opener(*handlers, RedirectFixture())), \
            patch.object(fetch_doc, "robots_refusal", return_value=None):
        unchanged, retained, statistics = check([candidate], prior, gate=lambda url, items: None)
    ok("a 304 after an allowed redirect retains the original cache without a body",
       unchanged[0]["state"] == UNCHANGED and unchanged[0]["why"] == "304"
       and retained == prior and statistics["not_modified"] == 1, str(unchanged))

    print("\nhistorical corrections retain proof without licensing new figures")
    import tempfile
    import copy
    with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {"GITHUB_ACTIONS": ""}), \
            patch.object(HistoricalNoteProof, "remote_main", lambda self: self.git("rev-parse", "refs/remotes/origin/main")):
        repo = Path(td)
        def git(*args):
            return subprocess.check_output(["git", *args], cwd=repo, text=True,
                                           stderr=subprocess.DEVNULL).strip()
        git("init", "-q")
        git("config", "user.name", "Fixture")
        git("config", "user.email", "fixture@example.invalid")
        git("remote", "add", "origin", "https://github.com/Talonsturgill/TexasAIDocket.git")
        (repo / "ledger").mkdir()
        original = noted("The line is 765 kV.", "A 765 kV line.")
        original["history"].insert(0, {"date": "2026-08-24", "note": "The record was admitted."})
        def commit_record(record, message):
            (repo / "ledger/docket.json").write_text(json.dumps({"items": record if isinstance(record, list) else [record]}))
            git("add", "ledger/docket.json")
            git("commit", "-qm", message)
            return git("rev-parse", "HEAD")
        introduced = commit_record(original, "Publish verified note")
        git("update-ref", "refs/remotes/origin/main", introduced)
        corrected = copy.deepcopy(original)
        corrected["claims"][0]["verbatim_quote"] = "A transmission line."
        corrected["history"].append({"date": "2026-08-26", "note": "Correction. The earlier figure is withdrawn."})
        proof_reader = HistoricalNoteProof(repo)
        receipts = []
        ok("an exact published note replays against its introducing source snapshot",
           not check_notes([corrected], historical=proof_reader, diagnostics=receipts)
           and receipts[0]["commit"] == introduced, str(receipts))
        for label, mutate in (
                ("changed note", lambda x: x["history"][1].update(note="The line is 999 kV.")),
                ("duplicate old note", lambda x: x["history"].append(copy.deepcopy(original["history"][1]))),
                ("deleted prefix", lambda x: x["history"].pop(0)),
                ("deleted only checked note", lambda x: x["history"].pop(1)),
                ("cleared checked marker", lambda x: x["history"][1].pop("checked")),
                ("reordered prefix", lambda x: x["history"].reverse())):
            candidate = copy.deepcopy(corrected)
            mutate(candidate)
            ok(label + " cannot use historical proof", bool(check_notes([candidate], historical=proof_reader)))
        candidate_sha = commit_record(corrected, "Correct current source")
        # A subsequent main baseline no longer quotes the figure. Its original introduction does.
        git("update-ref", "refs/remotes/origin/main", candidate_sha)
        ok("the next merged baseline still uses the original introduction",
           not check_notes([corrected], historical=HistoricalNoteProof(repo)))
        fake = copy.deepcopy(corrected)
        fake["history"].append({"date": "2026-08-27", "note": "Checked 999 filings.", "checked": True})
        commit_record(fake, "Unmerged candidate note")
        ok("a candidate-only commit and new figure are not publication evidence",
           bool(check_notes([fake], historical=HistoricalNoteProof(repo))))
        approved = candidate_sha
        forged = git("rev-parse", "HEAD")
        git("update-ref", "refs/remotes/origin/main", forged)
        with patch.object(HistoricalNoteProof, "remote_main", return_value=approved):
            ok("a locally relabeled candidate is not the actual remote main",
               bool(check_notes([corrected], historical=HistoricalNoteProof(repo))))
        # Same global note count, but a different item's first structural appearance.
        moved_from = copy.deepcopy(original)
        moved_from["id"] = "tx-source"
        commit_record(moved_from, "Publish source item")
        moved_to = copy.deepcopy(original)
        moved_to["id"] = "tx-target"
        moved_from["history"] = []
        moved_sha = commit_record([moved_from, moved_to], "Move exact note between items")
        git("update-ref", "refs/remotes/origin/main", moved_sha)
        moved_to["claims"][0]["verbatim_quote"] = "A transmission line."
        ok("item-specific discovery finds a note moved without a global count change",
           not check_notes([moved_to], historical=HistoricalNoteProof(repo)))
        # The first publication is invalid; a later removal and reintroduction cannot fix it.
        invalid = copy.deepcopy(original)
        invalid["id"] = "tx-invalid"
        invalid["claims"][0]["verbatim_quote"] = "A transmission line."
        commit_record(invalid, "Publish unsupported historical figure")
        removed = copy.deepcopy(invalid)
        removed["history"].pop()
        commit_record(removed, "Remove invalid note")
        supported_later = copy.deepcopy(invalid)
        supported_later["claims"][0]["verbatim_quote"] = "A 765 kV line."
        commit_record(supported_later, "Reintroduce note with later numeric support")
        latest = commit_record(invalid, "Correct later active claim")
        git("update-ref", "refs/remotes/origin/main", latest)
        ok("a later supported reintroduction cannot launder a failed original note",
           bool(check_notes([invalid], historical=HistoricalNoteProof(repo))))
        git("remote", "set-url", "origin", "https://github.com/other/repository.git")
        ok("a noncanonical origin cannot authorize historical proof",
           bool(check_notes([corrected], historical=HistoricalNoteProof(repo))))

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
        historical_proofs = []
        bad = check_notes(items, diagnostics=historical_proofs)
        for proof in historical_proofs:
            print("reverify: historical note provenance " + json.dumps(proof, sort_keys=True))
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
        LEDGER.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n",
                          encoding="utf-8")
    save_cache(fresh, today)
    return report(findings, stats, stamped)


if __name__ == "__main__":
    raise SystemExit(main())
