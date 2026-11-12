# Run record, November 12th, 2026 (carousel no. 75)

**Shipped at the round cap, 7.426 (panel median, `score.json`), under round 1's 8.0 bar by 0.574 and the round 2 rung of 7.7 by 0.274. No hard fail in any round. The artwork median, 6.8, is under the 8.5 craft floor, which stands down at the cap.**

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
| aggregates     | PASS   | 16 declaration(s), 25 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 8.18 MB, vector |
| score          | WARN   | 7.426 at the round cap after 3 round(s), the finished deck ships; 8.0 top rung, shortfall named |
| labels         | PASS   | 74 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 86 published string(s) read from one list, every universal names its set |
| verbatim       | WARN   | no dossier declares a `verbatim:` block, so no on-frame string was held to a quote, 1 slot note(s) |
| dossiers       | PASS   | 32,212 chars planned |
| caption        | PASS   | 139 words |
| craft floor    | PASS   | 9 frame(s), median 791, floor 142 |
| plan vs render | WARN   | 0 of 65 acceptance item(s) checkable |
| texan          | WARN   | places Dallas, Houston, Laredo / body yes / deadline yes / next step NO |
| absences       | WARN   | 4 of 6 scoped to a named document, 2 unscoped |
| numerals       | PASS   | 31 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->

## Panel

Three rounds of three fresh judges (integrity, craft, reader), combined by `panel.py`.

| round | judges | median | rung | verdict |
|---|---|---|---|---|
| 1 | 7.00, 7.28, 7.20 | 7.25 | 8.0 | keep editing |
| 2 | 7.24, 7.55, 7.39 | 7.386 | 7.7 | keep editing |
| 3 | 7.28, 7.362, 7.40 | 7.426 | cap | ships, shortfall named |

Every judge in every round ranked the same frames weakest, 8 then 5, 3, 6 and 4. **The round rule's recompositions,
said here as the routine asks.** Frame 8 (the seated observer read as asleep beside an empty wheel) was recomposed
three ways in round 2 (lean the figure back about the hip, a camera behind the seats, a camera over the driver's
shoulder) and each hid or lost the figure, so the frame shipped at its first camera with the copy put in attribution
("Two releases say a person sits up front") and Kodiak's Permian line (c68) added. The defect is the engine's: the kit
person's only seated pose bakes a bowed head. Frame 5 (the rule as a grey-middle slab) was rebuilt as a narrower,
brighter bar with a taller stop and a recessed gold channel and was still charged grey in round 3; the stair-stepped
stop-block cast is the relief height field's. Frame 4 was recomposed from the empty end of the row in round 1 and
still read as a car in front of full rows to the round 2 and 3 judges. Frame 3's labels were moved twice and its pool
once. Integrity notes left past the cap (not hard fails): slide 8's "its Permian Basin trucks" against c68's
"customer-owned trucks", slide 6 omitting the department's Chapter 552 answer (c52), and the cover setting the
authorization rule beside a report count that never says authorized.

**Copy fixes made for the gates, and why.** aggregate_check detects only a number followed by a plural noun, and
numeral_trace wanted declarations for 74, 825 and the 100 threshold, which aggregate_check then refused as stale. Slide
2's dek now reads "That 74 percent leaves 825 vehicles to the other 15 companies" and slide 3's "fewer than 100
vehicles each". Queued as aggregate-and-numeral-trace-disagree-on-bare-figures.


## Timing

Measured by `studio_clock.py` from wake (05:04 UTC): record done at 11 minutes, audition at 51, all nine frames at 141,
review done at 211, panel done at 299, package done at 329.

## Package

`ship_images.py` encoded eight frames to WebP at 40.0 to 43.8 dB and kept slide 9 as PNG, because its WebP measured
38.8 dB at quality 96, under the 40.0 floor. The art review is bound to the delivered images (`art_preflight.py
--archive`), `measurements.json` was written from the shipped frames, and `computed.json` carries `figures.json` so the
site authorises the deck's own arithmetic on its article page. The site rebuilt at 1002 pages. docket_build, site_fresh,
house_style, schema, port_audit, media, seo and schema_contract exited 0. Two claim texts (c31, c36) were split for the
article page's 30 word backstop. `tests/article_edition.mjs` could not import Playwright as an ES module in this
checkout and is left to CI.

## Retro

**Did the run wait on a human.** `prompt_audit.py` (interim, Phase 17) measured 1547 tool calls and flagged 48 with a
permission decision of 1.0 to 19.4 seconds, the longest on Agent spawns, every one resolved with nobody answering. The
no-stall hook was armed at 05:03:59 UTC, judged the session unattended (the host's `CLAUDE_CODE_SESSION_ATTENDED` was 0)
and refused nothing. Everything after this reading can still prompt.

**Instincts.** Confirmed read-the-repair-at-feed-scale, a-paraphrase-can-outrun-its-quote and the-plan-is-not-the-product.
Added kit-sit-read-bakes-a-bowed-head and computed-figures-need-a-detectable-phrase.

**Queue.** Raised kit-person-reads-as-mannequin-within-two-metres to repeat 6 and relief-plate-reads-as-a-tray to repeat
4, and added kit-person-no-upright-seated-pose, fleet-lot-models-built-in-chassis, crossover-paint-turns-blue-under-dusk-sky
and aggregate-and-numeral-trace-disagree-on-bare-figures. The two raised counts made the weekly pass due today.

**The weekly pass** (one upgrade engineer, `prompts/machine_weekly.md`) shipped two changes under the `upgrade` stamp: a
`sit_drive` pose with `headPitch` and `hands` options and the cab's rim points (opt in, frame 8 re-renders pixel identical),
and aggregate_check judging a declared phrase a surface prints. Every verify command it returned was rerun here and
exited 0. Two proposals for a maintainer are in UPGRADE_BACKLOG (a GATE_LESSONS entry, and the relief height field's
stair-stepped cast in txbench.js).

**After the pass.** `shipped_check` found the topics ledger's angle narrating spelled counts it could not trace; the
angle was reworded, and the first comment's sources block was cut to the claim ids the deck prints.
