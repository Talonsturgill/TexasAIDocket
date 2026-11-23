# Run record, November 20th, 2026 (carousel no. 83)

**Shipped at the round cap, 7.474 (panel median, `score.json`), 0.53 under round 1's 8.0 bar. No judge found a hard fail in any round. The art median, 7.6, is under the 8.5 craft floor, which stands down at the cap.** Round 3 judges scored 7.474 (integrity), 7.51 (craft) and 7.462 (reader).

**Effort note.** `run_state.json` recorded `$CLAUDE_EFFORT` as `medium` at wake, the seventh run in a row. `.claude/settings.json` carries `effortLevel: high`, and nothing in this repository can change what the host passes.

**The run finished on November 21st (UTC).** It is dated by its branch and its run directory, as every run is.

## The record, first

- **Wake.** Branch `claude/daily-2026-11-20`. Git identity and `core.hooksPath .githooks` set before the first write.
- **Re-verification**, commits 3f3cf85a and 5e697cee. The pass stamped the unchanged items. PDF and PUCT sources were read by hand through `fetch_doc.py`. Thirty eight automatic movement notes were reworded for the house style check.
- **Boundaries.** Twenty three boundaries whose seven day clock had lapsed were re-measured with the project user agent and refused again, and each note carries "Re-measured 2026-11-20 ... Nothing was routed around." Eight earlier boundaries (tx-2026-0044, 0062, 0125, 0161, 0166, 0173, 0186, 0227) now answer or allow robots, so they were left to lapse on their own clock rather than re-stamped.
- **Admission**, commits 3f3cf85a and a4066a30. tx-2026-0253, East Texas A&M's GPS spoofing study in Commerce, Hunt County, research, 14 claims from the university's November 16th release. Commit f4b40368 extended c3's quote to the release's own "In a study accepted for presentation at WATCH 2026" sentence after the round 2 integrity judge found the claim text said more than its quote. It verifies 14 of 14.
- **Grid and water pages.** `pagecheck` exited 2 on the November 1st missing day, which is cron's and advisory. Nothing was touched.

## Selection, and what shipped

**Story.** tx-2026-0253. East Texas A&M researchers tested whether AI can spot false location in a drone's flight records from its own motion sensors, with no GPS readings. A public dataset of 96 recorded flights, 42 normal and 54 spoofed, with 22 whole flights held back for testing. Eight models compared. Given 10 consecutive readings, a pretrained model called Chronos scored 97.5 percent on a measure that balances catches against correct alerts. The first author is an undergraduate. The study evaluated recorded flights, and running the check in flight is a next step.

**Integrity limits, stated on the frames.** The ridge and valley are the release's own hypothetical and every frame that draws them says so. The 97.5 is one score on one measure for one model and never a share of attacks caught. The paper and the dataset were not opened, so the dataset's name and the other seven models stay off the deck. No face is drawn for any team member.

**Art.** The seventh BESPOKE + LOOK V2 run, people tone, spine `assets/js/deck/2026-11-20-truetrack-bespoke.js` with chassis models `survey_quad` (ghost, open and folded modes) and `flight_board`. Accent #ff9f1c means only motion the drone itself measured. The reported position is always frosted periwinkle glass that casts no shadow.

## Deviations, stated

- **The rework rounds took the critics' and judges' fixes rather than second concepts**, except frame 9, which the art director sent to a different representation, and frame 4, below.
- **Frame 4 changed representation twice after round 1.** Seated kit people were charged as mannequins, so the artist cropped them to hands, and those read as cartoon fists. The showrunner then removed every person: four open laptops set at the table, asserted against FIG.team_ug + FIG.team_grad, with nobody drawn. The dek dropped "The people are drawn to illustrate." and copy.json and the storyboard were synced.
- **Copy changes after round 1.** The cover went to present tense ("Sent to the ridge. It flies to the next valley.") and frame 4's headline became "An undergraduate is first author", both on the integrity judge's reading of c18 and c22 to c23. After round 2, frame 9's dek dropped the workshop sentence (and c3 from its claim line) and closes on c13's forward question.
- **Frame 8 lost its score bar in round 3.** Two judges read the bar filled almost to its stop as a share of something, against the dek's own "not a share". The trough was cut and the score pill sits on the loupe's rim. FIG.readings is still drawn and asserted.
- **Dossiers reconciled at ship.** `ship_images` refused frame 6 as a GRID that holds as one piece at thumb scale and frame 8 at a 0.25 detail rect. Frame 6 is DIAGRAM, which is what it is, a tablet of tracks with an enlarged pair. Frame 8's rect was drawn around the loupe at [100, 600, 980, 1040] with no bleed. No pixel changed.
- **Two web edition rendering faults fixed at ship, words only.** `{{number:c11:1}}` already carries its percent sign, so "scored {{number:c11:1}}%" printed "97.5%%". The extended c3 quote put a comma after 2026 that the numeral token swallowed, so "WATCH {{number:c3}}," printed "2026,,". Both passed `article_check` and were caught by reading the rendered page.
- **Frame 2's ground.** `panel_ready`'s middle ground patch sits on the sweep's horizon, where mipmapping smooths the tooth. The fix enlarged the texel scale and switched the brushed streak, which every judge charged as scanlines, to a fine isotropic grain. It measures 4.56 against the 4.0 floor.
- **Ship-time source fixes from `shipped_check`, after round 3.** Frame 6's "enlarged" pill carried an opaque inline plate, so it now takes the deck's translucent `.lab.plain` pill and machine QA has no fail on it. Frames 1, 2, 4 and 5 carried "FIG must be empty" assertions that made `fig_inject` treat them as dynamic readers, so those throw lines were removed, and frame 4 reads its two figures by name. Frames 1, 2, 4 and 5 re-rendered byte identical. Frame 1's source change took a sixth art director reading of the unchanged image. The topics ledger prose dropped count words the run did not compute ("eight", "four", "three", "ten"). The panel scored frame 6 with the opaque pill.
- **`tests/article_edition.mjs` did not run here.** It imports `playwright` as an ES module and the container's global install resolves only through `require`. CI runs it.

## The three-frame review

On a bespoke run the review is bound through slide critics at 8.0 or through `carousel-art-director`. Frame 3, the hardest, stayed bound from the art director's third reading. After round 1's repairs a cold critic scored frame 1 at 7.1 on the image that shipped and frame 9 at 6.8. Frame 9 took the critic's two fixes (open shell, a cartridge lifted onto the mat, grass moved off the accent). The art director then accepted both on its fourth reading, frame 9 again on a fifth after its dek changed, and frame 1 on a sixth after a source line was removed at ship. The critic rows are in `slide_critics.json`, each with a note on whether its image shipped.

## Panel

- **Round 1**, 7.228 (7.18, 7.36, 7.316), no hard fail, under the 8.0 rung. Repairs to frames 4, 8, 6, 9, 7 and 2 and copy on the cover and frame 4.
- **Round 2**, 7.338 (7.316, 7.53, 7.322), no hard fail, under the 7.7 rung. Repairs to frames 4, 6, 7 and 8 by their artists, frame 2's grain, frame 9's dek and c3's quote by the showrunner.
- **Round 3**, 7.474 at the cap. Ships.

**Named shortfall.** All three round 3 judges named frame 4 first. The shell-off drone reads as loose parts, with arms and the GPS mast apart from the tub and an arm crossing a laptop lid. Frame 7's top third is flat magenta and frames 7 and 8 sit in a hotter studio than the rest. Frame 8's lower third is empty. Frame 9's oak canopies speckle. Frame 6 keeps a faint wash edge and a bright sliver in its recess. Frame 5's "which way" pill sits 52 px from the edge. The stake is the release's hypothetical ridge, no Texas operator is named, and "drawn to illustrate" appears on five frames.

**Images.** Five of nine frames ship as PNG because the LOOK V2 grain encodes under the 40 dB WebP floor.

The web edition at `ledger/articles/2026-11-20.json` passes `article_check` and `tests/test_article_edition.py`.

## Retro

- **Weekly machine pass not due** (last pass November 18th, no repeat offender). No machine change in this run.
- **Queued** five new machine defects and raised two repeats: `depth-floor-blind-to-chassis-helpers`, `article-number-token-swallows-trailing-comma`, `kit-people-cartoon-at-table-range`, `survey-quad-open-reads-exploded`, `sweep-horizon-fails-ground-floor`, and `layout-cli-passes-what-ship-refuses` and `bespoke-brief-stale-after-panel-repair` to repeat 1.
- **Instincts.** Confirmed `read-the-repair-at-feed-scale`, `a-paraphrase-can-outrun-its-quote`, `read-the-rendered-token` and `the-plan-is-not-the-product`, added `show-people-by-their-places`.
- **Sources field log**, commit 70142466, records the East Texas A&M, WATCH programme and arXiv reads and the boundary re-measurements.
- **Arsenal** rebuilt and current.

## Prompt audit

`prompt_audit.py` measured 1,925 tool calls and reports 62 with a permission decision wait over its threshold, the longest 33.6 s, on `SendMessage`, `Agent` and `Bash` calls. The no-stall hook was armed at 05:03:21 UTC, judged the session unattended at start (the host's `CLAUDE_CODE_SESSION_ATTENDED` was 0) and refused nothing. Every measured wait ended within 34 s with nobody at a keyboard, so none stopped the run. **This reading is interim.** It was taken before the merge, the Gmail draft and the social delivery.

## Timing

`studio_clock.py --report`, minutes from wake. record 31.9, audition 57.7, art 81.0, review 174.4, panel 244.8, package 267.2. The two frame 4 recompositions and four extra art director readings sit inside the review and panel spans.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 26 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 2 warn(s) |
| aggregates     | PASS   | 11 declaration(s), 14 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 8.7 MB, vector |
| score          | STALE  | score.json predates the newest render, so it describes a deck that no longer exists. Re-run it |
| labels         | PASS   | 50 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 81 published string(s) read from one list, every universal names its set |
| verbatim       | WARN   | no dossier declares a `verbatim:` block, so no on-frame string was held to a quote |
| dossiers       | PASS   | 30,522 chars planned |
| caption        | PASS   | 141 words |
| craft floor    | PASS   | 9 frame(s), median 1324, floor 238 |
| plan vs render | WARN   | 0 of 61 acceptance item(s) checkable |
| texan          | WARN   | places NONE / body NO / deadline NO / next step NO |
| absences       | WARN   | 0 of 15 scoped to a named document, 15 unscoped |
| numerals       | PASS   | 11 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
