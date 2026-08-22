# Run record, August 22nd, 2026

## THE FINDING A HUMAN HAS TO SEE

**The record cannot admit a new item until a maintainer changes one file, and no automation in
this repo is allowed to change it.**

Seven items passed every gate and the admission bar this run and were held anyway. Admitting them
turns `site_build.py` red, and the reason is worth reading in full because it is the third time a
gate here has been passing for the wrong reason.

The construction page prints a TDLR project name, `Project Gold Phase 2 - DFW44`. `numeral_lint`
tokenises reader copy and asks of `44` whether the build computed it. The construction page's own
authorised set never adds the digits inside a project or campus name, so that page has only ever
passed because the SITE-WIDE set happened to carry `44` from somewhere else.

Somewhere else was the docket. **`44` was the number of items in `ledger/docket.json` whose
`public_access.room` is `open_meeting`.** Admitting seven items moves that count from 44 to 47, the
site-wide set loses `44` along with `42`, `58`, `69` and `314`, and a page that has nothing to do
with the docket fails on a filer's project name.

This is exactly what `_item_numerals` warns about in its own comment, one order of magnitude up: a
name's digits waved through because a small number is almost always in the site-wide set from some
unrelated computation. Today was the day it stopped being true.

**MEASURED, not argued.** The paragraph above was reasoning when it was first written, and reasoning
about a gate is how a wrong finding gets recorded as a true one. So the run ran it. A merged ledger
of the 69 published items plus the 7 admissible ones was written to `out/2026-08-22/tmp/`,
`ledger/docket.json` was swapped for it under a shell trap that restores the original whatever
happens, and `site_build.py` was built into a scratch directory:

```
  numeral: construction/index.html: 44
  numeral: construction/index.html: 44
site_build: 2 page(s) print a numeral this build did not compute.
site_build EXIT=1
LEDGER RESTORED
```

The same build at 69 items exits 0. `open_meeting` counts 44 at 69 items and 47 at 76, both counted
in code. The finding is a measurement, and the scratch ledger and the trial site were deleted.

**A second reason the seven were held, and it was this run's own defect.** The promote gate refused
all seven for `last_verified is <date> and the movement log carries no line for that date`. The
first draft of this record claimed they passed every gate, and they did not. Seven movement lines
were written into `seed/docket_seed.json`, each naming what the fetched source showed, and the gate
now admits all seven. That is what made the measurement above possible at all, and it is why the
claim in this section is now true rather than nearly true.

**Proposal, out of lane.** In `site_build.py`, where `_tnums` is assembled for
`construction/index.html`, authorise the numerals found inside project and campus names the way the
item layer already does through `dk._name_numerals`. A filer's project name is an identifier taken
from the filing system, in the same class as a statute number, and it should be authorised as one
rather than borrowing a docket count. Add the self-test case that proves the gate can still go red
on a genuinely uncomputed figure.

`ownership.yaml` gives `scripts/site/site_build.py` to `human` and to no automation. `daily` was
refused, and so was `upgrade`. So this run records it and stops, per `CLAUDE.md`.

The seven items sit in `seed/docket_seed.json` with every gate passing. A later run promotes them
automatically the moment the fix lands. They are tx-2026-0074, tx-2026-0084, tx-2026-0085,
tx-2026-0086, tx-2026-0087, tx-2026-0088 and tx-2026-0089.

## The record

**Worklist.** The selector named 46 of 69 items due. Nothing rotten, nothing deferred, and no
`--budget` was passed. All 46 were re-verified against a fetched primary source and all 46 carry a
dated movement line, including the ones where nothing moved. Every fetch returned HTTP 200.

**Two items stopped being unconfirmed.** tx-2026-0008 and tx-2026-0025 both rest on Government Code
Chapter 2054, and two previous runs recorded them as unconfirmed because the chapter text those runs
could read stopped at Section 2054.0702. This run's fetch of the same URL returned the whole
chapter, 283,798 characters. The three Subchapter S enactments are now confirmed on the face of the
code. One runs Sections 2054.651 to 2054.654 on website modernization. Two more both begin at
Section 2054.701, one creating an artificial intelligence division and one setting artificial
intelligence duties, and the codifier flags the conflict rather than resolving it. Section 2054.711
is confirmed as well, including the subsection letting an academic medical center or public hospital
satisfy the notice duty with a generalized statement in a patient consent form.

**Backlog.** Held at three, the same three that predate the rule. tx-2026-0001, tx-2026-0002 and
tx-2026-0007 still name no county. A statewide flag was considered and refused: these are PUCT rules
for the ERCOT region, and the ERCOT region is not the state, which two El Paso items in this same
record already turn on. Publishing a scope nobody checked is worse than leaving the entry.

**Admitted.** None, for the reason at the top of this record.

## Discoverability signoff

- **One decision's card, opened as an image.** `og/tx-2026-0082.png`, the record's newest item.
  Wraps as "UTMB moved its Epic / health record into / Microsoft's cloud and / named advanced...".
  Legible, breaks fall where a reader would break them, and it ends on a whole word plus an
  ellipsis rather than a stump. One observation: the cut lands after the adjective "advanced" and
  the phrase is "advanced technologies", so the truncation ends on a dangling modifier. Not a fault
  in the wrapper, which cuts on width, but the least graceful of the cuts looked at.
- **`/questions/`, read as a reader.** The questions are ones somebody would type. One finding
  worth acting on. "How the public can take part" answers for **5** of 69 entries, and 5 is exactly
  the number of items whose room is `open_comment`. The record holds **44** items whose room is
  `open_meeting`, and an open meeting is precisely a way for the public to take part. The shape
  appears to answer only for `open_comment`, so the most common room on the record produces no
  answer to the question it most obviously answers. Also noted: the count renders zero padded as
  `05` beside unpadded `69` and `64`.
- **The `Open right now` section of `llms.txt`.** Lists tx-2026-0015, 0016, 0048, 0002, 0024, 0075
  and 0077. Cross checked against every window this run re-verified. Every close date is on or after
  today and none closed today, so nothing stale is listed and the merge order is right.
  tx-2026-0077 closes August 25th, three days out, and is correctly still listed. One observation:
  tx-2026-0024 is listed with `closes` unset, so a section that promises "a dated way in" carries
  one entry a reader can't date.
- **`/sources/`.** The share reads **242 of 314 claims rest on a primary document, across 124
  documents from 58 publishers.** It did not move this run, which is the right outcome given nothing
  was admitted. The top publisher is `webapi.legistar.com` at 29 claims, 26 of them primary, and its
  document list reads as documents: city and county legislative records, which is a proper primary
  source rather than a report about one. The quoted material exemption is still doing its job and is
  not hiding any of our own sentences.
- **`/topic/`.** The hub's eight cards read 21, 1, 4, 14, 8, 5, 10 and 6, and every one equals the
  number of decisions listed on that beat's own page. They sum to 69, which is the figure the front
  page counter prints. Checked, agrees.
- **`/place/`.** Nothing landed anywhere this run, so no place page changed and none was expected to.
  Checked rather than assumed.

**The water map's pins.** The latest water record carries 119 reservoirs. The map's largest SVG
draws 253 circles, but they are `tank` and `rim` pairs plus a `wf` class, so the circle count is not
the pin count and this check could not be completed the way the routine describes it. Recorded as
NOT SETTLED rather than as fine.

**Instrument once over.** All green by exit code. `gridwatch_pagecheck` 0, `waterwatch_pagecheck` 0,
`waterwatch_page --self-test` 0, `media_check` 0, `schema_check` 0, `og --self-test` 0,
`favicon --self-test` 0, `truetype --self-test` 0, `indexnow --self-test` 0, `seo_check` 0. No
instrument has stopped and no page is reading wrong.

**The scanner's daily ceiling.** NOT CHECKED. The Supabase connector is not available in this
session, so the `scanner.scans` query could not be run. Recorded rather than skipped silently.

## The deck, and why it did not ship

**The panel held it at 6.56 against a floor of 7.0, on the sixth reading. The record shipped and
the deck did not.** That is the degradation ladder working rather than failing: the run's first
deliverable is on `main`, and the second is on this branch with its evidence.

Six panels, and the honest reading of them is that the deck sits at about 7.0 and the judges'
variance is wider than the gap:

| panel | integrity | craft | reader | median |
|---|---|---|---|---|
| 1 | 6.14 | 6.73 | 6.94 | 6.77, hard fail |
| 3 | 7.03 | 7.42 | 7.41 | 7.40 |
| 4 | 6.49 | 7.05 | 7.04 | 6.98 |
| 5 | 6.75 | 6.98 | 7.08 | 6.87 |
| 6 | 6.49 | 6.96 | 6.75 | 6.56, hard fail |

**Panel 1's hard fail, and the defect class it opened.** Slide 7's hook read "The deadline sits in
the index twice." That is a count over a 34 row index the deck quotes 10 rows of, and no claim or
computation carried it. It escaped `aggregate_check` because "twice" is not in that gate's number
words. The repair was applied as a rule and not a patch, and the rule found two more instances: slide
4's "Two filed on the same day" had the same unscoped shape, and slide 1's cover lit ten of its
thirty four recesses in a 4-3-2-1 staircase, a shape chosen because it looked like something. The
cover now lights the index positions the deck actually quotes, items 10 and 25 through 34 with 27
correctly dark, derived from `aggregates.json`.

**A quoted row that was not the quote.** Slides 6 and 7 print index rows inside straight quotation
marks, which promises the characters between them are the source's. Six rows carried `&nbsp;` after
a plain space to open a column gap, rendering two character cells where the claim has one. No gate
could see it: `render.py` collapses whitespace runs when it captures `textContent`, and
`copy_sync_check` compares skeletons with every non-alphanumeric stripped. It took measuring line
box widths against the 14.4px mono advance. The fragments that measured 27, 20 and 30 cells now
measure 25, 19 and 29, and a judge re-measured and confirmed all seven rows character-for-character.

**Panel 6's hard fail was in the record, not the deck, and it was this run's own.** See the section
below.

**What the panel wanted and this run did not do.** Every lens, repeatedly, asked for one plain
sentence saying what the rule would actually do to a Texan, and for slide 6 to stop being a list
after a list. The first was refused as an inference, and a judge pushed back with a better answer
this run should have taken: the statute quote already sitting in `tx-2026-0002-c10` carries "to be
deployed in the event of an anticipated emergency condition", so a traceable plain reading was
available and quoting it is not inferring. That is the next run's first move and it is written into
the proposals below. The second needs a frame redesigned, not patched.

## THE SECOND FINDING A HUMAN HAS TO SEE

**The published record asserted four things this run's own fact-checker had rejected by name, and
the first correction missed the field that mattered most.**

A scoring judge read `tx-2026-0002`, the docket item this deck's first comment sends readers to, and
found the summary calling the rule "the category that covers data centers" and saying "Individual
Texans as well as utilities and data center operators have already filed". Both are on this run's
rejected list. The first is refuted by `c20`, which searched the published rule text and found the
words at zero occurrences. Three claim texts also said more than their quotes carried, and
`tx-2026-0002-c8` quoted "33 filing(s)." while stamped `last_verified` today, on a page this run
fetched at 34.

**Then the correction itself was wrong, and two judges caught it.** The summary was fixed and
`public_access.how` was not, which is the field the site publishes as "How to take part" and the one
paragraph telling a Texan how to act. It still read "Individuals have already done so without
counsel", published three times on the item page including inside the JSON-LD. And the dated history
line written with that first correction claimed the assertion had been removed. **A correction line
describing a change that did not happen is worse than no line**, because the next run reads it and
believes the field is clean. Both are fixed, and the second history line says plainly what the first
one missed.

The deck was more rigorous than the record it cites. The record is the deliverable that comes first,
and it is now correct on every published surface.

## Proposals for the machine, none of them in this actor's lane

- **A rejected-findings gate.** Read every published string field of any docket item a run touches
  against that run's `claims.json` rejected list and fail the build on a match. This run corrected
  one field, wrote a history line saying it was done, and left the same assertion standing in
  another. Nothing checked.
- **A verbatim gate.** Diff every quoted string on a frame, byte for byte, against the `quote` field
  of the claim that frame cites. `copy_sync_check` compares skeletons and is blind to whitespace by
  construction, which is how six doubled spaces shipped inside quotation marks.
- **`aggregate_check` cannot see a count in a sentence.** It refuses "13 days" and refused a
  spelled "twice", so the deck's largest drawn numeral sits in `_undeclarable`, a field no gate
  reads. Apply EXEMPT to the matched span rather than discarding the whole node, and add the
  multiplicative number words.
- **`render_report` should emit a measured cell count per monospace node**, so a text-reading gate
  cannot be fooled by a rendered space in either direction.
- **The captions ledger's three exclusion lists are hand kept and drifted a second time**, stopping
  at 2026-08-20 and never picking up 08-21. Derive them from the entries.
- **`site_build.py`'s construction page numeral**, unchanged from the top of this record.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 23 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | PASS   | 9 slide(s), zero fails, zero warns |
| aggregates     | PASS   | 6 declared and re-derived |
| assembly       | PASS   | 9 slide(s), 3.37 MB, vector |
| score          | PASS   | 7.09 |
| dossiers       | PASS   | 28,198 chars planned |
| caption        | PASS   | 212 words |
| craft floor    | PASS   | 9 frame(s), median 658, floor 118 |
| plan vs render | WARN   | 6 of 48 acceptance item(s) checkable |
| texan          | WARN   | places NONE / body yes / deadline yes / next step yes |
| absences       | PASS   | 8 of 8 scoped to a named document |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
