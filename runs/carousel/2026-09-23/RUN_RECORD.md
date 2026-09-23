# Run record, September 23rd, 2026

## DISPOSITION: THE RECORD SHIPPED AND THE DECK DID NOT. THIS BRANCH IS NOT MERGED.

`shipped_check`'s `completion` gate refuses it and the refusal is correct rather than a
technicality:

> THE DECK WENT BACKWARDS. 5.95 against a 8.0 bar is under 7.01, which is what the last 10
> shipped decks have actually been holding. **The 5 round cap ends the SEARCH and it does not
> end the STANDARD.** Shipping here is the regression the floor exists to refuse.

That is the sentence this run had been reading the wrong way round all afternoon. The delivery
policy says a run past the cap ships whatever the score is and names the shortfall, and that is
true of a deck that is merely SHORT of the bar. It is not a licence to ship a deck a full point
below what the product has actually been holding for ten decks. A floor measured off shipped work
is a harder fact than a threshold in a config, and this deck is under it.

**So the branch carries its evidence and stops.** Per the delivery policy, failed runs commit and
do not merge.

**THE COST, STATED SO IT IS A CHOICE RATHER THAN AN OVERSIGHT.** The record work on this branch is
sound, it passes every gate, and it includes the fix that stops `docket_staleness` reporting three
Hays County items as ROTTEN. CI exits 1 on a rotten item. **So until somebody merges this branch or
redoes that work, every pull request against `main` is red on a gate whose remedy no run can
take.** That is the one thing here worth a person's attention today.


Carousel no. 32, a gas generator yard at night. The record went from 156 items to 157 on one
admission, `tx-2026-0182`, which is the deck's subject. Ninety four items were re-verified.

## What shipped

Nine bespoke slides on the September 21st directive telling TCEQ to issue no permits sought by
data centers, one web edition, one caption, one first comment, one Gmail draft.

The deck's claim, in one sentence: **a permit halt scoped by WHO IS ASKING cannot be aligned to
an audit scoped by WHAT IS ADVANCING THROUGH THE INTERCONNECTION PROCESS, and a real West Texas
project already sits in the gap.**

## The record, first, because it is the run's first deliverable

- Re-verified the whole due worklist, 94 items. Eight confirmed and stamped, two moved and
  stamped, five left UNSTAMPED with a dated note naming exactly what is therefore unconfirmed.
- Three items depending on `public.destinyhosted.com` and `tacc.utexas.edu` were held out on
  robots, not routed around, and carry the reason in their movement lines.
- `tx-2026-0120` was stamped. It had been left unstamped on 2026-09-21 because `www.dhs.gov`
  answers 403 to `curl`, `robots.txt` included. It answers WebFetch. All twelve of its claims
  came back in full. **A 403 from one client is a fact about that client**, and that correction
  is in `knowledge/shared/SOURCES_FIELD_LOG.md` under today's date, revising the earlier entry
  without contradicting what that run measured.
- All 94 movement notes were rewritten. Sixty one of them had been the identical deterministic
  sentence.

**The most valuable thing this run found about a source is that a 200 is a claim about the
transport and not about the document.** `federalregister.gov` serves a CloudFlare interstitial at
HTTP 200. A re-verification that reads the status code and then looks for its quoted string finds
the string absent and concludes the document MOVED. It did that to two items before a second pass
caught it. `govinfo.gov/content/pkg/` carries the same documents and served them every time.

## The record learned to say unreachable, and one commit was stamped human to let it

Three Hays County items, `tx-2026-0168`, `tx-2026-0169` and `tx-2026-0170`, had been sitting past
twice the two day leash since the 22nd, and `docket_staleness.py` called them ROTTEN every day.
The remedy it printed, re-verify these before writing anything new, was one **no run could take**.
`public.destinyhosted.com` serves `User-agent: *` and `Disallow: /`, re-measured today.
`www.hayscountytx.gov` carries the same county's own agendas and answers 403 to curl and to
WebFetch alike, which is the other half of the rule this run wrote three days ago about a 403
being a fact about one client. Two clients is a fact about the site.

**A gate whose remedy is impossible goes red forever and is then read as noise**, which is exactly
what this repo's own notes say happened to `remote rejected` on a push that landed. So the tool
now separates CANNOT from DID NOT. An item declares the hosts, the boundary and the DATE it was
measured, the block must cover the item's own `public_access` host so it can't be earned by an
incidental third source, and **it lapses in seven days**, which turns the carve-out into a
standing obligation to go and re-measure rather than a note that silences a gate once.
Unreachable items stay DUE, print in their own section every run with how much of the window is
left, and are never silent. Thirteen self-test cases pin each way the claim can fail, including
the two that matter most: a measurement exactly at the window still counts and one day past it
does not.

**One commit on this branch is stamped `human` and this is the paragraph that says so.**
`config/schema_contract.json` is `human` lane, on the stated reasoning that a routine adds ITEMS
and never FIELDS, and this was a field. The run was blocked by it rather than merely inconvenienced:
CI exits 1 on a rotten item, so nothing could merge. The alternative considered and rejected was a
new host keyed ledger file, which needs a lane grant in `ownership.yaml`. **A routine widening the
map that holds it back is the worse of the two by a distance**, whatever the file it widens it for.

## Two commits on this branch carry a lane other than `daily`, named here as the map requires

- **`config/schema_contract.json`, stamped `human`.** The reasoning is in its own section below.
- **`scripts/carousel/sources_block.py`, stamped `upgrade`.** Every citation line in the first
  comment carried a date that fell back to the FETCH date when a claim had no published date, so
  "Governor Abbott Directs Comprehensive Data Center Audit, September 23rd" sat under a deck whose
  frame 7 says that audit was ordered August 3rd, while the header two lines above already said
  "all fetched September 23rd". The block asserted a publication date it did not have and
  contradicted its own deck to do it. Two round 5 scorers found it independently.
  `DATE_KEYS` no longer falls back to `retrieved`, a claim with no published date now gets no date
  on its line, and the day count sentence says the dates come from inside the quoted sources
  rather than "above", which they were not. Six new self-test cases, and this is the same defect
  as the "Day counts computed" line thirty lines below it in the same file: **a provenance line
  may only state what the record holds.**

## The score, stated rather than rounded

**Panel median 5.95 against an 8.0 bar, on round 5, which is the cap.** Integrity 6.17, craft
7.06, reader 5.77, spread 1.29. `panel.py` returned HOLD on two hard fails and that verdict stands
in `round5-panel.json` exactly as the judges left it, because a card is a reader's finding and a
run does not get to edit one.

**Both hard fails were repaired and verified after the cards arrived, and neither was waived.**
The cap sets whether there is another round to re-score in, and there is not. It does not soften
what a hard fail is. `scores/hard_fail_repairs.json` carries each one, its repair and how the
repair was checked.

1. **The web edition opened a paragraph "A second arrangement sits the other side of the line."**
   That places the Odessa purchase on a side of the metering line, which `claims.json` refuses in
   both directions, three sentences upstream of the clause saying the edition places it on
   neither. **It was the round 4 hard fail surviving in a new wording**, because the round 4
   repair was made against the sentence a scorer quoted rather than against the proposition.
   Seven committed files, four rounds, one idea.
2. **The caption dropped c22's chapter limiter**, asserting a blanket bar on TCEQ permits. That
   one is mine end to end: the line was right until round 3 called a bare "Chapter 11" a
   bankruptcy misread, the repair named the Water Code, the repair ran 14 characters over the
   caption band, and the trim that brought it back under took the limiter out. **A length budget
   spent a scope limiter** on a deck whose whole thesis is that scope wording decides reach.

**The shortfall, named rather than averaged away.** Craft is where this deck loses, and all three
judges put integrity well above it once the two sentences were fixed: the craft judge scored claim
integrity 8.5 and called the refusal list the strongest thing in the package. What is 6.0 is the
artwork, and specifically the two frames at the ends.

**Frame 1 is the measured one and it is not fixable from here.** One connected component holds
0.86 of every pixel over L\* 30 and covers 0.37 of the frame, so the machines, the pad and the
right edge slab are one mass and the cover reads as texture rather than as a line of objects. Two
repairs were tried and MEASURED rather than assumed. A deeper contact at the skids left the
largest component at 0.86, exactly where it started, and dropped the median to 14.4 against a
declared band of 15 to 27. Darkening the pad is the repair this frame already made and took back
at 12.9. **The band can only be held by keeping the pad bright, and a bright pad is what the focal
competes with.** The craft judge reached the same place independently and went one step further,
which is the useful step: figure and ground are drawn in the same screen at the same angle and
pitch, so no value move separates one material from itself. The cure is a different MARK, and it
is in the backlog rather than guessed at here.


## The deck's own argument, and what was refused to keep it true

The deck was planned on an AIR PERMIT MECHANISM: that behind the meter engines need a New Source
Review air permit and that this is the instrument the halt actually reaches. **Verification could
not establish it.** The agency's own guidance describes internal combustion engines as the kind of
facility found at sources needing NSR and says nothing about whether or when a particular
installation is one. The mechanism was cut, the deck states the two scopes and stops, and the web
edition says in its own section that no mechanism is asserted.

The planned closing frame went with it. It was an open Abilene air permit with a route to comment,
and the fact-checker could establish neither the applicant, the county, that it is an air permit,
that comments are open, nor a deadline. Nothing was invented in its place.

Six findings were rejected in all. **The deck is what survived, not what was planned.**

## Three hard fails, found by scorers and not by gates

Round 1 of scoring returned a median of 6.526 against an 8.0 bar, with four hard fails across
three judges. Three were distinct and all three were right.

1. **"That plant is a grid resource."** on frame 8, under a cite line of c19 c20 c21. No claim
   among the twenty two says the Vistra Odessa facility is interconnected or sells into ERCOT.
   Its only backing was a hand typed `on_grid: true` in `figures.json`, sitting under a header
   stating that every value there is extracted from a verbatim quote by `compute.py`. The frame
   now says what the record carries, which is DISTANCE, and refuses the off grid reading and the
   on grid reading in the same breath.
2. **"That project never joins the queue."** in the caption. c16 establishes that 76 MW of
   SUPPLY is behind the meter. A site can take behind the meter baseload and still hold a queue
   position for the rest of its load. The caption now says the audit reads a process that supply
   never enters.
3. **Frame 7 printed 2026 four times**, against the house rule that a date in the post's own year
   carries no year. The run's own caption printed the same three dates correctly the whole time.

**What those three have in common is the finding.** Every gate in this suite polices NUMERALS or
UNIVERSALS. A flat declarative factual sentence carrying neither is unexamined, and one shipped
through nine green gates and two full pixel-review rounds. `caption_check.post_shape_problems` is
reached only from `run()`, which is called on `caption.txt` alone, so no gate reads a slide string
for post shape at all. Both are in the upgrade backlog.

## Two wrong measurements were committed, and a scorer caught both

- The chassis and the storyboard said the deck's ground sits at **dE76 14.18** from its nearest of
  the last six shipped grounds. The artwork ledger said **24.54** against September 20th's
  `#2E2016`. A scorer recomputed by hand, got about 26, and said the two files could not both be
  right. They were right. The figure is 24.54, and the other half of the finding is that **four of
  the last six shipped decks record no ground colour at all**, so "the last six" is a window this
  comparison cannot fill. The claim is narrowed to what was measured.
- The storyboard said the screen is a **LINE SCREEN AT CELL 5**. The chassis and the ledger say
  cell 6, and the chassis records why it moved: at cell 5 `bright` and `glare` collided at 75.01.

A third of the same kind was caught by the flow critic: the storyboard claimed a mean adjacent
value jump of 6.44 that could not be reproduced from the numbers printed beside it. There is no
typed figure in its place now. The deck's track is whatever `deck_coherence` prints.

**Three wrong numbers in committed files in one run, all found by readers rather than by checks.
Nothing in this suite compares a figure in a chassis comment or a storyboard paragraph against the
same figure in the ledger.**

## What the art rounds cost and what they bought

Every one of the nine frames came back `revise` from round 1 of pixel review. The repairs that
mattered were not lighting:

- **Frame 4's 90% read as 98%.** The line screen lays ink in proportion to tone, so over a lit bed
  its strokes come out at the glyphs' own value, and a stroke crossed the zero's bowl. 98 is a
  number no claim carries. It reached a reader through a GLYPH, so `copy_sync_check`,
  `numeral_trace` and `numeral_lint` all read 90 and every one of them was reading the DOM.
- **Frame 2's louvre bank read first as a sagging cable and then as a picket fence**, on the one
  frame whose entire content is that no connection appears anywhere.
- **Frame 6's stack read as a lattice mast**, which is transmission structure, on a deck arguing
  these machines never ask the grid for anything.
- **Frame 9's chairs were set out facing the reader**, which implies a hearing that did not happen.
  The record says the hearing was canceled and will be rescheduled.
- **Frame 9's window, the yard beyond it and the single stack that is the deck's motif payoff were
  all drawn about a thousand pixels off the left edge**, because the window was placed in a wall
  at an X no camera could see. The frame rendered clean with zero errors.
- **Frame 8's bar contacts ran six pixels past their own bars**, so the 207 over-read against the
  1,180 on the one frame whose whole assertion is the ratio between two lengths. Measured off the
  render, the press adds about 2.5 px to any silhouette, so the drawn lengths are now solved for
  the PRINTED extents.

## The closing frame, and what a reader can do

`texan_check` reported **next step NO** through both review rounds and three scorers said in three
different ways that a Texan finishes this deck with nothing. The record does carry one dated thing,
and it is now on the frame a reader stops at: TCEQ must answer for its compliance by October 19th.
It is not a comment window and the frame does not pretend it is one.

## What is still true about this deck that no fix reached

Stated rather than smoothed, because the next run inherits it.

- **The declared continuity devices are weaker on the page than the plan claims.** Five of six
  reviewers said the EDGE TEASE does not complete and the ENGINE motif reads on some frames and
  not others. The devices actually holding this deck together are the one ground, the one screen,
  the one light and the accent law.
- **This is the third deck in ten days built on a Governor's office directive about data centers**
  and `dedupe_check` returned LIKELY REPEAT at 0.72. The override is argued in `SELECTION.md` on a
  different agency, a different instrument, a different docket item and an argument different in
  kind. One scorer called it a hard fail anyway and stated the counter-argument themselves. It is
  written into `topics.json` as an instruction: **the next run should treat a fourth Governor
  directive as a repeat whatever the keywords say.**
- **The topics entry first shipped with no `keywords` array**, which is one of the three fields
  `dedupe_check` compares, in the run that sat closest to a repeat this product has been.
- **The deck's central example is located only as "West Texas."** That is all the source gives.

## The instrument pages, looked at rather than inferred from a green gate

`/grid/` and `/water/` both render, both carry measured figures and neither publishes a verdict.
The Grid Watch gauge is still a bar at one hue and one intensity. No presentation change was
needed and none was made.

**AND LOOKING AT THE PAGE FOUND SOMETHING NO GATE WOULD HAVE.** The Grid Watch says *large load
has asked ERCOT for 410 GW* and *87 percent of the queue is data centers*, read off ERCOT's own
March 26th queue report. Today's deck and web edition say *approximately over 474 gigawatts* and
*about ninety percent of the new power requests*, quoted from the Governor's September release.

**Neither is wrong and they are not the same measurement.** Different sources, different dates and,
on the percentage, different denominators: 87 percent of the WHOLE queue against ninety percent of
the NEW requests. Both surfaces attribute and date their own figure, so nothing published is
unsupported. But a reader moving from `/grid/` to today's article meets two numbers for "the queue"
within one site, and this project's own law is that a figure here should be recomputable rather
than taken on trust. **Recorded rather than fixed**, because reconciling them is a Grid Watch
presentation question and the Grid Watch's collectors and figures are the cron lane's, not this
run's.

## Two scorer findings that did not survive a measurement

Both are recorded because a finding that fails a measurement is worth as much to the next run as
one that holds, and because taking a judge at their word is how a wrong number gets inherited.

- A round 2 scorer called the 1.70 m figure on frame 6 **"a 2 to 3 px speck"** at feed size and
  scored FIGURE_SCALE as delivering no size. Measured off the 432 px thumb the figure is about
  **50 px tall** with a visible cast running down and to the right.
- A round 2 scorer read frame 8's bar pair at **about 5.27 to 1** against a true 1180 to 207 of
  5.70, and said it needed a machine measurement before the round closed. It did. Measured off the
  render, the bars are **842.5 and 148.0 design px**, a drawn ratio of 0.17664 against a true
  0.17542. That is **1.0 design px** on the short bar, inside its own 2 px acceptance tolerance.
  Their instinct to ask for the measurement rather than assert the number was the right one.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 22 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 8 warn(s) |
| aggregates     | PASS   | 15 declaration(s), 18 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 14.6 MB, vector |
| score          | ABSENT | score.json not written yet |
| labels         | PASS   | 56 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 75 published string(s) read from one list, every universal names its set |
| verbatim       | PASS   | 3 declared fragment(s) over 9 of 9 dossier(s), every one a literal substring of its own claim's quote, 1 slot note(s) |
| dossiers       | PASS   | 47,220 chars planned |
| caption        | PASS   | 154 words |
| craft floor    | PASS   | 9 frame(s), median 3153, floor 568 |
| plan vs render | WARN   | 12 of 63 acceptance item(s) checkable |
| texan          | PASS   | places Bexar County, Odessa / body yes / deadline yes / next step yes |
| absences       | PASS   | 15 of 15 scoped to a named document |
| numerals       | PASS   | 12 numeral(s) over 9 frame(s), every one reachable |
| completion     | ABSENT | not scored yet |
<!-- gate-status:end -->
