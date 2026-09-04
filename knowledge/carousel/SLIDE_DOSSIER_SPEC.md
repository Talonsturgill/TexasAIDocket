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
job: >
  One sentence. What this slide does that no other slide in the deck does. If two dossiers
  have the same job, one of the slides is cuttable.

claims: [c4, c7]          # every factual string on this slide, by claim id
numerals:                 # every figure, and where it comes from
  - value_from: c4        # a claim, or
  - computed_by: "scripts/... , peak divided by approved"   # a computation

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
  value_structure: "what is lightest, what is darkest, and what each is doing"
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

An item that is genuinely about judgement stays prose, and should. `the void reads as a hole
rather than as a dark tile at 432px` cannot be mechanised and is one of the best items ever
written on this deck. The rule is not that every item must be checkable. It is that an item
which HAPPENS to assert a string, a colour or a count should not throw that away in the
phrasing, because the phrasing is the only reason it was uncheckable.

## Nine dossiers, nine different jobs

If the deck's dossiers could be produced by filling in the same template nine times, the deck
will be one drawing nine times, and `bespoke_check.py` will say so in a number after the fact.
The dossier stage is where that is cheap to fix.
