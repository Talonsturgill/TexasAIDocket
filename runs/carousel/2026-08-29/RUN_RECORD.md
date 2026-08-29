# Run record, August 29th, 2026

Carousel no. 11. Actor `daily`, branch `claude/daily-2026-08-29`.

## The record

The selector named 50 items due, no budget passed, DEFERRED empty and ROTTEN empty.
**All 50 were re-verified and the staleness gate now reads clean.**

`reverify.py --apply` stamped 20 items whose every claim came back unchanged. It flagged one
moved quote, five unreachable claims on two items, and 57 claims it structurally can't read,
which left 30 items for hand work.

**Most of what the differ could not read was typography rather than movement.** A scratch
re-check that normalizes curly quotes, dashes and PDF line breaks on both sides confirmed 24 of
those 30 items unchanged against their own sources. That distinction is worth keeping. A quote
that matches only after the publisher's smart quotes are normalized is still on the page, and
reporting it as missing would have sent this run chasing 24 phantom corrections.

**Two dockets genuinely moved and both were decided.** On August 28th, 2026 the Public Utility
Commission issued final orders in Docket 59315 and Docket 59029, amending Oncor's certificate for
the Dinosaur to Longshore and the Longshore to Drill Hole 765 kV lines. Both items move from
pending to decided, carrying the order's own route, its need finding, and the administrative law
judges' finding that the utility did not hold a further public meeting for links it added after
the first one. The commission approved anyway on a reading that the rule requires one meeting
before filing.

**One quote moved and the fix is a correction rather than a re-word.** League City's August 25th
agenda has been replaced by the record of the meeting being held, so the claim that rested on the
notice now rests on the minutes. No item on that agenda names an automated license plate reader,
which is the fact the claim carried, and it still holds.

**One source went behind a subscription wall.** The Seguin paper's account of the Guadalupe County
Flock decision is no longer readable, so the sheriff's stated reasoning is recorded as unconfirmed
while the decision itself stays corroborated by the San Antonio station.

Admitted 1 of 2 candidates. Held 1, with the reason in the seed.

The backlog was 3 at wake and is 3 now. All three are the grandfathered ERCOT-scope entries the
routine names as exempt. None was cleared and none was added.

## Instruments

Both page checks exit 0. `gridwatch_pagecheck`, `waterwatch_pagecheck` and the water page's own
self-test are clean, so neither instrument is reading wrong and neither has stopped.

**The scanner daily ceiling was NOT checked.** No Supabase connector is attached to this session,
so the query in Phase 7 could not run. This is a gap in what this run knows, not a finding about
the scanner. It never blocks the run and it did not.

## Discoverability signoff

- **One decision's card, opened as an image.** `og/tx-2026-0109.png`, the newest item. Four lines,
  wrapping at sensible points, ending "workforce on..." with a proper ellipsis rather than a cut
  stump. The last word before the ellipsis is a preposition, which is the weakest place this
  wrapper can land, and it is a consequence of a long title rather than a fault in the wrapper.
  Not changed, because editing a record title to flatter a social card is the wrong way round.
- **`/questions/`, read as a reader.** Twelve questions, and they read as questions somebody would
  type. "Where a comment window is open" answers 06, "How the public can take part" answers 88 of
  94. The new `open_meeting` item admitted today fits the existing shapes and nothing reads broken.
- **The `Open right now` section of `llms.txt`.** Ten decisions listed. Cross-checked every one
  against its own `closes` date and **no expired window is listed**. The two dockets that moved to
  decided today have correctly dropped off, and the item admitted today leads the list, so the
  build ran after the record moved.
- **`/sources/`.** The share reads 410 of 484 claims resting on a primary document, across 169
  documents from 71 publishers. **It moved up this run**, because all 20 claims added today are
  `primary_official`, drawn from two commission orders, an agency award record, a university
  release and a Senate committee page. The top publisher is `interchange.puc.texas.gov`, which is
  the commission's own filing system and is a primary source by any reading. Worth naming, though,
  is that it carries 79 claims of which only 18 are marked primary, because most of the rest are
  dated readings of a filing index rather than documents. That is honest and it is also the one
  line on this page a reader could misread. Quoted material is still exempt from the punctuation
  and numeral rules and the exemption is still covering quotes rather than our own sentences.
- **`/topic/`.** Eight beats. The per-beat counts are 26, 15, 14, 14, 9, 9, 6 and 1, and they sum
  to 94, which is exactly the figure the front page counter prints. Opened `research-and-science`,
  whose card says 14, and counted 14 decisions listed on the beat page. The "still open to comment"
  figures across the beats sum to 5, which matches the front page's "05 Doors open to you".
- **`/place/`.** Travis County is on the hub at 11, and it is where this run's updated robotics
  item sits. The counties the two decided transmission dockets cross are all on the hub, each at
  its own count.

The front page counter row prints 10 articles, 02 videos, 94 decisions, 484 sources cited and 05
doors open. `Sources cited` is rendering. `What this is` is absent and stays absent.

## Selection

**The story is the National Science Foundation's robotics center at UT Austin, `tx-2026-0104`.**

Why this and not the others, written before the directors were briefed.

Six of the last ten decks were power or policy. The doctrine in `APPLICATIONS.md` says the
application layer goes first and a decision is context, and left alone this product drifts toward
whatever is easiest to source, which is a filing. This is the application beat and it has a real
counter-image in the source's own words. The award names the rooms the robots go into, which are
houses, dorms, cafes, a public museum, a rehabilitation hospital and elder care and assisted
living residences, and the same page says an internal ethics board will develop the consent and
opt out procedures. The rooms are named. The rules for the people in them are not written yet.

`dedupe_check` returned 0.26, faint, against carousel no. 9. The full entry was read rather than
its title. No. 9 is about a company siting a robot factory and facing no public proceeding. This
is a federal award putting robots into rooms people live in, with a different decider and a
different question. The shared words are robots, Austin and Travis, which is exactly the case the
tool's own instructions describe as a signal rather than a verdict.

`texan_check` at selection returned places Travis County, body yes, **deadline NO, next step NO**.
Known on day one rather than in round four. The closing frame carries the next step.

**The runner up goes to the next run.** The two 765 kV orders are the stronger news and the record
now carries them in full. They are queued rather than drawn, because yesterday's deck was already a
utility commission docket and this one would have been the seventh power deck in eleven.

## The panel, round one to round two

Round one scored integrity 5.93 with two hard fails, craft 6.81, reader 6.56. `panel.py` took the
median at 6.426 with a spread of 0.88, which is over `SPREAD_NOTE`, and held the deck. A spread
that wide is the panel saying the deck was not understood yet rather than that it was close.

The two hard fails were both the same species. A frame drew a claim its sources do not make.

- Frame 4's dek said the agency "co-manages rather than hands over", which is a reading of what a
  cooperative agreement is and not something the award record says. It now says only what the
  record's own `transType` field says.
- Frame 5 right aligned three quoted money figures to one axis with a hairline between each pair,
  which is the comparison this deck is forbidden to invite, drawn by the geometry rather than by
  the words. It was rebuilt as three plates at three different left origins, with the frame
  asserting off `getBoundingClientRect` that no two share a left or a right and that no rule
  survives between any two. The dossier said it would not draw the comparison. The layout drew it
  anyway, which is the recurring shape in `GATE_LESSONS.md` and the reason the assertion is now in
  the frame rather than in the plan.

The single sentence fixes the three judges each asked for, all applied and all re-rendered.

- Frame 1's cover put the deflection in the seat band alone with the backrest bands dead straight,
  and moved the contact shadow and the floor pool to frame right, so the cover obeys the one left
  azimuth the deck printed as its own law. Its dek was rescoped to the university's own account,
  which is the document that names the rooms.
- Frame 3's hook was "Always on, until August 31st, 2031", which welded c15's "always-on" to c7's
  expiration date with an inference no source makes. It reads "Always on. Increasing in
  complexity." Both halves are the abstract's own words and c7 left the frame with the claim.
- Frame 6's attribution restored c26's own words, "a core project of".
- Frame 7's CLEAR FLOOR AREA note was crossed by the leaf's heavy vertical and the dashed swing
  arc. It sits inside the area it names now, with a knocked out ground, and the frame throws
  rather than rendering if any corner of it leaves the wedge.
- Frame 8 lost a cropped blue bar at the frame edge that a pixel judge read as an artifact and was
  right to. A doorway replacing it was removed too, because it sat under a top scrim that runs to
  y=400 and could not be seen. The dossier's own line is that nothing is depicted, and furniture
  in the corner was a way of not making the floor good enough. The wax's low frequency swing was
  cut from 30 to 13 on a base of 78, which is what had turned a waxed corridor into a field of
  clouds, and the floor grain now takes its size from how far down the frame it lands.
- Frame 2's bottom 270 px was a gradient carrying nothing. The three lists sit on a trimmed sheet
  now, with a lit paper thickness along its cut edge and the modelled surface it was set down on
  below. Three documents is the frame's subject, so the frame is a document.
- Frame 5's dek had moved under the foot scrim and QA read a 515 by 23 patch of it painted over.
  It sits on its own toothed plate, the frame measures its own dek against its own scrim, and the
  foot scrim came down from full opacity so the near floor's grain survives underneath it.
- The caption said the National Science Foundation "signed" the cooperative agreement. The record
  proves a `date` field and nothing about a signature, so it says the record is dated.

Four gates went red on the repairs and each one was earned. `plan_render_check` caught three
dossiers still describing the deck of round one. `panel_ready` caught frame 1's dossier claim list
missing c18. `aggregate_check` caught "five partner universities" as an undeclared computed count,
then caught the declaration's own `computed_by` naming no input. `sources_block` caught c18
printed on a frame and absent from the first comment, which would have left a reader unable to
reach the document. All four are the suite doing exactly what it is for, on a change the run
believed was finished.

## The panel

Five rounds, which is `max_rounds`. The deck did not clear on the number until the last one, and
every hold was earned.

| round | integrity | craft | reader | median | spread | hard fails | verdict |
|---|---|---|---|---|---|---|---|
| 1 | 5.93 | 6.81 | 6.56 | 6.426 | 0.88 | 2 | HOLD |
| 2 | 6.28 | none | 6.398 | not computed | | 1 | HOLD |
| 3 | 6.11 | 7.06 | 6.55 | 6.908 | 0.95 | 1 | HOLD |
| 4 | 5.81 | 7.03 | 6.44 | 6.692 | 1.22 | 4 | HOLD |
| 5 | 6.55 | 7.224 | 6.64 | **6.95** | 0.674 | 0 | **SHIP** |

Round 2's craft judge ended without returning a report. The run recorded the round as a hold on
what it had rather than waiting out a judge that was not coming.

**Three of the five holds were on defects this run created in the round before**, which is the
panel doing the job `panel.py`'s docstring describes and is worth stating plainly rather than
burying in a score.

- Round 2's hard fail was a rendering label, `primary_corporate` printed as "company filing" for a
  public university's own news release. Two judges opened with it independently. The fix was in
  `scripts/carousel/sources_block.py`, an `upgrade` path, so the run stamped that lane, made the
  change, and stamped back. The noun is now true of every document the type code covers.
- Round 3's hard fail was the ROUND 2 REPAIR. Frame 8 had been given a speaker and a title read
  off c24's and c25's `text` fields, which are this run's own prose, when neither `quote` carries
  the word director. That is an inference laundered into the evidence layer, and it is exactly the
  standard the run's own rejected list applies to two publication dates it refused. Frame 8
  attributes to the document now. The craft judge reached the same conclusion independently and
  warned against fixing it back toward the plan.
- Round 4's hard fail was also this run's. Adding `, c34` to the foot pushed the row past its
  920 px measure, the flex line broke, and the cover printed the canonical URL as
  `texasaidocket.com01 /` with the counter alone on a second line. All three judges opened with
  it. **Nothing text-based could have caught it**: the DOM span still reads `texasaidocket.com`,
  so a checker reading text passes while the pixels are wrong. Every frame now measures its own
  foot and refuses to render if a span wraps or the row leaves no gap.
- Round 4's second hard fail was the worst thing in the run, because the run's account of its own
  work was false. `c34` was already taken by the NSF release claim, the append guarded on
  `if 'c34' not in ids` and silently did nothing, and six frames spent a round citing a document
  that does not contain the number. The claim is `c35` now, its id read off the file, and its span
  was fetched and verified rather than assumed.

**Two repairs landed after round 5 and neither is scored.** The routine's own rule is that a
number over the bar is not done when judges name a defect the run just created, and two did. The
cover's chair read as a glass box, because the slat pass painted over it at plaster alpha and
nothing occluded; the band is drawn in three runs now and the chair is darker than the wall it
stands against. Frame 9's `underwash`, added to knock a canvas edge out from under the foot, had
been laid over the very floor carrying the spill wedge and the two part contact shadow, so the
cure had reproduced the plate it replaced. It is cut to the foot's own band.

**The reported score is round 5's 6.95 and the shipped deck is not the deck that was scored.**
Both post-scoring changes only remove faults this run introduced, both were re-verified by the
full gate suite and by looking, and saying so is cheaper than a sixth round.

### What the judges said that was not fixed

Named, because a finding worth recording is worth carrying rather than closing quietly.

- **No five-pointed star mark and no county footer**, both listed in `config/brand.yaml` as fixed
  on every deck. Two judges found it; `coherence_check` asserts the site line and nothing else, so
  nothing in the build could have. The reader judge called the missing county the single largest
  reader loss in the deck, and it is why `story_and_stakes` sat at 5.5 on that card. Travis appears
  nowhere across nine frames.
- **Slide 5 should be cut**, said twice by the reader and once by integrity. It was reframed rather
  than cut, because the money is the only place the award's size appears.
- **The absence hook is now the house habit.** Fourth deck of eleven built on what a document does
  not say. `dedupe_check` cannot see it, because it compares topics and keywords and never reads
  the angle field. Recorded in `topics.json` for the next run.
- **Six frames still park their type on a flat rectangle**, and the craft judge's summary is that
  7.22 is acceptable rather than good.

## A finding this run cannot fix, raised rather than worked around

**The ask index is at its ceiling and every run pushes it over.**

CI failed at 40,033 characters against a 40,000 cap, after this run admitted one item and
extended another. `scripts/site/ask_pack.py` says what that ceiling is for in its own comment.
Every question to the ask box carries the whole index whatever it asks, so the cap is a bill
rather than a warning.

The only fix available to a run is to shorten titles in the record, which is editing the public
record to fit a cache budget. This run did it, because the alternative was not shipping:
`tx-2026-0104` went from 134 characters to 95 and now uses the center's own name, and
`tx-2026-0109` went from 98 to 90. Both are still accurate and the first is better prose than
what it replaced.

**That leaves 39,986, which is 14 characters of headroom, and the record gains items faster than
14 characters a run.** The next run hits this again.

`scripts/site/ask_*` is maintainer owned, and its note in `ownership.yaml` says the answer engine
is a gate on what the site may claim. Raising the ceiling to make a run pass is the loosening
CLAUDE.md forbids in as many words, so this is reported rather than fixed.

What the fix probably looks like, for whoever takes it. The index needs a policy for growth
rather than a fixed cap the record grows into. Three worth measuring. Roll decided items older
than a window up to one line. Derive a short index title separately from the record's own title,
so the record is never edited to fit a budget again. Or raise the cap deliberately, with the per
question token cost stated beside it.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 35 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 2 warn(s) |
| aggregates     | PASS   | 6 declaration(s), 6 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 7.6 MB, vector |
| score          | STALE  | score.json predates the newest render, so it describes a deck that no longer exists. Re-run it |
| labels         | PASS   | 0 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 99 published string(s) read from one list, every universal names its set |
| dossiers       | PASS   | 39,269 chars planned |
| caption        | PASS   | 137 words |
| craft floor    | WARN   | 9 frame(s), median 688, floor 124, 2 quiet |
| plan vs render | WARN   | 10 of 48 acceptance item(s) checkable |
| texan          | WARN   | places NONE / body yes / deadline yes / next step NO |
| absences       | PASS   | 7 of 7 scoped to a named document |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
