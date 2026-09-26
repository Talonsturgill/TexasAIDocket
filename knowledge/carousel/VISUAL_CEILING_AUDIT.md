# Visual ceiling audit — replacing the V1 artwork lane

## Mandate

This is not a regression repair. The entire daily artwork lane was a competent V1: it proved
that a researched article could become a coherent, deterministic, hand-coded LinkedIn carousel.
The next lane must prove something much more ambitious: that every day's record can generate a
piece of computational editorial art people stop for, remember and want to share.

The target is not “raise a six to a seven.” It is a new ceiling:

- slide 1 stops the feed before the headline has been read;
- every later slide has an authored visual idea, including deliberately quiet slides;
- the image and the claim are inseparable — another story could not wear the same frame;
- light, material, camera, scale and motion are designed, not added as finish;
- the deck has cinematic rhythm rather than nine variations of one plate;
- the pixels hold up beside elite editorial illustration, data storytelling, title design and
  generative art while remaining accurate to the public record.

Scores remain useful diagnostics. They are not the ambition.

## Corpus reviewed

The audit covers every shipped carousel contact sheet available in the repository at the time
of review, its artwork-panel median and the rendered article for the three newest decks. The
eleven-deck median is **6.9** and the mean is **6.8**. More importantly, the same ceiling is
visible in high- and low-scoring decks: coherent art direction, but limited spatial drama and a
small family of repeated constructions.

| Date | Artwork median | Dominant construction | Ceiling observed |
|---|---:|---|---|
| 2026-08-16 | 6.8 | Dark editorial atmosphere | Polished title-card language carries too much of the deck |
| 2026-08-18 | 6.0 | Cream record plates | Documents and text become layout furniture rather than image-making |
| 2026-08-19 | 7.8 | Dark technical editorial | Strongest V1 deck, but still largely diagram-plus-type rather than cinematic scenes |
| 2026-08-20 | 7.0 | Restrained cream editorial | Consistent and readable; limited depth, scale change and material surprise |
| 2026-08-21 | 7.0 | Dark data/record graphics | Information is designed, but frames share a similar planar grammar |
| 2026-08-22 | 7.0 | Cream archival editorial | Evidence is present; the document surface often becomes the composition |
| 2026-08-25 | 7.1 | Dark technical plates | Good system coherence; few images have a singular silhouette at feed size |
| 2026-08-26 | 6.9 | Cream serif editorial | Publication polish without a sufficiently new visual world |
| 2026-08-27 | 6.0 | Black industrial object plates | Repeated headline/object/footer staging and under-realized techniques |
| 2026-08-28 | 6.4 | Geological strata/data plates | Several slides reuse the same layered-section construction |
| 2026-08-29 | 6.5 | Institutional room/material plates | Planar centered compositions; type on muted rectangles dominates the image |

The last three scores are evidence, not the scope. A return to the earlier median would only
restore the V1 ceiling.

## What V1 already gets right

The replacement should preserve these gains:

- a real article claim and evidence dossier precede the art;
- slide HTML is bespoke, deterministic and reconstructable;
- the render engine already supports Canvas, SVG, d3, software 3D, Three.js, signed-distance
  fields, relief, engraving, cartography and film-grade post-processing;
- type remains vector and objective QA catches many silent production failures;
- the decks maintain publication coherence and avoid generic stock imagery.

This is why buying another rendering primitive is not the main move. The machinery is already
capable of more than the lane routinely asks it to make.

## The six structural limits

### 1. Treatment is prose, not pixels

The treatment directors can read and describe, but they cannot make competing styleframes.
The showrunner chooses among promises about images instead of images. A paragraph can sound
cinematic while collapsing into a dark rectangle, a centered object and a footer at 432 pixels.

**Replacement:** require divergent rendered styleframes — at minimum the cover and one interior
turn — before a deck language is chosen. Judge silhouette, value structure and legibility at
feed size, not rhetorical confidence.

### 2. One generalist crosses too many crafts

Phase 11 asks one showrunner to translate research, direct a visual system, model scenes, light
materials, compose type, code every slide and finish the deck. That encourages the cheapest
reliable construction and makes difficult art the first thing traded away under time pressure.

**Replacement:** give the art maker a studio operating system: visual thesis, reference
research, styleframe, graybox, camera, light, material, type integration and finish. Later,
wire the routine so those artifacts exist before full production.

### 3. The review loop is plan-relative

Pixel critics compare the render with the chosen dossier. They can catch poor execution of a
good idea, but a thin idea faithfully executed can pass. Judges arrive after the expensive
decisions and are deliberately not an art-direction loop.

**Replacement:** add a ceiling review before production: “Is this image singular enough to
deserve nine frames?” Keep later critics, but make them compare against both the plan and the
north-star scorecard below.

### 4. Research is counted, not converted into craft

The routine requests searches, but does not persist an annotated visual research artifact.
Search activity therefore has no reliable path into camera, material, palette, typography or
visual metaphor.

**Replacement:** a small, cited reference set per deck. Every reference must name what is being
studied and the transformation into this story. Reference is a springboard, never a style to
copy.

### 5. The technique library names tools more than shots

The existing library is strong on primitives and failure modes. It is weaker on the larger
construction: what the viewer sees, where the camera is, which material owns the highlights,
how evidence enters the image and why the frame has a memorable silhouette.

**Replacement:** pair the engine with a code atelier of finished constructions. Agents should
learn how primitives combine into a shot, not treat “flow field” or “SDF” as an art direction.

### 6. The lane has converged on familiar AI-design defaults

The corpus repeatedly reaches for restrained serif editorialism, cream archival plates, or
near-black technical plates with one warm accent. These are coherent, but they are also among
the most common current AI design defaults. Consistency has become similarity.

**Replacement:** use an explicit anti-default pass. If the concept can be summarized as “dark
field + floating object + elegant serif” or “cream paper + rules + document fragment,” it must
earn that choice against two materially different alternatives.

## The 10x scorecard

Evaluate the full-resolution render and the 432-pixel feed thumbnail. A showstopper should land
at **9 or better in every category**; one category cannot average away another. Accuracy and
legibility remain hard gates.

| Dimension | 6-level V1 | 9-level target | Review question |
|---|---|---|---|
| Feed stop | Tasteful layout | Immediate visual event | Would the silhouette interrupt a fast scroll with type hidden? |
| Story specificity | Topic-adjacent mood | Claim embodied in form | Could this exact image belong to another article? |
| Composition | Balanced arrangement | Directed tension and hierarchy | Is there one unmistakable entry point and a controlled eye path? |
| Depth and camera | Layered flatness | Intentional space and scale | Can the reviewer name lens, vantage, horizon and depth order? |
| Light and material | Palette plus texture | Light reveals story material | Do highlights, occlusion and shadow explain what things are made of? |
| Type relationship | Text placed over/around art | Type participates in the scene | Does type affect scale, rhythm or meaning without becoming a plate? |
| Evidence integrity | Accurate labels and numbers | Evidence is the visual engine | Is every data-bearing geometry traceable and every metaphor bounded? |
| Craft density | One technique executed cleanly | Multiple systems resolve as one image | Does close inspection reward attention without muddying the thumb? |
| Deck rhythm | Variations on one system | Designed sequence of pressure and release | Do scale, density, perspective and tempo change across the swipe? |
| Memorability | Professionally on-brand | Ownable image | Can someone describe the frame tomorrow in one concrete sentence? |

### Hard vetoes

Reject a direction before production when any of these are true:

- the cover depends on reading more than seeing;
- the main image has no recognizable silhouette at 432 pixels;
- the reference set contains only other AI-made work or only one aesthetic family;
- the visual metaphor implies an unsupported fact, magnitude, location or causal relationship;
- three or more slides could be produced by changing the text inside the same composition;
- “premium,” “cinematic,” “editorial,” “bold” or a named technique substitutes for a shot;
- polish is expected to rescue an unresolved graybox;
- the deck repeats a recent material world, palette, camera grammar or signature construction
  without a claim-specific reason.

## The new capability contract

Before the daily routine is rewired, the artwork layer needs four durable assets:

1. **This audit** — a shared definition of the ceiling and the gap.
2. **A reference atlas** — primary, craft-specific sources with translation rules.
3. **A carousel art-studio skill** — a progressive workflow that turns evidence into visual
   thesis, divergent pixels and production-ready shot plans.
4. **A code atelier** — executable styleframes proving that the committed engine can produce
   dimensional, authored images rather than merely naming advanced techniques.

Only after those exist should the routine decide which agents make which artifacts. Otherwise
automation would merely make the V1 process more elaborate.

## Definition of success for the later workflow phase

When the new capability is wired into the routine, it should be measurable beyond panel score:

- compare styleframe candidates at feed size before committing the deck;
- record which visual construction, material world and camera grammar shipped;
- track cover dwell/stop proxies, document opens, completion/swipe behavior where LinkedIn
  exposes them, saves, shares and qualified comments;
- run periodic blind side-by-side reviews against both prior Docket decks and current
  best-in-class references;
- treat repeated visual language as creative debt even when it scores well.

The north star is simple: a reader should recognize the Texas AI Docket because the work is
specific and excellent, not because every deck looks the same.
