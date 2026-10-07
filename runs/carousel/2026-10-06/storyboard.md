# Storyboard, 2026-10-06
# "Taylor's terms, in feet"

## The story, and what the fact check did to it

The City of Taylor is considering a proposed agreement with Big Watt Digital and PowerHouse Data
Centers for annexation and development of Taylor Technology Campus, formerly Project Mustang (c1), a
664-acre project with data center facilities and on-site power generation (c2) between FM 112 and US
79, immediately east of the city limits (c3). The City Council votes on it at its October 8th meeting
(c4). The developers withdrew their annexation and zoning application on September 3rd (c5, c6). The
city says that without the agreement the land stays in unincorporated Williamson County, which has no
zoning authority (c8), and that the city would have no authority over any aspect of the project (c9).
With it, the land is annexed (c10) and held to written terms: noise capped at 65 dBA or the
pre-development level, whichever is greater, against the state's 85 dBA the city lists without it
(c12, c13, c14). Dark Skies lighting (c15). A closed cooling loop on reclaimed water with an initial
fill of 1.575 million gallons (c17), potable water kept out of cooling except in three named
circumstances (c19 to c22). City pretreatment rules for wastewater against a TCEQ discharge permit to a
creek (c23, c24), with that permit application withdrawn (c25). Buildings 300 feet from the north,
east and west lines (c30). Data centers, generation and batteries 700 feet from the south line, and
accessory buildings 500 (c31). A 400 foot landscaped buffer along the south line near FM 112 (c32)
with earthen berms at least 6 feet high (c33), there, the city says, to separate the development from
nearby homes (c59). Backup generators tested on weekdays between 8 a.m. and 5 p.m. (c34). $28.2
million committed (c35), the seven listed parts summing to it exactly (figures.json), and no tax
abatement asked (c43). In June a coalition of residents petitioned for a temporary ban on new data
centers (c50), about 1,400 signatures as KEYE reports (c52), and KEYE reports the city found the
measure can't reach the ballot because Texas law does not allow zoning by popular vote (c51).

The record carries this as tx-2026-0203, admitted this run.

**WHAT THE FACT CHECK CHANGED.**
- **The table's WITHOUT cells for light, water, electricity and setbacks ("No regulations") are not
  claims.** They are under the quote floor and repeat in four rows. The deck never prints them. It
  carries the city's own general sentences instead (c8, c9) and the two WITHOUT cells long enough to
  quote, noise (c13) and wastewater (c24).
- **No October 8th agenda was posted.** No time and no room are printed for that meeting. c58 is the
  standing schedule and the deck uses only its "City Hall Council Chambers".
- **The petition outcome is KEYE's reporting**, not a city page, and every surface says so.
- **The Attorney General's investigation (c55 to c57) is a different project, Blueprint, and stays
  out of the deck.**
- **The halls' size, the parcel's shape and where the berm sits inside the buffer are not in the
  record.** No parcel outline or map is drawn, the halls are illustrative massing with a kicker that
  says so, and no frame argues what a berm hides.

## Why this treatment, and what was grafted

Three directors pitched THE SURVEYOR (a 6 foot survey lath at every distance the terms write down,
overcast), THE NEIGHBOUR (a house across FM 112, one camera for today, without and with, at night) and
THE TOWN (the town's water tower and its long evening shadow, the walk into the council chamber,
golden hour). THE SURVEYOR is the spine, because its hero IS a figure of the record: every stake in the
deck stands exactly 6 feet above grade, the berm height the terms set (c33), so the object a reader
looks at on every frame carries the argument's unit.

- From THE SURVEYOR: the lath, its states, the rows at 400, 500 and 700 feet, the identical camera for
  1 and 2 (the rows driven, then pulled), the meter at the line, the person at the fence, the stake
  buried flush in the berm's crest, the fill as one basin 6 feet deep, the 1,400 stakes, and the close
  on one stake top.
- From THE TOWN: the WORLD and its geography. The parcel lies east of the city limits (c3), so the view
  from the land toward the town that decides runs into the evening sun. goldenHour, the sun low in the
  west south west. Its utility line along FM 112 carries the close toward the sun in the west.
- From THE NEIGHBOUR: the measurement frame at the line, the two bars for 65 and 85 dBA at one scale,
  and the reason for the buffer, now carried as c59 (the city's own sentence about nearby homes), drawn
  as two kit houses across FM 112 on the aerial, small, generic and labelled as drawn.
- Refused: a house as the hero (no claim places a home at the line), overcast (probed, and honest but
  flat, with no stake shadow), night (the Dark Skies pair can't be shown honestly when no fixture is in
  the record), 282 limestone blocks for the dollars and 140 people for the signatures (staged data art
  and five frames of the open mannequin defect), and a council chamber close (no agenda posted, and a
  countable dais would assert the council's size).

## The world, and the laws that hold it

**THE BLACKLAND PRAIRIE EAST OF TAYLOR AT THE LAST OF AN OCTOBER DAY.** The chassis is
`assets/js/deck/2026-10-06-prairie.js` and every frame loads it. It declares `sky: goldenHour` with the
haze warmed to Blackland field dust (#C9B393), and the light at azimuth -78 and elevation 7, low in the
west south west over town. Every cast in the deck runs east. A stake on the far rows stands as a
silhouette on the horizon's bright band, which the probe proved. The calm values for type are the dark
worked clay in the lower frame (hook and dek, light ink) and the clear sky high above the band (the
furniture). The probe's lessons are in `out/2026-10-06/tmp/probe/NOTES.md`.

1. The hero is `survey_lath`, a kit model the chassis builds: pine, 38 by 9.5 mm, a chisel point, a hub
   with a tack, two tails of survey pink flagging. Every lath is driven so `TT.ft(6)` stands above grade.
2. The ground is worked Houston Black clay, a `TXT.ground` dirt surface near #3A3129, with sparse
   stubble. No cotton rows near the camera (the probe found them tree sized at a standing eye) and no
   rock scatter (Blackland carries none).
3. `earthen_berm` is the deck's second kit model, at `TT.ft(6)` crest, wherever the terms' buffer is
   drawn. Its place inside the buffer is illustrative.
4. Every standing thing gets `TXT.contact`, every frame `TXT.weather`, and type sits on the dark clay or
   high sky, never on scatter.
5. Aerial frames set the setup fog near 0.0006 (the world's 0.0048 whites out a site at 400 m, probed).

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#1E1A16` | the DOM body behind the render |
| `accent` | `#E05A8F` | survey pink, the flagging tape on the lath, which marks a distance the terms write down. Frames 1, 3, 4, 5, 8, 9. Absent on 2 (the rows pulled), 6 (the flagging gone where the earth reached the stake top) and 7 (drowned to the knot) |
| `hook` | `#F3EFE6` | light type on the dark clay |
| `dek` | `#E8E2D6` | the dek |
| `rule` | `#E8E2D6` | the site line, the source line and the counter |

The world's own colours are lit materials: Houston Black clay #3A3129, dry crust #4A4036, October
stubble #A5977A, bar ditch bermuda #6E6E48, pine lath #C4A47A, FM asphalt #4A4946, galvanised wire
#9DA3A6, a T-post's green, and the haze #C9B393 at the horizon.

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE
    VALUE CUT: frame 9

1. **Motif evolution.** The 6 foot lath changes state on every frame: driven in rows (1), pulled and
   lying at the fence (2), the rows seen from above (3), at the line beside the meter (4), beside a
   person at the fence (5), buried flush in the berm's crest (6), drowned to its knot in the fill (7),
   multiplied once per reported signature (8), alone at the close (9).
2. **Camera move.** Frames 1 and 2 share one camera to the centimetre, the rows driven and then pulled,
   which is the before and after beat the rotation allows. Then up 60 m (3), down to the line (4), back
   to standing at the fence (5), crouched at the berm's toe (6), standing at a basin's lip (7), up 40 m
   (8), and in to one stake top at the close (9).

## The rotation

    FULL_BLEED  FULL_BLEED  DIAGRAM  CLOSE_CROP  FIGURE_SCALE  OBJECT_AND_CAPTION  SPLIT_HORIZON  FULL_BLEED  CLOSE_CROP

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | WIDE, standing eye 1.6 m on the FM 112 shoulder, horizon on the upper third | the worked clay field, Houston Black dirt ground worn and broken by stubble, raked by the low west sun; the near survey lath in pine with its grain, a mud ring and a contact at its foot, its long shadow east across the clay |
| 02 | WIDE, frame 1's camera to the centimetre | the same worked clay field, raked by the same sun; the pulled lath lying at the fence foot with mud on its point and a contact where it lies |
| 03 | AERIAL, 60 m up over FM 112 looking north north west | the clay field from above, the three stake rows crossing it, the earthen berm with its turf skin from green faces to straw crest, grass shoulders and the FM 112 asphalt worn at its edges |
| 04 | CLOSE, standing eye 1.4 m at the south line | the sound level meter on its tripod, aluminium legs grimed at their feet, a foam windscreen, the lath beside it cropped by the top edge, a contact where each foot meets the clay |
| 05 | MEDIUM, raised eye 4.2 m behind the south fence | the field paced in seven flagged rows to a data hall's long insulated metal panel wall, its louvre bays and plinth weathered from the ground up, its contact on the apron |
| 06 | MEDIUM, low eye 1 m off the berm's end, looking along it | the earthen berm, a vertex coloured turf skin with a bump texture from mown green faces to a straw crest, raking light from the low west sun on its crest and shade on its east face, worn bare and dirty at the toe where it meets the clay, young cedar elms with contact shadows on its face |
| 07 | WIDE, standing eye 1.6 m at a basin's lip | the fill basin, a cut in the worn clay with 2 to 1 banks, a damp stain darkening the banks near the waterline, a glossy water material carrying the sky's light, the drowned lath's knot casting a small shadow on the surface |
| 08 | AERIAL, 40 m up looking north | the stake field, 1,400 pine lath in fourteen blocks of a hundred, each lath lit from the west and casting a long shadow east across the worn clay, a contact at every foot, the far blocks in haze |
| 09 | CLOSE, standing eye 1.6 m, 3.6 m from one stake at the fence | the survey lath, pine backlit dark against the low sun with a rim on its sunward edge, its foot in the clay with a contact and its long shadow east, mud weathering its lower third, the two tails of flagging streaming along the fence, FM 112 and a pickup soft behind, utility poles receding toward the sun |

Showstopper frame: 01, the flagged rows standing as silhouettes on the burning horizon band over worked black clay, the near stake's shadow running east across the field
Tonal arc: opens mid dark on 01 and 02 with the bright band behind, lifts on the aerial 03, closes in on 04 and 05, darkest on 06 at the berm's shaded face, lifts on 07 with the water carrying the sky, lightest on the aerial 08, and settles dark on 09 against the last of the band.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "a worked Blackland clay field north of FM 112 at golden hour, three rows of flagged 6 foot survey lath crossing it at 400, 500 and 700 feet, the near stake standing large at the right"
  rect: [0, 330, 1080, 1020]
  bleeds: [left, right, bottom]
accent: "#E05A8F"
job: >
  Stop the scroll on a field with nothing built on it and flagged stakes at measured distances, so
  the deck's argument, terms written in feet, is a picture before it is a sentence.

claims: [c1, c2, c4, c30, c31, c32, c33]
numerals:
  - value_from: c2
  - value_from: c4

data_in_art:
  figure: setback_south_ft
  drives: stake row depth, rows at 400, 500 and 700 feet from the south line and every stake 6 feet above grade

depth:
  eye: 1.6
  horizon: 430
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION, HEIGHT_IN_FIELD]
  subject_at: {X: 2.6, Z: -7}

composition:
  structure: >
    A standing eye on the FM 112 shoulder looking north north west across the south line fence, the
    field running to a horizon on the upper third, three stake rows hugging the horizon band, the near
    stake in the right third owning the near silhouette and throwing its shadow east.
  bands: >
    Top third, the sky holding the kicker and the counter, the horizon's bright band with the far rows
    on it. Middle third, the worked clay field and the fence. Bottom third, the hook and the dek over
    the worked clay near the camera, clods and stubble lit from the left by the low sun and the near
    stake's long shadow crossing it toward the right.
  focal: "the near survey lath and its pink flagging against the bright band"

art:
  technique: "physically based render through txthree.js in the deck's goldenHour world, the chassis survey_lath, kit barbed_wire_fence, TXT.ground dirt"
  why_this_technique: "a stake at a measured distance is the plainest physical form a written setback can take"
  palette: "Houston Black clay, the warm horizon band, pine lath, survey pink"
  value_structure: >
    Lightest is the horizon band and the sky above it. Darkest is the near clay under the type.
    Frame median L* planned at 17, the plan rewritten to the measured value before the panel (it was 34, then a band of 18 to 46 in pixel round 3, now 14 to 46): the near clay under the type is the deck's darkest ground, and brightening the frame put a lit ridge edge through the dek.

type:
  hook: "Taylor's terms, in feet"
  dek: "The City Council votes October 8th on a proposed agreement for a 664-acre data center campus with its own power generation. The stakes in this field mark the south line and the distances its terms set."
  labels: []

verbatim: []

acceptance:
  - "the worked clay field fills at least 0.45 of the frame's height at full size, and the near survey lath stands at least 300 px tall on it, its pink flagging #E05A8F visible against the horizon band"
  - "three rows of flagged lath cross the field at the horizon band, and a render with no stake rows fails"
  - "the barbed wire fence crosses the frame between the camera and the field"
  - "the hook reads 'Taylor's terms, in feet' in light type on the dark clay"
  - "no building of any kind stands in the frame"
  - "the frame's median L* at 432px is between 14 and 46"

risks:
  - "the far rows go sub pixel at 432 px, so the flagging carries them and the rows sit on the horizon's bright band"
```

```yaml
slide: 2
layout: FULL_BLEED
primary_image:
  subject: "frame 1's field from frame 1's camera with every stake row pulled, one lath lying unflagged on the clay at the fence foot"
  rect: [0, 330, 1080, 1020]
  bleeds: [left, right, bottom]
accent: none
job: >
  Show the city's own claim about the alternative: the same field with no written distances, which
  the city says it would have no say over at all.

claims: [c5, c6, c8, c9]
numerals:
  - value_from: c6

data_in_art: none

depth:
  eye: 1.6
  horizon: 430
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, HEIGHT_IN_FIELD]
  subject_at: {X: 1.2, Z: -3}

composition:
  structure: >
    Frame 1's camera to the centimetre. Every row is gone. The pulled lath lies across the clay just
    inside the fence, large in the lower right, its point muddy.
  bands: >
    Top third, the sky and the horizon band, now empty. Middle third, the fence and the field.
    Bottom third, the hook and the dek over the worked clay, its clods lit
    from the left by the low sun and the pulled lath's shadow lying beside it.
  focal: "the pulled lath lying at the fence foot"

art:
  technique: "the same render, the same camera, the hero's state changed"
  why_this_technique: "the identical camera makes the only change the absence of the written distances"
  palette: "Houston Black clay, the warm horizon band, pine lath"
  value_structure: >
    Lightest is the horizon band. Darkest is the near clay. Frame median L* planned at 17.

type:
  hook: "Without it, no zoning at all"
  dek: "The developers withdrew their annexation and zoning application on September 3rd. The city says that without the agreement the land stays in unincorporated Williamson County, which has no zoning authority."
  labels: []

verbatim: []

acceptance:
  - "the pulled lath lies on the clay inside the fence and is at least 180 px long at full size"
  - "no stake stands upright anywhere in the frame, and a render showing the rows fails"
  - "the camera, the fence and the horizon sit where frame 1 put them, within 6 px"
  - "no pink flagging #E05A8F appears in the frame"
  - "the hook reads 'Without it, no zoning at all'"

risks:
  - "it reads as a re-render of frame 1, so the pulled lath sits large in the near field"
```

```yaml
slide: 3
layout: DIAGRAM
primary_image:
  subject: "the field from 60 m over FM 112 looking north, three stake rows crossing it at 400, 500 and 700 feet from the south line, a berm inside the buffer, two houses across the road"
  rect: [0, 360, 1080, 990]
  bleeds: [left, right, bottom]
accent: "#E05A8F"
job: >
  Lay the terms out at one scale from above, so each distance has a place on the ground and a label
  that names what it governs.

claims: [c31, c32, c33, c59]
numerals:
  - value_from: c31
  - value_from: c32
  - value_from: c33

data_in_art:
  figure: buffer_ft
  drives: row spacing on the ground, the buffer row at 400 feet, the accessory row at 500 and the data center row at 700, and the berm crest at 6 feet

depth:
  eye: 60
  horizon: 330
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: -150}

composition:
  structure: >
    An oblique aerial from over the south side of FM 112, the road across the lower frame, two houses
    small beyond its near shoulder, the fence on the south line, and the three stake rows receding
    across the clay toward a horizon on the upper quarter. DOM leaders end on each row.
  bands: >
    Top quarter, the sky with the kicker and the counter. Upper middle, the far field and the 700 foot
    row. Middle, the 500 and 400 foot rows and the berm. Bottom third, the asphalt of FM 112 with its worn
    shoulders, the two houses lit from the west with a long shadow each, and the type over the dark grass verge.
  focal: "the three flagged rows and their labels"

art:
  technique: "physically based render from above with DOM SVG leaders and mono labels"
  why_this_technique: "a set of distances is a mechanism, and a labelled drawing at one scale explains it"
  palette: "Houston Black clay, berm turf, asphalt, survey pink"
  value_structure: >
    Lightest is the sky and the horizon. Darkest is the clay in the near field. Frame median L*
    planned at 16.

type:
  hook: "From the south line"
  dek: "Near FM 112, a buffer of at least 400 feet with earthen berms at least 6 feet high. Accessory structures at least 500 feet back. Data centers, generation and batteries at least 700 feet back."
  labels: ["400 FT BUFFER", "500 FT ACCESSORY", "700 FT DATA CENTERS"]

verbatim: []

acceptance:
  - "the three flagged stake rows cross the clay field at increasing depth and each row spans at least 600 px of the frame's width at full size"
  - "three labels read '400 FT BUFFER', '500 FT ACCESSORY' and '700 FT DATA CENTERS', each #E05A8F leader ending on its row"
  - "the labels stack in order of distance, 700 at the top and 400 at the bottom"
  - "the data hall stands beyond the 700 foot row in the upper right and is cut by the right edge"
  - "no parcel outline is drawn"

risks:
  - "the berm at 6 feet vanishes from 60 m up, so its lit west face and its shadow carry it"
```

```yaml
slide: 4
layout: CLOSE_CROP
primary_image:
  subject: "a sound level meter on a tripod at the south property line beside a 6 foot lath, cropped by the top and right edges, the field and the far rows soft behind"
  rect: [380, 120, 700, 1080]
  bleeds: [right]
accent: "#E05A8F"
job: >
  Put the noise term where it would be measured, at the property line, and set the cap beside the
  limit the city lists without the agreement at one scale.

claims: [c12, c13, c14]
numerals:
  - value_from: c12
  - value_from: c13

data_in_art:
  figure: noise_with_dba
  drives: bar length, two bars from zero at one scale, 65 and 85 dBA

depth:
  eye: 1.4
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 0.4, Z: -1.6}

composition:
  structure: >
    A close standing eye at the line. The meter's foam windscreen at 1.5 m and its tripod fill the
    right half, cropped by the top and right edges. The lath stands just behind it, its flagging in
    frame. The field recedes left to the horizon.
  bands: >
    Top third, the sky and the kicker, the windscreen. Middle third, the horizon and the two bars.
    Bottom third, the hook and the dek on the worked clay, the tripod's
    feet and their shadows at the top of it, the clay falling into shadow toward the frame's foot.
  focal: "the foam windscreen against the bright band"

art:
  technique: "physically based render, close crop, with two DOM bars at one scale"
  why_this_technique: "a measurement is an instrument at a place, and a bar never a dial carries the two numbers"
  palette: "aluminium, grey foam, Houston Black clay, survey pink"
  value_structure: >
    Lightest is the band behind the windscreen. Darkest is the clay. Frame median L* planned at 23.

type:
  hook: "65 decibels, or the level before"
  dek: "The terms cap the campus's noise at 65 dBA or the level before construction, whichever is greater. A study at the property lines would set that level. Without the agreement, the city lists the state's 85 dBA."
  labels: ["WITH THE TERMS 65 DBA OR THE BASELINE", "WITHOUT 85 DBA"]

verbatim: []

acceptance:
  - "the sound level meter and its tripod stand at least 700 px tall at full size, all three feet on the clay with a contact"
  - "two bars from one zero carry lengths in the ratio of 65 to 85, the WITH bar in survey pink #E05A8F"
  - "the bar labels read 'WITH THE TERMS 65 DBA OR THE BASELINE' and 'WITHOUT 85 DBA'"
  - "a lath with pink flagging stands behind the tripod, its tails above the horizon"
  - "the hook reads '65 decibels, or the level before'"

risks:
  - "the meter reads as a microphone stand, so the windscreen ball and the body proportions carry it"
```

```yaml
slide: 5
layout: FIGURE_SCALE
primary_image:
  subject: "a person at the south line fence beside a 6 foot lath, seven flagged rows paced every 100 feet ahead, ending at a data hall's long wall 700 feet out"
  rect: [0, 280, 1080, 880]
  bleeds: [left, right]
accent: "#E05A8F"
job: >
  Give 700 feet a size a reader has walked, from a fence a person stands at, to the closest data hall the
  terms would allow on the south side.

claims: [c31]
numerals:
  - value_from: c31

data_in_art:
  figure: setback_south_ft
  drives: depth of the hall's near face, seven stake rows at 100 foot spacing ending at 700 feet

depth:
  eye: 1.6
  horizon: 470
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, TEXTURE_GRADIENT, OCCLUSION]
  subject_at: {X: -2.4, Z: -2}

composition:
  structure: >
    A standing eye behind a person at the fence, turned three quarters away and under a fifth of the
    frame. Seven flagged rows recede at even steps to a long pale hall wall across the far field.
  bands: >
    Top third, the sky and the kicker. Middle third, the paced rows and the hall on the horizon. Bottom
    third, the person's shoulders lit from the left, the fence wire catching the light, and the type
    on the shadowed clay.
  focal: "the hall wall at the end of the paced rows"

art:
  technique: "physically based render, the kit person and kit data_center at true scale, the chassis lath"
  why_this_technique: "a person beside a stake gives 6 feet, and seven paced rows give 700"
  palette: "Houston Black clay, insulated metal panel grey, survey pink"
  value_structure: >
    Lightest is the sky and the hall's lit west end. Darkest is the near clay. Frame median L*
    planned at 19.

type:
  hook: "The closest a data hall gets to the south line"
  dek: "Data centers, power generation and battery storage would stand at least 700 feet from the south line. The hall here is drawn for scale, and the size of the real buildings is not in the record."
  labels: []

verbatim: []

acceptance:
  - "the data hall's long wall spans at least 500 px of the frame's width at full size at the end of the seventh row"
  - "seven rows of flagged lath stand between the fence and the hall"
  - "the person stands at the fence turned away and is under a fifth of the frame's height"
  - "a lath beside the person stands just above the person's head"
  - "the hook reads 'The closest a data hall gets to the south line'"

risks:
  - "the kit person reads as a mannequin, so it stays small, turned away and lit from the camera side"
```

```yaml
slide: 6
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "an earthen berm as the terms describe it, seen from its toe, turf from green faces to straw crest, young cedar elms on its face, a lath buried flush at its 6 foot crest"
  rect: [0, 430, 1080, 880]
  bleeds: [left, right]
accent: none
job: >
  Make the 6 foot berm a solid thing, and make the stake's height and the berm's height the same
  number, drawn.

claims: [c32, c33, c59]
numerals:
  - value_from: c32
  - value_from: c33

data_in_art:
  figure: berm_ft
  drives: berm crest height above grade, equal to the stake's height so the stake's top meets the crest

depth:
  eye: 0.6
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, FORM_SHADING]
  subject_at: {X: 0, Z: -9}

composition:
  structure: >
    A crouched eye at the berm's toe. The berm's long face runs across the frame, its crest on the
    middle of the frame against the sky, young cedar elms on the face, one lath standing at the crest
    with its top flush with the earth.
  bands: >
    Top third, the sky with the kicker. Middle, the berm's crest line and the elms against the sky.
    Bottom third, the berm's east face in shadow, its turf
    texture and the elms' contact shadows, with the type on the darkest of it.
  focal: "the lath's top meeting the crest"

art:
  technique: "physically based render, the chassis earthen_berm and survey_lath, kit cedar_elm"
  why_this_technique: "a monument camera at the toe makes 6 feet of earth read as a wall"
  palette: "berm turf green to straw, cedar elm, the shaded clay, the sky"
  value_structure: >
    Lightest is the sky above the crest. Darkest is the berm's shaded east face under the type. Frame
    median L* planned at 26.

type:
  hook: "6 feet of earth"
  dek: "A buffer of at least 400 feet along the south line would carry landscaping and earthen berms at least 6 feet high. The city says the buffer areas would separate the development from nearby homes."
  labels: []

verbatim: []

acceptance:
  - "the earthen berm's face spans the full width of the frame and stands at least 280 px tall at full size"
  - "one 6 foot lath stands unflagged at the berm's toe, at least 300 px tall at full size"
  - "the berm's crest recedes as a diagonal from the left edge toward the right, its turfed face lit by the low sun"
  - "the sky stands only above the crest, and the berm's toe meets bare clay above the type"
  - "no pink flagging #E05A8F appears in the frame"
  - "the hook reads '6 feet of earth'"

risks:
  - "a smooth earthwork reads as a CG ridge, so the turf colour, the bump and the saplings break it"
```

```yaml
slide: 7
layout: SPLIT_HORIZON
primary_image:
  subject: "a basin cut 6 feet into the clay holding the cooling loop's initial fill of 1.575 million gallons, a lath drowned to its knot in the middle, the far bank and field beyond"
  rect: [0, 330, 1080, 870]
  bleeds: [left, right]
accent: none
job: >
  Give the first fill a size, using the deck's own 6 foot unit as its depth, and say what keeps
  drinking water out of the loop.

claims: [c17, c19, c20, c21, c22]
numerals:
  - value_from: c17

data_in_art:
  figure: fill_million_gal
  drives: basin waterline side, solved for the fill's volume at a 6 foot depth with 2 to 1 banks

depth:
  eye: 1.6
  horizon: 330
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: -40}

composition:
  structure: >
    A standing eye at the basin's near lip, the straight near bank the horizontal cut at about six
    tenths of the frame. Above it the water, the drowned lath, the far bank and the field to a horizon
    on the upper quarter. Below it the dark clay bank with the type.
  bands: >
    Top quarter, the sky and the kicker. Middle half, the water carrying the sky and the drowned lath.
    Bottom, the near clay bank in shadow, its damp
    texture darker at the waterline, and the type on it.
  focal: "the drowned lath's knot at the water's surface"

art:
  technique: "physically based render, a basin cut into TXT.ground with a reflective water plane"
  why_this_technique: "a volume at one scale, using the deck's own 6 foot unit as its depth"
  palette: "water carrying the warm sky, Houston Black clay, pine"
  value_structure: >
    Lightest is the water carrying the sky. Darkest is the near clay bank. Frame median L* planned at 39.

type:
  hook: "1.575 million gallons to start"
  dek: "Cooling would run in a closed loop on reclaimed water with an initial fill of 1.575 million gallons, drawn here as one basin 6 feet deep. Drinking water would stay out of cooling except in three circumstances."
  labels: []

verbatim: []

acceptance:
  - "the basin's water spans the frame's width and at least 300 px of its height at full size"
  - "a lath stands in the water with only its top and knot above the surface"
  - "the near bank is a straight horizontal edge across the frame"
  - "the hook reads '1.575 million gallons to start'"
  - "no pink flagging #E05A8F appears above the water"

risks:
  - "it reads as a planned pond, so the kicker says THE FIRST FILL, DRAWN AS ONE BASIN"
```

```yaml
slide: 8
layout: FULL_BLEED
primary_image:
  subject: "about 1,400 flagged 6 foot lath in fourteen blocks of a hundred on worked clay, seen from 40 m, two people at the near corner"
  rect: [0, 330, 1080, 1020]
  bleeds: [left, right]
accent: "#E05A8F"
job: >
  Draw the counter image at the deck's own scale: the residents who asked for a different answer, one
  stake per reported signature, beside the city's reply.

claims: [c50, c51, c52, c54]
numerals:
  - value_from: c52

data_in_art:
  figure: petition_signatures
  drives: stake count, fourteen blocks of a hundred stakes, one per reported signature

depth:
  eye: 40
  horizon: 300
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: -90}

composition:
  structure: >
    An oblique aerial looking north over the field, the fourteen blocks in two rows of seven running
    away from the camera, each block a square of flagged stakes, long shadows running east, two people
    at the near corner for scale, the horizon on the upper quarter.
  bands: >
    Top quarter, the sky and the kicker. Middle, the stake blocks receding into haze. Bottom third,
    the near blocks lit from the west with their long shadows running east, the two people and their
    shadows, and the type over the clay between the shadows.
  focal: "the near blocks of stakes with their pink flags"

art:
  technique: "physically based render, instanced chassis lath at true scale, kit person"
  why_this_technique: "a count a reader can count, at the same scale as every other stake in the deck"
  palette: "Houston Black clay, pine, survey pink, the warm haze"
  value_structure: >
    Lightest is the sky and the far haze. Darkest is the clay between the blocks. Frame median L*
    planned at 17.

type:
  hook: "About 1,400 signed a ban petition"
  dek: "In June residents petitioned for a temporary ban on new data centers. KEYE reports the city found it can't go on the ballot. Texas Standard reports coalition members filed a motion with the Third Court of Appeals."
  labels: []

verbatim: []

acceptance:
  - "the fourteen blocks of stakes span at least 600 px of the frame's width at full size, two columns of seven receding toward the horizon"
  - "each block stands on its own raked square, lighter than the clay around it, so fourteen squares can be counted at 432 px"
  - "two people stand in the aisle between the columns and neither is taller than 60 px at full size"
  - "the hook reads 'About 1,400 signed a ban petition'"

risks:
  - "the metaphor reads as advocacy, so the dek carries the city's answer and the kicker states the drawing rule"
```

```yaml
slide: 9
layout: CLOSE_CROP
primary_image:
  subject: "the top of one 6 foot lath at the south line, its pink flagging lifting in the last light, FM 112 and a pickup heading west soft behind, utility poles receding toward the sun"
  rect: [380, 330, 700, 1350]
  bleeds: [right, bottom]
accent: "#E05A8F"
job: >
  Close on the one stake still standing and the date that decides whether any of it binds, with what
  else the agreement carries.

claims: [c1, c4, c35, c43, c58]
numerals:
  - value_from: c4
  - value_from: c35

data_in_art: none

depth:
  eye: 1.85
  horizon: 610
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, OCCLUSION]
  subject_at: {X: 0.12, Z: -0.5}

composition:
  structure: >
    A macro at the stake's top, the pine end and the knot of flagging in the right half cropped by the
    top edge, the tails lifting toward the left. Behind, soft, the road, a pickup heading west and the
    town's tower on the bright band.
  bands: >
    Top third, the kicker and the stake's top against the sky. Middle third, the flagging, the bright
    band and the tower. Bottom third, the hook and the dek over the field
    falling into shadow, the road's verge a soft dark texture behind them.
  focal: "the flagging lifting against the bright band"

art:
  technique: "physically based render, macro on the chassis lath, kit pickup and water_tower out of focus"
  why_this_technique: "the deck's unit, close enough to see the grain, alone at the end"
  palette: "pine, survey pink, the burning band, Houston Black clay"
  value_structure: >
    Lightest is the band behind the flagging. Darkest is the field under the type. Frame median L*
    planned at 34.

type:
  hook: "The vote is October 8th"
  dek: "Big Watt Digital and PowerHouse Data Centers would commit $28.2 million and ask for no tax abatement. Regular council meetings are held in the City Hall Council Chambers."
  labels: []

verbatim: []

acceptance:
  - "the lath stands at least 600 px tall at full size, a quarter of the frame height, its flagging #E05A8F streaming in the wind"
  - "FM 112 runs left of the fence toward the sun, a pickup on it and utility poles receding to the horizon"
  - "the flagging ends above the hook and crosses no line of type"
  - "the hook reads 'The vote is October 8th'"

risks:
  - "a single stick reads as little at thumb size, so the flagging and the sun carry the silhouette"
```
