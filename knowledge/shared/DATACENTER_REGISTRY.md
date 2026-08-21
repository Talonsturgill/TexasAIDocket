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
