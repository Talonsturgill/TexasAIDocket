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
| 6 | claims | IN PROGRESS. fact-checker out on the VISION story |
| 7 | instrument once over | DONE. All page checks exit 0. Supabase connector unavailable |
| 8 | selection + dedupe | DONE. VISION picked, dedupe 0.31, texan_check says NO next step |
| 9 | directors room | TODO |
| 10 | copy chamber | TODO |
| 11 | art build | TODO |
| 12 | pixel review | TODO |
| 12b | the six gates | TODO |
| 13 | aggregate gate | TODO |
| 14 | assembly, panel_ready | TODO |
| 15 | scoring panel | TODO |
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

**The story is the Texas A&M University System's VISION supercomputer.** A large shared AI
machine at Texas A&M in Brazos County, ranked the fastest university supercomputer in the United
States on the June 2026 TOP500, whose access runs system-wide to twelve universities and eight
state agencies, and whose own site still lists it as in beta ahead of wider release.

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
