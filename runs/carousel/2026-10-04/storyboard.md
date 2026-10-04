# Storyboard, 2026-10-04
# "The state board said no."

## The story, and what the fact check did to it

Emails obtained by The Texas Tribune and ProPublica show Texas Education Agency staff helped connect
Alpha School's AI learning platform, now often called TimeBack (c13), with public school districts
(c12). Commissioner Mike Morath answered Alpha associates in September 2025 (c9, c10), offered to
introduce an Alpha leader to the superintendent he appointed to run Houston ISD's takeover (c11),
and went back to Alpha's campuses with six other TEA leaders on the same day as Houston
superintendent Mike Miles (c33). State officials and Alpha affiliates approached at least 10
districts (c16). At least three launched pilots, Houston, Fort Davis and Aldine (c17), all as
supplemental learning rather than Alpha's full model of AI teaching basic subjects in two hours a
day (c18, c34). At least five said no (c19). TEA says there is no formal partnership and that it
left the decision to the districts (c21, c22). Before any of it, the State Board of Education,
which has the final say on charters, voted the Alpha leaders' charter bid down 10 to 3 (c7, c8).
At Texas Preparatory School, which used the platform, an Alpha leader claimed 50 to 60 percent of
students were passing (c39), TEA's published results don't back that up (c40), and 21 percent
passed (c28, c41).

The record carries this as tx-2026-0200.

**WHAT THE FACT CHECK CHANGED.**
- **Valenta Academy is never called Alpha's.** No source names it. The deck's board vote is the
  Tribune's "10 to 3" (c7), never the minutes' 10-3-1.
- **No Houston ISD campus is named or drawn as a particular school.** No district document was
  found, so every pilot fact is the Tribune's reporting.
- **TEA connected and districts decided** (c22). No frame says TEA put, forced, approved or bought
  the tool.
- **The 10 is "at least".** The 2 standing back on frame 5 are a computed floor, approached
  districts the reporting names neither way (approached_unnamed), never "two unknown districts".
- **c39 never appears without c40.** c44 is about vouchers and is not used.
- **The buses are a drawing of the count,** one bus per district, and the deck says so. No bus is
  lettered with a district's name. The names are DOM type.

## Why this treatment, and what was grafted

Three directors pitched THE CLOCK, THE ROUTE and THE DOOR, and all three chose highNoon without
seeing each other. THE ROUTE's hero is the spine, because a school bus is the one honest unit for
a district every Texan already knows, and its stop arm is the one part of the vehicle built to say
no. So the arm carries the count: out where an answer was no, folded where a district said yes.

- From THE ROUTE: the bus as the hero and the unit, the arm as the state, the bus lot as the
  showstopper count, Aldine's four wings with Houston hazed beyond, and a close at a neighbourhood
  stop.
- From THE CLOCK: the empty chairs counting the board's vote rather than seating thirteen real
  members, and the school clock with its two hour sector, which is now the Fort Davis frame's
  subject and the only place the full model is drawn.
- From THE DOOR: the seven walkers on the return visit, Texas Preparatory School as a measured
  frame at one scale, and the close that names a step a reader can take.
- Refused: THE ROUTE's and THE CLOCK's painted play-court map (a 30 m TXGeo decal in 3D for one
  count the bus lot already makes), lettered buses (legible type rendered into a texture), THE
  DOOR's field of ten doors (a conceptual render rather than a photograph of a place), and every
  version of a page that invents an email header.

## The world, and the laws that hold it

**A TEXAS SCHOOL DAY AT NOON.** The chassis is `assets/js/deck/2026-10-04-noonbell.js` and every
frame loads it. It declares `sky: highNoon`, tuned toward a pale caliche horizon with a little dust
in the haze. One light: the sun at azimuth 10, elevation 58, high in the south and a touch west. The
table gives highNoon to "strain" and to dark type, and this is a story about public schools and a
tool sold as a way to save time, told in the light where nothing hides in a shadow longer than the
thing that casts it. These emails came out through public information requests. The deck stands in
the least dramatic light Texas has, so it reports rather than insinuates.

+x is east and -z is north. A camera looking north sees sunlit faces and short black shadows
falling toward it.

**THE HERO OBJECT.** One Type C school bus, the kit's `school_bus`, chrome yellow, white roof,
no district lettering, `TXT.weather` dust low on the skirts. Its states: stop arm OUT (a no), arm
folded (a yes), and a pilot bus carries the accent card in its windshield. **The school clock**,
`school_clock`, is a kit addition in the chassis: a 0.36 m dial with a black case, no numerals, and
a sector two hours wide in the accent. It appears on frame 6 only, where the full model is
weighed.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#E7E3DA` | the DOM body behind the render |
| `accent` | `#C2477A` | "the platform". The card in a pilot bus's windshield (5, 7), the two hour sector on the clock (6), and the measured column at Texas Preparatory School (8). Never a sky, a building, a person or a light |
| `hook` | `#15171C` | dark type on the bleached sky |
| `dek` | `#1D2026` | the dek |
| `rule` | `#1D2026` | the site line, the source line and the counter |

The world's own colours are lit materials: bus chrome yellow (#F4AB00) under dust, buff ISD brick
(#C49460), cast stone, broom finished concrete, Austin limestone, October grama straw and rhyolite
rimrock for Fort Davis, Gulf haze for Aldine.

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE, VALUE_ARC

1. **Motif evolution.** The bus's stop arm is the argument's state: out in Austin after the board's
   no (1), counted out on five and folded on three in the lot (5), folded beside the Fort Davis
   clock (6) and at Aldine (7), and out again at a neighbourhood stop where the reader's own
   district decides (9).
2. **Camera move.** Street eye in Austin (1), into the rooms (2, 3), back out at standing eye on a
   campus walk (4), down to a long lens on a lot (5), close under a walkway (6), up over Aldine
   (7), into a room (8), and back to street eye at a stop (9).
3. **Value arc.** Noon opens bright on 1. The rooms on 2 and 3 step down to mid. The walk and the
   lot on 4 and 5 lift to the deck's brightest. Frame 6 drops into the walkway's shade, the darkest.
   Aldine lifts on 7, the room settles to mid on 8, and the stop closes bright on 9.

## The rotation

    FULL_BLEED  DIAGRAM  DOCUMENT  FIGURE_SCALE  FULL_BLEED  CLOSE_CROP  SPLIT_HORIZON  DIAGRAM  FULL_BLEED

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | WIDE, standing eye 1.6 m on the east sidewalk of Congress Avenue, horizon on the lower third | the school bus at the near kerb, chrome yellow paint lit full on its east flank by the noon sun, the stop arm out, road dust darkening its skirts and tyres from TXT.weather, a contact under each axle on the asphalt, the Capitol hazed at the street's end |
| 02 | MEDIUM, seated eye 1.2 m from the public rows, long lens | the block of thirteen exec office chairs, black leather catching the window light on their backs, each a little askew, contacts on the carpeted floor, the dais and blank seal behind in the room's pale limestone |
| 03 | CLOSE, seated eye at a desk by a lit window | the letter sheet on the walnut desk, bright paper in the window light with a soft curl and a contact line where it lies, the document stacks and a dark monitor beyond it in shallow focus |
| 04 | WIDE, standing eye 1.6 m on a campus walk | the covered walkway, a ribbed galvanized deck on dark posts throwing a black band of noon shade across broom finished concrete, the brick wing behind with its windows, seven walkers small in the light beyond the shade, each with a short shadow at the feet |
| 05 | WIDE, long lens at 1.2 m from 70 m, horizon at a third | ten school buses nose on in a row, chrome yellow under dust, five stop arms out as red octagons, three folded with the accent card, two set back in haze, short black pools under each bumper on the asphalt lot |
| 06 | CLOSE, 0.7 m off the clock, looking up under the walkway | the school clock, black moulded case and white face with its two hour sector, hung from the walkway's edge beam, the ribbed deck black above it, the bus flank and the Davis Mountains rimrock in bleached light behind |
| 07 | AERIAL, 28 m up over the street, horizon on the upper third | four brick middle school wings receding along the road, their roofs and walk canopies throwing short shadows, a bus at the near kerb with the accent card, Houston's towers in Gulf haze |
| 08 | MEDIUM, standing eye across a long table in a pale room | the columns on the table at one scale, limestone and glass and one accent column, each with a contact on the oak top and a soft window shadow, the room's limestone wall behind |
| 09 | MEDIUM, standing eye 1.6 m at a neighbourhood stop | the school bus with its stop arm out at the kerb, chrome yellow under dust, a parent beside it at true scale three quarters away, a live oak's black pool of shade and a brick ranch house behind |

Showstopper frame: 05, ten buses nose on under a white noon sky, five red arms out in a row like a sentence and three folded, two standing back in the heat haze, the lot's depth built from the bus sizes stepping back and the haze on the far pair
Tonal arc: bright noon on 01, the rooms on 02 and 03 step down to mid, 04 and 05 lift to the deck's brightest, 06 drops into the walkway shade as the darkest frame, 07 lifts again, 08 settles to mid, and 09 closes bright.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "a chrome yellow school bus at the near kerb of Congress Avenue at noon, its stop arm out, the Texas Capitol hazed at the street's north end"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: none
job: >
  Stop the scroll on a school bus saying no at the Capitol's door, and say the whole story in the
  hook and dek: the board said no, and a different route was found district by district.

claims: [c6, c7, c12]
numerals:
  - value_from: c7

depth:
  eye: 1.6
  horizon: 900
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION, FORM_SHADING]
  subject_at: {X: 4, Z: -16}

composition:
  structure: >
    A standing eye on the sidewalk, the avenue running north to the Capitol, the bus at the near
    kerb filling the lower right so its arm points into the street.
  bands: >
    Top third, the bleached sky holding the kicker and the hook. Middle third, the dek, then the
    Capitol's dome hazed at the avenue's end. Bottom third, the bus's sunlit yellow flank in the
    foreground, its red arm out, its tyres on their contact shadows and the asphalt's lane lines
    running away into haze.
  focal: "the bus's flank and its red stop arm"

art:
  technique: "physically based render through txthree.js in the deck's highNoon world, the kit school_bus, capitol, road and streetlight"
  why_this_technique: "a bus with its arm out at the Capitol is a no a reader recognises before reading a word"
  palette: "bleached sky, Austin limestone and asphalt, chrome yellow, one red arm"
  value_structure: >
    Lightest is the sky and the sunlit flank. Darkest is the shade under the bus and its tyres.
    Frame median L* planned at 70.

type:
  hook: "The state board said no."
  dek: "The Tribune reports it voted the Alpha leaders' AI charter bid down 10 to 3. Emails obtained by The Texas Tribune and ProPublica show Texas Education Agency staff helped connect the same AI platform with school districts."
  labels: []

verbatim: []

acceptance:
  - "a yellow school bus reads at 432px as one object owning the lower right of the frame"
  - "the bus's red stop arm is out from its side and visible at 432px"
  - "the Capitol's dome stands at the avenue's far end, hazed lighter than the bus"
  - "the bus's tyres touch the asphalt with a contact shadow darker than the road beside them"
  - "the hook reads 'The state board said no.' in dark type on the sky"
  - "the frame's median L* at 432px is between 58 and 80"

risks:
  - "the Capitol at 600 m can shrink to a bump, so the lens is long enough that its dome clears the roofline"
```

```yaml
slide: 2
layout: DIAGRAM
primary_image:
  subject: "thirteen empty black exec chairs in a hearing room, a block of ten and a block of three with an aisle between, the dais behind"
  rect: [0, 600, 1080, 750]
  bleeds: [left, right, bottom]
accent: none
job: >
  Draw the board's vote as a count a reader can count, without seating thirteen real members on a side.

claims: [c7, c8]
numerals:
  - value_from: c7

data_in_art:
  figure: board_for
  drives: mark count, the chairs in the left block, with board_against chairs in the right block across the aisle

depth:
  eye: 1.2
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: -3}

composition:
  structure: >
    A seated eye from the public rows on a long lens, so the two blocks of chairs read at one size
    and the aisle between them is the vote's line.
  bands: >
    Top third, the room's pale wall and the hook. Middle third, the dek, the dais and its blank seal.
    Bottom third, the two blocks of chairs in the foreground,
    their leather lit by the window, each on its own contact shadow on the carpet.
  focal: "the aisle between the block of ten and the block of three"

art:
  technique: "physically based render, TXT.interior hearing room with the kit hearing_dais, seal_plaque and office_chair"
  why_this_technique: "empty chairs count votes without assigning a real person to a side"
  palette: "Austin limestone wall, black leather, walnut dais, a blue grey carpet"
  value_structure: >
    Lightest is the window lit wall. Darkest is the chair leather and the shade under the dais.
    Frame median L* planned at 76.

type:
  hook: "Voted down 10 to 3, the Tribune reports."
  dek: "The board has the final say on charters. Members cited the use of AI to teach, student screen time and questions about the test gains Alpha leaders presented."
  labels: ["10 IN THE MAJORITY", "3 IN THE MINORITY"]

verbatim: []

acceptance:
  - "two blocks of chairs read at 432px, ten on the left and three on the right, with a clear aisle between"
  - "every chair stands on the floor with a contact shadow"
  - "no person is seated in any chair"
  - "the hook reads 'Voted down 10 to 3, the Tribune reports.' and names the Tribune"
  - "the frame's median L* at 432px is between 66 and 86"

risks:
  - "thirteen chairs on a long lens can merge into one black mass, so they stand at a pitch with floor between them"
```

```yaml
slide: 3
layout: DOCUMENT
primary_image:
  subject: "a single letter sheet lying in window light on a walnut desk, carrying the one line the reporting quotes from the commissioner's reply"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: none
job: >
  Put the commissioner's own words in front of the reader, and only those words.

claims: [c9, c10, c11]
numerals:
  - value_from: c9

depth:
  eye: 1.2
  horizon: 560
  cues: [LINEAR_PERSPECTIVE, CAST_SHADOW, OCCLUSION, FORM_SHADING, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A seated eye at the desk looking down across the sheet toward the window, so the page reads as
    a page and the line on it is legible.
  bands: >
    Top third, the room's wall and the hook. Middle third, the dek and the window. Bottom third,
    the sheet lit by the window in the foreground, its soft shadow on the walnut and its one line.
  focal: "the quoted line on the sheet"

art:
  technique: "physically based render, TXT.interior office with the kit desk, document_stack and monitor, a letter sheet in the chassis"
  why_this_technique: "a page on a desk is the honest shape of an email the public saw only because records were requested"
  palette: "walnut, bright paper, limestone, a dark monitor"
  value_structure: >
    Lightest is the sheet and the wall. Darkest is the walnut and the desk's shadow.
    Frame median L* planned at 72.

type:
  hook: "The commissioner wrote back."
  dek: "Mike Morath answered Alpha School associates in September 2025. He offered to introduce an Alpha leader to the superintendent he appointed to run the state takeover of Houston ISD."
  labels: []

verbatim:
  - c10: "I'd love to schedule a follow-up discussion"

acceptance:
  - "a single sheet of paper reads at 432px as a page lying on a desk"
  - "the quoted line is legible on the sheet and matches c10 word for word"
  - "the attribution names Morath and the newsrooms, and no email header is drawn"
  - "the sheet casts a soft contact on the desk"
  - "the frame's median L* at 432px is between 60 and 82"

risks:
  - "a page with type on it can read as a plate, so the type is set on the rendered sheet's own surface and nowhere else"
```

```yaml
slide: 4
layout: FIGURE_SCALE
primary_image:
  subject: "seven people at true scale walking along a school campus walk in noon light, beyond the black band of a covered walkway's shade"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: none
job: >
  Show the return visit as seven people, so the commissioner's party is a size a reader can see.

claims: [c33]
numerals: []

data_in_art:
  figure: tea_party
  drives: mark count, the number of walking figures

depth:
  eye: 1.6
  horizon: 880
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: -14}

composition:
  structure: >
    A standing eye under the walkway's edge, the shade a black band across the foreground, the
    seven walking away into the sunlit walk beyond, small against the brick.
  bands: >
    Top third, the sky over the roofline and the hook. Middle third, the dek, the brick wing and
    the walkway's edge. Bottom third, the black shade band and the walkers in the light beyond it.
  focal: "the seven walkers in the sunlit walk"

art:
  technique: "physically based render, the kit school wing with its covered walk, seven kit people walking"
  why_this_technique: "a party of seven at true scale is a count and a scene at once"
  palette: "buff brick, cast stone, galvanized deck, broom finished concrete, black shade"
  value_structure: >
    Lightest is the sunlit walk and sky. Darkest is the walkway shade band.
    Frame median L* planned at 62.

type:
  hook: "Back again, with six others."
  dek: "Emails show Morath went back to Alpha's campuses with six other TEA leaders. His staff timed it for the same day as Houston superintendent Mike Miles. The campus drawn is no particular school."
  labels: []

verbatim: []

acceptance:
  - "seven separate people read at 432px, each standing on the walk with a short shadow at the feet"
  - "no face is shown front on and every walker is under a fifth of the frame height"
  - "the walkway's shade reads as a dark band along the wing behind the walkers, and the near walk carries grit and wear"
  - "no school bus is in the frame"
  - "the frame's median L* at 432px is between 50 and 76"

risks:
  - "the kit person can read as a mannequin, so every walker is turned away and small"
```

```yaml
slide: 5
layout: FULL_BLEED
primary_image:
  subject: "ten school buses on an asphalt lot at noon seen from 12 m up, three pulled forward out of their stalls onto bays painted in the accent, five still in their stalls with their stop arms out, two set back in a second row, a brick campus wing beyond the fence"
  rect: [0, 700, 1080, 650]
  bleeds: [left, right, bottom]
accent: "#C2477A"
job: >
  Make the count the reader carries away, one bus per district, as a photograph of a lot.

claims: [c16, c17, c19, c22]
numerals:
  - value_from: c16
  - value_from: c17
  - value_from: c19
  - computed_by: "out/2026-10-04/compute.py, approached_unnamed = districts_approached - pilot_districts - declined_districts"

data_in_art:
  figure: districts_approached
  drives: mark count, the buses on the lot, with pilot_districts buses pulled forward onto accent bays, declined_districts in their stalls with arms out, and approached_unnamed set back in the second row

depth:
  eye: 10
  horizon: 640
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 13, Z: 0}

composition:
  structure: >
    A raised eye over the lot so every bus reads as its own unit and the three groups separate by
    where they stand, which reads at any size, rather than by the stop arms alone.
  bands: >
    Top third, the sky holding the hook and dek. Middle third, the two group labels over the sky,
    the campus wing and its flags beyond the fence. Bottom third, the buses lit by the noon sun in
    the foreground, the pilots on their accent bays, the black shadow pooled under each bumper.
  focal: "the three buses pulled forward onto their accent bays, against the row of five behind"

art:
  technique: "physically based render, the kit school_bus ten times on an asphalt lot, the kit school and pipe_rail_fence beyond"
  why_this_technique: "a bus is the honest unit for a district, and a lot of them is a count anyone can read"
  palette: "white sky, chrome yellow, five red arms, three accent bays, asphalt, buff brick"
  value_structure: >
    Lightest is the sky and the bus roofs. Darkest is the shade pooled under the bumpers.
    Frame median L* planned at 62.

type:
  hook: "Approached, at least 10. Piloted, 3. Declined, 5."
  dek: "One bus per district in the reporting, and every count is a floor. The 2 set back stand for approached districts it does not name. TEA says it connected interested district leaders and left the choice to them."
  labels: ["PILOT DISTRICTS HOUSTON, ALDINE, FORT DAVIS", "DECLINED ECTOR COUNTY, FORT BEND, IRVING, PECOS, PFLUGERVILLE"]

verbatim: []

acceptance:
  - "ten buses read at 432px, three pulled forward, five in stalls and two set back"
  - "three buses stand on bays painted in the accent and no other bus does"
  - "red stop arms stand out from the five buses in their stalls"
  - "every bus touches the asphalt with a dark shadow under its bumper"
  - "the accent covers under eight percent of the frame"
  - "the frame's median L* at 432px is between 50 and 76"

risks:
  - "ten buses at this distance are small, so the groups are told apart by position and the bays, and the labels name them"
```

```yaml
slide: 6
layout: CLOSE_CROP
primary_image:
  subject: "a school clock in a cast stone surround on a Fort Davis campus entry, its white face carrying a two hour sector in the accent, the brick pier and wing cropped by the right and bottom edges"
  rect: [180, 700, 900, 650]
  bleeds: [right, bottom]
accent: "#C2477A"
job: >
  Weigh the full model against what Fort Davis is actually doing, on the one frame that draws the two hours.

claims: [c18, c23, c34, c35]
numerals:
  - value_from: c23

data_in_art:
  figure: model_dial_degrees
  drives: arc sweep, the two hour sector on the clock's face, model_hours of a twelve hour dial

depth:
  eye: 1.6
  horizon: 1300
  cues: [OCCLUSION, CAST_SHADOW, FORM_SHADING, RELATIVE_SIZE, LINEAR_PERSPECTIVE]
  subject_at: {X: -15.5, Z: 10}

composition:
  structure: >
    A long lens from below the entry so the clock and its surround fill the lower middle, cropped
    with the brick by the right and bottom edges, and the bleached sky above holds the type.
  bands: >
    Top third, the sky and the hook. Middle third, the dek, then the top of the clock's surround and
    the cast stone coursing. Bottom third, the clock face lit by the noon sun in the foreground, the
    brick pier and the shadow under the surround's edge.
  focal: "the accent sector on the white face"

art:
  technique: "physically based render, the chassis school_clock on the kit school's entry"
  why_this_technique: "the full model is a length of the school day, and a clock is where a school day is measured"
  palette: "white dial, black case, cast stone, buff brick, bleached sky"
  value_structure: >
    Lightest is the dial and the cast stone in sun. Darkest is the case and the shade under the
    surround. Frame median L* planned at 62.

type:
  hook: "Extra help, not a two hour day."
  dek: "Fort Davis ISD enrolls around 800 students. It will use the model in its K-8 classrooms for students who need extra help in reading and math. Alpha's full model has AI teach all students basic subjects in two hours a day."
  labels: []

verbatim: []

acceptance:
  - "a clock face reads at 432px, its surround cropped with the brick by the right or bottom edge"
  - "an accent sector covers two hours of the twelve on the face and nothing else in the frame is the accent"
  - "the face carries no numerals"
  - "the hook sits on the sky above the clock"
  - "the frame's median L* at 432px is between 50 and 76"

risks:
  - "a dial with a coloured sector can read as a gauge with a zone, so the sector is labelled only as two hours a day in the dek and never as a score"
```

```yaml
slide: 7
layout: SPLIT_HORIZON
primary_image:
  subject: "four brick middle school wings receding along a street seen from above, a school bus with the accent card at the near kerb, Houston's towers hazed on the horizon"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: none
job: >
  Give Aldine its size, and land the Houston facts a reader most needs, that the contract is being withheld.

claims: [c24, c25, c26, c27]
numerals:
  - value_from: c24

data_in_art:
  figure: aldine_campuses
  drives: mark count, the school wings receding along the street

depth:
  eye: 28
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: -60}

composition:
  structure: >
    An aerial view over the street so four wings step back in size along it and the skyline hazes
    on the horizon, the type above the horizon in the sky.
  bands: >
    Top third, the sky and the hook. Middle third, the dek, the skyline in haze and the far wings.
    Bottom third, the near wings lit on their roofs, the
    shadow under their walkways and the bus at the kerb.
  focal: "the four wings stepping back along the street"

art:
  technique: "physically based render, the kit school four times, the kit road, school_bus and city_skyline"
  why_this_technique: "four campuses at true scale is a count a reader reads as a neighbourhood"
  palette: "buff brick, flat roofs, asphalt, chrome yellow, Gulf haze"
  value_structure: >
    Lightest is the hazed horizon and roofs. Darkest is the shade under the walk canopies.
    Frame median L* planned at 64.

type:
  hook: "Aldine's pilot spans four middle schools."
  dek: "Aldine will use the platform with roughly 300 students who need math support. Houston ISD plans to use it for students with strong test scores and says it isn't paying Alpha. The district asked the Texas attorney general to let it withhold the pilot contract."
  labels: []

verbatim: []

acceptance:
  - "four school buildings read at 432px, stepping back along a street"
  - "a yellow bus stands at the near kerb with a contact shadow and reads as a bus at 432px"
  - "a city skyline stands hazed on the horizon"
  - "the hook sits on the sky above the horizon"
  - "the frame's median L* at 432px is between 52 and 76"

risks:
  - "four identical wings can read as copies, so each is turned and seeded differently"
```

```yaml
slide: 8
layout: DIAGRAM
primary_image:
  subject: "rendered columns standing on a long oak table at one scale, a glass band for the claimed range, a solid accent column for the share that passed, and a short column beside an empty footprint for the share at grade level"
  rect: [0, 760, 1080, 560]
  bleeds: [left, right]
accent: "#C2477A"
job: >
  Put the one school with scores in front of the reader at one scale, the claim beside the result.

claims: [c28, c39, c40, c42, c43]
numerals:
  - value_from: c39
  - value_from: c28
  - value_from: c42

data_in_art:
  figure: tprep_pass
  drives: column height, the accent column at tprep_pass of a hundred, beside a glass band from alpha_claim_low to alpha_claim_high and a column at tprep_grade_before beside tprep_grade_after

depth:
  eye: 1.5
  horizon: 760
  cues: [CAST_SHADOW, OCCLUSION, FORM_SHADING, RELATIVE_SIZE, LINEAR_PERSPECTIVE]
  subject_at: {X: 0, Z: -2}

composition:
  structure: >
    A near parallel view along the table on a long lens so every column stands at one scale, the
    labels on leaders beside them.
  bands: >
    Top third, the pale wall and the hook. Middle third, the dek and the tops of the columns.
    Bottom third, the columns lit by the window in the
    foreground, each with its contact shadow on the oak.
  focal: "the accent column standing well below the glass band"

art:
  technique: "physically based render, TXT.interior room with the kit conference_table, columns built in the chassis"
  why_this_technique: "a claim and a result at one scale is the only honest way to set them side by side"
  palette: "limestone wall, oak, glass, one accent column, cast stone"
  value_structure: >
    Lightest is the wall and the glass band. Darkest is the table's shade and the columns' contacts.
    Frame median L* planned at 78.

type:
  hook: "Claimed 50% to 60%.<br>Passed, 21%."
  dek: "An Alpha leader told state officials in May 2025 that its platform brought this Austin charter to that pass rate. ProPublica reports TEA's results don't back it up. It got a third straight F."
  labels: ["AN ALPHA LEADER CLAIMED 50% TO 60%", "PASSED 21%", "AT GRADE LEVEL, DOWN FROM 10% TO ZERO"]

verbatim: []

acceptance:
  - "the accent column height equals 21 on the same scale as the glass band's 50 to 60 span, within 5 percent, and reads at 432px"
  - "the glass band spans a range, not a point"
  - "every column stands on the table with a contact shadow"
  - "each label sits beside its own column"
  - "the frame's median L* at 432px is between 66 and 88"

risks:
  - "glass on a pale wall can vanish, so the band carries a visible edge and a tint"
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: "a school bus at a neighbourhood stop at noon with its stop arm out, a parent standing beside it at true scale, a live oak and a brick ranch house behind"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: none
job: >
  Hand the decision to the reader's own district, and name the step a reader can take.

claims: [c22]
numerals: []

depth:
  eye: 1.6
  horizon: 900
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION, FORM_SHADING]
  subject_at: {X: 2, Z: -10}

composition:
  structure: >
    A standing eye on the street, the bus side on at the kerb with its arm out toward the reader's
    lane, the parent beside the front door, the neighbourhood behind.
  bands: >
    Top third, the sky and the hook. Middle third, the dek, the oak's crown and the house roof.
    Bottom third, the sunlit bus in the foreground, its red
    arm, the parent and the kerb with their short shadows.
  focal: "the parent beside the bus and its red arm"

art:
  technique: "physically based render, the kit school_bus, person, live_oak and ranch_house"
  why_this_technique: "a stop on a street is where a district meets a family, which is where this choice now sits"
  palette: "bleached sky, live oak green, buff brick, chrome yellow, one red arm"
  value_structure: >
    Lightest is the sky and the sunlit bus. Darkest is the oak's pool of shade.
    Frame median L* planned at 66.

type:
  hook: "Ask the district that runs this bus."
  dek: "TEA says it left the choice to each district. Ask at your school board's next meeting whether yours was approached about Alpha's platform and what a pilot must prove. A public information request asks it in writing."
  labels: []

verbatim: []

acceptance:
  - "a yellow school bus reads at 432px with its red stop arm out"
  - "a person stands beside the bus at true scale, three quarters away, with a shadow at the feet"
  - "a tree and a house stand behind in the light"
  - "the hook reads 'Ask the district that runs this bus.'"
  - "the frame's median L* at 432px is between 54 and 78"

risks:
  - "the parent can read as a mannequin, so she is turned three quarters away and lit from the camera's side"
```
