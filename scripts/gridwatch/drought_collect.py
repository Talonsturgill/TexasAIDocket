#!/usr/bin/env python3
"""drought_collect.py — how much of Texas is in drought, weekly, and what a normal week holds.

WHAT THIS IS FOR

The front page chip rotates between candidates and leads with whichever sits furthest from its
own normal. This is the fifth candidate and the first that is not weather measured at a
station. It is the share of Texas in moderate drought or worse, as classified by the United
States Drought Monitor.

THE THING THAT MAKES THIS DIFFERENT FROM EVERY OTHER SERIES HERE, AND IT GOVERNS THE COPY

Every other number this project publishes is either measured by an instrument or computed by
us from something that was. **This one is a panel's judgement.** The Drought Monitor is authored
weekly by rotating authors at NDMC, USDA and NOAA, who read precipitation, soil moisture,
streamflow, reservoir levels and local reports and then draw lines on a map. It is the best
drought record in the country and it is not an instrument reading.

Two rules follow, and both are set down in knowledge/shared/TEXAS_TELEMETRY.md section 6:

  IT IS ATTRIBUTED EVERY TIME. The chip names the Drought Monitor in its first segment, where
  the weather candidates name the station. That segment answers "whose number is this", which
  is the honest question for both.

  IT CARRIES THE MAP DATE, NEVER TODAY'S. A map is published Thursday for conditions through
  the previous Tuesday, so a page stamping it with today's date claims a freshness the
  classification does not have. The record stores `valid_start` and the chip prints it.

WHAT IS OURS AND WHAT IS THEIRS. The percentage is theirs, republished with their name on it.
The NORMAL beside it is ours: the mean and spread of that same week across the prior years,
computed here from the same feed. So the comparison a reader makes is between one authority's
figure and its own history, which is the only comparison this data supports.

WHY D1 AND NOT D0. The columns are CUMULATIVE. `D0` is abnormally dry or worse and reads as
alarming in a normal Texas summer, because abnormally dry is a watch category rather than a
drought. `D1` is moderate drought or worse, which is what the Drought Monitor itself means by
"in drought" and what its own summaries quote.

THE FEED. Keyless, no account, and it serves history: 1,389 weekly maps back to January 2000,
every gap exactly seven days, every map a Tuesday. It answers CSV even though nothing in the
query says so, which is why this parses CSV rather than JSON.

    drought_collect.py --self-test    hermetic, no network, gates every collection
    drought_collect.py --collect      append any map the record does not hold
    drought_collect.py --normals      recompute the weekly normals from the full history
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import io
import json
import statistics
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "ledger" / "gridwatch" / "drought.jsonl"
NORMALS = REPO_ROOT / "config" / "gridwatch" / "drought_normals.json"

SERVICE = ("https://usdmdataservices.unl.edu/api/StateStatistics/"
           "GetDroughtSeverityStatisticsByAreaPercent")
AOI = "48"                      # FIPS 48, Texas
SOURCE_NAME = "US Drought Monitor"

# The first year the Drought Monitor published, and the first full year of its record.
FIRST_YEAR = 2000

# A weekly normal needs enough years behind it to mean anything. ISO week 53 exists in only a
# handful of years, so without a floor that one week would carry a spread computed from four
# samples and the chip would rank it against the others as though it were as well founded.
MIN_WEEKS_SAMPLED = 10

UA = ("TexasAIDocket/1.0 (+https://talonsturgill.github.io/TexasAIDocket; "
      "weekly public-interest drought record; one request per week)")

SPEC = 1


def iso_week(d: _dt.date) -> int:
    """The ISO week a map belongs to.

    KEYED BY ISO WEEK AND NOT BY MONTH AND DAY, which is the opposite of the weather record
    and right for the opposite reason. These maps land on a Tuesday, so the same calendar day
    recurs only every few years and a month-day key would compare almost nothing to anything.
    ISO week lines the Tuesdays up. Week 53 straddles the New Year, which is seasonally
    coherent, and is thinly sampled, which MIN_WEEKS_SAMPLED handles.
    """
    return d.isocalendar()[1]


# --------------------------------------------------------------------------- fetch
def fetch(start: _dt.date, end: _dt.date, timeout: int = 120) -> str:
    url = (f"{SERVICE}?aoi={AOI}&startdate={start.month}/{start.day}/{start.year}"
           f"&enddate={end.month}/{end.day}/{end.year}&statisticsType=1")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode()


# --------------------------------------------------------------------------- parse
def parse(body: str) -> list[dict]:
    """One record per weekly map.

    THE COLUMNS ARE CUMULATIVE AND THAT IS THE TRAP. `D0` is the share in D0 OR WORSE, so
    `D0 >= D1 >= D2 >= D3 >= D4` always holds and `None + D0` is a hundred. Reading them as
    disjoint bands and adding them up produces a number over a hundred that still looks like a
    percentage. The self-test asserts the ordering on every parsed row rather than trusting
    this note.

    A row missing the figure is dropped, never read as zero. Zero percent in drought is a real
    and common reading for Texas, so a missing value that became zero would be indistinguishable
    from the state being entirely out of drought.
    """
    rows = []
    for r in csv.DictReader(io.StringIO(body)):
        start = (r.get("ValidStart") or "").strip()
        if len(start) != 10:
            continue
        try:
            vals = {k: float(r[k]) for k in ("None", "D0", "D1", "D2", "D3", "D4")}
        except (KeyError, TypeError, ValueError):
            continue
        order = [vals["D0"], vals["D1"], vals["D2"], vals["D3"], vals["D4"]]
        if any(a + 1e-6 < b for a, b in zip(order, order[1:])):
            raise ValueError(f"{start}: severity columns are not cumulative: {order}")
        rows.append({
            "_spec": SPEC,
            "valid_start": start,
            "valid_end": (r.get("ValidEnd") or "").strip(),
            "in_drought_pct": round(vals["D1"], 2),      # moderate drought or worse
            "abnormally_dry_pct": round(vals["D0"], 2),
            "severe_pct": round(vals["D2"], 2),
            "extreme_pct": round(vals["D3"], 2),
            "exceptional_pct": round(vals["D4"], 2),
            "source": SOURCE_NAME,
            "verified": True,
        })
    rows.sort(key=lambda r: r["valid_start"])
    return rows


# --------------------------------------------------------------------------- ledger
def load(path: Path = LEDGER) -> list[dict]:
    if not path.exists():
        return []
    rows = [json.loads(t) for t in (s.strip() for s in path.read_text().splitlines()) if t]
    rows.sort(key=lambda r: r["valid_start"])
    return rows


def append(rows: list[dict], path: Path = LEDGER) -> int:
    """Add only maps the record does not hold. A published map is never revised in place.

    APPEND ONLY, AND UNLIKE THE WEATHER RECORD THAT RULE IS KEPT. Both series can be refetched,
    so neither is irreplaceable, but nothing here needs a past line rewritten: the Drought
    Monitor's published maps are final once issued. The weather ledger earned its carve-out by
    needing a new FIELD on every existing line. This does not, so it stays under the strict
    rule, where the default belongs.
    """
    held = {r["valid_start"] for r in load(path)}
    fresh = [r for r in rows if r["valid_start"] not in held]
    if not fresh:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        for r in sorted(fresh, key=lambda r: r["valid_start"]):
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    return len(fresh)


# --------------------------------------------------------------------------- normals
def build_normals(rows: list[dict], through_year: int) -> dict:
    """Mean and spread of the in-drought share, per ISO week, over complete prior years.

    THE CURRENT YEAR IS EXCLUDED. A normal that includes the reading it is about to be compared
    against pulls itself toward that reading, and with twenty-six samples one of them moves the
    mean by four percent of itself. Small, and the comparison is the entire point of the
    figure, so it is computed against prior years only and the file says which.
    """
    by_week: dict[int, list[float]] = {}
    for r in rows:
        d = _dt.date.fromisoformat(r["valid_start"])
        if not (FIRST_YEAR <= d.year <= through_year):
            continue
        by_week.setdefault(iso_week(d), []).append(r["in_drought_pct"])

    weeks = {}
    for w, vals in sorted(by_week.items()):
        if len(vals) < MIN_WEEKS_SAMPLED:
            continue
        weeks[str(w)] = [round(statistics.fmean(vals), 2),
                         round(statistics.pstdev(vals), 2), len(vals)]
    if not weeks:
        raise ValueError("no ISO week has enough years behind it")
    return {
        "_spec": SPEC,
        "source": SOURCE_NAME,
        "source_url": "https://droughtmonitor.unl.edu/",
        "measure": "share of Texas in moderate drought or worse, the D1 category and above",
        "base_period": [FIRST_YEAR, through_year],
        "min_weeks_sampled": MIN_WEEKS_SAMPLED,
        "note": ("Per ISO week, as [mean, standard deviation, years sampled]. The current year "
                 "is excluded so a reading is never compared against a normal containing it."),
        "by_week": weeks,
    }


# --------------------------------------------------------------------------- commands
def collect() -> int:
    today = _dt.date.today()
    held = load()
    start = (_dt.date.fromisoformat(held[-1]["valid_start"]) - _dt.timedelta(days=21)
             if held else _dt.date(FIRST_YEAR, 1, 1))
    n = append(parse(fetch(start, today)))
    rows = load()
    print(f"drought: {n} new map(s); record holds {len(rows)}"
          + (f", through {rows[-1]['valid_start']}" if rows else ""))
    return 0


def normals() -> int:
    today = _dt.date.today()
    print(f"drought: fetching {FIRST_YEAR} to {today.year} from the Drought Monitor")
    rows = parse(fetch(_dt.date(FIRST_YEAR, 1, 1), today))
    doc = build_normals(rows, today.year - 1)
    NORMALS.parent.mkdir(parents=True, exist_ok=True)
    NORMALS.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    weeks = doc["by_week"]
    print(f"drought: normals from {len(rows)} weekly maps, {len(weeks)} ISO weeks kept "
          f"of 53, base {doc['base_period'][0]} to {doc['base_period'][1]}")
    return 0


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    fails = []

    def check(label, cond, extra=""):
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}" + ("" if cond else f"  {extra}"))
        if not cond:
            fails.append(label)

    head = "MapDate,StateAbbreviation,None,D0,D1,D2,D3,D4,ValidStart,ValidEnd,StatisticFormatID"
    body = "\n".join([
        head,
        "20260811,TX,42.72,57.28,27.90,11.27,6.14,0.39,2026-08-11,2026-08-17,1",
        "20260804,TX,45.00,55.00,25.00,10.00,5.00,0.00,2026-08-04,2026-08-10,1",
        "20260728,TX,62.31,37.69,23.20,9.53,1.18,0.00,,,1",           # no ValidStart, dropped
    ])
    rows = parse(body)
    check("a map with no valid date is dropped", len(rows) == 2, [r["valid_start"] for r in rows])
    check("the in-drought share is D1, moderate or worse, not D0",
          rows[-1]["in_drought_pct"] == 27.90, rows[-1])
    check("the record keeps the map's own dates, not today's",
          rows[-1]["valid_start"] == "2026-08-11" and rows[-1]["valid_end"] == "2026-08-17")
    check("maps come back oldest first",
          [r["valid_start"] for r in rows] == ["2026-08-04", "2026-08-11"])
    check("every source is named on every record", all(r["source"] == SOURCE_NAME for r in rows))

    # THE CUMULATIVE ORDERING IS ENFORCED, NOT ASSUMED.
    bad = f"{head}\n20260811,TX,42.72,20.00,27.90,11.27,6.14,0.39,2026-08-11,2026-08-17,1"
    try:
        parse(bad)
        check("a row whose severities are not cumulative is refused", False, "it parsed")
    except ValueError:
        check("a row whose severities are not cumulative is refused", True)

    check("a feed with only a header is an answer, not a crash", parse(head) == [])
    miss = f"{head}\n20260811,TX,42.72,57.28,,11.27,6.14,0.39,2026-08-11,2026-08-17,1"
    check("a missing share is dropped rather than read as no drought", parse(miss) == [])

    # ISO WEEK KEYING, including the New Year straddle.
    check("a January date in the previous year's last ISO week keys to that week",
          iso_week(_dt.date(2027, 1, 1)) == 53, iso_week(_dt.date(2027, 1, 1)))
    check("a mid-August Tuesday keys to week 33", iso_week(_dt.date(2026, 8, 11)) == 33)

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "drought.jsonl"
        append([{"valid_start": "2026-08-04", "in_drought_pct": 25.0},
                {"valid_start": "2026-08-11", "in_drought_pct": 27.9}], p)
        first = p.read_text()
        n = append([{"valid_start": "2026-08-04", "in_drought_pct": 99.9},
                    {"valid_start": "2026-08-18", "in_drought_pct": 30.0}], p)
        check("a published map is never rewritten", n == 1 and "99.9" not in p.read_text())
        check("the lines already written are untouched", p.read_text().startswith(first))

    # NORMALS from a synthetic record whose answer is known by construction.
    synth = []
    for y in range(2000, 2027):
        d = _dt.date(y, 1, 7)
        while d.year == y:
            # Week 33 alternates 20 and 40, so its mean is 30 and its spread is 10.
            v = (20.0 if y % 2 == 0 else 40.0) if iso_week(d) == 33 else 50.0
            synth.append({"valid_start": d.isoformat(), "in_drought_pct": v})
            d += _dt.timedelta(days=7)
    n = build_normals(synth, 2025)
    check("a week's normal is the mean of the prior years",
          n["by_week"]["33"][0] == 30.0, n["by_week"]["33"])
    check("...and carries the spread beside it", n["by_week"]["33"][1] == 10.0, n["by_week"]["33"])
    check("...and the count of years behind it", n["by_week"]["33"][2] == 26, n["by_week"]["33"])
    check("the base period stops before the current year", n["base_period"] == [2000, 2025])
    check("a thinly sampled week is left out rather than published weakly",
          all(v[2] >= MIN_WEEKS_SAMPLED for v in n["by_week"].values()))

    thin = [r for r in synth if iso_week(_dt.date.fromisoformat(r["valid_start"])) != 33
            or r["valid_start"][:4] in ("2000", "2001", "2002")]
    n2 = build_normals(thin, 2025)
    check("a week that falls under the floor disappears from the normals",
          "33" not in n2["by_week"], n2["by_week"].get("33"))

    print(f"\ndrought self-test: {'all passed' if not fails else str(len(fails)) + ' FAILED'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--collect", action="store_true")
    ap.add_argument("--normals", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if not (a.collect or a.normals or a.self_test):
        ap.print_help()
        return 2
    if a.self_test:
        return self_test()
    if a.normals:
        return normals()
    return collect()


if __name__ == "__main__":
    sys.exit(main())
