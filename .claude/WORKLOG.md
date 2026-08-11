# WORKLOG — Texas AI Docket build

READ THIS FIRST. This is the durable plan and progress ledger for a long multi-context
build. It exists because context gets compacted and a plan that lives only in context does
not survive. Resume from the status table. Update it after every commit. Do not delete it
until every wave is DONE and shipped.

Approved plan of record: `/root/.claude/plans/hey-so-we-have-groovy-platypus.md`
Build started 2026-08-11. Branch `claude/texas-ai-docket-setup-vf2a23`.

---

## What we are building

A Texas equivalent of the whole Alaska.Ai product family: a public fact-checked docket of
Texas AI decisions, a website built to be read by people and by LLMs, a daily LinkedIn
carousel, a daily narrated 2.5D video, a daily numeric energy record, and the consulting
wing on top of it.

Source machines total ~79,000 lines across three Alaska repos, which are REFERENCE ONLY.

## Repo topology (three repos, mirroring Alaska's proven split)

| Repo | Owns | Why separate |
|---|---|---|
| `TexasAIDocket` (this one) | site, docket, carousel, grid watch, ask | the product |
| `TexasAIDispatch` | video engine and renders | Alaska's video repo is 3.7 GB; keeping it out means the daily carousel and grid-watch crons never clone video media |
| `TexasAIScanner` | scanner backend, Supabase functions | separate lifecycle, fires on API trigger |

## Owner decisions (do not relitigate)

| | |
|---|---|
| Domain | `talonsturgill.github.io/TexasAIDocket` for now; ONE config key drives every absolute URL so a custom domain is a one-line change |
| Visibility | `TexasAIDocket` must be flipped PUBLIC before Wave 3 ships (Pages + `raw.githubusercontent` image URLs both require it) |
| Mailbox | `docket@alaskaaihq.com` as a `DRAFT_TO` constant. NEVER `me` — the Gmail connector rejects it outright |
| Attribution | NO Claude/Anthropic attribution on any commit or PR, ever |
| Merge policy | Autonomous. Passing runs open a ready (non-draft) PR and merge to `main` in the same run |
| Docket launch | Seeded with real, fact-checked items |
| Video | Full port, no shortcuts, purpose-built Texas art library |
| Commercial | Services page + Bottleneck Scanner + proposal-microsite pattern |
| Narrator | A Texan public-radio persona, auditioned on measured read quality |
| Permissions | `defaultMode: bypassPermissions` (unattended runs wedge on a prompt with no responder) |
| Integrations | Buttondown, Supabase, Cloudflare worker — all wired, each no-ops without its key |

## The two problems this build is really solving

1. **Three automations in one repo.** Each ends in a phase whose job is editing its own
   machine. Prose boundaries are not enough. Solved by `ownership.yaml` + `ownership_check.py`,
   enforced at commit time and in CI, and by making `docs/` a pure deterministic function of
   the ledgers so no run can corrupt the site.
2. **Porting 79k lines without dropping any.** The previous attempt moved files over and
   never wired them up. Solved by `PORT_MANIFEST.tsv` + `port_audit.py`, whose WIRING check
   fails on any script not referenced by a workflow, a routine prompt, or another script.

## Status table

| # | Wave | Status | Notes |
|---|---|---|---|
| 0 | Foundation, ownership guard, port audit | **DONE** | 535 files / 158,683 lines routed, 0 unrouted |
| 1 | Texas identity: research, doctrine, tokens, geodata | TODO | |
| 2 | Docket spine + fact-checked seed items | TODO | 15 unverified research findings resolve here |
| 3 | Website + AI-discoverability layer | TODO | `site_build.py` is the single biggest item |
| 4 | In-browser ask engine | TODO | |
| 5 | Texas Grid Watch (ERCOT) | TODO | **+ a SECOND daily instrument: TWDB reservoir storage.** Decided on measured evidence, see below |
| 6 | Carousel machine | TODO | |
| 7 | Video dispatch + Texas art library | TODO | lands in `TexasAIDispatch` |
| 8 | Commercial wing + scanner | TODO | lands here + `TexasAIScanner` |
| 9 | Wire-up, end-to-end proof, routine handoff | TODO | |
| A | Metro scoping (cuts across waves 2, 3, 4, 5) | TODO | owner directive 2026-08-11 |
| B | Data cleanliness spine: places + entity resolution | **PARTIAL** | see below |

### Wave B progress

DONE: all 254 counties with FIPS and computed area-weighted centroids, the resolver, the
provenance law, and CI reproducibility (`tx-places.json` must rebuild byte-for-byte).

STILL NEEDED, each blocked on a **cited** source, never a guess:
- county to **ERCOT weather zone** (8 zones) and **load zone** (`LZ_HOUSTON`, `LZ_NORTH`,
  `LZ_SOUTH`, `LZ_WEST`) mapping. Needed for per-metro grid reporting.
- which counties are **outside ERCOT** entirely: El Paso is WECC, parts of the Panhandle and
  East Texas are SPP or MISO. Getting this wrong makes a whole region's numbers silently wrong.
- cities with population and county, MSA definitions, physiographic region
- county seats
- the **entity canonicalizer**: stable ids plus aliases for agencies, utilities, companies and
  school districts, so "City of Houston", "Houston" and "COH" collapse to one thing

Census API needs a free key (tested: returns "Missing Key"). Find a keyless route or get a key.

## Owner directive 2026-08-11: Texas is not Alaska in scale

Alaska is effectively one system and a village is a handful of people. Texas is 30M people
across 254 counties, so two things become first-class rather than nice to have.

**Metro scoping.** A reader in Houston must be able to zero in on Houston without reading
about the Panhandle. Every docket item, article and grid reading carries a canonical region.
Per-metro landing pages (Houston, Austin, DFW, San Antonio, El Paso, Permian, Rio Grande
Valley) double as a major local-SEO surface Alaska never had a reason to build.

The grid half of this is nearly free: ERCOT already publishes per-metro natively. Load zones
`LZ_HOUSTON`, `LZ_NORTH` (DFW), `LZ_SOUTH` (San Antonio and Corpus), `LZ_WEST` (Permian),
and `weather-forecast.json` carries per-city forecasts for DFW, Austin, San Antonio and
Houston. Both are already in the feeds Wave 5 pulls.

**Data cleanliness has to be a gate, not a convention.** At Texas volume, entity drift is the
failure that quietly destroys the record: "City of Houston", "Houston" and "COH" becoming
three entities breaks every count, every facet and every per-metro filter at once. So:
`assets/geo/tx-places.json` (254 counties with FIPS, major cities with lat/lon, MSA
definitions, ERCOT load-zone and weather-zone mapping, physiographic region) plus
`scripts/shared/places.py` to resolve any location string to it, and an entity canonicalizer
with stable ids and alias lists. Validated with `--self-test`: every docket item location must
resolve, every entity must canonicalize, no orphan aliases.

## Decided 2026-08-11: the second daily instrument is reservoir storage

Statewide conservation storage from TWDB, with per-metro decomposition and same-calendar-day
historical ranking. Full argument and the worked computation in
`knowledge/shared/SOURCES_REGISTRY.md`. The short version:

- **It is the only genuinely daily candidate.** The Drought Monitor, the co-favorite, is weekly:
  Travis County returned identical figures for three consecutive pull dates. **A daily instrument
  fed by weekly data republishes an unchanged number six days in seven, which is worse than not
  publishing.** Reservoir storage moved 26,085 acre-feet in one day.
- **It needs no `modeled` label at all.** Volume, deltas and a 94-year percentile are arithmetic
  over a fetched CSV, unlike the grid watch which must carry a modeled component.
- **94 years of daily history (from 1933)**, so it ships with real historical rank on day one
  rather than after a year of self-collection.
- **The metro spread is the story with no modeling:** Austin 99.1, Houston 97.3, Dallas 94.3
  against **Midland-Odessa 27.6, San Angelo 33.2, Abilene 45.2**. The Permian metros nearest the
  new load have the least water.

**Two traps to encode before any metro number publishes.** El Paso's only tagged reservoir is
**Elephant Butte Lake, which is in New Mexico** and reads 1.4 percent full; publishing that as
"El Paso's water supply" would be a serious credibility error. Its municipal CSV is also the only
one of twenty that 500s. **That is the second time El Paso has broken a default assumption**, after
the ERCOT membership question, which is a pattern worth generalizing into the places test suite.

## Blocked on the owner

- [ ] Register domains (`texasaihq.com`, `texasaidocket.com`, `.org` all verified unregistered 2026-08-11)
- [ ] Create the `TexasAIDispatch` repo (public)
- [ ] Flip `TexasAIDocket` to public (before Wave 3 ships)
- [ ] Create routine triggers at claude.ai/code/routines once prompts land (Waves 6, 7, 8)
- [ ] Keys when we reach them: Buttondown, Supabase project, Cloudflare Worker + KV + Turnstile

## Owner directive 2026-08-11: editorial scope is wider than the docket

The carousel and the video cover **Texas AI companies doing real work** and **AI applications
making an impact in the state, in the cities and outside them**. Not only government decisions.

This creates a real schema question to settle in Wave 2, and it should be settled deliberately
rather than by accident:

- A **docket item** is a decision. It has a decider, dates, a public-access status, and a
  formal way in. That is what gives the docket its integrity, and diluting it would cost the
  thing that makes it citable.
- A **company or deployment** is an entity doing something. A hospital system rolling out
  ambient AI, a school district's grading engine, a ranch running herd analytics, an oilfield
  service company shipping a drilling optimizer. These often have no decider and no deadline.

Provisional resolution, to confirm when the schema is built: keep `ledger/docket.json`
decision-centric, and add a separate `ledger/deployments.json` with its own schema for
companies and applications. A deployment that becomes a public decision (a district adopting a
policy, a county approving a permit) gets a docket item that **references** the deployment
record, so the two link without merging.

**CONFIRMED by the companies research, 2026-08-11**, and it added a required field. Almost
everything published about AI companies is an announcement wearing the clothes of a deployment,
so `deployments.json` carries a **`maturity` enum**: `announced`, `piloted`, `deployed`,
`verified_by_third_party`. Two findings forced this:

- MD Anderson's data science institute states on its own page that its AI work is in pilots and
  not deployed patient care. A publication reporting "MD Anderson uses AI to predict surgical
  complications" would have misrepresented a source that was being careful with its reader.
- Across the entire research pass, exactly ONE item qualified as `verified_by_third_party`
  (Edge Case's independent safety assessment of Aurora, June 25th 2026). That rarity is itself
  reportable, and only a schema that can express it can report it.

No Texas outlet tags this. It costs one enum field and it is the cheapest credibility this
product can buy. See `knowledge/shared/TEXAS_AI_COMPANIES.md` section 1.

The rural half matters and is under-covered by everyone: agriculture and ranching, oilfield
operations, rural hospitals and clinics, small school districts, water districts, and
precision farming. City coverage will find itself; rural coverage has to be sought.

## Hard-won facts (do not rediscover)

- The Alaska PIL/Taichi video engine is RETIRED, explicitly, at `dispatch_routine.md:530`.
  The live renderer is Remotion 4.0.399 + React 19 + hand-authored SVG. Do not port the old one.
- `alaska-ai-weekly/prompts/routine_instructions.md` is a stale legacy prompt, NOT the
  Facebook routine. Its CLAUDE.md says otherwise and is wrong.
- Merging the two Alaska repos collides on five surfaces: both ship `gmail_draft.py`, both
  ship `caption_check.py`, both ship `scorer.md` and `flow-critic.md` agents, both use
  `config/brand.yaml`, and `docs/` means "published site" in one and "craft doctrine" in the
  other. Hence the namespaced layout.
- ERCOT publishes an undocumented, keyless, CORS-open, robots-permitted dashboard JSON API at
  `/api/1/services/read/dashboards/`. Verified 11 endpoints returning 200 on 2026-08-11.
  `system-wide-demand.json` carries measured `systemLoad` AND ERCOT's own forecast in the same
  record, so unlike Cook Inlet we do not have to fit a demand model to get the measured/modeled
  pair. NEVER build on `mis.ercot.com` (SiteMinder-gated) or `api.ercot.com` (two-secret OAuth).
- Alaska's ledger memory must NOT be copied. It would poison the Texas dedupe and divergence
  gates, which compare against recent history.
- Git identity in this repo is `Talon Sturgill <Talon.sturgill@gmail.com>`. The container
  default is `Claude <noreply@anthropic.com>` and must be overridden in every fresh clone.
- Config divergence from the ported original is declared in `config/parity_map.yaml`, never by
  deleting a row from `REFERENCE_CONFIGS` in `port_audit.py`. Three dispositions: `renamed`
  (the named Texas key must EXIST, checked), `dropped` (reason required), `deferred` (reason
  plus `blocked_on` required, and it prints on every audit run). A map entry for a key that is
  present is stale and FAILS, because that is how a strict gate rots into a decorative one.
- **The comma-discipline ceiling is deferred, not forgotten.** It is ten percent below a mean
  measured on a corpus this product has not shipped. Copying the number would publish a figure
  typed by a person from another product's captions and then enforce it as a hard gate against
  copy it was never measured on. Compute it after 20 captions ship, and settle on ONE unit
  while doing it (the source config carries both per-100-words and per-100-characters).
- Many essential Texas sources refuse direct HTML fetches: texastribune.org, texasstandard.org
  and tacc.utexas.edu all 403, and news.utsa.edu and utsouthwestern.edu are JS-only. A blocked
  HTML endpoint is NOT a blocked source; feeds are built to be fetched by machines and are
  often served from the same domains. Resolve via the feed registry, not by giving up.
- `agrilifetoday.tamu.edu` is fetchable including its `?s=` search, publishes dated AI work with
  named researchers every few weeks, and is read by nobody outside agriculture. It is the single
  best rural AI source in Texas and it is how the rural half of the beat gets covered at all.
- **A tool-level failure is NOT a property of a source.** An earlier pass recorded
  texastribune.org as 403 and nearly wrote the best news source in Texas onto a permanent blocked
  list. `curl` fetched the same article at the same moment, **HTTP 200, 292,873 bytes**. Retest
  with a second client before any domain enters a blocked list an automation will inherit.
- **ERCOT's dashboard feeds carry NO archive.** Rolling windows of 1 to 3 days, no date parameter,
  no bulk file. **A day not collected is gone**, which is measured confirmation of the
  cron-not-routine-phase rule rather than an analogy for it. Snapshot daily and within a year we
  own a five-minute ERCOT series that does not otherwise exist for free.
- **11 ERCOT dashboard endpoints is a proven ceiling**, extracted from the pages' own `apiUrl`
  declarations: 12 names exist, 11 return 200, the 12th is vestigial. **The real extension is
  `/content/cdr/`**, which carries system frequency, inertia, settlement prices by hub and load
  zone, and a **7-day load forecast by weather zone** that the dashboards do not.
- **Google removed the FAQPage rich result in May 2026** and deprecated SpecialAnnouncement in
  July 2025. The plan named FAQPage; that would have been wasted work. **`Dataset` JSON-LD is the
  one type with a live documented consumer** (Google Dataset Search).
- **No major AI crawler documents that it reads `/llms.txt`.** Google, Anthropic and Perplexity all
  describe robots.txt as the control surface and none mention it. Publish one as cheap hygiene,
  claim nothing.
- **Do not block `Google-Extended`, `GPTBot`, `ClaudeBot`, `Claude-SearchBot` or
  `PerplexityBot`.** Google states Google-Extended is not a ranking signal; Perplexity explicitly
  recommends allowing its bot to be cited. **For a record built to be cited, a permissive
  robots.txt is the product strategy.**
- **Workers KV allows 1,000 writes/day.** A read counter writing per pageview breaks at ~1,000
  views. Must batch. **Supabase free projects pause after 7 days of inactivity** and restore is a
  dashboard action, so the daily Worker should issue one authenticated query.
- **Open-Meteo forbids commercial use of the free API** ("You may only use the free API services
  for non-commercial purposes"), and the CC-BY data licence is not a defence because the *service*
  is separately restricted. **Stadia Maps free forbids commercial use outright.** NWS and NCEI are
  keyless, public domain, and cover degree days.
- **`gwlevels` is decommissioned**, redirects removed after June 1st, 2026. Build any USGS work on
  `api.waterdata.usgs.gov`, never `waterservices.usgs.gov`, which USGS itself describes as
  end-of-life.
- Abbott's binding energy commitments come from the Legislature; his data center commitments come
  from letters. **CORRECTED 2026-08-11: an earlier version of this bullet called SB 6's
  December 31st, 2026 4CP deadline "the hardest date on the Texas data center calendar." That is
  now CONTESTED and must not be published.** A second agent fetched the full text of Utilities Code
  Chapter 39 and found no such deadline; the only 2026 date is a September 1st reference elsewhere.
  It may sit in an uncodified section, which needs the enrolled bill to settle. **What IS verified:
  PUCT Project 58482 is where SB 6 is actually being implemented.** See the correction block in
  `knowledge/shared/TEXAS_GOVERNMENT.md`.
- **robots.txt must be re-checked per host, never inherited.** `gisweb.tceq.texas.gov` is
  `Disallow: /` for all agents despite being listed here as working. `courtlistener.com` disallows
  `*` but **explicitly allows `claudebot`**, so our UA is the compliant one there. And a 402 or 403
  is not a robots decision: `interchange.puc.texas.gov` has no robots.txt but 402s a ClaudeBot UA.
- **`texreg.sos.state.tx.us` is allowed and unexploited.** The Texas Register is the authoritative
  publication for proposed rules and their official comment instructions, which makes it the best
  single addition to the collector set.
