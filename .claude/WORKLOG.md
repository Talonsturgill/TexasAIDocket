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
| 5 | Texas Grid Watch (ERCOT) | TODO | |
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
