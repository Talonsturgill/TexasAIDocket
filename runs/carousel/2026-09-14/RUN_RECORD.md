# Carousel no. 24 — September 14th, 2026

**The audit turned out to be a form.** Panel median **7.118**, spread 0.228, over the 6.7 bar,
no hard fails standing. Two were raised in round 1 and both were closed, in three rounds.

## The record

Two items admitted, `tx-2026-0156` and `tx-2026-0157`, taking the docket to 135 items and 742
claims. Five movement notes on `tx-2026-0093`, `0147`, `0144`, `0024` and `0107` were rewritten
from boilerplate into item-specific prose. `tx-2026-0120` was re-verified and stamped, the
account answering this run and still carrying the sentences quoted from it.

One candidate was held rather than admitted, and the promote gate is why: `tx-2026-0157`'s
summary tripped the first-person check on the bare "I" in "Helios I". The summary was reworded to
avoid standalone roman numerals. The claims keep the verbatim project names.

## The deck

Nine frames on ERCOT's Batch Zero eligibility verification. 43 verified claims from seven
documents, five official and two a company published about itself. 11 rejections and one declared
absence.

**The story is the gap between the size of an order and the size of an instrument.** Texas ordered
a comprehensive verification and audit of every data center advancing through the interconnection
process. What arrived is a questionnaire, due in ten business days, carrying a notarized
attestation from each of three parties, submittable only by the transmission provider, locked once
sent. Seventeen large loads at 6,608 MW of modeled five year peak have finished every other ERCOT
process and hold no approval to energize.

Measured value arc, on `panel_ready.ARC_GRID`: 6.0, 84.4, 4.1, 57.2, 7.4, 3.8, 3.8, 60.4, 5.2
against a plan of 8, 80, 8, 58, 9, 6, 4, 62, 6. Every frame inside one Munsell step. Deck median
5.6, spread 80.6, accent on four frames.

## Three things measured rather than reasoned about

**A FRAME'S MEDIAN IS DECIDED BY ITS RESERVE BANDS AND ITS SKY BEFORE ITS ART GETS A VOTE.** Frame
6 came back at 3.8 against a planned 14, the only miss over a step. The first diagnosis was that
its yard was too dark and a second measurement said otherwise before any of it was written down.
`tmp/bands.py` reports each frame's median twice, whole-frame and art-band, and frame 6's art band
read 4.4 where every other scene frame read 8.9 to 9.5. So the yard WAS the darkest thing in the
deck and the caliche pad under the substation was printing as nothing. It was fixed on its own
terms, a graded plane with a scraped shoulder, worn wheel tracks and depth-sized gravel. **The art
band went from 4.4 to 10.7, the strongest of any scene frame. The frame median moved by 0.0.**
Frame 6 reserves 680 px of 1,350 for type and its night sky is another 406, so 80 per cent of it
is page ground by construction. The plan moved to 6 only after that was demonstrated, and the pad
stayed, because it was a real defect in the image and fixing it buying nothing on the gauge is the
finding rather than a reason to undo it.

**A FIGURE OUTSIDE THE FRAME PASSES EVERY GATE THIS PRODUCT HAS.** Frame 1's person was at X -13,
which at that frame's camera and Z 9 projects to x -644, off the left edge of a 1080 px frame. The
cover's entire true-scale argument was missing. `layout_check --require`, `qa.py`,
`plan_render_check`, `craft_floor`, `bespoke_check` and a pixel critic all passed it, because every
one of them measures what IS inside the rect and none asks whether something the dossier declared
is in it at all. Two of three scoring judges found it independently, on three frames at once.

**AND MOVING IT INTO FRAME BROKE THE THING THE FRAME EXISTS FOR.** The first repair put her at 9 m
in front of a building at 30 m, so she rendered at 184 px beside a 16 m wall and the frame told a
reader the hall was about 3.4 m tall. Round 2 caught that and it is the better lesson: a frame
whose job is to give a size can be repaired into giving a wrong one, and "the figure is visible
now" is not the same check as "the ratio is true". She stands at 27 m, 48 px, inside her own
declared band, and the judge measured the wall a reader reads off the picture at 13.3 m.

## Two things that were about to be published and were not

**A fabricated email address and a fabricated attachment line, on frame 2.** "Questions to
BatchZero@ercot.com" and "Attachment, the dispute form the notice names" were set in the same
serif as two verbatim quotations, inside a drawn facsimile of a real ERCOT notice, on the frame
whose whole argument is what a document does and does not say. No claim in this run carries an
email address or mentions an attachment. Both came off. The dossier's declared dek had said the
notice carries "a contact address", which is what invited them, and that phrase came out too.

**An unsourced date, on frame 8.** "SEPTEMBER 8TH" was set as the Galaxy release's dateline and no
claim carries it. It came off.

Both were found by pixel critics reading the render rather than by any gate.

## Two relations that were refused

A caption candidate put the Caspian project inside Dickens County by adjacency. `c37` locates the
HELIOS campus there and **no claim locates Caspian anywhere.** The two sentences were separately
true and the join was a fabrication. The candidate lost on it.

The winning candidate asserted "the next open meeting is September 17th". `c41` says the
commission's calendar carries an open meeting on that date and says nothing about ordering, and
`c19` shows the same feed carrying a December 17th one. The phrase came out of the caption and out
of the deck's closing frame, which carried it too.

## The crawl boundary

`gov.texas.gov` now disallows ClaudeBot host-wide. Measured this run: 403 to ClaudeBot, 200 and
822 bytes to a browser, and the robots file names ClaudeBot with `Disallow: /`, against a sources
registry that says the host serves no robots file. A fact-checker had already fetched three claims
from it in good faith before the finding existed. **All three were dropped rather than published.**
The Governor's directive reaches the deck only through `c21`, which is ERCOT restating it in its
own presentation. The whole of it is in `knowledge/shared/SOURCES_FIELD_LOG.md`.

## Carried into the next run, not fixed here

- The cover kicker sets "BATCH ZERO, DICKENS COUNTY" over a population the record never locates in
  that county, and the caption sets the seventeen beside Galaxy's Helios base load classifications,
  which the release itself files under projects approved before Batch Zero. Two judges flagged the
  adjacency and it stands.
- Frame 5's label reads "Or the load comes off Batch Zero" where `c4` says MAY be removed. The
  neighbouring label was explicitly protected to keep "requested", so this one is inconsistent
  with the frame's own care.
- Frame 9 names a room and no city, so a Texan outside Austin cannot reach the next step from what
  is printed. The reachable half, the filing archive, is in the first comment only.
- Frame 3's blank nameplate rules carry the deck's load bearing absence and nothing on that frame
  says the seventeen are unnamed, so the absence lands on frame 2 alone.
- The deck's accent is four different treatments across four frames, under a structural law that is
  specifically about the accent.
- `brand.yaml`'s `visual.constellation` lists five FIXED elements and a judge found three on every
  frame and two on none. Either the config is stale or it is a fourth instance of the pattern
  `CLAUDE.md` names, a rule stated in config with a surface keeping its own copy.

## Upgrades

Two proposals, both in `knowledge/carousel/UPGRADE_BACKLOG.md`, neither made here.

`fetch()` does not work on a `file://` slide and the engine's own contract documents it as the way
to load committed geodata. Frame 7 failed on it and `examples/demo-deck/slides/slide-02.html`
fails identically, which is the engine's own demo, so the documented API is broken rather than one
slide getting it wrong. `XMLHttpRequest` works first time. The fix is one line in `render.py` and
one in `SKILL.md`, both under `.claude/`, which the host stops a session on at every edit.

The caption room's exclusion windows are one shipped entry behind, so this run's writers were
briefed to close on the substance the previous run had just shipped. One of them did, and the
critic caught it at the judging step rather than the briefing step, which is the one place
`CAPTION_CRAFT.md` says the room must never be told no. The window is one function and it is
`upgrade` lane, and the lists it derives are STORED in `captions.json`, which is `daily` lane, so
it is one edit in two lanes and not a change a self-upgrade phase gets to make.

## Permissions

`prompt_audit.py` over 1,023 tool calls: **none waited on a human.** No file was written under
`.claude/` and no lane stamp was written anywhere.
