# Run record, October 20th, 2026

Carousel no. 55, Houston Methodist's operating room cameras: a study in the Journal of Imaging ties four wall
cameras in each of the 15 rooms of Walter Tower's cardiothoracic suite to an estimated 25 more cases a month,
and says plainly it can't show the cameras caused it. Docket item tx-2026-0222, admitted this run.

Effort at wake: `high`, as the repo's settings carry it.

## The record, first

- **Worklist.** `docket_staleness.py` named 35 items due, 3 of them ROTTEN (tx-2026-0015, tx-2026-0186,
  tx-2026-0198) and 24 behind a measured crawl boundary. Nothing deferred.
- **Re-verify** (commit 307d03a8). `reverify.py --apply` stamped 6 items unchanged, and their machine lines were
  re-worded by hand. Nine more were checked by hand against one primary source each: 0015, 0061, 0062, 0078,
  0079, 0126, 0138, 0186 and 0198.
  - **tx-2026-0198 moved.** Kodiak's October 6th release puts its readiness measure at 96 percent at the end of
    September, up from 93. Added as c17.
  - **tx-2026-0186 moved.** The FAA's review page no longer carries the call for comments and now says the
    period closed on October 11th. c2 now quotes what the page says today.
- **Boundaries re-measured.** 23 unreachable items had their boundary measured again today, every one still
  refusing, nothing routed around. tx-2026-0055 and tx-2026-0044 carry the claim-source boundary format and were
  left for their own window. Two robots files are unusual and were read the way a literal reader reads them:
  public.destinyhosted.com serves `User-agent: * Disallow: /` on one line, and clinicaltrials.gov splits its one
  group with a blank line before `Disallow: /api/`.
- **Admitted** (commits fb18da3f, 7a2efc7d). tx-2026-0222 (Houston Methodist's operating room camera study),
  tx-2026-0223 (Texas A&M's finding that models trained on junk posts skip reasoning steps) and tx-2026-0224
  (Rice's plan for 40 more AI faculty). All three rest on primary sources. Admission first held 0222 for a comma
  rate of 4.82 per 100 words, and the summary was split at its commas.
- **Backlog.** The temp build printed no `backlog:` line.

## Craft refresh

Focus: the material reliefs and spatial interiors of the last three decks, and paper or stacked units as a measured scale.

- Paper is a thin layered material whose look mixes subsurface scatter, specular, retroreflection and sheen, and a classic microfacet model can't reproduce its two sided look. https://diglib.eg.org/items/d47b1de1-f554-48fd-8f77-f1594391a4dc/full
- MeshPhysicalMaterial costs per pixel and every feature adds cost; sheen is for cloth, clearcoat suits glass and coated metal. https://threejs.org/docs/pages/MeshPhysicalMaterial.html
- Physicalised counts read best when the unit is a real object, per the physical visualisation catalogue. https://dataphys.org/list/solid-statistics/

## Selection

The strongest candidate of the morning was STAAR rescoring, which the Tribune reported on October 7th: reading
rescore requests went from 2,758 to 21,620 to 64,489 in three springs while an engine scores most answers first.
**`dedupe_check` refused it at exit 3**: the record carries it as tx-2026-0194, and carousel no. 38 of September
30th was built on that same item and its same TEA documents. The thirty day rule is binding, so it was dropped.

Houston Methodist's study was chosen over the rest of the scouts' field because it is AI in use with a measured
outcome and the honest counter-image is in the paper itself: an estimate with a wide interval, a placebo test at
p = 0.182, a bundle the cameras can't be split from, and a hospital that owns part of the vendor. It cleared the
thirty day rule against all 25 decks in the window, the last Houston Methodist deck being no. 19 of September 9th.
The other leads, and why not today: Texas A&M's junk data study (fresh and primary, but two research decks ran on
the 17th and 18th), the Harris County plate reader working group and the Comptroller's grant order (journalism
only, and plate readers ran on October 1st), Plano's AI purchase (journalism only, no outcome), Zipline in Round
Rock (the same company over the same metros as no. 33).

## The deck

- **Directors and plan.** Nine dossiers, CRAFT PLAN, continuity CAMERA_MOVE, MOTIF_EVOLUTION and VALUE_ARC, VALUE
  CUT at frame 7. Scales from figures.json: one sterile container end per case (339 in steel, 25 more in gold),
  one taped bay per case of the interval's high end (41, a white stripe to 8.3), one clamp per unit of the placebo
  test (11, the second gold), four cameras per room.
- **The audition, and what it cost.** The art director needed five readings before accepting 1, 4 and 9, and a
  sixth after the pixel and flow repairs moved the chassis. Causes found and fixed: TXT.interior's back wall is
  0.2 m thick and centred on its nominal plane, so a board placed there vanished; the lit back wall behind the
  container wall read as an extruded slab, cured by taking the room out of the pool; the close was reshot twice,
  first without the worker, then close on the container; the sterile container read as a toy suitcase until it was
  rebuilt in the chassis with a gasket, perforated filter plates, bail handles, latches and a separate tamper tag;
  coplanar card parts z-fought into slivers on the instanced wall.
- **Pixel review** (two rounds, smaller tier). Round 1 returned all nine revise and round 2 cleared 01 only.
  Summaries in `runs/carousel/2026-10-20/reviews/pixel_round1.md`. Named holdouts after round 2: 02's footer
  crossing (fixed in the flow repairs), 03 and 04's even light (a raking flood added), 05's stripe contrast and
  vinyl, 06's towel, 07's kit figure (cut), 08's grey page and 09's empty middle band.
- **One flow pass** predicted art 6.0, weakest 7, 8, 5, 2, 3, 6, 4, and named a one-skeleton type layout on all nine
  frames. Repairs, one each: 07 cut the figure and brought the camera near on a boom arm, turned on the board; 08
  ended the page above the footer as the one bright object on near black steel; 05 staged the lids in the key's
  pool; 02 lifted the model off the footer and modelled each camera from above; 03 and 04 took a raking flood from
  the left; 06 a finer, quieter weave and a harder key; 09 pulled back to the whole container with its contact and a
  tile wainscot washed behind it. **Not done**: the type skeleton is unchanged on all nine frames, and the gold on
  frame 9 is not explained on that frame. The pixel critics rechecked the changed frames: 02 to 05, 07 and 08 ship,
  06 and 09 named one non-blocking defect each, both then repaired.

## The panel

Three judges each round, combined by `panel.py`. Read `score.json` for every figure.

- **Round 1**: the integrity judge named one hard fail. The caption called Apella "the vendor" and slide 8's turn
  rested on it, while c13's quote only said the hospital holds an equity interest in Apella. The paper does say it,
  in its own words, and the run re-fetched the page and added that sentence as c28 to the claims and to
  tx-2026-0222, with c13's text cut back to what its quote proves. Also repaired from the round: slide 9's hook
  scoped to surgery footage and its close moved to the consent the hospital's blog describes (c26), dropping the
  retention figures whose audio line the blog contradicts; slide 6 now says the placebo result points the same way
  (c9); slide 1 says the system is image based AI and went live in December 2022 (c4); slide 8 names Apella as the
  vendor (c28). Art, one change each: 05's lids taller with longer casts and the vinyl outside the pool darker, 02's
  walls taller, 06's jaws shorter, 07's boom arm cast removed, 08's page warmer.
- **Round 2**: no hard fail, under the 7.7 rung, so the work order said keep editing, frames 7, 5, 8, 2, 3, 4, 9 in
  that order. Repaired, one change each: 07's camera now closes the boom arm on its own plate and the board's blocks
  take the deck's colours with one gold; 05's low-end marker raised so the key reaches it, white at feed size; 08's
  page falls into shadow below its upper half; 02's camera housings pale with gold lens rings. **Tried and reverted**:
  a deeper room behind 03 and 04 to remove the black base of the back wall, which lit the container wall flat and
  pale, so both frames went back to the accepted state. **Not done**: 09's camera can't sit lower at a real mount
  height in this framing, and 04's rake and crown were left as the art director accepted them. The judges' round 2
  cards were transcribed by the showrunner from their hand-backs, scores and totals as returned, reasons abridged.
- **Round 3, the cap**: no hard fail. **The deck ships at 7.09, 0.91 under the 8.0 top rung.** The art median is
  6.5, under the 8.5 craft floor, which stands down at the cap. Round 3's cards were transcribed by the showrunner
  from the judges' hand-backs, scores, totals and weakest frames as returned, reasons abridged.
- **Named by the judges and not fixed, for the next run**: frame 7 is the weakest image in every round (the board's
  flat blocks, the mount); frame 8 reads as type on a plate in the mid tones; frame 2 reads as a floor plan; frame 5
  reads as a grid; the walls on 3 and 4 are lit evenly with the black base of the room's back wall behind them;
  gold is used beyond its one meaning on 2, 7 and 9. On the copy, frame 7 carries the blog's turnover line where the
  paper's own operative-minutes result (c12) belongs, the first comment's id list omits c12 though the caption
  states it, and frame 5's headline reads a 95% interval as bounds. Past the cap only a hard fail may be repaired.

## Ship

Shipped images bound to the accepted review by `art_preflight --archive`, quality 40.1 to 44.6 dB against a 40.0
floor; `measure_shipped` wrote `measurements.json` and its check matches. Ledgers updated by `update_ledgers.py`.
The web edition is `ledger/articles/2026-10-20.json`, and `article_edition.mjs` passed 900 reader checks after
`npm ci` installed its pinned Playwright; the article was read at 390 and 1280 px. `main` had nothing new to merge
before the rebuild. The record rebuild found two of today's summaries over the 30 word backstop, and splitting
tx-2026-0222's also corrected its "11 other" sites to c8's 10 donor sites. All nine verification checks exited 0.

**Studio clock.** Minutes from wake: record_done 113.9, audition_done 117.0, art_done 120.4, review_done 175.4,
panel_done 206.9, package_done 224.7. **record_done and audition_done were stamped late**, at 07:02 and after the
fifth art reading rather than when each phase ended; the record work was committed at 05:44, about 36 minutes
after wake, and the audition ran most of the two hours between.

**CI on the first head went red** on `gates`, `email_check --all`, because the email payload had not been built yet. Built and committed before the merge, as carousel no. 7 taught. Reproducing the rest of that job locally found `ledger_check` refusing today's topic prose for number words (four, one, eleven) that are not counting figures, so they became digits, and frame 7's line in the topic and artwork ledgers stopped describing the crew member that round 1 removed.

## Discoverability signoff

Read on a temp-dir build of the record as it stands after today's three admissions (`site_build --out
out/2026-10-20/tmp/site`, 920 pages, 196 items). It was read late, during the art phase, so the record it shows
already carries tx-2026-0222 to tx-2026-0224. The merged build is the one Phase 16 opens.

- **Card, tx-2026-0224** (`og/tx-2026-0224.png`, the newest item). Rice's headline wraps at whole words and ends
  in "take..." with an ellipsis. Clean.
- **`/questions/`.** The hub's ItemList carries 2,128 answered questions, up from 2,053 on October 18th with the
  week's admissions.
- **`llms.txt`, Open right now.** Eight entries. Austin Community College's policy town hall, the CFTC compute derivatives
  request (its window closes today), the NTIA internet use survey closing November 9th and the governor's
  interconnection queue audit lead the list. No window this morning's re-verification saw close is still listed.
- **`/sources/`.** 1,188 of 1,353 claims rest on a primary document, across 355 documents from 154 publishers.
  interchange.puc.texas.gov still leads with 144 claims.
- **`/topic/`.** Health and education reads 30 of 196 decisions with its blurb and carries tx-2026-0222.
- **`/place/`.** `county-harris` carries 30 items with its map and now includes tx-2026-0222.

## Retro

- **Did this run wait on a human? Interim reading, Phase 17.** `prompt_audit.py` exited 1: 1,928 tool calls
  measured and 23 whose permission decision took longer than an auto-approval, 21 of them subagent spawns and 2
  Bash calls, each released without a refusal, the longest about 20.6 s. The no-stall hook was armed at 05:07:08 UTC,
  judged the session unattended from session start (`CLAUDE_CODE_SESSION_ATTENDED=0`, and the host's value was 0),
  and refused nothing. Phase 19 takes the reading that counts.
- **Sources.** Seven findings appended to `knowledge/shared/SOURCES_FIELD_LOG.md`: pmc.ncbi.nlm.nih.gov,
  www.houstonmethodist.org, kodiak.ai and Europe PMC answered 200; www.mdpi.com, a PDF on www.faa.gov and
  www.mylubbock.us answered 403; www.keranews.org redirected to www.kera.org, which answered 403.
- **Instincts confirmed**: `a-paraphrase-can-outrun-its-quote` (c13's text said vendor, its quote did not),
  `the-records-own-prose-drifts-while-you-draw` (two summaries over the backstop found only at the rebuild),
  `recompose-kit-primitives-at-distance` and `stand-back-from-a-kit-figure` (the close's worker cut, the container
  rebuilt), `read-the-repair-at-feed-scale` (the deeper room behind 03 and 04 made them worse and was reverted).
  **Added**: `interior-back-wall-is-thick`, `keep-the-wall-mount-on-its-wall`.
- **Machine queue**: six new items (the eight operating room models to lift into the kit, TXT.interior's back wall
  swallowing wall mounts, a small ground showing its edge in a wide shot, K.make re-centring wall-hung models,
  depth_floor asking for a literal ground inside an interior, and judge cards that came back under three different
  keys so six were transcribed by hand) and three repeats raised (the full length kit person, the detail floor on
  dark walls, the audition re-binding after each copy repair). `machine_due.py`: the weekly pass is not due, last run
  October 16th, 74 items queued.
- **Arsenal** rebuilt and current.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 28 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 4 warn(s) |
| aggregates     | PASS   | 9 declaration(s), 14 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 8.8 MB, vector |
| score          | WARN   | 7.09 at the round cap after 3 round(s), the finished deck ships; 8.0 top rung, shortfall named |
| labels         | PASS   | 50 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 62 published string(s) read from one list, every universal names its set |
| verbatim       | PASS   | 3 declared fragment(s) over 9 of 9 dossier(s), every one a literal substring of its own claim's quote |
| dossiers       | PASS   | 34,998 chars planned |
| caption        | PASS   | 152 words |
| craft floor    | PASS   | 9 frame(s), median 1880, floor 338 |
| plan vs render | PASS   | 9 of 50 acceptance item(s) checkable |
| texan          | WARN   | places Houston / body NO / deadline yes / next step NO |
| absences       | WARN   | 5 of 7 scoped to a named document, 2 unscoped |
| numerals       | PASS   | 18 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
