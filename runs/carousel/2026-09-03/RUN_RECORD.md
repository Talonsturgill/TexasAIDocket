# Run record — 2026-09-03

Carousel no. 14. The Texas A&M University System's VISION supercomputer, and who may use it.

## The headline

The record woke in good shape for the first time this week, because yesterday's run cleared all 98
items. **6 due, 0 rotten, 0 deferred.** All six were worked by hand, four decisions were admitted,
the deck's own story was admitted as a fifth, and the ledger went from 98 items to 103 and from
517 claims to 549.

**Two items came off sources no client here can read**, which is the more useful half of the day.

## Phase 3, the record

| reading | at wake | now |
|---|---|---|
| items due | 6 of 98 | 0 |
| rotten | 0 | 0 |
| backlog | 3, its grandfathered floor | 3 |
| `docket_build --validate` | exit 0, two staleness WARNs | exit 0, clean |
| `reverify --apply` | exit 1, 0 items stamped | all six worked by hand |
| `reverify --check-notes` | not run | exit 0, every figure traceable |

`reverify --apply` stamped nothing. It read 13 urls behind 33 claims, reported three quotes gone,
three sources that did not answer and six it could not read, and every one of the six due items
needed a person.

**Two items were resting on documents that cannot be re-read, and both were moved.**

- **`tx-2026-0038`, the Harlingen Waterworks effluent agreement**, rested on a news article whose
  page serves nothing a quote can be read from. The board's own posted minutes answer. Four claims
  now cite them, and they carry more than the article did: the vote, 6 yeas and 0 nays, the
  executive session on what the agenda calls the RGVPG Data Center reclaimed water agreement, and
  the officer who recommended approval. His title is corrected to interim general manager.
- **`tx-2026-0098`, the Rice READINESS award**, rested on a university announcement that returns
  HTTP 406 to every client tried, a browser user agent included. Three claims now cite the NSF
  award record. One sentence came out of the summary with them, because the university's framing
  of responsible AI appears nowhere in the award record and this record does not print what it
  cannot re-read.

**Four claims were quoting strings that a rolling feed throws away.** `tx-2026-0024` is the item
whose whole subject is the PUCT calendar feed, and its claims quoted the entries a meeting leaves
behind once it is held. That is the feed working rather than the calendar moving. They now quote
the entry titles, which survive.

## Phase 4 and 5, what was admitted

Five items, each with a primary source and each naming where it is.

| id | what | why it is here |
|---|---|---|
| tx-2026-0115 | Austin City Council, a resolution starting land code amendments for data center use | The city's own record still reads agenda ready with no date of passage, so this item does NOT say the council acted |
| tx-2026-0116 | Dallas Public Safety Committee, a September 8th briefing on the police Flock program | The chief of police is listed among the presenters |
| tx-2026-0117 | UT Austin, a course AI policy required in every syllabus every semester | Permitted, prohibited or partially permitted, named course by course |
| tx-2026-0118 | The Commodity Futures Trading Commission, comment open to October 20th on compute derivatives | The only new door in the batch a reader can still walk through |
| tx-2026-0119 | The Texas A&M System's VISION supercomputer | This run's deck story, admitted so the carousel is built on a decision the record holds |

**Two scout findings were dropped rather than admitted.** A Katy ISD framework whose headline
quote turned out to be two sentences merged with the full stop removed, and a Pflugerville Flock
non-renewal that rests on journalism alone.

**The promotion gate held all five on the first pass and every reason was real.** Two decider
types outside the vocabulary, one new item with a stamp and no movement line, one summary at 4.23
commas per 100 words against a 3.97 ceiling, and one title of my own writing carrying the numeral
100 that no quote supported.

## Discoverability signoff

- **One decision's card, opened as an image.** `docs/og/tx-2026-0114.png`, the newest item before
  today's admissions. The headline wraps where a reader would break it and the plate is clean.
  **It ends on a stump.** The last line reads "equipment on..." because the wrapper cuts on width
  and this title is long. Not a fault in the builder and not fixable from this lane, but the next
  card for a long title will do the same thing.
- **`/questions/`, read as a reader.** Four shapes, and the counts are honest: 103 answered on
  what each decision is, 103 on who decides, 96 on how the public can take part, 07 on where a
  comment window is open. Those are questions a Texan would actually type.
- **The `Open right now` section of `llms.txt`.** Cross checked against the four open windows the
  record derives. Nothing that closed is still listed. tx-2026-0001 and tx-2026-0015 both closed
  in August and neither appears.
- **`/sources/`.** The share at the top reads 437 of 517 claims resting on a primary document at
  the time it was read, and this run moved it UP rather than down, because four claims on the
  Harlingen item came off a news article and onto the board's own minutes. The top publisher is
  `interchange.puc.texas.gov` at 85 claims across 20 documents, which is a filing index and is
  the right thing to be leaning on hardest. The quoted material exemption is still doing its job
  and is not hiding any of our own sentences.
- **`/topic/`, counting one card against its own page.** The eight beat cards sum to exactly 98,
  which is what the front page counter printed at the time, and the per beat open to comment
  figures sum to 4, which matches the four windows the record derives as open today.
- **`/place/`, for a place this run landed something in.** Travis County took two of today's
  admissions. Its page reads 13 items in the record and the ledger holds 13 for Travis. The
  VISION item is statewide and correctly absent from it.

**The water map's pins against the day's reservoir count.** 119 depth-classed pins on the map
against a readout of 119 reservoirs. The map is not one lake short.

**The backlog lines.** Three, unchanged, all three grandfathered ERCOT items that predate the
geography rule. Not grown.

## Phase 7, the instruments

Every page check and every discoverability self-test exit 0. Nothing is reading wrong and nothing
has stopped.

**The Supabase connector is not available in this session**, so the scanner's daily cap query
could not run for the second consecutive day. The routine's own third outcome applies. Recorded,
not worked around, and nobody is notified about a ceiling nobody is notified about.

## Phase 8, the story, and why this one

**Five of the last thirteen decks came off `power-and-compute` and every one was about compute
somebody fenced off.** This is the same subject from the other side. It is the one big AI machine
in Texas that is public, whose access rule is published, and that a student at a small campus is
told is theirs.

`dedupe_check` returned 0.31 against a 30 day window, well under the repeat threshold, and the one
entry it named was a different university system doing a different thing.

**The fact check changed the story and improved it.** Four framings were rejected and the deck
holds every one:

- **TOP500 publishes no university category.** Neither its list page nor its system detail page
  calls VISION the fastest university supercomputer in the United States. That framing belongs to
  the System and to Tarleton State, and VISION's own site says only "one of the highest-performing
  AI supercomputers at any North American university". **The run's own Phase 8 note carried the
  rejected framing for two more phases and a caption director caught it**, which is exactly how a
  refused claim gets inherited.
- **No county and no city.** No page fetched names one for the West Campus Data Center, and
  College Station appears only in a headquarters address in a page footer, which is a different
  building. The item is published statewide on the reach the chancellor states.
- **Nobody at a System campus can get on it today.** The documentation says access is
  invitation-only under a controlled beta.
- **No dated Board of Regents vote.** The newsroom asserts the approval and gives no meeting date
  and no agenda item. The minutes are PDFs this run could not extract.

## Phase 15, the panel

<!-- score block written at scoring time -->

**FIVE ROUNDS. Medians 6.526, 5.896, 6.300, 6.602 and 6.762 against a 6.8 bar.** `max_rounds` is
5, so the deck ships on the last of those. Round 5 is the first round in which **no judge found a
hard fail**, and two of the three refused on the threshold and said so rather than manufacturing
a fault.

| round | integrity | craft | reader | median | spread | hard fails |
|---|---|---|---|---|---|---|
| 1 | 6.51 | 6.76 | 6.34 | **6.526** | 0.42 | 3, all the same one |
| 2 | 6.296 | 6.17 | 5.81 | **5.896** | 0.49 | 2, both the same one |
| 3 | 5.77 | 6.382 | 6.288 | **6.300** | 0.61 | 2, both from one judge |
| 4 | 6.01 | 6.85 | 7.002 | **6.602** | 1.10 | 1 |
| 5 | 6.75 | 6.51 | 7.002 | **6.762** | 0.49 | **none** |

The arithmetic is `panel.py`'s, per-criterion median then weighted, and it is not mine to do.

**The spread at round 4 was 1.10 and the file says so**, which is what `SPREAD_NOTE` is for: three
judges disagreeing by more than 0.75 have not converged on the same deck, and reader 7.11 against
integrity 6.01 on the same nine frames is the panel working rather than failing.

## The five hard fails, and the one shape under four of them

1. **Slide 4's fairness sentence rendered at 1.05 to 1 on bare cream** and was gone from the 432px
   thumb. Round 1, all three judges.
2. **Slide 4 credited c10's quotation to c8's publisher**, taking the name from the wrong one of
   the two claims on its own frame. Round 2.
3. **The cover awarded a TOP500 rank to an institution**, which the deck's own rejected list says
   TOP500 does not rank. Round 3, and round 2's repair wrote it.
4. **c19's text field asserted an identity slide 5 denies in the deck's own voice**, and credited
   the System with a Tarleton sentence. Round 3.
5. **Slide 7 credited the docs page with a sentence from the testing page.** Round 4, and round
   3's repair wrote it.

**Four of these are one thing: a gate reading what a document SAYS while nothing reads what the
page SHOWS.** Every numeral traced. Every string was present. `copy.json` carried the sentence
because the browser really did lay it out. What none of the twelve gates asked was whether the
ink differs from the paper, whether the label names the right publisher, or whether the drawing
agrees with the arithmetic.

**Three of my own repairs wrote the next round's hard fail.** Fixing an instance three times in
three rounds is what happens when nothing binds a frame's source stamp to the claims its copy
carries, and both round 5 judges proposed exactly that binding, independently, as their one
sentence fix.

### What the panel found, round by round

**Round 1. 6.51, 6.76, 6.34, median 6.526 against a 6.8 bar. Three hard fails, all the same one.**

Slide 4's dek is two sentences. The second, "No meeting date is published for that approval.",
laid out below the sepia curl on bare cream while keeping its cream fill, at roughly 1.05 to 1.
A faint ghost at full size and entirely absent from the 432px thumb and the contact sheet.

The sentence that vanished is the frame's whole guard. c8 is medium confidence and the claims
file's own rejected list says the record carries the System's assertion and does not claim a
dated governing body vote. Without that line the frame reads as the Board of Regents approving
45 million dollars with no qualifier at all.

**Every gate passed it, and that is the finding.** `copy.json` carried the string because the
browser really did lay it out. `dossier_check` passed an acceptance item reading "the dek says No
meeting date is published" because the string was in the DOM. `numeral_lint` traced every
numeral. `qa.py` returned zero fails. `panel_ready` reported that every line cleared the rubric's
4.5 contrast floor, and reported it while this line sat at 1.05.

Not one of them asks the only question that mattered, which is whether the ink is different from
the paper. Twelve gates read what the document SAYS and none reads what the page SHOWS.

**Round 2. 6.296, 6.17, 5.81, median 5.896. Two hard fails, and the number went DOWN.**

All three judges verified all nine of round 1's repairs as landed. `claim_integrity` collapsed
from a 6.5 median to 4.5 on one finding that predated round 1 and that round 1's own repair made
visible.

**Slide 4 credited the wrong publisher and had done so from the start.** The attribution read
"QUOTED IN THE SYSTEM'S NEWSROOM". The quotation is c10, fetched from `tarleton.edu`, and the
deck's own first comment under the same post says "quoted by Tarleton State University".

The label was not invented. Slide 4 declares c8 and c10, and c8 IS the System's newsroom, so it
was taken from the wrong one of the two claims on its own frame. Nothing compared an attribution's
publisher against the claims the frame declares. Two judges called that a gate-shaped hole rather
than a writing slip, and it was in the dossier before it was in the render.

Round 1's repair extended and darkened that plate so a lost sentence would read, and nobody
re-read the line two inches above it. A repair verified against the defect it was written for, on
a frame carrying a different defect the whole time.

**The integrity judge found no hard fail in round 2 and refused on the number**, 6.296 against
the bar, saying it had looked hard and would not manufacture one. `panel.py` derives that as a
threshold dissent from the judge's own score rather than from any field the run could write, so
it counts in the median and is not a second veto.

## Sources field log

Appended to `knowledge/shared/SOURCES_FIELD_LOG.md` in the same commit range.

## Prompt audit

**1,488 tool calls measured, none waited on a human.** `prompt_audit.py` reads
`permissionDecisionMs` off the debug log, which is the measurement the 2026-09-02 run established
after eleven days of wrong guesses. No routine wrote under `.claude/` and no actor stamp was
written by any tool at any path.

## The one gate this run cannot make green, and why it is not merging on its own say-so

**`scripts/site/ask_pack.py --self-test` fails. The ask index is 40,450 characters against a
40,000 ceiling, over by 450.** It runs in `guards.yml`, so CI is red on this branch.

**It is this run's doing and the measurement says so.** Against `main`'s record the index builds
to 39,393, with 607 characters of headroom. This run admitted five decisions and crossed it.

**Where the 40,450 sits:**

| part | chars |
|---|---|
| `INDEX_HEAD`, fixed prose | 1,546 |
| 103 docket lines, at 225 characters each | 23,216 |
| the instrument sections, chiefly a 119 reservoir roll call | 15,686 |

**The record is 57 percent of the index and the instruments are 39 percent.**

**THE FIX IS NOT IN THIS RUN'S LANE.** `ownership.yaml` gives `scripts/site/ask_pack.py` to
`human`, with the reason written beside it: *"The answer engine is a gate on what the site may
claim. Maintainer-owned."* `ownership_check --actor daily --files scripts/site/ask_pack.py` exits
1. The instrument series belong to `gridwatch`. Neither is reachable from `daily` and neither is
reachable from `upgrade` either.

**What was done inside the lane, on its own merits.** Four of this run's five new titles were
genuinely long, and two were bad titles rather than merely long ones: `tx-2026-0119` packed two
clauses into one title and `tx-2026-0116` carried a date that will go stale. All four were
tightened and that recovered 176 characters. Three claims were also rewritten to carry a readable
verbatim quote instead of raw Legistar JSON and a bare URL, which the same self-test was failing
on separately and which were defects in their own right.

**What was NOT done, deliberately.** The remaining 450 characters are reachable only by cutting
titles across the existing record. The median title is 111 characters and the longest eight are
single informative clauses at about 150. **There is nothing there this project would cut on its
merits, and cutting a 103 item public record to fit a byte budget is the exact pressure that
degrades a record.** `CLAUDE.md`'s own rule is that a gate is fixed at source or reported, never
loosened and never worked around.

**So this run does not merge itself green.** The evidence is committed to the branch and the
pull request is open. A maintainer session owns the decision, and the decision is a real one
rather than a formality:

- **The ceiling now binds structurally, not once.** The docket adds about 225 characters a day.
  Even at zero admissions tomorrow the index stays over, and every future run inherits a red gate.
- **The instruments are the bulk and the record is the growth.** A reservoir roll call naming 119
  lakes is 39 percent of the block every question pays for, and it does not change with what the
  docket does.
- Three shapes of answer exist and this run gets to propose none of them: raise the ceiling on
  measurement rather than by feel, move the instrument sections out of the always-sent index into
  a retrieved section, or compress the docket line (the longest one spells 22 county names).

**The run's own gates are green.** `docket_build --validate`, `house_style_check`,
`schema_contract`, `site_fresh_check`, every carousel gate, `qa.py` with zero fails and
`panel_ready` all exit 0. This is one gate, in one file, that this actor may not touch.
