# Texas AI Docket

**[texasaidocket.com](https://texasaidocket.com)**

A public, fact-checked record of AI decisions in Texas: who is deciding, by when, whether the
public still has a way in, and a fetched primary source behind every fact.

Three things run off this repo:

- **The docket** — every AI infrastructure decision in Texas, re-verified daily, published as
  a page, as open data under CC BY 4.0, and as a corpus written to be read by LLMs.
- **The daily carousel** — one verified Texas AI story a day, planned in forensic detail and
  rendered as bespoke code, delivered as a post-ready email draft.
- **The Texas Grid Watch** — a daily numeric record of the ERCOT grid's position, built around
  the load factor, which is the one number here that is genuinely about AI: a data center draws
  at four in the morning close to what it draws at five in the afternoon, so large constant load
  lifts the overnight floor faster than the afternoon ceiling.
- **The Texas Water Watch** — daily reservoir storage for 119 Texas reservoirs, rolled up by
  metro. The driest metro in Texas is in the Permian, which is where much of the new load is
  landing. The page publishes both numbers and draws no conclusion from them.
- **The ask box** — a question about the record, answered in the reader's own browser from an
  index that shipped with the page. Nothing is sent anywhere, and `tests/ask_engine.mjs` cuts
  the network and asks every catalogued question anyway.

Two sibling repos carry the rest: `TexasAIDispatch` (the narrated video engine) and
`TexasAIScanner` (the Bottleneck Scanner backend).

## How it fits together

```
ERCOT  ──► gridwatch collector  ──► ledger/gridwatch/readings.jsonl ──┐
TWDB   ──► waterwatch collector ──► ledger/gridwatch/water.jsonl    ──┤
                                    (both cron, never a routine)      ├──► site_build ──► docs/ ──► Pages
research ──► claims ──► docket routine ──► ledger/docket.json ────────┘        │
                              │                                                ├──► ask index + catalogue
                              │                                                └──► llms.txt, feeds, JSON-LD
                              └──► carousel routine ──► runs/ ──► Gmail draft
```

`docs/` is generated. It is a pure deterministic function of the ledgers, and
`site_fresh_check.py` proves it by rebuilding into a temp directory and requiring byte
equality. Nothing hand-edits the published site.

## The laws

**Numbers are computed, never generated.** Every numeral published traces to a quoted source or
to code that computed it from data, and `numeral_lint` fails the build otherwise. It is stated
publicly on the site, because it is the reason a reader should believe a number here.

**Every path has exactly one owning actor.** Several unattended routines share this history and
each ends in a phase whose job is editing its own machine. Prose is not a boundary against
that; `ownership.yaml` is.

**`docs/` is generated and never hand-edited**, proven by rebuilding into a temp directory and
requiring byte equality.

**A gate that cannot go red proves nothing.** Every checker here self-tests by reintroducing a
known-bad input and requiring itself to reject it, before its real run is allowed to mean
anything.

See `HANDOFF.md` for what has to happen outside this repo to turn it all on.

## Running the guards

Both structural gates self-test before they run.

```bash
# No automation may write outside its lane.
python3 scripts/shared/ownership_check.py --self-test
python3 scripts/shared/ownership_check.py --actor daily --diff origin/main...HEAD

# Is the port done, and is what we moved actually wired up?
python3 scripts/shared/port_audit.py --self-test
python3 scripts/shared/port_audit.py
python3 scripts/shared/port_audit.py --summary      # just the progress table
```

## Why there is an ownership map

Several unattended routines share this one git history, and each of them ends in a phase whose
entire job is editing its own machine. `ownership.yaml` gives every path exactly one owning
actor, and the check runs at commit time and again in CI. An automation that wants to change
something outside its lane records a proposal in its run record and stops.

## Enable the hooks

Cloning does not install hooks. Once per clone:

```bash
git config core.hooksPath .githooks
```

`pre-commit` enforces the ownership map. `post-commit` mirrors every commit to origin
immediately, because this code runs in ephemeral containers where committing is not durable
and only pushing is.

## Repo layout

| Path | What |
|---|---|
| `prompts/` | the routine prompts; each is the source of truth for its routine |
| `knowledge/` | `shared/` Texas research and design doctrine, `carousel/` deck craft |
| `config/` | `brand.yaml` shared voice and tokens, then per-surface config |
| `ledger/` | committed state: the public docket, plus per-actor memory |
| `scripts/` | namespaced by owning actor: `site/`, `carousel/`, `gridwatch/`, `shared/` |
| `assets/` | fonts, art libraries, Texas geodata, places gazetteer |
| `docs/` | the published site. GENERATED, never hand-edited |
| `runs/` | shipped artifacts, merged to main each run |
| `out/` | per-run scratch, gitignored |

`CLAUDE.md` is the law: attribution, merge policy, the ownership model, the Grid Watch rules,
and the house style rules that do not bend. `WORKLOG.md` at the repository root is the build
ledger for a task too large for one context, and exists only while such a task is open.
`knowledge/shared/GATE_LESSONS.md` is permanent, and is the record of faults that shipped with
every check passing.

## Status

Under construction. `port_audit.py --summary` reports how much of the machine has landed.
