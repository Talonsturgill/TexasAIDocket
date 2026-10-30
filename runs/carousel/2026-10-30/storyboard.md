# Storyboard, 2026-10-30
# "Weighed in one motion."

## The story, and what the fact check did to it

Plano's City Council meeting of October 12th, 2026 (c5) carried a citywide AI purchase as item (f) of its consent agenda,
which the council acts on in one motion (c6). The item buys ChatGPT Enterprise from Carahsoft for $190,000 (c1), the Darwin
AI governance platform from Carahsoft for $150,000 (c2) and Microsoft Enterprise from SHI for $10,000 (c3), and holds a
further $40,000 for growth inside a not to exceed total of $390,000 (c4). The meeting's minutes note on the item reads
approved (c7), and those minutes are still marked draft (c8). Darwin AI says its platform tracks AI use across users, tools
and departments (c9), monitors AI activity with a complete audit trail (c10), turns written policy into automated controls
(c11) and applies data loss prevention to prompts and responses (c12). Plano lies in Collin and Denton counties (c13, c14),
and the Census Bureau's 2024 estimate is 293,286 residents (c15).

The turn, all computed in `compute.py`. For every chatbot dollar the item sets aside 79 cents for the platform that watches
how staff use AI (`darwin_cents_per_chat_dollar`). The chatbot line exceeds the watcher line by $40,000, which is exactly the
reserve (`chat_minus_darwin_usd` equals `reserve_usd`). The greatest common divisor of the four lines is $10,000, the
Microsoft line itself, so the whole item is 39 weights of $10,000 (`ceiling_units`): 19, 15, 1 and 4.

The fact check moved four things, and every surface obeys them.
1. **Every Government Technology detail is gone.** The license count, the annual estimate, the city's stated uses and the
   funding sources rest only on govtech.com, which names ClaudeBot with a whole-site disallow. No surface prints them.
2. **"Approved" is the draft minutes' word.** Every action field on the event item is empty and the minutes are still a
   draft. The deck says the minutes note it approved and that they are a draft. It never says the council voted.
3. **What Darwin does is Darwin's own description**, attributed every time. Nothing says what Plano will use it for.
4. **No count of licenses, staff or uses** appears, because none is in a record this run could read.

## Why this treatment, and what was grafted

Director C's ONE CHANGING OBJECT is the spine: a brass laboratory pillar balance with slotted weights of one drawing unit.
The story is a comparison of two lines, and a balance is the instrument a reader trusts to compare two things. The unit is
$10,000, the greatest common divisor of the four lines and the Microsoft line itself, so every line is a whole count of
identical weights, and the reader counts the purchase.

Grafted from Director A (THE MEASURED LEDGER): the "difference equals the reserve" fit. On frame 5 the watcher row stops four
weights short of the chatbot row, and the empty length of its groove is the reserve's four. A's black Blackland clay carrier,
which is Plano's own ground, is the board every relief stands on.

Grafted from Director B (AFTER HOURS): the city hall's lit council chamber as the far warm light behind the balance on frames 1
and 9, and every interior pool with its source in frame.

Refused: B's lit floors as dollars (a building's floors imply a program the record does not hold), B's audit trail of paper
(the record never says where Darwin runs or that anything prints), A's pennies per resident (the per resident figure is
honest but small, and a coin grid risked the polka dot reading), and C's needle on a graduated arc as a reading (kept, but
the arc carries no numerals and the dek calls the tilt a drawing).

## The world, and the laws that hold it

**LASTLIGHT, STAGED.** The chassis is `assets/js/deck/2026-10-30-balance.js` and every frame loads it. It declares
`sky: lastLight` with the key at azimuth -58, elevation 13: the last light low in the west south west. A camera looking north
(-z) has the key on its LEFT, every lit edge is on the left, and every cast runs long to the right. TXBENCH reads the same
declaration, so every relief is lit from the upper left and casts to the lower right.

One key casts. The chamber glazing is light placed behind glass, and the needle's index is the only accent that is not a
blued weight.

The materials of the deck: polished brass for the chatbot's weights, heat blued steel for the watcher's, nickel for the
Microsoft weight and the needle, pecan heartwood for the case and the balance base, Austin chalk limestone for the plinth,
Blackland Prairie clay (near black vertisol) for the boards, black felt in the wells.

## Palette

| token | hex | where |
|---|---|---|
| `ground` | `#08070C` | the DOM body behind the render |
| `accent` | `#4E5FA8` | bluebonnet, worn ONLY as the heat blued steel of the Darwin AI weights, so it means one thing, the watcher. Frames 1, 3, 5, 7, 9 |
| `hook` | `#ECE8DF` | light type on the dark |
| `dek` | `#D6D0C4` | the dek |
| `material` | `#B08D57` | the brass of the chatbot's weights |

## The continuity devices

    CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE, VALUE_ARC

1. **Motif evolution, the balance and its weights change state with every claim.** Loaded and leaning on 1, one weight
   holding the agenda leaf on 2, the case counted open on 3, the brass stack alone on 4, the two rows laid down on 5, the
   needle at the reserve on 6, the watcher pan riding high on 7, the case shut on the dais ledge on 8, the loaded balance at
   rest beside a resident on 9.
2. **Camera move around one instrument.** A low three quarter on the plaza (1), plan (2, 3, 5), macro on the stack (4) and the
   needle (6), a worm's eye under the watcher pan (7), a seated eye at the dais (8) and a standing eye on the plaza (9).
3. **Value arc, dusk to night.** The warm seam behind the balance on 1, the lit metal of the reliefs through the middle, the
   seam behind the raised pan on 7, the chamber's one window on 8, and the darkest frame on 9 with the chamber's glow.

## The rotation

    FULL_BLEED  DOCUMENT  OBJECT_AND_CAPTION  CLOSE_CROP  DIAGRAM  CLOSE_CROP  OBJECT_AND_CAPTION  FULL_BLEED  FIGURE_SCALE

`TXLAYOUT.check` returns an empty list. Type sits on the dark sky, the dark clay or the dark room on every frame.

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | CLOSE, eye 0.55 m over the plinth top, 1.4 m off, fov 30, low three quarter | the chassis equal_arm_balance: a turned brass pillar on an ebonized pecan base, a 0.64 m brass beam on a knife edge, stirrups of three rods carrying spun brass pans, 19 brass weights stacked left and 15 blued right, the beam tilted toward the brass, on a chalk plinth with contact, raked by the low key with a bright line down every knurled edge |
| 02 | AERIAL, orthographic material relief | an agenda sheet on a pecan board, cool grey paper with greeked consent rows raised and four raised rules under item (f), lit by the grazing key in a snooted pool, its edge casting onto the board, one brass slotted weight standing on row (f) and casting across the rows, the pecan worn darker at the sheet's edge |
| 03 | CLOSE, eye 1.3 m over the desk, 0.9 m back, looking down about 55 degrees, fov 34 | the chassis weight_case open on a dark desk, a pecan top plate cut with 39 felt lined wells, 19 polished brass, 15 heat blued and 1 nickel slotted weight standing proud with chamfers and knurled bands, 4 wells empty, lit through the window by the low key in one pool with the studio panels in the metal, each weight casting into its well, the pecan worn at the corners |
| 04 | MACRO, 0.38 m from the brass stack at mid height, fov 28, level | the brass stack of 19 slotted weights in the left pan, polished brass with a dark seam between discs and chamfers, lit by the low key with a specular line down the lit side and the seam behind, seated in the spun brass pan with a contact shadow, handling marks and a dull patina on the lower discs |
| 05 | AERIAL, orthographic material relief | a board of Blackland clay with two machined grooves from one brass origin bar, near black vertisol with shrink swell cracks, brass and blued discs with raised rims, lit by the key raking along the grooves, each disc casting onto the clay and seated in its groove, the clay worn pale along the groove lips |
| 06 | MACRO, level with the arc at 0.30 m, fov 26 | the nickel needle over a nickel silver arc of 39 engraved graduations, polished nickel with bevelled engraving, lit by the low key with the seam behind the needle's edge, the needle's shadow cast onto the arc face, fine wiping marks and a tarnished rim on the arc |
| 07 | CLOSE, 0.25 m below the right pan rim, looking up 18 degrees, fov 32 | the watcher end of the beam riding high, 15 blued weights over the pan rim against the last light seam, a weak rim light on the dark edge only |
| 08 | MEDIUM, seated eye 1.1 m, 2.4 m from the dais ledge, fov 40 | the kit hearing_dais ledge in a dark TXT.interior room lit through one window on the left, blank brass nameplates, gooseneck mics, the chassis weight_case shut and latched on the ledge |
| 09 | MEDIUM, eye 1.38 m, 2.7 m back on the plaza aimed at the pans, fov 31 | the loaded balance filling about 45 percent of the frame width on its plinth top, the plinth face cut by the bottom edge, a kit resident passing just behind the left pan toward the lit glazed chamber of the kit city_hall, the beam at the same computed tilt as 01 |

Showstopper frame: 03, thirty nine fitted wells in one pool of low light, three metals and four empty wells, its depth made by the contact and cast shadow of each weight in its well, the occlusion of the desk and the room falling off behind.
Tonal arc: the warm seam behind the balance on 01, the lit leaf on 02, the brightest metal on 03, the brass macro on 04, the
two rows on 05, the needle's edge on 06, the seam behind the raised pan on 07, one window on 08, and the darkest frame on 09
with the chamber's glow.
VALUE CUT: frame 5. The deck turns from what was bought to how the two lines compare.

---

```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: "a brass laboratory pillar balance on a chalk plinth at last light, 19 brass weights in the left pan and 15 blued steel weights in the right, the beam tilted toward the brass, the city hall's lit chamber far behind in the dark"
  rect: [150, 540, 800, 700]
  bleeds: []
accent: "#4E5FA8"
job: >
  Put the whole comparison in one instrument before a word is read: the chatbot in one pan, the platform that watches it in
  the other, and the beam leaning toward the chatbot.

claims: [c1, c2, c3, c5, c9, c17]
numerals:
  - value_from: c1
  - value_from: c2
  - value_from: c3
  - value_from: c5

data_in_art:
  figure: chatgpt_units
  drives: weight count in the left pan stack, with darwin_units setting the right pan stack and chat_minus_darwin_units the beam tilt

depth:
  eye: 0.55
  horizon: 520
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The balance is seen from a low three quarter just above the plinth so the beam crosses the frame as a long tilted line and
    the two stacks stand as two unequal towers, the brass lower because its pan is down. The plinth's lit top runs out of the
    bottom edge and the pans reach both side edges, so the instrument owns the lower sixty percent.
  bands: >
    Top third, the dark sky with the kicker, the hook and the dek. Middle third, the beam and the tops of both stacks against
    the seam, the chamber glazing a dim ember far back. Bottom third, the pans, the stacks' lower weights and the lit chalk
    plinth top with the long casts of every weight.
  focal: "the brass stack and its pan, the brightest metal area in the frame"

art:
  technique: "physically based render of the chassis equal_arm_balance, slotted_weight and a chalk plinth in the lastLight world, staged on the balance, the kit city_hall far behind"
  why_this_technique: "a modelled instrument raked by a low key shows brass and blued steel as different metals and makes the weights countable, which is the whole argument"
  palette: "polished brass, heat blued steel, nickel, pecan, Austin chalk, near black sky with a warm seam"
  value_structure: >
    Lightest is the lit edge of the brass stack and the plinth's lit top. Darkest is the sky and the plaza beyond the pool.
    Frame median L* planned at 14.

type:
  hook: "A chatbot for Plano, and Darwin AI beside it"
  dek: "The city's October 12th agenda carried $190,000 for ChatGPT Enterprise and $150,000 for Darwin AI, a platform its maker says tracks AI use. Each weight is $10,000, a drawing unit. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the left pan holds exactly 19 brass weights and the right pan exactly 15 blued weights, countable at full size"
  - "the beam visibly tilts toward the brass pan at 432 px"
  - "the brass and the blued weights are told apart by colour at 432 px"
  - "the plinth meets the ground with a contact shadow and the weights cast onto the plinth top"
  - "no beam, pan or weight crosses a glyph of the hook or dek"
  - "the frame's median L* at 432 px is 26 or lower"
  - "the chassis equal_arm_balance is present with its pillar, beam, both pans and needle modelled"
  - "the balance owns at least half of the frame width and at least 220 px of height at 432px"
risks:
  - "the balance reads as the scales of justice, so it is a pillar balance with a needle and slotted weights, with no chains"
```

```yaml
slide: 2
layout: DOCUMENT
primary_image:
  subject: "an agenda sheet of the consent agenda on a pecan board, greeked rows raised, four raised rules under item (f), one brass slotted weight standing on the row and casting across the sheet"
  rect: [120, 430, 960, 920]
  bleeds: [right, bottom]
accent: "none"
job: >
  Show how it passed: one item among a run of consent items, acted on in one motion, held down by the first weight the deck
  shows.

claims: [c6, c4]
numerals:
  - value_from: c4

data_in_art:
  figure: lines_on_item
  drives: count of raised rules drawn under row (f)

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    The leaf lies square in plan with its right and bottom edges cut by the frame, so it reads as a page too large to fit,
    and the one weight on row (f) is the tallest thing on it, so its cast across the rows leads the eye to the item.
  bands: >
    Top third, the dark pecan board and the type. Middle third, the upper consent rows and row (f) with its weight and cast.
    Bottom third, the four raised rules under (f) lit in the pool, the sheet edge casting a shadow onto the pecan, the lower rows running out of the bottom edge.
  focal: "the brass weight on row (f) and its long cast"

art:
  technique: "TXBENCH multi-material relief, a document under a paperweight, with a keyMask pool on the leaf"
  why_this_technique: "a page in plan with real height lets one weight sit on one row and cast, which says which item it is without a pointer"
  palette: "cool grey paper, pecan heartwood, brass"
  value_structure: >
    Lightest is the pooled paper around row (f). Darkest is the pecan board outside the pool and the weight's cast.
    Frame median L* planned at 24.

type:
  hook: "One item, on the consent agenda"
  dek: "Item (f) sat on the consent agenda, which the council acts on in one motion. It held four lines inside a ceiling of $390,000. Drawn to illustrate."
  labels: ["(f)"]

verbatim: []

acceptance:
  - "exactly four raised rules sit under row (f)"
  - "one brass weight stands on row (f) and casts across at least two rows"
  - "the paper reads as a sheet with an edge that casts onto the board"
  - "no legible text is rendered in the art, only the DOM label (f)"
  - "the frame's median L* at 432 px is 34 or lower"
  - "the agenda sheet on the pecan board is present with its raised consent rows"
  - "the agenda sheet owns at least half of the frame height at 432px"
risks:
  - "a pale sheet can push mid tones and read as a cream ground, so the paper is cool grey and pooled, falling to dark pecan"
```

```yaml
slide: 3
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "a fitted pecan weight case open on a desk, seen obliquely, with 39 felt lined wells, 19 brass weights, 15 blued, 1 nickel and 4 wells empty"
  rect: [0, 600, 1080, 750]
  bleeds: [left, right, bottom]
accent: "#4E5FA8"
job: >
  Count the whole item at a glance: every line of the purchase as weights of one unit, and the reserve as wells left empty.

claims: [c1, c2, c3, c4]
numerals:
  - value_from: c4
  - computed_by: "compute.py, ceiling_units, chatgpt_units, darwin_units, microsoft_units and reserve_units over unit_usd"

data_in_art:
  figure: ceiling_units
  drives: well count, with chatgpt_units, darwin_units and microsoft_units setting the filled wells per metal and reserve_units the empty wells

depth:
  eye: 2.06
  horizon: -400
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: -0.36}

composition:
  structure: >
    The case fills the lower two thirds in plan with its rim cut by both side edges while every well stays inside, so the
    count is complete. The wells fill in reading order, brass first, then blued, then the one nickel, then four empty, so the
    reserve is the last thing the eye reaches.
  bands: >
    Top third, the dark clay field and the type. Middle third, the brass and the first blued rows. Bottom third, the last
    blued row, the nickel weight and the four empty wells in shadow, the case rim running out of the bottom edge.
  focal: "the boundary where the blued rows end and the four empty wells begin"

art:
  technique: "physically based render of the chassis weight_case open on a long kit council table in a TXT.interior council office lit through one window, staged on the case"
  why_this_technique: "modelled weights with chamfers and knurled bands, seen obliquely, read as real metal a reader can count, and the empty felt wells hold shadow as the reserve. A plan relief of the same case read as dial faces twice in the audition, so the representation changed"
  palette: "brass, heat blued steel, nickel, pecan heartwood, black felt, Blackland clay"
  value_structure: >
    Lightest is the lit rims and slots of the brass weights. Darkest is the felt in the empty wells and the casts.
    Frame median L* planned at 20.

type:
  hook: "The whole ceiling, in weights"
  dek: "39 wells of $10,000 each. 19 hold ChatGPT Enterprise, 15 Darwin AI and 1 Microsoft. The 4 empty wells are the reserve the item holds for growth and other costs. Drawn to illustrate."
  labels: ["CHATGPT ENTERPRISE", "DARWIN AI", "MICROSOFT", "RESERVE"]

verbatim: []

acceptance:
  - "the case holds exactly 39 wells, all inside the frame"
  - "exactly 19 wells hold brass, 15 hold blued steel, 1 holds nickel and 4 are empty"
  - "at 432 px the three metals are told apart and the empty wells read as dark holes"
  - "every weight sits in its well with contact occlusion and a short cast to the lower right, so each reads attached"
  - "the frame's median L* at 432 px is 30 or lower"
  - "the weight case owns at least a third of the frame height at 432px"
risks:
  - "dozens of small cylinders in plan can read as a dotted card at 432 px, the no. 62 failure, so the weights stand 30 px proud under el 13 with a snooted pool, and if one repair fails the frame becomes a txthree oblique of the open case"
```

```yaml
slide: 4
layout: CLOSE_CROP
primary_image:
  subject: "the brass stack of 19 slotted weights in the balance's left pan at macro, the pan rim and stirrup rods cropped"
  rect: [300, 60, 600, 860]
  bleeds: []
accent: "none"
job: >
  Stand the biggest line alone: the chatbot's nineteen weights, nearly half the ceiling, close enough to count.

claims: [c1, c3, c4]
numerals:
  - value_from: c1
  - computed_by: "compute.py, chatgpt_pct_of_ceiling"

data_in_art:
  figure: chatgpt_units
  drives: disc count in the stack and its height at 0.018 m a disc

depth:
  eye: 0.95
  horizon: 760
  cues: [RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: -0.32, Z: 0}

composition:
  structure: >
    The stack stands right of centre, level with the camera so every disc's chamfer and seam reads, the pan cut by the
    left and bottom edges, and the seam low behind so the stack's silhouette separates from the sky.
  bands: >
    Top third, the dark sky with the type. Middle third, the upper discs against the seam. Bottom third, the lower discs lit on their chamfers,
    the pan rim in shadow and a stirrup rod running out of the bottom edge.
  focal: "the lit chamfers of the stack's middle discs"

art:
  technique: "physically based macro render of the chassis slotted_weight stack in the lastLight world"
  why_this_technique: "at macro the weights are real machined objects, so the reader counts nineteen things rather than reading a bar"
  palette: "polished brass, nickel rods, near black sky with a warm seam"
  value_structure: >
    Lightest is the specular line down the stack's lit side. Darkest is the sky above the seam and the pan's shadow side.
    Frame median L* planned at 12.

type:
  hook: "Of the ceiling, 49 percent covers the chatbot"
  dek: "ChatGPT Enterprise from Carahsoft is $190,000 of the $390,000 ceiling. 19 weights of $10,000. Drawn to illustrate."
  labels: []

verbatim: []

acceptance:
  - "the stack holds exactly 19 discs, each seam visible at full size"
  - "the stack is at least 600 px tall at full size"
  - "the whole pan hangs in frame above the plinth top with its rim lit, and no rod crosses a glyph"
  - "the frame's median L* at 432 px is 24 or lower"

risks:
  - "a stack of identical discs can read as a brass bar, so the seams carry a dark line and each disc a chamfer highlight"
```

```yaml
slide: 5
layout: DIAGRAM
primary_image:
  subject: "a board of black Blackland clay with two machined grooves from one brass origin bar, 19 brass discs in the upper groove, 15 blued discs in the lower and the lower groove running on empty for 4 disc widths"
  rect: [40, 760, 1000, 470]
  bleeds: []
accent: "#4E5FA8"
job: >
  Turn the deck: lay the two lines down at one scale so the watcher row stops 79 cents into every chatbot dollar, and the
  empty groove it leaves is the reserve.

claims: [c1, c2]
numerals:
  - computed_by: "compute.py, darwin_cents_per_chat_dollar"
  - computed_by: "compute.py, chat_minus_darwin_usd"

data_in_art:
  figure: darwin_cents_per_chat_dollar
  drives: the lower row's length as a share of the upper row, drawn as darwin_units against chatgpt_units discs at one pitch, with chat_minus_darwin_units empty disc widths

depth:
  projection: orthographic_relief
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]

composition:
  structure: >
    Two long rows run left to right from one brass bar near the left edge, so both lengths start at one origin and the eye
    reads the difference at the right end, where the lower groove continues empty. Mono labels sit at each row's end.
  bands: >
    Top third, the dark clay and the type. Middle third, the brass row. Bottom third, the blued row lit along its rims,
    the shadowed groove continuing past it and the cracked clay texture running out of the bottom edge.
  focal: "the right end of the blued row where its groove continues empty"

art:
  technique: "TXBENCH multi-material relief, measured rows at one scale under a grazing key"
  why_this_technique: "two rows of the same disc at one pitch make the ratio a length a reader sees, and the cavity of the empty groove is the difference"
  palette: "brass, heat blued steel, Blackland clay, polished brass origin bar"
  value_structure: >
    Lightest is the lit rims of the brass discs. Darkest is the clay outside the pool and the empty groove's floor.
    Frame median L* planned at 16.

type:
  hook: "79 cents for Darwin AI per chatbot dollar"
  dek: "For each dollar of ChatGPT Enterprise, the item sets aside 79 cents for Darwin AI. Drawn to illustrate."
  labels: ["CHATGPT ENTERPRISE", "DARWIN AI"]

verbatim: []

acceptance:
  - "the upper groove holds exactly 19 brass discs and the lower exactly 15 blued discs at the same pitch"
  - "both rows start at one brass bar"
  - "the lower groove continues empty for exactly 4 disc widths past its last disc"
  - "every disc casts onto the clay at 432 px"
  - "the frame's median L* at 432 px is 26 or lower"
  - "the clay board with its two grooves spans at least two thirds of the frame width at 432px"
risks:
  - "two rows in plan can read as a striped bar chart, so each disc has a raised rim and a slot and the key grazes along the grooves"
```

```yaml
slide: 6
layout: CLOSE_CROP
primary_image:
  subject: "the balance's nickel needle hanging over a nickel silver arc of 39 engraved graduations, deflected four graduations onto a brass index"
  rect: [0, 600, 1080, 750]
  bleeds: [left, right, bottom]
accent: "none"
job: >
  Read the difference off the instrument: the needle rests on the reserve, because the chatbot line beats the watcher by
  exactly what the item holds back for growth.

claims: [c1, c2, c4]
numerals:
  - value_from: c4
  - computed_by: "compute.py, chat_minus_darwin_usd"

data_in_art:
  figure: chat_minus_darwin_units
  drives: needle deflection in graduations from zero, and the brass index's position at reserve_units

depth:
  eye: 1.05
  horizon: 900
  cues: [RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}

composition:
  structure: >
    The arc sweeps across the lower middle at macro, the needle's tip on the brass index slightly left of centre, the
    pillar cut by the bottom edge and the beam by the top, so the reader is inside the instrument.
  bands: >
    Top third, the dark sky and the type, the beam crossing at the top edge. Middle third, the needle against the seam.
    Bottom third, the arc lit on its polished face with the needle casting a shadow across the graduations, the pillar head running out of the bottom.
  focal: "the needle tip on the brass index"

art:
  technique: "physically based macro render of the chassis balance's pointer and scale in the lastLight world"
  why_this_technique: "a needle at rest is the one reading a balance gives, and engraved graduations with no numerals keep it a drawing"
  palette: "nickel, nickel silver, a brass index, near black sky with a warm seam"
  value_structure: >
    Lightest is the needle's lit edge and the arc's polished face. Darkest is the sky and the pillar's shadow side.
    Frame median L* planned at 13.

type:
  hook: "The difference equals the reserve"
  dek: "ChatGPT Enterprise outweighs Darwin AI by $40,000. The reserve the item holds for more licenses and other costs is also $40,000. The tilt is a drawing."
  labels: []

verbatim: []

acceptance:
  - "the arc carries 39 graduations and no numerals"
  - "the needle tip sits on the fourth graduation from zero, on the brass index, within 6 px at full size"
  - "the needle reads as nickel against the seam at 432 px"
  - "the frame's median L* at 432 px is 24 or lower"
  - "the needle and arc span at least half of the frame width at 432px"
risks:
  - "engraved graduations at macro can alias, so they are geometry with a bevel and the camera stays level with the arc"
```

```yaml
slide: 7
layout: OBJECT_AND_CAPTION
primary_image:
  subject: "the watcher end of the balance riding high, 15 blued steel weights over the pan rim against the last light seam"
  rect: [180, 0, 680, 700]
  bleeds: [top]
accent: "#4E5FA8"
job: >
  Say what the watcher is, in its maker's own words, under the pan that carries it.

claims: [c9, c10, c17]
numerals: []

data_in_art:
  figure: darwin_units
  drives: blued disc count in the raised stack

depth:
  eye: 0.82
  horizon: 1010
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0.32, Z: 0}

composition:
  structure: >
    A worm's eye under the right pan puts the blued stack high in the upper two thirds against the seam, the stirrup rods
    converging up to the beam end, so the lighter pan reads as raised. The caption sits on the dark plinth face below.
  bands: >
    Top third, the beam end, the stirrups and the top of the blued stack against the sky. Middle third, the pan and the
    lower discs. Bottom third, the plinth face in shadow with the chalk texture catching a faint light, carrying the hook and the quoted description.
  focal: "the blued stack's lit edge against the seam"

art:
  technique: "physically based render, worm's eye contre jour with a weak rim light on the dark edge only, in the lastLight world"
  why_this_technique: "from below the lighter pan rides high, which is the instrument's own statement of which line is smaller"
  palette: "heat blued steel, brass stirrups, chalk plinth in shadow, the warm seam"
  value_structure: >
    Lightest is the seam behind the stack and the stack's rim light. Darkest is the plinth face under the type.
    Frame median L* planned at 12.

type:
  hook: "What Darwin AI says it does"
  dek: "The item's reseller links to this maker. Drawn to illustrate."
  labels: ["\"Track AI usage across users, tools, and departments\"", "\"Continuously monitor AI activity, investigate violations, and maintain a complete audit trail.\""]

verbatim:
  - c9: "Track AI usage across users, tools, and departments"
  - c10: "Continuously monitor AI activity, investigate violations, and maintain a complete audit trail."

acceptance:
  - "the raised stack holds exactly 15 blued discs"
  - "the pan reads as higher than the camera with its underside visible"
  - "both quoted lines are set in straight quotes and match c9 and c10 word for word"
  - "the frame's median L* at 432 px is 24 or lower"
  - "the watcher end of the beam riding high is present with its stirrups, pan and blued stack"
  - "the watcher end of the beam with its blued stack stands at least 120 px tall at 432px"
risks:
  - "blued steel under a warm key drifts toward violet, so the accent is measured off the render before round 1"
```

```yaml
slide: 8
layout: FULL_BLEED
primary_image:
  subject: "the kit hearing_dais ledge in a dark council room lit through one window, blank brass nameplates, gooseneck mics, the weight case shut and latched on the ledge"
  rect: [80, 860, 1000, 490]
  bleeds: [right, bottom]
accent: "none"
job: >
  Name what the city's record does not give: the minutes note it approved, they are still a draft, and the Legistar entry
  shows no license count and no planned use.

claims: [c7, c8, c18, c20, c22]
numerals:
  - value_from: c20
  - value_from: c7

data_in_art: none

depth:
  eye: 1.1
  horizon: 700
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: -2.4}

composition:
  structure: >
    The dais ledge runs across the frame from a seated eye with both ends cut, the window key raking along it from the
    left, the shut case in the pool at left of centre and the nameplates falling into the dark, so the room is dark around
    one source and no seat count can be read.
  bands: >
    Top third, the dark back wall in shadow with the type. Middle third, the ledge, the case, two nameplates and a mic in
    the window's pool. Bottom third, the dais front panels running out of the bottom edge into shadow.
  focal: "the shut case and the nearest nameplate in the window's pool"

art:
  technique: "physically based render of the kit hearing_dais and the chassis weight_case in a TXT.interior room lit by one window"
  why_this_technique: "the case shut on the ledge says the weights are out of sight, as the record is, in the room the item passed in"
  palette: "pecan, brass nameplates, the walnut of the dais, a dark plaster wall, the window's warm last light"
  value_structure: >
    Lightest is the window's pool on the ledge and the case's brass latch. Darkest is the back wall and the dais front.
    Frame median L* planned at 10.

type:
  hook: "Approved, in records still marked draft"
  dek: "The October 12th minutes note the item approved. The October 26th minutes, also a draft, mark those minutes approved."
  labels: []

verbatim: []

acceptance:
  - "the weight case is shut, its latch visible and lit"
  - "the dais ledge is cut by both side edges and no full row of seats is visible"
  - "the back wall is visibly darker than the ledge pool at 432 px"
  - "no screen or legible text appears in the art"
  - "the frame's median L* at 432 px is 22 or lower"
  - "the dais ledge spans the full frame width and at least 90 px of height at 432px"
risks:
  - "the room can read as a generic CG interior, so the crop is tight on the ledge with one window source and no person"
```

```yaml
slide: 9
layout: FIGURE_SCALE
primary_image:
  subject: "the loaded balance close at eye height on its plinth top, a resident passing just behind its left pan toward the lit glazed council chamber of the kit city_hall"
  rect: [160, 650, 860, 700]
  bleeds: [bottom]
accent: "#4E5FA8"
job: >
  Bring it home to a resident: the item's ceiling comes to about $1.33 for each of Plano's residents in the Census
  estimate, and the balance stands in the plaza where the item was decided.

claims: [c4, c15, c21]
numerals:
  - value_from: c15
  - computed_by: "compute.py, ceiling_cents_per_resident"
  - value_from: c21

data_in_art:
  figure: chatgpt_units
  drives: weight count in the balance's left pan, with darwin_units in the right, the same loaded state as frame 1

depth:
  eye: 1.2
  horizon: 940
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 2.2, Z: -1.0}

composition:
  structure: >
    The loaded balance stands close at eye height and owns the frame, its plinth top in the lower third with the face cut
    by the bottom edge. The person passes just behind the left pan three quarters away toward the lit chamber, so the
    instrument and the place it was decided sit in one frame and the person gives both a size.
  bands: >
    Top third, the dark sky with the type. Middle third, the chamber's glazing glowing far back and the person's lit
    silhouette. Bottom third, the balance's lit pans and the plinth top in the pool, its face cut by the bottom edge.
  focal: "the lit chamber glazing and the person against it"

art:
  technique: "physically based render of the chassis balance, the kit person and the kit city_hall in the lastLight world, staged on the balance and the person"
  why_this_technique: "a person at true scale beside the instrument and the building turns a ledger into a place a resident walks through"
  palette: "brass, blued steel, chalk, the city hall's limestone in shadow, the chamber's warm glow"
  value_structure: >
    Lightest is the chamber glazing and the balance's lit metal. Darkest is the sky and the plaza outside the pools.
    Frame median L* planned at 9.

type:
  hook: "A ceiling of about 133 cents a resident"
  dek: "The $390,000 ceiling spread over Plano's 293,286 residents in the Census estimate. Plano's Legistar lists the council's next meeting for November 9th."
  labels: []

verbatim: []

acceptance:
  - "the person stands under a fifth of the frame height, three quarters away, lit from the camera side"
  - "the balance holds 19 brass and 15 blued weights, the same state as frame 1"
  - "the city hall's chamber glazing is lit and is the brightest large area beyond the balance"
  - "the person meets the ground with a contact shadow and the balance's feet meet the plinth top"
  - "the frame's median L* at 432 px is 22 or lower"
  - "the balance on its plinth stands at least 160 px tall at 432px"
risks:
  - "the kit person within a few metres reads as a mannequin, so it stays small, three quarters away and lit from the camera side"
```
