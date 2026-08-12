# WORKLOG — carousel machine to v1

Written before touching code, per CLAUDE.md, because this does not fit one context.

## The directive

> "lets launch this task first that way we can get this repo to a v1 before we move to the
> other repos"

The task is the gap identified when the owner asked whether the carousel automation is as
robust as the one in `alaskaaicarousels`. The honest answer was: scaffolded and wired, not as
deep. This closes it.

## What v1 means here

**The carousel routine can run unattended and produce a deck that meets the standard, with the
gates as the reviewer.** Not "every Alaska file exists in Texas". The measure is whether an
unattended run can fail safely and ship honestly, because nobody reviews the output.

That ordering matters and drives the wave order below: **gates first, craft second, prompt
depth third.** A deep prompt with shallow gates is a machine that produces confident bad decks.
Shallow prompt with deep gates produces fewer decks, which is the survivable failure.

## Measured starting point (2026-08-12, main at a455aa8)

| | Texas | Alaska |
|---|---|---|
| routine prompt | 13 KB, phases 0-14 | 83 KB, 17 phase headings |
| knowledge | 15.6 KB / 4 docs | 316 KB / 6 docs |
| carousel gates | 3 | 10 |
| agents | 10 of 10, avg ~85% depth | 10 |
| engine skill | complete (5 files) | complete |
| ledgers | artwork, captions, topics, upgrades | + instincts |
| runs shipped | **0** | 30 |

Missing knowledge: `TECHNIQUE_LIBRARY.md` (45 KB, 80+ named techniques), `CAPTION_CRAFT.md`
(12 KB).
Missing gates: `dossier_check`, `copy_sync_check`, `aggregate_check`, `claims_check`,
`dedupe_check`, `gate_status`, `ship_images`.
Thinnest agents: pixel-critic 53%, caption-critic 62%, upgrade-engineer 62%.

## Rules this work obeys

1. **Alaska is REFERENCE ONLY.** Never write to those repos. Never copy ledger memory: the
   dedupe and divergence gates compare against recent history and Alaska's would poison them.
2. **Every gate is replayed against the defect it exists for** and watched go red. A gate that
   has never failed is a decoration. See `knowledge/shared/GATE_LESSONS.md` first.
3. **No numeral typed.** Thresholds come from an external standard or from a measurement whose
   date and corpus are recorded. Never "ten percent below our own" more than once, dated.
4. **Ported means retheemed, not copied.** Alaska's technique library is Alaska's material.
   Texas needs Texas material or the decks will look like a borrowed brand.
5. `port_audit.py --reconcile` after each wave, and the manifest must agree with the tree.

## Waves

| # | Wave | Status |
|---|---|---|
| A | The seven missing gates, each with self-test + replay | **IN PROGRESS** — `claims_check` DONE (21 checks, every sibling drift replayed, wired into Phase 3 and CI). Next: `dedupe_check`, `copy_sync_check`, `dossier_check`, `aggregate_check`, `gate_status`, `ship_images` |
| B | `instincts.json` + the ledger the retro phase writes | TODO |
| C | `CAPTION_CRAFT.md`, Texas material | TODO |
| D | `TECHNIQUE_LIBRARY.md`, Texas material | TODO |
| E | Deepen pixel-critic, caption-critic, upgrade-engineer | TODO |
| F | Deepen `carousel_routine.md` against the new gates and craft | TODO |
| G | End-to-end proof: render the demo deck, run every gate on it | TODO |
| H | Reconcile manifest, update CLAUDE.md layout, hand off triggers | TODO |

## Handoff still owed to the owner (not blockers)

- Create the two Claude routines in the routines UI. Trigger text is already in
  `prompts/CAROUSEL_PROMPT.txt` and `prompts/DOCKET_PROMPT.txt`. Neither routine exists yet, so
  neither has ever fired.
- Register the domains (all still open as of the plan).
- Buttondown key when subscriber alerts are wanted. Every integration no-ops without its key.

## Log

- 2026-08-12 — worklog written, starting Wave A.
- 2026-08-12 — `claims_check.py` written and wired. Replays all nine shape drifts the sibling
  suffered across eighteen runs, plus eight quality faults. The strictest check is that `text`
  and `quote` may not be identical: if they are, the fact-checker copied the source into the
  claim rather than verifying a statement against it, and the distinction the whole gate rests
  on has collapsed. Coverage 70 -> 71 of 402.
- 2026-08-12 — the manifest drift gate caught its first real case immediately: the new
  `claims_check.py` row was still TODO. Reconciled. Working as intended on the first use.
