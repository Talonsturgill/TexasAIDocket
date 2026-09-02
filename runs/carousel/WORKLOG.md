# WORKLOG — run 2026-09-02

Durable plan for the daily routine, written to survive context compaction. Delete when every
wave is DONE.

**This file used to live at `.claude/WORKLOG.md` and moved here on 2026-09-02.** The host classes
everything under `.claude/` as a sensitive file and prompts on every edit, whatever the permission
mode says, and the old path was `human` lane on top of that, so the routine was told to maintain a
file it could neither write unattended nor commit. `runs/carousel/**` is `daily` and is not
sensitive. See CLAUDE.md and `scripts/shared/sensitive_paths.py`.

## Context this run inherited

The previous WORKLOG was for 2026-08-30 and was STALE. That run finished and shipped carousel
no. 12 as PR no. 243, and nothing deleted the file.

**Two runs did not happen.** There is no `runs/carousel/2026-08-31` and no `2026-09-01`. So the
record went five days without a re-verification pass against a two day leash, and CI on `main` was
already red on `Nothing rotten in the record` before this run started.

## The session was interrupted, and it cost the first scout pass

The first process ran 06:16 to 06:36 UTC and was interrupted. Six `carousel-scout` agents had been
spawned at 06:19 and were in-process, so their findings were lost with it. The record work
survived because it was on disk. Scouts were re-spawned at 12:15 on four beats rather than six,
carrying this run's own measured source notes.

## Decisions already made, with the measured reason

- **PUCT is NOT down, and last run's field note saying so is wrong.** `interchange.puc.texas.gov`
  answers HTTP 200 to a browser User-Agent and refuses ours with 402 or 503. That is exactly what
  `SOURCES_REGISTRY.md` already said. Six items were about to be written off as unverifiable and
  four of them had genuinely moved.
- **The Supabase connector is not available in this session**, so Phase 7's scanner cap query
  cannot run. The routine's own third outcome applies. Recorded, not worked around.
- **The deck may not be a data center, ERCOT or PUCT story.** Five of the last twelve came off
  `power-and-compute` and two more off ALPR.

## Off the table today

Topics, 30 days, all twelve ledger entries are inside the window: the Grimes County fab and JETI;
HISD Future 2; the Governor's data center audit and Batch Zero; League City's ALPR ballot;
driverless trucking and SB 2807; PUCT Project 58482 as a DECK; the twelve local governments
pattern; the UT System capital program; Amazon's Austin robotics siting; PUCT Docket 59220 and
Crusoe; the NSF robotics centre at UT Austin; the Flock money trail and the MVCPA.

Art, from `artwork.json` `avoid_next`:
- **The halo set in the field is spent** on deck no. 12. A second consecutive one is one drawing
  made twice.
- **The soft luminous edgeless field is spent**, and its failure mode is recorded: a field with no
  edges gives a reader nothing to hold at 432px.
- The high bay night interior (no. 9) and the notice case (no. 7) are each inside one cycle.
- A light deck is near its cap. No. 8 breached it on 2026-08-26 against a one-per-eight-runs rule,
  so this run aims mid to dark and MEASURES rather than declares.

## Craft refresh, Phase 1

Focus: **what makes a frame survive 432px**, chosen because it is what deck no. 12's own
`avoid_next` note says it got wrong. The usable finding is the illustrator's **silhouette test**.
Fill the subject solid, remove every interior line, and check the contour alone still says what
the frame is about. It is worth having because it is CHECKABLE rather than a taste note, so it can
go in a dossier acceptance list instead of being argued in a review round.

## What the record did, and it was the whole first half of the run

| reading | at wake | now |
|---|---|---|
| items due | **98 of 98** | 1 |
| rotten | **14** | **0** |
| backlog | 3 | 3, its floor, all grandfathered |
| `docket_build --validate` | exit 0, WARN | exit 0, WARN |
| `reverify --check-notes` | not run | exit 0, 192 notes, every figure traceable |

`reverify.py --apply` read 176 urls behind 501 claims and stamped 61 items. The remaining 37 were
worked by hand against a primary source each.

**Two items were telling readers something that had stopped being true**, which is the whole point
of the leash:
- `tx-2026-0109` promised a September 3rd Senate Economic Development hearing on AI and the Texas
  workforce. It is **canceled** and the committee is reset for September 22nd.
- `tx-2026-0015` read as an open federal comment window on NRC reactor licensing. It **closed on
  August 31st**.

Four PUCT dockets had moved once the User-Agent was right: a published comment deadline on the
Large Load rule, a ballot memorandum on Docket 59220 after Ensign's motion for rehearing, an order
severing proceedings plus an amicus brief from the Attorney General on Docket 59029, and the staff
memo that opened comments on Project 59550.

**One item is deliberately left unstamped.** `tx-2026-0038` (Harlingen waterworks) returned 503,
so nothing about it is confirmed and it says so rather than carrying a stamp it did not earn.

## Wave status

| wave | what | status |
|---|---|---|
| 0 | wake, branch, hooks, gates | DONE |
| 1 | craft refresh | DONE, see above |
| 2 | scouts, staleness read | RE-SPAWNED 12:15, four beats |
| 3 | **re-verify the record, 98 due** | **DONE. 0 rotten, backlog steady** |
| 4 | discover | pending the scouts |
| 5 | admit | TODO |
| 6 | claims | TODO |
| 7 | instrument once over | PARTIAL. Page checks and self-tests green, Supabase unavailable |
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

## Sources field log to append at Phase 17

- **PUCT is not down and the 2026-08-30 note saying it was is wrong.**
  `interchange.puc.texas.gov` and `puc.texas.gov` answer HTTP 200 to a browser User-Agent and
  refuse ours with 402 or 503. The registry already said this and last run recorded an outage
  instead. Cost this run six items nearly written off, four of which had moved.
- `taylortx.gov` newsflash detail pages now 404 to every client, browser User-Agent included. The
  Compal abatement notice at `/m/newsflash/Home/Detail/2066` is withdrawn and the city has
  published no outcome for the August 13th council meeting it noticed.
- `news.rice.edu` returns HTTP 406 to this client.
- `www.oncor.com` deep project pages time out, and the parent
  `current-transmission-line-projects.html` answers.
- `myharlingennews.com` returned 503.
- Legistar (`webapi.legistar.com/v1/<place>/matters/<id>/histories`) is reliable and is the
  cheapest primary source in the record for a city or county vote.
- Federal Register API and NSF award API both answer cleanly.
