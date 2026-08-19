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

## Proposals, which this run may not carry out itself

1. **Wire `coherence_check.py` into `guards.yml` and into Phase 12.** The gate is built, self
   tested and run by hand this run. `.github/workflows/**` and `prompts/daily_routine.md` are
   `human` owned, so a run cannot connect its own gate to CI. Until a maintainer wires it, the gate
   protects only the runs that remember to call it, which is the exact shape of the defect it was
   written for.
2. **The Legistar Web API belongs in the sources registry.** `webapi.legistar.com` serves agenda
   item text, matter status and voting histories as JSON for Denton, Dallas, El Paso, League City
   and Brazoria County, where the Legistar HTML calendars publish meeting dates and no item text.
   Nine items were left partly unconfirmed this run for want of that route.
3. **A county gazetteer for Texas cities.** `assets/geo/tx-places.json` carries counties and
   statistical areas but no cities, so a source naming a town cannot be resolved to a county and
   the item is held. That is the correct behaviour today and it costs real items.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 18 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 5 warn(s) |
| aggregates     | PASS   | 7 declared and re-derived |
| assembly       | PASS   | 9 slide(s), 2.27 MB, vector |
| score          | ABSENT | score.json not written yet |
| dossiers       | PASS   | 32,599 chars planned |
| caption        | PASS   | 150 words |
<!-- gate-status:end -->
