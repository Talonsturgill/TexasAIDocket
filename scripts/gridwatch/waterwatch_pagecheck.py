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

WHO RUNS THIS AND WHY IT CANNOT FAIL LOUDLY

The daily routine runs it once per run, read only.

    EXIT 0  the page is current and holds its promises
    EXIT 2  something wants attention
    EXIT 1  reserved for this script itself being broken, and nothing else

THE EXIT CODES ARE THE WHOLE DESIGN, copied deliberately from the sibling. A check that can
abort the run it rides along with is a check that will eventually be removed for costing a day's
carousel over a stale chart. So the finding is 2, the routine treats 2 as advisory, and a bad
water watch never stops a good run. The inverse matters just as much: a bad run never stops the
check, because the check reads the PUBLISHED site rather than anything the run produced.

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


def findings(page_html: str, records: list, today: str) -> list[str]:
    """Everything wrong with the published page, in the order a reader would meet it."""
    import waterwatch_page as wp

    out: list[str] = []
    if not page_html.strip():
        return ["the published water watch page is missing or empty"]

    if not records:
        out.append("the record holds no readings at all; the collector has never succeeded")
        return out

    dates = [r["date"] for r in records if r.get("date")]
    last = max(dates)
    behind = (_dt.date.fromisoformat(today) - _dt.date.fromisoformat(last)).days
    if behind > STALE_DAYS:
        out.append(f"the newest reading is {last}, which is {behind} days back; "
                   f"the collector may have stopped")

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

    # A METRO WITH NO LINE IS A GAP, NEVER A DRY CITY. The state's water data tags reservoirs to
    # some statistical areas and not others, and San Antonio is one it does not tag. Publishing
    # that as an absence would read as a city with no water, which is exactly backwards.
    latest = max(records, key=lambda r: r.get("date") or "")
    cov = (latest.get("coverage") or {}) if isinstance(latest.get("coverage"), dict) else {}
    # `metros` is a dict keyed by slug, so the slugs are what name the metros with a line.
    metro_slugs = " ".join(str(k).lower().replace("-", " ").replace("_", " ")
                           for k in (latest.get("metros") or {}))
    if "san antonio" not in metro_slugs and "san antonio" not in low:
        out.append("San Antonio has no line and the page does not explain why; an untagged "
                   "metro read as a dry one is exactly backwards")

    if latest.get("excluded_out_of_state") and "el paso" not in low:
        out.append("out of state reservoirs are excluded and the page does not say so; "
                   "El Paso's absence needs the sentence that explains it")

    if last not in page_html and _fmt(last) not in page_html:
        out.append(f"the published page does not show the newest reading ({last}); "
                   f"the site is stale against the ledger")
    return out


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

    f = findings(shell(good_body.replace("San Antonio", "That city")), records, today)
    check("San Antonio's absence going unexplained is caught",
          any("San Antonio" in x for x in f), str(f))

    f = findings(shell(good_body.replace("El Paso", "That city")), records, today)
    check("El Paso's exclusion going unexplained is caught",
          any("El Paso" in x for x in f), str(f))

    f = findings(shell(good_body + "<p>1,234,567 acre feet appeared from nowhere.</p>"),
                 records, today)
    check("a numeral tracing to no computation is caught",
          any("trace to no computation" in x for x in f), str(f))

    # The chrome must not be linted, or this reports a finding every day and trains whoever
    # reads it to ignore the one that matters.
    check("the site chrome's own numerals are not reported",
          findings(good, records, today) == [], str(findings(good, records, today)))

    if failures:
        print(f"\nwaterwatch_pagecheck self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\nwaterwatch_pagecheck self-test: all passed (the check can go red)")
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
    found = findings(html, load(Path(a.readings)), a.today)

    if not found:
        print("water watch page: current, and holding its promises")
        return 0
    print(f"water watch page: {len(found)} finding(s)", file=sys.stderr)
    for f in found:
        print(f"  - {f}", file=sys.stderr)
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
