# Run record, 2026-09-17, carousel no. 27

**Software drafts your lab result note.** Memorial Hermann Health System in Houston uses an
Epic-built assistant to draft the patient-facing note that comes with a lab or imaging result.
The health system published three figures. A trade publication read the same announcement, named
what those figures do not establish, and pointed to a randomized pilot of 52 doctors at UC San
Diego Health whose result missed statistical significance. Business and Commerce Code Sec.
552.051 took effect January 1st, and subsection (b) puts a disclosure duty on a governmental
agency while (f) puts one on the provider of the service or treatment. Chapter 552 has no section
headed Applicability.

## THE DECK SHIPPED UNDER THE BAR AND HERE IS BY HOW MUCH

**6.856 against an 8.0 threshold. A shortfall of 1.144.** Five scoring rounds, which is the
rubric's `max_rounds` cap, and zero hard fails standing at the end. That is the one path
`run_complete.py` provides that is under the threshold and not a failure, and it is only that
because the run did the work the cap measures. The number is stated here, in the pull request and
in the email rather than rounded away.

| round | integrity | craft | reader | median | spread | hard fails |
|---|---|---|---|---|---|---|
| 1 | 6.18 | 6.89 | 6.72 | 6.740 | 0.71 | 1 |
| 2 | 6.19 | 6.95 | 6.86 | 6.860 | 0.76 | 1 |
| 3 | 6.81 | 7.03 | 6.57 | 6.736 | 0.464 | 0 |
| 4 | 7.32 | 7.03 | 7.11 | 7.216 | 0.284 | 0 |
| 5 | 6.66 | 7.05 | 6.89 | 6.856 | 0.392 | 0 |

The median is nearly flat across five rounds and the two columns that moved are the ones worth
reading. Hard fails went to zero and stayed there. The spread fell by nearly two thirds, which
matters because in round 1 the judges disagreed about `claim_integrity` by 3.5 points and by
round 4 that gap had closed to 1.3. A panel that agrees is a panel that has understood the deck.

## THE TWO HARD FAILS, AND WHY BOTH WERE THE SAME DEFECT

The fact-checker REJECTED the finding that this statute requires Memorial Hermann to disclose.
Honouring that in the ARRANGEMENT rather than only in the strings was this run's hardest
editorial work, and the panel caught the deck leaning anyway, twice, in the same place.

**Round 2.** Frame 7 set `A governmental agency` over `shall disclose to each consumer, before
or at the time of interaction` and deleted twelve words of limiting clause from the middle with
no mark. Both fragments were verbatim. The sentence they made is not in the statute, and it
stated the duty MORE BROADLY than the statute does. Subsections (c) and (f) beside it were
contiguous joins set in identical typography, which is precisely what hid the splice. Three
readers reached it independently.

**Round 3.** The same frame truncated (c) at `under Subsection (b)`, dropping the clause that
makes it a rule about OBVIOUSNESS and leaving `A person` standing in display type beside `A
governmental agency` as though it named a second duty holder. `c22`'s own note says (c) is
evidence about the ambiguity rather than a resolution of it, and the frame was using it as the
resolution.

**The second hard fail, round 2.** Frame 8 printed `SUBCHAPTER B. DUTIES AND PROHIBITIONS`,
truncating `ON USE OF ARTIFICIAL INTELLIGENCE`, on the one frame whose entire argument is
exhaustive verbatim transcription.

All three are fixed. Frame 7 now sets (b), (c) and (f) as contiguous runs and prints BOTH
readings of (f)'s scope, including `Read the other way, (f) sets only the timing for a duty (b)
gives to an agency`, which is the reading that cuts against the deck. Two round 5 judges called
that line the best thing on the frame.

**The pattern under all three is worth more than the incidents.** Every string was verbatim every
time. The lean came from what the frame CHOSE TO SET and WHERE IT CHOSE TO STOP, which no gate in
this repo measures and three separate judges found by reading. A deck that shortens a sentence
silently has no standing to tell a reader what another sentence does not say.

## WHAT THE PANEL FOUND THAT THIS RUN DID NOT FIX

The cap permits repairing a hard fail and nothing else, so these are recorded rather than
repaired. They are the next run's first work, in this order.

1. **Frame 9's halftone reserve was repaired in the source string and never reached the pixels.**
   `.card` was added to the `lineBoxes` selector, but `lineBoxes` measures LIVE geometry through
   `getClientRects` and the card is positioned AFTER the canvas work, so the reserve was computed
   at the card's static position, outside the tooth region. The deck's one screen still runs under
   the five mono lines on the accent card, against the chassis's own oldest rule. A round 5 craft
   judge found it by reading the code AND the render; this run reported it fixed and it was fixed
   in the string only. THE ORDERING IS THE LESSON: position, then measure. `lineBoxes`' own
   docstring warns about exactly this.
2. **Frame 7 omits (f)'s opening trigger clause**, `If an artificial intelligence system is used
   in relation to health care service or treatment`, which is what makes (f) the health-care
   provision and the only reason it is in this deck. An omission rather than a falsehood, and two
   integrity judges disagreed about it: round 3 said the lowercase opening signals the cut
   honestly, round 5 said nothing marks it. Both read the same pixels.
3. **Frame 2 is cuttable on five independent readings across five rounds.** Deleting a slide at
   round 5 is a `copy.json` edit and a renumber rather than a restructure, and one judge said so
   directly. This run judged that more risk than value against a deck complete and honest at nine
   frames. THE DISAGREEMENT IS RECORDED RATHER THAN SETTLED, because five judges is a stronger
   signal than one showrunner's risk call.
4. **Frame 3 reads poorly at feed size after four rounds of correct arithmetic.** Each round
   repaired a different symptom: no desk, then no top face, then a base that missed the figures'
   ground line, then mixed depths. The bench now checks to the pixel at 1096.1, 1489.4, 873.9,
   937.25 and PXM 341.67, and two round 5 judges still called the monitor a floor lamp and the
   empty chair unreadable. CORRECT PROJECTION IS NECESSARY AND IS NOT SUFFICIENT, and no gate in
   this repo measures whether a drawn object is RECOGNISABLE.
5. **Four `bleeds` declarations disagree with the drawn sheets.** `layout_check` measures the
   `primary_image` RECT and passes; two craft judges measured the `N.sheet` CALL and found frames
   4, 5 and 7 ending 100 to 250px inside the frame and frame 2 declaring a top bleed its panel at
   y 392 never makes. The declaration and the gate agree with each other and not with what a judge
   sees, which is the worst shape a check can have.

## THE ONE GATE THAT WOULD HAVE CAUGHT MOST OF THIS

A round 5 craft judge's own words, and it is the best upgrade proposal the panel produced:

> Add one gate that reads each frame's drawn geometry back out of its own source and fails the
> build when it disagrees with the dossier.

That single check catches items 1, 5 and the three false bottom bleeds, and four rounds of judges
were spent finding by eye what it finds for free. It is in `knowledge/carousel/UPGRADE_BACKLOG.md`.

## THE RUN'S OWN PATTERN, NAMED BY A JUDGE

> The gap between how carefully this run writes things down and how carefully it checks the
> writing against the pixels is the pattern worth naming to the next one.

That is fair and it is the honest summary. Three declarations in the plan were false about what
shipped and were corrected once measured rather than defended: a 28 degree oblique that is 1.2
degrees and could never have been more, because `N.sheet` rotates an axis-aligned rectangle with
no projection in it; a desk declared at 0.75 m that measured as a 0.17 m plinth; and an acceptance
item citing an absences block that writes ranges with `through` rather than the sixteen numbers it
claimed. Each is now either fixed or stated honestly, including the cases where the honest
statement is that the primitive cannot do what the plan promised.

## THE SCORE ROW IS STALE AND HERE IS EXACTLY WHY

`gate_status` reports `score` as STALE and it is right. After round 5 closed, `shipped_check`
found that `slide-04.html` did not carry the string `copy.json` says it prints: the source had
`SEARCHED &nbsp;&nbsp; FOUND` and the record says `SEARCHED FOUND`, because a browser collapses
those entities in the text node. `copy_sync_check` reads the RENDER and passed; `shipped_check`
reads the SHIPPED SOURCE and was correct that a file a reader can open must say what the record
says it says. The fix replaced the entities with a CSS gap and required a re-render of frame 4.

**Measured rather than asserted: 8,388 pixels changed, 0.1438 percent of that one frame, inside a
box at logical x 870 to 1039, y 390 to 495**, which is the position of the word FOUND. No string,
no claim, no numeral and no other frame changed. The judges scored a deck whose frame 4 had that
word a few pixels to one side. That is the whole of the staleness and the trade was taken
deliberately: a shipped source that does not carry its own recorded string is the defect the gate
exists for, and a word moving 0.14 percent of a frame is a fact that can be stated precisely.

## Permissions

`prompt_audit` measured **1,379 tool calls and none waited on a human.** Nothing in this run
stopped for a permission, and no setting had to be changed to keep it going.

## Record

Three items admitted: `tx-2026-0162` (Memorial Hermann, the story), `tx-2026-0163` (the NSF
Science and Technology Center at UT Austin), `tx-2026-0165`. One held for want of a county,
`tx-2026-0164`. Six due items re-verified, and `tx-2026-0024`'s claim c3 and summary corrected.
42 claims, 5 absences each with a stated method, 8 rejected findings.

## Sources

`gov.texas.gov` now serves a robots.txt disallowing this crawler across the whole host, where
`SOURCES_REGISTRY.md` records that it serves none. Nothing was fetched from it. The registry is
`human` lane and carries the crawl boundary, so the observation is in
`knowledge/shared/SOURCES_FIELD_LOG.md` and the decision is a maintainer's. `dhs.gov` returned 403
to every User-Agent this container tried and answered WebFetch for the same URL minutes later, so
that 403 is a property of the client path rather than the host and nothing goes on a blocked list.

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 42 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | PASS   | 9 slide(s), zero fails, zero warns |
| aggregates     | PASS   | 5 declaration(s), 6 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 8.81 MB, vector |
| score          | STALE  | score.json predates the newest render, so it describes a deck that no longer exists. Re-run it |
| labels         | PASS   | 56 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 105 published string(s) read from one list, every universal names its set |
| verbatim       | PASS   | 9 declared fragment(s) over 9 of 9 dossier(s), every one a literal substring of its own claim's quote |
| dossiers       | PASS   | 46,912 chars planned |
| caption        | PASS   | 148 words |
| craft floor    | PASS   | 9 frame(s), median 4044, floor 728 |
| plan vs render | WARN   | 9 of 70 acceptance item(s) checkable |
| texan          | WARN   | places Houston / body yes / deadline yes / next step NO |
| absences       | PASS   | 14 of 14 scoped to a named document |
| numerals       | PASS   | 27 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
