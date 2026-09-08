# RUN RECORD — 2026-09-08 — carousel no. 18

Branch `claude/daily-2026-09-08`. Today is the America/Chicago date.

**The session was told to develop on `tsturg/practical-franklin-7ozl8m`.** It did not, and the
reason is mechanical rather than a preference. `resolve_actor()` reads the lane off the branch
prefix, so a run on that branch resolves to `human` and `.githooks/pre-commit` refuses every
write this routine makes. `CLAUDE.md`'s delivery policy already says it wins over a
session-injected branch directive, and this is the case it was written for.

## The record

The selector named **97 items** on a three day gap, no deferrals and nothing rotten.
`reverify.py --apply` stamped **66** and handed back **31** it could not settle.

**Not one of the 31 was a claim that had moved.** Every one was a page the checker's own client
could not read: a PDF, a JavaScript rendered filing index, or a host that answers a plain client
with a 406. All 31 were re-fetched here with a browser client and every claim quote was tested
against the page it cites. **The worklist was cleared in full and the selector now reports 0 due.**

That is worth stating as a finding rather than as a statistic. `reverify.py` reported 53 claims it
"cannot read" and 16 unreachable, and on inspection **the record was right about almost all of
them**. The gap is in the fetcher, not in the ledger. Three sources answered a browser client and
refused the checker: `news.rice.edu` returns 406, the PUCT Interchange returns a JavaScript shell,
and the San Angelo document centre serves PDFs the checker does not parse.

**Two quotes were wrong and are corrected.**

| claim | what the record carried | what the source says |
|---|---|---|
| tx-2026-0056-c3 | "the three-member board denied a petition by Wimberley resident Margaret Elizabeth Hill" | the article says the board **also** denied it. The dropped word changes the sentence from the meeting's main action to one of several |
| tx-2026-0122-c1 | one quotation running from "PhaseForge shows how" through "across academia, national laboratories and industry" | the page separates those two passages with "said Dr. Ibrahim Karaman, head of the Department of Materials Science and Engineering". The record had joined two real passages into one quotation that was never spoken as one |

The second is the more serious of the two and it is the same defect the dossier spec's `verbatim`
key exists for. A quotation that splices across an attribution is not a misquote a reader could
catch, because both halves are genuine.

**Two filing indexes moved.** PUCT control number 59315 now reads 5825 filings and 59029 now reads
509, one more each than the record last held, and both readings are entered as their own dated
claims rather than by editing the old ones.

**Every one of the 66 deterministic notes was re-worded.** The script writes each stamped item the
same three sentences from the item's own fields, so a reader opening ten items in a row met one
template ten times. `reverify.py --check-notes` passes on all 426 checked notes.

## Six decisions admitted, two held, and one that had to be re-sourced

| id | what |
|---|---|
| tx-2026-0129 | Austin forbids its city manager from buying a park camera or drone that depends on artificial intelligence |
| tx-2026-0130 | The National Science Foundation puts UT Austin's supercomputing centre in an operating role on the national AI research resource |
| tx-2026-0131 | Texas State moves an AI pavement assessment method toward statewide highway use |
| tx-2026-0132 | Texas A&M names one approved platform for campus AI use and states the data classification it is cleared for |
| tx-2026-0133 | North Texas opens a named undergraduate artificial intelligence degree |
| tx-2026-0136 | A federal defect evaluation was opened into a driverless system after crashes in Dallas and Austin |

**Held rather than admitted, both for the same reason.** Katy ISD's artificial intelligence
framework and the grid operator's first interconnection study batch. Neither source names a
county, and the batch applies across the grid operator's region, which is not the state. A
`statewide: true` on either would be a claim about scope that no source supports.

**The primary source share moved up rather than down**, from 525 of 606 claims at wake to 561 of
642 now. Every item admitted this run is primary sourced.

## THE RECORD WAS RESTING ON SOURCES THIS PROJECT HAS DECIDED NOT TO FETCH

The `/sources/` signoff turned this up and it is the run's most important finding about the record.

`lrl.texas.gov` sits at twelfth on the publisher ranking with 12 claims across four entries. That
host is **off limits, whole host, all clients**, decided August 25th. Three more entries cite
`capitol.texas.gov/tlodocs/`, which the host's own robots.txt disallows.

**An entry resting on a source the project may not return to is an entry nothing can re-verify.**
It will fail every future re-check for a reason that looks like a fetch problem and is actually a
boundary the project drew on purpose.

**One of them was promoted from the seed by this run**, tx-2026-0126, and all three of its claims
cited the disallowed path. That is the second time in two days an item has entered the record from
a path already ruled out, and the first time it came through the seed rather than through a fresh
admission. It has been re-sourced onto `senate.texas.gov`, whose robots.txt disallows neither
`cmte.php` nor `videoplayer.php`. Three facts that only the disallowed notice carried, the time,
the room and the two minute limit on public testimony, were **dropped rather than kept**, because
a fact the record can't go back and check is a fact it should not publish.

**Four older entries still carry the problem**, tx-2026-0073, tx-2026-0077, tx-2026-0078 and
tx-2026-0079. The compliant substitute is the one used here. This run did not do that work and
says so rather than leaving it implied.

**The gate that would have stopped it does not exist.** `docket_build` checks quote, source url
shape, geography, house style and staleness. It does not check the source against the crawl
boundary, and the boundary lives in prose in `SOURCES_REGISTRY.md` where nothing reads it. That is
this run's upgrade proposal and it is GATE_LESSONS' oldest shape, a rule stated in one place with
nothing in between checking it.

## TWO SCOUTS FETCHED HOSTS THIS PROJECT HAS RULED OUT

Reported plainly because the alternative is that it goes unrecorded.

- The `power-and-compute` and `policy-and-money` scouts both fetched
  `capitol.texas.gov/tlodocs/89R/schedules/`, which is a disallowed path.
- The `policy-and-money` scout listed `lrl.texas.gov` among its sources.

**Nothing sourced from either was admitted or used.** The Senate Water hearing they both found is
already on the record as tx-2026-0096 and now rests on compliant sources, so nothing was lost. The
scout briefs named five off limits hosts and did not name these two, which is the fixable half.

## Discoverability signoff

- **One decision's card, opened as an image.** `docs/og/tx-2026-0136.png`, the run's newest item.
  Reads "Federal investigators / opened a defect / evaluation into a / driverless system...".
  Four lines, every break where a reader would put one, and the truncation falls after a whole
  word rather than mid-stump. LOOKED AT, correct.
- **`/questions/`, read as a reader.** The hub headings are noun phrases and the questions
  themselves only appear on the pages beneath them, where they read as things somebody would type
  ("Can the public comment on it?"). One honest wrinkle. The open-comment page's subtitle says
  "The decisions taking written comment right now" and answers for six entries, two of which say
  in their own answer that the window has closed. The answers are correct and dated. The subtitle
  is the part that overreaches. LOOKED AT, one observation, no change made.
- **The `Open right now` section of `llms.txt`.** Eleven entries. Cross checked against the
  record's own open comment rooms and their close dates. tx-2026-0016 closes today and is
  correctly still listed. tx-2026-0001 and tx-2026-0015 have shut and are correctly not in this
  section. Today's newly admitted tx-2026-0129 IS listed, which proves the build ran after the
  record moved. LOOKED AT, correct.
- **`/sources/`.** The share reads 561 of 642 claims on a primary document, across 209 documents
  from 96 publishers, and it moved UP this run. The top publisher is
  `interchange.puc.texas.gov` at 95 claims, which is the filing system itself and is exactly what
  should be at the top of that list. The quoted-material exemption is still doing its own job and
  not sheltering any of our sentences. LOOKED AT, and it is where the off limits finding above
  came from.
- **`/topic/`.** Eight beats. The per beat counts are 28, 3, 12, 15, 11, 22, 17 and 10, which sum
  to 118, the figure the front page's own counter prints. The `still open to comment` figures sum
  to 4, which is the front page's `04 Doors open to you`. The surveillance and policing card says
  10 and its page says "10 of 118". LOOKED AT, counts agree in both directions.
- **`/place/`.** Travis County took three items today. The hub says 19 and the county page says 19
  and names the Austin resolution among them. LOOKED AT, correct.

**The front page counter row** reads 17 articles, 05 videos, 118 decisions, 642 sources cited and
04 doors open. `Sources cited` is rendering, which is the entry that spent its early life invisible
behind a cap of four. `What this is` is absent, as instructed.

**The backlog did not grow.** Three entries at wake, three now, the same grandfathered
tx-2026-0001, tx-2026-0002 and tx-2026-0007. None can be cleared honestly, because each is a rule
or a queue applying across the grid operator's region rather than across the state.

## Instruments

Both page checks exit 0 and both self-tests pass. `gridwatch_pagecheck`, `waterwatch_pagecheck`
and `waterwatch_page --self-test` are green, so **no instrument has stopped and no page is reading
wrong**. Nothing in `scripts/gridwatch/` or `ledger/gridwatch/` was touched by this run.

The front page weather chip is live and rotating. It leads today with Dallas Fort Worth, 39 days
at 100 by September 3rd against a normal of 19.

**The scanner's daily ceiling could not be read.** No Supabase connector is attached to this
environment, so the query in Phase 7 has nothing to run against. That is the third of the three
outcomes the phase names and it does not block the run. A requester who hit the cap today would
still not have been noticed by anybody.

## Sources, and what they actually did

- **The PUCT calendar RSS is the run's best poll and the routine has its URL slightly wrong.**
  `GetCalendarRss.aspx` 301s to the lowercase `getcalendarrss.aspx`, and `WebFetch` returned 503
  twice rather than following it. A browser client following the redirect gets 200 and 36 items.
  It named a live comment deadline the record already holds, Project 59550 closing September 17th,
  and a September 22nd workshop on Project 58555, the grid operator's ancillary services cost
  allocation study. Neither 58555 nor 59550 is an AI decision, so neither was admitted.
- **`texreg.sos.state.tx.us` now disallows named AI agents site wide**, including GPTBot,
  ChatGPT-User, OAI-SearchBot, Googlebot and bingbot. The Texas Register is the third source the
  routine's Phase 4 tells a run to poll, and it is no longer pollable by an agent. Not routed
  around.
- **`www.nhtsa.gov` returns 403 on every path including its own robots.txt.** `static.nhtsa.gov`,
  which carries the investigation documents, serves no robots.txt at all and answers 200. The
  registry's own CourtListener precedent says a 403 on the robots file is an edge failure rather
  than a policy change, so the host is not written off, and nothing was fetched from it.
- **`statutes.capitol.texas.gov` serves its homepage shell for every statute path tried**, so no
  Texas statutory text was read this run.
- Three publishers refused the fact-checker or the scouts and none was routed around:
  `news.rice.edu` 406, `tacc.utexas.edu` 403 by name, `beckershospitalreview.com` 403.

All of it is appended to `knowledge/shared/SOURCES_FIELD_LOG.md` rather than to the registry,
which is `human` lane and carries the crawl boundary.

## The deck — carousel no. 18

**The story is tx-2026-0129, Austin's Resolution No. 20260812-017**, admitted to the record by
this run from the executed and attested copy in the city's own document system.

### Why this story and not the other one, written down because it was a close call

The strongest thing the scouts brought back was **tx-2026-0136**, the federal defect evaluation
opened into the Avride automated driving system after crashes in Dallas and Austin. It was fact
checked in full first, its claims file is complete, and it is admitted to the record. It is not
the deck.

`dedupe_check` returned it at 0.32 against carousel no. 5 of 2026-08-21, under the repeat
threshold, with the tool's own advice to read the top entry anyway. **Reading the full entry is
what changed the answer.** Carousel no. 5 was Texas authorising commercial driverless operation
and the Senate committee sitting to study it, and its declared angle was "the gap between what
the machines measure continuously and what the state publishes a crash count for". A federal
crash count taken off machine video, eighteen days later, is the answer to that deck's own
question rather than a new story. The thirty day call is the showrunner's after reading, and this
is a repeat.

That is the failure mode the phase warns about, arriving from the opposite direction. The sibling
product's near miss came from reading a TITLE and clearing a repeat. This one would have come
from reading a SCORE and clearing it.

**The Avride claims file is kept** at `claims-avride-deferred.json` and the item is on the record,
so a run after September 20th can build the deck the window currently forbids.

### Why the Austin story earns it on its own terms

- The document is **executed, attested and signed**, and every quote was verified against a local
  extraction made in this run rather than against any third party reader.
- **It has a door, and the deck owes one.** `avoid_next` on carousel no. 16 recorded that four
  decks running had closed on an absence. This one closes on December 9th, 2026, a Council
  Climate, Water, Environment, and Parks Committee meeting a reader can attend.
- `texan_check` at selection returned places Austin, body yes, deadline yes. Its one gap was the
  next step, and the closing frame is where that gets spent.
- Its nearest neighbours in the variety ledger are 0.30 and 0.25, and the 0.30 shares only
  geography words with a deck about Amazon siting a robotics factory.
- **It is the rarest kind of AI decision this record carries.** Every other surveillance entry is
  about adopting a system or pausing one. This is a government writing artificial intelligence
  OUT of a purchase, by name, in operative text.

### The argument, and it is one summer's escalation by a council against itself

On April 23rd, 2026 the same council adopted the TRUST Act at City Code Chapter 2-19. It gates
four acts behind council approval and acquiring new surveillance technology is the second of
them. Before the vote a department files a privacy impact assessment, four weeks ahead, posted
publicly the same day, and that assessment analyses ten numbered properties the technology might
have. **Using the data to train artificial intelligence is number five on that list**, and the
ordinance says any one of the ten "shall weigh strongly against a determination that the
surveillance technology presents no or minimal risk".

Thirteen weeks later the same council wrote "shall not consider acquisition".

**A factor on a weighing list became a wall.** That is the deck.

Both figures are parsed out of the ordinance's own numbered enumeration by `compute.py` rather
than counted by anybody, and the frame that prints them names the set they were counted over,
which is the instinct the ledger handed this run.

### What the resolution does not say, read in the whole two page text

No definition of what it means to depend upon artificial intelligence. Nobody named to decide
which side a system falls on. No enforcement, no penalty, no consequence. It reaches future
acquisition only, so anything the city already runs is untouched. And no vote is published
anywhere, because the city's own Council Voting Record has loaded no meeting later than
May 28th, 2026.

`absence_check` refuses a stated absence that names no document, so every one of those is
asserted against Resolution No. 20260812-017 by name.

### Measured before a frame was written, which is the cheapest round there is

The last three decks shipped at deck median L\* 22.5, then 16.5, then 11.4. A fourth near-black
deck is a rut rather than variety, and the light deck cap is spent by 2026-09-03 so the deck
also can't go light. The band is 28 to 42.

A first ground written the way the last three decks were written **measured 16.1**, which is the
rut, and it was caught by rendering one throwaway frame and reading the pixels rather than by a
judge in round three. The ground base was solved numerically from there, and the type contrast
on the whole resulting range was checked before any frame was drawn.

| ground base | deck median L\* | limestone on it | caliche on it |
|---|---|---|---|
| 40 | 16.6 | 11.70:1 | 10.33:1 |
| 58 | 25.1 | 8.95:1 | 7.90:1 |
| 70 | 30.5 | 7.38:1 | 6.52:1 |
| 78 | 34.0 | 6.49:1 | 5.73:1 |

`dust #C9B393` falls to 3.98:1 at the top of that range and is therefore furniture only, never
body text. Carousel no. 17's own `avoid_next` said a dark deck should plan its type reserves at
storyboard time and set its arc from what is left. This is that, done arithmetically and before
the drawing.

### `plan_render_check` has been reading a third of every plan, and it found none of this

Phase 12b's report on this deck read `0 of 16 acceptance items carry a machine-checkable
assertion`. The deck's nine dossiers carry **52** acceptance items, not 16, and most of them
quote a string, name a count or state a tolerance. Both halves of that sentence were wrong for
the same reason.

The gate takes the acceptance block with

```
re.search(r"^acceptance:\s*\n((?:  - .*\n)+)", body, re.M)
```

and `(?:  - .*\n)+` stops at the first line that does not begin with two spaces and a dash. An
acceptance item long enough to wrap is written with its continuation indented four spaces, so
**the block ends at the first wrapped item** and everything after it in that slide's list is
never read. Measured across this deck's nine dossiers:

| slide | items the gate read | items actually written |
|---|---|---|
| 1 | 1 | 6 |
| 2 | 1 | 5 |
| 3 | 2 | 7 |
| 4 | 3 | 5 |
| 5 | 1 | 5 |
| 6 | 1 | 6 |
| 7 | 1 | 5 |
| 8 | 1 | 6 |
| 9 | 5 | 7 |
| | **16** | **52** |

The items that survive truncation are the SHORT ones, and a short item is the one least likely
to quote a string, which is why the checkable ratio then reported as zero. The gate was not
finding uncheckable plans. It was reading the fragment of each plan that happens to fit on one
line.

**This is GATE_LESSONS' oldest shape and it is the gate built to answer that shape.** It exists
because the plan-versus-render defect shipped in all three early runs, and it has been certifying
a third of the plan since. Its own `--self-test` passes, because the fixture it tests against
writes every item on one line.

`ownership.yaml` puts `scripts/carousel/**` in the `upgrade` lane and says why in as many words:
the routine runs these every day and does not edit them mid run. So this run does not touch it.
It is written up here, it is carried into Phase 17 as the upgrade this run proposes first, and
the daily-lane answer taken now is to write this deck's acceptance items on single lines so the
gate reads all fifty two of them.

### Three frames missed their own declared value, and only one mattered

The per-frame median L\* is declared in each dossier's acceptance list with a tolerance, and
every one of those declarations sits past its slide's first wrapped item, so the gate above had
never read one. Measured directly on the 270 by 338 grid:

| slide | declared | measured | verdict |
|---|---|---|---|
| 1 | 34 +- 8 | 28.0 | ok |
| 2 | 30 +- 4 | 26.2 | ok |
| 3 | 38 +- 4 | 43.4 | over by 1.4 |
| 4 | 24 +- 4 | 21.4 | ok, and the darkest frame as declared |
| 5 | 33 +- 4 | 35.4 | ok |
| 6 | 26 +- 4 | 27.4 | ok |
| 7 | 62 +- 5 | 70.6 | over by 3.6, and the brightest frame as declared |
| 8 | 29 +- 4 | 32.0 | ok |
| 9 | 41 +- 4 | 31.1 | **under by 5.9** |

Slides 3 and 7 came out brighter than planned and neither carries a ranking claim that the miss
breaks. Slide 9 does. Its dossier calls it the second brightest frame in the deck and it rendered
fifth, which is not a tolerance miss, it is the closing frame failing to be the lift the arc was
built around.

## PIXEL REVIEW, and the two sentences that had no source behind them

Five critics, one per one or two frames. Two findings were integrity rather than craft, both were
verified against `claims.json` before anything moved, and both were fixed at the COPY rather than
at the drawing, because the drawing was not the thing that was wrong.

| frame | printed | what the record actually holds |
|---|---|---|
| 3 | `None of it is published yet.` | c5 says what the plan must establish. Nothing in this run records a dated search of the city's plan publication surface, so the sentence asserts a state of the world the deck never looked at |
| 4 | `Nothing is fitted yet.` | c10 says which parks go first. No claim records a deployment status as of today, a month after adoption |

Frame 3 now reads `It establishes none of it`, which is a fact about the document its own locator
names. Frame 4 keeps `The mount is bare`, which is a statement about the drawing and needs no
claim, and drops the second sentence.

**Neither was caught by a gate and both were caught by two readers independently.** `absence_check`
passed because each frame carries a locator, and a locator satisfies it whether or not the document
it names could settle the sentence beside it. That is the same defect as frame 9's locator below,
and it is worth stating as one thing: **naming a search is not the same as naming the right one.**

### Five quotes were stored cut short, and one of them made a frame's contested fact untraceable

A judge found `(B)` printed twice on frame 5 and in none of the six claims the frame cites. The
letter is in the fetched source, `(B) acquiring new surveillance technology;` in the executed copy
of the April ordinance, and `compute.py` had parsed it correctly. What was wrong is that the stored
quote began after the letter.

| claim | was stored as | now carries |
|---|---|---|
| c15 | `acquiring new surveillance technology` | the `(B)` in front of it |
| c25, c26, c27 | the same, without `(A)`, `(C)`, `(D)` | their own letters |
| c24 | ends at `presents no or` | `no or minimal risk to civil liberties and privacy rights`, which is what frame 8 prints |

Three claims are new and each names a passage the run had already fetched. c29 and c30 carry the
two section headings, `§ 2-19-3 COUNCIL APPROV AL REQUIRED.` and `§ 2-19-4 PRIV ACY IMPACT
ASSESSMENT.`, with the scan's own word splits kept so a quote can still be found in the document.
c31 carries the risk question subsection (C) opens on. All thirty one assert against the snapshots.

**The generalisable half.** `numeral_lint` cannot see a letter, and `verbatim_check` only holds the
strings a dossier declares, so a subsection letter set beside a quoted phrase is in nobody's
window. It reached the render wearing the costume of a citation, which is the carousel no. 15
defect in a form the gate built for that defect does not cover.

### Two of the deck's own structural laws were mis-drafted

Both were found by judges rather than by a gate, and in both cases the frames were right.

**L1's second half read "every frame carries at least one hard silhouette against the sky".**
Frames 6, 7 and 8 declare no sky at all, so no version of them could ever have met it. Two critics
named it independently and both called it a drafting error in the law. It now reads "at least one
hard edge against its own field" and the substitute edge is named per frame. The six outdoor frames
still carry a silhouette against sky, and frames 1 and 2 did not until this round: frame 1's
uprights all began below the horizon and frame 2's rail terminated exactly on it, so the only hard
edge against the sky on either was the ground plane's own top line.

**L5 read that frames 3, 7 and 9 carry the resolution's locator.** Frame 9's absence is the missing
vote tally, and the resolution's extent cannot settle that however fully it is read. It now carries
`VOTING RECORD 3c89-i35a / LOADED TO MAY 28TH, 2026`, which is the search the sentence rests on.

### The one finding judged and not taken

Frame 8's ten witness lines carry no factor text, and a critic held that nine blank rules read as
withheld rather than as nine other factors. The fix it proposed was to set each row with its own
factor text from the ordinance. Measured: the annotation run beside a dimension line is 458 design
px and the shortest honest fragment of factor (5) needs 659 px at the deck's 24 px mobile floor, so
ten rows of source text do not fit at a size a reader can have. The alternative was to truncate ten
quotations, which is worse than leaving them out.

What was taken instead is the half of that finding that is unambiguous. The `(5)` callout had sat
inside the stack on two lines with its second line level with the `(6)` label, so the thumb read
`(6) artificial intelligence` and the frame's whole numeric claim inverted. It is now one line
below the stack with a drafting leader onto the `(5)` rule, and **all ten rules are drawn
identically with nothing on any of them**, which is what the dossier's job line says the frame is
for.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 39 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | PASS   | 9 slide(s), zero fails, zero warns |
| aggregates     | PASS   | 6 declaration(s), 6 numeric phrase(s) in the render, all re-derived |
| assembly       | STALE  | final/assemble_report.json predates the newest render, so it describes a deck that no longer exists. Re-run it |
| score          | ABSENT | score.json not written yet |
| labels         | PASS   | 46 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 89 published string(s) read from one list, every universal names its set |
| verbatim       | PASS   | 11 declared fragment(s) over 9 of 9 dossier(s), every one a literal substring of its own claim's quote |
| dossiers       | PASS   | 55,387 chars planned |
| caption        | PASS   | 133 words |
| craft floor    | WARN   | 9 frame(s), median 922, floor 166, 1 quiet |
| plan vs render | PASS   | 12 of 77 acceptance item(s) checkable |
| texan          | PASS   | places Austin / body yes / deadline yes / next step yes |
| absences       | PASS   | 9 of 9 scoped to a named document |
| numerals       | PASS   | 13 numeral(s) over 9 frame(s), every one reachable |
| completion     | ABSENT | not scored yet |
<!-- gate-status:end -->

## ROUND TWO, and both of the round one fixes bought a new problem

A flow critic on the sequence and two pixel critics on the four frames that were rebuilt hardest.
The most useful thing they returned is that **a fix is a change, and a change can be wrong.**

| frame | the round one fix | what it cost |
|---|---|---|
| 6 | the galvanized stock moved below the clause | it told the reader there was more page under the sentence, which is the opposite of the frame's argument. The clause stopped with 272 design px of empty sheet under it and frame 7's whole payoff rests on it running out |
| 8 | the AI callout moved off the row stack | the misread at 432px went, and nine of ten witness lines were left carrying nothing |
| 9 | the locator moved to the voting record | correct, and the sentence beside it had been widened to a universal negative, so the two now pointed at different scopes |

### A third unsourced sentence, on the frame that closes the deck

`No count for the adopting vote is public` claims that no count exists anywhere public. c19
supports only that **the city's own published voting record** holds no tally, because its most
recent loaded meeting predates the adopting one. The line now reads `The city's own voting record
holds no count for the meeting that adopted it`, which is what the locator directly beneath it
names.

That is three sentences in one deck asserting a state of the world wider than the search behind
them, and none of them was caught by a gate. `absence_check` reads whether a frame names a
document. It cannot read whether that document could settle the sentence. **Naming a search is not
the same as naming the right one**, and that is the upgrade this run proposes first after the
acceptance-item truncation.

### What was fixed, and it is mostly the drawing paying for the copy

- **6** the clause block runs to the footer, so the sentence reaches the foot of the page and
  stops. The stock moved to the sheet's far cut edge, overhanging onto the granite, and its
  contact became a two part occlusion rather than one hard line. Both quarter folds are drawn,
  because at 432px a tan trapezoid between dark walls with no crease in it reads as a ROAD, and a
  page with two visible creases cannot.
- **9** the canopy was upside down. Its straight edge faced the sky and its ragged edge faced the
  ground, which is a torn paper strip rather than a treeline, and it was the frame's only
  silhouette. The crown is ragged now and rises through the horizon. The post feet lost a
  symmetric pool four times the post's own width, which is a cast shadow in a deck whose first law
  is that nothing casts. The paint band moved clear of the lit arris it had been sitting against,
  which is where the pale outline on both its long edges came from.
- **5** the fence floated, with the brightest amber in the frame directly under the bottom selvage
  and the granite arriving as a hard unbroken line. The ground's occlusion now runs up into the
  fabric. The gate leaf existed only at full size and now reads at 432px, which was the point of
  drawing it.
- **7** the press block was rendered as simulated glyphs and read as BLACKED OUT TEXT at 432px,
  which is the exact misread frame 3's whole design avoids, on the one frame whose job is that the
  sentence is complete and readable in the open. Nine ruled lines now, at page two's own line
  lengths, asserting that a document continues and nothing about what it says.
- **2** carried no fact the argument uses and opened the deck at frame 1's own weight. It states
  the audit's July 2025 date, which c4's quote carries, and it moved from 26.1 to 31.1.
- **3** was the only frame outside its own declared value. The silkscreen went to `liveoak` in the
  first round, which bought exactly the headroom the board needed to come down from 43.4 to 41.8.

### The one request refused, and the reason is a measurement

Two critics asked for the four gated acts stencilled on frame 5's fabric, which its own dossier
had promised. **The deck's reading load ceiling forbids them.** The four acts in the ordinance's
own words are 28 words, the frame already carries 54, and `coherence_check` fails a frame over 65.
Paraphrasing them down to fit is what put `minimal risk` on frame 8 in the first place. The
dossier's bands paragraph was corrected to stop promising it, with the arithmetic written into the
plan so the next run does not rediscover it.

Every frame now measures inside its own declared median L\*, which none of three did before this
round: 27.6, 31.1, 41.8, 22.3, 31.1, 27.4, 65.3, 32.0, 42.4, deck median 31.1 against a plan of 33.

## THREE GATES THIS RUN WERE MEASURING SOMETHING OTHER THAN WHAT THEY CERTIFY

Written together because it is one pattern and GATE_LESSONS' oldest one. Each is `upgrade` lane,
so this run does not touch any of them, and each is carried into Phase 17 as a proposal.

**`plan_render_check` reads the acceptance items before the first wrapped one.** 16 of this
deck's 52. Measured per slide in the table earlier in this record. Its `--self-test` passes
because the fixture writes every item on one line.

**`absence_check` reads whether a frame names a document, not whether that document could settle
the sentence.** Three sentences in this deck asserted a state of the world wider than the search
behind them, `absence_check` passed all three, and two readers found them by reading. The check
it is missing is a comparison: the locator's subject against the sentence's subject.

**`label_guard` reads the L5 locator as a set of labels.** It reports eight problems on this deck
and every one of them is a word from `RESOLUTION 20260812-017 / READ IN FULL, BOTH PAGES` on
frames 3 and 7: READ, FULL, BOTH, PAGES. That string is structural furniture mandated by a
structural law, and it is not a claim about what a body did, which is what the gate's own
docstring says a label is. Slide 9's locator does not fire, because `VOTING RECORD` and `LOADED`
happen to appear in c19's text, which is luck rather than correctness.

The deck was NOT distorted to satisfy the third one. `SLIDE_DOSSIER_SPEC` already records the
rule for this case in as many words: **a gate that fires on correct behaviour gets switched off**,
and the answer is to narrow its window rather than to reword a locator until a false positive
goes quiet. `label_guard` EXITS 0 and `gate_status` marks the row FAIL, and both are correct: the script's exit code is advisory and the row is computed from the problems it lists. Two judges read that pair as a contradiction in this file, so it is stated here rather than left to be picked. Nothing was suppressed either way.

## SCORING ROUND ONE, and three of the four hard fails were real

| lens | score | hard fails | ship |
|---|---|---|---|
| integrity | 6.41 | 4 | no |
| craft | 7.19 | 0 | yes |
| reader | 6.78 | 0 | no |

**Any one judge's hard fail stops the deck**, so every one of the four was checked against the
claims rather than taken on trust. Three held.

**The cover asserted a closed set the source declares open.** c6 reads `potentially including but
not limited to, security cameras, non-recording drones as first responders, lighting, access
control/fencing/gates, signage and wayfinding, and radio communication systems`. The hook read
`Austin ordered six kinds of equipment.` and `aggregates.json` declared the ratio `two of the six`
on that denominator. `compute.py`'s own splitter is documented as cutting after the stem
`potentially including but not limited to,`, so **the run read the qualifier and then wrote past
it.** The hook is now `Austin's order names six kinds of equipment.` and the dek says the list is
not limited to them.

**Frame 3 asserted a universal the deck's own claims refute.** `It establishes none of it` was
cited to c5 alone, and the board's five heads include PRIORITY LOCATIONS and IMPLEMENTATION
TIMELINES. c10 fixes a priority rule and frame 4 prints it verbatim one swipe later. c11 fixes a
date and frame 9 prints it in the largest type in the deck. The line now reads `The plan itself is
not in it`, which is true of the document and is what the empty board is about.

**Frame 5 scoped an obligation wider than its own claim.** `Whatever is bought meets Chapter 2-19.`
c7 attaches the obligation to `Any surveillance technology sought`, and four of the six kinds the
deck had just named are not surveillance technology. The hook is now `Surveillance technology
meets Chapter 2-19.` The frame's own dek had the scope right the whole time, which is the shape of
all three: **the deks and the locators were careful and the display type was not.**

The fourth was a numerals row the judge read out of this file after it had been repaired and
re-stamped. It is recorded because a judge reading a committed run record is reading the run's own
testimony, and a stale gate table is a run certifying a failure that no longer exists.

### The thesis was on no frame at all

Both the flow critic and the reader judge found it independently, and the reader judge put the
cost plainly: the caption says `The forbidding one is the weaker instrument` and on LinkedIn that
line sits behind a see-more tap, so a reader who swipes and does not expand gets nine frames whose
plain reading is that Austin banned AI cameras in its parks. **That is the exact overstatement
`claims.json` forbids in capitals.**

Frame 7 now carries it, immediately after the page turn pays off, and both halves are sourced
rather than interpreted: `The April ordinance weighs it. This one directs a manager not to
consider it.` The comparison the caption draws is left to the caption. The frame states the
asymmetry and lets a reader see it.

### A number was typed on a deck whose first law is that no number is typed

`aggregates.json` and this record both called the interval **thirteen weeks**. April 23rd, 2026 to
August 12th, 2026 is **111 days, fifteen weeks and six days**, computed rather than typed. It was
on no slide and in no caption so it failed no gate, and it sat in the entry explaining why the
interval is deliberately not computed. A wrong number inside the paragraph that says a number was
withheld is the sharpest available demonstration of why the law exists, and it is left recorded
rather than quietly corrected.

### The coil that read as a lens, twice

Frame 1's bay held a roll of chain link seen end on. A first-round critic called it a dome camera,
it was redrawn with a spiral winding, banding straps and a barrel to remove every lens cue, and
the integrity judge called it a target anyway. **A circular form in that bay was not worth
defending on a deck about cameras**, so the bay now carries a stack of flat fence panels, which is
the same material as a stock item and has no circular form in it at all. L2 is the law that stops
the deck inventing the one thing the record does not contain, and the honest reading of two
independent judges is the measurement that matters here.

### A hashtag was a proper noun outside claim coverage

The caption publishes `#TRUSTAct`. A judge went looking for it in `claims.json`, did not find it,
was ready to call it a fabrication, then found it in the fetched resolution and withdrew the
finding in writing. The resolution reads `codified at City Code Chapter 2-19 and known as the ~'
TRUST Act.` with the scan garbling the opening quotation mark.

The name was correct and it was outside claim id coverage, and **for a proper noun published to
readers that is the same defect as an unsourced numeral.** c32 now carries it, with the garbled
mark kept so the string can still be found in the document. The check the run was missing is the
one the judge performed by hand: every proper noun on a published surface, the caption's tag block
included, traced to a claim.

### The L5 locator stopped tripping `label_guard`, without weakening the locator

`label_guard` reads the capitalised run beside a claim id, and the locator's instruction words
were landing in that window: READ, FULL, BOTH, PAGES, none of which is a claim about what a body
did. The citation stays in capitals, because it is the citation, and the extent went to lower
case, because it is a sentence about a search. `RESOLUTION 20260812-017 / read in full, both
pages`. The gate now reports every printed label tracing to its claim's own words, and the
locator still names the document and the extent read on all three frames that carry one.

That is the answer this file argued for two sections earlier and it is worth saying that it cost
the deck nothing. The alternative, adding claims until READ and FULL traced to something, would
have been the gate writing the record.

### The same discipline, applied to the caption

The caption read `This one directs a manager. It creates no offense and reaches only what the city
has yet to buy.` **No claim supports the first half**, and the same sentence was refused on a
frame earlier in this run for exactly that reason, so it should not have survived in the copy a
reader meets first.

A contrast that IS observable was checked and refused as well. The resolution's two pages contain
no instance of penalty, offense, violation or enforce; the ordinance contains penalty once. The
ordinance's is a requirement that a CITY CONTRACT WITH A THIRD PARTY carry penalties for breaching
a surveillance use policy, which is not a penalty for violating the ordinance, so writing "the
April measure names a penalty and this one names none" would have swapped one unsupported
sentence for a better dressed one.

What was left is the contrast the caption's own preceding sentences already carry, a codified
chapter that gates a purchase on council approval and a filed assessment against a resolution that
directs an officer. The analytical line, `The forbidding one is the weaker instrument`, stays,
because it rests on those sourced facts rather than asserting a legal conclusion of its own.

### The sources block published a computation that did not happen, again

`sources_block.py` appends `Day counts computed in compute.py from the source dates above.`
whenever any aggregate declares a `duration` or a `span`. Its own comment records why that line is
conditional: the 2026-08-26 deck published it unconditionally over a `compute.py` that parses no
date, an integrity judge called it a hard fail, and the gate's comment says in as many words that
**a line claiming a computation is exactly the defect `compute.py` exists to close.**

This deck fired it through the `kind` field. Its only durations are the two instances of `four
weeks`, and both are QUOTED verbatim from c17 rather than computed. Their own notes said so, and
they were still labelled `duration`, so the block published a provenance claim about arithmetic
this deck deliberately never performed. The interval between the two instruments is in
`deliberately_not_computed` for the same reason.

The label was wrong rather than the line. `kind` is now `quoted_duration` on both, the line is
gone, and the two counts the block itself computes, `two official records`, are declared with the
computation that produced them.

**That is the second time in one run that a correct gate fired off a field nobody had checked**,
the first being `label_guard` reading the L5 locator. Both are the same shape as the acceptance
truncation: the check was right and its INPUT was not what anybody thought it was.

## SCORING ROUND TWO, AND THE DECK'S THESIS WAS FALSE

| lens | score | hard fails | ship |
|---|---|---|---|
| integrity | 5.92 | 2 | no |
| craft | 7.18 | 0 | yes |
| reader | 6.69 | 1 | no |

**THE FINDING THAT DECIDED THE RUN.** The deck argued that City Code Chapter 2-19 WEIGHED
artificial intelligence as one of ten privacy assessment factors in April, and that the August
resolution turned it into a bar thirteen weeks later. Section **2-19-9 PROHIBITED TECHNOLOGIES**
of the same ordinance reads:

> The following surveillance technologies or data uses are not permitted ... **(B) artificial
> intelligence or machine learning tools, except as consistent with City policy**

**April had already said no.** The run had the whole fourteen page extraction in hand, cited six
other sections of it, and never read the section six pages past the one its argument stood on. A
sweep run after the finding shows the ordinance mentions artificial intelligence in **twelve
places across five provisions** and the run had read one.

Nothing was published. What this cost is a scoring round and a rebuilt spine, and the second spine
is better than the first because it is what the whole instrument says.

### The spine now

**April prohibited the tools with a door in it. August closed the door and narrowed the room.**

- The April prohibition reaches artificial intelligence or machine learning TOOLS across the city
  and carries an exception, `except as consistent with City policy`.
- The August clause reaches a camera or drone in the PARKS, carries no exception at all, and binds
  one officer for one kind of purchase.

Frame 5's fence with a single gate leaf turned out to be the right drawing for a prohibition with
an exception in it, which is not what it was drawn to be. Its hook went from `Surveillance
technology meets Chapter 2-19.` to `April had already listed the tools.`, its stencil from
`CITY CODE 2-19-3 COUNCIL APPROVAL BEFORE (B) ACQUIRING` to `CITY CODE 2-19-9 NOT PERMITTED (B)
ARTIFICIAL INTELLIGENCE`, and frame 7's thesis line from `The April ordinance weighs it. This one
directs a manager not to consider it.` to `April had already listed those tools as not permitted.
That listing carries an exception and this clause carries none.`

Seven claims were added for the sections the run should have read: c33 and c34 the prohibition and
its artificial intelligence entry, c35 the facial recognition entry beside it, c36 the
`Except as otherwise permitted in this chapter` carve out that opens 2-19-3, c37 and c38 the two
express exception sections, and c39 the surveillance use policy's own duty to describe a
technology's machine learning capabilities.

### The check that was missing, in the judge's own words

> Before a deck asserts a contrast between two instruments, grep the FULL snapshot of BOTH
> documents for the subject noun and either claim or explicitly reject every place it appears.

That sweep is now run and its disposition is in `claims.json`. The resolution mentions artificial
intelligence in its one clause and nowhere else. The ordinance mentions it twelve times. Three
provisions are claimed, four more are recorded in `rejected` as read and not carried. **A deck
that argues from one section of a document it has fetched in full has not read the document.**

### Two hard fails that were not fails

Both judges reported that `claims.json` held 31 claims and no c32 for the TRUST Act name, and the
integrity judge computed the source_type split to prove it. **The file held 32 with c32 when they
read it and holds 39 now.** They read a state that existed for a few minutes between the c31 and
c32 additions, which is a hazard of scoring a run that is still repairing itself.

The lesson is not that the judges were careless. It is that **`runs/carousel/2026-09-08/claims.json`
really was four claims stale**, because it is written at Phase 6 and refreshed at Phase 16, and a
judge reading the run directory rather than the scratch directory sees a record the deck has
outgrown. That is a real defect with a real fix, and it is why the artifact copy happens before
the panel from now on.
