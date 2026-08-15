# WORKLOG — the written answer lane

Started 2026-08-15. Owner asked for "the exact same thing we just did" on the sibling
product, meaning the ask box gains a model-backed written answer beside the free in-page
engine it already has.

Delete this file when the wrap tasks are all DONE.

---

## Scope, as approved

The box on the front page today answers entirely in the browser from an inline index and
sends nothing anywhere. That stays exactly as it is and is not touched. What gets added is a
second lane: pressing enter sends the question to a Cloudflare Worker, which puts the whole
published record in one prompt, checks every returned sentence against that record, and
streams back only what passed.

The free lane is most of what the box does and is why it works on a phone with no signal in
a county meeting room. Nothing here may weaken that.

## Measured facts behind the decisions

Numbers taken on 2026-08-15, recorded so a later session does not re-derive them.

**The record is 2.9x the sibling's, and that is item count, not bloat.** Texas carries 58
decisions at 4,211 chars each. The sibling carries 20 at 4,929 each. Texas records are
LEANER. This is a scaling problem that Texas meets first and the sibling meets at 58 items,
not a Texas problem.

**A third of the claims payload is plumbing the model never uses.** Claims are 57.4% of the
ledger. Inside them: verbatim_quote 27.4%, text 16.6%, source_url 16.2%, source_title 14.1%,
source_type 2.8%, fetched 2.1%. Only 95 distinct URLs across 234 claims, so most of the URL
weight is the same link repeated. The bottom four fields belong in the corpus, which is what
the checker verifies against, and on the page, which is where a reader clicks. They do not
belong in the prompt: answers cite the decision, never a raw URL.

Dropping them takes the record from 61,070 to 45,482 tokens. Prose rendering cuts about 28%
more on the sibling's observed ratio, landing near 32,700 tokens against its 20,718.

**Therefore about $0.085 a cold question and $0.010 a follow-up** at Sonnet 5 intro rates,
roughly 1.8x the sibling. A 200 per month ceiling is about $17. THE CEILING IS THE COST
CONTROL, not a retrieval layer: sending only the records a ranking picks is cheaper and
reintroduces the failure whole-record prompting exists to avoid, which is the right item not
being selected. One config variable beats a new subsystem.

**No retrieval, no embeddings, no chunking.** The corpus fits. This is the same call the
sibling made and the reason its answers cannot cite something that is not on the record.

## Two places this deliberately does NOT copy the sibling

**1. The allow-list is derived from the PACK, not from the ledger.** The sibling authorises
every numeral in its whole gas watch series while showing the model only the current reading,
so its allow-list is far more permissive than what the model was actually given. Copying that
here would be worse than loose, it would be useless: `docs/weather.json` is 231,769 bytes of
time series, and authorising it would admit nearly every small number that exists, at which
point an invented figure passes by coincidence. So `ask_corpus.build()` calls
`ask_pack.build()` and derives the allow-list from the pack's own text. The invariant becomes
exact: THE MODEL MAY STATE A NUMBER ONLY IF THAT NUMBER WAS IN WHAT IT WAS SHOWN. Feeds are
summarised into the pack as current readings, never pasted in whole.

**2. Numeral tokenising must agree across two languages.** `numeral_lint.NUMERAL` is
`\d(?:[\d,]*\d)?(?:\.\d+)?`, which takes `8,927` as ONE token. The sibling's simpler pattern
splits it into `8` and `927`. The worker's checker is JavaScript and has to tokenise
identically or the gate is measuring something different from the build-time lint. Normalise
strips commas as well as leading zeros, so a model shown `8,927` may write `8927`. Needs a
test that runs the same strings through both implementations.

## Guards, which are NOT a copy of the sibling's

The sibling refuses three things. Texas refuses more, because its house rules are stricter
and its instrument is different. Every one of these is a hard fail in the worker's checker,
and every one needs a red case in the test suite proving the gate can go red.

| guard | why |
|---|---|
| numeral | every figure traces to the published allow-list. `numeral_lint` already enforces this on the built site; the worker enforces the same set on model prose |
| citation | a named decision must be on the record |
| verdict | NEVER a grid reliability verdict. Not a shortfall prediction, not an all clear, not a blackout call. CLAUDE.md, and it does not bend |
| colon, semicolon | banned in published copy. The sibling's `plainly()` already strips both and ports directly |
| cannot | always "can't" |
| sentence-initial And, But | banned. NOT in the sibling |
| first person | banned in published copy. NOT in the sibling |
| comma density | under 3.97 per 100 words on running prose, measured the way `house_style_check` measures it |

## File map

| path | state | what |
|---|---|---|
| `scripts/site/ask_answers.py` | EXISTS, untouched | the free engine. 611 lines. `index()` already derives counties, metros, window state and days_left from the gazetteer, so the pack builder leans on it rather than recomputing |
| `scripts/site/ask_corpus.py` | TO WRITE | the published allow-list the worker checks answers against. Machine shaped, never read by a model |
| `scripts/site/ask_pack.py` | TO WRITE | the same record as prose, for the prompt. Pure function of `ask_corpus.build()` so there is no second source of truth. Size ceiling is a HARD build gate, because every token is paid on every question |
| `workers/ask/` | TO WRITE | ported from the sibling: worker.js, answer.js, checks.js, bundle.mjs, four test suites. Prompt caching and the spend counter from the start, not retrofitted |
| `scripts/site/site_build.py` | TO EDIT | the written lane's client. Thread above the field, streaming render, withheld reason surfaced, Turnstile, capped copy, one-press follow-up chip |
| `tests/ask_engine.mjs` | EXISTS | free-lane suite. Must stay green untouched: it is the proof the free lane still sends nothing |
| `tests/ask_written.mjs` | TO WRITE | the outbound lane in a real browser, worker stubbed answering and refusing |

## Infrastructure, owner's hands

Domain `texasaidocket.com` registered 2026-08-15 through Cloudflare Registrar.

| item | state |
|---|---|
| DNS, four A records plus www CNAME, all DNS-only | DONE, verified resolving to the four Pages IPs on apex and www. They are the real Pages addresses and not Cloudflare's proxy range, which is the proof the grey cloud was set |
| Cloudflare KV namespace | DONE |
| Turnstile widget | DONE. Site key `0x4AAAAAAEQ2csplf8Pifi79`, public, bakes into the page. Secret key is the owner's and goes in the worker, never here |
| Pages custom domain in repo settings | WAITING ON OWNER. Until it is set, the apex answers 404 and no certificate issues. The CNAME being in the artifact is necessary and not sufficient |
| Anthropic API key | WAITING |
| Worker shell named texasai-ask | WAITING |
| monthly ceiling | UNDECIDED. Recommendation 200, about $17 |

## Gotchas already paid for

**`claude/ask-` is a reserved branch prefix.** `ownership.yaml` maps it to the archive
automation's lane, which may not touch `site_build.py` or regenerate `docs/`. A branch named
that fails the ownership gate with 155 violations before a line of code is read. Work on this
from a prefix that maps to no actor, which the checker treats as `human`.

**CNAME must be IN THE ARTIFACT.** Actions deploys publish exactly what the artifact
contains, so a custom domain set only in Pages settings is dropped on the next deploy.

## Tasks

| # | task | status |
|---|---|---|
| 1 | move the site to texasaidocket.com | DONE, PR #50, merge BLOCKED on owner DNS |
| 2 | `ask_corpus.py` against the Texas schema | DONE. 228 authorised numerals, 68 ledger numerals correctly dropped |
| 3 | `ask_pack.py`, with the claims trim, plus a hard size ceiling | DONE. 150,314 chars, roughly 37,578 tokens, ceiling 220,000 |
| 4 | `workers/ask/` port, Texas guard set, red case for every guard | TODO |
| 5 | written lane client in `site_build.py` | TODO |
| 6 | `tests/ask_written.mjs` | TODO |
| 7 | wire all of it into `.github/workflows/guards.yml` | TODO |
| 8 | owner walkthrough for worker deploy, once 4 is done | TODO |

### Wrap

| # | task | status |
|---|---|---|
| W1 | carry the claims trim back to the sibling's pack, where the same plumbing rides in every prompt | TODO |
| W2 | delete this file | TODO |
