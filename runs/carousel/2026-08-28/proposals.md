# Proposals from the 2026-08-28 run

Each is out of the `daily` lane and is written down rather than made.

## 1. The caption ledger's exclusion lists are wrong in both directions, and a judge used them

`ledger/carousel/captions.json` stores `opening_moves_recent` and `structures_recent` as hand-kept
arrays. Computed from `entries`, the last six opening moves are `the plain question, the before and
after, the deadline, the quiet decision, the number that is wrong, the who`. The STORED array reads
`the two things, the plain question, the before and after, the deadline, the quiet decision, the
number that is wrong`. It carries a move that is seven runs back and omits yesterday's. The same is
true of the structures. The ledger's own `recent_lists_note` predicted this on 2026-08-20 and asked
for `caption_check.py` to DERIVE the lists from entries. It has not been done.

This run paid for it. The caption room was handed the computed lists and the critic judged against
the stored ones, so the two halves of one phase were working from different exclusion sets. The
critic's rejection was still right on other grounds, which is luck rather than a defence.

**The change.** Derive both lists in `scripts/carousel/caption_check.py` from `entries` and delete
the stored arrays, or make the gate fail when the stored arrays disagree with what entries compute.

## 2. `label_guard` fails closed on decks that print no act labels

It looks for an `ACTED` shape map in `compute.py`, a construction one earlier deck used to print a
place, an act and a claim id together. This deck prints source attributions instead, so the gate
reports "found no shape map in compute.py, so it is reading the wrong file" and exits 1. A gate that
refuses a deck for not using one particular construction is answering a question it was not given.
It is not in `guards.yml` and `shipped_check` is clean, so nothing broke, and a red exit code that
nobody can act on is how a run learns to stop reading exit codes.

**The change.** Report NOT APPLICABLE when the deck prints no labelled acts, and keep failing when a
map exists and a frame's label disagrees with it.

## 3. `docket_build.backlog` prints an exemption that no longer describes anything

`GEOGRAPHY_BACKLOG` is a dict of three item ids and every build prints one line per id
unconditionally. `tx-2026-0007` already carries `statewide: true`, so its line is false about the
current record, and no amount of work on the record can ever clear it because the printer never
looks at the item. A ratchet that cannot move is a decoration, which is the exact shape
`GATE_LESSONS.md` keeps recording.

**The change.** Print a backlog line only when the item still has the gap the exemption names, and
say out loud when an exemption has gone stale so it can be deleted.

## 4. `brand.yaml`'s `ends_with: engagement_question` collapses five closing moves into one

`CAPTION_CRAFT.md` offers five closes and tells the room to rotate them. `caption_check` enforces
`linkedin_post.ends_with: engagement_question`, so every caption must end on a question mark. Four
of the last four shipped captions therefore close by asking the question the decision leaves open,
because that is the only one of the five moves that is natively a question. The doctrine and the
config are pulling against each other and the config wins every time.

**The change.** Either drop `ends_with`, or rewrite the four other closes in CAPTION_CRAFT so each
has an interrogative form, and have the ledger record which was used.

## 5. The scout agents cannot write the file the routine tells them to write

`carousel-scout` is defined with `WebSearch`, `WebFetch` and `Read`. `prompts/daily_routine.md`
Phase 2 has them write `out/research/scout-<beat>.json`. All six scouts reported the same failure
unprompted and returned their findings in their replies instead, so nothing was lost. A step that
can never succeed is a step that silently does nothing.

**The change.** Either give the scout a write tool, or drop the instruction and have the showrunner
persist the replies.

## 6. `plan_render_check`'s palette regex cannot express this project's own token names

`PALETTE_DEF = re.compile(r"`([a-z][a-z ]*?) (#[0-9A-Fa-f]{6})`")`. The name pattern allows lower
case letters and spaces and nothing else, so `sky_predawn`, `rim_light`, `caliche_cap`,
`satin_spar` and `ledge_shadow` can never match, and the declared-colour check reported "the
storyboard defines no `name #HEX` palette" all run. Every palette this project has shipped uses
underscored token names.

**The change.** Allow an underscore in the token name.
