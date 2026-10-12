# Run record, October 12th, 2026

Effort at wake: `high` (as the repo's settings carry it). The no-stall hook logged `armed` at
05:05:45 UTC and judged the session unattended from SessionStart, with the host's
`CLAUDE_CODE_SESSION_ATTENDED=0`. It refused nothing. The interim reading in Phase 17 measured 1,477
tool calls, none waiting on a human; 439 waited on the auto mode classifier, the longest 12.3
seconds. **That reading is interim.** Phase 19 takes the one that counts, and the email carries it.

## DISPOSITION: SHIPPED AT THE ROUND CAP, 6.854, UNDER THE 8.0 TOP RUNG, HARD FAILS REPAIRED IN ROUNDS 1 AND 2

Carousel no. 50, "UT San Antonio's flood sensor runs its AI on the device", is nine frames in one
staged floodlit world, a San Antonio low-water crossing on a wet night, declared once in
`assets/js/deck/2026-10-12-crossing.js`, with cold cobra head lamps as the practicals and beacon amber
#FFA21F as the one accent, lit only where the water has reached a sensor. The hero is the flood node
on eight of nine frames; frame 5 is the one canvas map. Every frame says it is drawn to illustrate
where it shows a scene, because the release names no site.

The panel: round 1, 6.52 under the 8.0 rung, one hard fail (the first comment's date lacked the
ordinal); round 2, 7.25 under the 7.7 rung, one hard fail (the first comment still carried the year
on a 2026 date); round 3, 6.854 at the cap, judges 6.88, 7.222 and 6.80, no hard fail. The art
median is 6.6 and the craft floor stood down at the cap. `claim_integrity` is contested (6.5, 8.3,
6.8). All three round 3 judges named frames 2 and 6 for the art.

**Named at the cap and not repaired, because past the cap only a hard fail may be.** Two round 3
judges charged the cover dek's "with no server" and frame 4's hook "No server in the loop" as
looser than the release: c5 scopes the server-free part to the node's own flood-risk call, and the
verified c10 says a central site runs server software and a second, larger model. Both judges
weighed it and filed no hard fail. The web edition carries c10 in full. It is the first thing the
next deck on this record should not repeat.

## The deck's work, in order

1. **Chassis and audition.** The crossing world (`assets/js/deck/2026-10-12-crossing.js`, floodlit,
   key az -135 el 48, ground #0C0D10, beacon amber #FFA21F) builds flood_node, rain_column,
   depth_gauge and low_water_crossing because the kit has none. The first art review asked for
   revisions twice before accepting: the first uniform 3D rain read as a screen, so the rain was lit
   only where a lamp catches it, faded above the lamp heads and thinned in the type band.
2. **Layout gates.** layout_check refused the first full render on detail (five frames), silhouette
   (three) and one accent short. Repairs were the world's own: the 3D rain, a lamp raking the box
   on frame 4, a stone relief on the county slab (frame 5), rain films and drops on the score
   column (frame 7), a closer cover camera with a lamp behind the lens, and a built station beside
   its parts (frame 6).
3. **Pixel review, three rounds.** Round 1 named type collisions on 3, 4 and 8, a leader through the
   dek on 3, the amber as a floodlight decal, a speckle texture on the map that read as a screen,
   and frame 6's primitives. Round 2 named label stacking on 7, footer crossings on 8 and 9, and
   the stone relief; round 3 left the cover's amber pool, frame 4's clean box and frame 6 open.
4. **Flow review, two rounds.** Round 1 asked for a reorder (radar to 2, the score column to 7, so
   the turn lands straight into the absences on 8), hero continuity through the middle frames and
   one sentence on 7's dek. All done. Round 2 shipped the sequence.
5. **Panel round 1, 6.52** (judges 6.59, 7.03, 6.42), under the 8.0 rung, one hard fail: the first
   comment printed 'September 28, 2026' without the ordinal. Repaired. Integrity repairs from the
   judges: the cover hook said 'on the post', a mounting the release never describes, so it says
   'on the device'; slide 3 says 'Drawn to illustrate' and its RAIN GAUGE label reads PRECIPITATION
   (c2's word); slide 2 leads with UT San Antonio's own stake (c18) before UT Arlington's radar
   finding; slide 8 and the caption name the release's target, small coastal towns (c19).
6. **Panel round 2, 7.25** (judges 6.91, 7.22, 7.51), under the 7.7 rung, one hard fail: the first
   comment still carried the year on a 2026 date. The release date moved out of each claim's
   document string into a `published` field, the block rebuilt to 'September 28th', and
   `compute.py` now reads the date from that field instead of a typed literal. Further repairs:
   'Drawn to illustrate' on 8 and 9, slide 9 cites c22 only, slide 2 no longer draws the node
   beside the radar columns (a link no claim makes), slide 6 names the Texas Coastal Management
   Program grant (c15), slide 3's leaders no longer cross, and two labels moved inside the margin.
7. **Panel round 3, 6.854, the cap.** What ships and what the judges still charge: frame 2's lit
   mid-grey floor and the plate under its source line; frame 6's exploded parts reading as
   primitives in a thin band; frame 7's floor patch left of the column and the films inside its
   glass; frame 9's dark pickup with the rain gauge over its cab; frame 3's small node; the cover's
   amber reading as a pool rather than a ring. Variety scored 6.2 to 6.5: another near-black staged
   deck carried by one hero, and a fourth institution release read for what it leaves out.
8. **After the cap, gates only.** `shipped_check` refused the caption ledger: the close repeated
   the last run's closing substance (a question the release leaves open), so the close now asks
   where the field record is, which is the menu's "name what is still not public" in the
   interrogative form `brand.yaml` requires; the structure label is the menu's "Zoom out". The
   ledger's derived exclusion lists were re-derived from its entries. Three counts in the topics
   entry's prose that no computation backed were cut. A storyboard acceptance item's planning
   threshold in L* was reworded. `house_style_check` split one 34 word sentence in tx-2026-0214's
   summary. No frame changed.

## The record, first

- **Worklist.** `docket_staleness.py` named 77 items due. `reverify.py` and a hand check stamped 49
  with checked notes (commit 4ff54470); 28 stayed unreachable behind the crawl boundary or a
  non-answering host and were not stamped. tx-2026-0152's quote was corrected to the source's text.
- **Corrected.** tx-2026-0141 and tx-2026-0167 now date UT San Antonio's flood sensor release
  September 28th, the date its own page carries (commit 36afad20).
- **A duplicate, disclosed.** tx-2026-0141 and tx-2026-0167 record the same release. Both stay;
  merging two public ids is a decision about published history, so it is named here for a
  maintainer.
- **Admitted.** tx-2026-0214, the federal motor carrier exemption that lets Aurora and other Level 4
  automated truck carriers use cab-mounted warning beacons instead of triangles (commit a2b54194).

## Sources that behaved differently from the registry

Appended to `knowledge/shared/SOURCES_FIELD_LOG.md` under October 12th: federalregister.gov's full
text link redirected to unblock.federalregister.gov, which robots.txt disallows, so the GovInfo PDF
was read instead.

## Instruments

All exit 0 in Phase 7. No instrument stopped.

## Engine defects named in two rounds or more (round rule)

- **Frame 6's exploded parts as primitives** (all three rounds). Recomposed once: a built station
  stood beside its parts and the camera came in; the parts still read as primitives. Queued as
  `crossing-models-built-in-chassis`.
- **Frame 2's lit floor** (all three rounds). The lamp moved out of frame and the floodlit rig's
  fill was ruled out in a scratch render; the floor stays lit by the world's key. Recomposed by
  removing the floating node.
- **Frame 7's floor patch** (rounds 2 and 3, and every audition recheck). Two scratch renders ruled
  out the stage pool, the rig fill and the rim light; the source is not found.
- **The amber as a pool** (frames 1 and 9, every round). The accent gate's presence floor can only be
  met at cover distance by the lit water at the post. Queued as `accent-presence-forces-a-pool`.

## Phase 16 notes

- The art review was refreshed and accepted by the flow critic after each change to its three
  frames. One refresh bound a review to identical PNG hashes after a no-op furniture declaration
  changed the slide HTML; queued as `type-spine-reads-html-only`.
- `tests/article_edition.mjs` needed `npm install` in this container; it then passed 825 reader
  checks. Its screenshots still write to `out/2026-09-18/` (queued `article-test-screenshots-fixed-path`).

## Did this run stop and wait for a human

Not on the interim reading: 1,477 calls measured, none waited on a human, and the hook refused
nothing.

## The weekly machine pass

**Due**, on one repeat offender. Run in this run, before the merge; its changes are the upgrade
commits on this branch and the email's machine lines.

## Queued for the next pass

Five new items in `knowledge/carousel/MACHINE_QUEUE.md`: `crossing-models-built-in-chassis`,
`rain-built-in-chassis`, `accent-presence-forces-a-pool`, `type-spine-reads-html-only` and
`canvas-map-detail-needs-material`. Repeats raised on `kmake-recentres-after-make` and
`scorer-thumb-path`.

## Craft memory

Added `light-the-weather-where-a-lamp-is` and `check-the-cover-noun-against-the-release`. Confirmed
`acceptance-items-need-a-floor`, `read-the-repair-at-feed-scale` and `a-paraphrase-can-outrun-its-quote`.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 22 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | PASS   | 9 slide(s), zero fails, zero warns |
| aggregates     | PASS   | 5 declaration(s), 8 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 7.87 MB, vector |
| score          | WARN   | 6.854 at the round cap after 3 round(s), the finished deck ships; 8.0 top rung, shortfall named |
| labels         | PASS   | 44 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 87 published string(s) read from one list, every universal names its set |
| verbatim       | WARN   | no dossier declares a `verbatim:` block, so no on-frame string was held to a quote, 2 slot note(s) |
| dossiers       | PASS   | 35,742 chars planned |
| caption        | PASS   | 143 words |
| craft floor    | PASS   | 9 frame(s), median 1282, floor 231 |
| plan vs render | PASS   | 12 of 49 acceptance item(s) checkable |
| texan          | WARN   | places Arlington, San Antonio / body NO / deadline yes / next step NO |
| absences       | WARN   | 8 of 10 scoped to a named document, 2 unscoped |
| numerals       | PASS   | 11 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
