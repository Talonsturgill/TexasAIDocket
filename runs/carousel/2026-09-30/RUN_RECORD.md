# Run record, September 30th, 2026

## DISPOSITION: SHIPPED AT THE ROUND CAP, 7.45, 0.25 UNDER THE 7.7 RUNG AND 0.55 UNDER THE 8.0 TOP RUNG

Carousel no. 38, "A machine reads it first.", is nine frames rendered in one overcast Texas ISD
campus world with a combo student desk as the hero. It went through a critic round and five scoring
rounds with three judges each. The panel medians were 6.924, 7.18, 7.19, 7.40 and 7.45.

- **Round 1** carried one hard fail, slide 7 stating the agency's statement (c20) as fact, repaired in round 2.
- **Round 5** carried one hard fail on the web edition, an unscoped universal ("every written answer a
  Texas student types") that c20, c21 and c22 refute, with the same unscoped set on the cover dek and
  the caption. It was repaired on every surface after the cards arrived, which is the one repair a round
  past the cap may make. Four integrity-only passes verified it. Each of the first three found
  the same set still unscoped somewhere the last repair had not reached: the record item, the web
  dek, the web lede and a Spanish sentence. Each finding was repaired before the next pass, and the
  fourth confirmed every earlier repair. No sixth round scored the repair.

At the cap the finished deck ships under the ladder. The heaviest drag is artwork_craft, 6.3 to 6.5
across the final judges. The most repeated named defects:
- the kit people read as mannequins
- frame 5's classroom reads unfinished
- the ground and the school read as a render engine
- the close gives no rescore dates or fee, because no fetched claim carries them

## The record, first

- **Worklist.** `docket_staleness.py` named 53 items due, none rotten. `reverify.py --apply` asked
  104 urls behind 344 claims (13 answered 304, 84 sent a body, 7 did not answer) and stamped 21
  items checked and unchanged. Seventeen of those deterministic lines were rewritten by hand, same
  facts, and `reverify.py --check-notes` passed on every figure (1,532 checked notes).
- **The four boundary stamps were withdrawn again.** `reverify.py` stamped tx-2026-0125 (TACC, a
  host the crawl boundary puts off limits whole) and tx-2026-0168, 0169 and 0170 (the Hays County
  agenda on public.destinyhosted.com, whose robots.txt is `User-agent: * Disallow: /` on one line).
  It fetched both hosts to do it, exactly as on September 29th. The stamps rest on refused requests,
  so they were withdrawn and each item carries a dated line naming what is unconfirmed. **The
  defect in `reverify.py` is unfixed and is now a two day old proposal.**
- **This run's own helper made the same mistake once, and it is recorded rather than hidden.** A
  scratch re-verification helper used Python's `urllib.robotparser`, which does not parse a
  robots.txt written on a single line, so it read public.destinyhosted.com as allowed and fetched
  the agenda for the three Hays County items. The parser was fixed to split directives before
  parsing, the result was discarded, and the three items stayed unstamped. `crawl_boundary.py` has
  no rule for that host, so the registry does not catch it either.
- **Stamped by hand after reading a primary source (27, plus 0186).** tx-2026-0003, 0015, 0016,
  0027, 0028, 0032, 0033, 0037, 0039, 0046, 0052, 0054, 0056, 0057, 0063, 0076, 0077, 0099, 0124,
  0129, 0142, 0152, 0156, 0157, 0159, 0165 and 0189, and tx-2026-0186. Every one read a primary
  document or the item's own primary source, with a normalised quote match. Partial matches were
  inspected and each was a text layer artifact (a page break, a stripped section sign), never a
  change. The FAA's Zipline page and draft assessment 403 the project's own agent and answer a
  browser agent, and faa.gov's robots.txt permits `/uas/` to a browser, so tx-2026-0186 was read
  that way, as the registry does for PUCT and the Tribune, and all 17 of its claims held.
- **Not stamped (8), each with a dated line naming what is unconfirmed.** tx-2026-0036 (Guadalupe
  County Flock contract) and tx-2026-0044 (Angelina County resolution): both published accounts
  sit on hosts whose robots.txt names ClaudeBot with `Disallow: /` (seguingazette.com, ksat.com,
  kltv.com, lufkindailynews.com), and neither county's front door page carries the vote.
  tx-2026-0088 (Brazos County, 403 to every client). tx-2026-0120 (dhs.gov answered 403 to the
  project's agent and to a browser agent, page and robots.txt alike, now recorded as an
  `unreachable` block). tx-2026-0125, 0168, 0169, 0170 as above.
- **Banned word.** tx-2026-0024's summary and access note carried "matters" and failed the record
  gate once stamped. Reworded to "cases".
- **Admitted (1).** tx-2026-0194, the Texas Education Agency's hybrid scoring of written STAAR
  answers, on the agency's own December 2023 scoring process and March 2024 key questions
  presentation, with the Tribune's September 4th account of the annual rescore. Statewide,
  state-agency, decided, room `contact_only` (a family starts with the district's testing staff).
- **Backlog.** `site_build` printed no backlog lines.
- **Phase 7.** Both instrument page checks exit 0 (current and holding their promises), and every
  discoverability self-test and check exits 0.
- **Scanner ceiling.** Not checked. This run has no Cloudflare D1 access and no Worker settings
  access, so `today`, `failed_24h` and the live `DAILY_CAP` are all unknown. Nothing is reported
  healthy from a repository default.

## What the deck is

Carousel no. 38, "A machine reads it first.", is nine frames rendered in one overcast world on a
Texas ISD campus, the chassis at `assets/js/deck/2026-09-30-firstreader.js`. The lid is a cool
luminous overcast (zenith 0x8d98a6, horizon 0xe3e6e6), the key sits at azimuth -40 and elevation
48, and dark type sits on the pale sky. The hero is built in the chassis: `student_desk`, a combo
chair desk with a putty laminate top, a bent black tube frame and a charcoal seat shell, carrying
the kit laptop with its screen lit. Any count stands as a field of instanced desks with footprint
contact decals, and the desks nearest a lens are the full model while the count stays exact. The
one accent is bluebonnet, #4E5FA8, and it is only ever the shirt of a person reading an answer.

The deck counts in desks.
- One desk alone on the practice field (frame 1).
- 3,000 on the school's football field (frame 2).
- A block of a hundred with the attended quarter as its near left five by five (frame 3).
- A row of four with the fourth read by two people (frame 4).
- A classroom row of five with a reader at every one (frame 5).
- A thousand from frame 3's camera with a content expert at seventeen (frame 6).
- 27,200 craned up from frame 1's seat (frame 7).

The close walks the parent under the school's covered entry (frame 8), then stands her at frame
1's desk, on frame 1's camera, reading the screen (frame 9).

**Copy decisions the record forced.**
- Frame 7's headline carries "The agency says", because c20 is a spokesperson's statement relayed
  by the Tribune.
- The deck never says the engine is accurate or inaccurate. The fall corrections were answers the
  engine never scored (c20, c21, c22).
- Low confidence is printed as low confidence, because c7 says such answers are often borderline,
  not that they are the borderline ones.
- No fee amount and no window appear anywhere, because no claim carries either.
- The 75% is scoped to the agency's own chart, since c13 is a March 2024 presentation.

## Critic round and panel rounds

- **Pixel and flow critics (five pixel, one flow).**
  - Frame 5 was rebuilt: five desks, not three, and no teacher desk or unexplained props.
  - Frame 6 was redrawn from frame 3's camera as a block of desks, not a foreshortened band.
  - Frame 7 was craned up from the home seat, because at a seated eye 27,200 read as fewer than
    frame 2's 3,000.
  - The readers were put in accent shirts.
  - Frame 8 got a real covered walk.
  - The rescore copy was split between frames 8 and 9.
  - Frame 7 was made to lead with c20.
  - c33 and c34 were added for the routing.
- **Round 1, 6.924, one hard fail.** Slide 7's headline stated the agency's statement as fact.
  Every judge named the readers: none of them was reading. The judges also named:
  - the parent in the scorers' shirt
  - frame 5's mannequins
  - the pale wash under the footer on 2 and 7
  - the caption's line narrating the deck
  - the missing why (c14)
- **Round 2 repairs.**
  - The attribution is on slide 7.
  - The cover names its set and gives the why.
  - Slide 4 says low confidence.
  - Slide 6 says its thousand desks are a per thousand drawing.
  - Two kit poses let every reader sit at a screen or lean over one.
  - The parent wears her own shirt.
  - Frame 4 draws four whole desks with the leaders on the screen.
  - Frame 5 is a seated row against a window band.
  - Frame 7 has an expert reading at a desk.
  - The footer band darkens instead of washing pale.
  - The desk's back posts run into the panel.

**The rounds, in one line each.**
- Round 1, 6.924. Hard fail on slide 7's unattributed c20. Every judge named that no reader was reading.
- Round 2, 7.18. Readers seated and leaning through two new kit poses, the parent out of the accent,
  the cover scoped to Spanish, the why (c14) on the cover.
- Round 3, 7.19. Hands on the desk, the banded halo dithered, the flags off the type, c35 (the rescore
  window) added from the same primary document.
- Round 4, 7.40. Frame 5 furnished and relit, frame 6 redrawn, frame 7's meaning stated, one
  bracket leader on 4, shade under the school's walk, cloud in the lid.
- Round 5, 7.45. Frame 6's experts back at the lit screens, frame 3's quarter moved to the far corner,
  frame 7's inference scoped to the web edition's words. Hard fail on the web edition's universal,
  repaired after the round.
- **The judges pulled frame 6 two ways.** Round 3's integrity judge read experts at only the seventeen
  improved desks as people rereading 1.7%. Round 4's read lit screens with no person as the engine's
  own sign. Round 5 seats experts at the lit screens and names the answer type in the dek, and neither
  reading came back as a hard fail.
- **A reader card misread the sources block once.** Round 5's reader judge said the first comment
  omits c21 and c22. It lists both on the Tribune line.
- **The score row reads as round 5's cards.** score.json describes the render before the hard fail
  repair (frame 1's dek, frame 5's back row and the web edition). No score was refreshed by hand.


## Did this run stop and wait for a human

`prompt_audit.py` exits 1 at Phase 17 and reports 1,704 calls measured, 482 over its one second line.
**This reading is interim**, since everything after Phase 17 can still prompt, and Phase 19 takes the
one that counts.

**What was measured.** The debug log's permission decisions fall into two groups:
- 1,202 calls under 100 ms and 20 from 100 ms to 1 s
- 438 calls from 1 to 2 s, 43 from 2 to 5 s, and one Bash call at 10.5 s at 09:36:16 UTC

**What the hook saw.** The no-stall hook was armed at 06:15:48 UTC. It judged the session unattended, with the host's own
`CLAUDE_CODE_SESSION_ATTENDED=0`. It refused nothing and logged no dialog waiting.

**How to read it.** Hundreds of waits of one to three seconds, in a session nobody attended, look like
the host's own decision latency rather than a person. The tool's rule says past a second is a human, so
this record reports the reading as the tool gives it and says why that reading is doubtful. The
upgrade phase wrote a proposal to count a wait as human only when the hook logged a dialog for it
(UPGRADE_BACKLOG, 2026-09-30).

## Instrument check and web edition

- Every page check exited 0, and so did the whole Phase 16 verify list on the rebuilt site.
- `tests/article_edition.mjs` passed 645 reader checks. It needed `npm ci` in this container, which
  had no `node_modules`.
- The rebuild first refused the web dek, which was over 200 characters. It was cut to 172, scoped to
  English language tests.
- house_style_check refused four sentences over 30 words and a comma rate 0.24 over the ceiling. Each
  was split at a clause.
- The phone screenshot showed "75%%", "65%%", "95%%" and "1.7%%", and "December 2023,.". A number token
  carries its own unit and punctuation, so the edition's text around each token was rewritten.
- **The same double percent is on the published September 27th article** ("26%% to 69%%"). That is
  shipped history this run does not rewrite, so a maintainer call is owed.

## Discoverability signoff

- **Card.** docs/og/tx-2026-0194.png was opened as an image. The scoped title cut to a stump at the card's
  four lines twice, so the title was shortened until the card carried the whole claim: "A machine
  scores the longer written answers on English STAAR first".
- **/questions/.** It was rebuilt with the item.
- **llms.txt, Open right now.** tx-2026-0194 carries no open window, because the rescore window's dates are not in the record,
  so it is not listed.
- **/topic/.** tx-2026-0194 is on the health and education topic page.
- **/place/.** The item is statewide with no county, so no place page lists it.

## The upgrade phase

The upgrade engineer made three kit upgrades in the `upgrade` lane, each proved through the carousel
engine on this deck's frames.
- **`student_desk` and `student_desk_rows` lifted into `assets/js/kit/interior.js`** at round 1's named fix.
  Each side frame is one continuous bent tube, and the back posts run into a moulded back. The rows
  share its tessellation, so no detail seam shows.
- **The kit school shades its own covered walk.** The chassis's shade quad landed 6.53 m in front of the
  wall, measured by ray cast, because it was placed after the school was re-centred.
- **`classroom_window`**, the model half of frame 5's top defect.

Frame 5's room is also half the engine. A real window opening needs `TXT.interior` openings in
`txthree.js`, which is `human`. It heads the backlog.

The engineer also found the captions ledger's exclusion lists one entry behind for the fifth run
running. They were re-derived with `ledger_check --derive` before the merge.

## Things this run did not do

- **No second pixel critic round.** The panel read every frame after the critics' round.
- **No fee amount, no rescore window.** The agency's documents describe the process and not its
  price or this year's dates, so the deck and the web edition both say only what the record holds.
- **Maintainer calls owed.**
  - The September 27th article prints a doubled percent sign. Shipped history, not rewritten here.
  - `reverify.py` still fetches hosts the crawl boundary refuses. This is the third run to
    withdraw its stamps.
  - `crawl_boundary.py` has no rule for public.destinyhosted.com.
- **Scanner ceiling not checked** (above).

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 35 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 10 warn(s) |
| aggregates     | PASS   | 6 declaration(s), 7 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 8.47 MB, vector |
| score          | STALE  | score.json predates the newest render, so it describes a deck that no longer exists. Re-run it |
| labels         | PASS   | 30 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 82 published string(s) read from one list, every universal names its set |
| verbatim       | PASS   | 2 declared fragment(s) over 9 of 9 dossier(s), every one a literal substring of its own claim's quote |
| dossiers       | PASS   | 28,542 chars planned |
| caption        | PASS   | 159 words |
| craft floor    | PASS   | 9 frame(s), median 3069, floor 552 |
| plan vs render | WARN   | 15 of 54 acceptance item(s) checkable |
| texan          | WARN   | places NONE / body yes / deadline yes / next step NO |
| absences       | WARN   | 0 of 4 scoped to a named document, 4 unscoped |
| numerals       | PASS   | 15 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
