# WORKLOG — beyond ERCOT: naming the data centers, and generation by county

Approved 2026-08-18 by the owner ("build it all") off the source investigation at
https://claude.ai/code/artifact/31afdbd6-daeb-48cd-83e6-8a03e6605135

## Why

The grid page measured ERCOT and left attribution to inference. Two public sources
were probed live and change that:

  A  Texas Comptroller data center registry. 149 named facilities, owner/occupant/
     operator, effective dates 2013 to 2026. Keyless HTML table. THE ONLY SOURCE
     TESTED THAT NAMES DATA CENTERS.
  B  EIA-860M generator inventory. Monthly xlsx, ~14MB, keyless with a UA. County,
     Balancing Authority, lat/long, nameplate MW, and separate Operating / Planned /
     Retired / Canceled sheets. Joins to the 50 counties the docket already lights.

Dead, confirmed by probe, do not revisit: FERC 714 (403 to bots) and Chapter 403
JETI (excludes data centers by statute).

## Laws this work does not bend

- NO LOAD ATTRIBUTION. Nothing tested publishes a data center's power draw. The
  registry names facilities, ERCOT gives a system total, and the distance is the gap
  this page already publishes honestly. A modelled per-site figure would trade the
  page's best property for a number.
- Neither collector joins the DAILY cron. An outage on Comptroller or EIA must never
  cost an ERCOT demand day, which is the one irreversible failure here.
- Every published numeral is computed and authorised where it is computed.
- No reliability verdict. Bars, never dials.

## File map

  scripts/gridwatch/datacenters_collect.py   registry reader + self-test        [A]
  scripts/gridwatch/generators_collect.py    EIA-860M reader + self-test        [B]
  scripts/site/datacenters_panel.py          renderer + numeral authorisation   [C]
  scripts/site/generators_panel.py           renderer + numeral authorisation   [D]
  ledger/gridwatch/datacenters.json          current roster, full               [A]
  ledger/gridwatch/datacenters.jsonl         one line per read, counts only     [A]
  ledger/gridwatch/generators.jsonl          one line per report month          [B]
  .github/workflows/datacenters.yml          weekly                             [E]
  .github/workflows/generators.yml           monthly                            [E]

## The trap already paid for

EIA-860M's sheet XML OMITS EMPTY CELLS, so positional column indexing silently
shifts and produces a confidently wrong join. Cost two passes during research. The
parser MUST read each cell's r="A1" reference and the self-test MUST replay a row
with a gap in it.

## Tasks

| # | task | status |
|---|---|---|
| A1 | datacenters_collect.py, parse + plausibility + self-test | DONE |
| A2 | live collect, commit the roster | DONE 149 facilities |
| B1 | generators_collect.py, cell-ref parser + self-test | DONE |
| B2 | live collect, commit the series | DONE 202,461 MW op |
| C  | datacenters_panel.py, the registry curve and operators | DONE |
| D  | generators_panel.py, county generation | DONE |
| E  | two workflows, own cadence, never the daily cron | DONE |
| F  | wire panels into grid_page, numeral union | DONE |
| G  | full gates incl. browser suites, PR, merge | IN PROGRESS |

## Wrap

W1 delete this file when G is done.

## Bugs found while building, both silent

1. The registry nests a <ul class="dc-list"> inside a cell when a site has several
   operators. Flattening it welded "C1 Dallas - Allen (LOT 1) LLC" and "Oracle
   America, Inc." into one operator that belongs to neither. Cells now yield lists.
2. sharedStrings.xml holds rich text as several <r><t> runs inside ONE <si>.
   Counting each <t> as an entry shifted every index after the first formatted
   cell, which put the header one column left of its data: 'Entity Name' above the
   Entity ID values, every county read as a balancing authority. Nothing raised.
   One string per <si> now, and the plausibility floor is what caught it.
