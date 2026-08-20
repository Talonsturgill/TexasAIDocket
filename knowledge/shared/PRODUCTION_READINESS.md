# Production readiness, audited against the standard list

A widely shared list of about a hundred things "vibe coders" supposedly do not know about, taken
seriously and checked one by one against what this project actually runs. Audited 2026-08-20.

**The finding in one line: most of that list is inapplicable here, and that is a property of the
architecture rather than an excuse.** The parts that do apply are mostly already in place, and
three real gaps came out of it.

---

## 1. What this project actually runs, because it decides everything below

| | |
|---|---|
| The site | 171 static HTML pages on GitHub Pages, custom domain, Cloudflare DNS in front |
| The one server | A single Cloudflare Worker for the written ask lane |
| The datastore | Committed JSON and JSONL files in git. **There is no database** |
| The scheduler | Four GitHub Actions workflows, three of them cron |
| Dependencies | **Zero third-party Python packages.** Standard library only. Fonts, art libraries and geodata are committed, and no built page loads anything from a CDN |
| Users | Nobody logs in. There are no accounts, no sessions, no personal data, and no reader can write to anything |

Four consequences fall straight out of that, and they are why the list mostly does not bite:

- **No database means no database problems.** Indexing, N+1, connection pooling, read replicas,
  sharding, partitioning, replication, query optimisation, migrations and locking are all
  answers to questions this project never asks.
- **No long-lived process means no process problems.** Memory leaks, garbage collection, thread
  safety, deadlocks and backpressure need a server that stays up. Every script here starts,
  does one thing and exits.
- **No cluster means no cluster problems.** Kubernetes, service discovery, leader election, CAP,
  distributed transactions, sagas and network partitions need more than one node that has to
  agree with another one.
- **No user data means most of the security surface does not exist.** No accounts is no auth, no
  sessions, no CSRF, no IAM, no OAuth, no JWT rotation, and no personal data to encrypt at rest.

**This is a deliberate position, not a stage to grow out of.** A static site backed by git is
the most durable and cheapest shape available for a public record, and every item this
architecture makes irrelevant is an item that can never fail at three in the morning with nobody
at the keyboard.

---

## 2. The audit

### Already in place

| Topic | Where it lives |
|---|---|
| Rate limiting | Turnstile on the worker plus a KV-backed monthly spend cap, default 200 |
| Caching, CDN, edge caching | GitHub Pages plus Cloudflare, free and global |
| Cache invalidation | The stylesheet URL carries a content hash, so a deploy cannot serve new markup with the old sheet |
| CI/CD | `guards.yml`, 79 steps, on every push and pull request |
| Timeouts | Every fetch in every collector sets one, 20 to 120 seconds |
| Retries and exponential backoff | Deploy retries three times, git push retries four with 2, 4, 8, 16 second waits |
| Idempotency | A collector re-run on the same day exits with "already held complete, nothing to do" |
| Cron jobs | Three scheduled workflows, plus a two-hourly deploy backstop |
| Distributed locks and race conditions | Actions `concurrency` groups with `cancel-in-progress: false`, so two runs queue rather than fight over a ledger |
| Dead letter equivalent | A failed fetch writes an explicit unverified record and carries no number forward |
| Server-sent events | The worker streams NDJSON sentence by sentence |
| Rollbacks | `docs/` is generated, so reverting the source and rebuilding is exact by construction |
| Disaster recovery, backups | Git history is the entire system. A fresh clone rebuilds every published byte |
| Multi-region | Both CDNs serve from edge, at no cost and no configuration |
| TLS, encryption in transit, HTTP/2 and HTTP/3, DNS | Free from Cloudflare and GitHub Pages |
| DDoS, WAF | Cloudflare in front of the worker and the domain |
| XSS | Everything interpolated is escaped, plus a Content Security Policy hashed from the bytes that ship |
| CORS | Set explicitly by the worker |
| Secrets management | No secret is in this repository. The worker's live in Cloudflare, and every collector is keyless by design |
| Cost optimisation | Free tiers throughout, with the only paid path capped |
| Clock skew | UTC everywhere, and the collector trusts the payload's own timestamp over HTTP freshness |
| Infrastructure as code | The workflows and `config/` are the infrastructure. There is no cloud estate to declare |
| Dependency hell | Structurally impossible. There are no dependencies |
| Postmortems | `GATE_LESSONS.md`, 30 entries, each naming what to check instead |
| Chaos engineering, lightly | Gates are proved by planting the real defect and watching them go red, and the build is proved against a one-commit shallow clone |
| Observability, partially | `gridwatch_pagecheck.py` reads the published page daily and exits 2 when the collector has fallen behind |

### Does not apply, and why

**Needs a database:** indexing, query optimisation, N+1, connection pooling, read replicas,
sharding, replication, optimistic and pessimistic locking, migrations.
**Needs a long-lived process:** memory leaks, garbage collection, thread safety, deadlocks,
backpressure, liveness and readiness probes, cold starts beyond the worker's own.
**Needs a cluster:** Kubernetes, Docker, service discovery, leader election, CAP, eventual
consistency as a design problem, distributed transactions, sagas, network partitions, failover,
autoscaling, horizontal and vertical scaling, load balancing, reverse proxies, API gateways.
**Needs queues or many services:** message queues, pub/sub, event-driven architecture,
distributed tracing, gRPC, circuit breakers.
**Needs accounts:** IAM, OAuth, JWT rotation, CSRF, encryption at rest, SQL injection.
**Needs a deployment fleet:** blue-green, canary, rolling deploys, Terraform, Helm.
**Needs traffic this does not have:** P99 and tail latency, throughput, error budgets, on-call.

Adopting any of these now would add a failure mode to buy nothing. **A thing that is not there
cannot break.**

---

## 3. The three real gaps

### Gap 1. Nothing checks that the live site is actually serving

Every gate proves the BUILD is correct. Not one of them opens `texasaidocket.com` and confirms
it answers. If DNS lapsed, the `CNAME` were clobbered, the domain expired or Pages unpublished
the site, every check would stay green and the site would be dark.

**This exact shape has already happened once.** `GATE_LESSONS` entry 10 records a merge that
left the live site on the previous build with every gate green, because a `GITHUB_TOKEN` push
does not start a workflow, so no run had even begun. The fix was a two-hourly deploy backstop,
which re-deploys blindly. It does not verify the result.

**The plan.** A scheduled workflow that fetches the live URL and asserts a 200, the expected
title, a sitemap that parses, and a `docket.json` whose item count matches the committed ledger.
It fails loudly, which for a scheduled workflow means GitHub emails the owner. Cheap, and it
closes the one fault class this project has already suffered.

### Gap 2. The published data has no schema version

`docket.json` is published as open data under CC BY and is meant to be consumed by other people
and by machines. It carries `_spec.generated`, a date, and no version. A consumer has no way to
detect that a field changed meaning or went away.

**The plan.** A `_spec.version` following semantic versioning, asserted by a gate that requires
the major to rise whenever a required field is removed or retyped. The rule matters more than
the number, because a version nobody is obliged to bump is decoration.

### Gap 3. The whole system has one point of failure, and it is the GitHub account

Git history is the disaster recovery story, and it is a good one, but every copy lives in one
place. A suspended account or a repository deleted by mistake takes the record, the site, the
automation and the history together.

**The plan.** A weekly workflow that pushes a mirror to a second remote. Anywhere that is not
GitHub qualifies. This is the cheapest insurance on the list and the only item where the
consequence is total.

### A fourth, smaller one

The worker's monthly cap bounds the bill but not the burst. Someone could exhaust the month's
200 answers in an afternoon and the lane would be closed for everyone until the first. Turnstile
raises the cost of doing that and does not make it impossible. A per-day sub-cap, or a per-IP
counter in the KV that already exists, would turn a month-long outage into a day-long one.

---

## 4. What the list gets right, and it is worth saying

The instinct behind that tweet is sound, and it applies here in one specific way. Everything
above is a question about **what happens when something fails and nobody is watching**, and on
this project nobody is ever watching, because there is no human at the keyboard by design.

That does not argue for Kubernetes. It argues for the thing this project already does more of
than most, which is making failure loud, making state reconstructible, and writing down what a
green check is not evidence of.
