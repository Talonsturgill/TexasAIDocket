# Directors' brief, carousel no. 76, November 13th, 2026

## The story (docket item tx-2026-0072, statewide, ERCOT)
On November 5th, 2026 ERCOT gave the Public Utility Commission a PRELIMINARY summary (c1, c2) of the Data Center State and
Community Impact RFI, the questionnaire the Governor's audit set off. ERCOT issued it to 465 loads (c3). 433 of 465 (93%)
submitted, covering about 177 GW (about 97%) of requested interconnection capacity (c4); 417 on time, 16 late (c5); 32 Medium
Load responses not submitted (c6). All 245 Large Loads, 75 MW or greater, responded (c7) and they are about 94% of requested
capacity, about 166 GW (c8). 33 projects ask for more than 1 GW each and hold 36% of capacity (c9). Every load zone has
requests; West Texas holds the plurality, 41%, 73 GW (c10). By zone (429 reviewed loads, NOIE zones excluded, a load's zone
may change at interconnection, c15, c16): West 88 Large, 39 Medium, 73 GW (c11); South 72, 38, 49 GW (c13); North 69, 85,
45 GW (c12); Houston 14, 24, 10 GW (c14). Respondents answered 83% of nearly 67,000 questions (c17). THE LARGEST SHARE OF
UNANSWERED QUESTIONS WAS COOLING: many projects had not determined their final cooling configuration (c18). N/A ran about
16% for Large Loads and 19% for Medium (c19); projects due 2028 or later answered N/A 30% more often (c20). About 95% of
facilities will do no crypto mining, 175.9 GW (c21); 22 report mining, 20 of them Medium Loads (c22). Final report targeted
December 10th (c23, c37). Separately, ERCOT's Batch Zero verification reviewed 257 developers' responses, about 5,140
questions (c24), is sending second RFIs to 80% of developers with a 5 business day deadline (c25, c26), must finish this
month to report on December 10th (c27), and names four recurring problems: affiliate documentation, site control,
long-lead equipment, financial security (c28 to c31). The September 14th notice went to developers of data centers of 25 MW
and larger (c32, c33), was due October 12th (c34), and warned non-responders would be reported to the PUC and the Governor
(c35). The commission's calendar lists an open meeting on December 17th (c38).
The REJECTED claims: the per-row cooling and water N/A percents can't be quoted, so no frame may print or draw 37, 45, 21 or
29. The cooling finding is a SENTENCE (c18), not a number.

## The honest counter-image
Every figure is self-reported by developers and preliminary. Nothing here says how much water any data center will use.
The thing the developers most often could not say is how they will cool the building.

## Off the table (variety ledger, last 30 days). Read ledger/carousel/artwork.json for the full entries.
- No. 60, October 25th, the SAME questionnaire from the other end: a cast iron return plate, a threaded bore per facility, a
  brass hex plug in each that answered. NO BORES, NO PLUGS, NO "slot filled for each that answered" metaphor, no cast iron.
- No. 75 (Nov 12) a parked lot of stand-in cars at last light with a gold stripe; no. 74 (Nov 11) tidal flats, survey laths,
  precast blocks, a city limit sign; no. 73 (Nov 10) compute trays in a floodlit machine hall; no. 72 (Nov 8) a black plate
  lab with tubes and plates; no. 71 (Nov 7) a house and a truck camera at night; no. 70 (Nov 6) a rig floor.
- A data hall seen as a whole building has been the subject of several October decks; if you use the kit data_center, the
  frame must explain the claim through it (an empty cooling yard, a roof with no coolers), not show a building for its own sake.

## What the judges charged the last three decks (actual weakest frames, all three judges each time)
- no. 75 frame 8: a cab interior with the wheel beside the figure, grey door panel, no road. Frame 5: TXBENCH relief read as
  a flat mid-grey slab with a stair-stepped cast and a banded dead bottom. Frame 3: leaders ending on dim cars.
- no. 74 frame 4: a flat plank, low-poly clods, mid-tone crust. Frame 6: a pale primitive a fifth of the frame on the horizon.
  Frame 2: a flat ribbon outline with nothing of known size.
- no. 73 frame 7: a uniform dark-grey field bleeding off both edges, the subject tiny. Frame 3: a straight-on plan that read
  as a keyboard. Repairs that failed: re-lighting a primitive; moving a camera without changing what the frame draws.
- artwork_craft has been the lowest criterion (6.6 to 6.8). Craft refresh this morning (out/2026-11-13/tmp/craft_refresh.md):
  stair-stepped casts are shadow map texels (tight frustum, bigger map, small normalBias); raking light is one narrow source;
  a dark subject on a dark field needs a rim or a lighter surface under it; keep the rig to key, rim and one catch.

## Instincts the ledger confirms (instincts.py --top 5)
- Read every repair at 432px against the defect it was meant to cure.
- A claim's own paraphrase can assert more than its quote. (Every frame here says preliminary where the claim does.)
- Write every acceptance item so that rendering NOTHING fails it.
- Rebuild every derived artifact in the same commit as the thing it derives from.
- Run house_style_check straight after admitting anything to the record.

## The rotation rule (travels with the brief)
The rotation rule changed on 2026-09-16. Read `knowledge/carousel/ILLUSTRATION_SYSTEM.md`, "THE DECK IS THE UNIT", and judge
against that. If anything in your own definition disagrees with it, this paragraph wins. At most TWO of the same archetype in
a row and at least THREE distinct, not five. ONE visual argument, ONE light, ONE grade for the whole deck, and no screen at
all, because the print register is deleted. Name at least two continuity devices from ILLUSTRATION_SYSTEM.md.

## The laws you plan to
- prompts/carousel_studio.md: two physical routes, txthree spatial scenes and txbench material reliefs, or a mix. At least six
  of nine frames physical; five stand in a world (TXT.sky), a room (TXT.interior) or a measured relief.
- THE STAGE: start in lastLight (or floodlit). Dark field, one subject a third to two thirds of the frame in a pool of light,
  light type on the dark, a wash may only darken. Mean deck mid-tone share at most 0.35.
- At least six frames declare data_in_art: a figure from the list above that sets a drawn parameter (a count of instanced
  things, a length, a height). Parallel projection for quantities, perspective for scenes.
- Kit first: name every object by its kit model and options from knowledge/carousel/ARSENAL.md (THE KIT, THE ENGINE). The kit
  has data_center, chiller, cooling_tower, access_floor, server_rack, node_rack, substation, power_transformer,
  transmission_tower, machine_pad (an empty taped bay), structural_frame, warehouse, people, interior rooms, landscape. A model
  it lacks is built once in the deck chassis in kit conventions; say in metres what it is.
- No place is named by the story beyond West, North, South and Houston load zones; the closing frame must carry a next step
  (December 10th report, December 17th open meeting).
- House rules for any copy you propose: ordinal dates month first, no dashes, no colons or semicolons, no first person, can't,
  never gap, matters, pattern. Every numeral from a claim.
