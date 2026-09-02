# Carousel no. 13, 2026-09-02

**The deck HOLDS at 6.562 against a 6.8 bar. No judge raised a hard fail. It does not merge.**

The record half of this run merged separately as #248, and the docket is current.

## What shipped and what did not

| | |
|---|---|
| Record (PR 248) | merged to `main`, 98 items re-verified, 0 rotten |
| Deck | built, gated, scored, **held** |
| Panel | 6.25 integrity, 6.62 craft, 6.58 reader, per-criterion median **6.562** |
| Spread | 0.37, inside the 0.75 the rubric flags |
| Hard fails | three raised, all three repaired, none surviving |

## The three hard fails, and why they were right

The integrity judge stopped the deck on three findings in round one. All three were accepted.

**1. The deck's premise was an inference.** The caption read "The Senate Committee on Economic
Development had September 3rd for an interim charge." Nothing in the record joins that meeting to
that charge. The listing's row is one cell reading `Economic Development (Canceled/see notice) Type:
Public Hearing Location: E1.016 (Hearing Room)`, which carries a committee, a type, an hour and a
room and **no subject**. The committee's own page carries the charge and lists no meeting against
it. The document that would join them is the hearing notice the row links, at
`capitol.texas.gov/tlodocs/`, which robots.txt disallows and this record does not crawl.

So the join was an inference and the deck asserted it as fact in its title, its caption and its
opening frame. Frame 3 is now the frame that says so, and it is the better deck: kicker "What the
row does not say", hook "The listing gives no subject." The refusal is recorded in `claims.json`.

**2. "The red row is the listing's own."** Written this run to mark a verbatim row, and wrong twice
over. Re-reading the fetched page turned up `class="redText"` on the cancellation note, so the
listing's own red marks the **canceled** row while this deck's reserved red marks the **open** one.
A provenance claim about a colour nobody fetched, on the one frame that asks a reader to act. Gone.

**3. The room binding.** `c2`'s quote had been clipped to a bare `Location: E1.016 (Hearing Room)`,
which binds a room to nothing, while its text asserted "Both", "public hearings" and "at 9:00 AM",
none of which its quote carried. That is the same defect this run's own rejected block refuses for
the chair's name. `c2` now carries the contiguous cell and `c25` carries the September 22nd row's.

## What the review rounds cost, and the lesson

Fourteen agent invocations before the panel: five pixel critics over two rounds, one flow critic,
three scorers, then one scorer again. **That is the single most expensive habit this routine has**
and the run's own prompt already says so: "the cheapest round is the one you do not need."

The pixel critics earned their keep in round one, finding five assertions the sources did not carry
and a value argument inverted in the pixels while every gate was green. Round two found less per
agent. The flow critic found the one thing worth the whole phase, that frame 4 published frame 9's
payload five frames early, which no gate could see.

The fix is not fewer critics. It is **acceptance items a machine can fail**. `plan_render_check`
reported 0 of 44 items asserting anything a render could contradict, which is to say the pixel
critic was the only reader forty-four planning sentences ever had. It is 13 of 69 now.

## Two gate defects this run hit

- **`numeral_trace` and `aggregate_check` give contradictory instructions.** The first tells a run
  to declare an untraceable figure in `aggregates.json` "where `aggregate_check` can re-derive it".
  The second reads only the phrases its own detector produced and refuses every other declaration
  as a leftover. So the named remedy is unavailable for any figure that is not one of four
  aggregate shapes. The deck serial and a retrieval year are both such figures, and this run took
  them off the frames rather than fix a gate it does not own.
- **`label_guard` cannot run on a deck that places no map marks.** It returns "reading the wrong
  file" on an empty shape map. Declaring frame 6's three plates in it was the right answer and it
  immediately caught a real defect: `c12`'s text read "The district's own statement inside that same
  article", naming no district, with "that same" pointing at a claim from another publication.

## Where the deck actually stands

Machine QA is clean on all nine frames. Every content gate passes. The value argument holds in the
pixels: frame 3 darkest at 14.6, frame 5 brightest at 91.8, deck median 20.4 against a planned 30,
recorded as measured rather than rounded toward the plan.

What holds it under the bar is craft and story, not integrity. `artwork_craft` medians 6.5 because
one primitive, a lighter rectangle holding type seated on granite, carries five of nine frames, and
the detail budget is front-loaded exactly opposite to the argument, which ends on 7 to 9.
`story_and_stakes` medians 6.2 because the deck hands a Texan a room number with little around it
and the AI charge does not arrive until frame 5.

Both are real and neither is repairable by another copy pass.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 25 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | PASS   | 9 slide(s), zero fails, zero warns |
| aggregates     | PASS   | 6 declaration(s), 6 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 5.71 MB, vector |
| score          | FAIL   | 6.562, below threshold |
| labels         | PASS   | 22 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 72 published string(s) read from one list, every universal names its set |
| dossiers       | PASS   | 43,892 chars planned |
| caption        | PASS   | 136 words |
| craft floor    | WARN   | 9 frame(s), median 531, floor 96, 1 quiet |
| plan vs render | PASS   | 13 of 69 acceptance item(s) checkable |
| texan          | PASS   | places NORTHSIDE ISD, WORTH ISD / body yes / deadline yes / next step yes |
| absences       | WARN   | 5 of 11 scoped to a named document, 6 unscoped |
| numerals       | PASS   | 11 numeral(s) over 9 frame(s), every one reachable |
| completion     | FAIL   | THE DECK DID NOT SHIP, so this run is not done |
<!-- gate-status:end -->
