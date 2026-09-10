# Run record, 2026-09-10. Carousel no. 20.

The record cleared a 16 item worklist and admitted two items, one of them the deck's own
subject and every one of its twelve claims drawn from a federal document this run fetched and
read. The deck is nine bespoke frames on a certification question rather than a driving one,
and the distinction is the reason this story is not a repeat of carousel no. 5.

## Phase 0, wake

Clean checkout of `origin/main` at `40def58f`, branch `claude/daily-2026-09-10`. Git identity,
email and `core.hooksPath` set before the first write, so both hooks ran on every commit below.
`guards_local.py --fast --only Ownership` passed, three steps green and the CI-only step
skipped as designed. `docket_build.py --validate` and `ownership_check.py --self-test` both
exited 0 at wake, so nothing shipped past a gate on the previous run. No `prompts/NEXT_RUN.md`.

## Phase 1, craft refresh

**Rotating focus: ARTWORK CRAFT, chosen from the panel's own numbers rather than from taste.**
The last three panels scored `artwork_craft` 7.1, 6.8 and 6.5. It carries the heaviest weight in
the rubric at 0.28 and it has fallen three runs running, which no other criterion has done.
`variety` is lower in absolute terms at 6.0, 7.2 and 5.5, and it was already a named focus on a
recent run.

The reading that shaped the plan is `SLIDE_DOSSIER_SPEC.md`'s focal law, because it is the one
place in this repo where a craft lesson is attached to a measured movement: rewriting three
declared focals from LINES to AREAS moved `artwork_craft` from 6.4 to 7.8 in a single run. Every
dossier this run declares an area and names the lightest and darkest thing in its frame.

## Phases 2 and 3, the record

`docket_staleness.py` named **16 items due, nothing rotten, nothing deferred**, and no
`--budget` was passed. Exit 0.

`reverify.py --apply` read 35 urls behind 121 claims. Four answered 304, thirty sent a body, one
did not answer. **Eleven items stamped as checked and unchanged.** Exit 1, which is the report
handing back the five items that needed a person.

### The commission's calendar dropped a deadline, and four claims went with it

`tx-2026-0002` and `tx-2026-0024` each quoted the September 4th public comment deadline out of
the PUCT calendar feed. That feed is a rolling window and an entry comes off it once its date
has passed, which is exactly what happened. The run re-fetched the feed with a browser
User-Agent and confirmed the absence rather than assuming it.

Both items were repaired against sources that keep their own history. `tx-2026-0002`'s two
claims moved onto the Interchange filing index, where they now carry the earlier April 8th round
of questions for comment and the numbered open meeting item that set the September deadline,
both of which the record did not previously hold. `tx-2026-0024`'s two moved onto entries the
feed still carries, and they now record that the commission's calendar also lists the grid
operator's own board meetings at a separate address. The Texas Register acknowledgement filed
under control number 58482 still states the September 4th deadline, so nothing about the shut
window was lost.

`tx-2026-0024`'s summary said the feed carried two comment deadlines. It carries one. That was
corrected in the same commit.

### Three items confirmed where the diff could not confirm them

- `tx-2026-0120`, the border biometrics assessment, returned **403 to the record's fetcher on
  twelve claims** and read normally through a different path. The account is still published and
  still says image capture exceeded expectations in both day and night conditions.
- `tx-2026-0036` and `tx-2026-0046` sit behind publishers whose crawl rules now exclude
  automated readers. Both were confirmed against their OTHER source, the San Antonio station and
  the company's own filing with the federal securities regulator, and both carry a dated line
  naming what stays unconfirmed.

### The geography backlog is empty and stayed empty

`site_build.py` printed no `backlog:` lines at all, on a run that admitted two items. Both new
items name a county.

**All twelve deterministic movement notes were re-worded.** `reverify.py --check-notes` reads
531 checked notes and finds every figure traceable.

## Phases 4 and 5, discovery and admission

Five scouts, three of them on application beats, per the rule that at least half must be. The
PUCT calendar, the Texas Register, the Federal Register API and CourtListener were all polled.

**The record and the calendar agree.** The feed's live September 17th comment deadline for
Project 59550 is `tx-2026-0107`, its September 22nd workshop on Project 58555 is
`tx-2026-0109`, and its October 6th workshop is `tx-2026-0139`. Three independent
cross-checks that the record is current rather than merely recent.

**The policy scout's largest gap was closed from the main context.** It could not read the
September 4th Texas Register `In Addition` item titled "Public Utility Commission of Texas -
Memo Establishing Comment Deadline", and named it as the likeliest missed primary document. It
is **Project 60154**, a rulemaking petition by Jeff Pelletier to amend 16 TAC Section 25.211(n)
so utilities file distributed generation interconnection reports monthly rather than annually,
with comments due Friday, October 2nd, 2026. It is not admitted, because it is a grid visibility
petition with no AI nexus, and admitting it would be padding the record with something a reader
came here for the opposite of.

Two items admitted, two more promoted automatically because their sources cleared this run
(`tx-2026-0126` and `tx-2026-0130`), and both of those were re-verified and stamped before the
build.

- **`tx-2026-0140`**, the deck's subject. NHTSA Audit Query AQ26002. Twelve claims, every one
  primary, all from the agency's own opening resume.
- **`tx-2026-0141`**, UT San Antonio's off-grid flood node. Eight claims, all primary.

**The admission gate caught one of my own sentences.** `tx-2026-0141` was held on the first pass
for the British spelling "programme" in prose I wrote. That is the house-style gate doing its
job on the run rather than on the sources.

## Phase 7, the instruments and the discoverability signoff

`gridwatch_pagecheck`, `waterwatch_pagecheck` and `waterwatch_page --self-test` all exited 0.
Both pages are current and holding their promises. Nothing to fix and nothing stopped.

One observation that is NOT an alarm and is recorded because a later run should not rediscover
it as one. `ledger/gridwatch/weather.jsonl` runs to September 7th and `readings.jsonl` to
September 8th, while both files were written today. Those are publication lags in NCEI and in
the ERCOT dashboard feed rather than a stopped collector, and the two page checks that exist to
tell those apart both returned 0. **A run does not own these files and this one did not touch
them.**

**The scanner ceiling was NOT checked.** No Supabase connector is available in this session, so
`scanner.scans` could not be queried. This is recorded as not looked at rather than as fine.

### Discoverability signoff

- **One decision's card, opened as an image.** `docs/og/tx-2026-0139.png`, the newest item at
  the time of the check. Four lines, wrapping at real word boundaries, dark ground and the flag
  block at left. **It ends "would curtail a…", which truncates on an article.** The wrapper cuts
  on width and the last word it kept is a two letter function word, so the card trails off
  rather than stopping. Not a broken card and not a gate failure. Written up as an upgrade
  candidate below rather than fixed inline, because `scripts/site/og.py` is in this lane and the
  fix belongs with the phase whose job is editing the machine.
- **`/questions/`, read as a reader.** Eight question shapes. "Where a comment window is open"
  answers 03, and those three are `tx-2026-0107` closing September 17th, `tx-2026-0118` closing
  October 20th and `tx-2026-0075` closing November 3rd. Every one is genuinely open. Questions a
  Texan would type, and the counts are honest.
- **The `Open right now` section of `llms.txt`.** Ten entries, and the one that matters is the
  one that is NOT there. `tx-2026-0002`'s window shut on September 4th, its room is
  `contact_only`, and it is correctly absent. A window that closed six days ago and was still
  advertised would be the exact merge-order fault this bullet exists to catch.
- **`/sources/`.** **573 of 655 claims rest on a primary document, across 214 documents from 99
  publishers.** The top publisher is `interchange.puc.texas.gov` at 97 claims, which is the
  commission's own filing index and is a primary source, so the record leans hardest on exactly
  the kind of document it says it does. Both items admitted today are entirely primary, so this
  run moved the share up rather than down. Quoted material is still carrying its punctuation
  exemption and none of our own sentences are hiding inside it.
- **`/topic/`.** Eight beats. The card counts are 29, 3, 13, 14, 12, 21, 17 and 10, which sum to
  119, the number the front page's own counter printed at the time of the check. The three
  "still open to comment" figures sum to 03, which matches the front page and `/questions/`.
  Three surfaces computing the same figure from the same ledger and agreeing.
- **`/place/`.** 63 counties across 28 statistical areas. Travis, where `tx-2026-0140` landed,
  and Bexar, where `tx-2026-0141` landed, both already carry pages, and both appear on the hub.

The seven discoverability checks all exited 0.

## Phase 8, selection

**The story is `tx-2026-0140`, NHTSA Audit Query AQ26002.** On September 3rd, 2026 Tesla began
paid commercial deployment of the Cybercab in Austin. The vehicle has no brake pedal, no gas
pedal, no steering wheel and no mirrors. Tesla certified it ITSELF as compliant with every
applicable Federal Motor Vehicle Safety Standard and told the agency so. The agency opened an
audit the same day into the process and the technical data behind that certification, and said
it will consider how far the certification rested on Tesla determining that certain standards do
not apply at all.

**Why this and not the others.** Three candidates cleared their sources this run.

- The **statewide Flock unwind** was the loudest story of the week. Bastrop decommissioned and
  wrote a standing bar, Liberty Hill terminated 7 to 0, El Paso halted about 150 state funded
  cameras, and Dallas voted to keep paying for its own out of local money on the same day its
  police lost the state grant. `dedupe_check` returned **LIKELY REPEAT at 0.70** against carousel
  no. 12 and 0.48 against carousel no. 4, and `surveillance-and-policing` is five of the last
  nineteen decks and **two of the last three**. A third surveillance deck in four days is a feed
  rather than a record. The record still takes the story; the deck does not.
- The **UTSA flood node** returned "nothing close" and is the cleanest story here. It is
  admitted as `tx-2026-0141` and it is a good deck for a later run. It is a prototype with no
  named deployment site, which is a real ceiling on stakes.
- The **Cybercab audit** returned nothing at the repeat threshold, one faint 0.21.

**The overlap I read in full before clearing it, because a run eight days ago got this exact
call right from the other direction.** Carousel no. 5 lists NHTSA among its entities and
"robotaxi" among its keywords. On 2026-09-08 a run rejected a federal crash count story as a
repeat of no. 5, correctly, because no. 5's declared angle was "the gap between what the machines
measure continuously and what the state publishes a crash count for", and a crash count is the
ANSWER to that deck's own question.

This story is not. No. 5 was the STATE authorising commercial operation. This is a FEDERAL
agency auditing a manufacturer's own certification of a vehicle's construction. Different body,
different instrument, different question, and the agency says in its own words that the audit is
about the certification rather than about how the vehicle drives.

**So the angle is locked on certification and the deck may not drift into driving.** The
fact-checker was instructed to REJECT any claim about how the vehicle drives, its safety record
or crash data, and to say why. That instruction is what keeps this deck distinct from no. 5, and
it is a constraint on the art as much as on the copy.

`texan_check` at selection: places Austin and Travis County, body yes, next step yes.
