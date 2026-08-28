# Run record, August 28th 2026

Deck no. 10. One run, two deliverables. Branch `claude/daily-2026-08-28`.

## The record

**Worklist cleared in full.** `docket_staleness --today 2026-08-28` named 41 items due, nothing
rotten and nothing deferred. All 41 were re-verified and the selector now reports nothing due.

- `reverify.py --apply` fetched 66 urls behind 200 claims. Seven answered 304, 59 sent a body,
  none failed to answer. It stamped 38 items as checked and unchanged and handed back three it
  could not read.
- The three it handed back were done by hand. tx-2026-0015 was confirmed against the Federal
  Register document page, which still carries the Executive Order 14300 framing and the August
  31st close date. tx-2026-0002 and tx-2026-0024 were confirmed against the commission's calendar
  feed, fetched with a browser User-Agent.
- **The 37 template notes the script wrote were rewritten into prose.** The deterministic line is
  the floor and not the finish, and a reader who opens ten items in a row should not meet the same
  three sentences ten times. `reverify --check-notes` reads 90 checked notes with every figure
  traceable.

**One item corrected on the world moving.** The commission's calendar feed added a second public
comment deadline, so tx-2026-0024 no longer says the feed carries one. The August 20th and August
21st open meetings have come off the feed now they have been held, and the two claims that rested
on them are rewritten against the August 28th meeting the feed leads with.

**Two items admitted, both on primary documents read in full this run.**

- `tx-2026-0107` PUCT Project 59550, the first five year review of the ERCOT system-wide offer cap
  programs. Comments due September 17th, 2026. Found by following the new calendar entry to the
  staff memorandum behind it.
- `tx-2026-0108` PUCT Docket 59220, the net metering order and the motion for rehearing against
  it. This is the deck's story.

**Fifteen candidates held in the seed**, on the same reasons as previous runs, and nothing was
lowered to admit them. One is worth naming because it is a vocabulary gap rather than a source
gap. `tx-2026-0083` is held on `topic 'ai-in-the-field' is not in the vocabulary`. That beat is in
the routine's scout table and is not in `docket_build.TOPICS`, so a scout finding filed under it
can never be admitted. Proposal below.

## The backlog

**Three entries at wake and three now.** Held steady, which the success criteria allow, and it did
not grow.

**One of the three describes a gap that no longer exists.** `tx-2026-0007` already carries
`statewide: true`, so the line saying it names no county and is not statewide is false about the
current record. `docket_build.backlog` prints every id in `GEOGRAPHY_BACKLOG` unconditionally
rather than checking whether the item still has the gap, which means this ratchet can never
shrink no matter what the record does. That is the shape `GATE_LESSONS.md` keeps recording, a
green surface measuring something other than what it appears to certify. `scripts/site/` is
`human` owned, so this is a proposal and not a change.

The other two, `tx-2026-0001` and `tx-2026-0002`, are genuine. Both are PUCT rulemakings whose
scope is the ERCOT region rather than a set of counties, and the record has no grain for that.
They were left rather than flagged statewide, because a statewide flag used to mean the scope
could not be established is worse than holding the gap open.

## Discoverability signoff

- **One decision's card, opened as an image.** `og/tx-2026-0108.png`. The first title ran long and
  the card cut at "behind a wind farm and", stopping on a conjunction. The title was rewritten so
  its first clause is the whole story, and the card now carries "PUCT told an Armstrong County AI
  data center to shed its whole load, and" across its four lines. The wrapper's budget is about
  four lines, so the fix is a title whose first clause stands alone rather than a shorter title.
- **`/questions/`, read as a reader.** Twelve question shapes, 93 answered on most and 87 on how
  the public can take part. The six open comment windows count includes today's tx-2026-0107. The
  questions read as ones somebody would type.
- **The `Open right now` section of `llms.txt`.** Nine entries. tx-2026-0107 is listed with its
  September 17th window, correctly. tx-2026-0108 is not listed, also correctly, because its room
  is `contact_only` and it has no dated window. Nothing listed there has a window that closed.
- **`/sources/`, the record's own report card.** 378 of 452 claims rest on a primary document,
  across 165 documents from 71 publishers. Every claim admitted today is `primary_official`, so
  this run moved the share up rather than down. The top publisher is
  `interchange.puc.texas.gov`, which is the state's own filing system and is what a primary source
  looks like. Its document list reads as filings. The quoted-material exemption is still doing its
  job and is not hiding any of our own sentences.
- **`/topic/`, one card against its own page.** Data centers reads 26 of 93 on both the hub and
  the beat page. The eight beat counts sum to 93, which is what the front page's own counter
  prints.
- **`/place/`, for the place this run landed something in.** Armstrong County is on the hub at 1
  and its own page says 1 item and names the Amarillo metropolitan statistical area, which is
  right. The front page now lights 62 of 254 counties.
- **The water map's pins against the day's reservoir count.** `waterwatch_pagecheck` and the page
  self-test both pass and the map draws one circle per reservoir at its own gauge. The readout and
  the drawing agree.

## Instruments

`gridwatch_pagecheck` and `waterwatch_pagecheck` both exit 0, current and holding their promises.
`waterwatch_page --self-test` all passed. **No instrument has stopped and nothing here needed a
presentation fix.**

`schema_check` went red once during this run and it was this run's own doing, not a defect. A
claim's source url had been repointed at the Federal Register API while the item page still cited
the document page, so the page cited a url in no claim. The claim was restored to the document
page, which was fetched this run and carries the quote. Green after.

## What the scouts found and what was not published

Six scouts on six beats, four of them application beats. Thirteen findings were rejected and the
reasons are in `claims.json` beside the verified claims. The pattern worth naming is that the
strongest-sounding findings were the weakest sourced. An AI drone surveillance operation over
Texas livestock turned out to rest on a podium description while the agency's own page never uses
the words. A hospital AI result with a percentage in it turned out to rest on a vendor's release
rather than on either journal article.

**Two Texas cities let their Flock camera contracts lapse on the same Tuesday night**, Pflugerville
and Wylie, both on August 25th. Both agendas were fetched and quote cleanly. It is held rather than
published because the rejections themselves rest on reporting while neither city's minutes are
final, and it is queued as the strongest lead for the next run.

## The scanner's daily ceiling

**Not checked this run, because there is no Supabase connector in this session.** The tool search
returns nothing for the `texas-ai-scanner` project, so the query in the routine could not be run at
all. That is the third of the three outcomes the phase names and it does not block the run, but it
is worth saying plainly rather than folding into a list. The ceiling nobody is notified about is
still unwatched today, and a requester who hit it was told the day was full and nobody heard.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 26 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | PASS   | 9 slide(s), zero fails, zero warns |
| aggregates     | PASS   | 7 declaration(s), 10 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 7.2 MB, vector |
| score          | ABSENT | score.json not written yet |
| labels         | ABSENT | label_report.json not written yet. Run scripts/carousel/label_guard.py <run-dir> |
| quantifiers    | ABSENT | quantifier_report.json not written yet. Run scripts/carousel/quantifier_check.py <run-dir> |
| dossiers       | PASS   | 36,570 chars planned |
| caption        | PASS   | 143 words |
| craft floor    | PASS   | 9 frame(s), median 253, floor 60 |
| plan vs render | WARN   | 8 of 49 acceptance item(s) checkable |
| texan          | PASS   | places Armstrong County / body yes / deadline yes / next step yes |
| absences       | PASS   | 7 of 7 scoped to a named document |
| completion     | ABSENT | not scored yet |
<!-- gate-status:end -->
