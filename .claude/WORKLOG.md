# WORKLOG — the data centers tab

Owner's directive, 2026-08-22. Data centers are what people care about, so they get their own
tab. To keep the masthead at eight, About rolls into Services. The data center material comes
off the Grid page and the Grid keeps only grid. Lead the new page with the registry field, the
force directed graph, and make it snazzy. Do not overcrowd Services, and keep the way to send
a message or book a call obvious. **Data centers sits immediately right of Docket.**

## The masthead

Was: Home · Docket · Articles · Videos · Grid · Water · Services · About
Now: Home · Docket · **Data centers** · Articles · Videos · Grid · Water · Services

Eight either way. `FOOTNAV` derives from `NAV[1:]`, so About leaves the footer with it.

## What moves where

| Section | From | To |
|---|---|---|
| The registry field (the graph) | `/company/` | `/datacenters/`, leading |
| Who is here, the certified roster | `/grid/` | `/datacenters/` |
| What Texas filed to build, in summary | `/construction/` stays, summary added | `/datacenters/` |
| The Queue Gap | `/grid/` | stays |
| Yesterday on the grid | `/grid/` | stays |
| What is being built for them, generation | `/grid/` | stays. It is EIA generator data, a grid fact |
| One desk two jobs, and the four promises | `/about/` | `/services/` |
| How the work gets verified | `/about/` | already on `/data/` as "How a fact gets in" |

`/about/` is removed. Every link to it today is the masthead itself, on three hundred and
seventy pages, so dropping it from `NAV` removes them all. Check for prose links before the
build, because `link_check` fails on a href that resolves to nothing.

## Status

| # | Task | State |
|---|---|---|
| 1 | Worklog | DONE |
| 2 | `NAV`, with Data centers after Docket and About gone | DONE |
| 3 | `/datacenters/` page, graph leading | DONE |
| 4 | Move Who is here off the grid page | DONE |
| 5 | Construction summary on the new page | DONE |
| 6 | Services, About folded in, layout decluttered | DONE |
| 7 | Remove `/about/`, fix every reference | DONE |
| 8 | Crumbs and cross links repointed at the new tab | DONE |
| 9 | Gates, render and look, both widths | |
| 10 | Ship | |

## Rules this touches

`link_check` proves every page is reachable from home and every canonical resolves.
`table_fit` proves a data table's columns fit their content, at four widths.
`house_style_check` reads every published sentence.
`site_fresh_check` proves `docs/` is exactly what the ledgers produce.
Numerals stay computed. Nothing on the new page is typed.

## What the work found

**The grid page was mostly not about the grid.** The certified roster was fifty nine of its
hundred and five kilobytes. Moving it left a grid page of forty six kilobytes carrying the
queue gap, yesterday's load and the generation being built, which is what the tab says it is.

**The field was on the wrong page.** It led nothing. It sat under an intro paragraph on the
companies index, a page reached by following a link from a section of another page. It leads
the new tab now and `/company/` links up to it rather than drawing a second copy, because two
forty node simulations on two pages give a reader no way to know which is the real one.

**The tile row was a broken grid before it was looked at.** `auto-fit` fitted three counts at
the reading measure and dropped the fourth onto a row of its own beside an empty cell. Stated
as four, and two at the phone breakpoint, in the sheet that defines them.

**About left four references behind**, none of them in the page itself. The llms.txt map, two
lists in `lastmod.py`, and the fixture `site_fresh_check` hand edits to prove it can still go
red. A route is never only its builder.
