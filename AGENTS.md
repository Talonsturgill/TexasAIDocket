# Texas AI Docket: Codex entry point

Read `CLAUDE.md` in full before making changes. It is the repository constitution and remains
the detailed source of truth. This file is the compact Codex entry point; do not let it become
a competing copy. Also read `ownership.yaml`, the nearest path-specific instructions, and any
active `runs/carousel/WORKLOG.md` before writing.

## What this project is

Texas AI Docket is a deterministic civic publication about Texas AI, data-center, grid, water,
policy, and public-access decisions. The product is the verified public record and the useful
reader experience built from it—not merely a website or a social post.

Use this priority order when tradeoffs are real:

1. factual accuracy, source provenance, privacy, and reader trust;
2. clear consequences and a concrete route for a Texan to participate;
3. accessibility, legibility, performance, and reliable behavior;
4. visual craft and editorial distinctiveness;
5. maintainer or automation convenience.

Do not stop at “how can I patch this?” Ask how the change can make the experience clearer,
safer, faster, more trustworthy, or more useful for the reader. Fix the underlying seam when it
is in scope, and verify the behavior a reader encounters rather than only the implementation.

## Repository map

- `ledger/` is committed source-of-truth data. Preserve provenance and append-only histories.
- `scripts/site/` deterministically builds the publication from committed records.
- `docs/` is generated and published. Never hand-edit it; change inputs or builders.
- `scripts/gridwatch/` and their archives collect grid and water instruments independently.
- `.claude/skills/carousel-engine/`, `scripts/carousel/`, and `assets/` build and gate the daily
  LinkedIn deck. Numbers are computed, never invented or typed from memory.
- `prompts/daily_routine.md` is the versioned master prompt for the daily cloud editor.
  `prompts/ROUTINE_PROMPT.txt` is the intentionally tiny Cloud Routines UI trigger.
- `runs/` contains shipped run records and artifacts. Do not rewrite history.
- `workers/ask/` is the written Ask lane; browser behavior is specified in `tests/`.
- `knowledge/` contains doctrine and evidence notes; `GATE_LESSONS.md` records why gates exist.
- `ownership.yaml` defines who may write each path. A human maintainer owns all paths; unattended
  actors do not.

## The daily cloud routine

The routine configured in the Cloud Routines UI runs once daily. Its UI prompt delegates to the
versioned prompt on `main`; edit the repository prompt, not an unversioned copy in the UI. Do not
alter the external routine, cadence, permissions, or connector setup unless Talon explicitly asks.

The daily actor updates and re-verifies the public record first, selects one supported story,
builds and critiques the carousel, opens a PR, performs its narrowly scoped upgrade phase, waits
for exact-head guards, merges only when the routine contract permits it, and creates a Gmail
draft. It never sends the email or publishes the LinkedIn post. Grid and water collectors remain
separate cron actors so an editorial failure cannot erase instrument history.

## Working rules

- The intended GitHub repository is `Talonsturgill/TexasAIDocket`, not the similarly named work
  account. Do not change remotes or accounts without explicit direction.
- Treat an ordinary interactive Codex task as a `human` maintainer session unless an actor stamp
  or the user says otherwise. Respect the per-commit actor model in `ownership.yaml`.
- Preserve unrelated and concurrent changes. This checkout may be shared by several tasks.
- Do not commit, push, open a PR, merge, send, publish, or change cloud configuration unless the
  user explicitly requests that action. The versioned daily routine is the exception only when
  it is itself the active actor.
- Obey the strict source boundary in `CLAUDE.md`. Never work around robots rules or retain personal
  data that a collector is required to discard.
- Draft external communications only. Never send them.
- Never call a skipped check green. A checker self-test proves the gate can fail; the actual gate
  proves the current product passes. Run both when changing that surface.
- Use a temporary output below `out/<date>/tmp/` for manual experiments. Do not use generated
  `docs/` or shipped `runs/` as scratch space.
- When intent would materially change the reader outcome, ask Talon concrete product questions:
  who the reader is, what they should understand or do, and what success looks like.

## Local setup

The committed versions and lock files are authoritative. On Windows, the verified baseline is
Python 3.11 (matching CI), Node `24.18.0`, Git Bash, GitHub CLI, and Playwright Chromium.

```powershell
nvm use 24.18.0
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-carousel.txt
npm ci
npx playwright install chromium
git config core.hooksPath .githooks
```

Reuse an existing `.venv` and `node_modules` when their pins still match. Install or upgrade
development tools when needed, but do not silently move past repository pins: update the pin and
its lock or guard in the same intentional change.

## Verification ladder

During iteration, run the narrow checker self-test and its real product invocation. Before a
handoff or push-ready claim, run the relevant browser tests plus the local workflow runner:

```powershell
.\.venv\Scripts\python.exe scripts\shared\guards_local.py --fast
.\.venv\Scripts\python.exe scripts\shared\guards_local.py
```

`--fast` skips Node/browser suites; the second command is the fuller local approximation of CI.
Some CI-context steps can only run on GitHub and must be reported as skipped, not passed. Inspect
rendered output when visual correctness is part of the change; machine gates do not replace pixel
review.
