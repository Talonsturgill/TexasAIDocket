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
