# Run record, October 17th, 2026

Carousel no. 53, MD Anderson's SPACER, an AI model that reads gene activity mapped across intact
tumor tissue to infer why T cells gather in some regions and avoid others, and whose leading finding
is that mucin may form a physical barrier keeping T cells away. Docket item tx-2026-0217, admitted
this run. The first deck under `prompts/carousel_studio.md`, and the first whose every frame is a
material relief through `txbench.js` rather than a staged spatial scene.

Effort at wake: `high`, as the repo's settings carry it.

## The record, first

- **Worklist.** `docket_staleness.py` named 29 items due, none rotten. 24 sit behind a measured crawl
  boundary (re-measured October 15th, five days left on that measurement) and are named UNREACHABLE
  by the selector, not counted as rot.
- **Re-verify** (commit 08c21a2e). `reverify.py --apply` stamped three items whose every claim came
  back unchanged (tx-2026-0118, tx-2026-0182, tx-2026-0212), and their tool-written notes were
  re-worded. Six more were checked by hand against the sources that answered and stamped with their
  own movement lines: tx-2026-0062 (Community Impact), tx-2026-0078 and tx-2026-0079 (the House
  committee meeting archives), tx-2026-0126 (the Senate committee meeting archive), tx-2026-0138
  (Texas Public Radio) and tx-2026-0179 (the city's own finance committee briefing and FOX 4). Each
  names what stays unconfirmed. `reverify.py --check-notes` exits 0.
- **Unreachable this run, and not stamped.** 403 from wilcotx.gov, keranews.org, brazoscountytx.gov,
  dhs.gov, brownsvilletx.gov, mylubbock.us, hayscountytx.gov, leandertx.gov and globenewswire.com,
  and 24 urls the crawl boundary refused before any request.
- **Admitted.** tx-2026-0217 (commit 79ed5e6f), MD Anderson's October 13th release, eleven claims,
  all primary, Harris County.
- **Discover.** Six scouts ran (ai-in-the-field, clinic-and-classroom, research-and-machines,
  what-texas-makes, power-and-compute, community-signal). The Federal Register API returned no open
  Texas AI comment window beyond the CFTC compute derivatives request the record already carries
  (tx-2026-0118, closing October 20th). Leads held for a later run, each needing its primary
  document: Plano's city council approval of a citywide AI initiative (October 12th, news reports
  only), the PUC's suit against the Attorney General's open records rulings on its data center
  survey (Texas Tribune, October 6th), USDA's AI-assisted screwworm drone flights over Texas (KRGV,
  October 12th), Fermi America's AMD credit support agreement at Project Matador in Carson County
  (company release, October 13th), Mesquite and La Joya ISDs' AI drafting of special education
  plans (trade press, October 13th) and UT Health San Antonio's dementia model fairness study
  (October 12th release).
- **Backlog.** The temp-dir build printed no `backlog:` lines, so the list held at zero.

## Instruments

Phase 7 ran every page check and every discoverability self-test, and all exited 0. The scanner's
daily ceiling was not read: this run holds no Cloudflare D1 access and no reading of the live
Worker's `DAILY_CAP`, so both values are unknown rather than healthy.

## Craft refresh

Not run as searches. The scouts spent the session's whole web search budget before Phase 1's
queries ran, so the refresh was the studio material instead: `examples/studio-proof/`, the
`txbench.js` source and `examples/art-direction-proof/`.

## Why this story and not the others

SPACER is AI in use at the bench rather than a decision about AI, it has a primary source on the
institution's own site and a peer reviewed abstract behind it, it is in Houston, and it carries a
physical claim, a sugar coat that may wall T cells off, that a material relief can draw directly.
`dedupe_check.py --item tx-2026-0217` exited 0 and the item clears the thirty day rule against all
26 decks in the window. Its host, mdanderson.org, is new to the window's instruments. Its beat,
research-and-science, carried 2 of the 26.

Refused, and why. Kodiak and Charger's Dallas to Laredo lane is tx-2026-0209 already and shares a
company and a city with no. 41 inside the window. Tesla's Cybercab count in Austin rests on a Tesla
post relayed by a fan site, the day after no. 52's robotaxi deck. The USDA screwworm drones rest on
one TV station's account. Fermi's AMD agreement is a company release on a site the record already
carries three items about. The UT System's Abridge agreement is tx-2026-0210. TEA's rescoring
requests are no. 38's subject.

`texan_check` at selection read places Houston, no public body, no deadline and no next step. A
research result has no comment window, so the deck carries its score on the art and on a close that
says plainly what the finding is not yet.

## The directors room

Three treatment directors pitched THE MEASURED EVIDENCE FIELD (one slide world under a darkfield key
at seven scales), ADDRESSES AND A WALL (the release's own postal comparison, a copper route stopping
at a mucin rampart) and WHAT A TEXAN HOLDS (a glass slide the size of a finger, down to the wall and
back up to the bench). The synthesis kept the first's spine and world, the second's wall and funders
and the third's 2 by 2 and its honest close, and refused the postal route (SPACER infers signals and
tracks no cell's route, so a drawn route overclaims), every txthree frame and every new kit model (a
microscope, a quarter, a gloved hand). `storyboard.md` carries the reasons. The deck is all nine
frames as material reliefs through `txbench.js`, the first under the studio route.

## The audition, and what it cost

The art director reviewed the cover, frame 7 (the wall, the hardest) and the close three times.

- **First reading, revise.** The coat and the wall split into two flat tones with a ragged
  boundary and speckled highlights, the wall cast nothing on the tumor, and the close was flat
  rectangles: a matte card for glass, a grey slab of stage, a beige disc for the light.
- **Second reading, revise.** The cover passed. Frame 7 carried screen aligned stripes and no
  crest highlight, and frame 9's light still read as a ceramic plate. The one repair rule applied,
  so the representation changed. Test renders with the cast off and then the specular off proved
  the stripes were geometry: the wall's centre line and the nest's outline wobbled on a three octave
  noise whose upper octaves changed their slope every 60 to 120 px. Both now follow smooth sums of
  sines. The close became darkfield: the aperture stays black, and light shows only as a thin ring
  at its rim and a lit rim on the section's outline.
- **Third reading, accept**, with polish items for the pixel pass: vary the coat's width, put a
  tighter highlight on the wall's crest, shade the engraved funder lines as cavities.

The relief engine has no transparency, no second specular lobe and no emissive term, and the
close's light from below is a screened stroke laid over the render after `TXBENCH.relief`. Queued.

## Pixel review and the flow pass

- **Pixel round 1, revise on all nine.** Five critics named the same deck fault in different
  words: murky rather than bold, no lit edges or pools, the mucin a matte grey, a hard seam under
  the type, letters colliding in two hooks, labels in the wrong place. The repairs went into the
  chassis (a key pool through `keyMask`, a glossier coat, darker steel, balanced hooks) and into
  every frame. Frame 9 was rebuilt round a bored aperture, frame 8's cores were made one size with
  the rim inside the edge, frame 6's kerb went from steel to the nest's own oxblood.
- **Pixel round 2, ship on seven.** Frame 1 still carried a hard step under the dek, which was the
  seam helper itself starting at half opacity, and frame 8's two higher mucin halos merged into one
  beaded figure eight. Both were fixed after the round (the seam now feathers both ways, the halos
  shrank and leave bare glass between the rows). Frame 8 then failed `layout_check`'s silhouette,
  so its four cores now sit on one bevelled array slide.
- **The flow pass, revise, predicted artwork 6.5.** Its craft block, by slide: 4 (5.5, the plate
  read as a chart on graph paper), 5 (6.0, the same), 9 (6.0, a thin close with the motif gone and a
  sticker outline on the section), 2 and 3 (6.5, grey label ends as the brightest mass). Cross frame,
  the palette strobed between warm tissue and cold grey hardware, and all nine frames share one
  skeleton, type on top and art in a band below. One change each went in: an anodised brushed
  plate on 4 and 5, the cover's nest held under the lens on 9 with a cool darkfield glow, darker
  label ends and warm specular bevels on 2 and 3, a lit pool where the count ends on 3, a plum black
  stage across the hardware, and the coat's own low glaze on 8's rims. Frame 7's dek lost its
  dictionary sentence, so c25 left the deck. **Not done, and the panel may charge it:** merging 4
  and 5 into one benchmark frame and re-seating three frames off the shared skeleton. Each is a new
  composition, past what one repair cycle buys.
- Frame 5's dek lost "It is no measure of any treatment" because `absence_check` found an absence
  that named no document.
- **Rechecks after the flow pass.** Pixel critics passed frames 1 to 4 at once. Frames 8 and 9
  came back revise: halo cells touching the array slide's bevel and a rim with scalloped seams on
  8, and on 9 the coat under the lens uncited (c7 added to its source line) and the stage's lit
  front edge running through the footer (raised clear, the faint vernier removed). Frame 5's
  plate lost a stitched band of tall cells. All four then shipped.
- **The audition was read three more times after the chassis changed.** The second reading
  failed frame 7 as a flat curb with no crest and no cast, frame 1 for a pale sawtooth where its
  coat met the torn edge, and frame 9 for the footer on the stage edge. The coat material went
  darker and wetter with a tight crest, frame 1's nest moved down, and the wall became a rounded
  ridge of varying width. The third reading passed 1 and 9 and failed 7 a second time, so the
  representation changed: the wall is now a heap of about 1,400 overlapping glossy globules over a
  low gel underlay, each one catching the key, with the T cells banked twice as densely at its
  foot.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 25 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 9 warn(s) |
| aggregates     | PASS   | 5 declaration(s), 9 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 8.51 MB, vector |
| score          | STALE  | score.json predates the newest render, so it describes a deck that no longer exists. Re-run it |
| labels         | PASS   | 46 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 89 published string(s) read from one list, every universal names its set |
| verbatim       | WARN   | no dossier declares a `verbatim:` block, so no on-frame string was held to a quote |
| dossiers       | PASS   | 32,975 chars planned |
| caption        | PASS   | 137 words |
| craft floor    | PASS   | 9 frame(s), median 620, floor 112 |
| plan vs render | PASS   | 9 of 37 acceptance item(s) checkable |
| texan          | WARN   | places NONE / body NO / deadline yes / next step NO |
| absences       | PASS   | 2 of 2 scoped to a named document |
| numerals       | PASS   | 8 numeral(s) over 9 frame(s), every one reachable |
| completion     | FAIL   | THE DECK DID NOT SHIP, so this run is not done |
<!-- gate-status:end -->

## The panel

- **Round 1, median 6.986 against the 8.0 rung, no hard fail, keep editing.** Integrity 6.914,
  craft 7.21, reader 6.94, spread 0.296. All three charged the same block: frames 2 to 5 as grey
  hardware outside the tissue world, 4 and 5 as bar charts on graph paper with no SPACER on the
  bars, 2 and 3 with mid grey label ends and no lit edge. Craft and integrity charged frame 1's
  matte coat against frame 7's glossy wall, craft and reader frame 6's invisible ring. All three
  named the missing Texas stake: no place, no body, no next step, the texan gate's own WARN.
  Integrity found three looser attributions, none a hard fail: the cover's MD Anderson date rested
  on the journal's date (c17), frame 2's journal kicker sat over release copy, frame 9's headline
  was Linghua Wang's sentence unattributed.
- **The repairs for round 2.** Frosted ends went pale and steel went dark with a hard specular
  across the chassis. Frames 2 and 3 got taller ground bevels and a cool darkfield rim on every
  section, and 3 a lit pool where the count stops. Frames 4 and 5 lost the graph grid. 4 now
  carries rows of engraved quarter-unit ticks with no ruled lines between them, because a bare
  plate fell under `layout_check`'s detail floor. 5 carries one engraved scale under the 21 bar,
  and both name SPACER on the bars. Frame 6's kerb rose into a lit ring and the T cells thin away
  from it. Frame 1's coat took the audition's own repair, about 2,600 small glossy globules. The
  cover's kicker now reads "Published October 13th", frame 2's "The method", frame 9's "Co-lead
  Linghua Wang" with c11, and the cover defines a T cell from c24. The caption lost its line
  about the frames and its narrowed statement of purpose.
- **Houston could not be named.** Fetched again this round, the release carries no dateline and
  names Houston only in its site navigation, so no claim supports a place. The merge of 4 into 5
  and a frame spent on a Texas stake were not made: each needs a new composition, and the second
  needs a fetched source the run doesn't have.
- **Round 2, median 6.96 against the 7.7 rung, no hard fail, keep editing.** Integrity 7.026,
  craft 6.81, reader 6.96, spread 0.216. The same block was charged again (4 and 5 as charts, 2 and
  3 as identical slides with outline halos and grey label ends), so round 3 recomposed rather than
  re-rendered, as the rule for a defect named twice says. Integrity caught a stale `copy.json`
  still carrying the round 1 caption, because `build_copy.py` reads the render report and had run
  before the caption edit. It was rebuilt and is rebuilt after every render now.
- **The repairs for round 3.** Frame 4 dropped the tick field, kept only the engraved scale along
  its top margin, and moved SPACER and the 4 onto the long bar's own track with room between the
  tracks. Frame 5 rose into the empty band, set each SPACER label on its own track and the 21 over
  its bar's end, and its engraved scale now runs all 21 units (it had stopped at 18 where a label
  lane cut it). Frames 2 and 3 lost the outline halos: each section now has height and casts, and
  the frost face is darker so the bevels and sections carry the light. Frame 3's pool sits on the
  bench where the count stops. Frame 9's frost end is lifted to the lightest surface after the
  aperture, its kicker reads "Linghua Wang says" (c10), and its absence names the release.
  "One slide here stands for each dataset" left frame 3 and became "Each glass slide drawn here
  stands for one dataset" on 2. The caption's absence names the release and CPRIT now helped fund
  "the study", as c12 says.
