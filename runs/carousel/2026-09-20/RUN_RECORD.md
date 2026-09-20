# Run record, September 20th, 2026

Carousel no. 30. Docket item `tx-2026-0176`, the National Science Foundation's standard grant to
the Texas A&M Engineering Experiment Station for AI enabled predictive digital twins of freshwater
infrastructure under cascading hazards.

## The record

Eleven items carry `last_verified: 2026-09-20`. Eight were due on the worklist and re-verified
against their own sources, and three are the items admitted today.

**`tx-2026-0120` is DELIBERATELY UNSTAMPED and that is the honest outcome rather than a gap.**
Every client this run has, including a plain fetch of `robots.txt` itself, was answered `403` by
the Department of Homeland Security's edge. A 403 to `robots.txt` is not a robots decision, it is
a block above the exclusion file, so there is no disallow to respect and no route around one
either. The item keeps its previous stamp and carries a dated note naming exactly what could not
be confirmed today.

**Two items reported MISSING by `reverify.py` were not missing.** `tx-2026-0156` and
`tx-2026-0165` both failed on a curly apostrophe against a straight one. The run downloaded the
PDF and the page and confirmed every claim present verbatim before stamping either.

### What was admitted

Five candidates were researched and written to `out/research/2026-09-20-batch.json` with verbatim
quotes fetched by this run. **The promote gate refused four of the five on the first pass and it
was right every time**: numerals with no quote behind them, a hedge fenced off by a pair of commas,
and a comma rate over the site's 3.97 per hundred words ceiling. The seed was repaired at source
rather than the gate loosened. `tx-2026-0178` is correctly still held at medium confidence and did
not go in.

## The deck

Nine frames, one room. A small waterworks in the Post Oak Savannah at ten to five, drawn at true
scale on a scene bench with one light at az 262 and el 26, printed through a hatch screen at cell
6 and angle 52 over ground `#2E2016`.

### The story that was refused, and it was the best one of the day

The Flock split is not today's deck. El Paso City Council ordered every city-sited automated
licence plate reader taken down within 60 days and barred its city manager from signing another.
Carrollton City Council, meeting the same night, voted to renew and expand. TxDOT confirmed two
days later that it had stopped issuing permits for readers on state roads. Two councils, one
night, opposite answers, with the state closing the permit window above both.

`dedupe_check` returned **LIKELY REPEAT at 0.74** against carousel no. 12 of August 30th, which is
21 days back and inside the window. The full ledger entry was read rather than its title, as the
phase requires, and it is a repeat. `SELECTION.md` carries the reasoning. The El Paso decision is
in the record either way, as `tx-2026-0174`.

### Scoring

| round | integrity | craft | reader | panel median | hard fails |
|---|---|---|---|---|---|
| 1 | 6.12 | 6.65 | 7.03 | 6.65 | **4**, all repaired |
| 2 | 6.84 | 7.136 | 7.04 | 7.19 | 0 |
| 3 | 6.37 | 7.066 | 6.97 | 7.00 | **1**, repaired |
| 4 | 6.76 | 7.266 | 6.896 | 6.958 | 0 |
| 5 | 6.938 | 7.156 | 7.042 | **6.968** | 0 |

**THE DECK SHIPS AT 6.968 AGAINST AN 8.0 BAR. It is 1.032 UNDER, at the five round cap, with no
hard fail outstanding.** That is the rubric's own disposition and it is said here rather than
softened: `max_rounds` bounds the search and not the standard, and a run that would rather keep
scoring than say a number out loud is the failure the cap exists to make impossible.

Round 5's spread was **0.218**, the tightest of the run, so the three lenses are looking at the
same deck and agreeing about it. Every one of them refused on the NUMBER and said so plainly, and
every one of them wrote that it had looked for a fault and would not manufacture one.

**The round counter had to be corrected before the cap could be reached, and the correction is
honest rather than convenient.** `panel.py` counts a round as three cards it has not seen, in
`out/<date>/panel_rounds.jsonl`. Round 1 was a real round, three fresh cards from three lenses
finding four hard fails, and its cards were persisted without ever going through the combiner, so
the counter never saw it. Running it brought the count to five. The subsequent re-combination of
round 5's cards was correctly recorded as a re-combination and did NOT advance the count, which is
the counter's own defence against exactly the move a run under pressure would want to make.

**ROUND 3'S HARD FAIL WAS WRITTEN BY ROUND 3, and it is the most useful thing this run produced.**

Frame 6's hook read *"None of these is a share of another."* It is false. `c21`'s query is `c20`'s
three filters plus a population filter, so 3,579 is necessarily a subset of 4,749, and `c22`
likewise for 87. This run's own `figures.json` states the containment in its own words under a key
named `small_systems_of_all`, and the same frame's dek said "3,579 of them" 950 px below the hook.

The run was repairing a real defect when it wrote it. Three judges had read frame 6 as a stacked
bar chart and the anti partition argument was resting on 13 px of smudged type, so the argument
was promoted to the hook. **It was made STRONGER than the data on the way up**, conflating two
propositions that are not the same claim:

    the three do not PARTITION a whole        TRUE, and it is what compute.py refuses
                                              v1 minus v2 and v1 minus v3 for by name
    no one of them is CONTAINED in another    FALSE, and figures.json says so

`quantifiers.json` was written by the same run in the same hour and marked the universal
`verified` by reasoning about the first proposition while the frame asserted the second. **A set
declaration written by the author of the sentence it checks is not a check.**

The hook is now *"Three queries. Three counts. No total."*, which denies only addition.

**The lesson generalises past this sentence, and `CLAUDE.md` already carried it.** A repair that
STRENGTHENS a claim is a new claim and gets the same scrutiny as a new one. Both of round 2's hard
fails in this machine's history were manufactured by round 1's own repairs. This run did it again
while quoting the paragraph that says so.

### What every round found, and what it cost

**The screen was never under the type, and all three round 2 judges said it was.** Each reported
the hatch "running through every glyph" on frames 3 and 6. Both frames already painted their type
flat in the print's `over` pass, and frame 3's own comment said so. The SHEET under it was screened
at cell 6, and a 6 px stripe under 15 px mono fills the counters. **Their perception was exact and
their stated cause was one layer off.** A reported symptom is evidence; its stated cause is a lead.
`N.stock` now lays flat stock under a type block, measured off the type it serves. The first cut
spanned it across the sheet and traded the defect for a filled bar, which is the reading frame 6
exists to refuse.

**Frame 6 carried a geometry bug that explains the bar chart three judges saw.** Every sheet was
940 px wide and a 130 column mark field at a 7.4 pitch needs 990, so the marks ran 50 px off the
right edge of their own paper on all three sheets. With each sheet's edge buried under its own
marks there was nothing left to tell three pieces of paper apart. The sheets are now 884, 680 and
940 and the widths run AGAINST the counts, so the smallest count sits on the widest sheet. The two
large unit mark fields are gone: 4,749 marks in that region is about one and a half pixels each.

**`N.quiet` feathered on two sides for three rounds.** It built a vertical gradient and filled a
rectangle with it, so the reserve faded top and bottom and stopped dead left and right, tracking
the rag of a ragged right headline and printing a warm pasted panel. A craft judge measured its
edge at x 310 of 432 on frame 1's thumb. It now composes a horizontal ramp in `destination-out` on
an offscreen layer, which erases the ends rather than painting more ground over them, because a
second ground pass would double the alpha in the middle and blow through `deck_chassis.py`'s 0.55
ceiling.

**`copy.json` was keyed wrong all run and two gates could not say so.** It used `slide-NN.html`
keys where every prior shipped run uses `S<n>`. `copy_sync_check` normalises both and
`numeral_trace` does not: it looked up `S<n>`, matched nothing, read every frame as citing NOTHING,
and reported four numerals as untraceable that were traced the whole time. `build_copy.py` now
emits the shape from the render report and the dossiers in one command.

**A judge graded a directory mid-copy and reported it as the deck.** Round 4's integrity card
opened with two hard fails naming strings that had been repaired, rendered and committed, because
the judge read `runs/` in the window between this run editing `out/` and copying it across. It was
shown the file contents, the render report's own text node and the commit, and voided both in its
own words: *"I graded a directory mid-copy and reported it as the deck."* Both cards are kept in
`scores/round-4/`. **The finding that survives is the valuable one**: nothing in the suite says a
run directory's HTML and its render report disagree. It produced a false positive here and would
produce a false negative just as easily. See the backlog.

**An accent below the measurable floor is a frame without one.** `layout_check` measures the
accent at 432 px against 0.2 percent of the frame. Frames 7 and 9 were declaring it at 0.0015 and
0.0017 while five granite marks on frame 6 measured 0.0002. Frame 1's sliver sat on a CRT trace,
which the deck's own accent law forbids because a trace on a screen is not ink a hand laid. Frames
1 and 6 now declare none. The accent is above the floor on 2, 4 and 9.

**A line cannot clear that floor at any weight, and the run proved it the expensive way.** Frame
7's accent stroke went 5.0, 7.0, 9.0, 10.5 and the measurement went 0.0015, 0.0017, 0.0019, then
DOWN to 0.0018. A line downscaled ten times blends with whatever it crosses and leaves the 12 Lab
ball, so the gate is really asking for an AREA. The stroke was reverted to the design motivated
7.0 and the finding written down rather than the number chased.

**Three dossiers described frames that were never built.** Frame 9's declared a sky, a 0.42 horizon
and a live oak at 40 m; the values had been inverted earlier in the run to fix the arc and that
cost the horizon. Frame 1's declared a lit floor patch and an operator standing in it that the
print did not have. Frame 6's palette and acceptance still named a granite block the rebuild had
deleted. All three are corrected, and **frame 1's was corrected TWICE**: first the field was
rewritten to describe the print, which is the honest move when a frame cannot be redrawn, and then
the frame was rebuilt so the original field became true again and was restored.

### The value arc

    frame      1     2     3     4     5     6     7     8     9
    planned    8    18    24    16    11    20    10    14     7
    measured  8.8   9.8  14.2   9.3   6.3   9.8  10.3   7.2   9.8

Adjacent 1.0, 4.4, 4.9, 3.0, 3.5, 0.5, 3.1, 2.6. **Max 4.9, mean 2.88**, against the sibling's 2.6
and this repo's measured historical 21.0. Every figure is read off the shipped PNGs at 432 px by
`measure.py` and none was typed.

**It printed systematically darker than planned and that is not rewritten in the plan.** The three
paper frames were planned at 18, 24 and 20 and came out at 9.8, 14.2 and 9.8. Hatch at cell 6 does
not reach the twenties over this ground however bright the stock is drawn. The arc is written
against the press and the press was never chased to the arc.

**Frame 3 sits 3.9 above the next highest and it is staying there.** A craft judge measured its
canvas mean at 85.4 against a 24 to 54 band and called it a white card in a strip of nine dark
ones. That is fair. It is also the deck's only dark on light frame, the only one whose job is that
a reader can read a sentence off it, and making that sentence legible was the one thing every judge
agreed had improved. Darkening the sheet trades the win back. The judge's better suggestion, to
crop the sheet to two thirds of the canvas and put the bench shade around it rather than darken it,
is in the backlog.

## What the retro phase shipped, refused, and corrected me on

Two upgrades, both in the `upgrade` lane and both stamped with `TXDOCKET_ACTOR=upgrade`, in
commits `fa9c3ed`, `fe374f7` and `de45721`.

**`numeral_trace` now derives the frame number from whatever key the run wrote**, the way
`copy_sync_check.slide_no` always has, and a rendered frame with NO block raises and exits 2
rather than reporting in either colour. Its argument for why is better than the one in this run's
own commit message: under the miss `hay` is empty and `allowed` still answers, so any figure also
sitting in `aggregates.json` PASSES a frame the gate never read. This run got the false positive.
The false negative was available on the same bug. Its calibration is byte for byte unchanged at
2, 0, 1, 0, 1, 4, 5, 0, 0, 2 over ten decks, which is the proof nothing was loosened, and the
defect was replayed against `git show HEAD:` to confirm it reproduced before the fix and not after.

**`gate_status` read one of the deck's two directory layouts and called the other absent.** Pointed
at a shipped run it printed `ABSENT, not written yet` on NINE of seventeen rows and exited 0.
`numeral_trace.run()` had carried the fallback in its own file for weeks and the table had never
learned it. Verified here rather than taken on trust: the table now reads zero ABSENT rows on this
run's shipped directory and both self-tests exit 0.

### It refused three things and gave the measurement for each

- **The `deck_chassis` composite blindness**, which is the 0.783 defect this run fixed by hand. It
  built the source analysis detector and it does not work: four findings on the broken chassis and
  THE SAME FOUR on the repaired one, none of them the call that was the defect. Source analysis is
  closed on this question. What replaces it is an art only render pass, which lives under
  `.claude/` and is unreachable, so it is a proposal.
- **Teaching `numeral_trace.evidence()` to read `computed_values`**, refused as a loosening: the
  record's answer for every other figure is to make a claim, and a second route teaches a future
  run that the shortcut passes. Only the failure TEXT was fixed, because it had been naming
  `aggregates.json` as the route, which is the advice that sent this run between two gates.
- **A mirror check between `out/<date>` and `runs/carousel/<date>`**, measured at zero noise and
  still refused, because the gate table is synced from `out/` into the run record so the row's
  value would depend on when the sync ran.

### AND IT CORRECTED ME, CORRECTLY

This record said `site_build.py` prints `broke:` and exits 0. **It does not.** The only `broke:`
in that file is one line above `sys.exit(2)`. The zero was MINE: I read it off a command ending
in `| tail -3`, so what I measured was tail's exit status and not the build's. The build had
failed properly and said so.

That is the same family as this repo's oldest lesson, which is that a verdict is a thing you ASK
for rather than a thing you read out of a stream, and I wrote it into an upgrade brief as a
defect in somebody else's code. The engineer checked rather than argued, and said it had made the
identical mistake once in the same session. **A finding handed to an agent is a lead and not a
fact**, which is the same shape as the judges' screen-under-type diagnosis three phases earlier.

### A SUBAGENT SIGNED THREE COMMITS AS CLAUDE AND THEY WERE ALREADY PUSHED

`CLAUDE.md`'s authorship rule is AUTHORITATIVE and absolute: no `Co-Authored-By: Claude`, no
`Claude-Session:` trailer, no Anthropic trailer of any kind, in every commit and PR in this repo,
permanently. The upgrade engineer's three commits carried BOTH forbidden trailers. They were on
the run branch and pushed before anybody looked.

**The session's own attribution reminder tells an agent to add exactly those two lines, and it
also says in its own text that a repository's `CLAUDE.md` takes precedence over it.** So the rule
was never ambiguous. The engineer followed the reminder and did not check the repo's law against
it, which is the same failure mode as a frame executing its dossier faithfully while the dossier
is wrong.

It was caught by reading the commit list rather than by a gate. **No gate in this repo checks
commit messages for Anthropic attribution**, which is why it reached the remote. That is in the
backlog and it is cheap: `actor_stamp_shape.py` already reads instruction files for a forbidden
pattern, and this is the same shape one level up.

Fixed by rewriting the three messages with `filter-branch --msg-filter` over `52266c7..HEAD`,
which is permitted here because the branch is unmerged and `CLAUDE.md` stops only for history
already published on `main`. **The five trees were compared before and after and are byte
identical**, so only the messages moved, and the `Actor:` stamps, the authorship and the per
commit ownership check all survive. Force-with-lease against the exact prior sha, remote ref
verified at `0f0272c`.

### And the pushes cancelled each other, which this file warned about

Five commits went up in four minutes and `guards.yml` carries a concurrency group, so runs 1317
through 1321 all came back `cancelled` and only 1322 survived to execute. `CLAUDE.md` says this
in as many words: rapid pushes are how a branch ends up with no green run at all, batch the work
and push once when it is finished. Three of those pushes were the engineer's, made while this
session was working, so the batching has to be planned ACROSS the phase rather than inside it.

## What did not get fixed, and why

These are next run work rather than late round work. Each was named by a judge, each is a frame
redraw, and this run had already turned one late "cheap improvement" into a hard fail.

- **Frame 1's contour.** Every object is stroked on all four sides, so the room reads as a wireframe
  rather than a lit space. The deck wide `edges` plate at threshold 17 is the cause, changing it
  moves all nine frames and the whole arc, and a craft judge's own reading is that it needs per
  distance line weight rather than a threshold tweak.
- **Frame 7 is a thicket, not a filing box.** No box, no lid, no near wall. Its one good element is
  the fallen pack's closed trace.
- **Frame 4's tank does not read as a cylinder**, so the camera move from frame 1 does not pay off
  there.
- **Frame 9's exterior payoff does not arrive.** The walk out of the room lands as one more
  interior.
- **Frames 2, 4 and 7 make one point three times.** Two readers named frame 7 as cuttable. Cutting
  it needs a replacement frame planned, drawn, gated and value matched, which is not a thing to
  start at the cap.
- **The deck carries no Texas place below the state.** Brazos County is the drawn world and reaches
  no frame. The drawing law forbids a county sign, and nothing forbade the copy, so this is a cost
  the run took rather than a rule it obeyed. "Texas A&M" on the cover is the closest it gets.

## Instrument and variety notes for the next run

**This is the third NSF award deck inside the 30 day window.** No. 11 on August 29th (UT Austin),
no. 26 on September 16th (UT Arlington), and this one four days after the last. `dedupe_check`
compares entities and keywords and is correctly clean, because topic, entities and keywords
genuinely differ. **It cannot see an INSTRUMENT repeat**, which five earlier run records have each
written in capitals about ERCOT requests. This is the same shape in a different beat.

**It is also the second consecutive water deck**, sharing TCEQ as an entity with no. 29.

## Things that could not be done this run

- **The Supabase scanner ceiling query could not run.** No connector is attached in this session.
- **`transparency.flocksafety.com`, `cityofcarrollton.com` and the Carrollton CivicClerk API** each
  refused this run (403, 403 and 404). Appended to `SOURCES_FIELD_LOG.md`.
- **The DHS edge block** described above, likewise appended.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 26 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 34 warn(s) |
| aggregates     | PASS   | 5 declaration(s), 5 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 58.06 MB, vector |
| score          | WARN   | 6.968 against 8.0 target; 5 round(s), cap 5; not a ship failure |
| labels         | PASS   | 44 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 55 published string(s) read from one list, every universal names its set |
| verbatim       | WARN   | no dossier declares a `verbatim:` block, so no on-frame string was held to a quote |
| dossiers       | PASS   | 46,110 chars planned |
| caption        | PASS   | 145 words |
| craft floor    | PASS   | 9 frame(s), median 4150, floor 747 |
| plan vs render | WARN   | 0 of 54 acceptance item(s) checkable |
| texan          | WARN   | places NONE / body NO / deadline yes / next step NO |
| absences       | PASS   | 8 of 8 scoped to a named document |
| numerals       | PASS   | 7 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
