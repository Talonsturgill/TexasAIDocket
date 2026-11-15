# Run record, November 15th, 2026 (carousel no. 78)

**Shipped at the round cap, 7.09 (panel median, `score.json`), under round 1's 8.0 bar by 0.91 and the round 2 rung of 7.7 by 0.61. Round 1 found one hard fail (slide 4 drew the 86 teacher-use laptops and the 29 policy folders on the same hundred desks, a cross tabulation the source never reports) and it was repaired. Rounds 2 and 3 found none. The artwork median, 6.8, is under the 8.5 craft floor, which stands down at the cap.**

**The first BESPOKE + LOOK V2 run.** `config/carousel/bespoke.json` `bespoke_from` is 2026-11-15, so every frame was conceived, built and reworked by its own `carousel-slide-artist` on one spine chassis, `assets/js/deck/2026-11-15-ruleroom-bespoke.js` (LOOK V2, people tone, accent #ff9f1c meaning a written rule), and scored by its own `carousel-slide-critic`.

**Effort note.** `run_state.json` recorded `$CLAUDE_EFFORT` as `medium` at wake. `.claude/settings.json` carries `effortLevel: high`. This is the second run in a row to read `medium`, and nothing in this repository can change what the host passes.

## The record, first

- **Wake.** Branch `claude/daily-2026-11-15`. Git identity and `core.hooksPath .githooks` set before the first write. No `prompts/NEXT_RUN.md`. PIL was broken in the fresh container and `bootstrap.sh` repaired it.
- **Re-verification.** One pass over the docket's sources, committed as c2197b75. 31 items were stamped checked on November 15th.
- **Corrected.** tx-2026-0027's claim c10 and its summary said "Zone No. 11". The fetched packet says "Zone No. 10", so both now say that.
- **Moved.** tx-2026-0062 gained c8 (the first public hearing on the moratorium was held) and c9 (the January 12, 2027 council meeting carries the second hearing and first reading), with that date as a key date.
- **Admitted.** tx-2026-0248, Texas 2036's November 10th preview of its report on AI in Texas classrooms and district policy, ten claims from texas2036.org. It was held once on a comma rate of 4.76, split into shorter sentences and promoted.
- **Held.** The Kodiak and Atlas Permian story. Neither the release nor either company's SEC filing names a county.

## Instruments

Phase 7, logged under `out/2026-11-15/tmp/p7_*.log`. `gridwatch_pagecheck.py` exited 2 on one advisory: **November 1st is still missing from the Grid Watch series, and ERCOT can't backfill it.** The collector and ledger are cron's, so nothing was changed. The `site_build.py` probe hit the probe wrapper's 124 timeout, as on November 14th. The real rebuild ran in Phase 16. The water page check and self-test, media, schema, og, favicon, truetype, indexnow and seo checks exited 0.

## Selection, and what shipped

**Story.** tx-2026-0248. Per Texas 2036, in a fall 2025 survey 86% of Texas school and district leaders reported teacher AI use and 61% reported student use, while 29% reported a district policy on student use and 20% one for staff. By its count 42 states have some form of statewide guidance and Texas does not. The voter figures are nearly 85% on student privacy and 71% on teaching responsible use, with four named priorities. No topic repeats inside 30 days. The one earlier school AI deck, no. 2 on August 18th, is far outside the window.

**The drawing unit.** One object for each leader in a hundred, declared in `figures.json` as a drawing unit. Desks on 2 and 4, lockers on 3, staff mailboxes on 5. Frame 6 draws one binder per state. Every count is computed from `window.FIG` with a throw on a mismatch.

**Art.** Nine artists, two critic rounds, then panel repairs. Final cold critic scores were 7.4, 8.0, 7.8, 7.6, 8.0, 7.2, 8.0, 6.6 and 7.4 for frames 1 to 9, before the panel repairs to 2, 5, 6 and 8 that followed.

## Panel

Three rounds of three judges, combined by `panel.py`.

| round | integrity | craft | reader | median | rung | result |
|---|---|---|---|---|---|---|
| 1 | 6.73 | 7.33 | 7.30 | 7.26 | 8.0 | one hard fail, keep editing |
| 2 | 7.23 | 7.33 | 7.24 | 7.25 | 7.7 | keep editing |
| 3 | 6.87 | 7.27 | 7.13 | 7.09 | cap | ships, shortfall named |

**Round 1 repairs.** The hard fail: frame 4's laptops all went dark and identical, only the 29 amber folders count, and the headline became "A student AI policy, reported by 29%". Frames 2, 6 and 8 were recomposed (a custodian for scale, window light and the Texas pill at the shelf's gap, parents at the covered walk).

**Round 2 repairs, and what was reverted.** Frame 5 lost its white memo slips, so only the 20 amber sheets remain. Frame 8 was rebuilt under the covered walk with the parents at true scale, the bus a pale secondary and every raster letter gone. Its headline seat was deepened to clear panel_ready's 4.5 contrast floor. **Frames 4 and 9 were rebuilt and then restored to their round 2 pixels.** Frame 4's rebuild drew all hundred desks inside the frame with no laptops. Four cold critic readings scored it 5.4 to 7.0 and every one judged its main subject unfinished, which art_preflight refuses on the bound evidence frame. Frame 9's rebuild scored 5.8 against the round 2 frame's 7.4. Both shipped frames are byte identical to the reviewed renders. A further frame 8 pass reached a better picture that failed QA's strike-through check on one row under the dek, so the r3a composition shipped.

**Round 3, what the judges still charge.** Artwork 6.5, 6.8 and 7.0. All three name frame 4 (a wall in the top half, the grid cropped, dark laptops), frame 8 (sky banding behind the headline, flat pale trousers) and frame 9 (wavy kit wood, the orange room near the accent). Frame 6 shows about 14 of its 42 binders. Story is 6.5 from every judge: nobody decided anything, no deciding body or date is named, and the caption asks which laws without the deck naming them.

**A contradiction between judges, named.** Round 1's integrity judge failed frame 4 for drawing slide 2's lit laptops beside the folders. Round 3's integrity judge charged the dark laptops as contradicting slide 2's own legend. Both are recorded. Neither round 3 judge called it a hard fail.

**Ambiguity left in the copy.** Slide 9's dek says Texas "is not among its 42 states", where "its" is Texas 2036. The cornice struck the dek when the line was reworded, so the original stands.

## Timing

`studio_clock.json` holds the checkpoints: wake, record_done, audition_done, art_done, review_done, panel_done, package_done. Measured minutes from wake: record 26.06, audition 42.97, art 66.95, review 116.28, panel 210.49, package 234.25.

## Package

Nine frames, `carousel.pdf` in vector mode, `og.jpg` from slide 1. **Seven frames shipped as PNG.** Frames 2 to 7 and 9 measured 31.7 to 39.7 dB at WebP quality 96 against the 40.0 floor, so `ship_images.py` shipped the PNGs, about 45 MB. Slides 1 and 8 shipped as WebP at 40.5 and 41.5 dB. `art_preflight.json` binds the delivered images to the reviewed renders. `measurements.json` was written by `measure_shipped.py`, deck median L* 30.5. Web edition `ledger/articles/2026-11-15.json`.

**A machine fix made in the run.** `ship_images.py` refused the reviewed originals on layout rules that `layout_check` only reports on a bespoke run, so the first bespoke run could not ship. The fix, under the upgrade lane, takes the originals' findings as the baseline and charges only a finding the encode adds.

## Retro

- **Did this run stop for a human.** `prompt_audit.py`, the interim Phase 17 reading, measured 1,919 calls and listed 69 over its threshold, led by Agent and SendMessage spawns at 1 to 36 s. The no-stall hook was armed at 05:03:20 UTC, judged the session unattended from its start (`CLAUDE_CODE_SESSION_ATTENDED=0`, the host's value too) and refused nothing. These waits are the agent-latency pattern queued as `prompt-audit-counts-agent-latency`, now at repeat 10. **This reading is interim.** Phase 19 takes the one that counts.
- **Queued** in `knowledge/carousel/MACHINE_QUEUE.md`: ruleroom models built in the chassis, counted grids that can't both fill the frame and stay countable, briefs left stale after a panel repair, art_preflight with no bespoke route, the kit school bus paint near an amber accent, LOOK V2 grain defeating the WebP floor, and the ship_images fix as shipped. Raised: `prompt-audit-counts-agent-latency` and `kit-person-reads-as-mannequin-within-two-metres`.
- **Instincts.** Confirmed `read-the-repair-at-feed-scale`. Added `integrity-repair-rewrites-brief` and `decide-the-legend-once`.
- **Weekly pass.** Not due. The last pass ran November 13th.
- **Sources.** Appended to `knowledge/shared/SOURCES_FIELD_LOG.md`.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 16 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 7 warn(s) |
| aggregates     | PASS   | 2 declaration(s), 6 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 8.86 MB, vector |
| score          | WARN   | 7.086 at the round cap after 3 round(s), the finished deck ships; 8.0 top rung, shortfall named |
| labels         | PASS   | 38 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 79 published string(s) read from one list, every universal names its set |
| verbatim       | WARN   | no dossier declares a `verbatim:` block, so no on-frame string was held to a quote |
| dossiers       | PASS   | 33,653 chars planned |
| caption        | PASS   | 140 words |
| craft floor    | PASS   | 9 frame(s), median 1691, floor 304 |
| plan vs render | WARN   | 0 of 63 acceptance item(s) checkable |
| texan          | WARN   | places NONE / body NO / deadline yes / next step NO |
| absences       | WARN   | 0 of 6 scoped to a named document, 6 unscoped |
| numerals       | PASS   | 20 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
