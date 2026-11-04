# Run record, November 3rd, 2026

Effort at wake: `high`, as the repo's settings carry it.

**THE GRID WATCH'S LARGE LOAD QUEUE READING IS STILL STOPPED, and CI fails on it.** `gridwatch_pagecheck.py` exits 3,
read at wake and again at ship: the newest verified queue month is 2026-08, three months back. It is the same cause the
November 1st and 2nd runs named, a filename the collector builds with a year ERCOT doesn't publish. The collector is cron
lane and this run may fix nothing in it. Because `main` is red on that step, this run's pull request will not show green
on its head and **does not merge**, like the pull requests for November 1st (no. 455) and November 2nd (no. 456). It
carries their commits, so merging this one once `main` is green lands all three days.

**Wake.** Branch `claude/daily-2026-11-03`, cut from `claude/daily-2026-11-02` merged with `origin/main`, because
November 2nd's deck never landed. Git identity and `core.hooksPath .githooks` were set before the first write.

## Craft refresh

Focus: material reliefs and staged contact shadows, the two surfaces the last three decks (nos. 64 to 66) leaned on.

- Ambient occlusion over a height field is computed as its own layer and multiplied into the shaded relief, which keeps cavity darkness independent of the key light. https://cartographicperspectives.org/index.php/journal/article/view/1901
- Line-sweep horizon lighting computes terrain occlusion in one pass over rows of the grid, cheap enough to run per frame on a relief. https://rreusser.github.io/notebooks/line-sweep-terrain-lighting/
- Relief mapping packs depth and normals in one texture and shades per fragment from both, which is the model TXBENCH's normal plus cavity pass already follows. https://developer.nvidia.com/gpugems/GPUGems3/gpugems3_ch18.html
- A contact shadow is a blurred top-down depth pass that ignores the light, so it belongs under a directional key shadow, never in place of one. https://discourse.threejs.org/t/how-to-be-closest-as-possible-to-that-render-shadow-diffuse-animated/21923
- Combining contact shadow, SAO and a noise pass is the forum recipe for grounded product renders. https://discourse.threejs.org/t/shadow-contact-threejs/29505
- Dark carousels stand out against the feed's white chrome, and covers that carry one bold claim with minimal clutter are the vendor consensus. https://www.trymypost.com/blog/linkedin-pdf-carousel-design-guide-2026

## The record, first

- **Re-verify, commit 582bee91.** 71 URLs behind 215 claims. 7 answered 304, 17 sent a body, 10 did not answer and 37
  were refused by the crawl boundary and never requested, so no item was stamped as checked and unchanged, and the
  unconfirmed items carry a dated line. www.utsouthwestern.edu and www.utep.edu did not answer their robots.txt and were
  read as refusing. The 403s came mostly from www.faa.gov, www.wilcotx.gov, www.globenewswire.com and
  www.brownsvilletx.gov. Nothing was routed around. The field log carries it.
- **Admitted, commit 3e58f2f2.** tx-2026-0239, Aurora's third quarter shareholder letter on SEC EDGAR, and tx-2026-0238,
  San Antonio's data center process, promoted on the City of San Antonio's own pages with Texas Public Radio as the
  secondary report.
- **At ship**, four claim sentences over the 30 word backstop were split and "9-2" became "9 to 2" in the record and the
  claims file, and tx-2026-0238's summary opens on two sentences instead of one. `docket_build.py --validate` exits 0.

## Selection

tx-2026-0239. Aurora's third quarter shareholder letter, filed with the SEC on October 28th, is a primary document about AI in use on Texas freight lanes, and it carries its own counter-image: the same letter that says the Aurora Driver now decides for itself whether a weigh station is open and will drive straight into customer sites in November says the truck build is about six weeks behind plan, held back by component quality and end-of-line testing, and reports a quarter's revenue of $3 million against an operating loss of $257 million. dedupe_check clears it against the 24 decks in the window (Kodiak's no. 41 was October 3rd, outside it).

Not chosen: San Antonio's data center vote (a decision the docket already narrates, and yesterday's deck was San Antonio), the AG's suit against OpenAI (journalism only, the release answered 402), UT Austin's ChatGPT Edu and Claude Edu contracts (journalism only, contracts unopened), Memorial Hermann's AI scribe (a vendor release over an unopened KLAS report), Mesquite ISD's IEP tool (journalism, a district claim), UTSA's Housing Helper (San Antonio again, and the measured figure is the rental data rather than the tool).

## The deck

Carousel no. 67, scale lane. Six spatial scenes in one floodlit weigh station and truck yard world at night (frames 1 to 4, 8 and 9) and three TXBENCH material reliefs (5 to 7), one chassis, `assets/js/deck/2026-11-03-scalelane.js`, with seven chassis models the kit lacked: `truck_scale`, `scale_house`, `scale_signal`, `flood_pole`, `guard_gate`, `cab_beacon` and `yard_stalls`. The visual argument: the truck makes the scale house call a driver used to make, and the company's own letter is weighed beside it. The one accent, rust primer #8C5A3C, means only what the letter says will happen and has not: November's stop bar (3), the production stop (5), the expected 2026 revenue groove (6), Charger's planned studs and New Braunfels (7), the 200 and 1,000 stalls (9).

Three treatment directors pitched (scale lane, measured ledger, corridor). Base WEIGH-IN; the primer accent rule arrived independently in two of three pitches and was grafted.

**The audition took three readings.** The art director revised twice: the cover did not read as a weigh station, the evidence frame's three rings and fork did not read, the close showed seven tractors and a hundred stalls. Accepted at the third reading after a rebuild of frame 2 around the truck's path, a visible flood source, and a counted yard.

**The caption room.** Two candidates (the before and after with Ledger; the who with Question and answer). The critic rejected both, A at 924 characters and with a hook that gave Aurora a claim about trucks in general, B for an above-the-fold plain question, the excluded move, and took one rewrite: the who, Ledger, pointing at the record.

**Frame 3 was rebuilt twice.** A view from inside the cab could not show the empty seat and the gate at once, so the gate is seen from beyond the boom with the tractor's nose at the primer bar.


**Two pixel rounds, one flow pass, and a recheck.** Round 1 sent all nine frames back for revision and round 2 sent all nine back again. The flow critic predicted 6.6 for artwork and ranked 3, 4, 8, 6, 2, 5, 9 and 7 weakest. The gate was moved so its cabinet post sits in the right half of 3. Frame 4 was rebuilt three ways: an oblique showed 14 to 15 of the 20 tractors and broke the GRID count, so the frontal two-rank view was kept, pulled back until all 20 are in frame and raised so the far rank fills the band the ground check reads. On 8 the camera went forward and below the roof line, and the beacon dome was brought back from cream to amber. On 6 the bar became blue-black mill scale and dropped 100 px. On 2 the scale house was turned so its lit window and door face the camera, and the third label was moved right of the house with an elbow leader that never enters ring 2. On 5 the pool closes in on the six-week span and the stop. The far 1,000 label on 9 went below its kerb.

**Not done, and named for the panel.** The flow critic asked for the type to come off the top band on 3 and 8, and for the beacon frame to move to position 3. Each would change counters, kickers and type layout on six frames and need a full new review round, so neither was attempted. Frame 7's stair-stepped county borders and the inlay's slab casts stay, because lowering the relief takes the frame under print_ban's cast floor. Frame 4's far rank shows sleeper backs as plain boxes.

**The audition took six readings in all.** It was accepted at the third reading, went stale when the pixel and flow repairs touched frames 1, 2 and 9, and was re-bound at the fourth (revise on 2's leader), fifth (accept) and sixth (accept, after a label halo panel_ready asked for).

## The panel

**Round 1, median 6.92, one hard fail.** The integrity judge charged frame 7's headline "One route now, one route
planned" as a count no claim supports. c21 names Dallas to Houston as Aurora's own route, the Fort Worth to El Paso
finding was rejected as unconfirmed rather than refuted, and c5 quotes Charger's president on autonomous operations
already launched on the Laredo corridor. The headline became "Aurora's own route, and a customer's plan". The same
round moved the $9 million mark out of the quarterly loss bar onto the datum, recomposed frame 8 as the whole stopped
tractor, darkened frame 5's steel, kept "about" before six weeks on the web edition, fixed the hardware_start_year basis
and cut the caption line that narrated the deck. The first `panel.py` call ran on cards with no lens field and counted a
round, so the log line was removed and the same three cards re-combined as round 1. No judge was paid twice.

**Round 2, median 7.16, no hard fail, under the 7.7 rung.** The work order named 4, 8, 6, 3, 5 and 9. Frame 3 got a gate
cabinet and a hook closer to c6 ("Next, through the security gate"), 4 was pulled back, 5's grooves were cut deeper, 6's
$9 million became a primer bracket from the billet's left edge, 8's lights went neutral, and the web edition's uncited
"call a driver used to make" line was replaced. Frames 2 and 9 were not changed because the audition review binds them.

**Round 3, the cap, median 7.11. It ships 0.89 under the 8.0 top rung, with no hard fail in rounds 2 or 3.** The
artwork median is 6.5, under the 8.5 craft floor, which stands down at the cap. Judges 6.82, 7.14 and 7.43.

**Named in every round and never fixed:** frame 4 reads as a toy lot of front-on tractors in a thin band (an oblique broke
the drawn count and a wider pull-back broke the detail floor), frame 8's kit cab reads as a model in a void with a pale
beacon, frame 6 reads as a textured bar more than steel, frame 3's gate is built from primitives, and the same kit grille
faces the camera on five frames. The integrity judge's round 3 lead is c5: it is verified and printed nowhere, so a
reader of frame 7 and the web edition can come away thinking nothing autonomous runs Dallas to Laredo. That is a lead
for the next deck on this corridor, not a fix made here.

## Ship

Artifacts in `runs/carousel/2026-11-03/`, `ship_images.py` at 40.1 to 44.4 dB against the 40.0 floor (slide 9's thumb
ships as PNG because WebP fell under the floor at quality 96), the review bound to the delivered images,
`measurements.json` written and checked. Web edition `ledger/articles/2026-11-03.json`, checked by `article_check` and
`tests/test_article_edition.py`. Its money tokens rendered "$3" and "$257" without "million" until the article said
"million" after each token. `SITE=docs node tests/article_edition.mjs` failed to import playwright as an ES module, the
queue's open item, so the page was opened at phone width by a CommonJS script instead: 6 images loaded, none broken.
Site rebuilt on top of `main`. `docket_build --validate`, `site_fresh_check`, `house_style_check`, `schema_check`,
`port_audit`, `media_check`, `seo_check`, `schema_contract`, `word_ban --run` and `article_check` all exit 0.

## Discoverability signoff

- og card: opened `docs/og/tx-2026-0239.png`. The headline wraps at whole words and ends "run straight to..." on a whole word.
- /questions/: read the hub. 210 answered for what each decision is and 208 for who decides. The questions read as typed questions.
- llms.txt Open right now: read it. tx-2026-0145 (closing November 9th) and tx-2026-0072 lead, and nothing closed today is listed.
- /sources/: the share reads 1360 of 1544 claims on a primary document, across 394 documents from 170 publishers. Today's two admissions rest on SEC EDGAR, ir.aurora.tech and sa.gov.
- /topic/: the State policy card says 29 decisions, and the ledger carries 29 items on that beat.
- /place/: Webb County reads 3 on the hub and its page lists 3 items (tx-2026-0037, 0209 and 0239).

## Timing

Minutes from wake: record 23.4, audition 94.9, art 118.2, review 204.4, panel 243.0, package 273.2.

## Permissions

`prompt_audit.py` (interim reading, Phase 17) measured 1,789 calls and listed 52 that waited 1 to 20 seconds, all of
them Agent launches, SendMessage calls and Bash calls that resolved with nobody present. That is the queue's open
`prompt-audit-counts-agent-latency` item, not a dialog. The no-stall hook was armed at 05:03:43Z, judged the session
unattended from the start (`CLAUDE_CODE_SESSION_ATTENDED=0` from the host), and refused nothing. The Phase 19 reading is
the one that counts.

## Retro

- **Light desaturates an accent.** Primer at the accent hex came out 10 to 20 Lab units off under the cool flood. The
  stop bar and the kerbs needed warmer albedo, and frame 9's accent fell off the frame when the pool moved off its stalls.
- **A relief's cast comes from height, not cast length**, and the cast floor and a judge asking for flatter county lines
  pull in opposite directions. Frame 7 landed at borders 8 px below the clay.
- **Moving a relief moves its rect.** Frame 6's dossier rect had to follow the bar twice or the detail floor read empty bed.
- **A count on the frame wants the camera that shows the count.** Three oblique views of frame 4 hid five or six of the
  twenty tractors. The frontal view kept the count and lost the drama, and the judges charged that every round.
- **An audition frame is frozen from the moment its review binds.** Every later repair to 2 or 9 cost a fresh reading,
  six in all, so the judges' last notes on 2 and 9 went unanswered.

## The weekly machine pass

`machine_due.py` found the pass due, because the queue's playwright item had bitten three runs. One
`carousel-upgrade-engineer` worked from `out/2026-11-03/week_digest.md`, where artwork_craft was the lowest criterion on
four of six decks and "largest object unmodelled" and "primitive model where a kit model belongs" were named on six of
six. It made two changes. The run re-ran every verify command it returned: `node --check`, `arsenal.py --check`, both
`examples/kit/build.py` proofs through the carousel engine, and `examples/kit/sizes.py` (138 of 138). All exit 0.

- **The kit `semi_truck` holds a close crop** (`assets/js/kit/vehicles.js`). It now has pressed windscreen posts with
  gaskets in place of round tubes, coated side glass, a door with hinges, a lock and grab handles, a sleeper baggage door,
  ribbed steps, and a bumper with a step, tow hooks and an air dam. The judges named the old one as primitive in every
  round of no. 67.
- **New kit models `checkpoint_gate` and `weigh_house`** (`assets/js/kit/civic.js`), built to the judges' named fix. The
  cabinet has a door seam, louvres, a bolted base plate and a caged amber lens. The house has a framed door, a hung
  canopy and railed steps. The queue item for this deck's chassis models is shipped in part. `yard_stalls`,
  `flood_pole`, `truck_scale`, `scale_signal` and `cab_beacon` stay in the chassis.
- **Escalated for a maintainer:** `tests/article_edition.mjs` can't import playwright as an ES module (nos. 60, 62 and
  67). `tests/` is human lane, so the fix is written up in `UPGRADE_BACKLOG.md`.

No. 67's shipped frames are unaffected, because they were rendered and bound before the kit changed. Re-rendering
today's slides would draw the new truck, which is the point of the lift for tomorrow's deck.

## Pull request

#457, ready, carrying #455 and #456. CI's `gates` job is red on the same `gridwatch_pagecheck` self-test step as `main`,
and the PR carries one comment saying so. It does not merge.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 27 verified claim(s) |
| render         | WARN   | 9 slide(s), 1 overflow warning(s) |
| qa             | WARN   | 0 fail(s), 6 warn(s) |
| aggregates     | PASS   | 9 declaration(s), 12 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 7.78 MB, vector |
| score          | STALE  | score.json predates the newest render, so it describes a deck that no longer exists. Re-run it |
| labels         | PASS   | 44 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 93 published string(s) read from one list, every universal names its set |
| verbatim       | WARN   | no dossier declares a `verbatim:` block, so no on-frame string was held to a quote |
| dossiers       | PASS   | 35,535 chars planned |
| caption        | PASS   | 122 words |
| craft floor    | WARN   | 9 frame(s), median 1981, floor 357, 1 quiet |
| plan vs render | WARN   | 9 of 61 acceptance item(s) checkable |
| texan          | WARN   | places Comal County, Dallas, Houston, Laredo, New Braunfels / body NO / deadline yes / next step yes |
| absences       | PASS   | 0 of 0 scoped to a named document |
| numerals       | PASS   | 20 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
