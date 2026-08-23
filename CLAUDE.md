# Texas AI Docket

Source repo for the Texas AI Docket: a public, fact-checked record of AI decisions in Texas,
the website that publishes it, the daily routine that maintains both, the Texas Grid Watch, and
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

## First commands in a fresh clone (AUTHORITATIVE — run these before you write anything)

Both of these are REPOSITORY CONFIGURATION, which does not travel with a clone, and both are
load bearing. Run all three lines together or neither is done.

```
git config user.name  "Talon Sturgill"
git config user.email "Talon.sturgill@gmail.com"
git config core.hooksPath .githooks
```

The third line is the one that was missing on 2026-08-16, and the cost was a whole run of
commits landing with no ownership check on any of them. `.githooks/pre-commit` and
`.githooks/commit-msg` are committed and executable, and git runs neither until it is pointed
at them. The first refuses an out-of-lane write. The second stamps the `Actor:` trailer that CI
reads to judge which lane a commit is in, so without it every commit reaches CI unstamped.

`guards_local.py` now FAILS rather than skips when this is unset, so the gap cannot pass under
a green banner a second time.

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
you are (`daily`, `upgrade`, `gridwatch`, `ask`, `human`) and write only what that actor owns.

The record and the deck were two routines until 2026-08-12 and are one now, on the owner's call.
One process gets one actor, `daily`. Two actors for one process is a fiction the checker cannot
enforce, because the process stamps one name and then needs the other's lane, and the first thing
it learns is that the stamp is negotiable.

`upgrade` is the exception and it earns its keep. The retro phase's whole job is editing the
machine, and while the carousel was its own actor it could not reach `ledger/docket.json` because
it simply did not own it. Merged, that protection is gone unless it is stated, so the phase stamps
`upgrade`, which owns the machine's own files and nothing else. **A self-editing phase must never
be able to edit the public record.**

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

## The record is not published as a file (AUTHORITATIVE, 2026-08-23)

**`docket.json` is never written into `docs/`, and nothing links to it.** The docket is the
most expensive thing this project makes. Publishing it as one CC BY download handed the whole
of it to anyone who wanted to reproduce the site from a single fetch.

What that does and does not mean:

- The record is still READ, item by item, at `/record/` and `/item/<id>/`, with every claim
  and every source. Nothing about what a reader can see changed.
- The `/data/` page is gone and so is its footer entry. The `Dataset` JSON-LD node advertises
  no `DataDownload`, because a structured-data promise that 404s is worse than no promise.
- **The instrument series stay open.** `gridwatch.json`, `waterwatch.json` and `weather.json`
  are still published. They derive from ERCOT, USGS and NOAA, anyone can rebuild them from the
  same public sources, and they are what backs the promise below that a figure here can be
  recomputed rather than taken on trust. The Grid Watch rule that calls it open data is intact.
- `schema_contract.py` still runs, against `ledger/docket.json` rather than the built file. Its
  subject was never the strangers parsing a download. It is the ten modules here that read the
  record and would each break differently on a silent reshape.

**Three surfaces still carry the whole record and are deliberate.** `llms-full.txt` and the
per-item `index.md` twins exist so a model can read the record without parsing HTML, which is
the AI-discoverability work this site was built for. `ask-pack.json` is the record as prose and
the ask worker fetches it from a public URL, so the box cannot answer without it. Removing the
download closed the bulk-import front door. It did not make the record unreadable, and saying
otherwise would be the kind of claim this project does not get to make.

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
- The daily routine LOOKS at the page every run and may fix PRESENTATION only, in
  `scripts/site/gridwatch_page.py` and `scripts/site/waterwatch_page.py`, which are named one by
  one in `ownership.yaml` rather than covered by a glob. The collectors, the model config and the
  ledgers are off limits to it. That check never blocks a run and a bad run never stops the check.

## Sibling repos

| Repo | Owns |
|---|---|
| `TexasAIDispatch` | the video engine and its renders |
| `TexasAIScanner` | the Bottleneck Scanner: its method, its four agents and its renderer. It has NO backend on purpose. The form here posts to FormSubmit, the scan runs locally, and the report goes into a Gmail draft that a human sends. Nothing about a requester is ever stored or published |

`TexasAIDispatch` writes exactly one file here, `docs/videos/videos.json`, via its publish
step. Nothing else in this repo may write it, and no build here may reformat it.

The Alaska repos (`alaskaaicarousels`, `alaska-ai-weekly`, `alaska-ai-scanner`) are REFERENCE
ONLY. Never write to them from a session working here. Their ledger memory must never be
copied into this repo: the dedupe and divergence gates compare against recent history, and
Alaska's history would poison them.

## The public URL (AUTHORITATIVE)

**The site is `texasaidocket.com`. That is the only URL this project publishes, on any surface.**

Never `talonsturgill.github.io/TexasAIDocket`. That is the GitHub Pages host that served the site
before the domain was pointed at it, and it carries the owner's personal name. It is not a brand
URL and it must never appear on a slide, in an email, in a caption, in a User-Agent or on a page.

`docs/CNAME` has said `texasaidocket.com` since the move on 2026-08-15 and `site_build.SITE_URL`
was changed with it, so the SITE has been right the whole time. What was wrong was every surface
that kept its own copy of the string instead of reading the one in `config/brand.yaml`:

- `config/brand.yaml` `visual.constellation.site`, which is the source of truth for the footer
- `frame.py`, which hardcoded it and printed it on the bottom of all eight slides of three
  published decks
- `gmail_draft.SITE`, so every run's email linked it
- four `scripts/gridwatch/*_collect.py` User-Agent strings, which announced it to every server
  this project fetches from

This is the same defect as the missing hashtags and the missing progress counter, for the third
time: a rule stated in config, a surface that keeps its own copy, and nothing in between checking
they agree. `coherence_check.py` now asserts the rendered site line equals the brand.yaml value on
every frame, so a fourth one fails the build instead of shipping.

## Scratch never leaves the working tree (AUTHORITATIVE)

**Every temporary file a run writes goes in `out/<run>/tmp/`. Never `/tmp`, never a system
scratchpad, never anywhere outside this directory.** `out/` is gitignored, so nothing there is
ever committed, and it is inside the tree, which is the whole point.

This is not tidiness. The Bash sandbox and the permission mode are two different mechanisms, and
knowing that is worth an afternoon. `.claude/settings.json` has set `bypassPermissions` since
2026-08-11 and it is correct. A SANDBOXED command that writes outside the working tree still
cannot complete, and the tool then stops and asks to re-run it unsandboxed, which is a prompt the
permission mode does not reach. An unattended run has nobody to answer it.

On 2026-08-20 the owner was interrupted twice by exactly this, on a run whose permissions had been
right for nine days, and the session went looking at the permission mode first because that is
where the word permission is. A run that keeps its scratch inside the tree never has the problem
and never has to work out why it had it.

The exception a session will reach for and must not take: writing outside the tree "just this
once" for a big file. `out/<run>/tmp/` takes big files.

## Layout

- `prompts/` — `daily_routine.md` is the single source of truth for the one daily routine, which
  maintains the record and then ships the deck. `ROUTINE_PROMPT.txt` is the thin pointer pasted
  into the routines UI, which says only "read that file from main and execute it", deliberately,
  so the real instructions stay versioned and reviewable rather than living in a settings box
  nobody diffs.
- `knowledge/` — `shared/` (Texas research, design doctrine, vernacular, sources registry),
  `carousel/` (`TECHNIQUE_LIBRARY.md`, what the engine can execute and how each technique fails;
  `CAPTION_CRAFT.md`, the caption room's menus and the anti-template law; `SLIDE_DOSSIER_SPEC.md`,
  the planning format `dossier_check` enforces; `DESIGN_DOCTRINE.md`; `FIELD_NOTES.md`). Video
  craft doctrine lives in `TexasAIDispatch`.
  **`shared/GATE_LESSONS.md` is required reading before you add a gate, trust one, or conclude
  that a green suite means a correct product.** It is the record of faults that shipped with
  every check passing, and each entry names what to check instead. A green suite has been wrong
  about the colour of the page, the promise on the front page, the state of a badge, whether the
  site published at all, whether a rule in this repo's own ownership map was even in force,
  whether a gate was connected to anything, and prose that had not rendered yet.
- `config/` — `brand.yaml` (shared Texas voice and tokens), then per-surface subdirectories.
- `ledger/` — committed state. `docket.json` is the public record. `carousel/` holds the variety
  ledgers (`topics`, `artwork`, `captions`), the automation-change trail (`upgrades`) and
  `instincts.json`, the craft memory. **An instinct records the DATES it was confirmed and
  contradicted and carries no confidence number**, because confidence is derived by
  `scripts/carousel/instincts.py` and a machine allowed to grade its own lesson grades it high.
- `scripts/` — namespaced by owning actor: `site/`, `carousel/`, `gridwatch/`, `shared/`. The
  carousel gates each carry the defect they exist for in their own docstring, and each has a
  `--self-test` that replays it. Run them by EXIT CODE, never by reading the last line: a report
  that prints advice on failure and one clean line on success looks reassuring either way under
  `tail -1`, and that has shipped a red gate here before.
  **Before you push, run `python3 scripts/shared/guards_local.py`.** It runs the whole of
  `guards.yml` here, by exit code, and it reads that file rather than keeping its own list so it
  cannot fall behind CI. `--fast` defers the node suites while you iterate. Running every
  `--self-test` instead is the wrong half and has already put a red build on the board: a
  self-test proves the checker can go red, and only the checker proves the product is clean.
- `assets/` — committed fonts, art libraries, Texas geodata, places gazetteer.
- The front page's one live line is the **weather chip**, in `scripts/site/frontchip.py` with
  its collector in `scripts/gridwatch/weather_collect.py`.
  `knowledge/shared/TEXAS_TELEMETRY.md` section 0 is the decision record.
  **It ROTATES.** Four candidates run (hundred degree days, freezing nights, nights over 80,
  inches of rain) and it leads with whichever is furthest from its own normal for that date,
  measured in units of that metric's own year to year spread so unlike things can be ranked.
  **The comparison that chooses is never published** — the page prints only what was measured
  and what is normal, because a standard score is good enough to rank four candidates and not
  a number this project would put its name on. A candidate is in season when its own normal
  sits between 10 and 98 percent of a full cycle, so no calendar table decides anything and a
  new candidate needs no window written for it. Its self-test walks all 366 days and asserts
  the chip is never left with nothing to say.
  Two rules inherited from the research: there is no canonical statewide station, so it is
  **city scoped and names the city**, and the station is picked on a stated rule rather than
  for producing the most striking number.
  Its ledger, `ledger/gridwatch/weather.jsonl`, is the one series here that is **not**
  append-only, because NCEI is a permanent archive and every line is re-derivable. That
  carve-out is stated in `ownership.yaml` and nowhere else.
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
a relative pronoun, and no hedge fenced off by a pair of commas. Write "A data center needs
electricity. Most cooling designs need water too", never "A data center needs electricity and,
in most cooling designs, water". DENSITY, over running prose: under the ceiling MEASURED ON THAT
SURFACE. The site's is 3.97 per 100 words, ten percent below its own measured 4.41. Three things
that number has to get right, and each was wrong once: it is measured on RUNNING PROSE, which is
what the gate reads, not whole-page text; it counts only the commas a WRITER CHOSE, since a date
comma and a thousands separator can't be split at; and it is measured on the corpus BEFORE any
comma rule touched it, because ten percent below an already-cut corpus is a ratchet that reaches
zero. Captions have no ceiling because no caption has shipped, and borrowing the site's would be
exactly the typed-in number the compute-not-generate law forbids. The cure is splitting the
sentence at the comma, never deleting the comma and leaving a run-on.
Never "cannot", always "can't".
Never open a sentence with "And" or "But".
No first person in published copy.
Every fact carries a claim-id and traces to a fetched source.
No topic repeats within 30 days. No two decks visually alike (ledger-enforced).
Honest scores, honest emails. If it is not in the claims file, it does not exist.
