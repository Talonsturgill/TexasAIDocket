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

## Batch 6 candidates

Unchanged from batch 4 and still the best targets: the five Amazon codenames want a county
appraisal district pass, and CoreWeave Denton, CoreWeave Plano, the Microsoft San Antonio cluster,
Project Eagle at Wharton and Horizon Junction all have banked research waiting to be encoded.
