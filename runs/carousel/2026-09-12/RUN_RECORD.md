# Run record, September 12th, 2026

Branch `claude/daily-2026-09-12`. One routine, two deliverables, the record first.

## THE RECORD

**The worklist was cleared in full and nothing was deferred.** `docket_staleness --today
2026-09-12` named 99 of 127 items due, every one of them three days past a two day leash, with
nothing rotten and nothing in DEFERRED. After the pass, `docket_staleness` reads 0 due today.

`reverify.py --today 2026-09-12 --apply` did the bulk of it and did it for nothing: 178 urls
behind 520 claims, 22 answered 304 and sent no body at all, and **68 items came back with every
claim unchanged and were stamped with their movement line written.** It exited 1 and handed back
31 items, which is the part worth a person's attention and is what the rest of this section is
about.

### What the fetcher could not settle, and what each one turned out to be

The handback split three ways: one quote genuinely gone, 22 claims whose source did not answer,
and 55 that the check says it cannot read and claims nothing about either way. Every one of the
31 items was fetched again this run with a browser client that reads PDF and JSON as well as
HTML, and the disposition below is what the page actually said rather than what the first pass
could see.

**18 items came back with every claim present**, once the fetch could read the document. The
three things that had been in the way were a PDF with no extractor behind it, a JSON API whose
smart apostrophe survived one encoding and not another, and a numbered list whose tab became a
space. None of them was the record moving. San Angelo's three water ordinances, Killeen's
agenda, the Armstrong County order with its twenty four claims, and the Somervell to Howard line
all read exactly as the record holds them.

**Four items rest on a page that only carries what is still ahead**, and their entry has rolled
off it. The canceled Carson County meeting is off the agency's hearing list with no rescheduled
date posted. The August 25th transportation hearing and both water and agriculture sittings are
off the chamber's upcoming list. Brazos County's own notice of the RELLIS abatement assignment
has rolled off its news page. Nothing about any of those decisions moved. What moved is the
reader's way in, and each item's movement line says so plainly rather than reporting a fetch.

**Two dockets keep growing and the record now says so with a dated count.** PUCT 59315 stands at
5829 filings and 59029 at 514, both read this run. Each is added as a NEW claim rather than
written over the old ones, because every earlier count was true on the day it was taken and the
series is the thing that shows the docket is still live.

**Two items rest on a university page that refuses this client.** `news.rice.edu` answered 406
to every request for the Army antenna center and the Energy Department magnet award. Both items
are still funded on the terms the record holds and both movement lines name what is therefore
unconfirmed today, which is the wording of the university's own description.

**`tx-2026-0027` is confirmed by its own 404.** The City of Taylor's notice of the amended Compal
abatement is still gone from the page that carried it, which is what the item says, so the
absence is the confirmation rather than a failure to confirm.

### ONE THING MOVED, AND IT IS THE KIND OF THING THIS RECORD EXISTS FOR

**The Motor Vehicle Crime Prevention Authority has taken its next board meeting off its page.**

`tx-2026-0111` is the Governor's order pausing state agency funding for Flock plate reader
cameras. The authority that wrote those grants is where a further grant would have to appear, so
the item's public access pointed at the authority's own meetings page and its claim `c7` quoted
the line that listed a board meeting for October 13th, 2026.

That line is gone. The page's public meetings list now ends at a July 24th, 2026 board meeting,
and the block that used to head the page with an upcoming date is commented out of the HTML
behind a note saying no future meeting information is available. A reader opening that page today
sees no future meeting at all.

So `c7` now quotes what the page says, the October date is off the item's key dates, the public
access note says there is no posted date on which a further grant could be taken up, and the
summary says the authority listed the meeting and has since taken it down. **The pause itself is
still in force and no agency has published a resumption**, which the six other claims on that
item confirmed this run.

This is the case for a two day leash on a decided item, made by the record rather than argued.
Nobody announces a delisting.

### Admitted

Three, all on a document this run fetched, all naming where they land.

- **`tx-2026-0147`, El Paso City Council posts two items to strip the police plate reader
  cameras off city property and bar the next contract.** El Paso County, pending, and the only
  one of the three a reader can act on. The council meets at 9:00 AM on September 15th and the
  agenda is final. Item 25 would give the City Manager 60 days to remove every fixed camera from
  city property and right of way. Item 26 would bar a further contract without a council vote and
  give the City Attorney 30 days to draft the resolution. Source is the council's own agenda.
- **`tx-2026-0148`, Energy Department funds a synthetic underground test pit at a Navasota
  drilling site to prove out mining automation.** Grimes County, decided September 9th. The
  department's announcement names Navasota as the project location, and Navasota is the Grimes
  County seat. The university's Dallas headquarters is a decider address and is deliberately not
  carried as a county.
- **`tx-2026-0149`, Science foundation funds a Texas A&M engineering station to build AI digital
  twins of small water systems.** Brazos County, decided September 9th, running to August 31st,
  2029. The award record carries Artificial Intelligence among its programs and names no Texas
  utility, so which water system's data this reaches is not stated.

### Held, and why it is the right answer

Nineteen seed candidates stayed held. Two of them are worth naming because the reason is
structural rather than a defect in the item.

**`tx-2026-0135` and `tx-2026-0143` are the same shape of decision and the record treats them
differently.** Both are ERCOT acting across its whole footprint on Batch Zero. `tx-2026-0143` is
published with `statewide: true`. `tx-2026-0135` is held because it names no county and the
admission gate is explicit that `on_ercot` is a property rather than a place. The previous run's
hold was careful and its reasoning is sound on its own terms. What is not sound is the record
carrying both answers, and resolving it either way is a call a maintainer should make rather than
an unattended run. Named here rather than quietly fixed.

**`tx-2026-0134`, Katy ISD, is held for a county the gazetteer cannot supply.** The district's
own posting does not name the counties it sits in, and `assets/geo/tx-places.json` holds counties
and metros but no city to county crosswalk, so there is no source in this repo that turns a
district name into a place. Left held.

### The backlog

**Zero at wake and zero at ship.** `docket_build.backlog` returns nothing: no item on the record
is without a county or statewide flag, and no reader copy points at an id the record does not
carry. The ratchet is at the floor and this run did not move it either way.

## Discoverability signoff

Six surfaces, opened and read this run on the build at `out/2026-09-12/tmp/site`.

- **One decision's card, opened as an image.** `og/tx-2026-0149.png`, the run's newest item.
  Four lines of Fraunces on the night plate beside the star, wrapping at word boundaries, ending
  on a whole word with an ellipsis after "to build AI digital". The wrapper cuts on width and
  this title's longest token is "foundation", so nothing stumps. LOOKED AT, correct.
- **`/questions/`, read as a reader.** Eight questions, and they are questions somebody would
  type: what each decision is, who decides, how the public can take part, where a comment window
  is open, where in Texas each one applies, what has been decided, what happens next. The counts
  behind them are 130, 130, 125, 5, 130, 130 and 127. The 125 and the 127 are the honest ones:
  five items carry no room the record can name and three have no next dated step. LOOKED AT,
  correct.
- **The `Open right now` section of `llms.txt`.** Four decisions with a dated way in, and it
  leads with `tx-2026-0147`, admitted this run, at the September 15th council meeting. Cross
  checked against the open windows Phase 3 re-verified: the two federal comment windows close
  October 9th and November 9th, the compute derivatives window is still open, and nothing that
  closed is still listed. The build ran after the record moved, which is the merge order this
  bullet exists to catch. LOOKED AT, correct.
- **`/sources/`, the record's own report card.** **628 of 710 claims rest on a primary
  document**, across 226 documents from 102 publishers. All three of this run's admissions cite
  `primary_official` on every claim, so the share moved up rather than down. The top publisher is
  `interchange.puc.texas.gov` at 99 claims and the second is `api.nsf.gov` at 54, and both are
  the filing system and the award record themselves rather than a report about one, which is the
  answer this bullet is looking for. The quoted material exemption is still scoped to quotes.
  LOOKED AT, correct.
- **`/topic/`, one card against its own page.** Research and science prints 25 on the card and
  its page lists 25 decisions. The eight beats sum to 130 and the front page counter row prints
  130. The `still open to comment` figures are 3, 1 and 1, summing to the 5 that `/questions/`
  answers and the `05` the front page prints. LOOKED AT, correct.
- **`/place/`, for the places this run landed something in.** El Paso County, Grimes County and
  Brazos County are all on the hub and all three pages exist. Grimes County's page reads 2 items
  in the record and lists 2. El Paso County reads 5 and lists 5. Brazos County reads 7 and lists
  7. Each moved with the record on this build rather than after it. LOOKED AT, correct.

**The front page counter row.** 21 articles, 09 videos, 130 decisions, **710 sources cited**, 05
doors open to you. `Sources cited` is rendering, which is the row this file has told two previous
runs to protect.

**The water map's pins against the day's reservoir count.** The readout says 119 reservoirs. The
map's SVG carries 119 `hit` circles, one per reservoir, and 122 drawn tanks, of which three carry
no depth class and are the size legend's own samples. 119 pins for 119 reservoirs. The map is not
a lake short.

## THE INSTRUMENTS

**No stopped instrument.** Every check in Phase 7 exited 0: both page checks, the water page self
test, and the six discoverability surfaces. Nothing to report and nothing to fix.

**The scanner's daily ceiling was NOT read this run.** There is no Supabase connector attached to
this session, so the query in Phase 7 could not be run at all. This is the phase's third outcome
and it blocks nothing, but it means nobody knows today whether the scan form hit its cap or
whether a scan failed, and a ceiling nobody is notified about is exactly what that step exists to
catch.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 28 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 5 warn(s) |
| aggregates     | PASS   | 7 declaration(s), 8 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 8.54 MB, vector |
| score          | ABSENT | score.json not written yet |
| labels         | PASS   | 24 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 95 published string(s) read from one list, every universal names its set |
| verbatim       | PASS   | 8 declared fragment(s) over 9 of 9 dossier(s), every one a literal substring of its own claim's quote, 1 slot note(s) |
| dossiers       | PASS   | 54,981 chars planned |
| caption        | PASS   | 156 words |
| craft floor    | PASS   | 9 frame(s), median 3192, floor 575 |
| plan vs render | WARN   | 0 of 47 acceptance item(s) checkable |
| texan          | PASS   | places Austin / body yes / deadline yes / next step yes |
| absences       | PASS   | 3 of 3 scoped to a named document |
| numerals       | PASS   | 11 numeral(s) over 9 frame(s), every one reachable |
| completion     | ABSENT | not scored yet |
<!-- gate-status:end -->

## THE DECK

Carousel no. 22. **Texas State University's AI method for pavement condition assessment**, docket
item `tx-2026-0131`, selected over five other candidates against the dedupe gate with the reasons
written down before a frame was drawn. El Paso's plate readers came back at 0.92 LIKELY REPEAT and
were correctly refused.

The argument is one sentence. **The judgement left the shoulder, and the same team's own peer
reviewed paper puts it back in a human hand.** Frames 1 through 6 build that one direction without
hedging and frame 7 reverses it out of c17, which says the precision of the technology often leads
to inaccuracies that must be verified by pavement engineers.

### THE REGISTER INVERTED AT FRAME ONE, AND THAT IS THE RUN'S BEST DECISION

The plan opened on a PAPER register. The first frame built rendered clean, read handsomely and
**measured a median L\* of 91.5 against the light cap's threshold of 60.0.** That is not a drawing
that came out too pale. It is what a print on paper IS: a screen is marks on a ground, most pixels
are the ground, and the median of a hatched field on caliche is caliche. The three treatments'
planned medians of 44, 48 and 55 were all unreachable in that register and no amount of extra
coverage would have moved a median that is counting the paper between the strokes.

So `TXINK.print`'s ground and ink were swapped, the same twin greys and the same drawing came back
at **6.1**, and the deck shipped at a measured deck median of 6.1 with the cap's window already
holding two light decks against a cap of one.

**Two ledger entries in a row record a run that declared a value band and did not measure it until
round three.** This one measured it at frame one and paid four hours instead of two rounds.

### What the three pixel critics found, and what it cost to fix

Nine frames went to three critics. The findings that mattered, each fixed in one repair round:

- **THE TURN'S ACCENT WAS MARKING NOTHING.** Frame 7's granite was a stroked pencil loop on a white
  card and the figure's nearest finger was 165 px away from it. The deck's whole reversal is
  carried by the accent law, granite means a person, and on the one frame built to carry it the
  colour marked an empty circle on a desk. The granite is now the SHEET, filled, with a hand
  resting on it.
- **FRAME 4'S SECTION WAS ASSERTING SOMETHING NO CLAIM CARRIES.** The stain was drawn in section
  with the surface line running unbroken through it, which is a drawn claim that a stain has no
  depth. c6 says only that the pairing distinguishes damage from stains. The frame's own risk
  block had named this disposition before a line was drawn, and the section now shows the crack
  alone.
- **FRAME 5 PRINTED A COVERAGE CLAIM.** The label read PIXEL LEVEL, CONTINUOUS over EVERY SECTION,
  END TO END, six inches from the frame's own scrupulous EXTENT NOT STATED. Nothing fetched says
  the new reading covers every section. It reads PIXEL LEVEL over THE RESOLUTION, NOT THE EXTENT.
- **FRAME 8 RESTATED A PUBLISHED SCORE AS A PERFECT ONE.** The THIS MODEL label for the all
  distress series sat on the same baseline as the 1.0 gridline with dashes running out of either
  side of it, so at 432 px the eye read one line, "1.0 THIS MODEL". Both endpoint pairs now sit
  below their own point.
- **FRAME 9 WAS DRAWING RAILROAD TRACK.** Nine transverse light bands at decreasing spacing toward
  a vanishing point is the visual grammar of sleepers. The closing frame of a pavement deck now
  carries a broken centre line and one long falloff instead.
- **FRAME 1'S GRANITE WAS ON A CLIPBOARD.** Re-spriting the whole figure in the accent painted the
  board he holds as well. A clipboard is an object. The granite plate is now the body alone.
- **FRAME 5'S BREAK LINES WERE DIMENSION TERMINATORS.** Stroked in granite over a granite fill,
  only the spurs outside the block showed and they read as the arrowheads of a measured span,
  which is the exact assertion the frame exists to refuse. They are drawn in the ink now and the
  Z kink is visible through the block.

### EVERY DOSSIER WAS CORRECTED TO THE FRAME THE RUN MADE

Not one of the nine plans survived contact unamended, and `plan_render_check` found most of it
before a critic did. The palettes were written in the paper register and named nine colours no
frame contains. Frame 1's composition declared a camera on the centreline with the rater at Z 7,
which projects him to x 41 and cuts the subject in half at the left edge. Frame 3's plan asked for
the figure at 283 px against the van's 284 so the two would read as the same height, which would
have put the person NEARER the camera than the thing they are the scale for. Frame 8's composition
described a cut at y 594 with the chart above it, which was superseded twice. Frame 6's acceptance
demanded casts running down and left under a light of az +34 el 52, which is the treatment's light
and not the deck's.

**The plan is corrected to what was built, every time, with the reason recorded beside it.** The
alternative is the 2026-08-19 defect this gate exists for, where a plan said the differing words
are marked in pecos and five passes shipped uniform ink.

### What the numbers are, and where each came from

Four F1 values, a threshold of 70 and a commission calendar. **Every one is either QUOTED, lifted
out of a claim's own sentence by regex in `compute.py`, or declared in `aggregates.json` with the
claim ids it was computed from and re-derived by the gate.** Eight computed figures are declared.
Eleven numerals reach a claim the frame citing them carries.

The stationing interval on frame 5 is the one figure the plan asked for and the frame does not
print. No claim it cites carries that digit anywhere in its quote, its text, its title or its url,
so a reader following the cite would arrive at a page without the number. The ticks carry the
rhythm and the frame prints no numeral at all.
