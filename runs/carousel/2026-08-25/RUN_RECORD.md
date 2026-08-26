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

## THE FINDING A HUMAN HAS TO SEE

**Six of nine frames declared a texture in a comment and never drew a pixel of it, for the whole
run, and nothing in the suite noticed.**

`TX.rng` in `assets/js/noise.js` is a PRNG FACTORY. `TX.rng(42)` returns a generator function.
Every texture loop in this deck called it as `TX.rng()`, which returns the function object, so
`TX.rng()*W` is `NaN` and `fillRect(NaN, NaN, ...)` is a silent no operation. The paper tooth on
frame 7, the cork tooth and the staple hole field on frames 6 and 9, and the wall grain on 1, 4,
5 and 8 all drew nothing at all.

What that survived is the point:

- `render.py` exits 0, because a NaN rect throws nothing.
- `qa.py` exits 0, because a missing texture is not a fail.
- `craft_floor` passed all nine frames, because the frames still carry a real light and a real
  dark from their geometry.
- THREE pixel critics read the frames and did not name it.
- The flow critic read all nine and named frame 6 as reading like an unfinished render, which is
  the symptom, and diagnosed it as an alpha problem, which it was not.

It was found by cropping a patch of cork at 1 to 1 and measuring it. Standard deviation 3.42
luminance levels over a 19 level range, which is a flat fill. The first two repairs raised the
alpha and the chip size and moved the number to 3.42 both times, and an unchanged measurement
after a substantial change is the fact that pointed at the generator rather than at the paint.

Fixed by seeding one generator per frame off that frame's own reseed value. Measured after, the
cork carries a standard deviation of 9.04 and the letterboard felt 23.26. The first fix
overshot to 31.98, which is a camouflage pattern, and the number is what said so.

**The lesson for the machine.** A canvas API that fails silently on NaN means an effect can be
fully written, reviewed by three critics and shipped, having never existed. The only check that
finds it is measuring the pixels the effect was supposed to change. `knowledge/` is `human` owned and this run
stamps `daily`, so it goes in the proposals below rather than into `GATE_LESSONS.md`, which is
the rule working: a run that can edit the record of what fooled it has no such record.

## What the flow critic changed

It returned `revise` and it was right on nine of its ten findings. It was wrong on one, that
frame 1's specular crosses the dek's last line, and the crop shows 78px of clearance. Measured
before acting, not after.

- **Frames 2 and 3 were doing one job.** Frame 2 already prints all eight body names under the
  eight instruments and frame 3 reprinted the same eight alone for one new line of payload.
  Frame 3 is the CHRONOLOGY now, eight dated marks in the order the bodies acted, on the same
  changeable letter board. Its dek carries a figure no other frame holds, four of the eight
  falling inside the final twenty one days.
- **Frame 5's hook was a quantifier where the law requires a count.** "Most of these do not
  bind" asserted a proportion nothing computed. It reads `Two of the eight stop nothing` now,
  from `stated_nonbinding`, and its foot carries `force_unstated`, the four bodies the record
  says nothing about either way. The deck is stronger for it, because it now publishes the size
  of what it does not know rather than rounding it into "most".
- **Frame 7's dek repeated frame 6's card verbatim.** Both dossiers had declared the same
  sentence. Frame 7 carries the fuller act from the same claim.
- **Frame 8's reflection was an inset panel with three readable strings on it**, against its own
  acceptance list, which says a reflected document is not evidence. It is sheared, rippled and
  Fresnel weighted now and carries nothing legible. Laredo's evidence moved onto the sheet at
  full toner. Its thesis line was pale grey type sitting INSIDE the cream sheet and running
  across the decorative rules, which is the frame's own point set in the least readable way on
  the frame.
- **Frame 8 had no denominator.** Two bodies declined arrived with no set to be two of. Its foot
  states the ten now.
- **Frame 6's cork was flat and its caption's descenders were clipped by the case lip.**
- **Frame 1's numeric lockup misread at 432px** as "8 BODIES INSTRUMENTS", and the dek's fourth
  line overlapped the numeral by 15px. It counts both nouns now.
- **The 6 to 7 value snap ran backwards.** Both dossiers claim frame 6 is the brightest field and
  frame 7 the darkest immediately after. Measured, 6 was 64.1 and 7 was 69.4. Frame 7's field
  was dropped to 61.4 and its falloff widened rather than flattened, so the four repeats now
  span 17.2 L\* instead of 3.4.

## Three more gates were wrong about a correct deck

All three were found by writing copy the gates had never been shown, and all three are in the
`upgrade` lane with self-tests both directions.

`aggregate_check` could not see a ratio written with the article, so "three of the nine" would
have asserted a proportion no computation had to back. Worse, matching a ratio BROKE OUT of the
shape loop, so every later shape anywhere in the same string was suppressed: "Four of the eight
came in the last 21 days" reported the ratio and silently exempted the 21, on the gate whose
entire purpose is that an undeclared number cannot reach a frame. Commit `4d2c58d0`.

That makes five gate repairs in one run. Every one of them was a gate reporting a correct deck
as wrong, or a wrong deck as correct, and none of them was found by a self-test. Self-tests prove
a checker can go red. Only the product proves it is looking at the right thing.

## The panel, round one, and why three judges are not one judge run three times

integrity 6.42 with FIVE hard fails. reader 5.85 with one. craft 7.36 with none, and craft said
ship. Any one judge's hard fail stops the deck, so it did not.

**Every hard fail was a WORD, and not one was a number.** That is the finding, and it is bigger
than this deck. The compute-not-generate law covers numerals and this run enforced it well: all
thirteen declared figures re-derive, every numeral on every frame traces to a claim or a
computation, and the panel confirmed it. Nothing was reading the NOUNS and QUANTIFIERS wrapped
around those numerals, and that is where all six failures were.

1. **`caption.txt` still said "Most bind nothing."** The exact quantifier the flow critic struck
   from frame 5 four hours earlier, recorded as fixed in the storyboard and in this record, and
   shipped in the caption anyway. The frame was reread and the caption was not. It carries
   `stated_nonbinding` now, and the four the record is silent on beside it.
2. **`first_comment.txt` said "Sources, all primary and fetched August 25th, 2026"** on a run
   whose own claims file types seven of its twelve documents `secondary_reported`. That is the
   one line whose entire job is telling a reader how good the evidence is, on the surface a
   sceptic checks first, and it overstated exactly that. `sources_block.provenance_line()` COUNTS
   it now, both directions self-tested, and it reads "seven news reports and five official
   records".
3. **Frame 1 called the Texas Water Development Board a local government**, on a deck that names
   that agency on two other frames, and said all eight "refused" when four of them started a
   process, directed staff to draft, asked for disclosure and denied a petition.
4. **Frame 1's hook spoke AS Texas**, which `TEXAS_VERNACULAR` forbids by name, and contradicted
   the deck's own thesis one frame later.
5. **Frame 8 said eight bodies "imposed" a restriction**, contradicted by c22, c30, c8 and c29.
6. **Frame 9 said everything else in the record is already decided**, contradicted by c18, c30,
   c13 and by c23, which this deck quotes on frame 4.

Two more, neither a hard fail and both worse in kind than a hard fail, because both were FALSE
PROVENANCE inside the computation itself:

- `brazoria_apps = 4` was a typed literal and `aggregates.json` described it as "counted over the
  RESTRICTED and DECLINED maps". It carries `value_from: c11` now, and compute.py says in its own
  comment that it is not computed and must never say it is.
- `LATE_WINDOW = 21` was CHOSEN and it is the smallest window that yields four. At twenty the
  answer is three. A tuned parameter presented as a finding. The split is half the set now, which
  nobody tuned, and the span those four occupy is measured after the fact.

The rubric's own history says a single scorer graded one deck seven times and found zero hard
fails where a panel of three found four. This run is that lesson again with a different number:
one judge of three said ship.

## The panel, round two, and the number that was wrong

integrity 6.46 with FOUR hard fails, reader 6.44 with none, craft 7.23 with none. Round one's six
were all repaired and all four judges' checks confirmed the repairs landed in the RENDER and not
only in the source. These four were different, and one of them was the deck's headline number.

**THE COUNT WAS EIGHT AND THE RECORD SUPPORTS SEVEN.** The Texas Water Development Board sat in
`compute.py`'s `RESTRICTED` map. What it actually did, per c29, is DENY A PETITION filed by a
Wimberley resident asking the agency to project data center water demand as its own category.
That is a refusal to add scrutiny, which is the opposite direction, and `compute.py`'s own stated
IN rule excludes it in words on the line above the map.

It was in there because that map was typed by hand from memory of the record rather than read off
it, and once it was in, eight became the cover, the cover's numeral lockup, frame 2's hook and its
eight rows, frame 3's eight dated marks, frame 5, frame 8 and five sentences of the caption. Every
gate was green over it. `aggregate_check` re-derived eight correctly from a map that was wrong.
`claims_check` passed a claims file that says the opposite. A judge reading c29 against the rule
found it in one pass.

**The silent set was empty and the deck published four.** Frame 5 and the caption said the record
says nothing either way about four bodies. It speaks to every one of the seven: c30 says the
Corpus Christi motion bans nothing, c22 and c23 are the entire subject of frame 4, and c18 says
Killeen's commission vote is a recommendation the council still has to act on. So five of the
seven stop nothing in their own records, two bind, and nothing is unaccounted for. The deck is
better for the correction than it was for the error.

**Frame 7 asserted an absence its own record contradicts.** "NO OTHER APPLICANT IS NAMED IN THIS
RECORD" against `tx-2026-0051`, which reads "two from Bulldog Power and two from Old Ocean
Datacenter".

**Laredo's shape cited a claim that does not state it.** `moratorium declined` came from the
docket item's title. c14 says "no action taken" and that is what the map says now.

reader's round two was six point four four with no hard fail, and its findings were config
compliance rather than truth: the caption ran 980 characters against `brand.yaml`'s stated hard
band of 300 to 900, ended on a link against `links_in_body: false`, and closed on a record
pointer against `ends_with: engagement_question`. Three rules stated in config that no gate reads.
Its one sentence fix, replacing the cover's "8 BODIES / 8 INSTRUMENTS" with the two part number
the deck actually proves, was taken: the cover reads **7 ACTED / 2 BOUND**.

craft's round two caught a false count I had typed into `ledger/carousel/artwork.json` in the same
entry whose whole purpose was recording a measurement rather than an assertion:
`frames_inside_declared_band: 1` beside a `per_frame_median_L` array showing zero. It is computed
from the array now.

## Proposals for the machine, none of them in this actor's lane

1. **A gate that proves a declared texture reached a pixel.** `knowledge/` and the engine skill
   are `human` owned, so this is a proposal. Every frame declares its technique in its dossier.
   A check could crop the region the technique claims to act on, measure its standard deviation
   and fail a frame whose declared texture measures flat. Today's defect would have been caught
   on the first render rather than after three pixel critics and a flow critic.
2. **`assets/js/noise.js` should refuse to be called wrong.** `TX.rng` returning a function when
   called with no seed is a footgun that costs a whole deck's texture and reports nothing. It
   could return a default seeded stream, or throw. Either beats `NaN`.
3. **The dossier spec should require at least one MEASURABLE acceptance item per frame.**
   `plan_render_check` reports 0 of 46 checkable for the second deck running, and the items that
   could have been tests here (a falloff spread in L\*, a contrast ratio, a band angle, an air
   gap's separation) were all measured by hand after the frames existed.
4. **The value register belongs in the artwork ledger as a MEASUREMENT.** The storyboard typed
   "ground at L\* 62 to 68" and the deck measures a 67 point range around a median of 54.7. A
   script could compute the per-frame medians at ship time and write the ledger entry from them,
   which is the compute-not-generate law applied to the machine's own memory.

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
| render         | WARN   | 9 slide(s), 26 overflow warning(s) |
| qa             | WARN   | 0 fail(s), 33 warn(s) |
| aggregates     | PASS   | 13 declared and re-derived |
| assembly       | PASS   | 9 slide(s), 3.23 MB, vector |
| score          | ABSENT | score.json not written yet |
| dossiers       | PASS   | 35,183 chars planned |
| caption        | PASS   | 155 words |
| craft floor    | WARN   | 9 frame(s), median 6061, floor 1091, 1 quiet |
| plan vs render | WARN   | 0 of 46 acceptance item(s) checkable |
| texan          | PASS   | places Hill County, Tom Green County / body yes / deadline yes / next step yes |
| absences       | PASS   | 10 of 10 scoped to a named document |
| completion     | ABSENT | not scored yet |
<!-- gate-status:end -->
