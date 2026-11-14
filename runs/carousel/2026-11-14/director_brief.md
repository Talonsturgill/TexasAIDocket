# Director brief, carousel no. 77, November 14th, 2026

## The story (verified claims, out/2026-11-14/claims.json; docket item tx-2026-0247)

Texas Tech's Whitacre College of Engineering received an additional Texas Semiconductor Innovation Fund award "of over $19 million" (c1), announced November 13th, 2026 (c2). It will help Texas Tech "establish a next-generation computing cluster in Lubbock" (c3). The cluster is NOT built and no install date is given (c4). A cluster is servers "designed to function as a single unified system to handle massive, parallel workloads" (c5). The project will "integrate artificial intelligence (AI) with high-fidelity simulation data and experimental results" (c6) to "shorten development cycles for next-generation semiconductor devices and materials" (c7). The dean says Texas Tech "will be one of the first universities to have access to the newest generation of Nvidia chips to power the cluster" (c8). Roland Faller leads the team (c9). Planned work includes "AI-driven materials discovery and modeling" (c10) and "AI-enabled epitaxial growth of ultrawide-bandgap semiconductors" (c11). Conventional design "relies heavily on physics-based modeling" which can be computationally intensive (c12). President Schovanec thanked Governor Abbott and state leaders (c13). Earlier awards from the same fund: a clean room and wide/ultrawide bandgap work for harsh environments (c14); $12 million in January toward a clean room (c15) that Texas Tech matched for a $24 million project (c16); roughly $4.5 million in May for wide and ultrawide bandgap research (c17). The fund is administered by the Texas CHIPS Office in the Office of the Governor (c18), created by the Texas CHIPS Act in 2023 (c19).

What the record does NOT have: chip model, node or GPU count, cluster size, power draw, building, site, install date, a count of the research team, any result. Nothing may draw or print those. "Over $19 million" is a floor, not an exact value, so no sum or ratio may treat it as exact. The story's place is Lubbock (Lubbock County, South Plains). texan_check at selection: places Lubbock / body NO / deadline NO / next step NO, so the deck carries its score on art and on the closing frame.

## The rotation rule (travels with every brief)

> The rotation rule changed on 2026-09-16. Read `knowledge/carousel/ILLUSTRATION_SYSTEM.md`,
> "THE DECK IS THE UNIT", and judge against that. If anything in your own definition disagrees
> with it, this paragraph wins. At most TWO of the same archetype in a row and at least THREE distinct,
> not five. ONE visual argument, ONE light, ONE grade for the whole deck, and no screen at all,
> because the print register is deleted. Judge
> whether the nine frames read as one deck and whether at least two continuity devices are
> doing real work, and treat a deck that turns the page nine different ways as a FAULT.

Name at least two continuity devices from ILLUSTRATION_SYSTEM.md.

## Read before pitching

- prompts/carousel_studio.md (two physical routes: txthree spatial scenes, txbench material reliefs; mix allowed)
- knowledge/carousel/ILLUSTRATION_SYSTEM.md: THE STAGE, THE WORLD, THE ARTWORK CARRIES THE DATA, THE TEN LAYOUTS, What still fails
- knowledge/carousel/ARSENAL.md: THE ENGINE and THE KIT. Name every object by its kit model and options. Useful here: crop_rows (cotton), cotton_module, grain_elevator, caliche_road, windmill, structural_frame, machine_pad, server_rack, node_rack, document_stack, desk, laptop, person (people family). A thing the kit lacks (a wafer, an epitaxy reactor, a crystal layer stack) is built once in the chassis, sized in metres.
- examples/bold-proof/README.md, examples/art-direction-proof/README.md, examples/figure-bearing/storyboard.md

## Exclusions (the last decks, do not repeat)

- no. 73 (November 10th, TACC Frontera): node trays and racks as the hero. Do NOT make a rack, tray or data hall the hero of this deck. A rack may appear at most as a small supporting element.
- no. 74 tidal flats with survey lath; no. 75 a parked lot of crossovers; no. 76 a cooling yard of pads, reels, a copper bus pack and a grated trench relief.
- Last three decks all used staged lastLight exteriors plus one relief. A different balance is welcome (more relief, or interiors).

## Known engine defects to compose AROUND (machine queue, unfixed)

- lastLight horizon steps into a hard band where sky meets ground fog (no. 76 frames 1, 6, 7, 8, 9). Prefer cameras that keep the horizon out or high, or interiors.
- Copper under lastLight reads as wood or brick. Avoid copper heroes.
- Emitter sprites draw nothing in the snapshot, and stage fog swallows basic emitters. Use MeshBasic emitters with fog false.
- Long lens on a textured ground smears into streaks.
- A sunk model needs a ground cut (no. 76's cutGround helper exists in assets/js/deck/2026-11-13-coolingyard.js).
- Kit bake collapses an InstancedMesh to its first instance. Use separate meshes merged per material.
- Last judges' weakest frames: an orthographic relief on a mid-tone field read as a floor vent (no. 76 frame 5); a flat untextured slab (no. 74 frame 4); kit mannequins beside objects.

## Craft refresh (this morning)

Brushed metal reads through anisotropy and grain direction, not colour. Relief depth reads when height-derived normals are paired with a cavity term darkening recesses next to raised features, plus self-shadowing. A rim light separates a silhouette from a dark field and is overused if every frame carries one.

## Instincts the machine has confirmed (top 5)

1. Read every repair at 432px against the defect it was meant to cure.
2. A claim's own paraphrase can assert more than its quote.
3. Write every acceptance item so that rendering NOTHING fails it.
4. Rebuild every derived artifact in the same commit as the thing it derives from.
5. Run house_style_check straight after admitting anything to the record.

## House rules for any string you propose

No em or en dashes, no colons or semicolons, never "cannot", no sentence opening with And or But, no first person, never gap/gaps/matters/pattern/patterns. Ordinal dates month first, no year for dates in 2026. No numeral that is not quoted in a claim or computed.

## What to return

ONE complete treatment: title, one-sentence visual argument, world (from the THE WORLD table, argued; lastLight is the default to argue away from), material vocabulary, the hardest frame and why, nine frames each with layout archetype, subject (kit model and options or metres), route (txthree or txbench), the claim ids it carries, the figure it draws (data_in_art, at least six frames), shot (AERIAL/WIDE/MEDIUM/CLOSE/MACRO, no shot more than three frames), and the closing frame's next step or honest limit. Two continuity devices.
