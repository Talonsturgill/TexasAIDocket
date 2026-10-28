# Run record, October 28th, 2026

Effort at wake: `high`, as the repo's settings carry it.

**Wake.** Branch `claude/daily-2026-10-28`. Git identity and `core.hooksPath .githooks` were set before the first
write. The October 27th run had committed its record work to `claude/daily-2026-10-27` (re-verify, 125 items
confirmed, admit tx-2026-0233) and never merged it, so this run merged that branch first (5d1499aa) to carry it to
`main`. A Phase 0 background command (branch, clock and ownership check) reached its background time limit and was
stopped; its steps were rerun in the foreground and passed.

## The record, first

- **Re-verify.** `reverify.py` stamped 9 items confirmed and 53 dated unconfirmed lines (commit 7b8ed31f). Two items
  went to the staleness hard list and were re-pointed rather than routed around:
  - tx-2026-0203. The Taylor newsflash item 2113 now answers 404, so claims c1 to c18 moved to the city's Taylor
    Technology Campus project page, with the four quotes that changed recorded in the item's history.
  - tx-2026-0028. KUT disallows this project in robots.txt, so claim c2 moved to Community Impact's report of the
    resolution, and the summary sentence that only KUT carried was removed.
- **Admitted.** None. The scouts' leads went to selection and the record.
- **Instrument check (Phase 7).** The Grid Watch and Water Watch page checks, the site self-tests and the schema check
  ran. The schema check named three stale citations on item pages, the two re-pointed items and tx-2026-0179's govtech
  link, all resolved by this run's rebuild. No presentation change was needed.
- **Craft refresh.** Reduced to no searches this run, stated in `run_state.json`.
- **Sources.** Five findings were appended to `knowledge/shared/SOURCES_FIELD_LOG.md`: the dallascityhall.com briefing
  PDFs read cleanly, Taylor's newsflash 404 and the project page, KUT's robots refusal, a PMC reCAPTCHA page, and
  nbcdfw.com refusing while fox4news.com read.

## Selection

tx-2026-0179. Dallas runs City Detect computer vision cameras on 50 Sanitation brush trucks. The city's October 19th
briefing to the Quality of Life, Arts, and Culture Committee says an observation is not a confirmed violation, staff
review every one, and the first courtesy letter now sets no deadline. Its results table counts six rows and it
publishes no accuracy figure. Carousel no. 31 covered the program on September 21st, 37 days back and outside the
30 day window, and every judge named the repeat under variety.

## The deck

Carousel no. 62, "Cameras ride 50 brush trucks". Nine spatial scenes in the staged lastLight world. The chassis
`assets/js/deck/2026-10-28-route.js` builds the brush truck, camera pod, brush pile, cut limb, limb rack, count token
and notice letter, because the kit has none of them. That is queued. The accent is the camera's cyan `#7CC6D6`, on
the coated lenses, the review queue's title strip, the tape on the 5,318 limb and the blank accuracy tag.

**Frame 5 changed representation.** A txbench curb relief failed the art director twice as flat bars on a tray, and the
six counts became barked limbs on a galvanized rack in a city yard. Building it found that `K.make` centres a model's
footprint, which moved every limb's butt by half its length, fixed with `userData.keepOrigin`. Both are queued.

**Audition.** Six art director rounds on frames 1, 5 and 9 (`reviews/art-director.md`). The binding is current and
the shipped encodes are bound to it (`art_preflight.py --archive`).

**Pixel and flow.** Two pixel rounds and one recheck (`reviews/pixel_round1.md`), one flow pass (`reviews/flow.md`).
The flow critic's swap of frames 7 and 8 put the accuracy turn second to last. Two notes in the pixel record went stale
after later repairs and are corrected here: frame 4's tiles were set to one value with a dark gutter at round 2 on the
craft judge's round 1 ask, so the "three value steps" line describes an earlier state, and frame 8's label was moved
again after its recheck.

## The panel

| round | judges | median | spread | verdict |
|---|---|---|---|---|
| 1 | 6.86, 7.23, 6.756 | 6.896 | 0.474 | keep editing, under the 8.0 rung |
| 2 | 6.90, 7.10, 6.94 | 6.992 | 0.2 | keep editing, under the 7.7 rung |
| 3 | 6.862, 7.37, 7.08 | 7.086 | 0.508 | ship at the round cap |

No judge found a hard fail in any round. **The deck ships at 7.086, 0.914 under the 8.0 top rung**, and the art median
of 6.8 is under the 8.5 craft floor, which stands down at the cap. Contested in round 3: claim_integrity and variety.

Repairs between rounds, in the work order's order. Round 1 to 2: frame 2 restaged on its near rows, frame 4 darkened
with a seated panel, frame 8 recomposed on the bare arm, frame 3 relit with an iris on the lens, frame 6 pushed in with
the letter in the door, frame 1 re-attributed and its piercing limbs culled, frame 5's second upright cleared, frame 9
naming the committee, the caption attributing the letter. Round 2 to 3: frame 4 recomposed as a smaller pool on a
dark desk, frame 3's loader cylinder taken matte so its sky reflection stopped reading as a cut-out, frame 6 given an
open mail door and a key on the letter, frame 2 and 3's hooks attributed to the plan and the city, the caption's review
sentence attributed.

**Named and not repaired, because past the cap only a hard fail is repaired:**
- Frame 8's accuracy label clamps at the left margin and its last letters graze the upright.
- Frame 6's headline states the city's own description of its letter; the dek attributes it.
- Frame 1 keeps a few leaf cards from the culled limbs floating at native size.
- Frame 4 is the deck's mid-tone outlier and has no reviewer in frame.
- No surface gives a resident a next date or a route, because none was fetched.

## Ship

Run folder `runs/carousel/2026-10-28/`, shipped encodes at 40.1 to 41.6 dB against the 40.0 floor, `og.jpg` from
slide 1, `measurements.json` written and checked. Web edition `ledger/articles/2026-10-28.json`, `article_check` and
the browser test clean. Variety ledgers updated. The site rebuilt (948 pages) and the Phase 16 suite exited 0 on every
step.

## Timing

Elapsed minutes from wake, from `studio_clock.json`: record 26.8, audition 124.9, art 151.2, review 179.3, panel
232.4, package 248.2.

## Retro

- **Permission waits.** `prompt_audit.py` measured 1,641 calls and counted 183 with a permission decision delay, the
  longest 24.9 s on agent spawns and the Bash calls under 5 s. The no-stall hook was armed at 05:04 UTC, judged the
  session unattended with the host's `CLAUDE_CODE_SESSION_ATTENDED=0`, and refused nothing. No call waited on a person.
- **What cost the run.** Frame 5's two failed reliefs and the origin debugging, and three art director rebinds caused
  by chassis edits that frame 5 did not use. Both are in the machine queue with repeats counted.
- **Instincts.** Two added (`a-count-is-stock-racked-in-a-place`, `check-the-origin-before-the-camera`), two confirmed
  (`recompose-a-frame-named-twice-in-round-one`, `stand-back-from-a-kit-figure`).

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 51 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 3 warn(s) |
| aggregates     | PASS   | 12 declaration(s), 16 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 8.2 MB, vector |
| score          | WARN   | 7.086 at the round cap after 3 round(s), the finished deck ships; 8.0 top rung, shortfall named |
| labels         | ABSENT | label_report.json not written yet. Run scripts/carousel/label_guard.py <run-dir> |
| quantifiers    | ABSENT | quantifier_report.json not written yet. Run scripts/carousel/quantifier_check.py <run-dir> |
| verbatim       | WARN   | no dossier declares a `verbatim:` block, so no on-frame string was held to a quote |
| dossiers       | PASS   | 35,640 chars planned |
| caption        | PASS   | 135 words |
| craft floor    | PASS   | 9 frame(s), median 794, floor 143 |
| plan vs render | PASS   | 9 of 56 acceptance item(s) checkable |
| texan          | WARN   | places Dallas / body NO / deadline yes / next step NO |
| absences       | WARN   | 2 of 10 scoped to a named document, 8 unscoped |
| numerals       | PASS   | 20 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
