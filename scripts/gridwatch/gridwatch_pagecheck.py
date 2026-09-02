#!/usr/bin/env python3
"""gridwatch_pagecheck.py — the daily once over of the published Grid Watch page.

WHO RUNS THIS AND WHY IT CANNOT FAIL LOUDLY

The carousel routine runs it once per run, read only. The grid watch has no routine of its own
and no reader: it is a cron that writes a file and a builder that renders it, and neither of
those would ever notice the page going wrong. Something has to look.

    EXIT 0  the page is current and holds its promises
    EXIT 2  something wants attention. ADVISORY, and CI turns it into a warning
    EXIT 3  an instrument has STOPPED. Halting, and CI fails on it
    EXIT 1  reserved for this script itself being broken, and nothing else

TWO SEVERITIES, BECAUSE THEY WERE ONE AND THAT WAS A HOLE. Everything here reported 2 and CI
turned 2 into a `::warning::` and passed, on the stated reasoning that an instrument must never
fail a build over presentation. That reasoning is right about a sentence that drifted. It is
wrong about a collector that died, and until 2026-08-21 the two shared a code, so a dead
collector produced a warning from the cron and a warning from this check and BOTH JOBS WENT
GREEN. ERCOT keeps no archive, and this repo's own documentation calls a missed day the one
irreversible failure it has.

So a page reading wrong stays advisory and an instrument that has stopped now fails. The
original reasoning survives intact: exit 2 still cannot cost a day's carousel over a stale
chart, and the ROUTINE still treats every finding as advisory, because a routine cannot fix a
collector and stopping it would only cost the deck as well. CI is where a 3 is a red, and CI
runs on every push to `main`, which includes this collector's own twice daily push.

The inverse still matters as much: a bad run never stops the check, because the check reads the
published site rather than anything the run produced.

WHAT THE ROUTINE MAY DO ABOUT WHAT IT FINDS

Presentation only. It may fix wording, layout and markup in the site builder. It may NOT touch
the collector, the ledgers or the model config, because cron writes those and a routine that
edits them corrupts a series ERCOT keeps no archive to rebuild. That boundary is enforced by
ownership.yaml and this file is only the messenger.
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

PAGE = REPO_ROOT / "docs" / "grid" / "index.html"

# How far behind the collector may fall before it is worth a human's attention. Two scheduled
# runs a day means a single missed slot is invisible; two days dark means both slots failed
# twice, which is a broken collector rather than a bad morning.
STALE_DAYS = 2

QUEUE_LEDGER = REPO_ROOT / "ledger" / "gridwatch" / "queue.jsonl"

# THE QUEUE IS MONTHLY, so its staleness is counted in months and not in days. ERCOT publishes
# the Monthly Operational Overview in arrears, so the newest verified month sitting one behind
# the calendar is the healthy steady state. Two is the slack for a report that runs late.
QUEUE_STALE_MONTHS = 2


def _months_between(a: str, b: str) -> int:
    """Whole months from one YYYY-MM to another. Negative if b is behind a."""
    ay, am = (int(x) for x in a.split("-")[:2])
    by, bm = (int(x) for x in b.split("-")[:2])
    return (by - ay) * 12 + (bm - am)


def queue_rows(path: Path = QUEUE_LEDGER) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out


def queue_findings(rows: list[dict], today: str,
                   halting: list | None = None) -> list[str]:
    """Whether the large load queue reading is still arriving, and still verifying.

    THE HOLE THIS CLOSES, and it is the shape this project keeps finding. The queue is
    collected daily and its figures are numeral gated daily, so both halves LOOK covered. What
    nothing watched was whether a reading was still ARRIVING.

    `queue_collect` is built to write an explicit unverified record rather than guess when the
    figures it reads move out of the report's text layer, which is correct and is the whole
    reason it can be trusted. Its workflow then treats exit 2 as a normal outcome, which is
    also correct, because a report that is not up yet is not a failure.

    Put those two correct decisions together and the failure mode is silent. If ERCOT moves the
    two funnel figures into the chart image, as this collector's own docstring anticipates,
    every run writes unverified, every run exits 2, the job stays GREEN, and the grid page goes
    on publishing the last month that verified for as long as anybody leaves it. On a site with
    no humans in it that is indefinitely.

    Two rules, because the two failures look different. A collector that has STOPPED leaves the
    newest verified month falling further behind the calendar. A collector that is still running
    and no longer UNDERSTANDS the report leaves a fresh unverified record on top of a stale
    verified one.

    EVERY FINDING HERE IS HALTING, which is not true of the page rules above. There is no
    presentation failure this function can report. Each of its four findings means a figure the
    page publishes has stopped being refreshed, and each clears the moment a verified month
    lands, so none of them can become the permanently red gate this repo keeps warning itself
    about. `halting` is filled through a parameter for the same reason the caller's is: one
    implementation of each rule, rather than two that can drift.
    """
    out: list[str] = []
    halt = halting if halting is not None else []

    def stop(msg: str) -> list[str]:
        halt.append(msg)
        out.append(msg)
        return out

    if not rows:
        return stop("the queue ledger holds no readings at all; that collector has never "
                    "succeeded")

    months = sorted(r["month"] for r in rows if r.get("month"))
    verified = sorted(r["month"] for r in rows if r.get("verified") and r.get("month"))
    if not verified:
        return stop("no queue reading has ever verified; the figures may have left the "
                    "report's text layer, and the page has nothing it may publish")

    newest, newest_ok = months[-1], verified[-1]
    behind = _months_between(newest_ok, today[:7])
    if behind > QUEUE_STALE_MONTHS:
        stop(f"the newest verified queue month is {newest_ok}, which is {behind} months "
             f"back; the large load reading may have stopped arriving")
    # An unverified row means two different things. Before ERCOT publishes the next monthly
    # overview it is the collector honestly recording "not here yet". Once a source URL exists,
    # an unverified row means the report arrived but the collector could no longer understand
    # it. Only the second condition is immediate parser drift. Publication delay is already
    # bounded by the verified-month staleness rule above.
    newest_rows = [r for r in rows if r.get("month") == newest]
    report_arrived_unverified = any(
        not r.get("verified") and bool(r.get("source_url")) for r in newest_rows)
    if newest > newest_ok and report_arrived_unverified:
        stop(f"the newest queue reading ({newest}) is unverified while the newest "
             f"verified one is {newest_ok}; the report's sentence may have moved and the "
             f"page is publishing an older month")
    return out


def findings(page_html: str, records: list, today: str,
             queue_data: dict | None = None,
             queue_months: list | None = None,
             halting: list | None = None) -> list[str]:
    """Everything wrong with the published page, in the order a reader would meet it.

    `queue_data` IS THE HERMETIC SEAM, and it exists for one reason worth stating. Production
    passes nothing and the live queue ledger is read, which is right, because the real page
    prints real queue figures and they have to be authorised.

    A TEST must pass its own. `gridwatch_page` learned this first and wrote it down next to its
    `NO_QUEUE` fixture: handing the live ledger to a hermetic test let a planted "8.9" pass,
    because the ledger happened to hold a month at 8,926 MW and the page renders that as
    "8.9 GW". The planted numeral was authorised, so the check that is supposed to catch a typed
    figure reported a clean page, truthfully, and could not go red.

    That fix landed one file away and this one kept calling `figures` with the live ledger, so
    the same assertion here went quiet in exactly the same way. A gate that cannot fail is worse
    than no gate, because the suite reports it green.

    `halting` COLLECTS THE SUBSET THAT MEANS AN INSTRUMENT HAS STOPPED, as opposed to a page
    reading wrong. See the exit codes at the top of this file for why the two stopped sharing
    one. Filled through a parameter rather than returned separately so there is ONE
    implementation of each rule, because two functions computing staleness is two places for it
    to drift.

    WHAT IS DELIBERATELY NOT HALTING. A gap in the series and a day already recorded unverified
    are PERMANENT, because ERCOT keeps no archive to backfill from. Failing on those would make
    the build red forever with no action that could clear it, which is the trap this repo
    already knows: a check that is always red is a check somebody turns off, and it takes the
    real findings with it. They stay findings. So does every presentation rule below them.
    """
    import gridwatch_page as gp

    out: list[str] = []
    halt = halting if halting is not None else []

    def stop(msg: str) -> None:
        """A finding that means something has stopped rather than read wrong."""
        out.append(msg)
        halt.append(msg)

    if not page_html.strip():
        stop("the published grid watch page is missing or empty")
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
    # `queue_findings` was written for, one series over, and neither daily series was checking
    # it. It also put this rule at odds with the site rule at the bottom of this function,
    # which compares against the newest reading the page is ALLOWED to show.
    #
    # The collector files the SETTLED PREVIOUS day, so one day behind is the healthy steady
    # state and is not a finding. Anything past the threshold is.
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
        out.append(f"{len(gaps)} day(s) missing from the series, first {gaps[0]}; "
                   f"ERCOT cannot backfill these")

    unver = [r["date"] for r in records if not r.get("verified")]
    if unver:
        out.append(f"{len(unver)} day(s) recorded unverified, first {min(unver)}")

    # THE QUEUE, WHICH IS THE OTHER SERIES THIS PAGE PUBLISHES. Everything above is the demand
    # ledger. The queue arrives monthly on its own cron and nothing was watching whether it
    # still arrived. Its rows travel through the same hermetic seam the figures do.
    out.extend(queue_findings(queue_rows() if queue_months is None else queue_months,
                              today, halt))

    # THE PROMISES, CHECKED AGAINST WHAT IS ACTUALLY PUBLISHED rather than against what the
    # builder would produce now. A hand edit or a half deployed build is exactly the case
    # where those two differ, and it is the case worth catching.
    #
    # Only the grid watch's own body is linted. The surrounding shell carries the site's
    # rebuild date, its structured data and its viewport, all computed elsewhere and checked
    # elsewhere; sweeping them in here would report a finding every single day and train
    # whoever reads this to ignore it.
    main = _main_of(page_html)
    if main is None:
        out.append("the page has no main element; the site shell has changed shape and the "
                   "numeral check cannot tell copy from chrome")
        main = ""
    stray = gp.lint(main, gp.figures(records, queue_data))
    if stray:
        out.append("numerals on the published page trace to no computation: "
                   + ", ".join(stray[:8]))

    low = page_html.lower()
    verdicts = [w for w in ("shortfall", "blackout", "all clear", "emergency", "at risk",
                            "conservation appeal") if w in low]
    if verdicts:
        out.append("reliability verdict language on a page that promises never to publish "
                   "one: " + ", ".join(verdicts))

    if "conic-gradient" in low or re.search(r'class="[^"]*\bdial\b', low):
        out.append("the gauge has become a dial; it must be a bar, because a dial implies a "
                   "red zone and a red zone is a verdict")
    if re.search(r'class="fill [a-z]', low):
        out.append("the gauge fill has gained a severity class; one hue at every value")

    # SEARCHED IN THE DAILY SECTION, NOT THE WHOLE PAGE. This looked for the newest reading's
    # date anywhere in the bytes, which was fine while the page carried a handful of dates and
    # became a gate passing by collision the moment it carried many: the registry roster prints
    # an effective date for all 149 facilities, two of them took effect on 2026-08-10, and a
    # page deliberately built one day stale against a ledger ending 2026-08-10 reported itself
    # current. Changing the fixture's date would have hidden it rather than fixed it, because
    # the registry gains rows daily and any day a facility's effective date equals the newest
    # grid reading the real check would go blind in exactly the same way.
    #
    # The newest reading belongs to the daily panel, so that is where it has to appear. If the
    # section cannot be found the whole page is used, because a missing section is a different
    # finding and this check should not silently become unfailable.
    daily = DAILY.search(page_html)
    where = daily.group(1) if daily else page_html
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


DAILY = re.compile(r'(<section class="daily".*?</section>)', re.DOTALL | re.IGNORECASE)
MAIN = re.compile(r"<main\b[^>]*>(.*)</main>", re.DOTALL | re.IGNORECASE)


def _main_of(page_html: str) -> str | None:
    """The reader facing body, separated from the shell around it.

    Returns None when there is no main element, which is a finding in its own right rather
    than a reason to check nothing.
    """
    m = MAIN.search(page_html)
    return m.group(1) if m else None


def _fmt(iso: str) -> str:
    d = _dt.date.fromisoformat(iso)
    suf = "th" if 11 <= d.day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d.day % 10, "th")
    return f"{d:%B} {d.day}{suf}, {d.year}"


def self_test() -> int:
    import gridwatch_page as gp
    failures = 0

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    def rec(date, verified=True):
        n = 24
        load = [60000.0 + 900 * min(i, 16) for i in range(n)]
        return {"_spec": 1, "date": date, "verified": verified,
                "hour_ending": list(range(1, n + 1)), "load_mw": load,
                "day_ahead_forecast_mw": [v + 400 for v in load], "capacity_mw": [99000.0] * n,
                "hours_measured": n, "hours_in_day": n,
                "peak_load_mw": max(load), "peak_hour_ending": 17,
                "min_load_mw": min(load), "min_hour_ending": 1,
                "mean_load_mw": round(sum(load) / n, 1), "energy_mwh": round(sum(load), 1),
                "load_factor": round((sum(load) / n) / max(load), 4),
                "capacity_at_peak_mw": 99000.0, "reserve_at_peak_mw": 99000.0 - max(load),
                "forecast_peak_mw": max(load) + 400, "peak_forecast_error_mw": 400.0,
                "fuel_energy_mwh": {"Natural Gas": 900000.0, "Wind": 400000.0}}

    def shell(body: str) -> str:
        """The body inside the site's real chrome, numerals and all.

        The chrome carries a viewport, a rebuild date and structured data, none of which the
        grid watch computed. Wrapping the test bodies in it is what proves the check reads
        copy and not chrome.
        """
        return (
            '<!doctype html><html lang="en-US"><head>'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<script type="application/ld+json">{"@type":"Dataset","dateModified":'
            '"2026-08-11","version":3}</script></head><body>'
            '<header class="masthead"><a class="wordmark" href="./">Texas AI Docket</a></header>'
            f'<main id="main" class="wrap">{body}</main>'
            '<footer class="site"><p class="num">Rebuilt August 11th, 2026.</p>'
            '<p>13 items, 254 counties.</p></footer></body></html>')

    good = [rec("2026-08-08"), rec("2026-08-09"), rec("2026-08-10")]
    html = shell(gp.body(good, "2026-08-11", gp.NO_QUEUE))
    check("a current page with a whole series is clean",
          findings(html, good, "2026-08-11", gp.NO_QUEUE) == [], str(findings(html, good, "2026-08-11", gp.NO_QUEUE)))
    check("the site's own chrome numerals are not read as grid watch copy",
          not any("trace to no computation" in x
                  for x in findings(html, good, "2026-08-11", gp.NO_QUEUE)))
    check("a page with no main element says so rather than checking nothing",
          any("no main element" in x
              for x in findings("<body><p>1234567</p></body>", good, "2026-08-11", gp.NO_QUEUE)))

    check("one day behind is the healthy steady state, not a finding",
          not any("collector may have stopped" in f
                  for f in findings(html, good, "2026-08-11", gp.NO_QUEUE)))
    late = findings(html, good, "2026-08-14", gp.NO_QUEUE)
    check("four days behind is a finding",
          any("collector may have stopped" in f for f in late), str(late))

    holed = [rec("2026-08-05"), rec("2026-08-08"), rec("2026-08-09"), rec("2026-08-10")]
    f = findings(shell(gp.body(holed, "2026-08-11", gp.NO_QUEUE)), holed, "2026-08-11",
                 gp.NO_QUEUE)
    check("a hole in the series is found and counted",
          any("missing from the series" in x and "2026-08-06" in x for x in f), str(f))

    unv = good + [{"_spec": 1, "date": "2026-08-11", "verified": False}]
    # ---- THE QUEUE, WHOSE FAILURE IS THE QUIET ONE -----------------------------------
    # Each of these is a state the daily job reports as SUCCESS, because an unverified reading
    # is the correct output of a collector that refuses to guess. That correctness is exactly
    # what made the silence possible, so these are the shapes that have to go red here.
    healthy = [{"month": "2026-06", "verified": True}, {"month": "2026-07", "verified": True}]
    check("a queue one month behind the calendar is the healthy state",
          queue_findings(healthy, "2026-08-20") == [], str(queue_findings(healthy, "2026-08-20")))

    check("a queue reading that stopped arriving is CAUGHT",
          any("may have stopped arriving" in x
              for x in queue_findings(healthy, "2026-11-20")),
          str(queue_findings(healthy, "2026-11-20")))

    waiting = healthy + [{"month": "2026-08", "verified": False,
                          "source_url": None,
                          "note": "no Monthly Operational Overview published for this month yet"}]
    check("a not-yet-published report uses the verified-month grace window",
          queue_findings(waiting, "2026-09-01") == [],
          str(queue_findings(waiting, "2026-09-01")))

    moved = healthy + [{"month": "2026-08", "verified": False,
                        "source_url": "https://www.ercot.com/report.pdf",
                        "note": "the Approval to Energize sentence did not match"}]
    check("a fresh unverified reading over a stale verified one is CAUGHT",
          any("sentence may have moved" in x for x in queue_findings(moved, "2026-08-20")),
          str(queue_findings(moved, "2026-08-20")))

    never = queue_findings([{"month": "2026-08", "verified": False}], "2026-08-20")
    check("a queue that has never verified is CAUGHT",
          any("has ever verified" in x for x in never), str(never))

    check("an empty queue ledger is CAUGHT",
          any("never succeeded" in x for x in queue_findings([], "2026-08-20")))

    # AND THE LIVE LEDGER, which is the only reason the four above matter.
    live_q = queue_rows()
    check("the committed queue ledger is arriving and verifying",
          not queue_findings(live_q, _dt.date.today().isoformat()),
          "; ".join(queue_findings(live_q, _dt.date.today().isoformat())))

    f = findings(shell(gp.body(unv, "2026-08-12", gp.NO_QUEUE)), unv, "2026-08-12",
                 gp.NO_QUEUE)
    check("an unverified day is reported", any("unverified" in x for x in f), str(f))

    f = findings(html.replace("</h1>", "</h1><p>roughly 8.9 GW</p>"), good, "2026-08-11", gp.NO_QUEUE)
    check("a typed numeral on the published page is caught",
          any("trace to no computation" in x and "8.9" in x for x in f), str(f))

    f = findings(html.replace("</h1>", "</h1><p>ERCOT faces a shortfall</p>"),
                 good, "2026-08-11", gp.NO_QUEUE)
    check("verdict language on the published page is caught",
          any("reliability verdict language" in x for x in f), str(f))

    f = findings(html.replace('class="bar"', 'class="dial"'), good, "2026-08-11", gp.NO_QUEUE)
    check("the gauge turning into a dial is caught",
          any("become a dial" in x for x in f), str(f))
    f = findings(html.replace('class="fill"', 'class="fill critical"'), good, "2026-08-11", gp.NO_QUEUE)
    check("a severity class on the gauge is caught",
          any("severity class" in x for x in f), str(f))

    stale = shell(gp.body(good[:-1], "2026-08-11", gp.NO_QUEUE))
    f = findings(stale, good, "2026-08-11", gp.NO_QUEUE)
    check("a site stale against the ledger is caught",
          any("does not show the newest verified reading" in x for x in f), str(f))

    check("an empty page is a finding, not a crash",
          findings("", good, "2026-08-11", gp.NO_QUEUE) == ["the published grid watch page is missing or "
                                               "empty"])
    check("an empty record is a finding, not a crash",
          any("never succeeded" in x for x in findings(html, [], "2026-08-11", gp.NO_QUEUE)))

    # ----------------------------------------------------------------- THE TWO SEVERITIES
    # Every case above asserts a rule FIRES. These assert it fires at the right VOLUME, which
    # is the half that was missing: every finding here reported exit 2, CI turned 2 into a
    # warning, and a dead collector was therefore indistinguishable from a drifted sentence.
    #
    # Each check below states which side of the line it is on and why, because the line is a
    # judgement and a judgement nobody wrote down gets redrawn by whoever edits next.

    def split(page, recs, when="2026-08-11", q=None, months=None):
        halt: list[str] = []
        return (findings(page, recs, when, gp.NO_QUEUE if q is None else q,
                         healthy if months is None else months, halt), halt)

    f, h = split(html, good)
    check("a clean page is neither, and exits 0", (f, h, code_for(f, h)) == ([], [], 0), str(f))

    # STOPPED. Nothing a page edit can reach, and every one means a number a reader is looking
    # at is no longer being refreshed.
    f, h = split(html, good, "2026-08-14")
    check("a collector that stopped is HALTING", any("days back" in x for x in h), str(h))
    check("...so it exits 3, which CI fails on", code_for(f, h) == 3)

    f, h = split("", good)
    check("a missing page is HALTING", h != [] and code_for(f, h) == 3, str(h))
    f, h = split(html, [])
    check("a record with no readings at all is HALTING", h != [] and code_for(f, h) == 3, str(h))

    # THE FAILURE THAT LOOKS LIKE HEALTH FROM OUTSIDE. The collector runs on schedule, writes a
    # record every day and exits 0, and every one of those records says it could not trust what
    # it fetched. Nothing is missing, nothing errors, the cron is green, and the page has been
    # frozen on the last day that verified for as long as it has been going on.
    dead = [rec("2026-08-02"), rec("2026-08-09", verified=False),
            rec("2026-08-10", verified=False)]
    f, h = split(shell(gp.body(dead, "2026-08-11", gp.NO_QUEUE)), dead)
    check("a collector still writing but no longer VERIFYING is HALTING",
          any("no longer getting a reading it can trust" in x for x in h), str(h))
    check("...and it names both dates, so the two failures can be told apart",
          any("2026-08-02" in x and "2026-08-10" in x for x in h), str(h))

    unverified_only = [rec("2026-08-09", verified=False), rec("2026-08-10", verified=False)]
    f, h = split(html, unverified_only)
    check("a collector that has NEVER verified is HALTING",
          any("no verified reading at all" in x for x in h), str(h))

    f, h = split(shell(gp.body(good[:-1], "2026-08-11", gp.NO_QUEUE)), good)
    check("a site stale against its own ledger is HALTING",
          any("stale against the ledger" in x for x in h), str(h))

    # THE QUEUE, WHOSE EVERY FINDING IS HALTING. It publishes one figure a month and nothing
    # about it is presentation, so there is no advisory half to get wrong.
    stalled = [{"month": "2026-01", "verified": True}]
    drifted = healthy + [{"month": "2026-08", "verified": False,
                          "source_url": "https://www.ercot.com/report.pdf"}]
    virgin = [{"month": "2026-08", "verified": False}]
    for label, months in (("a queue that stopped arriving", stalled),
                          ("a queue that no longer verifies", drifted),
                          ("a queue that never verified", virgin),
                          ("an empty queue ledger", [])):
        f, h = split(html, good, months=months)
        check(f"{label} is HALTING, and exits 3",
              h != [] and code_for(f, h) == 3, str(h))

    # ADVISORY. Each of these is a page reading wrong, and a page reading wrong must never cost
    # a build, because the fix is a commit and the cost of blocking is a day of everything else.
    for label, page in (
            ("a reliability verdict",
             html.replace("</h1>", "</h1><p>ERCOT faces a shortfall</p>")),
            ("a typed numeral", html.replace("</h1>", "</h1><p>roughly 8.9 GW</p>")),
            ("a gauge turned into a dial", html.replace('class="bar"', 'class="dial"')),
            ("a severity class on the fill",
             html.replace('class="fill"', 'class="fill critical"'))):
        f, h = split(page, good)
        check(f"{label} is ADVISORY, and exits 2",
              f != [] and h == [] and code_for(f, h) == 2, str(h))

    # THE TWO THAT ARE DELIBERATELY NOT HALTING, and this is the check that records why.
    # ERCOT keeps no archive to backfill from, so a gap and an already-recorded unverified day
    # are PERMANENT. Failing on them would make the build red forever with no action that could
    # clear it, and this repo already knows what a permanently red gate becomes: a gate somebody
    # turns off, taking the real findings with it.
    f, h = split(shell(gp.body(holed, "2026-08-11", gp.NO_QUEUE)), holed)
    check("a permanent hole in the series is reported but NOT halting",
          any("missing from the series" in x for x in f) and h == [], str(h))
    f, h = split(shell(gp.body(unv, "2026-08-12", gp.NO_QUEUE)), unv, "2026-08-12")
    check("a day already recorded unverified is reported but NOT halting",
          any("unverified" in x for x in f) and h == [], str(h))

    # AND THE TWO CHANNELS DO NOT SWALLOW EACH OTHER. A page can be stale AND read wrong at the
    # same time, and the likeliest way to get this split wrong is for one severity to short
    # circuit the other: return early on the first halting finding and the presentation report
    # goes quiet, so the day the collector dies is the day nobody hears about anything else.
    f, h = split(html.replace("</h1>", "</h1><p>ERCOT faces a shortfall</p>"), good, "2026-08-14")
    check("a stopped collector and a verdict are reported TOGETHER",
          any("days back" in x for x in h)
          and any("reliability verdict" in x for x in f), str(f))
    check("...with only the collector halting, and the pair still exiting 3",
          not any("reliability verdict" in x for x in h) and code_for(f, h) == 3, str(h))

    if failures:
        print(f"\ngridwatch_pagecheck self-test: {failures} FAILED")
        return 1
    print("\ngridwatch_pagecheck self-test: all passed (the check can go red, at two volumes)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--today", default=_dt.date.today().isoformat())
    ap.add_argument("--page", default=str(PAGE))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    import gridwatch_page as gp
    page = Path(a.page)
    halting: list[str] = []
    found = findings(page.read_text(encoding="utf-8") if page.exists() else "",
                     gp.load(), a.today, halting=halting)
    code = code_for(found, halting)
    if code == 0:
        print("gridwatch page: current, and holding its promises")
        return 0
    print(f"gridwatch page: {len(found)} finding(s)\n", file=sys.stderr)
    for x in found:
        print(f"  {'STOPPED' if x in halting else 'advisory'}  {x}", file=sys.stderr)
    if code == 3:
        print("\n  HALTING. An instrument has stopped rather than read wrong, so this fails\n"
              "  rather than warns. No presentation fix can reach it. ERCOT keeps no archive to\n"
              "  rebuild a series from, so every hour this stays true is a reading nobody gets.",
              file=sys.stderr)
        return 3
    print("\n  ADVISORY. The routine may fix PRESENTATION only. The collector, the ledgers and\n"
          "  the model config are off limits to it: cron writes those. Anything else goes in\n"
          "  the run record as a proposal.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                       # noqa: BLE001
        # EXIT 1 MEANS THIS SCRIPT BROKE, never that the page is bad. The routine reads 1 as
        # "the checker is broken, carry on" and 2 as "look at the page".
        print(f"gridwatch_pagecheck: broke: {exc}", file=sys.stderr)
        sys.exit(1)
