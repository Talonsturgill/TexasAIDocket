# The data center registry, and what it actually says

The roster on the grid page is the Texas Comptroller's certified list of data centers holding a
sales tax exemption. It is a **tax record**, not an inventory of buildings, and almost every
mistake available here comes from forgetting that.

Source of record: https://comptroller.texas.gov/taxes/data-centers/data-center-lists.php
Collected by `scripts/gridwatch/datacenters_collect.py` into `ledger/gridwatch/datacenters.json`.

## The three roles are legal positions, not job descriptions

The registry gives each facility an **owner**, an **occupant** and an **operator**. These are the
statutory roles in an exemption application under Tax Code 151.359. They are not a claim about who
runs the building, who owns the land, or whose logo is on the door.

**This is the trap, and it is `GATE_LESSONS` entry 44 ("A field's name is not a claim about
today") waiting to happen again.** Writing "Anthropic owns a data center in Abernathy" from an
occupant field is wrong in a way that reads perfectly. What the record supports is narrower and
more interesting: *Anthropic, PBC is the certified qualifying occupant of the Fluidstack Abernathy
Data Center, effective January 20th, 2026.*

Write the role, name the date, and let the reader draw the inference. A dossier that says
"occupant of record" is both correct and more informative than one that says "owns".

## What certification requires, which is why these are large

A **qualifying data center** under 151.359 needs at least 100,000 square feet in a single
building, at least $200 million of capital investment over five years, and at least 20 qualifying
jobs in the county. The exemption runs 10 to 15 years depending on the investment.

A **qualifying large data center project** under 151.3595 needs at least 250,000 square feet on a
single parcel or contiguous parcels, at least $500 million over five years, and at least 40
qualifying jobs. That exemption runs 20 years from certification.

Two things follow. Every facility on this list has already cleared a nine figure investment bar,
so none of them is small. And the `effective` date is the **certification date**, not the date
concrete was poured, not the date it energized, and not the date anyone announced it. Those are
four different dates and a dossier should carry whichever ones it can source, each labelled.

## What the registry proves, and what it can't

It proves a facility exists, that the state certified it, who filed in each role, and when the
exemption took effect. That is a genuinely hard, primary, government-issued fact and it is the
spine of every dossier.

It says nothing about megawatts, acreage, square footage, cooling, water, tenants, chips, or
whether the thing is running. Every one of those has to come from somewhere else, and where it
can't be sourced the dossier says so rather than estimating. Publishing the size of the gap is
the house position and it applies here exactly as it does on the grid page.

## The state record carries data-entry noise, and we publish it faithfully

The operator lists in particular are dirty. Real examples from the August 2026 read:
`Riot Corsicana Data Center I. LLC` with a stray period, `Riot Data Centers, LLC 3` with a
trailing numeral, `Whinstone, US, Inc.` with a comma inside the name.

Do not silently clean these. The registry is the record and a reader comparing our page against
the Comptroller's should find the same strings. Normalise for MATCHING if a lookup needs it, and
render what the state published.

## THE LIST IS EDITED IN PLACE, AND THAT GOVERNS EVERY SENTENCE ABOUT IT

Proven, not assumed. Between the readings of August 19th and August 21st of 2026 the Comptroller
added two rows and REWROTE two. `Hutto Data Center Campus LLC` had its owner replaced by three
entities including a power company, against an unchanged effective date of March 10th, 2025.

    A ROW'S PARTIES ARE CURRENT AS OF THE READING. The effective date says when the exemption
    was granted. It does NOT say who held it then.

`HELO1 DC` is the clearest case. Its effective date is June 2021. It names Galaxy, which bought
that site from Argo in late 2022, and CoreWeave, which leased it in 2025. Nothing is wrong with
the row. It is simply not a historical record, and reading it as one produces a confident
sentence about 2021 that is false.

**This corrected two pages that were already published.** Both said, in effect, that two rows
record a site changing hands from mining to AI. Two rows show two LIVE certifications under one
facility name with different dates and different occupants. The change of use at Cedarvale and at
Black Pearl is real and is established by the LEASES, which are separately sourced. It is not
established by the rows, and the rows no longer get the credit.

So the safe form is narrow. Say the state certifies this facility, say when, say who is named
now. Never say who was named then unless a snapshot proves it.

`scripts/site/registry_changes.py` diffs the collector's raw snapshots and publishes what moved.
It ignores a date that was merely reformatted, because burying an owner swap under punctuation
noise is how a watch stops being read. **The record starts on August 19th of 2026**, the first
snapshot, and the page says so rather than implying the list was stable before anyone looked.

## THERE IS A SECOND STATE REGISTER, AND IT IS ABOUT BUILDINGS

The Comptroller's list records a TAX STATUS. It carries no address, no size, no cost and no
schedule, because none of those is what an exemption is about.

The Texas Department of Licensing and Regulation registers CONSTRUCTION. Every large commercial
project is filed with it under the architectural barriers program, and the filing is public. Each
one carries a project name, a street address, a county, a type of work, a scope in the filer's own
words, a square footage, an estimated cost and a schedule.

    THE TWO REGISTERS DISAGREE AND NEITHER IS WRONG. They record different acts. Microsoft's
    certified rows in San Antonio name SAT designations 09 to 17, 80 to 85 and 89 to 90. Its
    construction filings name SAT40, SAT46, SAT93 and SAT94 as well, and put the newest and
    largest of them in MEDINA COUNTY, which carries no Microsoft row in the Comptroller's list at
    all. Only reading both shows the shape of a buildout.

The filings also confirm a registry oddity from the outside. The oldest row in the certified list
is a Microsoft building whose occupant is Chevron, which reads like an error until a 2019
construction filing turns up named "Microsoft Chevron/SN7 Colo 1".

**At statewide scale it is $37.55 billion.** 201 data center filings by the operators this
project tracks, 38.9 million square feet, 20 counties, from 2008 to 2029. Almost none of it is
old. The filings sit near zero for fifteen years and then go vertical in 2024, and the single
largest county is **Shackelford**, population under four thousand, at $10.6 billion of Vantage
buildings.

**The two registers join, and the state published the join on both sides.** Vantage's Shackelford
filings are owned by `Vantage Data Centers TX304, LLC`, and that exact entity is an owner of
record on a Comptroller row. Galaxy Helios II and DB Data Center Red Oak behave the same way.
Seventeen certified facilities can be priced this way.

**The join is only valid on a SINGLE PURPOSE ENTITY.** A parent company name is not a building.
The first version matched on `Microsoft Corporation` and attached all twenty two Microsoft filings,
and $3.6 billion, to one facility called NADC. A party joins only when it names at most two
certified facilities, which is a stated judgement rather than a buried one.

**Several operators file nothing at all.** CoreWeave, EdgeConneX, Nscale, Anthropic, Whinstone and
Poolside return zero rows from the owner search. That is not an absence of building. It is the
difference between a company that builds and one that leases what somebody else built, and it is
why the construction register alone would badly understate who is in Texas.

**Four things about this source that will produce a wrong number if they are forgotten.**

- **The search endpoint ignores its city parameter.** A search for Microsoft in San Antonio
  returns the Irving buildings too. Scope on the RECORDS, never on the request.
- **A designation can be filed more than once.** SAT82 has two filings at two addresses. SAT93 and
  SAT94 each have a large filing and a small later one. Summing every row as a separate building
  overstates the buildout, so money is grouped by the designation AS FILED.
- **A filing that names a range names several buildings and has ONE cost.** Spreading SAT11-14's
  sixty two million across four rows reports it four times.
- **A substring needs a boundary on BOTH ends.** `\bvantage` keeps EVANTAGE HOLDINGS out, which
  is 27 filings that are not Vantage. `stream\b` keeps Streamline out. A brand token without both
  guards quietly annexes another company's buildings.
- **The filings name operators the certified list does not.** Digital Realty and Crusoe build in
  Texas and hold no certification at all, so a reader working from the tax record alone would not
  know they are here. The published page states that, computed from the two records rather than
  asserted.
- **The ledger is the artifact and `out/` is scratch.** `tdlr_fetch --build` MERGES on the project
  number rather than rebuilding from disk. A rebuild-from-disk on a fresh container would have cut
  626 filings to the 25 sitting there, and every gate would have stayed green over it. See
  GATE_LESSONS entry 61 ("The build that would have deleted thirty billion dollars because its
  scratch was gone").
- **The owner search is a SUBSTRING match and cannot be trusted.** A query for Meta returns Metal
  Building Supplies. Core Scientific returns Core & Main, CORE Construction and a nail bar.
  Prologis returns that landlord's whole Texas portfolio. Membership is decided on the owner field
  the filing itself carries, never on the search that found it.
- **An operator's filings are not all data centers.** Amazon builds fulfilment centres and
  Microsoft refreshes cafes. Classification is on what the filer wrote, exclusions first, because
  a warehouse and a data hall share the airport code naming convention and `Fulfillment Center
  DFW7` matched the include list on its first version. The rule is published on the page so a
  reader can disagree with it. The same companies filed $3.7 billion of other Texas work, counted
  separately and added to nothing.
- **A campus could be filed by two owners and counted twice.** Two filings at one address for one
  cost under different owners is that shape. `shared_buildings()` checks every build and has found
  none. Lancium and Crusoe both filed a $292 million Abilene building and they are two buildings on
  two streets that happen to cost the same.
- **The county field is filer entered.** Five filings share postcode 78245 on the Lambda Drive
  campus and one of them says Medina where the other four say Bexar. The published page reports
  that disagreement and does not resolve it. It also does NOT decide the question from the
  postcode: ZIPs cross county lines, and an earlier version of that check invented a postcode to
  county table and flagged four correct filings as errors against it.

**It names people and this project does not.** Every filing carries the contact who submitted it
and the registered accessibility specialist who inspects it, with direct phone numbers. The parser
drops all of it at the point of parsing, and the gate checks again on what landed.

`robots.txt` at tdlr.texas.gov disallows `/ithelp/` and `*.csv` and nothing else, so the search
endpoint and the print view are both permitted. `scripts/site/tdlr_fetch.py` pulls and parses,
writing the raw response to disk before reading it so a reparse costs no second visit.
`scripts/site/tdlr_projects.py` computes every figure the page shows. Neither runs on a cron and
neither is a routine phase. This is research, run by hand.

## THE RAW TABLE CARRIES A REGISTRATION NUMBER AND THE LEDGER DROPS IT

Every party on every row has one, in the form `LD370879-OW1`, `-OC1`, `-OP1` for the owner, the
occupant and the operator of one facility. `ledger/gridwatch/datacenters.json` holds none of them,
because the collector discards the column.

They are worth having, for two reasons that nothing else in the record supplies. The suffix states
the ROLE explicitly, where the ledger infers it from which array a name sits in. The stem is a
stable key for a facility ACROSS a re-certification, which is the one thing this record cannot
currently follow, since the state edits rows in place and keeps the original effective date.

`scripts/gridwatch/**` belongs to the `gridwatch` actor. A session in another lane writes this
down and does not make the change. Whoever takes it should know that adding a field does not
backfill the history, and that `ledger/gridwatch/raw/` is what a backfill would have to read.

## A CELL CAN HOLD A LIST, AND STRIPPING THE TAGS GLUES IT

Several parties in one role are marked up as `<ul><li>`, and the state does not always leave
whitespace between the items. Removing tags alone turned three owners into
`Hutto Data Center 1 LLC Hutto Data Center 2 LLC Hutto Data Center Campus Power LLC` and two
registration numbers into `LD370879-OP2LD370879-OP3`, which is neither of them.

It is not only unreadable. Two different lists can glue to the same string and one list can glue
to two different strings, so any comparison of two readings is being made on a lossy rendering of
the cell. `registry_changes.cells()` splits on the list item and the line break before it strips
anything, and its self-test carries the exact markup that produced the fault.

## A REPEATED NAME IS A RE-CERTIFICATION, AND IT IS THE BEST THING IN THIS FILE

Four names appear twice in the August 2026 read. They are not duplicates to be cleaned. A second
row is a SECOND CERTIFICATION for the same facility, and comparing the two rows shows the
occupant CHANGING.

    Cipher Black Pearl LLC Data Center
      2024-02-15   occupant Cipher Black Pearl LLC        (certified for its own use)
      2026-01-23   occupant Amazon Data Services, Inc.    (re-certified with a hyperscaler in it)

    Cedarvale, Barslow/Pyote TX Data Center
      2024-01-30   occupant Ionic Digital Mining LLC
      2026-03-16   occupant Nscale Ward County Borrower SPV, LLC

Both of those are a bitcoin mine becoming an AI facility, recorded in the state's tax file rather
than in a press release. Two others, Giga Texas Datacenter and Hockley Data Center, repeat with
the same occupant weeks apart, which reads as separate buildings or phases certified under one
name.

**So the registry is a time series of tenancy and not a flat list**, and nobody reads it that way.
A dossier for a facility with more than one row should carry both rows and say what moved between
them. Deduplicating by name throws away the only longitudinal signal this source has.

## A CERTIFICATION IS NOT A BUILDING, AND POOLSIDE IS THE PROOF

The single most important caveat on this whole surface, learned the hard way in batch three.

Poolside held two certifications on a Pecos County site for Project Horizon, a two gigawatt
campus. CoreWeave signed as anchor tenant for the first 250 MW and then TERMINATED that lease in
the spring of 2026 after Poolside's funding round failed to close. Trade coverage called it the
most prominent failure in the Texas pipeline.

**The state certified phase two on March 6th, 2026, days before that termination was reported,
and nothing in the registry has changed since.**

So the list records exemptions the Comptroller granted. It does not record buildings that exist,
buildings that are energized, or projects that are still alive. A dossier may say the state
certified a facility on a date. It may NEVER say a facility is operating, and no page here does.

## READ DOWN THE COLUMNS, NOT JUST ACROSS THE ROWS

Batch three's whole yield came from this. Reading one facility at a time hides everything that
matters about who is building Texas.

- **Oracle America Cloud Services is the occupant of record on twenty five facilities**, the
  largest single relationship in the state. It was invisible because the state filed it under two
  spellings that differ by a comma. Ten of those are Vantage buildings certified on one day and
  eight are the Abilene campus.
- **Sixteen companies are split across multiple spellings.** Google appears three ways, Whinstone
  three ways. Counting strings instead of companies gets the ranking wrong.
- **Entity names give away the business model.** Nexus files a POWER company beside every building
  company at Hubbard, which is exactly the behind the meter gas design its coverage describes.
  Fermi files a turbine warehouse and a mobile generation entity. Neither of those is something a
  colocation landlord files.
- **An SPV family reveals scale.** Ten numbered Vantage entities, eight Abilene DC entities,
  sixteen Nexus entities, twelve Compass entities. A campus is usually one entity per building
  because that is how each building gets financed separately.

`scripts/site/entities.py` does the resolution and publishes it at `/company/`. The mechanical
layer needs no judgment. The parent grouping does, so it lives in `config/entity_groups.json`
where every grouping states its reason.

## NAME THE ROW, NOT THE REGISTRY

A correction worth keeping, because it was published live before it was caught.

A Cedarvale dossier said Microsoft "does not appear in the registry at all". Microsoft appears on
**fourteen facilities**. What was true is that Microsoft is not named on THAT row, where the
certified occupant is an Nscale borrowing entity.

The corrected sentence is both accurate and better: Microsoft holds fourteen certifications of its
own, so its absence from one row is not avoidance, it is the difference between being the
occupant and being the occupant's customer. **Before writing that a company is absent, count.**

## The research ladder, in the order that pays

Worked out against the first batch. Higher rungs are primary and load bearing, lower rungs fill in
colour and are more often wrong.

1. **SEC filings.** 8-K exhibits and 10-Qs for any public parent. Cipher Mining, Riot Platforms,
   TeraWulf and Applied Digital all file, and their releases carry MW, contract value, term,
   counterparty and delivery date in language their lawyers checked. This is the best rung.
2. **The company's own investor newsroom**, which usually carries the same numbers with more
   physical detail such as acreage and phase counts.
3. **County appraisal district and local economic development announcements.** These carry
   address, parcel, square footage, abatement terms and job commitments. The Development
   Corporation of Abilene release is the model.
4. **TCEQ air permits** for backup generation, which is how you learn the generator count and size
   when nobody advertises it.
5. **ERCOT large load interconnection material** for the electrical side.
6. **Trade press** such as Data Center Dynamics and Data Center Knowledge, useful for narrative
   and for finding the primary document, rarely quotable on its own for a number.
7. **Aggregators** such as datacentermap and baxtel. Treat as a lead, never as a source. Their
   figures are frequently stale or interpolated and several disagreed with the filings this week.

## A caution the first batch earned

A company press release describing a corporate transaction may frame a facility differently from
how the state certified it. TeraWulf's July 2026 release places an Anthropic lease at a different
campus and describes Abernathy as sold to Fluidstack, while the Comptroller's record names
Anthropic as Abernathy's occupant. Both are true statements about different things.

When sources disagree, the dossier carries both with their dates and does not adjudicate. The
disagreement is itself the most valuable thing on the page, and resolving it silently would throw
away the only part a reader could not have got elsewhere.
