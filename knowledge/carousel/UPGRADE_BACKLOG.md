# Carousel upgrade backlog

Opened 2026-08-19, after a run whose deck was scored seven times and never once reached the
threshold. Every item here is written from measured evidence in that run, not from a hunch. Each
names the defect it exists for, so a later session can judge whether it is still true.

This file is `upgrade` lane, and it is where the backlog lives because a routine keeps no other
durable plan of its own. The general run state is `out/<date>/run_state.json`, which is scratch
and gitignored, so a lesson meant to outlive one run needs a committed home and this is it.

The sentence here used to point at a worklog under `.claude/` as the natural home. There is no
worklog now, at any address. Writing one there interrupted the owner on five consecutive
unattended runs, and CLAUDE.md carries the account under the heading saying the routine writes
none.

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

### 2. Make the dossier the thing the copy is checked against. **BUILT, and it found something worse.**

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

### 3. Trace NOUNS, not only numerals. **BUILT for absences, the half that shipped fabrications.**

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


---

## WHAT THE 2026-08-19 UPGRADE PASS ACTUALLY FOUND

Written after cataloguing 125 defects across all three shipped runs and auditing every gate for
what it cannot see. The ranking is by HOW MANY RUNS a root cause appears in, because a thing
that happened once is an incident and a thing that happened in all three is the machine.

### Item 2 is built, and the measurement under it is worse than the defect

`plan_render_check.py` compares the plan to the render. Palette tokens a dossier names must be
on the frame. A quoted string an acceptance item says the frame carries must be in the rendered
text. A quoted string it says appears nowhere must not be. Zero false positives on all eight
frames of the shipped deck, and it catches the 2026-08-16 slide 2 and 2026-08-19 slide 5 palette
defects.

Then it reported the thing worth knowing:

    0 of 46 acceptance items carry a machine-checkable assertion

**Not one.** Every item on the deck that scored 8.03 is true, careful, written before the render
and unverifiable by any machine, because they are prose ABOUT the frame rather than claims about
it. `the legend carries EXACTLY ONE row, reading no class stated` asserts something exact and
throws it away in the phrasing.

So this defect survived three runs of people actively looking for it because the gate was
missing AND there was nothing underneath to check. `SLIDE_DOSSIER_SPEC.md` now says how to write
a checkable item, and `gate_status` prints the ratio in every run record so the number has to go
up in public.

### Item 3 is built for absences

`absence_check.py`. Every honest absence in three decks names the document it looked in. Every
fabricated one names nothing. The gate asks whether the frame says WHERE IT LOOKED, which is the
one part of this a machine can see.

Calibrated: 7 of 7 scoped on 08-16, 5 of 6 on 08-18, 8 of 8 on 08-19. The single warning across
three shipped decks lands on 08-18 slide 7, the frame the run record documents as printing a
product name on the frame whose entire claim is that no product is named.

The proper-noun half of item 3 is NOT built. A first pass raised 33, 10 and 8 candidates per
deck, and the noise is sentence-initial capitals and all-caps design furniture. It needs a
session that is not also shipping a deck, exactly as this item said when it was written.

### NEW, and it outranks everything else on this page

**CI proves the checkers can go red and almost never runs them on the product.**

Of the fifteen carousel steps in `guards.yml`, THIRTEEN are `--self-test`. The only two that
touch a real artifact are `email_check --all` and `bespoke_check --slides-dir
examples/demo-deck/slides`, and that second one points at a demo deck rather than at anything
this project ever published.

`coherence_check`, `craft_floor`, `run_complete`, `sources_block`, `plan_render_check`,
`absence_check`, `qa.py` and `render.py` are in CI in no form at all. Six of those eight were
built BY these runs to catch defects these runs shipped.

A gate nothing runs protects only the runs that remember to call it, which is the exact defect
each was written for. This is item 6 and it is now the most valuable unbuilt thing here, because
it is the multiplier on every other gate in the suite.

### NEW. The scoring phase is one agent, and it never found a hard fail

`prompts/daily_routine.md` Phase 15 spawns one `carousel-scorer`. On 2026-08-19 that single
scorer ran seven rounds and found ZERO hard fails. A three-judge panel then ran five rounds and
found FOUR, two of which were fabrications that had already survived every gate and a pixel
review.

The panel also caught what a single grader structurally cannot: on three separate rounds all
three judges independently named the SAME defect, and twice that defect had been introduced by
the previous round's fix. One grader has no way to distinguish a real finding from its own taste.

### NEW. The two criteria nobody ever attacked

`story_and_stakes` and `voice` are 0.30 of the rubric between them. Across all five panel rounds,
from all three judges, NEITHER EVER REACHED 8.0, and every judge gave the same reason in nearly
the same words: no county, no town, no person, nothing a reader could not read as any state's
utility commission. The 2026-08-18 scorer wrote "Change three nouns and this is Ohio."

Twelve scoring rounds went into artwork. Zero went into this. It is the only finding that
appeared in every round of every panel and was never once attacked, and the reason is that the
run kept treating it as a property of the story rather than as a thing the selection and copy
phases could be asked for.

### NEW. A live bug, found by auditing rather than by a defect

`craft_floor.bands_of()` read three key names that `qa.py` has never written, so its WARN tier
was unreachable dead code and every thin frame was a hard fail on a condition that never ran.
Third instance in this repo of a consumer reading a key its producer does not write, after
`gate_status` and `email_check` both missed `weighted_score`.

The self-test had asserted that tier worked, and passed, on every run of the broken build,
because it built its own fixture with the key already in it. **A self-test that only ever reads
a fixture the consumer wrote for itself cannot see a broken contract.** Both new gates in this
pass assert against a real shipped artifact or against the producer's own source for that reason.

---

# 2026-08-21, the upgrade phase

Three landed, four filed. The three that landed are in `ledger/carousel/upgrades.json` with the
commands that prove each can go red. What follows is the part a later session needs and a ledger
entry cannot carry.

## The lesson these three share, and it belongs in GATE_LESSONS.md

`knowledge/shared/**` is `human` owned, so this cannot be written there. **Proposed as a new
GATE_LESSONS entry, in the maintainer's words to keep the file one voice.**

> **A checker's empty case and its clean case printed the same line.** `sources_block.py` was
> invoked as `--run <date>` for a whole run. There is no `--run`. Argparse matched an unambiguous
> prefix of `--run-dir`, the bare date became the path, the path did not exist, the gate found no
> printed claim ids, concluded that every printed id resolved, printed `sources block: clean` and
> exited 0, every time it was asked, including immediately after the deck gained two claim ids the
> published block did not list. `shipped_check` caught the real state one step later.
>
> **An exit code proves nothing about a checker that was handed the wrong path.** The repo's own
> rule is to run a gate by exit code rather than by reading its last line, and this arrives at the
> same failure from the direction the rule does not cover: the code was 0, the line was reassuring,
> and the gate had never been pointed at anything.
>
> **What to check instead.** Three separate things, because there were three separate silences.
> Turn off prefix matching, so a flag that does not exist is an error rather than a guess. Fail on
> an input path that does not exist. And fail on the empty result, because the empty set trivially
> satisfies any "every X resolves" assertion. Ask of any gate: what does it print when it was given
> nothing? If that is the same line it prints when the product is clean, it is not a gate.
>
> **And check the order of the guards.** The exemption here was keyed on the directory NAME and was
> tested first, so any path at all ending in the exempt date passed without a byte being read. The
> self-test asserting the exemption worked used `/nonexistent/2026-08-16` and proved the opposite of
> what it claimed. Existence is now tested before the exemption, and the self-test builds a real
> directory.

## Filed, not landed, and why each one stopped

**`aggregate_check` short-circuits a whole text node on `EXEMPT`, and the fix is measured and
ready.** `if EXEMPT.search(text): return []` runs before any detection, so one bill number or bare
year switches aggregate detection off for a whole sentence. The fix is four lines: blank the exempt
spans with spaces, which preserves every offset `is_slide_counter` reads, and scan what is left.

It did not land TODAY for one reason and the reason expires tomorrow. Replayed across every shipped
deck it surfaces six aggregates nothing declares, and five of them are on **2026-08-21, which is
the newest deck**, so `shipped_check` scopes them fatal and CI goes red on an artifact this lane
does not own and cannot amend.

    2026-08-18  slide 8  "nine campuses"
    2026-08-21  slide 1  "100,000 driverless miles"
    2026-08-21  slide 3  "35 driverless trucks"
    2026-08-21  slide 5  "100,000 riders"
    2026-08-21  slide 6  "392 days"  and  "392 days after the Dallas"

Every one is a real aggregate that should have been declared, and "392 days" is the one this run
tried to declare and could not, because the gate refused it as undetected. **The moment 2026-08-21
stops being the newest deck those five become notes rather than failures**, and the fix costs
nothing. The next upgrade phase should land it first, before it writes anything else, and should
re-run the measurement above rather than trusting this list.

**`texan_check`'s DATE regex is case sensitive while its ACTION regex is not.** `DATE` is compiled
without `re.I` and `ACTION` with it, so a closing frame setting its date in caps reads as having no
date. This run's slide 9 carries `AUGUST 25TH, 2026` in white mono on the red plate, the most
prominent thing on the frame, and the gate reported `next step NO`. Add `re.I` and a self-test case
asserting an all caps closing date is seen. This is GATE_LESSONS 35 exactly, one file over: a rule
written against a rendered form by somebody who did not go and read the renderer.

**The deck builder should delete `out/<date>/slides/` before it writes.** `_footer_fit` refused this
run's build and the previous build's HTML was still on disk, so the renderer rendered it. A refused
build must leave nothing behind to render. The builder is the run's own scratch and not this lane's.

## What the `DECLARED` check in `plan_render_check` cannot see, stated so nobody infers a guarantee

It compares only strings the plan DECLARES under `type:`. The 2026-08-21 defect had two halves.
Slide 4's dek is declared, so it is caught. Slide 9's source line is declared nowhere, so a byline
filing a TxDOT claim under the Legislature is still invisible to it. The natural next move is for
`type:` to declare the source line too, which costs the dossier one key and closes the other half.

## Why `--run` was typed at all, which is the finding under the finding

`absence_check.py` takes `--date` for `out/<date>/` and `--run` for a shipped run under
`runs/carousel/`. `sources_block.py` takes `--date` and `--run-dir`, and `--run-dir` is a PATH
rather than a date. `shipped_check.py` takes `--run <date>`. Three sibling gates, three meanings
for the same idea, and one of them silently accepted the neighbour's flag as a prefix.

The operator error was correct behaviour applied to the wrong gate. `allow_abbrev=False` turns
that into an error message, which is the fix that ends the story at the command line, and it
leaves the real problem standing.

**Proposed, in lane, bounded, for a later phase.** One vocabulary across `scripts/carousel/**`:
`--date` means `out/<date>/` and `--run` means `runs/carousel/<date>/`, everywhere, with a check
that walks every script in the directory, parses its `add_argument` calls, and fails on a gate
that spells either of those two differently. That check can go red: rename one flag and watch it.
Do it in the same pass as `allow_abbrev=False` on every parser in the directory, because a
uniform vocabulary with prefix matching still on is a vocabulary with synonyms nobody chose.

## Frontier scan, 2026-08-21. Focus area: verifying that a sentence says what its source says

This run's two hard fails, three panels apart, are one defect. The cover asserted an absence the
record had declined to establish. Slide 7 said DPS PUBLISHES first responder plans where its cited
claim says the page TAKES them. In both cases the composition chose the word and the fact was
fitted to it afterwards, and every gate stayed green, because a gate can check that a claim id
resolves and cannot check that the sentence above it says what the claim says.

Ten searches. Two findings worth acting on and one worth refusing.

**Refused: an NLI model as a gate.** The 2026 literature is settled on decomposing generated text
into atomic claims and running an entailment model against source chunks, and it is the right
answer for a system that can carry the dependency. This one cannot. CI installs `pyyaml` and
nothing else, and GATE_LESSONS 15 is the entry about a gate that passed fifteen times locally and
failed on the first push for exactly that. A gate whose verdict is a model's is also a gate whose
verdict moves when the model does, on a project whose whole argument is that its numbers are
recomputable from the same inputs. Not this.

**Worth acting on, and it is nearly free. Evidence ABSENCE is not evidence INSUFFICIENCY.** The
fact-verification literature separates them and this repo currently does not. `absence_check` asks
whether an absence names the document it is scoped to, which is the right first question and stops
one step short. Panel 6's hard fail was an absence scoped to a page **that never rendered**, and
the run's own rejected list said so in writing. So the second question is mechanical and the data
to answer it is already in `claims.json`: an absence may not be scoped to a document this run
failed to retrieve. A page that returned 403, or a query that never rendered, produces
insufficiency, and publishing that as absence is the one error this deck's whole subject is about.
**Bounded, in lane, and it can go red on a real artifact: replay panel 6's cover against this
run's own rejected list.**

**Worth acting on, cheaply, on the verb.** `noun_trace` does the positive half for named things and
warns rather than fails, which is the right register. The same shape over the main verb attached to
a named entity would have printed one line saying that PUBLISHES appears in no claim cited on slide
7, where the claims say TAKES and ACCEPTS. Not a truth test and not a phrase list of banned words,
which GATE_LESSONS 46 is the argument against. A LIST of the verbs a frame asserts that no cited
claim uses, for a human to read in seconds. The literature's own note on lexical methods is that
they cannot tell a paraphrase from a contradiction, which is precisely why this warns and never
fails.

**And the stale build half has a plain answer outside this repo.** Build systems treat this as
settled: a failed build cleans its output tree unconditionally, and a cached failure is replayed as
a failure rather than resolved from whatever is on disk. That is proposal 17 in the run record,
stated by everybody else who has hit it.
