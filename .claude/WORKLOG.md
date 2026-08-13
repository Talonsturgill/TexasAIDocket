# WORKLOG — metro scoping

Written before touching code, per CLAUDE.md. The previous worklog (carousel machine to v1)
had all its waves DONE and is replaced here rather than kept, which is what that file's own
rule says to do.

## The directive

> "do #2, Metro scoping, massive task so go slow"

Task #2 in the standing list: **per-city views across the docket, the site, the grid watch and
the ask engine.** A reader in Abilene should be able to see what this record says about Abilene.

## Measured starting point (2026-08-13, main at 6ce6c2b)

| | state |
|---|---|
| `ledger/docket.json` | 13 items, **`metro: null` on every one** |
| items with any county | **1 of 13** (tx-2026-0003, the Abilene buildout, 22 counties) |
| items `statewide: false` with no county and no metro | **3** — geographically null, on no page at all |
| `assets/geo/tx-places.json` | 254 counties, FIPS, computed centroids, aliases, provenance. **No metro layer** |
| the site's map | real, generated from the record, currently lighting **22 of 254** |
| the site's `counties/` page | real, and reflects the same one item |
| `ledger/gridwatch/water.jsonl` | **already carries 19 metros**, from reservoir tags |
| the ask engine's smart views | `open_now, by_county, by_topic, by_decider, by_status, item, counts` — **no metro view** |

So the honest summary: the schema anticipated this, the plumbing is largely built, and the
data layer that would make any of it mean something does not exist.

## Three findings that shape the design

### 1. Half of Texas is in no metro, and it is the half this story is about

The 2023 OMB delineation file puts **133 of 254 Texas counties inside a CBSA. The other 121 are
in none.** Those are not empty quarters: Shackelford, Childress, the Permian outside
Midland-Odessa, the Panhandle wind and most of the Ogallala are where the physical AI buildout
is actually happening.

**So the scoping unit cannot be the metro.** A geography facet that only knows metros cannot
place the Vantage site in Shackelford County, and would quietly drop the most Texas half of the
record. The unit is a **place**: a metro where there is one, a county where there is not.

### 2. There are already two metro vocabularies, and they disagree

`waterwatch_collect.py` groups reservoirs into 19 metros. Adding a second list for the docket
is precisely the entity drift `places.py` was written to prevent -- "Austin" meaning two
different things on two pages of one site.

**Every divergence resolves against the federal file, with a code.** Checked, not assumed:

| water watch says | OMB says |
|---|---|
| `dallas` and `fort_worth` separately | Metropolitan **Divisions** 19124 Dallas-Plano-Irving and 23104 Fort Worth-Arlington-Grapevine, inside CBSA 19100 |
| `midland_odessa` as one | two MSAs, 33260 Midland and 36220 Odessa, inside **CSA** 372 Midland-Odessa-Andrews |
| `temple_killeen` | CBSA 28660 **Killeen-Temple**. A name-order alias |
| `nacogdoches` | CBSA 34860, **Micropolitan** rather than Metropolitan. Real, just not an MSA |
| no `san_antonio` | CBSA 41700 exists. This is a **gap in the reservoir tagging**, not a taxonomy question. Canyon and Medina serve it |

The water watch's groupings are RIGHT for water -- a reservoir serves a city, not a statistical
area -- and they are the right grain: divisions and CSAs are real OMB entities with codes. So
the registry carries all three grains and a surface picks the one it needs. **One id, several
memberships.**

### 3. I cannot write the record, and that is correct

`ownership.yaml` gives `ledger/docket.json` to the `daily` actor. A maintainer session owns
`scripts/`, `assets/`, `knowledge/shared/` and the workflows. **So this work builds the machine
and the gate; the daily routine populates the geography during its re-verify phase.**

That is the right split and it decides the shape of the gate: a hard fail on day one would
block every run until a thirteen-item backlog was cleared by hand, in a lane the runs own. So
the gate is a **ratchet** -- it fails on any newly admitted item that is unlocatable, and
reports the existing backlog without failing, and the backlog can only shrink.

## Rules this work obeys

- Numbers are computed, never generated. The county-to-metro mapping is READ from the OMB
  delineation file and vendored with its source, never typed from memory. The 2023 file already
  caught two names I would have got wrong: Houston is **Houston-Pasadena-The Woodlands** since
  the 2023 revision, and Austin is **Austin-Round Rock-San Marcos**.
- The provenance rule in `places.py`: a field this program did not compute or read from a cited
  source is not written at all.
- `docs/` is generated. Never hand-edited.
- Every gate gets a `--self-test` that replays the defect it exists for, and every gate is run
  by exit code.
- No em dashes, no colons or semicolons in published copy, ordinal dates, no first person.

## Waves

| # | Wave | Status |
|---|---|---|
| M1 | The place spine: vendor the Texas CBSA subset, extend `places.py` with metro/division/CSA, resolver + self-tests | **DONE** — 26 metro + 41 micro areas, 2 divisions, 13 combined, 133 of 254 counties covered. 13 new self-tests |
| M2 | Locatability: tighten the rule that had a loophole, resolve every county name, derive the metro, ratchet the backlog | **DONE** — 6 new assertions in `docket_build`, and it caught its own fixture |
| M3 | Derivation: the projection carries `by_metro` and `unmetroed_counties` | **DONE** — and the first run proved the design: 13 of one item's 22 counties are in no metro |
| M4 | The site: `/places/` index, a page per metro and per touched county, cross-linked from every item | **DONE** — 27 pages to 48. The numeral gate had to be made able to fail first, and what it then found was most of this wave |
| M5 | The ask engine: a `by_metro` view, metro entities in the vocabulary, catalogued questions | **DONE** — 142 catalogued questions, and it caught a place answer counting statewide items as local coverage |
| M6 | The water watch reconciled onto the registry, and the San Antonio gap reported | **DONE** — crosswalk derives the registry id beside TWDB's own tag, never over it |
| M7 | The daily routine's prompt: the re-verify phase fills geography, and the admit phase requires it | **DONE** — plus the backlog is now a success criterion |
| M8 | Proof: rebuild the site, check freshness byte-equality, run every gate, look at the pages | **DONE** — and looking found three things every gate passed |

## Log

(appended as waves land)

### M1 — the place spine (2026-08-13)

Vendored `assets/geo/tx-cbsa-2023.json` from the OMB July 2023 delineation, extended
`places.py` with a `cbsa` subcommand and a metro layer on every county, and made metros
first-class place records.

**The existing self-test caught the design error immediately, and it was a Texas-specific
one.** The first version folded each CBSA and CSA name into its member counties' aliases,
and five counties stopped resolving: El Paso, Lubbock, Midland, Pecos and Tyler. A Texas
metro is named for its central city, and there is frequently a DIFFERENT county with that
name somewhere else. **Reeves County contains the city of Pecos. Pecos County is two hundred
miles away. Smith County contains Tyler. Tyler County is in the Piney Woods.** One index made
those strings ambiguous, and this resolver refuses ambiguity by design, so it correctly
refused both readings and the county lookups that had worked for weeks went dark.

So the index is per GRAIN: county, cbsa, division, csa. That turned out to be needed twice
over -- adding principal cities as aliases (nobody types "Houston-Pasadena-The Woodlands")
made "Houston" ambiguous between the CBSA and the Houston-Pasadena CSA, which one metro index
would also have refused.

Reading the file rather than remembering it caught two more: Houston has been
**Houston-Pasadena-The Woodlands** since the 2023 revision and Austin has been
**Austin-Round Rock-San Marcos**. Typed from memory, both would have been the previous
decade's names, on the two biggest pages of the site.

Resolver behaviour now, checked end to end: `Taylor County` walks to the Abilene MSA,
`Shackelford` resolves as a county and returns None for its metro rather than guessing,
`Arlington` lands on Dallas-Fort Worth, `The Woodlands` on Houston, `Round Rock` on Austin.

### M2 — locatable, and the rule that already existed (2026-08-13)

The plan said "add a gate". The gate was already there, and its third clause was a loophole:

    if not (statewide or counties or on_ercot):  fail("Every item is somewhere")

**Three items pass that on `on_ercot: true` alone**, with no county and not statewide. ERCOT
carries about ninety percent of the state's load, so "on the ERCOT grid" is barely narrower
than "in Texas". It is a PROPERTY of an item rather than a PLACE, and it is not something a
reader can filter by. Those three appear on no county page, light no county on the map, and
would appear on no metro page either, while the check written to prevent exactly that
reported clean. The shape `GATE_LESSONS.md` keeps collecting: **a rule satisfied by a value
that does not carry the meaning the rule is about.**

`on_ercot` stays in the schema, because it is a true and useful fact. It no longer counts as
a location.

Second half: **twenty-two county names sat in the record as free strings and nothing had ever
checked they were real Texas counties.** They all happen to resolve. A typo would have been
stored, lit nothing on the map, and said so to nobody. They resolve through `places.py` now,
and an unresolvable name comes back with candidates.

Third: **the metro is derived and never typed.** If `geography.metro` disagrees with what the
counties compute to, the build fails. That is the compute-not-generate law applied to a field
a well-meaning editor would otherwise fill in by hand.

**The backlog is a ratchet.** `ledger/docket.json` belongs to `daily`, so this session cannot
fill the three in; the routine does it at re-verify. A hard fail today would block every run
out of a lane it does not own. So the three are named in `GEOGRAPHY_BACKLOG`, they are the
only exemptions, and the list can only shrink.

**And the gate caught its own test.** `base()` in the self-test uses id `tx-2026-0001`, which
is one of the three backlogged items, so the exemption swallowed the "item that is nowhere"
assertion and a test that had checked something real for weeks began passing for the wrong
reason. Fixed by giving that fixture an id outside the backlog, and the ratchet itself is now
asserted in both directions.

### M3 — the projection carries places (2026-08-13)

`project()` now emits `by_metro` and `unmetroed_counties`, both derived from the counties
through `places.metro_of`, plus the two counts a page can publish.

**The first run vindicated the two-index design in one line.** The single substantial item in
the record touches 22 counties. They resolve to 7 statistical areas covering 9 counties, and
**13 counties fall outside every metro** -- Borden, Coke, Coleman, Comanche, Eastland,
Glasscock, Hamilton, Mitchell, Runnels, Shackelford, Somervell, Stephens and Sterling. A
metro-only view would have silently dropped more than half of the most substantial item in
the record, **including Shackelford, which is the Vantage data centre county.**

So `counties_touched_outside_any_metro` is published rather than hidden. Same instinct as the
grid watch publishing the size of what is not public: a per-city page that quietly omitted
those counties would be a more confident and a less honest page.

### M4 — the place pages, and the gate that could not fail (2026-08-13)

The wave was meant to be pages. Most of it turned out to be the gate.

`CLAUDE.md` calls `numeral_lint` "a hard build gate" over every numeral in published copy.
It ran over two of forty-eight pages. Wiring it to the rest took ten lines, and then it
**still could not fail on anything**, for two unrelated reasons, both green the whole time.

**First, scope.** The watch pages' authorised sets were merged into one site-wide set. The
grid watch authorises an hourly series and a full fuel mix, several hundred figures across
every magnitude, so almost any number was authorised somewhere. **A gate is only as strong
as its narrowest scope.**

**Second, and worse, the scanner deleted authorised strings as SUBSTRINGS.** Any real page
authorises all ten single digits within a few counts and dates. So `8,927` was deleted one
character at a time by four authorisations that had nothing to do with it, nothing survived,
and nothing was reported. Every figure on the site dissolved from the inside. The module's
own docstring claimed it was "strong on the figures that matter, which are the multi digit
and decimal ones", and that was the exact class it was blind to.

Neither was found by a test. Both were found by planting a figure by hand. So the plant is
a test now, three of them, and one plants a figure that IS computed on a different page,
which is the only way to catch a set that has quietly widened again.

What the working gate found, in order:

- The footer printed **hand-typed coordinates** four words from the line "Every numeral
  computed from data", and the comment above them granted itself an exemption in prose. The
  typed pair also named a different point from anything in the repository. Read from the
  gazetteer's Travis County centroid now, rounding rule written down.
- `&#x27;` in that same footer put a phantom `27` on all 48 pages. Entities are decoded now,
  because the scanner has to read what the reader reads.
- `_watch_numerals` fed raw readings to a function that wants a derived frame. Every call
  raised `KeyError`, a bare `except` swallowed it, and both watch pages then failed on their
  own correctly computed figures.
- **The record tells readers "See item tx-2026-0010" and no such item exists.** Fact
  checking culled it and the pointer survived. Three checks nearly should have caught it:
  the link checker reads `href` attributes and this is prose, the claims gate checks claims
  and this is not one, and the numeral gate's own self-test **used that same id** to
  demonstrate the cross-reference exemption. New shape for `GATE_LESSONS.md`: **a reference
  is a dependency even when it is not a link.**

`gate_cross_references` is ratcheted like the geography backlog, because `ledger/docket.json`
belongs to `daily`. Both ratchets now print on every build, green or not, because an
exemption nobody sees stops being a debt.

The pages themselves: `/places/`, a page per metro and per unmetroed county, and a `Where`
section on every item linking both. Checked as a **round trip** rather than as "the page
contains the word place", so a link that points at a page which does not list that item back
is a red build.

### M5 — by area, and a true count of the wrong set (2026-08-13)

A reader types a city. The box had no way to hear one. `by_metro` is a view now and the
matcher knows every area's principal-city aliases.

Two lists, deliberately different. The **index** carries all 67 areas as vocabulary, so a
reader typing "El Paso" is told the record holds nothing there rather than handed the
nearest fuzzy match. The **catalogue** names only areas the record reaches, so it never
promises an answer it does not have.

**The defect this uncovered mattered more than the feature.** The first working version
answered "El Paso" with "9 items in the El Paso area", one line above a note saying nothing
had been found in either of El Paso's counties. All nine were statewide. **Every number in
that sentence was correct and the sentence was false**, so no count assertion could have
caught it. Local and statewide are counted separately now, in both place views, and
`tests/ask_engine.mjs` recomputes the local set from the shipped index for all 87 place
questions. Verified by mutation.

### M6 — one registry, and the source's own words kept (2026-08-13)

The water watch's nineteen slugs are not a vocabulary this project chose. They are
`municipal_*` tags TWDB publishes. So they are not rewritten, and `Resolver.crosswalk`
derives the registry id beside each one.

The grain is chosen by what resolves rather than declared. Dallas and Fort Worth land on
metropolitan **divisions**, which is right because they are two water systems.
`temple_killeen` resolves by token set against Killeen-Temple, so a reversed name needs no
special case. `midland_odessa` resolves to **two** CBSAs rather than to the combined area,
because that area also contains Andrews and the tag does not claim Andrews.

**San Antonio has no line and that is now published as a gap**, with Canyon and Medina named
because both are confirmed present in the day's record.

**And an error the numeral gate cannot see.** The first version published "20 of the 67
statistical areas". 67 is the CBSA count and the 20 included two divisions, which are not
CBSAs and are both inside one, so Dallas and Fort Worth were counted twice and their shared
area counted zero times. Both numerals were computed and the gate passed them: **a gate that
checks whether a figure was computed cannot check whether it was the right figure.** Every
grain lifts to a CBSA before counting now, and the self-test asserts `lined + unlined ==
areas`, which is the assertion that would have caught it.

### M7 — the routine owns the backlog (2026-08-13)

Both ratchets exist because the record belongs to `daily`. That is half a design until the
routine is told they are its work. Phase 3 reads the `backlog:` lines and both kinds are
named with what to do. Phase 5 closes the door: a new item names its counties or is
statewide, or it is **held in the seed**. A statewide flag used to mean "I could not tell"
is worse than holding it.

Phase 7 looks at the water page too. `CLAUDE.md` has always named both watch pages as the
ones a run looks at, and the only checker is the grid one, so **the water page has been going
out unread every day**. A water page check belongs beside the grid one and would live in
`scripts/gridwatch/`, which neither the daily routine nor a maintainer session owns, so it
is recorded here as a proposal rather than written.

### M8 — looking at it (2026-08-13)

Every self-test green, 48 pages byte-fresh, house style clean, port audit clean, ask engine
green. Then the part none of that can do, which found three things:

- **Every item page and every topic page marked HOME as `aria-current="page"`.** `""` meant
  both "Home's href" and "none of these". A screen reader was told it was on the front page
  while reading an item. `None` is the sentinel now and those pages mark THE RECORD, which
  is true of both.
- **A place page's map was 900 pixels of mostly unlit Texas** with the one item it exists to
  show below the fold. On a place page the map is orientation, not the subject. An inset
  variant at a third the height, with the survey furniture off, because at that size the
  graticule labels are seven pixels and a reader can see they are there and cannot read them.
- **A two column tally stranded its count a thousand pixels from its label.** Giving the
  label 99% only moves the gulf when there is no third column to absorb it, so the table
  itself is capped.

One thing that looked like a fourth and was not: the masthead appeared transparent over
scrolled content. It is not. `scroll-behavior: smooth` meant the screenshot caught the band
mid-fade at 300ms. Measured before changing anything.
