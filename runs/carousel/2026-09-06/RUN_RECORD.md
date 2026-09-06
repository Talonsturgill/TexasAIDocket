# Run record, 2026-09-06, carousel no. 17

Branch `claude/daily-2026-09-06`. One run, two deliverables, the record first.

## Phase 0, wake

Clean checkout off `origin/main` at `331f7e0a`. Hooks wired to `.githooks` and identity set to
the owner, both of which a clone does not carry. `guards_local.py --fast --only Ownership`
exited 0, which is what proves the hooks are actually in force rather than merely present.
`docket_build.py --validate` exited 0 with one WARN block naming eight items due for a
re-check, and `ownership_check.py --self-test` passed all cases. No gate was red at wake, so
nothing was inherited from the last run.

No `prompts/NEXT_RUN.md` existed. No `out/<date>/run_state.json` existed, so this is a fresh
container rather than a resumed run.

## Phase 1, craft refresh

One rotating focus, chosen because the last two runs already spent theirs on legibility at feed
scale and on drawing an absence. **The sequence rather than the frame.** Two findings were
handed to the directors room.

An image in a sequence takes its value from the one before it and the one after it, so a break
in rhythm only reads as a break when the rhythm around it is strong enough to be broken. That is
the argument for planning the value arc across all nine frames before any single frame is coded,
and for spending exactly one inversion rather than three.

The second is about where a reader actually leaves. Engagement falls after the third slide and
recovers at the eighth, and the transition from slide one to slide two is the highest friction
point in the whole deck. So the middle is where a deck is lost, the turn belongs there, and the
debt slide 1 leaves is the most expensive sentence in the deck to get wrong.

## Phase 2, the worklist

```
docket staleness  2026-09-06  leash 2d, no cap  of 108 item(s)
  11 due today
```

Eleven due, nothing rotten, nothing deferred. No `--budget` was passed and none exists.

## Phase 3, re-verify

`reverify.py --today 2026-09-06 --apply` read 23 urls behind 58 claims. None answered 304 and
all 23 sent a body. Seven items came back unchanged on every claim and were stamped.

**The seven deterministic notes were re-worded, which is the part of this phase a machine should
not keep.** A reader opening seven items in a row would otherwise meet the same sentence seven
times. `reverify.py --check-notes` exited 0 over 330 checked notes, so no figure entered a
re-worded note that was not already in the deterministic line or in the item's own quotes.

**Four items the diff structurally could not read were fetched by hand**, and all four stand.

- **tx-2026-0016.** The Federal Register's own HTML now 302s to an unblock page for this client.
  The notice's abstract and its closing date were confirmed from the agency's keyless JSON
  document service instead, which returned the same wording character for character.
- **tx-2026-0036.** The Seguin paper answers 200 at 370 KB and serves the headline, the photo
  credit and no article body, which is a subscription wall wearing a success code. The San
  Antonio station still carries the corroborating account and it was confirmed. The sheriff's
  own words on cost stay unconfirmed and the item now says so.
- **tx-2026-0038.** The board's minutes are a PDF, which the checker cannot read. It was pulled
  with `curl` into `out/2026-09-06/tmp/` and read with `pypdf`, and **all five claims stand.**
  Four of them failed a naive string test and every one of those failures was a curly apostrophe,
  a doubled space inside `effluent  water`, or a tab run in the vote line. Nothing had moved.
- **tx-2026-0046.** The station's page opened this run after the 2026-09-05 run recorded it
  walled. Every claim confirmed.

**The backlog did not grow.** Three legacy entries at wake, the same three at ship, and they are
the three named exemptions that predate the geography rule.

## Phase 4 and 5, discover and admit

Five scouts, three of them on application beats as required: `ai-in-the-field`,
`clinic-and-classroom`, `what-texas-makes`, `policy-and-money`, `power-and-compute`.

**Phase 4's first and highest value poll did not happen.** All three Public Utility Commission
hosts returned 503 for the whole run, the calendar RSS included. The 2026-09-04 field log entry
said in as many words that a 503 here on a day the worklist needed a docket sweep would cost a
run its record work, and this is that day. A reported Commission vote on the first two 765 kV
lines of the Permian Basin Reliability Plan was dropped for want of any fetchable primary
document. There is no second source for a Texas utility docket.

Four items were admitted, 108 to 112. **Every quote in all four was fetched and read by this
run rather than taken from a scout's report.**

| id | what | where |
|---|---|---|
| tx-2026-0125 | The Education Freedom Accounts checklist, four requirements, read against a school that says an AI tutor delivers its coursework | statewide |
| tx-2026-0126 | ERCOT's Batch Zero conditional classifications, issued September 3rd | statewide, on ERCOT |
| tx-2026-0127 | The state technology agency's account of carrying out the four AI laws of the 89th Legislature | statewide |
| tx-2026-0128 | Tesla's Austin Semiconductor Fab registration with the licensing department | Travis |

**All four were HELD on the first pass and the gate was right every time.** Two carried a
`last_verified` stamp with no movement line beside it. One put a notice identifier in reader copy
that no claim quote carried. One ran the comma ceiling by 0.14 per hundred words and was fixed by
splitting sentences rather than by deleting commas. Sixteen further candidates stay in the seed
with their reasons, which costs nothing and loses nothing.

**The Tesla item is the one worth naming for a reason that is not the company.** The licensing
department's project record carries its own County field, so `Travis` came off the document
rather than off the address, which is the thing the geography rule exists to prevent.

## Phase 7, instrument once over

Every check exited 0.

```
gridwatch_pagecheck  0     media_check   0     og --self-test        0
waterwatch_pagecheck 0     schema_check  0     favicon --self-test   0
waterwatch --self-test 0   seo_check     0     truetype --self-test  0
                                                indexnow --self-test  0
```

No instrument has stopped and no page is reading wrong, so nothing was edited in
`gridwatch_page.py` or `waterwatch_page.py` and nothing needed to be.

**The scanner's daily ceiling could not be read.** No Supabase connector is available to this
session, so the query in Phase 7 did not run. Per that phase's own third outcome this is a thing
to say and not a thing to block on. Nobody is notified when that cap is hit, so it stays unread
until a session with the connector runs.

### Discoverability signoff

- **One decision's card, opened as an image.** `docs/og/tx-2026-0124.png`. The headline wraps
  `Energy Department / research arm funds a / Houston led team / using AI to search...` and
  every break lands between words. The truncation ends on a whole word before the ellipsis
  rather than on a stump. Looked at, correct.
- **`/questions/`, read as a reader.** Twelve shapes, all of them questions a Texan would type.
  `Where a comment window is open` reads 07 against 108 on the others, which is the honest
  ratio rather than a fault. Looked at, correct.
- **The `Open right now` section of `llms.txt`.** Four decisions listed, and they are the same
  four the beat pages count as open. Two close September 8th and both were re-verified this run
  as still open. Nothing closed today is still listed, so the build did not run ahead of the
  record.
- **`/sources/`, the record's own report card.** The share reads **500 of 578 claims resting on
  a primary document, across 196 documents from 87 publishers.** The 2026-09-05 run recorded 490
  of 568. **The share moved up, from 86.27 to 86.51 percent**, because every claim admitted this
  run except the reporting on the deck's own story cites a filing, a notice or an agency page.
  The top publisher is `interchange.puc.texas.gov`, the Commission's filing interchange, which is
  a primary source by construction, and second is `api.nsf.gov`. Nothing near the top of that
  list would embarrass the promise the page makes. The quoted material exemption is still
  covering quotations and not our own sentences.
- **`/topic/`, one card against its own page.** Research and science reads 19 on the hub card
  and the beat page lists 19 distinct items. The eight beat counts sum to 108, which is what the
  front page counter printed before this run's admissions. The `still open to comment` figures
  sum to 4 and the front page prints `04 Doors open to you`.
- **`/place/`, for the place this run landed something in.** Travis County is on the hub, its
  page says 16 items in the record, and 16 distinct item links are on it. The Tesla registration
  landed and the hub knows about it.

### Then the pages themselves

- **The water map's pins against the day's reservoir count.** The map draws 119 circles carrying
  the hit class and the readout says `Reservoirs 119`. The map is not one lake short.
- **The front page counter row.** `16 Articles written`, `04 Videos published`,
  `108 Decisions tracked`, `578 Sources cited`, `04 Doors open to you`. Sources cited is
  rendering, which is the one on that row worth protecting.
- **The `backlog:` lines.** Three at wake, three at ship, and they are the same three.

## Phase 8, selection, and why this story and not the others

The run had five strong candidates. ERCOT's Batch Zero classifications, Tesla's semiconductor
filing, the state technology agency's four AI laws, Apple's Houston AI server line, and this.

**This one, because it is the only one where a Texan is the subject rather than the audience.**
The others are decisions about infrastructure. This is a decision about who is allowed to teach
somebody's child on public money, and the answer turns on a four line checklist.

`dedupe_check` returned nothing at the repeat threshold. Its loudest entry was 0.21 and faint,
and reading the full entry rather than its title is what made it matter.

**It named Houston ISD's Future 2 model, which this account shipped as its own deck on August
18th, nineteen days ago and inside the window.** The candidate story had a Houston ISD half and
that half is now cut entirely rather than reframed. The gate did exactly the job the sibling
product's near miss put it there for.

**The ledger's own advice notes then changed the shape of the deck.** Three of them say the same
thing in three different runs. Four of eleven decks have opened on what a document does not say,
the absence hook has become the house habit rather than a choice, and the next run should pick a
story where something happened. The first draft of this deck was an absence at its spine, which
would have been the fifth. So the spine is now two dated events, a board that refused and a
program that accepted, and the absence gets exactly one frame in the middle where it lands
hardest.

`texan_check` at selection reported no Texas place and no next step, which is a brief to the
directors room rather than a fault. The ten town names are in the claims file and the closing
frame carries the next step.

## Phase 9, the directors room

Three lenses pitched. **Threshold and admission at architectural scale, in daylight** was taken
whole and is the spine. Two lawful routes drawn as two built openings in one wall, and the
argument needs no adjectives because a reader can see which opening has a stop and a strike
milled into it.

**The two that lost each gave something up, and each named its own fault first.** The measured
day drew the difference as periodicity and lit every frame by a sun computed for a printed clock
time. It is the more beautiful idea and it puts nine chances to be caught wrong on nine frames,
because a Texan knows what eight in the morning in September looks like. Ground and population
drew the state as a body of Blackland clay and descended to a hand's width of soil, and its own
author named the fault, which is that its frame 3 answers an agenda line with an invented
concrete monument.

**Four grafts, two from the winner's self-critique and two from the lenses that lost.**

- Its frame 3 was a plate with words on it, one step from the label-chip defect two earlier decks
  were marked down for. The letters are now recessed into cast bronze with the deck's one sun
  raking across the cut walls.
- Its frame 5 carried the counter-image on a drawing convention most readers have never met. The
  isolux plot stayed and the frame's own script now asserts a minimum contour spacing. **That
  assertion fired on the first render at 2.2 px and refused the frame**, which is the gate
  working rather than a gate being passed.
- **A place is a boundary or a name, and never a dot**, taken whole from the ground lens because
  it is sharper than the rule it replaced. Ten dots is a count drawn in ink and this deck may not
  print a campus count.
- Frame 3 carries its guard on its own face rather than only in the plan, reading "The line is an
  update on an application cycle. It names no applicant."

`dossier_check` passed after one repair. Slide 3's bottom band named only flat furniture, which
is the dead lower zone stated aloud, and the plan was fixed rather than the gate.

## Phase 10, the caption room

Two directors wrote, the critic judged, and it disqualified candidate B four ways before taste
entered. **The one worth naming is that B counted "two applicants" off a page rather than from
code**, which is this project's central law, and the storyboard's own slide 4 shows the
discipline it ignored.

**Both candidates shared one hard gate failure and neither had been through the linter.**
`caption_check.NUM_RANGE` reads "the 2026-27 school year" as a range and wants it written X to Y.
The critic cut the clause rather than expanding it, because writing 2027 would put a numeral in
published copy that appears in neither the claims file nor `computed.json`.

**One further cut was made after the critic.** It flagged that "elected" rests on a claim's own
summary field rather than on any fetched string. Two State Board of Education pages were fetched
to source it and neither says it, so the word came out. The record's rule is get the quote or cut
it, and this is the cheap end of that rule.

`caption_check` exits 0 at 135 words, zero writer-chosen commas, three niche tags.

## Phases 11 to 14b, the art

Nine bespoke frames, one canvas each at a 2x backing store with the type in the DOM above it.

**The gates found real defects and every one of them was a measurement rather than a taste call.**

- `qa.py` failed six frames for a DRAWN RULE running through a glyph band, which at feed width
  reads as a strikethrough. Every one was a real edge doing its job in the wrong place, a board
  seam or an arris or a threshold nosing. The remedy was a reserve painted under each text block,
  and the second lesson was ordering: the reserve has to be the LAST thing painted, because a
  grain tile at five percent laid the edges straight back over the type the reserve had cleared.
- **A plate at eighty percent is not a plate.** Slide 3 proved the engine's own sentence. An edge
  at 2.2 to 1 came through an 0.8 reserve, and only a fully opaque one cleared it.
- `panel_ready` found 18 things a judge should never have to see, in three classes. Thirteen lines
  under the rubric's 4.5 contrast floor, one dossier describing a frame the run no longer made,
  and four grounds measuring under the worked-ground floor. **A gradient is a promise of light and
  not of material**, and the fix was to give four frames a real tooth rather than a smoother wash.
- `plan_render_check` opened at 15 findings. Most were one character: acceptance items written as
  double-quoted YAML reached the gate with literal backslashes, because it reads the raw
  storyboard. Three dossiers also named palette tokens their frames never drew, which is the
  2026-08-19 defect exactly, and the dossiers were corrected to the tokens the frames use. It now
  reports **21 of 21 declared display strings found on their own frame**, against 3 before.
- Frame 6 was rebuilt once against the deck's own structural law. Its four requirements sat in
  dark bars on the light ground, which is four redactions at feed size, and the law says nothing
  in this deck is a black rectangle. The cuts became narrow slots and the words moved onto the lit
  concrete in dark ink.

**Disclosed rather than hidden.** Only 5 of 57 acceptance items carry an assertion a render could
contradict, which is low and is the ratio `SLIDE_DOSSIER_SPEC.md` warns about. The GPU bench was
not spent on frame 7 and its declared fallback was taken. `bespoke_check` puts the median pairwise
similarity at 0.4524 and names frames 4 and 6 as the closest pair at 0.7891. **That pair is
deliberate**, 4 states the list and 6 shows where it stops on inverted ground, and the panel was
told so and asked to test the call rather than discover it.

Machine QA finished at zero fails across all nine frames. `panel_ready` exits 0. The PDF is
vector.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 25 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | STALE  | render/machine_qa.json predates the newest render, so it describes a deck that no longer exists. Re-run it |
| aggregates     | PASS   | 7 declaration(s), 9 numeric phrase(s) in the render, all re-derived |
| assembly       | STALE  | final/assemble_report.json predates the newest render, so it describes a deck that no longer exists. Re-run it |
| score          | STALE  | score.json predates the newest render, so it describes a deck that no longer exists. Re-run it |
| labels         | PASS   | 96 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 85 published string(s) read from one list, every universal names its set |
| verbatim       | PASS   | 13 declared fragment(s) over 9 of 9 dossier(s), every one a literal substring of its own claim's quote |
| dossiers       | PASS   | 44,617 chars planned |
| caption        | PASS   | 134 words |
| craft floor    | WARN   | 9 frame(s), median 1291, floor 232, 1 quiet |
| plan vs render | WARN   | 6 of 62 acceptance item(s) checkable |
| texan          | WARN   | places Austin, Brownsville, Fort Worth, Houston, Plano, The Woodlands / body yes / deadline yes / next step NO |
| absences       | PASS   | 12 of 12 scoped to a named document |
| numerals       | PASS   | 4 numeral(s) over 9 frame(s), every one reachable |
| completion     | FAIL   | THE DECK DID NOT SHIP, so this run is not done |
<!-- gate-status:end -->

## Two frames changed while the panel was reading, and both changes were gate forced

`numeral_lint`, read through `gate_status`, failed the deck after the scorers were already out.
Slide 4 printed row markers 01 to 04 that trace to no claim, and slide 5's figure label printed
2027 where c8's own quote says 2026-27. **A numeral typed as furniture is still a numeral**, and
the law is that every one of them is quoted or computed. The markers were cut, because four rows
are self evidently four and numbering them asserted a figure while adding nothing, and the label
now says what the source says.

Both frames were re-rendered and `copy.json` refreshed from the new render report. The judges
may therefore have transcribed either version of those two frames. It is small and it is stated
here rather than left for a reader of the report cards to trip over.

`quantifier_check` was the last gate to go green and it found two universals with no set behind
them, "Not one of them" in the caption and "every claim and every source" in the first comment.
Both are now declared in `quantifiers.json` with their members named, and the first one's set is
measured by `compute.py` rather than asserted, on every build.

## SCORING, FIVE ROUNDS, AND THE DECK IS HELD

**Panel median 6.552 against a 6.8 bar, and one hard fail.** Judges: integrity 6.67, craft 6.66,
reader 6.20, spread 0.47. Two of the three refused on the NUMBER and said so plainly, and neither
could name a fault. The third named one, and a hard fail stops the deck at any round whatever the
median is and whatever the other two said.

**The hard fail, verbatim, on the frame a stranger meets first.** Slide 1's dek reads "Texas has
two ways to put a school in front of a child on public money." The frame cites c14, c15 and c1 and
not one of them enumerates the routes. "The other ends at a published checklist" closes the set
with a definite article, so the sentence asserts there are exactly two, and on the plain reading it
is false: a child's zoned district school is a school in front of a child on public money and
arrives by neither route.

**The scope limit existed the whole time and never reached the frame.** `aggregates.json` declares
the count with `what_two_counts` reading "the two routes the record carries, and never a claim that
Texas has no other way of funding a school". That sentence is correct and it is in a JSON file. The
frame is where a reader is, and the frame closed the set.

### Every hard fail this run was one species

| round | frame | the sentence | why it was a fault |
|---|---|---|---|
| 2 | slide 1 dek | "Only one of them ends at a body that can say no" | an unmeasured negative, cited to c14 and c15 which carry no such comparison, and refuted by the deck's own c1 and c21 |
| 3 | slide 5 dek | "no second date has been set against it" | a negative about the state's action, where a1 looked for teaching words on that page and never for a closing date |
| 3 | first comment | "or of its founders" | a3 searched one founder's name, and no claim records the reporting naming any founder |
| 4 | first comment | "Every date below is the date this run fetched the document" | false of three of the five lines directly under it |
| 5 | slide 1 dek | "Texas has two ways to put a school..." | a count that closes a set, asserted as a measured fact, computed by nothing |

**Four rounds repaired the sentence a judge named and shipped the next one.** That is the finding
worth more than the deck. `ledger/carousel/instincts.json` now carries it as
`a-negative-needs-an-absence-record`, and the sweep it asks for is over every sentence in the
deck, the caption and the first comment rather than over the frame that was named.

### The deck was left exactly as the panel scored it

The fault is a one sentence fix and it is NOT applied here. A run that repairs a hard fail after
the final round and then ships has graded its own repair, which is the failure the rubric's
`refusal` section was written against, in this repository, after a run wrote a field onto a
judge's file. The branch therefore carries the deck the panel actually read, the score describes
that deck, and the fix is written down rather than made.

**The fix, for whoever takes it next.** Two sentences that assert nothing about the count of
routes, for example "Two of the ways into a Texas classroom on public money end in different
places. One ends at a board that votes. The other ends at a published checklist." Both judges who
raised it separately also asked for the same second thing: frame 4 should print c2 and c3 whole,
the way requirement four now is, because "Be a proven operator" is content free while c3's "that
has successfully run a campus for at least two years" is the evidence frame 6's hinge rests on.

### What the two threshold dissents said, since a held deck's other findings still count

The craft judge verified five of six round 5 repairs in both code and pixels and then found two
instances of the same class it had named the round before, `slide-03.html`'s two fully opaque
reserves over the plate's own grain and `slide-06.html`'s reserve edge still visible at x=330 in a
432 px thumbnail. Its sentence: an audit that finds five of seven and reports done is the failure
mode GATE_LESSONS is entirely about. That is now `repair-the-class-not-the-instance`.

The integrity judge confirmed round 4's hard fail closed at the artifact rather than in the report,
and then found four dossier statements false of the frames they describe, including one acceptance
line contradicting another six lines above it in the same file. Its fix is a gate this repo does
not have: re-derive each dossier's `verbatim`, `labels`, `focal` and `acceptance` from the render
report's laid out text nodes and fail the build when they disagree, the way `copy.json` is already
built from the report rather than from the storyboard.

**No variety ledger entries were written.** `topics.json`, `artwork.json` and `captions.json`
exist to constrain the next deck against what SHIPPED, and this one did not. Recording it would
exclude a palette, an opening move and a subject from future runs on the strength of a deck no
reader ever saw.

**AN ARTICLE PAGE WAS PUBLISHED, AND AN EARLIER DRAFT OF THIS SECTION SAID IT WAS NOT.** That
sentence was written from the plan rather than from the artifact, which is the exact defect two
judges spent this run's last two rounds naming. `docs/articles/2026-09-06/index.html` is tracked
and carries the deck's copy. It is not a choice the run makes: `site_build.py` writes an article
page for any date with run artifacts under `runs/carousel/`, and `site_fresh_check` then requires
the committed page to match a rebuild byte for byte, so the page cannot be deleted without
changing the builder. `scripts/site/` is the `human` lane.

**Nothing publishes, because the branch does not merge.** That is the whole of what protects the
site here, and it is worth saying out loud that it is the only thing: a maintainer who merges this
branch to clear the record work would publish an article page for a deck the panel held. The
proposal is that `site_build.py` should read the run's `score.json` and decline to write an
article page for a run whose panel returned HOLD, rather than treating the presence of artifacts
as evidence that something shipped.

## CI WENT RED AFTER THE PULL REQUEST OPENED, AND THE RECORD HALF WAS NOT AS CLEAN AS IT LOOKED

`docket_calendar.py --self-test` failed on the pull request head with three failures this branch
caused and `main` has never seen. All three trace to one `key_date` on `tx-2026-0128`, the Tesla
fab registration, admitted this morning with `{"date": "2029-12-31", "kind": "expires"}`.

**Three things were wrong with it and only the first is what CI could see.**

1. `docket_calendar.py`'s `KIND_LABEL` knows nine kinds and `expires` is not one, so its own
   assertion that every kind on the real record has an explicit label failed the moment the item
   landed. That table is in `scripts/site/`, which is the `human` lane, so the record is where
   this gets fixed and not the labeller.
2. **The kind is wrong on the facts.** Nothing expires on that date. The filing prints a
   completion date the registrant stated, and a builder's own estimate of when it will finish is a
   fact about the project rather than a procedural event on a docket. `key_dates` is the record's
   calendar. A private completion estimate four years out is not on it, which is also what broke
   the other two assertions: a date that far out moves the record's own end and the calendar's
   window arithmetic is computed from it.
3. **Neither date the summary prints carried a claim.** The item states a registration date and a
   completion date, and its three claims covered the scope text, the funding and the project name.
   The house law is that every fact carries a claim id and traces to a fetched source. The filing
   was re-fetched and both dates now carry a verbatim claim.

### Two gate gaps, and the second is the one that matters

**`docket_build.py --validate` passed this.** Its numerals check reports "172 numeral(s) in copy,
all traceable to a quote or a name", and both of these dates were traceable to a KEY_DATE rather
than to a quote. A date can therefore enter the public record, be printed in a summary, and
satisfy the numeral gate on the strength of a field the same run typed. That is the
compute-not-generate law with a hole in it, and `scripts/site/docket_build.py` is `human` lane, so
it is a proposal rather than a fix.

**Phase 16's verification list does not contain `docket_calendar.py --self-test`.** Nine checks
are named there and CI runs more than nine. `CLAUDE.md` already says what covers that:
`guards_local.py` reads `guards.yml` so it cannot fall behind on WHICH steps run. This run ran the
Phase 16 list and pushed, and CI found in four minutes what the whole suite would have found
before the push. The list is a summary of the suite and it was read as a substitute for it.
