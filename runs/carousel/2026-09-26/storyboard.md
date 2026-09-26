# Storyboard, 2026-09-26
# "Nobody at the wheel"

## The story, and what the fact check did to it

Texas has required a state authorization for commercial driverless vehicles since May 28th, 2026
(c1), and the record admitted it today as tx-2026-0188. On the Dallas to Houston lane, Kodiak says
it will launch "unsupervised long-haul driverless service" by the end of 2026 (c22), its deliveries
from its Lancaster hub to Houston run "without human intervention" (c23), and "the safety observer
never touched the wheel, including on surface streets" (c24). Aurora's release said investor day attendees "will have the opportunity to ride" its trucks "without
a person behind the wheel" on a segment of its Dallas-to-Houston route (c28) and says it is "fully allocated to
exit the year with 200 driverless trucks in operation" (c29).

The authorization is six acknowledged statements (c5 to c10) and a certified first responder plan
(c11). "No fees are required" and authorizations "do not expire" (c12). The department acts when an
operation "has resulted, or is likely to result, in serious bodily injury" (c13) and is "unlikely to
take administrative enforcement action" below that (c14). The City of Dallas asked the department to
require crash history (c18). The department answered that the statute does "not allow" it (c19).

**WHAT THE FACT CHECK CHANGED.**
- **"Unsupervised", never "observer-free".** Kodiak's word (c22). The deck never says when the
  observer leaves, because the release gives no date.
- **The 80 percent is Waabi's own loads**, not corridor freight, and the deck does not use it.
- **219 and 240 are two companies' figures for one corridor** and are never reconciled, averaged or
  differenced. The deck draws Kodiak's 219 (c25) on the map frame and names Waabi's 240 (c33) in text
  only, attributed.
- **Aurora's release gives no count running now.** The 20 is Breitbart's, citing a CNBC ride (c34),
  and the frame that uses it says so. The 200 is an allocation, not trucks running.
- **No fetched record shows which companies hold an authorization.** No frame implies that any of
  the three does.
- **The recorder and the cab are drawn to illustrate.** c6 says only that the vehicle is "equipped
  with a required recording device". The sensor kit is no one company's hardware.

## Why this treatment, and what was grafted

Three directors pitched: THE EMPTY SEAT, THE PERMISSION and THE LANE. The deck is THE EMPTY SEAT's
spine, because every claim in this story is about a person who is not there, and the truck is the
one object every absence is shaped around: the driver gone (c28), the observer's hands off the wheel
(c24), the state at arm's length (c19, c14).

- From THE LANE: the blue hour world and its reason (glass goes dark from outside, a lit cab shows
  its empty seat from inside), the MAP of the lane with Kodiak's 219 as a scale bar, and the close
  at the Houston end with the authorization's run drawn as a bar that becomes a hairline.
- From THE PERMISSION: the recorder as the accent and the counter-image frame, and the six
  acknowledgements drawn as six rows on a sheet lying on the empty seat.
- From THE EMPTY SEAT: the Permian 35 and the 200 on one scale, the cab from its own dash, and the
  review clock as one painted stripe on a truck court.
- Refused: "observer-free", any claim of who holds an authorization, a painted clay "plan" fleet
  (clean clay is a named failure), a seated kit person (the kit has no sit pose, so the observer is
  cropped to hands in a lap).

## The world, and the laws that hold it

**INTERSTATE 45 AT BLUE HOUR IN LATE SEPTEMBER.** The chassis is
`assets/js/deck/2026-09-26-fortyfive.js` and every frame loads it. It declares `sky: 'blueHour'` and
one light at azimuth -160, elevation 32, the high-mast lamps' key inside the preset's lamp range of
25 to 45. Why this light: freight that runs without a driver runs at the hour nobody is watching,
and blue hour is the one hour a truck is known by its lamps rather than its driver. From outside the
cab glass mirrors the sky, which is the question the rule leaves open. From inside, the dash lights
an empty seat. Marker lamps and sensor bands glow under the bloom knee, and only the recorder's
lamp clears it.

**ONE HERO OBJECT.** The kit's `semi_truck` (Class 8 long-hood sleeper and 53 ft van), unbranded,
carrying the chassis's sensor kit, and the chassis's CAB set for every frame inside it. The cab and
the sensors are illustrative and a frame that shows them close says so.

**THE RECORDER LAMP IS THE MOTIF AND THE ACCENT.** `#E0956A`, dusk_gold from config/brand.yaml,
worn by the recording device's 6 mm status lamp and one tick on the sheet, frames 3, 6 and 7. The
amber marker lamps stay yellower (`#FFB547`) and under 1.0 so nothing competes.

**THE MUTE WORLD LAW.** No logo, no fleet name, no readable plate, no real hub. The truck court and
the yards stand for a kind of place.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#151D33` | the DOM body behind the render |
| `accent` | `#E0956A` | the recorder lamp (3, 7), the recording device tick (6) |
| `hook` | `#F3F1EC` | the hook on every frame, on the sky or the dark cab |
| `dek` | `#E3E7EE` | the dek on every frame |
| `rule` | `#C8D1DC` | the site line, the source line and the counter |

The world's own colours are lit materials: pale continuously reinforced concrete lanes, black
Blackland clay verges, September straw, cedar elm olive, a white fleet tractor, blue hour cobalt
with an amber seam in the west. Frame 4 alone stands on Permian caliche because its claim is there.

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE, VALUE_ARC
    VALUE CUT: frame 6

The one hard cut is frame 6, and it is the turn: the deck leaves the lane and the yards, where
the companies' numbers live, and goes back into the dark cab to read the state's own paper.

1. **Motif evolution, the empty seat and the record.** The seat is seen empty through the glass
   (1), empty beside the observer's hands with the recorder lamp lit behind it (3), empty 35 times
   (4), empty in 20 rigs among 200 stalls (5), holding the state's paper (6), with the recorder over
   it (7), rolling down the review stripe (8) and passing under a Texan (9).
2. **Camera move.** Outside the cab (1), above the state (2), inside the cab (3), up high over two
   yards at one scale (4, 5), back inside at the seat (6) and the bulkhead (7), out onto a court (8),
   and up on an overpass rail (9).
3. **Value arc.** One world, and the camera turns steadily away from the amber seam toward the
   deeper blue, so the ground steps down from frame 1 to the Houston end and never back up.

## The rotation

    FULL_BLEED  MAP  CLOSE_CROP  FULL_BLEED  FULL_BLEED  DOCUMENT  CLOSE_CROP  DIAGRAM  SPLIT_HORIZON

`TXLAYOUT.check` returns an empty list. Seven distinct, no TYPE_AS_OBJECT, FULL_BLEED and CLOSE_CROP
three between them, eight frames bleeding an edge.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "a white Class 8 tractor with a 53 ft van coming toward the camera in the right lane of I-45 at blue hour, sensor pods on its mirror arms, headlamps on, the dark windshield mirroring the sky, the concrete lanes and a Blackland verge running off the bottom"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: none
job: >
  Stop the scroll on a truck a Texan has passed a thousand times, and make the one wrong thing about
  it the question the deck answers, before a word of policy.

claims: [c22, c25, c28]
numerals:
  - value_from: c22   # 2026, the end of 2026 target
  - value_from: c25   # 45, Interstate 45 in the kicker


depth:
  eye: 0.8
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, OCCLUSION, CAST_SHADOW, FORM_SHADING]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A low three quarter front camera on the right shoulder puts the tractor's grille and pods on the
    right third, the van running off the left edge behind it, and the lanes converging to the amber
    seam on the left. The type sits in the deep blue sky above the horizon.
  bands: >
    Top third, the blue hour sky deepening to cobalt with the hook and the dek. Middle third, the
    amber seam on the horizon, the lit cab front with its sensor pods and the dark windshield, the
    fencerow in haze. Bottom third, the pale concrete lanes with skip lines modeled by the lamps, the
    rumble strip and the Blackland verge with straw grass lit from the side, the tyres and their
    contact shadows.
  focal: "the lit grille and the dark windshield above it, the one place a driver should be"

art:
  technique: "physically based render through txthree.js in the declared blueHour world, the kit highway and semi_truck, scatter kept off the type, contact and weather, bloom on lamps only"
  why_this_technique: >
    The claim is a real vehicle on a real road. Only a render at true size, lit like the hour it
    runs, makes the dark windshield read as a question rather than a design choice.
  palette: "cobalt zenith, amber seam, white tractor paint, black glass, pale concrete, Blackland black verge, straw grass"
  value_structure: >
    Lightest is the amber seam and the headlamps. Darkest is the windshield and the verge in the
    lower corners. The hook sits on the mid blue sky. Frame median L* planned at 30.
  motion: "from the hook down to the windshield, then along the lane to the seam"

type:
  kicker: "Interstate 45, Dallas to Houston"
  hook: "Nobody at the wheel"
  dek: "Kodiak plans unsupervised driverless service on the Dallas to Houston lane by the end of 2026. Aurora said investor day guests could ride part of its route with nobody behind the wheel."

acceptance:
  - "the frame reads \"Nobody at the wheel\""
  - "the tractor's front and both mirror sensor pods are visible and the van runs back toward the left edge"
  - "a fencerow of cedar elm and high-mast lamps stand beyond the lane under a blue sky"
  - "the headlamps bloom and no painted surface does"
  - "no grass blade, lamp or truck edge crosses the hook or the dek"
  - "no logo, fleet name or legible plate appears anywhere on the truck"

risks:
  - "the windshield must stay dark from outside, the deck's point, and frame 3 answers it from inside"
```

```yaml
slide: 2
layout: MAP
primary_image:
  subject: "Texas's counties in the Albers projection under the type, Dallas County and Harris County lit and marked at their centroids, no line joining them, and a scale bar at Kodiak's 219 miles computed through the projection"
  rect: [0, 440, 1080, 910]
  bleeds: [left, right, bottom]
accent: none
job: >
  Make the lane a place with a length, in the company's own number, so the reader knows the size of
  the road the rest of the deck is on.

claims: [c25, c32, c33]
numerals:
  - value_from: c25   # 219 miles
  - value_from: c33   # 240, Waabi's figure, text only

data_in_art:
  figure: kodiak_lane_miles
  drives: the scale bar's length in px, computed from the projection's own scale at the corridor's latitude

composition:
  structure: >
    The state fills the lower two thirds, cropped so the east half of Texas sits large. The two
    endpoint counties glow and a dashed line joins Lancaster to Houston. The scale bar lies along the
    Gulf coast below it with its own mono label, and the type sits in the dark above the Panhandle.
  bands: >
    Top third, the hook and the dek over the dark field above the state. Middle third, North and
    Central Texas with Dallas County lit and marked, the dashed line starting south.
    Bottom third, the line reaching the lit Harris County and the Houston mark, and the scale bar
    at the lower left over South Texas counties shaded by the raking light.
  focal: "the two lit counties and the scale bar"

art:
  technique: "cartography from assets/geo through TXGeo, the county mesh shaded by a low raking light, the scale bar and marks in mono"
  why_this_technique: >
    The claim is a distance between two named places. A map is the only picture of that, and the
    projection is what makes the scale bar a measurement rather than a decoration.
  palette: "near black blue field, slate county fills, the two endpoint counties in a lit steel blue, pale county lines, the bar in the rule colour"
  value_structure: >
    Lightest is the two lit counties and the scale bar. Darkest is the field around the state.
    Frame median L* planned at 22.
  motion: "from the hook to Dallas County, down to Harris County, to the bar"

type:
  kicker: "The lane"
  hook: "219 miles, Kodiak says"
  dek: "That is Kodiak's figure for the Dallas and Houston metros along Interstate 45. Waabi hauls the same corridor and calls it roughly 240."

acceptance:
  - "the frame reads \"219 miles, Kodiak says\""
  - "Dallas County and Harris County are the only lit counties"
  - "the scale bar is labelled with Kodiak's 219 miles and its length is computed from the projection"
  - "no drawn length joins the two counties, so no line can be read as either company's distance"
  - "no numeral 240 is drawn in the art, only in the dek"

risks:
  - "a line between the endpoints would equal the bar and be read as the distance, so none is drawn"
```

```yaml
slide: 3
layout: CLOSE_CROP
primary_image:
  subject: "inside the cab from the bunk looking forward through the windshield at blue hour: the empty driver's wheel on the left, the passenger seat back on the right with the observer hidden behind it, the recorder's lamp lit on the overhead console, and the lane running ahead to the horizon"
  rect: [0, 420, 1080, 660]
  bleeds: [left, right]
accent: "#E0956A"
job: >
  Answer the cover from inside. There is somebody aboard, and nobody is driving.

claims: [c23, c24]
numerals: []

depth:
  eye: 3.2
  horizon: 560
  cues: [LINEAR_PERSPECTIVE, OCCLUSION, RELATIVE_SIZE, AERIAL, FORM_SHADING]
  subject_at: {X: 0.55, Z: -0.2}

composition:
  structure: >
    The camera sits on the dash looking back into the cab, so the empty driver's seat and the wheel
    rim take the left edge, the observer sits on the right third, and the recorder glows on the
    bulkhead between them. The type sits on the dark headliner at the top.
  bands: >
    Top third, the headliner in shadow with the hook and the dek. Middle third, the two headrests, the
    recorder's lit housing on the bulkhead between them, the observer's head and shoulder.
    Bottom third, the pleated vinyl seat backs modeled by the dome light, the wheel's dark rim
    at the left edge, and the observer's shirt and arm at the right edge.
  focal: "the empty seat and the wheel against the lit lane"

art:
  technique: "physically based render of the chassis cab set with the kit highway outside, the world's sky through the glass, dome light and dash emissive"
  why_this_technique: >
    The claim is a behaviour, hands that never touched the wheel. It can only be shown as a real
    seat, a real wheel and hands somewhere else, at the size a person knows.
  palette: "dark vinyl, charcoal dash, warm dome pool, cool blue glass, amber seam, pale concrete"
  value_structure: >
    Lightest is the lane and seam through the glass. Darkest is the headliner behind the type.
    Frame median L* planned at 26.
  motion: "from the hook down to the wheel, out through the glass to the lane"

type:
  kicker: "Inside the cab"
  hook: "Hands off the wheel"
  dek: "A safety observer rides on Kodiak's deliveries from Lancaster to Houston. Kodiak says the observer never touched the wheel."

acceptance:
  - "the frame reads \"Hands off the wheel\""
  - "the driver's seat is empty and no hand touches the wheel"
  - "the recorder's lamp is the only point of #E0956A on the frame"
  - "the windshield shows the blue hour sky and the lane ahead"

risks:
  - "the observer is hidden by the passenger seat back, so no face or pose is invented"
```

```yaml
slide: 4
layout: FULL_BLEED
primary_image:
  subject: "thirty five white bobtail tractors with sensor pods parked seven across and five deep on a pale caliche pad in the Permian at blue hour, seen from a high oblique with the haze horizon at the top edge, every cab empty and casting its shadow, mesquite at the pad's edge"
  rect: [0, 500, 1080, 850]
  bleeds: [left, right, bottom]
accent: none
job: >
  Show that the end state already exists in Texas, counted one truck per truck, in the company's
  own number.

claims: [c27]
numerals:
  - value_from: c27   # 35 trucks

data_in_art:
  figure: permian_trucks
  drives: mark count, 35 rendered tractors read from figures.json

depth:
  eye: 180
  horizon: 440
  cues: [RELATIVE_SIZE, CAST_SHADOW, FORM_SHADING, AERIAL, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A long lens from high above flattens the block of tractors to one size. The rows fill the lower
    two thirds, running off the sides, and the horizon with a pump jack sits high under the type.
  bands: >
    Top third, the blue sky with the hook and the dek over a thin caliche horizon and a small pump
    jack. Middle third, the first rows of tractors, each a white roof and hood casting a soft shadow.
    Bottom third, the nearest rows on the pale caliche pad with tyre tracks, mesquite scrub and
    grass at the pad edge, each tractor's contact shadow dark on the caliche.
  focal: "the block of thirty five white cabs"

art:
  technique: "physically based render, the chassis truck instanced as a bobtail thirty five times, caliche ground, scrub scatter off the pad"
  why_this_technique: >
    A count of machines wants the machines, each countable, at one scale. The render makes each one a
    truck a reader recognises rather than a mark.
  palette: "white tractor paint, pale caliche, mesquite olive, cobalt sky, amber seam"
  value_structure: >
    Lightest is the white cab roofs and the caliche. Darkest is the shadows between the rows. Frame
    median L* planned at 40.
  motion: "from the hook down into the rows"

type:
  kicker: "The Permian Basin"
  hook: "35 already ran with nobody in the cab"
  dek: "Kodiak says 35 driverless trucks were running commercially in its Permian Basin deployment with no humans in the cab at the end of the second quarter."

acceptance:
  - "the frame reads \"35 already ran with nobody in the cab\""
  - "exactly 35 tractors are rendered and each reads as a separate truck at 432 px"
  - "no grass or scrub crosses the hook or the dek"

risks:
  - "the only frame off the corridor, argued as the same seat on the other Texas"
```

```yaml
slide: 5
layout: FULL_BLEED
primary_image:
  subject: "a truck yard at blue hour from a high oblique: 200 painted places in twenty rows of ten on dark asphalt receding to the haze, twenty tractors with lamps lit parked in the two nearest rows, oil stains under them, a mast lamp pooling at each side"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: none
job: >
  Put Aurora's year end number and the reported number running now on one scale, each named for the
  set it counts.

claims: [c29, c34]
numerals:
  - value_from: c29   # 200
  - value_from: c34   # 20

data_in_art:
  figure: aurora_trucks_year_end
  drives: painted stall count, 200, and the occupied stall count from aurora_trucks_now_reported, 20

depth:
  eye: 40
  horizon: 0
  cues: [RELATIVE_SIZE, CAST_SHADOW, FORM_SHADING, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    From above the near aisle, the yard is a field of places. Twenty rows of ten recede from the
    lower third to the haze, the twenty tractors fill the two nearest rows, and the type sits on the far rows.
  bands: >
    Top third, dark asphalt under the hook and the dek. Middle third, rows of empty painted places,
    each a pale pad with its own edge, forty to a row. Bottom third, the nearest row with twenty
    white tractors parked in its first places, roofs and hoods with modeled form and a soft contact
    shadow under each on the pale pads, and the pads beyond them running on to the right edge over the
    asphalt texture.
  focal: "the one row of twenty tractors against a field of empty places"

art:
  technique: "physically based render from a long lens overhead, instanced stall stripes as their own lower roughness material, the chassis truck twenty times, mast lamps"
  why_this_technique: >
    Two counts at one scale, one of them a plan and one a report, need the plan drawn as places and
    the report drawn as trucks, so neither is mistaken for the other.
  palette: "grey concrete, white stall paint, white rigs, warm mast pools, blue shadow"
  value_structure: >
    Lightest is the rig roofs and the lamp pools. Darkest is the concrete at the top behind the
    type. Frame median L* planned at 28.
  motion: "from the hook down the empty stalls to the row of rigs"

type:
  kicker: "Aurora's year"
  hook: "200 places, 20 trucks"
  dek: "Aurora says it is fully allocated to end 2026 with 200 driverless trucks. Breitbart puts the fleet running now at 20. It cites a CNBC ride."

acceptance:
  - "the frame reads \"200 places, 20 trucks\""
  - "exactly 200 places are painted and exactly 20 hold a tractor, each cab readable at 432 px"
  - "the dek attributes the 20 to Breitbart citing CNBC"

risks:
  - "the yard is an illustration for counting and is not Aurora's real yard"
```

```yaml
slide: 6
layout: DOCUMENT
primary_image:
  subject: "the empty driver's seat seen from under the roof, a letter sheet lying on the cushion with six ruled rows and six tick boxes, the second tick in dusk gold, the dome light pooling on it, the windshield's blue at the top edge"
  rect: [0, 420, 1080, 930]
  bleeds: [left, right, bottom]
accent: "#E0956A"
job: >
  Show how little paper the permission is. Six statements on a page that lies where a driver would
  sit, no fee and no expiry.

claims: [c1, c5, c6, c7, c8, c9, c10, c12]
numerals:
  - value_from: c1    # May 28th, 2026
  - computed_by: "out/2026-09-26/compute.py, the count of acknowledgements c5 to c10"

data_in_art:
  figure: acknowledgements
  drives: the ruled row count and tick count on the sheet, six, with no seventh line

depth:
  eye: 2.9
  horizon: 120
  cues: [OCCLUSION, FORM_SHADING, CAST_SHADOW, RELATIVE_SIZE]
  subject_at: {X: 0.55, Z: 0.2}

composition:
  structure: >
    Looking down past the wheel rim onto the seat cushion, the sheet lies on it slightly turned. The
    six rows and ticks are geometry on the page. The type sits on the dark headliner and windshield
    band at the top.
  bands: >
    Top third, the seat back and headrest in shadow behind the hook and the dek. Middle
    third, the wheel rim cropped across and the sheet's top rows. Bottom third, the sheet's lower
    rows with their tick boxes on the dark vinyl cushion, the bolster modeled by the dome light and
    the seat belt buckle in shadow.
  focal: "the sheet on the seat and its second tick"

art:
  technique: "physically based render inside the chassis cab set, the sheet as a bent plane with ruled geometry and extruded ticks, dome light pool"
  why_this_technique: >
    The claim is the size of a permission. A page on the seat a driver would use is the size of it,
    in the place it replaces a person.
  palette: "dark vinyl, white sheet, charcoal rules, dusk gold tick, warm dome pool"
  value_structure: >
    Lightest is the sheet. Darkest is the headliner behind the type. Frame median L* planned at 24.
  motion: "from the hook down to the sheet, row by row"

type:
  kicker: "The permission"
  hook: "Six statements and no fee"
  dek: "Since May 28th a company running vehicles with no driver needs a state authorization. The company acknowledges six statements and pays nothing. The authorization does not expire."

acceptance:
  - "the frame reads \"Six statements and no fee\""
  - "the sheet carries exactly six ruled rows and six ticks"
  - "the second tick, the recording device row, is the only #E0956A on the frame"
  - "the driver's seat is empty"

risks:
  - "no row text is legible in the art, so no statement is paraphrased on the page"
```

```yaml
slide: 7
layout: CLOSE_CROP
primary_image:
  subject: "the recording device on a worn painted steel kick panel bolted to the sleeper bulkhead, its charcoal finned housing under a neutral dome light, its one dusk gold status lamp blooming, the seat backs either side"
  rect: [160, 560, 760, 600]
  bleeds: []
accent: "#E0956A"
job: >
  The turn. The truck must carry a recorder, and the state that authorizes it can't require its
  crash history.

claims: [c6, c18, c19]
numerals:
  - value_from: c19   # 545.453 and 545.456, the sections, text only

depth:
  eye: 2.6
  horizon: 520
  cues: [OCCLUSION, FORM_SHADING, CAST_SHADOW, AERIAL]
  subject_at: {X: 0, Z: 0.9}

composition:
  structure: >
    A detail camera between the seats a meter from the housing puts the recorder just under the
    middle, on a tread plate panel that runs off three edges. The type sits on the dark curtain above.
  bands: >
    Top third, the dark bulkhead and curtain behind the hook and the dek. Middle third, the
    mounting plate and the recorder's fins catching the dome light. Bottom third, the tread plate's
    lugs breaking the dome light into glints, falling off into shadow at the floor.
  focal: "the lit status lamp on the housing"

art:
  technique: "physically based render at detail scale inside the chassis cab set, emissive driven bloom on the lamp only"
  why_this_technique: >
    The counter-image is one physical thing, the record, and one refusal. A close render of the thing
    with its lamp on is the record present in the truck.
  palette: "brushed aluminium, charcoal carpet, dusk gold lamp, cool blue window light"
  value_structure: >
    Lightest is the lamp and the fin highlights. Darkest is the bulkhead behind the type. Frame median
    L* planned at 20.
  motion: "from the hook down to the lamp"

type:
  kicker: "What the state can't ask for"
  hook: "It carries a recorder"
  dek: "The truck must be equipped with a recording device. Dallas asked the state to require crash history too. The department said the statute does not allow it."

acceptance:
  - "the frame reads \"It carries a recorder\""
  - "the recorder's lamp is the only #E0956A on the frame and it blooms"
  - "the recorder is labelled drawn to illustrate in the source line"

risks:
  - "the recorder's form and place are illustrative, since c6 gives neither"
```

```yaml
slide: 8
layout: DIAGRAM
primary_image:
  subject: "a concrete truck court at blue hour from a high oblique, a white rig parked parallel to the dock, and one painted stripe across the court in three segments at a quarter meter per day, with mono labels on leaders"
  rect: [0, 540, 1080, 480]
  bleeds: [left, right]
accent: none
job: >
  Draw when the state steps in and how long an operator can be kept off the road, as a length a
  reader can pace.

claims: [c13, c15, c16, c17]
numerals:
  - value_from: c15   # 10 days
  - value_from: c16   # 10 and 60 days
  - computed_by: "out/2026-09-26/compute.py, soah.longest_path_days, 10 plus 10 plus 60"

data_in_art:
  figure: soah.longest_path_days
  drives: the stripe's total length in meters at a quarter meter per day, split into soah.request_days, soah.file_days and soah.hearing_days segments

depth:
  eye: 24
  horizon: 430
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, FORM_SHADING, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    A high oblique down the court lays the rig left to right across the middle and the stripe under
    it, its three segments separated by gaps, the whole review about one rig long. Mono labels on DOM leaders
    sit above the stripe. The type sits in the sky over the warehouse roofline.
  bands: >
    Top third, the blue hour sky with the hook and the dek above the warehouse roofline. Middle
    third, the dock face with its doors and the rig backed in, lamps pooling on the concrete. Bottom
    third, the painted stripe segments on the tined concrete with shadowed joints, the rig's long
    cast shadow reaching across them, the court's wheel marks and oil stains modeled by the lamps.
  focal: "the long third segment of the stripe"

art:
  technique: "physically based render of the kit warehouse and chassis truck on concrete, the stripe as its own lower roughness material, DOM SVG leaders"
  why_this_technique: >
    A sequence of durations is a quantity and wants one scale. Painting it at one scale beside the
    rig makes the whole review a length a reader can hold against a truck.
  palette: "grey concrete, white stripe, white rig, warm mast pools, blue sky"
  value_structure: >
    Lightest is the stripe and the rig. Darkest is the dock doors. Frame median L* planned at 30.
  motion: "from the hook down to the rig, along the stripe to its end"

type:
  kicker: "When the state steps in"
  hook: "The line is serious bodily injury"
  dek: "The department counts an operation as endangering the public when it has caused or is likely to cause serious bodily injury. After a final decision an operator has 10 days to ask for a hearing. If it isn't held in time the authorization is reinstated."

acceptance:
  - "the frame reads \"The line is serious bodily injury\""
  - "the stripe's three segments are set from figures.json soah at a quarter meter per day"
  - "every leader ends on the stripe segment it labels, and the end label says reinstatement happens only if the hearing is not held"

risks:
  - "the stripe is drawn at a quarter meter per day and the source line says it is drawn to scale, so it is not a real marking"
```

```yaml
slide: 9
layout: SPLIT_HORIZON
primary_image:
  subject: "a Texan at an overpass rail over I-45 at the deepest blue of the hour, the white rig passing south beneath with its tail lamps lit, the lanes running to Houston's glow on the horizon; below the cut, one bar from May 28th to today becoming a hairline to the edge"
  rect: [0, 360, 1080, 990]
  bleeds: [left, right, bottom]
accent: none
job: >
  Close on the one person in the deck with a way in, and on the authorization's own run, which has
  no end date.

claims: [c1, c12, c36, c37]
numerals:
  - value_from: c1    # May 28th
  - computed_by: "out/2026-09-26/compute.py, days_enforceable_to_run"

data_in_art:
  figure: days_enforceable_to_run
  drives: the bar's length in px at the frame's day scale, followed by a hairline to the right edge

depth:
  eye: 8.6
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, AERIAL, OCCLUSION, CAST_SHADOW]
  subject_at: {X: -1, Z: 30}

composition:
  structure: >
    The upper sixty percent is the render from behind the Texan on the overpass, the rig below
    heading away down the lanes toward the glow. Below the cut, on the dark ground band, the bar runs
    from its May 28th tick to a today tick and continues as a hairline. The hook and dek sit in the
    band under the bar.
  bands: >
    Top third, the deep blue sky and the far glow of Houston on the horizon over the lanes. Middle
    third, the Texan's shoulder and the rail at the left, the rig's van roof and tail lamps below,
    streetlights along the ramp. Bottom third, the overpass deck's concrete parapet in the foreground
    modeled by the streetlight, falling into the dark band that carries the bar, its ticks and the
    hook and dek.
  focal: "the rig's tail lamps heading away under the Texan's gaze"

art:
  technique: "physically based render in the blueHour world with the kit highway, overpass, person and chassis truck; a DOM SVG bar below the cut"
  why_this_technique: >
    The close is a person and a duration. The render gives the person and the truck their sizes, and
    the bar puts the only open-ended number in the story on a scale.
  palette: "deepest cobalt, warm city glow, red tail lamps, pale lanes, the rule colour for the bar"
  value_structure: >
    Lightest is the city glow and the tail lamps. Darkest is the band below the cut. Frame median
    L* planned at 18.
  motion: "from the Texan's shoulder down to the tail lamps, then down to the bar and the dek"

type:
  kicker: "If you see one"
  hook: "A way in"
  dek: "A concern about a driverless vehicle that could cause serious bodily injury or death can go to the TxDMV Enforcement Division at txmccs.txdmv.gov/truckstop. Law enforcement can verify authorizations there too."

acceptance:
  - "the frame reads \"A way in\""
  - "the bar starts at a tick labelled May 28th and ends at a tick labelled today, and a hairline runs on to the right edge"
  - "the Texan stands at the rail and the rig passes beneath"
  - "no tail lamp or streetlight crosses the hook, the dek or the bar labels"

risks:
  - "the day scale is stated on the bar so the length reads as days"
```
