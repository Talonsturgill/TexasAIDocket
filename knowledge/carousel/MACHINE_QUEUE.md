# Machine queue: what the weekly machine pass works on

Since 2026-10-03 a run fixes only what broke in its own run and queues every other machine change
here, in Phase 17, under the `upgrade` stamp. Once a week the machine pass (Phase 17, brief in
`prompts/machine_weekly.md`) reads the week's own artifacts through
`scripts/carousel/week_digest.py`, works the themes that recurred and this list, and marks what it
shipped. `scripts/carousel/machine_due.py` reads this file to decide whether a pass is due early.

The owner's words, 2026-10-02: the daily automation should "only fix like the things that were
broken during the run", and once a week spend time "addressing the things that really need to be
fixed based on the recurring themes that it saw during the week ... based on actual output".

One line per item, in this exact shape, so the due check can read it:

    - [ ] <date found> | repeat: <runs it has bitten beyond the first> | <signature> | evidence: <what showed it, with frames and rounds> | fix: <the proposed change>

**A defect already open is never added twice.** The run that meets it again raises its `repeat`
count in place and appends its date to the evidence. An item at `repeat: 2` makes the pass due the
next day rather than waiting out the week.

A pass that ships an item changes `[ ]` to `[x]` and appends ` | shipped <date> <commit>`. An item
it can't fix safely stays open with ` | escalated <date>: <why>`. An item that needs a `human`
file, the engine (`assets/js/txthree.js`) or the kit registry (`assets/js/txkit.js`), is written
up in `UPGRADE_BACKLOG.md` and named at the top of the email.

## Open

(none yet)

## Done

(none yet)
