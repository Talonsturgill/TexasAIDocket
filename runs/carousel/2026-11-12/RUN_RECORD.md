# Run record, November 12th, 2026 (carousel no. 75)

**RESULT LINE WRITTEN AT PHASE 15.**

Run date note. The schedule fired at 23:04 on November 11th Chicago time (05:04 UTC November 12th). The routine names the
America/Chicago date, and every prior run has taken the UTC date at fire time, so this edition is named 2026-11-12 like the
runs before it. The 2026-11-11 edition had already shipped as no. 74.

## The record, first

- **Wake.** Branch `claude/daily-2026-11-12`, cut from `origin/main` at 2e4ec968. Git identity and `core.hooksPath .githooks` set before the first write. `$CLAUDE_EFFORT` read `high`. No `prompts/NEXT_RUN.md`. `docket_build.py --validate` and `ownership_check.py --self-test` exited 0 at wake. The local Ownership guard step (`guards_local.py --fast --only Ownership`) hung and was stopped by its 300 second timeout, as it did on November 11th. The pre-commit hook judged every commit in lane.
- **Worklist.** `docket_staleness.py` listed 61 due items. `reverify.py --apply` read 139 urls behind 430 claims: 15 answered 304, 58 sent a body, 13 did not answer and 53 were refused by the crawl boundary, so it stamped 1 item and returned 20 moved quotes (the PUCT calendar feed on tx-2026-0024 and the two PubMed pages behind tx-2026-0150 and tx-2026-0151) and 243 unconfirmed. A second pass fetched one primary source per remaining item and stamped the 28 whose primary quote was still on its page, each with a re-worded movement note that states only what the source confirmed (`reverify.py --check-notes` exits 0). 22 items had no source answer and 7 rested on journalism only; those keep their earlier stamps.
- **Moved.** tx-2026-0188 (the state authorization for commercial driverless vehicles) gained the department's Company and Vehicle Summary Report, data as of October 29th: 17 companies and 3,164 automated vehicles, Waymo 1,259 and Tesla Robotaxi 1,080 (c10 to c14 on the item). tx-2026-0062 (Fort Worth's moratorium) gained the city's own page: the first public hearing scheduled for the November 10th council meeting, adoption no sooner than February 2027 and by a supermajority, 19 commission recommendations.
- **Admitted.** None. Fort Worth's hearing was already tx-2026-0062 and the TxDMV report was already tx-2026-0188, so both went in as movements.
- **Not confirmed.** tx-2026-0024's calendar quotes rolled off the PUCT feed, and the PubMed pages still answer with a cookie wall. Neither was re-stamped.

## Instruments

Phase 7, logged in `out/2026-11-12/tmp/phase7.log`. `gridwatch_pagecheck.py` exited 2 on one advisory: **November 1st is missing from the Grid Watch series, and ERCOT can't backfill it.** The collector and ledger are cron's, so nothing here was changed. The water page check and self-test, media, schema, og, favicon, truetype, indexnow and seo all exited 0. The scratch `site_build.py` into `out/` hit its 15 minute timeout (exit 124); Phase 16's rebuild into `docs/` is the build of record.

## Craft refresh

Focus: close-range surface realism on spatial scenes. No. 74's judges named "pale primitive boxes", "reads as a diagram" and "untextured" lath, and the last three decks all leaned on txthree spatial scenes.
- Uniform roughness is the commonest CG giveaway. Break it with faint low-contrast noise, since high contrast reads as dirt or wet rather than a made finish. https://novedge.com/blogs/design-news/cinema-4d-tip-cinema-4d-polished-material-look-development
- A small bevel gives a highlight somewhere to sit, so a box edge reads as a made edge rather than a primitive. https://www.tripo3d.ai/blog/explore/photorealistic-3d-product-rendering
- Edge wear is a convex-edge mask multiplied by noise so it lands heavier in some places and not at all in others. Pure curvature wear is too even, and heavy weathering is the exception. https://www.strayspark.studio/learn/tutorials/procedural-edge-wear-blender
- Noise that modulates roughness after the roughnessmap chunk through onBeforeCompile, projected in model space so UV-less primitives take it with no stretching. https://discourse.threejs.org/t/wrap-texture-around-object-without-stretching-with-meshstandardmaterial/56948
- Flat even light is what makes a scene sterile. Put dark regions next to bright reflections so a shiny object reads as solid. https://www.willgibbons.com/realistic-rendering/

## Selection, and what shipped

**Story.** tx-2026-0188, the TxDMV's Company and Vehicle Summary Report for Senate Bill 2807 authorizations, data as of
October 29th. `dedupe_check.py` exited 0 against the last 30 days (no. 59's Waymo airport curb and no. 66's Aurora letter
were the nearest, and neither shares the roster). The deck carries one visual argument, the whole roster parked at one
stand-in car per ten listed vehicles (`compute.py`, rounded half up and never fewer than one), and follows it from the
cover's front row to the census from above, the fifteen-company column, its last car, the rule's no-fee plate, Dallas's
request, the department's line, the freight cab and the fence at the tail.

**Art.** One chassis, `assets/js/deck/2026-11-12-roster.js`, declares the `roster` world (lastLight, key at azimuth -55
and elevation 10, one grade, accent dusk_gold #E0956A). It carries two kit models built for this deck, `wheel_stop` and
`fleet_lot` (the packed three-column lot from FIG.units, instanced crossovers, stall bars, wheel stops, white company
dividers and the gold lane). Eight frames are spatial txthree scenes and frame 5 is a TXBENCH material relief.

**Audition.** Cover, frame 2 (hardest) and close were reviewed by the art director before the remaining six. Frame 9 was
sent back twice, first for the gold lane filling the foreground as a slab, then for the lane reading as self-lit tape.
The chassis repair made the lane lit, shadow-receiving worn paint with its hue in the albedo and a self light that holds
the accent in shade, and the third review accepted all three, bound to the current source, chassis and images
(`art_preflight.py` exit 0).

**Pixel passes.** Two rounds, five critics then three. Round 1 drove the near-car scale on 1 and 4, the census framing on 2,
the label column and visible dividers on 3, a full-height relief plate on 5, a darker ground and a seated skyline on 6,
the road markings on 7 and the camera off the lane on 9. Round 2 drove the leaders and the column on 3 (the camera now
looks down the column so the rows stack in rank order), the stripe tip and label on 2, ribs kept off the type field on 5.

**Flow pass.** One flow critic. Its craft block named 8, 5, 3, 6 and 4 weakest. Repairs made: frame 4 recomposed from
the empty end of the row looking back to the one car with the roster behind it (it also cleared panel_ready's ground
check); frame 5's stop block raised to 150 px relief and the weekly graduations cut deeper than the daily ones; frame 3's
pool moved onto Avride's rows. **Not made, and why.** Frame 8's bowed head: the kit person's only seated pose
(`sit_read`) bakes a 0.42 rad head pitch into its geometry, so no pivot can be raised from a frame, and leaning the whole
figure back hides it behind the seat from this camera. That is an engine defect, carried to the backlog in Phase 17.
The flow critic's reorder (frame 8 after frame 5) would renumber four frames and void the accepted audition bindings on
the close, so it was not taken this run.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 68 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 3 warn(s) |
| aggregates     | FAIL   | 4 problem(s) |
| assembly       | PASS   | 9 slide(s), 8.16 MB, vector |
| score          | ABSENT | score.json not written yet |
| labels         | ABSENT | label_report.json not written yet. Run scripts/carousel/label_guard.py <run-dir> |
| quantifiers    | ABSENT | quantifier_report.json not written yet. Run scripts/carousel/quantifier_check.py <run-dir> |
| verbatim       | ABSENT | verbatim_report.json not written yet. Run scripts/carousel/verbatim_check.py --date <date> |
| dossiers       | PASS   | 32,099 chars planned |
| caption        | PASS   | 139 words |
| craft floor    | PASS   | 9 frame(s), median 806, floor 145 |
| plan vs render | WARN   | 0 of 65 acceptance item(s) checkable |
| texan          | WARN   | places Dallas, Houston, Laredo / body yes / deadline yes / next step NO |
| absences       | WARN   | 4 of 6 scoped to a named document, 2 unscoped |
| numerals       | PASS   | 29 numeral(s) over 9 frame(s), every one reachable |
| completion     | ABSENT | not scored yet |
<!-- gate-status:end -->
