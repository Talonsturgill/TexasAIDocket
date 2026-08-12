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

## 2. Repository visibility — ALREADY DONE

`TexasAIDocket`, `TexasAIDispatch` and `TexasAIScanner` are all public. This unblocked GitHub
Pages and the `raw.githubusercontent.com` image URLs the run email uses for the deck
thumbnails, and it means the instrument crons in item 4 can run.

Nothing in the repo holds a secret, which is the point. The record is meant to be read,
`robots.txt` says yes rather than no deliberately, and both collectors use keyless public
endpoints.

**What is left here:** confirm GitHub Actions is enabled and that Pages is set to deploy from
the `pages.yml` workflow rather than from a branch.

---

## 3. Create the routine triggers

At claude.ai/code/routines. Each trigger's prompt is a thin pointer; the real instructions live
in this repo so they are versioned and reviewable.

| routine | prompt file | cadence |
|---|---|---|
| Texas AI Docket, carousel | `prompts/carousel_routine.md` | daily |
| Texas AI Docket, record | `prompts/docket_routine.md` | daily, offset from the carousel |

The trigger prompt should say, in full: *read `prompts/<file>` from `main` and execute it.*

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
python3 scripts/gridwatch/gridwatch_pagecheck.py   # is the grid watch current and honest
```

The first two are the ones that matter. `port_audit` answers "did anything land without being
connected", which is how the previous attempt at this port failed. `site_fresh_check` answers
"does the published site say anything the record does not", which is the promise the whole
product rests on.
