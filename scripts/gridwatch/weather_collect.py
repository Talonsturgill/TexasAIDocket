#!/usr/bin/env python3
"""weather_collect.py — the observed daily weather at the anchor station, and its normals.

WHAT THIS IS FOR

The front page opens with one live, computed, dated line about the physical world. The sibling
product opens with how much daylight its state capital has left today and how fast it is losing
it, and that single detail is most of why its front page reads as alive rather than published.
It works because it is true, it is about a real place, and it is different every morning.

Texas has no daylight story. What it has is weather people already keep score of without being
taught the unit: the hundred degree day, the freezing night, the night that never dropped below
eighty, and how far behind on rain the year is. This collects the daily observations those four
counts are computed from, plus the thirty year normals each is compared against.

WHY FOUR SERIES AND NOT ONE

The chip rotates. It leads with whichever of the four sits furthest from its own normal for
today's date, so it surfaces what is actually unusual rather than what a calendar table decided
in advance. That selection needs, for every metric and every calendar day, both a normal AND a
spread, because "six days above normal" means one thing for a metric that varies by two and
another for one that varies by nine. So the normals here carry a standard deviation beside every
mean. See `scripts/site/frontchip.py`, which does the selecting.

WHY THIS COLLECTOR IS SHAPED NOTHING LIKE THE ERCOT ONE

`gridwatch_collect.py` exists under a permanent emergency: ERCOT's dashboard feeds are rolling
windows with no archive, so a missed day is gone from here and from everywhere. Every design
choice there follows from that.

NONE OF IT APPLIES HERE, and copying it would be cargo cult. NCEI's `daily-summaries` service
is the archive. It serves any station and any date range back to the nineteenth century, it is
United States government work in the public domain, and it needs no key. Four consequences,
each the opposite of the grid collector's:

  A MISSED DAY COSTS NOTHING. This fetches a trailing window and fills whatever is absent, so
  a cron that fails for a week catches up completely on the next run.

  NO RAW SNAPSHOT IS KEPT. The grid collector gzips every response before parsing it, because
  a parser found to be wrong later has no other route back to the source bytes. Here the source
  bytes are re-fetchable forever by the same URL, so a snapshot would be a redundant copy of a
  permanent archive, committed daily, growing without end.

  THE LEDGER IS NOT APPEND ONLY, and `ownership.yaml` says so explicitly for this file alone.
  A rewrite here is a re-derivation, not a loss. That is what made it possible to add
  precipitation to a record that already held temperature, which under the append-only rule
  would have been blocked outright.

  IT IS NOT THE PROJECT'S IRREPLACEABLE JOB. It may fail, loudly, and nothing is lost.

WHY THE RECORD LAGS, AND WHY THAT IS PUBLISHED RATHER THAN PAPERED OVER

Daily summaries settle a few days behind real time, because the observation is quality
controlled before it is published. So every count is a count THROUGH the last settled day, and
the chip prints that date beside it. Reaching for today's number from a forecast feed would mix
a projection into a measured count, which is the one thing this project was built never to do.

    weather_collect.py --self-test    hermetic, no network, gates every collection
    weather_collect.py --collect      fill any gap in the trailing window
    weather_collect.py --normals      recompute the normals file from 30 years
"""
from __future__ import annotations

import argparse
import calendar
import datetime as _dt
import json
import statistics
import sys
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "ledger" / "gridwatch" / "weather.jsonl"
NORMALS = REPO_ROOT / "config" / "gridwatch" / "weather_normals.json"

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
# The research behind this, including why there is no honest STATEWIDE version of any of these
# counts, is knowledge/shared/TEXAS_TELEMETRY.md.
STATION = "USW00003927"
STATION_NAME = "Dallas Fort Worth"

# The thresholds, in whole degrees Fahrenheit. All three are round numbers the public already
# counts in, which is the entire point: the chip reports what people were already scoring.
HOT_F = 100      # a day is hot when the high reaches this
COLD_F = 32      # a night is freezing when the low reaches this
WARM_F = 80      # a night never really cooled off when the low stays at or above this

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

UA = ("TexasAIDocket/1.0 (+https://texasaidocket.com; "
      "daily public-interest climate record; one request per day)")

SPEC = 2

# THE FOUR METRICS, each a cumulative total that only ever climbs through its cycle.
#
# CUMULATIVE ON PURPOSE, AND THIS IS THE DESIGN CONSTRAINT RATHER THAN A DETAIL. A chip built
# on "yesterday's high against the normal high" would be a different number every morning for
# no reason a reader could feel, and with four of those rotating on which was most extreme it
# would flicker. A running total moves slowly, carries the season inside it, and reads as a
# clock, which is the whole reason the sibling's daylight line works.
#
#   key      what it counts                     cycle    field   test
METRICS = {
    "hot":  dict(cycle="year",   field="tmax_f", op=">=", threshold=HOT_F,  unit="count"),
    "cold": dict(cycle="season", field="tmin_f", op="<=", threshold=COLD_F, unit="count"),
    "warm": dict(cycle="year",   field="tmin_f", op=">=", threshold=WARM_F, unit="count"),
    # Rain is a SUM of a measured depth rather than a count of days over a threshold, so it
    # carries no threshold at all and its unit is inches.
    "rain": dict(cycle="year",   field="prcp_in", op="sum", threshold=None, unit="inches"),
}


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


def cycle_keys(cycle: str) -> list[str]:
    return year_keys() if cycle == "year" else season_keys()


def season_of(day: _dt.date) -> int:
    """The freeze season a date belongs to, named for the year it started in."""
    return day.year if day.month >= SEASON_START_MONTH else day.year - 1


def cycle_of(day: _dt.date, cycle: str) -> int:
    return day.year if cycle == "year" else season_of(day)


# --------------------------------------------------------------------------- fetch
def fetch(start: str, end: str, station: str = STATION, timeout: int = 120) -> bytes:
    q = urllib.parse.urlencode({
        "dataset": "daily-summaries",
        "stations": station,
        "startDate": start,
        "endDate": end,
        "dataTypes": "TMAX,TMIN,PRCP",
        "units": "standard",
        "format": "json",
    })
    req = urllib.request.Request(f"{SERVICE}?{q}",
                                 headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# --------------------------------------------------------------------------- parse
def parse(raw: bytes) -> list[dict]:
    """Observed daily weather, one row per day that carries at least one reading.

    A MISSING TEMPERATURE IS ABSENT, NEVER ZERO. NCEI returns the field as an empty string
    when an observation did not pass quality control, and `float("")` raises while a bare
    `or 0` would file a missing summer day as a low of zero degrees.

    A DRY DAY IS ZERO, NOT MISSING, AND THAT IS THE OPPOSITE RULE FOR THE SAME SHAPE OF
    DATA. Precipitation is reported as "0.00" on the great majority of Texas days, and that
    zero is a measurement. Treating it as absent the way a missing temperature is treated
    would drop most of the year out of the rainfall total and leave the count of measured
    days looking healthy, because the days that DID rain would all still be there. This is
    the one place in this file where `if not value` would be a silent, plausible, and
    completely wrong reading of the record.
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

        def num(field, cast):
            v = row.get(field)
            if v is None or str(v).strip() == "":
                return None
            try:
                return cast(float(v))
            except (TypeError, ValueError):
                return None

        hi = num("TMAX", lambda x: int(round(x)))
        lo = num("TMIN", lambda x: int(round(x)))
        # Hundredths of an inch is what the instrument reports; keeping it is what makes the
        # yearly total recomputable rather than approximately right.
        pr = num("PRCP", lambda x: round(x, 2))
        if hi is None and lo is None and pr is None:
            continue
        out.append({
            "_spec": SPEC,
            "date": date,
            "station": str(row.get("STATION") or STATION),
            "tmax_f": hi,
            "tmin_f": lo,
            "prcp_in": pr,
            "source": "ncei daily-summaries",
            "verified": True,
        })
    out.sort(key=lambda r: r["date"])
    return out


# --------------------------------------------------------------------------- ledger
def load(path: Path = LEDGER) -> list[dict]:
    """Every reading held, oldest first.

    SORTED ON READ RATHER THAN ASSUMED. Gap filling appends a date older than the last line
    whenever a backfill lands after a newer reading, so file order is not date order.
    """
    if not path.exists():
        return []
    rows = [json.loads(t) for t in (s.strip() for s in path.read_text().splitlines()) if t]
    rows.sort(key=lambda r: r["date"])
    return rows


def write(rows: list[dict], path: Path = LEDGER) -> int:
    """Replace the ledger with `rows`, sorted by date.

    A REWRITE IS LEGITIMATE HERE AND NOWHERE ELSE IN THIS DIRECTORY. See the module docstring
    and the carve-out in ownership.yaml. Every line is re-derivable from NCEI by date range,
    so this is a re-derivation rather than the destruction of an unrepeatable measurement.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(json.dumps(r, sort_keys=True) + "\n"
                   for r in sorted(rows, key=lambda r: r["date"]))
    path.write_text(body)
    return len(rows)


def merge(existing: list[dict], fresh: list[dict]) -> list[dict]:
    """Fresh readings win for the dates they cover; everything else is kept.

    NEWER DATA REPLACES OLDER FOR THE SAME DAY, which matters because NCEI revises. A value
    that failed quality control on Tuesday and passed on Friday should end up in the record
    as the value that passed, and a collector that refused to overwrite would hold the
    provisional one forever.
    """
    by_date = {r["date"]: r for r in existing}
    by_date.update({r["date"]: r for r in fresh})
    return sorted(by_date.values(), key=lambda r: r["date"])


# --------------------------------------------------------------------------- normals
def _running_totals(by_cycle: dict, years: list[int], keys: list[str], spec: dict) -> dict:
    """For each calendar key, every year's cumulative total up to and including that key."""
    out, running = {}, {y: 0.0 for y in years}
    field, op, thr = spec["field"], spec["op"], spec["threshold"]
    for key in keys:
        mm, dd = (int(x) for x in key.split("-"))
        for y in years:
            # A season spans two calendar years, so the row for a key before the season's
            # start month lives in the FOLLOWING calendar year.
            cal_year = y if (spec["cycle"] == "year" or mm >= SEASON_START_MONTH) else y + 1
            if mm == 2 and dd == 29 and not calendar.isleap(cal_year):
                continue
            row = by_cycle.get(cal_year, {}).get(key)
            v = row.get(field) if row else None
            if v is None:
                continue
            if op == "sum":
                running[y] += v
            elif (op == ">=" and v >= thr) or (op == "<=" and v <= thr):
                running[y] += 1
        out[key] = [running[y] for y in years]
    return out


def build_normals(rows: list[dict]) -> dict:
    """Mean and spread of each metric's cumulative total, for every calendar day.

    WHY THE SPREAD IS HERE AND NOT DERIVED LATER. The chip picks whichever metric is furthest
    from its own normal, across metrics measured in days and in inches. Those are only
    comparable once each is expressed in units of its own year to year variation, so the
    standard deviation is as much a part of the published normal as the mean, and it is
    computed from the same thirty years in the same pass.

    YEARS WITH THIN COVERAGE ARE EXCLUDED, NOT PATCHED. See MIN_YEAR_COVERAGE.
    """
    lo_y, hi_y = NORMALS_BASE
    by_cal: dict[int, dict[str, dict]] = {}
    for r in rows:
        d = _dt.date.fromisoformat(r["date"])
        by_cal.setdefault(d.year, {})[f"{d.month:02d}-{d.day:02d}"] = r

    whole = [y for y in range(lo_y, hi_y + 1)
             if len(by_cal.get(y, {})) / (366 if calendar.isleap(y) else 365)
             >= MIN_YEAR_COVERAGE]
    if not whole:
        raise ValueError("no year in the base period has usable coverage")

    metrics = {}
    for key, spec in METRICS.items():
        # A season needs both of its calendar years measured.
        years = (whole if spec["cycle"] == "year"
                 else [y for y in whole if (y + 1) in whole])
        if not years:
            raise ValueError(f"{key}: no usable cycle in the base period")
        keys = cycle_keys(spec["cycle"])
        totals = _running_totals(by_cal, years, keys, spec)
        through = {}
        for k in keys:
            vals = totals[k]
            through[k] = [round(statistics.fmean(vals), 3),
                          round(statistics.pstdev(vals), 3) if len(vals) > 1 else 0.0]
        metrics[key] = {
            "cycle": spec["cycle"], "unit": spec["unit"], "threshold": spec["threshold"],
            "cycles_used": len(years),
            "through": through,
            "full": through[keys[-1]][0],
        }

    return {
        "_spec": SPEC,
        "station": STATION,
        "station_name": STATION_NAME,
        "source": "ncei daily-summaries",
        "base_period": list(NORMALS_BASE),
        "season_start_month": SEASON_START_MONTH,
        "note": ("Each metric's cumulative total through each calendar day, as [mean, "
                 "standard deviation] over the base period. Counts are days; rain is inches."),
        "metrics": metrics,
    }


# --------------------------------------------------------------------------- commands
def collect(window_days: int = 45) -> int:
    """Fill every gap in the trailing window. Idempotent, and a no-op once caught up."""
    today = _dt.date.today()
    start = today - _dt.timedelta(days=window_days)
    fresh = parse(fetch(start.isoformat(), today.isoformat()))
    before = load()
    merged = merge(before, fresh)
    write(merged)
    added = len(merged) - len(before)
    print(f"weather: {added} new day(s), {len(fresh)} refreshed; ledger holds {len(merged)}"
          + (f", through {merged[-1]['date']}" if merged else ""))
    return 0


def seed(start: str) -> int:
    """Re-derive the whole ledger from the archive, from `start` to today."""
    today = _dt.date.today().isoformat()
    print(f"weather: re-deriving {start} to {today} from NCEI")
    rows = parse(fetch(start, today))
    n = write(merge(load(), rows))
    print(f"weather: ledger holds {n} day(s)")
    return 0


def normals() -> int:
    lo, hi = NORMALS_BASE
    print(f"weather: fetching {lo} to {hi} for {STATION}, this takes a moment")
    rows = parse(fetch(f"{lo}-01-01", f"{hi}-12-31"))
    doc = build_normals(rows)
    NORMALS.parent.mkdir(parents=True, exist_ok=True)
    NORMALS.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    print(f"weather: normals from {len(rows)} daily records")
    for k, m in doc["metrics"].items():
        print(f"  {k:5} {m['cycles_used']:2} cycles   a normal {m['cycle']} holds "
              f"{m['full']} {m['unit']}")
    return 0


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    """Hermetic. Every case is a defect this collector could actually ship."""
    fails = []

    def check(label, cond, extra=""):
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}" + ("" if cond else f"  {extra}"))
        if not cond:
            fails.append(label)

    raw = json.dumps([
        {"DATE": "2026-07-01", "STATION": STATION, "TMAX": "101", "TMIN": "78", "PRCP": "0.00"},
        {"DATE": "2026-07-02", "STATION": STATION, "TMAX": "", "TMIN": "76", "PRCP": "1.25"},
        {"DATE": "2026-07-03", "STATION": STATION, "TMAX": "", "TMIN": "", "PRCP": ""},
        {"DATE": "2026-07-04", "STATION": STATION, "TMAX": "99.6", "TMIN": "75", "PRCP": "0.04"},
    ]).encode()
    rows = parse(raw)
    check("a day missing every value is dropped", len(rows) == 3, [r["date"] for r in rows])
    check("a day missing one value keeps the others",
          rows[1]["tmax_f"] is None and rows[1]["tmin_f"] == 76 and rows[1]["prcp_in"] == 1.25,
          rows[1])
    check("a missing high is never read as zero",
          all(r["tmax_f"] is None or r["tmax_f"] > 50 for r in rows), rows)
    check("a fractional degree rounds rather than truncating toward zero",
          rows[2]["tmax_f"] == 100, rows[2])

    # THE ZERO THAT IS A MEASUREMENT. Most Texas days report 0.00 inches, and reading that as
    # missing would quietly drop the majority of the year from the rainfall total.
    check("a dry day is zero rain and not a missing reading",
          rows[0]["prcp_in"] == 0.0 and rows[0]["prcp_in"] is not None, rows[0])
    check("a hundredth of an inch survives rounding", rows[2]["prcp_in"] == 0.04, rows[2])
    check("an empty range is an answer, not a crash", parse(b"[]") == [])

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "weather.jsonl"
        write([{"date": "2026-07-03", "tmax_f": 103}, {"date": "2026-07-01", "tmax_f": 101}], p)
        check("the ledger is written in date order",
              [r["date"] for r in load(p)] == ["2026-07-01", "2026-07-03"])
        # NCEI REVISES, so a re-fetch of a held day must win rather than be discarded.
        merged = merge(load(p), [{"date": "2026-07-01", "tmax_f": 102},
                                 {"date": "2026-07-02", "tmax_f": 99}])
        check("a revised reading replaces the one held",
              [r["tmax_f"] for r in merged] == [102, 99, 103], merged)
        check("a backfilled gap lands in date order",
              [r["date"] for r in merged] == ["2026-07-01", "2026-07-02", "2026-07-03"])

    yk, sk = year_keys(), season_keys()
    check("the year holds 366 keys including February 29th",
          len(yk) == 366 and "02-29" in yk, len(yk))
    check("the freeze season starts in July and ends in June",
          sk[0] == "07-01" and sk[-1] == "06-30" and len(sk) == 366, (sk[0], sk[-1]))
    check("a January date belongs to the season that began the previous July",
          season_of(_dt.date(2026, 1, 9)) == 2025 and season_of(_dt.date(2026, 8, 9)) == 2026)

    # THE NORMALS, FROM A SYNTHETIC RECORD WHOSE ANSWER IS KNOWN BY CONSTRUCTION.
    synth = []
    for y in range(NORMALS_BASE[0], NORMALS_BASE[1] + 1):
        d = _dt.date(y, 1, 1)
        # One year in three is a "hot" year, so the spread is non-zero and checkable.
        extra = 1 if y % 3 == 0 else 0
        while d.year == y:
            hot = (d.month, d.day) in ((7, 1), (8, 1)) or (extra and (d.month, d.day) == (9, 1))
            synth.append({"date": d.isoformat(),
                          "tmax_f": 101 if hot else 90,
                          "tmin_f": 30 if (d.month, d.day) == (1, 15) else 70,
                          "prcp_in": 1.0 if d.day == 1 else 0.0})
            d += _dt.timedelta(days=1)
    n = build_normals(synth)
    hot, cold, rain, warm = (n["metrics"][k] for k in ("hot", "cold", "rain", "warm"))

    check("a normal year holds the hot days the record contains",
          abs(hot["full"] - (2 + 10 / 30)) < 0.01, hot["full"])
    check("the cumulative count by mid-July holds only what has passed",
          hot["through"]["07-15"][0] == 1.0, hot["through"]["07-15"])
    check("a metric that varies between years has a non-zero spread",
          hot["through"]["12-31"][1] > 0, hot["through"]["12-31"])
    check("a metric identical every year has a spread of zero",
          cold["through"]["06-30"][1] == 0.0, cold["through"]["06-30"])
    check("the freeze count carries across New Year inside one season",
          cold["through"]["01-16"][0] == 1.0 and cold["through"]["12-31"][0] == 0.0,
          (cold["through"]["12-31"], cold["through"]["01-16"]))
    check("rain accumulates as a sum of depth, not a count of wet days",
          abs(rain["full"] - 12.0) < 0.001, rain["full"])
    check("rain by the end of March holds three monthly inches",
          abs(rain["through"]["03-31"][0] - 3.0) < 0.001, rain["through"]["03-31"])
    check("a warm night threshold that nothing crosses yields a zero normal",
          warm["full"] == 0.0, warm["full"])
    check("every metric is keyed for February 29th",
          all("02-29" in m["through"] for m in n["metrics"].values()))
    check("a cumulative normal never decreases through its cycle",
          all(all(m["through"][a][0] <= m["through"][b][0] + 1e-9
                  for a, b in zip(cycle_keys(m["cycle"]), cycle_keys(m["cycle"])[1:]))
              for m in n["metrics"].values()))

    thin = [r for r in synth if not (r["date"].startswith("2005-") and r["date"] > "2005-03-01")]
    n2 = build_normals(thin)
    check("a year with a long outage is dropped from the normals",
          n2["metrics"]["hot"]["cycles_used"] == hot["cycles_used"] - 1,
          (n2["metrics"]["hot"]["cycles_used"], hot["cycles_used"]))

    print(f"\nweather self-test: {'all passed' if not fails else str(len(fails)) + ' FAILED'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--collect", action="store_true")
    ap.add_argument("--normals", action="store_true")
    ap.add_argument("--seed", metavar="YYYY-MM-DD",
                    help="re-derive the whole ledger from this date to today")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--window", type=int, default=45,
                    help="days of trailing window to fill on --collect")
    a = ap.parse_args()
    # A GATE INVOKED WITH NO ARGUMENTS EXITS 2 AND NEVER RUNS. A bare call that silently does
    # nothing and exits 0 is a workflow step that looks green having done no work.
    if not (a.collect or a.normals or a.seed or a.self_test):
        ap.print_help()
        return 2
    if a.self_test:
        return self_test()
    if a.normals:
        return normals()
    if a.seed:
        return seed(a.seed)
    return collect(a.window)


if __name__ == "__main__":
    sys.exit(main())
