# Run record, 2026-09-05

Branch `claude/daily-2026-09-05`. One routine, two deliverables, the record first.

## Phase 0, wake

`guards_local.py --fast --only Ownership` exit 0, so `core.hooksPath` is wired to `.githooks`
and the gate that used to skip when it was not now passes on having been asked. Git identity set
to the owner's in the fresh clone, per CLAUDE.md. `docket_build --validate` and
`ownership_check --self-test` both exit 0 on the clean checkout, so nothing shipped past a gate
yesterday. `bootstrap.sh` exit 0. No `prompts/NEXT_RUN.md`, so no story was queued.

**Off the table today**, read before anything was chosen. All fifteen entries in
`ledger/carousel/topics.json` fall inside the thirty day window, so every shipped deck's topic is
excluded. Opening moves from the last six runs are off the caption menu, being the two things,
the object twice, the before and after, the plain question and the place. Structures from the
last three are off, being pivot, question and answer, and two columns.

## Phase 1, craft refresh

One rotating focus, chosen against where the last several panels actually lost craft marks
rather than against the story, since the story was not yet picked. **Legibility at feed scale and
the single dominant focal.** The finding worth handing the directors room is that attention
studies of dispersed compositions measure roughly half the central concentration of ones with a
single dominant focal, and that formal guidance for visualisation thumbnails is thin enough that
the honest move is to test at 432px rather than to trust a rule. That is the same instruction the
technique library already gives under TYPE AND CAROUSEL MECHANICS, so this run treats it as
confirmation rather than as news, and the operative sentence for the dossiers is that a frame
declares ONE focal and it is an area.

Yesterday's focus was absence and reference frames. Not repeated, deliberately, and the reason is
in Phase 8.

## Phase 2, the worklist

`docket_staleness --today 2026-09-05` exit 0. **95 of 105 items due, nothing rotten, nothing
deferred, and no `--budget` passed.** The leash is two days for every item whatever its status,
so the worklist is however long that is, and today it was 95.

## Phase 3, re-verify

`reverify.py --today 2026-09-05 --apply` exit 1, which is the code that means the report lists
what needs a person. 173 urls behind 494 claims, 23 answered 304, 147 sent a body, 3 did not
answer. **65 items stamped by the script as checked and unchanged.**

**The 65 deterministic notes were re-worded, which is the part of this phase a machine should not
keep.** The script wrote eight distinct sentences across 65 items, one of them 41 times. Each is
now the item's own sentence about its own decision. `reverify.py --check-notes` exit 0 over 323
checked notes, so no figure was introduced by hand. `docket_build --validate` caught one British
spelling in a note I wrote and it is fixed, which is the gate working on the run rather than on
the previous run.

**The 31 the diff handed back were worked one source at a time**, and most were not sources that
moved. They were sources this checker structurally cannot read. San Angelo and Killeen serve
PDFs, Legistar and the PUCT Interchange serve pages the plain fetcher cannot match, and several
newspapers refuse a bare client. Re-fetched with a browser user agent and a PDF reader, they
confirm. The Federal Register answered 500 twice and confirmed on the third attempt with backoff.

**Two real movements, and one of them was the record telling a reader something untrue.**

`tx-2026-0096` carried status `open` and room `open_meeting` and a title promising the committee
"sits again on September 2nd". Both sittings on the data center cooling water charge have been
held, and the Legislature's upcoming meetings listing no longer carries either, which is what a
past hearing looks like on that page. Status moves to `pending`, the room to `contact_only`, and
the title and summary stop advertising a door that has shut. This is exactly the failure the two
day leash exists to catch, and it is the reason a `decided` item gets the same leash as an open
one.

The two Oncor 765 kV dockets have each taken further filings, so the newest filing-count claim on
each is refreshed against today's index.

**Named as unconfirmed rather than dropped or asserted.** `seguingazette.com` and
`newschannel10.com` now serve a wrapper rather than the article, so the sheriff's words on
`tx-2026-0036` and the commissioners' words on `tx-2026-0046` could not be confirmed this run and
the items say so. Taylor's notice address still answers 404, which is what `tx-2026-0027` already
claims, so that item is confirmed by the absence rather than damaged by it.

**96 of 105 items carry today's stamp and a dated movement line.** `--validate` reports all items
verified within two days.

## The backlog

Three entries at wake and three at close, all of them the ERCOT-region items exempt by name.
`tx-2026-0001`, `tx-2026-0002` and `tx-2026-0007`. **Not cleared, and the reason is a judgement
rather than a shortfall.** Each is a commission proceeding about the ERCOT region. ERCOT is not
Texas, since El Paso and part of the east are outside it, so `statewide: true` would publish a
claim about scope that no source makes, and naming two hundred counties is not what the field is
for. The backlog held steady, which the routine accepts. It did not grow.

## Phase 7, the instruments

`gridwatch_pagecheck` exit 0, `waterwatch_pagecheck` exit 0, `waterwatch_page --self-test` exit 0.
Both instruments read as current and holding their promises. Nothing to fix and nothing stopped.

**The scanner ceiling was NOT checked and this is the one thing in this phase a person should
see.** The Supabase connector is installed and connected at the org level and is
`enabledInChat: false` for this session, so its tools are not loaded and the query cannot be run.
That is not a failed query, it is an unrun one. Per Phase 7 this never blocks the run, and per the
same phase a ceiling nobody is notified about is one you learn about from the people who gave up.
**A maintainer enabling the Supabase connector for this session's environment is what fixes it.**

## Phase 4 and 5, discovery and admission

Polled, in order. PUCT calendar RSS, which named three project numbers with dates and is the
reason this run found that Project 58482's comment deadline fell yesterday and that Project 58555
is an ERCOT ancillary services study rather than an AI matter. PUCT Interchange by control number
with a browser user agent. Texas Register. Federal Register with a comment-date filter, 18 open
windows, all national rather than Texan. CourtListener v4 across the Texas federal districts and
CA5, 8 results, mostly patent suits.

Six scouts, four of them on application beats as the doctrine requires, and all six returned.

**Three items admitted and the ledger closed at 108.** It reached 110 for a few minutes and came
back down, which is not a typo and is explained in the next section.

## THE BEAT THIS RUN WANTED, TOOK, AND GAVE BACK

This is the run's largest finding and it is a contradiction between two authoritative files
rather than a defect in either.

**What was found.** `docket_build.TOPICS` carries eight beats and every one of them is about what
is being DECIDED about AI. `knowledge/shared/APPLICATIONS.md` exists to correct exactly that and
says to put the application layer first. The vocabulary that decides what the record may admit
never carried the correction, so the record has been silently refusing the thing its own doctrine
says matters most.

That is not an inference. Two candidates were sitting in `seed/docket_seed.json` naming it as the
reason they could not be filed, a driverless service opening to the public in Houston and a plant
assembling AI servers in the same county.

**CORRECTED, and the correction is the point.** This section first claimed both candidates had
already been written against the slug `ai-in-the-field` AND the decider type `company` by earlier
runs. A review bot checked the parent revision and that is only half true. Both were written against
`company`. Only the Waymo candidate was written against `ai-in-the-field`, and the Apple one was
filed under `state-policy` until THIS run changed it. So the earlier diagnosis covers the decider
type for both and the beat for one, and presenting this run's own edit as prior evidence was an
overstatement about the strength of the case.

**The second half of the gap had already cost the published record.** `DECIDER_TYPES` had no word
for a company acting alone, so items were filed under the nearest wrong one. `tx-2026-0101`
carried Houston Methodist, a private hospital system, as a `special-district`, which is a unit of
Texas local government. A closed vocabulary with no word for a thing does not stop the thing being
admitted. It makes the record say something false about it instead.

**What was done and then undone.** Both values were added, `site_build.py --self-test` passed with
the blurb check green on both sides of the two file beat change, `--validate` passed, and both
held items promoted cleanly under the new beat. Then `schema_contract.py` asked for its record to
be updated, and `ownership.yaml` refused `config/schema_contract.json` to `daily` on a stated
ground this run agrees with, being that a contract the process changing the data can also rewrite
is not a contract.

So the topic addition was reverted, the contract file was restored, and the two items were removed
from the ledger before anything was committed. **`DECIDER_TYPES` is not tracked by the schema
contract, so that half is wholly inside this lane and it stayed**, along with the `tx-2026-0101`
correction it makes possible.

**Why the items were not simply filed under an existing beat.** Because that is the same fault
this run just corrected. Filing a robotaxi launch under state policy or a server plant under
research would make the record say something false in order to avoid saying nothing, and the
Houston Methodist entry is what that looks like a month later. Both are held on their own claims,
both were re-verified against their sources today, and the held reason is now one file rather
than two.

**The proposal, for a maintainer.** Add `ai-in-the-field` to `docket_build.TOPICS`, the matching
line to `TOPIC_BLURBS` in `scripts/site/site_pages/docket.py`, and the value to
`config/schema_contract.json`. Adding a value to a vocabulary is additive and does not bump
`SPEC_VERSION`, by the contract note in `docket_build.py` itself. The blurb this run wrote and
reverted, offered as a starting point rather than as the answer, was "AI already at work on Texas
ground. Oilfields and farms, freight lanes and plant floors, and who is doing the job differently
now."

**The contradiction worth naming, because a later run will meet it too.** Phase 5 of
`prompts/daily_routine.md` tells a run what to do when it admits a beat the record has never
carried, and describes it as a two file change. It is a three file change, and the third file is
`human`. Either the routine's instruction or the map needs to move, and neither is this lane's to
move.

## What was admitted

Three items, each on its institution's own announcement, each fetched this run, each naming its
county and citing a primary source.

- A Texas A&M materials screening tool the college states is free and openly available.
- Four UT Austin fusion seed grants whose release states the limits of the machine learning
  method alongside its promise, which is a rarer thing for a university to publish than the
  promise alone.
- An Energy Department award to a Houston led team using AI to design magnets that avoid imported
  rare earths.

The gate held all three at first and was right every time. One on a key date kind outside the
vocabulary, one on a British spelling, one on a comma rate of 4.52 against the 3.97 ceiling, and
two on a stamp with no movement line beside it. Each was fixed rather than argued with.

## Discoverability signoff

Six surfaces, opened rather than inferred, on the 2026-09-05 temp build of 667 pages and 108 items.

- **One decision's card, opened as an image.** `og/tx-2026-0124.png`, the run's newest item.
  Opened as a PNG. The headline breaks after "Energy Department", after "research arm funds a"
  and after "Houston led team", which are all places a reader would break it, and the fourth
  line ends on the whole word "design" before the ellipsis rather than on a stump. The wrapper
  cuts on width and this title is longer than the card holds, so the ellipsis is doing its job.
  No defect.
- **`/questions/`, read as a reader.** Opened and read. Eight shapes, and they are questions a
  person would type. What each decision is, who decides, how the public can take part, where a
  comment window is open, where in Texas it applies, what has been decided, what happens next,
  when each one started. The counts differ by shape rather than all reading 108, which is the
  honest behaviour. No shape has stopped making sense against this run's new items.
  **CORRECTED after a review bot read it against the ledger.** This bullet first paired the counts
  with the wrong shapes, saying who decides answered 101 of 108. Every one of the 108 items carries
  a decider name, so who decides answers 108. The 101 is the take part shape, which is every item
  whose room is not an open comment window, and the 7 is the comment shape, which is exactly the
  seven open windows. Counted off the ledger rather than off the page this time.
- **The `Open right now` section of `llms.txt`.** Ten entries, cross checked against what
  Phase 3 moved. tx-2026-0096 is correctly ABSENT, which is the check that matters today. Its
  hearings were held on September 1st and 2nd and this run moved its room from open_meeting to
  contact_only, so a window that shut is no longer advertised as a way in. tx-2026-0109 is
  correctly PRESENT with its September 22nd reset. The build ran after the record moved.
  One correction to my own reading, recorded because the wrong version nearly went in this
  file. A first extraction of this section came back empty and read as a defect. The range
  expression terminated on the heading it started from. The section was populated the whole
  time.
- **`/sources/`, the record's own report card.** The share at the top reads 490 of 568 claims
  resting on a primary document, across 195 documents from 86 publishers. The top publisher is
  `interchange.puc.texas.gov` at 87 claims, which is the commission's own filing index and is a
  primary source, so the heaviest thing this record leans on is a document rather than a report
  about one. Second is `api.nsf.gov`, also primary. Nothing on the top of that list would
  embarrass the promise.
- **`/topic/`, counting one card against its own page.** The hub prints 8 beats. Data centers
  27, defense and federal 2, health and education 10, land water and permitting 14, power and
  the grid 11, research and science 19, state policy 16, health and education 10, surveillance and
  policing 9.
  Those eight sum to 108 and the front page counter row prints 108 decisions tracked, so the
  beats and the counter agree.
  The figure that could have disagreed is the one about TODAY rather than about the record, and
  it does not. Four beats each print "1 still open to comment", which sums to 4. The front page
  prints "04 Doors open to you". The ledger itself holds exactly four items whose room is
  `open_comment` with a close date on or after today, being tx-2026-0016, tx-2026-0075,
  tx-2026-0107 and tx-2026-0118. Three published surfaces and the record agree.
- **`/place/`, for the places this run landed items in.** All three are on the hub with counts.
  Harris County 9, Brazos County 5, Travis County 15. This run admitted one item into each of
  the three, so the hub was rebuilt after the record moved.
