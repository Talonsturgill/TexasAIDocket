# Run record, November 14th, 2026 (carousel no. 77)

**Shipped at the round cap, 7.10 (panel median, `score.json`), under round 1's 8.0 bar by 0.90 and the round 2 rung of 7.7 by 0.60. Round 1 found one hard fail (slide 6 called January's $12 million "exact", which no claim supports) and it was repaired. Rounds 2 and 3 found none. The artwork median, 6.5, is under the 8.5 craft floor, which stands down at the cap.**

**Effort note.** `run_state.json` recorded `$CLAUDE_EFFORT` as `medium` at wake. `.claude/settings.json` carries `effortLevel: high`, and the runs before this one read `high`, so this run reasoned a level lower than the setting asks. Nothing in this repository can change what the host passes. It is stated here so the next run can compare.

## The record, first

- **Wake.** Branch `claude/daily-2026-11-14`. Git identity and `core.hooksPath .githooks` set before the first write. No `prompts/NEXT_RUN.md`.
- **Re-verification.** One pass over the docket's sources, committed as e3679eb8 with `ledger/reverify.json`. Movement notes were regenerated where a source changed. Item 0055's structured v1 note no longer matched its checked date and was regenerated from the fetched hashes. Item 0189's auto note was reworded to clear the comma rate. Items 0133 and 0165 were unblocked after their boundary re-measurements. Item 0044 still carries a stale v1 block, left for a maintainer because its source did not answer cleanly.
- **Moved.** PUCT filing counts: tx-2026-0003 gained claim c22 ("5865 filing(s).") and tx-2026-0076 gained claim c20 ("534 filing(s)."), both counted by code off the docket pages.
- **Admitted.** tx-2026-0247. The Texas Semiconductor Innovation Fund gave Texas Tech's engineering college an award of over $19 million for an AI computing cluster in Lubbock, announced November 13th. Decider is the Texas CHIPS Office in the Office of the Governor. County Lubbock, on ERCOT.
- **Corrected during the panel.** Two claims on tx-2026-0247 were tightened to what their quotes say. c16 now reads "will match" (the source says "The university will match"), not "matched". c9 now says Roland Faller "is on the research team" (the quote is "Along with Faller, the research team consists of"), not that he leads it. Both edits are in `ledger/docket.json`, `seed/docket_seed.json` and the archived claims.
- **Lubbock and ERCOT.** An editor note drafted during admission said Lubbock is outside ERCOT. Lubbock Power and Light joined ERCOT in 2021, so the item carries `on_ercot: true` and the sentence was removed before commit.

## Instruments

Phase 7, logged under `out/2026-11-14/tmp/p7_*.log`. `gridwatch_pagecheck.py` exited 2 on one advisory: **November 1st is still missing from the Grid Watch series, and ERCOT can't backfill it.** The collector and ledger are cron's, so nothing here was changed. The temporary `site_build.py` probe into `out/2026-11-14/tmp/site` hit the 124 timeout of the probe wrapper and is not a build failure; the real rebuild in Phase 16 ran without a timeout. The water page check and self-test, media, schema, og, favicon, truetype, indexnow and seo checks all exited 0.

Field notes for the fetch layer, carried into Phase 17: the reverify user agent got 406 from news.rice.edu; PMC and PubMed now serve a reCAPTCHA page to automated fetches; the UNT hosts answered again; the Angelina County PDF that failed earlier in the week now answers.

## Selection, and what shipped

**Story.** tx-2026-0247, Texas Tech's TSIF award for a computing cluster in Lubbock, with the fund's January clean room award and its May bandgap research award from the same university's own announcements. `dedupe_check.py` exited 0. Two judges noted the story shape sits close to no. 65 (a university facility with no opening date) and the subject near no. 73 (research computing). No topic repeats inside 30 days.

**The drawing unit.** One wafer for every $1 million, declared in `figures.json` as a drawing unit with no source claim. Nineteen wafers for the November floor, twelve for January, twelve beside twelve for the match, four and a cleaved half for May. No total of the three awards is printed or drawn, because one figure is a floor and one is approximate.

**Art.** One chassis, `assets/js/deck/2026-11-14-waferbench.js`, declares the `waferbench` world (floodlit, key at azimuth -58 and elevation 28, accent dusk_gold #E0956A meaning the November award) with three chassis models, `wafer`, `wafer_boat` and `lab_bench`, and `labEnv`, a reflection environment of light strips for mirror silicon. Five frames are spatial txthree scenes on one black epoxy bench (1, 3, 4, 5, 8) and four are TXBENCH reliefs (2, 6, 7, 9).

**Audition.** Cover, frame 6 and the close were reviewed by the art director before the other six were built and again after every change to any of them. Frame 6 began as three boats in perspective and became a plan view tray, because only a plan view shows a capped end, a cleaved half and an open end at one scale.

**Pixel passes.** Two rounds across all nine frames, the second over the eight frames the first round changed. Round 1 found the copy faults the judges would later have charged: the match tense, a comma-fenced hedge on 6, a comma splice on 8, and a figure on 8 whose hair crossed the dek.

**Flow pass.** One flow critic, predicted artwork 6.6. Its craft block named 8, 7, 2, 5 and 6 weakest. Repairs made: frame 8's figure darkened to a silhouette, frame 7's steps raised and its island pulled into frame, frame 2 re-projected so Lubbock County spans 434 px, frame 6's tray set to its planned near black with dusk_gold rims on November's discs, frame 3 re-shot from above so it stops repeating the cover. Tried and reverted: a camera swing on frame 5, which hid the cleaved half. Not made: the hard seam under the type band on the four reliefs.

## Panel

Three rounds of three judges, combined by `panel.py`.

| round | integrity | craft | reader | median | rung | result |
|---|---|---|---|---|---|---|
| 1 | 6.73 | 7.40 | 6.91 | 7.12 | 8.0 | one hard fail, keep editing |
| 2 | 7.20 | 7.00 | 6.79 | 6.98 | 7.7 | keep editing |
| 3 | 7.00 | 7.30 | 7.13 | 7.10 | cap | ships, shortfall named |

**Round 1 repairs.** The hard fail: "January was $12 million exactly" and the label "January, exact" became "a stated $12 million" and "January, stated". Claim c9 corrected as above. Frame 8 lost the kit person and became the boat on the desk; frame 7 grew from one sheet to two sheets with islands ahead of their fronts; frame 2's label moved onto the county face in black ink; frame 6's tray moved to the type margin so its labels clear the safe zone.

**Round 2 repairs.** Frames 7 and 8 were named in both rounds, so both were recomposed rather than re-rendered. Frame 7's terraces and growth now sit inside one wafer's disc on the bench. Frame 8 is one wafer cut into a grid of dies; a server rack was refused because the plan keeps racks out of this deck after no. 73. Frame 9's IN SERVICE recess carries nineteen empty wafer pockets, so the close holds the November count in its geometry. Copy: slide 8 now attributes the cluster definition to the university, and slide 5 and the caption no longer tie "harsh environments" to the May award, which c17 does not say.

**Round 3, what the judges still charge.** Artwork 6.5 median. All three name the flat black type band and hard seam over the reliefs on 2, 6, 7 and 9, slide 2 as a tile rather than a place, and slide 9 as a type panel. Variety is contested (6.0, 7.5 and 8.0 across the three rounds' judges): the one object per counted unit move has run on most decks since late October. Claim integrity holds at 8.0 from every judge in round 3. The leans they name, not fails: "not built yet" is inferred from "will help establish", the governor's own fund listing was off limits so c18 rests on the university's restatement, and "Lubbock County" is geography from the committed county data rather than a claim.

**Holdouts named.** Frame 2's county grid reads as tiles because South Plains counties really are near-square survey blocks. Frame 1's lowest band is dark bench without visible scratches.

## Timing

`studio_clock.json` holds the checkpoints: art_done, review_done, panel_done, package_done.

## Package

Nine frames, `carousel.pdf` in vector mode, shipped as WebP at 40.2 to 44.4 dB against a 40.0 floor, `og.jpg` from slide 1. `art_preflight.json` binds the delivered encodes to the reviewed PNGs. `measurements.json` written by `measure_shipped.py`, deck median L* 5.5. Web edition `ledger/articles/2026-11-14.json`.

## Retro

Written in Phase 17 below.

## Gate status

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 19 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 5 warn(s) |
| aggregates     | PASS   | 6 declaration(s), 6 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 7.4 MB, vector |
| score          | WARN   | 7.1 at the round cap after 3 round(s), the finished deck ships; 8.0 top rung, shortfall named |
| labels         | PASS   | 52 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 84 published string(s) read from one list, every universal names its set |
| verbatim       | WARN   | no dossier declares a `verbatim:` block, so no on-frame string was held to a quote |
| dossiers       | PASS   | 30,913 chars planned |
| caption        | PASS   | 149 words |
| craft floor    | PASS   | 9 frame(s), median 463, floor 83 |
| plan vs render | WARN   | 0 of 57 acceptance item(s) checkable |
| texan          | WARN   | places Lubbock, Lubbock County / body yes / deadline yes / next step NO |
| absences       | WARN   | 0 of 10 scoped to a named document, 10 unscoped |
| numerals       | PASS   | 13 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
