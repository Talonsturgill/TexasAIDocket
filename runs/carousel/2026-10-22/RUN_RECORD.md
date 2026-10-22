# Run record, October 22nd, 2026

Carousel no. 57, the Texas A&M and UT Austin study of language models trained on junk social media posts
(tx-2026-0223).

Effort at wake: `high`, as the repo's settings carry it.

**Wake.** Pillow was broken in the container before bootstrap (`cannot import name '_imaging'`), so the first
`guards_local --fast --only Ownership` failed on the shallow clone build. `bootstrap.sh` reinstalled Pillow 12.3.0
and the check was re-run after it.

## The record, first

- **Worklist.** `docket_staleness.py` named 41 items due and none deferred. 24 sit behind a measured crawl
  boundary inside their window. Nothing was ROTTEN outside a measured boundary.
- **Re-verify** (commit d361747b). `reverify.py --apply` read 85 urls behind 268 claims and stamped 2 items
  unchanged (tx-2026-0212, tx-2026-0220). The other 15 due items outside a boundary were checked by hand through
  `fetch_doc.py`, which asks the crawl boundary first, and no quote had gone missing anywhere.
  - Stamped with their own movement line, every reachable quote confirmed: tx-2026-0037, 0044, 0049, 0052, 0071,
    0072, 0075, 0084, 0103, 0112 and 0162.
  - **tx-2026-0072.** Eight of its claims quote a PUCT filing delivered as a ZIP. The ZIP was opened in scratch and
    all eight quotes were found in the presentation and the letter inside it, three of them cell by cell from a
    table.
  - **Unconfirmed today, not stamped**: tx-2026-0133, 0161, 0165 and 0173. www.uta.edu, news.unt.edu and
    engineering.unt.edu fail TLS verification through the container's proxy (`self-signed certificate in
    certificate chain` and `unable to get local issuer certificate`, with the proxy's CA bundle). That is not a
    robots refusal and was not measured as a boundary. Each item carries a dated line saying what is unconfirmed.
    They reach the six day hard limit on October 24th if the hosts stay unreachable.
  - www.oncor.com's robots.txt closes the connection to the project's reader (`RemoteDisconnected`), so Oncor's
    page for tx-2026-0112 stays unconfirmed. Nothing was routed around.
- **Admitted.** tx-2026-0226, the Comptroller's October 13th ban on state grant money for Flock cameras and other
  license plate readers, on the Comptroller's own GovDelivery bulletin, statewide. tx-2026-0227, UTEP's NASA funded
  flood mapping work with El Paso Water and the Prithvi-EO model, on the university's own release, El Paso County.
- **Held, not seeded.** Midland's vote to end its Flock contract (journalism only). H&P and ExxonMobil's rig floor
  robots (the release names no Texas place and no AI). The Fifth Circuit's Flock argument (journalism, no docket
  fetched). Northside ISD's ChatGPT for Teachers launch (journalism, launch unconfirmed). The TWDB data center
  survey response counts (journalism, the board's own data not fetched).
- **Backlog.** To be read off the Phase 7 build.
- **Backlog.** The Phase 7 temp build printed no `backlog:` line.
- **Instruments.** Every Phase 7 check exited 0: both page checks, the water page self-test, the build, media,
  schema, the cards, the favicon, the glyph reader, IndexNow and SEO. No instrument has stopped.
- **Scanner ceiling.** Not checked. This run holds no Cloudflare D1 access and no read of the live `texas-scan`
  Worker's `DAILY_CAP`, so today's scan count, the failures of the last day and the deployed cap are all unknown.

## Discoverability signoff

Read on the Phase 7 temp build of this run's record (`out/2026-10-22/tmp/site`).

- **Card, tx-2026-0227** (`og/tx-2026-0227.png`, opened as an image). The headline wraps at whole words and ends
  "model can map..." with an ellipsis after a whole word. Clean.
- **`/questions/`.** Opened. The hub carries the questions as structured data rather than item ids, so the two new
  items were not traced through it. NOT LOOKED AT for whether a new shape reads well.
- **`llms.txt`, Open right now.** Seven entries. Austin Community College's tx-2026-0212 still leads, and its
  community seminar is dated today, so the listing holds today. Every other entry carries a future date.
- **`/sources/`.** 1,218 of 1,392 claims rest on a primary document, across 361 documents from 158 publishers, up
  from 1,205 of 1,379 on October 21st. The new claims were all primary.
- **`/topic/`.** Surveillance and policing now carries tx-2026-0226, and its page lists 36 item links.
- **`/place/`.** `county-el-paso` carries tx-2026-0227 and `county-brazos` carries tx-2026-0223.

## Craft refresh

Focus: a measured quantity built as a physical object under a low key, since the last four decks drew counts as
units and plan reliefs and this story is a dose response measured in benchmark scores.

- A solid bar is read by its length and a sphere by its surface area, so a score is built as a length, never a
  volume. https://test01.ku.dk/:obvius/pureproxy/3974268/en/publications/a-psychophysical-investigation-of-size-as-a-physical-variable
- A transmission material without reflections and light behind it reads dull, opacity stays at 1 and the cost per
  pixel is real. https://tympanus.net/codrops/?p=57089
- Low key glass and metal is lit from behind or above for the rim, with the background kept far and black cards
  cutting spill. https://www.picturecorrect.com/expert-lighting-techniques-for-photographing-still-life/

## Selection

**tx-2026-0223**, the Texas A&M study with the University of Texas at Austin and Purdue listed as its institutions.
`dedupe_check` exit 0, nothing close, and the thirty day rule clears it against the 25 decks in the window. It was
chosen because its primary document carries a measured dose response a picture can build at one scale (ARC Challenge
with chain of thought at 57.2, 64.1, 69.3, 71.2 and 72.1 as the junk share falls from 100% to 0%), an honest
counter image in the paper's own limits (one platform, four open models, closed models untested, doses rather than
an estimate of the internet) and a Texas lab. The fact check found the releases date the posts to 2010 and the paper
to 2023, so the record was corrected and the deck prints no collection year.

Others and why not today: the Comptroller's license plate reader grant ban (admitted as tx-2026-0226, but Flock was
carousel no. 39's subject on October 1st), UTEP's flood mapping (admitted as tx-2026-0227, no result yet, and a flood
deck ran on October 12th), H&P's rig floor robots (no Texas place and no AI in the release), the TWDB data center
survey counts (journalism only), the Alpha pilots in Houston, Fort Davis and Aldine (the Alpha charter was no. 42 on
October 4th). `texan_check` at selection: places Austin, Brazos County and College Station, no body, no deadline, no
next step, so the close has to carry what follows.

## The deck

- **Directors and plan.** Nine dossiers, CRAFT PLAN, continuity MOTIF_EVOLUTION, CAMERA_MOVE and VALUE_ARC, VALUE
  CUT at frame 6. One scale for every score, 0.06 m per point (`CH.S`), so a landing's height is its score and the
  brass datum is the base model's. Counts from figures.json: five doses, three variable tracking landings, the bare
  share of the carcass from the 84% No Thinking share, four whole treads and one sawn to 0.8 for 4.8 times the junk
  tokens, four flights for four models.
- **The chassis** (`assets/js/deck/2026-10-22-stair.js`) built five models the kit lacks: an open stair flight with
  weathering steel stringers and aggregate treads, a landing on a limestone pier, a coursed datum wall with a brass
  band, one loose cast tread and a chalked pad. They are queued for the weekly lift.
- **The audition** took five readings before 1, 3 and 9 were accepted. Revise on the first build (a cork aggregate,
  flat stone, a frontal frame 3 with no piers). Accept on the second. Revise twice more after the datum band changed:
  hung down from the datum it ate the shortfall under the 0% landing, its coplanar accent plane z-fought into a moire
  the critics read as a screen, then self-lit it read as a painted stripe, and the cover's feet were out of frame.
  Accept on the fifth, with lit brass standing 4 cm proud, warm shadow-side steel and a cover standing on its ground.
- **Pixel review** (two rounds on all nine, smaller tier, then one recheck of 4, 6, 7 and 8 after the flow pass).
  Copy caught in review: "viral" on the cover was stronger than c18 and c19 say, "open" in "four open models" rests
  on no claim, "the clean data" on slide 6 named the other repair, slide 9's dek read as if better data caused the
  difficulty (c68 says the opposite), slide 7 said "model" where c47 says "models". All rewritten. Every critic read
  the body face's straight apostrophe as curly; the DOM carries U+0027 throughout.
- **One flow pass** predicted art 6.6, weakest 4, 7, 6, 8 and 2. Repaired one change each: frame 4 rebuilt as a low
  side profile under a brass rail on posts, off the shared wall; frame 7 as a three quarter view of the whole repaired
  flight with a fresh limestone landing; frame 6's stacks with every end in frame and worked ground behind; frame 8's
  flights two metres apart with the pad in line as the fifth place. Not done: frame 2 (the relief), 1, 3 and 9 (bound
  to the accepted audition), and frame 5, whose restaging under the open side rendered as a silhouette below the
  detail floor and was reverted. The limestone mottle the flow critic named on five frames lives in the chassis and
  was left, because changing it reopens the accepted audition.

## The panel

Three judges each round, combined by `panel.py`. Read `score.json` for every figure. The cards were written to
`score-<lens>.json` from the judges' hand-backs as returned.

- **Round 1**: no hard fail, median 7.12 under the 8.0 rung. All three named frame 4 first (a stone bar chart), then
  6, 9 and 1. Integrity named slide 8's "four models" against the run's own c58, the appendix test on Llama3 70B
  Instruct, and no slide naming Twitter/X; it also found the frame code holding typed constants beside comments that
  said "from figures.json". Repaired, one change each where a frame was named: frame 4 rebuilt with the no junk
  landing it cited and never drew, under the datum wall, from a low three quarter so every landing shows its top and
  the cliff falls into shadow; frame 6's treads narrowed so the camera comes in with every end in frame, the scatter
  cut to fine grit; frame 9's figure turned up the broken flight and held under a fifth of the frame; frame 1's dek
  measure narrowed off the landing; frame 2's slivers kept whole in frame and its top edge feathered into the dark;
  frame 8's labels on one baseline at the type floor. Slide 8 now names Twitter/X and the 70B result (c15, c58) and
  says "Four main models". Every frame now reads its figures by name from figures.json, written into the page at
  build time by `fig.py`, so no frame carries a typed number. The caption's opening line was rewritten, which two
  judges called thin.
- **Round 2**: no hard fail, median 7.16 under the 7.7 rung. Every judge again named frame 4 first, then 7, 6, 8
  and 9. Integrity found slide 8's 57.8 and 52.7 for the 70B model readable against the chain of thought scores on
  slides 3 and 7 (it is a different ARC Challenge measure), and the 84% stated without its junk measure. Repaired:
  slide 8 now says the 70B model also fell, with no figure to misread; slide 5 says the 84% is for junk defined by
  engagement; frame 4's eye lowered to just above the landings so the short riser is not inflated; frame 7 framed
  tighter on the repaired flight with the wall a step darker; frame 6's label brought to its tread; frame 9's figure
  in dark matte cloth, near a silhouette against the lit pier. A finer pier grain on frame 4 tiled visibly and was
  reverted.
