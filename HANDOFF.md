# Handoff — what has to happen outside this repo

Everything in this repo runs. What follows is the list of things it cannot do for itself,
because they live in a GitHub setting, a DNS record, a routines UI or a payment page.

Each item says what it unblocks and what happens if it never gets done, so nothing here is a
vague "should". Where something can wait, it says so.

---

## 1. Register the domains. This is the only genuinely urgent one.

Every domain worth having was **unregistered** when this was checked (RDAP and DNS, both):

    texasaihq.com          texasaidocket.com      texasaidocket.org
    texasaidocket.net      txaidocket.com         lonestaraidocket.com

**`texasaihq.com` is the structural match.** The sibling product's pattern is a `<state>aihq`
domain, a wordmark, and the docket as a section of it, and following that pattern means the
docket domains redirect rather than compete.

**If this is never done:** the site lives on a `github.io` URL forever, which costs credibility
with exactly the readers this is for (an agency staffer, a county commissioner, a reporter),
and somebody else eventually registers the name.

**When the domain exists**, one key changes: `SITE_URL` in `scripts/site/site_build.py`. Every
absolute URL, the sitemap, the feeds and the structured data are derived from it, so it is a
one line change and a rebuild.

**The services page is waiting on this too.** It currently says the contact address is not
published yet, because a Texas record should be reachable at a Texas address and publishing a
borrowed one would be a small dishonesty on a page whose whole argument is that the small ones
are what matter. Register the domain, add the address, rebuild.

---

## 2. Pages is on and the site is live. DONE, and here is what it cost.

**https://talonsturgill.github.io/TexasAIDocket/** serves every page.

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

The site is at **https://talonsturgill.github.io/TexasAIDocket/** until the domain in item 1
replaces it. `SITE_URL` in `scripts/site/site_build.py` is the one key to change.

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

## 4. The instrument crons are already wired and need nothing

`.github/workflows/gridwatch.yml` runs twice daily on GitHub Actions and requires no key, no
connector and no routine. It collects ERCOT demand and TWDB reservoir storage, rebuilds the
site, and pushes to `main`.

**It starts working the moment the repo is public and Actions are enabled.** Check
`ledger/gridwatch/readings.jsonl` after a day: one line per settled day, and the newest date
should be yesterday.

**A missed day cannot be recovered.** ERCOT's feeds are rolling windows with no archive behind
them. This is the one irreversible failure the project has, which is why the collector runs
alone, twice, on its own schedule, and never as a step inside an editorial routine that could
fail for an unrelated reason.

---

## 5. Keys, when they are wanted. None of them block anything.

Every integration no-ops cleanly without its key, so the build stays green either way.

| key | unlocks | without it |
|---|---|---|
| Buttondown API key | subscriber email when a docket item opens for comment | the alert step SKIPs |
| Supabase project | the Bottleneck Scanner backend | the scan page is static |
| Cloudflare Worker, KV, Turnstile | the scanner's form handling | no form |

**Texas needs its own Supabase project.** Do not reuse the sibling product's, which is shared
between its scanner and a read counter.

---

## What is deliberately not here

**No analytics, no tracking, no cookies.** The ask box answers in the reader's browser and
sends nothing anywhere. That is a stated promise on the page and a tested one in
`tests/ask_engine.mjs`, which cuts the network and asks every question anyway. Adding an
analytics tag would silently break a promise the site makes in writing.

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
