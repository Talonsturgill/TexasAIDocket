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

WRITTEN AT PHASE 15.
