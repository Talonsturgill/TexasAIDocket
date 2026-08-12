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
| carousel gates | 3 -> **10** | 10 |
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
| A | The seven missing gates, each with self-test + replay | **DONE** — `claims_check` (21), `aggregate_check` (20), `dedupe_check` (10), `copy_sync_check` (21), `dossier_check` (26), `gate_status` (20), `ship_images` (15). 133 new self-tests. Every one wired into the routine AND into CI, and every one replayed against the defect it exists for |
| A2 | Merge the two routines into one, on the owner's call | **DONE** |
| B | `instincts.json` + the ledger the retro phase writes | **DONE** — 39 self-tests. Confidence is DERIVED, never written |
| C | `CAPTION_CRAFT.md`, Texas material | **DONE** — written, not retheemed. Manifest disposition corrected to REBUILD |
| D | `TECHNIQUE_LIBRARY.md`, Texas material | TODO |
| E | Deepen pixel-critic, caption-critic, upgrade-engineer | TODO |
| F | Deepen `daily_routine.md` against the new gates and craft | TODO |
| G | End-to-end proof: render the demo deck, run every gate on it | TODO |
| H | Reconcile manifest, update CLAUDE.md layout, hand off triggers | TODO |

## Handoff still owed to the owner (not blockers)

- Create the ONE Claude routine in the routines UI. Trigger text is `prompts/ROUTINE_PROMPT.txt`.
  It does not exist yet, so it has never fired. This was two routines until 2026-08-12.
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
- 2026-08-12 — `aggregate_check.py`. The gap between `claims_check` and `numeral_lint`: neither
  looks at the arithmetic performed ON TOP of the claims, and that is where a slide invents a
  number out of verified parts. Detects four shapes in the text the browser actually laid out,
  requires a declaration naming the claim ids, re-derives. An undeclared aggregate fails,
  because "I did not notice it was an aggregate" is how the sibling rendered FIVE where the
  answer was four. Wired as Phase 9.5, between pixel review and assembly, so it runs on what
  was rendered rather than on what was written.
- 2026-08-12 — `dedupe_check.py`. Reads the FULL entry, which is the whole point: the sibling's
  near-repeat survived because a truncated title was read instead of the angle and entities.
  Scores as a share of the candidate's fingerprint so a verbose ledger entry cannot dilute its
  own similarity, and an entry with an unreadable date counts as inside the window so a bad
  date cannot hide a repeat. Graded exits, and the loudest still says read rather than reject.
  Coverage 71 -> 73 of 402.
- 2026-08-12 — the record routine and the carousel routine merged into one,
  `prompts/daily_routine.md`, on the owner's call, matching the sibling product. Two daily
  routines meant two branches, two pull requests, two merges and two site rebuilds racing for
  the same `docs/` tree. It also fixed an ordering fault: the record is now updated BEFORE the
  story is picked, so a deck can only be built on a decision the record already holds. Phase 2
  spawns the scouts and then works the record's worklist while they run, which is wall-clock
  free. The degradation ladder gained two rungs, because the record survives four the deck does
  not: a lost deck costs a post, a lost day of re-verification lets a wrong public fact stand.
- 2026-08-12 — the merge forced a re-read of `ownership.yaml` and found TWO dead rules.
  `scripts/site/**` was written twice, and the second one granted the carousel write access to
  every gate that judges it while the first said, in the plainest words available, that it must
  not. Fixed, and `shadowed()` now proves every rule still answers for its own namesake path.
  It found the second dead rule the moment it was switched on. Actors are now `daily` and
  `upgrade`, one process one actor, with the retro phase's narrow lane keeping a self-editing
  phase off the public record. GATE_LESSONS 12.
- 2026-08-12 — `port_audit`'s orphan check counted a CI `--self-test` line as wiring, which made
  it structurally unable to fail for any gate in the repo. Caught while rewriting the routine
  prompt from scratch, which is precisely when a gate gets dropped by hand. Fixed, replayed, and
  the over-correction ("must appear in a prompt") is guarded against too, because the cron
  collectors appear in no prompt by design. GATE_LESSONS 13.
- 2026-08-12 — `copy_sync_check.py`. Two failures, one file. The record going stale when a
  slide's HTML is hand-edited during pixel review, which is the sibling's slide 05 kicker; and a
  slide citing a claim id that is not in the claims file, which no gate looked at at all. The
  first draft compared a 40 character prefix and its own self-test caught that as strictly worse
  than using the full 80 characters the render records: two bodies agreeing for 64 characters and
  diverging after passed it, which is the exact shape a late edit takes. The remaining blind spot
  past character 80 is pinned by a test that asserts it is NOT detected, so nobody later mistakes
  the limit for a matcher bug and shortens the needle to fix it.
- 2026-08-12 — `dossier_check.py`, the only gate that fires before anything is drawn. The
  sequencing hole it closes: a pixel critic grades each slide against its own dossier, so a bad
  plan executed faithfully passes every review after it, and the sibling's dead lower zone reached
  the scorer six runs running for exactly that reason. Reads the bottom band as its OWN clause,
  because a lavish top third would otherwise vouch for an unplanned bottom, and that substitution
  is the whole defect. Carries the sibling's word-boundary lesson: "ground" is not a hint, since
  "the ground plane is left flat" describes the defect and as a substring it also cleared every
  slide with a background.
- 2026-08-12 — `gate_status.py`. Three sibling failures, each tighter than the last: a
  hand-written reconciliation claiming zero QA warnings while the artifact said five; a correct
  block pasted once with four render rounds run under it; and the same instinct broken twice in
  one run at high confidence. So artifacts are PARSED and never measured (a valid report was once
  false-flagged for being 196 bytes against a 200 byte threshold), binaries are checked by magic
  bytes, and `--sync` writes the block rather than asking anyone to retype it. Idempotent, because
  a rule with a cost gets skipped at the moment it matters. The row this version adds is STALE: an
  artifact that predates the newest render is answering about a deck that no longer exists, and it
  will say PASS forever.
- 2026-08-12 — `ship_images.py`. Every figure measured on the files in front of it, per the
  compute-not-generate law, which a script whose whole output is numerals is the last place to
  break. Refuses any encode under 40 dB, an EXTERNAL visually-lossless threshold rather than one
  measured from our own encodes, which would pass whatever we happened to ship first. Its first
  fixture accumulated grain in uint8, wrapped 255 to 4, scattered speckle over the brightest band
  and measured 34 dB and 99x: both numbers about the bug, not the encoder. A gate whose fixture is
  pathological measures its fixture. Fixed in int16 with a clip, it measures 42.1 dB, which lands
  where the sibling's real decks measured. `--all` refuses to write without `--force`, because it
  reaches into runs that have already shipped and CLAUDE.md puts that on the stop-and-ask list.
- 2026-08-12 — **WAVE A DONE.** Carousel gates 3 to 10. The measure was never "Alaska's files
  exist here", it was whether an unattended run can fail safely and ship honestly, and the seven
  gates are the reviewer that nobody is.
- 2026-08-12 — `instincts.json` and `instincts.py`, and the one thing deliberately not ported.
  The sibling's ledger carries 101 entries, 47 of them at 0.90 confidence, and only 25 have ever
  been confirmed once. The arithmetic only goes one way, so those numbers were typed at the moment
  the lesson was written, by the same model that had just decided the lesson was worth writing. A
  machine allowed to grade its own lesson grades it high, and that number is what decides which
  lessons reach the next run's directors room. It is the compute-not-generate law with a hole in
  it, in the file that shapes how every future deck gets made. Here an entry records the DATES it
  was confirmed and contradicted, confidence is Laplace's rule of succession over those events,
  and a written confidence field is a hard fail on load, along with score, weight, certainty and
  priority, which are the words a model reaches for once confidence is refused. The injection bar
  of 0.7 is not a dial: under this formula it means three confirmations with no contradiction, so
  an instinct reaches the prompt by surviving three runs. Starts empty, because this repo has
  shipped zero decks and cannot have learned anything from running.
- 2026-08-12 — `CAPTION_CRAFT.md`, written as Texas material rather than retheemed, and the
  manifest disposition corrected from PORT_RETHEMED to REBUILD to say so. The menus are the most
  repeatable part of a caption, so Alaska's would carry Alaska's civic vocabulary and its landscape
  into every Texas post. Ten opening moves, eight structures, five closes, all new and all Texas.
  The comma ceiling stays deliberately unset, because no caption has shipped and borrowing the
  site's 3.97 would be exactly the typed-in number the law forbids. The doc named a ledger contract
  captions.json did not declare, so the contract is now declared, including that `first_line` is
  stored VERBATIM: the critic's real job is catching a sentence skeleton that survived a change of
  nouns, and it can only do that with the real lines in front of it.
- 2026-08-12 — writing that doc immediately created the exact defect the port audit exists for. It
  existed on disk, referenced only by the WORKLOG, which the audit deliberately does not count as
  wiring. Wired into the routine's context block, Phase 10, and both caption agents. The manifest
  drift gate caught the stale row on the same run, its third real catch.
