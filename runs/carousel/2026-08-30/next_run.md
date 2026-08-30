# WORK THE PANEL FOUND PAST THE CAP

`config/carousel/scoring_rubric.yaml` sets `max_rounds: 5`. Past that cap a round may repair a
HARD FAIL and nothing else, and everything else goes here rather than into another render loop.
Each item below was MEASURED by a judge in round 5 and verified here against the artifact, so
none of it is taste.

## The deck as shipped

- **Slide 5's eastern label is biased left of the end it names.** Verified in
  `render_report.json`: `THE LOUISIANA BORDER` spans x 470 to 800 and its lit terminator sits at
  x 677 to 773. The label DOES cover its end, so this is not the round 2 defect returning, but its
  centre is at 635 against a terminator centre of 725 and a judge reading the 432px thumb attached
  it to the state's interior. The fix is `dx: -48` rather than `-138` in slide 5's label table.
  Not changed here, because two of round 5's three judges were still scoring the deck when it was
  found and moving the artifact under them would have made their reports describe something else.

- **Slide 8 names where an absence was looked for and never names where the ORDER came from.**
  The frame prints `gov.texas.gov/news` with a retrieval stamp for c41, which is the absence, and
  the Governor stopping the money is the most consequential fact in the deck. c11 and c12 are both
  `texastribune.org/2026/08/28/texas-greg-abbott-flock-cameras-order-state-money`. Slide 3 got
  exactly this fix in round 4 and slide 8 did not.

- **The reader lens raised the same objection in four consecutive rounds and it is still open.**
  The deck makes the fee universal in its own words on slide 4 and then offers one door, a state
  board meeting in Austin. Nothing on nine frames tells a reader in Lubbock or Corpus how to find
  whether their own city has these cameras. Closing it needs a FETCH this run did not make: the
  authority's own grant award list, on the same txdmv.gov domain slide 9 already cites. That is a
  Phase 2 scout task, not a repair.

- **The caption closes on a rhetorical question for the fifth run running**, which
  `ledger/carousel/captions.json` has now recorded against itself twice.

## The machine

- **`machine_qa` reports `visible 0%/0%, seen 0/0px at 432w` identically on all nine frames**, and
  `render_report` carries `a_visible_frac: 0` and `b_visible_frac: 0` on every encoding, while dE
  and AUC beside them vary sensibly per frame. Two judges flagged it independently across three
  rounds. A field that returns the same value on nine different drawings is measuring nothing, and
  it is the ONE number that would say whether a declared focal survives to the size a reader gets,
  which is the question this deck most needed answered. There is now direct evidence it points the
  wrong way: slide 9 was rebuilt to cure an 0.66 AUC and came back at 0.62 while visibly improving.
  This is engine code, so it belongs to `upgrade` rather than to `daily`.

- **The value arc is planned in the storyboard and read by nothing.** The integrity lens's fix:
  make it a computed per frame target the render pipeline asserts against and fails on, the way
  slide 8 already asserts its own 0.38 break. This deck shipped seven of nine frames inside a 19
  point band against a planned arc spanning 48, and its own `arc_note` recorded the miss in prose
  instead of stopping it.

- **Nothing checks a frame's declared encoding against `claims.json`.** Round 3's hard fail was a
  drawing asserting a per camera power state c20 gives in neither direction, and the assertion was
  sitting in `data-encodes` in the frame's own source. `machine_qa` reads that string as a
  specification and measures whether two regions differ. It never asks whether the specification
  is licensed. Three judges found it; no gate could.

- **`plan_render_check` can only machine check STRING presence and absence.** 18 of 51 acceptance
  items carry an assertion it can contradict, up from 3 of 53, and the other 33 are prose. All
  three judges' one sentence fix in round 1 was the same: fail the build when a declared item is
  absent from the pixels. That needs the checker to read measurements out of `render_report`, not
  just text nodes.

## The craft memory

- The halo and the soft luminous field are spent on a whole deck. `artwork.json` `avoid_next`
  carries the reason and it is the run's own best sentence about itself: a field with no edges
  anywhere gives a reader nothing to hold at 432px, and every frame that worked here worked
  because it had ONE hard thing in it.
- Three drawings had to be thrown away to learn one rule each, and all three are in the dossiers:
  glowing circles put a lens on a deck whose first law forbids one; bands of lit air are a smear at
  feed size; three masses of decreasing height on one baseline are a bar chart.

## Round 5's craft findings, per frame

Recorded rather than repaired, because round 5 is the cap. Each was measured off the render.

- **Slide 7, the frame the deck should cut or rebuild first.** The height fix is real (807 / 525 /
  330 at display scale against last round's 460 / 462 / 450, bases ascending as they recede), but
  the near mass has no internal value gradient and goes transparent low in the frame, so the
  field's mottling reads straight through it. The cast that `value_structure` declares the frame's
  DARKEST element is not findable at either size. And the mid and far masses ABUT rather than
  overlap, so the second occlusion pair is a tangent: the fix landed on pair one only. The right
  40 percent of the frame is empty.
- **Slide 6's material identity is wrong even though its joint is now right.** The aggregate
  renders as spherical beads with a highlight and a shadow, so at 432px it reads as condensation
  on brushed metal rather than as stone in a sunlit slab. Its probe measures dE 4.9, the deck's
  lowest by a factor of three, on the one frame whose whole job is to be the light extreme.
- **Slide 8's break moved its defect rather than losing it.** The top is genuinely ragged over
  about 100px now; the LOWER boundary is a razor straight full width step. The bottom 55 percent
  of the frame carries no drawing at all.
- **Slide 2 still has two hard rectangular fold terminations**, at roughly (648, 1165) and
  (965, 1055) in display space, even though the bands now fade along their length.
- **Slide 5's two terminators are horizontal streaks aimed inward at each other**, El Paso's
  running right and Louisiana's running left, and a reader completes a line between two collinear
  streaks pointing at one another. That is the corridor inference the frame's printed refusal
  exists to prevent, arriving by a different route than the span line that was removed in round 3.
  `THE LOUISIANA BORDER` is also set inside the silhouette, in the interior the deck law declares
  empty.
- **`band_ratio` sits within 5 percent of 1.0 on five of nine frames**, which is the machine
  reporting evenly spread field noise rather than a detail budget.
- **Exactly one bright frame planted in an otherwise dark deck is now a habit rather than an
  inversion.** Decks 1 and 3 both used it at their own slide 5. This is its third outing in twelve.

## The one number that would have shortened this run

Five scoring rounds, fifteen judge reports, and the single measurement that would have answered
the question the deck kept failing on was dead the whole time. Two judges found it independently.
Fix `a_visible_frac` and `b_visible_frac` before the next deck is planned, not after it is drawn.

## Found after the branch was pushed, when `shipped_check` first ran on this deck

- **`measurements.json` had never been written by any run in this repo.** `shipped_check`'s
  `measured figures` gate reads it, and with the file absent the gate returned None on every deck
  it has ever seen. It is written now, by `measure.py`, off the rendered PNGs. The lesson is the
  registry's own: a gate whose artifact never exists reports clean forever, and only the
  reachability assertion in the self-test can see it. Every new gate needs one.

- **`ledgers` was unreachable for the same reason and found five decks of drift the moment it
  ran.** `captions.json`'s `opening_moves_recent` and `structures_recent` had disagreed with
  their own entries since 2026-08-25, and the disagreement sat in the shipped_check notes for
  five consecutive runs where nothing was reading it. Both lists are pure derivations. **Nothing
  should be hand-maintaining a value that is a function of the entries beside it**, which is
  CLAUDE.md's oldest recurring shape, and the durable fix is for the caption phase to write them
  by derivation rather than by hand.

- **`dossier_check` never runs during a run, only afterwards through `shipped_check`.** Eleven
  problems in the storyboard's `bands` fields reached a shipped deck, one of them describing a
  body that round 2 had deleted. Run it in the planning phase, before the first render, where a
  band plan can still shape the drawing instead of being corrected against it.

- **`compute.py` is written fresh each run and forgets what the last one learned.** The sources
  tally, the run's own counts and the figures file were all things a previous run had already
  worked out and this one had to rediscover, twice getting the wrong answer first. A small shared
  helper for the figures every deck needs would have cost nothing and saved both wrong answers.

## The near miss worth carrying forward

**A gate that ten decks passed was not a gate that worked.** `plan_render_check`'s colour test
matched hex literals only, and ten storyboards had written their colours as hex, so it had never
once been asked a question it could get wrong. The first deck to compute its gradients would have
been reported as declaring colours it never drew, and the wrong verdict was one commit from being
written into this run's record as a finding about the deck.

What saved it was reading slide 7's source instead of trusting the gate's output. **A gate's
green history says how it has been exercised, not whether it is correct.** Before trusting any
gate on a deck that does something new, check that the gate can SEE the new thing.

The same question is open on three other checks and should be asked of each before the next deck:
`craft_floor`, `bespoke` and `coherence` all read the frame source, and none has been tested
against a frame that computes what it draws.
