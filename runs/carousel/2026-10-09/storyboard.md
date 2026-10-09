# Storyboard, 2026-10-09
# "The question is asked inside the chart"

## The story, and what the fact check did to it

UTMB and OpenEvidence announced on September 22nd (c1, c3) that OpenEvidence, an AI platform that answers
clinical questions with citations, is embedded inside UTMB's electronic health record environment (c2, c5).
It went live in March (c4). Clinicians sign in with their standard UTMB credentials (c6), ask in natural
language and get answers that cite medical literature and guidelines (c7). UTMB says more than half of its
clinicians actively use it (c9), that use and queries grew strongly (c8), and that it will keep evaluating
utilization and clinician experience (c17). UTMB has hospitals on four campuses and more than 100 clinics
across Southeast Texas (c11, c12). Texas Health and Safety Code Sec. 183.005 (c18), added by S.B. 1188 (c24)
and in force since September 1st, 2025 (c25), lets a practitioner use AI for diagnostic purposes under three
conditions (c19 to c22) and says a practitioner who does so must disclose it to patients (c23). UTMB's other
AI contract, with Qualified Health, grew from $825,000 to $9,850,000 and reaches all seven UT health
institutions (c28 to c31, c34, c35). The Regents meet next on November 18th to 19th in Austin (c42), and the
public may testify on agenda topics with 24 hours' notice (c43 to c45). The record carries the decision as
tx-2026-0208, with tx-2026-0094 and tx-2026-0151 as context.

**WHAT THE FACT CHECK CHANGED.**
- **The statute and UTMB are never linked.** No source says OpenEvidence use is "diagnostic purposes". The
  deck sets the statute beside UTMB's account, quotes both terms and says no source read says which it is.
  It never says UTMB must disclose, did not, or broke anything.
- **No accuracy figure exists in the release.** The deck says so, naming the release, and never suggests the
  tool is inaccurate.
- **"More than half" has no denominator.** The fill is drawn to half and left open, and the frame says the
  total is not published.
- **The Qualified Health contract is not OpenEvidence**, and no vote record was read, so never "approved".
- **March has no year.** No span from March is drawn or printed.

## Why this treatment, and what was grafted

Three directors pitched THE OBJECT (one clinical workstation cart whose monitor swivels from the clinician
toward the reader across the deck), THE PLACE (a small clinic at night with one exam room lit, the region's
clinics as lights on a flat horizon) and THE EVIDENCE (the cart standing beside measured exhibits at true
scale: a share column, the statute as steps, the contract as three columns).

- From THE OBJECT, the hero and the spine: `workstation_cart`, built once in the chassis, and the monitor's
  swivel as the progress motif, 0 on the cover (its back to the reader) to 180 at the close (its face to
  the reader). The barrier with the half fill (4) and the held camera with the measured bars (5). The exam room
  page (6) and the turned screen (8).
- From THE PLACE, the horizon of clinic lights behind the cart on the cover and the close, one light per
  clinic up to the claim's floor of 100, placed for the drawing.
- From THE EVIDENCE, the contract as three galvanized columns at one scale with the cart at the foot of the
  shortest, its screen dark (7).
- Refused: the clinic building as a new kit model (a 26 m model with eight rooms against a deadline is the
  defect no. 34 was charged for), the statute as limestone steps (a metaphor a judge has to decode), people
  at face scale (the open mannequin defect), and a hearing room (no. 42 drew one five days ago).

## The world, and the laws that hold it

**A CLINIC'S CONCRETE APRON ON THE FLAT UPPER GULF COAST AT NIGHT, UNDER ONE COLD LED FLOOD.** The chassis is
`assets/js/deck/2026-10-09-chart.js` and every frame loads it. It declares `sky: floodlit` with the haze at
#0E1220 and the light at azimuth -50 and elevation 40, high on camera left. +x is east, +z is south.

1. **Start dark.** A black sky, the cart in a pool of cold light, the world behind it gone dark. Every
   exterior frame stages its subject.
2. **Type is light, on the dark field**, and every wash only darkens.
3. **The screen lights only itself.** It is an unlit material, so no lamp prints a hotspot on it, and a
   frame that wants its glow on a surface adds `CH.screenLight`.
4. Every standing thing gets `TXT.contact`, every frame `TXT.weather`.
5. **No legible UI, no maker, no label on the cart.** The screen is drawn to illustrate.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#0C0D11` | the DOM body behind the render |
| `accent` | `#E3A83B` | badge amber, what the record prints and a reader can point to: the 100 clinic lights on 1 and 9, the strip under each campus cart on 3, the half fill on 4, the (b) line on the statute page on 6. Absent on 2, 5, 7 and 8 |
| `hook` | `#EEF1F2` | light type on the dark sky |
| `dek` | `#DDE2E4` | the dek |
| `screen` | `#DFEAF2` | the cool clinical white of the cart's lit screen, the deck's one practical |

The world's materials: the cart's off white powder coat over aluminium, grey ABS, black housing, rubber
casters; shell aggregate concrete going to black at the pool's edge; galvanized steel; a cool clinical white
screen #DFEAF2. Nothing warm except the accent.

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE

1. **Motif evolution.** The one cart, its monitor swivelling: back to the reader on the cover (1), facing the
   clinician's eye (2), four carts all facing away (3), edge on at the half (4), turned three quarters away (5),
   dark (6), lit over the page (7), turned toward the patient's chair (8), facing the reader (9). The face square
   to the reader comes only on 2, the clinician's own view, and on 9.
2. **Camera move.** Close and low on the apron (1), the clinician's standing eye (2), a long lens down the
   row (3), the same held camera on the barrier (4, 5), a long lens at the columns' foot (6), down onto the
   work surface (7), from the patient's chair (8), and frame 1's camera returned (9).
Edge tease was planned and struck after flow round 1: the barrier stands whole on 4, and two devices carry the deck.

## The rotation

    FULL_BLEED  CLOSE_CROP  OBJECT_AND_CAPTION  DIAGRAM  DIAGRAM  FIGURE_SCALE  DOCUMENT  OBJECT_AND_CAPTION  FULL_BLEED

`TXLAYOUT.check` returns an empty list.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | CLOSE, eye 1.15 m, 2.6 m off the cart's back left quarter, horizon on the lower third | the cart, powder coat with scuffs over a cast aluminium star base, rubber twin casters with contacts on shell concrete, the monitor's vented black housing rimmed by the flood with the screen's light leaking round it |
| 02 | MEDIUM, eye 1.55 m at the push bar, looking down at the screen and surface | the monitor face and work surface, the illustrated answer with citation chips, the badge reader's amber LED off, keyboard keys instanced, a back wall in shadow |
| 03 | WIDE, eye 1.2 m, long lens fov 16, 28 m down a row of four | four carts at one size, staged as one subject, each on an amber strip, monitors away and lit |
| 04 | MEDIUM, eye 1.0 m, 7 m off a 4 m precast barrier lying across the frame | the barrier, precast concrete with arrises and a cast channel, the amber fill to its half tick then open, the cart at the left third side on |
| 05 | MEDIUM, frame 4's camera held | the same precast barrier, cast concrete with chipped arrises and a cast channel, two brushed aluminium bars bedded in it catching the cold flood, contacts and grime where the barrier meets the apron, an empty third channel, the cart past side on |
| 06 | WIDE, eye 1.2 m, long lens fov 18, square on to three galvanized columns | three galvanized columns at one scale, each a bevelled square tube in spangled galvanized steel with a weld bead, bolted base plates with contacts on the concrete, lit on the flood side and dark on the far side, rust bloom and grime at the plates, the cart at the shortest one's foot with its screen dark |
| 07 | CLOSE, eye 1.5 m over an exam room desk, looking down, room behind | a letter page on a black blotter on a dark veneer desk, its four clause blocks, the screen's cool light falling on it from the cart out of frame |
| 08 | WIDE, eye 1.15 m from beside an empty patient chair in an exam room | the cart with its screen turned toward the chair, the chair's black vinyl and casters, the back wall in shadow |
| 09 | CLOSE, frame 1's camera, the cart turned | the cart with its lit screen facing the reader, the 100 amber lights on the horizon behind |

Showstopper frame: 01, the cart close and low under one cold flood with its screen's light leaking round the back of the monitor and a horizon of a hundred amber points across the black coast
Tonal arc: near black on the apron through 1 to 6, lifting on 7 where the page takes the screen's light and staying in the room on 8, closing on 9's lit screen facing the reader

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "the workstation cart close and whole on a lit concrete apron, its monitor's back to the camera with the screen light leaking round it, a horizon of 100 small amber lights across the dark land behind"
  rect: [400, 600, 680, 750]
  bleeds: [right, bottom]
accent: "#E3A83B"
job: >
  Put the place the question is asked in front of the reader, from the side a patient sees it, and say whose
  account this is and when it was published.

claims: [c1, c2, c3, c5, c12]
numerals:
  - value_from: c12

data_in_art:
  figure: clinics
  drives: the count of amber lights on the horizon, 100, one per clinic up to the claim's floor

depth:
  eye: 1.15
  horizon: 960
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera sits low off the cart's back left quarter so the monitor's housing rises into the dark sky and
    the work surface, mast and star base stack down the frame to the casters in the lit pool. The cart stands
    right of centre. The horizon of lights runs behind it on the lower third, so the cart reads against a
    region rather than a void.
  bands: >
    Top third, the black sky with the hook and dek, the monitor's top edge rising into it. Middle third, the
    monitor back and work surface, the amber horizon lights behind. Bottom third, the mast, the battery, the
    five casters with their contacts on the lit concrete going to black toward the camera.
  focal: "the screen light spilling round the monitor's housing onto the grey work surface"

art:
  technique: "physically based render of the chassis cart on a staged apron, with the clinic lights as instanced emissive points"
  why_this_technique: "a cart reads as a real object only modelled and standing on its casters, and a region of clinics reads only as many small lights at distance"
  palette: "off white powder coat, black housing, shell concrete, black sky, amber points"
  value_structure: >
    Lightest is the screen's leak and the lit concrete. Darkest is the sky and the near ground. Frame median
    L* planned at 12.

type:
  hook: "The question is asked inside the chart"
  dek: "UTMB says the AI platform OpenEvidence puts cited medical evidence inside the UTMB electronic health record. It announced the collaboration on September 22nd. The cart and the lights are drawn to illustrate."
  labels: ["100 LIGHTS MORE THAN 100 CLINICS"]

verbatim: []

acceptance:
  - "the cart's casters, mast, battery, work surface and monitor housing are modelled and lit, and the cart owns at least 35 percent of the frame"
  - "the monitor's back faces the camera and its screen light shows at the housing's edges"
  - "a row of small amber lights runs along the horizon behind the cart, and rendering none of them fails this item"
  - "every caster stands on the concrete with a dark contact under it"
  - "no part of the cart crosses a glyph of the hook or the dek"
  - "the sky above the horizon is near black"

risks:
  - "the lights read as stars, so they sit on the land band under the horizon line, never above it"
  - "a cart outdoors reads as abandoned, so the apron is lit like a stage and nothing else is in the pool"
```

```yaml
slide: 2
layout: CLOSE_CROP
primary_image:
  subject: "the monitor face and the work surface from the clinician's side, the screen's illustrated answer with citation chips, the keyboard tray and the badge reader"
  rect: [0, 725, 780, 625]
  bleeds: [left, bottom]
accent: none
job: >
  Show what the tool does in UTMB's own words, from where the clinician stands.

claims: [c4, c6, c7]
numerals: []

depth:
  eye: 1.55
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera stands where the clinician would, behind the push bar, and looks down at the screen and the
    surface, so the reader occupies the clinician's place before the deck turns the screen away from them.
    The monitor sits in the right two thirds, the push bar and keyboard run off the bottom edge.
  bands: >
    Top third, the dark back wall of the room with the hook and dek. Middle third, the lit screen with its
    answer bars and citation chips. Bottom third, the keyboard tray and the badge reader lit by the screen's glow, the chrome push bar
    catching a highlight as it runs off the bottom edge into shadow.
  focal: "the lit answer on the screen, the brightest area in the frame"

art:
  technique: "physically based render in a TXT.interior room, the screen as its one practical"
  why_this_technique: "the answer with sources is the claim, and it reads only as a lit screen seen where the person using it stands"
  palette: "cool clinical white screen, black housing, grey tray, shadowed wall"
  value_structure: >
    Lightest is the screen. Darkest is the room's back wall and the floor. Frame median L* planned at 16.

type:
  hook: "An answer with its sources"
  dek: "Clinicians sign in with their UTMB credentials and ask in plain language. Answers cite medical literature and guidelines, UTMB says. The tool went live in March."
  labels: []

verbatim: []

acceptance:
  - "the screen shows a question bubble, answer bars and small blue citation chips, and no legible word or numeral"
  - "the keyboard's keys, the push bar and the badge reader are modelled, and an empty screen fails this item"
  - "the room's back wall shows behind the monitor in shadow"
  - "no part of the screen crosses a glyph of the hook or dek"
  - "the monitor face owns at least a third of the frame width at 432px"

risks:
  - "a screen close crop reads as a stock photo, so the cart's hardware stays in frame and the room stays dark"
```

```yaml
slide: 3
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "four workstation carts in a row on the apron through a long lens, all at one size, each on an amber strip, monitors facing away and lit"
  rect: [0, 700, 1080, 420]
  bleeds: [left, right]
accent: "#E3A83B"
job: >
  Give UTMB's reach as a count a reader can see, and say what was counted and what was not named.

claims: [c11, c12]
numerals:
  - value_from: c11
  - value_from: c12

data_in_art:
  figure: campuses
  drives: the count of rendered carts, 4, one per hospital campus

depth:
  eye: 1.2
  horizon: 900
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL]
  subject_at: {X: 0, Z: -14}

composition:
  structure: >
    A long lens down a diagonal row so the four carts read near one size and the eye counts them left to
    right. Each stands on its own amber strip so the count is four objects, not a texture. The row fills the
    middle band edge to edge.
  bands: >
    Top third, the black sky with the hook and dek. Middle third, the four carts and their screen glows.
    Bottom third, the lit apron with four amber strips and the carts' contacts, going dark at the bottom edge.
  focal: "the four glowing monitor edges in a row against the black"

art:
  technique: "a count as rendered units, staged as one subject"
  why_this_technique: "four campuses is a count, and a count reads as that many of one object"
  palette: "powder coat, black housings, amber strips, black field"
  value_structure: >
    Lightest is the lit apron and the screen leaks. Darkest is the sky. Frame median L* planned at 9.

type:
  hook: "Four hospital campuses"
  dek: "UTMB has hospitals on four campuses and more than 100 clinics across Southeast Texas. One cart is drawn for each campus, to illustrate."
  labels: ["ONE CART PER CAMPUS"]

verbatim: []

acceptance:
  - "exactly four carts are rendered and each is readable as a cart at 432px, and rendering three or five fails this item"
  - "each cart stands on an amber strip with a contact under it"
  - "the four carts read within a quarter of one size of each other"
  - "no cart crosses a glyph of the hook or dek"
  - "each of the four carts stands at least 90 px tall at 432px"

risks:
  - "four lit screens imply use at four campuses, so the dek names the set as campuses with hospitals and nothing more"
```

```yaml
slide: 4
layout: DIAGRAM
primary_image:
  subject: "a 4 m precast concrete barrier lying across the apron, its channel filled with amber to the half tick and open past it, the cart side on at the left"
  rect: [0, 620, 1080, 730]
  bleeds: [left, right, bottom]
accent: "#E3A83B"
job: >
  Draw UTMB's one usage figure exactly as far as it goes, and show where its total is missing.

claims: [c3, c9]
numerals: []

data_in_art:
  figure: share_using
  drives: the amber fill length, half of the barrier's 4 m channel, then a fading open end

depth:
  eye: 1.0
  horizon: 880
  cues: [LINEAR_PERSPECTIVE, CAST_SHADOW, RELATIVE_SIZE, AERIAL]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The barrier lies parallel to the image plane so its length reads true, the amber fill running from the left
    end to the half tick and fading past it with no end cap. The cart stands side on at the left third, its
    monitor turned to the camera's side, so the reader sees the thing counted beside the count.
  bands: >
    Top third, the black sky with the hook and dek. Middle third, the cart's monitor and mast, the labels.
    Bottom third, the barrier with its fill and half tick on the lit concrete.
  focal: "the amber fill in the barrier's channel, the only warm area on the frame"

art:
  technique: "the residual bar, a bar never a dial, as a rendered precast barrier"
  why_this_technique: "a share with no denominator is a length that stops where the claim stops"
  palette: "precast concrete, amber fill, powder coat, black"
  value_structure: >
    Lightest is the lit barrier top and the fill. Darkest is the sky. Frame median L* planned at 10.

type:
  hook: "More than half of its clinicians use it"
  dek: "That is UTMB's own figure. The release prints no count of clinicians and no total. The fill stops at half and is left open past it."
  labels: ["HALF", "MORE THAN HALF", "NO TOTAL"]

verbatim:
  - c9: "MORE THAN HALF"

acceptance:
  - "the amber fill ends solid at the half tick and fades out past it with no end cap"
  - "the barrier is modelled with arrises and a channel and casts a shadow on the concrete"
  - "the cart is side on at the left with its monitor edge on to the camera"
  - "each label sits beside its mark, within 24px"
  - "the barrier spans at least 70 percent of the frame width and the cart stands at least 150 px tall at 432px"

risks:
  - "the fade reads as a value, so the label says the total is not published"
```

```yaml
slide: 5
layout: DIAGRAM
primary_image:
  subject: "frame 4's barrier from the same camera, its channels holding two brushed aluminium bars at one scale and an empty third, the cart past side on"
  rect: [0, 620, 1080, 730]
  bleeds: [left, right, bottom]
accent: none
job: >
  Turn the deck: what a published test of a clinical model looks like, beside the release that prints none.

claims: [c1, c17, c40, c41]
numerals:
  - value_from: c40

data_in_art:
  figure: cindex_train
  drives: bar length, 0.615 and 0.574 times the barrier's 4 m channel, and the empty third channel's bar count of 0

depth:
  eye: 1.0
  horizon: 880
  cues: [LINEAR_PERSPECTIVE, CAST_SHADOW, RELATIVE_SIZE, AERIAL]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    Frame 4's camera held, so the reader compares on one bench. Two aluminium bars lie in the barrier's upper
    channels at one scale, the third channel is empty. The cart has turned further, past side on.
  bands: >
    Top third, the black sky with the hook and dek. Middle third, the cart and the three labels. Bottom
    third, the barrier with its bars and empty channel on the lit concrete.
  focal: "the two aluminium bars catching the flood, the brightest metal in the frame"

art:
  technique: "two lengths at one scale beside a drawn absence"
  why_this_technique: "a test is two measured lengths, and a missing test is an empty slot on the same bench"
  palette: "brushed aluminium, precast concrete, powder coat, black"
  value_structure: >
    Lightest is the bars and the lit barrier. Darkest is the sky and the empty channel. Frame median L* planned at 10.

type:
  hook: "Use is reported. No test is printed."
  dek: "UTMB's release prints no accuracy, error or outcome figure. UTMB says it will keep evaluating use. The bars are a different tool, an MRI model of survival in brain metastases with UTMB radiology authors, scored by C-index."
  labels: ["TRAINING, 0.615", "EXTERNAL, 0.574", "OPENEVIDENCE AT UTMB, NONE PRINTED"]

verbatim: []

acceptance:
  - "two bars lie in the barrier's channels and the shorter is visibly shorter, and rendering one bar fails this item"
  - "the third channel is visibly empty"
  - "the cart stands at the left with its monitor past side on"
  - "each label sits beside its bar or channel, within 24px"
  - "the barrier spans at least 70 percent of the frame width and the longer bar at least 40 percent at 432px"

risks:
  - "the bars read as OpenEvidence's score, so they carry no accent and the dek names the different tool"
```

```yaml
slide: 6
layout: FIGURE_SCALE
primary_image:
  subject: "three galvanized square columns at one scale of 1 m per $1,000,000, the tallest with a weld at the first amendment's height and seven bands above it, the cart at the shortest column's foot with its screen dark"
  rect: [50, 850, 1030, 450]
  bleeds: [right]
accent: none
job: >
  Size UTMB's other AI contract at one scale, with the cart for scale, and say plainly it is not OpenEvidence.

claims: [c26, c27, c28, c29, c30, c31, c34, c35]
numerals:
  - value_from: c29
  - value_from: c30
  - value_from: c35
  - value_from: c34
  - value_from: c31

data_in_art:
  figure: contract_total
  drives: column heights at one scale, 0.825 m, 4.25 m and 9.85 m, the weld at 4.25 m and 7 clamp sleeves above it, one per institution

depth:
  eye: 1.2
  horizon: 1040
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    Square on through a long lens so the three heights compare honestly, the tallest bleeding the top edge.
    The cart, 1.6 m, stands at the foot of the shortest column so the reader feels the scale in a known
    object.
  bands: >
    Top third, the tallest column rising past the hook into the black sky. Middle third, the middle column's
    top and the weld and bands on the tallest. Bottom third, the shortest column and the dark cart at its
    foot on the lit concrete.
  focal: "the tallest column's lit galvanized face"

art:
  technique: "lengths at one scale, rendered in galvanized steel at true size"
  why_this_technique: "three dollar amounts compare only as three lengths at one scale, and a known object at their foot makes the scale physical"
  palette: "galvanized steel, concrete, powder coat, black"
  value_structure: >
    Lightest is the lit faces of the columns. Darkest is the sky. Frame median L* planned at 11.

type:
  hook: "UTMB's other AI platform"
  dek: "UTMB's Qualified Health agreement began at $825,000. Item 65 on the Regents' August consent agenda would take it to $9,850,000 across all seven UT health institutions. It never names OpenEvidence, so the cart's screen is dark."
  labels: ["$825,000", "$4,250,000 OCTOBER 2025", "$9,850,000", "ADDS $5,600,000", "7 INSTITUTIONS"]

verbatim: []

acceptance:
  - "three columns stand at heights in the ratio of 825 to 4,250 to 9,850, measured off the render within 5 percent"
  - "the tallest carries a weld ring and seven clamp sleeves above it, and six or eight fail this item"
  - "the cart stands at the shortest column's foot with its screen dark"
  - "each amount label sits beside its column's top, within 24px"
  - "the three galvanized columns are modelled with a weld bead and base plates, and missing or flat columns fail this item"
  - "the tallest column runs at least two thirds of the frame height"

risks:
  - "the tallest column crowds the hook, so the hook sits left of it in the sky"
```

```yaml
slide: 7
layout: DOCUMENT
primary_image:
  subject: "a letter page with the statute's four clause blocks on a black blotter on an exam room desk, lit from frame left by the cart's screen out of frame, in a dark room"
  rect: [0, 560, 1080, 790]
  bleeds: [left, right, bottom]
accent: "#E3A83B"
job: >
  Set the law beside UTMB's account, quote both terms, and refuse to join them.

claims: [c9, c18, c19, c20, c21, c22, c23, c25]
numerals:
  - value_from: c18
  - value_from: c25

data_in_art:
  figure: conditions
  drives: the count of numbered clause blocks on the page, 3, plus the one disclosure block

depth:
  eye: 1.6
  horizon: 300
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The camera stands over the work surface and looks down at the page, so the reader reads the law where the
    question is asked. The page sits right of centre on the tray, the keyboard at the lower left, the monitor's
    base at the top edge throwing its light down.
  bands: >
    Top third, the room's dark back wall and the hook and dek. Middle third, the page with its four blocks.
    Bottom third, the keyboard's keys in the screen's glow, the tray edge and the push bar falling
    into shadow as they run off the bottom edge.
  focal: "the lit page with its amber disclosure block"

art:
  technique: "a rendered page in a TXT.interior room, lit by the screen practical from frame left"
  why_this_technique: "a statute is a document, and its place in this story is the work surface where the question is typed"
  palette: "white page, grey tray, black keys, amber rule"
  value_structure: >
    Lightest is the page. Darkest is the back wall. Frame median L* planned at 20.

type:
  hook: "The law has a disclosure line"
  dek: "Since September 1st, 2025, Sec. 183.005 says a practitioner who uses AI for \"diagnostic purposes\" must disclose it to patients. UTMB calls its use \"clinical decision support.\" The record here can't say whether the section reaches this use."
  labels: ["(1) WITHIN THE LICENSE", "(2) NOT BARRED BY LAW", "(3) REVIEWS AI RECORDS", "(B) DISCLOSE TO PATIENTS"]

verbatim: []

acceptance:
  - "the page carries four ruled blocks, the fourth edged in amber, and a blank page fails this item"
  - "the page lies on a black blotter on a dark wood desk"
  - "the room's back wall fills the top band and is dark"
  - "each label sits beside its block, within 24px"
  - "the page owns at least a fifth of the frame at 432px"

risks:
  - "the page's own type is illegible at 432px, so the DOM labels carry the clause words"
  - "the frame reads as an accusation, so the dek says no source read says which this is"
```

```yaml
slide: 8
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "the cart in a dark exam room with its monitor turned toward an empty patient chair, the screen the room's brightest thing"
  rect: [300, 700, 780, 650]
  bleeds: [right, bottom]
accent: none
job: >
  Hand the reader the exam room's question, without saying anyone failed to tell them.

claims: [c1, c23]
numerals: []

depth:
  eye: 1.15
  horizon: 760
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    From beside the patient's chair at seated height, the cart three quarters on with its screen turned toward
    the chair, so the reader is in the chair's place. The room is dark around the cart's pool, the back wall
    in shadow.
  bands: >
    Top third, the dark wall with the hook and dek. Middle third, the monitor turned to the chair. Bottom third, the chair's back and casters near left in silhouette, the cart's base and its cast
    shadow on the floor and the right wall.
  focal: "the lit screen turned toward the empty chair"

art:
  technique: "a room dark around one practical, the screen, and one cold key from out of frame"
  why_this_technique: "the question a patient can ask lives in this room, and an empty chair puts the reader in it without a mannequin"
  palette: "black vinyl chair, powder coat, screen white, cold floor pool"
  value_structure: >
    Lightest is the screen and the floor pool. Darkest is the back wall and the corners. Frame median L* planned at 14.

type:
  hook: "A patient can ask"
  dek: "Which tool was used? Did it shape the plan? Texas law has practitioners disclose AI used for diagnostic purposes."
  labels: []

verbatim: []

acceptance:
  - "the monitor's screen faces the chair and is lit, and a dark screen fails this item"
  - "the chair is empty, with its casters on the floor and a contact under it"
  - "a lit floor pool holds the cart, and its cast shadow falls on the right wall"
  - "no part of the cart crosses a glyph of the hook or dek"
  - "the cart stands at least 260 px tall at 432px"

risks:
  - "an empty chair reads as absence, so the screen is turned toward it, which is an act"
```

```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: "frame 1's apron and camera, the cart turned so its lit screen faces the reader, the 100 amber lights on the horizon behind"
  rect: [300, 700, 780, 650]
  bleeds: [right, bottom]
accent: "#E3A83B"
job: >
  Close on the dated way in, the Regents' November meeting and its testimony rule, with the screen facing the reader.

claims: [c12, c42, c43, c44]
numerals:
  - value_from: c42
  - value_from: c44

data_in_art:
  figure: clinics
  drives: the count of amber lights on the horizon, 100, the same row as frame 1

depth:
  eye: 1.15
  horizon: 960
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    Frame 1's camera returned with the cart turned, so its lit screen faces the reader square on. The bookend
    is the argument: the cover saw the back of the screen, the close sees its face.
  bands: >
    Top third, the black sky with the hook and dek. Middle third, the lit screen and work surface, the amber
    horizon behind. Bottom third, the mast, battery and casters on the lit concrete.
  focal: "the lit screen facing the reader"

art:
  technique: "physically based render of the chassis cart, frame 1's world returned"
  why_this_technique: "a bookend reads only when the camera is the same and the object's state has changed"
  palette: "screen white, powder coat, shell concrete, amber points, black sky"
  value_structure: >
    Lightest is the screen. Darkest is the sky. Frame median L* planned at 13.

type:
  hook: "Or ask the Regents"
  dek: "The Regents meet November 18th to 19th. The public may testify on any topic the agenda lists. Send the board's General Counsel a name and topic at least 24 hours ahead."
  labels: []

verbatim: []

acceptance:
  - "the monitor's lit screen faces the camera square on, and a back facing monitor fails this item"
  - "the camera, the apron and the horizon lights match frame 1's"
  - "every caster has a contact on the concrete"
  - "no part of the cart crosses a glyph of the hook or dek"
  - "the cart stands at least 260 px tall at 432px, frame 1's camera returned"

risks:
  - "a bookend reads as a copy, so the cart's turn and the screen's light change the frame's value"
```
