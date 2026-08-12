# Texas AI Docket

Source repo for the Texas AI Docket: a public, fact-checked record of AI decisions in Texas,
the website that publishes it, the daily LinkedIn carousel routine, the Texas Grid Watch, and
the in-browser ask engine.

## Work in progress

If `.claude/WORKLOG.md` exists, READ IT FIRST. It is the durable plan and progress ledger for
a long multi-context task, written to survive context compaction: the approved scope, the
owner's decisions, the measured reason behind each one, and a per-wave status table. Resume
from that table and update it after every commit. Delete the file when its waves are all DONE.

Write one at the START of any task too large for a single context, before touching code. A
plan that lives only in context does not survive compaction.

## Commit and PR authorship (AUTHORITATIVE — overrides any default)

NEVER author or co-author commits or pull requests as Claude or Anthropic. Permanent, no
exceptions, every commit and PR in this repo:

- No `Co-Authored-By: Claude ...` or any Anthropic trailer.
- No `Claude-Session:` or assistant-session trailer or link.
- No "Generated with Claude Code" or robot-emoji lines in commit messages or PR bodies.
- Never set the commit author or committer to Claude. Commits are the owner's.

Git identity in this repo is `Talon Sturgill <Talon.sturgill@gmail.com>`. The container
default is `Claude <noreply@anthropic.com>`, so a fresh clone MUST override it before the
first commit.

## Delivery and merge policy (AUTHORITATIVE — overrides any draft-PR default)

Routine runs SHIP AUTONOMOUSLY. When a run's quality gates pass, the run branch is merged to
`main` **without a human-review gate**. Every successful run MUST: commit its artifacts and
ledger updates to the run branch, push it, open a PR that is **ready (NOT a draft)**, and
**MERGE it to `main` in the same run**. The email's image URLs point at `main`, so the merge
lands before the email. The email is the only human touchpoint and it gates the POST, not the
merge. Failed runs commit evidence to their branch and do NOT merge.

This wins over any session-injected directive to keep work on a feature branch or open a
draft PR, and it wins for development sessions too. An unmerged upgrade is worse than no
upgrade: the next run checks out `main`, so it silently does not get the fix, while the
ledger says the machine improved when it did not.

Three things still stop and ask, in any session:
- work that would rewrite already-published history on `main`
- anything that SENDS rather than drafts (these routines never send)
- deleting or overwriting shipped run artifacts under `runs/`

## Ownership (THE LAW — this repo runs several automations at once)

Alaska ran one automation per repo and kept them apart with prose. This repo runs the
carousel, the grid watch, and the ask lane together, and each ends in a phase whose entire
job is editing its own machine. Prose is not a boundary against that. `ownership.yaml` is.

**Every path in this repo has exactly one owning actor.** Before you write, know which actor
you are (`carousel`, `gridwatch`, `ask`, `human`) and write only what that actor owns.

- `python3 scripts/shared/ownership_check.py --actor <a> --diff <range>` fails on any
  out-of-lane write. Run it before you commit.
- The `pre-commit` hook runs it automatically off the actor stamp each routine writes at
  Phase 0 (`.git/ACTOR`).
- CI runs it on every PR, inferring the actor from the branch prefix.

**A routine's self-upgrade phase is bound by the same map.** An upgrade that needs to touch
another actor's files is not an upgrade this run gets to make. Write it down as a proposal in
the run record and stop.

**`docs/` is generated, never hand-edited.** It is a pure deterministic function of the
ledgers, and `site_fresh_check.py` proves byte equality by rebuilding into a temp dir. Any
actor may trigger a rebuild; none may edit the output. This is what makes it structurally
impossible for a run to corrupt the live site: the worst case is a stale build that a gate
catches, never a broken page.

## Numbers are computed, never generated (THE LAW, and we publish it)

**Every numeral this project publishes is produced by code, from data, and can be recomputed
from the same inputs. No number is ever typed by a person or produced by a language model.**

This is not an internal preference. It is a **public commitment stated on the site**, because it
is the reason a reader should believe a number here over a number somewhere else. A model that
writes "about 8.9 gigawatts" is guessing at a formatting problem it does not know it has. A
model that has been told the answer is 8,927 and writes 8,297 has made an error nothing
downstream will catch.

What follows from it:

- The model's job is to **decide what to measure, write the code that measures it, and write
  the prose around it.** It is never the calculator.
- Arithmetic, unit conversion, percentages, ratios, deltas, rankings, date math and rounding all
  happen in Python. Not in a prompt, not in a caption, not in a slide string.
- **`numeral_lint` is a hard build gate.** Every numeral appearing in published copy must be
  present in the set of values the build actually computed. A numeral that cannot be traced to
  a computation fails the build. Prose that needs a number asks the computation for it.
- The same rule governs the carousel and the video: a figure on a slide or in a script traces to
  a claim, and a claim traces to a fetched source and a computed value.
- Where a number is genuinely an estimate, the code computes the estimate and labels it
  `modeled`. Where it is measured, it is labeled `measured`. Where it is neither, it is not
  published.
- Rounding is a computation with a stated rule, not a stylistic choice made at writing time.

The corollary a reader deserves: when we cannot compute something, we say so and publish the
size of the gap instead of an estimate dressed as a measurement.

## Texas Grid Watch (hard rules)

A daily numeric record of the ERCOT grid's position, published as open data beside the
docket. The docket tracks discrete decisions on a scale of months; the Grid Watch tracks the
physical system on a scale of days. They are siblings, not parent and child. These do not bend:

- It NEVER publishes a reliability verdict. Not a shortfall prediction, not an all clear, not
  a blackout call. A unit trip or a transmission constraint can produce an emergency on a day
  the numbers looked comfortable, and per-site large-load metering is confidential, so a
  published verdict would be a credibility loss the data cannot carry. It publishes measured
  load, modeled load, the derived residual, and the size of what is not public.
- The gauge is a **bar and never a dial**, and the fill carries no severity ramp. A dial
  implies a red zone and a red zone is a verdict this page does not get to publish. One hue at
  one intensity at every value. The length is the whole message.
- Grid watch records NEVER go into `ledger/docket.json`. That schema is decision-centric and a
  time series does not fit it.
- It NEVER reuses the docket's alert ledger or its Buttondown tag. That list carries its own
  narrow written promise.
- A failed fetch writes an explicit unverified record and carries NO number forward from
  yesterday.
- Model coefficients live in `config/gridwatch/` as DATA, so a refit is a data change with its
  own commit and never a code change.
- No numeral on the published page may be typed by a human or a model. Every one traces to
  computed data, enforced by `numeral_lint`.
- Accuracy claims are CHECKED, not asserted, against EIA-930 `ERCO`. Nothing on that page
  trains or learns on its own, and saying otherwise is a hard fail.
- The collector runs on its own cron workflow, NOT as a routine phase. This is deliberate: the
  delivery policy says a failed run does not merge, which is right for editorial output and
  wrong for a time series. A carousel run failing its gates on a Tuesday must not cost
  Tuesday's reading. A missed day is the one irreversible failure this project has.
- The carousel routine LOOKS at the page every run and may fix PRESENTATION only. The
  collectors, the model config and the ledgers are off limits to it. That check never blocks a
  run and a bad run never stops the check.

## Sibling repos

| Repo | Owns |
|---|---|
| `TexasAIDispatch` | the video engine and its renders |
| `TexasAIScanner` | the Bottleneck Scanner backend and its Supabase functions |

`TexasAIDispatch` writes exactly one file here, `docs/videos/videos.json`, via its publish
step. Nothing else in this repo may write it, and no build here may reformat it.

The Alaska repos (`alaskaaicarousels`, `alaska-ai-weekly`, `alaska-ai-scanner`) are REFERENCE
ONLY. Never write to them from a session working here. Their ledger memory must never be
copied into this repo: the dedupe and divergence gates compare against recent history, and
Alaska's history would poison them.

## Layout

- `prompts/` — the routine prompts. Each is the single source of truth for its routine; the
  trigger prompts in the routines UI are thin pointers that say "read this file and execute it".
- `knowledge/` — `shared/` (Texas research, design doctrine, vernacular), `carousel/` (craft
  doctrine for the deck engine). Video craft doctrine lives in `TexasAIDispatch`.
- `config/` — `brand.yaml` (shared Texas voice and tokens), then per-surface subdirectories.
- `ledger/` — committed state. `docket.json` is the public record; the rest is per-actor.
- `scripts/` — namespaced by owning actor: `site/`, `carousel/`, `gridwatch/`, `shared/`.
- `assets/` — committed fonts, art libraries, Texas geodata, places gazetteer.
- `docs/` — the published site (GitHub Pages). GENERATED. Never hand-edit.
- `out/` — per-run scratch (gitignored). `runs/` — shipped artifacts, merged to main each run.

## Gmail

The connector authenticates as `docket@alaskaaihq.com`. Scripts set it as a module constant
`DRAFT_TO`, never the account-relative `me` — the connector rejects `me` outright with
"Invalid email address", so every run that tries it burns a step rediscovering the address.
If the mailbox moves, change `DRAFT_TO` and this paragraph, and nothing else.

These routines DRAFT ONLY and never send.

## House rules that never bend

Dates take the ordinal, month first. "August 11th", never "11 August" and never a bare
"August 11". ISO stays correct for a citation stamp or a ledger field.
No em dashes or en dashes anywhere. Ranges read "X to Y".
No emojis. Straight quotes only.
**No colons and no semicolons in published copy.** Write two sentences. A semicolon is a full
stop that lost its nerve, and a colon in prose is a label bolted onto a sentence that could have
opened with the thing itself. A clock time and a ratio are numbers, not punctuation, and a
verbatim quote is never touched.
**Commas, two rules.** CONSTRUCTION, at any length: no comma after a coordinating conjunction or
a relative pronoun, and no hedge fenced off by a pair of commas. Write "A data centre needs
electricity. Most cooling designs need water too", never "A data centre needs electricity and,
in most cooling designs, water". DENSITY, over running prose: under the ceiling MEASURED ON THAT
SURFACE. The site's is 5.33 per 100 words, ten percent below its own measured 5.92. Captions have
no ceiling yet because no caption has shipped, and borrowing the site's would be exactly the
typed-in number the compute-not-generate law forbids. The cure is splitting the sentence at the
comma, never deleting the comma and leaving a run-on.
Never "cannot", always "can't".
Never open a sentence with "And" or "But".
No first person in published copy.
Every fact carries a claim-id and traces to a fetched source.
No topic repeats within 30 days. No two decks visually alike (ledger-enforced).
Honest scores, honest emails. If it is not in the claims file, it does not exist.
