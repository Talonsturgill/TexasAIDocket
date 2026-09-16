# Run record, September 16th, 2026

Branch `claude/daily-2026-09-16`. Carousel no. 26.

## The instrument check

Both instruments clean by exit code. `gridwatch_pagecheck` 0, `waterwatch_pagecheck` 0,
`waterwatch_page --self-test` 0. Nothing has stopped and nothing is reading wrong.

**THE SCANNER'S DAILY CEILING WAS NOT CHECKED, and that is a gap rather than a quiet day.**
Phase 7 asks for a Supabase query against project `texas-ai-scanner`. No Supabase connector is
attached to this environment, so the query could not be run by any route. A requester who hit
the cap today would not have been noticed here, which is the exact failure the step exists to
catch. This never blocks the run and it is named here because a ceiling nobody is notified
about is one you find out about from the people who gave up.

## The record

The selector named **128 of 138 items due**, nothing rotten, and DEFERRED empty. No `--budget`
was passed. **The worklist finished at zero due.**

`reverify.py --today 2026-09-16 --apply` read 225 urls behind 701 claims. 35 answered 304, 184
sent a body, 6 did not answer, and it stamped 90 items as checked and unchanged.

The remaining **38 were re-checked by hand**, and the reason they landed there is worth stating
because it is a property of the fetcher rather than of the record. `wilcotx.gov` and
`brownsvilletx.gov` answered 429, `news.rice.edu` answered 406, six items cite an agenda or an
attachment PDF, and Oncor timed out. A browser User-Agent and a PDF reader settled all but six
claims. Twelve items came back with every claim present. Every one of the 38 carries its own
dated movement line.

The 90 deterministic lines were re-worded one at a time. `reverify.py --check-notes` reports 910
checked notes with every figure traceable.

### Nine claims were resting on a page that cannot hold them

Three items cited `capitol.texas.gov/Committees/MeetingsUpcoming.aspx`, which carries only what
is still AHEAD. A quote taken from it stops being verifiable the moment the hearing is held, so
those claims had been reported as moved on every run since the sittings, and would have been
forever.

`MeetingsByCmte.aspx` is the permanent archive, on the same allowed host path, and it reproduces
the same date, time and committee. Seven claims now cite it.

**One was deliberately left where it was.** `tx-2026-0096-c5` carries the hearing room, and the
room has no durable home: the notice PDF that would carry it is under `/tlodocs/`, which the
sources registry puts off limits. Re-pointing it would have quietly dropped a sourced fact from
reader copy, which `--check-notes` caught by refusing the numeral. A claim that can no longer be
re-confirmed is better than a fact the record stops being able to show.

### What moved

**House State Affairs sat again on September 14th and September 15th.** Both sittings are in the
record now, from the committee's own archive, with the dates as key dates. What it took up at
either is not yet established here.

`tx-2026-0027` is confirmed by its own failure. The item says the City of Taylor's notice of the
amended abatement is no longer posted, and the address now answers 404.

### The backlog

**Both ratchets are at zero and neither grew.** No item is without a county or a statewide flag,
and no reader-copy pointer names an item the record does not hold.

## Discoverability signoff

- **One decision's card, opened as an image.** `docs/og/tx-2026-0161.png`, the run's newest item.
  1200 by 630. The headline wraps after "builds a", "federally funded AI" and "tutor that
  withholds", all places a reader would break it, and it ends on a whole word before the
  ellipsis. **The finding is the truncation rather than the wrap.** The title carries two halves
  and the card shows one, so somebody who meets this item through a shared link sees the tutor
  and never learns the same method is being pointed at police training. That is a title-length
  problem, not a renderer problem.
- **`/questions/`, read as a reader.** 13 questions. They are the ones somebody would type, and
  "Where a comment window is open" and "When each one was last checked" are the two that only
  this record can answer. No shape has broken against the statuses now in the ledger.
- **The `Open right now` section of `llms.txt`.** Three federal windows, each with its dated way
  in, and each one matches an item Phase 3 re-verified as still open today. Nothing closed today
  is still listed, so the build is not running ahead of the record.
- **`/sources/`, the record's own report card.** **682 of 764 claims rest on a primary document,
  across 239 documents from 106 publishers.** The share is the figure that tests the promise the
  whole record makes and it is the one to watch. The top publisher is
  `interchange.puc.texas.gov` at 99 claims over 20 documents, which is the filing system itself
  rather than a report about one, so the head of that list is where it should be. `api.nsf.gov`
  is second at 54. The quoted-material exemption is still doing its own job and is not sheltering
  any of our sentences.
- **`/topic/`, counting one card against its own page.** The research and science page says 26 of
  138. The eight beats on the hub row read 30, 6, 17, 15, 16, 26, 17 and 11, which sum to 138 and
  match both the ledger and the front page's own `138 Decisions tracked`.
- **`/place/`, for the place this run landed something in.** `place/county-tarrant/` says 4 items
  and links exactly the four the ledger puts in Tarrant County, `tx-2026-0059`, `tx-2026-0062`,
  `tx-2026-0103` and `tx-2026-0161`. Tarrant is on the hub, so the build did not run ahead of the
  record.

The front page counter row prints five of its six candidates and `Sources cited` is among them.

## Sources, what they actually did

Appended to `knowledge/shared/SOURCES_FIELD_LOG.md` in this run's commit range.

## The deck: the panel, and the repair round it forced

The first panel scored the deck under the ship threshold on all three lenses (integrity 6.376,
craft 6.708, reader 6.492) and it was right to. The planning in the storyboard was sound and the
renders executed about half of it. **The single root cause under most of the findings was
arithmetic no gate was checking.** The run computed all nine frames' 432px median value, wrote
them to `measured_arc.json` beside the storyboard, and never compared them to the nine bands the
storyboard had written for itself. Five of nine frames were outside their own band, three by more
than twenty points, while the storyboard still asserted every frame was inside its range.

So the first fix was a gate. `out/2026-09-16/measure_arc.py` measures each frame's median at feed
size against its dossier's declared band and fails on any frame outside it. It is the deck-side
twin of the lesson GATE_LESSONS keeps recording: a number on disk that nothing reads is not a
measurement.

Then every frame was rebuilt or retuned against the panel's specific findings:

- **Frame 1.** The answer line, which is the deck's whole thesis, had working drawn across it and
  no bare page anywhere. The strokes stop at line nine now, the answer line is empty with bare
  page above it, and the pencil is at true page scale rather than half of it.
- **Frame 3.** A lit classroom whose median was being read off two opaque black plates covering
  ~42 percent of the frame, so relighting the room never moved it. Light bond plates with dark
  type now, the instructor and students separable at 8 L* or more, and the accent is a real
  desktop light pool drawn as a perspective quad rather than a floating ellipse.
- **Frame 4.** The declared subject was not on the canvas at all. At eye 1.60 and f 900 the table
  at Z 2.05 projected 132 px below the frame foot, so only heads were ever in the picture. The
  camera looks along the table now, the whole scene is in frame, the tablet is at its true area,
  and the researcher Shuchi Deb and the University of Texas at Arlington are named at reading size,
  which is what gives the headline's "her" a referent for the first time in the deck.
- **Frame 5.** "teaches, not tells" now stands on a lit floor with per-line extrusion, and the
  letters are dark and engraved rather than white, which clears the 4.5 contrast floor on the lit
  concrete wall without darkening the wall out of its value band.
- **Frame 6, the turn.** Two people facing each other across the blue floor patch, the light
  raking from the left so the type's corner is dark by construction, and the accent printed
  through the halftone rather than laid over it.
- **Frame 7, the payload.** The accent was on the NSF funding line, which broke the deck's one
  structural law on the one frame that declared none, and the payload footnote was set smaller
  than the furniture. The accent is gone, the footnote is at reading size, the grant number is
  mono so a 1 is a 1, and the lit empty ruled field the storyboard promised is finally drawn.
- **Frame 8.** Three units meant to be identical were drawn three times and came out different
  sizes with unequal accent patches, so the frame ranked three things the source does not rank.
  One unit is drawn once and stamped three times now, identical by construction, on posts with
  nameplates over a receding grid.
- **Frame 9, the close.** The podium had no top face and the person stood a metre away facing
  nowhere. The podium has a lit top face now, the person is at it, three desk backs are cropped
  in the near ground, and there is no fed_blue anywhere, which is the deck's load bearing absence.

After the repair every frame is inside its own declared band, the measured arc is
77.8, 77.5, 51.0, 34.1, 45.9, 20.8, 77.5, 43.5, 13.0, deck median 45.9, spread 64.8, under
`ledger_check`'s 60.0 cap. `machine_qa.py` is WARN with zero fails across nine frames, every
local gate is green by exit code, and `panel_ready` reports the deck ready to be scored. The
second panel is scoring the rebuilt deck as this is written and its report card is recorded once
`panel.py` combines the three lenses.

## The caption

Two candidates, the object opener on a Ledger structure and the quiet decision on a Clock. The
critic took the object, imposing seven repairs, the load bearing one being that the first cut's
close welded the NSF start date to the Fort Worth police half, which is the causal link the claims
file explicitly rejects. The shipped close names instead how thin the public account of the police
half is. `caption_check` exit 0.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 35 verified claim(s) |
| render         | WARN   | 9 slide(s), 14 overflow warning(s) |
| qa             | WARN   | 0 fail(s), 52 warn(s) |
| aggregates     | PASS   | 7 declaration(s), 7 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 14.5 MB, vector |
| score          | PASS   | 7.492 |
| labels         | PASS   | 32 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 76 published string(s) read from one list, every universal names its set |
| verbatim       | PASS   | 7 declared fragment(s) over 9 of 9 dossier(s), every one a literal substring of its own claim's quote |
| dossiers       | PASS   | 37,919 chars planned |
| caption        | PASS   | 145 words |
| craft floor    | PASS   | 9 frame(s), median 5796, floor 1043 |
| plan vs render | WARN   | 9 of 55 acceptance item(s) checkable |
| texan          | PASS   | places Arlington, Fort Worth / body yes / deadline yes / next step yes |
| absences       | PASS   | 15 of 15 scoped to a named document |
| numerals       | PASS   | 7 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
