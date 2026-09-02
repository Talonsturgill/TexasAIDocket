# Production readiness, audited against the standard list

A widely shared list of about a hundred things "vibe coders" supposedly do not know about, taken
seriously and checked one by one against what this project actually runs. Audited 2026-08-26.

**The finding in one line: most of that list is inapplicable here, and that is a property of the
architecture rather than an excuse.** The parts that do apply are mostly already in place, and
the remaining gaps are recorded below.

---

## 1. What this project actually runs, because it decides everything below

| | |
|---|---|
| The site | 390 static HTML pages and 588 total published files on GitHub Pages, custom domain, Cloudflare DNS in front, as of August 26th, 2026 |
| The one server | A single Cloudflare Worker for the written ask lane |
| State | Committed JSON and JSONL files in git, plus Cloudflare KV for the Ask cache, usage receipts, and spend counter. **There is no relational database** |
| The scheduler | Seven GitHub Actions workflows, six of them scheduled |
| Dependencies | The publication core is mostly standard library, but validation, rendering, extraction, and font work use PyYAML, Pillow, NumPy, Playwright, pypdf, img2pdf, openpyxl, fonttools, and brotli. There is no central dependency manifest or lock file |
| Users | Nobody logs in and there are no accounts or sessions. Submitted Ask questions leave the browser for the Worker and Anthropic; checked answers may be cached in KV |

Four consequences fall straight out of that, and they are why the list mostly does not bite:

- **No relational database means no relational database problems.** Indexing, N+1, connection
  pooling, read replicas, sharding, partitioning, SQL migrations and row locking are answers to
  questions this project never asks. KV still has availability, retention, and counter semantics
  that the Worker must handle.
- **No long-lived process means no process problems.** Memory leaks, garbage collection, thread
  safety, deadlocks and backpressure need a server that stays up. Every script here starts,
  does one thing and exits.
- **No cluster means no cluster problems.** Kubernetes, service discovery, leader election, CAP,
  distributed transactions, sagas and network partitions need more than one node that has to
  agree with another one.
- **No accounts removes most account security.** There is no login, session, OAuth, JWT rotation,
  password reset, or account database. The Ask and form submission paths still have input,
  privacy, abuse, CORS, and secret-management responsibilities.

**This is a deliberate position, not a stage to grow out of.** A static site backed by git is
the most durable and cheapest shape available for a public record, and every item this
architecture makes irrelevant is an item that can never fail at three in the morning with nobody
at the keyboard.

---

## 2. The audit

### Already in place

| Topic | Where it lives |
|---|---|
| Rate limiting | Turnstile plus KV-backed monthly, daily, and salted per-reader caps, default 200, 100, and 50 uncached answers |
| Caching, CDN, edge caching | GitHub Pages plus Cloudflare, free and global |
| Cache invalidation | The stylesheet URL carries a content hash, so a deploy cannot serve new markup with the old sheet |
| CI/CD | `guards.yml`, 126 command steps reported by `guards_local.py` across eight jobs, on every pull request and every push to `main` |
| Timeouts | Every fetch in every collector sets one, 20 to 120 seconds |
| Retries and exponential backoff | Deploy retries three times, git push retries four with 2, 4, 8, 16 second waits |
| Idempotency | A collector re-run on the same day exits with "already held complete, nothing to do" |
| Cron jobs | Six scheduled workflows, including collectors, a six-hourly live check, and a two-hourly deploy backstop |
| Distributed locks and race conditions | Actions `concurrency` groups with `cancel-in-progress: false`, so two runs queue rather than fight over a ledger |
| Dead letter equivalent | A failed fetch writes an explicit unverified record and carries no number forward |
| Server-sent events | The worker streams NDJSON sentence by sentence |
| Rollbacks | `docs/` is generated, so reverting the source and rebuilding is exact by construction |
| Disaster recovery, backups | A fresh clone rebuilds every published byte. Worker bindings and secrets remain external Cloudflare state |
| Multi-region | Both CDNs serve from edge, at no cost and no configuration |
| TLS, encryption in transit, HTTP/2 and HTTP/3, DNS | Free from Cloudflare and GitHub Pages |
| DDoS, WAF | Cloudflare in front of the worker and the domain |
| XSS | Everything interpolated is escaped, plus a Content Security Policy hashed from the bytes that ship |
| CORS | Set explicitly by the worker |
| Secrets management | No secret is in this repository. The worker's live in Cloudflare, and every collector is keyless by design |
| Cost optimisation | Free tiers throughout, with the only paid path capped |
| Clock skew | UTC everywhere, and the collector trusts the payload's own timestamp over HTTP freshness |
| Infrastructure as code | Workflows, site configuration, and Worker source are committed. DNS, Pages settings, Worker deployment, bindings, and secrets remain external state documented in `HANDOFF.md` |
| Dependency control | Playwright is pinned in CI and workflows install their Python packages explicitly. Python packages are not centrally declared or locked |
| Postmortems | `GATE_LESSONS.md`, 70 entries, each naming what to check instead |
| Chaos engineering, lightly | Gates are proved by planting the real defect and watching them go red, and the build is proved against a one-commit shallow clone |
| Observability | `livecheck.py` opens the public site every six hours; the grid and water page checks distinguish a stopped instrument from an advisory presentation fault |

### Does not apply, and why

**Needs a relational database:** indexing, query optimisation, N+1, connection pooling, read replicas,
sharding, replication, optimistic and pessimistic locking, migrations.
**Needs a long-lived process:** memory leaks, garbage collection, thread safety, deadlocks,
backpressure, liveness and readiness probes, cold starts beyond the worker's own.
**Needs a cluster:** Kubernetes, Docker, service discovery, leader election, CAP, eventual
consistency as a design problem, distributed transactions, sagas, network partitions, failover,
autoscaling, horizontal and vertical scaling, load balancing, reverse proxies, API gateways.
**Needs queues or many services:** message queues, pub/sub, event-driven architecture,
distributed tracing, gRPC, circuit breakers.
**Needs accounts:** IAM, OAuth, JWT rotation, password resets, session revocation.
**Needs a deployment fleet:** blue-green, canary, rolling deploys, Terraform, Helm.
**Needs traffic this does not have:** P99 and tail latency, throughput, error budgets, on-call.

Adopting any of these now would add a failure mode to buy nothing. **A thing that is not there
cannot break.**

---

## 3. Findings and remaining gaps

### Gap 1. Nothing checked that the live site was actually serving. CLOSED 2026-08-20

At the time of the finding, every gate proved the BUILD was correct and none opened
`texasaidocket.com` to confirm it answered. If DNS lapsed, the `CNAME` were clobbered, the domain
expired or Pages unpublished the site, every check stayed green while the site was dark.

**This exact shape has already happened once.** `GATE_LESSONS` entry 11 ("A deploy that depends on who pushed") records a merge that
left the live site on the previous build with every gate green, because a `GITHUB_TOKEN` push
does not start a workflow, so no run had even begun. The fix was a two-hourly deploy backstop,
which re-deploys blindly. It does not verify the result.

**What shipped.** `.github/workflows/livecheck.yml` runs every six hours. It fetches the canonical
address from `docs/CNAME`, requires the front page to identify this site, parses the live sitemap,
and compares `/status.json` with the committed ledger count. A dark site exits 1. A reachable site
that is only behind exits 2 and becomes a warning, so a deploy in flight does not train anyone to
ignore the alarm.

### Gap 2. The published data has no schema version. CLOSED 2026-08-20

**And the first description of it here was wrong, which is worth keeping.** The version was not
missing. `ledger/docket.json` carried `_spec.version` all along and the publish step rebuilt the
block from scratch with only the build date, so it existed and reached no reader. That is the
same shape as the site URL, the hashtags and the progress counter: a value stated in one place
and a surface keeping its own copy. Looking before writing found it; writing from the summary
would not have.

**What shipped.** All four published data files carry the version now. The rule that governs it
lives beside the constant in `docket_build.SPEC_VERSION`, and `schema_contract.py` enforces it
against `config/schema_contract.json`.

**The rule, on the owner's call.** An integer rather than semver, because `_spec.generated`
already answers "did the content change" and that leaves exactly one question, which is "will
my code still work". Breaking is a required field removed or demoted, any field retyped, or a
value removed from a vocabulary. **Adding is never breaking**, including adding a topic, because
a version that rises every time a beat is added is a version nobody reads.

**The part worth copying.** Publishing the number is the easy half and on its own it makes
things WORSE. A version nothing is obliged to move is not a weak promise, it is a false one: a
consumer who pins to it and receives a silently reshaped file is worse off than one who knew
there was no guarantee, because the number talked them out of checking.

**Two design choices that keep the gate honest.** "Required" is read from the validator's own
tuple rather than from what today's items happen to contain, so an optional field every current
item carries is not mistaken for a promise. And the contract file is owned by `human` rather
than `daily`, because a contract the process that changes the data can also rewrite is not a
contract.

### Gap 3. The whole system has one point of failure, and it is the GitHub account

Git history is the disaster recovery story, and it is a good one, but every copy lives in one
place. A suspended account or a repository deleted by mistake takes the record, the site, the
automation and the history together.

**The plan.** A weekly workflow that pushes a mirror to a second remote. Anywhere that is not
GitHub qualifies. This is the cheapest insurance on the list and the only item where the
consequence is total.

### Closed gap 4. The monthly cap needed a shorter fuse

Closed on 2026-08-27. The worker refuses uncached calls once its KV-backed counts reach 100 across
the site per UTC day or 50 from one salted reader key, while the 200-call monthly ceiling remains
the final backstop. Cached answers still open after every ceiling because they cost nothing new.
The reader key is a salted digest of the connecting address, expires after three days, and
contains no raw address. KV is eventually consistent, so these are fail-soft circuit breakers,
not an accounting ledger for simultaneous calls from different edges. The request itself is
bounded at 96 KiB, 65 messages, and 64,000 conversation characters before Turnstile, retrieval,
or the model can be called.

### Gap 5. Python dependencies are not centrally declared

The workflows install the packages their own jobs need and the carousel bootstrap discovers some
packages at runtime. That is enough to run today and is not a reproducible dependency contract.
There is no `requirements.txt`, `pyproject.toml`, or lock file tying local work, CI, and future
maintenance to one reviewed set. Centralizing and pinning those packages would make dependency
changes visible in one diff instead of several workflow and bootstrap files.

---

## 4. What the list gets right, and it is worth saying

The instinct behind that tweet is sound, and it applies here in one specific way. Everything
above is a question about **what happens when something fails and nobody is watching**, and on
this project nobody is ever watching, because there is no human at the keyboard by design.

That does not argue for Kubernetes. It argues for the thing this project already does more of
than most, which is making failure loud, making state reconstructible, and writing down what a
green check is not evidence of.
