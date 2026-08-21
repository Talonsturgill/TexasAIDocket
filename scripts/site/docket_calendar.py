#!/usr/bin/env python3
"""docket_calendar.py — the record arranged by when, instead of by how soon you can act.

WHY THIS EXISTS. The record page sorts by urgency, which is the right first answer and the
wrong only answer. Everything past the open comment windows became one list of sixty four
items in no reader-visible order, and a list that long is a thing you scroll past rather than
read. The owner's words: "it's just not very digestible or readable."

AN ITEM IS NOT A DATE, and that is the fact the whole module is shaped around. Half the items
carry two or more key_dates and one carries five: filed in April, heard in June, ordered in
August. So this plots EVENTS, not items, and the same decision legitimately appears in three
months. A flat list can only ever show it once, under whichever date somebody chose, which is
precisely the information a reader loses.

WHAT IT DELIBERATELY DOES NOT DO. It renders nothing. It has no opinion about grids, columns
or phones. It turns a ledger into buckets and labels, so the arithmetic can be tested without
a browser and the layout can change without touching the arithmetic.

THE LABELS ARE PASSED IN, NOT REIMPLEMENTED. `ordinal` is a house rule with a written reason
living in site_build, which imports this module, so importing it back is a cycle. Passing it
follows `schema.Ctx`, which solved the same problem for the same reason: a second copy is how
a heading and a URL drift apart.

    docket_calendar.py --self-test
"""
from __future__ import annotations

import calendar
import datetime as _dt
import json
import sys
from pathlib import Path

# THE ONE PLACE A DATE KIND BECOMES ENGLISH. The ledger's kinds are filing vocabulary and
# `statutory_deadline` shouted at a reader is what a database looks like. Every kind present in
# the shipped ledger must appear here, which the self-test checks against the real file: an
# unlabelled kind would otherwise reach a reader as a slug and nothing would go red.
KIND_LABEL = {
    "filed": "filed",
    "hearing": "hearing",
    "ordered": "ordered",
    "decided": "decided",
    "signed": "signed",
    "effective": "takes effect",
    "comment_opens": "comment opens",
    "comment_closes": "comment closes",
    "statutory_deadline": "statutory deadline",
}

# The kinds that are a DOOR rather than a record of something already done. A reader scanning a
# month wants these to stand out, because they are the ones that can still be acted on.
ACTIONABLE = {"comment_opens", "comment_closes", "hearing", "statutory_deadline"}


def kind_label(kind: str) -> str:
    """English for a ledger kind, and a readable fallback rather than a raw slug."""
    return KIND_LABEL.get(kind, (kind or "").replace("_", " ").strip() or "dated")


def events(items: list) -> list:
    """Every dated event on the record, flattened, each carrying what a cell needs.

    Sorted by date and then by item id, so two events on one day have a stable order and a
    rebuild is byte identical. A date the ledger cannot parse is DROPPED rather than guessed
    at, and the count of what was dropped is returned beside the events so a caller can say so
    instead of quietly showing fewer.
    """
    out, dropped = [], 0
    for it in items:
        for kd in it.get("key_dates") or []:
            raw = (kd or {}).get("date") or ""
            try:
                d = _dt.date.fromisoformat(raw)
            except (ValueError, TypeError):
                dropped += 1
                continue
            out.append({
                "date": d,
                "iso": raw,
                "month": raw[:7],
                "kind": (kd.get("kind") or "").strip(),
                "note": (kd.get("note") or "").strip(),
                "item_id": it.get("id", ""),
                "title": it.get("title", ""),
                "topic": it.get("topic", ""),
                "status": it.get("status", ""),
                "actionable": (kd.get("kind") or "").strip() in ACTIONABLE,
            })
    out.sort(key=lambda x: (x["date"], x["item_id"], x["kind"]))
    return out, dropped


def month_keys(evs: list) -> list:
    """Every month from the first event to the last, INCLUDING the empty ones.

    The gaps are information. This record has nothing at all in October 2026 and nothing across
    2022 to 2024, and a rail that silently closed those up would tell a reader the record is
    continuous when it is not. An empty month renders as an empty month.
    """
    if not evs:
        return []
    first, last = evs[0]["date"], evs[-1]["date"]
    keys, y, m = [], first.year, first.month
    while (y, m) <= (last.year, last.month):
        keys.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return keys


def by_month(evs: list) -> dict:
    out = {}
    for ev in evs:
        out.setdefault(ev["month"], []).append(ev)
    return out


def by_day(evs: list) -> dict:
    out = {}
    for ev in evs:
        out.setdefault(ev["iso"], []).append(ev)
    return out


def weeks(key: str) -> list:
    """The month as calendar rows, Sunday first, with None for days outside the month.

    Sunday first because this is a United States civic record and that is the week a Texan
    reads. `calendar` defaults to Monday, which is a European convention and would silently
    shift every column.
    """
    y, m = int(key[:4]), int(key[5:7])
    cal = calendar.Calendar(firstweekday=6)          # 6 is Sunday
    return [[d if d.month == m else None for d in wk]
            for wk in cal.monthdatescalendar(y, m)]


def month_label(key: str) -> str:
    y, m = int(key[:4]), int(key[5:7])
    return f"{calendar.month_name[m]} {y}"


def month_short(key: str) -> str:
    return calendar.month_abbr[int(key[5:7])]


# HOW FAR BACK THE CALENDAR REACHES. One event from 2021 dragged a whole year of empty grids
# into the year view to show a single marked day, which the owner cut. This is a WINDOW rather
# than a hardcoded year: it is computed from today every build, so the calendar keeps moving
# and no date is ever typed. Anything older is still on the record and still reachable in the
# list view and on its own page; it is just not worth twelve grids.
YEARS_BACK = 2


def horizon(today: str) -> str:
    """The first day the calendar shows, computed from today and never typed."""
    d = _dt.date.fromisoformat(today)
    return f"{d.year - YEARS_BACK}-01-01"


def summarise(items: list, today: str) -> dict:
    """Everything a page needs to render the calendar, computed once.

    `current` is the month a reader lands on. It is today's month when the record has anything
    in it, and otherwise the busiest month, because opening on an empty grid with the record's
    own dates a scroll away is a worse first impression than opening on the crowd.
    """
    evs, dropped = events(items)
    # WINDOWED, and the count of what fell outside is kept so the page can say so rather than
    # quietly showing less than the record holds.
    floor = horizon(today)
    older = sum(1 for ev in evs if ev["iso"] < floor)
    evs = [ev for ev in evs if ev["iso"] >= floor]
    keys = month_keys(evs)
    months = by_month(evs)
    now = today[:7]
    if now in months:
        current = now
    elif months:
        current = max(months, key=lambda k: (len(months[k]), k))
    else:
        current = now
    return {
        "events": evs,
        "dropped": dropped,
        "month_keys": keys,
        "by_month": months,
        "current": current,
        "n_events": len(evs),
        "n_months": len(keys),
        "n_live": sum(1 for k in keys if months.get(k)),
        "busiest": max(months, key=lambda k: (len(months[k]), k)) if months else "",
        "older": older,
        "horizon": floor,
    }


# --------------------------------------------------------------------------- self-test
def _self_test() -> int:
    fails = []

    def ok(label, cond, extra=""):
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + str(extra)}")
        if not cond:
            fails.append(label)

    print("A. an item with several dates lands in several months")
    it = {"id": "x-1", "title": "T", "topic": "t", "status": "pending", "key_dates": [
        {"date": "2026-04-02", "kind": "filed"},
        {"date": "2026-06-11", "kind": "hearing"},
        {"date": "2026-08-20", "kind": "ordered"}]}
    evs, dropped = events([it])
    ok("three dates make three events", len(evs) == 3, len(evs))
    ok("...in three different months", len({e['month'] for e in evs}) == 3)
    ok("...and every one points back at the item", all(e["item_id"] == "x-1" for e in evs))
    ok("nothing was dropped", dropped == 0)

    print("\nB. a date the ledger cannot parse is dropped and counted, never guessed")
    evs, dropped = events([{"id": "x-2", "key_dates": [
        {"date": "2026-13-40", "kind": "filed"}, {"date": "", "kind": "filed"},
        {"date": None, "kind": "filed"}, {"date": "2026-05-05", "kind": "filed"}]}])
    ok("the good one survives", len(evs) == 1)
    ok("...and the three bad ones are counted rather than silently missing", dropped == 3, dropped)

    print("\nC. the empty months are kept, because a gap is information")
    evs, _ = events([{"id": "a", "key_dates": [{"date": "2026-01-05", "kind": "filed"}]},
                     {"id": "b", "key_dates": [{"date": "2026-04-05", "kind": "filed"}]}])
    ks = month_keys(evs)
    ok("the range is spanned end to end", ks == ["2026-01", "2026-02", "2026-03", "2026-04"], ks)
    ok("...and the two months with nothing in them are present", len(ks) - len(by_month(evs)) == 2)
    ok("a year boundary is crossed correctly",
       month_keys([{"date": _dt.date(2025, 11, 1), "month": "2025-11"},
                   {"date": _dt.date(2026, 2, 1), "month": "2026-02"}])
       == ["2025-11", "2025-12", "2026-01", "2026-02"])
    ok("no events means no months rather than a crash", month_keys([]) == [])

    print("\nD. the grid is a real month, and the week starts on Sunday")
    wk = weeks("2026-08")
    ok("every row is seven days", all(len(w) == 7 for w in wk), [len(w) for w in wk])
    days = [d for w in wk for d in w if d]
    ok("August has its thirty one days, once each", len(days) == 31 and len(set(days)) == 31)
    ok("...and they are consecutive", days == sorted(days))
    ok("the first column is a Sunday", all(w[0].weekday() == 6 for w in wk if w[0]),
       "a Monday-first grid would shift every column")
    feb = [d for w in weeks("2024-02") for d in w if d]
    ok("a leap February is twenty nine days", len(feb) == 29, len(feb))
    ok("...and a common one is twenty eight", len([d for w in weeks("2026-02") for d in w if d]) == 28)

    print("\nE. labels are English, and every kind in the shipped ledger has one")
    ok("a slug becomes a phrase", kind_label("comment_closes") == "comment closes")
    ok("an unknown kind is readable rather than raw", kind_label("some_new_kind") == "some new kind")
    ok("an empty kind still says something", kind_label("") == "dated")
    ok("the month reads as a month", month_label("2026-08") == "August 2026")
    led = Path(__file__).resolve().parents[2] / "ledger" / "docket.json"
    if led.is_file():
        real = json.loads(led.read_text(encoding="utf-8"))["items"]
        kinds = {(kd.get("kind") or "").strip()
                 for it in real for kd in (it.get("key_dates") or [])}
        missing = sorted(k for k in kinds if k and k not in KIND_LABEL)
        ok("every kind on the real record has an explicit label", not missing, missing)

        print("\nF. against the record as it actually stands")
        s = summarise(real, "2026-08-20")
        ok("every dated event inside the window is present, and the rest are counted",
           s["n_events"] + s["dropped"] + s["older"]
           == sum(len(it.get("key_dates") or []) for it in real),
           f"{s['n_events']}+{s['dropped']}+{s['older']}")
        ok("the rail covers the whole span with no month missing",
           s["n_months"] == len(s["month_keys"]) and s["n_months"] > s["n_live"])
        ok("it opens on today's month when the record has one", s["current"] == "2026-08")
        # A WINDOW THAT HAS MOVED PAST THE WHOLE RECORD IS AN EMPTY CALENDAR, and an empty one
        # has to be a page that renders rather than a crash. The renderer returns nothing at
        # all for this, which is the honest output: there is no month to draw.
        far = summarise(real, "2031-01-01")
        ok("a window past the end of the record is empty rather than broken",
           far["n_events"] == 0 and far["month_keys"] == [] and far["older"] > 0,
           f"n={far['n_events']} older={far['older']}")
        ok("...and it still reports today's month, so a caller has something to say",
           far["current"] == "2031-01", far["current"])
        # And inside the window, a today with no events of its own opens on the busiest month.
        mid = summarise(real, "2026-10-01")
        ok("a quiet month opens on the busiest one instead of on nothing",
           mid["current"] == mid["busiest"] and mid["current"] != "2026-10", mid["current"])
        ok("every event carries a link target", all(e["item_id"] for e in s["events"]))
        ok("the calendar reaches back two whole years and no further",
           s["horizon"] == "2024-01-01", s["horizon"])
        ok("...so the lone 2021 date is outside it, and counted rather than dropped silently",
           s["older"] >= 1 and all(k >= "2024" for k in s["month_keys"]),
           f"older={s['older']} first={s['month_keys'][0]}")
        ok("...and the window MOVES, because it is computed from today and never typed",
           summarise(real, "2030-06-01")["horizon"] == "2028-01-01")
        ok("the actionable kinds are a subset of the labelled ones",
           ACTIONABLE <= set(KIND_LABEL))

        # ------------------------------------------------------------------------------
        # G. NOTHING HERE IS FROZEN.
        #
        # The site publishes with no human in the loop, so the failure that matters is not a
        # wrong number, it is a number that WAS right. A year typed into a template, a count
        # copied out of one build, a window pinned to the season somebody wrote it in: each of
        # those is green on the day it ships and quietly false a month later, and nothing goes
        # red. So this walks a ladder of dates and asserts that everything the page publishes
        # actually MOVES, which is the property a frozen value cannot fake.
        print("\nG. nothing on the page is frozen: every figure moves when the date does")
        ladder = ["2026-08-20", "2027-01-05", "2028-06-01", "2029-06-01", "2030-06-01"]
        walk = [summarise(real, d) for d in ladder]
        ok("the window is always two whole years back from today, at every date",
           all(w["horizon"] == f"{int(d[:4]) - YEARS_BACK}-01-01"
               for d, w in zip(ladder, walk)),
           [w["horizon"] for w in walk])
        ok("...so it only ever moves forward as the dates do",
           all(a["horizon"] < b["horizon"] or a["horizon"] == b["horizon"]
               for a, b in zip(walk, walk[1:])) and walk[0]["horizon"] < walk[-1]["horizon"],
           [w["horizon"] for w in walk])
        ok("what the calendar shows shrinks as the window slides past the record",
           all(a["n_events"] >= b["n_events"] for a, b in zip(walk, walk[1:]))
           and walk[-1]["n_events"] < walk[0]["n_events"],
           [w["n_events"] for w in walk])
        # NOTHING IS LOST WHEN THE WINDOW MOVES, it is only moved into the sentence that says
        # how much is older. A count that stopped adding up would mean the page had started
        # publishing less than the record holds without saying so.
        total = sum(len(it.get("key_dates") or []) for it in real)
        ok("...and every date is still accounted for at every one of those dates",
           all(w["n_events"] + w["older"] + w["dropped"] == total for w in walk),
           [(w["n_events"], w["older"], w["dropped"]) for w in walk])
        # The landing month is the other thing a reader would never catch going stale, because
        # a calendar opening on a plausible wrong month looks exactly like one opening right.
        ok("the month it opens on follows today, whenever the record holds today's month",
           all(summarise(real, k + "-15")["current"] == k
               for k in ("2026-06", "2026-08", "2026-11", "2027-02")))

    print(f"\ndocket_calendar self-test: {'all passed' if not fails else str(len(fails)) + ' FAILED'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(_self_test() if "--self-test" in sys.argv else _self_test())
