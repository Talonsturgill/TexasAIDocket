# WORKLOG — run 2026-09-03

Durable plan for the daily routine, written to survive context compaction. Delete when every
wave is DONE.

Lives at `runs/carousel/**` (the `daily` lane, not sensitive) and never under `.claude/`. See
CLAUDE.md and `scripts/shared/sensitive_paths.py`.

## Context this run inherited

The 2026-09-02 run COMPLETED and shipped carousel no. 13 at 6.562 on the owner's instruction. Its
WORKLOG was left behind at `runs/carousel/WORKLOG.md` with waves 4 through 19 still reading TODO,
which was stale rather than true. This file replaces it.

**The record is in good shape at wake, and that is new.** Yesterday's run cleared all 98 items, so
this run woke to **6 due and 0 rotten** rather than 98 and 14. `docket_build --validate` is exit 0
with two staleness WARNs, both of which are on today's worklist.

## Branch, and a deliberate departure from the session directive

The session trigger named `tsturg/practical-franklin-2bgu78` as the development branch. **This run
is on `claude/daily-2026-09-03` instead**, and that is not a preference. `resolve_actor()` in
`scripts/shared/ownership_check.py` reads the lane off the branch PREFIX, so `claude/daily-` is the
only thing that makes both git hooks judge this run as `daily`. On the named branch every commit
would resolve to `human` and the pre-commit hook would refuse the run's own work. The routine file
is the source of truth per the trigger's own last line, and it names this branch shape in Phase 0.

## Decisions already made, with the measured reason

- **`news.rice.edu` returns HTTP 406 to this client**, confirmed again this run on
  `tx-2026-0098`. Yesterday's field log already carries it. The NSF award API is the primary
  source for that item and it answers, so the item is repairable rather than unverifiable.
- **The PUCT calendar RSS is a ROLLING FEED**, so a quote leaving it is the feed advancing rather
  than a decision moving. `tx-2026-0024` is the item whose whole subject is that feed, and its
  claims will age out of it by design. This needs a durable answer, not a re-quote every two days.
- **`yahoo.com` article urls are not a primary source** and `tx-2026-0038` rests on two of them.
  That item was already left unstamped on 2026-09-02 for a 503.

## Off the table today

Topics, 30 days, all thirteen ledger entries are inside the window: the Grimes County fab and
JETI; HISD Future 2; the Governor's data center audit and Batch Zero; League City's ALPR ballot;
driverless trucking and SB 2807; PUCT Project 58482 as a DECK; the twelve local governments
pattern; the UT System capital program; Amazon's Austin robotics siting; PUCT Docket 59220 and
Crusoe; NSF award 2535195 and the UT Austin robotics centre; the Flock money trail and the MVCPA;
the Senate Economic Development calendar row.

Beat balance: five of the last thirteen decks came off `power-and-compute` and three more off
policy. **This run aims at an application beat.**

Art, from deck no. 13's own `avoid_next`:
- **One primitive carried five of nine frames** on no. 13, a lighter rectangle holding type seated
  on stone with a lit bevel and a contact shadow. The craft judge scored artwork_craft 5.5 and
  named the real fault: the detail budget was front loaded exactly opposite to the argument, which
  ends on frames 7 to 9. **This deck spends its invention where the argument ends.**
- **A declared technique that did not reach a reader.** No. 13's frame 8 declared white line
  intaglio and shipped 190 low alpha lines inside two thin strips, so a judge said the frame
  carried no engraving at all. An acceptance item can be vacuously satisfied by a frame that draws
  nothing.
- **The declared key elevation did not render.** 8 degrees was in the dossier and in no drawing
  step, so nothing measured it. A declared light angle goes in the code or it is not declared.
- Spent and not to be reached for: the halo behind type (no. 12), the soft luminous edgeless field
  (no. 12), red granite under one grazing key (no. 13).

## Wave status

| wave | what | status |
|---|---|---|
| 0 | wake, branch, hooks, gates | DONE. validate exit 0, ownership self-test exit 0, bootstrap ok |
| 1 | craft refresh | TODO |
| 2 | scouts away, staleness read | DONE. 5 scouts spawned. 6 due, 0 rotten, 0 deferred |
| 3 | re-verify the record, 6 due | IN PROGRESS. reverify --apply exit 1, 0 stamped, all 6 need hand work |
| 4 | discover | TODO |
| 5 | admit | TODO |
| 6 | claims | TODO |
| 7 | instrument once over | TODO |
| 8 | selection + dedupe | TODO |
| 9 | directors room | TODO |
| 10 | copy chamber | TODO |
| 11 | art build | TODO |
| 12 | pixel review | TODO |
| 12b | the six gates | TODO |
| 13 | aggregate gate | TODO |
| 14 | assembly, panel_ready | TODO |
| 15 | scoring panel | TODO |
| 16 | assemble, PR | TODO |
| 17 | retro + upgrade | TODO |
| 18 | merge | TODO |
| 19 | gmail draft | TODO |

## The six items on today's worklist

| id | what | what reverify said |
|---|---|---|
| tx-2026-0109 | Senate Economic Development cancels its September 3rd hearing | c4 quote gone from MeetingsUpcoming. Key date is TODAY |
| tx-2026-0002 | PUCT Project 58482, Large Load rule | c4 not readable on the RSS |
| tx-2026-0024 | PUCT open meeting calendar as a live feed | c1 and c3 gone, c2 and c4 unreadable. Rolling feed |
| tx-2026-0016 | Federal comment window on AI questions in the ATUS | c1 not readable on the Federal Register page |
| tx-2026-0038 | Harlingen Waterworks effluent water agreement | c1 and c2 rest on yahoo.com. Unstamped since 08-29 |
| tx-2026-0098 | NSF funds a Rice AI materials laboratory | news.rice.edu 406 on c2, c3, c4 |

## Sources field log to append at Phase 17

- `news.rice.edu` returns HTTP 406 to this client, second consecutive run.
