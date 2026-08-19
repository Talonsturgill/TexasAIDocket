# WORKLOG: carousel root causes, opened 2026-08-19

The owner's brief: three runs are on the record now. Find the REPEAT OFFENDERS that keep
holding the deck under the eval gates, attack the root causes rather than the incidents, and
fill the biggest holes. Scope is the CAROUSEL POST only. The reasoning given is the one that
matters: **if the agents can wow the judges, they can wow the humans.**

This file exists because the task is too large for one context. Resume from the wave table.

## THE EVIDENCE THIS IS BUILT ON

Twelve independent judge reports from 2026-08-19 (four rounds, three judges), the score
history of all three runs, every RUN_RECORD, GATE_LESSONS.md, UPGRADE_BACKLOG.md,
upgrades.json and instincts.json, plus a full audit of what each gate can and cannot see.

Score history, and it is the shape of the problem rather than the size of it:

| run | rounds | scores | shipped at |
|---|---|---|---|
| 2026-08-16 | not recorded per round | | 7.0 |
| 2026-08-18 | not recorded per round | | 7.01 |
| 2026-08-19 | 12 | 6.51 6.87 6.93 6.82 6.56 6.62 6.71 / 6.53 7.14 7.01 7.44 8.03 | 8.03 |

Two decks shipped within 0.01 of the bar and the third took twelve rounds. That is not three
stories of differing quality. That is a machine with no way to find its own defects before a
judge does.

## WAVE TABLE

| wave | what | status |
|---|---|---|
| 0 | Evidence: defect catalogue, gate blind-spot map, rubric extract | DONE |
| 1 | Rank repeat offenders by rounds-lost, pick the root causes worth code | DONE |
| 2 | Build the gates that close them, each with a self-test that replays the REAL defect | DONE, PR #104 |
| 3 | Wire into guards.yml + gate_status + daily_routine, prove red then green | gate_status DONE. guards.yml is human lane, next |
| 4 | Doctrine: fold the durable lessons into the knowledge base | |

## RULES THIS WORK OBEYS

- A gate, not a paragraph. The owner's standing correction: prose is not a boundary.
- Every gate's self-test must replay a REAL historical defect from a named run, not a
  synthetic case. A self-test that only proves the checker's logic is how a green suite
  shipped the wrong URL on three decks.
- Prove the gate goes RED on the historical artifact before believing it green on today's.
- No gate may be added without also being wired into guards.yml. UPGRADE_BACKLOG item 6 is
  a list of gates that exist and are connected to nothing.


---

# WAVE 1: THE ANALYSIS

125 defects catalogued across the three runs. Ranked by how many RUNS each root cause appears
in, because a thing that happened once is an incident and a thing that happened in all three is
the machine.

## THE REPEAT OFFENDERS, RANKED

### RC-A. The plan is never checked against the render. THREE RUNS, ~15 incidents.

08-16: slide 2's declared palette never drawn, slide 8's declared focal never drawn, two
acceptance items satisfiable by rendering NOTHING. 08-18: all five of slide 5's acceptance items
passed while the frame was a Gantt chart that contradicted its own caption; slide 9 printed a
word its first acceptance line forbids. 08-19: five frames shipped against their own lines, the
worst being slide 5's pecos marking, which is the acceptance line of the frame the whole deck
turns on and shipped as uniform ink for five passes.

**`dossier_check` validates FORMAT and never CORRESPONDENCE.** It proves a plan EXISTS. A pixel
critic then grades each frame against that plan, so a stale or unexecuted plan passes every
review after it. This is UPGRADE_BACKLOG item 2, written after run 1, never built.

### RC-B. Nouns are not traced. THREE RUNS, ~10 incidents.

08-16: "SB 6" in no quote, a county judge renamed "ITS EXECUTIVE", a hook reading "Four
signatures" over four rows carrying no signature. 08-18: fabricated Gantt start times, "MAP" on
the frame whose claim is that no product is named, a filled dot for a claim with no coordinates.
08-19: three invented Batch Zero categories under a c2 attribution chip that survived four
passes and every gate; an invented Coalition statement introduced BY THE FIX for the first one.

**The compute-not-generate law is enforced on numerals and on nothing else.** `claims_check`
proves claims are fetched, `copy_sync_check` proves the slide says what copy.json says and the
copy said it, `aggregate_check` reads numerals. Nothing asks whether a NOUN came from a source.
UPGRADE_BACKLOG item 3, never built.

### RC-C. CI proves the checkers can go red and almost never runs them on the product.

VERIFIED BY HAND. Of 15 carousel steps in guards.yml, 13 are `--self-test`. The only two that
touch real artifacts are `email_check --all` and `bespoke_check --slides-dir
examples/demo-deck/slides`, and that second one points at a DEMO DECK, not at anything shipped.

`coherence_check`, `craft_floor`, `run_complete`, `sources_block`, `qa.py` and `render.py` are
in CI in no form at all. Four of those six were built BY these runs to catch defects these runs
shipped. **A gate nothing runs is a gate that protects the runs that remember to call it**,
which is the exact defect each was written for. UPGRADE_BACKLOG item 6.

### RC-D. Machine QA measures boxes, and defects arrive as ink. TWO RUNS, 4 incidents.

08-18 slide 9: a 2px table border struck a footnote and QA reported PASS, zero fails, zero
warns. A gate was built for it, `rule_strikes`. 08-19 slide 5: a CANVAS-drawn sheet edge ran
through the last line of the same kind of paragraph, twice, and the new gate did not see it
because it enumerates DOM rules. 08-19 also shipped 296px of type in a 260px column with zero
fails, because the collision detector measures the ELEMENT and the defect was the INK.

**Every fix here has enumerated one more kind of thing that can cross a word.** The class is
"anything drawn", and canvas is the half the DOM cannot describe.

### RC-E. A fix is where the next defect comes from. TWO RUNS, 4 incidents.

08-18: a dashed leader added to satisfy the dead-lower-zone gate drew a causal accusation.
08-19: the slide 6 dek fabrication was written while fixing slide 3; the round-10 panel found a
defect round 9's fix created; the round-11 hard fail was created by round 10's fix.

Judge A named the mechanism in one line: **a fix with no gate behind it always looks like this.**

### RC-F. One scorer, and the run grades itself.

Seven single-scorer rounds on 08-19 found ZERO hard fails. Five panel rounds found FOUR. The
routine spawns exactly one scorer (daily_routine.md line 741). `run_complete` then reads a
score.json the graded run wrote.

### RC-G. A correction reaches some of the places a fact lives. TWO RUNS.

Cutting one slide on 08-19 reached copy.json, the renders and the gates, and did not reach
first_comment.txt, computed.json, aggregates.json, storyboard.md or artwork.json. It took three
further sweeps and a judge each time. 08-16's variety ledgers went stale the same way and
variety scored lowest of six criteria.

### RC-H. Two frames of one deck, and neither ever cleared the bar.

story_and_stakes and voice are 0.30 of the rubric between them. Across all five panel rounds on
08-19, from all three judges, NEITHER EVER REACHED 8.0, and every judge gave the same reason in
almost the same words: no county, no town, no person, nothing a Texan could not read as any
state's utility commission. 08-18's scorer wrote "Change three nouns and this is Ohio."

Nothing was ever built for this. It is the only finding that appeared in every round of every
panel and was never once attacked.

## LIVE BUG FOUND WHILE AUDITING

**`craft_floor.bands_of()` reads keys that do not exist.** It looks for `bands` / `thirds` /
`craft_bands` in each qa slide record. Verified against the shipped machine_qa.json: the only
keys are `file`, `fails`, `warns`. So `bands` is ALWAYS empty, `lopsided` is ALWAYS False, and
the branch `thin and (lopsided or not bands)` makes every thin frame a HARD FAIL. The documented
WARN tier for a deliberately quiet frame is unreachable dead code.

`qa.py`'s `frame_balance()` computes those bands and throws them away into a message string.

This gate was written in this run, by me, to protect against a frame not worth drawing, and it
has been making a decision on data it never had. Same shape as the `weighted_score` lookup miss
in gate_status and email_check: **a consumer reading a key its producer does not write.** Third
instance in this repo.


---

# WAVE 2, BUILT. PR #104

| what | closes | proof it can go red |
|---|---|---|
| `qa.py` persists per-third bands | a live bug | removing the write turns craft_floor's self-test red |
| `craft_floor` asserts the PRODUCER writes what it reads | RC live bug | shown red then green |
| `plan_render_check.py` | RC-A, 3 runs ~15 incidents | replays the 08-19 pecos defect |
| `SLIDE_DOSSIER_SPEC` checkable-item rule + focal law | RC-A's other half | n/a, doctrine |
| `absence_check.py` | RC-B, 3 runs ~10 fabrications | replays the 08-19 Coalition fabrication |
| `shipped_check.py` | RC-C, the multiplier | self-test asserts every gate is REACHABLE |
| `gate_status` rows | visibility | the 0-of-46 ratio now prints in every run record |

## THE NUMBER THAT MATTERS MOST

**0 of 46 acceptance items on the 8.03 deck carry a machine-checkable assertion.**

The plan-versus-render defect survived three runs of people actively hunting it because the gate
was missing AND there was nothing underneath to check. Fixing the gate alone would have shipped
a green check over an empty test.

## STILL OPEN, IN PRIORITY ORDER

1. **guards.yml wiring.** Human lane. Until `shipped_check` is in CI it is one more gate that
   protects only the runs that remember to call it, which is the defect it exists for.
2. **The panel.** Phase 15 spawns ONE scorer. Seven single-scorer rounds found zero hard fails;
   five panel rounds found four. Three judges also caught what one structurally cannot: on three
   rounds all three independently named the same defect, and twice that defect had been
   introduced by the previous round's fix.
3. **story_and_stakes and voice.** 0.30 of the rubric, never reached 8.0 in any round from any
   judge across the whole run, same reason every time, and nothing has ever been built for it.
   Twelve rounds went into artwork and zero went into this.
4. **Proper-noun tracing.** The other half of RC-B. A first pass raised 33, 10 and 8 candidates
   per deck; the noise is sentence-initial capitals and all-caps design furniture. Needs a
   session that is not also shipping a deck.
5. **Canvas geometry crossing text.** RC-D. Every fix so far has enumerated one more kind of
   thing that can cross a word. The class is "anything drawn", and canvas is the half the DOM
   cannot describe.
