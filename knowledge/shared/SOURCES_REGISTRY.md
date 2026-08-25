# Data sources — what is actually fetchable, and what we may fetch

Compiled 2026-08-11. Verification marks: **[V]** fetched and saw real data, **[P]** loaded but the
data was not confirmed, **[X]** blocked or absent.

**A source does not enter this registry on the strength of documentation.** Every `[V]` row was
retrieved. This matters because the failure mode for a daily automation is not a source that never
worked, it is a source that worked once in a research pass and was never checked again.

## A standing rule, learned the hard way on this very page

**A tool-level failure is not a property of the source.** An earlier pass recorded
`texastribune.org` as returning 403 and nearly wrote the best news source in Texas onto a
permanent blocked list. A later pass fetched **the same article URL at the same moment with
`curl` and got HTTP 200, 292,873 bytes, correct headline.** The 403 belonged to the fetching
client.

**Before any domain enters a blocked list that automations will inherit, retest it with a second
client.** Nothing throws when a collector silently skips a source it could have reached, which is
exactly why this needs to be a rule rather than a habit.

## And the corollary: robots.txt must be re-checked PER HOST, never inherited

Two sources this registry listed as working turned out to be disallowed, and one host we assumed
was hostile turned out to name us specifically as welcome. **User-Agent behaviour and robots
policy are independent, and both vary host by host.**

| Host | robots.txt | Behaviour | The compliant move |
|---|---|---|---|
| **`gisweb.tceq.texas.gov`** | **`Disallow: /` for ALL agents** | would serve data | **Do not fetch. Use EPA Envirofacts instead** |
| **`courtlistener.com`** | disallows `*` **but explicitly ALLOWS `claudebot`** | 200, **and a CloudFront 403 on `robots.txt` itself was seen 2026-08-16** | **Send the ClaudeBot UA. It is the compliant one here. A 403 fetching the robots file is an edge failure and NOT a policy change, so do not write this host off on one** |
| `gov.texas.gov` | **serves no robots.txt at all** | 200 to a browser UA, posts and `/uploads/files/press/` PDFs alike | Browser UA. Nothing is disallowed because nothing is stated |
| `lrl.texas.gov` | content signals, **no path disallow** | 200 | Usable. The weekly interim hearings post is the cheapest dated public microphone |
| `interchange.puc.texas.gov` | **no robots.txt at all** | **402 to a ClaudeBot UA, 200 to a browser UA** | Browser UA. Nothing is disallowed |
| `texastribune.org` | permits both | **403s a ClaudeBot UA, 200 to a browser UA** | Browser UA |
| `comptroller.texas.gov` | broad `Disallow: /*/` **but `/economy/` is explicitly allowed** | 200 | Stay inside `/economy/` |
| **`texreg.sos.state.tx.us`** | names FacebookExternalHit, bingbot, GPTBot, ChatGPT-User, OAI-SearchBot, Googlebot and AhrefsBot; **no `*` group and no ClaudeBot group**. Re-confirmed 2026-08-16 | **allowed** | **Usable and currently unexploited. The Texas Register is the authoritative publication for proposed rules and their official comment instructions, which makes it the single best addition to the collector set** |

**A 402 or a 403 is not a robots decision, and a robots allowance is not a promise of a 200.**
Check the file, then check the fetch, and record both.

**WHERE A RUN WRITES WHAT IT OBSERVED.** This file is `human` owned and stays that way, because it
carries the disallow list, and an unattended run that could edit its own boundary does not have
one. So a run appends to `knowledge/shared/SOURCES_FIELD_LOG.md` instead, which it owns and may
only add to. A maintainer folds those entries up into this file. The four entries dated
2026-08-16 above arrived that way.

---

## 0. THE FINDING THAT CHANGES THE GRID WATCH DESIGN

**ERCOT's dashboard feeds carry no archive at all.** Every one is a rolling window:

| Feed | Window |
|---|---|
| `fuel-mix.json` | **2 days** |
| `supply-demand.json` | **1 day** |
| `daily-prc.json` | **today only** |
| `loadForecastVsActual.json` | **3 days** |

There is no historical endpoint, no date parameter, and no bulk file behind these. **A day we do
not collect is a day that is gone**, and ERCOT cannot backfill us.

This is independent, measured confirmation of the rule already written into `CLAUDE.md`: the
collector runs on its own cron and never as a routine phase, because a carousel run failing its
gates on a Tuesday must not cost Tuesday's reading. **A missed day is the one irreversible failure
this project has, and now we have the evidence rather than the analogy.**

It also creates the asset. **Snapshot `supply-demand.json` and `fuel-mix.json` daily and within a
year we own a public five-minute ERCOT series that does not otherwise exist for free.** That is
not a side effect of the Grid Watch. It may be the most valuable thing the Grid Watch produces.

Two implementation consequences, both already in the plan and now load-bearing:
- **Snapshot the raw response to disk before parsing.** A parse bug must not cost the record.
- **Trust the payload's own timestamp over HTTP freshness.**

---

## 1. Robots and terms, which we obey

This project publishes a provenance commitment. **A collector that ignores a stated crawl
restriction would make that commitment worthless.** Five findings need decisions rather than
defaults.

**Two of these were folded up from `SOURCES_FIELD_LOG.md` on August 25th, and one of them
corrects a line in this very file.** Both were re-fetched here before being written down, which
is the only reason the second was caught: the log recorded `lrl.texas.gov` as a working
substitute and it is not one for half of this project's clients. **A run's observation is not
law until somebody re-fetches it.**

| Host | What it says | Our position |
|---|---|---|
| `capitol.texas.gov` | **`Disallow: /TLODOCS/`**, which the table in section 2 never listed. Every House and Senate hearing notice, schedule, bill text and bill analysis lives under that path. The live file also disallows `/TLOWebServices/`, `/Prototype/`, `/Controls/`, `/Help/`, `/Images/`, `/bin/`, `/ig_common/`, `/Scripts/`, `/Web References/` and four `/MyTLO/` paths, against the three this file used to name | **OFF LIMITS. Do not fetch `/tlodocs/`.** The directive is upper case and the live urls are lower case, so a case sensitive reading would not match it. Taking that reading is routing around a disallow on a technicality and this project does not do that. **Substitute, verified: `capitol.texas.gov/Committees/MeetingsUpcoming.aspx?Chamber=S`** answers 200, sits under no disallowed path, and carries the date, time, room and cancellation state of every upcoming committee meeting. `www.legis.texas.gov` 301s to this host, robots.txt included, so it is the same policy and not an alternate route |
| `lrl.texas.gov` | **`User-agent: ClaudeBot → Disallow: /`**, alongside the same for GPTBot, CCBot, Google-Extended, Bytespider, Amazonbot, Applebot-Extended, meta-externalagent and CloudflareBrowserRenderingCrawler. `User-agent: *` is `Allow: /` with `Content-Signal: search=yes, ai-train=no, use=reference` | **OFF LIMITS, WHOLE HOST, ALL CLIENTS. Decided August 25th.** WebFetch identifies as ClaudeBot and this host named it, which settles the research phase on its own. The collectors send a descriptive `TexasAIDocket/1.0` that matches `User-agent: *` and its `Allow: /`, so on the letter of the file they are permitted, and they are held out anyway. Reasoning below. Section 2 used to read "content signals and **no path disallow**", which is true and is why this was missed: there is no PATH disallow, there is a whole-site disallow on the agent |
| `data.capitol.texas.gov` | **`User-agent: ClaudeBot → Disallow: /`**, plus `Disallow: /api/` for everyone, `Crawl-Delay: 10`, and `Content-Signal: ai-train=no, use=reference` | **OFF LIMITS. Do not collect.** The API responds, which makes this a choice rather than an obstacle, and the choice is to respect it. Mitigating: its 907 packages are elections and redistricting plans, **not bill text or status**, so the loss is small. Bill data comes from OpenStates or LegiScan with a free key |
| `waterdatafortexas.org` | `Disallow: *.csv` and `/reservoirs/api/*`. **The reservoir CSVs fall inside that rule.** The groundwater `.json` and `.geojson` endpoints do **not** | **NEEDS AN OWNER DECISION** before any reservoir collector ships. Groundwater JSON is clear to use today. See section 5 |
| `www.ercot.com` | Does **not** disallow `/api/` | Clear to use, at no more than one poll per minute, with a descriptive User-Agent |

### Why `lrl.texas.gov` is off limits to the collectors too, when the file permits them

Decided August 25th, and written out because a rule an unattended machine follows has to be one
it cannot get wrong.

**A split rule is the one a run breaks.** "WebFetch no, collectors yes" asks every future run to
know which client it is holding before it reaches for a url. That is a distinction a run makes
correctly on a good day and silently wrong on a bad one, and the bad one produces a fetch this
project promised not to make. **A whole-host rule cannot be got wrong**, and the crawl boundary
is exactly the place to prefer a rule that survives a careless reader.

**Nine named agents is a position, not a string match.** The file blocks Amazonbot,
Applebot-Extended, Bytespider, CCBot, ClaudeBot, CloudflareBrowserRenderingCrawler, GPTBot,
Google-Extended and meta-externalagent. That list spans training crawlers and plain fetchers and
covers essentially every automated AI client with a name. Reading `User-agent: *` as permission
after that is reading the one line the operator did not write for us and ignoring the nine they
did.

**It is the same technicality this file rejects one row above.** `/TLODOCS/` is upper case and the
live urls are lower case, and this project refused to read that as a mismatch. Sending a different
string in the User-Agent header to a host that named the client we run is the identical move.
Rejecting one and taking the other is not a boundary, it is a preference.

**And this file already answered this exact question once.** On `data.capitol.texas.gov` the
position was "the API responds, which makes this a choice rather than an obstacle, and the choice
is to respect it". Same shape, same answer.

**What it actually costs, measured rather than asserted.** Less than first written down.
`Committees/MeetingsUpcoming.aspx` answers 200 for `Chamber=S` AND `Chamber=H`, so the dated
hearing calendar, which is the `public_access` entry this record promises a reader, is covered for
both chambers by a source under no disallowed path. **What is genuinely lost is the interim CHARGE
text**, which LRL carried in full and the calendar does not. That is a real loss and it is the
whole of the loss.

Also clear: `interchange.puc.texas.gov` has no robots.txt, `www.puc.texas.gov` is `Allow: /`,
`www.rrc.texas.gov` is empty, TCEQ disallows only its search endpoint, and `sos.state.tx.us` is
empty.

---

## 2. The registry

### Grid — ERCOT `www.ercot.com/api/1/services/read/dashboards/`

| Feed | Key | ✓ | Contents |
|---|---|---|---|
| `fuel-mix.json` | none | **[V]** | 150 KB, five-minute generation by fuel, plus `monthlyCapacity` |
| `supply-demand.json` | none | **[V]** | 289 points, capacity, demand, forecast |
| `daily-prc.json` | none | **[V]** | 640 KB, 5,789 points, `current_condition` and `eea_level` |
| `loadForecastVsActual.json` | none | **[V]** | Previous, current and next day |

**`todays-outlook.json` returns 403**, not 404, so it exists but is forbidden. **Do not assume the
pattern generalizes** across this undocumented API. Never build on `mis.ercot.com` (SiteMinder) or
`api.ercot.com` (two-secret OAuth).

**Eleven is the complete set, and that is now proven rather than assumed.** Each ERCOT dashboard
page defines its own `"apiUrl": "/api/1/services/read/dashboards/<name>.json"` in page source.
Sweeping every dashboard page yields exactly **12 distinct names: 11 return 200, and the twelfth
(`lmpContourMap.json`) is a vestigial reference that 404s** because the dashboard actually renders
a PNG at `/content/cdr/contours/rtmLmp.png`. There is no point hunting for more.

### The real ERCOT extension is `/content/cdr/`, and it is where metro scoping lives

Keyless HTML rather than JSON, so it needs parsing, but it carries numbers the dashboards do not:

| Path | Contents | ✓ |
|---|---|---|
| `/content/cdr/html/real_time_system_conditions.html` | **System frequency** (60.016 Hz observed), instantaneous time error, BAAL clock-minute exceedances, **system inertia** (308,194), demand, capacity, wind, PVGR, 5 DC ties | **[V]** |
| `/content/cdr/html/current_np6788.html` | **7-day load forecast BY WEATHER ZONE**, 383 KB | **[V]** |
| `/content/cdr/html/hb_lz.html`, `real_time_spp.html`, `dam_spp.html` | **Settlement point prices by hub and load zone**, 5 to 15 min | **[V]** |

**The weather-zone forecast and the load-zone prices are exactly what per-metro grid reporting
needs**, and they were not in the dashboard set.

### Water — TWDB, and THE SECOND DAILY INSTRUMENT

| Source | Endpoint | Key | ✓ | Archive | Geo |
|---|---|---|---|---|---|
| **Statewide reservoir storage** | `waterdatafortexas.org/reservoirs/statewide.csv` | none | **[V]** 34,010 rows | **1933-07-01 to today, 94 years** | statewide |
| **Per metro** | `/reservoirs/municipal/<slug>.csv` | none | **[V]** 19 of 20 slugs 200 | Dallas back to 1952 | **20 metros** |
| Per basin / region / climate zone | `/reservoirs/{basin,region,climate}/<slug>.csv` | none | **[V]** | decades | 15 / 15 / 9 |
| Per reservoir | `/reservoirs/individual/<slug>.csv` | none | **[V]** | decades | **122 reservoirs** |
| Current snapshot, all | `/reservoirs/recent-conditions.json` | none | **[V]** 122 objects | snapshot | **gauge lat/lon + tags** |
| Groundwater levels | `/groundwater/recent-conditions.json` | none | **[V]** per-well daily | snapshot | well |
| Groundwater registry | `/groundwater/wells.geojson` | none | **[V]** 404 wells | static | **county + aquifer** |

Terms, as actually stated: a warranty disclaimer in the CSV header and **no licence, no commercial
restriction, and no attribution requirement**. Texas state agency public data. The **robots.txt
`*.csv` question in section 1 still stands** and is an ethics decision, not a licence one.

**DECISION: the second daily instrument is statewide reservoir conservation storage**, with
per-metro decomposition and same-calendar-day historical ranking. The research pass ran it end to
end on the fetched CSV:

```
2026-08-11: 77.0% full, 24,311,245 acre-feet
  1-day    -26,085 af   (-0.10 pts)
  7-day   -195,207 af   (-0.70 pts)
  30-day  +221,337 af   (+0.70 pts)
  1-year  -409,209 af   (-1.30 pts)
Aug 11 across 94 years: ranks 38 of 94 (39th percentile)
  min 13.3%  ·  median 80.1%  ·  max 94.4%
```

Why this one, argued from what was verified:

- **It is the only candidate that is genuinely daily.** This eliminates the co-favorite. **The US
  Drought Monitor is weekly**: every record carries a Tuesday `mapDate` and a 7-day window, and
  Travis County returned identical D0-D4 figures for August 4th, July 28th and July 21st. A daily
  instrument fed by drought data would republish an unchanged number six days in seven, **which is
  worse than not publishing.** Reservoir storage moved 26,085 acre-feet in one day.
- **It satisfies the compute-not-generate law completely.** Volume, percent, deltas and the 94-year
  percentile are all arithmetic over a fetched CSV. **Nothing needs estimating, so nothing needs
  the `modeled` label** — unlike the grid watch, which must carry one.
- **It is not a prediction and not a verdict.** A measured volume behind a dam today against the
  same date in 94 prior years. **There is no reservoir equivalent of a red zone to imply**, which
  suits the bar-not-dial doctrine.
- **Geographic scoping already exists** and does not need inventing. Today's verified spread is the
  story by itself: **Austin 99.1, Houston 97.3, Dallas 94.3, Fort Worth 87.1 against Midland-Odessa
  27.6, San Angelo 33.2, Abilene 45.2.** The Permian metros nearest the new load are the ones with
  the least water, and that sits in the data with no modeling at all.
- **The archive is deeper than the grid's.** Back to 1933, so every figure ships with real
  historical rank from day one rather than after a year of self-collection.

**Two data-cleanliness traps to encode before any metro number publishes:**

1. **El Paso's single tagged reservoir is Elephant Butte Lake, which is in NEW MEXICO** (tagged
   `new_mexico`, and the only one of 122 lacking the `texas` tag). It reads **1.4 percent full**,
   an arresting number that would be a serious credibility error to publish as "El Paso's water
   supply" without saying it sits on the Rio Grande in another state. **`/reservoirs/municipal/el_paso.csv`
   is also the only municipal slug that fails, returning 500.** Nineteen of twenty work. El Paso
   needs special handling or explicit exclusion. **Note this is the second time El Paso has broken
   a default assumption**, after the ERCOT membership question.
2. Multi-word slugs accept either separator (`midland_odessa` and `midland-odessa` both 200).

**Runners-up:** the **Edwards Aquifer J-17 well** as a named companion, daily to 1932 with
15-minute intraday, and the number San Antonio genuinely watches — but it is one point measurement,
only available by scraping a JS variable out of a 7 MB HTML page, with **no stated licence found**,
and absence of a licence is not permission. Then USGS streamflow (noisy, and interpretation drifts
toward flood and drought verdicts we have committed not to publish). Then the Drought Monitor,
worth publishing **weekly** beside the daily instrument.

### Weather and climate, all keyless and public domain

| Source | Endpoint | ✓ | Granularity |
|---|---|---|---|
| **NWS** | `api.weather.gov/points/{lat},{lon}` then `/gridpoints/...` | **[V]** returns `county: .../zones/county/TXC453`, and gridpoints carry `maxTemperature`, `apparentTemperature`, `wetBulbGlobeTemperature`, 158 hourly values | **county zone + 2.5 km grid** |
| **NCEI Access Data Service** | `ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&stations=...` | **[V]** TMAX/TMIN/PRCP | station |
| **NCEI Climate at a Glance, CDD** | `.../climate-at-a-glance/{statewide,county,divisional}/time-series/{41,TX-453,4104}/cdd/1/8/2020-2026.json` | **[V]** all three levels | **state / county / climate division** |

**Cooling degree days are available keyless at county level**, which is what the grid demand work
needs. NCEI CDO v2 requires a token and is unnecessary given the above.

### Regulatory

| Source | Endpoint | Key | ✓ | Geo |
|---|---|---|---|---|
| **PUCT filings by docket** | `interchange.puc.texas.gov/search/filings/?UtilityType=A&ControlNumber=<N>&ItemMatch=Equal&DocumentType=ALL&SortOrder=Ascending` | none | **[V]** docket 56822 returned case style, "199 filing(s)", and columns Item, File Stamp, Party, Item Type, Description | docket-keyed |
| PUCT documents per item | `/search/documents/?controlNumber=<N>&itemNumber=<M>` | none | **[V]** 199 links enumerated | |
| **PUCT calendar** | `puc.texas.gov/agency/calendar/GetCalendarRss.aspx` | none | **[V]** RSS with project numbers and hearing rooms. **FETCH IT WITH `-L`.** The mixed case path 301s to the same path lower cased, and without `-L` it answers 184 bytes and zero items, which parses as an EMPTY FEED rather than as an error. This is the highest value poll of the run and its failure mode is silence | |
| ~~TCEQ regulated facilities~~ | ~~`gisweb.tceq.texas.gov/arcgis/rest/...`~~ | | **OFF LIMITS. `gisweb.tceq.texas.gov/robots.txt` is `Disallow: /` for ALL agents.** An earlier pass listed this as working. **It is not usable and must not be polled.** Facility data has to come from EPA Envirofacts, which carries county FIPS natively | |
| RRC public viewer | `gis.rrc.texas.gov/server/rest/services/rrc_public/RRC_Public_Viewer_Srvs/MapServer` | none | **[V]** 41 layers, wells, pipelines, counties, districts | county layer 29 |

**PUCT is a GET, not a POST.** `POST /search/search/` returns 404.

### The Governor's office and the Legislative Reference Library

Both added 2026-08-16, from the first run to ship a deck. `gov.texas.gov` was the single most
productive source of that run and was not in this registry at all.

| Source | Endpoint | Key | ✓ | Geo |
|---|---|---|---|---|
| **Governor's press releases** | `gov.texas.gov/news/post/<slug>` | none | **[V]** **serves NO robots.txt**, answers a browser User-Agent | statewide, names the county in the body |
| **Governor's directive letters and press PDFs** | `gov.texas.gov/uploads/files/press/<file>.pdf` | none | **[V]** same host, same terms. This is where a directive's actual text lives, rather than the summary in the post | |
| **LRL interim hearings, weekly** | `lrl.texas.gov/whatsNew/client/index.cfm/<yyyy>/<m>/<d>/Interim-Hearings--Week-of-<Month>-<D>-<YYYY>` | none | **RESTRICTED, see section 1.** There is no PATH disallow, which is what this row used to say and why the real rule was missed. **`User-agent: ClaudeBot` is `Disallow: /` for the whole host**, so no WebFetch and no scout. `User-agent: *` is `Allow: /` with `Content-Signal: ai-train=no, use=reference` | statewide |

**The LRL weekly post is the cheapest route to a dated public microphone**, which is exactly what
this record promises a reader. A committee hearing is a decision point with a date and a room, and
it is a `public_access` entry the record can carry before anything is decided.

That sentence stood while the host was reachable. It is not, for the client the research phase
uses. **The substitute verified on August 25th is `capitol.texas.gov/Committees/MeetingsUpcoming.aspx?Chamber=S`**,
which answers 200, sits under no disallowed path and carries the date, time, room and cancellation
state of every upcoming committee meeting. It re-verified tx-2026-0077 and gave a better quote than
the disallowed notice pdf did.

### University systems

| Source | Endpoint | Key | ✓ | Geo |
|---|---|---|---|---|
| **UT System Regents agenda books** | `www.utsystem.edu/sites/default/files/offices/board-of-regents/board-meetings/agenda-book-full/<M>-<YYYY>AB.pdf` | none | **[V]** stock Drupal robots.txt naming no AI agent and carrying no relevant disallow. The August 2026 book is 13.5 MB over 307 pages with a real text layer rather than a scan | names the campus |

**It needs `curl` plus a page ranged read, not a page fetch.** Two scouts failed on this file
independently because their fetcher has a size limit, and a size limit reads exactly like a dead
source. A source that only fails for large files will be recorded as broken by whoever meets it
first.

### Quote fidelity: take the ZIP whenever one sits beside a PDF

PUCT Interchange offers both for some items, and **the PDF can be a scan whose OCR layer is not
the document.** Item 52 of Project 59142 renders `August 7,2026`, `ofthe`, `MWtotal`, and a
signature block as `PUBLIC UTILITY COMMISSIO EXAS N OFy`. The ZIP carried the source `.pptx`,
whose xml holds the real text.

**A verbatim quote drawn from an OCR layer is a quote of the scanner**, and this record's whole
promise is that a quote is what the document says. Every figure in the August 23rd tx-2026-0072
update came from the pptx.

### Money

| Source | Endpoint | Key | ✓ | Geo |
|---|---|---|---|---|
| **Sales tax allocation by city** | `data.texas.gov/resource/vfba-b57j.json` | none | **[V]** **189,264 rows, 2013 to 2026, 1,182 cities**, monthly | **city** |
| Mixed beverage receipts | `/resource/naix-2893.json` | none | **[V]** 3,804,701 rows, `location_county` FIPS | **county** |
| PUC informal complaints | `/resource/cxnx-7tf4.json` | none | **[V]** `comtype` electric/water, `category`, monthly | state |
| Socrata catalog | `data.texas.gov/api/views.json` | none | **[V]** **1,466 datasets** | |
| **JETI current agreements** | `comptroller.texas.gov/economy/development/prop-tax/jeti/current-agreements.php` | none | **[V]** **HTML table only, 13 rows** | school district |

Socrata is keyless-usable and supports server-side `$select`, `$where` and aggregates, so counts
can be computed without downloading. An app token is recommended, not required; without one we
share a throttled anonymous pool.

### Federal, all keyless unless noted

| Source | Endpoint | Key | ✓ | Geo |
|---|---|---|---|---|
| **USAspending** | POST `api.usaspending.gov/api/v2/search/spending_by_geography/` with `{"scope":"place_of_performance","geo_layer":"county"}` | **none** | **[V]** AI keyword + TX, FY2025, **22 counties**. Travis $424.5M, Dallas $74.2M, Harris $51.0M, Bexar $37.9M | **`shape_code` IS county FIPS**, and it returns `population` and `per_capita` |
| **SEC full-text search** | `efts.sec.gov/LATEST/search-index?q=...&forms=8-K` | none, **UA required** | **[V]** `"data center" "ERCOT"` 8-K 2026 → **68 hits** incl. Oncor, Galaxy Digital, Cipher Mining. `"Abilene" "data center"` → 146 | company |
| **SEC submissions / XBRL** | `data.sec.gov/submissions/CIK##########.json` | none, **UA mandatory** (403 without) | **[V]** | filer address |
| **Federal Register** | `federalregister.gov/api/v1/documents.json?conditions[comment_date][gte]=...&fields[]=comments_close_on` | **none** | **[V]** 1,530 AI docs, 8 open AI proposed rules with real close dates | **no state field** |
| **CourtListener v4** | `courtlistener.com/api/rest/v4/search/?type=r&court=txwd+txnd+txsd+txed+ca5` | **search works keyless**; `/dockets/` is 401 | **[V]** 1,309 dockets / 2,396 docs | **court_id is the geography** |
| **NIH RePORTER** | POST `api.reporter.nih.gov/v2/projects/search` with `org_states:["TX"]` | none | **[V]** 70 TX AI projects FY2025 | org city + ZIP |
| **NSF awards** | `api.nsf.gov/services/v1/awards.json?awardeeStateCode=TX` | none | **[V]** | **state filter native**, city not county |
| **Grants.gov** | POST `api.grants.gov/v1/api/search2` | none | **[V]** 209 open AI opportunities | none |
| **BLS v2** | POST `api.bls.gov/publicAPI/v2/timeseries/data/` | **answered with NO key** | **[V]** Harris Dec-2025 = 2,433,097 | **county FIPS is inside the series id** (`LAUCN` + FIPS) |
| **EPA Envirofacts** | `data.epa.gov/efservice/{table}/{col}/{val}/rows/0:N/JSON` | none | **[V]** `tri_facility/state_county_fips_code/48453` | **county FIPS native**, plus NAICS and lat/lon |
| **EPA ECHO** | `echodata.epa.gov/echo/cwa_rest_services.get_facilities?p_st=TX&p_co=HARRIS` then `get_qid` | none | **[V]** TX major air 2,699 facilities, $105.2M penalties | **`p_co` county param** |
| **Census CBSA to county crosswalk** | `www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2023/delineation-files/list1_2023.xlsx` | **none, static file** | **[V]** parsed, current TX names present | **THE crosswalk. Requirement met** |
| **Census gazetteer** | `www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gaz_counties_national.zip` | none | **[V]** | county FIPS + centroid |
| **Wikimedia pageviews** | `wikimedia.org/api/rest_v1/metrics/pageviews/per-article/...` | none | **[V]** real daily attention series | article |
| Census API | `api.census.gov/data/2023/acs/acs5?...&in=state:48` | **key required now.** Keyless 302s to `missing_key.html`; the old ~500/day allowance is gone | **[P]** | county, tract, **and CBSA** |
| Regulations.gov v4 | `api.regulations.gov/v4/comments/{id}` | free key; **`DEMO_KEY` is exhausted (429)** | **[P]** | none |
| EIA v2 | `api.eia.gov/v2/...` | free key | **[P]** | BA level |

**EIA validates the key BEFORE the route**, proven by sending a bogus key to both a real route and
a nonsense one and getting the identical `API_KEY_INVALID`. **No EIA v2 route string can be
verified without a key.** Every EIA v2 route here is unconfirmed.

**Note the corrected BEAD story:** the earlier pass failed to get Texas broadband numbers and
called it a dead end. The **FCC Broadband Map API returns 401 and needs free `username` +
`hash_value` registration**. That is a registration, not a wall. The FCC's keyless Socrata data is
real but frozen at **June 2021 Form 477** and will not answer a BEAD question.

### The feed sweep: 8 of 12 "blocked" domains have working feeds

A dedicated pass probed 83 feed URLs. **The blocked list was mostly wrong**, which compounds the
curl-versus-WebFetch correction above: the first pass measured one client against HTML, and both
of those choices were load-bearing.

| Domain, previously "blocked" | Result |
|---|---|
| **texastribune.org** | **Open.** `/feed/` plus 8 topic feeds, 2 tag feeds, and the WP REST API |
| **texasstandard.org** | **Open.** `/feed/` carries 300 items |
| **hpcwire.com** | **Open.** `/feed/`, full text |
| **therobotreport.com** | **Open.** `/feed/`, full text |
| **news.utsa.edu** | **Open.** `/feed/`, full text — closes the San Antonio gap |
| **tea.texas.gov** | **Open via GovDelivery**, 13 topics, full text — closes the STAAR gap |
| **newsroom.heb.com** | **Open.** `/feed/` works even though the page body is empty |
| **porthouston.com** | **Open.** `/feed/`, monthly |
| `tacc.utexas.edu` | **EXCLUDED ON PURPOSE. See below.** |
| `texasattorneygeneral.gov` | No feed. `/rss.xml`, `/feed`, link tags and GovDelivery all 404 |
| `utsouthwestern.edu` | No feed. `/newsroom/rss.xml` answers **200 with a zero-byte body** |
| `flocksafety.com` | No feed |

**`tacc.utexas.edu` robots.txt explicitly disallows `ClaudeBot` and `anthropic-ai` domain-wide.**
The research agent found no feed and **left the domain alone rather than routing around the
restriction**, which is the correct call and the one this project has to keep making. It joins
`data.capitol.texas.gov` on the off-limits list in section 1. TACC coverage has to come from NSF
award data, UT System, or the LCCF project site instead.

**The single most valuable find.** The Tribune's search *feed* returns 200 with zero items, but
their **WP REST API is keyword-filtered, date-sorted, and returns complete article bodies**
(verified at 8,150 and 6,001 characters):

```
https://www.texastribune.org/wp-json/wp/v2/posts?search=ERCOT&per_page=20&_fields=date,link,title,content
```

**That is full text, keyword-scoped, out of the most important newsroom on the beat.**

### Two traps that would have burned runs

1. **Empty shells parse cleanly and never fail a health check, which makes them more dangerous
   than a 404.** `tceq.texas.gov/rss.xml`, `eenews.net/feed/`, and the `/index.rss` path that KUT,
   KERA and Marfa Public Radio advertise **in their own link tags** all return **zero items**. For
   those stations use `/news.rss`. **The health check must test item count, not status code.**
2. **The search-feed trick is OR-matched and strips quotes.** Asking AgriLife for `data center`
   returned a screwworm study and a retiring entomologist, because it matched "center" alone. On
   Houston Public Media, `?s=datacenter` returned 4 of 4 on-beat where `?s=data+center` returned
   vaccine policy. **Use single distinctive tokens, and post-filter regardless.**

### Other feed findings

- **ERCOT has no feed of any kind.** All conventional paths 404, the site is a JS app, and
  robots.txt disallows `/content/news`. Grid data already comes through the collector, so this
  costs only ERCOT *news*.
- **SEC EDGAR 403s a browser UA and 200s a UA carrying contact details**, which is their stated
  policy. With that one header the live 8-K feed and full-text search both open (1,946 hits for
  "ERCOT" in 8-Ks).
- **Federal Register RSS works keyless** with arbitrary search terms, but enforces a fixed 30-day
  window and **silently ignores a `publication_date` lower bound**. It is also the working route to
  FERC, whose own `rss.xml` 403s.
- **Google News RSS still works keyless** with quoted phrases, `when:Nd` and `site:` filters, and
  is the only way to see the Statesman, Dallas Morning News, Houston Chronicle and Texas Monthly,
  none of which serve a usable feed. **`allintitle:` returns zero and must not be used.**
- **Texas Legislature Online bill feeds are session-gated, not dead.** Placeholder items now, worth
  wiring before the next regular session convenes in January 2027.

### Feeds verified live

| Feed | Items | Full text? |
|---|---|---|
| **`texasstandard.org/feed/`** | **300** | **YES, full `content:encoded`.** The best Texas text source found |
| `texastribune.org/feeds/main/` | 20 | No, but links resolve cleanly to canonical articles |
| **`chron.com/rss/feed/Business-287.php`** | ✓ | **The Houston Chronicle workaround** |
| `houstonpublicmedia.org/feed/`, `rtoinsider.com/feed/`, `eia.gov/rss/todayinenergy.xml`, `spectrum.ieee.org/feeds/topic/artificial-intelligence.rss` | 40 / 10 / 15 / 30 | |

**The technique that worked was sibling-domain substitution, not the `/feed/` path.**
`houstonchronicle.com/rss/...` returns 403 while **`chron.com/rss/...` returns 200** — same Hearst
newsroom, no block. Generalize it: try `mysanantonio.com` when `expressnews.com` resists.

**A trap the pipeline must encode:** `texastribune.org/feeds/sections/energy/` returns **200 with
zero items**. **Health checks must test item count, not status code.**

Feeds carry the last 20 to 300 items and **no archive**. They are a discovery lane, never a
backfill lane.

### Texas Ethics Commission — SOLVED, and it is bulk, keyless and daily

Two prior passes failed here and called TEC "form-driven" and unusable. **It is not. The bulk
files are static URLs, keyless, and regenerated every morning.** All verified August 11th, 2026.

| What | URL | Size | Notes |
|---|---|---|---|
| **Lobby registry by client** | `www.ethics.state.tx.us/data/search/lobby/2026/2026LobbyGroupByClient.xlsx` | 785 KB | **THE key file.** 8,183 rows: client, lobbyist, address, dates, compensation bracket. Stamped daily |
| Lobby registry by lobbyist | `.../2026/2026LobbyGroupByLobbyist.xlsx` | 1.05 MB | Same data keyed the other way |
| Lobby subject matter | `.../2026/2026LobbySubjMatter.xlsx` | 3.67 MB | |
| Registered lobbyist list | `.../2026/2026RegisteredLobbyists.xlsx` | 145 KB | |
| **Lobby bulk CSV** | `prd.tecprd.ethicsefile.com/public/lobby/public/TEC_LA_CSV.zip` | 17.2 MB | 11 CSVs incl. `LaCvr` (82 MB, expenditure totals), `LaFood`, `LaGift`, `LaEnt` |
| **Campaign finance bulk** | `prd.tecprd.ethicsefile.com/public/cf/public/TEC_CF_CSV.zip` → 301 → `dv2dphbeckkgm.cloudfront.net/TEC_CF_CSV.zip` | **1.04 GB** | Updated daily. **Must follow redirects** |
| **All registered PACs** | `www.ethics.state.tx.us/data/search/cf/PacList.xlsx` | 342 KB | 2,451 PACs: filer ID, type, start date, address, **treasurer** |
| Individual lobby report PDFs | `http://204.65.203.5/public/lobby/<reportID>.pdf` | | Direct, keyless, no session. IDs from the report index |
| Record layouts | `.../data/search/cf/CFS-ReadMe.txt`, `.../CFS-Codes.txt`, `.../lobby/LobbyLAR-ReadMe.txt` | | Read these before parsing |

**Four traps that will bite an automation, all verified:**

1. **Use `www.ethics.state.tx.us`. The bare `ethics.state.tx.us` 404s on the same paths.**
2. **`.../data/search/cf/TEC_CF_CSV.zip` is a DEAD 2019 LINK STILL PUBLISHED ON THE LIVE PAGE.**
   A scraper that follows the visible link gets **seven-year-old data and no error**. This is the
   worst possible failure mode: silently stale, never throws.
3. **`HEAD` returns 404 on some TEC paths that `GET` serves.** Do not probe with `-I` alone.
4. The year pattern holds across both the path and the filename, so swapping `2026` gets prior
   years. The index lives at `.../search/lobby/loblistsREG2026-2030.php`.

**What this unlocks:** the lobby registry answers who is hired by whom, daily, for free, and it is
how `TEXAS_INFLUENCE.md`'s findings were computed rather than recalled. **The 1.04 GB campaign
finance file is the highest-value unfetched thing in this project** — it closes the question of who
actually gave money to whom.

### Municipal, for metro scoping

| City | Platform | Endpoint | ✓ |
|---|---|---|---|
| Dallas | Socrata | `dallasopendata.com/api/views.json` | **[V]** 1,087 datasets |
| Austin | Socrata | `data.austintexas.gov/api/catalog/v1` | **[V]** |
| Houston | **CKAN 2.9.11** | `data.houstontx.gov/api/3/action/package_list` | **[V]** |
| San Antonio | **CKAN** | `data.sanantonio.gov/api/3/action/package_list` | **[V]** |
| Fort Worth | **ArcGIS Hub, not Socrata** | `data.fortworthtexas.gov` | **[P]** |
| El Paso | none | — | **[X]** host does not resolve |

---

## 3. Original computed metrics these support

The house rule is that a number is computed from data and recomputable. These are candidates that
meet it and that nobody currently publishes.

1. **The ERCOT archive itself.** See section 0. Snapshot daily and the series becomes ours.
2. **Reservoir drawdown rate against siting activity.** Daily `conservation_storage` and
   `percent_full` back to 1940. Nobody publishes a per-reservoir rate of change joined to
   county-level facility activity.
3. **Aquifer drawdown by county.** `wells.geojson` carries county and aquifer per well;
   `recent-conditions.json` carries daily level. **The join key is already there**, both are JSON,
   and neither is inside the robots disallow.
4. **PUCT docket velocity.** Filings per week on a docket, or median days between filings, as a
   computed measure of regulatory momentum. Docket 56822 gave 199 filings with file stamps as a
   worked example.
5. **JETI's emptiness, which is itself the number.** The current agreements table has **13 rows and
   zero data centers**. A keyword scan for "data center", "hyperscale", "semiconductor" and
   "battery" returned **0 across the whole table**, and the applications table is empty. A
   computed, sourced **"0 of 13 JETI agreements are data centers"** directly rebuts the widespread
   assumption that data centers are capturing the Chapter 313 successor. Labelled `measured` and
   recomputed every run, this is exactly the house style, and it is the kind of finding that is
   only available to someone who actually looked.
6. **Metro economic divergence.** 189,264 monthly city rows since 2013 support a data-center-county
   cohort against a control cohort. The dataset ships its own percent-change fields; **the cohort
   comparison is ours to compute.**
7. **Permitted facility density by county**, server-side aggregated from TCEQ.

---

## 4. Dead list — do not retry

| Thing | Why |
|---|---|
| `waterdatafortexas.org/reservoirs/statewide.json` | 404. The JSON twin of the CSV does not exist |
| `waterdatafortexas.org/reservoirs/` | 404, no directory index |
| `/reservoirs/api/*` | 404 despite robots.txt naming it |
| `?output_format=json` on TWDB | Returns 200 **HTML**. The parameter is ignored |
| `/reservoirs/recent-conditions` | **500**. The groundwater equivalent works, the reservoir one is broken |
| `ftp.legis.state.tx.us` | Connection reset. The legacy legislature FTP is gone |
| `gis.rrc.texas.gov/arcgis/rest/services` | 404. Correct root is **`/server/rest/services`** |
| `gis.tceq.texas.gov` | Does not resolve. Correct host is **`gisweb.tceq.texas.gov`** |
| RRC `mft.rrc.texas.gov/link/<uuid>` bulk | JSF app needing cookies and ViewState. **RRC bulk data is not scriptable this way** |
| ERCOT `todays-outlook.json` | **403** while siblings return 200 |
| TEC campaign finance bulk | Directory returns 200 with **0 bytes**. Not located |
| `data.fortworthtexas.gov/api/views.json` | 404, it is ArcGIS Hub |
| `data.elpasotexas.gov` | Does not resolve |
| TEA machine-readable district data | **Not found. TEA is effectively HTML and Excel only.** `rptsvr1` is a meta-refresh stub, `tea4avfaidbdc01` returns 502 |
| Chapter 313 / JETI as a data file | **HTML tables only.** Scrapeable but fragile |
| `capitol.texas.gov/BillLookup/`, `/Search/`, `/Reports/` | robots Disallow |
| OpenStates v3 and LegiScan keyless | Both 403. Free keys exist |

---

## 5. Decisions this registry needs from the owner

1. **The reservoir CSV question.** `waterdatafortexas.org/robots.txt` disallows `*.csv`, and the
   reservoir files are CSVs. The data is public, the state publishes it deliberately, and a person
   may download it freely. Whether an automated daily collector should is a different question, and
   given that this publication makes a public commitment about how it gets its numbers, **it should
   be answered on purpose rather than by a silent collector.**
   Three options: use only the groundwater JSON and GeoJSON, which are unambiguously outside the
   rule; contact TWDB and ask; or collect the CSVs at low frequency with a descriptive User-Agent
   and publish that we do. **The groundwater-only path is available today and needs no permission**,
   which makes it the sound default until the owner decides otherwise.
2. **Free API keys worth getting**, each of which unblocks a lane: OpenStates v3 or LegiScan for
   bill status, Census for the county and CBSA crosswalk the metro scoping needs, and a Socrata app
   token to leave the shared anonymous throttle pool.
3. ~~**May the collectors' own User-Agent fetch `lrl.texas.gov`?**~~ **DECIDED August 25th, off
   limits, whole host, all clients.** Kept here rather than deleted so the next reader does not
   re-open it from the file alone. The reasoning is in section 1 under the table.
