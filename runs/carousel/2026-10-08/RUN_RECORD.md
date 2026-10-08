# Run record, October 8th, 2026

Effort at wake: `high` (as the repo's settings carry it). The no-stall hook logged `armed` at
06:16:02 UTC and judged the session unattended from SessionStart, with the host's
`CLAUDE_CODE_SESSION_ATTENDED=0`. It refused nothing. The interim reading in Phase 17 measured 1,419
tool calls. Six `Agent` dispatches carry a permission wait of 10.3 to 19.6 seconds, which
`prompt_audit.py` lists as WAITED ON A HUMAN. No human was present and none answered anything, so
those six are the host's own dispatch latency for a subagent spawn rather than a dialog. They are
reported as measured. 447 calls waited on the auto mode classifier, the longest 26.2 seconds.
**That reading is interim.** Phase 19 takes the one that counts, and the email carries it.

## DISPOSITION: SHIPPED AT THE ROUND CAP, 6.988, 0.712 UNDER THE 7.7 RUNG, AFTER TWO HARD FAILS WERE REPAIRED

Carousel no. 46, "Software on the radio. Merlin's account of the Project Nexus kickoff", is nine
frames rendered in one staged lastLight airfield world at Fort Worth Alliance Airport (haze
#1E2536, the sun at azimuth -104 and elevation 6), declared once in
`assets/js/deck/2026-10-08-nexus.js`. The hero is an illustrative white Caravan built to a 208B's
proportions in the chassis, drawn to illustrate on every frame that shows it. It is close at the
nose on 1, tail on to the tower on 2, paired with a second Caravan on 3, broadside under three
leaders on 4, absent from the record table on 5, a stopped propeller on 6, absent from the map on
7, on the threshold stripes on 8, and standing at the end of the 28 lit day lamps on 9. One radio
cyan (#8FE0F0) marks the radio path, the one lit record lamp, the Texas stripe and the elapsed days.

The story is tx-2026-0205, admitted today. TxDOT launched the first phase of Project Nexus at
Fort Worth Alliance Airport on September 10th. Merlin says TxDOT invited it to demonstrate its
Merlin Pilot there, including AI-powered air traffic control communications. Neither TxDOT's
release nor the FAA's names Merlin, and none of the three releases says whether a pilot was aboard
or prints a measured result.

The deck went through these reviews:
- three pixel critic rounds, the smaller tier, five critics in round 1 and three in rounds 2 and 3
- two flow critic rounds, the first returning revise with a reorder, the second returning ship
- five art preflight rechecks by the same flow critic, the last accepted on the shipped frames
- three panel rounds of three judges

The panel medians were 6.614, 6.942 and 6.988, read from `score.json` each round. Round 3 is the
cap on the ladder (8.0, 7.7, then ship). The finished deck ships at 6.988, 0.712 under round 2's
7.7 rung. **The craft floor stood down at the cap with the art median at 6.5**, under its 8.5 line.

**The round 1 hard fail.** The integrity judge failed the absence "none of the three says how it
went". Merlin's own release (c27) says the demonstration showed the Merlin Pilot can "safely and
effectively" perform pilot responsibilities, so the deck had widened the fact check's narrower
finding, and `compute.py` had typed the table's two silent rows as constants. The repair:
- the record table's third row is now PRINTS A RESULT
- `compute.py` scans the three release snapshots for both silent rows with regexes, and its result
  pattern skips the ticker line in the syndication chrome
- frame 5's dek, the caption and the web edition say none prints a measured result
- frame 4's dek carries c27's "safely and effectively", attributed to Merlin

**The round 3 hard fail.** The integrity judge failed the web edition's "reducing pilot workload
rather than removing the pilot" (c28). The quote says only "while reducing pilot workload,
improving operational efficiency, and enhancing safety". c28's text and the article now say that,
the judge read both files and reissued its round 3 card with no hard fail, and `panel.py`
recombined the cards without counting a fourth round.

**After the cap, one numeral repair.** The Phase 17 gate sync found "1,096" on frame 9 tracing to
nothing once the day count was reworded to "28 days in, of 1,096", because no declared aggregate
carried it. An untraced numeral is a hard fail, so frame 9's dek now reads "28 of 1,096 days had
passed by October 8th", declared as a ratio from `compute.py`. Only that sentence changed, the
art preflight was re-accepted on it, and `panel.py` recombined the same three cards, which is not
a round. The judges scored the frame with the earlier wording.

**What the panel named and the run repaired between rounds.**
- The day count reads "28 days in, of 1,096", because "day 28" mixed conventions.
- Frame 1 cites c2 for the FAA's release, and frame 4's third label carries c26's full
  "in-flight re-planning and threat avoidance".
- The caption's next phase is "medical and cargo logistics", as c17 states it.
- Frame 6 pulled back so the nose gear stands on the lit apron with a horizon. Frame 9's Caravan
  moved beside the 28th lamp and the camera dollied up the runway. Frame 4 raised and yawed off
  broadside, and its labels were restacked after a leader crossed AVOIDANCE.
- The first comment's document titles no longer carry the post's own year.
- The "names Merlin's Caravan" row now scans each snapshot for both words anywhere. The TxDOT
  snapshot, text and HTML, contains no "Merlin" at all, which closes the judge's open question.

**What the panel named and the run did not fix.**
- The hero model. All three judges in every round charged the art to the chassis Caravan: flat
  black window cutouts, the high wing a slab from a long lens, the strut crossing the windows, the
  tower's L-shaped base. A defect named in every round is a composition problem, and recomposition
  moved it only partly, so it is queued as `aviation-models-built-in-chassis`.
- Frame 3's empty lower apron. Two recompositions were tried and both cropped the planes worse, so
  the run kept the round 2 camera.
- Frames 5 and 8 carry the lastLight horizon's warm band behind the type. The world is declared
  once for the deck, so it can't change per frame. Queued as `lastlight-horizon-warm-band-behind-type`.
- c33, the Dallas Innovates caption credited to TxDOT that shows Merlin's Caravan in the test
  flights, is cited on frame 3 and printed nowhere. The integrity judge asked for one sentence
  carrying it. That is not a hard fail and the cap allows only hard fails, so it is work for the
  record entry and the next deck that touches this story.
- Frame 5's dek leaves "result." on a fifth line, a widow the preflight critic named twice.
- No frame names a next step for a reader. The record holds no comment window or meeting for this
  program to point to.

## The deck's work, in order

1. **Scouts, six beats.** The policy beat carried Project Nexus. 48 claims verified, 25 rejected.
2. **Selection.** `runs/carousel/2026-10-08/SELECTION.md`. Memorial Hermann was refused by the
   30-day rule, Volvo and Waabi sat too close to no. 41's Kodiak trucks, and the PUC lawsuit and
   the WT feedlot plan were thin.
3. **Directors and storyboard.** One world, one hero, CONTINUITY on MOTIF_EVOLUTION, CAMERA_MOVE and
   EDGE_TEASE.
4. **Chassis.** The Caravan, lamp row, windsock and tower were built in the chassis because the kit
   has no aviation models. An apron flood (`N.flood`) makes the stage's pool a real light.
5. **The layout gate.** It refused four frames on detail and the accent on two. The cure was
   recomposing the frames and fitting each rect to where its subject renders. The lamp table is
   declared OBJECT_AND_CAPTION because the GRID piece count reads the lit apron as one silhouette,
   queued as `grid-piece-count-reads-lit-ground-as-subject`.
6. **The flow critic's reorder.** Merlin's claims moved ahead of the record table, so the record
   frame alone carries the absence and turns the deck.
7. **Frame 9 rebuilt twice.** Seen from beside the threshold, the 28 lit lamps of 1,096 filled the
   foreground and read as most of the schedule. From the infield behind the threshold the lit run
   reads short against a long dark row, and the Caravan stands where it ends.

## The record, first

- Re-verification: 83 items stamped with reworded notes, every reworded note passing
  `reverify.py --check-notes`. tx-2026-0024's PUCT calendar was rewritten from the live feed with
  its October 15th hearing and November 16th workshop.
- Boundaries re-measured on October 8th. tx-2026-0041 now carries a legacy `blocks_every_client`
  block, and tx-2026-0055's claim-source block was re-measured with its hashes.
- Admitted: tx-2026-0205 (TxDOT Project Nexus, statewide), tx-2026-0206 (Volvo and Waabi's Warp,
  Dallas and Harris), tx-2026-0207 (the WT feedlot, Randall).
- Two re-verification notes, on tx-2026-0162 and tx-2026-0202, were split after the house style
  check found sentences over 30 words in the rebuilt pages.
- `docket_build.py --validate` is clean.

## Sources that behaved differently from the registry

Appended to `knowledge/shared/SOURCES_FIELD_LOG.md` under October 8th: the FAA's newsroom split
between the fetcher and a browser, Wichita Falls' agenda center refusing both, the TACC robots
split, Angelina County's minutes PDF now readable, Merlin's release read through Finviz's
syndication, and the Attorney General's 402.

## Instruments

All exit 0: `gridwatch_pagecheck`, `waterwatch_pagecheck`, `waterwatch_page --self-test`, the
scratch site build, `media_check`, `schema_check`, `og --self-test`, `favicon --self-test`,
`truetype --self-test`, `indexnow --self-test` and `seo_check`. No instrument stopped.

## Did this run stop and wait for a human

No dialog was answered by anyone. The hook refused nothing. Six `Agent` dispatches carry a
permission wait of 10 to 20 seconds in the debug log, measured above and named in the email.

## The weekly machine pass

Not due. The last pass ran on October 7th, and no queued item reached a repeat count of 2.

## Queued for the next pass

Five new items in `knowledge/carousel/MACHINE_QUEUE.md`:
`aviation-models-built-in-chassis`, `stage-pool-hides-flood-light`,
`lastlight-horizon-warm-band-behind-type`, `grid-piece-count-reads-lit-ground-as-subject` and
`scorer-thumb-path`. `article-test-screenshots-fixed-path` was raised to repeat 1, because the
article browser test again wrote its screenshots for the September 18th edition and today's new
edition was checked by its 765 automated reader checks only.

## Craft memory

Confirmed `a-paraphrase-can-outrun-its-quote` (c28), `a-repair-lands-on-every-surface` (the round 1
repair reached the slides, the caption and the edition) and `acceptance-items-need-a-floor`
(`dossier_check` refused frame 9's list). Added `perspective-overstates-the-near-run`.

## Things this run did not do

- The weekly machine pass, which was not due.
- A visual inspection of the new article's screenshots, for the reason queued above.
- Any rewrite of a shipped run.

## Discoverability signoff

- Card, opened as an image: `og/tx-2026-0205.png`, the run's newest item. The title wraps on word
  breaks and ends on the whole word "aircraft" with an ellipsis.
- `/questions/`: 180 answered for what each decision is and 175 for who decides. Nothing new in
  shape today, since the three admissions use `contact_only`.
- `llms.txt`, Open right now: the Zipline window (closes October 11th), the CFTC window (October
  20th), the energy department's window (closes October 9th) and the PUCT calendar. Nothing listed
  has closed. tx-2026-0072 is listed because its item carries an open meeting room, which is worth
  a maintainer's look.
- `/sources/`: 1043 of 1196 claims rest on a primary document, across 325 documents from 139
  publishers.
- `/topic/`: State policy shows 23 decisions, including tx-2026-0205 and tx-2026-0206, checked
  against the record rather than the page's link count.
- `/place/`: Randall County is on the hub with 3, including tx-2026-0207.

## Gate status

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 48 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 5 warn(s) |
| aggregates     | PASS   | 15 declaration(s), 21 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 8.22 MB, vector |
| score          | WARN   | 6.988 at the round cap after 3 round(s), the finished deck ships; 8.0 top rung, shortfall named |
| labels         | PASS   | 72 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 87 published string(s) read from one list, every universal names its set |
| verbatim       | PASS   | 3 declared fragment(s) over 9 of 9 dossier(s), every one a literal substring of its own claim's quote, 1 slot note(s) |
| dossiers       | PASS   | 35,795 chars planned |
| caption        | PASS   | 136 words |
| craft floor    | PASS   | 9 frame(s), median 1772, floor 319 |
| plan vs render | WARN   | 2 of 42 acceptance item(s) checkable |
| texan          | WARN   | places Austin, Dallas, Fort Worth, Houston, San Antonio / body yes / deadline yes / next step NO |
| absences       | WARN   | 4 of 10 scoped to a named document, 6 unscoped |
| numerals       | PASS   | 6 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
