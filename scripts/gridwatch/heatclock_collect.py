#!/usr/bin/env python3
"""heatclock_collect.py — the observed daily extremes at the anchor station, and their normals.

WHAT THIS IS FOR

The front page opens with one live, computed, dated line about the physical world. The sibling
product opens with how much daylight its state capital has left today and how fast it is
losing it, and that single detail is most of why its front page reads as alive rather than
published. It works because it is true, it is about a real place, and it is different every
morning.

Texas has no daylight story. Its felt seasonal clock is heat, and the unit Texans actually
count in is the hundred degree day. So this collects the observed daily maximum and minimum at
one anchor station and the site counts days at or above 100, against what a normal year holds
by the same date. In the cold half of the year the same clock counts nights at or below
freezing, which is the other extreme Texas counts and the reason it argues about the grid at
all.

WHY THIS COLLECTOR IS SHAPED NOTHING LIKE THE ERCOT ONE

`gridwatch_collect.py` exists under a permanent emergency: ERCOT's dashboard feeds are rolling
windows with no archive, so a missed day is gone from here and from everywhere. Every design
choice there follows from that.

NONE OF IT APPLIES HERE, and copying it would be cargo cult. NCEI's `daily-summaries` service
is the archive. It serves any station and any date range back to the nineteenth century, it is
United States government work in the public domain, and it needs no key. Three consequences,
each the opposite of the grid collector's:

  A MISSED DAY COSTS NOTHING. This fetches a trailing window and fills whatever is absent, so
  a cron that fails for a week catches up completely on the next run. There is no recovery
  lever here because there is nothing to recover.

  NO RAW SNAPSHOT IS KEPT. The grid collector gzips every response before parsing it, because
  a parser found to be wrong later has no other route back to the source bytes. Here the source
  bytes are re-fetchable forever by the same URL, so a snapshot would be a redundant copy of a
  permanent archive, committed daily, growing without end. The URL in each record is the
  snapshot.

  IT IS NOT THE PROJECT'S IRREPLACEABLE JOB. It may fail, loudly, and nothing is lost.

WHY THE RECORD LAGS, AND WHY THAT IS PUBLISHED RATHER THAN PAPERED OVER

Daily summaries settle a few days behind real time, because the observation is quality
controlled before it is published. So the count this drives is a count THROUGH the last settled
day, and the site prints that date beside it. Reaching for today's number from a forecast feed
would mix a projection into a measured count, which is the one thing the grid watch was built
never to do.

WHAT THE NORMALS ARE

The 1991 to 2020 period, which is the current standard climate normals base, computed from the
same daily record this collects, so a reader can recompute both from one source. They are DATA,
in `config/gridwatch/heat_normals.json`, so a rebase to a new period is a data change with its
own commit and never a code change.

    heatclock_collect.py --self-test    hermetic, no network, gates every collection
    heatclock_collect.py --collect      fill any gap in the trailing window
    heatclock_collect.py --normals      recompute the normals file from 30 years
"""
from __future__ import annotations

import argparse
import calendar
import datetime as _dt
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "ledger" / "gridwatch" / "heat.jsonl"
NORMALS = REPO_ROOT / "config" / "gridwatch" / "heat_normals.json"

SERVICE = "https://www.ncei.noaa.gov/access/services/data/v1"

# THE ANCHOR IS ONE STATION AND IT IS NAMED ON THE PAGE.
#
# Dallas Fort Worth International, the reference station for the largest metropolitan area in
# Texas, and the hundred degree count the state's own newsrooms quote every summer.
#
# Picking the station is the one judgement call in this file, so it is made once, in the open,
# on a stated rule: the largest metro's official station. It is emphatically NOT chosen for
# giving the most dramatic number. Wichita Falls runs hotter against its normal most summers,
# and selecting a station because its figure is more striking would be the exact dishonesty
# this project's numbers law exists to prevent.
#
# ONLY ONE STATION IS COLLECTED, deliberately. The grid collector hoards every series it can
# reach because ERCOT keeps no archive. Here, adding a station later costs one backfill against
# a permanent public archive, so collecting stations against a use nobody has yet would buy
# nothing and commit us to maintaining them.
STATION = "USW00003927"
STATION_NAME = "Dallas Fort Worth"

# The thresholds the clock counts in, in whole degrees Fahrenheit. Both are the round numbers
# the public already counts in, which is the entire point of the chip: it reports the thing
# people were already keeping score of.
HOT_F = 100      # a day is "hot" when the high reaches this
COLD_F = 32      # a night is "freezing" when the low reaches this

# The freeze season runs July to June so a single winter is one season rather than two halves
# split at New Year. A count of freezing nights that resets on January 1st, in the middle of
# the only season that produces them, would be a number about the calendar and not the weather.
SEASON_START_MONTH = 7

# The current standard base period for United States climate normals.
NORMALS_BASE = (1991, 2020)

# Coverage below this fraction of days in a year disqualifies that year from the normals. A
# station outage does not make a year cold, it makes it unmeasured, and averaging an
# unmeasured year in as though it were a mild one biases every normal downward.
MIN_YEAR_COVERAGE = 0.95

UA = ("TexasAIDocket/1.0 (+https://talonsturgill.github.io/TexasAIDocket; "
      "daily public-interest climate record; one request per day)")

SPEC = 1


# --------------------------------------------------------------------------- calendar keys
def year_keys() -> list[str]:
    """Every month-day in calendar order, including February 29th.

    KEYED BY MONTH AND DAY, NEVER BY DAY OF YEAR. Day 60 is March 1st in a common year and
    February 29th in a leap year, so a normals table indexed by ordinal silently compares
    March against February for three years in every four.
    """
    return [f"{m:02d}-{d:02d}"
            for m in range(1, 13)
            for d in range(1, calendar.monthrange(2024, m)[1] + 1)]


def season_keys() -> list[str]:
    """The same keys rotated to start at the freeze season's first day."""
    keys = year_keys()
    start = keys.index(f"{SEASON_START_MONTH:02d}-01")
    return keys[start:] + keys[:start]


def season_of(day: _dt.date) -> int:
    """The freeze season a date belongs to, named for the year it started in."""
    return day.year if day.month >= SEASON_START_MONTH else day.year - 1


# --------------------------------------------------------------------------- fetch
def fetch(start: str, end: str, station: str = STATION, timeout: int = 60) -> bytes:
    q = urllib.parse.urlencode({
        "dataset": "daily-summaries",
        "stations": station,
        "startDate": start,
        "endDate": end,
        "dataTypes": "TMAX,TMIN",
        "units": "standard",
        "format": "json",
    })
    url = f"{SERVICE}?{q}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# --------------------------------------------------------------------------- parse
def parse(raw: bytes) -> list[dict]:
    """Observed daily extremes, one row per day that actually carries a reading.

    A DAY WITH NO READING IS ABSENT, NEVER ZERO. NCEI returns the field as an empty string
    when an observation did not pass quality control, and `float("")` raises while a bare
    `or 0` would file a missing summer day as a low of zero degrees. Either would be a
    fabricated measurement, so a row missing both values is dropped and a row missing one
    keeps the other as None.

    The service returns an empty list for a range it holds nothing for, which is a legitimate
    answer and not an error.
    """
    doc = json.loads(raw)
    if not isinstance(doc, list):
        raise ValueError("daily-summaries did not return a list of rows")

    out = []
    for row in doc:
        if not isinstance(row, dict):
            continue
        date = str(row.get("DATE") or "")[:10]
        if len(date) != 10 or date[4] != "-":
            continue

        def num(field):
            v = row.get(field)
            if v is None or str(v).strip() == "":
                return None
            try:
                return int(round(float(v)))
            except (TypeError, ValueError):
                return None

        hi, lo = num("TMAX"), num("TMIN")
        if hi is None and lo is None:
            continue
        out.append({
            "_spec": SPEC,
            "date": date,
            "station": str(row.get("STATION") or STATION),
            "tmax_f": hi,
            "tmin_f": lo,
            "source": "ncei daily-summaries",
            "verified": True,
        })
    out.sort(key=lambda r: r["date"])
    return out


# --------------------------------------------------------------------------- ledger
def load(path: Path = LEDGER) -> list[dict]:
    """Every reading held, oldest first.

    SORTED ON READ RATHER THAN ASSUMED. This ledger is append only, and gap filling appends a
    date older than the last line whenever a backfill lands after a newer reading. That is
    correct and it means file order is not date order, so anything reading "the latest" off
    the last line would be reading whatever was written last.
    """
    if not path.exists():
        return []
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    rows.sort(key=lambda r: r["date"])
    return rows


def append(rows: list[dict], path: Path = LEDGER) -> int:
    """Add only dates the ledger does not already hold. Never rewrite a settled line."""
    held = {r["date"] for r in load(path)}
    fresh = [r for r in rows if r["date"] not in held]
    if not fresh:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        for r in sorted(fresh, key=lambda r: r["date"]):
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    return len(fresh)


# --------------------------------------------------------------------------- normals
def build_normals(rows: list[dict]) -> dict:
    """Cumulative mean counts of hot days and freezing nights, by month and day.

    For each month-day key, the mean across the base period of how many qualifying days that
    year or season had held BY that date. The site subtracts the by-date figure from the
    full-period figure to say how many a normal year has left, which is the forward-looking
    half of the chip and the part that makes it a clock rather than a statistic.

    YEARS WITH THIN COVERAGE ARE EXCLUDED, NOT PATCHED. See MIN_YEAR_COVERAGE.
    """
    lo_y, hi_y = NORMALS_BASE
    by_year: dict[int, dict[str, dict]] = {}
    for r in rows:
        d = _dt.date.fromisoformat(r["date"])
        by_year.setdefault(d.year, {})[f"{d.month:02d}-{d.day:02d}"] = r

    hot_years, cold_seasons = [], []
    for y in range(lo_y, hi_y + 1):
        days = by_year.get(y, {})
        expected = 366 if calendar.isleap(y) else 365
        if len(days) / expected >= MIN_YEAR_COVERAGE:
            hot_years.append(y)

    # A freeze season spans two calendar years, so it needs both of them measured.
    for s in range(lo_y, hi_y):
        if s in hot_years and (s + 1) in hot_years:
            cold_seasons.append(s)

    if not hot_years or not cold_seasons:
        raise ValueError("no year in the base period has usable coverage")

    def cumulative(keys, years, pick_year, field, hit):
        """Mean cumulative count across `years`, walking `keys` in order."""
        table = {}
        running = {y: 0 for y in years}
        for key in keys:
            for y in years:
                mm, dd = (int(x) for x in key.split("-"))
                cal_year = pick_year(y, mm)
                if mm == 2 and dd == 29 and not calendar.isleap(cal_year):
                    continue
                row = by_year.get(cal_year, {}).get(key)
                if row and row.get(field) is not None and hit(row[field]):
                    running[y] += 1
            table[key] = round(sum(running.values()) / len(years), 3)
        return table

    hot = cumulative(year_keys(), hot_years, lambda y, mm: y,
                     "tmax_f", lambda v: v >= HOT_F)
    cold = cumulative(season_keys(), cold_seasons,
                      lambda y, mm: y if mm >= SEASON_START_MONTH else y + 1,
                      "tmin_f", lambda v: v <= COLD_F)

    return {
        "_spec": SPEC,
        "station": STATION,
        "station_name": STATION_NAME,
        "source": "ncei daily-summaries",
        "base_period": list(NORMALS_BASE),
        "hot_threshold_f": HOT_F,
        "cold_threshold_f": COLD_F,
        "season_start_month": SEASON_START_MONTH,
        "hot_years_used": len(hot_years),
        "cold_seasons_used": len(cold_seasons),
        "hot_through": hot,
        "cold_through": cold,
        "hot_full_year": hot[year_keys()[-1]],
        "cold_full_season": cold[season_keys()[-1]],
    }


# --------------------------------------------------------------------------- commands
def collect(window_days: int = 45) -> int:
    """Fill every gap in the trailing window. Idempotent, and a no-op once caught up."""
    today = _dt.date.today()
    start = today - _dt.timedelta(days=window_days)
    rows = parse(fetch(start.isoformat(), today.isoformat()))
    n = append(rows)
    held = load()
    print(f"heatclock: {n} new reading(s); ledger holds {len(held)}"
          + (f", through {held[-1]['date']}" if held else ""))
    return 0


def normals() -> int:
    lo, hi = NORMALS_BASE
    print(f"heatclock: fetching {lo} to {hi} for {STATION}, this takes a moment")
    rows = parse(fetch(f"{lo}-01-01", f"{hi}-12-31"))
    doc = build_normals(rows)
    NORMALS.parent.mkdir(parents=True, exist_ok=True)
    NORMALS.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    print(f"heatclock: normals from {len(rows)} daily records "
          f"({doc['hot_years_used']} years, {doc['cold_seasons_used']} seasons); "
          f"a normal year holds {doc['hot_full_year']} days at {HOT_F} "
          f"and {doc['cold_full_season']} nights at {COLD_F}")
    return 0


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    """Hermetic. Every case is a defect this collector could actually ship."""
    fails = []

    def check(label, cond, extra=""):
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}" + ("" if cond else f"  {extra}"))
        if not cond:
            fails.append(label)

    # A MISSING OBSERVATION IS NOT A COLD DAY. NCEI sends "" for a value that failed quality
    # control, and both `float("")` and a bare `or 0` are wrong in opposite directions.
    raw = json.dumps([
        {"DATE": "2026-07-01", "STATION": STATION, "TMAX": "101", "TMIN": "78"},
        {"DATE": "2026-07-02", "STATION": STATION, "TMAX": "", "TMIN": "76"},
        {"DATE": "2026-07-03", "STATION": STATION, "TMAX": "", "TMIN": ""},
        {"DATE": "2026-07-04", "STATION": STATION, "TMAX": "99.6", "TMIN": "75"},
    ]).encode()
    rows = parse(raw)
    check("a day missing both values is dropped", len(rows) == 3, [r["date"] for r in rows])
    check("a day missing one value keeps the other",
          rows[1]["tmax_f"] is None and rows[1]["tmin_f"] == 76, rows[1])
    check("a missing high is never read as zero",
          all(r["tmax_f"] is None or r["tmax_f"] > 50 for r in rows), rows)
    check("a fractional degree rounds rather than truncating toward zero",
          rows[2]["tmax_f"] == 100, rows[2])

    check("an empty range is an answer, not a crash", parse(b"[]") == [])

    # APPEND ONLY, AND GAPS FILL IN THE MIDDLE.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "heat.jsonl"
        append([{"date": "2026-07-01", "tmax_f": 101, "tmin_f": 78},
                {"date": "2026-07-03", "tmax_f": 103, "tmin_f": 79}], p)
        first = p.read_text()
        n = append([{"date": "2026-07-01", "tmax_f": 999, "tmin_f": 999},
                    {"date": "2026-07-02", "tmax_f": 102, "tmin_f": 77}], p)
        check("a settled date is never rewritten", n == 1 and "999" not in p.read_text())
        check("the lines already written are untouched", p.read_text().startswith(first))
        got = load(p)
        check("a backfilled gap reads back in date order",
              [r["date"] for r in got] == ["2026-07-01", "2026-07-02", "2026-07-03"],
              [r["date"] for r in got])

    # THE CALENDAR KEYS.
    yk, sk = year_keys(), season_keys()
    check("the year holds 366 keys including February 29th",
          len(yk) == 366 and "02-29" in yk, len(yk))
    check("the freeze season starts in July and ends in June",
          sk[0] == "07-01" and sk[-1] == "06-30" and len(sk) == 366, (sk[0], sk[-1]))
    check("a January date belongs to the season that began the previous July",
          season_of(_dt.date(2026, 1, 9)) == 2025 and season_of(_dt.date(2026, 8, 9)) == 2026)

    # THE NORMALS, BUILT FROM A SYNTHETIC RECORD WHOSE ANSWER IS KNOWN.
    synth = []
    for y in range(NORMALS_BASE[0], NORMALS_BASE[1] + 1):
        d = _dt.date(y, 1, 1)
        while d.year == y:
            # Exactly two hot days a year, on July 1st and August 1st, and exactly one
            # freezing night a season, on January 15th.
            hot = (d.month, d.day) in ((7, 1), (8, 1))
            cold = (d.month, d.day) == (1, 15)
            synth.append({"date": d.isoformat(), "tmax_f": 101 if hot else 90,
                          "tmin_f": 30 if cold else 70})
            d += _dt.timedelta(days=1)
    n = build_normals(synth)
    check("a normal year holds exactly the hot days the record contains",
          n["hot_full_year"] == 2.0, n["hot_full_year"])
    check("the cumulative count by mid-July holds only the days already passed",
          n["hot_through"]["07-15"] == 1.0, n["hot_through"]["07-15"])
    check("a normal season holds exactly the freezing nights the record contains",
          n["cold_full_season"] == 1.0, n["cold_full_season"])
    check("the freeze count is zero before its season's first freeze",
          n["cold_through"]["12-31"] == 0.0, n["cold_through"]["12-31"])
    check("the freeze count carries across New Year within one season",
          n["cold_through"]["01-16"] == 1.0, n["cold_through"]["01-16"])
    check("what a normal year has left is never negative",
          all(round(n["hot_full_year"] - v, 3) >= 0 for v in n["hot_through"].values()))
    check("February 29th does not crash a common year", "02-29" in n["hot_through"])

    # A THIN YEAR IS EXCLUDED RATHER THAN AVERAGED IN AS A MILD ONE.
    thin = [r for r in synth if not (r["date"].startswith("2005-")
                                     and r["date"] > "2005-03-01")]
    n2 = build_normals(thin)
    check("a year with a long outage is dropped from the normals",
          n2["hot_years_used"] == n["hot_years_used"] - 1,
          (n2["hot_years_used"], n["hot_years_used"]))
    check("dropping it does not drag the normal down",
          n2["hot_full_year"] == n["hot_full_year"],
          (n2["hot_full_year"], n["hot_full_year"]))

    print(f"\nheatclock self-test: {'all passed' if not fails else str(len(fails)) + ' FAILED'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--collect", action="store_true")
    ap.add_argument("--normals", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--window", type=int, default=45,
                    help="days of trailing window to fill on --collect")
    a = ap.parse_args()
    # A GATE INVOKED WITH NO ARGUMENTS EXITS 2 AND NEVER RUNS. A bare call that silently does
    # nothing and exits 0 is a workflow step that looks green having done no work.
    if not (a.collect or a.normals or a.self_test):
        ap.print_help()
        return 2
    if a.self_test:
        return self_test()
    if a.normals:
        return normals()
    return collect(a.window)


if __name__ == "__main__":
    sys.exit(main())
