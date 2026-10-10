# Run record, October 10th, 2026

Effort at wake: `high` (as the repo's settings carry it). The no-stall hook logged `armed` at
06:15:15 UTC and judged the session unattended from SessionStart, with the host's
`CLAUDE_CODE_SESSION_ATTENDED=0`. It refused nothing. The interim reading in Phase 17 measured 1,576
tool calls and none waited on a human. **That reading is interim.** Phase 19 takes the one that
counts, and the email carries it.

## DISPOSITION: SHIPPED AT THE ROUND CAP, 7.29, 0.71 UNDER THE 8.0 TOP RUNG, NO HARD FAIL IN ANY ROUND

Carousel no. 48, "Austin Community College is writing its AI policy", is nine frames rendered in
one staged lastLight world, a campus lawn at last light (key azimuth -77.7, elevation 6.4, both
computed from the sun's position in `compute.py`), declared once in
`assets/js/deck/2026-10-10-lastlawn.js`. The hero is the kit student desk with its laptop lit and a
blank sheet on its top, on all nine frames. The walk is the calendar: one limestone paver per day
from the October 9th post to the October 22nd seminar, fourteen in all, with granite (#9A3B2A) on
the three event days. The motif changes state across the deck: the desk at the start of the walk on
1, labelled with the five TRUST rules on 2, one of 79 on 3, the titled PDF on its lid on 4, in use
on 5, on the town hall paver on 6, shut with a paperback at the walk's end on 7, in the corner of
the town hall room on 8, and empty on the town hall paver on 9.

The story is tx-2026-0212, admitted today. Austin Community College says it is developing what it
calls its first-ever AI policy under a five rule framework. Its own AI Resource Hub already links a
PDF titled Acceptable Use of Artificial Intelligence Policy, marked for faculty and staff only. The
post names no adoption date, no vote and no adopting body. The deck sets the two documents side by
side and closes on who is invited.

The panel: round 1, 7.12 under the 8.0 rung; round 2, 7.242 under the 7.7 rung; round 3, 7.29 at
the cap, judges 7.04, 7.24 and 7.32. No judge found a hard fail in any round. The art median is 6.5
and the craft floor stood down at the cap. The round 3 judges named frames 8, 5, 3, 9, 6, 4 and 7
for the art.

## The deck's work, in order

1. **Selection.** `runs/carousel/2026-10-10/SELECTION.md`. `dedupe_check` cleared at 0.25.
2. **Directors and storyboard.** All three directors chose the kit `student_desk` on their own.
   Nobody checked that against the artwork ledger, and no. 38 on September 30th had built its deck
   on the same desk, alone on a field and then counted as a field of desks. Two judges scored
   variety 4.5 and 5.5 for it. That is the craft lesson added below.
3. **The three-frame audition.** Accepted after one revise. It was re-bound and re-reviewed four
   more times, because every later repair to frames 1, 3 or 9 makes the accepted review stale, and
   the gate is right to refuse it. The second `--write` without `--middle` bound slide 4 as the
   evidence frame where the first had bound slide 3; that is queued.
4. **Pixel rounds, three, and flow rounds, two.** Round 1 sent all nine back. The repairs that held:
   frame 1's desk turned so the chair's open frame faces the camera; frame 2's hook names TRUST and
   its labels moved clear of the leaders; frame 4 restaged on the putty top; frame 6's labels moved
   to the open lawn; frame 7 rebuilt as the planned close on the shut lid and the paperback; frame
   9's copy rewritten from a recap of dates into the invitation. Cameras on 5, 7 and 9 are chosen by
   code that pitches until the lid or the head clears the dek band.
5. **Tried and reverted.** Frame 3 with the block's lids dark (the pixel critics asked, to end the
   far-screen moire) measured one piece and then two against the GRID floor of four, so the lids
   stayed lit low. Wider spacing and a hero-only pool were worse. Frame 9 over a walker's shoulder put
   the head under the hook from every position that kept the desk large. Frame 5 from the right
   shoulder put the head behind the kicker.
6. **Panel round 1, 7.12.** The work order named 5, 8, 4, 9, 3 and 6. Frame 5 lost the head above
   the shoulder and moved to the left shoulder so the field is the dark sky rather than the warm
   horizon. Frame 8's window was drawn as a window with mullions and a warm band. Frame 4 lost the
   sheet that read as a white bar. The c19 quote was re-read on the hub page and now carries its
   access label, and c16 was added to the first comment.
7. **Panel round 2, 7.242.** Frames 4, 5, 8 and 9 had been named two rounds running, so they were
   recomposed rather than re-rendered, per the round rule. Frame 4: the camera back with a darker
   desk top so the page is the light. Frame 5: the person's cloth set to dark cotton. Frame 8: the
   audience set to silhouettes. Frame 9: **the walker removed**, the desk turned side-on on the town
   hall paver with its seat empty, layout OBJECT_AND_CAPTION. Frame 4's dek, the caption, the record
   entry and the web edition now say "a PDF titled ... marked for faculty and staff only", because
   two judges read "a faculty and staff document" as the document's audience when the source marks
   access.
8. **Panel round 3, 7.29, the cap.** No hard fail. What the judges still charge, and what ships:
   the kit figures on 5 and 8 still read as mannequins at full size; frame 3's far lids still alias;
   the pavers read as boards and the granite as flat paint on 1, 6, 7 and 9; frame 6 shows 13
   pavers inside the frame against a headline of fourteen, the first cropped at the bottom; frame
   9's walk reads as stacked slabs behind the desk. The integrity judge also named the caption's
   closing question as presupposing that the unread PDF is a separate adopted policy. Past the cap
   only a hard fail may be repaired, so it stands and is named here.

9. **After the cap, at Phase 16.** `shipped_check` measured frame 3 on the shipped WebP and found 3
   pieces against the GRID floor of 4, where the lossless render had measured 4 or 5. The frame is
   unchanged. Its dossier now declares OBJECT_AND_CAPTION, which is what the weekly pass's
   escalation of the GRID count prescribes until the count is read from the scene. The topic ledger
   entry dropped count words the run never computed.

## The record, first

- **Worklist.** `docket_staleness.py` named 33 items due of 183. `reverify.py` asked 65 urls behind
  270 claims: 12 answered 304, 19 sent a body, 9 did not answer and 25 were refused by the crawl
  boundary and never requested. FAA's 403 to this project's agent left 152 claims undecided by
  their own source. The rest were read one source at a time through `reverify.Boundary` and
  `fetch_doc.py`, and the stamps are in commit 87ab3cf1. tx-2026-0186 (Zipline, comment window
  closing October 11th) was stamped today.
- **A helper fault, disclosed.** The first hand-check helper checked `crawl_boundary.forbidden`
  and Python's robotparser with `*` only, so it requested public.destinyhosted.com and kbtx.com
  pages that items carry measured robots blocks for. Those results were discarded and nothing was
  stamped on them. The helper was rewritten on `reverify.Boundary`.
- **A scout brief fault.** The what-texas-makes scout brief named gov.texas.gov, which the registry
  puts off limits to WebFetch. Two scouts fetched pages there. Nothing from that host reached a
  claims file. The next run's brief must not name it.
- **Admitted.** tx-2026-0212, Austin Community College's AI policy. `promote` held it twice, once
  for the comma rate and once for a missing history line, and both were fixed in the entry. Its id
  was renumbered from 0211, which yesterday's withdrawn item had used. At Phase 16
  `house_style_check` found a 33 word sentence in its summary, which was split and reworded to the
  source's access label.
- **Dropped.** c26, from Spectrum News, whose robots.txt disallows the fetcher.

## Sources that behaved differently from the registry

Appended to `knowledge/shared/SOURCES_FIELD_LOG.md` under October 10th: FAA's 403 to this project's
agent, dhs.gov's 403, the PUCT RSS bare host redirect, tech.utexas.edu's 403, ACC's three hosts
answering, and Spectrum News's disallow.

## Instruments

All eleven exit 0 in Phase 7. No instrument stopped.

## Did this run stop and wait for a human

No, on the interim reading. 1,576 calls measured, none waited on a human. 353 waited on the auto
mode classifier, the longest 4.8 seconds. The hook refused nothing.

## The weekly machine pass

**Due and run.** `machine_due.py` found one repeat offender, the GRID piece count, which this run
raised to repeat 2. The upgrade engineer worked in its own worktree and its four commits were merged
into this branch before the pull request. Every verify command it returned was re-run here and
exits 0: `week_digest.py --self-test`, `arsenal.py --check`, `print_ban.py --assets` and
`examples/kit/sizes.py`.

- `week_digest.py` reads the judges' ranked list under the key the scorer writes. The ranked
  artwork section had been empty for all five weekly passes because it read a key the judges
  stopped writing on October 3rd.
- `workstation_cart`, no. 47's hero, is a kit model at the judges' named fix: a moulded monitor
  back with vents, a VESA mount, a cable run and a cool rim of light.
- Escalated for a maintainer: the GRID piece count (three pixel fixes tried, each loosened or
  broke the gate; the proposal counts units from the engine's scene), and `tests/article_edition.mjs`
  still writing its screenshots to September 18th's folder. Both in `UPGRADE_BACKLOG.md` under
  2026-10-10.

## Queued for the next pass

Four new items in `knowledge/carousel/MACHINE_QUEUE.md`: `campus-models-built-in-chassis`
(paver_walk, policy_sheet, paperback, wall_clock), `kit-person-head-reads-as-mannequin`,
`lit-accent-drifts-in-lab` and `art-preflight-middle-default`.
`grid-piece-count-reads-lit-ground-as-subject` was raised to repeat 2. The article browser test
wrote to September 18th's folder again; the run screenshotted today's edition at 390 and 1440 with
its own script and read both.

## Craft memory

Confirmed `read-the-repair-at-feed-scale` (three recompositions read at feed size and reverted),
`a-paraphrase-can-outrun-its-quote` (c19's "posted for faculty and staff" against an access label),
`the-records-own-prose-drifts-while-you-draw` (a 33 word summary sentence found at Phase 16) and
`acceptance-items-need-a-floor` (the critics found several acceptance lists a bare frame would pass).
Added `check-the-hero-against-the-artwork-ledger`.

## Things this run did not do

- The flow critic's reorder of slide 5 to slot 3. It would have broken the bound three-frame review
  and every counter, and slide 5 carries the rule's full text where slide 2 carries only its name.
- Any change to the caption's closing question after round 3, which is past the cap.
- Any request for the faculty and staff PDF.
- Any rewrite of a shipped run.

## Discoverability signoff

- Card, opened as an image: `og/tx-2026-0212.png`. It wraps on word breaks and ends on "a five"
  with an ellipsis.
- `/questions/`: tx-2026-0212 appears once on each of the eleven question pages, including who
  decides and taking part.
- `llms.txt`, Open right now: tx-2026-0212 leads the list, with Zipline (closes October 11th), the
  CFTC window, the NTIA survey, League City's November 3rd election and the PUCT calendar.
- `/sources/`: 1079 of 1232 claims rest on a primary document, across 331 documents from 143
  publishers. Today's admission rests on three primary ACC pages.
- `/topic/`: Health and education carries tx-2026-0212.
- `/place/`: Travis County and the Austin-Round Rock-San Marcos metro both carry tx-2026-0212.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 30 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | PASS   | 9 slide(s), zero fails, zero warns |
| aggregates     | PASS   | 7 declaration(s), 8 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 8.47 MB, vector |
| score          | WARN   | 7.29 at the round cap after 3 round(s), the finished deck ships; 8.0 top rung, shortfall named |
| labels         | PASS   | 52 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 84 published string(s) read from one list, every universal names its set |
| verbatim       | PASS   | 12 declared fragment(s) over 9 of 9 dossier(s), every one a literal substring of its own claim's quote |
| dossiers       | PASS   | 35,167 chars planned |
| caption        | PASS   | 140 words |
| craft floor    | PASS   | 9 frame(s), median 1250, floor 225 |
| plan vs render | WARN   | 0 of 53 acceptance item(s) checkable |
| texan          | WARN   | places Austin / body NO / deadline yes / next step NO |
| absences       | WARN   | 0 of 4 scoped to a named document, 4 unscoped |
| numerals       | PASS   | 4 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
