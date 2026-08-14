# Texas endpoints: what this project may poll, what it may not, and what lies

Swept 2026-08-14 across Texas state agencies, the energy and water instruments, and the federal
surfaces that carry Texas decisions. Every status here was fetched, not assumed. Every `robots`
line is quoted from the file on the host that would actually be hit.

**Read this before wiring anything that runs on a schedule.** Half of what follows is a list of
things that return a clean 200 and are still off limits.

---

## The rule this sweep exists to enforce

**Working and permitted are different questions, and only one of them is visible in the
response.** `api.weather.gov/alerts/active?area=TX` returns 200 with real Texas advisories and
its host answers every crawler with `Disallow: /`. It was in `TEXAS_TELEMETRY.md` as a viable
candidate, listed by status code, for as long as that file existed.

Three corollaries, each of which cost something here:

1. **Check the robots file of the host you are about to hit, not the host you are reading.** The
   Texas Ethics Commission's lobby search is open and links a bulk zip on a different host that
   disallows the exact path the link points at.
2. **A 500 is a day, not a property.** `waterdatafortexas.org/reservoirs/recent-conditions.json`
   was recorded here as a 500 and is a 200. Re-check a dead endpoint before designing around its
   death.
3. **A knowledge file's instruction is a standing order.** This repo carried an instruction to
   recompute the ERCOT demand record from the MIS archive, and the MIS is disallowed. Nobody
   crawled it, but only because nobody got to it.

---

## Wire these first

| # | What it detects | Endpoint | Key | Cadence |
|---|---|---|---|---|
| 1 | A federal rule with an open comment window | `federalregister.gov/api/v1/documents.json` | none | daily |
| 2 | A Texas rule, permit notice or AG opinion request | Texas Register weekly issue | none | weekly, Friday |
| 3 | ERCOT declaring a grid condition or an EEA | `ercot.com/api/1/services/read/dashboards/daily-prc.json` | none | 10 s |
| 4 | A company disclosing a Texas campus | `efts.sec.gov/LATEST/search-index` | none | continuous |
| 5 | A Texas agency publishing a dataset | `api.us.socrata.com/api/catalog/v1?domains=data.texas.gov` | none | daily |

### 1. Federal Register API

The cleanest decision detector in the sweep, and the clearest signal of publisher intent
anywhere in it: **the same publisher disallows its own HTML search and leaves the API open.**
`robots.txt` blocks `/documents/search`, `/articles/search`, `/regulations/search` and carries
no line matching `/api`.

Every record is already a docket item without interpretation. A named agency, a dated document,
a comment deadline. Keyless, full archive, and `fields[]` trims a heavy default payload.

Two traps. `conditions[comment_date][is]=open` returns **400**; the working form is
`conditions[comment_date][gte]=<today>` with the date computed in code. And the API echoes its
own filter back in a `description` string, which is a free self-test assertion a collector
should use rather than hand-write.

### 2. The Texas Register

Statutory, weekly since 1976, and on a host whose `robots.txt` is **empty**. It is the only
Texas source carrying PUC, TCEQ, TEA and Attorney General activity in one place, which matters
enormously because three of those four are otherwise unreachable (see below).

Poll `https://www.sos.state.tx.us/texreg/texreg.xml` for the ping, then **derive** the issue URL
from the date: `/texreg/archive/<MonthDDYYYY>/index.html`, month name capitalised, no
separators, **no leading zero on a single digit day** (`August72026`).

- **Do not follow the feed's own links.** On the day of the sweep the HTML item's link read
  `.../archive/Augsut142026/index.html`. The typo is in the publisher's source and the URL is
  broken.
- **Do not trust the archive index.** It listed three issues as newest while the newer directory
  was already live and returning 200. The index lags publication; the derived URL does not.
- The feed carries no `pubDate` and no `guid`. Dedupe on the channel description, which names
  the issue date.
- Section sub-pages contain **literal spaces** that must be percent encoded:
  `/Proposed%20Rules/16.ECONOMIC%20REGULATION.html`.

**The `In Addition` section is the TCEQ workaround** and it is the only one. It carries notices
of receipt, notices of public meeting and comment deadlines, because TCEQ is required to publish
them there.

On the day of the sweep this one route produced `§25.521 Large Load Demand Management Service`
with "Comments must be filed by September 4, 2026" — a PUC large-load rule with an open window,
found with no PUC endpoint at all.

### 3. ERCOT dashboard feeds

Undocumented, keyless, CORS-restricted to `mis.ercot.com` so they must be fetched server side,
and not matched by any `Disallow` line. Four are in use:

| File | Carries | Window |
|---|---|---|
| `daily-prc.json` | grid condition, EEA level, physical responsive capability | today only |
| `system-wide-demand.json` | hourly load, current and day-ahead forecast, HSL | 3 days |
| `supply-demand.json` | 5-minute committed capacity and demand, 7-day forecast | today + forecast |
| `fuel-mix.json` | generation by fuel, plus monthly installed capacity | 2 days |

**`daily-prc.json` is the one that carries a DECISION.** Everything else is a measurement.
`eea_level` and `condition_note` are ERCOT saying something official on a dated day, which is
quotable rather than derived, and it respects the never-a-verdict rule because the verdict is
ERCOT's.

Traps: `prc_value` arrives as a **string with a thousands comma** while `data[].prc` is an
integer. Power storage generation goes **negative** while charging. Sampling on the PRC feed is
irregular, roughly every 8 to 12 seconds. And the names cannot be guessed, `todays-outlook.json`
is a 403 and `hourly-wind-power-production.json` a 404.

**Every one of these is a rolling window measured in days.** A missed day is permanent. That is
the whole argument for the collector running on its own cron rather than as a routine phase.

### 4. SEC EDGAR full text search

The state facet is the prize. One query returns filings mentioning a Texas data center with a
ready-made bucket count by business state, which is the corporate half of this record arriving
pre-filtered. An 8-K carries legal consequence a press release does not.

Two honest caveats. `efts.sec.gov/LATEST/search-index` is the **undocumented backend** behind
the EDGAR search UI and can move without notice. And SEC enforces a **declared User-Agent with
a contact** and 10 requests per second, at the host level.

### 5. Socrata catalogue for data.texas.gov

Keyless, documented, paginated, with real `updatedAt` timestamps. Diff the top of the list.

**Always pass `domains=data.texas.gov`.** The portal-relative form federates and will quietly
return Los Angeles parking meters mixed in with Texas rows. `order=last_modified` is a 400;
`order=updatedAt` works. A wrong dataset id returns **404 rather than an empty array**, so a
poller must treat 404 as a schema break and never as an absence of news. `Crawl-delay: 1`.

---

## Also useful, with their own traps

- **JETI current agreements** (`comptroller.texas.gov/economy/development/prop-tax/jeti/`). A
  listing rather than a form, which is what makes it pollable, and the closest thing Texas keeps
  to a register of what a large compute project was promised and what it promised back. No CSV,
  no JSON. Pin the parser to the column headers and fail loudly when they move. The **pending
  applications page is broken**: it returns 200 with a client-side table that failed to load and
  a "we experienced a problem" message, so zero rows there must be treated as an outage.
- **TLO committee meeting feeds**, House and Senate. Earliest warning that the Legislature is
  taking up AI or large loads. Read the feed only: item links point into `/tlodocs/` and robots
  says `Disallow: /TLODOCS/`. Path matching is case sensitive so the lowercase path does not
  literally match, and **the publisher's intent is not a technicality**. No `pubDate`; dedupe on
  the link. Out of session the daily feeds return a **sentinel item**, not an empty list, so a
  poller counting items reads 1 and thinks it found news.
- **NCEI daily summaries and 1991-2020 normals.** Keyless, no rate limit, full archive. Already
  behind the front page weather chip. Observed lag is about three days, so never assume the
  requested end date is present. `units=standard` returns Fahrenheit and inches; omitting it
  returns tenths of a degree Celsius, which is a silent unit trap.
- **US Drought Monitor state statistics.** Keyless, weekly, history to 2000. Returns **CSV
  unless an Accept header asks for JSON**. Columns are cumulative and one is literally named
  `None`, which collides with a Python keyword in a naive unpack.
- **EIA-930.** The API is 403 without a free key. The **six-month bulk CSV is keyless** and is
  the better route for backfill, with `opendata/bulk/manifest.txt` as its change detector. EIA
  **soft-404s to its homepage**, so assert on content shape rather than status.
- **USGS legacy `waterservices.usgs.gov`** serves no robots file. A range with no data returns
  success with an empty array, so assert on record count.
- **EPA Envirofacts** (`data.epa.gov/efservice/`) filters to a single Texas county, which is the
  grain this record writes at. Pagination is a path segment, not a query parameter.

---

## Closed. Do not poll these.

| Host | The line, verbatim | What is lost |
|---|---|---|
| `dir.texas.gov` | `User-agent: ClaudeBot` / `Disallow: /` | the HB 2060 AI inventory, the sandbox, contracts |
| `texasattorneygeneral.gov` | `User-agent: ClaudeBot` / `Disallow: /` | AG opinions and enforcement actions |
| `www15.tceq.texas.gov` | `User-agent: *` / `Disallow: /` | the entire permit Central Registry |
| `search.txcourts.gov` | `User-Agent: *` / `Disallow: /` | all appellate case search |
| `api.weather.gov` | `User-agent: *` / `Disallow: /` | every NWS alert |
| `waterdatafortexas.org` | `Disallow: *.csv`, `/reservoirs/api/*` | the reservoir API and every CSV |
| `echodata.epa.gov` | `User-agent: *` / `Disallow: *` | ECHO compliance records |
| `prd.tecprd.ethicsefile.com` | `Disallow: /public/lobby/` | the bulk lobby registration file |
| `ercot.com/misapp`, `/misdownload` | `Disallow:` both | the MIS report archive, incl. the GIS report |

DIR and the AG name **ClaudeBot and anthropic-ai specifically**, under a comment reading
"Block AI and data crawlers". A scheduled unattended poller is a bot whatever user-agent string
it sends. There is no reading of that which permits this project to fetch those sites, and the
partial substitutes are the Texas Register for the AG and `data.texas.gov` for DIR — where a
search for artificial intelligence returns exactly one asset, and it is a meeting video.

**PUCT could not be tested at all.** Thirteen paths across `interchange.puc.texas.gov` and
`www.puc.texas.gov` returned **HTTP 402**. Only the very first request of the session succeeded,
which reads like edge protection engaging rather than a paywall. The Interchange has no
`robots.txt`, so permission is not the obstacle. **This is the largest gap in the register**: it
is where large-load interconnection filings and every PUC docket document land first, and PUC
coverage has to run through the Texas Register until the block is understood.

**No official Texas agency MCP server exists.** The registry returns two entries for "texas" and
neither is governmental. One is a community wrapper around the same Socrata API this project can
call directly, and adopting it would add a third-party dependency in front of a keyless
endpoint. Nothing here is reachable by MCP; everything is HTTP.

---

## Unresolved, and needing a decision rather than a guess

**The USGS contradiction.** `api.waterdata.usgs.gov/robots.txt` says, in a comment, "Our data is
public and you are welcome to scrape it!" and then, in a machine-readable directive, disallows
`/ogcapi/*/collections/*/items*`, which is the only path that returns data. The remedy USGS
names in the same file is a free API key, which suggests the directive targets unkeyed bots
rather than a polite keyed client.

Under the rule as written the directive wins, so this project uses the older
`waterservices.usgs.gov` host, which serves no robots file at all. **That is an uncomfortable
outcome that should be decided deliberately rather than by default**: the discipline routes us
onto a legacy service because the modern one asked nicely in prose and refused in syntax.

**ERCOT's `/gridinfo` and `/services`.** Robots disallows `/content/gridinfo` and
`/content/services`. ERCOT runs Adobe Experience Manager, where `/content/X` is the internal
repository path for the public `/X`. By the letter the public paths are allowed; by intent they
are not. Resolution used here: **poll the dated `/files/docs/` URLs directly** (unambiguously
allowed) and treat the index pages as a human step.
