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
| 5 | The dated timeline strip, key dates with TODAY marked and the next date called | `human` | DONE |
| 6 | Per item questions block, generated from the record | `human` | DONE |
| 7 | Cite this block, and beat cross links | `human` | DONE |
| 8 | Decide whether `key_dates[].note` joins the copy gates, with the evidence below | `human` | TODO |
| 9 | Rank `/sources/` by weight, lead with the primary share, one page per publisher | `human` | DONE |
| 10 | Put `/sources/` in the daily routine's eyes-on list, beside the grid page | `human` (`prompts/`) | DONE |

## Waves 9 and 10, the source archive, opened on the owner's call 2026-08-18

> "the other thing we forgot to add into the site and also incorporate into our daily upkeep
> https://alaskaaihq.com/sources/"

**We have the page.** `/sources/` exists, groups every fetched document by host, and gives each
one a citation count. What it does not do is the thing that makes the reference version worth
reading.

**Sorted alphabetically, which ranks nothing.** The reference page sorts by how much of the
record rests on each source, so the first screen answers "who is this record leaning on". Ours
opens on whichever host starts with the earliest letter, and a reader has to read all of it to
learn the same thing. The data for the better sort is already computed on the page.

**The one figure that tests the promise is missing.** The reference page leads with the share of
claims that rest on a primary document rather than on a report about one. That is the single
number that says whether "every fact traces to a fetched source" is a standard or a slogan, and
it is the number this project should most want to publish about itself, in both directions. Ours
prints documents and publishers, which are facts about the archive's size rather than its
quality. `source_type` is already stored on every claim, so this is arithmetic on data we hold
and no new fetching.

**Per source, the counts are thinner than they need to be.** The reference gives primary count,
claim count and article count per source. Ours gives one entry count. All three are derivable.

Wave 10 is the upkeep half of the ask. The routine already looks at the grid page every run and
may fix presentation only. `/sources/` deserves the same standing look, and the run record for
2026-08-18 is evidence for it: `/sources/` was signed off as fine that day on a glance at how
titles render, and `/questions/` was recorded honestly as NOT LOOKED AT. A page nobody is told
to open is a page that gets signed off from memory.

**Nothing about either wave lets a run edit the archive.** The page is generated from
`ledger/docket.json` like every other, so the routine's standing look is a presentation check in
`scripts/site/`, exactly as the grid page's is, and the same sentence in `ownership.yaml`
governs it.

### What was built, and the discovery argument for it

> "the sources tab will be a robust thing and will need to be upkeep daily by the automation so
> you'll need to wire then it and how, properly, its huge for indexing so u wanna do it in the
> way that helps us get discovered"

**One page per publisher, 51 of them.** The archive already held everything a page about a
publisher needs. It was not addressable, and a search engine indexes a URL. Forty publishers on
one URL is one thing to rank, competing with itself for every query, and a reader arriving from
a search for one of them landed at the top of a list of the other fifty. The site went from 170
pages to 221.

**Why this is not a doorway farm, which is the fair objection.** A doorway page exists for a
crawler and carries nothing for a reader. Every sentence and every figure on these is computed
from the ledger, each page carries the actual documents and the actual entries that rest on
them, and a reader who followed a citation back to a publisher gets what they came for. They are
also the missing half of the item page's evidence block, which listed a source and dead ended.

**The link goes three ways, which is the part a sitemap cannot do.** The hub ranks and links
down, each publisher page links back to every entry that cites it, and every entry's evidence
block now links out to the publisher. A crawler that finds any one finds the other two.

**Everything downstream came for free, by design rather than by luck.** The sitemap takes any
`index.html`, so all 51 are in it. `pages.yml` submits the day's changed URLs to IndexNow off
the sitemap's own `lastmod`. Each page carries a `CollectionPage` node naming its members and a
breadcrumb. `llms.txt` names every publisher with its URL, ranked, so a model asked what this
record rests on answers from one fetch. None of that needed a new mechanism, which is the
argument for the page family having been the right shape.

**The address is built from the host and never from the title.** A source title is the
document's words and changes when a publisher retitles a page. A URL that moves loses whatever
rank it had. `interchange-puc-texas-gov` is ugly and permanent, and permanent is the half that
matters for an address.

**The share is the point of the hub.** It publishes how many claims rest on a primary document
rather than on a report about one. The page used to open with documents and publishers, which
are facts about the archive's size, while the claim the record makes is about its quality. The
routine is now told to read that share every run and to treat a fall as a finding about the
record rather than a defect on the page, because the only way to move it is to go and find the
filing.

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
