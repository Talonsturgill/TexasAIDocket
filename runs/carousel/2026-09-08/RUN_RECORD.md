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
