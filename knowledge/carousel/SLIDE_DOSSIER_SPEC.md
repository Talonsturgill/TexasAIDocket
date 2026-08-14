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
  focal: "what the eye lands on first, and what pulls it there"

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

acceptance:               # THE PIXEL CRITIC GRADES AGAINST THIS, ITEM BY ITEM
  - "the peak figure is legible at 432px against the ember band"
  - "the transmission line reads as a line over terrain, not as a crack in it"
  - "the trough label lands on the trough, within 24px"
  - "no numeral on this slide is absent from claims.json"

risks:
  - "what could make this frame fall flat, named before it does"
```

## What makes an acceptance item good

**It is checkable by looking.** "Well composed" is not an acceptance item. "The bottom third
carries the annotation rule and the scale bar" is.

**It names the failure it is guarding against.** Every item on this list should be there because
something specific could go wrong, not because a template had five slots.

**It is written before the render.** An item added after seeing the output is a description, and
descriptions always pass.

## Nine dossiers, nine different jobs

If the deck's dossiers could be produced by filling in the same template nine times, the deck
will be one drawing nine times, and `bespoke_check.py` will say so in a number after the fact.
The dossier stage is where that is cheap to fix.
