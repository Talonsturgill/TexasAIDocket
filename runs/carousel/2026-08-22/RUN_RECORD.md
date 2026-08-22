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
