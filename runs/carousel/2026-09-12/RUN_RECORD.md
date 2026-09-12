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
