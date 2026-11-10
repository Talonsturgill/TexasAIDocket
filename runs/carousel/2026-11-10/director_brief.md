# Directors brief, carousel no. 73, November 10th, 2026

## The story (verified claims only: out/2026-11-10/claims.json, read every one)
The Texas Advanced Computing Center at UT Austin published its account on October 29th of TACCSTER, its September symposium for Texas researchers. Frontera, for most of its life the fastest academic supercomputer in the United States, was retired in October 2026 after more than eight million jobs and over seven years of production, the longest run of any TACC system. Its successor Horizon (NSF Leadership-Class Computing Facility) is in its first phase of early operations: power infrastructure complete, exabyte storage in place, its AI-focused hardware being installed. Jose Rizo-Rey of UT Southwestern Medical Center (Dallas) studies synaptic transmission. His lab simulates membrane fusion: a vesicle, a flat bilayer and four SNARE protein complexes, 5.3 million atoms. On Frontera that ran on 64 CPU nodes at 43 nanoseconds per day. On TACC's Vista, eight GPU nodes gave "almost the same speed", after many GROMACS optimizations made with TACC staff. The simulation points to the "local detergent model": SNAREs act as a local detergent that mixes the hydrophobic interiors of the two membranes.
Docket item tx-2026-0245, admitted this run (tx-2026-0125 holds Frontera's queue closing). Places: Austin (Travis County) and Dallas (Dallas County).

## Hard facts for drawing
- THE VISUAL ARGUMENT AVAILABLE: 64 CPU nodes against 8 GPU nodes for about the same speed, a ratio a drawing can make physical (64 units against 8 units at one scale). Any ratio or derived figure printed must come from compute.py, never typed.
- "Almost the same speed" is Rizo-Rey's spoken account in TACC's release, not a benchmark. Never draw the two speeds as equal bars with a number on the Vista side; Vista's speed is not given as a figure.
- The molecular system (vesicle, flat bilayer, four SNARE complexes) may be DRAWN TO ILLUSTRATE, never as the lab's real structure or a real trajectory frame. Membranes are lipid bilayers: two leaflets of lipids with heads out, tails in.
- Any hardware fact (what a node is, node counts, where the machines sit) only if claims.json carries it.
- No real person's likeness. TACC's machine room is not to be depicted as a real photograph; a dark machine room drawn to illustrate is fine.

## What is off the table (variety ledger and recent decks)
Last eight decks: dark interior labs (foundry, AlphaFold plate), outdoor night scenes (west side block, weigh station, well pad, dock door, rig floor, Dallas street). Accents used in the window: bluebonnet (twice), dusk_gold (twice), primer rust, dusk_ember, brass/dust. Avoid those accents. research-and-science is the commonest beat in the window, and there were supercomputer decks on September 3rd (Texas A&M VISION) and September 7th (Frontera queues closing): the ART must not be a generic server row. A data center server row is the subject this record draws most. If racks appear, they appear because their COUNT is the claim (64 against 8), not as wallpaper.
Suggested accent, from config/brand.yaml: comal_lit #8FE0F0 (or comal #2A7A9E), meaning ONE thing, chosen by the director.

## What the judges charged on the last three decks (give these to every pitch)
- Kit person read as a mannequin (nos. 69, 70, 71). If a person appears, crop to hands or shoulder, side light, under a fifth of the frame.
- Flat slabs and flat printed grids: a relief that read as a bar chart or blinds (no. 70 frame 8), flat card slabs (no. 71 frame 7), a cell slab with no wall or cast (no. 72 frames 3, 5, 6). Grids of identical units at feed size read flat unless each unit has a lit edge and a cast.
- Small subject in the lower band; flat grey cylinders (no. 72 frame 7); plates hovering with ghost rims and no contact (no. 72 frame 8).
- Grey mid tones; overlit pale subjects. Start dark (lastLight or floodlit, staged), one lit subject filling a third to two thirds.

## Craft refresh for this deck (Phase 1)
- Raking light reveals relief only near parallel to the surface; a narrow source gives sharp casts; features parallel to the beam vanish, so choose the key against the relief's main edges.
- Exaggerate relief height; keep sharp brightness transitions at ridges and valleys.
- On a dark field a rim light behind the subject separates dark materials from the void; set background brightness before raising light.
- Volume in a quantity drawing earns its ink only when height or depth encodes the value; keep units few and value differences large.

## Routes (prompts/carousel_studio.md, read it)
txthree.js spatial scenes (a TXT.worlds world or a TXT.interior room) and/or txbench.js material reliefs (measured height, two or more materials, cast shadows, carrier over 30 percent of the frame). One material vocabulary, one light, one grade, one visual argument. Name every object by its kit model from knowledge/carousel/ARSENAL.md (server_row, server_rack, etc.), or in metres for anything the kit lacks (a lipid bilayer, a vesicle, a SNARE bundle, a compute node tray), which the chassis builds once as a kit model.

## The rotation rule (Phase 12 paragraph, verbatim)
The rotation rule changed on 2026-09-16. Read `knowledge/carousel/ILLUSTRATION_SYSTEM.md`, "THE DECK IS THE UNIT", and judge against that. If anything in your own definition disagrees with it, this paragraph wins. At most TWO of the same archetype in a row and at least THREE distinct, not five. ONE visual argument, ONE light, ONE grade for the whole deck, and no screen at all, because the print register is deleted. Judge whether the nine frames read as one deck and whether at least two continuity devices are doing real work, and treat a deck that turns the page nine different ways as a FAULT.

## Read before pitching
knowledge/carousel/ILLUSTRATION_SYSTEM.md (THE STAGE before THE WORLD, THE ARTWORK CARRIES THE DATA, THE TEN LAYOUTS, What still fails), examples/bold-proof/README.md, examples/art-direction-proof/README.md, knowledge/carousel/TECHNIQUE_LIBRARY.md, knowledge/carousel/ARSENAL.md (KIT and ENGINE), prompts/carousel_studio.md, and the contact sheets of the last three decks: runs/carousel/2026-11-06/contact_sheet.png, runs/carousel/2026-11-07/contact_sheet.png, runs/carousel/2026-11-08/contact_sheet.png.
