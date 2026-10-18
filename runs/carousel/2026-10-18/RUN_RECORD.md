# Run record, October 18th, 2026

Carousel no. 54, USDA's AI screwworm models: the Agricultural Research Service's Kerrville laboratory
builds predictive models that already pick areas for surveillance, fly trapping and sterile fly
releases against New World screwworm in Texas, and its director says they can't predict people
moving infested animals. Docket item tx-2026-0218, admitted this run. Rendered in TXT's lastLight
world with two material reliefs, through the chassis `assets/js/deck/2026-10-18-brush.js`.

Effort at wake: `high`, as the repo's settings carry it.

## The record, first

- **Re-verify** (commit e2258800). 157 items checked, 112 by the reverify diff and 45 by hand, each
  hand-checked item stamped with its own movement line.
- **Admitted** (commit 1707c81a). Four items: tx-2026-0218 (USDA's screwworm models), tx-2026-0219
  (the PUC's suit against the Attorney General's open records rulings on its data center survey),
  tx-2026-0220 (San Antonio data center zoning) and tx-2026-0221 (UT Austin's Google.org fusion AI
  award). tx-2026-0218 was widened in two later commits (7a8dd983, 64e76701) with the commission's
  detections, the Edinburg facility, the reporting route and the zone counties.
- **At ship**, `house_style_check` named over-long sentences in the summaries of 0219, 0220 and 0221
  and in three claim texts behind the web edition (c1, c21, c29). Each was split at a clause; no fact
  changed.
- **Unreachable**: federalregister.gov and faa.gov answered 403, so no rule text is carried.

## The deck

- **Directors and plan.** Nine dossiers, CRAFT PLAN, continuity CAMERA_MOVE, MOTIF_EVOLUTION and
  VALUE_ARC. Scales from figures.json: one windmill per premises (43), one box per million flies a
  week (80 in a 100 slot block, the 300 plant as three more blocks), one animal per thousand seen (36).
- **The audition, and what it cost.** The macro fly on a wire failed twice as a cover (a toy over a
  mid-tone ground) and the representation changed to a backlit water point. The art director needed
  five readings before accepting 1, 5 and 9, then re-bound the frames three more times as the
  panel's repairs touched them. Causes found and fixed: kit metal mirroring the navy sky as the
  accent (a galvanized override in the chassis), TXT.stage behind and depth passed in metres rather
  than fractions (a lit band behind every headline), slot paint rotated by -yaw (outline corners that
  never closed), and a tank whose water can't be seen from a low eye (the rim now hides it).
- **Pixel review** (sonnet, round 1, all nine revise) and **one flow pass** (predicted art 6.7,
  weakest 6, 7, 8, 4). Summaries in `runs/carousel/2026-10-18/reviews/pixel_round1.md`.

## The panel

Three rounds, three judges each, combined by `panel.py`. Read `score.json` for every figure.

- **Round 1**: two judges named the same hard fail, frame 7's hook "None had it.", which went past
  c11. Repaired to "No case found.". Also repaired: frame 2's kicker and labelled zone rims, frame
  5's dropped "over Texas and Mexico", frame 8's "above all", the caption's line about the deck, the
  aircraft standing on frame 4's trap, the sky banding on frame 1.
- **Round 2**: two judges named a new hard fail, introduced by round 1's own repair: frame 5's
  "elsewhere in South Texas" placed the plant where no claim does. Repaired to "being built in South
  Texas". Frame 2's zone sentence now says "parts of", and frame 6's dek keeps c25's "helped".
- **Round 3, the cap**: no hard fail. **The deck ships at 7.36, 0.64 under the 8.0 top rung.** The
  art median is 6.5, under the 8.5 craft floor, which stands down at the cap.
- **Named by the judges and not fixed, for the next run**: the drone's lamp on frame 7 is still a
  flat disc (named in rounds 2 and 3 by all three), the kit figures on 4 and 9 read as mannequins,
  frame 8's slats lack a metal response, frame 3's towers tangle at feed size, frame 6's bedding
  lines cross the cuts, and the cover and slide 4 give the models agency c2 gives to USDA.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 34 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 7 warn(s) |
| aggregates     | PASS   | 9 declaration(s), 16 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 9.57 MB, vector |
| score          | WARN   | 7.36 at the round cap after 3 round(s), the finished deck ships; 8.0 top rung, shortfall named |
| labels         | PASS   | 54 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 79 published string(s) read from one list, every universal names its set |
| verbatim       | WARN   | no dossier declares a `verbatim:` block, so no on-frame string was held to a quote |
| dossiers       | PASS   | 38,404 chars planned |
| caption        | PASS   | 125 words |
| craft floor    | PASS   | 9 frame(s), median 543, floor 98 |
| plan vs render | PASS   | 9 of 51 acceptance item(s) checkable |
| texan          | WARN   | places Edinburg, Kerrville, Zavala County / body yes / deadline yes / next step NO |
| absences       | WARN   | 6 of 8 scoped to a named document, 2 unscoped |
| numerals       | PASS   | 15 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->


## Ship

Shipped images bound to the accepted review by `art_preflight --archive`; `measure_shipped` wrote
`measurements.json`. Ledgers updated by `update_ledgers.py`; the web edition is
`ledger/articles/2026-10-18.json` and `article_edition.mjs` passed every reader check. `main` was
merged before the rebuild and the nine verification checks exited 0.

## Discoverability signoff

Read on the temp-dir build of the record as it stood after re-verification and before today's four admissions; the merged build is the one Phase 16 opens.

- **Card, tx-2026-0217** (`og/tx-2026-0217.png`, the newest item in that build). Ends in a whole word and an ellipsis, but the wrap breaks "T cells" across two lines, "where T / cells", which no reader would do. A wrapper fix, not a record fix. Queued.
- **`/questions/`**. The hub carries 2,053 answered questions in its ItemList. The shapes read as typed questions on the beats sampled. Nothing new in shape since no new room or status entered that build.
- **`llms.txt`, Open right now.** Eight entries. Austin Community College's town hall of October 12th is still listed because the item's room stays open while the policy is in development. The CFTC compute derivatives window still closes October 20th and is listed. No window Phase 3 saw close today is still listed.
- **`/sources/`.** 1,120 of 1,282 claims rest on a primary document, across 344 documents from 148 publishers. The top publisher is interchange.puc.texas.gov (144 claims), a primary filer. Quoted material is still exempt and no house sentence hides inside an exempt block on the page read.
- **`/topic/`.** Research and science carries its blurb. Counted against its page after Phase 16, since today's admissions add two to it.
- **`/place/`.** NOT LOOKED AT on this build, because Kerr and Bexar take items only after today's admissions. Read after Phase 16.

**After Phase 16, on the merged build:**

- **Card, tx-2026-0221** (`og/tx-2026-0221.png`, the newest item). Wraps at whole words and ends in
  "testing..." with an ellipsis. Clean.
- **`/place/`.** `county-kerr` and `metro-kerrville` now carry 2 items each and `county-bexar` 11,
  each with its map. Read.
- **`/topic/`.** Research and science reads 38 of 193 decisions with its blurb. Read.

## Gate status



## Retro

- **Did this run wait on a human? Interim reading, Phase 17.** `prompt_audit.py` exited 1: 1,703
  tool calls measured and 25 whose permission decision took longer than an auto-approval, the
  longest 21.4 s, almost all of them subagent spawns, each released without a refusal. The no-stall
  hook was armed at 05:03:34 UTC, judged the session unattended from session start
  (`CLAUDE_CODE_SESSION_ATTENDED=0`, and the host's value was 0), and refused nothing. Phase 19
  takes the reading that counts.
- **Sources.** Five findings appended to `knowledge/shared/SOURCES_FIELD_LOG.md`: ars.usda.gov,
  aphis.usda.gov, krgv.com and tahc.texas.gov answered 200, and federalregister.gov and faa.gov
  answered 403.
- **Instincts added**: `stage-takes-fractions-not-metres`, `stand-back-from-a-kit-figure`.
- **Machine queue**: eight new items (kit metal mirroring the sky as the accent, TXT.stage's units,
  the painted plane rotation sign, the survey drone and stock trailer to lift into the kit, the full
  length kit person, long sentences passing admission, and the audition re-binding after each copy
  repair) and two repeats raised (sky banding, water with no reflection). `machine_due.py`: the
  weekly pass is not due, last run October 16th.
- **Arsenal** rebuilt and current.

## Review on the pull request

Codex reviewed the run commit and raised seven findings. All seven were taken.

- tx-2026-0221 now names Google.org as the decider, type company. UT Austin is the recipient.
- tx-2026-0218 lists Zavala County, so the county page for the first detection carries the item.
- tx-2026-0218 c3 was carrying two assertions on one quote. It is split into c3, models already
  used to choose surveillance, trapping and release areas, and c16, models can't predict every
  scenario, each with its own verbatim passage. The deck's claims file maps c5 to c16.
- tx-2026-0220 pointed its meeting route at a news release with no way to act on it. It now points
  at the city's Development Services public input page, which says how to comment by email, mail,
  hand delivery or voicemail and by when.
- The caption ledger row now uses `caption_check.comma_rate`, so it records the same count as the
  rest of the corpus.
- The round one pixel summaries are archived at `reviews/pixel_round1.md` beside this record.
- The Gmail payload finding was already fixed in the commit after the one reviewed.
