# Run record, August 19th, 2026

Carousel No. 3. Story `tx-2026-0072`, the Governor's August 3rd data center audit directive and
what it has actually done to the interconnection queue's own clock.

## The record

**Worklist cleared in full.** The selector named 46 items. All 46 were re-verified against one
primary source each, and 50 items carry a dated movement line for today. The selector now reports
0 due.

**Movement coverage went from 19 of 61 to 61 of 61.** Before this run, two thirds of the record
carried no movement log at all while `last_verified` stamps advanced behind them, so "How this
decision moved" rendered empty on the majority of the record. Every item now has one.

**Real movement found.**

- `tx-2026-0072`. The directive has already cost a deadline. ERCOT said on August 3rd it would not
  tell service providers how any large load is classified in the Batch Zero study by the August 7th
  deadline, and that it would ask the commission for a good cause exception ahead of the August 20th
  open meeting. The Governor's office said on August 18th that the Data Center Coalition will comply
  and that one data center that could not comply ended operations before construction began.
- `tx-2026-0069`. The Energy Forge One JETI application gained a posted agreement dated July 24th.
  The application is still not executed.
- `tx-2026-0015`. The NRC reactor licensing rule took a correction on July 27th and still closes
  August 31st.
- `tx-2026-0052`. Brazoria County adopted two license plate reader agreements on July 31st, with the
  Department of Public Safety and with the Houston High Intensity Drug Trafficking Area. Those are
  discovery candidates rather than movement on the item itself.

**THE RUN'S OWN WORST MOMENT, AND WHAT CAUGHT IT.** The commission's filing search and calendar
feed returned HTTP 503 to every fetch across the whole run, and to the scouts before that.
`tx-2026-0001`, `tx-2026-0002`, `tx-2026-0003` and `tx-2026-0024` were written up as unconfirmed
and committed that way.

Reading `SOURCES_FIELD_LOG.md` to write this run's entry is what caught it. That file already
carries the rule, in this project's own words, that a tool-level failure is not a property of the
source, and an entry from 2026-08-16 recording these exact hosts answering 200 to curl with a
browser User-Agent after returning 402 to a different client.

Retested. All four answered 200. The calendar returned 12,722 bytes and 32 entries, and the three
dockets returned 67, 34 and 2,000 filings. **Project 58482 had taken a comment from Modern Tex
Consulting on August 18th that this run was about to miss entirely.** The August 20th and
August 21st open meetings and the September 4th comment deadline are now confirmed against the feed
rather than resting on a market notice that names one of them in passing. All four notes were
replaced rather than left standing beside the truth.

Three status codes have now been recorded against these hosts by three clients on three days, 402
and 503 and 200, and the host was serving on all three. The lesson is not about PUCT. It is that a
status code is a fact about the fetcher, and that a run which writes its field log entry BEFORE it
finishes its worklist gets to use what the file already knows.

**What remains genuinely unconfirmed**, recorded as what is unknown rather than as what a fetch did.

- Government Code Chapter 2054 is published in a form that stops at Section 2054.0702, short of the
  three Subchapter S enactments `tx-2026-0008` and `tx-2026-0025` rest on. The provisions are not
  gone. The retrieval is.
- Nine items sit on agenda portals that publish meeting dates without item text, so what is
  confirmed for them is that the body met and not what it did. The Legistar Web API fixed five of
  those and there is no equivalent for the rest.

**A near miss worth recording.** Two El Paso items were close to being written down as overstated.
The Legistar Matters endpoint shows both "Agenda Ready" with a null passed date, which is the exact
shape of the Houston ISD board policy the last run flagged. The Histories endpoint carries the
motion, the second and a PassedFlag of 1 on both. The record was right and the status field is the
unreliable half. **`MatterStatusName` is not evidence. `/Histories` is.**

**Backlog holds at 3**, the three items exempt by name. Neither can be cleared today, because the
source that would name their geography is the one that is not answering.

## Admitted and held

**Nothing admitted this run.** The strongest candidate the scouts returned is the Atlas Energy and
Kodiak driverless proppant fleet in the Permian, which has dated primary corporate sources and a
schedule taking the fleet from 28 trucks to 100. **It is held in the seed because no source names
its Texas county.** The company's own release names the Permian Basin and its Austin headquarters
and nothing else, and the repo's gazetteer carries counties rather than cities, so Kermit cannot be
resolved to Winkler from data this project holds. A statewide flag would be a claim about scope
nobody checked, which the admission rule says is worse than holding it.

That is the rule working rather than failing. The item keeps its research and a later run promotes
it when a source names the place.

## Discoverability signoff

- **One decision's card, opened as an image.** `docs/og/tx-2026-0073.png`, the run's newest item,
  94,282 bytes. LOOKED AT.
- **`/questions/`, read as a reader.** LOOKED AT. Seven shapes, each with its own count: what each
  decision is at 61, who decides at 61, how the public can take part at 57, where a comment window
  is open at 4, where in Texas each applies at 58, what has been decided at 61. The questions read
  as things somebody would type. The comment window count of 4 is narrower than the eight entries
  `llms.txt` lists as open right now, and that is correct rather than a contradiction, because the
  llms list counts any dated way in and includes open meetings.
- **The `Open right now` section of `llms.txt`.** LOOKED AT. Eight entries. Cross checked against
  the windows Phase 3 re-verified and nothing closed today is still listed.
- **`/sources/`.** LOOKED AT. **184 of 256 claims rest on a primary document, across 99 documents
  from 51 publishers**, which is 71.9 percent. Nothing admitted this run, so this run did not move
  it. The top publisher is `tcss.legis.texas.gov`, the Texas statutes site, which is unambiguously
  a primary source, and its own page lists three documents all marked primary official.
  **A false finding was nearly recorded here.** The row reads "25 claims 3 primary 3 documents" and
  that looked like 22 claims failing to be primary. The publisher's own page shows the primary
  column counts DOCUMENTS, and all three of its documents are primary. Checked before writing.
- **`/topic/`.** LOOKED AT as a hub. Counted the beats against the ledger rather than by eye.
- **`/place/`.** LOOKED AT. The record names 50 of 254 counties across 23 statistical areas. Nothing
  landed anywhere this run, so no place should have changed and none did.

## The instruments

Nine checks run by exit code, all 0.

`gridwatch_pagecheck`, `waterwatch_pagecheck`, `waterwatch_page --self-test`, `media_check`,
`schema_check`, `og --self-test`, `favicon --self-test`, `truetype --self-test`,
`indexnow --self-test`.

No presentation fix was needed in `gridwatch_page.py` or `waterwatch_page.py` and neither was
touched.

## The third scoring pass held, and what it found

**6.932 against a 7.0 threshold.** The arithmetic is 1.904 + 1.300 + 1.260 + 0.864 + 0.864 + 0.740.
Artwork 6.8, claim integrity 6.5, story 7.0, sequence 7.2, voice 7.2, variety 7.4. Nothing was
rounded, and the scorer noted that a full point more on artwork would still not have carried it, so
the gap was never one judgment call wide.

**It held on new ground, and the new ground was a pattern rather than an incident.** Cutting slide 4
after the second pass reached `copy.json`, the renders, the gates, the topics ledger and the
techniques array. It did not reach five other artifacts. Every gate passed on all five.

- `first_comment.txt`, the PUBLISHED sources block, listed seven claim ids. The deck prints sixteen.
  Nine resolved to nothing for a reader, including all three claims this run added and four of the
  five printed on the closing frame, which is the one frame that asks a reader to act.
- `computed.json` said 18 verified claims against 21.
- `aggregates.json` declared five figures against the pre-cut slide files, so the file whose whole
  job is proving traceability no longer described the deck.
- `storyboard.md` was stale for four of eight blocks.
- **`ledger/carousel/artwork.json` is committed cross-run memory and it was wrong.** It named slide 6
  for a paper inversion that ships at slide 5, named slide 7 for two accent fills that ship at
  slide 6, and listed nine camera moves beside a `slides: 8` field. The next run reads that file to
  decide what it may not reach for again.

## The fourth pass, and what was rebuilt

Everything above was corrected, and the two artwork faults the scorer named were rebuilt rather
than patched.

**Slide 6 was redrawn.** The four label plates sat 37 pixels off the four band boundaries beneath
them, because the words were laid out in a safe-area inset box while the bands were drawn full
bleed. Two layers, two independent statements of the same geometry, and only one of them moved when
the safe zone was fixed. The bands are still four full-bleed vertical terrazzo inlays and each
guardrail's word is now set ALONG its own band. Band centre, word length and knockout all come from
one constant substituted into both layers, so there is nothing left for them to disagree about.
NEIGHBORHOODS sets on one line at the same size as every other word. It had been broken across two
lines with no hyphen, which made one word read as two, in the largest type on the frame.

**Slide 4 was built to its own dossier.** It had shipped as three rows of tabular mono on flat
ground with three brass hairlines, against a plan calling for a chart table with measured plates, a
low lamp and plate shadows as the frame's darkest tone. It now has the table as a slab in
perspective with a lit far edge and a brass front lip, the lamp at the upper left, and a real cast
shadow per plate whose corners are projected away from the lamp point along their own rays, so the
throws fan and the near plate throws longest. Machine QA's dead lower zone FAIL on this frame is
gone and so are its three contrast warnings.

**Slide 8 lost an orphan and gained a connection.** The small brass day tick under the lit cell was
the mark for a label that left with the rewrite, so it meant nothing to a reader and it is gone. The
lit cell now throws a shaft down onto the dated list, which was the answer to two compositions
stacked with a gap between them.

**The September 4th row was split in two.** It had read "Public comment deadline. Project 58482 took
a comment on August 18th." `c20` verifies a September 4th deadline on the commission's calendar and
names no docket. `c21` verifies a filing in Project 58482 dated August 18th. Nothing fetched links
them and a dated row is read as one fact. September 4th now carries only what the calendar verifies
and says plainly that the calendar names no docket against it, and Project 58482 has its own row
naming the proposed rule a reader can actually file into. That also fixes the scorer's other
complaint, that the one row a reader could act on was the under-specified one.

**A collision the machine did not see.** "September 4th, 2026" is 296 pixels of JetBrains Mono
advance in what was a 260 pixel column, so the ink printed straight through the sentence beside it.
Machine QA reported zero fails, because it compares ELEMENT boxes and the element was 260 wide. It
was caught by opening the render. The column is now 312.

**And a gate that was measuring the wrong thing.** `bespoke_check` failed the deck at 0.5508 against
a 0.55 line. On the closest pair it shared 50 tokens and exactly ONE of them was a drawing call. The
other 49 were the standing masthead this run's own coherence upgrade had put on every frame, which
is the whole point of a masthead. The gate now strips anything carrying a `tx-` class with its
subtree and its CSS. **The two shipped decks move 0.3997 to 0.4061 and 0.2298 to 0.2300**, because
neither carried that masthead, and that is the evidence the change is surgical rather than a loosened
line. This deck measures 0.2817.

## The fourth pass held too, and the run stops

**6.82, down from 6.932.** Claim integrity rose 6.5 to 7.5 and sequence rose 7.2 to 7.5, which is
the bookkeeping and the close. Artwork fell 6.8 to 6.5, story 7.0 to 6.5 and voice 7.2 to 6.5, and
the scorer put all three on one cause in one sentence. **The deck is procedurally impeccable and has
no place and no person in it.** Swap ERCOT for PJM and every line survives.

That is not a frame to redraw. It is what the admission rule produced when it correctly refused to
guess a county for a statewide procedural story, and a fifth pass would be polishing further away
from it. Four passes, 6.51 to 6.87 to 6.932 to 6.82, and the number stopped climbing. The run
commits its evidence to this branch and merges nothing.

Three findings from that pass were still fixed, because each was simply wrong rather than a matter
of taste.

- **Slide 7 drew three hollow boxes where the record has one gap.** The blank row was being
  segmented like every other row and each segment drawn hollow. That slide's own acceptance line
  says exactly one field is empty, because two would imply a count the record does not carry.
- **`ledger/carousel/artwork.json` still carried 0.5314**, the bespoke figure measured while the
  gate was counting the masthead. It is 0.2717.
- **The storyboard's value arc still listed nine beats** and named the inversion and the trough by
  their pre-cut numbers.

And the caption said the deck closes on three dates. Splitting the September 4th row made it four
ways in, so it now says every date and docket.

## THE WORST THING IN THIS RUN, found on the fifth pass

**Slide 3 printed a taxonomy nobody published.** Its legend read `base load`, `studied`, `excluded`,
set as three named classification categories directly under the attribution chip
`ERCOT market notice M-A080326-01 c2`. **No claim in the claims file names any Batch Zero
classification category.** `c2` says only that ERCOT would not notify providers of "how any Large
Load is classified". The storyboard's own plan for that frame used generic labels. The shipped copy
substituted an invented taxonomy, and a reader would take those three words as ERCOT's classes.

It survived four scoring passes, every gate in the suite and a pixel review. `claims_check` proves
each claim is fetched and quoted. `copy_sync_check` proves the slides say what the copy says, and
the copy said it. `aggregate_check` reads numerals, and these are words. Nothing in the machine asks
the one question that would have caught it, which is whether a NOUN on a slide traces to a source
the way a numeral has to.

That is the founding promise of this project broken, on the single frame whose entire argument is
that nobody was told the answer. The legend is now one row reading **`no class stated`**, which is
what `c2` supports and nothing more, so the key has exactly one entry and that entry says nothing
can be keyed. The frame is stronger for it.

**The generalisation belongs in `GATE_LESSONS.md`.** The compute-not-generate law is enforced on
numerals by `numeral_lint` and `aggregate_check`, and a named category is a claim about the world in
exactly the way a number is. A machine that checks its arithmetic and not its nouns has secured half
the surface.

## Two more the fifth pass found

**Slide 5 never executed its own acceptance line.** That dossier says the words differing between
the two wordings are marked in pecos, and both quotes shipped as uniform ink for five passes, so the
turn the whole deck is built around gave a reader no help finding the difference. They are now
marked, the words themselves untouched and still verbatim, and the foot says what the colour means.

**The storyboard's synthesis still carried pre-cut numbering** after the value arc was fixed, and
one line contradicted the top of the same file about which frame the cut took. Both corrected. The
renumbering had reached the arc and the artwork ledger and stopped there, which is the third time in
one run that a correction reached some of the places a fact lives and not all of them.

## Proposals, which this run may not carry out itself

1. **Wire `coherence_check.py` into `guards.yml` and into Phase 12.** The gate is built, self
   tested and run by hand this run. `.github/workflows/**` and `prompts/daily_routine.md` are
   `human` owned, so a run cannot connect its own gate to CI. Until a maintainer wires it, the gate
   protects only the runs that remember to call it, which is the exact shape of the defect it was
   written for.
2. **Wire `sources_block.py --check` into `guards.yml` and into Phase 12,** for the same reason. A
   reader who cannot resolve a claim id printed on a slide has been handed a citation that does not
   cite. Nine of sixteen were unreachable today and no gate in the suite was looking.
3. **Teach `aggregate_check`'s detector to read a numeral and its unit across sibling text nodes.**
   Slide 2 sets "4" at 52px beside "DAYS AHEAD" at 26px, which must be two elements to be two sizes,
   and the detector reads one text node at a time. Both of this deck's computed durations are
   invisible to it, and declaring them turns the gate red, so they ship undeclared. The fix needs the
   render report to carry sibling adjacency, which is a format change feeding a consumer change, and
   that combination already put one red build on the board today.
4. **Teach machine QA to measure text collisions on the INK rather than the element box.** An
   overflowing nowrap string inside a fixed width flex item printed through its neighbour today with
   zero fails reported.
5. **The Legistar Web API belongs in the sources registry.** `webapi.legistar.com` serves agenda
   item text, matter status and voting histories as JSON for Denton, Dallas, El Paso, League City
   and Brazoria County, where the Legistar HTML calendars publish meeting dates and no item text.
   Nine items were left partly unconfirmed this run for want of that route.
6. **A gate that traces NOUNS, not only numerals.** This is the run's most important proposal and
   it comes straight off the slide 3 defect above. Every numeral on a slide must resolve to a
   computed value or a quoted figure, and `numeral_lint` and `aggregate_check` enforce it. A named
   category, a named body, a named place or a named status is a claim about the world in exactly
   the same way, and nothing checks those at all. The shape is the one `sources_block` uses: pull
   the proper nouns and quoted-looking terms out of `copy.json`, and fail any that appear in no
   claim's text, quote or publisher. `scripts/carousel/**` is the upgrade lane and this is buildable
   there, but it needs a run that is not also shipping a deck, because a first pass will be noisy
   and tuning it against real copy is the work.
7. **An entry in `knowledge/shared/GATE_LESSONS.md` for the masthead measurement.** The
   generalisation is worth more than the instance. When a gate subtracts what a deck shares on
   purpose, the subtraction is a LIST, and a list goes stale the moment the product starts sharing
   something new. The question to ask a gate is not whether its exclusions are correct. It is what
   the product began sharing after those exclusions were written.
8. **A county gazetteer for Texas cities.** `assets/geo/tx-places.json` carries counties and
   statistical areas but no cities, so a source naming a town cannot be resolved to a county and
   the item is held. That is the correct behaviour today and it costs real items.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 21 verified claim(s) |
| render         | PASS   | 8 slide(s) |
| qa             | WARN   | 0 fail(s), 6 warn(s) |
| aggregates     | PASS   | 12 declared and re-derived |
| assembly       | PASS   | 8 slide(s), 2.25 MB, vector |
| score          | FAIL   | 6.62, below threshold |
| dossiers       | PASS   | 30,755 chars planned |
| caption        | PASS   | 160 words |
<!-- gate-status:end -->
