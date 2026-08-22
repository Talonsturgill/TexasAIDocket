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
| 2 | `NAV`, with Data centers after Docket and About gone | |
| 3 | `/datacenters/` page, graph leading | |
| 4 | Move Who is here off the grid page | |
| 5 | Construction summary on the new page | |
| 6 | Services, About folded in, layout decluttered | |
| 7 | Remove `/about/`, fix every reference | |
| 8 | Crumbs and cross links repointed at the new tab | |
| 9 | Gates, render and look, both widths | |
| 10 | Ship | |

## Rules this touches

`link_check` proves every page is reachable from home and every canonical resolves.
`table_fit` proves a data table's columns fit their content, at four widths.
`house_style_check` reads every published sentence.
`site_fresh_check` proves `docs/` is exactly what the ledgers produce.
Numerals stay computed. Nothing on the new page is typed.
