#!/usr/bin/env python3
"""gridwatch_collect.py — one complete measured day of the ERCOT grid, every day, forever.

WHY THIS COLLECTS YESTERDAY AND NOT TODAY

The obvious design polls the live grid and writes down what it sees. It is wrong, and the
payloads say why. `supply-demand.json` carries five-minute intervals for the CURRENT Texas
local day only, and its rows carry a `forecast` FLAG: rows before now are telemetry, rows
after now are projection, in the same list, under the same key names. A collector that reads
"the latest row" reads a projection and files it as a measurement. That is not a bug that
shows up in the output. It shows up as a number that is simply wrong, forever, in a series
nobody can rebuild.

`system-wide-demand.json` carries three blocks: `previousDay`, `currentDay`, `nextDay`. The
`previousDay` block is a COMPLETE local day, hour by hour, measured, already settled. So we
take that. Three things follow, and all three are worth more than the freshness we give up:

  THE DAY IS WHOLE BY CONSTRUCTION. No partial-day arithmetic, no coverage caveat in the
  common case, no race against local midnight, no peak missed because the cron fired early.

  A LATE CRON STOPS MATTERING. GitHub's scheduler is routinely minutes to tens of minutes
  late. Against a current-day window that lateness eats the end of the day; against a settled
  previous day the run has the whole following day to land.

  MEASURED AND MODELED ARRIVE TOGETHER. Each hour carries `systemLoad` (measured) beside
  `dayAheadForecast` (ERCOT's own model, published the day before). So the accuracy check is
  ERCOT's forecast against ERCOT's telemetry, computed here, and this project never has to fit
  a demand model or defend one. The gap is a fact, not our opinion.

It still cannot be backfilled. Tomorrow's `previousDay` is today. A day missed entirely is
gone, from here and from anywhere else, which is why this runs on its own cron and never as a
phase of an editorial routine. A carousel run failing its gates on a Tuesday must not cost
Tuesday's reading.

WHAT IT REFUSES TO COLLECT

`daily-prc.json` is the reliability feed. It carries ERCOT's own `current_condition` block:
a state, an EEA level, and a sentence like "There is enough power for current demand." It
would be easy to store and it is exactly the thing this project has promised never to publish.
A verdict does not become ours to publish because someone else said it first, and a field that
exists in the ledger is a field a future page will eventually render. So it is not collected.
The refusal is the feature.

WHAT A RECORD HOLDS

The full hourly series, not just the summary. Three arrays of one value per hour, plus the
figures computed from them. That costs about seven hundred bytes a day and buys the strongest
claim this project can make about its own numbers: **every published figure recomputes from
`readings.jsonl` alone**, with no re-fetch and no trust in whatever this file did on the day.
If a summary here is ever found wrong, the series beside it is the correction.

A FAILED FETCH WRITES AN EXPLICIT UNVERIFIED RECORD AND CARRIES NO NUMBER FORWARD. A gap that
says it is a gap is honest. A gap papered over with yesterday's figure is a fabrication that
nothing downstream can detect.

    gridwatch_collect.py --self-test        hermetic, gates every scheduled collection
    gridwatch_collect.py --collect
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "ledger" / "gridwatch" / "readings.jsonl"
RAW = REPO_ROOT / "ledger" / "gridwatch" / "raw"

BASE = "https://www.ercot.com/api/1/services/read/dashboards"
FEEDS = {
    "demand": f"{BASE}/system-wide-demand.json",
    "fuel_mix": f"{BASE}/fuel-mix.json",
}

# A descriptive agent is the courteous thing and it is also what keeps this working. ERCOT does
# not disallow /api/ in robots.txt; a nameless scraper is what gets a path closed.
UA = ("TexasAIDocket/1.0 (+https://talonsturgill.github.io/TexasAIDocket; "
      "daily public-interest grid record; two requests per day)")

SPEC = 1

# ROUNDING IS A COMPUTATION WITH A STATED RULE, NEVER A CHOICE MADE AT WRITING TIME.
# Measured series are stored exactly as ERCOT published them, so no rounding rule applies and
# no information is lost. Every figure DERIVED from them is rounded half-even to one decimal
# megawatt, which is one part in roughly eight hundred thousand of a summer peak.
DERIVED_DP = 1


def _r(x):
    return None if x is None else round(float(x), DERIVED_DP)


# --------------------------------------------------------------------------- fetch
def fetch(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# --------------------------------------------------------------------------- parse
def parse_demand(raw: bytes) -> dict:
    """The settled previous local day, hour by hour, out of ERCOT's own payload.

    THE DATE COMES FROM THE PAYLOAD, NEVER FROM OUR CLOCK. A container in UTC does not know
    what day it is in Texas, the answer changes twice a year, and ERCOT already stamped the
    block with the day it means. Reading our own clock here would be inventing an answer that
    is already published.

    Hour count is read, never assumed. A spring-forward day is 23 hours and a fall-back day is
    25, and a collector that hardcodes 24 files a wrong mean twice a year.
    """
    doc = json.loads(raw)
    block = doc.get("previousDay")
    if not isinstance(block, dict):
        raise ValueError("payload carries no previousDay block")

    day = str(block.get("dayDate") or "")[:10]
    if len(day) != 10 or day[4] != "-":
        raise ValueError(f"previousDay carries no usable dayDate: {day!r}")

    rows = block.get("data")
    if not isinstance(rows, list) or not rows:
        raise ValueError("previousDay carries no hourly rows")

    rows = sorted((r for r in rows if isinstance(r, dict)), key=lambda r: r.get("epoch") or 0)

    def series(field):
        return [r.get(field) if isinstance(r.get(field), (int, float)) else None for r in rows]

    return {
        "date": day,
        "hour_ending": [r.get("hourEnding") for r in rows],
        "load_mw": series("systemLoad"),
        "day_ahead_forecast_mw": series("dayAheadForecast"),
        "capacity_mw": series("currentDayHsl"),
        "hours_in_day": len(rows),
        "ercot_stamp": doc.get("lastUpdated"),
    }


def parse_fuel_mix(raw: bytes, day: str) -> dict | None:
    """Energy by fuel for one settled day, computed from ERCOT's five-minute generation.

    Returns None rather than raising when the day is absent. The load series is the spine of
    this record and must not be lost because a second, softer feed moved.

    STORAGE IS SIGNED AND STAYS SIGNED. `Power Storage` is negative while batteries charge, and
    over a full day it is usually net negative because a round trip loses energy. Clamping that
    to zero would publish a fleet that only ever discharges. Shares are the builder's problem,
    with a denominator it has to name out loud; the collector's job is the honest signed total.
    """
    doc = json.loads(raw)
    days = doc.get("data")
    if not isinstance(days, dict):
        return None
    samples = days.get(day)
    if not isinstance(samples, dict) or not samples:
        return None

    # Five-minute samples of instantaneous generation in MW. Energy is the mean times the
    # hours covered, which is the same as the sum times five over sixty when samples are
    # evenly spaced. Deriving the interval from the sample count keeps it right if ERCOT
    # ever changes cadence, and keeps a short day short.
    totals: dict[str, float] = {}
    for reading in samples.values():
        if not isinstance(reading, dict):
            continue
        for fuel, v in reading.items():
            gen = v.get("gen") if isinstance(v, dict) else v
            if isinstance(gen, (int, float)):
                totals[fuel] = totals.get(fuel, 0.0) + float(gen)

    n = len(samples)
    if not totals or not n:
        return None
    interval_h = 24.0 / n
    return {
        "fuel_energy_mwh": {k: _r(v * interval_h) for k, v in sorted(totals.items())},
        "fuel_samples": n,
    }


# --------------------------------------------------------------------------- compute
def summarise(d: dict) -> dict:
    """Every figure a page could want, computed here, from the series stored beside it.

    THE LOAD FACTOR IS THE POINT. Mean over peak is the shape of the day, and it is the one
    number on this page that is genuinely about AI. A data center is a flat load: it runs at
    four in the morning at close to what it runs at five in the afternoon. Air conditioning is
    the opposite, a tall narrow spike against a low night. So a grid absorbing large constant
    load has its trough rise faster than its peak, and the load factor climbs. That is a
    fingerprint no press release can spin and no single day can show, which is exactly why it
    is worth starting the series today.
    """
    load = [v for v in d["load_mw"] if v is not None]
    cap = d["capacity_mw"]
    fc = d["day_ahead_forecast_mw"]
    out: dict = {
        "hours_measured": len(load),
        "hours_in_day": d["hours_in_day"],
        "peak_load_mw": None, "peak_hour_ending": None,
        "min_load_mw": None, "min_hour_ending": None,
        "mean_load_mw": None, "energy_mwh": None, "load_factor": None,
        "capacity_at_peak_mw": None, "reserve_at_peak_mw": None,
        "forecast_peak_mw": None, "peak_forecast_error_mw": None,
        "mean_absolute_forecast_error_mw": None,
    }
    if not load:
        return out

    hi = max(range(len(d["load_mw"])), key=lambda i: (d["load_mw"][i] is not None,
                                                      d["load_mw"][i] or 0))
    lo = min((i for i, v in enumerate(d["load_mw"]) if v is not None),
             key=lambda i: d["load_mw"][i])
    mean = sum(load) / len(load)
    peak = d["load_mw"][hi]

    out["peak_load_mw"] = _r(peak)
    out["peak_hour_ending"] = d["hour_ending"][hi]
    out["min_load_mw"] = _r(d["load_mw"][lo])
    out["min_hour_ending"] = d["hour_ending"][lo]
    out["mean_load_mw"] = _r(mean)
    # Each hourly figure is an average megawatt over one hour, so megawatt hours is the sum.
    out["energy_mwh"] = _r(sum(load))
    out["load_factor"] = round(mean / peak, 4) if peak else None

    if isinstance(cap[hi], (int, float)):
        out["capacity_at_peak_mw"] = _r(cap[hi])
        out["reserve_at_peak_mw"] = _r(cap[hi] - peak)

    fcv = [v for v in fc if v is not None]
    if fcv:
        out["forecast_peak_mw"] = _r(max(fcv))
        # ERCOT's model against ERCOT's telemetry. Signed on the peak so the direction shows,
        # absolute across the day so overs and unders cannot cancel into a flattering zero.
        out["peak_forecast_error_mw"] = _r(max(fcv) - peak)
        paired = [(m, f) for m, f in zip(d["load_mw"], fc) if m is not None and f is not None]
        if paired:
            out["mean_absolute_forecast_error_mw"] = _r(
                sum(abs(f - m) for m, f in paired) / len(paired))
    return out


def reading(*, offline: dict) -> dict:
    """One settled day's record. Always returns a record; never raises past a bad payload."""
    base = {
        "_spec": SPEC,
        "date": None,
        "source": "ercot system-wide-demand",
        "verified": False,
        "note": "",
    }
    try:
        d = parse_demand(offline["demand"])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        base["note"] = f"demand payload did not parse: {type(exc).__name__}"
        return base

    base["date"] = d["date"]
    base["ercot_stamp"] = d["ercot_stamp"]
    base["hour_ending"] = d["hour_ending"]
    base["load_mw"] = d["load_mw"]
    base["day_ahead_forecast_mw"] = d["day_ahead_forecast_mw"]
    base["capacity_mw"] = d["capacity_mw"]
    base.update(summarise(d))
    base["verified"] = base["hours_measured"] == base["hours_in_day"] > 0
    if not base["verified"]:
        base["note"] = (f"incomplete day: {base['hours_measured']} of "
                        f"{base['hours_in_day']} hours measured")

    if offline.get("fuel_mix"):
        try:
            fm = parse_fuel_mix(offline["fuel_mix"], d["date"])
        except (ValueError, TypeError, json.JSONDecodeError):
            fm = None
        if fm:
            base.update(fm)
            base["generation_load_gap_pct"] = _reconcile(base)
        else:
            base["note"] = (base["note"] + "; " if base["note"] else "") + \
                "fuel mix absent for this day"
    return base


def _reconcile(rec: dict) -> float | None:
    """Total generation against total load, as a percentage of load.

    TWO FEEDS, PARSED SEPARATELY, THAT MUST AGREE. Everything generated in an interconnection
    is consumed in it, so the day's generation summed across fuels has to land on the day's
    load, off only by DC tie flows and losses. On the first real day collected it landed within
    0.11 percent.

    That makes this the cheapest and by far the strongest integrity check available here. Both
    parsers read undocumented payloads that can change shape without notice, and a silent shape
    change is the failure mode that hurts: it does not raise, it just files a wrong number into
    a series nobody can rebuild. Nothing else in this file would notice. A reconciliation that
    suddenly reads eleven percent instead of one tenth of one percent is impossible to miss.

    It is computed and published, never asserted, and it is not a verdict about the grid. It is
    a statement about our own arithmetic, which is the one thing this project is allowed to
    make claims about.
    """
    load = rec.get("energy_mwh")
    fuels = rec.get("fuel_energy_mwh")
    if not isinstance(load, (int, float)) or not load or not isinstance(fuels, dict):
        return None
    gen = sum(v for v in fuels.values() if isinstance(v, (int, float)))
    return round((gen - load) / load * 100.0, 3)


# --------------------------------------------------------------------------- ledger
def append(rec: dict, ledger: Path = LEDGER) -> None:
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, separators=(",", ":"), sort_keys=True) + "\n")


def held(date: str, ledger: Path = LEDGER) -> dict | None:
    """The record currently standing for a date, which is the LAST one written for it.

    Append only is not the same as write once. A run that catches an incomplete day may be
    followed by one that catches it whole, and the later record supersedes the earlier without
    erasing it. Readers take the last line for a date; the earlier lines stay as the audit
    trail of what was known when.
    """
    if not ledger.exists():
        return None
    out = None
    for line in ledger.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("date") == date:
            out = rec
    return out


def worth_writing(new: dict, old: dict | None) -> bool:
    """Would this record improve on what we already hold for its day?"""
    if old is None:
        return True
    if old.get("verified"):
        return False                       # a settled complete day is never rewritten
    return new.get("hours_measured", 0) > old.get("hours_measured", 0) or bool(new.get("verified"))


# --------------------------------------------------------------------------- collect
def collect() -> int:
    # SNAPSHOT BEFORE PARSING. A parse bug must never cost the day: bytes on disk can be
    # re-parsed by a later fix, and a day never fetched cannot be recovered from anywhere.
    payloads: dict[str, bytes] = {}
    errors: list[str] = []
    for name, url in FEEDS.items():
        try:
            payloads[name] = fetch(url)
        except Exception as exc:                                   # noqa: BLE001
            errors.append(f"{name}: {type(exc).__name__}")
            print(f"gridwatch: {name} fetch failed: {exc}", file=sys.stderr)

    if "demand" not in payloads:
        # No demand payload means no date, so there is no day to file this against. Say so
        # loudly and write nothing: a record with a guessed date is worse than a visible gap,
        # and the gap is recoverable for another day.
        print(f"gridwatch: no demand payload ({'; '.join(errors)}), nothing recorded",
              file=sys.stderr)
        return 1

    rec = reading(offline=payloads)
    if errors:
        rec["note"] = (rec["note"] + "; " if rec["note"] else "") + "fetch errors: " + \
            "; ".join(errors)

    if rec["date"]:
        # THE ARCHIVE, GZIPPED. The ledger stores the hourly series, so the raw is not needed
        # to redraw the page; it is needed the day a parse turns out to have been wrong, or a
        # question gets asked that wants five-minute fuel data this file never summarised.
        # Uncompressed that is about sixty megabytes a year in a repo every cron clones, which
        # is enough to make someone delete it. Compressed it is about six, which is enough to
        # keep forever, and keeping it forever is the entire point.
        RAW.mkdir(parents=True, exist_ok=True)
        for name, body in payloads.items():
            with gzip.open(RAW / f"{rec['date']}-{name}.json.gz", "wb", compresslevel=9) as fh:
                fh.write(body)

    standing = held(rec["date"]) if rec["date"] else None
    if not worth_writing(rec, standing):
        print(f"gridwatch: {rec['date']} already held complete, nothing to do")
        return 0

    append(rec)
    state = "verified" if rec["verified"] else "UNVERIFIED"
    print(f"gridwatch: {rec['date']} {state} peak={rec.get('peak_load_mw')} MW "
          f"load_factor={rec.get('load_factor')} "
          f"forecast_error={rec.get('peak_forecast_error_mw')} MW {rec['note']}".rstrip())
    return 0


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    """Hermetic. No network. This gates every scheduled collection, so it must never need one."""
    import tempfile
    failures = 0

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    def day(n_hours=24, load=None, fc=None, cap=None, date="2026-08-10"):
        load = load if load is not None else [60000.0 + 1000 * i for i in range(n_hours)]
        fc = fc if fc is not None else [None if v is None else v + 500 for v in load]
        cap = cap if cap is not None else [95000.0] * n_hours
        rows = [{"hourEnding": i + 1, "dstFlag": "N", "epoch": 1000 + i,
                 "systemLoad": load[i], "dayAheadForecast": fc[i], "currentDayHsl": cap[i],
                 "timestamp": f"{date} {i + 1:02d}:00:00-0500"} for i in range(n_hours)]
        rows = [{k: v for k, v in r.items() if v is not None} for r in rows]
        return json.dumps({"lastUpdated": f"{date} 23:59:00-0500",
                           "previousDay": {"dayDate": f"{date} 00:00:00-0500", "data": rows},
                           "currentDay": {"dayDate": "x", "data": []}}).encode()

    r = reading(offline={"demand": day()})
    check("a complete day verifies", r["verified"] is True, r["note"])
    check("the date comes from the payload, not the clock", r["date"] == "2026-08-10", r["date"])
    check("the peak is the measured maximum", r["peak_load_mw"] == 83000.0,
          str(r["peak_load_mw"]))
    check("the peak carries the hour it happened in", r["peak_hour_ending"] == 24,
          str(r["peak_hour_ending"]))
    check("the trough is the measured minimum", r["min_load_mw"] == 60000.0,
          str(r["min_load_mw"]))
    check("energy is the sum of the hourly averages",
          r["energy_mwh"] == _r(sum(60000.0 + 1000 * i for i in range(24))), str(r["energy_mwh"]))
    check("the load factor is mean over peak", r["load_factor"] == round(
        (sum(60000.0 + 1000 * i for i in range(24)) / 24) / 83000.0, 4), str(r["load_factor"]))
    check("the reserve at peak is capacity minus load there",
          r["reserve_at_peak_mw"] == 12000.0, str(r["reserve_at_peak_mw"]))
    check("the full hourly series is stored, not just the summary",
          len(r["load_mw"]) == 24 and len(r["day_ahead_forecast_mw"]) == 24)
    check("measured values are stored unrounded, exactly as published",
          r["load_mw"][0] == 60000.0)

    # THE ACCURACY CHECK. ERCOT's model against ERCOT's telemetry, computed here.
    check("the peak forecast error is signed, so the direction survives",
          r["peak_forecast_error_mw"] == 500.0, str(r["peak_forecast_error_mw"]))
    over_under = reading(offline={"demand": day(
        load=[70000.0] * 24, fc=[71000.0] * 12 + [69000.0] * 12)})
    check("mean absolute error does not let overs and unders cancel",
          over_under["mean_absolute_forecast_error_mw"] == 1000.0,
          str(over_under["mean_absolute_forecast_error_mw"]))

    # DST. A collector that hardcodes 24 files a wrong mean twice a year.
    spring = reading(offline={"demand": day(n_hours=23, date="2027-03-14")})
    check("a 23 hour spring forward day is complete, not short",
          spring["verified"] is True and spring["hours_in_day"] == 23, spring["note"])
    fall = reading(offline={"demand": day(n_hours=25, date="2027-11-07")})
    check("a 25 hour fall back day is complete, not over long",
          fall["verified"] is True and fall["hours_in_day"] == 25, fall["note"])
    check("the mean divides by the hours that exist, not by 24",
          fall["mean_load_mw"] == _r(sum(60000.0 + 1000 * i for i in range(25)) / 25),
          str(fall["mean_load_mw"]))

    # THE RULE THAT MATTERS MOST. A failure produces an explicit unverified record with no
    # number in it, never a number carried forward.
    bad = reading(offline={"demand": b"{not json"})
    check("a broken payload still returns a record", isinstance(bad, dict))
    check("...marked unverified", bad["verified"] is False)
    check("...carrying NO number forward",
          bad.get("peak_load_mw") is None and bad.get("load_mw") is None)
    check("...and saying why", "did not parse" in bad["note"], bad["note"])

    for label, payload in (
        ("an empty previousDay", json.dumps({"previousDay": {"dayDate": "2026-08-10",
                                                             "data": []}}).encode()),
        ("a missing previousDay", json.dumps({"currentDay": {"data": []}}).encode()),
        ("a dateless previousDay", json.dumps({"previousDay": {"data": [{"systemLoad": 1}]}
                                               }).encode()),
    ):
        rec = reading(offline={"demand": payload})
        check(f"{label} is unverified, not zero",
              rec["verified"] is False and rec.get("peak_load_mw") is None, rec["note"])

    part = reading(offline={"demand": day(load=[60000.0] * 18 + [None] * 6)})
    check("a partial day is recorded as partial, with its real hour count",
          part["verified"] is False and part["hours_measured"] == 18
          and part["hours_in_day"] == 24, part["note"])
    check("a partial day still publishes the peak it did measure",
          part["peak_load_mw"] == 60000.0, str(part["peak_load_mw"]))

    nocap = reading(offline={"demand": day(cap=[None] * 24)})
    check("a missing capacity leaves the reserve null rather than guessed",
          nocap["reserve_at_peak_mw"] is None and nocap["peak_load_mw"] == 83000.0)

    # Fuel mix rides along, and never takes the load series down with it.
    fm = json.dumps({"data": {"2026-08-10": {
        f"2026-08-10 {h:02d}:{m:02d}:00-0500": {"Natural Gas": {"gen": 30000.0},
                                                "Wind": {"gen": 10000.0},
                                                "Power Storage": {"gen": -500.0}}
        for h in range(24) for m in (0, 30)}}}).encode()
    withfuel = reading(offline={"demand": day(), "fuel_mix": fm})
    check("fuel energy is generation integrated over the day, not a sample sum",
          withfuel["fuel_energy_mwh"]["Natural Gas"] == 720000.0,
          str(withfuel["fuel_energy_mwh"]["Natural Gas"]))
    check("storage stays signed, so charging is not published as generation",
          withfuel["fuel_energy_mwh"]["Power Storage"] == -12000.0,
          str(withfuel["fuel_energy_mwh"]["Power Storage"]))
    wrongday = reading(offline={"demand": day(), "fuel_mix": json.dumps(
        {"data": {"1999-01-01": {"t": {"Wind": {"gen": 1.0}}}}}).encode()})
    check("a fuel mix for another day is refused, not attached to this one",
          "fuel_energy_mwh" not in wrongday and "fuel mix absent" in wrongday["note"],
          wrongday["note"])
    check("...and the load series survives it",
          wrongday["peak_load_mw"] == 83000.0 and wrongday["verified"] is True)
    brokenfuel = reading(offline={"demand": day(), "fuel_mix": b"{not json"})
    check("a broken fuel mix never takes the load record down with it",
          brokenfuel["peak_load_mw"] == 83000.0 and "fuel_energy_mwh" not in brokenfuel)

    # THE RECONCILIATION. Two undocumented feeds, parsed separately, that physics says must
    # agree. This is what catches a silent shape change in either one.
    flat = [70000.0] * 24                                    # 1,680,000 MWh of load
    even = json.dumps({"data": {"2026-08-10": {
        f"2026-08-10 {h:02d}:{m:02d}:00-0500": {"Natural Gas": {"gen": 70000.0}}
        for h in range(24) for m in (0, 30)}}}).encode()
    rec = reading(offline={"demand": day(load=flat), "fuel_mix": even})
    check("generation matching load reconciles to zero",
          rec["generation_load_gap_pct"] == 0.0, str(rec["generation_load_gap_pct"]))
    skewed = json.dumps({"data": {"2026-08-10": {
        f"2026-08-10 {h:02d}:{m:02d}:00-0500": {"Natural Gas": {"gen": 77000.0}}
        for h in range(24) for m in (0, 30)}}}).encode()
    drift = reading(offline={"demand": day(load=flat), "fuel_mix": skewed})
    check("a feed drifting ten percent shows up as ten percent, not as silence",
          drift["generation_load_gap_pct"] == 10.0, str(drift["generation_load_gap_pct"]))
    check("the reconciliation is signed, so a shortfall reads differently from a surplus",
          reading(offline={"demand": day(load=flat), "fuel_mix": json.dumps(
              {"data": {"2026-08-10": {
                  f"2026-08-10 {h:02d}:{m:02d}:00-0500": {"Natural Gas": {"gen": 63000.0}}
                  for h in range(24) for m in (0, 30)}}}).encode()}
                  )["generation_load_gap_pct"] == -10.0)
    check("no fuel mix means no reconciliation, rather than a reconciliation against zero",
          reading(offline={"demand": day()}).get("generation_load_gap_pct") is None)

    # NO RELIABILITY VERDICT. Not ours, and not ERCOT's quoted as ours.
    banned = {"shortfall", "emergency", "safe", "unsafe", "all clear", "blackout", "risk",
              "risky", "warning", "alert", "critical", "danger", "dangerous", "conservation",
              "eea", "condition_note", "energy_level_value"}
    text = json.dumps(withfuel).lower()
    hits = sorted(w for w in banned if w in text)
    check("no reliability verdict vocabulary reaches a record", not hits, str(hits))
    check("the reliability feed is not among the feeds collected",
          not any("prc" in u for u in FEEDS.values()), str(list(FEEDS)))

    with tempfile.TemporaryDirectory() as td:
        led = Path(td) / "readings.jsonl"
        append(r, led)
        check("a reading appends one line", led.read_text().count("\n") == 1)
        check("the day is then held", (held("2026-08-10", led) or {}).get("verified") is True)
        check("a different day is not", held("2026-09-01", led) is None)
        check("a complete day is never rewritten", not worth_writing(r, held("2026-08-10", led)))

        led2 = Path(td) / "supersede.jsonl"
        append(part, led2)
        check("an incomplete day invites a better record", worth_writing(r, held(
            part["date"], led2)))
        check("...but not a worse one", not worth_writing(
            reading(offline={"demand": day(load=[60000.0] * 6 + [None] * 18)}),
            held(part["date"], led2)))
        append(r, led2)
        check("the superseding record is the one that stands",
              (held("2026-08-10", led2) or {}).get("verified") is True)
        check("...and the earlier one is still on disk, unrewritten",
              len(led2.read_text().strip().splitlines()) == 2)

    if failures:
        print(f"\ngridwatch_collect self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\ngridwatch_collect self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--collect", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.collect:
        # The self-test gates every collection. A collector whose own checks are broken has no
        # business appending to a series nobody can rebuild.
        if self_test() != 0:
            print("gridwatch: self-test failed, refusing to collect", file=sys.stderr)
            return 1
        return collect()
    ap.print_help()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                       # noqa: BLE001
        print(f"gridwatch_collect: broke: {exc}", file=sys.stderr)
        sys.exit(1)
