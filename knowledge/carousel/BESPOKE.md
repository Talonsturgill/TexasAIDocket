# BESPOKE, one artist per slide (owner, 2026-11-14)

**The owner, verbatim:** *"I want every single slide to really be like custom. I don't want this in just
some kind of template. I want like bespoke artwork on every single slide, because that's where we can
separate ourselves from everyone else. Everyone else is just going to use some stupid template. We can
have an agent, you know, create masterful artwork on every single slide separately, so that sure, they
say they follow the same flow like for a post, but you can tell that it's custom artwork."*

This page is the whole art doctrine for a run dated on or after `config/carousel/bespoke.json`
`bespoke_from`. Where an older rule in `daily_routine.md`, `ILLUSTRATION_SYSTEM.md`, CLAUDE.md or an
agent file asks for one world, one light, one rig, one layout menu or one fixed type position on every
frame, this page wins for that run. LOOK V2 (CLAUDE.md) still sets the colour, and every integrity rule
still stands.

## What went wrong (measured 2026-11-14, runs Oct 23 to Nov 14)

- **Twenty of twenty decks** ran to the round cap and shipped under the 8.0 bar (6.83 to 7.46).
  `artwork_craft` sat at 6.2 to 6.8 against a floor of 8.5, which stood down every day.
- **Every slide was the same slide.** Kicker top left, a Fraunces headline pinned at y 150, a 35 word
  dek, the art in the bottom half under a dark band, the footer. The type owned the top 40 to 50
  percent of every frame, so the art could only vary underneath it.
- **One author.** The main session wrote all nine slides in one context from one chassis, through the
  same twelve call recipe (`CH.boot`, `CH.stage`, sky, ground, rig, weather, stage, snapshot, develop,
  dress, finish). Nobody conceived a slide on its own.
- **Coherence was enforced at the pixel, not the story.** One world (`TXT.sky` threw on any other), one
  light, one grade, a value track capped at 14.9 L* per step, and a rubric whose 10 was "any frame is
  unmistakably from this deck". The cheapest way to pass was to make nine near copies.
- **One motif per deck.** The data-in-art floor turned into rows of the deck's hero object at nine
  counts.

The September 16 owner note that started the chassis asked for the same thing as today: *"I want each
page to really seem like custom artwork, not just like somebody went and like threw some text boxes on
a page."* The chassis answered "flow together" and lost "custom". This page restores the balance.

## The split: what the deck shares, what each slide owns

**The deck shares its SPINE, and only its spine:**

- the tone, its palette and its grade (`TXDECK.declare({ look: "v2", tone, bespoke: true, grade })`,
  `TXDECK.finish` last on every canvas)
- the type faces (Fraunces for the hook, Manrope for the dek, JetBrains Mono for furniture), the
  counter, the site line and the claim ids, at their furniture sizes
- the accent's one meaning
- the story's order and the visual argument's through line, written in `storyboard.md`
- any models the chassis builds for the story, which a slide may use or leave

**Each slide owns everything else:**

- **its world.** Studio sweep, a lit interior, an outdoor world at any hour, a material relief, a map
  relief, a cutaway, a macro, an exploded diagram, a type built as an object. `TXT.sky(R, world)` takes
  the frame's own world on a bespoke deck.
- **its light.** `TXT.deckRig(R, spec, { light: { az, el } })` turns the key for this picture.
- **its camera.** Lens, height, distance, crop. A worm's eye, an aerial, a 30 cm macro, an orthographic
  plan.
- **its composition and its type.** The slide decides where the headline sits, how big, in how many
  lines, and how the art makes quiet for it: top, bottom, a column beside the subject, inside the sky,
  across a wall. Seat it with `TXLOOK.typeSeat` (or `CH.seat`), which follows the type wherever it is.
  Never a plate. Every factual sentence of the copy stays word for word. A dek sentence that only
  describes the picture ("drawn to illustrate", "one wafer stands for $1 million") is the artist's to
  rewrite so it describes the picture actually drawn, with "drawn to illustrate" kept and no new
  number, date, name or claim. `copy.json` is updated from the slide's own HTML after the art, as it is
  today.
- **its medium.** Any bench in the ARSENAL. Two adjacent slides should rarely share one.

## How the work is done

1. **The showrunner plans, it does not draw.** After the copy chamber, it writes one SLIDE BRIEF per
   frame into `runs/carousel/<date>/briefs/slide-NN.md`: the beat (what this slide must make a reader
   feel and know), the exact copy from `copy.json`, the figures from `figures.json` the art must carry,
   the claim ids, the spine (chassis path, tone, accent meaning), the neighbours' beats, and what the
   last four decks already did. It writes the spine chassis with `bespoke: true` and the shared models.
2. **Nine slide artists, in parallel.** One `carousel-slide-artist` per frame, all spawned in one
   message. Each reads only its brief, this page, CLAUDE.md LOOK V2 and the ARSENAL. Each pitches three
   different concepts to itself, picks the strongest, builds `slides/slide-NN.html`, renders it with
   `render.py --only NN`, opens its own PNG, judges it against THE SLIDE BAR below, and reworks it. It
   iterates until it scores itself 8.5 or better or it has spent its six renders, and hands back the
   slide, its concept in two sentences, its self score and its weakest point.
3. **One slide critic per slide.** A `carousel-slide-critic` (session model) scores each finished frame
   cold against THE SLIDE BAR, with the brief and the PNG and nothing else. A frame under 8.0 goes back
   to its artist with the critic's two fixes, once. A frame still under 8.0 is rebuilt from a different
   concept, once. A critic after the first is handed the earlier critique and checks whether its fixes
   landed before it names anything new, so the bar holds still between rounds. After the rebuild round
   the frame ships at its score and the panel decides.
4. **The deck pass.** The flow critic reads the contact sheet for the story's order and the spine, never
   for sameness. `distinct_check.py` proves the frames differ. The panel scores as before.

## THE SLIDE BAR, which the artist and the critic both apply

At 432 px with the type covered, and then at full size with it:

1. **Could only have been made for this sentence.** Swap in another slide's headline: does the picture
   stop making sense? If not, it is decoration.
2. **One idea a stranger gets in a second.** One subject, one figure, one turn of the story.
3. **Composed, not placed.** The type and the art were designed together. The art makes the quiet the
   type sits in, and the type's position is the one this picture wanted.
4. **Crafted to the edges.** Real materials, a light the shadows agree with, contact where things touch,
   detail where the eye lands, no primitive left as a primitive, no grey middle, LOOK V2's colour.
5. **Unlike its neighbours.** Different world, camera, scale or medium from the slide before and after,
   while the tone and the type say it is the same post.
6. **Honest.** Every count and length drawn is read from `figures.json` in the slide's own code, and
   anything illustrative is labelled so in the dek.

10 is the opening spread of a magazine feature commissioned for this exact story. 8 is strong with one
soft spot. 6 is competent and could have run on another story. 4 is a template.

## The gates on a bespoke run

- `distinct_check.py` replaces sameness gates with a difference gate: no two frames too alike as images,
  type placed in at least four distinct places across nine frames, no more than two frames with the type
  in the same spot in a row.
- `deck_chassis.py` keeps one chassis, one declare and `TXDECK.finish` on every frame. Those are the
  spine.
- `value_register.py --look v2`, `print_ban.py`, `figure_bearing.py`, every integrity gate: unchanged.
- **Stood down on a bespoke run:** the one world rule, the one light rule, `deck_coherence.py`'s value
  strobe cap (the turn between two worlds is the point), `layout_check.py`'s archetype rotation, the
  fixed `.hook` position, the twelve call recipe and the "unmistakably from this deck" reading of
  `deck_coherence` in the rubric, which on a bespoke deck asks whether the nine read as one post by the
  spine and the story.

## What the worked example measured (2026-11-14)

- Difference: round one adjacent mean 0.377 with the type in 4 places and runs of 3. After one rework,
  adjacent mean 0.302, max pair 0.643, the type in 6 places and a longest same-place run of 1. The last fourteen
  shipped decks measured 0.452 to 0.567 with the type in 1 or 2 places.
- Craft: artists scored themselves 7.3 to 8.3; cold critics scored the same frames 4.8 to 7.6 in round
  one and 5.8 to 7.2 after one rework. Self scores run about 1.5 points high, so the critic stage is
  load bearing. Two of nine frames changed critic score by more than a point in the wrong direction,
  because round two's critic did not see round one's critique, which is why later critics now do.
- What held the craft score down was the engine, not the process: capsule figures, flat discs, plain
  cylinders and pastel gradients where the critic asked for real silicon, glass and machined parts.
  More rounds of the same kit give little. The next lift is the model and material library.

## The worked example

`examples/bespoke-proof/2026-11-14/`: the Nov 14 story, copy and figures, built by nine slide artists
on the spine `assets/js/deck/2026-11-14-waferbench-bespoke.js`, beside the shipped deck and the look v2
proof. Copy the method, never the pictures.
