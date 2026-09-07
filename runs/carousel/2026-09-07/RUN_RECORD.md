# RUN RECORD — 2026-09-07 — carousel no. 17

Branch `claude/daily-2026-09-07`. Today is the America/Chicago date. There was no run on
2026-09-06, so parts of the record came in two days stale rather than one.

## The record

The selector named **14 items**, no deferrals and nothing rotten. `reverify.py --apply` stamped
**8** of them and handed back **6** it could not settle. All six were fetched by hand and all six
are resolved. **The worklist was cleared in full** and the selector now reports 0 due.

**Project 58482 moved, and it is the largest single change to the record in weeks.** The comment
window on the proposed Large Load Demand Management Service rule shut on September 4th, 2026 and
the filing index went from 37 filings to 64. Almost all of it landed on the deadline day itself.
Oncor, AEP Texas, CenterPoint Energy Houston Electric and Texas New Mexico Power all filed. So did
ERCOT, NRG, Vistra, ENGIE and the Lower Colorado River Authority. The Sierra Club filed, the Data
Center Coalition filed, and Google filed under its own name. A supplemental public comment was
entered on September 6th, two days after the deadline, so the index is still accepting filings
with no dated way in left. The item's room moves from `open_comment` to `contact_only` and six
claims were added.

**Carson County's abatement now rests on a primary source and the record now says two documents
disagree.** Fermi Inc's Form 10-Q of August 14th, 2026 states the county approved a 10-year
property tax abatement and established a reinvestment zone for Project Matador. The Amarillo
station reported an agreement covering 15 phases that could extend for up to 25 years. Those are
not the same length, neither document reconciles them, and the county's own signed agreement is
not published. The record now carries both and says they differ.

**Four items were admitted**, every one naming its counties or statewide and every one citing a
primary source.

| id | what |
|---|---|
| tx-2026-0125 | Frontera's queues close permanently on October 1st, 2026, and Horizon is still internal only |
| tx-2026-0126 | Senate Water, Agriculture and Rural Affairs heard the data center water charge on September 1st |
| tx-2026-0127 | The Supreme Court of Texas hears argument October 6th on an AI-assisted deposition transcript |
| tx-2026-0128 | Brownsville takes up a temporary moratorium on data centers |

**Held rather than admitted.** Project Watershed 250, the Governor's water utility cybersecurity
pilot announced August 31st. The Governor's own release never uses the words artificial
intelligence, and the AI in it is the participating vendors' description of themselves. That is a
journalism-sourced AI claim about a primary-sourced non-AI announcement, and the admission bar
says hold it.

**The backlog did not grow.** It stands at the same three grandfathered items it held at wake,
tx-2026-0001, tx-2026-0002 and tx-2026-0007. None can be cleared honestly: each is a rule or a
queue that applies across the ERCOT region, which is not the state, so `statewide: true` would be
a claim about scope that no source supports.

## THE CRAWL BOUNDARY MOVED UNDER THIS RECORD, and three publishers it cites now exclude it

Checked per host this run, as the rule requires, and all three are new findings appended to
`knowledge/shared/SOURCES_FIELD_LOG.md`:

- **`seguingazette.com`** disallows `ClaudeBot`, `Claude-Web` and `anthropic-ai` by name.
- **`newschannel10.com`** disallows the same three by name.
- **`tacc.utexas.edu` and `lccf.tacc.utexas.edu`** disallow `ClaudeBot`, `ClaudeBot/1.0` and
  `anthropic-ai` by name. **`docs.tacc.utexas.edu` serves no robots.txt at all**, and it is the
  compliant path to the same organisation's own documentation. Every fact in today's deck comes
  from that subdomain or from `api.nsf.gov`.

Nothing was fetched from any disallowed host. Two pages that had already been retrieved before
their robots files were read were **deleted unread**. Eight claims across two items now stand
unconfirmed as a result, and the record says so on the items rather than quietly keeping the
stamps. For Guadalupe County the San Antonio station carries the sheriff's words in its own text,
so three claims were re-sourced there and they do not differ.

`dhs.gov` returned 403 to a direct request and served the same page through a different reader.
Its own robots.txt is also 403, so no disallow is established and the 403 is an edge failure
rather than a policy. All twelve claims on tx-2026-0120 stand.

## Discoverability signoff

- **One decision's card, opened as an image.** `og/tx-2026-0125.png`, opened three times. The
  first title was 139 characters and the card cut it at "closes its...", which wraps on a whole
  word and reads correctly but loses the date, which is the entire news. A second title lost the
  day at "on October...". The title is now "Frontera's queues close permanently on October 1st,
  2026" and the card carries the whole headline with no ellipsis. Three lines, no stump, date
  intact.
- **`/questions/`, read as a reader.** Twelve kinds, all with real answers behind them. The
  "Where a comment window is open" card reads `06`, which is `{:02d}` padding. **This was
  investigated and it is house style, not a defect**, and the change made to remove it was
  reverted. The front page counter row pads the same way at `editorial.py:1377` and the routine's
  own text about that row assumes a two-digit face. One observation stands for the upgrade lane:
  the questions hub registers its figures with the numeral gate UNPADDED at `feeds.py:301` while
  rendering them PADDED at line 308, where the front page registers both forms. Nothing is wrong
  on the page today and the mismatch is latent.
- **The `Open right now` section of `llms.txt`.** Five entries, and **Project 58482 is correctly
  gone from it.** Its window shut on September 4th, and the room was changed in Phase 3 before
  Phase 16 built the site, so the merge order is right. This is the exact cross-check the phase
  asks for and it is the first run where it had something to catch.
- **`/sources/`, the record's own report card.** The primary share is **528 of 609 claims across
  203 documents from 91 publishers**, against 500 of 578 across 196 from 87 at wake. It moved up.
  Four items were admitted on primary sources and one journalism-only item gained a primary
  source, which is what moved it. The top publisher is `interchange.puc.texas.gov` at 93 claims,
  which is the commission's own filing index and is a primary source, so the head of the list is
  not resting on a report about a document. The quoted-material exemption is still doing its job
  and is not hiding any of this record's own sentences.
- **`/topic/`, counting a card against its own page.** The research and science beat page lists 20
  decisions and its hub card says 20. The per-beat "still open to comment" figures are 1, 1, 1 and
  1 and they **sum to 4**, which is exactly what the front page's "Doors open to you" counter
  prints and exactly what the ledger holds. Before today it would have been 5. That agreement is
  produced by Phase 3 closing 58482, not by luck.
- **`/place/`.** Travis County took tx-2026-0125 and tx-2026-0126 today and both appear on the
  county page and in the Austin-Round Rock-San Marcos metro. Cameron County took tx-2026-0128 and
  appears under Brownsville-Harlingen. Montgomery County took tx-2026-0127. All are on the hub
  with counts matching the pages behind them.

## Instruments

All ten checks exit 0. Grid watch page check, water watch page check, the water page self-test,
`media_check`, `schema_check`, and the self-tests for `og`, `favicon`, `truetype`, `indexnow`, and
`seo_check`. **No instrument has stopped and no page is reading wrong.** Nothing was changed in
`gridwatch_page.py` or `waterwatch_page.py`, and nothing needed to be.

**The scanner's daily ceiling was NOT checked.** No Supabase connector is attached to this
session, so the query could not be run at all. This is the state the phase says to name and carry
on from, and it is worth a maintainer's attention only if it repeats.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 21 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 5 warn(s) |
| aggregates     | PASS   | 6 declaration(s), 7 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 7.12 MB, vector |
| score          | ABSENT | score.json not written yet |
| labels         | ABSENT | label_report.json not written yet. Run scripts/carousel/label_guard.py <run-dir> |
| quantifiers    | ABSENT | quantifier_report.json not written yet. Run scripts/carousel/quantifier_check.py <run-dir> |
| verbatim       | PASS   | 10 declared fragment(s) over 8 of 9 dossier(s), every one a literal substring of its own claim's quote |
| dossiers       | PASS   | 42,451 chars planned |
| caption        | PASS   | 153 words |
| craft floor    | WARN   | 9 frame(s), median 791, floor 142, 1 quiet |
| plan vs render | PASS   | 9 of 56 acceptance item(s) checkable |
| texan          | WARN   | places NONE / body NO / deadline yes / next step yes |
| absences       | PASS   | 6 of 6 scoped to a named document |
| numerals       | PASS   | 13 numeral(s) over 9 frame(s), every one reachable |
| completion     | ABSENT | not scored yet |
<!-- gate-status:end -->

## The deck — carousel no. 17

**The story.** The Texas Advanced Computing Center closes the queues on Frontera permanently on
October 1st, 2026. Its own user guide, last updated September 3rd, 2026, still calls Frontera the
largest cluster dedicated to open science in the United States. The guide for Horizon, the machine
the same center is building under the Leadership Class Computing Facility construction award, says
of itself "This user guide is in progress" and carries a notice dated 07/24/2026 saying it is
"still limited only to internal users".

**Why this story.** It is a THING SOMEBODY DID with a date on it, which four consecutive run
records asked for in capitals and did not get. It has a deadline a reader can act before, which is
the one thing this record publishes that a person can use. And it is an application beat rather
than a filing, which the beat table says the run drifts away from when left alone. `dedupe_check`
returned nothing at the repeat threshold, with the loudest entry at 0.35 sharing only generic
words with the NSF robot centre deck of August 29th.

**Sources, and the boundary.** Everything rests on `docs.tacc.utexas.edu` and `api.nsf.gov`.
`tacc.utexas.edu` and `lccf.tacc.utexas.edu` both disallow this project by name and **nothing was
fetched from either**. The documentation subdomain serves no robots.txt at all and carries the
same organisation's own user guides, which is the useful half of that finding and is now in the
field log.

## The directors room, and what was taken from where

Three treatments came back and all three were buildable.

- **The spine is TWO MANUALS, ONE FINISHED AND ONE UNFINISHED**, because it is the truest reading
  of a record where everything is carried by two documents in different states of repair.
- **From the queue room, the light.** A plane source UNDER the raised floor, up through 25 percent
  open perforated tile, so every vertical surface is brightest at its foot and every cast runs UP.
  Nothing in sixteen decks lights this way, and it is what gives a two-documents deck a real value
  structure instead of nine frames of aqua on black, which is the risk that room named against
  itself. Also its law that there is no vanishing point anywhere.
- **From the machine room, the attribution discipline** (a colour means one thing and each frame's
  own script counts it) **and its warning** that nine grey close-ups collapse into one picture,
  answered with nine camera classes and a cap of two frames on the cavity idiom.

The load-bearing law is **a document is lit exactly as far as it is written**. The two guides are
drawn from one construction and differ only in EXTENT, never in colour, so the unfinished one is
never warned about, it is simply less lit. That is the grid watch's bar law applied to a document
and it is what keeps a severity verdict out of the deck.

## What the ledger asked for, and whether it was paid

| debt, from deck 16's avoid_next and earlier | paid |
|---|---|
| a close that gives a reader a door, after three decks ended on an absence | yes. Frame 9 carries a date, a named route and a reachable address |
| a spine that is a thing somebody did | yes. The cover opens on the act, dated |
| spend the invention on 7, 8 and 9 | partly. 7 and 8 are clearly two of the three most drawn. The craft judge put frame 4 above frame 9 on drawn elements |
| the type moves on at least three frames, planned not repaired | yes, six of nine, planned in the storyboard |
| the one value inversion is not at slide 5 for a sixth deck running | yes, it is at frame 3 |
| at least one MEASURED acceptance item per frame at plan time | yes. 9 of 56 items are machine checkable and every one holds. Every frame also carries probes that THROW rather than report |
| an absence boundary that survives 432 pixels | yes. Frame 4's cavities are 104 by 124 design px, which is about 42 px at feed size |

## What the value arc cost, and it is the run's main craft finding

`panel_ready` measured the first build at a **deck median L\* of 4.1 against a plan of 20**. That
is not a deck that came out a little dark, it is nine near-black rectangles, and it is the same
failure deck 15's first render had at 6.3 against a plan of 24.

**The frames were REDRAWN, not the plan rewritten.** The plane source kept its shape and its
direction and gained the amplitude it always needed, which moved the deck to 10.4.

**Then the plan was corrected for the residue, and that half is worth stating plainly.** What held
the deck under its original 20 was the SCRIMS the rubric's own 4.5 contrast floor required under
six frames' type. A scrim is the engine's own prescribed remedy for type over art and it
necessarily darkens the frame it saves. So the arc in the storyboard is now the frame that exists.
**The next deck in a dark register should plan its type reserves at storyboard time and set its
arc from what is left**, rather than planning an arc and discovering the reserves afterwards.

## Three of this run's own probes were wrong, and none of them was the drawing

Every acceptance item on this deck is a probe that throws inside the frame rather than a sentence
a critic reads. Three fired, and all three were faults in the measurement:

- **Slide 4** sampled a cavity at x 1052, which sits mostly off the right edge, so `getImageData`
  clamped it to a sliver and the lip and the floor measured the same thing. The threshold did not
  move.
- **Slide 6's bloom test was ABSOLUTE**, at L\* 20, which only measured bleed while the ground
  happened to be near black. On a correctly lit frame it fires on the ground. It now compares the
  strip beside the light line against the ground far from it, which is what it always meant.
- **Slide 5 took the MAX pixel** above its boundary, so once every punched hole gained the lit
  lower lip structural law 4 requires, the probe fired on the law being kept. It now measures the
  region's median and the share above L\* 40, which is what "the empty rail is not a lit mass"
  meant.

A probe that can only be satisfied by drawing less is not a test of the drawing.
