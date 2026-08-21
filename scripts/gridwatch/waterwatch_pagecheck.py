#!/usr/bin/env python3
"""waterwatch_pagecheck.py — the daily once over of the published Water Watch page.

WHY THIS EXISTS, AND WHY IT IS A SEPARATE FILE FROM ITS SIBLING

The grid watch has had `gridwatch_pagecheck.py` since it shipped. The water watch had nothing,
and it is the same shape of thing: a cron writes a file, a builder renders it, and neither of
them would ever notice the page going wrong. The August 16th run recorded the absence as a
proposal because `scripts/gridwatch/` is not the daily routine's lane to write.

Two instruments, two checks, and they are NOT merged into one parameterised checker. The
promises differ. The grid watch promises never to publish a reliability verdict and that its
gauge is a bar. The water watch promises those and three more that have no grid equivalent:
percent full is computed from storage over capacity rather than read from the feed's own field,
a metro with no line is a gap in the source's tagging rather than a dry city, and out of state
reservoirs are excluded rather than counted. A shared checker would have to grow a flag per
promise, and the flags would be where the promises quietly stopped being checked.

WHO RUNS THIS, AND THE ONE THING IT IS ALLOWED TO FAIL OVER

The daily routine runs it once per run, read only. CI runs it on every pull request and on every
push to `main`, which includes the collector's own twice daily push, so this is the check that
sees a reading land.

    EXIT 0  the page is current and holds its promises
    EXIT 2  something wants attention. ADVISORY, and CI turns it into a warning
    EXIT 3  an instrument has STOPPED. Halting, and CI fails on it
    EXIT 1  reserved for this script itself being broken, and nothing else

TWO SEVERITIES, BECAUSE THEY WERE ONE AND THAT WAS A HOLE. Everything here reported 2 and CI
turned 2 into a `::warning::` and passed, on the stated reasoning that an instrument must never
fail a build over presentation. That reasoning is right about a sentence that drifted. It is
wrong about a collector that died, and until 2026-08-21 the two shared a code, so a dead water
collector produced a warning from the cron and a warning from this check and BOTH JOBS WENT
GREEN. The record could stop growing entirely and nothing would say so, on a site whose own
documentation calls a missed day the one irreversible failure it has.

So a page reading wrong stays advisory and an instrument that has stopped now fails. The
original reasoning survives intact: exit 2 still cannot cost a day's carousel over a stale
chart, and the routine still treats every finding as advisory, because the routine cannot fix a
collector and stopping it would only cost the deck as well. CI is where a 3 is a red.

The inverse still matters as much: a bad run never stops the check, because the check reads the
PUBLISHED site rather than anything the run produced.

WHAT THE ROUTINE MAY DO ABOUT WHAT IT FINDS

Presentation only, in `scripts/site/waterwatch_page.py`, which `ownership.yaml` names one by one
rather than by glob. It may NOT touch the collector or the ledgers. `ledger/gridwatch/water.jsonl`
is append-only and a reading nobody collected is gone.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "site"))

PAGE = REPO_ROOT / "docs" / "water" / "index.html"
READINGS = REPO_ROOT / "ledger" / "gridwatch" / "water.jsonl"

# The water collector files one reading a day. One day behind is the healthy steady state, so
# the threshold matches the grid watch's for the same reason: a single missed slot is invisible
# and two days dark is a broken collector rather than a bad morning.
STALE_DAYS = 2

# The verdict vocabulary. The water page's own words are "a low bar is not a conclusion about a
# city's supply and a full bar is not a promise", so these are the words that would break it.
# `drought` is deliberately ABSENT: there is a drought monitor collector beside this one and the
# page may legitimately name what that source publishes. A verdict is this project grading the
# supply, never a fetched classification being reported.
VERDICTS = ("running dry", "running out", "shortage", "crisis", "critically low",
            "safe", "plenty", "no risk", "will run out", "at risk")


def load(path: Path = READINGS) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


MAIN = re.compile(r"<main\b[^>]*>(.*)</main>", re.DOTALL | re.IGNORECASE)


def _main_of(page_html: str) -> str | None:
    """The reader facing body, separated from the shell around it.

    Returns None when there is no main element, which is a finding in its own right rather than
    a reason to check nothing.
    """
    m = MAIN.search(page_html)
    return m.group(1) if m else None


# THE COPY A PERSON READS, which is a smaller thing than the document that carries it.
CODE = re.compile(r"<(script|style)\b.*?</\1>", re.DOTALL | re.IGNORECASE)
# The head is published copy too. A verdict in the sentence that represents this page in a
# search result or a shared link is still a verdict, and more people read that sentence than
# read the page, so it is scanned with the body rather than left out of the rule.
HEAD = re.compile(r"<head\b[^>]*>(.*?)</head>", re.DOTALL | re.IGNORECASE)
HEAD_COPY = re.compile(
    r"<title\b[^>]*>(?P<title>.*?)</title>"
    r'|<meta\b[^>]*\bname="description"[^>]*\bcontent="(?P<desc>[^"]*)"',
    re.DOTALL | re.IGNORECASE)


def _reader_copy(page_html: str, main: str) -> str:
    """Everything on this page a person actually reads, lowercased, and nothing else.

    WHY THE VERDICT SCAN NEEDED ITS OWN VIEW OF THE PAGE.

    It read `page_html.lower()`, the whole document, two lines after `findings` had carefully
    separated `main` from the chrome around it. So it matched the "safe" inside
    `style-src-attr 'unsafe-inline'` in the content security policy meta tag, and reported
    **supply verdict language on the one page whose entire promise is that it publishes no
    verdict**. Every run, on a correct page.

    It is advisory and never blocks, which made it worse rather than better. A finding that is
    always there and always wrong is how a reader learns to skim past the one that is real. The
    same argument this repo makes about a liveness check that cries wolf about a deploy in
    flight.

    IT WENT UNCAUGHT BECAUSE THE FIXTURE WAS NOT THE PAGE. `shell()` says in its own docstring
    that wrapping the test bodies in real chrome is what proves the check reads copy and not
    chrome, and its chrome had no policy meta in it. So the one piece of chrome that breaks the
    rule was the one piece the fixture left out. It is in there now.

    Script and style come out for the same reason they come out of `numeral_lint` and
    `house_style_check`. A stylesheet is not prose, and the water page carries its drawings'
    stylesheet inline, so leaving it in would put several kilobytes of CSS in front of a scan
    looking for English words.
    """
    parts = [CODE.sub(" ", main or "")]
    # SCOPED TO `<head>`, NOT SEARCHED ACROSS THE DOCUMENT. `<title>` is also an SVG element,
    # where it is the accessible name of a shape and the thing a browser shows on hover, and
    # the water map carries one per reservoir. Pointed at the whole page this pulled a hundred
    # and nineteen lake tooltips into a scan looking for English verdicts. The page title lives
    # in the head, so that is where it is read from.
    head = HEAD.search(page_html)
    if head:
        for m in HEAD_COPY.finditer(head.group(1)):
            parts.append(m.group("title") or m.group("desc") or "")
    return " ".join(parts).lower()


def _fmt(iso: str) -> str:
    d = _dt.date.fromisoformat(iso)
    suf = "th" if 11 <= d.day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d.day % 10, "th")
    return f"{d:%B} {d.day}{suf}, {d.year}"


def findings(page_html: str, records: list, today: str,
             halting: list | None = None) -> list[str]:
    """Everything wrong with the published page, in the order a reader would meet it.

    `halting` COLLECTS THE SUBSET THAT MEANS AN INSTRUMENT HAS STOPPED, and it exists because
    this check was advisory in CI for every finding it could make.

    That was right for most of them and badly wrong for a few. The workflow turns exit 2 into a
    `::warning::` and passes, on the stated reasoning that an instrument must never fail a build
    over presentation. True of a sentence that drifted. NOT true of a collector that died: a dead
    water collector produced a warning from the cron and a warning from this check, and both jobs
    went green. The record could stop growing entirely and nothing would say so, on a site whose
    own documentation calls a missed day the one irreversible failure it has.

    So the two severities stop sharing one exit code. A page reading wrong stays advisory. An
    instrument that has stopped, or a site that is no longer being rebuilt, fails.

    WHAT IS DELIBERATELY NOT HALTING. A gap in the series and an unverified day already in the
    record are permanent, because TWDB keeps no archive to backfill from. Failing on those would
    make the build red forever with no action that could clear it, which is the trap this repo
    already knows: a check that is always red is a check somebody turns off. They stay findings.

    Filled through a parameter rather than returned separately so there is ONE implementation of
    each rule. Two functions computing staleness is two places for it to drift.
    """
    import waterwatch_page as wp

    out: list[str] = []
    halt = halting if halting is not None else []

    def stop(msg: str) -> None:
        """A finding that means something has stopped rather than read wrong."""
        out.append(msg)
        halt.append(msg)

    if not page_html.strip():
        stop("the published water watch page is missing or empty")
        return out

    if not records:
        stop("the record holds no readings at all; the collector has never succeeded")
        return out

    dates = [r["date"] for r in records if r.get("date")]
    last = max(dates)

    # STALENESS IS MEASURED ON THE NEWEST VERIFIED READING, and it was measured on the newest
    # record of any kind. The page publishes only verified days, deliberately: an unverified
    # record is the collector saying it fetched and could not trust what came back, and the
    # builder renders no figure from one.
    #
    # So the old rule asked whether the collector was RUNNING and called that the instrument
    # working. A collector that runs every day and writes unverified every day passed it
    # forever, while the page froze on the last day that verified. That is the exact failure
    # `queue_findings` was written for one series over, and neither daily series was checking
    # it. It also put this rule at odds with the site rule at the bottom of this function,
    # which compares against the newest reading the page is ALLOWED to show.
    ok_dates = [r["date"] for r in records if r.get("verified") and r.get("date")]
    if not ok_dates:
        stop("the record holds no verified reading at all; every day the collector has written "
             "is a fetch it could not trust, and the page has nothing it may publish")
        return out
    last_ok = max(ok_dates)
    behind = (_dt.date.fromisoformat(today) - _dt.date.fromisoformat(last_ok)).days
    if behind > STALE_DAYS:
        stop(f"the newest verified reading is {last_ok}, which is {behind} days back; "
             + (f"the collector is still writing ({last}) and no longer getting a reading it "
                f"can trust" if last > last_ok else "the collector may have stopped"))

    span = (_dt.date.fromisoformat(last) - _dt.date.fromisoformat(min(dates))).days + 1
    if span > len(set(dates)):
        have = set(dates)
        d0 = _dt.date.fromisoformat(min(dates))
        gaps = [(d0 + _dt.timedelta(days=i)).isoformat() for i in range(span)
                if (d0 + _dt.timedelta(days=i)).isoformat() not in have]
        out.append(f"{len(gaps)} day(s) missing from the series, first {gaps[0]}")

    unver = [r["date"] for r in records if not r.get("verified")]
    if unver:
        out.append(f"{len(unver)} day(s) recorded unverified, first {min(unver)}")

    # THE PROMISES, CHECKED AGAINST WHAT IS ACTUALLY PUBLISHED rather than against what the
    # builder would produce now. A hand edit or a half deployed build is exactly the case where
    # those two differ, and it is the case worth catching.
    main = _main_of(page_html)
    if main is None:
        out.append("the page has no main element; the site shell has changed shape and the "
                   "numeral check cannot tell copy from chrome")
        main = ""
    try:
        stray = wp.lint(main, wp.figures(records))
    except Exception as exc:                                           # noqa: BLE001
        out.append(f"the numeral gate could not run against the published page: {exc}")
        stray = []
    if stray:
        out.append("numerals on the published page trace to no computation: "
                   + ", ".join(stray[:8]))

    low = page_html.lower()
    said = [w for w in VERDICTS if w in _reader_copy(page_html, main)]
    if said:
        out.append("supply verdict language on a page that promises never to publish one: "
                   + ", ".join(said))

    # THE GAUGE IS A BAR. Same doctrine as the grid watch and for the same reason: a dial
    # implies a red zone, and a red zone is a verdict this page does not get to publish.
    if "conic-gradient" in low or re.search(r'class="[^"]*\bdial\b', low):
        out.append("the gauge has become a dial; it must be a bar, because a dial implies a "
                   "red zone and a red zone is a verdict")
    if re.search(r'class="fill [a-z]', low):
        out.append("the gauge fill has gained a severity class; one hue at every value")

    # PERCENT FULL IS COMPUTED, NEVER READ. The page says so in its own copy, and that sentence
    # is the promise a reader is given about where the number came from. If the sentence goes,
    # either the method changed and the page stopped saying so, or the page stopped explaining
    # a method it still uses. Both are worth a look.
    if "storage over capacity" not in low:
        out.append("the page no longer says percent full is computed from storage over "
                   "capacity; that sentence is the provenance promise for its headline number")

    # THE SAN ANTONIO AND EL PASO DISCLOSURE RULES ARE GONE, on the owner's explicit
    # instruction, 2026-08-20. Recorded here because it reverses a rule this repo argued for.
    #
    # They required the page to explain that the state's water data does not tag San Antonio,
    # and that El Paso's only tagged reservoir is Elephant Butte Lake in New Mexico. The
    # reasoning was that a page which simply omitted San Antonio reads as a city with no water,
    # which is exactly backwards. That reasoning is still sound. The owner's call is that the
    # sentences are not worth the screen space they cost a reader, and what a page is FOR is
    # the owner's decision rather than this checker's.
    #
    # THE RULE AND ITS COPY WENT TOGETHER, which is the part worth keeping in mind. A gate left
    # standing over copy nobody intends to write again is a permanently red advisory, and this
    # project has already learned twice what that does: a finding that is always there trains
    # whoever reads it to skim past the one that is real. See the verdict scan above, which was
    # exactly that for months.
    #
    # The facts are still published. `waterwatch.json` carries the exclusions per reservoir and
    # the metro tagging is visible in the roll up itself.

    # SEARCHED IN THE READER'S VIEW, NOT IN THE WHOLE BYTES. This asked whether the newest
    # reading's date appeared anywhere in the file, and the head carries a `temporalCoverage`
    # ending on exactly that date, computed by the builder from the same ledger. So the check
    # was answering a question about its own input rather than about the page: it passed
    # because the structured data agreed with the ledger, which it always will.
    #
    # The sibling learned this first, with the registry roster's effective dates, and wrote it
    # down. Same defect, one file over, found by the severity self-test below rather than by
    # anything reading the rule. The promise is that a READER can see the newest reading, so
    # the reader's half of the document is where it is checked. If there is no main element
    # that is already its own finding above, and the whole page is used rather than letting
    # this quietly become unfailable.
    where = main or page_html
    if last_ok not in where and _fmt(last_ok) not in where:
        stop(f"the published page does not show the newest verified reading ({last_ok}); "
             f"the site is stale against the ledger")
    return out


def code_for(found: list[str], halting: list[str]) -> int:
    """The exit code, as a pure function, so the self-test can assert on the CODE itself.

    Inline in `main` this was three lines nothing could reach without writing fixture files and
    rewriting `sys.argv`, so the self-test asserted on the findings list and simply trusted that
    main mapped it correctly. That is the gap the whole severity split exists to close, one
    level down: a rule that is right and a wiring that drops it.
    """
    if not found:
        return 0
    return 3 if halting else 2


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    """Prove the check can go red. A check that cannot fail proves nothing about the page."""
    import waterwatch_page as wp
    failures = 0

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    def rec(date, verified=True, storage=24303346.0):
        """One day's reading in the shape the collector actually writes.

        `metros` is a dict keyed by slug and `reservoirs` is a map of name to storage, not
        lists. Writing them as lists here would produce a fixture that passes a check the real
        ledger would crash, which is the wrong direction for a self-test to be wrong in.
        """
        return {"_spec": 1, "date": date, "verified": verified,
                "storage_af": storage, "capacity_af": 31558535.0,
                "percent_full": round(storage / 31558535.0 * 100, 2), "reservoir_count": 121,
                "percent_full_max_disagreement": 0.02,
                "excluded_no_conservation_pool": ["Lewisville Flood Pool", "Grapevine Flood"],
                "excluded_out_of_state": ["Elephant Butte Lake"],
                "source": "TWDB", "note": "",
                "reservoirs": {"Travis": 1.0, "Buchanan": 2.0},
                "metros": {"austin": {"percent_full": 60.0, "storage_af": 1000.0,
                                      "capacity_af": 2000.0, "reservoirs": 3},
                           "abilene": {"percent_full": 44.67, "storage_af": 422369.0,
                                       "capacity_af": 945568.0, "reservoirs": 4}}}

    def shell(body: str) -> str:
        """The body inside the site's real chrome, numerals and all.

        The chrome carries a viewport, a rebuild date and structured data, none of which the
        water watch computed. Wrapping the test bodies in it is what proves the check reads
        copy and not chrome.
        """
        return ('<!doctype html><html lang="en-US"><head>'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                # THE CONTENT SECURITY POLICY IS PART OF THE CHROME, and leaving it out is what
                # let a false positive live here. `style-src-attr 'unsafe-inline'` carries the
                # letters of "safe", so the real page reported a supply verdict every run while
                # this fixture reported none. A fixture that is missing the one piece of chrome
                # that breaks the rule is not testing the rule.
                '<meta http-equiv="Content-Security-Policy" content="default-src \'self\'; '
                "style-src 'self' 'sha256-AAAA'; style-src-attr 'unsafe-inline'; "
                'object-src \'none\'">'
                '<script type="application/ld+json">{"@type":"Dataset","dateModified":'
                '"2026-08-16","version":3}</script></head><body>'
                '<header class="masthead"><a href="./">Texas AI Docket</a></header>'
                f'<main id="main" class="wrap">{body}</main></body></html>')

    today = "2026-08-16"
    records = [rec("2026-08-15"), rec(today)]
    good_body = wp.body(records, today)
    good = shell(good_body)

    check("the real builder's own page passes", findings(good, records, today) == [],
          str(findings(good, records, today)))

    # THE RED CASES. Each one is a promise, and each has to be able to break.
    check("an empty page is caught", findings("", records, today) != [])
    check("no readings at all is caught", findings(good, [], today) != [])

    stale = [rec("2026-08-01")]
    f = findings(shell(wp.body(stale, today)), stale, today)
    check("a collector that stopped is caught", any("days back" in x for x in f), str(f))

    gappy = [rec("2026-08-11"), rec("2026-08-13"), rec("2026-08-16")]
    f = findings(shell(wp.body(gappy, today)), gappy, today)
    check("a hole in the series is caught", any("missing from the series" in x for x in f),
          str(f))

    unver = [rec("2026-08-15"), rec(today, verified=False)]
    f = findings(shell(wp.body(unver, today)), unver, today)
    check("an unverified day is reported", any("unverified" in x for x in f), str(f))

    f = findings(shell(good_body + "<p>The state is running dry.</p>"), records, today)
    check("a supply verdict is CAUGHT", any("verdict language" in x for x in f), str(f))
    f = findings(shell(good_body + "<p>Supplies are safe.</p>"), records, today)
    check("...including a reassuring one, which is equally a verdict",
          any("verdict language" in x for x in f), str(f))

    # THE FALSE POSITIVE THAT LIVED HERE, REPLAYED. The chrome above now carries a real content
    # security policy, and `style-src-attr 'unsafe-inline'` contains the letters of "safe". This
    # asserts the scan reads copy, so the policy can say what it has to say without the page
    # being accused of grading the water supply.
    f = findings(shell(good_body), records, today)
    check("the policy meta's own unsafe-inline is not read as a verdict",
          not any("verdict language" in x for x in f), str(f))

    # ...AND THE SCAN DID NOT SIMPLY NARROW TO NOTHING. Scoping a check to fix a false positive
    # is one edit away from scoping it until it cannot fail, so the head is still read: the
    # description is the sentence that represents this page in a search result and in a shared
    # link, and more people read it than read the page.
    verdict_head = shell(good_body).replace(
        '<meta name="viewport"',
        '<meta name="description" content="Texas water supplies are safe"><meta name="viewport"')
    f = findings(verdict_head, records, today)
    check("...while a verdict in the page description is still caught",
          any("verdict language" in x for x in f), str(f))

    # ...but a fetched drought classification is reporting, not grading, and must stay quiet.
    f = findings(shell(good_body + "<p>The drought monitor lists D2 across the Panhandle.</p>"),
                 records, today)
    check("...while naming what the drought monitor published is NOT a verdict",
          not any("verdict language" in x for x in f), str(f))

    f = findings(shell(good_body.replace("<div", '<div class="dial"', 1)), records, today)
    check("a gauge turned into a dial is caught", any("dial" in x for x in f), str(f))
    f = findings(shell(good_body + '<span class="fill high"></span>'), records, today)
    check("a severity class on the fill is caught",
          any("severity class" in x for x in f), str(f))

    f = findings(shell(good_body.replace("storage over capacity", "the feed")), records, today)
    check("dropping the provenance sentence is caught",
          any("storage over capacity" in x for x in f), str(f))

    f = findings(shell(good_body + "<p>1,234,567 acre feet appeared from nowhere.</p>"),
                 records, today)
    check("a numeral tracing to no computation is caught",
          any("trace to no computation" in x for x in f), str(f))

    # The chrome must not be linted, or this reports a finding every day and trains whoever
    # reads it to ignore the one that matters.
    check("the site chrome's own numerals are not reported",
          findings(good, records, today) == [], str(findings(good, records, today)))

    # ----------------------------------------------------------------- THE TWO SEVERITIES
    # Every case above asserts a rule FIRES. These assert it fires at the right VOLUME, which
    # is the half that was missing: every finding here reported exit 2, CI turned 2 into a
    # warning, and a dead collector was therefore indistinguishable from a drifted sentence.
    #
    # Each check below states which side of the line it is on and why, because the line is a
    # judgement and a judgement nobody wrote down gets redrawn by whoever edits next.

    def split(html, recs, when=today):
        halt: list[str] = []
        return findings(html, recs, when, halt), halt

    f, h = split(good, records)
    check("a clean page is neither, and exits 0", (f, h, code_for(f, h)) == ([], [], 0), str(f))

    # STOPPED. Nothing a page edit can reach, and every one of them means a number a reader is
    # looking at is no longer being refreshed.
    f, h = split(shell(wp.body(stale, today)), stale)
    check("a collector that stopped is HALTING", any("days back" in x for x in h), str(h))
    check("...so it exits 3, which CI fails on", code_for(f, h) == 3)

    f, h = split("", records)
    check("a missing page is HALTING", h != [] and code_for(f, h) == 3, str(h))
    f, h = split(good, [])
    check("a record with no readings at all is HALTING", h != [] and code_for(f, h) == 3, str(h))

    # THE FAILURE THAT LOOKS LIKE HEALTH FROM OUTSIDE. The collector runs on schedule, writes a
    # record every day and exits 0, and every one of those records says it could not trust what
    # it fetched. Nothing is missing, nothing errors, the cron is green, and the page has been
    # frozen on the last day that verified for as long as it has been going on.
    dead = [rec("2026-08-02"), rec("2026-08-15", verified=False), rec(today, verified=False)]
    f, h = split(shell(wp.body(dead, today)), dead)
    check("a collector still writing but no longer VERIFYING is HALTING",
          any("no longer getting a reading it can trust" in x for x in h), str(h))
    check("...and it names both dates, so the two failures can be told apart",
          any("2026-08-02" in x and today in x for x in h), str(h))

    never = [rec("2026-08-15", verified=False), rec(today, verified=False)]
    f, h = split(good, never)
    check("a collector that has NEVER verified is HALTING",
          any("no verified reading at all" in x for x in h), str(h))

    # A site that stopped rebuilding. The reading landed and no reader can see it, which is the
    # same outage from where a reader stands.
    day_before = [rec("2026-08-14"), rec("2026-08-15")]
    f, h = split(shell(wp.body(day_before, today)), records)
    check("a site stale against its own ledger is HALTING",
          any("stale against the ledger" in x for x in h), str(h))

    # ADVISORY. Each of these is a page reading wrong, and a page reading wrong must never cost
    # a build, because the fix is a commit and the cost of blocking is a day of everything else.
    for label, body in (
            ("a supply verdict", good_body + "<p>The state is running dry.</p>"),
            ("a typed numeral", good_body + "<p>1,234,567 acre feet appeared from nowhere.</p>"),
            ("a gauge turned into a dial", good_body.replace("<div", '<div class="dial"', 1)),
            ("a dropped provenance sentence",
             good_body.replace("storage over capacity", "the feed"))):
        f, h = split(shell(body), records)
        check(f"{label} is ADVISORY, and exits 2",
              f != [] and h == [] and code_for(f, h) == 2, str(h))

    # THE TWO THAT ARE DELIBERATELY NOT HALTING, and this is the check that records why.
    # TWDB keeps no archive to backfill from, so a gap and an already-recorded unverified day
    # are PERMANENT. Failing on them would make the build red forever with no action that could
    # clear it, and this repo already knows what a permanently red gate becomes: a gate somebody
    # turns off, taking the real findings with it.
    f, h = split(shell(wp.body(gappy, today)), gappy)
    check("a permanent hole in the series is reported but NOT halting",
          any("missing from the series" in x for x in f) and h == [], str(h))
    f, h = split(shell(wp.body(unver, today)), unver)
    check("a day already recorded unverified is reported but NOT halting",
          any("unverified" in x for x in f) and h == [], str(h))

    # AND THE TWO CHANNELS DO NOT SWALLOW EACH OTHER. A page can be stale AND read wrong at the
    # same time, and the likeliest way to get this split wrong is for one severity to short
    # circuit the other: return early on the first halting finding and the presentation report
    # goes quiet, so the day the collector dies is the day nobody hears about anything else.
    f, h = split(shell(wp.body(stale, today) + "<p>The state is running dry.</p>"), stale)
    check("a stopped collector and a verdict are reported TOGETHER",
          any("days back" in x for x in h) and any("verdict language" in x for x in f), str(f))
    check("...with only the collector halting, and the pair still exiting 3",
          not any("verdict language" in x for x in h) and code_for(f, h) == 3, str(h))

    if failures:
        print(f"\nwaterwatch_pagecheck self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\nwaterwatch_pagecheck self-test: all passed (the check can go red, at two volumes)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--today", default=_dt.date.today().isoformat())
    ap.add_argument("--page", default=str(PAGE))
    ap.add_argument("--readings", default=str(READINGS))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        return self_test()

    page = Path(a.page)
    html = page.read_text(encoding="utf-8") if page.exists() else ""
    halting: list[str] = []
    found = findings(html, load(Path(a.readings)), a.today, halting)

    code = code_for(found, halting)
    if code == 0:
        print("water watch page: current, and holding its promises")
        return 0
    print(f"water watch page: {len(found)} finding(s)", file=sys.stderr)
    for f in found:
        print(f"  {'STOPPED' if f in halting else 'advisory'}  {f}", file=sys.stderr)

    if code == 3:
        print("\n  HALTING. The instrument has stopped rather than read wrong, so this fails "
              "rather than\n  warns. Presentation fixes cannot reach it. The collector and the "
              "ledgers belong to\n  cron and to whoever maintains it.", file=sys.stderr)
        return 3
    print("\n  ADVISORY. This never blocks a run. Presentation fixes go in "
          "scripts/site/waterwatch_page.py\n  and nowhere else. The collector and the ledgers "
          "belong to cron.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                           # noqa: BLE001
        print(f"waterwatch_pagecheck: broke: {exc}", file=sys.stderr)
        sys.exit(1)
