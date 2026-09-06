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
