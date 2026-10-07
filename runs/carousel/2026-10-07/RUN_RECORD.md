# Run record, October 7th, 2026

Effort at wake: `high` (as the repo's settings carry it). The no-stall hook logged `armed` at
06:15:52 UTC and judged the session unattended from SessionStart, with the host's
`CLAUDE_CODE_SESSION_ATTENDED=0`. It refused nothing. The interim reading in Phase 17 measured 1,210
tool calls and none waited on a human. 293 waited on the auto mode classifier, the longest 4.2
seconds. **That reading is interim.** Phase 19 takes the one that counts, and the email carries it.

## DISPOSITION: SHIPPED AT THE ROUND CAP, 6.726, 1.274 UNDER THE 8.0 TOP RUNG, AFTER A ROUND 1 HARD FAIL WAS REPAIRED

Carousel no. 45, "The tax break came first. Saronic's Brownsville shipyard", is nine frames rendered
in one highNoon Gulf world on the Brownsville Ship Channel (haze #D3D8D4, the sun at azimuth 25 and
elevation 58), declared once in `assets/js/deck/2026-10-07-portalpha.js`. The hero is an illustrative
autonomous hull, drawn to illustrate and not Saronic's design. It appears afloat on frame 1, close at
its deckhouse on 2, and broadside with a 150 tonne steel block on 3. It is a speck at the bank of
the 835 acre square on 4 and on keel blocks at the head of an 850 foot line on 5. It is absent from
the courtroom on 6, small at the quay on 7, on blocks before twenty workers on 8, and gone from frame
5's camera on 9. Bluebonnet plan ink marks every release figure that isn't built.

The story is tx-2026-0204, admitted today. Saronic broke ground on Port Alpha at the Port of
Brownsville on September 30th. The Texas Tribune reported on June 18th that the Cameron County
Commissioners Court approved a $211 million tax break before Saronic had picked the port.

The deck went through these reviews:
- three pixel critic rounds, three critics each, the smaller tier
- two flow critic rounds, the second returning ship
- three panel rounds of three judges

The panel medians were 6.55, 6.818 and 6.726, read from `score.json` each round. Round 3 is the cap
on the ladder (8.0, 7.7, then ship). The finished deck ships at 6.726, 1.274 under the 8.0 top rung.
**The craft floor stood down at the cap with the art median at 5.8**, under its 8.5 line.

**The round 1 hard fail.** The integrity judge failed frame 9's dek, "The line runs 850 feet, the
length of the first ships Saronic says the yard will build." c9 is a ceiling, vessels up to 850
feet, and c16 names Navy landing craft for the first phase. The dek now reads "the longest Saronic
says the yard can build at first", the judge's own repair. Round 2 and round 3 found no hard fail.

**What the panel named and the run repaired between rounds.**
- Frame 3 now says the release names Navy landing craft for the first phase (c16), so the Marauder's
  figures aren't read as Port Alpha's product.
- Frame 6, the courtroom, carries a drawn-to-illustrate kicker.
- Frame 7 says the quay is drawn to its length and the positions and hull to illustrate.
- Frame 2 dropped "Corsair", which sits outside c24's quote span.
- The caption's close became "Who will count the jobs, and when?", because the cited article itemises
  jobs by role and the old question implied the record was silent.
- `aggregates.json` carried slide references from before the 6 and 7 swap, and they were corrected.

**What the panel named and the run did not fix.**
- The hero model, a slab hull with a stepped frustum deckhouse. All three judges ranked it the top art
  defect in every round. It is the chassis's own model and the round rule says a defect named twice is
  a composition problem. Recomposition didn't reach it, so it is queued as
  `marine-models-built-in-chassis` for the kit.
- Frames 4 and 7, the aerials, read as noise or a game board in all three rounds. A 450 m oblique on
  frame 4 in round 3 was worse, both squares lost to one texture, so the run reverted it. Queued as
  `aerial-ground-reads-as-noise`.
- Frames 2 and 3 spend two slots on Saronic's own claims, and every judge said so. The county half of
  the story rests on the Tribune because Cameron County's agendas are scanned PDFs with no text. Not
  cut, because the claims file holds no county primary that could replace them.
- No frame names a next step for a reader. The record holds no meeting, review date or published
  agreement to point to.
- The integrity judge's round 3 notes, not hard fails: "broke ground on September 30th" against c1's
  release wording, "told the Tribune" against c37's "issued a statement", and the first comment's
  release line omitting c4, which no frame prints.

## The deck's work, in order

- Pixel round 1 found a dark hull, no wash, faceted rocks, type over water, a missing hull on the quay
  frame, the courtroom and frame 8's count.
- Pixel round 2 found no visible wash, palms in the type, nested squares that didn't read, an
  uncountable lattice of build positions, a crowd of fourteen where twenty were promised, and a
  sourcing gap on frame 9's hook.
- Flow round 1 asked for the courtroom and quay frames to swap so the turn lands at 6, and the run did
  it.
- The foam skirt on the hull, the `keepClear` pass that hides trees projected into the type, the mast
  option and the projected crowd layout were all built in the chassis this run.
- Exposure went down to give the deck a true dark, then the type band went up so every line cleared
  4.5.

Value track, measured at 432 px off the shipped frames: 60.4, 62.3, 59.1, 59.6, 54.6, 42.7, 55.4,
57.1, 56.9 (`measurements.json`), deck median 57.1, under the light deck line.

## The record, first

Worklist at wake: 35 items due on the two day leash, none ROTTEN, no `--budget`. `reverify.py
--apply` stamped 16 items and wrote 19 dated unconfirmed lines for items behind measured boundaries.
tx-2026-0127 gained a claim from the Supreme Court of Texas's October 6th submission schedule, read on
txcourts.gov. Commit `91af281e`.

Admitted: tx-2026-0204, Saronic's Port Alpha groundbreaking on a Cameron County abatement, on
Saronic's release (read on PR Newswire) and the Tribune's June 18th report (commit `e1bc462e`). Held:
nothing new.

Discovery: the Federal Register returned nothing Texas specific, and the PUCT calendar's comment
deadlines held nothing AI.

The craft refresh studied sky banding, in `out/2026-10-07/tmp/craft_refresh.md`. Banding is 8 bit
quantisation, the cure is dither before the 8 bit write, and a frame that crops the sky toward the
horizon shows fewer rings.

## Sources that behaved differently from the registry

Appended to `knowledge/shared/SOURCES_FIELD_LOG.md` under 2026-10-07:
- faa.gov's 403 to `fetch_doc.py` and 200 to a browser user agent under `/uas/`
- Europe PMC as the route for tx-2026-0150 and tx-2026-0151
- txcourts.gov's text-layer schedules
- gov.texas.gov's robots refusal, with Saronic's release read on PR Newswire
- Cameron County's scanned agendas
- the Port of Brownsville's 403
- shipyardofthefuture.com's redirect to saronic.com
- the attorney general's 402

## Instruments

The page checks exited 0. The scanner's daily ceiling is unmeasured: today's count, the last day's
failures and the live `DAILY_CAP` are all unknown, because this session has no Cloudflare D1 access
and no read of the live Worker's settings. Nothing was reported healthy from a repository default.

## Did this run stop and wait for a human

The interim reading is above. No dialog, and nothing the hook refused. Phase 19's reading is the one
that counts and the email carries it.

## The weekly machine pass

Due today. Raising `qa-glyph-run-as-rule` to repeat 2 made `machine_due.py --date 2026-10-07` exit
0. The pass read seven shipped runs from `week_digest.py` and made one change, committed in `b7a0ea14`
under the upgrade lane.

- `autonomous_vessel`, `keel_block_line` and `riprap_bank` are lifted from this deck's chassis into
  `assets/js/kit/vehicles.js` and `assets/js/kit/landscape.js` at the judges' named fix. The hull has
  a sheer, a flared bow, a bulwark, a chamfered deckhouse, a lattice mast with radomes and one matte
  plate, and the riprap is quarried stone. The pass proved it by re-rendering this deck's frames 2,
  3 and 5 against the kit, and `sizes.py` passes 115 of 115. This run re-ran every verify command
  the pass returned, both proof renders included, and all exited 0. **This deck ships its chassis
  models.** The chassis's `installKit` returns early once the kit defines the vessel, so a re-render
  of no. 45 would now draw the kit's.
- `qa-glyph-run-as-rule` is escalated to `UPGRADE_BACKLOG.md` for a maintainer. Its fix is in `qa.py`
  under `.claude/`, which no run edits.
- The engine themes, render artifacts (7 runs, 21 rounds) and missing ground contact (7 runs, 20
  rounds), are carried to the backlog. `assets/js/txthree.js` is human lane.
- `dry_van` and its roadside siblings are deferred a fourth time. The next pass is due October 14th.

## Codex's review of the record

Six findings on the opened PR, all verified against the files and all fixed in `58579cc6`.
- tx-2026-0204 named the company and the county court as one decider of type `company`. The decider
  is now the Cameron County Commissioners Court.
- Its `decided` date was the Tribune's publication date, not the vote's. It is removed until the vote
  date is established.
- Its participation note called the June terms enforceable. It now says they are the terms reported
  before Saronic chose the site and their current form is not in the sources.
- tx-2026-0127 still advertised an open meeting after its October 6th argument. Its route is now
  contact only, and its title says the court set the argument.
- tx-2026-0127's `last_verified` had moved to October 7th on a check of one new source while c1 to
  c4 sit behind a robots refusal. It is back to September 30th.
- The article's alt text for slide 2 dropped "claims the", because the stamp pattern took any word
  after "claims" as a claim id. The id must now carry a digit.

## Queued for the next pass

Five items added to `knowledge/carousel/MACHINE_QUEUE.md`: `marine-models-built-in-chassis`,
`scatter-seeds-at-y0`, `aerial-ground-reads-as-noise`, `article-token-drops-unit` and
`make-slides-rewrites-every-frame`. Raised in place: `qa-glyph-run-as-rule` to repeat 2, which made
the weekly pass due today, and `caption-ledger-opening-moves-stale`, `sources-block-build-prose` and
`footer-veil-peaks-below-the-line` to repeat 1.

**The web edition's tokens.** `{{money:c26}}` rendered "$211 tax break" and `{{number:c28}}%` rendered
"95%%". `article_check` and the article tests passed both, and only reading the built page found
them. The prose now carries the magnitude word after each money token and no percent sign after the
number token. Queued as `article-token-drops-unit`.

## Craft memory

Confirmed `read-the-repair-at-feed-scale` (frame 4's 450 m oblique was worse than the defect it was
meant to cure), `measure-the-declared-value-arc-as-you-render` (the arc was measured and rewritten
every render) and `acceptance-items-need-a-floor` (the pixel critics again called several lists
trivially satisfiable). Added `lay-out-a-counted-crowd-by-projection` and `stand-the-wash-on-the-hull`.

## Things this run did not do

- It did not cut frames 2 and 3, which every judge named as cuttable.
- It did not read Cameron County's abatement order, which is a scanned PDF with no text layer.
- It did not remodel the hull. That is a kit lift for the weekly pass.
- It did not measure the scanner's day.

## Discoverability signoff

- **Decision card**: opened `docs/og/tx-2026-0204.png`. The title wraps at "Saronic breaks / ground
  at the Port of / Brownsville on Port / Alpha, a shipyard..." and ends on a whole word.
- **/questions/**: the fixed shapes read as a reader would type them ("What each decision is", 177
  answered). No new shape appeared today.
- **llms.txt Open right now**: ten entries, Taylor's October 8th vote and the FAA's Zipline comment
  window among them. tx-2026-0204 has no dated public way in and is rightly absent.
- **/sources/**: 1,025 of 1,178 claims rest on a primary document, across 321 documents from 136
  publishers. Today's admission added a company release and journalism. texastribune.org carries 54
  claims and 0 primaries, which is the county half of today's story.
- **/topic/**: the Defense and federal beat's page lists 9 decisions, matching the 9 the front page's
  beat card prints.
- **/place/**: Cameron County is on the hub and its page lists 3 items, tx-2026-0204 among them.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 34 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 2 warn(s) |
| aggregates     | PASS   | 9 declaration(s), 11 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 7.45 MB, vector |
| score          | WARN   | 6.726 at the round cap after 3 round(s), the finished deck ships; 8.0 top rung, shortfall named |
| labels         | PASS   | 46 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 74 published string(s) read from one list, every universal names its set |
| verbatim       | PASS   | 1 declared fragment(s) over 9 of 9 dossier(s), every one a literal substring of its own claim's quote |
| dossiers       | PASS   | 34,128 chars planned |
| caption        | PASS   | 148 words |
| craft floor    | PASS   | 9 frame(s), median 2464, floor 444 |
| plan vs render | PASS   | 9 of 48 acceptance item(s) checkable |
| texan          | WARN   | places Brownsville, Cameron County / body NO / deadline yes / next step NO |
| absences       | WARN   | 4 of 6 scoped to a named document, 2 unscoped |
| numerals       | PASS   | 18 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
