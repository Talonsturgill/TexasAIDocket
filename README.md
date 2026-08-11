# Texas AI Docket

A public, fact-checked record of AI decisions in Texas: who is deciding, by when, whether the
public still has a way in, and a fetched primary source behind every fact.

Three things run off this repo:

- **The docket** — every AI infrastructure decision in Texas, re-verified daily, published as
  a page, as open data under CC BY 4.0, and as a corpus written to be read by LLMs.
- **The daily carousel** — one verified Texas AI story a day, planned in forensic detail and
  rendered as bespoke code, delivered as a post-ready email draft.
- **The Texas Grid Watch** — a daily numeric record of the ERCOT grid's position, including how
  much of the large flexible load Texas has approved is actually drawing power.

Two sibling repos carry the rest: `TexasAIDispatch` (the narrated video engine) and
`TexasAIScanner` (the Bottleneck Scanner backend).

## How it fits together

```
ERCOT + EIA ──► gridwatch collector ──► ledger/gridwatch/*.jsonl ──┐
                                                                   ├──► site_build ──► docs/ ──► Pages
research ──► claims ──► docket phase ──► ledger/docket.json ───────┘         │
                                              │                              └──► llms.txt, feeds, JSON-LD
                                              └──► carousel run ──► runs/ ──► email draft
```

`docs/` is generated. It is a pure deterministic function of the ledgers, and
`site_fresh_check.py` proves it by rebuilding into a temp directory and requiring byte
equality. Nothing hand-edits the published site.

## Running the guards

Two structural gates, both of which self-test before they run, because a gate that cannot go
red proves nothing about what it guards.

```bash
# No automation may write outside its lane.
python3 scripts/shared/ownership_check.py --self-test
python3 scripts/shared/ownership_check.py --actor carousel --diff origin/main...HEAD

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
and the house style rules that do not bend. `.claude/WORKLOG.md` is the live build ledger.

## Status

Under construction. `port_audit.py --summary` reports how much of the machine has landed.
