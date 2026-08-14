#!/usr/bin/env python3
"""heatclock.py — the front page's one live line about the physical world.

WHAT THE CHIP IS AND WHY IT IS NOT ABOUT THE GRID

The front page opens with a single computed, dated fact. It used to report what ERCOT's peak
drew against committed capacity, which was true, current and correct, and almost nobody cares.
"Peak drew 75.5% of committed capacity" asks a reader to already know what committed capacity
is before it can mean anything, and a front page's opening line is the worst possible place to
require homework.

The sibling product opens with how much daylight its state capital has today and how fast it
is losing it. That line works for reasons worth naming, because they are the specification:

    IT IS ABOUT SOMETHING THE READER ALREADY FEELS. Nobody needs the unit explained.
    IT MOVES. Coming back tomorrow shows a different number.
    IT IS A CLOCK, NOT A STATISTIC. It accumulates in one direction and you can feel where
    you are in the season from it.
    IT IS TRUE WITHOUT A CAVEAT.

Texas has no daylight story worth telling, so this is the heat. The hundred degree day is the
unit Texas already counts in, without being taught it, and the count runs all summer as a
shared grievance. In the cold half of the year the same clock counts freezing nights, which is
the other extreme Texas counts and the reason it argues about its grid at all.

It also happens to be the site's whole thesis in one line. Heat drives load, load is what the
new data centres are landing on top of, and the record next door is about who gets to decide.
The chip never says that. It just reports the heat and lets the rest of the page follow.

WHY IT COMPARES AGAINST THE LAST SETTLED DAY AND NOT AGAINST TODAY

The count and the normal are measured through the SAME date, which is the last day the record
actually holds. Comparing a count through the 10th against a normal through the 14th would be
comparing unequal windows, and it would read as this year running cool.

WHAT IT REFUSES TO DO

It never forecasts. "6 more in a normal year" is an observed thirty year mean and says so. It
never reaches for today's number from a forecast feed to close the settling lag, because that
would mix a projection into a measured count.

It disappears rather than going stale. See STALE_AFTER_DAYS.
"""
from __future__ import annotations

import datetime as _dt
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

LEDGER = REPO_ROOT / "ledger" / "gridwatch" / "heat.jsonl"
NORMALS = REPO_ROOT / "config" / "gridwatch" / "heat_normals.json"

# WHICH HALF OF THE YEAR COUNTS WHICH EXTREME.
#
# April to October counts hot days, November to March counts freezing nights. The switch is by
# month rather than by "whichever happened most recently", because a single freak November
# afternoon would otherwise flip the chip back to a summer count that stopped moving weeks ago.
HOT_MONTHS = range(4, 11)

# The record settles a few days behind real time and the collector runs daily, so a gap wider
# than this means the collector has been broken for a fortnight rather than that NCEI is
# quality controlling. At that point the honest thing is to show nothing. A chip reading "by
# March 3rd" in August is accurate and still looks broken, which costs more trust than the
# line earns.
STALE_AFTER_DAYS = 21


def load(path: Path = LEDGER) -> list[dict]:
    """Every reading held, oldest first. Sorted on read; see the collector on why."""
    if not path.exists():
        return []
    rows = [json.loads(t) for t in (s.strip() for s in path.read_text().splitlines()) if t]
    rows.sort(key=lambda r: r["date"])
    return rows


def normals(path: Path = NORMALS) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _season_of(d: _dt.date, start_month: int) -> int:
    return d.year if d.month >= start_month else d.year - 1


def reading(today: _dt.date, rows: list[dict] | None = None,
            norms: dict | None = None) -> dict | None:
    """Every figure the chip prints, computed here, or None when it must not print.

    Returns None when the record is empty, when the normals are missing, or when the record
    has gone stale. A front page that invents a number to fill a slot is the exact failure
    this project exists not to have.
    """
    rows = load() if rows is None else rows
    norms = normals() if norms is None else norms
    if not rows or not norms:
        return None

    # THE LATEST DATE, NOT THE LAST LINE. `load()` sorts, so reading `rows[-1]` is correct
    # for anything that came through it and silently wrong for anything that did not. The
    # collector fills gaps by appending a date older than the line above it, so "last written"
    # and "most recent" are different questions about this ledger and only one of them is
    # the one being asked.
    last = _dt.date.fromisoformat(max(r["date"] for r in rows))
    if (today - last).days > STALE_AFTER_DAYS or last > today:
        return None

    hot = today.month in HOT_MONTHS
    key = f"{last.month:02d}-{last.day:02d}"
    table = norms["hot_through"] if hot else norms["cold_through"]
    if key not in table:
        return None

    if hot:
        thresh = norms["hot_threshold_f"]
        window = [r for r in rows
                  if r["date"][:4] == str(last.year) and r.get("tmax_f") is not None]
        count = sum(1 for r in window if r["tmax_f"] >= thresh)
        full = norms["hot_full_year"]
    else:
        thresh = norms["cold_threshold_f"]
        start = norms["season_start_month"]
        season = _season_of(last, start)
        window = [r for r in rows
                  if _season_of(_dt.date.fromisoformat(r["date"]), start) == season
                  and r.get("tmin_f") is not None]
        count = sum(1 for r in window if r["tmin_f"] <= thresh)
        full = norms["cold_full_season"]

    # ROUNDING IS A COMPUTATION WITH A STATED RULE. Whole days, nearest, and clamped at zero
    # because a normal year cannot hold a negative number of days still to come. Late in
    # December the subtraction goes slightly negative on rounding alone.
    so_far = table[key]
    remaining = max(0, round(full - so_far))

    return {
        "hot": hot,
        "place": norms["station_name"],
        "count": count,
        "threshold": thresh,
        "through": last,
        "normal_by_now": round(so_far),
        "remaining": remaining,
        "days_measured": len(window),
    }


def phrasing(r: dict) -> tuple[str, str, str]:
    """The chip's three segments, as plain text.

    Singular and plural are computed rather than assumed. "1 DAYS AT 100" is the kind of
    detail that makes an otherwise careful page look automated, which is precisely what it is
    and precisely what it must not look like.
    """
    noun = ("day", "days") if r["hot"] else ("night", "nights")
    at = f"at {r['threshold']}" if r["hot"] else "at freezing"
    period = "year" if r["hot"] else "winter"

    if r["count"] == 0:
        middle = f"no {noun[1]} {at} by {{through}}"
    else:
        middle = f"{r['count']} {noun[0] if r['count'] == 1 else noun[1]} {at} by {{through}}"

    if r["remaining"] == 0:
        # Roughly six weeks a year, between the last normal hundred degree day in September
        # and the switch to the freeze count in November, this is what the chip says. It
        # reads as the season closing out, which is exactly what it is.
        tail = "normally none left"
    elif r["remaining"] == 1:
        tail = f"1 more in a normal {period}"
    else:
        tail = f"{r['remaining']} more in a normal {period}"

    return r["place"], middle, tail


def figures(r: dict) -> list:
    """Exactly the numerals the chip prints, for the front page's authorisation set.

    THE SAME CALL THAT DRAWS IT AUTHORISES IT. The alternative is writing the rounding rule
    down a second time in the lint's allowlist, and two copies of a rounding rule is one copy
    and one bug waiting.

    EXACTLY WHAT IT PRINTS, not everything it holds. An allowlist is a gate, and every value
    added to it that no copy actually uses is a numeral the lint will wave through somewhere
    else on the page. The threshold appears only on the hot branch, because the cold branch
    writes "at freezing" rather than the number.
    """
    out = [r["count"], r["remaining"], r["through"].day]
    if r["hot"]:
        out.append(r["threshold"])
    return out


# --------------------------------------------------------------------------- self-test
def _self_test() -> int:
    fails = []

    def check(label, cond, extra=""):
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}" + ("" if cond else f"  {extra}"))
        if not cond:
            fails.append(label)

    norms = {
        "station_name": "Dallas Fort Worth", "hot_threshold_f": 100, "cold_threshold_f": 32,
        "season_start_month": 7,
        "hot_through": {"08-10": 14.6, "10-31": 20.3, "12-31": 20.3, "01-15": 0.0},
        "cold_through": {"01-15": 12.4, "06-30": 29.4, "08-10": 0.0},
        "hot_full_year": 20.3, "cold_full_season": 29.4,
    }
    rows = ([{"date": f"2026-07-{d:02d}", "tmax_f": 101, "tmin_f": 78} for d in range(1, 18)]
            + [{"date": "2026-08-10", "tmax_f": 99, "tmin_f": 77}])

    r = reading(_dt.date(2026, 8, 14), rows, norms)
    check("the summer chip counts days at or above the threshold", r["count"] == 17, r)
    check("what a normal year has left is the full year minus what has passed",
          r["remaining"] == 6, r["remaining"])
    check("the normal is read at the last SETTLED day, not at today",
          r["normal_by_now"] == 15, r["normal_by_now"])

    # THE STALENESS CUTOFF. A chip that is honest and months out of date still looks broken.
    check("a record within the window prints", reading(_dt.date(2026, 8, 20), rows, norms))
    check("a record past the window prints nothing",
          reading(_dt.date(2026, 9, 30), rows, norms) is None)
    check("a record dated after today prints nothing",
          reading(_dt.date(2026, 8, 1), rows, norms) is None)
    check("an empty record prints nothing", reading(_dt.date(2026, 8, 14), [], norms) is None)
    check("a missing normals file prints nothing",
          reading(_dt.date(2026, 8, 14), rows, {}) is None)

    # THE WINTER BRANCH IS A REAL BRANCH, not a comment about one.
    wrows = [{"date": f"2026-01-{d:02d}", "tmax_f": 40, "tmin_f": 28} for d in range(1, 16)]
    w = reading(_dt.date(2026, 1, 16), wrows, norms)
    check("the winter chip counts nights at or below freezing", w["count"] == 15, w)
    check("the winter chip measures against the season, not the year", w["hot"] is False)
    check("a January night belongs to the season that began in July",
          w["remaining"] == 17, w["remaining"])

    # A DAY WITH NO READING IS NOT A COOL DAY. The hole is dated inside the range rather than
    # after it, so the last settled day stays put and this tests the counting rather than
    # accidentally testing the staleness cutoff.
    holed = rows + [{"date": "2026-07-20", "tmax_f": None, "tmin_f": None}]
    hr = reading(_dt.date(2026, 8, 14), holed, norms)
    check("a day missing its high is left out rather than counted as a cool day",
          hr["days_measured"] == 18 and hr["count"] == 17, hr)

    # PHRASING, where an automated page most easily gives itself away.
    _, mid, tail = phrasing({**r, "count": 1})
    check("one day is a day and not 1 days", mid.startswith("1 day at"), mid)
    _, mid0, _ = phrasing({**r, "count": 0})
    check("a count of zero reads as words, not as a 0", mid0.startswith("no days"), mid0)
    _, _, t1 = phrasing({**r, "remaining": 1})
    check("one remaining is 1 more and not 1 mores", t1.startswith("1 more in"), t1)
    _, _, t0 = phrasing({**r, "remaining": 0})
    check("nothing remaining reads as a sentence, not as 0 more",
          "none left" in t0 and "0" not in t0, t0)

    # A NORMAL YEAR NEVER HAS A NEGATIVE NUMBER OF DAYS TO COME.
    #
    # Tested at the end of OCTOBER, which is where it actually bites. December is a winter
    # month here, so the hot branch never reaches December at all, and an end-of-December
    # case would have been testing a state the chip cannot be in.
    late = reading(_dt.date(2026, 10, 31),
                   rows + [{"date": "2026-10-31", "tmax_f": 80, "tmin_f": 55}], norms)
    check("the remainder is clamped at zero once a normal year is spent",
          late["remaining"] == 0, late["remaining"])
    check("a spent year still reports the count it measured", late["count"] == 17, late)

    # THE AUTHORISATION SET IS EXACTLY WHAT THE CHIP PRINTS. Checked by rendering the
    # sentence and reading the numerals back out of it, rather than by listing them twice.
    import re as _re
    for case in (r, w):
        place, mid, tail = phrasing(case)
        text = f"{place} {mid.format(through=case['through'].strftime('%B %-d') + 'th')} {tail}"
        printed = {int(x) for x in _re.findall(r"\d+", text)}
        check(f"the {'summer' if case['hot'] else 'winter'} chip authorises every numeral "
              f"it prints", printed <= set(figures(case)), (text, printed, figures(case)))
        check(f"the {'summer' if case['hot'] else 'winter'} chip authorises nothing it does "
              f"not print", set(figures(case)) <= printed, (text, figures(case)))

    print(f"\nheatclock self-test: {'all passed' if not fails else str(len(fails)) + ' FAILED'}")
    return 1 if fails else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(_self_test())
    got = reading(_dt.date.today())
    print(json.dumps(got, indent=1, default=str) if got else "nothing to print")
