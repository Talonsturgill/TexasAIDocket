# Carousel no. 74, November 11th, 2026: the city line

## The story, and what the fact check did to it

The City of Starbase gave notice that its City Commission will meet in public session on Wednesday, December 9th, 2026 at
7 p.m. at 48491 State Highway 4 to consider a Chapter 312 tax abatement and a related Chapter 380 economic development
agreement with Space Exploration Technologies Corp. (c4, c5, c6). SpaceX proposes a gas-fired power plant and super-compute
facility (c1), with capital investment for initial phases estimated at approximately $24 billion (c2), on an approximately
444-acre tract in Cameron County just east of Brownsville between Boca Chica Blvd and the Port of Brownsville, now inside
Starbase's limits (c3, c8). The public is invited to attend and be heard (c7). The Texas Tribune reports Brownsville
commissioners voted unanimously at a six hour weekend meeting to de-annex the land at SpaceX's request (c14, c9) for up to
$220 million in water and wastewater projects (c15), on an offer that would be off the table unless approved that day (c16,
c20). Starbase later annexed it (c10). Brownsville's 90-day moratorium on data center applications took effect the week
before the Tribune's November 10th story, and the Tribune says the project circumvents it (c9, c13). The plant could power the facility
without a connection to the state grid (c11, c19). The Tribune says the Governor directed grid operators in August to pause data center connection requests until the data centers could be audited (c18).

The fact check held it to its words. The notice says super-compute facility, and data center is the Tribune's word. $24
billion is an estimate and $220 million a ceiling, and the one comparison drawn (109) says so. Nothing is approved. No
plat, site plan, turbine count or building design is in the record, so the tract is drawn as a square of its area and
never its shape, and the plant is drawn to illustrate. Whether the site connects to ERCOT is not established.
Brownsville's own moratorium page refused the fetch, so the pause rests on the Tribune.

Docket item tx-2026-0246, admitted this run. Place: Cameron County.

## Why this treatment, and what was grafted

Base: THE LINE THAT MOVED. Every fact here is about which side of a line a piece of ground sits on, and a city limit is
the one legal object a Texan already knows as a physical thing, the green sign on two posts at the edge of town and the
lath and flagging of a survey crew. The deck draws the line with the tools that mark one. Grafted from THE MACHINE: the
plant seen beyond the line in its own pool (6) and the close in the public's room (7, 8). Grafted from THE MEASURE: the
tract's area at true scale (2) and the estimate stacked as 109 blocks of the water ceiling beside one block (3). Dropped: a county relief map
and a relief of the notice page (too close to the plan reliefs charged on nos. 72 and 73), a kit person (charged as a
mannequin on nos. 69 to 71), a 24 bay steel frame (reads as construction underway when nothing is approved), and the
kit power_plant at close range (a probe render read it as a pale boxy table at 432 px).

## The world, and the laws that hold it

`lastLight`, staged. The sun is just down over Brownsville, to the west. The key is azimuth -68, elevation 7, low on the
left, so every lit face looks left and every cast runs long to the right, east, onto the tract. The warm seam lies on the
city's side and the tract is already dark. The hearing room (7, 8) is dark around one lamp, its window on the left taking
the same last light. Type is light on the dark sky. A wash only darkens.

## Palette

salt crust bone #BDB6A4 (inside the pool only), tidal clay umber #3E352B, algal mat olive black #1F241C, saltgrass straw
#8C7B55, weathered pine lath #9C8460, galvanized steel #A9ADB0, copper #B87A4B, sodium seam #C98A4A, signal_open #4FC79A (as rendered #3FA07A)

The accent is brand.yaml's signal_open #4FC79A, measured as rendered under the deck's light and grade at #3FA07A, the green of a city limit sign, and it means ONE thing, a city limit as it stands
now. It sits on the sign face (1, 9), the flagging on the line (5, 6) and the square's edge (2). The hearing room and
the count carry none.

## The continuity devices

CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE, VALUE_ARC

1. **Motif evolution, the line.** The sign standing (1), the square drawn in green on the flats (2), the estimate stacked in blocks of the water ceiling (3),
   the old stake pulled from its hole (4), the flagged line run to the horizon (5), the line ending at the plant (6), and the sign again at
   night on the road to the meeting (9).
2. **Camera move.** 1 and 9 are the same sign from the same side, the second swung into the lane after dark. 5 looks
   north along the line from the tract, and 6 looks down the same line to what stands at its far end.
3. **Value arc.** The last seam is warmest on 1, the aerial 2 the darkest field with one green edge, the brightest pool on
   the
lone block (3), dusk going out across 4 to 6, the one lamp in the room (7, 8), and full night on 9 with the sign
   face as the brightest thing in the frame.

## The rotation

    FULL_BLEED  DIAGRAM  FIGURE_SCALE  CLOSE_CROP  SPLIT_HORIZON  OBJECT_AND_CAPTION  OBJECT_AND_CAPTION  CLOSE_CROP  FULL_BLEED

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | CLOSE, eye 1.25 m, 5.6 m off the sign on the far side of it, looking into the seam with the sign backlit, fov 34 | the kit city_limit_sign, prismatic green sheeting with an inset white border, galvanized U channel posts with domed bolts, rimmed on its top edge, on a caliche shoulder with saltgrass, TXT.contact at both posts |
| 02 | AERIAL, eye 700 m, 1,500 m back, fov 30, horizon in the top quarter | the tidal flats as a TXT.ground dirt surface with a green 4 m ribbon laid as a square of side_m metres, the kit road along its near side and the kit riprap_bank with black water along the far side, saltgrass and a far sodium seam over Brownsville |
| 03 | MEDIUM, long lens fov 22 from 75 m out and 15 m up, horizon on the upper third | 109 chassis unit_block models, 2 m precast concrete cubes with chamfered edges, lifting loops and form tie dimples, stacked six by six by three with one begun on top, and one alone in the pool, TXT.contact under both and TXT.weather grime at their bases |
| 04 | CLOSE, eye 0.72 m, 1.3 m from the stake looking down across it, fov 30 | one chassis survey_lath lying on cracked salt crust, weathered pine with a dark wet clay foot and limp faded flagging, beside the hole it came from, TXT.contact under it |
| 05 | WIDE, eye 1.6 m, looking north along the line, horizon at y 470, fov 34 | moratorium_days chassis survey_lath stakes 10 m apart with green flagging and a stringline running from the lower left to the vanishing point, every cast running right across the line, sodium streetlights along the far west seam, TXT.contact at every stake |
| 06 | WIDE, eye 3.2 m, long lens fov 6 down the line toward the unit side_m metres out | the kit gas_peaker at the far end of the flagged line, its enclosures and stack side lit by the low key in its own pool, a chassis survey_lath stake every 20 m with green flagging and a stringline leading to it, TXT.contact under each |
| 07 | MEDIUM, eye 1.2 m at the back of a TXT.interior hearing room, fov 38 | the kit public_seating, days_to_hearing padded chairs in rows facing the front, the kit podium and an empty kit hearing_dais beyond in one lamp's pool, the window on the left taking the last light |
| 08 | CLOSE, eye 1.3 m, 1.4 m from the lectern, fov 32 | the kit podium with its gooseneck microphone, a veneer body with a raked reading desk, lit by one lamp from above, TXT.contact on the floor |
| 09 | MEDIUM, eye 1.1 m in the lane, 9 m behind the sign, fov 42 | the cover's kit city_limit_sign, same seed, cropped by the right edge, its face the brightest thing in the frame, the kit road running east with days_to_hearing chassis pavement_marker reflectors stepping along the edge line into the black |

Showstopper frame: 05, the flagged line running from the lower left corner to the vanishing point, every stake throwing a
long shadow right across the line onto the dark tract, Brownsville's sodium lights strung along the last seam on the left.
Tonal arc: the warm seam behind the sign on 01, the darkest field on 02 with one green edge, the brightest pool on the
lone block on 03, dusk going out across 04 to 06, one lamp in the room on 07 and 08, and full night on 09 with the sign
face the brightest thing in the deck.
VALUE CUT: frame 7. The deck leaves the flats for the room where the public is heard.

---
```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: a green city limit sign on two galvanized posts, close and low on the caliche shoulder of a two lane road on the flats east of Brownsville, the last warm seam behind it on the left
  rect: [270, 560, 560, 790]
  bleeds: [bottom]
accent: '#3FA07A'
data_in_art: null
job: Put the line in front of the reader as an object they know, before a number is read.
claims: [c1, c3, c9, c10, c14]
numerals:
- {value_from: c3}
depth:
  eye: 1.25
  horizon: 1060
  cues: [CAST_SHADOW, FORM_SHADING, OCCLUSION, AERIAL, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'A low three quarter view. The sign face sits right of centre in the middle third, its feet on the lit shoulder between the footer''s two lines of type.', bands: 'Top third, the
    near black sky with the kicker, hook and dek. Middle third, the green face, its white border and the low seam on the left horizon. Bottom third, the two galvanized posts standing in the pool, the caliche
    shoulder lit warm in the pool, saltgrass tufts and the post shadows running long to the right.', focal: the green face and its lit top edge}
art:
  technique: physically based render of the kit city_limit_sign on a TXT.ground caliche shoulder in the lastLight world, staged on the sign
  why_this_technique: the claim is about a city line, and the sign that marks one is a real object at a size every reader knows
  palette: signal_open green, galvanized steel, caliche bone, saltgrass straw, the sodium seam
  value_structure: Lightest is the green face's lit edge and the seam. Darkest is the sky above and the ground away from the pool. Frame median L* planned at 6.
type:
  hook: "Brownsville let the land go."
  dek: "Brownsville took the land out of its city limits at SpaceX's request, and Starbase annexed it. Starbase will now consider a tax break for a gas-fired power plant and super-compute facility on the site, which its notice puts at about 444 acres."
  labels: []
verbatim: []
acceptance: [the sign face owns at least a sixteenth of the frame area and the frame fails if no sign is drawn, both posts cast a shadow to the right on the ground, the sign face does not cross a glyph
    of the hook or dek, the frame's median L* at 432 px is 30 or lower, the sky shows above the sign, the sign face spans at least 380 px wide at full size and the frame fails if no city_limit_sign is drawn]
risks: ['a green face can wash pale under its own glow, so the glow is held low and measured at the probe']
```

```yaml
slide: 2
layout: DIAGRAM
primary_image:
  subject: the tidal flats east of Brownsville from 700 m up, a square of the tract's area drawn as a green ribbon on the ground between the road and the ship channel bank
  rect: [0, 820, 1080, 440]
  bleeds: [left, right]
accent: '#3FA07A'
data_in_art: {figure: side_m, drives: 'the side of the green square in metres, laid at true scale on the ground'}
job: Show how much ground 444 acres is, at true scale, between the two places the notice names.
claims: [c3, c10]
numerals:
- {value_from: c3}
- {computed_by: 'compute.py:side_m'}
depth:
  eye: 700
  horizon: 330
  cues: [LINEAR_PERSPECTIVE, TEXTURE_GRADIENT, AERIAL, RELATIVE_SIZE, OCCLUSION]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'A high oblique. The green square sits in the middle of the frame foreshortened into a wide rhombus, the road running along its near edge and the channel bank along its far edge,
    the horizon high.', bands: 'Top third, the type over the dark sky and the far seam. Middle third, the far edge, the channel and the bank. Bottom third, the green near edge and corner of the square lit
    in the pool, the road''s lit shoulder and its shadowed ditch, saltgrass tufts casting short shadows and salt crust ridges in the flats, all darkening away from the pool.', focal: the square's green
    near corner}
art:
  technique: physically based render of a TXT.ground dirt plain with the kit road and kit riprap_bank and a ribbon square in the lastLight world
  why_this_technique: an area is only understood against things of known size, and a true scale aerial with a road and a ship channel gives the reader those
  palette: tidal clay umber, salt crust bone, the green ribbon, black channel water, the sodium seam
  value_structure: Lightest is the green edge and the seam. Darkest is the channel and the flats away from the pool. Frame median L* planned at 6.
type:
  hook: "About 444 acres, east of Brownsville"
  dek: "Between Boca Chica Blvd and the Port of Brownsville, now inside Starbase's limits, in Cameron County. The square holds the tract's area at true scale. The notice gives its area, not its shape."
  labels: ["Boca Chica Blvd", "Port of Brownsville", "1,340 metres a side"]
verbatim: []
acceptance: [the green square shows all four sides and spans at least 60 percent of the frame width, the road runs along the near side and water along the far side, the horizon shows in the top third, no
    label crosses the square's edge, the tidal flats ground and the green ribbon square are drawn and the frame fails if either is missing, the tidal flats with the green square own at least half of the
    frame height]
risks: ['a square could be read as the tract''s outline, so the dek says it is not']
```

```yaml
slide: 3
layout: FIGURE_SCALE
primary_image:
  subject: a stack of 109 precast concrete blocks, six by six by three with one more begun on top, and one identical block standing alone in front in the pool, on the tidal flat at last light
  rect: [100, 560, 800, 600]
  bleeds: []
accent: none
data_in_art: {figure: capex_per_water, drives: 'the number of blocks built into the stack, beside one block for the water ceiling'}
job: Make the estimate and the ceiling one comparison a reader can count, and say they are not the same kind of money.
claims: [c2, c15]
numerals:
- {value_from: c2}
- {value_from: c15}
- {computed_by: 'compute.py:capex_per_water'}
depth:
  eye: 20
  horizon: 120
  cues: [CAST_SHADOW, FORM_SHADING, OCCLUSION, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'A long lens from a raking three quarter. The stack fills the middle of the frame, its left face lit and its right face in cool shadow, the lone block in front and right in the
    pool, the horizon on the upper fifth.', bands: 'Top third, the type over the dark sky and the thin seam. Middle third, the stack with its joints and the one block begun on top. Bottom third, the lone
    block in the pool with its chamfers lit, its lifting loops and its cast running right across the clay toward the stack''s longer shadow.', focal: the lone block in the pool}
art:
  technique: physically based render of the chassis unit_block stack and lone block on a TXT.ground dirt flat in the lastLight world, staged on both
  why_this_technique: a ratio is two quantities at one scale, and 109 blocks against one let the reader see it before counting it
  palette: precast concrete, steel lifting loops, tidal clay, the warm seam
  value_structure: Lightest is the lit left face of the stack and the lone block. Darkest is the stack's right face and the sky. Frame median L* planned at 10.
type:
  hook: "About $24 billion, and up to $220 million"
  dek: "The notice estimates approximately $24 billion for the first phases. SpaceX agreed to give Brownsville up to $220 million for water and wastewater. The estimate is about 109 times that ceiling. One is an estimate and one a payment, so this is scale and not a price."
  labels: ["one block, up to $220 million", "109 blocks,<br>about $24 billion"]
verbatim: []
acceptance: [every block in the stack's lit face shows its joints at 432 px, the stack and the lone block each cast a shadow to the right, the count is built from capex_per_water in the frame's own code,
  the frame's median L* at 432 px is 30 or lower, the stack of blocks spans at least 520 px wide at full size, exactly one block stands apart from the stack and the frame fails if it is missing]
risks: ['blocks for money can read as an installation, so the dek says each block stands for the ceiling and is drawn to illustrate']
```

```yaml
slide: 4
layout: CLOSE_CROP
primary_image:
  subject: one weathered pine survey lath lying on cracked salt crust beside the hole it was pulled from, its foot dark with clay and its old flagging limp
  rect: [0, 700, 1080, 560]
  bleeds: [left, right]
accent: none
data_in_art: null
job: Carry the Saturday vote, the offer made for that day only, as one pulled stake.
claims: [c14, c16, c20, c21]
numerals:
- {value_from: c14}
depth:
  eye: 1.05
  horizon: 200
  cues: [CAST_SHADOW, FORM_SHADING, OCCLUSION, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'Looking down across the ground. The fallen lath crosses the lower half on a diagonal, cut by the left edge, the dark hole beside its foot, the cracked crust running away into the
    dark above it.', bands: 'Top third, the type over the dark crust. Middle third, the crust''s cracks and channels lit by the low key. Bottom third, the fallen lath''s lit face and dark clay foot, the
    hole with crumbs at its lip, and the salt crust with grit and cracks in its tone under the cast.', focal: the clay dark foot of the fallen lath beside the hole}
art:
  technique: physically based render of the chassis survey_lath on a TXT.ground caliche crust with the chassis tidal flat albedo in the lastLight world
  why_this_technique: a vote that moved a line on paper is drawn with the object that marks a line in the ground
  palette: pine, clay umber, salt crust, faded flagging
  value_structure: Lightest is the fallen lath's lit face. Darkest is the hole and the sky. Frame median L* planned at 10.
type:
  hook: "\"Why are we rushing this?\""
  dek: "A Brownsville resident asked it at the Saturday meeting, the Tribune reported on August 31st. SpaceX's Sheila McCorkle told commissioners the offer would be off the table unless approved that day. They voted unanimously to de-annex."
  labels: []
verbatim: []
acceptance: [the fallen lath crosses at least 40 percent of the frame width, a dark hole sits beside the fallen lath's foot, 'the lath carries no green, since green means the line as it stands now', the
    frame's median L* at 432 px is 30 or lower]
risks: ['a pulled stake could suggest surveyors moved something, so the dek says the vote moved the line']
```

```yaml
slide: 5
layout: SPLIT_HORIZON
primary_image:
  subject: a line of flagged survey lath stakes on a stringline running from the lower left corner north to the vanishing point across the flats, Brownsville's streetlights strung along the last seam on
    the left
  rect: [180, 560, 640, 790]
  bleeds: [bottom]
accent: '#3FA07A'
data_in_art: {figure: moratorium_days, drives: 'the number of stakes built along the line, one per day of Brownsville''s moratorium'}
job: Show that Brownsville's pause stops at a line, and the tract is on the other side.
claims: [c9, c10, c13]
numerals:
- {value_from: c13}
depth:
  eye: 1.6
  horizon: 470
  cues: [LINEAR_PERSPECTIVE, CAST_SHADOW, RELATIVE_SIZE, AERIAL, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'Standing on the tract looking north. The line enters at the lower left and runs to the vanishing point on the upper third, every stake''s shadow falling right across it.', bands: 'Top
    third, the type over the dark sky. Middle third, the horizon with the seam and the streetlights on the left. Bottom third, the three nearest stakes large with lit faces and green flagging, their contacts
    in the clay and long shadows running right across the stringline onto the dark tract.', focal: the nearest three flagged stakes and their shadows}
art:
  technique: physically based render of the chassis survey_lath line on a TXT.ground dirt plain with grass scatter in the lastLight world, staged on the line
  why_this_technique: a boundary is a direction in space, and a line run to the horizon under a raking key shows which side is which
  palette: pine, green flagging, clay umber, saltgrass straw, sodium lights
  value_structure: Lightest is the seam and the near flagging. Darkest is the sky and the tract right of the line. Frame median L* planned at 14.
type:
  hook: "Brownsville's pause stops at the line"
  dek: "Brownsville's 90-day moratorium on data center applications took effect the week before the Tribune's November 10th story. The Tribune says the project in Starbase circumvents it."
  labels: ["one stake per day<br>of the pause"]
verbatim: []
acceptance: [at least 20 stakes are distinct at 432 px, every near stake casts a shadow to the right, the horizon sits in the upper half, the frame's median L* at 432 px is 30 or lower, the nearest stake
    stands at least 300 px tall at full size]
risks: ['a thin stake vanishes at feed size, so the flagging is sized up and the near stakes carry the frame']
```

```yaml
slide: 6
layout: OBJECT_AND_CAPTION
primary_image:
  subject: the flagged line running away across the flats from the lower left to a gas-fired generating unit standing at its far end in its own pool, side lit by the low key
  rect: [340, 690, 680, 660]
  bleeds: [bottom]
accent: '#3FA07A'
data_in_art: {figure: side_m, drives: 'the length of the flagged line in metres, from the camera to the generating unit at its far end'}
job: Show what would stand there and that it could make its own power, without drawing a grid connection either way.
claims: [c1, c11, c18]
numerals:
- {value_from: c18}
depth:
  eye: 3.2
  horizon: 900
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, TEXTURE_GRADIENT, AERIAL, FORM_SHADING]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'Frame 5''s line seen down its length through a long lens. The stakes enter at the lower left and step toward the unit, which stands right of centre on the horizon in its pool,
    the world behind gone dark.', bands: 'Top third, the type. Middle third, the unit and its stack against the dark sky. Bottom third, the nearest flagged stakes large at the lower left with their contacts
    in the clay, saltgrass lit in the key''s pool along the line, and the stringline stepping toward the unit.', focal: the unit's lit flank and stack at the end of the line}
art:
  technique: long lens physically based render of the kit gas_peaker at the end of a chassis survey_lath line in the lastLight world, staged on both
  why_this_technique: the notice names a gas-fired plant, and a rendered unit at true distance across the line shows what the record names without inventing its design
  palette: galvanized and painted steel, pine, green flagging, clay umber
  value_structure: Lightest is the unit's lit face. Darkest is the sky and the near ground. Frame median L* planned at 6.
type:
  hook: "It could make its own power"
  dek: "The Tribune reports the gas-fired plant could power the facility without connecting to the state grid. It says the Governor had grid operators pause data center connection requests in August, pending audits. Drawn to illustrate."
  labels: []
verbatim: []
acceptance: [the generating unit stands at least 220 px tall at full size, no transmission tower or line is drawn, at least 20 flagged stakes lead from the lower left toward the unit, the frame's median
    L* at 432 px is 30 or lower, the kit gas_peaker is drawn and the frame fails if it is missing, the gas_peaker spans at least 260 px wide at full size]
risks: ['one unit could be read as a turbine count, so the dek says drawn to illustrate']
```

```yaml
slide: 7
layout: OBJECT_AND_CAPTION
primary_image:
  subject: the back of a hearing room, rows of empty padded chairs facing an empty dais and a lectern in one lamp's pool, the window on the left taking the last light
  rect: [0, 640, 1080, 430]
  bleeds: [left, right]
accent: none
data_in_art: {figure: days_to_hearing, drives: 'the number of chairs built, one per day from this edition to the hearing'}
job: Turn from the land to the room where the public is heard, and count the days until it meets.
claims: [c4, c5, c6, c7]
numerals:
- {value_from: c4}
depth:
  eye: 1.2
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, OCCLUSION, CAST_SHADOW, RELATIVE_SIZE]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'From the back of the room. The chair rows fill the lower half, the lectern and dais beyond in the lamp''s pool, the window a cool panel on the left wall.', bands: 'Top third, the
    type over the dark back wall. Middle third, the dais and lectern in the pool. Bottom third, the backs of the nearest chair rows with their padded tops catching the lamp''s edge, their legs and contacts
    on the concrete floor in shadow.', focal: the empty lectern in the pool}
art:
  technique: physically based render inside TXT.interior of the kit public_seating, podium and hearing_dais, dark around one lamp
  why_this_technique: the next step a reader can take is a meeting, and an empty room with one lit lectern is that step
  palette: oak veneer, charcoal upholstery, concrete floor, the lamp's warm white
  value_structure: Lightest is the pool on the lectern. Darkest is the back wall and the near chairs. Frame median L* planned at 8.
type:
  hook: "28 days to be heard"
  dek: "Starbase's City Commission meets Wednesday, December 9th. It will consider a Chapter 312 tax abatement and a Chapter 380 agreement with SpaceX."
  labels: ["one chair per day until the hearing"]
verbatim: []
acceptance: [exactly days_to_hearing chairs are built, the lectern stands in the brightest pool of the frame, the frame's median L* at 432 px is 30 or lower, no chair crosses a glyph of the hook or dek,
  the kit public_seating rows are drawn and the frame fails if they are missing, the kit public_seating rows own at least a third of the frame height]
risks: ['empty chairs can read as a cemetery of seats, so the lectern pool leads the eye forward']
```

```yaml
slide: 8
layout: CLOSE_CROP
primary_image:
  subject: a speaker's lectern with a gooseneck microphone over its raked reading desk, lit from above by one lamp
  rect: [270, 560, 560, 790]
  bleeds: [bottom]
accent: none
data_in_art: null
job: Give the reader the notice's own invitation, in its words.
claims: [c17, c22, c23]
numerals: []
depth:
  eye: 1.3
  horizon: 420
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'Close on the lectern from the public''s side, its desk and microphone in the upper middle, its body cropped by the bottom edge.', bands: 'Top third, the type. Middle third, the
    raked reading desk and the microphone head. Bottom third, the lectern''s raked veneer body with its plinth, its grain catching the lamp on the left edge and its contact on the floor in shadow.', focal: the
    microphone head over the desk}
art:
  technique: physically based render of the kit podium inside TXT.interior, one lamp
  why_this_technique: to be heard is to stand at a microphone, and the lectern is the public's object in the room
  palette: oak veneer, black steel, warm lamp
  value_structure: Lightest is the desk's lit edge and the microphone's rim. Darkest is the room behind. Frame median L* planned at 8.
type:
  hook: "Brownsville stands by its vote"
  dek: "The city said it decided on the information and circumstances presented at the time. The South Texas Environmental Justice Network has announced a protest over air, water and energy bills. A Brownsville teacher told the Tribune many people need jobs and SpaceX has contributed to them."
  labels: []
verbatim: []
acceptance: [the lectern owns at least a fifth of the frame area, the microphone head is lit against the dark, the frame's median L* at 432 px is 30 or lower, the kit podium is drawn and the frame fails
    if it is missing, the podium stands at least 600 px tall at full size]
risks: ['a lectern alone could read as stock, so the microphone and the veneer are modelled at kit detail']
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: the cover's green city limit sign after dark, cropped by the right edge, its face the brightest thing in the frame, the two lane road running east with reflectors stepping along the edge line
  rect: [430, 640, 650, 710]
  bleeds: [right, bottom]
accent: '#3FA07A'
data_in_art: {figure: days_to_hearing, drives: the number of raised pavement markers built along the edge line}
job: Close on the road to the meeting, with the date and the place a reader needs.
claims: [c4, c7]
numerals:
- {value_from: c4}
depth:
  eye: 1.1
  horizon: 690
  cues: [LINEAR_PERSPECTIVE, TEXTURE_GRADIENT, RELATIVE_SIZE, OCCLUSION, CAST_SHADOW]
  subject_at: {X: 0, Z: 0}
composition: {structure: 'In the lane behind the sign. The sign stands close on the right, cut by the right edge; the road runs to a vanishing point left of centre with its reflectors stepping away.', bands: 'Top
    third, the type over the night sky. Middle third, the sign face and the far road. Bottom third, the near lane''s worn asphalt and edge line, the first large reflectors catching light, and the sign''s
    posts and contact on the shoulder.', focal: the green face}
art:
  technique: physically based render of the kit city_limit_sign and kit road with chassis pavement_marker reflectors in the lastLight world after the seam, staged on the sign and the road
  why_this_technique: the deck opened on this sign and closes on it, turned toward the meeting, so the reader leaves with the place and the date
  palette: signal_open green, asphalt, amber reflectors, black sky
  value_structure: Lightest is the sign face. Darkest is the sky and the verge. Frame median L* planned at 4.
type:
  hook: "Starbase hears the tax break December 9th"
  dek: "7 p.m., 48491 State Highway 4. The notice invites interested persons to attend and be heard on the proposed agreements."
  labels: []
verbatim: []
acceptance: [the sign face is the brightest region of the frame, at least 12 reflectors are distinct at 432 px, the reflector count is built from days_to_hearing in the frame's own code, the frame's median
    L* at 432 px is 30 or lower, the sign face spans at least 300 px wide at full size and the frame fails if no city_limit_sign is drawn]
risks: ['reflectors can dim to nothing outside the pool, so they carry a small emissive return']
```

