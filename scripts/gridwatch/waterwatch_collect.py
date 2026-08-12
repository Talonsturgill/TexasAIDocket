#!/usr/bin/env python3
"""waterwatch_collect.py — one measured day of Texas reservoir storage, every day, forever.

THE SECOND DAILY INSTRUMENT, AND WHY IT IS THIS ONE

Water was chosen over the obvious alternative on measured evidence. The US Drought Monitor is
the instrument everyone reaches for, and it is WEEKLY: pulled on three consecutive days it
returned an identical figure for Travis County all three times. A daily page fed by weekly data
republishes an unchanged number six days in seven, which trains a reader to stop looking. Texas
reservoir storage moved 26,085 acre feet in a single day.

It also needs no modeled component at all. Storage, capacity, percent full and day over day
deltas are arithmetic over a fetched payload. The grid watch has to carry a modeled figure and
label it; this does not, which makes it the cleaner companion rather than a second version of
the same caveat.

WHY IT READS THE JSON AND NOT THE CSV, WHICH IS A RULE AND NOT A PREFERENCE

`waterdatafortexas.org/robots.txt` says, today, verbatim:

    User-agent: *
    Disallow: *.csv
    Disallow: /*?output_format=*
    Disallow: /coastal/api/*
    Disallow: /reservoirs/api/*

The reservoir CSVs, including the statewide file with 94 years of daily history, fall inside
`Disallow: *.csv`. So they are not collected here, and the history that comes with them is not
ours to have. `recent-conditions.json` is neither a CSV nor under an api path, and it is what
this file reads. One request per day.

THE COST OF THAT, PUBLISHED RATHER THAN HIDDEN. Without the archive there is no 94 year
percentile to rank today against, so the page does not print one. It prints instead that the
comparison exists, that the publisher has asked crawlers not to take the file it lives in, and
that our own history therefore starts the day we started. That is a smaller claim and a true
one.

THE TRAP THE DATA ITSELF MARKS

El Paso's only tagged reservoir is **Elephant Butte Lake, which is in New Mexico**, sitting at
1.4 percent full. Publishing that as El Paso's water supply would be a serious error, and it is
the second time El Paso has broken a default assumption about Texas, after the question of
whether it is inside ERCOT at all. It is not. TWDB already marks it: Elephant Butte is the only
record in the payload without a `texas` tag. So the statewide roll up requires that tag rather
than trusting a filename, and the self-test asserts the exclusion by name.

    waterwatch_collect.py --self-test        hermetic, gates every scheduled collection
    waterwatch_collect.py --collect
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
LEDGER = REPO_ROOT / "ledger" / "gridwatch" / "water.jsonl"
RAW = REPO_ROOT / "ledger" / "gridwatch" / "raw"

FEED = "https://www.waterdatafortexas.org/reservoirs/recent-conditions.json"
UA = ("TexasAIDocket/1.0 (+https://talonsturgill.github.io/TexasAIDocket; "
      "daily public-interest water record; one request per day)")

SPEC = 1

# The tag TWDB puts on reservoirs that are in Texas. Elephant Butte carries `new_mexico`
# instead, and is the only record in the payload that does. Requiring the positive tag rather
# than excluding the negative one means a second out of state reservoir added later is also
# excluded, without anybody having to notice it arrived.
IN_STATE = "texas"
METRO_PREFIX = "municipal_"


def fetch(url: str = FEED, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _num(x):
    return x if isinstance(x, (int, float)) else None


def parse(raw: bytes) -> dict:
    """One day of storage, per reservoir, rolled up statewide and by metro.

    NULL IS NOT ZERO. Two of the reservoirs in this payload are flood control dams with no
    conservation pool at all, so their storage is null. Treating that as zero would drag the
    statewide percentage down with dams that are supposed to be empty. They are excluded from
    every total, and the count of what was excluded is recorded so the omission is visible.
    """
    doc = json.loads(raw)
    if not isinstance(doc, dict) or not doc:
        raise ValueError("payload is not a reservoir map")

    stamps = {r.get("timestamp") for r in doc.values() if isinstance(r, dict)}
    stamps.discard(None)
    if not stamps:
        raise ValueError("payload carries no timestamp")
    # The payload stamps itself. Reading our own clock here would invent an answer that is
    # already published, and would be wrong on any day the feed lags.
    day = sorted(stamps)[-1]

    reservoirs: dict[str, dict] = {}
    excluded_no_pool: list[str] = []
    out_of_state: list[str] = []
    for key, r in sorted(doc.items()):
        if not isinstance(r, dict):
            continue
        tags = r.get("tags") or []
        if IN_STATE not in tags:
            out_of_state.append(key)
            continue
        s, c = _num(r.get("conservation_storage")), _num(r.get("conservation_capacity"))
        if s is None or c is None or c <= 0:
            excluded_no_pool.append(key)
            continue
        reservoirs[key] = {
            "storage_af": s,
            "capacity_af": c,
            "metros": sorted(t[len(METRO_PREFIX):] for t in tags
                             if t.startswith(METRO_PREFIX)),
        }

    storage = sum(v["storage_af"] for v in reservoirs.values())
    capacity = sum(v["capacity_af"] for v in reservoirs.values())

    metros: dict[str, dict] = {}
    for v in reservoirs.values():
        for m in v["metros"]:
            b = metros.setdefault(m, {"storage_af": 0.0, "capacity_af": 0.0, "reservoirs": 0})
            b["storage_af"] += v["storage_af"]
            b["capacity_af"] += v["capacity_af"]
            b["reservoirs"] += 1
    for m, b in metros.items():
        b["storage_af"] = round(b["storage_af"], 1)
        b["capacity_af"] = round(b["capacity_af"], 1)
        b["percent_full"] = round(b["storage_af"] / b["capacity_af"] * 100.0, 2) \
            if b["capacity_af"] else None

    # OUR ARITHMETIC AGAINST THEIRS. TWDB publishes a percent_full per reservoir; we never use
    # it, we compute from storage over capacity. Comparing the two is free and catches the day
    # their field means something other than what we assume it means.
    diffs = []
    for key, v in reservoirs.items():
        theirs = _num(doc[key].get("percent_full"))
        if theirs is not None and v["capacity_af"]:
            diffs.append(abs(v["storage_af"] / v["capacity_af"] * 100.0 - theirs))

    return {
        "date": day,
        "reservoirs": {k: {"storage_af": v["storage_af"], "capacity_af": v["capacity_af"]}
                       for k, v in reservoirs.items()},
        "reservoir_count": len(reservoirs),
        "storage_af": round(storage, 1),
        "capacity_af": round(capacity, 1),
        "percent_full": round(storage / capacity * 100.0, 2) if capacity else None,
        "metros": dict(sorted(metros.items())),
        "excluded_no_conservation_pool": sorted(excluded_no_pool),
        "excluded_out_of_state": sorted(out_of_state),
        "percent_full_max_disagreement": round(max(diffs), 3) if diffs else None,
    }


def reading(*, offline: bytes | None = None) -> dict:
    """One day's record. Always returns a record; never raises past a bad payload."""
    base = {"_spec": SPEC, "date": None, "source": "twdb recent-conditions",
            "verified": False, "note": ""}
    try:
        raw = offline if offline is not None else fetch()
        parsed = parse(raw)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
        base["note"] = f"fetch failed: {type(exc).__name__}"
        return base
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        base["note"] = f"payload did not parse: {type(exc).__name__}"
        return base

    base.update(parsed)
    base["verified"] = bool(parsed["reservoir_count"]) and parsed["percent_full"] is not None
    if not base["verified"]:
        base["note"] = "payload carried no usable reservoir"
    return base


def append(rec: dict, ledger: Path = LEDGER) -> None:
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, separators=(",", ":"), sort_keys=True) + "\n")


def held(date: str, ledger: Path = LEDGER) -> dict | None:
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


def collect() -> int:
    try:
        raw = fetch()
    except Exception as exc:                                       # noqa: BLE001
        print(f"waterwatch: fetch failed: {exc}", file=sys.stderr)
        return 1

    rec = reading(offline=raw)
    if not rec["date"]:
        print(f"waterwatch: no usable date ({rec['note']}), nothing recorded", file=sys.stderr)
        return 1

    standing = held(rec["date"])
    if standing and standing.get("verified"):
        print(f"waterwatch: {rec['date']} already held, nothing to do")
        return 0

    RAW.mkdir(parents=True, exist_ok=True)
    with gzip.open(RAW / f"{rec['date']}-water.json.gz", "wb", compresslevel=9) as fh:
        fh.write(raw)

    append(rec)
    state = "verified" if rec["verified"] else "UNVERIFIED"
    print(f"waterwatch: {rec['date']} {state} "
          f"{rec.get('percent_full')}% full across {rec.get('reservoir_count')} reservoirs "
          f"{rec['note']}".rstrip())
    return 0


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    import tempfile
    failures = 0

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    def res(storage, capacity, tags, pct=None, stamp="2026-08-11"):
        return {"conservation_storage": storage, "conservation_capacity": capacity,
                "tags": tags, "timestamp": stamp,
                "percent_full": pct if pct is not None else
                (round(storage / capacity * 100, 1) if storage and capacity else None)}

    payload = {
        "Travis": res(900000.0, 1000000.0, ["texas", "municipal_austin", "water_supply"]),
        "Buchanan": res(700000.0, 1000000.0, ["texas", "municipal_austin"]),
        "Houston": res(120000.0, 150000.0, ["texas", "municipal_houston"]),
        # THE TRAP. In New Mexico, tagged for El Paso, all but empty.
        "ElephantButte": res(27141.0, 1960900.0, ["new_mexico", "municipal_el_paso"]),
        # A flood control dam. Dry on purpose, and not a shortage.
        "Addicks": res(None, None, ["texas", "flood_control"]),
    }
    p = parse(json.dumps(payload).encode())

    check("the date comes from the payload, not the clock", p["date"] == "2026-08-11")
    check("Elephant Butte is excluded from the Texas total because it is in New Mexico",
          "ElephantButte" not in p["reservoirs"]
          and p["excluded_out_of_state"] == ["ElephantButte"])
    check("...and excluding it is done by requiring the texas tag, not by naming it",
          IN_STATE == "texas" and "ElephantButte" not in open(__file__).read().split(
              "def self_test")[0].split("IN_STATE")[1][:400])
    check("a flood control dam with no conservation pool is excluded, not counted as zero",
          "Addicks" not in p["reservoirs"]
          and p["excluded_no_conservation_pool"] == ["Addicks"])
    check("the statewide total is the sum of what remains",
          p["storage_af"] == 1720000.0 and p["capacity_af"] == 2150000.0,
          f'{p["storage_af"]} / {p["capacity_af"]}')
    check("percent full is computed, never taken from the feed",
          p["percent_full"] == 80.0, str(p["percent_full"]))
    check("the reservoir count counts what was counted", p["reservoir_count"] == 3)

    check("a metro rolls up only its own reservoirs",
          p["metros"]["austin"]["reservoirs"] == 2
          and p["metros"]["austin"]["storage_af"] == 1600000.0)
    check("...and gets its own computed percentage",
          p["metros"]["austin"]["percent_full"] == 80.0)
    check("El Paso does not appear as a metro at all, having no Texas reservoir",
          "el_paso" not in p["metros"], str(sorted(p["metros"])))

    # OUR ARITHMETIC AGAINST THEIRS.
    check("agreement with the publisher's own percentage is measured",
          p["percent_full_max_disagreement"] is not None
          and p["percent_full_max_disagreement"] < 0.1,
          str(p["percent_full_max_disagreement"]))
    skew = dict(payload, Houston=res(120000.0, 150000.0, ["texas", "municipal_houston"],
                                     pct=42.0))
    check("a publisher figure that disagrees with ours is surfaced, not silently preferred",
          parse(json.dumps(skew).encode())["percent_full_max_disagreement"] > 30)

    # A FAILED FETCH CARRIES NO NUMBER FORWARD.
    bad = reading(offline=b"{not json")
    check("a broken payload still returns a record", isinstance(bad, dict))
    check("...marked unverified", bad["verified"] is False)
    check("...carrying NO number forward",
          bad.get("storage_af") is None and bad.get("percent_full") is None)
    check("...and saying why", "did not parse" in bad["note"], bad["note"])
    for label, doc in (("an empty payload", b"{}"), ("a list", b"[]"),
                       ("a payload with no timestamp",
                        json.dumps({"A": {"conservation_storage": 1}}).encode())):
        r = reading(offline=doc)
        check(f"{label} is unverified, not zero",
              r["verified"] is False and r.get("storage_af") is None, r["note"])

    only_out = reading(offline=json.dumps({"ElephantButte": payload["ElephantButte"]}).encode())
    check("a payload with nothing in Texas is unverified rather than zero percent full",
          only_out["verified"] is False and only_out["percent_full"] is None,
          str(only_out.get("percent_full")))

    ok = reading(offline=json.dumps(payload).encode())
    check("a good payload verifies", ok["verified"] is True)
    check("the per reservoir series is stored, so the roll ups are recomputable",
          set(ok["reservoirs"]) == {"Travis", "Buchanan", "Houston"})
    check("capacity is stored too, so a resurvey shows up instead of moving history silently",
          ok["reservoirs"]["Travis"]["capacity_af"] == 1000000.0)

    # NO VERDICT. Water has no red zone to imply either.
    banned = {"drought", "shortage", "crisis", "emergency", "critical", "safe", "warning"}
    txt = json.dumps(ok).lower()
    check("no verdict vocabulary reaches a record",
          not (banned & set(txt.replace('"', " ").replace(":", " ").split())))

    with tempfile.TemporaryDirectory() as td:
        led = Path(td) / "w.jsonl"
        append(ok, led)
        check("a reading appends one line", led.read_text().count("\n") == 1)
        check("the day is then held", (held("2026-08-11", led) or {}).get("verified") is True)
        check("a different day is not", held("2026-01-01", led) is None)

    if failures:
        print(f"\nwaterwatch_collect self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\nwaterwatch_collect self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--collect", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.collect:
        if self_test() != 0:
            print("waterwatch: self-test failed, refusing to collect", file=sys.stderr)
            return 1
        return collect()
    ap.print_help()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                       # noqa: BLE001
        print(f"waterwatch_collect: broke: {exc}", file=sys.stderr)
        sys.exit(1)
