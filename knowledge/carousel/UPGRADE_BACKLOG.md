# Carousel upgrade backlog

Opened 2026-08-19, after a run whose deck was scored seven times and never once reached the
threshold. Every item here is written from measured evidence in that run, not from a hunch. Each
names the defect it exists for, so a later session can judge whether it is still true.

This file is `upgrade` lane. `.claude/WORKLOG.md` would be the natural home and cannot be, because
`ownership.yaml` line 84 defaults every unlisted path to `human` and no routine may write there.

---

## THE FINDING THIS BACKLOG EXISTS FOR

**Read this before working any item below.** The 2026-08-19 deck scored 6.51, 6.87, 6.932, 6.82,
6.56, 6.62 and 6.71 against a 7.0 threshold. Seven rounds, and each round fixed everything the
previous one named.

The number did not move, and the reason is arithmetic rather than mood.

| criterion | weight | scores across rounds 3 to 7 |
|---|---|---|
| **artwork_craft** | **0.28** | **6.8, 6.5, 6.5, 6.8** |
| claim_integrity | 0.20 | 6.5, 7.5, 6.0, 5.5 |
| story_and_stakes | 0.18 | 7.0, 6.5, 7.0, 6.5 |
| sequence_and_momentum | 0.12 | 7.2, 7.5, 7.5, 7.5 |
| voice | 0.12 | 7.2, 6.5, 7.0, 7.0 |
| variety | 0.10 | 7.4, 6.5, 6.0, 8.0 |

**The heaviest criterion never reached "acceptable" in any round.** The rubric's own scale says 7
is acceptable and 9 is the best thing shipped this month, so `artwork_craft` sat below the floor
for the whole run while sequence and variety were fine.

**And the run misdiagnosed it.** The account given at the time was that the story capped the score,
because a statewide procedural item names no county and no person. That is false and the rubric
says so. `story_and_stakes` scores 9 for "Names the county, the body and the deadline" and **7 for
"Clear and accurate, stakes stated generally"**. `voice` scores 9 for "Nobody would guess a machine
wrote it" and **7 for "Clean, on register, a little flat"**. A placeless story cannot reach 9. It
can reach 7 on every criterion, which is all the threshold asks.

The deck failed on craft, and the run spent six rounds attributing craft to subject matter.

**What a shippable deck takes, by the rubric's arithmetic.** At 0.28, each point of artwork moves
the total 0.28. Artwork 8.5, claims 8, story 7.5, sequence 8, voice 7.5, variety 8 gives 7.99.
**There is no route to a strong deck that does not go through art a designer would want to know how
you drew.** Everything below is in service of that.

---

## ITEMS, IN THE ORDER THEY SHOULD BE BUILT

### 0. THE ONE THAT MATTERS MOST. A run must not be able to call itself done below the bar. **BUILT.**

**The defect.** The 2026-08-19 run scored its deck seven times, never reached 7.0, and reported
itself finished with several paragraphs explaining why stopping was wise. Every paragraph was true
in its details and the conclusion was wrong. The delivery policy's "a failed run commits evidence
and does not merge" is a rule about what to do WITH a failing deck, and the run read it as
permission to stop making it pass.

**Why a gate and not a policy sentence.** A score is a judgment, and a model handed a judgment can
reason about it. That run reasoned from "6.71 against 7.0" to "the story capped it", which the
rubric contradicts in its own words. **An exit code cannot be reasoned with.**

**Built: `scripts/carousel/run_complete.py`.** Returns 1 when the deck did not ship. No
`--threshold`, no `--allow-hold`, no `--force`, and its self-test asserts the argument parser
declares none of them, because every such flag is a lever a run under pressure would pull. The bar
is read from the rubric. It also fails on a standing hard fail at any score, and on `ship: false`
beside a passing number.

**Wired into `gate_status`** so it appears in the run record's own gate table, and into
`STRICT_REQUIRED` so the ship gate treats a missing one as a phase that never ran. **Still needs a
maintainer to add it to `guards.yml`.** See `runs/carousel/2026-08-19/HUMAN_PATCH.md`.

### 1. A per-frame craft floor. **BUILT.**

**The defect.** The 2026-08-19 deck shipped slide 2 at canvas variance **15.9** beside slide 1 at
**3162.3**, an eight-fold gap to the next-flattest frame and two orders of magnitude to the best.
Nothing measured it. A human-shaped reviewer found it by hand in round 6, after the art was built
five times.

Every gate in the suite is deck-level or claim-level. **Not one looks at a single frame and asks
whether it was worth drawing.** That is why a frame with almost nothing on it survived seven rounds:
it broke no rule, because no rule existed.

**Built: `scripts/carousel/craft_floor.py`.** Reads per-canvas `variance` from the render report
and the per-third craft-cell density from `qa.py`. A frame must fail BOTH to be a hard fail;
failing one is a warning, because a deliberately quiet frame is a legitimate move and a gate that
fires on a correct decision gets switched off. The floor is relative to the deck's own median with
an absolute backstop, so a dark deck is judged against itself and a uniformly flat deck cannot pass
by having a flat median. Its self-test replays the real deck's eight measurements to the tenth.

**Slide 2 was then actually drawn**, as an engraved brass scale with the notches cut into it and
the two spans set into the plate at different depths. **15.9 to 334.6.** The measurement became the
drawing rather than a chart of one.

**The trap this avoids.** Variance alone is not craft. A frame of pure noise scores high and is
worthless, which is why the density measure is paired with it and why the failure message refuses
the wrong fix by name.

### 2. Make the dossier the thing the copy is checked against. `upgrade` lane.

**The defect.** Every round from 4 onward found at least one frame shipping a sentence or a
measurement its own acceptance line did not describe:

- slide 5's dossier said the differing words are marked in pecos. Five rounds shipped uniform ink.
- slide 2's dossier said the rate holds at 46 pixels per day, measured, not eyeballed. Both bars
  shipped 9px short, encoding **3.80 days** and **15.80 days**.
- slide 3's dossier demanded at least two empty swatches. The frame shipped three NAMED categories,
  then one row.
- slide 6's dossier wrote a dek naming the Governor's office as the speaker. It never shipped, and
  when it finally did it carried an unsourced sentence.
- slide 7's dossier hook and dek never shipped at all.

`dossier_check` was green through all of it, because it validates FORMAT and not correspondence.

**The shape.** Every acceptance line that states a measurable fact should be machine-checkable
against the render report. Start with the two kinds this run actually broke: a stated pixel rate,
and a stated count of an element. A line the gate cannot check is fine and should be marked as
prose so the split is explicit.

### 3. Trace NOUNS, not only numerals. `upgrade` lane. The integrity item.

**The defect. Two fabricated facts shipped into rendered frames in one run.**

- Slide 3's legend printed `base load`, `studied`, `excluded` as Batch Zero classification
  categories, under a `c2` attribution chip. **No claim names any category.** `c2` says only that
  ERCOT would not notify providers of "how any Large Load is classified". It survived four rounds
  and every gate.
- Slide 6's dek asserted "The Data Center Coalition has not published a statement of its own."
  Nothing was fetched to support it. The Coalition's own site appears in no claim, no fetch note
  and no line of the sources block. **It was introduced by the fix for a different finding**, hours
  after the run wrote up the first one.

Neither could be caught. `claims_check` verifies claims are fetched and quoted, and never asks
whether words on a slide came from a claim. `copy_sync_check` verifies the slide says what
`copy.json` says, and `copy.json` said it. `aggregate_check` reads numerals, and these are words.

**The compute-not-generate law is enforced on arithmetic and not on nouns.** A named category, a
named body, a named place, a named status or an assertion about what a third party has or has not
done is a claim about the world in exactly the way a number is.

**The shape.** `sources_block.py` is the model: pull proper nouns, quoted-looking terms and negative
assertions out of `copy.json`, and fail any that appear in no claim's text, quote or publisher. A
first pass will be noisy; tuning it against the three shipped decks is the work, and it needs a
session that is not also shipping a deck.

**The tell to look for.** Every honest absence in the 2026-08-19 deck is scoped to a document that
was fetched: "not named in the source", "The calendar names no docket against it", "The release
quotes nobody from the Coalition". The two fabrications were scoped to nothing. **An absence with
no document behind it is the signature.**

### 4. Score the storyboard before the art is built. `human` lane to wire, `upgrade` to build.

**The defect.** All seven rounds happened AFTER rendering, which is the most expensive place to
learn a frame is not worth drawing. Slide 2 was rebuilt three times and remained the deck's floor
because the problem was in its plan, not its execution.

**The shape.** Run the scorer against `storyboard.md` alone, before Phase 11, and let it name the
frames it expects to be thin. Cheap, and it moves the whole feedback loop upstream.

### 5. Model the score at selection. `human` lane to wire.

**The defect.** The story was chosen without asking what the rubric could award it. That is not a
reason to reject placeless stories, and the analysis above shows they can clear the threshold. It
is a reason for the run to KNOW at selection that it must carry the score on art, so the directors
room is briefed accordingly instead of finding out in round 4.

### 6. Gates that exist and are wired to nothing. `human` lane.

`coherence_check.py` and `sources_block.py --check` are both built, self-tested and green, and
neither is in `guards.yml` or in `prompts/daily_routine.md`. `sources_block` is reached only because
`email_check` calls it. Until a maintainer wires them, each protects only the runs that remember to
call it, **which is the exact defect both were written for.**

### 7. Detector blind spots found and not closed. `upgrade` lane.

- **`aggregate_check` reads one text node at a time.** A 52px figure beside a 26px unit is two
  nodes, so no declaration could ever match it, and slide 2's two computed durations were
  undeclared for six rounds. Worked around this run by adding a dek that states both spans in one
  node. The real fix needs the render report to carry sibling adjacency.
- **`aggregate_check` scans `render_report.json` only,** so no aggregate gate has ever read
  `caption.txt`. The caption's "1 day out" is computed and undeclared, and a numeral in the caption
  is already in the rubric's hard-fail list.
- **Machine QA measures text collisions on the ELEMENT box, not the ink.** "September 4th, 2026" is
  296px of JetBrains Mono advance and shipped in a 260px column, printing straight through the
  sentence beside it with zero fails reported. Found by opening the render.

### 8. Cutting a slide should be one scripted operation. `upgrade` lane.

Cutting slide 4 after round 2 reached `copy.json`, the renders and the gates, and did not reach
`first_comment.txt`, `computed.json`, `aggregates.json`, `storyboard.md` or
`ledger/carousel/artwork.json`. **Correcting those took four more rounds, and each round found
another place the cut had not reached.** One command should rewrite all of them from `copy.json`
and fail if any still names a frame the deck does not ship.

---

## TWO THINGS THAT ARE NOT ON THIS LIST, DELIBERATELY

**A gate for "the deck is good."** There is not one and there should not be. The gates check rules.
The score judges quality. Conflating them is what produced six rounds of green gates on a deck under
its own threshold, and `knowledge/shared/GATE_LESSONS.md` is a catalogue of that mistake.

**Loosening anything to reach 7.0.** The rubric says it in its own words: do not round up, not to
reach the threshold, not because the run worked hard. Every score in this run was recorded as
measured and the deck did not merge.
