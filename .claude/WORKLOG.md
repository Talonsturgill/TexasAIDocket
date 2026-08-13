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
| M2 | `geography_check.py`: an item must be locatable. Ratchet, with the backlog reported and not failed | TODO |
| M3 | Derivation: metro is COMPUTED from counties, never typed. Wire into `docket_build.py` | TODO |
| M4 | The site: `/places/` index, a page per metro and per touched county, cross-linked from every item | TODO |
| M5 | The ask engine: a `by_metro` view, metro entities in the vocabulary, catalogued questions | TODO |
| M6 | The water watch reconciled onto the registry, and the San Antonio gap reported | TODO |
| M7 | The daily routine's prompt: the re-verify phase fills geography, and the admit phase requires it | TODO |
| M8 | Proof: rebuild the site, check freshness byte-equality, run every gate, look at the pages | TODO |

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
