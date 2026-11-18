# Run record, November 17th, 2026 (carousel no. 80)

**The instrument pages were down at wake, and main's CI is red on a runner change this run can't fix.** At 02:25 UTC on November 18th, `gridwatch.yml` run 44221269317 collected the November 16th settled day and its site rebuild failed. Commit da83516b then removed 807 files from `docs/` (sources 188, place 153, facility 150, water 121, articles 80, company 67, questions 13, topic 9). `gridwatch_pagecheck` and `waterwatch_pagecheck` exited 3 because `docs/grid/index.html` and `docs/water/` were missing on main. Pages last deployed at 00:30 UTC on 35d5f7d1 and won't deploy while guards are red, so the live site is stale, not broken. The cause was a date-dependent refusal in `scripts/site/site_pages/feeds.py`. The questions check raised when the "Can the public comment on it" shape had no open comment window that day. The fix (546d2e3b, here and on PR #497) lets a dated shape be empty and gives its page an empty-state lede. This run's rebuild restores the deleted files. The collector and its ledgers are cron's and were not touched.

**CI.** `ubuntu-latest` now resolves to Ubuntu 26.04, where Playwright 1.56.1 fails with "does not support chromium on ubuntu26.04-x64". browser-layout, browser-read and browser-render are red on main (guards run 44236261916) and on every pull request. The fix is human lane, either `runs-on: ubuntu-24.04` in `guards.yml` or a Playwright bump in `package.json`. The owner was notified at wake and PR #497 carries the account.

**Shipped at the round cap, 7.378 (panel median, `score.json`), 0.622 under round 1's 8.0 bar. No judge found a hard fail in any round. The art median, 7.4, is under the 8.5 craft floor, which stands down at the cap.** Round 3 judges scored 7.30 (integrity), 7.37 (craft) and 7.53 (reader).

**Effort note.** `run_state.json` recorded `$CLAUDE_EFFORT` as `medium` at wake, the fourth run in a row. `.claude/settings.json` carries `effortLevel: high`, and nothing in this repository can change what the host passes.

## The record, first

- **Wake.** Branch `claude/daily-2026-11-17`. Git identity and `core.hooksPath .githooks` set before the first write. Pillow's compiled module was broken in the system Python at wake, and `bootstrap.sh` installed Pillow 12.3.0.
- **Re-verification**, commit 8396ec9c. 153 URLs read. 15 items were stamped unchanged, and six more (0065, 0066, 0067, 0069, 0147, 0159) after their PDFs were read through `fetch_doc.py`. Fifteen automatic notes were reworded. The PUCT Interchange filing lists cited on tx-2026-0003 and tx-2026-0076 no longer show the filings quoted by c17 to c21, because those list pages drop older filings, so both stay unstamped rather than read as a change. tx-2026-0072 (a ZIP read with zipfile and pypdf) and tx-2026-0075 were re-verified by hand (9cf00ec5), which cleared the rotten-source gate CI had raised.
- **Moves and admissions**, commit 9d386ff5. tx-2026-0194 gained the Texas Tribune's October 7th claims on the spring rescore counts, a summary and history. tx-2026-0182 gained TCEQ claims c34 to c37 on the permit review resuming. tx-2026-0250, TACC's Horizon system in Williamson County, was admitted.

## Selection, and what shipped

**Story.** tx-2026-0194. Since December 2023 TEA's automated scoring engine has scored the written answers on English STAAR tests first, and its design, as TEA described it in December 2023 and March 2024, routes at least 25 percent to people too, whose score counts. Requests to regrade reading answers went from 2,758 in spring 2024 to 64,489 this spring (Texas Tribune), the state raised more than 13,300 reading scores after the reviews, and Dallas ISD saw 34% of more than 5,100 come back higher. A rescore costs $50 a test if the score holds and is free if it changes.

**Refused.** Horizon (tx-2026-0250) scored LIKELY REPEAT 0.86 against the November 10th Frontera deck, which named it. The TCEQ restart rests on journalism alone.

**Integrity limits, stated on the frames.** The 2026 counts rest on one Tribune report because TEA's rescore pages answered 404. TEA's design figures are dated to their documents. The September review of 27,200 students is a different review and never sits beside the requests.

**Art.** The fourth BESPOKE + LOOK V2 run, watch tone, spine `assets/js/deck/2026-11-17-scorebench-bespoke.js`, accent #e0956a (dusk gold) meaning a person's score and nothing else. The deck is bookended. Frame 1 leaves a person's desk dark behind the machine that reads first, and frame 9 lights that desk at the end of a gold chute from the same machine.

## The three-frame review

Cold slide critics read frame 1 five times (6.4, 5.8, 5.6, 5.6, 5.9) and frame 9 four times. Their yes and no answers on `encoding_reads` and `dominant_subject_finished` flipped between two readings of near identical pixels. The review moved to `carousel-art-director`, the reviewer the routine names. It accepted 5 and 9, and sent frame 1 back twice: first because the page lay on a tray tipped toward the viewer and read as printer output, then because a framed upright page read as a screen or a typewriter. The third representation, a smoked glass read chamber where the swallowed half of the page curls over a roller past a lilac scan bar, was accepted. The review was refreshed and accepted again before rounds 2 and 3, each time on the art director's own reading. Frame 5's ream bands came back coral and were recoloured kraft before round 3.

## Panel

- **Round 1**, 7.26 (6.96, 7.46, 7.16), no hard fail, under the 8.0 rung. Repairs: copy (frame 1 "English", frame 3 TEA's own "closed database" wording, frame 5 "Then the requests multiplied", frame 7's "one in five of this spring's requests" removed because no quote ties 13,300 raised scores to the 64,489 requests, and frame 8 names Dallas County); art on 4, 6, 7 and 9.
- **Round 2**, 7.336 (7.26, 7.31, 7.53), no hard fail, under the 7.7 rung. Repairs: frame 2 cites TEA's own March 2024 document (c18) for the hand scoring cost, and `compute.py` now parses c18 and asserts it equals c10. "Redesigned" is gone from frame 2, frame 5 says "regrade" as its source does, and the caption's first line says "written answer" because no claim says STAAR answers are typed. Frame 7 became a diagonal macro of a block of 200 sheets with one gilded sheet pulled proud, `changed_one_in` = 200 computed from c5's 0.5 percent. Its first version, seven gilded pages in 44, contradicted the dek's "fewer than half of one percent". Frame 4 was pushed in, frame 6's floating foot and stray desk leg were fixed, frame 8's gold tiles retuned and frame 5 polished.
- **Round 3**, 7.378 at the cap. Ships.
- **After scoring, before shipping.** `fig_inject --check` read eight slides as dynamic FIG users because error strings named FIG. The checks were rewritten as static reads before round 3, and every re-render was pixel identical except small noise patches on 4 and 6. `layout_check --require` then refused the ship at the image step because dusk gold measured on one frame: the gold on 4, 6 and 7 was too small or rendered orange under the watch grade. Frames 7 and 8 were retuned until 7, 8 and 9 carried it (coverage 0.0065, 0.008 and 0.003 against a 0.002 floor). Frame 7's single gold stripe now reads more strongly than the judges saw. **The deck was not scored again for those two retunes.** The sources block was rebuilt to list c18 and drop c10.

**Named shortfall.** The craft median of 7.4 is held down by frame 2 (flat orthographic relief, aliased strata texture), frame 4 (the one-in-four pages small at feed size, an empty left third), frame 1 (a machine still close to a typewriter silhouette) and the kit desk and chair on 1, 4, 6 and 9 two days after a desks deck. On story, every judge asked for a rescore window or deadline and the route a parent takes through a district. Neither is in the claims file, so neither is on the deck. "Drawn to illustrate" closes eight deks.

## Retro

- `knowledge/carousel/MACHINE_QUEUE.md` (upgrade lane, 02ecc375 and 61acbaa1). New items cover the scoring_engine chassis (floating rollers, an infeed tray that reads as an outfeed), K.make centring a footprint (the 2026-11-13 backlog proposal again), the studio-ground gate fix, the cover's read-versus-whole tension, render_report.json being overwritten by parallel renders, fig_inject reading string literals as dynamic, running the accent floor before the panel, and the level camera over a ground vertex. Repeat counts were raised on dusk-gold-under-watch-key and art-preflight-has-no-bespoke-route.
- `scripts/carousel/depth_floor.py` (upgrade lane, d12451a5). A TXT.studio sweep counts as a ground, with self-tests.
- `knowledge/carousel/UPGRADE_BACKLOG.md`. One engine proposal for a maintainer, TXT.ground offsetting its grid from a level camera.
- `ledger/carousel/instincts.json` (3d0c679c). Confirmed a-paraphrase-can-outrun-its-quote and a-drawing-may-not-state-what-the-data-refutes. Added parallel-renders-clobber-one-report.
- `knowledge/shared/SOURCES_FIELD_LOG.md` (3195f24a). PUCT filing lists drop older filings, TEA's rescore pages answered 404, and the 0072 ZIP was read outside WebFetch.
- `machine_due.py`: no weekly pass due (last ran November 13th).

## Prompt audit (interim)

`prompt_audit.py`: 2373 tool calls measured, 72 over its waiting threshold. The longest are Agent and SendMessage calls at 7 to 25 seconds, plus Bash calls under 8 seconds, the latency shape already queued as prompt-audit-counts-agent-latency. The no-stall hook was armed at 05:07:15 UTC, judged the session unattended (`CLAUDE_CODE_SESSION_ATTENDED=0` from the host) and refused nothing. Phase 19 takes the reading that counts.

## Social delivery and email

Social delivery for this edition runs after the merge, under the DAILY SOCIAL DELIVERY section, and its receipts go to the Gmail draft rather than this record, because the merge is the last thing that touches git. With main's CI red on the runner change, the merge is expected to be blocked, and the draft will say so.

## Discoverability signoff

The web edition at `ledger/articles/2026-11-17.json` passes `article_check` and `tests/test_article_edition.py`. The site build passes `seo_check`, `schema_check`, `media_check` and `site_fresh_check`, and the questions page is restored.
