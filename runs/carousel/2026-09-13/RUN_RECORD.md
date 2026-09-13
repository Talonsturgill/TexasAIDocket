# Run record, September 13th, 2026

Carousel no. 22. Branch `claude/daily-2026-09-13`.

## The record

**The worklist was cleared in full.** `docket_staleness` named 115 items due of 127 on the two
day leash, with nothing rotten. `reverify.py --apply` confirmed 79 of them unchanged against
their own quotes and stamped them. The remaining 48 were checked by hand, one primary source
each, and every one of them carries its own dated movement line.

**No claim moved this run.** The report carried no `missing` findings at all, which is to say
every quote the record holds was still on the page it came from wherever the page could be read.
What it did carry was 27 claims behind sources that would not answer and 53 behind sources the
string check structurally can't read, which is PDFs, Legistar's JSON API and JavaScript rendered
agenda centers. Those 48 items are the ones taken by hand.

**One item was left unstamped, deliberately.** `tx-2026-0120`, the Homeland Security facial
biometric assessment at the Progreso International Bridge, rests on a single page at `dhs.gov`
that returned 403 to the checker, to a browser user agent and to the fetch tool alike. Its
movement line says what is therefore unconfirmed rather than what the fetcher did, and its
previous stamp stands.

**Three items were admitted.**

| id | what it is |
|---|---|
| `tx-2026-0147` | an AJR expert panel review, with radiologists at Texas Children's and UT Southwestern among its authors, stating that pediatric imaging is substantially underrepresented across AI in radiology |
| `tx-2026-0148` | an MD Anderson and UT Medical Branch MRI radiomics model whose discrimination fell on an outside cohort |
| `tx-2026-0149` | ERCOT's market notice telling providers which large loads sit provisionally in Batch Zero, every placement conditional |

**Three were held in the seed, all for the same reason.** Kodiak AI's Permian driverless
deployment, Galaxy Digital's Batch Zero classifications and the Texas A&M AgriLife far
ultraviolet poultry trial. None of the three in window sources names a Texas county, and
Kodiak's own earlier release puts the load-out sites in two states. A statewide flag used to
mean nobody could tell is a claim about scope that nobody checked, so each is held with its
reason and a later run that finds the place can promote it.

**The backlog is empty and was empty at wake.** `site_build` printed no `backlog:` lines, so
there is no item on no county page and no reader copy pointing at an item the record does not
carry.

**The primary share.** `/sources/` reports 635 of 717 claims resting on a primary document,
across 226 documents from 101 publishers. All three admissions this run cite primary documents
only, so the share was not moved down by them.

## Discoverability signoff

- **One decision's card, opened as an image.** `docs/og/tx-2026-0147.png`. The headline wraps
  across four lines and truncates on a whole word with an ellipsis, "Texas Children's and UT
  Southwestern radiologists publish that imaging AI has...". No stump, no mid word break. The
  title is long enough that the card loses the verb, which is a note for the next run rather
  than a defect in the wrapper.
- **`/questions/`, read as a reader.** Twelve questions, each one a reader would type. "Where a
  comment window is open" answers 05, and the per beat figures on `/topic/` sum to the same
  five, so the two surfaces agree.
- **The `Open right now` section of `llms.txt`.** Eight decisions listed, and each one was
  cross checked against Phase 3. The two windows that closed, the NRC reactor licensing notice
  on August 31st and the time use survey on September 8th, are both correctly absent. Project
  59550, whose comment deadline is September 17th, is present and matches the commission's own
  calendar feed read this run.
- **`/sources/`, the record's own report card.** The share is above. The top publisher is the
  PUCT Interchange at 97 claims over 20 documents, and its page reads as documents, orders and
  filing indexes rather than as reporting. The quoted material exemption is still doing its
  own job and is not hiding any of this project's own sentences.
- **`/topic/`, one card against its own page.** Eight beats, 29 plus 6 plus 16 plus 15 plus 14
  plus 23 plus 17 plus 10, which is the 130 the front page counter prints.
- **`/place/`, for the places this run landed something in.** Harris County carries 12 items,
  Galveston County 4 and Dallas County 4, each on the hub, which names 63 of the 254 counties.

## The instruments

Every check green by exit code. `gridwatch_pagecheck` 0, `waterwatch_pagecheck` 0,
`waterwatch_page --self-test` 0, `media_check` 0, `schema_check` 0, `og --self-test` 0,
`favicon --self-test` 0, `truetype --self-test` 0, `indexnow --self-test` 0, `seo_check` 0.

The water map draws 119 pins and the readout says 119 reservoirs, so the drawing is not a lake
short of its own figures.

**The scanner's daily ceiling could not be read this run.** The Supabase connector is installed
and authenticated for the organisation and its tools are not enabled in this session, so the
query against `scanner.scans` had nowhere to run. Nothing about the cap is therefore known
today, which is the one thing on that check worth saying out loud.

## THE DECK SHIPPED AT 6.784, WHICH IS 0.016 UNDER THE BAR

Carousel no. 22, nine frames, on what a model fitted to one population does when it meets
another. Two papers, both dated September 9th, both with Texas radiology departments among
their authors. The panel review says imaging AI has largely skipped children and names off
label use of adult trained models as a concern. The second paper puts a number on the same
move and watches its own discrimination fall.

**The panel did not clear the bar and nothing is being papered over.** Five rounds, fifteen
judge reports, and the trajectory was 6.26, 6.46, 6.578, 6.638, 6.784. `max_rounds` is 5 and
this run did 5, so past the cap a deck with no hard fail outstanding ships at whatever it
scored with the number said out loud. **No judge found a hard fail in round 5.** Two judges
refused on the threshold rather than on a fault, at 6.65 and 6.542, and both dissents are
carried in the per criterion median rather than averaged away. The precedent is carousel
no. 14, which shipped at 6.762 at the same cap.

`panel.py`'s own round counter reads 6 and the honest figure is 5. The combiner was re-run
once against a stale integrity card while round 4's bookkeeping was being corrected, and that
invocation was not a scoring round. `score.json` carries both the corrected number and the
note, because a counter quietly left one high is exactly the kind of thing the next run
inherits and believes.

### Three integrity hard fails were found by the panel and all three were real

Each one was a sentence this deck could not support, and each was fixed at the source rather
than reworded around the judge.

- **Round 2, frame 4.** Claim c26's quote had been cut three clauses early and its text
  enumerated two radiology departments where the uncut affiliation field names three, on a
  paper with eight institutions. The frame printed that partial list as though it were the
  whole. Verified against the saved PubMed XML, then fixed by carrying the entire 867
  character affiliation field as the quote, rewriting the text so it does not enumerate, and
  changing the frame's kicker to "Texas departments among its authors".
- **Round 2, frame 7.** The frame asserted an absence about two papers when what this run
  actually fetched was two PubMed abstract records. Fixed by putting the real scope on the
  frame, "Neither record", and restating the absences entry to match. `quantifiers.json` now
  declares the two URL set that phrase ranges over, which is the honest fix rather than
  rewording until `quantifier_check` stops firing.
- **Round 4, frame 9.** The frame said the federal device list "says nothing about children"
  while this run's own absences entry recorded two occurrences of "pediatric" on that page.
  Fixed by putting the scope on the frame. It now says the word appears in two device names
  and nowhere in the list's own text, which is what `fda_words.py` measured.

### What the frames are, and the value arc that did not survive

| # | archetype | planned median L\* | measured |
|---|---|---|---|
| 1 | FIGURE_SCALE, a child and an adult at the bore of a scanner drawn in metres | 22 | 13.5 |
| 2 | DOCUMENT, the review's first page on the table pad, four words underlined | 46 | 28.8 |
| 3 | CLOSE_CROP, a child on a bed built from its own parts and painted flat | 34 | 11.6 |
| 4 | DIAGRAM, the model sealed in a taped box on a cart | 30 | 11.1 |
| 5 | GRID, 198 units above and 69 below, one unit to one patient | 26 | 18.8 |
| 6 | OBJECT_AND_CAPTION, the reading room with the study's own slices as the accent | 18 | 11.1 |
| 7 | SPLIT_HORIZON, the deck's turn, hook set dark on the lightest field | 72 | 41.1 |
| 8 | MAP, five departments on an Albers sheet, three of them leaving it | 26 | 11.1 |
| 9 | FULL_BLEED, three mirrored bays and a lit lobby through the glazing | 28 | 14.1 |

**Every frame came out darker than planned and the arc collapsed.** The plan asked for a
sequence running 22, 46, 34, 30, 26, 18, 72, 26, 28, which is a deck that breathes. What
shipped measures 11.1 to 41.1 with four frames sitting within half a point of each other at
the floor. The inversion at frame 7 survived and is still the brightest thing in the deck, at
41.1 against a planned 72, so the turn reads but at a little over half its intended lift.
This is the run's largest unrepaired finding and it is a planning fault rather than a drawing
fault. A frame's median is decided by how much of it the print screens and how much is painted
flat, and nothing in the plan states a target the render can be checked against while it is
being drawn. Measured after the fact by `measure.py`, which this run wrote.

### The five things the panel found that were NOT repaired

Written down rather than repaired, because the cap arrived first. Each is next run work.

- **Frame 4's bridge.** Three reader judges in three consecutive rounds said the frame does
  not carry the reader from the panel review into the second paper. The frame was rebuilt
  twice and the finding survived both rebuilds, which means the fault is in the sequence
  rather than in the drawing.
- **Frame 3's read.** Four judges across the five rounds could not read the frame at feed
  width. Three rebuilds, including dropping the catalogue hospital bed for one built from its
  own parts, and it still does not resolve.
- **The value arc**, above.
- **One type skeleton on seven of nine frames.** Two frames break it, frame 2 by putting the
  hook below the document and frame 7 by setting it dark on the lightest field. The other
  seven open kicker, hook, image, dek in that order.
- **The INSTRUMENT register, for the third run in a row.** `dedupe_check` structurally cannot
  see this: it compares topics, entities and artwork, and a recurring visual register is none
  of those. Recorded here because nothing in the machine will raise it.

### The caption was rewritten rather than relabelled

`ledger_check` refused the build because the caption's opening move, "the two things", was
inside its own six run exclusion window, having been used on September 9th. The fix a run
reaches for here is to relabel the move and keep the copy, which is the gate being defeated
rather than obeyed. The caption was rewritten from scratch on "the plain question", opening
"What was the scanner taught on?", and `aggregates.json` was corrected to match it.

### The record's own house style gate went red at Phase 16 and the fix was in the record

`house_style_check` named 12 sentences over the 30 word backstop, across the three items this
run admitted, two of its re-verify movement lines and one claim text on the article page. All
12 were this project's own prose rather than quoted source text. Each was split at a clause in
`ledger/docket.json` and in `claims.json`, never in `docs/`, and the site was rebuilt. It is
worth naming because the gate did not fire on the deck at all. **The record's own writing is
the surface that drifts when a run's attention is on the carousel.**

## THE RUN DID NOT MERGE, AND CI IS WHY

**No check run exists on this branch and none can be made to exist from inside this session.**
`CLAUDE.md` is explicit that zero checks is not green, so PR no. 301 is open, ready and carrying
everything, and `main` is untouched.

What was tried, in the order Phase 18 prescribes, with the result of each.

| lever | result |
|---|---|
| the pull request being opened | `guards.yml` has `total_count: 0` on this branch |
| a push to a branch with an open pull request, which Phase 18 says fires `pull_request: synchronize` | two pushes landed after the PR opened, `0de1893` and the upgrade lane's `b57cac3`. Neither started a run |
| `workflow_dispatch`, which `guards.yml` declares | `403 Resource not accessible by integration` |

**This is not the 2026-08-27 mistake of writing a confident account while the state was one push
away.** That push was made, twice, and the PR's own head moved to match. GitHub updated the pull
request and started nothing.

**It is also not a repo fault, and the evidence is yesterday.** Run 1104 of `guards.yml` was an
`event: pull_request` run on `claude/daily-2026-09-12`, for the identical routine, with
`Talonsturgill` as its triggering actor. The mechanism works here. What changed is the
credentials this session's GitHub access uses, which no file in this repository can set. It is
the same shape as the 2026-08-30 finding about `bypassPermissions`, and it has the same answer.
**The remaining lever is the environment's own configuration, outside the repo.**

So the email leads with this, its image URLs point at the run branch rather than `main`, and the
one action that clears it is a maintainer merging PR no. 301 once they have seen a green run, or
granting this session's token the right to dispatch `guards.yml`.

## A REVIEW BOT READ THE BRANCH AND FOUND SIX THINGS, AND FIVE OF THEM WERE REAL

Codex reviewed `96b699a` while this run was in Phase 17. Every finding was checked against the
repository rather than taken at its word, which is how one of them came apart.

- **The shipped run carried no `gmail_payload.json`.** CONFIRMED by running it.
  `email_check.py --all` exits 1 naming this run, and that step is in `guards.yml`. **This is
  the carousel no. 7 incident exactly**, which `CLAUDE.md` already carries in full, and the
  reason it recurred is that Phase 19 builds the payload AFTER Phase 18's merge while CI reads
  it across every shipped run. The payload is now built and committed inside this run's own
  commit range.
- **`fda_words.py` could not run from a fresh checkout.** CONFIRMED. The committed script read
  `tmp/fda_ai_devices.html`, which lives under `out/` and is gitignored, so it raised
  `FileNotFoundError` on the one measurement frame 9 and two of this run's absences rest on. It
  now writes `fda_words.json` beside itself, that file is committed, and the script falls back
  to it and says which bytes the figures came from. The measurement is unchanged and it stands.
  Child, children and adult appear zero times on that page, and pediatric twice, both inside
  device names.
- **The record said the model "lost accuracy" and the authors did not say that.** CONFIRMED and
  it is the worst of the six. The Harrell C-index measures discrimination rather than accuracy,
  the paper's own intervals overlap, no test of a decline is reported, and the item's history
  note went further and attributed the claim to the authors, who wrote "limited standalone
  discrimination". The title, the summary and the note are restated to say the score was lower
  on the cohort the model was not built on, with the overlap and the absent test named. **The
  carousel ledger had it right the whole time**, which is what makes this a record defect rather
  than a run-wide one.
- **Two acceptance items printed an L\* threshold this run never measured.** CONFIRMED.
  `shipped_check.g_measured` returned two fatal findings, so CI would have been red on this
  independently of the email. `measure.py` now measures both against the shipped PNGs at full
  resolution. Frame 9's lit entrance is the brightest region in the frame at 96.3 against 11.6
  beside it, a lift of 84.8 against a threshold of 25, and it is found by luminance rather than
  by being handed the entrance's rectangle. **Frame 7's item is NOT met and is recorded as
  failing.** Its two named rows differ by 19.1 where the item asks for more than 40, because
  they sit inside the step rather than either side of it. The edge they were written to test
  runs 78.0 L\* across 6 CSS pixels, which is under three pixels at feed width, so the drawing
  does what the item intended and the item asks the wrong two rows. That is a sixth unrepaired
  finding and next run work.
- **The topic ledger's own provenance note was false twice.** CONFIRMED. It said the record
  names no county for either item, and the record files the review under Harris and Dallas and
  the second paper under Harris and Galveston, which this run's own discoverability signoff had
  already counted. It also read as though three out of state institutions were in the `entities`
  array when they are deliberately not. Both corrected, with the reason the three are left out
  now stated, because this entry is durable memory a later run reads.
- **The sixth was wrong.** It said the acceptance literal `"Limited standalone discrimination."`
  mismatches the rendered lowercase string and that `shipped_check.g_plan_render` reports it as
  fatal. `g_plan_render` was run directly against this run and returns an empty list.

## THE UPGRADE LANE, AND THE GATE THAT NOW FAILS THIS DECK

Two upgrades shipped on `b57cac3`, stamped `upgrade`.

**`panel_ready.py` now reads a value arc declared frame by frame.** The finding underneath it is
sharper than this run's own: the arc did not merely collapse, **a gate built for exactly this
collapse printed a pass.** Carousel 22 declared its plan nine times inside each frame's
`art.value_structure` and wrote no summary paragraph, `arc_spans` found nothing, and the gate
reported that the storyboard declares no arc it can read. Measured across all 22 shipped
storyboards, this is the only one since 2026-08-29 whose arc the gate could not see, because
every earlier deck happened to carry a summary span as well.

**So the gate now goes red on this very deck**, at a measured 13.5 against its own planned 28, a
miss of 14.5. That is the correct outcome and it is left standing. `guards.yml` does not run
`panel_ready` against shipped runs, so it does not change the merge question, and the number is
the same one the value arc table above already reports.

**`panel.py` counts a round by the content of the three judge cards** rather than by the length
of its own log, which is what let this run's counter read 6 where five panels had sat.

Four things were written into `knowledge/carousel/UPGRADE_BACKLOG.md` as proposals rather than
built, each because the file that would carry it is outside the `upgrade` lane. The one worth
naming here is that **ten carousel gates have a `--self-test` that CI never runs**, measured
rather than guessed, and `panel_ready` is one of them, so the first upgrade above is proved
locally and by nothing else.

## Did this run stop and wait for a human

`prompt_audit.py` measured **1678 tool calls and none of them waited on a human.** Exit 0, with
a debug log present, so this is a measurement rather than an absence of one.

**This reading is interim and everything after it can still prompt.** The upgrade worker runs
after this line, files are committed and pushed, the pull request is checked and merged, and
the Gmail connector is called. Phase 19 takes the reading that counts, immediately before the
email is built, and that is the figure the email carries.


## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 27 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 6 warn(s) |
| aggregates     | PASS   | 6 declaration(s), 7 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 9.95 MB, vector |
| score          | FAIL   | 6.784, below threshold |
| labels         | PASS   | 28 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 88 published string(s) read from one list, every universal names its set |
| verbatim       | PASS   | 11 declared fragment(s) over 9 of 9 dossier(s), every one a literal substring of its own claim's quote, 1 slot note(s) |
| dossiers       | PASS   | 44,407 chars planned |
| caption        | PASS   | 135 words |
| craft floor    | PASS   | 9 frame(s), median 2335, floor 420 |
| plan vs render | WARN   | 9 of 82 acceptance item(s) checkable |
| texan          | WARN   | places Dallas, Houston / body NO / deadline yes / next step NO |
| absences       | PASS   | 9 of 9 scoped to a named document |
| numerals       | PASS   | 18 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
