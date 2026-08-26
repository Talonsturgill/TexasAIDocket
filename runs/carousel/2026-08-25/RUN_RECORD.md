# Run record, August 25th, 2026

Carousel No. 7. Nine frames. The deck half of the daily routine, run on the owner's instruction
to take it all the way through to a Gmail draft.

## The story

Eight Texas governmental bodies restricted a data center between March 10th and August 11th, and
no two of them reached for the same instrument. A permit refused in Killeen, an incentive denied
in Archer County, disclosure asked for in Lubbock County, staff directed to draft in Corpus
Christi, a reinvestment zone refused in Brazoria County, a category denied by the Texas Water
Development Board, a process started in Fort Worth, and water capped by ordinance in San Angelo.
Eight bodies, eight shapes. Two more considered a restriction and declined it.

The deck's argument is that the SHAPE of a refusal decides whether anything stops, and most of
these shapes stop nothing. Archer County's unanimous denial "does not stop the project from moving
forward". A Lubbock County commissioner said "Resolutions do nothing, they are not binding." San
Angelo's ordinance is the exception, and it passed 7 to 0.

`tx-2026-0072` was rejected at selection as a LIKELY REPEAT at 0.70 against carousel No. 3 on
August 19th, same docket item, six days inside the thirty day window. The story that shipped is
the PATTERN across ten bodies rather than any one of them.

## Every numeral on every frame was computed

`out/2026-08-25/compute.py` derives all nine figures from `ledger/docket.json` and writes
`figures.json`. Not one was typed. The rule that mattered most is `ordered_on`, which takes the
date the BODY ACTED, from the `ordered` key date and nothing else. Its first version took the
earliest key date of any kind and returned a FILED date for one item, which would have put a
wrong span on frame 3 in the largest mono on the frame.

`aggregate_check` re-derives all nine independently and exits 0. Word form numerals count: the
gate caught `eight`, `Four` and `Two` on three frames as computed counts, which is correct and is
why they are declared.

## Two gates were fixed this run, both in the upgrade lane, both wrong about a correct deck

**`claims_check` refused a claims file whose every claim had been re-fetched at 200 that morning.**
Its quote rule was a word count, which is right for prose and wrong for a structured span. Half
this project's primary sources are JSON APIs, where the string that proves a fact is a field pair
like `"EventDate":"2026-06-16T00:00:00"`. One whitespace token, 33 characters, and about as
locatable as a string gets. The rule now passes on four words OR twenty eight characters, so
`"no action taken"` is still refused at three words and fifteen characters, which is correct.
That phrase appears twice in its own response and everywhere else in Legistar. Commit `4706c342`.

**`texan_check` reported that the deck gave a reader nothing dated to act on.** The closing frame
carries NOVEMBER 10TH at 58px, the largest numeral in the deck and the one thing in the record
that has not happened yet. Two faults in one regex pair. `ACTION` was case insensitive and `DATE`
was not, so one half of the same test could read a caption and the other half could never read a
slide, and display type is set in caps as a matter of course. Then `ACTION` could not match a
plural, so "the first of two required public hearings" was invisible to it. That frame passed the
action half only because the word DEADLINE happened to sit elsewhere on it, which means the gate
was right by accident about a frame it had misread. Commit `cdd1b389`.

Both carry self-tests in both directions.

## The claims file was repaired, and the repair is not cosmetic

Fifteen claims carried `source_type: journalism`, a synonym `claims_check` documents by name and
refuses because it drifted in on August 18th. Every one is a news report of an official act, so
every one is `secondary_reported`. The three rejections were keyed `{claim, why}` against a
contract of `{finding, reason}`, so a gate reading three fully reasoned rejections reported three
blank ones. `c14`'s quote was the bare phrase `no action taken`; it is now the field pair, re-fetched
at 200 from Laredo's Legistar this run, which is the span a reader can actually find.

## What the pixel review changed, and what it measured

Three critics ran in parallel over the nine frames. Four frames were rebuilt.

**Frame 7's bounce falloff was 3.4 L\* across the four repeats.** The frame's entire technique is
repetition down a falloff, and a 3.4 L\* spread is a falloff no reader sees. Measured after the
rebuild it is 12.2 L\*, monotonic, 86.4 to 98.6.

**Frame 4's camera was never rendered and its argument was inverted.** The dossier declared a
steep oblique with the glazing near edge on, and the frame was square on with a wider left stile.
It is now drawn in true perspective, one set of constants shared by the canvas projection and a
CSS transform on the type, so the case and the words on it are one object rather than a picture
with type over it.

The veil was worse than the camera. Sky reflected off glazing at grazing incidence ADDS light, so
it lifts the ink and the paper together and the contrast between them collapses. The frame drew
that veil on the canvas, UNDER the type, where it could only make paper brighter, and then faked
the effect by setting the veiled paragraph in a lighter grey. Brighter paper with darker ink is
more readable, not less, which is the opposite of what the frame exists to say. The veil is now an
overlay above the type that screens. Measured, the veiled block reads 4.43 to 1 against paper at
L\*95.9, and the clear block reads 12.96 to 1 against paper at L\*94.2. Brighter and three times
harder to read, which is the argument stated optically.

**Frame 5's blowout ran at 7.3 degrees where its dossier said about 28.** The reason was
geometric rather than careless. With both quotes stacked at one left margin the corridor between
them is 396px tall, and a 190px band at 28 degrees needs 640px of it. Moving the quotes to
opposite corners opens 306px of clearance and the band now runs at 28 degrees with 44px to the
nearest quoted line on both sides. Its kicker read THE TURN, which is the storyboard's word for
what the frame does to the DECK. A reader does not know there is a turn. It names the two counties
speaking, as frames 4 and 7 do.

**Frame 9 spent flag red on the words NOT LATER THAN as well as the date**, against its own
acceptance list, which reserves the deck's one red for the date. It drew three sprung clips under
a comment reading TWO SPRUNG CLIPS. Its decorative rules ran through the date annotation and the
source line and the last two fell off the sheet onto the cork.

**Frame 7 read as a console log rather than a minute**, which is risk one in its own dossier.
Three of its four title cells were mono sentences saying the applicant was not named. They are
ruled and empty now, which is what the dossier asked for and what a clerk would actually leave,
and one line above the table says it once.

## What is measurably not what the storyboard said

**This is not the mid value deck it declares.** The storyboard says "ground at L\* 62 to 68".
Measured medians, frame by frame, are 54.4, 55.0, 14.4, 30.8, 81.4, 64.1, 69.4, 81.6 and 49.5,
with a median of medians of 55.0 and a range of 67 L\*. Three frames sit inside the declared band
and six do not.

The band was typed by the directors room rather than measured, which is the compute-not-generate
law being broken in a planning document. The frames were not re-graded to reach it, because the
extremes are load bearing and stated in the dossiers themselves. Frame 7's dossier asks for "the
deck's darkest field, immediately after its brightest", and flattening it to hit a number would be
editing the artifact to match a record instead of the reverse.

What goes into `ledger/carousel/artwork.json` is the MEASUREMENT, because that ledger is what
future decks are checked for divergence against, and a register recorded as mid when it is a 67
point range poisons every dedupe after it.

**`plan_render_check` reports 0 of 46 acceptance items checkable.** The routine's own prompt
warns about exactly this number on exactly this gate, and names the deck that scored 8.03 as
having the same 0 of 46. This deck's acceptance lists are descriptions. The items that COULD have
been tests, the falloff spread, the veil's contrast ratio, the band's angle and the air gap's L\*
separation, were all measured during pixel review, by hand, after the frames existed. Writing them
into the dossiers now would be writing the test to fit the artifact. It is a proposal for the
planning phase of the next run rather than a repair to this one.

## Confirmations

Frame 3 sits under the craft floor at variance 520 against a floor of 1030. It is deliberate. It
is the roster, a flat dark list of eight bodies between two heavily modelled frames, and its
detail is spread across the frame rather than absent. `craft_floor` asks for the confirmation
rather than failing, and this is it.

## Gate status

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 30 verified claim(s) |
| render         | WARN   | 9 slide(s), 24 overflow warning(s) |
| qa             | WARN   | 0 fail(s), 48 warn(s) |
| aggregates     | PASS   | 9 declared and re-derived |
| assembly       | PASS   | 9 slide(s), 1.89 MB, vector |
| score          | ABSENT | score.json not written yet |
| dossiers       | PASS   | 29,336 chars planned |
| caption        | PASS   | 141 words |
| craft floor    | WARN   | 9 frame(s), median 5723, floor 1030, 1 quiet |
| plan vs render | WARN   | 0 of 46 acceptance item(s) checkable |
| texan          | PASS   | places Hill County, Tom Green County / body yes / deadline yes / next step yes |
| absences       | PASS   | 10 of 10 scoped to a named document |
| completion     | ABSENT | not scored yet |
<!-- gate-status:end -->
