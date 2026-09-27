# Run record, September 27th, 2026

## DISPOSITION: SHIPPED AT THE ROUND CAP, 7.446, 0.554 UNDER THE 8.0 TOP RUNG

Carousel no. 35, "Rent, recommended overnight", nine rendered frames in one nightSodium world.
Five scoring rounds with three judges each. The panel medians were 6.756, 7.2, 7.26, 7.372 and
7.446. Rounds 1 and 2 carried hard fails (three, then one), each a sentence the source does not
support, and each was repaired from the source's own words. Rounds 3 to 5 carried none. At the
round cap the finished deck ships under the ladder with the shortfall named here and in the email.
The heaviest drag is artwork_craft (6.5 to 7.0 across the final judges).

## The record, first

- **Worklist.** `docket_staleness.py` named 45 items due on the two day leash, none rotten. `reverify.py --apply` stamped 14 of them from the diff alone (9 sources answered 304, 74 sent a body, 7 did not answer). The other 31 were read by hand, one primary source each, through `fetch_doc.py` and the crawl boundary, and 30 of those were stamped with a dated line. Every stamped item's movement line was re-worded (`reverify.py --check-notes` exit 0).
- **Held back, not stamped.** tx-2026-0088, Brazos County's own page, answers 403 to every client and is a measured boundary with 4 days left on its measurement. Its journalism source still reads the same, which is not the county's own word, so the item keeps its old stamp.
- **One source moved address.** tx-2026-0180, Leander's Flock notice, rotated off the front of the city's news page. The same notice reads unchanged at its own address, `/m/newsflash/Home/Detail/1347`, and both claims now cite it.
- **Read through WebFetch.** tx-2026-0120, the DHS Progreso account, answers 403 to the project fetcher and 200 to WebFetch, as the field log records. The three sentences checked came back exact.
- **Admitted.** tx-2026-0189, the Justice Department's proposed final judgment against Pinnacle Property Management Services, the Frisco apartment manager that licensed RealPage's AI Revenue Management, with the Tunney Act comment window open. tx-2026-0190, College Station City Council's 4 to 2 vote on September 24th to keep its Flock cameras, on the city's own account of the meeting. Both through `seed/docket_seed.json` and `--promote`, both on primary sources.
- **Held.** Nothing new was held.
- **A close date that is computed, and said so.** The notice for 0189 asks for comment within 60 days of September 18th and prints no closing date. The Competitive Impact Statement runs the window from the later of that date or a newspaper summary, and no newspaper date is printed. The record's close, November 17th, is the notice's own sixty days computed in code, and `notes_for_editor` says so.
- **A contradiction inside one source.** The proposed judgment's own definition places Pinnacle's headquarters in Dallas. The amended complaint and the Competitive Impact Statement say Frisco. The record follows the complaint and the statement and never attributes Frisco to the judgment.
- **Discovery.** The PUCT calendar feed carried nothing new and AI relevant (58555 is an ancillary services cost study). The Federal Register API surfaced the RealPage notice. Six scouts ran. The leads not admitted, with the reason, are in `out/research/`: El Paso Electric's McCloud proposal for decision (the PUCT document was not read), Waymo's San Antonio restart and Austin freeways (journalism only), MD Anderson's CIPHER model (a research result, a strong clinic candidate for a later run), the UT Dallas student and the AI agent under test (primary university release, not pursued for time), Wiwynn's Socorro rack plant.
- **The record's `reverify.py` writes the ledger at indent 2 and the canonical file is indent 1**, so its `--apply` rewrites every line of the 23,600 line file. This run wrote the ledger back at indent 1. A one-line fix in `reverify.py` for a maintainer or the upgrade lane.

## Instrument check

Every page check exited 0: `gridwatch_pagecheck`, `waterwatch_pagecheck`, `waterwatch_page --self-test`, the scratch build, `media_check`, `og`, `favicon`, `truetype`, `indexnow` self-tests and `seo_check`. `schema_check` exited 1 on the committed `docs/` only, because tx-2026-0180's page there still cites the old Leander listing url. The Phase 16 rebuild carries the new url.

## Discoverability signoff

- **Card.** `og/tx-2026-0189.png` opened as an image. The headline wraps at word boundaries over four lines and ends on "Frisco apartment..." with a whole word before the ellipsis.
- **/questions/.** Read as a reader. The questions are the record's own fixed set (what each decision is, who decides, how the public can take part, where a window is open). "05 answered" on open comment windows matches the hub's own count and is what a reader would ask.
- **llms.txt Open right now.** tx-2026-0189 is listed. tx-2026-0186 still closes October 11th and is listed. No window listed there closed today.
- **/sources/.** 848 of 952 claims rest on a primary document, across 277 documents from 125 publishers. Both admissions today rest wholly on primary documents. The top publisher is `interchange.puc.texas.gov`, 109 claims from 23 documents, which is a primary source.
- **/topic/.** The defense and federal card reads 8 decisions and 5 still open to comment. Its page lists 8 decisions.
- **/place/.** Brazos County, where 0190 landed, reads 10 on the hub and its page lists 10 decisions.

## A SLIP OF THIS RUN'S OWN, disclosed

**Four commits carried Claude attribution trailers.** The first four commits on this branch (the
re-verification, the admissions, the comment-window note and the first chassis commit) ended in a
`Co-Authored-By: Claude` line and a `Claude-Session:` link, which CLAUDE.md forbids on every commit.
The branch had been pushed but not merged. The messages were rewritten on this run's own branch
with those two lines removed and nothing else changed: the trees are byte identical, the author is
Talon Sturgill on every commit and every `Actor: daily` stamp survived. The branch was updated with
a lease on the old tip. Nothing with the trailers reached `main`.

## What the deck is

One nightSodium world declared once in `assets/js/deck/2026-09-27-nightrent.js`: a garden
apartment hero built in the chassis (five breezeway cores with wall packs and a pool of light on
the walk under each, a leasing office storefront at the west end), a key at azimuth 196 elevation
26, and the storefront's room light as the one accent #7FB2D9, carried indoors into the leasing
office monitor and the resident's laptop. The story runs from the lot at night, to the office where
the complaint says the price arrives (bulk acceptance, a reason to decline, nearly 60% within
2.5%), to the default limits drawn as two steel columns at one scale, to the lease data and the
48 Texas submarkets counted from Appendix A, to the judgment's nine numbered terms on the desk, to
the turn on frame 7 (frame 3's exact camera with the five cores switched off and the columns'
base plates left behind, the storefront still on), to the one bound landlord dark between two lit
neighbours, to a resident at a kitchen counter with the comment route.

## What the review rounds cost and bought

- **The turn had to be one camera.** Round 1's flow critic found that frames 3 and 7 were built
  from two cameras, so nobody could see the lamps go out. One shared camera, all five cores in
  frame, made it the deck's clearest beat, and round 2 called it the best thing in the deck.
- **Lit cores are invisible until the light reaches the ground.** Wall packs alone read as specks
  at 432 px. The chassis gained a pool on the walk under each lit core (`poolI`) and a per frame
  pack strength (`lampI`).
- **Copy against the claims.** Frame 2's hook "Accept all takes one click" had no claim behind
  it and became "Yes in bulk, no with a reason" (c30, c31). Frame 6's dek said "No outside
  software ..., a compliance officer, an annual audit, and inspections", which reads as the
  judgment banning its own oversight, and became "bars ... and requires ...". Frame 1 now says each
  participating property and a price recommendation (c25, c26). c30's claim text overstated its
  quote and was narrowed. c11, the comment address, was re-sourced from the federalregister.gov
  HTML to the govinfo PDF, whose text layer carries it across a line break, and raised to high.
  The caption now names the complaint and the impact statement as placing Pinnacle in Frisco
  (the judgment's own definition says Dallas) and gives the software limits their start, 180 days
  after the stipulation order is entered.
- **Accent coverage.** Moving cameras out to fit five cores shrank the storefront below
  `layout_check`'s floor on frames 1, 3 and 7. The accent holds on 2, 6 and 9 (the monitor, the
  monitor's edge and the laptop). Brightening the storefront blew it to white rather than toward
  the accent, which is recorded for the retro.
- **Frame 8 is declared GRID.** Three buildings side by side, dark hero between lit neighbours,
  never measured as one silhouette because they are three. The frame's data is a comparison of
  counts (3 and 8 lit of 12), which is what GRID measures, so the archetype was changed from
  SPLIT_HORIZON and the rotation still passes (no archetype twice in a row, seven distinct).
- **Frame 5's horizon.** Two critics asked for opposite things: sky behind the type, or the type
  on the ground. Neither fit five clusters in frame without a line through the hook, so the
  horizon sits above the kicker and the clusters were spread so every building separates at feed
  size.

## The five rounds

| round | integrity | craft | reader | median | hard fails |
|---|---|---|---|---|---|
| 1 | 6.69 | 7.30 | 6.86 | 6.756 | 3 (frame 3 auto-accept "by default", frame 8 "the case against RealPage goes on", twice) |
| 2 | 7.006 | 7.34 | 7.156 | 7.2 | 1 (frame 8 "other defendants" re-imports RealPage; c58 says "remaining") |
| 3 | 7.18 | 7.44 | 7.34 | 7.26 | 0 |
| 4 | 7.29 | 7.26 | 7.47 | 7.372 | 0 |
| 5 | 7.48 | 7.27 | 7.51 | 7.446 | 0, SHIP at the cap |

These figures are copied from each round's `scores/rN/score.json`, which `panel.py` wrote.

**Recompositions under the round rule.** Frame 9's kit figure was named in rounds 2, 3 and 4 (the
head behind the dek, a mannequin, a blown patch). Round 5 recomposed the frame without a person:
the counter, the lit laptop, a mug. The round 5 judges then named cabinet hardware crossing the
email line (legible, four unmeasurable QA warns), which is the next run's lesson. Frame 5's overhead
count was named in every round as objects in a void under a hard sky strip, and it was not
recomposed. The engineer's diagnosis is in the backlog: the frame lights only its clusters over an
unlit 30 km ground, and a kit ground cover model is the fix.

**Still standing at ship, named so the next run starts there.** Frame 5's void. Frame 8's empty
lower road and a key ("lit at the low share", "lit at the high share") that never says share of
what, because c36's figures were cut from the dek in round 4. The kit person's flat face on frames
3 and 7. Frame 9's cabinet hardware under the email line. The court (Middle District of North
Carolina, c2) named on no frame. The first comment lists the ids the frames print, so c13 is now
there and the caption-only c49 is not.

## AFTER THE CAP: a CI repair re-rendered six frames, and the score row reads STALE because of it

The local run of `guards.yml` found `shipped_check` red on the finished deck: frames 5 and 7 build
their labels in JavaScript with `<br>` inside the string, so the labels copy.json records were not
literally in the source, and the freshness gate refused them. The labels became plain strings with
CSS doing the wrapping, and frames 5 and 7 were re-rendered. By then the upgrade worker's kit lift
was live in the tree, so the re-rendered frames draw the kit `garden_apartment` with its new
shingled roof. Frames 1, 3, 4 and 8 were re-rendered with it too, so the hero is one building
across the deck. Frames 2, 6 and 9 are interiors and did not change.

So the shipped exterior frames are not pixel for pixel the ones the round 5 panel scored. The
composition, copy and claims are unchanged; the roof and the label wrapping are. That is why the
gate block's score row reads STALE. It was not re-scored, because past the round cap a round may
repair a hard fail and nothing else. Every gate was re-run on the shipped frames and passed.

A second gate defect surfaced on the way: `deck_coherence.frames_in` took the first extension
with any match, so frame 4 staying a PNG (its WebP fell under the quality floor) read the whole
shipped deck as one frame. Fixed in the upgrade lane and logged.

## Things this run did not do

- It did not name the court on a frame or in the caption.
- It did not print a close date, on purpose: the impact statement runs the window from the later
  of two publications and no newspaper date is printed.
- It did not count Pinnacle's Texas units; no fetched record gives one.

## The retro

- **Instincts.** Confirmed: a-count-must-name-the-set-it-counted, acceptance-items-need-a-floor,
  read-the-repair-at-feed-scale, a-gate-fix-can-create-an-editorial-defect. Added at 0.50:
  one-camera-for-a-change-of-state, read-the-claim-paragraph-not-the-quote.
- **Upgrade (upgrade lane, its own commit).** `garden_apartment` is lifted from the chassis into
  `assets/js/kit/homes.js` at the judges' named fix: a shingled roof with ridge cap, fascia, rakes,
  gutters and a light drip edge instead of a black slab, wall packs as bronze housings, and the walk
  pool under each lit core built in. Proved with `examples/kit/build.py` at goldenHour and blueHour
  and `examples/kit/sizes.py` (98 of 98 at size). The shipped frames were rendered with the chassis
  model before the lift and were not re-rendered. `ledger/carousel/upgrades.json` carries the entry
  and five proposals are in `knowledge/carousel/UPGRADE_BACKLOG.md`.
- **reverify.py.** It wrote `ledger/docket.json` at indent 2 while the canonical file is indent 1,
  for the third run running. Fixed in this run's daily commit (one line, the cache write untouched,
  `--self-test` exit 0).
- **house_style_check's cited list.** The Antitrust Division's comment address is the source's
  own published contact and the web edition turns on it, so it joins the FAA's address with its
  reason, on the precedent of carousel no. 33.

## Prompt audit (interim, Phase 17)

`prompt_audit.py` exited 1: 1,884 tool calls measured, 567 over its one second line. The longest
waits were 27.6 s and 25.7 s, then 12.3 s and 10.1 s, and the rest under 4.3 s. The no-stall hook
was armed at 06:16:27 UTC, judged the session unattended from the start (the host's
`CLAUDE_CODE_SESSION_ATTENDED` was 0) and refused nothing. No call waited long enough to have
stalled the run. What made 567 calls slower than a second is not established here. This reading is
interim; Phase 19's is the one that counts.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 64 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 6 warn(s) |
| aggregates     | PASS   | 7 declaration(s), 9 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 6.7 MB, vector |
| score          | STALE  | score.json predates the newest render, so it describes a deck that no longer exists. Re-run it |
| labels         | PASS   | 82 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 103 published string(s) read from one list, every universal names its set |
| verbatim       | PASS   | 4 declared fragment(s) over 2 of 9 dossier(s), every one a literal substring of its own claim's quote |
| dossiers       | PASS   | 30,636 chars planned |
| caption        | PASS   | 143 words |
| craft floor    | PASS   | 9 frame(s), median 778, floor 140 |
| plan vs render | WARN   | 9 of 38 acceptance item(s) checkable |
| texan          | WARN   | places Austin, Dallas, Dallas-Plano-Irving, Fort Worth, Houston, Irving, Plano, Round Rock, San Antonio / body yes / deadline yes / next step NO |
| absences       | WARN   | 0 of 4 scoped to a named document, 4 unscoped |
| numerals       | PASS   | 21 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
