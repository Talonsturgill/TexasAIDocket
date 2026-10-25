# Run record, October 25th, 2026

Effort at wake: `high`, as the repo's settings carry it.

**Wake.** Branch `claude/daily-2026-10-25`. `bootstrap.sh` exited 0 and repaired PIL. `docket_build.py --validate`,
`ownership_check.py --self-test` and `arsenal.py --check` exited 0 at wake. The first `guards_local.py --fast --only
Ownership` ran before `bootstrap.sh` and failed its shallow clone step on the container's broken system PIL. That is
the container, not the repository. It was run again after bootstrap.

## The record, first

- **Worklist.** `docket_staleness.py` named 44 items due, none deferred, and exited 2 for items past twice the leash.
  Every one of those rotten items sits behind a measured crawl boundary.
- **Re-verify.** `reverify.py --apply` read 88 urls behind 298 claims. 6 answered 304, 31 sent a body, 13 did not
  answer and 38 were refused by the crawl boundary and never requested. It stamped 5 items unchanged: tx-2026-0137,
  tx-2026-0212, tx-2026-0220, tx-2026-0226 and tx-2026-0227.
- **Confirmed by hand, 4 items.** tx-2026-0099 and tx-2026-0215 on Rice's own pages, which answered `fetch_doc.py`
  though they gave the re-verifier a 406. tx-2026-0223 on the A&M release, where the conference sentence is still on
  the page and was missed only because the page puts a space either side of the linked words. tx-2026-0207 at the A&M
  System story's new address, `tamus.edu/news/2026/10/07/...`, after the old `news.tamus.edu` address answered 404.
  All seven of its claims were re-pointed there.
- **tx-2026-0171 moved.** The Texas Tribune reported on October 14th that the water board says it has no authority to
  prosecute a facility that skips the survey, and that the penalty is a Class C misdemeanor with a fine of up to $500.
  Two claims were added from that page.
- **35 items unconfirmed today**, each with a dated line naming what is unconfirmed. Most rest on newsrooms or county
  sites that bar this project in robots.txt. tx-2026-0203's city notice at taylortx.gov now redirects to a 404 page,
  and the city's robots.txt refuses the redirect target, so its terms rest on CBS Austin's report until another
  primary copy is found.
- **Crawl boundaries.** All 23 legacy boundary declarations were re-measured today and every one held, so their seven
  day windows now run to November 1st. The two claim-source declarations (tx-2026-0044 and tx-2026-0055) were
  measured on October 21st and were not re-measured.
- **Admitted: tx-2026-0231**, UT Austin's $643,719 award to build an AI movement language model, on the university's
  own news item of October 23rd. The ledger holds 203 items.
- **Not admitted: the Attorney General's suit against OpenAI**, filed October 23rd in Collin County district court per
  the Texas Tribune. `texasattorneygeneral.gov` disallows this project in robots.txt and the petition was not
  reachable, so the item rests on journalism alone and stays out until a primary copy is found.
- **A scout fetched a host the record treats as refusing this project.** The policy scout read dir.texas.gov's AI
  sandbox page with WebFetch although the record's boundary for tx-2026-0113 says dir.texas.gov's robots.txt refuses
  this project. Nothing from that page is used anywhere.

## Discoverability signoff

Read on this run's final build in `docs/`, after `main` was merged in (already up to date).

- **Card, tx-2026-0231** (`og/tx-2026-0231.png`, opened as an image). Four lines ending "build an AI model..." with
  the ellipsis after a whole word. Clean.
- **`/questions/`.** The eleven question pages are built (decided or pending, kind of decision, last checked, on the
  ERCOT grid, open comment, sources behind it, taking part, what happens next, what it is, when it started, where in
  Texas). The new item adds no new status or room. Its 42 word summary sentence failed `house_style_check` on
  `questions/what-it-is` and was split in the record and the seed before this build.
- **`llms.txt`, Open right now.** Six entries, among them tx-2026-0145 closing November 9th, tx-2026-0048's November
  3rd election and tx-2026-0220's October 29th vote. None closed today.
- **`/sources/`.** 1,258 of 1,434 claims rest on a primary document, across 368 documents from 161 publishers, up
  from 1,253 of 1,427 yesterday. The new claims came from UT Austin's own news item and ERCOT's and the Tribune's
  pages. The top publisher is still interchange.puc.texas.gov. texastribune.org is third at 56 claims, none primary,
  and today's tx-2026-0171 claims added two of those.
- **`/topic/`.** Research and science carries tx-2026-0231, and its card's 43 decisions equals the 43 item links on
  its page.
- **`/place/`.** `county-travis` and `metro-austin-round-rock-san-marcos` carry tx-2026-0231.

## Craft refresh

Focus: the page skeleton and the lit subject. The last three decks (nos. 57 to 59) were staged spatial scenes, and no.
59's flow critic named nine of nine frames sharing one skeleton. The five findings are in `craft_refresh.md`: alternate
type-led and image-led frames on one grid, carry a fragment across frames, keep a rim-lit subject's interior dark,
keep a touch of context, and avoid cloth.

## Selection

tx-2026-0171, the water use survey, on the Tribune's October 14th count (334 facilities, 233 never returned the
survey, up to $500, no authority to prosecute) against ERCOT's September 14th notice M-B091426-01, which carries the
water board's Section C questions. No water survey or ERCOT RFI deck sits in the 30-day window. The nearest are no. 29
on September 19th, on the same docket item 36 days back, and no. 24, 41 days back. The fact check's four rules held on
every surface: ERCOT is the issuer, never "jointly" and never "the same questions", the 233 are never said to be
covered by the request, and the December 10th report is expected, not existing.

## The deck

Chassis `assets/js/deck/2026-10-25-returnplate.js`, in the lastLight world, key az -62 el 13, with brass #C9B393 as
the one accent, meaning an answer returned. It has two chassis models, `return_plate` (334 threaded bores at 75 mm
pitch, 101 brass hex plugs) and `ground_storage_tank` (60 m by 13.4 m, the volume of the survey's 10 million gallon
line). The art director accepted the three-frame audition (1, 2 and 9). Frame 2's top chamfer was re-reviewed twice,
and frame 9 was re-reviewed after its dek was rewritten.

## Pixel review

Two rounds, on the smaller tier per the 2026-10-02 pin. All nine frames came back revise in round 1, and slide 9
shipped in round 2. The record is `reviews/pixel-r1.md`. The material corrections:

- Slide 9's dek set ERCOT's December 10th report beside "a skipped survey" and implied a link to the 233. It now says
  the report sets out conclusions from ERCOT's own review with the PUC (c25).
- Slide 7's hook "isn't connected yet" overstated c7 and became "isn't energized yet". Its lower labels had read as
  one wrong phrase, and "and larger" was removed.
- Slide 3's "any penalty" was narrowed to c35's "any misdemeanor penalty ... against a data center".
- "The hookup is drawn to illustrate" became "The transformer".

Three critics reported curly apostrophes. Those are the display face's U+0027 glyph, and the source and render
report carry straight quotes.

## Flow critic, one whole-deck pass

Verdict revise, predicted artwork_craft 6.6, showstopper named as frame 4. Its weakest frames, 6, 8 and 7, were
repaired (`reviews/flow.md`). The conductors on 6 struck the type and were removed. The seal on 8 was struck in brass
to carry the motif through the turn. The copper on 7 lost its wood grain. It also found that the skeleton alternation
the storyboard declared was never built, and the storyboard now says so.

## The panel

Three rounds of three judges, integrity, craft and reader, combined by `panel.py`. The cards are in `scores/` and the
repairs between rounds in `reviews/panel_repairs.md`.

| round | judges | median | hard fails |
|---|---|---|---|
| 1 | 6.58, 6.99, 6.87 | 6.92 | 0 |
| 2 | 6.82, 7.23, 6.94 | 7.07 | 0 |
| 3 | 6.99, 7.22, 7.23 | 7.09 | 0 |

**The deck shipped at the round cap with a median of 7.09, 0.91 under the 8.0 top rung and 0.61 under round 2's 7.7.**
The craft floor stood down at the cap with the art median at 6.5, under 8.5.

Between rounds, the frames the judges named twice were recomposed rather than re-rendered. Frame 6 moved from a
padmount to a substation transformer bay. Frame 5 moved from a plan relief to an oblique farm of 140 tank clones.
Frame 3 now looks down at the bores. The integrity lens moved the copy. The request is now bound to the notice's own
set on frame 7 and in the caption. c5 was re-fetched and carries the verbatim "Substantiated Load" quote. The caption
carries c32's "of its own", and frame 8's hook is in the past tense.

What the final round still names, for the next run:
- Frame 8 reads as a safe door or a combination dial, and its sheet sits in the grey middle.
- Frame 6 is grey kit clay with no ground or contact, gantry clutter, and a nameplate square behind the footer's c12.
  Every close crop of the bay struck the type.
- Frame 5's tanks read as pucks on a lit mid-tone floor.
- Frame 3 has a brown haze band behind the hook. Pitching down far enough to lose it also loses the sky, which
  `print_ban` requires.
- Frame 7 reads as a ruler on a rail. The judges' cure is to draw both routes, or an undrilled blank beside the
  drilled plate.
- Frames 6 to 8 leave the plate's iron and brass vocabulary. All three judges named this, and it is the deck's
  composition fault.
- Story and stakes. The deck names no county and gives no action. c33's county and district attorneys are the
  lever it left out.

## Ship

- Artifacts are copied to `runs/carousel/2026-10-25/`.
- `ship_images.py` encoded nine WebP frames, nine thumbs and `og.jpg` at 40.1 to 42.4 dB against a 40.0 floor, 58.49
  MB down to 4.82 MB.
- `art_preflight --archive` bound the delivered images to the accepted review.
- `measure_shipped` wrote `measurements.json`, with a deck median L* of 5.0, and `--check` agrees.
- The ledgers were updated by `update_ledgers.py` and `ledger_check` agrees. The closing move was first labelled
  "ask the one question", which yesterday's run had used. The caption's close asks whether ERCOT's expected report will
  say how many responded, so its substance is "name what happens next and when", and it was relabelled to that.
- `sources_block --build` wrote the first comment: 31 claim ids across three documents, with c5 included. Six claim
  documents were named from the pages' own titles.
- The web edition is `ledger/articles/2026-10-25.json`. `article_check`, `test_article_edition` and the browser suite
  (975 reader checks) pass. Global Playwright was linked into the ignored `node_modules/` so the ESM import resolves.
- `main` was merged in (already up to date) and the site rebuilt. The verify list exited 0 once two house-style faults
  were fixed in their sources. tx-2026-0231's 42 word summary sentence was split. c1's text read "M-B091426-01
  September 14th", which the checker reads as a day-first date in the article's disclosure, and it became
  "M-B091426-01 on September 14th".

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 57 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 4 warn(s) |
| aggregates     | PASS   | 10 declaration(s), 13 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 12.73 MB, vector |
| score          | WARN   | 7.09 at the round cap after 3 round(s), the finished deck ships; 8.0 top rung, shortfall named |
| labels         | PASS   | 74 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 79 published string(s) read from one list, every universal names its set |
| verbatim       | WARN   | no dossier declares a `verbatim:` block, so no on-frame string was held to a quote |
| dossiers       | PASS   | 38,326 chars planned |
| caption        | PASS   | 152 words |
| craft floor    | PASS   | 9 frame(s), median 679, floor 122 |
| plan vs render | WARN   | 7 of 55 acceptance item(s) checkable |
| texan          | WARN   | places Austin / body yes / deadline yes / next step NO |
| absences       | WARN   | 6 of 10 scoped to a named document, 4 unscoped |
| numerals       | PASS   | 25 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->

## Timing

Measured by `studio_clock.py --report`, in minutes from wake at 05:08 UTC: record done 27.0, audition done 94.4, art
done 108.1, review done 168.6, panel done 226.0, package done 258.6.
