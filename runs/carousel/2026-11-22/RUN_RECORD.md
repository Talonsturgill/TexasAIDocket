# Run record, November 22nd, 2026 (carousel no. 85)

@@SCORE_LINE@@

**The run finished on November 23rd (UTC).** It is dated by its branch and its run directory, as every run is.

## The record, first

- **Wake.** Branch `claude/daily-2026-11-22`, run date November 22nd (America/Chicago), woken at about 05:04 UTC on November 23rd. Git identity and `core.hooksPath .githooks` set before the first write. `docket_build.py --validate` was clean at wake. `ownership_check.py --self-test` passed.
- **Effort.** `$CLAUDE_EFFORT` read `medium` at wake, the ninth run in a row. `.claude/settings.json` carries `effortLevel: high`.
- **Wake gate.** `guards_local.py --fast --only Ownership` failed one of three steps for a container reason: the shallow clone build step imported a broken system Pillow (`/usr/lib/python3/dist-packages/PIL`, no `_imaging`) where the session's python uses `/usr/local/lib/python3.11`. Not a repository defect. The hooks are wired and every commit printed the pre-commit ownership check.
- **Social preflight.** Upload-Post profile `default` lists the Texas AI Docket Facebook page 113073681274871 and LinkedIn organization 78748279, and both pins name them. TikTok offers PUBLIC_TO_EVERYONE. The social state branch initialized and read back.
- **Worklist.** The selector named 151 items due at wake. `reverify.py --apply` stamped 116 as checked and unchanged. Seven claims of tx-2026-0024 (the PUCT calendar feed) moved because their listings rolled off the live feed, so those claims, the summary and the key dates were brought to the December and January listings with a movement line. Six more items were checked against their own pages and stamped with written notes (tx-2026-0013, 0016, 0037, 0078, 0079, 0126). tx-2026-0062 (Fort Worth's page answered 403) and tx-2026-0077 (one Senate archive claim not found on the committee page) were left unstamped at three days. Twenty six items wait behind crawl boundaries measured November 20th and 21st, still inside their seven day window, and nothing was routed around.
- **Not done.** The 116 deterministic movement lines `reverify.py` wrote were not reworded this run. They are true and dated.
- **Admitted.** tx-2026-0256 (TACC opens Horizon to early users, research-and-science, 8 claims from news.utexas.edu) and tx-2026-0257 (the Dell Med and IC² Institute AI Learning Lab, health-and-education, Travis County, 4 claims from ic2.utexas.edu). **One judgement to state.** UT's Horizon page names Round Rock and no county, and the item carries Williamson, where Round Rock overwhelmingly sits. The November 21st run held Horizon for exactly this reason. This run admitted it on the city's county, and a maintainer may reverse that call.
- **Held as leads.** Wing's Fort Worth drone factory (company announcement, no topic in the vocabulary), TCEQ resuming data center permit reviews, Austin ISD's AI policy, Fermi America's hyperscaler deal, Giga Energy's Hunt County lease, Atlas Energy's Kodiak sand trucks, UT Southwestern's triage study (already tx-2026-0228) and UTMB's companion robot study.

## Instruments and discoverability

- `gridwatch_pagecheck` exit 2, advisory: November 1st is missing from the series and ERCOT can't backfill it. `waterwatch_pagecheck` and the water page self-test exit 0. `site_build` built 1037 pages from 228 items. media, schema, og, favicon, truetype, indexnow and seo checks exit 0.

## Discoverability signoff
- Card: `og/tx-2026-0257.png` opened. The headline wraps on whole words and ends in an ellipsis after "patient".
- `/questions/`: NOT LOOKED AT.
- `llms.txt` Open right now: the PUCT calendar item lists the December and January listings this run brought current. Fort Worth's moratorium, the ERCOT audit and Starbase's December 9th hearing are listed.
- `/sources/`: NOT LOOKED AT.
- `/topic/`: NOT LOOKED AT.
- `/place/`: NOT LOOKED AT.

## Selection, and what shipped

**Story.** tx-2026-0257, the Dell Med and IC² Institute AI Learning Lab: 80 clinicians meet paid actors in simulated encounters, half with Claude and half with UpToDate with its AI disabled, and researchers watch how each group reasons. It is AI in use in a Texas medical school, it rests on two primary pages, and `dedupe_check` cleared it at exit 0. **Refused:** TACC Horizon, `dedupe_check` exit 1 LIKELY REPEAT (0.70) against carousel no. 73, TACC's Frontera retirement on November 10th, and research-and-science is 8 of the 26 decks in the window.

**Claims.** One fact-checker returned 20 claims from the release and the project page, every quote re-matched against the fetched page by this run. `claims_check` clean. Rejected: any study dates, the team roster, the project page's Executive Vice Dean title, and any claim that the study has data.

**Treatment.** Three directors pitched (the controlled split, the clinician's hands, measuring a thought), all in explainer tone. Base: THE FAIR TEST. Grafted: the three questions as instruments at rest (5, 6, 7), the stethoscope wall (2) and the exam paper lengths (8). Accent cyan #22d3ee means only the tool within reach.

**Caption.** Two directors (the two things and Ledger; the quiet decision and Zoom out). The critic chose A and fixed four lines: a deck narration line and a scaffold line cut, the absence scoped to the release, Korndorffer and Kang put back to their claims' words. B failed the anti-template law against November 21st's first line and ran 913 characters.

## Slide artists and critics, by round

@@CRITIC_TABLE@@

## Flow critic, art director and the repair pass

See `flow_and_art_review.md`. The flow critic predicted art at 7.0 and named cyan pills on 6 and 7, three different tab designs on 5 to 7 and a misplaced ask pill. The art director first read the audition as revise (frame 7's rails did not end at the tool), then accepted it after one repair pass. A contrast pass to clear the 4.5 floor then muddied frame 7's bench, which was tightened and re-reviewed.

## Panel

@@PANEL@@

## Deviations, stated

- **Craft refresh (Phase 1) was not run.** No refresh searches this run.
- **Final art round split two ways.** Doctrine sends every frame still under 8.0 after its rework to a rebuild from its second concept. Frames under 7.0 (6, 7, 8, 9) were rebuilt; frames at 7.0 to 7.8 (1, 2, 3, 5) took a final pass on their round 2 fixes instead, because a full re-conception of a near frame was the likelier way to lose ground. Frames 6 and 7's rebuilds were worse and their round 2 frames were restored pixel for pixel.
- **Round 1 critic hand-backs for frames 1 to 3, 5, 7 to 9 are stored condensed** in `slide_critics.json`, not verbatim. Round 2 onward are close to verbatim.
- **Frame 6's last render** dropped an inline pill background that `deck_chassis` read as a plate, after its recheck critic had read it. The art did not change.
- **Artist render caps were exceeded** on several frames, chiefly frame 8 (18 renders in its first pass), much of it lost to a chassis bug: `K.make` centres a model's footprint, so the chassis `paper_roll` and `exam_table` land offset and `paper_roll.userData.end` is wrong.

## Retro

@@RETRO@@

## Prompt audit

@@PROMPT_AUDIT@@

## Timing

@@TIMING@@

## Gate status
