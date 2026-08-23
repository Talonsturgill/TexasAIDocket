# Run record, August 23rd, 2026

**Outcome. The record was updated in full and the run did NOT merge**, because the site build
cannot go green without a one token change to a file this actor may not write. The defect, the
fix and the evidence are below. Everything else in this run is committed to the branch and is
ready to merge the moment that change lands.

## THE BLOCKER, and it is a gate that has been green for the wrong reason

`python3 scripts/site/site_build.py` exits 1 with:

```
  numeral: construction/index.html: 44
site_build: 2 page(s) print a numeral this build did not compute.
```

**The page is right and the authorised set is wrong.** `/construction/` prints the campus name
`Project Gold Phase 2 - DFW44`, which is an identifier taken from a filing, not a measurement.
`numeral_lint` reads `44` out of it and asks who computed it.

The asymmetry is in `site_build.py`, in the block that assembles `_tnums` for that page. The
campus loop authorises three figures and never the name:

```python
for _c in tdlr_projects.campuses(_dc):
    _tnums |= {_bn(_c["cost"]), entities.n0(_c["sqft"]), entities.n0(_c["buildings"])}
```

Eight lines below it, the facility loop does exactly what the campus loop does not:

```python
for _f in _ent["facilities"]:
    _tnums.add(_f["name"])
```

**The proposed fix is one token**, adding the campus's own name the same way a facility's is
added. The campus record's key is `project` rather than `name`:

```python
for _c in tdlr_projects.campuses(_dc):
    _tnums |= {_bn(_c["cost"]), entities.n0(_c["sqft"]),
               entities.n0(_c["buildings"]), _c["project"]}
```

**Why it never fired before, and this is the part worth keeping.** The authorised set is
site wide. `by_room["open_meeting"]` was **44** on `main`, so `44` was authorised as a count of
open meeting rooms and the campus name's digits were covered by an unrelated coincidence. This
run admitted four items, one of which carries an `open_meeting` room, so that count moved to 45
and the cover came off. `Project Gold Phase 2 - DFW44` is the only campus name in
`ledger/facilities/projects.json` carrying digits, which is why one coincidence was enough to
hide it.

Measured rather than argued:

```
44 authorised on main?  True      by_room = {closed 2, contact_only 18, open_comment 5, open_meeting 44}
44 authorised now?      False     by_room = {closed 5, contact_only 18, open_comment 5, open_meeting 45}
```

**This belongs in `knowledge/shared/GATE_LESSONS.md`.** It is a green gate that was green because
of a number in a different subsystem, and the day the record grew it went red on a page this run
never touched. A maintainer adding the fix should add the case that proves it can still go red,
which is a campus name carrying digits that match no computed figure.

## Why this run did not just fix it

`scripts/site/site_build.py` resolves to the `human` actor in `ownership.yaml`. Both actors this
branch may stamp were tested against a staged edit and both were refused:

```
--actor daily   -> An automation may not write outside its lane.
--actor upgrade -> An automation may not write outside its lane.
```

That is the map working. The routine's instruction for exactly this case is to write the change
down as a proposal and stop, and `CLAUDE.md` is explicit that a self editing phase must not be
able to reach past its lane. The alternative routes were all worse and all were rejected on
purpose. Reverting today's admissions to move a count back to 44 would be gaming a gate with the
record. Choosing which items to admit so that some quoted figure contains `44` would be the same
thing wearing a better hat. Neither was done.

## THE RECORD

**Worklist cleared in full.** The selector named 6 items due and all 6 were re-verified against a
primary source fetched this run. Nothing rotten, and `DEFERRED` stayed empty. After the pass,
`docket_build --validate` reports every item verified within two days.

| item | what happened |
|---|---|
| tx-2026-0072 | **MOVED.** See below. |
| tx-2026-0057 | Checked and unchanged. The TCEQ cancelation notice for the Carson County meeting on Fermi Equipment Holdco's air permits still stands and still says the meeting will be rescheduled. No new date posted. |
| tx-2026-0077 | Checked and unchanged, through a route that is not the one the item cites. See the disallow below. |
| tx-2026-0075 | Checked and unchanged. Pflugerville ORD-0890 passed second reading August 11th with all members voting in favor, and the city's own legislative record carries no later action. |
| tx-2026-0048 | Checked and unchanged. League City Ordinance No. 2026-27 still shows approval on first and final reading on August 11th and nothing after it. |
| tx-2026-0073 | Checked and unchanged. Both House hearings still listed on the Legislative Reference Library's posting, and both dates have now passed. |

**tx-2026-0072 moved, and it is the largest movement on the record this run.** The utility
commission signed an order in Project No. 59142 on August 20th granting ERCOT the good cause
exceptions it asked for, so the August 7th classification deadline is formally excused and the
Batch Zero study of loads at 75 megawatts or more is paused until the audit is done. ERCOT filed
the audit's design the same day. Twelve claims were added, every one of them from a primary
document.

Two things in that filing are worth a reader's attention and both are now on the record. The
community impact half of the audit reaches **data centers and crypto facilities of 25 megawatts
or more that have not yet energized**, which is a lower floor than the 75 megawatt pause uses. And
the grid operator reports it **has reviewed 290 dynamic models with approximately 18 percent
acceptable on first review.**

**Admitted, 4 of 5 candidates that got as far as the gate.**

| id | item | place |
|---|---|---|
| tx-2026-0090 | NSF funds an open access robot run alloy laboratory at Texas A&M that outside researchers may book | Brazos |
| tx-2026-0092 | NSF funds UT San Antonio and Texas A&M to adapt large language models where the compute is not there | Bexar |
| tx-2026-0093 | NSF funds Rice to let AI propose algorithms only where a proof checker certifies them | Harris |
| tx-2026-0094 | A generative AI platform at UTMB reached the Regents only on its third amendment, at $9,850,000 | Galveston |

**Held, with reasons, and nothing is lost by holding.**

- **Amazon's Austin robotics plant.** Verified, quotes checked against both the Governor's release
  and the company's own. Held because `decider.type` has no value for a company and both
  announcements state no public body acted, the mayor being quoted saying the company asked for no
  economic incentives and no public money. Admitting it needs either a public decision to point at
  or a change to what this record counts as a decision, and that second one is the owner's call.
- **DIR's HB 3512 artificial intelligence training certification.** Its August 31st compliance
  deadline is stated only on a DIR page dated January 30th, and the page that would confirm it is
  current returned 429 to both clients on every attempt. A door a reader can't reliably date is not
  a door.
- **PUCT Project 59550**, surfaced by the calendar poll with a September 17th comment deadline.
  Read in full and it is a quinquennial review of system wide offer caps with no AI or large load
  question in it. Not an AI decision, so not admitted.
- **The CFTC's request for comment on listing compute derivatives**, closing October 20th. The
  notice's full text carries zero mentions of Texas, ERCOT, electricity or megawatts. Admitting it
  as statewide would publish a claim about scope nobody checked.

**Backlog held at 3 and did not grow.** The same three ERCOT items that predate the geography rule
and are exempt by name.

**The primary source share moved UP**, from 242 of 314 claims to 256 of 328 at the point it was
read, 77.07 percent to 78.05 percent. Every item admitted this run rests on a federal award record
or a board's own agenda book, which is what moved it.

## Discoverability signoff

- **One decision's card, opened as an image.** `docs/og/tx-2026-0082.png`. Wraps after "Epic",
  "into" and "and", which is where a reader would break it, and ends on the whole word "advanced"
  followed by an ellipsis rather than on a stump. Fine.
- **`/questions/`.** NOT LOOKED AT as a reader. The parse used to pull the questions out returned
  zero, and the blocker took the time that would have gone into opening it properly. Recorded as
  not looked at rather than as fine.
- **`Open right now` in `llms.txt`.** Cross checked against the windows re-verified this run. It
  lists tx-2026-0015 closing August 31st, tx-2026-0016 closing September 8th, tx-2026-0002 closing
  September 4th, tx-2026-0048 and tx-2026-0075 on November 3rd, and tx-2026-0077 on August 25th.
  Nothing closed today, so nothing is listed that should have dropped.
- **`/sources/`.** The share at the top reads 242 of 314 claims on a primary document across 124
  documents from 58 publishers, and a fresh build with this run's work reads 256 of 328. The top
  publisher is `webapi.legistar.com` at 29 claims, which is a municipal legislative record system
  rather than a newsroom, so the head of that list is a primary source and reads correctly.
- **`/topic/`.** NOT LOOKED AT card against page. The build that would have carried this run's new
  items into it is the build that is failing.
- **`/place/`.** NOT LOOKED AT for Galveston County, for the same reason.

The three surfaces marked NOT LOOKED AT are written down that way deliberately. A surface nobody
opened is recorded as not opened, never as fine.

## The instruments

Both green and neither blocked anything.

```
scripts/gridwatch/gridwatch_pagecheck.py   exit 0   gridwatch page: current, and holding its promises
scripts/gridwatch/waterwatch_pagecheck.py  exit 0   water watch page: current, and holding its promises
scripts/site/waterwatch_page.py --self-test exit 0
```

The scanner's daily ceiling was NOT checked. No Supabase connector is available in this session,
so the query in the routine could not be run. Recorded rather than skipped silently.

## THE DISALLOW, and it is the run's other real finding

**`capitol.texas.gov/robots.txt` now carries `Disallow: /TLODOCS/`.** The sources registry lists
only `/BillLookup/`, `/Reports/` and `/Search/` for that host. Every House and Senate hearing
notice, schedule, bill text and bill analysis lives under `/tlodocs/`.

This context read the file before fetching and did not fetch it. Three scouts checked
independently and reported the same directive without being asked to look for it. The directive is
upper case and the live urls are lower case, and taking that as permission would be routing around
a disallow on a technicality, so it was treated as off limits.

The record already cites four `/tlodocs/` urls on tx-2026-0073 and tx-2026-0077, admitted before
today. Citing a url is not fetching it, so nothing was withdrawn. **Neither item can be
re-verified through that path again**, and tx-2026-0077 was re-verified this run through
`capitol.texas.gov/Committees/MeetingsUpcoming.aspx`, which is not disallowed and gave a better
quote than the notice pdf did.

**A maintainer needs to fold this into `SOURCES_REGISTRY.md` on purpose.** It is written into
`SOURCES_FIELD_LOG.md` with the working substitutes.

## What else the sources did

Full detail is in `knowledge/shared/SOURCES_FIELD_LOG.md`. The one worth repeating here is a
quote fidelity finding. **A PUCT Interchange filing offers a PDF and a ZIP, and the ZIP holds the
original office file.** Item 52 of Project 59142 is a scan whose OCR layer renders `August 7,2026`,
`ofthe`, `MWtotal` and a signature block as `PUBLIC UTILITY COMMISSIO EXAS N OFy`. The ZIP carried
the source `.pptx`, whose xml holds the real text. Every figure in this run's tx-2026-0072 update
came from the pptx, because a verbatim quote taken from an OCR layer is a quote of the scanner.

## The deck

Selection, dedupe and the claims file are done and committed. `dedupe_check` reported nothing
close. The claims file passes `claims_check` with 10 verified claims and 3 rejected, and every one
of the 10 quotes was verified character for character against the source document's own text
layer, with one hyphenated line wrap rejoined.

**The deck was not built**, because a deck that can't publish costs the run the thing it is for and
the blocker above takes precedence. The three treatments the directors room produced are strong and
the story is unusually good, so the story is queued for the next run rather than spent.

Rejected during fact checking, and worth recording because a whole story died on it: several
outlets describe the UT Dell Medical Center approved at the same meeting as an **AI-native**
hospital. The Regents' own agenda book never uses the words artificial intelligence in that item.
It says "digital technology, robotics, and automation" and a "digitally enabled infrastructure".
The AI-native framing is the coverage's and not the document's, so it was not available.

## Retro

**Instincts, two added, both at 0.50, which is the honest score for a lesson nothing has tested.**

- `verify-the-adjective-not-just-the-figure`. The compute-not-generate law guards numerals and
  this run nearly lost a whole treatment to an ADJECTIVE. Check the word against the document.
- `read-the-exit-code-after-the-record-changes`. The numeral gate's authorised set is site wide,
  so admitting an item can turn a page red that this run never touched. Two builds had already
  been read by their tail rather than their exit code before the red was noticed, which is the
  fault `CLAUDE.md` names and which caught this run anyway.

No instincts were confirmed or contradicted, because the ledger held none. It has shipped no
lesson that has survived three runs, so the directors room was handed nothing, which is correct
rather than a gap.

**Upgrades, zero, and the reason is the run's own blocker.** The one upgrade this run identified
is the `_c["project"]` token in `site_build.py`, and that file is `human` owned. The routine's
rule for an upgrade that needs another actor's file is to write it down as a proposal and stop,
which is what happened. No upgrade engineer was spawned, because there is no second candidate
worth editing the machine for on a run that is not merging.

## Against the success criteria, honestly

| criterion | result |
|---|---|
| Worklist cleared in full | **Met.** All 6, each against a primary source fetched this run. |
| Nothing rotten remains | **Met.** The selector reported none and exited 0. |
| Every admitted item cites a primary source and names where it is | **Met.** 4 items, each on a federal award record or a board's own agenda book, each with a county. |
| Backlog no longer than at wake | **Met.** Held at 3, unchanged. |
| A deck shipped, merged, with a Gmail draft waiting | **NOT MET.** No deck, no merge, no draft. |
| Every fact traces to a verified claim | **Met.** All 10 deck claims verified character for character; every new record claim quoted from a fetched document. |
| Every machine gate green by exit code | **NOT MET.** `site_build.py` exits 1. Everything else green. |
| Ledgers updated so tomorrow cannot repeat today | **Partly.** Instincts written. Topics, artwork and captions untouched, because no deck shipped and writing them would claim a deck that does not exist. |
| `docs/` rebuilt and byte fresh | **NOT MET.** Blocked by the same gate. |
| Branch merged, or run marked failed with evidence committed | **Met, the second way.** |

This run is rung (d) of the degradation ladder, the record updated in full and no deck, and it
got there through an external blocker rather than through a choice. The record is the durable
half and it is saved.

## PROPOSAL 2. Rung (d) of the degradation ladder is unreachable as written

The ladder's rung (d) is "Record updated in full, no deck, **post-mortem in the email**." This run
landed exactly there and could not produce that email.

`gmail_draft.py` refuses to build a payload without post copy:

```
gmail_draft: runs/carousel/2026-08-23/caption.txt is empty or missing.
An email with no post copy is the defect this builder exists to prevent
```

**That refusal is correct and should not be loosened.** It exists because run No. 2 hand wrote a
long plaintext essay about how the day had gone with no post copy, no first comment, no PDF and no
images, and the whole point of the builder is that this cannot ship. Phase 18 also states plainly
that the email is not hand written.

So the two rules meet and leave no move. A deckless run is told to put a post-mortem in the email,
the builder refuses an email with no deck in it, and hand writing one is forbidden. This run
obeyed both rules and produced no email, which means **on rung (d) the owner gets no email at
all**, which is the opposite of what the ladder intends.

Three ways out, for a maintainer to choose between rather than for a run to pick:

1. Give `gmail_draft.py` an explicit post-mortem mode, entered by a flag rather than by the
   absence of a file, which builds the account of the day with the gates, the degraded list and
   the notes and prints no post copy, no first comment and no PDF because there are none. The
   builder stays the only thing that writes the email, and `email_check.py` learns the second
   shape.
2. Change rung (d) to say the post-mortem goes in the run record and the pull request, which is
   where this run actually put it.
3. Leave both as they are and accept that a deckless run reaches its owner through the pull
   request alone.

The first is the one that keeps the ladder's promise. This run's account of the day went out
through the run record, the pull request and a push notification instead, and the payload inputs
it would have used are committed beside this file as `gates.json`, `degraded.json`,
`upgrades.json` and `notes.txt` so the email can be built the moment a mode exists for it.

**No Gmail draft was created this run.** Nothing was hand written and nothing was sent.
