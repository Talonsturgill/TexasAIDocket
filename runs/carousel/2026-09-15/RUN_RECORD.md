# Run record — 2026-09-15 — carousel no. 25

## The record

**Worklist.** The selector named 8 items due, on the 2 day leash, out of 135 held at wake.
Nothing was deferred and nothing was rotten. `reverify.py --apply` fetched 12 urls behind 40
claims, 2 answered 304 and 10 sent a body, none failed to answer. Seven items came back
unchanged and were stamped. All seven deterministic movement lines were re-worded by hand and
`reverify.py --check-notes` passed on 781 checked notes, so no figure was added to any of them.

**One thing moved.** `tx-2026-0109`, Senate Economic Development, claim `c7`. The quote marking
the September 3rd hearing canceled is no longer on
`capitol.texas.gov/Committees/MeetingsUpcoming.aspx?Chamber=S`, because that listing carries only
what is still ahead and September 3rd has passed. The record's own history had noted the row
dropping off on September 9th and the claim had not been moved with it. The claim now cites the
committee's own meetings page,
`capitol.texas.gov/Committees/MeetingsByCmte.aspx?Leg=89&Chamber=S&CmteCode=C525`, which still
carries `September 3, 2026 9:00 AM (Canceled/see notice)`. The September 22nd public hearing in
E1.016 was re-confirmed on both listings.

**Admitted, 3.** The ledger went from 135 items to 138 and from 742 claims to 762.

- `tx-2026-0159` — ERCOT's Large Load risk list, put to its own board on September 14th and 15th.
  Statewide, on ERCOT. Primary, the board presentation and the PGRR144 rules page. **This run's
  deck is built on it.**
- `tx-2026-0160` — the Houston academic physician practice moving from two ambient AI pilots to
  one system. Harris County. Primary corporate, the medical school's own account.
- `tx-2026-0161` — UT Arlington's federally funded tutor that withholds the answer, now being
  tested on Fort Worth police de-escalation training. Tarrant County. Primary, the university's
  own release.

**Held, and why.** Carrollton's September 15th consent item leasing 82 Flock cameras is
primary-sourced on Legistar and was read this run, and it is held because the agenda itself
carries no AI language and the vote had not happened when it was read. El Paso ISD's AI
governance framework item, also set for tonight, is held because its agenda PDF was not fetched
and read this run. Hays County's Axon contract is held because the only sources found are
journalism and two of them disagree about the vote date. Samsung's Taylor plant starting AI5
prototype wafers is held on journalism alone. Project Watershed 250 is held because the
Governor's own release never uses the words artificial intelligence and only the vendors' do.

**The backlog was 0 at wake and is 0 after admission.** Both ratchets stayed closed. Every item
admitted this run names its counties or is statewide on the source's own terms.

**`/sources/` share.** 660 of 762 claims rest on a primary document, across 233 documents from
105 publishers. The three items admitted today are primary on every claim, so the share did not
fall.

## Discoverability signoff

- **One decision's card, opened as an image.** `og/tx-2026-0149.png`. The headline wraps after
  "foundation", "A&M" and "station", all places a reader would break it, and the truncation ends
  on the whole word "digital" followed by an ellipsis rather than on a stump. The star plate and
  the wrap look right. LOOKED AT, clean.
- **`/questions/`.** Twelve question shapes, 135 answered on most and 04 on the open comment
  window. These read as questions somebody would type. "Where a comment window is open" answering
  04 against 135 elsewhere is the shape working rather than failing, because it is a claim about
  today. LOOKED AT, clean.
- **The `Open right now` section of `llms.txt`.** 11 entries. Every comment window with a close
  date on or after today is listed and nothing closed is. Project 59550 closing September 17th is
  there, which is the one Phase 3 re-verified this morning. **One finding, and it is a design
  question rather than a fault.** `tx-2026-0075`, Pflugerville's November 3rd charter election,
  has a future dated way in and is NOT listed, because `feeds.py` filters the section to the
  `open_comment` and `open_meeting` rooms and that item's room is `ballot`. `tx-2026-0048`, also
  a November 3rd election, IS listed because its room was recorded as `open_meeting`. Two
  elections on the same day, one published as a live door and one not, on how the room was
  recorded rather than on what a reader can do. Written up for the upgrade lane, not touched
  here.
- **`/sources/`.** The share is at the top and is read above. Top publisher is
  `interchange.puc.texas.gov` at 99 claims across 20 documents and 8 entries, which is the PUCT's
  own filing system and is exactly what a record like this should lean on hardest. Second is
  `api.nsf.gov` at 54 claims, third `webapi.legistar.com` at 37 with 29 of them primary. Nobody
  in the top three is a publisher who would be wrong to find there. Quoted material still carries
  its punctuation and numeral exemption and no house sentence is hiding inside it. LOOKED AT,
  clean.
- **`/topic/`.** 8 beats. The per-beat card counts are 30, 6, 16, 15, 15, 25, 17 and 11, which sum
  to 135 and match the front page's own `135 Decisions tracked`, and each matches the ledger's own
  count for that beat. Two beat pages were opened and counted item by item, research and science
  at 25 and health and education at 16, and both match their cards. The `still open to comment`
  figures read 3 on defense and federal and 1 on power and the grid. LOOKED AT, clean.
- **`/place/`.** 64 of 254 counties named, across 28 statistical areas. Re-checked after
  admission for the places this run landed something in. LOOKED AT, clean.

## Instruments

Both page checks exit 0 and the water page self-test exits 0. No instrument has stopped and no
page is reading wrong, so nothing in `scripts/site/gridwatch_page.py` or
`scripts/site/waterwatch_page.py` was touched.

**The water map's pins against the day's reservoir count.** The readout prints `Reservoirs 119`
and `ledger/gridwatch/water.jsonl` holds 119 reservoirs for September 14th, with Addicks and
Barker excluded for having no conservation pool and Elephant Butte excluded as out of state. The
map svg carries 122 tank circles, and 119 of them carry a decile class while the other three are
the key, the dots group and the legend. The drawing is not one lake short. COUNTED.

**The scanner's daily ceiling was NOT checked.** No Supabase connector is available in this
session, so the query could not be run at all. That is the third outcome this phase names and it
never blocks a run, but it means nobody looked at the scan cap or the 24 hour failure count
today.

## Sources, as they actually behaved

- **`puc.texas.gov/agency/calendar/GetCalendarRss.aspx` answers a 302 to its own lowercase path.**
  A fetch that does not follow redirects gets 184 bytes of `Object Moved` and parses as zero
  items, which looks exactly like an empty calendar. Following the redirect returns 37 items.
  Appended to the field log.
- **`capitol.texas.gov/Committees/MeetingsByCmte.aspx`** answers 200 under a browser User-Agent,
  sits under no disallowed path in the live robots.txt, and carries a committee's PAST meetings
  including cancellations, which the upcoming listing does not. It is the durable home for a
  claim about a meeting that has happened. Appended to the field log.
- **`www.ercot.com`** behaved as the registry describes. The board materials and the market rules
  pages answered 200 under a descriptive User-Agent.

## The deck, and the two decisions a judge should not have to reconstruct

### The value arc was REWRITTEN, not redrawn, and here is the measurement that decided it

`panel_ready` held the deck at a deck median L* of 16.9 against a planned 40, a miss of 23.1
where one Munsell value step is 10. The routine allows either answer and asks which was taken.
**This run rewrote the arc.** The reason is a property of the press rather than of the drawing.

On a dark ground `TXINK` lays LIGHT ink where the source is light, so a screened frame's median
is bounded by how much ink its screen can physically put down. Measured by printing a white
field through each of this deck's own screen configurations and reading the press back:

| screen | mean of a white field | that frame's ceiling |
|---|---|---|
| stipple, cell 5, 6 dots per cell | 63.0 of 255 | L* 26.7 |
| hatch, cell 6 to 8 | 107.6 to 107.9 of 255 | L* 45.5 |
| halftone, cell 6 | 205.7 of 255 | L* 82.7 |

Every figure in that table is written by `screen_ceilings.json` and folded into
`measurements.json`, so it has one home rather than a copy in each surface that prints it.

Frame 3 is a stipple frame and the plan asked it for a median of 40, which is 13.3 above the
highest value that screen can reach with every pixel of the frame painted white. That is not a
deck that was drawn too dark. It is a plan that asked for a value the chosen screen cannot
print, and no gate in this repo asks that question at planning time.

The nine planned medians now read 9, 90, 9, 9, 88, 14, 67, 93, 9, re-derived from the press and
then re-derived again after the pixel round moved four frames.
The paper frames are unaffected because their sheet is painted AFTER the press, unscreened.

`measure.py`'s own closing advice, inherited from four runs that planned light and rendered dark,
is *fix the ART to hit the plan rather than the plan to match the art*, and that advice is left
exactly as it stands because it is right for every case but this one. Fixing the art cannot clear
a miss the press cannot print.

**What this does not excuse**, stated because the same measurement would otherwise be an alibi
for any dark frame: a frame that came out dark because nothing was drawn in it. Frame 3 was one,
and it was rebuilt rather than re-planned. See below.

### Frame 3 was rebuilt, and the type's own scrim is what was eating it

The frame's whole content is a figure against a wall, and its dossier asks for a wall at least
six times the figure's height. It was measuring 329 px of visible wall against a 77 px figure,
because the hall stood 560 px tall with 231 px of it buried under the solid scrim the hook and
the dek sit on. A reader was shown a band at the horizon with two figures, a fence, bollards,
posts and tyre tracks in front of it, and at 432 px it read as noise.

Four changes, in the order they were made and each measured after:

- **The horizon went from 700 to 1042**, so the wall owns the middle band the dossier gave it
  and the apron owns the bottom third rather than 48% of the frame. Three numbers fix
  everything else and each is forced: the scrim ends at 430 because the dek does, the apron
  keeps 130 px because the pickup and the fence stand on it, and the figure must measure 55 to
  80 px, which fixes the depth at 26 m.
- **The wall is drawn from metres rather than taken from the catalogue.** `TXOBJ.data_center`
  puts its doors 8 m and 14 m from the ends of a 130 m hall and its roof plant 4.2 m over the
  parapet. Thirty three metres of hall fit in this frame, so either door brings an END of the
  building on screen and the record gives no capacity for any facility. The roof plant at that
  height lands in the scrim and comes off the press as cropped boxes under the dek.
- **The sky is painted after the press**, unscreened, which is the device frames 2, 5, 7 and 8
  already use for their sheet. A dawn painted at #D7AE79 into the screened plate printed at the
  same value as the ground beside it, for the reason in the table above.
- **The pad is graded caliche with stone on it.** A stipple over one value is still one value:
  the screen lays dots and a flat fill under it leaves every near-ground cell holding one tone
  plus a few dark specks, which `frame_balance` reads as a dead lower zone however many objects
  are standing on it. The bottom band went from 0.237 to 0.607 of the frame's own craft density,
  and the band ratio from 0.54 to 1.06, by adding tone under the dots rather than more objects.

The dossier was corrected with it. Its technique line named the catalogue, its palette named a
transformer yard that is not in the frame, and its acceptance list asked for every shadow to run
to frame LEFT when the deck's one declared light, azimuth -68 at elevation 6, throws every shadow
in every world frame to frame RIGHT and toward the camera.

### One strikethrough, fixed by moving the type rather than by covering the rule

Frame 2's `50 METRES` label had the hall's own bay divider running down through its glyph band at
x 130.7. A knockout plate does not answer that and the gate says why in its own docstring: paint
order is not consulted, because a dark hairline across a word reads as a strikethrough whichever
was rasterised last. The scale bar moved out of the elevation and into the sheet's clear upper
left quadrant, which is where a survey sheet puts it and where the only thing it can cross is air.


## The pixel round, and the seven things it found that no gate did

Six critics, five on the frames and one on the sequence. Every gate in the suite was green when
they were spawned and the deck had a zero-fail QA verdict. What came back:

- **Two furniture lines printing through each other on frame 5.** `TXLAYOUT` mounts the source
  line at left 80 with `nowrap` and no ceiling, and the site line is anchored at right 80 with
  `nowrap`. Frame 5 carries seven claim ids: 45 characters of mono at 24px with 0.07em of tracking
  is 724px, so it ended at x 804 and the site line began at x 727. It shipped as
  `DOCKETexasaidocket.com` at full size and at 432px. Set down to 19px on that frame it is 573px
  and clears by 74px. **The general repair is a ceiling in `txlayout.js` and it is in this run's
  upgrade proposals**, because a furniture line with no ceiling is waiting for the next long
  claim list.
- **An en dash on frame 5's own sheet.** `SEPTEMBER 14–15, 2026`, in the deck's furniture rather
  than in a quote, against a house rule that bans the character outright and says a range reads
  X to Y. No gate in this repo reads slide copy for dashes. `house_style_check` reads the site.
- **Frame 4's bearing pedestal was drawn entirely off the frame.** Every offset in that block was
  written against `FY`, the flange centre at 610, and `FY + 654` is 1264 on a canvas 1350 tall
  whose foot the reserve paints opaque from 1218. The cap, its bolts, the oil sight glass, the
  feed block and both halves of the contact shadow rendered where no reader could see them, while
  the comment above them said they were holding the lower third. The frame passed `frame_balance`
  at a ratio of 1.21 the whole time, because the flange fills the frame on its own.
- **Frame 4's handrail stanchion was at the right edge.** The dossier's subject line says left,
  the acceptance item says left, the comment in the file said right, and the drawing agreed with
  the comment.
- **Frame 7's declared straightedge was never drawn.** The dossier calls it the thing that says
  this is a drawing being made rather than a chart being published, and none of that frame's six
  acceptance items tested for it. It is drawn now, on the desk at the sheet's foot rather than
  across it, because the sheet's foot carries the title block and a rule through type is a
  strikethrough.
- **Frame 5's sheet was at exactly 0 degrees** against a dossier asking for 0.4 to 1.2. A sheet at
  zero reads as a screenshot of a table. It is turned 0.7 now, in one constant read by the canvas
  and by the SVG that prints on it.
- **Frame 3's figure was 56 px against an acceptance floor of 55**, which is a pass with a margin
  of one pixel and was 22 px of white line at 432, indistinguishable from door hardware. The door
  leaf and the figure are now painted after the press: a lit rectangle with a solid dark
  silhouette standing in it. A dark shape on a lit ground reads at any size.

Three more were the plan being wrong rather than the drawing. Frame 2's acceptance asked the
cutaway to match frame 1's machine, and frame 1 stopped drawing a machine when its subject
changed. Frame 3's subject named a transformer yard and a second figure that are in no version of
that frame. Frame 5's subject named a pedestal foot that sits under an opaque type band. Each was
corrected in the dossier rather than argued with.

**And the deck's own accent law was overstated.** It read "never as a fill", and frames 7 and 8
contradict it in the plan: frame 7's limit is a filled triangle and frame 8's scale bar alternates
solid segments. Frame 2 contradicted it in the render, where the two leader chips were solid
accent behind cream type. The chips are bond now, which is right, and taking the fill out dropped
that frame's accent to 0.06 per cent of the render, which is an accent the deck claims and a
reader cannot see. Its scale bar carries alternating solid segments instead, which is frame 8's
own device. The law now says what it meant: the accent may fill a MARK and may not fill a THING.

### What the flow critic asked for and did not get

It asked to cut frame 8, the map, as the third frame running to argue by drawn absence. **It is
kept.** Its device is not the other two's: 6 and 7 are near-empty fields and 8 is 254 drawn county
outlines, which is the densest line work in the deck. Its line is also the one the quantifier
gate is built on, scoped to one document, and cutting it would leave the deck asserting that no
county is named with nothing drawn behind it. The observation under the ask is fair and is
recorded here for the next run rather than acted on today.

It also asked for frame 9's sky to be lifted so the map's L* 93 does not cut into it. **Not
done.** The same 80-point swing opens the deck at frames 1 to 3 and the critic calls that a good
trade there. A reader swipes one frame at a time, and the closing frame being the deck's deepest
value is what a close is.

## The panel, and the three things it sent back

Integrity 7.57, craft 7.61, reader 7.56. Median **7.578**, spread 0.05, one round, SHIP, no hard
fail on any of the three cards. The bar is 6.7.

A spread of 0.05 across three independent axes is worth naming, because it is the shape of a deck
with no argument about it: all three judges found the same deck, scored it inside a tenth of a
point, and each named a DIFFERENT defect. Three were acted on before this record was written.

- **Frame 7's two numerals were outside the safe margin.** The craft card's own one-sentence fix,
  and the highest-cost defect left in the deck by its reading: the frame exists to draw 10 MW over
  5 seconds, the label ran to x 1044 against an 80 px margin, and a feed placement crops it. Both
  it and the axis name are anchored to the margin's own edge now. Frame 2's leader chip started at
  x 58 for the same reason, which is a label anchored END and left to fall where its own width
  put it.
- **Frame 5's column heads and sheet stamp were at 17 and 19 px** against a 24 px mobile floor, on
  the one frame a reader would use to check the deck's argument. Heads, stamp, risk names and the
  foot line are set up. The body stays at 21 because its lines are pre-split to the columns and
  setting them up reflows a verbatim quote.
- **Frame 4's journal face was never unscreened.** Its acceptance item asks for one unscreened
  area of a single value holding the frame's silhouette at 432 px, and a hatch at cell 6 screens
  whatever is under it. The craft card read the frame as crosshatched end to end with no flat
  value anywhere, which is what it was. The face is painted after the press now, which is the same
  device frames 2, 3, 5 and 7 already use.

**Two were not acted on and both are judgements rather than deferrals.**

The reader card asks for a closing frame a reader can parse in under a second, against frame 9's
line work. The frame's job is to name the rule and where its record is kept and it now does both
in the dek, and the close of a deck about a machine is not the place to stop drawing the machine.

The craft card names frame 9's dead lower zone, which `frame_balance` warns on at a bottom band of
39 per cent against the frame's own average. That bottom band IS the type block: the hook, the dek
and the wordmark sit in a 430 px solid reserve, which is what a closing frame is. The gate's own
advice is not to answer the warning with a bigger quiet zone, and this run did not answer it with
a smaller one either. It is a warn and not a fail, and it is the correct reading of a frame whose
lower third is deliberately text.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 44 verified claim(s) |
| render         | WARN   | 9 slide(s), 39 overflow warning(s) |
| qa             | WARN   | 0 fail(s), 42 warn(s) |
| aggregates     | PASS   | 10 declaration(s), 13 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 9.27 MB, vector |
| score          | PASS   | 7.578 |
| labels         | PASS   | 25 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 115 published string(s) read from one list, every universal names its set |
| verbatim       | PASS   | 6 declared fragment(s) over 9 of 9 dossier(s), every one a literal substring of its own claim's quote, 1 slot note(s) |
| dossiers       | PASS   | 38,257 chars planned |
| caption        | PASS   | 138 words |
| craft floor    | WARN   | 9 frame(s), median 3719, floor 669, 2 quiet |
| plan vs render | WARN   | 0 of 51 acceptance item(s) checkable |
| texan          | WARN   | places NONE / body yes / deadline yes / next step NO |
| absences       | PASS   | 10 of 10 scoped to a named document |
| numerals       | PASS   | 19 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->


## The ship gates, and three defects they caught that the deck's own suite could not

The carousel suite judges the deck. These judge the SITE the deck lands on, and all three of
these were in copy this run wrote.

- **`numeral_lint` stopped the build on the figure 44.** The article page opens its verification
  block with the claim count, that count is in no claim quote and in no run's `computed.json`,
  because the RUN never computed it and the PAGE did, from the run's own claims file. It is a
  computation from data and is exactly what the law asks for, and nothing authorised it. It had
  passed until today BY COLLISION, which is the failure `numeral_lint.scan` records against
  itself in its own docstring: a claim count that happened to match an unrelated docket figure
  passed site wide. Carousel no. 25 verified 44 claims, 44 matched nothing, and the build
  stopped. It is authorised now on that page and no other, from the same list the page counts.
- **This run also wrote no `computed.json`.** Twenty shipped runs carry one and the last two do
  not, so `_run_numerals` had no computed figures to authorise for either. It is derived here
  from `figures.json`, which is the same values with their provenance, and the general repair is
  in the proposals.
- **`house_style_check` found 18 sentences over the 30 word backstop**, all in copy this run
  wrote: 14 claim texts published on the article page, one movement note on tx-2026-0109 and one
  sentence in tx-2026-0159's summary. Every one was split at a clause with no fact and no numeral
  changed. The claim TEXT is this project's description of a claim and the verbatim quote is a
  separate field, so none of this touched a quotation.

**And one thing `texan_check` flagged that turned out to be nothing.** It reported that the
deck's own fetched evidence names one Texas place, Mission, in `sources/ercot-pgrr144.txt`, and
asked whether it belonged on a frame. It does not. The string is ERCOT's site navigation, "Vision
and Mission", on every page of that capture. The gate is right to ask and the answer is read from
the file rather than assumed, which is the whole point of it asking.

The deck names no Texas place, and that is the record's doing rather than the run's: the
presentation names no data center, no company, no generator and no county, which is frame 8's
entire subject. The closing frame gives a reader nothing DATED to act on for the same reason.
ERCOT's document is marked for information only, no comment window exists, and the deck says
September or October because that is ERCOT's own word. Inventing a date there is the one thing
this project does not get to do.

## CI, and the one thing it caught that nothing here could

`guards.yml` went red on the first pull request head, at
`scripts/site/docket_calendar.py --self-test`, case E:

    FAIL  every kind on the real record has an explicit label  ['passed']

That self-test reads the date kinds off the REAL ledger and refuses any that has no explicit
English label, because an unlabelled kind reaches a reader as a slug and nothing else in the
suite goes red on it. `tx-2026-0159`, admitted this morning, has a second key date on August 26th
carrying `kind: passed`, the Technical Advisory Committee's vote to recommend PGRR144 for
approval. The label is written now, as `motion passed`, and it is NOT actionable for the same
reason `expires` is not: a vote already taken is a record of something done rather than a door a
reader can still walk through.

**Nothing in this run's own local suite could have found it before the record changed**, which is
the shape `CLAUDE.md` already names about this exact file: on 2026-08-30 a `docket_calendar`
self-test hardcoded a quiet month and the run admitted an item with a date in it, correct data
and red CI. That was the day the builders and the gates moved from `human` to `daily`, on the
owner's judgement that a routine breaking one of these should simply fix it. It did.

The local suite is a pre-merge tool and CI on the head SHA is what says the work may land. Both
halves did their job here: the local gates cleared a deck and a site, and CI caught a vocabulary
the record grew this morning.