# WORKLOG — the deck, August 25th 2026

Lives here rather than in `.claude/`, which `ownership.yaml` resolves to `human`. A run stamped
`daily` is refused there and clearing the stamp to get past a guard is how a guard stops being one.
The run directory is this actor's own lane, so the plan is committed rather than uncommitted, and
it now survives a reclaimed container as well as a compaction. Recorded as a proposal in `c992ba19`.

Owner's directive, 2026-08-25, verbatim in substance: run the deck half in full, make the pretty
deck, update it to the site, drop it in Gmail drafts. Autonomous, owner is walking. "no empty RUNS
only a great carousel post is an option, be great and wow the readers".

Rung (a) of the degradation ladder is the only acceptable outcome. Nine slides.

## What is already true when this starts

- `main` at `7ebe2ec3`. Record is 73 items, live, built and deployed.
- The record half for this cycle shipped as #186 (August 23rd run) and merged today. Worklist
  cleared, 4 items admitted, primary source share 78.05 percent.
- No deck has ever shipped from this repo. `ledger/carousel/topics.json` and `artwork.json` are
  therefore near empty, so dedupe has little to bite on and `instincts.py --top 5` will print
  nothing. That is correct rather than a gap, per Phase 9.
- The August 23rd run left a claims file, but non-negotiable 1 says every claim carries a URL
  retrieved THIS RUN. Those claims are re-fetched here, not reused.

## Branch and actor

`claude/daily-2026-08-25`, actor stamp `daily` in `.git/ACTOR`. Run dir `runs/carousel/2026-08-25/`,
scratch `out/2026-08-25/` which is gitignored and inside the tree.

## Status

| # | Phase | State |
|---|---|---|
| 0 | Worklog, branch, actor stamp, run dirs | DONE |
| 8 | Selection + dedupe gate + texan_check | DONE. tx-2026-0072 REJECTED, LIKELY REPEAT 0.70, same item as No.3 six days ago. Story is the PATTERN across 10 bodies |
| 6 | Claims, re-fetched this run | DONE. 21 claims, 9 primary, ALL 21 re-fetched and confirmed. compute.py wrote figures.json. Killeen vote count REFUSED, two sources disagree |
| 9 | Directors room, 3 lenses. BEHIND GLASS wins the spine, THE INSTRUMENT's nine-camera discipline and its honesty catch grafted. 9 dossiers, dossier_check EXIT 0 | DONE |
| 10 | 2 directors done, both pass caption_check. Critic RUNNING | IN PROGRESS |
| 11 | 9 slides authored, render EXIT 0, qa EXIT 0 no fails, bespoke median 0.2479 | DONE |
| 12 | copy_sync EXIT 0 after rebuilding copy.json FROM the renders. Pixel critics RUNNING | IN PROGRESS |
| 12b | ALL SIX EXIT 0. plan_render caught zero dossiers declaring display strings, absence caught slide 1 citing nothing | DONE |
| 13 | EXIT 0. 9 declarations. The gate caught WORD FORM numbers, eight and Four and Two, as computed counts | DONE |
| 14 | EXIT 0, pdf_mode vector | DONE |
| 15 | Panel of 3 scorers, panel.py, gate_status --sync | |
| 16 | Ship: images, ledgers, site rebuild, 9 exit-code gates, LOOK at pages, PR, merge | |
| 17 | Retro + upgrade | |
| 18 | gmail_draft.py, email_check.py, create_draft | |

## Rules this run must not break

Numerals computed in Python, never typed. Every fact a claim id. Ordinal dates month first. No em
or en dashes, no colons or semicolons in published copy, no emojis, straight quotes, never
"cannot". No first person. Slides bespoke, dossiers before code. Bounded fan-out, showrunner only,
subagents never spawn. Draft only, never send. `ship_images.py` exit code is a stop. Read gates by
EXIT CODE.

## The gate this run fixed, in lane

`caption_check` reported first person on a caption quoting Brazoria County's minute line
"No action taken due to I.3 failed", because a period is a word boundary and `\bI\b` matched
the I in I.3. Both ways past it damaged the record, so the fix went to the gate.

It belongs to `upgrade`, not `daily`, so the actor stamp was switched for that one commit and
switched back. That is what the two-actor split is for and it is the second time this run the
ownership map has stopped something: the first was the worklog itself.

Five self-test cases, both directions, and a copy of the file carrying the old regex was run
against the new suite and went red on exactly the two new cases. `30a0aa83`.
