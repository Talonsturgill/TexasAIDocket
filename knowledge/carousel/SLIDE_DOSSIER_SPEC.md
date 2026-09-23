# Slide dossier spec — the planning format

A dossier is written for every slide BEFORE any code is written for it. This is not process for
its own sake. A slide planned while it is being coded gets argued for rather than judged,
because by the time anybody looks at it the work is already done and the reviewer is being
asked to reject effort rather than assess a plan.

The dossier is also what the pixel critic grades against, which is the second reason it comes
first: a checklist written after the render is a checklist that describes the render.

## The format

```yaml
slide: 3
layout: OBJECT_AND_CAPTION    # one of the ten in assets/js/txlayout.js, rotated across the deck
primary_image:
  subject: "a school bus at 6.6 m on a caliche lot at dusk, bleeding both sides"
  rect: [0, 330, 1080, 1020]  # x, y, w, h in frame px, at least 0.30 of the frame
  bleeds: [left, right, bottom]
accent: "#E0956A"             # the deck's ONE accent, from config/brand.yaml, or none
job: >
  One sentence. What this slide does that no other slide in the deck does. If two dossiers
  have the same job, one of the slides is cuttable.

claims: [c4, c7]          # every factual string on this slide, by claim id
numerals:                 # every figure, and where it comes from
  - value_from: c4        # a claim, or
  - computed_by: "scripts/... , peak divided by approved"   # a computation

# REQUIRED on at least six of nine frames. THE ARTWORK CARRIES THE DATA, in
# knowledge/carousel/ILLUSTRATION_SYSTEM.md, is the law and figure_bearing.py is the gate.
# `numerals` above says where the TYPE's numbers come from. This says where the IMAGE's
# dimensions come from, and until 2026-09-20 nothing asked. Four decks shipped with six, four,
# two and six of nine frames carrying no numeral at all: rooms, walkways and a brick wall, each
# drawn well and each silent about the story beside it.
data_in_art:
  figure: small_systems_of_all   # a key in figures.json, or a claim's computed value
  drives: mark count             # the DRAWN parameter that figure sets
# `drives` names something a renderer can set: column height, mark count, stipple density, arc
# sweep, ring radius, row spacing. Never a mood. "The sense that the system is strained" is not
# a parameter and no reviewer can check a drawing against it.
#
# Then DRAW it. The gate looks for the value in the frame's code with the text nodes stripped
# out, so a figure that reaches the headline and not the canvas does not satisfy this.

# REQUIRED on at least five of nine frames. THE FRAME STANDS IN A PLACE, in
# knowledge/carousel/ILLUSTRATION_SYSTEM.md, is the law and depth_floor.py is the gate.
# Name the camera this frame stands in and the cues it builds. A frame drawn in screen pixels
# is a diagram of a place rather than a place, and 241 frames were drawn that way before this
# existed, on a bench that had been sitting in assets/js/txscene.js since September 11th.
depth:
  eye: 1.4                 # camera height in metres. A standing adult is 1.6, seated 1.2
  horizon: 640             # screen y of the horizon. Hold it across the deck unless the
                           # storyboard declares a CAMERA_MOVE
  cues: [LINEAR_PERSPECTIVE, RELATIVE_SIZE, CAST_SHADOW, AERIAL]
  subject_at: {X: 2, Z: 30}   # where the primary image stands, in metres
# The light is NOT named here. It belongs to the chassis, TXSCENE.create is told it, and
# depth_floor.py fails a frame whose scene light disagrees with the chassis's declaration.

composition:
  structure: >
    How the frame is organised, and why this content wants that organisation rather than
    another. "Centered" is not an answer; "the figure sits on the horizon line so the reader
    reads the scale before the number" is.
  bands: >
    What occupies the top, middle and bottom third. All three must have an answer.
  focal: "what the eye lands on first, and what pulls it there. AN AREA, NEVER A LINE"

art:
  technique: "named, from knowledge/carousel/TECHNIQUE_LIBRARY.md"
  why_this_technique: "what it does for THIS claim that another would not"
  palette: "drawn from this story's own region, with the source named"
  value_structure: >
    what is lightest, what is darkest, and what each is doing. Ends with the frame's own
    target, written exactly like this so panel_ready can read it: Frame median L* planned at 22.
  motion: "how the eye travels, if the frame has a path"

type:
  hook: "..."             # the words, final, house style
  dek: "..."
  labels: ["..."]

verbatim:                 # EVERY STRING ON THIS FRAME SET AS SOMEBODY ELSE'S WORDS
  - c7: "EXCEEDED EXPECTATIONS"
  - c9: "HIGH-QUALITY FACIAL IMAGES"

acceptance:               # THE PIXEL CRITIC GRADES AGAINST THIS, ITEM BY ITEM
  - "the peak figure is legible at 432px against the ember band"
  - "the transmission line reads as a line over terrain, not as a crack in it"
  - "the trough label lands on the trough, within 24px"
  - "no numeral on this slide is absent from claims.json"

risks:
  - "what could make this frame fall flat, named before it does"
```

## THE THREE IMAGE KEYS, and the gate that reads them off the pixels

**`layout`, `primary_image` and `accent` open every dossier, and they are written before `job`
because they are decided before it.** Added 2026-09-11. `scripts/carousel/layout_check.py`
holds the deck to them with `--require`: a deck with no `layout` keys did not plan its layouts,
and a deck with the keys on some frames and not others is not in the system.

- `layout` is one of the ten names in `assets/js/txlayout.js`. The nine values in slide order
  must pass `TXLAYOUT.check`, which is where the rotation rule LIVES. This line carried its own
  copy of it until 2026-09-18 and the copy was the superseded one, "no repeat in a row, at least
  five distinct", nine days after the rule was rebalanced on 2026-09-16 toward continuity. A
  planning spec that states a rule the checker does not hold is a spec that argues the deck back
  toward the defect, so the rule is not restated here. `TXLAYOUT.check` and
  `ILLUSTRATION_SYSTEM.md` "The rotation, rebalanced" are the two places it is written, and
  `layout_check.py --prose` fails the build on any surface that keeps a third.
- `primary_image.subject` names a THING. `rect` is where it lives, in frame px, at least thirty
  percent of the frame. `bleeds` lists the edges the rect actually touches. The gate measures
  detail and a silhouette inside that rect at thumb scale, so a rect drawn around a flat plate
  with a headline on it fails whatever the prose says.
- `accent` is the deck's one accent, the same hex on every frame that uses it, `none` on a frame
  that does not, never the flag red. The gate counts it at thumb scale: present on three to six
  frames, never over eight percent of one.

`knowledge/carousel/ILLUSTRATION_SYSTEM.md` is where the archetypes and the register are
explained, and `examples/figure-bearing/storyboard.md` carries dossiers written this way. A
dossier that names a screen, a paper stock or a print register is planning the deleted look, and
`print_ban.py` will refuse the frame it produces.

## THE VERBATIM KEY, and the five strings that made it necessary

**Any frame that seats a fragment of a source's own words lists every one of them under
`verbatim:`, each filed under the claim whose QUOTE carries it.** `scripts/carousel/verbatim_check.py`
holds each listed string to that claim and refuses one the quote does not contain.

A frame that seats none writes `verbatim: []`. That is not the same as leaving the key out, and
the gate reports the two differently: the empty list is a run that looked and says there are none,
and an absent key is a frame nobody asked the question about.

**Why the key exists.** Carousel no. 15 printed five strings that look sourced and are not, and
three judges found all five independently while every gate stayed green.

| frame | printed | what the record actually says |
|---|---|---|
| 8 | `IT DID JUST THAT` | in no claim quote at all, on a plate under the heading STATED |
| 8 | `HIGH QUALITY IMAGES` | c9 says `high-quality facial images`. The narrowing word was dropped |
| 4 | `MARYLAND, ROOFED` | a physical assertion about a real place, in no claim |
| 4 | `PROGRESO, OPEN SKY` | the same, and it contradicted the deck's own frame 1 |
| 6 | `CARRIL DE CAPTURA` and `CARRIL DE EXCLUSION` | the source says the signs were in English and Spanish. It never says what they said |

`label_guard` reads the capitalised run beside a CLAIM ID, so a plate in the art region with the
citation chip in the footer was never in its window. `noun_trace` warns on named THINGS, and
`IT DID JUST THAT` names no thing. Its whole defect is that it wears the costume of a quotation.

**The declaration is what makes this checkable, and a detector that guessed was measured and
refused.** A gate cannot tell a verbatim slot from an ordinary label by looking, because a deck
legitimately prints `SELECTION`, `BTS BORDER DATA` and `01 / 09`. An auto-discovering draft of
that gate was replayed across all fifteen shipped decks and fired on the repaired deck of
2026-09-04, on two correct authored labels. A gate that fires on correct behaviour gets switched
off, so what survives is a declaration a person writes and a machine checks.

**Write the string exactly as the frame will print it**, casing included. The check normalises
case, dashes and punctuation before comparing, so a hyphen against a space is never the reason a
line goes red. Only a word can be.

## THE PLANNED FRAME MEDIAN, and the one sentence a gate can read it out of

**Every dossier's `art.value_structure` states what that frame comes out at, in the form
`Frame median L* planned at 22`.** Nine of them, one per frame, and the nine are the deck's
value arc. `scripts/carousel/panel_ready.py` reads them straight out of `value_structure` and
measures the rendered PNGs against them BEFORE a judge is spawned.

A deck may state the arc as a summary instead, in a paragraph naming the value arc, and several
have. Where a deck writes both, the summary wins and `arc_disagreement` refuses a deck whose two
statements of one figure disagree. **Write it one way.**

**Three things the sentence has to carry, and each of them is a gate that has gone red.**

- The qualifier. `frame median L*` or `planned median L*`. A bare `median L* 44` reads as some
  REGION's median, and the gate will not guess: it treats that dossier as declaring nothing.
  2026-09-11 wrote six of its nine with the qualifier and three without.
- The number in the same sentence as the phrase. The reader stops at the sentence end, so
  `Frame median L* planned at 18, the deck's floor.` is 18 and the next sentence is not read.
- All nine or none. Eight of nine is a plan for part of a deck, and it is reported as that
  rather than compared, because an eight value plan against a nine frame render otherwise comes
  back as a stale plan, which sends a run looking in the wrong file.

**Why it is written here rather than left to a paragraph.** Carousel 22 planned 22, 46, 34, 30,
26, 18, 72, 26, 28 and shipped 13.5, 28.8, 11.6, 11.1, 18.8, 11.1, 41.1, 11.1, 14.1, four frames
inside half a point of each other at the floor, and **the gate that exists to catch exactly that
printed a pass.** It printed a pass because the plan was in the dossiers and the gate only knew
how to read a summary. The collapse was found by a one-off script written after the deck had
shipped at 6.784, which is how carousel 15's collapse was found too, which is what that gate was
built to stop happening again.

Acceptance items are free to talk about medians and should. The gate does not read them, because
they talk about REGIONS, and an item like `the frame's median L* at 432px is 45 or higher` is a
floor rather than a plan.

## THE FOCAL LAW

**A declared focal must be an AREA carrying one extreme of the frame's value range. Never a
line.**

Written into the 2026-08-19 storyboard and migrated here, because a lesson that lives in one
run's plan is a lesson the next run does not read.

A judge counted the frames whose declared focal actually won the eye across that deck and got
**two of eight**, then named why: slide 2 declared the origin tick, slide 5 the column hairline,
slide 6 the band boundaries. A hairline cannot win an eye at 432 pixels however well the frame
around it is lit, so those three frames had their art and their plan arguing about different
pictures. Rewriting those three declarations to the area each frame actually leads with moved
`artwork_craft` from 6.4 to 7.8, which is the largest single movement in the criterion that
carries the heaviest weight in the rubric.

The two frames repaired earlier in the same run were repaired the same way and nobody noticed
the pattern at the time. Slide 3's empty key went from a 54px swatch to a lit ruled block in the
bed's darkest quarter. Slide 7's NAME field went from a bright keyline round a dark box to a
recess in a lit plate. Both fixes turned a LINE into an AREA.

The test to apply while writing the dossier, before any code: **name the lightest thing in the
frame and the darkest thing in the frame. If the focal is neither, and is not the one place the
light dies, it will lose.**

## What makes an acceptance item good

**It is checkable by looking.** "Well composed" is not an acceptance item. "The bottom third
carries the annotation rule and the scale bar" is.

**It names the failure it is guarding against.** Every item on this list should be there because
something specific could go wrong, not because a template had five slots.

**It is written before the render.** An item added after seeing the output is a description, and
descriptions always pass.

**Where it asserts a STRING, a COLOUR or a COUNT, it writes that thing in a form a gate can
find.** Added 2026-08-19, and it is the most expensive line on this page.

`scripts/carousel/plan_render_check.py` was built to compare the plan against the render, and
run against the deck that scored 8.03 it reported **0 of 46 acceptance items carrying an
assertion a render could contradict**. Not one. Every item was true, careful and written before
the render, and no machine could check any of them, because they are prose ABOUT the frame
rather than claims about it.

That is why the plan-versus-render defect appeared in all three shipped runs and roughly fifteen
times. The gate was missing, and under it there was nothing to check.

Three cheap habits fix it, and none of them costs the writing anything:

- quote the exact string. `the legend carries EXACTLY ONE row, reading no class stated` becomes
  `the legend carries exactly one row, reading "no class stated"`. Now a gate can look.
- name the colour by its palette token. `the differing words are marked in pecos` already does
  this, and it is the item that shipped broken for five scoring passes, so the token is what
  makes the check possible.
- give the number and the unit. `the rate holds at 46 pixels per day` is checkable.
  `the rate is consistent` is not.

**The frame's own median value band, written in the one form the gate measures.** Added
2026-09-16, and it is the cheapest checkable item there is, because the number on the other side
of the comparison is a measurement of the frame rather than anything anybody has to write down.

    the frame's median L* at 432px is between 36 and 52
    the frame's median L* at 432px is 60 or higher
    the frame's median L* at 432px is 28 or lower
    the frame median L* measures 34 plus or minus 8 on the 270 by 338 grid

Three things make it readable and each one was learned by a deck getting it wrong.

- **Say FRAME.** A bare `median L* 44` reads as some region's median, and acceptance items
  legitimately state those: `the punch column's median L* is at least 10 below the rail face
  median`. The gate refuses to read one of those as the frame's band, because inventing a number
  the plan does not contain is worse than missing one.
- **Say at what size.** `at 432px` is the size a reader receives in the feed, and a median moves
  with the resampling, so a band with no stated size cannot be settled and the gate reports it as
  unchecked rather than picking one.
- **Put the band first and the reasoning after a comma.** `is 45 or higher, which is at least 18
  above the deck median` reads correctly. The gate stops at the comma, so the sentence can say
  why without a second number confusing what is being asserted.

**The defect this exists for.** Carousel no. 26 wrote a band into all nine dossiers, measured all
nine medians, and never compared them. Five of nine frames were outside their own band, three by
more than twenty points, while the storyboard asserted every one was inside. The first panel came
back under the bar on all three lenses and the craft judge's one line fix was to make the pixel
phase do the comparison. `plan_render_check` does it now, at Phase 12b, on the frame's own pixels
against the frame's own plan.

**A LIT FACE AGAINST ITS OWN SHADE FACE, written so a camera can settle it.** Added 2026-09-21.
Say which rectangle is lit and which is shaded, in fractions of the frame's own canvas, and at
what size to measure them.

    the cab turns, lit 0.62,0.53,0.06,0.05 shade 0.78,0.53,0.06,0.05 at 432px

`plan_render_check` samples both rectangles off the rendered PNG at that size and refuses the
frame when their contrast ratio is under 3 to 1, which is what WCAG 2.1 SC 1.4.11 asks of a
graphical object against its adjacent colours. Two faces of one solid are exactly that: the
separation IS the information that the object turns in space rather than being a silhouette with
a colour. It also refuses a frame where the rectangle called lit is the darker of the two, which
is a different fault and gets its own message.

- **Put the rectangles INSIDE the faces, clear of the outline.** A rectangle straddling a bright
  contour reads the contour as a lit face and the gate will believe it. Measured on carousel 31's
  frame 1, where a 3 percent rectangle on the truck's drawn edge reads 3.8 to 1 on a truck that
  has no faces at all.
- **Say at what size, for the reason a band does.** A cast on carousel 31's ground measured L*
  37.8 against 32.1 and a judge still could not see it at 432px. That pair is 1.24 to 1 and this
  floor refuses it, which no rule derived from our own frames would have.

**The defect this exists for.** Four scoring rounds on carousel 31 produced four DISJOINT sets of
elements the storyboard declared and the render does not carry, sixteen in all, no two rounds
naming the same one. Frame 1 declared `the truck's left face is measurably darker than its right
face` and shipped outline linework with no faces. Frame 9 declared the same of a dais and shipped
the same way. Both items are true-sounding and neither could be settled by anything, so the gate
now names an item of that shape as unsettled every run until it carries rectangles.

An item that is genuinely about judgement stays prose, and should. `the void reads as a hole
rather than as a dark tile at 432px` cannot be mechanised and is one of the best items ever
written on this deck. The rule is not that every item must be checkable. It is that an item
which HAPPENS to assert a string, a colour or a count should not throw that away in the
phrasing, because the phrasing is the only reason it was uncheckable.

## Nine dossiers, nine different jobs

If the deck's dossiers could be produced by filling in the same template nine times, the deck
will be one drawing nine times, and `bespoke_check.py` will say so in a number after the fact.
The dossier stage is where that is cheap to fix.
