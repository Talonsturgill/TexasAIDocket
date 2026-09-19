# Run record — carousel no. 29, September 19th, 2026

**Deck.** The law did not change and the enforcement did. On September 14th the Office of the
Texas Governor told the Texas Water Development Board to enforce the state water use survey
against data centers, naming a criminal offense and a TCEQ permit ineligibility that the Texas
Water Code already carried, and ERCOT issued a market notice the same day carrying the board's
own water questions with a deadline on them.

**Both deliverables shipped in one commit range**, the record and the deck together, so the site
was never built from a record half a run old.

---

## THE RECORD, which is the first deliverable and the one that matters most

| | |
|---|---|
| worklist | 126 due at wake, cleared to 0 |
| re-verified | 87 items read against their own sources, movement lines written for all of them |
| admitted | 3 new items (tx-2026-0171, 0172, 0173) plus one folded in |
| backlog | empty at wake and empty at close |
| docket | 145 to 149 items, 846 claims, `docket_build --validate` clean |

**One claim had MOVED and the movement was in the quote's own shape rather than in the facts.**
`tx-2026-0078`'s claim quoted a span that ran from a committee page's heading into its first
meeting row, and two new September sittings pushed the row out from under it. The August 19th
hearing is still listed and nothing about the item changed. The claim was narrowed to
`"August 19, 2026 8:00 AM"`, which is the sentence the record actually needs and the one a future
sitting cannot break.

**The fact checker caught two attribution defects that had already reached the ledger**, and both
were corrected in `ledger/docket.json` before anything was built.

- The state water plan sentence is the **Governor's office describing the board's position**, not
  the board speaking. Every surface that carries it, the record, frame 6 and the caption, now says
  "The release states" in front of it.
- The ERCOT notice's stated AUDIENCE is broader than its body's recipient rule. The record no
  longer says every developer of 25 MW and larger receives the request, and neither does the deck,
  which is the subject of the deck's own round 1 hard fail below.

**A COMPLIANCE SLIP, THIS RUN'S OWN, AND IT IS THE FIRST THING IN THIS RECORD FOR A REASON.**
`out/2026-09-19/recheck.py` is a helper this run wrote to fetch what `reverify.py` can't read, and
its copy of the crawl boundary was a tuple of HOSTS. Three entries on that boundary are hosts and
one is a PATH, `capitol.texas.gov/TLODOCS/`, on a host that is otherwise allowed, so a host-level
guard passes it by construction. One `/TLODOCS/` URL was fetched before the shape of the guard was
noticed. **Nothing from that fetch reached a claim, the record or a frame.** The guard now checks
paths as well as hosts, case-insensitively, and the finding is in
`knowledge/shared/SOURCES_FIELD_LOG.md`.

The lesson is not "read the boundary more carefully". A boundary with two KINDS of entry needs a
checker that knows there are two kinds, and a run that re-implements the boundary in a scratch
script will re-implement whichever kind it looked at first. The durable answer is one shared
checker every fetcher calls, and it is a proposal rather than a change this run made, because the
fetchers it would reach across belong to more than one lane.

---

## THE DECK

**Nine frames, world FIRSTLIGHT. A caliche pad on the Edwards Plateau at first light.**
One light, low in the east off the camera's left shoulder at 14 degrees, so every lit face is a
left face and every cast runs right. One halftone at cell 7 and angle 22 across all nine frames.
One accent, comal `#2A7A9E`, which lands only on water somebody holds a number for.

### Round 1 stopped the deck on two hard fails, from two different judges

**The integrity judge's, and it was an editorial fault rather than a drawing one.** The cover's dek
read "The request goes to developers of data centers 25 MW and larger." and frame 2 asked "Who the
request reaches" over "Twenty five megawatts and larger." This run's own `claims.json` rejects
exactly that and supplies the permitted wording: copy may say the request is AIMED AT developers
of that size and may not say every one of them receives it. The notice's body restricts its
recipients to two narrower conditional groups, so the claim was wrong in both directions at once.
**The rejection named the word "every" and the copy dropped the word while keeping the assertion.**
`SELECTION.md` had the safe phrasing in it the whole time.

The cure moved the cover onto c4, the Texas Water Code's own requirement, which also put the word
WATER on a deck whose nine headlines had not carried it once, and changed frame 2's kicker to the
fact checker's own permitted wording.

**The craft judge's, and no gate in this suite could have seen it.** Frame 3's letterhead read
`FFICE OF THE TEXAS GOVERNOR`, because a drawn block sat at the sheet's left margin, which is the
exact origin of the letterhead line. `machine_qa` raised a tiny-text warn on that same string and
never saw it was occluded, because it reads the DOM and a reader reads pixels. The block moved to
the sheet's right margin, where a seal sits.

### What the panel converged on, and it was the same sentence three ways

Three judges, three lenses, and all three named flat drawing where the deck's argument needed a
modeled one. **`TXOBJ.sprite("data_center")` carried a 130 m hall on frames 1, 6 and 8 at three
different distances and rendered at all three as tall square merlons on a single cream fill.** The
words used for it were "a crenellated battlement", "one flat cream plane" and "the weakest frame
in the deck". A catalogue sprite is a good object at the size it was drawn for and a silhouette at
any other. Each of the three frames now builds its own hall from the frame's own projection, and
each differently.

**Four figures at true scale were inked bright while standing against bright halls and lit
caliche**, and one judge reported that no figure was findable on the cover at all. They were all
present in the code and all the right size. A figure is read against what is behind it, never
against the palette. Frames 1, 4, 8 and 9 ink theirs dark now. Frame 7's stayed bright because its
ground is dark, which is the same rule rather than an exception to it.

**Frame 3's tailgate was "horizontal wallpaper stripes".** Its ribs were drawn as full-width
rules, and a stripe that reaches both frame edges belongs to the FRAME rather than to an object,
so nothing in the drawing said where the gate stopped. It is a trapezoid now with its own side
edges inside the picture, converging ribs, pressed swages, latch bezels and the bed walls behind
it, and the sheet on it has the corner curl its own header comment had been promising since the
frame was written.

### What the plan got wrong, said plainly rather than edited away

**The planned value arc came in systematically high and the plan was NOT rewritten to match the
render.** The dossiers asked for frames in the thirties and forties and the deck measured
`[12.4, 35.7, 32.5, 16.7, 8.3, 10.7, 19.1, 21.3, 18.5]` at 432px against a planned
`[16, 22, 32, 26, 38, 34, 44, 40, 26]`, a miss of thirty points on frame 5 and twenty five on
frames 7 and 8. `panel_ready` passes because its check is on the deck's MEDIAN rather than per
frame, so nothing stopped it and nothing should have. Editing nine dossiers to match nine renders
is the inversion `measure.py`'s own docstring exists to prevent. Both tracks are in
`measurements.json` and the gap is the finding.

**Frame 2's dossier described a frame that had been thrown away.** The frame was redrawn as the
property line after `bespoke_check` measured the deck as "one drawing repeated", and only its
subject line was updated, so two judges graded a picture against a plan belonging to another one.
The dossier is rewritten, including the two things about that frame that are deliberate and read
as defects against the old plan: it carries the accent, and it is the only frame in the deck with
no person in it.

**The chassis prose described a different deck entirely.** `2026-09-19-firstlight.js` named a
staff gauge, a pump, a brass register in a hole in the ground and the state's own instrument
shelter, none of which is drawn anywhere in these nine frames, and its accent law named the wrong
frames. The functional `declare` was correct the whole time, so nothing rendered wrong. What was
wrong is that the one place a frame author goes to find out what deck they are drawing was telling
them about another one.

### Frames 7 and 8 still run the calendar backwards, and that is a decision

Frame 7 carries October 14th and frame 8 carries October 12th. A judge named it in round 1 and the
order was not changed, because swapping the two would renumber the deck, move the archetype
rotation and relocate the continuity device for a gain measured in one reader's reading order.
What was changed is the frame that made the pair fail: frame 8's hall stood at the courthouse's
own distance, and a 130 m building at 34 m is half the frame in one value with no sky above it.
It stands at 48 m now.

### Round 2 found a second hard fail, and it was made by round 1's own repair

`first_comment.txt` did not list `c4` while the cover printed `c4 TEXAS AI DOCKET`. Round 1 moved
frame 1 onto c4 and frame 5 off c17 and c21, and nothing re-derived the one published surface
whose entire job is resolving the ids a reader sees. `sources_block.py` exists for exactly this
defect, its docstring opens on a deck that printed sixteen ids over a block listing seven, and it
would have gone red the moment it was asked. It was not asked. `run_state.json` went on reporting
that gate as exit 0, which was true of the deck before the repair and false of the deck that would
have shipped.

**The lesson is the judge's own sentence and it is going in the backlog rather than into prose
here.** A cite-line edit has to invalidate every artifact derived from it. This run applied that by
hand in round 3 and the mechanism is a proposal.

Round 2 also found two modals flattened on frame 7, "reports back October 14th" where c10 says
shall update BY that date, and "noncompliance is referred" where c8 says the board MUST ENFORCE
those remedies INCLUDING referral. The same run had repaired that exact defect on frame 9 one
round earlier and left these standing, and the caption had it right on the same day. Both are the
source's wording now.

### Round 3 drew what round 1 had answered with a comment

Frame 5's three elevations laid casts 7 px tall on a 1350 px frame. Round 1 was told and rewrote
the COMMENT above them. That is the worst available response to a drawing note and a judge said
so in as many words. Round 3 drew the casts, moved the route off the mast it was crossing against
the frame's own stated rule, corrected a scale comment that declared 0.19 metres per pixel over
code holding 0.058, and filled the 55 percent of that frame a judge had measured as empty with a
raking ground apron and the three leaders the dossier had been promising since planning.

The same round inked frame 7's two figures dark, which is the cure round 1 applied to four other
frames and did not carry across, and drew the six column casts that frame's acceptance list has
always required, at positions read off the catalogue's own geometry rather than eyeballed.

**The deck's own motif was a flat blue ellipse on four frames.** Two judges used almost the same
words for it. The accent law in this deck turns on the word GAUGED and the drawing never carried
it, so the recurring object registered as a colour rather than as the one thing on the frame
somebody holds a number for. The chassis hands out `N.tank` now, with a contact, a rim, the water
inset and a staff gauge standing in it, and all four frames call it.

### On publishing the size of the gap, which a judge asked for twice and the deck does not do

The reader judge's one fix was a line saying nobody publicly knows how much water these sites use.
**The deck already publishes the gap and does not publish a size for it, and that is deliberate.**
Frame 6 carries c5, which is the state's own sentence that the board can't write a state water
plan while it is denied detail on existing and anticipated water consumption. That is the gap, in
the voice of the party that has it.

What the deck does not say is HOW BIG. Neither fetched document publishes a count or a share of
unreturned surveys, which the fact checker established and wrote into the rejections, and the
house law asks for the size of a gap to be COMPUTED rather than asserted. There is nothing here to
compute it from. Publishing an unscoped negative would also fail `absence_check`, correctly, since
this run registered no absence claim for it. **The miss is at Phase 6 rather than at Phase 12**: an
absence worth publishing is worth registering as a claim with its own id while the documents are
open, and this run did not.

### Rounds 4 and 5, and what four rounds of judging actually taught this run

**The panel found the same class of fault four times wearing four different frame numbers**, and
the run repaired the instance each time. Round 3 said slide 8's numerals block declared a claim
carrying no numeral; round 4 found slides 1 and 5 doing the same thing and the run had fixed only
slide 8. Round 3 said slides 7 and 8 both claimed an identical rect the drawing does not have;
round 4 found slide 8's acceptance item still demanding it fifty lines below its own retraction.
Round 4's integrity judge wrote the lesson in one sentence and it is the most useful thing any
judge said this run: **repair the CLASS across all nine before re-scoring, not the item that was
pointed at.** Round 4's repair pass finally did, including three declared focals that named parts
their drawings do not have.

**A repair can go invisible for a NEW reason and that is not a repair.** Round 2 rebuilt frame 5's
three casts because a 7 px sliver could not be seen at any size. Round 3 then drew a ground apron
across the same band, after the elevations, so the hatch went straight over the wedges. Round 4's
craft judge found it by reading the draw order against the render and it is his one-sentence fix.
The apron is drawn before the elevations now, which is this repo's own instinct about drawing a
ground plane before what stands on it, arrived at from the other direction.

**Nine frames named neither institution until the last round.** Every frame said "the board" and
"the grid operator", which two judges called a real reader kindness and a third measured as the
deck's largest story defect: a reader finishes nine frames unable to search for either body.
Frame 5's dek now carries c13's own wording and names the Texas Water Development Board and ERCOT
in full, and frame 9's headline gives its report an owner so it can't be read as frame 7's
October 14th report slipping to December.

---

## Degraded

- **The vector PDF is 61.5 MB against 6 to 14 MB for every deck before it.** Three hypotheses were
  MEASURED rather than argued: a coarser screen cell was worth about 5 MB, a raised screen floor
  and a higher gamma were worth nothing at all, and cutting the film grain and the dither was
  worth about 9 MB, which is why the grain runs at 0.012 against the house 0.044. What is left is
  that this is the first deck to run the full halftone across the whole of all nine frames, and
  round 1's repairs added drawing to six of them. It ships DISCLOSED rather than cured.
- **`texan_check` reads "places NONE".** Neither document names a county, a city or a volume of
  water, so the deck names none either and carries its place on art alone.
- **The Supabase scanner ceiling check did not run.** No connector for it exists in this
  environment. It is not a failure of the check and it is not evidence the ceiling is fine.
- **`ledger/carousel/captions.json`'s exclusion lists are one shipped entry behind**, for the third
  recorded time. The caption room was handed a structure list omitting September 18th's Clock and a
  director was assigned Clock two days after Clock shipped. The critic caught it at the judging step
  rather than the briefing step, which is the one place `CAPTION_CRAFT.md` says the room must never
  be told no, and it cost the room's one rewrite. The fix is one change in two lanes at once and
  stays in `UPGRADE_BACKLOG.md` until a maintainer lands both halves.
- **This is the fifth ERCOT request in the dedupe window and `dedupe_check` cannot see that.** It
  compares entities and keywords, and an INSTRUMENT repeat is invisible to both. Four earlier run
  records have each written this in capitals. `c18` separates this notice from the Batch Zero
  request in the notice's own words and is printed on no frame.

---

## Release decision: SHIP AT 6.966, UNDER THE BAR, AT THE ROUND CAP

`config/carousel/scoring_rubric.yaml` sets the threshold at 8.0 and `max_rounds` at 5. The panel
ran all five. Its medians, per round, are **6.398, 6.88, 7.12, 6.95 and 6.966**, and the final
per-judge scores are [6.89, 7.374, 6.87] with a spread of 0.504, which is the tightest agreement of the run.

**No judge raised a hard fail in rounds 3, 4 or 5.** Two were raised earlier and both were cured
and verified by the judge who raised them: round 1's cover overclaim about who receives the
request, and round 2's sources block that had gone stale against round 1's own repair. Every
judge this round stated plainly that `ship: false` was a threshold dissent rather than a veto and
that they had looked for a hard fail and refused to manufacture one.

**So the bounded-search rule applies and the deck ships at 6.966.** The routine's own words:
past the cap the run ships at whatever the median is, stated honestly in the email, with the run
record saying it shipped under the bar and by how much. It is 1.034 under.

**Where the deck lost its points, in the judges' own weighting.** `artwork_craft` at 0.22 is the
heaviest criterion and it scored 6.4 to 6.8 in every round. The single sentence three judges wrote
in three different rounds is the same one: **four frames give 30 to 55 percent of the canvas to
empty graded ground, so the detail budget sits where the frame starts rather than where the
argument lands.** That was round 1's finding and it is still true at the cap, and it is the reason
the value arc the deck DECLARED could never print: a frame whose lower half is dark caliche cannot
reach a planned median in the forties whatever is drawn in its upper half.

**What was repaired across five rounds**, and it is a long list because the panel earned it: the
cover's audience claim, a stale sources block, three flattened modals, four miscited frames, a
letterhead block sitting on its own first glyph, a catalogue sprite that rendered a 130 m building
as battlements on three frames, four figures inked invisible against their own grounds, six column
casts that were never drawn, a scale bar that was decoration pretending to be rigour, a stock tank
motif that was a flat lozenge on four frames, a tailgate with no edges, a cut that read as three,
a chassis describing a different deck, and eleven separate assertions in the plan that named parts
the drawings do not have.

**What ships unfixed and goes to the next run:** the empty lower thirds, the unprinted value arc,
frame 4 as a detour, frames 7 and 8 running their dates backwards, the deck naming no Texas place,
and a 61.8 MB vector PDF. Each is in Degraded below or in `knowledge/carousel/UPGRADE_BACKLOG.md`.

**Four planning corrections landed AFTER the round 5 panel read the deck**, and they are recorded
here rather than hidden: seven sibling assertions of the gable falsehood in frames 1 and 8's
dossiers, frame 6's focal, frame 5's focal and value_structure, and frame 2's cite line gaining
`c1`, which is the one that touched a rendered frame. **Only that last one changed a pixel**, by
three characters in a footer, and every gate was re-run and the deck re-assembled after it. The
judges' scores are reported as they were given.

---

## Gate status

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 21 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | PASS   | 9 slide(s), zero fails, zero warns |
| aggregates     | PASS   | 3 declaration(s), 3 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 61.77 MB, vector |
| score          | STALE  | score.json predates the newest render, so it describes a deck that no longer exists. Re-run it |
| labels         | PASS   | 34 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 62 published string(s) read from one list, every universal names its set |
| verbatim       | PASS   | 2 declared fragment(s) over 1 of 9 dossier(s), every one a literal substring of its own claim's quote |
| dossiers       | PASS   | 41,444 chars planned |
| caption        | PASS   | 139 words |
| craft floor    | PASS   | 9 frame(s), median 6841, floor 1231 |
| plan vs render | WARN   | 9 of 48 acceptance item(s) checkable |
| texan          | WARN   | places NONE / body yes / deadline yes / next step yes |
| absences       | PASS   | 0 of 0 scoped to a named document |
| numerals       | PASS   | 3 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->

**THE `score` ROW READS STALE AND IT IS TELLING THE TRUTH.** `score.json` was written when the
round 5 panel reported, and `render/slide-02.png` was re-rendered after it, so the file predates
the newest frame exactly as the row says. What changed in that re-render is **three characters in
a footer**: frame 2's cite line gained `c1`, because the round 5 integrity judge found that the
frame's dek draws its first sentence from c1 while its footer printed only c12 and c13. Every
other pixel in the deck is the one the panel scored, the three report cards are reported as they
were given, and the deck was re-assembled and every gate re-run after the change.

The row is not softened and the file is not touched to clear it. `gate_status` exists to notice a
re-render that nothing else in a run would, it noticed one, and the honest answer is to say what
it was rather than to make the row green.



---

## A CODE REVIEW ON THE PULL REQUEST, AND SEVEN OF ITS EIGHT FINDINGS WERE RIGHT

The Codex reviewer read PR 331 at `d217cd0f` and posted eight findings, seven of them marked P1.
Every one was checked against the primary source or against this repo's own claim record before
anything was changed, and the record now carries the repairs. What follows is what each was, and
the two that are worth more than their fix.

**The one that should never have needed a reviewer.** `tx-2026-0167` was `tx-2026-0141` admitted
a second time, off the same UT San Antonio article reached over `http` rather than `https`. Its
four claims were already carried by 0141 as c9, c10, c5 and c6, so nothing needed merging and the
item was removed outright. **The same duplicate, from the same URL pair, was admitted and removed
on 2026-09-18 as well.** A code review caught it both times and the admission phase caught it
neither. `dedupe_check` compares entities and keywords, so one article at two schemes reads as
two decisions and always will until something normalises the URL. That is now the first proposal
in the backlog rather than a third history note.

**The one that was a false statement in a title.** The item read "Governor directs the water board
to prosecute data centers that did not return the state water use survey". The board does not
prosecute. c8's own quote says "referral to the appropriate County or District Attorney", and the
title propagates into the item heading, the feeds, the metadata and the generated questions, so
the wrong verb was telling a reader the wrong thing in four places at once. Retitled to what the
directive actually orders.

The other five record repairs, each verified the same way:

- **`geography.on_ercot` was `false` on a statewide water directive**, which renders as a flat
  "No. It sits outside the ERCOT interconnection". The question does not apply to a reporting
  requirement, and `null` is the state the schema added on 2026-09-03 for exactly this, after a
  review bot found the same defect on PR 252. Where it is neither measured nor modelled, it is
  not published.
- **Two deadlines were stored `statutory_deadline` and neither was created by a statute.** October
  14th comes from the Governor's directive and October 12th from ERCOT's market notice. The site
  prints the kind verbatim, so both mis-stated the legal authority behind a real clock.
  `administrative_deadline` is added to `DATE_KINDS` and to the calendar's label map, with the
  same reasoning `expires` and `passed` carry: the record had a state the field could not
  express, so the field widens rather than the record rounding itself off.
- **`tx-2026-0173` asserted far more than its one stored quote could carry.** The university's
  release was re-fetched and two claims added in its own words. The summary was also wrong in a
  way nobody had flagged: it named "a Bachelor of Science and a Master of Science" where the
  release says only "bachelor's and master's degree programs". The history note claimed the old
  programs are "closed to new entry", which the release does not say, and it now says what the
  release says instead.
- **`tx-2026-0172`'s summary said the provider files on the developer's behalf and no claim
  carried it.** The market notice was re-fetched and it says so outright, "Each TSP or DSP must
  submit the RFI in RIOO on behalf of the data center developer", so the claim was added rather
  than the sentence trimmed. A British spelling in the same summary was corrected with it.
- **The web edition asserted a global absence.** "No enforcement action has been announced" reads
  as an exhaustive check of TWDB, TCEQ and every county and district attorney, and this run read
  two documents. It now says that neither document announces a completed action and that whether
  something was filed elsewhere is not a question these two can answer.

**THE EIGHTH FINDING WAS WRONG, AND CHECKING IT FOUND A REAL DEFECT POINTING THE OTHER WAY.** The
reviewer read frame 5's three-body chain as contradicting the docket summary, which says the
developer does not file its own response. It does contradict it. What the reviewer assumed is
that the summary was the sourced side and the frame was the lapse, and the opposite was true: no
claim anywhere in this run established the filing mechanism, and the deck's count is exactly what
its claims support. **The unsupported sentence was in the public record, which is the more
serious of the two places for it to be.** The fix is therefore in the record, above, and the deck
is unchanged.

The frame stands on its own terms as well. Its kicker is "Who asks whom", and all three labels are
individually true and claim-traced: the board authorizes the asking, the operator asks on its
behalf, and the developer answers under a notarized attestation, which c16 says in as many words.
The provider transmits that answer and neither asks nor is asked. **That is a scoped count rather
than a wrong one, and the scope is printed on the frame.** Re-rendering a scored and assembled
deck to widen a count its own kicker already bounds would have cost a full render, gate and
assembly cycle to make a true frame differently true.

**What this round is really evidence of.** Seven defects in the public record, in one day's
admissions, and the local suite was green over all of them. Not one is a thing a gate here looks
for: a duplicate reachable only by normalising a URL, a verb that overstates a legal power, an
enum that answers a question that does not apply, a second enum that mis-names an authority, a
summary that out-runs its claims, a claim that was never recorded for a sentence that needed it,
and an absence with no scope. `numeral_lint` would pass all seven, because not one of them is a
number. **The gates here measure whether a number can be traced and whether a file agrees with
the file beside it. Six of these seven are about whether a SENTENCE is true**, and the only thing
that has ever caught that class in this project is a reader, human or machine, going through the
copy a claim at a time.
