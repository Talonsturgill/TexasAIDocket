# Run record, September 16th, 2026

Branch `claude/daily-2026-09-16`. Carousel no. 26.

## The instrument check

Both instruments clean by exit code. `gridwatch_pagecheck` 0, `waterwatch_pagecheck` 0,
`waterwatch_page --self-test` 0. Nothing has stopped and nothing is reading wrong.

**THE SCANNER'S DAILY CEILING WAS NOT CHECKED, and that is a gap rather than a quiet day.**
Phase 7 asks for a Supabase query against project `texas-ai-scanner`. No Supabase connector is
attached to this environment, so the query could not be run by any route. A requester who hit
the cap today would not have been noticed here, which is the exact failure the step exists to
catch. This never blocks the run and it is named here because a ceiling nobody is notified
about is one you find out about from the people who gave up.

## The record

The selector named **128 of 138 items due**, nothing rotten, and DEFERRED empty. No `--budget`
was passed. **The worklist finished at zero due.**

`reverify.py --today 2026-09-16 --apply` read 225 urls behind 701 claims. 35 answered 304, 184
sent a body, 6 did not answer, and it stamped 90 items as checked and unchanged.

The remaining **38 were re-checked by hand**, and the reason they landed there is worth stating
because it is a property of the fetcher rather than of the record. `wilcotx.gov` and
`brownsvilletx.gov` answered 429, `news.rice.edu` answered 406, six items cite an agenda or an
attachment PDF, and Oncor timed out. A browser User-Agent and a PDF reader settled all but six
claims. Twelve items came back with every claim present. Every one of the 38 carries its own
dated movement line.

The 90 deterministic lines were re-worded one at a time. `reverify.py --check-notes` reports 910
checked notes with every figure traceable.

### Nine claims were resting on a page that cannot hold them

Three items cited `capitol.texas.gov/Committees/MeetingsUpcoming.aspx`, which carries only what
is still AHEAD. A quote taken from it stops being verifiable the moment the hearing is held, so
those claims had been reported as moved on every run since the sittings, and would have been
forever.

`MeetingsByCmte.aspx` is the permanent archive, on the same allowed host path, and it reproduces
the same date, time and committee. Seven claims now cite it.

**One was deliberately left where it was.** `tx-2026-0096-c5` carries the hearing room, and the
room has no durable home: the notice PDF that would carry it is under `/tlodocs/`, which the
sources registry puts off limits. Re-pointing it would have quietly dropped a sourced fact from
reader copy, which `--check-notes` caught by refusing the numeral. A claim that can no longer be
re-confirmed is better than a fact the record stops being able to show.

### What moved

**House State Affairs sat again on September 14th and September 15th.** Both sittings are in the
record now, from the committee's own archive, with the dates as key dates. What it took up at
either is not yet established here.

`tx-2026-0027` is confirmed by its own failure. The item says the City of Taylor's notice of the
amended abatement is no longer posted, and the address now answers 404.

### The backlog

**Both ratchets are at zero and neither grew.** No item is without a county or a statewide flag,
and no reader-copy pointer names an item the record does not hold.

## Discoverability signoff

- **One decision's card, opened as an image.** `docs/og/tx-2026-0161.png`, the run's newest item.
  1200 by 630. The headline wraps after "builds a", "federally funded AI" and "tutor that
  withholds", all places a reader would break it, and it ends on a whole word before the
  ellipsis. **The finding is the truncation rather than the wrap.** The title carries two halves
  and the card shows one, so somebody who meets this item through a shared link sees the tutor
  and never learns the same method is being pointed at police training. That is a title-length
  problem, not a renderer problem.
- **`/questions/`, read as a reader.** 13 questions. They are the ones somebody would type, and
  "Where a comment window is open" and "When each one was last checked" are the two that only
  this record can answer. No shape has broken against the statuses now in the ledger.
- **The `Open right now` section of `llms.txt`.** Three federal windows, each with its dated way
  in, and each one matches an item Phase 3 re-verified as still open today. Nothing closed today
  is still listed, so the build is not running ahead of the record.
- **`/sources/`, the record's own report card.** **682 of 764 claims rest on a primary document,
  across 239 documents from 106 publishers.** The share is the figure that tests the promise the
  whole record makes and it is the one to watch. The top publisher is
  `interchange.puc.texas.gov` at 99 claims over 20 documents, which is the filing system itself
  rather than a report about one, so the head of that list is where it should be. `api.nsf.gov`
  is second at 54. The quoted-material exemption is still doing its own job and is not sheltering
  any of our sentences.
- **`/topic/`, counting one card against its own page.** The research and science page says 26 of
  138. The eight beats on the hub row read 30, 6, 17, 15, 16, 26, 17 and 11, which sum to 138 and
  match both the ledger and the front page's own `138 Decisions tracked`.
- **`/place/`, for the place this run landed something in.** `place/county-tarrant/` says 4 items
  and links exactly the four the ledger puts in Tarrant County, `tx-2026-0059`, `tx-2026-0062`,
  `tx-2026-0103` and `tx-2026-0161`. Tarrant is on the hub, so the build did not run ahead of the
  record.

The front page counter row prints five of its six candidates and `Sources cited` is among them.

## Sources, what they actually did

Appended to `knowledge/shared/SOURCES_FIELD_LOG.md` in this run's commit range.
