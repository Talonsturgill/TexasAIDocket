# Run record, 2026-08-27, carousel no. 9

## THE RECORD, which is the first deliverable and the one that ships whatever else happens

**The worklist was cleared in full.** `docket_staleness` named four items due on the two day
leash and all four were re-verified. `reverify.py --apply` fetched twelve urls behind forty
claims, four answered 304 and eight sent a body, and none failed to answer. One item was stamped
by the script and three needed a person.

**Two claims were corrected and both corrections matter.**

`tx-2026-0072-c7` cited the commission's rolling calendar feed for an open meeting on August
20th. That meeting has been held and has come off the feed, so the claim pointed at a url that
no longer carried it and would have been re-flagged every run forever. It now cites the December
17th open meeting, which is the date the audit's own filed schedule ends on, and the item's
participation note points a reader there instead of at a meeting that has happened.

`tx-2026-0090-c7` quoted the National Science Foundation saying researchers anywhere in the
country should get their hands on this equipment. The stored quote stopped at "on this
equipment." and gave the sentence a full stop the source does not have. The speaker actually
carried on, "and work together to pursue those ideas". A quote trimmed to a shorter claim is a
quote this project broke, and it now runs to the end.

**Ten decisions were admitted.** Six cleared the promotion gate from the seed on the first pass.
`tx-2026-0102`, the UT Southwestern item stating that artificial intelligence has replaced more
than 91 percent of the human grading of medical students' clinical notes, was held for a missing
verification stamp, was re-fetched, held both its quotes word for word, and went in. Three more
were written from this run's scouts and verified against their own primary sources.

| id | what |
|---|---|
| tx-2026-0084 | Amazon's Austin robotics manufacturing siting. **This run's deck is built on it** |
| tx-2026-0085 | NSF's self driving semiconductor laboratory at Rice |
| tx-2026-0086 | NSF's open access robot run alloy laboratory at Texas A and M |
| tx-2026-0087 | Denton City Council's data center moratorium resolution |
| tx-2026-0088 | the RELLIS abatement reassigned in Brazos County |
| tx-2026-0089 | the House charge on using artificial intelligence against fraud in state spending |
| tx-2026-0102 | UT Southwestern grading clinical exam notes by machine |
| tx-2026-0104 | NSF's five year Science and Technology Center on human and robot co adaptation at UT Austin |
| tx-2026-0105 | the Texas Politics Project's August poll on data centers |
| tx-2026-0106 | Austin City Council's Item 61, taken up today, to write data centers into the land development code |

The record now holds **91 items and 431 claims**, and `docket_build --validate` is clean on
every gate including staleness.

## A BOUNDARY BREACH FOUND IN THE PUBLISHED RECORD, and repaired

**`tx-2026-0089` reached the public record citing four claims whose only source sat under
`capitol.texas.gov/tlodocs/`, which robots.txt disallows for every agent.** It was admitted from
the seed on August 22nd. Nothing between the seed and the ledger checks a claim's url against
the crawl boundary, so an item can be published that this project may never re-fetch to
re-verify. That makes it stale by construction, and it would have hard failed the six day leash
within a day.

The repair is real rather than cosmetic. `www.house.texas.gov` serves `User-agent: * /
Disallow:`, an empty disallow, and the Speaker's interim charges for every House committee are
published there in full. The item is rewritten around that document and every claim on it is
verified against it. The charge text is identical, so nothing about what the record states
changed.

**The gap itself is unfixed** and is written up as a proposal below.

## The backlog

Three entries at wake and three at close, all of them the same three geography exemptions that
predate the rule. Held steady, which the routine calls acceptable. The one entry that is
genuinely clearable is written up as a proposal below, because clearing it needs a file this
actor does not own.

## Sources

Every finding this run made about a source is appended to
`knowledge/shared/SOURCES_FIELD_LOG.md`, which is the file this actor owns. The registry itself
was not touched. The findings worth naming here are the `/tlodocs/` breach above, the
`house.texas.gov` substitute that repaired it, and one that would have cost a later run an
afternoon: **the Office of the Texas Governor's post slugs are not guessable, and a wrong guess
returns a 404 with a 90,489 byte body**, so a run checking only for a non-empty response reads
the 404 page as content.

`puc.texas.gov` answered a browser User-Agent with 200 for this session and its calendar feed
parsed to thirty one items, while a scout on the same beat recorded 503 from that host on four
attempts in the same hour. **The host is intermittent rather than closed**, and one run's
failure there is not a finding about the source.

## Instrument once over

Both instruments are green. `gridwatch_pagecheck` and `waterwatch_pagecheck` each report the
page current and holding its promises, and `waterwatch_page --self-test` passes. Nothing was
edited in either lane.

The discoverability surfaces are all clean by exit code. `media_check`, `schema_check`,
`og --self-test`, `favicon --self-test`, `truetype --self-test`, `indexnow --self-test` and
`seo_check` all returned 0.

**The scanner's daily ceiling could NOT be checked.** No Supabase connector is available to this
session, so the query in the routine had nowhere to run. That is the routine's third outcome,
which says to record it and carry on, and it is recorded here rather than left silent.

## Discoverability signoff

- **One decision's card, opened as an image.** `docs/og/tx-2026-0103.png`, which was the newest
  item at wake. The headline wraps after "campuses", "the" and "Department's", all places a
  reader would break it, and the wrapper truncates with an ellipsis after "science" on a whole
  word. Legible and correct.
- **`/questions/`, read as a reader.** Twelve questions, and they read as things somebody would
  type. "How the public can take part" and "Where a comment window is open" are the two doing
  real work. The counters print with a leading zero, so an answer count of five reads `05`,
  which is the row's own style rather than a fault.
- **The `Open right now` section of `llms.txt`.** Eight entries, cross checked against Phase 3's
  own list of open windows. All six items with a live close date are present. `tx-2026-0077`,
  whose window closed on the 25th, and `tx-2026-0073`, whose closed on the 20th, are both
  correctly gone. The build ran after the record moved.
- **`/sources/`.** The share at the top reads **320 of 393 claims resting on a primary
  document**, across 146 documents from 63 publishers, against 320 of 392 yesterday. **The share
  moved DOWN by one claim's worth**, and the honest reason is that at the time it was read this
  run had corrected claims without adding primary ones. Every one of the ten items admitted
  after that reading cites a primary source, so the next reading moves it up. The top publisher
  is `interchange.puc.texas.gov` with 40 claims across 11 documents, which is the commission's
  own filing index and primary by any reading. `lrl.texas.gov` still appears with 12 claims,
  which is the citation half of the boundary question and is historical rather than new.
- **`/topic/`, counting one card against its own page.** The eight beat cards sum to 81, which is
  what the hub's own `All` figure and the front page counter printed at the time of reading. The
  `power-and-the-grid` card says 8 decisions and 1 still open to comment, and the beat's own page
  lists 8 of 81 with exactly one open window, `tx-2026-0002`. Its card prints "8 days left to
  comment, closes September 4th", which is a claim about TODAY and is correct.
- **`/place/`, for the place this run landed something in.** The hub says the record names 59 of
  the state's 254 counties across 27 statistical areas. Travis County took four items this run
  and Austin-Round Rock-San Marcos was already carrying 12 before them, so the place existed
  rather than being created. **The post-admission rebuild happens in Phase 16**, so the counts on
  the live hub at the time of this reading are yesterday's, which is the expected order and not
  a fault.

## THE DECK, and four rounds of a panel that refused it three times

The panel is three judges reading the same deck through different lenses, and `panel.py` takes
the MEDIAN and the UNION of the hard fails, so any one judge's hard fail stops the deck whatever
the other two said. It stopped this deck twice more after the first refusal.

| round | integrity | craft | reader | median | hard fails | verdict |
|---|---|---|---|---|---|---|
| one | 5.288 | 5.48 | 6.15 | 5.48 | several, all three judges | HOLD |
| two | 6.17 | 7.08 | 7.008 | 6.978 | 3, all integrity | HOLD |
| three | 6.22 | 6.84 | 7.038 | 6.84 | 1, integrity | HOLD |
| four | 6.02 | 6.91 | 6.906 | 6.906 | 2, integrity | HOLD |
| five | 5.67 | 6.746 | 7.022 | 6.494 | 2, integrity | HOLD |
| six, verification | 5.95 | 6.96 | 7.00 | see score.json | 2, integrity, both bookkeeping | repaired |
| six, confirmation | 6.71 | 6.96 | 7.00 | **6.86** | none on any lens | **SHIP** |

**The deck ships at a panel median of 6.86 against a 6.8 threshold, with a spread of 0.29.**
The integrity lens was the low card at 6.71, under the bar by 0.09, and asked that its note
be carried verbatim: *"ship is true because this lens found no reason the deck must not
ship, not because 6.71 clears anything. A deck that ships at 7.0 is acceptable rather than
good, and this card did not reach acceptable."* That is the fair description of this deck.

One process note, because it is the kind of thing that must be said out loud. That card first
came back `ship: false` while its own prose said the refusal was the THRESHOLD rather than a
defect, and `panel.py` counts a bare `ship: false` as a refusal either way, which is the
right rule. The boolean was **not edited**. The judge was asked what it meant and answered
that it had misused the field, that `ship` is the panel's refusal switch rather than a place
to restate arithmetic the panel already does on the median, and that its score should stand
at 6.71. Overriding a red gate on a run's own judgement is the failure this repo keeps
writing down. Asking the author of the evidence what the evidence meant is not that.

Round six was a VERIFICATION of round five's two hard-fail repairs rather than another design
pass, on the owner's instruction that past five rounds a run fixes only hard fails. Craft and
reader both returned ship. Integrity returned two more, and both were BOOKKEEPING rather than
copy: `final/contact_sheet.png` had not been regenerated after the repairs, so the packaged
artifact a reviewer and the email look at still printed both refuted sentences, and
`quantifiers.json` still declared the refuted relation as the membership test while carrying no
entry at all for the two universals that actually shipped. Both were repaired, and the same lens
confirmed both closed against the contact sheet, all nine thumbs, `copy.json` and the DOM in
`render_report.json`. Its final card names no hard fail and comes in at 6.71 on the threshold.

### What round five refused, and one repair that made the deck worse before it made it better

**The deck asserted a RELATION its own membership test never computes.** Frame 4 read "All
thirteen name a tax break or a land rule OVER a data center" and the caption said each one
"CARRIES" one. The test finds an ask word and a subject word ANYWHERE in an item's record and
never tests that one is about the other. `tx-2026-0052` is the proof: a county resolution that
its own summary says is explicitly not a rule and that sought no tax break, admitted to the set
because its last sentence mentions a reinvestment zone the same court refused **on a different
item**. The count is right. The relation was invented.

**The set was NOT changed and that is a decision, not an oversight.** Round five's own evidence
shows the test is crude in both directions: any stricter rule requiring the ask word and the
subject word to share a sentence would also drop `tx-2026-0046`, a real tax abatement for a data
centre campus, because its title says HyperGrid and its data centre reference is two sentences
later. Redesigning a membership test is a design change and this run was past the point where it
should be making them. What changed is that the deck now says only what the test computes, and
`compute.py` emits `ask_evidence` per member so the crudeness is auditable rather than arguable.

**Frame 8's row had now been wrong twice, in opposite directions.** It read "CAPITAL FIGURE / NOT
STATED IN EITHER RELEASE", which round four called too broad because c8 has the state calling
this a multi-billion-dollar development. The repair wrote "NEITHER RELEASE STATES A NUMBER", and
round five refuted THAT on c9, a claim the same frame declares, whose quote states $100 billion.
`quantifiers.json` had already recorded that exact phrasing being struck from FRAME 3 in round
three, on the same claims, and round four wrote the struck sentence onto frame 8. The fault was
never the adjective. It was the SCOPE, and the row now names the plant.

### The guards, and the sharpest finding of the whole run

The set's gloss was refuted four separate times, each time in a new coat: an actor, then a
direction, then an idiom, then a relation. Each repair added a word list. Round six then found
that the round-five repair had been **phrased into its own guard's blind spot**: `_surfaces_hold`
matched "each names" and "each carries", and the sentence the repair produced is "Each RECORD
names", on the frame and again in the caption. A guard written specifically to read the published
surfaces had gone blind to the exact sentence the repair wrote, by accident, which is worse than
by design.

Both guards now carry `DIRECTION`, `IDIOM` and `RELATION`, the `ABOUT` pattern was widened, and a
second guard `_declarations_hold` runs the check the other way round and fails the build when
`quantifiers.json` declares a phrase its own surface does not print. **All of them were proven
red against the exact defects that shipped and green on the state that ships.**

And the final card says the whole approach is wrong, which is right: *"Stop guarding this deck's
one computed set with enumerated word lists and make frame 4 print the figure compute.py already
computes instead of a universal, because 'over' escaped, then 'Each record names' escaped the
ABOUT regex, now 'beside' escapes RELATION and 'both' escapes UNIVERSAL, and
`ask_members_with_both_words_in_one_sentence` is 10 of 13 and needs no guard at all."*

### What round four refused, and one of the two refusals was wrong

Two hard fails, both from the integrity lens. **One was accepted and one was refuted, and the
difference is worth the paragraph.**

**Accepted.** Frame 9 stencilled `ON DATA CENTER WATER USE` as the subject of a specific
hearing. No source this run fetched states the AGENDA of either sitting: c20's note carries a
date, a time, a room and the words Public Hearing, and the line's actual source, c21, is the
committee's standing INTERIM CHARGE, which `tx-2026-0096-c2` shows also covers desalination and
permitting. **A charge is what a committee was told to examine over an interim. An agenda is what
a particular sitting will take up.** Reading the first as the second put an unfetched fact on the
one frame whose whole job is sending a reader to a room, and it got there because round three's
reader lens asked what each room was ABOUT and the honest answer was that nothing this run
reached says. The line now names the charge as a charge. The frame's dossier gained an acceptance
item forbidding any line that states an agenda.

**Refuted, and checked before it was refused.** Round four called `tx-2026-0104-c8` a fabrication
on the reasoning that one JSON document cannot carry both `"fundsObligatedAmt":"5999999"` and
`FY 2026 = $5,999,999.00`, and honestly flagged that it could not fetch the URL to confirm. It
can and it does, in adjacent fields. The response reads
`,"fundsObligated":["FY 2026 = $5,999,999.00"],"fundsObligatedAmt":"5999999",` and the raw bytes
were read again this run before the finding was set aside. **A hard fail resting on a premise the
evidence refutes is a lead, not a verdict**, which is `panel.py`'s own rule for a lone objection,
and it is the only finding across five rounds this run has not simply taken.

What WAS wrong is the half the judge could see. c8's `text` announced its own purpose, that the
quote carried the separators the summary needed. **A claim that explains why the run wanted it
reads as a claim written to license a format, whatever its bytes.** It now says what the source
says, and the item's `notes_for_editor` carries the response so the next reader gets the evidence
rather than the argument.

### The recurring shape, now measured four rounds running

Round three named it: each repair **"was applied to one surface and not its twin"**. Round four
found it inside the guard pair written to stop it. `IDIOM` had been added to `_surfaces_hold` and
not to `_gloss_holds`, so the phrase that shipped in round three would still have passed the
older guard, and `_surfaces_hold`'s own `ABOUT` regex read only "thirteen" and "twelve count", so
two further assertions about the counted set sat on the caption invisible to it. Both are fixed.
The pattern is the single most useful thing this run produced and it belongs in
`GATE_LESSONS.md`.

### Repairs that made things worse, and were reverted

**Deriving frame 9's accent from its declared token was correct and its consequence was not.**
The declared `#D7677E` is darker than the `#E2788E` the frame had been painting, the two dates
fell to 4.0 and 4.2 against the rubric's 4.5 floor, and the panel under them was darkened to
rescue the measurement. Round four measured what that cost: on the one frame where the record
actually holds the rooms, the blocks carrying them became the darkest objects on a lit floor,
which inverts this deck's own law 1, and painted floor tape darker than the concrete it is
painted on is backwards besides. **The panel is back and the DECLARATION moved instead.** That is
not moving a floor to fit an encode. The 4.5 contrast floor is the promise and it has not moved.
The token was an internal declaration that disagreed with the code, and the code's value is the
one chosen for legibility.

### Two frames ship with their own acceptance items recorded as MISSED

`ledger/carousel/artwork.json` states both rather than describing either as met.

- **Frame 9's stencil is not projected.** One vertical scale on the block and a per-line font
  size from its own depth, so the glyphs stay square to the camera, which the frame's own
  acceptance item fails.
- **Frame 5's cut reads as an emboss.** Two `feOffset` copies of the glyph alpha under a gradient
  fill. Two rounds read it as raised type rather than an aperture, the lit rim falls in the
  opposite quadrant to this deck's own lamp, and law 3 forbids anything embossed.

The craft lens was asked directly whether that is a stop and said it is not: no enumerated hard
fail covers a frame that misses its own acceptance item and says so, the frames are finished, and
the 2026-08-21 entry on deck no. 5 is the precedent. **Recording it is the whole point.** The run
corrected frame 9's ledger line after a judge caught it and would otherwise have left frame 5's
twin standing three frames earlier, which is the same shape one more time.

### What round two refused, and what it cost to find out

Three hard fails, all from the integrity lens, all accepted rather than argued.

1. **Frame 4 narrated a computed set in words its own membership test never tested.** The frame
   said somebody ASKED a Texas city or county for a tax break on every one of thirteen items.
   `compute.py` admits an item when its reader copy NAMES a tax break or a land rule and the
   decider is a city or county, whichever direction the request ran, and about half the set runs
   the other way: El Paso eliminating its own incentives, Corpus Christi directing staff to
   prohibit them, Fort Worth opening its own moratorium, and a Webb County item whose record says
   nobody had applied at all. The count was right, which is exactly what made the gloss
   convincing.
2. **The cover asserted "No incentives." as fact in the largest type in the deck**, sourced only
   to a quote by the company inside the company's own release, which the deck itself correctly
   presented as a QUOTE two frames later.
3. **Frame 5 stamped a person's name beside a claim that does not carry it.** `c6` carries the
   mayor's words and not the mayor's name, and the only place the name appeared in the run was
   inside the REJECTED block.

### What round three refused, and it is the more useful lesson

One hard fail, and it was the same claim as no. 1 above, still standing on a surface the repair
had not reached. Frame 4's dek was fixed, `compute.py` grew a `_gloss_holds` guard, and
`caption.txt` paragraph 3 went on opening **"Thirteen items on this record run the other way"**,
where a reader actually meets it. The guard read a string literal inside `compute.py`. It could
not see the caption and never would have.

The judge's own words for the shape, and they are worth keeping: each repair **"was applied to
one surface and not its twin"**. It happened three times in one round. `compute.py` fixed and
the caption not. The storyboard's numeral inventory fixed and `quantifiers.json` not. Frame 6's
universal scoped and the caption's closing question not.

**The ratchet:** `_surfaces_hold` now reads `caption.txt` and `copy.json`, restricted to
sentences that mention the counted set, and fails the build on a direction verb or a direction
idiom. It was proven RED against the exact sentence that shipped and green against the repair.
What it cannot do is written into the file beside it: it matches words, so it catches "asked"
and it catches "the other way" because that one is now written down, and it will not catch the
next phrasing that implies a direction without naming one. That is what the panel is for.

### Craft repairs, and one that was invisible in the source

- **Frame 5's cut had never rendered, in any round.** The filter was declared `id="cut"` and so
  was the SVG element carrying it, so `url(#cut)` had been resolving to the ELEMENT. Two judges
  read the frame as a flat knockout and were exactly right, while the source read like a filter
  chain. Found by measuring the plate-to-glyph transition on the render, which was one sample
  step wide with no rim on either side. **No amount of reading the code would have found it.**
- **Frame 4's thirteen crates were one value** because the face mix ran through a clamp that
  bound on two thirds of the stack, and every body on the crate except the plywood ignored the
  lamp entirely. Measured falloff up the stack is now 58, 94, 132, 110, 66.
- **Frame 8's four pockets were a typed 214 pixels** while its own acceptance said the widths are
  measured from the laid out strings. Each is now as wide as its own field name.
- **Frame 9's longitudinal joints were dotted hairlines** because the loop stepped a parameter
  rather than image rows. Both painted panels were clamping to full bleed rectangles, which is
  why two judges read the type as square to the camera when the type was in fact foreshortened
  and the SHAPE around it was not.
- **Frame 1's steel took 45 percent of its value from distance dimming rather than from the
  lamp**, so the columns beat the frame's own declared focal.

### Probes that could not fail, replaced with probes that can

Three `data-encodes` probes were measuring things the defect left alone, which is the recurring
shape in `GATE_LESSONS.md` one layer down. Frame 5's read glyph-white against plate-grey and
reported dE 68.1, which a flat knockout passes as easily as a cut plate. Frame 4's read a lit
crate face against a dark stack gap, which thirteen identical crates pass. Frame 6's sampled a
region entirely occluded by the hook, so the perforation claim was measured against nothing and
passed. Each now measures the property its acceptance item actually names.

## GAPS THIS RUN COULD NOT FILL, and did not guess at

Round three's reader lens asked for the DOOR rather than the room, and named two specifics. The
run tried both and could take neither.

- **The building E1.012 sits in.** `capitol.texas.gov/Committees/MeetingsUpcoming.aspx` was
  re-fetched. Its location line reads `E1.012 (Hearing Room)` and names no building. The E prefix
  is a Capitol Extension convention a Texan may know and this project does not get to assert from
  convention, so the frame says what the listing says.
- **How a written comment on Project 58482 is filed.** Three hosts that could state it refused
  this run: both PUCT hosts earlier, and now `www.sos.state.tx.us`, which returned 403 to two
  fetch paths in the same run that had already proved the DEADLINE against the Texas Register.
  The deadline is on the frame. The method is not, because nothing this run could reach states
  it.

Both are in `knowledge/shared/SOURCES_FIELD_LOG.md`. A deck that hands a reader a date and no
door is worse than one that hands them both, and a deck that invents the door is worse than
either.

## A JUDGED CALL THE PANEL RAISED AND THE RUN DID NOT TAKE

Round three's integrity lens found `tx-2026-0106` in this run's own record: Austin City Council
item 61, data center land use, an open meeting in Travis County dated the day this deck ships,
while frame 6 prints "No local body. No room." and frame 9 counts two rooms without it.

The run left the deck alone, on two grounds stated here so a later reader can disagree with them.
The item is a **different subject**, city-wide data center land use rather than the Amazon plant
the deck is about, and frame 6's dek scopes its claim to the two releases in words a reader sees.
And it is dated the ship day, so by the time the post is read the room has closed, while frame 9
exists to hand a reader rooms they can still walk into. **The counter-argument is real**: the
deck stamps TRAVIS COUNTY on seven frames and prints "No room" on a day its own record holds an
open Travis County data center room, and a reader who checks will find it.

## Defects found in the record while shipping, and repaired

- **`tx-2026-0104`'s summary printed `29,999,998` and `5,999,999`**, thousands separators and all,
  and NO claim carried either figure in that form. The NSF API serves bare digit strings. Every
  other comma-formatted figure in the record's summaries appears verbatim in a claim quote, which
  is the house pattern and this was the only exception. The obligated figure is now stated as the
  agency states it, `$5,999,999.00`, proved by a new claim quoting `FY 2026 = $5,999,999.00`
  verbatim from the same award service. The estimated total is named rather than formatted,
  because nothing this run could fetch states it with separators.
- **`tx-2026-0102` carried a field called `held_reason` that this run invented.** No script reads
  it, it is in no schema contract, and it sat on an item whose status is `decided` rather than
  held. `schema_contract.py --update` would have blessed it into a public contract and
  `ownership_check` refused that write, correctly: **a routine adds ITEMS and never FIELDS.** The
  sentence moved to `notes_for_editor`, which already existed for exactly this, and
  `config/schema_contract.json` was left untouched.
- **Nine written sentences across seven items ran over the 30 word backstop** and were split at a
  clause.

## THE OWNER'S INSTRUCTION, 2026-08-27, and it is the most important thing this run produced

Given mid-run, after the fifth scoring round, verbatim in substance:

> After 5 rounds of editing, transition to only fixing the hard fails. We need to spend a session
> improving the agents who are creating the carousel so they can do a better job impressing the
> judges, maybe using web search to equip them with better info and more skills. We don't want
> them to rely on the judges for design. The judges should just be for tweaks, because the initial
> agents are making it so great, instead of using the editing gloop as a crutch. In 5 rounds they
> should be able to get passing scores, and if not they need to get better.

**This run is the evidence for that instruction, not a counterexample to it.** Six scoring rounds,
eighteen judge reports, and the deck still left the last full round at a median of 6.494 against a
6.8 threshold. The rubric already says this in its own words, added the same day the cap went from
ten to five: *"A panel is a CHECK on a deck the run already believes is finished. This run used it
as a design loop, shipping a half-considered frame into three judges and letting them find what a
careful pass would have found for nothing."* That is exactly what happened again here.

Two specific pieces of evidence a later session should start from.

**The panel found things no amount of self-review would have.** Frame 5's filter had never executed
in any round because its `id="cut"` collided with the SVG element carrying it, and the source read
like a working filter chain the whole time. Frame 4's declared focal measured AUC 0.62, near
chance, and the machine had already reported it. Neither was a taste call.

**And the panel also did work the builders should have done.** Three separate `data-encodes` probes
were measuring properties the defect left alone. Two frames shipped without their own declared
technique. The membership test's gloss was refuted three separate times, each time in a new coat.
None of that needed a judge.

### What the improvement session should carry, in the order it matters

1. **The builders must read their own acceptance list before they render, and measure against it.**
   Every craft hard finding in this run was a frame failing an item its own dossier had already
   written down. `plan_render_check` proves the STRINGS match. Nothing proves the DRAWING does.
2. **A probe must be authored off the render, never from the plan's arithmetic.** Frame 6's probe
   was wrong twice from sheet-space geometry and right the first time it was measured off pixels.
   `qa.py` already says this in its own failure text and the run had to be told twice.
3. **A computed set may only be narrated by its own membership test, and the guard must read the
   PUBLISHED surfaces.** This defect mutated through four rounds by changing which word did the
   overstating: an actor, then a direction, then an idiom, then a relation. The guards now carry
   `DIRECTION`, `IDIOM` and `RELATION` and read `caption.txt` and `copy.json`. That is a patch on a
   symptom. The cause is that a builder wrote a sentence about a set without reading the code.
4. **Equip the treatment and copy agents with real craft references.** The owner's suggestion of
   web search is the right instinct: the recurring craft failures here are ordinary rendering
   knowledge, an aperture lit against its own scene's key, a floor projection with no keystone on
   the glyphs, a cast shadow with no penumbra.
5. **The membership test itself is crude in both directions and needs designing, not patching.**
   Round five's own evidence: `tx-2026-0052` is admitted because a sentence in its summary mentions
   a reinvestment zone that a different item is about, and `tx-2026-0028` because a sentence
   compares it to other counties' incentive votes. Meanwhile any stricter rule requiring the ask
   word and the subject word to share a sentence would drop `tx-2026-0046`, a real tax abatement
   for a data centre campus, because its title says HyperGrid and its data centre reference is two
   sentences later. `compute.py` now emits `ask_evidence` per member so this is auditable rather
   than arguable: 10 of 13 members carry both words in one sentence and the three that do not are
   named.

## Proposals for the upgrade lane, which this actor may not make

1. **`_surfaces_hold` belongs in `scripts/carousel/`, not in a run's own `compute.py`.** It is a
   general rule (a computed set may only be narrated by its own membership test, on every surface
   a reader meets) and it currently lives in one run's scratch and dies with it.
2. **Make every acceptance item measurable off the 432px thumb.** Round three's craft lens named
   this as its single fix and it is right: `machine_qa` already computes the focal AUC and
   reported frame 4 at 0.62, near chance, while the run recorded three panel repairs without
   checking one of them against a thumb.
3. **Frame 5's aperture wants `feDiffuseLighting` over a blurred alpha** and frame 9's stencil
   wants a real perspective matrix on the glyphs. Both were named by the craft lens; neither was
   attempted here, and frame 9's acceptance item is recorded as MISSED in
   `ledger/carousel/artwork.json` rather than described there as met.
4. **A duplicate-id check for slide sources.** One `id` collision cost this deck two rounds.
5. **`bootstrap.sh` fails on PyYAML** with "Cannot uninstall PyYAML 6.0.1, RECORD file not found",
   and every run works around it with `--break-system-packages --no-deps --ignore-installed`.
6. **The `GEOGRAPHY_BACKLOG` ratchet can never shrink from `daily`**, and nothing checks a seed
   claim's URL against the crawl boundary before it reaches the record.
