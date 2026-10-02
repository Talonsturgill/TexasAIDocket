# Storyboard, 2026-10-02
# "Software pointed at a gene. Flies ran the test."

## The story, and what the fact check did to it

Researchers at the Duncan Neurological Research Institute at Texas Children's Hospital, Baylor
College of Medicine and the Texome Project report in the American Journal of Human Genetics that
variants in BRSK1 are a likely diagnosis for a rare neurodevelopmental disorder (c2, c3, c4, c26).
It began with one child in the Texome Project, free genetic testing for medically underserved
people with rare, undiagnosed conditions (c5, c27). Standard genetic analysis of the child and a
parent found no answer (c7). AI-MARRVEL, a random forest classifier from Baylor trained on over 3.5
million variants (c32, c33), highlighted a rare change in BRSK1 as a promising candidate (c8).
Shared through GeneMatcher (c9, c37), the finding drew in other families: 10 affected individuals
from seven unrelated families (c10), all with some developmental delay, two with seizures (c11,
c13). Fruit flies did the proving. The fly gene is sff, "sugar-free frosting" (c16). With it
disabled the flies had trouble moving and lived shorter lives (c17). The normal human gene largely
corrected them (c18) and the three patient variants modeled (c29) only partially restored them
(c19). The authors' conclusion is a model, not a certainty (c31). A Texas family without the means
to pay for sequencing can ask the Texome Project, whose testing is free over 5 visits in 2 years
(c39, c40, c42, c43).

The record carries this as tx-2026-0195.

**WHAT THE FACT CHECK CHANGED.**
- **98% is never accuracy.** It is a precision rate on one confidence metric, beside 57% of
  diagnosable cases found among 871 (c35). Frame 5 exists to say so.
- **The release's 10 and the paper's nine are never summed.** compute.py checks they agree and the
  sum is never printed.
- **No family is located** beyond the first child, enrolled in a Texas program.
- **No funder is named for the study.** The release defers to the paper.
- **No fly size and no climb height is a measurement.** Where the flies sit on the wall is a
  picture of the release's words "largely" and "partially", never a scale.
- **There is no deadline.** The closing frame's next step is an address, not a date.

## Why this treatment, and what was grafted

Two directors pitched THE OBJECT and THE POINTER AND THE PROOF. Both chose the same hero without
seeing each other, a fruit fly culture vial carried through nine frames, and both put it on a
Houston parapet against the sky because that is how a fly worker reads a vial, held up to the light.
The third pitch, THE READER'S ROAD, carried a roadside mailbox whose flag goes up, and it was refused
as the spine: it keeps the deck out of the lab, so the proof reaches the reader only as printed words,
it reads as a mail metaphor for an email, and its seven boxes on one road would place seven families
the record does not place. Grafted from it: the reader's next step stands on the closing frame as an
address, and the two rules of frame 5 name their own bases so two metrics on one scale are never read
as comparable.

The spine is THE POINTER AND THE PROOF's. The vial has an outside the machine marks and an inside
that has to be alive. The one accent is a strip of tape on the vial, the machine's mark, and it never
touches a fly, so the colour itself refuses to give the tool the credit. The turn (frame 6) is the
moment the claim passes from software into flies.

- From THE OBJECT: the vial rack on the parapet as the deck's comparison (frame 7), and the vial's
  STATE as the progress indicator: sterile, marked, alive, down, compared, full.
- From THE POINTER: the counter-image placed just before the turn (frame 5), the consult room as a
  bookend (frames 2 and 9), and frame 8 as frame 1's camera returned to.
- Refused from both: highNoon. Both pitched it, and it is the right light, but deck no. 38 measured
  60.6 median L*, a light deck inside the eight run window, and brand.yaml caps light decks at one
  per eight. So the deck stands in goldenHour with the sun to the camera's left, which keeps a blue
  sky behind the type and lights the vial's food and plug from the side, and the parapet faces north
  toward downtown.
- Refused: ten kit people standing in a field for the ten individuals (it implies ages and a place
  the record does not give), a map of families, a DNA helix, a dial for 98%, any modelled child, and
  any number printed inside the render.

## The world, and the laws that hold it

**A HOUSTON MEDICAL DISTRICT PARAPET AT GOLDEN HOUR, AND TWO ROOMS IN THE SAME BUILDING.** The
chassis is `assets/js/deck/2026-10-02-vials.js` and every frame loads it. It declares
`sky: goldenHour` (fog thinned to 0.0012 so the far skyline reads as haze, not smog) and one light
at azimuth -78, elevation 7. +x is east and -z is north. The exterior camera looks north along the
coping toward downtown, so the sun comes from its left and every cast falls to its right. The city
beyond the coping is blurred in 2D after the snapshot, as a macro lens holds a few millimetres, and
the vial stays sharp.

The hero is `fly_vial`, a kit addition in the chassis: a clear polystyrene vial 25 mm across and
95 mm tall, cornmeal food at its foot with yeast on top, a cellulose plug, pupae on the wall, adult
flies with red eyes and folded wings. No frame prints a dimension of it.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#20232B` | the DOM body behind the render |
| `accent` | `#4FC79A` | signal_open in brand.yaml, the machine's mark: the tape on the vial and the fills of frame 5's two rules. Never a fly |
| `hook` | `#FBF7EF` | the hook, light on the blue sky |
| `dek` | `#F4F0E8` | the dek |
| `rule` | `#EFEBE4` | the site line, the source line and the counter |

The world's own colours are lit materials: a golden hour blue zenith with a gold seam, precast
concrete gone warm on its sun side, cornmeal food in molasses amber, a cream cellulose plug, fly eyes
in brick red, the hazed glass towers of downtown.

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE
    VALUE CUT: frame 2

1. **Motif evolution.** The vial's state is the progress indicator: alive and marked (1), sterile
   and unmarked (2), marked by the machine (3, 4, 5), alive with the gene off (6), one of five in a
   rack (7), alive and marked again (8), the mark turned away (9).
2. **Camera move.** One coping seen from four positions (the low macro of 1 and 8, square on to the
   rules on 5, the close crop of 6, along the rack on 7) and one room seen twice from the same seat
   (2 and 9), with the bench between them (3 and 4).

## The rotation

    FULL_BLEED  OBJECT_AND_CAPTION  CLOSE_CROP  DOCUMENT  DIAGRAM  CLOSE_CROP  DIAGRAM  FULL_BLEED  OBJECT_AND_CAPTION

`TXLAYOUT.check` returns an empty list.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "one fly culture vial standing on a precast parapet coping, flies on its wall, the strip of green tape at its shoulder, downtown Houston's towers melted into golden hour haze beyond"
  rect: [200, 600, 700, 750]
  bleeds: [bottom]
accent: "#4FC79A"
job: >
  Stop the scroll on the object itself and say the whole turn in the hook, software pointed and
  living flies did the test.

claims: [c1, c2, c3, c8]
numerals: []

depth:
  eye: 18.04
  horizon: 1000
  cues: [AERIAL, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: 0.12}

composition:
  structure: >
    A low macro camera at the vial's foot looks a little up past it, so the vial stands as one
    clear column against the sky and the city's towers sit on the lower third behind it.
  bands: >
    Top third, the blue sky holding the kicker and the hook. Middle third, the dek, then the plug
    and the flies on the wall. Bottom third, the amber food lit warm on its sun side and shaded on the other, the vial's foot casting a soft shadow across the precast coping, and the coping's rounded edge falling away into the hazed towers.
  focal: "the flies on the clear wall between the cream plug and the amber food"

art:
  technique: "physically based render through txthree.js in the deck's goldenHour world, the chassis's fly_vial, the kit city_skyline and hospital towers, the city softened by the world's own haze"
  why_this_technique: "the story's proof is a physical object a person holds up to the light, and only a lit render of it carries that"
  palette: "golden hour blue, gold seam, cream plug, molasses food, precast warm grey, one green tape"
  value_structure: >
    Lightest is the sky's seam behind the skyline. Darkest is the coping in its own shade and the
    flies. Frame median L* planned at 38.

type:
  hook: "Software pointed at a gene. Flies ran the test."
  dek: "Researchers at Texas Children's and Baylor name variants in BRSK1 as a likely diagnosis for a rare disorder that had gone unexplained."
  labels: []

verbatim: []

acceptance:
  - "a clear vial with a cream plug, amber food and dark flies on its wall reads at 432px as one object"
  - "at least ten flies are separately visible on the vial wall at full size"
  - "the green tape is visible on the vial and no fly is green"
  - "the city behind the vial is soft and the vial's edges are sharp"
  - "a horizon with towers on it sits in the lower half of the frame"
  - "the vial's foot touches the coping with a shadow darker than the coping beside it"
  - 'the hook reads "Software pointed at a gene. Flies ran the test."'
  - "no type crosses the plug or the food"

risks:
  - "glass that renders dark or invisible, so the wall carries a clearcoat and a low opacity and is read at 432px"
```

```yaml
slide: 2
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "a consult room in late light, a desk with a stack of papers and a chair, a sterile empty fly vial standing on the desk, and on the wall a study schedule drawn as a rule of months with three follow up flags"
  rect: [0, 860, 1080, 490]
  bleeds: [left, right, bottom]
accent: none
job: >
  Put the reader where the story began, a family's appointment in a Texas program that pays for
  the test, before any machine appears.

claims: [c5, c7, c27, c50]
numerals: []

data_in_art:
  figure: texome_years
  drives: rule length on the wall schedule, one tick per month across the study's years, with the first flag set at followup_months_first

composition:
  structure: >
    Seated eye height across the desk toward the lit window, so the room is quiet and the vial is
    small and alone on the desk before the deck brings it close.
  bands: >
    Top third, the wall and the hook. Middle third, the dek and the wall schedule. Bottom third, the oak desk top catching the window light along its front edge, a ragged stack of papers with its own shadow, the sterile vial standing on the desk with a contact shadow, and the office chair's seat and arms modelled in the falloff.
  focal: "the vial standing alone on the desk in the window's light"

art:
  technique: "physically based render in a room TXT.interior builds, kit desk, office_chair, document_stack, the chassis's fly_vial, a schedule board built in the frame"
  why_this_technique: "the record says where it began, a program a family enrols in, and a room is the honest place for it"
  palette: "warm plaster, oak veneer, window gold, white paper"
  value_structure: >
    Lightest is the window and the paper. Darkest is the floor under the desk. Frame median L*
    planned at 40.

type:
  hook: "One child, and no answer."
  dek: "The child was enrolled in the Texome Project, which offers free genetic testing to medically underserved people with rare, undiagnosed conditions. Standard analysis of the child and a parent did not reveal an answer."
  labels: []

verbatim: []

acceptance:
  - "a desk, a chair and a window read at 432px as a room"
  - "the vial on the desk is empty of flies and carries no green tape"
  - "the wall schedule shows a long rule with tick marks and exactly three flags"
  - "no person is modelled in the room"
  - "the frame shows a lit window and the floor touches the wall with a shadow"
  - 'the hook reads "One child, and no answer."'

risks:
  - "a mid grey wall behind the type, so the window light falls off toward the hook"
```

```yaml
slide: 3
layout: CLOSE_CROP
primary_image:
  subject: "the vial close on a lab bench in front of a monitor, a fresh strip of green tape at its shoulder, the monitor's screen carrying two bars at one scale"
  rect: [0, 620, 1080, 730]
  bleeds: [left, right, bottom]
accent: "#4FC79A"
job: >
  Show the machine's act exactly as large as it was, a mark on the vial and a measured advantage on
  a screen, and nothing more.

claims: [c8, c32, c33, c34]
numerals:
  - value_from: c33

data_in_art:
  figure: solved_multiplier
  drives: bar length, AI-MARRVEL's solved cases bar drawn at solved_multiplier times the benchmarked methods bar at one scale

composition:
  structure: >
    The camera stands close at bench height, the vial cropped by the bottom edge in front and the
    monitor behind it filling the middle, so the mark and the screen are read together.
  bands: >
    Top third, the hook and dek over the dark room. Middle third, the monitor's two bars. Bottom third, the vial's plug and shoulder modelled by the screen's cool light, the green tape wrapped round it, and the bench top's grain running toward the camera into shadow.
  focal: "the green tape on the vial against the lit screen"

art:
  technique: "physically based render in a room TXT.interior builds, kit monitor and desk, the chassis's fly_vial, the screen a canvas texture drawn from figures.json"
  why_this_technique: "the claim is a measured comparison, so two lengths at one scale on the screen carry it without a numeral in the render"
  palette: "dark lab, cool screen light, green tape, amber food"
  value_structure: >
    Lightest is the screen. Darkest is the room behind it. Frame median L* planned at 26.

type:
  hook: "Then software flagged BRSK1."
  dek: "AI-MARRVEL, a classifier trained on over 3.5 million variants, highlighted a rare change in BRSK1 as a promising candidate."
  labels: ["Solved cases, three cohorts", "Benchmarked methods", "AI-MARRVEL"]

verbatim: []

acceptance:
  - "the screen shows exactly two bars and the longer is twice the shorter within five percent"
  - "the labels name both bars and no numeral appears on the screen"
  - "the vial carries the green tape and no fly is green"
  - "the vial is cropped by the bottom edge"
  - 'the hook reads "Then software flagged BRSK1."'

risks:
  - "a screen that blooms the bars away, so the screen's emissive stays under the bloom threshold"
```

```yaml
slide: 4
layout: DOCUMENT
primary_image:
  subject: "a printed page lying on the bench under the window light, a row of ten marks and seven ruled lines on it, the taped vial standing on its corner"
  rect: [200, 560, 700, 790]
  bleeds: [bottom]
accent: none
job: >
  Count what the network found, people and families as two separate counts the record gives, with
  the two who had seizures marked.

claims: [c9, c10, c13, c37]
numerals: []

data_in_art:
  figure: affected_individuals
  drives: mark count on the page, one mark per affected individual, with seizures setting how many are filled and families setting the count of ruled family lines

composition:
  structure: >
    A camera above the bench looks down at the page at a shallow angle, so the marks read as a
    count and the vial standing on the corner keeps it the same object as every other frame.
  bands: >
    Top third, the hook and dek over the dim bench. Middle third, the page's two counts. Bottom third, the page's lower ruled lines in raking light, the vial standing on the page corner with its food lit amber and its shadow across the paper, and the bench's rounded edge in shade.
  focal: "the row of ten marks on the page"

art:
  technique: "physically based render in a room TXT.interior builds, a page built in the frame with its marks as geometry, the chassis's fly_vial"
  why_this_technique: "two separate counts from one sentence want a page that keeps them separate rather than a field of figures"
  palette: "white paper, graphite marks, warm bench, green tape"
  value_structure: >
    Lightest is the page. Darkest is the bench beyond it. Frame median L* planned at 34.

type:
  hook: "Ten people. Seven unrelated families."
  dek: "Shared through GeneMatcher, the finding drew in other families with rare variants in the same gene. Two of the ten had seizures."
  labels: []

verbatim: []

acceptance:
  - "the page carries exactly ten round marks in one row"
  - "exactly two of the ten marks are filled"
  - "the page carries exactly seven ruled lines, separate from the marks"
  - "the vial stands in front of the page's lower right corner with the green tape visible"
  - 'the hook reads "Ten people. Seven unrelated families."'

risks:
  - "marks too small at 432px, so each mark is drawn at 18 mm on a page the camera fills"
```

```yaml
slide: 5
layout: DIAGRAM
primary_image:
  subject: "two lengths of white tape laid along the sunlit parapet coping, each filled with green to its own length, the vial standing at their end, the hazed city beyond"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#4FC79A"
job: >
  The counter-image before the turn. Say what the tool's best number measures and what it does not.

claims: [c35]
numerals:
  - value_from: c35

data_in_art:
  figure: precision_pct
  drives: fill length, the first tape filled to precision_pct of its length and the second to diagnosable_found_pct of the same length

depth:
  eye: 18.32
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, AERIAL, CAST_SHADOW, RELATIVE_SIZE, FORM_SHADING]
  subject_at: {X: 0, Z: 0.12}

composition:
  structure: >
    The camera stands square to the coping and looks along it, so the two tapes run away in
    parallel at one scale and the vial at their end is the scale a reader knows.
  bands: >
    Top third, the hook and dek in the sky. Middle third, the city on the horizon and the far end
    of the tapes. Bottom third, the two tapes running toward the camera at full width with their green fills and edges catching the low sun, their labels beside them, and the vial standing on the coping with its shadow laid across both tapes.
  focal: "where the two green fills stop at different lengths"

art:
  technique: "physically based render in the goldenHour world, two tape rules built in the frame at one length, the chassis's fly_vial, the city softened by the world's own haze"
  why_this_technique: "two percentages of different populations are two lengths at one scale, laid where the reader can see they are not one thing"
  palette: "golden hour blue, warm coping, white tape, green fill"
  value_structure: >
    Lightest is the sky's seam and the tape. Darkest is the coping's shaded face. Frame median L*
    planned at 40.

type:
  hook: "A good pointer is still a pointer."
  dek: "On one confidence metric, AI-MARRVEL reached 98% precision and found 57% of diagnosable cases among 871. That is not its accuracy."
  labels: ["98% precision", "57% of diagnosable cases found"]

verbatim: []

acceptance:
  - "two tapes of equal length lie along the coping and the first green fill is longer than the second"
  - "each tape's label sits beside its own tape, within 24px"
  - "the word accuracy does not appear on any label"
  - "a horizon with towers sits behind the tapes"
  - 'the hook reads "A good pointer is still a pointer."'

risks:
  - "the tapes read as road markings, so the vial stands at their end to set the scale"
```

```yaml
slide: 6
layout: CLOSE_CROP
primary_image:
  subject: "the vial filling the frame top to bottom, its flies down on the food and the low wall, two on their backs, the sky through the clear wall"
  rect: [500, 580, 580, 770]
  bleeds: [right, bottom]
accent: none
job: >
  The turn. The question leaves the software and goes into living flies, and the first thing the
  flies show is what losing the gene does.

claims: [c15, c16, c17]
numerals: []

depth:
  eye: 18.05
  horizon: 1080
  cues: [AERIAL, CAST_SHADOW, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: 0.12}

composition:
  structure: >
    A macro camera at the vial's middle crops it top and bottom, so the reader is inside the
    vial's scale and the flies down on the food are the picture.
  bands: >
    Top third, the hook in the sky beside the plug. Middle third, the empty clear wall where flies
    would climb. Bottom third, the amber food filling the width of the crop, its darker worked surface with yeast grains, and the flies lying on it, two on their backs, every one casting a small shadow on the food.
  focal: "the flies lying on the food surface"

art:
  technique: "physically based render in the goldenHour world at macro scale, the chassis's fly_vial in its down state, the city softened by the world's own haze"
  why_this_technique: "the release says the flies had difficulties moving, and a vial whose flies stay on the food says it without a number"
  palette: "blue sky through clear wall, amber food, brick red eyes, no tape in view"
  value_structure: >
    Lightest is the sky through the wall. Darkest is the flies on the food. Frame median L* planned
    at 42.

type:
  hook: "With the gene off, the flies had trouble moving."
  dek: "The fly version of BRSK1 is called sugar-free frosting. Disabled, it also left the flies with shorter lives."
  labels: []

verbatim:
  - c16: "sugar-free frosting"

acceptance:
  - "the vial is cropped by the bottom edge and its plug's foot sits at the top edge"
  - "most flies are on the food surface and none are near the plug"
  - "no fly is drawn on its back, since no claim says so"
  - "the food's surface fills the vial's width with the flies lying on it"
  - 'the hook reads "With the gene off, the flies had trouble moving."'

risks:
  - "flies on the food lost against the amber, so the food's top is darker than its side"
```

```yaml
slide: 7
layout: DIAGRAM
primary_image:
  subject: "a cardboard tray of five vials on the parapet coping, flies down in the first, spread up the wall in the second, part way up in the last three, downtown in haze behind"
  rect: [100, 640, 980, 710]
  bleeds: [right, bottom]
accent: none
job: >
  The test itself. Set the gene off, the human gene and the patients' versions side by side, so the
  reader sees "largely" and "partially" as places on a wall.

claims: [c18, c19, c29, c51]
numerals: []

data_in_art:
  figure: variants_modeled
  drives: vial count under the patient variant label, one vial per variant modeled

depth:
  eye: 18.06
  horizon: 920
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, FORM_SHADING]
  subject_at: {X: 0, Z: 0.12}

composition:
  structure: >
    The camera stands low and a little to the side of the tray, so the five vials step back in a
    row and their flies read as heights against one another.
  bands: >
    Top third, the hook and dek in the sky. Middle third, the plugs and the climbing flies.
    Bottom third, five amber foods lit from the left in a row, the cardboard tray's lit top and shaded face, the three labels set beneath, and the coping's precast surface catching the sun.
  focal: "the difference between the second vial's high flies and the third's low ones"

art:
  technique: "physically based render in the goldenHour world, the chassis's fly_vial in four states and its vial_tray, the city softened by the world's own haze"
  why_this_technique: "a rescue experiment is a comparison of living populations, and a row of vials is how it looks"
  palette: "golden hour blue, five cream plugs, five amber foods, no tape, the accent kept for the machine"
  value_structure: >
    Lightest is the sky between the vials. Darkest is the tray's shaded face. Frame median L*
    planned at 40.

type:
  hook: "The patients' versions only partly fixed the flies."
  dek: "The normal human gene largely corrected the flies. The team modeled three patient variants, and those restored the flies only partially."
  labels: ["gene off", "human gene", "patient variants"]

verbatim: []

acceptance:
  - "five vials stand in one tray"
  - "the first vial's flies are on the food, the second's spread high up the wall, the last three part way"
  - "the patient variants label spans exactly three vials"
  - "no axis, scale or numeral is drawn against the fly heights"
  - 'the hook reads "The patients'' versions only partly fixed the flies."'
  - 'the labels print "patient variants" on one baseline with "gene off" and "human gene", over a bracket spanning the last three vials'
  - "vial 1 shows no fly above its food and vial 2's flies sit in the top 40 percent of its open wall"

risks:
  - "five vials reading as one blur, so the camera is close enough that each holds 120px"
```

```yaml
slide: 8
layout: FULL_BLEED
primary_image:
  subject: "the opening vial again, closer and from a little higher, the flies spread up its wall, condensation on the glass and the green tape at its shoulder, the city soft behind"
  rect: [290, 510, 540, 840]
  bleeds: [bottom]
accent: "#4FC79A"
job: >
  Say what it adds up to and what it does not, on the same object the deck opened with.

claims: [c3, c11, c12]
numerals: []

depth:
  eye: 18.04
  horizon: 1000
  cues: [AERIAL, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: 0.12}

composition:
  structure: >
    The opening vial again, nearer and seen from a little higher than frame 1, so the reader
    recognises the object and reads the change in its flies and in the words.
  bands: >
    Top third, the hook. Middle third, the dek and the plug. Bottom third, the amber food lit warm on its sun side, the vial's
    foot and its soft shadow on the precast coping, and the hazed towers behind.
  focal: "the flies climbing toward the plug"

art:
  technique: "physically based render in the goldenHour world, the chassis's fly_vial, the kit city, the city softened by the world's own haze"
  why_this_technique: "a bookend is the same picture with the argument now behind it"
  palette: "golden hour blue, gold seam, cream plug, molasses food, green tape"
  value_structure: >
    Lightest is the seam. Darkest is the coping. Frame median L* planned at 38.

type:
  hook: "A likely diagnosis. Not a certain one."
  dek: "Every affected person had some developmental delay. Common features included delayed speech and autism."
  labels: []

verbatim: []

acceptance:
  - "the same vial and coping as frame 1, seen closer, with the skyline behind"
  - "the flies are spread up the wall"
  - "the green tape is visible and no fly is green"
  - 'the hook reads "A likely diagnosis. Not a certain one."'

risks:
  - "reading as a repeat of frame 1, so the flies' places and the light differ and the words carry the turn"
```

```yaml
slide: 9
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "frame 2's consult room from the same seat, the chair pulled back and empty, the full vial on the desk with its tape turned away, the wall schedule now carrying five round visit stickers below its rule"
  rect: [0, 860, 1080, 490]
  bleeds: [left, right, bottom]
accent: none
job: >
  Hand the reader the door. A family that can't pay for sequencing can ask, and the deck says how.

claims: [c39, c40, c42, c43, c50]
numerals:
  - value_from: c43

data_in_art:
  figure: texome_visits
  drives: sticker count on the wall schedule, one round sticker per study visit, spread along the rule's years

composition:
  structure: >
    Frame 2's camera exactly, so the deck ends where it began, with the room now holding the
    answer and the schedule filled.
  bands: >
    Top third, the hook. Middle third, the dek and the schedule with its five stickers. Bottom third, the oak desk top in the window light, the vial standing on it with flies inside and a contact shadow, the stack of papers, and the empty chair pulled back with its seat and arms modelled in the falloff.
  focal: "the five stickers on the schedule"

art:
  technique: "physically based render in a room TXT.interior builds, kit desk, office_chair, document_stack, the chassis's fly_vial, the schedule board built in the frame"
  why_this_technique: "the next step happens in a room like this one, so the deck returns to it"
  palette: "warm plaster, oak veneer, window gold, white paper"
  value_structure: >
    Lightest is the window. Darkest is the floor under the desk. Frame median L* planned at 40.

type:
  hook: "Families who can't pay can ask."
  dek: "Candidates are underserved people with a suspected rare disease who can't pay for sequencing. Testing and follow-up are free, 5 visits in 2 years, in person or virtual. Write to texome-project@bcm.edu."
  labels: []

verbatim: []

acceptance:
  - "the wall schedule carries exactly five round stickers"
  - "the vial on the desk holds flies and its green tape faces away from the camera"
  - "the vial stands at the front of the desk, larger than on frame 2"
  - "the email address in the dek is legible at 432px"
  - 'the hook reads "Families who can''t pay can ask."'
  - 'the dek prints "Write to texome-project@bcm.edu." with the address on one line'
  - "the five stickers sit in one row under the rule as a count, not placed against its months"

risks:
  - "a final frame too like frame 2, so the stickers, the vial's flies and the chair carry the change"
```
