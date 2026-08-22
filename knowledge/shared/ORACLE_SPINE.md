# The Oracle spine

What the state record holds about the two Texas campuses that answer to one tenant. Written from
the research for batch 9 so the next session starts where this one finished rather than searching
again.

## The one thing to know first

**Two campuses in this record answer to the name Abilene and they are not in the same county.**
Everything else here follows from getting that right.

| | Lancium Abilene Clean Campus | Vantage Frontier |
|---|---|---|
| County | Taylor | Shackelford |
| City on the filing | Abilene | Abilene |
| Actually in Abilene | yes | no, it is a rural mailing address |
| Builder | Crusoe | Vantage |
| Certified buildings | 8 | 10 |
| Announced capacity | 1.2 GW | 1.4 GW |
| Occupant of record | Oracle America Cloud Services | Oracle America Cloud Services |

A rural site takes the mailing city of the post office that serves it, which is ordinary and is
not an error in the filing. It does mean that a reader, a scraper or a model working from the
city line alone will merge two separate campuses into one place. Every public
account of "Abilene" AI construction is exposed to this. **Read the county, never the city.**

## Vantage Frontier, Shackelford County

Announced August 19th, 2025. Ten data centers, 3.7 million square feet, 1.2 thousand acres,
1.4 GW, twenty five billion dollars, first building delivered in the second half of 2026, liquid
cooling on a closed loop chiller.

The Comptroller certified ten numbered entities, `Vantage Data Centers TX301, LLC` through
`TX310`, all effective October 8th, 2025. Oracle America Cloud Services is the occupant on every
one. **The announcement came first and the record followed.**

The construction register carries eleven filings under one project name,
`Vantage DC Abilene - TX3 - Project Frontier`, all at `246 PR 1604`, building by building.

- **The entity number is the building number.** `TX304` files `BLDG 4`. The register's own
  `facility` field states it.
- **Ten of the eleven are data center buildings.** The eleventh is scoped `New Office Building`
  under facility `TX311`, and its floor area is larger than all ten buildings together. Adding
  the group up without reading `scope` describes a campus half again bigger than the one being
  built. `tdlr_projects.dc_scope()` exists for exactly this.
- **Three floor plans.** Six buildings repeat one, three repeat a second, and one stands alone.
  Filed cost tracks the plan closely, which is what a repeated design looks like in a cost
  register.
- **Entity number is not schedule order.** The build sequence runs across three calendar years
  and does not follow the numbering.

**The corroboration.** Ten companies filed ten buildings over sixteen months and their floor
areas sum to within half a percent of the total Vantage announced before the first was filed.
Neither register was built to check the other and neither is a press release. This is the
strongest single thing the two register join has produced, and the figure is computed on the
construction page rather than typed anywhere.

## Lancium Abilene Clean Campus, Taylor County

Stargate site one. Lancium holds the land and the power, Crusoe built it, Oracle is the certified
occupant and OpenAI is Oracle's customer. Crusoe announced on March 18th, 2025 that the campus
would go from two buildings to eight, about four million square feet, 1.2 GW. The first two
buildings are 980,000 square feet and 200 MW.

The Comptroller certified eight, and the dates are the interesting part.

| Effective | Rows |
|---|---|
| 2022-05-26 | Clean Campus (unnumbered) |
| 2025-01-28 | Clean Campus III, alone |
| 2025-03-16 | Clean Campus IV, V, VI, VII and VIII, five on one day |
| 2026-04-17 | Clean Campus II, last of the eight |

**The record moved before the announcement here**, which is the reverse of Frontier. Five
certifications took effect two days before Crusoe announced the expansion. The row numbered
second was certified last, more than a year after the ones numbered above it, so certification
order and building number do not correspond on this campus.

**The two registers disagree about how much of it exists.** The Comptroller has certified all
eight. The construction register carries two Taylor County filings and no more, `Project
Ludicrous Building 1` under Lancium and `Project Plaid` under Crusoe, both about 483,000 square
feet and both 292 million dollars. The six later buildings have no construction filing. That is
published as a gap rather than explained away.

Both project names are Spaceballs references. That is not evidence of anything and it is not on
the site.

## Method notes worth keeping

**A certification is a tax status and a construction filing is a building.** Neither implies the
other. On Frontier the two agree building for building. On the Clean Campus they are six
buildings apart. Saying which register a fact came from is not pedantry here, it is the fact.

**Resolve source ids by url, never by position.** A bulk edit across ten dossiers wrote facts
citing `s1`, which was the construction register on the nine new rows and the developer's press
release on the one that already existed. The dossier gate caught it. Ids are local to a record.

**Check the other register before publishing a gap.** Nine dossiers were written with a gap
reading "The street address is not public" while the address sat in the construction filing this
same build reads. A gap is a claim about the world and no gate could check one, so
`site_build.contradicted_gaps()` now checks the class that is checkable and the build fails on
it. It found two more, on dossiers written long before this batch.

## What is still open

- Per building capacity is public on neither campus.
- Energization dates per building are public on neither campus.
- The six later Clean Campus buildings have no construction filing to price them.
- Water sourcing and cooling design for the Clean Campus are not public. Frontier has published
  a cooling design and no water figure.
- Vantage has not confirmed that the ten numbered entities are the announced campus. The count,
  the county and the floor area all agree with it, and agreement is not confirmation.
