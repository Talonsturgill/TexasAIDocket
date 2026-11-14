# Texas carousel studio

Effective for runs dated October 17th, 2026 onward. This is part of the daily master routine.
Keep Texas research, sources, history, voice and factual gates. The sibling supplies the renderer
and workflow reference; its stories and variety ledgers are never inputs to Texas selection.

## BESPOKE (owner, 2026-11-14): on a run dated on or after `config/carousel/bespoke.json` `bespoke_from`

One artist per slide. `knowledge/carousel/BESPOKE.md` is the art doctrine for that run and wins over the
route rules, the audition and every one-world, one-light or fixed-layout instruction below. The deck
shares its spine (LOOK V2 tone, palette, grade, type faces, counter, site line). Nine
`carousel-slide-artist` agents each conceive, build, render and rework one frame, nine
`carousel-slide-critic` agents score them, and `distinct_check.py` proves they differ. The daily
routine's BESPOKE MODE section has the phases.

## LOOK V2 (owner, 2026-11-14): read this first

**The owner, verbatim:** *"make it 10x better, the artwork on the carousels is nowhere near the
quality it needs to be."* The same week, on the films: *"very 2D ... every corner is very sharp ...
faded colors. I want more pungent ... think about how Apple MacBook they do it."*

**What the dark stage did.** THE STAGE below cured "faded" by measuring lightness only, so every
deck went to a staged near black world. The shipped Nov 14 deck measured a median L* of 5.6, 0.62
of its pixels near black and a median chroma of 2.2: one small object in a black room under a black
type band. TikTok viewers gave Texas decks 2.85 to 3.03 seconds against 17.65 for the sibling's.
"Faded" was never mid tones. It was mid tones with no colour: the October 4th deck holds 0.62 of its
pixels at L* 30 to 70 with chroma under 18.

**For every run dated on or after `config/carousel/look.json` `v2_from`, this section wins over THE
STAGE and over any instruction to stage a deck dark:**

- **One tone per deck.** The chassis calls `TXDECK.declare({ ..., look: "v2", tone })`, with tone one
  of `wonder`, `explainer`, `win`, `watch`, `people`, and `grade: TXLOOK.grade(tone)`. The tone is how
  the story should leave a reader. Rotate it; at most two `watch` decks in any seven. Pick the
  matching world `TXT.V2_WORLD[tone]` (`v2wonder`, `v2explainer`, `v2win`, `v2watch`, `v2people`).
- **Colour, never black.** Shadows lean to the tone's violet or navy, never black. No `TXT.stage`, no
  dark room, no black type band. Seat type with `TXLOOK.typeWash` and the footer with
  `TXLOOK.footWash`, both in the tone's own deep hue.
- **The studio.** An object frame stands in `TXT.studio(R, { tone })`: a seamless sweep in the tone's
  colours under a big soft key, a cool rim behind and a coloured environment, so metal and glass
  reflect colour. It counts as the frame's room for `print_ban`. A relief frame starts from
  `TXLOOK.sky2d`, takes `TXLOOK.reliefLight()` and gives its materials saturated tone albedos, warm
  ground under the cool sky, the accent on the one thing that matters.
- **Round and lit.** `TXT.roundedBox` edges, soft contact shadows, the subject filling at least half
  the frame. Labels are accent pills (`TXLOOK.css`), never a mono caption on black.
- **Measured.** `value_register.py` judges a v2 run on colour: grey mid tones (L* 30 to 70, chroma
  under 18) at most 0.30 of a probe frame and 0.20 of the deck mean, vivid pixels (chroma 30 or more)
  at least 0.20 of a probe frame and 0.30 of the deck mean, near black at most 0.25 of any frame and
  0.12 of the deck mean. The light deck cap is unchanged.
- **The worked example** is `examples/look-v2-proof/2026-11-14/`: the shipped Nov 14 story and figures
  rebuilt on look v2, explainer tone, with its chassis `assets/js/deck/2026-11-14-waferbench-v2.js`.
  Deck median L* 49.7, median chroma 26.9, vivid 0.54, near black 0.04. Copy its approach, never its
  subject.

Everything else in THE ARTWORK IS RENDERED stands: rendered frames, no print screen, six of nine on
a physical bench, one light, one grade, computed figures.

## Choose the image before building the scene

Read the last three Texas score cards, open their contact sheets and read the current machine queue. Give the directors the
actual weakest-frame findings, including which attempted repairs failed. Ask for three distinct
visual arguments. At least one must draw the evidence directly with a measured scale or a
changing material motif. A vehicle, a room and a podium are subjects only when their geometry
explains the claim. A measurement can be more direct than another scene around a kit model.

Choose from two physical render routes, or mix them within one coherent deck.

- `txthree.js` builds spatial scenes with a camera, physical materials, ground and a sky or room.
  Use it when perspective, a place or an object's construction explains the story.
- `txbench.js` renders a material relief from a height field. It computes normals, cavity
  occlusion, specular response and cast shadows under the chassis's declared light. Use it for
  measured cuts, traces, surfaces and material evidence. Its report must show at least two
  materials, a real height range, cast shadows and a carrier covering at least 30 percent of
  the frame. A flat chart or a fallback does not count as a physical render.

One material vocabulary, light, grade and visual argument hold the deck together. The
individual subjects and techniques can change with the claims. A single hero object on every
slide is optional. Keep the print ban, rendered-frame floor, value checks and bespoke drawing
requirement. In an entirely orthographic relief deck the depth cues are form shading, cast
shadow and cavity occlusion. Perspective is required only of a scene that claims perspective.
The existing score weights and ship thresholds do not change.

## Rehearse the hardest frame

Before the copy room or the rest of the art, write `out/<date>/art_plan.json`.

```json
{
  "hardest_frame": 3,
  "visual_argument": "The measured distinction a reader should see without the headline",
  "build_risk": "The difficult subject or physical effect and the available implementation",
  "distinct_from_recent": "The specific difference from each of the last three visual treatments"
}
```

Render the cover, that hardest interior frame and the close at final size. Use
`art_preflight.py --date <date> --write`; it reads the selection from the plan. The default
evidence frame number from old runs is no longer a selection method. Review all three at feed
size and the hardest subject at native size. Use one `carousel-art-director` on the inherited
session model for this review. Supply the actual images, dossiers and input digests. Run
`python3 scripts/carousel/critic_brief.py --run-dir out/<date> --slide 1 --slide <hardest> --slide 9`
and supply its craft lines and complete native crop paths. Every successful render now cuts
1080x900 pixel tiles in `render/crops/`; the helper refuses stale or incomplete sets. Read
every selected tile at 100 percent to judge material and lighting, then the feed view to judge
the argument. Re-render a selected frame when its crops are missing or stale. The
mechanical pixel critic does not substitute for this visual judgement. The review records the existing subject,
visual consequence, weakness and repair, plus these fields on each frame.

```json
{
  "encoding_reads": true,
  "dominant_subject_finished": true,
  "feed_legible": true,
  "inputs": {"copy the exact frame source, image and shared-asset digest map here": "sha256"}
}
```

The initial manifest lists the digests and a `frame_inputs` map keyed by slide number. Copy
that frame's map into its review; it includes only assets its HTML actually references. A
chassis used by all three still binds all three; a helper used only by the close binds the
close. Accept only after viewing the rendered evidence. A boxy dominant model, an
unreadable water effect or an image whose data encoding needs the caption is a failed audition.
After one unsuccessful repair, choose a more feasible treatment or change the representation
before building six more dependent frames. Do not spend late panel rounds on an engine effect
the audition could not produce. A simpler physical representation still has to explain the
claim and pass the same image and factual gates.

## Review changed evidence once

Run `art_preflight.py --write` after a repair. Version 2 preserves only frame reviews whose
source, rendered image, shared assets and art plan are identical. `needs_review` lists the
frames requiring a fresh reading. Supply only those frames to the visual reviewer, preserve
the unchanged entries and keep the frame list in selected order. The reviewer binds each new
entry to its exact digests. Set the overall decision to `accept` after all three are approved.
A changed chassis invalidates all three; a changed close invalidates the close.

Batch the current pass's concrete repairs, render only changed slides and re-review those
slides. Use at most two pixel polish passes and one whole-deck flow pass. Apply the flow
critic's concrete repairs, then recheck changed frames. Failed factual, render and legibility
gates still require repair and fresh verification. Finish all nine before assembling once. The flow critic receives the whole sequence
and the native crops for the weakest subjects. The independent three-judge final panel stays;
its historical factual catches are documented in panel.py. It is the final check after the
audition and review, rather than the first reader of an unfinished model.

## Verify what will ship

Copy the final storyboard and render report beside the PNGs before `ship_images.py`. The
encoder now runs layout_check against the WebPs while the original PNGs still exist. If
compression changes a passing layout, it uses lossless WebP for the affected frame and checks
again. The PSNR floor stays in force. A failure already present in the original is repaired in
the artwork. Never change the dossier to describe an accidental compressed result.

Archive `art_plan.json`, `art_preflight.json` and `studio_clock.json` with the run. The existing
shipped-image, factual, article, CI and draft-only delivery requirements still apply.

## Measure the next runs

At wake and each named phase exit call `scripts/carousel/studio_clock.py`. Record actual UTC
timestamps for wake, record_done, audition_done, art_done, review_done, panel_done and
package_done. Checkpoints are idempotent across compaction. `--report` computes elapsed minutes
from these timestamps; no duration is typed into copy. Archive through package_done before the
PR is opened. Use GitHub's PR merge timestamp for the subsequent release interval.

Compare the next three normal daily runs with the audit baseline. Report artwork and
normalized total scores separately, the number of visual and panel rounds, audition revisions,
compression repairs, time to package and PR-to-merge time. A source outage or a weekly machine
pass gets its own interval. No target duration ends a run, weakens a gate or becomes a claim
that a faster full run has already been measured.
