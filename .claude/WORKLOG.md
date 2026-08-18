# WORKLOG — the item page overhaul, from quote wall to tracked decision

Opened 2026-08-18 on the owner's call. **Read this first and resume from the wave table.**

## The complaint, and it is correct

> "we need an overhaul of what you are actually tracking. I looked at the Texas page and it looks
> like for some reason all ur doing is quote collecting. When the Alaska page is actually keeping
> a timeline of each decision."

Measured against the two pages the owner linked. The reference item page carries a section headed
**How this decision moved**, "one dated line per material change, oldest first", and on the LNG
tax item it runs to roughly 27 dated entries from July 8th to August 15th. Many of those lines
say nothing changed, in as many words. "Checked and unchanged." "Re-verified. Nothing has moved."
"Carried forward against reporting from July 16 and July 21."

That is the whole difference. A reader of that page sees a decision being watched. A reader of
ours sees a stack of quotes with one date on it.

## Root cause, and there are two, both ours

**1. The routine throws the fact away.** `prompts/daily_routine.md` Phase 3 says, in bold:

> Add a history note **only when something changed**.

So every "checked and unchanged" observation is discarded at the moment it is made. This directly
contradicts the rule three lines above it, which is right and which the run already follows for
the stamp:

> Set `last_verified` **even when nothing changed.** "Checked and unchanged" is a fact about the
> item, and an unset stamp is indistinguishable from never having looked.

The stamp keeps that fact. The history does not. **57 of 61 items carry no movement log at all.**

**2. Nothing renders it even when it exists.** `scripts/site/site_build.py` mentions `history`
exactly once, in a comment, on a line about something else. The four items that DO carry an entry
show a reader nothing. The field is also absent from `gate_schema`, so it is unvalidated as well
as unrendered.

A field that is written, never validated and never displayed is not a feature, it is a habit.

## What we may NOT do, and it needs saying before anyone starts

**We cannot backfill.** Writing "2026-08-14, checked and unchanged" for a check nobody recorded
would be inventing an observation, on the one surface whose entire promise is that it does not.
The log starts from the first run that writes it and grows forward. The only honest seed is a
single dated `Tracked.` line per item, built from dates the record ALREADY holds, and even that
is a wave 3 decision rather than an assumption.

## Waves

| # | what | owner lane | status |
|---|---|---|---|
| 1 | Flip the rule so every re-verification writes a dated line, unchanged included | `human` (`prompts/`) | DONE |
| 2 | Render `How this decision moved` on the item page, oldest first | `human` (`scripts/site/`) | DONE |
| 3 | Validate history in `gate_schema` so it can never drift or narrate | `human` (`scripts/site/`) | DONE |
| 4 | Write today's lines for every item re-verified this run | `daily` (`ledger/`) | DONE |
| 5 | The dated timeline strip, key dates with TODAY marked and the next date called | `human` | TODO |
| 6 | Per item questions block, generated from the record | `human` | TODO |
| 7 | Cite this block, and beat cross links | `human` | TODO |
| 8 | Decide whether `key_dates[].note` joins the copy gates, with the evidence below | `human` | TODO |

## What waves 1 to 4 actually turned up, and three of them were nothing to do with history

**Wave 4 was marked DONE before it was.** Twelve items carried `last_verified: 2026-08-18` and
one of them carried a movement line. That is the exact defect this whole overhaul exists to fix,
sitting in the ledger while the wave table said the wave was finished. Eleven lines were written
from what the run had already recorded, in the run record and in commit `7d5fccc`'s own message,
so nothing was invented. **The lesson is that a wave table is a claim like any other and the
thing to check is the artifact, not the row.**

**The numeral gate needed the same carve-out twice.** `docket_build` excludes history notes from
its numeral gate for a structural reason, a movement line's whole job being to cite a value that
is by definition no longer in any current claim. The site layer has its own numeral set and had
no such exclusion, so the record validated clean and the site it produced failed the build. A
carve-out made at one layer and not the other is not a carve-out, it is a discrepancy waiting for
a run to hit it. Both are now written down where they are made.

**Item pages were never spaced, they were spaced by accident.** `main > section` sets the band on
every section on the site and has never matched an item page, because item pages wrap their
sections in `<article>` and that selector does not reach inside. Computed top margin on all 61
pages was zero. What separated the sections was the previous section's last paragraph, borrowed.
The moment a section ended in a table the next heading landed against it, which "The evidence"
has been doing under the Dates table on every page that has one, unnoticed, until the movement
log went between them and made it impossible to keep missing. `article > section` now carries its
own margin. **This is the third entry in this repo of a rule styling by document shape and
silently missing the pages nobody screenshotted**, and the comment above it in `theme.py` had
already written the lesson down for the previous two.

**The Markdown twin carries the log too.** Leaving it out would have rebuilt, one layer down, the
exact gap the section was opened to close, and the twin is what a machine reader gets.

## Wave 8, found while wiring wave 3, and deliberately not acted on

`key_dates[].note` renders in the Dates table on every item page and is outside every copy gate,
which is the same hole history notes were in. Folding it into `_reader_text` was tried and
reverted in the same session, because it does two different things at once and only one of them
is obviously right.

**Right:** a key date note must not narrate the machine, and must keep the punctuation rules.

**Not obviously right:** the comma rule is a MEASURED ceiling, calibrated on running prose. A key
date note is a label fragment. Folding fragments into the density measure moves a number that was
measured on something else, which is the exact error CLAUDE.md warns about when it says the
ceiling is measured on running prose and not on whole-page text.

It found three real defects in copy readers already see, and they are worth fixing whatever is
decided about the gate:

- `tx-2026-0031` "August 12th and 13th, 2026". The numeral gate reads the `13` as an untraceable
  figure. It is an ordinal date, so this is likely the extractor rather than the copy.
- `tx-2026-0041` "NewsChannel 6". The `6` is part of a broadcaster's name. Same shape of false
  positive, and a warning that widening a numeral gate over proper nouns needs care.
- `tx-2026-0034` comma rate 4.62 against the 3.97 ceiling, but only once fragments are counted.
  This is the measurement question above rather than a defect in the sentence.

Waves 5 to 7 are the rest of "more robust" and are worth doing in that order. Wave 5 is the one a
reader feels next, because it answers "when does this move" without reading a table.

## The house rule that constrains the prose

The reference log writes lines like "Alaska Beacon returned HTTP 403 on re-fetch this run". **We
may not.** `gate_narration` refuses machine narration in reader copy and it is right to. A Texas
movement line is about the DECISION and is dated. If a source could not be reached, the honest
line names what is therefore unconfirmed, not what the fetcher did.

Good: "Checked and unchanged. The August 21st open meeting is still on the calendar."
Bad: "Re-fetched this run, source 403'd, carried forward."
