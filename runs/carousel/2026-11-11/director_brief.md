# Directors brief, carousel no. 74, November 11th, 2026

## The story (verified claims only: out/2026-11-11/claims.json, read every one; figures: out/2026-11-11/figures.json)
The City of Starbase posted notice that its City Commission will meet in public session on Wednesday, December 9th, 2026 at 7 p.m. at 48491 State Highway 4 to consider a Chapter 312 property tax abatement and a related Chapter 380 economic development agreement with Space Exploration Technologies Corp. (c4, c5, c6). SpaceX proposes to construct, own and operate "a gas-fired power plant and super-compute facility" (c1), with estimated capital investment for initial phases of approximately $24 billion and future expansions possible (c2). The site is an approximately 444-acre tract in Cameron County, just east of Brownsville between Boca Chica Blvd and the Port of Brownsville, now inside Starbase's corporate limits, in the Cameron County Enterprise Zone (c3, c8). The notice invites the public to attend and be heard (c7).
The Texas Tribune reports Brownsville commissioners voted unanimously at a six hour weekend special meeting in August to de-annex the land at SpaceX's request (c14, c9), in exchange for up to $220 million for water and wastewater projects (c15), with SpaceX's McCorkle telling them the deal was off the table unless approved that day (c16, c20). Starbase later annexed it (c10). Brownsville's own 90-day moratorium on data center applications took effect the week before the Tribune's November 10th story, and the site sits outside it (c9, c13). The gas plant could power the facility without a connection to the state grid (c11, c19), against the background of the Governor's August pause on data center grid connections pending audit (c18). SpaceX did not answer the Tribune (c12). Brownsville stands by the de-annexation (c17). A resident asked why the city was rushing on a Saturday (c21). The South Texas Environmental Justice Network announced a protest (c22). A Brownsville teacher said people need the jobs (c23).
Docket item tx-2026-0246, admitted this run. Place: Cameron County (Starbase, Brownsville). The next step a reader can take: attend and speak on December 9th.

## Hard facts for drawing
- Computed figures available (figures.json): capex_billion 24, acres 444, water_million 220, moratorium_days 90, days_to_hearing 28 (from this edition's date), water_share_pct 0.9 (the water ceiling as a percent of the capex estimate), capex_per_water 109 (floored), side_m 1340 (side of a square of the tract's area, a DRAWING SCALE only, never the tract's shape: no plat is in the record), ch312, ch380, hearing_day 9.
- $24 billion is an estimate for initial phases, never spent. $220 million is a ceiling ("up to"), never paid. Any comparison of the two says so.
- The notice says "super-compute facility". "Data center" is the Tribune's word. SpaceX has stated no purpose and no customer. Do not say AI training, xAI or anything not in the claims.
- Nothing is approved. The hearing is a consideration of proposed agreements. No abatement amount, term or percentage is in the record.
- Whether the site connects to ERCOT is not established; the plant "could" keep it off the grid. Never draw a grid connection or a disconnected island as fact.
- No plat, site plan, turbine count, turbine model, building design or rendering is in the record. Every object is drawn to illustrate. No SpaceX logo, rocket likeness or real person.
- The protest's date and place are not in the record.

## What is off the table (variety ledger and recent decks)
The last three decks were dark interiors: a code office and dais (no. 71), a dark lab (no. 72), a windowless machine hall of trays (no. 73). Last eight accents: dusk_gold (three times), primer rust, dusk_ember, bluebonnet, brass, comal_lit. Avoid those. Two of the last 24 decks were data-centers (Soluna Dorothy 3 on October 29th, with tower sections and stakes as 10 MW units, and the Tribune's data center water bores on October 25th). Do not draw a generic data hall, a server row or tower-section stacks. A hearing dais was drawn on no. 71 frame 8.
Suggested accent candidates from config/brand.yaml: signal_open #4FC79A (the green of a city limit sign), capitol_granite #9A3B2A, or comal #2A7A9E. The accent means ONE thing, which the director chooses.

## What the judges charged on the last three decks (give these to every pitch)
- Straight-on plan reliefs read as a keyboard, a chart or a flat waffle (no. 73 frames 3, 7; no. 72 frame 6). A relief must be raked three quarter with lit chamfers and casts, field falling to black at the edges, and its labels inside the safe margin (a label 23 px from the edge was charged on no. 73).
- Flat slabs and folder planes with no thickness (no. 71 frames 7, 8); hovering plates with no contact; primitive wire racks (no. 73 frame 8).
- A small subject over a dead grey panel (no. 71 frame 1). Kit person read as a mannequin (nos. 69 to 71): if a person appears, crop to hands or shoulder, side lit, under a fifth of the frame.
- Grey mid tones. Start dark (lastLight or floodlit, staged), one lit subject filling a third to two thirds.

## Craft refresh for this deck (Phase 1, out/2026-11-11/craft_refresh.md)
- A night exterior reads as one subject when the background equals the fog colour, a low ambient carries the field and one tight key with a soft edge carries the subject.
- A dark subject's top disappears into a dark field without a rim from behind aimed at its silhouette edge.
- Hard rim for metal, softer for organic surfaces.
- One subject as the anchor at a half to two thirds of the frame, with negative space reserved for the type.

## Routes (prompts/carousel_studio.md, read it)
txthree.js spatial scenes (a TXT.worlds world or a TXT.interior room) and/or txbench.js material reliefs. One material vocabulary, one light, one grade, one visual argument. Name every object by its kit model from knowledge/carousel/ARSENAL.md, for example `K.make('power_plant', { units: 2, cooling: 'acc' })`, `gas_peaker`, `modular_gas_genset`, `genset_block`, `city_limit_sign` (legend option), `hearing_dais`, `public_seating`, `podium`, `document_stack`, `riprap_bank` (ship channel bank), `shipping_container`, `water_tower`, `transmission_tower`, `road`, `caliche_road`, `pipe_rail_fence`, `chain_link_fence`. Anything the kit lacks (a survey stake, a water main section, a turbine exhaust stack) is said in metres and built once in the chassis as a kit model.

## The rotation rule (Phase 12 paragraph, verbatim)
The rotation rule changed on 2026-09-16. Read `knowledge/carousel/ILLUSTRATION_SYSTEM.md`, "THE DECK IS THE UNIT", and judge against that. If anything in your own definition disagrees with it, this paragraph wins. At most TWO of the same archetype in a row and at least THREE distinct, not five. ONE visual argument, ONE light, ONE grade for the whole deck, and no screen at all, because the print register is deleted. Judge whether the nine frames read as one deck and whether at least two continuity devices are doing real work, and treat a deck that turns the page nine different ways as a FAULT.

Name at least two continuity devices from ILLUSTRATION_SYSTEM.md (for example MOTIF_EVOLUTION, CAMERA_MOVE, VALUE_ARC). At least six of nine frames declare data_in_art: a figure from figures.json and the drawn parameter it sets.

## Read before pitching
knowledge/carousel/ILLUSTRATION_SYSTEM.md (THE STAGE before THE WORLD, THE ARTWORK CARRIES THE DATA, THE TEN LAYOUTS, What still fails), examples/bold-proof/README.md, examples/art-direction-proof/README.md, knowledge/carousel/TECHNIQUE_LIBRARY.md, knowledge/carousel/ARSENAL.md (KIT and ENGINE), prompts/carousel_studio.md, and the contact sheets of the last three decks: runs/carousel/2026-11-07/contact_sheet.png, runs/carousel/2026-11-08/contact_sheet.png, runs/carousel/2026-11-10/contact_sheet.png.
