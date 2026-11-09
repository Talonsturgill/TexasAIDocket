# Directors brief, carousel no. 72, November 8th, 2026

## The story (verified claims only: out/2026-11-08/claims.json, 28 claims, read every one)
Texas A&M AgriLife scientists in College Station (Department of Biochemistry and Biophysics, Gohil lab) repurposed Google DeepMind's AlphaFold-Multimer as a classifier and ran it on every pairing of a curated list of 1123 human mitochondrial proteins (c1, c2, c5, c7). 630,003 possible pairs screened, 2,895 likely interactions catalogued (c3, c4, c9: 2895 interactions involving 1004 proteins). A pair counts as likely when its mean ipTM score clears 0.5, which on the authors' test set gives 67% recall at a false discovery rate of about 15% (c8, c10); the paper also states 85% precision (c11, medium) and ~40% of true positives at 90% precision (c12). 57% of the predictions were in no existing database (c14, "more than half" c13). 85 previously uncharacterized proteins got their first probable partners (c15). Extended to 11 eukaryotes (c16). Lab work guided by the predictions nominated the coenzyme Q metabolon and mapped the copper delivery pathway to cytochrome c oxidase (c17, c18). About two years of lab experiments confirmed SEVERAL predicted partnerships in yeast and human cells (c19); no count of pairs tested exists. Predictions posted free as MitoMatch (c20, c21). Nearly 30% of mitochondrial proteins carry disease-linked mutations (c22). Honest limits: cures may be far off (c23); the method can't give binding affinity (c24); many pairs may only occur inside larger complexes (c25). Compute: Texas A&M High Performance Research Computing (c26). Paper published August 25th; the university release is November 5th (do not imply the paper is new).
Docket item tx-2026-0244. Place: College Station, Brazos County. No deadline, no public process; the next step a reader can take is MitoMatch being free to any researcher.

## Hard facts for drawing
- 630,003 is exactly the count of distinct pairs among 1123 proteins (a half matrix, a triangle). A drawing may use that geometry; any ratio or share printed must be computed by code in compute.py from the claims (no number typed).
- No protein structure from the paper is in the claims. Any protein shape is DRAWN TO ILLUSTRATE, never a real structure. No real lab, instrument or person likeness.
- "Several" confirmed. Never draw a count of confirmed pairs.

## What off the table (variety ledger and recent decks)
The last six decks were all SPATIAL SCENES at night outdoors (west side block, weigh station, well pad, dock door, rig floor, Dallas street) with two or three TXBENCH reliefs; accents used: dusk_gold (twice), primer rust, dusk_gold tape, dusk_ember, bluebonnet. Avoid another exterior night street/yard deck and those accents. research-and-science is already the most common beat in the window (7 of 24), so the ART must carry variety. Recent Texas A&M decks: no. 57 (language model study) and no. 65 (Aggie AI Foundry, copper hearth and alloy buttons). Do not reuse a copper hearth, a lab bench of domes, or a robot arm.

## What the judges charged on the last three decks (carousel_studio: give directors the weakest frames)
- Kit person read as a mannequin, front lit, at the face's own scale (nos. 69, 70, 71). If a person appears, crop to hands or shoulder, side light, under a fifth of the frame.
- Boxes and slabs: cold box facades, rounded blocks, flat card fans, folders with no thickness, a relief that read as a bar chart or as blinds (nos. 69 to 71).
- Reliefs of round objects read as dials or coins (queue: relief-of-round-objects-reads-as-dials, pipe-ends-read-as-coins); a county relief read as a flat card; relief cylinders read flat.
- Grey mid tones and a horizon band; overlit pale subjects. Start dark (lastLight / staged), one lit subject filling a third to two thirds.

## Routes (prompts/carousel_studio.md, read it)
txthree.js spatial scenes (a world or a TXT.interior room) and/or txbench.js material reliefs (measured height, two or more materials, cast shadows, carrier >= 30% of frame). A mixed deck is allowed and an orthographic relief deck is allowed. At least six of nine frames physical; at least five placed (TXT.sky, TXT.interior or a measured TXBENCH.relief). Three-frame audition: cover, the HARDEST interior frame (evidence, draws a computed quantity), close (consequence, different composition from the cover).

## The rotation rule (travels with every brief, verbatim)
> The rotation rule changed on 2026-09-16. Read `knowledge/carousel/ILLUSTRATION_SYSTEM.md`,
> "THE DECK IS THE UNIT", and judge against that. If anything in your own definition disagrees
> with it, this paragraph wins. At most TWO of the same archetype in a row and at least THREE distinct,
> not five. ONE visual argument, ONE light, ONE grade for the whole deck, and no screen at all,
> because the print register is deleted. Judge
> whether the nine frames read as one deck and whether at least two continuity devices are
> doing real work, and treat a deck that turns the page nine different ways as a FAULT.
Name at least two continuity devices from ILLUSTRATION_SYSTEM.md.

## Instincts (instincts.py --top 5)
- Read every repair at 432px against the defect it was meant to cure, because a repair can be worse than the defect.
- Write every acceptance item so that rendering NOTHING fails it, not just so that rendering too much fails it.
- A claim's own paraphrase can assert more than its quote, and every surface downstream inherits the excess.
- Rebuild every artifact DERIVED from a thing you just changed in the same commit that changes it.
- Run house_style_check straight after admitting anything to the record.

## Craft refresh (this run)
out/2026-11-08/tmp/craft_refresh.md: silhouette first then colour block then detail; negative space inside an outline; a narrow rim behind the subject separates it on a dark field, sharp for metal, soft for organic; Isotype: more units at one size in aligned rows, never a stretched unit.

## Read before pitching
knowledge/carousel/ILLUSTRATION_SYSTEM.md (THE STAGE, THE WORLD, THE DECK IS THE UNIT, THE ARTWORK CARRIES THE DATA, What still fails), knowledge/carousel/ARSENAL.md (THE ENGINE, THE KIT, LIBRARIES), knowledge/carousel/TECHNIQUE_LIBRARY.md, prompts/carousel_studio.md, examples/art-direction-proof/README.md, examples/bold-proof/README.md, knowledge/shared/TEXAS_DESIGN_DOCTRINE.md.
