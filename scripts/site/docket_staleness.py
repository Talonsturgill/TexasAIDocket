#!/usr/bin/env python3
"""docket_staleness.py — which docket items must be re-verified TODAY, ranked and uncapped.

THE LEASH IS TWO DAYS, FOR EVERY ITEM, AND THERE IS NO BUDGET (owner's call, 2026-08-18)

This tool used to hand back a capped list. Statuses carried different leashes, 3 to 60 days,
and `--budget` truncated whatever survived. Both are gone. Every item on the record is due
every two days, whatever its status, and the work list is however long that is.

The owner's reasoning, and it is the right reading of what this product sells: re-verification
IS the product. A docket whose items quietly age is a docket that lies slowly. A cap is a
promise to check less than the record needs, made by whoever set the number, and the number was
set for the convenience of the run rather than for the reader.

The arithmetic is not frightening. 61 items on a two day leash is about 30 due on an ordinary
day, which is a morning of fetches, not an impossible one. If it is 30 tomorrow the tool is
doing its job.

DECIDED ITEMS GET THE SAME TWO DAYS. That was the one place a longer leash could be argued for,
since a decided fact does not move. It is still two days, because "this was decided" is exactly
the class of claim that goes stale without announcing itself: a decision gets appealed,
rescinded, superseded or corrected, and the item that says it is settled is the one nobody
looks at again.

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

So: an item awaiting an unscheduled decision is not a quiet item, it is the LOUDEST one. Under
the flat two day leash it no longer needs its own shorter rule, because nothing is slower than
it any more. The urgency ranking still lifts it, which is what decides the ORDER a run works in
now that nothing is dropped from the list.

Three properties this tool must keep:

  1 IT RANKS. Urgency is computed, so the run never picks favourites. With no cap the ranking
    no longer decides WHO gets checked, only the order, which is how it should have been.
  2 IT ALWAYS PRINTS WHAT IT DEFERRED. There is nothing to defer by default any more. If a run
    passes --budget by hand the deferred list still prints, loudly, because a cap that does not
    announce itself is indistinguishable from full coverage and that is how the leak went
    unnoticed the first time.
  3 IT NAMES WHAT IS ROTTEN. Past twice its limit while still live is a different and worse
    condition than merely due, and it exits non-zero so a scheduled check cannot ignore it.

  4 IT SEPARATES CANNOT FROM DID NOT (2026-09-23). Rot is the run's failure to do reachable
    work. An item whose own front door is shut to every client this routine has is a
    different condition, it is a published limit of the record, and working harder does not
    touch it. Three Hays County items sat on a vendor agenda portal serving
    `Disallow: /` to `User-agent: *`. Their movement notes had said so for three days running,
    the tool called them ROTTEN every day, and the remedy it printed, re-verify these before
    writing anything new, was one no run could take. A gate whose remedy is impossible is a
    gate that goes red forever and is then read as noise, which is the exact failure this
    repo's own notes record about `remote rejected` on a push that landed.

    SO IT IS NOT AN EXEMPTION AND IT IS NOT FREE. Three things hold it down:

      - IT IS EARNED BY EVIDENCE THE ITEM CARRIES, never by a status. The item declares
        `unreachable` with the hosts, the boundary, and the DATE the boundary was measured.
        No block, no carve-out. A run that wants the red to stop must go and look.
      - IT IS TIED TO THE ITEM'S FRONT DOOR. `public_access.url`'s host must be one of the
        named hosts, so this covers an item a reader can't reach either, rather than an item
        whose incidental third source happens to be shut.
      - IT LAPSES IN 7 DAYS. A robots file is a live document and this repo's rule is to
        re-check it per host. An unreachable block older than the window stops counting and
        the item is rotten again, which is what makes the carve-out a standing obligation
        rather than a note that silences a gate once.

    It is also LOUD. Unreachable items print in their own section every run, with their age
    and the boundary, whether or not anything else is due. They are not hidden, they are
    filed under the right heading.

    docket_staleness.py --today 2026-08-11
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
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "ledger" / "docket.json"
TEXAS_TIME = ZoneInfo("America/Chicago")

# ONE LEASH, EVERY ITEM, WHATEVER ITS STATUS. Owner's call on 2026-08-18. See the docstring:
# a per-status table meant that the items nobody was worried about were the items nobody
# checked, and "decided" is precisely the status that goes wrong quietly.
LEASH_DAYS = 2

SLA = {
    "open": LEASH_DAYS,
    "pending": LEASH_DAYS,
    "unknown": LEASH_DAYS,
}
SLA_TERMINAL = {
    "decided": LEASH_DAYS,
    "withdrawn": LEASH_DAYS,
}
# Statuses where the world can still move under us.
LIVE = {"open", "pending", "unknown"}

# How long a measured crawl boundary counts for. A robots file can change any day, so an
# `unreachable` block is a measurement with a shelf life rather than a standing exemption.
UNREACHABLE_WINDOW_DAYS = 7
UNREACHABLE_BOUNDARIES = {"robots", "blocks_every_client"}


def _host(url: str) -> str:
    """The netloc of a URL, lowercased, or "" for anything unparseable."""
    try:
        return urlparse(str(url or "")).netloc.lower()
    except ValueError:
        return ""


def unreachable_state(item: dict, today: _dt.date) -> dict | None:
    """Return the item's live crawl-boundary declaration, or None.

    None covers every way the claim can fail: no block, a block naming no hosts, a boundary
    this tool does not recognise, an undated or unparseable measurement, a measurement past
    the window, and a block whose hosts do not include the item's own front door. Each is a
    reason to keep calling the item rotten, because each leaves the assertion unproven.
    """
    block = item.get("unreachable")
    if not isinstance(block, dict):
        return None
    hosts = [str(h).lower() for h in (block.get("hosts") or []) if str(h).strip()]
    if not hosts:
        return None
    if str(block.get("boundary", "")) not in UNREACHABLE_BOUNDARIES:
        return None
    try:
        checked = parse_date(str(block.get("checked", "")))
    except Exception:
        return None
    age = (today - checked).days
    if age < 0 or age > UNREACHABLE_WINDOW_DAYS:
        return None
    door = _host((item.get("public_access") or {}).get("url"))
    if not door or door not in hosts:
        return None
    return {"hosts": hosts, "boundary": block.get("boundary"),
            "checked": checked.isoformat(), "checked_age_days": age,
            "note": str(block.get("note", ""))[:160]}

# The unscheduled-decision leash. Equal to the flat leash now, so it tightens nothing and is
# kept only so the reason for it stays readable beside the rule it used to carry.
UNSCHEDULED_LEASH = LEASH_DAYS


def texas_today(now: _dt.datetime | None = None) -> _dt.date:
    """Return today's date where this Texas record is published.

    Hosted runners keep their operating-system clock in UTC. Using ``date.today()`` there
    advances this gate at 7 p.m. Central during daylight time, so a September 1 record is
    judged as September 2 while every Texas reader is still on September 1. Start from an
    aware UTC instant and convert it explicitly so laptops and CI share the same day boundary.
    """
    instant = now if now is not None else _dt.datetime.now(_dt.timezone.utc)
    if instant.tzinfo is None:
        raise ValueError("texas_today requires an aware datetime")
    return instant.astimezone(TEXAS_TIME).date()


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

    unreachable = unreachable_state(item, today)

    return {
        "id": item.get("id"),
        "title": str(item.get("title", ""))[:60],
        "status": status,
        "age_days": age,
        "sla_days": sla,
        "due": bool(reasons),
        # STILL DUE, NEVER ROTTEN. An unreachable item stays on the work list, because the
        # boundary is what a run re-measures and the item is what it re-reads if it opens.
        # What it stops being is the run's failure to do work it could have done.
        "rotten": age > sla * 2 and status in LIVE and unreachable is None,
        "unreachable": unreachable,
        "days_to_next_key": days_to_next,
        "no_scheduled_event": unscheduled,
        "urgency": round(urgency, 2),
        "reasons": reasons,
    }


def select(items: list, today: _dt.date, budget: int | None) -> tuple[list, list, list]:
    """budget None means NO CAP, which is the default. Everything due is work.

    Slicing cannot express that on its own: `due[None:]` is the whole list, so a naive
    `due[:budget], due[budget:]` would report every due item as both worked and deferred.
    """
    rows = [assess(i, today) for i in items]
    due = sorted([r for r in rows if r["due"]], key=lambda r: -r["urgency"])
    rotten = [r for r in rows if r["rotten"]]
    if budget is None:
        return due, [], rotten
    return due[:budget], due[budget:], rotten


def unreachable_rows(items: list, today: _dt.date) -> list:
    """Every item whose crawl boundary is currently proven, oldest first."""
    rows = [assess(i, today) for i in items]
    return sorted([r for r in rows if r["unreachable"]], key=lambda r: -r["age_days"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--today", default=texas_today().isoformat())
    ap.add_argument("--budget", type=int, default=None,
                    help="OPTIONAL cap, for a run that is deliberately doing less. There is no "
                         "cap by default: everything due is work. A capped run prints what it "
                         "dropped, because a cap that does not announce itself is "
                         "indistinguishable from full coverage")
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

    blocked = unreachable_rows(items, today)

    if a.json:
        print(json.dumps({"work": work, "deferred": deferred, "rotten": rotten,
                          "unreachable": blocked}, indent=1))
        return 2 if rotten else 0

    cap = "no cap" if a.budget is None else f"capped at {a.budget}"
    print(f"docket staleness  {a.today}  leash {LEASH_DAYS}d, {cap}  "
          f"of {len(items)} item(s)\n")
    print(f"  {len(work)} due today\n")
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

    # Printed whether or not anything else is due, because the whole point is that these are
    # filed rather than hidden. The age is printed too: a reader of this output should be able
    # to see exactly how stale the record is admitting it has gone.
    if blocked:
        print(f"\n  UNREACHABLE, and NOT counted as rot. The boundary is measured, the record "
              f"can't go back to the source, and working harder does not touch it:")
        for r in blocked:
            u = r["unreachable"]
            print(f"    {r['id']}  ({r['age_days']}d since last verified, boundary "
                  f"{u['boundary']} on {', '.join(u['hosts'])}, measured {u['checked']}, "
                  f"{UNREACHABLE_WINDOW_DAYS - u['checked_age_days']}d left)")
        print(f"    RE-MEASURE the boundary within {UNREACHABLE_WINDOW_DAYS}d or these go "
              f"rotten again. Never route around one.")
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

    expect("UTC midnight is still the prior calendar day in Texas",
           texas_today(_dt.datetime(2026, 9, 2, 1, 35, tzinfo=_dt.timezone.utc)),
           _dt.date(2026, 9, 1))
    expect("the calendar advances after midnight in Texas",
           texas_today(_dt.datetime(2026, 9, 2, 5, 1, tzinfo=_dt.timezone.utc)),
           _dt.date(2026, 9, 2))

    # The core regression: an item with NO future key date, awaiting an unscheduled decision.
    a = assess(item(last_verified="2026-08-07"), today)          # 4 days, no future date
    expect("an unscheduled live item is due at 4 days", a["due"], True)
    expect("...and the leash is the flat 2, whatever the status", a["sla_days"], LEASH_DAYS)
    expect("...and it says why", "no scheduled event" in " ".join(a["reasons"]), True)

    # ...but not the day it was checked. This is what stops the worklist becoming noise.
    b = assess(item(last_verified="2026-08-11"), today)
    expect("an unscheduled item verified today is NOT due", b["due"], False)

    # A scheduled item used to buy a longer leash by having a date on the calendar. It does
    # not any more: a hearing in December is no reason to let the item age until then.
    c = assess(item(last_verified="2026-08-07",
                    key_dates=[{"date": "2026-12-01", "kind": "hearing"}]), today)
    expect("a scheduled item at 4 days IS due, its far-off date buys it nothing", c["due"], True)
    expect("...and it is on the same 2 day leash as everything else", c["sla_days"], LEASH_DAYS)
    d2 = assess(item(last_verified="2026-08-10",
                     key_dates=[{"date": "2026-12-01", "kind": "hearing"}]), today)
    expect("...but one day old is still inside the leash", d2["due"], False)

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
    # Decided items are on the SAME leash now. A decision that was appealed, rescinded or
    # superseded is exactly the claim that goes stale without announcing itself.
    expect("a decided item is due at 10 days like anything else", assess(
        item(status="decided", last_verified="2026-08-01"), today)["due"], True)
    expect("...and inside two days it is not", assess(
        item(status="decided", last_verified="2026-08-10"), today)["due"], False)
    expect("...but it is never ROTTEN, because rot is a live-item condition", assess(
        item(status="decided", last_verified="2026-08-01"), today)["rotten"], False)

    # NO CAP is the default, and that is the whole point of the 2026-08-18 change.
    items = [item(id=f"i{n}", status="open", last_verified="2026-07-25") for n in range(9)]
    work, deferred, rot = select(items, today, budget=None)
    expect("with no budget every due item is work", len(work), 9)
    expect("...and nothing is deferred", len(deferred), 0)
    expect("...and all 9 are rotten and named", len(rot), 9)

    # THE BUG THIS GUARDS: `due[None:]` is the whole list, so a naive slice would report every
    # due item as deferred as well as worked. That would have read as total coverage failure
    # on a run that actually covered everything.
    expect("no item is both worked and deferred",
           set(r["id"] for r in work) & set(r["id"] for r in deferred), set())

    # The optional cap still announces what it dropped, for a run deliberately doing less.
    work6, deferred6, _ = select(items, today, budget=6)
    expect("an explicit budget still caps the worklist", len(work6), 6)
    expect("...and the other 3 are reported as deferred, never dropped", len(deferred6), 3)

    # THE CRAWL BOUNDARY, and every way the claim can fail. Each `expect` below is one thing
    # a future edit could loosen without noticing, so each is pinned rather than described.
    def blocked(**o):
        d = {"hosts": ["public.destinyhosted.com"], "boundary": "robots",
             "checked": "2026-08-10", "note": "Disallow: / to User-agent: *"}
        d.update(o)
        return d
    door = {"url": "https://public.destinyhosted.com/agenda_publish.cfm?id=1", "room": "contact_only"}
    rotten_base = dict(status="open", last_verified="2026-07-20", public_access=door)

    expect("the same item with no block is rotten",
           assess(item(**rotten_base), today)["rotten"], True)
    ok = assess(item(unreachable=blocked(), **rotten_base), today)
    expect("a proven boundary takes it out of rot", ok["rotten"], False)
    expect("...and it is STILL due, because the boundary is what gets re-measured",
           ok["due"], True)
    expect("...and it is reported, never silent",
           unreachable_rows([item(unreachable=blocked(), **rotten_base)], today)[0]["id"], "x")

    expect("a block naming no hosts proves nothing", assess(
        item(unreachable=blocked(hosts=[]), **rotten_base), today)["rotten"], True)
    expect("a boundary this tool does not recognise proves nothing", assess(
        item(unreachable=blocked(boundary="site was slow"), **rotten_base), today)["rotten"], True)
    expect("an undated measurement proves nothing", assess(
        item(unreachable=blocked(checked=""), **rotten_base), today)["rotten"], True)
    expect("a measurement from the future proves nothing", assess(
        item(unreachable=blocked(checked="2026-09-01"), **rotten_base), today)["rotten"], True)
    # THE SHELF LIFE IS THE WHOLE DIFFERENCE between a measurement and an exemption. 2026-08-11
    # minus 7 days is 2026-08-04, so that date is the last one that still counts.
    expect("a measurement exactly at the window still counts", assess(
        item(unreachable=blocked(checked="2026-08-04"), **rotten_base), today)["rotten"], False)
    expect("...and one day past it does not", assess(
        item(unreachable=blocked(checked="2026-08-03"), **rotten_base), today)["rotten"], True)
    # A BLOCK THAT DOES NOT COVER THE ITEM'S OWN FRONT DOOR is a fact about some third source.
    expect("a block that misses the public_access host proves nothing", assess(
        item(unreachable=blocked(hosts=["www.axon.com"]), **rotten_base), today)["rotten"], True)
    expect("an item with no public_access url cannot claim one", assess(
        item(unreachable=blocked(), status="open", last_verified="2026-07-20"),
        today)["rotten"], True)
    expect("a block that is not an object proves nothing", assess(
        item(unreachable="robots", **rotten_base), today)["rotten"], True)

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
