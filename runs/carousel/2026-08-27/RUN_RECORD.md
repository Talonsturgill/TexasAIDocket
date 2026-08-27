# Run record, 2026-08-27, carousel no. 9

## THE RECORD, which is the first deliverable and the one that ships whatever else happens

**The worklist was cleared in full.** `docket_staleness` named four items due on the two day
leash and all four were re-verified. `reverify.py --apply` fetched twelve urls behind forty
claims, four answered 304 and eight sent a body, and none failed to answer. One item was stamped
by the script and three needed a person.

**Two claims were corrected and both corrections matter.**

`tx-2026-0072-c7` cited the commission's rolling calendar feed for an open meeting on August
20th. That meeting has been held and has come off the feed, so the claim pointed at a url that
no longer carried it and would have been re-flagged every run forever. It now cites the December
17th open meeting, which is the date the audit's own filed schedule ends on, and the item's
participation note points a reader there instead of at a meeting that has happened.

`tx-2026-0090-c7` quoted the National Science Foundation saying researchers anywhere in the
country should get their hands on this equipment. The stored quote stopped at "on this
equipment." and gave the sentence a full stop the source does not have. The speaker actually
carried on, "and work together to pursue those ideas". A quote trimmed to a shorter claim is a
quote this project broke, and it now runs to the end.

**Ten decisions were admitted.** Six cleared the promotion gate from the seed on the first pass.
`tx-2026-0102`, the UT Southwestern item stating that artificial intelligence has replaced more
than 91 percent of the human grading of medical students' clinical notes, was held for a missing
verification stamp, was re-fetched, held both its quotes word for word, and went in. Three more
were written from this run's scouts and verified against their own primary sources.

| id | what |
|---|---|
| tx-2026-0084 | Amazon's Austin robotics manufacturing siting. **This run's deck is built on it** |
| tx-2026-0085 | NSF's self driving semiconductor laboratory at Rice |
| tx-2026-0086 | NSF's open access robot run alloy laboratory at Texas A and M |
| tx-2026-0087 | Denton City Council's data center moratorium resolution |
| tx-2026-0088 | the RELLIS abatement reassigned in Brazos County |
| tx-2026-0089 | the House charge on using artificial intelligence against fraud in state spending |
| tx-2026-0102 | UT Southwestern grading clinical exam notes by machine |
| tx-2026-0104 | NSF's five year Science and Technology Center on human and robot co adaptation at UT Austin |
| tx-2026-0105 | the Texas Politics Project's August poll on data centers |
| tx-2026-0106 | Austin City Council's Item 61, taken up today, to write data centers into the land development code |

The record now holds **91 items and 431 claims**, and `docket_build --validate` is clean on
every gate including staleness.

## A BOUNDARY BREACH FOUND IN THE PUBLISHED RECORD, and repaired

**`tx-2026-0089` reached the public record citing four claims whose only source sat under
`capitol.texas.gov/tlodocs/`, which robots.txt disallows for every agent.** It was admitted from
the seed on August 22nd. Nothing between the seed and the ledger checks a claim's url against
the crawl boundary, so an item can be published that this project may never re-fetch to
re-verify. That makes it stale by construction, and it would have hard failed the six day leash
within a day.

The repair is real rather than cosmetic. `www.house.texas.gov` serves `User-agent: * /
Disallow:`, an empty disallow, and the Speaker's interim charges for every House committee are
published there in full. The item is rewritten around that document and every claim on it is
verified against it. The charge text is identical, so nothing about what the record states
changed.

**The gap itself is unfixed** and is written up as a proposal below.

## The backlog

Three entries at wake and three at close, all of them the same three geography exemptions that
predate the rule. Held steady, which the routine calls acceptable. The one entry that is
genuinely clearable is written up as a proposal below, because clearing it needs a file this
actor does not own.

## Sources

Every finding this run made about a source is appended to
`knowledge/shared/SOURCES_FIELD_LOG.md`, which is the file this actor owns. The registry itself
was not touched. The findings worth naming here are the `/tlodocs/` breach above, the
`house.texas.gov` substitute that repaired it, and one that would have cost a later run an
afternoon: **the Office of the Texas Governor's post slugs are not guessable, and a wrong guess
returns a 404 with a 90,489 byte body**, so a run checking only for a non-empty response reads
the 404 page as content.

`puc.texas.gov` answered a browser User-Agent with 200 for this session and its calendar feed
parsed to thirty one items, while a scout on the same beat recorded 503 from that host on four
attempts in the same hour. **The host is intermittent rather than closed**, and one run's
failure there is not a finding about the source.

## Instrument once over

Both instruments are green. `gridwatch_pagecheck` and `waterwatch_pagecheck` each report the
page current and holding its promises, and `waterwatch_page --self-test` passes. Nothing was
edited in either lane.

The discoverability surfaces are all clean by exit code. `media_check`, `schema_check`,
`og --self-test`, `favicon --self-test`, `truetype --self-test`, `indexnow --self-test` and
`seo_check` all returned 0.

**The scanner's daily ceiling could NOT be checked.** No Supabase connector is available to this
session, so the query in the routine had nowhere to run. That is the routine's third outcome,
which says to record it and carry on, and it is recorded here rather than left silent.

## Discoverability signoff

- **One decision's card, opened as an image.** `docs/og/tx-2026-0103.png`, which was the newest
  item at wake. The headline wraps after "campuses", "the" and "Department's", all places a
  reader would break it, and the wrapper truncates with an ellipsis after "science" on a whole
  word. Legible and correct.
- **`/questions/`, read as a reader.** Twelve questions, and they read as things somebody would
  type. "How the public can take part" and "Where a comment window is open" are the two doing
  real work. The counters print with a leading zero, so an answer count of five reads `05`,
  which is the row's own style rather than a fault.
- **The `Open right now` section of `llms.txt`.** Eight entries, cross checked against Phase 3's
  own list of open windows. All six items with a live close date are present. `tx-2026-0077`,
  whose window closed on the 25th, and `tx-2026-0073`, whose closed on the 20th, are both
  correctly gone. The build ran after the record moved.
- **`/sources/`.** The share at the top reads **320 of 393 claims resting on a primary
  document**, across 146 documents from 63 publishers, against 320 of 392 yesterday. **The share
  moved DOWN by one claim's worth**, and the honest reason is that at the time it was read this
  run had corrected claims without adding primary ones. Every one of the ten items admitted
  after that reading cites a primary source, so the next reading moves it up. The top publisher
  is `interchange.puc.texas.gov` with 40 claims across 11 documents, which is the commission's
  own filing index and primary by any reading. `lrl.texas.gov` still appears with 12 claims,
  which is the citation half of the boundary question and is historical rather than new.
- **`/topic/`, counting one card against its own page.** The eight beat cards sum to 81, which is
  what the hub's own `All` figure and the front page counter printed at the time of reading. The
  `power-and-the-grid` card says 8 decisions and 1 still open to comment, and the beat's own page
  lists 8 of 81 with exactly one open window, `tx-2026-0002`. Its card prints "8 days left to
  comment, closes September 4th", which is a claim about TODAY and is correct.
- **`/place/`, for the place this run landed something in.** The hub says the record names 59 of
  the state's 254 counties across 27 statistical areas. Travis County took four items this run
  and Austin-Round Rock-San Marcos was already carrying 12 before them, so the place existed
  rather than being created. **The post-admission rebuild happens in Phase 16**, so the counts on
  the live hub at the time of this reading are yesterday's, which is the expected order and not
  a fault.
