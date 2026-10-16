# Texas carousel studio

Effective for runs dated October 17th, 2026 onward. This is part of the daily master routine.
Keep Texas research, sources, history, voice and factual gates. The sibling supplies the renderer
and workflow reference; its stories and variety ledgers are never inputs to Texas selection.

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

The initial manifest lists the digests. `frame_inputs()` in art_preflight.py selects each
frame's map. Accept only after viewing the rendered evidence. A boxy dominant model, an
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
