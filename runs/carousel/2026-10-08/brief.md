# Directors' brief, October 8th, 2026 (read this whole file)

## The story (docket item tx-2026-0205)
Claims: out/2026-10-08/claims.json, c1 to c40 are this story. Every fact a frame states cites a claim id.
- TxDOT launched the first phase of Project Nexus at Fort Worth Alliance Airport (Perot Field, AFW) on
  September 10th, 2026 (c1, c15, c21). Selected for the federal eIPP in March (c4, c5). Eight projects,
  more than 30 proposals, 26 states (c5 to c7). Texas partners Archer, BETA, Joby, Wisk (c9). Regional
  flights Dallas, Austin, San Antonio, eventually Houston (c8).
- First phase: traditional aircraft, helicopters and fixed-wing planes (c13). The initial flights carry
  NO PASSENGERS and collect data and validate routes (c14). Three years in phases (c16). Next: medical
  supplies or organs between rural facilities and Austin and San Antonio medical centers (c17). Last:
  passengers, air taxi across the Texas triangle (c18).
- The FAA will use the data to write new regulations (c12). More test flights planned through the year (c23).
- At the kickoff: BETA's ALIA and Joby's S4 demonstrated (c20). Merlin, an invited guest by its own
  account (c25), says it demonstrated autonomous takeoff and landing and AI-powered air traffic control
  communications with its Merlin Pilot (c26), narrated by its CEO (c27), framed as reducing pilot
  workload (c28). Its release calls its expectations of capability and performance forward-looking (c31).
  Its photo: a Cessna Caravan at Alliance Airport (c32, c33). Joby's J208, a Cessna 208B Caravan with
  Joby's autonomous flight technology, flying coast to coast, was to stop at AFW on September 10th (c36).
  Joby's S4 was described as piloted (c39). Dallas Innovates reports a 2029 air taxi goal (c40, reported only).
- NOT KNOWN (rejected, never stated as fact): whether a pilot was aboard Merlin's Caravan; how the
  demonstration performed; that TxDOT or the FAA named Merlin; that Wisk flew. An absence printed on a
  frame must name the documents it is absent from (TxDOT's release, the FAA's release, Merlin's release).
- The angle to argue: two Caravans that fly themselves came to the state's air taxi kickoff, by their
  makers' accounts, while the state's own first phase asks for data and no passengers. What a reader
  can and can't know from the documents.

## The world and the hero (already built, Phase 10.5 chassis: assets/js/deck/2026-10-08-nexus.js)
- World `lastLight` (the house register, STAGED): az -104, el 6, the sun just down in the west, a near
  black sky with one warm seam, a pool of light where the subject stands, the world behind gone dark.
  Light type on the dark field. Washes only darken.
- HERO: `turboprop_caravan`, a kit model built in the chassis to 208B proportions (about 12.7 m long,
  15.9 m span, 4.5 m tall), white with a navy cheat line, UNMARKED, drawn to illustrate (no livery, no
  registration, neither Merlin's nor Joby's). Options: prop stopped|disc, lights true|false (red, green
  nav lights, red beacon, landing lights), pod, pitch (nose up degrees for rotation or climb).
- Other chassis models: `airfield_lamp_row` (edge lamps: runway white, caution amber, taxiway, threshold
  green, end red), `windsock`, `control_tower`. Chassis primitives: NX.runway (asphalt, paint, lamps),
  NX.apron (concrete ramp), NX.infield (dry grass), NX.grass (scatter).
- Kit models available (knowledge/carousel/ARSENAL.md, THE KIT): `person`, `pickup`, `sedan`,
  `warehouse` (a hangar stand-in), `city_skyline` (dallas, houston, austin, san_antonio at dusk),
  `hospital` (with helipad), `live_oak`, `mesquite`, `ranch_house`, `transmission_tower`, interior models.
- Accent: comal_lit #8FE0F0, the ONE accent, on three to six frames. A probe render of the model is at
  out/2026-10-08/tmp/probe/render/slide-01.png (Read it).

## Laws (read these files): knowledge/carousel/ILLUSTRATION_SYSTEM.md (THE STAGE, THE WORLD, THE DECK IS THE
UNIT, THE ARTWORK CARRIES THE DATA, THE PRIMARY IMAGE LAW, THE TEN LAYOUTS, What still fails),
knowledge/carousel/TECHNIQUE_LIBRARY.md, knowledge/carousel/SLIDE_DOSSIER_SPEC.md (CRAFT PLAN),
examples/bold-proof/README.md, examples/art-direction-proof/README.md.

THE ROTATION RULE: The rotation rule changed on 2026-09-16. Read knowledge/carousel/ILLUSTRATION_SYSTEM.md,
"THE DECK IS THE UNIT", and judge against that. If anything in your own definition disagrees with it, this
paragraph wins. At most TWO of the same archetype in a row and at least THREE distinct, not five. ONE hero
object, ONE light, ONE grade for the whole deck, and no screen at all, because the print register is
deleted. Judge whether the nine frames read as one deck and whether at least two continuity devices are
doing real work, and treat a deck that turns the page nine different ways as a FAULT.

At least six of nine frames carry a figure from the claims IN THE ART (data_in_art): a count drawn as that
many rendered units, a span drawn to scale. Candidate figures: 3 phases over 3 years (c16), 8 projects (c5),
more than 30 proposals (c6), 26 states (c7), the 4 named partner companies (c9), 4 cities (c8), 2 Caravans
(c32, c36), 0 passengers in phase one (c14), September 10 to 14 Joby campaign (c34), the sixth location (c3).

Instincts the machine has confirmed: read every repair at 432px against its defect; write every acceptance
item so rendering nothing fails it; measure each frame's median L* against its declared value; make every
count name the set it counted.

Variety: accents of the last eight decks were bluebonnet (twice), highway green, bench green, dusk_ember,
magenta, dusk_gold, survey pink. Worlds of the last decks were daylight places (noon channel, golden field,
blue hour hospital). Do not repeat a wide daylight place.

House rules for any copy you suggest: no colons, semicolons, em or en dashes; never "cannot"; never the words
gap, gaps, matters, pattern, patterns; no sentence starting with And or But; no first person; ordinal dates.
