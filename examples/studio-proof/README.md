# Material relief renderer study

Three native HTML studies use the frozen figures from Texas no. 52 to exercise `TXBENCH.relief`.
They show a computed mark count, a cut scale and a multi-material inset. This is an engineering
proof. It is not a daily release, an approved treatment or an independent artwork score.

The renderer's upstream source and exact commit are recorded in `txbench.js`. Geometry, copy and materials here are Texas
inputs. Each slide authors its own height and material functions; the shared chassis supplies
only the light, palette and finish. All visible type remains DOM text.

```bash
python3 examples/studio-proof/build.py
python3 .claude/skills/carousel-engine/render.py \
  --slides-dir examples/studio-proof/slides --out-dir out/studio-proof/render
python3 .claude/skills/carousel-engine/qa.py --render-dir out/studio-proof/render
node tests/txbench.mjs
python3 tests/carousel_studio.py
```

The native renderer tests verify deterministic pixels, visible cast shadows under window masks, inherited light,
invalid geometry and a flat carrier that casts no shadow. The Python regression tests cover
hardest-frame selection, changed-image review binding, phase-clock resumption and the real
calendar encode that lost a component after passing PSNR. They also check the master prompt's
actual agent assignment and checkpoint names, and reject a new package with missing layout
inputs before the encoder writes or removes an image. The replay uses ordinary file copies.
The native crop regression reconstructs a complete 2160x2700 image exactly from its six tiles,
then rejects changed frames, changed tiles and incomplete coverage. The reviewer brief reads
the real Texas YAML dossiers and sends their craft and lower-third plans with the crops.
