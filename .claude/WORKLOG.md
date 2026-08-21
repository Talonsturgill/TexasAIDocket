# WORKLOG — the ask box learns to retrieve

Opened 2026-08-21 on the owner's call, while a second workstream (the registry dossiers) is
still live further down this file. Both are real. Read the one whose files you are touching.

Owner's brief, verbatim in spirit: make the search agent the best in the world, **as long as it
is free**, stay on Sonnet, go slow, think big. Free is a hard constraint and it is the reason
several obvious moves below are refused rather than deferred.

**Read this first, then resume from the wave table at the bottom of this section.**

## What is actually there, measured before designing anything

    the pack            189,365 chars   ~47,341 tokens   86% of the 220,000 hard ceiling
    preamble             2,335 chars    counts, open windows, the daily instruments
    69 decisions       187,030 chars    ~2,710 chars each, delimited by [[tx-2026-NNNN]]
    corpus                 69 slugs, 266 authorised numerals
    catalogue             ~500 questions, each paired with a route
    cost                 ~$0.14 a question uncached, input to output about 7 to 1
    cap                   200 model calls a month

Two lanes, and only one of them is an LLM.

**The typing lane** runs in the browser with no network. IDF weighted token overlap against the
catalogue's QUESTIONS, plus a direct mention override for county, metro, decider and topic.
Floor 0.9. No length normalisation, no item level index, no rerank.

**The written lane** is one Sonnet 5 call in a Cloudflare worker with the WHOLE pack in the
system block, sentence by sentence verification against the corpus, streaming. No tools, no
loop, no retrieval.

## The forcing function is the ceiling, not the bill

At 200 calls a month the written lane costs under $30. Cost is not the problem. The problem is
that the pack is at 86% of a ceiling whose crossing is a HARD BUILD FAILURE, and the registry
dossier work further down this file is adding items faster than anything is removing them.

"No retrieval" was a good decision and it has a shelf life measured in weeks.

## The decision: retrieve in the worker, keep the index whole

One model call, not an agent loop. An agentic tool loop was considered and refused: three or
four sequential round trips is SLOWER than one call on a record this size, it multiplies the
call count against a cap that counts calls, and it buys nothing that assembling the context
deterministically does not.

Three system blocks, in this order:

    1  the instructions          cached, stable
    2  preamble + a compact index of EVERY decision   cached, stable for a day
    3  the full text of the decisions this question needs   not cached, small

Block 2 is the safety property and the whole reason this is not a normal RAG bolt-on. The model
always knows what EXISTS, even for items whose body it was not given, so the failure mode of
retrieval — confidently answering as if the missing thing is not there — is designed out rather
than mitigated. It can say "there is an item about that" and, better, retrieval can be generous
because the index is cheap.

Estimated ~9.4k tokens against 47.3k, and it stays flat as the record grows: only the index
line grows, never the retrieved slice.

## What is refused, and why

- **Embeddings and a vector store.** Not free, and a second service to keep alive.
- **A reranker model call.** Not free, and it doubles latency on the one part of the page a
  reader is waiting on.
- **An agent tool loop.** Slower here, and it spends the call cap three times faster.
- **Opus.** Owner's call, explicitly.
- **Raising the pack ceiling.** That is a bill on every question, and the owner said free.

Everything below is deterministic code that runs in a worker or a browser and costs nothing.

## Wave table

| # | Wave | State | What it must prove |
|---|------|-------|--------------------|
| 0 | effort low + usage counters | **DONE** 787b45c7 | 91 assertions, effort fallback proved red |
| 1 | eval harness, free, no model calls | **DONE** | 232 cases, 85.8% found / 83.2% first |
| 2 | body search + two real router bugs | **DONE** | 99.1% found, nonsense 75% -> 100% |
| 3 | the worker retrieves | TODO | token drop measured, ceiling pressure gone |
| 4 | verify, rebuild, ship | TODO | guards_local green, docs fresh, merged |

## What wave 1 measured, and the two bugs it found

The gold set is 232 cases generated from the record: an item's title trimmed the way a person
types, three rare words from its body, its county, its decider, its topic, plus negatives that
share no vocabulary with the record at all.

    baseline        found 85.8   first 83.2
    after wave 2    found 99.1   first 95.7

The headline was `phrase`, questions built from a detail in a decision's BODY, at **53.6%**.
The bodies were shipped in the browser's index the whole time and never searched: the scorer
only ever matched a query against the catalogue's QUESTIONS, which are generated from titles,
counties, deciders and topics. Adding BM25 over the bodies cost no payload at all and took it
to **97.1%**.

Two real bugs, both pre-existing, both found by having a number rather than an opinion.

**The unseen word scored highest.** The catalogue scorer credited a stem match with the rarity
of the word the READER typed. A word absent from the catalogue has the maximum rarity there is,
so "train" stem matching "trained" scored as the most distinctive word in the record, and "best
way to train for a marathon" reached a grant about robot safety with total confidence. The
evidence for a catalogue entry is the catalogue's own word, so that is the one whose rarity now
counts.

**Rarity is not evidence.** The first fix required a second corroborating word, with an escape
hatch for a single word rare enough to identify a decision alone, on the reasoning that a docket
number does exactly that. It does, and so does "way", which appears in exactly one of 69
decisions by accident. The hatch is gone rather than patched.

**And the rule had to be scoped, not blanket.** Requiring two words everywhere broke "What can I
still comment on?", which carries exactly one word the scorer keeps and where that word is
decisive. The size of the claim sets the evidence: naming ONE decision out of sixty nine needs
two words behind it, answering with a view over the whole record does not.

`tests/ask_eval.mjs` runs in CI and fails on one thing only, a query sharing nothing with the
record getting an answer. Everything else prints against `tests/fixtures/ask_eval_baseline.json`
and leaves the judgement to a person, because a measurement that fails a build is a measurement
people learn to route around.

Rules for this workstream. The retriever is ONE implementation generated into both lanes, never
two that agree today. Every wave lands with its own red case. Nothing here may add a recurring
cost. The sentence guard is never weakened to make retrieval look better.

---

# WORKLOG — the registry becomes a dossier

Opened 2026-08-21 on the owner's call. The grid page lists 151 certified data centers with five
fields each. Wanted: click a facility, get "every single piece of information that exists about
that data center", researched one by one. Explicitly NOT a blanket pass: "this is really gonna be
where we earn our keep as a data company". Ten or so per session, bespoke each time.

**Read this first.** Resume from the task table at the bottom. Read
`knowledge/shared/DATACENTER_REGISTRY.md` before researching anything.

## What the data is, measured before designing

    151 facilities, 5 fields each: name, effective, owners, occupants, operators
    owners present on 147 of 151, the other three fields on all 151
    85 of 151 name a major operator (Amazon, Google, Oracle, Anthropic, Lambda, Riot, Cipher...)

The registry is a TAX record from the Comptroller, under Tax Code 151.359 and 151.3595. Owner,
occupant and operator are statutory roles in an exemption filing, not job descriptions. The whole
doctrine is in `knowledge/shared/DATACENTER_REGISTRY.md` and it is not optional reading.

## Three findings from batch 1 that a blanket pass would never have produced

- **Anthropic, PBC is the certified occupant of TWO facilities**, Fluidstack Abernathy
  (owner FS AB LLC) and Cipher Barber Lake (operator Fluidstack USA II INC.).
- **LBB01 is named for Lubbock and owned by ALIGNED DATA CENTERS (ABERNATHY) PROPCO, LLC.** So
  Abernathy holds two unrelated data centers, an Aligned building with Lambda as occupant and the
  Fluidstack building with Anthropic as occupant. Nothing in the registry says they are different
  and nothing says they are the same.
- **TeraWulf's July 2026 release contradicts the state record**, placing the Anthropic lease at a
  different campus and describing Abernathy as sold to Fluidstack. Both are true about different
  things. The dossier carries both and adjudicates neither.

## The design

**A DOSSIER IS DATA, NOT PROSE.** This is what makes it legal to publish under the
compute-not-generate law. Every number lives in a `facts[]` entry as a real value with a unit and
a source id, and the page renders it through the same formatting call that authorises it for
`numeral_lint`. Prose lives in `notes[]` and **may not contain a numeral at all**, which the gate
enforces. A note says Google backstops the lease obligations. The 1.4 billion is a fact field.

**Every fact carries a source id** resolving to a `sources[]` entry with url, publisher, retrieved
date and kind. No source, no publish. Same rule the docket already runs on.

**Gaps are published.** `gaps[]` names what is not public for this facility. A dossier with four
facts and six gaps is honest and useful. One with four facts and silence is neither.

**A page AND a modal, not a modal alone.** The owner asked for a popup and a popup is right for
reading in place. But a modal is invisible to search, and 151 indexable pages each about a named
Texas data center is the single largest discoverability asset this project could hold. So each
facility gets a real page at `/facility/<slug>/` in the sitemap and `llms.txt`, and the registry
row opens the same content in a dialog with a link through. Progressive enhancement, same as the
calendar: with script off the row is a plain link to the page.

## The rules this has to hold

- Numerals computed, never typed. `numeral_lint` is a hard build gate.
- Every fact traces to a fetched source, with the retrieved date.
- `docs/` is generated. `site_fresh_check` proves byte equality.
- The dossier ledger is owned by `human` in `ownership.yaml`. **No routine may rewrite researched
  facts**, and the daily run must not be able to touch this file.
- Registry strings are published faithfully, data-entry noise included.
- House voice: no em dash, no colon or semicolon in published copy, straight quotes, "can't",
  dates as "August 21st".
- CSP hashes inline scripts, so the dialog script goes through `csp.apply`.
- Responsive, contrast gated, nothing overflows sideways.

## Tasks

| # | task | state |
| --- | --- | --- |
| A | Measure the registry, find its source, read the collector | DONE |
| B | `knowledge/shared/DATACENTER_REGISTRY.md`, the program's real semantics | DONE |
| C | This worklog | DONE |
| D | Research batch 1, ten marquee AI facilities | DONE, shipped in #148 |
| D2 | Research batch 2, ten more | DONE, shipped in #149 |
| D3 | Batch 3: the entity layer, plus nine more dossiers | DONE, 29 dossiers and 197 facts |
| D4 | Batch 4: the network field, the change log, three gate defects | DONE, 30 dossiers and 213 facts |
| D5 | Batch 5: nine more, and two tenants the announcements withheld | DONE, 39 dossiers and 271 facts |
| D6 | Batch 6: the construction register, and two faults in shipped pages | DONE, 32 filings and /construction/ |
| D7 | Batch 7: the register at scale, and the join between the two | DONE, 626 filings, $36.97bn, 17 joined |
| E | Dossier schema + `ledger/facilities/dossiers.json` | DONE |
| F | `facility_dossier.py` gate, 24 self-tests | DONE |
| G | Per-facility page at `/facility/<slug>/`, in the sitemap | DONE |
| H | The dialog on the registry row, progressive enhancement | DONE |
| I | `tests/facility_dossier.mjs`, 17 checks | DONE |
| J | Full sweep, ship | DONE through batch 4 |

## Wrap

W1. Delete this file when every task is DONE and all 151 have dossiers, or when the owner calls
    the project finished. Batches after the first resume at task D with a new ten.

## Batch 1, the ten

Fluidstack Abernathy (Anthropic) · Cipher Barber Lake (Anthropic) · Lancium Abilene Clean Campus II
(Oracle, Stargate) · LBB01 (Lambda, Aligned) · Meitner (Google) · Stingray (Amazon, Cipher) ·
Cipher Black Pearl (Amazon) · Riot Rockdale 1 · Riot Corsicana I · ECX AUS31-36 (EdgeConnex)

Chosen by signal rather than alphabetically. These are the rows a reader actually clicks, and they
are the ones with enough public record to prove the format works before it meets a small colo site
with almost nothing findable.

## Batch 2, shipped

The next ten. Pick by signal again rather than alphabetically, and read
`knowledge/shared/DATACENTER_REGISTRY.md` first, particularly the re-certification section,
which was the best finding of batch 1 and was not in the plan.

Candidates, all named in the registry with a major occupant and none researched yet:
Flamingo, Pecos Ranch, Bexar 1, Spectrum, Gulf Horizon and C1 Bosque I and II (all Amazon or
Google), DFW-04 (Lambda), TX11-12 (Oracle), Riot Rockdale 2 and Corsicana 02, and
Cedarvale/Pyote, which holds a re-certification showing Ionic Digital handing off to Nscale and
so is worth doing early while that pattern is fresh.

ECX AUS31-36 shipped deliberately thin and is the standing example of an honest sparse dossier.
It is also the first candidate for a second pass if better sourcing turns up.

## What batch 2 found

- **Cedarvale is the re-certification working as advertised.** Ionic Digital Mining in 2024,
  Nscale Ward County Borrower SPV in 2026, and behind the second row a lease of the whole site
  with Nvidia hardware going in for Microsoft. **Microsoft appears nowhere in the registry.** The
  certified occupant is a single purpose borrowing entity, which is the clearest example yet of
  why occupant is a legal position and not a tenant.
- **Two Bosque parcels, two different hyperscalers.** Google is the occupant of one and Amazon of
  the other, certified six days apart. Trade coverage of the CyrusOne campus in that county says
  the tenant is undisclosed. Whether these are the same campus is NOT established and is written
  as a gap rather than an inference.
- **Design, LLC operates two separate Google facilities**, here and at Meitner. A cross-row
  pattern invisible to anyone reading one facility at a time.
- **Amazon files under codenames.** Flamingo, Pecos Ranch, Bexar 1, Spectrum and Gulf Horizon
  appear in no public reporting. A state licensing filing for a San Antonio building uses the name
  Lavender Hill, so this is a documented practice rather than a guess. For those five the
  Comptroller's list is the only public evidence the facilities exist, and their dossiers say so
  rather than padding.

## Batch 3 candidates

Riot Rockdale 2 and Corsicana 02 (siblings of batch 1, cheap), plus the unresearched majors still
in the roster. The five Amazon codenames are the best second-pass target: a county appraisal
district search on Bexar, Pecos and the coastal counties would likely resolve addresses that no
press release carries.

Two units were added to the formatter across these batches, `units` for hardware counts. Any new
unit needs a formatter or the gate refuses the fact, which is the intended behaviour.

## Batch 3: reading down the columns

The yield this time came from a structural change rather than more research. The registry was
being read one row at a time and everything that matters is between the rows.

**`scripts/site/entities.py`** resolves the companies and `/company/` publishes them.

- **Oracle America Cloud Services is the occupant of record on twenty five facilities**, the
  largest relationship in Texas, and it was hidden because the state filed it under two spellings
  separated by a comma. Ten are Vantage buildings certified in one day. Eight are the Abilene
  campus.
- **Sixteen companies are split by punctuation alone.** Google three ways, Whinstone three ways.
- **Resolution is mechanical, grouping is curated.** Case, punctuation and corporate suffix are
  stripped for matching and nothing else is. Parent groups live in `config/entity_groups.json`
  where each states its reason, because saying two different legal entities are one company is a
  judgment and belongs somewhere a reader can argue with it.

Nine dossiers added: Poolside Pecos I, Fermi Data Center 1, Nexus Data Centers, DFW 9 through 12,
Lancium Abilene Clean Campus, TX 301.

## Two corrections this batch forced, both worth keeping

**A published claim was false.** The Cedarvale page said Microsoft "does not appear in the
registry at all". Microsoft is on fourteen facilities. Corrected to name the ROW rather than the
registry, which is both true and a better point. Count before writing that a company is absent.

**A certification is not a building.** Poolside's Project Horizon lost its anchor tenant when
CoreWeave terminated, and the state certified phase two days before that was reported. Nothing in
the registry changed. No page here says a facility is operating and none ever should.

## Batch 4 candidates

The five Amazon codenames still want a county appraisal district pass. Beyond that: CoreWeave's
eight, Microsoft's fourteen San Antonio and Red Oak sites, Galaxy Helios, Rowan's four codenamed
sites, the IE US family, Compass DFW III, and Hutto, which shows the same power-entity-per-building
pattern Nexus does and is worth checking for the same reason.

## Batch 4: the graph, and three defects it turned up

One dossier this batch, HELO1 DC (Galaxy's Helios campus, leased to CoreWeave). The work went
into the surface that the batch 3 entity layer made possible and into what building it exposed.

**`scripts/site/registry_graph.py`** draws the registry as a network on `/company/`. Nodes are
companies on more than one facility, edges are facilities two of them share, node AREA carries
reach and edge width carries how many they share. Forty nodes, forty four edges. The layout is
computed at build time with no clock and no random seed, because `site_fresh_check` rebuilds and
compares bytes, and a graph that settles somewhere new each build would fail that gate forever.
The browser animates FROM those positions, so motion is a read time behaviour that never touches
the bytes on disk.

**`scripts/site/registry_changes.py`** diffs consecutive raw registry snapshots and publishes what
the state changed. It is a pure function of `ledger/gridwatch/raw/*-datacenters.html.gz` computed
at build time, so it needs no new ledger and crosses no ownership lane.

### Three defects, and what each one taught

**A gate that reported a correct page as a violation.** `house_style_check` read "Galaxy Helios I"
as a first person pronoun. It is how the state spells that owner, and on that row the letter is
the point, because a second Helios certification spells the same occupant with a digit. The
`data-proper-name` mechanism already existed for page titles and had never been applied to the
body. It is now, and a fact declares `proper_name` in the ledger, and `facility_dossier` bounds
what may be declared: text only, never a computed value, no terminal punctuation, no clause
punctuation, eight words. A text fact IS allowed to be a sentence and several are, so without
that bound the flag would be a way to lift a whole sentence out of the house rules.

**Three CSS custom properties that nothing defined.** `--signal-link`, `--signal-shut` and
`--dusk-gold`, written from memory instead of from the file that defines them. CSS discards a
declaration it cannot resolve and logs nothing, so the graph drew forty four filaments with no
stroke at all and every gate was green. `scripts/site/css_tokens.py` now checks that every
`var()` resolves, and on its first run it also found `--ink-dim` and `--ink-quiet`, live on the
published site and older than this batch. GATE_LESSONS entry 59 ("CSS fails silently, and a green
suite has never once looked at a colour").

**A control character in published copy, and a wrong diagnosis of it.** The registry changes page
drew a box with "92" beside it where an arrow was meant. It was first read as a missing glyph and
written up that way. The served mono face carries U+2192: the real cause is that the stylesheet is
built from a Python string, where `content:"\2192"` is not a CSS escape but Python's octal
escape, giving chr(17) followed by the text "92". Reading the cmap of the actual woff2 is what
caught the wrong explanation before it shipped. `tests/glyphs.mjs` now refuses a control character
in published copy and checks glyph coverage for the faces this project ships, measured in a
browser because the served fonts are brotli compressed and this repo has no dependencies.

**A layout that passed eleven of eleven and drew a rectangle of dots.** Textbook Fruchterman
Reingold with no gravity, clamped to the field: thirty five of forty nodes ended up stacked
against the wall, and every assertion the self-test could make was true of that picture. Rewritten
with gravity, an unbounded relaxation fitted to the frame afterwards, a spacing pass in final
coordinates, and a deliberate outer ring for the nine companies that share nothing with anyone.
Found by rendering the page and looking at it. GATE_LESSONS entry 60 ("Thirty five of forty nodes were stacked against the wall and every
gate said yes").

The same page then had a second fault no gate has an opinion about: the cursor well pushed hardest
exactly where the pointer was, so every node stepped aside as a reader reached for it and not one
of the forty links could be clicked. The push now ramps to nothing inside the hit radius.

## Proposal, out of lane: the registry drops its registration IDs

The raw Comptroller HTML carries a registration number on every row, in the form `LD370879-OW1`,
`-OC1`, `-OP1` for the owner, occupant and operator of one facility. `ledger/gridwatch/
datacenters.json` holds none of them: the collector discards the column.

They are worth having. The suffix states the ROLE explicitly, where the ledger infers it from
which array a name sits in. The stem is a stable key for a facility across a re-certification,
which is the one thing the current record cannot follow, since the state edits rows in place and
keeps the original effective date.

`scripts/gridwatch/**` belongs to the `gridwatch` actor. This session is `human` and does not get
to make that change, so it is written down here instead. Whoever takes it should note that adding
a field to the collector does not backfill the history, and the raw snapshots under
`ledger/gridwatch/raw/` are what a backfill would have to read.

## A second proposal: two registry typos split one company

Entity resolution merges on case, punctuation and corporate suffix only, deliberately, because a
resolver that guesses merges two real companies. Two rows currently defeat it:
`Coreweave Compute Acquisition Co. III, LLC` and `Coreweave Compute Acquistion Co. III, LLC`,
where the second is the state's typo. Any fix has to be a stated rule with its own self-test, not
a similarity threshold.

## Batch 5: nine dossiers, and two tenants the announcements withheld

Thirty nine dossiers, 271 facts. The picks were made from the graph rather than alphabetically,
which is what the graph was built for.

**Hutto is the find.** `Hutto Data Center Campus LLC` is the exact name of the Skybox and Prologis
joint venture that signed a ten year Chapter 312 abatement with the City of Hutto for a $10 billion
campus on the megasite, six buildings and 3.9 million square feet, branded PowerCampus Austin. The
reporting names the developers, the acreage and the money. **The state record names Google as the
occupant.** No announcement does.

Careful about what that row proves. Google did not appear on it for the first time this week. The
state rewrote the row on August 21st and Google MOVED from the operator column into the occupant
column while Design, LLC went the other way. What changed is a role, not the presence of a name.
This is the third time a draft of a page here credited a registry row with more than it says, so
the note states the movement rather than the arrival.

**Red Oak is the same shape.** Compass announced the campus for "hyperscale, cloud and enterprise
customers", which is what a developer writes when the lease forbids naming one, and coverage since
has said the buildings are fully taken by a single unnamed tenant. The certified occupant is
Microsoft, on two certifications with twelve single building entities between them. Red Oak also
holds a second, unrelated hyperscale campus: DataBank with Oracle, already dossiered.

**Switch AUS 4 carries the best evidence yet that operator is a legal position.** One of its
operators of record is `Coreweave Financing DDTL V-V, LLC`. A delayed draw term loan vehicle does
not run a data hall. Anyone reading this registry as an operations directory gets it wrong there
first.

**Two rows carry no owner of record at all**, Denton and the Austin Hibbetts Road building, both
Core Scientific sites leased to CoreWeave. An empty owner column is rare here and it is
information.

Also added: `Hutto Data Center 3 LLC`, `PowerCampus Dallas by Lancaster Data Center Campus LP`
(the same Design and Google pair, in swapped columns), `Red Oak Texas Data Center 2`, and
`C1 Richardson LLC Data Center`.

`tests/glyphs.mjs` failed CI on its own control assertion and passed locally, which is exactly
what the control is for. See GATE_LESSONS entry 59 ("CSS fails silently, and a green suite has
never once looked at a colour").

## Batch 6: a second state register

The batch started as Microsoft's eleven San Antonio rows and turned into a new data source.

**The Comptroller is not the only register.** Every large commercial project in Texas is filed
with the Department of Licensing and Regulation under the architectural barriers program, and the
filing is public: project name, street address, county, type of work, scope in the filer's own
words, square footage, estimated cost, schedule and design firm. `robots.txt` permits both the
search endpoint and the print view.

For Microsoft in the San Antonio area that is 25 filings and $3.86 billion, and it names buildings
the certified list does not: SAT40, SAT46, SAT93 and SAT94. The newest and largest of them are in
**Medina County**, which carries no Microsoft row in the Comptroller's list at all. A 2019 filing
named "Microsoft Chevron/SN7 Colo 1" also explains the oddest row in the certified list, where the
oldest Microsoft building has Chevron as its occupant.

`scripts/site/tdlr_fetch.py` pulls and parses, `scripts/site/tdlr_projects.py` computes every
figure, `ledger/facilities/projects.json` holds the filings and `/construction/` publishes it.
Neither script is a routine phase and neither runs on a cron.

### Four ways this source produces a wrong number, all of them real

- The search endpoint takes a city and ignores it. A Microsoft search scoped to San Antonio
  returns the Irving buildings. Scoping happens on the records.
- A designation can be filed twice. SAT82 has two filings at two addresses. Money is grouped by
  the designation as filed so a building is not counted twice.
- A filing naming a range names several buildings and has ONE cost. Spreading SAT11-14's sixty two
  million across four rows would report it four times.
- The county field is filer entered. Five filings share one postcode on the Lambda Drive campus
  and one says Medina where four say Bexar. The page reports the disagreement.

The first version of that last check invented a postcode to county table and flagged four correct
filings against it. A postcode does not belong to a county. The check is now purely internal and
makes no claim about geography.

### The parser drops every person

A filing carries the contact who submitted it and the accessibility specialist who inspects it,
with direct phone numbers. None of it reaches a file. The gate checks again on what landed.

### Two faults this batch found in pages already shipped

**Every facility and company page had a doubled canonical.** `page()` prefixes the site to the
canonical it is handed and five call sites handed it an absolute URL, so the tag read
`https://texasaidocket.com/https://texasaidocket.com/facility/...`, along with og:url. A canonical
is markup, so no copy lint ever read one, and it resolves in a browser so nothing looked broken.
`page()` now refuses an absolute canonical at the point of use.

**Three pages were orphans.** `registry-changes` and `questions` were in the sitemap and reachable
by URL with nothing on the site linking to them. `questions` was simply left out of the footer
list its siblings are in. `scripts/site/link_check.py` checks both faults and carries an allowlist
where an unlinked page needs a stated reason.

## Batch 7: the register at scale, $36.97 billion

626 filings pulled, 480 with an owner this project tracks, 201 of them data center work.
**$36.97 billion, 38.9 million square feet, 20 counties, 2008 to 2029.**

The chart is the finding. Filings sit near zero for fifteen years and go vertical in 2024. The
largest county is **Shackelford**, population under four thousand, at $10.6 billion of Vantage
buildings. Then Dickens at $4.31 billion (Galaxy Helios Phase 2), Medina at $3.19 billion
(Microsoft), Wharton at $3.00 billion (Amazon's Project Eagle, four buildings at $300 million
each), Floyd at $1.20 billion (Horizon Junction, and one filing named CONFIDENTIAL DATA CENTER).

**The two registers join and the state published the join on both sides.** Vantage's Shackelford
filings are owned by `Vantage Data Centers TX304, LLC`, which is an owner of record on a
Comptroller row. Seventeen certified facilities can now be priced building by building.

### Six traps, every one of them real in this data

1. **The owner search is a substring match.** Meta returns Metal Building Supplies. Core Scientific
   returns Core & Main and a nail bar. Membership is decided on the owner field the filing carries.
2. **Not every filing by an operator is a data center.** Classification is on what the filer wrote,
   with exclusions first. $3.7 billion of other work by the same companies is counted separately.
3. **A warehouse and a data hall share the airport code convention.** `Fulfillment Center DFW7`
   matched the include list on its first version.
4. **A parent company is not a building.** Joining on `Microsoft Corporation` attached all
   twenty two Microsoft filings, and $3.6 billion, to one facility. The join now requires an entity
   naming at most two certified facilities.
5. **A campus could be filed by two owners and counted twice.** Checked every build, none found.
   Lancium and Crusoe both filed a $292 million Abilene building and they are two buildings.
6. **A designation can be filed twice, and a range names several buildings under one cost.**
   Carried over from batch 6 and still live at this scale.

**Several operators file nothing under their own name**: CoreWeave, EdgeConneX, Nscale, Anthropic,
Whinstone, Poolside. They lease. The construction register alone would badly understate who is in
Texas, which is why the page says so.

`tdlr_projects.py` is now 53 self-tests. The chart is deterministic, one hue, no ramp, and draws
an empty column for a year with nothing filed rather than dropping it.

## Batch 8 candidates

The four owner queries too loose to pull (Prologis 682 rows, Core Scientific 398, Applied Digital
233, Meta 85) need a name filter on the search results before fetching. Beyond that: a per facility
panel showing that facility's own filings, which the join now makes possible, and the Oracle spine
(17 undossiered rows across Vantage TX 302 to 310 and Lancium Abilene III to VIII).

Unchanged from batch 4 and still the best targets: the five Amazon codenames want a county
appraisal district pass, and CoreWeave Denton, CoreWeave Plano, the Microsoft San Antonio cluster,
Project Eagle at Wharton and Horizon Junction all have banked research waiting to be encoded.
