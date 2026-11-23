# Run record, November 19th, 2026 (carousel no. 82)

**Shipped at the round cap, 7.47 (panel median, `score.json`), 0.53 under round 1's 8.0 bar. No judge's hard fail survived any round. The art median, 7.2, is under the 8.5 craft floor, which stands down at the cap.** Round 3 judges scored 7.54 (integrity), 7.378 (craft) and 7.47 (reader).

**Effort note.** `run_state.json` recorded `$CLAUDE_EFFORT` as `medium` at wake, the sixth run in a row. `.claude/settings.json` carries `effortLevel: high`, and nothing in this repository can change what the host passes.

**The run finished on November 20th (UTC).** It is dated by its branch and its run directory, as every run is.

## The record, first

- **Wake.** Branch `claude/daily-2026-11-19`. Git identity and `core.hooksPath .githooks` set before the first write.
- **Re-verification**, commits 856729c3 and 2b5743f7. 309 URLs behind 1,294 claims were asked, and 116 items were stamped unchanged. The moved claims were PUCT Interchange list pages and the PUCT rolling calendar, which page older entries away, and they stay unstamped rather than reading absence as a change. Thirty two automatic movement notes were reworded at the house style check, and tx-2026-0024 carries a calendar note.
- **Admission**, commit ac296d26. tx-2026-0252, UT Arlington's $3.1 million USDA funded project for an AI smart trap against New World screwworm, statewide, research and science, decided, 15 claims from UT Arlington's November 12th news release.
- **Grid and water pages.** The November 1st missing day is cron's and advisory. Nothing was touched.

## Selection, and what shipped

**Story.** tx-2026-0252. Screwworm, declared eliminated in 1966, is back with more than 120 confirmed animal cases as of November 12th, most in Texas. Today's traps catch insects indiscriminately and can't tell wild flies from the sterile flies a federal program releases. UT Arlington's planned trap would keep wild flies, especially the egg laying females, and free the sterile flies and other insects. Producers and veterinarians would report cases with phone photos. A prototype is expected next spring and the project runs through June 2028. Context from USDA ARS (AI models already inform the release, from Kerrville) and APHIS (the Edinburg facility, more than 80 million sterile flies a week, more than 100 screwworm traps monitored since July 2025).

**Integrity limits, stated on the frames.** The trap is unbuilt and is never drawn as a field device. Every frame says it is drawn to illustrate. The case count is UT Arlington's citation of the USDA dashboard, and the dashboard itself was not opened. No accuracy figure, field result or catch count exists, and the web edition says so.

**Art.** The sixth BESPOKE + LOOK V2 run, wonder tone, spine `assets/js/deck/2026-11-19-sortglass-bespoke.js`, accent #e0956a (dusk gold) meaning only the fly the sort keeps.

## Deviations, stated

- **The rework rounds took the critics' and judges' fixes, not second concepts**, as on November 18th.
- **The judges' re-sequence (frames 4 and 5 before 3) was declined.** The cover's question is answered by frame 3's sort, and moving today's traps ahead of it would bury the answer under the problem.
- **Dossiers reconciled with the frames at ship.** `ship_images` measured the strict layout on the reviewed originals and found rects and bleeds the frames no longer had after the round 3 rebuilds. Frame 1's rect is [400, 540, 680, 660] and bleeds right. Frame 2's reaches the bottom. Frame 3's is [380, 420, 620, 750] with no bleed, which keeps its detail floor. Frame 4 is FIGURE_SCALE rather than GRID, because the rack holds as one silhouette at thumb scale. Frame 7's rect was drawn around its grid after the camera pulled back. Frame 9's is [400, 560, 680, 790] and bleeds right and bottom. No pixel changed.
- **Ship copy fixes after round 3, words only.** The web edition's money tokens dropped "million" ("$3.1 project") and now carry it. Three web edition and two record sentences were split for the 30 word backstop and the comma ceiling. The sources block no longer lists c13, c18 and c23, which no frame or caption prints. The topics ledger angle was rewritten to describe the shipped frames without count words the run did not compute.
- **One judge's hard fail was withdrawn.** The round 3 craft judge first charged the art review as unbound to frames 1 and 9, reading superseded critic hashes as newer ones. The bound hashes equal the current renders (`sha256sum`, and `art_preflight.py` exits 0), the judge was shown that and withdrew it, and `score-craft.json` carries the note.
- **The no. 54 overlap.** October 18th told the same parasite from USDA's side. It is outside the 30 day window, and the integrity judge noted it.
- **No rancher action.** No reporting route or instruction is in the claims file, so the close is a date to watch.

## The three-frame review

On a bespoke run the review is bound through slide critics at 8.0 or through `carousel-art-director`. Frame 3 stayed bound by its round 3 slide critic. Frames 1 and 9 were rebuilt after round 2's panel. Cold critics then scored frame 1 at 7.0 and frame 9 at 5.0, so both went to the art director. It sent both back. Frame 9 was recomposed with the sort glass dominant beside a modelled phone over a spring pasture and accepted on the second reading. Frame 1 needed three more passes: a thin open rim in place of a sealed dish, the glass resting on a real sweep, the banding dithered out, and a detached shade plane removed. The fourth reading accepted all three.

## Panel

- **Round 1**, 7.016 (6.85, 6.89, 7.05), no hard fail, under the 8.0 rung. Repairs to frames 9, 8, 7, 2, 4 and 5 and copy on 2, 4 and 6 and the caption.
- **Round 2**, 7.458 (7.338, 7.456, 7.502), no hard fail, under the 7.7 rung. Five slide artists repaired frames 9, 2, 7, 1 and 5. Frame 7's camera then pulled back so all 40 boxes can be counted, and frames 1 and 9 were rebuilt as above.
- **Round 3**, 7.47 at the cap. Ships.

**Named shortfall.** All three judges named frame 5 first. Its flies still read as ants on the bucket and nothing in the picture shows the trap failing to tell sterile from wild. Frame 9's close is a still life whose phone screen reads as abstract, with repeated grass cards and a flat oak. Frame 7's boxes sit small on a flat floor. Frame 2 draws a "sterile female" cell, which c4 supports and c23's male only release strain undercuts. "Drawn to illustrate" closes every dek. The caption's "keep everything" is looser than "capture insects indiscriminately".

**Cold critics after the round 2 repairs**, recorded in `slide_critics.json` as round 4: frame 1 7.0, frame 2 7.7, frame 5 5.8, frame 7 6.9, frame 9 5.0. Frames 1, 7 and 9 changed again after that, and the final images are the ones the panel scored.

**Images.** Six of nine frames ship as PNG because the LOOK V2 grain encodes under the 40 dB WebP floor.

The web edition at `ledger/articles/2026-11-19.json` passes `article_check`, `tests/test_article_edition.py` and `tests/article_edition.mjs`.

## Retro

- **Weekly machine pass not due** (last pass November 18th, no repeat offender). No machine change in this run.
- **Queued** five new machine defects and raised one repeat: `money-token-drops-unit`, `layout-cli-passes-what-ship-refuses`, `cover-rebuild-takes-four-readings`, `slide-critics-rows-not-marked-superseded`, `v2-banding-in-seat-washes`, and `render-report-clobbered-by-parallel-renders` to repeat 1.
- **Instincts.** Confirmed `parallel-renders-clobber-one-report` and `one-accent-one-meaning-across-every-artist`, added `read-the-rendered-token` and `a-review-hash-is-a-time-not-a-truth`.
- **Sources field log**, commit 39558f03, records the UT Arlington, ARS and APHIS reads and the PUCT calendar redirects.

## Prompt audit

`prompt_audit.py` measured 2,208 tool calls and reports 138 with a permission decision wait over its threshold, the longest 32.9 s, on `SendMessage` and `Agent` calls and the rest on `Bash` calls of about a second. The no-stall hook was armed at 05:03:50 UTC, judged the session unattended at start (the host's `CLAUDE_CODE_SESSION_ATTENDED` was 0) and refused nothing. Every measured wait ended within 33 s with nobody at a keyboard, so none stopped the run.

## Timing

`studio_clock.py --report`, minutes from wake. record 26.2, audition 50.4, art 87.4, review 141.3, panel 322.8, package 375.2. The four extra art director readings and the frame 1 rebuilds sit inside the panel span.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 24 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 3 warn(s) |
| aggregates     | PASS   | 7 declaration(s), 8 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 8.48 MB, vector |
| score          | WARN   | 7.47 at the round cap after 3 round(s), the finished deck ships; 8.0 top rung, shortfall named |
| labels         | PASS   | 52 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 76 published string(s) read from one list, every universal names its set |
| verbatim       | WARN   | no dossier declares a `verbatim:` block, so no on-frame string was held to a quote |
| dossiers       | PASS   | 34,008 chars planned |
| caption        | PASS   | 134 words |
| craft floor    | PASS   | 9 frame(s), median 1908, floor 343 |
| plan vs render | WARN   | 0 of 57 acceptance item(s) checkable |
| texan          | WARN   | places Arlington, Edinburg, Kerrville / body NO / deadline yes / next step NO |
| absences       | WARN   | 0 of 4 scoped to a named document, 4 unscoped |
| numerals       | PASS   | 12 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
