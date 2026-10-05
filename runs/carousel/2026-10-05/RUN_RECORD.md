# Run record, October 5th, 2026

Effort at wake: `high` (as the repo's settings carry it). The no-stall hook logged `armed` at
06:22:16 UTC and judged the session unattended from SessionStart, with the host's
`CLAUDE_CODE_SESSION_ATTENDED=0`. It refused nothing. The session's worker process was restarted
once mid-run, during the round 1 repairs, and the run resumed from its branch and `run_state.json`.

## DISPOSITION: SHIPPED AT THE ROUND CAP, 7.124, 0.576 UNDER THE 7.7 RUNG AND 0.876 UNDER THE 8.0 TOP RUNG

Carousel no. 43, "12 of 120. The UT System's health AI pilots", is nine frames rendered in one
wards world (blueHour sky, Gulf haze, the lamp key at azimuth -60 and elevation 32) declared once
in `assets/js/deck/2026-10-05-wards.js`. The hero is the kit hospital at ten floors with a chassis
bay skin of 120 lit rooms, one per submission, and a 2 by 6 gold block for the 12 funded pilots.
The story is tx-2026-0201, admitted today. UT REAL Health AI, the UT System's health care AI
laboratory, funded 12 pilot projects out of 120 systemwide submissions with awards of more than
$3.6 million. Only one entry, the no-show project, states what it already saved, more than 6,500
appointments and $900,000 at UTHealth Houston, and the page cites no audit behind it.

The deck went through these reviews:
- three pixel critic rounds, with three critics each round
- one flow critic round (the second was not spent)
- three panel rounds of three judges

The panel medians were 6.93, 7.014 and 7.124, read from `score.json` each round. No judge in any
round found a hard fail. Round 3 is the cap on the ladder (8.0, 7.7, then ship), so the deck ships
with the shortfall named.

**The craft floor stood down at the cap.** The panel's `artwork_craft` median was 6.5 against the
8.5 floor. `score.json` carries `craft_floor: capped`.

The heaviest drags, named in every round:
- **artwork_craft** (6.0 to 6.7 across the judges). Frame 5, the waiting room, was named first in
  rounds 1 and 3 by all three judges: a room with no ceiling, no light source and a glazing band
  read as a plate. Frame 6, the turn, was named in all three rounds as a flat facade with no
  ground. Frame 3's top third and window band were named in all three. Frame 8's skyline as boxes
  in all three.
- **variety** (6.0 to 7.0). Blue hour repeats no. 39 four decks back, the count-as-objects cover
  repeats nos. 39 to 42, and this is the third clinic deck in four, as SELECTION.md says.
- **sequence_and_momentum** (6.5 to 7.0). Frames 7 and 8 return to the pilot catalogue after the
  turn at 5 and 6. The flow critic asked for a reorder to 1, 2, 7, 8, 3, 4, 5, 6, 9 in its round 1.
  **The reorder was declined** as a renumbering of nine frames, their dossiers, counters and
  copy with the panel still to run. Every judge then named the same sag. It is the first thing the
  next deck with a turn should plan for.

**Defects named twice, and what the round rule did with each.**
- **The screen moire on frame 3 and the pane speckle on frames 1, 8 and 9 were z-fighting, not
  shadow acne.** Pixel rounds 2 and 3 and panel rounds 1 and 2 named them. Two repairs aimed at the
  shadow map (receiveShadow off, then an unshadow pass before the snapshot) did nothing. An
  experimental render with the weather pass removed did nothing. A render with the near plane at
  0.5 m cleared it at once. The chassis stage defaulted to near 0.05 with far 12000, and the bay
  cards stand 3 cm proud of the kit mullions. Every frame now sets its own near plane, 0.2 to 2.0.
  Queued as `near-plane-zfight-on-card-skins`.
- **Frame 5 was RECOMPOSED twice.** It moved from a flat back wall to a band of night glazing in
  pixel round 2, then to floor-to-ceiling glazing on a mullion pitch with downlights after panel
  round 1. The floor was tinted to the glazing's blue so `layout_check` could separate the seat
  blocks (queued as `grid-ground-from-whole-outside`). The judges still read it as a diagram. A
  standing-eye camera facing the glazing, which all three proposed, was not tried.
- **Frame 6 changed its motif state three times.** The eleven bays went from base white (flow
  critic: reads as defunded) to an ember (panel round 1: reads as twelve lit) and back to a dim
  corridor white under one gold bay (round 2 and 3 did not name the colour again). The garage
  parapet was added at its foot in round 3 and read as a dark band.
- **Lamp pools** were invisible as PointLights, clipped to white discs as SpotLights at 9x, and
  capped at 4.2x with a full penumbra from pixel round 3. Frame 1 and 9 gained a lamp inside 30 m
  of the camera so a pool reads at all. Queued as `lamp-pool-reads-only-near`.

**Copy and integrity repairs through the panel.**
- "The project's own count" was replaced on every surface (slide 5 dek and label, slide 6 dek, the
  caption, the first comment, the web edition, tx-2026-0201's summary and its history note) by
  what the page supports, that the page states the saving and cites no audit behind it.
- c17's quote was extended from a re-read of the page to cover "suicide risk detection", and c23's
  to cover the 15,000 to 20,000 annual range. The integrity judge of round 1 could not refute the
  printed phrase from the stored quote.
- Speech was put on the page's terms: "One entry states what it saved", "Only the no-show entry
  states what it already saved". Slide 3 and c51 now say the tools aim to automate lab result
  messaging and generate imaging summaries, not that they draft them. Slide 7 says "routes
  patients". Slide 5's kicker no longer gives the project to UTHealth Houston. Slide 8's hook is
  "Two more expand earlier platforms." Slide 1's dek adds the more than $3.6 million (c8).
- Slide 9's unsourced "A patient can ask a UT hospital which of the twelve pilots it takes part
  in" was replaced by c54, the home page's registration link for the symposium.
- **Named by round 3's integrity judge and not repaired, because past the cap only a hard fail
  is:** the caption's first line still places the no-show entry at UTHealth Houston, slide 5
  draws a cumulative count and an annual projection at one scale without naming either period, and
  slide 6's "the other eleven describe the work" sits beside c48's 88 percent accuracy, which no
  slide prints.

**Plan values revised**, each said here because the gate asks:
- Frame 2's L* band was rewritten to 8 to 24 when the type moved onto the dark drive, and frame
  6's to 16 to 32 when only the gold block was left lit (both before pixel round 1).
- Frame 3's band was rewritten to 6 to 22 after pixel round 2 asked for a darker floor.
- Frame 5's band was rewritten to 6 to 22 after pixel round 2, the floor made the room's dark so
  the seats separate. Frame 5 is the declared VALUE CUT.
- Frame 8's band was rewritten to 18 to 34 after pixel round 3 filled the ground with a dark lot.
- Primary rects moved on frames 2, 4, 5, 6, 7 and 8 to the subjects as rendered, frame 4's to
  `[200, 500, 680, 650]` so the screen and desk read as one piece, frame 5's to
  `[40, 600, 1000, 470]` below the glazing.
- Frame 8's accent was set to `#E0956A` for its two gold bays.

## The record, first

Re-verification ran on the diff for 82 items and on fetched primaries for 21 (`f951c869`).
tx-2026-0112 moved. The PUCT's final order in docket 59315 was re-read and rehearing motions filed
on September 22nd were added as c6 and c7. Boundary blocks were written for tx-2026-0041 and
tx-2026-0055 in the claim-source boundary v1 form, and tx-2026-0046 was re-measured. Unconfirmed
history notes were rewritten against their titles, and unverified absence claims were removed.

Admitted (`776790be`): tx-2026-0201, UT REAL Health AI's 12 pilot projects, and tx-2026-0202,
ERCOT's energization pause. Held: a UT Austin item on its pilot, whose source answered 403 to this
project's client, so it was not admitted on a secondary. Discovery polled the Federal Register and
the PUCT and found nothing actionable.

After the panel, tx-2026-0201's summary and history note were reworded (`5ab73ecb`), and one
history note on tx-2026-0065 was split under the sentence backstop (`22b38ecd`).

## Sources that behaved differently from the registry

Appended to `knowledge/shared/SOURCES_FIELD_LOG.md` (`273de9e1`): the PUCT interchange document
path, Oncor's robots.txt not answering for a second run, tech.utexas.edu and www.faa.gov answering
403, and yahoo.com inside the crawl boundary's refusals.

## Instruments

All eleven instrument checks exited 0.

## Did this run stop and wait for a human

The interim reading (Phase 17) measured 1,235 tool calls with 370 over the audit's threshold, the
longest 36.1 seconds. None was a dialog. This is the queued `prompt-audit-reads-auto-mode-as-human`
defect, now at repeat 1: the audit reads the auto mode classifier's seconds as a human's wait. The
no-stall hook was armed, judged the session unattended from SessionStart and refused nothing.
**This reading is interim.** Phase 19 takes the reading that counts, immediately before the email.

## The weekly machine pass

Due early: `acceptance-lists-trivially-satisfiable` reached repeat 2 when this run's pixel critics
named it again. The `carousel-upgrade-engineer` made four changes, each verify command rerun here
before the commit:
- the kit tractor (`semi_truck`) rebuilt at the judges' named fix from no. 41
- the kit school bus's yellow lip across the front wheel removed
- `dossier_check.py` requires, from storyboards dated 2026-10-06, that each acceptance list name
  the CRAFT PLAN's largest object and set a lower bound on a visible size
- `ship_images.py` takes `og.jpg` from slide 1 by name

The kit person, still the most named model, could not change while this deck used it. It is the
next pass's first job. Backlog items 6 to 8 of 2026-10-05 carry the engine and maintainer
proposals.

## Queued for the next pass

`near-plane-zfight-on-card-skins`, `hospital-bays-built-in-chassis`, `lamp-pool-reads-only-near`,
`txadd-resets-receive-shadow` and `grid-ground-from-whole-outside` were added (`e10c0e41`).
`prompt-audit-reads-auto-mode-as-human` was raised to repeat 1.

## Craft memory

Confirmed: `acceptance-items-need-a-floor`, `read-the-repair-at-feed-scale`,
`the-plan-is-not-the-product`, `a-gate-fix-can-create-an-editorial-defect`. Added:
`stipple-means-check-the-near-plane` and `a-motif-state-keeps-its-class`.

## Things this run did not do

- It did not reorder the deck after the flow critic's round 1, and it did not run a second flow
  round.
- It did not recompose frame 5 at a standing eye, the fix all three judges named in round 3.
- It did not repair the three looser phrasings round 3's integrity judge named, because the round
  cap allows only a hard fail.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 42 verified claim(s) |
| render         | WARN   | 9 slide(s), 2 overflow warning(s) |
| qa             | WARN   | 0 fail(s), 5 warn(s) |
| aggregates     | PASS   | 15 declaration(s), 19 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 6.88 MB, vector |
| score          | WARN   | 7.124 at the round cap after 3 round(s), the finished deck ships; 8.0 top rung, shortfall named |
| labels         | PASS   | 42 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 81 published string(s) read from one list, every universal names its set |
| verbatim       | PASS   | 2 declared fragment(s) over 9 of 9 dossier(s), every one a literal substring of its own claim's quote |
| dossiers       | PASS   | 30,120 chars planned |
| caption        | PASS   | 159 words |
| craft floor    | WARN   | 9 frame(s), median 1996, floor 359, 1 quiet |
| plan vs render | WARN   | 11 of 32 acceptance item(s) checkable |
| texan          | WARN   | places Austin, Houston, San Antonio / body NO / deadline yes / next step NO |
| absences       | PASS   | 10 of 10 scoped to a named document |
| numerals       | PASS   | 12 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
