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
- ~~No deck has ever shipped from this repo.~~ WRONG, corrected 2026-08-25 by reading
  `runs/carousel/`. SIX decks have shipped, August 16th through 22nd, each with nine webp frames
  and a score. `artwork.json` carries six registers to diverge from and `topics.json` is real.
  The run's own behaviour was right anyway: selection rejected `tx-2026-0072` at 0.70 against
  carousel No. 3, which it could only do by reading a populated ledger. The sentence was wrong
  and the machine was not, which is the more dangerous of the two ways round.
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
| 15 | Panel of 3 scorers | THREE ROUNDS. R1 six hard fails, R2 four, R3 running. R2 found the deck's headline count was eight where the record supports seven |
| 16 | Ship: images, ledgers, site rebuild, 9 exit-code gates, LOOK at pages, PR, merge | |
| 17 | Retro + upgrade | |
| 18 | gmail_draft.py, email_check.py, create_draft | |

## Phase 12 as it actually went

Three pixel critics over nine frames. Frames 4, 5, 7 and 9 rebuilt. Frame 4 was a full rewrite:
its declared camera had never been drawn and its veil was under the type where it could only
make the paper brighter, which inverts the frame's whole argument. Measured after: veiled block
4.43 to 1, clear block 12.96 to 1. Frame 7's falloff went from 3.4 L* across the four repeats to
12.2. Frame 5's band went from 7.3 degrees to 28 by moving the quotes to opposite corners.

`copy.json` rebuilt FROM the renders, in readable form, every string matched by skeleton against
a node the browser actually laid out so nothing unrendered entered the record.

Two gates fixed in the `upgrade` lane, both wrong about a correct deck: `claims_check`'s word
count refusing a JSON field pair, and `texan_check` reading a caption but never a slide.
`claims.json` repaired: 15 source types, 3 rejection keys, one quote extended.

Gate block synced into `RUN_RECORD.md` by `gate_status --sync`. Zero QA fails, verdict WARN.

## The one thing this run did not fix and said so

`plan_render_check` reports 0 of 46 acceptance items checkable, the same ratio the routine's own
prompt warns about by name. The dossiers' acceptance lists are descriptions. Fixing them now
means writing tests to fit frames that already exist. It is a proposal for the next run's
planning phase and it is in the run record.
