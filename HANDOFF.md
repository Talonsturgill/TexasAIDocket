# Handoff — what has to happen outside this repo

Everything in this repo runs. What follows is the list of things it cannot do for itself,
because they live in a GitHub setting, a DNS record, a routines UI or a payment page.

Each item says what it unblocks and what happens if it never gets done, so nothing here is a
vague "should". Where something can wait, it says so.

---

## 1. The domain is registered and live. DONE.

**https://texasaidocket.com/** is the canonical public address. Cloudflare DNS, the Pages custom
domain, `docs/CNAME`, `SITE_URL` in `scripts/site/site_build.py`, and the site value in
`config/brand.yaml` all name it now. The services page is live and no longer waits on domain
registration.

This is not a pending handoff item. It remains here because a future domain move has more than one
surface: update the CNAME and site builder, the brand configuration, and the Ask Worker's origin
and pack URLs, rebuild `docs/`, then let `livecheck.yml` prove the public result.

---

## 2. Pages is on and the site is live. DONE, and here is what it cost.

**https://texasaidocket.com/** serves every page.

Left in place because the same trap catches the next repository, and because the failure mode
is a deploy job that fails in about one second with no steps and no logs.

**Settings → Pages → Build and deployment → Source → GitHub Actions.**

That is the whole task. Nothing else is needed, no branch to pick, no folder to set.

**It must be `GitHub Actions`, not `Deploy from a branch`.** Those two look interchangeable and
are not. Picking the branch option still creates the `github-pages` environment, but it locks
that environment's deployment branch policy to the Pages build rather than to `main`, and the
workflow's deploy job is then rejected before it runs a single step:

    Branch "main" is not allowed to deploy to github-pages due to environment protection rules.

The tell is a deploy job that fails in about one second with NO steps and NO logs. A job that
fails inside a step has a log; a job rejected by an environment rule never starts. If that
happens, either set Source to `GitHub Actions`, or go to **Settings → Environments →
github-pages → Deployment branches** and allow `main`.

**Why it cannot be automated.** The workflow asks, with `enablement: true` on
`configure-pages`, and GitHub refuses: `Create Pages site failed. Error: Resource not
accessible by integration`. A workflow's `GITHUB_TOKEN` may DEPLOY to Pages but may not CREATE
the Pages site, and it cannot edit an environment's protection rules either. Both are reserved
to a repository admin, deliberately.

**The second half of the trap, which is the one that actually bit here.** With Source set
correctly, the deploy was still rejected. The `github-pages` environment had come up set to
**Protected branches only** with **no branch protection rules configured**, which means zero
branches qualify and `main` is not special. The fix was **Settings → Environments →
github-pages → Deployment branches → No restriction**. Same one-second, no-log failure, a
different cause, and the two are indistinguishable from the run page.

The canonical site is **https://texasaidocket.com/**. `docs/CNAME` and `SITE_URL` must continue to
agree; `livecheck.yml` opens that address every six hours and fails if the front page, sitemap, or
build stamp is unavailable.

---

## 3. Create the routine trigger

**One routine, not two.** At claude.ai/code/routines. The trigger's prompt is a thin pointer; the
real instructions live in this repo so they are versioned and reviewable.

| routine | prompt file | cadence |
|---|---|---|
| Texas AI Docket, daily | `prompts/daily_routine.md` | daily |

The trigger prompt is the contents of `prompts/ROUTINE_PROMPT.txt`, which says in full: *read
`prompts/daily_routine.md` from `main` and execute it.*

This was two routines until 2026-08-12, one for the record and one for the deck. They are one
now, matching the sibling product. Two daily routines meant two branches, two pull requests, two
merges and two site rebuilds racing each other for the same `docs/` tree. A single routine cannot
race itself, and it updates the record **before** it picks the story, so a deck can only be built
on a decision the record already holds.

**Set permissions to `bypassPermissions`.** An unattended run wedges forever on a permission
prompt with nobody there to answer it.

**Connectors:** Gmail (for the draft). Nothing else is required.

**If this is never done:** everything still works when run by hand; nothing happens on its own.

---

## 4. The scheduled workflows are already wired and need nothing

`.github/workflows/gridwatch.yml` runs twice daily on GitHub Actions and requires no key, no
connector and no routine. It collects ERCOT demand and TWDB reservoir storage, rebuilds the
site, and pushes to `main`.

The other schedules are `datacenters.yml` for the Comptroller registry, `generators.yml` for the
EIA inventory, `queuewatch.yml` for ERCOT's monthly queue report, `livecheck.yml` for the public
site, and `pages.yml` as the deployment backstop. There are seven workflows in total and six have
a schedule; `guards.yml` is the unscheduled validation workflow.

**It starts working the moment the repo is public and Actions are enabled.** Check
`ledger/gridwatch/readings.jsonl` after a day: one line per settled day, and the newest date
should be yesterday.

**A missed day cannot be recovered.** ERCOT's feeds are rolling windows with no archive behind
them. This is the one irreversible failure the project has, which is why the collector runs
alone, twice, on its own schedule, and never as a step inside an editorial routine that could
fail for an unrelated reason.

---

## 5. The Ask Worker bindings

The static build needs no secret. The written Ask lane is a Cloudflare Worker and its live
bindings are configured outside this repository.

| binding | unlocks | without it |
|---|---|---|
| `ANTHROPIC_API_KEY` | written answers | the worker returns that the answerer is not configured |
| `ASK_KV` | answer cache, usage receipts, and the monthly cap | answers can run, but caching and cap accounting are unavailable |
| `TURNSTILE_SECRET` | server-side verification of the public Turnstile token | the worker reports the missing binding at `/_config` and does not enforce the human check |
| Workers AI binding `AI` | optional reranking of the retrieval shortlist | deterministic BM25 and reciprocal-rank retrieval still run |

`ASK_ORIGIN`, `ASK_PACK_URL`, `ASK_CORPUS_URL`, `ASK_MODEL`, `ASK_EFFORT`, `ASK_RETRIEVAL`, and
`ASK_MONTHLY_CAP` are optional overrides. The Worker exposes non-secret configuration state at
`/_config` and a live provider probe at `/_probe`.

---

## What is deliberately not here

**No analytics, no audience tracking and no account cookies.** Typing in the Ask box sends
nothing. Submitting a question is different: after Turnstile, the question goes to the Ask Worker
and Anthropic, and a checked answer may be cached in KV under a content hash. The browser catalogue
path is tested in `tests/ask_engine.mjs`; the network lane and its guard are tested under
`workers/ask/`. Adding analytics would still be a new collection decision rather than a harmless
script tag.

**No human review gate.** The gates are the review, by design, and `CLAUDE.md` states it.

---

## How to check it is working, in one minute

```bash
python3 scripts/shared/port_audit.py            # is the port done, and is it wired
python3 scripts/site/site_fresh_check.py        # is the site exactly what the ledgers produce
python3 scripts/site/house_style_check.py       # does the published copy keep the house rules
python3 scripts/site/theme.py --contrast        # can a reader actually read every colour
python3 scripts/gridwatch/gridwatch_pagecheck.py   # is the grid watch current and honest
```

The first two are the ones that matter. `port_audit` answers "did anything land without being
connected", which is how the previous attempt at this port failed. `site_fresh_check` answers
"does the published site say anything the record does not", which is the promise the whole
product rests on.

---

## Regenerating the web fonts

Only needed if a typeface changes or the subset range does. The output is committed on purpose,
because `docs/` has to be byte-identical to a rebuild and subsetting is not stable across
`fonttools` versions, while a copy is.

```bash
pip install fonttools brotli
python3 scripts/site/fonts_build.py             # rewrites assets/fonts/web/
python3 scripts/site/site_build.py              # copies them into docs/
```

CI never runs this. It runs `fonts_build.py --self-test`, which reads the committed manifest and
needs no font tooling at all.
