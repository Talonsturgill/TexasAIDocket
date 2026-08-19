#!/usr/bin/env python3
"""gridwatch_pagecheck.py — the daily once over of the published Grid Watch page.

WHO RUNS THIS AND WHY IT CANNOT FAIL LOUDLY

The carousel routine runs it once per run, read only. The grid watch has no routine of its own
and no reader: it is a cron that writes a file and a builder that renders it, and neither of
those would ever notice the page going wrong. Something has to look.

    EXIT 0  the page is current and holds its promises
    EXIT 2  something wants attention
    EXIT 1  reserved for this script itself being broken, and nothing else

THE EXIT CODES ARE THE WHOLE DESIGN. A check that can abort the run it rides along with is a
check that will eventually be removed for costing a day's carousel over a stale chart. So the
finding is 2, the routine treats 2 as advisory, and a bad grid watch never stops a good run.
The inverse matters just as much: a bad run never stops the check, because the check reads the
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


def findings(page_html: str, records: list, today: str,
             queue_data: dict | None = None) -> list[str]:
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
    """
    import gridwatch_page as gp

    out: list[str] = []
    if not page_html.strip():
        return ["the published grid watch page is missing or empty"]

    if not records:
        out.append("the record holds no readings at all; the collector has never succeeded")
        return out

    dates = [r["date"] for r in records if r.get("date")]
    last = max(dates)
    behind = (_dt.date.fromisoformat(today) - _dt.date.fromisoformat(last)).days
    # The collector files the SETTLED PREVIOUS day, so one day behind is the healthy steady
    # state and is not a finding. Anything past the threshold is.
    if behind > STALE_DAYS:
        out.append(f"the newest reading is {last}, which is {behind} days back; "
                   f"the collector may have stopped")

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
    if last not in where and _fmt(last) not in where:
        out.append(f"the published page does not show the newest reading ({last}); "
                   f"the site is stale against the ledger")
    return out


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
          any("does not show the newest reading" in x for x in f), str(f))

    check("an empty page is a finding, not a crash",
          findings("", good, "2026-08-11", gp.NO_QUEUE) == ["the published grid watch page is missing or "
                                               "empty"])
    check("an empty record is a finding, not a crash",
          any("never succeeded" in x for x in findings(html, [], "2026-08-11", gp.NO_QUEUE)))

    if failures:
        print(f"\ngridwatch_pagecheck self-test: {failures} FAILED")
        return 1
    print("\ngridwatch_pagecheck self-test: all passed")
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
    found = findings(page.read_text(encoding="utf-8") if page.exists() else "",
                     gp.load(), a.today)
    if not found:
        print("gridwatch page: current, and holding its promises")
        return 0
    print("gridwatch page: wants attention\n")
    for x in found:
        print(f"  - {x}")
    print("\n  The routine may fix PRESENTATION only. The collector, the ledgers and the model\n"
          "  config are off limits to it: cron writes those, and ERCOT keeps no archive to\n"
          "  rebuild a series from. Anything else goes in the run record as a proposal.")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                       # noqa: BLE001
        # EXIT 1 MEANS THIS SCRIPT BROKE, never that the page is bad. The routine reads 1 as
        # "the checker is broken, carry on" and 2 as "look at the page".
        print(f"gridwatch_pagecheck: broke: {exc}", file=sys.stderr)
        sys.exit(1)
