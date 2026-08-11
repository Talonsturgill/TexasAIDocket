# Live telemetry — the numbers that tell a Texan this site is from here

Research completed 2026-08-11. Every endpoint below was tested live that day; HTTP status is as
observed. This is the design record for the site hero and any live counter.

---

## 1. What we are reproducing

The Alaska product's hero reads `ANCHORAGE · 15H 55M OF DAYLIGHT · LOSING 6 MIN A DAY`. It works
because it pairs **a level with a rate**, is computed from first principles, changes every day,
and names something every Alaskan physically feels. It says "from here" before you read a word.

Texas has no daylight story. The latitude spread is small and nobody thinks about it.

## 2. The Texas answer

> **TEXAS · RESERVOIRS 77% FULL · LOSING 27,887 ACRE-FEET A DAY**

Verified 2026-08-11: 24,311,245 acre-feet of 31,558,535 acre-feet conservation capacity, with a
seven-day mean change of −27,887 af/day. Every numeral computed from the last rows of one CSV.

**Source:** `https://waterdatafortexas.org/reservoirs/statewide.csv` — HTTP **200**, 1.46 MB,
five columns, **no key**, regenerated daily. (The `.json` variant is a 404 and
`/recent-conditions` is a 500. Only the CSV works.)

**Why it beats drought as the lead:** it moves daily rather than weekly, it is a measurement of
stored water rather than a panel's classification, and the rate term is the exact structural
twin of "losing 6 minutes a day."

**It has the same annual physics as daylight.** Mean daily change by month, 1933 to 2026, in
acre-feet per day:

| Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|
| +5,965 | +8,047 | +4,960 | +4,913 | +7,903 | −2,349 | −12,739 | −15,875 | −3,382 | +2,878 | +3,859 | +5,252 |

Texas reservoirs fill October through May and drain June through September. **The sign of the
rate flips twice a year on its own**, so in April the same line reads `GAINING 4,913 ACRE-FEET A
DAY` with no code change.

## 3. The number nobody publishes

The same file supports a same-calendar-day rank against 94 years of daily statewide storage:

> **TEXAS · RESERVOIRS 77% FULL · FULLER THAN 37 OF THE LAST 94 AUGUST 11THS**

TWDB publishes the level. The rank is ours. The August 11th range across the record runs from
13.3% (1933) to 94.4% (1945).

Phrase it as **a count of past observations**, never as "39th percentile," which sounds like a
model output rather than a tally.

## 4. The full candidate set, tested

| Rank | Number | Source | HTTP | Key | Cadence |
|---|---|---|---|---|---|
| 1 | Statewide reservoir storage and daily rate | `waterdatafortexas.org/reservoirs/statewide.csv` | 200 | no | daily |
| 2 | Counties under a burn ban, of 254 | `tfsfrp.tamu.edu/WILDFIRES/BURNBAN.txt` | 200 | no | daily |
| 3 | Percent of Texas in drought by category | `usdmdataservices.unl.edu/api/StateStatistics/...` | 200 | no | weekly, Thursday |
| 4 | Wind and solar share of ERCOT generation now | ERCOT `fuel-mix.json` | 200 | no | 5 minutes |
| 5 | ERCOT demand against the all-time record | ERCOT `supply-demand.json` | 200 | no | 5 minutes |
| 6 | Texas counties under an NWS heat advisory | `api.weather.gov/alerts/active?area=TX` | 200 | no | continuous |
| 7 | Days at or above 100°F this year, by station | `data.rcc-acis.org/MultiStnData` | 200 | no | daily |
| 8 | Days left in hurricane season, active systems | `nhc.noaa.gov/CurrentStorms.json` | 200 | no | continuous |
| 9 | Days until the 90th Legislature convenes | date math, no source needed | n/a | n/a | daily |

The burn ban feed is unusually good: **the count is pre-computed in line one**, so it is
self-validating. Note it is UTF-16.

**Dropped after testing:** the Edwards Aquifer J-17 well (the USGS site exists but both `nwis/iv`
and `nwis/dv` return empty series, and the Edwards Aquifer Authority page is a 26 MB single-page
app with no JSON endpoint — not cron-safe). Bluebonnet bloom timing (no data source exists;
purely anecdotal). The ArcGIS burn-ban layer returns an empty 72-byte response; use the TXT feed.

## 5. Seasonal rotation, rule-driven not calendar-driven

| Window | Lead |
|---|---|
| June to September | reservoir level and daily loss |
| July to August peak | wind and solar share, as an alternate |
| February to April | burn bans, the driest fuel of the year |
| October to January | reservoir refill, the same line with the sign flipped |
| November to January, odd years | days until the Legislature convenes |
| any week drought moves materially | drought, with the map date attached |
| August to October, coastal | hurricane season days remaining |

**Rotate by rule, not by calendar:** lead with whichever candidate is furthest from its own
historical norm for that calendar day. All four finalists have enough history to compute that —
reservoirs 94 years, drought 26 years, ACIS about a century. This never needs hand-tuning and it
automatically surfaces whatever is actually unusual today.

Underlying seasonal concern calendar: January to February ice storms and the grid; March to
April wildfire; April to May hail and tornadoes; June onward heat and drawdown; August peak heat
and peak reservoir loss; August to October hurricanes; October to December refill.

## 6. Honesty rules for the hero

**ERCOT demand against the record is the dangerous one.** On 2026-08-11 actual demand was 86,926
MW against an all-time record of 87,533 MW set July 21st, 2026 — **99.3%**. Rendered as a
percentage of record that reads as a siren, and it is not one: demand near the record on a day
with 96,980 MW online is a normal August afternoon.

If it is published at all, publish **demand and available capacity as two separate measured
numbers and never their ratio**, and never a fill bar. This is the same reasoning as the
bar-never-a-dial rule.

**And the record figure itself came from Wikipedia.** Under this project's law that numbers are
computed and never generated, it cannot be typed into a template. It must be recomputed from the
ERCOT MIS archive (`IceDocListJsonWS?reportTypeId=13101` returns 200, `mirDownload?doclookupId=`
returns a zip) and committed to `config/` as data with a recompute script.

**Reservoir storage** is safe because it is a measurement, but the rate must be labeled as what
it is: a **seven-day trailing mean**. Say "LOSING," never "ON PACE TO" or "WILL BE EMPTY BY."
Never extrapolate it forward.

**Drought is a panel's classification, not an instrument reading.** Attribute it every time, and
publish the **map date** rather than today's date, or the page is claiming a freshness it does
not have.

**Burn bans are the cleanest of all** — a count of county orders in effect is a legal fact, not
a hazard assessment. `133` is not a fire-risk score and must never sit next to one.

**Heat has no canonical station**, so there is no honest statewide "Texas has had N
hundred-degree days." Days at or above 100°F this year, as of 2026-08-11: El Paso 39, Midland
20, DFW 17, Austin 12, Lubbock 12, Corpus Christi 2, Houston 1, San Antonio 1. Use it city
scoped or not at all.

## 7. Two things that must start on day one

**Both the burn ban feed and the ERCOT fuel mix are current-state only.** The burn ban file
carries no history at all, and the ERCOT feed carries a two-day window. So "up from 118 last
week" is impossible unless we have been storing our own daily snapshot since the beginning.

Start that ledger on the first day the collector runs, or the delta can never be published.

## 8. Architecture note

ERCOT sends `access-control-allow-origin: https://mis.ercot.com`, so a browser fetch from a
static Pages site will fail. The other finalists send no CORS header at all. Every one of these
must be fetched **server side in the cron**, with the value baked into the build — which is
exactly how this project already works.
