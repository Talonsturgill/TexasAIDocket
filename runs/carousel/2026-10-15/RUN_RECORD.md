# Run record, October 15th, 2026

Carousel no. 51, In re Patrick Hughey: a Montgomery County trial court struck a deposition
transcript made with an AI platform because no certified shorthand reporter prepared it, and the
Supreme Court of Texas heard the mandamus petition on October 6th. Docket item tx-2026-0127.

## DISPOSITION: SHIPPED AT THE ROUND CAP, 7.258, UNDER THE 8.0 TOP RUNG, HARD FAIL REPAIRED IN ROUND 1

Three panel rounds. Round 1 combined at 6.902 with a hard fail from two of three judges, round 2 at
7.176 under its 7.7 rung, round 3 at 7.258 at the cap with no hard fail, so the finished deck ships
with the shortfall named. `score.json` carries the arithmetic. The art median in round 3 was 6.7,
under the 8.5 craft floor, and the floor stands down at the cap; the deck ships as it was measured.

The world is a staged lastLight night around a granite courthouse stair whose risers count the
months from the strike to the argument, declared once in `assets/js/deck/2026-10-15-transcript.js`.
The hero is the bound transcript on every frame. Bluebonnet #4E5FA8 is the one accent and means
certification only. The AI transcript's own certificate is drawn in grey ink, because the deck's
legend would otherwise draw the struck transcript as certified (round 1, integrity judge).

## The deck's work, in order

- **Art preflight.** The first review of the cover, frame 5 and the close said revise: the cover
  climbed to nothing and the close read as a striped floor. Both were recomposed, the chassis's
  granite texture was rewritten as a wrapped, jointed stone, and the review accepted. It was rebound
  and rechecked after each later change to those three frames, five reviews in all.
- **Pixel review, three rounds.** Round 1 returned revise on all nine frames, round 2 on five,
  round 3 on two (frames 3 and 8). Frame 8's navy void was fixed after round 3 by taking the sky's
  environment off the room. The flow critic said revise in round 1 and ship in round 2.
- **Panel round 1, hard fail.** "The court has not ruled" rested on an October 6th report. The
  repair read the court's own record: the orders pronounced on October 9th list no order in
  25-0463 (c30), and the 2026 orders index lists no later orders date when read on October 15th
  (c31). The cover, the close, the caption, the web edition and tx-2026-0127 now carry that dated
  statement. Slide 2 stopped placing the deposition itself in Montgomery County, and the caption's
  Bland line took the source's "assurance of a human being standing behind".
- **Panel round 2 work order.** Frame 3's camera turned toward the reader, frame 9 named the case
  in its kicker and seated its book on one tread, frame 1 took the sourced strike as its dek,
  frame 7 attributed its count, frame 4's camera came lower.

## The record, first

- **Re-verify.** The diff confirmed 111 items unchanged with each note re-worded by hand, and a hand
  check read 49 more, PDFs through `fetch_doc.py` (commit fef8866). The Texas A&M System's VISION
  documentation now reads general availability with access by application, so tx-2026-0119's claims
  and summary are corrected. Three items whose windows passed moved from open to pending,
  tx-2026-0186 among them. Every crawl boundary was re-measured and still holds.
- **Admitted.** tx-2026-0215, Rice University's October 13th initiative to hire 75 AI faculty
  (commit 782ec09).
- **Updated.** tx-2026-0127 carries the October 6th argument, Rule 203.6, and from Phase 15 the
  October 9th orders claim (tx-2026-0127-c10) in place of an undated "has not ruled".
- **For a maintainer.** A scout read on docs.tacc.utexas.edu, outside the boundary, that the TACC
  Frontera queues close on October 15th. tx-2026-0125 says October 1st. Not used and not changed.

## Sources that behaved differently from the registry

Appended to `knowledge/shared/SOURCES_FIELD_LOG.md` under October 15th: www.txcourts.gov's orders
pages and PDFs answered 200 inside the boundary; search.txcourts.gov stays disallowed, so the case
page was carried from September 7th and the first comment says so.

## Instruments

All exit 0 in Phase 7. No instrument stopped.

## Engine defects named in two rounds or more (round rule)

- **Frame 3's camcorder** (every judge, every panel round). Recomposed twice: the camera moved to
  the right edge with dark legs, then turned three-quarter to the reader. It still reads as a
  primitive; queued as `courtroom-models-built-in-chassis`.
- **Frame 7's bench** (both flow rounds, every panel round). A nine seat dais needs an 86 degree
  lens from its centre of curvature to hold all nine, which the frame's count requires. The
  lectern moved twice; queued as `hearing-bench-too-wide-for-portrait`.
- **Frames 3 and 8, the room in a navy void** (pixel rounds 1 to 3). The snapshot stages by default;
  cured by an unstaged snapshot and a near zero environment on the room. Queued as
  `snapshot-stages-interiors-to-sky-hue`.
- **The plates behind furniture** (frame 4's counter and frame 7's source line, panel rounds 1 to 3).
  Frame 7's was removed by moving the lectern. Frame 4's counter fails contrast without it at 2.4,
  so it stays at 0.6 and the judges named it.
- **Frame 2's transcript** sits on the deposition table and reads only as an edge from the frame's
  eye height. Accepted and named here.

## Phase 16 notes

- After the panel, claim texts c11, c16, c18, c23, c25 and c27 were split at a clause for the
  30 word backstop, and c11's paraphrase replaced a straight-quoted "we" that the style gate reads
  as first person. The quotes are unchanged. c28 and c29's quotes were widened to the rule's full
  sentences from the fetched rules text, and c31's to a longer run of the index page, so the
  verbatim and claims gates can find them. No judge saw these edits and none changes a fact.
- Frame 6's rule text was split into its two sentences as two elements so the word ban could read
  all of it, and the frame was re-rendered and re-shipped.
- The web edition's three sentences over 30 words were split. `tests/article_edition.mjs` needed
  `npm install` in this container, then passed 840 reader checks.
- At wake `guards_local.py --only Ownership` ran over 30 minutes and was killed; the ownership
  self-test was run on its own and exited 0.

## Did this run stop and wait for a human

Interim reading, Phase 17: 1,580 calls measured, none waited on a human. The no-stall hook was
armed at 05:09:12 UTC, judged the session unattended, and refused nothing. Phase 19 takes the
reading that counts.

## The weekly machine pass

Due today: two queue items reached repeat 2 with this run's evidence
(`kit-person-head-reads-as-mannequin`, `footer-veil-peaks-below-the-line`). The pass ran in this run
before the merge (the seventh weekly pass, `config/carousel/machine_pass.json`, commit 3266633).
Two changes, each with a verify script that exits 0 on the change and was rerun by the run: the kit
gains `pro_camcorder` and `bound_transcript` at the judges' named fixes for this deck's top ranked
artwork defect, under new names so the shipped chassis is untouched, and the footer row wash is now
documented in `TECHNIQUE_LIBRARY.md` with a check that goes red on the copied bottom veil. The kit
person's mannequin look was deferred a second time with a measured A/B. Two engine changes are
written up for a maintainer in `UPGRADE_BACKLOG.md` 2026-10-15 item 4: `TXT.snapshot` fogging an
interior room to the sky's hue, and a horizon veil behind type.

## Queued for the next pass

Four new items in `knowledge/carousel/MACHINE_QUEUE.md`: `courtroom-models-built-in-chassis`,
`snapshot-stages-interiors-to-sky-hue`, `chassis-texture-stretched-on-long-box` and
`hearing-bench-too-wide-for-portrait`. Repeats raised on `kit-person-head-reads-as-mannequin`,
`footer-veil-peaks-below-the-line` and `lastlight-horizon-warm-band-behind-type`.

## Craft memory

Added `date-every-status-to-a-document-read-today` and `snapshot-a-room-unstaged`. Confirmed
`a-paraphrase-can-outrun-its-quote`, `acceptance-items-need-a-floor` and
`the-records-own-prose-drifts-while-you-draw`.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 31 verified claim(s) |
| render         | WARN   | 9 slide(s), 4 overflow warning(s) |
| qa             | WARN   | 0 fail(s), 9 warn(s) |
| aggregates     | PASS   | 6 declaration(s), 7 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 8.75 MB, vector |
| score          | WARN   | 7.258 at the round cap after 3 round(s), the finished deck ships; 8.0 top rung, shortfall named |
| labels         | PASS   | 70 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 85 published string(s) read from one list, every universal names its set |
| verbatim       | PASS   | 3 declared fragment(s) over 9 of 9 dossier(s), every one a literal substring of its own claim's quote |
| dossiers       | PASS   | 37,098 chars planned |
| caption        | PASS   | 139 words |
| craft floor    | PASS   | 9 frame(s), median 1091, floor 196 |
| plan vs render | WARN   | 11 of 45 acceptance item(s) checkable |
| texan          | WARN   | places Montgomery County / body NO / deadline yes / next step NO |
| absences       | PASS   | 16 of 16 scoped to a named document |
| numerals       | PASS   | 9 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
