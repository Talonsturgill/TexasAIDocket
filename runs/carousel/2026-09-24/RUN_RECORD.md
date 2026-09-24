# Run record, September 24th, 2026

## DISPOSITION: HELD UNDER THE FLOOR. THE PULL REQUEST IS OPEN AND READY AND IS NOT MERGED.

Carousel no. 33 finished the rubric's five scoring rounds at a panel median of **6.418**. The bar
is 8.0, and the ratchet floor at the cap is **7.01**, the level the last ten shipped decks held.
`run_complete.py` refuses a deck under that floor at the cap as a regression, and this run does not
override it. **Shipping this deck is the owner's call.** The path is an `owner_override` in
`score.json` with the instruction in the owner's words and a date. `run_complete` accepts that path
and records who took it.

The round 5 integrity judge raised a hard fail on frame 7. It was repaired after the cards arrived,
which is the one repair a round past the cap may make. The repair and its verification are in
`scores/hard_fail_repairs.json`. Every gate exits 0 on the repaired render. So if the threshold is
spent, no hard fail stands in the way.

| round | integrity | craft | reader | median | hard fails |
|---|---|---|---|---|---|
| 1 | 6.41 | 6.918 | 6.47 | 6.57 | 2, the same one: the caption pointed to an address the first comment did not carry |
| 2 | 6.09 | 6.87 | 6.874 | 6.798 | 1: the web edition said a person enters the draft in one sentence |
| 3 | 6.80 | 6.79 | 6.63 | 6.74 | 0 |
| 4 | 6.24 | 7.074 | 6.642 | 6.784 | 1: frame 7's bars showed a noise margin the draft does not give |
| 5 | 6.126 | 6.868 | 6.36 | 6.418 | 1: frame 7's repair showed no margin where the draft estimates one |

The numbers come from `scores/roundN-panel.json`, which `panel.py` wrote. They are not
recomputed here.

## The record, first, because it is the run's first deliverable

- **The worklist fell from 52 items due to 13.** Thirty-eight items were re-verified in Phase 3.
  The 13 still due all sit at a measured access boundary with a stamp inside its seven-day window,
  or are pending items whose next scheduled step has not arrived. None is rotten.
- **Two items were admitted.** tx-2026-0186 is the FAA's draft environmental assessment of
  Zipline's drone package delivery in five Texas metros, open for comment until October 11th.
  tx-2026-0187 is the PUCT's order adopting 16 TAC 25.194, decided September 18th and effective
  October 8th.
- **Boundaries were measured and stamped, not routed around.** Six CivicPlus-style municipal hosts
  returned a block page to every client, and newschannel10 refuses this fetcher in robots.txt. The
  details are in `knowledge/shared/SOURCES_FIELD_LOG.md`.
- **The judges' integrity findings reached the record, not only the deck.** tx-2026-0186 now has
  these fixes:
  - `on_ercot` is null, because the metros straddle the grid.
  - The summary says the draft "assesses" rather than "allows", says the pod "evaluates the drop
    spot automatically", and no longer ties the noise finding to setbacks.
  - Claim c12 says delivery noise "does not exceed" the threshold the draft uses.
  - The notes report the Section 106 letter's county discrepancy rather than repair it.
  - The FAA page title is corrected to the page's own title.
  - The FAA comment address stays on the FAA's page rather than in this site's prose, which
    house style requires.

## THE MOST SERIOUS THING THIS RUN DID IS A ROBOTS VIOLATION

During re-verification the run fetched three agenda pages on `public.destinyhosted.com`, a host
whose robots file disallows this fetcher. The run's robots reader parsed a robots.txt served as a
single line with no newlines as empty and treated it as permissive. The bodies were deleted,
nothing from them stamps a record or backs a claim, and tx-2026-0168 to 0170 stay on their
existing robots boundary.

An earlier draft of this record named a fourth fetch, a video page on `taylortx.new.swagit.com`,
as a violation too. The retro read that host's robots.txt and it disallows nothing, so that line
was wrong and is withdrawn.

The fix belongs to the daily lane, which owns `reverify.py` and `scripts/shared/**`. An earlier
draft called it a maintainer's fix, and that was wrong too. `reverify.py` has no robots reader, so
every run improvises one, and this is the third run in a row to trip on it. The proposal is in
`knowledge/carousel/UPGRADE_BACKLOG.md`.

## What the deck is

Nine frames are rendered through `txthree.js` in one golden-hour neighbourhood. The chassis is
`assets/js/deck/2026-09-24-droneline.js`. The motif is the pod on its winch line in the one accent,
#8FE0F0, carried across frames 1, 2, 3, 4 and 7 and gone on frame 9, where the gate that was shut
on frame 1 stands open. The deck turns on the one sentence where the draft sends an image to an
operator and gives no figure for how often. It closes on the FAA's comment address and the
October 11th deadline.

## Frame 7 took four encodings and three hard fails. That is the run's lesson

1. Linear decibel bars from zero drew 58.1 as nine tenths of 65.
2. Energy-scaled bars set the draft's 59.7 cap against 65, a margin the draft's own section 3.6.1
   removes: added noise of 59.7 is exactly what lifts 63.5 to 65. That was a hard fail in round 4.
3. Equal bars, 59.7 against that 59.7 lift, drew no margin. The draft's own estimate at the
   delivery point is 58.1, under its line. That was a hard fail in round 5.
4. Now there are no bars. The frame prints the draft's estimate, its screening line and its
   conclusion as text from `figures.json`, under the hook "It finds no significant impact".

Every encoding asserted a margin, and every margin was the run's inference rather than the
draft's. That is recorded as the instinct `a-decibel-bar-asserts-a-margin`.

The web edition's hard fail came the same way: a universal ("a person enters in one sentence")
that a text search of the fetched draft would have refuted. That is recorded as the instinct
`sweep-the-noun-before-an-absence`. The instinct
`a-repair-that-strengthens-a-claim-is-a-new-claim` held again and is confirmed.

## Claims added after the fact check, each matched verbatim against the fetched draft

- c29: 400 a day stands for places such as a large apartment complex.
- c30: the aircraft attaches to the dock from below.
- c31: "such as a residential yard".
- c32 and c34: docks per Charger, and three towers of twelve.
- c33: the Remote Pilot in Command.
- c35: the 59.7 screening line.
- c36: the noise report was prepared by ICF for the FAA.
- c37 and c38: the draft's 63.5 to 65 dB example.

The later judges checked all of these against `zipline_ea.txt`. The source is a same-day curl copy,
because WebFetch returned 403 from the FAA.

## What the art rounds cost and what they bought

Pixel review ran three rounds, each with three pixel critics and a flow critic. Scoring ran five
rounds. The judges agreed across all five rounds that artwork craft sat under 6. It was held there
by the showstopper cap and by primitives the engine does not yet build well:

- capsule people
- windowless box houses
- star-sprite grass
- sky banding on frame 3

The count frame, 6, went through a parallel camera, a long lens and a perspective lot, and never
satisfied both the grid gate and the judges' demand for a horizon. **The next deck that needs a
world should get the backyard kit built once, in the chassis, before any frame is composed.** Every
craft card named that fix.

## Things this run did not do

- The Supabase ask-pack step was not run.
- `article_check --date 2026-09-24` found no shipped run to check, because the deck is held, so the
  web edition was verified by `tests/test_article_edition.py` and the record gates only.
  `docs/articles/2026-09-24/` is not built, for the same reason.
- `reverify.py --apply` wrote `ledger/docket.json` at indent 2, and the run rewrote it at the
  canonical indent 1 by hand. Line 797 writes `indent=2` where `docket_build.py` writes 1. It is a
  daily lane fix, left for the next run.

## Prompt audit

`prompt_audit.py`, final reading before the email: 1861 tool calls measured, none waited on a
human.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 38 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 32 warn(s) |
| aggregates     | PASS   | 10 declaration(s), 12 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 8.58 MB, vector |
| score          | WARN   | 6.418 against 8.0 target; 5 round(s), cap 5; not a ship failure |
| labels         | PASS   | 58 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 90 published string(s) read from one list, every universal names its set |
| verbatim       | WARN   | no dossier declares a `verbatim:` block, so no on-frame string was held to a quote |
| dossiers       | PASS   | 33,846 chars planned |
| caption        | PASS   | 125 words |
| craft floor    | PASS   | 9 frame(s), median 2502, floor 450 |
| plan vs render | WARN   | 8 of 39 acceptance item(s) checkable |
| texan          | WARN   | places Amarillo, Austin, El Paso, Houston, San Antonio / body NO / deadline yes / next step yes |
| absences       | PASS   | 10 of 10 scoped to a named document |
| numerals       | PASS   | 21 numeral(s) over 9 frame(s), every one reachable |
| completion     | FAIL   | THE DECK DID NOT SHIP, so this run is not done |
<!-- gate-status:end -->
