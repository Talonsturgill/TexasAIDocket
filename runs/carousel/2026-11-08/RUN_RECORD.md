# Run record, November 8th, 2026 (carousel no. 72)

**SHIPPED AT THE ROUND CAP AT 7.266, 0.734 UNDER THE 8.0 TOP RUNG.** Three ladder rounds and one hard-fail repair round,
three judges each. The art median stood at 6.8 and the craft floor stood down at the cap. Two hard fails were found and
repaired, both the same shape: a university release overstating what the paper says, stated in the deck's own voice.

## The record, first

- **Wake.** Branch `claude/daily-2026-11-08`, cut from `origin/main` at b7a7ad91, which carries PR no. 463's restoration of the November chain. Git identity and `core.hooksPath .githooks` set before the first write. Effort `high`. No `prompts/NEXT_RUN.md`. `docket_build --validate` was red at wake on staleness only, the expected clock. The guard step "the build reads the ledgers" failed once at wake because bootstrap was installing Pillow in parallel; Pillow 12.3.0 imports cleanly after.
- **Worklist.** `docket_staleness` named 92 due items, none rotten. `reverify --apply` stamped 7 unchanged (reworded per item). A run-scratch verifier then fetched each remaining item's claim sources through `fetch_doc.py` (boundary, robots and PDF text) and confirmed 60 more on a verbatim quote, each given its own dated line. 23 items behind measured crawl boundaries were re-measured with today's responses appended and a dated line each; tx-2026-0055's structured claim-source boundary was rebuilt from today's robots and county-page hashes. tx-2026-0150 and tx-2026-0151 (PubMed abstracts) were confirmed through NCBI E-utilities after pubmed.ncbi.nlm.nih.gov answered a 203 challenge page.
- **Moved.** League City voters rejected the fixed plate reader cameras on November 3rd by the city's unofficial count; removal follows the November 17th canvass and the mayor asked staff to cover them now (tx-2026-0048, four claims from the city's own pages). ERCOT told the commission on November 5th it had reviewed answers from 257 developers, expects second questions for most, and must report on December 10th (tx-2026-0156, tx-2026-0072). Oncor's two 765 kV dockets grew to 5864 and 533 filings (tx-2026-0003, tx-2026-0076).
- **Admitted.** tx-2026-0244, Texas A&M AgriLife's AlphaFold-Multimer screen of the human mitochondrial proteome, on the university's November 5th release and the paper's Europe PMC record. 11 claims, all primary. Brazos County from the authors' College Station affiliation.
- **Held.** Nothing new held. The seed's older held candidates stay held.
- **Backlog.** `site_build` printed no backlog lines; the list is no longer than at wake.
- **Discovered and not admitted.** The scouts' Kodiak, Tesla Fort Worth, Comptroller, STAAR, Alpha School, Rice and UT Dallas leads are either already in the record or journalism-only this run.

## Instruments

`gridwatch_pagecheck` exit 2, an advisory rather than a stopped instrument: one day missing from the series, November 1st, which ERCOT can't backfill. Not presentation, so nothing for this run to fix. `waterwatch_pagecheck` 0. Discoverability gates all 0.

## Craft refresh
Focus: figures and hard surfaces that read as mannequins and slabs at feed size (no. 71's kit person on four frames and frame 7's fans read as two slabs).
- A figure reads at silhouette first, then colour block, then detail, so cut small protrusions and judge the side and three quarter view at thumbnail size before adding detail. https://80.lv/articles/efficient-character-design-for-games-tips-tricks/ and https://polycount.com/discussion/comment/1852693
- Negative space inside the outline (an arm off the body, a gap at the knees) sharpens a small figure more than surface detail does. https://sidney-eliot.github.io/3d-artists-handbook/work_in_progress/artistic-side-of-character-design
- On a dark field the subject separates by a narrow light behind it drawing the contour, sharp for metal and softer for organic forms, with background brightness set before light intensity. https://www.creativebloq.com/3d/how-to-use-key-fill-and-rim-lighting-in-3d-art and https://3drender.com/light/3point.html
- A larger quantity is shown by more units at one size in aligned rows, never by a stretched unit, which gives the reader both a count and a height. https://isotyperevisited.org/2012/08/introduction.php and https://tableau.com/sites/default/files/2023-01/Haroz_CHI_2015.pdf

## Selection, and what shipped

tx-2026-0244, Texas A&M's AlphaFold-Multimer screen of the human mitochondrial proteome, on the paper's own text
(Nature Communications, read through Europe PMC) and the university's November 5th release. As shipped: a curated list of
1123 proteins, every pairing of them, 630,003 pairs, screened; 2,895 kept at a mean ipTM cutoff of 0.5, the paper's 0.46%;
57% of those in none of the databases checked; at least one predicted partner for 85 uncharacterized proteins; several
partnerships confirmed in yeast and human cells over about two years; the list free at mitomatch.web.app. Brazos County.

## Art

The audition (cover, frame 4, close) took twelve readings by the `carousel-art-director`. Frame 4 was accepted on the
fourth. The close failed five times as a slate-tile scene, each repair finding a new cause (contact decals blacking the
foreground, the stage pool, a reversed light vector, a footer wash dulling the block), and was accepted on the ninth only
after its representation changed to the cover's own bench answered. The cover's hard step under the dek was the window
sill, not the wash. The grey chain tops across four readings were the type washes fading past the dek. Two pixel rounds,
one flow pass (predicted art 6.3, weakest 6, 5, 7, 8, 3, 2) and one recheck of the changed frames.

## Panel

| round | integrity | craft | reader | median | hard fail |
|---|---|---|---|---|---|
| 1 | 6.55 | 7.25 | 7.16 | 7.14 | none |
| 2 | 6.74 | 7.20 | 6.88 | 7.166 | web edition dated AlphaFold-Multimer to 2022 on the release's word |
| 3 | 6.63 | 7.27 | 7.12 | 7.086 | slide 7 said the 85 proteins got their "first" partners, from the release |
| 4 | 7.26 | 7.256 | 7.10 | 7.266 | none |

`panel.py` medians. Round 2's repair narrowed c6 to "Google DeepMind created AlphaFold-Multimer, according to the release"
with no year on any surface, and added c29, MitoMatch's address from the paper. Round 3's repair replaced c15 with c30,
the paper's "at least one interacting partner for 85 uncharacterized proteins". Holdouts the judges named late, none a hard
fail, shipped as they are:
- Frames 7 and 8 read as primitives: grey cylinder tubes, a petri tower that reads as pancakes. Named in every round.
- Frames 5 and 6 read as flat reliefs; frame 5's 0.5 step sits low and its precision leader points at one boss.
- Frame 3 is a dark triangle with an unexplained raised band.
- Slide 7's kicker "NEW PARTNERS" is looser than the paper, which recapitulates two partners already reported.
- Several judges asked for the cutoff (5) before the find (4); the order was not changed past the cap.
- "Drawn to illustrate" on seven of nine deks reads as boilerplate.

## Retro

- **Instincts.** Confirmed `a-paraphrase-can-outrun-its-quote`, `check-the-cover-noun-against-the-release` and
  `the-plan-is-not-the-product`. Added `read-the-release-against-the-paper` and
  `a-type-wash-past-the-dek-greys-the-subject`.
- **Weekly machine pass (due, last pass November 3rd).** Commit d8df7c4b lifts lab glassware into
  `assets/js/kit/interior.js` (`microcentrifuge_tube`, `microcentrifuge_rack`, `petri_dish`) at the judges' named fix, the
  week's top theme, a primitive where a kit model belongs, named on 6 of 6 runs over 19 rounds. Commit 72302521 fits the
  kit worker's hi-vis vest to the body (queue repeat 3); the face and hands stay open at repeat 5. Queue, backlog and
  `upgrades.json` in dab1f3ba, `machine_pass.json` in ed288636. Escalated, both outside the upgrade lane:
  `prompt_audit.py` counting agent spawn latency as human waits (repeat 7), and `fetch_doc` passing hosts whose robots.txt
  names ClaudeBot for the whole site. The verify commands were rerun here: `node --check` on both kit files, `arsenal.py
  --check`, `machine_due.py --self-test` and `ownership_check --actor upgrade` all exit 0, and `machine_due.py` reports
  not due.
- **Prompt audit (interim).** 1,993 calls measured, 83 counted as waiting. The top of the list is Agent spawns at 4 to
  18 s and the slowest Bash call is about 1.1 s, the escalated latency count. No call has the shape of a human answering a
  dialog. The no-stall hook was armed at 05:03:36 UTC, judged the session unattended and refused nothing.

## Discoverability signoff
- og card: `og/tx-2026-0244.png` opened as an image. The headline wraps after whole words in four lines and ends "of human..." on a whole word.
- /questions/: twelve section questions read as a reader ("Who decides", "How the public can take part", "Where a comment window is open" and so on). Per-question answers NOT LOOKED AT this run.
- llms.txt Open right now: the federal survey office's household internet survey question, closing November 9th, still leads, then the Governor's data center audit (tx-2026-0072), which now carries ERCOT's December 10th report date.
- /sources/: the share reads 1452 of 1656 claims on a primary document across 414 documents from 181 publishers. The top publisher is interchange.puc.texas.gov. The Tribune ranks third with 57 claims and none primary, which is the record leaning on journalism for those items. Publisher pages NOT LOOKED AT.
- /topic/: tx-2026-0244 is on `research-and-science`. Card count against beat page NOT LOOKED AT.
- /place/: tx-2026-0244 is on `county-brazos`. Hub count NOT LOOKED AT.

## Email

Written at Phase 19.

## Merge

Written at Phase 18.

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 30 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 4 warn(s) |
| aggregates     | PASS   | 8 declaration(s), 13 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 6.49 MB, vector |
| score          | WARN   | 7.266 at the round cap after 4 round(s), the finished deck ships; 8.0 top rung, shortfall named |
| labels         | PASS   | 54 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 64 published string(s) read from one list, every universal names its set |
| verbatim       | WARN   | no dossier declares a `verbatim:` block, so no on-frame string was held to a quote |
| dossiers       | PASS   | 33,171 chars planned |
| caption        | PASS   | 144 words |
| craft floor    | WARN   | 9 frame(s), median 2462, floor 443, 2 quiet |
| plan vs render | PASS   | 9 of 62 acceptance item(s) checkable |
| texan          | WARN   | places College Station / body NO / deadline NO / next step NO |
| absences       | WARN   | 0 of 8 scoped to a named document, 8 unscoped |
| numerals       | PASS   | 25 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
