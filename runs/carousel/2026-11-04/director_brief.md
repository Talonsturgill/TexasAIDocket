# Directors room brief, November 4th, 2026 (carousel no. 68)

## The rotation rule (it travels with every brief)

> The rotation rule changed on 2026-09-16. Read `knowledge/carousel/ILLUSTRATION_SYSTEM.md`,
> "THE DECK IS THE UNIT", and judge against that. If anything in your own definition disagrees
> with it, this paragraph wins. At most TWO of the same archetype in a row and at least THREE distinct,
> not five. ONE visual argument, ONE light, ONE grade for the whole deck, and no screen at all,
> because the print register is deleted. Judge
> whether the nine frames read as one deck and whether at least two continuity devices are
> doing real work, and treat a deck that turns the page nine different ways as a FAULT.

Name at least two continuity devices from ILLUSTRATION_SYSTEM.md (`layout_check --require` refuses fewer).

## Read before pitching

- `prompts/carousel_studio.md` (two physical routes: `txthree.js` spatial scenes, `txbench.js` material reliefs, or a deliberate mix; three distinct visual arguments across the room, at least one drawing the evidence directly with a measured scale or changing material motif).
- `knowledge/carousel/ILLUSTRATION_SYSTEM.md`: THE STAGE first, then THE WORLD, THE SHOWSTOPPER TEST, THE TEN LAYOUTS, THE ARTWORK CARRIES THE DATA, and "What still fails".
- `examples/bold-proof/README.md`, `examples/world-proof/compare.webp`, `examples/figure-bearing/contact_sheet.webp`, `examples/art-direction-proof/README.md`.
- `knowledge/carousel/ARSENAL.md`, THE ENGINE and THE KIT. A model the kit has is never rebuilt from primitives. Name every object by kit model and options, e.g. `K.make('pump_jack', { crank: 40 })`. Kit models that fit this story: `pump_jack` (true linkage, crank in degrees), `oil_tank` (Permian tank battery with heater treater, separator, combustor), `pipe_rail_fence`, `ranch_gate`, `cattle_guard`, `caliche_road`, `semi_truck`, `pickup` if listed, `person`, `windmill`, `mesa`. Anything else is said in metres and built once in the chassis as a kit model.
- Worlds: start in `lastLight` (the house register, staged) or `floodlit`. Argue for anything else in writing.

## The weakest frames of the last three decks, as their judges named them (do not repeat these)

- No. 65 (Nov 1st), artwork 6.5: a toy robot arm of cylinders and boxes on a mid grey floor; a beige slab in the grey middle; stepped dome rings and a pale gradient; 72 relief dogbones read as an embossed calendar tile with a hard plate edge.
- No. 66 (Nov 2nd), artwork 6.4: a primitive monitor with a banded clip in the grey middle; a slab in a void with a dead lower third; labels on smudge plates and a small dog in a mid tone band; a boxy phone slab with no lens discs.
- No. 67 (Nov 3rd), artwork 6.5: twenty tractors in a band a quarter of the frame tall with an empty lower third; a kit truck cast in one gold mid tone with no ground; a gate cabinet as a plain box with a pale ball for a lamp; a material relief that read as a slab in a void with an empty field from y 680 to 1050.
- The repairs that failed across those decks: re-lighting a primitive object instead of replacing it with a kit model or cropping it out; small heroes made brighter instead of bigger. The fix that works: one subject filling a third to two thirds of the frame, camera low and close, the lower third occupied by lit ground and contact.

## The story (docket item tx-2026-0240, admitted this run)

Permian Resources, the Midland producer, filed its third quarter 2026 results with the SEC on November 4th (c4). It says its Production Operations team has deployed an AI-powered artificial lift monitoring system to increase runtime and optimize well performance (c1). Artificial lift is the pumping that lifts oil from a well once pressure alone won't; the pump jack is its most familiar form in West Texas (context for the art only; no claim defines it, so no slide may assert a definition). It says it is integrating proprietary subsurface data with large language models for development strategy, wellbore placement and drilling parameters in real time (c2). It credits power and compression projects with record runtimes (c18). The release gives NO measured result for either AI tool. It reports 457,528 boe/d, up 22% (c6), 208,029 bbl/d of crude (c7), its fastest well ever at over 2,700 feet per day (c8), $518 million capex (c9), about 560,000 net acres in West Texas and Southeast New Mexico (c10), concentrated in the core of the Delaware Basin (c11). Its 2025 10-K puts about 67% of net leasehold in Texas, 33% in New Mexico (c15), and names Reeves County, Texas for drilling, completion and water connection work (c17). Its own cautionary note lists "technological advancement, including artificial intelligence, machine learning and its application in our industry" among risks (c5).

Counter-image: on May 21st the Texas Tribune reported the Railroad Commission said it is not aware of any use of AI by oil and gas companies (c27), in an article where experts said AI is reshaping produced water handling (c28). 167 days separate that report from this release (computed, days_since_rrc).

Beside it: ExxonMobil's October 26th Permian post plans to automate more than half its unconventional drilling fleet by year-end 2028 (c20), says the technology could eliminate roughly one-third of high-consequence drilling incidents (c19), cites H&P's FlexRobotics demonstrations (c21), says handling heavy drill pipe has historically required workers on the rig floor (c22), and expects similar staffing on automated rigs (c23). The post does NOT use the words AI or machine learning: it is automation, and must be drawn and written as automation. It places nothing in Texas specifically (Permian spans Texas and New Mexico).

Claims: `out/2026-11-04/claims.json`. Figures (every numeral a frame draws or prints comes from here): `out/2026-11-04/figures.json`: boe_per_day 457528, qoq_pct 22, oil_per_day 208029, oil_share_pct 45.5, fastest_ft_per_day 2700, fastest_ft_per_hour 112.5, capex_musd 518, net_acres 560000, oil_target_2026 202.5, oil_4q_over 210, texas_lease_pct 67, nm_lease_pct 33, lease_acres_2025 480000, ai_tools 2, llm_uses 3, days_since_rrc 167, xom_technologies 50, xom_automate_year 2028, xom_target_mboe 2.5, xom_target_year 2030.

What the record does NOT hold, so nothing may draw it as fact: which wells or how many carry the monitor, any runtime or uptime number, the AI vendor or model, any Texas county other than Reeves, any ExxonMobil rig location, any well count. Every frame is drawn to illustrate; no real pad, rig or person is depicted.

Off the table from the variety ledger (last decks): floodlit weigh station and white tractor (no. 67), San Antonio streets and phone camera (no. 66), foundry robot arm and dogbone reliefs (no. 65), road paint stripes (no. 64). No deck in the 30 day window was set in the oilfield. Avoid the floodlit pad look of no. 67 if you pick floodlit; lastLight is the default and this story's natural light is the Permian at last light.

Six of nine frames must declare `data_in_art` naming a figure above and the drawn parameter it sets (THE ARTWORK CARRIES THE DATA).

Instincts handed down (from `instincts.py --top 5`): read every repair at 432px against the defect it was meant to cure; write every acceptance item so rendering NOTHING fails it; a claim's paraphrase can assert more than its quote; rebuild every derived artifact in the same commit; run house_style_check straight after admitting anything.

Craft refresh (Phase 1): dusk pump jack photographs separate the beam and horsehead as a crisp silhouette against a low warm seam with reflective wet ground in front (stock references, e.g. https://www.gettyimages.ca/detail/photo/pumpjack-at-dusk-in-the-permian-basin-royalty-free-image/1212606243); rim light at grazing angles is what separates a silhouette from its background (https://www.cryengine.com/docs/static/engines/cryengine-3/categories/1114113/pages/1048629).

## What to return

ONE complete treatment: a name, the visual argument in one sentence, the WORLD and why, the hero kit model(s) with options, nine frames each with its claim ids, its layout archetype (run the rotation through TXLAYOUT.check rules: at most two same in a row, at least three distinct, FULL_BLEED+CLOSE_CROP at least two, TYPE_AS_OBJECT at most once, four frames bleeding an edge), its subject named by kit model or metres, its shot (AERIAL/WIDE/MEDIUM/CLOSE/MACRO), its data_in_art figure and drawn parameter (six of nine at least), a draft hook of under ten words, and the route (txthree or txbench). Then the two or more continuity devices, the one accent and its one meaning, the hardest frame and its build risk, and how this differs from nos. 65, 66 and 67. No first person in hooks; no colons, semicolons or dashes; never "gap", "matters" or "pattern".
