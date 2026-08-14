#!/usr/bin/env python3
"""frontchip.py — the front page's one live line, and the rule that decides what it says.

WHAT THE CHIP IS

One computed, dated fact at the top of the front page. The sibling product opens with how much
daylight its state capital has today and how fast it is losing it, and that single detail is
most of why its front page reads as alive rather than published. What makes it work is worth
naming, because it is the specification everything below serves:

    IT IS ABOUT SOMETHING THE READER ALREADY FEELS. Nobody needs the unit explained.
    IT MOVES. Coming back tomorrow shows a different number.
    IT IS A CLOCK, NOT A STATISTIC. It accumulates in one direction and you can feel where
    you are in the season from it.
    IT IS TRUE WITHOUT A CAVEAT.

Texas has no daylight story, so this is the weather Texans already keep score of.

THE ROTATION, WHICH IS THE POINT OF THIS FILE

Four candidates run, and the chip leads with whichever is FURTHEST FROM ITS OWN NORMAL for
today's date. Hundred degree days, freezing nights, nights that never dropped below eighty, and
inches of rain for the year. Nothing here is scheduled by a calendar table. The season falls out
of the climatology, and the chip automatically surfaces whatever is actually unusual today
rather than whatever somebody decided in advance would be interesting in August.

    HOW FOUR DIFFERENT UNITS ARE COMPARED. Days and inches cannot be ranked against each
    other directly. Each candidate's distance is measured in units of its OWN year to year
    variation, so "eleven nights above a normal of nine" beats "three days above a normal of
    thirteen" when the first is a large departure for that metric and the second is noise.
    Hundred degree day counts at this station swing enormously between years, so being a few
    days ahead means very little, and the arithmetic knows that where a human eye would not.

    THE COMPARISON IS NEVER PUBLISHED. The distance decides which candidate leads and then
    it is thrown away. The page prints only what was measured and what is normal, because a
    standard score on a right skewed rainfall distribution is a defensible way to rank four
    things and not a number this project would put its name on. Choosing what to show is
    allowed to use rougher arithmetic than showing it.

    WHY EVERY CANDIDATE IS A RUNNING TOTAL. A chip built on yesterday's high against the
    normal high would be a different number every morning for no reason a reader could feel,
    and rotating on which of four such numbers was most extreme would make it flicker. A
    cumulative count moves slowly and carries the season inside it.

    WHY THE FORM NEVER CHANGES EVEN THOUGH THE SUBJECT DOES. Every candidate renders as
    place, then what has happened by the settled date, then what is normal by then. A reader
    meets the same sentence every day with a different fact in it, so the rotation reads as
    a single instrument rather than as an arbitrary fact generator.

WHY IT COMPARES AGAINST THE LAST SETTLED DAY AND NOT AGAINST TODAY

The observation and the normal are read through the SAME date, which is the last day the record
actually holds. Comparing a count through the 10th against a normal through the 14th would be
comparing unequal windows and would read as the year running cool.

WHAT IT REFUSES TO DO

It never forecasts. It never reaches for today's number from a forecast feed to close the
settling lag, because that would mix a projection into a measured count. It disappears rather
than going stale, see STALE_AFTER_DAYS.
"""
from __future__ import annotations

import datetime as _dt
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

LEDGER = REPO_ROOT / "ledger" / "gridwatch" / "weather.jsonl"
NORMALS = REPO_ROOT / "config" / "gridwatch" / "weather_normals.json"
DROUGHT_LEDGER = REPO_ROOT / "ledger" / "gridwatch" / "drought.jsonl"
DROUGHT_NORMALS = REPO_ROOT / "config" / "gridwatch" / "drought_normals.json"

# The record settles a few days behind real time and the collector runs daily, so a gap wider
# than this means the collector has been broken for a fortnight rather than that NCEI is
# quality controlling. At that point the honest thing is to show nothing. A chip reading "by
# March 3rd" in August is accurate and still looks broken, which costs more trust than the
# line earns.
STALE_AFTER_DAYS = 21

# WHEN A CANDIDATE IS IN SEASON, DERIVED FROM ITS OWN NORMAL RATHER THAN FROM A CALENDAR.
#
# A candidate is eligible while its normal is between these two fractions of a full cycle. The
# floor keeps out a metric that has barely started, where a single event swings the total and
# the comparison says nothing: two hundred degree days in June is not a heatwave, it is June.
# The ceiling retires a metric whose season is climatologically over, so a finished winter's
# freeze count stops competing in May.
#
# Both are properties of the metric's own accumulation curve, so adding a candidate needs no
# window written for it anywhere. `_self_test` walks all 366 days and asserts the chip is
# never left with nothing to say, which is the real constraint these two numbers have to meet.
SEASON_FLOOR = 0.10
SEASON_CEIL = 0.98

# Ranking is by distance, and this settles exact ties so a rebuild is byte identical. Two
# candidates matching to the full float is vanishingly unlikely and "vanishingly unlikely"
# is how a build becomes non-deterministic and a freshness gate starts flapping.
ORDER = ("hot", "cold", "warm", "rain", "drought")

# `None` already means something to `candidates`: read the real drought ledger. So "the caller
# said nothing" needs its own value, and it cannot be None or False without colliding with the
# two states that already have meanings.
_UNSET = object()

# How each candidate reads. `noun` takes (singular, plural); `qualifier` follows the count.
VOICE = {
    "hot":  dict(noun=("day", "days"), qualifier="at {threshold}"),
    "cold": dict(noun=("night", "nights"), qualifier="at freezing"),
    "warm": dict(noun=("night", "nights"), qualifier="over {threshold}"),
    "rain": dict(noun=("inch", "inches"), qualifier="of rain"),
}

# THE FIFTH CANDIDATE IS A DIFFERENT KIND OF THING, and the code says so rather than pretending.
#
# The four above are TOTALS: they accumulate through a cycle and only ever climb, which is what
# makes them read as a clock. Drought is a LEVEL. It is a share of the state on one day, it can
# fall as easily as rise, and it has no cycle to accumulate through.
#
# A level was ruled out of this rotation once, and the reason was flicker: a number that moves
# every morning for no reason a reader can feel makes the chip jump between subjects. That
# reason does not apply here. The Drought Monitor publishes ONCE A WEEK, so this figure is
# constant for seven days at a time and moves by a few points when it moves at all. The rule
# the rotation actually needs is that a candidate be SLOW, and accumulation was only ever one
# way of being slow.
#
# It also cannot use the season gate, which asks how far a total has come through its cycle.
# Drought is in season in Texas every week of the year. It is gated on having a fresh map and
# a week with enough years behind it instead.
DROUGHT_STALE_AFTER_DAYS = 21
# Whole percent. The feed carries two decimals and a tenth of a percent of Texas is noise at
# the scale of a headline, which is why the Drought Monitor's own summaries quote whole points.
DROUGHT_DP = 0

# Rounding is a computation with a stated rule. Counts are whole days. Rain is a tenth of an
# inch, which is the finest reading a rain gauge is quoted at and coarser than the noise in a
# yearly total.
RAIN_DP = 1


def load(path: Path = LEDGER) -> list[dict]:
    if not path.exists():
        return []
    rows = [json.loads(t) for t in (s.strip() for s in path.read_text().splitlines()) if t]
    rows.sort(key=lambda r: r["date"])
    return rows


def normals(path: Path = NORMALS) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def drought_rows(path: Path = DROUGHT_LEDGER) -> list[dict]:
    if not path.exists():
        return []
    rows = [json.loads(t) for t in (s.strip() for s in path.read_text().splitlines()) if t]
    rows.sort(key=lambda r: r["valid_start"])
    return rows


def drought_normals(path: Path = DROUGHT_NORMALS) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def drought_candidate(today: _dt.date, rows: list[dict] | None = None,
                      norms: dict | None = None) -> dict | None:
    """The share of Texas in drought, against its own normal for that week of the year.

    THE FIRST SEGMENT NAMES THE DROUGHT MONITOR WHERE THE WEATHER LINES NAME A STATION, and
    that is a rule rather than a flourish. This figure is a panel's classification, not an
    instrument reading, and the research that admitted it to this rotation admitted it on the
    condition that it is attributed every time it is shown. The segment answers "whose number
    is this", which happens to be the honest question for the weather candidates too.

    IT CARRIES THE MAP'S DATE, NEVER TODAY'S. A map covers the week ending on its Tuesday and
    publishes on the Thursday after, so stamping it with today would claim a currency the
    classification does not have.
    """
    rows = drought_rows() if rows is None else rows
    norms = drought_normals() if norms is None else norms
    if not rows or not norms.get("by_week"):
        return None
    last = rows[-1]
    when = _dt.date.fromisoformat(last["valid_start"])
    if (today - when).days > DROUGHT_STALE_AFTER_DAYS or when > today:
        return None
    stats = norms["by_week"].get(str(when.isocalendar()[1]))
    if not stats:
        return None
    mean, sd = stats[0], stats[1]
    value = last.get("in_drought_pct")
    if value is None or sd <= 0:
        return None
    return {"key": "drought", "value": float(value), "mean": float(mean), "sd": float(sd),
            "unit": "percent", "threshold": None,
            "distance": abs(float(value) - float(mean)) / float(sd),
            "through": when, "place": norms.get("source", "US Drought Monitor")}


def _cycle_year(d: _dt.date, cycle: str, start_month: int) -> int:
    if cycle == "year":
        return d.year
    return d.year if d.month >= start_month else d.year - 1


def observed(rows: list[dict], key: str, spec: dict, last: _dt.date, start_month: int) -> float:
    """What this metric actually holds for the cycle `last` falls in, through `last`.

    A DAY WITH NO OBSERVATION IS SKIPPED, NEVER COUNTED AS BELOW THE THRESHOLD. A missing
    high is not a cool day and a missing gauge reading is not a dry one.
    """
    cyc = _cycle_year(last, spec["cycle"], start_month)
    total = 0.0
    for r in rows:
        d = _dt.date.fromisoformat(r["date"])
        if d > last or _cycle_year(d, spec["cycle"], start_month) != cyc:
            continue
        v = r.get({"hot": "tmax_f", "cold": "tmin_f",
                   "warm": "tmin_f", "rain": "prcp_in"}[key])
        if v is None:
            continue
        if key == "rain":
            total += v
        elif key == "cold":
            total += 1 if v <= spec["threshold"] else 0
        else:
            total += 1 if v >= spec["threshold"] else 0
    return total


def candidates(today: _dt.date, rows: list[dict] | None = None,
               norms: dict | None = None, drought=_UNSET) -> list[dict]:
    """Every candidate that is in season today, with its measured value and its normal.

    Returned sorted by distance, furthest first. The caller takes the head.

    HERMETIC BY THE SHAPE OF THE CALL, and it was not, which broke five of its own tests the
    day the drought candidate was added. A caller that hands in `rows` or `norms` is running a
    scenario, and a scenario that reaches out to `ledger/gridwatch/drought.jsonl` is not a
    scenario, it is the live rotation wearing a fixture. The synthetic tests asserted that two
    candidates ran and got three, the third being real Texas drought data with a real distance
    that reordered the result. Passing `drought` explicitly still wins over this, so a test
    that wants to exercise the drought path says so with a tuple and one that wants it gone
    says `False`.
    """
    rows_given, norms_given = rows, norms
    rows = load() if rows is None else rows
    norms = normals() if norms is None else norms
    if not rows or not norms.get("metrics"):
        return []

    last = _dt.date.fromisoformat(max(r["date"] for r in rows))
    if (today - last).days > STALE_AFTER_DAYS or last > today:
        return []

    start_month = norms.get("season_start_month", 7)
    key_md = f"{last.month:02d}-{last.day:02d}"
    out = []
    for key in ORDER:
        spec = norms["metrics"].get(key)
        if not spec or key_md not in spec["through"]:
            continue
        mean, sd = spec["through"][key_md]
        full = spec["full"] or 0.0
        if sd <= 0 or full <= 0:
            continue
        progress = mean / full
        if not (SEASON_FLOOR <= progress <= SEASON_CEIL):
            continue
        value = observed(rows, key, spec, last, start_month)
        out.append({
            "key": key, "value": value, "mean": mean, "sd": sd,
            "unit": spec["unit"], "threshold": spec["threshold"],
            "distance": abs(value - mean) / sd,
            "through": last, "place": norms["station_name"],
        })
    # The level candidate runs beside the totals and is ranked by the same distance. It reads
    # its own record and its own normals, so a missing drought file costs the rotation one
    # candidate and nothing else.
    if drought is _UNSET:
        drought = None if (rows_given is None and norms_given is None) else False
    if drought is not False:
        d = drought_candidate(today, *drought) if isinstance(drought, tuple) \
            else drought_candidate(today)
        if d:
            out.append(d)
    out.sort(key=lambda c: (-c["distance"], ORDER.index(c["key"])))
    return out


def reading(today: _dt.date, rows: list[dict] | None = None,
            norms: dict | None = None) -> dict | None:
    """The winning candidate, or None when the chip must print nothing."""
    got = candidates(today, rows, norms)
    return got[0] if got else None


def _fmt(value: float, unit: str) -> str:
    if unit == "inches":
        return f"{value:.{RAIN_DP}f}"
    if unit == "percent":
        return f"{value:.{DROUGHT_DP}f}"
    return str(int(round(value)))


def phrasing(r: dict) -> tuple[str, str, str]:
    """The chip's three segments as plain text, with `{through}` left for the caller.

    Singular and plural are computed rather than assumed. "1 days at 100" is the kind of
    detail that makes an otherwise careful page look automated, which is exactly what it is
    and exactly what it must not look like.
    """
    if r["key"] == "drought":
        # "on", not "by". A total is a count THROUGH a date; this is a reading TAKEN on one.
        return (r["place"],
                f'{_fmt(r["value"], r["unit"])}% of Texas in drought on {{through}}',
                f'normal is {_fmt(r["mean"], r["unit"])}')
    v = VOICE[r["key"]]
    shown = _fmt(r["value"], r["unit"])
    # Plural on the VALUE AS PRINTED, not on the raw number. Rain rounds to one decimal, and
    # "1.0 inch" is wrong where "1 inch" is right, so the test is whether the printed string
    # is exactly one.
    one = shown in ("1", "1.0")
    noun = v["noun"][0] if one else v["noun"][1]
    qual = v["qualifier"].format(threshold=r["threshold"])

    middle = (f"no {v['noun'][1]} {qual} by {{through}}" if r["value"] == 0
              else f"{shown} {noun} {qual} by {{through}}")
    tail = f"normal is {_fmt(r['mean'], r['unit'])}"
    return r["place"], middle, tail


def figures(r: dict) -> list:
    """Exactly the numerals the chip prints, for the front page's authorisation set.

    THE SAME CALL THAT DRAWS IT AUTHORISES IT. The alternative is writing the rounding rule
    down a second time in the lint's allowlist, and two copies of a rounding rule is one copy
    and one bug waiting.

    EXACTLY WHAT IT PRINTS, not everything it holds. An allowlist is a gate, and every value
    on it that no copy actually uses is a numeral the lint waves through somewhere else. The
    distance that chose this candidate is deliberately absent, because it is never shown.
    """
    out = [_fmt(r["value"], r["unit"]), _fmt(r["mean"], r["unit"]), str(r["through"].day)]
    if r["threshold"] is not None and "{threshold}" in VOICE[r["key"]]["qualifier"]:
        out.append(str(r["threshold"]))
    return out


# --------------------------------------------------------------------------- self-test
def _self_test() -> int:
    fails = []

    def check(label, cond, extra=""):
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}" + ("" if cond else f"  {extra}"))
        if not cond:
            fails.append(label)

    def norm(through_pairs, full, cycle="year", unit="count", threshold=100):
        return {"cycle": cycle, "unit": unit, "threshold": threshold,
                "through": through_pairs, "full": full, "cycles_used": 30}

    # A synthetic pair where the SMALLER raw departure is the LARGER real one, which is the
    # whole reason the ranking is not done on raw difference.
    norms = {
        "station_name": "Dallas Fort Worth", "season_start_month": 7,
        "metrics": {
            # hot sits 4 above a normal of 13, on a metric that swings by 12 between years.
            # warm sits only 2 above a normal of 15, on one that barely moves. The SMALLER
            # raw gap is the larger real departure, and warm must win.
            "hot":  norm({"08-10": [13.0, 12.0]}, 20.0, threshold=100),
            "warm": norm({"08-10": [15.0, 0.5]}, 20.0, threshold=80),
        },
    }
    rows = ([{"date": f"2026-07-{d:02d}", "tmax_f": 101, "tmin_f": 81, "prcp_in": 0.0}
             for d in range(1, 18)]
            + [{"date": "2026-08-10", "tmax_f": 99, "tmin_f": 70, "prcp_in": 0.0}])
    got = candidates(_dt.date(2026, 8, 14), rows, norms)
    check("both in-season candidates run", [c["key"] for c in got] == ["warm", "hot"],
          [(c["key"], round(c["distance"], 2)) for c in got])
    check("the larger departure wins even though its raw gap is smaller",
          got[0]["key"] == "warm" and got[0]["value"] - got[0]["mean"]
          < got[1]["value"] - got[1]["mean"],
          [(c["key"], c["value"] - c["mean"], round(c["distance"], 2)) for c in got])

    # SEASON GATING, derived from the normal rather than from a month.
    early = {"station_name": "X", "season_start_month": 7,
             "metrics": {"hot": norm({"08-10": [0.5, 1.0]}, 20.0)}}          # 2.5% of a cycle
    check("a metric that has barely started is out of season",
          candidates(_dt.date(2026, 8, 14), rows, early) == [])
    done = {"station_name": "X", "season_start_month": 7,
            "metrics": {"hot": norm({"08-10": [19.9, 4.0]}, 20.0)}}          # 99.5%
    check("a metric whose season is climatologically over is retired",
          candidates(_dt.date(2026, 8, 14), rows, done) == [])
    flat = {"station_name": "X", "season_start_month": 7,
            "metrics": {"hot": norm({"08-10": [10.0, 0.0]}, 20.0)}}
    check("a metric with no year to year spread cannot be ranked and is skipped",
          candidates(_dt.date(2026, 8, 14), rows, flat) == [])

    # THE DROUGHT CANDIDATE, EXERCISED ON PURPOSE.
    # It used to be exercised by accident: `candidates` read the real ledger even when handed a
    # fixture, so these synthetic scenarios silently ranked live Texas drought data alongside
    # two made up metrics, and five checks broke the day that data moved. Making the scenarios
    # hermetic fixed those five and left this path with no coverage at all, which is the worse
    # of the two states because it is the quiet one. So it is passed in explicitly here.
    dnorm = {"by_week": {"33": [40.0, 10.0]}}                  # week 33 normal, 40 percent, sd 10
    drow = [{"valid_start": "2026-08-11", "in_drought_pct": 92.0}]      # 5.2 sd above normal
    withd = candidates(_dt.date(2026, 8, 14), rows, norms, drought=(drow, dnorm))
    check("drought ranks beside the weather candidates and can beat them",
          [c["key"] for c in withd][0] == "drought",
          [(c["key"], round(c["distance"], 2)) for c in withd])
    check("a drought record past its window is dropped rather than carried forward",
          candidates(_dt.date(2026, 10, 1), rows, norms,
                     drought=(drow, dnorm)) == candidates(_dt.date(2026, 10, 1), rows, norms,
                                                          drought=False))
    check("a week with no published normal cannot be ranked and is skipped",
          [c["key"] for c in candidates(_dt.date(2026, 8, 14), rows, norms,
                                        drought=(drow, {"by_week": {"9": [40.0, 10.0]}}))]
          == ["warm", "hot"])
    dhead, dmid, dtail = phrasing(withd[0])
    check("the drought line names the Drought Monitor first, where a weather line names a station",
          "Drought Monitor" in dhead, dhead)
    check("the drought line carries the map's own date and not today's",
          withd[0]["through"] == _dt.date(2026, 8, 11) and "{through}" in dmid,
          (withd[0]["through"], dmid))
    check("the drought line prints a whole percent against a whole normal",
          dmid.startswith("92% of Texas in drought") and dtail == "normal is 40", (dmid, dtail))
    # A scenario is hermetic unless it says otherwise, and that is what the five broken checks
    # bought. Asserted, so it cannot quietly revert to reading the repository.
    check("a scenario never reaches the real drought ledger unless it asks to",
          [c["key"] for c in candidates(_dt.date(2026, 8, 14), rows, norms)] == ["warm", "hot"])

    # STALENESS AND EMPTINESS.
    check("a record within the window prints", reading(_dt.date(2026, 8, 20), rows, norms))
    check("a record past the window prints nothing",
          reading(_dt.date(2026, 9, 30), rows, norms) is None)
    check("a record dated after today prints nothing",
          reading(_dt.date(2026, 8, 1), rows, norms) is None)
    check("an empty record prints nothing", reading(_dt.date(2026, 8, 14), [], norms) is None)
    check("missing normals print nothing", reading(_dt.date(2026, 8, 14), rows, {}) is None)

    # A MISSING OBSERVATION IS NOT A COOL DAY AND NOT A DRY ONE.
    holed = rows + [{"date": "2026-07-20", "tmax_f": None, "tmin_f": None, "prcp_in": None}]
    check("a day with no reading changes no total",
          reading(_dt.date(2026, 8, 14), holed, norms)["value"]
          == reading(_dt.date(2026, 8, 14), rows, norms)["value"])

    # THE TOTAL IS SCOPED TO THE CYCLE THE SETTLED DAY FALLS IN.
    spill = rows + [{"date": "2025-07-05", "tmax_f": 105, "tmin_f": 85, "prcp_in": 0.0}]
    check("last year's heat does not count toward this year",
          reading(_dt.date(2026, 8, 14), spill, norms)["value"]
          == reading(_dt.date(2026, 8, 14), rows, norms)["value"])

    # A SEASON METRIC CARRIES ACROSS NEW YEAR.
    wnorms = {"station_name": "X", "season_start_month": 7,
              "metrics": {"cold": norm({"01-15": [9.0, 3.0]}, 29.0,
                                       cycle="season", threshold=32)}}
    wrows = ([{"date": f"2025-12-{d:02d}", "tmin_f": 30} for d in range(20, 32)]
             + [{"date": f"2026-01-{d:02d}", "tmin_f": 28} for d in range(1, 16)])
    w = reading(_dt.date(2026, 1, 16), wrows, wnorms)
    check("a freeze count spans December and January as one season",
          w and w["value"] == 27, w)

    # PHRASING, where an automated page most easily gives itself away.
    _, mid, tail = phrasing({**got[0], "value": 1})
    check("one night is a night and not 1 nights", mid.startswith("1 night over"), mid)
    _, mid0, _ = phrasing({**got[0], "value": 0})
    check("a count of zero reads as words, not as a 0", mid0.startswith("no nights"), mid0)
    r1 = {**got[0], "key": "rain", "unit": "inches", "value": 1.0, "mean": 22.68,
          "threshold": None}
    _, midr, tailr = phrasing(r1)
    check("one inch is an inch and not 1.0 inches", midr.startswith("1.0 inch of rain"), midr)
    check("rain prints to a tenth and its normal matches", tailr == "normal is 22.7", tailr)
    check("the rain line carries no threshold numeral", "100" not in midr and "80" not in midr)

    # THE AUTHORISATION SET IS EXACTLY WHAT IS PRINTED, checked by reading the numerals back
    # out of the rendered sentence rather than by listing them twice.
    import re as _re
    for case in (got[0], got[1], r1, w):
        place, mid_, tail_ = phrasing(case)
        # THE CASE'S OWN SETTLED DATE, not a fixed string. Formatting every case with the
        # same "August 10th" made this pass for three candidates and fail for the winter one
        # purely because the harness printed a day the candidate had never claimed.
        stamp = f"{case['through'].strftime('%B')} {case['through'].day}th"
        text = f"{place} {mid_.format(through=stamp)} {tail_}"
        printed = set(_re.findall(r"\d+(?:\.\d+)?", text))
        auth = set(figures(case))
        check(f"the {case['key']} line authorises every numeral it prints",
              printed <= auth, (text, printed - auth))
        check(f"the {case['key']} line authorises nothing it does not print",
              auth <= printed, (text, auth - printed))

    # THE REAL CONSTRAINT ON THE SEASON BAND: the chip is never left with nothing to say.
    # Walked over the shipped normals, one day at a time, all the way round the year.
    live = normals()
    if live.get("metrics"):
        empty, counts = [], {}
        for i in range(366):
            d = _dt.date(2026, 1, 1) + _dt.timedelta(days=i)
            md = f"{d.month:02d}-{d.day:02d}"
            n = 0
            for k in ORDER:
                m = live["metrics"].get(k)
                if not m or md not in m["through"]:
                    continue
                mean, sd = m["through"][md]
                if sd > 0 and m["full"] > 0 and SEASON_FLOOR <= mean / m["full"] <= SEASON_CEIL:
                    n += 1
            counts[md] = n
            if n == 0:
                empty.append(md)
        check("every day of the year has at least one candidate in season",
              not empty, f"{len(empty)} empty: {empty[:6]}")
        check("at least one day of the year has a real contest",
              max(counts.values()) >= 2, max(counts.values()))

    print(f"\nfrontchip self-test: {'all passed' if not fails else str(len(fails)) + ' FAILED'}")
    return 1 if fails else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(_self_test())
    got = candidates(_dt.date.today())
    for c in got:
        print(f'  {c["key"]:5} value={c["value"]:<8} normal={c["mean"]:<8} '
              f'distance={c["distance"]:.2f}')
    if got:
        p, m, t = phrasing(got[0])
        print("\n  " + " | ".join([p, m.format(through="<date>"), t]))
