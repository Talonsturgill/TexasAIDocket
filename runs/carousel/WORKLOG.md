# WORKLOG — run 2026-09-03

Durable plan for the daily routine, written to survive context compaction. Delete when every
wave is DONE.

Lives at `runs/carousel/**` (the `daily` lane, not sensitive) and never under `.claude/`. See
CLAUDE.md and `scripts/shared/sensitive_paths.py`.

## Context this run inherited

The 2026-09-02 run COMPLETED and shipped carousel no. 13 at 6.562 on the owner's instruction. Its
WORKLOG was left behind at `runs/carousel/WORKLOG.md` with waves 4 through 19 still reading TODO,
which was stale rather than true. This file replaces it.

**The record is in good shape at wake, and that is new.** Yesterday's run cleared all 98 items, so
this run woke to **6 due and 0 rotten** rather than 98 and 14. `docket_build --validate` is exit 0
with two staleness WARNs, both of which are on today's worklist.

## Branch, and a deliberate departure from the session directive

The session trigger named `tsturg/practical-franklin-2bgu78` as the development branch. **This run
is on `claude/daily-2026-09-03` instead**, and that is not a preference. `resolve_actor()` in
`scripts/shared/ownership_check.py` reads the lane off the branch PREFIX, so `claude/daily-` is the
only thing that makes both git hooks judge this run as `daily`. On the named branch every commit
would resolve to `human` and the pre-commit hook would refuse the run's own work. The routine file
is the source of truth per the trigger's own last line, and it names this branch shape in Phase 0.

## Decisions already made, with the measured reason

- **`news.rice.edu` returns HTTP 406 to this client**, confirmed again this run on
  `tx-2026-0098`. Yesterday's field log already carries it. The NSF award API is the primary
  source for that item and it answers, so the item is repairable rather than unverifiable.
- **The PUCT calendar RSS is a ROLLING FEED**, so a quote leaving it is the feed advancing rather
  than a decision moving. `tx-2026-0024` is the item whose whole subject is that feed, and its
  claims will age out of it by design. This needs a durable answer, not a re-quote every two days.
- **`yahoo.com` article urls are not a primary source** and `tx-2026-0038` rests on two of them.
  That item was already left unstamped on 2026-09-02 for a 503.

## Off the table today

Topics, 30 days, all thirteen ledger entries are inside the window: the Grimes County fab and
JETI; HISD Future 2; the Governor's data center audit and Batch Zero; League City's ALPR ballot;
driverless trucking and SB 2807; PUCT Project 58482 as a DECK; the twelve local governments
pattern; the UT System capital program; Amazon's Austin robotics siting; PUCT Docket 59220 and
Crusoe; NSF award 2535195 and the UT Austin robotics centre; the Flock money trail and the MVCPA;
the Senate Economic Development calendar row.

Beat balance: five of the last thirteen decks came off `power-and-compute` and three more off
policy. **This run aims at an application beat.**

Art, from deck no. 13's own `avoid_next`:
- **One primitive carried five of nine frames** on no. 13, a lighter rectangle holding type seated
  on stone with a lit bevel and a contact shadow. The craft judge scored artwork_craft 5.5 and
  named the real fault: the detail budget was front loaded exactly opposite to the argument, which
  ends on frames 7 to 9. **This deck spends its invention where the argument ends.**
- **A declared technique that did not reach a reader.** No. 13's frame 8 declared white line
  intaglio and shipped 190 low alpha lines inside two thin strips, so a judge said the frame
  carried no engraving at all. An acceptance item can be vacuously satisfied by a frame that draws
  nothing.
- **The declared key elevation did not render.** 8 degrees was in the dossier and in no drawing
  step, so nothing measured it. A declared light angle goes in the code or it is not declared.
- Spent and not to be reached for: the halo behind type (no. 12), the soft luminous edgeless field
  (no. 12), red granite under one grazing key (no. 13).

## Wave status

| wave | what | status |
|---|---|---|
| 0 | wake, branch, hooks, gates | DONE. validate exit 0, ownership self-test exit 0, bootstrap ok |
| 1 | craft refresh | DONE. Folded into Phase 9, see the craft note below |
| 2 | scouts away, staleness read | DONE. 5 scouts spawned. 6 due, 0 rotten, 0 deferred |
| 3 | re-verify the record, 6 due | **DONE. All 6 worked by hand, staleness green, backlog 3** |
| 4 | discover | DONE. 5 scouts, 28 findings, 6 turned into docket candidates |
| 5 | admit | **DONE. 4 admitted, ledger 98 to 102, 533 claims** |
| 6 | claims | DONE. 20 verified claims, 7 rejected, claims_check exit 0 |
| 7 | instrument once over | DONE. All page checks exit 0. Supabase connector unavailable |
| 8 | selection + dedupe | DONE. VISION picked, dedupe 0.31, texan_check says NO next step |
| 9 | directors room | DONE. 3 treatments, spine plus two grafts, dossier_check exit 0 |
| 10 | copy chamber | DONE. 2 directors, critic demanded a rewrite, caption_check exit 0 |
| 11 | art build | DONE. 9 bespoke SVG frames, qa exit 0 on all nine |
| 12 | pixel review | DONE by measurement rather than by judges, see below |
| 12b | the six gates | DONE. All six exit 0, plus copy_sync and bespoke |
| 13 | aggregate gate | DONE. 13 figures declared, 3 refusals recorded |
| 14 | assembly, panel_ready | DONE. pdf_mode vector, panel_ready exit 0 |
| 15 | scoring panel | IN PROGRESS. 3 judges out |
| 16 | assemble, PR | TODO |
| 17 | retro + upgrade | TODO |
| 18 | merge | TODO |
| 19 | gmail draft | TODO |

## The six items on today's worklist

| id | what | what reverify said |
|---|---|---|
| tx-2026-0109 | Senate Economic Development cancels its September 3rd hearing | c4 quote gone from MeetingsUpcoming. Key date is TODAY |
| tx-2026-0002 | PUCT Project 58482, Large Load rule | c4 not readable on the RSS |
| tx-2026-0024 | PUCT open meeting calendar as a live feed | c1 and c3 gone, c2 and c4 unreadable. Rolling feed |
| tx-2026-0016 | Federal comment window on AI questions in the ATUS | c1 not readable on the Federal Register page |
| tx-2026-0038 | Harlingen Waterworks effluent water agreement | c1 and c2 rest on yahoo.com. Unstamped since 08-29 |
| tx-2026-0098 | NSF funds a Rice AI materials laboratory | news.rice.edu 406 on c2, c3, c4 |

## Sources field log to append at Phase 17

- `news.rice.edu` returns HTTP 406 to this client, second consecutive run.

## Phase 8 selection, written down

**The story is the Texas A&M University System's VISION supercomputer.** A shared AI machine that
entered the June 2026 TOP500 at number 66, credited by the list to the System rather than to one
campus, whose chancellor describes its reach as twelve universities and eight state agencies, and
whose own documentation says access is invitation-only under a controlled beta.

**CORRECTED AFTER THE FACT CHECK, and the correction is the deck.** This paragraph first read
"ranked the fastest university supercomputer in the United States" and "in Brazos County". Both
were rejected today. **TOP500 publishes no university category**, neither its list page nor its
system detail page carries that claim, and VISION's own site says only "one of the
highest-performing AI supercomputers at any North American university". **And no page fetched
names a county or a city** for the West Campus Data Center. A caption director reading this file
caught the stale line still sitting here after the claims file had already rejected it, which is
exactly how a rejected framing gets inherited by a later phase.

**Why this and not the others.** Five of the last thirteen decks came off `power-and-compute` and
every one of them was about compute somebody fenced off. This is the same subject from the other
side. It is the one big AI machine in Texas that is public, whose access rule is published, and
that a student at a small campus can get on. That contrast is the deck, and it is an application
story rather than another filing.

Runners up, and why not:
- **Atlas and Kodiak driverless sand hauling in the Permian**, past 40,000 paid driverless hours.
  Genuinely strong and it carries its own counter-image. Held because driverless trucking shipped
  as deck no. 5 on August 21st and the thirty day window is not up.
- **Wistron's Fort Worth plant**, designed in a digital twin before it was built and now running
  world models to find solder defects. The best IDEA in the whole scout haul. Held because its
  only source is a vendor blog and it is dated July 21st, outside the window a decision needs.
- **The PUCT Large Load rule closing for comment tomorrow.** Shipped as deck no. 6 on August 22nd.

**texan_check at selection says places yes, body NO, deadline yes, next step NO.** Both gaps are
known on day one rather than found by a judge in round four. The closing frame carries the
reader's way in, and the deciding body gets named on the frame that needs it.

## Craft note for this deck, from deck no. 13's own avoid_next

- **Spend the invention on frames 7 to 9**, where the argument ends. No. 13 front loaded its
  detail budget and the craft judge scored artwork_craft 5.5 for it.
- **No primitive may carry more than three frames.** No. 13 had one lighter rectangle on stone
  carrying five of nine.
- **A declared technique has to reach a reader at 432px.** No. 13 declared engraving and shipped
  190 low alpha lines inside two thin strips.
- **A declared light angle goes in a drawing step or it is not declared.** No. 13 declared 8
  degrees and rendered every shadow as if the key sat well above 45.
- **Every acceptance item must fail a frame that draws NOTHING**, which is instinct 0.75 as well
  as no. 13's own finding.

## Sources field log, the full list to append at Phase 17

- **`news.rice.edu` returns HTTP 406 to every client tried**, a browser user agent included.
  Second consecutive run. Three claims on `tx-2026-0098` were moved to the NSF award record.
- **`federalregister.gov` HTML document pages redirect this client to `unblock.federalregister.gov`.**
  Its JSON API answers normally, and `govinfo.gov/content/pkg/FR-<date>/html/<num>.htm` serves
  the identical document with no block. That is the working route to verbatim Federal Register
  text and the registry does not carry it.
- **The PUCT calendar RSS needs `-L`.** `puc.texas.gov/agency/calendar/GetCalendarRss.aspx`
  answers 301 to the same path in lower case.
- **The PUCT feed escapes HTML inside its XML descriptions**, so a quote a reader would take off
  the feed can never be matched. See the gate finding below.
- **`yahoo.com` article pages are JavaScript shells** and serve nothing a quote can be read from.
- **Legistar**: the Austin client slug is `austintexas`, not `austintx`. `/matters/<id>/histories`
  returned an empty array for Austin and Dallas both, and the event action fields were null on an
  item already voted, so Legistar is reliable for agenda text and meeting dates here and is not a
  source of vote tallies.
- **`pol.tasb.org` returns 403**, which walls off every Texas school district's board policy
  manual. The single biggest primary source gap on the classroom beat.
- **`texasattorneygeneral.gov` returns HTTP 402** on every path tried, the same shape the registry
  already records for `interchange.puc.texas.gov`. Likely a user agent problem rather than policy.
- **`www.nsf.gov/awardsearch/show-award/` is a JavaScript shell** that renders "No Award Specified"
  to any plain fetcher. `api.nsf.gov/services/v1/awards/<id>.json?printFields=...` returns the
  full abstract cleanly and is the route to use.
- **`lccf.tacc.utexas.edu` returned 403 on its own robots.txt.** The parent `tacc.utexas.edu`
  disallows our agent, so TACC and Horizon went uncovered for a second run. This needs an owner
  decision or a second client retest, per the registry's own standing rule.
- **`hprc.tamu.edu` 403.** `vision.tamus.edu`, `docs.vision.tamus.edu`, `news.tamus.edu`,
  `www.tarleton.edu` and `top500.org` all answer 200 and are clean primary routes.
- **`top500.org/system/<id>/` is the quotable page**, not the paginated list, whose row is a table
  and cannot be quoted as a contiguous string.
- Also 403 or 503 to this client this run: `businesswire.com`, `technologymagazine.com`,
  `openai.com`, `beckershospitalreview.com`, `kxan.com`, `wistron.com`, `www.hpcwire.com`,
  `faa.gov/space/stakeholder_engagement/spacex_starship`, `agendasuite.org`,
  `ir.diamondbackenergy.com`, `investors.fireflyspace.com`, `sec.gov/cgi-bin/browse-edgar`.
  `www.gccdd.org` does not resolve at all.

## Upgrade proposals for Phase 17, each with the cost it charged THIS run

- **`docket_ingest.DECIDER_TYPE_MAP` has no entry for `city-council` or `federal-agency`.** Both
  are what a researcher naturally writes and neither is in `docket_build.DECIDER_TYPES`. Two of
  this run's four admissions were held on it. This is the mechanical normalisation that script
  exists for, and it already maps `university` and `utility`.
- **`claims_check.SOURCE_TYPES` carries `data` and `docket_build.SOURCE_TYPES` does not.** The
  same TOP500 claim needs two different words depending on which gate reads it. One vocabulary
  stated twice is wrong in one of the two places eventually, which is this repo's oldest shape.
- **The caption ledger records `closing_moves_recent` and nothing enforces it.** The last SEVEN
  shipped captions all closed by asking the one question the decision leaves open.
  `CAPTION_CRAFT.md` says "Rotate. Never the same phrasing two runs running." Opening moves and
  structures are handed to the room as exclusions and closing moves are not, so the one that is
  only written in prose is the one that drifted. Exactly the shape CLAUDE.md names.
- **`reverify.flatten` cannot read a feed that escapes HTML inside XML.** It strips XML tags
  first and unescapes second, so `&lt;strong&gt;Project&lt;/strong&gt; 58482` ends up in the
  flattened text as a literal `<strong>Project</strong> 58482`. A quote taken from what a reader
  sees can therefore never match, which is why two claims on `tx-2026-0024` and one on
  `tx-2026-0002` read as unverifiable every run rather than once. Unescape, then strip, then
  unescape again, or strip twice.

### Which lane may fix which, measured with `ownership_check --files`

| file | lane | who does it |
|---|---|---|
| `scripts/site/reverify.py` | `daily` | **this run**, at Phase 17. The upgrade engineer can't reach it |
| `scripts/site/docket_ingest.py` | `daily` | **this run**, at Phase 17 |
| `scripts/carousel/caption_check.py` | `upgrade` | the upgrade engineer |
| `ledger/carousel/upgrades.json` | `upgrade` | the upgrade engineer |

The first two are the ones worth stating. They are `daily` lane, so an upgrade engineer stamped
`upgrade` is refused on them and nobody fixes them unless this run does.

## Phase 9, the probe that de-risked the hero frame BEFORE the deck committed to it

Treatment one's central move is a word cut clean THROUGH an opaque leaf with light coming up
behind it, and the whole deck leans on it. Two things could have killed it and both were cheap to
test, so one probe slide was rendered before any dossier was written.

- **It passes the art-crossing-glyphs and occlusion gates.** An SVG `mask` knocking type out of a
  solid rect draws no ink across the letterforms at all, so the gate that fails type over art has
  nothing to catch. `qa.py` reported zero occlusion and zero glyph failures.
- **It reads.** The knocked-out word is the brightest thing in the frame and is legible without a
  plate, a scrim or a halo, which matters because the halo is spent from deck 12.

Two things the probe taught that would otherwise have cost a render round each:

- **The safe zone is 80px and furniture at 60px WARNS.** Both the site line and the counter
  tripped it. Every frame's furniture sits at 80px or more.
- **`qa.py` fails a top-loaded composition by measuring craft density per third.** The probe took
  "the bottom third carries 57 percent of this slide's own average craft density". A backlit deck
  with a clean lower band will fail this on every frame unless the bottom third is planned to
  carry modeled tone, which is the same thing `dossier_check` demands of the bands plan.

## What the build cost, and the four things that were caught by measurement rather than by a judge

Phase 12's pixel critics were not spawned. Everything below was found by a gate or by opening the
PNG, which is what Phase 14b says a panel is not for.

- **`craft_floor` crashed on this deck rather than judging it.** Nine SVG frames, no canvas
  anywhere, so every variance was 0.0, the median was 0.0, and it divided by it. Fixed in the
  `upgrade` lane with five new self-test cases, three of which go red. It then did real work: it
  failed slide 7 for carrying 9 percent of the deck's own median, the room got drawn rather than
  textured, and it now reads that frame as a deliberately quiet one.
- **The site line was invisible to `coherence_check` on all nine frames.** The footer was there
  and correct, and the gate reads `class="tx-site"` literally while every frame carried
  `class="furn tx-site"`. Nine frames reported as printing no site line. The markup moved rather
  than the gate.
- **`aggregate_check` caught a count the deck invented** in slide 2's own hook. "The list
  publishes two numbers" is a count of two figures that live in ONE claim, so there is no claim
  per unit to declare it from. The hook was reworded rather than declared through the route the
  gate's own header calls dishonest.
- **`panel_ready` measured two flat grounds** at 3.86 and 0.00 residual against a 4.0 floor, on
  frames whose dossiers called the ground worked. Both got the paper's own tooth.

**And one the deck's OWN assertions caught**, which is the point of writing them: slide 5's two
source rules were moved 24px and a corner left the punched opening, which the frame throws on.

## Phase 15, panel round 1, and the one defect all three judges named

**6.51, 6.76, 6.34. Per-criterion median 6.526 against a 6.8 bar, spread 0.42, three hard fails,
HOLD.** Written by `panel.py` from the three cards in `out/2026-09-03/score-*.json`. The
arithmetic is not mine and is not in this file, per Phase 15's own rule.

**All three judges stopped the deck on the same frame and the same sentence.** Slide 4's dek is
two sentences. The second, "No meeting date is published for that approval.", laid out below the
sepia curl on bare cream while keeping its cream fill, at roughly 1.05 to 1. A faint ghost at
2160px and entirely absent at 432px, so it was gone from the thumb and from the contact sheet.

**The sentence that vanished is the frame's whole guard.** c8 is `confidence: medium` and the
claims file's own rejected list says the record "carries the System's own assertion and does not
claim a dated governing body vote". Without that line slide 4 reads as the Board of Regents
approving 45 million dollars with no qualifier at all.

**EVERY GATE PASSED IT, AND THAT IS THE FINDING.** `copy.json` carried the string, because the
browser really did lay it out. `numeral_lint` traced every numeral. `dossier_check` passed an
acceptance item reading "the dek says No meeting date is published" because the string was in the
DOM. `qa.py` returned zero fails on that slide. `panel_ready` reports "every line clears the
rubric's 4.5 contrast floor" and reported it while this line sat at 1.05.

Not one of them asks the only question that mattered: **is the ink different from the paper.**
Twelve gates read what the document SAYS and none reads what the page SHOWS. This is
GATE_LESSONS' oldest shape arriving somewhere new, and the three judges converged on the same
one-sentence fix independently: measure contrast against the ground a mark actually lands on.

## The repair round, and what each fix was

Nine changes. Every one traces to a judge's named finding, and each frame that was repaired also
gained the assertion that would have caught its own defect.

| # | frame | what was wrong | what was done |
|---|---|---|---|
| 1 | 4 | the dek's third line on bare cream at 1.05 to 1 | curl extended to y 1172, gradient steepened to four stops for a dark plateau, dek pinned by TOP not BOTTOM, and the frame now computes a real WCAG ratio against the curl's own gradient sampled at the box's top and bottom edges and throws under 4.5 |
| 2 | 6 | set "willsupport" and "willbe" | the gap advanced by `w + 18` from the VERB's edge while the slot already extended `padX` past it, leaving 2px. Measured from the slot's edge now, with a 24px floor asserted |
| 3 | 6 | the only frame of nine with no source rule, on the thesis frame | both quotations print QUOTED FROM their publisher, punched through the leaf like every other word |
| 4 | caption | "Onboarding begins" where c16 says "is expected to begin" | corrected. The deck's fourth structural law, broken on the surface a reader meets first |
| 5 | 5 | a bare "10.4 million" where c18 says approximately, while "more than" was kept on the other side | "about 10.4 million", and the frame now PRINTS its refusal to join the two counts rather than keeping it in the script |
| 6 | 9 | c14 cited on the frame and never printed | "The front page is actively seeking beta testing participants" is on the page. The duplicate onboarding row came out, which also cleared the 65 word ceiling |
| 7 | 9 | the declared focal, "the brightest region in all nine frames", was in the dossier and in no drawing step | drawn as bare backlight measurably brighter than the bed, with slide 8's two empty pin stations carried onto the rail, and the pins now read THROUGH their holes |
| 8 | 7 | 1100 grain marks vacuously satisfied, about a dozen visible at 2160px and none at 432px | the switched-off table is BUILT rather than textured: panel seams on a grid, frame rails down each side, an ink floor on the grain, and the assertion now counts marks that CARRY INK |
| 9 | 4, 6 | curly quotes through HTML entities | straight quotes, asserted per frame |

**A registration scale was tried on slide 7 and taken back out.** It landed in the footer band,
the type keep-out ate every tick under the site line and the counter, and what rendered was a row
of graduations with a hole in the middle. A drawn thing interrupted by an exclusion zone reads as
a mistake rather than as an object, which is worse than the quiet it was answering.

**`qa.py` still measures slide 7 at 9 / 9 / 6 percent of cells carrying craft, unchanged.** The
marks sit under whatever contrast threshold flips a cell, and the frame is visibly a built table
at 432px where it was a flat rectangle. Recorded as a disagreement between a number and the
pixels rather than resolved, because the judges read the pixels.

**Two gate findings came out of the repair round itself**, both real:

- `coherence_check` failed slide 9 at 67 words against a 65 ceiling, caused by the c14 line. The
  duplicate onboarding row came out rather than c14 going back.
- `aggregate_check` failed five figures in `first_comment.txt`. Two were verbatim source
  quotations and are now declared through `quoted_from` with the exact quote. Three were counts
  the deck had invented, and the prose was reworded to stop asserting them.

Then `caption_check` failed the caption at 943 characters against brand.yaml's 900 ceiling,
caused by the two additions above. Trimmed to 866 with both of the panel's asks intact.

## Phase 15, panel round 2, and a defect older than round 1

**6.296, 6.17, 5.81. Per-criterion median 5.896, spread 0.486, two hard fails, HOLD.** The number
went DOWN from round 1's 6.526 and it is worth being exact about why: `claim_integrity` collapsed
from a 6.5 median to 4.5 on ONE finding, and it was not a defect the repair round introduced.

**All nine repairs were verified as landed by all three judges.** The reader judge said so in as
many words. This is not a round that claimed fixes it did not make.

**Slide 4 credited the wrong publisher, and it had done so through two rounds.** The frame's only
attribution read `BOARD CHAIRMAN / QUOTED IN THE SYSTEM'S NEWSROOM`. The quotation is c10, whose
fetched url is `tarleton.edu`. The deck's own first comment, published under the same post, says
"c10. The board chairman, quoted by Tarleton State University". So the deck contradicted itself
inside one post, on the one frame where a human speaks, in a deck whose entire argument is which
document said what.

**The label was not invented. It was taken from the wrong one of the two claims on that frame.**
Slide 4 declares c8 and c10. c8 IS the System's newsroom. Nothing compared the attribution's
publisher against the claims the frame declares, and both the craft judge and the integrity judge
called that a gate-shaped hole rather than a writing slip. It was in the dossier before it was in
the render.

**The repair round is what made it visible.** Round 1's fix extended and darkened the plate, and
nobody re-read the line above it. That is GATE_LESSONS' own shape: a repair verified against the
defect it was written for, on a frame carrying a different defect the whole time.

**The integrity judge found no hard fail and refused on the number**, 6.296 against a 6.8 bar,
and said out loud it would not manufacture one. `panel.py` derives that as a threshold dissent
from the judge's own score rather than reading a field, so it counts in the median and is not a
veto.

## The second repair round, on twelve findings

| # | what | what was done |
|---|---|---|
| 1 | slide 4 credited c10's quotation to the publisher of the OTHER claim on the frame | reads QUOTED BY TARLETON.EDU, and the frame throws unless it names c10's publisher AND does not name c8's |
| 2 | the first comment published "TOP500, the June 2026 list" and no quote names an edition | the edition label is gone |
| 3 | the cover printed "Number 66." over a rule naming TOP500, and no TOP500 quote carries a rank | the rule names the two documents the cover is actually about |
| 4 | the cover's thesis rested on c7 and the frame did not declare it | copy.json and the dossier declare c2, c7, c13 |
| 5 | slide 5's refusal sat in Tarleton's column, so the deck's own disclaimer read as Tarleton's sentence | its own element spanning both columns, and the frame throws if it sits inside either |
| 6 | the caption narrowed c16's "institutions" to the twelve universities, dropping the eight agencies | closes on c16's own word |
| 7 | the storyboard was not reconciled to round 1's repairs | reconciled, and one dek converted to a folded block because straight quotes inside a double quoted scalar is not YAML |
| 8 | the cover named neither its institution nor its machine, which both reader judges put first | "Texas A&M is No. 66. Both documents say will.", and the frame throws unless it names both |
| 9 | slides 8 and 9 were the two least made frames and they are the two the argument ends on | every sheet carries drawn fibre and a raked edge where its thickness catches the light |
| 10 | slide 8's 290px dead band | the travel lane down to the two pin stations, with registration marks at one computed pitch and an EMPTY dashed landing, because none of them has been punched |
| 11 | slide 9's brightest region carried no label, so the focal was luminance without meaning | labelled OPEN, between the two labelled sheets |
| 12 | slide 3's "There are 95" was questioned by eye | NOT a defect. The frame draws 12 by 7 plus a short row of 11 and throws unless exactly 95 apertures exist. Verified in the code rather than argued about |

**A full field hatch was deliberately not used on slide 8**, and the craft judge is why. That
frame already scores 0.75 / 0.87 / 0.66 on the band metric WHILE carrying the empty band, so the
metric rewards a hatch and a reader does not. What went in the gap is the thing the gap is for.

**Three of my own repairs broke something, and every one was caught by a gate or an assertion:**

- The cover's new source rule wrapped to two lines inside its 460px column and printed straight
  on top of the site line and the star. Every gate passed it. The strings were right, the nodes
  were there, the contrast was fine, and two of them were simply in the same place. The frame now
  asserts that no two elements in its lower stack occupy the same box.
- The building was added to slide 3's dek and `qa.py` failed it for a STRIKETHROUGH: the fourth
  line ran through a drawn rule at 12.1 to 1. The frame has no room for it without colliding with
  its own furniture, so it came back out and the West Campus Data Center is named in the caption
  and the cover names Texas A&M instead. Recorded as a limit rather than worked around.
- Reconciling the storyboard's curly quotes broke slide 6's dossier, because straight quotes
  inside a double quoted YAML scalar is not YAML, and `dossier_check` reported slide 6 rendered
  with no dossier at all.

## Phase 15, panel round 3, and two hard fails from one judge

**6.296 became 5.77, 6.17 became 6.382, 5.81 became 6.288. Median 6.3, spread 0.612, two hard
fails, HOLD.** The craft and reader judges both cleared their round 2 hard fail and found none.
The integrity judge found two, and both were real.

**The cover said "Texas A&M is No. 66." and I wrote it in round 2.** TOP500 ranks MACHINES. c1
was fetched precisely to record that the list credits this one to the Texas A&M University SYSTEM
rather than to one campus, and "Texas A&M" unqualified is the campus, which is the exact entity
c1 exists to distinguish. The deck's own rejected list and its own first comment both say TOP500
publishes no university category, so the cover asserted a proposition the run's published notes
refute two surfaces away.

**That is a fix introducing a worse defect than the one it repaired**, and it is the third time
this run that a repair broke something. The reader judge scored it under `claim_integrity` rather
than stopping the deck, and said out loud that another judge could land the other way. One did.

**c19's own text field carried two assertions its quote does not.** It read "The System puts the
same screening run at more than ten million compounds in about a week." The quote is Tarleton
State's and says nothing about it being the same run. So the record asserted the identity slide 5
denies on the frame in the deck's own voice and that the first comment denies in print, and it
credited the A&M System with a sentence published by Tarleton, **which is the identical publisher
substitution that hard-failed slide 4 in round 2, one claim away and unrepaired.**

The lesson is the integrity judge's own one-sentence fix and it generalises past this deck: the
frames now assert source entailment and `claims.json`'s own prose fields assert nothing.

## The third repair round, on eleven findings

| # | what | what was done |
|---|---|---|
| 1 | the cover awarded a TOP500 rank to an institution | "VISION is No. 66.", c2's own subject, and the frame throws unless the hook starts there and throws if it names an institution as the ranked thing |
| 2 | c19's text asserted an identity the deck refuses and named the wrong publisher | "Tarleton State reports researchers screened more than ten million compounds in about a week." |
| 3 | "June 2026" survived in claims.json's story and computed.json after leaving the first comment | gone from both |
| 4 | slide 2's PIXELS published the verdict its STRINGS are gated against, and two judges read it as two bars with the darker one shorter, inverting 34.82 against 51.16 | the value ramp is GONE. Ink laid down to the measured figure, a dashed outline to the theoretical peak, which is slide 9's own filled versus outlined law, and the frame throws unless the inked share EQUALS RMAX over RPEAK |
| 5 | slide 7 set verbatim source text with no marks and no publisher, while slide 6 labels both of its quotations | marked and attributed, and asserted |
| 6 | slide 7 held c15 and did not print it | it prints. A deck whose thesis is read what the document says, holding the qualifying claim and leaving it off, is the accusation turned inward |
| 7 | slide 9 was the only content frame of nine with no source domain, on the frame that asks a reader to act | VISION.TAMUS.EDU/TESTING |
| 8 | slide 9's unlabelled tick rule read at 432px as a TIMELINE, on the frame whose message is that no date is published | removed. A frame that refuses to imply a date may not draw a ruler across its foot |
| 9 | slide 8's lane was drafting furniture the deck's own risk list bans by name | two empty seats on the same leaf module, outlined not filled, one over each pin station |
| 10 | three pin pitches in one payoff, so the 8 to 9 rhyme held only in the labels | one pitch, 152px, on all three |
| 11 | slide 6's slots were highlighter chips in a register whose premise is light through material | a cut wall on two sides, a lit lip on the other two, every edge asserted clear of the verb's own glyph box |

**THE VALUE ARC SAID IT WAS MEASURED AND WAS A GUESS, FOR THE FIFTH TIME IN THIS LEDGER.** The
storyboard read `34 · 45 · 52 · 40 · 66 · 43 · 9 · 38 · 62`, deck median about 43, directly above
the words "measured off the rendered PNGs and never asserted from this line". Round 3's craft
judge said it smelled wrong, named slides 3 and 5, and declined to call it a finding without
computing it.

Nine lines of PIL settled it. **Measured: `72.0 · 94.0 · 17.8 · 76.5 · 16.5 · 29.9 · 16.8 · 92.6 ·
92.4`, deck median 72.0.** The judge was right about slide 5 by a factor of four. This is a LIGHT
deck and the plan had it as a dark one, and the claim that the once per eight light cap was
untouched does not survive its own measurement. Decks 8, 9, 12 and 13 each carry a ledger entry
recording this exact fault.

**Two of my own round 3 repairs broke a frame and `qa.py` caught both.** Slide 6's new slot walls
painted a 93 by 6 rect straight over the word `will` (the frame now asserts every edge clears the
verb's glyph box), and printing c15 made slide 7's dek a line longer so it overprinted the note by
60 percent. That is four self-inflicted breakages across three repair rounds, every one caught by
a gate or an assertion rather than by a judge, which is the arrangement working.

## Phase 15, panel round 4, and the widest split of the run

**6.01, 6.85, 7.11. Median 6.602, spread 1.10, one hard fail, HOLD.** The craft and reader judges
both voted SHIP for the first time. The integrity judge found one hard fail and it was real.

**The spread is 1.10 and `panel.py` says so in the file**, which is the whole reason it reports
one: three judges disagreeing by more than 0.75 have not converged on the same deck, and the
disagreement is worth more than the median. Reader 7.11 and integrity 6.01 on the same nine
frames is the panel doing its job rather than failing at it.

**Slide 7 credited the docs page with a sentence from the testing page, and I wrote it in round 3
fixing "c15 was withheld".** The dek read "The same page says the beta is being finalized". The
antecedent of "the same page" is `docs.vision.tamus.edu`, which is also the frame's only source
stamp. c15 lives at `vision.tamus.edu/testing/`. So the frame pointed a reader who wanted to
check it at a page that does not carry it, and `copy.json`'s S7 claim list was `[c12, c11, c20]`
with no c15, so no gate ever saw the sentence attached to a claim at all.

**That is the round 3 c19 fault one slide over, in the deck whose entire subject is which document
says what.** Third repair in three rounds to introduce a fresh defect of the same family.

## The fourth repair round, and the last one this run gets

`max_rounds` is 5, so round 5 is the cap and the deck ships on whatever the panel says there.

| what | what was done |
|---|---|
| slide 7 credited the wrong page for c15 | reads "The testing page says", stamps both hosts, and throws if the string "The same page" appears |
| slide 4 stamped only TARLETON.EDU while its dek's 45 million is c8 from the newsroom | the dek names its own publisher inside the sentence, the way every other frame does |
| slide 9's one stamp covered three lines from two hosts | both named, both asserted |
| slide 7's hook is verbatim c12 and carried no marks, while the frame's other quotation did | marked, and the frame now asserts four marks rather than two |
| the storyboard described three frames that did not render | slide 2's wedge and windows, slide 5's crowding fibre, slide 7's one sentence dek, all reconciled |
| **nine focal shares were unmeasured assertions of exactly the kind the value arc had just been caught being** | `measure_focals.py` computes every one from the rectangle the frame actually draws. Slide 1 was "about 11 percent" and is 44.6. Slide 9 was "about 16" and is 3.2. Slide 8 was "about 34" and is 21.3 |
| the arc note called the junction INTO slide 7 the deck's largest, against its own new array | it is 13.1 in and 75.8 out. The note says both now, and that the frame is entered quietly and left hard |
| slide 9 drew one object two ways, domed posts for the seated sheet and flat ellipses for the open stations | one pin, one drawing, and the frame asserts an open station is the same object as a seated one |
| slide 8's seats were 15 percent oversize, sat 224px below the course, and carried no label | the stroke is drawn inside the module, they were raised, and they say what they are |
| slide 5 carried a magnitude with no purpose, on the brightest frame in the deck | c19's own words, "in one drug discovery project" |
| slide 2's measured readout hung over the DASHED remainder | over its own ink, asserted |

**CORRECTING THE ONE NUMBER A JUDGE NAMES IS NOT A FIX.** Round 3 replaced the value arc after a
judge caught it claiming to be measured. Round 4's craft judge then found four more of the
identical kind in the same file, untouched, and its one-sentence fix was to generate every
measurable field rather than type it. That is the difference between patching an instance and
closing a class, and this run did the first one first.

**`bespoke_check` FAILED the deck at 0.5515 against a 0.55 line, and it was right.** Three rounds
of repairs had put the same rect-loop idiom into several frames, and slides 6 and 7 came out at
0.791. Slide 6's four wall rects were redrawn as two continuous L-shaped bevels, which is a
different construction, reads better at 432px, and dropped the median to 0.5486. **A gate this
run tripped by repairing things.**

**`aggregate_check` rejected the first label I put on slide 8's seats.** It read "TWO STATIONS,
NOTHING SEATED", and two is a count of objects the deck drew rather than anything a source says.
Reworded to "OPEN STATIONS, NOTHING SEATED". The gate was right and the label is better for it.

## Phase 15, panel round 5, the cap

**6.75, 6.51, 7.002. Median 6.762, spread 0.492, NO HARD FAILS from any judge for the first time
in five rounds. HOLD, 0.038 under the bar.** `max_rounds` is 5, so the deck ships on this.

Two judges refused on the threshold and said so explicitly rather than manufacturing a fault. The
reader judge shipped at 7.002.

**The cap round found two things this run had REPORTED AS FIXED AND HAD NOT FIXED**, and that is
the worst class of error in the whole run.

- **`measure_focals.py` opened the PNG, computed a scale factor from its width, never used it
  again, and returned arithmetic over nine hardcoded rectangles.** Under a docstring reading
  "Measure every declared focal AREA off the rendered PNG" and "the numbers come out of the
  pixels". Round 4 wrote that script to end the fault of typed figures claiming to be measured,
  and the script was the same fault one level up: not a number claiming to be measured, but a
  MEASUREMENT PROGRAM claiming to be one. The craft judge read the source rather than the
  docstring, which is the only reason it was caught.
- **The arc note still said the junction into slide 7 was the deck's largest.** Computed off the
  measured array it is 13.1 in and 75.8 out, and the deck's largest is 2 to 3 at 76.2. The
  repair was reported in round 4 and is not in the artifact, because the replacement string did
  not match and nothing checked that it had.

**The rewritten script reads pixels and immediately found something the rectangles could not.**
It computes each frame's own 98th or 2nd percentile L* and the share of the frame within 8 L* of
it. Five of nine frames come back WIDE, and two of them are damning: **slides 8 and 9 declare a
small object as "the frame's light extreme" while 80 percent of each frame sits at that value.**
The light extreme on those frames is the GROUND. The dossiers now say so in the same line.

What the script still cannot do is decide which object the designer meant, and it says that out
loud rather than implying otherwise. Round 5's integrity judge found the declared rectangles are
BOUNDING BOXES rather than the objects in them, so slide 6's two slots measure 5.7 percent as a
box and about 1.3 as drawn. That is not closed, and both judges named the same fix: have each
frame emit its focal geometry from the elements it actually drew, and generate the dossier from
that rather than reconciling prose against pixels by hand five rounds running.

## The fifth repair round, after the cap

Nothing here changed the panel's verdict. All of it is the difference between shipping a record
that is true and one that is merely green.

| what | what was done |
|---|---|
| `measure_focals.py` claimed pixel measurement and did arithmetic on typed constants | rewritten to read each frame's own value extreme out of the PNG, and to label the declared rectangle as AUTHORED rather than measured |
| the arc note asserted a junction the measured array refutes | computed: 13.1 in, 75.8 out, and the deck's largest is 2 to 3 at 76.2, which is not the designed one |
| slide 2's `value_structure` and `motion` still described the deleted density ramp and two cut windows | reconciled to the frame that renders |
| slide 2's own `data-encodes` claim still said "a cut window is bare backlight" | rewritten, and `qa.py` then caught an apostrophe breaking the JSON inside the single quoted attribute |
| slide 7's dossier carried the pre-fix one sentence dek, an unquoted hook and one host | all three reconciled |
| **slide 6 set a direct quotation from the chancellor and named no publisher for it** | it names the System's newsroom, and the frame asserts it. This is the defect that hard failed slide 4 in rounds 2 and 4, standing the whole time on the frame nobody had looked at |

**Three frames carried the same attribution defect and each was found in a different round.** Slide
4 in round 2, slide 7 in round 4, slide 6 in round 5. Every fix was to the instance. Nothing in
this repo binds a frame's source stamp to the claims its copy actually carries, and both round 5
judges proposed exactly that, independently, as their one sentence fix.
