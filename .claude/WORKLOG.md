# WORKLOG — the nine proposals from the August 16th run

Started 2026-08-16. The first daily run to ship a deck ended with nine proposals it could not
act on, because each needs a lane the `daily` actor does not own. The owner asked for all nine.

This session is `human`, on branch `maintenance/2026-08-16-proposals`, which matches no prefix
in `branch_actors` and is therefore treated as `human` by the checker. All thirteen target paths
were confirmed writable as `human` before any edit.

Delete this file when every wave is DONE.

---

## Carried forward from the previous WORKLOG, which this replaces

The written answer lane shipped. Tasks 1 to 8 all DONE, worker live at
`texas-ask.talon-sturgill.workers.dev`. Two wrap items were outstanding and both are resolved
here rather than lost:

- **W1, carry the claims trim back to the sibling's pack. CANNOT BE DONE FROM THIS REPO and is
  now closed as such.** The sibling is an Alaska repo. CLAUDE.md says the Alaska repos are
  REFERENCE ONLY and never written to from a session working here, and this session's GitHub
  scope is `talonsturgill/texasaidocket` alone. It needs a session opened against that repo. The
  measured finding it would carry over is recorded in the note below so it does not have to be
  re-derived.
- **W2, delete the file.** Superseded. The file is reused for this task instead.

**The finding W1 would have carried.** A third of the claims payload is plumbing the model never
uses. `verbatim_quote` 27.4%, `source_url` 16.2%, `source_title` 14.1%, `source_type` 2.8%,
`fetched` 2.1%. Only 95 distinct URLs across 234 claims, so most of the URL weight is one link
repeated. Dropping the bottom four took Texas from 61,070 to 45,482 tokens. Answers cite the
decision and never a raw URL, so the model never needed them.

---

## The shape of the whole thing

Six of the nine are ordinary defects. **Three of them are one fault**, and that fault is the
reason to do this in the order below rather than easiest first.

Proposals 8 and 9 are both about the ownership law not being enforced, and proposal 6 is about
the law contradicting the routine that has to obey it. The law is what makes every other gate
in this repo trustworthy, so it is repaired first and everything else lands on top of a checker
that actually runs.

## Waves

| # | wave | proposals | paths | status |
|---|---|---|---|---|
| A | the ownership law is not in force | 8, 9 | `ownership.yaml`, `guards.yml`, `guards_local.py`, `CLAUDE.md`, `.githooks/commit-msg`, `ownership_check.py`, Phase 0 and 17 | **DONE** |
| B | the law contradicts the routine | 6 | `ownership.yaml`, `SOURCES_FIELD_LOG.md` (new), `SOURCES_REGISTRY.md`, Phase 17 | **DONE** |
| C | a documented command destroys the record | 7 | `docket_build.py`, `prompts/daily_routine.md` | **DONE** |
| D | two carousel gates measure the wrong thing | 4, 5 | `copy_sync_check.py`, `aggregate_check.py` | **DONE** |
| E | the site says two things it does not mean | 1, 2 | `site_build.py`, `texas_map.py`, `docs/` rebuilt | **DONE** |
| F | the water page has no page check | 3 | `waterwatch_pagecheck.py` (new), `guards.yml`, Phase 7 | **DONE** |
| G | write the lessons down | all | `GATE_LESSONS.md` entries 19 to 22 | **DONE** |

## Decisions taken, with the reason

Recorded here so a later context does not relitigate them.

**Wave A, proposal 8. Add `claude/upgrade-` to `branch_actors` AND teach CI to read the stamp
per commit.** The run record framed these as alternatives and offered the choice. Both are
right and they fix different halves. The prefix keeps the narrow upgrade lane real, which is
the protection that stops a self-editing phase reaching the public record. Per-commit CI is
what makes the hook and the runner agree about what a lane is scoped to, which is the actual
disagreement. Doing only the prefix leaves the two checkers still measuring different things.

**Wave A, proposal 9. A missing local mechanism is a FAILURE, never a skip.** A skip is what a
check looks like when it is not needed. This is a check that cannot run, which is the opposite,
and it printed under a green banner while the ownership law was not in force for a whole run.

**Wave B, proposal 6. `ownership.yaml` moves, not the routine.** The routine's instruction is
correct on the merits: a source that behaved differently than the registry says is knowledge the
next run needs, and making a run drop it on the floor loses it. The narrow fix is a carve-out
for the one file, not opening `knowledge/shared/**`.

**Wave C, proposal 7. `promote()` refuses the destructive form outright.** Documentation that
says "do not pass `--out`" is not a guard. The command in the routine is fixed too, but the
code is what has to refuse.

## The rule this whole task is under

Never loosen a gate to make something pass. Every widening here carries a red case proving the
gate still fires, because a narrowing with no red case is indistinguishable from a deletion.
That is the lesson the August 16th run learned twice and it applies to its own repairs.
