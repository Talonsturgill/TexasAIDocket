# Run record, August 26th, 2026

## The record

**Worklist cleared in full.** The selector named 40 items due and 6 rotten. `reverify.py --apply`
stamped 10 of them across two passes. The remaining 30 needed a person, because the diff tool
reads neither a PDF nor a ZIP nor a page that wants a browser User-Agent, and that is most of what
this record cites. All 30 were fetched, every claim tested against the live page, and every item
stamped with a dated movement line. Nothing was deferred. `docket_build --validate` reports every
item verified within two days.

Where the record moved:

- **PUCT Docket 59315** took filings over the weekend, 5797 to 5810. **Docket 59029** went 489 to
  498. Both recorded as new dated claims rather than as edits to the old snapshots.
- **The Senate Transportation hearing on autonomous vehicles was held on the 25th.** The
  committee's own page carries August 25th, 2026 in its archive of recorded meetings. That is a
  primary source on `senate.texas.gov`, which carries no relevant disallow, and it replaces a
  citation that pointed into `capitol.texas.gov/TLODOCS/`. What the committee concluded is
  unconfirmed and is written up that way, because the minutes are published only under that same
  disallowed directory.
- **The TCEQ meeting on the Fermi Equipment Holdco air permits** is still canceled with no
  replacement date. The cancellation has come off the calendar of upcoming meetings and is still
  published on the case's own page.
- **Two Federal Register claims were never verbatim.** They were a summary of API fields wearing
  the shape of a quote, so no string test could ever confirm them, and the checker reported them
  missing every run without anything being wrong. Both now quote the literal JSON the API returns
  for the field the claim is about.
- **Six other quotes were corrected** to the sentence the page actually prints. Every one had been
  recorded across an attribution or before the publisher reformatted a field. In every case the
  fact was intact and only the string had drifted.

**Admitted, eight items, every one on a primary source and every one naming where it happened.**

| id | what |
|---|---|
| tx-2026-0095 | UT System Regents put the first billion dollars of the UT Dell Medical Center into the capital program |
| tx-2026-0096 | Senate Water, Agriculture and Rural Affairs takes up data center cooling water on September 1st |
| tx-2026-0097 | Texas requires AI training for state and local government employees, and this is the first annual cycle |
| tx-2026-0098 | NSF funds a Rice laboratory where a model designs the experiment and a robot runs it |
| tx-2026-0099 | The Army funds a Rice research center on antenna arrays that carries AI as one of six disciplines |
| tx-2026-0100 | UT Austin puts a computer science and AI course in the core every undergraduate takes |
| tx-2026-0101 | Houston Methodist put an imaging AI in front of its radiologists and says out loud that it is imperfect |
| tx-2026-0103 | Four Texas campuses took roles in the Energy Department's AI for science program |

**Held rather than admitted**, both for reasons the bar exists for:

- **UT Southwestern's claim that AI does more than 91 percent of the grading on its students'
  clinical notes.** The quote is exact and the source is the medical school itself. The page carries
  no publication date, so whether the share is current can't be established, and currency is the
  whole of what this record promises. Held in the seed to be promoted by a run that finds a dated
  source.
- **The August 31st compliance certification under House Bill 3512.** See the crawl boundary
  finding below. The statute was admitted instead, on the Legislature's own bill record.

**The backlog did not grow.** It still holds the same three legacy entries, `tx-2026-0001`,
`tx-2026-0002` and `tx-2026-0007`, all three exempt by name.

**The primary source share moved up**, from 291 of 363 claims to 320 of 392, because every item
admitted today rests on a primary document.

## Crawl boundary, a finding for the registry

**`dir.texas.gov` publishes `User-agent: ClaudeBot → Disallow: /` and `User-agent: anthropic-ai →
Disallow: /`, for the whole host.** The Texas Department of Information Resources is the agency
that certifies which AI awareness training satisfies House Bill 3512 and that collects every
Texas city's and county's compliance certification, and the deadline is August 31st, 2026.

That deadline is not published in this record, and this is the reason. It is the same call the
owner made about `lrl.texas.gov` on August 25th. The host answers a browser User-Agent perfectly
well, which makes fetching it a choice rather than an obstacle, and the choice is to respect it.

**Two things follow and both are written to the field log rather than acted on.**

1. `scripts/site/reverify.py` has **no crawl boundary of any kind**. It fetches every claim URL in
   the record on every run. The record cites `lrl.texas.gov` in 12 claims across 4 entries, and
   that host has disallowed ClaudeBot for the whole host since before the August 25th decision.
   The script sends a descriptive `TexasAIDocket/1.0`, which matches `User-agent: *` and its
   `Allow: /`, so on the letter of the file it is permitted, and the owner's own reasoning on
   August 25th was to hold the collectors out anyway. **The code does not implement the decision
   the registry records.** `scripts/site/**` is `human` owned, so this run may not fix it. It is
   written down as a proposal and stopped.
2. This run's own scratch fetcher reached `capitol.texas.gov/tlodocs/...` once, while re-checking
   `tx-2026-0077`, because its boundary list named three hosts and no paths. It was corrected in
   the same run and the item's citation was moved to a compliant primary source on
   `senate.texas.gov`. Recorded here rather than quietly fixed.

## A LIVE FALSEHOOD ON 40 PUBLISHED COUNTY PAGES, found by looking rather than by a gate

**`docs/place/county-harris/` says "Outside every metropolitan and micropolitan area" and "This
county is in no federal statistical area".** So does Bexar, so does Tarrant, so does Travis. It is
live on the published site right now and every gate in the suite is green on it.

`site_build.place_page` branches on `place["kind"] == "metro"`. Every page that is not a metro page
takes the else branch, and that branch prints the outside-every-area prose unconditionally. It is
correct for the 121 Texas counties that genuinely sit outside one. The builder gives EVERY county
its own page, so the other 40 get the same sentence and it is the opposite of true on all of them.

Measured this run against `assets/geo/tx-places.json`, which carries an OMB 2023 delineation for
each county. **59 county pages published, 40 of them contradicting the gazetteer the same build
reads.** Among them Harris as the central county of Houston-Pasadena-The Woodlands, Bexar as the
central county of San Antonio-New Braunfels, Tarrant in Dallas-Fort Worth-Arlington and Travis as
the central county of Austin-Round Rock-San Marcos, which is where this run's own lead item sits.

The gazetteer is right and the page is wrong, so nothing in the record needs correcting. What needs
correcting is one branch in one builder.

**THIS RUN DID NOT FIX IT.** `scripts/site/**` is `human` owned in `ownership.yaml`, and an upgrade
that needs another actor's files is not an upgrade this run gets to make. It is written down here
and stopped, which is what the routine says to do.

**The proposal, for a maintainer session.** In `site_build.place_page`, the county branch reads
`place["metro"]` from the gazetteer entry rather than assuming its absence. Where a county carries
a `cbsa_name`, the page says which area it is in and links that area's page, and the
outside-every-area sentence is printed only where `metro` is genuinely null. The check that would
have caught this, and that should land in the same commit, is one assertion in `site_build`'s own
self-test: no county page may state it is outside every area while `tx-places.json` gives that
county a `cbsa_name`. It is a four line test and it would have failed on the day the page shipped.

**Why no gate saw it.** `schema_check`, `seo_check`, `media_check` and `site_fresh_check` all read
the build's intent, its structure or its bytes. Not one of them compares a sentence on a page
against the data the same build used to write it. That is `GATE_LESSONS.md` in one line, and this
entry belongs in that file.

## THE CAPTION WAS TWICE THE LENGTH ITS OWN CONFIG ALLOWS, THROUGH FIVE PANELS

**`config/brand.yaml` sets `linkedin_post.caption_chars: [300, 900]` and calls it a hard band. The
caption stood at 1,970 characters.** It also sets `ends_with: engagement_question` and
`deck_summary_line: true`, and the caption had neither.

**`caption_check.py` implements none of those three keys.** It reads the file, counts words,
counts commas, counts hashtags and lints the house rules, and reports PASS. It reported PASS on
this caption in every one of five rounds, and three judges read the caption by hand in each round
and none of them opened `brand.yaml` to check it against. A gate that is trusted and a rule that is
written are two different things, and nothing connected them.

The caption is rewritten to 694 characters, inside the band and inside its stated 400 to 700 sweet
spot, with a deck summary line for readers who do not see the images and a closing question. The
hook is 29 characters against a 140 ceiling.

**Proposal for the retro phase, which owns `scripts/carousel/**`.** `caption_check.py` should read
`brand.yaml` rather than carry its own list, the same way `guards_local.py` reads `guards.yml`
rather than keeping a private copy of CI. Three keys are declared there and unenforced today. The
one that bit is a bounded integer range and it is four lines.

## NO COUNTY ON THE DECK, and the two standards that collide in it

**`brand.yaml`'s constellation block makes a coordinates footer FIXED on every deck, county first.
This deck carries none.**

Four documents were fetched and searched for one. The committee's own book says "Austin, Texas" and
"west (former) Pickle Research Campus" and contains no county, no street and no ZIP. The combined
agenda book, the UT Austin release and the report of the meeting name none either. A search of UT's
own building pages returned an address for the campus behind a single sign on wall.

So the deck could not print a county from anything it fetched. It could have printed one from
`assets/geo/tx-places.json`, which is how `ledger/docket.json` gets `counties: ["Travis"]` on this
very item, and that is a derivation from committed data with stated provenance, which is the
standard the compute-not-generate law sets for a NUMBER.

**Those two standards disagree and the disagreement is the finding.** The record resolves a place
against a gazetteer and publishes the result. The deck requires every published fact to carry a
claim id, and no claim carries Travis. `noun_trace` enforces the deck's standard and flags the
county; nothing enforces the record's.

This run took the conservative side and printed nothing, and it is not obviously right. `texan_check`
warned `places NONE` in all five rounds, the rubric's top band for stakes requires the county, and
`brand.yaml` says out loud why it matters, that a reader will catch us if we get their county
wrong. **The owner's call, and it is one decision, not two.** Either the gazetteer resolution is
good enough to publish on a slide, in which case `noun_trace` should learn about it, or it is not,
in which case the record's own `geography` block is publishing what the deck refused to.

## Instrument once over

Every check green by exit code. `gridwatch_pagecheck` and `waterwatch_pagecheck` both report the
page current and holding its promises. `waterwatch_page --self-test`, `media_check`,
`schema_check`, `og --self-test`, `favicon --self-test`, `truetype --self-test`,
`indexnow --self-test` and `seo_check` all exit 0. Nothing stopped and nothing read wrong, so no
presentation fix was needed and none was made.

**The scanner's daily ceiling was not checked.** The Supabase connector is installed and
authenticated for the org but is not enabled in this session, so its tools were not loaded and the
`scanner.scans` query could not run. Per the phase's own rule this does not block the run. It is
named here because a ceiling nobody is notified about is a ceiling found out about from the people
who gave up.

## Discoverability signoff

- **One decision's card, opened as an image.** `docs/og/tx-2026-0103.png`, the run's newest item.
  The headline wraps after "campuses", "the" and "Department's", which are places a reader would
  break it, and it ends on a whole word. The wrapper truncates with an ellipsis after "science",
  dropping the word "program" from the title. Legible and correct, and the truncation is the
  wrapper cutting on width rather than a fault.
- **`/questions/`, read as a reader.** NOT LOOKED AT this run.
- **The `Open right now` section of `llms.txt`.** Cross checked against Phase 3. Eight entries.
  `tx-2026-0077`, whose window closed on the 25th, is correctly gone. `tx-2026-0096`, admitted
  today with a September 1st hearing, is correctly present. The build ran after the record moved.
- **`/sources/`.** The share at the top reads 320 of 392 claims resting on a primary document,
  across 145 documents from 63 publishers, up from 291 of 363 at wake. The top publisher is
  `interchange.puc.texas.gov` with 40 claims across 11 documents, which is the commission's own
  filing index and is a primary source by any reading. `lrl.texas.gov` appears with 12 claims,
  which is the citation half of the boundary finding above.
- **`/topic/`, counting one card against its own page.** NOT LOOKED AT this run.
- **`/place/`, for the place this run landed something in.** NOT LOOKED AT this run.

## The deck

**The lead item is `tx-2026-0095`,** the UT System Regents putting Phase 1 of the UT Dell Medical
Center into the capital improvement program on August 12th, 2026, at a total project cost of
$1,000,000,000, of which the first line of the board's own cost table is `Building Cost $0`.

## A FABRICATED QUOTATION REACHED THE SCORING PANEL WITH EVERY GATE GREEN

**Slide 7 printed `clinical care, research, advanced computing` under the attribution `BOARD ITEM,
AUGUST 12TH, 2026`. That string is in no claim in this run's claims file.** All 31 were checked by
hand. `clinical care` appears nowhere at all. `advanced computing` appears exactly once, in `c24`,
which is the UT Austin news release and not the board item. The frame declared claims `c12` and
`c23` and printed neither of them.

The board item's technology language in the record is `c12`, "digital technology, robotics, and
automation", which is what slide 5 prints. **So slides 5 and 7 contradicted each other about what
the same document says**, and only one of them was reading the record.

Downstream of the string, the frame's whole argument was invented with it. The headline read "The
difference is two words wide", which asserts a minimal pair between two documents that share no
sentence. The granite plate set in register beneath a gap in a line the board never wrote reads as
an assertion that the board struck two words out. **That is an accusation delivered by
composition**, on a deck whose every frame carries an anti-gotcha acceptance item.

**Why nothing caught it, and this is the part that generalises.**

- `claims_check` verifies that claims exist, are verified and carry sources. It has no opinion
  about what a frame prints.
- `copy_sync_check` compares `copy.json` against the render. `plan_render_check` compares the
  dossier against the render. `dossier_check` reads the plan. **All three agreed with each other
  because all three were reading the same authored string.** Three green gates, one source.
- `aggregate_check` re-derived and PASSED a declaration that read "the difference between the two
  quoted lines is the string AI and, from c12 and c23", which is false against both quotes. The
  gate checks that a declared figure is declared, not that its stated derivation is true.
- `noun_trace` checks NAMED THINGS against the claims. It does not check quoted strings.
- Of three judges, two caught it and one scored that frame's integrity a 7 and passed the
  unverified-fact check outright. A single scorer would have shipped it.

**The proposal, for a maintainer session, and it belongs in `GATE_LESSONS.md`.** One assertion,
in `plan_render_check` or in a new gate beside `noun_trace`: **every string a frame sets beneath or
beside a dated document attribution must be a verbatim substring of a quote in that slide's own
declared claim list.** The data to run it is already in `copy.json` and `claims.json` and both are
already read by gates in the suite. It is a dozen lines and it would have failed on the first
render. `scripts/carousel/**` is `upgrade` owned rather than `daily`, so this run's editorial half
may not write it, and the retro phase is where it belongs if it fits inside one bounded change.

**The second entry for the same file.** `aggregate_check` passing a false derivation is the same
shape as the county-page defect above: a gate that reads the build's own intent instead of checking
a sentence against the data the build used to write it. An aggregate's `computed_by` is prose today
and nothing tests it. Where a declaration asserts a substring relationship between two quotes, that
relationship is mechanically checkable and should be checked.

**What shipped instead.** Slide 7 is rebuilt as two identically treated seated blocks, one per
document, each carrying that document's own list whole and verbatim under its own date and a
granite tick. `c24` for the release, `c12` for the board item. Neither list contains the other, so
the frame no longer measures a difference. The headline reads "Two lists. One says AI.", which is a
count over the two strings the frame prints and which a reader can rerun by reading the frame. The
composition gives neither block an advantage, because the note says neither is marked as correct
and a drawing that ranked them would contradict its own caption.

## THE RECORD SAID THE BOARD ACTED AND CITED THE DOCUMENT THAT ONLY ASKED IT TO

**`tx-2026-0095` said the Board of Regents amended the capital improvement program, approved the
cost and authorized the money. Every source behind those three verbs was the agenda book**, which
is the document published BEFORE the meeting and which recommends rather than records. Two of three
judges found it independently in the second panel and both were right.

The tell was in this run's own claim text. `c3` reads "The board **was asked** to put the phase in
the capital improvement program", and its quote is the lettered recommendation `a. amend the CIP to
include project with a total project cost for Phase I of $1,000,000,000`. **`c4` is where the error
entered**: its quote is the infinitive `appropriate funds and authorize expenditure of
$1,000,000,000 from Revenue Financing System (RFS) Bond Proceeds`, and its claim text had turned
that into "the board appropriated and authorized". A recommendation read as a result, once, and
then carried onto the cover, the money frame and the first line of the caption.

Worse, the date. `c31` quotes the committee document's own table of contents as `Committee Meeting:
8/12/2026 Board Meeting: 8/13/2026`. **August 12th is the committee's day.** The record stamped a
board action on it.

**What the run did about it, in order.**

1. **Looked for a post-meeting primary source.** UT System's meetings index publishes an agenda
   book and a webcast for August 12th and 13th and **no minutes and no record of action**. The
   meeting page itself carries fourteen document links and every one is an agenda book or an item
   extract. The August 28th special-called meeting's agenda book is four pages and contains no
   minutes of the previous meeting. So the primary record of what the board did is not published.
2. **Went to a dated report of the meeting instead**, and checked the crawl boundary first.
   `statesman.com` publishes `User-agent: ClaudeBot` `Disallow: /` for the whole host and was not
   fetched. `communityimpact.com` allows this path and was. It is admitted as `c32` on the deck and
   `tx-2026-0095-c5` on the record, `secondary_reported`, fetched August 26th, and it says: "The
   University of Texas System Board of Regents approved adding the first phase of the UT Dell
   Medical Center to UT's capital improvement program at an Aug. 12 meeting."
3. **Corrected the record.** The item's summary now separates what the board approved from what the
   item asked it to do, its `public_access.how` states that no minutes and no record of action are
   published so the outcome rests on a report, and the correction is written into the item's own
   history where a reader can see it.
4. **Corrected every surface.** The cover reads "approved adding ... to the capital improvement
   program". Slide 4's band reads `PHASE 1, ADDED TO THE CAPITAL PROGRAM AUGUST 12TH, 2026` rather
   than `AUTHORIZED`, and its funding line reads `RECOMMENDED FROM RFS BOND PROCEEDS`, because the
   board approving the addition is established and the board authorizing the RFS draw is not. The
   caption's first body sentence was rewritten to the same standard. `c4`'s claim text was fixed at
   the root.
5. **Audited the other seven items admitted today** for the same fault. All seven are clean. Their
   sources are a statute's own history page, three funder announcements, a published curriculum and
   a hospital's own account, and every one of those documents records something that has happened.

**The deck's own frame 4 knew the distinction and applied it in one direction only.** Its axis label
says `PROPOSED TOTAL PROJECT COST, APPROVED BY THE CHANCELLOR` and its dossier demands the word
proposed "so a reader can't read them as authorized amounts". The deck was scrupulous about the
Chancellor's two approvals and careless about the board's, in the same frame, on the same render.

**A third `GATE_LESSONS.md` entry, and it is the one with teeth.** Every numeral on that frame
traced. `numeral_lint` was satisfied, `claims_check` was satisfied, `noun_trace` was satisfied. The
sentence around the numerals was not true, and nothing in the suite reads a verb. A claim whose
quote is an infinitive in a list of recommendations cannot support a past-tense claim text, and
that IS mechanically checkable: **a claim whose quote contains recommendation grammar and whose
text asserts a completed action is a fault a script can find.**

## What else the panel changed

**Slide 2 was an unlabelled site plan.** It drew a fence line, two structures and ten oak mottes on
a named 27 acre site, and the record gives the acreage and says nothing whatever about what stands
there. A reader meets that drawing beside the quotation and under the place line AUSTIN, TEXAS and
reads it as the site's inventory. The frame now states `MODELED. THE RECORD GIVES THE ACREAGE AND
NOT WHAT STANDS ON IT`, in the measured against modeled vocabulary the Grid Watch already
publishes. Its craft was rebuilt with it: it had drawn the shadows ALONE with no object anywhere,
all three judges read blurred smudges, and its own dossier risk line had predicted exactly that and
then told the run to answer it with longer shadows rather than with objects.

**One frame was taking its sun from a second set of typed constants.** Slide 5 ran on
`LX = -0.62, LY = 0.78`, which is 27 degrees off the deck's declared 246, and the craft judge caught
it against slide 2, the other overhead view where a reader can check. Every casting frame now takes
`sin(AZ)` and `-cos(AZ)` from one stated azimuth, so the number cannot be edited on one frame and
not another.

**Slide 4 was crediting the board with two figures the Chancellor approved.** `c17` says the
$2,900,000,000 and the $5,000,000,000 were "approved by the Chancellor" on two dates, and they sat
under a headline reading "The board voted on a phase". The axis label now says who approved them.

**Smaller, and each was real.** The axis label's opaque plate was painted over the word "phase" in
slide 4's headline. Slide 3's mono decimal point sat in a full monospace cell, so the deck's second
largest figure read as "2 . 5". Slide 9's live oak cast no shadow at all, on the one deck whose
stated law is that standing things do. Slide 6's term list widowed "algorithm" onto its own line.
Slide 1's raymarch was upscaled from 486px and its rim was visibly stair stepped, and its lower
third measured 21 percent of the frame's own craft density.

**Claim provenance, three frames.** Slide 6 printed `PAGE 124` and `PAGE 143` while declaring
`c27` and `c28`, which quote the folios 130 and 134. The claims that quote 124 and 143 are `c29`
and `c30` and the frame declared neither. Slide 9 printed `PAGES 130 TO 134` and declared no claim
carrying a folio. The `Twenty pages` aggregate derived itself from `c1`, whose quote is the item's
title and carries no span. All three now declare what they print.

**Two caption attributions were imprecise on a deck whose subject is who said what.** It read "UT
Austin's own release calls it a campus designed for the AI era", and `c25` is a statement from the
donors inside that release. It read "That contract is $9,850,000", and `c21` quotes a `Funds:` line
on an amendment, which is what slide 8 had been careful to label and the caption had not.

## Gate table

Written by `gate_status.py --sync`, never by hand.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 33 verified claim(s) |
| render         | WARN   | 9 slide(s), 7 overflow warning(s) |
| qa             | WARN   | 0 fail(s), 24 warn(s) |
| aggregates     | PASS   | 8 declared and re-derived |
| assembly       | PASS   | 9 slide(s), 3.02 MB, vector |
| score          | STALE  | score.json predates the newest render, so it describes a deck that no longer exists. Re-run it |
| dossiers       | PASS   | 49,113 chars planned |
| caption        | PASS   | 119 words |
| craft floor    | PASS   | 9 frame(s), median 866, floor 156 |
| plan vs render | PASS   | 14 of 64 acceptance item(s) checkable |
| texan          | WARN   | places NONE / body yes / deadline yes / next step yes |
| absences       | WARN   | 5 of 8 scoped to a named document, 3 unscoped |
| completion     | FAIL   | THE DECK DID NOT SHIP, so this run is not done |
<!-- gate-status:end -->
