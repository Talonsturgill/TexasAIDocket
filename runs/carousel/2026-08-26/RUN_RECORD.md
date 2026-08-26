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

Filled in at ship.

## Gate table

Written by `gate_status.py --sync`, never by hand.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 30 verified claim(s) |
| render         | WARN   | 9 slide(s), 10 overflow warning(s) |
| qa             | WARN   | 0 fail(s), 33 warn(s) |
| aggregates     | PASS   | 6 declared and re-derived |
| assembly       | PASS   | 9 slide(s), 2.65 MB, vector |
| score          | ABSENT | score.json not written yet |
| dossiers       | PASS   | 39,481 chars planned |
| caption        | PASS   | 263 words |
| craft floor    | WARN   | 9 frame(s), median 1520, floor 274, 3 quiet |
| plan vs render | PASS   | 14 of 59 acceptance item(s) checkable |
| texan          | WARN   | places NONE / body yes / deadline yes / next step yes |
| absences       | WARN   | 2 of 5 scoped to a named document, 3 unscoped |
| completion     | ABSENT | not scored yet |
<!-- gate-status:end -->
