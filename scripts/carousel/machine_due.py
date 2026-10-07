#!/usr/bin/env python3
"""machine_due.py — is the weekly machine pass due today? Exit 0 = yes, run it. Exit 1 = no.

WHY THIS EXISTS (owner, 2026-10-02)

Until this day every run ended in a retro phase that spawned the upgrade engineer and made zero to
three changes to the machine from what THAT ONE RUN saw. The owner's words: the daily automation
should "only fix like the things that were broken during the run", and once a week a run should
spend time "addressing the things that really need to be fixed based on the recurring themes that
it saw during the week. So that it can be constantly making upgrades each week based on actual
output." One run is one sample. A defect the judges name on four decks in a week is a defect in
the machine, and one they name once may be that deck's.

So a run now fixes what broke in it and QUEUES the rest in `knowledge/carousel/MACHINE_QUEUE.md`,
and the weekly pass reads the whole week (`week_digest.py`) and works the themes that recurred.

THE PASS IS DUE WHEN
  no pass has ever run, or
  the last one was DAYS or more days ago, or
  an open queue item has bitten two or more runs beyond the one that found it, and the last pass
  was not today, because a repeat offender waiting a week is a week of decks paying for it.

A REPEAT OFFENDER THE LAST PASS ALREADY ESCALATED DOES NOT MAKE IT DUE AGAIN (2026-10-06). The
pass of October 6th was due early on `prompt-audit-reads-auto-mode-as-human` at repeat 2, a fix in
`scripts/shared/prompt_audit.py`, which is `daily` lane and not the pass's to make, so the pass
escalated it and left it open. Read the old way, that open repeat 2 item made the pass due again
on the 7th, the 8th and every day after until somebody else acted, each time to escalate the same
line again. So an item whose newest ` | escalated <date>` is the last pass's own date, and whose
evidence names no ` also <date>` after it, is waiting on its owner and does not count. The next run
it bites appends ` also <date>`, as the queue's own header says to, and from that day it counts
again. The seven day schedule is untouched.

It is due on schedule even with an empty queue, unlike the sibling's video routine, because the
themes come from the week's own score cards and not only from what a run remembered to queue.

  python3 scripts/carousel/machine_due.py --date 2026-10-09
  python3 scripts/carousel/machine_due.py --self-test
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE = REPO_ROOT / "config" / "carousel" / "machine_pass.json"
QUEUE = REPO_ROOT / "knowledge" / "carousel" / "MACHINE_QUEUE.md"
DAYS = 7
ITEM = re.compile(r"^- \[ \] (.*)$")
REPEAT = re.compile(r"repeat:\s*(\d+)", re.I)
ESCALATED = re.compile(r"\|\s*escalated (\d{4}-\d\d-\d\d)")
BITTEN = re.compile(r"\balso (\d{4}-\d\d-\d\d)")


def open_items(text: str) -> list[dict]:
    """Open items, column 0 only, so the indented format example never counts."""
    items = []
    for line in text.splitlines():
        m = ITEM.match(line)
        if m:
            r = REPEAT.search(m.group(1))
            items.append({"text": m.group(1), "repeat": int(r.group(1)) if r else 0})
    return items


def parked(item: dict, last_pass: dt.date) -> bool:
    """The last pass escalated this item and no run has met it since (see the docstring)."""
    def dates(rx):
        out = []
        for d in rx.findall(item["text"]):
            try:
                out.append(dt.date.fromisoformat(d))
            except ValueError:
                pass
        return out
    escalated, bitten = dates(ESCALATED), dates(BITTEN)
    if not escalated or max(escalated) != last_pass:
        return False
    return not any(b > last_pass for b in bitten)


def verdict(state: dict, queue_text: str, today: dt.date) -> tuple[bool, str]:
    items = open_items(queue_text)
    last = state.get("last_pass")
    if not last:
        return True, f"no weekly pass has run yet ({len(items)} item(s) queued)"
    try:
        last_d = dt.date.fromisoformat(str(last))
    except ValueError:
        return True, f"the last pass date {last!r} does not parse, so treat the pass as never run"
    age = (today - last_d).days
    if age >= DAYS:
        return True, f"last pass {last}, {age} days ago, {len(items)} item(s) queued"
    repeats = [i for i in items if i["repeat"] >= 2 and not parked(i, last_d)]
    if repeats and age >= 1:
        return True, f"{len(repeats)} repeat offender(s) queued, last pass {last}"
    return False, (f"last pass {last}, {age} day(s) ago, due at {DAYS}; {len(items)} item(s) "
                   f"queued, {len(repeats)} repeat offender(s)")


def self_test() -> int:
    bad = 0

    def ok(label, cond, extra=""):
        nonlocal bad
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        bad += 0 if cond else 1

    d = dt.date(2026, 10, 10)
    q0 = ("    - [ ] <date found> | repeat: <n> | the format example\n"
          "## Open\n(none)\n## Done\n- [x] 2026-10-01 | repeat: 3 | old\n")
    q1 = "## Open\n- [ ] 2026-10-03 | repeat: 0 | a | evidence: x | fix: y\n"
    q2 = "## Open\n- [ ] 2026-10-03 | repeat: 2 | a | evidence: x | fix: y\n"
    ok("the format example and done items are not open items", open_items(q0) == [])
    ok("no pass ever run is due, even with nothing queued", verdict({}, q0, d)[0])
    ok("a pass seven days ago is due with nothing queued", verdict({"last_pass": "2026-10-03"}, q0, d)[0])
    ok("a pass three days ago with one ordinary item is not due",
       not verdict({"last_pass": "2026-10-07"}, q1, d)[0])
    ok("a repeat offender makes it due early", verdict({"last_pass": "2026-10-07"}, q2, d)[0])
    ok("...but never twice on one day", not verdict({"last_pass": "2026-10-10"}, q2, d)[0])
    # ESCALATED BY THE LAST PASS (2026-10-06), replayed on the real line that made that pass due
    real = ("## Open\n- [ ] 2026-10-04 | repeat: 2 | prompt-audit-reads-auto-mode-as-human | evidence: "
            "no. 42 interim prompt_audit exit 1 ; also 2026-10-05 (no. 43) ; also 2026-10-06 (no. 44) "
            "| fix: scripts/shared/prompt_audit.py separates a classifier band\n")
    ok("the real repeat 2 line made the 2026-10-06 pass due",
       verdict({"last_pass": "2026-10-05"}, real, dt.date(2026, 10, 6))[0])
    marked = real.replace("band\n", "band | escalated 2026-10-06: daily lane, patch handed to the run\n")
    ok("...and once that pass escalated it, it does not make the 7th due",
       not verdict({"last_pass": "2026-10-06"}, marked, dt.date(2026, 10, 7))[0])
    bit = marked.replace("(no. 44) ", "(no. 44) ; also 2026-10-07 (no. 45) ")
    ok("...until a run meets it again and appends its date, which makes the 8th due",
       verdict({"last_pass": "2026-10-06"}, bit, dt.date(2026, 10, 8))[0])
    later = real.replace("band\n", "band | escalated 2026-10-08: a run's Phase 17\n")
    ok("an escalation dated after the last pass (a run's, not the pass's) still makes it due",
       verdict({"last_pass": "2026-10-06"}, later, dt.date(2026, 10, 9))[0])
    ok("...and the seven day schedule fires over a parked item",
       verdict({"last_pass": "2026-10-06"}, marked, dt.date(2026, 10, 13))[0])
    ok("a date that does not parse is treated as never run", verdict({"last_pass": "soon"}, q1, d)[0])
    ok("the live queue and state parse", isinstance(open_items(QUEUE.read_text(encoding="utf-8")
                                                               if QUEUE.exists() else ""), list))
    print("\nmachine_due self-test: " + ("all passed" if not bad else f"{bad} FAILED"))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    due, why = verdict(state, QUEUE.read_text(encoding="utf-8") if QUEUE.exists() else "",
                       dt.date.fromisoformat(a.date))
    print(f"weekly machine pass {'DUE' if due else 'not due'}: {why}")
    return 0 if due else 1


if __name__ == "__main__":
    sys.exit(main())
