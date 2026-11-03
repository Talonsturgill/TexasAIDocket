# Run record, November 2nd, 2026

Effort at wake: `high`, as the repo's settings carry it.

**THE GRID WATCH'S LARGE LOAD QUEUE READING IS STILL STOPPED, and CI fails on it.** `gridwatch_pagecheck.py` exits 3
again, read at wake and again at ship: the newest verified queue month is 2026-08, three months back, and the newest
verified daily reading is 2026-10-31. The queue cause is the one the November 1st run named, a filename. ERCOT publishes
the Monthly Operational Overview with no year in the name and `queue_collect.py` builds the name with `-2026`. The
collector is cron lane and this run may fix nothing in it. The fix is one more candidate filename in `report_url`. The
owner was notified by push at wake.

**Wake.** Branch `claude/daily-2026-11-02`, cut from `main` with PR 455's unmerged commits merged in, because November
1st's deck never landed for the same CI red. Git identity and `core.hooksPath .githooks` were set before the first write.
No `prompts/NEXT_RUN.md` was queued. `arsenal.py --check` asked for a regenerated `ARSENAL.md`, committed in the upgrade
lane (fcd0b65b). The run also fixed the one red step on `main` that was in its own lane: the grid page's monthly queue
chart ran 42px past a 320px screen and now scrolls inside its own box (`scripts/site/theme.py`, in af8a9eaa).

## Craft refresh

Focus: the hardest frame of the plan, a believable dog built procedurally in the kit's SDF body, at feed size and at
native size. The refresh's working notes did not survive a context compaction and are not reconstructed here. What the
build itself learned is in the artwork ledger entry and under "Retro" below.

## The record, first

- **Re-verify, commit 66be1fb5.** 10 items confirmed against their primary pages, 3 stamped as checked and unchanged,
  11 carry a dated unconfirmed line. Four claims the checker can't read (two Killeen agenda PDFs, a Community Impact quote
  and a League City Legistar quote it has never found) claim nothing either way.
- **Admitted tx-2026-0236** (af8a9eaa), San Antonio's automated survey of unrestrained dogs, on the SwRI release and the
  City of San Antonio release of October 20th. **Held** tx-2026-0237 (Pflugerville's SAFE policy) and tx-2026-0238 (San
  Antonio's data center vote) at medium confidence until a primary record is fetched.
- **Corrected during the panel.** The integrity judges read the record as well as the deck. tx-2026-0236's history line
  said "Field research is under way", which no claim carries, and now says it is expected to run through December 2026
  (c20). Its summary said the stray or owned "call rests on appearance", which goes past the release, and now says the
  release describes strays as appearing malnourished and skittish, in the release's tense. Its key date is still kind
  `effective` for an announcement, because `DATE_KINDS` has no `announced`; that is a schema question for a maintainer.
- The Federal Register poll failed at discovery and the scouts' sweep was folded in instead.
- `docket_build.py --validate` exits 0.

## Selection

tx-2026-0236. Southwest Research Institute and San Antonio Animal Care Services will repeat the city's 2019 manual
survey of unrestrained dogs in the same 32 study areas, with a phone on a vehicle window paired with object detection
software and automated and human review of the clips. Field research is expected through December 2026, then SwRI
forwards a final report to the department. The city says the sample is not meant to count every unrestrained dog. Two
primary sources and the ACS statistics page. The 2019 study PDF was too large for the fetcher, so no 2019 finding is in
the claims and slide 7 says so.

## The deck

Carousel no. 66, sightline. Five spatial scenes on one staged lastLight west side block at night (frames 1 to 4 and 9),
one dark room lit by its screen (5), and three TXBENCH material reliefs (6 to 8), one chassis,
`assets/js/deck/2026-11-02-sightline.js`, with two new chassis models, `street_dog` (an SDF body with fur normals, lean
and full builds, three poses, five coats) and `window_phone`. The visual argument follows one tan dog through the
survey: boxed in four gold corners through the car window, on the phone's screen, inside four labelled corners, split
as stray and roaming, on a reviewer's screen beside four unticked checks, then the record's half (32 caliche plugs on a
clay city plan, the 2019 mould beside the 2026 cast with a 7 division rule, a field block over October to December with
the report past it), and the dog watching the survey car leave. Dusk gold means the machine's detection.

**The audition took nine readings** across the run. The art director accepted 1, 4 and 9 at the fourth reading, then
every pixel round, the flow pass and both repair rounds changed at least one of them, and a changed image needs a new
review. The binding in `art_preflight.json` is the ninth reading (frame 9; frame 1 from the eighth, frame 4 from the
seventh).

**Pixel review, two rounds on all nine frames, then rechecks on every changed frame.** The holdout after the cap was
frame 3, and it was recomposed in the last repair round: the car cropped out, the long sight lines removed, the dog drawn
over the corner marks.

**The flow critic** estimated artwork at 6.5 and named 5, 9 and 3 as the weakest frames. All three were repaired (5 lit
only from its screen with a keyboard, 9 recomposed at 6.5 m with a side key, 3 given a lens bead and then recomposed).
Its not_done list (9 echoing 8, 6 and 7 as two grids, type in the top 40 percent on all nine) is in `flow_craft.json`.

**The planned value arc was rewritten to the measured one** after the render (median L* planned near 14, measured 3.7).
`panel_ready` asked for one or the other; the frames were already in the dark register the rubric asks for.

## The panel

| round | integrity | craft | reader | median | rung |
|---|---|---|---|---|---|
| 1 | 6.36 | 7.04 | 6.49 | 6.546 | 8.0 |
| 2 | 7.006 | 7.13 | 6.91 | 6.936 | 7.7 |
| 3 | 7.01 | 7.046 | 6.66 | 6.868 | cap |

**It ships at the round cap at 6.868, 1.132 under the 8.0 top rung, with no hard fail in any round.** Round 1's
integrity judge moved the most: the release's future tense flattened to present fact, "car" for "vehicle", the checks
given to software alone, and a machine-first order on frame 5. All were fixed. Round 3 named one more punctuation point
that was not fixed, because past the cap only a hard fail may be repaired: frame 5 closes the c4 quote with the stop
inside the marks where the source sentence continues.

**Named in all three rounds and never fixed:** the SDF dog reads as a smooth figurine at native size (club paws, an even
coat), frame 5's monitor and keyboard are primitives, frames 6 and 7 read as two grids of squares back to back, and the
close lands softly. Recomposition was tried on 3 and 9 and held. The dog and the monitor are the engine's, and go to the
machine queue below.

## Ship

Artifacts in `runs/carousel/2026-11-02/`, `ship_images.py` at 40.0 to 41.2 dB against the 40.0 floor, the review bound
to the delivered images, `measurements.json` written and checked. Web edition `ledger/articles/2026-11-02.json`, checked
by `article_check` and the browser suite (1065 reader checks). Site rebuilt on top of `main`; `docket_build --validate`,
`site_fresh_check`, `house_style_check`, `schema_check`, `port_audit`, `media_check`, `seo_check` and `schema_contract`
all exit 0.

**This run does not merge if CI is red on `gridwatch_pagecheck`**, which it was on `main` at ship. See the top.

## Timing

Minutes from wake: record 34.9, audition 98.3, art 105.7, review 160.2, panel 209.2, package 230.4.

## Permissions

`prompt_audit.py` (interim reading, Phase 17) measured 1,716 calls and listed 39 that waited, the longest 30.9 s on a
SendMessage and 19.5 s on an Agent launch, all resolved without anybody present. The no-stall hook was armed at
05:03:24Z, judged the session unattended from the start (`CLAUDE_CODE_SESSION_ATTENDED=0` from the host), and refused
nothing. The Phase 19 reading is the one that counts.

One hook asked for commits authored as Claude with a Claude address. CLAUDE.md forbids that and the repo's own hooks and
CI refuse it, so commits stayed in the owner's identity.

## Retro

- **A camera space occluder built for one fov is wrong at another.** Frame 1's window seal kept the old fov after the
  frame's fov changed, and its bevel ran through the type column for a pixel round.
- **A line drawn in front of the subject strikes it.** Frame 3's sight lines crossed the dog for three rounds; drawing
  the dog last fixed the crossing, and the lines were then cut because they started from nothing.
- **A frontal key flattens a body seen from behind.** Frame 9's dog read as felt until the frontal key fell to a third
  and a low side key raked the flank.
- **A screen inside a render is a second render**, and its box has to be sized to that render's aspect or it falls off
  the screen.
- **Copy at the panel is where integrity is won.** The tense and attribution fixes moved claim integrity on the judge
  that charged them from 5.5 to 8.0 between rounds 1 and 2.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 54 verified claim(s) |
| render         | WARN   | 9 slide(s), 4 overflow warning(s) |
| qa             | WARN   | 0 fail(s), 9 warn(s) |
| aggregates     | PASS   | 7 declaration(s), 8 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 9.22 MB, vector |
| score          | WARN   | 6.868 at the round cap after 3 round(s), the finished deck ships; 8.0 top rung, shortfall named |
| labels         | PASS   | 58 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 86 published string(s) read from one list, every universal names its set |
| verbatim       | PASS   | 6 declared fragment(s) over 9 of 9 dossier(s), every one a literal substring of its own claim's quote |
| dossiers       | PASS   | 33,507 chars planned |
| caption        | PASS   | 151 words |
| craft floor    | PASS   | 9 frame(s), median 896, floor 161 |
| plan vs render | WARN   | 9 of 59 acceptance item(s) checkable |
| texan          | WARN   | places San Antonio / body yes / deadline NO / next step NO |
| absences       | PASS   | 4 of 4 scoped to a named document |
| numerals       | PASS   | 9 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
