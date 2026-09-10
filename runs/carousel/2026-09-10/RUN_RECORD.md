# Run record, 2026-09-10. Carousel no. 20.

The record cleared a 16 item worklist and admitted two items, one of them the deck's own
subject and every one of its twelve claims drawn from a federal document this run fetched and
read. The deck is nine bespoke frames on a certification question rather than a driving one,
and the distinction is the reason this story is not a repeat of carousel no. 5.

## Phase 0, wake

Clean checkout of `origin/main` at `40def58f`, branch `claude/daily-2026-09-10`. Git identity,
email and `core.hooksPath` set before the first write, so both hooks ran on every commit below.
`guards_local.py --fast --only Ownership` passed, three steps green and the CI-only step
skipped as designed. `docket_build.py --validate` and `ownership_check.py --self-test` both
exited 0 at wake, so nothing shipped past a gate on the previous run. No `prompts/NEXT_RUN.md`.

## Phase 1, craft refresh

**Rotating focus: ARTWORK CRAFT, chosen from the panel's own numbers rather than from taste.**
The last three panels scored `artwork_craft` 7.1, 6.8 and 6.5. It carries the heaviest weight in
the rubric at 0.28 and it has fallen three runs running, which no other criterion has done.
`variety` is lower in absolute terms at 6.0, 7.2 and 5.5, and it was already a named focus on a
recent run.

The reading that shaped the plan is `SLIDE_DOSSIER_SPEC.md`'s focal law, because it is the one
place in this repo where a craft lesson is attached to a measured movement: rewriting three
declared focals from LINES to AREAS moved `artwork_craft` from 6.4 to 7.8 in a single run. Every
dossier this run declares an area and names the lightest and darkest thing in its frame.

## Phases 2 and 3, the record

`docket_staleness.py` named **16 items due, nothing rotten, nothing deferred**, and no
`--budget` was passed. Exit 0.

`reverify.py --apply` read 35 urls behind 121 claims. Four answered 304, thirty sent a body, one
did not answer. **Eleven items stamped as checked and unchanged.** Exit 1, which is the report
handing back the five items that needed a person.

### The commission's calendar dropped a deadline, and four claims went with it

`tx-2026-0002` and `tx-2026-0024` each quoted the September 4th public comment deadline out of
the PUCT calendar feed. That feed is a rolling window and an entry comes off it once its date
has passed, which is exactly what happened. The run re-fetched the feed with a browser
User-Agent and confirmed the absence rather than assuming it.

Both items were repaired against sources that keep their own history. `tx-2026-0002`'s two
claims moved onto the Interchange filing index, where they now carry the earlier April 8th round
of questions for comment and the numbered open meeting item that set the September deadline,
both of which the record did not previously hold. `tx-2026-0024`'s two moved onto entries the
feed still carries, and they now record that the commission's calendar also lists the grid
operator's own board meetings at a separate address. The Texas Register acknowledgement filed
under control number 58482 still states the September 4th deadline, so nothing about the shut
window was lost.

`tx-2026-0024`'s summary said the feed carried two comment deadlines. It carries one. That was
corrected in the same commit.

### Three items confirmed where the diff could not confirm them

- `tx-2026-0120`, the border biometrics assessment, returned **403 to the record's fetcher on
  twelve claims** and read normally through a different path. The account is still published and
  still says image capture exceeded expectations in both day and night conditions.
- `tx-2026-0036` and `tx-2026-0046` sit behind publishers whose crawl rules now exclude
  automated readers. Both were confirmed against their OTHER source, the San Antonio station and
  the company's own filing with the federal securities regulator, and both carry a dated line
  naming what stays unconfirmed.

### The geography backlog is empty and stayed empty

`site_build.py` printed no `backlog:` lines at all, on a run that admitted two items. Both new
items name a county.

**All twelve deterministic movement notes were re-worded.** `reverify.py --check-notes` reads
531 checked notes and finds every figure traceable.

## Phases 4 and 5, discovery and admission

Five scouts, three of them on application beats, per the rule that at least half must be. The
PUCT calendar, the Texas Register, the Federal Register API and CourtListener were all polled.

**The record and the calendar agree.** The feed's live September 17th comment deadline for
Project 59550 is `tx-2026-0107`, its September 22nd workshop on Project 58555 is
`tx-2026-0109`, and its October 6th workshop is `tx-2026-0139`. Three independent
cross-checks that the record is current rather than merely recent.

**The policy scout's largest gap was closed from the main context.** It could not read the
September 4th Texas Register `In Addition` item titled "Public Utility Commission of Texas -
Memo Establishing Comment Deadline", and named it as the likeliest missed primary document. It
is **Project 60154**, a rulemaking petition by Jeff Pelletier to amend 16 TAC Section 25.211(n)
so utilities file distributed generation interconnection reports monthly rather than annually,
with comments due Friday, October 2nd, 2026. It is not admitted, because it is a grid visibility
petition with no AI nexus, and admitting it would be padding the record with something a reader
came here for the opposite of.

Two items admitted, two more promoted automatically because their sources cleared this run
(`tx-2026-0126` and `tx-2026-0130`), and both of those were re-verified and stamped before the
build.

- **`tx-2026-0140`**, the deck's subject. NHTSA Audit Query AQ26002. Twelve claims, every one
  primary, all from the agency's own opening resume.
- **`tx-2026-0141`**, UT San Antonio's off-grid flood node. Eight claims, all primary.

**The admission gate caught one of my own sentences.** `tx-2026-0141` was held on the first pass
for the British spelling "programme" in prose I wrote. That is the house-style gate doing its
job on the run rather than on the sources.

## Phase 7, the instruments and the discoverability signoff

`gridwatch_pagecheck`, `waterwatch_pagecheck` and `waterwatch_page --self-test` all exited 0.
Both pages are current and holding their promises. Nothing to fix and nothing stopped.

One observation that is NOT an alarm and is recorded because a later run should not rediscover
it as one. `ledger/gridwatch/weather.jsonl` runs to September 7th and `readings.jsonl` to
September 8th, while both files were written today. Those are publication lags in NCEI and in
the ERCOT dashboard feed rather than a stopped collector, and the two page checks that exist to
tell those apart both returned 0. **A run does not own these files and this one did not touch
them.**

**The scanner ceiling was NOT checked.** No Supabase connector is available in this session, so
`scanner.scans` could not be queried. This is recorded as not looked at rather than as fine.

### Discoverability signoff

- **One decision's card, opened as an image.** `docs/og/tx-2026-0139.png`, the newest item at
  the time of the check. Four lines, wrapping at real word boundaries, dark ground and the flag
  block at left. **It ends "would curtail a…", which truncates on an article.** The wrapper cuts
  on width and the last word it kept is a two letter function word, so the card trails off
  rather than stopping. Not a broken card and not a gate failure. Written up as an upgrade
  candidate below rather than fixed inline, because `scripts/site/og.py` is in this lane and the
  fix belongs with the phase whose job is editing the machine.
- **`/questions/`, read as a reader.** Eight question shapes. "Where a comment window is open"
  answers 03, and those three are `tx-2026-0107` closing September 17th, `tx-2026-0118` closing
  October 20th and `tx-2026-0075` closing November 3rd. Every one is genuinely open. Questions a
  Texan would type, and the counts are honest.
- **The `Open right now` section of `llms.txt`.** Ten entries, and the one that matters is the
  one that is NOT there. `tx-2026-0002`'s window shut on September 4th, its room is
  `contact_only`, and it is correctly absent. A window that closed six days ago and was still
  advertised would be the exact merge-order fault this bullet exists to catch.
- **`/sources/`.** **573 of 655 claims rest on a primary document, across 214 documents from 99
  publishers.** The top publisher is `interchange.puc.texas.gov` at 97 claims, which is the
  commission's own filing index and is a primary source, so the record leans hardest on exactly
  the kind of document it says it does. Both items admitted today are entirely primary, so this
  run moved the share up rather than down. Quoted material is still carrying its punctuation
  exemption and none of our own sentences are hiding inside it.
- **`/topic/`.** Eight beats. The card counts are 29, 3, 13, 14, 12, 21, 17 and 10, which sum to
  119, the number the front page's own counter printed at the time of the check. The three
  "still open to comment" figures sum to 03, which matches the front page and `/questions/`.
  Three surfaces computing the same figure from the same ledger and agreeing.
- **`/place/`.** 63 counties across 28 statistical areas. Travis, where `tx-2026-0140` landed,
  and Bexar, where `tx-2026-0141` landed, both already carry pages, and both appear on the hub.

The seven discoverability checks all exited 0.

## Phase 8, selection

**The story is `tx-2026-0140`, NHTSA Audit Query AQ26002.** On September 3rd, 2026 Tesla began
paid commercial deployment of the Cybercab in Austin. The vehicle has no brake pedal, no gas
pedal, no steering wheel and no mirrors. Tesla certified it ITSELF as compliant with every
applicable Federal Motor Vehicle Safety Standard and told the agency so. The agency opened an
audit the same day into the process and the technical data behind that certification, and said
it will consider how far the certification rested on Tesla determining that certain standards do
not apply at all.

**Why this and not the others.** Three candidates cleared their sources this run.

- The **statewide Flock unwind** was the loudest story of the week. Bastrop decommissioned and
  wrote a standing bar, Liberty Hill terminated 7 to 0, El Paso halted about 150 state funded
  cameras, and Dallas voted to keep paying for its own out of local money on the same day its
  police lost the state grant. `dedupe_check` returned **LIKELY REPEAT at 0.70** against carousel
  no. 12 and 0.48 against carousel no. 4, and `surveillance-and-policing` is five of the last
  nineteen decks and **two of the last three**. A third surveillance deck in four days is a feed
  rather than a record. The record still takes the story; the deck does not.
- The **UTSA flood node** returned "nothing close" and is the cleanest story here. It is
  admitted as `tx-2026-0141` and it is a good deck for a later run. It is a prototype with no
  named deployment site, which is a real ceiling on stakes.
- The **Cybercab audit** returned nothing at the repeat threshold, one faint 0.21.

**The overlap I read in full before clearing it, because a run eight days ago got this exact
call right from the other direction.** Carousel no. 5 lists NHTSA among its entities and
"robotaxi" among its keywords. On 2026-09-08 a run rejected a federal crash count story as a
repeat of no. 5, correctly, because no. 5's declared angle was "the gap between what the machines
measure continuously and what the state publishes a crash count for", and a crash count is the
ANSWER to that deck's own question.

This story is not. No. 5 was the STATE authorising commercial operation. This is a FEDERAL
agency auditing a manufacturer's own certification of a vehicle's construction. Different body,
different instrument, different question, and the agency says in its own words that the audit is
about the certification rather than about how the vehicle drives.

**So the angle is locked on certification and the deck may not drift into driving.** The
fact-checker was instructed to REJECT any claim about how the vehicle drives, its safety record
or crash data, and to say why. That instruction is what keeps this deck distinct from no. 5, and
it is a constraint on the art as much as on the copy.

`texan_check` at selection: places Austin and Travis County, body yes, next step yes.

## Phases 9 to 14, the deck

### The directors room, and two of the three corrected the showrunner

Three treatments, three lenses. **Lens C, THE PATH ALREADY WALKED, is the spine**, and the
deciding argument is not taste. Carousel no. 19's `avoid_next` says *"Draw the next deck in the
Big Bend dusk family and do not reach for a light ground until the counted window holds none."*
Lens A was a shop interior under a raking LED strip and lens B a fabrication table under an unseen
overhead source. Both were dark. **Neither was Big Bend dusk.** C is a caliche two-track on the
Edwards Plateau twenty minutes after sunset and its cover technique is the dusk field itself.

C also carries the strongest answer to this deck's hardest constraint, and it answers it as
GEOMETRY rather than as wording: **no vanishing point in nine frames, so not one camera sits where
a driver would.** A caption can be argued with. A camera position can't. Grafted from B and made
absolute: **no vehicle in nine frames**, not whole, not in part, not in silhouette. Grafted from
A, its own stated risk, adopted verbatim as this deck's editorial law: *if a judge reads any frame
as a safety finding, that frame is rebuilt, not relabelled.*

**Director C corrected a factual error in my brief, and it is the second correction this run.** I
told C that Zoox "was investigated" after self-certifying. **That is nowhere in `claims.json`.**
c20 is the 2022 self-certification, c21 is "then went through the official process and filed", c22
is the July 2026 approval, and the fact-checker's `rejected` list had already thrown out the
reporter's characterisation about commercialisation being slowed. No frame says it. The first
correction was the fact-checker throwing out my "instead of" framing on the same two claims.

### The palette was MEASURED before it was drawn, and the metric was calibrated first

Director C warned that this register's colours sit where decks 18 and 19 already sat, and named it
as the failure deck 10 shipped. Measured in CIELAB against the 80 distinct hexes in the last eight
decks' ledger entries, **all eleven proposed tokens came back inside dE 10.**

**That number means nothing without a baseline, so a baseline was computed before anything moved.**
Against those same 80 hexes a RANDOM colour's nearest neighbour has a median dE of 29.2, and only
about one in ten falls under 10.4. Eleven of eleven under 10 is a real signal rather than an
artefact of a dense corpus. Calibration probes: pure magenta 94.5, chartreuse 73.9, mid grey 2.4.

Four tokens moved, and each move is also physically truer for twenty minutes after sunset, when
caliche is lit by a rose sky band rather than a yellow sun.

| token | was | dE | now | dE |
|---|---|---|---|---|
| `roadbase_sun` | `#E0A97E` | 8.9 | **`#C4736D`** | 13.1 |
| `roadbase_sky` | `#7A7488` | 9.8 | **`#655F82`** | 15.9 |
| `dust_lit` | `#F4DCC0` | 5.8 | **`#E9C0B8`** | 11.9 |
| `post` | `#5A4A44` | 6.9 | **`#584049`** | 11.5 |

**Three could NOT be moved past dE 10 and are kept with that stated rather than hidden.** `sheet`
at 6.2, `sheet_shade` at 7.9 and `guard_pipe` at 7.5 are near-neutrals, and the last eight decks
have colonised the desaturated grey-blue region thoroughly. Every candidate tested came back
inside 10. A variety judge comparing those three is comparing greys, and this deck's separation
argument for them is structural rather than chromatic.

`bond` was replaced by a COOL `sheet` for a reason other than distance. Decks 12, 13 and 14 shipped
three consecutive creams and no. 19 shipped a fourth. The dE against a prior is only 6.2 and the
material family is different, which is the repetition a variety judge actually charges for.

Kept deliberately: `sky_ember` at 3.4 and `sky_high` at 0.0 are `brand.yaml` tokens and are
SUPPOSED to recur. `cedar` at 3.3 and `rut` at 7.7 are near-blacks, and below about L* 12 the eye
is not resolving hue.

### Nothing in a frame is a literal, and the mechanism was proven before nine frames leaned on it

Carousel no. 19's `avoid_next` names hand-synced literals as the defect four scoring panels did not
see. `compute.py` lifts every figure OUT OF a claim quote by pattern rather than retyping it beside
one, and raises rather than falling back if a quote stops carrying its figure.
`inject_computed.py` then writes the whole computed block into each frame in place of a
`<!--@@COMPUTED@@-->` marker, so **there is no number in a frame to go stale.** `--check` fails on
any marker left unreplaced and on any frame that never asked for the block.

**It was proven on a throwaway probe frame before a single real slide depended on it**, and the
probe rendered `4` read from `window.C.absent_control_count`. The frames are authored in `src/` and
staged into `slides/`, so injection is never a half-applied edit.

### What the gates caught, in the order they caught it, and every one was mine

- **`dossier_check` refused the first plan on SIX frames** for a bottom third carrying only flat
  furniture. All six bands were rewritten before any code was written. That is the dead lower zone
  the sibling shipped six times, killed at the stage where it costs a paragraph.
- **The cover took three builds and the second one broke the deck's own first law.** Parallel ruts
  read as drapery. Given the slight convergence a long lens really has, the frame immediately read
  as the view down a road from a seat. **Director C had named that exact repair in advance as one
  to refuse at the plan rather than argue at round four**, so it was refused: the shipped camera
  looks ACROSS the track, where nothing converges and a driver's read is geometrically impossible.
- **`putImageData` ignores the canvas transform.** Scanlines written after `g.scale(2,2)` landed in
  a quadrant and the cover came back at median L* 3.2 against a planned 26. The field is now
  written at device resolution and put once.
- **`plan_render_check` found twelve places my plan and my frames had drifted apart**, including
  three declared palette tokens no frame actually drew. Frames were changed where the plan was
  right and the plan where the frames were.
- **`verbatim_check` caught a dropped narrowing word inside a verbatim slot.** The dossier declared
  `filed for a temporary exemption from eight Federal Motor Vehicle Safety Standards` and c21 says
  `a temporary PART 555 exemption from eight...`. That is HIGH QUALITY IMAGES exactly, which three
  judges found on 2026-09-04 and no other gate could see.
- **`numeral_trace` caught the rotating footer cell** printing 49 and 555 on two frames citing
  claims that carry neither figure. The cells now read FMVSS and ZOOX, 2022, both traceable to
  claims those frames cite.
- **`panel_ready` opened at 32 findings.** Contrast was systemic: the furniture palette was chosen
  for restraint and almost every line measured under the rubric's 4.5 floor.

### THE RUN'S WORST HALF HOUR, and it is a measurement error rather than a craft one

A whole round of colour fixes came back reading as no change at all. `panel_ready` takes its
contrast numbers from `machine_qa.json`, and that file was **seven minutes older than the PNGs it
was describing**, because `qa.py` had not been re-run after the render. The fixes had worked the
whole time. The same report, read fresh, went from 30 contrast failures to 9.

That is the STALE row `gate_status` exists to catch, arriving one stage earlier and with nothing
watching for it. **`qa.py` now runs inside `build.sh` on every render, full or `--only`**, so a
report can no longer predate the artifact it describes.

### The value arc, measured off the shipped PNGs rather than asserted

```
planned    26   12   58   16    9   34   11   20   33
measured 28.5  9.6 52.4 24.7  7.4 42.6 17.7 12.0 45.0
```

Deck median **24.7** against a planned 20, which pays the artwork ledger's dark-deck debt with
room. The shape holds: the floor is slide 5 at 7.4 and the inversion is slide 3 at 52.4, **28 L*
above the deck median**. Frames 4, 6 and 9 came in 7 to 12 lighter than planned and the plan is
NOT rewritten to hide it.

The inversion had to be rescued. Slide 3 first measured 35.7, only 11 above the deck median, and
an inversion a reader can't feel is not one. The sheet was enlarged and its ground pool lifted.

### The close was drawn first, and then rebuilt twice

Five consecutive decks have written down that slide 9 is the thinnest frame and none has paid it.
This one drew the close before the cover. It still took two rebuilds after that: the guard's rails
ran through the hook's glyph band and `qa.py` read them as a strikethrough four times over, and the
first shading pass made the ruts read as lit vertical columns rather than as troughs from above.
A rut in true plan is darker than the crown at its floor and takes the key on ONE lip.

### The deck's known ceiling, stated rather than papered over

`texan_check` reports **NEXT STEP NO**, and the record is why. AQ26002 carries no comment window,
no hearing and no deadline anywhere in `claims.json`. The close gives the reader the thing the
record actually holds, which is a published resume and a number to read it by. **The reserved flag
red is unspent for the same reason**, because it is for a dated door and this record opens none.
Manufacturing one would have been the drawing asserting something the record does not.

## Phase 10, the caption room, and the critic returned NEITHER

Two directors, distinct assigned opening moves, and a critic that refused both and demanded one
rewrite. It was right on both counts and it found two things I had already rendered onto a frame.

- **"paid" appears in NO claim.** c7 says commercial deployment and c12 says putting passengers in
  it. Neither says anyone paid, and the word was building an implicit contrast with Zoox's
  exemption, which c21 ties to charging for rides. **It was on the cover's dek at the time.**
- **c10's qualifiers are load bearing.** The source says the vehicles lack PERMANENTLY ATTACHED,
  CONVENTIONAL manual controls. A car with no brake PEDAL still has brakes, and "no brake pedal"
  beside the word Defects is the safety implication this deck may not make. The cover carried the
  stripped version.
- Candidate B asserted "That list is not in the public file", which is an absence no document in
  the record establishes.

The shipped caption is the rewrite: opening move **the who**, structure **Clock**, closing move
**point at the record plainly**. 124 words, 767 characters, three hashtags, and all 76 of
`brand.yaml`'s banned phrases checked by hand, because `caption_check.py` does not read that key.

### THE CRITIC ALSO FOUND A LEDGER BUG, and it mis-briefed the room

`ledger/carousel/captions.json` handed the caption directors a **stale exclusion list**.
`structures_recent` reads `["Ledger", "Zoom out", "Pivot"]` when the last three shipped are Zoom
out, Pivot and **Two columns**. `closing_moves_recent` carries one entry when no. 19 shipped
"Name what is still not public, and how big that is". So the room was told Ledger was off the
table when it is not, and never told that Two columns and B's own close are. Both lists are
brought current in this run's ledger update.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 23 verified claim(s) |
| render         | WARN   | 9 slide(s), 39 overflow warning(s) |
| qa             | WARN   | 0 fail(s), 81 warn(s) |
| aggregates     | PASS   | 2 declaration(s), 3 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 6.14 MB, vector |
| score          | ABSENT | score.json not written yet |
| labels         | PASS   | 58 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 104 published string(s) read from one list, every universal names its set |
| verbatim       | PASS   | 15 declared fragment(s) over 9 of 9 dossier(s), every one a literal substring of its own claim's quote, 1 slot note(s) |
| dossiers       | PASS   | 49,615 chars planned |
| caption        | PASS   | 124 words |
| craft floor    | WARN   | 9 frame(s), median 701, floor 126, 1 quiet |
| plan vs render | PASS   | 12 of 72 acceptance item(s) checkable |
| texan          | WARN   | places Austin / body yes / deadline yes / next step NO |
| absences       | WARN   | 2 of 4 scoped to a named document, 2 unscoped |
| numerals       | PASS   | 17 numeral(s) over 9 frame(s), every one reachable |
| completion     | ABSENT | not scored yet |
<!-- gate-status:end -->
