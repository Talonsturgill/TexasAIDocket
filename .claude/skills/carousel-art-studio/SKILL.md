---
name: carousel-art-studio
description: Art-direct and construct show-stopping, evidence-grounded computational artwork for Texas AI Docket LinkedIn carousels. Use when researching visual references, inventing a carousel treatment, making or comparing styleframes, planning shots, coding bespoke slide art, or reviewing whether a deck reaches the publication's 10x visual ceiling. Produces visual theses, rendered alternatives and production decisions; use carousel-engine separately for rendering and machine QA.
---

# Carousel art studio

Make an image worth stopping for before making a deck worth approving. This skill is the
creative studio upstream of `carousel-engine`: it decides what the art says, finds a singular
visual world, proves that world in pixels and develops the shots. The engine renders and checks
the result; it does not provide the art direction.

The standard is `knowledge/carousel/VISUAL_CEILING_AUDIT.md`. The source shelf is
`knowledge/carousel/REFERENCE_ATLAS.md`. The publication rules in
`knowledge/carousel/DESIGN_DOCTRINE.md` and the accuracy/technical contracts in
`carousel-engine` still apply.

## Read by task, not by habit

Load only the references needed for the present decision:

- concept or treatment: `references/visual-thesis.md` and
  `references/composition-and-camera.md`;
- styleframe competition: `references/styleframe-brief.md` and
  `references/linkedin-native.md`;
- dimensional scene: `references/light-material-depth.md`;
- generative, data-bound or simulated form: `references/computational-systems.md`;
- full-deck sequencing or pixel review: `references/linkedin-native.md` and
  `references/review-gates.md`;
- coding an advanced construction: `references/atelier.md`, then inspect only the relevant
  source under `examples/art-atelier/`.

Do not read an atelier frame as a template. Read it to understand how camera, value, light,
material, typography and code resolve into one shot.

## Non-negotiable output

Do not select a treatment from prose. A selected direction requires:

1. a one-sentence visual thesis tied to the verified claim;
2. a cited reference cut with study/transform/do-not-copy notes;
3. at least three materially divergent candidate directions;
4. rendered pixels for each candidate — cover plus one interior turn when selecting a deck
   language, not a cover alone;
5. full-size and 432-pixel comparisons;
6. a written selection decision and discarded-direction reasons;
7. a shot card for every production slide.

If the task does not permit rendering, label the result **unproven treatment**. Never imply
that prose has passed the visual gate.

## Studio sequence

### 1. Lock the visual truth

Extract one claim the image can honestly carry. Separate:

- verified fact, quantity, place and time;
- measured or modeled data;
- bounded metaphor;
- unknown or unavailable information.

Geometry is a sentence. Size, position, direction, connection, material and absence all make
claims even without labels. Do not invent a magnitude, map location, causal link, crowd,
machine detail or record fragment for drama. Read `references/visual-thesis.md`.

### 2. Cut references with intent

Use three to six references from the atlas and primary story-domain sources. Research a craft
property, not a vibe. For each reference write what to study, what evidence it serves, how it
will be transformed and what must not be copied. At least one source must come from the actual
material world of the story and at least two must break from the current AI-design defaults.

Do not collect a wall of similar images. That narrows invention while pretending to expand it.

### 3. Write the visual thesis

The thesis names a visible event, not an adjective stack:

> The record becomes **[specific world/object/system]**, seen from **[decisive vantage]**, where
> **[verified tension/change]** is expressed by **[spatial/material behavior]** and illuminated
> by **[motivated light]**.

Then name the cover's memory sentence: the concrete description a reader could repeat tomorrow.
If it is “text over a nice background,” restart.

### 4. Diverge in construction, not decoration

Make at least three directions that differ in all of these:

- image architecture: object, environment, section, field, machine, evidence excavation, etc.;
- vantage and lens: plan, macro, low wide, orthographic, cutaway, impossible evidence camera;
- material and light behavior;
- type's spatial role;
- motion or generative rule;
- feed-size silhouette.

A palette swap, font swap or alternate arrangement of the same plate is one direction.
Explicitly challenge the cream/serif archival plate, near-black/bright-accent object plate and
hairline broadsheet layout. They may win only for a claim-specific reason.

### 5. Prove the hard parts in pixels

For each candidate, build a graybox before finish:

1. three-value composition and crop;
2. subject silhouette and camera;
3. depth planes and type reserve;
4. key/fill/practical light and contact;
5. material response;
6. evidence layer and annotations;
7. finish: atmosphere, grade, grain and optical detail.

Render at 1080×1350 and inspect at 432 pixels. If the graybox is weak, do not texture it.
Use `references/styleframe-brief.md` for the artifact and `carousel-engine` for rendering.

### 6. Choose against the ceiling

Score candidates with `references/review-gates.md`, beginning with feed stop, story specificity
and memorability. Accuracy and legibility are vetoes. Select the direction with the strongest
image system, not the one that was easiest to code or most eloquently described. Preserve the
losers and the decision so tomorrow does not rediscover them.

### 7. Direct the deck as a sequence

Give every slide a different visual job inside one world. Alternate pressure and release:
scale, density, camera distance, value, tempo and evidence mode. A quiet frame can be
exceptional; it still needs a decisive image, proportion or absence. Read
`references/linkedin-native.md`.

Write a shot card per slide before production. If three cards differ only in copy, the deck is
still a template.

### 8. Build by passes

Keep construction passes explicit so criticism can target the real problem:

- `G0 truth` — encoded geometry is supported;
- `G1 read` — graybox and silhouette work at feed size;
- `G2 space` — camera, overlap, occlusion and scale read;
- `G3 light` — value hierarchy and motivated illumination reveal form;
- `G4 material` — surfaces respond differently and specifically;
- `G5 evidence` — labels, data and source matter integrate honestly;
- `G6 type` — display and body type participate without becoming furniture;
- `G7 finish` — atmosphere, grade and microdetail unify the resolved shot.

Do not jump from G0 to G7. Finish amplifies what is already there, including weakness.

### 9. Review the image and the system

Use the full render, the 432-pixel thumbnail and the contact sheet. Review the frame with type
briefly hidden to expose compositional dependence. Review the deck in grayscale to expose value
collapse. Then run the machine QA. A green harness means the artwork is safe to judge, not that
it is great.

## Studio prohibitions

- No invented facts disguised as visual specificity.
- No adjective-only art direction: premium, cinematic, tactile and bold are outcomes.
- No named technique standing in for a shot.
- No full deck before divergent styleframes.
- No generic background whose only job is filling space behind type.
- No panel score used as permission for repeatable sameness.
- No copyrighted style or living artist requested “in the style of.” Study transferable craft
  properties from original sources and transform them.
- No external runtime dependency or network asset in slide HTML.

The goal is not maximal visual noise. It is maximal authorship: the most inevitable, surprising
and beautifully resolved image this particular public record can truthfully support.
