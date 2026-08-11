#!/usr/bin/env python3
"""docket_staleness.py — which docket items must be re-verified TODAY, ranked and capped.

WHY A SCRIPT CHOOSES AND NOT THE RUN

The sibling product learned this the expensive way and the lesson ports whole. Its rule was
prose: re-check anything "whose next key date is within 7 days or has passed, bounded work, a
handful of fetches at most." It leaked, and the maintainer caught it: "I am afraid that it is
not checking each item daily."

Measured that day, nine of seventeen live items had NO future key date at all, so every one of
them fell through the "or has passed" clause. That nominates nine items at once against a budget
of "a handful", with no priority order and no record of which ones lost. Whichever items a run
happened to notice got checked and the rest aged in silence. One sat 19 days at pending. Another
sat 11.

THE BLIND SPOT WAS WORST WHERE THE STAKES WERE HIGHEST. The single largest item on that docket
was awaiting a decision with no published date, which meant it had no future key date, which
meant the selector meant to catch breaking changes was structurally least able to see the item
most likely to break.

So: an item awaiting an unscheduled decision is not a quiet item, it is the LOUDEST one. It gets
a three day leash here.

Three properties this tool must keep:

  1 IT RANKS. Urgency is computed, so the run never picks favourites.
  2 IT ALWAYS PRINTS WHAT IT DEFERRED. A cap that does not announce itself is
    indistinguishable from full coverage, which is exactly how the leak went unnoticed.
  3 IT NAMES WHAT IS ROTTEN. Past twice its limit while still live is a different and worse
    condition than merely due, and it exits non-zero so a scheduled check cannot ignore it.

    docket_staleness.py --today 2026-08-11 --budget 6
    docket_staleness.py --json
    docket_staleness.py --self-test

EXIT CODES
    0  nothing rotten          2  at least one item is rotten          1  the tool broke
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "ledger" / "docket.json"

# How long an item of each status may go unverified before it is due. A live window gets the
# tightest ordinary leash because the page is actively telling a reader they can still act.
SLA = {
    "open": 3,
    "pending": 7,
    "unknown": 7,
}
SLA_TERMINAL = {
    "decided": 30,
    "withdrawn": 60,
}
# Statuses where the world can still move under us.
LIVE = {"open", "pending", "unknown"}

# The unscheduled-decision leash. See the module docstring.
UNSCHEDULED_LEASH = 3


def parse_date(s) -> _dt.date:
    return _dt.date.fromisoformat(str(s))


def assess(item: dict, today: _dt.date) -> dict:
    status = item.get("status", "unknown")
    sla = SLA.get(status, SLA_TERMINAL.get(status, 14))
    last = item.get("last_verified")
    try:
        age = (today - parse_date(last)).days if last else 9999
    except ValueError:
        age = 9999

    dates = []
    for k in item.get("key_dates") or []:
        try:
            dates.append(parse_date(k["date"]))
        except (ValueError, KeyError):
            continue
    dates.sort()
    future = [d for d in dates if d >= today]
    next_key = future[0] if future else None
    days_to_next = (next_key - today).days if next_key else None

    unscheduled = status in LIVE and not future

    # The unscheduled case TIGHTENS the limit rather than standing on its own as a reason. An
    # item whose next event has no announced date can change on any morning, so it earns a
    # shorter leash. It does NOT earn being listed as due on a day it was just verified: a
    # worklist that names things the run did an hour ago is a worklist the run learns to skim,
    # and then the one real entry goes past with the noise.
    if unscheduled:
        sla = min(sla, UNSCHEDULED_LEASH)

    reasons, urgency = [], 0.0
    if age > sla:
        reasons.append(f"{age}d since last verified, over its {sla}d limit")
        urgency += (age - sla) / max(1.0, sla)
        if unscheduled:
            reasons.append("no scheduled event, so any change arrives unannounced")
            urgency += 2.0
        if status == "open":
            reasons.append("the page is telling a reader they can still act")
            urgency += 1.0

    # A near key date is its own trigger, because the day a window closes is the day the page
    # must be right, whatever its last-verified stamp says. Still not on the same day it was
    # checked.
    if days_to_next is not None and days_to_next <= 7 and age >= 1:
        reasons.append(f"key date in {days_to_next}d")
        urgency += 2.5 - (days_to_next * 0.2)

    return {
        "id": item.get("id"),
        "title": str(item.get("title", ""))[:60],
        "status": status,
        "age_days": age,
        "sla_days": sla,
        "due": bool(reasons),
        "rotten": age > sla * 2 and status in LIVE,
        "days_to_next_key": days_to_next,
        "no_scheduled_event": unscheduled,
        "urgency": round(urgency, 2),
        "reasons": reasons,
    }


def select(items: list, today: _dt.date, budget: int) -> tuple[list, list, list]:
    rows = [assess(i, today) for i in items]
    due = sorted([r for r in rows if r["due"]], key=lambda r: -r["urgency"])
    return due[:budget], due[budget:], [r for r in rows if r["rotten"]]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--today", default=_dt.date.today().isoformat())
    ap.add_argument("--budget", type=int, default=6,
                    help="how many items this run will actually re-fetch")
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        return self_test()

    path = Path(a.ledger)
    if not path.exists():
        print(f"docket_staleness: no ledger at {path}", file=sys.stderr)
        return 1
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = raw if isinstance(raw, list) else raw.get("items", [])
    today = parse_date(a.today)
    work, deferred, rotten = select(items, today, a.budget)

    if a.json:
        print(json.dumps({"work": work, "deferred": deferred, "rotten": rotten}, indent=1))
        return 2 if rotten else 0

    print(f"docket staleness  {a.today}  budget {a.budget}  of {len(items)} item(s)\n")
    if not work:
        print("  nothing due today")
    for r in work:
        print(f"  [{r['urgency']:5.2f}] {r['id']}  ({r['status']}, {r['age_days']}d old)")
        print(f"           {r['title']}")
        for why in r["reasons"]:
            print(f"           - {why}")

    # A cap that does not announce itself is indistinguishable from full coverage.
    if deferred:
        print(f"\n  DEFERRED past the --budget of {a.budget}. THESE ARE NOT COVERED TODAY:")
        for r in deferred:
            print(f"    {r['id']}  ({r['age_days']}d old, urgency {r['urgency']})")
        print("    Raise --budget, or carry them at the top of tomorrow's list.")

    if rotten:
        print("\n  ROTTEN, past TWICE the limit while still live:")
        for r in rotten:
            print(f"    {r['id']}  ({r['age_days']}d old against a {r['sla_days']}d limit)")
        print("    Re-verify these BEFORE writing anything new.")
    return 2 if rotten else 0


def self_test() -> int:
    """Prove the selector catches what it was built to catch."""
    failures = 0
    today = _dt.date(2026, 8, 11)

    def item(**o):
        d = {"id": "x", "title": "t", "status": "pending",
             "last_verified": "2026-08-11", "key_dates": []}
        d.update(o)
        return d

    def expect(label, got, want):
        nonlocal failures
        ok = got == want
        print(f"  {'ok  ' if ok else 'FAIL'}  {label}")
        if not ok:
            failures += 1
            print(f"        got {got!r}, wanted {want!r}", file=sys.stderr)

    # The core regression: an item with NO future key date, awaiting an unscheduled decision.
    a = assess(item(last_verified="2026-08-07"), today)          # 4 days, no future date
    expect("an unscheduled live item is due at 4 days, on a 3 day leash", a["due"], True)
    expect("...and the leash is 3, not the status default of 7", a["sla_days"], 3)
    expect("...and it says why", "no scheduled event" in " ".join(a["reasons"]), True)

    # ...but not the day it was checked. This is what stops the worklist becoming noise.
    b = assess(item(last_verified="2026-08-11"), today)
    expect("an unscheduled item verified today is NOT due", b["due"], False)

    # A scheduled item keeps the ordinary leash.
    c = assess(item(last_verified="2026-08-07",
                    key_dates=[{"date": "2026-12-01", "kind": "hearing"}]), today)
    expect("a scheduled item at 4 days is not yet due", c["due"], False)
    expect("...and keeps its 7 day limit", c["sla_days"], 7)

    # A near key date triggers on its own, whatever the stamp says.
    d = assess(item(last_verified="2026-08-10",
                    key_dates=[{"date": "2026-08-13", "kind": "comment_closes"}]), today)
    expect("a key date in 2 days is due even at 1 day old", d["due"], True)

    # An open window outranks a pending item of the same age.
    o = assess(item(status="open", last_verified="2026-08-01"), today)
    p = assess(item(status="pending", last_verified="2026-08-01"), today)
    expect("an open window outranks a pending item of equal age", o["urgency"] > p["urgency"],
           True)

    # Rot.
    r = assess(item(status="open", last_verified="2026-07-20"), today)   # 22d on a 3d leash
    expect("past twice the limit while live is rotten", r["rotten"], True)
    expect("a decided item ages slowly", assess(
        item(status="decided", last_verified="2026-08-01"), today)["due"], False)

    # The budget must announce what it dropped.
    items = [item(id=f"i{n}", status="open", last_verified="2026-07-25") for n in range(9)]
    work, deferred, rot = select(items, today, budget=6)
    expect("the budget caps the worklist at 6", len(work), 6)
    expect("...and the other 3 are reported as deferred, never dropped", len(deferred), 3)
    expect("...and all 9 are rotten and named", len(rot), 9)

    if failures:
        print(f"\ndocket_staleness self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\ndocket_staleness self-test: all passed")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                    # noqa: BLE001
        print(f"docket_staleness: broke: {exc}", file=sys.stderr)
        sys.exit(1)
