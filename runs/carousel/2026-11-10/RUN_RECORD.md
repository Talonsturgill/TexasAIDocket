# Run record, November 10th, 2026 (carousel no. 73)

**SHIPPED AT THE ROUND CAP AT 6.97, 1.03 UNDER THE 8.0 TOP RUNG.** Three ladder rounds, three fresh judges each, no hard
fail in any round. The art median stood at 6.8 and the craft floor stood down at the cap. The median fell from round 1
(7.226) to round 2 (6.912), the repairs to frames 2, 5 and 8 changing what the judges charged rather than lifting it.

## The record, first

- **Wake.** Branch `claude/daily-2026-11-10`, cut from `origin/main` at d7c0fe89. Git identity and `core.hooksPath .githooks` set before the first write. Effort `high`. No `prompts/NEXT_RUN.md`. The local Ownership guard step went red once at wake while another writer was committing to `main`; its self-test and a rerun later passed.
- **Worklist.** `reverify --apply` read 238 URLs behind 1053 claims and stamped 117 items checked and unchanged, each note reworded per item. 35 quotes reported as gone, which the run read source by source rather than trusting the diff.
- **Moved.** ERCOT's November 5th Community Impact RFI update to the commission added four claims to the Governor's data center audit (tx-2026-0072). Texas premises confirmed with at least one New World screwworm detection rose from 66 to 69 on the federal page (tx-2026-0218). tx-2026-0109, 0137, 0222 and 0242 carry dated history lines for what moved on their pages. tx-2026-0125 (Frontera) gained its retirement claim and is not stamped, because its own source sits behind the docs.tacc boundary.
- **Admitted.** tx-2026-0245, TACC retiring Frontera after more than eight million jobs and a UT Southwestern lab's account of almost the same speed on eight Vista GPU nodes as on 64 Frontera CPU nodes. 12 claims from TACC's October 29th account as carried by HPCwire. Travis County only, since no fetched source states UT Southwestern's city.
- **Held.** Nothing new held.
- **Discovered and not admitted.** The scouts' remaining leads were already in the record or journalism only this run.

## Instruments

`gridwatch_pagecheck` exit 2, an advisory rather than a stopped instrument: November 1st is still missing from the series and ERCOT can't backfill it. Not presentation, so nothing for this run to fix. `waterwatch_pagecheck` 0. Discoverability gates all 0.


## Craft refresh
Focus: material reliefs and slabs that read flat at feed size (no. 72 frames 3, 5 and 6 a flat printed grid, no. 71 frame 7 flat slabs, no. 70 frame 8 a bar chart with weak casts). The last three decks leaned on TXBENCH reliefs and kit interiors.
- Raking light reveals topography only when the source is near parallel to the surface, and a narrow point source gives the sharpest casts while a diffuse one kills the contrast. Features running parallel to the beam vanish, so the key's azimuth is chosen against the relief's main edges. https://www.conservation-wiki.com/wiki/Raking_light and https://Www.Wikipedia.org/wiki/Raking_light
- Exaggerated shading for relief: exaggerate the height and keep sharp brightness transitions at ridges and valleys, adjusting the effective light locally so no area goes flat. https://pixl.cs.princeton.edu/pubs/Rusinkiewicz_2006_ESF/exaggerated_shading.pdf
- On a dark field a rim light behind the object separates dark materials from the void; adjust background brightness before raising light intensity, and give polished objects something bright and shaped to reflect. https://xo3d.co.uk/resources/3d-rendering/product-rendering/lighting-guide/ and https://www.creativebloq.com/3d/how-to-use-key-fill-and-rim-lighting-in-3d-art
- Volume in a quantity drawing earns its ink only when depth or height encodes the value; occlusion and shadows read as marks, so keep few units, large value differences, and casts that cannot be mistaken for data. https://www.juiceanalytics.com/design-principles/rarely-use-3d and https://arxiv.org/html/2406.06146v3

## Selection, and what shipped

tx-2026-0245. TACC retired Frontera in October after more than eight million jobs and more than seven years of production.
Jose Rizo-Rey's lab at UT Southwestern Medical Center typically ran a 5.3 million atom membrane fusion simulation on 64
Frontera CPU nodes at 43 nanoseconds a day, and says eight Vista GPU nodes gave "almost the same speed" after "a lot of
optimizations with GROMACS, with the help of people here at TACC." Horizon, the successor, is in its first phase of early
operations. Every TACC fact is read through HPCwire's off-the-wire reprints of TACC's releases, because tacc.utexas.edu is
off limits to this project. The comparison is one lab's account, never a benchmark, on every surface. UT Southwestern is
left unplaced because no fetched source states its city.

## Art

A MIX, in the chassis `assets/js/deck/2026-11-10-tray.js` (floodlit world, key at azimuth -60 and elevation 30, comal_lit
cyan meaning a Vista GPU node and nothing else). Spatial scenes in one windowless machine hall (1, 2, 6, 8, 9) and TXBENCH
reliefs (3, 4, 5, 7). The chassis builds `compute_tray`, `tray_tower`, `raised_floor` and `equipment_crate`, none of which
the kit has. The audition (cover, frame 3, close) was accepted by the `carousel-art-director` on the third reading and is
bound to the current digests. Two pixel rounds and one flow pass (predicted art 6.6) before the panel.

Panel repairs, all one change per named frame:
- Round 2. Frame 2 rebuilt as the whole open tray with its walls, bezel and a board with traces; frame 5's raised join
  band rebuilt as a fusion neck; frame 6 raised clear of the footer; frame 7's eight cells doubled in height with crisp
  casts; frame 8's plywood crate (read as a nightstand by two judges) replaced by the deck's own tower half filled with
  unlit trays and a back row of empty frames. c28's quote widened to place TACC at UT Austin; c34 added to bind the model's
  name to Rizo-Rey's own words; the caption's production note cut.
- Round 3. Frame 2's board taken toward black; frame 4's headline to "four SNARE complexes", the claim's own count;
  frame 5 pushed in 1.25x; the contact decals on 6 and 8 removed (their planes read as pale rectangles on the floor);
  frame 7's field bled off both sides; frame 8's floods tightened.
- Frames 1, 3 and 9 were never repaired, because they are the bound audition and a change unbinds it.

## Panel

| round | integrity | craft | reader | median | hard fail |
|---|---|---|---|---|---|
| 1 | 6.99 | 7.08 | 7.37 | 7.226 | none |
| 2 | 6.84 | 6.88 | 7.00 | 6.912 | none |
| 3 | 6.77 | 6.99 | 7.00 | 6.97 | none |

`panel.py` medians. The bar stepped 8.0, 7.7, then the cap. Holdouts the judges named late, none a hard fail, shipped as
they are:
- Frames 3 and 7, the deck's two count frames, read as flat charts in every round, straight on and in the grey middle.
  All three judges named both in round 3. Frame 3 is audition bound; frame 7's raking three quarter view is something a
  height field relief can't do, so the honest fix is a spatial scene.
- Frame 7's "860 compute nodes" label sits at x 23, inside the 80 px margin, after round 3 bled the field. Machine QA
  warned and the frame shipped as scored.
- Frame 5's neck still reads to two judges as two caps with a gap rather than one merge.
- Frame 8's tower frames read as wireframe primitives; frame 9 ships its two duller teal lowest bars.
- Story and stakes held at 5.5 to 6.5 in every round: no decider, no date for Horizon, no step for a reader, and the
  caption closes on a question. Two judges asked for frame 3's slot to carry how a Texas lab gets time on Vista or Horizon.
- Frame 9's headline "Frontera is dark. The work moved." was charged as unbounded by the integrity judge in rounds 2 and
  3. Its dek bounds it to one lab; the headline is audition bound and was not changed.
- Frame 2's two Xeons per node rests on c30's expansion nodes and c29's "same configuration", one step removed.

## Discoverability signoff
- og card: `og/tx-2026-0245.png` opened as an image. The headline wraps after whole words in four lines and ends "and a UT..." on a whole word.
- /questions/: twelve section questions read as a reader ("Who decides", "What happens next", "How the public can take part" and so on). Per-question answers NOT LOOKED AT this run.
- llms.txt Open right now: the Governor's data center audit (tx-2026-0072) leads, now carrying ERCOT's November 5th RFI update, then the Justice Department's comment window on the Frisco rent software judgment (tx-2026-0189).
- /sources/: the share reads 1470 of 1674 claims on a primary document across 416 documents from 182 publishers. tx-2026-0245's twelve claims are all HPCwire reprints of TACC releases, labelled primary for their text and journalism hosted, because tacc.utexas.edu is off limits. Publisher pages NOT LOOKED AT.
- /topic/: tx-2026-0245 is on `research-and-science`. Card count against beat page NOT LOOKED AT.
- /place/: tx-2026-0245 is on `county-travis` and the Austin metro hub. Hub count NOT LOOKED AT.


## Timing

`studio_clock.py --report`, minutes from wake: record 45.72, audition 74.4, art 104.27, review 156.66, panel 215.95,
package 237.74.

## Retro

- **Instincts.** Confirmed `a-paraphrase-can-outrun-its-quote` (slide 5's "the researchers call it" outran c13's
  quote), `read-the-repair-at-feed-scale` (round 2's repairs lowered the median) and `audition-frames-freeze-at-binding`.
  Added `a-plan-relief-count-reads-as-a-chart` and `read-the-speakers-words-before-naming`.
- **Queue.** Four new items (tray models built in the chassis, a contact decal drawn pale under a spot, a judge's dark
  field against the silhouette gate, panel_ready reading file times) and three repeats raised in place
  (`relief-plate-reads-as-a-tray` to 3, `audition-rebind-after-every-panel-repair` to 7,
  `prompt-audit-counts-agent-latency` to 8), committed in 4265483e.
- **Weekly machine pass (due on three repeat offenders, last pass November 8th).** Three changes, each its own
  `upgrade` commit. 12bb6eaf lifts a data hall into `assets/js/kit/industry.js` (`node_tray`, `node_rack` as a panelled
  enclosure with lit chamfers and dark empty slots, `access_floor`) at the judges' named fix for the week's top theme, a
  primitive where a kit model belongs (6 of 6 runs, 17 rounds); no. 73's chassis keeps its own models, so the shipped
  frames are unchanged. 03f80d8b changes the art doctrine from a plan view for any quantity to a parallel projection
  seen from a raking three quarter, on a census of 22 of 53 plan reliefs charged as charts against 21 of 136 spatial
  frames. b28c1a34 makes `panel_ready` accept a frame whose file times say stale only when its PNG, sources and render
  report match the bytes it last passed. Records in 10b0ba12. The run reran every verify command: `node --check`,
  `arsenal.py --check`, `print_ban.py --assets`, `panel_ready.py --self-test`, the census, `upgrades.json` parsing and
  `machine_due.py` (not due) all exit as stated; `examples/kit/sizes.py` exits 0 at 144 of 144 models. Proposals outside the lane:
  the routine's "parallel projection for any quantity" sentence (human), a GATE_LESSONS entry for the panel_ready change
  (human), `TXT.contact` under a spot (engine, human), and `prompt_audit.py`'s agent latency count (daily lane, not
  fixed this run).
- **Ledger check.** `ledger_check --date` refused today's topic prose for spelled counts the figures don't name; the
  counts are now numerals.
- **Prompt audit.** 1,585 calls measured, 63 counted as waiting. The top of the list is SendMessage and Agent dispatches at 3 to 25 s, the queued agent latency count (repeat 8), and no call has the shape of a human answering a dialog. The no-stall hook was armed at 05:03:41 UTC, judged the session unattended (the host's CLAUDE_CODE_SESSION_ATTENDED was 0) and refused nothing.

## Email

The payload is built by `gmail_draft.py` before the merge so CI's `email_check --all` reads it, and `email_check` exits 0 for this run and for all. It first refused the sources block as stale: the block still listed c16 to c20, c27, c31 and c32, which no frame or caption prints after the panel repairs, and missed c34. The block was rebuilt to the ids the deck prints, and TOP500's line went with c32. The Gmail draft itself is created after the merge.

## Merge

Written at Phase 18.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 34 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 5 warn(s) |
| aggregates     | PASS   | 19 declaration(s), 28 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 6.82 MB, vector |
| score          | WARN   | 6.97 at the round cap after 3 round(s), the finished deck ships; 8.0 top rung, shortfall named |
| labels         | PASS   | 68 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 79 published string(s) read from one list, every universal names its set |
| verbatim       | WARN   | no dossier declares a `verbatim:` block, so no on-frame string was held to a quote |
| dossiers       | PASS   | 33,023 chars planned |
| caption        | PASS   | 140 words |
| craft floor    | PASS   | 9 frame(s), median 585, floor 105 |
| plan vs render | PASS   | 9 of 48 acceptance item(s) checkable |
| texan          | WARN   | places Austin / body NO / deadline yes / next step NO |
| absences       | WARN   | 0 of 4 scoped to a named document, 4 unscoped |
| numerals       | PASS   | 18 numeral(s) over 9 frame(s), every one reachable |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
