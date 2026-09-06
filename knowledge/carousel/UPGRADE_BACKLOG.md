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

---

## 2026-09-03, deck no. 14. The two lessons this run's upgrades belong to

`knowledge/shared/GATE_LESSONS.md` is `human` lane, measured with
`ownership_check.py --actor upgrade --files` rather than assumed, so these are written here and the
carry across is a proposal in `ledger/carousel/upgrades.json`. Both are argued from the shipped
ledgers rather than from a hunch, and both have a gate now.

### A checker that verifies a rule's DERIVATION has said nothing about whether the rule was OBEYED

`ledger_check` has three checks on `captions.json`'s exclusion lists. Every recorded move is a name
`CAPTION_CRAFT.md` carries, the three `*_recent` lists equal what the entries derive, and no date
appears twice. All three are correct and all three are about the LIST.

The lists exist for one reason, which is to be handed to the caption room BEFORE it writes so the
room cannot repeat itself. Nothing ever asked whether the room obeyed them. Replayed against the
ledger as it stood, **eight shipped entries used a move their own window covered**, and this gate
was green on every one of them.

- 2026-08-30 opening move `the object`, one run after 2026-08-29 shipped `the object`
- 2026-08-30 structure `Zoom out`, one run after 2026-08-29 shipped `Zoom out`
- 2026-08-26 through 2026-09-02, six entries, all closing the same way

The tell is that the gate's docstring describes the lists as "what the caption room is handed
BEFORE it writes" and every assertion in the file is about how the lists were computed. **When a
gate's own prose says what a thing is FOR, read the assertions and ask whether any of them tests
that.** Derivation is the easy question, and a checker that answers the easy one reports it as
though it answered the hard one.

**What to check instead.** For any derived exclusion, allowlist or blocklist, assert the CONSUMER
side as well as the producer side. `exclusion_violations` walks each entry against its own window
and the self-test replays it against the real `captions.json`, not only against fixtures, because a
fixture written beside a detector agrees with it.

### A hard form constraint on one surface silently deletes options from a menu stated on another

`config/brand.yaml` sets `linkedin_post.ends_with: engagement_question`. `caption_check` began
enforcing it on 2026-08-25. `CAPTION_CRAFT.md` lists five closing moves and four of them are
declarative, so from that day the doctrine was telling the caption room to rotate through four
closes the gate refuses.

**Seven consecutive captions closed the same way and nothing reported it.** The variety ledger
recorded `closing_moves_recent` faithfully the whole time, which is the part worth sitting with: a
ledger that records what was USED without recording what was AVAILABLE reads healthy while one
option is the only legal one. `ConInstruct` (arXiv 2511.14342) measures exactly this behaviour in
models and finds detection is strong while notification is nearly absent. They resolve a conflict
silently. So did this room, seven times, and each run rediscovered the reason from scratch.

**What to check instead.** On the day a hard form rule is added to any surface, read the doctrine
that surface's writers are handed and say what the rule COSTS that menu. Where an option cannot
survive, mark it unavailable in the doctrine rather than leaving a name on a list, and make the
enforcing gate's message name the collision so the next writer reads the resolution instead of
inferring it. The gate here was right seven times and told nobody anything it did not already know.

### And the two proposals this run could not make

- **The source vocabulary is stated twice.** `claims_check.SOURCE_TYPES` carries
  `secondary_reported` and `data`. `docket_build.SOURCE_TYPES` carries `journalism` and no `data`.
  Measured 2026-09-03 across thirteen shipped decks and the record, 71 deck claims against 80
  record claims for the same concept under two names, and 5 deck claims the record has no word for
  at all. `scripts/site/**` is another lane, and a one sided reconciliation would be a third
  statement of one vocabulary, so `claims_check` DECLARES the divergence and fails on an
  undeclared one instead. The declaration reports itself stale the day the record adopts the word,
  which is how whoever makes the real fix finds the other half.
- **`captions.json`'s `_spec` still says two exclusions are handed to the room.** The closing
  substance is now enforced and is not on that string. `ledger/carousel/captions.json` is `daily`
  lane.

### The ship step says "copy artifacts" and three of fifteen decks archived no slide HTML

`prompts/daily_routine.md` step 1 of the ship phase reads "Copy artifacts to
`runs/carousel/<date>/`, archiving `prompts/NEXT_RUN.md` if it existed". Nothing on that line
names `out/<date>/slides/*.html`, so what each run copies is what that run happened to think of.
Measured 2026-09-03 across fifteen shipped decks, twelve kept `slides/` and three did not, today's
included.

The cost was invisible until 2026-09-03 because nothing read those files. `label_guard` tests a
LABEL BESIDE A CLAIM ID, and the only surface carrying that adjacency is the rendered frame. A
`copy.json` keeps `labels` and `claims` in separate fields, so a deck with no archived slide HTML
cannot be checked at all. That is now reported honestly rather than passed: the gate raises
`Absent`, exits 2, writes `{"status": "absent"}`, `gate_status` renders ABSENT and `--strict`
refuses to ship on one. So the gap is visible now, on every future run, which is the half this
run could make.

**The proposal.** Name the file on the line. Step 1 becomes an enumerated list that includes
`slides/*.html` alongside the renders, `copy.json`, `claims.json`, `compute.py`, `figures.json`
and the receipts, so a run copies a stated set rather than a remembered one.

**Why this run did not make it.** `prompts/daily_routine.md` is `human` lane in `ownership.yaml`,
with the note that a run rewriting the instructions it is currently executing is how a machine
drifts without anyone noticing. This run is executing it. The lane is the answer and the gate is
already reporting the defect in the meantime.

---

## 2026-09-04, deck no. 15. What three judges found and no gate could

Three upgrades landed and are in `ledger/carousel/upgrades.json` with the commands that prove each
can go red. What follows is the part a later session needs and a ledger entry cannot carry.

### The lesson these belong in GATE_LESSONS.md, and why it is written here instead

`knowledge/shared/**` is `human` lane, measured with `ownership_check.py --actor upgrade --files`
rather than assumed. **Proposed as a new entry, in the maintainer's words to keep the file one
voice.**

> **A gate that checks WHERE a string sits cannot check WHAT it claims to be.**
>
> Carousel 15 printed five strings dressed as somebody else's words that no claim carries.
> `IT DID JUST THAT` on a plate under the heading STATED, in no quote at all. `HIGH QUALITY
> IMAGES`, which dropped `facial` out of c9's `high-quality facial images` in a verbatim slot.
> `MARYLAND, ROOFED` and `PROGRESO, OPEN SKY`, two physical assertions about real places, the
> second contradicting the deck's own frame 1. `CARRIL DE CAPTURA` and `CARRIL DE EXCLUSION`,
> Spanish sign text on a frame whose whole subject is what the signs said, where the source says
> only that the signs were in English and Spanish.
>
> Two gates exist for this class and both passed, each answering its own question correctly.
> `label_guard` tests a label BESIDE A CLAIM ID and its window is a few words wide, so a plate in
> the art region with the citation chip in the footer was never in it. `noun_trace` warns on
> named THINGS, and `IT DID JUST THAT` names no thing. It is a sentence, and its whole defect is
> the costume it wears.
>
> **What to check instead.** Hold the string to the WORDS of the claim it is filed under. That
> needs a declaration, because a machine looking at a frame cannot tell a quotation from a label:
> a deck legitimately prints `SELECTION`, `BTS BORDER DATA` and `01 / 09`. An auto-discovering
> draft was replayed across all fifteen shipped decks and fired on the REPAIRED deck of
> 2026-09-04, on two correct authored labels, which is how a gate earns being switched off.
>
> **And the half that needs no declaration is worth keeping separately.** Where a frame prints one
> label that IS a literal fragment of a quote, every other label in the same RENDERED STYLE on
> that frame is standing in the same slot. Measured across fifteen decks that discovery names
> three groups, at least two of them legitimate, so it prints a list and decides nothing. On the
> deck the panel saw it names both frame 8 fabrications with no declaration anywhere. A detector
> too noisy to fail on is not too noisy to read.

### A second lesson, from the value arc

> **Every deck missed its own planned value arc and every one of them RECORDED the miss instead of
> preventing it.** 2026-08-29 planned near 32 and measured 15.6. 2026-08-30 planned 40 and
> measured 21.2. 2026-09-02 planned 30 and measured 20.4. Carousel 15's first render planned 24
> and measured 6.3, eight of nine frames between 4.5 and 10.1, and it was found by the showrunner
> writing a one-off `measure.py` AFTER three judges had been spawned on it.
>
> The artwork ledger has a `deck_median_L` field and it was always filled in honestly. **A ledger
> that records an outcome is not a gate that refuses one**, and four consecutive runs wrote down
> the same miss without anything reading the plan beside it.
>
> **What to check instead.** Where a plan states a measurable target, the gate that stands before
> the expensive step measures it. `panel_ready` now parses the arc out of the storyboard and
> refuses to declare the deck scorable more than one Munsell value step from its own plan. The
> tolerance is external on purpose: adjacent Munsell values are one plainly visible lightness step
> apart and sit about 10 L* apart at every end of the scale, so it can never be re-derived
> downward off our own decks.

### Filed, not landed, and why each one stopped

**`verbatim_check` and the two gates beside it are in `guards.yml` in no form.** The backlog's
own NEW item above says thirteen of fifteen carousel steps in CI are `--self-test` and only two
touch a real artifact. `verbatim_check.py --self-test` belongs on that list, and its calibration
block reads every shipped deck, so the CI step is the one that catches a parser going quiet.
`.github/workflows/**` is `human` lane. Proposal filed in the ledger.

**The routine does not call `verbatim_check` anywhere.** `prompts/daily_routine.md` is `human`
lane and this run is executing it, so the gate is reachable today only through the run record's
gate table, where `gate_status` now renders a `verbatim` row. That row is WARN rather than PASS on
a deck that declares nothing, so the gap is visible on every future run in the meantime. The two
places it should be called are Phase 12, beside `label_guard`, and the ship gate.

**`dedupe_check`'s standing notes are printed and nothing requires them to be read.** The honest
next move is not a gate. It is one line in the selection phase telling the run to quote the notes
it read into the run record, so a run that ignored one has to say it ignored it. `human` lane.

**`shipped_check --self-test` is red at HEAD and it is not this phase's.** It reports that the
newest deck did not run `ledgers`, `construction` or `completion`, which is a fact about
`runs/carousel/2026-09-04/` rather than about any gate. That directory is `daily` lane. Verified
by stashing this phase's files and running it again at HEAD, where it fails identically.

### Frontier scan, 2026-09-04. Focus area: holding generated text to its own source span

Rotated deliberately away from 08-21's entailment question, which reached the right answer and
the wrong dependency. The finding worth acting on is narrower and needs no model.

**Quotation integrity is a span problem, not a similarity problem.** The literature on quotation
verification separates two errors that a similarity score cannot: a quotation that does not appear
in the source at all, and a quotation that appears with a word removed that changes its scope.
`HIGH QUALITY IMAGES` is the second kind and it is the harder one, because every word in it is in
the source and in that order. **A substring test over a normalised span catches it and a bag of
words does not**, which is why the check landed as a literal substring rather than as a token
overlap ratio, and why the normalisation is loose on punctuation and strict on words.

**Refused again, for the reason 08-21 gave.** Nothing here installs an entailment model, CI
installs `pyyaml` and nothing else, and a verdict that moves when a model moves is not a verdict
this project can publish. GATE_LESSONS 15.

### Two proposals from round 3 of the 2026-09-04 panel, NOT BUILT this run

Filed by the showrunner into this lane rather than written by it, because this file is `upgrade`
lane and the run should not write behind the phase that owns it. **Neither was implemented.** This
phase had already landed its three, and the ceiling is three, so a fourth would have shipped
without the calibration the other three each got. Both carry enough measured evidence to be built
in one pass by the next upgrade phase, and both should be verified against a real deck before they
are believed.

#### A. QUANTIFIERS SHOULD BE EXTRACTED, NOT AUTHORED

**The defect, three rounds and three locations.** `quantifier_check` reads
`out/<date>/quantifiers.json`, which is HAND WRITTEN, so it only ever sees the universals somebody
remembered to write down.

- **Round 3.** `The way in is counted every month.` in 60pt type on frame 7. An unqualified
  universal over a set of months that this run's own rejected-claims list refutes in writing. The
  register held two entries and had never seen it.
- **Round 2.** The plate `PROGRESO, NO ROOM OPEN`.
- **Round 1.** Frame 9's `This test opens no comment period and no hearing`.

One blind spot, found three times, each time by a judge. **This is GATE_LESSONS 39 exactly**, one
gate over: `copy_sync_check` selected what to examine by matching KEY NAMES against a list and was
blind to twelve of one deck's nineteen keys. An allowlist fails silent, because a thing nobody
thought of is a thing nobody checks and nothing reports the omission. A hand written register is an
allowlist wearing a different coat, and the run authoring it is the same run whose universals it is
supposed to catch.

**The shape.** The gate extracts every universal and absence word mechanically, `every`, `only`,
`no`, `none`, `each`, `never`, `all`, `always`, from ALL nine hooks, all nine deks, every on-frame
plate in `copy.json`, the caption and the first comment, and refuses the build until each extracted
one names the set it quantifies and the claim that establishes it. **The authored file becomes the
ANSWER sheet rather than the question sheet**, which is the whole of the change.

**Verify it against the defect before believing it.** Replay this run's frame 7 hook against this
run's `quantifiers.json` and watch it go red, then add the scoping and watch it go green. And
measure the extraction across all fifteen shipped decks before setting any severity: a first pass
will be noisy, `no` is a common word, and the tuning is the work. Warn on what it cannot scope and
fail on what a register explicitly contradicts, if the noise floor turns out high.

#### B. A DECLARED FOCAL MUST EXIST IN THE PICTURE

**The defect.** Frame 4's dossier declared its focal as *"the near volume's lit soffit, the only
closed modeled surface in the frame and the largest light area on it"* and the render contained no
soffit at all. Two bare hairlines, a small far portal and a floor wash. It survived three scoring
rounds, a green `machine_qa` and a full pixel review, because nothing in the suite reads a
dossier's focal against the pixels.

That is the FOCAL LAW in `SLIDE_DOSSIER_SPEC.md` failing in a new place. The law was written after
a judge counted the frames whose declared focal actually won the eye and got two of eight, and
every one of those was a focal that was a LINE rather than an AREA. This is worse: a focal that is
not in the drawing at all.

**The shape, in the craft judge's own words.** A gate that reads each dossier's declared focal,
resolves it to a region in the rendered PNG, and proves that region exists and carries the frame's
stated value extreme. `dossier_check` already parses `focal` and `value_structure` and already
compares them to each other, so this is the same comparison taken one step further, to the picture.

**The hard part is resolving prose to a region, and the honest first cut is narrower.** Prove that
the frame's brightest connected region of at least some stated size sits on the SIDE and LEVEL the
focal names, using the axis vocabulary `dossier_check.light_disagreement()` already has. That is
mechanical, it needs no new vocabulary, and it would have caught frame 4, whose brightest area is a
floor wash at the bottom while the declared focal is a soffit above.

**Two traps this one has to avoid, both already paid for here.** A size floor typed into the file
is a threshold with no argument behind it, so derive it from the canvas rather than typing a pixel
count, or take it from an external standard the way the value arc tolerance takes one Munsell step.
And a gate that misreports costs more than one that misses, because the run then hunts for
something that was never there, so run it across every shipped deck with PNGs before wiring it, and
make it WARN wherever the prose does not resolve to an axis rather than guessing one.

## 2026-09-04, found by a review bot on PR 266, not by this run

### `guards_local --verdict` has no concurrency guard, and a run believed it did

**What it actually checks.** `read_verdict()` refuses a missing file, a verdict written by another
runner version, a verdict whose tree state does not match this tree, a verdict from a `--fast` or
`--only` invocation, and one whose steps did not all pass. Every branch is a refusal with a reason
and there is no path that returns 0 on a partial file. That is the design and it holds.

**What it does not check.** There is **no lock, no pid and no active-run marker** anywhere in the
verdict. Each run deletes `out/gates/verdict.json` at startup and writes it once at the end by
atomic rename. So if run A finishes and writes a green verdict while run B is still executing on
the same tree, `--verdict` reads A's file, finds the tree state matching and every step passed, and
**exits 0 while a suite is still running.**

**How it surfaced.** The 2026-09-04 run put three suites on one tree at once, through a separate
mistake, and then wrote in its own run record that this was "precisely the state `--verdict` exists
to refuse". It is not, and a review bot on PR 266 caught the sentence before it merged. The run
record now says the opposite. This is the shape `CLAUDE.md` warns about twice over: a wrong
explanation is worse than none, because the next session inherits it and stops looking.

**The proposal.** Write the running pid and a monotonically increasing run id into
`out/gates/running.json` at startup and remove it on exit, then have `read_verdict()` refuse while
that file names a live process. Cheap, and it closes the hole in the direction that fails safe.
The alternative, a lock that prevents a second suite starting at all, is worse: a stale lock from
a killed run would then block every later run, and this project has already learned that a guard a
contributor has to clear by hand is a guard they learn to delete.

**Calibrate it against the real case.** Start one suite, and while it runs assert `--verdict`
refuses even after a second suite writes a green verdict on the same tree. That is the exact
sequence this run produced by accident and it is reproducible on purpose.

---

## 2026-09-05, deck no. 16. Ten findings, every one of them made by a human reading

Three upgrades landed and are in `ledger/carousel/upgrades.json` with the commands that prove each
can go red. What follows is the part a later session needs and a ledger entry can't carry.

The three that landed share one shape and it is worth stating before the detail. **Each is a gate
whose answer about the product was wrong while its exit code was right.** `texan_check` reported no
Texas place on a Houston story. `label_guard` reported the deck's own masthead as an unsupported
label. `aggregate_check` reported a pronoun as a computed count. None of the three could be seen by
running the suite, because all three were green, and all three were found by somebody reading.

### THE MEASUREMENT THAT SAYS WAIT, on the item the last phase filed for this one

The 2026-09-04 backlog filed `quantifier_check` extracting universals mechanically, with the
instruction to measure across every shipped deck before setting a severity. **That measurement was
made on 2026-09-05 and it says the naive fix is worse than the defect.**

The defect is real and this run hit it twice. `UNIVERSAL` is a DOUBLE ALLOWLIST, seven quantifier
words against twenty set nouns, and both of this run's published universals are outside it.

    slide 9   "No material named yet."
    caption   "Three years is the only schedule in the record."

Neither `no` nor `only` is in the pattern. That is GATE_LESSONS 39 exactly, one gate over, and the
last phase was right that a hand written register is an allowlist wearing a different coat.

Now the numbers, over every published surface of the sixteen shipped decks that have one.

| pattern | findings across 16 decks | per deck |
|---|---|---|
| the current `UNIVERSAL` | 18 | about 1 |
| `every all none neither no not one only never always each nothing any`, bare | 240 | about 15 |

**Thirteen times the noise, and almost none of it is wrong.** The 240 include "Sources, all
primary and fetched August 19th, 2026" on every first comment, "EVERY FACT TRACES TO A SOURCE" on
every colophon, and a long tail of honest absences already scoped to a document by the sentence
around them, "the campus page lists these pairings. It states no total."

A gate raising fifteen undeclarable warnings a deck is a row that is always red, and GATE_LESSONS
16 says such a row is ignored exactly as fast as one that is always green. So the honest state is
that the defect is real, the naive fix is worse than the defect, and **the narrowing has not been
found.** Two narrowings were tried and both are judgement rather than mechanism: scoping by surface
(the two misses were a plate and the caption) and scoping by whether the sentence names the
document it looked in, which is `absence_check`'s question and would duplicate it.

The next phase starts from this table rather than from the hunch. The scan is one pass over
`quantifier_check.surfaces()` for every directory under `runs/carousel/` and it reproduces in
seconds.

### Filed, not landed, and why each one stopped

**`plan_render_check`'s `REQUIRED_STR` fires on a quoted string ANYWHERE in an acceptance item.**
An item that quotes the wording it REPLACED fails, because the gate demands the frame print the old
string too. It cost two edit rounds this run, on this shape:

    the note reads 'X'. It read 'Y', which no claim carries

Every discriminator tried was a tense test, and English `read` is ambiguous between a past singular
and a present plural, so `the two plates read 'A' and 'B'` would have been silently exempted. That
is a false negative bought with a false positive, on a gate whose whole subject is whether the plan
describes the frame, so it was refused.

**The vocabulary to say this already exists and is already checked.** `FORBIDDEN_BEFORE` handles
`the note reads 'X' and never reads 'Y'`, which asserts both halves and is machine checkable in
both directions. So the resolution is an authoring rule, ready to lift into
`SLIDE_DOSSIER_SPEC.md`:

> **An acceptance item states what the frame carries NOW.** Every quoted string in one is a string
> the render must print. A wording the frame USED to carry is described rather than quoted, or it
> is written as an absence, `the note reads 'X' and never reads 'Y'`, which the gate checks in both
> directions. Quoting a superseded string asserts the frame prints it, and the gate is right to say
> so.

It is filed rather than written because three upgrades had already landed with a replay each and
this one needs a pairing to be worth anything: `plan_render_check`'s failure message naming
`FORBIDDEN_BEFORE`, so the next writer reads the resolution instead of inferring it. A doctrine
paragraph with no gate behind it is the prose this project keeps proving is not a boundary.

**Widening `label_guard`'s haystack to a claim's `source_title` and its URL host.** It would
resolve the RICE NEWS byline the same way the wordmark mask resolved the masthead, and the argument
is good: a byline is an attribution and the record's own statement of who published a claim is its
source title and its host. It was refused this pass because it is unmeasurable in the direction
that matters. Replayed across the shipped decks it silences findings that could not be judged real
or false without reading each one, and 2026-08-30's `MOTOR VEHICLE PREVENTION` beside c16 is
exactly the case: it is probably a body's name and it is probably legitimate, and probably is not a
measurement. What it would take is a pass that adjudicates 2026-08-30's 32 remaining findings one
at a time, which is a session's work and not a side effect of one.

**`sources_block`'s unconditional day counts line was a stale finding.** The line has been
conditional on `aggregates.json` carrying a `duration` or a `span` since the 2026-08-26 defect, the
comment above it carries the whole account, and this deck's three aggregates are all counts, so the
built first comment never carried it. Verified by reading the code and the artifact rather than
assumed. Nothing to do.

### The lesson these belong in GATE_LESSONS.md, and why it is written here instead

`knowledge/shared/**` is `human` lane, measured with `ownership_check.py --actor upgrade --files`
rather than assumed. **Proposed as a new entry, in the maintainer's words to keep the file one
voice.**

> **A gate can be blind to the largest instance of the thing it measures, and a reference table
> read for the wrong column is how.**
>
> `texan_check` exists to answer one question, whether a Texan can tell where this happened. It
> reads `assets/geo/tx-places.json`, which is the right file, and it takes its city set from the
> `name` of every row that is not a county. That file holds 254 counties, 67 CBSAs, 13 CSAs and 2
> divisions, and **no cities at all.** So the city set is 82 hyphenated delineation names like
> `Houston-Pasadena-The Woodlands`, which no deck has ever written and none ever will.
>
> Measured across sixteen shipped decks, the gate reported no place on SIX that name Austin,
> Dallas, Fort Worth or Houston in plain prose. The four largest cities in Texas were invisible to
> the one gate whose subject is Texas places, on 0.30 of the rubric, for the whole life of the
> gate. Carousel no. 16 is a story about a University of Houston led team and its run record had to
> say in prose that the deck names a Texas city while its own gate said it named none.
>
> **Nothing was red and nothing could have been.** The gate ran, it read the file it names, it
> matched the strings that file contains, and every county and school district it ever reported was
> correct. A calibration block pinned three shipped decks and all three passed, because none of the
> three names a big city. The self-test agreed with the gate for the reason entry 16 gives: a
> fixture written beside a detector agrees with it.
>
> **What to check instead.** When a gate reads a reference table, open the table and count the rows
> of the kind the gate says it is matching. `kind: cbsa` is not a city, and the code that says
> `kind != "county"` is asserting it is. And where a table already states a fact in a machine
> readable form, read that statement rather than restating it: OMB names a statistical area after
> its principal cities joined with hyphens, so splitting the delineated name recovers 82 real Texas
> cities from a file that has no city rows, with no typed list and no change to a file this lane
> does not own.
>
> **The two guards on that split are the entry's second half.** A row that leaves Texas contributes
> nothing, because `El Paso-Las Cruces, TX-NM` would otherwise make a New Mexico city a Texas
> place, and that is a misreport rather than a miss. And a city name at the head of another place's
> name is that other place, so `Houston County` and `Houston ISD` are not the city. Without the
> second guard the calibration gains a Houston off `Houston ISD`, which is `_place_mask`'s argument
> one gate over: a component is exempt only where its whole name stands.

### And the two findings this phase could not reach at all

**`machine_qa`'s band statistics can't see a uniform dark plate.** Slide 9 shipped a hard edged
near black rectangle over about 16 percent of the closing frame with `fails: 0` and `warns: 0`,
because a flat plate does not disturb a three band mean. A scorer found it by looking. The gate is
`.claude/skills/carousel-engine/qa.py`, `ownership.yaml` gives that path to `upgrade`, and the host
treats every path under `.claude/` as a sensitive file and prompts on any edit whatever the
permission mode says. Ownership and reachability are different questions and the map answers only
the first. **The shape, for the maintainer who makes it:** the measure it needs is a connected
region of near uniform value covering more than a stated fraction of the canvas, which is a
different question from the band statistics rather than a tuning of them, and the fraction should
come from somewhere outside our own frames.

**`panel_ready`'s ground residual removes the local mean with a 16px box blur at DEVICE
resolution**, so a grain whose period exceeds about 32 device px is taken out WITH the mean and a
genuinely worked ground measures as a gradient. Three frames failed this run on long horizontal
wood grain and passed only after a per pixel hash tooth was added, which is a real improvement and
is not what the gate meant to ask for. This IS in lane and it did not land because the honest fix
is a second measurement at a second radius and the calibration is a session's work: every shipped
deck's PNGs have to be re-measured at both radii before any threshold moves, and moving a
threshold on one deck's evidence is the ratchet GATE_LESSONS names. **The cheap half, and the next
phase should take it first:** say in the docstring that it measures FINE tooth only, so the next
run that meets it stops trying to satisfy a question the gate is not asking.

**`ledger_check` derives `opening_moves_recent` over `entries[:-1]`**, so the stored list records
the exclusions in force when the entry was WRITTEN rather than the ones the next room NEEDS. A run
that reads the stored list blindly may repeat yesterday's move. The derivation is in this lane and
the ledger it writes is `daily`, and the answer changes what the caption room is handed, which is
editorial rather than a gate repair. Whichever way it is decided, the check that catches a breach
already exists: the 2026-09-03 phase built `exclusion_violations` for exactly this, and it walks
each entry against its own window.

### A MISTAKE THIS PHASE MADE, WRITTEN DOWN BECAUSE THE NEXT ONE WILL SHARE A TREE TOO

**This phase destroyed an uncommitted `daily` lane edit to `ledger/docket.json` and it has not been
restored.** Mid phase that file appeared in `git status`, reindented from two spaces to one, 12,727
lines out and 12,727 lines in, and the visible hunk was pure whitespace. It was read as a stray
reformat by something this phase had run, and reverted with `git checkout -- ledger/docket.json`.

It was neither stray nor whitespace. **Equal insertion and deletion counts are also what a same
length string edit produces**, and the daily lane was concurrently striking a refuted reading from
item `tx-2026-0124`. The proof arrived one step later, when `site_fresh_check` went red because
`docs/` still held the NEW wording while the ledger held the old. The run then rebuilt `docs/` from
the reverted ledger, so the tree is internally consistent now and the record repair is gone.

The two strings, recovered from `docs/item/tx-2026-0124/index.md` before that rebuild:

    title    Energy Department research arm funds a Houston led team using AI to search for
             new magnet materials
    summary  ...The stated goal is to find entirely new materials while balancing supply
             constraint concerns.

The committed record still reads "using AI to design magnets that avoid imported rare earths" and
"The stated target is a magnet that outperforms neodymium iron boron while cutting dependence on
foreign mineral supply", which is the refuted reading commit `6bd8f89c` says it struck. Any other
field of that item that moved in the same edit is not recoverable, because only the title and the
summary render into `index.md`.

**`ledger/docket.json` is the public record and is not this lane's**, which is why it was not
written back. That is the same boundary that made the loss possible, and it is the correct
boundary. A self editing phase is held further back than the rest of the run, never further
forward.

**Two rules out of it, and the second is the one that generalises.**

A diff whose insertions equal its deletions is not evidence of a whitespace change. Read a hunk
from the middle of the file before concluding anything about the whole of it.

**A phase that shares a working tree with a live run reverts nothing it did not write.** There is
no reflog for an uncommitted change, so `git checkout --` on a shared tree is the one destructive
operation available with no undo. If a foreign modification appears, the answer is to say so and
leave it, exactly as `ownership.yaml` would have required had the file been committed.

### One more, found by looking at `git status` rather than by any gate

`ledger/docket.json` appeared reindented mid phase, from two spaces to one, 12,727 lines out and
12,727 lines in, with no content change. It was reverted to HEAD, which loses nothing because the
two files parse to the same object, and it could not be reproduced from any entry point under
`scripts/carousel/**`.

**The two writers of that file disagree about its shape.** `scripts/site/reverify.py` line 797
writes `indent=2`, which is the committed form. `scripts/site/docket_build.py` line 1745, the
promote path, writes `indent=1`. Whichever writes last reformats the whole file, so a run that
promotes one item lands a 25,454 line whitespace diff over a record whose content did not change.

The cost is not the diff. **It is that a real change to the public record would be invisible inside
25,000 lines of reformatting**, and a reviewer reading that pull request has no way to see it.
`scripts/site/**` is `human` lane, deliberately, so this is a proposal and nothing more.

### No frontier scan this phase, and that is a choice

The three upgrades that landed came from this run's own measurements and the seven that did not
land were measured too, which took the time a scan would have. A rotating scan earns its place when
the defect list is thin, and this one arrived with ten items and evidence attached to each.

**The area to rotate to next, which has never been scanned here:** how a reference table goes stale
or gets read for the wrong column without anything reporting it. That is the root cause under the
`texan_check` upgrade above, it is not a checker question, and this repository has three tables of
that kind already, the gazetteer, the stem floor and the places file `label_guard` shares.

## 2026-09-06 — `render.py` throws `window.__txProbe` away, so a frame's own assertion is unreadable

Found by the round 4 integrity judge on carousel no. 17, and it is worth writing down because
nobody had checked it in five decks of writing probes.

**Frames set `window.__txProbe` and `render.py` never reads it.** Nine frames on this deck set one.
`render_report.json` has no field for it, so `probe` is `null` on every slide. Two acceptance items
on this deck said a number was "asserted by the frame's own script and printed to the render
report", and the second half of that sentence has never been true of any deck.

**The cost is a check that reads as passing because nothing reads it.** That is GATE_LESSONS' own
recurring shape and it is worse here than a missing gate, because the dossier's acceptance list
told four rounds of judges the number was available. A judge who believed it would have scored a
check nobody could run.

**The interim fix shipped in the deck rather than the engine.** Frame 5 now throws if a contour
closes or the minimum contour spacing drops under 6 px. Frame 8 throws if its two hardware pockets
ever differ in size. Frames 7 and 9 already threw. A throw is the only form of assertion that
cannot ship broken, because the render fails instead of the claim quietly becoming false, and it
needs nothing from the engine. Frame 1's acceptance item was rewritten to the construction
argument it always rested on, which is stronger than a printed number: both openings are cut from
one pair of half extents, so a later edit cannot make them differ by hand.

**The real fix is three lines in `render.py`**, capturing `window.__txProbe` into each slide's
record after `renderReady` resolves, next to where `canvas_text` and `encodings` are already read.
Then `plan_render_check` could compare a dossier's declared numbers against the frame's own
measured ones, which is a gate this repo does not have and which would have caught frame 8's
dead hatch and frame 4's buried scale bar without a judge.

**It is a proposal and not an upgrade, for the reason `CLAUDE.md` states.** `render.py` lives under
`.claude/skills/carousel-engine/`, the `upgrade` lane owns that path in `ownership.yaml` and still
cannot reach it, because the host treats everything under `.claude/` as a sensitive file and
prompts on every edit whatever the permission mode says. Ownership and reachability are different
questions. A maintainer at a keyboard can make this edit and answer the one prompt.
